# D42 — abort the full 2018-2024 acquisition; run a one-year 2022 development pilot

**Doc:** CBR-DEC-042 · **Date:** 2026-09-19 · **Status:** owner decision recorded
The full archive is off the immediate critical path. The goal is a meaningful first performance read without waiting
weeks for the whole span. Nothing about the model changes: PC4, D38 execution semantics and the D39 real-data
integration are untouched.

---

## 1. The long-run acquisition is stopped, not discarded

The staged 2018-2024 run was stopped at a safe atomic checkpoint. Every downloaded tick file, manifest, hash, retry
entry, completed block and pilot fixture is preserved so the full acquisition can resume later. The exact stop point
is recorded in `docs/governance/phase15a-status-report.md` §2.

## 2. OQ-24 is unchanged

Authoritative data architecture remains Dukascopy XAUUSD ticks — **structure** tick-derived midpoint, **execution**
tick-derived bid/ask. D42 changes **only the immediate historical span**: not the feed, not structure semantics, not
execution semantics, not PC4, not Phase 14A, not Phase 14A.1.

## 3. Phase 15A — one-year development pilot

**2022-01-01 → 2022-12-31**, frozen now, before any PC4 performance is measured.

Chosen because it is a full calendar year, already inside the frozen development period, the latest complete year of
2018-2022 development, and it touches neither 2023-2024 validation nor 2025-2026 holdout. **The year is not changed
after seeing performance.**

## 4. What this result is

**DEVELOPMENT PILOT.** Not a full development baseline, not validation, not holdout, not a robust edge. It answers
one question: *is the frozen CBR1H implementation promising enough to justify the cost of the full historical study?*

## 5. Validation and holdout stay untouched

No performance from 2023, 2024, 2025 or 2026 is accessed during Phase 15A. Existing parity and data-fidelity fixture
use stays governed by its existing exceptions and is never used for performance.

## 6. Six-day availability pilot

Finished. Final verdict recorded in §4 of the status report. **Data quality only** — the pilot days are never used
for strategy performance.

## 7-8. Acquire 2022 only, reusing what exists

A dedicated staged, resumable acquisition for 2022 alone, under the unchanged D41 transport requirements: single
request stream, resume from valid cached files, atomic writes, persistent retry queue, adaptive pacing, 429 cooldown,
no redownload of verified files, scheduled closures skipped only where the canonical calendar is certain, explicit
unresolved-failure accounting. Existing local 2022 files that pass source-integrity, hash, decoder, timestamp,
bid/ask and manifest validation are reused rather than refetched.

## 9-10. Completeness gate, and no partial-year performance

Strategy performance does not run until the declared 2022 span is **complete**, reported across the fifteen
accounting fields of §9 of the ruling. No unresolved market-open hour may silently disappear. PC4 is **not** run on
January, Q1, the first six months, or "the completed months so far" while acquisition is still running: the first
performance result uses the entire frozen span, so no partial period can influence a later decision.

## 11-13. Protocol frozen first; PC4 frozen; authoritative execution

`docs/acceptance/phase15a-2022-development-pilot.md` is written and hashed **before** historical signals are
generated. `CBR1H_BASELINE_V1` (frozen PC4) is used exactly as it stands — no change to CBR rules, HVCS, Type-3,
extension activation, swing k, target, stop, session rules, DXY handling or candidate selection. No strategy tuning
occurs in Phase 15A. The authoritative result comes from the Phase 14A simulator with the Phase 14A.1 real-tick
integration; TradingView Strategy Tester, Backtesting.py and bar assumptions are not authoritative.

## 14-16. Metrics and interpretation

Signals, performance, execution quality and descriptive breakdowns as listed in the acceptance document.
Breakdowns are descriptive and are not tuned from. **Primary metric: net expectancy in R per executed canonical
trade**; win rate is secondary and CBR is not judged primarily by it. The pilot may return **PROMISING**,
**INCONCLUSIVE** or **NEGATIVE** — never *validated edge*. One development year neither kills the project nor
promotes the strategy.

## 17. Astra review package

After the run: `phase15a_report.md`, `run_manifest.json`, `signals.csv`, `trades.csv`, `monthly_metrics.csv`,
`equity_curve.csv`, `drawdowns.csv`, `execution_quality.csv`. Astra's task is to **audit the result**, not to
optimize the strategy, and no rule change may be recommended until the owner has reviewed the untouched pilot.

## 18-21. TradingView parallel track

**Phase 14B — CBR1H PC4 Research Strategy**, a Pine Script v6 draft for visual human review, Strategy Tester
exploration, Python ↔ Pine signal parity and eventual alert groundwork. TradingView results are
**NON-AUTHORITATIVE / EXPLORATORY** and may not alter the 2022 Python pilot. Pine parameters are not optimized from
Strategy Tester results. Where Pine and Python disagree, the first assumption is a **Pine translation difference**:
Pine is investigated before PC4 is touched, and PC4 reopens only if the discrepancy reveals an independently
supported real strategy-definition defect. Backtesting.py is optional and is not a blocker.

## 22. After the result

**STOP** after the untouched 2022 pilot and the Astra package. PC4 is not modified. The owner then chooses between
continuing the full 2018-2024 acquisition, acquiring the remaining development years first, further fidelity checks,
or stopping/revising the project. Validation performance is not accessed without a new owner decision.
