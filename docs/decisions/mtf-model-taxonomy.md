# MTF Model Taxonomy Review: TRR CT, TRR PT, IFS, FS, R — and the journal cases

**Doc:** CBR-EVD-TAX-001 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D33 §10-13
**Status:** FOR OWNER DECISION. Level-1 evidence first; Level-2 reported separately and never used to override L1.
No rule changed, no case deleted, no P&L or outcome column read.

---

## 1. What Level 1 says the models are

| Id | Source · time | Verbatim (L1) |
|---|---|---|
| E1H-010 | V1H-mtf_model_types · 00:00:04 | "There's **three main middle-timeframe models** that I have broken down the most common ranges into. First off, you have a **normal range**. I can call it a ranging range … then you have a **trending range** … relatively clear direction … still correcting over 50% on average" |
| — | same · 00:01:45 | "you can trade at the highs, so the lows or the highs. You can also trade **pro trending range** … **or counter trending range**. And there's two different ways that you trade this a bit differently" |
| — | same · 00:02:03 | "In a **pro trending range**, you're mainly looking for like an **AOI**, a shift for that pro trending range continuation … for **counter trending range** you want price to be **below the lows** … beyond structure … trading towards 50% of the previous move" |
| E1H-010 | same · 00:02:57 | "and then that kind of moves us on to a **fractal shift** / **inverse fractal shift** … a middle timeframe shift that happens over the past five to twelve plus hours, and you're either looking for price to overextend back in towards 50 [inverse], or you can do a **shift within the shift** for continuation [fractal shift]. Those are **three types of middle timeframe models that I define and I trade**" |
| E1H-011 | V1H-what_direction_condition · 00:07:13 | "it's an **inverse** when you're trading the correction, so if you're taking a buy here into 50, that's inverse, you're inversing that fractal shift" |
| — | V1H-mtf_model_types · 00:03:22 | "if I look at price action and it's **none of these at all** … that is an amazing indication that I should not be trading. **If it's trending, definitely shouldn't be trading**" |
| — | V1H-trade_journal · 00:00:27 | "you can look at how I define the variables when I'm taking a trade … because **I've been using that over the last month, like only been trading this model**" |
| E1H-047 | V1H-where_aoi_er_oe · 00:10:56 (slide) | journal columns: "Correlation \| **Condition** \| **CB Hour** \| MS Align \| Shifts \| 5m Interval \| OE LTF HVCS (10-30m) \| Pair \| Account \| Wick \| **Setup** \| AOI \| Entry Relativity \| Session Time \| 15m Intervals" |
| — | VP2-bonus_trr_forever_model · 00:00:06 | "if I just had to use one setup for the rest of my life … it's called the **trend range rejection, the TRR forever model**" — a separate phase-2 bonus setup with its own what/where/when |

**Level-2 clarification, reported separately and not used to decide anything:** in the long recording
`V1H-mastering_entry_timing_and_market_structure_for_trading_success` (00:19:52) Tom enumerates "TR CT, R … IFS …
FS … five types of middle timeframe models". That is the same taxonomy as E1H-010 with the trending range split into
its pro and counter variants, and the fractal pair split in two. It corroborates L1; it adds nothing L1 lacks.

## 2. Classification (D33 §10)

The journal records **CBR trades only** (V1H-trade_journal 00:00:27), so these labels describe the middle-timeframe
*context* of a CBR1H trade, not a different entry model.

| Label | Meaning in L1 | Classification | Engine status |
|---|---|---|---|
| **R** | normal / ranging range: corrections ≥ 75% | **CBR1H_VARIANT** (context label) | implemented — `RANGE` + `M1H-LOC-01` |
| **TRR PT** | trending range traded **pro**-trend; needs an AOI, "within structure" | **CBR1H_VARIANT** (context + location) | implemented — `TRENDING_RANGE` + `M1H-LOC-02` (AOI variants exist) |
| **TRR CT** | trending range traded **counter**-trend; price beyond the lows/highs, target ≈ 50% | **CBR1H_VARIANT** (context + location) | implemented — `TRENDING_RANGE` + `M1H-LOC-03` |
| **IFS** | inverse fractal shift: an MTF shift over 5-12+ h, traded as the correction back toward 50% | **CBR1H_VARIANT by model, UNIMPLEMENTED by context** | **not implemented** — no FS/IFS class exists in `condition.py` (`RANGE`, `TRENDING_RANGE`, `TREND`, `UNDEFINED` only) |
| **FS** | fractal shift: the same MTF shift traded as continuation ("shift within the shift") | **CBR1H_VARIANT by model, UNIMPLEMENTED by context** | not implemented |
| **TRR Forever** | "trend range rejection", a separate phase-2 bonus setup | **SEPARATE_MODEL** | out of scope for CBR1H entirely |
| "Trending" (journal `Condition` value) | not a model name; Tom's word for a trending-range context | **QUALITY_LABEL / JOURNAL_ONLY_LABEL** | maps loosely to `TRENDING_RANGE`, not deterministically |
| "Volume" (journal `Condition` value) | not in the L1 condition taxonomy at all; matches his extension-quality vocabulary ("is it high volume, low volume?", E1H-018) | **JOURNAL_ONLY_LABEL** | **UNRESOLVED** — no engine field corresponds |

