# OQ-24 availability pilot — interim report

**Doc:** CBR-RPT-OQ24-PILOT · **Date:** 2026-09-18 · **Ruling:** D40 §4-6 · **Status:** IN PROGRESS
Data quality only: no signals, no fills, no P&L, no price-action selection.

The six dates were **predeclared and committed before any byte was fetched** (commit `e55f0e5`), are ordinary
mid-week trading days, and none duplicates an existing project fixture.

## Per-day results

| Day | Hours cached | Hours with data | Empty hours | Ticks | Dups | Bad spreads | 1m / 5s bars | Verdict |
|---|---|---|---|---|---|---|---|---|
| 2018-02-14 | 24/24 | 23 | 1 (22 UTC = 17:00 EST break) | 283,453 | 0 | 0 | 1,380 / 16,333 | **PASS** |
| 2018-09-12 | 24/24 | 23 | 1 (21 UTC = 17:00 EDT break) | 129,454 | 0 | 0 | 1,379 / 15,160 | **PASS** |
| 2019-03-13 | 12/24 | — | — | — | — | — | — | fetching |
| 2019-10-16 | 0/24 | — | — | — | — | — | — | queued |
| 2020-03-18 | 0/24 | — | — | — | — | — | — | queued |
| 2020-09-16 | 0/24 | — | — | — | — | — | — | queued |

Every D40 §5 check passes on both completed days: hourly files available · the single empty hour on each day is the
scheduled daily break, correctly DST-aware · decoder succeeded · timestamps monotonic · no non-positive prices ·
`ask > bid` throughout · duplicate count matches the Phase 9 manifest · 5s and 1m STRUCTURE bars build
deterministically · the bid/ask execution stream builds · manifest and source hashes generated · no unexplained
missing period · canonical bars built.

Coverage is full-day: 2018-02-14 runs 00:00:00.066 → 23:59:59.732; 2018-09-12 runs 00:00:00 → 23:59:48.

**Interim availability finding:** 2018 tick history is present and clean, at volumes comparable to 2025 fixtures
(283k and 129k ticks/day against a 310k mean for the stored recent days). Nothing so far suggests the materially
incomplete history that D40 §6 would stop on.

## Throughput — the material finding

| Measurement | Value |
|---|---|
| Best observed | ≈ 13 s per hourly file |
| Sustained after warm-up | ≈ 50 s per hourly file |
| Current, under rate limiting | ≈ 100-150 s per hourly file |
| Observed server response | **HTTP 429** once concurrent requests were made |

The feed rate-limits, and the existing fetcher's backoff is doing its job. But projected over the approved span —
1,827 weekdays × 24 hours = **43,848 hourly files**:

| At | Full 2018-2024 acquisition takes |
|---|---|
| 13 s/hour (best) | ≈ 6.6 days continuous |
| 50 s/hour (sustained) | ≈ 25 days continuous |
| 150 s/hour (current) | ≈ 76 days continuous |

Storage remains trivial (≈ 5.6 GB). **The cost of Option A is wall-clock time, and it is larger than the earlier
estimate implied.** Parallelising requests would very likely worsen rate limiting rather than help — the 429 above
appeared as soon as a second stream ran.

This is an owner-level decision and the reason this report is interim: the pilot itself is unaffected and continues.
