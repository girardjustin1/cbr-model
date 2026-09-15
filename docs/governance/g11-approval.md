# G11 CBR15 Engine Gate: Approval Record

**Doc:** CBR-GATE-G11 · **Date:** 2026-09-15 · **Decided by:** Owner (ruling D17) · **Phase:** 11 → 12

## Result

**PHASE 11: PASS WITH CONCERNS. G11 APPROVED** for engine construction quality, causality and determinism.
**CBR15 is NOT baseline-eligible.**

## Accepted

- STRUCTURE-only engine input; tick-derived midpoint structure prices
- Causal decision-time evaluation; lifecycle events separated from decision rules
- Complete candidate ledger; deterministic output; future-data mutation and truncation tests
- Spec-compliant latest confirmed swing-pair handling (F-3), with backward compatibility for existing callers
- No execution bid/ask inside the signal engine; no profitability-based rule changes
- The three course-example windows are hourly (CBR1H) examples: **diagnostic only for Phase 11, never described as
  CBR15 parity tests**

## Rulings (D17)

| Id | Item | Ruling | Implemented |
|---|---|---|---|
| D17-1 | OQ-34 hourly veto | **Open until Phase 12.** Report `NOT_EVALUATED`; not PASS, not FAIL; never reject an otherwise valid candidate solely because the hourly engine is unavailable; carry an explicit eligibility flag. Rerun CBR15 with M15-HTF-01 once CBR1H exists | Rule outcome `None` (in `rules_not_evaluated`, never in `rules_failed`); blocker `HTF_NOT_EVALUATED (OQ-34)` |
| D17-2 | OQ-35 stop anchor | **Resolved.** Stop anchor = the most adverse canonical STRUCTURE extreme of the active extension observed causally up to entry activation / fill (SHORT: highest; LONG: lowest). Execution spread and the final executable stop belong to the execution layer. Keep separate: extension extreme at candle open, evolving extension extreme, sweep extreme, structure extreme at activation, structure extreme at fill, final execution stop. CX-LT1-1 supports but doesn't universally validate this; later contradicting Level 1 evidence reopens OQ-35 | `candle_open_price`, `extension_extreme_at_decision`, `sweep_extreme`, `structure_stop_anchor` + `stop_anchor_time` + `stop_anchor_source`, `stop_anchor_path` (5s STRUCTURE), `structure_extreme_at_fill` = null (execution), `final_execution_stop` = null (14A) |
| D17-3 | OQ-36 prior working setup | **Current interpretation NOT approved.** Don't remove, weaken, zero or reinterpret COND-03 by signal count. Produce an OQ-36 evidence resolution package from Level 1 evidence before CBR15 is baseline-eligible; if evidence is insufficient, report unresolved | COND-03 unchanged; blocker `COND03_INTERPRETATION_UNAPPROVED (OQ-36)` on every candidate |
| D17-4 | OQ-37 trending range without direction | **Resolved.** Don't infer direction: `TREND_DIRECTION_UNRESOLVED` is a deterministic context failure, recorded in the ledger. New Level 1 evidence reopens it | Candle rule `M15-COND-TR-DIRECTION`; `context_reason`, `reject_reasons` |
| D17-5 | OQ-38 type 3 before the second half | **Approved with clarification.** A type 3 resolving before minute 7.5 isn't a valid CBR15 entry and doesn't stay armed (`TYPE3_RESOLVED_TOO_EARLY`). A new, causally independent type 3 later in the candle is evaluated normally; the early one is never resurrected | Lifecycle cancel `TYPE3_RESOLVED_TOO_EARLY` at the structure break; each swing pair arms once |
| D17-6 | F-3 | Spec-literal "last two confirmed swings" approved for the reference engines; legacy primitive behaviour preserved for unrelated callers and documented | `track_type3(latest_pair_only=True)` in engines |

## CBR15 baseline eligibility gate (all required)

1. OQ-36 resolved
2. Phase 12 provides hourly CBR state
3. M15-HTF-01 evaluable
4. Engine remains causal and deterministic
5. Rule changes from those resolutions covered by tests
6. Frozen CBR15 machine specification updated
7. Phase 13 prerequisites relevant to CBR15 satisfied

No Phase 16 baseline statistics before this gate passes.

## Phase 12

**Authorized** after this record (D17-7). No profitability, optimization, holdout P&L, Backtesting.py or Astra × Fable
review. V-1 remains a hard Phase 13 requirement.
