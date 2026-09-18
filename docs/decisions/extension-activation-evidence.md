# Extension-Activation Evidence Review: When Has an Extension Begun?

**Doc:** CBR-EVD-ACT · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D27 §2 (from D26) · **Status:** FOR OWNER DECISION
PC2 frozen and unchanged. **No numeric activation threshold is proposed.** D8 stays `HOUR_OPEN` (owner ruling); this
review is about when a move becomes an *extension* at all, i.e. when the 20-minute and 50%-pullback tests start to
apply. Quotes verified mechanically. No outcomes, no P&L, no parameter search.

---

## 1. The problem restated

PC2 treats the hour as extending from the first bar. The no-pullback test activates as soon as the running move
exceeds `oe.activation_atr = 0.5 × ATR(1m,14)` (OQ-08, ASSUMPTION, research range 0.25 / 0.5 / 1.0), so a $2 move in the
first minutes is an "extension" whose retrace disqualifies the hour permanently.

Measured on the three course hours (Dukascopy STRUCTURE):

| Example | Failing retraces | First | **Last** | Running extension at the last failure | Full extension by Tom's entry |
|---|---|---|---|---|---|
| CX-LT1-1 | 8 | 01:01 (+1m) | **01:12 (+12m)** | $10.36 | $35.77 |
| CX-TE1-1 | 1 | 04:05 (+5m) | **04:05 (+5m)** | $6.05 | $19.56 |
| CX-LT3-2 | 10 | 01:01 (+1m) | **01:10 (+10m)** | $4.27 | $33.00 |

Every failure occurs in the **first twelve minutes**, against moves 3-8× smaller than the extension Tom is describing.

## 2. Evidence

### 2.1 The extension may begin after the hour open

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| **NEW** | **L1** | V1H-candle_behavior_timing · 00:02:39-00:02:45 | "the overextension can happen, **can start around seven to 15 minutes in**, and then you're gonna have that happen, shift around 37 minutes in" | the extension's **start** is explicitly allowed to be 7-15 minutes into the hour |
| **NEW** | **L1** | V1H-candle_behavior_timing · 00:02:16-00:02:26 | "if the alley counter opens and it kind of you know fucks around for a [bit] and then pushes. Sometimes you can have the reversal happen a little bit later on into the hour" | early aimless movement is **not** the extension |
| NEW | L1 | V1H-candle_behavior_timing · 00:02:27-00:02:32 | "If you have it open and immediately push, sometimes you have the reversal happen a bit earlier on, around 22 minutes in" | the immediate-push case is the *other* branch, not the only one |
| NEW | L1 | V1H-candle_behavior_extension · 00:10:42 | "If the alley candle opens and kind of goes sideways for a bit and then pushes, you might have it set up around 37 to 52 minutes into the hour" | same structure, in a second lesson |
| NEW | **L2** | V1H-mastering_entry_timing… · 00:40:17 | "the open of the hour into around 13 minutes into the hour there's a delay so you have a 13 minute delay if you were to take a trade 22 minutes in it would only be like a seven minute extension" | duration is counted from the **start of the push**; the delay is subtracted |

### 2.2 What marks the beginning

| Concept | Evidence | Strength |
|---|---|---|
| **Displacement / decisiveness** | "clear decisive shift of direction with volume" (EP1-008, L1, about type 3); "high volume" and "impulse" throughout; never quantified (OQ-08) | moderate concept, **no number** |
| **Beyond structure** | "you want it to be beyond low timeframe, middle timeframe structure, beyond previous high or low" (V1H-seconds_shift_1m_hilo_hvcs · 00:01:47, L1); E1H-017 external structure | moderate |
| **Elapsed time** | "can start around seven to 15 minutes in" (00:02:41, L1) — a description of when it *can* start, not a rule | moderate as a range, weak as a rule |
| **Proportion of the candle** | "around 20 to 30 minutes of price action extending in one direction"; "40 to 50 percent of that candle pushing in one direction" (E1H-018, L1) | strong for the **length**, silent on the start |
| **Sideways start voids the hour** | "where the alley counter opens and you go sideways for 30 minutes that's telling you that there isn't a trade" (L1) | bounds how late an extension may begin |

