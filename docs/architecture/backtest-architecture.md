# Proposed Backtest Architecture

Status: **proposal for approval**. No backtest code exists yet, by design (first milestone stops before
implementation).

> **Superseded in part (2026-09-14, D13).** Execution (the `backtest/` layer in §2 and §4) is now planned in
> `phase14-execution-architecture.md`: Phase 14A is the authoritative custom simulator and Phase 14B the Backtesting.py
> adapter, parity and visualization. The Pine/PineTS runner (§6) moves downstream of validation (Phases 26-27,
> CBR-GOV-001 §8). Layout names below (`strategy/`, `ledger/`) are indicative; the Phase 14 doc gives the current layout.

## 1. Principles carried into code

- **One source of truth for signals.** A Python reference engine computes every setup. Pine and any external
  tool must *match it*, not the other way round.
- **Event-time causality.** Every feature is computed from bars whose close time ≤ decision time. Swing points
  are usable only after their confirming bars close. Enforced by tests that shift the future and assert
  unchanged signals.
- **Canonical vs research separation.** Rule implementations carry their rule id (`CBR1H-OE-001`); anything not
  in a spec is labelled `RESEARCH-DERIVED` or `LEVEL-2-DERIVED` and lives in a separate module.
- **Diagnostics over filters.** Discretionary proxies and optional confluences are recorded on every signal
  (signal ledger) and only become filters through a logged ablation.
- **Frozen versions.** A model version = rules + parameters + code hash + data manifest hash. Never overwritten.

## 2. Layers

```
config/            strategy.yaml (per model version: rule toggles + ASSUMPTION values)
                   sessions.yaml (IANA tz session windows) · research.yaml (splits, costs)
src/cbr/
  ingestion/       videos, slides, journal (done) · market data: dukascopy ticks → 5s/1m parquet
  data/            bar loaders (DuckDB over parquet), XAUUSD↔DXY alignment, gap flags
  structure/       swing detection (causal), shift detection (type-3), HILO, HVCS, condition classifier,
                   entry relativity, external/internal, AOI levels
  candles/         candle-behavior state per candle (open, extension duration, pullback %, wick side,
                   minute-in-candle) for 5m / 15m / 1h / 1d
  strategy/
    cbr1h/         rules.py (one function per rule id) · model.py (state machine) · CBR1H_BASELINE_V1
    cbr15/         same structure · CBR15_BASELINE_V1
  dxy/             independent context module: DXY candle behavior, inverse-extension state, lead/lag
  backtest/        execution simulator on 5s bars with bid/ask: stop-entry fills, stop/target priority,
                   spread + slippage model, one position per model
  ledger/          signal ledger (every qualifying signal, taken or not) → parquet
  analysis/        metrics, R-distribution, segmentation, ablation runner
  validation/      temporal splits, walk-forward, Monte Carlo / bootstrap
  pine_parity/     export bars → PineTS run → compare trades with Python ledger
strategies/pine/   cbr1h_baseline_v1.pine, cbr15_baseline_v1.pine
reports/           extraction/ baseline/ experiments/ walkforward/ robustness/
tests/             unit per rule id · causality tests · fixtures/reference_setups/ (course & journal days)
```

Dependencies flow downward: `analysis → backtest → strategy → structure/candles → data`. `strategy/` never imports
`analysis/`.

## 3. Signal state machine (per model, per candle)

```
IDLE ─(candle opens inside a qualifying condition)→ WATCH_OE
WATCH_OE ─(extension ≥ min duration, no 50% pullback, reaches range extreme / beyond structure)→ OE_CONFIRMED
OE_CONFIRMED ─(within timing window: type-3 shift per entry model)→ SIGNAL  → ledger row
SIGNAL ─(entry order filled)→ IN_TRADE ─(stop | target | management exit)→ CLOSED
any state ─(window expires | invalidation rule)→ INVALIDATED (reason code) → ledger row
```

Every transition records the rule ids that passed or failed, so every no-trade is explainable.

## 4. Execution realism

- Entries on seconds-shift breaks are **stop orders** at the break price, filled at the first 5s bar that trades
  through it, at worse of (trigger + slippage, bar open).
- Stop and target touched in the same 5s bar → **stop first** (conservative), counted and reported.
- Costs: Dukascopy spread from ticks + configurable slippage (ticks) + commission per lot.
- Gold targets are small (50% of a 20-30 min extension), so costs are material. Every report shows results
  before and after costs.

## 5. Experiment workflow (Phases 15-23)

1. Freeze `CBR15_BASELINE_V1` / `CBR1H_BASELINE_V1` (only `in` rows of the rule matrix; ASSUMPTIONs declared).
2. Parity: reference setups (course examples, journal days) → does the engine produce the taught signal?
   `reports/signal-parity.md`.
3. Baseline on Development split → metrics suite (trade count, win rate, PF, expectancy in R, MaxDD, streaks,
   long/short, monthly/yearly, R-distribution).
4. Hypothesis log entry **before** each experiment (`research/hypothesis-log.md`).
5. Ablations on Validation split, one rule at a time (DXY confluence, DXY veto, sessions, adaptive TP, 15m
   alignment, management rules).
6. Limited parameter research only on OQ items marked `RESEARCH PARAMETER`, with small grids and walk-forward
   selection.
7. Holdout evaluated once per frozen candidate version.
8. Robustness: trade-order reshuffle, bootstrap expectancy CI, drawdown and losing-streak distributions.

## 6. Pine role

- Pine baselines mirror the Python rules for the TradingView indicator and for independent confirmation.
- **Known limitation:** seconds-level entries. Pine V1 uses 1m entries (`SIMPLIFIED-ENTRY`), and the parity report
  quantifies the signal/trade differences vs the Python 5s reference.
- Runner: PineTS locally (see `tooling-report.md`), gated by TradingView Strategy Tester parity.

## 7. Open decisions that affect this design

OQ-01 swing definition · OQ-04 FS/IFS in baseline · OQ-09 Academy definitions · OQ-10 seconds data ·
OQ-16 sessions. See `docs/strategy/open-questions.md`.
