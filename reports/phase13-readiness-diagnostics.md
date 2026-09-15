# Phase 13 Readiness Diagnostics

> **Historical (D19).** Generated at commit `3e45fc8` by `src/cbr/engine/readiness_diagnostics.py`, which D19 retired: it evaluated at Tom's entry time or selected candidates near it, and it ran the pre-D19 engine semantics. Not regenerated; not evidence for Phase 13 parity.


Generated 2026-09-15T10:03:58.460686+00:00 by `src/cbr/engine/readiness_diagnostics.py`. STRUCTURE facts only; no fills, outcomes or P&L. Tom's entry time is only the evaluation point; nothing is selected by it.

## CX-LT1-1 (BUY, entry 2025-10-21 01:39:15+00:00)

### OQ-39

```json
{
 "s5_type3_breaks_near_entry": [
  {
   "sweep": "2025-10-21 01:38:35+00:00",
   "break": "2025-10-21 01:39:35+00:00",
   "trigger": 4340.185,
   "sweep_extreme": 4332.955
  }
 ],
 "hilo_arms_near_entry": [
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:34:00+00:00",
   "trigger": 4348.04,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:35:00+00:00",
   "trigger": 4346.57,
   "touch": "2025-10-21 01:35:05+00:00"
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:36:00+00:00",
   "trigger": 4347.43,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:37:00+00:00",
   "trigger": 4345.035,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:38:00+00:00",
   "trigger": 4342.575,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:39:00+00:00",
   "trigger": 4340.185,
   "touch": "2025-10-21 01:39:35+00:00"
  },
  {
   "tier": "5m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:30:00+00:00",
   "trigger": 4352.97,
   "touch": null
  },
  {
   "tier": "5m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:35:00+00:00",
   "trigger": 4350.58,
   "touch": null
  },
  {
   "tier": "5m",
   "kind": "prior",
   "arm_time": "2025-10-21 01:40:00+00:00",
   "trigger": 4347.43,
   "touch": "2025-10-21 01:42:25+00:00"
  }
 ],
 "ltf_1m_type3_breaks_in_hour": []
}
```

### OQ-40

```json
{
 "A_clock_hours": {
  "window_start": "2025-10-20 17:00:00+00:00",
  "window_hours": 8.0,
  "condition": "RANGE",
  "c_med": 0.813,
  "n_legs": 3,
  "direction": "NONE",
  "range_high": 4381.5565,
  "range_low": 4337.2865,
  "hour_rules_pass": true
 },
 "B_tradable_hours": {
  "window_start": "2025-10-20 16:00:00+00:00",
  "window_hours": 9.0,
  "condition": "RANGE",
  "c_med": 0.813,
  "n_legs": 3,
  "direction": "NONE",
  "range_high": 4381.5565,
  "range_low": 4337.2865,
  "hour_rules_pass": true
 },
 "C_populated_5m_bars": {
  "window_start": "2025-10-20 16:00:00+00:00",
  "window_hours": 9.0,
  "condition": "RANGE",
  "c_med": 0.813,
  "n_legs": 3,
  "direction": "NONE",
  "range_high": 4381.5565,
  "range_low": 4337.2865,
  "hour_rules_pass": true
 },
 "D_session_segment": {
  "window_start": "2025-10-20 22:00:00+00:00",
  "window_hours": 3.0,
  "condition": "UNDEFINED",
  "c_med": null,
  "n_legs": 0,
  "direction": "NONE",
  "range_high": 4375.5615,
  "range_low": 4353.281499999999,
  "hour_rules_pass": false,
  "segment": "since the last expected closure ended (2025-10-20 22:00:00+00:00)"
 }
}
```

### OQ-41

```json
{
 "oe_direction": "DOWN",
 "oe_extreme": 4332.955,
 "oe_extreme_time": "2025-10-21 01:38:00+00:00",
 "R1_15m_before_candle_containing_decision": {
  "candle_open": "2025-10-21 01:15:00+00:00",
  "high": 4361.0735,
  "low": 4349.47,
  "break": true
 },
 "R2_15m_before_candle_containing_oe_extreme": {
  "candle_open": "2025-10-21 01:15:00+00:00",
  "high": 4361.0735,
  "low": 4349.47,
  "break": true
 },
 "R3_last_15m_of_previous_hour": {
  "candle_open": "2025-10-21 00:45:00+00:00",
  "high": 4370.9865,
  "low": 4364.455,
  "break": true
 },
 "R4_previous_hourly_candle": {
  "candle_open": "2025-10-21 00:00:00+00:00",
  "high": 4371.15,
  "low": 4356.3835,
  "break": true
 }
}
```

