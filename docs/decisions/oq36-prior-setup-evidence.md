# OQ-36 Evidence Resolution Package: "Prior Working Setup" / "Played Out"

**Doc:** CBR-EVD-036 · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D17-3, D18-6 · **Status:** FOR OWNER DECISION
COND-03 (CBR15) and M1H-COND-04 (CBR1H) are **unchanged** until the owner rules.

**Method.** Two passes:
1. Search of all 15min, hourly, phase1 and phase2 transcripts, slide OCR, frames and existing evidence records.
2. Mechanical verification: every transcript quote below matched the JSON transcript with the `tests/test_evidence.py` normalizer (**24/24 verified, timestamps within 60 s**). Slide text was checked against `research/slides/*.jsonl` OCR.

No P&L, no signal counts.

**Evidence levels.** L1 = course lesson. **L2** = the three long recordings, per D4:
- `V1H-mastering_entry_timing_and_market_structure_for_trading_success`
- `V1H-mastering_market_structure_and_timing_in_trading`
- `V1H-in_depth_backtesting_strategies_for_trading_success`

L2 can clarify, never define.

---

## 1. Tom's language

- **Phrases that never occur** in any course transcript: "working setup", "active setup", "resolved", "setups in the last hour", "prior setup".
- **Phrases used:**
  - "clean (15-min) CBRs", "clean setups";
  - "previous (cbr) setup(s)", "previous 15 minute cbrs / previous hourly cbrs";
  - "set up (and played out)", "play out nicely";
  - "CBRs roll in gangs / packs".
- **"Played out"** appears once on a slide (E15-049) and once in speech (E15-007).

## 2. Evidence

| Id | Level | Source (video · time) | Verbatim | Model | Informs |
|---|---|---|---|---|---|
| E15-049 (slide) | L1 | V15-defining_ltf_range · 00:07:52 (frame 00-10-52) | "Look back 1.5 to 2 hours and count how many clean 15-min CBRs set up and played out." / "3+ clean setups in that window: good condition." / "Zero setups in the last hour: bad condition. Sit out." | CBR15 | the only written "played out"; it sits on the 1.5-2 h **count**; the hard last-hour clause says "Zero **setups**" |
| slide (OCR) | L1 | V15-overview_methodology · 00:00:02 | "1.5 to 2 hours and count how many clean 15-minute CBRs set up" / "3* setups in that window, condition is good - CBRs roll in gangs" / "If you have seen zero setups in t[he past hour]…" | CBR15 | same rule **without** "played out" |
| slide (OCR) | L1 | V15-hourly_cb_structure · 00:09:02 | "If you see 3+ setups in that window, condition is good - CBRs roll in gangs" / "…zero setups in the past hour…" | CBR15 | third version, no "played out" |
| E15-007 | L1 | V15-overview_methodology · 00:05:20 / 00:05:26 | "it's just to look back and see have you had the setup that you look for" … "set up and play out nicely in the previous couple of hours" | both | only spoken "play out"; ending event undefined |
| NEW | L1 | V15-overview_methodology · 00:04:20 | "if it's you know low time frame it's again that 90 minutes ... five ten plus hours and see it have i had a previous setup a previous cbr setup" | both | lookbacks ≈ 90 min (15m) / 5-10+ h (hourly) |
| NEW | L1 | V15-overview_methodology · 00:05:09 | "just look at the prior candles and seeing you know have we had some cbrs and how frequently" | both | judged from prior **candles** and frequency |
| NEW | L1 | V15-overview_methodology · 00:05:45 | "not trying to guess for CBR to happen. You just want to see that it is happening and then take" | both | framed as "is it happening" |
| E15-008 | L1 | V15-defining_ltf_range · 00:06:48 / 00:07:00 / 00:07:09 | "past you know 1.5 to 2 plus hours of price action and see if there's been previous 15 minute cbrs" … "past five ten plus hours you know is there enough frequency that there's been previous hourly cbrs" … "looking to take a cbr and there's been no cbrs prior to that you're probably trading in the" | both | existence and frequency; evaluated when "looking to take" a CBR |
| NEW | L1 | V15-defining_ltf_range · 00:07:19 | "cbr probably not trading in the right condition and vice versa ... but you just want to see the type of cbr that you're going for happen previously" | both | **same model size** required |
| E15-009 | L1 | V15-defining_ltf_range · 00:11:05 | "want you know two one two three clean setups prior if there's no setups is probably a bad condition" | both | 2-3 clean prior; none = bad ("probably") |
| NEW | L1 | V15-defining_ltf_range · 00:05:36 | "uh cbr setups on the alley and then we can look for you know the the third or the fourth alley cbr ... i'm going to look for some alley cbrs for the next two three hours" | CBR1H | a regime judgement that carries forward |
| NEW (visual) | L1 | V15-defining_ltf_range · 00:11:46 / 00:12:13 (frames 00-11-44, 00-12-36, 00-12-46) | "this is just you know for an hourly cbr example but you can apply it exactly the same ... no no no this is pretty like more of a fake out uh pretty low volume not that nice pretty little" … "If you just go back a little bit further, say, okay, we have a really nice CBR here, ... nice CBR, nice CBR, you know, good extensions, good sort of range. ... previous setups happen more frequently as well" | both | he points at **hourly candles** with extensions and reversal wicks; no target or stop is marked; a "fake out"/"low volume" one is rejected |
| NEW | L1 | V15-overview_methodology · 00:06:41 | "a 50 minute cbr will set up the same way that an hourly cbr sets up" | both | same logic scaled (×4 on slides) |
| NEW | L1 | V15-overview_methodology · 00:07:22 | "extends uh for the first half around the second half you have that shift ... can do target back in towards 50% of this extension here." | both | background: a CBR's target is 50%; not tied to "played out" |
| LR-48 | **L2** | V1H-mastering_entry_timing… · 00:28:12 / 00:33:42 | "you know four to five hours ... did you have a previous CBR? ... That was clean. ... in the previous couple of hours?" … "so if i didn't have a cpr in previous 45 hours you would sit out completely as the condition ... kind of a new sort of mindset I guess like so I don't have data to back it up" | CBR1H | hourly lookback ≈ 4-5 h; called new and untested |
| LR-73 | **L2** | V1H-mastering_market_structure… · 00:59:27 / 00:59:58 | "is it hitting the right thing at the right time? ... do we have past clean CBRs ... five hours and count them." … "They roll in gangs. ... So when you see one, you're more likely to see a couple more. ... i think of it as like boosting the the current cbr ... You're trying to catch the third or the second, third, fourth CBR." | CBR1H | count clean CBRs in 5 h; a quality "boost" |
| LR-28 | **L2** | V1H-in_depth_backtesting… · 01:17:56 | "to be followed by another trade or trade after that within a couple of hours does that make sense ... like if there's a prior cbr and i'll just take a cbr like that's high quality ... so one cbr goes into another so even this is like kind of low quality of a an entry ... since you have a a previous cbr i probably still" | CBR1H | a prior CBR makes a weaker entry acceptable (quality, not gate) |
| NEW | **L2** | V1H-in_depth_backtesting… · 01:00:18 | "high into taking out this low and to pull back into 50 that would be a nice setup ... So you had two nice CBRs here." | CBR1H | closest support that "nice setup" includes the 50% pullback |

