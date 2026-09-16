# OQ-48 Evidence Review: HVCS duration and counting semantics

**Doc:** CBR-EVD-OQ48 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D32 §3-7
**Status:** FOR OWNER DECISION. PC3 is unchanged and frozen. Nothing here selects an interpretation, and no
interpretation was chosen because it recovers examples. No trade outcomes, fills or P&L were read.

Companion artefacts: `reports/phase13c-hvcs-reconstruction.md` (minute-by-minute, D32 §5) ·
`reports/phase13c-evaluation-instant.md` (decision vs shift, D32 §5/§8).

---

## 1. What PC3 requires today

`M1H-6A-1-HVCS-INTO-SHIFT` passes when `hvcs_structural()` returns a run of **≥ 4** conforming 1-minute candles
**ending at the extension-extreme bar as known at the 5s shift** (D29-11 / H-3). A candle conforms when it respects the
relevant side (DOWN: `high ≤ previous high`; UP: `low ≥ previous low`). The first candle of the sequence is the
reference and is **not** counted. The run stops at the **first** candle that breaks the side.

Measured on the three course positives: **3, 2 and 0** conforming minutes → the rule rejects all three (Phase 13C).

## 2. Evidence

| Id | Level | Source · time | Verbatim | What it fixes |
|---|---|---|---|---|
| E1H-003 (slide) | L1 | V1H-defining_a_good_extension · 00:00:38 | "HVCS->HILO **1. HVCS, 4+ mins** 2. Goes beyond prev LTF/MTF HIGH **3. After 15m open, PA create wick/pushes a bit more** 4. HILO beyond structure, entry on BOS of HILO 5. Target 50% of prev LTF move" | the **order**: the 4+ minute HVCS and the take of the previous extreme come *before* the new 15m candle opens; the wick/extra push comes *after* it; the entry comes last |
| E1H-034 | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:01:19 | "You want a high volume counter sequence. **You want volume to push immediately for at least four minutes or more**, and you want it to go beyond the previous low timeframe, middle timeframe high. I would say the previous 15 minute candle high or low … **and then around the halfway point of that, you want a second shift or high low entry**" | the only spoken number (4 minutes), the direction of travel (beyond the previous 15m extreme), and the entry's position (halfway through the 15m candle) |
| — | L1 | V1H-seconds_shift_1m_hilo_hvcs · 00:02:06 | "i want this sort of high volume candle sequence so you see **we're respecting all the all the highs** we're just consistently moving bearish" | conformity = respecting the side (already adopted as H-1) |
| EP2-005 | L1 | VP2-1m_hilo_entries · 00:05:13 | "an HVCS … we're moving, **respecting lows and highs**. We're kind of trending on low timeframes. And this would be a low volume candle sequence, an LVCS" | same definition; LVCS is the contrast case |
| — | L1 | VP2-1m_hilo_entries · 00:04:49 | "it doesn't have to be one or two candles it can be multiple candles so like **this previous candle didn't do anything but it's more of an indecision candle**" | indecision candles sit **inside** a valid sequence |
| E1H-018 | L1 | V1H-defining_a_good_extension · 00:01:14 | "we want it to overextend **for around 20 minutes** … it's around 20 to 30 minutes of price action extending in one direction without a pullback … if it's 15 minute candle behavior that's **around seven and a half minutes**, 40-50% of that kind of behavior pushing" | Tom's durations elsewhere are **elapsed time measured from a candle's open**, expressed as a fraction of that candle — not a count of qualifying candles |
| E1H-024 | L1 | V1H-candle_behavior_timing · 00:01:17 | reversals ":22-:52, better :30-:45, best ~:37" | the entry instant, used below to test whether a reading places the entry where Tom places it |

**Nothing in the corpus states** where the counted run starts or ends, whether the first candle counts, or whether the
sequence must remain unbroken until the shift. Those are the gaps below.

## 3. The ten questions (D32 §4)

| | Question | Evidence answer |
|---|---|---|
| **A** | What starts the clock? | **Not stated.** The slide places the HVCS before the new 15m candle opens and E1H-034 says "push **immediately**", which implies the start of a directional push, but no source names the bar that starts it. |
| **B** | What ends the clock? | **Not stated.** The rule's own name ("into the shift") and the slide's ordering both point at the entry region; PC3 instead ends it at the extension-extreme bar. Three readings survive (H-A, H-D, H-F in §4). |
| **C** | Does the first qualifying minute count as minute 1? | **Not stated.** "4+ mins" is a duration, and Tom's other durations (E1H-018) are elapsed time from a candle open, which would count the first minute. PC3 does not count it. |
| **D** | Does the minute containing the extension extreme count? | **Yes, permissively** — D29's H-2 ruling already allows the run to end on that bar. No source requires it to end there. |
| **E** | Does the minute containing the 5s shift count? | **Not stated.** It is never closed at the decision instant, so PC3 could not count it without breaking causality; a completed-bar reading excludes it. |
| **F** | Count of candles, wall-clock, tradable time, or push-to-shift? | **Not resolvable.** "four minutes" (E1H-034) and "4+ mins" (E1H-003) are both time; E1H-018 measures analogous durations as elapsed time from a candle open. PC3 counts candles. On 1m bars with no gaps the two coincide **only** if the first candle is counted. |
| **G** | May an indecision candle count? | **Yes** (VP2-1m_hilo_entries 00:04:49). PC3 already allows this (H-1). |
| **H** | May an opposing-close candle count if structure is respected? | **Yes** (same quote plus E1H-SS-0206; this is the H-1 correction D29 approved). PC3 allows it. |
| **I** | Must the sequence stay continuous to the shift? | **Not stated.** PC2 tolerated `hvcs.max_violations = 1` broken candle inside the run; PC3 tolerates none (see §5). Neither number appears in any source. |
| **J** | Is "4 minutes" CANON for CBR1H, CBR15, or both? | **CBR1H only.** Both sources (E1H-003, E1H-034) are hourly-model lessons. CBR15's `oe.min_minutes = 4` (E15-021/E15-022) is the 15-minute model's **overextension** minimum — a different quantity that happens to share the number. `config/strategy.yaml` has no `hvcs` block under CBR15. |

