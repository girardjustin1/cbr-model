# V-1 Assessment: TradingView Exports Supplied by the Owner

**Doc:** CBR-V1-ASSESS-001 · **Date:** 2026-09-15 · **Ruling:** D22 (D21 follow-up) · **Status:** FOR OWNER DECISION
File and metadata inspection only. No prices reproduced, no engine output, no comparison with course examples, no
calibration run. Generated matrices: `reports/tradingview-exports-inspection-charts.{md,json}`
(`python -m cbr.engine.v1_ingest inspect references/charts --report`). **Update D23:** `references/tom-chart-data` holds FOREXCOM:XAUUSD exports; see `docs/decisions/v1-tom-chart-data-assessment.md`.

## 1. Files found

A search of the whole project (excluding `.venv`, `.git`, caches and video frames) found TradingView exports only in
`references/charts/`. There are 12 CSV files, all downloaded from `https://www.tradingview.com/` (macOS
`kMDItemWhereFroms` attribute) on 2026-09-15.

| Instrument | Files (timeframe) |
|---|---|
| Gold | `FX_XAUUSD, 1.csv` (1m), `, 5.csv` (5m), `, 15.csv` (15m), `, 60.csv` (1h), `, 240.csv` (4h), `, 1D.csv` (1D) |
| DXY | `TVC_DXY, 1.csv` (1m), `, 5.csv`, `, 15.csv`, `, 60.csv`, `, 240.csv`, `, 1D.csv` |

Common format for all 12:
- **Columns:** `time, open, high, low, close, Volume, Volume MA` (`Volume MA` is a chart indicator column).
- **Timestamps:** unix epoch seconds, so UTC by definition. The chart's timezone setting doesn't change them, and no
  conversion is needed.
