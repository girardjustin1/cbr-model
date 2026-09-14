# 1-Hour CBR: Written Strategy Specification

**Model.** Candle Behavior Reversal on the hourly candle ("CBR", "30-minute reversal").
**Status.** Draft v0.1, extracted from Level 1 sources only. Not yet a machine spec (Phase 8).
**Sources.** `references/hourly cbr/` lesson videos; the three long recordings and the four trade-example videos
are still being processed and may add or amend rules.
**Evidence.** Rule citations are ids in `research/evidence/strategy_evidence.jsonl`; each record holds the video,
timestamp, verbatim quote and classification. Terms are defined in `glossary.md`; ambiguities in
`open-questions.md`.

**Classification keys.**
`OBJ` objective · `DISC` discretionary · `REQ` required · `OPT` optional/quality · `UNK` unknown ·
Confidence `H/M/L`.

---

## 1. Core idea (context, not a rule)

Price oscillates around fair value. A candle that opens and pushes hard in one direction for the first half of
its duration ("stretching the elastic band") tends to correct toward the middle of that push in the second half.
The model trades that small correction, timed by candle behavior, and doesn't try to call direction (E1H-001,
E1H-027). Stated goal: consistency and win rate over large R:R; realised ~1.5R on average (E1H-038).

**Three steps** (master slide, E1H-002):
1. Identify an MTF ranging condition.
2. Wait for an hour candle to open and overextend into the high or low of the range.
3. Wait for a type-3 shift at an AOI around the halfway point of the hour → enter; SL beyond external H/L;
   TP 50% of previous move; check correlation.

---

## 2. Rules

### 2.1 Condition ("what")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-COND-001 | Evaluate the past **5-12+ hours** of price action (MTF window). | OBJ | REQ | H | E1H-005, E1H-002 |
| CBR1H-COND-002 | Classify condition by average correction of previous moves: **range 75-100%+**, **trending range 50-75%**, **trend <50%**. | OBJ | REQ | H | E1H-007, E1H-008 (conflict E1H-009 → OQ-02) |
| CBR1H-COND-003 | Tradeable MTF models: **range**, **trending range** (pro or counter), **fractal shift / inverse fractal shift**. If none is identifiable, don't trade. | OBJ | REQ | H | E1H-010 |
| CBR1H-COND-004 | **No trade in a high-volume trend** (corrections <50%). If trading anyway, reduce the target. | OBJ | REQ | H | E1H-046, E1H-038 |
| CBR1H-COND-005 | Prefer high-volume (large-swing) ranges; avoid low-volume ranges. | DISC | OPT | H | E1H-013 |
| CBR1H-COND-006 | Condition check via prior setups: have hourly CBRs set up and played out over the past 5-10+ hours? No prior setups → probably the wrong condition. | OBJ | REQ | M | E15-008 (stated for both models) |
| CBR1H-COND-007 | Direction (HH/HL vs LH/LL) is **not a filter**; it determines entry location (see 2.2). | OBJ | REQ | H | E15-011, E1H-012 |
| CBR1H-COND-008 | Unclear / "weird" condition → no trade. | DISC | REQ | H | E1H-010, E15-010 |

### 2.2 Location ("where")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-LOC-001 | **Range:** the overextension must reach the **high or low** of the range (sells upper half / buys lower half; best at 75-100% extremes; avoid midpoint). | OBJ | REQ | H | E1H-002, E15-012, E15-015 |
| CBR1H-LOC-002 | **Pro trending-range** trade: pullback into structure, ideally at an AOI, at 50-75% of the previous impulse. | OBJ | REQ | H | E1H-012, E1H-015 |
| CBR1H-LOC-003 | **Counter trending-range** trade: price must be **beyond the external high/low** first. AOI not needed. | OBJ | REQ | H | E1H-012, E15-011 |
| CBR1H-LOC-004 | **IFS:** trade the correction back toward 50% of a large MTF impulse. **FS:** at ~50% of the impulse, trade a lower-timeframe shift in the impulse direction. | OBJ | REQ | M | E1H-011 (baseline scope → OQ-04) |
| CBR1H-LOC-005 | Entry relativity buckets: 25% not advised (unless trendy), 50% good, 75% very good. | OBJ | OPT | M | E1H-015, E1H-016 |
| CBR1H-LOC-006 | AOI = hourly/30m/4h candle opens & closes; only AOIs relevant to the condition (range extremes; pullback level in pro trending ranges). Secondary to location. | OBJ | OPT | H | E1H-014, E15-019 |
| CBR1H-LOC-007 | Best reversals take out the **previous 15m candle's high/low** (external) before shifting. | OBJ | OPT | H | E1H-017, E1H-021 |

