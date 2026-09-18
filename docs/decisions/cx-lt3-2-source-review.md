# CX-LT3-2 source review, the 20-minute rule, and the HVCS contradiction question

**Doc:** CBR-EVD-LT32 · **Version:** v1.0 · **Date:** 2026-09-18 · **Ruling:** D36 §3-7
**Status:** EVIDENCE ONLY. PC4 is unchanged and frozen, no rule was altered, no PC5 exists, no run was repeated.
No trade outcome was used. (Disclosure: the live-trade frames display a running P&L panel; it was seen incidentally
while locating the entry chart, is recorded nowhere, and plays no part in any conclusion below.)

---

## 1. What the source actually says about CX-LT3-2

The video clock maps to UTC with a constant offset of **+01:23:36**, confirmed by three independent anchors: Tom says
"23 minutes into the second hour of Asia" at 00:00:04, "36 minutes in" at 00:12:24, and "approaching 52 minutes into
the hour" at 00:28:19. All three land correctly on 01:23, 01:36 and 01:51 UTC.

| Video | ≈ UTC | Verbatim | Bearing |
|---|---|---|---|
| 00:01:07 | 01:24:43 | "So very bullish, um, a little bit trendy. **I'm not the biggest fan of this sort of condition to be taking a reversals in**, but it is, uh, a pretty nice extension." | condition flagged as one he dislikes for reversals |
| 00:01:20 | 01:24:56 | "Did we correct? **I guess kind of did correct.**" | hedged on the no-pullback quality |
| 00:02:11 | 01:25:47 | "Even though gold's very trendy, it's a nice extension." | extension accepted, condition still flagged |
| 00:05:06 | 01:28:42 | "Really high volume." | about the extension push, ~01:28 |
| 00:08:10 | 01:31:46 | "ideally this to push bullish take out the previous high and then like have a you know shift set up … perfect sort of scenario would be **37 minutes in**" | the entry he is waiting for is *take the previous high, then a seconds shift* |
| 00:08:34 | 01:32:10 | "not really clean shift at all i mean technically you took out but **not big enough** shit for me to care" | he rejects an earlier candidate by eye |
| 00:12:24 | 01:36:00 | "So we've taken out previous hire. It's **36 minutes in**." | previous-15m take confirmed by Tom at ~01:36 |
| 00:15:11 | 01:38:47 | "might potentially enter around **38, 39 minutes** into the hour" | |
| 00:16:26 | 01:40:02 | "Looks like we are in a position." | entry ≈ 01:40, matching the frozen stated entry |
| 00:17:40 | 01:41:16 | "this could like, you know, **very easily lose** and I'll just be happy with it" | |
| 00:17:47 | 01:41:23 | "**It's not the best condition.**" | |
| 00:17:58 | 01:41:34 | "**I think this is good enough though.**" | explicit discretionary acceptance |

**What Tom never says in this video:** "HVCS", "high volume candle sequence", "20 minutes", "textbook", or any claim
that the setup satisfies a stated rule. There is no recap slide and no exception carve-out.

**Cross-references:** the trade appears nowhere else in the corpus. There is no journal-table row for 2025-11-10 in
the captured frame. By contrast the same journal table labels **"textbook · October 24"** (= CX-TE1-1) and
**"new · October 21"** (= CX-LT1-1) — the two examples PC4 reproduces cleanly.

## 2. The 20-minute extension rule (D36 §4)

| Id | Source · time | Verbatim | Force |
|---|---|---|---|
| E1H-018 | V1H-defining_a_good_extension 00:01:19 | "We want it to overextend for **around** 20 minutes without much of a pullback at all" | **approximate** |
| E1H-018 | same 00:02:12 | "it's **around 20 to 30 minutes** of price action extending in one direction without a pullback" | **range, approximate** |
| — | same 00:02:26 | "it's just around like **40 to 50 percent** of that candle pushing in one direction … if it's 15 minute candle behaviour that's around seven and a half minutes" | **proportional guidance**, not a floor |
| — | same 00:03:10 | "this hourly candle open here and immediately push bullish **around almost 20 minutes**. It happened a bit early on in the hour, but it's a **really nice overextension**" | **explicitly validates a sub-20-minute extension as "really nice"** |
| — | same 00:04:41 | "you have a really nice … **20 to 30 minutes** of price action pushing bearish, you have a bit of a pullback around 22 minutes in but that's not really 50 so that's still fine" | tolerance language |
| — | same 00:05:03 | "where the alley candle opens and you **go sideways for 30 minutes** — that's telling you there isn't a trade" | the failure mode is *no push*, not a *short* push |
| E1H-002 (slide) | same 00:00:38 | "OE? → **around 2 15 min intervals** push in one direction" | **approximate** |
| L2 only | V1H-in_depth_backtesting 00:25:18 / 00:58:00 / 01:08:39 | "you have around 20 minutes of extension"; "definitely have 20 minutes of extension, 30 minutes of extension" | consistent; reported as clarification, never used to override L1 |

