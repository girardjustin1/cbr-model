# Phase 13 Readiness Checklist

**Doc:** CBR-READY-013 · **Created:** 2026-09-15 (owner ruling D18-12) · **Updated:** 2026-09-15 (D24, fidelity revision) ·
**Status:** FAIL twice. PC2 failed Phase 13 (D26) and PC3 failed Phase 13C (CBR-RUN-013C-1, accepted in D32). Both candidates stay frozen and no PC4 exists. The D32 failure-diagnosis package (OQ-48, OQ-49, OQ-50; eight classified candidate changes, none applied) is with the owner; Phase 14 not authorized

Phase 13 is now **STRATEGY FIDELITY AND BEHAVIORAL PARITY** (D24; gate CBR-ACC-013). It may not run while any
mandatory item in sections A or C is unchecked. Section B (V-1) is **supporting feed-fidelity validation** and no longer
blocks (D24-2). Items are checked only by an owner ruling or a recorded, reproducible result.

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
| 20 | [x] Full suite passing | 504 passed, 1 skipped; ruff clean (D23 commit) | |

## B. V-1: supporting feed-fidelity validation (non-blocking since D24)

Historical FOREXCOM:XAUUSD 1m data for the 2025 course and calibration windows was unavailable: TradingView intraday
export history reached only about one week of 1m bars (FOREXCOM 1m from 2026-09-09; D22, D23). The V-1 tooling, reports
and Dukascopy calibration days are preserved as supporting evidence.

| # | Item (supporting) | Status | Reference |
|---|---|---|---|
| 21 | [ ] FOREXCOM:XAUUSD calibration exports (2025-10-22, 2025-11-11) | **V1_TOM_DATA_INSUFFICIENT**: `references/tom-chart-data` has FOREXCOM:XAUUSD (PROBABLE_FOREXCOM) but 1m only from 2026-09-09; no FOREXCOM 1m bar on either calibration day | `docs/decisions/v1-tom-chart-data-assessment.md` |
| 22 | [ ] FOREXCOM:XAUUSD course-window exports (1m) | same: FOREXCOM 1h covers all three course windows, 1m covers none | same |
| 23 | [ ] Identity screenshots (symbol, feed, chart timezone UTC) | missing (would move Gold identity from PROBABLE to CONFIRMED_FOREXCOM) | protocol §6.3a |
| 24 | [x] Dukascopy comparison data for the calibration dates | D21: 2025-11-11 fetched (24 hour-files, 271,884 ticks); both days pass integrity, deterministic rebuild, STRUCTURE role and manifest-hash checks; 1,380/1,380 scheduled-open minutes each, 0 vendor gaps | `reports/v1-dukascopy-calibration-days.md`; `v1_ingest status` |
| 25 | [ ] Feed calibration complete | not started (`v1_ingest calibrate` refuses); tool now reports all D22-1 measurements | D19-11, D22-1 |
| 26 | [ ] Zero-lag requirement passes | not evaluated | protocol §4.3 |
| 27 | [ ] Numeric V-1 price tolerances frozen | `config/phase13_tolerances.yaml` NOT_FROZEN; no longer a prerequisite (D24): the behavioral run uses structural-event equivalence and the P-4 feed band | D19-11/12, D24 |
| 28 | [ ] Final V-1-based parity authorization | superseded by item 36 (D24); `parity.main()` still refuses the V-1 scoring path | D20-9, D24 |

## C. Behavioral-parity gate (mandatory, D24)

| # | Item | Status | Reference |
|---|---|---|---|
| 29 | [x] Behavioral-parity run protocol and decisions P-1…P-8 approved | D25: approved; P-5 option B as the D25-P5 standard; run spec `config/phase13_behavioral_run.yaml` | `docs/governance/d25-phase13-run-approval.md` |
| 30 | [x] Protocol frozen (hash) and run code committed with tests | frozen at commit `36e096c` (527 passed, 1 skipped; ruff clean); recent Dukascopy absent at freeze | `reports/phase13-freeze-manifest.json` |
| 31 | [x] Recent feed comparison complete (Dukascopy for the P-2 days fetched and validated; agreement rates and feed band reported) | 4 days ready, 0 vendor gaps; zero lag; δ $0.00; τ $0.20; `reports/phase13-feed-comparison.md` | CBR-ACC-013 G; CBR-PROT-013B §7.1 |
| 32 | [x] Higher-timeframe fidelity (FOREXCOM 1h/4h/1D; TVC:DXY 1h) reported | `reports/phase13-higher-timeframe-fidelity.md` | CBR-ACC-013 F; §7.2 |
| 33 | [x] Behavioral-parity runs executed twice with identical result hashes (gate A) | CBR-RUN-013B-2: `f3905430…d063` both runs; spot-check defect 1 recorded in the post-run review | §2 |
| 34 | [x] Every mismatch classified; no unexplained or open implementation mismatch (gates B, D, E) | all classified; no IMPLEMENTATION_BUG in PC2; checking-code defects 2-3 recorded | `reports/phase13-post-run-review.md` §5 |
| 35 | [x] Feed differences documented (gate F) and gate G assessed under the P-5 rule | criterion 9 MET (O-1 reading) | §6, §7.1 |
| 36 | [x] Owner Phase 13 verdict issued (PASS / PASS WITH CONCERNS / FAIL) | **FAIL** accepted by the owner (D26); PC2 permanently frozen as the failed candidate; Phase 13R spec reconciliation opened | `docs/governance/d26-phase13-fail-reconciliation.md` | CBR-ACC-013 §7 |

## D. PC3 scored-parity gate (D31, CBR-PROT-013C v1.1)

| # | Item | Status | Reference |
|---|---|---|---|
| 37 | [x] PC3 created, implemented and frozen (`7032f400…`); PC2 untouched (`4dadc8b9…`) | D29 / D30 | `docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC3.yaml` |
| 38 | [x] Expanded parity set frozen (`a3ee0bd6…`, 4 ENTRY_LEVEL + 3 HOUR_LEVEL + 7 NARRATIVE_ONLY) | D30-11 | `research/examples/parity_set_manifest.json` |
| 39 | [x] CBR-PROT-013C approved and frozen with mappings M-1…M-7 | D31 | `docs/governance/d31-pc3-scored-parity-authorization.md` |
| 40 | [x] Scored run executed twice with identical result hashes | CBR-RUN-013C-1: `718efebd…caef` both runs | `reports/phase13c-run-manifest.json` |
| 41 | [x] Every mismatch classified (22: 1 OWNER_BASELINE_CHOICE, 15 UNRESOLVED_SPEC_AMBIGUITY, 6 CANON_MISMATCH) | STEP 7 register | `reports/phase13c-parity.md` |
| 42 | [x] Owner Phase 13C verdict issued | **FAIL** accepted by the owner (D32); PC3 frozen, no PC4 | `docs/governance/d32-phase13c-failure-diagnosis.md` |
| 43 | [ ] Phase 13C failure diagnosis reviewed | package returned: OQ-48 (HVCS semantics), OQ-49 (journal scope), OQ-50 (evaluation instant), 8 classified candidate changes, none applied | D32 §4-6 |

**Current status (2026-09-16): NOT READY.** Mandatory: 20 of 28 checked (A 20/20; C 0/8). Supporting V-1: 1 of 8
checked. PC3 scored parity **FAILED** (CBR-RUN-013C-1) and the FAIL is accepted (D32); PC3 stays frozen and no PC4
exists. Next step: owner review of the failure-diagnosis package and rulings on OQ-48, OQ-49 and OQ-50 — in
particular whether to restore `hvcs.max_violations` (candidate F-1, the only change ready for a ruling).
