# Phase 13: Strategy Fidelity and Behavioral Parity Report

Run `CBR-RUN-013B-2` · generated 2026-09-15T22:27:59+00:00 · protocol CBR-PROT-013B (approved D25) · spec under test CBR1H_BASELINE_V1-PC2 · signal state only: no fills, outcomes, P&L or optimization.

## Verdict: **FAIL**

FAIL conditions:
- gate A: a truncation / future-mutation spot check differed
- CX-LT3-2 core_structural_trigger: not met (CANON_MISMATCH)
- CX-TE1-1 core_structural_trigger: not met (CANON_MISMATCH)

Owner determination required:
- CX-LT1-1 core_structural_trigger: failed with OWNER_BASELINE_CHOICE only

| D25-P5 criterion | Result |
|---|---|
| 1_model_family_3of3 | True |
| 2_direction_3of3 | True |
| 3_extension_direction_3of3 | True |
| 4_core_structural_trigger_3of3 | False |
| 5_negative_control_clean | True |
| 6_no_open_implementation_bug | True |
| 7_no_unexplained_canon_mismatch | True |
| 8_every_mismatch_classified | True |
| 9_feed_study | MET |

Concerns (each classified below):
- CX-LT1-1 dim 6 extension_timing: CANON_MISMATCH
- CX-LT1-1 dim 8 shift_type: OWNER_BASELINE_CHOICE
- CX-LT1-1 dim 9 shift_time: OWNER_BASELINE_CHOICE
- CX-LT1-1 dim 10 stop_anchor: FEED_DIFFERENCE
- CX-LT1-1 dim 11 target_concept: FEED_DIFFERENCE
- CX-LT1-1: engine candidate REJECTED (failed: IMPL-REWARD=CANON_MISMATCH, M1H-COND-04=UNRESOLVED_SPEC_AMBIGUITY, M1H-LOC-01=CANON_MISMATCH, M1H-OE-01=CANON_MISMATCH, M1H-OE-02=OWNER_BASELINE_CHOICE, M1H-OE-04a=FEED_DEPENDENT_SIGNAL_DIFFERENCE, M1H-OE-04b=UNRESOLVED_SPEC_AMBIGUITY)
- CX-LT3-2 dim 3 condition: UNRESOLVED_SPEC_AMBIGUITY
- CX-LT3-2 dim 4 tr_direction: UNRESOLVED_SPEC_AMBIGUITY
- CX-LT3-2 dim 7 previous_15m_take: CANON_MISMATCH
- CX-LT3-2 dim 9 shift_time: CANON_MISMATCH
- CX-LT3-2 dim 10 stop_anchor: FEED_DIFFERENCE
- CX-LT3-2 dim 11 target_concept: CANON_MISMATCH
- CX-LT3-2: engine candidate REJECTED (failed: M1H-6A-1-HVCS-INTO-SHIFT=UNRESOLVED_SPEC_AMBIGUITY, M1H-6A-2-PREV-15M-BROKEN-BY-Q=CANON_MISMATCH, M1H-6A-3-NEW-EXTREME-IN-Q=CANON_MISMATCH, M1H-COND-03=UNRESOLVED_SPEC_AMBIGUITY, M1H-COND-04=UNRESOLVED_SPEC_AMBIGUITY, M1H-OE-02=OWNER_BASELINE_CHOICE)
- CX-TE1-1 dim 4 tr_direction: UNRESOLVED_SPEC_AMBIGUITY
- CX-TE1-1 dim 9 shift_time: CANON_MISMATCH
- CX-TE1-1 dim 10 stop_anchor: FEED_DIFFERENCE
- CX-TE1-1 dim 11 target_concept: FEED_DIFFERENCE
- CX-TE1-1: engine candidate REJECTED (failed: M1H-COND-04=UNRESOLVED_SPEC_AMBIGUITY, M1H-OE-02=OWNER_BASELINE_CHOICE)

Criterion 7 and 8 are structural: every CANON_MISMATCH carries cited evidence and every non-match has one primary class. D25 O-1…O-8 (criterion 9 reading, control window, variants, trigger, approved explanations, concerns, negative-control classification, DXY) are Research Engineer operationalizations frozen before the run.

## 1-3. Frozen inputs and hashes

| Item | SHA-256 |
|---|---|
| Protocol CBR-PROT-013B | `7a364f70cff2a780536ce4912b256ad056ac0804de07f439acca988dc88ffc7f` |
| Run specification CBR-RUN-013B-2 | `2dafe514d545442e27ca3b0b18a570da1a500e9997ca5832444732738d743a07` |
| Ruling D25 | `4672b9065e71f266371357dd54465a7952b1583dbc8bd8d04191f18d562f1b9a` |
| PC2 spec hash (CBR1H) | `4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2` |
| Freeze commit | `eb1a9f372d9a30514ab130e7902b9793c2b70450` (frozen 2026-09-15T22:20:39+00:00) |

Pre-execution tests at the freeze: 528 passed, 1 skipped in 44.04s; lint at the freeze: [*] 1 fixable with the `--fix` option.. All frozen files: `reports/phase13-run-manifest.json`. Superseded run CBR-RUN-013B-1 stopped before any result (`docs/governance/phase13-run-incident-1.md`). Research Engineer post-run review: `reports/phase13-post-run-review.md`.

