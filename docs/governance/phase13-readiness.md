# Phase 13 Readiness Checklist

**Doc:** CBR-READY-013 · **Created:** 2026-09-15 (owner ruling D18-12) · **Updated:** 2026-09-15 (D22, TradingView export inspection) ·
**Status:** NOT READY

Phase 13 (Tom ↔ Python parity) may not start while any mandatory item is unchecked. Items are checked only by an owner
ruling or a recorded, reproducible result, with the reference noted.

## A. Spec resolution and implementation

| # | Item | Status | Reference |
|---|---|---|---|
| 1 | [x] OQ-36 resolved | D19-1 (reading C′) | `d19-phase13-readiness-ruling.md` |
| 2 | [x] "Setup formed" semantics | D20-1; `raw_setup_armed`, non-recursive, no fill/outcome | tests `test_prior_setup_formed_without_its_own_prior_requirement_*` |
| 3 | [x] CBR1H prior-window endpoint | D20-2; [H.t0 − 10 h, H.t0) (10 h ASSUMPTION); window fields recorded | test `test_current_hour_setups_never_satisfy_that_hours_prior_requirement` |
| 4 | [x] OQ-39 resolved | D19-2; 5s shift trigger, variants A/B separate | `1h-cbr-machine-spec.md` §6 |
| 5 | [x] OQ-40 owner assumption recorded | D19-3; CBR1H tradable-time window | test `test_condition_window_uses_tradable_time_across_the_weekend` |
| 6 | [x] OQ-41 resolved | D19-4; Q−1 broken by Q (CBR1H exception sourced) | test `test_previous_15m_candle_broken_by_q_three_cases` |
| 7 | [x] CBR15 Q−1 exception interpretation | D20-3; no exception, no transfer by analogy | test `test_cbr15_q_minus_1_has_no_trade_direction_exception` |
| 8 | [x] OQ-42 evaluation timing resolved | D19-5; at the 5s shift; hard veto unresolved, diagnostic only | test `test_timing30_is_diagnostic…` |
| 9 | [x] OQ-43 principle resolved | D19-6 | `hvcs_into_shift` |
| 10 | [x] OQ-44 resolved as ASSUMPTION | D20-4; continuity diagnostics, never filters; blocker removed | test `test_hvcs_continuity_is_deterministic_future_safe_and_diagnostic_only` |
| 11 | [x] OQ-45 resolved as ASSUMPTION | D20-5; CBR15 tradable-market time; vendor gaps stay visible | test `test_cbr15_condition_window_uses_tradable_time_and_keeps_vendor_gaps` |
| 12 | [x] M15-HTF-01 signal/fill split | D19-15, D20-6; fill NOT_EVALUATED = EXECUTION_DEPENDENT | test `test_htf_signal_state_and_fill_state_are_separate` |
| 13 | [x] D8/D9 switches and parity views | D19-9 | tests `test_d8_d9_switches…`, `test_views_baseline_and_one_ablation_at_a_time` |
| 14 | [x] D8/D9 classification policy frozen | D19-8; pinned in PC2 | `parity.classify_mismatch` |
| 15 | [x] Candidate-selection rule frozen | D19-10; pinned in PC2 | `parity.selection_key` / `select_candidate` |
| 16 | [x] CBR15 parity-candidate spec frozen | `CBR15_BASELINE_V1-PC2` (PC1 kept for audit) | `docs/strategy/parity-candidates/`; hash tests |
| 17 | [x] CBR1H parity-candidate spec frozen | `CBR1H_BASELINE_V1-PC2` (PC1 kept for audit) | same |
| 18 | [x] Causality tests passing | truncation + future mutation at mid-minute cuts (decision and trigger fields), timeframe completion, HVCS future-safety, determinism, ledger completeness | `tests/engine/` |
| 19 | [x] Price-role guard tests passing | engines refuse non-STRUCTURE bars; guard scan | `tests/test_price_series.py`, `tests/engine/` |
| 20 | [x] Full suite passing | 502 passed, 1 skipped; ruff clean (D22 commit) | |

## B. Waits on V-1 and owner authorization

| # | Item | Status | Reference |
|---|---|---|---|
| 21 | [ ] FOREXCOM:XAUUSD calibration exports (`v1_cal_2025-10-22.csv`, `v1_cal_2025-11-11.csv`) | **V1_SYMBOL_MISMATCH**: supplied Gold exports are FX:XAUUSD; 1m history starts 2026-09-08 | `docs/decisions/v1-tradingview-exports-assessment.md` |
| 22 | [ ] FOREXCOM:XAUUSD course-window exports (`v1_CX-LT1-1.csv`, `v1_CX-TE1-1.csv`, `v1_CX-LT3-2.csv`) | same | same |
| 23 | [ ] Identity screenshots (symbol, feed, chart timezone UTC) | missing | protocol §6.3a |
| 24 | [x] Dukascopy comparison data for the calibration dates | D21: 2025-11-11 fetched (24 hour-files, 271,884 ticks); both days pass integrity, deterministic rebuild, STRUCTURE role and manifest-hash checks; 1,380/1,380 scheduled-open minutes each, 0 vendor gaps | `reports/v1-dukascopy-calibration-days.md`; `v1_ingest status` |
| 25 | [ ] Feed calibration complete | not started (`v1_ingest calibrate` refuses); tool now reports all D22-1 measurements | D19-11, D22-1 |
| 26 | [ ] Zero-lag requirement passes | not evaluated | protocol §4.3 |
| 27 | [ ] Numeric price tolerances frozen before course scoring | `config/phase13_tolerances.yaml` NOT_FROZEN | D19-11/12 |
| 28 | [ ] Final Phase 13 authorization issued | not issued; `parity.main()` refuses | D20-9 |

**Owner-supplied charts (2026-09-15).** `references/charts` holds `FX:XAUUSD` and `TVC:DXY` exports; the 1m file starts
2026-09-08, so no FOREXCOM:XAUUSD 1m export covers the V-1 windows: **DATA_LIMITATION** (`reports/v1-export-inspection.md`).
Not substituted (D19-13/14).

**Current status (2026-09-15): NOT READY.** 21 of 28 items checked. Unchecked: 21 FOREXCOM calibration exports, 22 FOREXCOM
course-window exports, 23 screenshots, 25 feed calibration, 26 zero-lag check, 27 numeric tolerances frozen, 28 final
Phase 13 authorization. V-1 state: `V1_SYMBOL_MISMATCH` (secondary `ONE_MINUTE_HISTORY_INSUFFICIENT`).
