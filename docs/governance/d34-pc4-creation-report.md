# D34 — PC4 creation completion report

**Doc:** CBR-RPT-034 · **Date:** 2026-09-17 · **Ruling:** D34 §19 · **Status:** returned for owner review
PC4 created and frozen. **PC4 is not scored.** No Phase 13 rerun · no Phase 14 · no backtest · no optimization ·
no P&L or trade outcome · no Backtesting.py · no Astra × Fable review.

---

## 1. PC3 → PC4 change summary

Three behavioural changes, one documentation change, and explicit no-changes. Nothing else moved.

| Id | Change | Classification | Ruling |
|---|---|---|---|
| **F-1** | The HVCS conforming run applies the configured `hvcs.max_violations = 1` again (`structure/shifts_pc4.py`). PC2 applied it; PC3 stopped without a ruling. Value unchanged and untested at other values | **IMPLEMENTATION_FIX** | D34 §2 |
| **F-9** | `M1H-6A-2-PREV-15M-BROKEN-BY-Q` and `M1H-6A-3-NEW-EXTREME-IN-Q` — and **only** those two — are evaluated at the final canonical 5s shift instead of at the type-3 arm | **CANON_CORRECTION** | D34 §5 |
| **F-10** | For those two rules, `Q` = the 15m candle containing the final shift, `Q−1` = the previous completed candle, judged only from bars closed at or before the shift decision instant | **ASSUMPTION** | D34 §6 |
| **F-11** | The OQ-48 anchor, counting convention and unit are recorded as explicit ASSUMPTIONS in `config/strategy_pc4.yaml`; OQ-48 stays UNRESOLVED_SPEC_AMBIGUITY | **ASSUMPTION_CHANGE** | D34 §4 |
| **A-1** | HVCS endpoint stays the extension extreme. `HVCS_TO_SHIFT` is computed as `hvcs_to_shift_minutes` and never gates anything | **NO_CHANGE** | D34 §3 |
| **A-2** | Type-3 re-anchoring, sweep-extreme timer, whole-extension pullback, PRE_EXTENSION/EXTENSION_ACTIVE, minute-7 activation, Q1 qualifier, HOUR_OPEN, k = 3, directionless trending range → RANGE, candidate selection, tradable-time window, prior-setup gate removal | **NO_CHANGE** | D34 §13 |
| **A-3** | Every `M1H-LOC-*`, `M1H-OE-*` and `M1H-COND-*` evaluation instant | **NO_CHANGE** | D34 §5 |

Guarded by `test_the_approved_change_set_is_exactly_what_d34_authorized`, which fails if the behavioural set is ever
anything other than {F-1, F-9, F-10}, and by `test_f9_scope_is_exactly_two_rules`.

## 2. PC4 spec hash

```
62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7
```

Records: `docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC4.yaml` (IMPLEMENTED) and
`CBR15_BASELINE_V1-PC4.yaml` (SPEC_ONLY, unchanged from PC3 — CBR15 has no `hvcs` block, and the previous-15m
correction is a CBR1H Variant-A path that is not transferred by analogy).

## 3. Proof PC2 is unchanged

`spec_hash() = 4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2` — identical to the value
CBR-RUN-013B-2 and CBR-RUN-013C-1 were frozen against. Asserted by `test_pc2_and_pc3_remain_byte_identical` and by
the pre-existing PC2 record guard.

## 4. Proof PC3 is unchanged

`spec_hash_pc3() = 7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453` — identical to the value
CBR-RUN-013C-1 was scored under. PC4 is additive: `shifts_pc3.py`, `cbr1h_pc3.py`, `overextension_pc3.py`,
`condition_pc3.py`, `params_pc3.py` and `config/strategy_pc3.yaml` are untouched, and the PC3 record's own guard
still passes. The CBR-RUN-013C-1 freeze manifest also still verifies.

## 5. F-1 implementation

`src/cbr/structure/shifts_pc4.py` → `hvcs_structural_pc4(..., max_violations)`. The keyword is **required**, so no
call site can silently drop it again — the defect that produced this whole cycle. Conformity is PC3's (structural
respect only; close direction irrelevant; indecision and opposing-close candles inside the run). A run may not start
on a violation; a tolerated violation inside the run is counted, as PC2 counted it; the walk stops when the
tolerance is exceeded. `HvcsPC4` adds a `violations` diagnostic. Wired at `cbr1h_pc4.py::_hvcs_at`, which also
records `hvcs_to_shift_minutes` as the D34 §3 diagnostic.

## 6. OQ-50 implementation

`cbr1h_pc4.py::_prev_15m_at_shift()`. At the decision instant both rules are written as `None` — they never enter
the decision ledger, exactly as D29-11 did for HVCS — and PC3's decision-time verdicts are kept as
`prev_15m_broken_at_decision` and `new_extreme_in_q_at_decision` diagnostics so the change is visible in the ledger.
At the trigger, `Q = shift.floor("15min")`, `Q−1` the previous completed candle, and both the previous-15m break and
the extension extreme are read at `shift + 5s` — the shift bar's close, which is when the signal exists. Nothing
later inside `Q` is read.

## 7. F-9 / F-10 / F-11 implementation

Implemented exactly as classified in D33 and approved in D34, with no scope expansion: F-9 covers two rules, F-10
defines `Q` for those two rules only, F-11 is documentation in `config/strategy_pc4.yaml`. No additional strategy
interpretation was required, so nothing was returned for owner review under D34 §8.

## 8. Corrected parity-set inventory

`research/examples/parity_set_manifest_v2.json`. The v1 manifest is untouched and still hashes to `a3ee0bd6…`.

