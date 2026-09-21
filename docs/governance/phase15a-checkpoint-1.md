# Phase 15A checkpoint 1 — infrastructure complete, acquisition running (D42 §22)

**Doc:** CBR-RPT-015A-1 · **Date:** 2026-09-20 · **Status:** returned for owner review
No PC4 performance has been run. No historical CBR outcome exists. Validation (2023-2024) and holdout (2025-2026)
were not accessed. The Phase 15A protocol hash is unchanged:
`baba0fff090a331c7b9209d8fb41468d93473880304b2f64e3325a0b81389d09`.

---

## 1. Acquisition progress

| | |
|---|---|
| Blocks complete | **5 of 12** (January-June; July in progress at 247/473 hours) |
| Successful hours | **3,204** of 5,894 requested open hours (54.4%) |
| Unresolved so far | 2,653 (hours not yet reached — not failures) |
| Bytes | 128.1 MB |
| Existing 2022 data reused | 3 fixture days, not refetched |

## 2. Measured seconds per file

**33.3 s/file** over the last completed day, and the run has been stable in the 29-35 s band since early January.
The earlier 2.0 s/file reading came from the first 23 files before the feed began throttling; it was not
representative and is withdrawn.

**Estimated completion: ≈ 25 hours** for the remaining ~2,650 hours at the current rate.

## 3. Retry / 5xx / 429 counts

| | |
|---|---|
| Retries | 762 |
| HTTP 429 | **0** |
| HTTP 5xx | **513** |
| Unresolved failures in completed blocks | **0** |

The constraint is Dukascopy 5xx responses absorbed by backoff, not rate limiting. Every retried hour has so far
resolved: no completed block carries an unresolved failure.

## 4. Unexpected-gap status — investigated and classified

**37 unexpected gaps, all resolved, none blocking.** Register:
`research/data_quality/unexpected_gaps_2022.json`, hash
`5f79e3828e9131c33207de3d3f134dd74044e2cd8db2b7d89cb7ac66b3c0c6ec`.

| Trading day | Hours | Holiday |
|---|---|---|
| 2022-01-17 | 4 | Martin Luther King Jr. Day |
| 2022-02-21 | 2 | Presidents' Day |
| 2022-04-15 | 23 | Good Friday (whole session, starting 17:00 New York on 04-14) |
| 2022-05-30 | 2 | Memorial Day |
| 2022-06-20 | 2 | Juneteenth |
| 2022-07-04 | 2 | Independence Day |
| 2022-11-24 | 2 | Thanksgiving Day |

**Classification: `DATA_LIMITATION`** for all 37, from the existing data-quality taxonomy. The canonical session
calendar encodes only the weekend and the daily 17:00 New York break, so a genuine holiday closure necessarily
surfaces as an "unexpected" gap under the Phase 9 AC-07 criterion.

The classification is never granted by the calendar alone. Each hour must also show, in stored artefacts, that the
feed returned a **404 with no file** and that the empty hours form one contiguous run which either reaches the daily
break (an early close) or covers the whole session (a full closure). Evidence is recorded per hour: artefact bytes,
the run, the neighbouring hours' bytes, and the trading day. Thanksgiving shows the expected taper — 14.8 KB at
16:00, 9.3 KB at 17:00, 4.7 KB at 18:00, 2.0 KB at 19:00, then nothing until the 23:00 UTC reopen.

**Nothing was interpolated, forward-filled or invented, and no hour was silently marked complete.** A
`DATA_LIMITATION` hour is *not* repaired: its minutes still reach the simulator as gaps, so D38's unprovable
outcomes fire exactly as they would for any other missing interval. Three refusals are enforced by test: an
unclassified gap blocks, an ordinary missing market hour blocks as `DATA_GAP`, and an isolated hole on a holiday
with trading either side still blocks.

**Owner decision worth recording:** the canonical calendar has no holiday schedule. Adding one would change
`sessions.expected_closed`, which feeds the TRADABLE condition-window basis and is therefore a **strategy-relevant**
change. It has not been made, and PC4 is untouched. The consequence of leaving it alone is that Good Friday and the
holiday afternoons present as gaps rather than closures — conservative, and visible in every report.

## 5. Decoded-day progress

**3 of 260** trading days decoded. Decoding is deliberately deferred: `dukascopy_fetch.fetch` issues requests for
any hour it does not find cached, and scheduled closures are never cached, so decoding now would compete with the
running downloader for the same throttled endpoint. It runs as one pass when acquisition finishes.

## 6. Historical signal runner — **built**

`src/cbr/engine/historical_runner.py`, version `15A.1`, hash
`8ce91da71b46ce367ba956d91b35f7b2015c730e60f9ec6896d0df25a36add5a`.

Applies frozen PC4 across a span and emits the signal ledger with every `signal_id` preserved, the candidate and
rejection frames intact, per-day source hashes, and a ledger hash. It holds no strategy logic of its own.

Four refusals, each covered by test:

| Guard | Behaviour |
|---|---|
| `FrozenSpecDrift` | PC4 spec, execution config and protocol hashes are verified **before** any bar is loaded |
| `PartialSpanRefused` | any subset of the frozen year is refused outright — month-by-month, quarterly and part-year performance are impossible, not merely discouraged |
| `SpanIncomplete` | the completeness gate must read COMPLETE for the whole span (the hard test D42 §5 requires) |
| `RestrictedPeriod` | 2023-2024 and 2025-2026 are refused without an explicit owner authorization token, which is recorded when used |

