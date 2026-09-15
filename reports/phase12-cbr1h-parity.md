# Phase 12: CBR1H Course-Example Parity

Generated 2026-09-15T05:13:36.832624+00:00 by `src/cbr/engine/phase12_run.py`. Implementation parity only: no fills, trade outcomes or P&L. Tolerances: price MATCH ≤ $0.50, FEED_NEAR ≤ $2.00, entry time MATCH ≤ 2 min (**not pre-registered**: set after an exploratory look at engine output on these windows).

## CX-LT1-1 · variant A

Hour context: {'condition': 'RANGE', 'c_med': 0.8126784180292626, 'n_legs': 3, 'cond_direction': 'NONE', 'rules_failed': [], 'context_reason': None, 'h_open': 4368.726500000001} · candidates 50 · ARMED 0

| Dimension | Engine | Tom | Diff | Class | Mismatch classification |
|---|---|---|---|---|---|
| context | RANGE | RANGE |  | MATCH |  |
| direction | BUY | BUY |  | MATCH |  |
| extension | {'dir': 'DOWN', 'duration_min': 38.0, 'no_pullback': False, 'extreme': 4332.955, 'two_sided': False} | hour pushed one way ~20-30 min into the range extreme |  | MISMATCH | DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open) |
| timing_window | 22 ≤ mih ≤ 52 | 39.25 |  | MATCH |  |
| structure_trigger | {'trigger': np.float64(4340.185), 'tier': '1m', 'kind': 'prior', 'decision': Timestamp('2025-10-21 01:39:00+0000', tz='UTC')} | 4340.13 | 0.055 | MATCH |  |
| entry_time | 2025-10-21 01:39:35+00:00 | 2025-10-21 01:39:15+00:00 | 0.33 | MATCH |  |
| stop_anchor | {'at_activation': np.float64(4332.955), 'at_touch': np.float64(4332.955)} | 4332.96 | -0.005 | MATCH |  |
| target_inputs | {'h_open': np.float64(4368.726500000001), 'target_at_touch': np.float64(4350.84075)} | 4351.59 | -0.749 | FEED_NEAR | DATA_DIFFERENCE (feed/level offset within $2; Phase 9) |
| acceptance | REJECTED | taken |  | MISMATCH | COMPOSITE (see failed-rule classes) |

Failed rules on the nearest candidate:

- `M1H-6A-4-HILO-TIER` → **SPEC_VS_EXAMPLE_CONFLICT**: OQ-39: this HILO's tier isn't the one spec 6A prescribes for the HVCS volume (1m normally, 5m when low-volume); Tom enters on a 5-second shift
- `M1H-COND-04` → **UNRESOLVED_INTERPRETATION**: OQ-36 scope: prior played-out setups (resolution basis not approved)
- `M1H-OE-02` → **DECLARED_BASELINE_CHOICE**: D8 / OQ-22: V1 measures no-pullback from the hour open; LAST_RESET is a pre-registered ablation