| Data | Files | Hash check |
|---|---|---|
| Course STRUCTURE bars | 16 | all match canonical manifest: True |
| Recent ticks / STRUCTURE bars | 4 / 8 | all present: True |
| DXY CFD candles | 3 | all present: True |
| FOREXCOM / TVC exports | 7 | unchanged since the freeze |

## 4. Recent feed comparison (summary; full: `reports/phase13-feed-comparison.md`)

Zero lag: True · δ = 0.0000 · p95 residual 0.1600 · **τ = $0.20** · criterion 9: **MET**

| Core concept | Agreement |
|---|---|
| condition_at_hour_open | 98.8% (80/81; 95% CI 93.3-99.8%) |
| hour_extension_direction | 96.3% (234/243; 95% CI 93.1-98.0%) |
| hour_level_membership | 99.6% (224/225; 95% CI 97.5-99.9%) |
| ltf_swing_membership | 88.0% (249/283; 95% CI 83.7-91.3%) |
| mtf_swing_membership | 100.0% (39/39; 95% CI 91.0-100.0%) |
| takes_15m | 98.1% (689/702; 95% CI 96.9-98.9%) |
| type3_1m | 92.0% (23/25; 95% CI 75.0-97.8%) |

## 5. Higher-timeframe fidelity: see `reports/phase13-higher-timeframe-fidelity.md`

## 6. Behavioral parity per positive example

| Example | Scored variant | Model family | Direction | Extension direction | Core trigger | Example verdict |
|---|---|---|---|---|---|---|
| CX-LT1-1 | A | ✓ BEHAVIORAL_MATCH | ✓ BEHAVIORAL_MATCH | ✓ BEHAVIORAL_MATCH | ✗ OWNER_BASELINE_CHOICE | **FEED_DEPENDENT_SIGNAL_DIFFERENCE** |
| CX-LT3-2 | A | ✓ BEHAVIORAL_MATCH | ✓ BEHAVIORAL_MATCH | ✓ BEHAVIORAL_MATCH | ✗ CANON_MISMATCH | **CANON_MISMATCH** |
| CX-TE1-1 | A | ✓ BEHAVIORAL_MATCH | ✓ BEHAVIORAL_MATCH | ✓ BEHAVIORAL_MATCH | ✗ CANON_MISMATCH | **CANON_MISMATCH** |

### CX-LT1-1 · hour 2025-10-21T01:00:00+00:00 · BUY

#### Variant A · BASELINE_SPEC · DIAGNOSTIC_FIRST_IN_ORDER · candidates in hour 9 (ARMED 0)

Candidate `CBR1H_BASELINE_V1/A/20251021T0100/BUY/0` · event **REJECTED** · decision 2025-10-21T01:07:00+00:00 · shift None at 4366.8150 · cancel OE_PULLBACK · example verdict **FEED_DEPENDENT_SIGNAL_DIFFERENCE**

| # | Dimension | Engine | Course | Status | Class | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | model | {"entry_model": "HVCS_S5_SHIFT", "parent": "HVCS", "variant": "A"} | CBR1H 5s shift | MATCH | **BEHAVIORAL_MATCH** |  |
| 2 | direction | BUY | BUY | MATCH | **BEHAVIORAL_MATCH** |  |
| 3 | condition | {"c_med": 0.8126784180292626, "cond_direction": "NONE", "condition": "RANGE", "n_legs": 3} | [{"condition": "RANGE"}, {"condition": "TRENDING_RANGE"}] | MATCH | **BEHAVIORAL_MATCH** |  |
| 4 | tr_direction | NONE | — | NOT_APPLICABLE | **NOT_APPLICABLE** |  |
| 5 | extension_direction | DOWN | DOWN | MATCH | **BEHAVIORAL_MATCH** | margin_usd +3.492 |
| 6 | extension_timing | {"oe_duration_min": 6.0, "oe_extreme_time": "2025-10-21T01:06:00+00:00", "oe_no_pullback": false, "reference_time": "2025-10-21T01:07:00+00:00"} | duration ≥ 20 min, extreme before the shift | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-018, E1H-002; course CX-LT1-1 overextension: Hour candle opened and pushed bearish into the low of the larger range; duration not stated (00:00:09-00:00:18) |
| 7 | previous_15m_take | {"q_break_by_q": true, "q_open_utc": "2025-10-21T01:00:00+00:00", "q_prev_closed_in_trade_direction": false} | 15m candle over-extended bearish and broke the low before the ~37-39 min shift | MATCH | **BEHAVIORAL_MATCH** | margin_usd +2.830 |
| 8 | shift_type | {"cancel_reason": "OE_PULLBACK", "m1_hilo_armed_at_decision": true, "s5_type3_direction": "BUY", "shift_completed": false} | seconds shift (5-second chart: low then take out a high) | MISMATCH | **OWNER_BASELINE_CHOICE** | canon_evidence: E1H-018; cancel OE_PULLBACK; course CX-LT1-1 entry_model: seconds shift (5-second chart: low then take out a high) (00:02:47-00:02:56); owner_baseline_choice: a completed shift in the course direction under ['STRICT_COURSE:oe_origin=LAST_RESET'] |
| 9 | shift_time | — | {"tolerance_s": 15, "tom_interval": ["2025-10-21T01:39:15+00:00", "2025-10-21T01:39:15+00:00"]} | MISMATCH | **OWNER_BASELINE_CHOICE** | canon_evidence: E1H-018; cancel OE_PULLBACK; course CX-LT1-1 entry_model: seconds shift (5-second chart: low then take out a high) (00:02:47-00:02:56); owner_baseline_choice: a completed shift in the course direction under ['STRICT_COURSE:oe_origin=LAST_RESET'] · P-3 {'equivalent': False, 'reason': 'no completed shift'} |
| 10 | stop_anchor | {"anchor_at_shift": 4358.514999999999, "buffer_price": 0.2726986464631361, "source": "STRUCTURE_TICK_MID_5S_EXTENSION_EXTREME"} | {"delta_h": 0.06925, "tom_stop": 4332.96, "tom_stop_minus_delta_h": 4332.8907500000005} | FEED_DIFFERENCE | **FEED_DIFFERENCE** | tom_minus_engine -25.555 · adjusted_minus_engine -25.624 |
| 11 | target_concept | {"concept": "50% of extension from H.open", "target_at_shift": 4363.62075} | {"concept": "FIFTY_PERCENT_OF_MOVE", "tom_target": 4351.59} | FEED_DIFFERENCE | **FEED_DIFFERENCE** | tom_minus_engine -12.031 · adjusted_minus_engine -12.100 |
| 12 | dxy (descriptive) | {"dxy_15m_forming_direction": "UP", "dxy_15m_forming_state": "OK", "dxy_15m_last_direction": "UP", "dxy_1h_forming_direction": "UP", "dxy_1h_forming_state": "OK", "dxy_1h_last_direction": "DOWN", "dxy_confidence": "FULL", "dxy_reason_codes": "", "field": "dxy_1h_forming_direction", "time": "2025-10-21T01:07:00+00:00", "tvc_hour_direction": "UP", "tvc_note": "TVC:DXY 1h bar final direction (hour close; hindsight, descriptive)", "value": "UP"} | {"compare_field": "dxy_1h_forming_direction", "direction": "UP", "text": "DXY still bullish at entry, into highs"} | MATCH | **BEHAVIORAL_MATCH** |  |

