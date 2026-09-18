# D37 — Phase 13 closed as research-sufficient; PC4 promoted; Phase 14A authorized

**Doc:** CBR-DEC-037 · **Date:** 2026-09-18 · **Status:** owner decision recorded
**Phase 13 status:** **RESEARCH-SUFFICIENT WITH DOCUMENTED FIDELITY CONCERNS**

---

## 1. The distinction that must never be collapsed

| | |
|---|---|
| **Parity run** | **FAIL** under the frozen D35 acceptance criteria (CBR-RUN-013D-1) |
| **Owner research promotion** | **APPROVED** for baseline research on the full evidence record |

The scored PC4 parity run is **not** labelled PASS, now or in any later document. The promotion is a governance
decision about what the model is good enough *for*, not a re-scoring of the run.

**The frozen historical record is unchanged and is never rewritten:**

| Candidate | Run | Verdict |
|---|---|---|
| PC2 | CBR-RUN-013B-2 | **FAIL** |
| PC3 | CBR-RUN-013C-1 | **FAIL** |
| PC4 | CBR-RUN-013D-1 | **FAIL** |

## 2. Why Phase 13 may close (D37 §1)

PC4 reproduces the two strongest narrated / journal-supported CBR1H examples as eligible signals with all strict
dimensions satisfied — **CX-LT1-1** (trigger 01:39:35 vs Tom's ~01:39:15) and **CX-TE1-1** (04:38:55, inside Tom's
stated 04:37-04:39) — and correctly rejects the explicit negative control **CX-LT3-1**
(`NO_ELIGIBLE_CANONICAL_SIGNAL`). On CX-LT3-2 it reproduces the model family, direction, extension direction,
extension activation, previous-candle event, type-3 geometry, the 5-second shift and the approximate trigger time
(01:39:40 vs ~01:40:00); the remaining rejection falls on an example Tom himself calls "not the best condition",
"good enough", and capable of easily losing. No Level-1 evidence establishes a specific PC5 correction, and the
remaining uncertainty is localized rather than systemic. Continued rule revision would now risk parity overfitting
more than the unresolved ambiguity does.

## 3. What this approval means — and does not (D37 §9)

**Means:** the frozen PC4 implementation is sufficiently faithful to the stable, documented core of Tom's CBR1H
methodology to determine whether this deterministic interpretation has historical edge.

**Does not mean:** that PC4 is the unique correct implementation of CBR · that every discretionary Tom trade must be
reproduced · that OQ-48, OQ-50 or OQ-52 are solved · that CBR is profitable · that CBR has a statistically robust
edge.

## 4. Case and rule dispositions

| Item | Disposition |
|---|---|
| **CX-LT3-2** | **DISCRETIONARY_EXCEPTION**, preserved permanently as a **DISCRETIONARY_REFERENCE_CASE**. Not binding for future baseline specification, never deleted, never used to alter PC4. The classification rests on Tom's contemporaneous description, not on PC4's performance |
| **~20-minute extension** | **CANONICAL GUIDANCE**, not a proven hard minimum (OQ-53). PC4's hard-floor implementation is **preserved unchanged**; the discrepancy is documented and becomes a later controlled research question |
| **OQ-48 (HVCS)** | **OPEN**, `UNRESOLVED_SPEC_AMBIGUITY`. HVCS existence is canonical and "4+ minutes" is taught; the deterministic counting semantics are not uniquely specified. Approved as a future sensitivity experiment. PC4 unchanged |
| **OQ-50 (previous-15m instant)** | **OPEN**. Sufficiently resolved for research use, not uniquely proven. PC4 unchanged |
| **OQ-52 (condition classified at the hour open)** | **OPEN**. A real limitation of the deterministic model, preserved. `k = 3` unchanged, condition evaluation timing unchanged. PC4's classifier remains authoritative for the untouched baseline; later research may test it under a pre-registered ablation |
| **PC5** | **Not created.** PC4 becomes the frozen `CBR1H_BASELINE_V1` research specification |

## 5. The baseline alias (D37 §7)

`CBR1H_BASELINE_V1` is an **alias**, implemented in `src/cbr/engine/baseline_v1.py`. It adds no behaviour: it
resolves to the exact frozen PC4 spec hash
`62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7` and raises `BaselineDrift` if the live spec
differs. The frozen parity record `CBR1H_BASELINE_V1-PC4.yaml` is not renamed or edited. Every baseline artefact
carries `provenance()`, which restates the parity verdict as **FAIL** and lists the five documented fidelity
concerns, so no downstream report can present the model as validated.

## 6. Strategy lock (D37 §10)

From this decision until the untouched CBR1H baseline is produced, **none** of the following may change: type-3
logic · extension activation · pullback logic · HVCS interpretation · condition classifier · swing `k` · candidate
selection · 15m timing semantics · stop construction · target construction · DXY rules.

Any strategy-rule change before the untouched baseline invalidates the frozen baseline designation and requires a
new version. `baseline_v1.verify()` enforces this mechanically on every run.

## 7. Phase 14A authorization (D37 §11-16)

Phase 14A — the authoritative execution simulator — is authorized. Its purpose is **not** to change which signals
exist, only to determine what happens when frozen PC4 signals are executed under realistic market assumptions.
Signal generation and execution stay separate: the simulator may not invent signals, reject signals with new
strategy logic, alter direction, reinterpret CBR rules, or optimize stop or target placement.

**No performance analysis yet.** Phase 14A is tested on synthetic and designated non-performance fixtures. The
historical CBR1H success-rate report and the untouched baseline wait for Phase 14A acceptance. No execution
assumption may be tuned from trade outcomes.

## 8. Sequence after Phase 14A

14B (Backtesting.py adapter, secondary, never `Backtest.optimize()`) → Phase 15 (untouched CBR1H baseline, where
performance statistics are first computed) → Phase 16 (CBR15, only when independently baseline-ready). The Astra ×
Fable review does not begin until the untouched baseline exists, so that the baseline stays untouched by hypothesis
generation. **OQ-24** (baseline feed) must be resolved before the untouched baseline, on signal fidelity, data
availability, historical coverage, tick granularity, bid/ask availability, reproducibility and roll/basis risk —
never by comparing profitability.

## 9. Preservation

All historical FAIL verdicts, failed candidates and failed runs are preserved. PC1, PC2, PC3 and PC4 records, all
run manifests, and every frozen parity-set manifest remain in the repository unchanged.
