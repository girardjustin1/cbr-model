# Phase 13: Research Engineer Post-Run Review (CBR-RUN-013B-2)

**Written after the verdict.** Nothing here changes a frozen rule, candidate, class or the verdict. It records what the
Research Engineer checked in the generated reports, the defects found in the Phase 13 checking code, and a labelled
post-run diagnosis for owner review. Generated reports: `phase13-behavioral-parity.md` (main), `phase13-feed-comparison.md`,
`phase13-higher-timeframe-fidelity.md`, `phase13-supplementary-candidates.md`, `phase13-run-manifest.json`.

## Frozen verdict: FAIL

Hard dimensions over the three positive examples (scored variant A; variant B produced no candidate in any course hour):

| Hard dimension | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | Result |
|---|---|---|---|---|
| Model family | ✓ | ✓ | ✓ | 3/3 |
| Direction | ✓ | ✓ | ✓ | 3/3 |
| Core extension direction | ✓ | ✓ | ✓ | 3/3 |
| Core structural trigger | ✗ no completed shift | ✗ shift 04:24:45 vs Tom 04:37-04:39 | ✗ shift 01:50:40 vs Tom 01:40:00 | 0/3 |

- No candidate was ARMED in any course hour (baseline or strict views). The frozen selection therefore evaluated
  `DIAGNOSTIC_FIRST_IN_ORDER`: the earliest completed 5s shift in the hour.
- Negative control CX-LT3-1: NO_ELIGIBLE_CANONICAL_SIGNAL. It carries little information: no candidate completed a
  shift in the control window and nothing armed in that hour at all.
- Deterministic rerun: identical result hashes (`f3905430…d063`); every engine-run repeat identical.
- Criterion 9: MET under the O-1 reading (all seven core rates ≥ 0.80).

The FAIL does not depend on the defects below: CX-TE1-1 and CX-LT3-2 fail the core structural trigger with classes
that are not approved explanations, and CX-LT1-1 does too once defect 2 is corrected.

## Defects found in the Phase 13 checking code (not in PC2)

| # | Defect | Effect on the report | Effect on the verdict |
|---|---|---|---|
| 1 | Causality spot check filtered trigger rows by the 5s shift bar's **open** time ≤ cut instead of its close. At CX-TE1-1 A the shift bar 04:24:45 closes 04:24:50, after the 04:24:47 cut; under mutation at 04:25:17 a bar straddling the cut created a shift at 04:25:15 (closes 04:25:20). Both events are unknowable at the cut. Reproduced by direct re-execution; the engine behaved causally | "gate A: a truncation / future-mutation spot check differed" is a false FAIL reason | none (FAIL stands on hard dimensions) |
| 2 | Dimension 9 inherits dimension 8's class when no baseline shift completed. CX-LT1-1: dimension 8 is OWNER_BASELINE_CHOICE (LAST_RESET completes a shift), but the strict-view evaluated shift is 01:29:05, not D25-P3 equivalent, so the timing mismatch does not disappear under any alternative | CX-LT1-1 is listed as "owner determination required" instead of a plain hard-dimension failure | none (FAIL either way) |
| 3 | Dimension 10 marks FEED_DIFFERENCE whenever Tom's stop is beyond the engine anchor, regardless of distance. CX-LT1-1's evaluated candidate (01:07) has an anchor $25.55 above Tom's stop | a large structural difference is labelled as a feed difference | none |
| 4 | Criterion 9 "hour-level setup membership" (99.6%) is dominated by hours that are non-members on both feeds (members: FOREXCOM 0, Dukascopy 1); the per-rule agreement (96.8-100%) is the informative figure | the headline membership rate overstates the evidence | none (criterion 9 is MET on the other six concepts too) |
| 5 | Lint at the freeze reported one import-order finding (I001) in `tests/engine/test_phase13_behavioral.py`; the `&&` chain before the freeze didn't stop on it | cosmetic | none |

Defects 1-3 were left in place: fixing frozen code after seeing results and rerunning would be a new, unapproved run.

## Post-run diagnosis (labelled, not scored)

`phase13-supplementary-candidates.md` lists every BASELINE_SPEC candidate in the course hours and follows the candidates
nearest Tom's shift, by identity, into each STRICT_COURSE run. Selection wasn't changed; this only shows whether the
engine sees Tom's structure.

| Example | Engine sweep near Tom | Level vs Tom entry | Baseline (D8 HOUR_OPEN) | Same candidate under LAST_RESET |
|---|---|---|---|---|
| CX-LT1-1 | BUY/6, decided 01:38:40 | 4340.185 vs 4340.13 | cancelled OE_PULLBACK before the shift | shift **01:39:35** (Tom 01:39:15; D25-P3 equivalent); still REJECTED: M1H-6A-1, M1H-COND-04, M1H-OE-01 |
| CX-TE1-1 | BUY/12, decided 04:36:40 | 4105.565 vs 4105.58 | cancelled OE_PULLBACK | shift **04:38:55** (inside Tom's 04:37-04:39); still REJECTED: M1H-6A-1, M1H-COND-04 |
| CX-LT3-2 | SELL/6, decided 01:43:35 | 4048.53 vs 4050.71 | cancelled OE_PULLBACK | no shift (S5_T3_NEW_SWING); REJECTED: M1H-6A-1, M1H-COND-03, M1H-COND-04 |

Readings for the owner (hypotheses, not rulings):
1. **The 5s structure detection reproduces Tom's trigger on two of three examples** (same sweep, level within $0.06,
   time within 20 s) but only under the pre-registered D8 alternative `LAST_RESET`. With the V1 baseline `HOUR_OPEN`,
   each hour's earlier ≥ 50% pullback cancels every later candidate (OQ-22, first raised as parity finding F-1).
2. **Three rules reject every candidate that reaches Tom's time**: M1H-COND-04 (a setup formed in the prior 10 h,
   OQ-05/OQ-36), M1H-6A-1 (HVCS runs into the shift, OQ-44), and on CX-LT3-2 M1H-COND-03 (trending range with
   direction NONE, OQ-02).
3. **Selection by earliest shift** (D19-10) would still pick an earlier shift under LAST_RESET on CX-LT1-1 (01:29:05,
   the OQ-23 / F-2 early shift), so D9's guards matter as well.
4. **Feed differences are not the cause.** The recent study found zero lag, a $0.00 median offset, τ = $0.20, and
   ≥ 88% agreement on every core structural concept. The course-hour FOREXCOM 1h/4h bars agree with Dukascopy on
   direction and extended side in every fully covered bar, and on 4h extreme hours in 17 of 18.

Any change these readings suggest (D8/D9 baseline choice, COND-04 lookback, HVCS continuity, selection rule) is a spec
decision for the owner and would need a new PC version and a new, separately approved Phase 13 run.
