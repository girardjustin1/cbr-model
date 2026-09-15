# Phase 13 Behavioral-Parity Run Protocol

**Doc:** CBR-PROT-013B · **Version:** v0.1 **PROPOSED** · **Date:** 2026-09-15 · **Ruling:** D24 · **Gate:** CBR-ACC-013
**Status:** NOT APPROVED. Nothing here runs until the owner approves this protocol and decisions P-1…P-8 (§9). After
approval it is frozen (hash recorded in the run manifest) before any data is fetched or any engine run starts.

Inherited unchanged from CBR-PROT-013 (pinned in PC2):
- two parity views (§2);
- deterministic, course-blind candidate selection (`parity.select_candidate`, §5);
- the mismatch-class order (§3);
- the D19-12 time tolerances.

No outcomes, P&L, optimization or parameter change. PC2 is frozen throughout; an `IMPLEMENTATION_BUG` needs PC3 and a
full rerun.

## 1. Inputs (all pinned by hash in the run manifest)

| Input | Source |
|---|---|
| Spec | PC2: `CBR1H_BASELINE_V1-PC2.yaml` (spec_hash `4dadc8b9…`), code at the run commit |
| Canonical STRUCTURE data | Dukascopy STRUCTURE 1m/5s bars: 2025-10-20…24, 2025-11-07, 11-09, 11-10 (stored; manifest hashes) |
| DXY context | Phase 10 causal module on Dukascopy DOLLARIDXUSD 1m + Databento DX (stored) |
| Course truth | `research/examples/course_examples.jsonl` rows CX-LT1-1, CX-TE1-1, CX-LT3-2 (file hash) and cited evidence records |
| Higher-timeframe fidelity | `references/tom-chart-data/FOREXCOM_XAUUSD, 60.csv`, `240.csv`, `1D.csv`; `TVC_DXY, 60.csv` (hashes in `reports/tradingview-source-manifest.json`) |
| Recent feed comparison | `references/tom-chart-data/FOREXCOM_XAUUSD, 1.csv`, `5.csv`, `15.csv` + Dukascopy ticks for the P-2 days (to fetch) |

## 2. Engine runs (course windows)

For each example hour H (UTC): CX-LT1-1 2025-10-21 01:00, CX-TE1-1 2025-10-24 04:00, CX-LT3-2 2025-11-10 01:00.

1. `run_cbr1h(start=H, end=H+1h)` for variants **A** and **B** on stored bars (earlier bars are warm-up), view
   **BASELINE_SPEC**.
2. The same for **STRICT_COURSE**, one pre-registered alternative per run: `oe_origin=LAST_RESET`,
   `early_shift_guard=FINAL_PUSH`, `early_shift_guard=ALIGN_15M`. This is used only to classify
   `OWNER_BASELINE_CHOICE`.
3. Candidate choice per variant and view, engine information only:
   - `parity.select_candidate` → the selected ARMED candidate;
   - else the `DIAGNOSTIC_ONLY` candidate;
   - else the first candidate in `selection_key` order, labelled `DIAGNOSTIC_FIRST_IN_ORDER`.

   Tom's time, price and outcome are never inputs.
4. Every run is executed twice; decision, trigger and result hashes must be identical (gate A).

## 3. Course side (pre-registered from the example records; verbatim sources in the jsonl)

| Dimension | CX-LT1-1 (buy) | CX-TE1-1 (buy) | CX-LT3-2 (sell) |
|---|---|---|---|
| Condition | "range bound over the past five to 12 plus hours" (journal TRR CT / Ranging) | "bearish trending range", trading counter, "more range bound" (journal TRR CT / Ranging) | "very bullish, a little bit trendy"; unclear, a condition he dislikes |
| Accepted engine condition | RANGE or TRENDING_RANGE | TRENDING_RANGE (DOWN) or RANGE | TRENDING_RANGE (UP); TREND → classified, not matched (P-6) |
| Extension | hour opened, pushed bearish into the range low | hour pushed bearish 20-30 min into LTF/MTF lows | hour rallied into highs by the halfway point |
| Previous 15m take | 15m broke the low before the ~37-39 min shift | :30 candle took the previous 15m low | :30 candle took the previous high at 36 min |
| Shift type | 5-second shift (low, then takes a high) | seconds shift breaking the seconds-chart high ("a bit of a high low") | seconds shift (takes the low) |
| Shift / entry time (UTC) | 01:39:15 (tool hover with seconds → ±15 s) | ~04:37-04:38 (minute-level journal / discussion → ±60 s around [04:37:00, 04:39:00)) | 01:40:00 (tool x-axis with seconds → ±15 s) |
| Stop concept | just below the extension low (tool 4332.96) | below the extension low (tool 4102.80) | just above the high (tool 4053.30) |
| Target concept | 50% of the previous LTF move (tool 4351.59; closed manually ~1.3R) | 50% of the previous move (tool 4109.71; tool levels may be illustrative) | initial TP at a nearer level; 50% of the extension called most aggressive (tool 4043.80) |
| DXY (documented) | wanted DXY bearish; at entry DXY still bullish, into highs | DXY range-bound; hourly candle opened bullish into highs | DXY bearish at start; shifted bullish at entry |
| Entry price (tool) | 4340.13 | 4105.58 | 4050.71 |

