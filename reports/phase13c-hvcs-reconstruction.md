# Phase 13C — HVCS reconstruction and counting comparison

**Ruling:** D32 §4-7 · **Status:** DIAGNOSTIC ONLY. PC3 is unchanged and nothing here selects an interpretation. No trade outcomes were read.

## Counting comparison (D32 §6)

| Reading | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | passes ≥ 4 |
|---|---|---|---|---|
| **H-A** | 3 | 2 | 0 | 0/3 |
| **H-B** | 4 | 3 | 0 | 1/3 |
| **H-C** | 3.58 | 2.92 | 0.0 | 0/3 |
| **H-D** | 3 | 2 | 1 | 0/3 |
| **H-E** | 4 | 3 | 2 | 1/3 |
| **H-G** | 6 | 4 | 0 | 2/3 |
| **H-H** | 6 | 4 | 4 | 3/3 |
| **H-F** | 0 | 1 | 1 | 0/3 |

| Reading | Anchor | What it means |
|---|---|---|
| H-A | run ends at the extension-extreme bar 01:38 | PC3 as implemented; the first candle of the sequence is the reference and is not counted |
| H-B | same run as H-A | counts the first candle of the sequence as minute 1 |
| H-C | first H-A candle open → 5s shift 01:39:35 | elapsed wall-clock reading of 'push for at least four minutes' |
| H-D | run ends at the last 1m bar closed before the shift | 'HVCS runs directly into the shift' (D19-6) read as the anchor, not the extension extreme |
| H-E | same run as H-D | H-D with the first candle counted |
| H-G | run ends at the extension-extreme bar 01:38 | PC3 conformity with PC2's `hvcs.max_violations` = 1 restored; PC3's H-1 rewrite dropped that tolerance without D29 ruling on it |
| H-H | run ends at the last 1m bar closed before the shift | H-G anchored at the shift instead of the extension extreme |
| H-F | run ends at the last 1m bar closed before the entry 15m candle opens | master-slide order E1H-003: HVCS (4+ mins) and the take of the previous LTF/MTF extreme come BEFORE 'after 15m open, PA create wick/pushes a bit more' |

Anchors differ per case; the anchor column shows CX-LT1-1's. Full per-case anchors are in the JSON.

## CX-LT1-1

Extension DOWN · activation 2025-10-21 01:07:00+00:00 · extreme 2025-10-21 01:38:00+00:00 · 5s sweep 2025-10-21 01:35:30+00:00 · 5s shift 2025-10-21 01:39:35+00:00 · entry 15m candle opens 2025-10-21 01:30:00+00:00.
Previous 15m candle 2025-10-21 01:15:00+00:00 → 2025-10-21 01:30:00+00:00: high 4361.0735, low 4349.47.
PC3 measured 3.0 conforming minutes against a required 4 → rule state False.

