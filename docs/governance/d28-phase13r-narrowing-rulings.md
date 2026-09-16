# D28 Phase 13R Upstream Review: Narrowing Rulings

**Doc:** CBR-RULING-D28 · **Date:** 2026-09-16 · **Decided by:** Owner ("OWNER RULING — PHASE 13R UPSTREAM REVIEW")

## Result

The Phase 13R upstream review is **accepted**. PC2 remains frozen as the failed parity candidate. **PC3 is not created.**
No Phase 13 rerun, no Phase 14, no backtest, no optimization, no P&L, no Astra × Fable review.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D28-1 | T3-B | **Leading canonical interpretation.** PC2's frozen pre-sweep pair behaviour is not well sourced. The architectural principle is approved: a newly confirmed opposing swing may become the current trigger, and the pattern must not disarm merely because a newer opposing swing forms. **Not yet authorized for PC3**: OQ-47 and OQ-01 must be resolved first |
| D28-2 | Event counts | 1.66× more raw type-3 events is neither evidence for nor against T3-B. Do not optimize the count; do not add restrictions to move it toward PC2 |
| D28-3 | OQ-47 | Highest-priority evidence question: what external structure must the sweep take (options A-G), with machine definitions and membership implications |
| D28-4 | OQ-47 application | Apply to all non-parity type-3 material (CX-LT2-1/2, drawn examples, HILO examples), reporting CONSISTENT / INCONSISTENT / NOT DETERMINABLE; never fabricate prices |
| D28-5 | OQ-01 | Reopened for the re-anchored model: at what exact causal time may a new swing become the trigger (options A-F). The rule must be causal; do not optimize N or ATR values; numeric outcomes are ASSUMPTIONS |
| D28-6 | OQ-09 | Resolve the reversal-timer anchor (first sweep event vs latest sweep-extreme update) from "immediately reverse" wording; not from fixture pass rate |
| D28-7 | Extension activation | **PC2's immediate activation from the hour open is not approved for PC3.** Opening noise must not permanently invalidate a later valid extension |
| D28-8 | Activation state model | `PRE_EXTENSION` (movements set context but cannot fail the 50% rule) → `EXTENSION_ACTIVE` (rule applies to the active extension) |
| D28-9 | Activation timing | `EARLIEST_EXTENSION_ACTIVATION = minute 7`, classified ASSUMPTION implementing CANON timing guidance; not a required activation time, not an expiry at minute 15; no dollar/ATR floor to fit the examples; record `pre_extension_start`, `extension_activation_time`, `extension_activation_reason`, `extension_origin_price`, `extension_extreme_path` |
| D28-10 | Qualifying push | Define from existing canon (directional progression, extension toward the range extreme, previous-candle take, existing OE geometry). No new indicator; present alternatives if several remain |
| D28-11 | OE-2 | Stays open until activation is defined, then determine the 50% reference (full move from the hour open / active extension leg / latest push / other) from Level-1 language; not from which recovers the examples |
| D28-12 | HVCS | H-1 / H-2 CANON_CORRECTION and H-3 IMPLEMENTATION_FIX approved for the future PC3 set; implement only after PC3 is authorized |
| D28-13 | `M1H-COND-04` | **Remove as a hard canonical gate for PC3.** Preserve prior-setup information as diagnostics only. Does not affect the distinct CBR15 rule, which Level-1 evidence supports |
| D28-14 | D8 | **No change**: `HOUR_OPEN` stays canonical; `LAST_RESET` is not promoted. The activation states address early noise separately |
| D28-15 | W-1 | **No change**: keep the tradable-time window; OQ-46 is the relevant CX-LT3-2 issue. Do not alter the lookback to isolate Monday |
| D28-16 | OQ-46 | Focused evidence review of direction in a contracting range; do not invent a trend classifier; do not decide from CX-LT3-2 alone |
| D28-17 | Expanded parity set | Authorized to build. No new instruments in backtest research scope; USDJPY course examples usable for strategy-definition parity only. Label every example; prioritize examples with real data; no outcomes |
| D28-18 | Expanded set goal | Minimum contents listed; separate MACHINE PARITY SET from NARRATIVE / GEOMETRY CONSISTENCY SET |
| D28-19 | PC3 creation gate | PC3 may not be created until seven items are returned: OQ-47, OQ-01, OQ-09, activation definition, OE-2, OQ-46 and the parity-set inventory |
| D28-20 | Next report | Ten specified items, then stop |

## Deliverables produced under this ruling

| Gate item | Deliverable |
|---|---|
| OQ-47 external sweep review | `docs/decisions/oq47-external-sweep-evidence.md` |
| OQ-01 swing confirmation timing | `docs/decisions/oq01-swing-confirmation-evidence.md` |
| OQ-09 max_reversal timing | `docs/decisions/oq09-max-reversal-anchor.md` |
| Extension activation definition | `docs/decisions/extension-activation-definition.md` |
| OE-2 pullback reference | `docs/decisions/oe2-pullback-reference-evidence.md` |
| OQ-46 direction review | `docs/decisions/oq46-trending-range-direction-evidence.md` |
| Expanded parity-set inventory | `research/examples/expanded-parity-set-inventory.md` |
| Final proposed PC3 change set | `docs/strategy/pc3-proposed-change-set.md` (v0.3, not implemented) |

42 transcript quotes verified mechanically across the Phase 13R package (0 failures). PC2 spec hash unchanged
(`4dadc8b9…`). All measurements are STRUCTURE-data diagnostics; the type-3 comparison engine remains a scratchpad
prototype and was never added to `src/`.

## Status

PC2 frozen; PC3 not created; Phase 13 not rerun; Phase 14 not authorized. **Stopped for owner review.**
