# CBR Rule Matrix: 15m vs 1h

One row per rule concept, both models side by side. Cells give the model's parameter or rule id; `n/s` = not
stated for that model; `inh` = inherited from the hourly model by the 15m course's "same thing, ¼ the
time" principle (E15-001). Full wording and evidence: `15min-cbr-spec.md`, `1h-cbr-spec.md`.

**Req:** REQ required · OPT optional/quality · UNK unknown. **Quant:** Y quantifiable now · P quantifiable once
an open question is settled · N visual/discretionary. **Baseline V1:** in / out / diag (recorded as a diagnostic
feature, not a filter).

## Condition (what)

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| Condition window | 1.5-2.5 h (CBR15-COND-001) | 5-12+ h (CBR1H-COND-001) | REQ | Y | H | in | OQ-03 |
| Range / trending range / trend by correction % | 75-100 / 50-75 / <50 (CBR15-COND-003) | same (CBR1H-COND-002) | REQ | P | H | in | OQ-01, OQ-02 |
| No trade in trend (<50%) | inh | CBR1H-COND-004 | REQ | P | H | in | OQ-02 |
| Swing count 3-6 in window | CBR15-COND-002 | n/s | REQ | P | H | in (15m) | OQ-01 |
| Prior same-model setups in lookback | 3+ good, 0 in last hour = no trade (CBR15-COND-004) | "previous hourly CBRs" (CBR1H-COND-006) | REQ | P | H/M | in | OQ-05 |
| Not the first CBR / legs 3-5 | CBR15-COND-005 | inh (stated generally, E15-007) | REQ | P | H | in | OQ-06 |
| MTF model types (range, TR, FS/IFS) | Model A-D (CBR15-MODEL-*) | CBR1H-COND-003 | REQ | P (FS/IFS: N) | H | range + TR in; FS/IFS out | OQ-04 |
| Range "volume" preference | n/s | CBR1H-COND-005 | OPT | N | H | diag | OQ-08 |
| Unclear condition → skip | CBR15-COND-007 | CBR1H-COND-008 | REQ | N | H | diag | none |

## Location (where)

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| Range half (sell upper / buy lower) | CBR15-LOC-001 | CBR1H-LOC-001 | REQ | P | H | in | OQ-01 |
| Range extreme 75-100% | CBR15-LOC-001 | CBR1H-LOC-001 | REQ | P | H | in | OQ-01 |
| Trending range: counter must be external | CBR15-LOC-002 | CBR1H-LOC-003 | REQ | Y | H | in | none |
| Trending range: pro at 50-75% pullback | CBR15-LOC-002 | CBR1H-LOC-002 | REQ | P | M/H | in | OQ-01 |
| External break of prior high/low | default (CBR15-LOC-003) | quality (CBR1H-LOC-007) | REQ / OPT | Y | H | in (15m), diag (1h) | none |
| Entry relativity 25/50/75 | via LOC-001/002 | CBR1H-LOC-005 | OPT | Y | M | diag | none |
| AOI (candle open/close levels) | CBR15-LOC-006 | CBR1H-LOC-006 | OPT | P | H | diag | OQ-07 |
| Side of 15m open | CBR15-LOC-005 | n/s | REQ | Y | L | in | OQ-14 |

## Overextension (how)

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| OE duration | ≥4-5 min, ideal ~7.5 (CBR15-OE-001) | 20-30 min (CBR1H-OE-001) | REQ | Y | H | in | none |
| No 50% pullback during OE | inh (CBR15-OE-006) | CBR1H-OE-002 | REQ | Y | H | in | none |
| OE into range high/low | CBR15-LOC-003 | CBR1H-OE-003 | REQ | P | H | in | OQ-01 |
| Invalid: sideways / two-sided wicks / grind | CBR15-OE-002/003 | CBR1H-OE-004 | REQ | P | H | in (sideways, two-sided wick); diag (grind) | OQ-08 |
| Decisive / high volume | CBR15-OE-004 | CBR1H-OE-006 | REQ | N | H | diag | OQ-08 |
| Minimal opposite wick at open | n/s | CBR1H-OE-005 | OPT | Y | M | diag | none |

