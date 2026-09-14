# Phase 9: Historical Data Pipeline Acceptance Criteria

**Doc:** CBR-ACC-009 · **Version:** v2.0 · **Approved:** 2026-09-14 (owner: "APPROVED WITH MINOR CHANGES", decision D11)
**Supersedes:** AC-11 v1 (complete 2018-2024 Dukascopy history as a Phase 9 requirement)
**Implementation:** `src/cbr/data/phase9_acceptance.py` → `reports/phase9-data-acceptance.{json,md}`
**Exceptions register:** `reports/phase9-exceptions.yaml`

Sample days, tick windows and thresholds below were **declared before the sample data was downloaded**. Failing
sample days are never dropped or replaced.

---

## 1. Criteria

| ID | Criterion | Scope |
|---|---|---|
| AC-01 | 1m candle coverage for every trading day in the course-fixture windows, XAUUSD and DOLLARIDXUSD | Fixtures |
| AC-02 | Tick windows (entry hour −2 h to +2 h) for all 3 course entries, both instruments | Fixtures |
| AC-03 | Decoder parity: ticks identical to the reference CLI (285,935 ticks, 2025-11-10); candle open/close identical to tick-built bars | Fixtures |
| AC-04 | Integrity: no duplicate or out-of-order timestamps, UTC, minute/5s alignment, no non-positive prices, no crossed quotes, consistent OHLC, manifest hashes match | Fixtures + samples |
| AC-05 | Determinism: 5s and 1m bars rebuilt from stored ticks equal the stored bars | Fixtures + sample tick windows |
| AC-06 | Reconciliation: tick counts; 5s → 1m roll-up exact; tick-window 1m vs candle files | Fixtures + sample tick windows |
| AC-07 | Every missing minute classified (weekend, daily 17:00-18:00 New York break, or unexpected); unexpected gaps listed | Fixtures + samples |
| AC-08 | Spikes and wide spreads flagged and reported (never removed) | Fixtures + samples |
| AC-09 | Cross-feed comparison documented: XAUUSD vs GC **and** DXY CFD vs DX | Fixtures + samples |
| AC-10 | Timezone and price verified against Tom's chart points | Fixtures |
| **AC-11A** | **Spot pipeline proven on the 16-day stratified 2018-2024 sample (§2, §3)** | Samples |
| **AC-11B** | **Complete historical spot dataset: DEFERRED** (§5) | Not required for Phase 9 |

---

## 2. AC-11A: stratified sample (pre-declared)

All days are in the development/validation periods (2018-2024); none is in the holdout. Use: data integrity and feed
agreement only, with no trade simulation and no P&L.

| Sample id | Date (UTC) | Rule |
|---|---|---|
| MID-2018 | 2018-02-21 | Wednesday on/after the 15th; month rotates 2, 4, 6, 8, 10, 12, then 3 |
| MID-2019 | 2019-04-17 | same |
| MID-2020 | 2020-06-17 | same |
| MID-2021 | 2021-08-18 | same |
| MID-2022 | 2022-10-19 | same |
| MID-2023 | 2023-12-20 | same |
| MID-2024 | 2024-03-20 | same |
| DST-SPRING-2019 | 2019-03-11 | Monday after the US spring clock change (2019-03-10) |
| DST-AUTUMN-2023 | 2023-11-06 | Monday after the US autumn clock change (2023-11-05) |
| US-HOLIDAY-2022-THANKSGIVING | 2022-11-24 | US holiday, thin trading |
| MONDAY-REOPEN-2021 | 2021-02-01 | First Monday of February 2021 (weekend reopen) |
| DXY-CFD-FIRST-MONTH-2018 | 2018-01-17 | Wednesday on/after the 15th of the DXY CFD's first full month |
| HIGHVOL-2020-03-09 | 2020-03-09 | Pre-declared high-volatility date |
| HIGHVOL-2020-03-16 | 2020-03-16 | Pre-declared high-volatility date |
| HIGHVOL-2022-03-08 | 2022-03-08 | Pre-declared high-volatility date |
| HIGHVOL-2024-04-12 | 2024-04-12 | Pre-declared high-volatility date |

