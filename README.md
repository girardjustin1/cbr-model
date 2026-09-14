# CBR Model

Research implementation of the **CBR (Candle Behavior Reversal)** trading methodology, with 15-minute and
1-hour models, for **XAUUSD** with DXY confluence.

The goal is to find out whether the method has a repeatable, robust edge and which conditions define it, not
to maximize a historical win rate.

## Status

**Milestone 1: Strategy knowledge base** (in progress; no backtests or indicators yet)

| Deliverable | Location |
|---|---|
| Video inventories: 15m 8, 1h 26 (3 duplicates), Phase 1 14, Phase 2 25 (~15.2 h unique) | `research/video_index/{15min,hourly,phase1,phase2}.json` |
| Course examples, long calls, Phase 1/2 candidate records | `research/examples/` |
| Databento GC + DX 1m bars (local, manifest with known issues) | `data/raw/databento/` |
| Timestamped transcripts (local only) | `research/transcripts/` |
| On-screen slide text, OCR (local only) | `research/slides/` |
| Evidence records (verbatim quote + timestamp per rule) | `research/evidence/strategy_evidence.jsonl` |
| Transcription corrections | `research/evidence/transcription_corrections.md` |
| 15m / 1h written specs | `docs/strategy/15min-cbr-spec.md`, `docs/strategy/1h-cbr-spec.md` |
| Glossary | `docs/strategy/glossary.md` |
| Rule matrix (15m vs 1h, baseline scope) | `docs/strategy/rule-matrix.md` |
| Ambiguity register + questions | `docs/strategy/open-questions.md` |
| Journal catalog (TomTradesJournal, Level 2) | `research/journal/` |
| Tooling report (Trader.dev + alternatives) | `docs/architecture/tooling-report.md` |
| Backtest architecture | `docs/architecture/backtest-architecture.md` |
| Data requirements | `docs/architecture/data-requirements.md` |
| TradingView architecture | `docs/architecture/tradingview-architecture.md` |

## Evidence hierarchy

1. **Level 1:** local course videos (`references/`), the only source that defines rules.
2. **Level 2:** TomTradesJournal videos: clarify and illustrate, never silently redefine.
3. **Level 3:** backtest discoveries, always labelled `RESEARCH-DERIVED`.

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]" ocrmac pillow imagehash
.venv/bin/python -m cbr.ingestion.videos index        # manifest (hashes, durations, duplicates)
.venv/bin/python -m cbr.ingestion.videos transcribe   # mlx-whisper large-v3, local, resumable
.venv/bin/python -m cbr.ingestion.slides              # frame sampling + macOS Vision OCR, local
.venv/bin/python -m cbr.ingestion.slide_digest        # readable slide text
.venv/bin/python -m cbr.ingestion.journal             # journal catalog + captions
.venv/bin/python -m pytest                            # evidence integrity tests
```

Requires macOS (Apple Silicon for mlx-whisper; Vision framework for OCR), ffmpeg, yt-dlp.

## Not in git

`references/` (course videos), `research/transcripts/`, `research/slides/`, `research/frames/`, `data/`, `.env`,
`.mcp.json`. The course material is copyrighted and this repository is public.
