# 15-Minute CBR: Written Strategy Specification

**Model.** Candle Behavior Reversal on the 15-minute candle.
**Status.** Draft v0.1, extracted from Level 1 sources only. Not yet a machine spec (Phase 8).
**Sources.** `references/15min cbr/` (8 lessons). Evidence ids refer to
`research/evidence/strategy_evidence.jsonl`; terms in `glossary.md`; ambiguities in `open-questions.md`.

**Classification keys.** `OBJ` objective · `DISC` discretionary · `REQ` required · `OPT` optional/quality ·
`UNK` unknown · Confidence `H/M/L`.

---

## 0. Relationship to the hourly model

The 15m course states it is **the hourly CBR applied to a 15-minute candle, scaled by ¼** and assumes the hourly
course as a prerequisite (E15-001). Rules below are either:
- **INHERITED:** the hourly rule applies with durations scaled (reference to `1h-cbr-spec.md` rule id), or
- **15M-SPECIFIC:** stated in the 15m course.

Where the 15m course states a number itself, that number is used rather than a mechanical ¼ scaling.

Stated trade-offs vs hourly: more setups (author expects ~4-12 good setups/day vs 1-3), lower R:R, and it needs
better entry skill (E15-047).

**Core sequence** (E15-002): the 15m candle opens → extends for its first half → shift around the second half →
target back toward 50% of the extension.

---

## 1. Condition ("what")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-COND-001 | Evaluate a **low-timeframe range of ~1.5-2.5 hours** (~90+ min). | OBJ | REQ | H | E15-003, E15-004 |
| CBR15-COND-002 | Swing frequency in the range window: **3-6 swings = target**; 1-2 = range too big, sit out; 7+ = lower-timeframe range, adapt entry. | OBJ | REQ | H | E15-048, E15-006, E15-005 |
| CBR15-COND-003 | Condition by average pullback depth: **range 75-100%**, **trending range 50-75%**, **trend <50%**. | OBJ | REQ | M | E15-014, E15-013 (INHERITED CBR1H-COND-002) |
| CBR15-COND-004 | **Prior-setup check:** look back 1.5-2 h and count clean 15m CBRs that set up and played out. **3+ = good**; **zero in the last hour = bad, sit out**. | OBJ | REQ | H | E15-049, E15-008, E15-009 |
| CBR15-COND-005 | **Never take the first CBR in a range.** Target legs 3, 4, 5 into the range, not legs 1 or 2. | OBJ | REQ | H | E15-050, E15-007 (conflict on leg 2 → OQ-06) |
| CBR15-COND-006 | If recent setups are of a different model size (e.g. hourly CBRs happening, not 15m), it's the wrong condition for this model. | OBJ | REQ | M | E15-008 |
| CBR15-COND-007 | Unclear/confusing condition → don't trade. | DISC | REQ | H | E15-010 |
| CBR15-COND-008 | Direction is not a filter; it changes entry location (counter → external; pro → internal allowed). | OBJ | REQ | H | E15-011 |
| CBR15-COND-009 | Also workable in trending ranges and higher-volume trends via continuation setups (Model C). | OBJ | OPT | M | E15-035, E15-013 |

## 2. Location ("where")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-LOC-001 | **Range:** sells only in the upper half, buys only in the lower half; target CBRs at **75-100%** extremes; avoid the midpoint. | OBJ | REQ | H | E15-012, E15-015 |
| CBR15-LOC-002 | **Trending range:** sells only after taking out highs (counter); buys at **50-75%** pullbacks (pro). Mirror for bearish. | OBJ | REQ | M | E15-015 |
| CBR15-LOC-003 | **Default is external:** the 15m candle opens and over-extends to take out a high/low, then shifts back toward 50%. | OBJ | REQ | H | E15-034 |
| CBR15-LOC-004 | Internal-to-structure trades (taking only an internal high/low) are allowed but **lower quality**; mainly when a prior hourly close is in your favor. | OBJ | OPT | H | E15-016, E15-034 |
| CBR15-LOC-005 | **Buys below the 15m open, sells above it** (spoken the other way round; read as misspoken). | OBJ | REQ | L | E15-018 (→ OQ-14) |
| CBR15-LOC-006 | AOIs/levels are secondary to location in the range. Optional confluence: levels from prior hourly or 15m candle closes. | OBJ | OPT | H | E15-019, E15-020 |

