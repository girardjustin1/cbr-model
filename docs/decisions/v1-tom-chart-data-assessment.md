# V-1 Assessment: "Tom Chart Data" (references/tom-chart-data)

**Doc:** CBR-V1-ASSESS-002 · **Date:** 2026-09-15 · **Ruling:** D23 · **Status:** FOR OWNER REVIEW
File, metadata and source-identity inspection only.
- **Not done:** no prices reproduced, no engine output, no comparison with Tom's labelled trades, no calibration, no
  change to PC2 or OQ-26.
- **Originals:** unmodified and hashed.
- **Generated:**
  - `reports/tradingview-exports-inspection-tom-chart-data.{md,json}`
  - `reports/tradingview-source-manifest.json` (families A and B)
  - `reports/tradingview-source-comparison.json`
- **Commands:** `python -m cbr.engine.v1_ingest inspect references/tom-chart-data --report`,
  `python -m cbr.engine.v1_ingest sources`.

## 1. Inventory

12 regular files, no subfolders, no screenshots, no metadata sidecars.

Common properties:
- **Type:** CSV text with columns `time, open, high, low, close, Volume, Volume MA`.
- **Timestamps:** unix epoch seconds, so UTC with no conversion needed. They are strictly increasing with no duplicates.
- **Volume:** `Volume` and `Volume MA` are empty in all 12 files.
- **Origin:** all downloaded from `https://www.tradingview.com/` (macOS download attribute) on 2026-09-15 between
  13:01:03 and 13:02:37 UTC.

| File | Symbol (TradingView export name) | Timeframe (modal bar spacing) | First bar (UTC) | Last bar (UTC) | Rows | SHA-256 (first 16) |
|---|---|---|---|---|---|---|
| FOREXCOM_XAUUSD, 1.csv | FOREXCOM:XAUUSD | 1m | 2026-09-09 00:20 | 2026-09-15 13:01 | 6,281 | `5fb0a1b5d1ca717e…` |
| FOREXCOM_XAUUSD, 5.csv | FOREXCOM:XAUUSD | 5m | 2026-08-13 16:15 | 2026-09-15 13:00 | 6,280 | `5d8f2d185eec39bb…` |
| FOREXCOM_XAUUSD, 15.csv | FOREXCOM:XAUUSD | 15m | 2026-06-10 19:45 | 2026-09-15 13:00 | 6,280 | `69b731582a2e161c…` |
| FOREXCOM_XAUUSD, 60.csv | FOREXCOM:XAUUSD | 1h | 2025-08-22 11:00 | 2026-09-15 13:00 | 6,280 | `dd7814e2227d0f3d…` |
| FOREXCOM_XAUUSD, 240.csv | FOREXCOM:XAUUSD | 4h | 2022-08-23 02:00 | 2026-09-15 10:00 | 6,280 | `a83531dd6fd32a55…` |
| FOREXCOM_XAUUSD, 1D.csv | FOREXCOM:XAUUSD | 1D | 2002-06-18 22:00 | 2026-09-14 22:00 | 6,280 | `891c30eb69cc2304…` |
| TVC_DXY, 1.csv | TVC:DXY | 1m | 2026-09-08 20:31 | 2026-09-15 13:02 | 6,289 | `e839f89ad852e7cb…` |
| TVC_DXY, 5.csv | TVC:DXY | 5m | 2026-08-13 06:05 | 2026-09-15 13:00 | 6,288 | `ec616d90026c4ac5…` |
| TVC_DXY, 15.csv | TVC:DXY | 15m | 2026-06-10 05:45 | 2026-09-15 13:00 | 6,288 | `aa09004f9f3e6001…` |
| TVC_DXY, 60.csv | TVC:DXY | 1h | 2025-09-08 06:00 | 2026-09-15 13:00 | 6,288 | `1602a763e7c5269e…` |
| TVC_DXY, 240.csv | TVC:DXY | 4h | 2022-10-10 23:00 | 2026-09-15 11:00 | 6,288 | `b5b801d7218afc13…` |
| TVC_DXY, 1D.csv | TVC:DXY | 1D | 2001-11-11 22:00 | 2026-09-14 23:00 | 6,280 | `8d77090ca4e334cd…` |

**Timeframes.** Each file's interval comes from its dominant bar spacing, which agrees with its file name. For example,
the 1m file has 6,276 one-minute steps, and the remaining gaps are the daily break and the weekend.
- Present: 1m, 5m, 15m, 1h, 4h, 1D.
- **Absent:** 5-second and 30-minute.

## 2. Source identity

