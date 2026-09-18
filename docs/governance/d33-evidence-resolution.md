# D33 — post-D32 evidence resolution: OQ-48, OQ-50, MTF taxonomy, journal scope

**Doc:** CBR-DEC-033 · **Date:** 2026-09-16 · **Status:** package returned for owner review
**Scope:** evidence resolution only. PC3 frozen and unmodified · PC4 not created · no parity run · no Phase 13 rerun ·
no Phase 14 · no backtest · no optimization · no P&L or trade outcome · no Backtesting.py · no Astra × Fable review.

The CBR-RUN-013C-1 verdict stands as executed: **FAIL**. Nothing in this package reinterprets or overwrites it.

---

## 1. Deliverables (D33 §19)

| | Deliverable | Where |
|---|---|---|
| 1 | OQ-48 independent Level-1 evidence inventory | `reports/oq48-independent-examples.md` (+ `.json`); `docs/decisions/oq48-hvcs-duration-evidence.md` §8 |
| 2 | HVCS interpretation comparison on independent examples | same, §9 |
| 3 | Recommended OQ-48 ruling | same, §10 |
| 4 | OQ-50 evidence review | `docs/decisions/oq50-previous-15m-evaluation-time.md` |
| 5 | Recommended previous-15m evaluation time | same, §4 |
| 6 | Recommended definition of Q | same, §5 |
| 7 | Complete MTF model taxonomy | `docs/decisions/mtf-model-taxonomy.md` |
| 8 | JM-2025-10-16 scope ruling | same, §3 |
| 9 | JM-2025-10-17 scope ruling | same, §4 |
| 10 | JM-2025-10-29 source interpretation | same, §5 |
| 11 | Corrected future CBR1H parity-set proposal | `research/examples/cbr1h-parity-set-proposal.md` |
| 12 | F-1 implementation plan | `docs/governance/f1-max-violations-implementation-plan.md` |
| 13 | Proposed PC4 change list by classification | §3 below |
| 14 | Remaining unresolved questions | §4 below |
| 15 | PC4 readiness verdict | §5 below |

Measurement code: `src/cbr/engine/oq48_examples.py` — reads stored 1-minute bars only, runs no engine, touches no
parity case.

## 2. The finding that matters most

Two Level-1 examples outside the parity set were located with **legible chart dates**, and both days' data is held:

- **HX-1** — `V1H-seconds_shift_1m_hilo_hvcs` @ 00:02:06, the lesson that *defines* the HVCS, 2025-10-23 ≈ 05:18-05:26 UTC.
- **HX-2** — `V1H-candle_behavior_extension` @ 00:03:38, "the high volume counter sequence into a high low entry", 2025-10-29 ≈ 02:29-02:36 UTC.

Each is a sequence Tom points at and calls valid. Each is 8-9 candles long and contains **exactly one** structural
violation — a single higher high of $0.70 and $0.25 inside an obvious push.

**PC3 measures 1 conforming minute on both.** Every reading without the violation tolerance is INCONSISTENT with both
examples (1-3 minutes against a canon minimum of 4). The two readings with `hvcs.max_violations = 1` restored measure
**9 and 10** and are CONSISTENT with both. The run anchor makes no difference to either example.

This confirms **F-1 from independent evidence**, and F-1 was approved before these measurements existed. It also
means the remaining OQ-48 questions — anchor, inclusive counting, unit — are not what broke the rule.

## 3. Proposed PC4 change list by classification (D33 §16)

