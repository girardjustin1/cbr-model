# Weekend Condition-Window Evidence Note (W-1)

**Doc:** CBR-EVD-W1 · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D27 §9 (from D26) · **Status:** SECONDARY, FOR OWNER INFORMATION
Secondary to T3-1 by owner instruction. PC2 unchanged; **no change proposed**. Quotes verified mechanically.

---

## 1. What prompted it

On CX-LT3-2 (Monday 2025-11-10, 01:00 UTC, the second hour of Asia), the 8-hour **tradable-time** condition window
(OQ-40, D19-3 ASSUMPTION) starts **Friday 2025-11-07 16:00**. The engine's condition is `TRENDING_RANGE` with
`direction = NONE`, computed from Friday's MTF swings, while Tom says "So very bullish, um, a little bit trendy".

## 2. Evidence on what the window is

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| E1H-005 / NEW | L1 | V1H-defining_mtf_ranges · 00:01:00 | "I define middle time frame as the past 5 to 12 plus hours. 5 to 12 plus hours. Low time frame is defined by the past 30 minutes to an hour" | a **rolling lookback over price action**, expressed in hours |
| NEW | L1 | V1H-defining_mtf_ranges · 00:01:51 | "the easiest way to identify middle time frame is just to look back and see how has the past five to four plus hours been looking" | "**look back**" at the chart: whatever candles are displayed |
| NEW | L1 | V1H-defining_mtf_ranges · 00:04:17 | "you want to identify price action over the past 5 to 12 plus hours that has been correcting over 50 or 50 or more of the previous [move]" | the window is the input to the correction ratio |
| NEW | L1 | V1H-candle_behavior_timing · 00:03:45 | "where is the alley candle opening within the middle time frame range" | the window positions the hour inside a range |

**Nothing in Level 1 mentions weekends, session boundaries or a reset after a market closure.** Tom describes looking
back over the last N hours of chart price action; on a TradingView chart the weekend simply has no candles, so "the
past 8 hours of price action" on a Monday Asia hour *does* reach back into Friday — which is what the engine does.

## 3. Assessment

| Concept (D26 §9 list) | Support | Note |
|---|---|---|
| Rolling **tradable** hours (PC2) | consistent with "look back … past 5-12+ hours" of chart price action | reaches Friday on a Monday-Asia hour under **any** window length in the 5-12 h range |
| Rolling **clock** hours | not distinguishable from the above in Tom's language | would reach further back in calendar time and include even more of Friday |
| Current-session structure | no L1 support found | Tom discusses sessions for *timing*, not for the MTF range definition |
| Post-open (since the week's reopen) structure | no L1 support found | would be a new rule |
| Uninterrupted range | no L1 support found | — |

**Finding: the window basis is not the most likely cause of the CX-LT3-2 condition mismatch.** Every window length in
the quoted 5-12+ hour range reaches back across the weekend into Friday, so no window choice makes the engine read the
Monday rally alone.

The mismatch is more plausibly in the **direction test**: the engine derives `direction` from the last two MTF swing
highs and lows (higher-high + higher-low = UP). In this window the highs fall (4027.53 → 4009.29) while the lows rise
(3992.47 → 3994.55), giving `NONE`, and `M1H-COND-03` then blocks every candidate. That is the swing/direction
definition (OQ-01, OQ-02 ASSUMPTIONS), not the window basis.

## 4. Recommendation

- **No change to W-1.** The tradable-time window is defensible on the evidence.
- The open item that actually bears on CX-LT3-2's condition is the **trending-range direction test** (OQ-01/OQ-02):
  whether "bullish trending range" should be read from the last two swing pairs, from the range's position, or from a
  directional measure. That deserves its own evidence review if the owner wants CX-LT3-2's condition reconciled, but it
  is independent of T3-1 and not on the critical path.
- Reclassify W-1 in the PC3 change set from `ASSUMPTION_CHANGE` to **NO_CHANGE**, with the direction test recorded as a
  new open question instead.