| Evidence | Gold | DXY |
|---|---|---|
| TradingView-generated export name | `FOREXCOM_XAUUSD` → FOREXCOM:XAUUSD | `TVC_DXY` → TVC:DXY |
| Symbol metadata inside the CSV | none (TradingView exports have no symbol field) | none |
| Symbol-info / timezone screenshots | none | none |
| Tom's chart labels (course slide OCR) | `Gold Spot / U.S. Dollar · FOREXCOM` | `TVC` |
| Data differs from another feed with the same ticker | yes: vs owner `FX:XAUUSD` exports on 6,179–6,259 overlapping bars per timeframe (V-1 windows excluded), only 0.03–1.3% of OHLC values identical; median close difference $0.15–0.36. FOREXCOM files carry no volume; FX:XAUUSD files do | n/a |
| Agreement with an independent export of the same symbol | n/a | vs owner `TVC_DXY` exports: ≥ 99.98% identical OHLC on 6,188–6,283 overlapping bars per timeframe (the few differences are the still-forming last bar at export time) |

**Classifications:**
- **Gold: `PROBABLE_FOREXCOM`.** The export name, the distinct data (different from FX:XAUUSD, with no volume) and
  Tom's chart label all point to FOREXCOM:XAUUSD. `CONFIRMED_FOREXCOM` needs direct identity evidence: a TradingView
  symbol-info screenshot for this export.
- **DXY: `PROBABLE_TVC_DXY`.** Same evidence standard; it reproduces a second, independent TVC:DXY export.

**"Tom's actual chart/feed".** The files match the symbols on Tom's charts. They were downloaded from tradingview.com on
2026-09-15, about an hour after the owner's `references/charts` exports. Nothing in them identifies whose TradingView
account or chart layout produced them. They establish the **feed** (FOREXCOM:XAUUSD / TVC:DXY) that V-1 needs, not
Tom's personal chart session.

## 3. Coverage of the five V-1 windows

| File | CAL 10/22 | CAL 11/11 | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 |
|---|---|---|---|---|---|
| FOREXCOM:XAUUSD 1m | NONE | NONE | NONE | NONE | NONE |
| FOREXCOM:XAUUSD 5m | NONE | NONE | NONE | NONE | NONE |
| FOREXCOM:XAUUSD 15m | NONE | NONE | NONE | NONE | NONE |
| FOREXCOM:XAUUSD 1h | FULL (23 bars) | FULL (23) | FULL (11) | FULL (11) | FULL (15) |
| FOREXCOM:XAUUSD 4h | SPAN | SPAN | SPAN | SPAN | SPAN |
| FOREXCOM:XAUUSD 1D | SPAN | SPAN | SPAN | SPAN | SPAN |
| TVC:DXY 1m / 5m / 15m | NONE | NONE | NONE | NONE | NONE |
| TVC:DXY 1h | FULL | FULL | FULL | FULL | FULL |
| TVC:DXY 4h / 1D | SPAN | SPAN | SPAN | SPAN | SPAN |

**Gold 1m: `ONE_MINUTE_HISTORY_INSUFFICIENT`.**
- It spans 2026-09-09 00:20 → 2026-09-15 13:01.
- It covers none of 2025-10-20…24, 2025-10-22 or 2025-11-07…11.

| Window | Days short |
|---|---|
| CX-LT1-1 | 323 |
| CX-TE1-1 | 320 |
| CX-LT3-2 | 305 |
| CAL 10/22 | 322 |
| CAL 11/11 | 302 |

The export depth is about 6,280 bars per file, so it holds roughly one week of 1m bars.

## 4. Can Tom's data satisfy V-1?

**Outcome D (right source, no 1m history for the windows).**
- It is **not** outcome A or B: no FOREXCOM 1m bars for any calibration or course window.
- It is **not** outcome C: the source is the intended one.

**What it does support:**
- Identity of the intended feed.
- 1h-resolution coverage of all five windows. That is not 1m, so it can't satisfy V-1's 1-minute calibration or
  1m structure checks.

**Calibration vs parity (kept separate):**
- **Pre-registered calibration data:** none. There's no FOREXCOM 1m bar on 2025-10-22 or 2025-11-11.
- **Other non-course FOREXCOM 1m data:** 2026-09-09 → 09-15, after the holdout period ends on 2026-08-31. It could only
  become calibration data by owner approval, with new calibration days and a Dukascopy fetch for those days.
- **Course-window data:** only the 1h bars (and 4h / 1D spans). No 1m course-window data exists.

**Derived slices:** none created. No 1m file fully covers a window, so `slice` has nothing to derive. The manifest
records `derived_slices: []`.

## 5. OQ-26 (DXY) evidence (OQ-26 unchanged)