All candidates in the trade direction decided within [Tom − 3 min, Tom + 1 min] (selection rule: closest structure touch to Tom's entry time, fixed before comparison):

| Decision | Tier | Kind | Trigger | Trigger − Tom | Touch | Failed rules |
|---|---|---|---|---|---|---|
| 01:37:00 | 1m | prior | 4345.035 | 4.905 | — | M1H-6A-4-HILO-TIER, M1H-COND-04, M1H-OE-02 |
| 01:38:00 | 1m | prior | 4342.575 | 2.445 | — | M1H-6A-4-HILO-TIER, M1H-COND-04, M1H-OE-02 |
| 01:39:00 | 1m | prior | 4340.185 | 0.055 | 01:39:35 | M1H-6A-4-HILO-TIER, M1H-COND-04, M1H-OE-02 |
| 01:40:00 | 5m | prior | 4347.43 | 7.3 | — | M1H-COND-04, M1H-OE-02 |

Rule failures in the hour: [('M1H-COND-04', 50), ('M1H-OE-02', 48), ('M1H-LOC-01', 30), ('M1H-OE-01', 23), ('M1H-6A-4-HILO-TIER', 23), ('M1H-TIME-01', 19), ('M1H-OE-04b', 16), ('IMPL-REWARD', 12), ('M1H-6A-2-PREV-BREAK', 11), ('M1H-6A-3-NEW-EXTREME-IN-Q', 9), ('M1H-OE-04a', 6), ('M1H-6A-1-HVCS', 1)]

## CX-LT1-1 · variant B

Hour context: {'condition': 'RANGE', 'c_med': 0.8126784180292626, 'n_legs': 3, 'cond_direction': 'NONE', 'rules_failed': [], 'context_reason': None, 'h_open': 4368.726500000001} · candidates 0 · ARMED 0

| Dimension | Engine | Tom | Diff | Class | Mismatch classification |
|---|---|---|---|---|---|
| context | RANGE | RANGE |  | MATCH |  |
| direction | BUY | BUY |  | MATCH |  |
| extension | {'dir': 'DOWN', 'duration_min': 38.0, 'no_pullback': False, 'extreme': 4332.955, 'two_sided': False} | hour pushed one way ~20-30 min into the range extreme |  | MISMATCH | DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open) |
| timing_window | 22 ≤ mih ≤ 52 | 39.25 |  | MATCH |  |
| structure_trigger | None | 4340.13 |  | NOT_REPRODUCED | SPEC_VS_EXAMPLE_CONFLICT (OQ-39: Tom's entry is a 5s shift; FRACTAL_1M found no completed 1m type 3) |

Rule failures in the hour: []

## CX-TE1-1 · variant A

Hour context: {'condition': 'RANGE', 'c_med': 1.0587606202839743, 'n_legs': 4, 'cond_direction': 'UP', 'rules_failed': [], 'context_reason': nan, 'h_open': 4122.4400000000005} · candidates 44 · ARMED 0

| Dimension | Engine | Tom | Diff | Class | Mismatch classification |
|---|---|---|---|---|---|
| context | RANGE | TRENDING_RANGE (bearish, counter) or RANGE |  | MATCH |  |
| direction | BUY | BUY |  | MATCH |  |
| extension | {'dir': 'DOWN', 'duration_min': 36.0, 'no_pullback': False, 'extreme': 4103.110000000001, 'two_sided': False} | hour pushed one way ~20-30 min into the range extreme |  | MISMATCH | DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open) |
| timing_window | 22 ≤ mih ≤ 52 | 37.5 |  | MATCH |  |
| structure_trigger | {'trigger': np.float64(4104.085000000001), 'tier': '1m', 'kind': 'prior', 'decision': Timestamp('2025-10-24 04:38:00+0000', tz='UTC')} | 4105.58 | -1.495 | FEED_NEAR | DATA_DIFFERENCE (feed/level offset within $2; Phase 9) |
| entry_time | 2025-10-24 04:38:00+00:00 | 2025-10-24 04:37:30+00:00 | 0.5 | MATCH |  |
| stop_anchor | {'at_activation': np.float64(4102.8814999999995), 'at_touch': np.float64(4102.8814999999995)} | 4102.8 | 0.081 | MATCH |  |
| target_inputs | {'h_open': np.float64(4122.4400000000005), 'target_at_touch': np.float64(4112.66075)} | 4109.71 | 2.951 | MISMATCH | EXAMPLE_TARGET_NOT_SPEC_TARGET (tool levels may be illustrative (tool R:R 1.49 vs stated 2.3R)) |
| acceptance | REJECTED | taken |  | MISMATCH | COMPOSITE (see failed-rule classes) |

Failed rules on the nearest candidate:

- `M1H-COND-04` → **UNRESOLVED_INTERPRETATION**: OQ-36 scope: prior played-out setups (resolution basis not approved)
- `M1H-OE-02` → **DECLARED_BASELINE_CHOICE**: D8 / OQ-22: V1 measures no-pullback from the hour open; LAST_RESET is a pre-registered ablation

