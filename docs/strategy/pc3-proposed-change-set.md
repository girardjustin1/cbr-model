# Proposed PC3 Change Set (NOT IMPLEMENTED)

**Doc:** CBR-PC3-PROP · **Version:** v0.3 FINAL PROPOSAL · **Date:** 2026-09-16 · **Rulings:** D26 §13, D27 §13, D28 §19-20
**Status:** FOR OWNER APPROVAL. PC2 stays frozen and available for audit. **Nothing here is implemented.**
Supersedes v0.2. Every item cites a completed evidence review; none was selected because it recovers a parity example.

Reviews behind this set: `t3-1-type3-sweep-evidence.md` · `oq47-external-sweep-evidence.md` ·
`oq01-swing-confirmation-evidence.md` · `oq09-max-reversal-anchor.md` · `extension-activation-definition.md` ·
`oe2-pullback-reference-evidence.md` · `oq46-trending-range-direction-evidence.md` · `hvcs-continuity-evidence.md` ·
`cond04-prior-setup-evidence.md` · `d8-extension-anchor-evidence.md` · `weekend-condition-window-note.md` ·
`research/examples/expanded-parity-set-inventory.md`.

---

## 1. CANON_CORRECTION

| Id | Rule | Change | Evidence | Owner status |
|---|---|---|---|---|
| **T3-1** | 5s type-3 semantics | a newly confirmed opposing swing **re-anchors** the trigger instead of disarming the pattern | EP1-008 "take out **a** low" (unqualified); EP2-001/002/003 HILO re-anchors per candle; Tom equates HILO and 5s shift | principle **approved** (D28 §1); authorization pending OQ-47 + OQ-01 |
| **OE-2** | `M1H-OE-02` reference | the 50% retrace is measured against **the extension as a whole** (deepest adverse excursion vs the extension to the extreme so far), re-evaluated at each decision, **no latch** | "Didn't correct 50% at all. Didn't even come close to that" (L1, applied to a chart); "on average correcting 50% of the previous move" | **new recommendation** |
| **H-1** | `M1H-6A-1` conforming candle | conform = structural respect and directional progression; drop `close < open` | "respecting all the all the highs … consistently moving bearish"; "respecting lows and highs"; indecision candles allowed | **approved** (D27 §4) |
| **H-2** | `M1H-6A-1` run end | the run may end on the bar that sets the extension extreme | same | **approved** (D27 §4) |
| **C04-1** | `M1H-COND-04` | remove from canonical signal eligibility | no L1 hourly gate; L2 gate self-flagged as unevidenced; PC2 form unsatisfiable (0 raw setups in 60 hours) | **ruled** (D27 §3, D28 §13) |
| **OQ-46** | condition taxonomy | when the correction ratio says trending range but no clear HH/HL (or LL/LH) sequence exists, classify **RANGE** rather than a directionless trending range | "this is more of a trending range **because we're making high highs and high lows**"; "still correcting … **but you're making clear** [higher highs/lows]" | **new recommendation** |

## 2. ASSUMPTION_CHANGE

| Id | Parameter | Change | Classification note | Owner status |
|---|---|---|---|---|
| **ACT-1** | extension activation | two-state model: `PRE_EXTENSION` → `EXTENSION_ACTIVE`; `EARLIEST_EXTENSION_ACTIVATION = minute 7` | ASSUMPTION implementing CANON timing guidance ("can start around seven to 15 minutes in") | **ruled** (D27 §8-9) |
| **ACT-2** | qualifying directional push | **Q1**: price trades beyond the previous 15m candle's extreme in the extension direction, at or after minute 7 | no new indicator, no dollar/ATR floor; reuses the `M1H-6A-2` concept | **recommended** (alternative Q2 offered) |
| **ACT-3** | `M1H-OE-01` duration | measure the 20 minutes from `extension_activation_time` | matches the "13 minute delay … only a seven minute extension" passage | **recommended** |

## 3. IMPLEMENTATION_FIX

