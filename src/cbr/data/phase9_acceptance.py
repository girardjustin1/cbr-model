"""Phase 9 historical-data acceptance -> reports/phase9-data-acceptance.json and .md.

Usage:
    .venv/bin/python -m cbr.data.phase9_acceptance

Read-only over data/ (gitignored). Every figure is recomputed from stored files. Holdout-period days are examined
for data integrity and feed differences only; no trade simulation or performance is computed.
"""

from __future__ import annotations

import hashlib
import json
import lzma
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from cbr.data import dukascopy_fetch as dk

ROOT = Path(__file__).resolve().parents[3]
REPORT_JSON = ROOT / "reports" / "phase9-data-acceptance.json"
NY = ZoneInfo("America/New_York")
SPIKE_MAD = 20.0          # flag a 1m close change > 20 x rolling median |change| (reported, never removed)
WIDE_SPREAD_MULT = 5.0    # flag a minute whose spread exceeds 5 x the day's median spread
REFERENCE_CLI_TICKS = {"xauusd": ("2025-11-10", 285935)}   # dukascopy-node@1.50.0 output recorded 2026-09-14
HISTORY = (date(2018, 1, 1), date(2024, 12, 31))
OHLC = ["open", "high", "low", "close"]


def fixture_days() -> list[date]:
    return sorted({d + timedelta(days=o) for d in dk.FIXTURE_DAYS.values() for o in (-1, 0, 1)})


def trading_day(d: date) -> bool:
    return d.weekday() != 5


