# D35 — CBR-PROT-013D / PC4 scored parity authorized

**Doc:** CBR-DEC-035 · **Date:** 2026-09-17 · **Status:** owner ruling, frozen with the protocol before execution
**Run id:** CBR-RUN-013D-1 · **Authorizes:** the scored Phase 13D run of PC4 under CBR-PROT-013D v1.1

Do not modify PC4 · do not modify the corrected parity-set manifest · do not optimize · do not inspect P&L or trade
outcomes · do not begin Phase 14 until the completed Phase 13D report is returned.

---

## 1. Frozen inputs, verified before execution (§1)

| Input | Hash | Verified |
|---|---|---|
| PC4 spec | `62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7` | yes |
| Corrected parity manifest v2 | `e12f3882f01b8ac4655520f00d5cd19829da989a371a1feb15b070d1a718804e` | yes |
| PC3 spec (unchanged) | `7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453` | yes |
| PC2 spec (unchanged) | `4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2` | yes |

If any hash differs the run STOPS; nothing is regenerated automatically.

## 2. Binding machine set (§2-3)

ENTRY_LEVEL: **CX-LT1-1**, **CX-TE1-1**, **CX-LT3-2** (positive) and **CX-LT3-1** (negative control).
HOUR_LEVEL: **JM-2025-10-16**. No case may be added after the run begins.

Non-binding and preserved as evidence: JM-2025-10-17 (`IFS_NOT_IMPLEMENTED`), JM-2025-10-29 (`SOURCE_AMBIGUITY`),
HX-1, HX-2 and the seven narrative cases.

## 3. Entry-level standard (§4-5)

Hard dimensions, frozen before execution and not redefinable afterwards: **model family · direction · extension
direction · extension activation · location / previous-15m event · HVCS eligibility under PC4 · 5-second type-3
structural shift · eligible candidate existence**. Condition compatibility is scored and classified but is not a hard
dimension.

For the three positives: 3/3 on the core structural event, direction, extension direction, and an eligible candidate
unless covered by a pre-existing approved non-failing classification. An unexplained IMPLEMENTATION_BUG or
CANON_MISMATCH on signal membership is a FAIL.

## 4. Negative control (§6)

CX-LT3-1 must return `NO_ELIGIBLE_CANONICAL_SIGNAL`. Admitting the rejected setup is a FAIL, and no exempting reason
may be created after the run.

## 5. E-2 — hour-level threshold (§7-9)

The single remaining hour-level journal case is **supporting independent evidence** and is not evidentially
equivalent to the narrated entry-level examples.

- **1/1 HOUR_MATCH** allows an overall clean PASS if every other PASS requirement holds.
- **0/1 HOUR_MATCH** does **not** independently cause FAIL; the verdict is then capped at **PASS WITH CONCERNS**,
  provided every binding entry-level hard gate and the negative control pass. The mismatch is still reported,
  classified, explained and retained as a concern.
- The hour-level case **cannot rescue** an entry-level failure, and a 1/1 journal match does not compensate for a
  failed negative control.

**Why this differs from D31, recorded before execution (§9):** D31 carried three hour-level journal cases. The later
source and taxonomy review found that one belonged to an unimplemented model (IFS), one contained contradictory
source columns, and only one remained validly scoped to CBR1H. The evidence set changed for methodological reasons
that are independent of PC4's results, and the threshold is revised **before** PC4 is scored. This is not a post-hoc
response to PC4 performance.

## 6. Reporting, selection and prohibitions (§10-14)

Strict and descriptive views are pre-declared: only eligible candidates count for scored parity; the descriptive view
is diagnostic and can never satisfy strict acceptance. The frozen deterministic selector is unchanged, and each
positive example reports (A) whether the expected structural event exists, (B) whether an eligible expected event
exists, and (C) which candidate the selector chooses; a divergence is `CANDIDATE_SELECTION_MISMATCH`, never a type-3
failure. No alternative setting is tested during the run (§13). Every scored mismatch receives exactly one primary
classification from the frozen taxonomy, and `UNRESOLVED_SPEC_AMBIGUITY` may not be used to conceal an
implementation defect.

## 7. Assumptions (§12)

Passing does not promote any assumption into CANON: the F-11 HVCS anchor/counting/unit, minute-7 activation, the Q1
qualifier, ATR zig-zag k = 3, swing-confirmation behaviour, the tradable-time window, the extension-origin
implementation and the F-10 Q interpretation all remain assumptions. A PASS means the frozen translation is
sufficiently faithful to begin baseline testing.

## 8. Pre-freeze smoke disclosure (§20)

**Confirmed: no real parity case was executed against PC4 before this authorization.** Every PC4 invocation in the
repository is in `tests/engine/test_cbr1h_pc4.py`, against a synthetic random walk dated 2030. Nothing to disclose.

## 9. Verdict rules (§15-17)

**PASS**: three positive entry-level cases satisfy their hard core dimensions and produce the expected eligible core
signal · negative control passes · JM-2025-10-16 is HOUR_MATCH · no unresolved implementation bug and no unexplained
canonical mismatch affects signal membership · causality, determinism and frozen hashes pass.

**PASS WITH CONCERNS**: as above but JM-2025-10-16 is HOUR_MISMATCH, fully classified, with the binding entry-level
cases and the control clean.

**FAIL**: any positive entry-level hard core requirement fails without an approved non-failing classification · the
expected core structural event is absent · the expected eligible signal is absent where eligibility is hard · the
control admits the rejected setup · an implementation bug or unexplained canonical mismatch affects signal
membership · causality, determinism or frozen-input integrity fails. The journal case alone can never cause FAIL.

## 10. After execution (§21)

Return exactly one verdict. Do not modify PC4 after seeing the result, do not launch a corrective run, do not begin
Phase 14. On PASS or PASS WITH CONCERNS, return the remaining concerns and the exact prerequisites for Phase 14A. On
FAIL, preserve the run and return the first causal divergence for each failed binding case.
