# Phase 14 Execution Architecture: Authoritative Simulator (14A) + Backtesting.py Adapter (14B)

**Doc:** CBR-ARCH-014 · **Version:** v0.1 (plan) · **Date:** 2026-09-14 · **Owner instruction:** "Integrate Backtesting.py
into the CBR project without weakening the existing research methodology" (decision D13)
**Status:** PLANNED. No Phase 14 code is written before Phases 10-13 are complete and gate G2 passes. The
Backtesting.py dependency is **not** added to `pyproject.toml` until 14B implementation begins.
**Supersedes:** §2 `backtest/` and §4 of `backtest-architecture.md` for execution. Signal semantics stay in the machine
specs (`cbr-primitives-machine-spec.md` §8, `1h-cbr-machine-spec.md` §6-7, `15min-cbr-machine-spec.md` §7-8).

---

## 1. Research chain (unchanged in authority)

```
Tom's evidence → machine specification → CBR reference engine (Phases 11-12) → Tom ↔ Python parity (13, G2)
  → authoritative execution simulator (14A) → Backtesting.py parity + visualization (14B)
  → untouched baselines (15-16) → validation → Astra × Fable review (17) → controlled research → holdout → TradingView
```

| Question | Authority | Never decided by |
|---|---|---|
| Does a CBR signal exist? Direction, trigger, stop rule, target? | CBR reference engine (frozen spec + config) | Backtesting.py, any execution layer |
| How does a signal fill and exit (bid/ask, spread, slippage, same-bar, gaps, rollover, missing data)? | Custom simulator (14A) | Backtesting.py |
| Is there an edge? | Ledger-based R metrics from 14A on frozen baselines, then governance (CBR-GOV-001) | Backtesting.py statistics |
| Visual inspection, standard statistics, secondary execution cross-check | Backtesting.py (14B) | n/a |

**Backtesting.py is a secondary execution implementation, a standard-metrics layer, an interactive visual layer and a
parity check.** It is never the source of truth for signal detection, rule interpretation, bid/ask execution,
causality or research conclusions. When it disagrees with the custom simulator, **the custom simulator wins** and the
difference is classified (§7).

---

## 2. Layout (adapted to the existing repository)

The owner's sketch used top-level `src/execution/`, `src/backtest/` and `src/cbr/{context,swings,…}.py`. The repo packages
only `src/cbr` (hatch), and structure primitives already exist in `src/cbr/structure/`, so nothing is duplicated:

```
src/cbr/
  structure/          (exists) indicators, swings, condition, overextension, shifts, levels
  data/               (exists) dukascopy_fetch, databento_fetch, quality (D12 detectors), phase9_acceptance
    alignment.py      (14A-prereq, Phase 10) causal XAU↔DXY as-of alignment honouring MISSING intervals
    resampling.py     (Phase 11) causal 5s → 1m → 15m → 1h; bar usable only at its close time
    bidask_bars.py    (14A) tick → bid OHLC and ask OHLC bars (5s, 1m); today only mid bars exist
  dxy/                (Phase 10) DXY context module: availability, confidence, 15m/1h direction
  engine/             (Phases 11-12) cbr15.py, cbr1h.py state machines → frozen Signal records + ledger events
  contracts/          (Phase 11) signal.py: frozen dataclass mirroring docs/architecture/schemas/cbr-signal.v1.schema.json
  execution/          (14A, authoritative)
    simulator.py      event loop over bid/ask bars; consumes frozen signals only
    fills.py          stop-entry, stop, target, forced-exit fill rules (machine spec §8)
    costs.py          spread from bars, slippage, commission
    ledger.py         ledger writer (every candidate signal, taken or not)
  backtest/           (14B, secondary)
    backtesting_py_adapter.py   frozen signals + bars → Backtesting.py DataFrame; run manifest
    backtesting_py_strategy.py  thin Strategy: read precomputed signal, submit order, attach SL/TP, tag signal_id
    metrics.py        R metrics from the ledger (authoritative); library stats kept as secondary
    reports.py        stats, trade table, equity, HTML chart, parity report, manifest
tests/
  execution/  backtest/  parity/
```