| Id | Change | Classification | Status |
|---|---|---|---|
| **F-1** | Restore `hvcs.max_violations = 1` in the HVCS run | **IMPLEMENTATION_FIX** | **Approved (D33 §1); plan ready** (`f1-max-violations-implementation-plan.md`). Must ship inside PC4 |
| **F-9** | Evaluate `M1H-6A-2` and `M1H-6A-3` at the 5s shift instead of at the type-3 arm | **CANON_CORRECTION** | **Recommended** (`oq50…` §4). Rests on E1H-003's step order and E1H-034, not on any parity case; the type-3 arm has no counterpart in the course vocabulary |
| **F-10** | Define `Q` as the 15m candle containing the final shift | **ASSUMPTION** | **Recommended** (`oq50…` §5), deterministic, consistent with both independent examples |
| **F-11** | Record the OQ-48 anchor (run ends at the extension extreme known at the shift), exclusive first-candle counting, and candle-count units as explicit ASSUMPTIONS | **ASSUMPTION_CHANGE** (documentation of an existing choice) | **Recommended** (`oq48…` §10.2). Status quo, chosen because it cannot have been picked to recover examples. **Disclosure:** it leaves CX-LT3-2's HVCS at 0 minutes; the alternative anchor would give 4 |
| **F-5** | Move JM-2025-10-17 out of the CBR1H machine set (IFS is not implemented), preserved for a future model | **PARITY_SET_CORRECTION** | **Recommended** (`mtf-model-taxonomy.md` §4) |
| **F-6** | Downgrade JM-2025-10-29 to NARRATIVE / REFERENCE ONLY | **PARITY_SET_CORRECTION** (SOURCE_AMBIGUITY) | **Recommended** (same, §5) |
| **F-12** | Keep JM-2025-10-16 as a CONFIRMED_CBR1H hour-level case; its condition disagreement feeds OQ-01 | **NO_CHANGE** to rules; parity-set field addition (`model_scope`) | **Recommended** (same, §3) |
| **F-2 / F-3** | HVCS shift-anchor; inclusive counting | **CANON_CORRECTION / ASSUMPTION_CHANGE** if adopted | **Not recommended.** Superseded by F-11 unless the owner reads the rule's name and D19-6 as evidence for the anchor (`oq48…` §10.4) |
| **F-4** | Move `M1H-LOC-*` and `M1H-OE-01` to the trigger instant | — | **Withdrawn for now.** No Level-1 evidence ties them to the entry instant; it was proposed from CX-LT3-2 alone, which D33 forbids |
| **F-7** | ATR-zig-zag `k` / condition-classifier disagreement (JM-2025-10-16) | **NO_CHANGE**; feeds OQ-01 | unchanged |
| **F-8** | Type-3 re-anchoring, sweep-extreme timer, whole-extension pullback, PRE_EXTENSION/EXTENSION_ACTIVE, minute-7 activation, Q1 qualifier, HOUR_OPEN, k = 3, directionless trending range → RANGE, candidate selection, tradable-time window, prior-setup gate removal | **NO_CHANGE** | Explicitly not reopened (D33 §17). Nothing found in this review contradicts them |

## 4. Remaining unresolved questions (D33 §19.14)

1. **OQ-48 anchor.** Extension extreme vs the shift. Not discriminated by any example; the recommendation is the
   status quo, with the consequence for CX-LT3-2 disclosed.
2. **OQ-50 scope.** Whether `M1H-LOC-*` and `M1H-OE-01` follow `M1H-6A-2/-3` to the trigger instant.
3. **The D19-4 exception × F-10.** How "Q−1 closed in the trade direction" interacts with anchoring Q to the shift.
4. **FS / IFS.** Extend CBR1H with a fractal-shift context, or specify a separate model? Tom trades three MTF models;
   the project implements two.
5. **Journal `Condition = Volume`.** No engine field corresponds; journal condition values cannot be scored until
   this is settled.
6. **Journal column semantics.** Whether the time column is entry, observation or logging time, and whether `Setup`
   or a separate column carries the MTF label.
7. **HX-1 / HX-2 admissibility.** They were used as evidence to resolve OQ-48, so scoring the same rule against them
   later would be circular (`cbr1h-parity-set-proposal.md` §C).
8. **Boundary frequency** for F-10: how often a shift lands in the first minutes of a new 15m candle. Measurable from
   existing diagnostics, but only under an authorized run.

## 5. Readiness verdict (D33 §19.15)

### PC4 IS NOT READY FOR OWNER APPROVAL.

One change is ready (**F-1**, approved, planned, evidence-confirmed independently). Two more are recommended with
Level-1 support (**F-9**, **F-10**) and three are parity-set corrections (**F-5**, **F-6**, **F-12**). But a candidate
cannot be specified while:

- the **OQ-48 anchor** is unsettled — it decides whether `M1H-6A-1` passes on CX-LT3-2, and the recommendation and
  the alternative differ on exactly that;
- the **OQ-50 scope** is unsettled — F-9 covers two rules, and whether `M1H-LOC-*` / `M1H-OE-01` join them changes
  the candidate's behaviour;
- the **parity set** has not been re-approved — a candidate should be frozen against a set whose scope is known, and
  the corrected set is a proposal.

Those are four owner rulings, not further research. Once they are made, PC4 can be specified in one pass: F-1 plus
whatever F-9/F-10/F-11 the owner approves, with the corrected parity set frozen alongside it and the two-layer
reporting pre-declared before any run.

## 6. Stop

Package returned for owner review. PC3 unchanged, PC4 not created, no parity run, Phase 14 unauthorized.