**No Level-1 source states a minimum price displacement for an extension to be "active".** The floor currently in PC2
has no course origin.

## 3. Candidate concepts (D26 §2 list)

| Id | Concept | Deterministic definition | Evidence |
|---|---|---|---|
| **A** | Active immediately from the hour open (PC2) | pullback test applies from the first bar once the move exceeds `activation_atr` | slide step order; "open and immediately push" |
| **B** | Active after minimum elapsed time | the test applies only to price action after *t* minutes into the hour | "can start around seven to 15 minutes in" (L1) |
| **C** | Active after a meaningful displacement | the test applies once the move exceeds a displacement measure (ATR- or volume-based) | "decisive … with volume"; OQ-08, **unquantified** |
| **D** | Active after taking a relevant structural level | the test applies once the hour trades beyond the previous 15m candle's high/low (or the MTF range edge) in the extension direction | "beyond previous high or low" (L1); already a separate rule (`M1H-6A-2`) |
| **E** | Recognised retrospectively as the push into the extreme | the extension is the final directional leg; the hour open only fixes which candle is traded | "delay" passages (L2); "start of the push" language |

## 4. Effects on the three course hours (diagnostic only)

Measuring the extension from each concept's start point, evaluated at Tom's entry time:

| Concept | Start (CX-LT1-1 / CX-TE1-1 / CX-LT3-2) | No-pullback passes? |
|---|---|---|
| A hour open | 01:00 / 04:00 / 01:00 | **no / no / no** |
| D beyond the previous 15m level | 01:04 / 04:07 / 01:00 | **no / no / no** |
| E start of the final push | 01:01 / 04:00 / 01:02 | **no / no / no** |
| B after the early phase | — | passes on all three **only if** the start is later than +12 / +5 / +10 minutes |

**Finding.** Moving the *anchor* does not fix the pullback test (A, D and E all still fail): the disqualifying retraces
happen inside the first twelve minutes but *after* those anchors. Only two things change the outcome: (i) starting the
measurement after the early phase (concept B), or (ii) changing what counts as an extension worth testing at all
(concept C — the activation floor — or the pullback reference, OE-2 in the PC3 list).

The observed last-failure times (+12, +5, +10 minutes) fall **inside** the 7-15 minute window Tom describes. That is a
consistency check between the evidence and the data, **not** a threshold selection: the range comes from the quote, and
no value is chosen here.

## 5. Findings

1. **Level 1 explicitly allows the extension to start after the hour open** ("seven to 15 minutes in"), and explicitly
   treats early aimless movement as not-the-extension. PC2 has no representation of either statement.
2. **No Level-1 evidence supports a minimum displacement number.** If a displacement floor is kept, it is an
   ASSUMPTION and should carry a pre-registered research range.
3. The two most evidence-backed concepts are **B** (an early phase that is not yet the extension) and **D** (the
   extension counts once price is beyond the prior structural level). D has the advantage of being structural rather
   than numeric, but on these three hours it does not change the outcome on its own.
4. Concept C is the current implicit mechanism (`activation_atr`), and it is the parameter actually responsible for the
   failures — while having no course source at all.

## 6. Recommendation (no number proposed)

Ask the owner to rule on the **concept** first:
- if **B**: the duration/pullback tests apply to price action after an early phase, with the phase length declared as
  an ASSUMPTION over a pre-registered range taken from the quoted "7 to 15 minutes";
- if **D**: activation is structural (beyond the previous 15m high/low), with no new number, and the pullback question
  (OE-2) must then be settled separately because D alone does not resolve these hours;
- if **C**: `activation_atr` stays but must be justified as an assumption and given a declared range.

A numerical assumption **is** required under B and C; under D it is not. In every case the pullback *reference*
question (whole move since the anchor vs the current leg, OE-2) remains open and is the other half of this problem.