Dependencies flow downward: `backtest → execution → contracts ← engine → structure/dxy → data`. `engine/` never imports
`execution/` or `backtest/`. `backtest/` never imports `engine/` rule code (it reads frozen signal files), which enforces
"no CBR logic inside Backtesting.py" structurally. A test will assert this import rule.

---

## 3. Signal contract (stable interface: engine → every execution backend)

Schema: `docs/architecture/schemas/cbr-signal.v1.schema.json` (planning draft; finalized in Phase 11, frozen before Phase
13). A signal is written once by the engine and is **immutable**: execution layers read it and may never create, delete
or edit a signal, or change whether it exists. A frozen signal set is a parquet file plus a manifest with its SHA-256;
both 14A and 14B must load the same hash.

### 3.1 Required fields

| Field | Meaning (definition fixed here so "timestamp parity" is testable) |
|---|---|
| `signal_id` | Deterministic id: `model/variant/candle_open_utc/direction/seq` |
| `model` | `CBR1H_BASELINE_V1` / `CBR15_BASELINE_V1` (+ `variant`) |
| `timestamp` | **Decision time** (UTC): close time of the last bar used to arm the signal. Every input has close time ≤ this |
| `direction` | `LONG` / `SHORT` |
| `entry_trigger_time` | Time the entry **order becomes active** (= first bar whose open is > `timestamp`). Not the fill time; the fill is an execution outcome |
| `entry_expiry_time` | Order cancelled if unfilled by this time (`timing.end`; spec §8 "Order expiry") |
| `entry_order_type` | `STOP` (spec §8: break entries) |
| `entry_reference_price` | Trigger price (`t3.trigger_price` / `hilo.trigger_price`) |
| `stop_price` | Stop specification at decision time (see §3.2) |
| `target_price` | `oe_extreme − 0.5 × (oe_extreme − candle.open)` (mirror LONG) |
| `extension_high`, `extension_low` | Extension extremes at decision time, with `extremes_source` (`TICK_MID` / `SIDE_EXTREME_MEAN`; D12-5) |
| `range_high`, `range_low` | Condition-range extremes at decision time |
| `context_state` | Condition class, OE state, timing-window state |
| `dxy_state` | Phase 10 output: `AVAILABLE` / `MISSING` / `REFERENCE_UNAVAILABLE` + 15m/1h direction (no 1m/5s structure; D12-6) |
| `session_state` | Session label + no-trade windows active (`NT_SYDNEY`, `NT_ROLLOVER`, `NT_INCOMPLETE`) |
| `source_feed` | Feed id + data manifest hash (OQ-24) |
| `data_confidence` | `FULL` / `REDUCED` / `UNAVAILABLE` with data-quality reason codes (e.g. `DXY_CFD_MISSING_WHILE_DX_ACTIVE`) |
| `reason_code` | Engine event code: `ARMED`, or a no-trade code (`BLOCKED_*`, `INVALIDATED_*`, `NT_*`, `MISSING_DATA`) |
| `spec_hash` | Hash of machine spec + `strategy.yaml` + engine code that produced the signal |

Optional diagnostics are the ledger fields of `1h-cbr-machine-spec.md` §7 / `15min-cbr-machine-spec.md` §8.

### 3.2 Conflict to resolve in Phase 11: stop resolved at fill (OQ-28)

The current spec computes the stop **at fill**: `oe_extreme (at fill) ± buffer_atr × ATR(1m,14) ± spread`
(M1H-SL-01, primitives §8). A contract with a fixed `stop_price` at decision time is not the same thing. The planned
handling, pending owner decision OQ-28:

- The contract carries `stop_rule` = {`anchor` (oe_extreme at decision), `buffer_price` (ATR buffer at decision),
  `spread_policy: ADD_SPREAD_AT_FILL`} and `stop_price` = anchor ± buffer (the spread-free specification).
