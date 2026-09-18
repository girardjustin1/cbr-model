# Phase 14A acceptance criteria — authoritative execution simulator

**Doc:** CBR-ACC-014A · **Version:** v1.0 **PROPOSED** · **Date:** 2026-09-18 · **Ruling:** D37 §11-16
**Status:** written **before** any historical outcome is measured (D37 §16). For owner approval.

Phase 14A determines what happens when frozen `CBR1H_BASELINE_V1` (= PC4, spec
`62a2310e…`) signals are executed under realistic market assumptions. It does **not** change which signals exist.

---

## A. Separation of concerns (hard gate)

| Id | Criterion |
|---|---|
| A-1 | The simulator consumes signals only through `baseline_v1.run_baseline` / a frozen signal file. It never imports CBR rule modules to re-derive a decision |
| A-2 | The simulator **never** invents a signal, rejects one on strategy grounds, alters direction, or reinterprets a CBR rule. Execution may only decide *whether and at what price* a signal's orders fill |
| A-3 | No execution assumption may be fitted, chosen or tuned from trade outcomes. Every assumption is declared before the first historical run |
| A-4 | Every execution record links to its signal by `signal_id`, and every signal consumed appears in the ledger exactly once, including those that never fill |
| A-5 | `baseline_v1.verify()` passes at the start of every run; a drifted spec aborts the run |

## B. Price-series semantics (D37 §13)

| Id | Criterion |
|---|---|
| B-1 | STRUCTURE = tick-derived midpoint; EXECUTION = tick-derived bid/ask. The simulator reads EXECUTION bars for every fill decision and never fills on mid |
| B-2 | **LONG:** entry on **ask**; stop and target evaluated against **bid**. **SHORT:** entry on **bid**; stop and target evaluated against **ask** |
| B-3 | Spread is time-varying wherever the tick data supports it; any fallback is declared, tagged on the record, and never silently zero |
| B-4 | A price-role guard refuses EXECUTION logic fed STRUCTURE bars, and vice versa, as the engines already do |

## C. Fill mechanics

| Id | Criterion |
|---|---|
| C-1 | **Deterministic fills:** the same inputs produce byte-identical ledgers, verified by a repeat run and a result hash |
| C-2 | **No lookahead:** a fill decision at time `t` uses only EXECUTION data closed at or before `t`. Truncation and future-mutation tests pass, as they do for the engines |
| C-3 | **Entry:** a STOP order at `entry_reference_price`, live from `entry_trigger_time` to `entry_expiry_time`, filled under the frozen entry rule (E-OQ-5) |
| C-4 | **Same-bar ambiguity** is resolved by one frozen rule declared before the run (E-OQ-3); every ambiguous bar is flagged on the record whichever way it resolves |
| C-5 | **Gap through stop** and **gap through target** are handled by one frozen rule each (E-OQ-6), and gapped fills are flagged |
| C-6 | **Slippage** follows one frozen model (E-OQ-4), applied identically to winners and losers, never asymmetric |
| C-7 | **Stop resolution** follows the frozen answer to OQ-28 (E-OQ-1); the simulator writes `final_execution_stop` and shows its inputs |
| C-8 | **Forced exit** follows the frozen rule (E-OQ-2); if the ruling is "none", positions end only at stop, target or data end, and that is stated |
| C-9 | **One-position rule** is applied where canonical (E-OQ-7); concurrent signals that are suppressed are recorded as suppressed, not dropped |
| C-10 | **Rollover exclusion** and the daily break follow the frozen rule (E-OQ-8) |
| C-11 | **Missing data** during a live position follows the frozen rule (E-OQ-10) and is always visible on the record, never imputed |

## D. Outputs

| Id | Criterion |
|---|---|
| D-1 | A complete **execution ledger**: one row per signal with `signal_id`, order state, fill times and prices, spread at fill, slippage applied, stop and target as resolved, exit time, **exit reason**, and every flag from C-4/C-5/C-11 |
| D-2 | **Gross R** and **net R** per trade, with the R definition stated once and applied uniformly |
| D-3 | Exit reasons are a closed enumeration (`STOP`, `TARGET`, `FORCED_EXIT`, `EXPIRED_UNFILLED`, `CANCELLED`, `DATA_END`, `SUPPRESSED`) — no free text |
| D-4 | Every artefact carries `baseline_v1.provenance()`, so the parity verdict FAIL and the five fidelity concerns travel with the numbers |
| D-5 | A run manifest pins the baseline spec hash, the execution-assumption set, code commit, data hashes and the result hash |

## E. Testing (before any historical run)

| Id | Criterion |
|---|---|
| E-1 | Synthetic fixtures only for development, as in Phase 13 |
| E-2 | Each of C-3 … C-11 has a dedicated synthetic test, including at least one adversarial case per rule (gap past both levels; stop and target inside one bar; spread widening at the fill instant; a bar missing mid-position) |
| E-3 | Determinism, truncation and future-mutation suites pass |
| E-4 | A hand-computed worked example is asserted end-to-end, so the arithmetic is verified by something other than the code that produced it |
| E-5 | Full suite and lint clean on the acceptance commit |

## F. Acceptance verdict

Phase 14A passes when A-1…A-5, B-1…B-4, C-1…C-11, D-1…D-5 and E-1…E-5 hold, **every** execution assumption in
E-OQ-1…E-OQ-10 has an owner ruling recorded before the first historical run, and the owner accepts the result. No
performance statistic is computed as part of this acceptance.
