# Phase 10 DXY Context Acceptance Report

Generated 2026-09-15T00:19:49.490537+00:00 by `src/cbr/dxy/phase10_acceptance.py` against CBR-ACC-010 v1.0.

## Verdict: **PASS WITH CONCERNS**

| Criterion | Status |
|---|---|
| AC10-01 | MET |
| AC10-02 | MET |
| AC10-03 | MET |
| AC10-04 | MET |
| AC10-04b | MET |
| AC10-05 | MET |
| AC10-06 | MET |
| AC10-07 | MET |
| AC10-08 | MET |
| AC10-09 | MET |
| AC10-10 | MET |

## Concerns

- Causal quote shown for up to 10 decision minutes at the start of a ruled vendor outage (max age 10 min, REDUCED confidence) before it becomes UNAVAILABLE; hindsight mask marks the full outage. Ledger use: OQ-31.
- On 9 of 9 EST (winter) trading days, last-closed 15m DXY context has no quotes (NO_QUOTES/VENDOR_MISSING) for decision times 00:15-01:00 UTC (Asia hour 1, tradable after NT_SYDNEY): the CFD does not quote 18:00-20:00 New York. CBR setups there will carry DXY UNAVAILABLE.
- Report artifact, not a data property: each day file starts at 00:00 UTC, so windows reaching back before 00:00 are NOT_LOADED for the first 15 (15m) / 60 (1h) decision minutes of every test day. Contiguous multi-day loads (engine use) don't have this.
- 60 last-closed window decision times REDUCED (low coverage) on 2018-2019 days: early DXY CFD quoting is thinner (Phase 9: 16-20% zero 1m returns in 2019).
- IMPL thresholds (flat_epsilon 0, min_coverage_full 0.5, max_quote_age 10 min) validated on 24 days only; revalidate on AC-11B history before baseline use.
- No DXY highs/lows, extension extremes, range condition or DXY shifts: those need OQ-25 and remain Phase 17/18 ablation inputs; 1m/5s DXY structure excluded (D12-6).

## AC10-10: last-closed direction agreement vs DX (FULL on both, |DX move| ≥ 0.01)

- 15m: 1154 / 1173 = 0.9838
- 1h: 340 / 344 = 0.9884

## Ruled vendor-gap intervals (D12-1, D12-2)

- 2019-03-11T00:00:00+00:00 → 2019-03-11T01:00:00+00:00: hindsight mask on every minute = True; causal quote still shown for 0 decision minutes (max age nan s)
- 2020-03-09T20:00:00+00:00 → 2020-03-09T21:00:00+00:00: hindsight mask on every minute = True; causal quote still shown for 10 decision minutes (max age 600 s)

## Per-day summary

