# M1H-6A-1 Evidence Review: "HVCS Runs Directly Into the Shift"

**Doc:** CBR-EVD-HVCS · **Version:** v1.0 · **Date:** 2026-09-15 · **Rulings:** D26 §8 (extends OQ-43 / OQ-44, D19-6, D20-4)
**Status:** FOR OWNER DECISION. PC2 unchanged and frozen. Quotes verified mechanically; no outcomes, no P&L; no
indecision-bar count is invented below.

---

## 1. What PC2 requires today

`M1H-6A-1-HVCS-INTO-SHIFT` passes when all of:
1. **End bar** = the closed 1m bar that set the extension extreme, known at the decision instant;
2. `hvcs(direction, end_bar)` is **valid**: the run of 1m candles ending at that bar is ≥ `hvcs.min_minutes` = 4, where a
   conforming candle is (DOWN) `high ≤ previous high` **and** `close < open`, with at most `hvcs.max_violations` = 1
   non-conforming candle inside the run, and the run must **end on a conforming candle**;
3. **Continuity**: no closed bar between the end bar and the decision breaks the respected side.

Failures: 469 of 536 candidates across the three course windows — the second most frequent rule failure.

## 2. Evidence

### 2.1 What an HVCS is

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| E1H-034 (slide) | L1 | V1H-defining_a_good_extension · 00:00:38 (OCR) | "1. HVCS, 4+ mins" | the only number: **4+ minutes** |
| slide | L1 | V1H-defining_a_good_extension · 00:00:52 (OCR) | "OE LTF HVCS (10-30m)" | the *overextension* as an HVCS is **10-30 minutes**; the entry-model HVCS is the 4+ min one |
| **NEW** | **L1** | V1H-seconds_shift_1m_hilo_hvcs · 00:02:06 | "i want this sort of high volume uh candle sequence so you see **we're respecting all the all the highs** we're just you know consistently moving bearish" | the defining property is **respecting the highs** plus consistent direction |
| **NEW** | **L1** | VP2-1m_hilo_entries · 00:05:19 | "We're moving, **respecting lows and highs**. We're kind of trending on low timeframes" | same definition, phase-2 source |
| **NEW** | **L1** | VP2-1m_hilo_entries · 00:04:49 | "it doesn't have to be one or two candles it can be multiple candles so like **this previous candle didn't do anything but it's more of an indecision candle**" | **indecision candles are explicitly inside** a valid sequence |
| NEW | **L2** | V1H-mastering_market_structure… · 00:18:49 | "if you have a high volume candle sequence which is the extension and it's too high volume so the extension is just maybe one or two massive one minute candles" | the HVCS **is** the extension; too few candles is a defect |
| EP2-005 | L1 | phase 2 | HVCS/LVCS structure | volume grading, not a close-direction rule |

**No source requires every candle in the sequence to close in the trade direction.** The property Tom states twice, in
two different videos, is that the sequence **respects the highs (or lows)** while trending.

### 2.2 "Runs directly into the shift" (OQ-43)

D19-6 approved the principle from the master slide ordering "HVCS → HILO". The evidence adds no count of bars between
the sequence and the shift; D20-4 already recorded the continuity reading as an ASSUMPTION with counts as diagnostics.

## 3. What actually happened on the recovered examples

Evaluated at the engine's own decision instants (STRUCTURE 1m bars; extension direction DOWN for both buys):

### CX-LT1-1 — a bar-close timing artefact

| Instant | Extension extreme bar | HVCS run | Valid (≥ 4) | Continuity |
|---|---|---|---|---|
| 01:38:40 (engine decision) | 01:37 | **3 min** | **no** | CONTINUOUS |
| 01:39:35 (shift under LAST_RESET) | 01:38 | 4 min | yes | CONTINUOUS |
| 01:40:00 | 01:38 | 4 min | yes | SIDE_BROKEN |

The rule fails at the decision instant **only because the bar that sets the extension low (01:38) has not closed yet**.
One minute later the same sequence is valid. The 1m bars into the low (01:35-01:38) are: 01:35 non-conforming (close
above open), 01:36 conform, 01:37 conform (body $5.40), 01:38 conform (the low bar).