| Failed rule | Primary class | Secondary | Tags | Dukascopy margin | Evidence |
|---|---|---|---|---|---|
| IMPL-REWARD | **CANON_MISMATCH** | [] | [] | — | canon_evidence: PC2 rule IMPL-REWARD (M1H-TP-01); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12) |
| M1H-COND-04 | **UNRESOLVED_SPEC_AMBIGUITY** | [] | [] | — | canon_evidence: PC2 rule M1H-COND-04 (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12); open_question: M1H-COND-04 governed by OQ-05, OQ-36 |
| M1H-LOC-01 | **CANON_MISMATCH** | [] | [] | -13.2710 | canon_evidence: PC2 rule M1H-LOC-01 (E15-015, E1H-002); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12) |
| M1H-OE-01 | **CANON_MISMATCH** | [] | [] | — | canon_evidence: PC2 rule M1H-OE-01 (E1H-018, E1H-002); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12) |
| M1H-OE-02 | **OWNER_BASELINE_CHOICE** | [] | [] | -4.8325 | canon_evidence: PC2 rule M1H-OE-02 (E1H-018); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12); owner_baseline_choice: M1H-OE-02 passes under STRICT_COURSE:oe_origin=LAST_RESET (same candidate identity) |
| M1H-OE-04a | **FEED_DEPENDENT_SIGNAL_DIFFERENCE** | ['UNRESOLVED_SPEC_AMBIGUITY', 'CANON_MISMATCH'] | ['UNVERIFIED', 'DATA_LIMITATION'] | -0.0592 | canon_evidence: PC2 rule M1H-OE-04a (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12); feed_dependent: M1H-OE-04a: Dukascopy margin -0.0592 within feed band τ = 0.2; open_question: M1H-OE-04a governed by OQ-08 |
| M1H-OE-04b | **UNRESOLVED_SPEC_AMBIGUITY** | [] | [] | -4.2149 | canon_evidence: PC2 rule M1H-OE-04b (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-LT1-1 mtf_model: range (spoken); journal row for the matching Oct 21 12:39 PM trade says 'TRR CT' / 'Ranging' (00:07:07-00:07:12); open_question: M1H-OE-04b governed by OQ-08 |

STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):

| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |
|---|---|---|---|---|---|---|---|
| STRICT_COURSE:early_shift_guard=ALIGN_15M | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | None | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |
| STRICT_COURSE:early_shift_guard=FINAL_PUSH | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | None | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |
| STRICT_COURSE:oe_origin=LAST_RESET | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-10-21T01:29:05+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |

Causality spot checks (truncation + future mutation at mid-minute cuts): True · {"decision": {"cut": "2025-10-21T01:07:32+00:00", "future_mutation": {"decision_identical": true, "decision_rows": 1, "trigger_identical": true, "trigger_rows": 0}, "truncation": {"decision_identical": true, "decision_rows": 1, "trigger_identical": true, "trigger_rows": 0}}}

#### Variant B · BASELINE_SPEC · NO_CANDIDATE · candidates in hour 0 (ARMED 0)

