# Phase 13C — PC3 Scored Behavioural Parity (CBR-RUN-013C-1)

**Protocol:** CBR-PROT-013C v1.1 · **Authorization:** owner ruling D31 · **Generated:** 2026-09-16T14:26:35+00:00

## Verdict: FAIL

**Failing requirements**

- entry-level hard dimension core_structural_trigger: 0/3 (CX-LT1-1, CX-TE1-1, CX-LT3-2)
- hour-level: 0/3 HOUR_MATCH (D31-8: 0/3 or 1/3 is a FAIL)

| Gate | Result |
|---|---|
| Entry-level hard dimensions (A-1) | model_family 3/3, direction 3/3, extension_direction 3/3, core_structural_trigger 0/3 |
| Hour-level (A-3, D31-8 threshold) | 0/3 HOUR_MATCH |
| Negative control CX-LT3-1 (A-4) | NO_ELIGIBLE_CANONICAL_SIGNAL |
| Determinism (A-5) | yes — `718efebdb12370e8…` |
| Frozen hashes | PC3 `7032f400688a…`, PC2 `4dadc8b99cc4…`, manifest `a3ee0bd6ba22…` (unchanged) |
| Pre-execution suite | 579 passed, 1 skipped in 61.19s (0:01:01) |

## Scoring convention used for the dimension table

Two readings are reported for every entry-level case, and only the strict one affects the verdict.

- **Strict (binds acceptance).** The structural event exists only if a D25-P3-equivalent candidate is also `ARMED_AT_TRIGGER` (mapping M-7). This is the core-trigger hard dimension in A-1 and it is applied exactly as frozen.
- **Descriptive (reporting only).** Dimensions 1-8 are read off the closest candidate the engine produced, eligible or not, so the table names the rule that actually rejected it instead of reporting all nine dimensions as mismatches whenever one gate fails. Dimension 9 is the eligibility dimension and stays strict.

This split was added during execution, after the first case showed a rejected-at-trigger candidate on the expected geometry. It changes what the report explains, not what passes: no threshold, dimension or acceptance rule was altered.

**Pre-flight disclosure.** Before the frozen run, the runner was executed once over all seven machine cases to check that it completes without raising, after the CBR-RUN-013B-1 crash. It wrote no scored output and changed neither PC3 nor any scoring rule; because every step is deterministic, its engine output is identical to the run reported here.

## CX-LT1-1 (positive, ENTRY_LEVEL)

Scored candidate: `CBR1H_BASELINE_V1-PC3/A/20251021T0100/BUY/3` (eligible: **no**)

