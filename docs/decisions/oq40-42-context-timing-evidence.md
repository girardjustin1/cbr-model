# OQ-40 / OQ-41 / OQ-42 Evidence Resolution Package: Condition Window, Previous 15m Candle, :30 Veto Timing

**Doc:** CBR-EVD-040 · **Version:** v1.0 · **Date:** 2026-09-15 · **Rulings:** D18-2, D18-3, D18-4 · **Status:** FOR OWNER DECISION
Specs are **unchanged** until the owner rules.

**Method.** Transcript, slide OCR and frame search.
- Every transcript quote below was verified mechanically against the JSON transcripts (**all verified, 0 failures, 0 timestamp mismatches**).
- Frame readings are marked as visual interpretations. Two key frames were re-checked by eye (V1H-live_trade_3 00:00:34; V1H-mastering_market_structure 00:32:10).
- **L2** = the three long recordings (D4).
- Effects on the examples come from `reports/phase13-readiness-diagnostics.md` (STRUCTURE facts, no P&L).

---

# OQ-40: condition window across market closures

## Evidence

| Id | Level | Video · time | Verbatim | Reading |
|---|---|---|---|---|
| E1H-005 | L1 | V1H-defining_mtf_ranges · 00:01:00 | "I define middle time frame as the past 5 to 12 plus hours." | a duration, not a chart timeframe |
| NEW | L1 | V1H-defining_mtf_ranges · 00:00:46 | "I only care about duration of price action." | unit = duration **of price action** (fits tradable time better than calendar time; not explicit) |
| NEW | L1 | V1H-defining_mtf_ranges · 00:01:20 | "It's not exact science, but it's a general sort of range." | fuzzy window |
| NEW | L1 | V1H-defining_mtf_ranges · 00:02:13 | "to just stay on the one minute timeframe and use the measure tool to look at, you know, five to" | measured on a 1m chart with the measure tool (shows bars and elapsed time) |
| NEW | L1 | V1H-what_direction_condition · 00:00:50 | "be a bit longer. It could be half a day, maybe almost up to around a day" | lookback can exceed 8 h |
| E15-004 | L1 | V15-defining_ltf_range · 00:01:21 | "So high timeframe range is 20 hours, middle timeframe, five to 10 and low timeframe," | tiers as hours |
| NEW | L1 | V15-defining_ltf_range · 00:09:18 | "frequency of highs and lows over different durations of price action to identify the" | condition judged by swing frequency |
| NEW | L1 | VP1-1_5_fractal_structure · 00:02:59 | "i say the past like eight hours um four to eight hours of price action is like middle time frame" | 4-8 h of price action |
| NEW (visual) | L1 | V1H-live_trade_3_gold_win · 00:01:07 + frame 00:00:34 | "So very bullish, um, a little bit trendy." | **CX-LT3-2 (Monday):** the DXY 1m chart axis runs "23:00 · 8 · 01:00 … Mon 10 Nov". Pre-weekend bars sit directly before Monday's, with a channel drawn across them |
| NEW | L1 | V1H-live_trade_3_gold_win · 00:17:47 | "It's not the best condition." | he knowingly took a weak condition: not a tuning target |
| NEW (visual) | **L2** | V1H-in_depth_backtesting… · 00:02:16 / 00:02:53 + frame 00:03:26 | "So we are Monday 10 a.m. So I think we'll wait for ... Second of Asia is 12" … "Yeah, I can't end this bullish trending range." | Monday replay: trending-range channel drawn from Friday through Monday |
| NEW (visual) | **L2** | V1H-mastering_market_structure… · 00:32:08 + frame 00:32:10 | "for example over the past that means it's over the fucking weekend is it why does it say three ... No, it's one day." | measure tool "1628 bars, 3d 5h 8m" across Fri→Mon; he rejects the clock reading ("one day" ≈ trading time) |
| E1H-042 | L1 | V1H-session_timing · 00:00:00 | "I mainly focus on around the second hour of Asia, sometimes the first hour for UJ" | Monday second hour of Asia is a normal time for him |
| NEW | L1 | VP1-1_3_conditions · 00:07:20 | "low volume and a more like ranging. ... I rather just wait for the second hour." | skips the Asia open for volume, not context |
| EP1-017 | L1 | VP1-trading_sessions_pairs · 00:02:01 | "But don't trade gold in Sydney session." | session exclusion only |

