# T3-1 Evidence Review: What Is the Type-3 Sweep?

**Doc:** CBR-EVD-T31 · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D27 §6-8 (from D26) · **Status:** FOR OWNER DECISION
PC2 frozen and unchanged; the type-3 implementation was **not modified**. The comparison engine below is a scratchpad
prototype used for measurement only (never in `src/`). No profitability, no trade outcomes, no parameter search.
Transcript quotes verified mechanically with the `tests/test_evidence.py` normalizer.

---

## 1. The conflict

PC2 (`structure/shifts.py::track_type3`, `latest_pair_only=True`) arms a pair of consecutive confirmed swings
**X → Y**, then requires price to **exceed X again** (the sweep) and afterwards break **Y**, the opposing swing that was
confirmed *before* the sweep. A newly confirmed opposing swing **disarms** the pattern (`NEW_SWING`).

In CX-LT3-2, Tom's sell is the break of a low that formed **after** the high that took the previous 15m high. PC2
classifies that same price event as the **sweep leg of a BUY** and never arms a SELL there.

## 2. Evidence

### 2.1 The canonical definition

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| EP1-008 | L1 | VP1-1_4_shifts_type_3_choch · 00:01:33-00:01:52 | "the main characteristic of it is that you um take out the higher low and then reverse and take out the opposite so for example for a cell example you you take out high, then reverse, immediately reverse, take out **a low**" | "**a** low" — the opposing swing is **not qualified** as the one that existed before the sweep |
| EP1-008 | L1 | same · 00:01:14 | "you go from making higher highs and high lows **making a higher high** you have a break to the upside this is for a cell example" | the sweep leg is the **making of a new higher high**, i.e. the creation of the extreme, not a re-test of an old one |
| EP1-009 | L1 | same · 00:02:13-00:02:36 | "you just want a clear break of a high you want a clear break of a low uh ideally you want to close beyond to the high or the low and reverse" | two breaks, in order; no statement about which low |
| EP1-012 | L1 | same · 00:03:40-00:04:14 | "you just want the stop loss behind previous high low" | the stop sits behind the **swept extreme** (consistent with both readings) |
| NEW (frame) | L1 | same · 00:03:04 (frame `slides/00-03-04.jpg`) | drawn: price takes out the **range high**, reverses, takes out the **range low**, then shifts up | the levels swept are **pre-existing external structure**; the reversal follows |

### 2.2 The HILO, which Tom equates with the seconds shift

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| EP2-001 | L1 | VP2-1m_hilo_entries · 00:00:09-00:00:55 | "A one minute high low is just where you go from breaking either, you know, a **previous candle**, one minute candle high to breaking a one minute **candle low** within the span of like one or two candles" | both legs reference the **most recent** candle extremes, which move forward every candle |
| EP2-002 / EP2-003 | L1 | same · 00:02:44-00:03:43 | "the candle prior to the break of structure needs to also break a structure the previous candle higher low … So you want it to break a low and then break a high. You always need that" | the reference level **re-anchors** candle by candle |
| NEW | **L2** | V1H-mastering_market_structure… · 00:46:52 | "Every one minute high low is a second's market structure shift" | the 1m HILO and the 5s type 3 are the same object at different resolutions |

**Finding.** The only *mechanised* definition Tom gives of the same object (the HILO) uses **continuously re-anchored**
levels. Nothing in L1 freezes the opposing level at the moment the pattern is armed, and nothing says a newly formed
opposing swing cancels the setup.

### 2.3 Independent examples outside the three parity examples

| Example | Level | What it shows |
|---|---|---|
| **CX-LT2-2** (USDJPY, 2025-10-23, sell, taken) | L1 | "okay so i'll take a sell at the brick of that low" — the same geometry: sweep into the extension high, then sell the **break of a low**. Different instrument, different session, same structure. Not data-testable (USDJPY out of instrument scope, D7) |
| **CX-LT2-1** (USDJPY, same hour, **not taken**) | L1 | an early "bit of a second shift" at ~22 minutes that Tom **rejects** — an independent negative case for the trigger family |
| **CX-LT3-1** (XAUUSD, 2025-11-10, not taken) | L1 | the rejected early shift; **neither** interpretation fires in its window (§4.3) |
| Frame `00-03-04` (XAUUSD, 2025-01-20/21) | L1 | the drawn ranging type 3; no stored tick data for that date, so narrative only |
| Journal rows | L2 | 44 rows; entry times and prices are not recorded, so none is data-testable |