### OQ-42

```json
{
 "fill_time_reading (Tom's entry)": {
  "at": "2025-10-21 01:39:15+00:00",
  "in_30_candle": true,
  "push_beyond_open": 17.434,
  "push_threshold": 1.005,
  "pushed": true,
  "q15_closed_in_trade_direction": false,
  "vetoed": false
 },
 "arm_time_reading (engine decision)": {
  "at": "2025-10-21 01:39:00+00:00",
  "in_30_candle": true,
  "push_beyond_open": 17.434,
  "push_threshold": 1.005,
  "pushed": true,
  "q15_closed_in_trade_direction": false,
  "vetoed": false
 }
}
```

### OQ-43

```json
{
 "oe_direction": "DOWN",
 "E1_longest_run_in_hour_up_to_decision (implemented)": {
  "end_bar": "2025-10-21 01:04:00+00:00",
  "minutes": 6,
  "valid": true,
  "lvcs": true,
  "hilo_tier": "5m"
 },
 "E2_last_displacement_bar (oe extreme bar)": {
  "end_bar": "2025-10-21 01:38:00+00:00",
  "minutes": 4,
  "valid": true,
  "lvcs": false,
  "hilo_tier": "1m"
 },
 "E3_bar_before_the_breaking_bar (j-1)": {
  "end_bar": "2025-10-21 01:38:00+00:00",
  "minutes": 4,
  "valid": true,
  "lvcs": false,
  "hilo_tier": "1m"
 },
 "E4_bar_two_before_the_break (j-2, the HILO reference bar's predecessor)": {
  "end_bar": "2025-10-21 01:37:00+00:00",
  "minutes": 3,
  "valid": false,
  "lvcs": false,
  "hilo_tier": "1m"
 }
}
```

## CX-TE1-1 (BUY, entry 2025-10-24 04:37:30+00:00)

### OQ-39

```json
{
 "s5_type3_breaks_near_entry": [
  {
   "sweep": "2025-10-24 04:36:35+00:00",
   "break": "2025-10-24 04:38:55+00:00",
   "trigger": 4105.565,
   "sweep_extreme": 4102.881
  }
 ],
 "hilo_arms_near_entry": [
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-24 04:34:00+00:00",
   "trigger": 4106.565,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-24 04:35:00+00:00",
   "trigger": 4105.41,
   "touch": "2025-10-24 04:35:00+00:00"
  },
  {
   "tier": "1m",
   "kind": "same",
   "arm_time": "2025-10-24 04:36:25+00:00",
   "trigger": 4105.565,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-24 04:37:00+00:00",
   "trigger": 4105.23,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-10-24 04:38:00+00:00",
   "trigger": 4104.085,
   "touch": "2025-10-24 04:38:00+00:00"
  },
  {
   "tier": "5m",
   "kind": "same",
   "arm_time": "2025-10-24 04:30:30+00:00",
   "trigger": 4109.505,
   "touch": null
  },
  {
   "tier": "5m",
   "kind": "prior",
   "arm_time": "2025-10-24 04:35:00+00:00",
   "trigger": 4107.73,
   "touch": null
  }
 ],
 "ltf_1m_type3_breaks_in_hour": []
}
```

### OQ-40

```json
{
 "A_clock_hours": {
  "window_start": "2025-10-23 20:00:00+00:00",
  "window_hours": 8.0,
  "condition": "RANGE",
  "c_med": 1.059,
  "n_legs": 4,
  "direction": "UP",
  "range_high": 4144.469999999999,
  "range_low": 4106.06,
  "hour_rules_pass": true
 },
 "B_tradable_hours": {
  "window_start": "2025-10-23 19:00:00+00:00",
  "window_hours": 9.0,
  "condition": "RANGE",
  "c_med": 1.059,
  "n_legs": 4,
  "direction": "UP",
  "range_high": 4144.469999999999,
  "range_low": 4106.06,
  "hour_rules_pass": true
 },
 "C_populated_5m_bars": {
  "window_start": "2025-10-23 19:00:00+00:00",
  "window_hours": 9.0,
  "condition": "RANGE",
  "c_med": 1.059,
  "n_legs": 4,
  "direction": "UP",
  "range_high": 4144.469999999999,
  "range_low": 4106.06,
  "hour_rules_pass": true
 },
 "D_session_segment": {
  "window_start": "2025-10-23 22:00:00+00:00",
  "window_hours": 6.0,
  "condition": "RANGE",
  "c_med": 1.198,
  "n_legs": 3,
  "direction": "UP",
  "range_high": 4144.469999999999,
  "range_low": 4106.06,
  "hour_rules_pass": true,
  "segment": "since the last expected closure ended (2025-10-23 22:00:00+00:00)"
 }
}
```