### Contradicting / ambiguous

| Id | Level | Video · time | Verbatim | Issue |
|---|---|---|---|---|
| E1H-006 | L1 | V1H-where_aoi_er_oe · 00:07:26 | "time frame um anything over an hour to two is a lot more middle time frame you know even into" | different tier scale (for moves) |
| NEW | L1 | V1H-defining_mtf_ranges · 00:01:51 | "to look back and see how has the past five to four plus hours been looking this is a lot more" | likely mistranscribed "5 to 12+" |
| NEW | L1 | V1H-mtf_model_types · 00:09:21 | "This is over the weekend," | frame shows Thu-Fri; no closure visible, so it tells us nothing |

No evidence supports D (session segments such as "since London" or "the Asian range").

## Interpretations and CX-LT3-2 effects (hour 2025-11-10 01:00 UTC, MTF 5m swings, frozen k and thresholds)

| Id | Interpretation | Supporting | Exact algorithm | Window | Condition | c_med | Legs | Direction | Hour rules pass | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | Elapsed clock time (implemented) | "past 5 to 12 plus hours" wording | bars with `t ∈ (as_of − 8 h, as_of]` | 8 h (from Sun 17:00) | UNDEFINED | — | 0 | NONE | **no** (COND-01/02) | ASSUMPTION for closures |
| **B** | Tradable (expected-open) time | frames (LT3-2 00:00:34; L2 00:03:26, 00:32:10), "duration of price action", 1m + measure tool | walk back over expected-open minutes only until 8 h collected | 57 h clock (from Fri 16:00) | TRENDING_RANGE | 0.678 | 3 | NONE | **no** (`TREND_DIRECTION_UNRESOLVED`) | ASSUMPTION (visual inference) |
| **C** | Populated bar count | as B (the measure tool shows bars) | last 96 × 5m populated bars | 57 h clock | TRENDING_RANGE | 0.678 | 3 | NONE | **no** (`TREND_DIRECTION_UNRESOLVED`) | ASSUMPTION |
| **D** | Session segment (since the last expected closure ended) | none | window from the end of the last expected-closed minute | since Sun 23:00 reopen | UNDEFINED | — | 0 | NONE | **no** | not supported |
| **E** | Structure frequency with a flexible length (refinement of B/C) | V15 00:09:18, what_direction 00:00:50, E15-008 | B/C, extending 5 h → up to ~12-24 h tradable until ≥ N legs; else UNDEFINED | — | not computed (needs N) | | | | | ASSUMPTION algorithm; CANON that frequency judges condition |

The other two examples don't cross a closure; A, B and C agree:
- **CX-LT1-1:** RANGE, 3 legs, pass (A 8 h clock; B/C 9 h because the daily break falls inside).
- **CX-TE1-1:** RANGE, 4 legs, pass (same).

D differs for CX-LT1-1: UNDEFINED (the window since the 22:00 reopen is only 3 h, 0 legs); for CX-TE1-1 D is RANGE, 3 legs, and passes.

## Assessment

- **Weak-to-moderate.** No statement in words covers closures. Three independent chart walkthroughs are consistent with **B/C**: pre-closure bars count toward the window. Pure clock time (A) is not what Tom does on Mondays.
- **E** is a compatible refinement.
- **No reading makes CX-LT3-2 eligible.** B and C become a trending range whose direction is unresolved (D17-4), and Tom himself called it "not the best condition".
- **Proposed handling if the owner wants an assumption now:** **B (tradable time)** as an explicit ASSUMPTION, with `CONDITION_WINDOW_UNRESOLVED` recorded until ruled.

