# OQ-24 — baseline data / acquisition architecture

**Doc:** CBR-EVD-OQ24 · **Version:** v2.0 · **Date:** 2026-09-18 · **Ruling:** D39 §16-17
**Status:** DECISION PACKAGE, for owner ruling before the untouched baseline. Nothing is chosen from profitability
(D37 §8, D39 §15). No performance statistic exists yet, so none could have influenced this.

**The question that decides it:** *can this architecture produce **every** signal frozen PC4 would produce?* An
architecture that cannot is disqualified from being the authoritative untouched baseline, whatever else it offers.

---

## 1. What PC4 actually requires per candidate hour

From the frozen spec, not from preference:

| Input | Requirement | Why it binds acquisition |
|---|---|---|
| 5-second STRUCTURE bars | the entry trigger is a 5s type-3 shift | no vendor 5s bar product is canonical here; 5s bars are built from ticks (D16) |
| 1-minute STRUCTURE bars | HVCS, extension, previous-15m, location | rolled up from the same ticks |
| MTF context window | 8 **tradable** hours before the hour, ATR(1h,14) warm-up | a candidate hour needs roughly the prior trading day loaded, not just the hour |
| Previous 15m candle | the Q1 activation qualifier | one candle before the hour |
| EXECUTION bid/ask ticks | every fill decision (D38) | the same tick files, different projection |

So the atomic unit of acquisition is **a day of ticks**, and a scored hour needs its own day plus enough prior
tradable time for the context window.

## 2. Measured facts (this repository, today)

| | |
|---|---|
| Stored tick days | 34 |
| Storage | 104 MB total, **3.1 MB/day** mean (parquet) |
| Ticks per day | mean 310,304 · min 6,628 (holiday) · max 591,556 |
| Weekdays 2018-2024 | 1,827 |
| **Projected full-history tick storage** | **≈ 5.6 GB** for 2018-2024 |
| Integration status | the 14A.1 loader reads these files directly and validated a real hour at 26,393 ticks |

## 3. The options

### A. Full Dukascopy spot tick history

| Dimension | Assessment |
|---|---|
| Structure fidelity | **Highest.** STRUCTURE = tick mid and EXECUTION = tick bid/ask from one source, exactly the frozen architecture |
| 5-second availability | Complete — built from ticks |
| Bid/ask availability | Complete |
| 2018-2024 availability | Dukascopy publishes XAUUSD ticks across the period |
| Acquisition time | The dominant cost. Prior fetches ran at roughly a day of ticks per fetch unit with 503 retries and resumable caching; 1,827 weekdays is a long, unattended job, not an afternoon |
| Storage | ≈ 5.6 GB, trivial |
| Reproducibility | **Highest.** Per-file SHA-256 already recorded and now surfaced in execution provenance |
| Probability of missing a candidate signal | **Zero by construction** — every hour is present |
| Feed consistency | One feed, one clock, one convention |
| Engineering complexity | Lowest: the loader already exists and is tested |
| Licensing | Dukascopy historical data is publicly downloadable; already used throughout the project |
| Execution realism | Highest: real bid/ask sequencing |

### B. Staged acquisition behind a screening stage

Screen cheaply for hours that *could* contain a PC4 signal, then fetch ticks only for those.

| Dimension | Assessment |
|---|---|
| Structure fidelity | Same as A **within** fetched windows |
| Missing-signal probability | **The whole risk.** D39 §16 requires the screen to be *proven incapable* of excluding a valid PC4 signal |
| Screening feasibility | The cheapest screen would use vendor 1m candles to pre-filter hours. But PC4's own gates depend on 5s structure (the type-3 trigger), on tick-derived extremes (D16 exists precisely because candle extremes are unreliable), and on an 8-hour tradable context window. A screen using a different price series can differ on exactly the extremes that decide a sweep |
| Proof burden | To prove the screen safe you would need the full-tick answer to compare against — which is option A. The proof costs what it saves |
| Acquisition time | Lower, but unknown until the screen exists |
| Engineering complexity | Higher: a second pipeline, a screen-safety proof, and a permanent caveat on every baseline number |
| Reproducibility | Weaker: results depend on the screen's version as well as the data |

### C. Hybrid / other source (Databento futures, vendor bars, mixed)

| Dimension | Assessment |
|---|---|
| Structure fidelity | **Fails the binding test.** GC futures are a different instrument with roll and basis; vendor bars are not tick-derived. D16 already ruled that candle files are not canonical for extremes, and D23-D24 found the available vendor 1m history insufficient |
| Bid/ask availability | Futures top-of-book is available but is not the instrument PC4 was specified on |
| Signal membership | Cannot be guaranteed identical — different extremes produce different sweeps and shifts |
| Verdict | Disqualified as the **authoritative** baseline. Retains value as a cross-feed sensitivity check *after* a baseline exists |

## 4. Recommendation

**Option A — full Dukascopy spot tick history — as the authoritative baseline architecture.**

The reasoning is entirely about signal membership and reproducibility:

1. **It is the only option that answers the binding question with certainty.** A and B differ only in whether some
   hours are absent; B's safety depends on a screen whose proof requires A's data.
2. **The cost is time, not money or complexity.** 5.6 GB and an existing, tested loader. The expensive resource is
   unattended download time, which can run while other work proceeds.
3. **It removes a permanent caveat.** Under B every baseline statistic would carry "subject to screen coverage"
   forever, and any surprising result would first have to be litigated against the screen.

**Suggested shape, for the owner to accept or vary:** stage the *download* (chronologically, resumable, per-day
manifest entries as already implemented) while treating the *baseline* as runnable only once a declared contiguous
span is complete. That captures B's practical benefit — useful data early — without B's epistemic cost, because the
baseline is never computed over a screened subset.

**What would change the recommendation:** evidence that Dukascopy XAUUSD tick history is materially incomplete
before some date. That is a data-availability question, answerable by sampling a handful of 2018-2020 days before
committing to the full run, and it should be settled first.

## 5. Not part of this recommendation

Instrument scope stays XAUUSD (D7). CBR15 is out of scope until independently baseline-ready. The choice of research
period, and any decision about how many years the baseline should cover, is separate and is not addressed here.
