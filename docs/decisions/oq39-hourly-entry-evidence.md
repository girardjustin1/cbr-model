# OQ-39 / OQ-43 Evidence Resolution Package: CBR1H Entry Trigger and HVCS End Bar

**Doc:** CBR-EVD-039 · **Version:** v1.0 · **Date:** 2026-09-15 · **Rulings:** D18-1, D18-5 · **Status:** FOR OWNER DECISION
The canonical CBR1H entry rule is **unchanged** until the owner approves a change.

**Method.** Search of hourly, 15min, phase1 and phase2 transcripts, slide OCR, frames and existing evidence. Every
transcript quote below was verified mechanically against the JSON transcript with the `tests/test_evidence.py` normalizer
(**all transcript quotes in this file verified, 0 failures, 0 timestamp mismatches**; slide quotes checked against OCR and `research/evidence/strategy_evidence.jsonl`); slide text checked against OCR (`research/slides/*.jsonl`).

**Evidence levels.** L1 = course lesson. **L2** = the three long recordings (D4: `V1H-mastering_entry_timing_…`,
`V1H-mastering_market_structure_…`, `V1H-in_depth_backtesting_…`), which can clarify, never define.

Effects on the examples come from `reports/phase13-readiness-diagnostics.md`: STRUCTURE facts only, with Tom's entry used
as the evaluation point, never as a selector. No P&L.

---

# OQ-39: what is the CBR1H entry trigger?

## 1. Supporting evidence (Level 1 first)

