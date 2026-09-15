# Phase 13 Readiness Checklist

**Doc:** CBR-READY-013 · **Created:** 2026-09-15 (owner ruling D18-12) · **Updated:** 2026-09-15 (D19 implementation) ·
**Status:** NOT READY

Phase 13 (Tom ↔ Python parity) may not start while any mandatory item is unchecked. Items are checked only by an owner
ruling or a recorded, reproducible result, with the reference noted.

## Spec resolution and implementation

| # | Item | Status | Reference |
|---|---|---|---|
| 1 | [x] OQ-36 resolved | D19-1 (reading C′); formation-based prior-setup rule implemented in both engines | `d19-phase13-readiness-ruling.md`; tests `test_prior_rule_counts_setups_formed…`, `test_prior_setups_count_formation…` |
| 2 | [x] OQ-39 resolved | D19-2 (reading A); 5s shift trigger, variants A/B with separate parent structures | `1h-cbr-machine-spec.md` §6; `cbr1h.py` |
| 3 | [x] OQ-40 owner assumption recorded | D19-3; CBR1H `window_basis = TRADABLE` (ASSUMPTION); clock/tradable/missing minutes recorded | `config/strategy.yaml`; test `test_condition_window_uses_tradable_time…` |
| 4 | [x] OQ-41 resolved | D19-4; Q−1 broken by Q with the sourced exception (CBR1H); tests for the three cases | tests `test_previous_15m_candle_broken_by_q_three_cases`, `test_q_minus_1_must_be_broken_by_q_itself` |
| 5 | [x] OQ-42 evaluation timing resolved | D19-5; evaluated at the 5s shift; hard veto UNRESOLVED and non-blocking (`timing30_state`) | test `test_timing30_is_diagnostic…` |
| 6 | [x] OQ-43 principle resolved | D19-6; HVCS into the shift, structural continuity, no count | test `test_hvcs_into_shift…` |
| 7 | [x] M15-HTF-01 signal/fill split implemented | D19-15; `htf_signal_state` vs `htf_fill_state`, fill never rejects | test `test_htf_signal_state_and_fill_state_are_separate` |
| 8 | [x] D8/D9 switches and parity views implemented | D19-9; switches off by default (hash-identical); one alternative per STRICT COURSE run | tests `test_d8_d9_switches…`, `test_views_baseline_and_one_ablation_at_a_time` |
| 9 | [x] D8/D9 classification policy frozen | D19-8 order implemented; protocol v0.2 pinned in PC1 | `parity.classify_mismatch`; PC1 `selection_protocol` hashes |
| 10 | [x] Candidate-selection rule frozen | D19-10; 5s shift time as primary key; answer-aware runners removed; pinned in PC1 | `parity.selection_key` / `select_candidate`; tests |
| 11 | [x] CBR15 parity-candidate spec frozen | `CBR15_BASELINE_V1-PC1` | `docs/strategy/parity-candidates/CBR15_BASELINE_V1-PC1.yaml`; hash test |
| 12 | [x] CBR1H parity-candidate spec frozen | `CBR1H_BASELINE_V1-PC1` | `docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC1.yaml`; hash test |
| 13 | [x] Causality tests passing | truncation + future mutation at mid-minute cuts for decision and trigger fields (CBR15, CBR1H), timeframe completion, determinism, ledger completeness, causal hourly state | `tests/engine/` |
| 14 | [x] Price-role guard tests passing | engines refuse non-STRUCTURE bars; guard scan | `tests/test_price_series.py`, `tests/engine/` |
| 15 | [x] Full suite passing | 481 passed, 1 skipped; ruff clean (D19 implementation commit) | |
| 16 | [ ] OQ-44 owner review (HVCS indecision continuity reading) | open; CBR1H-A signals carry an eligibility blocker | `open-questions.md` OQ-44 |
| 17 | [ ] OQ-45 owner decision (CBR15 window basis across closures) | open; CBR15 stays CLOCK | `open-questions.md` OQ-45 |

Items 16-17 were raised during D19 implementation. They're listed as mandatory until the owner says otherwise.

## Waits on V-1

| # | Item | Status | Reference |
|---|---|---|---|
| 18 | [ ] V-1 export obtained | not obtained: 5 FOREXCOM:XAUUSD 1m UTC CSVs + screenshots (symbol identity, feed, chart timezone) in `data/raw/tradingview/` | protocol §6 |
| 19 | [ ] Dukascopy ticks for the 2025-11-11 calibration day | not fetched (24 hour-files) | protocol §6.2 |
| 20 | [ ] V-1 calibration completed | not started: `parity.calibrate` on the two non-course days; report n, distribution, median offset (+ per day), p95, max, zero lag | protocol §4.3; D19-11 |
| 21 | [ ] Numeric parity tolerances frozen | `config/phase13_tolerances.yaml` status NOT_FROZEN, values null | D19-11/12 |
| 22 | [ ] Final Phase 13 parity authorized | owner authorization; `parity.main()` refuses until 18-21 are done | D19-20 |

**Current status (2026-09-15): NOT READY.** 15 of 22 items checked. Remaining: OQ-44 and OQ-45 owner decisions, then
V-1 data, calibration, frozen tolerances and final-run authorization. A change to any PC1-pinned file needs PC2 and a
new parity run.