| Class | Cases |
|---|---|
| **Binding ENTRY_LEVEL (4)** | CX-LT1-1, CX-TE1-1, CX-LT3-2 (positive) · CX-LT3-1 (negative) |
| **Binding HOUR_LEVEL (1)** | JM-2025-10-16 — `CONFIRMED_CBR1H` (TRR CT), dating corroborated inside the frozen hour |
| **NARRATIVE_ONLY (11)** | JM-2025-10-17 (`IFS_NOT_IMPLEMENTED`, preserved for its future model) · JM-2025-10-29 (`SOURCE_AMBIGUITY`, preserved with its ambiguity record) · HX-1, HX-2 (OQ-48 evidence, never binding) · the seven original narrative cases |

Every binding case carries `case_id`, `source`, `evidence_level`, `model_scope`, `direction`,
`positive_or_negative`, `scoring_level`, `source_supported_fields`, `market_data_hashes` and `evidence_hashes`, and
`model_scope = CONFIRMED_CBR1H` is enforced by test.

## 9. Parity-set manifest hash

```
e12f3882f01b8ac4655520f00d5cd19829da989a371a1feb15b070d1a718804e
```

## 10. Tests added

50 new tests in three files, synthetic fixtures only:

| File | Tests | Covers |
|---|---|---|
| `tests/engine/test_cbr1h_pc4.py` | 32 | F-1 A-F (zero / one / two violations, close direction irrelevant, causal counting, determinism, UP mirror, run may not start on a violation, zero-tolerance reproduces PC3) · OQ-50 boundary cases A-E · the decision/trigger split · truncation and future-mutation causality · price-role guard · parameter and variant checks |
| `tests/engine/test_parity_candidate_specs_pc4.py` | 9 | the frozen record, the pinned file set, PC2/PC3 immutability, the exact approved change set, F-9's two-rule scope, OQ-48 kept visible |
| `tests/engine/test_parity_set_manifest_v2.py` | 9 | manifest freeze, required fields, `CONFIRMED_CBR1H` binding rule, preserved (not deleted) journal cases, HX-1/HX-2 never binding, pinned-file integrity |

No scored parity case is used as a development test (D34 §15).

## 11. Total tests passing

**633 passed, 1 skipped** (was 583 + 1 before PC4). `ruff check src tests` clean.

## 12. Causality results

- HVCS: `hvcs_structural_pc4(bars[:t], t, …) == hvcs_structural_pc4(bars, t, …)` for every `t`, including when a
  later bar would be a violation.
- Previous-15m: mutating every bar after the shift leaves both rules' verdicts unchanged; a take that occurs later
  inside `Q` does **not** retroactively validate the signal (boundary case E), while the same data with a later
  shift does satisfy it.
- Engine: decision-frame records under truncation at a mid-minute cut, and under a ×1.03 mutation of every bar after
  that cut, are identical to the untruncated run.
- The two moved rules are `None` in every decision ledger row and `True`/`False` at the trigger.

## 13. Determinism results

`result_hash` identical across repeat runs of the synthetic 8-hour window; `hvcs_structural_pc4` returns an identical
frozen dataclass across repeated evaluation; `spec_hash_pc4()` stable across calls.

## 14. Proposed CBR-PROT-013D

`docs/governance/phase13d-pc4-parity-protocol.md` — **drafted, not run.** Defines the five binding machine cases,
the entry-level and hour-level dimensions, the pre-declared strict/descriptive two-layer reporting, the mismatch
taxonomy, negative-control handling, candidate-selection handling, acceptance rules D-1…D-7, carried assumptions,
prohibitions and execution order.

**It asks one substantive question:** with only **one** binding hour-level case (D31 had three), what is the D-3
threshold? The draft proposes 1/1 for a clean PASS and 0/1 capping at PASS WITH CONCERNS rather than failing the
run, on the grounds that a single case is too thin to carry a FAIL alone. That is a change from D31's rule and needs
an explicit owner decision (E-2).

## 15. Exact remaining assumptions

1. **OQ-48 anchor** — the run ends at the extension-extreme bar known at the shift.
2. **OQ-48 counting** — the first candle of the sequence is the reference and is not counted.
3. **OQ-48 unit** — a count of completed 1m candles, not elapsed time.
4. **F-10 boundary** — `Q` follows the shift, so a shift early in a new 15m candle moves `Q`.
5. **Minute-7** earliest activation; **Q1** qualifier; **extension origin** = most adverse price before activation.
6. **ATR zig-zag k = 3** (OQ-01; CX-LT3-2's trigger disappears at k = 4).
7. **Tradable-time** condition window.
8. **FS / IFS** middle-timeframe contexts are not implemented (OQ-51).

Passing parity would convert none of these into CANON.

## 16. Exact blockers before scoring

| # | Blocker |
|---|---|
| 1 | **PC4 scoring is not authorized** (D34 §18) |
| 2 | **CBR-PROT-013D is not approved** — decisions E-1…E-5, in particular the D-3 hour-level threshold (E-2) |
| 3 | **The corrected parity set is not confirmed as the scoring set** (E-3) — it is built and frozen, but only the owner can make it the binding set |
| 4 | No freeze manifest exists for a 013D run, and no run id has been issued |

None of these is research. All four are owner decisions.

## 17. Readiness verdict

### PC4 IS NOT READY FOR SCORED PARITY APPROVAL — it is ready for *protocol* approval.

The candidate itself is complete, frozen, tested and reproducible: every approved change is implemented and
classified, PC2 and PC3 are provably untouched, causality and determinism hold, and the corrected parity set exists
with the required fields. What is missing is not engineering. PC4 cannot be scored until the owner approves
CBR-PROT-013D, settles the one-case hour-level threshold, and confirms the corrected set — at which point the run
can be frozen and executed in one pass.

## 18. Stop

PC4 is not scored. Phase 14 is not started. Returned for owner review.
