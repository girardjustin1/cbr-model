# OQ-24 availability pilot — interim report

**Doc:** CBR-RPT-OQ24-PILOT · **Date:** 2026-09-18 · **Ruling:** D40 §4-6 · **Status:** COMPLETE — overall verdict **PASS**
Data quality only: no signals, no fills, no P&L, no price-action selection.

The six dates were **predeclared and committed before any byte was fetched** (commit `e55f0e5`), are ordinary
mid-week trading days, and none duplicates an existing project fixture.

## Per-day results — all six complete

| Day | Hours cached | Hours with data | Empty hours | Ticks | Dups | Bad spreads | 1m / 5s bars | Verdict |
|---|---|---|---|---|---|---|---|---|
| 2018-02-14 | 24/24 | 23 | 1 (22 UTC break) | 283,453 | 0 | 0 | 1,380 / 16,333 | **PASS** |
| 2018-09-12 | 24/24 | 23 | 1 (21 UTC break) | 129,454 | 0 | 0 | 1,379 / 15,160 | **PASS** |
| 2019-03-13 | 24/24 | 23 | 1 (21 UTC break) | 93,361 | 0 | 0 | 1,373 / 12,315 | **PASS** |
| 2019-10-16 | 24/24 | 23 | 1 (21 UTC break) | 227,478 | 0 | 0 | 1,374 / 14,749 | **PASS** |
| 2020-03-18 | 24/24 | 23 | 1 (21 UTC break) | 369,778 | 0 | 0 | 1,380 / 16,330 | **PASS** |
| 2020-09-16 | 24/24 | 23 | 1 (21 UTC break) | 213,719 | 0 | 0 | 1,380 / 15,810 | **PASS** |

**Overall verdict: PASS.**

Every D40 §5 check passes on every day: 24/24 hourly files available · the single empty hour on each day is the
scheduled daily break, correctly DST-aware · decoder succeeded · timestamps monotonic · no non-positive prices ·
`ask > bid` throughout · duplicate counts match the Phase 9 manifest · 5s and 1m STRUCTURE bars build
deterministically · the bid/ask execution stream builds · manifest and source hashes generated · no unexplained
missing period · canonical bars built.

**Availability finding.** Historical Dukascopy XAUUSD tick history is present and clean back to 2018 at volumes
comparable to the recent stored fixtures (93k-370k ticks/day against a 310k mean for 2025 days). The D40 §6 stop
condition — materially incomplete older history — **is not met**. Full acquisition is therefore authorized to
proceed under D41 §3.

## Throughput — the material engineering finding

| Measurement | Value |
|---|---|
| Best observed | ~13 s per hourly file |
| Sustained single stream | ~50 s per hourly file |
| Under rate limiting | ~100-150 s per hourly file |
| Observed server response | **HTTP 429** once concurrent requests were made |
| Pilot total | 144 hourly files in ~100 minutes (~42 s/file average) |

Projected over the approved span, after removing the 2,430 scheduled-closure hours the staged downloader never
requests (**41,418 request-hours** of 43,848):

| At | Full 2018-2024 acquisition |
|---|---|
| 13 s/file | ≈ 6.2 days continuous |
| 42 s/file (pilot average) | ≈ 20 days continuous |
| 150 s/file | ≈ 72 days continuous |

Storage remains trivial (≈ 5.6 GB). The cost of Option A is wall-clock time; D41 §12 accepts that, and the staged
downloader is built to survive it.
