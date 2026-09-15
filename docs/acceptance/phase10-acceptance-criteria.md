# Phase 10: DXY Context Module Acceptance Criteria

**Doc:** CBR-ACC-010 · **Version:** v1.1 · **Declared:** 2026-09-14, **before** the module was run on market data
**Owner instruction:** Phase 10 continues (D14). Deterministic, causal DXY context primitives. No DXY rules optimized, no
profitability questions, no holdout P&L, no research-derived DXY filters.
**Implementation:** `src/cbr/dxy/context.py` (+ `config/dxy_context.yaml`) → `src/cbr/dxy/phase10_acceptance.py` →
`reports/phase10-dxy-context.{json,md}`

---

## 1. Scope

The module turns Dukascopy DOLLARIDXUSD (DXY CFD) 1m candles into context attached to any UTC decision-time grid (XAUUSD
1m or 5s bar close times):

- **Quote context:** the last DXY close known at the decision time, its age, availability and confidence.
- **15m and 1h candle context:**
  - the **last closed** candle's direction and move (close − open);
  - the **forming** candle's direction and move as of the decision time. This is the view of E15-042 ("gold open and extend bullish … DXY open and extend bearish") and E1H-044.
  - Both carry availability state, confidence, coverage and reason codes.

**Out of scope (explicit):**
- 1m/5s DXY structure (D12-6).
- DXY highs, lows and extension extremes: they need a canonical extremes source (OQ-25). Phase 10 uses 1m **open and close only**, which Phase 9 validated (AC-03: identical to tick-built bars).
- DXY range condition, DXY type-3 shifts, inversion/veto/confluence rules (`CBR15-DXY-001/003`, EP2-026/029). These stay Phase 18 ablations via Phase 17.
- Any use of DX futures prices: DX is used only to **flag** CFD vendor gaps (D12-1), never as a substitute value.

## 2. Definitions (IMPL unless cited)

| Term | Definition |
|---|---|
| 1m row | A DXY candle-file row (zero-volume rows already dropped in Phase 9). Open time `m`, close time `m + 1 min` |
| Known at `t` | A 1m row is known at decision time `t` iff its close time ≤ `t`. Nothing else is used |
| Candle window | 15m/1h UTC-aligned `[open, open + tf)`. Last closed candle at `t`: the one with close = `floor(t, tf)`. Forming candle: open = `floor(t, tf)`; its elapsed part is `[open, t)` |
| Candle open / close | Open of the first known row in the window; close of the last known row. No price is carried in from outside the window |
| Direction | `UP` if close − open > `flat_epsilon`, `DOWN` if < −`flat_epsilon`, else `FLAT` (candle close direction, as used for CBR levels; E15-042 same-candle view) |
| Expected-closed minute | Weekend (Fri 17:00 → Sun 18:00 New York) or daily break 17:00-18:00 New York (DST-aware). Same schedule as Phase 9 AC-07 |
| Coverage | Known rows ÷ expected-open minutes in the elapsed window |
| Causal vendor-gap flag | `DXY_CFD_MISSING_WHILE_DX_ACTIVE` evaluated **only on data known at `t`**: a CFD no-row run, truncated at `t`, of ≥ 30 min containing ≥ 15 DX minutes with volume > 0 (data_quality.yaml thresholds) |
| DX reference available | The DX 1m dataset covers the minute (DX history starts 2018-12-26 01:00 UTC) |

### 2.1 Window states → confidence (first matching row wins)

| State | Condition | Confidence | Reason code |
|---|---|---|---|
| `NO_ELAPSED_TIME` | Forming window with 0 elapsed minutes | UNAVAILABLE | `DXY_WINDOW_NOT_STARTED` |
| `NOT_LOADED` | Any elapsed minute lies outside the loaded CFD range (never confused with no quotes) | UNAVAILABLE | `DXY_NOT_LOADED` |
| `CLOSED_SCHEDULE` | Every elapsed minute is expected-closed | UNAVAILABLE | `DXY_SESSION_CLOSED` |
| `VENDOR_MISSING` | The elapsed window intersects a causal vendor-gap flag | UNAVAILABLE | `DXY_CFD_MISSING_WHILE_DX_ACTIVE` |
| `NO_QUOTES` | No known rows in the window | UNAVAILABLE | `DXY_NO_QUOTES` |
| `LOW_COVERAGE` | Coverage < `min_coverage_full` | REDUCED | `DXY_LOW_COVERAGE` |
| `UNVERIFIED_GAP` | The window overlaps a CFD no-row run (truncated at `t`) ≥ 30 min that includes minutes without DX reference | REDUCED | `DX_REFERENCE_UNAVAILABLE` |
| `OK` | otherwise | FULL | none |

Quote context: `dxy_close` = close of the last known row if its age ≤ `max_quote_age_minutes`, it isn't separated from
`t` by a causal vendor-gap flag, and no expected-closed minute lies between it and `t`. Otherwise NaN (`DXY_QUOTE_STALE`,
`DXY_CFD_MISSING_WHILE_DX_ACTIVE` or `DXY_SESSION_CLOSED`). Quote confidence: FULL if the row closed at `t` itself
(age 0), REDUCED if 0 < age ≤ max age, UNAVAILABLE when NaN.

