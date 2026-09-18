# D38 — Phase 14A execution semantics, frozen before any historical outcome

**Doc:** CBR-DEC-038 · **Date:** 2026-09-18 · **Status:** owner ruling recorded and implemented
**Config:** `config/execution.yaml` (spec_version `EXEC-14A`) · **Baseline:** `CBR1H_BASELINE_V1` = frozen PC4
`62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7`

Phase 13 remains **RESEARCH-SUFFICIENT WITH DOCUMENTED FIDELITY CONCERNS**; PC2, PC3 and PC4 parity runs remain
**FAIL** and are never rewritten. No P&L was inspected while implementing these rules, nothing was optimized, PC4 was
not altered, and signal membership was not touched.

---

## The frozen semantics

| § | Question | Ruling | Where it lives |
|---|---|---|---|
| §1 | Separation | Execution decides fill / price / stop / target / exit / R only. It never decides that a signal exists, its direction or any CBR context | `src/cbr/execution/*`, guarded by `tests/execution/test_architecture_guard.py` |
| §2 | **E-OQ-1 / OQ-28** stop construction | Final stop computed **at entry fill** from the latest canonical STRUCTURE anchor available causally through the fill, plus the approved buffer and the frozen spread policy — then **frozen**, never trailed | `position.resolve_stop`, `position.anchor_through` |
| §3 | Sides | LONG enters on ASK, stop/target on BID; SHORT enters on BID, stop/target on ASK. Structure anchors stay tick-mid | `fills.py` |
| §4 | **E-OQ-2** forced exit | **None.** Canon supplies no mechanical time exit. Only `ROLLOVER_EXIT` and `DATASET_END_EXIT` exist, labelled separately and never called canonical CBR exits | `ledger.CANONICAL_EXITS`, `simulate._close_open_position` |
| §5-6 | Rollover / dataset end | No entry may fill inside the exclusion window; an open position is closed on the last executable quote before it; a position open at data end closes for ledger completeness and is reported separately | `orders.window`, `simulate` |
| §7-8 | **E-OQ-3** sequencing | **Actual tick sequence is authoritative**; the first event observed wins. Where tick sequencing is unavailable: `EXECUTION_UNPROVABLE_INTRABAR`, never a favourable convention | `fills.first_event`, `prices.quotes_from_*` |
| §9 | **E-OQ-4** slippage | Additional slippage **0**, recorded as an ASSUMPTION — not a claim that real slippage is zero | `config/execution.yaml`, `ledger.net_r` |
| §10-11 | **E-OQ-5** entry fill | First executable quote that triggers; the theoretical trigger price is never granted; nothing fills before activation | `fills.entry_touch` |
| §12 | **E-OQ-6** stop gap | Fills at the first executable quote after the breach, at the worse price | `fills.stop_touch` |
| §13 | Target gap | LIMIT semantics: fills **at the target price**; a gap never awards improvement (deliberately conservative) | `fills.target_touch` |
| §14-15 | **E-OQ-7** position scope | One open CBR1H position per instrument; the first fill in tick sequence wins; orders pending at that moment are cancelled; later signals while open are logged, not executed | `simulate.simulate`, `position.PositionBook` |
| §16 | Rollover entries | No activation or fill inside the window; a pending order reaching it is `ROLLOVER_CANCEL` | `orders.window` |
| §17 | **E-OQ-9** spread fallback | **None.** No median, daily, fixed, neighbouring, futures or forward-filled spread → `EXECUTION_DATA_UNAVAILABLE` | `prices.spread_at`, `simulate` |
| §18-21 | **E-OQ-10** missing data | No interpolation, no forward fill, no synthetic execution. Only a classified `DATA_GAP` makes an outcome unprovable; scheduled closure, rollover and sparse quoting do not | `prices.Gap`, `simulate` |
| §22-23 | R | Risk from the actual filled trade, must be > 0 or `EXECUTION_INVALID_RISK`; gross R as ruled; net R never double-counts spread | `ledger.initial_risk`, `gross_r`, `net_r` |
| §24 | Commission | `explicit_commission = 0`, ASSUMPTION / NOT YET BROKER-SPECIFIC | `config/execution.yaml` |
| §25 | Target | The frozen PC4 canonical target is used as given; no variant tested | `contract.parse` |
| §26 | Eligibility | External D37 promotion gate; PC4 and its records are never edited | `contract.eligible` |
| §27-28 | Ledger | One row per signal; closed status and reason enumerations; exit reasons only on CLOSED rows | `ledger.ExecutionRecord.validate` |
| §29 | No performance | Synthetic and mechanics only; no historical population run | — |
