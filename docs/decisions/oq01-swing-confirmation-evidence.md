# OQ-01 (Reopened): When May a Newly Formed Swing Become the Type-3 Trigger?

**Doc:** CBR-EVD-001R · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §5 (from D27) · **Status:** FOR OWNER DECISION
PC2 frozen; nothing implemented. Reopened specifically for the **re-anchored** type-3 model: under T3-B the trigger
level moves to newly confirmed opposing swings, so *when a swing is confirmed* now decides signal membership.
No parameter was optimized; the k-sensitivity below is a sensitivity measure, not a selection.

---

## 1. Why this matters now

Under PC2 the trigger level is fixed when the pair is armed, so swing-confirmation timing mostly affects *which pair*
exists. Under T3-B the trigger is the **most recent confirmed opposing swing**, so confirmation timing directly sets
the trigger price and the moment a break becomes possible.

**Causality requirement (D27 §5):** the trigger must have existed, knowably, before the bar that breaks it.

## 2. Evidence

| Id | Level | Source | Verbatim | Reading |
|---|---|---|---|---|
| P1F-3 (slide, third-party graphic) | L1 | VP1-1_0_market_structure_direction · 00:01:52 (OCR) | "SWING occurs when price breaks an old High or Low" | a **break-based** definition: the swing is recognised when the prior extreme is broken |
| P2G-16 / P2G-66 | L1 | phase 2 | swing choice is "intuitive"; "can't give you purely mechanical rules" | **Tom gives no mechanical rule** |
| EP2-001 | L1 | VP2-1m_hilo_entries · 00:00:17 | "A one minute HILO entry is simply a even lower time frame shift" | at the entry tier the reference levels are **previous candle extremes**, known at each candle close |
| EP2-002/003 | L1 | VP2-1m_hilo_entries · 00:02:44-00:03:43 | "the candle prior to the break of structure needs to also break a structure the previous candle higher low" | confirmation is **candle-close based**, one or two candles |
| OQ-01 (existing) | — | `config/strategy.yaml` | ATR zig-zag, k = 3, ASSUMPTION with research range 2 / 3 / 4 | current implementation |

**Finding:** the course contains **no definition of when a swing is confirmed**. The only mechanical analogue is the
HILO, where the reference level is simply the previous candle's extreme at its close.

## 3. Options

| Id | Rule | Confirmation time | Causal? | Notes |
|---|---|---|---|---|
| **A** | after N bars without a new extreme | close of the Nth bar | yes | N has no source; ASSUMPTION |
| **B** | after opposing displacement (ATR zig-zag) | when price reverses k × ATR from the extreme | yes | **current PC2**; k = 3 ASSUMPTION |
| **C** | when price starts moving away | first bar closing away from the extreme | yes | earliest confirmation, most permissive |
| **D** | ATR zig-zag (= B) | — | — | — |
| **E** | HILO-style candle confirmation | the previous candle's extreme at its close | yes | closest to the only mechanical course definition; at the 5s tier this means a level every 5 s |
| **F** | direct course definition | **none exists** | — | P1F-3 is a third-party graphic, not Tom's wording |

## 4. Causality check on the three examples (current rule B, k = 3)

| Example | Trigger swing | Confirmed | Broken | Margin |
|---|---|---|---|---|
| CX-LT1-1 | H 4340.18 @01:38:15 | 01:38:35 | 01:39:35 | **60 s** |
| CX-TE1-1 | H 4105.56 @04:35:40 | 04:36:35 | 04:38:55 | **140 s** |
| CX-LT3-2 | L 4050.97 @01:37:50 | 01:38:40 | 01:39:40 | **60 s** |

All three triggers existed causally before their break, with a minute or more to spare. **Re-anchoring does not
introduce a look-ahead** in these cases.

## 5. Sensitivity of membership to the swing parameter (diagnostic, not a selection)

Tom's own trigger under T3-B at each zig-zag k:

| Example | k = 2 | k = 3 (PC2) | k = 4 |
|---|---|---|---|
| CX-LT1-1 (Tom 4340.13) | 01:39:35, trigger 4340.19 | 01:39:35, 4340.19 | 01:39:35, 4340.19 |
| CX-TE1-1 (Tom 4105.58) | 04:35:40, 4105.43 | 04:38:55, 4105.57 | 04:38:55, 4105.57 |
| CX-LT3-2 (Tom 4050.71) | 01:39:35, 4051.07 | 01:39:40, 4050.96 | **none within 3 minutes** |

**CX-LT1-1 is insensitive; CX-LT3-2 is lost at k = 4.** So under re-anchoring the swing definition is *material* to
membership, exactly as the owner anticipated, and k cannot be treated as a free research parameter without noting that
it now changes whether a course example is reproduced at all.

## 6. Conclusion

1. **No course definition exists** (option F is empty). Any rule is an ASSUMPTION.
2. **Keep option B (ATR zig-zag) for the parity candidate**, unchanged at k = 3, because: it is already frozen and
   tested, it is causal with a 60-140 s margin on all three examples, and changing it now would confound the T3-B
   decision with a parameter change.
3. **Record the sensitivity as a known risk**, not as a reason to move k. The pre-registered research range (2 / 3 / 4)
   stays research-only; the owner should note that a future ablation over k now also changes example reproduction.
4. **Option E (HILO-style) deserves a separate future review** if the owner wants the entry tier to follow the only
   mechanical course analogue. It would be a larger change: at 5 s, the trigger would re-anchor every bar.

**Classification if adopted as recommended: NO_CHANGE for PC3** (k and the zig-zag stay), with the sensitivity recorded
in the spec record as an explicit open risk under re-anchoring.
