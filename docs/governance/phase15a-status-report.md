# Phase 15A status report — pre-performance (D42 §23)

**Doc:** CBR-RPT-015A-0 · **Date:** 2026-09-19 · **Status:** returned for owner review
No PC4 performance has been run. No trade outcome, P&L, expectancy or win rate exists anywhere in this report. No
validation or holdout data was accessed.

---

## 1. Full acquisition safely stopped

Yes. The staged `2018-01 → 2024-12` run was stopped between hourly files. The fetcher writes each file `.part` →
atomic rename and persists `retry_queue.json` atomically after **every** hour, so any instant between files is a safe
checkpoint.

Verified after the stop: **0** `.part` files · **0** `retry_queue.tmp` files · `retry_queue.json` parses as valid
JSON · no acquisition process remains.

## 2. Exact stop point

| | |
|---|---|
| Last completed block | **2018-02** (manifest written, `complete: true`) |
| Block in progress when stopped | **2018-03** |
| Last hourly file written | `2018-03-09 13:00 UTC` |
| Files in cache (all years) | **1,999** `.bi5` (90 MB), of which 100 are legitimate empty (404) hours |
| Retry queue | 1 pending: `2018-03-01T06:00:00+00:00` — preserved, will be retried when 2018-03 resumes |
| Blocks written | `xauusd_2018-01.json` (complete), `xauusd_2018-02.json` (complete) |

2018-03 has **no** block manifest, which is correct: a manifest is written only when a block finishes. Re-running
`run 2018-03` later resumes from the cache and refetches nothing.

## 3. Existing files preserved

Nothing was deleted. All tick files, hourly cache artefacts, block manifests, source hashes, the retry queue, the day
manifest and the six availability-pilot fixtures are intact. The full 2018-2024 acquisition can resume with
`run 2018-03 2024-12`.

## 4. Final six-day availability pilot verdict

### PASS (6/6)

| Day | Verdict | Ticks | Hours data/empty | Failed checks |
|---|---|---|---|---|
| 2018-02-14 | PASS | 283,453 | 23/1 | — |
| 2018-09-12 | PASS | 129,454 | 23/1 | — |
| 2019-03-13 | PASS | 93,361 | 23/1 | — |
| 2019-10-16 | PASS | 227,478 | 23/1 | — |
| 2020-03-18 | PASS | 369,778 | 23/1 | — |
| 2020-09-16 | PASS | 213,719 | 23/1 | — |

Every day: 24/24 hourly files attempted, decoder succeeded, manifest entry present, monotonic timestamps, all prices
positive, `ask > bid` throughout, Phase 9 duplicate policy matched, source hashes present, 5s/1m structure and
execution streams rebuild deterministically, and no unexplained large missing period. The single empty hour each day
is the scheduled daily break. **Data quality only** — these days are not used for strategy performance (D42 §6).

## 5. 2022 acquisition started

Yes: `staged_acquisition run 2022-01 2022-12`, same D41 transport — single request stream, resume from cache, atomic
writes, persistent retry queue, adaptive pacing, 429 cooldown, scheduled closures skipped only where the canonical
calendar is certain.

One transport-only change was made first: the runner now prints a **progress line per completed day** (cumulative
hours, seconds per file, retries, 429s, 5xx, unresolved). The previous version printed only at block completion,
which left a healthy six-hour run indistinguishable from a hung one. Fetch behaviour is unchanged.

## 6. Existing 2022 coverage reused

Inventoried before downloading: **3 days** of 2022 already present and valid — `2022-03-08`, `2022-10-19`,
`2022-11-24` — 72 cached hourly artefacts and 3 decoded tick parquet files carrying 674,994 ticks with **0**
duplicates, **0** bad spreads and **0** non-positive prices. These are reused, not refetched: `fetch_hour` returns a
cached hour without issuing a request.

## 7-8. Acquisition progress and estimated completion

Measured, not assumed (first 10 minutes of the run): **47 hourly files, mean 13.2 s/file**, 7 retries, **0** HTTP
429, **6** HTTP 5xx. Throughput is bimodal — bursts at ~1.7 s/file, then a server-side stall (one 250 s) that the
backoff absorbs. The constraint is Dukascopy 5xx responses, not rate limiting.

