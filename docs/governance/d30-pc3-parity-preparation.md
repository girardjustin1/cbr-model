# D30 PC3 Implementation Accepted; Parity Preparation: Ruling Record

**Doc:** CBR-RULING-D30 · **Date:** 2026-09-16 · **Decided by:** Owner ("OWNER RULING — PC3 IMPLEMENTATION ACCEPTED / PARITY STILL BLOCKED")

## Result

The PC3 implementation is **accepted as complete for engineering purposes**. PC3 is **READY FOR PARITY PREPARATION**
and **NOT AUTHORIZED FOR SCORED PARITY**. PC2 stays byte-identical and preserved as the failed prior candidate.
No Phase 13C run, no Phase 14, no backtest, no optimization, no P&L, no Astra × Fable review.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D30-1 | PC3 changes | Accepted as implemented, with the classifications as recorded (CANON_CORRECTION: type-3 re-anchoring, whole-extension pullback without latch, structural HVCS, CBR1H prior-setup gate removal, directionless trending-range fallback; ASSUMPTION_CHANGE: extension states, minute-7 earliest activation, Q1 qualifier, duration from activation; IMPLEMENTATION_FIX: HVCS at shift time, timer anchored to the latest sweep extreme; DIAGNOSTIC_ONLY: prior-setup fields; NO_CHANGE: hour-open reference, tradable window, k = 3, no extra type-3 external level, deterministic selection). Not to be modified before parity unless a new evidence defect is found and approved |
| D30-2 | Causality fixes | The two defects (trigger-time HVCS contaminating decision fields; the ledger storing the final re-anchored trigger) are accepted as legitimate implementation bugs, correctly fixed. The wide-bar retracement fix is accepted. All regression tests preserved |
| D30-3 | PC3 status | CBR1H PC3 = **IMPLEMENTED**; CBR15 PC3 = **SPEC_ONLY**. The distinction must remain explicit; CBR15 PC3 is never described as implemented or validated and cannot be scored until an engine binding and a machine-testable example set exist |
| D30-4 | Priority | Complete and freeze the expanded CBR1H parity set before any PC3 scoring |
| D30-5 | Fetch | Continue the authorized resumable fetch for 2025-10-15/16/17/28/29; do not restart valid cached hours; handle 503s with the existing retry/resume logic; report per date: requested hours, downloaded hours, legitimate empty hours, unresolved failures, tick count, duplicates, bad spreads, timestamp integrity, canonical bar build, manifest/hash status. No unresolved failure may disappear silently |
| D30-6 | Journal extraction | For JM-2025-10-16/17/29 freeze only what exists independently of PC3 output: source, evidence level, instrument, UTC hour, session, direction, model label, condition label, CB timing label, positive/negative, and what can actually be scored. Never invent entry, stop, target or second-level trigger |
| D30-7 | Journal scoring scope | HOUR_LEVEL cases: may score setup existence, model family where defined, direction, condition, coarse timing bucket. May **not** score exact 5s trigger, entry, stop or target, and those fields are never inferred from PC3 |
| D30-8 | Original cases | CX-LT1-1, CX-TE1-1, CX-LT3-2 and negative CX-LT3-1 remain the ENTRY_LEVEL machine cases; not scored yet |
| D30-9 | Narrative set | Frozen separately (CX-LT2-2, CX-LT2-1, drawn type-3, HILO valid/invalid, good/bad extension, 2026-05 CBR15 walkthrough); used only for geometry consistency; contributes no machine pass counts |
| D30-10 | 2026-05 CBR15 | Accepted as illustrative with insufficient entry metadata: NARRATIVE_ONLY, no fabricated entry, CBR15 PC3 unscored |
| D30-11 | Parity-set manifest | Immutable manifest with `case_id`, `source`, `evidence_level`, `instrument`, `model`, `direction`, `positive_or_negative`, `session`, `start_time`, `end_time`, `scoring_level` (ENTRY_LEVEL / HOUR_LEVEL / NARRATIVE_ONLY), `source_hashes`, `market_data_hashes`, `fields_allowed_for_scoring`; frozen and hashed before any scored run |
| D30-12 | CBR-PROT-013C | Prepare the final proposed protocol without executing it; hard dimensions defined separately per scoring level (nine for ENTRY_LEVEL positives; supported-only for HOUR_LEVEL; negatives judged against exactly what the source says was rejected) |
| D30-13 | Core trigger | Frozen before the run for both variants (A: context → extension active → extension quality → location → previous-15m take → valid HVCS → 5s type 3 → eligible candidate; B: context → extension active → 1m type-3 parent → required pullback → 5s type 3 → eligible candidate). No post-hoc redefinition |
| D30-14 | Acceptance | No single overall percentage. Categorical acceptance via hard dimensions and case-level verdicts: the original three ENTRY_LEVEL positives keep the previous hard requirement unless a pre-existing approved mismatch class applies; HOUR_LEVEL cases are judged only on source-supported fields; negatives must avoid the specifically rejected behaviour. Proposed for owner approval before execution |
| D30-15 | Candidate selection | Frozen. The run reports both whether the correct structural event exists anywhere in the eligible set and which candidate the frozen rule selects; a mismatch is `CANDIDATE_SELECTION_MISMATCH`, never a type-3 failure, and selection is never changed during the run |
| D30-16 | Assumptions | Minute-7 activation, Q1 qualifier, k = 3, swing confirmation behaviour, tradable-time window and the extension-origin choice stay explicit ASSUMPTIONS. Passing parity does not convert them to CANON; it means only that the translation is faithful enough for baseline testing |
| D30-17 | No sensitivity during parity | No k = 2/4, activation-minute, FINAL_PUSH, LAST_RESET, max_reversal or ranking variations during the scored run |
| D30-18 | Fetch failure rule | Dates that cannot be fully acquired are classified `DATA_LIMITATION` and **retained** in the manifest; no substitution, and never after seeing PC3 output |
| D30-19 | Readiness gate | Twelve checklist items must hold before PC3 is presented for scored-run approval |
| D30-20 | Next report | Twelve items, then stop; no scoring until explicitly authorized |
