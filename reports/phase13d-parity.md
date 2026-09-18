# Phase 13D — PC4 Scored Behavioural Parity (CBR-RUN-013D-1)

**Protocol:** CBR-PROT-013D v1.1 · **Authorization:** owner ruling D35 · **Generated:** 2026-09-18T01:19:46+00:00

## Verdict: FAIL

**Failing requirements**

- entry-level hard dimension hvcs_state: 2/3 (CX-LT3-2)
- entry-level hard dimension eligible_candidate: 2/3 (CX-LT3-2)

| Gate | Result |
|---|---|
| Entry-level hard dimensions (D-1) | model_family 3/3, direction 3/3, extension_direction 3/3, extension_activation 3/3, location_or_previous_candle_event 3/3, hvcs_state 2/3, type3_5s_structural_trigger 3/3, eligible_candidate 2/3 |
| Hour-level (D-3, E-2 threshold) | 0/1 HOUR_MATCH |
| Negative control CX-LT3-1 (D-4) | NO_ELIGIBLE_CANONICAL_SIGNAL |
| Determinism (D-5) | yes — `361232f6f20d6346…` |
| Frozen hashes | PC4 `62a2310e43d7…`, manifest `e12f3882f01b…`, PC3 `7032f400688a…`, PC2 `4dadc8b99cc4…` (all unchanged) |
| Pre-execution suite | 647 passed, 1 skipped in 66.34s (0:01:06) |
| Pre-freeze real-case smoke run (D35 §8) | NONE — every PC4 invocation before this freeze is in tests/engine/test_cbr1h_pc4.py against a synthetic random walk (D35 §8) |

## Strict and descriptive views (pre-declared, D35 §6)

**STRICT** scores only eligible candidates and is the only view that touches acceptance. **DESCRIPTIVE** shows the closest structurally relevant candidate so the report can name the rule that blocked it; it can never satisfy acceptance. Each case below states which view its scored row came from.

## CX-LT1-1 (positive, ENTRY_LEVEL) — view: STRICT

Scored candidate: `CBR1H_BASELINE_V1-PC4/A/20251021T0100/BUY/3` (eligible: yes)

| # | Dimension | Hard | Engine | Source | Status | Class |
|---|---|---|---|---|---|---|
| 1 | model_family | yes | `"HVCS_S5_SHIFT"` | `"CBR1H"` | MATCH | — |
| 2 | direction | yes | `"BUY"` | `"BUY"` | MATCH | — |
| 3 | condition | no | `{"cond_direction": "NONE", "condition": "RANGE", "fallback_applied": false}` | `[{"condition": "RANGE"}, {"condition": "TRENDING_RANGE"}]` | MATCH | — |
| 4 | extension_direction | yes | `"DOWN"` | `"DOWN"` | MATCH | — |
| 5 | extension_activation | yes | `{"activation_time": "2025-10-21T01:07:00+00:00", "state": "EXTENSION_ACTIVE"}` | `"EXTENSION_ACTIVE"` | MATCH | — |
| 6 | location_or_previous_candle_event | yes | `{"failed_rules": [], "pos_oe_extreme": 0.0978879602439525, "q_break_by_q_at_trigger": null}` | `"location and previous-15m rules pass at the shift (F-9)"` | MATCH | — |
| 7 | hvcs_state | yes | `{"failed_rules": [], "minutes": 6.0, "state": true, "to_shift_diagnostic": null, "violations": null}` | `"valid at the shift for variant A; not applicable for varian` | MATCH | — |
| 8 | type3_5s_structural_trigger | yes | `{"reanchored": 1, "shift_time": "2025-10-21T01:39:35+00:00", "trigger_at_break": 4340.185, "trigger_` | `{"rule": "D25-P3 equivalence", "tom_interval": ["2025-10-21T` | MATCH | — |
| 9 | eligible_candidate | yes | `{"event_at_trigger": "ARMED_AT_TRIGGER", "rules_failed_at_trigger": []}` | `"ARMED_AT_TRIGGER"` | MATCH | — |

**Selection (D35 §6).** A — expected structural event exists: yes. B — eligible expected event exists: yes. C — frozen selector chose: 3. Classification: —.

| Variant | Candidates | Eligible | Frozen selection | Selection eligible |
|---|---|---|---|---|
| A | 5 | 1 | `3` | yes |
| B | 0 | 0 | `—` | **no** |

## CX-TE1-1 (positive, ENTRY_LEVEL) — view: STRICT

Scored candidate: `CBR1H_BASELINE_V1-PC4/A/20251024T0400/BUY/3` (eligible: yes)