## 4. Dimension rules

Every dimension records engine value, course value, price difference where applicable, primary class and evidence.

| # | Dimension | Engine value | BEHAVIORAL_MATCH when | Otherwise |
|---|---|---|---|---|
| 1 | Model | a CBR1H candidate in H with `entry_model` = 5s shift; the variant(s) that produce it | a CBR1H 5s-shift candidate exists in H (Tom's parent setup type isn't stated, so the variant is reported, not scored) | none in H → classify its absence (§5) |
| 2 | Direction | candidate `direction` (from the extension) | equals Tom's | classify |
| 3 | Condition | hour `condition` | in the §3 accepted set | classify (e.g. TREND on CX-LT3-2 → CANON_MISMATCH candidate; UNDEFINED from window basis → UNRESOLVED_SPEC_AMBIGUITY, OQ-40) |
| 4 | TR state / direction | `cond_direction` | matches §3 where stated; n/a for range | classify (NONE → `TREND_DIRECTION_UNRESOLVED`, D17-4) |
| 5 | Extension direction | `oe_dir` | equals §3 | classify |
| 6 | Extension timing | `oe_duration_min`, `oe_extreme_time`, `oe_no_pullback` | duration ≥ 20 min and the extreme precedes the shift; CX-TE1-1 also reports duration vs "20-30 min" | classify (OE-02 failure disappearing under LAST_RESET → OWNER_BASELINE_CHOICE) |
| 7 | Previous 15m take | `q_break_by_q` (and exception flag) before the shift | take present before the shift | classify; margin test (§6) |
| 8 | Shift type | 5s type 3 direction; `m1_hilo_armed_at_decision` reported | 5s shift in Tom's direction (HILO recorded for CX-TE1-1's "bit of a high low") | classify |
| 9 | Shift time | `five_second_shift_time` | within the §3 tolerance | outside it but the same structural event (P-3) → FEED_DIFFERENCE; else classify |
| 10 | Stop-anchor concept | `anchor_at(shift)` = most adverse extension extreme (D17-2) | the anchor is the extension extreme Tom's stop sits beyond (same side, same swing) | report Tom stop − (anchor ± buffer); a different extreme → classify |
| 11 | Target concept | 50% of the hour extension from H.open at activation | Tom's concept is 50% of the extension or move | report Tom target − engine target; a nearer or manual target → CANON_MISMATCH (discretion) |
| 12 | DXY context | Phase 10 causal DXY fields at the shift (1h / 15m direction, state); TVC:DXY 1h shown alongside | engine direction state agrees with Tom's note | CFD vs TVC disagreement → FEED_DIFFERENCE; unavailable → DATA_LIMITATION. Descriptive: CBR1H V1 has no DXY rule |
| — | Acceptance | `event`, `rules_failed` | ARMED (Tom took all three) | each failing rule classified; the example still gets its dimension table |

## 5. Classification and verdict

- **Per dimension:** one primary class in the CBR-PROT-013 order (DATA_LIMITATION → FEED_DIFFERENCE →
  EXECUTION_DEPENDENT → OWNER_BASELINE_CHOICE → UNRESOLVED_SPEC_AMBIGUITY → IMPLEMENTATION_BUG → CANON_MISMATCH), plus
  D24's `FEED_DEPENDENT_SIGNAL_DIFFERENCE` (§6), which ranks after FEED_DIFFERENCE. An IMPLEMENTATION_BUG is always
  flagged even when another class is primary.
- **Per example verdict (CBR-ACC-013 §5):** the most severe class, `IMPLEMENTATION_BUG` >
  `FEED_DEPENDENT_SIGNAL_DIFFERENCE` > `CANON_MISMATCH` > `UNRESOLVED_SPEC_AMBIGUITY` (incl. DATA_LIMITATION) >
  `OWNER_BASELINE_CHOICE` > `BEHAVIORAL_MATCH_WITH_FEED_DIFFERENCE` > `BEHAVIORAL_MATCH`.
- **Views:** BASELINE-SPEC and STRICT-COURSE results are shown side by side, never merged. No percentage is computed.

## 6. Feed differences and materiality

- **Reported for every price:** Tom value, Dukascopy value, difference, and the FOREXCOM 1h offset for that hour
  (supporting).
- **Structural-event equivalence** (P-3): same event kind and direction, the same swing broken or swept on the timeline
  (swing extreme bar within ±1 bar of its tier), the shift in the same 15m candle as Tom's entry, and |Δt| ≤ 3 min.
  Equivalent events with different prices or times → `FEED_DIFFERENCE`.