---

# OQ-41: which previous 15m candle?

## Evidence

| Id | Level | Video · time | Verbatim | Reading |
|---|---|---|---|---|
| E1H-034 | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:01:25 | "I would say the previous 50 minute candle higher low." | previous 15m candle high/low ("50" = "15", transcription) |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:01:33 | "you want this current 50 minute candle to push" | the **current** 15m candle does the breaking |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:02:50 | "and so what that's going to look like this is the previous 15 minute candle here you have the" | walkthrough: previous candle → next opens and pushes → shift in its second half |
| E1H-017 | L1 | V1H-where_aoi_er_oe · 00:09:15 | "this 15 minute candle here is external we've taken out the low of the previous 15 minute candle low" | same definition; Notion "External" options: Prev CB H/L 15m, LTF, MTF, HTF |
| NEW | L1 | V1H-trade_example_1 · 00:08:22 | "we broke in the previous 15 minute low so we were outside of that as well that's just what external" | same |
| E1H-021 | L1 | V1H-candle_behavior_extension · 00:02:47 | "push bearish again ideally i want to take out the previous low for a buy take out the previous high" | said of the :30 candle |
| NEW (visual) | L1 | V1H-candle_behavior_extension · 00:07:32 + frame 00:07:38 | "nice volume come in at the uh the second half of the hour you take out the previous 50 minute" | a line at the **:15-:30 candle** low, broken by the :30 candle: reference = Q−1 of the breaking candle |
| NEW | L1 | V1H-candle_behavior_extension · 00:04:56 | "You take out the previous high, which is nice." | after the :30 candle opens |
| NEW | L1 | V1H-1m_fractal_shift · 00:07:04 | "previously previous 15 minute candle closes bearish so we kind of want it to take out the" | the new :30 candle takes the :15 candle's low |
| NEW | L1 | V1H-live_trade_3_gold_win · 00:07:47 | "What I'm kind of waiting for, looking for, is a 5 minute, 15 minute candle to open, take" | live: the next candle takes the previous high |
| NEW | L1 | V1H-trade_journal · 00:00:46 | "bullish nice volume 15 minute counter behavior takes up previous high and 37 minutes into the" | journal definition |
| NEW | L1 | V15-15m_cb_timing · 00:06:26 | "does the five minute candle open you extend above uh take a previous five minute candle high you" | fractal: previous 5m candle when aligning 5m candle behaviour |
| E15-034 | L1 | V15-hourly_cb_structure · 00:04:36 | "uh over extend to take out a high and then look for a shift back in towards 50 percent here" | CBR15: "a high", not named |
| NEW | **L2** | V1H-mastering_market_structure… · 01:03:12 / 01:03:56 / 01:04:27 | "How crucial is it based on the data that the new 50 minute candle takes up previous 50 ... minute candle high or low before high low forms?" … "because it's unlikely that ... you'll get a good entry if it doesn't ... break the previous 50-minute" … "like likely on a good extension on this 50 minute candle it's going to take out the previous high" | new candle takes the previous candle's H/L before the HILO |

### Contradicting / ambiguous

| Id | Level | Video · time | Verbatim | Issue |
|---|---|---|---|---|
| E1H-034 | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:01:22 | "and you want it to go beyond the previous low timeframe," | LTF/MTF offered before narrowing to the 15m candle |
| NEW | L1 | V1H-where_aoi_er_oe · 00:08:26 | "low time frame, middle time frame, and high time frame, and then this previous 15 minute candle." | four separate "external" categories |
| E1H-023 | L1 | V1H-candle_behavior_extension · 00:07:55 | "the previous high um is if you have like a nice shift set up or nice 15 minute candle uh close" | exception: not needed when the previous candle closed in the trade direction |
| NEW | L1 | V1H-1m_fractal_shift · 00:03:23 | "closes in our action i don't really need it as much to take out the previous low like it's okay" | same exception |
| NEW | L1 | V15-hourly_cb_structure · 00:05:05 | "but yeah it's just some examples i don't need uh this to you know take out the previous low" | same exception (CBR15) |
| NEW | **L2** | V1H-in_depth_backtesting… · 00:18:58 / 00:40:46 | "You want to take out the previous middle timeframe." … "you take out the proof is high on the 30 minute as well" | structural reference when counter-MTF; unclear 30m |

