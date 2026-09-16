# Proposed PC3 Change Set (NOT IMPLEMENTED)

**Doc:** CBR-PC3-PROP · **Version:** v0.1 PROPOSED · **Date:** 2026-09-15 · **Ruling:** D26 §13 · **Status:** FOR OWNER DECISION
PC2 stays frozen and available for audit. **Nothing here is implemented.** No item was chosen because it makes a course
example pass; each cites evidence and states what is still missing. Classifications use D26 §13:
`CANON_CORRECTION` · `ASSUMPTION_CHANGE` · `IMPLEMENTATION_FIX` · `NO_CHANGE`.

Sources: `docs/decisions/d8-extension-anchor-evidence.md` (A), `cond04-prior-setup-evidence.md` (B),
`hvcs-continuity-evidence.md` (C), `reports/phase13r-cx-lt3-2-reconstruction.md` (D).

---

## 1. Summary table

| Id | Rule | Proposal | Class | Evidence strength | Blocks a course example? |
|---|---|---|---|---|---|
| H-1 | `M1H-6A-1` HVCS conforming candle | drop `close < open`; conform = respects the high (DOWN) / low (UP) | **CANON_CORRECTION** | strong (two L1 definitions) | yes — CX-TE1-1 |
| H-2 | `M1H-6A-1` end of run | allow the run to end on the extreme bar even if it closes against | **CANON_CORRECTION** | strong (same passages) | yes — CX-TE1-1 |
| H-3 | `M1H-6A-1` evaluation instant | evaluate the end bar as the extension-extreme bar known **at the shift**, not at the decision | **IMPLEMENTATION_FIX** | mechanical | yes — CX-LT1-1 |
| C04-1 | `M1H-COND-04` object | count prior **hourly candles with CBR candle behaviour**, not prior engine candidates | **CANON_CORRECTION** | moderate-strong | yes — all three |
| C04-2 | `M1H-COND-04` status | demote to a diagnostic / quality field for CBR1H | **CANON_CORRECTION** | moderate (L1 has no hourly gate) | yes — all three |
| C04-3 | `M1H-COND-04` recursion | a formed setup must not require every other rule to pass | **IMPLEMENTATION_FIX** | mechanical | yes — all three |
| C04-4 | `prior.lookback_hours` | 10 h → the L1 range (5 h, or "5-10+" as a declared assumption) | **ASSUMPTION_CHANGE** | moderate | no |
| OE-1 | `oe.activation_atr` | the minimum extension worth pullback-testing (currently 0.5 × ATR(1m) ≈ $1-2) | **ASSUMPTION_CHANGE** | no course number exists | yes — CX-LT1-1, CX-LT3-2 |
| OE-2 | `M1H-OE-02` reference | "50% of the previous move" = the current leg, not the move since the hour open | **CANON_CORRECTION** (ambiguity) | moderate | yes — all three |
| D8-1 | `oe_origin` | keep `HOUR_OPEN`; do **not** promote `LAST_RESET` on current evidence | **NO_CHANGE** | see A §6 | — |
| D8-2 | delayed extensions | handle the L1 "opens sideways, then pushes" case explicitly | **CANON_CORRECTION** (gap) | moderate (one clear L1 passage) | yes — indirectly |
| T3-1 | 5s type-3 sweep leg | what counts as the "take out the high" leg | **needs its own evidence review first** | open | yes — CX-LT3-2 |
| W-1 | `cond.window_basis` across a weekend | 8 tradable hours reaches into Friday on a Monday-Asia hour | **ASSUMPTION_CHANGE** | OQ-40 already an assumption | yes — CX-LT3-2 |
| S-1 | candidate selection | no change until signal generation is reconciled (D26 §10) | **NO_CHANGE** | — | — |
| R-1 | `IMPL-REWARD`, `M1H-TIME-01`, `NT_*` | no change | **NO_CHANGE** | — | — |

## 2. Items in detail

### H-1 / H-2 — HVCS conforming candle and run end · CANON_CORRECTION
**Now:** a candle counts only if it respects the side **and** closes in the trade direction; the run must end on such a
candle. **Proposed:** conform = respects the side; the run may end on the bar that sets the extension extreme.
**Evidence:** "we're respecting all the all the highs we're just you know consistently moving bearish"
(V1H-seconds_shift_1m_hilo_hvcs 00:02:06, L1); "We're moving, respecting lows and highs" (VP2-1m_hilo_entries 00:05:19,
L1); indecision candles explicitly allowed (VP2 00:04:49, L1). No source requires a close in the trade direction.
**Missing:** whether "high volume" should then carry the quality load that `close < open` was implicitly carrying
(OQ-08 is still open). **Effect:** CX-TE1-1's sequence becomes non-zero; CX-LT1-1 and CX-LT3-2 unaffected on their own.

