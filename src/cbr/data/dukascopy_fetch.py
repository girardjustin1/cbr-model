"""Dukascopy tick download (free, public) -> normalized UTC tick parquet + 5s/1m mid bars.

Usage:
    .venv/bin/python -m cbr.data.dukascopy_fetch --fixtures           # course parity windows
    .venv/bin/python -m cbr.data.dukascopy_fetch --from 2025-11-09 --to 2025-11-12

Reads Dukascopy's public hourly bi5 tick files directly (decoded here; dukascopy-node was rate-limited).
Output under data/ (gitignored):
    data/raw/dukascopy/<instrument>/ticks/YYYY-MM-DD.parquet
    data/normalized/<instrument>/bars_5s/YYYY-MM-DD.parquet
    data/normalized/<instrument>/bars_1m/YYYY-MM-DD.parquet
    data/raw/dukascopy/manifest.json
Bars: open-time UTC, OHLC from mid=(bid+ask)/2, spread stats, tick_count. Empty intervals produce no bar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import time
import urllib.error
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "dukascopy"
NORM = ROOT / "data" / "normalized"
MANIFEST = RAW / "manifest.json"
CACHE = ROOT / ".cache" / "dukascopy"      # per-hour artifact cache so retries resume
FEED = "https://datafeed.dukascopy.com/datafeed"
ATTEMPTS = 6
BACKOFF_SEC = 30
PAUSE_SEC = 1.0
INSTRUMENTS = {"xauusd": "XAUUSD", "dollaridxusd": "DXY_CFD"}
# Integer price divisor. Verified 2025-11-10 01h: XAUUSD 4044.46 vs FOREXCOM chart 4046.10 at 01:53 UTC;
# DOLLARIDXUSD 99.57 vs TVC:DXY watchlist ~99.64 the same session.
PRICE_SCALE = {"xauusd": 1000.0, "dollaridxusd": 1000.0}
# bi5 record: ms offset in hour, ask, bid (int32 scaled), ask volume, bid volume (float32), big-endian.
TICK_DTYPE = np.dtype([("ms", ">i4"), ("ask", ">i4"), ("bid", ">i4"), ("ask_vol", ">f4"), ("bid_vol", ">f4")])

# Course parity examples (research/examples/course_examples.jsonl), XAUUSD only (scope D7).
# Each window = the example day plus the previous day (for the 5-12 h condition window) and the next day.
FIXTURE_DAYS = {"CX-LT1-1": date(2025, 10, 21), "CX-TE1-1": date(2025, 10, 24), "CX-LT3-2": date(2025, 11, 10)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hour_file(instrument: str, hour: datetime) -> bytes:
    """One hour of ticks (LZMA 'bi5'); cached on disk. Month in the URL is zero-based."""
    cached = CACHE / instrument / f"{hour:%Y-%m-%d_%H}.bi5"
    if cached.exists():
        return cached.read_bytes()
    url = (f"{FEED}/{instrument.upper()}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/"
           f"{hour.hour:02d}h_ticks.bi5")
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cbr-research/0.1"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            break
        except urllib.error.HTTPError as err:
            if err.code == 404:
                data = b""                      # no file for this hour (market closed)
                break
            if err.code not in (429, 500, 502, 503, 504):
                raise
            reason = f"HTTP {err.code}"
        except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
            reason = type(err).__name__
        wait = BACKOFF_SEC * attempt
        print(f"  {instrument} {hour:%Y-%m-%d %H}h {reason}; retry in {wait}s", flush=True)
        time.sleep(wait)
    else:
        raise RuntimeError(f"download failed after {ATTEMPTS} attempts: {url}")
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    time.sleep(PAUSE_SEC)
    return data


def _download_day(instrument: str, day: date) -> pd.DataFrame:
    frames = []
    scale = PRICE_SCALE[instrument]
    for h in range(24):
        hour = datetime(day.year, day.month, day.day, h, tzinfo=UTC)
        raw = _hour_file(instrument, hour)
        if not raw:
            continue
        payload = lzma.decompress(raw)
        rec = np.frombuffer(payload, dtype=TICK_DTYPE)
        base_ms = int(hour.timestamp() * 1000)
        frames.append(pd.DataFrame({
            "ts": pd.to_datetime(base_ms + rec["ms"].astype("int64"), unit="ms", utc=True),
            "bid": rec["bid"] / scale, "ask": rec["ask"] / scale,
            "bid_vol": rec["bid_vol"].astype("float64"), "ask_vol": rec["ask_vol"].astype("float64"),
        }))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _validate_ticks(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "monotonic": bool(df["ts"].is_monotonic_increasing),
        "duplicate_ts": int(df["ts"].duplicated().sum()),
        "non_positive_spread": int((df["ask"] <= df["bid"]).sum()),
        "first_ts": str(df["ts"].min()) if len(df) else None,
        "last_ts": str(df["ts"].max()) if len(df) else None,
    }


def _bars(ticks: pd.DataFrame, freq: str) -> pd.DataFrame:
    t = ticks.set_index("ts")
    mid = (t["bid"] + t["ask"]) / 2
    spread = t["ask"] - t["bid"]
    grouped = mid.resample(freq, label="left", closed="left")
    bars = grouped.ohlc()
    bars["tick_count"] = grouped.count()
    bars["spread_mean"] = spread.resample(freq, label="left", closed="left").mean()
    bars["spread_max"] = spread.resample(freq, label="left", closed="left").max()
    bars = bars[bars["tick_count"] > 0]                     # no bar for empty intervals; gaps stay explicit
    bars.index.name = "open_time"
    return bars


def fetch(days: list[date], instruments: list[str]) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"source": FEED, "days": {}}
    for inst in instruments:
        for day in days:
            key = f"{inst}/{day.isoformat()}"
            tick_path = RAW / inst / "ticks" / f"{day.isoformat()}.parquet"
            if tick_path.exists() and key in manifest["days"]:
                print(f"skip {key}")
                continue
            ticks = _download_day(inst, day)
            entry = {"instrument": inst, "label": INSTRUMENTS[inst], "day": day.isoformat(),
                     "fetched_utc": datetime.now(UTC).isoformat()}
            if ticks.empty:
                entry["status"] = "EMPTY"            # weekend/holiday; recorded, not an error
                manifest["days"][key] = entry
                print(f"{key}: no ticks")
                continue
            checks = _validate_ticks(ticks)
            if not checks["monotonic"]:
                ticks = ticks.sort_values("ts", kind="stable")
            tick_path.parent.mkdir(parents=True, exist_ok=True)
            ticks.to_parquet(tick_path, index=False)
            entry.update(status="OK", tick_checks=checks, files={})
            entry["files"][str(tick_path.relative_to(ROOT))] = _sha256(tick_path)
            for freq, name in (("5s", "bars_5s"), ("1min", "bars_1m")):
                bars = _bars(ticks, freq)
                out = NORM / inst / name / f"{day.isoformat()}.parquet"
                out.parent.mkdir(parents=True, exist_ok=True)
                bars.to_parquet(out)
                entry["files"][str(out.relative_to(ROOT))] = _sha256(out)
                entry[f"{name}_rows"] = len(bars)
            manifest["days"][key] = entry
            MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
            print(f"{key}: {checks['rows']:,} ticks, {entry['bars_1m_rows']} 1m bars, "
                  f"{entry['bars_5s_rows']} 5s bars, dup_ts={checks['duplicate_ts']}, "
                  f"bad_spread={checks['non_positive_spread']}", flush=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fixtures", action="store_true")
    p.add_argument("--from", dest="start")
    p.add_argument("--to", dest="end")
    p.add_argument("--instrument", action="append", choices=list(INSTRUMENTS))
    a = p.parse_args()
    if a.fixtures:
        days = sorted({d + timedelta(days=o) for d in FIXTURE_DAYS.values() for o in (-1, 0, 1)})
    else:
        start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    fetch(days, a.instrument or list(INSTRUMENTS))


if __name__ == "__main__":
    main()