**Tick windows (5s validation outside the holdout), 00:00-03:00 UTC (Asia hours 1-3), both instruments:**
DXY-CFD-FIRST-MONTH-2018 · HIGHVOL-2020-03-16 · US-HOLIDAY-2022-THANKSGIVING · MID-2024.

## 3. AC-11A thresholds (pre-declared)

| Check | Pair / instrument | Threshold |
|---|---|---|
| 1m return correlation, lag 0 | XAUUSD spot vs GC front month | ≥ 0.95 |
| Best lag in −3…+3 min | XAUUSD vs GC | 0 min |
| Intraday basis jump (1m) | XAUUSD vs GC | ≤ $5.00, excluding roll minutes (front-month instrument change) |
| Price-scale sanity | XAUUSD vs GC | median \|GC / spot − 1\| ≤ 2% |
| 1m return correlation, lag 0 | DXY CFD vs DX front month | ≥ 0.90 |
| Best lag in −3…+3 min | DXY CFD vs DX | 0 min |
| Price-scale sanity | DXY CFD vs DX | median \|DX / CFD − 1\| ≤ 2% |
| Integrity / determinism / reconciliation / gaps / flags | each sample day, both instruments | AC-04…AC-08 as above |

Minimum overlap for a feed comparison: 60 common minutes. Less is itself recorded as a failure to classify.

---

## 4. Failure classification (owner change to the verdict rule)

Every failed check, on any fixture or sample day, is recorded in `reports/phase9-exceptions.yaml` with one class and
an explanation backed by evidence:

| Class | Meaning | Effect on verdict |
|---|---|---|
| `PIPELINE_ERROR` | Our code decoded, built, stored or compared data incorrectly | **FAIL until resolved** |
| `DATA_ERROR` | The vendor data itself is wrong (corrupt, missing hours, bad prints) | **FAIL until resolved** (repaired, re-sourced, or excluded by a documented rule that doesn't bias downstream use) |
| `EXPECTED_MARKET_BEHAVIOR` | Real market conditions explain it (holiday session, extreme volatility, limit moves) | Concern; not a failure, if it doesn't invalidate the intended downstream use |
| `EXPECTED_FEED_DIFFERENCE` | A known structural difference between feeds explains it (contract roll, CFD vs futures session hours, basis carry, thinner DXY CFD) | Concern; not a failure, if it doesn't invalidate the intended downstream use |
| `UNEXPLAINED_FEED_DIFFERENCE` | Feeds disagree and no evidence-backed explanation exists | **FAIL until resolved** |
| `UNCLASSIFIED` | Not yet investigated | **FAIL** (verdict can't be issued) |

Failing days are **never dropped or replaced**.

## 5. AC-11B: deferred historical spot acquisition

- Not a Phase 9 requirement. It remains an **explicit unresolved dependency** for whichever later phase requires full
  spot history. That depends on the baseline-feed decision (OQ-24), which must be frozen before Phase 14.
- No bulk download is started without owner instruction.

## 6. Verdict rule

| Verdict | Condition |
|---|---|
| **PASS** | AC-01…AC-10, AC-11A and AC-11B met; no failures, or only EXPECTED_* concerns |
| **PASS WITH CONCERNS** | AC-01…AC-10 and AC-11A met; every failure classified, none of them PIPELINE_ERROR / DATA_ERROR / UNEXPLAINED_FEED_DIFFERENCE unresolved; AC-11B outstanding and/or documented EXPECTED_* concerns |
| **FAIL** | Any unresolved PIPELINE_ERROR, DATA_ERROR or UNEXPLAINED_FEED_DIFFERENCE; any UNCLASSIFIED failure; or any of AC-01…AC-10 / AC-11A not met |

## 7. Phase 10 entry conditions

Phase 10 does not begin until: AC-01…AC-10 are resolved, AC-11A is complete, every failure is classified, a Phase 9
verdict is issued, and the owner accepts it.
