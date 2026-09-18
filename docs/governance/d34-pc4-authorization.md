# D34 — PC4 creation authorized after D32 / D33

**Doc:** CBR-DEC-034 · **Date:** 2026-09-17 · **Status:** owner ruling recorded; PC4 created, scoring **not** authorized
**Scope:** PC4 creation only. No Phase 13 rerun · no Phase 14 · no backtest · no optimization · no P&L or trade
outcome · no Backtesting.py · no Astra × Fable review.

The completed scored runs stay permanently frozen and are not altered or overwritten: **PC2 FAIL**
(CBR-RUN-013B-2) · **PC3 FAIL** (CBR-RUN-013C-1).

---

## 1. The research position (D34 §1)

**PC2** reproduced the broad setup context but failed Tom's core 5-second structural trigger on 3/3 positive examples.

**PC3** reproduces the underlying 5-second structural event and its approximate timing on **3/3**, then rejects all
three downstream through `M1H-6A-1-HVCS-INTO-SHIFT`, plus one separately identified previous-15m evaluation-time
issue. Working PC3 components are not reopened without new direct evidence (§13).

## 2. Rulings implemented in PC4

| § | Ruling | Implementation | Classification |
|---|---|---|---|
| §2 | **F-1**: restore `hvcs.max_violations = 1`. The setting stayed configured, loaded, documented and inherited; its omission from PC3 was not authorized. Value not changed, not optimized | `src/cbr/structure/shifts_pc4.py` | IMPLEMENTATION_FIX |
| §3 | **HVCS anchor**: keep the extension-extreme endpoint. The shift-anchored reading is **not** adopted and must not be adopted because it produces 3/3. `HVCS_TO_SHIFT` is preserved as a diagnostic only | `hvcs_to_shift_minutes`, never gates | NO_CHANGE (anchor) |
| §4 | **OQ-48** stays UNRESOLVED_SPEC_AMBIGUITY. PC4 uses the simplest inherited deterministic convention and keeps the ambiguity visible in the spec. No alternate convention during a scored run | `config/strategy_pc4.yaml` → `documented_assumptions` | ASSUMPTION_CHANGE (F-11) |
| §5 | **OQ-50, narrow**: only the two rules whose requirement is directly "the active 15m candle has taken the previous completed 15m high/low" move to the final 5s shift — `M1H-6A-2` and `M1H-6A-3`. Overextension quality, activation, condition and other location rules do **not** move | `_prev_15m_at_shift()` | CANON_CORRECTION (F-9) |
| §6 | **Q** = the 15m candle containing the final canonical 5s entry shift; **Q−1** = the previous completed 15m candle; judged only from data available through the shift decision instant | same | ASSUMPTION (F-10) |
| §13 | Components that recovered Tom's trigger geometry stay unchanged | — | NO_CHANGE |

## 3. What PC4 does **not** change

Type-3 re-anchoring · the latest sweep-extreme reversal timer · the whole-extension pullback ·
PRE_EXTENSION / EXTENSION_ACTIVE · minute-7 earliest activation · the Q1 activation qualifier · the HOUR_OPEN
reference · ATR zig-zag k = 3 · directionless trending range → RANGE · candidate selection · the tradable-time
window · the removal of the CBR1H prior-setup hard gate · every `M1H-LOC-*`, `M1H-OE-*` and `M1H-COND-*` evaluation
instant.

## 4. Parity-set rulings (D34 §9-12)

- The journal case belonging to a model the CBR1H engine does not implement (**JM-2025-10-17**, an inverse fractal
  shift) is removed from binding CBR1H machine parity and preserved for its correct future model —
  **PARITY_SET_CORRECTION**.
- The journal row with contradictory source columns (**JM-2025-10-29**) moves to **NARRATIVE / REFERENCE** and may not
  bind a CBR1H verdict; nothing about it is inferred from engine output — **PARITY_SET_CORRECTION**.
- **JM-2025-10-16** may stay in machine parity at `model_scope = CONFIRMED_CBR1H`, scored no further than the journal
  source actually states.
- Every binding machine case must carry `case_id`, `source`, `evidence_level`, `model_scope`, `direction`,
  `positive_or_negative`, `scoring_level`, `source_supported_fields`, `market_data_hashes` and `evidence_hashes`, and
  must satisfy `model_scope = CONFIRMED_CBR1H`.

## 5. Process rulings carried into the next protocol

- **§16 Strict / descriptive reporting**, pre-declared before any run: the STRICT view scores only eligible signals;
  the DESCRIPTIVE view may show the closest structurally relevant candidate for diagnosis and can never satisfy
  strict acceptance.
- **§17 Smoke tests**: synthetic fixtures only before the freeze. The real scored parity set must not be executed
  before the candidate and protocol are frozen.
- **§15**: no scored parity case may be used as a development test.

## 6. Status

PC4 is created and frozen as `CBR1H_BASELINE_V1-PC4`. **PC4 scoring is not authorized.** The proposed protocol
`CBR-PROT-013D` is drafted and not run. The completion report is
`docs/governance/d34-pc4-creation-report.md`.