## Interpretations and effects

| Id | Interpretation | Algorithm | Examples (at Tom's entry) | Status |
|---|---|---|---|---|
| **R1** | Previous 15m candle `P = Q−1` relative to the current 15m candle `Q` in which the push, shift and entry occur, **broken by Q itself** before the shift | `max(high[Q.open, trigger)) > P.high` (SELL; mirror BUY); exception recorded if `P.close` in trade direction (E1H-023) | all three: break = true | reference candle CANON; strict ">" and trigger as reference point ASSUMPTION |
| R1′ (implemented) | Candle before the one containing the decision time, tested on the **hour's** `oe_extreme` | `oe_extreme > high(Q_dec − 1)` | all three: true | differs from R1 when the hour's extreme was set in an earlier 15m candle (R1 rejects: the current candle didn't break) |
| R2 | 15m candle before the candle containing the OE extreme | `oe_extreme > high(Q_extreme − 1)` | all three: true | ASSUMPTION |
| R3 | Last 15m candle of the previous hour | `oe_extreme > high(H.t0 − 15m)` | all three: true | ASSUMPTION |
| R4 | Previous hourly candle | `oe_extreme > high(H − 1)` | all three: true | not supported |
| R5 | Structural LTF/MTF swing | last swing on the tier | — | CANON as a **separate** "external" category (`beyond_external`), not this primitive |

## Assessment

- **R1: strong.** The previous completed 15m candle relative to the current (shift/entry) candle, and the current candle must be the one breaking it.
- **The exception: moderate.** It holds when the previous candle closed in the trade direction.
- **Engine edge case:** the implemented reading (R1′) should be tightened to "broken by Q".
- **None of the readings change the three examples.**
- **CBR15** in-candle reference: moderate/ambiguous ("a high"; previous 5m candle when aligning 5m candle behaviour).

---

# OQ-42: the :30 veto timing

## Evidence

| Id | Level | Video · time | Verbatim | Reading |
|---|---|---|---|---|
| E1H-021 | L1 | V1H-candle_behavior_extension · 00:02:32 | "is when the 30 minute candle or the third 15 minute candle opens and then immediately continues" | positive template: :30 candle keeps pushing against the trade |
| E1H-022 | L1 | V1H-candle_behavior_extension · 00:05:33 / 00:05:39 | "candle uh immediately pushing bearish to create that shift that's not what you want um you want" … "the open of the 50 minute candle to continue pushing bullish take out the high and then to" | objection is to **how the shift is created**; order: push against, take the high, then shift |
| NEW | L1 | V1H-candle_behavior_extension · 00:06:28 | "but you don't want the the the shift to be forming um around 30 minutes in with that 50 minute kind" | keyed to **when the shift forms** |
| NEW | L1 | V1H-candle_behavior_extension · 00:06:18 | "shift here or you can have the shift happen where you have the new 50 minute candle open" | allowed alternative (previous candle closed in trade direction) |
| NEW | L1 | V1H-candle_behavior_extension · 00:07:05 / 00:09:08 | "and you immediately push bearish" … "continue to push in the same direction for another you know six seven minutes six seven um and then" | bad case vs best case (6-7 min against, shift ~:37) |
| NEW | L1 | V1H-live_trade_3_gold_win · 00:08:04 / 00:12:24 | "I'm not the biggest fan of immediately pushing bearish off a 5 or 15 minute candle open," … "So we've taken out previous hire." | live: declines the early shift; waits for the previous high to be taken |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:03:08 | "the entry on the break of the of the low on the break of this low i'm not waiting for a pullback" | stop entries: shift completion = fill moment |
| E15-028 | L1 | V15-15m_cb_timing · 00:05:29 | "open and it creates a shift here so the five minute candle opens it immediately dumps pushes bearish" | same rule one level down (CBR15) |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:42:42 | "wick um i'm not the biggest fan of that so ideally you want to to open push against you first" | push against first |

### Contradicting / ambiguous

| Id | Level | Video · time | Verbatim | Issue |
|---|---|---|---|---|
| NEW | L1 | V1H-live_trade_2_uj_loss · 00:22:51 | "Also not the biggest fan about how this fibrin account opened and immediately pushed bearish." | CX-LT2-2 (USDJPY): entered anyway → quality downgrade, not an absolute veto? ("fibrin account" needs a frame check) |
| NEW | L1 | V1H-live_trade_3_gold_win · 00:07:53 | "out the previous high, or just create a top wick, push against me, and then potentially" | a wick suffices; taking the high is ideal |
| E1H-022 | L1 | V1H-candle_behavior_extension · 00:05:48 | "the halfway point of this 50 minute candle most likely it'll shift bullish yeah and then just" | probabilistic language |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:10:51 | "the 30-minute open it's just as simple as that why um you know the 30-minute candle is like like" | a different timing rule; don't merge |

## Classification of the rule

| Id | Belongs to | Supporting | Exact algorithm | Status |
|---|---|---|---|---|
| **A** | **Signal eligibility** evaluated **at the moment the shift/trigger breaks** | E1H-022 00:05:33, 00:06:28; E15-028; LT3 00:08:04 | when the trigger breaks at `t_b` inside the :30 candle Q30, veto if Q30 never traded beyond `Q30.open` against the trade in `[Q30.open, t_b)`; exception: the :15 candle closed in the trade direction; diagnostic `took_prev_15m_extreme` | CANON (what is tested); time reference ASSUMPTION |
| B | Order activation (implemented) | none | veto if the order becomes active in Q30 | weakly supported; **conflicts** with A for orders armed before :30 and broken by an immediate :30 push |
| C | Fill eligibility (spec wording) | seconds_shift 00:03:08 | as A with `t_b` = fill time | identical to A for stop-at-trigger entries **on STRUCTURE**, but a true fill (EXECUTION) can differ from the structure break by the spread |
| D | Post-signal lifecycle | none | — | not supported |

**Effect on the three examples (diagnostics).** Evaluated both at Tom's entry (fill-time reading) and at the engine decision (arm-time reading):

| Example | Q30 push against the trade | Threshold (0.25 × ATR1m) | :15 closed in trade direction | Vetoed (either reading) |
|---|---|---|---|---|
| CX-LT1-1 | $17.43 | $1.01 | no | no |
| CX-TE1-1 | $3.92 | $0.54 | no | no |
| CX-LT3-2 | $5.56 | $0.71 | no | no |

## Assessment and D18-4 handling

- **Moderate evidence that the rule is signal eligibility tested at the shift break (A).** Tom's entries are stop entries on that break.
- **The implemented activation-time reading (B) is not supported.**
- Per D18-4, whether the deciding moment is the **structure break** or the **actual fill** matters when they differ:
  - **A on STRUCTURE (break time)** can be evaluated causally in the engine.
  - **C (true fill)** is `EXECUTION_DEPENDENT` and would be deferred to Phase 14A.
  - Either way, the engine must retain the causal inputs: Q30 open, running against-trade excursion, :15 candle close direction.
- **Hard veto vs quality downgrade: ambiguous.** It is not decided by which examples pass.

**Owner decisions required:**
- (i) A-on-structure-break vs C-at-true-fill (`EXECUTION_DEPENDENT`);
- (ii) hard veto vs recorded downgrade.
