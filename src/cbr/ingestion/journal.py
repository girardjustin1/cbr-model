"""TomTradesJournal catalog: public metadata + YouTube captions as timestamped transcripts.

Usage:
    .venv/bin/python -m cbr.ingestion.journal

Level-2 evidence only. Captions are auto-generated where the uploader provided none;
the source of each transcript is recorded.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHANNEL = "https://www.youtube.com/@TomTradesJournal/videos"
OUT_DIR = ROOT / "research" / "journal"
TRANSCRIPTS = ROOT / "research" / "transcripts" / "journal"
RAW = ROOT / ".cache" / "journal"


def _yt(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["yt-dlp", *args], capture_output=True, text=True, check=False)


def _fmt(ts: float) -> str:
    s = int(ts)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def _json3_segments(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    segs = []
    for ev in data.get("events", []):
        text = "".join(s.get("utf8", "") for s in ev.get("segs", []) or []).strip()
        if text and text != "\n":
            start = ev["tStartMs"] / 1000
            segs.append({"start": round(start, 3),
                         "end": round(start + ev.get("dDurationMs", 0) / 1000, 3),
                         "text": " ".join(text.split())})
    return segs


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ids = _yt("--flat-playlist", "--print", "%(id)s", CHANNEL).stdout.split()
    catalog = []
    for vid in ids:
        url = f"https://www.youtube.com/watch?v={vid}"
        meta_file = RAW / f"{vid}.info.json"
        if not meta_file.exists():
            r = _yt("--skip-download", "--write-info-json", "--write-subs", "--write-auto-subs",
                    "--sub-langs", "en.*,en", "--sub-format", "json3",
                    "-o", str(RAW / "%(id)s.%(ext)s"), url)
            if r.returncode != 0:
                print(f"FAILED {vid}: {r.stderr.strip().splitlines()[-1:]}")
                continue
        meta = json.loads(meta_file.read_text())

        manual = meta.get("subtitles", {}) or {}
        subs = sorted(RAW.glob(f"{vid}.en*.json3"))
        sub_file = subs[0] if subs else None
        source = None
        if sub_file:
            lang = sub_file.name.split(".")[1]
            source = "uploader_captions" if lang in manual else "youtube_auto_captions"
            segs = _json3_segments(sub_file)
            (TRANSCRIPTS / f"J-{vid}.json").write_text(json.dumps(
                {"video_id": f"J-{vid}", "url": url, "title": meta["title"],
                 "transcript_source": source, "segments": segs}, indent=1) + "\n")
            (TRANSCRIPTS / f"J-{vid}.md").write_text(
                f"# {meta['title']}\n\n{url} · uploaded {meta.get('upload_date')} · "
                f"source: {source}\n\n"
                + "\n".join(f"[{_fmt(s['start'])}] {s['text']}" for s in segs) + "\n")

        catalog.append({
            "journal_video_id": f"J-{vid}",
            "url": url,
            "title": meta["title"],
            "upload_date": meta.get("upload_date"),
            "duration_sec": meta.get("duration"),
            "description": meta.get("description"),
            "chapters": meta.get("chapters"),
            "transcript_path": f"research/transcripts/journal/J-{vid}" if sub_file else None,
            "transcript_source": source,
            # Filled in during Phase 6 review, from transcript content, never from the title.
            "relevance": "unreviewed",
        })
        print(f"{vid} {meta.get('upload_date')} {source or 'NO CAPTIONS':<22} {meta['title']}")

    (OUT_DIR / "index.json").write_text(json.dumps(
        {"channel": CHANNEL, "fetched_utc": datetime.now(UTC).isoformat(),
         "videos": catalog}, indent=2) + "\n")
    print(f"wrote research/journal/index.json ({len(catalog)} videos)")


if __name__ == "__main__":
    main()