- **Volume:** populated for Gold; empty for DXY.
- **Size:** about 7,000 bars per intraday file (TradingView's export depth for this account).

## 2. Symbol identity

| Evidence | Gold | DXY |
|---|---|---|
| TradingView export file name `<EXCHANGE>_<TICKER>, <interval>.csv` | `FX_XAUUSD` → **`FX:XAUUSD`** | `TVC_DXY` → **`TVC:DXY`** |
| Metadata inside the CSV | none (TradingView exports carry no symbol field) | none |
| Download origin attribute | tradingview.com (source site only, not the symbol) | same |
| Owner screenshots in the project | none | none |
| Feed on Tom's charts (slide OCR) | `Gold Spot / U.S. Dollar · FOREXCOM` (V1H-session_timing 00:01:50, VP2-analysis 00:02:52, VP2-collection 00:06:30, live-trade walkthroughs) | `TVC` (live trades 1-3, trade example 1, VP2 DXY correlation) |

**Gold: `SYMBOL_MISMATCH`.** The supplied Gold exports are `FX:XAUUSD`, not `FOREXCOM:XAUUSD`.
- The file name is the only identity evidence, and TradingView generates it from the chart symbol, so it is reliable
  for the exchange prefix.
- Which data provider TradingView shows for the `FX` prefix can't be confirmed from the files; a symbol-info screenshot
  would settle it.
- Classification: **REFERENCE_ONLY**, plus **TRADINGVIEW_REFERENCE_FIXTURE** for the 5m / 15m / 1h / 4h / 1D files.
  They are not rejected from all future use.

**DXY:** `TVC:DXY` is the same TradingView feed label Tom's DXY charts show.

## 3. History coverage

**Gold 1m: `ONE_MINUTE_HISTORY_INSUFFICIENT`.**
- It spans 2026-09-08 08:15 → 2026-09-15 11:54 UTC (7,099 bars).
- It contains none of 2025-10-20…24, 2025-10-22 or 2025-11-07…11.
- Days short of each window start:

| Window | Days short |
|---|---|
| CX-LT1-1 | 322 |
| CX-TE1-1 | 319 |
| CX-LT3-2 | 304 |
| CAL 10/22 | 321 |
| CAL 11/11 | 301 |

**Other Gold timeframes:**

| Timeframe | Span | V-1 windows |
|---|---|---|
| 5m | from 2026-08-10 | none covered |
| 15m | from 2026-05-29 | none covered |
| 1h | from 2025-07-08 | all five FULL (every scheduled-open hour present) |
| 4h | from 2022-02-23 | all five spanned |
| 1D | from 1999-07-06 | all five spanned |

**V-1 eligible Gold files: none** (wrong symbol, and no 1m history for the windows).

## 4. DXY reference potential (evidence for OQ-26; OQ-26 unchanged)

OQ-26 asks for an independent reference for 1m/5s DXY structure.

| TVC:DXY file | Span | Overlap with stored Dukascopy DXY data | What it could validate |
|---|---|---|---|
| 1m | 2026-09-08 → 09-15 | **none** (stored DXY days: 2018-2024 samples, 2025-10-20…25, 2025-11-09…11) | 1m structure only if Dukascopy DXY ticks were fetched for 2026-09-08…15 (after the holdout period) |
| 5m / 15m | from 2026-08-13 / 2026-06-10 | none | same, at 5m/15m |
| 1h | from 2025-09-08 | covers the Oct–Nov 2025 fixture days | 1h DXY candles and direction (Phase 10 context) on fixture days |
| 4h | from 2022-10-13 | covers sample days 2022-10-19, 2022-11-24, 2023-11-06, 2023-12-20, 2024-03-20, 2024-04-12 | 4h context on those sample days |
| 1D | from 2001-11-30 | all | daily context |

**Findings:**
- The supplied files can't satisfy OQ-26's 1m/5s need for any stored day.
- They could partly support it at 1h/4h, and at 1m/5m for a recent post-holdout week if Dukascopy DXY ticks for those
  days were fetched.
- `TVC:DXY` is an index feed; the Dukascopy DOLLARIDXUSD CFD is a different instrument, so level offsets are expected.
- Any use needs an owner decision.

## 5. Screenshots and metadata

No screenshots or metadata files in the project establish the owner's export symbol, feed or chart timezone.

Still required for V-1, in `data/raw/tradingview/screenshots/`:
1. A `*symbol*` screenshot showing `FOREXCOM:XAUUSD` in TradingView's symbol info, including the exchange/provider line.
2. A `*timezone*` screenshot showing the chart timezone set to UTC.

With unix-time exports, the timezone screenshot documents the setting; the timestamps are UTC regardless.

## 6. Deterministic ingestion when a valid export exists (D22-8)

`python -m cbr.engine.v1_ingest slice "<FOREXCOM_XAUUSD, 1.csv>"` handles a valid 1m export:
- It writes each fully covered V-1 window as the original CSV rows for [start, end) to `data/raw/tradingview/v1_*.csv`.
- It records `source_file`, `source_sha256`, `slice_sha256`, row count and window in `v1_provenance.json`.
- The original file is never modified, and an existing slice with different content is never overwritten.
- It refuses any symbol other than `FOREXCOM:XAUUSD` and any timeframe other than 1m.

So the owner needn't re-export data that already exists under TradingView's default file name.

## 7. V-1 state

**`V1_SYMBOL_MISMATCH`** (secondary: `ONE_MINUTE_HISTORY_INSUFFICIENT`).
- Gold data exists, but not from `FOREXCOM:XAUUSD`.
- Even if the symbol were right, the 1m history doesn't reach the windows.
- Nothing is sliceable, so this isn't `V1_PARTIALLY_READY`.
- Dukascopy is ready for both calibration days (D21).

## 8. Options (owner decides; none chosen here)

| Option | What | Research impact | D19/D20 protocol change | New calibration days | PC2 change | New owner decision |
|---|---|---|---|---|---|---|
| **A** | Obtain `FOREXCOM:XAUUSD` 1m for the five existing windows (a TradingView plan/session that loads October–November 2025 1m history; export via `slice`) | none: V-1 as approved | no | no | no | no |
| **B** | A FOREX.com-native historical 1m export (e.g. MetaTrader 5 history from a FOREX.com account) for the same windows | same feed family, different export path. Needs checks: symbol mapping, server timezone to UTC conversion (MT5 servers commonly use a non-UTC offset), bar-time convention | yes: source definition in protocol §6 (not the method) | no | no | yes (approve the source and its timestamp conversion) |
| **C** | Approve `FX:XAUUSD` as a replacement fidelity source | V-1 then measures FX:XAUUSD vs Dukascopy, not Tom's FOREXCOM chart feed. Course parity would compare with a different feed than Tom's. The residual between FX and FOREXCOM stays unmeasured | yes (replacement fidelity test, D19-14 B) | **yes if history stays short:** the pre-registered 2025 days aren't in the 1m file; recent non-course days (e.g. 2026-09-08…15, post-holdout) would need a Dukascopy fetch and a new pre-registration before looking at results. The course windows still have no 1m coverage | no (tolerances are outside PC2) | yes (new decision record) |

**Shortest path to Phase 13 without changing the approved protocol: Option A.**

After the files arrive:
1. `slice` (if needed), then `status`.
2. Owner confirmation, then `calibrate`, which is PROPOSED only.
3. Owner approval of δ, τ_price, FEED_NEAR, zero-lag and time tolerances.
4. Freeze the tolerances.
5. Owner authorization of the final Phase 13 run.