| Id | Level | Video · time | Verbatim | Describes | Applies | Reading |
|---|---|---|---|---|---|---|
| E1H-004 | L1 | V1H-overview_methodology · 00:05:47 | "two sub-edge models a high volume counter sequence into a high low technically that's a second shift in market structure or a one minute type three kind of like a fractal shift" | trigger | CBR1H | the HVCS→HILO model's HILO **is** a seconds shift |
| E1H-003 (slide) | L1 | V1H-defining_a_good_extension · 00:00:38-00:00:44 (OCR) | "1m T3, 50% pullback, 5s T3 Fr[actal Shift]" · "- HVCS-> HILO → 15m CB" · "- 1m T3 - > HILO @ 50%" | setup + trigger | CBR1H | master slide: the fractal model's trigger is written as a **5s T3** |
| NEW | L1 | V1H-1m_fractal_shift · 00:00:00 | "Okay, so now we're going to go over the two types of shifts that we can be taking. First, we'll go over one minute fractal shifts here, ... And then we'll also go over some second shifts" | taxonomy | CBR1H | two hourly shift types |
| E1H-032 | L1 | V1H-1m_fractal_shift · 00:00:25 | "it's if it's a higher volume condition you're more likely to go for a second shift" | model choice | CBR1H | volume decides |
| NEW | L1 | V1H-1m_fractal_shift · 00:01:23 | "i look for it as a fractal shift so i trade second shifts differently from one minute shifts" | trigger | CBR1H | distinct execution types |
| E1H-031 | L1 | V1H-1m_fractal_shift · 00:01:50 | "i want maybe second shift to take out a high into taking a low or i want a one minute high low" | trigger in pullback | CBR1H | fractal reaction = 5s shift **or** 1m HILO |
| NEW | L1 | V1H-1m_fractal_shift · 00:02:16 | "most time on a second shift i'll just take the entry on the break of the low if we've come into 50% of the previous move" | order placement | CBR1H | stop entry on the 5s break inside the 50% zone |
| NEW | L1 | V1H-1m_fractal_shift · 00:04:00 | "If you have TradingView Premium or the Pro version, you can drop down onto the five seconds chart. I'm going to use the five seconds chart and look for a reaction within this 50% area on the pullback." | trigger | CBR1H | fractal walkthrough on the 5s chart |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:00:37 | "around the halfway point of this 15 minute candle you want that seconds to shift bullish it could be a high low entry" | trigger | CBR1H | seconds shift = trigger; HILO equivalent |
| E1H-035 | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:03:02 | "you have a high low or a second shift and for second shifts i'm just taking the entry on the break of the of the low" | order placement | CBR1H | stop at the 5s break |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:03:39 | "So that's kind of the second shift. It's a bit more aggressive of an entry." | trigger | CBR1H | named entry type |
| E1H-029 | L1 | V1H-when_candle_behavior_timing · 00:06:42 | "If the shift happens over a couple minutes, like five minutes, I'll just say it's like a second shift because on the second time frame," | trigger | CBR1H | a short shift is read on seconds |
| NEW | L1 | V1H-when_candle_behavior_timing · 00:08:44 | "but if you get on two seconds on a one minute shift pretty much always like you'll have a second shift within that one minute shift" | nesting | CBR1H | a 5s shift sits inside a 1m shift |
| NEW | L1 | V1H-stop_losses · 00:00:08 | "You're either going to be entering off a second shift or like a normal one minute shift." | trigger | CBR1H | the two entry types |
| NEW | L1 | V1H-trade_management · 00:00:43 | "and scale for example uh in this so i entered on the second shift here and on the second shift here" | actual fill | CBR1H | first entry on the seconds shift |
| EP2-001 | L1 | VP2-1m_hilo_entries · 00:00:17 | "A one minute HILO entry is simply a even lower time frame shift." | definition | both | HILO = proxy for a lower-TF shift |
| NEW | L1 | VP2-1m_hilo_entries · 00:00:43 | "So this could be the seconds timeframe or the tick chart." | definition | both | as above |
| NEW | L1 | V1H-trade_example_1 · 00:11:58 | "entry models will always be a shift. It could be of the seconds timeframe or one minute structure here." | trigger | CBR1H | rule statement inside an example |
| NEW | L1 | V1H-trade_example_1 · 00:12:17 | "so i just entered off the break of that high because it's a second shift um it's a bit of a high low entry as well but yeah more of a second shift" | actual fill (CX-TE1-1) | CBR1H | fill called both |
| NEW | L1 | V1H-live_trade_1_gold_win · 00:02:47 | "Had a shift of market structure on the 5 second to get the low to take out a high." | actual fill (CX-LT1-1) | CBR1H | example |
| NEW | L1 | V1H-live_trade_3_gold_win · 00:07:47 | "and then potentially look for a setup to, like a shift, on the seconds time frame." | trigger plan (CX-LT3-2) | CBR1H | example |
| NEW | **L2** | V1H-mastering_market_structure… · 00:46:52 | "Every one minute high low is a second's market structure shift." | trigger | both | equivalence |
| NEW | **L2** | V1H-mastering_market_structure… · 00:54:00 | "a one minute high volume counter sequence into a high low is a seconds over extension into a seconds shift" | formation + trigger | both | equivalence |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:01:25 / 00:02:29 / 00:03:16 / 01:13:34 | "So first off, you have the one minute high volume candle sequence into a one minute high low slash five seconds shift." … "The first entry model is just a second shift. And you're trying to validate that through some other things, through the volume in the prior candles to that and 15 minute candle behavior." … "you want to pull back to 50% and then maybe have you look for you know five seconds shift as well" … "One minute high volume counter sequence into a five second shift with 15 minute counter behavior." | both models | CBR1H | recap board (OCR 00:05:02): "1m HVCS→1 Hilo/5s shift w. 15m CB" / "1m T3 Shift, Pullback 50% → 5s shift" |
| NEW | **L2** | V1H-mastering_market_structure… · 00:48:09 | "for a one hour CB like around 20 minutes OE you can have both a 1M fractal shift or a high or low slash seconds shift so it's a bit of both" | trigger choice | CBR1H | either model |

## 2. Contradicting / ambiguous evidence

