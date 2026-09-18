# D36 — CBR-RUN-013D-1 accepted as FAIL; final source-contradiction review and decision package

**Doc:** CBR-DEC-036 · **Date:** 2026-09-18 · **Status:** decision package returned for owner review
**Scope:** source review only. PC4 frozen and unmodified · no PC5 · no Phase 13 rerun · no Phase 14 · no backtest ·
no optimization · no P&L or trade outcomes · no Astra × Fable review. No rule, threshold, anchor or parameter was
changed, and nothing was tuned toward CX-LT3-2 (D36 §2).

Companion evidence: `docs/decisions/cx-lt3-2-source-review.md`.

---

## 1. PC4 progress, recorded (D36 §1)

PC4 materially improved fidelity. It produces fully eligible **9/9 STRICT** signals on **CX-LT1-1** and
**CX-TE1-1**, with trigger timing approximately matching Tom (01:39:35 vs ~01:39:15; 04:38:55 inside the stated
04:37-04:39). It preserves the negative control: **CX-LT3-1 → NO_ELIGIBLE_CANONICAL_SIGNAL**.

On **CX-LT3-2** PC4 still reproduces model family, direction, extension direction, extension activation, location,
the previous-15m event, the 5-second type-3 shift and the approximate trigger time (01:39:40 vs ~01:40:00), then
rejects the candidate on:

- **A.** HVCS duration / anchor semantics — 0 conforming minutes at the extension-extreme anchor;
- **B.** `M1H-OE-01` — 16 minutes at the decision instant against a canonical 20.

This is a source/specification question, not a geometry problem.

## 2. The eight returned items (D36 §10)

### 2.1 CX-LT3-2 classification

**DISCRETIONARY_EXCEPTION.** Tom flags the condition as one he is "not the biggest fan of … for taking reversals
in", calls it "not the best condition", accepts it with "I think this is good enough though", and expects it "could
very easily lose". He never names an HVCS, never cites a duration, never calls it textbook, and the trade carries no
journal-table row — while the two examples PC4 reproduces cleanly are labelled "textbook" (Oct 24) and "new"
(Oct 21) in his own journal. Full reasoning, including why the runner-up label was rejected:
`cx-lt3-2-source-review.md` §5.

### 2.2 The 20-minute rule

**GUIDANCE, not a hard requirement.** Every Level-1 statement is hedged — "around 20 minutes", "around 20 to 30
minutes", "40 to 50 percent of that candle", "around 2 15-minute intervals" — and one L1 instance explicitly calls
an extension of **"almost 20 minutes"** a **"really nice overextension"**, which a hard `≥ 20` floor would reject.
The corpus never says "at least", "minimum" or "must". PC4 implements it as a hard floor labelled CANON: the number
is sourced, the hardness is not. This conclusion does not rest on CX-LT3-2.

### 2.3 Independent duration examples

Measured from bars only, hour open → extension extreme at the stated entry:

| Case | From hour open | From Q1 activation | Tom's assessment |
|---|---|---|---|
| CX-LT1-1 | 38 min | 31 min | journal "new" |
| CX-TE1-1 | 37 min | 30 min | journal **"textbook"** |
| CX-LT3-2 | 37 min | 27 min (**16 at the decision instant** — what PC4 scores) | "good enough though" |
| HX-1 | 26 min | **5 min** | valid entry in the HVCS-defining lesson |
| HX-2 | 36 min | 26 min | "the high volume counter sequence into a high low entry" |

**No dated example measures under 20 minutes from the hour open.** Sub-20 figures appear only under PC4's
conventions — the decision-instant evaluation (LT3-2: 16) and the activation anchor (HX-1: 5) — and Tom accepts both
setups. The practical constraint is *when and whence* duration is measured, not the number.

### 2.4 HVCS contradiction

**No direct source contradiction exists.** Tom never calls CX-LT3-2's sequence an HVCS; the word appears nowhere in
the video. The requirement is **inferred by us** from variant A, which makes HVCS mandatory for every CBR1H entry.
PC4 measuring 0 minutes therefore contradicts no statement in the source. Recorded, and the anchor is **not**
changed.

### 2.5 JM-2025-10-16 diagnosis

**A genuine CBR1H classifier limitation, and it is about the evaluation instant — not k, not taxonomy, not the
journal.**

The condition is classified **once, at the hour open**, and fixed for the whole hour. At 00:00 only **2** swing legs
are confirmed, so the hour is `UNDEFINED` and `M1H-COND-01/-02` block all five candidates. By **00:41** — the
journal's recorded time, and the minute of the engine's own SELL candidate shift at 00:41:20 — **4** legs are
confirmed, which clears `min_legs = 3`. The two swings involved formed before the hour and confirmed inside it
(H 4216.08 formed 23:00, confirmed 00:05; L 4204.96 formed 00:00, confirmed 00:20).