### OQ-41

```json
{
 "oe_direction": "DOWN",
 "oe_extreme": 4103.110000000001,
 "oe_extreme_time": "2025-10-24 04:36:00+00:00",
 "R1_15m_before_candle_containing_decision": {
  "candle_open": "2025-10-24 04:15:00+00:00",
  "high": 4116.745,
  "low": 4105.2335,
  "break": true
 },
 "R2_15m_before_candle_containing_oe_extreme": {
  "candle_open": "2025-10-24 04:15:00+00:00",
  "high": 4116.745,
  "low": 4105.2335,
  "break": true
 },
 "R3_last_15m_of_previous_hour": {
  "candle_open": "2025-10-24 03:45:00+00:00",
  "high": 4123.620000000001,
  "low": 4116.370000000001,
  "break": true
 },
 "R4_previous_hourly_candle": {
  "candle_open": "2025-10-24 03:00:00+00:00",
  "high": 4123.620000000001,
  "low": 4107.610000000001,
  "break": true
 }
}
```

### OQ-42

```json
{
 "fill_time_reading (Tom's entry)": {
  "at": "2025-10-24 04:37:30+00:00",
  "in_30_candle": true,
  "push_beyond_open": 3.915,
  "push_threshold": 0.543,
  "pushed": true,
  "q15_closed_in_trade_direction": false,
  "vetoed": false
 },
 "arm_time_reading (engine decision)": {
  "at": "2025-10-24 04:37:00+00:00",
  "in_30_candle": true,
  "push_beyond_open": 3.915,
  "push_threshold": 0.543,
  "pushed": true,
  "q15_closed_in_trade_direction": false,
  "vetoed": false
 }
}
```

### OQ-43

```json
{
 "oe_direction": "DOWN",
 "E1_longest_run_in_hour_up_to_decision (implemented)": {
  "end_bar": "2025-10-24 04:24:00+00:00",
  "minutes": 9,
  "valid": true,
  "lvcs": false,
  "hilo_tier": "1m"
 },
 "E2_last_displacement_bar (oe extreme bar)": {
  "end_bar": "2025-10-24 04:36:00+00:00",
  "minutes": 2,
  "valid": false,
  "lvcs": false,
  "hilo_tier": "1m"
 },
 "E3_bar_before_the_breaking_bar (j-1)": {
  "end_bar": "2025-10-24 04:36:00+00:00",
  "minutes": 2,
  "valid": false,
  "lvcs": false,
  "hilo_tier": "1m"
 },
 "E4_bar_two_before_the_break (j-2, the HILO reference bar's predecessor)": {
  "end_bar": "2025-10-24 04:35:00+00:00",
  "minutes": 0,
  "valid": false,
  "lvcs": true,
  "hilo_tier": "5m"
 }
}
```

## CX-LT3-2 (SELL, entry 2025-11-10 01:40:00+00:00)

### OQ-39

```json
{
 "s5_type3_breaks_near_entry": [],
 "hilo_arms_near_entry": [
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-11-10 01:35:00+00:00",
   "trigger": 4045.765,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-11-10 01:36:00+00:00",
   "trigger": 4050.218,
   "touch": null
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-11-10 01:37:00+00:00",
   "trigger": 4051.38,
   "touch": "2025-11-10 01:37:45+00:00"
  },
  {
   "tier": "1m",
   "kind": "prior",
   "arm_time": "2025-11-10 01:38:00+00:00",
   "trigger": 4050.96,
   "touch": null
  },
  {
   "tier": "5m",
   "kind": "same",
   "arm_time": "2025-11-10 01:35:05+00:00",
   "trigger": 4045.625,
   "touch": null
  },
  {
   "tier": "5m",
   "kind": "prior",
   "arm_time": "2025-11-10 01:40:00+00:00",
   "trigger": 4050.218,
   "touch": "2025-11-10 01:40:15+00:00"
  }
 ],
 "ltf_1m_type3_breaks_in_hour": []
}
```