| Id | Level | Video · time | Verbatim | Issue |
|---|---|---|---|---|
| E15-037 | L1 | V15-seconds_entry_model · 00:00:08 | "But instead of looking for a one minute type three shift, we are looking for a five second or 15 second type three shift." | the only direct statement that hourly = 1m T3 and 15m = 5s; probably refers to the fractal model's 1m setup |
| NEW | L1 | V1H-1m_fractal_shift · 00:04:25 | "you don't have to use the second start you can look for a one minute high low entry" | in the fractal model the 5s chart is optional |
| NEW | L1 | V1H-1m_fractal_shift · 00:10:16 | "so i'll mainly use second shifts when it's higher volume one minute shifts when it's lower volume it's been pretty high volume recently so i haven't been using one minute shifts as much" | regime explains why all examples are seconds shifts |
| NEW | L1 | VP2-1m_hilo_entries · 00:04:49 | "um if it's low volume you know you can wait um for it doesn't have to be one or two candles it can be multiple candles" | a HILO and a 5s shift aren't mechanically identical |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:03:27 | "you're kind of expecting this to create a bigger type 3 shift as well. So you're trying to like catch the smaller shift," | the 5s shift is an early entry on a forming 1m T3 |
| NEW | **L2** | V1H-mastering_market_structure… · 00:48:42 | "for 15 minute CB you're always going to want a high low into seconds or like slash seconds shift" | seconds shifts belong naturally to 15m candle behaviour |
| NEW | **L2** | V1H-mastering_market_structure… · 00:54:15 | "A 1 minute extension into 1 minute shift is a 5 minute high volume candle sequence into a 5 minute high low with hourly candle behavior." | pure hourly scale pairs 1m shift / 5m HILO |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:14:04 / 00:41:40 | "…you should really only be taking like um like a one minute type three shift that late" … "it depends on volume again because the higher the volume the more likely you're going to be looking for a high low sort of entry a second shift" | time-limited / volume-dependent |

## 3. Candidate interpretations

| Id | Interpretation | Supporting | Contradicting | Exact machine rule | Effect on the 3 examples (diagnostics) | CANON or implementation |
|---|---|---|---|---|---|---|
| **A** | 5s shift **is** the CBR1H trigger, in two distinct variants: **A-HVCS** (HVCS extension into a 5s type 3; 1m HILO an accepted coarse equivalent) and **A-FRACTAL** (1m type 3 → ≥ 50% pullback → 5s type 3; 1m HILO accepted equivalent) | E1H-004, E1H-003 slide, E1H-031, E1H-035, NEW 00:00:37, 00:01:23, 00:02:16, 00:04:00, 00:03:39, E1H-029, 00:08:44, stop_losses 00:00:08, trade_management 00:00:43, EP2-001; L2 recaps | E15-037; 00:04:25 (5s optional in fractal); 00:04:49 | A-HVCS: after a valid HVCS in direction `oe_dir`, inside the current 15m candle, a **type 3 in direction d on S5** (primitives §4.1, S5 tier) completes; ORDER stop at `t3.trigger_price`. Declared trigger-resolution variant `{S5_T3, M1_HILO}`, each scored separately, never merged. A-FRACTAL: M1 type 3 break → pullback ≥ 50% of impulse, not beyond the sweep extreme → **S5 type 3 in direction d inside the pullback** (variant `{S5_T3, M1_HILO}`) | S5 type 3 breaks near Tom's entry: **CX-LT1-1** 01:39:35, trigger 4340.185 (same level as the 1m HILO); **CX-TE1-1** 04:38:55, trigger 4105.565; Both breaks print **after** Tom's recorded entry times (LT1-1 +20 s vs 01:39:15; TE1-1 +85 s vs 04:37:30) on Dukascopy STRUCTURE; whether this is feed/time-reference difference or a different 5s structure is a V-1 question, not evidence for or against A. **CX-LT3-2** none found with the frozen S5 swing k; HILO touches in that hour are 1m at 01:37:45 (4051.38) and 5m at 01:40:15 (4050.218). M1 type 3 (fractal setup): none in any of the three hours | **CANON change**: the spec's trigger is 1m HILO only; Level 1 names the seconds shift as the trigger with HILO as equivalent |
| **B** | 5s shift = refinement after a 1m setup (fractal model only) | E1H-031, 00:02:16, 00:04:00, 00:08:44 | 00:04:25 | as A-FRACTAL | as above (no 1m type 3 in the three hours) | CANON change for the fractal model |
| **C** | Optional execution refinement of a 1m HILO | 00:04:25 (fractal only), 00:04:00 (premium-chart caveat) | E1H-004, E1H-035, stop_losses, E1H-029 | trigger = 1m HILO; the 5s shift may only improve the fill | current engine (1m/5m HILO arms, as in the Phase 12 diagnostics) | implementation only; **weak** as the primary reading |
| **D** | Example-specific | 00:10:16 (regime explanation) | every teaching source | — | — | rejected |
| **E** | Only relevant to CBR15 | E15-037; L2 00:48:42, 00:54:15 | E1H-004, E1H-003 slide, E1H-035, stop_losses, trade_management | — | — | rejected as a whole; keep the nuance that CBR1H Variant A is timed on nested 15m candle behaviour |
| **F** | Unresolved | — | — | applies only to 5s detection details (S5 swing definition OQ-01, "decisive" shift, 5s data availability OQ-10) | — | not a trigger-identity question |

