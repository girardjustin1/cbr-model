# Phase 14A completion report — authoritative execution simulator

**Doc:** CBR-RPT-014A · **Date:** 2026-09-18 · **Ruling:** D38 · **Status:** returned for owner approval
No historical performance was run · no P&L or trade outcome inspected · PC4 unmodified · Backtesting.py not started ·
Astra × Fable not started.

---

## 1. Modules and files

| Path | Role |
|---|---|
| `config/execution.yaml` | the frozen D38 semantics, `spec_version: EXEC-14A` |
| `src/cbr/execution/contract.py` | frozen-signal validation + the D37 external eligibility gate |
| `src/cbr/execution/prices.py` | the executable quote stream, spread lookup, gap classification, rollover window |
| `src/cbr/execution/orders.py` | entry-order live window: activation → expiry / cancel / rollover |
| `src/cbr/execution/fills.py` | the four frozen fill rules + tick-sequence resolution |
| `src/cbr/execution/position.py` | stop resolution at fill, position book (one per instrument) |
| `src/cbr/execution/ledger.py` | record schema, closed enumerations, R arithmetic, run manifest |
| `src/cbr/execution/simulate.py` | the deterministic driver |
| `tests/execution/test_architecture_guard.py` | import guard (3 tests) |
| `tests/execution/test_simulator.py` | the D38 §30 inventory (31 tests) |
| `tests/execution/test_worked_example.py` | the hand-computed example (1 test) |
| `docs/governance/d38-phase14a-execution-semantics.md` | the ruling, mapped rule-by-rule to code |

## 2. Execution semantics implemented

All twenty-odd rulings in D38, mapped to their implementation in the table in the D38 record. Every value lives in
`config/execution.yaml`, so none is buried in code.

## 3. OQ-28 resolution

Implemented as ruled: the stop is resolved **at the entry fill**, from the latest canonical STRUCTURE anchor
available causally through the fill timestamp (`position.anchor_through` reads only path points at or before the
fill), then frozen. A later, more adverse structure extreme never moves it —
`test_the_stop_is_resolved_at_fill_and_then_frozen` proves both halves: the anchor advances from 98.00 to 97.00
before the fill and ignores the 90.00 that arrives after it.

Preserved separately on every record: `signal_stop_anchor`, `fill_time_stop_anchor`, `stop_buffer`, `fill_spread`,
`final_execution_stop`.

## 4. Stop formula

```
anchor  = min(path points ≤ fill, signal anchor)   for LONG      # most adverse through fill
        = max(path points ≤ fill, signal anchor)   for SHORT
widen   = buffer_atr × ATR(1m,14) at the decision  +  spread at fill   (spread_policy = ADD_SPREAD_AT_FILL)
stop    = anchor − widen   (LONG)        stop = anchor + widen   (SHORT)
```

Stop exit: LONG when `bid ≤ stop`, filling at that **bid**; SHORT when `ask ≥ stop`, filling at that **ask**. A jump
through the stop fills at the worse quote; `stop_gap` records the difference.

## 5. Target formula

The frozen PC4 `target_price` is used unchanged. LIMIT semantics: LONG needs `bid ≥ target`, SHORT needs
`ask ≤ target`, and the fill is **at the target price** even when the quote gapped past it. The unclaimed
improvement is recorded for diagnostics, never paid.

## 6. Entry semantics

STOP order, live from `entry_trigger_time` to the earliest of expiry, the signal's own cancel time, the rollover
window and data end. LONG triggers on `ask ≥ trigger` and fills at that ask; SHORT on `bid ≤ trigger`, filling at
that bid. `entry_gap` records how far the quote moved through the trigger. Quotes before activation cannot fill the
order, and a pre-activation crossing never fabricates a fill.

## 7. Gap semantics

Entry and stop take the **first executable quote** after the level is breached, so a jump fills worse. Targets never
improve. Both gaps are recorded (`entry_gap`, `stop_gap`), so a later analysis can quantify what gapping cost.

## 8. Same-bar and tick sequencing

Tick sequence is authoritative: stop and target are each located in the post-fill quote stream and the earlier
timestamp wins, regardless of which aggregated bar they share. Where the stream is **not** tick-resolved, the run
returns `EXECUTION_UNPROVABLE_INTRABAR` — including when an unresolved bar merely *precedes* a resolved event, since
that bar could have contained the real first touch. No stop-first or target-first convention exists in the code.

## 9. Position scope

One open CBR1H position per instrument. The earliest fill in tick sequence opens it; orders **pending at that
instant** are cancelled `SIBLING_ORDER_CANCELLED_ON_FILL`; signals that activate while the position is open are
recorded `POSITION_ALREADY_OPEN`; a signal activating after the close may trade normally. Variants A and B are never
concurrent trades.

## 10. Rollover handling

No activation or fill inside the canonical exclusion window (`rollover_pre_min` 15 / `rollover_post_min` 60 around
17:00 New York, DST-aware, reusing the existing strategy helper). A pending order reaching it is `ROLLOVER_CANCEL`.
An open position is closed on the **last executable quote before** the window, exit reason `ROLLOVER_EXIT` — LONG on
the bid, SHORT on the ask.

