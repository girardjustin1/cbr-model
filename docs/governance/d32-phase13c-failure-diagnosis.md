# D32 — CBR-RUN-013C-1 accepted as FAIL; failure-diagnosis package

**Doc:** CBR-DEC-032 · **Date:** 2026-09-16 · **Status:** owner ruling recorded; diagnosis returned for owner review
**Scope:** failure diagnosis only. PC3 is frozen and unmodified, PC4 does not exist, no parity run was repeated, no
backtest, no optimization, no P&L or trade outcome, no Astra × Fable review.

---

## 1. The ruling

The Phase 13C verdict **FAIL** (CBR-RUN-013C-1, CBR-PROT-013C v1.1) is accepted by the owner. PC3 remains frozen at
`7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453`.

## 2. Progress from PC2 to PC3, recorded explicitly (D32 §1)

PC3 materially improved behavioural fidelity. On all three original positive examples it reproduced the model family,
the direction, the extension direction, the extension activation, the underlying 5-second type-3 geometry, and
approximately the demonstrated trigger time:

| Case | Engine 5s shift | Tom's stated entry | Difference |
|---|---|---|---|
| CX-LT1-1 | 01:39:35 | ≈ 01:39:15 | +20 s |
| CX-TE1-1 | 04:38:55 | ≈ 04:37-04:39 | inside the stated interval |
| CX-LT3-2 | 01:39:40 | ≈ 01:40:00 | −20 s |

PC2 produced a D25-P3-equivalent trigger on **0/3**; PC3 produces one on **3/3**. **The Phase 13C FAIL does not mean
the D29 corrections failed.** The failure is downstream of the recovered structural geometry: no candidate carrying
that geometry survives to `ARMED_AT_TRIGGER`.

## 3. Negative control (D32 §2)

`CX-LT3-1` still returns `NO_ELIGIBLE_CANONICAL_SIGNAL`, and no candidate of any kind has a 5s shift in the rejected
window 01:28-01:36. PC3 became more permissive in several structural areas (re-anchoring, whole-extension pullback,
structural HVCS, prior-setup removal) **without** admitting the setup Tom rejected. Nothing is changed on this basis.

## 4. The package (D32 §17)

| | Deliverable | Where |
|---|---|---|
| A | OQ-48 evidence review, questions A-J answered, classification | `docs/decisions/oq48-hvcs-duration-evidence.md` |
| B | Minute-by-minute HVCS reconstruction, three positives | `reports/phase13c-hvcs-reconstruction.md` (+ `.json`) |
| C | Diagnostic counting comparison, eight readings | same report, §"Counting comparison" |
| D | CX-LT3-2 location mismatch diagnosis | `reports/phase13c-cx-lt3-2-location.md` |
| E | OQ-49 reconstruction, three journal cases | `reports/phase13c-journal-reconstruction.md` (+ `.json`) |
| F | Journal model-taxonomy review | `docs/decisions/oq49-journal-generalization.md` §1 |
| G | Whether the hour-level set was validly scoped | same, §5 |
| H | Proposed change classifications | §6 below |
| — | Evaluation-instant comparison (decision vs shift) | `reports/phase13c-evaluation-instant.md` (+ `.json`) |

Diagnostic code: `src/cbr/engine/phase13c_diagnosis.py`, tested with synthetic fixtures in
`tests/engine/test_phase13c_diagnosis.py`. It re-runs the frozen engine read-only and changes nothing.

## 5. What the diagnosis found

**5.1 The single blocking rule on all three positives is `M1H-6A-1-HVCS-INTO-SHIFT`** (3, 2 and 0 conforming minutes
against a CANON minimum of 4). No evidence-supported counting convention explains it: the off-by-one readings recover
at most 1 of 3, and the sequence-order reading (H-F) recovers none. **OQ-48 is classified UNRESOLVED_SPEC_AMBIGUITY**
— seven of the ten D32 §4 questions have no answer anywhere in the corpus.

**5.2 A separate, concrete implementation defect.** PC3's `hvcs_structural()` silently dropped PC2's
`hvcs.max_violations = 1` tolerance. D29-10 ruled only on the close-direction requirement; the tolerance is an
approved ASSUMPTION (OQ-08) that is still configured, still loaded and never applied. On this axis the "loosening"
D29 authorized made PC3 **stricter** than PC2. Restoring it changes the measured runs from 3, 2, 0 to 6, 4, 0.

**5.3 An evaluation-instant pattern across four cases.** PC3 writes extension-derived rules into the ledger at the
instant the type 3 *arms*; canon (E1H-003) lets every step complete before the entry. Evaluating at the 5s shift
instead flips `M1H-6A-2`, `M1H-6A-3` and `M1H-OE-01` from FAIL to PASS on CX-LT3-2 and `M1H-LOC-01` from FAIL to PASS
on JM-2025-10-17. **It is not a clean fix:** on JM-2025-10-17 the same move flips `M1H-6A-2` and `M1H-6A-3` from PASS
to FAIL, because that shift lands 1.6 minutes inside a new 15m candle and `Q` moves with it. Which candle anchors `Q`
is unsettled.

