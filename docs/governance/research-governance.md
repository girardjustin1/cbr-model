# Research Governance: Astra × Fable Review Framework

**Doc:** CBR-GOV-001 · **Version:** v1.0 · **Adopted:** 2026-09-14 (owner instruction) · **Applies from:** Phase 15 onward

This framework adds two formal joint research reviews to the CBR project. It **adds to** every existing control
(evidence hierarchy, CANON / ASSUMPTION / IMPL labelling, chronological splits, single-use holdout, hypothesis log)
and replaces none of them.

Central objective (unchanged): determine whether CBR has a repeatable, robust edge. **A trustworthy finding of no
edge is a successful research outcome.**

---

## 1. Roles

| Role | Responsible for | May NOT |
|---|---|---|
| **Fable: Research Director** | Interpreting results; identifying possible market mechanisms; finding weaknesses in the CBR hypothesis; proposing testable hypotheses, ablations and high-information experiments; identifying regime dependencies and alternative explanations for apparent performance. May *propose* research-derived features. | Change CANON CBR rules · implement changes · optimize against the holdout · introduce unexplained parameters · promote a feature into the production model |
| **Astra: Independent Quant Auditor** | Challenging Fable's hypotheses; identifying hindsight bias, overfitting, multiple testing, leakage/lookahead; evaluating sample size, statistical validity and parameter-selection methodology; judging whether experiments are scientifically defensible and whether conclusions are supported. Rules each proposal **APPROVE / APPROVE WITH CONSTRAINTS / REJECT**. | Attempt to make CBR profitable |
| **Claude Code: Research Engineer** | Implementing frozen specifications; running **approved** experiments; producing reproducible outputs; maintaining tests and the signal ledger; generating reports. | Independently invent trading rules because they improve historical results · run an experiment that is not owner-approved and registered · modify a registered experiment after execution starts |
| **Owner** | Final approval over experiment execution, methodology changes, promotion of research-derived features, holdout evaluation, and production indicator composition. | none |

Fable and Astra are review roles. Each review is produced as a separate, independent document with its own inputs,
so reasoning can be audited. Fable and Astra never see each other's Round 1 work before submitting their own.

---

## 2. Phase 17: Astra × Fable pre-experiment review

**Precondition:** Phases 15 (untouched CBR1H baseline) and 16 (untouched CBR15 baseline) are complete and frozen.
Phase 17 must not start before both baselines exist.

### 2.1 Research package (identical for both reviewers)

PRD · machine specifications · rule matrix · ambiguity register · evidence hierarchy · open questions · baseline
signal ledger · all baseline trades · rejected/no-trade reason codes · year-by-year statistics · expectancy after
costs · profit factor · win rate · drawdown · trade count · regime breakdowns · execution assumptions · known data
limitations.

**Excluded:** any holdout-period performance. Course-example days inside the holdout appear only in the parity report,
never with outcome statistics.

### 2.2 Rounds

| Round | Who | Output | Rule |
|---|---|---|---|
| 1a | Fable (independent) | Baseline diagnosis + **at most 10** high-information experiments | Sees package only |
| 1b | Astra (independent) | Methodology audit + statistical/research risk register | Sees package only |
| 2 | Astra | Ruling per Fable experiment: APPROVE / APPROVE WITH CONSTRAINTS / REJECT, with reasoning | Must address: economic rationale, hindsight risk, researcher degrees of freedom, multiple testing, parameter ranges, sample size, falsifiability, validation contamination, holdout contamination |
| 3 | Fable | Per proposal: defend / modify / narrow / withdraw | No new experiments, except ones marked "future research round" |
| 4 | Astra | Final audit ruling per experiment | Then **STOP** |

**Output:** `reports/governance/phase17-owner-approval.md`, listing each experiment with Fable's case, Astra's
final ruling and constraints, and an owner decision field. **Nothing executes automatically.**

---

## 3. Frozen experiment registry

Owner-approved experiments are written to `research/experiments/registry.yaml` **before** execution
(schema: `research/experiments/SCHEMA.md`, enforced by `tests/test_experiment_registry.py`).

- Required fields: `experiment_id, title, proposed_by, reviewed_by, status, hypothesis, economic_rationale,
  classification, variables, parameter_ranges, baseline_comparison, primary_metric, secondary_metrics,
  development_period, validation_period, holdout_status, failure_condition, promotion_condition, overfitting_risk,
  implementation_notes`.
