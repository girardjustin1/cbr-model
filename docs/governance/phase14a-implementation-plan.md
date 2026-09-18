# Phase 14A implementation plan — authoritative execution simulator

**Doc:** CBR-PLAN-014A · **Version:** v1.0 · **Date:** 2026-09-18 · **Ruling:** D37 §11-16, §22
**Status:** PLAN. No execution code has been written. Ten execution assumptions need owner rulings first (§3).

---

## 1. Frozen signal contract, confirmed (D37 §22.1)

Pinned by `tests/engine/test_pc4_signal_contract.py` (9 tests) against the frozen emitter. 25 top-level fields:

| Group | Fields | What Phase 14A does with them |
|---|---|---|
| Identity | `signal_id`, `model`, `variant`, `price_role`, `spec_hash`, `timestamp` | key the ledger; assert `price_role = STRUCTURE` and the frozen spec hash |
| Direction | `direction` (`LONG`/`SHORT`) | picks the bid/ask side per B-2 |
| Entry | `entry_order_type` = `STOP`, `entry_reference_price`, `entry_trigger_time`, `entry_expiry_time` | a stop order live over a bounded window |
| Structure | `entry_structure.*` (parent type/time, sweep times, trigger confirmation, re-anchor count, 5s shift level) | diagnostics on the record; never re-derived |
| Extension | `extension.*` (state, activation, origin, size, duration, retracement) | diagnostics and R context |
| Stop | `stop_rule.*` — anchor, anchor path through activation, `buffer` (`stop.buffer_atr`, ATR(1m,14), ASSUMPTION/OQ-11), `spread_policy = ADD_SPREAD_AT_FILL`; **`stop_price` and `final_execution_stop` are `None`** | **the simulator resolves the stop** from these inputs under E-OQ-1 |
| Target | `target_price` (resolved at activation) | used as given; never re-optimized |
| Context | `context_state.*`, `range_high/low`, `dxy_state`, `source_feed`, `data_confidence` | carried onto the record for later analysis |
| Lifecycle | `lifecycle.cancel_time`, `cancel_reason`, `five_second_shift_time`, `timing30_state` | a cancelled signal may not fill after `cancel_time` |
| Eligibility | `eligibility.baseline_eligible = False`, `blockers = ["PHASE13C_PARITY_NOT_RUN"]` | see §2 |

**Two contract facts that shape the work:**

1. **The stop is a rule, not a price.** PC4 deliberately emits inputs (anchor, path, buffer parameter, spread policy)
   and leaves `stop_price` null. Resolving it is an execution responsibility and needs OQ-28 settled (E-OQ-1).
2. **There is no exit time in the contract.** Canon's trade management is explicitly discretionary — "I'll exit
   around that halfway point of that 15 minute candle", "exit if we have that counter behaviour", "every entry is an
   exit" (`V1H-trade_management`) — so no mechanical forced-exit rule exists to inherit. It must be ruled on
   (E-OQ-2).

## 2. The inherited eligibility blocker (no code change to PC4)

Every PC4 signal still carries `baseline_eligible = False` and the blocker `PHASE13C_PARITY_NOT_RUN`, because PC4 was
frozen before its own parity run. PC4 must not be edited (D37 §7, §10), so Phase 14A gates eligibility
**externally**: the simulator accepts signals whose only blocker is that constant, records the D37 promotion as the
authority, and refuses any signal carrying a different blocker. This keeps the frozen artefact honest and the
promotion auditable.

## 3. Execution assumptions requiring an owner ruling (blockers)

None of these can be chosen by evidence from the corpus, and none may be chosen from outcomes. Each must be frozen
before the first historical run.

