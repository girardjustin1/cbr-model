# G10 DXY Context Gate: Approval Record

**Doc:** CBR-GATE-G10 · **Date:** 2026-09-14 · **Decided by:** Owner (ruling D15) · **Phase:** 10 → OQ-25 package (Phase 11 blocked)

## Result

**PHASE 10: PASS WITH CONCERNS. G10 APPROVED**, subject to the documented limitations
(`reports/phase10-dxy-context.md`, CBR-ACC-010 v1.1).

## Accepted

- The causal DXY context architecture (`docs/architecture/dxy-context-module.md`)
- The separation between causal decision-facing fields (`dxy_*`) and hindsight-only data-quality fields
  (`dq_hindsight_*`)
- UTC-only decision timing
- No forward-fill across prohibited gaps
- Explicit confidence and availability states
- DX futures used only as a data-quality reference, never as a substitute price source
- 15m and 1h DXY directional context as currently supported
- The restriction against treating 1m or 5s DXY structure as validated canonical logic
- The two first-run defects (UTC dtype on an all-empty column; missing `DX_REFERENCE_UNAVAILABLE` visibility) were
  legitimate implementation defects, correctly fixed without weakening the criteria

## Rulings (D15)

| Id | Item | Ruling |
|---|---|---|
| D15-1 | OQ-31 DXY outage handling | Stays **OPEN** until before baseline statistics. Owner preference: **Option B**. Affected rows stay in the ledger, keep the causal DXY availability at decision time, and get a hindsight lower-confidence / data-quality label after the fact. They are **not** excluded from the canonical baseline. Baseline reports show ALL SIGNALS vs SIGNALS WITH FULL DXY DATA as a **diagnostic only**, never promoted to the canonical result without explicit approval |
| D15-2 | Recurring DXY CFD daily unavailability (18:00-20:00 New York; winter Asia hour 1) | Accepted as a known feed limitation. No fabricated context. Setups carry `DXY_AVAILABLE = false` with the reason/confidence state. Absence of DXY context is **not** confirmation, veto, bullish, bearish or neutral confluence unless a later canonical or research-approved rule defines it |
| D15-3 | Engineering thresholds (flat classification, coverage, quote age) | Implementation parameters only. Not strategy parameters, not optimized for profitability. Any sensitivity test must be pre-registered under research governance |
| D15-4 | Next task | OQ-25 canonical price-extremes decision package. **Phase 11 NOT STARTED** until OQ-25 is resolved; no CBR15 built on provisional highs/lows |

## What G10 does NOT mean

- DXY 1m/5s structure is validated
- DXY confluence, veto or inversion rules are adopted
- DXY absence has any directional meaning
- The engineering thresholds are validated beyond the 24 acceptance days
