# OQ-48 — independent Level-1 HVCS examples

**Ruling:** D33 §3-6 · **Status:** EVIDENCE MEASUREMENT ONLY. No engine, candidate or parity case was run; geometry is measured from stored Dukascopy 1-minute STRUCTURE bars. No outcome, fill or P&L was read. Neither example is CX-LT1-1, CX-TE1-1 or CX-LT3-2.

**Feed caveat.** The lesson charts are FOREX.com; the measurements below are Dukascopy. A marginal one-tick difference could move a single structural violation, which is why the tables report the violation positions rather than only a count.

## Reading comparison across the independent examples

| Reading | HX-1 | HX-2 | verdict |
|---|---|---|---|
| H-A | 1 | 1 | INCONSISTENT |
| H-B | 2 | 2 | INCONSISTENT |
| H-C | 1.0 | 1.0 | INCONSISTENT |
| H-D | 1 | 1 | INCONSISTENT |
| H-E | 2 | 2 | INCONSISTENT |
| H-F | 1 | 3 | INCONSISTENT |
| H-G | 9 | 10 | CONSISTENT |
| H-H | 9 | 10 | CONSISTENT |

## HX-1 — V1H-seconds_shift_1m_hilo_hvcs @ 00:02:06-00:02:19

> i want this sort of high volume uh candle sequence so you see we're respecting all the all the highs we're just you know consistently moving bearish … and then we have a shift, take out a low into taking out a high

XAUUSD · chart date Thu 23 Oct '25, GMT+11 · extension DOWN · trade BUY · Tom presents it as VALID.

| Field | Value |
|---|---|
| Visible sequence (UTC) | 2025-10-23 05:18:00+00:00 → 2025-10-23 05:26:00+00:00 |
| Visible 1m candles | 9 |
| First qualifying candle (PC3 run) | 05:26 |
| Extension-extreme candle | 05:26 |
| 5s / HILO shift | 05:27 (APPROXIMATE, read from the frame) |
| Type-3 arm time | UNKNOWN (determining it would require running a candidate engine, which is not authorized) |
| Type-3 sweep time | UNKNOWN (same reason) |
| Entry time | UNKNOWN (no entry price or time is stated in the lesson) |
| Elapsed duration of the visible sequence | 9 min |
| Structural violations inside it | 1 |
| Indecision bars | 0 |
| Opposing-close bars | 3 |
| Previous 15m window | 2025-10-23 05:00:00+00:00 → 2025-10-23 05:15:00+00:00 |
| Previous 15m reference | 4088.64 |
| Q takes it at | 05:20 |

| Time | O | H | L | C | Respects | Progresses |
|---|---|---|---|---|---|---|
| 05:18 | 4091.07 | 4091.54 | 4089.65 | 4089.75 | yes | yes |
| 05:19 | 4089.77 | 4090.49 | 4088.95 | 4089.08 | yes | yes |
| 05:20 | 4089.13 | 4089.36 | 4086.71 | 4087.00 | yes | yes |
| 05:21 | 4087.00 | 4088.21 | 4085.95 | 4086.81 | yes | yes |
| 05:22 | 4086.85 | 4087.03 | 4084.80 | 4085.38 | yes | yes |
| 05:23 | 4085.37 | 4086.57 | 4084.29 | 4085.45 | yes | **no** |
| 05:24 | 4085.45 | 4086.21 | 4085.32 | 4085.82 | yes | **no** |
| 05:25 | 4085.81 | 4086.91 | 4084.65 | 4086.57 | **no** | **no** |
| 05:26 | 4086.53 | 4086.57 | 4084.05 | 4084.83 | yes | yes |

| Reading | Value | ≥ 4 |
|---|---|---|
| H-A | 1 | **no** |
| H-B | 2 | **no** |
| H-C | 1.0 | **no** |
| H-D | 1 | **no** |
| H-E | 2 | **no** |
| H-F | 1 | **no** |
| H-G | 9 | yes |
| H-H | 9 | yes |

## HX-2 — V1H-candle_behavior_extension @ 00:03:38-00:03:47

> around the halfway point of this of this 15 minute candle you have the high volume counter sequence into a high low entry this would be like a second shift

XAUUSD · chart date Wed 29 Oct '25, GMT+11 · extension DOWN · trade BUY · Tom presents it as VALID.

| Field | Value |
|---|---|
| Visible sequence (UTC) | 2025-10-29 02:29:00+00:00 → 2025-10-29 02:36:00+00:00 |
| Visible 1m candles | 8 |
| First qualifying candle (PC3 run) | 02:36 |
| Extension-extreme candle | 02:36 |
| 5s / HILO shift | 02:37 (APPROXIMATE, read from the frame) |
| Type-3 arm time | UNKNOWN (determining it would require running a candidate engine, which is not authorized) |
| Type-3 sweep time | UNKNOWN (same reason) |
| Entry time | UNKNOWN (no entry price or time is stated in the lesson) |
| Elapsed duration of the visible sequence | 8 min |
| Structural violations inside it | 1 |
| Indecision bars | 0 |
| Opposing-close bars | 2 |
| Previous 15m window | 2025-10-29 02:15:00+00:00 → 2025-10-29 02:30:00+00:00 |
| Previous 15m reference | 3962.30 |
| Q takes it at | 02:30 |

| Time | O | H | L | C | Respects | Progresses |
|---|---|---|---|---|---|---|
| 02:29 | 3965.24 | 3965.24 | 3963.27 | 3963.57 | yes | yes |
| 02:30 | 3963.59 | 3964.90 | 3962.16 | 3962.98 | yes | yes |
| 02:31 | 3963.03 | 3963.39 | 3959.44 | 3960.20 | yes | yes |
| 02:32 | 3960.20 | 3961.34 | 3954.41 | 3957.14 | yes | yes |
| 02:33 | 3957.24 | 3958.12 | 3954.97 | 3955.50 | yes | yes |
| 02:34 | 3955.51 | 3955.76 | 3952.03 | 3955.75 | yes | **no** |
| 02:35 | 3955.78 | 3956.01 | 3946.97 | 3947.93 | **no** | yes |
| 02:36 | 3947.93 | 3950.26 | 3944.07 | 3948.15 | yes | **no** |

| Reading | Value | ≥ 4 |
|---|---|---|
| H-A | 1 | **no** |
| H-B | 2 | **no** |
| H-C | 1.0 | **no** |
| H-D | 1 | **no** |
| H-E | 2 | **no** |
| H-F | 3 | **no** |
| H-G | 10 | yes |
| H-H | 10 | yes |
