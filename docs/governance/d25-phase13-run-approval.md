# D25 Phase 13 Behavioral-Parity Run Approval: Ruling Record

**Doc:** CBR-RULING-D25 · **Date:** 2026-09-15 · **Decided by:** Owner ("OWNER APPROVAL — CBR-PROT-013B / PHASE 13
BEHAVIORAL PARITY")

## Result

CBR-PROT-013B is **APPROVED** subject to the rulings below. Phase 13 behavioral-parity execution is authorized after
the protocol, code, fixtures and acceptance criteria are frozen.

Standing conditions:
- PC2 is not changed during the run.
- No optimization, no profitability, no trade outcomes.
- Phase 14 does not begin until the Phase 13 report is returned for owner review.
- Freeze first, then execute Phase 13 exactly once under the frozen protocol, followed by the required deterministic
  rerun. Return the report and stop.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D25-P1 | Protocol | APPROVED. Phase 13 evaluates behavioral fidelity to Tom's taught CBR methodology, not exact broker-feed price replication: do the frozen PC2 engines identify the same underlying CBR behavior shown in the course examples? |
| D25-P2 | Recent feed-comparison days | APPROVED: 2026-09-09, 2026-09-10, 2026-09-11, 2026-09-14. Used only for FOREXCOM:XAUUSD vs Dukascopy XAUUSD feed/structure comparison. Never for parameter selection, optimization, profitability, threshold tuning or model selection. Frozen before Dukascopy is downloaded or measured |
| D25-P3 | Structural event match | APPROVED. Same event when: (1) same underlying price-action structure; (2) direction agrees; (3) within ±1 relevant structural bar where a bar comparison is appropriate; (4) timing differs by ≤ 3 minutes where a lower-timeframe timestamp comparison is required. The 3 minutes absorb feed/event representation differences and never select a different candidate because it is closer to Tom's entry. Selection stays deterministic and answer-independent |
| D25-P4 | Feed band | APPROVED: τ = max($0.02, p95 offset-adjusted residual), rounded up to the nearest $0.05, on the pre-declared recent days only. The formula isn't modified after course results are seen. Descriptive/supporting evidence; never a strategy parameter |
| D25-P5 | Acceptance standard | **Option B:** pre-declared before the run, evaluated dimension by dimension, no exact price equality. Positive-example dimensions: A model family, B direction, C condition, D extension, E location / previous-candle event, F structural trigger, G timing, H stop concept, I target concept (owner baseline choices classified separately) |
| D25-P5-H | Hard dimensions | For the three positive examples: model family 3/3, direction 3/3, core extension direction 3/3, core structural trigger 3/3. No unexplained `IMPLEMENTATION_BUG` or `CANON_MISMATCH` may remain on a hard dimension |
| D25-P5-S | Supporting dimensions | Condition subtype, exact price, target level and other dimensions affected by feed differences, explicit owner baseline choices or unresolved non-core course ambiguity are reported individually. They don't automatically fail behavioral parity when the CBR behavior is equivalent and the mismatch has a defensible pre-existing classification. Never hidden in an aggregate score |
| D25-P5-V | Overall verdict | **PASS** requires: (1) 3/3 model family; (2) 3/3 direction; (3) 3/3 core extension direction; (4) 3/3 core structural-trigger concept; (5) the negative control produces no eligible canonical signal; (6) no unresolved implementation bug affects signal membership; (7) no unexplained canonical mismatch affects signal membership; (8) every other mismatch explicitly classified; (9) the recent FOREXCOM/Dukascopy comparison shows no evidence that normal feed differences routinely destroy the structural concepts CBR requires. **PASS WITH CONCERNS:** hard dimensions pass but documented feed differences, owner baseline choices, data limitations or non-core ambiguities remain. **FAIL:** a hard dimension fails without an already-approved explanation, or the feed study shows CBR signal membership is materially unstable across reasonable spot feeds. No post-hoc numerical overall score |
| D25-P6 | Course condition mapping | APPROVED. CX-LT3-2: `TRENDING_RANGE UP` is compatible with Tom's condition; `TREND` alone is not equivalent. The exact engine classification is preserved in the report, never rewritten as MATCH |
| D25-P7 | Negative control | APPROVED: CX-LT3-1 (Tom passed on the setup), frozen before the run. Expected: **NO ELIGIBLE CANONICAL SIGNAL**. If the engine produces one, classify exactly which rule difference caused it. PC2 isn't altered and nothing is tuned to make it pass |
| D25-P8 | DXY | APPROVED, descriptive only. Report the DXY context at each course example where supported. No DXY agreement requirement, no DXY veto, no DXY optimization, no DXY-based signal change. DXY's incremental value belongs in later ablation research |
| D25-F | Freeze before execution | Freeze and hash: CBR-PROT-013B; PC2; the four recent dates; the four course examples (CX-LT1-1, CX-TE1-1, CX-LT3-2, CX-LT3-1 negative control); candidate-selection rules; mismatch taxonomy; P-3 criteria; P-4 formula; P-5 rules. Run the complete pre-execution test suite |
| D25-E | Execution | 1 acquire Dukascopy for the four days; 2 compare recent FOREXCOM:XAUUSD vs Dukascopy XAUUSD (timestamp alignment, OHLC residuals, feed offset, p95 residual, feed band, swing agreement, previous-candle take agreement, extension-extreme agreement), modifying nothing; 3 historical FOREXCOM 1h/4h/1D vs Dukascopy around the course examples (supporting); 4 PC2 on the three positive examples; 5 PC2 on CX-LT3-1; 6 repeat the complete run from the same frozen inputs (identical results required); 7 classify every mismatch with the frozen taxonomy; 8 report |
| D25-R | Report | Frozen protocol hash; PC2 hashes; data hashes; recent feed comparison; higher-timeframe comparison; behavioral-parity table per positive example; negative-control result; every mismatch and its class; deterministic rerun; causality status; unresolved concerns; verdict PASS / PASS WITH CONCERNS / FAIL. Stop for owner review |
| D25-A | Administrative cleanup | Correct the stale PRD status metadata (current phase 13; branch, commit and push state). Documentation only; historical decision records unchanged. Trader.dev stays documented as unavailable; it no longer blocks the project because Phase 14A and Backtesting.py are the planned local backtesting architecture |

## Research Engineer operationalization (frozen in `config/phase13_behavioral_run.yaml`)

The approval leaves a few execution details without an explicit rule. Each is fixed below, **before** any Dukascopy
data for the D25-P2 days is fetched and before any Phase 13 engine run, and is flagged here for owner review in the
verdict. None is a strategy rule and none changes PC2.

| # | Detail | Frozen reading | Basis |
|---|---|---|---|
| O-1 | Criterion 9 has no number | For seven core structural concepts (LTF 1m swing membership, MTF 5m swing membership, 15m previous-candle takes, hourly extension direction, condition class at the hour open, 1m type 3 events, hour-level CBR1H setup membership without the 5s trigger): **FAIL evidence** if any agreement point estimate < 0.50 ("routinely" = more often than not); **CONCERN** if any < 0.80. Wilson 95% intervals reported | 0.80 = CBR-ACC-010 AC10-10 concern precedent; 0.50 = the plain meaning of "routinely". Owner may reject this reading in the verdict |
| O-2 | CX-LT3-1 control window | ARMED BASELINE_SPEC candidate (variant A or B) whose `five_second_shift_time` ∈ [2025-11-10 01:28:00, 01:36:00) UTC = an eligible canonical signal | Video clock 00:00:00 = 12:23:41 UTC+11; discussion 00:07:47-00:09:16 → 01:31:28-01:32:57 UTC; D25-P3 3-minute allowance each side, widened to whole minutes |
| O-3 | Variants | A and B each get a full dimension table. An example meets the hard dimensions when one variant's engine-selected BASELINE_SPEC candidate meets all four; the scored variant is the first in order A, B that does (else the one meeting most, ties → A) | Protocol §4 dim 1: Tom's parent setup type isn't stated, so the variant is reported, not scored |
| O-4 | Core structural trigger | Dim 8 MATCH (5s shift completed in Tom's direction) **and** dim 9 MATCH or FEED_DIFFERENCE (D25-P3 equivalent: same direction, 5s type 3, same 15m candle as Tom's entry, \|Δt\| ≤ 3 min) | D25-P3; protocol §4 dims 8-9, §6 |
| O-5 | Already-approved explanations on a hard dimension | FEED_DIFFERENCE (D25-P3) counts as a match; OWNER_BASELINE_CHOICE (D8/D9) is approved but isn't a match: a hard dimension failing only for that reason gives **OWNER_DETERMINATION_REQUIRED** (neither the PASS/PWC nor the FAIL rule applies). Any other class on a failed hard dimension → FAIL | D25-P5-V wording |
| O-6 | Concerns | PASS only if every dimension (except DXY) is BEHAVIORAL_MATCH, every example is ARMED, the negative control is clean and criterion 9 has no concern. Otherwise, with hard dimensions met and no FAIL condition, PASS WITH CONCERNS | D25-P5-V |
| O-7 | Negative-control classification | A signal that disappears under one D8/D9 alternative → OWNER_BASELINE_CHOICE; otherwise UNRESOLVED_SPEC_AMBIGUITY (OQ-08: shift size / cleanliness unquantified in PC2), secondary OUT_OF_SCOPE_INSTRUMENT (gold spread, D7); IMPLEMENTATION_BUG only with a failing test (→ FAIL) | Tom's stated reasons (CX-LT3-1 record); protocol §3 taxonomy |
| O-8 | DXY | Excluded from example verdicts and concerns | D25-P8 |

## Documents

- Protocol: `docs/governance/phase13-behavioral-parity-protocol.md` (CBR-PROT-013B, APPROVED by this record).
- Frozen run specification: `config/phase13_behavioral_run.yaml` (CBR-RUN-013B-1).
- Freeze manifest: `reports/phase13-freeze-manifest.json`.
- Acceptance criteria: `docs/acceptance/phase13-acceptance-criteria.md` (CBR-ACC-013), gate G read with D25-P5.
