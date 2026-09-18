# Phase 15 — untouched CBR1H baseline acceptance criteria

**Doc:** CBR-ACC-015 · **Version:** v1.0 **PROPOSED** · **Date:** 2026-09-18 · **Ruling:** D40 §11-22
**Status:** written and frozen **before** any historical signal is generated or any outcome observed. For owner
approval.

Phase 15 measures the frozen model. It does not improve it. Nothing in this document may be revised after results
are seen; a change requires a new version and a new owner ruling.

---

## 1. What is under test

| | |
|---|---|
| Model | `CBR1H_BASELINE_V1` = frozen PC4, spec hash `62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7` |
| Execution | D38 semantics, `config/execution.yaml` (`EXEC-14A`) |
| Data | D39 real-data integration: Dukascopy tick-mid STRUCTURE, tick bid/ask EXECUTION |
| Scope | **CBR1H only**, XAUUSD only. CBR15 is not baseline-ready and is not mixed in (D40 §11) |
| Variants | A (`HVCS_S5_SHIFT`) and B (`FRACTAL_1M_S5_SHIFT`), reported together and separately |

## 2. Periods, fixed before results (D40 §13)

| Split | Period | Use in Phase 15 |
|---|---|---|
| **Development** | 2018-01-01 → 2022-12-31 | primary measurement |
| **Validation** | 2023-01-01 → 2024-12-31 | sign-consistency check |
| **Holdout** | 2025-2026 | **not accessed**; any access is logged and would void the run |

The baseline runs only over a **declared complete** acquisition span. A partial span is never measured (D40 §10).

## 3. Frozen settings (D40 §14)

PC4 specification and its assumptions · D38 execution config · additional slippage **0** · explicit commission **0**
· actual bid/ask spread · actual gap execution · canonical exits **stop and target only** · rollover exclusion. None
is optimized, and no alternative value is tried.

## 4. Signal inclusion

| Rule | |
|---|---|
| Population | every signal frozen PC4 emits over the declared span, both variants, no filtering |
| Eligibility | the D37 external promotion gate only; a signal with any other blocker is recorded and excluded from executed statistics |
| One-position | D38 §14 applies: siblings cancelled at the winner's fill, later activations logged `POSITION_ALREADY_OPEN` |
| No post-hoc exclusion | a signal may never be dropped because of how it turned out |

## 5. Treatment of non-canonical outcomes

| Outcome | Treatment |
|---|---|
| `TARGET`, `STOP` | **canonical completed trades** — the only rows in primary win/loss and expectancy statistics |
| `ROLLOVER_EXIT`, `DATASET_END_EXIT` | administrative; reported separately with counts and R, never silently discarded, never merged into canonical statistics (D40 §20) |
| `ENTRY_FILL_UNPROVABLE_DATA_GAP`, `TRADE_OUTCOME_UNPROVABLE_DATA_GAP`, `EXECUTION_UNPROVABLE_INTRABAR` | reported individually; **no win or loss is inferred**; the rate `unprovable / eligible signals` is a baseline data-quality metric (D40 §21) |
| `ENTRY_NOT_TRIGGERED`, `ROLLOVER_CANCEL`, `SIBLING_ORDER_CANCELLED_ON_FILL`, `POSITION_ALREADY_OPEN`, `EXECUTION_DATA_UNAVAILABLE`, `EXECUTION_INVALID_RISK` | counted in the signal funnel, excluded from trade statistics |

## 6. Metrics (predeclared, D40 §15)

**Signal counts:** total candidate signals · executable · not triggered · cancelled · unprovable · filled trades.

**Trade metrics** (canonical completed trades): wins · losses · win rate · planned R:R at fill · realized gross R ·
realized net R · average winner · average loser · median R · **expectancy per trade** · profit factor.

**Risk:** max drawdown in R · longest losing streak · drawdown duration · worst trade · yearly R distribution.

**Stability:** by year · by direction · by variant A/B · by session and time bucket (**descriptive only**, never a
selection criterion) · trade concentration.

**Execution quality:** spread distribution · entry-gap distribution · stop-gap distribution · rollover exits ·
dataset-end exits · unprovable outcomes.

## 7. Primary metric (D40 §16)

**Net expectancy in R per executed canonical trade.** Win rate is secondary and is never optimized for.

## 8. Pass / fail logic (D40 §17)

No arbitrary profitability magnitude is required. The predeclared condition is **sign consistency**:

> **Development net expectancy > 0** *and* **validation net expectancy > 0.**

Meeting it authorizes continued robustness research. It does **not** establish a robust edge, and this document may
not be read as claiming one.

## 9. Statistical uncertainty (D40 §18)

Report a confidence interval around expectancy from a **bootstrap over trade-level R outcomes** (resampling
completed canonical trades with replacement, 10,000 resamples, percentile interval, seed recorded in the manifest).
No rule is tuned from the bootstrap. Walk-forward, Monte Carlo, parameter sensitivity, yearly stability and the
holdout remain later, separate gates.

## 10. Year concentration (D40 §19)

Report R by year, trade count by year, the percentage of total net R attributable to the best year, and the result
excluding the best year. Diagnostic during the untouched baseline: no automatic rejection from a threshold unless
separately approved.

## 11. Prohibited in Phase 15 (D40 §22)

No ablation of any kind: DXY on/off · HVCS alternatives · OQ-48 / OQ-50 / OQ-52 alternatives · k = 2 or 4 ·
different targets or stops · different sessions · different activation minutes · LAST_RESET · FINAL_PUSH · new
filters. No parameter change, no signal filtering, no execution-assumption change, and no re-run after seeing
results.

## 12. Reporting structure

`reports/phase15-cbr1h-baseline.{md,json}` and `reports/phase15-run-manifest.json`, containing: the run id, the PC4
spec hash, the execution config hash, the acquisition-span declaration with per-day source hashes, the signal
population hash, the result hash, the full signal funnel, the metrics of §6 split development / validation, the
§9 interval, the §10 concentration table, and `baseline_v1.provenance()` — which continues to state the parity
verdict **FAIL** and the five documented fidelity concerns. Every statistic carries its denominator.

## 13. Acceptance

Phase 15 is accepted when: the run covers a declared complete span · every §6 metric is reported with its
denominator · §5 treatments are visibly applied · the §8 condition is evaluated and stated plainly whichever way it
falls · the §9 interval and §10 concentration are present · determinism holds across a repeat run · no prohibited
item in §11 occurred · and the owner accepts the report. **A negative result is an acceptable outcome of a valid
run**, and is reported without mitigation.