| # | Dimension | Hard | Engine | Source | Status | Class |
|---|---|---|---|---|---|---|
| 1 | model_family | yes | `"HVCS_S5_SHIFT"` | `"CBR1H"` | MATCH | — |
| 2 | direction | yes | `"BUY"` | `"BUY"` | MATCH | — |
| 3 | condition | no | `{"cond_direction": "UP", "condition": "RANGE", "fallback_applied": false}` | `[{"condition": "TRENDING_RANGE", "direction": "DOWN"}, {"con` | MATCH | — |
| 4 | extension_direction | yes | `"DOWN"` | `"DOWN"` | MATCH | — |
| 5 | extension_activation | yes | `{"activation_time": "2025-10-24T04:07:00+00:00", "state": "EXTENSION_ACTIVE"}` | `"EXTENSION_ACTIVE"` | MATCH | — |
| 6 | location_or_previous_candle_event | yes | `{"failed_rules": [], "pos_oe_extreme": -0.06001041395470852, "q_break_by_q_at_trigger": null}` | `"location and previous-15m rules pass at the shift (F-9)"` | MATCH | — |
| 7 | hvcs_state | yes | `{"failed_rules": [], "minutes": 4.0, "state": true, "to_shift_diagnostic": null, "violations": null}` | `"valid at the shift for variant A; not applicable for varian` | MATCH | — |
| 8 | type3_5s_structural_trigger | yes | `{"reanchored": 1, "shift_time": "2025-10-24T04:38:55+00:00", "trigger_at_break": 4105.5650000000005,` | `{"rule": "D25-P3 equivalence", "tom_interval": ["2025-10-24T` | MATCH | — |
| 9 | eligible_candidate | yes | `{"event_at_trigger": "ARMED_AT_TRIGGER", "rules_failed_at_trigger": []}` | `"ARMED_AT_TRIGGER"` | MATCH | — |

**Selection (D35 §6).** A — expected structural event exists: yes. B — eligible expected event exists: yes. C — frozen selector chose: 3. Classification: —.

| Variant | Candidates | Eligible | Frozen selection | Selection eligible |
|---|---|---|---|---|
| A | 4 | 1 | `3` | yes |
| B | 0 | 0 | `—` | **no** |

## CX-LT3-2 (positive, ENTRY_LEVEL) — view: DESCRIPTIVE

Scored candidate: `CBR1H_BASELINE_V1-PC4/A/20251110T0100/SELL/3` (eligible: **no**)

| # | Dimension | Hard | Engine | Source | Status | Class |
|---|---|---|---|---|---|---|
| 1 | model_family | yes | `"HVCS_S5_SHIFT"` | `"CBR1H"` | MATCH | — |
| 2 | direction | yes | `"SELL"` | `"SELL"` | MATCH | — |
| 3 | condition | no | `{"cond_direction": "NONE", "condition": "RANGE", "fallback_applied": true}` | `[{"condition": "TRENDING_RANGE", "direction": "UP"}]` | MISMATCH | OWNER_BASELINE_CHOICE |
| 4 | extension_direction | yes | `"UP"` | `"UP"` | MATCH | — |
| 5 | extension_activation | yes | `{"activation_time": "2025-11-10T01:10:00+00:00", "state": "EXTENSION_ACTIVE"}` | `"EXTENSION_ACTIVE"` | MATCH | — |
| 6 | location_or_previous_candle_event | yes | `{"failed_rules": [], "pos_oe_extreme": 1.6536653758846294, "q_break_by_q_at_trigger": null}` | `"location and previous-15m rules pass at the shift (F-9)"` | MATCH | — |
| 7 | hvcs_state | yes | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "minutes": 0.0, "state": false, "to_shift_diagnostic"` | `"valid at the shift for variant A; not applicable for varian` | MISMATCH | CANON_MISMATCH |
| 8 | type3_5s_structural_trigger | yes | `{"reanchored": 1, "shift_time": "2025-11-10T01:39:40+00:00", "trigger_at_break": 4050.9599999999996,` | `{"rule": "D25-P3 equivalence", "tom_interval": ["2025-11-10T` | MATCH | — |
| 9 | eligible_candidate | yes | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-1-HVCS-INTO-SHIFT", ` | `"ARMED_AT_TRIGGER"` | MISMATCH | CANON_MISMATCH |

**Selection (D35 §6).** A — expected structural event exists: yes. B — eligible expected event exists: **no**. C — frozen selector chose: 4. Classification: —.

| Variant | Candidates | Eligible | Frozen selection | Selection eligible |
|---|---|---|---|---|
| A | 6 | 0 | `4` | **no** |
| B | 0 | 0 | `—` | **no** |

## CX-LT3-1 (negative, ENTRY_LEVEL) — view: STRICT

Window 2025-11-10 01:28:00+00:00 → 2025-11-10 01:36:00+00:00. **NO_ELIGIBLE_CANONICAL_SIGNAL**.

| Candidate | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|
| — | — | — | no candidate of any kind had a 5s shift in the rejected window |

## JM-2025-10-16 (HOUR_LEVEL) — **HOUR_MISMATCH**

Journal row: 2025-10-16 11:41 AM (UTC+11) · TRR CT · Trending · CB 37 · LLTF (Seconds). Source level L1_FRAME_JOURNAL_TABLE, model_scope CONFIRMED_CBR1H.

