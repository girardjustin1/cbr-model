# Historical Data Requirements

What data the CBR research needs, why (with rule ids), where it comes from, and how it's normalized.
Status: **proposal**. Nothing has been downloaded yet.

## 1. What the rules demand

| Need | Why (rule ids) | Resolution |
|---|---|---|
| XAUUSD 1m OHLC | condition windows, swings, OE duration, 1m type-3 shift, 15m/hour candle behavior (CBR1H-COND-*, -OE-*, -ENTRY-003) | 1m |
| XAUUSD **5s / 15s** bars | 15m entry trigger (CBR15-ENTRY-001); hourly Model A seconds shift / HVCS→HILO (CBR1H-ENTRY-002) | 5s (built from ticks) |
| XAUUSD ticks (bid/ask) | building 5s bars; realistic spread & stop/target fill simulation for small targets | tick |
| DXY 1m (and 5s) | inverse-extension confluence over the same candle (CBR15-DXY-*); author watches DXY on 5s (E1H-044) | 1m + 5s |
| 15m, 1h, 4h, daily | derived from 1m, never fetched separately, so every timeframe comes from one source of truth | resampled |
| Economic calendar (optional, later) | regime segmentation only; not in canonical rules | event times |

Higher timeframes (4h, daily, weekly) are needed only for diagnostic context (daily/weekly CBOE, CBR1H-HTF-001),
not for baseline filters.

## 2. Sources

