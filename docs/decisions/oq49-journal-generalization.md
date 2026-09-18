# OQ-49 Evidence Review: journal-hour generalization and model taxonomy

**Doc:** CBR-EVD-OQ49 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D32 §9-14
**Status:** FOR OWNER DECISION. PC3 unchanged; no rule relaxed; no entry price, stop or outcome column inferred or
read; no engine run outside a frozen hour. Companion: `reports/phase13c-journal-reconstruction.md`.

The 0/3 HOUR_LEVEL result is independently sufficient to fail Phase 13C (D31-8), so each case is analysed on its own
before any conclusion is drawn about the set.

---

## 1. The model taxonomy question first (D32 §13)

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| — | L1 | V1H-mastering_entry_timing… · 00:19:52 | "so you have you know **TR CT, R** you have R and you have **IFS** and you have **FS** … you know **five types of middle time frame models** … the trending range, you're trading counter to the trending range, you're just trading in the normal range, and you're trading an inverse [fractal shift]" | TRR CT / TRR PT / R / FS / IFS are the **middle-timeframe model / condition** taxonomy of the hourly methodology |
| E1H-010 | L1 | V1H-mtf_model_types · 00:03:04 | "fractal shift inverse versus fractal shifts … those are three types of middle time frame models … if it's trending definitely shouldn't be trading" | same taxonomy, collapsed to three families: range, trending range, fractal shift / inverse |
| E1H-011 | L1 | V1H-what_direction_condition · 00:07:13 | "it's an inverse when you're trading the correction so if you're taking a buy here into 50 that's inverse, you're inversing that fractal shift" | **IFS = trade the correction back toward 50% of an MTF impulse** |
| E1H-047 | L1 | V1H-where_aoi_er_oe · 00:10:56 | journal property list: "Correlation \| Condition \| CB Hour \| MS Align \| Shifts \| 5m Interval \| OE LTF HVCS (10-30m) \| Pair \| Account \| Wick \| **Setup** \| AOI \| Entry Relativity \| Session Time \| 15m Intervals" | the journal's own columns; `Condition` and `Setup` are **separate** fields |

**Answer to D32 §13:** these labels are **(A) CBR1H middle-timeframe model labels**, not other strategies — the same
journal table's rows for 2025-10-21 and 2025-10-24 are CX-LT1-1 and CX-TE1-1, both CBR1H course examples. But they are
only **(D) partially mappable**:

| Label | Course meaning | Engine status |
|---|---|---|
| TRR PT | trending range, traded pro-trend | in scope — `TRENDING_RANGE` + `M1H-LOC-02` |
| TRR CT | trending range, traded counter-trend | in scope — `TRENDING_RANGE` + `M1H-LOC-03` |
| R | plain range | in scope — `RANGE` + `M1H-LOC-01` |
| **FS / IFS** | fractal shift / its correction (E1H-011) | **out of scope — no such condition class exists in PC2 or PC3.** `src/cbr/structure/condition.py` emits only `RANGE`, `TRENDING_RANGE`, `TREND`, `UNDEFINED` |

Note a naming collision to avoid: CBR1H **variant B** is called `FRACTAL_1M_S5_SHIFT`, but its "fractal" is the
1-minute type-3 parent structure inside an hour. It is not the MTF fractal-shift model Tom means by FS/IFS.

A second mapping problem: the journal's `Condition` column carries values "Trending", "Volume" and "Ranging".
"Volume" is not a condition in the course taxonomy at all — it describes the extension's character (E1H-018:
"Is it high volume, low volume?"). The frozen mapping M-4 guessed at this by scoring "Trending" against
{TRENDING_RANGE, RANGE} and declaring "Volume" NOT_SCORED. That guess is now visibly under-evidenced.

## 2. JM-2025-10-16 — journal SELL, TRR CT, Trending, CB 37

**Engine hour:** condition **UNDEFINED**, `n_legs = 2` in the 8-hour tradable window from 2025-10-15 15:00; hour rules
failed `M1H-COND-01`, `M1H-COND-02`. Five SELL candidates exist and one reaches a 5s shift at 00:41:20, but the hour
itself is never classifiable, so nothing can arm.

**First divergence: the MTF condition classifier.** The ATR zig-zag (`k_mtf = 3` on 5-minute bars) finds two legs where
Tom records a trending range. `min_legs` is CANON; `k` is the ATR-zigzag ASSUMPTION carried through parity (D30-16,
OQ-01).

**Corroboration that the hour assignment is right:** the hour opens 4209.58, tops at **4227.32 at 00:40**, and closes
4210.55 — an up-extension reversing near minute 40. The journal's local time (11:41 AM UTC+11 = 00:41 UTC) and
CB 37 both land there. So this case is correctly scoped and correctly dated: the disagreement is real and is upstream
of every entry rule.

## 3. JM-2025-10-17 — journal BUY, IFS, Volume, CB 52

