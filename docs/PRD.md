# CBR Model: PRD Summary

**Doc:** CBR-PRD-001 · **Version:** v1.0 · 2026-09-14 · **Status:** Active (Phase 9) · **Instruments:** XAUUSD + DXY
**Branch:** `cbr-work-091426-10am` · Full version: `docs/PRD.html`

---

## Primary objective

Find out whether Tom's CBR method has a **repeatable, robust edge on XAUUSD** (with DXY as context), and **which conditions create that edge**.

A trustworthy "no edge" answer counts as success. The TradingView indicator is built **only if** the edge survives out-of-sample testing.

---

## The problem

- CBR is taught visually and discretionarily. Words like "decisive", "high volume" and "clean" matter but have no numbers.
- Tom's reported win rates (e.g. "80% with DXY") come from hand-journaled trades with no sample sizes. His one backtest was ~10 trades in a month he picked.
- Three risks the project guards against:
  - **Hindsight bias:** judging setups by outcome
  - **Overfitting:** tuning until history looks good
  - **Unfaithful translation:** coding something he didn't teach

---

## Goals

- Traceable written and machine specs for the 15m and 1h models
- A Python engine that reproduces his setups with no lookahead
- **Baseline backtests of his rules as taught**, before any tuning
- Chronological testing: development 2018-2022 · validation 2023-2024 · holdout 2025-2026 (used once)
- Tests showing which extras actually add value (DXY, levels, sessions, 15m alignment)
- A non-repainting indicator and alerts, **only after validation**
- A ledger recording every signal, taken or not

## Non-goals

- Maximizing win rate
- Inventing rules
- Other instruments (USDJPY, silver, gold spread)
- Live auto-trading
- Publishing course material or market data
- Tuning before baselines exist

---

## Principles

- **Evidence levels**
  - **Level 1:** course videos define rules
  - **Level 2:** journal and live calls only clarify
  - **Level 3:** backtest findings, labeled `RESEARCH-DERIVED`
- **Every rule cites** a video, timestamp and verbatim quote, checked by tests
- **Every number is labeled:**
  - `CANON`: from Tom, cites evidence
  - `ASSUMPTION`: our choice, test range declared in advance
  - `IMPL`: engineering only
- **No lookahead**, all times UTC; validity judged at entry, never from the outcome
- **Missing data lowers confidence**; it's never filled in
- **Local-first:** no keys, course material or market data in git

---

## Owner decisions

| # | Decision |
|---|---|
| D1 | Fractal-shift setups excluded from the first baseline |
| D2 | 5-second bars from Dukascopy ticks; Pine uses 1-minute (labeled simplified) |
| D3 | No session filter, except no trading in the Sydney session or through rollover |
| D4 | Long recorded calls = Level 2 |
| D5 | TRR Forever becomes a third model, after the CBR baselines |
| D6 | No Notion journal for now |
| D7 | XAUUSD + DXY only |

---

## The models

**Core idea:** a candle opens and pushes hard one way for about half its duration, then price reverses toward the middle of that push. Timing comes from candle behavior; entry comes from a market-structure shift.

| Model | Condition | Extension | Entry | Status |
|---|---|---|---|---|
| **CBR1H** | 5-12 h range or trending range | Hour pushes ≥ 20 min, no 50% pullback, into range high/low | Shift between :22 and :52 (best :37) via HVCS→HILO or 1m fractal shift. 4 variants. | Specified |
| **CBR15** | 1.5-2.5 h range, 3-6 swings, ≥ 1 working setup in the last hour | 15m candle pushes ≥ 4 min, takes the previous 15m high/low | 5-second type 3 in the candle's second half; never against an active hourly CBR. 2 variants. | Specified |
| **TRR Forever** | Trend range, ≥ 50% pullback into a 30m/1h level | High-volume push into the level | Shift at :15 / :30 / :45 | After baselines |

Both CBR models: **stop** beyond the extension extreme, **target** 50% of the extension.

---

## Requirements

### Functional

| ID | Requirement |
|---|---|
| FR-01 | Reproducible video ingestion (manifest, hashes, transcripts, slide OCR) |
| FR-02 | Evidence base with verbatim quotes verified by tests |
| FR-03 | Written + machine specs, rule matrix, ambiguity register |
| FR-04 | Parameter config with CANON / ASSUMPTION / IMPL labels |
| FR-05 | Tick → 5s / 1m bar pipeline (UTC, gaps explicit) |
| FR-06 | Python reference engine with unit and lookahead tests |
| FR-07 | Signal ledger with a reason code for every no-trade |
| FR-08 | Execution simulator with bid/ask, slippage, costs |
| FR-09 | Signal parity report against course examples |
| FR-10 | Baseline metrics, temporal validation, ablations, walk-forward, Monte Carlo |
| FR-11 | Pine strategies + library; indicator and alerts after validation |
| FR-12 | Journal / screenshot workflow comparing real trades to model signals |

### Non-functional

