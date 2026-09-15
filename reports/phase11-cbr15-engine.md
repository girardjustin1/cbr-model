# Phase 11: CBR15 Reference Engine Run (course-example windows)

Generated 2026-09-15T04:40:38.733549+00:00 by `src/cbr/engine/phase11_run.py`. Implementation parity use only: no fills, trade outcomes or P&L. The course examples are **CBR1H** trades; CBR15 output here is informational.

## CX-LT1-1

Tom (CBR1H): {'direction': 'BUY', 'entry_utc': '2025-10-21 01:39', 'entry': 4340.13, 'stop': 4332.96, 'target': 4351.59, 'model': 'CBR1H'}. Candles 2025-10-21 01:00 → 2025-10-21 02:00 UTC, warm-up from 2025-10-20 18:00.
Deterministic: True · causality (truncation at 3 cut times): True · spec hash `acb1ae2df03f`

| Candle | Condition | Legs | c_med | Candle-level failures | Candidates |
|---|---|---|---|---|---|
| 01:00 | TRENDING_RANGE | 5 | 0.741 | — | 1 |
| 01:15 | RANGE | 5 | 1.084 | — | 2 |
| 01:30 | RANGE | 5 | 1.084 | — | 2 |
| 01:45 | RANGE | 6 | 1.177 | — | 3 |

| Decision (UTC) | Dir | Event | Failed rules | Not evaluated | OE dur | OE extreme | 5s sweep bar | Sweep beyond OE | Trigger | Target | Prior 60m | Cancel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:07:00 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-OE-02, M15-OE-03a | M15-HTF-01 | 6 | 4361.625 | 4361.625 | False | 4366.815 | 4365.176 | 0 | OE_PULLBACK |
| 01:24:20 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-OE-01, M15-OE-02, M15-OE-03b | M15-HTF-01 | 2 | 4354.275 | 4355.375 | False | 4358.455 | 4356.642 | 0 | OE_PULLBACK |
| 01:28:55 | BUY | REJECTED | M15-COND-03, M15-OE-02 | M15-HTF-01 | 11 | 4349.470 | 4350.090 | False | 4352.610 | 4354.240 | 0 | OE_PULLBACK |
| 01:35:40 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-OE-01 | M15-HTF-01 | 0 | 4341.620 | 4344.178 | False | 4347.430 | 4346.004 | 0 | OE_PULLBACK |
| 01:38:40 | BUY | REJECTED | M15-COND-03, M15-OE-02 | M15-HTF-01 | 7 | 4335.212 | 4334.782 | True | 4340.185 | 4342.800 | 0 | OE_PULLBACK |
| 01:49:00 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-LOC-01, M15-LOC-04, M15-OE-01, M15-OE-02, M15-OE-03a, M15-OE-03b | M15-HTF-01 | 3 | 4342.810 | 4342.810 | False | 4347.040 | 4344.512 | 0 | OE_PULLBACK |
| 01:56:10 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-LOC-04, M15-OE-02 | M15-HTF-01 | 5 | 4339.165 | 4344.870 | False | 4348.195 | 4342.690 | 0 | OE_PULLBACK |
| 01:58:05 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-LOC-04, M15-OE-02 | M15-HTF-01 | 5 | 4339.165 | 4344.100 | False | 4347.185 | 4342.690 | 0 | WINDOW_END |

Rule failure counts: [('M15-COND-03', 8), ('M15-OE-02', 7), ('IMPL-REWARD', 6), ('M15-OE-01', 3), ('M15-LOC-04', 3), ('M15-OE-03a', 2), ('M15-OE-03b', 2), ('M15-LOC-01', 1)]
ARMED signals: 0

## CX-TE1-1

Tom (CBR1H): {'direction': 'BUY', 'entry_utc': '2025-10-24 04:37', 'model': 'CBR1H'}. Candles 2025-10-24 04:00 → 2025-10-24 05:00 UTC, warm-up from 2025-10-23 20:00.
Deterministic: True · causality (truncation at 3 cut times): True · spec hash `acb1ae2df03f`