**Engine hour:** condition `RANGE` (c_med 0.985, 6 legs), range 4261.51-4379.93. Five BUY candidates with a DOWN
extension activated 01:07. Candidate 3 (decision 01:38:20, shift 01:46:35) fails **only** `M1H-LOC-01`.

**Evaluation-instant detail:** at the decision the extension extreme is 4317.99 (01:33), range position 0.477, so a
BUY fails the ≤ 0.25 location test; at the shift the extreme is 4279.07 (01:44), position 0.148, which passes. But at
the shift instant `M1H-6A-2` and `M1H-6A-3` flip the other way, because 01:46:35 sits inside the *next* 15m candle.
See `reports/phase13c-cx-lt3-2-location.md` §"counter-evidence".

**But the scoping question comes first.** The journal labels this row **IFS** — the inverse-fractal-shift MTF model,
which by E1H-011 is "trade the correction back toward 50%" of an MTF impulse. **PC3 implements no IFS model.** The
engine classified the hour `RANGE` and evaluated it with range rules; whether an IFS hour should produce a CBR1H
range/trending-range setup at all is undetermined. Scoring this hour as a CBR1H parity case tested the engine against
a model it was never built to contain.

**Timing note (not scored):** journal 12:53 PM UTC+11 = 01:53 UTC, consistent with CB 52. The engine's nearest shift
is 01:46:35, minute 46 — inside the frozen M-5 bucket [45, 60) but 6½ minutes before Tom's recorded time.

## 4. JM-2025-10-29 — journal BUY, TRR PT, Trending, CB 37

**Engine hour:** condition `RANGE` (c_med 0.745, 3 legs, direction NONE), range 3944.08-4001.67, extension **UP**
activated 08:07. Six candidates, **all SELL**. A CBR1H trade is always the reversal of the hourly extension, so an
up-extension hour can only produce sells; a BUY is impossible by construction, not by a failed rule.

**First divergence: direction, and it is structural.** Within the frozen hour the low is at the hour open (4000.49 at
08:00) and price rises all hour to 4018.66 at 08:58. There is no down-extension in this hour for a buy to reverse.

**A scoping doubt this raises (reported, not acted on).** The journal's local time 7:14 PM UTC+11 = **08:14 UTC**. For
the two corroborating rows the journal time equals the entry time to the minute (12:39 PM → CX-LT1-1's 01:39:15;
3:38 PM → CX-TE1-1's 04:37-04:39). Here 08:14 is minute 14, which is inconsistent with the same row's CB 37 and with
the canonical :22-:52 window. Either the journal time or the CB-hour column means something different on this row, and
the parity set's hour assignment (08:00 UTC) rests on the time column. That the frozen hour's low sits exactly at its
open is consistent with a down move having ended just before 08:00 — but **no engine run was made on any other hour**
(D32 §12), and no claim is made about what a different hour contains.

## 5. Was the independent hour-level set validly scoped? (D32 §G)

| Case | Correctly a CBR1H case? | Correctly dated? | Fit to score |
|---|---|---|---|
| JM-2025-10-16 | **Yes** (TRR CT maps to TRENDING_RANGE counter-trend) | Yes — price action and CB 37 both match minute 40-41 | **Valid.** Its failure is a genuine engine-vs-Tom disagreement at the condition classifier |
| JM-2025-10-17 | **No** — IFS has no counterpart in PC2 or PC3 | Yes (01:53 UTC, CB 52) | **Invalid as scored.** The engine cannot express the model the row records |
| JM-2025-10-29 | Label maps (TRR PT), but the direction is unreachable in the stated hour | **Doubtful** — the time column (minute 14) and the CB column (37) disagree | **Not safely scorable** until the hour assignment is resolved |

So one of the three hour-level cases was well-scoped, one was not, and one has an unresolved dating question. The
0/3 result stands as the run reported it — **D32 §13 forbids retroactively changing the verdict, and nothing here
does** — but the hour-level set as constructed cannot carry the same evidential weight in a future run.

## 6. What must be settled before these cases are used again (D32 §14)

1. Does an `IFS` / `FS` MTF model belong in a CBR1H parity candidate at all, or is it a separate model (like TRR
   Forever) that the current engine is not meant to reproduce?
2. What does the journal's `Condition` column mean when it reads "Volume", and does it map to any engine field?
3. Is the journal's time column the entry time, the logging time, or neither, and does `CB Hour` or the time column
   determine the hour under test?
4. Should a journal row with no price ever score `direction` as a hard field, given that direction in CBR1H follows
   from the hourly extension the engine computes?

Until 1-3 are answered, **no strategy change may be proposed from a journal-case failure** (D32 §14). The only
journal-derived finding that is ready for owner consideration is JM-2025-10-16's condition-classifier disagreement,
and even that is an input to the existing OQ-01 / `k_mtf` question rather than a new proposal.
