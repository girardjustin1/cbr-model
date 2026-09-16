# OQ-09: Where Does the Type-3 Reversal Timer Start?

**Doc:** CBR-EVD-009R · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §6 (from D27) · **Status:** FOR OWNER DECISION
PC2 frozen. Chosen on evidence and causal reasoning, **not on fixture pass rate** (D27 §6). Quotes verified mechanically.

---

## 1. The question

`primitives.t3.max_reversal_minutes` (S5 = 3 min, ASSUMPTION, research range 2 / 3 / 5) bounds how long after the sweep
a type 3 may complete. Under re-anchoring the sweep extreme can keep extending, so the timer may run from:

- **A** the first sweep event (the first bar beyond the swept level), or
- **B** the latest update of the sweep extreme.

## 2. Evidence

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| EP1-008 | L1 | VP1-1_4_shifts_type_3_choch · 00:01:47 | "you take out high, then reverse, **immediately reverse**, take out a low" | the clock is on the **reversal after the extreme**, not on the whole excursion |
| EP1-008 | L1 | same · 00:01:04 | "a clear decisive shift of direction with volume" | the decisive move follows the extreme |
| EP1-009 | L1 | same · 00:02:13 | "you just want a clear break of a high you want a clear break of a low … and reverse" | same ordering |
| E1H-029 | L1 | V1H-when_candle_behavior_timing · 00:06:42 | "If the shift happens over a couple minutes, like five minutes, I'll just say it's like a second shift" | a few minutes is the scale of the shift itself |

**No timed example defines the anchor.** The wording "immediately reverse" describes the move *after* the high is
taken; while price is still making new highs, it has not yet reversed, so the reversal cannot have started.

## 3. Reasoning

Under anchor **A**, a sweep that keeps extending consumes its own timer: the pattern expires while price is still
making the extreme it will reverse from. That contradicts "take out high **then** reverse", because the timer would run
during the take-out rather than during the reversal.

Under anchor **B**, the clock starts when price stops extending, i.e. exactly when the reversal can begin.

## 4. Effect on the examples (reported, not the basis of the choice)

| Example | First sweep bar | Latest sweep extreme | Break | Elapsed under A | Elapsed under B | 3-minute limit |
|---|---|---|---|---|---|---|
| CX-LT1-1 | 01:38:35 | 01:38:50 | 01:39:35 | 60 s | 45 s | both pass |
| CX-TE1-1 | 04:36:35 | 04:37:05 | 04:38:55 | 140 s | 110 s | both pass |
| CX-LT3-2 | 01:34:40 | 01:37:35 | 01:39:40 | **300 s → expires** | 125 s | **only B passes** |

CX-LT3-2 is decided by this choice, which is why it must be settled on wording rather than on outcome.

## 5. Effect on the existing unit fixtures

`test_type3_rejects_slow_reversal` (a 2-minute gap with a 1-minute limit) still yields TIMEOUT under anchor B, because
in that fixture price does not extend after the sweep bar. The fixture is **anchor-agnostic**, so it cannot decide the
question either — and was not used to.

## 6. Conclusion

**Recommend anchor B (latest update of the sweep extreme).** It follows the Level-1 sequencing ("take out high, then
reverse, immediately reverse"): the reversal clock starts when the extension stops.

If the owner judges the wording insufficient, the **conservative baseline** is anchor **A** with the timer measured from
the *last* bar that made a new extreme — which is anchor B by another name — or, strictly conservative, anchor A with a
longer `max_reversal` treated as an ASSUMPTION. The value itself (3 minutes) is unchanged and not proposed for
modification here.

**Classification if adopted: IMPLEMENTATION_FIX** (a definitional clarification of an existing rule, no new parameter).