- **Materiality test** (D24-5): for each rule that decides a disputed dimension (e.g. the previous-15m take, a location
  threshold, OE no-pullback, a sweep), compute the Dukascopy margin, meaning how far price was from flipping the
  outcome.
  - If |margin| ≤ the feed band (P-4) **and** available FOREXCOM evidence (Tom's labelled levels, FOREXCOM 1h bars)
    shows the opposite outcome → `FEED_DEPENDENT_SIGNAL_DIFFERENCE`.
  - If the margin is inside the band but FOREXCOM evidence at the needed resolution doesn't exist →
    `FEED_DEPENDENT_SIGNAL_DIFFERENCE`, tagged `UNVERIFIED` + `DATA_LIMITATION`.
  - If the margin is outside the band → not feed-dependent; classify normally.

## 7. Supporting studies (run before the course comparison)

**7.1 Recent feed comparison (gate G).** Days per P-2. Steps:
1. Fetch and validate Dukascopy ticks (D21 integrity checks), build STRUCTURE bars.
2. Compare with FOREXCOM 1m / 5m / 15m. Structure primitives run on both feeds; FOREXCOM bars are a reference role and
   never enter the signal engine.
3. Measure:
   - lag (best 1m return lag) and per-field offsets, using the D22 calibration measurements;
   - bar-direction agreement (1m / 5m / 15m);
   - swing membership (LTF 1m and MTF 5m zig-zag, same kind with extreme within ±1 bar): matched, FOREXCOM-only and
     Dukascopy-only counts;
   - 15m previous-candle takes per 15m candle, with margins;
   - hourly extension direction, extreme time (±1 min), duration ≥ 20, no-pullback and two-sided flags;
   - condition class at each hour open;
   - 1m HILO arms and 1m type 3 events (same direction, ±1 bar);
   - hour-level CBR1H state: every rule evaluable without the 5s trigger, at minutes 25, 35 and 45 of each hour.
4. 5s comparisons are `DATA_LIMITATION` (no FOREXCOM 5s).
5. Report each rate with counts and 95% Wilson intervals, and the P-4 feed band.

**7.2 Higher-timeframe fidelity (D24-7).** FOREXCOM 1h / 4h / 1D vs Dukascopy roll-ups:
- on the three course hours (±3 h) and the course days: per-field offsets, hour direction, which side extended more,
  and the extreme's position;
- the same for TVC:DXY 1h vs the Dukascopy DXY CFD, descriptive (index vs CFD).

## 8. Outputs and order

**Order:**
1. Owner approves CBR-PROT-013B and P-1…P-8.
2. Freeze: protocol hash recorded; code committed.
3. Fetch and validate Dukascopy for the P-2 days.
4. Recent feed comparison (§7.1), which fixes the feed band.
5. Higher-timeframe fidelity (§7.2).
6. Behavioral-parity runs (§2), twice.
7. Classification register and per-example verdicts.
8. Report, then **STOP** for the owner's Phase 13 verdict.

**Outputs:**
- `reports/phase13-feed-comparison.{md,json}`
- `reports/phase13-higher-timeframe-fidelity.{md,json}`
- `reports/phase13-behavioral-parity.{md,json}` (dimension tables, both views, mismatch register, verdicts)
- `reports/phase13-run-manifest.json` (protocol, PC2, data and code hashes; result hashes of both repeats)

Holdout access (course windows) is logged; the recent 2026 days are post-holdout.

**Code to add after approval (not PC2-pinned):**
- `src/cbr/engine/phase13_behavioral.py` (runs, dimension extraction, classification helpers);
- `src/cbr/data/feed_comparison.py`;
- tests on synthetic data. Classification helpers never read course values during candidate selection.

## 9. Owner decisions required before the run

| Id | Decision | Proposal |
|---|---|---|
| P-1 | Approve this protocol | — |
| P-2 | Recent comparison days | 2026-09-09 (from 01:00 UTC), 09-10, 09-11, 09-14: full weekdays inside the FOREXCOM 1m export; non-course and post-holdout (the holdout ended 2026-08-31). Fetch about 96 Dukascopy hour-files |
| P-3 | Structural-event equivalence for shift time | same event kind and direction, same swing (±1 bar), same 15m candle, and \|Δt\| ≤ 3 min. The 3-min value is a proposal (1m-structure resolution), not derived from engine output |
| P-4 | Feed band for materiality | the D19-11 formula applied to the P-2 days: τ = max($0.02, p95 offset-adjusted HLC residual) rounded up to $0.05; also report p99. Used only for the §6 margin test, never as an equality tolerance |
| P-5 | Gate G acceptance rule | owner choice: (a) owner judgement on the reported agreement rates and intervals; or (b) a pre-registered minimum agreement for hour-level CBR states and swing membership, with the numbers set by the owner before §7.1 runs |
| P-6 | Course-side condition mapping | the §3 accepted sets (in particular CX-LT3-2: TRENDING_RANGE UP matches; TREND is classified as a canon or discretion difference, not matched) |
| P-7 | Optional negative check | include CX-LT3-1 (XAUUSD, not taken: Tom rejected an early, too-small shift at ~12:31-12:33 local) as a supporting "engine should not treat it as the taken setup" check; excluded from the three-example verdict |
| P-8 | DXY dimension | descriptive comparison (engine CFD context and TVC 1h vs Tom's notes); never affects acceptance, since V1 has no DXY rule |