**Conclusion: GUIDANCE, not a hard requirement.** Every L1 statement is hedged ("around", "40 to 50 percent",
"around 2 15-minute intervals"), and one L1 instance **explicitly calls an extension of "almost 20 minutes" a really
nice overextension** — an example that a hard `≥ 20` floor would reject. The corpus nowhere says "at least",
"minimum" or "must". PC4 implements `oe.min_minutes = 20` as a hard floor labelled CANON; the *number* is sourced,
the *hardness* is not.

This conclusion does not rest on CX-LT3-2 and was not inferred from it (D36 §4).

## 3. Independent duration measurements (D36 §5)

Measured from stored 1-minute bars only — no PC4 output, no engine run. Duration runs from the stated anchor to the
extension extreme reached by the source's own stated entry time.

| Case | Hour | Extreme | From hour open | Q1 activation | From activation | Tom's assessment |
|---|---|---|---|---|---|---|
| CX-LT1-1 | 01:00 | 01:38 | **38 min** | 01:07 | 31 min | journal row "new"; taught as a live win |
| CX-TE1-1 | 04:00 | 04:37 | **37 min** | 04:07 | 30 min | journal row **"textbook"** |
| CX-LT3-2 | 01:00 | 01:37 | **37 min** | 01:10 | **27 min** | "not the best condition… good enough though" |
| HX-1 | 05:00 | 05:26 | 26 min | 05:21 | **5 min** | presented as a valid HVCS→HILO entry in the lesson that *defines* the HVCS |
| HX-2 | 02:00 | 02:36 | 36 min | 02:10 | 26 min | "the high volume counter sequence into a high low entry" |

Two findings, both independent of PC4's verdict:

1. **No example measures under 20 minutes from the hour open.** The 20-minute figure is comfortably satisfied by
   every dated example when measured the way E1H-018 describes it — from the candle open.
2. **The binding constraint in practice is *when and whence* duration is measured, not the number.** CX-LT3-2
   measures 27 minutes at its shift but **16** at the decision instant, which is what PC4 scores. HX-1 measures 26
   minutes from the hour open but **5** from the Q1 activation anchor — and Tom presents that setup as valid.
   *Caveat:* the HX-1 lesson frames its example at the 15-minute scale and states no hourly extension, so the 5-minute
   figure tests PC4's activation convention rather than an explicit hourly judgement by Tom.

## 4. The HVCS contradiction question (D36 §6)

**Tom does not call CX-LT3-2's sequence an HVCS.** The word never appears in the video, nor does "high volume candle
sequence". The only volume remark, "Really high volume" at ≈ 01:28:42, describes the extension push roughly eleven
minutes before the entry, not the run into the 01:39-01:40 shift. The entry he narrates is "take out the previous
high … then a shift set up on the seconds time frame" — the seconds type-3 path, not the HVCS→HILO path.

The HVCS requirement on this case comes from **our** variant-A model, which makes HVCS mandatory for every CBR1H
entry. It is **inferred by us, not asserted by the source.**

**Therefore there is no direct source contradiction to record.** PC4 measuring 0 conforming minutes at the
extension-extreme anchor contradicts no statement Tom makes about this trade. (Variant B, which carries no HVCS
rule, produced no candidate in this hour, so the model offers no non-HVCS route to the trade either — that is a
separate structural observation, not a contradiction.)

## 5. Classification (D36 §7)

### DISCRETIONARY_EXCEPTION

**Evidence for it.** The source frames the entry as a judgement call, in Tom's own words, twice: he is "not the
biggest fan of this sort of condition to be taking a reversals in", says "it's not the best condition", concludes
"I think this is good enough though", and expects it "could very easily lose". He never claims the setup satisfies
a stated rule, never names an HVCS, never cites a duration, and the trade carries no journal label — unlike the two
examples PC4 reproduces cleanly, one of which his own journal calls "textbook".

**Why not CANONICAL_EXAMPLE_WITH_UNRESOLVED_RULE_CONFLICT** — the closest runner-up. That label asserts a conflict
between the source and a rule. A conflict requires the source to claim the rule was met; here Tom claims nothing of
the kind. What remains is a *model* question (both blocking rules are assumption-dependent), not a source conflict.

**Why not the others.** It is not MISLABELED (it is genuinely a CBR1H hourly reversal on XAUUSD, and PC4 reproduces
six of its eight hard dimensions plus the trigger time to within 20 seconds). It is not a NONCANONICAL_VARIANT (no
different entry model is described). It is not SOURCE_INCONSISTENT (nothing Tom says contradicts anything else he
says — he is consistent that this is a marginal trade). It is not INSUFFICIENT_EVIDENCE (the video is 29 minutes of
continuous narration with a legible chart).

**The residual, stated plainly.** Classifying the example as discretionary does not make PC4's two blockers correct.
The `M1H-OE-01` failure at 16 minutes is an artefact of evaluating duration at the decision instant — the same
evaluation-instant family as OQ-50 — and the HVCS anchor remains the OQ-48 assumption. Both stay open. Neither may
be resolved from this case (D36 §2).
