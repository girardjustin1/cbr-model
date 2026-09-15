# Phase 13 Run Incident 1: CBR-RUN-013B-1 Stopped Before Any Result

**Doc:** CBR-INC-013-1 · **Date:** 2026-09-15 · **Ruling context:** D25 · **Status:** recorded for owner review

## What happened

1. CBR-RUN-013B-1 was frozen at 2026-09-15T20:55:57Z (commit `36e096c`; 527 passed, 1 skipped; recent Dukascopy data
   absent). Manifest kept unchanged as `reports/phase13-freeze-manifest-CBR-RUN-013B-1.json`.
2. Execution step 1 (D25-E1) fetched Dukascopy XAUUSD ticks for 2026-09-09, 09-10, 09-11 and 09-14 (vendor 503 /
   URLError retries, all resolved) and built STRUCTURE bars. Tick file hashes printed by the fetch:
   - 2026-09-09 `cecfb0bb925e3664ddbe4cbe5d7e52c8c746d1f2f1792aff38299d5a2955c2c3`
   - 2026-09-10 `b1e09a8e87442a496513238ce72ae0817c7dcaa4e83a2176ba6d528e2ce15ac5`
   - 2026-09-11 `8c2edcf5188f331659deca1db9de6d2aee370753d8adba236f58fa5349c557a2`
   - 2026-09-14 `fa654a0b8cda75e4d955ecddfbba0be6b3dd17a5c727fc249621f009a9b4d0c6`
3. Complete run 1 raised `AttributeError: 'Index' object has no attribute 'floor'` inside `parity.calibrate`, the first
   computation of step 2, before it returned. **No measurement, feed band, engine run or course comparison was
   produced**: no run file was written, nothing but the traceback was printed, and no course-window engine run had
   started (step 2 precedes steps 3-5).

## Cause

FOREXCOM exports load with a second-unit index in `datetime.timezone.utc`; stored Dukascopy bars load with a
millisecond-unit index in `ZoneInfo("UTC")`. Joining the two returned a plain `Index`. The synthetic tests built both
feeds from one index, so they didn't cover it. Diagnosis read index types only (no prices).

## Fix

`feed_comparison.ns()` converts every study input to one nanosecond UTC index before any join. Regression test
`test_mixed_timestamp_units_are_normalized` reproduces the exact error without the fix and passes with it. No other
code, PC2 file, criterion, date, example, window, taxonomy or threshold changed.

## Governance handling

- A change to a frozen file means a new run id: **CBR-RUN-013B-2**, frozen again with the full pre-execution suite.
- The D25-P2 ticks fetched under freeze 1 are kept, not refetched. Freeze 2 accepts them only if their SHA-256 equals
  the hashes above and no run output exists; both facts are recorded in the new manifest.
- "Execute exactly once" is read as: CBR-RUN-013B-2 is the one execution that produces results, plus its deterministic
  rerun. The owner may rule otherwise.
