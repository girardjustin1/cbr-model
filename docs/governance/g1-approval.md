# G1 Data Gate: Approval Record

**Doc:** CBR-GATE-G1 · **Date:** 2026-09-14 · **Decided by:** Owner (ruling D12) · **Phase:** 9 → 10

## Result

**PHASE 9: PASS WITH CONCERNS.** G1 **APPROVED WITH CONDITIONS.**

The owner issued rulings D12-1 through D12-6, and the full acceptance suite was then rerun
(`reports/phase9-data-acceptance.md`, CBR-ACC-009 v2.1):

| Owner condition for G1 | Rerun result |
|---|---|
| AC-01…AC-06 remain MET | MET (AC-06 now also checks the candle high/low error bound on every tick-window minute) |
| AC-07 contains only detected/classified missing source data; no unresolved pipeline defect | MET WITH CONCERNS: 0 PIPELINE_ERROR; the 2 ruled items are flagged by `DXY_CFD_MISSING_WHILE_DX_ACTIVE` |
| AC-08 and AC-10 remain MET | MET |
| AC-09 remains MET WITH CONCERNS | MET WITH CONCERNS |
| AC-11A remains MET WITH CONCERNS | MET WITH CONCERNS |
| AC-11B remains deferred | DEFERRED: 16 / 2,192 weekdays per instrument |
| All 408+ tests pass | 416 pass |

Failures: 51 in total, 0 unclassified, 0 blocking, all 51 preserved as concerns. No sample day was dropped, and no threshold was changed.

## Owner rulings (D12)

| Id | Item | Ruling |
|---|---|---|
| D12-1 | 2020-03-09 DXY CFD 20:00-20:59 UTC, empty source file while DX traded 56 min | Confirmed `DATA_ERROR` (source-data defect). Interval is **MISSING**: no forward-fill, no interpolation, no prices synthesized from DX, no DXY structure inferred across it. Setups whose required context intersects it get reason code `DXY_CFD_MISSING_WHILE_DX_ACTIVE` and lower confidence. A generic automated detector is required |
| D12-2 | 2019-03-11 DXY CFD 00:00-00:59 UTC, no ticks while DX traded 31 min | Kept `UNEXPLAINED_FEED_DIFFERENCE`; no explanation invented. Interval is **MISSING** under the same rules. The DST-Monday diagnostic is approved but not required for Phase 9. It must be completed before DXY availability assumptions are frozen for baselines (OQ-27) |
| D12-3 | 2018 DXY days: no DX reference before 2018-12-26 | New class `REFERENCE_UNAVAILABLE` (not EXPECTED_FEED_DIFFERENCE). No cross-feed agreement is claimed for those dates, and the limitation stays visible downstream |
| D12-4 | 2020-06-17 XAUUSD vs GC, 1m corr 0.920 | `EXPECTED_FEED_DIFFERENCE`, `cause_status: HYPOTHESIZED`. Observations are recorded separately; the EFP-volatility narrative is not evidence |
| D12-5 | Candle-file high/low construction (SIDE_EXTREME_MEAN) | **Hard safeguard before baseline backtesting** (see below and OQ-25) |
| D12-6 | DXY timeframe implications | Dukascopy DXY supports 15m/1h direction and broader inverse context. 1m and 5s DXY structure are **not** validated; they need an independent reference before entering the canonical strategy (OQ-26) |

## D12-5 safeguard (binding)

- A. Candle open and close may be used where validated (AC-03: identical to tick-built bars).
- B. Every bar file carries `hl_method`: `SIDE_EXTREME_MEAN` for candle files, `TICK_MID` for tick-built bars. **Done.**
- C. For parity windows and any signal requiring precise extremes, canonical highs and lows come from tick-built bars or
  another validated source.
- D. **Before Phase 14**, the canonical historical OHLC source must be defined for swing detection, range highs/lows,
  extension extremes, stop placement, and liquidity sweep/take detection (OQ-25, gate G2d).
- E. If full-history baselines rely on candle-file highs/lows, the issue must be resolved, or shown quantitatively not to
  change signal membership or material execution results.
- F. Test for artificial extremes from non-synchronous bid/ask highs/lows: `tests/test_data_quality.py`. **Done.**

Measured so far on 10 tick-window pairs:
- Artificial minutes (candle extreme beyond the tick-mid extreme by more than 0.05 for XAUUSD / 0.005 for DXY): 0-28 per XAUUSD window and 0-67 per DXY window.
- Largest error: $0.425 (XAUUSD) and 0.3185 (DXY).
- The candle-only warning flag (`CANDLE_HL_SYNTHETIC_EXTREME_SUSPECT`, ratio declared before measurement) catches spread spikes but **misses most artificial minutes**. It is not a sufficient safeguard on its own.

## What G1 means

"The historical-data pipeline is sufficiently trustworthy to proceed with model-engineering work, subject to documented
feed limitations and missing-data safeguards."

## What G1 does NOT mean

- complete spot history has been acquired (AC-11B deferred)
- futures and spot are interchangeable
- DXY fine structure (1m, 5s) has been validated
- candle-file extremes are safe for baseline trading logic
- OQ-24 (baseline feed) has been resolved

## Phase 10 authorization (scope)

Phase 10 builds the **DXY context module** within the current evidence:

- missing periods remain missing; no interpolation across missing DXY data
- availability and confidence are explicit outputs, with deterministic reason codes (`DXY_CFD_MISSING_WHILE_DX_ACTIVE`)
- 15m/1h DXY context is treated as better supported than 1m/5s structure
- no research-derived DXY trading filter is optimized

Not authorized: baseline profitability testing · resolving OQ-24 using performance · inspecting holdout P&L · starting
the Astra × Fable Phase 17 review.