**Limitation to state plainly:** there is no *additional data-testable* positive type-3 example in the stored data.
The independent evidence is narrative (CX-LT2-1/2, frames) plus the negative controls.

## 3. Candidate interpretations

| Id | Interpretation | Deterministic machine definition |
|---|---|---|
| **T3-A** | **PC2 today** | pair the last two confirmed swings X→Y; arm when Y confirms; sweep = price exceeds X; trigger = break of Y (fixed at arm time); a new confirmed swing of Y's kind **disarms**; `max_reversal` from the sweep bar |
| **T3-B** | **Re-anchoring** | sweep = price exceeds the most recent confirmed swing of the extension's kind; while swept, the trigger is the **most recent confirmed opposing swing at each moment** (a new opposing swing **re-anchors** instead of disarming); `max_reversal` from the latest sweep extreme; tick offset, causality and ordering unchanged |
| **T3-C** | **External-level sweep** | as T3-B, but the sweep must take a *named* external level (previous 15m candle high/low, or range boundary) rather than any prior swing |
| **T3-D** | **HILO-literal** | trigger = break of the previous candle's opposing extreme on the entry tier (EP2-001), with the prior-candle validity rule of EP2-002 |

T3-A and T3-B differ in exactly one behaviour: **what a newly confirmed opposing swing does after the sweep** —
disarm (A) or re-anchor (B).

## 4. Effects (measured, STRUCTURE data, no outcomes)

### 4.1 The three positive course examples

| Example | Tom's entry | T3-A | T3-B |
|---|---|---|---|
| CX-LT1-1 | 4340.13 @ 01:39:15 | break 01:39:35, trigger **4340.19** ✓ | break 01:39:35, trigger **4340.19** ✓ |
| CX-TE1-1 | 4105.58 @ ~04:38 | break 04:38:55, trigger **4105.57** ✓ | break 04:38:55, trigger **4105.57** ✓ |
| CX-LT3-2 | 4050.71 @ 01:40:00 | earliest SELL break **01:50:40** ✗ (10 min late) | break **01:39:40**, trigger **4050.96** ✓ (swept extreme 4053.43, broke the 01:37:50 low) |

T3-B reproduces all three triggers; T3-A reproduces two. **This alone is not a reason to adopt T3-B** (D26 §8).

### 4.2 Signal-volume effect

5-second type-3 completions over all stored XAUUSD data (194 hours: the three course windows plus the four recent
feed-comparison days):

| | T3-A | T3-B | ratio |
|---|---|---|---|
| completed 5s type-3 breaks | 1,123 | 1,863 | **1.66×** |

T3-B is meaningfully more permissive. These are raw structural events, before any CBR rule gating.

### 4.3 Negative controls

| Control | T3-A | T3-B |
|---|---|---|
| CX-LT3-1 window (2025-11-10 01:28-01:36) | 0 breaks | **0 breaks** |

T3-B does not fire where Tom explicitly refused.

### 4.4 Effect on the existing type-3 unit fixtures

| Fixture | Under T3-B |
|---|---|
| `test_type3_sell_detected` | unchanged (SELL break, trigger 99.99, swept 110, broke 100) — **passes** |
| `test_type3_rejects_slow_reversal` | TIMEOUT, no break — **passes** |
| `test_type3_buy_matches_course_example_structure` (CX-LT1-1 shape) | identical (trigger 4340.19, sweep extreme 4332.95) — **passes** |
| `test_type3_rejects_when_new_swing_low_forms_first` | **intent inverted**: no SELL at the old level 100 (assertion still true), but a SELL now fires at the **re-anchored** level 104. This fixture encodes T3-A's disarm rule and would need restating |

So one of four fixtures encodes the disputed behaviour; the other three are agnostic.

## 5. Answers to the ten questions (D26 §7)