Fixture mode takes caller-supplied synthetic bars, never reads the canonical store, and stamps its output
`FIXTURE_NON_PERFORMANCE`.

**Chunking and warm-up.** The year runs in month chunks with **10 days** of warm-up, far beyond the engine's longest
lookback (the 10-hour prior-setup window over the 8-hour condition window). Warm-up is drawn **only from inside the
span**, so the first hours of January have less context than later hours and may classify `UNDEFINED`. No 2021 data
is pulled to fix this, because that would widen the frozen span. **This is an owner decision if a different warm-up
policy is wanted**; the current one is recorded in provenance as `warmup_source: WITHIN_SPAN_ONLY`.

## 7. Execution orchestrator — **built**

`src/cbr/execution/orchestrator.py`, version `15A.1`, hash
`fa30bb1b108f1dcf4d721f7d20246c84f3f041f471215568cd2e78fc1a8060de`.

Connects the signal ledger to the Phase 14A simulator over Phase 14A.1 tick replay, duplicating no strategy logic
and no execution semantics. Signals are grouped by **trading session** — the metals day rolling at 17:00 New York —
and each session is replayed over its own window. A session is the correct boundary because D38 forces every
position flat at rollover, so no position can cross one; grouping by calendar day would split a session at midnight
UTC and let one position appear open in two chunks. A signal carrying no activation time is recorded as
`NOT_EXECUTED`, never dropped, and the orchestrator raises if the ledger does not hold exactly one record per
signal. No summary statistic is computed there.

## 8. Metrics and package writer — **built**

`src/cbr/reporting/phase15a_metrics.py` (`15A.1`) and `src/cbr/reporting/phase15a_package.py` (`15A.1`).

Every §14 metric is implemented: the full signal funnel, the sixteen trade metrics, execution-quality
distributions, and month / direction / variant / session breakdowns marked **DESCRIPTIVE ONLY** in the output
itself. The primary metric is unchanged — **net expectancy in R per executed canonical trade** — and win rate is
secondary.

The protocol's separations are enforced in code, not remembered: only `CLOSED` trades exiting at `TARGET` or `STOP`
enter expectancy; `ROLLOVER_EXIT` and `DATASET_END_EXIT` are reported with their own counts and R and never merged;
unprovable outcomes carry no inferred win or loss; every statistic carries its denominator.

The writer emits all eight artefacts with the required `signals.csv` and `trades.csv` columns, and **refuses** to
write a package whose manifest is missing any of the sixteen required provenance fields (D42 §13). A test confirms
an auditor can recompute expectancy from `trades.csv` alone and get the manifest's number.

## 9. Deterministic rerun harness — **built**

`src/cbr/reporting/rerun_harness.py`, hash
`a6d0c5bfbb9171fd174d18719765c34105e1240e3f4138486b6030ab2640a063`.

Compares signal-ledger, execution-ledger, metrics and result hashes, plus every package file — byte-for-byte where
the file is deterministic, and by **semantic content hash** for `run_manifest.json` and `phase15a_report.md`, which
legitimately carry a generation timestamp. Any substantive divergence is **FAIL**. Tests confirm that a timestamp
difference alone passes while a changed expectancy in the manifest fails.

## 10. Pine compile-readiness

`research/tradingview/cbr1h-pc4-research-strategy.pine` plus a new `README.md` for the track. `max_bars_back = 5000`
was added for the bounded HVCS scan. TD-1…TD-6 are documented in both the file header and the README, with TD-6
(prior-setup count not implemented) named as the largest known functional gap — it is shown as `N/A`, never as
passing.

**Still not compiled in TradingView**: static review only. The README lists the six constructs most likely to need
attention at first compile and states the first objective as COMPILE + VISUALIZE, not tester performance.

## 11. Tests

**769 passed**, 0 failed, 0 skipped. `ruff check src tests` clean. Forty new tests since the last report: the gap
registry (8), the completeness gate's gap wiring, and the Phase 15A pipeline (25) covering the runner's four
refusals, session grouping, metric separations, package provenance refusal and the rerun harness.

## 12. Remaining blockers before PRE-RUN readiness

| # | Blocker | Status |
|---|---|---|
| 1 | 2022 acquisition incomplete — 5 of 12 blocks | running, ≈ 25 h |
| 2 | 257 of 260 days not decoded to canonical tick and bar files | one pass after acquisition, ~1-2 h (to be measured) |
| 3 | Gate not yet COMPLETE — waiting on 1 and 2 | automatic once both land |
| 4 | Gap register must be re-run over the **full** year; the remaining holidays (Labor Day, Christmas observed) will appear | mechanical, blocks if anything fails to classify |
| 5 | End-to-end pipeline has never run on real data at year scale — memory and wall-clock are unmeasured | first real exercise is the pilot itself |

None of these is a strategy question, and none can be cleared early.

### One expectation worth stating before the result exists

On synthetic random-walk bars PC4 arms roughly **one signal per ten days** across both variants. If 2022 behaves
similarly, the pilot may produce a **small sample**, which the frozen protocol already anticipates: `INCONCLUSIVE`
is a predeclared verdict for exactly that case. This is a statement about the model's selectivity observed during
construction, not a prediction of performance, and no rule was changed in response to it.
