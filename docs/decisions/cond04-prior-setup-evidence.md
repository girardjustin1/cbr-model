# M1H-COND-04 Evidence Review: The Prior-Setup Requirement

**Doc:** CBR-EVD-C04 · **Version:** v1.0 · **Date:** 2026-09-15 · **Ruling:** D26 §7 · **Status:** FOR OWNER DECISION
PC2 unchanged and frozen. Extends `docs/decisions/oq36-prior-setup-evidence.md` (CBR-EVD-036, D19-1 ruling C′) with the
questions D26 §7 asks. Quotes verified mechanically (normalizer of `tests/test_evidence.py`); no outcomes, no P&L.

---

## 1. What PC2 requires today

`M1H-COND-04`: at least `prior.min_count = 1` setup **formed** (`raw_setup_armed`) with decision time in
`[H.t0 − 10 h, H.t0)`. `raw_setup_armed` means a candidate passed **every** setup rule except the recursive prior-setup
rule itself (D20-1). Lookback 10 h and count 1 are ASSUMPTIONS (OQ-05, OQ-36); the rule's object (a raw CBR1H
candidate) is an implementation choice, not a course object.

## 2. The measured problem: the rule is currently unsatisfiable

Diagnostic over the three stored course windows (STRUCTURE bars, variant A, no outcomes):

| Window | Hours evaluated | Candidates | Raw setups formed | ARMED |
|---|---|---|---|---|
| 2025-10-20 → 21 | 19 | 182 | **0** | 0 |
| 2025-10-23 → 24 | 22 | 187 | **0** | 0 |
| 2025-11-07 + 10 | 19 | 167 | **0** | 0 |
| **Total** | **60** | **536** | **0** | **0** |

`M1H-COND-04` failed on **536 of 536** candidates — the most frequent failure in the engine. Because its object is a
`raw_setup_armed` candidate, the rule inherits the strictness of every other rule: while `M1H-OE-02` (443 failures) and
`M1H-6A-1` (469) fail this often, no setup can ever *form*, so the prior-setup counter can never leave zero. The rule
is not discriminating between good and bad hours; it is switched off in the closed position.

This is a **structural interaction in the implementation**, not evidence about what Tom teaches.

## 3. Evidence on Tom's own rule

### 3.1 Is a prior setup required at all?

| Level | Source · time | Verbatim | Reading |
|---|---|---|---|
| L1 slide (E15-049) | V15-defining_ltf_range · 00:07:52 | "Zero setups in the last hour: bad condition. Sit out." | the only hard clause anywhere, and it is **CBR15's**, not the hourly model's |
| L1 | V15-defining_ltf_range · 00:07:00 | "for the past five ten plus hours you know is there enough frequency that there's been previous hourly cbrs" | hourly version is about **frequency**, phrased as a question, with no sit-out clause |
| L1 | V15-overview_methodology · 00:04:26 | "five ten plus hours and see it have i had a previous setup a previous cbr setup" | same |
| L1 (E15-009) | V15-defining_ltf_range · 00:11:05 | "want you know two one two three clean setups prior if there's no setups is probably a bad condition" | "**probably**" |
| **L2** | V1H-mastering_entry_timing… · 00:33:42 | "so if i didn't have a cpr in previous 45 hours you would sit out completely as the condition wouldn't be there essentially" | the only **hourly** sit-out statement, and L2 |
| **L2** | V1H-mastering_entry_timing… · 00:28:39 | "the easiest way to tell if a condition is good for a CBR is that did you have a previous CBR in the previous couple of hours" | a **diagnostic of condition**, not a gate |
| **L2** | V1H-mastering_entry_timing… · 01:15:31 | "in the past 45 hours did you have a previous cbr if yes probably a little bit higher quality" | explicitly **quality**, not permission |
| **L2** (LR-28) | V1H-in_depth_backtesting… · 01:19:10 | "so one cbr goes into another so even this is like kind of low quality of a an entry like the condition is quite nice and since you have a a previous cbr i probably still could have taken this trade" | a prior CBR **upgrades a weak entry**; the reverse of a gate |
| **L2** (LR-48) | V1H-mastering_entry_timing… · 00:33:42 (same passage) | "kind of a new sort of mindset I guess like so I don't have data to back it up" | Tom flags the hourly rule as untested |

**Finding.** For the hourly model, L1 never states a hard gate. The gate language is CBR15's slide (one-hour window)
and one L2 sentence that Tom immediately qualifies as unproven. L2 more often treats a prior CBR as a **quality boost**.

