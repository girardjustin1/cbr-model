# Hypothesis Log

Every experiment is logged **before** it runs. No silent parameter mining; no re-running until something looks
profitable. Holdout results are recorded once per frozen version.

## Template

```
### H-000 · <short title>
- Date logged:
- Model / version under test:
- Hypothesis:
- Reason / source: (rule id, evidence id, OQ id, or journal trade id; label LEVEL-1 / LEVEL-2-DERIVED / RESEARCH-DERIVED)
- Parameter(s) tested:
- Expected effect (direction + which metric):
- Test range (fixed before running):
- Dataset / split:
- Baseline compared against:
- Minimum sample size to judge:
- Result: (filled after running; link report)
- Decision: ADOPT / REJECT / INCONCLUSIVE, with reason
```

## Pre-registered constraints

- Course example days (Oct-Nov 2025) are used only for signal parity, never for performance or tuning
  (they fall inside the holdout).
- Splits fixed in `docs/architecture/data-requirements.md` §6 before any backtest.

## Entries

_None yet. Milestone 1 (knowledge base) has no experiments._
