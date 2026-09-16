# D27 Phase 13R Reconciliation Review: Ruling Record

**Doc:** CBR-RULING-D27 · **Date:** 2026-09-15 · **Decided by:** Owner ("OWNER RULING — PHASE 13R RECONCILIATION REVIEW")

## Result

The Phase 13R reconciliation package is **accepted**. PC2 remains frozen as the failed Phase 13 candidate. **PC3 is not
created.** No Phase 13 rerun, no Phase 14, no backtest, no optimization, no P&L inspection, no Astra × Fable review.

The next objective is to resolve the remaining upstream strategy-definition questions **before** any PC3 specification.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D27-1 | D8 extension anchor | **Keep `HOUR_OPEN`.** `LAST_RESET` is not promoted to canonical and stays research/diagnostic only; it may not be used to make the course examples pass. Evidence supports the hour open as the normal reference and allows a later start, but defines no canonical reset rule |
| D27-2 | Early extension / pullback | Accepted as a separate problem: a very small early move can become an active extension, after which a normal opening retracement permanently violates the 50% rule. **No activation value may be chosen yet**; a focused Extension-Activation Evidence Review is required, comparing concepts A-E without selecting numeric thresholds from the three examples. Any number needed for implementation is an ASSUMPTION with a pre-registered research range |
| D27-3 | `M1H-COND-04` | **The current hard gate is not approved for PC3.** Remove it from canonical signal eligibility unless new Level-1 evidence before the PC3 freeze clearly establishes a hard prior-setup gate. Preserve `prior_setup_exists`, `prior_setup_count`, `prior_setup_model`, `prior_setup_age` as diagnostics; Level-2 quality claims are DIAGNOSTIC / RESEARCH-DERIVED context, never a baseline veto. No outcomes or profitability |
| D27-4 | HVCS continuity | **Approved: CANON_CORRECTION.** A conforming candle is decided by structural respect and directional progression, not by candle-body close direction. Indecision candles may exist if they do not structurally invalidate the sequence. No arbitrary maximum indecision count |
| D27-5 | HVCS end time | **Approved: IMPLEMENTATION_FIX.** Evaluate the sequence causally through the entry shift, using information available at the canonical 5-second shift decision time; no future information beyond the shift. Add explicit causality tests |
| D27-6 | Type-3 sweep (T3-1) | **The next required task.** Do not modify the type-3 implementation yet. A dedicated evidence review must determine what Tom teaches, since this is upstream of signal membership |
| D27-7 | T3-1 questions | Ten specified questions (sweep prerequisites, external vs internal take, swing confirmation, SELL/BUY sufficiency, retest requirement, per-model differences, what fixes sweep/trigger time and price, and whether the engine's CX-LT3-2 direction is wrong) |
| D27-8 | T3-1 output | Per interpretation: evidence ids, video, timestamp, exact quote, visual evidence, deterministic machine definition, effect on each course example and on the existing type-3 unit fixtures. Look for independent examples outside the three parity examples; do not choose an interpretation because it recovers CX-LT3-2 |
| D27-9 | Weekend window | No change yet; a focused evidence note, secondary to T3-1. Do not change it merely to make CX-LT3-2 eligible |
| D27-10 | Candidate selection | **No change.** Signal-generation semantics come first |
| D27-11 | O-1 / O-4 | O-1 thresholds did not bind and remain historical for the failed PC2 run; they are not strategy criteria. O-4 is recognized as material: any future PC3 parity protocol must define the exact required trigger components **before** execution, never as an evaluator-defined concept afterwards |
| D27-12 | Checker fixes | Accepted as infrastructure corrections; they do not alter the failed PC2 result. Regression tests preserved |
| D27-13 | Proposed PC3 | After the T3-1 and extension-activation reviews, produce a single grouped change list (CANON_CORRECTION / ASSUMPTION_CHANGE / IMPLEMENTATION_FIX / DIAGNOSTIC_ONLY / NO_CHANGE). Do not implement without owner approval |
| D27-14 | PC3 validation | When PC3 is approved, do not validate only against the same three positive examples. Assemble an expanded independent parity set first (positive type-3 examples, rejected/pass examples, different sessions, both directions, both CBR1H variants, CBR15 where available). No trade outcomes |
| D27-15 | Next task | A: T3-1 review · B: extension-activation review · C: weekend-window note. Then report and stop |

## Deliverables produced under this ruling

| Id | Deliverable | File |
|---|---|---|
| A | T3-1 type-3 sweep evidence review | `docs/decisions/t3-1-type3-sweep-evidence.md` |
| B | Extension-activation evidence review | `docs/decisions/extension-activation-evidence.md` |
| C | Weekend condition-window note | `docs/decisions/weekend-condition-window-note.md` |
| — | Revised proposed PC3 change set (v0.2, not implemented) | `docs/strategy/pc3-proposed-change-set.md` |

All transcript quotes were verified mechanically with the `tests/test_evidence.py` normalizer. Measurements are
STRUCTURE-data diagnostics; the T3 comparison engine is a scratchpad prototype and was never added to `src/`. PC2's
spec hash is unchanged (`4dadc8b9…`).

## Status

PC2 frozen; PC3 not created; Phase 13 not rerun; Phase 14 not authorized. **Stopped for owner review.**
