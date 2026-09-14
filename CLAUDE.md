# CLAUDE.md

Guidance for Claude Code in this repository.

## What this project is

A research implementation of the CBR trading methodology (15-minute and 1-hour models) for
XAUUSD, with DXY confluence where the source material specifies it. The question is whether the
method has a repeatable edge and which conditions define it, not how high a backtest can go.

**Instrument scope (user decision, 2026-09-14): XAUUSD and DXY only.** The course also uses USDJPY,
a "gold spread" composite and silver correlation. Catalog those passages, but don't build rules,
data pipelines or parity fixtures for them.

## Evidence hierarchy (never blur these)

1. **Level 1, canonical:** local videos in `references/15min cbr`, `references/hourly cbr` and the
   prerequisite course `references/phase 2` (defines shifts, HILO, MS alignment, correlation).
   Only these define the strategy. Videos flagged `provenance_unconfirmed` in
   `config/ingestion.yaml` are cited but marked until the user classifies them.
2. **Level 2, strategy-in-action:** TomTradesJournal videos. May clarify or illustrate; may not
   silently redefine a Level 1 rule. Conflicts go to `docs/strategy/open-questions.md`.
3. **Level 3, research-derived:** anything learned from backtests. Always labelled
   `RESEARCH-DERIVED`, never `ORIGINAL CBR RULE`.

## Research governance (CBR-GOV-001, `docs/governance/research-governance.md`)

- **Claude Code is the Research Engineer.** Implement frozen specs, run only **owner-approved, registered**
  experiments (`research/experiments/registry.yaml`), keep tests, the signal ledger and reports reproducible.
- **Never invent trading rules** because they improve historical results. Never modify a registered experiment
  after it starts; a change is a new experiment ID.
- **Fable** (Research Director) proposes; **Astra** (Independent Quant Auditor) rules; the **owner** approves.
  Phase 17 review only after the untouched baselines (Phases 15-16) exist; it stops at an owner-approval report.
- **Holdout 2025-01-01 → 2026-08-31 is single-use.** No holdout performance may inform any selection. Course-example
  days in it are for implementation parity only. Log every holdout-period data access in
  `research/holdout-access-log.md`.
- TradingView work stays downstream of validation. The Python reference engine is authoritative.

## Rules

- **Do not invent the strategy.** Every rule in a spec cites video id + timestamp. No citation,
  no rule; it goes in the ambiguity register instead.
- **Transcripts are machine output.** Whisper mishears jargon (e.g. "CBR" → "paper"). When a rule
  hinges on a term, check the frame at that timestamp before trusting the word.
- **Ambiguity is registered, not resolved.** Batch questions for the user.
- **No lookahead, no repainting, confirmed bars only.** All timestamps UTC internally.
- **Journal outcomes never define setup validity.** Validity uses information known at entry.
- **Chronological splits only.** Never optimize against the holdout. Log every experiment in
  `research/hypothesis-log.md` before running it.
- **Never overwrite a strategy version.** New behaviour = new version id.
- **Never claim something works without running it.** Paste real output.
- **Secrets:** never print, log or commit API keys (Trader.dev included).
- **Copyright:** `references/`, `research/transcripts/`, `research/frames/` stay out of git.
  The GitHub repo is public. Nothing is pushed without the user's explicit go-ahead.

## Commands

```bash
uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m cbr.ingestion.videos index        # rebuild video manifest
.venv/bin/python -m cbr.ingestion.videos transcribe   # resumable; skips up-to-date transcripts
.venv/bin/python -m cbr.ingestion.journal             # journal catalog + captions
.venv/bin/python -m pytest
.venv/bin/ruff check src tests
```

Python 3.12 venv (mlx-whisper needs it; system Python is 3.14).