### 2.3 Overextension ("how price gets there")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-OE-001 | The hour candle **opens and pushes in one direction for ~20-30 minutes** ("around two 15-minute intervals"). | OBJ | REQ | H | E1H-018, E1H-002 |
| CBR1H-OE-002 | **No pullback** during the extension, where pullback = a 50% correction of the move so far. | OBJ | REQ | H | E1H-018 |
| CBR1H-OE-003 | Extension goes **into the high or low of the range** (or beyond structure for counter trades). | OBJ | REQ | H | E1H-002, E1H-003 |
| CBR1H-OE-004 | **Invalid:** hour goes sideways ~30 min, creates wicks both ways, or grinds on low volume correcting ~50%. | OBJ | REQ | H | E1H-019, E1H-026 |
| CBR1H-OE-005 | Minimal opposite wick at the hour's open preferred (a wick delays the reversal). | OBJ | OPT | M | E1H-020 |
| CBR1H-OE-006 | Extension should be decisive / high volume. | DISC | REQ | H | E1H-019 (→ OQ-08) |

### 2.4 Timing ("when")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-TIME-001 | Reversal shift/entry **between :22 and :52** of the hour; better **:30-:45**; best **~:37**. | OBJ | REQ | H | E1H-024, E1H-001, E1H-002 ("T3 shift 20-45m") |
| CBR1H-TIME-002 | Earlier (~:22) with an immediate push / high volume / opening near the target extreme; later (:37-:52) with a delayed push / low volume / farther away. | DISC | OPT | H | E1H-025 |
| CBR1H-TIME-003 | **15m alignment:** the third 15m candle (opens :30) opens and **continues against the trade**, taking the previous 15m high/low, then reverses near its halfway point (~:37). | OBJ | OPT | H | E1H-021 |
| CBR1H-TIME-004 | **Avoid:** the :30 15m candle opening straight in the trade direction to create the shift (tends to flip against you). | OBJ | REQ | M | E1H-022 |
| CBR1H-TIME-005 | Exception to TIME-003: prior 15m candle closed in the trade direction and the next 15m candle creates its opposite wick first. | OBJ | OPT | M | E1H-023 |
| CBR1H-TIME-006 | Continuations are timed differently: first 0-15 min of the hour after the opposite wick. | OBJ | OPT | H | E1H-026 |

### 2.5 Entry models

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-ENTRY-001 | **Every entry requires a market-structure shift** (type-3: take a high then a low, or the reverse). | OBJ | REQ | H | E1H-029, E1H-030, E1H-002 |
| CBR1H-ENTRY-002 | **Model A (HVCS→HILO):** (1) HVCS ≥4 min; (2) beyond previous LTF/MTF high/low (previous 15m high/low); (3) after a 15m open, price wicks / pushes a bit more; (4) HILO beyond structure, **enter on its break**; (5) target 50% of previous LTF move. Counter to the 1m trend or within a larger shift. | OBJ | REQ* | H | E1H-003, E1H-034, E1H-035 |
| CBR1H-ENTRY-003 | **Model B (1m fractal shift):** 1m type-3 shift → pullback to ~50% of the breaking impulse → reaction there (seconds shift or 1m HILO) → enter. | OBJ | REQ* | H | E1H-031 |
| CBR1H-ENTRY-004 | Model selection: high volume → Model A (≈:22-:37); lower volume / pro-trend continuation → Model B (≈:30-:52). | DISC | REQ | H | E1H-032 |
| CBR1H-ENTRY-005 | Seconds-shift entries are taken on the break, without waiting for a pullback. | OBJ | REQ | H | E1H-035 |

\* One of Model A or Model B is required.

### 2.6 Stop loss

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-SL-001 | **Conservative (default):** beyond the external high/low of the extension. | OBJ | REQ | H | E1H-036, E1H-002 |
| CBR1H-SL-002 | **Aggressive:** beyond the seconds-shift swing inside the fractal shift, only for the highest-quality setups. | DISC | OPT | H | E1H-036 |
| CBR1H-SL-003 | Buffer size unspecified. | n/a | UNK | n/a | OQ-11 |