| # | Dimension | Engine | Course | Status | Class | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | model | — | CBR1H 5s-shift candidate in H | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-021, E1H-022; course CX-LT1-1 entry_model: seconds shift (5-second chart: low then take out a high) (00:02:47-00:02:56) |

STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):

| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |
|---|---|---|---|---|---|---|---|
| STRICT_COURSE:early_shift_guard=ALIGN_15M | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |
| STRICT_COURSE:early_shift_guard=FINAL_PUSH | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |
| STRICT_COURSE:oe_origin=LAST_RESET | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |

Causality spot checks (truncation + future mutation at mid-minute cuts): None · {}

### CX-LT3-2 · hour 2025-11-10T01:00:00+00:00 · SELL

#### Variant A · BASELINE_SPEC · DIAGNOSTIC_FIRST_IN_ORDER · candidates in hour 9 (ARMED 0)

Candidate `CBR1H_BASELINE_V1/A/20251110T0100/SELL/8` · event **REJECTED** · decision 2025-11-10T01:50:00+00:00 · shift 2025-11-10T01:50:40+00:00 at 4050.9600 · cancel S5_SHIFT_TRIGGERED · example verdict **CANON_MISMATCH**

| # | Dimension | Engine | Course | Status | Class | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | model | {"entry_model": "HVCS_S5_SHIFT", "parent": "HVCS", "variant": "A"} | CBR1H 5s shift | MATCH | **BEHAVIORAL_MATCH** |  |
| 2 | direction | SELL | SELL | MATCH | **BEHAVIORAL_MATCH** |  |
| 3 | condition | {"c_med": 0.6780091432032203, "cond_direction": "NONE", "condition": "TRENDING_RANGE", "n_legs": 3} | [{"condition": "TRENDING_RANGE", "direction": "UP"}] | MISMATCH | **UNRESOLVED_SPEC_AMBIGUITY** | open_question: trending-range direction governed by OQ-01, OQ-02 |
| 4 | tr_direction | NONE | UP | MISMATCH | **UNRESOLVED_SPEC_AMBIGUITY** | open_question: direction governed by OQ-01, OQ-02; NONE = TREND_DIRECTION_UNRESOLVED (D17-4) |
| 5 | extension_direction | UP | UP | MATCH | **BEHAVIORAL_MATCH** | margin_usd +31.745 |
| 6 | extension_timing | {"oe_duration_min": 37.0, "oe_extreme_time": "2025-11-10T01:37:00+00:00", "oe_no_pullback": false, "reference_time": "2025-11-10T01:50:40+00:00"} | duration ≥ 20 min, extreme before the shift | MATCH | **BEHAVIORAL_MATCH** |  |
| 7 | previous_15m_take | {"q_break_by_q": false, "q_open_utc": "2025-11-10T01:45:00+00:00", "q_prev_closed_in_trade_direction": false} | Waited for the :30 15m candle to push bullish and take out the previous high before shifting (achieved at 36 min) | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-017, E1H-023; course CX-LT3-2 fifteen_min_cb: Waited for the :30 15m candle to push bullish and take out the previous high before shifting (achieved at 36 min) (00:08:10-00:08:25) · margin_usd -0.585 |
| 8 | shift_type | {"cancel_reason": "S5_SHIFT_TRIGGERED", "m1_hilo_armed_at_decision": true, "s5_type3_direction": "SELL", "shift_completed": true} | seconds shift with correlation (DXY shift bullish + gold spread shift bearish + take out low) | MATCH | **BEHAVIORAL_MATCH** |  |
| 9 | shift_time | 2025-11-10T01:50:40+00:00 | {"tolerance_s": 15, "tom_interval": ["2025-11-10T01:40:00+00:00", "2025-11-10T01:40:00+00:00"]} | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-021, E1H-022; frozen selection D19-10 takes the first shift; course CX-LT3-2 cb_hour_timing: previous high taken at 36 min; entry ~38-40 min (00:12:24-00:15:11) · P-3 {'direction_agrees': True, 'distance_to_tom_interval_s': 640.0, 'equivalent': False, 'same_15m_candle': False} |
| 10 | stop_anchor | {"anchor_at_shift": 4053.425, "buffer_price": 0.2405893769514883, "source": "STRUCTURE_TICK_MID_5S_EXTENSION_EXTREME"} | {"delta_h": 0.0375, "tom_stop": 4053.3, "tom_stop_minus_delta_h": 4053.2625000000003} | FEED_DIFFERENCE | **FEED_DIFFERENCE** | tom_minus_engine -0.125 · adjusted_minus_engine -0.162 |
| 11 | target_concept | {"concept": "50% of extension from H.open", "target_at_shift": 4036.925} | {"concept": "NEARER_DISCRETIONARY", "tom_target": 4043.8} | MISMATCH | **CANON_MISMATCH** | canon_evidence: M1H-TP-01 50% of the hour extension; course discretion: CX-LT3-2 target_description: initial TP at a nearer level; next target below the low; 50% of the extension described as the most aggressive TP (00:17:07-00:29:10) · tom_minus_engine +6.875 · adjusted_minus_engine +6.838 |
| 12 | dxy (descriptive) | {"dxy_15m_forming_direction": "DOWN", "dxy_15m_forming_state": "OK", "dxy_15m_last_direction": "UP", "dxy_1h_forming_direction": "DOWN", "dxy_1h_forming_state": "OK", "dxy_1h_last_direction": null, "dxy_confidence": "FULL", "dxy_reason_codes": "1h_last:DXY_CFD_MISSING_WHILE_DX_ACTIVE", "field": "dxy_15m_forming_direction", "time": "2025-11-10T01:50:40+00:00", "tvc_hour_direction": "DOWN", "tvc_note": "TVC:DXY 1h bar final direction (hour close; hindsight, descriptive)", "value": "DOWN"} | {"compare_field": "dxy_15m_forming_direction", "direction": "UP", "text": "DXY bearish at the start; shifted bullish at entry"} | MISMATCH | **CANON_MISMATCH** | canon_evidence: no DXY rule in CBR1H V1 (D25-P8); course DXY bearish at the start; shifted bullish at entry |

