# F-1 implementation plan — restore `hvcs.max_violations = 1`

**Doc:** CBR-PLAN-F1 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D33 §1, §15
**Classification:** **IMPLEMENTATION_FIX** (restores configured, inherited behaviour; introduces no new behaviour)
**Status:** PLAN ONLY. Nothing in this document has been applied. **PC3 is not modified** (D33 §15): the change
belongs to the next candidate, and PC3's spec hash `7032f400…` stays valid.

---

## 1. Where the defect is

| | |
|---|---|
| **File / function** | `src/cbr/structure/shifts_pc3.py` → `hvcs_structural(bars_1m, end_time, direction, *, atr_1m, min_minutes, lvcs_body_atr)` |
| **Caller** | `src/cbr/engine/cbr1h_pc3.py:248`, inside `_hvcs_at()` |
| **Current PC3 behaviour** | the backwards walk `break`s at the **first** candle that fails `high ≤ previous high` (DOWN) / `low ≥ previous low` (UP). No violation is tolerated. The docstring says "No maximum count is imposed", which refers to the run's *length*, not to violations |
| **Correct inherited behaviour** | PC2's `hvcs()` (`src/cbr/structure/shifts.py:179-198`) tolerates up to `max_violations` non-conforming candles inside the run, counts the violating candle itself, and breaks when the count is exceeded. `hvcs.max_violations = 1`, label `ASSUMPTION`, source OQ-08, in `config/strategy.yaml` |
| **What D29-10 actually ruled** | remove the `close < open` requirement (H-1) and allow the run to end on the extreme bar (H-2). It did **not** rule on the violation tolerance; the PC3 spec record still describes the PC2 baseline as "(max 1 violation)" |
| **Value** | `1`. **Not to be changed and not to be tested at other values** (D33 §1) |

## 2. The change

1. Add a required keyword `max_violations: int` to `hvcs_structural()` and implement PC2's counting semantics on top
   of PC3's conformity test (structural respect only; close direction still irrelevant; indecision still counted
   separately into `indecision_bars`).
2. Pass `max_violations=p.hvcs_max_violations` at `cbr1h_pc3.py:248`. The parameter is already loaded on
   `Cbr1hPC3Params` through its `__getattr__` delegation to the PC2 params — no new plumbing.
3. Record the violation count on `HvcsPC3` (a new `violations: int` field) so the ledger can report it as a
   diagnostic, the way `indecision_bars` already is.
4. Keep the walk otherwise identical: a run may not *start* on a violation, the violating candle is counted, and the
   verdict is `length >= min_minutes` with `min_minutes = 4` unchanged.

Making the keyword **required** is deliberate: it forces every call site to state the value, so the parameter cannot
be silently dropped again.

## 3. Test changes (D33 §1 A-F)

New synthetic tests — no market data, no parity case, per D33 §18:

| | Requirement | Test |
|---|---|---|
| A | zero violations passes | a clean 5-candle run with `max_violations=1` measures 5 and is valid at `min_minutes=4` |
| B | one structural violation may pass | a 9-candle run containing exactly one higher high measures 9 and is valid — the HX-1 / HX-2 shape, built synthetically |
| C | two violations fail | the same run with a second violation stops at it, measures below 4 and is invalid |
| D | close direction stays irrelevant | a run whose candles close against the direction but respect the side measures identically to one that closes with it; `indecision_bars` differs, `minutes` does not |
| E | future bars cannot change an earlier verdict | `hvcs_structural(bars[:t], t, …)` equals `hvcs_structural(bars, t, …)` for every `t`, including when a later bar would have been a violation |
| F | violation counting is deterministic | repeated evaluation returns identical `minutes`, `violations` and `indecision_bars`; the count is independent of how much history is passed in |

Existing tests that must keep passing unchanged: `tests/engine/test_cbr1h_pc3.py:175,181` (H-1 / H-2 behaviour) and
`tests/engine/test_phase13c_diagnosis.py`, whose `conforming_tolerant` helper already encodes the target semantics
and becomes the oracle the new implementation must match.

## 4. Schema, config and candidate impact

| Question | Answer |
|---|---|
| Config change needed? | **No.** `hvcs.max_violations: {value: 1, label: ASSUMPTION, source: [OQ-08]}` already exists and is already loaded |
| Schema change needed? | Only the additive `violations` diagnostic field on `HvcsPC3` and, if the owner wants it in the ledger, one new diagnostic column. No scored field changes |
| Spec-record change needed? | Yes: correct the H-1 entry in the parity-candidate spec so it states the tolerance explicitly instead of the ambiguous "no maximum count" |
| **Does this require a new candidate?** | **Yes.** It changes signal-affecting behaviour, so it cannot be applied to PC3 without breaking the frozen hash that CBR-RUN-013C-1 was scored under. It must land in **PC4**, whose creation the owner has not authorized |
| Does it change PC2? | No. PC2 keeps its own `hvcs()` and its own frozen hash |
| Effect on the parity examples | **Not measured here and not to be measured before a candidate is frozen.** The D32 diagnostic figures (6, 4, 0 at the extreme anchor) are already on record; no new run was made |

## 5. Ordering constraint

F-1 alone is a faithful restoration and can be specified now. But because it must ship inside PC4, and because PC4
must not be created until the OQ-48 anchor question and the OQ-50 evaluation-point question are ruled on, **F-1 is
ready but not yet actionable**. The sequence is: owner rulings on OQ-48 §10 and OQ-50 §4-5 → PC4 authorization →
F-1 plus whatever else those rulings approve, implemented together → freeze → authorized scored run.