### OQ-40

```json
{
 "A_clock_hours": {
  "window_start": "2025-11-09 17:00:00+00:00",
  "window_hours": 8.0,
  "condition": "UNDEFINED",
  "c_med": null,
  "n_legs": 0,
  "direction": "NONE",
  "range_high": 4023.995,
  "range_low": 3997.95,
  "hour_rules_pass": false
 },
 "B_tradable_hours": {
  "window_start": "2025-11-07 16:00:00+00:00",
  "window_hours": 57.0,
  "condition": "TRENDING_RANGE",
  "c_med": 0.678,
  "n_legs": 3,
  "direction": "NONE",
  "range_high": 4027.535,
  "range_low": 3990.09,
  "hour_rules_pass": false
 },
 "C_populated_5m_bars": {
  "window_start": "2025-11-07 16:00:00+00:00",
  "window_hours": 57.0,
  "condition": "TRENDING_RANGE",
  "c_med": 0.678,
  "n_legs": 3,
  "direction": "NONE",
  "range_high": 4027.535,
  "range_low": 3990.09,
  "hour_rules_pass": false
 },
 "D_session_segment": {
  "window_start": "2025-11-09 23:00:00+00:00",
  "window_hours": 2.0,
  "condition": "UNDEFINED",
  "c_med": null,
  "n_legs": 0,
  "direction": "NONE",
  "range_high": 4023.995,
  "range_low": 3997.95,
  "hour_rules_pass": false,
  "segment": "since the last expected closure ended (2025-11-09 23:00:00+00:00)"
 }
}
```

### OQ-41

```json
{
 "oe_direction": "UP",
 "oe_extreme": 4053.425,
 "oe_extreme_time": "2025-11-10 01:37:00+00:00",
 "R1_15m_before_candle_containing_decision": {
  "candle_open": "2025-11-10 01:15:00+00:00",
  "high": 4052.0114999999996,
  "low": 4027.195,
  "break": true
 },
 "R2_15m_before_candle_containing_oe_extreme": {
  "candle_open": "2025-11-10 01:15:00+00:00",
  "high": 4052.0114999999996,
  "low": 4027.195,
  "break": true
 },
 "R3_last_15m_of_previous_hour": {
  "candle_open": "2025-11-10 00:45:00+00:00",
  "high": 4023.995,
  "low": 4016.535,
  "break": true
 },
 "R4_previous_hourly_candle": {
  "candle_open": "2025-11-10 00:00:00+00:00",
  "high": 4023.995,
  "low": 4011.215,
  "break": true
 }
}
```

### OQ-42

```json
{
 "fill_time_reading (Tom's entry)": {
  "at": "2025-11-10 01:40:00+00:00",
  "in_30_candle": true,
  "push_beyond_open": 5.56,
  "push_threshold": 0.71,
  "pushed": true,
  "q15_closed_in_trade_direction": false,
  "vetoed": false
 },
 "arm_time_reading (engine decision)": {
  "at": "2025-11-10 01:40:00+00:00",
  "in_30_candle": true,
  "push_beyond_open": 5.56,
  "push_threshold": 0.71,
  "pushed": true,
  "q15_closed_in_trade_direction": false,
  "vetoed": false
 }
}
```

### OQ-43

```json
{
 "oe_direction": "UP",
 "E1_longest_run_in_hour_up_to_decision (implemented)": {
  "end_bar": "2025-11-10 01:23:00+00:00",
  "minutes": 9,
  "valid": true,
  "lvcs": false,
  "hilo_tier": "1m"
 },
 "E2_last_displacement_bar (oe extreme bar)": {
  "end_bar": "2025-11-10 01:37:00+00:00",
  "minutes": 0,
  "valid": false,
  "lvcs": true,
  "hilo_tier": "5m"
 },
 "E3_bar_before_the_breaking_bar (j-1)": {
  "end_bar": "2025-11-10 01:39:00+00:00",
  "minutes": 0,
  "valid": false,
  "lvcs": true,
  "hilo_tier": "5m"
 },
 "E4_bar_two_before_the_break (j-2, the HILO reference bar's predecessor)": {
  "end_bar": "2025-11-10 01:38:00+00:00",
  "minutes": 0,
  "valid": false,
  "lvcs": true,
  "hilo_tier": "5m"
 }
}
```
