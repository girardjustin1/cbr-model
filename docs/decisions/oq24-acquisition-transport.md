# OQ-24 — acquisition transport investigation (D41 §9-11)

**Doc:** CBR-EVD-OQ24-TRANSPORT · **Version:** v1.0 · **Date:** 2026-09-18 · **Status:** for owner review
**Scope:** transport efficiency only. The canonical dataset is unchanged and unchangeable here: Dukascopy XAUUSD
ticks, tick-mid STRUCTURE, tick bid/ask EXECUTION (D41 §11). No alternative *feed* is proposed.

---

## 1. The decisive prior evidence, from this repository

`src/cbr/data/dukascopy_fetch.py` states, in its own module docstring:

> "Reads Dukascopy's public hourly bi5 tick files directly (decoded here; **dukascopy-node was rate-limited**)."

and `data/raw/dukascopy/manifest.json` records `"cli": "dukascopy-node@1.50.0"` from the earlier Phase 9 work. So
the project has **already tried the best-known third-party client**, hit rate limiting, and moved to direct `bi5`
reads for that reason. The current slowness is not a defect of the current client.

## 2. What every candidate path actually fetches

| Path | Underlying source | Faster? |
|---|---|---|
| Current direct `bi5` reads | `datafeed.dukascopy.com/datafeed/XAUUSD/YYYY/MM/DD/HHh_ticks.bi5` | baseline |
| `dukascopy-node` (JS) | **the same per-hour `bi5` files, same host** | no — already rate-limited here |
| `duka` / `dukascopy-cli` and similar | the same per-hour files | no reason to differ |
| JForex platform historical export | same archive behind a desktop client; manual, not reproducible in a pipeline | not automatable to our provenance standard |
| Dukascopy "freeserv" endpoints | candle data, not ticks | **fails D41 §11** — candle files are not canonical (D16) |
| Bulk archive download | Dukascopy publishes no official bulk tick archive | n/a |

The unit of publication **is** the hourly file. Every client walks the same 43,848 URLs. Transport efficiency is
therefore bounded by the server's per-client rate limit, not by the library.

## 3. Measured behaviour of the limit

| Observation | Value |
|---|---|
| Cold, single stream | ≈ 13 s per hourly file |
| Sustained single stream | ≈ 50 s per hourly file |
| After concurrent requests were introduced | **HTTP 429**, then ≈ 100-150 s per hourly file |

Concurrency made throughput **worse**, which is why D41 §4 mandates a single stream and why the staged downloader
enforces one.

## 4. The one idea worth testing, and it is counter-intuitive

**Slower, steadier pacing may finish sooner.** Our current cost is dominated by 429 cooldowns, not by transfer.
A polite constant rate that never trips the limiter could plausibly beat an aggressive one that repeatedly earns a
180-second penalty.

This is measurable without committing to anything: run two equal-size blocks under different pacing constants and
compare wall-clock per successful hour. It costs one day of downloading to learn, and it does not touch the feed
choice, the canonical semantics or the research period. **Recommended as the next acquisition experiment**, with the
pacing constant recorded in the block manifests either way.

## 5. Conclusion

**No faster access path to the same data has been identified.** The limit is server-side and per-client, the third
party client was already tried and rejected for this reason, and no official bulk tick archive exists. The staged,
single-stream, rate-limit-aware downloader is the appropriate fallback, and D41 §12 already authorizes it to run for
weeks.

**If an alternative path is proposed later,** D41 §10 governs it: before it may produce authoritative data it must
reproduce already-validated direct-download days on tick timestamps, bid, ask, tick ordering, session gaps and tick
count. Byte identity is not required if the encoding differs; decoded content equivalence is. `oq24_equivalence()`
in `src/cbr/data/staged_acquisition.py` is the place to add that comparison when there is something to compare.
