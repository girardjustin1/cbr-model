# CBR Glossary

Terms used by the CBR methodology, as defined in the canonical course videos. Every definition cites
evidence ids from `research/evidence/strategy_evidence.jsonl`; open issues link to
`open-questions.md` (OQ-ids).

**Legend.** *Deterministic*: can be computed from OHLC(V) data without judgment once the listed
open questions are settled. *Visual*: the author judges it by eye; any formula is an interpretation.

Transcription note: raw transcripts say "counter behavior", "alley", "50 minute", "second shift". These are
Whisper mishearings of *candle behavior*, *hourly*, *15 minute*, *seconds shift*
(`research/evidence/transcription_corrections.md`).

---

## Durations and conditions

### LTF / MTF / HTF (low / middle / high timeframe)
- **Definition.** Durations of price action, not chart timeframes. LTF = past 30-60 min; MTF = past 5-12+ h;
  HTF = ~1 day+ (E1H-005). The 15m course scales down: LTF range 1.5-2.5 h, MTF 5-10 h, HTF 20+ h (E15-003, E15-004).
- **Measured.** On the 1m chart with a measure tool over the lookback window.
- **Deterministic?** Window lengths yes; they are ranges, not points.
- **Unresolved.** A second, move-based tiering (LTF move <1 h, MTF 1-4 h) appears in E1H-006 (OQ-03). The 15m course
  labels 1.5-2.5 h "low timeframe", while the hourly course calls 30-60 min LTF (OQ-03).

### Condition (range / trending range / trend)
- **Definition.** How range-bound price is, measured by the average correction of each previous move over the
  lookback window (E1H-007, E1H-008, E15-014, slide E15-048 context):

  | Condition | Avg. correction of previous move | Structure breaks |
  |---|---|---|
  | Range | 75-100%+ | both directions (E15-013) |
  | Trending range | 50-75% | mainly one direction, clear HH/HL or LH/LL |
  | Trend (avoid) | < 50% (~25%) | one direction |

- **Heuristic.** "If you're unsure about direction, it's probably range bound" (E1H-008).
- **Deterministic?** Yes, given a swing definition (OQ-01) and an averaging rule (OQ-02).
- **Counterexample.** High-volume trend correcting <50%: author's documented loss (E1H-046).
- **Unresolved.** The What lesson says range = ">50%" (E1H-009) vs 75%+ elsewhere (OQ-02).

### Condition volume
- **Definition.** "Volume" means the size/speed of swings, not exchange volume. XAUUSD spot has no
  centralized volume. Prefer high-volume (large-swing) MTF ranges; avoid low-volume ranges (E1H-013).
- **Deterministic?** No (visual). Candidate proxy: swing amplitude vs ATR (RESEARCH-DERIVED, untested).

### Swing frequency (15m model)
- **Definition.** Number of swings in the range window: 1-2 = range too big, sit out; **3-6 = target**;
  7+ = lower-timeframe range, adapt entry (E15-048, E15-006, E15-005).
- **Deterministic?** Yes, given a swing definition (OQ-01).

### MTF model
- **Definition.** Named structure types the author trades (E1H-010): (1) **range**, (2) **trending range**
  (pro-trend continuation or counter-trend reversal), (3) **fractal shift / inverse fractal shift**. None
  identifiable → no trade.

### Fractal shift (FS) / Inverse fractal shift (IFS)
- **Definition.** After a large MTF impulse that breaks structure (a type-3 shift): **IFS** trades the correction
  back toward 50% of the impulse; **FS** waits for price to reach ~50% of the impulse and trades a lower-timeframe
  shift in the impulse direction (E1H-011, E1H-010). "IFS actually stands for an inverse fractal shift"
  (journal, J-PXleXsFFm-8 00:05:06, Level 2).
- **Deterministic?** Partly. Impulse detection is visual (OQ-04).
- **Also used at 1m scale** as an entry model (see *1m fractal shift*).

