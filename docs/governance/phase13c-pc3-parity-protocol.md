# Phase 13C PC3 Parity Protocol (FINAL PROPOSAL)

**Doc:** CBR-PROT-013C · **Version:** v1.0 **PROPOSED** · **Date:** 2026-09-16 · **Rulings:** D29 §25, D30 §12-15
**Gate:** CBR-ACC-013C · **Status:** NOT APPROVED, NOT EXECUTED. PC3 exists, is frozen and has **never been scored**
against any parity case. Nothing here runs until the owner approves this protocol and the §10 decisions.

Inherited unchanged: the two parity views, deterministic answer-independent candidate selection, the mismatch taxonomy
and its order, structural-event equivalence (D25-P3), the feed-band method (D25-P4), DXY as descriptive only.

**Spec under test:** `CBR1H_BASELINE_V1-PC3` (spec hash `7032f400…`). `CBR15_BASELINE_V1-PC3` is **SPEC_ONLY** and is
**out of scope** (D30-3). **Parity set:** `research/examples/parity_set_manifest.json`, manifest hash `a3ee0bd6…`.

---

## 1. The core trigger, frozen before execution (D30-13)

No evaluator may redefine these after seeing results.

**CBR1H variant A (HVCS_S5_SHIFT)**

`CONTEXT → EXTENSION_ACTIVE → EXTENSION QUALITY → LOCATION → PREVIOUS-15M TAKE → VALID HVCS → 5S TYPE-3 SHIFT → ELIGIBLE CANDIDATE`

| Step | Machine condition (PC3) |
|---|---|
| CONTEXT | `M1H-COND-01`, `M1H-COND-02` (after the OQ-46 fallback) |
| EXTENSION_ACTIVE | `M1H-OE-00-ACTIVE`: activation at or after minute 7 by the Q1 qualifier |
| EXTENSION QUALITY | `M1H-OE-01` (≥ 20 min from activation), `M1H-OE-02` (deepest retracement < 50% of the active extension), `M1H-OE-04a`, `M1H-OE-04b` |
| LOCATION | `M1H-LOC-01` / `-02` / `-03` as the condition dictates (`-04` for AOI variants) |
| PREVIOUS-15M TAKE | `M1H-6A-2-PREV-15M-BROKEN-BY-Q`, `M1H-6A-3-NEW-EXTREME-IN-Q` |
| VALID HVCS | `M1H-6A-1-HVCS-INTO-SHIFT`, evaluated at the 5s shift decision time |
| 5S TYPE-3 SHIFT | a re-anchored 5s type 3 opposing the extension whose trigger breaks inside the entry window (`M1H-TIME-01`, `NT_*`, `IMPL-REWARD`) |
| ELIGIBLE CANDIDATE | `event_at_trigger = ARMED_AT_TRIGGER` |

**CBR1H variant B (FRACTAL_1M_S5_SHIFT)**

`CONTEXT → EXTENSION_ACTIVE → 1M TYPE-3 PARENT → REQUIRED PULLBACK → 5S TYPE-3 SHIFT → ELIGIBLE CANDIDATE`

