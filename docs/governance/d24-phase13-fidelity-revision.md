# D24 Phase 13 Fidelity Revision: Ruling Record

**Doc:** CBR-RULING-D24 · **Date:** 2026-09-15 · **Decided by:** Owner ("Revise Phase 13 fidelity requirement")

## Result

Phase 13 is redefined as **STRATEGY FIDELITY AND BEHAVIORAL PARITY**.
- V-1 moves from **HARD PARITY GATE** to **SUPPORTING FEED-FIDELITY VALIDATION**.
- Exact historical FOREXCOM:XAUUSD 1-minute data for the 2025 course windows is no longer required. It was unavailable
  because of TradingView intraday history limits: the exports hold about 6,300-7,100 bars, and 1m history started
  2026-09-09 (D22, D23).
- PC2 is unchanged.
- **Status: NOT READY.** Phase 13 runs only after the owner approves the proposed run (CBR-PROT-013B). No Phase 14,
  profitability or optimization.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D24-1 | Canonical feeds | Dukascopy tick-mid = STRUCTURE, Dukascopy tick bid/ask = EXECUTION (unchanged). The claim is sufficiency of the spot data for the CBR price-action principles, not identity with FOREXCOM |
| D24-2 | V-1 | Reclassified as SUPPORTING FEED-FIDELITY VALIDATION; existing V-1 work and reports preserved; the unavailability of historical FOREXCOM 1m is recorded |
| D24-3 | Phase 13 objective | Does the deterministic engine recognize the same underlying CBR market behavior Tom teaches? |
| D24-4 | Behavioral parity dimensions | model, direction, market condition, range / trending-range state, extension direction, extension timing, previous-candle take, structural shift type, approximate shift time, stop-anchor concept, target concept, documented DXY context. No exact price equality required |
| D24-5 | Price differences | Always reported. `FEED_DIFFERENCE` when the structural event is equivalent; `FEED_DEPENDENT_SIGNAL_DIFFERENCE` when the difference changes the strategy interpretation (e.g. Tom's feed takes the high and shifts, Dukascopy never takes it) |
| D24-6 | Course examples | The three hourly examples (CX-LT1-1, CX-TE1-1, CX-LT3-2) on canonical Dukascopy data. No outcome or P&L. No tuning. PC2 frozen during the evaluation |
| D24-7 | Tom's FOREXCOM exports | Preserved. Historical 1h / 4h / 1D = supporting higher-timeframe fidelity evidence on the course windows. Recent 1m / 5m / 15m = independent feed-comparison fixtures. Never used to tune CBR parameters |
| D24-8 | Recent 1m feed comparison | Approved as a supporting validation study. May acquire Dukascopy data for recent non-course days overlapping the FOREXCOM 1m export. Compares timestamps, direction, OHLC, structural highs/lows, swing membership, 15m takes, extension extrema, and 5s/1m structure where comparable. Not used to select parameters; estimates how often feed differences change structural interpretation |
| D24-9 | New Phase 13 gate | A causal and deterministic engine; B frozen spec implemented correctly; C behavioral agreement on core CBR concepts; D every mismatch classified; E no unexplained implementation mismatch; F feed differences documented; G no evidence that reasonable spot-feed differences change CBR signal membership at an unacceptable rate |
| D24-10 | Verdicts per example | BEHAVIORAL_MATCH, BEHAVIORAL_MATCH_WITH_FEED_DIFFERENCE, OWNER_BASELINE_CHOICE, UNRESOLVED_SPEC_AMBIGUITY, FEED_DEPENDENT_SIGNAL_DIFFERENCE, IMPLEMENTATION_BUG, CANON_MISMATCH; categorical rule-by-rule assessment instead of an arbitrary match percentage |
| D24-11 | PC2 | Unchanged; the feed-validation requirement is governance, not a CBR rule |
| D24-12 | Meaning of a pass | "The engine is sufficiently faithful to Tom's taught CBR price-action methodology to begin execution and baseline testing." Not: tick-for-tick FOREXCOM reproduction, profitability, robust edge, or feed identity |
| D24-13 | Next | Update the PRD and Phase 13 acceptance criteria; preserve V-1 as supporting evidence; propose the exact behavioral-parity run; stop for owner approval before running it |

## Documents

- Acceptance criteria: `docs/acceptance/phase13-acceptance-criteria.md` (CBR-ACC-013).
- Proposed run: `docs/governance/phase13-behavioral-parity-protocol.md` (CBR-PROT-013B, PROPOSED).
- **CBR-PROT-013** (`phase13-parity-protocol.md`) stays pinned in PC2 and unedited. Its §5 selection, §3 mismatch
  classes and §2 views still apply. Its §6 V-1 section is now supporting validation, and its hard-gate wording is
  superseded by this record.