| Candle | Condition | Legs | c_med | Candle-level failures | Candidates |
|---|---|---|---|---|---|
| 04:00 | RANGE | 4 | 1.242 | — | 3 |
| 04:15 | RANGE | 5 | 1.250 | — | 6 |
| 04:30 | RANGE | 4 | 1.242 | — | 2 |
| 04:45 | RANGE | 3 | 1.065 | — | 3 |

| Decision (UTC) | Dir | Event | Failed rules | Not evaluated | OE dur | OE extreme | 5s sweep bar | Sweep beyond OE | Trigger | Target | Prior 60m | Cancel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 04:07:20 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-LOC-01, M15-LOC-04, M15-OE-02 | M15-HTF-01 | 4 | 4116.390 | 4116.300 | True | 4119.453 | 4119.415 | 0 | OE_PULLBACK |
| 04:12:20 | BUY | REJECTED | M15-COND-03, M15-LOC-01, M15-OE-02 | M15-HTF-01 | 8 | 4115.960 | 4116.810 | False | 4119.191 | 4119.200 | 0 | OE_PULLBACK |
| 04:14:10 | BUY | REJECTED | M15-COND-03, M15-LOC-01, M15-OE-02 | M15-HTF-01 | 8 | 4115.960 | 4115.710 | True | 4117.314 | 4119.200 | 0 | WINDOW_END |
| 04:18:15 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-LOC-01, M15-OE-01, M15-OE-03b | M15-HTF-01 | 1 | 4114.145 | 4113.765 | True | 4115.530 | 4115.363 | 0 | T3_NEW_SWING |
| 04:19:20 | BUY | REJECTED | M15-COND-03, M15-LOC-01, M15-OE-01, M15-OE-03b | M15-HTF-01 | 3 | 4113.765 | 4112.230 | True | 4114.640 | 4115.172 | 0 | T3_TIMEOUT |
| 04:23:50 | BUY | REJECTED | M15-COND-03 | M15-HTF-01 | 6 | 4107.790 | 4107.720 | True | 4109.740 | 4112.185 | 0 | T3_NEW_SWING |
| 04:24:15 | BUY | REJECTED | M15-COND-03 | M15-HTF-01 | 8 | 4107.500 | 4107.440 | True | 4109.130 | 4112.040 | 0 | WINDOW_END |
| 04:25:05 | BUY | REJECTED | M15-COND-03 | M15-HTF-01 | 9 | 4105.234 | 4105.610 | False | 4109.270 | 4110.907 | 0 | WINDOW_END |
| 04:28:35 | BUY | REJECTED | M15-COND-03 | M15-HTF-01 | 9 | 4105.234 | 4107.265 | False | 4109.505 | 4110.907 | 0 | WINDOW_END |
| 04:33:30 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-OE-01, M15-OE-03b | M15-HTF-01 | 0 | 4103.755 | 4103.875 | False | 4106.565 | 4105.390 | 0 | OE_PULLBACK |
| 04:36:40 | BUY | REJECTED | IMPL-REWARD, M15-COND-03, M15-OE-02, M15-OE-03b | M15-HTF-01 | 4 | 4103.510 | 4103.290 | True | 4105.565 | 4105.267 | 0 | OE_PULLBACK |
| 04:47:40 | SELL | REJECTED | IMPL-REWARD, M15-COND-03, M15-LOC-01, M15-OE-01, M15-OE-02, M15-OE-03b | M15-HTF-01 | 1 | 4109.055 | 4109.075 | True | 4107.750 | 4107.887 | 0 | OE_PULLBACK |
| 04:53:50 | SELL | REJECTED | M15-COND-03, M15-LOC-01, M15-OE-02 | M15-HTF-01 | 4 | 4113.800 | 4113.415 | False | 4111.845 | 4110.260 | 0 | OE_PULLBACK |
| 04:58:25 | SELL | REJECTED | M15-COND-03, M15-LOC-01, M15-OE-02 | M15-HTF-01 | 4 | 4113.800 | 4112.880 | False | 4111.865 | 4110.260 | 0 | OE_PULLBACK |

Rule failure counts: [('M15-COND-03', 14), ('M15-LOC-01', 8), ('M15-OE-02', 7), ('IMPL-REWARD', 5), ('M15-OE-03b', 5), ('M15-OE-01', 4), ('M15-LOC-04', 1)]
ARMED signals: 0