| Id | Item | Change | Owner status |
|---|---|---|---|
| **H-3** | HVCS evaluation instant | evaluate causally through the canonical 5s shift decision time; no information after the shift; add causality tests | **approved** (D27 §5) |
| **OQ-09** | type-3 reversal timer | the `max_reversal` clock runs from the **latest update of the sweep extreme** ("take out high, **then** reverse, immediately reverse") | **recommended** |
| **C04-3** | `raw_setup_armed` recursion | remove the recursive dependency now that COND-04 is diagnostic | follows D28 §13 |
| **ACT-4** | new recorded fields | `pre_extension_start`, `extension_activation_time`, `extension_activation_reason`, `extension_origin_price`, `extension_extreme_path` | **ruled** (D27 §9) |

## 4. DIAGNOSTIC_ONLY

| Id | Item | Treatment | Owner status |
|---|---|---|---|
| **C04-D** | prior-setup context | `prior_setup_exists`, `prior_setup_count`, `prior_setup_age`, `prior_setup_model`; never canonical eligibility; no outcomes | **ruled** (D28 §13) |
| **OQ-47-D** | "sweep extreme = hour extension extreme" | keep as the pre-registered D9 ablation `FINAL_PUSH`, not a canonical requirement | **recommended** (OQ-47 review) |
| **D8-LR** | `oe_origin = LAST_RESET` | research/diagnostic only | **ruled** (D27 §1) |
| **HVCS-V** | LVCS / volume grading | recorded, never a gate | existing |
| **OQ-01-S** | swing-parameter sensitivity | record that under re-anchoring, k = 4 loses CX-LT3-2's trigger while CX-LT1-1 is insensitive | **new**, as an explicit spec risk |

## 5. NO_CHANGE

| Id | Item | Reason | Owner status |
|---|---|---|---|
| **D8-1** | `oe_origin = HOUR_OPEN` | canonical hourly reference; activation handles early noise separately | **ruled** (D27 §1, D28 §14) |
| **OQ-01** | swing definition and k = 3 | no course definition exists; causal with 60-140 s margin on all three examples; changing it now would confound the T3-B decision | **recommended** |
| **OQ-47** | external level on the sweep | externality already carried by `M1H-6A-2` and `M1H-LOC-01/02/03`; the one L1 statement about the trigger's own external need is a denial | **recommended (option G)** |
| **W-1** | condition-window basis | every window in the 5-12+ h range reaches across the weekend; not the cause of the CX-LT3-2 condition | **ruled** (D28 §15) |
| **S-1** | candidate selection | signal generation first | **ruled** (D27 §10, D28 §10) |
| **R-1** | `IMPL-REWARD`, `M1H-TIME-01`, `NT_*`, CBR15 prior-setup rule | no evidence of a mismatch; CBR15's rule is separately evidenced | **ruled** (D28 §13) |

## 6. Combined effect on the three course examples (diagnostic, not a score)

| Layer | With this set |
|---|---|
| Extension direction, extreme, timing | already correct under PC2 |
| `M1H-OE-02` | passes on all three (retraces 25% / 22% / 19% of the extension) |
| `M1H-6A-1` | CX-TE1-1 no longer fails on the close-direction test; CX-LT1-1 no longer fails on the bar-close instant |
| `M1H-COND-04` | no longer blocks (diagnostic) |
| `M1H-COND-03` (CX-LT3-2) | no longer blocks; the hour reads as RANGE and `M1H-LOC-01` passes at position 1.69 |
| 5s trigger | CX-LT1-1 4340.19, CX-TE1-1 4105.57, CX-LT3-2 4050.96 — Tom's three entries |
| CX-LT3-1 negative control | still no eligible signal in the control window |

**This is a forecast from component diagnostics, not a parity run.** Nothing was run end-to-end, and candidate
selection (unchanged) may still pick an earlier shift in a given hour.

## 7. Dependency order for implementation

1. T3-1 (+ OQ-09 timer anchor) — upstream of every candidate
2. OE-2, then ACT-1/2/3 (activation)
3. H-1 / H-2 / H-3
4. C04-1 / C04-D / C04-3
5. OQ-46

## 8. Validation requirement before PC3 is scored (D28 §14, §17-18)

The expanded parity set must be assembled first. Today the machine-testable set is still 3 positive + 1 negative, all
XAUUSD CBR1H Asia-session. `research/examples/expanded-parity-set-inventory.md` identifies four dated candidates for
acquisition (three XAUUSD journal dates, one CBR15 walkthrough) requiring extraction work and owner-authorized data
fetches, plus six narrative geometry cases.