So: **not** an OQ-01 detection failure (k = 3 finds the legs), **not** a taxonomy issue (TRR CT is implemented as
`TRENDING_RANGE` + `M1H-LOC-03`), **not** insufficient journal evidence (the hour, direction and CB bucket are all
corroborated by price action — the hour tops at 4227.32 at 00:40 and reverses). It implicates the hour-open
classification convention, interacting with swing-confirmation lag (OQ-01) and `min_legs` (OQ-02, an ASSUMPTION).
`k = 3` is not changed from this case (D36 §8). Recorded as **OQ-52**.

### 2.6 Is any PC5 change independently justified?

**No — not on evidence that uniquely determines a mechanization.**

Three candidates were examined and each is declined:

| Candidate | Why it is declined |
|---|---|
| Soften the 20-minute floor | The evidence that it is guidance is real and independent (§2.2), but mechanizing "around 20" requires inventing a tolerance. No source states one. Choosing one now, with CX-LT3-2 at 16-27 minutes in view, would be tuning |
| Evaluate `M1H-OE-01` at the shift | This is the D33 **F-4** proposal I already **withdrew**, on the grounds that no Level-1 evidence supports moving it and it was proposed from CX-LT3-2 alone. Nothing new has appeared since. Resurrecting it now, because CX-LT3-2 failed on exactly that rule, is precisely what D36 §2 forbids |
| Move the HVCS anchor | §2.4 shows there is no source contradiction to fix, and D34 §3 already refused this reading because it produces 3/3 |

The one genuinely new finding — that the **condition is classified once at the hour open** (§2.5) — is a real
limitation, but it comes from a single case the ruling explicitly says must not drive PC5, and it belongs to the
same unresolved evaluation-instant family as OQ-50.

### 2.7 Recommendation: **PATH B**

**PC4 is sufficient with documented source ambiguity.**

PC4 reproduces the stable core method: it produces complete, eligible, correctly-timed signals on both course
examples Tom's own journal labels, refuses the setup he explicitly rejected, and fails only on an example the source
itself frames as a marginal judgement call. The two remaining blockers are assumption-dependent, both are already
documented as open questions, and neither can be resolved without an arbitrary choice.

Path A is not available: no independent evidence shows PC4 mechanizing a canonical rule incorrectly in a way that
determines the fix. Path C overstates the problem: the method is *not* globally under-specified — PC4 mechanizes it
deterministically and it now reproduces the textbook cases — the under-specification is localized to two named
questions (OQ-48's anchor, OQ-50/OQ-52's evaluation instants).

**Path B requires a NEW OWNER DECISION redefining the Phase 13 completion criterion.** That decision is yours; this
document does not make it and must not be read as making it. Concretely it would mean deciding that Phase 13
completes when a candidate reproduces the *textbook* examples and the negative control, with discretionary examples
and assumption-dependent rules documented rather than mechanized.

### 2.8 Exact risks of the recommendation

| # | Risk | Mitigation available to the owner |
|---|---|---|
| 1 | **Moving the goalposts.** The completion criterion would change after three failures. Even with sound reasons, the sequence looks like redefining success to reach it | Require that the new criterion be written and frozen **before** any further scoring, and that it name CX-LT3-2 as excluded on its own stated grounds rather than on PC4's result |
| 2 | **The discretionary label may be too convenient.** CX-LT3-2 is the only case PC4 fails, and it is the case being reclassified. The evidence is Tom's own words, but the motive is visible | The classification rests only on source quotations, and the runner-up label is recorded. An independent reviewer can check it against the transcript in minutes |
| 3 | **Sample size.** Path B would declare sufficiency on **two** clean entry-level examples plus one negative control. That is thin | Treat any Phase 14A result as provisional until more dated examples are extracted; the HX-1/HX-2 examples are already located but are evidence-tainted for scoring |
| 4 | **Two open assumptions remain inside the engine.** The HVCS anchor and the OE-01/condition evaluation instants still affect signal membership, so baseline results will inherit them | Carry both into Phase 14A explicitly as declared model risk, and re-test them when new evidence appears rather than during the baseline |
| 5 | **The hour-open condition convention (OQ-52) is now known to reject a setup Tom took.** It will suppress signals elsewhere too | Quantify its frequency during baseline testing as a diagnostic, without changing it |
| 6 | **Path B forecloses nothing, but delays.** If a future example shows PC4 mechanizing a canonical rule wrongly, PC5 becomes justified after all and the baseline work would need revisiting | Keep OQ-48, OQ-50 and OQ-52 open, and keep `HVCS_TO_SHIFT` and the decision/trigger diagnostics recorded in every run |

## 3. Stop

Decision package returned. PC4 unchanged and frozen, no PC5, no new scored run, Phase 14 not started.
