# TradingView Exports: Inspection and V-1 Coverage

Generated 2026-09-15T13:08:25+00:00 by `python -m cbr.engine.v1_ingest inspect references/tom-chart-data --report`. File and metadata inspection only: no prices reproduced, no engine output, no comparison with course examples.

**V-1 state: `V1_ONE_MINUTE_HISTORY_INSUFFICIENT`** · usable as V-1: none

Coverage: FULL = every bar holding a scheduled-open minute is present; SPAN = 4h/1D bars span the window; NONE = no bars in the window.

## Gold (XAUUSD)

| File | Symbol | TF | Rows | Start (UTC) | End (UTC) | CAL 10/22 | CAL 11/11 | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | V-1 eligible | Classification | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FOREXCOM_XAUUSD, 1.csv | FOREXCOM:XAUUSD | 1 | 6281 | 2026-09-09 00:20 | 2026-09-15 13:01 | NONE | NONE | NONE | NONE | NONE | no | TRADINGVIEW_REFERENCE_FIXTURE | ONE_MINUTE_HISTORY_INSUFFICIENT for v1_CX-LT1-1.csv, v1_CX-TE1-1.csv, v1_CX-LT3-2.csv, v1_cal_2025-10-22.csv, v1_cal_2025-11-11.csv |
| FOREXCOM_XAUUSD, 15.csv | FOREXCOM:XAUUSD | 15 | 6280 | 2026-06-10 19:45 | 2026-09-15 13:00 | NONE | NONE | NONE | NONE | NONE | no | TRADINGVIEW_REFERENCE_FIXTURE | not a 1-minute export (V-1 needs 1m OHLC) |
| FOREXCOM_XAUUSD, 1D.csv | FOREXCOM:XAUUSD | 1D | 6280 | 2002-06-18 22:00 | 2026-09-14 22:00 | SPAN | SPAN | SPAN | SPAN | SPAN | no | TRADINGVIEW_REFERENCE_FIXTURE | not a 1-minute export (V-1 needs 1m OHLC) |
| FOREXCOM_XAUUSD, 240.csv | FOREXCOM:XAUUSD | 240 | 6280 | 2022-08-23 02:00 | 2026-09-15 10:00 | SPAN | SPAN | SPAN | SPAN | SPAN | no | TRADINGVIEW_REFERENCE_FIXTURE | not a 1-minute export (V-1 needs 1m OHLC) |
| FOREXCOM_XAUUSD, 5.csv | FOREXCOM:XAUUSD | 5 | 6280 | 2026-08-13 16:15 | 2026-09-15 13:00 | NONE | NONE | NONE | NONE | NONE | no | TRADINGVIEW_REFERENCE_FIXTURE | not a 1-minute export (V-1 needs 1m OHLC) |
| FOREXCOM_XAUUSD, 60.csv | FOREXCOM:XAUUSD | 60 | 6280 | 2025-08-22 11:00 | 2026-09-15 13:00 | FULL | FULL | FULL | FULL | FULL | no | TRADINGVIEW_REFERENCE_FIXTURE | not a 1-minute export (V-1 needs 1m OHLC) |

| File | Timestamp basis | OHLC | Volume | Extra columns | Oct–Nov 2025 bars | SHA-256 |
|---|---|---|---|---|---|---|
| FOREXCOM_XAUUSD, 1.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `5fb0a1b5d1ca717e…` |
| FOREXCOM_XAUUSD, 15.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `69b731582a2e161c…` |
| FOREXCOM_XAUUSD, 1D.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 43 | `891c30eb69cc2304…` |
| FOREXCOM_XAUUSD, 240.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 258 | `a83531dd6fd32a55…` |
| FOREXCOM_XAUUSD, 5.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `5d8f2d185eec39bb…` |
| FOREXCOM_XAUUSD, 60.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 984 | `dd7814e2227d0f3d…` |

**ONE_MINUTE_HISTORY_INSUFFICIENT**

- FOREXCOM_XAUUSD, 1.csv: earliest 2026-09-09 00:20:00+00:00, latest 2026-09-15 13:01:00+00:00; days short of each window start: CX-LT1-1 323, CX-TE1-1 320, CX-LT3-2 305, CAL 10/22 322, CAL 11/11 302

## DXY (informational)

| File | Symbol | TF | Rows | Start (UTC) | End (UTC) | CAL 10/22 | CAL 11/11 | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TVC_DXY, 1.csv | TVC:DXY | 1 | 6289 | 2026-09-08 20:31 | 2026-09-15 13:02 | NONE | NONE | NONE | NONE | NONE | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 15.csv | TVC:DXY | 15 | 6288 | 2026-06-10 05:45 | 2026-09-15 13:00 | NONE | NONE | NONE | NONE | NONE | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 1D.csv | TVC:DXY | 1D | 6280 | 2001-11-11 22:00 | 2026-09-14 23:00 | SPAN | SPAN | SPAN | SPAN | SPAN | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 240.csv | TVC:DXY | 240 | 6288 | 2022-10-10 23:00 | 2026-09-15 11:00 | SPAN | SPAN | SPAN | SPAN | SPAN | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 5.csv | TVC:DXY | 5 | 6288 | 2026-08-13 06:05 | 2026-09-15 13:00 | NONE | NONE | NONE | NONE | NONE | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 60.csv | TVC:DXY | 60 | 6288 | 2025-09-08 06:00 | 2026-09-15 13:00 | FULL | FULL | FULL | FULL | FULL | TRADINGVIEW_REFERENCE_FIXTURE (informational) |

| File | Timestamp basis | OHLC | Volume | Extra columns | Oct–Nov 2025 bars | SHA-256 |
|---|---|---|---|---|---|---|
| TVC_DXY, 1.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `e839f89ad852e7cb…` |
| TVC_DXY, 15.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `aa09004f9f3e6001…` |
| TVC_DXY, 1D.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 43 | `8d77090ca4e334cd…` |
| TVC_DXY, 240.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 265 | `b5b801d7218afc13…` |
| TVC_DXY, 5.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `ec616d90026c4ac5…` |
| TVC_DXY, 60.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 1018 | `1602a763e7c5269e…` |
