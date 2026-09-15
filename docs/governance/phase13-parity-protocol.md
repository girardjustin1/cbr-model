# Phase 13 Parity Protocol (proposal for owner approval)

**Doc:** CBR-PROT-013 · **Version:** v0.1 PROPOSED · **Date:** 2026-09-15 · **Ruling:** D18-7…D18-11
**Status:** NOT FROZEN. Nothing here takes effect until the owner approves it. Numeric tolerance values are set from V-1
non-course data (§4.3) **before** the final parity run, never from engine output on the course examples.

---

## 1. Scope

Phase 13 compares the reference engines with Tom's taught course examples on **signal state** (context, direction,
extension, timing, structure trigger, entry activation/trigger time, stop-anchor inputs, target inputs, acceptance).
**Execution state** (fills, filled hourly veto, P&L) is out of scope (D18-11). No outcomes, P&L or optimization.

Course-example windows are in the holdout period: parity use only, logged in `research/holdout-access-log.md`.

## 2. Two parity views (D18-7)

| View | Engine configuration | Purpose |
|---|---|---|
| **BASELINE-SPEC PARITY** | Frozen V1 specs exactly as approved (D8 `oe_origin = HOUR_OPEN`, D9 `early_shift_guard = NONE`, all resolved rulings) | Does the implementation reproduce the frozen baseline faithfully? |
| **STRICT COURSE PARITY** | The same engine, with each **pre-registered** D8/D9 alternative switched on **one at a time**: `oe_origin = LAST_RESET`; `early_shift_guard = FINAL_PUSH`; `early_shift_guard = ALIGN_15M`. No other change, no combinations | Shows what the deliberate V1 exclusions cost against the course, without hiding it |

Rules:
- Only settings already declared in `config/strategy.yaml → ablations` (research_range) may appear in STRICT COURSE PARITY.
- These runs are parity diagnostics on the course windows only (no outcomes). They do **not** execute the Phase 17/18
  experiments and don't change the baseline.
- **Not yet implemented.** The engines don't have these switches today. They must be added (off by default, baseline
  `spec_hash` unchanged) before STRICT COURSE PARITY can run: readiness item 18.

## 3. Mismatch classification (D18-7)

Every comparison dimension that doesn't match gets exactly one class. The first applicable class in this order wins, and
the evidence for it is recorded.

| Order | Class | Assign when |
|---|---|---|
| 1 | `DATA_LIMITATION` | The engine can't evaluate the dimension from stored data: missing or insufficient bars, warm-up not covered, a vendor gap flagged (`DXY_CFD_MISSING_WHILE_DX_ACTIVE` or an XAU equivalent) |
| 2 | `FEED_DIFFERENCE` | The difference is within the frozen V-1 tolerance (§4), or disappears when the same STRUCTURE computation runs on the V-1 FOREXCOM bars for that dimension (1m-and-coarser structure only) |
| 3 | `EXECUTION_DEPENDENT` | The dimension needs fill information (e.g. a fill-time rule under OQ-42 if so classified; the FILLED component of M15-HTF-01) |
| 4 | `OWNER_BASELINE_CHOICE` | The mismatch exists in BASELINE-SPEC PARITY and disappears when exactly one pre-registered D8/D9 alternative is switched on in STRICT COURSE PARITY |
| 5 | `UNRESOLVED_SPEC_AMBIGUITY` | The deciding rule is governed by an open question (at freeze time none should remain; any that do block readiness) |
| 6 | `IMPLEMENTATION_BUG` | The engine output contradicts the frozen machine spec (reproduced by a failing unit test) |
| 7 | `CANON_MISMATCH` | The engine follows the frozen spec and its Level 1 evidence, yet the example differs (Tom deviating from his own taught rule, or discretion: manual target, management) |

`IMPLEMENTATION_BUG` blocks G2 until fixed. `CANON_MISMATCH` rows cite the evidence showing the rule and the example.

## 4. Tolerances (D18-8)

### 4.1 What they compare

| Quantity | Engine side | Course side |
|---|---|---|
| Price levels (trigger, stop anchor, target inputs, extension/range extremes, Tom's labelled prices) | Dukascopy tick-mid STRUCTURE price | FOREXCOM:XAUUSD (V-1 export; Tom's chart labels) |
| Times (extension extreme bar, trigger/touch, activation) | UTC bar/tick time | Tom's chart times (UTC+11 → UTC), V-1 bar times |

### 4.2 Independent inputs already measured (not from engine closeness to Tom)