| Failed rule | Primary class | Secondary | Tags | Dukascopy margin | Evidence |
|---|---|---|---|---|---|
| M1H-6A-1-HVCS-INTO-SHIFT | **UNRESOLVED_SPEC_AMBIGUITY** | [] | [] | — | canon_evidence: PC2 rule M1H-6A-1-HVCS-INTO-SHIFT (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-LT3-2 mtf_model: unclear (strongly bullish / 'a little bit trendy'; counter-direction reversal in a condition he dislikes) (00:01:07-00:01:20); open_question: M1H-6A-1-HVCS-INTO-SHIFT governed by OQ-44, OQ-08 |
| M1H-6A-2-PREV-15M-BROKEN-BY-Q | **CANON_MISMATCH** | [] | [] | -0.5850 | canon_evidence: PC2 rule M1H-6A-2-PREV-15M-BROKEN-BY-Q (E1H-017, E1H-023); engine value from STRUCTURE bars; course: CX-LT3-2 mtf_model: unclear (strongly bullish / 'a little bit trendy'; counter-direction reversal in a condition he dislikes) (00:01:07-00:01:20) |
| M1H-6A-3-NEW-EXTREME-IN-Q | **CANON_MISMATCH** | [] | [] | -0.5850 | canon_evidence: PC2 rule M1H-6A-3-NEW-EXTREME-IN-Q (E1H-021); engine value from STRUCTURE bars; course: CX-LT3-2 mtf_model: unclear (strongly bullish / 'a little bit trendy'; counter-direction reversal in a condition he dislikes) (00:01:07-00:01:20) |
| M1H-COND-03 | **UNRESOLVED_SPEC_AMBIGUITY** | [] | [] | — | canon_evidence: PC2 rule M1H-COND-03 (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-LT3-2 mtf_model: unclear (strongly bullish / 'a little bit trendy'; counter-direction reversal in a condition he dislikes) (00:01:07-00:01:20); open_question: M1H-COND-03 governed by OQ-02 |
| M1H-COND-04 | **UNRESOLVED_SPEC_AMBIGUITY** | [] | [] | — | canon_evidence: PC2 rule M1H-COND-04 (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-LT3-2 mtf_model: unclear (strongly bullish / 'a little bit trendy'; counter-direction reversal in a condition he dislikes) (00:01:07-00:01:20); open_question: M1H-COND-04 governed by OQ-05, OQ-36 |
| M1H-OE-02 | **OWNER_BASELINE_CHOICE** | [] | [] | -3.3900 | canon_evidence: PC2 rule M1H-OE-02 (E1H-018); engine value from STRUCTURE bars; course: CX-LT3-2 mtf_model: unclear (strongly bullish / 'a little bit trendy'; counter-direction reversal in a condition he dislikes) (00:01:07-00:01:20); owner_baseline_choice: M1H-OE-02 passes under STRICT_COURSE:oe_origin=LAST_RESET (same candidate identity) |

STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):

| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |
|---|---|---|---|---|---|---|---|
| STRICT_COURSE:early_shift_guard=ALIGN_15M | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-11-10T01:50:40+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |
| STRICT_COURSE:early_shift_guard=FINAL_PUSH | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-11-10T01:50:40+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |
| STRICT_COURSE:oe_origin=LAST_RESET | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-11-10T01:50:40+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |

Causality spot checks (truncation + future mutation at mid-minute cuts): True · {"decision": {"cut": "2025-11-10T01:50:32+00:00", "future_mutation": {"decision_identical": true, "decision_rows": 9, "trigger_identical": true, "trigger_rows": 0}, "truncation": {"decision_identical": true, "decision_rows": 9, "trigger_identical": true, "trigger_rows": 0}}, "shift": {"cut": "2025-11-10T01:51:12+00:00", "future_mutation": {"decision_identical": true, "decision_rows": 9, "trigger_identical": true, "trigger_rows": 1}, "truncation": {"decision_identical": true, "decision_rows": 9, "trigger_identical": true, "trigger_rows": 1}}}

#### Variant B · BASELINE_SPEC · NO_CANDIDATE · candidates in hour 0 (ARMED 0)

| # | Dimension | Engine | Course | Status | Class | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | model | — | CBR1H 5s-shift candidate in H | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-021, E1H-022; course CX-LT3-2 entry_model: seconds shift with correlation (DXY shift bullish + gold spread shift bearish + take out low) (00:15:20-00:15:30) |

STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):

| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |
|---|---|---|---|---|---|---|---|
| STRICT_COURSE:early_shift_guard=ALIGN_15M | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |
| STRICT_COURSE:early_shift_guard=FINAL_PUSH | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |
| STRICT_COURSE:oe_origin=LAST_RESET | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |

Causality spot checks (truncation + future mutation at mid-minute cuts): None · {}

### CX-TE1-1 · hour 2025-10-24T04:00:00+00:00 · BUY

#### Variant A · BASELINE_SPEC · DIAGNOSTIC_FIRST_IN_ORDER · candidates in hour 13 (ARMED 0)

Candidate `CBR1H_BASELINE_V1/A/20251024T0400/BUY/7` · event **REJECTED** · decision 2025-10-24T04:24:15+00:00 · shift 2025-10-24T04:24:45+00:00 at 4109.1300 · cancel S5_SHIFT_TRIGGERED · example verdict **CANON_MISMATCH**

| # | Dimension | Engine | Course | Status | Class | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | model | {"entry_model": "HVCS_S5_SHIFT", "parent": "HVCS", "variant": "A"} | CBR1H 5s shift | MATCH | **BEHAVIORAL_MATCH** |  |
| 2 | direction | BUY | BUY | MATCH | **BEHAVIORAL_MATCH** |  |
| 3 | condition | {"c_med": 1.0587606202839743, "cond_direction": "UP", "condition": "RANGE", "n_legs": 4} | [{"condition": "TRENDING_RANGE", "direction": "DOWN"}, {"condition": "RANGE"}] | MATCH | **BEHAVIORAL_MATCH** |  |
| 4 | tr_direction | UP | DOWN | MISMATCH | **UNRESOLVED_SPEC_AMBIGUITY** | open_question: direction governed by OQ-01, OQ-02 |
| 5 | extension_direction | DOWN | DOWN | MATCH | **BEHAVIORAL_MATCH** | margin_usd +13.975 |
| 6 | extension_timing | {"oe_duration_min": 23.0, "oe_extreme_time": "2025-10-24T04:23:00+00:00", "oe_no_pullback": false, "reference_time": "2025-10-24T04:24:45+00:00"} | duration ≥ 20 min, extreme before the shift; course 20-30 min | MATCH | **BEHAVIORAL_MATCH** |  |
| 7 | previous_15m_take | {"q_break_by_q": true, "q_open_utc": "2025-10-24T04:15:00+00:00", "q_prev_closed_in_trade_direction": false} | The :30 15m candle opened and pushed bearish for its first half (~7.5 min), taking out the previous 15m low | MATCH | **BEHAVIORAL_MATCH** | margin_usd +8.270 |
| 8 | shift_type | {"cancel_reason": "S5_SHIFT_TRIGGERED", "m1_hilo_armed_at_decision": true, "s5_type3_direction": "BUY", "shift_completed": true} | seconds shift (break of the seconds-chart high; he also calls it 'a bit of a high low entry') | MATCH | **BEHAVIORAL_MATCH** |  |
| 9 | shift_time | 2025-10-24T04:24:45+00:00 | {"tolerance_s": 60, "tom_interval": ["2025-10-24T04:37:00+00:00", "2025-10-24T04:39:00+00:00"]} | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-021, E1H-022; frozen selection D19-10 takes the first shift; course CX-TE1-1 cb_hour_timing: ~37 minutes into the hour; labelled a '30m Reversal' (30-45 min window) (00:11:31-00:11:47) · P-3 {'direction_agrees': True, 'distance_to_tom_interval_s': 735.0, 'equivalent': False, 'same_15m_candle': False} |
| 10 | stop_anchor | {"anchor_at_shift": 4107.083500000001, "buffer_price": 0.16422989492096496, "source": "STRUCTURE_TICK_MID_5S_EXTENSION_EXTREME"} | {"delta_h": 0.015, "tom_stop": 4102.8, "tom_stop_minus_delta_h": 4102.785} | FEED_DIFFERENCE | **FEED_DIFFERENCE** | tom_minus_engine -4.284 · adjusted_minus_engine -4.299 |
| 11 | target_concept | {"concept": "50% of extension from H.open", "target_at_shift": 4114.761750000001} | {"concept": "FIFTY_PERCENT_OF_MOVE", "tom_target": 4109.71} | FEED_DIFFERENCE | **FEED_DIFFERENCE** | tom_minus_engine -5.052 · adjusted_minus_engine -5.067 |
| 12 | dxy (descriptive) | {"dxy_15m_forming_direction": "UP", "dxy_15m_forming_state": "OK", "dxy_15m_last_direction": "UP", "dxy_1h_forming_direction": "UP", "dxy_1h_forming_state": "OK", "dxy_1h_last_direction": "DOWN", "dxy_confidence": "FULL", "dxy_reason_codes": "", "field": "dxy_1h_forming_direction", "time": "2025-10-24T04:24:45+00:00", "tvc_hour_direction": "UP", "tvc_note": "TVC:DXY 1h bar final direction (hour close; hindsight, descriptive)", "value": "UP"} | {"compare_field": "dxy_1h_forming_direction", "direction": "UP", "text": "DXY range bound; hourly candle opened and pushed bullish into highs"} | MATCH | **BEHAVIORAL_MATCH** |  |

| Failed rule | Primary class | Secondary | Tags | Dukascopy margin | Evidence |
|---|---|---|---|---|---|
| M1H-COND-04 | **UNRESOLVED_SPEC_AMBIGUITY** | [] | [] | — | canon_evidence: PC2 rule M1H-COND-04 (1h-cbr-machine-spec.md); engine value from STRUCTURE bars; course: CX-TE1-1 mtf_model: trending range counter (journal: MTF model 'TRR CT', condition 'Ranging') (00:01:46-00:01:57); open_question: M1H-COND-04 governed by OQ-05, OQ-36 |
| M1H-OE-02 | **OWNER_BASELINE_CHOICE** | [] | [] | -0.5875 | canon_evidence: PC2 rule M1H-OE-02 (E1H-018); engine value from STRUCTURE bars; course: CX-TE1-1 mtf_model: trending range counter (journal: MTF model 'TRR CT', condition 'Ranging') (00:01:46-00:01:57); owner_baseline_choice: M1H-OE-02 passes under STRICT_COURSE:oe_origin=LAST_RESET (same candidate identity) |

STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):

| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |
|---|---|---|---|---|---|---|---|
| STRICT_COURSE:early_shift_guard=ALIGN_15M | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-10-24T04:24:45+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |
| STRICT_COURSE:early_shift_guard=FINAL_PUSH | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-10-24T04:24:45+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |
| STRICT_COURSE:oe_origin=LAST_RESET | DIAGNOSTIC_FIRST_IN_ORDER | REJECTED | 2025-10-24T04:24:45+00:00 | ✓ | ✓ | ✓ | ✗ CANON_MISMATCH |

Causality spot checks (truncation + future mutation at mid-minute cuts): False · {"decision": {"cut": "2025-10-24T04:24:47+00:00", "future_mutation": {"decision_identical": true, "decision_rows": 8, "trigger_identical": true, "trigger_rows": 1}, "truncation": {"decision_identical": true, "decision_rows": 8, "trigger_identical": false, "trigger_rows": 1}}, "shift": {"cut": "2025-10-24T04:25:17+00:00", "future_mutation": {"decision_identical": true, "decision_rows": 9, "trigger_identical": false, "trigger_rows": 1}, "truncation": {"decision_identical": true, "decision_rows": 9, "trigger_identical": true, "trigger_rows": 1}}}

#### Variant B · BASELINE_SPEC · NO_CANDIDATE · candidates in hour 0 (ARMED 0)

