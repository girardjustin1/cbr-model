"""Build canonical STRUCTURE and EXECUTION bars from stored XAUUSD tick days (D16).

Usage:
    .venv/bin/python -m cbr.data.canonical_bars

Output (gitignored):
    data/normalized/xauusd/structure_5s|structure_1m/YYYY-MM-DD.parquet   price_role STRUCTURE, hl_method TICK_MID
    data/normalized/xauusd/execution_5s|execution_1m/YYYY-MM-DD.parquet   price_role EXECUTION, hl_method BID_ASK
    data/normalized/xauusd/canonical_manifest.json                        per file: role, method, source tick hash
No bulk download happens here: only tick days already stored are processed (full history deferred, D16-4).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data import price_series as ps

OUT = dk.NORM / "xauusd"
MANIFEST = OUT / "canonical_manifest.json"
BUILDS = (("structure", ps.structure_bars, ps.STRUCTURE, ps.TICK_MID), ("execution", ps.execution_bars, ps.EXECUTION,
                                                                        ps.BID_ASK))


def build(day_files: list | None = None) -> dict:
    ticks_dir = dk.RAW / "xauusd" / "ticks"
    files = sorted(day_files or ticks_dir.glob("*.parquet"))
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"decision": "D16", "files": {}}
    for f in files:
        ticks = pd.read_parquet(f)
        tick_hash = dk._sha256(f)
        for name, builder, role, method in BUILDS:
            for freq, tag in (("5s", "5s"), ("1min", "1m")):
                bars = builder(ticks, freq)
                out = OUT / f"{name}_{tag}" / f.name
                out.parent.mkdir(parents=True, exist_ok=True)
                bars.to_parquet(out)
                manifest["files"][str(out.relative_to(dk.ROOT))] = {
                    "price_role": role, "hl_method": method, "bar": tag, "rows": len(bars),
                    "sha256": dk._sha256(out), "source_ticks": str(f.relative_to(dk.ROOT)), "source_sha256": tick_hash}
    manifest["built_utc"] = datetime.now(UTC).isoformat()
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def load_structure(start: pd.Timestamp, end: pd.Timestamp, bar: str) -> pd.DataFrame:
    """STRUCTURE bars with open time in [start, end), concatenated across stored days, guard-checked."""
    frames = []
    for day in pd.date_range(start.floor("D"), end, freq="D", inclusive="left"):
        p = OUT / f"structure_{bar}" / f"{day.date().isoformat()}.parquet"
        if p.exists():
            frames.append(pd.read_parquet(p))
    if not frames:
        raise FileNotFoundError(f"no STRUCTURE {bar} bars stored for {start}..{end}")
    bars = pd.concat(frames).sort_index()
    return ps.require_structure(bars[(bars.index >= start) & (bars.index < end)])


def main() -> None:
    m = build()
    roles = pd.Series([v["price_role"] for v in m["files"].values()]).value_counts().to_dict()
    print(f"{len(m['files'])} canonical bar files: {roles}")


if __name__ == "__main__":
    main()