## 3. Overextension ("how")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-OE-001 | Extension lasts **~4-5 minutes minimum** (~7.5 min = half the candle is the scaled ideal). | OBJ | REQ | H | E15-021, E1H-018, E1H-048 |
| CBR15-OE-002 | Too short (e.g. 2 min) is invalid: no structure forms to break. | OBJ | REQ | H | E15-022 |
| CBR15-OE-003 | **Profile:** fast/strong early, slowing near the 7.5-min mark, forming small structure that can be broken. Avoid both too-fast (no structure) and grinding extensions. | DISC | REQ | H | E15-024 |
| CBR15-OE-004 | Extension must be decisive and large enough that 50% of it is a worthwhile target. | DISC | REQ | H | E15-023 |
| CBR15-OE-005 | May be read as a high-volume trend on the seconds chart. | DISC | OPT | M | E15-025 |
| CBR15-OE-006 | No 50% pullback during the extension. | OBJ | REQ | M | INHERITED CBR1H-OE-002 |

## 4. Timing ("when")

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-TIME-001 | Any time of day on gold; condition dominates. | OBJ | REQ | H | E15-026 |
| CBR15-TIME-002 | Any of the four 15m candles in the hour may be traded; which one depends on condition and prior hourly close/structure. | OBJ | REQ | H | E15-030 |
| CBR15-TIME-003 | Preferred: shift/entry in the **second half** of the 15m candle (after 7.5 min). Within-hour anchors **:07, :22, :37, :52**. | OBJ | OPT | H | E15-027, E15-031 |
| CBR15-TIME-004 | :22 / :37 / :52 can align with an hourly CBR. :07 works best with prior hourly structure (hourly close in your favor). | OBJ | OPT | H | E15-031 |
| CBR15-TIME-005 | Caution: a shift made by a new 5m candle opening straight through structure may just be that 5m candle's wick before it flips. | DISC | OPT | M | E15-028 |
| CBR15-TIME-006 | Optional 5m confluence: 5m candle behavior aligned inside the 15m CBR (5m extension over prior 5m high/low; 5m close in trade direction). | OBJ | OPT | M | E15-029 |