| Day | DX ref | Quote available | 15m last FULL/REDUCED/UNAVAIL | 1h last FULL/REDUCED/UNAVAIL | 15m agree | 1h agree | Hash |
|---|---|---|---|---|---|---|---|
| fixture 2025-10-20 | True | 0.875 | 1260/0/180 | 1260/0/180 | 40/41 | 17/17 | `7d09c81d975b` |
| fixture 2025-10-21 | True | 0.875 | 1260/0/180 | 1260/0/180 | 57/59 | 19/19 | `c9f11a0d5b81` |
| fixture 2025-10-22 | True | 0.875 | 1260/0/180 | 1260/0/180 | 46/47 | 16/16 | `a14616ecedc6` |
| fixture 2025-10-23 | True | 0.875 | 1260/0/180 | 1260/0/180 | 40/43 | 16/16 | `a9fc6bcd7217` |
| fixture 2025-10-24 | True | 0.875 | 1260/0/180 | 1260/0/180 | 49/50 | 14/14 | `6687d8bb461d` |
| fixture 2025-11-09 | True | 0.0 | 0/0/1440 | 0/0/1440 | 0/0 | 0/0 | `538c037b9118` |
| fixture 2025-11-10 | True | 0.875 | 1260/0/180 | 1260/0/180 | 55/56 | 17/17 | `abdf14e135a5` |
| fixture 2025-11-11 | True | 0.875 | 1260/0/180 | 1260/0/180 | 44/44 | 13/14 | `469dd0868d6f` |
| MID-2018 2018-02-21 | False | 0.8729 | 1245/15/180 | 1260/0/180 | — | — | `4a01f6880fde` |
| MID-2019 2019-04-17 | True | 0.875 | 1245/15/180 | 1260/0/180 | 52/52 | 16/16 | `50beb19e6680` |
| MID-2020 2020-06-17 | True | 0.875 | 1260/0/180 | 1260/0/180 | 62/63 | 20/20 | `20ed1f0243fb` |
| MID-2021 2021-08-18 | True | 0.875 | 1230/30/180 | 1260/0/180 | 50/50 | 15/15 | `f125cf90c83c` |
| MID-2022 2022-10-19 | True | 0.875 | 1260/0/180 | 1260/0/180 | 75/76 | 19/19 | `af4f3302f514` |
| MID-2023 2023-12-20 | True | 0.875 | 1260/0/180 | 1260/0/180 | 50/50 | 18/19 | `4652baf50556` |
| MID-2024 2024-03-20 | True | 0.875 | 1260/0/180 | 1260/0/180 | 46/47 | 12/13 | `4ac9b5331977` |
| DST-SPRING-2019 2019-03-11 | True | 0.8333 | 1200/0/240 | 1200/0/240 | 40/41 | 11/11 | `dfd9fd9e68b9` |
| DST-AUTUMN-2023 2023-11-06 | True | 0.875 | 1260/0/180 | 1260/0/180 | 57/59 | 18/18 | `c0ca14d16c88` |
| US-HOLIDAY-2022-THANKSGIVING 2022-11-24 | True | 0.7146 | 1020/0/420 | 989/0/451 | 57/58 | 14/14 | `0777ea955a84` |
| MONDAY-REOPEN-2021 2021-02-01 | True | 0.875 | 1260/0/180 | 1260/0/180 | 56/56 | 16/17 | `0c18f837117d` |
| DXY-CFD-FIRST-MONTH-2018 2018-01-17 | False | 0.8681 | 1230/30/180 | 1260/0/180 | — | — | `245fda7dcf64` |
| HIGHVOL-2020-03-09 2020-03-09 | True | 0.8403 | 1200/0/240 | 1200/0/240 | 77/77 | 19/19 | `1589972706b1` |
| HIGHVOL-2020-03-16 2020-03-16 | True | 0.875 | 1260/0/180 | 1260/0/180 | 74/77 | 19/19 | `2a1a5da078cb` |
| HIGHVOL-2022-03-08 2022-03-08 | True | 0.875 | 1260/0/180 | 1260/0/180 | 67/67 | 16/16 | `03c1e438710c` |
| HIGHVOL-2024-04-12 2024-04-12 | True | 0.875 | 1260/0/180 | 1260/0/180 | 60/60 | 15/15 | `092ab82d6cc1` |

## Last-closed 15m UNAVAILABLE decision minutes by UTC hour

| Day | NY offset | Hours (UTC: minutes) |
|---|---|---|
| fixture 2025-10-20 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| fixture 2025-10-21 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| fixture 2025-10-22 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| fixture 2025-10-23 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| fixture 2025-10-24 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| fixture 2025-11-09 | -5 | 00: 60, 01: 60, 02: 60, 03: 60, 04: 60, 05: 60, 06: 60, 07: 60, 08: 60, 09: 60, 10: 60, 11: 60, 12: 60, 13: 60, 14: 60, 15: 60, 16: 60, 17: 60, 18: 60, 19: 60, 20: 60, 21: 60, 22: 60, 23: 60 |
| fixture 2025-11-10 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| fixture 2025-11-11 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| MID-2018 2018-02-21 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| MID-2019 2019-04-17 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| MID-2020 2020-06-17 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| MID-2021 2021-08-18 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| MID-2022 2022-10-19 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| MID-2023 2023-12-20 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| MID-2024 2024-03-20 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| DST-SPRING-2019 2019-03-11 | -4 | 00: 60, 01: 15, 21: 45, 22: 60, 23: 60 |
| DST-AUTUMN-2023 2023-11-06 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| US-HOLIDAY-2022-THANKSGIVING 2022-11-24 | -5 | 00: 60, 01: 15, 18: 45, 19: 60, 20: 60, 21: 60, 22: 60, 23: 60 |
| MONDAY-REOPEN-2021 2021-02-01 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| DXY-CFD-FIRST-MONTH-2018 2018-01-17 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| HIGHVOL-2020-03-09 2020-03-09 | -4 | 00: 15, 20: 45, 21: 60, 22: 60, 23: 60 |
| HIGHVOL-2020-03-16 2020-03-16 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |
| HIGHVOL-2022-03-08 2022-03-08 | -5 | 00: 60, 01: 15, 22: 45, 23: 60 |
| HIGHVOL-2024-04-12 2024-04-12 | -4 | 00: 15, 21: 45, 22: 60, 23: 60 |

## Check details

- AC10-01: 48 / 48 passed
- AC10-02: 24 / 24 passed
- AC10-03: 24 / 24 passed
- AC10-04: 26 / 26 passed
- AC10-04b: 24 / 24 passed
- AC10-05: 24 / 24 passed
- AC10-06: 24 / 24 passed
- AC10-07: 24 / 24 passed
- AC10-08: 24 / 24 passed
- AC10-09: 25 / 25 passed
- AC10-10: 2 / 2 passed
