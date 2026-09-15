# Phase 13 Readiness Checklist

**Doc:** CBR-READY-013 · **Created:** 2026-09-15 (owner ruling D18-12) · **Status:** NOT READY

Phase 13 (Tom ↔ Python parity) may not start while any required item is unchecked. Items are checked only by an owner
ruling or a recorded, reproducible result, with the reference noted.

| # | Item | Status | Reference / notes |
|---|---|---|---|
| 1 | [ ] OQ-36 resolved or formally owner-assumed | package delivered; evidence insufficient for "played out"; awaiting owner (candidate assumption C′) | evidence package: `docs/decisions/oq36-prior-setup-evidence.md` |
| 2 | [ ] OQ-39 resolved | package delivered; evidence strong for A (5s shift = trigger, two distinct variants); awaiting owner, canonical rule unchanged | evidence package: `docs/decisions/oq39-hourly-entry-evidence.md` |
| 3 | [ ] OQ-40 resolved | package delivered; `CONDITION_WINDOW_UNRESOLVED` on explicit evidence; B (tradable time) is the assumption candidate | evidence package: `docs/decisions/oq40-42-context-timing-evidence.md` |
| 4 | [ ] OQ-41 resolved | package delivered; evidence strong for R1 (Q−1, broken by Q); awaiting owner | same package |
| 5 | [ ] OQ-42 classified / resolved | package delivered; signal eligibility at the structure break (A) recommended; true-fill reading would be `EXECUTION_DEPENDENT`; veto vs downgrade open | same package |
| 6 | [ ] OQ-43 resolved | package delivered; adjacency (a) moderate; gap-bar limit has no source number | `docs/decisions/oq39-hourly-entry-evidence.md` §OQ-43 |
| 7 | [ ] D8/D9 classification rules frozen | proposed | `docs/governance/phase13-parity-protocol.md` §3 |
| 8 | [ ] parity tolerances frozen | proposed (values need V-1 non-course data) | `docs/governance/phase13-parity-protocol.md` §4 |
| 9 | [ ] candidate-selection rule frozen | proposed | `docs/governance/phase13-parity-protocol.md` §5 |
| 10 | [ ] V-1 data obtained and validated | not obtained | `docs/governance/phase13-parity-protocol.md` §6 |
| 11 | [ ] CBR15 spec frozen for parity | open: depends on items 1, 5 and item 16 (M15-HTF-01 split, D18-11) | |
| 12 | [ ] CBR1H spec frozen for parity | open (depends on 2-6) | |
| 13 | [ ] causality tests passing | passing at `95da789` (re-check at freeze) | `tests/engine/` |
| 14 | [ ] STRUCTURE/EXECUTION guard tests passing | passing at `95da789` (re-check at freeze) | `tests/test_price_series.py` |
| 15 | [ ] full test suite passing | 460 passed, 1 skipped at `95da789` (re-check at freeze) | |
| 16 | [ ] M15-HTF-01 split into SIGNAL-STATE (hourly veto on STRUCTURE) and EXECUTION-STATE (`HTF_FILL_STATE = NOT_EVALUATED`) in the CBR15 engine and report | not implemented | D18-11 |
| 17 | [ ] Engine updated to the owner's OQ-36/39/40/41/42/43 rulings, with unit tests | not started (blocked on rulings) | implementation maps |
| 18 | [ ] D8/D9 ablation switches (`oe_origin = LAST_RESET`; `early_shift_guard = FINAL_PUSH`, `ALIGN_15M`) implemented for STRICT COURSE PARITY, off by default, baseline hash unchanged | not implemented | protocol §2 |
| 19 | [ ] Parity runner selects candidates only by protocol §5 (Phase 12 "closest to Tom" selection removed) | not implemented | D18-9 |
| 20 | [ ] 2025-11-11 Dukascopy calibration-day ticks fetched (24 hour-files) | not fetched | protocol §6.2 |

Items 13-15 stay unchecked until re-run on the frozen specs.

**Current status (2026-09-15): NOT READY.** 0 of 20 items checked. Items 1-9 await owner rulings; 10 and 20 need data; 16-19 need implementation after rulings.