### CX-TE1-1 — the extreme bar closes against the sequence

| Instant | Extension extreme bar | HVCS run | Valid |
|---|---|---|---|
| 04:36:40 (engine decision) | 04:34 | 0 min | no |
| 04:38:55 (shift under LAST_RESET) | 04:37 | **0 min** | **no** |

The 04:37 bar makes the extension low (4102.88) but **closes bullish** (open 4103.59 → close 4104.07) while still
respecting the highs (high 4104.08 ≤ previous high 4105.22). PC2 requires the run to end on a candle that closes in the
trade direction, so the run length is 0 and the rule fails at every instant. By Tom's stated definition — "respecting
all the highs … consistently moving bearish" — the bar that prints the low and holds below the prior high is part of
the sequence, and the reversal candle at the extreme is exactly what the entry is taken against.

### CX-LT3-2 — a genuine break

At Tom's entry time the sequence is 0 minutes with `SIDE_BROKEN` continuity: price had traded back above the end bar's
high before the entry. CX-LT3-2's problems are not primarily HVCS (see the event reconstruction).

## 4. Candidate interpretations of "runs directly into the shift"

| Id | Reading | Machine definition | Supporting | Against |
|---|---|---|---|---|
| **A** | Immediately adjacent bars | run must end on the bar before the shift | slide ordering | contradicted by VP2 00:04:49 (indecision candles allowed) |
| **B** | Same directional leg | the sequence and the shift belong to one unbroken leg | 00:02:06, 00:05:19 | needs a leg definition |
| **C** | Same unresolved displacement sequence | run ends at the extension extreme; no opposing reset before the shift (PC2 today) | D19-6, D20-4 | the *conforming-candle* test is stricter than the evidence |
| **D** | **No opposing structural reset** | the sequence is the run that respects the highs/lows; it survives while nothing takes out the end bar's respected side | **00:02:06, 00:05:19, 00:04:49** (the only definitions Tom gives) | no explicit count anywhere |
| **E** | Volume-graded (HVCS vs LVCS) | grading only, never a gate | EP2-005, 00:05:25 | already diagnostic in PC2 |

The evidence points at **D**. The distance between D and PC2's C is the `close < open` requirement on every conforming
candle, plus the requirement that the run **end** on such a candle.

## 5. Findings

1. **The conforming-candle test is not evidence-backed.** Tom defines the sequence by *respecting the highs/lows* while
   trending, and explicitly admits indecision candles. PC2 additionally requires a close in the trade direction on every
   counted candle and on the final candle.
2. **CX-TE1-1's failure follows entirely from that extra requirement**: the extreme bar respects the highs but closes
   bullish.
3. **CX-LT1-1's failure is an evaluation-instant artefact**: the displacement bar has not closed at the decision. This
   is the OQ-43 "end bar ≤ as_of" reading, and it means the rule can only pass one minute after the extension extreme.
4. `min_minutes = 4` is the one number with a source ("HVCS, 4+ mins"). The 10-30 minute figure on the same slide
   belongs to the overextension, not to this rule — worth confirming the two are not conflated.
5. `max_violations = 1` and `lvcs_body_atr` are ASSUMPTIONS (OQ-08) with no course number, and the owner's instruction
   not to invent an indecision count is respected: no count is proposed.

## 6. Options for the owner (not selected here)

| Id | Option | Classification if adopted |
|---|---|---|
| H-1 | Conforming candle = respects the high/low only (drop `close < open`) | CANON_CORRECTION |
| H-2 | Allow the run to **end** on a bar that respects the side but closes against it (the reversal bar at the extreme) | CANON_CORRECTION |
| H-3 | Evaluate the end bar as the extension extreme bar **known at the shift**, not at the decision | IMPLEMENTATION_FIX (causality preserved: the shift is later than the bar close) |
| H-4 | Keep C and accept that the rule rejects Tom's own examples | NO_CHANGE |

H-1 and H-2 are the same evidence question seen from two sides; H-3 is independent and mechanical.
