# Open Questions & Ambiguity Register

Nothing here is silently resolved. Each item states the problem, the evidence, the possible
interpretations, and a **proposed baseline default**. A default is only a placeholder that lets the
baseline be built; it is labelled `ASSUMPTION` in the machine spec and becomes a tested parameter
where it matters.

**Status values.** `NEEDS USER DECISION` · `NEEDS SOURCE CHECK` (may be settled by a frame, the long
recordings, or the Notion journal) · `RESEARCH PARAMETER` (legitimately ambiguous; test a small range) ·
`RESOLVED` (with the evidence that resolved it).

---

## A. Definitions the models depend on

### OQ-01 · What counts as a swing high/low?
- **Problem.** Condition, entry relativity, external/internal, shifts and swing counts all depend on swing
  points. No source defines a pivot rule; the author reads them visually on the 1m chart (E1H-005).
- **Interpretations.** A. N-bar fractal pivot (e.g. 2-2, 3-3) on 1m · B. zig-zag with a minimum reversal
  size (ATR multiple) · C. scale-dependent: one pivot rule per duration tier.
- **Update (Phase 1).** No objective rule exists in any course. Tom's own words: swing choice is "intuitive"
  (P2G-16), and there are no "purely mechanical rules" (P2G-66). The only definitional statement is the board slide
  "SWING occurs when price breaks an old High or Low" (P1F-3), plus "only external breaks are shifts" (EP2-018).
- **Proposed default.** D. **Break-confirmed swings**: a swing high is confirmed when price subsequently breaks the
  most recent swing low (and vice versa), computed separately per duration tier, with a minimum swing size
  (ATR multiple) to separate internal from external. A causal zig-zag, so no lookahead. Alternative C (fractal pivots,
  strength ∈ {2,3,5}) is kept as a robustness check. Both are `RESEARCH PARAMETER`.
- **Status.** `RESEARCH PARAMETER`, and may be clarified by the Notion journal screenshots.

### OQ-02 · Condition thresholds and averaging
- **Problem.** Range = ">50%" correction in one lesson (E1H-009), "75-100%" in two others and the 15m slide
  (E1H-007, E1H-008, E15-014). Also unstated: mean vs median, and how many moves.
- **Interpretations.** A. 75%+ range / 50-75% trending range / <50% trend · B. >50% range.
- **Proposed default.** A (three sources plus a slide agree), median of the last N completed swings in the
  window. N is `RESEARCH PARAMETER`.
- **Status.** `NEEDS SOURCE CHECK` → likely resolves to A.

### OQ-03 · Which duration tiers apply to which model?
- **Problem.** Hourly course: LTF = 30-60 min, MTF = 5-12 h (E1H-005). Move tiers in E1H-006: LTF <1 h, MTF
  1-4 h. 15m course: "low timeframe range" = 1.5-2.5 h (E15-004).
- **Update (Phase 2).** Market-structure alignment tiers: LTF 10-30 min (1m/5m charts), MTF 4-5 h (15m/30m/1h),
  HTF past day (4h/1D/1W) (EP2-011, EP2-012, EP2-016). These are the tiers for **MS alignment** (LTF first, 2+
  aligned good, 3 best; EP2-014), a different use from the CBR **condition window** (5-12 h).
- **Proposed default.** Condition window = 5-12 h for hourly CBR, 1.5-2.5 h for 15m CBR; MS-alignment tiers per
  Phase 2 (10-30 min / 4-5 h / 1 day); E1H-006 tiers used only to label the *previous move* for entry relativity
  and targets.
- **Status.** `NEEDS SOURCE CHECK`.

### OQ-04 · Detecting an MTF impulse (for FS / IFS)
- **Problem.** "Massive impulse" is visual (E1H-010, E1H-011).
- **Proposed default.** Leave FS/IFS **out of baseline V1**. Baseline trades only range and trending-range
  models, which are measurable. FS/IFS become a separate V-next model.
- **Status.** `NEEDS USER DECISION` (see batch Q2).

### OQ-05 · "Clean setup that played out" for the prior-setup check
- **Problem.** E15-049 counts prior CBRs that "set up and played out"; "clean" is undefined.
- **Proposed default.** A prior signal from the *same machine rules* that reached its 50% target before its
  stop. Uses only closed past outcomes, so there's no lookahead.
- **Status.** `RESEARCH PARAMETER` (min count ∈ {1,2,3}).

### OQ-06 · Minimum leg / setup number in a range
- **Problem.** Slide: "Target legs 3, 4, and 5 into the range. Not legs 1 or 2" (E15-050). Narration: "3rd/4th,
  maybe the second if a bit more aggressive" (E15-007).
- **Proposed default.** Slide wins: leg ≥ 3. Leg ≥ 2 tested as an ablation.
- **Status.** `RESEARCH PARAMETER`.

### OQ-07 · AOI zone construction
- **Problem.** Which candle opens/closes, how close to merge into a zone, and which are "relevant" (E1H-014).
- **Conflict (course examples).** In the textbook counter trending-range example Tom says "this actually doesn't
  have an AOI because you're a bit beyond that", yet the matching journal row lists an AOI and the plan slide
  reads "Wait for Hourly OE 20-30 mins into H/L of range with AOI" (CAND-022, CAND-023). Consistent with
  E1H-012 (counter trades need no AOI), not with an AOI requirement.
- **Conflict (Phase 2, Level 1).** "for any sort of 15 minute 30 minute reversal it has to tap into a 30 minute or
  an hourly area of interest and reject from that" (EP2-023). The 15m reversal also requires a push "into an hourly
  or 30 minute level" (EP2-022). That makes the AOI a **requirement** in the prerequisite course, against "not as
  important" in the 15m CBR course (E15-019) and "lowest priority" in the calls (LR-49).
- **Proposed default.** Run **two baselines**: V1a without an AOI requirement (CBR course), V1b requiring a
  tap of a 30m/hourly open-close zone (Phase 2). AOI zone = hourly and 30m candle open/close prices ± a zone
  width (`RESEARCH PARAMETER`). This is a direct test of which teaching adds information.
- **Status.** `RESEARCH PARAMETER`.

### OQ-08 · "High volume" / "decisive" extensions and HVCS
- **Problem.** Central quality words with no number (E15-023, E15-024, E1H-013, E1H-034). XAUUSD spot volume is
  broker tick volume, not exchange volume.
- **Interpretations.** A. range of the extension ≥ k × ATR(tier) · B. fraction of bars moving in the
  extension direction · C. tick volume vs rolling median.
- **Proposed default.** Measure A and B as `discretionary_proxy` fields; no hard filter in baseline V1 beyond
  the objective duration and "no 50% pullback" rules.
- **Status.** `RESEARCH PARAMETER`, flagged `RESEARCH-DERIVED` if ever used as a filter.

