# Phase 15A — 2022 one-year development pilot: frozen protocol

**Doc:** CBR-ACC-015A · **Version:** v1.0 **FROZEN** · **Date:** 2026-09-19 · **Ruling:** D42
**Status:** written and hashed **before** any historical signal is generated and before any outcome is observed.

This document measures a frozen model over a frozen year. It does not improve the model. Nothing here may be
revised after results are seen; a change requires a new version, a new hash and a new owner ruling.

---

## 1. What is under test (D42 §12-13)

| | Frozen value |
|---|---|
| Model | `CBR1H_BASELINE_V1` = frozen PC4 |
| PC4 spec hash | `62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7` |
| Execution semantics | D38, `config/execution.yaml` (`EXEC-14A`), SHA-256 `12be582e16b9fbf0fdec9322200446f539a8f2ae08efba8eb7d2ca83f22b0551` |
| Real-data integration | D39 / Phase 14A.1, `simulator_version = 14A.1` |
| Authoritative engine | Phase 14A simulator + Phase 14A.1 tick integration. **Not** TradingView, **not** Backtesting.py, **not** bar assumptions |
| Instrument | XAUUSD, CBR1H only. CBR15 is not baseline-ready and is not mixed in |
| Variants | A (`HVCS_S5_SHIFT`) and B (`FRACTAL_1M_S5_SHIFT`), reported together and separately |

No CBR rule, HVCS parameter, Type-3 definition, extension-activation rule, swing `k`, target, stop, session rule,
DXY handling or candidate-selection rule is changed during Phase 15A. **No strategy tuning is permitted.**

## 2. Period (D42 §3)

**2022-01-01 00:00 UTC → 2022-12-31 23:59:59.999 UTC**, frozen before measurement.

Inside the already-frozen 2018-2022 development split. **2023-2024 validation and 2025-2026 holdout performance are
not accessed.** The year is not changed after seeing performance, and no other year is substituted if the result
disappoints.

## 3. Status of the result (D42 §4, §16)

This is a **DEVELOPMENT PILOT** — not a full development baseline, not validation, not holdout, not a robust edge.
It answers: *is the frozen CBR1H implementation promising enough to justify the full historical study?*

| Verdict | Predeclared meaning |
|---|---|
| **PROMISING** | net expectancy > 0 with enough trade observations to justify continuing |
| **NEGATIVE** | net expectancy < 0 under the frozen model |
| **INCONCLUSIVE** | sample size, unprovable rate or data quality prevents a useful conclusion |

**VALIDATED EDGE is not an available verdict.** One development year neither kills the project nor promotes the
strategy.

## 4. Frozen execution settings (D42 §11)

| Setting | Frozen value |
|---|---|
| Additional slippage | **0** — recorded as an ASSUMPTION, not a claim about real fills |
| Explicit commission | **0** — non-broker-specific |
| Spread | **actual historical bid/ask** at each instant; never a modelled or average spread |
| Entry / stop fills | first executable quote at or through the level (LONG entry and SHORT stop on ASK; SHORT entry and LONG stop on BID) |
| Targets | limit-priced: filled exactly at the target, never improved by a gap |
| Stop | resolved at fill from the structure anchor, then **frozen** for the life of the trade |
| Time exit | none is invented |
| Rollover | canonical rollover window excluded; pending orders in it cancel `ROLLOVER_CANCEL`; open positions exit `ROLLOVER_EXIT` |
| Missing data | Phase 9 AC-07 gap criterion, translated not redefined: a minute with no data that is not `expected_closed` is a gap. Gaps produce `ENTRY_FILL_UNPROVABLE_DATA_GAP` / `TRADE_OUTCOME_UNPROVABLE_DATA_GAP`; ambiguous intrabar sequencing produces `EXECUTION_UNPROVABLE_INTRABAR` |
| Concurrency | one position per instrument; siblings cancelled at the winner's fill; later activations logged `POSITION_ALREADY_OPEN` |
| Dataset end | an open position at the end of the span exits `DATASET_END_EXIT` |

## 5. Signal inclusion