| Input | Value | Source |
|---|---|---|
| FOREXCOM quote precision on TradingView XAUUSD | 0.01 | chart price scale (to confirm in V-1 export) |
| Dukascopy tick-mid precision | 0.0005 | tick decimals (Phase 9) |
| Dukascopy half-spread (bid vs mid) per day, median | $0.11-0.39 | `reports/oq25-extrema-evidence.md` (21 days, non-engine) |
| Candle-file vs tick-mid extreme error | 2.0% of minutes > $0.05 | same (explains why candle files aren't used) |
| Structure bar resolution | 5 s (entries), 1 m (extension, HVCS/HILO) | D2, primitives §0 |
| Tom's time references | position-tool x-axis hover to the second; journal rows to the minute | `research/examples/course_examples.jsonl` price/time sources |

The three Phase 9 AC-10 Tom-label comparisons (−1.759, −0.005, +0.445) come from course-example labels. They're shown for
context only and **don't set any tolerance**.

### 4.3 Frozen formulas (values computed from V-1 non-course windows before the final run)

- **Level offset** `δ` = median over V-1 **non-course** minutes of (FOREXCOM close − Dukascopy tick-mid close), per
  calibration day. If the day-to-day spread of `δ` exceeds its own p95 dispersion, no offset is removed and this is
  reported.
- **Price tolerance** `τ_p` = max(0.02, p95 over non-course minutes of |(FOREXCOM high/low/close − Dukascopy mid
  high/low/close) − δ|), rounded **up** to the next $0.05.
  - `FEED_NEAR` band = `3 × τ_p` (reported, never counted as a match).
- **Bar alignment** check: best lag of 1m close-to-close returns between FOREXCOM and Dukascopy on non-course minutes
  must be 0 minutes. Otherwise V-1 fails and parity doesn't start.
- **Time tolerance** `τ_t`:
  - 1m-resolution events (extension extreme bar, HVCS/HILO bars): same bar, i.e. ±0 bars, after lag check;
  - Tom's position-tool entry times: ±60 s (minute rows) or ±15 s where the tool shows seconds, fixed per example from
    its recorded source type, not from engine output.
- **Structure point match**: same kind (H/L), extreme bar within ±1 bar of its tier, price within `τ_p`.

The computed values, the calibration days and their data hashes are written into this document and the readiness
checklist item 8 is checked **before** the final parity run. After that they can't change.

## 5. Candidate selection (D18-9)

The engine may emit several candidates per hour or 15m candle. Parity compares the course example with **one**
engine-selected candidate, chosen only from engine-available information:

1. **Eligible set:** candidates with event `ARMED` in the view being scored (§2), for the example's model and its
   canonical variant(s) (CBR1H: each variant scored separately, never merged).
2. **Ordering:** earliest decision time; ties by earliest order activation time; then the spec's primary HILO tier
   (1m before 5m); then `prior` before `same`; then `signal_id`.
3. **Selected candidate:** the first in that order. This mirrors the specs' "at most one filled trade per hourly candle" (1h spec §1) and "one position per model" (primitives §8): the first valid order is the one that would be live. The Phase 9 parity notes (F-2) recorded the same V1 reading ("V1 takes the first valid signal").
4. **No eligible candidate:** the example is scored "no signal" (acceptance mismatch). As a diagnostic, the report also
   shows the first candidate, in the same ordering, whose failed rules all carry classes 1-5 of §3. It's labelled
   `DIAGNOSTIC_ONLY` and never counts as a match.
5. Tom's entry time, price or outcome is **never** an input to selection.

## 6. V-1 acquisition (D18-10)

### 6.1 Required export

| Setting | Value |
|---|---|
| Symbol | `FOREXCOM:XAUUSD` (TradingView "Gold Spot / U.S. Dollar", the feed on Tom's charts) |
| Timeframe | **1 minute** |
| Chart timezone | **UTC** (Chart settings → Symbol → Timezone → UTC) before exporting |
| Session | Regular / all hours (no session filter) |
| Method | Chart menu → **Export chart data…** (CSV; "ISO time" format if offered). Load the full window on screen first (scroll or Bar Replay / Go to date) so every bar is in the export |
| Also capture | a screenshot of the symbol info panel (data vendor, price scale) and the chart settings showing UTC |

### 6.2 Windows (UTC)

| File name | From | To | Purpose |
|---|---|---|---|
| `v1_CX-LT1-1.csv` | 2025-10-20 15:00 | 2025-10-21 03:00 | CX-LT1-1 hour + 8 h condition window + 10 h prior lookback |
| `v1_CX-TE1-1.csv` | 2025-10-23 18:00 | 2025-10-24 06:00 | CX-TE1-1 (same coverage) |
| `v1_CX-LT3-2.csv` | 2025-11-07 12:00 | 2025-11-10 04:00 | CX-LT3-2, including Friday for the OQ-40 window readings |
| `v1_cal_2025-10-22.csv` | 2025-10-22 00:00 | 2025-10-23 00:00 | **Non-course calibration day** (tolerances §4.3) |
| `v1_cal_2025-11-11.csv` | 2025-11-11 00:00 | 2025-11-12 00:00 | **Non-course calibration day** |

Dukascopy ticks for all of these dates are already stored except the 2025-11-11 calibration day, which would need one small
targeted fetch (24 hour-files, no bulk download). Calibration days fall in the holdout period
and are used for data fidelity only.

### 6.3 Known risk

TradingView limits how far back 1m bars load depending on the account plan. October-November 2025 is about 11 months
before today. If 1m history doesn't reach these dates:
- export whatever 1m history exists for those dates, plus 5m bars for the full windows;
- record `DATA_LIMITATION` for 1m-only checks;
- tell the owner. The requirement stays hard; this may block Phase 13.

Place files in `data/raw/tradingview/` (gitignored). No TradingView data is committed.

### 6.4 V-1 checks (data fidelity only)

Open, high, low, close agreement after `δ`; bar alignment (lag 0); key structure extremes (extension extremes, range
boundaries over the condition windows, swing points at 1m/5m) on both feeds; Tom's labelled prices vs both feeds. Any
difference that changes **signal membership** on a course example stops Phase 13 and reopens OQ-25 (D18-10).