### OQ-09 · Shift types 1/2/3 and the exact HILO pattern
- **Problem.** "Type 1", "type 2", "type 3" shifts and "HILO" are referenced as known terms ("covered in phase two of
  the academy"). That Academy course isn't in the reference folders (E15-032, E1H-031, E1H-003).
- **Update (Phase 2 course, Level 1).**
  - **HILO: `RESOLVED`.** Within 1-2 candles, price breaks a previous candle's high then a previous candle's low
    (or the reverse). The candle before the break must itself have broken its previous candle's opposite
    high/low, or one candle breaks both. Bigger breaks are better (EP2-001…004, frame-confirmed). The same rule
    applies on 5m when 1m is a low-volume sequence (EP2-005).
  - **HVCS: `RESOLVED` (structure part).** Consecutive large same-direction 1m candles, each respecting the prior
    candles' lows (up) / highs (down); LVCS = small overlapping candles (EP2-005, frame-confirmed). "Large" is
    still unquantified (OQ-08).
  - **Type 1/2/3: `RESOLVED` (Phase 1, Level 1).**
    - **Type 1** (candle behavior): bullish close then bearish close (bearish type 1); the next candle wicks
      into that level in its first half, then continues (EP1-002, quality EP1-003).
    - **Type 2** (candle behavior): a candle closes decisively beyond a level (its wick breaking the previous
      low/high); the next candle retests the level with its wick in its first half (EP1-005, EP1-006).
    - **Type 3** (market structure): take out a swing high, immediately reverse, take out a swing low
      (sell; mirror for buy), decisive and high-volume, ideally closing beyond both. Entry on the pullback, stop
      behind the swing taken out, target the previous LTF opposite swing (EP1-007…009, EP1-012).
    - **CHoCH:** any BOS turning HH/HL into LH/LL; all type 3s are CHoCHs, not vice versa (EP1-010).

    The Phase 2 remark calling break-high→break-low a "type two" (EP2-008) conflicts with this and is treated as
    loose speech. The usage hypothesis in EP2-009 was close for type 3 but wrong in detail.
- **Proposed default.** HILO and HVCS per the above; shifts per Phase 1 definitions. A shift against HTF
  direction without a big external break is a pullback (EP1-011, EP2-018).
- **Status.** `RESOLVED` (definitions); swing-point detection remains OQ-01.

### OQ-10 · Seconds-chart entries
- **Problem.** The 15m entry trigger is a 5s type-3 shift (E15-037). Hourly model A uses seconds shifts
  (E1H-034). Pine `request.security` to seconds needs a TradingView plan with seconds data; bulk seconds
  history needs tick data.
- **Interpretations.** A. build 5s bars from Dukascopy ticks (faithful) · B. approximate with 1m shifts
  (labelled simplification) · C. both, and measure the gap.
- **Proposed default.** C. Python reference uses tick-built 5s bars; Pine baseline V1 uses 1m and is labelled
  `SIMPLIFIED-ENTRY`.
- **Status.** `NEEDS USER DECISION` (batch Q3).

### OQ-11 · Stop buffer size
- **Problem.** "Beyond the external high/low", "give breathing room" (E1H-036, E15-040); no size.
- **Proposed default.** Conservative stop = external extreme ± spread + 0.1 × ATR(1m, 14). Buffer multiple
  ∈ {0, 0.1, 0.25}.
- **Status.** `RESEARCH PARAMETER`.

### OQ-12 · Target: 50% of extension vs 1:1 vs external high
- **Problem.** Course default is 50% of the overextension (E1H-037, E15-039). Adaptive rule (E1H-038). E15-017
  says target the external high for counter-direction reversals. Journal (Level 2) says 1:1 for 15m CBRs and
  1.5-1.75R as his stated optimum.
- **Proposed default.** Baseline V1 = 50% of the overextension, fixed. Adaptive and 1:1 variants are separate
  ablations. Journal-derived variants labelled `LEVEL-2-DERIVED`.
- **Update (course examples).** In a trendy live trade Tom calls 50% of the extension the "most aggressive take
  profit", with a nearer initial target (CAND-003, V1H-live_trade_3_gold_win 00:29:01). Consistent with the
  adaptive rule; weakens "always 50%" as a default in trendy conditions.
- **Status.** `RESEARCH PARAMETER`.

### OQ-13 · DXY: optional confluence or veto?
- **Problem.** Course: "ideally" DXY extends opposite (E15-042, OPTIONAL). Journal: setups skipped when DXY
  extends the same way (veto). Plus a "gold spread" series he ranks above DXY (Level 2).
- **Update (course examples, Level 1).** The live gold trades add a **gold spread** instrument (gold priced
  against a basket of non-USD currencies) and a combined trigger: DXY shifts opposite + gold spread shifts in the
  trade direction + gold breaks its seconds low/high (CAND-007…009). The gold spread is now Level 1, not only
  journal evidence. Its exact TradingView symbol/construction is not yet identified.
- **Scope (user, 2026-09-14).** XAUUSD and DXY only: the gold spread and silver correlation are cataloged,
  **not** implemented.
- **Update (Phase 2 DXY lesson, Level 1).** Specific, testable rules (EP2-026…030):
  (a) **entry inversion**: gold type-3 shift in one direction with a DXY type-3 shift in the other (author claims
  80% win rate); (b) **veto**: "if they're both moving in the same direction with lots of volume i just wouldn't
  take a trade"; (c) **scope**: DXY most useful in high-volume ranges, **ignored** when gold is extremely
  strong/trending or at all-time highs; (d) **exit** if DXY rejects against the trade; (e) relative strength
  (big DXY move, small inverse gold move = gold strong). This moves the course position from "optional" toward a
  **conditional veto**, consistent with the journal.
- **Updated default.** Baseline V1 still has no DXY rule. Phase 18 ablations test (a), (b), (b)+(c) and (d)
  separately against baseline.
- **Proposed default.** Baseline V1 has **no DXY rule**. DXY is tested as (a) confluence score, (b) veto, (c)
  timing trigger, against the baseline (Phase 18). This is exactly the ablation question.
- **Status.** `RESEARCH PARAMETER`.

---

## B. Conflicts and unclear statements in the sources

### OQ-14 · Buy/sell relative to the 15m open (E15-018)
- **Problem.** Spoken: "you won't be looking for buys below the open … and sells above the open". That's the
  opposite of the model, since a buy follows a bearish extension below the open. Journal evidence
  ("top wick first" before sells) supports reading it as misspoken.
- **Proposed default.** Buys only below the 15m open, sells only above.
- **Status.** `NEEDS SOURCE CHECK` (frame at V15-entry_relativity 00:08:25-00:08:36 was ambiguous).

### OQ-15 · Daily candle behavior: unimportant or a setup?
- **Problem.** "don't worry about candle behavior day" (E1H-028) vs the Daily CBOE / London reversal context
  (E1H-043).
- **Proposed default.** Daily CB is not a filter for the hourly/15m baselines; the London daily-CBOE reversal
  is a separate higher-timeframe context, recorded as a diagnostic feature.
- **Status.** `RESOLVED` as two different scopes (pending user confirmation).

### OQ-16 · Session filter for the hourly model
- **Problem.** Author trades Asia hours 1-3 and London hours 2-3 (E1H-042) because of his timezone. The 15m
  course says "anytime within the day" on gold (E15-026).
- **Update (course examples).** Tom counts hours from the Asia session start and notes DST moves it on his clock.
  Chart evidence: 12:17-12:23 UTC+11 = "second hour of Asia"; Fri 24 Oct 2025 15:38 UTC+11 = "fifth hour of
  Asia" (CAND-015). So hour 1 of Asia = 00:00-01:00 UTC in Oct-Nov 2025, and he also traded hour 5.
- **Proposed default.** No session filter in either baseline. Session is a segmentation variable (Phase 17). The
  author's windows are tested as an ablation. Session anchor: Asia hour 1 = 00:00 UTC (evidence above); London
  open per `Europe/London` 08:00 local (DST-aware); still an `ASSUMPTION` outside Oct-Nov 2025.
- **Status.** `NEEDS USER DECISION` (batch Q4).

### OQ-21 · Trend: hard no-trade or quality downgrade?
- **Problem.** Lessons say don't trade high-volume trends ("if it's trending definitely shouldn't be trading",
  E1H-010, E1H-046). In two course live trades Tom took reversals in conditions he called "a little bit trendy…
  not the best condition" (gold, CAND-001) and "quite directional… no overextension on the 15 minute" (UJ,
  CAND-002).
- **Interpretations.** A. Trend (<50% corrections) is a hard filter; "a bit trendy" trending ranges are still
  allowed · B. condition is a quality tier, not a gate.
- **Proposed default.** A for baseline V1 (lesson rule, measurable threshold). B tested as an ablation that
  records condition as a feature. Outcomes of those two trades are **not** used to decide.
- **Status.** `RESEARCH PARAMETER`.

### OQ-22 · Overextension origin: hour open or last reset? (parity F-1)
- **Problem.** CX-LT1-1: the hour retraced 85% around minute 10, then pushed cleanly ~26 min. Tom calls it a clean
  overextension; V1 measures the no-pullback test from the hour open and rejects it.
- **Evidence.** E1H-025 (delayed push → later reversal), LR-41 (Level 2: "a big pullback restarts the count").
- **Options.** `HOUR_OPEN` (V1 as written) · `LAST_RESET` (duration and no-pullback from the start of the push after
  the most recent ≥ 50% pullback; stop and target still from the hour open).
- **Decision D8.** Test both: V1 baseline keeps `HOUR_OPEN`; `LAST_RESET` is a pre-declared single-rule ablation.
- **Status.** `RESEARCH PARAMETER`.

### OQ-23 · An earlier valid shift fires before the taught entry (parity F-2)
- **Problem.** CX-LT1-1: a valid 5s type 3 BUY at 01:29 (inside :22-:52), ~12 points above Tom's entry at 01:39, while
  the push was still extending. V1 takes the first valid signal.
- **Evidence.** E1H-021 (the :30 15m candle continues against, takes the previous 15m low, then reverses ~:37),
  E1H-022.