| Id | Question | Options | Note |
|---|---|---|---|
| **E-OQ-1** | **OQ-28**: is the stop resolved at fill, or frozen at the decision? | (a) at fill, from the anchor path through activation (D17-2's reading); (b) frozen at decision | Long-standing open question; changes fills directly |
| **E-OQ-2** | **Forced exit** — canon gives none | (a) none: stop/target/data-end only; (b) end of the entry hour; (c) end of the next 15m candle; (d) fixed horizon; (e) ~:52 into the hour, mirroring Tom's live close | (a) is the most neutral; (e) imports a discretionary habit |
| **E-OQ-3** | **Same-bar ambiguity**: stop and target both inside one 5s bar | (a) stop first (conservative); (b) target first; (c) resolve from the underlying tick sequence — **we hold the ticks**; (d) mark AMBIGUOUS and exclude | (c) is the most faithful and costs a tick pass |
| **E-OQ-4** | **Slippage model** | (a) none; (b) fixed ticks; (c) proportional to the spread at fill; (d) from tick depth | Must apply identically to winners and losers |
| **E-OQ-5** | **Entry fill price** for a STOP order | (a) at `entry_reference_price` when touched; (b) at the next available ask/bid after the touch; (c) gap-aware: the worse of the two | Interacts with E-OQ-4 |
| **E-OQ-6** | **Gap through stop / target** | (a) fill at the gapped price (realistic); (b) fill at the level (optimistic) | Recommend the same choice for both, stated explicitly |
| **E-OQ-7** | **One-position rule** | (a) none; (b) one per instrument; (c) one per model; (d) one per model+variant | Variants A and B can both signal in one hour |
| **E-OQ-8** | **Rollover / daily break** (21:00 UTC) | (a) no entries within N minutes, hold through; (b) force exit before the break; (c) ignore | |
| **E-OQ-9** | **Spread fallback** when tick spread is unavailable for a bar | (a) last known; (b) session median; (c) refuse to fill and flag | D37 §13 keeps spread time-varying where data supports it; this covers where it does not |
| **E-OQ-10** | **Missing EXECUTION data** during a live position | (a) hold and flag; (b) force exit at the last known price; (c) void the trade | Never imputed silently |

`OQ-24` (baseline feed) is **not** a 14A blocker but must be resolved before Phase 15, on the non-profitability
criteria in D37 §8. `OQ-29` (execution clock) is treated as settled at 5 seconds by the frozen spec; confirm in the
ruling.

## 4. Architecture

```
src/cbr/execution/
  contract.py     load and validate frozen signals; external eligibility gate (§2); refuse unknown blockers
  prices.py       EXECUTION bar access, bid/ask side selection, spread lookup, price-role guards
  orders.py       stop-order lifecycle: armed -> filled / expired / cancelled
  fills.py        the frozen rules from E-OQ-3..E-OQ-6, each behind one named, tested function
  position.py     stop resolution (E-OQ-1), target, forced exit (E-OQ-2), one-position policy (E-OQ-7)
  ledger.py       the execution record, exit-reason enum, gross/net R, run manifest with provenance()
  simulate.py     the deterministic driver: signals in, ledger out, no CBR logic anywhere
```

Dependencies flow one way: `simulate → position → fills → orders → prices → contract`. No module imports a CBR rule
module. `cbr.engine.baseline_v1` is the only bridge, and it is read-only.

## 5. Build order

1. `contract.py` + tests: load signals, validate against the pinned contract, apply the external eligibility gate.
2. `prices.py` + tests: bid/ask selection, spread lookup, guards, missing-data detection.
3. `orders.py` + tests: the stop-order lifecycle against `entry_trigger_time` / `entry_expiry_time` / `cancel_time`.
4. `fills.py` + tests: **only after E-OQ-3…E-OQ-6 are ruled**; one function per rule, each with adversarial cases.
5. `position.py` + tests: **only after E-OQ-1, E-OQ-2, E-OQ-7 are ruled.**
6. `ledger.py` + tests: schema, exit-reason enum, R arithmetic, provenance, manifest.
7. `simulate.py` + tests: determinism, truncation, future mutation, the hand-computed worked example (E-4).
8. Acceptance run on synthetic and designated non-performance fixtures; acceptance report; **stop**.

Steps 1-3 and 6 can proceed immediately; 4, 5 and 7 are blocked on the rulings.

## 6. What this plan deliberately does not do

No historical performance run · no untouched baseline · no trade-count, win-rate or expectancy figure · no
`Backtest.optimize()` · no Backtesting.py adapter (that is 14B, secondary) · no Astra × Fable review · no change to
any strategy rule, including the four documented fidelity concerns.
