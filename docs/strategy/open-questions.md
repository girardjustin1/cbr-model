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
- **Status.** `HARD PRECONDITION` for Phase 14 (gate G2d). Open.

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
