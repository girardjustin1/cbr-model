# Phase 13 Acceptance Criteria: Strategy Fidelity and Behavioral Parity

**Doc:** CBR-ACC-013 · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D24 · **Status:** ACTIVE (gate definition)
**Run protocol:** `docs/governance/phase13-behavioral-parity-protocol.md` (CBR-PROT-013B, PROPOSED, awaiting owner
approval) · **Spec under test:** PC2 (`docs/strategy/parity-candidates/*-PC2.yaml`), frozen

## 1. Question

Does the deterministic, causal engine recognize the same underlying CBR market behavior Tom teaches?

A pass means: **the engine is sufficiently faithful to Tom's taught CBR price-action methodology to begin execution
and baseline testing.**

It does **not** mean:
- Tom's FOREXCOM chart is reproduced tick for tick;
- CBR is profitable;
- CBR has a robust edge;
- Dukascopy and FOREXCOM are identical.

## 2. Feeds

| Role | Source | Status |
|---|---|---|
| STRUCTURE (signals) | Dukascopy tick-derived mid | canonical (D16, D24-1) |
| EXECUTION (Phase 14+) | Dukascopy tick-derived bid/ask | canonical |
| Course truth | Tom's recorded examples (`research/examples/course_examples.jsonl`) and evidence records | Level 1 examples |
| Higher-timeframe fidelity | FOREXCOM:XAUUSD 1h / 4h / 1D (family A, `references/tom-chart-data`) | supporting (D24-7) |
| Feed comparison | FOREXCOM:XAUUSD recent 1m / 5m / 15m vs Dukascopy on recent non-course days | supporting study (D24-8) |
| V-1 (historical FOREXCOM 1m) | unavailable (TradingView history limit, D22/D23) | supporting validation, not a gate (D24-2) |

## 3. Gate

Every criterion must be met. Each is judged from recorded, reproducible outputs; nothing is judged on outcomes or P&L.

| Id | Criterion | Pass when | Evidence |
|---|---|---|---|
| **A** | Causal and deterministic engine | the full suite passes on the PC2 commit, including truncation and future-mutation tests (decision and trigger fields, mid-minute cuts), deterministic reruns and STRUCTURE/EXECUTION guards; the behavioral-parity run is repeated and produces identical result hashes | test report; run manifest hashes |
| **B** | Frozen spec implemented correctly | PC2 hash tests pass before and after the run; no `IMPLEMENTATION_BUG` remains open (any found is fixed under a new spec version and the run repeated) | `test_parity_candidate_specs.py`; mismatch register |
| **C** | Behavioral agreement on core CBR concepts | for each of the three examples, every core dimension (§4) is BEHAVIORAL_MATCH or BEHAVIORAL_MATCH_WITH_FEED_DIFFERENCE, **or** its difference is classified as OWNER_BASELINE_CHOICE, UNRESOLVED_SPEC_AMBIGUITY or CANON_MISMATCH with cited evidence; no example is FEED_DEPENDENT_SIGNAL_DIFFERENCE or IMPLEMENTATION_BUG unless the owner accepts it in the verdict | per-example dimension tables |
| **D** | Every mismatch classified | each non-matching dimension has exactly one primary class (§5) with evidence; secondary tags allowed | mismatch register |
| **E** | No unexplained implementation mismatch | zero dimensions left unclassified; zero open IMPLEMENTATION_BUG | mismatch register |
| **F** | Feed differences documented | for every compared price (entry trigger, stop anchor, extension extreme, target input, labelled levels): Tom value, Dukascopy value, difference, and whether the structural event is equivalent; FOREXCOM 1h / 4h vs Dukascopy offsets on the course hours reported | feed-difference table; higher-timeframe fidelity table |
| **G** | Feed differences don't change signal membership at an unacceptable rate | the recent 1m feed-comparison study reports agreement rates for structural states (§6) and the owner judges them against the acceptance rule pre-registered in CBR-PROT-013B before the study runs | feed-comparison report |

Exact historical FOREXCOM 1-minute price equality is **not** required.

## 4. Core behavioral dimensions (per example)

| # | Dimension |
|---|---|
| 1 | Model (CBR1H; entry variant A HVCS / B fractal) |
| 2 | Direction |
| 3 | Market condition |
| 4 | Range / trending-range state (and direction) |
| 5 | Extension direction |
| 6 | Extension timing (duration and extreme time) |
| 7 | Previous 15m candle take where required |
| 8 | Structural shift type |
| 9 | Approximate structural-shift time |
| 10 | Stop-anchor concept |
| 11 | Target concept |
| 12 | DXY context where documented |

Candidate acceptance (ARMED vs REJECTED and its failing rules) is reported alongside, with each failing rule
classified.

## 5. Classes

**Per dimension (primary class):**
- `BEHAVIORAL_MATCH`: same concept, and prices within display rounding.
- `FEED_DIFFERENCE`: same structural event; prices or times differ.
- `FEED_DEPENDENT_SIGNAL_DIFFERENCE`: the feed difference changes the interpretation, e.g. a take or shift exists on
  one feed and not the other.
- `OWNER_BASELINE_CHOICE`: disappears under exactly one pre-registered D8/D9 alternative.
- `UNRESOLVED_SPEC_AMBIGUITY`: governed by an open question or assumption (OQ-42 veto, OQ-44, OQ-40/45 windows, OQ-36
  lookback).
- `IMPLEMENTATION_BUG`: the engine contradicts PC2, reproduced by a failing test.
- `CANON_MISMATCH`: the engine follows PC2 and its evidence; Tom deviates or uses discretion.
- `DATA_LIMITATION`: can't be evaluated from stored data. It is a mismatch class under CBR-PROT-013; for an example
  verdict it aggregates like UNRESOLVED.

**Per example (verdict):** the most severe dimension class, in this order:

`IMPLEMENTATION_BUG` > `FEED_DEPENDENT_SIGNAL_DIFFERENCE` > `CANON_MISMATCH` > `UNRESOLVED_SPEC_AMBIGUITY` >
`OWNER_BASELINE_CHOICE` > `BEHAVIORAL_MATCH_WITH_FEED_DIFFERENCE` > `BEHAVIORAL_MATCH`

`BEHAVIORAL_MATCH_WITH_FEED_DIFFERENCE` applies when every dimension matches and at least one is FEED_DIFFERENCE. The
full dimension table is always shown; no single percentage is computed.

## 6. Supporting studies

- **Higher-timeframe fidelity (D24-7).** FOREXCOM 1h / 4h / 1D vs Dukascopy-rolled bars on the course hours and days:
  per-field offsets, extension direction of each course hour, the hour's extreme bar, and the 4h / 1D context.
- **Recent feed comparison (D24-8).** Non-course days overlapping the FOREXCOM 1m export, with Dukascopy ticks fetched
  for those days. Agreement of:
  - timestamps (lag);
  - bar direction and OHLC;
  - swing highs and lows (membership and time);
  - 15m previous-candle takes;
  - hourly extension direction and extreme time;
  - hour-level CBR states (condition, OE rules);
  - 1m structure events (HILO, 1m type 3).

  No FOREXCOM 5s data exists, so 5s comparisons are `DATA_LIMITATION`.
- **V-1 tooling and reports (D19-D23)** are kept as supporting evidence.

## 7. Verdict

The owner issues the Phase 13 verdict (PASS / PASS WITH CONCERNS / FAIL) after reviewing the gate evidence. Phase 14
doesn't start without it.
