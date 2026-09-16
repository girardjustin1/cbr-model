# Phase 13 Checker-Fix Report

**Doc:** CBR-FIX-013 · **Date:** 2026-09-15 · **Ruling:** D26 §11 · **Status:** COMPLETE, FOR OWNER REVIEW
Phase 13 **infrastructure** only: the checking, classification-labelling and reporting code. **No PC2 file, strategy
rule, parameter, threshold or course record was touched**, and no scored Phase 13 run was repeated (D26 §11, §14).

---

## 1. Fixes

### A. The causality spot check must use the bar close time

- **Defect.** `causality_checks` filtered trigger rows by the 5s shift bar's **open** time ≤ cut. A shift bar that opens
  before the cut closes after it, so a truncated run correctly lacks it and a mutated run can correctly gain one.
- **Effect on the run.** CX-TE1-1 variant A reported a truncation difference at cut 04:24:47 (shift bar 04:24:45 closes
  04:24:50) and a mutation difference at cut 04:25:17 (a mutated bar produced a shift at 04:25:15, closing 04:25:20).
  Both fed the false FAIL reason "gate A: a truncation / future-mutation spot check differed".
- **Fix.** Compare only shifts whose bar closed by the cut (`shift + 5s ≤ cut`).
- **Verified.** The engine itself was never at fault: re-execution showed the truncated run simply had no row, and the
  mutated run's extra row came from the mutated straddling bar.

### B. A hard-dimension failure is only "owner determination" when an approved alternative explains it

- **Defect.** Dimension 9 (shift time) inherited dimension 8's class when no baseline shift completed. On CX-LT1-1,
  dimension 8 was OWNER_BASELINE_CHOICE because `LAST_RESET` produces *a* shift (01:29:05) — but that shift is ten
  minutes before Tom's and is not D25-P3 equivalent.
- **Effect on the run.** CX-LT1-1 was listed under "owner determination required" instead of as a plain hard failure.
- **Fix.** Dimension 9 is classified on its own evidence: OWNER_BASELINE_CHOICE only when an alternative produces a
  D25-P3-equivalent shift; otherwise CANON_MISMATCH with the cancel reason cited.

### C. A structural price gap is not a feed difference

- **Defect.** Dimension 10 called any Tom-stop-beyond-anchor case FEED_DIFFERENCE regardless of size; CX-LT1-1's
  evaluated candidate (01:07) sat $25.55 from Tom's stop with a measured feed band of $0.20.
- **Fix.** MATCH within display rounding; FEED_DIFFERENCE only when the offset-adjusted gap ≤ τ; otherwise
  CANON_MISMATCH stating that Tom's stop references a different structural level, with the gap and the band quoted.

### D. Lint

The import block in `tests/engine/test_phase13_behavioral.py` (I001, recorded in the freeze manifest as the one lint
finding) is sorted. `ruff check src tests` is clean.

## 2. Regression tests

| Test | Guards |
|---|---|
| `test_shift_known_only_at_its_bar_close_in_the_causality_check` | A — runs the real engine on synthetic bars, takes candidates with completed shifts and asserts the spot check reports no difference |
| `test_timing_class_is_not_inherited_from_the_shift_type_class` | B — a far alternative shift gives CANON_MISMATCH on dim 9 while dim 8 stays OWNER_BASELINE_CHOICE; a P-3-equivalent alternative gives OWNER_BASELINE_CHOICE |
| `test_stop_gap_beyond_the_feed_band_is_not_a_feed_difference` | C — $25 gap with a $0.20 band is CANON_MISMATCH; a gap inside the band is FEED_DIFFERENCE |

All three **fail on the pre-fix code and pass on the fixed code** (verified by reverting the module and re-running).
Suite after the fixes: **531 passed, 1 skipped**; `ruff check src tests` clean.

## 3. What this does NOT change

- The **CBR-RUN-013B-2 verdict stands as reported**: FAIL. Reports under `reports/phase13-*.md` and the run manifest are
  the record of that run and were not regenerated.
- Fixes A-C would not have changed the verdict. A removes one of three FAIL reasons; B converts CX-LT1-1 from
  "owner determination" to a plain hard-dimension failure (already a FAIL condition); C relabels a supporting dimension.
- **No rerun.** Because frozen files changed, `phase13_behavioral run` now refuses with "frozen inputs changed after the
  freeze" — the intended guard. A future scored run needs PC3 approval and a new freeze (D26 §11, §14).

## 4. Known checker weakness left in place (documented, not fixed)

Criterion 9's "hour-level setup membership" concept is dominated by hours that are non-members on both feeds (members:
FOREXCOM 0, Dukascopy 1 across 225 evaluations), so its 99.6% agreement carries little information. The per-rule
agreement table (96.8-100%) is the informative measure. Changing the concept list would change a D25-frozen acceptance
input, so it is left for the owner (see the O-1 audit).