| Field | Engine | Source | Status |
|---|---|---|---|
| setup_exists_in_hour | `false` | `true` | MISMATCH |
| direction | `null` | `"SELL"` | MISMATCH |
| model_family | `null` | `"CBR1H (journal labels are not scored as subtypes)"` | MISMATCH |
| condition | `null` | `["TRENDING_RANGE", "RANGE"]` | MISMATCH |
| timing_bucket | `null` | `"CB 37 -> [30, 45) minutes"` | MISMATCH |

Eligible candidates in the hour: none.

| Candidate | Dir | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|
| `0` | BUY | None | NO_TRIGGER | IMPL-REWARD, M1H-COND-01, M1H-COND-02, M1H-OE-00-ACTIVE, M1H-OE-01, M1H-OE-04b |
| `0` | SELL | None | NO_TRIGGER | M1H-COND-01, M1H-COND-02, M1H-OE-01 |
| `1` | SELL | None | NO_TRIGGER | M1H-COND-01, M1H-COND-02 |
| `2` | SELL | 2025-10-16 00:41:20+00:00 | REJECTED_AT_TRIGGER | M1H-6A-1-HVCS-INTO-SHIFT, M1H-COND-01, M1H-COND-02 |
| `3` | SELL | None | NO_TRIGGER | IMPL-REWARD, M1H-COND-01, M1H-COND-02 |

## Mismatch register

| Case | Dimension | Hard | Class | Engine | Source |
|---|---|---|---|---|---|
| CX-LT3-2 | 3 condition | no | OWNER_BASELINE_CHOICE | `{"cond_direction": "NONE", "condition": "RANGE", "fallback_applied": t` | `[{"condition": "TRENDING_RANGE", "direction": "UP"` |
| CX-LT3-2 | 7 hvcs_state | yes | CANON_MISMATCH | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "minutes": 0.0, "state"` | `"valid at the shift for variant A; not applicable ` |
| CX-LT3-2 | 9 eligible_candidate | yes | CANON_MISMATCH | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger":` | `"ARMED_AT_TRIGGER"` |
| JM-2025-10-16 | setup_exists_in_hour | no | CANON_MISMATCH | `false` | `true` |
| JM-2025-10-16 | direction | no | CANON_MISMATCH | `null` | `"SELL"` |
| JM-2025-10-16 | model_family | no | CANON_MISMATCH | `null` | `"CBR1H (journal labels are not scored as subtypes)` |
| JM-2025-10-16 | condition | no | CANON_MISMATCH | `null` | `["TRENDING_RANGE", "RANGE"]` |
| JM-2025-10-16 | timing_bucket | no | CANON_MISMATCH | `null` | `"CB 37 -> [30, 45) minutes"` |

Taxonomy order: DATA_LIMITATION → FEED_DIFFERENCE → FEED_DEPENDENT_SIGNAL_DIFFERENCE → EXECUTION_DEPENDENT → OWNER_BASELINE_CHOICE → UNRESOLVED_SPEC_AMBIGUITY → IMPLEMENTATION_BUG → CANON_MISMATCH → CANDIDATE_SELECTION_MISMATCH → PARITY_SET_CORRECTION.
Every mismatch has exactly one primary classification; none is unclassified.

## Concerns

- CX-LT3-2 dim 3 condition: OWNER_BASELINE_CHOICE — PC4 keeps PC3's approved OQ-46 correction; D25-P6 named the accepted set
- JM-2025-10-16: HOUR_MISMATCH — caps the verdict at PASS WITH CONCERNS (E-2)
- JM-2025-10-16 setup_exists_in_hour: engine False vs source True
- JM-2025-10-16 direction: engine None vs source SELL
- JM-2025-10-16 model_family: engine None vs source CBR1H (journal labels are not scored as subtypes)
- JM-2025-10-16 condition: engine None vs source ['TRENDING_RANGE', 'RANGE']
- JM-2025-10-16 timing_bucket: engine None vs source CB 37 -> [30, 45) minutes

## Limits of this run (CBR-PROT-013D §11)

- Binding machine set: 4 ENTRY_LEVEL + 1 HOUR_LEVEL — XAUUSD only, CBR1H only.
- The hour-level evidence is a **single** case, weaker than the three D31 used.
- CBR15-PC4 is SPEC_ONLY and unscored; FS/IFS contexts are not implemented.
- `k = 3` is fixed; CX-LT3-2's trigger is known to disappear at `k = 4`.
- PC4 carries the OQ-48 anchor/counting/unit, minute-7 activation, the Q1 qualifier, k = 3, the tradable-time window, the extension origin and the F-10 Q interpretation as **assumptions**. A PASS does not promote any of them into CANON.
- No P&L, fills or trade outcomes were read at any point.

## Stop

Phase 13D is complete and execution stops here. PC4 is unchanged since the freeze, no corrective run was launched, and Phase 14 is not started.