| # | Dimension | Engine | Course | Status | Class | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | model | — | CBR1H 5s-shift candidate in H | MISMATCH | **CANON_MISMATCH** | canon_evidence: E1H-021, E1H-022; course CX-TE1-1 entry_model: seconds shift (break of the seconds-chart high; he also calls it 'a bit of a high low entry') (00:12:17-00:12:30) |

STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):

| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |
|---|---|---|---|---|---|---|---|
| STRICT_COURSE:early_shift_guard=ALIGN_15M | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |
| STRICT_COURSE:early_shift_guard=FINAL_PUSH | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |
| STRICT_COURSE:oe_origin=LAST_RESET | NO_CANDIDATE | None | None | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH | ✗ CANON_MISMATCH |

Causality spot checks (truncation + future mutation at mid-minute cuts): None · {}

## 7. Negative control CX-LT3-1

Window 2025-11-10T01:28:00+00:00 → 2025-11-10T01:36:00+00:00 (D25 O-2) · expected NO_ELIGIBLE_CANONICAL_SIGNAL · result **NO_ELIGIBLE_CANONICAL_SIGNAL**


## 8. Mismatch register (scored variants, BASELINE_SPEC)

| Example | Item | Primary class | Secondary | Tags |
|---|---|---|---|---|
| CX-LT1-1 | dim 6 extension_timing | CANON_MISMATCH | [] | [] |
| CX-LT1-1 | dim 8 shift_type | OWNER_BASELINE_CHOICE | [] | [] |
| CX-LT1-1 | dim 9 shift_time | OWNER_BASELINE_CHOICE | [] | [] |
| CX-LT1-1 | dim 10 stop_anchor | FEED_DIFFERENCE |  |  |
| CX-LT1-1 | dim 11 target_concept | FEED_DIFFERENCE |  |  |
| CX-LT1-1 | rule IMPL-REWARD | CANON_MISMATCH | [] | [] |
| CX-LT1-1 | rule M1H-COND-04 | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT1-1 | rule M1H-LOC-01 | CANON_MISMATCH | [] | [] |
| CX-LT1-1 | rule M1H-OE-01 | CANON_MISMATCH | [] | [] |
| CX-LT1-1 | rule M1H-OE-02 | OWNER_BASELINE_CHOICE | [] | [] |
| CX-LT1-1 | rule M1H-OE-04a | FEED_DEPENDENT_SIGNAL_DIFFERENCE | ['UNRESOLVED_SPEC_AMBIGUITY', 'CANON_MISMATCH'] | ['UNVERIFIED', 'DATA_LIMITATION'] |
| CX-LT1-1 | rule M1H-OE-04b | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT3-2 | dim 3 condition | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT3-2 | dim 4 tr_direction | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT3-2 | dim 7 previous_15m_take | CANON_MISMATCH | [] | [] |
| CX-LT3-2 | dim 9 shift_time | CANON_MISMATCH | [] | [] |
| CX-LT3-2 | dim 10 stop_anchor | FEED_DIFFERENCE |  |  |
| CX-LT3-2 | dim 11 target_concept | CANON_MISMATCH | [] | [] |
| CX-LT3-2 | dim 12 dxy (descriptive) | CANON_MISMATCH | [] | [] |
| CX-LT3-2 | rule M1H-6A-1-HVCS-INTO-SHIFT | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT3-2 | rule M1H-6A-2-PREV-15M-BROKEN-BY-Q | CANON_MISMATCH | [] | [] |
| CX-LT3-2 | rule M1H-6A-3-NEW-EXTREME-IN-Q | CANON_MISMATCH | [] | [] |
| CX-LT3-2 | rule M1H-COND-03 | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT3-2 | rule M1H-COND-04 | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-LT3-2 | rule M1H-OE-02 | OWNER_BASELINE_CHOICE | [] | [] |
| CX-TE1-1 | dim 4 tr_direction | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-TE1-1 | dim 9 shift_time | CANON_MISMATCH | [] | [] |
| CX-TE1-1 | dim 10 stop_anchor | FEED_DIFFERENCE |  |  |
| CX-TE1-1 | dim 11 target_concept | FEED_DIFFERENCE |  |  |
| CX-TE1-1 | rule M1H-COND-04 | UNRESOLVED_SPEC_AMBIGUITY | [] | [] |
| CX-TE1-1 | rule M1H-OE-02 | OWNER_BASELINE_CHOICE | [] | [] |

