# OQ-47 Evidence Review: What External Structure Must the Sweep Take?

**Doc:** CBR-EVD-047 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §3-4 (from D27) · **Status:** FOR OWNER DECISION
PC2 frozen; type-3 implementation unmodified. Measurements are STRUCTURE-data diagnostics from a scratchpad prototype.
Quotes verified mechanically. **Event counts are reported as implications, never as evidence** (D28 §2).

---

## 1. The question

Under the approved re-anchoring principle (T3-B), what must the **sweep leg** take out for a CBR type 3 to be valid?

## 2. Evidence

| Id | Level | Source · time | Verbatim | Bears on |
|---|---|---|---|---|
| EP1-008 | L1 | VP1-1_4_shifts_type_3_choch · 00:01:47 | "you take out high, then reverse, immediately reverse, take out a low" | **G**: ordinary type-3 geometry, no named level |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:01:31 | "if you're taking a buy off a second shift, you want **this current 50 [15] minute candle** to push and take out **the previous high**" | **C**: the external take is performed by the 15m candle |
| NEW | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:02:32 | "**the 15-minute candle to take out the previous high or low to be beyond structure**" | **C**, and it names the purpose: "beyond structure" |
| E1H-021 | L1 | V1H-candle_behavior_extension · 00:02:47 | "ideally i want to take out the previous low for a buy take out the previous high" | **C** |
| NEW | L1 | V1H-candle_behavior_extension · 00:04:56 | "You take out the previous high, which is nice. And then you have the reversal set up" | **C**, sequencing: take first, setup after |
| E1H-017 | L1 | V1H-where_aoi_er_oe · 00:08:08 | "external just means that you're um like beyond structure … i find the best of reversals is when you take out the previous high" | **B/E**: "beyond structure" as a location quality |
| NEW | **L2** | V1H-mastering_market_structure… · 01:04:22 | "it's not going to be a very good extension if we don't take out the previous high" | **C** as a *quality of the extension*, not of the 5s trigger |
| NEW | L1 | V1H-1m_fractal_shift · 00:03:23 | "**i don't really need it as much to take out the previous low** like it's okay if it doesn't take out the previous low especially when we have a shift form" | **against a hard external requirement on the trigger** |
| EP1-012 | L1 | VP1-1_4… · 00:03:40 | "you just want the stop loss behind previous high low" | the swept extreme is the stop reference (**D**) |
| NEW | L1 | V1H-stop_losses · 00:01:34 | "i'll tend to go for … a stop above the most external high or low" | **D**: the relevant extreme is the *most external* one — the extension extreme |

### Where each requirement already lives in PC2

- The **15m external take** (option C) is already a separate rule: `M1H-6A-2-PREV-15M-BROKEN-BY-Q`.
- **Beyond structure / range position** (option E) is already `M1H-LOC-01/02/03`.
- The **extension extreme** (option D) is already the stop anchor (`anchor_at`, D17-2) and is the D9 pre-registered
  ablation `FINAL_PUSH` ("the entry's type 3 sweep must set the hour's extension extreme at entry", OQ-23).

## 3. Candidate readings and machine definitions

| Id | Reading | Machine definition (5s tier) | Verdict on the evidence |
|---|---|---|---|
| **A** | any confirmed LTF swing | sweep = new extreme beyond the most recent confirmed 5s swing of that kind | supported by EP1-008 alone; this is T3-B as prototyped |
| **B** | the immediately relevant structural swing | as A, but the swept swing must be the latest *external* structure of the entry tier | no distinct wording; collapses into A or E |
| **C** | the previous 15m candle high/low | the sweep bar's extreme must be beyond the previous 15m candle's extreme in the extension direction | strongly evidenced — **but as a property of the 15m candle, already rule `M1H-6A-2`** |
| **D** | the active extension extreme | the sweep extreme must be the hour's extension extreme known at that moment | evidenced indirectly (stop "above the most external high or low"); equals the D9 `FINAL_PUSH` ablation |
| **E** | a range high/low or named liquidity level | sweep must take an MTF range boundary | covered by `M1H-LOC-01/02/03`; no separate trigger-level wording |
| **F** | different levels for CBR15 vs CBR1H | — | **no evidence of a difference**; the tier changes, not the definition |
| **G** | no separately named external level | ordinary type-3 geometry at the entry tier; externality carried by the *other* rules | the 1m-fractal quote ("i don't really need it as much to take out the previous low") argues the trigger itself carries no external requirement |