### Direction / market-structure alignment (MS Align)
- **Definition.** Direction = sequence of highs and lows (HH/HL bullish, LH/LL bearish). MS alignment = LTF
  structure shifting back in line with MTF structure before a pro-direction trade (E1H-045). Direction is
  **not** a filter; it changes where you may enter (E15-011).

### Prior-setup condition check ("CBRs roll in packs")
- **Definition.** Look back over the model's window (15m: 1.5-2 h; hourly: 5-10+ h) and count clean CBRs that
  set up and played out. 15m slide: 3+ = good; zero in the last hour = bad, sit out (E15-049, E15-008, E15-009).
  Never take the first CBR in a range; target legs 3-5 (E15-050, E15-007).
- **Deterministic?** Yes, once "clean" and "played out" are defined (OQ-05). It uses only past outcomes, so
  there's no lookahead.
- **Unresolved.** Slide says "not legs 1 or 2"; narration allows the 2nd "if more aggressive" (OQ-06).

---

## Location ("where")

### AOI (area of interest)
- **Definition.** Open/close prices of hourly (also 30m, 4h) candles; clusters drawn as zones. Only AOIs at the
  range extremes matter in a range; in pro trending ranges, an HTF candle-body level at the pullback (E1H-014).
  Secondary to location within the range (E15-019).
- **Deterministic?** Levels yes; zone merging and relevance are visual (OQ-07).

### Entry relativity (ER)
- **Definition.** How deep the current pullback is relative to the previous move, measured from the move's origin
  to its extreme (the extreme is extended until a ≥50% correction occurs). Buckets: 25% (not advised unless
  trendy), 50% (good), 75% (very good) (E1H-015). Range: trade at 75-100% extremes, avoid midpoint; trending
  range: sells above highs, buys at 50-75% (E15-015). Sells only in the upper half / buys in the lower half of
  a range (E15-012).
- **Deterministic?** Yes, given a swing definition (OQ-01).
- **Author statistic (hypothesis).** ~40% win rate at 25% vs higher at 75% (E1H-016).

### External / internal
- **Definition.** *External* = price is beyond a prior swing high/low (LTF, MTF, or the previous 15m candle's
  high/low). *Internal* = inside it. Counter-direction trades must be external; pro-direction trades may be
  internal (E15-011, E1H-012, E1H-017). External breaks are higher quality (E15-016).
- **Deterministic?** Yes.

---

## How price gets there

### Overextension (OE) / CBOE (candle behavior overextension)
- **Definition.** A candle opens and price moves in one direction for ~40-50% of that candle's duration **without
  a pullback**, where pullback = a 50% correction of the move so far (E1H-018). Durations:

  | Candle | OE duration | Evidence |
  |---|---|---|
  | Hourly | 20-30 min ("around 2 15-min intervals push in one direction") | E1H-018, E1H-002 |
  | 15m | ~7.5 min; minimum 4-5 min | E15-021, E1H-048 |
  | Daily | ~8-10 h, reversal around London hours 2-3 | E1H-043 |
  | Weekly | ~2 days, reversal Tue-Thu London | E1H-043 |

- **Quality.** Fast early, slowing near the halfway point, forming small structure that can be broken; minimal
  opposite wick at the open (E15-024, E1H-020). Invalid: sideways hour, wicks both ways, low-volume grind
  (E1H-019, E1H-026). Too fast with no structure (2 min) is also bad (E15-022).
- **Deterministic?** Duration and "no 50% pullback" yes. "Decisive/high volume" is visual (OQ-08).
- **Expansion.** "CBOE = Candle Behavior OverExtension" is inferred from the filename and speech; not yet seen
  spelled out on screen.

### HVCS (high-volume candle sequence)
- **Definition.** A directional run of large candles on the seconds/1m chart lasting **≥4 minutes**, pushing
  beyond the previous 15m candle high/low (LTF/MTF structure) (E1H-034, E1H-003). Phase 2: consecutive
  same-direction candles each respecting the prior candles' lows (up) / highs (down) ("trending on low
  timeframes"); the opposite is an **LVCS**, small overlapping candles (EP2-005, frame-confirmed).