### 3.2 What type of prior setup?

| Level | Source · time | Verbatim | Reading |
|---|---|---|---|
| L1 | V15-defining_ltf_range · 00:07:19 | "you just want to see the type of cbr that you're going for happen previously" | **same model size** (strong) |
| L1 (visual) | V15-defining_ltf_range · 00:11:46-00:12:36 | Tom points at hourly candles with extensions and reversal wicks; a "fake out … pretty low volume" one is rejected | the object is **candle behaviour**, not a triggered signal |

No L1 or L2 source requires the prior setup to be in the **same direction**, to have **triggered an entry**, or to have
reached a target. The direction question is not discussed anywhere; searches for direction-qualified prior setups
returned nothing relevant.

### 3.3 What lookback?

| Level | Source | Value |
|---|---|---|
| L1 | V15-defining_ltf_range · 00:07:00; V15-overview_methodology · 00:04:26 | "five ten plus hours" (hourly) |
| L1 slide | E15-049 | 1.5-2 h count and a 1-hour zero clause (**CBR15**) |
| L2 | V1H-mastering_entry_timing… · 00:33:42, 01:15:31 | "45 hours" (Whisper for "4-5 hours") |
| PC2 | `prior.lookback_hours` | 10 h (ASSUMPTION, research range 5 / 10) |

**Finding.** 5-10+ h is the L1 range; PC2's 10 h sits at its top. L2 suggests 4-5 h. Nothing supports a precise number;
"plus" is open-ended.

### 3.4 Hard gate or descriptive context?

L1 phrases it as a question to ask about the condition ("is there enough frequency", "have i had a previous setup"),
inside lessons on **defining the range/condition**. The single hard formulation is CBR15's slide. L2 uses both
framings, with the gate framing self-flagged as unevidenced and the quality framing used repeatedly in live review.

## 4. Answers to D26 §7

| Question | Answer | Strength |
|---|---|---|
| A prior setup at all? | For CBR1H, **not established as a hard gate** by L1 | moderate |
| What type? | A **clean CBR of the same model size** (candle behaviour: extension + reversal) | moderate-strong |
| Same direction? | **No evidence either way**; never mentioned | none |
| Same model? | **Yes**, same size/model ("the type of cbr that you're going for") | strong |
| Actual lookback? | L1 "five ten plus hours"; L2 "4-5"; CBR15 uses 1.5-2 h with a 1 h zero clause | moderate |
| 5 h / 10 h / range-dependent / conceptual? | **Conceptual**, expressed as frequency over a window, not a precise count | moderate |
| Hard gate or descriptive? | L1: **descriptive condition input**. L2: mostly **quality**, once a gate (self-qualified) | moderate |

## 5. Findings

1. PC2's implementation makes the rule **vacuously blocking** (0 raw setups in 60 hours, §2). Whatever the owner rules
   about Tom's meaning, this behaviour is an implementation defect: a rule whose object can never exist.
2. The rule's **object** is wrong relative to the evidence. Tom counts **prior hourly candles that behaved as CBRs**
   (extension + reversal). PC2 counts prior *engine candidates that passed every other engine rule*, which is a
   recursive, far stricter object.
3. The **hourly hard gate is not supported by L1**. CBR-EVD-036 already concluded this; the run now shows what it costs.
4. The **10-hour lookback** is at the top of the L1 range and was never evidence-led.

## 6. Options for the owner (not selected here)

| Id | Option | Classification if adopted |
|---|---|---|
| C04-1 | Keep the rule, change its object to prior **hourly candles with CBR candle behaviour** (extension per M1H-OE + reversal), independent of engine rules | CANON_CORRECTION (object) + ASSUMPTION_CHANGE (reversal geometry) |
| C04-2 | Demote the rule to a **diagnostic / quality field**, not a gate (matches L1 for CBR1H) | CANON_CORRECTION |
| C04-3 | Keep as a gate but fix the recursion so a formed setup doesn't require every other rule | IMPLEMENTATION_FIX |
| C04-4 | Change the lookback to the L1 range (5 h or "5-10+" as a declared assumption) | ASSUMPTION_CHANGE |
| C04-5 | No change | NO_CHANGE — but then the rule stays unsatisfiable, and Phase 13 cannot pass |

Do not choose C04-2 merely because it unblocks the examples; §3 is the reason to consider it, §2 is the reason the
current form cannot stand either way.
