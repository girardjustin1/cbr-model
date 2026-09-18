# Audit of the Pre-Run Readings O-1 to O-8

**Doc:** CBR-AUD-O · **Date:** 2026-09-15 · **Ruling:** D26 §12 · **Status:** FOR OWNER REVIEW
O-1…O-8 were Research Engineer operationalizations, frozen in `config/phase13_behavioral_run.yaml` before any Phase 13
data was fetched and listed in `docs/governance/d25-phase13-run-approval.md`. **D25 thresholds are not changed
retroactively; CBR-RUN-013B-2 stands as judged under D25.** This audit says only what each reading was, what it did,
and what should happen next.

| # | Reading | Evidence source | Explicitly owner-approved? | Affected acceptance? | Should remain? | Needs a new ruling? |
|---|---|---|---|---|---|---|
| **O-1** | Criterion 9 thresholds: FAIL evidence if a core agreement rate < 0.50, concern if < 0.80, over seven core concepts | 0.80 from CBR-ACC-010 AC10-10 precedent; 0.50 = plain meaning of "routinely" | **No.** D25-P5 chose option B but set no number for criterion 9 | **Yes, in principle** — it decides criterion 9. In this run no rate fell below 0.80, so the outcome (MET) is identical under any threshold ≤ 0.88 | Only as a placeholder | **Yes** — the owner should set or ratify the numbers before any run where they could bind |
| **O-2** | CX-LT3-1 control window = shift in [01:28:00, 01:36:00) UTC, derived from the video clock and the D25-P3 3-minute allowance | Video clock 12:23:41 UTC+11 at 00:00:00; discussion 00:07:47-00:09:16 | **No** (D25-P7 approved the control, not a window) | Yes — it defines criterion 5 | Yes, with the derivation on record | **Ratify.** The result was "no candidate shifted in the window at all", so the exact bounds did not bind |
| **O-3** | Variants: an example meets a hard dimension if one variant's evaluated candidate does; scored variant = first of A, B meeting all four, else the one meeting most | Protocol §4 dim 1 ("the variant is reported, not scored") | **No** | Yes, formally | Yes | **Ratify.** Variant B produced no candidate in any course hour, so A was scored throughout and the rule never had to choose |
| **O-4** | Core structural trigger = dim 8 MATCH **and** dim 9 MATCH or FEED_DIFFERENCE | D25-P3 + protocol §4 dims 8-9 | **No** (D25-P5-H names the dimension, not its composition) | **Yes** — it is the hard dimension all three examples failed | Yes | **Ratify or restate.** Without the dim-9 component, "trigger" would be satisfied by any completed 5s shift anywhere in the hour, including ten minutes from Tom's |
| **O-5** | On a hard dimension, FEED_DIFFERENCE counts as a match; OWNER_BASELINE_CHOICE does not, and yields OWNER_DETERMINATION_REQUIRED | D25-P5-V wording ("without an already-approved explanation") | **No** | Yes — it produced the CX-LT1-1 "owner determination" line | **Revise.** Checker defect 2 (D26 §11-B) showed the label was applied where no alternative reproduced Tom's event | **Yes**, if the OWNER_DETERMINATION state is to exist at all; the fix now restricts it correctly |
| **O-6** | PASS only if every non-DXY dimension is BEHAVIORAL_MATCH, every example ARMED, control clean, criterion 9 without concern; else PASS WITH CONCERNS | D25-P5-V | **No** | Not in this run (FAIL reached first) | Yes | No, but worth confirming that "every example ARMED" is required for PASS |
| **O-7** | Negative-control classification: OWNER_BASELINE_CHOICE if absent under one D8/D9 alternative, else UNRESOLVED_SPEC_AMBIGUITY (OQ-08) with an out-of-scope tag; IMPLEMENTATION_BUG only with a failing test | Tom's stated rejection reasons in the CX-LT3-1 record; protocol §3 | **No** | No — the control produced no signal | Yes | No |
| **O-8** | DXY excluded from example verdicts and concerns | D25-P8 ("never affects acceptance") | **Yes, in substance** | No | Yes | No |

## Summary

- **Only O-8 follows directly from an owner decision.** The rest were engineer readings of gaps in D25.
- **Two bound the result:** O-1 (criterion 9) and O-4 (composition of the core trigger). O-4's effect was decisive;
  O-1's was not, because every core rate was ≥ 0.88.
- **One was wrong as written:** O-5, corrected by checker fix B; the CX-LT1-1 hard-dimension failure has no approved
  explanation and should never have been labelled owner-determination.
- **None changed a strategy rule, a candidate, a class threshold inside PC2, or the data.**

## Recommendation

Before any future scored run (which requires PC3 approval anyway), the owner should rule on **O-1** and **O-4**
explicitly, and decide whether the **OWNER_DETERMINATION_REQUIRED** state (O-5) exists in the verdict vocabulary. The
others can be ratified as recorded.
