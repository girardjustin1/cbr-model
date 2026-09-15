# G12 CBR1H Engine Gate: Approval Record

**Doc:** CBR-GATE-G12 · **Date:** 2026-09-15 · **Decided by:** Owner (ruling D18) · **Phase:** 12 → Phase 13 readiness

## Result

**PHASE 12: PASS WITH CONCERNS. G12 APPROVED** for deterministic CBR1H engine construction, causal state handling,
implementation quality, hourly-state exposure to CBR15, and diagnostic parity analysis.
**CBR1H is NOT baseline-eligible. Phase 13 is NOT authorized.**

## Rulings (D18)

| Id | Item | Ruling |
|---|---|---|
| D18-1 | OQ-39 hourly entry model | Level 1 evidence conflict. Not resolved by matching examples, nor by favouring the earlier spec. **OQ-39 evidence package** required: the 5s shift classified as A actual trigger / B refinement after a 1m setup / C optional execution refinement / D example-specific / E other model / F unresolved; distinct variants preserved; each interpretation with supporting and contradicting evidence, exact machine rule, effect on the three examples, CANON vs implementation. Stop for owner approval before changing the canonical CBR1H entry rule |
| D18-2 | OQ-40 condition window across closures | Open pending evidence. No automatic clock / trading / bar-count / session reading. Compare A clock, B tradable time, C populated bars, D session segments; CX-LT3-2 effects on range classification, swings, state, eligibility. If evidence is insufficient: `CONDITION_WINDOW_UNRESOLVED`, owner assumption required before baseline eligibility |
| D18-3 | OQ-41 previous 15m reference | Don't guess. Evidence package listing interpretations with algorithm, consequences for the three examples, CANON vs ASSUMPTION |
| D18-4 | OQ-42 :30 veto timing | Open. Spec says at fill; engine evaluates at arm time; not equivalent. Classify as signal eligibility / order activation / fill eligibility / lifecycle. If Level 1 says "at fill", preserve it; if true fill information is needed, mark `EXECUTION_DEPENDENT`, defer to 14A, and retain the causal inputs. No decision-time approximation to ease Phase 13 |
| D18-5 | OQ-43 HVCS end bar | Open pending evidence: last displacement bar / reversal bar / HILO bar / bar before the structure break / taught alternative; effects on HVCS class, HILO eligibility, arm time, the three examples |
| D18-6 | OQ-36 prior setup | Evidence package **required before Phase 13**; COND-03 unchanged until reviewed; define working setup, played out, evaluation time, ending event, timeframe, and whether CBR15 and CBR1H differ (represent separately if so) |
| D18-7 | D8/D9 in parity | Not unexplained failures, not hidden. Mismatch classes: `CANON_MISMATCH`, `IMPLEMENTATION_BUG`, `FEED_DIFFERENCE`, `OWNER_BASELINE_CHOICE`, `UNRESOLVED_SPEC_AMBIGUITY`, `EXECUTION_DEPENDENT`, `DATA_LIMITATION`. Report both **STRICT COURSE PARITY** and **BASELINE-SPEC PARITY** |
| D18-8 | Phase 13 tolerances | Phase 12 tolerances rejected (post-hoc). New tolerances from independent evidence (Phase 9 feed comparisons, FOREXCOM vs Dukascopy offsets, timestamp resolution, tick size/precision, non-course fixture differences), frozen before the final Phase 13 run; never from engine closeness to Tom's examples |
| D18-9 | Candidate selection | Pre-registered, using engine-available information only (not "closest to Tom's entry"); frozen before the final run |
| D18-10 | V-1 | Hard Phase 13 requirement: FOREXCOM:XAUUSD 1m TradingView export for the course-example periods; data fidelity only; feed-driven mismatches classified; if signal membership changes materially, stop and reopen OQ-25 |
| D18-11 | M15-HTF-01 fill component | Phase 14A not required for Phase 13. Separate SIGNAL-STATE parity (hourly candidate exists, direction, armed, trigger touched) from EXECUTION-STATE parity. A fill-proof requirement is `EXECUTION_DEPENDENT` with `HTF_FILL_STATE = NOT_EVALUATED`; this doesn't invalidate engine parity, but CBR15 isn't fully baseline-eligible until evidence shows fill is unnecessary or 14A evaluates it. No fabricated fills |
| D18-12 | Readiness | `docs/governance/phase13-readiness.md` checklist; Phase 13 may not start with any required item unchecked |

Standing constraints: no profitability, optimization, holdout P&L, Backtesting.py or Astra × Fable review; no canonical
spec change before owner rulings.