- 14A resolves the final stop at fill from the actual spread. 14B does **not** take the resolved stop from 14A's fill
  records, because that would make it depend on 14A outcomes. It receives the same `stop_rule` and applies the documented
  spread approximation (§6.1). The difference is classified `SPREAD_APPROXIMATION`.
- Specification parity (100%) compares `stop_rule` / `stop_price` / `target_price`. The resolved stop is an execution
  outcome (classified, not 100%).
- Alternative (owner may choose): freeze the stop fully at decision time. That changes M1H-SL-01's wording and would be
  recorded as a spec revision **before** Phase 13, never after baselines.

---

## 4. Phase 14A: authoritative execution simulator

Inputs: a frozen signal set + canonical bid/ask bars (5s from ticks; the extremes source is fixed by OQ-25 / G2d) +
`config/execution.yaml` (to be created in 14A, labelled CANON/ASSUMPTION/IMPL).

| Requirement | Rule (from machine spec §8 unless noted) |
|---|---|
| Deterministic inputs | Only frozen signals; the signal-set hash is recorded in every result |
| Long / short | Both; one position per model (`SKIPPED_IN_TRADE`) |
| Entry | Stop order active from `entry_trigger_time`: LONG fills when **ask** trades through the trigger at `max(trigger, ask.open)` + slippage; SHORT when **bid** trades through at `min(trigger, bid.open)` − slippage |
| Stop / target | LONG exits observed against **bid** (stop: bid.low ≤ stop; target: bid.high ≥ target); SHORT against **ask** |
| Gaps | Stop gapped through → fill at the bar open (worse; consistent with spec §8 `max(trigger, bar.open)`). Target gapped through: **not specified in the machine spec**. Proposal for `config/execution.yaml` (IMPL, owner-approved before baselines): fill at the target (no gap improvement, conservative), recorded `GAP_THROUGH_TARGET` |
| Same-bar stop & target | Stop first (IMPL conservative), counted and reported; includes the entry bar |
| Spread | From bid/ask bars (time-varying), never a flat rate |
| Slippage | `ASSUMPTION` ticks per fill (declared before baselines) |
| Commission | Per lot, if applicable (`ASSUMPTION`) |
| Rollover | No entries in `NT_ROLLOVER`; forced flat at `17:00 NY − rollover_flat_before_min` (EP1-018) |
| Missing data | No bar → no fill and no exit on that interval; a position crossing a gap exits on the first bar after it using gap rules and records `MISSING_DATA`; a signal whose required data is MISSING is never executed (`data_confidence = UNAVAILABLE`) |
| Expiry | Unfilled at `entry_expiry_time` → `EXPIRED` |
| Output | Fill records: entry/exit timestamps and prices (bid/ask side), exit reason, spread at fill, gross R, net R (after spread, slippage, commission), `signal_id` |
| Ledger | Every candidate signal gets a row: executed, rejected, invalidated, expired, skipped, missing-data, with reason codes |
| Reproducibility | Same signals + bars + config → byte-identical fill parquet (hash test) |
| Holdout lock | Refuses holdout dates unless given the frozen candidate hash + owner approval ref (CBR-GOV-001 §7) |

Gate **G14A**: unit tests per fill rule, same-bar and gap fixtures, a determinism hash test, the holdout-lock test, and
hand-verified trades on the course parity examples (execution only, no performance statistics).

---

## 5. Phase 14B: Backtesting.py adapter

### 5.1 Pinned version and licence

- Candidate pin: **`backtesting==0.6.6`** (latest on PyPI at 2026-09-14; sdist sha256
  `844af11c961fa0f47bfddb04b448416f93b02b731faadfa3df8b98a44081fd0b`). It requires `bokeh` (exclude 3.0.*, 3.2.*),
  which will be pinned too. Re-confirm the pin and re-verify §6 against that version when 14B starts.
- **Licence: AGPL-3.0.** The repository is public. Owner review is required before adding it (OQ-30).

