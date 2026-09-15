# D20 D19 Follow-up (Phase 13 Readiness): Ruling Record

**Doc:** CBR-RULING-D20 · **Date:** 2026-09-15 · **Decided by:** Owner ("D19 / Phase 13 readiness follow-up", recorded as D20)

## Result

D19 implementation accepted (architecture, frozen parity-candidate specs, causality protections, refusal-to-run gate).
**Phase 13 remains NOT READY.** No final parity, course-example scoring, profitability, optimization, holdout P&L,
Backtesting.py or Astra × Fable review.

| Id | Item | Ruling | Implemented as |
|---|---|---|---|
| D20-1 | "Setup formed" | A raw candidate reached ARMED passing every setup rule except the recursive prior-setup requirement; never fill, target, stop, outcome or played-out | `raw_setup_armed` (CBR15, CBR1H); used for prior-setup existence |
| D20-2 | CBR1H prior window | Ends at H.t0; current-hour setups don't count; 10 h ASSUMPTION, not optimized | `prior_setup_window_start`, `prior_setup_window_end`, `prior_setup_count` (both models) |
| D20-3 | CBR15 Q−1 | No trade-direction exception; no transfer between models by analogy | `cbr15.q_takes_prev_candle(oe)` (no close input) |
| D20-4 | OQ-44 HVCS continuity | Current deterministic reading approved as ASSUMPTION; no count; diagnostics only; remove blocker | `hvcs_start_time`, `hvcs_end_time`, `hvcs_extension_extreme_time`, `bars_between_hvcs_and_shift`, `indecision_bars_between`, `continuity_state`; blocker removed |
| D20-5 | OQ-45 CBR15 window | Tradable-market time (ASSUMPTION); vendor gaps stay in time and visible | CBR15 `window_basis = TRADABLE`; three duration fields on candles and candidates |
| D20-6 | HTF fill dependency | Split unchanged; fill NOT_EVALUATED = EXECUTION_DEPENDENT; doesn't block signal parity; blocks full CBR15 eligibility | unchanged |
| D20-7 | Specs | New PC2 specs; PC1 preserved | `docs/strategy/parity-candidates/*-PC2.yaml`; PC1 files untouched |
| D20-8 | Tests | A recursion, B current-hour exclusion, C CBR15 Q−1, D HVCS continuity, E tradable CBR15 window, F vendor gap; re-run causality, determinism, guards, frozen specs, suite, lint | `tests/engine/` |
| D20-9 | Readiness | OQ-44/45, setup-formed, CBR1H window end, CBR15 Q−1 no longer block; V-1 remains | `phase13-readiness.md` |
| D20-10 | V-1 next action | Prepare ingestion; never fabricate; report V1_WAITING_FOR_OWNER_DATA when absent | `src/cbr/engine/v1_ingest.py`; protocol §6.3a |
| D20-11 | No course parity | Smoke tests only (runs, schemas, causal fields, deterministic selection); no comparison with Tom's labels before frozen tolerances | — |
| D20-12 | Report | PC2 hashes, files, OQ states, tests, totals, checklist, V-1 readiness, status | — |
