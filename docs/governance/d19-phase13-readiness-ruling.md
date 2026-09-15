# D19 Phase 13 Readiness / Spec Resolution: Ruling Record

**Doc:** CBR-RULING-D19 · **Date:** 2026-09-15 · **Decided by:** Owner (ruling D19) · **Phase:** 13 readiness (implementation)

## Result

Evidence packages (CBR-EVD-036, CBR-EVD-039, CBR-EVD-040) and the proposed parity protocol accepted for review.
OQ-36 and OQ-39…OQ-43 resolved enough to update the machine specs. **Phase 13 remains NOT READY.** The final parity
run waits on V-1, independent calibration, frozen numeric tolerances and owner authorization.

## Rulings

| Id | Item | Ruling | Implemented as |
|---|---|---|---|
| D19-1 | OQ-36 prior setup | Reading C′. Hard requirement = a qualifying same-model prior setup EXISTS (formed) in the lookback; "played out" diagnostic only; no target/structure/touch/fill termination. Models separate; any CBR1H numeric lookback not in Level 1 is ASSUMPTION | CBR15 `[Q.t0 − 60 min, Q.t0)`, CBR1H `[H.t0 − 10 h, H.t0)` (ASSUMPTION); `prior_setup_exists/count/latest_time/played_out_status=UNKNOWN`; raw-setup outcome resolution removed |
| D19-2 | OQ-39 entry trigger | Reading A. The 5s shift is the canonical CBR1H trigger; variants A (HVCS → shift → 5s trigger) and B (1m type 3 → pullback → 5s shift) kept distinct; a 1m HILO is an observable equivalent / parent only | Candidates are 5s type 3 sweeps; `entry_model`, `parent_structure_type/time`, `five_second_shift_time/level`, `activation_time`; HILO-tier rule removed; `m1_hilo_armed_at_decision` diagnostic |
| D19-3 | OQ-40 condition window | ASSUMPTION: scheduled closures don't consume the window; vendor gaps stay missing data; record clock, tradable and missing minutes | CBR1H `cond.window_basis = TRADABLE`; three duration fields. CBR15 unchanged (OQ-45) |
| D19-4 | OQ-41 previous 15m candle | Q−1 = previous completed 15m candle; the break must be made by Q; trade-direction exception encoded where Level 1 supports it; tests for the three cases | `M1H-6A-2-PREV-15M-BROKEN-BY-Q` (exception: E1H-023, V1H-1m_fractal_shift 00:03:23); CBR15 `M15-LOC-04` confirmed, no exception |
| D19-5 | OQ-42 :30 timing | Evaluated at the 5s shift / entry-trigger time. Hard veto vs quality downgrade UNRESOLVED: diagnostic `timing30_state`; never rejects | `timing30_state` ∈ PASS / QUALITY_CONCERN / NOT_APPLICABLE / UNRESOLVED; `M1H-TIME-02` removed from rules |
| D19-6 | OQ-43 HVCS end bar | HVCS runs directly into the shift and ends at the final displacement bar; no invented indecision count; open a question if a number is needed | End bar = closed 1m bar that set the extension extreme; continuity = indecision bars keep the respected side; `hvcs_gap_bars`; OQ-44 opened for review |
| D19-7 | Parity protocol | Approved in principle (views, deterministic selection, taxonomy, tolerance method, calibration days, V-1); numeric tolerances not frozen | Protocol v0.2; `src/cbr/engine/parity.py`; `config/phase13_tolerances.yaml` (NOT_FROZEN) |
| D19-8 | Classification order | DATA_LIMITATION → FEED_DIFFERENCE → EXECUTION_DEPENDENT → OWNER_BASELINE_CHOICE → UNRESOLVED_SPEC_AMBIGUITY → IMPLEMENTATION_BUG → CANON_MISMATCH; one primary; secondary tags allowed; bugs never concealed | `parity.classify_mismatch` |
| D19-9 | Two parity views | BASELINE-SPEC and STRICT COURSE reported separately; OWNER_BASELINE_CHOICE still reported | `parity.view_params`, `parity.strict_course_ablations`; D8/D9 switches in CBR1H |
| D19-10 | Candidate selection | Deterministic, engine-only, per variant; 5s trigger time as the primary key; remove "closest to Tom" | `parity.selection_key`, `parity.select_candidate`; `phase12_run.py` and `readiness_diagnostics.py` removed |
| D19-11 | Price tolerance | Method approved: δ robust offset; τ_p = max($0.02, p95 residual) rounded up to $0.05; document n, distribution, median, p95, max, zero lag before freezing | `parity.calibrate` |
| D19-12 | Time tolerance | Same 1m bar; ±60 s without seconds; ±15 s with seconds; report feed time offsets | `parity.compare_time` |
| D19-13 | V-1 | Hard gate; exact symbol, timeframe, timezone, windows, screenshots; no symbol substitution | Protocol §6; `parity.final_run_blockers` |
| D19-14 | V-1 availability failure | Not waived: DATA_LIMITATION + alternative FOREXCOM sources; blocked until done or replacement approved | Protocol §6.3 |
| D19-15 | M15-HTF-01 | `HTF_SIGNAL_STATE` vs `HTF_FILL_STATE`; fill NOT_EVALUATED = EXECUTION_DEPENDENT; no contamination of signal parity; CBR15 not fully eligible | `htf_signal_state` (rule), `htf_fill_state`, blocker `HTF_FILL_STATE_EXECUTION_DEPENDENT` |
| D19-16 | Required engine changes | CBR15 and CBR1H lists; no :30 hard veto; no HVCS count | As above; CBR15 `five_second_shift_time`, `trigger_mic`, `trigger_timing_state` |
| D19-17 | Causality re-run | Truncation, future mutation, timeframe completion, guards, determinism, ledger completeness; no 1m leakage into 5s | Tests in `tests/engine/` (mid-minute cut tests) |
| D19-18 | Spec freeze | PARITY-CANDIDATE specs with version, evidence hash, decisions, CANON/ASSUMPTION parameters, unresolved and execution-dependent rules; frozen during parity | `docs/strategy/parity-candidates/*-PC1.yaml`, `src/cbr/engine/freeze_specs.py`, hash test |
| D19-19 | Checklist | Update after implementation; V-1-dependent items stay unchecked | `docs/governance/phase13-readiness.md` |
| D19-20 | Next task | Readiness implementation only; no final parity scoring | — |

Standing constraints: no profitability, optimization, holdout P&L, Backtesting.py or Astra × Fable review.
