# D8 Evidence Review: What Starts the Hourly Extension?

**Doc:** CBR-EVD-D8 · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D26 §6 · **Status:** FOR OWNER DECISION
PC2 is unchanged and stays frozen. Nothing here is implemented; no parameter was selected; no profitability was used.

**Method.** Search of the hourly, 15min, phase1 and phase2 transcripts, slide OCR and the evidence register for the
anchor of the hourly overextension. Every transcript quote below was verified mechanically against the JSON transcript
with the `tests/test_evidence.py` normalizer (**29/29 quotes verified across the Phase 13R package, 0 failures**,
cited timestamps within 10 s). Engine effects are diagnostics on stored STRUCTURE bars, evaluated at Tom's stated times
as an evaluation point, never as a selector. No outcomes, no P&L.

**Evidence levels.** L1 = course lesson (defines). **L2** = the three long recordings (D4): can clarify, never define.

---

## 1. What PC2 does today

`M1H-OE-01` (duration ≥ 20 min) and `M1H-OE-02` (no ≥ 50% pullback) are both measured from **the hour open**
(`ablations.oe_origin = HOUR_OPEN`, D8 baseline; `LAST_RESET` is the pre-registered alternative). One switch moves both
measurements together. The pullback test compares each bar's adverse excursion with the *running* extension since the
hour open, once that extension exceeds an activation floor of `0.5 × ATR(1m,14)` (OQ-08, ASSUMPTION).

## 2. Evidence

### 2.1 Anchored at the hour open (interpretation A)

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| E1H-003 (slide) | L1 | master slide, e.g. V1H-defining_a_good_extension · 00:00:00 (OCR) | "2 Wait for an hour candle open to overextend into high or low low of the range" | the step order is: hour opens → it overextends |
| E1H-018 | L1 | V1H-defining_a_good_extension · 00:01:19 | "We want it to overextend for around 20 minutes without much of a pullback at all" | duration and pullback in one sentence, on the hour candle |
| E1H-018 | L1 | V1H-defining_a_good_extension · 00:01:26 | "i just want to immediately push in one direction so i'll define a pullback is that you correct 50%" | "immediately" = from the open |
| NEW | L1 | V1H-trade_example_1 · 00:09:41 (CX-TE1-1) | "hourly candle behavior over extension 20 to 30 minutes we've had an hourly candle immediately push bearish for 20 to 30 minutes" | Tom narrates his own example from the open |
| NEW | L1 | V1H-live_trade_1_gold_win · 00:00:09 (CX-LT1-1) | "We've had the hourly candle open, immediately push bearish into the low" | same |

### 2.2 Anchored at the start of the push, wherever it begins (interpretations B and C)

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| **NEW** | **L1** | V1H-candle_behavior_extension · 00:10:42 | "If the alley candle opens and kind of goes sideways for a bit and then pushes, you might have it set up around 37 to 52 minutes into the hour, the reversal setup" | **the push may start after the open**, and the whole setup shifts later with it |
| NEW | L1 | V1H-defining_a_good_extension · 00:02:12 | "it's around 20 to 30 minutes of price action extending in one direction without a pullback" | the object measured is "price action extending in one direction", not "time since the open" |
| NEW | L1 | V1H-defining_a_good_extension · 00:05:16 | "you over extend push bearish in one example but it's pretty low volume and you're on average correcting 50% of the previous move" | "**on average** correcting 50% of the previous move" reads as repeated corrections of each leg, not one test against the move since the open |
| NEW | L1 | V1H-defining_a_good_extension · 00:07:12 | "You can still look for the setup around 30 minutes in and towards 50% of its previous move" | the setup is timed off the push, not the open |
| NEW | **L2** | V1H-mastering_entry_timing… · 01:14:35 | "If the extension starts later into the hour, the setup, ideally you want to enter then as well" | explicit: the extension can start later |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:40:17 | "the open of the hour into around 13 minutes into the hour there's a delay so you have a 13 minute delay if you were to take a trade 22 minutes in it would only be like a seven minute extension" | duration is counted **from the start of the push**, and the delay is subtracted |
| LR-41 | **L2** | V1H-mastering_entry_timing… · 01:15:58 | "big pull backs kind of reset the move as well" | a large pullback resets the count |
| NEW | **L2** | V1H-mastering_market_structure… · 01:07:10 | "you can do the the second push you just still want the prerequisites um i would still just wait for i mean 20 minutes of extension" | a second push qualifies on its own, with the same 20 minutes |

### 2.3 Against a free-floating anchor

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| NEW | L1 | V1H-defining_a_good_extension · 00:05:03 | "where the alley counter opens and you go sideways for 30 minutes that's telling you that there isn't a trade" | a long sideways start **disqualifies** the hour; the push can't start arbitrarily late |
| NEW | L1 | V1H-defining_a_good_extension · 00:02:21 | "it's just around like 40 to 50 percent of that of that candle pushing in one direction" | the push must occupy 40-50% of the candle, which bounds how late it may start |

## 3. Candidate interpretations