Steps 1-2 and the quality/location/previous-candle steps as above, then `M1H-6B-1-T3-AFTER-OE` (completed re-anchored
1m type 3 inside the hour, known at its break bar's close), `M1H-6B-3-PULLBACK` (≥ 50% retrace on closed 5s bars), then
the 5s shift. Variant B carries no HVCS rule.

## 2. Hard dimensions by scoring level (D30-12)

### 2.1 ENTRY_LEVEL positives (CX-LT1-1, CX-TE1-1, CX-LT3-2)

| # | Hard dimension |
|---|---|
| 1 | Model family |
| 2 | Direction |
| 3 | Condition compatibility |
| 4 | Extension direction |
| 5 | Extension activation |
| 6 | Location / previous-candle event |
| 7 | Required HVCS state for the variant |
| 8 | Type-3 / 5s structural trigger (D25-P3 equivalence) |
| 9 | Eligible candidate existence |

Supporting (reported, never aggregated into a score): trigger time and price, stop-anchor concept, target concept, DXY.

### 2.2 HOUR_LEVEL positives (JM-2025-10-16, JM-2025-10-17, JM-2025-10-29)

Only source-supported fields (D30-7):

| # | Dimension | Source field |
|---|---|---|
| 1 | Setup exists during the declared hour | journal row exists for that hour |
| 2 | Direction | journal Buy/Sell |
| 3 | Model family if source-defined | TRR CT / TRR PT / IFS |
| 4 | Condition if source-defined | Trending / Volume |
| 5 | Timing bucket if source-defined | CB hour 37 / 52 (bucketed, not exact) |

**Never scored:** exact 5s trigger, entry, stop, target — and never inferred from PC3 output.

### 2.3 Negative cases

`CX-LT3-1`: no eligible candidate whose 5s shift falls in the rejected window 2025-11-10 01:28-01:36 UTC, judged
against exactly what the source says was rejected (an early, too-small seconds shift). `CX-LT2-1` is narrative.

### 2.4 NARRATIVE_ONLY

Geometry consistency only: CONSISTENT / INCONSISTENT / NOT_DETERMINABLE. Never a machine pass count.

## 3. Proposed acceptance rules (D30-14; for owner approval, categorical, no overall percentage)

| Id | Rule |
|---|---|
| **A-1** | **ENTRY_LEVEL positives:** all three must match hard dimensions 1, 2, 4 and 8 (model family, direction, extension direction, core trigger) unless a pre-existing approved mismatch class applies (FEED_DIFFERENCE by D25-P3; OWNER_BASELINE_CHOICE by D8/D9). This preserves the previous requirement |
| **A-2** | **ENTRY_LEVEL positives, remaining hard dimensions** (3, 5, 6, 7, 9): each mismatch is classified and reported; an unclassified mismatch is a FAIL |
| **A-3** | **HOUR_LEVEL positives:** each case is `HOUR_MATCH` when the declared hour contains an eligible candidate in the stated direction, `HOUR_MISMATCH` otherwise. Model family, condition and timing bucket are reported per case and classified when they differ. **No threshold is proposed for how many of the three must match**: the owner sets it, because three journal-sourced cases are a small and newly added sample |
| **A-4** | **Negative:** CX-LT3-1 must produce no eligible candidate in its window. A signal there is a FAIL unless classified as an approved mismatch class |
| **A-5** | **Gate A/B:** the complete run is repeated with identical result hashes; PC3 and PC2 hashes unchanged; the full suite passes on the run commit |
| **A-6** | **Selection:** `CANDIDATE_SELECTION_MISMATCH` never counts as a trigger failure (§4) and is returned for owner review |
| **A-7** | **Verdict:** PASS only if A-1, A-4 and A-5 hold with no unclassified mismatch and no concern; PASS WITH CONCERNS if they hold with documented classified mismatches; FAIL if a hard dimension fails without an approved class, an implementation bug is open, or determinism fails |

**Owner must set before execution:** the A-3 threshold, and whether HOUR_LEVEL results can affect the overall verdict
at all or are reported as supporting evidence only.

## 4. Candidate selection (D30-15)

The selection algorithm stays frozen. For every case the run reports **both**:

- **A.** whether the correct structural event exists **anywhere** in the eligible candidate set;
- **B.** which candidate the frozen selection rule actually chooses.

If A is true and B differs, the case is `CANDIDATE_SELECTION_MISMATCH` — never a type-3 failure. Selection is never
changed during the run.

## 5. Assumptions carried through parity (D30-16)

Minute-7 earliest activation · Q1 qualifier · ATR zig-zag k = 3 · swing-confirmation behaviour · tradable-time condition
window · the extension-origin choice (most adverse price before activation). **Passing parity does not convert any of
these into CANON.** It means only that PC3 is a sufficiently faithful executable translation to begin baseline testing.

## 6. Prohibited during the run (D30-17)

No k = 2/4, no alternative activation minutes, no FINAL_PUSH or LAST_RESET, no alternative `max_reversal`, no
alternative candidate rankings, no optimization, no P&L, no outcome data, no parameter change, no post-hoc trigger
redefinition, and no informal answer-aware adjustment of PC3.

## 7. Execution order (when approved)

1. Freeze: protocol hash, PC3 hashes, parity-set manifest hash, market-data hashes; full suite run.
2. Machine set (7 cases: 4 ENTRY_LEVEL, 3 HOUR_LEVEL), twice, identical result hashes.
3. Narrative set assessed qualitatively (7 cases).
4. Classification register and per-case verdicts, including selection reporting.
5. Report, then **STOP** for the owner's Phase 13C verdict.

## 8. Outputs

`reports/phase13c-parity.{md,json}` · `reports/phase13c-run-manifest.json` (protocol, PC3, parity-set and data hashes;
both result hashes) · a mismatch register · a selection register.

## 9. Known limits to state in the report

- The machine set is XAUUSD-only, CBR1H-only, 7 cases (6 positive, 1 negative), two sessions.
- The three HOUR_LEVEL cases come from Tom's journal table in a Level-1 frame — weaker than a narrated walkthrough —
  and carry no prices.
- CBR15 is unscored (SPEC_ONLY).
- `k = 3` is fixed; CX-LT3-2's trigger is known to disappear at k = 4.
- PC3 carries six unresolved assumptions recorded in its spec record.

## 10. Owner decisions required before the run

| Id | Decision |
|---|---|
| C-1 | Approve this protocol and the §1 trigger compositions |
| C-2 | Approve the §2 hard dimensions per scoring level |
| C-3 | Approve the §3 acceptance rules and set the A-3 threshold |
| C-4 | Decide whether HOUR_LEVEL cases affect the verdict or are supporting evidence only |
| C-5 | Confirm CBR15 stays out of scope |
| C-6 | Confirm the parity set is frozen as inventoried (manifest hash `a3ee0bd6…`), including cases PC3 may fail |
| C-7 | Authorize the scored run, which is the only step that lets PC3 see the parity cases |