### Contradicting / ambiguous

| Id | Level | Source | Verbatim | Issue |
|---|---|---|---|---|
| slides | L1 | V15-overview_methodology 00:00:02 vs V15-defining_ltf_range 00:07:52 | "set up" vs "set up and played out" | the slides disagree on whether "played out" is required |
| E15-049 | L1 | as above | "Zero setups in the last hour: bad condition. Sit out." | the only hard clause counts *setups*, not played-out setups |
| NEW | **L2** | V1H-mastering_market_structure… · 01:13:48 | "this is such a nice cbr nice extension like this would be a good loss" | a losing setup is still "nice": "clean/nice" reads as candle shape, not outcome |
| NEW | **L2** | V1H-mastering_market_structure… · 01:00:31 | "How many in the previous hour?" | possibly a chat question read aloud; doesn't set an hourly 1 h window |
| NEW | L1 | V15-defining_ltf_range · 00:11:46 | "…more of a fake out uh pretty low volume not that nice…" | could mean the reversal failed, or poor volume/extension |

## 3. Answers to the owner's questions

| # | Question | Finding | Strength |
|---|---|---|---|
| 1 | Language | See §1 | moderate |
| 2 | What a "working setup in the previous hour" means | Mostly **existence of a clean same-size CBR** ("has there been", "have we had", "zero setups"). "Played out" is written once, undefined | weak |
| 3 | What ends / plays out a setup | **Not stated.** Indirect hints point to the 50% pullback (L2 01:00:18; target definition); an L2 "nice cbr … good loss" cuts against it. "Target *before stop*" has no source | **insufficient** |
| 4 | When it's evaluated | Before taking a CBR ("looking to take a cbr", "do not expect one now"); regime judgement carried forward ("next two three hours") | weak |
| 5 | Which timeframe / concept | **Same model size** (strong: 00:07:19). Walkthroughs show candle-level extension + reversal behaviour; no link to a 5s type 3 or 1m structure | moderate (size) / weak (tier) |
| 6 | Visual examples | Two walkthroughs (L1 V15-defining_ltf_range 00:11:44-00:12:46; L2 mastering 01:02-01:13): hourly candles with reversal wicks, no targets or stops marked | weak |
| 7 | CBR15 vs CBR1H | Same logic, different windows: CBR15 1.5-2 h count with a 60-min zero clause; CBR1H 5-10+ h (L1), 4-5 h (L2). No hourly "zero in the last N hours" clause and no hourly "good" count in L1 | moderate |