| Source | Instrument ids | Coverage (library metadata, unverified) | Cost | Role |
|---|---|---|---|---|
| **Dukascopy** public datafeed via `dukascopy-node` 1.50.0 | `xauusd` (XAU/USD), `dollaridxusd` (DOLLAR.IDX/USD, "US Dollar Index") | XAUUSD ticks from 2003-05-05; Dollar Index ticks from **2017-12-01** | free, keyless | **Primary** bulk history |
| TradingView chart export (CSV) | **`FOREXCOM:XAUUSD`** (the feed on Tom's live-trade chart, frame V1H-live_trade_3_gold_win 00:28:58), `TVC:DXY` | plan-limited bar count | your plan | **Parity checks**: specific days from course/journal examples, matching what Tom saw |
| Databento CME (GLBX.MDP3) | `GC` gold futures, `DX` dollar index futures | deep, tick | pay-as-you-go | Optional robustness check on futures (different microstructure) |

**Joint history for gold + DXY: 2017-12 → present (~8.7 years).** Gold-only studies can go back to 2003.

**Caveats (must be carried into every report):**
- Dukascopy prices are one liquidity provider's CFD/spot quotes, not exchange prints. DOLLAR.IDX/USD is Dukascopy's
  index CFD, not ICE's DXY. Tom watches `TVC:DXY`; small level differences are expected, and direction
  comparisons should be robust. Verify with a parity sample.
- Tick "volume" is per-side tick count, not traded volume. Nothing in the baseline uses volume as a filter
  (OQ-08).
- Coverage dates above are what the library declares. The ingestion job must verify actual first/last timestamps
  and gaps, and write them to the data manifest.

## 3. Storage layout (local, gitignored)

```
data/
  raw/dukascopy/<instrument>/ticks/YYYY/MM/DD.parquet      # bid, ask, bid_vol, ask_vol, ts_utc
  normalized/<instrument>/bars_5s/YYYY/MM.parquet          # mid OHLC + spread stats + tick_count
  normalized/<instrument>/bars_1m/YYYY.parquet
  normalized/<instrument>/bars_15m|1h|4h|1d/…              # resampled from 1m
  manifest.json                                            # source, library version, fetched_at, row counts,
                                                           # first/last ts, gap list, sha256 per file
```

DuckDB reads the parquet tree directly; Polars does the numeric work.

## 4. Normalization rules

1. **UTC everywhere internally.** Every timestamp is `timestamp[ns, UTC]`, bar **open** time.
2. **Bar construction.** A 5s/1m bar covers `[open, open+Δ)`. OHLC from **mid** = (bid+ask)/2. Also keep
   `spread_open`, `spread_max`, `tick_count`. Empty intervals produce **no bar** (never forward-filled). Gaps
   are explicit.
3. **Resampling** 1m → 15m/1h/4h/1d uses UTC clock-aligned boundaries (15m at :00/:15/:30/:45; hour on the hour),
   which is what "minute into the hour" rules need. Daily candles: **decide the session boundary**. Tom's
   "open of the day" follows his TradingView/broker daily candle, not UTC midnight (see §5).
4. **Alignment XAUUSD ↔ DXY.** Inner join on bar open time for same-candle comparisons. DXY has shorter trading
   hours and different holidays than gold. Missing DXY bars mark DXY features `unavailable`, never neutral
   ("missing data lowers confidence"). Lead/lag features (Phase 10) use explicit integer bar offsets on
   the aligned index.
5. **DST.** Session windows (Tokyo, London, NY) are defined in their local exchange time zones
   (`Asia/Tokyo`, `Europe/London`, `America/New_York`) and converted per date. Never fixed UTC offsets.
6. **Weekend/holiday handling.** The market week opens Sunday ~22:00-23:00 UTC; the first hour after the reopen
   is flagged. Holiday-thin sessions are flagged, not dropped.
7. **Validation checks** (fail the ingest): monotonic timestamps, no duplicate bar opens, high ≥ max(open, close),
   low ≤ min(open, close), spread > 0, per-day tick count within tolerance of trailing median.

## 5. Timezone facts from the sources

- Tom is based in Australia (E1H-042); a TradingView frame shows **GMT+11** ("Market closed Last update at 07:59
  GMT+11"; V1H-when_candle_behavior_timing slide 00:07:22), consistent with AEDT in Oct-Nov 2025.
  Chart times in course examples must be converted from that offset before matching to UTC data.
- Minute-of-hour rules (:22/:37/:52) are timezone-invariant for whole-hour offsets. Session and daily-candle rules
  are not.

### Parity fixtures identified so far (course examples, `research/examples/course_examples.jsonl`)

| Example | Instrument, direction | Chart time (as shown) | ≈ UTC | TZ evidence |
|---|---|---|---|---|
| CX-TE1-1 | XAUUSD buy | Fri 2025-10-24 ~15:37-15:38 | 04:37 UTC | "UTC+11" clock in frame |
| CX-LT1-1 | XAUUSD buy | Tue 2025-10-21 ~12:39 | 01:39 UTC | indirect (journal row) |
| CX-LT3-2 | XAUUSD sell | Mon 2025-11-10 12:40 | 01:40 UTC | "UTC+11" clock in frame (checked) |

CX-LT2-2 (USDJPY) is excluded: scope is XAUUSD + DXY only (user decision, 2026-09-14).

Needed data: 1m + 5s XAUUSD and DXY for those three days, from Dukascopy and, ideally, a `FOREXCOM:XAUUSD`
export to measure feed differences.

## 6. Temporal splits (proposal; fixed before any backtest)

With joint coverage 2017-12 → 2026-09:

| Split | Period | Use |
|---|---|---|
| Development | 2018-01-01 → 2022-12-31 | rule implementation, parity, baseline diagnostics |
| Validation | 2023-01-01 → 2024-12-31 | ablations, the limited parameter research |
| **Holdout** | 2025-01-01 → 2026-08-31 | touched once per frozen model version |

The course examples are from Oct-Nov 2025, inside the holdout. They are used **only** for signal parity (does the
code reproduce the taught setup?), never for performance measurement or tuning. This is recorded in the
hypothesis log.

## 7. What's needed from the user

Nothing blocking. Optional: TradingView plan level (determines whether 5s charts and exports are available for
parity checks) and whether a Databento futures cross-check is wanted later.
