# D26 Phase 13 FAIL Accepted; Phase 13R Spec Reconciliation: Ruling Record

**Doc:** CBR-RULING-D26 · **Date:** 2026-09-15 · **Decided by:** Owner ("OWNER RULING — PHASE 13 FAIL / SPEC
RECONCILIATION REQUIRED")

## Result

The Phase 13 verdict is accepted as **FAIL** under frozen protocol CBR-PROT-013B and frozen PC2. The result establishes
that **PC2 does not yet reproduce the core structural trigger demonstrated in the three positive course examples**. It
is **not** evidence that CBR has no edge.

**Phase 14 is not authorized.** No profitability, no execution simulation, no Backtesting.py, no optimization, no
Astra × Fable research review.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D26-1 | Run incident | The handling of CBR-RUN-013B-1 is accepted: infrastructure-only fix (timestamp normalization), regression test added, source data reused under verified hashes, re-frozen before the substantive run. **CBR-RUN-013B-2 is the first substantive result-producing Phase 13 run.** RUN-013B-1 is preserved as an incident record |
| D26-2 | Phase 13 result | Accepted: model family, direction and extension direction correct on 3/3; **core structural trigger failed on 3/3**; the frozen acceptance rule correctly produces FAIL. The acceptance rule is **not** weakened after the fact |
| D26-3 | Feed differences | The feed study is accepted as strong evidence that normal FOREXCOM vs Dukascopy differences are **not** the primary explanation. Missing structural triggers may not be classified broadly as FEED_DIFFERENCE without event-level proof |
| D26-4 | PC2 | **Permanently frozen** as the failed Phase 13 candidate; kept for audit; never edited. Any strategy-definition change requires **PC3** with a new decision record, evidence justification, changed-rule list, new hashes and a newly approved parity run |
| D26-5 | Next stage | **Phase 13R — Spec Reconciliation**: determine why the engine's trigger state machine differs from the taught examples, without selecting rules because they make examples pass. Not optimization |
| D26-6 | D8 | Dedicated evidence review of what starts the hourly extension (hour open / last reset / final push / other), each with source, video, timestamp, verbatim quote, chart evidence, machine definition and effect on all course examples. `LAST_RESET` may not be chosen merely because it matches two examples |
| D26-7 | M1H-COND-04 | Dedicated evidence review: whether a prior setup is required at all, its type, direction, model, actual lookback, and whether Tom treats it as a hard gate or descriptive context. Neither remove it because it rejects the examples nor keep it because it exists |
| D26-8 | M1H-6A-1 | Dedicated evidence review of "HVCS runs directly into the shift", inspecting the visual sequences at CX-LT1-1 and CX-TE1-1. No invented indecision-bar count; no weakening merely because candidates fail |
| D26-9 | CX-LT3-2 | Separate rule-by-rule causal event reconstruction identifying the **first** semantic disagreement. No arbitrary parameter trials |
| D26-10 | Candidate selection | Frozen for now; reopened only if Level-1 evidence supports it, after signal generation is reconciled. Never select the candidate closest to Tom's entry |
| D26-11 | Checker defects | Fix the three reporting/checker defects (5s causality spot check at bar close; owner-determination labelling; stop-gap classification) plus the lint warning, with regression tests. Phase 13 infrastructure, no PC3 required. **No rescored Phase 13 run** until PC3 is separately approved |
| D26-12 | O-1…O-8 | Short audit of each pre-run reading: evidence source, owner approval, effect on acceptance, whether it remains, whether a new ruling is needed. D25 thresholds are not changed retroactively |
| D26-13 | Output | Deliverables A-G, each proposed PC3 change classified CANON_CORRECTION / ASSUMPTION_CHANGE / IMPLEMENTATION_FIX / NO_CHANGE with reasons. PC3 not implemented |
| D26-14 | Stop condition | Stop for owner review after the reconciliation package. No PC3, no Phase 13 rerun, no Phase 14, no backtest |

## Deliverables produced under this ruling

| Id | Deliverable | File |
|---|---|---|
| A | D8 extension-anchor evidence review | `docs/decisions/d8-extension-anchor-evidence.md` |
| B | M1H-COND-04 prior-setup evidence review | `docs/decisions/cond04-prior-setup-evidence.md` |
| C | HVCS-continuity evidence review | `docs/decisions/hvcs-continuity-evidence.md` |
| D | CX-LT3-2 event reconstruction | `reports/phase13r-cx-lt3-2-reconstruction.md` |
| E | O-1…O-8 audit | `docs/governance/phase13-o1-o8-audit.md` |
| F | Checker-fix report | `reports/phase13-checker-fix-report.md` |
| G | Proposed PC3 change set (not implemented) | `docs/strategy/pc3-proposed-change-set.md` |

All transcript quotes in A, B, C and D were verified mechanically against the stored transcripts with the
`tests/test_evidence.py` normalizer: **29/29 verified, 0 failures**, cited timestamps within 10 s.

## Status after this package

Phase 13 remains **FAIL**. PC2 is frozen and preserved. The Phase 13 run code refuses to run (frozen inputs changed by
the approved checker fixes), which is the intended guard: a future scored run needs PC3 approval and a new freeze.
**Stopped for owner review.**