| Time | O | H | L | C | Dir | New extreme | Respects (Tom's test) | Progresses | Counted by | Took prev 15m | Markers |
|---|---|---|---|---|---|---|---|---|---|---|
| 01:10 | 4363.94 | 4367.15 | 4362.92 | 4362.92 | down | yes | — | yes | — | — |  |
| 01:11 | 4362.94 | 4364.82 | 4362.47 | 4364.68 | up | yes | yes | no | — | — |  |
| 01:12 | 4364.67 | 4364.67 | 4361.24 | 4361.94 | down | yes | yes | yes | — | — |  |
| 01:13 | 4361.78 | 4362.19 | 4358.78 | 4358.86 | down | yes | yes | yes | — | — |  |
| 01:14 | 4358.81 | 4360.44 | 4358.62 | 4359.02 | up | yes | yes | no | — | — |  |
| 01:15 | 4359.01 | 4360.39 | 4357.18 | 4358.68 | down | yes | yes | yes | — | — |  |
| 01:16 | 4358.69 | 4359.61 | 4356.23 | 4356.41 | down | yes | yes | yes | — | — |  |
| 01:17 | 4356.46 | 4357.84 | 4354.27 | 4355.94 | down | yes | yes | yes | — | — |  |
| 01:18 | 4355.93 | 4357.93 | 4355.90 | 4357.78 | up | no | no | no | — | — |  |
| 01:19 | 4357.85 | 4359.64 | 4357.10 | 4359.28 | up | no | no | no | — | — |  |
| 01:20 | 4359.89 | 4361.00 | 4359.39 | 4360.76 | up | no | no | no | — | — |  |
| 01:21 | 4360.77 | 4361.07 | 4356.83 | 4356.91 | down | no | no | yes | — | — |  |
| 01:22 | 4356.88 | 4358.27 | 4355.40 | 4358.00 | up | no | yes | no | — | — |  |
| 01:23 | 4358.03 | 4358.44 | 4355.14 | 4356.01 | down | no | no | yes | — | — |  |
| 01:24 | 4356.01 | 4356.44 | 4350.89 | 4351.43 | down | yes | yes | yes | — | — |  |
| 01:25 | 4351.44 | 4352.31 | 4349.81 | 4350.72 | down | yes | yes | yes | — | — |  |
| 01:26 | 4350.55 | 4352.76 | 4349.47 | 4352.10 | up | yes | no | no | — | — |  |
| 01:27 | 4352.56 | 4352.96 | 4350.21 | 4350.45 | down | no | no | yes | — | — |  |
| 01:28 | 4350.60 | 4352.60 | 4349.52 | 4350.56 | down | no | yes | yes | — | — |  |
| 01:29 | 4350.58 | 4352.62 | 4349.74 | 4350.16 | down | no | no | yes | — | — |  |
| 01:30 | 4350.39 | 4350.57 | 4341.62 | 4344.38 | down | yes | yes | yes | — | yes | entry 15m candle opens |
| 01:31 | 4344.50 | 4347.74 | 4344.29 | 4346.01 | up | no | yes | no | — | yes |  |
| 01:32 | 4346.03 | 4348.10 | 4344.97 | 4346.87 | up | no | no | no | — | yes |  |
| 01:33 | 4346.89 | 4348.03 | 4344.44 | 4344.85 | down | no | yes | yes | H-G, H-H | yes |  |
| 01:34 | 4344.85 | 4346.56 | 4344.31 | 4346.22 | up | no | yes | no | H-G, H-H | yes |  |
| 01:35 | 4346.19 | 4347.42 | 4342.49 | 4343.20 | down | no | no | yes | H-G, H-H | yes | 5s sweep |
| 01:36 | 4343.10 | 4345.02 | 4341.39 | 4342.48 | down | yes | yes | yes | H-A, H-D, H-G, H-H | yes |  |
| 01:37 | 4342.49 | 4342.57 | 4335.21 | 4337.09 | down | yes | yes | yes | H-A, H-D, H-G, H-H | yes |  |
| 01:38 | 4337.09 | 4340.18 | 4332.95 | 4335.47 | down | yes | yes | yes | H-A, H-D, H-G, H-H | yes | extension extreme |
| 01:39 | 4335.44 | 4341.23 | 4335.44 | 4340.58 | up | no | no | no | — | yes | 5s shift / decision |

| Reading | Value | Anchor |
|---|---|---|
| H-A | 3 conforming 1m candles | run ends at the extension-extreme bar 01:38 |
| H-B | 4 1m candles, inclusive | same run as H-A |
| H-C | 3.58 elapsed minutes | first H-A candle open → 5s shift 01:39:35 |
| H-D | 3 conforming 1m candles | run ends at the last 1m bar closed before the shift (01:38) |
| H-E | 4 1m candles, inclusive | same run as H-D |
| H-G | 6 1m candles, ≤ 1 violation | run ends at the extension-extreme bar 01:38 |
| H-H | 6 1m candles, ≤ 1 violation | run ends at the last 1m bar closed before the shift (01:38) |
| H-F | 0 conforming 1m candles | run ends at the last 1m bar closed before the entry 15m candle opens (01:29) |

## CX-TE1-1

Extension DOWN · activation 2025-10-24 04:07:00+00:00 · extreme 2025-10-24 04:37:00+00:00 · 5s sweep 2025-10-24 04:33:20+00:00 · 5s shift 2025-10-24 04:38:55+00:00 · entry 15m candle opens 2025-10-24 04:30:00+00:00.
Previous 15m candle 2025-10-24 04:15:00+00:00 → 2025-10-24 04:30:00+00:00: high 4116.745, low 4105.2335.
PC3 measured 2.0 conforming minutes against a required 4 → rule state False.

| Time | O | H | L | C | Dir | New extreme | Respects (Tom's test) | Progresses | Counted by | Took prev 15m | Markers |
|---|---|---|---|---|---|---|---|---|---|---|
| 04:10 | 4117.27 | 4119.18 | 4117.20 | 4119.08 | up | yes | — | no | — | — |  |
| 04:11 | 4118.98 | 4118.98 | 4117.45 | 4117.48 | down | no | yes | yes | — | — |  |
| 04:12 | 4117.55 | 4117.55 | 4116.24 | 4117.17 | down | yes | yes | yes | — | — |  |
| 04:13 | 4117.16 | 4117.27 | 4116.29 | 4116.41 | down | no | yes | yes | — | — |  |
| 04:14 | 4116.38 | 4116.65 | 4115.71 | 4116.53 | up | yes | yes | no | — | — |  |
| 04:15 | 4116.58 | 4116.74 | 4114.80 | 4115.12 | down | yes | no | yes | — | — |  |
| 04:16 | 4115.09 | 4115.52 | 4114.15 | 4115.01 | down | yes | yes | yes | — | — |  |
| 04:17 | 4114.99 | 4115.02 | 4114.29 | 4114.88 | down | no | yes | yes | — | — |  |
| 04:18 | 4114.84 | 4114.84 | 4113.76 | 4114.33 | down | yes | yes | yes | — | — |  |
| 04:19 | 4114.38 | 4114.38 | 4111.78 | 4112.31 | down | yes | yes | yes | — | — |  |
| 04:20 | 4112.27 | 4112.27 | 4109.76 | 4109.87 | down | yes | yes | yes | — | — |  |
| 04:21 | 4109.90 | 4110.11 | 4107.79 | 4108.02 | down | yes | yes | yes | — | — |  |
| 04:22 | 4108.05 | 4109.73 | 4107.99 | 4108.91 | up | no | yes | no | — | — |  |
| 04:23 | 4108.89 | 4109.37 | 4107.50 | 4108.59 | down | yes | yes | yes | — | — |  |
| 04:24 | 4108.59 | 4109.26 | 4105.23 | 4106.34 | down | yes | yes | yes | — | — |  |
| 04:25 | 4106.36 | 4108.41 | 4105.52 | 4106.99 | up | no | yes | no | — | — |  |
| 04:26 | 4107.04 | 4109.27 | 4106.36 | 4108.84 | up | no | no | no | — | — |  |
| 04:27 | 4108.88 | 4109.10 | 4107.31 | 4109.06 | up | no | yes | no | — | — |  |
| 04:28 | 4109.08 | 4109.49 | 4106.17 | 4107.18 | down | no | no | yes | — | — |  |
| 04:29 | 4107.15 | 4107.51 | 4105.40 | 4106.99 | down | no | yes | yes | H-F | — |  |
| 04:30 | 4107.02 | 4107.72 | 4103.76 | 4104.07 | down | yes | no | yes | — | yes | entry 15m candle opens |
| 04:31 | 4104.07 | 4106.37 | 4103.78 | 4106.37 | up | no | yes | no | — | yes |  |
| 04:32 | 4106.37 | 4106.41 | 4104.19 | 4104.83 | down | no | no | yes | — | yes |  |
| 04:33 | 4104.67 | 4106.56 | 4103.62 | 4103.80 | down | yes | no | yes | — | yes | 5s sweep |
| 04:34 | 4103.77 | 4105.40 | 4103.51 | 4104.82 | up | yes | yes | no | H-G, H-H | yes |  |
| 04:35 | 4104.72 | 4105.56 | 4104.24 | 4105.12 | up | no | no | no | H-G, H-H | yes |  |
| 04:36 | 4105.11 | 4105.22 | 4103.11 | 4103.59 | down | yes | yes | yes | H-A, H-D, H-G, H-H | yes |  |
| 04:37 | 4103.59 | 4104.08 | 4102.88 | 4104.07 | up | yes | yes | no | H-A, H-D, H-G, H-H | yes | extension extreme |
| 04:38 | 4104.22 | 4105.69 | 4103.68 | 4105.39 | up | no | no | no | — | yes | 5s shift / decision |

| Reading | Value | Anchor |
|---|---|---|
| H-A | 2 conforming 1m candles | run ends at the extension-extreme bar 04:37 |
| H-B | 3 1m candles, inclusive | same run as H-A |
| H-C | 2.92 elapsed minutes | first H-A candle open → 5s shift 04:38:55 |
| H-D | 2 conforming 1m candles | run ends at the last 1m bar closed before the shift (04:37) |
| H-E | 3 1m candles, inclusive | same run as H-D |
| H-G | 4 1m candles, ≤ 1 violation | run ends at the extension-extreme bar 04:37 |
| H-H | 4 1m candles, ≤ 1 violation | run ends at the last 1m bar closed before the shift (04:37) |
| H-F | 1 conforming 1m candles | run ends at the last 1m bar closed before the entry 15m candle opens (04:29) |

## CX-LT3-2

Extension UP · activation 2025-11-10 01:10:00+00:00 · extreme 2025-11-10 01:37:00+00:00 · 5s sweep 2025-11-10 01:34:40+00:00 · 5s shift 2025-11-10 01:39:40+00:00 · entry 15m candle opens 2025-11-10 01:30:00+00:00.
Previous 15m candle 2025-11-10 01:15:00+00:00 → 2025-11-10 01:30:00+00:00: high 4052.0114999999996, low 4027.195.
PC3 measured 0.0 conforming minutes against a required 4 → rule state False.

| Time | O | H | L | C | Dir | New extreme | Respects (Tom's test) | Progresses | Counted by | Took prev 15m | Markers |
|---|---|---|---|---|---|---|---|---|---|---|
| 01:10 | 4022.78 | 4025.50 | 4022.39 | 4025.32 | up | yes | — | yes | — | — | extension activation |
| 01:11 | 4025.31 | 4029.43 | 4024.77 | 4027.98 | up | yes | yes | yes | — | — |  |
| 01:12 | 4028.01 | 4029.18 | 4026.36 | 4027.25 | down | no | yes | no | — | — |  |
| 01:13 | 4027.27 | 4028.03 | 4025.18 | 4027.32 | up | no | no | yes | — | — |  |
| 01:14 | 4027.29 | 4027.86 | 4026.60 | 4027.22 | down | no | yes | no | — | — |  |
| 01:15 | 4027.24 | 4030.01 | 4027.20 | 4029.36 | up | yes | yes | yes | — | — |  |
| 01:16 | 4029.34 | 4031.73 | 4029.10 | 4030.03 | up | yes | yes | yes | — | — |  |
| 01:17 | 4030.00 | 4030.97 | 4028.55 | 4028.89 | down | no | no | no | — | — |  |
| 01:18 | 4028.91 | 4032.51 | 4028.84 | 4031.98 | up | yes | yes | yes | — | — |  |
| 01:19 | 4031.95 | 4035.37 | 4031.82 | 4034.64 | up | yes | yes | yes | — | — |  |
| 01:20 | 4034.66 | 4036.65 | 4033.83 | 4036.40 | up | yes | yes | yes | — | — |  |
| 01:21 | 4037.14 | 4041.65 | 4037.14 | 4041.20 | up | yes | yes | yes | — | — |  |
| 01:22 | 4041.19 | 4045.51 | 4040.60 | 4043.53 | up | yes | yes | yes | — | — |  |
| 01:23 | 4043.54 | 4046.55 | 4042.60 | 4046.38 | up | yes | yes | yes | — | — |  |
| 01:24 | 4046.10 | 4047.14 | 4044.70 | 4045.58 | down | yes | yes | no | — | — |  |
| 01:25 | 4045.50 | 4047.05 | 4043.97 | 4046.38 | up | no | no | yes | — | — |  |
| 01:26 | 4046.47 | 4052.01 | 4046.38 | 4048.94 | up | yes | yes | yes | — | — |  |
| 01:27 | 4049.03 | 4051.19 | 4048.13 | 4048.27 | down | no | yes | no | — | — |  |
| 01:28 | 4048.28 | 4051.22 | 4046.78 | 4049.07 | up | no | no | yes | — | — |  |
| 01:29 | 4049.03 | 4050.10 | 4047.84 | 4047.84 | down | no | yes | no | H-F | — |  |
| 01:30 | 4047.86 | 4049.06 | 4045.80 | 4045.92 | down | no | no | no | — | no | entry 15m candle opens |
| 01:31 | 4045.94 | 4049.40 | 4045.64 | 4049.15 | up | no | no | yes | — | no |  |
| 01:32 | 4049.12 | 4049.61 | 4047.57 | 4047.57 | down | no | yes | no | — | no |  |
| 01:33 | 4047.53 | 4048.25 | 4046.16 | 4046.16 | down | no | no | no | — | no |  |
| 01:34 | 4046.10 | 4050.84 | 4045.78 | 4050.71 | up | no | no | yes | — | no | 5s sweep |
| 01:35 | 4050.72 | 4052.70 | 4050.23 | 4052.11 | up | yes | yes | yes | H-H | yes |  |
| 01:36 | 4052.05 | 4053.05 | 4051.39 | 4052.86 | up | yes | yes | yes | H-H | yes |  |
| 01:37 | 4052.89 | 4053.43 | 4050.97 | 4052.40 | down | yes | no | no | H-H | yes | extension extreme |
| 01:38 | 4052.38 | 4052.98 | 4051.09 | 4051.32 | down | no | yes | no | H-D, H-H | yes |  |
| 01:39 | 4051.29 | 4052.41 | 4050.59 | 4050.81 | down | no | no | no | — | yes | 5s shift / decision |

| Reading | Value | Anchor |
|---|---|---|
| H-A | 0 conforming 1m candles | run ends at the extension-extreme bar 01:37 |
| H-B | 0 1m candles, inclusive | same run as H-A |
| H-C | 0.0 elapsed minutes | first H-A candle open → 5s shift 01:39:40 |
| H-D | 1 conforming 1m candles | run ends at the last 1m bar closed before the shift (01:38) |
| H-E | 2 1m candles, inclusive | same run as H-D |
| H-G | 0 1m candles, ≤ 1 violation | run ends at the extension-extreme bar 01:37 |
| H-H | 4 1m candles, ≤ 1 violation | run ends at the last 1m bar closed before the shift (01:38) |
| H-F | 1 conforming 1m candles | run ends at the last 1m bar closed before the entry 15m candle opens (01:29) |