- Research-derived variables carry `classification: RESEARCH-DERIVED`.
- A spec is **immutable once `status` becomes `RUNNING`** (a content hash is recorded). Any change requires a **new
  experiment ID**; the old one is closed as `SUPERSEDED`. Never modify an experiment after observing results.
- Every registered experiment also gets a `research/hypothesis-log.md` entry.

---

## 4. Approved-experiment stage (Phases 18-19)

Only owner-approved, registered experiments run, on development and validation data only. Candidate categories
(**hypotheses, not assumed improvements**; none is implemented merely for being listed): DXY confirmation, veto,
timing; XAU/DXY divergence; range characteristics; extension duration, magnitude, velocity; retracement behavior;
volatility regime; session/time of day; significant levels; CBR15 × CBR1H interaction; structure-shift
characteristics.

Pre-existing owner decisions **D8** (overextension origin, OQ-22) and **D9** (early-shift guard, OQ-23) are
**pre-registered ablation candidates**. They enter the Phase 17 package and go through the same rounds and
registry. They are not executed before that.

## 5. Robustness stage (Phases 20-23)

For approved candidates: chronological validation · parameter sensitivity · walk-forward · bootstrap confidence
intervals · Monte Carlo · regime stability · year-by-year · concentration · execution-cost sensitivity. Holdout
stays locked.

---

## 6. Phase 24: Astra × Fable post-experiment review

- **Fable asks:** "What have we learned about the market behavior underlying CBR, and which findings appear
  economically meaningful?"
- **Astra asks:** "Which conclusions are supported strongly enough to survive independent quantitative scrutiny?"
- **Each finding is classified:** **PROMOTE · RESEARCH ONLY · INSUFFICIENT EVIDENCE · REJECT.** A research-derived
  feature becomes a holdout candidate **only if Astra approves its evidence** (and the owner approves promotion).
- **Output:** a final candidate-model specification, **frozen (hashed) before the holdout is accessed.**

## 7. Holdout policy (2025-01-01 → 2026-08-31)

- **Single use.** No person, role or process (Astra, Fable, Claude Code, any optimizer) may inspect holdout
  performance while selecting features, filters, thresholds, parameter values, models or scoring systems.
- **Course-example days** in the holdout remain usable **only for implementation parity**. They never contribute to
  performance evaluation or parameter selection.
- **Evaluation:** once the candidate spec is frozen and the owner approves, run the holdout **once** and record the
  result whether it succeeds or fails.
- **No retuning after the holdout** presented as validated. A retuned model is a new, unvalidated candidate.
- **Engineering controls:** the backtest runner refuses holdout dates unless invoked with the frozen candidate's
  spec hash and an owner-approval reference; each access is appended to `research/holdout-access-log.md`.

## 8. TradingView chain (downstream of validation)

Python reference model → Pine strategy parity implementation → Python ↔ Pine parity → validated TradingView
indicator → alerts → forward signal ledger. The polished indicator is **not** built before statistical validation.
LuxAlgo Quant may later assist with Pine implementation, but it is never the source of truth for strategy research.
**The Python reference engine is authoritative.**

## 9. Data-feed decisions (owner decision D11)

- The baseline data feed for Phases 15-16 (OQ-24: Dukascopy spot, GC/DX futures, or hybrid) stays **open** until Phase 9
  feed validation is complete, the CBR15 and CBR1H reference engines exist, Phase 13 parity is complete, and cross-feed
  signal agreement has been measured. It is **frozen before Phase 14** and recorded with its rationale.
- **Selection criteria:** fidelity to Tom's taught model · signal agreement · timestamp/structure agreement ·
  historical availability · execution realism · 5-second entry feasibility · reproducibility · known feed
  distortions (e.g. futures contract rolls).
- **Historical profitability must not be used to choose a feed.** Neither Fable nor Astra may compare strategy
  performance across feeds as input to this decision.
- Futures data may support baseline performance claims only after the **cross-feed signal-agreement** requirement
  (PRD gate G2b) passes, with its agreement threshold declared before measurement.
- Phase 9 data acceptance follows CBR-ACC-009: failures are classified (PIPELINE_ERROR, DATA_ERROR,
  EXPECTED_MARKET_BEHAVIOR, EXPECTED_FEED_DIFFERENCE, UNEXPLAINED_FEED_DIFFERENCE), failing days are never dropped
  or replaced, and complete spot history (AC-11B) is a deferred dependency, not a Phase 9 requirement.