**Label collision to record:** the journal's "TRR" (trending range) is *not* the phase-2 "TRR Forever" (trend range
rejection). Any future parsing of the journal must not conflate them.

**The gap this exposes:** Tom trades three MTF models and CBR1H implements two. A journal row in an FS/IFS context is
a CBR1H trade the engine structurally cannot classify, because the classifier has no state for it. That is a *scope*
fact about the implementation, not a defect in the rules that are implemented.

## 3. JM-2025-10-16 — TRR CT (D33 §12)

**Is TRR CT inside the CBR1H model family? YES.** It is the counter-trending-range variant, implemented as
`TRENDING_RANGE` + `M1H-LOC-03`, and the L1 description ("price beyond the lows … target 50% of the previous move")
matches the implemented rules.

**Ruling: the case may remain a future CBR1H machine-parity case**, with `model_scope = CONFIRMED_CBR1H`. Its dating
is corroborated independently of the journal time column: the hour tops at 4 227.32 at **00:40** and reverses, which
matches both the journal time (00:41 UTC) and CB 37.

Its disagreement is upstream of every entry rule — the hour classifies `UNDEFINED` on 2 MTF zig-zag legs where Tom
records a trending range — and **feeds OQ-01 / the condition-definition review**. Per D33 §12, no swing-logic change
is proposed from this one case.

## 4. JM-2025-10-17 — IFS (D33 §11)

**Is IFS a CBR1H variant the engine implements? NO.** It is one of Tom's three MTF models, but PC2/PC3 have no FS/IFS
condition class, no MTF-impulse detection, and no "correction toward 50% of the impulse" location rule. The engine
classified that hour `RANGE` and applied range location rules — a context the source does not claim.

**Ruling: PARITY_SET_CORRECTION.** JM-2025-10-17 must not bind a CBR1H parity verdict unless and until an FS/IFS
context is specified and implemented. Per D33 §11 the case is **preserved**, not deleted: it moves to a
`future_model_validation` section of the evidence base, tagged `model_scope = IFS_NOT_IMPLEMENTED`, ready for the
model that will contain it.

## 5. JM-2025-10-29 — TRR PT, and what the journal columns mean (D33 §13)

| Question | Answer from evidence |
|---|---|
| Is the time an entry time? | **Not established.** For two rows it coincides with the entry to the minute (12:39 PM → CX-LT1-1's 01:39:15; 3:38 PM → CX-TE1-1's 04:37-04:39). For this row, 7:14 PM → 08:14 UTC is minute 14, which contradicts the same row's CB 37 and falls outside the canonical :22-:52 window (E1H-024). Observation time, screenshot time and trade-management time are all consistent with what is visible and none can be excluded. |
| Is CB 37 a timing bucket? | **Yes, most likely.** ":37 is the sweet spot for the best reversals" (E1H-024, E1H-002 "T3 shift 20-45m"), and the `CB Hour` column is one of Tom's journal variables (E1H-047). It records where in the hour the candle-behaviour reversal sits. |
| Is TRR PT a model name? | **Yes** — the pro-trending-range MTF context (§2). |
| Does BUY describe the setup direction? | Presumably, but it cannot be checked: the frozen hour 08:00-09:00 has its low at the hour open and rises all hour, so no down-extension exists for a BUY reversal. Either the direction or the hour is wrong, and the source cannot say which. |
| Does the row correspond to the frozen hour? | **Unresolved.** The parity set derived the hour from the time column; the CB column implies a different minute. No engine run was made on any other hour (D33 §13). |

**Ruling: SOURCE_AMBIGUITY.** JM-2025-10-29 is downgraded to **NARRATIVE / REFERENCE ONLY**. It may not bind a
CBR1H parity verdict and no CBR1H rule may be changed because of it (D33 §13). It is preserved in the evidence base
with its ambiguity recorded.

## 6. Consequence for the hour-level set

Of the three HOUR_LEVEL cases, exactly **one** (JM-2025-10-16) survives as a `CONFIRMED_CBR1H` machine case. That
does not change the CBR-RUN-013C-1 verdict, which stays FAIL as executed — it changes what a *future* hour-level set
may contain (see `research/examples/cbr1h-parity-set-proposal.md`).

## 7. Open taxonomy questions

1. Should CBR1H be extended with an FS/IFS context, or should FS/IFS become a separate candidate model with its own
   spec? Tom trades all three; the project implements two.
2. What does the journal `Condition` column mean when it reads "Volume"? Until answered, journal condition values
   cannot be scored at all.
3. Does the journal `Setup` column (E1H-047) carry the MTF label, or is there a separate MTF-model column? The
   frozen manifest calls the field `mtf_model`; the slide shows `Condition` and `Setup` as separate properties.