## 4. Candidate interpretations

| Id | Interpretation | Supporting | Contradicting | Exact machine rule | CANON effect |
|---|---|---|---|---|---|
| **A** | A prior clean **same-size CBR formed** (extension then reversal on that candle) | E15-008, E15-009, slides 00:00:02 / 00:09:02, 00:05:09, 00:05:45, 00:07:19, L1 walkthrough | E15-049 "played out" | **CBR15:** ≥ 1 closed 15m candle in [Q.t0 − 60 min, Q.t0) meeting the CBR15 candle-behaviour geometry (OE rules M15-OE-01…03 on that candle and a reversal close back toward its open by ≥ 50% of its extension, `ASSUMPTION` on the reversal size); 3+ in 1.5-2 h recorded as "good". **CBR1H:** ≥ 1 closed hourly candle meeting CBR1H OE geometry + reversal in [H.t0 − 5-10 h, H.t0) (window `ASSUMPTION`). Evaluated at the candidate candle's open. No entry trigger, no outcome | redefines the rule's object from "raw setups" to candle behaviour; CANON wording supported, geometry thresholds ASSUMPTION |
| **B** | A prior setup **triggered** (entry shift fired) | none | all examples point at candle behaviour | A + the model's entry trigger fired inside its window | not supported |
| **C** | A prior setup **played out = reached its 50% target** (current implementation also requires target before stop) | E15-049, E15-007 ("play out nicely"), L2 01:00:18, target definition | slides without "played out"; last-hour clause "setups"; L2 "good loss" | current rule: raw setup with TARGET touched before STOP, resolved before Q.t0 (CBR15 60 min; CBR1H lookback) | "before stop" has **no source** (ASSUMPTION); otherwise CANON-ambiguous |
| **C′** | **Split reading of E15-049:** hard gate = A ("zero setups in the last hour"); "good" count = C over 1.5-2 h (recorded, not blocking) | E15-049 text structure, both slide versions | L2 sources treat it as quality, not gate | CBR15: gate `≥ 1 A-type setup in 60 min`; diagnostic `count of C-type in 1.5-2 h` (3+ = good). CBR1H: gate `≥ 1 A-type in lookback`; no hourly "good" count (not in L1) | closest to the literal slide; thresholds for "clean" ASSUMPTION |
| **D** | **Market respecting CBR behaviour** (frequency / metronome) | E15-048 slide, 00:07:00 "enough frequency", L2 00:59:27 | none direct | count of A-type candles in the window as a frequency measure | equivalent to A with counts |
| **E** | **Quality-graded formed setup ("clean")** | 00:11:46-00:12:30, L2 00:28:32 | "clean" never defined | A + prior candle passes the model's extension-size / two-sided / volume rules | A with extra ASSUMPTION thresholds |

**CBR15 vs CBR1H.** Under every reading, the rule should be represented **separately** per model:
- **CBR15:** 60-min zero clause; 1.5-2 h count.
- **CBR1H:** 5-10+ h lookback (L1); no L1 hard count window.
- The hourly "gate" rests mainly on L2 sources, where Tom says he has no data and might treat it as confluence.

## 5. Consequence for the existing examples (engine diagnostics only)

On the three course-example windows, the current reading (C, with "target before stop") failed `M15-COND-03` for **every** CBR15 candidate and `M1H-COND-04` for **every** CBR1H candidate. Four CX-TE1-1 CBR15 candidates failed only COND-03. Interpretations A, C′ and E aren't implemented; their effect needs an owner-approved reading first (an engine change), so no counts are produced here.

## 6. Recommendation

The evidence is **insufficient to define "played out"** (question 3) and doesn't support the ending event now implemented.

It does support three things:
- **(i) same-model-size prior CBRs**, represented separately per model;
- **(ii) existence / "clean" formation** as the core concept;
- **(iii)** the only hard clause, which is literally about *setups* in the last hour.

**OQ-36 stays unresolved on evidence.** If an owner assumption is needed for baseline eligibility, the reading closest to the Level 1 text is **C′**:
- the hard gate is A (a clean same-size CBR formed);
- the "played out" count is recorded as a non-blocking quality diagnostic;
- the candle-behaviour geometry thresholds are ASSUMPTION, with research ranges declared before use;
- CBR1H gets its own lookback (5-10 h ASSUMPTION) and no hourly hard count beyond ≥ 1.

**Owner decision required.**