### 5.2 Inputs per model

| Model | Execution clock | DataFrame columns |
|---|---|---|
| CBR1H | 5s bars under the current spec (primitives §8 fills both models on `B5s`). 1m only if Phases 11-13 prove it sufficient **and** the owner revises the spec (OQ-29) | `Open, High, Low, Close` + `CBR1H_SIGNAL, CBR1H_DIRECTION, ENTRY_PRICE, STOP_PRICE, TARGET_PRICE, EXPIRY, SIGNAL_ID` + DXY columns |
| CBR15 | 5s bars | same with `CBR15_*` |

- Signal columns are placed on the bar whose open time is `entry_trigger_time`. That is the first bar the strategy may act
  on, so nothing is visible before its decision time.
- Higher-timeframe context (1m, 15m, 1h) is computed outside Backtesting.py by the engine or `resampling.py`. It is
  attached only after that bar's close, and a test mutates future bars to prove the columns don't change.
- DXY columns (`DXY_CLOSE, DXY_15M_DIRECTION, DXY_1H_DIRECTION, DXY_AVAILABLE, DXY_CONFIDENCE`) use backward as-of
  alignment on close times. Intervals flagged MISSING stay NaN / `DXY_AVAILABLE = False`: no forward-fill across them
  (D12-1/2) and no 1m/5s DXY structure (D12-6). They are display and diagnostic only; the strategy never reads them to
  decide anything.

### 5.3 Thin Strategy (planned behaviour)

```
next():
  cancel any pending entry order past its EXPIRY           # library has no order expiry
  if bar carries SIGNAL_ID and signal is executable (data_confidence != UNAVAILABLE, no open position):
      buy/sell(stop=ENTRY_PRICE, sl=STOP_PRICE_APPROX, tp=TARGET_PRICE, size=UNITS, tag=SIGNAL_ID)
  if bar is the rollover flat time and a trade is open: close it   # precomputed FORCE_FLAT column
```

It never evaluates range, extension, structure shift, DXY confluence or whether a signal should exist. It doesn't use
`self.I` indicators for decisions (display-only overlays are allowed), so no warm-up offset changes the first tradable bar.
A test will scan `backtest/` for imports of `cbr.structure` / `cbr.engine`.

### 5.4 Outputs per run