| # | Question | Answer | Strength |
|---|---|---|---|
| 1 | Does the sweep require an already-confirmed swing before the liquidity take? | **No statement requires it.** EP1-008 describes "making a higher high"; the swept object in the frame is external range structure | moderate |
| 2 | Can the point that first takes the external high/low be the sweep extreme? | **Yes** on the evidence: that is what "making a higher high … then reverse" describes, and what Tom does in CX-LT3-2 and CX-LT2-2 | moderate |
| 3 | When is the post-sweep opposing swing confirmed? | Not addressed in the course. In the engine it is the ATR zig-zag `confirmed_at` (OQ-01 ASSUMPTION) | none from the course |
| 4 | SELL: take external high → form low → break low — sufficient? | Consistent with EP1-008 and with CX-LT3-2 / CX-LT2-2; no source contradicts it | moderate |
| 5 | BUY: the inverse? | Same, and it is what CX-LT1-1 and CX-TE1-1 show (both also satisfy T3-A) | moderate |
| 6 | Is a retrace/retest of the newly formed swing required first? | **No source requires it.** PC2's re-excursion requirement is the implementation reading | moderate |
| 7 | Does Tom distinguish external liquidity take from internal swing sweep? | He distinguishes **"beyond structure"** (E1H-017, "beyond previous high or low") as a *location* quality, not as a separate trigger class | weak-moderate |
| 8 | Different for CBR15 / CBR1H-A / CBR1H-B? | No evidence of different type-3 semantics per model; the tier changes (5s / 1m), not the definition | moderate |
| 9 | What fixes sweep_time, sweep_price, trigger_price, trigger_time? | Course level: sweep = the take of the level; trigger = the break of the opposing level; entry is a stop order at that break ("i'm just taking the entry on the break of the of the low", E1H-035). Exact tick offsets are IMPL | moderate |
| 10 | Is the engine's CX-LT3-2 direction wrong because it anchors the pair before the external high is created? | **Yes, that is the mechanism.** The pair (H 4053.43, L 4050.97) can only be armed for a *new* excursion above 4053.43, which never comes; meanwhile the same low-break is consumed as a BUY sweep | high (mechanically verified) |

## 6. Recommended deterministic definition (for owner decision, not implemented)

**T3-B**, stated precisely:

1. **Sweep.** While no arm is live in direction *d*, a sweep begins on the first bar whose extreme exceeds the most
   recent confirmed swing of the sweep kind (high for SELL, low for BUY). The sweep extreme updates while price
   continues beyond it.
2. **Trigger level.** The most recent confirmed opposing swing at each moment, minus/plus one tick. A newly confirmed
   opposing swing **re-anchors** the trigger; it does not disarm the pattern.
3. **Completion.** The arm completes when a later bar breaks the trigger; it expires when `max_reversal` elapses from
   the latest sweep-extreme update ("immediately reverse", EP1-008); causality and tick rules unchanged.

**Open risks the owner should weigh:** 1.66× more raw triggers; item 3 of §5 (swing confirmation) remains an OQ-01
assumption that now matters more, because re-anchoring makes the trigger depend on *when* a swing confirms; and one
unit fixture encodes the opposite rule.

## 7. Contradictory evidence

- The fixture comment and `t3_setup` docstring assert "break the low **that formed after it**" — i.e. after the swept
  high — which is T3-A's frozen pairing. This reading is *not* sourced to a quote in the evidence register.
- EP2-002's prior-candle validity rule ("the candle prior to the break needs to also break a structure") is a
  *restriction* that T3-B does not model; T3-D does. If the owner wants the HILO rule literally, T3-D should be
  reviewed alongside.
- CX-LT1-1 and CX-TE1-1 are equally consistent with T3-A, so two of three examples provide **no discrimination**.

## 8. Unresolved

1. Whether the sweep must take a *named external* level (T3-C) rather than any prior swing — untested, and it would
   reduce T3-B's extra volume.
2. Whether `max_reversal` should run from the first sweep bar or the latest sweep extreme (this changed one fixture
   result during prototyping and is an OQ-09 assumption either way).
3. No independent, data-testable positive example exists; the expanded parity set required by D26 §14 would have to be
   built before PC3 is validated.
