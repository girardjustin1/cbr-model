"""On-screen text extraction. The course is taught over a Miro board whose written slides state
rules more precisely than the narration, so slide text is first-class evidence.

Usage:
    .venv/bin/python -m cbr.ingestion.slides [--library 15min|hourly] [--only NAME]

Pipeline: sample a frame every SAMPLE_SEC -> skip frames perceptually identical to the last kept
frame -> macOS Vision OCR (local) -> keep each distinct text line with the first timestamp it
appeared. Outputs research/slides/<library>/<video_id>.{jsonl,md} and kept frames under
research/frames/<video_id>/slides/ (gitignored).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import imagehash
import yaml
from ocrmac import ocrmac
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
LIB_DIRS = yaml.safe_load((ROOT / "config" / "ingestion.yaml").read_text())["libraries"]
SAMPLE_SEC = 2
HASH_DISTANCE_SAME = 6       # phash distance at or below which two frames count as the same view
MIN_CONFIDENCE = 0.5
MIN_LINE_CHARS = 12
# Browser tabs, URL bar and toolbar sit in the top ~9% of a 1080p recording.
TOP_CROP = 0.09
BROWSER_NOISE = re.compile(r"miro\.com|Trading - Miro|Loom|Present|Share|Prop|TradeSim|XAUUSD \d")


def _fmt(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9%]+", " ", text.lower()).strip()


def process(entry: dict) -> None:
    lib = entry["strategy_type"]
    src = ROOT / LIB_DIRS[lib] / entry["filename"]
    out_dir = ROOT / "research" / "slides" / lib
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / f"{entry['video_id']}.jsonl"
    if jsonl.exists():
        print(f"skip {entry['video_id']} (done)")
        return
    frames_dir = ROOT / "research" / "frames" / entry["video_id"] / "slides"
    frames_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"fps=1/{SAMPLE_SEC}",
                        "-q:v", "2", f"{tmp}/%06d.jpg"], check=True)
        frames = sorted(Path(tmp).glob("*.jpg"))
        last_hash, seen_lines, records, kept = None, {}, [], 0
        for i, frame in enumerate(frames):
            ts = i * SAMPLE_SEC
            img = Image.open(frame)
            w, h = img.size
            img = img.crop((0, int(h * TOP_CROP), w, h))
            ph = imagehash.phash(img)
            if last_hash is not None and ph - last_hash <= HASH_DISTANCE_SAME:
                continue
            last_hash = ph
            lines = [
                t.strip() for t, conf, _ in ocrmac.OCR(img, recognition_level="accurate").recognize()
                if conf >= MIN_CONFIDENCE and len(t.strip()) >= MIN_LINE_CHARS
                and not BROWSER_NOISE.search(t)
            ]
            new = [ln for ln in lines if _norm(ln) not in seen_lines]
            if not new:
                continue
            for ln in new:
                seen_lines[_norm(ln)] = ts
            kept += 1
            frame_name = f"{_fmt(ts).replace(':', '-')}.jpg"
            img.save(frames_dir / frame_name, quality=85)
            records.append({"t": _fmt(ts), "sec": ts, "frame": frame_name, "new_lines": new})

    jsonl.write_text("".join(json.dumps(r) + "\n" for r in records))
    (out_dir / f"{entry['video_id']}.md").write_text(
        f"# Slide text: {entry['filename']}\n\n"
        "OCR of on-screen text (macOS Vision). Each block lists lines first visible at that time.\n\n"
        + "\n".join(f"## [{r['t']}] frame {r['frame']}\n" + "\n".join(f"- {ln}" for ln in r["new_lines"])
                    + "\n" for r in records))
    print(f"{entry['video_id']}: {len(frames)} sampled, {kept} frames with new text, "
          f"{len(seen_lines)} distinct lines", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--library", choices=list(LIB_DIRS))
    p.add_argument("--only")
    args = p.parse_args()
    for lib in [args.library] if args.library else list(LIB_DIRS):
        entries = json.loads((ROOT / "research" / "video_index" / f"{lib}.json").read_text())
        for e in sorted(entries, key=lambda x: x["duration_sec"]):
            if e["duplicate_of"] or (args.only and args.only not in e["filename"]):
                continue
            process(e)


if __name__ == "__main__":
    main()