### 2.7 Take profit

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-TP-001 | **Default: 50% of the overextension** (extension extreme to extension origin). | OBJ | REQ | H | E1H-037, E1H-002 |
| CBR1H-TP-002 | Adaptive: >50% in pro trending ranges or very range-bound conditions; <50% (1:1, previous 1m high/low, ~25%) when the MTF condition is trendy/high volume. | DISC | OPT | H | E1H-038 |

### 2.8 Trade management

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-MGMT-001 | Exit near the halfway point of the next 15m candle if it opens and pushes your way for its first half **without an opposite wick**. | OBJ | OPT | H | E1H-033 |
| CBR1H-MGMT-002 | Trail the stop to the most recent opposite swing after each break of structure in your favor. | OBJ | OPT | H | E1H-040 |
| CBR1H-MGMT-003 | Exit if price goes sideways for about the expected duration of the move. | DISC | OPT | M | E1H-041 |
| CBR1H-MGMT-004 | Scale in when a 1m type-3 forms after a seconds-shift entry and the new 15m candle creates its wick. | DISC | OPT | H | E1H-039 |
| CBR1H-MGMT-005 | "Every exit is an entry": exit when candle behavior turns opposite to what the entry required. | DISC | OPT | H | E1H-033 area |

### 2.9 Correlation

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-CORR-001 | Check that the correlated instrument supports the trade; drop to its seconds chart and wait for its shift for timing (UJ: DXY/yen; gold: DXY inverse). | DISC | OPT | M | E1H-044, E15-042 |

### 2.10 Sessions and higher timeframe

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR1H-SESS-001 | Author trades Asia hours 1-3 (priority hour 2) and London hours 2-3. NY untested by him, not excluded. | OBJ | UNK | H | E1H-042 (→ OQ-16) |
| CBR1H-HTF-001 | Daily CBOE context: Tokyo trending one way → reversals around London hours 2-3; weekly analogue Tue-Thu (esp. Wednesday). Separate higher-timeframe context. | OBJ | OPT | M | E1H-043 (→ OQ-15) |
| CBR1H-HTF-002 | Keep the higher timeframe in mind: a range can sit at an overextended HTF location. | DISC | OPT | M | E1H-005 area (defining_mtf_ranges 00:05:52) |
| CBR1H-HTF-003 | For pro-direction trades, wait for LTF structure to realign with MTF structure (MS Align). | OBJ | OPT | M | E1H-045 |

---

## 3. No-trade conditions (collected)

- High-volume trend correcting <50% of previous moves (CBR1H-COND-004)
- No identifiable MTF model / confusing condition (CBR1H-COND-003, -008)
- No overextension: sideways hour, two-sided wicks, low-volume grind (CBR1H-OE-004)
- Counter trending-range trade that isn't beyond external structure (CBR1H-LOC-003)
- Shift created by the :30 15m candle opening in the trade direction (CBR1H-TIME-004)
- No market-structure shift (CBR1H-ENTRY-001)
- Reversal attempted outside :22-:52 (CBR1H-TIME-001)

---

## 4. Objective vs discretionary summary

| Area | Objective core | Discretionary residue |
|---|---|---|
| Condition | window length, correction-% classification, model type | "volume" of range, "clear" vs "weird" |
| Location | range half, external/internal, entry relativity % | AOI relevance, zone merging |
| Overextension | 20-30 min duration, no 50% pullback | "decisive / high volume" |
| Timing | minute-of-hour windows, 15m candle sequence | early vs late adjustment |
| Entry | type-3 shift, HVCS ≥4 min, break entry | model A vs B choice |
| Risk | conservative stop, 50% target | aggressive stop, adaptive target |
| Management | 15m-candle exit, swing trailing | time stop, scaling |

The objective core is large enough for a deterministic baseline. Each discretionary element becomes a recorded
`discretionary_proxy` feature rather than a hidden rule.

---

## 5. Known gaps
- Shift types 1/2 and the precise HILO / HVCS definitions come from an Academy course not in the reference set
  (OQ-09).
- Four trade-example videos and three long recordings are still being processed.
- The author's Notion journal of CBR trades would provide reference setups (OQ-20).