- **Reproducibility:** pinned tools, file hashes, frozen model versions
- **Traceability:** rule → evidence → timestamp; parameter → evidence or open question
- **Privacy & licensing:** no market data, course material or keys in git
- **Cost control:** paid data only after an approved quote

---

## Data

| Source | What | Role | State |
|---|---|---|---|
| Dukascopy (free) | Spot gold + dollar index ticks | Primary data, 5-second bars | Test-case days downloading |
| Databento ($66.44) | GC + DX futures, 1-min, 2018-2026 | Cross-check with real volume | Downloaded |
| TradingView export | FOREXCOM:XAUUSD, TVC:DXY | Exact match to Tom's charts | Optional |

Course example days (Oct-Nov 2025) sit in the holdout and are used **only for parity**, never for performance or tuning.

---

## Roadmap (30 phases, 5 stages)

### A. Knowledge base (phases 0-8): ✅ done
- 0 Discovery · 1 Video ingestion · 2-5 Extraction, glossary, rule matrix, ambiguity register: **done**
- 6-7 Journal research & trade database: **draft**
- 8 Machine specs: **done, awaiting review**

### B. Data & engine (9-13): 🟡 in progress
- 9 Historical data pipeline: **in progress**
- 10 DXY context module
- 11-12 Python reference engine (CBR15, CBR1H)
- 13 **Parity check against Tom's 3 course examples** (gate)

### C. Baseline evidence (14-19)
- 14 Backtest runner (Trader.dev down → PineTS planned)
- 15-16 Baseline backtests + temporal validation
- 17-19 Regime analysis, confluence ablations, 15m × 1h interaction

### D. Robustness (20-25)
- 20-23 Limited parameter research, walk-forward, Monte Carlo, overfitting log
- 24-25 Journal-derived features, quality score (only if validated)

### E. Product (26-30): only if the edge holds
- 26-28 Indicator, alerts, signal ledger
- 29-30 Screenshot journal workflow, performance reports

---

## Validation gates (proposed, need owner sign-off)

1. **Faithful implementation:** the engine reproduces Tom's taught setups; every mismatch is classified.
2. **Baseline shows something:** positive expectancy after costs in development, with the same sign in validation.
3. **Robust edge:** walk-forward stays positive, the bootstrap confidence interval excludes zero, no single year carries the result, and drawdowns are survivable. The holdout confirms once.
4. **Indicator worth building:** only rules that proved themselves out-of-sample go in.

> A "no edge" result at any gate is a valid end, not a cue to keep tweaking.

---

## Current status

| Metric | Value |
|---|---|
| Course videos ingested | 73 (~15.2 h) |
| Core evidence records | 151 |
| Candidate records | 258 |
| Tests passing | 373 |
| Open questions tracked | 21 |
| Data spend | $66.44 (Databento) |

- **Commits:** `95b4794` knowledge base · `ff9fa1b` machine specs (local, not pushed)
- **Databento:** GC 3,036,783 and DX 2,122,629 one-minute bars; issues logged (GC roll jumps median $16.30, DX off-market publisher, 2 zero-price bars)
- **Dukascopy:** decoder verified exactly (285,935 ticks); Oct 20-22 gold saved with 0 duplicate or bad-spread ticks; resuming after server errors
- **Blocked:** Trader.dev MCP server returns 502 on every path
- **Next:** finish test-case data → compare spot vs futures → engine building blocks → parity check

---

## Key risks

| Risk | Mitigation |
|---|---|
| Swing points are intuitive for Tom; ours may not match his eye | ATR zig-zag with a declared range; sensitivity tests; parity gate |
| "High volume" / "decisive" can't be quantified | Recorded as diagnostics; become filters only if they prove useful |
| Overfitting from many variants | Pre-declared ranges, hypothesis log, chronological splits, single-use holdout |
| Feed differences (FOREX.com vs Dukascopy; TVC:DXY vs DXY CFD) | Measure on test-case days; optional TradingView export |
| Pine can't do 5-second entries | Declared simplification; quantify the difference |
| Small gold targets make costs decisive | Bid/ask fills, real spreads, rollover exclusion, results after costs |
| Vendor outages (Dukascopy, Trader.dev) | Cached, resumable downloads; local runners |

---

## Open questions that still matter

| ID | Question | Current handling |
|---|---|---|
| OQ-01 | What counts as a swing high/low? | ATR zig-zag, k ∈ {2, 3, 4} |
| OQ-02 | How range vs trend is measured | Tom's 75% / 50% thresholds; median of corrections |
| OQ-07 | Is a level required for reversals? | Two variants (with / without) |
| OQ-08 | What "high volume" means | Diagnostics only in V1 |
| OQ-11 / 12 | Stop buffer; 50% target vs 1:1 vs next level | Buffer range declared; target variants tested separately |
| OQ-13 | DXY as confluence, veto or timing trigger? | Not in baseline; each tested separately |
| OQ-21 | Trend: hard no-trade or quality downgrade? | Hard filter in V1; downgrade tested separately |

Full register: `docs/strategy/open-questions.md`
