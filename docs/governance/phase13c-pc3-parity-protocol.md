# Phase 13C PC3 Parity Protocol (PROPOSED)

**Doc:** CBR-PROT-013C · **Version:** v0.1 **PROPOSED** · **Date:** 2026-09-16 · **Ruling:** D29 §25 · **Gate:** CBR-ACC-013C
**Status:** NOT APPROVED. Nothing here runs until the owner approves this protocol and the decisions in §9. PC3 exists
and is frozen; **PC3 has not been scored against any course example** and must not be until this protocol is approved
and the expanded parity set is frozen (D29-20, D29-27).

Inherited unchanged from CBR-PROT-013B / D25: the two parity views, deterministic answer-independent candidate
selection, the mismatch taxonomy and its order, the structural-event equivalence rule (D25-P3), the feed-band method
(D25-P4) and the classification of DXY as descriptive only.

---

## 1. What this protocol fixes before execution (D29-25, D28 §11 on O-4)

The core-trigger composition is defined **here, before any run**. No evaluator discretion after the run.

### 1.1 CBR1H variant A (HVCS_S5_SHIFT)

An **eligible candidate** exists only when every step holds, in this order:

| # | Step | Machine condition (PC3) |
|---|---|---|
| 1 | CONTEXT | `M1H-COND-01` and `M1H-COND-02` on the hour's condition (RANGE or TRENDING_RANGE, after the OQ-46 fallback) |
| 2 | EXTENSION ACTIVE | `extension_state = EXTENSION_ACTIVE` (`M1H-OE-00-ACTIVE`), activated at or after minute 7 by the Q1 qualifier |
| 3 | EXTENSION QUALITY | `M1H-OE-01` (duration ≥ 20 min from activation), `M1H-OE-02` (deepest retracement < 50% of the active extension), `M1H-OE-04a`, `M1H-OE-04b` |
| 4 | REQUIRED LOCATION | `M1H-LOC-01` / `-02` / `-03` as the condition dictates (and `-04` for AOI variants) |
| 5 | PREVIOUS-CANDLE EVENT | `M1H-6A-2-PREV-15M-BROKEN-BY-Q` and `M1H-6A-3-NEW-EXTREME-IN-Q` |
| 6 | TYPE-3 / 5S SHIFT | a re-anchored 5s type 3 in the extension-opposing direction whose trigger **breaks** inside the entry window (`M1H-TIME-01`, `NT_*`, `IMPL-REWARD`) |
| 7 | HVCS VALID **at the shift** | `M1H-6A-1-HVCS-INTO-SHIFT` evaluated at the 5s shift decision time (D29-11) |
| — | ELIGIBLE CANDIDATE | `event_at_trigger = ARMED_AT_TRIGGER` |

### 1.2 CBR1H variant B (FRACTAL_1M_S5_SHIFT)

Steps 1-5 as above, then:

| # | Step | Machine condition |
|---|---|---|
| 6 | 1M TYPE-3 PARENT | a completed re-anchored 1m type 3 inside the hour, recognised at its break bar's close, with `M1H-6B-1-T3-AFTER-OE` |
| 7 | REQUIRED PULLBACK | `M1H-6B-3-PULLBACK`: ≥ 50% retrace of the parent impulse on closed 5s bars |
| 8 | 5S SHIFT | the re-anchored 5s type 3 inside that pullback, trigger broken in the entry window |
| — | ELIGIBLE CANDIDATE | `event_at_trigger = ARMED_AT_TRIGGER` (variant B carries no HVCS rule) |

### 1.3 CBR15

CBR15-PC3 is **spec-only** (the engine binding is not implemented) and is therefore **out of scope for scoring** in
this protocol. If the owner wants CBR15 scored, the engine must be implemented and this protocol extended with the
CBR15 composition before any run.

## 2. Verdict vocabulary