| Rate | Remaining 5,782 hours |
|---|---|
| 13.2 s/file (measured so far) | ≈ **21 hours** |
| 9.8 s/file (best sustained window) | ≈ 16 hours |
| 42 s/file (the 2018 run's rate) | ≈ 67 hours |

**Estimate: roughly one day**, with a worst case near three if the feed degrades to the 2018 behaviour. This will be
re-measured and reported rather than extrapolated.

## 9. Phase 15A protocol hash

`docs/acceptance/phase15a-2022-development-pilot.md` (CBR-ACC-015A v1.0) is written and **frozen before any signal
generation**:

| | |
|---|---|
| Protocol SHA-256 | `baba0fff090a331c7b9209d8fb41468d93473880304b2f64e3325a0b81389d09` |
| PC4 spec hash | `62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7` |
| Execution config hash | `12be582e16b9fbf0fdec9322200446f539a8f2ae08efba8eb7d2ca83f22b0551` |
| Simulator version | `14A.1` |
| Drift | none on any of the three dimensions |

`cbr.engine.phase15a_protocol` pins all three and a test fails if any drifts, so a post-hoc protocol edit cannot be
silent. The frozen span is 2022-01-01 → 2022-12-31 and the permitted verdicts are PROMISING / INCONCLUSIVE /
NEGATIVE.

## 10. TradingView Pine track status

`research/tradingview/cbr1h-pc4-research-strategy.pine` — Pine Script v6 strategy **CBR1H PC4 Research Strategy**,
first draft, marked NON-AUTHORITATIVE / EXPLORATORY in its header.

Implemented: causal ATR zig-zag swings, the condition classifier with the median-correction rule, range position,
hour-anchored overextension with duration / no-pullback / two-sided / size gates, HVCS with the restored
one-violation tolerance and the extension-extreme end bar, HVCS continuity, the previous-15m take with the E1H-023
exception, new-extreme-in-Q, the type-3 trigger, variant B's parent-plus-50%-pullback, the 22-52 timing window,
rollover and Sydney no-trade windows, stop from the structure anchor plus buffer, the 50% target, and an on-chart
status table showing the **first failing rule** as the rejection reason.

Six translation differences are declared in the file header (TD-1…TD-6), the largest being that TradingView has no
Dukascopy tick-mid feed, so the 5-second trigger is approximated on chart bars and degrades to a 1-minute
approximation on coarser charts; the script says which tier it is actually using. **Not yet compiled in
TradingView** — it has had a static review only, and first compilation is expected to need fixes. Per D42 §20, any
Pine/Python disagreement is treated as a Pine translation difference first.

## 11. Tests

**736 passed**, 0 failed, 0 skipped. `ruff check src tests` clean. Seven tests are new: the protocol freeze and the
2022 completeness gate, including that no unresolved market-open hour can silently disappear and that a scheduled
closure can never pad the open-hour accounting.

## 12. Blockers before the 2022 performance run

| # | Blocker | Status |
|---|---|---|
| 1 | **2022 acquisition incomplete** — 5,789 of 5,894 open hours outstanding; gate reads INCOMPLETE | in progress, ≈ 1 day |
| 2 | **Decode stage not run** — 257 of 260 trading days have no tick parquet, 1m/5s structure bars or manifest entry | blocked by 1 |
| 3 | **No historical signal-generation runner exists** — PC4 has only ever run on parity hours and synthetic data; producing a year of frozen PC4 signals is a separate component | to build |
| 4 | **No Phase 15A metrics or package writer** — the eight review-package artefacts and the run manifest need building | to build |
| 5 | **Determinism rerun harness** for the pilot's required repeat run | to build |

Items 3-5 are construction, not measurement, and will be built while acquisition runs; none of them inspects an
outcome. **No performance is run on January, Q1, six months or "the completed months" (D42 §10):** the first and
only pilot run will cover the entire frozen 2022 span after the gate reads COMPLETE.

### Current 2022 completeness gate

| Field | Value |
|---|---|
| requested trading days | 260 |
| requested open hours | 5,894 |
| successful hours | 103 |
| scheduled closures | 346 |
| legitimate empty hours | 3 |
| unresolved failures | 5,789 |
| retry count | 0 |
| HTTP 429 | 0 |
| HTTP 5xx | 0 |
| bytes | 3,878,894 |
| tick count | 674,994 |
| duplicates | 0 |
| bad spreads | 0 |
| non-positive prices | 0 |
| unexpected gaps | 2 |
| **hours fully accounted** | **true** |
| **verdict** | **INCOMPLETE** |

Retry/429/5xx read 0 because no 2022 block manifest has been written yet; they are populated per block on
completion. The two unexpected gaps are hours inside the existing fixture days for which the feed holds no file —
they are listed individually in `reports/phase15a-2022-completeness.json`, never absorbed into "empty".
