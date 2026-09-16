# D29 PC3 Authorization: Ruling Record

**Doc:** CBR-RULING-D29 · **Date:** 2026-09-16 · **Decided by:** Owner ("OWNER RULING — PHASE 13R PC3 GATE")

## Result

The Phase 13R PC3-gate review is accepted. PC2 remains **permanently frozen** as the failed parity candidate.
**PC3 creation is authorized. PC3 scoring is not.** No Phase 13 rerun, no Phase 14, no backtest, no optimization, no
P&L, no Astra × Fable review.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D29-1 | T3-1 | **Approved for PC3 (CANON_CORRECTION).** Use T3-B: sweep = price takes the relevant confirmed swing; the sweep extreme keeps updating while price extends; the trigger is the most recently confirmed opposing swing available causally; a newer opposing swing **re-anchors** the trigger and never disarms the pattern; completion is the break of the current trigger |
| D29-2 | OQ-47 | **Option G approved.** The type-3 trigger needs no separately named external level; externality stays in the previous-15m take, the beyond-structure/location rules and range context. `FINAL_PUSH` (sweep at the extension extreme) remains a **research ablation only** |
| D29-3 | OQ-01 | **No change for PC3.** ATR zig-zag, k = 3, ASSUMPTION. Not changed during the PC3 parity cycle; the k = 4 sensitivity (CX-LT3-2 disappears) is recorded for later robustness work; never optimized from parity examples |
| D29-4 | OQ-09 | **Approved.** The max-reversal timer starts from the most recent update of the sweep extreme; every new sweep extreme resets it. Preserve `first_sweep_time`, `latest_sweep_extreme_time`, `trigger_confirmation_time`, `trigger_break_time` as diagnostics |
| D29-5 | Extension activation | **Approved.** Two states: `PRE_EXTENSION` (the no-50%-pullback rule does not apply) and `EXTENSION_ACTIVE`. Earliest transition minute 7, an ASSUMPTION implementing the Level-1 guidance that the overextension can begin about 7-15 minutes into the hour; activation is never required exactly at minute 7 |
| D29-6 | Activation qualifier | **Q1 approved.** The push qualifies once the active move takes the relevant extreme of the immediately previous completed 15-minute candle, subject to the remaining context rules. No ATR, dollar, RSI or volume threshold. Record `extension_activation_time`, `extension_activation_price`, `extension_activation_reason`, `previous_15m_reference` |
| D29-7 | Extension duration | Measured from `extension_activation_time`, not the hour open. The hour open stays the canonical hourly reference (ASSUMPTION_CHANGE) |
| D29-8 | OE-2 | **Approved (CANON_CORRECTION).** The 50% rule is evaluated against the whole active extension with **no permanent early latch**: extension origin → running extreme → deepest opposing retracement, recomputed causally as the extension evolves |
| D29-9 | No lookahead | The ruling does not authorize hindsight. At any decision time, extension magnitude and deepest retracement use only data available then. Tests must prove truncation-invariance and that future extremes or retracements never rewrite an earlier verdict |
| D29-10 | HVCS H-1 / H-2 | **Approved (CANON_CORRECTION).** Remove the close-direction requirement; validity is structural progression and respect; indecision candles allowed; no arbitrary maximum count |
| D29-11 | HVCS H-3 | **Approved (IMPLEMENTATION_FIX).** Evaluate the sequence causally through the 5-second shift decision time; never before the final relevant minute bar is known, never after the shift |
| D29-12 | M1H-COND-04 | **Approved for removal** from canonical eligibility; the 10-hour assumption leaves the baseline. Prior-setup information is preserved as DIAGNOSTIC_ONLY; the fields are not deleted |
| D29-13 | CBR15 prior setup | **No change**: separately supported by its own course evidence |
| D29-14 | OQ-46 | **Approved (CANON_CORRECTION).** `TRENDING_RANGE` with `DIRECTION = NONE` is not in the taxonomy: classify such a context as `RANGE` rather than blocking the hour. No trend direction inferred, no new classifier |
| D29-15 | D8 | **No change**: `HOUR_OPEN`; `LAST_RESET` diagnostic/research only |
| D29-16 | W-1 | **No change**: keep the tradable-time window |
| D29-17 | Candidate selection | **No change for PC3 creation.** During the expanded parity run, a correct structural event chosen against a different earlier eligible candidate is reported as **CANDIDATE_SELECTION_MISMATCH** and returned for owner review; never silently changed |
| D29-18 | PC3 specs | Create immutable `CBR15_BASELINE_V1-PC3.yaml` and `CBR1H_BASELINE_V1-PC3.yaml`; do not modify PC2; list every difference with its classification, evidence references, decision ids, config changes, code hashes and unresolved assumptions |
| D29-19 | PC3 implementation | Implement the approved rules with independent tests for each before any scored run: type-3 re-anchoring (trigger update, no future leakage, timer reset, expiry, BUY/SELL symmetry); extension (pre-extension state, no pullback failure before activation, earliest minute 7, Q1, whole-extension pullback, no latch, causal evolution); HVCS (indecision allowed, invalid bar rejected, shift-time evaluation); prior setup (eligibility unaffected by its absence); condition (directionless trending range falls back to RANGE) |
| D29-20 | No scoring | Unit, causality, determinism, schema and synthetic smoke runs are allowed. Scored parity against CX-LT1-1, CX-TE1-1 and CX-LT3-2 is **not**, until the expanded parity set is frozen. No informal answer-aware adjustment after PC3 creation |
| D29-21 | Expanded set | Authorized to extract and acquire the identified XAUUSD examples (2025-10-16, 2025-10-17, 2025-10-29 and the ~2026-05 CBR15 walkthrough). Extract Level-1 metadata **before** fetching market data |
| D29-22 | Data fetch | Once extracted, fetch the minimum required Dukascopy XAUUSD tick windows with enough warm-up for range, swings, extension, prior candles and the lower-timeframe trigger. No unrelated history. Record every fetch and purpose. Parity fixtures only |
| D29-23 | Parity set structure | Build a MACHINE PARITY SET and a NARRATIVE / GEOMETRY SET; the narrative set validates geometry but never contributes to machine-pass counts |
| D29-24 | Required contents | The four original machine cases, the additional dated XAUUSD examples, the 2026-05 CBR15 example if datable, and the narrative cases. Examples are not discarded because PC3 fails them |
| D29-25 | Scoring protocol | Before running PC3, propose **CBR-PROT-013C** defining the exact core-trigger composition before execution, per variant and for CBR15. No evaluator discretion after the run |
| D29-26 | OQ-01 sensitivity | k = 3 for PC3 parity; no k = 2/3/4 alternatives during a scored run; sensitivity belongs to later robustness research |
| D29-27 | Completion gate | PC3 implementation is ready when: changes implemented, new rule tests pass, causality and determinism pass, PC2 unchanged, PC3 specs frozen, expanded extraction complete, authorized data acquired, expanded set frozen, CBR-PROT-013C proposed. Do not run CBR-PROT-013C without owner approval |
| D29-28 | Next report | Eleven items, then stop |

## Implementation note

PC3 is **additive**: PC2 pins the hashes of `engine/cbr1h.py`, `structure/shifts.py`, `structure/overextension.py`,
`structure/condition.py`, `engine/params.py` and `config/strategy.yaml`, so PC3 introduces new modules
(`cbr1h_pc3.py`, `shifts_pc3.py`, `overextension_pc3.py`, `condition_pc3.py`, `params_pc3.py`, `config/strategy_pc3.yaml`)
and leaves every PC2 file byte-identical. `tests/engine/test_parity_candidate_specs.py` continues to guard PC2.
