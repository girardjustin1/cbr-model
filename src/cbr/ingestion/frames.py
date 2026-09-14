"""Extract chart frames at given timestamps so transcript claims can be checked visually.

Usage:
    .venv/bin/python -m cbr.ingestion.frames V15-gold_dxy 00:01:32 00:02:10 [...]

Writes research/frames/<video_id>/<hh-mm-ss>.jpg (gitignored). Source video is read-only.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CONFIG = yaml.safe_load((ROOT / "config" / "ingestion.yaml").read_text())


def _entry(video_id: str) -> dict:
    for index in (ROOT / "research" / "video_index").glob("*.json"):
        for e in json.loads(index.read_text()):
            if e["video_id"] == video_id:
                return e
    raise SystemExit(f"unknown video_id {video_id}")


def extract(video_id: str, timestamps: list[str], width: int = 1280) -> list[Path]:
    e = _entry(video_id)
    src = ROOT / CONFIG["libraries"][e["strategy_type"]] / e["filename"]
    out_dir = ROOT / "research" / "frames" / video_id
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ts in timestamps:
        out = out_dir / f"{ts.replace(':', '-')}.jpg"
        if not out.exists():
            # -ss before -i seeks by keyframe then decodes to the exact time.
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", ts, "-i", str(src),
                            "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", str(out)],
                           check=True)
        paths.append(out)
    return paths


if __name__ == "__main__":
    for p in extract(sys.argv[1], sys.argv[2:]):
        print(p.relative_to(ROOT))
