# TradingView Exports: Inspection and V-1 Coverage

Generated 2026-09-15T13:08:25+00:00 by `python -m cbr.engine.v1_ingest inspect references/charts --report`. File and metadata inspection only: no prices reproduced, no engine output, no comparison with course examples.

**V-1 state: `V1_SYMBOL_MISMATCH`** · usable as V-1: none

Coverage: FULL = every bar holding a scheduled-open minute is present; SPAN = 4h/1D bars span the window; NONE = no bars in the window.

## Gold (XAUUSD)

| File | Symbol | TF | Rows | Start (UTC) | End (UTC) | CAL 10/22 | CAL 11/11 | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | V-1 eligible | Classification | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FX_XAUUSD, 1.csv | FX:XAUUSD | 1 | 7099 | 2026-09-08 08:15 | 2026-09-15 11:54 | NONE | NONE | NONE | NONE | NONE | no | REFERENCE_ONLY | SYMBOL_MISMATCH: FX:XAUUSD is not FOREXCOM:XAUUSD; ONE_MINUTE_HISTORY_INSUFFICIENT for v1_CX-LT1-1.csv, v1_CX-TE1-1.csv, v1_CX-LT3-2.csv, v1_cal_2025-10-22.csv, v1_cal_2025-11-11.csv |
| FX_XAUUSD, 15.csv | FX:XAUUSD | 15 | 7047 | 2026-05-29 12:15 | 2026-09-15 11:45 | NONE | NONE | NONE | NONE | NONE | no | REFERENCE_ONLY; TRADINGVIEW_REFERENCE_FIXTURE | SYMBOL_MISMATCH: FX:XAUUSD is not FOREXCOM:XAUUSD; not a 1-minute export (V-1 needs 1m OHLC) |
| FX_XAUUSD, 1D.csv | FX:XAUUSD | 1D | 7047 | 1999-07-06 22:00 | 2026-09-14 22:00 | SPAN | SPAN | SPAN | SPAN | SPAN | no | REFERENCE_ONLY; TRADINGVIEW_REFERENCE_FIXTURE | SYMBOL_MISMATCH: FX:XAUUSD is not FOREXCOM:XAUUSD; not a 1-minute export (V-1 needs 1m OHLC) |
| FX_XAUUSD, 240.csv | FX:XAUUSD | 240 | 7047 | 2022-02-23 11:00 | 2026-09-15 10:00 | SPAN | SPAN | SPAN | SPAN | SPAN | no | REFERENCE_ONLY; TRADINGVIEW_REFERENCE_FIXTURE | SYMBOL_MISMATCH: FX:XAUUSD is not FOREXCOM:XAUUSD; not a 1-minute export (V-1 needs 1m OHLC) |
| FX_XAUUSD, 5.csv | FX:XAUUSD | 5 | 7047 | 2026-08-10 22:25 | 2026-09-15 11:50 | NONE | NONE | NONE | NONE | NONE | no | REFERENCE_ONLY; TRADINGVIEW_REFERENCE_FIXTURE | SYMBOL_MISMATCH: FX:XAUUSD is not FOREXCOM:XAUUSD; not a 1-minute export (V-1 needs 1m OHLC) |
| FX_XAUUSD, 60.csv | FX:XAUUSD | 60 | 7047 | 2025-07-08 05:00 | 2026-09-15 11:00 | FULL | FULL | FULL | FULL | FULL | no | REFERENCE_ONLY; TRADINGVIEW_REFERENCE_FIXTURE | SYMBOL_MISMATCH: FX:XAUUSD is not FOREXCOM:XAUUSD; not a 1-minute export (V-1 needs 1m OHLC) |

| File | Timestamp basis | OHLC | Volume | Extra columns | Oct–Nov 2025 bars | SHA-256 |
|---|---|---|---|---|---|---|
| FX_XAUUSD, 1.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (7099 non-null) | Volume MA | 0 | `4d4aadd7f710d5fa…` |
| FX_XAUUSD, 15.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (7047 non-null) | Volume MA | 0 | `a0662450fdbd6b4f…` |
| FX_XAUUSD, 1D.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (7047 non-null) | Volume MA | 43 | `8310d22fe5348aad…` |
| FX_XAUUSD, 240.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (7047 non-null) | Volume MA | 258 | `b6d78625663278d7…` |
| FX_XAUUSD, 5.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (7047 non-null) | Volume MA | 0 | `c4368991e8e37586…` |
| FX_XAUUSD, 60.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (7047 non-null) | Volume MA | 988 | `5789336298f88a37…` |

**ONE_MINUTE_HISTORY_INSUFFICIENT**

- FX_XAUUSD, 1.csv: earliest 2026-09-08 08:15:00+00:00, latest 2026-09-15 11:54:00+00:00; days short of each window start: CX-LT1-1 322, CX-TE1-1 319, CX-LT3-2 304, CAL 10/22 321, CAL 11/11 301

## DXY (informational)

| File | Symbol | TF | Rows | Start (UTC) | End (UTC) | CAL 10/22 | CAL 11/11 | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TVC_DXY, 1.csv | TVC:DXY | 1 | 6291 | 2026-09-08 19:22 | 2026-09-15 11:55 | NONE | NONE | NONE | NONE | NONE | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 15.csv | TVC:DXY | 15 | 6291 | 2026-06-10 03:45 | 2026-09-15 11:45 | NONE | NONE | NONE | NONE | NONE | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 1D.csv | TVC:DXY | 1D | 6267 | 2001-11-30 00:00 | 2026-09-14 23:00 | SPAN | SPAN | SPAN | SPAN | SPAN | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 240.csv | TVC:DXY | 240 | 6275 | 2022-10-13 03:00 | 2026-09-15 11:00 | SPAN | SPAN | SPAN | SPAN | SPAN | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 5.csv | TVC:DXY | 5 | 6291 | 2026-08-13 04:45 | 2026-09-15 11:55 | NONE | NONE | NONE | NONE | NONE | TRADINGVIEW_REFERENCE_FIXTURE (informational) |
| TVC_DXY, 60.csv | TVC:DXY | 60 | 6275 | 2025-09-08 17:00 | 2026-09-15 11:00 | FULL | FULL | FULL | FULL | FULL | TRADINGVIEW_REFERENCE_FIXTURE (informational) |

| File | Timestamp basis | OHLC | Volume | Extra columns | Oct–Nov 2025 bars | SHA-256 |
|---|---|---|---|---|---|---|
| TVC_DXY, 1.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `9e51a104b02f5677…` |
| TVC_DXY, 15.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `dbe59f95c3a97536…` |
| TVC_DXY, 1D.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 43 | `dcf45641acea19a9…` |
| TVC_DXY, 240.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 265 | `d606cb938645fbd7…` |
| TVC_DXY, 5.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 0 | `1304040e9935d01f…` |
| TVC_DXY, 60.csv | unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them) | True | Volume (0 non-null) | Volume MA | 1018 | `0357f52a926cc8ed…` |