## Timing (when)

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| Shift window within candle | second half (>7.5 min) (CBR15-TIME-003) | :22-:52, best :30-:45, ~:37 (CBR1H-TIME-001) | REQ (1h) / OPT (15m) | Y | H | in | none |
| Within-hour anchors | :07 :22 :37 :52 (CBR15-TIME-003) | :37 (:52) | OPT | Y | H | diag | none |
| 15m candle continues against, takes prior 15m H/L, then reverses | n/s (5m analogue CBR15-TIME-006) | CBR1H-TIME-003 | OPT | Y | H | diag | none |
| Avoid shift made by a new sub-candle opening in trade direction | 5m candle (CBR15-TIME-005) | :30 15m candle (CBR1H-TIME-004) | OPT / REQ | Y | M | in (1h), diag (15m) | none |
| Session | anytime (CBR15-TIME-001) | author: Asia h1-3, London h2-3 (CBR1H-SESS-001) | UNK | Y | H | no filter; segment | OQ-16 |

## Higher-timeframe alignment

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| Not against active higher CBR | vs hourly CBR (CBR15-HTF-001) | n/s | REQ | P | H | in (15m) | OQ-01 |
| MS alignment for pro trades | inh | CBR1H-HTF-003 | OPT | P | M | diag | OQ-01 |
| Daily CBOE / London context | n/s | CBR1H-HTF-001 | OPT | Y | M | diag | OQ-15 |

## Entry

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| Structure shift required (type 3) | 5s/15s chart (CBR15-ENTRY-001) | 1m or seconds (CBR1H-ENTRY-001) | REQ | P | H | in | OQ-01, OQ-09, OQ-10 |
| HVCS ≥4 min → HILO, break entry | inh via seconds shift | Model A (CBR1H-ENTRY-002) | REQ* | P | H | in | OQ-09, OQ-10 |
| 1m fractal shift → 50% pullback → reaction | pullback variant (CBR15-ENTRY-002) | Model B (CBR1H-ENTRY-003) | REQ* | P | H | in | OQ-09 |
| Model choice by volume | breakout vs pullback (CBR15-ENTRY-002) | CBR1H-ENTRY-004 | REQ | N | H | both models run separately | OQ-08 |

## Stop / target / management

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| Stop beyond external extreme | CBR15-SL-001 | CBR1H-SL-001 | REQ | Y | H | in | OQ-11 |
| Aggressive stop (inside shift) | n/s | CBR1H-SL-002 | OPT | Y | H | out (ablation) | none |
| Stop buffer | "breathing room" (CBR15-SL-002) | n/s | REQ | P | H | parameter | OQ-11 |
| Target 50% of extension | CBR15-TP-001 | CBR1H-TP-001 | REQ | Y | H | in | OQ-12 |
| Adaptive target by condition | CBR15-TP-002 | CBR1H-TP-002 | OPT | P | H | out (ablation) | OQ-12 |
| Counter reversal → external high/low target | CBR15-TP-003 | n/s | REQ | Y | L | out (ablation) | OQ-12 |
| Exit on next 15m candle pushing w/o wick | inh | CBR1H-MGMT-001 | OPT | Y | H | out (ablation) | none |
| Trail to opposite swing | inh | CBR1H-MGMT-002 | OPT | P | H | out (ablation) | OQ-01 |
| Time stop (sideways) | inh | CBR1H-MGMT-003 | OPT | P | M | out (ablation) | none |
| Scale-in | n/s | CBR1H-MGMT-004 | OPT | P | H | out | none |

## DXY confluence

| Concept | 15m | 1h | Req | Quant | Conf | Baseline V1 | Open Q |
|---|---|---|---|---|---|---|---|
| DXY extends opposite over same candle | CBR15-DXY-001 | CBR1H-CORR-001 (general) | OPT | Y | H | out (Phase 18 ablation) | OQ-13 |
| DXY shift not required | CBR15-DXY-002 | n/s | OPT | Y | H | n/a | none |
| Same-direction DXY = warning / veto | CBR15-DXY-003 | n/s | OPT | Y | M | out (ablation) | OQ-13 |
| DXY diverging → exit | CBR15-MGMT-002 | n/s | OPT | P | M | out (ablation) | none |

\* One of the entry models is required per trade.

## Reading the matrix

- **Baseline V1 = every `in` row.** Only canonical rules, fixed at their stated values. Where a value is unstated,
  it's a declared `ASSUMPTION` from the ambiguity register, not an optimized number.
- **`diag` rows** are computed and stored per signal (the signal ledger) so later phases can test whether they
  add information, without being hidden filters.
- **`out (ablation)` rows** are canonical but optional. Each is tested alone against the baseline in Phase 18.