- **Deterministic?** Duration, candle-sequence structure and "beyond prior 15m high/low" yes; "large candles"
  still needs a size threshold (OQ-08).

---

## Timing ("when")

### Candle behavior (CB) hour timing
- **Definition.** Minute within the hour at which the reversal shift/entry happens. Acceptable :22-:52; better
  :30-:45; best **~:37** (E1H-024). Earlier with an immediate push / high volume / opening near the target
  extreme; later with a delayed push / low volume (E1H-025). Continuations: first 0-15 min (E1H-026).
- **15m model.** Any of the four 15m candles; preferred in the candle's second half (after 7.5 min);
  within-hour anchors :07, :22, :37, :52 (E15-027, E15-030, E15-031).
- **Deterministic?** Yes.

### 15m candle behavior inside the hour ("37-minute alignment")
- **Definition.** Best hourly setups: after the hour extends in its first half, the third 15m candle (opens :30)
  opens and **continues against the trade**, taking the previous 15m high/low, then reverses near its own
  halfway point (~:37) (E1H-021). Exception: not needed if the previous 15m candle closed in the trade
  direction and the next one creates its opposite wick first (E1H-023). Counterexample: the :30 candle opens
  straight in the trade direction to form the shift, and it tends to flip against you (E1H-022).
- **Deterministic?** Yes.

---

## Entry models

### Shift (market-structure shift) / Type-3 shift (T3)
- **Definition.** A change in direction shown by highs and lows: in bullish structure, price takes out a high
  and then takes out a low (and vice versa) (E1H-030). Every entry requires one (E1H-029). The master slide
  calls the required pattern a "T3 shift" (E1H-002).
- **Deterministic?** Yes, given a swing definition (OQ-01).
- **Phase 1 definitions (Level 1):**
  - **Type 3** = price takes out a swing high, immediately reverses and takes out a swing low (sell), or low
    then high (buy). It must be decisive with high-volume candles, ideally closing beyond both swings. Entry
    on the pullback; stop behind the swing taken out; target the previous LTF opposite swing (EP1-007…009,
    EP1-012).
  - **CHoCH** = any break turning HH/HL into LH/LL, with no sweep required; every type 3 is a CHoCH, not
    vice versa (EP1-010).
  - Context: a shift against HTF direction without a big external break is just a pullback (EP1-011).

### Type 1 / Type 2 (candle-behavior entries)
- **Type 1** (bearish): candle closes bullish, next closes bearish, forming a level at the junction. The following
  candle wicks up into the level in its first half, then pushes bearish. Mirror for bullish. Best: wick takes the
  previous candle's high, big top wick, small bottom wick, decent body (EP1-002, EP1-003). HTF type 1s usually
  look like LTF type 3s (EP1-004).
- **Type 2**: a candle closes decisively beyond a level (wick breaks the previous low/high). The next candle retests
  the level with its wick in its first half, then continues. Candles may be the same colour; a barely-beyond
  close isn't valid (EP1-005, EP1-006).
- Types combine across timeframes, e.g. HTF type 1 + LTF type 3 (EP1-001, EP1-013). "Hourly type one" in the 15m
  course (E15-032) = this hourly-candle pattern.
- **Deterministic?** Yes on candle OHLC; the "decisive" quality filters are measurable proxies.

### Seconds shift
- **Definition.** A shift read on the 5s (preferred) or 15s chart; used when a shift unfolds over only a few
  minutes (E1H-029, E15-037). Entry on the break, no pullback (E1H-035).
- **Data implication.** Needs seconds bars or tick data (OQ-10).

