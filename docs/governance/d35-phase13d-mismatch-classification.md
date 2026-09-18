# Phase 13D — STEP 7 mismatch classification register (CBR-RUN-013D-1)

**Doc:** CBR-REG-013D · **Date:** 2026-09-17 · **Ruling:** D35 §14 (STEP 7 of §18)
**Status:** classification of the completed run. The run artefacts (`data/phase13d/run-*.json`,
`reports/phase13d-parity.*`) are **unchanged**; this register assigns the single primary classification each scored
mismatch carries, with its reason. **It does not change the verdict**, which is FAIL either way, because
`UNRESOLVED_SPEC_AMBIGUITY` is not one of the frozen protocol's approved non-failing classes (only FEED_DIFFERENCE
per D25-P3 and OWNER_BASELINE_CHOICE per D8/D9 are).

The runner records `CANON_MISMATCH` as its default severity for any mismatch it cannot attribute. Where the failing
quantity is a carried ASSUMPTION, CBR-PROT-013D §4 requires the primary class to be `UNRESOLVED_SPEC_AMBIGUITY`
instead. D35 §14 forbids using that class to conceal an implementation defect; §3 below shows why no defect is being
concealed here.

---

## 1. The register

| # | Case | Dimension | Hard | Primary class | Failing quantity, and why that class |
|---|---|---|---|---|---|
| 1 | CX-LT3-2 | 3 condition | no | **OWNER_BASELINE_CHOICE** | PC4 keeps PC3's approved OQ-46 correction (D29-14), which classifies the hour `RANGE`; D25-P6's accepted set named `TRENDING_RANGE UP`. The divergence is an owner-approved baseline choice, not a model error |
| 2 | CX-LT3-2 | 7 hvcs_state | **yes** | **UNRESOLVED_SPEC_AMBIGUITY** | The run measures **0** conforming minutes because, at the shift instant, the extension-extreme bar (01:37) itself breaks the respected side. The failing quantity is the **run anchor**, which D34 §3 kept unchanged and F-11 records as an explicit ASSUMPTION under OQ-48. Canon does not state the anchor |
| 3 | CX-LT3-2 | 9 eligible_candidate | **yes** | **UNRESOLVED_SPEC_AMBIGUITY** | Consequence of #2 plus `M1H-OE-01`: the extension measures 16 minutes against a 20-minute minimum **at the decision instant**. Both inputs are assumption-dependent — the anchor (#2) and the minute-7 activation the duration is measured from, with the decision-time evaluation kept deliberately by D35 §5 |
| 4 | JM-2025-10-16 | setup_exists_in_hour | no | **UNRESOLVED_SPEC_AMBIGUITY** | Every candidate in the hour fails `M1H-COND-01` / `M1H-COND-02`: the classifier finds **2** MTF zig-zag legs and returns `UNDEFINED`, so nothing can arm. The failing quantity is leg detection under ATR zig-zag **k = 3**, an ASSUMPTION carried since PC2 and already open as OQ-01 |
| 5 | JM-2025-10-16 | direction | no | **UNRESOLVED_SPEC_AMBIGUITY** | Same cause as #4 — no eligible candidate exists to carry a direction. Note the engine **does** produce SELL candidates in the hour, including one whose 5s shift is 00:41:20, which matches the journal's recorded 00:41 |
| 6 | JM-2025-10-16 | model_family | no | **UNRESOLVED_SPEC_AMBIGUITY** | Same cause as #4 |
| 7 | JM-2025-10-16 | condition | no | **UNRESOLVED_SPEC_AMBIGUITY** | Same cause as #4; the hour never reaches a scored condition because it classifies `UNDEFINED` |
| 8 | JM-2025-10-16 | timing_bucket | no | **UNRESOLVED_SPEC_AMBIGUITY** | Same cause as #4 |

By class: OWNER_BASELINE_CHOICE 1 · UNRESOLVED_SPEC_AMBIGUITY 7 · CANON_MISMATCH 0 · IMPLEMENTATION_BUG 0. Every
mismatch has exactly one primary class; none is unclassified.

## 2. What is **not** in this register

No `IMPLEMENTATION_BUG`, and no mismatch affecting signal membership on CX-LT1-1 or CX-TE1-1: both scored clean on
all nine dimensions in the STRICT view. The negative control produced no eligible candidate. No
`CANDIDATE_SELECTION_MISMATCH` arose: on the two clean cases the frozen selector chose the expected candidate, and
on CX-LT3-2 no eligible expected event existed for the selector to miss.

## 3. Why UNRESOLVED_SPEC_AMBIGUITY conceals no defect here (D35 §14)

The implementation defect that dominated Phase 13C — the dropped `hvcs.max_violations` — was fixed as F-1, and this
run demonstrates the fix working on real data: the HVCS run measures **6** minutes on CX-LT1-1 and **4** on
CX-TE1-1, where PC3 measured 3 and 2 and rejected both. Those numbers reproduce the D32 diagnostic's prediction for
the extreme anchor with the tolerance restored (6, 4, 0) **exactly**, including the 0 on CX-LT3-2.

That 0 is not a defect in the code: it is the documented consequence of the anchor the owner deliberately kept in
D34 §3. It was disclosed in advance, in D33 §10.3, before any PC4 code existed:

> "On the *parity* cases measured in D32, the recommended set (extreme anchor + tolerance) gives 6, 4 and **0** —
> CX-LT3-2's HVCS would still fail … I am **not** recommending the anchor that turns CX-LT3-2 green."

The alternative anchor (`HVCS_TO_SHIFT`) was preserved as a diagnostic precisely so this could be revisited on
evidence rather than on results. Nothing in this run changes that position, and no change is proposed here.

## 4. First causal divergence for each failed binding case (D35 §10)

**CX-LT3-2.** The candidate carrying Tom's geometry is `…/A/20251110T0100/SELL/3`, 5s shift **01:39:40** against a
stated entry of ~01:40:00 — direction, extension direction, activation, location, previous-15m event and the type-3
trigger all agree. The first divergence is at the HVCS gate evaluated at that shift: the conforming run anchored at
the extension-extreme bar is **0 minutes** against a canon minimum of 4, because the extreme bar breaks the
respected side. `M1H-OE-01` (16 minutes from the assumed activation against a 20-minute minimum, measured at the
decision instant) is a second, independent blocker on the same candidate.

**JM-2025-10-16.** The first divergence is **upstream of every entry rule**: the hour classifies `UNDEFINED` on 2
MTF zig-zag legs, so `M1H-COND-01` / `M1H-COND-02` fail on all five candidates and none can arm. The engine does
produce a SELL candidate whose 5s shift (00:41:20) matches the journal's recorded time, and that candidate's only
other blocker is the same HVCS gate as CX-LT3-2.