## 4. Assessment

**A: strong on Level 1 alone.**
- The overview (E1H-004) and the master slide (E1H-003) define both hourly models with a seconds shift.
- The dedicated lessons ("1m Fractal Shift", "Seconds Shift (1m HILO HVCS)") and the stop-loss lesson describe entering on a second shift, with a 1m HILO as the equivalent.
- The L2 recordings agree but aren't needed.

**Keep the two setups as distinct variants, and the trigger resolution (S5 type 3 vs 1m HILO) as a declared, separately scored variant.**
- The one Level 1 contradiction (E15-037) is a comparison line in the 15-minute course.
- It plausibly refers to the fractal model's 1m type 3 setup.

**The course examples don't decide this.** CX-LT3-2 has no S5 type 3 at the frozen swing threshold, so adopting A would not by itself reproduce every example.

**Owner decision required before any canonical change.**

---

# OQ-43: where does the HVCS end?

## 1. Evidence

| Id | Level | Video · time | Verbatim | Reading |
|---|---|---|---|---|
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:02:06 | "i want this sort of high volume uh candle sequence so you see we're respecting all the all the highs we're just you know consistently moving bearish yeah and then Then we have a shift, take out a low into taking out a high." | the HVCS runs straight into the shift |
| E1H-034 | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:01:19 | "You want volume to push immediately for at least four minutes or more," | ≥ 4 min, from "immediately" |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:02:50 | "you have the next 15 minute candle open and you know immediately push bullish and then around the second half of that 15 minute candle you have a high low or a second shift" | 15m open → push → shift in the second half |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:00:25 | "ideally you want like seconds time frame to be making like a very directional move kind of trendy here and then around the halfway point of this 15 minute candle you want that seconds to shift bullish" | trend into the shift |
| NEW | L1 | VP2-1m_hilo_entries · 00:02:48 / 00:03:27 | "the candle prior to the break of structure needs to also break a structure the previous candle higher low" … "where in this candle sequence, we have this big bearish candle break this low. And then the next candle break this high." | the last sequence bar breaks the low; the next bar triggers |
| EP2-005 / NEW | L1 | VP2-1m_hilo_entries · 00:05:13 / 00:07:00 | "So this would be an HVCS, ... We're moving, respecting lows and highs." … "So as we can see here on the one minute candles, we are respecting lows." | membership = respecting the side |
| NEW | L1 | VP2-1m_hilo_entries · 00:03:45 | "For this example here, it's even better if you have a no wick, you open and then immediately push with lots of volume." | push right from the open preferred |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:02:29 | "…through the volume in the prior candles to that and 15 minute candle behavior." | the HVCS is the candles just before the shift |
| NEW | **L2** | V1H-mastering_market_structure… · 00:18:49 / 00:51:52 / 01:05:11 | "you know if you have a high volume candle sequence which is the extension…" … "…you overextend in one direction and the halfway point of the 50 minute candle you shift in your direction" … "…You could have the high-volume counter-sequence, high-low into a shift like that." | HVCS = the extension, "into" the shift |

### Contradicting / ambiguous

