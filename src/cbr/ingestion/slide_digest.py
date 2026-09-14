"""Condense noisy slide OCR into one readable line per distinct slide statement.

Usage:
    .venv/bin/python -m cbr.ingestion.slide_digest

Zoomed-out Miro frames OCR into garbled near-copies of the same sentence. A line is kept only when
most of its words are dictionary words (or known method jargon), and a garbled line is dropped in
favour of its cleanest near-duplicate. The raw OCR jsonl stays the source of record; the digest
lists each kept line with its first-seen timestamp so it can be traced back to a frame.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORDS = {w.strip().lower() for w in Path("/usr/share/dict/words").read_text().splitlines()}
JARGON = {
    "cbr", "cbrs", "cboe", "aoi", "aois", "er", "oe", "mtf", "ltf", "htf", "hilo", "hvcs", "dxy",
    "xauusd", "ifs", "bos", "choch", "fvg", "rr", "sl", "tp", "tp1", "tp2", "ny", "am", "pm",
    "asia", "london", "comex", "1m", "5m", "15m", "30m", "1h", "4h", "5s", "15s", "wick", "wicks",
    "pullback", "pullbacks", "timeframe", "timeframes", "breakeven", "entries", "setups", "hourly",
}
MIN_REAL_WORD_RATIO = 0.8
NEAR_DUPLICATE = 0.8


def _tokens(line: str) -> list[str]:
    return re.findall(r"[A-Za-z]+|\d+(?:[.:]\d+)?%?", line)


def quality(line: str) -> float:
    toks = _tokens(line)
    if len(toks) < 3:
        return 0.0
    good = sum(1 for t in toks if t[0].isdigit() or t.lower() in WORDS or t.lower() in JARGON)
    return good / len(toks)


def digest(jsonl: Path) -> list[tuple[str, str]]:
    kept: list[tuple[str, str, float]] = []  # (first_seen, line, quality)
    for rec in (json.loads(x) for x in jsonl.read_text().splitlines()):
        for line in rec["new_lines"]:
            q = quality(line)
            if q < MIN_REAL_WORD_RATIO:
                continue
            clean = re.sub(r"^[•*·\-\s]+", "", line).strip()
            for i, (t, existing, eq) in enumerate(kept):
                if difflib.SequenceMatcher(None, clean.lower(), existing.lower()).ratio() >= NEAR_DUPLICATE:
                    if q > eq:
                        kept[i] = (t, clean, q)  # keep earliest time, cleanest wording
                    break
            else:
                kept.append((rec["t"], clean, q))
    return [(t, ln) for t, ln, _ in kept]


def main() -> None:
    for jsonl in sorted((ROOT / "research" / "slides").glob("*/*.jsonl")):
        lines = digest(jsonl)
        out = jsonl.with_suffix(".digest.md")
        out.write_text(
            f"# Slide digest: {jsonl.stem}\n\nFiltered OCR (raw: {jsonl.name}). "
            "`[time]` = first seen; verify wording against the frame before quoting as a rule.\n\n"
            + "\n".join(f"[{t}] {ln}" for t, ln in lines) + "\n")
        print(f"{jsonl.stem}: {len(lines)} lines")


if __name__ == "__main__":
    main()