| Outcome | Meaning |
|---|---|
| `STRUCTURAL_MATCH` | the eligible candidate reproduces the example's core trigger (direction, extension direction, D25-P3-equivalent shift) |
| `STRUCTURAL_MATCH_WITH_FEED_DIFFERENCE` | as above, prices or times differ within the feed band |
| `CANDIDATE_SELECTION_MISMATCH` | PC3 produces the correct structural event **but** the frozen selection rule picks a different earlier eligible candidate (D29-17) — reported separately, never fixed during the run |
| `RULE_MISMATCH` | an eligible candidate does not exist; the first failing step in §1 is named |
| `IMPLEMENTATION_BUG` | PC3 contradicts its own spec, reproduced by a failing test |
| `NOT_DETERMINABLE` | the example lacks the data or metadata to decide |

Per-example verdicts aggregate by severity: `IMPLEMENTATION_BUG` > `RULE_MISMATCH` > `CANDIDATE_SELECTION_MISMATCH` >
`STRUCTURAL_MATCH_WITH_FEED_DIFFERENCE` > `STRUCTURAL_MATCH`.

## 3. Sets and how each is used

| Set | Contents | Contributes to pass counts? |
|---|---|---|
| MACHINE PARITY SET | examples with date, time, direction and Dukascopy coverage | yes |
| NARRATIVE / GEOMETRY SET | course examples without sufficient data | **no** — geometry consistency only, reported as CONSISTENT / INCONSISTENT / NOT DETERMINABLE |

The inventory and labels live in `research/examples/expanded-parity-set-inventory.md` and must be **frozen by hash**
before the run (D29-27).

## 4. Hour-level vs entry-level examples

The three journal-derived XAUUSD examples carry date, local time, direction, MTF model, condition and CB-hour timing,
but **no entry price or stop**. They are therefore scored at **hour level**:

- expected: an eligible candidate in the stated hour, in the stated direction, triggered by a seconds shift;
- not expected: a price match, because none is recorded.

The four original examples keep entry-level scoring (price and time, D25-P3 tolerances).

## 5. Acceptance (proposed, for owner decision)

Defined **before** the run, in the D25-P5 style:

| Id | Criterion |
|---|---|
| A | Causal and deterministic: full suite passes on the PC3 commit; the complete run is repeated with identical result hashes |
| B | PC3 frozen: the PC3 hash test passes before and after; PC2 untouched |
| C | Core trigger on the original three positives: model family, direction, extension direction and the §1 core trigger |
| D | The negative controls produce no eligible candidate in their windows |
| E | Every mismatch classified with one primary class and cited evidence |
| F | Feed differences documented |
| G | Selection mismatches reported separately, not silently fixed |

**Thresholds are for the owner to set before execution** (the D28 §11 lesson on O-4). No numbers are proposed here.

## 6. Order of execution

1. Owner approves this protocol and §9.
2. Freeze: protocol hash, PC3 hashes, expanded-set inventory hash, data hashes; run the full test suite.
3. Machine set runs, twice, with identical result hashes.
4. Narrative set assessed qualitatively.
5. Classification register and per-example verdicts.
6. Report, then **STOP** for the owner's Phase 13C verdict.

## 7. What must not happen

No optimization, no P&L, no outcome data, no parameter change during the run, no selection change, no evaluator-defined
trigger composition after the fact, and no informal answer-aware adjustment of PC3 (D29-20).

## 8. Known limits to state in the report

- The machine set is XAUUSD-only and CBR1H-only; CBR15 is unscored.
- The three journal examples are hour-level, and their source is Tom's journal table seen in a Level-1 frame.
- `k = 3` is fixed for this cycle (D29-26); CX-LT3-2's trigger is known to disappear at k = 4.
- PC3 carries six unresolved assumptions (listed in its spec record), including the extension origin price and the
  earliest-activation minute.

## 9. Owner decisions required before the run

| Id | Decision |
|---|---|
| C-1 | Approve this protocol and the §1 trigger compositions |
| C-2 | Approve the §2 verdict vocabulary, including `CANDIDATE_SELECTION_MISMATCH` |
| C-3 | Set the §5 acceptance thresholds (how many of each set must match, and what makes a FAIL) |
| C-4 | Confirm hour-level scoring for the journal-derived examples (§4) |
| C-5 | Confirm that CBR15 stays out of scope until its engine exists |
| C-6 | Confirm the expanded set is frozen as inventoried, including examples PC3 may fail |