| # | Dimension | Engine | Source | Status | Class |
|---|---|---|---|---|---|
| 1 | model_family | `"HVCS_S5_SHIFT"` | `"CBR1H"` | MATCH | — |
| 2 | direction | `"BUY"` | `"BUY"` | MATCH | — |
| 3 | condition | `{"cond_direction": "NONE", "condition": "RANGE", "fallback_applied": false}` | `[{"condition": "RANGE"}, {"condition": "TRENDING_RANGE"}]` | MATCH | — |
| 4 | extension_direction | `"DOWN"` | `"DOWN"` | MATCH | — |
| 5 | extension_activation | `{"activation_time": "2025-10-21T01:07:00+00:00", "state": "EXTENSION_ACTIVE"}` | `"EXTENSION_ACTIVE"` | MATCH | — |
| 6 | location_or_previous_candle_event | `{"failed_rules": [], "pos_oe_extreme": 0.0978879602439525, "q_break_by_q": true}` | `"location and previous-15m rules pass"` | MATCH | — |
| 7 | hvcs_state | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "indecision": 0.0, "minutes": 3.0, "state": false}` | `"valid at the shift for variant A; not applicable for variant B"` | MISMATCH | UNRESOLVED_SPEC_AMBIGUITY |
| 8 | type3_5s_structural_trigger | `{"reanchored": 1, "shift_time": "2025-10-21T01:39:35+00:00", "trigger_at_break": 4340.185, "trigger_at_decisio` | `{"rule": "D25-P3 equivalence", "tom_interval": ["2025-10-21T01:39:15+0` | MATCH | — |
| 9 | eligible_candidate | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-1-HVCS-INTO-SHIFT"]}` | `"ARMED_AT_TRIGGER"` | MISMATCH | UNRESOLVED_SPEC_AMBIGUITY |

Dimension 1 compares model *family*: the engine value is the variant's entry-model id, and the family is CBR1H in every case. Classes are the STEP 7 classifications, explained in the mismatch register below.

**Selection (D31-12).** Structural event exists (strict): **no**. D25-P3-equivalent candidates regardless of eligibility: 3. Frozen selection: 3. Classification: —.

| Variant | Candidates | Eligible | Frozen selection | Selection eligible |
|---|---|---|---|---|
| A | 5 | 0 | `3` | **no** |
| B | 0 | 0 | `—` | **no** |

## CX-TE1-1 (positive, ENTRY_LEVEL)

Scored candidate: `CBR1H_BASELINE_V1-PC3/A/20251024T0400/BUY/3` (eligible: **no**)

| # | Dimension | Engine | Source | Status | Class |
|---|---|---|---|---|---|
| 1 | model_family | `"HVCS_S5_SHIFT"` | `"CBR1H"` | MATCH | — |
| 2 | direction | `"BUY"` | `"BUY"` | MATCH | — |
| 3 | condition | `{"cond_direction": "UP", "condition": "RANGE", "fallback_applied": false}` | `[{"condition": "TRENDING_RANGE", "direction": "DOWN"}, {"condition": "` | MATCH | — |
| 4 | extension_direction | `"DOWN"` | `"DOWN"` | MATCH | — |
| 5 | extension_activation | `{"activation_time": "2025-10-24T04:07:00+00:00", "state": "EXTENSION_ACTIVE"}` | `"EXTENSION_ACTIVE"` | MATCH | — |
| 6 | location_or_previous_candle_event | `{"failed_rules": [], "pos_oe_extreme": -0.06001041395470852, "q_break_by_q": true}` | `"location and previous-15m rules pass"` | MATCH | — |
| 7 | hvcs_state | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "indecision": 1.0, "minutes": 2.0, "state": false}` | `"valid at the shift for variant A; not applicable for variant B"` | MISMATCH | UNRESOLVED_SPEC_AMBIGUITY |
| 8 | type3_5s_structural_trigger | `{"reanchored": 1, "shift_time": "2025-10-24T04:38:55+00:00", "trigger_at_break": 4105.5650000000005, "trigger_` | `{"rule": "D25-P3 equivalence", "tom_interval": ["2025-10-24T04:37:00+0` | MATCH | — |
| 9 | eligible_candidate | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-1-HVCS-INTO-SHIFT"]}` | `"ARMED_AT_TRIGGER"` | MISMATCH | UNRESOLVED_SPEC_AMBIGUITY |

Dimension 1 compares model *family*: the engine value is the variant's entry-model id, and the family is CBR1H in every case. Classes are the STEP 7 classifications, explained in the mismatch register below.

**Selection (D31-12).** Structural event exists (strict): **no**. D25-P3-equivalent candidates regardless of eligibility: 3. Frozen selection: 3. Classification: —.

| Variant | Candidates | Eligible | Frozen selection | Selection eligible |
|---|---|---|---|---|
| A | 4 | 0 | `3` | **no** |
| B | 0 | 0 | `—` | **no** |

## CX-LT3-2 (positive, ENTRY_LEVEL)

Scored candidate: `CBR1H_BASELINE_V1-PC3/A/20251110T0100/SELL/3` (eligible: **no**)

| # | Dimension | Engine | Source | Status | Class |
|---|---|---|---|---|---|
| 1 | model_family | `"HVCS_S5_SHIFT"` | `"CBR1H"` | MATCH | — |
| 2 | direction | `"SELL"` | `"SELL"` | MATCH | — |
| 3 | condition | `{"cond_direction": "NONE", "condition": "RANGE", "fallback_applied": true}` | `[{"condition": "TRENDING_RANGE", "direction": "UP"}]` | MISMATCH | OWNER_BASELINE_CHOICE |
| 4 | extension_direction | `"UP"` | `"UP"` | MATCH | — |
| 5 | extension_activation | `{"activation_time": "2025-11-10T01:10:00+00:00", "state": "EXTENSION_ACTIVE"}` | `"EXTENSION_ACTIVE"` | MATCH | — |
| 6 | location_or_previous_candle_event | `{"failed_rules": ["M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"], "pos_oe_extreme": 1.653665375` | `"location and previous-15m rules pass"` | MISMATCH | CANON_MISMATCH |
| 7 | hvcs_state | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "indecision": 0.0, "minutes": 0.0, "state": false}` | `"valid at the shift for variant A; not applicable for variant B"` | MISMATCH | UNRESOLVED_SPEC_AMBIGUITY |
| 8 | type3_5s_structural_trigger | `{"reanchored": 1, "shift_time": "2025-11-10T01:39:40+00:00", "trigger_at_break": 4050.9599999999996, "trigger_` | `{"rule": "D25-P3 equivalence", "tom_interval": ["2025-11-10T01:40:00+0` | MATCH | — |
| 9 | eligible_candidate | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-1-HVCS-INTO-SHIFT", "M1H-6A-2-` | `"ARMED_AT_TRIGGER"` | MISMATCH | UNRESOLVED_SPEC_AMBIGUITY |

Dimension 1 compares model *family*: the engine value is the variant's entry-model id, and the family is CBR1H in every case. Classes are the STEP 7 classifications, explained in the mismatch register below.

**Selection (D31-12).** Structural event exists (strict): **no**. D25-P3-equivalent candidates regardless of eligibility: 3. Frozen selection: 4. Classification: —.

| Variant | Candidates | Eligible | Frozen selection | Selection eligible |
|---|---|---|---|---|
| A | 6 | 0 | `4` | **no** |
| B | 0 | 0 | `—` | **no** |

## CX-LT3-1 (negative, ENTRY_LEVEL)

Window 2025-11-10 01:28:00+00:00 → 2025-11-10 01:36:00+00:00. **NO_ELIGIBLE_CANONICAL_SIGNAL**.

| Candidate | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|

No candidate at all had a 5s shift in the rejected window.
## JM-2025-10-16 (HOUR_LEVEL) — **HOUR_MISMATCH**

Journal row: 2025-10-16 11:41 AM (UTC+11) · TRR CT · Trending · CB 37 · LLTF (Seconds). Source level L1_FRAME_JOURNAL_TABLE (Tom's own record, no prices).

| Field | Engine | Source | Status |
|---|---|---|---|
| setup_exists_in_hour | `false` | `true` | MISMATCH |
| direction | `null` | `"SELL"` | MISMATCH |
| model_family | `null` | `"CBR1H (M-3: journal labels are not scored as subtypes)"` | MISMATCH |
| condition | `null` | `["TRENDING_RANGE", "RANGE"]` | MISMATCH |
| timing_bucket | `null` | `"CB 37 -> [30, 45) minutes"` | MISMATCH |

Eligible candidates in the hour: none.

| Candidate | Dir | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|
| `0` | BUY | None | NO_TRIGGER | IMPL-REWARD, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-COND-01, M1H-COND-02, M1H-OE-00-ACTIVE, M1H-OE-01, M1H-OE-04b |
| `0` | SELL | None | NO_TRIGGER | M1H-COND-01, M1H-COND-02, M1H-OE-01 |
| `1` | SELL | None | NO_TRIGGER | M1H-COND-01, M1H-COND-02 |
| `2` | SELL | 2025-10-16 00:41:20+00:00 | REJECTED_AT_TRIGGER | M1H-6A-1-HVCS-INTO-SHIFT, M1H-COND-01, M1H-COND-02 |
| `3` | SELL | None | NO_TRIGGER | IMPL-REWARD, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-COND-01, M1H-COND-02 |

## JM-2025-10-17 (HOUR_LEVEL) — **HOUR_MISMATCH**

Journal row: 2025-10-17 12:53 PM (UTC+11) · IFS · Volume · CB 52 · LLTF (Seconds) + LTF (1m). Source level L1_FRAME_JOURNAL_TABLE (Tom's own record, no prices).

| Field | Engine | Source | Status |
|---|---|---|---|
| setup_exists_in_hour | `false` | `true` | MISMATCH |
| direction | `null` | `"BUY"` | MISMATCH |
| model_family | `null` | `"CBR1H (M-3: journal labels are not scored as subtypes)"` | MISMATCH |
| condition | `null` | `"Volume (M-4: not scored)"` | NOT_SCORED |
| timing_bucket | `null` | `"CB 52 -> [45, 60) minutes"` | MISMATCH |

Eligible candidates in the hour: none.

| Candidate | Dir | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|
| `0` | BUY | None | NO_TRIGGER | IMPL-REWARD, M1H-LOC-01, M1H-OE-01 |
| `1` | BUY | 2025-10-17 01:30:25+00:00 | REJECTED_AT_TRIGGER | M1H-LOC-01, M1H-OE-01 |
| `2` | BUY | None | NO_TRIGGER | M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-LOC-01, M1H-OE-01 |
| `3` | BUY | 2025-10-17 01:46:35+00:00 | REJECTED_AT_TRIGGER | M1H-LOC-01 |
| `4` | BUY | None | NO_TRIGGER | M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q |

## JM-2025-10-29 (HOUR_LEVEL) — **HOUR_MISMATCH**

Journal row: 2025-10-29 7:14 PM (UTC+11) · TRR PT · Trending · CB 37 · LLTF (Seconds). Source level L1_FRAME_JOURNAL_TABLE (Tom's own record, no prices).

| Field | Engine | Source | Status |
|---|---|---|---|
| setup_exists_in_hour | `false` | `true` | MISMATCH |
| direction | `null` | `"BUY"` | MISMATCH |
| model_family | `null` | `"CBR1H (M-3: journal labels are not scored as subtypes)"` | MISMATCH |
| condition | `null` | `["TRENDING_RANGE", "RANGE"]` | MISMATCH |
| timing_bucket | `null` | `"CB 37 -> [30, 45) minutes"` | MISMATCH |

Eligible candidates in the hour: none.

| Candidate | Dir | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|
| `0` | SELL | None | NO_TRIGGER | M1H-OE-01, M1H-OE-04b |
| `1` | SELL | None | NO_TRIGGER | IMPL-REWARD, M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-OE-01, M1H-OE-04b |
| `2` | SELL | None | NO_TRIGGER | IMPL-REWARD, M1H-OE-01, M1H-OE-02, M1H-OE-04b |
| `3` | SELL | 2025-10-29 08:33:00+00:00 | REJECTED_AT_TRIGGER | M1H-6A-1-HVCS-INTO-SHIFT, M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-OE-01, M1H-OE-02, M1H-OE-04b |
| `4` | SELL | 2025-10-29 08:49:55+00:00 | REJECTED_AT_TRIGGER | IMPL-REWARD, M1H-6A-1-HVCS-INTO-SHIFT |
| `5` | SELL | None | NO_TRIGGER | — |

## Narrative / geometry set (never a machine pass count)

| Case | Assessment | Reason |
|---|---|---|
| CX-LT2-2 | CONSISTENT | PC3's geometry is sweep → break of the most recent opposing swing, which is exactly 'sell at the break of that low'. USDJPY has no data, so this is geometry only. |
| CX-LT2-1 | NOT_DETERMINABLE | The source rejects the setup on timing (~22 minutes in), and PC3 has no rule that encodes Tom's discretionary 'too early' judgement; no data to test. |
| T3-VP1-A | CONSISTENT | The drawn ranging type 3 takes the range high, then the range low, then shifts: PC3's sweep-then-break with a re-anchored trigger reproduces that ordering. |
| T3-VP1-B | CONSISTENT | The swept low is marked and extended as a level, then the reversal follows; PC3 treats the sweep extreme as the stop reference and the opposing swing as the trigger. |
| T3-VP2-HILO | CONSISTENT | The HILO lesson re-anchors its reference to the previous candle each candle, which is the evidence behind PC3's re-anchored trigger; the invalid example lacks the prior-candle break, which PC3 also rejects for lack of a confirmed opposing swing. |
| OE-GOOD-BAD | CONSISTENT | PC3 measures the deepest retracement against the whole active extension, so the 'didn't correct 50% at all' chart passes and the 'on average correcting 50%' chart fails, matching the lesson. |
| V15-SEM-2026-05 | NOT_DETERMINABLE | Illustrative CBR15 walkthrough with no stated entry; CBR15-PC3 is SPEC_ONLY and unscored (D30-3, D30-10). |

## Mismatch register (STEP 7)

| Case | Dimension | Class | Engine | Source |
|---|---|---|---|---|
| CX-LT1-1 | 7 hvcs_state | UNRESOLVED_SPEC_AMBIGUITY | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "indecision": 0.0, "minutes": 3.0` | `"valid at the shift for variant A; not applicable for varian` |
| CX-LT1-1 | 9 eligible_candidate | UNRESOLVED_SPEC_AMBIGUITY | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-` | `"ARMED_AT_TRIGGER"` |
| CX-TE1-1 | 7 hvcs_state | UNRESOLVED_SPEC_AMBIGUITY | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "indecision": 1.0, "minutes": 2.0` | `"valid at the shift for variant A; not applicable for varian` |
| CX-TE1-1 | 9 eligible_candidate | UNRESOLVED_SPEC_AMBIGUITY | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-` | `"ARMED_AT_TRIGGER"` |
| CX-LT3-2 | 3 condition | OWNER_BASELINE_CHOICE | `{"cond_direction": "NONE", "condition": "RANGE", "fallback_applied": true}` | `[{"condition": "TRENDING_RANGE", "direction": "UP"}]` |
| CX-LT3-2 | 6 location_or_previous_candle_event | CANON_MISMATCH | `{"failed_rules": ["M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"],` | `"location and previous-15m rules pass"` |
| CX-LT3-2 | 7 hvcs_state | UNRESOLVED_SPEC_AMBIGUITY | `{"failed_rules": ["M1H-6A-1-HVCS-INTO-SHIFT"], "indecision": 0.0, "minutes": 0.0` | `"valid at the shift for variant A; not applicable for varian` |
| CX-LT3-2 | 9 eligible_candidate | UNRESOLVED_SPEC_AMBIGUITY | `{"event_at_trigger": "REJECTED_AT_TRIGGER", "rules_failed_at_trigger": ["M1H-6A-` | `"ARMED_AT_TRIGGER"` |
| JM-2025-10-16 | setup_exists_in_hour | UNRESOLVED_SPEC_AMBIGUITY | `false` | `true` |
| JM-2025-10-16 | direction | UNRESOLVED_SPEC_AMBIGUITY | `null` | `"SELL"` |
| JM-2025-10-16 | model_family | UNRESOLVED_SPEC_AMBIGUITY | `null` | `"CBR1H (M-3: journal labels are not scored as subtypes)"` |
| JM-2025-10-16 | condition | UNRESOLVED_SPEC_AMBIGUITY | `null` | `["TRENDING_RANGE", "RANGE"]` |
| JM-2025-10-16 | timing_bucket | UNRESOLVED_SPEC_AMBIGUITY | `null` | `"CB 37 -> [30, 45) minutes"` |
| JM-2025-10-17 | setup_exists_in_hour | UNRESOLVED_SPEC_AMBIGUITY | `false` | `true` |
| JM-2025-10-17 | direction | UNRESOLVED_SPEC_AMBIGUITY | `null` | `"BUY"` |
| JM-2025-10-17 | model_family | UNRESOLVED_SPEC_AMBIGUITY | `null` | `"CBR1H (M-3: journal labels are not scored as subtypes)"` |
| JM-2025-10-17 | timing_bucket | UNRESOLVED_SPEC_AMBIGUITY | `null` | `"CB 52 -> [45, 60) minutes"` |
| JM-2025-10-29 | setup_exists_in_hour | CANON_MISMATCH | `false` | `true` |
| JM-2025-10-29 | direction | CANON_MISMATCH | `null` | `"BUY"` |
| JM-2025-10-29 | model_family | CANON_MISMATCH | `null` | `"CBR1H (M-3: journal labels are not scored as subtypes)"` |
| JM-2025-10-29 | condition | CANON_MISMATCH | `null` | `["TRENDING_RANGE", "RANGE"]` |
| JM-2025-10-29 | timing_bucket | CANON_MISMATCH | `null` | `"CB 37 -> [30, 45) minutes"` |

Taxonomy order applied: DATA_LIMITATION → FEED_DIFFERENCE → FEED_DEPENDENT_SIGNAL_DIFFERENCE → EXECUTION_DEPENDENT → OWNER_BASELINE_CHOICE → UNRESOLVED_SPEC_AMBIGUITY → IMPLEMENTATION_BUG → CANON_MISMATCH → CANDIDATE_SELECTION_MISMATCH.
By class: OWNER_BASELINE_CHOICE 1, UNRESOLVED_SPEC_AMBIGUITY 15, CANON_MISMATCH 6. Every mismatch is classified; none is unclassified.

**Why each class was assigned.** A rule whose failing quantity is a carried ASSUMPTION (D30-16) cannot be reported as a canon mismatch, because canon never fixed that quantity. A rule resting only on CANON-labelled parameters with a ruled-on reference instant is a canon mismatch.

For an HOUR_LEVEL case the class is taken across every same-direction candidate in the hour, at the least severe applicable class. That is deliberately the most forgiving reading: if any candidate in the right direction was blocked only by an assumption-dependent rule, the missing setup is reported as assumption-dependent rather than as a canon mismatch. Where the engine produced no candidate in the journal's direction at all, the class is CANON_MISMATCH.

| Blocking rule | Class | Reason |
|---|---|---|
| `M1H-COND-01` | UNRESOLVED_SPEC_AMBIGUITY | tradable-time condition window is a carried ASSUMPTION (D30-16) |
| `M1H-COND-02` | UNRESOLVED_SPEC_AMBIGUITY | same condition window assumption |
| `M1H-OE-00-ACTIVE` | UNRESOLVED_SPEC_AMBIGUITY | minute-7 earliest activation and the Q1 qualifier are ASSUMPTIONS (D29-16/17) |
| `M1H-OE-01` | UNRESOLVED_SPEC_AMBIGUITY | the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption |
| `M1H-OE-02` | CANON_MISMATCH | pullback_frac 0.50 is CANON and the whole-active-extension reference was approved in D29 |
| `M1H-OE-04a` | UNRESOLVED_SPEC_AMBIGUITY | two_sided_frac is an ASSUMPTION (OQ-08) |
| `M1H-OE-04b` | UNRESOLVED_SPEC_AMBIGUITY | oe min_size_atr is an ASSUMPTION (OQ-08) |
| `M1H-6A-1-HVCS-INTO-SHIFT` | UNRESOLVED_SPEC_AMBIGUITY | min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes |
| `M1H-6A-2-PREV-15M-BROKEN-BY-Q` | CANON_MISMATCH | previous-15m take is CANON and was not re-opened in PC3 |
| `M1H-6A-3-NEW-EXTREME-IN-Q` | CANON_MISMATCH | new-extreme-in-Q is CANON and was not re-opened in PC3 |
| `M1H-LOC-01` | CANON_MISMATCH | range_extreme 0.75 is CANON (E15-015, E1H-002) |
| `M1H-LOC-02` | CANON_MISMATCH | pro_er band is CANON (E1H-012, E15-015) |
| `M1H-LOC-03` | CANON_MISMATCH | counter-trend location is CANON |
| `IMPL-REWARD` | UNRESOLVED_SPEC_AMBIGUITY | the minimum reward ratio is an IMPL-labelled implementation rule, not canon |
| `NO_TRIGGER` | CANON_MISMATCH | no 5s type-3 shift was produced inside the entry window at all |

Reasons applied per case:

- **CX-LT1-1 / 7 hvcs_state** → UNRESOLVED_SPEC_AMBIGUITY: M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes
- **CX-LT1-1 / 9 eligible_candidate** → UNRESOLVED_SPEC_AMBIGUITY: M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes
- **CX-TE1-1 / 7 hvcs_state** → UNRESOLVED_SPEC_AMBIGUITY: M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes
- **CX-TE1-1 / 9 eligible_candidate** → UNRESOLVED_SPEC_AMBIGUITY: M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes
- **CX-LT3-2 / 3 condition** → OWNER_BASELINE_CHOICE: M-2: PC3's approved OQ-46 correction (D29-14) classifies this hour RANGE where D25-P6 named TRENDING_RANGE UP
- **CX-LT3-2 / 6 location_or_previous_candle_event** → CANON_MISMATCH: M1H-6A-2-PREV-15M-BROKEN-BY-Q — previous-15m take is CANON and was not re-opened in PC3; M1H-6A-3-NEW-EXTREME-IN-Q — new-extreme-in-Q is CANON and was not re-opened in PC3
- **CX-LT3-2 / 7 hvcs_state** → UNRESOLVED_SPEC_AMBIGUITY: M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes
- **CX-LT3-2 / 9 eligible_candidate** → UNRESOLVED_SPEC_AMBIGUITY: M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-16 / setup_exists_in_hour** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes; M1H-COND-01 — tradable-time condition window is a carried ASSUMPTION (D30-16); M1H-COND-02 — same condition window assumption; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-16 / direction** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes; M1H-COND-01 — tradable-time condition window is a carried ASSUMPTION (D30-16); M1H-COND-02 — same condition window assumption; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-16 / model_family** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes; M1H-COND-01 — tradable-time condition window is a carried ASSUMPTION (D30-16); M1H-COND-02 — same condition window assumption; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-16 / condition** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes; M1H-COND-01 — tradable-time condition window is a carried ASSUMPTION (D30-16); M1H-COND-02 — same condition window assumption; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-16 / timing_bucket** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-6A-1-HVCS-INTO-SHIFT — min_minutes = 4 is CANON, but neither the end anchor of the conforming run (PC3 ends it at the extension-extreme bar) nor whether the first candle of the sequence is counted was ever ruled on; measured runs were 3, 2 and 0 minutes; M1H-COND-01 — tradable-time condition window is a carried ASSUMPTION (D30-16); M1H-COND-02 — same condition window assumption; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-17 / setup_exists_in_hour** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-17 / direction** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-17 / model_family** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-17 / timing_bucket** → UNRESOLVED_SPEC_AMBIGUITY: IMPL-REWARD — the minimum reward ratio is an IMPL-labelled implementation rule, not canon; M1H-OE-01 — the 20-minute minimum is CANON but is measured from the assumed activation instant, so the failure is inseparable from the minute-7 assumption
- **JM-2025-10-29 / setup_exists_in_hour** → CANON_MISMATCH: the engine produced no BUY candidate at all in the hour
- **JM-2025-10-29 / direction** → CANON_MISMATCH: the engine produced no BUY candidate at all in the hour
- **JM-2025-10-29 / model_family** → CANON_MISMATCH: the engine produced no BUY candidate at all in the hour
- **JM-2025-10-29 / condition** → CANON_MISMATCH: the engine produced no BUY candidate at all in the hour
- **JM-2025-10-29 / timing_bucket** → CANON_MISMATCH: the engine produced no BUY candidate at all in the hour

## Concerns

- CX-LT1-1 dim 7 hvcs_state: CANON_MISMATCH
- CX-LT1-1 dim 9 eligible_candidate: CANON_MISMATCH
- CX-TE1-1 dim 7 hvcs_state: CANON_MISMATCH
- CX-TE1-1 dim 9 eligible_candidate: CANON_MISMATCH
- CX-LT3-2 dim 3 condition: CANON_MISMATCH — M-2: PC3 follows the approved OQ-46 correction (D29-14) while D25-P6 names the accepted set
- CX-LT3-2 dim 6 location_or_previous_candle_event: CANON_MISMATCH
- CX-LT3-2 dim 7 hvcs_state: CANON_MISMATCH
- CX-LT3-2 dim 9 eligible_candidate: CANON_MISMATCH
- JM-2025-10-16 setup_exists_in_hour: engine False vs source True
- JM-2025-10-16 direction: engine None vs source SELL
- JM-2025-10-16 model_family: engine None vs source CBR1H (M-3: journal labels are not scored as subtypes)
- JM-2025-10-16 condition: engine None vs source ['TRENDING_RANGE', 'RANGE']
- JM-2025-10-16 timing_bucket: engine None vs source CB 37 -> [30, 45) minutes
- JM-2025-10-17 setup_exists_in_hour: engine False vs source True
- JM-2025-10-17 direction: engine None vs source BUY
- JM-2025-10-17 model_family: engine None vs source CBR1H (M-3: journal labels are not scored as subtypes)
- JM-2025-10-17 timing_bucket: engine None vs source CB 52 -> [45, 60) minutes
- JM-2025-10-29 setup_exists_in_hour: engine False vs source True
- JM-2025-10-29 direction: engine None vs source BUY
- JM-2025-10-29 model_family: engine None vs source CBR1H (M-3: journal labels are not scored as subtypes)
- JM-2025-10-29 condition: engine None vs source ['TRENDING_RANGE', 'RANGE']
- JM-2025-10-29 timing_bucket: engine None vs source CB 37 -> [30, 45) minutes

## Limits of this run (CBR-PROT-013C §9)

- Machine set: {'ENTRY_LEVEL': 4, 'HOUR_LEVEL': 3, 'NARRATIVE_ONLY': 7} — XAUUSD only, CBR1H only.
- The three HOUR_LEVEL cases come from Tom's journal table in a Level-1 frame and carry no prices.
- CBR15-PC3 is SPEC_ONLY and unscored.
- `k = 3` is fixed; CX-LT3-2's trigger is known to disappear at `k = 4`.
- PC3 carries six unresolved assumptions; passing parity would not convert any of them into CANON.
- No P&L, fills or trade outcomes were read at any point in this run.

## Stop

Phase 13C is complete and execution stops here. Phase 14 is not started, PC3 is unchanged since the freeze, and no corrective run has been launched.
