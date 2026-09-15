# Phase 13: Recent FOREXCOM vs Dukascopy Feed Comparison

Run `CBR-RUN-013B-2` · generated 2026-09-15T22:27:59+00:00 · freeze commit `eb1a9f372d` · owner ruling D25.
Supporting evidence (CBR-PROT-013B §7.1). Days: 2026-09-09, 2026-09-10, 2026-09-11, 2026-09-14 (from 2026-09-09T01:00:00+00:00). Nothing here changed a parameter.

## Data validation (Dukascopy ticks for the D25-P2 days)

| Day | Ready | Tick rows | Vendor-gap minutes | STRUCTURE 1m rebuild = stored | Problems |
|---|---|---|---|---|---|
| 2026-09-09 | True | 284907 | 0 | True | none |
| 2026-09-10 | True | 558046 | 0 | True | none |
| 2026-09-11 | True | 498154 | 0 | True | none |
| 2026-09-14 | True | 476372 | 0 | True | none |

## Timestamp alignment and offsets

| Measure | Value |
|---|---|
| Comparison minutes (scheduled open) | 5340 |
| Matched minutes | 5340 (missing FOREXCOM 0, missing Dukascopy 0) |
| Best lag of 1m close returns (minutes) | 0 (zero lag confirmed: True) |
| Lag correlations | -1: -0.0105, -2: -0.0618, -3: -0.0416, 0: 0.9985, 1: -0.0168, 2: -0.0620, 3: -0.0371 |
| Median close offset δ (FOREXCOM − Dukascopy) | 0.0000 |
| Per-field median offsets | close 0.0000, high -0.0197, low 0.0165, open 0.0000 |
| Per-day median close offsets | 2026-09-09 0.0000, 2026-09-10 0.0017, 2026-09-11 0.0065, 2026-09-14 -0.0097 |
| HLC residual after δ: p50 / p75 / p90 / p95 / p99 | 0.0395 / 0.0750 / 0.1231 / 0.1600 / 0.2750 |
| Max HLC residual after δ | 4.3430 |

## Feed band (D25-P4)

τ = max($0.02, p95 0.1600) rounded up to $0.05 = **$0.20** · p99 residual 0.2750. Descriptive; used only in the materiality test.

## Agreement

| Concept | Agreement |
|---|---|
| Bar direction 1m | 96.9% (5175/5340; 95% CI 96.4-97.3%) |
| Bar direction 5m | 98.9% (1056/1068; 95% CI 98.0-99.4%) |
| Bar direction 15m | 98.9% (352/356; 95% CI 97.1-99.6%) |
| **LTF 1m swing membership** | 88.0% (249/283; 95% CI 83.7-91.3%) |
| **MTF 5m swing membership** | 100.0% (39/39; 95% CI 91.0-100.0%) |
| **15m previous-candle takes (pooled)** | 98.1% (689/702; 95% CI 96.9-98.9%) |
| 15m take of previous high | 98.0% (344/351; 95% CI 95.9-99.0%) |
| 15m take of previous low | 98.3% (345/351; 95% CI 96.3-99.2%) |
| **Hourly extension direction** | 96.3% (234/243; 95% CI 93.1-98.0%) |
| Extension extreme time ±1 min (same direction) | 92.7% (217/234; 95% CI 88.7-95.4%) |
| Extension duration ≥ 20 min flag | 94.2% (229/243; 95% CI 90.6-96.5%) |
| Extension no-pullback flag | 95.5% (232/243; 95% CI 92.1-97.5%) |
| Extension two-sided flag | 95.5% (232/243; 95% CI 92.1-97.5%) |
| **Condition class at the hour open** | 98.8% (80/81; 95% CI 93.3-99.8%) |
| Condition direction at the hour open | 98.8% (80/81; 95% CI 93.3-99.8%) |
| **1m type 3 events** | 92.0% (23/25; 95% CI 75.0-97.8%) |
| 1m HILO events | 85.8% (2396/2792; 95% CI 84.5-87.1%) |
| **Hour-level CBR1H setup membership (min 25/35/45)** | 99.6% (224/225; 95% CI 97.5-99.9%) |
| Full hour-level rule vector (same direction) | 92.1% (199/216; 95% CI 87.8-95.0%) |

Bold = criterion 9 core concept (D25 O-1). 5s structure: DATA_LIMITATION (no FOREXCOM 5s).

### Per-rule agreement (hour-level state, same extension direction)

| Rule | Agreement |
|---|---|
| M1H-6A-2-PREV-15M-BROKEN-BY-Q | 99.1% (214/216; 95% CI 96.7-99.7%) |
| M1H-6A-3-NEW-EXTREME-IN-Q | 99.1% (214/216; 95% CI 96.7-99.7%) |
| M1H-COND-01 | 98.6% (213/216; 95% CI 96.0-99.5%) |
| M1H-COND-02 | 98.6% (213/216; 95% CI 96.0-99.5%) |
| M1H-COND-03 | 98.6% (213/216; 95% CI 96.0-99.5%) |
| M1H-LOC-01 | 100.0% (102/102; 95% CI 96.4-100.0%) |
| M1H-LOC-02 | — (n = 0) |
| M1H-LOC-03 | — (n = 0) |
| M1H-OE-01 | 96.8% (209/216; 95% CI 93.5-98.4%) |
| M1H-OE-02 | 98.1% (212/216; 95% CI 95.3-99.3%) |
| M1H-OE-04a | 99.1% (214/216; 95% CI 96.7-99.7%) |
| M1H-OE-04b | 99.5% (215/216; 95% CI 97.4-99.9%) |

### Swing and event details

| Tier | Matched | FOREXCOM only | Dukascopy only | Median Δt (s) | Exact time share | Matched price |Δ − δ| median / p95 |
|---|---|---|---|---|---|---|
| ltf_1m | 249 | 20 | 14 | 0.0 | 0.973 | 0.0435 / 0.2150 |
| mtf_5m | 39 | 0 | 0 | 0.0 | 0.976 | 0.0450 / 0.2488 |
| type3_1m | 23 | 2 | 0 | 0.0 | 0.917 | — |
| hilo_1m | 2396 | 187 | 209 | 0.0 | 0.992 | — |

15m takes: 13 disagreements, 13 with |Dukascopy margin| ≤ τ. Hourly evaluations: 243 over 81 hours; hours excluded: {'by_reason': {'condition_window_before_study_start': 8}, 'count': 8}. Hour-level members: FOREXCOM 0, Dukascopy 1.
Exports vs 1m roll-ups: {'15m': {'bars': 356, 'identical': 356}, '5m': {'bars': 1068, 'identical': 1068}}.

## Criterion 9 (D25 O-1 reading, frozen before the study)

**MET** · FAIL evidence if any core rate < 0.50; concern if < 0.80.

| Core concept | Agreement |
|---|---|
| condition_at_hour_open | 98.8% (80/81; 95% CI 93.3-99.8%) |
| hour_extension_direction | 96.3% (234/243; 95% CI 93.1-98.0%) |
| hour_level_membership | 99.6% (224/225; 95% CI 97.5-99.9%) |
| ltf_swing_membership | 88.0% (249/283; 95% CI 83.7-91.3%) |
| mtf_swing_membership | 100.0% (39/39; 95% CI 91.0-100.0%) |
| takes_15m | 98.1% (689/702; 95% CI 96.9-98.9%) |
| type3_1m | 92.0% (23/25; 95% CI 75.0-97.8%) |