### HILO (high-low entry)
- **Definition (Phase 2, frame-confirmed).** Within one or two 1m candles, price breaks a previous candle's
  **high** then a previous candle's **low** (bearish), or low then high (bullish): a tick/seconds-chart shift
  expressed with 1m candles (EP2-001). **Validity:** the candle before the entry-break candle must itself have
  broken its previous candle's opposite high/low, **or** a single candle breaks both; otherwise it's a pullback
  (EP2-002, EP2-003). Bigger breaks are better (EP2-004). Entry on the break; stop beyond the previous 1m candle's
  high/low (EP2-007). If the 1m sequence is low volume (LVCS), apply the same rule on 5m candles (EP2-005).
  In the CBR slide: "HILO beyond structure, entry on BOS of HILO" (E1H-003).
- **Deterministic?** Yes.

### Entry model A: HVCS → HILO
1. HVCS ≥4 min; 2. beyond previous LTF/MTF high/low; 3. after a 15m open, price wicks / pushes a bit more;
4. HILO beyond structure, enter on its break; 5. target 50% of previous LTF move. "Counter 1m trend or within
larger shift" (E1H-003, E1H-034). Used in high volume (E1H-032).

### Entry model B: 1m fractal shift
1m type-3 shift, then pullback to ~50% of the breaking impulse, then a reaction there (seconds shift or 1m HILO),
enter on the reaction (E1H-031). Used in lower volume / pro-trend continuations (E1H-032).

### 15m model entry
Type-3 shift on the 5s (preferred) or 15s chart (E15-037). Small shift in a fast market: breakout entry. Bigger
shift in a slow market: wait for a ~50% pullback (E15-038).

---

## Risk and exits

### Stop loss
- **Conservative** (default): beyond the external high/low of the extension. **Aggressive:** beyond the
  seconds-shift swing, only for the best setups (E1H-036). 15m: give breathing room; slippage on seconds shifts
  (E15-040). Buffer size unspecified (OQ-11).

### Take profit
- **Default:** 50% of the overextension (E1H-037, E15-039). **Adaptive:** >50% in pro trending ranges or very
  range-bound conditions; <50% (1:1, prior 1m high/low, ~25%) in trendy/high-volume conditions (E1H-038).
  Counter-direction 15m reversals: target the external high/low (E15-017; possible conflict, OQ-12).
  Journal (Level 2): "with 15-minute CBRs ... just target a one to one" (OQ-12).

### Trade management
- Exit near the halfway point of the next 15m candle if it opens and pushes your way without an opposite wick
  (E1H-033). Trail stop to the last opposite swing after each break in your favor (E1H-040). Time stop if
  price goes sideways about as long as the expected move (E1H-041). Scale in on a 1m type-3 after a
  seconds-shift entry (E1H-039). DXY diverging from gold → consider exit (E15-045).

---

## Correlation

### DXY inverse confluence (gold)
- **Definition.** DXY should be in a similar range condition, and its candle should extend **opposite** to gold's
  over the same candle; both expected to retrace toward 50%. DXY shift not required (E15-042, E15-043).
  Same-direction extension preceded a failed setup (E15-044). Author views `TVC:DXY` on the 5s chart (E1H-044).
- **Phase 2 rules (Level 1).** Entry inversion: gold type-3 shift mirrored by an opposite DXY type-3 shift
  (EP2-026). **No trade** when both move the same way with high volume (EP2-029). DXY is most useful in high-volume
  ranges and **ignored** when gold is extremely strong/trending or at all-time highs (EP2-029). Exit if DXY rejects
  against the trade (EP2-027). Relative strength: a big DXY move with little inverse gold movement = gold strong
  (EP2-028). Inverse, but "not always" (EP2-030).
- **Requirement level.** 15m course: "ideally" (OPTIONAL). Phase 2 and journal: **conditional veto** (OQ-13).
- **Deterministic?** Candle-direction comparison yes; "similar range" partly.

---

## Sessions
- **15m model on gold:** "anytime within the day… condition specific more than time specific" (E15-026).
- **Hourly model:** author trades Asia hours 1-3 (priority hour 2) and London hours 2-3; New York untested by
  him because of his timezone, not excluded by the method (E1H-042). Separate daily/weekly CBOE context around
  London (E1H-043).
