"""Evidence integrity: every rule citation must be traceable to its source.

Transcript quotes must appear verbatim (after whitespace/punctuation normalisation) in the cited
video's transcript. Fragments are separated by "..." and bracketed editorial notes are ignored.
Transcripts are gitignored, so these tests skip on machines without them.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research" / "evidence" / "strategy_evidence.jsonl"
REQUIRED = {"evidence_id", "level", "strategy", "video_id", "start", "end", "concept", "quote",
            "interpretation", "classification", "requirement", "confidence", "needs_frame_check"}


CANDIDATES = sorted((ROOT / "research" / "examples").glob("*candidates.jsonl"))


def _rows(paths: list[Path] | None = None) -> list[dict]:
    return [json.loads(line) for p in (paths or [EVIDENCE]) for line in p.read_text().splitlines()
            if line.strip()]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9%]+", " ", text.lower()).strip()


def test_schema_and_unique_ids():
    rows = _rows()
    ids = [r["evidence_id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        assert REQUIRED <= r.keys(), r["evidence_id"]
        assert r["classification"] in {"OBJECTIVE", "DISCRETIONARY"}
        assert r["requirement"] in {"REQUIRED", "OPTIONAL", "UNKNOWN"}
        assert r["confidence"] in {"HIGH", "MEDIUM", "LOW"}
        assert re.fullmatch(r"\d\d:\d\d:\d\d", r["start"]) and re.fullmatch(r"\d\d:\d\d:\d\d", r["end"])


@pytest.mark.parametrize("row", [r for r in _rows([EVIDENCE, *CANDIDATES])
                                 if r.get("source_type", "transcript") == "transcript"],
                         ids=lambda r: r["evidence_id"])
def test_transcript_quotes_are_verbatim(row):
    lib = {"V15": "15min", "V1H": "hourly", "VP2": "phase2", "VP1": "phase1"}[row["video_id"].split("-", 1)[0]]
    path = ROOT / "research" / "transcripts" / lib / f"{row['video_id']}.json"
    if not path.exists():
        pytest.skip("transcripts are local-only")
    text = _norm(" ".join(s["text"] for s in json.loads(path.read_text())["segments"]))
    for fragment in re.split(r"\.\.\.|\[[^\]]*\]", row["quote"]):
        if len(_norm(fragment)) > 12:
            assert _norm(fragment) in text, f"{row['evidence_id']}: {fragment[:60]!r}"
