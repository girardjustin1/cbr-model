"""Local reference-video ingestion: manifest, audio extraction, timestamped transcripts.

Usage:
    .venv/bin/python -m cbr.ingestion.videos index
    .venv/bin/python -m cbr.ingestion.videos transcribe [--library 15min|hourly] [--only NAME]

Source videos are opened read-only and never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CONFIG = yaml.safe_load((ROOT / "config" / "ingestion.yaml").read_text())


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def _audio_md5(path: Path) -> str:
    """Hash of the compressed audio stream; identifies re-muxed copies of one recording."""
    out = _run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a", "-c", "copy",
                "-f", "md5", "-"])
    return out.strip().removeprefix("MD5=")


def _probe(path: Path) -> dict:
    d = json.loads(_run(["ffprobe", "-v", "error", "-show_entries",
                         "format=duration:stream=codec_type,codec_name,width,height",
                         "-of", "json", str(path)]))
    video = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    audio = next((s for s in d["streams"] if s["codec_type"] == "audio"), {})
    return {
        "duration_sec": round(float(d["format"]["duration"]), 2),
        "video_codec": video.get("codec_name"),
        "resolution": f"{video.get('width')}x{video.get('height')}" if video else None,
        "audio_codec": audio.get("codec_name"),
    }


def _slug(name: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", name.lower())).strip("_")


def _index_path(library: str) -> Path:
    return ROOT / CONFIG["index_dir"] / f"{library}.json"


def build_index() -> None:
    for library, rel in CONFIG["libraries"].items():
        prefix = CONFIG["id_prefix"][library]
        entries, seen_audio = [], {}
        # Browser re-download copies ("name (1).mp4") sort after the original.
        paths = sorted((ROOT / rel).glob("*.mp4"),
                       key=lambda p: (re.sub(r" \(\d+\)$", "", p.stem), p.stem))
        for path in paths:
            stat = path.stat()
            audio_md5 = _audio_md5(path)
            entry = {
                "video_id": f"{prefix}-{_slug(path.stem)}",
                "filename": path.name,
                "strategy_type": library,
                **_probe(path),
                "size_bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                "sha256": _sha256(path),
                "audio_md5": audio_md5,
                "duplicate_of": seen_audio.get(audio_md5),
                "provenance_unconfirmed": path.name in CONFIG["provenance_unconfirmed"],
            }
            if entry["duplicate_of"] is None:
                seen_audio[audio_md5] = entry["video_id"]
            entry["transcript_path"] = (
                f"{CONFIG['transcripts_dir']}/{library}/{entry['duplicate_of'] or entry['video_id']}"
            )
            entries.append(entry)
            print(f"{entry['video_id']:<70} {entry['duration_sec']:>8.0f}s"
                  f"{'  dup of ' + entry['duplicate_of'] if entry['duplicate_of'] else ''}")
        out = _index_path(library)
        out.parent.mkdir(parents=True, exist_ok=True)
        _refresh_status(entries)
        out.write_text(json.dumps(entries, indent=2) + "\n")
        print(f"wrote {out.relative_to(ROOT)} ({len(entries)} videos)")


def _refresh_status(entries: list[dict]) -> None:
    for e in entries:
        done = (ROOT / e["transcript_path"]).with_suffix(".json").exists()
        e["transcript_status"] = "complete" if done else "pending"


def _fmt(ts: float, sep: str = ".") -> str:
    ms = round(ts * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _whisper_settings() -> dict:
    return dict(CONFIG["whisper"])


def transcribe(library: str | None, only: str | None) -> None:
    import mlx_whisper  # heavy import; only needed here

    settings = _whisper_settings()
    libraries = [library] if library else list(CONFIG["libraries"])
    for lib in libraries:
        index_file = _index_path(lib)
        entries = json.loads(index_file.read_text())
        # Shortest first: early output to review, long recordings last.
        for e in sorted(entries, key=lambda x: x["duration_sec"]):
            if e["duplicate_of"] or (only and only not in e["filename"]):
                continue
            base = ROOT / e["transcript_path"]
            json_out = base.with_suffix(".json")
            if json_out.exists():
                prior = json.loads(json_out.read_text())
                if prior.get("sha256") == e["sha256"] and prior.get("whisper") == settings:
                    print(f"skip {e['video_id']} (up to date)")
                    continue

            wav = ROOT / CONFIG["audio_cache"] / lib / f"{e['video_id']}.wav"
            wav.parent.mkdir(parents=True, exist_ok=True)
            if not wav.exists():
                src = ROOT / CONFIG["libraries"][lib] / e["filename"]
                _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1",
                      "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])

            print(f"transcribing {e['video_id']} ({e['duration_sec']:.0f}s)...", flush=True)
            t0 = time.time()
            result = mlx_whisper.transcribe(
                str(wav),
                path_or_hf_repo=settings["model"],
                language=settings["language"],
                word_timestamps=settings["word_timestamps"],
                condition_on_previous_text=settings["condition_on_previous_text"],
                hallucination_silence_threshold=settings["hallucination_silence_threshold"],
                initial_prompt=settings["initial_prompt"],
            )
            elapsed = time.time() - t0

            segments = [
                {
                    "id": i,
                    "start": round(s["start"], 3),
                    "end": round(s["end"], 3),
                    "text": s["text"].strip(),
                    "avg_logprob": round(s.get("avg_logprob", 0.0), 4),
                    "no_speech_prob": round(s.get("no_speech_prob", 0.0), 4),
                    "words": [
                        {"w": w["word"], "start": round(w["start"], 3),
                         "end": round(w["end"], 3), "p": round(w.get("probability", 0.0), 3)}
                        for w in s.get("words", [])
                    ],
                }
                for i, s in enumerate(result["segments"])
            ]
            base.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(json.dumps({
                "video_id": e["video_id"],
                "filename": e["filename"],
                "strategy_type": lib,
                "sha256": e["sha256"],
                "duration_sec": e["duration_sec"],
                "whisper": settings,
                "transcribed_utc": datetime.now(UTC).isoformat(),
                "elapsed_sec": round(elapsed, 1),
                "segments": segments,
            }, indent=1) + "\n")
            base.with_suffix(".srt").write_text("".join(
                f"{i + 1}\n{_fmt(s['start'], ',')} --> {_fmt(s['end'], ',')}\n{s['text']}\n\n"
                for i, s in enumerate(segments)
            ))
            base.with_suffix(".md").write_text(
                f"# {e['filename']}\n\nvideo_id: `{e['video_id']}` · strategy: {lib} · "
                f"duration: {_fmt(e['duration_sec'])[:8]}\n\n"
                + "\n".join(f"[{_fmt(s['start'])[:8]}] {s['text']}" for s in segments) + "\n"
            )
            print(f"  done in {elapsed:.0f}s ({e['duration_sec'] / elapsed:.1f}x realtime), "
                  f"{len(segments)} segments", flush=True)

        _refresh_status(entries)
        index_file.write_text(json.dumps(entries, indent=2) + "\n")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index")
    t = sub.add_parser("transcribe")
    t.add_argument("--library", choices=list(CONFIG["libraries"]))
    t.add_argument("--only")
    args = p.parse_args(argv)
    if args.cmd == "index":
        build_index()
    else:
        transcribe(args.library, args.only)


if __name__ == "__main__":
    sys.exit(main())