All candidates in the trade direction decided within [Tom − 3 min, Tom + 1 min] (selection rule: closest structure touch to Tom's entry time, fixed before comparison):

| Decision | Tier | Kind | Trigger | Trigger − Tom | Touch | Failed rules |
|---|---|---|---|---|---|---|
| 04:35:00 | 1m | prior | 4105.41 | -0.17 | 04:35:00 | M1H-COND-04, M1H-OE-02 |
| 04:35:00 | 5m | prior | 4107.73 | 2.15 | — | M1H-6A-4-HILO-TIER, M1H-COND-04, M1H-OE-02 |
| 04:36:25 | 1m | same | 4105.565 | -0.015 | — | M1H-COND-04, M1H-OE-02 |
| 04:37:00 | 1m | prior | 4105.23 | -0.35 | — | M1H-COND-04, M1H-OE-02 |
| 04:38:00 | 1m | prior | 4104.085 | -1.495 | 04:38:00 | M1H-COND-04, M1H-OE-02 |

Rule failures in the hour: [('M1H-COND-04', 44), ('M1H-OE-02', 43), ('M1H-OE-01', 22), ('M1H-TIME-01', 22), ('M1H-OE-04b', 20), ('M1H-LOC-01', 16), ('M1H-6A-2-PREV-BREAK', 11), ('IMPL-REWARD', 10), ('M1H-6A-4-HILO-TIER', 9), ('M1H-6A-1-HVCS', 3), ('M1H-6A-3-NEW-EXTREME-IN-Q', 3), ('M1H-OE-04a', 2)]

## CX-TE1-1 · variant B

Hour context: {'condition': 'RANGE', 'c_med': 1.0587606202839743, 'n_legs': 4, 'cond_direction': 'UP', 'rules_failed': [], 'context_reason': nan, 'h_open': 4122.4400000000005} · candidates 0 · ARMED 0

| Dimension | Engine | Tom | Diff | Class | Mismatch classification |
|---|---|---|---|---|---|
| context | RANGE | TRENDING_RANGE (bearish, counter) or RANGE |  | MATCH |  |
| direction | BUY | BUY |  | MATCH |  |
| extension | {'dir': 'DOWN', 'duration_min': 36.0, 'no_pullback': False, 'extreme': 4103.110000000001, 'two_sided': False} | hour pushed one way ~20-30 min into the range extreme |  | MISMATCH | DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open) |
| timing_window | 22 ≤ mih ≤ 52 | 37.5 |  | MATCH |  |
| structure_trigger | None | 4105.58 |  | NOT_REPRODUCED | SPEC_VS_EXAMPLE_CONFLICT (OQ-39: Tom's entry is a 5s shift; FRACTAL_1M found no completed 1m type 3) |

Rule failures in the hour: []

## CX-LT3-2 · variant A

Hour context: {'condition': 'UNDEFINED', 'c_med': None, 'n_legs': 0, 'cond_direction': 'NONE', 'rules_failed': ['M1H-COND-01', 'M1H-COND-02'], 'context_reason': None, 'h_open': 4020.425} · candidates 45 · ARMED 0

| Dimension | Engine | Tom | Diff | Class | Mismatch classification |
|---|---|---|---|---|---|
| context | UNDEFINED | unclear: 'very bullish, a little bit trendy' |  | MISMATCH | SOURCE_AMBIGUITY (OQ-40: condition window across the weekend closure) |
| direction | SELL | SELL |  | MATCH |  |
| extension | {'dir': 'UP', 'duration_min': 37.0, 'no_pullback': False, 'extreme': 4053.425, 'two_sided': False} | hour pushed one way ~20-30 min into the range extreme |  | MISMATCH | DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open) |
| timing_window | 22 ≤ mih ≤ 52 | 40.0 |  | MATCH |  |
| structure_trigger | {'trigger': np.float64(4050.2185), 'tier': '5m', 'kind': 'prior', 'decision': Timestamp('2025-11-10 01:40:00+0000', tz='UTC')} | 4050.71 | -0.492 | MATCH |  |
| entry_time | 2025-11-10 01:40:15+00:00 | 2025-11-10 01:40:00+00:00 | 0.25 | MATCH |  |
| stop_anchor | {'at_activation': np.float64(4053.425), 'at_touch': np.float64(4053.425)} | 4053.3 | 0.125 | MATCH |  |
| target_inputs | {'h_open': np.float64(4020.425), 'target_at_touch': np.float64(4036.925)} | 4043.8 | -6.875 | MISMATCH | EXAMPLE_TARGET_NOT_SPEC_TARGET (initial TP at a nearer level; 50% described as most aggressive) |
| acceptance | REJECTED | taken |  | MISMATCH | COMPOSITE (see failed-rule classes) |