### H-3 — HVCS end-bar instant · IMPLEMENTATION_FIX
**Now:** the end bar is the extension-extreme bar **closed at the decision**, so at the decision instant the
displacement bar may still be open (CX-LT1-1: 3 minutes at 01:38:40, 4 minutes at 01:39:35). **Proposed:** evaluate the
rule with the extreme bar known at the **shift** (still causal: the shift is later). **Missing:** confirmation that
D19-6 intended the decision instant rather than the trigger instant.

### C04-1 / C04-2 / C04-3 — the prior-setup rule · CANON_CORRECTION / IMPLEMENTATION_FIX
**Measured:** 0 raw setups formed in 60 hours; `M1H-COND-04` failed 536/536 candidates — the rule cannot be satisfied
because its object is recursive (B §2). **Evidence:** Tom counts prior **CBR-shaped hourly candles** ("the type of cbr
that you're going for happen previously", V15-defining_ltf_range 00:07:19, L1); L1 states no hourly hard gate, and L2
mostly treats a prior CBR as quality ("probably a little bit higher quality", 01:15:31). **Missing:** the reversal
geometry that defines "a candle that behaved as a CBR" (an assumption with a declared range would be needed).
C04-3 alone (fix the recursion) leaves the gate in place; C04-1 changes what is counted; C04-2 removes the gate.

### OE-1 / OE-2 — the pullback test · ASSUMPTION_CHANGE / CANON_CORRECTION
**Measured (A §4.1):** the retraces that fail `M1H-OE-02` occur in the first minutes of the hour against running
extensions of $2.45 (CX-LT1-1) and $4.27 (CX-LT3-2), versus full extensions of $35.77 and $33.00. The activation floor
`0.5 × ATR(1m)` makes a $2 wiggle an "extension" whose retrace disqualifies the hour for the rest of it.
**Evidence:** "on average correcting 50% of the previous move" (V1H-defining_a_good_extension 00:05:16, L1) reads as
leg-relative; "20 to 30 minutes of price action extending in one direction without a pullback" (00:02:12, L1) describes
the push. **No course number exists for the floor** — any value is an assumption with a declared research range.
**Deliberately not proposed here:** a specific floor value.

### D8-1 / D8-2 — the extension anchor · NO_CHANGE / CANON_CORRECTION
`LAST_RESET` recovers CX-TE1-1 and CX-LT3-2's extension rules but **breaks CX-LT1-1** (duration 15 min < 20) and rests
on L2 only, so it should not become the baseline (A §6). The real L1 gap is the delayed start: "If the alley candle
opens and kind of goes sideways for a bit and then pushes, you might have it set up around 37 to 52 minutes into the
hour" (V1H-candle_behavior_extension 00:10:42), bounded by "go sideways for 30 minutes … there isn't a trade"
(V1H-defining_a_good_extension 00:05:03). PC2 has no representation of this case.

### T3-1 — what is the "take out the high" leg? · needs a dedicated evidence review
**Measured (D §3-4):** at Tom's CX-LT3-2 entry, the engine classifies the same price event as the **sweep of a BUY**
type 3, and never arms a SELL, because it requires price to exceed an already-confirmed swing high **again**. Tom takes
the new high that took the previous 15m high (4053.43) as the sweep and sells the break of the low formed after it
(4050.97 → entry 4050.71).
**Evidence seen so far:** "you take out high take out low and then you shift" (VP1-1_4_shifts_type_3_choch 00:03:03,
L1) and the CBR emphasis on taking the previous 15m candle's high (`M1H-6A-2`, E1H-017/E1H-023) are both consistent
with Tom's reading; PC2's re-excursion requirement is an implementation reading of primitives §4.1.
**Recommendation:** a separate type-3 evidence review (phase 1 + phase 2 sources) before any PC3 change. This is the
single change most likely to alter signal membership broadly, so it must not be decided from three examples.

### W-1 — condition window across the weekend · ASSUMPTION_CHANGE
On CX-LT3-2 the 8 **tradable**-hour window starts Friday 16:00, so the hour's condition and its `NONE` direction
describe Friday, while Tom describes the Monday rally ("So very bullish, um, a little bit trendy"). Options: clock-time
window, a session-aware window, or a shorter window after a reopen. All are assumptions (OQ-40); none is proposed.

### S-1 — candidate selection · NO_CHANGE
Per D26 §10, selection stays frozen until signal generation is reconciled. Recorded for later: under `LAST_RESET`,
CX-LT1-1's first completed shift is 01:29:05 while Tom's is 01:39:15, so "first valid shift" would still not reproduce
him even after the trigger rules are settled.

## 3. Dependency order

1. **T3-1** (what a type-3 sweep is) — upstream of every candidate.
2. **OE-1 / OE-2** (what counts as an extension and its pullback), then **D8-2** (delayed starts).
3. **H-1 / H-2 / H-3** (HVCS), which only matter once candidates survive.
4. **C04-1…C04-3** (prior-setup object and status).
5. **W-1**, then **S-1** (selection), last.

Any subset the owner approves becomes PC3 with a new decision record, changed-rule list, evidence justification, new
hashes and a newly approved parity run (D26 §4). **Nothing is implemented until then.**
