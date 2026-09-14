# Proposal: Split AC-11 (Phase 9 historical-data acceptance)

**Status:** APPROVED WITH MINOR CHANGES (owner, 2026-09-14; decision D11). Binding version: `docs/acceptance/phase9-acceptance-criteria.md` · **Date:** 2026-09-14 · **Affects:** `reports/phase9-data-acceptance`, PRD gate G1

> Nothing in the PRD or acceptance criteria has been changed. No history download is running or queued. Only the
> already-approved fixture job (Oct-Nov 2025 candles + entry tick windows) continues.

---

## 1. Why the current AC-11 is the wrong gate

- **It mixes two questions.** "Is the spot pipeline correct?" can be answered with a few dozen well-chosen days.
  "Do we own the full spot history?" is a data-acquisition problem. Only the first belongs in Phase 9.
- **It doesn't deliver what the baselines need anyway.** Full 1-minute spot candles still wouldn't give CBR15 its
  **5-second entries** (D2) across 2018-2024. That needs ticks around every armed signal, potentially thousands more
  hour files. Finishing today's AC-11 would cost days and still leave the Phase 15-16 data question open.
- **Today's fixtures are too narrow.** All of them fall in **Oct-Nov 2025, inside the holdout**, at gold ≈ $4,000.
  They prove the decoder in one regime only, not across 2018-2024 (different price levels, tick density, spreads,
  DST states, and the dollar index CFD's early years). So the requirement shouldn't just shrink; the proof has to get
  broader.

---

## 2. Proposed replacement

### AC-11A: Spot pipeline proven on representative fixtures (required for Phase 9)

All thresholds are fixed **before** the new days are downloaded.

1. **Stratified sample: 16 trading days from 2018-2024** (development/validation periods, integrity use only),
   chosen by rule, not by looking at prices:

   | Stratum | Days |
   |---|---|
   | One mid-month day per year, 2018-2024 | 7 |
   | US DST transition weeks (spring, autumn) | 2 |
   | US holiday with thin trading | 1 |
   | Monday after a weekend reopen | 1 |
   | Dollar index CFD's first full month (2018-01) | 1 |
   | Pre-declared high-volatility dates: 2020-03-09, 2020-03-16, 2022-03-08, 2024-04-12 | 4 |

2. **Every existing check applies to each day, for both instruments:** decoder parity, integrity, determinism,
   reconciliation, classified gaps, bad-data flags. For gold, the price scaling must also match GC to within the
   basis, so a historical point-value change can't slip through.

3. **Feed agreement against Databento on every sample day** (pre-declared thresholds):

   | Pair | 1m return correlation | Best lag | Other |
   |---|---|---|---|
   | XAUUSD spot vs GC | ≥ 0.95 | 0 min | No intraday basis jump > $5 outside roll dates |
   | DXY CFD vs DX | ≥ 0.90 (thinner instrument) | 0 min | none |

   Any failing day is reported, not dropped.

4. **Tick windows** on 4 of the 16 days, so 5-second bars are validated outside the holdout.

5. **Timezone:** Tom's chart points still match (already passing).

**Cost:** about 64 candle files plus about 20 tick hours, which is hours, not days.

### AC-11B: Complete historical spot dataset (deferred)

- Not required for Phase 9; tracked as the one open concern.
- **A hard precondition for whichever phase first consumes spot history.** Which phase that is depends on the
  baseline-feed decision (§5).

---

## 3. Explicitly unchanged (not weakened)

- Lookahead and causality tests, UTC, explicit gaps and bad-data flags.
- **Parity (Phase 13) stays on spot.** Tom's examples must be reproduced on Dukascopy spot, the feed closest to his
  FOREX.com chart.
- **AC-09 still requires the dollar index comparison**, which isn't measured yet. Phase 9 can't pass on gold evidence
  alone.

---

## 4. Verdict rule under the change (SUPERSEDED: owner replaced automatic FAIL with failure classification; see CBR-ACC-009 §4)

| Verdict | Condition |
|---|---|
| **PASS** | AC-01…AC-10, AC-11A and AC-11B all pass |
| **PASS WITH CONCERNS** | AC-01…AC-10 and AC-11A pass; AC-11B outstanding |
| **FAIL** | Any integrity, determinism, timezone or feed-agreement check fails on a sample day, until explained and fixed |

---

## 5. Research consequences for the owner

### 5.1 Phases 10-13 can proceed on validated fixtures
None of them needs full history.

### 5.2 The real decision moves to "which feed runs the baselines (Phases 15-16)?"
It must be settled before Phase 14. Proposed as new open question **OQ-24**.

| Option | For | Against |
|---|---|---|
| **a. Spot history (original plan)** | Matches Tom's feed | AC-11B blocks Phase 14. 1m history via candles is feasible over a long resumable download. **5s history for CBR15 is still unsolved.** |
| **b. GC/DX futures history, spot for parity** | Data already owned. Real exchange volume. Agreement so far 0.988-0.994. | Contract rolls ($16 median jumps) need a declared handling rule. ohlcv-1m has no bid/ask, so costs must come from spot spread statistics. DX ≠ TVC:DXY. No 5s bars without buying GC 1s (quoted $235). |
| **c. Hybrid** | 1m structure on GC/DX. Entries use spot ticks fetched only for armed-signal hours, with a request budget | Most engineering. Mixes feeds inside one signal, so it needs its own agreement check. |

### 5.3 New safeguard needed regardless of the feed choice (proposed for Phase 13/14, not Phase 9)
A **cross-feed signal-agreement test.** Run the engine on spot and GC for the 16 sample days and require the same
setups (direction, hour, entry window) at a pre-declared rate before any futures-based baseline counts. This catches
"CBR detected on GC but not on spot", the feed-mismatch risk.

### 5.4 The holdout isn't affected
The new sample days are all in 2018-2024, used only for data integrity (no trades, no P&L) and logged in
`research/holdout-access-log.md` for completeness.

---

## 6. Evidence so far (gold fixtures, 2025-10-20 → 2025-10-23)

| Check | Result |
|---|---|
| Tick integrity | 0 duplicates, 0 bad spreads, 0 non-positive prices, monotonic, UTC |
| Determinism | 5s and 1m bars rebuilt bit-identically; manifest hashes match |
| Reconciliation | Tick counts reconcile; 5s → 1m roll-up exact |
| Gaps | 60 missing minutes/day, all in the 17:00-18:00 New York break; 0 unexpected |
| Decoder parity | 285,935 ticks, identical to the reference CLI |
| Candle vs tick bars | Open/close identical on 1,380 minutes; high/low within $0.05 ≈ 90% (bid/ask averaging) |
| Spot vs GC | Basis +$14.08 to +$15.47 mean; 1m return correlation 0.988-0.994 at lag 0; futures moves ~2-3% larger |
| Tom's chart | Dukascopy low −$0.005 from his stop price |
| DXY CFD vs DX | **Not yet measured** (fixture download in progress) |

---

## 7. Owner decisions requested

1. **Approve splitting AC-11** into **AC-11A (required for Phase 9)** and **AC-11B (deferred)** as written, or edit
   the sample design or thresholds.
2. **Acknowledge OQ-24** (baseline feed: spot / futures / hybrid) as a decision required **before Phase 14**, not now.

Until approved, the PRD, acceptance criteria and phase status stay as they are, and Phase 10 does not start.
