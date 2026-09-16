# Proposed PC3 Change Set (NOT IMPLEMENTED)

**Doc:** CBR-PC3-PROP · **Version:** v0.2 PROPOSED · **Date:** 2026-09-15 · **Rulings:** D26 §13, D27 §13
**Status:** FOR OWNER DECISION. PC2 stays frozen and available for audit. **Nothing here is implemented.** No item was
selected because it makes a course example pass. Groups per D27 §13: `CANON_CORRECTION` · `ASSUMPTION_CHANGE` ·
`IMPLEMENTATION_FIX` · `DIAGNOSTIC_ONLY` · `NO_CHANGE`.

Supersedes v0.1. Changes in this version: D8 and the weekend window resolved to NO_CHANGE; COND-04 resolved to removal
from canonical eligibility with diagnostics retained (D27 §3); HVCS items approved in principle (D27 §4-5); T3-1 and
extension activation now have completed evidence reviews.

Sources: `docs/decisions/t3-1-type3-sweep-evidence.md`, `extension-activation-evidence.md`,
`d8-extension-anchor-evidence.md`, `cond04-prior-setup-evidence.md`, `hvcs-continuity-evidence.md`,
`weekend-condition-window-note.md`, `reports/phase13r-cx-lt3-2-reconstruction.md`.

---

## 1. CANON_CORRECTION

| Id | Rule | Change | Evidence | Owner status |
|---|---|---|---|---|
| **H-1** | `M1H-6A-1` conforming candle | conform = respects the relevant high (DOWN) / low (UP) with directional progression; **drop the `close < open` requirement** | "we're respecting all the all the highs … consistently moving bearish" (V1H-seconds_shift_1m_hilo_hvcs 00:02:06, L1); "We're moving, respecting lows and highs" (VP2-1m_hilo_entries 00:05:19, L1); indecision candles allowed (VP2 00:04:49, L1) | **approved in principle (D27 §4)** |
| **H-2** | `M1H-6A-1` run end | the run may end on the bar that sets the extension extreme even if that bar closes against the sequence | same passages; CX-TE1-1's extreme bar respects the high and closes bullish | **approved in principle (D27 §4)** |
| **C04-1** | `M1H-COND-04` | **remove from canonical signal eligibility**; no prior-setup gate in CBR1H baseline | L1 states no hourly hard gate; the only hard clause is CBR15's slide; L2 gate statement is self-flagged as unevidenced | **ruled (D27 §3)** unless new L1 evidence appears before PC3 freeze |
| **T3-1** | 5s type-3 semantics | a newly confirmed opposing swing **re-anchors** the trigger instead of disarming the pattern (full definition in §6 of the T3 review) | EP1-008 "take out **a** low" (unqualified); EP2-001/002/003 HILO re-anchors to the most recent candle extremes; Tom equates HILO and 5s shift | **pending owner decision** (this review) |

## 2. ASSUMPTION_CHANGE

| Id | Parameter | Change | Evidence | Owner status |
|---|---|---|---|---|
| **ACT-1** | extension activation | replace the implicit `oe.activation_atr` activation with an evidence-linked concept: **B** (an early phase that is not yet the extension, range quoted as "seven to 15 minutes") or **D** (active once beyond the previous 15m high/low) | "the overextension can happen, can start around seven to 15 minutes in" (V1H-candle_behavior_timing 00:02:41, L1); "beyond previous high or low" (V1H-seconds_shift… 00:01:47, L1) | **pending owner choice of concept**; a number is required under B, not under D |
| **OE-2** | `M1H-OE-02` reference | define "50% of the previous move" as the current leg rather than the whole move since the anchor | "on average correcting 50% of the previous move" (V1H-defining_a_good_extension 00:05:16, L1) | open; the other half of the activation problem |
| **C04-4** | `prior.lookback_hours` | only if any prior-setup concept survives: use the L1 range (5-10+ h) rather than the assumed 10 h | V15-defining_ltf_range 00:07:00; V15-overview_methodology 00:04:26 | moot if C04-1 removes the gate |

## 3. IMPLEMENTATION_FIX

| Id | Item | Change | Owner status |
|---|---|---|---|
| **H-3** | `M1H-6A-1` evaluation instant | evaluate the HVCS sequence with information available at the canonical 5s shift decision time, never beyond it; add explicit causality tests | **approved (D27 §5)** |
| **C04-3** | `raw_setup_armed` recursion | if any prior-setup concept is retained as a diagnostic, its object must not require every other rule to pass | follows from D27 §3 |
| **T3-2** | `max_reversal` anchor | state explicitly whether the "immediately reverse" clock runs from the first sweep bar or the latest sweep extreme (changed one fixture result during prototyping) | open, OQ-09 |

## 4. DIAGNOSTIC_ONLY

| Id | Item | Treatment | Owner status |
|---|---|---|---|
| **C04-D** | prior-setup context | retain `prior_setup_exists`, `prior_setup_count`, `prior_setup_model`, `prior_setup_age` as diagnostics; L2 quality claims recorded as RESEARCH-DERIVED context, never a baseline veto; no outcome or profitability input | **ruled (D27 §3)** |
| **D8-LR** | `oe_origin = LAST_RESET` | research/diagnostic only; never the canonical baseline | **ruled (D27 §1)** |
| **HVCS-V** | LVCS / volume grading | unchanged: recorded, never a gate | existing |

## 5. NO_CHANGE

| Id | Item | Reason | Owner status |
|---|---|---|---|
| **D8-1** | `oe_origin = HOUR_OPEN` | evidence supports the hour open as the normal reference; no canonical reset rule exists | **ruled (D27 §1)** |
| **W-1** | condition-window basis | every window length in the quoted 5-12+ hour range reaches back across the weekend; the CX-LT3-2 condition mismatch is in the direction test, not the window | revised to NO_CHANGE (this package) |
| **S-1** | candidate selection | signal generation must be reconciled first | **ruled (D26 §10, D27 §10)** |
| **R-1** | `IMPL-REWARD`, `M1H-TIME-01`, `NT_*` | no evidence of a mismatch | — |

## 6. New open questions raised by this package

| Id | Question | Why it matters |
|---|---|---|
| **OQ-46 (proposed)** | Trending-range **direction** test: last two swing pairs, range position, or a directional measure? | blocks CX-LT3-2's condition (`M1H-COND-03`) independently of T3-1; OQ-01/OQ-02 adjacent |
| **OQ-47 (proposed)** | Does the type-3 sweep require a **named external** level (previous 15m high/low, range edge) rather than any prior swing? | T3-C; would reduce T3-B's 1.66× extra trigger volume |

## 7. Dependency order

1. **T3-1** (decide the sweep semantics) — upstream of every candidate.
2. **ACT-1 / OE-2** (when an extension exists and what its pullback is measured against).
3. **H-1 / H-2 / H-3** (HVCS) — already approved in principle, implement with the rest.
4. **C04-1 / C04-D / C04-3** (prior setup: remove the gate, keep diagnostics).
5. **OQ-46** if CX-LT3-2's condition is to be reconciled.

## 8. Before PC3 is validated (D26 §14)

An **expanded independent parity set** must be assembled first: positive type-3 examples, rejected/pass examples, both
directions, multiple sessions, both CBR1H variants and CBR15 where available, with no trade outcomes. The T3-1 review
records that today only CX-LT2-1/CX-LT2-2 (USDJPY, narrative only) and the two negative controls exist outside the
three parity examples, and **no additional data-testable positive example** is available in the stored data. Assembling
that set is itself a task the owner must authorize, because it may require new instruments or data.
