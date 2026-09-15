# V-1 Export Inspection: owner-supplied TradingView charts

> **Superseded (D22)** by `reports/tradingview-exports-inspection.md` and `docs/decisions/v1-tradingview-exports-assessment.md`.

Generated 2026-09-15T12:00:49+00:00 by `python -m cbr.engine.v1_ingest inspect references/charts`. Metadata only (symbol, timeframe, span, coverage); no prices are reproduced and nothing was renamed, copied or substituted.

**Verdict: DATA_LIMITATION: no FOREXCOM:XAUUSD 1m export covers the V-1 windows** (D19-14). V-1 is not waived; Phase 13 stays blocked.

| File | TradingView symbol | Timeframe | Rows | First bar (UTC) | Last bar (UTC) | Required symbol | Covers V-1 windows |
|---|---|---|---|---|---|---|---|
| FX_XAUUSD, 1.csv | FX:XAUUSD | 1 | 7099 | 2026-09-08 08:15 | 2026-09-15 11:54 | no | 0/5 |
| FX_XAUUSD, 15.csv | FX:XAUUSD | 15 | 7047 | 2026-05-29 12:15 | 2026-09-15 11:45 | no | 0/5 |
| FX_XAUUSD, 1D.csv | FX:XAUUSD | 1D | 7047 | 1999-07-06 22:00 | 2026-09-14 22:00 | no | 5/5 |
| FX_XAUUSD, 240.csv | FX:XAUUSD | 240 | 7047 | 2022-02-23 11:00 | 2026-09-15 10:00 | no | 5/5 |
| FX_XAUUSD, 5.csv | FX:XAUUSD | 5 | 7047 | 2026-08-10 22:25 | 2026-09-15 11:50 | no | 0/5 |
| FX_XAUUSD, 60.csv | FX:XAUUSD | 60 | 7047 | 2025-07-08 05:00 | 2026-09-15 11:00 | no | 5/5 |
| TVC_DXY, 1.csv | TVC:DXY | 1 | 6291 | 2026-09-08 19:22 | 2026-09-15 11:55 | no | 0/5 |
| TVC_DXY, 15.csv | TVC:DXY | 15 | 6291 | 2026-06-10 03:45 | 2026-09-15 11:45 | no | 0/5 |
| TVC_DXY, 1D.csv | TVC:DXY | 1D | 6267 | 2001-11-30 00:00 | 2026-09-14 23:00 | no | 5/5 |
| TVC_DXY, 240.csv | TVC:DXY | 240 | 6275 | 2022-10-13 03:00 | 2026-09-15 11:00 | no | 5/5 |
| TVC_DXY, 5.csv | TVC:DXY | 5 | 6291 | 2026-08-13 04:45 | 2026-09-15 11:55 | no | 0/5 |
| TVC_DXY, 60.csv | TVC:DXY | 60 | 6275 | 2025-09-08 17:00 | 2026-09-15 11:00 | no | 5/5 |

## Findings

1. **Symbol.** The exports are `FX:XAUUSD` (file prefix `FX_`), not `FOREXCOM:XAUUSD`. D19-13: no symbol substitution without owner approval. Feed identity can't be confirmed without the symbol-info screenshot.
2. **1m history.** The 1m export starts 2026-09-08; each intraday export holds about 7,000 bars, so 1m, 5m and 15m don't reach the October-November 2025 windows. Only 60m, 240m and daily cover them.
3. **Timestamps.** Unix seconds (UTC by definition); 1-minute spacing confirmed on the 1m file.
4. The DXY exports (`TVC:DXY`) aren't part of V-1 (XAUUSD feed fidelity only).

## What would satisfy V-1

- `FOREXCOM:XAUUSD`, 1 minute, chart timezone UTC, covering the five windows in protocol §6.2, plus screenshots named `*symbol*` and `*timezone*` in `data/raw/tradingview/screenshots/`.
- If TradingView can't load 1m bars that far back on this account, alternatives needing owner approval (D19-14): (a) a FOREXCOM:XAUUSD 1m export from an account whose plan loads that history; (b) FOREX.com's own historical 1m data for the same symbol (e.g. a MetaTrader 5 history export from a FOREX.com account); (c) an owner-approved replacement fidelity test (for example recent non-course calibration days on FOREXCOM:XAUUSD with fresh Dukascopy ticks, plus 60m coverage of the course windows), which would change the pre-registered calibration days and needs explicit approval.
