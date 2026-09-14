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
| D8 | Overextension origin (hour open vs last reset): pre-registered ablation candidate → Phase 17 |
| D9 | Early-shift guard (final push / 15m alignment): pre-registered ablation candidate → Phase 17 |
| D10 | Astra × Fable research governance adopted (CBR-GOV-001) |

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

## Research governance: Astra × Fable (CBR-GOV-001)

Full framework: `docs/governance/research-governance.md`. It adds to all existing controls and replaces none.

| Role | Does | May NOT |
|---|---|---|
| **Fable: Research Director** | Interprets results, proposes market mechanisms, weaknesses, testable hypotheses, ablations, regime dependencies, alternative explanations; may *propose* research-derived features | Change CANON rules · implement · optimize on the holdout · add unexplained parameters · promote features |
| **Astra: Independent Quant Auditor** | Challenges hypotheses; audits hindsight, overfitting, multiple testing, leakage, sample size, statistical validity, parameter selection; rules **APPROVE / APPROVE WITH CONSTRAINTS / REJECT** | Try to make CBR profitable |
| **Claude Code: Research Engineer** | Implements frozen specs, runs approved experiments, keeps tests, ledger and reports reproducible | Invent rules because they improve history · run unregistered experiments · edit an experiment after it starts |
| **Owner** | Final approval: experiment execution, methodology changes, feature promotion, holdout evaluation, indicator composition | none |

**Frozen experiment registry:** `research/experiments/registry.yaml`, schema in `SCHEMA.md`, enforced by a test.
Experiments are registered **before** execution, locked by `spec_hash` once running, and any change needs a new ID.
Research-derived variables carry `classification: RESEARCH-DERIVED`.

---

## Roadmap (revised 2026-09-14)

### A. Knowledge base: phases 0-8 ✅
- 0 Discovery · 1 Video ingestion · 2-5 Extraction, glossary, rule matrix, ambiguity register: **done**
- 6-7 Journal research & trade database: **draft**
- 8 Machine specs: **done, awaiting owner review**

### B. Data & reference engines: phases 9-13 🟡
- **9 Historical data pipeline:** **in progress**
- 10 DXY context / data module
- 11 CBR15 Python reference engine
- 12 CBR1H Python reference engine
- **13 Tom ↔ Python parity gate:** the engine must reproduce the taught examples before any performance research

### C. Untouched baselines: phases 14-16
- 14 Backtest runner and execution simulator
- 15 Untouched CBR1H baseline
- 16 Untouched CBR15 baseline (**frozen; no optimization before this**)

### D. Governed research: phases 17-19
- **17 Astra × Fable pre-experiment review** (only after 15-16):
  - Round 1: independent Fable diagnosis (≤ 10 experiments) and independent Astra audit
  - Round 2: Astra rules on each proposal
  - Round 3: Fable defends, modifies, narrows or withdraws
  - Round 4: Astra final ruling → **STOP** → owner-approval report
- 18 Register owner-approved experiments in the frozen registry
- 19 Run approved experiments (development + validation only). Pre-registered candidates D8 / D9 enter here via Phase 17.

### E. Robustness: phases 20-23
- 20 Chronological validation and parameter sensitivity
- 21 Walk-forward analysis
- 22 Bootstrap confidence intervals and Monte Carlo
- 23 Regime stability, year-by-year, concentration, execution-cost sensitivity

### F. Final review & holdout: phases 24-25
- **24 Astra × Fable post-experiment review:** every finding classified PROMOTE / RESEARCH ONLY / INSUFFICIENT EVIDENCE / REJECT; promotion needs Astra's evidence approval and owner approval; final candidate spec **frozen (hashed)**
- **25 Single-use holdout evaluation** (owner-approved): run once, record whatever happens

### G. TradingView (only after validation): phases 26-30
- 26 Pine strategy parity implementation and Python ↔ Pine parity
- 27 Validated TradingView indicator
- 28 Alerts and forward signal ledger
- 29 Journal / screenshot workflow
- 30 Performance feedback

The Python reference engine is authoritative. LuxAlgo Quant may assist with Pine later, but is never the research source of truth. TRR Forever (D5) is a separate model track after the CBR baselines.

---

## Gates

| Gate | After phase | Pass condition | Decided by |
|---|---|---|---|
| G1 Data | 9 | Historical-data acceptance criteria met (`reports/phase9-data-acceptance.md`) | Owner |
| G2 Faithful implementation | 13 | Engine reproduces taught examples; every mismatch classified | Owner |
| G3 Baselines frozen | 16 | Untouched baselines recorded with hashes; no tuning | Owner |
| G4 Experiments approved | 17 | Astra final rulings + owner approval per experiment | Astra → Owner |
| G5 Candidate frozen | 24 | Only Astra-approved evidence promoted; spec hashed | Astra → Owner |
| G6 Holdout | 25 | One run, result recorded regardless of outcome | Owner |
| G7 Indicator | 26-27 | Python ↔ Pine parity on the frozen candidate | Owner |

> A "no edge" result at any gate is a valid end, not a cue to keep tweaking.

## Holdout policy

- 2025-01-01 → 2026-08-31 is **single-use**. No role or process may see holdout performance while choosing features, filters, thresholds, parameters, models or scores.
- Course-example days inside it are for **implementation parity only**. Every holdout-period data access is logged in `research/holdout-access-log.md`.
- Evaluation runs once, after the candidate is frozen and the owner approves. No retuned model is ever presented as validated.

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