| Id | Interpretation | Machine definition | Supporting | Contradicting |
|---|---|---|---|---|
| **A** | **Hour open** (PC2 today) | duration and pullback measured from `H.open` | §2.1 (master slide, E1H-018, both example narrations) | §2.2; fails all three examples in the run |
| **B** | **Last reset** (D8 alternative) | a ≥ 50% pullback restarts both measurements at its extreme | LR-41, 01:07:10, §2.2 generally | no L1 statement defines a reset rule; recovers 2 of 3 examples but breaks CX-LT1-1's duration (§4) |
| **C** | **Final directional push** | measurements start at the most adverse point before the extension extreme | 01:14:35, 00:40:17 ("13 minute delay"), 00:10:42 | not stated as a rule in L1; would make duration ≈ time from the swing low/high to the extreme |
| **D** | **Proportion of the candle** | no anchor: the push must occupy ≥ 40-50% of the hour in one direction, ending at the extreme | 00:02:21, 00:02:12 | never stated as the *measurement* rule; a restatement of "20-30 minutes" |
| **E** | **Split anchors** (new) | duration from the hour open (A); the pullback test applied to the current leg (B/C) | §2.1 for duration + §2.2's "on average correcting 50% of the previous move" for the pullback | no single passage states the split; it is a reading that reconciles both sets |

**PC2's D8 switch cannot express E**: `oe_origin` moves duration and pullback together.

## 4. Effect on every course example (diagnostic, at Tom's stated entry time)

STRUCTURE bars, engine primitives, `oe_min_minutes = 20`:

| Example | Anchor A (hour open) | Anchor B (last reset) | Final-push start (C) |
|---|---|---|---|
| CX-LT1-1 (Tom 01:39:15) | duration 38 min, **no-pullback FALSE**, extreme 4332.95 @01:38 | origin 01:23, duration **15 min → fails the 20-minute rule**, no-pullback TRUE | most adverse point 01:01 → 37 min to the extreme |
| CX-TE1-1 (Tom 04:38) | duration 37 min, **no-pullback FALSE**, extreme 4102.88 @04:37 | origin 04:11, duration 26 min, no-pullback TRUE → **both rules pass** | 04:00 → 37 min |
| CX-LT3-2 (Tom 01:40) | duration 37 min, **no-pullback FALSE**, extreme 4053.43 @01:37 | origin 01:09, duration 28 min, no-pullback TRUE → **both rules pass** | 01:02 → 35 min |

Under A the extension direction, extreme and extreme time match Tom on all three; only the pullback test fails.
Under B, CX-LT1-1 passes the pullback test but fails the duration rule. **Neither A nor B reproduces all three.**

### 4.1 Why the pullback test fails under A

The retraces that fail `M1H-OE-02` happen in the **first minutes of the hour**, when the running extension is still
tiny and the activation floor (`0.5 × ATR(1m)` ≈ $1.05-2.01 on these days) is already exceeded:

| Example | First failing retrace | Running extension at that moment | Full extension by Tom's entry |
|---|---|---|---|
| CX-LT1-1 | 01:01, retrace $6.05 = 248% | $2.45 | $35.77 |
| CX-TE1-1 | 04:05, retrace $3.05 = 50% | $6.05 | $19.56 |
| CX-LT3-2 | 01:01, retrace $4.01 = 94% | $4.27 | $33.00 |

CX-LT1-1 and CX-LT3-2 fail on **early-hour noise**, ten to forty minutes before the move Tom is describing, and the
failure then persists for the rest of the hour (the candidate lifecycle cancels every later candidate with
`OE_PULLBACK`). CX-TE1-1's single failing retrace is a genuine 50.0% retrace of a $6 leg.

This is a second, independent question from the anchor: **what minimum extension size is worth testing for a pullback**
(`oe.activation_atr`, OQ-08, ASSUMPTION). No value is proposed here.

## 5. Findings

1. L1 supports both the hour open (as the step order and the usual case) and the start of the push (when the hour
   opens sideways). They are not in conflict in Tom's telling: he expects the push to start at the open, and says what
   to do when it doesn't.
2. **No L1 passage defines a reset rule.** `LAST_RESET` rests on L2 ("big pull backs kind of reset the move") and on
   the delay discussion. Approving B on this evidence would make an L2 phrase canonical.
3. The strongest L1 statement against PC2's current behaviour is 00:10:42: a sideways start **delays** the setup rather
   than voiding the hour, which is exactly what PC2 does not allow.
4. The observed failures are driven more by the **activation floor** than by the anchor: two of three examples fail on
   retraces of $2-4 moves in the first minutes of the hour.
5. Interpretation **E** (duration from the open, pullback on the current leg) is the only reading consistent with both
   Tom's narration of his own examples ("opened and immediately pushed", 38 and 37 minutes) and his pullback language
   ("on average correcting 50% of the previous move"). It is a reading, not a quotation.

## 6. Recommendation to the owner

**Do not approve `LAST_RESET` as the baseline on this evidence.** It matches two examples and breaks the third, and its
only direct support is L2.

The evidence-led questions to rule on are, in order:
1. **Activation floor** (OQ-08): should a $2 excursion count as an extension whose 50% retrace disqualifies the hour?
   This is an ASSUMPTION with a declared research range and no course number.
2. **Pullback reference** (new): "the previous move" = the move since the hour open, or the current leg?
3. **Anchor for duration** (D8/OQ-22): the hour open, with the delay case of 00:10:42 handled explicitly.

Each is a separate spec decision; only after they are settled does the D8 switch have a defined meaning. Proposed
classifications are in `docs/strategy/pc3-proposed-change-set.md`.