Failed rules on the nearest candidate:

- `M1H-6A-4-HILO-TIER` → **SPEC_VS_EXAMPLE_CONFLICT**: OQ-39: this HILO's tier isn't the one spec 6A prescribes for the HVCS volume (1m normally, 5m when low-volume); Tom enters on a 5-second shift
- `M1H-COND-01` → **SOURCE_AMBIGUITY**: OQ-40: 8 h condition window measured in clock hours reaches into the weekend closure
- `M1H-COND-02` → **SOURCE_AMBIGUITY**: OQ-40: as above
- `M1H-COND-04` → **UNRESOLVED_INTERPRETATION**: OQ-36 scope: prior played-out setups (resolution basis not approved)
- `M1H-OE-02` → **DECLARED_BASELINE_CHOICE**: D8 / OQ-22: V1 measures no-pullback from the hour open; LAST_RESET is a pre-registered ablation

All candidates in the trade direction decided within [Tom − 3 min, Tom + 1 min] (selection rule: closest structure touch to Tom's entry time, fixed before comparison):

| Decision | Tier | Kind | Trigger | Trigger − Tom | Touch | Failed rules |
|---|---|---|---|---|---|---|
| 01:37:00 | 1m | prior | 4051.38 | 0.67 | 01:37:45 | M1H-COND-01, M1H-COND-02, M1H-COND-04, M1H-OE-02 |
| 01:38:00 | 1m | prior | 4050.96 | 0.25 | — | M1H-COND-01, M1H-COND-02, M1H-COND-04, M1H-OE-02 |
| 01:40:00 | 5m | prior | 4050.218 | -0.492 | 01:40:15 | M1H-6A-4-HILO-TIER, M1H-COND-01, M1H-COND-02, M1H-COND-04, M1H-OE-02 |

Rule failures in the hour: [('M1H-COND-01', 45), ('M1H-COND-02', 45), ('M1H-COND-04', 45), ('M1H-OE-02', 36), ('M1H-OE-01', 19), ('M1H-TIME-01', 19), ('IMPL-REWARD', 13), ('M1H-6A-2-PREV-BREAK', 11), ('M1H-6A-3-NEW-EXTREME-IN-Q', 11), ('M1H-OE-04b', 10), ('M1H-6A-4-HILO-TIER', 10), ('M1H-6A-1-HVCS', 6)]

## CX-LT3-2 · variant B

Hour context: {'condition': 'UNDEFINED', 'c_med': None, 'n_legs': 0, 'cond_direction': 'NONE', 'rules_failed': ['M1H-COND-01', 'M1H-COND-02'], 'context_reason': None, 'h_open': 4020.425} · candidates 0 · ARMED 0

| Dimension | Engine | Tom | Diff | Class | Mismatch classification |
|---|---|---|---|---|---|
| context | UNDEFINED | unclear: 'very bullish, a little bit trendy' |  | MISMATCH | SOURCE_AMBIGUITY (OQ-40: condition window across the weekend closure) |
| direction | SELL | SELL |  | MATCH |  |
| extension | {'dir': 'UP', 'duration_min': 37.0, 'no_pullback': False, 'extreme': 4053.425, 'two_sided': False} | hour pushed one way ~20-30 min into the range extreme |  | MISMATCH | DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open) |
| timing_window | 22 ≤ mih ≤ 52 | 40.0 |  | MATCH |  |
| structure_trigger | None | 4050.71 |  | NOT_REPRODUCED | SPEC_VS_EXAMPLE_CONFLICT (OQ-39: Tom's entry is a 5s shift; FRACTAL_1M found no completed 1m type 3) |

Rule failures in the hour: []

## CBR15 rerun with M15-HTF-01 fed by CBR1H-A hourly state

- CX-LT1-1: 8 candidates, HTF states [('CLEAR', 8)], ARMED 0
- CX-TE1-1: 14 candidates, HTF states [('CLEAR', 14)], ARMED 0
- CX-LT3-2: 9 candidates, HTF states [('CLEAR', 9)], ARMED 0