Every signal frozen PC4 emits over the declared span, both variants, **no filtering**. Eligibility uses the D37
external promotion gate only; a signal with any other blocker is recorded and excluded from executed statistics.
**A signal may never be dropped because of how it turned out.**

## 6. Treatment of non-canonical outcomes

| Outcome | Treatment |
|---|---|
| `TARGET`, `STOP` | **canonical completed trades** — the only rows in win/loss and expectancy statistics |
| `ROLLOVER_EXIT`, `DATASET_END_EXIT` | administrative; reported separately with counts and R; never silently discarded, never merged into canonical statistics |
| `ENTRY_FILL_UNPROVABLE_DATA_GAP`, `TRADE_OUTCOME_UNPROVABLE_DATA_GAP`, `EXECUTION_UNPROVABLE_INTRABAR` | reported individually; **no win or loss is inferred**; `unprovable / eligible signals` is a data-quality metric |
| `ENTRY_NOT_TRIGGERED`, `ROLLOVER_CANCEL`, `SIBLING_ORDER_CANCELLED_ON_FILL`, `POSITION_ALREADY_OPEN`, `EXECUTION_DATA_UNAVAILABLE`, `EXECUTION_INVALID_RISK` | counted in the signal funnel, excluded from trade statistics |

## 7. Data completeness gate (D42 §9-10)

Performance does not run until the declared 2022 span is **COMPLETE**. The gate reports all fifteen fields:

requested trading days · requested open hours · successful hours · scheduled closures · legitimate empty hours ·
unresolved failures · retry count · HTTP 429 count · HTTP 5xx count · bytes · tick count · duplicates · bad spreads ·
non-positive prices · unexpected gaps.

**No unresolved market-open hour may silently disappear.** PC4 is not run on January only, Q1, the first six months,
or the completed months while acquisition is still running: the first performance result uses the entire frozen span.

## 8. Metrics (D42 §14)

**Signals** — total frozen PC4 signals · executable · not-triggered · cancelled · unprovable · filled trades.

**Performance** (canonical completed trades) — wins · losses · win rate · planned R:R · average planned R:R ·
gross R · net R · average winner · average loser · median realized R · **expectancy per executed canonical trade** ·
profit factor · max drawdown in R · longest losing streak · total net R.

**Execution quality** — spread distribution · entry-gap distribution · stop-gap distribution · rollover exits ·
dataset-end exits · unprovable execution count and rate.

**Descriptive breakdowns** — long vs short · Variant A vs B · month · session/time bucket. **Descriptive only; no
tuning from them during the pilot.**

Every statistic carries its denominator.

## 9. Primary metric (D42 §15)

**NET EXPECTANCY IN R PER EXECUTED CANONICAL TRADE.** Win rate is secondary and is never optimized for; CBR is not
judged primarily by win rate.

## 10. Prohibited in Phase 15A

No ablation of any kind · no parameter change · no signal filtering · no execution-assumption change · no rerun
after seeing results (one pilot run, plus one determinism rerun that must reproduce it exactly) · no partial-period
performance · no access to 2023-2026 performance · no use of the six availability-pilot days for strategy
performance · `Backtest.optimize()` is never called.

## 11. Deliverables (D42 §17)

`reports/phase15a/` containing `phase15a_report.md`, `run_manifest.json`, `signals.csv`, `trades.csv`,
`monthly_metrics.csv`, `equity_curve.csv`, `drawdowns.csv`, `execution_quality.csv`.

The manifest carries: run id · PC4 spec hash · execution config hash · this protocol's hash · the 2022 span
declaration with per-day source hashes · signal-population hash · result hash · simulator version · and
`baseline_v1.provenance()`, which continues to state the parity verdict **FAIL** with its five documented fidelity
concerns.

## 12. Acceptance

Phase 15A is accepted when: the run covers the declared complete 2022 span · every §8 metric is reported with its
denominator · §6 treatments are visibly applied · the §3 verdict is stated plainly whichever way it falls ·
determinism holds across the repeat run (identical result hash) · no §10 prohibition occurred · and the owner
accepts the report. **A negative result is an acceptable outcome of a valid run**, and is reported without
mitigation.
