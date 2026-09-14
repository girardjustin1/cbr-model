"""Dukascopy tick download (free, public) -> normalized UTC tick parquet + 5s/1m mid bars.

Usage:
    .venv/bin/python -m cbr.data.dukascopy_fetch --fixtures                          # candles + entry tick windows
    .venv/bin/python -m cbr.data.dukascopy_fetch --samples                           # AC-11A stratified sample
    .venv/bin/python -m cbr.data.dukascopy_fetch --candles --from 2018-01-01 --to 2024-12-31   # 1m history
    .venv/bin/python -m cbr.data.dukascopy_fetch --tick-days --from 2025-11-09 --to 2025-11-10  # full-day ticks

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
REQUEST_TIMEOUT_SEC = 120
INSTRUMENTS = {"xauusd": "XAUUSD", "dollaridxusd": "DXY_CFD"}
# Integer price divisor. Verified 2025-11-10 01h: XAUUSD 4044.46 vs FOREXCOM chart 4046.10 at 01:53 UTC;
# DOLLARIDXUSD 99.57 vs TVC:DXY watchlist ~99.64 the same session.
PRICE_SCALE = {"xauusd": 1000.0, "dollaridxusd": 1000.0}
# bi5 record: ms offset in hour, ask, bid (int32 scaled), ask volume, bid volume (float32), big-endian.
TICK_DTYPE = np.dtype([("ms", ">i4"), ("ask", ">i4"), ("bid", ">i4"), ("ask_vol", ">f4"), ("bid_vol", ">f4")])

# Course parity examples (research/examples/course_examples.jsonl), XAUUSD only (scope D7).
# 1m candles cover the example day plus the previous and next day (the 5-12 h condition window needs history).
FIXTURE_DAYS = {"CX-LT1-1": date(2025, 10, 21), "CX-TE1-1": date(2025, 10, 24), "CX-LT3-2": date(2025, 11, 10)}
# Tick (5s entry) windows: entry hour -2 h to +2 h, UTC. Entries: 01:39, 04:37, 01:40.
FIXTURE_TICK_WINDOWS = {
    "CX-LT1-1": (datetime(2025, 10, 20, 23, tzinfo=UTC), datetime(2025, 10, 21, 4, tzinfo=UTC)),
    "CX-TE1-1": (datetime(2025, 10, 24, 2, tzinfo=UTC), datetime(2025, 10, 24, 7, tzinfo=UTC)),
    "CX-LT3-2": (datetime(2025, 11, 9, 23, tzinfo=UTC), datetime(2025, 11, 10, 4, tzinfo=UTC)),
}
# AC-11A stratified sample (CBR-ACC-009 §2), declared before download. Development/validation periods only.
SAMPLE_DAYS = {
    "MID-2018": date(2018, 2, 21), "MID-2019": date(2019, 4, 17), "MID-2020": date(2020, 6, 17),
    "MID-2021": date(2021, 8, 18), "MID-2022": date(2022, 10, 19), "MID-2023": date(2023, 12, 20),
    "MID-2024": date(2024, 3, 20), "DST-SPRING-2019": date(2019, 3, 11), "DST-AUTUMN-2023": date(2023, 11, 6),
    "US-HOLIDAY-2022-THANKSGIVING": date(2022, 11, 24), "MONDAY-REOPEN-2021": date(2021, 2, 1),
    "DXY-CFD-FIRST-MONTH-2018": date(2018, 1, 17), "HIGHVOL-2020-03-09": date(2020, 3, 9),
    "HIGHVOL-2020-03-16": date(2020, 3, 16), "HIGHVOL-2022-03-08": date(2022, 3, 8),
    "HIGHVOL-2024-04-12": date(2024, 4, 12),
}
SAMPLE_TICK_WINDOWS = {                      # 00:00-03:00 UTC (Asia hours 1-3) on 4 of the 16 days
    f"S-{sid}": (datetime(d.year, d.month, d.day, 0, tzinfo=UTC), datetime(d.year, d.month, d.day, 3, tzinfo=UTC))
    for sid, d in SAMPLE_DAYS.items()
    if sid in ("DXY-CFD-FIRST-MONTH-2018", "HIGHVOL-2020-03-16", "US-HOLIDAY-2022-THANKSGIVING", "MID-2024")
}
# Daily 1m candle file record (verified 2026-09-14 against tick-built bars: open/close identical on 1,380 minutes).
CANDLE_DTYPE = np.dtype([("sec", ">i4"), ("open", ">i4"), ("close", ">i4"), ("low", ">i4"), ("high", ">i4"),
                         ("vol", ">f4")])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hour_file(instrument: str, hour: datetime) -> bytes:
    """One hour of ticks (LZMA 'bi5'); cached on disk. Month in the URL is zero-based."""
    url = (f"{FEED}/{instrument.upper()}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/"
           f"{hour.hour:02d}h_ticks.bi5")
    return _fetch_cached(url, CACHE / instrument / f"{hour:%Y-%m-%d_%H}.bi5", f"{instrument} {hour:%Y-%m-%d %H}h")


def _candle_file(instrument: str, day: date, side: str) -> bytes:
    """One UTC day of 1m candles for BID or ASK."""
    url = f"{FEED}/{instrument.upper()}/{day.year}/{day.month - 1:02d}/{day.day:02d}/{side}_candles_min_1.bi5"
    return _fetch_cached(url, CACHE / instrument / "candles" / f"{day.isoformat()}_{side}.bi5",
                         f"{instrument} {day} {side} candles")


def _fetch_cached(url: str, cached: Path, label: str) -> bytes:
    if cached.exists():
        return cached.read_bytes()
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cbr-research/0.1"})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as resp:
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
        print(f"  {label} {reason}; retry in {wait}s", flush=True)
        time.sleep(wait)
    else:
        raise RuntimeError(f"download failed after {ATTEMPTS} attempts: {url}")
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    time.sleep(PAUSE_SEC)
    return data


def _download_day(instrument: str, day: date) -> pd.DataFrame:
    return _decode_hours(instrument, [datetime(day.year, day.month, day.day, h, tzinfo=UTC) for h in range(24)])


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


def _decode_hours(instrument: str, hours: list[datetime]) -> pd.DataFrame:
    scale, frames = PRICE_SCALE[instrument], []
    for hour in hours:
        raw = _hour_file(instrument, hour)
        if not raw:
            continue
        rec = np.frombuffer(lzma.decompress(raw), dtype=TICK_DTYPE)
        base_ms = int(hour.timestamp() * 1000)
        frames.append(pd.DataFrame({
            "ts": pd.to_datetime(base_ms + rec["ms"].astype("int64"), unit="ms", utc=True),
            "bid": rec["bid"] / scale, "ask": rec["ask"] / scale,
            "bid_vol": rec["bid_vol"].astype("float64"), "ask_vol": rec["ask_vol"].astype("float64"),
        }))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _decode_candles(instrument: str, day: date, raw: bytes) -> pd.DataFrame:
    rec = np.frombuffer(lzma.decompress(raw), dtype=CANDLE_DTYPE).astype(CANDLE_DTYPE.newbyteorder("="))
    scale = PRICE_SCALE[instrument]
    idx = pd.to_datetime(int(pd.Timestamp(day, tz="UTC").timestamp()) + rec["sec"].astype("int64"), unit="s", utc=True)
    df = pd.DataFrame({c: rec[c].astype("float64") / scale for c in ("open", "high", "low", "close")}, index=idx)
    df["vol"] = rec["vol"].astype("float64")
    return df


def fetch_candles(days: list[date], instruments: list[str]) -> None:
    """1m bid/ask candles per UTC day -> data/normalized/<inst>/candles_1m/YYYY-MM-DD.parquet.
    Columns: bid_*/ask_* OHLC, mid OHLC = mean of bid and ask OHLC, volume. Zero-volume (flat, no trading)
    minutes are dropped so gaps stay explicit; their count is recorded."""
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"source": FEED, "days": {}}
    manifest.setdefault("candles", {})
    for inst in instruments:
        for day in days:
            key = f"{inst}/{day.isoformat()}"
            out = NORM / inst / "candles_1m" / f"{day.isoformat()}.parquet"
            if out.exists() and key in manifest["candles"]:
                continue
            raw_bid, raw_ask = _candle_file(inst, day, "BID"), _candle_file(inst, day, "ASK")
            entry = {"instrument": inst, "day": day.isoformat(), "fetched_utc": datetime.now(UTC).isoformat()}
            if not raw_bid or not raw_ask:
                entry["status"] = "EMPTY"
                manifest["candles"][key] = entry
                MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
                continue
            bid, ask = _decode_candles(inst, day, raw_bid), _decode_candles(inst, day, raw_ask)
            df = pd.concat({"bid": bid, "ask": ask}, axis=1)
            df.columns = [f"{side}_{col}" for side, col in df.columns]
            for col in ("open", "high", "low", "close"):
                df[col] = (df[f"bid_{col}"] + df[f"ask_{col}"]) / 2
            live = df[(df["bid_vol"] > 0) | (df["ask_vol"] > 0)]
            live.index.name = "open_time"
            out.parent.mkdir(parents=True, exist_ok=True)
            live.to_parquet(out)
            entry.update(status="OK", rows_total=len(df), rows_with_volume=len(live),
                         flat_rows_dropped=len(df) - len(live),
                         crossed_rows=int((live["ask_close"] < live["bid_close"]).sum()),
                         files={str(out.relative_to(ROOT)): _sha256(out)})
            manifest["candles"][key] = entry
            MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
            print(f"candles {key}: {len(live)} 1m bars with volume ({len(df) - len(live)} flat dropped)", flush=True)


def fetch_tick_windows(windows: dict[str, tuple[datetime, datetime]], instruments: list[str]) -> None:
    """Ticks for [start, end) hours -> 5s/1m mid bars for entry-level parity."""
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"source": FEED, "days": {}}
    manifest.setdefault("tick_windows", {})
    for inst in instruments:
        for wid, (start, end) in windows.items():
            key = f"{inst}/{wid}"
            tick_path = RAW / inst / "tick_windows" / f"{wid}.parquet"
            if tick_path.exists() and key in manifest["tick_windows"]:
                continue
            hours = [start + timedelta(hours=i) for i in range(int((end - start) / timedelta(hours=1)))]
            ticks = _decode_hours(inst, hours)
            entry = {"instrument": inst, "window": [start.isoformat(), end.isoformat()],
                     "fetched_utc": datetime.now(UTC).isoformat()}
            if ticks.empty:
                entry["status"] = "EMPTY"
                manifest["tick_windows"][key] = entry
                continue
            checks = _validate_ticks(ticks)
            ticks = ticks.sort_values("ts", kind="stable")
            tick_path.parent.mkdir(parents=True, exist_ok=True)
            ticks.to_parquet(tick_path, index=False)
            entry.update(status="OK", tick_checks=checks, files={str(tick_path.relative_to(ROOT)): _sha256(tick_path)})
            for freq, name in (("5s", "window_bars_5s"), ("1min", "window_bars_1m")):
                bars = _bars(ticks, freq)
                out = NORM / inst / name / f"{wid}.parquet"
                out.parent.mkdir(parents=True, exist_ok=True)
                bars.to_parquet(out)
                entry["files"][str(out.relative_to(ROOT))] = _sha256(out)
                entry[f"{name}_rows"] = len(bars)
            manifest["tick_windows"][key] = entry
            MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
            print(f"ticks {key}: {checks['rows']:,} ticks, dup={checks['duplicate_ts']}, "
                  f"bad_spread={checks['non_positive_spread']}", flush=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fixtures", action="store_true", help="1m candles for fixture days + tick windows around entries")
    p.add_argument("--samples", action="store_true", help="AC-11A: 1m candles for the 16 sample days + 4 tick windows")
    p.add_argument("--candles", action="store_true", help="1m candles for --from/--to (history)")
    p.add_argument("--tick-days", action="store_true", help="full-day ticks for --from/--to (slow)")
    p.add_argument("--from", dest="start")
    p.add_argument("--to", dest="end")
    p.add_argument("--instrument", action="append", choices=list(INSTRUMENTS))
    a = p.parse_args()
    instruments = a.instrument or list(INSTRUMENTS)
    if a.fixtures:
        days = sorted({d + timedelta(days=o) for d in FIXTURE_DAYS.values() for o in (-1, 0, 1)})
        fetch_candles(days, instruments)
        fetch_tick_windows(FIXTURE_TICK_WINDOWS, instruments)
        return
    if a.samples:
        fetch_candles(sorted(SAMPLE_DAYS.values()), instruments)
        fetch_tick_windows(SAMPLE_TICK_WINDOWS, instruments)
        return
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    if a.candles:
        fetch_candles([d for d in days if d.weekday() != 5], instruments)     # Saturdays have no trading
    elif a.tick_days:
        fetch(days, instruments)
    else:
        p.error("choose --fixtures, --candles or --tick-days")


if __name__ == "__main__":
    main()