## 5. Higher-timeframe alignment

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-HTF-001 | **Do not trade a 15m CBR against an active hourly CBR** (e.g. the hourly candle has made its bottom wick and is flipping bullish, so don't sell the 15m reversal). Align as much as possible. | OBJ | REQ | H | E15-036 |
| CBR15-HTF-002 | Can be combined with hourly CBRs, hourly type-1 structure, and range reversals; "none of it's mutually exclusive". | OBJ | OPT | H | E15-032, E15-036 |

## 6. Setup models

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-MODEL-A | **Hourly structure:** after an hourly shift, a bullish hourly close then a bearish hourly close forms a level. The next hour opens and pushes into that level (≈50% of the shift), and a 15m CBR forms within ~the first 7 minutes. | OBJ | OPT | M | E15-032 |
| CBR15-MODEL-B | **15m structure:** prior 15m close forms a level; the next 15m candle opens, wicks into it (ideally first half), then reverses. | OBJ | OPT | M | E15-033 |
| CBR15-MODEL-C | **Continuation:** 15m candle opens and extends against the prior move into ≥50% of it, reacts around its halfway point; seconds-shift entry; target beyond the prior swing extreme (not 50%). For trendy conditions. | OBJ | OPT | M | E15-035 |
| CBR15-MODEL-D | **Default reversal:** 15m candle opens, over-extends beyond a high/low, shifts back toward 50% (the core model). | OBJ | REQ* | H | E15-034, E15-002 |

\* The baseline implements Model D. A-C are separate, later variants.

## 7. Entry

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-ENTRY-001 | Trigger: **type-3 shift on the 5-second (preferred) or 15-second chart** (hourly model uses 1m). | OBJ | REQ | H | E15-037 |
| CBR15-ENTRY-002 | Small shift + fast market → breakout entry at the seconds swing break. Bigger shift + slower market → wait for a pullback into ~50% of the shift (fractal shift). | DISC | REQ | M | E15-038 |
| CBR15-ENTRY-003 | The shift must be clear and decisive; many traders get faked out on the 5s chart. | DISC | REQ | H | E15-037 area (seconds_entry_model 00:02:55-00:03:08) |

## 8. Stop loss

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-SL-001 | Stop beyond the extension extreme (below the low for buys). | OBJ | REQ | H | E15-039 |
| CBR15-SL-002 | **No tight stops** on seconds shifts: give breathing room for slippage. Objective is win rate/consistency, not maximum R:R. | DISC | REQ | H | E15-040 |

## 9. Take profit

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-TP-001 | Reversal target: **50% of the extension.** | OBJ | REQ | H | E15-039, E15-002 |
| CBR15-TP-002 | Pro-condition trades may target further (continuation beyond prior swing). | OBJ | OPT | M | E15-039, E15-035 |
| CBR15-TP-003 | Counter-direction reversal: target the external high/low, not the internal one. | OBJ | REQ | L | E15-017 (→ OQ-12) |

## 10. Management

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-MGMT-001 | If the shift came from a new 5m candle's open, take profit more aggressively. | DISC | OPT | M | E15-041 |
| CBR15-MGMT-002 | Gold long: if DXY pushes strongly in your favor while gold goes sideways, consider exiting (short: mirror). | DISC | OPT | M | E15-045 |
| CBR15-MGMT-003 | Hourly management rules (15m-candle exit, swing trailing, time stop) apply, scaled. | OBJ | OPT | M | INHERITED CBR1H-MGMT-001…003 |

## 11. DXY correlation

| Rule ID | Rule | Class | Req | Conf | Evidence |
|---|---|---|---|---|---|
| CBR15-DXY-001 | Ideally DXY is range-bound in a similar range to gold, and **extends in the opposite direction** over the same 15m candle. | OBJ | OPT | H | E15-042 |
| CBR15-DXY-002 | A DXY shift is not required; the gold shift is primary. DXY should show the inverted condition/structure/candle behavior. | OBJ | OPT | H | E15-043 |
| CBR15-DXY-003 | Gold and DXY extending the **same** direction preceded a fake-out loss (single illustrative example). | OBJ | OPT | M | E15-044 (veto question → OQ-13) |
| CBR15-DXY-004 | If counter to DXY's own direction, DXY should also be external to its structure. | OBJ | OPT | L | E15-046 |

---

## 12. No-trade conditions (collected)

- Range window shows 1-2 swings, or no prior 15m CBRs in the last hour (COND-002, COND-004)
- First or second leg into a range (COND-005)
- Midpoint of a range (LOC-001)
- Extension shorter than ~4 min or grinding (OE-001…003)
- Against an active hourly CBR (HTF-001)
- Unclear condition (COND-007)

## 13. Objective vs discretionary summary

| Area | Objective core | Discretionary residue |
|---|---|---|
| Condition | 1.5-2.5 h window, 3-6 swings, correction %, prior-setup count, leg number | "clean", "clear" |
| Location | range half, 75-100% / 50-75%, external/internal, 15m open side | level relevance |
| Extension | ≥4-5 min, no 50% pullback | "decisive", slowing profile |
| Timing | second half, :07/:22/:37/:52 | 5m-candle fake-out judgment |
| HTF | not against active hourly CBR | degree of alignment |
| Entry | 5s/15s type-3 shift | breakout vs pullback choice |
| Risk | stop beyond extreme, 50% target | stop buffer size |

## 14. Known gaps
- 5-second entry trigger needs seconds data (OQ-10).
- "Type 3 shift" defined only by usage; Academy course not available (OQ-09).
- Journal (Level 2) suggests a 1:1 target for 15m CBRs and a stricter DXY stance. Recorded, not adopted
  (OQ-12, OQ-13).
