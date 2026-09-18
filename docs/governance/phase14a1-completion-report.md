# Phase 14A.1 completion report — real-data execution integration

**Doc:** CBR-RPT-014A1 · **Date:** 2026-09-18 · **Ruling:** D39 · **Status:** returned for owner review
No D38 execution semantic changed · no profitability, win rate, expectancy, profit factor or P&L computed · no CBR
signal outcome inspected · Backtesting.py not started.

---

## 1. Files and modules added

| Path | Role |
|---|---|
| `src/cbr/execution/market_data.py` | Dukascopy bid/ask tick loader, validation, provenance, interval classification |
| `src/cbr/execution/replay.py` | deterministic historical replay driver, contract→order adapter, provenance assembly |
| `tests/execution/test_real_data_integration.py` | 20 tests, synthetic signals over real quotes (D39 §9 A-L) |
| `docs/governance/d39-phase14a1-real-data-integration.md` | the ruling, mapped to implementation |
| `docs/decisions/oq24-baseline-data-architecture.md` | the updated OQ-24 decision package |

No existing execution module was modified: the D38 mechanics are untouched.

## 2. Tick-loader architecture

`load_quotes(start, end, instrument)` reads the stored canonical tick parquet files day by day, keeping only the
requested window. Each file is validated before use — `ts`/`bid`/`ask` present, timezone-aware UTC, `bid > 0`,
`ask > 0`, **`ask > bid` strictly** — and a malformed file raises `TickDataError` rather than being skipped. Order is
a stable sort on timestamp, so Phase 9's duplicate policy (duplicates retained, not dropped) carries through, and the
duplicate count is reported. The result is projected into the simulator's quote stream with `resolved = True`, which
is what makes tick sequencing authoritative. No downloader code lives in execution: acquisition and consumption stay
separate.

Verified against a real window: 2025-10-21 01:00-02:00 UTC loads **26,393 ticks**, first quote 01:00:00.204, last
01:59:59.912, one source file, zero duplicates.

## 3. Gap-metadata integration

`classify_intervals` labels every minute of the requested window and **translates** the project's existing Phase 9
criterion rather than inventing a second one. Phase 9 AC-07 calls a minute with no data that is not
`expected_closed` an *unexpected gap*; that is exactly the minute this adapter labels `DATA_GAP`.

| Label | Meaning |
|---|---|
| `VALID_SPARSE_QUOTES` | the minute has quotes — sparse quoting is never a gap |
| `SCHEDULED_CLOSURE` | no quotes, and `sessions.expected_closed` says the market is shut |
| `ROLLOVER_EXCLUSION` | no quotes, inside the canonical rollover window |
| `NOT_LOADED` | the day's tick file is not in the store |
| `DATA_GAP` | no quotes, none of the above — Phase 9's unexpected gap |

Only `DATA_GAP` and `NOT_LOADED` runs are handed to the simulator as `px.Gap`, so D38's unprovable-outcome rules fire
on exactly the intervals Phase 9 would have flagged, and never on a closure or a quiet minute.

## 4. Rollover integration

`prices.in_rollover_window` delegates to the existing `structure.levels.in_rollover`, which is DST-aware through
`America/New_York`. No second calendar exists in execution. Both regimes are tested on real stored dates:
**2025-10-21 (EDT)** where 17:00 New York is 21:00 UTC, and **2025-11-10 (EST)** where it is 22:00 UTC. A pending
order inside the real EST window is cancelled `ROLLOVER_CANCEL`.

## 5. Signal adapter

`replay.adapt` translates only approved contract fields and refuses rather than inventing: it returns an explicit
reason when the signal fails contract parsing, or carries no activation time, no entry reference price, neither a
stop anchor nor an anchor path, or no spread policy. A refusal produces a `NOT_EXECUTED` ledger row with the reason
recorded in `data_confidence`, so a refused signal is still visible. Handling is confirmed for `signal_id`,
direction, activation time, trigger price, the structure stop-anchor path, the stop buffer, the spread policy, the
target price, rollover policy and provenance.

## 6. Provenance fields

Every replay result carries: `instrument`, `requested_window`, `loaded_window`, `tick_count`, `source_file_ids`,
`source_hashes` (SHA-256 per file), `missing_days`, `duplicate_timestamps`, `gap_manifest_version`,
`day_manifest_sha256`, `classified_intervals`, `execution_config_hash`, `execution_semantics`, `signal_hash`,
`simulator_version`, `result_hash`, and the D37 `baseline_provenance` — which restates the parity verdict as **FAIL**
and carries the five fidelity concerns. That set is sufficient to reproduce a result exactly.

## 7-8. Synthetic-over-real tests and windows used

All twelve required cases, plus eight more:

| Case | Test |
|---|---|
| A LONG fills from ASK | asserts the fill equals the real ask at the fill instant |
| B SHORT fills from BID | same on the bid |
| C tick sequencing resolves two events | independently recomputes which level the real ticks reach first and asserts the simulator agrees |
| D time-varying spread preserved | requires > 5 distinct spreads in the window; asserts `fill_spread` equals the real spread at the fill |
| E real jump through entry | asserts the executable quote is used and `entry_gap > 0` |
| F real jump through stop | asserts the fill is at or worse than the stop, with `stop_gap` recorded |
| G target stays limit-priced | asserts the exit is exactly the target while the real bid went past it |
| H rollover, EST **and** EDT | 21:00 UTC vs 22:00 UTC; plus a real cancelled order |
| I closure is not a gap | the real daily break classifies as closure/rollover with zero `DATA_GAP` |
| J classified missing data | a genuinely absent stored day yields 60 `NOT_LOADED` minutes and `EXECUTION_DATA_UNAVAILABLE`; an injected gap over a real window yields an unprovable outcome |
| K identical repeat | same `result_hash` across replays |
| L source hashes in the ledger | 64-character hashes, manifest version, config and signal hashes all present |

Extra: adapter refusals (two), the promotion gate on real data, a populated hour showing zero gaps, and a check that
the loaded quotes are bid/ask and tick-resolved — never midpoint.

**Windows used:** 2025-10-21 01:00-02:00 UTC (populated hour, EDT), 2025-11-10 21:50-22:10 UTC (real rollover, EST),
2025-11-10 22:00-22:45 UTC (daily break), 2025-10-14 01:00-02:00 UTC (absent day). All are existing stored
development/validation days chosen for calendar and availability properties. **No window was chosen by outcome, and
no CBR signal was replayed.**

## 9-14. Status

| | |
|---|---|
| Tests added | 20 (real-data integration) |
| **Total** | **716 passed**, 0 failed, 0 skipped |
| Lint | `ruff check src tests` clean |
| Causality | no fill uses data after its own instant; the D38 suite's truncation and future-mutation tests still pass, and the loader only ever reads the requested window |
| Determinism | identical `result_hash` across repeated real-data replays |
| Architecture guard | passes, with the allow-list extended to three **data-layer** modules (`cbr.data.price_series`, `cbr.data.dukascopy_fetch`, `cbr.data.sessions`). No strategy-rule module is importable, no `M1H-` rule id appears in the package, and the guard now resolves `from cbr.data import sessions` to its fully-qualified name so a submodule cannot slip through |

## 15. Phase 14A.1 verdict

### PASS

Real Dukascopy bid/ask ticks load and validate; gap metadata integrates by translating the existing Phase 9
criterion; the DST-aware rollover calendar is reused and proven in both regimes; the frozen contract adapts or
refuses explicitly; real tick sequencing drives the approved simulator unchanged; provenance is reproducible;
causality, determinism and the import separation hold; every integration test passes on real data; the full suite and
lint are clean. None of the FAIL conditions in D39 §14 is present — no fabricated fill, no missed gap, no midpoint
execution, no lost sequencing, no rollover violation, no future quote, no divergence across runs.

## 16-17. OQ-24

Options evaluated in full in `docs/decisions/oq24-baseline-data-architecture.md` against the binding test — *can this
architecture produce **every** signal frozen PC4 would produce?*

**Recommended: Option A, full Dukascopy spot tick history**, on signal-membership and reproducibility grounds, not
performance (no performance figure exists). Measured: 3.1 MB/day, ≈ **5.6 GB** for 2018-2024, an already-tested
loader, and zero probability of missing a candidate hour. Option B's screening stage would have to be *proven*
incapable of excluding a valid PC4 signal, and that proof requires Option A's data — the proof costs what the option
saves. Option C is disqualified as authoritative: futures and vendor bars cannot guarantee identical signal
membership, and D16 already ruled candle extremes non-canonical.

Suggested shape: stage the *download* chronologically and resumably, but treat the *baseline* as runnable only over a
declared complete contiguous span, so no statistic is ever computed over a screened subset. **First action if
approved:** sample a handful of 2018-2020 days to confirm tick history is materially complete before committing to
the full run.

## 18. Remaining blockers to historical baseline execution

1. **OQ-24 is undecided** — the owner's ruling on the architecture above.
2. **Historical ticks are not acquired.** 34 stored days versus ~1,827 weekdays for 2018-2024.
3. **No signal-generation run exists over history.** PC4 has only ever run on parity hours and synthetic data;
   producing the frozen signal population is a separate, authorized step.
4. **Phase 15 acceptance criteria are not written.** The untouched-baseline gate needs its own criteria before any
   statistic is computed, as 14A's did.
5. Non-blocking: `PENDING`/`FILLED` statuses remain unused by the batch driver; commission stays 0 and
   non-broker-specific.

**Stopping here**, per D39 §15: the next decision is OQ-24, and the baseline is not run.