| Id | Level | Video · time | Verbatim | Issue |
|---|---|---|---|---|
| NEW | L1 | VP2-1m_hilo_entries · 00:04:49 | "um if it's low volume you know you can wait um for it doesn't have to be one or two candles it can be multiple candles" | indecision bars may sit between the last extension bar and the trigger |
| E1H-003 (slide) | L1 | V1H-defining_a_good_extension · 00:00:38 | "1. HVCS, 4+ mins 2. Goes beyond prev LTF/MTF HIGH 3. After 15m open, PA create wick/pushes a bit more 4. HILO beyond structure" | step order leaves room for the HVCS to finish before the 15m open |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:02:22 | "High volume pushes in that direction, second half of the previous 15-minute candle." | could place the HVCS in the previous 15m candle's second half |
| E1H-047 (slide) | L1 | V1H-where_aoi_er_oe · 00:10:56 | "OE LTF HVCS (10-30m)" | a journal field suggesting an OE-length HVCS |

## 2. Candidates and effects

| Id | End bar | Supporting | Contradicting | Exact rule | Effect at Tom's entry (diagnostics; HVCS minutes / valid / HILO tier) | CANON? |
|---|---|---|---|---|---|---|
| **(a)** | Last completed displacement bar, adjacent to the trigger | 00:02:06, EP2-005, 00:02:48, 00:03:27, L2 "into" wording, 00:04:49 (gap bars) | — | `end_bar` = last B1m bar before the trigger bar that made a new extreme in `oe_dir` while respecting the sequence side; HVCS = longest run ending there, ≥ 4 min; no bar between `end_bar` and the trigger breaks the respected side except the trigger (gap bars allowed up to an ASSUMPTION `max_gap_bars`) | ≈ E2/E3 below | adjacency CANON; gap limit ASSUMPTION |
| (b) | Reversal bar (single-bar HILO) | EP2-002 | EP2-005 (a breaking bar isn't respecting) | `end_bar = trigger_bar − 1` for same-bar HILOs | sub-case of (d) | implementation |
| (c) | HILO bar | none | 00:02:48, EP2-005 | — | — | rejected |
| (d) | Bar immediately before the structure break (`j−1`) | 00:03:27, 00:02:48 | 00:04:49 | `end_bar = trigger_bar − 1` | **CX-LT1-1** 4 min, valid, 1m · **CX-TE1-1** 2 min, invalid · **CX-LT3-2** 0 min, invalid | implementation (= (a) with no gap bars) |
| (e) | HVCS finished before the 15m open, then "pushes a bit more" | E1H-003 step order, 00:02:22, E1H-047 | 00:02:50, L2 01:05:11 | as (a), `end_bar` may precede `Q.open` if a new OE extreme prints after `Q.open` with the respected side unbroken | not computed separately | CANON widening |
| E1 (implemented) | Longest HVCS anywhere in the hour up to the decision | at most E1H-047 | 00:02:06, 00:02:50, 00:00:25, L2 "into" wording | current `end_bar ≤ as_of` | **CX-LT1-1** 6 min, valid, **5m tier (LVCS)** · **CX-TE1-1** 9 min, valid, 1m · **CX-LT3-2** 9 min, valid, 1m | not supported; should be tightened |
| E2 | The OE extreme bar | as (a) | — | `end_bar = oe_extreme bar` | **CX-LT1-1** 4, valid, 1m · **CX-TE1-1** 2, invalid · **CX-LT3-2** 0, invalid | variant of (a) |

## 3. Assessment

**Adjacency: moderate.** The HVCS is the extension the shift reverses and runs "into" the trigger. That supports **(a)**.

**The implemented "anywhere in the hour" reading (E1) is not supported by Level 1.**

**The choice is material.** Under (a)/(d)/E2 the HVCS at Tom's entry is **invalid on CX-TE1-1 and CX-LT3-2**. Under E1 it is valid on all three, but with a 5m tier on CX-LT1-1. So:
- neither reading simply "reproduces the examples";
- the gap-bar limit (no number in the sources) and whether the post-open "pushes a bit more" belongs to the HVCS (e) stay open;
- evidence strength is moderate, and the decision is the owner's.
