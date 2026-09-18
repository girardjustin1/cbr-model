# D40 — OQ-24 resolved: full Dukascopy spot tick history; acquisition and pilot

**Doc:** CBR-DEC-040 · **Date:** 2026-09-18 · **Status:** owner decision recorded
Phase 14A.1 accepted **PASS**. The authoritative execution stack is technically ready for historical replay. D38
execution semantics and frozen PC4 strategy logic are unchanged; no historical CBR performance is run.

---

## 1. OQ-24 — RESOLVED

**Option A — full Dukascopy spot tick history** is the authoritative data architecture for the untouched CBR1H
baseline. Canonical **structure** = tick-derived midpoint; canonical **execution** = tick-derived bid/ask, exactly
the architecture validated in Phases 9, 13 and 14A.

**Why (fidelity and reproducibility, never profitability — no performance figure exists):** canonical structure
extrema · 5-second signal construction · bid/ask execution · spread · chronological event sequencing · no
futures-roll contamination · one internally consistent spot source · **zero screening risk of dropping a candidate
hour**.

**Option B (staged screening)** is not authoritative: proving a screen can never remove a valid PC4 setup ultimately
requires the data the screen exists to avoid acquiring. **Option C (futures / candle files)** is not authoritative:
it cannot guarantee identical PC4 signal membership. Both remain available as secondary references.

## 2. Acquisition target

**XAUUSD Dukascopy ticks, 2018-01-01 → 2024-12-31.** The 2025-2026 holdout is **not** downloaded as part of this
acquisition; existing holdout fixtures stay restricted to parity and data-fidelity purposes under their existing
rules.

## 3. Temporal splits, fixed before results

| Split | Period |
|---|---|
| Development | 2018-2022 |
| Validation | 2023-2024 |
| Holdout | 2025-2026 (not accessed during Phase 15) |

Not modifiable after seeing results.

## 4. Availability pilot — predeclared before downloading

Data quality only: no signals, no fills, no P&L. The dates below were fixed **before** any byte was fetched, are
ordinary mid-week trading days, were not chosen by price action, and none duplicates an existing project fixture
(checked against the 34 stored tick days):

```
2018-02-14   2018-09-12   2019-03-13   2019-10-16   2020-03-18   2020-09-16
```

**Per-day acceptance (D40 §5):** expected hourly files available · legitimate scheduled empty hours classified · no
unexplained large missing periods · decoder succeeds · timestamps monotonic · no non-positive prices · `ask > bid` ·
duplicate policy matches Phase 9 · deterministic tick → 5s STRUCTURE bars · deterministic tick → 1m STRUCTURE bars ·
bid/ask execution stream builds · manifest and source hashes generated.

**Failure rule:** if older availability is materially incomplete, **STOP** and return an OQ-24 amendment package
(missing-period pattern, alternative Dukascopy access paths, whether the span must change, whether another spot
source is required). **No silent fallback to futures.**

## 5. Full acquisition requirements (after a pilot pass)

Resumable from valid cached hours · bounded retries with exponential backoff · atomic writes · no redownload of
verified hours · per-hour manifest · SHA-256 · explicit error classification · scheduled-closure classification · no
synthetic filling. Completeness tracked per §8: requested days and hours, successful hours, scheduled-empty hours,
unresolved failures, retries, bytes, ticks, duplicate timestamps, bad spreads, non-positive prices, unexpected gaps.
A span is not complete while unresolved hour failures remain without a documented ruling.

## 6. Storage

Raw canonical ticks are preserved, never discarded after bars are built. Derived 5-second and 1-minute STRUCTURE bars
are reproducible cached artefacts that reference their source-tick hashes. Execution keeps reading raw bid/ask tick
sequencing.

## 7. Separation during acquisition

The download job stays separate from strategy execution. **No PC4 signal is computed because a year finished
downloading** — the first baseline must run over a declared complete span, so partial-period performance is never
inspected, accidentally or otherwise.

## 8. Phase 15 scope

CBR1H only, using `CBR1H_BASELINE_V1` (frozen PC4) with D38 execution semantics, the D39 real-data integration and
the full declared historical span. CBR15 is not baseline-ready and is not mixed in. No research ablation of any kind
runs in Phase 15.