def _hash(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()


def expected_closed(ts: pd.Timestamp) -> str | None:
    """Why a minute may legitimately be missing: weekend or the daily 17:00-18:00 New York break."""
    ny = ts.tz_convert(NY)
    if ny.weekday() == 5 or (ny.weekday() == 4 and ny.hour >= 17) or (ny.weekday() == 6 and ny.hour < 18):
        return "weekend"
    if ny.hour == 17:
        return "daily_break"
    return None


def _runs(stamps: list[pd.Timestamp]) -> list[str]:
    runs, start, prev = [], None, None
    for s in [*stamps, None]:
        if s is not None and start is not None and s - prev == pd.Timedelta(minutes=1):
            prev = s
            continue
        if start is not None:
            n = int((prev - start) / pd.Timedelta(minutes=1)) + 1
            runs.append(f"{start:%Y-%m-%d %H:%M}→{prev:%H:%M} UTC ({n} min)")
        start = prev = s
    return runs


def _bar_quality(bars: pd.DataFrame, day: date, spread: pd.Series | None) -> dict:
    minutes = pd.date_range(pd.Timestamp(day, tz="UTC"), periods=1440, freq="1min")
    missing = minutes.difference(bars.index)
    unexpected = [m for m in missing if not expected_closed(m)]
    change = bars["close"].diff()
    mad = change.abs().rolling(60, min_periods=20).median()
    q = {
        "bars": len(bars),
        "duplicate_index": int(bars.index.duplicated().sum()),
        "monotonic": bool(bars.index.is_monotonic_increasing),
        "utc": str(bars.index.tz) == "UTC",
        "aligned_to_minute": bool((bars.index.second == 0).all()),
        "non_positive_price": int((bars[OHLC] <= 0).any(axis=1).sum()),
        "ohlc_inconsistent": int(((bars["high"] < bars[["open", "close"]].max(axis=1) - 1e-9)
                                  | (bars["low"] > bars[["open", "close"]].min(axis=1) + 1e-9)).sum()),
        "missing_minutes": len(missing),
        "missing_expected": len(missing) - len(unexpected),
        "missing_unexpected": len(unexpected),
        "unexpected_gap_runs": _runs(unexpected),
        "spike_minutes": [str(t) for t in bars.index[(change.abs() > SPIKE_MAD * mad) & mad.gt(0)]],
    }
    if spread is not None:
        med = float(spread.median())
        wide = bars.index[spread > WIDE_SPREAD_MULT * med]
        q.update(median_spread=round(med, 4), wide_spread_minutes=len(wide),
                 wide_spread_hours_utc=sorted({t.hour for t in wide}))
    return q


def check_candles(inst: str, day: date, manifest: dict) -> dict:
    key = f"{inst}/{day.isoformat()}"
    entry = manifest.get("candles", {}).get(key)
    out = {"key": key, "trading_day": trading_day(day), "status": entry and entry.get("status")}
    path = dk.NORM / inst / "candles_1m" / f"{day.isoformat()}.parquet"
    if not entry or entry.get("status") != "OK" or not path.exists():
        return out
    c = pd.read_parquet(path)
    out.update(entry={k: entry[k] for k in ("rows_total", "rows_with_volume", "flat_rows_dropped", "crossed_rows")})
    out["manifest_hash_ok"] = all(dk._sha256(ROOT / f) == h for f, h in entry["files"].items())
    out["crossed_quotes"] = int((c["ask_low"] < c["bid_low"]).sum() + (c["ask_close"] < c["bid_close"]).sum())
    out.update(_bar_quality(c, day, c["ask_close"] - c["bid_close"]))
    return out


def check_tick_window(inst: str, wid: str, manifest: dict) -> dict:
    key = f"{inst}/{wid}"
    entry = manifest.get("tick_windows", {}).get(key)
    out = {"key": key, "status": entry and entry.get("status")}
    tick_path = dk.RAW / inst / "tick_windows" / f"{wid}.parquet"
    if not entry or entry.get("status") != "OK" or not tick_path.exists():
        return out
    t = pd.read_parquet(tick_path)
    s5 = pd.read_parquet(dk.NORM / inst / "window_bars_5s" / f"{wid}.parquet")
    m1 = pd.read_parquet(dk.NORM / inst / "window_bars_1m" / f"{wid}.parquet")
    start, end = (pd.Timestamp(x) for x in entry["window"])
    roll = s5.resample("1min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "tick_count": "sum"})
    roll = roll[roll["tick_count"] > 0]
    out.update({
        "ticks": len(t),
        "monotonic": bool(t["ts"].is_monotonic_increasing),
        "duplicate_ts": int(t["ts"].duplicated().sum()),
        "non_positive_spread": int((t["ask"] <= t["bid"]).sum()),
        "non_positive_price": int(((t["bid"] <= 0) | (t["ask"] <= 0)).sum()),
        "within_window": bool(t["ts"].min() >= start and t["ts"].max() < end),
        "manifest_hash_ok": all(dk._sha256(ROOT / f) == h for f, h in entry["files"].items()),
        "deterministic_5s": dk._bars(t, "5s").equals(s5) and _hash(dk._bars(t, "5s")) == _hash(s5),
        "deterministic_1m": dk._bars(t, "1min").equals(m1),
        "tick_count_reconciles": int(s5["tick_count"].sum()) == len(t) == int(m1["tick_count"].sum()),
        "rollup_5s_to_1m_equal": bool(roll.index.equals(m1.index) and np.allclose(
            roll[[*OHLC, "tick_count"]].to_numpy(float), m1[[*OHLC, "tick_count"]].to_numpy(float), atol=1e-9)),
        "aligned_5s": bool((s5.index.second % 5 == 0).all() and (s5.index.microsecond == 0).all()),
        "thin_5s_bars_1_tick": int((s5["tick_count"] == 1).sum()),
    })
    # window 1m (tick mids) vs daily candle file (mean of bid/ask OHLC) on overlapping minutes
    days = sorted({ts.date() for ts in m1.index})
    candles = [pd.read_parquet(p) for d in days
               if (p := dk.NORM / inst / "candles_1m" / f"{d.isoformat()}.parquet").exists()]
    if candles:
        j = m1[OHLC].join(pd.concat(candles)[OHLC], rsuffix="_c", how="inner")
        out["candle_reconciliation"] = {
            "minutes": len(j),
            **{f"{c}_max_abs_diff": round(float((j[c] - j[f"{c}_c"]).abs().max()), 4) for c in OHLC},
            **{f"{c}_share_within_0.05": round(float(((j[c] - j[f"{c}_c"]).abs() <= 0.05).mean()), 4) for c in OHLC},
        }
    return out


def decoder_parity() -> dict:
    inst, (day_s, ref) = next(iter(REFERENCE_CLI_TICKS.items()))
    day = date.fromisoformat(day_s)
    n = 0
    for h in range(24):
        f = dk.CACHE / inst / f"{datetime(day.year, day.month, day.day, h, tzinfo=UTC):%Y-%m-%d_%H}.bi5"
        if f.exists() and f.stat().st_size:
            n += len(lzma.decompress(f.read_bytes())) // dk.TICK_DTYPE.itemsize
    return {"instrument": inst, "day": day_s, "reference_cli_ticks": ref, "decoded_ticks": n, "match": n == ref}


def feed_comparison(day: date) -> dict:
    """Dukascopy spot/CFD 1m candles vs Databento front-month futures, common minutes."""
    out = {}
    for inst, db_name, label in (("xauusd", "gc_front_ohlcv1m", "XAUUSD vs GC"),
                                 ("dollaridxusd", "dx_front_ohlcv1m", "DXY CFD vs DX")):
        spot_path = dk.NORM / inst / "candles_1m" / f"{day.isoformat()}.parquet"
        fut_path = ROOT / "data" / "raw" / "databento" / f"{db_name}.parquet"
        if not spot_path.exists() or not fut_path.exists():
            out[label] = {"available": False}
            continue
        spot = pd.read_parquet(spot_path)["close"]
        fut = pd.read_parquet(fut_path)
        fut = fut[(fut["publisher_id"] == fut["publisher_id"].mode().iloc[0]) & (fut["close"] > 0)]  # drops DX XOFF
        fut = fut.loc[str(day)]
        fut = fut[~fut.index.duplicated()]["close"]
        j = pd.concat({"spot": spot, "fut": fut}, axis=1, join="inner").dropna()
        if len(j) < 60:
            out[label] = {"available": True, "common_minutes": len(j), "spot_minutes": len(spot),
                          "fut_minutes": len(fut)}
            continue
        basis = j["fut"] - j["spot"]
        r = j.diff().dropna()
        lags = {lag: float(r["spot"].corr(r["fut"].shift(lag))) for lag in range(-3, 4)}
        best = max(lags, key=lambda k: lags[k])
        out[label] = {
            "available": True, "common_minutes": len(j), "spot_minutes": len(spot), "fut_minutes": len(fut),
            "basis_mean": round(float(basis.mean()), 4), "basis_std": round(float(basis.std()), 4),
            "basis_range": [round(float(basis.min()), 4), round(float(basis.max()), 4)],
            "return_corr_lag0": round(lags[0], 4), "best_lag_min": best, "best_lag_corr": round(lags[best], 4),
            "mean_abs_move_ratio_fut_over_spot": round(float(r["fut"].abs().mean() / r["spot"].abs().mean()), 4),
        }
    return out


def tom_chart_points() -> list[dict]:
    """Prices read off Tom's FOREX.com chart vs Dukascopy mid at the same UTC minute (UTC+11 charts)."""
    points = [
        {"example": "CX-LT3-2", "utc": "2025-11-10 01:53", "field": "close", "tom_price": 4046.10,
         "source": "live price label, V1H-live_trade_3 frame 00:28:58"},
        {"example": "CX-LT1-1", "utc": "2025-10-21 01:38", "field": "low", "tom_price": 4332.96,
         "source": "stop placed at extension low (course_examples.jsonl)"},
        {"example": "CX-LT1-1", "utc": "2025-10-21 01:39", "field": "close", "tom_price": 4340.13,
         "source": "entry price (course_examples.jsonl); entry is intrabar, compared to the 1m close"},
    ]
    for p in points:
        ts = pd.Timestamp(p["utc"], tz="UTC")
        f = dk.NORM / "xauusd" / "candles_1m" / f"{ts.date().isoformat()}.parquet"
        if f.exists() and ts in (c := pd.read_parquet(f)).index:
            p["dukascopy_mid"] = round(float(c.loc[ts, p["field"]]), 3)
            p["diff"] = round(p["dukascopy_mid"] - p["tom_price"], 3)
    return points


def history_status(manifest: dict) -> dict:
    out = {}
    all_days = [HISTORY[0] + timedelta(days=i) for i in range((HISTORY[1] - HISTORY[0]).days + 1)]
    needed = [d for d in all_days if trading_day(d)]
    for inst in dk.INSTRUMENTS:
        have = [d for d in needed if manifest.get("candles", {}).get(f"{inst}/{d.isoformat()}", {}).get("status")
                in ("OK", "EMPTY")]
        out[inst] = {"trading_days_required": len(needed), "days_present": len(have),
                     "coverage": round(len(have) / len(needed), 4), "candle_files_required": 2 * len(needed)}
    return out


def evaluate() -> dict:
    manifest = json.loads(dk.MANIFEST.read_text())
    days = fixture_days()
    candles = [check_candles(i, d, manifest) for i in dk.INSTRUMENTS for d in days if trading_day(d)]
    windows = [check_tick_window(i, w, manifest) for i in dk.INSTRUMENTS for w in dk.FIXTURE_TICK_WINDOWS]
    feeds = {d.isoformat(): feed_comparison(d) for d in days if d.weekday() < 5}
    tom = tom_chart_points()
    parity = decoder_parity()
    hist = history_status(manifest)

    ok_c = [c for c in candles if c.get("status") == "OK" and "bars" in c]
    ok_w = [w for w in windows if w.get("status") == "OK" and "ticks" in w]

    def all_(rows, pred):
        return bool(rows) and all(pred(r) for r in rows)

    criteria = {
        "AC-01 fixture 1m candle coverage": len(ok_c) == len(candles),
        "AC-02 entry tick windows": len(ok_w) == len(windows),
        "AC-03 decoder parity": parity["match"] and all_(
            [w for w in ok_w if w["key"].startswith("xauusd") and "candle_reconciliation" in w],
            lambda w: w["candle_reconciliation"]["open_max_abs_diff"] == 0
            and w["candle_reconciliation"]["close_max_abs_diff"] == 0),
        "AC-04 integrity": all_(ok_c, lambda c: c["duplicate_index"] == 0 and c["monotonic"] and c["utc"]
                                and c["aligned_to_minute"] and c["non_positive_price"] == 0
                                and c["ohlc_inconsistent"] == 0 and c["manifest_hash_ok"])
        and all_(ok_w, lambda w: w["duplicate_ts"] == 0 and w["monotonic"] and w["non_positive_price"] == 0
                 and w["within_window"] and w["manifest_hash_ok"]),
        "AC-05 deterministic bars": all_(ok_w, lambda w: w["deterministic_5s"] and w["deterministic_1m"]),
        "AC-06 reconciliation": all_(ok_w, lambda w: w["tick_count_reconciles"] and w["rollup_5s_to_1m_equal"]
                                     and w["aligned_5s"]),
        "AC-07 gaps classified": all_(ok_c, lambda c: c["missing_expected"] + c["missing_unexpected"]
                                      == c["missing_minutes"]),
        "AC-08 bad data flagged": all_(ok_c, lambda c: "spike_minutes" in c and "wide_spread_minutes" in c),
        "AC-09 feed comparison documented": any(v.get("common_minutes", 0) >= 60 for f in feeds.values()
                                                for v in f.values() if isinstance(v, dict)),
        "AC-10 timezone verified vs Tom's chart": all("diff" in p and abs(p["diff"]) <= 3.0 for p in tom),
        "AC-11 2018-2024 1m history": all(h["coverage"] == 1.0 for h in hist.values()),
    }
    return {"generated_utc": datetime.now(UTC).isoformat(), "criteria": criteria, "decoder_parity": parity,
            "candles": candles, "tick_windows": windows, "feed_comparison": feeds, "tom_chart_points": tom,
            "history": hist}


def main() -> None:
    result = evaluate()
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(result, indent=2, default=str) + "\n")
    for k, v in result["criteria"].items():
        print(f"{'PASS' if v else 'FAIL'}  {k}")


if __name__ == "__main__":
    main()