### 2.2 Causal fields vs hindsight data-quality mask

At a decision time inside a vendor outage, a causal module can't know yet that the gap is an outage and not thin quoting.
For up to `max_quote_age_minutes` it can show the last quote, with REDUCED confidence, until the gap exceeds that age or
the causal flag fires. Two field families are therefore produced:

- **Causal context fields** (`dxy_*`): the only fields a signal engine may read.
- **Hindsight data-quality mask** (`dq_hindsight_*`): the Phase 9 detector over the **whole** loaded span, marking every
  minute of a flagged vendor gap. It uses future data by design, so it is **never** an engine input. It exists so the ledger
  can label setups whose DXY context intersects a confirmed outage (D12-1 "lower data confidence"). How the ledger applies
  it is an owner decision (OQ-31), not settled in Phase 10.

Thresholds in `config/dxy_context.yaml` (`flat_epsilon` 0, `min_coverage_full` 0.5, `max_quote_age_minutes` 10) are
**IMPL**, declared here before measurement. Their distributions are reported, not tuned.

## 3. Criteria

| ID | Criterion | How tested |
|---|---|---|
| AC10-01 | **UTC normalization.** Inputs must have tz-aware UTC indexes (naive or non-UTC rejected); every output timestamp is UTC | Unit tests |
| AC10-02 | **Causality (truncation).** Context at `t` computed from data truncated to what is known at `t` equals context at `t` computed from the full data | Unit tests (every minute of a synthetic day); real data: 300 seeded decision times per fixture/sample day |
| AC10-03 | **Causality (future mutation).** Changing any DXY or DX data after `t` leaves context at `t` unchanged | Unit tests + real-data seeded check |
| AC10-04 | **No forward-fill through prohibited missing periods.** (a) Causal: once the causal flag has fired, the quote is NaN and every window intersecting the flagged run is UNAVAILABLE; a quote is never carried beyond `max_quote_age_minutes` or across a session closure; a window with no rows is never given a direction. (b) Hindsight mask: every minute of the ruled intervals 2020-03-09 20:00-21:00 and 2019-03-11 00:00-01:00 is `dq_hindsight_vendor_gap = True`; every 15m/1h window with no quotes in them is UNAVAILABLE | Unit tests + real data |
| AC10-04b | **Hindsight isolation.** Causal fields are identical whether or not the hindsight mask is computed; no causal field depends on data after `t` | Unit test |
| AC10-05 | **No DX substitution.** DX prices never influence any output (changing them changes nothing), and DX can only **remove** values: every numeric context value computed with DX equals the value without DX or is null | Unit test + real data |
| AC10-06 | **Closure handling.** Expected-closed windows → `CLOSED_SCHEDULE`; CFD no-quote periods outside the schedule are never labelled closed (no hypothesized CFD schedule in code) | Unit tests + real data |
| AC10-07 | **Direction correctness.** An independent naive recomputation of every 15m/1h window on real days matches the module | Real data |
| AC10-08 | **Determinism.** Two runs give byte-identical output hashes | Unit test + real data |
| AC10-09 | **Fixture coverage.** All 8 fixture days (course-example day ±1, Saturdays excluded) and all 16 AC-11A sample days processed. 2018 days carry `DX_REFERENCE_UNAVAILABLE` where applicable | Real data |
| AC10-10 | **Comparison vs DX (reporting; concern threshold declared now).** Last-closed 15m and 1h direction agreement between CFD and DX on windows where both are FULL and \|DX move\| ≥ 0.01 (2 DX ticks). Below 0.80 on any timeframe → documented concern (not FAIL: Phase 9 established 15m/1h return correlation, not direction agreement) | Real data |

## 4. Verdict rule

| Verdict | Condition |
|---|---|
| **PASS** | AC10-01…AC10-09 met, AC10-10 at or above the concern threshold, no open concerns |
| **PASS WITH CONCERNS** | AC10-01…AC10-09 met; AC10-10 below threshold and/or documented limitations affecting later use |
| **FAIL** | Any of AC10-01…AC10-09 not met |

Holdout-period fixture days (Oct-Nov 2025) are used for integrity/context checks only and are logged in
`research/holdout-access-log.md`. No trades, no P&L.

## 5. Revision log

| Version | Change | Why |
|---|---|---|
| v1.0 | Criteria and thresholds declared before the module ran on market data | n/a |
| v1.1 | After the first real-data run returned **FAIL**: (1) all `*_utc` output columns are forced to UTC even when every value is NaT; (2) every decision time whose last closed minute has no DX coverage carries reason code `DX_REFERENCE_UNAVAILABLE` | Run 1: AC10-01 failed on fixture 2025-11-09 (a DXY day with no quotes lost the timezone of an all-empty column); AC10-09 failed on both 2018 days (no-quote windows were UNAVAILABLE but nothing showed that DX could not verify them, contrary to D12-3). Both are output defects. **No threshold, state rule or AC10-10 comparison was changed**; AC10-02…AC10-08 and AC10-10 had already passed |
