# CBR Model: PRD Summary

**Doc:** CBR-PRD-001 · **Version:** v1.0 · 2026-09-14 · **Status:** Active (Phase 9 PASS WITH CONCERNS · G1 approved with conditions · Phase 10 authorized) · **Instruments:** XAUUSD + DXY
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
| D11 | AC-11 split: AC-11A (16-day stratified spot-pipeline proof, required for Phase 9) + AC-11B (full spot history, deferred); failures classified; baseline feed (OQ-24) open until parity and cross-feed agreement, frozen before Phase 14, never chosen by profitability |
| D12 | Phase 9 rulings: DXY 2020-03-09 20h = DATA_ERROR → MISSING, flagged by detector `DXY_CFD_MISSING_WHILE_DX_ACTIVE`; DXY 2019-03-11 00h stays UNEXPLAINED → MISSING; new class REFERENCE_UNAVAILABLE; `cause_status` (unproven causes never used as evidence); candle-file high/low = hard safeguard before Phase 14; 1m/5s DXY structure not validated. Record: `docs/governance/g1-approval.md` |
| D13 | Backtesting.py enters in **Phase 14B** as a secondary execution, standard-metrics, visualization and parity layer. The Phase 14A custom simulator is authoritative for execution; the CBR reference engine is authoritative for signals. Signal contract is immutable; parity thresholds pre-registered; no `optimize()` or parameter search in Phases 14-16. Plan: `docs/architecture/phase14-execution-architecture.md` |
| D14 | Phase 14 plan approved, not implemented; Backtesting.py not a dependency. OQ-28 open (contract carries canonical stop inputs, not an executable stop); OQ-29 open (5s CBR1H preserved); OQ-25 decision package due before Phase 11; OQ-30 licensing review before 14B. Phase 10 continues |
| D15 | Phase 10 accepted (PASS WITH CONCERNS, G10). OQ-31 open with preference B (label, don't exclude; ALL vs FULL-DXY diagnostic only). DXY daily unavailability = known limitation, `DXY_AVAILABLE = false`, no directional meaning. Engineering thresholds stay IMPL. OQ-25 package before Phase 11 |
| D16 | OQ-25 resolved (CBR-DEC-025): **STRUCTURE price = tick-derived mid, EXECUTION price = tick-derived bid/ask**, never one series for both; access guards and STRUCTURE/EXECUTION labels in schemas, manifests and reports. V-1 FOREXCOM export required before Phase 13 passes. Full tick history deferred (OQ-33). Phase 11 approved on the downloaded tick days. Candle files and GC not canonical for extremes |
| D17 | Phase 11 accepted (PASS WITH CONCERNS, G11); CBR15 not baseline-eligible. OQ-35/37/38 resolved (stop anchor through activation/fill; unresolved trend direction = context failure; early type 3 cancelled). OQ-34 open until Phase 12; OQ-36 interpretation not approved (evidence package). Phase 12 authorized |
| D18 | Phase 12 accepted (PASS WITH CONCERNS, G12); **Phase 13 not authorized**. Evidence packages for OQ-36, 39-43; Phase 12 tolerances and "closest to Tom" selection rejected; independent tolerances and deterministic selection pre-registered before the final run; BASELINE-SPEC vs STRICT COURSE parity with a 7-class mismatch policy; M15-HTF-01 signal vs execution state (`HTF_FILL_STATE = NOT_EVALUATED`); readiness checklist `docs/governance/phase13-readiness.md` |

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
| FR-08 | Authoritative execution simulator (14A): frozen signals only; bid/ask fills (long: ask in, bid out; short: bid in, ask out); spread, slippage, costs; rollover; missing data; same-bar and gap rules; gross and net R; deterministic |
| FR-08b | Backtesting.py adapter (14B): same frozen signals; thin strategy; standard stats, trade table, equity, interactive HTML; parity report vs 14A with every mismatch classified; run manifest |
| FR-08c | Signal contract `cbr-signal.v1` between the engine and every execution backend; immutable during execution |
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
| Dukascopy (free) | Spot gold ticks (canonical, D16) + dollar index 1m bid/ask candles | Gold ticks → STRUCTURE (mid) and EXECUTION (bid/ask) bars; DXY candles → context (open/close) | Tick days stored: 16 sample + 7 fixture-period days; full tick history **deferred** (OQ-33). Candle-file mid highs/lows never canonical (D16-6) |
| Databento ($66.44) | GC + DX futures, 1-min (GC 2018-2026; DX from 2018-12-26) | Cross-check with real volume | Downloaded. No DX reference before 2018-12-26 (REFERENCE_UNAVAILABLE) |
| TradingView export | FOREXCOM:XAUUSD, TVC:DXY | Exact match to Tom's charts; independent reference for 1m/5s DXY structure | Optional; needed if fine DXY structure is ever used (OQ-26) |

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

### B. Data & reference engines: phases 9-13 🟡 (9 ✅ with concerns)
- **9 Historical data pipeline:** **PASS WITH CONCERNS** (2026-09-14, after owner ruling D12); **G1 approved with conditions**
- **10 DXY context module: PASS WITH CONCERNS, accepted (D15, G10)** (CBR-ACC-010, `reports/phase10-dxy-context.md`). Causal quote + last-closed/forming 15m and 1h direction with state, confidence and reason codes; missing stays missing; hindsight vendor-gap mask kept separate (OQ-31); no DXY rule or filter. 
- **11 CBR15 Python reference engine: PASS WITH CONCERNS, accepted (D17, G11); not baseline-eligible** (`src/cbr/engine/cbr15.py`, `docs/engine/cbr15-implementation-map.md`, `reports/phase11-cbr15-engine.md`). STRUCTURE bars only; causal and deterministic; every candidate's rule outcomes in the ledger. Rulings D17: OQ-35/37/38 resolved; OQ-34 open until Phase 12; OQ-36 interpretation not approved (evidence package required)
- **12 CBR1H Python reference engine: PASS WITH CONCERNS, accepted (D18, G12)** (`src/cbr/engine/cbr1h.py`, `docs/engine/cbr1h-implementation-map.md`, `reports/phase12-cbr1h-parity.md`). Causal hourly state exposed for M15-HTF-01. Phase 12 parity tolerances and selection were rejected (D18) and aren't evidence. Model B reproduces none
- **13 Tom ↔ Python parity gate: NOT READY** (checklist `docs/governance/phase13-readiness.md`, 0/20 items; protocol `docs/governance/phase13-parity-protocol.md` v0.1 proposed; evidence packages in `docs/decisions/oq36-*`, `oq39-*`, `oq40-42-*`). The engine must reproduce the taught examples before any performance research. **V-1 hard requirement (D16-3):** tick-mid structure compared with a FOREXCOM:XAUUSD export on the course-example windows; material differences reopen OQ-25

### C. Untouched baselines: phases 14-16
- **Before 14:** define the canonical historical OHLC source for swings, range extremes, extension extremes, stops and sweeps (OQ-25, hard precondition, D12-5); complete the DXY DST/reopen availability diagnostic (OQ-27); freeze the baseline data feed (OQ-24: spot / futures / hybrid) on fidelity, signal agreement, structure agreement, availability, execution realism, 5s feasibility, reproducibility and known distortions, **never profitability**. If futures are chosen, the cross-feed signal-agreement requirement (G2b) must pass; if spot, AC-11B must be complete.
- **14A Authoritative custom execution simulator:** consumes frozen signals; bid/ask fills; spread, slippage, costs; rollover; missing data; same-bar and gap rules; ledger with reason codes; gross/net R; holdout lock. Gate G14A
- **14B Backtesting.py adapter, parity and visualization:** same frozen signal set; thin strategy (no CBR logic); standard stats, trade table, equity, interactive HTML; pre-registered parity vs 14A (membership, direction, timestamps, stop/target spec = 100%; every execution mismatch classified); pinned version; licence review (OQ-30). Gate G14B (PASS / PASS WITH CONCERNS / FAIL). **Not built before Phases 10-13 are complete**
- 15 Untouched CBR1H baseline
- 16 Untouched CBR15 baseline (**frozen; no optimization before this**; `Backtest.optimize()` prohibited in Phases 14-16)

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
| G1 Data ✅ | 9 | CBR-ACC-009 v2.1: AC-01…AC-10 + AC-11A; every failure classified; AC-11B may remain a concern. **Approved with conditions 2026-09-14** (`docs/governance/g1-approval.md`) | Owner |
| G2 Faithful implementation | 13 | Engine reproduces taught examples on spot; every mismatch classified; **V-1 FOREXCOM export check passed** (D16-3) | Owner |
| G2b Cross-feed signal agreement | 13/14 | Engine run on spot and GC/DX over the 16 AC-11A sample days yields the same setups (direction, hour, entry window) at a rate pre-declared before measurement. Required before futures data can support any baseline performance claim | Owner |
| G2d Canonical extremes source ✅ | pre-14 | **Decided D16 (tick mid structure, tick bid/ask execution).** Original condition: OQ-25 decided: extreme-sensitive logic uses tick-built bars or another validated source, or candle-file highs/lows are shown quantitatively not to change signal membership or material execution results | Owner |
| G2c Baseline feed frozen | pre-14 | OQ-24 decided on the owner's non-profitability criteria and recorded | Owner |
| G14A Authoritative simulator | 14A | Fill-rule unit tests, same-bar and gap fixtures, determinism hash, holdout lock, hand-verified execution on the parity examples (no performance statistics) | Owner |
| G14B Backtesting.py adapter | 14B | CBR-ARCH-014 §9: pinned version; adapter tests; signal membership, direction, entry-time and stop/target-spec parity 100%; every execution mismatch classified; deterministic reports; no rule changes; same frozen signal set as 14A | Owner |
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

_As of 2026-09-14, after owner ruling D12 and the Phase 9 acceptance rerun (`reports/phase9-data-acceptance.md`, CBR-ACC-009 v2.1)._

| Metric | Value |
|---|---|
| Course videos ingested | 73 (~15.2 h) |
| Core evidence records | 151 |
| Candidate records | 258 |
| Tests passing | 460 (+1 skipped until Phase 14A) |
| Open questions tracked | 43 |
| Data spend | $66.44 (Databento) |

### Phase 9: **PASS WITH CONCERNS** · G1 approved with conditions

| Criterion | Status |
|---|---|
| AC-01…AC-06, AC-08, AC-10 | MET (AC-06 now also checks the candle high/low error bound) |
| AC-07 gaps | MET WITH CONCERNS: only classified or detector-flagged missing source data; 0 pipeline errors |
| AC-09 fixture feed comparison | MET WITH CONCERNS |
| AC-11A 16-day sample | MET WITH CONCERNS |
| AC-11B full spot history | DEFERRED: 16 / 2,192 weekdays per instrument |

51 failures, all classified and preserved: 29 EXPECTED_FEED_DIFFERENCE, 18 EXPECTED_MARKET_BEHAVIOR, 2 REFERENCE_UNAVAILABLE,
1 DATA_ERROR (ruled MISSING), 1 UNEXPLAINED_FEED_DIFFERENCE (ruled MISSING). Cause status: 18 established, 31 hypothesized,
2 unknown.

**Concerns carried forward:**
- **DXY missing data.** The detector `DXY_CFD_MISSING_WHILE_DX_ACTIVE` flags 7 periods on the checked days: both ruled hours, the Monday 00h UTC blocks in EST (2021-02-01, 2023-11-06, 2025-11-10), Thanksgiving 2022 from 17:59 to 21:57 UTC, and Sunday 2025-11-09 from 23:00 UTC. All are MISSING.
- **DXY timeframes.** 15m/1h direction is supported. 1m/5s DXY structure is not validated (OQ-26).
- **No DX reference before 2018-12-26** (REFERENCE_UNAVAILABLE).
- **Candle-file highs/lows are not authoritative extremes.** Per tick window: up to 28 artificial minutes (XAUUSD) and 67 (DXY 2018); largest errors $0.425 and 0.3185. The candle-only flag misses most of them. Hard precondition before Phase 14 (OQ-25, G2d).
- **2020-06-17 gold.** 1m corr 0.920 with ~$3.7 basis drift; cause HYPOTHESIZED.
- **OQ-27.** The DST-Monday DXY diagnostic is still pending (required before DXY availability assumptions are frozen).

### Phase 10: **PASS WITH CONCERNS** (accepted, D15)

All CBR-ACC-010 criteria met on 24 days (8 fixture + 16 sample): UTC, truncation and future-mutation causality
(300 seeded times per day), no forward-fill, hindsight isolation, no DX substitution, closure labelling, direction
recomputation, determinism, reference flags. Last-closed direction agreement vs DX: 15m 98.4%, 1h 98.8%
(threshold 80%). Concerns: the causal quote persists up to 10 min into a vendor outage (OQ-31); winter Asia hour 1
(00:00-01:00 UTC) has no DXY context because the CFD doesn't quote 18:00-20:00 New York; thinner 2018-2019 coverage;
IMPL thresholds validated on 24 days only; no DXY extremes (OQ-25).

**Phase 10 accepted (D15, G10: `docs/governance/g10-approval.md`). OQ-25 resolved (D16): STRUCTURE = tick mid, EXECUTION = tick bid/ask; guards in `src/cbr/data/price_series.py`. Phase 11 accepted (D17, G11); CBR15 not baseline-eligible (OQ-36 evidence package, hourly veto). Phase 12 accepted (D18, G12). Phase 13 NOT READY: evidence packages for OQ-36/39-43 delivered, awaiting owner rulings; parity protocol proposed; V-1 export outstanding.** Full tick history deferred (OQ-33); V-1 required before Phase 13. Phase 14 is
planned only (`docs/architecture/phase14-execution-architecture.md`). Not authorized: baseline profitability testing,
OQ-24 via performance, holdout P&L, Phase 17, Backtesting.py implementation.

- **Commits:** local only, not pushed
- **Blocked:** Trader.dev MCP server returns 502 on every path

---

## Key risks

| Risk | Mitigation |
|---|---|
| Swing points are intuitive for Tom; ours may not match his eye | ATR zig-zag with a declared range; sensitivity tests; parity gate |
| "High volume" / "decisive" can't be quantified | Recorded as diagnostics; become filters only if they prove useful |
| Overfitting from many variants | Pre-declared ranges, hypothesis log, chronological splits, single-use holdout |
| Feed differences (FOREX.com vs Dukascopy; TVC:DXY vs DXY CFD) | Measure on test-case days; optional TradingView export |
| Pine can't do 5-second entries | Declared simplification; quantify the difference |
| Backtesting.py semantics differ (single price series, relative constant spread, no slippage, entry-bar SL/TP deferred, missing rows invisible, chart resampling above 10,000 bars) | Custom simulator authoritative; approximations labelled and quantified; every mismatch classified (CBR-ARCH-014 §6-7) |
| Visualization layer tempts parameter search | `optimize()` prohibited in Phases 14-16; test guard; frozen signal set shared with 14A |
| Small gold targets make costs decisive | Bid/ask fills, real spreads, rollover exclusion, results after costs |
| Vendor outages (Dukascopy, Trader.dev) | Cached, resumable downloads; local runners |
| Vendor data holes (e.g. DXY CFD hour empty while DX trades) | Detector `DXY_CFD_MISSING_WHILE_DX_ACTIVE`; MISSING, never filled; reason code and lower confidence on affected setups |
| Synthetic candle-file extremes distort swings, sweeps and stops | `hl_method` tag on every bar file; tick-built extremes for parity; canonical source decided before Phase 14 (OQ-25, G2d) |
| Fine-grained DXY structure unvalidated | Use 15m/1h DXY context only until an independent reference exists (OQ-26) |

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
| OQ-25 | Canonical OHLC source for extremes | **Resolved D16:** tick mid STRUCTURE, tick bid/ask EXECUTION; V-1 before Phase 13 |
| OQ-34 | CBR15 hourly veto depends on the CBR1H engine | Signal-state veto from ARMED CBR1H signals; FILLED part `EXECUTION_DEPENDENT`, `HTF_FILL_STATE = NOT_EVALUATED` (D18-11) |
| OQ-35 | Stop anchor | **Resolved D17-2:** most adverse STRUCTURE extension extreme through activation/fill; separate fields |
| OQ-36 | COND-03 "prior working setup" meaning | Evidence package delivered: "played out" undefined in Level 1; owner decision (candidate assumption C′) |
| OQ-37 | Trending range with no direction | **Resolved D17-4:** TREND_DIRECTION_UNRESOLVED context failure |
| OQ-38 | Type 3 break before minute 7.5 | **Resolved D17-5:** TYPE3_RESOLVED_TOO_EARLY; no resurrection |
| OQ-39 | CBR1H entry trigger: spec 1m HILO / fractal vs Tom's 5s shift in all three examples | Evidence package: strong for 5s shift as trigger (two distinct variants); owner decision |
| OQ-40 | Condition window across weekend closures (CX-LT3-2 → UNDEFINED) | Evidence package: `CONDITION_WINDOW_UNRESOLVED`; tradable time is the assumption candidate |
| OQ-41…43 | CBR1H readings: prev-15m reference, q30 veto timing, HVCS end bar | Evidence packages: Q−1 broken by current candle (strong); veto at structure break (moderate); HVCS adjacent to shift (moderate); owner decisions |
| OQ-33 | Historical tick acquisition strategy (full / targeted / other source / staged) | Deferred until after Phases 11-13 (D16-4); never by profitability |
| OQ-26 | Independent reference for 1m/5s DXY structure? | Open data dependency; only 15m/1h DXY context used meanwhile |
| OQ-27 | DXY CFD availability at DST-transition Mondays / weekly reopen | Diagnostic approved; required before DXY availability assumptions are frozen |
| OQ-28 | Stop resolved at fill (current spec) or frozen at decision? | Decide in Phase 11, before Phase 13 |
| OQ-29 | CBR1H execution clock: 5s (spec) or 1m? | 5s unless Phase 13 evidence + owner spec revision |
| OQ-30 | Backtesting.py is AGPL-3.0; the repo is public | Owner licence review before Phase 14B; 14A unaffected |
| OQ-31 | Ledger use of the hindsight DXY vendor-gap mask (label, exclude, or report only)? | Owner decision before baselines; engine reads causal fields only |
| OQ-24 | Baseline feed: Dukascopy spot, GC/DX futures, or hybrid? | Open until Phase 9 validation, engines, Phase 13 parity and cross-feed agreement exist; frozen before Phase 14; never chosen by profitability |

Full register: `docs/strategy/open-questions.md`