## 11. Missing-data behaviour

No interpolation, no forward fill, no synthetic quote, no spread substitution. A classified `DATA_GAP` intersecting
the pending window gives `ENTRY_FILL_UNPROVABLE_DATA_GAP`; one intersecting an open position gives
`TRADE_OUTCOME_UNPROVABLE_DATA_GAP`. Scheduled closure, the rollover window and ordinary sparse quoting are **not**
data gaps and are proved not to be by test. Absence of executable data altogether gives
`EXECUTION_DATA_UNAVAILABLE`, and the signal stays in the ledger unexecuted.

## 12. Ledger schema

One row per signal, every field D38 §27 requires, plus `entry_gap`, `stop_gap`, `tick_resolved`,
`additional_slippage`, `explicit_commission` and `simulator_version`. `validate()` enforces the closed
enumerations: statuses `NOT_EXECUTED / PENDING / FILLED / CANCELLED / CLOSED / UNPROVABLE`; exit reasons
`TARGET / STOP / ROLLOVER_EXIT / DATASET_END_EXIT` and **only on a CLOSED row**; ten separate non-exit reason codes.
`ROLLOVER_EXIT` and `DATASET_END_EXIT` are excluded from `CANONICAL_EXITS`, and the manifest reports their counts
separately so they cannot slip into stop/target statistics.

## 13. Gross and net R

```
initial_risk = fill − stop  (LONG)        stop − fill  (SHORT)        must be > 0 or EXECUTION_INVALID_RISK
gross_r      = (exit − fill) / risk (LONG)        (fill − exit) / risk (SHORT)
net_r        = gross_r − (additional_slippage + explicit_commission) / risk
             = gross_r   at the 14A baseline, because both are 0
```

Spread is already inside the bid/ask fills and is never subtracted again; `test_17_spread_is_not_double_counted`
asserts `net_r == gross_r` with the spread visible in `fill_spread`.

## 14. Synthetic test inventory (D38 §30)

All twenty required cases plus eleven more: 1 long target · 2 long stop · 3 short target · 4 short stop · 5 entry gap
· 6 stop gap · 7 target gap · 8 target before stop · 9 stop before target · 10 sibling cancellation · 11 rollover
cancel · 12 rollover forced exit · 13 missing bid/ask · 14 gap while pending · 15 gap while open · 16 non-positive
risk · 17 no double-counted spread · 18 dataset-end close · 19 deterministic repeat · 20 future mutation. Additional:
unresolved-bar unprovability · position-already-open · trade-after-close · scheduled closure is not a gap ·
pre-activation crossing · stop frozen after fill · unexpected blocker refused · promotion blocker accepted ·
executable stop in a signal refused · one row per signal · manifest provenance.

## 15. Worked example

`tests/execution/test_worked_example.py` documents the arithmetic by hand and asserts each number: fill 2000.40
(gap 0.40), spread 0.20, stop 1996.00 − 0.20 − 0.20 = 1995.60, risk 4.80, target exit at 2006.00, gross R
5.60 / 4.80 = **1.1666666666666667**, net R equal. The expected R is computed from an exact `Fraction`, not from
simulator output.

## 16-20. Status

| | |
|---|---|
| **Total tests** | **696 passed**, 0 failed, 0 skipped (35 new) |
| **Lint** | `ruff check src tests` clean |
| **Causality** | no fill uses data after its own instant: pre-activation quotes cannot fill; appending later quotes leaves fill time, fill price, exit reason and exit price unchanged; the at-fill anchor reads only path points ≤ fill |
| **Determinism** | identical `result_hash` across repeat runs |
| **Architecture guard** | no execution module imports a CBR rule module; strategy-side imports limited to an allow-list; no `M1H-` rule id appears anywhere in the package |

## 21. Remaining execution concerns

1. **Real-data quote stream not yet built.** The simulator consumes tick quotes; a loader from stored Dukascopy
   ticks is still to be written. Until then every historical window would be bar-resolved, which by ruling returns
   `EXECUTION_UNPROVABLE_INTRABAR` rather than a fill. This is the next piece of work, and it is mechanical.
2. **Gap classification input.** `DATA_GAP` intervals must come from the existing manifests; wiring that is pending.
3. **`PENDING` and `FILLED` statuses are defined but unused** by the batch driver, which resolves each signal to a
   terminal state in one pass. They remain in the enum for a future streaming mode — a non-behavioural limitation.
4. **Commission stays 0** and is not broker-specific (D38 §24).
5. **The five Phase 13 fidelity concerns** travel on every manifest through `provenance()` and are unchanged.

## 22. Phase 14A verdict

### PASS

Every frozen execution semantic in D38 is implemented and covered by a synthetic test; the mechanics suite, the
architecture guard and the hand-computed example all pass; causality, determinism and the import separation hold;
and no historical outcome was computed. Item 21.3 is a non-behavioural limitation and does not affect fill
correctness, so it does not reduce the verdict to PASS WITH CONCERNS — but the owner may prefer that label given
items 21.1 and 21.2 remain before any historical run is possible.

**Stopping here for owner approval** before Phase 14B or the OQ-24 baseline-feed resolution.
