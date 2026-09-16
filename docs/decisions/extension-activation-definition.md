# Extension Activation: Deterministic Definition for PC3 Planning

**Doc:** CBR-DEF-ACT · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §7-10 (from D27) · **Status:** FOR OWNER DECISION
PC2 frozen; nothing implemented. Builds on `extension-activation-evidence.md`. **No dollar/ATR displacement floor is
proposed** (D27 §10). Diagnostics from STRUCTURE data; no outcomes.

---

## 1. The state model (owner-specified, D27 §8)

| State | Meaning | Rules that apply |
|---|---|---|
| `PRE_EXTENSION` | from the hour open until a qualifying directional push has begun | movements establish context and extremes but **cannot fail** the no-50%-pullback rule |
| `EXTENSION_ACTIVE` | from activation onward | the no-50%-pullback rule applies to the **active** extension |

`EARLIEST_EXTENSION_ACTIVATION = minute 7` (D27 §9): the earliest minute at which the transition may occur, classified
**ASSUMPTION implementing CANON timing guidance** ("the overextension can happen, can start around seven to 15 minutes
in", V1H-candle_behavior_timing 00:02:41). Minute 7 is not itself an activation condition, and minute 15 is not an
expiry.

Fields to record: `pre_extension_start`, `extension_activation_time`, `extension_activation_reason`,
`extension_origin_price`, `extension_extreme_path`.

## 2. Candidate "qualifying directional push" definitions, built only from existing canon

| Id | Definition (activation = first time at or after minute 7 that the condition holds) | Canon source already in the spec |
|---|---|---|
| **Q1** | price trades **beyond the previous 15m candle's extreme** in the extension direction | `M1H-6A-2` concept; "the 15-minute candle to take out the previous high or low to be beyond structure" (L1) |
| **Q2** | price trades **beyond the most recent MTF (5m) swing** in the extension direction | `M1H-LOC-02` concept ("beyond structure") |
| **Q3** | the hour's extreme reaches the **range-extreme zone** (`pos ≥ range_extreme`, or ≤ 1 − it) | `M1H-LOC-01` concept |
| **Q4** | the current directional **leg** into the hour's extreme has begun (most adverse point at or after minute 7) | existing overextension geometry |

None introduces a new indicator, threshold, dollar amount or ATR floor.

## 3. Measured behaviour on the three course hours

Activation time, duration to the extreme, and whether the no-50%-pullback test passes **on the active extension**
(reading R1, the running sub-extension, as PC2 measures it):

| Example | Q1 | Q3 | Q4 |
|---|---|---|---|
| CX-LT1-1 | 01:07 (+7m), 31m, **fails** (margin −2.21) | 01:30 (+30m), 8m, fails (−1.74) | 01:10 (+10m), 28m, fails (−1.39) |
| CX-TE1-1 | 04:07 (+7m), 30m, fails (−0.96) | 04:15 (+15m), 22m, **passes** (+0.17) | 04:10 (+10m), 27m, fails (−1.75) |
| CX-LT3-2 | 01:10 (+10m), 27m, fails (−0.93) | 01:07 (+7m), 30m, fails (−1.60) | 01:09 (+9m), 28m, fails (−0.39) |

**Finding: the state model alone does not reconcile the examples.** Under every activation definition, small retraces
*after* activation still fail the pullback test while the active extension is young. The residual cause is not *when*
the extension starts but *what the 50% is measured against* — see `oe2-pullback-reference-evidence.md`, where the
whole-extension reading (R2) passes all three at 25%, 22% and 19% with no activation threshold at all.

## 4. Consequences for the two decisions

The two questions are **not independent**:

| Combination | Result on the three examples |
|---|---|
| Activation state + R1 (running sub-extension) | still fails (§3) |
| No activation state + R2 (whole extension) | passes all three (25% / 22% / 19%) |
| Activation state + R2 | passes all three; activation additionally protects against pre-push noise being counted as the extension |

The activation state is therefore **worth keeping for the reason the owner gave** — opening noise must not permanently
invalidate a later valid extension — but it is **not sufficient on its own**, and the pullback reference (OE-2) is the
operative fix.

## 5. Recommendation

1. **Adopt the two-state model** with `EARLIEST_EXTENSION_ACTIVATION = minute 7` as an ASSUMPTION implementing canon
   timing guidance, and record the five fields.
2. **Adopt Q1 as the qualifying push** ("beyond the previous 15m candle's extreme in the extension direction"): it is
   the most directly evidenced ("the 15-minute candle to take out the previous high or low to be beyond structure"),
   needs no number, activates at +7 / +7 / +10 minutes on the three examples — inside the quoted 7-15 minute window —
   and reuses a concept the spec already contains.
   - If the owner prefers a purely structural alternative, **Q2** is the same idea against MTF structure.
   - **Q3** is not recommended as the activation rule: on CX-LT1-1 it activates at minute 30, which contradicts "the
     overextension can start around seven to 15 minutes in".
3. **Duration** (`M1H-OE-01`, 20 minutes) should then be measured from `extension_activation_time`, which is what the
   "13 minute delay … it would only be like a seven minute extension" passage describes. On the three examples this
   gives 31 / 30 / 27 minutes — all still ≥ 20.
4. **D8 stays `HOUR_OPEN`** as the canonical hourly reference for stop and target construction (D27 §14): activation
   changes what the *extension tests* measure, not the hour's reference price.

**Remaining uncertainty:** whether activation should also expire (nothing supports minute 15 as an expiry), and whether
a hour whose push never qualifies should be `NO_EXTENSION` rather than failing `M1H-OE-01` — both are recorded as open.