Stored Dukascopy DXY data:
- 1m candle files for 2018-2024 sample days, 2025-10-20…25 and 2025-11-09…11;
- one 2018 tick window.

| TVC:DXY file | Overlap with stored Dukascopy DXY days |
|---|---|
| 1m / 5m / 15m | **none**: the files start 2026-06-10 at the earliest |
| 1h | 2025-10-20…25, 2025-11-09…11 (all fixture days) |
| 4h | sample days 2022-10-19, 2022-11-24, 2023-11-06, 2023-12-20, 2024-03-20, 2024-04-12, plus the 2025 fixture days |
| 1D | all stored days |

**Result: `OQ26_REFERENCE_NOT_AVAILABLE` at 1m/5m/15m; partial reference at 1h/4h** on the windows above.
- A 1m/5m reference would need Dukascopy DXY data for 2026-09-08…15, which is not stored.
- TVC:DXY is an index and Dukascopy's DXY a CFD, so level offsets are expected.

## 6. Source families (never combined or substituted)

| Family | Contents | Identity | Recommended use |
|---|---|---|---|
| **A. Tom chart data** (`references/tom-chart-data`) | FOREXCOM:XAUUSD and TVC:DXY, 1m…1D, 1m depth ≈ 1 week | PROBABLE_FOREXCOM / PROBABLE_TVC_DXY | V-1 source identity. Future FOREXCOM 1m exports belong in this family. 1h/4h/1D as multi-timeframe reference fixtures. TVC:DXY as a DXY reference. Not yet V-1 calibration or course data (no 1m coverage) |
| **B. Owner TradingView reference** (`references/charts`) | FX:XAUUSD and TVC:DXY, 1m…1D | DIFFERENT_SOURCE (Gold) / PROBABLE_TVC_DXY | Gold: REFERENCE_ONLY (a different feed from Tom's). DXY: duplicates family A's TVC:DXY; keep as a consistency check |
| **C. Dukascopy canonical** | XAUUSD tick days (fixtures, samples, both calibration days); STRUCTURE / EXECUTION bars; DXY CFD candles | canonical (D16) | The engine STRUCTURE / EXECUTION series. Calibration counterpart for V-1 (both calibration days ready, D21) |
| **D. Databento futures** | GC.v.0 1m 2018-01-01 → 2026-09-13; DX.v.0 1m 2018-12-26 → 2026-09-11 (continuous front month) | GLBX.MDP3 | Phase 9/10 cross-checks and DX activity; not a spot substitute (OQ-24) |

## 7. Multi-timeframe reference opportunity (not a new Phase 13 requirement)

FOREXCOM 1h/4h/1D and TVC:DXY 1h/4h/1D cover Oct–Nov 2025 and earlier. Compared against Dukascopy-derived and resampled
bars on **non-course** days, they could separate:
- a feed difference (a stable offset);
- a resampling bug (bar alignment, session boundaries, 4h/1D session-open convention; the FOREXCOM daily file's first bar
  opens at 22:00 UTC);
- an implementation bug.

The FOREXCOM 5m/15m/1m files could do the same for recent weeks if Dukascopy ticks were fetched for those days (after the
holdout period). This needs an owner decision and isn't part of V-1 as approved.

## 8. V-1 status

**Primary: `V1_TOM_DATA_INSUFFICIENT`.**
- The intended FOREXCOM:XAUUSD feed is now present (probable identity).
- Its 1m history doesn't reach any of the five windows.
- The tool state is `V1_ONE_MINUTE_HISTORY_INSUFFICIENT`, and nothing can be sliced.
- Still missing: FOREXCOM 1m for the five windows, and symbol / timezone screenshots.

## 9. Paths forward (owner decides)

| Option | What | Protocol change | New calibration days | PC2 change | Owner decision |
|---|---|---|---|---|---|
| A | FOREXCOM:XAUUSD 1m for the five windows from a TradingView session that loads Oct–Nov 2025 1m history (this export loaded about one week), dropped into family A; then `slice` | no | no | no | no |
| B | FOREX.com-native 1m history (e.g. MT5) for the five windows | source definition only | no | no | yes |
| C | Recalibrate on recent non-course FOREXCOM 1m days (e.g. 2026-09-09…14, post-holdout) with a Dukascopy fetch for those days; course windows still lack 1m FOREXCOM bars | yes (new pre-registered calibration days) | yes | no | yes |
| D | Add hourly FOREXCOM course-window fidelity (1h bars vs Dukascopy 1h) as a partial V-1 | yes (1h fidelity replaces or augments 1m) | depends | no | yes |

Screenshots still needed under any option: a FOREXCOM:XAUUSD symbol-info screenshot (moves Gold identity to CONFIRMED) and
the chart timezone.