## 4. Application to independent examples (qualitative geometry tests)

| Example | A | C | D | G |
|---|---|---|---|---|
| CX-LT1-1 (XAUUSD buy, taken) | CONSISTENT | CONSISTENT (sweep extreme beyond the previous 15m low) | CONSISTENT (sweep extreme = hour extension extreme) | CONSISTENT |
| CX-TE1-1 (XAUUSD buy, taken) | CONSISTENT | CONSISTENT | CONSISTENT | CONSISTENT |
| CX-LT3-2 (XAUUSD sell, taken) | CONSISTENT | CONSISTENT | CONSISTENT | CONSISTENT |
| CX-LT3-1 (XAUUSD, **rejected**) | CONSISTENT (no trigger fires in the window) | CONSISTENT | CONSISTENT | CONSISTENT |
| CX-LT2-2 (USDJPY sell, taken; narrative) | CONSISTENT ("sell at the break of that low") | NOT DETERMINABLE (no 15m levels recorded) | NOT DETERMINABLE (extension extreme not priced) | CONSISTENT |
| CX-LT2-1 (USDJPY, **rejected**; narrative) | NOT DETERMINABLE | NOT DETERMINABLE | NOT DETERMINABLE — Tom's stated reason is *timing* ("do I want to choose 22 minutes in? 37, 52"), not the sweep | NOT DETERMINABLE |
| VP1 drawn ranging type 3 (frame 00-03-04) | CONSISTENT | NOT DETERMINABLE | NOT DETERMINABLE | CONSISTENT — the levels drawn are **range boundaries** (supports E as a *location* idea) |
| VP2 HILO examples | CONSISTENT | NOT DETERMINABLE | INCONSISTENT — HILO levels are previous-candle extremes, not the extension extreme | CONSISTENT |

Measured on the three data-testable examples: in **all three**, Tom's own trigger has a sweep extreme that is both the
hour's extension extreme (D) and beyond the previous 15m extreme (C). No example discriminates between C, D and G,
because the CBR context makes them coincide.

## 5. Membership implications (reported, not used as evidence)

Of 1,794 re-anchored 5s type-3 breaks over 194 stored hours:

| Restriction | Share of T3-B breaks retained |
|---|---|
| D (sweep extreme = hour extension extreme) | 31% |
| C (sweep beyond the previous 15m extreme) | 35% |
| C **and** D | 22% |

These are consequences of each reading, not reasons to prefer one.

## 6. Conclusion

**Recommended: G, with the externality left where the course puts it.** The 5s type-3 trigger carries no separately
named external level; the external requirements are already expressed as distinct CBR1H rules —
`M1H-6A-2` (the 15m candle takes the previous high/low, option C) and `M1H-LOC-01/02/03` (beyond structure / range
position, option E). Adding an external condition to the sweep itself would **double-count** rules the engine already
applies, and the only Level-1 statement about the trigger's own external requirement is a denial ("i don't really need
it as much to take out the previous low … especially when we have a shift form").

**Option D deserves a separate decision** because it is materially different: it would require the entry's sweep to set
the hour's extension extreme. That is already the pre-registered D9 ablation `FINAL_PUSH`, it is consistent with all
three data-testable examples, and it is the natural reading of "a stop above the **most external** high or low". It is
recommended as a **research ablation to keep, not as a canonical requirement**, because no Level-1 sentence states it.

**Not recommended:** B (no distinct wording), F (no evidence of a model difference), C or E re-applied at the trigger.
