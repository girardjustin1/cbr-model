# D39 — Phase 14A accepted PASS WITH CONCERNS; Phase 14A.1 real-data integration

**Doc:** CBR-DEC-039 · **Date:** 2026-09-18 · **Status:** owner ruling recorded and implemented

Phase 14A core execution mechanics are **COMPLETE** and accepted **PASS WITH CONCERNS** — the concern being
integration, not semantics. Phase 14A.1 connects the approved simulator to real project data **without changing any
frozen execution behaviour**. No D38 semantic was altered. No profitability, win rate, expectancy, profit factor or
P&L was computed. Backtesting.py is not started.

---

## Implemented

| § | Ruling | Implementation |
|---|---|---|
| §2 | Execution quotes come from Dukascopy **bid/ask ticks** only — never midpoint, candle OHLC, futures, vendor bars or interpolation; `ask > bid`, both positive, UTC, chronological; duplicates follow the Phase 9 policy | `market_data.validate_ticks`, `market_data.load_quotes` |
| §3 | Tick loader: requested windows only, chronological, untransformed, source files identified and SHA-256 hashed, legitimate closure distinguished from missing data, deterministic, never silently skipping a malformed file | `market_data.load_quotes` (a bad file raises `TickDataError`) |
| §4 | Gap classification **translates** the existing Phase 9 criterion rather than defining a second one: a minute without quotes that is not `expected_closed` is an unexpected gap (AC-07) | `market_data.classify_intervals` → `SCHEDULED_CLOSURE`, `ROLLOVER_EXCLUSION`, `DATA_GAP`, `VALID_SPARSE_QUOTES`, `NOT_LOADED` |
| §5 | D38 gap behaviour preserved exactly | only `DATA_GAP` runs reach the simulator as `px.Gap` |
| §6 | The existing DST-aware rollover helper is reused; no second calendar | `prices.in_rollover_window` → `structure.levels.in_rollover`; EST and EDT both tested on real dates |
| §7 | Deterministic replay driver that never asks whether a signal is valid | `replay.replay` / `replay.execute_signal` |
| §8-9 | Integration proved with **synthetic signals over real quotes**, cases A-L | `tests/execution/test_real_data_integration.py` |
| §10 | Provenance sufficient to reproduce a result exactly | `market_data.TickProvenance` + `replay.replay`'s manifest |
| §11 | Contract → order adapter translating approved fields only, refusing with a reason code when an input is absent | `replay.adapt` |
| §12 | The D37 external eligibility gate still applies on real data; the frozen signal is never edited | `contract.eligible`, integration-tested |
| §13 | No performance summary produced | no aggregate over CBR signals exists anywhere in the package |

## Not changed

Every D38 execution semantic; PC4 and its frozen records; the D37 promotion gate; the strategy lock.