- **Options.** `NONE` (V1) · `FINAL_PUSH` (the entry's type 3 sweep must set the hour's extension extreme at entry) ·
  `ALIGN_15M` (the 15m candle containing the entry must first take out the previous 15m candle's high/low).
- **Decision D9.** Test both as pre-declared single-rule ablations against V1.
- **Status.** `RESEARCH PARAMETER`.

### OQ-24 · Baseline data feed for Phases 15-16: spot, futures or hybrid?
- **Problem.** Complete 2018-2024 Dukascopy spot history is costly to acquire (AC-11B deferred). Databento GC/DX
  futures 2018-2026 are already owned. CBR15 needs 5-second entries, which neither 1m source provides historically.
- **Options.** (a) Dukascopy spot · (b) GC/DX futures, spot for parity · (c) hybrid (1m structure on futures,
  entry ticks from spot for armed-signal hours).
- **Owner ruling (D11).** Do **not** choose yet. The decision stays open until: (1) Phase 9 feed validation is complete,
  (2) CBR15 and CBR1H reference engines exist, (3) Phase 13 parity is complete, (4) cross-feed signal agreement can be
  measured. It **must be frozen before Phase 14 begins**.
- **Selection criteria (owner).** Fidelity to Tom's taught model · signal agreement · timestamp/structure agreement ·
  historical availability · execution realism · 5-second entry feasibility · reproducibility · known feed distortions
  (e.g. futures contract rolls). **Historical profitability must not be used to choose the feed.**
- **Safeguard.** Futures data may support baseline performance claims only after passing the cross-feed
  signal-agreement acceptance requirement (Phase 13/14; see PRD gate G2b).
- **Status.** `NEEDS USER DECISION`, deferred to pre-Phase 14.

### OQ-25 · Canonical historical OHLC source for price extremes (owner ruling D12-5)
- **Problem.** Dukascopy candle files build mid high/low as the mean of per-side extremes (`SIDE_EXTREME_MEAN`), which
  may come from different ticks. On 10 tick-window pairs: 0-28 artificial XAUUSD minutes and 0-67 DXY minutes per
  window; largest errors $0.425 and 0.3185. The candle-only warning flag misses most of them.
- **Affects.** Swing detection · range highs/lows · extension extremes · stop placement · liquidity sweep/take
  detection · possibly structure-shift detection.
- **Options.** (a) Tick-built `TICK_MID` bars for all extreme-sensitive logic (needs ticks for history) · (b) candle
  files, only if shown quantitatively not to change signal membership or material execution results · (c) a hybrid:
  candle files for coarse structure, ticks for armed-signal hours · (d) another validated source.
- **Constraint.** Never chosen by profitability. Decided together with OQ-24.
- **Owner ruling D14-3 (2026-09-14).** Higher priority than Backtesting.py. Candle-file extremes must not silently become
  canonical. Not solved during Phase 10 unless Phase 10 genuinely needs it (it doesn't: DXY context uses opens and closes
  only). **Before Phase 11 starts**, deliver an owner decision package covering: (1) available sources for canonical
  extremes, (2) tick-derived mid/bid/ask options, (3) full-history availability, (4) implications for CBR15 and CBR1H,
  (5) implications for spot/futures/hybrid baselines, (6) implementation cost, (7) recommended choice, (8) validation
  tests. Never selected by profitability.
- **Decision package delivered (2026-09-15):** `docs/decisions/oq25-canonical-price-extremes.md` (CBR-DEC-025), evidence
  `reports/oq25-extrema-evidence.md`. Recommendation: STRUCTURE = tick-derived mid (`TICK_MID`), EXECUTION = tick
  bid/ask, as two concepts; second-best: cost-reduced candle/tick hybrid (H). Provisional on V-1 (FOREXCOM export).
  **Not implemented; canonical source unchanged until owner approval.**
- **Owner ruling D16 (2026-09-15): APPROVED.** STRUCTURE = tick-derived mid (`TICK_MID`, role `STRUCTURE`); EXECUTION =
  tick-derived bid/ask (role `EXECUTION`); never one series for both; access guards required. V-1 (FOREXCOM export) is a
  hard requirement before Phase 13 parity passes; material differences reopen OQ-25. Candle files and GC are not
  canonical for structure extremes. Full tick history deferred (OQ-33).
- **Status.** `RESOLVED` (D16). Gate G2d satisfied for source selection; validation V-1 pending before Phase 13.

### OQ-26 · Independent reference for fine-grained DXY structure (owner ruling D12-6)
- **Problem.** DXY CFD vs DX futures agree at 15m/1h (15m corr 0.963-0.993 on the days under the 1m threshold) but not
  at 1m (0.745-0.974). DX is too quantized/thin to validate 1m or 5s DXY structure (e.g. Tom's 5-second DXY shifts,
  EP2-026).
- **Handling.** Dukascopy DXY may be used for 15m/1h direction and broader inverse context. 1m/5s DXY structure is not
  promoted into the canonical strategy unless validated against an independent reference (e.g. a TradingView TVC:DXY
  export for fixture windows).
- **Status.** `OPEN DATA DEPENDENCY`.

### OQ-27 · DXY CFD availability around DST transitions and the weekly reopen (owner ruling D12-2)
- **Problem.** No CFD ticks at 00:00-00:59 UTC on 2019-03-11 (Monday after US DST start), while DX traded. Every other
  Monday checked fits a 20:00 New York CFD start; this one doesn't. The cause is unknown.
- **Task.** Diagnostic across other DST-transition Mondays (spring and autumn, 2018-2024). Report the pattern only; do not
  reclassify 2019-03-11 without evidence.
- **Status.** Approved, not required for Phase 9. **Must be complete before historical DXY availability assumptions
  are frozen for baseline testing.**

### OQ-28 · Stop resolved at fill or frozen at decision? (signal contract, D13)
- **Problem.** M1H-SL-01 and primitives §8 compute the stop at fill: `oe_extreme (at fill) ± buffer_atr × ATR(1m,14) ±
  spread`. An immutable signal contract (CBR-ARCH-014 §3) needs a stop specification at decision time.
- **Options.** (a) `ADD_SPREAD_AT_FILL`: the contract carries anchor + buffer; the simulator adds the fill-time spread
  (keeps the current spec) · (b) `FROZEN_AT_DECISION`: the whole stop is fixed when the signal is emitted (spec revision).
- **Constraint.** Decided on spec fidelity and testability, **before Phase 13**; never after baselines exist.
- **Owner ruling D14-1 (2026-09-14).** Stays **OPEN** until the Phase 11/12 engines and execution semantics exist. The
  signal contract carries the **canonical stop inputs** (extension extreme, direction, canonical stop buffer and its
  classification/source, spread/execution inputs when available), not a pretended executable stop price. The
  authoritative simulator may compute the executable stop from the fill-time spread if that stays consistent with the
  machine spec. No second trading rule is created to accommodate Backtesting.py; the custom simulator stays
  authoritative.
- **Status.** `OPEN` (revisit after Phases 11-12).

### OQ-29 · CBR1H execution clock: 5s or 1m? (D13)
- **Problem.** The owner allows CBR1H on 1m bars if Phases 11-13 prove it sufficient, but primitives §8 fills both
  models' stop entries on 5s bars.
- **Handling.** 5s stays the spec. Moving to 1m needs parity evidence that fills and signal membership don't change
  materially, plus an owner-approved spec revision before Phase 14A.
- **Owner ruling D14-2 (2026-09-14).** Stays **OPEN**. CBR1H is not simplified to 1m for convenience; 5s behavior is
  preserved. Phase 13 measures whether a 1m implementation gives sufficiently equivalent signal membership, timing,
  structure and execution. If it does, a spec change is **proposed** for owner approval.
- **Status.** `OPEN`, decided after Phase 13.

### OQ-30 · Backtesting.py licence (AGPL-3.0) in a public repository (D13)
- **Problem.** `backtesting` 0.6.6 is AGPL-3.0; the repository is public. Adding it as a dependency may carry copyleft
  obligations for the project code that uses it.
- **Handling.** Not added until Phase 14B. Owner reviews the licence implications (no legal conclusion is made here).
  Fallback if rejected: keep 14B visual/metrics outputs in a separate, isolated tool or choose another library,
  with no change to 14A.
- **Owner ruling D14-4 (2026-09-14).** Stays **OPEN** until Phase 14B; no legal conclusion now. Before 14B begins, run a
  licensing review appropriate to the repository's intended use and distribution. If it conflicts, Backtesting.py may be
  replaced without affecting the authoritative simulator or the research methodology.
- **Status.** `OPEN` (licensing review before Phase 14B).

### OQ-33 · Historical tick acquisition strategy (D16-4)
- **Problem.** D16 makes tick-derived mid/bid/ask canonical, but the full 2018-2026 XAU tick download (≈ 65k hourly files,
  6-7 GB, 1.5-24 days) is deferred until the needed granularity is known.
- **Options.** (A) full tick history · (B) targeted tick windows around armed candidate signals · (C) another validated
  tick source · (D) staged/resumable hybrid acquisition.
- **Constraint.** Decided after Phases 11-13 and the gate-required cross-feed/structure sensitivity checks, on fidelity,
  reproducibility and execution needs; **never profitability**. Note: option B couples data coverage to engine output,
  so its reproducibility and structure-window needs must be shown.
- **Status.** `DEFERRED` (owner, D16-4).

### OQ-34 · CBR15 hourly veto needs the CBR1H engine (Phase 11 sequencing)
- **Problem.** M15-HTF-01 vetoes a 15m setup against an ARMED/FILLED `CBR1H_BASELINE_V1-A` setup in the same hour. That
  engine is Phase 12, so Phase 11 can't evaluate the veto.
- **Handling now.** Injected dependency; default `NOT_EVALUATED`. Rule outcome `None`, signals carry
  `data_confidence = REDUCED` with `HTF_NOT_EVALUATED`. Raw setups for COND-03 treat a not-evaluated veto as not failing.
- **Also open.** "ARMED or FILLED": FILLED is an execution state (Phase 14A). Proposed reading: the veto uses the hourly
  engine's ARMED signals active at `as_of` (signal logic only), with FILLED added once execution exists, never by
  reading bid/ask in the engine.
- **Owner ruling D17-1 (2026-09-15).** Open until Phase 12. `NOT_EVALUATED` is neither PASS nor FAIL; an otherwise valid
  candidate is never rejected solely because the hourly engine is unavailable; an explicit eligibility flag is carried.
  Rerun CBR15 with M15-HTF-01 once CBR1H exists.
- **Owner ruling D18-11 (2026-09-15).** Separate SIGNAL-STATE parity (veto from ARMED hourly signals on STRUCTURE) from
  EXECUTION-STATE parity. The FILLED component is `EXECUTION_DEPENDENT` with `HTF_FILL_STATE = NOT_EVALUATED`; no
  fabricated fills. CBR15 isn't fully eligible until resolved (readiness item 16).
- **Implemented (D19-15).** `htf_signal_state` (the rule, from ARMED/PENDING hourly setups) and `htf_fill_state`
  (`NOT_EVALUATED` when an opposite hourly 5s shift already triggered) are separate fields; the fill state never rejects
  and carries the eligibility blocker `HTF_FILL_STATE_EXECUTION_DEPENDENT`.
- **Status.** `OPEN` (execution-dependent fill component; resolves with Phase 14A). CBR15 not fully baseline-eligible.

### OQ-35 · Stop anchor instant and granularity for CBR15 (and OE extreme at 5s)
- **Problem.** Three spec statements disagree: M15-SL-01 "stop beyond `oe_extreme`" (no instant); M1H-SL-01
  "`oe_extreme` **(at fill)**"; primitives §4.1 "`t3.sweep_extreme` (the stop anchor, EP1-012)". The OE is computed on
  **closed 1m bars**, so at a 5s decision the current minute's sweep is excluded.
- **Evidence (Phase 11, CX-LT1-1 01:38:40 BUY, tick mid).** `oe_extreme` at decision (closed 1m) **4335.21**; 5s sweep
  bar 4334.78; extreme before the structure break at 01:39:35 **4332.955**. Tom's stop: **4332.96**. Tom's stop matches
  the extreme at fill / sweep extreme, not the literal decision-time 1m value.
- **Options.** (a) literal: `oe_extreme` from closed 1m at decision (implemented now) · (b) structure extreme **at
  fill** including 5s bars, provided to the simulator as a precomputed STRUCTURE anchor path (step function over the
  order's life), so execution never reads structure bars (D16) · (c) `t3.sweep_extreme` up to the break.
  Related: whether location (`pos`) and OE duration should use 5s-inclusive extremes.
- **Constraint.** Decided on spec fidelity and parity evidence (Phase 13), never trade outcomes. Interacts with OQ-28.
- **Owner ruling D17-2 (2026-09-15): RESOLVED.** Stop anchor = the most adverse canonical STRUCTURE extreme belonging
  to the active extension, observed causally up to entry activation / fill (SHORT highest, LONG lowest). A STRUCTURE
  price; spread and the final executable stop belong to execution. Kept separate: extension extreme at candle open,
  evolving extreme, sweep extreme, structure extreme at activation, at fill, final execution stop. CX-LT1-1 supports but
  doesn't universally validate it; contradicting Level 1 evidence reopens OQ-35.
- **Status.** `RESOLVED` (D17-2).

### OQ-36 · Outcome basis of "raw setups that played out" (M15-COND-03; extends OQ-05)
- **Problem.** COND-03 needs past setups that reached target before stop. Under D16 signal code can't read bid/ask, and
  execution doesn't exist yet.
- **Handling now.** Raw setups are resolved on STRUCTURE 5s bars: trigger touch within the order window, then target vs
  stop touch (stop = anchor ± buffer, no spread), stop first on the same bar, forced flat at the rollover flat window. Only
  outcomes resolved by the candle open count. No aggregate outcome statistics are produced.
- **Options.** (a) STRUCTURE touches (implemented; mirrors how a chart shows "played out") · (b) execution-layer
  outcomes fed back once 14A exists (couples signal logic to execution assumptions).
- **Observation (not a decision input).** On the three course-example windows COND-03 failed for every candidate; on
  CX-TE1-1 four candidates failed only COND-03.
- **Owner ruling D17-3 (2026-09-15).** Current interpretation **NOT approved**. COND-03 is not removed, weakened, zeroed
  or reinterpreted by signal count. An **OQ-36 evidence resolution package** from Level 1 evidence is required before
  CBR15 is baseline-eligible: Tom's exact language (working/previous/played out/resolved/active setup), what "working
  setup in the previous hour" means, the terminating event, when it's evaluated, which structure tier it uses, and
  visual examples; each interpretation with evidence id, video, timestamp, quote, machine reading and consequences for the
  examples. No P&L, no choice by signal count. Insufficient evidence → reported unresolved for owner decision.
- **Evidence package (D18-1).** `docs/decisions/oq36-prior-setup-evidence.md`. "Played out" isn't defined in Level 1
  evidence; the hard clause is "zero setups in the last hour". Unresolved on evidence; candidate owner assumption C′.
- **Owner ruling D19-1 (2026-09-15): RESOLVED (reading C′).** The hard requirement is the EXISTENCE of a qualifying
  same-model prior setup FORMED in the model's lookback, never whether it played out, reached target, resolved, touched
  a level or filled. Implemented: a qualifying setup = a raw setup (every rule except the prior rule passes; CBR15: hourly
  signal state not VETO) with decision time in CBR15 `[Q.t0 − 60 min, Q.t0)` / CBR1H `[H.t0 − 10 h, H.t0)` (CBR1H
  lookback ASSUMPTION, own config). Fields `prior_setup_exists`, `prior_setup_count`, `prior_setup_latest_time`,
  `prior_setup_played_out_status = UNKNOWN` (non-blocking). The candle-geometry reading A (needs a reversal-size
  threshold, i.e. a level touch) was not used.
- **Status.** `RESOLVED` (D19-1).

### OQ-37 · CBR15 location in a trending range without a direction
- **Problem.** M15-LOC-02/03 need `cond.direction` (UP/DOWN). When the LTF swings give `NONE`, the CBR15 spec is silent.
  The CBR1H spec blocks this case (M1H-COND-03, ASSUMPTION).
- **Handling now.** `M15-LOC-TR-NODIR = False` (blocked by analogy), recorded per candidate.
- **Owner ruling D17-4 (2026-09-15): RESOLVED.** Don't infer direction. The case is `TREND_DIRECTION_UNRESOLVED`, a
  deterministic context failure rejecting the setup from canonical eligibility, recorded in the ledger. Future Level 1
  evidence defining a direction rule reopens it.
- **Status.** `RESOLVED` (D17-4).

### OQ-38 · Type 3 break before the 7.5-minute fill window
- **Problem.** A 5s type 3 can arm and break (on STRUCTURE price) before mic 7.5. M15-TIME-01 allows fills only from 7.5.
  A stop order placed after an earlier break would fill at the window open beyond the trigger.
- **Handling now.** Lifecycle cancel `T3_BREAK_BEFORE_WINDOW` at the structure break time (the shift fired in the first
  half, E15-027 "second half" entries). A setup re-arms only on a new sweep.
- **Owner ruling D17-5 (2026-09-15): RESOLVED.** A type 3 resolving before minute 7.5 isn't a valid CBR15 entry and
  doesn't stay armed (`TYPE3_RESOLVED_TOO_EARLY`). A new, causally independent type 3 later in the same candle is
  evaluated normally if its qualifying break falls in the second half. The early one is never resurrected.
- **Status.** `RESOLVED` (D17-5).

### OQ-39 · CBR1H entry trigger: spec entry models vs the course examples (Phase 12 parity)
- **Conflict.** The spec's CBR1H entry models are 6A `HVCS_HILO` (1m, or 5m when LVCS) and 6B `FRACTAL_1M` (1m type 3
  → 50% pullback → HILO). All three hourly course examples enter on a **5-second shift**:
  - CX-LT1-1: "Had a shift of market structure on the 5 second to get the low to take out a high" (V1H-live_trade_1, 00:02:47);
  - CX-TE1-1: "i just entered off the break of that high because it's a second shift um it's a bit of a high low entry as well but yeah more of a second shift" (V1H-trade_example_1, 00:12:17);
  - CX-LT3-2: seconds shift with DXY/gold-spread correlation (V1H-live_trade_3, 00:15:20).
- **Parity (Phase 12).** 6A reproduces entry time and stop anchor within MATCH tolerance on all three examples and the
  structure trigger within MATCH (CX-LT1-1, CX-LT3-2) or FEED_NEAR (CX-TE1-1, −$1.50) tolerance, but prescribes a HILO tier that conflicts with the nearest candidate on CX-LT1-1 (5m required, LVCS) and
  CX-LT3-2 (1m required). 6B reproduces **none** (no completed 1m type 3 in those hours).
- **Options.** (a) keep 6A/6B as written · (b) add a 5-second type 3 entry model for CBR1H (as CBR15 §7), as a new
  variant · (c) define the HILO tier differently. Decided on Level 1 evidence, never outcomes.
- **D18 note.** The Phase 12 tolerances and "closest to Tom" candidate selection quoted above were rejected (D18-8/9);
  those MATCH/FEED_NEAR labels are not evidence.
- **Evidence package (D18).** `docs/decisions/oq39-hourly-entry-evidence.md`: Level 1 evidence is strong that the 5s
  shift **is** the CBR1H trigger in both setups (HVCS→HILO/5s shift; 1m T3 → 50% → 5s shift), with the 1m HILO as a
  declared equivalent; kept as distinct variants. Canonical rule unchanged pending owner.
- **Owner ruling D19-2 (2026-09-15): RESOLVED (reading A).** The 5-second structure shift is the canonical CBR1H entry
  trigger; variants A (HVCS → 5s shift) and B (1m type 3 → ≥ 50% pullback → 5s shift) stay distinct. A 1m HILO is an
  observable equivalent only. Implemented: candidates are 5s type 3 sweeps; fields `entry_model`, `parent_structure_type`,
  `parent_structure_time`, `five_second_shift_time`, `five_second_shift_level`, `activation_time`; the 6A HILO-tier rule
  is removed (LVCS recorded as diagnostic); a 1m parent is used only after its bar close.
- **Status.** `RESOLVED` (D19-2).

### OQ-40 · Condition window across market closures (CBR1H 8 h, CBR15 2 h)
- **Problem.** `condition.classify` measures its window in clock hours. On CX-LT3-2 (Monday 01:00 UTC) the 8 h window
  starts Sunday 17:00, inside the weekend closure; only ~2 h of trading data qualify, giving 0 MTF legs → `UNDEFINED`.
  Tom: "very bullish, a little bit trendy" (V1H-live_trade_3, 00:01:07).
- **Options.** (a) clock hours (implemented) · (b) trading hours (skip expected-closed minutes, reaching back into
  Friday) · (c) block the first hours after a weekly reopen as insufficient context.
- **Evidence package (D18).** `docs/decisions/oq40-42-context-timing-evidence.md`. No explicit statement; chart
  walkthroughs are consistent with tradable time / contiguous bars; no support for session segments or a reopen block.
  `CONDITION_WINDOW_UNRESOLVED`; B is the assumption candidate. No reading makes CX-LT3-2 eligible (B/C →
  `TREND_DIRECTION_UNRESOLVED`).
- **Owner ruling D19-3 (2026-09-15): ASSUMPTION recorded.** Scheduled closures don't consume the condition window; it
  advances only in scheduled-tradable time; unexpected vendor gaps stay in the timeline as missing data. CBR1H
  `cond.window_basis = TRADABLE` (ASSUMPTION, research range CLOCK/TRADABLE, sensitivity only under the approved research
  process). Fields `condition_elapsed_clock_minutes`, `condition_tradable_minutes`, `condition_missing_minutes`. No other
  rule changed for CX-LT3-2. CBR15: see OQ-45.
- **Status.** `RESOLVED AS ASSUMPTION` (D19-3).

### OQ-41 · Reference candle for `oe_prev_candle_break` in CBR1H
- **Reading implemented.** The 15m candle before the one containing the decision time (a decision on a 15m boundary
  belongs to the ending candle). CBR15 uses Q−1 for its own candle. The spec says "the previous candle of timeframe 15m"
  without fixing the reference point for an hourly setup.
- **Evidence package (D18).** Same package. Strong for Q−1 relative to the current 15m candle, **broken by that candle**
  (the implemented check uses the hour's OE extreme and can pass without it); exception when Q−1 closed in the trade
  direction. No effect on the three examples.
- **Owner ruling D19-4 (2026-09-15): RESOLVED.** Q−1 = the previous completed 15m candle; the break must be made by the
  current candle Q itself. CBR1H 6A: `M1H-6A-2-PREV-15M-BROKEN-BY-Q` = Q's closed 5s bars take Q−1's high/low before the
  decision, or Q−1 closed in the trade direction (exception, E1H-023 and V1H-1m_fractal_shift 00:03:23). CBR15
  `M15-LOC-04` already tests Q's own extreme against Q−1; no CBR15 exception is encoded (the 15m-course quote at
  V15-hourly_cb_structure 00:05:05 concerns the previous hourly candle in an excluded model).
- **Status.** `RESOLVED` (D19-4).

### OQ-42 · M1H-TIME-02 (:30 candle veto): fill time vs decision time
- **Reading implemented.** The spec conditions on "the fill occurs in the 15m candle opening at :30". Fills are execution
  (D16), so the engine evaluates the veto for orders whose activation falls in that candle, using data before the
  decision; the :15 exception uses the closed :15 candle. An order armed before :30 that fills after :30 isn't vetoed.
- **Evidence package (D18).** Same package. Moderate: signal eligibility judged by how the shift forms, at the structure
  break; the implemented activation-time reading is unsupported. A true-fill reading would be `EXECUTION_DEPENDENT`.
  Hard veto vs quality downgrade ambiguous. No effect on the three examples.
- **Owner ruling D19-5 (2026-09-15): timing RESOLVED; hard veto UNRESOLVED.** Evaluated at the 5s shift time, never at
  arm time. Until veto semantics are approved it is the diagnostic `timing30_state` (PASS / QUALITY_CONCERN /
  NOT_APPLICABLE / UNRESOLVED) and never rejects a signal; `M1H-TIME-02` is removed from the rule set.
- **Status.** `PARTIALLY RESOLVED` (hard veto vs quality downgrade open).

### OQ-43 · HVCS "end_bar ≤ as_of" (6A condition 1)
- **Reading implemented.** Valid when the longest HVCS in the extension direction ending at any closed 1m bar of the hour
  up to the decision lasts ≥ 4 minutes; its body size decides the LVCS/5m tier.
- **Evidence package (D18).** `docs/decisions/oq39-hourly-entry-evidence.md` §OQ-43. Moderate: the HVCS runs directly
  into the shift (last displacement bar, indecision gap bars allowed, no source number for the limit); "anywhere in the
  hour" unsupported. Material: adjacent readings make the HVCS invalid on CX-TE1-1 and CX-LT3-2.
- **Owner ruling D19-6 (2026-09-15): principle RESOLVED.** The HVCS runs directly into the shift; it ends at the final
  displacement bar (implemented: the closed 1m bar that set the extension extreme); indecision bars may follow only while
  they don't break the side the sequence respected. No indecision count (see OQ-44).
- **Status.** `RESOLVED` (principle); count → OQ-44.

### OQ-44 · HVCS indecision bars between the displacement and the shift (D19-6)
- **Problem.** Level 1 allows indecision bars between the last HVCS bar and the shift ("it can be multiple candles",
  VP2-1m_hilo_entries 00:04:49) but gives no maximum.
- **Handling now.** No number. Continuity is structural: every closed 1m bar after the end bar must keep the respected
  side (DOWN: high ≤ end bar high; UP: low ≥ end bar low) up to the decision.
- **Owner ruling D20-4 (2026-09-15): RESOLVED AS ASSUMPTION.** The deterministic continuity reading is approved as an
  ASSUMPTION (not CANON); no maximum indecision count. Diagnostics recorded, never filters: `hvcs_start_time`,
  `hvcs_end_time`, `hvcs_extension_extreme_time`, `bars_between_hvcs_and_shift`, `indecision_bars_between`,
  `continuity_state`. The eligibility blocker is removed. Subject to later sensitivity analysis under research governance.
- **Constraint.** Never tuned on the course examples.
- **Status.** `RESOLVED AS ASSUMPTION` (D20-4).

### OQ-45 · CBR15 condition window across closures (D19-3 scope)
- **Problem.** D19-3 lists the tradable-time window change for CBR1H. The CBR15 2 h window crosses the daily break (1 h)
  and the weekend the same way.
- **Handling now.** CBR15 `cond.window_basis = CLOCK` (unchanged, ASSUMPTION); the three duration fields are available
  from the shared helper.
- **Owner ruling D20-5 (2026-09-15): RESOLVED AS ASSUMPTION.** CBR15 uses tradable-market time like CBR1H: scheduled
  closures don't consume the window; vendor outages and unverifiable gaps stay in time and remain visible in
  `condition_missing_minutes`. The rule uses `condition_tradable_minutes`. An engineering interpretation of time
  measurement, not a claim Tom taught closure handling; not optimized.
- **Status.** `RESOLVED AS ASSUMPTION` (D20-5).

### OQ-31 · How does the ledger use the hindsight vendor-gap mask? (Phase 10)
- **Problem.** At a decision time inside a DXY CFD vendor outage, a causal module can't yet tell the outage from thin
  quoting. The Phase 10 module shows the last quote for up to `max_quote_age_minutes` (10, IMPL) with REDUCED
  confidence before it goes UNAVAILABLE; the causal vendor-gap flag fires only after a 30-min run with 15 active DX
  minutes. The Phase 9 detector over the whole day (`dq_hindsight_*`) knows the outage immediately, but that uses future
  data.
- **Options.** (a) Causal fields only: a signal decides on what was knowable; the hindsight mask is reported but never
  changes membership · (b) the hindsight mask labels ledger rows (`data_confidence` → REDUCED/UNAVAILABLE and reason
  code) without changing whether the engine emitted a signal · (c) the hindsight mask excludes affected signals from
  baseline statistics (data-quality exclusion; hindsight about data, not about price outcomes).
- **Constraint.** The engine may never read `dq_hindsight_*` (enforced by column naming and the CBR-ACC-010 AC10-04b
  isolation test). Decided before Phase 15, never by profitability.
- **Owner ruling D15-1 (2026-09-14).** Stays **OPEN** until before baseline statistics. Owner preference **Option B**:
  affected rows stay in the ledger, keep causal DXY availability at decision time, and get a hindsight
  lower-confidence/data-quality label; **no automatic exclusion** from the canonical baseline (exclusion would be a new
  data-selection rule not in Tom's method). Baseline reports compare ALL SIGNALS vs SIGNALS WITH FULL DXY DATA as a
  diagnostic only; the subset is never promoted to the canonical result without explicit approval.
- **Status.** `OPEN` (owner preference B; confirm before baseline statistics).

### OQ-17 · Stop placement on the 15m model: tight vs breathing room
- **Problem.** Course: no tight stops (E15-040). One journal trade uses a tight stop; another journal loss is
  blamed on a stop that was too tight (Level 2).
- **Proposed default.** Course rule (conservative stop).
- **Status.** `RESOLVED` in favour of Level 1.

---

## C. Provenance and scope (need you)

### OQ-18 · Three long hourly recordings
`in_depth_backtesting_strategies…` (1:26), `mastering_entry_timing…` (1:24), `mastering_market_structure…`
(1:57). Course lessons (Level 1) or live sessions/webinars (Level 2)? Currently tagged
`provenance_unconfirmed`. **`NEEDS USER DECISION`** (batch Q5)

**Evidence gathered (verified in transcripts):** all three sound like recorded live community calls:
"Yep, I'm recording" / "I can record the chat as well" (backtesting call, 00:01:26, 00:16:26; browser shows a
Discord "Group Calls" tab and an FX Replay session "Feb Call Backtest"); "Feel free to tap in chat" and "with the
course content…" (entry-timing call, 01:02:49, 01:23:05, which refers to the course as something separate);
"i'm recording i will upload it", "out of anyone in this call", "i do live trading live analysis every friday"
(market-structure call, 00:47:58, 01:49:27, 01:55:51). **Recommendation: Level 2** (author's own words, but live
Q&A, not the structured course). 84 extracted records: `research/examples/long_recording_candidates.jsonl`.

Related, resolved: course video `Live_Trade_3_-_Gold_Win` is the same trade as public journal video
JuvmTSvghFI ("Live Day Trading Making $6,030", uploaded 2025-11-10). Charts show Mon 10 Nov '25 12:23-12:53
UTC+11, durations match (1771.85 s vs 1772 s), and the TradingView P&L column's latest row reads 6,030.00
(frame `research/frames/V1H-live_trade_3_gold_win/slides/00-28-58.jpg`, checked). Counted once, as Level 1.

### OQ-19 · USDJPY examples
`Live_Trade_2_-_UJ_Loss` and the correlation lesson use USDJPY. **`RESOLVED` (user, 2026-09-14): scope is
XAUUSD and DXY only.** UJ passages may clarify how a rule is applied; no UJ parity fixtures, data or rules.

### OQ-20 · Notion "Advanced Trading Journal" template
The course links a Notion template containing the author's CBR trades with variable tags and entry
screenshots (E1H-049). It's the best available source of reference setups. **Do you have access?**
**`NEEDS USER DECISION`** (batch Q1)

---

## D. Evidence from the long recordings (provenance unconfirmed; not applied to specs yet)

Record ids refer to `research/examples/long_recording_candidates.jsonl`. None of these change a spec until OQ-18
is decided. If classified Level 2 they can only clarify, never redefine.

| Topic | What the calls say | Relation to course rules | OQ |
|---|---|---|---|
| Minimum hourly extension | "at the very least 18 minutes of extension without a big pullback", 20+ as the rule; a big pullback restarts the count; a slow start delays the earliest entry equally (LR-40…43) | Sharpens CBR1H-OE-001 (20-30 min) with a hard floor | none |
| MTF window | "5h, maybe up to 8" (board: 5h-8h), later "5 to 12"; backtest ranges 3.5-15 h (LR-27, 59, 61) | Conflicts in part with E1H-005 (5-12+ h) | OQ-03 |
| Swing counting | counts "pushes and pulls" over ~5 h: ~3 too few for hourly CBR, ~7 fits; 9 in 3 h → seconds entries; no pivot rule (LR-47, 60-62) | Clarifies; still no deterministic swing definition | OQ-01 |
| Entry window | preferred :30-:52 (LR-39) | Conflicts with "best ~:37" / slide 20-45 m (E1H-024, E1H-002) | none |
| Prior-CBR check | a clean CBR in the past 4-5 h is a plus, not required ("I don't have data to back it up"); take the 2nd-4th, not the 1st (LR-28, 48, 73) | Softens E15-008/E15-049 (required, 5-10 h); leg rule close to E15-007 | OQ-05, OQ-06 |
| "High volume" | no fixed price thresholds, since typical range size roughly tripled 2022→2025; a 1-2 candle sequence is too extreme; wants a large breaking candle (LR-55, 65, 66) | Supports volatility-normalized proxies | OQ-08 |
| HILO / HVCS | 1m HILO = a shift on the seconds chart; HVCS→HILO = seconds overextension into seconds shift; taking the prior 15m H/L is "more crucial" for HILO entries (LR-64, 74, 75) | Clarifies E1H-003/E1H-034 | OQ-09 |
| Entry chart by candle size | 4h CBR → 1m fractal shift; 1h → 1m fractal shift or HILO/5s; 15m → always HILO/seconds; seconds chart = 5s (LR-31, 63) | Consistent with E15-037, E1H-032 | OQ-10 |
| Stops | breathing room, no size; external stop default (LR-19, 20) | Consistent | OQ-11 |
| Targets | 50% of the **current hour's** overextension, not prior moves (LR-77); in practice took 1:1 and <50% targets (LR-21…23) | Clarifies E1H-037 | OQ-12 |
| Correlation | optional; not used anywhere in the backtest (LR-6, 35) | Supports "optional" (vs journal veto) | OQ-13 |
| Sessions | Tokyo from hour 2; London from 1 h before open to hour 3 (LR-8, 70) | Conflicts with E1H-042 windows | OQ-16 |
| Levels/AOI | "lowest priority" (LR-49) | Supports AOI optional | OQ-07 |

**Author-reported statistics (claims, not evidence of edge):** manual FX Replay backtest of ~10 trades over 6
days in Aug 2025, 8W/2L, avg win 1.78%, avg loss −0.6%, PF 11.55 (LR-7), on a month he chose for its
favourable condition (LR-4), so the sample is selection-biased and tiny. 3-4 trades/week (LR-57). Ranges beat
trends in his records (LR-58).

---

## E. Phase 2 general lessons (Level 1; `research/examples/phase2_general_candidates.jsonl`, 76 records)

| Topic | What Phase 2 says | Effect | OQ |
|---|---|---|---|
| **Confluence priority** (slide, frame-checked) | 1. MS Align (direction H/L, condition push/pull, LTF 10-30m / MTF 5h / HTF 1+ day → entry relativity 50% fib, 30m/1h AOI); 2. 1h CB timing (15m intervals: trendy 0-15m continuations, rangey 15-30m reversals); 3. Correlation. "The best trades are when price is overextended." | MS alignment is his #1 requirement (P2G-22), conflicting with E1H-045 recorded as OPTIONAL | OQ-03, OQ-21 |
| **TRR Forever Model** (slides) | Trend Range Rejection: trade in overall direction; range-bound/trending-range condition; ≥50% retracement; 30m/1h open-close AOI; high-volume overextension into it; LTF shift (1m, tick, HILO) at :15/:30/:45 ±3 min; stop beyond shift low; target next hourly level / range high; 1-2 trades/week (P2G-1, 2, 9) | A complete, largely codeable model. Candidate **third baseline** alongside CBR15/CBR1H | OQ-07 |
| Swings / condition numbers | Swing choice "intuitive"; "can't give you purely mechanical rules" (P2G-16, 66) | Confirms OQ-01/02 must be research parameters | OQ-01, OQ-02 |
| Volume | High volume = impulse candles large relative to pullbacks, or price reaching the AOI right after the hourly open (P2G-7, 12) | Proxy candidates for OQ-08 | OQ-08 |
| Stops | Plan slide: "SL behind prev candle high/low", avoid tight stops (P2G-40, 13) | Conflicts with external-extreme stop (E1H-036) | OQ-11 |
| Targets | Next hourly level or range high; "TP before next HTF Level", ~1.5R (P2G-14, 41) | Adds a level-based target variant | OQ-12 |
| Trend | Filters trends by waiting for a lower-half pullback; trending + high volume → switch to continuations (P2G-65, 28, 64) | Supports OQ-21 option B (downgrade/switch model), not a ban | OQ-21 |
| Type 1/2/3 | Speech makes type 2 and type 3 indistinguishable (P2G-70) | Still needs Phase 1 | OQ-09 |

**Author-claimed statistics (no sample sizes; hypotheses only):** overall 61% → 80% with DXY spoken, 56% → 73% on
slides (P2G-42, 51, 36); 30m continuations 46% vs 30m reversals 90% (P2G-30); reversal win rate by minute
51.9% at :00 → 75% at :30; continuations 66.7% at :00-:10 (P2G-47); trading against no-wick candles 38%
(P2G-44); first half of Asia 33% (P2G-55); plan page +1.67R avg win / −0.835R avg loss / 83% (P2G-41). Journal
said to hold ~350 trades (P2G-37). The spoken and slide DXY figures disagree.

---

## F. Phase 1 foundations (Level 1; `research/examples/phase1_foundation_candidates.jsonl`, 72 records)

| Topic | What Phase 1 says | Effect | OQ |
|---|---|---|---|
| **Swing points** | No objective rule. Board slide (third-party graphic): "SWING occurs when price breaks an old High or Low" (P1F-3); internal/external and strong/weak highs/lows labelled, not explained (P1F-23); HH/HL illustrated as consecutive candle highs/lows (P1F-30); line chart endorsed for reading swings (P1F-6) | Supports **break-confirmed swings** (a high becomes a swing once price breaks the prior low, and vice versa) over N-bar pivots. Still a research parameter | OQ-01 |
| **Condition** | No numbers. Range = "equal push and pull"; trend = push outweighs pull; trending range = "almost equal push and pull but directional"; judged from past structure only (P1F-7, 15, 16, 18, 20, 21) | Consistent with 75-100% / 50-75% / <50% reading of later courses; thresholds remain `ASSUMPTION` | OQ-02 |
| **Levels / AOI** (slide checked) | "A new level forms when there is a shift in candle close direction" (hourly); zones = general area around the LTF highs/lows at that level; refine hourly → 15m → 1m; choose clearest, most recent, most touched (P1F-48…51) | **Level definition `RESOLVED`** (= open/close at a Type 1 candle pair). Zone width still a parameter | OQ-07 |
| **Durations** | HTF days-weeks, MTF 4-8 h, LTF 1-2 h; informally "past 15 min / past hour" (P1F-24, 57) | A fourth tier set; confirms tiers are fuzzy. Keep per-use definitions from OQ-03 | OQ-03 |
| **Sessions (gold)** (frame checked) | Asia = Tokyo+Sydney, chart 10:00-~19:00 UTC+10 = **00:00-~09:00 UTC**; trades "the second hour of Tokyo" = 01:00-02:00 UTC; never trade gold in Sydney session; don't trade/hold through daily rollover (P1F-67…70) | Session anchor `RESOLVED` for Asia; rollover exclusion is a new canonical no-trade rule | OQ-16 |
| **Daily candle bias** | Previous day closed bullish → expect a bottom wick / bearish move early in Asia; "don't look for buys" until the day's wick forms (P1F-45, 46, 60) | **Conflicts** with "don't worry about candle behavior day" (E1H-028). Becomes an ablation: daily-type-1 context filter | OQ-15 |
| **Candle timing** | Continuations form the opposite wick in the first half then push; journal rows show 30-min reversals entered ~:31-:34, continuations :01-:09 (P1F-31, 32, 59, 62) | Consistent with hourly/Phase 2 timing | none |
| **Plan page** | SL behind previous candle high/low; TP next HTF level ~1.5R; 1-2 setups/day (P1F-58) | Conflicts with E1H-036/E1H-037 and his "3-5 trades a day" remark. Stop/target variants for ablation | OQ-11, OQ-12 |
| **No-wick candles** | Trading against a no-wick candle lowers probability (P1F-35) | Tension with fading overextensions (E1H-020) | OQ-08 |

---

## User decisions (2026-09-14)

| # | Decision | Affects |
|---|---|---|
| D1 | Fractal-shift / inverse-fractal-shift setups **excluded** from baseline V1; later separate model | OQ-04 |
| D2 | Python engine uses **5-second bars built from Dukascopy ticks**; Pine uses 1m entries labelled `SIMPLIFIED-ENTRY` | OQ-10 |
| D3 | **No session filter** in baselines (canonical no-trade rules still apply: Sydney session, daily rollover); author's windows tested as ablation | OQ-16 |
| D4 | Three long recordings classified **Level 2** | OQ-18 |
| D5 | **TRR Forever** becomes a third model, specified and built **after** the CBR baselines | Section E |
| D6 | Tom's Notion journal: **no access for now**; proceed with course examples and journal videos | OQ-20 |
| D7 | Scope XAUUSD + DXY only (earlier decision) | OQ-13, OQ-19 |
| D8 | Overextension origin: V1 keeps hour open; "last reset" tested as a single-rule ablation | OQ-22 |
| D9 | Early-shift handling: V1 unchanged; "final push" and "15m alignment" each tested as single-rule ablations | OQ-23 |
| D10 | Astra × Fable research governance adopted (CBR-GOV-001) | Governance |
| D11 | AC-11 split into AC-11A (required: 16-day stratified pipeline proof) and AC-11B (deferred full spot history); failures classified, not auto-FAIL; baseline feed (OQ-24) stays open until parity and cross-feed agreement, frozen before Phase 14, never chosen by profitability | OQ-24, Phase 9 |
| D12 | Phase 9 rulings: 2020-03-09 DXY hour = DATA_ERROR → MISSING, with detector `DXY_CFD_MISSING_WHILE_DX_ACTIVE`; 2019-03-11 DXY hour stays UNEXPLAINED → MISSING; new class REFERENCE_UNAVAILABLE; `cause_status` field; candle high/low construction is a hard safeguard before Phase 14; 1m/5s DXY structure not validated. Phase 9 PASS WITH CONCERNS, G1 approved with conditions | OQ-25, OQ-26, OQ-27, G1 |
| D13 | Backtesting.py integrated in Phase 14B as a secondary execution, metrics, visualization and parity layer; Phase 14A custom simulator is authoritative; signal contract immutable; parity thresholds pre-registered (CBR-ARCH-014 §7); no `optimize()` or parameter search in Phases 14-16 | OQ-28, OQ-29, OQ-30, Phase 14 |
| D14 | Phase 14 plan approved (not implemented; no Backtesting.py dependency). OQ-28 open: contract carries canonical stop inputs, not an executable stop. OQ-29 open: 5s CBR1H preserved; 1m only via Phase 13 evidence + proposed spec change. OQ-25: decision package due before Phase 11. OQ-30 open: licensing review before 14B. Phase 10 continues | OQ-25, OQ-28, OQ-29, OQ-30, Phase 10 |
| D15 | Phase 10 accepted (PASS WITH CONCERNS, G10 approved). OQ-31 open, preference Option B (label, don't exclude; ALL vs FULL-DXY diagnostic only). Daily DXY CFD unavailability accepted: `DXY_AVAILABLE = false`, no directional meaning. Engineering thresholds stay IMPL, never optimized. OQ-25 decision package next; Phase 11 not started | OQ-25, OQ-31, G10 |
| D16 | OQ-25 resolved: STRUCTURE = tick mid, EXECUTION = tick bid/ask, never one series for both, access guards + STRUCTURE/EXECUTION labels in schemas/manifests/reports. V-1 required before Phase 13 passes (reopen OQ-25 on material differences). Full tick history deferred (OQ-33). Phase 11 approved on downloaded tick days. Candle files and GC not canonical for extremes | OQ-25, OQ-33, Phases 11/13 |
| D17 | Phase 11 accepted (PASS WITH CONCERNS, G11: construction, causality, determinism); CBR15 not baseline-eligible. OQ-34 open until Phase 12 (NOT_EVALUATED neither pass nor fail). OQ-35 resolved: stop anchor = most adverse STRUCTURE extension extreme through activation/fill, fields kept separate. OQ-36 interpretation not approved; evidence package required. OQ-37 resolved: TREND_DIRECTION_UNRESOLVED context failure. OQ-38 resolved: TYPE3_RESOLVED_TOO_EARLY, no resurrection. F-3 approved. Phase 12 authorized | OQ-34…OQ-38, G11 |
| D18 | Phase 12 accepted (PASS WITH CONCERNS, G12); Phase 13 not authorized. Evidence packages required for OQ-36, 39-43; Phase 12 tolerances and "closest to Tom" selection rejected; independent tolerances and deterministic selection to be pre-registered; D8/D9 parity classification with STRICT COURSE and BASELINE-SPEC views; M15-HTF-01 signal vs execution state (`HTF_FILL_STATE = NOT_EVALUATED`); Phase 13 readiness checklist | Phase 13 |
| D19 | Phase 13 readiness rulings: OQ-36 C′ (prior setup existence, played-out diagnostic); OQ-39 A (5s shift = CBR1H trigger, variants A/B separate); OQ-40 tradable-time window (ASSUMPTION); OQ-41 Q−1 broken by Q (+ trade-direction exception); OQ-42 evaluated at the shift, hard veto unresolved (diagnostic); OQ-43 HVCS into the shift, no indecision count; parity protocol approved in principle (two views, deterministic selection, taxonomy, calibration method); numeric tolerances not frozen; V-1 hard gate; HTF signal/fill split; parity-candidate specs | Phase 13 |
| D20 | D19 follow-up: D19 implementation accepted; "setup formed" = `raw_setup_armed` (every setup rule except the recursive prior-setup rule; no fill/outcome); CBR1H prior window ends at H.t0 (10 h ASSUMPTION; window fields recorded); CBR15 Q−1 has no trade-direction exception; OQ-44 continuity approved as ASSUMPTION with diagnostics, blocker removed; OQ-45 tradable-market time for CBR15 (ASSUMPTION); HTF split unchanged; PC2 specs (PC1 kept); V-1 ingestion prepared, no course scoring | Phase 13 |
| D21 | D20 accepted; PC2 are the current frozen candidates; no strategy-definition work; V-1 preparation only: fetch and validate Dukascopy 2025-11-11, confirm both calibration days ready; calibration order when FOREXCOM files arrive (validate → calibration days only → OHLC residuals incl. per-field and intraday stability → zero-lag or STOP → proposed τ_p, never auto-frozen); no substitute feeds (V1_DATA_LIMITATION path) | Phase 13 |
| D22 | D21 accepted; calibration tool completed (open residual, missing minutes per source, p90, per-day / intraday / OHLC / time-block / volatility-regime stability; zero-lag STOP); inspect existing TradingView exports: Gold = FX:XAUUSD (SYMBOL_MISMATCH, REFERENCE_ONLY; higher timeframes TRADINGVIEW_REFERENCE_FIXTURE), 1m history insufficient; TVC:DXY evidence for OQ-26 (unchanged); deterministic slicing adapter; V-1 state V1_SYMBOL_MISMATCH; options A/B/C for owner | Phase 13 |
| D23 | Tom chart data (`references/tom-chart-data`): 12 TradingView exports, FOREXCOM:XAUUSD (PROBABLE_FOREXCOM) and TVC:DXY (PROBABLE_TVC_DXY, identical to owner TVC exports) at 1m/5m/15m/1h/4h/1D; 1m from 2026-09-09 only → V1_TOM_DATA_INSUFFICIENT; 1h covers all five windows; OQ-26: no 1m/5m/15m overlap with stored Dukascopy DXY (partial 1h/4h), OQ-26 unchanged; source families A-D kept separate; options for owner | Phase 13 |
| D24 | Phase 13 redefined as STRATEGY FIDELITY AND BEHAVIORAL PARITY: Dukascopy stays canonical (sufficiency, not identity); V-1 reclassified to supporting feed-fidelity validation (historical FOREXCOM 1m unavailable, TradingView limits); behavioral dimensions on the three hourly examples; FEED_DIFFERENCE vs FEED_DEPENDENT_SIGNAL_DIFFERENCE; FOREXCOM 1h/4h/1D supporting, recent 1m/5m/15m feed-comparison study approved; new gate A-G; categorical verdicts; PC2 unchanged; pass = faithful enough for execution and baseline testing | Phase 13 |

## Batched questions for the user (historical; answered above)

1. **Missing material.** Phase 2 received (HILO and HVCS now defined). Still missing: (a) **Phase 1**, which
   defines type 1/2/3 structure shifts; (b) access to Tom's Notion "Advanced Trading Journal" template?
2. **FS/IFS in baseline.** OK to leave fractal-shift / inverse-fractal-shift setups out of baseline V1
   (visual impulse detection) and add them as a later model?
3. **Seconds data.** OK to build 5-second bars from Dukascopy tick data for the Python reference engine, with
   the Pine baseline using 1m entries labelled as a simplification?
4. **Sessions.** Baseline with no session filter (author's Asia/London windows tested as an ablation)?
5. **Long recordings.** Course lessons or live sessions?
6. ~~USDJPY~~: resolved, XAUUSD + DXY only.

### OQ-46 · Trending-range direction test (raised in Phase 13R)
- **Problem.** `M1H-COND-03` blocks every CX-LT3-2 candidate because the MTF direction is `NONE`: in the 8 h window the
  last two highs fall (4027.53 → 4009.29) while the last two lows rise (3992.47 → 3994.55). Tom calls the same market
  "very bullish, um, a little bit trendy" (V1H-live_trade_3_gold_win 00:01:07).
- **Options.** A last two swing pairs (current) · B range position (where the hour opens inside the range) · C a
  directional measure over the window · D another evidence-backed reading.
- **Status.** `REVIEWED` (D28 §16): `docs/decisions/oq46-trending-range-direction-evidence.md` recommends classifying a directionless trending range as RANGE. Owner decision pending.

### OQ-47 · Does a type-3 sweep require a named external level? (raised in Phase 13R)
- **Problem.** T3-B (re-anchoring) reproduces all three course triggers but produces 1.66× as many raw 5s type-3 events
  as PC2. Restricting the sweep to a *named* external level (previous 15m candle high/low, range edge) would tighten it.
- **Evidence.** "you want it to be beyond low timeframe, middle timeframe structure, beyond previous high or low"
  (V1H-seconds_shift_1m_hilo_hvcs 00:01:47, L1); E1H-017.
- **Status.** `REVIEWED` (D28 §3): `docs/decisions/oq47-external-sweep-evidence.md` recommends option G (no separate external level on the sweep; externality stays in M1H-6A-2 and the LOC rules). Owner decision pending.
