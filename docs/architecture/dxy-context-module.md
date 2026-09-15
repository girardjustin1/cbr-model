# DXY Context Module (Phase 10)

**Doc:** CBR-ARCH-010 · **Version:** v1.0 · 2026-09-14 · **Code:** `src/cbr/dxy/context.py` · **Config:**
`config/dxy_context.yaml` · **Acceptance:** CBR-ACC-010 → `reports/phase10-dxy-context.md`

DXY is context only, not a traded instrument (D7). This module produces **primitives** that the Phase 11/12 engines and
later Phase 17/18 experiments can consume. It contains **no** DXY trading rule, filter, veto or confluence decision (D14).

## Data flow

```
Dukascopy DOLLARIDXUSD 1m candles (open, close only; Phase 9 validated)      config/dxy_context.yaml
Databento DX 1m bars (volume only → vendor-gap flag; prices never read)      config/data_quality.yaml (detector thresholds)
Session calendar (weekend + daily 17:00-18:00 New York, DST-aware)            src/cbr/data/sessions.py
        │
        ▼
build_context(dxy, grid, loaded, dx, dx_range) ── one row per UTC decision time (XAU 1m or 5s bar close)
        │
        ├── causal fields  dxy_*            ← the only fields an engine may read
        └── hindsight mask dq_hindsight_*   ← whole-span detector; ledger/data-quality use only (OQ-31)
```

## Causality contract

- A 1m row with open time `m` is known at decision time `t` iff `m + 1 min ≤ t`. DX activity follows the same rule.
- No price enters a window from outside it. A quote is never carried beyond `max_quote_age_minutes`, across a session
  closure or across a causal vendor-gap flag.
- Minutes outside the loaded CFD range are `NOT_LOADED`, never `NO_QUOTES`.
- The vendor-gap flag is evaluated on runs **truncated at `t`**, so it fires only once 30 no-quote minutes with 15 active
  DX minutes have actually elapsed.
- Tests: truncation equivalence, future mutation, hindsight isolation (unit + 300 seeded times × 24 real days).

## Output fields

| Field | Meaning |
|---|---|
| `dxy_context_version` | `DXY_CONTEXT_V1` |
| `dxy_close`, `dxy_quote_close_utc`, `dxy_quote_age_s` | Last known DXY close and its age (NaN when stale, closed or flagged) |
| `dxy_available`, `dxy_confidence` | Quote usable; FULL (age 0) / REDUCED (0 < age ≤ 10 min) / UNAVAILABLE |
| `dxy_{15m,1h}_last_{open_utc,direction,move,state,confidence,coverage,rows}` | Last **closed** candle (close = `floor(t, tf)`) |
| `dxy_{15m,1h}_forming_{open_utc,elapsed_min,direction,move,state,confidence,coverage,rows}` | **Forming** candle as of `t` (same-candle view, E15-042) |
| `dxy_reason_codes` | Sorted `;`-joined codes, window codes prefixed `15m_last:` etc. |
| `dq_hindsight_vendor_gap`, `dq_hindsight_{tf}_{last,forming}_vendor_gap` | Hindsight mask (uses future data; never an engine input) |

Direction = `UP` / `DOWN` / `FLAT` from close − open (`flat_epsilon` 0).

States: `NO_ELAPSED_TIME`, `NOT_LOADED`, `CLOSED_SCHEDULE`, `VENDOR_MISSING`, `NO_QUOTES` → UNAVAILABLE ·
`LOW_COVERAGE`, `UNVERIFIED_GAP` → REDUCED · `OK` → FULL.

Reason codes: `DXY_WINDOW_NOT_STARTED`, `DXY_NOT_LOADED`, `DXY_SESSION_CLOSED`, `DXY_CFD_MISSING_WHILE_DX_ACTIVE`,
`DXY_NO_QUOTES`, `DXY_LOW_COVERAGE`, `DX_REFERENCE_UNAVAILABLE`, `DXY_QUOTE_STALE`.

## Explicitly not provided

DXY highs/lows and extension extremes (OQ-25) · DXY range condition · DXY type-3 or other structure shifts · 1m/5s DXY
structure (D12-6) · inversion, veto or confluence decisions (`CBR15-DXY-001/003`, EP2-026/029: Phase 17/18 ablations) ·
any DX-derived price.