## 9. Deterministic rerun

Complete-run result hashes: run 1 `f39054300808e2c4b11d074b4a8a4eeff4526a0707d5e63a9e1c4bb5cf10d063`, run 2 `f39054300808e2c4b11d074b4a8a4eeff4526a0707d5e63a9e1c4bb5cf10d063` → identical: **True**. Engine runs repeated within each complete run: 24, all identical: True.

## 10. Causality status

Pre-execution suite (truncation / future-mutation / guard / determinism tests included): 528 passed, 1 skipped in 44.04s. Per-example spot checks above. PC2 hash unchanged before and after the run (verified by the report step).

## 11. Unresolved concerns

- CX-LT1-1 dim 6 extension_timing: CANON_MISMATCH
- CX-LT1-1 dim 8 shift_type: OWNER_BASELINE_CHOICE
- CX-LT1-1 dim 9 shift_time: OWNER_BASELINE_CHOICE
- CX-LT1-1 dim 10 stop_anchor: FEED_DIFFERENCE
- CX-LT1-1 dim 11 target_concept: FEED_DIFFERENCE
- CX-LT1-1: engine candidate REJECTED (failed: IMPL-REWARD=CANON_MISMATCH, M1H-COND-04=UNRESOLVED_SPEC_AMBIGUITY, M1H-LOC-01=CANON_MISMATCH, M1H-OE-01=CANON_MISMATCH, M1H-OE-02=OWNER_BASELINE_CHOICE, M1H-OE-04a=FEED_DEPENDENT_SIGNAL_DIFFERENCE, M1H-OE-04b=UNRESOLVED_SPEC_AMBIGUITY)
- CX-LT3-2 dim 3 condition: UNRESOLVED_SPEC_AMBIGUITY
- CX-LT3-2 dim 4 tr_direction: UNRESOLVED_SPEC_AMBIGUITY
- CX-LT3-2 dim 7 previous_15m_take: CANON_MISMATCH
- CX-LT3-2 dim 9 shift_time: CANON_MISMATCH
- CX-LT3-2 dim 10 stop_anchor: FEED_DIFFERENCE
- CX-LT3-2 dim 11 target_concept: CANON_MISMATCH
- CX-LT3-2: engine candidate REJECTED (failed: M1H-6A-1-HVCS-INTO-SHIFT=UNRESOLVED_SPEC_AMBIGUITY, M1H-6A-2-PREV-15M-BROKEN-BY-Q=CANON_MISMATCH, M1H-6A-3-NEW-EXTREME-IN-Q=CANON_MISMATCH, M1H-COND-03=UNRESOLVED_SPEC_AMBIGUITY, M1H-COND-04=UNRESOLVED_SPEC_AMBIGUITY, M1H-OE-02=OWNER_BASELINE_CHOICE)
- CX-TE1-1 dim 4 tr_direction: UNRESOLVED_SPEC_AMBIGUITY
- CX-TE1-1 dim 9 shift_time: CANON_MISMATCH
- CX-TE1-1 dim 10 stop_anchor: FEED_DIFFERENCE
- CX-TE1-1 dim 11 target_concept: FEED_DIFFERENCE
- CX-TE1-1: engine candidate REJECTED (failed: M1H-COND-04=UNRESOLVED_SPEC_AMBIGUITY, M1H-OE-02=OWNER_BASELINE_CHOICE)

## 12. Verdict

**FAIL** (pending owner review; Phase 14 not started).