## CX-LT3-2

Tom (CBR1H): {'direction': 'SELL', 'entry_utc': '2025-11-10 01:40', 'model': 'CBR1H'}. Candles 2025-11-10 01:00 → 2025-11-10 02:00 UTC, warm-up from 2025-11-07 12:00.
Deterministic: True · causality (truncation at 3 cut times): True · spec hash `acb1ae2df03f`

| Candle | Condition | Legs | c_med | Candle-level failures | Candidates |
|---|---|---|---|---|---|
| 01:00 | RANGE | 9 | 0.886 | M15-COND-02 | 2 |
| 01:15 | RANGE | 8 | 0.853 | M15-COND-02 | 2 |
| 01:30 | RANGE | 6 | 0.853 | — | 1 |
| 01:45 | TREND | 4 | 0.498 | M15-COND-01 | 4 |

| Decision (UTC) | Dir | Event | Failed rules | Not evaluated | OE dur | OE extreme | 5s sweep bar | Sweep beyond OE | Trigger | Target | Prior 60m | Cancel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:07:55 | SELL | REJECTED | IMPL-REWARD, M15-COND-02, M15-COND-03, M15-OE-01 | M15-HTF-01 | 0 | 4024.695 | 4022.575 | False | 4021.015 | 4022.560 | 0 | WINDOW_END |
| 01:10:30 | SELL | REJECTED | IMPL-REWARD, M15-COND-02, M15-COND-03, M15-OE-01 | M15-HTF-01 | 0 | 4024.695 | 4023.880 | False | 4020.445 | 4022.560 | 0 | OE_PULLBACK |
| 01:18:35 | SELL | REJECTED | IMPL-REWARD, M15-COND-02, M15-COND-03, M15-OE-01 | M15-HTF-01 | 1 | 4031.730 | 4031.825 | True | 4028.540 | 4029.485 | 0 | OE_PULLBACK |
| 01:26:05 | SELL | REJECTED | M15-COND-02, M15-COND-03, M15-OE-02 | M15-HTF-01 | 9 | 4047.145 | 4047.170 | True | 4043.965 | 4037.193 | 0 | OE_PULLBACK |
| 01:43:35 | SELL | REJECTED | IMPL-REWARD, M15-COND-03, M15-OE-02 | M15-HTF-01 | 7 | 4053.425 | 4052.740 | False | 4048.530 | 4050.645 | 0 | OE_PULLBACK |
| 01:50:00 | SELL | REJECTED | IMPL-REWARD, M15-COND-01, M15-COND-03, M15-LOC-04, M15-OE-02, M15-OE-03a, M15-OE-03b | M15-HTF-01 | 4 | 4052.840 | 4052.840 | False | 4050.960 | 4051.863 | 0 | T3_BREAK_BEFORE_WINDOW |
| 01:52:50 | BUY | REJECTED | IMPL-REWARD, M15-COND-01, M15-COND-03, M15-LOC-04, M15-OE-02, M15-OE-03a, M15-OE-03b | M15-HTF-01 | 6 | 4047.060 | 4047.030 | True | 4049.935 | 4048.972 | 0 | OE_PULLBACK |
| 01:54:55 | BUY | REJECTED | M15-COND-01, M15-COND-03, M15-OE-02 | M15-HTF-01 | 8 | 4043.776 | 4042.631 | True | 4046.150 | 4047.331 | 0 | OE_PULLBACK |
| 01:56:25 | BUY | REJECTED | M15-COND-01, M15-COND-03, M15-OE-02 | M15-HTF-01 | 10 | 4041.700 | 4041.477 | True | 4044.330 | 4046.293 | 0 | OE_PULLBACK |

Rule failure counts: [('M15-COND-03', 9), ('IMPL-REWARD', 6), ('M15-OE-02', 6), ('M15-COND-02', 4), ('M15-COND-01', 4), ('M15-OE-01', 3), ('M15-LOC-04', 2), ('M15-OE-03a', 2), ('M15-OE-03b', 2)]
ARMED signals: 0
