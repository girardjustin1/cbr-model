# OE-2 Evidence Review: What Is the 50% Pullback Measured Against?

**Doc:** CBR-EVD-OE2 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §11 (from D27) · **Status:** FOR OWNER DECISION
PC2 frozen; nothing implemented. Quotes verified mechanically. Diagnostics from STRUCTURE data; no outcomes, no P&L.
**The reading recommended below was not chosen because it recovers the parity examples**; §3 gives the wording
argument, §4 gives the example effects, §5 gives the cost.

---

## 1. What PC2 does

`M1H-OE-02` walks the bars to the extension extreme. At each bar, if the extension **so far** exceeds the activation
floor and the adverse excursion is ≥ 50% of that **running** extension, the rule fails — and the failure **latches** for
the rest of the hour.

## 2. Tom's language for "50%"

The phrase "50% of the previous move" is used at three different scales:

| Use | Source | "The previous move" means |
|---|---|---|
| Condition classification | V1H-what_direction_condition · 00:01:26: "we identify a range by it **correcting over 50 of its previous move on average**" | each MTF **leg**, swing to swing (the engine already measures leg-to-leg ratios) |
| Target | E1H-037 / M1H-TP-01: "target 50% of the previous move" | the **hour's extension** |
| Overextension pullback | E1H-018 · 00:01:26: "i'll define a pullback is that you correct 50% of the previous move" | the move being judged — **the extension** |

| Id | Level | Source · time | Verbatim | Bears on |
|---|---|---|---|---|
| E1H-018 | L1 | V1H-defining_a_good_extension · 00:01:19-00:01:26 | "We want it to overextend for around 20 minutes without much of a pullback at all … i'll define a pullback is that you correct 50% of the previous move" | the test is a property of **the overextension** |
| **NEW** | **L1** | same · 00:03:19 | "I want you to focus on how it overextended here. Not much of a pullback at all, really high volume. Okay. **Didn't correct 50% at all. Didn't even come close to that**" | Tom judges the **whole** extension, retrospectively, in proportions ("didn't come close") |
| NEW | L1 | same · 00:05:16 | "you over extend push bearish … but it's pretty low volume and you're **on average correcting 50% of the previous move**" | "on average" describes repeated corrections across the move, not a single latching event |
| NEW | L1 | V1H-what_direction_condition · 00:01:26 | "correcting over 50 of its previous move **on average**" | same phrasing, leg-relative, in the condition rule |

## 3. Candidate readings

| Id | Reading | Machine definition (causal, at each decision time) |
|---|---|---|
| **R1** | running sub-extension (**PC2**) | fails if any adverse excursion ≥ 50% of the extension *at that moment*; latches |
| **R2** | whole extension | fails if the **deepest** adverse excursion before the extreme ≥ 50% of the extension measured from the anchor to the **extreme so far**; re-evaluated at each decision, no latch |
| **R3** | latest leg | fails if the retrace of the **current** directional leg ≥ 50% of that leg |
| **R4** | active extension from activation (D27 §8) | R1 or R2 applied from `extension_activation_time` |

R1 and R2 are both causal: at any decision time the engine knows the extreme so far and the deepest retrace so far.
They differ in *what the retrace is compared with*, and in whether an early failure is permanent.

## 4. Effect on the three course hours (anchor = hour open, D8 unchanged)

| Example | Deepest retrace before the extreme | Extension size | Retrace as % of the extension | R2 verdict | R1 verdict (PC2) |
|---|---|---|---|---|---|
| CX-LT1-1 | $8.95 (at 01:30) | $35.77 | **25%** | passes | fails (first failure 01:01, $6.05 vs a $2.45 running extension) |
| CX-TE1-1 | $4.26 (at 04:28) | $19.56 | **22%** | passes | fails (04:05, $3.05 vs $6.05) |
| CX-LT3-2 | $6.38 (at 01:31) | $33.00 | **19%** | passes | fails (01:01, $4.01 vs $4.27) |

R2 reproduces Tom's own description of these hours — "didn't even come close" — with a wide margin (19-25% against a
50% limit). R1 fails all three on retraces of $2-6 moves in the first minutes.

## 5. Selectivity (cost of the reading, reported honestly)

Evaluated causally at minutes 25, 35 and 45 of every stored hour (582 evaluations over 194 hours):

| Reading | Hour-evaluations passing |
|---|---|
| R1 (PC2) | 71 (**12%**) |
| R2 (whole extension) | 235 (**40%**) |

R2 is materially more permissive. It is not trivially true — 60% of hour-evaluations still fail — but it changes the
rule from a rare gate to a common one, and it is the largest single behavioural change in the PC3 set.

## 6. Conclusion

**Recommend R2**, with the anchor unchanged (`HOUR_OPEN`, D27 §14) and combined with the activation state:

1. It matches the only passage where Tom **applies** the rule to a specific chart ("Didn't correct 50% at all. Didn't
   even come close to that") — a proportional judgement of the finished push, not a trip-wire on its first minutes.
2. It removes the **latch**, which has no source: nothing says an early retrace permanently disqualifies an hour, while
   00:10:42 explicitly describes an hour that misbehaves early and then sets up later.
3. It is consistent with the same phrase's use in the condition rule, where the engine already measures corrections
   proportionally rather than as a one-shot failure.
4. It needs **no new number**: the 50% is canon.

**Classification if adopted: CANON_CORRECTION** (the reference and the latch, not the threshold).

**Residual uncertainty:** R3 (latest leg) is also consistent with "on average correcting 50% of the previous move" and
was not separately measured against the examples; if the owner wants it tested, that is a further diagnostic. And the
interaction is real: with R2 the activation state is no longer load-bearing for these three examples, though it remains
justified on its own evidence.