## 4. Counting comparison (D32 §6) — diagnostic, nothing selected

Full derivation and per-bar membership: `reports/phase13c-hvcs-reconstruction.md`.

| Reading | What it counts | CX-LT1-1 | CX-TE1-1 | CX-LT3-2 | ≥ 4 |
|---|---|---|---|---|---|
| **H-A** (PC3 today) | conforming candles ending at the extension-extreme bar; reference not counted | 3 | 2 | 0 | 0/3 |
| **H-B** | H-A counting the first candle | 4 | 3 | 0 | 1/3 |
| **H-C** | elapsed minutes, first H-A candle open → 5s shift | 3.58 | 2.92 | 0 | 0/3 |
| **H-D** | conforming candles ending at the last bar closed before the shift | 3 | 2 | 1 | 0/3 |
| **H-E** | H-D counting the first candle | 4 | 3 | 2 | 1/3 |
| **H-F** | conforming candles ending at the last bar before the entry 15m candle opens (the slide's order) | 0 | 1 | 1 | 0/3 |
| **H-G** | H-A with PC2's `max_violations = 1` restored | 6 | 4 | 0 | 2/3 |
| **H-H** | H-D with PC2's `max_violations = 1` restored | 6 | 4 | 4 | 3/3 |

**No single counting convention explains the failure.** H-B and H-E (the off-by-one readings) recover at most one of
the three. The only reading that recovers all three, H-H, differs from PC3 on **two** axes at once — the anchor *and*
the violation tolerance — and one of those two is not a counting question at all. H-H is reported because the
comparison requires it, **not** because it passes; it is not recommended here.

## 5. A separate, concrete finding: PC3 silently dropped `max_violations`

PC2's `hvcs()` (`src/cbr/structure/shifts.py:179`) allowed up to `hvcs.max_violations = 1` non-conforming candle
inside the run. PC3's `hvcs_structural()` (`src/cbr/structure/shifts_pc3.py:136`) takes no such parameter and breaks at
the first violation.

- The parameter still exists, is still loaded (`params.py`), and is still labelled `ASSUMPTION` (OQ-08) in
  `config/strategy.yaml`. It is simply never passed to the PC3 function.
- The PC3 spec record (`CBR1H_BASELINE_V1-PC3.yaml`, change H-1) describes the change as "structural respect and
  progression; indecision candles allowed; no maximum count" and records the PC2 baseline as "(max 1 violation)".
  **D29-10 ruled on the close-direction requirement only.** Removing the tolerance was not proposed, ruled on or
  recorded as a change.
- Direction of the effect: the D29 change was authorized as a *loosening* (indecision candles allowed) but, on this
  axis, PC3 is **stricter** than the PC2 it replaced. On CX-LT1-1 the run grows 3 → 6 when the tolerance is restored.

This is an implementation deviation from PC3's own spec record, independent of every question in §3.

## 6. Classification (D32 §7)

Two separable defects, so two classifications:

| Finding | Classification | Why |
|---|---|---|
| **Duration / counting semantics** (the questions in §3) | **UNRESOLVED_SPEC_AMBIGUITY** | Seven of the ten questions have no answer in the corpus. The one number that is CANON (4 minutes) is not accompanied by a start, an end or a counting convention, and no evidence-supported convention recovers the examples (§4). It is **not** IMPLEMENTATION_OFF_BY_ONE: the inclusive readings recover 1/3. It is **not** CURRENT_IMPLEMENTATION_SUPPORTED: nothing in the corpus anchors the run at the extension extreme. It is **not** CANON_INTERPRETATION_ERROR on the evidence available, because canon does not state the convention PC3 is alleged to have misread. |
| **Dropped `max_violations` tolerance** | **IMPLEMENTATION_FIX candidate** (a deviation from the recorded spec, not from canon) | The parameter is an approved ASSUMPTION that PC3 stopped applying without a ruling. Restoring it returns PC3 to its authorized behaviour; it does not by itself resolve §3. |

## 7. What would resolve the ambiguity

Owner review of, in order: (1) whether the HVCS run is anchored at the extension extreme, at the shift, or before the
entry 15m candle opens (§3 B); (2) whether "4+ mins" counts the first candle (§3 C); (3) whether `max_violations`
should be restored as the ASSUMPTION it is recorded to be (§5). Each is a separate decision, and the evidence here
supports none of them by itself. No change is proposed in this document.
