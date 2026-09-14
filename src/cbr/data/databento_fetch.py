"""Paid Databento downloads with a cost guard and a manifest.

Usage:
    .venv/bin/python -m cbr.data.databento_fetch            # downloads every request in REQUESTS

Each request is re-quoted immediately before download and skipped if the live quote exceeds the
approved quote by more than COST_TOLERANCE. Raw DBN files land in data/raw/databento/ (gitignored);
a parquet copy and a manifest entry (cost, symbols, range, row count, sha256) are written alongside.
The API key is read from .env and never printed or logged.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import databento as db

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "raw" / "databento"
MANIFEST = OUT / "manifest.json"
COST_TOLERANCE = 0.05

# Approved by the user on 2026-09-14 against these quotes.
REQUESTS = [
    {"name": "gc_front_ohlcv1m", "dataset": "GLBX.MDP3", "symbols": "GC.v.0", "stype_in": "continuous",
     "schema": "ohlcv-1m", "start": "2018-01-01", "end": "2026-09-14", "approved_usd": 11.09},
    {"name": "dx_front_ohlcv1m", "dataset": "IFUS.IMPACT", "symbols": "DX.v.0", "stype_in": "continuous",
     "schema": "ohlcv-1m", "start": "2018-12-23", "end": "2026-09-13", "approved_usd": 55.35},
]


def _key() -> str:
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("DATABENTO_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("DATABENTO_API_KEY missing from .env")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"downloads": []}
    done = {d["name"] for d in manifest["downloads"]}
    client = db.Historical(key=_key())

    for req in REQUESTS:
        if req["name"] in done:
            print(f"skip {req['name']} (already downloaded)")
            continue
        query = {k: req[k] for k in ("dataset", "symbols", "stype_in", "schema", "start", "end")}
        quote = client.metadata.get_cost(**query)
        if quote > req["approved_usd"] * (1 + COST_TOLERANCE):
            print(f"ABORT {req['name']}: live quote ${quote:.2f} exceeds approved ${req['approved_usd']:.2f}")
            continue

        dbn_path = OUT / f"{req['name']}.dbn.zst"
        print(f"downloading {req['name']} (quote ${quote:.2f})...", flush=True)
        store = client.timeseries.get_range(**query, path=dbn_path)
        df = store.to_df(pretty_ts=True, map_symbols=True)
        parquet_path = OUT / f"{req['name']}.parquet"
        df.to_parquet(parquet_path)

        entry = {
            **req,
            "quoted_usd": round(quote, 2),
            "downloaded_utc": datetime.now(UTC).isoformat(),
            "databento_client": db.__version__,
            "rows": len(df),
            "first_ts": str(df.index.min()) if len(df) else None,
            "last_ts": str(df.index.max()) if len(df) else None,
            "instrument_ids": sorted(int(i) for i in df["instrument_id"].unique()),
            "files": {p.name: {"bytes": p.stat().st_size, "sha256": _sha256(p)}
                      for p in (dbn_path, parquet_path)},
        }
        manifest["downloads"].append(entry)
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"  {entry['rows']:,} rows  {entry['first_ts']} → {entry['last_ts']}  "
              f"{len(entry['instrument_ids'])} contracts", flush=True)


if __name__ == "__main__":
    main()