**5.4 The journal set was partly mis-scoped.** JM-2025-10-17 is labelled **IFS**, a middle-timeframe model with no
class in PC2 or PC3 at all; JM-2025-10-29's journal time (minute 14) contradicts its own CB-hour column (37), and its
frozen hour contains no down-extension for a BUY to reverse; only JM-2025-10-16 is cleanly scoped, and it fails at the
MTF condition classifier (2 legs where Tom sees a trending range). **The Phase 13C verdict is not revisited.**

## 6. Proposed change classifications (D32 §17 H)

Nothing below is a change. Each row is a candidate for a future owner ruling, with the classification it would carry.

| Id | Candidate | Classification if adopted | Status |
|---|---|---|---|
| **F-1** | Restore `hvcs.max_violations = 1` in PC3's HVCS run, as PC2 applied it and as the spec record still describes | **IMPLEMENTATION_FIX** | Ready for a ruling: it restores authorized behaviour rather than choosing new behaviour. It does **not** on its own resolve OQ-48 (CX-LT3-2 stays at 0 conforming minutes at the extreme anchor) |
| **F-2** | Anchor the HVCS run at the shift rather than at the extension extreme | **CANON_CORRECTION** if adopted | **Blocked on OQ-48.** No source names the anchor; adopting it now would be selecting the reading that recovers examples |
| **F-3** | Count the first candle of the sequence toward "4+ mins" | **ASSUMPTION_CHANGE** | **Blocked on OQ-48 C/F.** Recovers 1/3 alone; would need its own evidence |
| **F-4** | Evaluate `M1H-LOC-*`, `M1H-6A-2`, `M1H-6A-3`, `M1H-OE-01` at the trigger instant, as D29-11 already did for HVCS | **CANON_CORRECTION** if adopted | **Blocked on the `Q`-anchoring question** raised by JM-2025-10-17 (§5.3). Causally legal either way |
| **F-5** | Remove JM-2025-10-17 from the machine parity set, or re-label it NOT_APPLICABLE, because IFS is outside the implemented model | **PARITY_SET_CORRECTION** | Ready for a ruling once the owner settles whether FS/IFS belong to CBR1H at all |
| **F-6** | Re-derive JM-2025-10-29's hour from the CB-hour column rather than the journal time, or drop the case | **PARITY_SET_CORRECTION** | Needs the owner's reading of the journal columns; no engine run outside the frozen hour was or will be made without authorization |
| **F-7** | JM-2025-10-16's condition disagreement (`k_mtf`, 2 legs vs a trending range) | **NO_CHANGE** for now; feeds existing **OQ-01** | Not a new proposal; the ATR-zigzag `k` is already an open assumption |
| **F-8** | Everything else exercised in Phase 13C — type-3 re-anchoring, extension activation, whole-extension pullback, condition fallback, candidate selection, the negative control | **NO_CHANGE** | They behaved as authorized; nothing in the diagnosis implicates them |

**No PC4 is proposed** (D32 §14): F-5 and F-6 are parity-set questions, F-1 restores recorded behaviour, and F-2/F-3/F-4
are blocked on evidence the corpus does not currently contain.

## 7. Governance decisions recorded

**7.1 Strict vs descriptive reporting (D32 §15).** The two-layer table introduced mid-run is accepted as a reporting
improvement only. It changed no frozen acceptance rule, no scored result and no verdict. **For future runs it must be
pre-declared before execution:** a STRICT layer (eligibility-aware, scored, binding) and a DESCRIPTIVE layer (closest
structural candidate, diagnosis only). A descriptive match may never satisfy strict acceptance. To be written into the
next parity protocol at drafting time, not during a run.

**7.2 Pre-run smoke execution (D32 §16).** The disclosed pre-freeze seven-case execution is accepted for
CBR-RUN-013C-1, because no scored result was retained or used, no strategy change followed, PC3 was unchanged and the
final run was deterministic. **Standing rule from now on: pre-freeze smoke tests use SYNTHETIC fixtures only.** The
full scored parity set must not be executed before the freeze, even without retaining results. This rule is applied
immediately: `tests/engine/test_phase13c_diagnosis.py` is synthetic-only.

## 8. Open questions opened or updated

- **OQ-48** — HVCS duration / counting semantics. `UNRESOLVED_SPEC_AMBIGUITY`, evidence review delivered.
- **OQ-49** — journal generalization and MTF model taxonomy. Evidence review delivered; three sub-questions returned.
- **OQ-01** — ATR-zigzag `k`: JM-2025-10-16 adds a second instance of the classifier disagreeing with Tom's reading.

## 9. Stop

The package is returned for owner review. PC3 is unchanged, PC4 does not exist, no parity run was repeated, and
Phase 14 remains unauthorized.
