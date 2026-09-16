# OQ-50 Evidence Review: when must the previous-15m take be satisfied, and what is Q?

**Doc:** CBR-EVD-OQ50 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D33 §7-9
**Status:** FOR OWNER DECISION. PC3 unchanged; no rule altered; no parity case re-run; no P&L or outcome read.
Measurements: `reports/oq48-independent-examples.md`, `reports/phase13c-evaluation-instant.md`.

---

## 1. The question

`M1H-6A-2-PREV-15M-BROKEN-BY-Q` requires the current 15m candle **Q** to have taken the previous completed candle
**Q−1**'s high (for a sell setup) or low (for a buy). PC3 evaluates it — and `M1H-6A-3-NEW-EXTREME-IN-Q`,
`M1H-LOC-*` and `M1H-OE-01` — at the instant the lower-timeframe type 3 **arms**. Candidate evaluation points:

A. before the type 3 arms (PC3 today) · B. by the type-3 sweep · C. by the final 5-second shift · D. by entry
activation · E. some other evidence-backed event.

## 2. Level-1 evidence

| Id | Source · time | Verbatim | Bearing |
|---|---|---|---|
| E1H-003 (slide) | V1H-defining_a_good_extension 00:00:38 | "1. HVCS, 4+ mins **2. Goes beyond prev LTF/MTF HIGH** 3. After 15m open, PA create wick/pushes a bit more **4. HILO beyond structure, entry on BOS of HILO**" | the take is step 2 of a five-step sequence that ends at the **entry**. Every step is a precondition of the entry, not of anything earlier |
| E1H-034 | V1H-seconds_shift_1m_hilo_hvcs 00:01:19 | "you want **this current 15 minute candle to push and take out the previous high** … and then **around the halfway point of that**, you want a second shift or high low entry set up and to take that sort of trade" | the take belongs to the *current* candle, and the entry comes **after** it, around that candle's midpoint |
| E1H-017 | V1H-where_aoi_er_oe 00:08:08 | "external just means you're beyond structure … the best of reversals is when you take out the previous low on the 15 minute candle" | the take is a quality condition of the *reversal*, i.e. of the trade |
| E1H-023 | V1H-1m_fractal_shift 00:03:23 | the Q−1-closed-in-trade-direction exception (already implemented, D19-4) | unchanged here |

**The decisive structural point.** The course vocabulary has no concept corresponding to "the type 3 arms". The arm is
an internal engine event: the moment a sweep-and-pending-break pair is created. Canon therefore **cannot** be
requiring the take to be complete before it. Every Level-1 statement ties the take to the entry candle and to the
entry itself.

## 3. Independent examples (D33 §8)

| Field | HX-1 (2025-10-23) | HX-2 (2025-10-29) |
|---|---|---|
| Q−1 window | 05:00-05:15 | 02:15-02:30 |
| Q window | 05:15-05:30 | 02:30-02:45 |
| Q−1 reference (low, buy setups) | 4 088.69 | 3 962.30 |
| Q takes it at | **05:20** | **02:30** |
| Type-3 sweep time | UNKNOWN (requires a candidate run, not authorized) | UNKNOWN |
| Type-3 arm time | UNKNOWN (same) | UNKNOWN |
| 5s / HILO shift | ≈ 05:27 (from the frame) | ≈ 02:37 (from the frame) |
| Entry time | UNKNOWN (not stated in the lesson) | UNKNOWN |
| Valid / rejected | valid | valid |

In both independent examples the take happens **early inside Q and before the shift**. They confirm the ordering
*take → shift → entry*, and they confirm the take and the entry live in the **same** 15m candle. They do **not**
discriminate A from C, because neither has a take that occurs after an arm. No Level-1 example in the corpus does.

CX-LT3-2 is the only known case where the two readings diverge (arm 01:34:45, take 01:35, extreme 01:37, shift
01:39:40), and per D33 §7 it must not drive the rule. It is reported, not used.

## 4. Recommendation — evaluation point

**Recommended: C, by the final 5-second structure shift**, classified **CANON_CORRECTION**.

The recommendation rests on §2, not on any example:

1. Every Level-1 statement makes the take a precondition of the *entry* ("entry on BOS of HILO" comes after "goes
   beyond prev LTF/MTF HIGH"; "this current 15 minute candle to push and take out the previous high … and then around
   the halfway point of that, a shift").
2. The type-3 arm has no counterpart in the course, so requiring the take before it imports a constraint canon never
   states.
3. It is the same correction D29-11 already applied to the HVCS rule (H-3), which moved a rule from the decision
   ledger to the trigger ledger without any causality loss: the shift is strictly later than every bar close the test
   reads.

Scope of the recommendation: `M1H-6A-2` and `M1H-6A-3`, which are the two rules the evidence speaks to. `M1H-LOC-*`
and `M1H-OE-01` are **not** included — no Level-1 statement ties the location test or the 20-minute extension
minimum to the entry instant rather than to the setup, and extending the change to them on the strength of one
parity case would be exactly the inference D33 forbids. They stay as they are, and stay listed as open.

## 5. Recommendation — what Q is (D33 §9)

**Recommended: A, the 15m candle containing the final shift**, classified **ASSUMPTION** (deterministic, and it is
also what PC3 already computes at whatever instant it evaluates).

- E1H-034 describes one candle doing both jobs: it "pushes and takes out the previous high", and the shift comes
  "around the halfway point of **that**" candle. Anchoring Q to the shift keeps the take and the entry in the same
  candle, which is the geometry Tom describes.
- Both independent examples satisfy this reading: HX-1 takes Q−1 at 05:20 and shifts at ≈ 05:27, both inside
  05:15-05:30; HX-2 takes Q−1 at 02:30 and shifts at ≈ 02:37, both inside 02:30-02:45.
- JM-2025-10-17 is **not** used here (D33 §9), and no other evidence bears on the boundary case.

**The boundary case, stated honestly.** If a shift lands very early in a new 15m candle, Q moves with it and the take
that occurred in the previous candle no longer counts. Under E1H-034's geometry that setup is *already* atypical —
the entry is supposed to be around the candle's midpoint, not in its first minutes — so the behaviour is
self-consistent rather than a defect. The existing `timing30_state` diagnostic (D19-5) records where in the candle a
shift lands and can measure how often this occurs; it does not reject signals, and no rejection is proposed.

## 6. What stays unresolved

- Whether `M1H-LOC-*` and `M1H-OE-01` should also move to the trigger instant (no Level-1 evidence either way).
- Whether the take may be satisfied by Q−1 closing in the trade direction *and* Q never taking the level, for a
  shift that lands in a later candle — the existing D19-4 exception interacts with §5 and has not been re-examined.
- The boundary frequency: how often a shift lands in the first minutes of a new 15m candle, which is measurable from
  existing diagnostics but requires a run that is not authorized now.