1. `stats` (standard Backtesting.py statistics, labelled SECONDARY)
2. trade table (`_trades`, with `Tag = signal_id`)
3. equity curve
4. interactive HTML chart (`plot(open_browser=False, filename=…)`), one per baseline run, plus per-signal window charts
   (§6 #13)
5. parity report vs 14A (§7)
6. manifest: model version, `spec_hash`, git commit, data feed + manifest hash, date range, execution and cost
   assumptions (including every approximation label), parameter set, signal-set hash, signal count,
   `backtesting`/`bokeh`/`pandas`/`numpy` versions, run timestamp

`_trades` never replaces the ledger. It links to it by `signal_id`, and the ledger keeps every candidate signal.

---

## 6. Execution-semantics comparison (verified against backtesting 0.6.6 source)

References are to `backtesting/backtesting.py` in the 0.6.6 sdist. Re-verify on the pinned version.

| # | Topic | Custom simulator (14A, authoritative) | Backtesting.py 0.6.6 | Handling |
|---|---|---|---|---|
| 1 | Market-order timing | Not used for entries (stop orders) | Order placed in `next()` fills at the **next bar's open** (`_process_orders`) | Not used; entries are stop orders |
| 2 | `trade_on_close` | n/a | If `True`, market orders fill at the current close; contingent SL/TP never do | Keep `False` |
| 3 | Stop-entry fill | Triggered on ask (LONG) / bid (SHORT); fill `max(trigger, open)` + slippage | Triggered when `High ≥ stop` (LONG) on the single price series; fill `max(open, stop)`, no slippage | Matches the gap rule; side and slippage differ → `SPREAD_APPROXIMATION` |
| 4 | Stop-loss fill | Observed on bid (LONG) / ask (SHORT); gap → open | SL is a stop order on the single series; gap → fill at open (`max/min(price, stop)`) | Same gap rule; side differs |
| 5 | Target fill | Observed on opposite side; gap → target (proposed IMPL, §4) | TP is a limit order; gap → fill at the **better** open | `GAP_FILL_DIFFERENCE` |
| 6 | Same-bar stop & target, existing trade | Stop first | SL orders are inserted at the queue front ("Ensure SL orders are processed first") → SL first | Consistent; still counted |
| 7 | Same-bar entry + SL/TP | Evaluated on the entry bar, stop first | For a **stop entry**: TP-only-hit is reprocessed on the same bar; any other SL/TP hit on the entry bar is **deferred to the next bar** with a warning (issue #119) | `SAME_BAR_AMBIGUITY`; warnings captured and counted |
| 8 | Commission | Per lot (ASSUMPTION) | Float rate, `(fixed, relative)` or callable `(size, price)`, applied at entry **and** exit; no time argument | Callable for fixed per-unit cost; mismatch → `LIBRARY_EXECUTION_SEMANTICS` |
| 9 | Spread | Time-varying bid/ask from ticks | `spread` = one **relative** rate for the whole run, applied to the entry price only (closes at the unadjusted price) | Approximation A or B below, labelled and quantified |
| 10 | Slippage | ASSUMPTION ticks per fill | None | Folded into the approximation; quantified |
| 11 | Missing bars | Explicit; gap rules; `MISSING_DATA` | NaN OHLC raises an error, so missing rows must be dropped and the next row is treated as contiguous | Rows absent; gap exits → `MISSING_DATA` / `GAP_FILL_DIFFERENCE` |
| 12 | Partial bars | Never used: bars exist only once closed | Operates on completed rows | Adapter builds closed bars only |
| 13 | Plot size | n/a | `resample=True` downsamples charts above 10,000 candles | Full-run chart resampled (labelled); per-signal window charts with `resample=False` for inspection |
| 14 | Order expiry | `EXPIRED` at `timing.end` | None | Strategy cancels at `EXPIRY` |
| 15 | Position size / R | R-based, lot size from risk | Whole units or equity fraction; P&L in cash | Fixed units; R recomputed in `metrics.py` from entry/exit/stop |
| 16 | Open trades at end | Rollover forces flat | Excluded from stats unless `finalize_trades=True` | `finalize_trades=True`; rollover column forces flat first |
| 17 | Statistics annualization | R metrics from ledger | Sharpe/Sortino via calendar resampling of equity | Library stats are SECONDARY; never used for conclusions |
| 18 | Warm-up | n/a | Starts at `1 + indicator warm-up`; bar 0 never trades | Adapter starts each run at least one bar before the first `entry_trigger_time` |
| 19 | Optimization | Prohibited | `Backtest.optimize()` exists | **Prohibited in Phases 14-16**; a test fails if `optimize(` appears in `src/cbr/backtest` |

### 6.1 Bid/ask approximation options for 14B (labelled, quantified)

- **A: mid series + relative spread.** Feed `TICK_MID` OHLC and set `spread` = median(spread/price) of the run.
  Simple. Wrong for time-varying spread and for exits observed on the wrong side. Label `APPROX_MID_RELATIVE_SPREAD`.
- **B (preferred): side series per direction.** Run LONG signals on **bid** OHLC and SHORT signals on **ask** OHLC, so
  exits are observed on the correct side. The entry trigger is shifted by the signal-time spread
  (`trigger − spread_at_decision` for LONG) and the entry-side cost is added back in `metrics.py`, labelled
  `APPROX_SIDE_SERIES_DECISION_SPREAD`. This needs two runs per model, so the equity curve is for visualization only.

For every run, report per-trade and aggregate |14A net R − 14B net R|. If approximation effects change conclusions
materially, they're reported as such, and the 14A result stands.

---

## 7. Parity: CBR engine → 14A → 14B

### 7.1 Pre-registered thresholds

Registered here on 2026-09-14, **before any baseline performance exists**. They can't be relaxed after results are seen.

| Check | Threshold |
|---|---|
| Signal membership: 14A and 14B consume the identical signal set (same ids, same hash) | **100%** |
| Direction | **100%** |
| Signal timestamp (`timestamp`) and entry activation time (`entry_trigger_time`) | **100%** |
| Stop / target specification (`stop_rule`, `stop_price`, `target_price`, `entry_reference_price`, expiry) | **100%** |
| Entry eligibility (executable vs not: data confidence, in-trade skip, no-trade windows) | **100%**, or every difference classified |
| Fill occurred (yes/no), entry fill time, exit time, exit reason, gross result (R) | As high as technically possible; **every mismatch classified**, none dropped |

### 7.2 Mismatch reason codes

`ORDER_TIMING_DIFFERENCE` · `SPREAD_APPROXIMATION` · `SAME_BAR_AMBIGUITY` · `GAP_FILL_DIFFERENCE` · `MISSING_DATA` ·
`LIBRARY_EXECUTION_SEMANTICS` · `IMPLEMENTATION_BUG`

`IMPLEMENTATION_BUG` blocks the gate until fixed. Unclassified mismatches block the gate. The parity report lists every
signal id with both outcomes and its code.

### 7.3 Test fixtures (planned)

Synthetic bar sequences with known answers for each §6 row: stop entry, gap through stop, gap through target, same-bar
SL/TP on an existing trade, SL/TP on the entry bar, expiry, a missing-bar interval, rollover flat. Plus course-example
windows for execution-only inspection (holdout days: parity use only, logged).

---

## 8. Baseline protection

- `Backtest.optimize()` is not called in Phases 14-16. No parameter search. No tuning of stop buffers, extension
  duration, DXY rules, swing definitions, timing windows, session filters or target logic before the untouched baselines
  exist and Phase 17 approves experiments.
- The first Backtesting.py baseline uses exactly the frozen `spec_hash` and signal set used by 14A.
- Backtesting.py-specific convenience never changes canonical rules. If the library can't express a rule, the difference
  is documented (§6) and the custom simulator's result stands.
- Holdout: 14B inherits the 14A holdout lock and access logging.

---

## 9. Gate G14B: acceptance (returns PASS / PASS WITH CONCERNS / FAIL)

| # | Condition |
|---|---|
| 1 | Backtesting.py (and bokeh) pinned to exact versions; §6 re-verified on that version |
| 2 | Adapter tests pass |
| 3 | Signal membership parity 100% |
| 4 | Direction parity 100% |
| 5 | Entry-time parity 100% (§3.1 definitions) |
| 6 | Stop/target specification parity 100% |
| 7 | Every execution mismatch classified; no `IMPLEMENTATION_BUG` open |
| 8 | Report generation deterministic: stats, trade table, equity and manifest byte-identical across reruns; HTML identical after normalizing Bokeh-generated ids and the run timestamp (whether Bokeh output is byte-stable must be tested, not assumed) |
| 9 | No Backtesting.py-specific logic changes canonical CBR rules (import-rule test + review) |
| 10 | 14A and 14B run from the same frozen signal-set hash |

- **PASS:** all 10, with no approximation affecting conclusions.
- **PASS WITH CONCERNS:** all 10, with labelled approximations or classified execution differences documented.
- **FAIL:** any of 1-7, 9 or 10 not met, or determinism not demonstrated.

---

## 10. Dependencies and timing

- Phase 14A needs: engines (11-12), parity G2 (13), canonical extremes source G2d (OQ-25), baseline feed G2c
  (OQ-24), bid/ask bar builder, full 5s history for the chosen feed (AC-11B or equivalent), DXY availability diagnostic
  (OQ-27).
- Phase 14B needs: G14A, licence review (OQ-30), version pin.
- Current active phase is unchanged: **Phase 10 (DXY context module)**.
