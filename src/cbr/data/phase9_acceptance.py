"""Phase 9 historical-data acceptance (CBR-ACC-009 v2.1) -> reports/phase9-data-acceptance.{json,md}.

Usage:
    .venv/bin/python -m cbr.data.phase9_acceptance

Every figure is recomputed from stored files. Every failed check becomes an itemized failure with a stable id; its
classification comes only from reports/phase9-exceptions.yaml (human-investigated). Unclassified failures force FAIL.
A DATA_ERROR / UNEXPLAINED_FEED_DIFFERENCE stops blocking only under an owner ruling with handling MISSING whose ruled
interval is independently flagged by an automated detector (D12); it stays in the report as a concern.
Holdout-period fixture days are examined for integrity and feed differences only; no trades or performance.
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
import yaml

from cbr.data import dukascopy_fetch as dk
from cbr.data import quality as q
from cbr.data.futures import load_front
from cbr.data.sessions import expected_closed

ROOT = Path(__file__).resolve().parents[3]
REPORT_JSON = ROOT / "reports" / "phase9-data-acceptance.json"
REPORT_MD = ROOT / "reports" / "phase9-data-acceptance.md"
EXCEPTIONS = ROOT / "reports" / "phase9-exceptions.yaml"
NY = ZoneInfo("America/New_York")
OHLC = ["open", "high", "low", "close"]

# ---- thresholds declared in CBR-ACC-009 §3 (before sample download) ----
CORR_MIN = {"XAUUSD vs GC": 0.95, "DXY CFD vs DX": 0.90}
BEST_LAG_REQUIRED = 0
BASIS_JUMP_MAX = {"XAUUSD vs GC": 5.00}
SCALE_TOLERANCE = 0.02
MIN_OVERLAP = 60
SPIKE_MAD = 20.0            # reporting flag only (AC-08)
WIDE_SPREAD_MULT = 5.0      # reporting flag only (AC-08)
REFERENCE_CLI_TICKS = ("xauusd", "2025-11-10", 285935)
TOM_PRICE_TOLERANCE = 3.0

CLASSES_FAIL = {"PIPELINE_ERROR", "DATA_ERROR", "UNEXPLAINED_FEED_DIFFERENCE"}
CLASSES_CONCERN = {"EXPECTED_MARKET_BEHAVIOR", "EXPECTED_FEED_DIFFERENCE", "REFERENCE_UNAVAILABLE"}
CAUSE_STATUS = {"ESTABLISHED", "HYPOTHESIZED", "UNKNOWN"}
RULED_HANDLING = "MISSING"
PAIRS = (("xauusd", "gc_front_ohlcv1m", "XAUUSD vs GC"), ("dollaridxusd", "dx_front_ohlcv1m", "DXY CFD vs DX"))


def fixture_days() -> list[date]:
    return sorted({d + timedelta(days=o) for d in dk.FIXTURE_DAYS.values() for o in (-1, 0, 1)
                   if (d + timedelta(days=o)).weekday() != 5})


def _runs(stamps: list[pd.Timestamp]) -> list[str]:
    runs, start, prev = [], None, None
    for s in [*stamps, None]:
        if s is not None and start is not None and s - prev == pd.Timedelta(minutes=1):
            prev = s
            continue
        if start is not None:
            runs.append(f"{start:%Y-%m-%d %H:%M}→{prev:%H:%M} UTC ({int((prev - start) / pd.Timedelta(minutes=1)) + 1} min)")
        start = prev = s
    return runs


def _hash(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()


class Collector:
    def __init__(self) -> None:
        self.failures: list[dict] = []

    def check(self, fid: str, criterion: str, ok: bool, observed, expected) -> bool:
        if not ok:
            self.failures.append({"id": fid, "criterion": criterion, "observed": observed, "expected": expected})
        return ok


# ---------------- per-dataset checks ----------------

def check_candles(inst: str, day: date, label: str, manifest: dict, col: Collector) -> dict:
    key = f"{inst}/{day.isoformat()}"
    entry = manifest.get("candles", {}).get(key)
    path = dk.NORM / inst / "candles_1m" / f"{day.isoformat()}.parquet"
    out = {"key": key, "label": label, "status": entry and entry.get("status")}
    ac_cov = "AC-01" if label == "fixture" else "AC-11A"
    if not col.check(f"{ac_cov}/coverage/{key}", ac_cov, bool(entry and entry.get("status") == "OK" and path.exists()),
                     out["status"] or "missing", "OK candle file"):
        return out
    c = pd.read_parquet(path)
    minutes = pd.date_range(pd.Timestamp(day, tz="UTC"), periods=1440, freq="1min")
    missing = minutes.difference(c.index)
    unexpected = [m for m in missing if not expected_closed(m)]
    change = c["close"].diff()
    mad = change.abs().rolling(60, min_periods=20).median()
    spread = c["ask_close"] - c["bid_close"]
    med = float(spread.median())
    out.update({
        "bars": len(c), "flat_dropped": entry.get("flat_rows_dropped"),
        "missing_minutes": len(missing), "missing_unexpected": len(unexpected),
        "unexpected_gap_runs": _runs(unexpected),
        "spike_minutes": [str(t) for t in c.index[(change.abs() > SPIKE_MAD * mad) & mad.gt(0)]],
        "median_spread": round(med, 4), "wide_spread_minutes": int((spread > WIDE_SPREAD_MULT * med).sum()),
    })
    f = f"{key}"
    col.check(f"AC-04/manifest_hash/{f}", "AC-04",
              all(dk._sha256(ROOT / p) == h for p, h in entry["files"].items()), "hash mismatch", "match")
    col.check(f"AC-04/duplicates/{f}", "AC-04", not c.index.duplicated().any(), int(c.index.duplicated().sum()), 0)
    col.check(f"AC-04/order_utc_alignment/{f}", "AC-04",
              bool(c.index.is_monotonic_increasing and str(c.index.tz) == "UTC" and (c.index.second == 0).all()),
              "not monotonic/UTC/minute-aligned", "monotonic, UTC, :00 seconds")
    col.check(f"AC-04/non_positive_price/{f}", "AC-04", not (c[OHLC] <= 0).any(axis=None),
              int((c[OHLC] <= 0).any(axis=1).sum()), 0)
    bad_ohlc = int(((c["high"] < c[["open", "close"]].max(axis=1) - 1e-9)
                    | (c["low"] > c[["open", "close"]].min(axis=1) + 1e-9)).sum())
    col.check(f"AC-04/ohlc_consistency/{f}", "AC-04", bad_ohlc == 0, bad_ohlc, 0)
    crossed = int((c["ask_close"] < c["bid_close"]).sum())
    col.check(f"AC-04/crossed_quotes/{f}", "AC-04", crossed == 0, crossed, 0)
    col.check(f"AC-07/unexpected_gaps/{f}", "AC-07", not unexpected, out["unexpected_gap_runs"], "no unexpected gaps")
    if inst == "dollaridxusd":
        start = pd.Timestamp(day, tz="UTC")
        out["dxy_missing_while_dx_active"] = [
            {k: (str(v) if isinstance(v, pd.Timestamp) else v) for k, v in r.items()}
            for r in q.dxy_cfd_missing_while_dx_active(c.index, load_front("dx_front_ohlcv1m"), start, start + pd.Timedelta(days=1))]
    out["candle_hl_suspect_minutes"] = int(q.suspect_candle_extrema(c).sum())
    return out


def check_tick_window(inst: str, wid: str, label: str, manifest: dict, col: Collector) -> dict:
    key = f"{inst}/{wid}"
    entry = manifest.get("tick_windows", {}).get(key)
    tick_path = dk.RAW / inst / "tick_windows" / f"{wid}.parquet"
    out = {"key": key, "label": label, "status": entry and entry.get("status")}
    ac_cov = "AC-02" if label == "fixture" else "AC-11A"
    if not col.check(f"{ac_cov}/coverage/{key}", ac_cov, bool(entry and entry.get("status") == "OK"
                                                               and tick_path.exists()),
                     out["status"] or "missing", "OK tick window"):
        return out
    t = pd.read_parquet(tick_path)
    s5 = pd.read_parquet(dk.NORM / inst / "window_bars_5s" / f"{wid}.parquet")
    m1 = pd.read_parquet(dk.NORM / inst / "window_bars_1m" / f"{wid}.parquet")
    start, end = (pd.Timestamp(x) for x in entry["window"])
    roll = s5.resample("1min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "tick_count": "sum"})
    roll = roll[roll["tick_count"] > 0]
    out.update({"ticks": len(t), "bars_5s": len(s5), "thin_5s_bars_1_tick": int((s5["tick_count"] == 1).sum())})
    col.check(f"AC-04/tick_integrity/{key}", "AC-04",
              bool(t["ts"].is_monotonic_increasing and not t["ts"].duplicated().any()
                   and ((t["bid"] > 0) & (t["ask"] > 0)).all() and t["ts"].min() >= start and t["ts"].max() < end),
              "order/duplicate/price/window violation", "clean")
    bad_spread = int((t["ask"] <= t["bid"]).sum())
    col.check(f"AC-04/non_positive_spread/{key}", "AC-04", bad_spread == 0, bad_spread, 0)
    col.check(f"AC-04/manifest_hash/{key}", "AC-04",
              all(dk._sha256(ROOT / p) == h for p, h in entry["files"].items()), "hash mismatch", "match")
    col.check(f"AC-05/determinism/{key}", "AC-05",
              bool(dk._bars(t, "5s").equals(s5) and _hash(dk._bars(t, "5s")) == _hash(s5)
                   and dk._bars(t, "1min").equals(m1)), "rebuild differs", "identical rebuild")
    col.check(f"AC-06/tick_counts/{key}", "AC-06",
              int(s5["tick_count"].sum()) == len(t) == int(m1["tick_count"].sum()), "counts differ", "equal")
    col.check(f"AC-06/rollup_5s_1m/{key}", "AC-06",
              bool(roll.index.equals(m1.index) and np.allclose(roll[[*OHLC, "tick_count"]].to_numpy(float),
                                                                m1[[*OHLC, "tick_count"]].to_numpy(float), atol=1e-9)),
              "roll-up differs", "identical")
    days = sorted({ts.date() for ts in m1.index})
    candles = [pd.read_parquet(p) for d in days if (p := dk.NORM / inst / "candles_1m" / f"{d.isoformat()}.parquet").exists()]
    if candles:
        j = m1[OHLC].join(pd.concat(candles)[OHLC], rsuffix="_c", how="inner")
        rec = {"minutes": len(j), **{f"{c}_max_abs_diff": round(float((j[c] - j[f"{c}_c"]).abs().max()), 4)
                                     for c in OHLC},
               **{f"{c}_within_0.05": round(float(((j[c] - j[f"{c}_c"]).abs() <= 0.05).mean()), 4) for c in OHLC}}
        out["candle_reconciliation"] = rec
        tol = q.load_config()["candle_extrema"]["tick_parity_tolerance"][inst]
        cs = pd.concat(candles)
        art = q.artificial_extrema_vs_ticks(cs, m1, tol)
        suspect = q.suspect_candle_extrema(cs.loc[art.index])
        out["candle_extrema"] = {
            "hl_method_candle": sorted(cs["hl_method"].unique()), "hl_method_ticks": sorted(m1["hl_method"].unique()),
            "tolerance": tol, "minutes": len(art), "artificial_minutes": int(art["artificial"].sum()),
            "max_high_overstatement": round(float(art["high_overstatement"].max()), 4),
            "max_low_overstatement": round(float(art["low_overstatement"].max()), 4),
            "suspect_flagged": int(suspect.sum()), "artificial_and_suspect": int((suspect & art["artificial"]).sum())}
        col.check(f"AC-06/candle_hl_bound/{key}", "AC-06", bool(art["within_bound"].all()),
                  int((~art["within_bound"]).sum()), "0 minutes outside the SIDE_EXTREME_MEAN error bound")
        col.check(f"AC-03/candle_open_close_parity/{key}", "AC-03",
                  rec["open_max_abs_diff"] == 0 and rec["close_max_abs_diff"] == 0,
                  {k: rec[k] for k in ("open_max_abs_diff", "close_max_abs_diff")}, "0 difference")
    else:
        col.check(f"AC-06/candle_reconciliation_missing/{key}", "AC-06", False, "no candle file", "candle file present")
    return out


def feed_comparison(day: date, label: str, col: Collector) -> dict:
    out = {}
    ac = "AC-09" if label == "fixture" else "AC-11A"
    for inst, db_name, pair in PAIRS:
        spot_path = dk.NORM / inst / "candles_1m" / f"{day.isoformat()}.parquet"
        fut = pd.read_parquet(ROOT / "data" / "raw" / "databento" / f"{db_name}.parquet")
        if not spot_path.exists():
            out[pair] = {"available": False, "reason": "spot candles missing"}
            continue
        fut = fut[(fut["publisher_id"] == fut["publisher_id"].mode().iloc[0]) & (fut["close"] > 0)]
        start = pd.Timestamp(day, tz="UTC")
        fut = fut[(fut.index >= start) & (fut.index < start + pd.Timedelta(days=1))]   # empty if no futures that day
        fut = fut[~fut.index.duplicated()]
        spot = pd.read_parquet(spot_path)["close"]
        j = pd.concat({"spot": spot, "fut": fut["close"], "iid": fut["instrument_id"]}, axis=1, join="inner").dropna()
        fid = f"{day.isoformat()}/{pair}"
        if not col.check(f"{ac}/feed_overlap/{fid}", ac, len(j) >= MIN_OVERLAP, len(j), f">= {MIN_OVERLAP} minutes"):
            out[pair] = {"available": True, "common_minutes": len(j), "spot_minutes": len(spot), "fut_minutes": len(fut)}
            continue
        basis = j["fut"] - j["spot"]
        r = j[["spot", "fut"]].diff().dropna()
        lags = {lag: float(r["spot"].corr(r["fut"].shift(lag))) for lag in range(-3, 4)}
        best = max(lags, key=lambda k: lags[k])
        same_contract = j["iid"].eq(j["iid"].shift())
        jumps = basis.diff().abs()[same_contract]
        scale = float((j["fut"] / j["spot"] - 1).abs().median())
        rec = {"available": True, "common_minutes": len(j), "spot_minutes": len(spot), "fut_minutes": len(fut),
               "basis_mean": round(float(basis.mean()), 4), "basis_std": round(float(basis.std()), 4),
               "return_corr_lag0": round(lags[0], 4), "best_lag_min": best, "best_lag_corr": round(lags[best], 4),
               "max_basis_jump_ex_roll": round(float(jumps.max()), 4) if len(jumps) else None,
               "roll_minutes": int((~same_contract).sum() - 1), "scale_median_abs": round(scale, 5)}
        out[pair] = rec
        col.check(f"{ac}/return_corr/{fid}", ac, lags[0] >= CORR_MIN[pair], round(lags[0], 4), f">= {CORR_MIN[pair]}")
        col.check(f"{ac}/best_lag/{fid}", ac, best == BEST_LAG_REQUIRED, best, BEST_LAG_REQUIRED)
        col.check(f"{ac}/price_scale/{fid}", ac, scale <= SCALE_TOLERANCE, round(scale, 5), f"<= {SCALE_TOLERANCE}")
        if pair in BASIS_JUMP_MAX and rec["max_basis_jump_ex_roll"] is not None:
            col.check(f"{ac}/basis_jump/{fid}", ac, rec["max_basis_jump_ex_roll"] <= BASIS_JUMP_MAX[pair],
                      rec["max_basis_jump_ex_roll"], f"<= {BASIS_JUMP_MAX[pair]}")
    return out


def decoder_parity(col: Collector) -> dict:
    inst, day_s, ref = REFERENCE_CLI_TICKS
    day = date.fromisoformat(day_s)
    n = sum(len(lzma.decompress(f.read_bytes())) // dk.TICK_DTYPE.itemsize
            for h in range(24)
            if (f := dk.CACHE / inst / f"{datetime(day.year, day.month, day.day, h, tzinfo=UTC):%Y-%m-%d_%H}.bi5").exists()
            and f.stat().st_size)
    col.check("AC-03/tick_decoder_parity", "AC-03", n == ref, n, ref)
    return {"instrument": inst, "day": day_s, "reference_cli_ticks": ref, "decoded_ticks": n}


def tom_chart_points(col: Collector) -> list[dict]:
    points = [
        {"example": "CX-LT3-2", "utc": "2025-11-10 01:53", "field": "close", "tom_price": 4046.10,
         "source": "live price label, V1H-live_trade_3 frame 00:28:58"},
        {"example": "CX-LT1-1", "utc": "2025-10-21 01:38", "field": "low", "tom_price": 4332.96,
         "source": "stop placed at extension low"},
        {"example": "CX-LT1-1", "utc": "2025-10-21 01:39", "field": "close", "tom_price": 4340.13,
         "source": "entry price (intrabar) vs 1m close"},
    ]
    for p in points:
        ts = pd.Timestamp(p["utc"], tz="UTC")
        f = dk.NORM / "xauusd" / "candles_1m" / f"{ts.date().isoformat()}.parquet"
        val = None
        if f.exists() and ts in (c := pd.read_parquet(f)).index:
            val = round(float(c.loc[ts, p["field"]]), 3)
            p["dukascopy_mid"], p["diff"] = val, round(val - p["tom_price"], 3)
        col.check(f"AC-10/tom_price/{p['example']}/{p['utc']}", "AC-10",
                  val is not None and abs(val - p["tom_price"]) <= TOM_PRICE_TOLERANCE,
                  p.get("diff", "missing"), f"|diff| <= {TOM_PRICE_TOLERANCE}")
    return points


def history_status(manifest: dict) -> dict:
    days = [date(2018, 1, 1) + timedelta(days=i) for i in range((date(2024, 12, 31) - date(2018, 1, 1)).days + 1)]
    needed = [d for d in days if d.weekday() != 5]
    return {inst: {"trading_days_required": len(needed),
                   "days_present": sum(1 for d in needed if manifest.get("candles", {}).get(f"{inst}/{d.isoformat()}",
                                                                                           {}).get("status") == "OK")}
            for inst in dk.INSTRUMENTS}


# ---------------- verdict ----------------

def _register() -> dict:
    return (yaml.safe_load(EXCEPTIONS.read_text()) if EXCEPTIONS.exists() else None) or {}


def register_errors(reg: dict) -> list[str]:
    allowed = CLASSES_FAIL | CLASSES_CONCERN
    errs = []
    for e in reg.get("exceptions", []):
        if e.get("class") not in allowed:
            errs.append(f"{e.get('id')}: class {e.get('class')!r} not allowed")
        if e.get("cause_status") not in CAUSE_STATUS:
            errs.append(f"{e.get('id')}: cause_status {e.get('cause_status')!r} not in {sorted(CAUSE_STATUS)}")
        if e.get("owner_ruling") and not (e.get("handling") == RULED_HANDLING and e.get("detector")
                                          and len(e.get("ruled_interval_utc") or []) == 2):
            errs.append(f"{e.get('id')}: owner ruling needs handling MISSING, detector and ruled_interval_utc")
    return errs


def _detected(f: dict, e: dict, detections: dict) -> bool:
    """The ruled interval intersects a detector flag with the ruling's reason code, on the failure's instrument/day."""
    parts = f["id"].split("/")
    flags = detections.get(f"{parts[2]}/{parts[3]}", []) if len(parts) >= 4 else []
    lo, hi = (pd.Timestamp(x) for x in e["ruled_interval_utc"])
    return any(r["reason_code"] == e["detector"] and pd.Timestamp(r["start"]) < hi and pd.Timestamp(r["end"]) > lo
               for r in flags)


def classify(failures: list[dict], detections: dict) -> tuple[list[dict], dict]:
    reg = _register()
    known = {e["id"]: e for e in reg.get("exceptions", [])}
    for f in failures:
        e = known.get(f["id"])
        f["class"] = e["class"] if e else "UNCLASSIFIED"
        f["cause_status"] = e.get("cause_status") if e else None
        f["explanation"] = e.get("explanation") if e else None
        f["owner_ruling"] = e.get("owner_ruling") if e else None
        f["handling"] = e.get("handling") if e else None
        f["detected"] = bool(e and e.get("owner_ruling") and _detected(f, e, detections))
        f["ruled_non_blocking"] = bool(f["class"] in CLASSES_FAIL and f["owner_ruling"]
                                       and f["handling"] == RULED_HANDLING and f["detected"])
    stale = sorted(set(known) - {f["id"] for f in failures})
    return failures, {"stale_exception_ids": stale, "register_errors": register_errors(reg)}


def verdict(failures: list[dict], criteria: list[str], history: dict, register_errs: list[str]) -> dict:
    blocking = [f for f in failures if f["class"] == "UNCLASSIFIED"
                or (f["class"] in CLASSES_FAIL and not f["ruled_non_blocking"])]
    concerns = [f for f in failures if f not in blocking]
    status = {}
    for c in criteria:
        fs = [f for f in failures if f["criterion"] == c]
        status[c] = ("FAIL" if any(f in blocking for f in fs) else "MET WITH CONCERNS" if fs else "MET")
    ac11b_done = all(h["days_present"] == h["trading_days_required"] for h in history.values())
    status["AC-11B"] = "MET" if ac11b_done else "DEFERRED (outstanding)"
    if blocking or register_errs:
        v = "FAIL"
    elif concerns or not ac11b_done:
        v = "PASS WITH CONCERNS"
    else:
        v = "PASS"
    return {"verdict": v, "criteria_status": status, "blocking": [f["id"] for f in blocking],
            "concerns": [f["id"] for f in concerns], "register_errors": register_errs}


def evaluate() -> dict:
    manifest = json.loads(dk.MANIFEST.read_text())
    col = Collector()
    parity = decoder_parity(col)
    fixtures = {"candles": [check_candles(i, d, "fixture", manifest, col) for i in dk.INSTRUMENTS for d in fixture_days()],
                "tick_windows": [check_tick_window(i, w, "fixture", manifest, col)
                                 for i in dk.INSTRUMENTS for w in dk.FIXTURE_TICK_WINDOWS],
                "feeds": {d.isoformat(): feed_comparison(d, "fixture", col) for d in fixture_days() if d.weekday() < 5}}
    samples = {"candles": [check_candles(i, d, sid, manifest, col) for sid, d in dk.SAMPLE_DAYS.items()
                           for i in dk.INSTRUMENTS],
               "tick_windows": [check_tick_window(i, w, "sample", manifest, col)
                                for i in dk.INSTRUMENTS for w in dk.SAMPLE_TICK_WINDOWS],
               "feeds": {f"{sid} {d.isoformat()}": feed_comparison(d, "sample", col)
                         for sid, d in dk.SAMPLE_DAYS.items()}}
    tom = tom_chart_points(col)
    history = history_status(manifest)
    detections = {c["key"]: c.get("dxy_missing_while_dx_active", [])
                  for c in fixtures["candles"] + samples["candles"]}
    failures, meta = classify(col.failures, detections)
    criteria = [f"AC-{i:02d}" for i in range(1, 11)] + ["AC-11A"]
    return {"generated_utc": datetime.now(UTC).isoformat(), "decoder_parity": parity, "fixtures": fixtures,
            "samples": samples, "tom_chart_points": tom, "history_ac11b": history, "failures": failures,
            **meta, "result": verdict(failures, criteria, history, meta["register_errors"])}


def render_md(r: dict) -> str:
    res = r["result"]
    lines = [
        "# Phase 9 Data Acceptance Report", "",
        f"Generated {r['generated_utc']} by `src/cbr/data/phase9_acceptance.py` against CBR-ACC-009 v2.1.", "",
        f"## Verdict: **{res['verdict']}**", "",
        "| Criterion | Status |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in res["criteria_status"].items()], "",
        (f"Blocking failures: {len(res['blocking'])} · Documented concerns (all preserved): {len(res['concerns'])} · "
         f"Register errors: {len(res['register_errors'])}"), "",
        *[f"- register error: {e}" for e in res["register_errors"]],
        "Concerns stay concerns: classification and owner rulings make a failure non-blocking, never resolved.", "",
        "## Failures and classifications", "",
        "| Id | Criterion | Observed | Expected | Class | Cause status | Owner ruling / handling / detected | Explanation |",
        "|---|---|---|---|---|---|---|---|",
        *[f"| `{f['id']}` | {f['criterion']} | {f['observed']} | {f['expected']} | {f['class']} | {f['cause_status']} | "
          f"{(f['owner_ruling'] + ' / ' + str(f['handling']) + ' / ' + str(f['detected'])) if f['owner_ruling'] else '—'} | "
          f"{(f['explanation'] or '').replace(chr(10), ' ')} |" for f in r["failures"]], "",
        "## Detector: DXY_CFD_MISSING_WHILE_DX_ACTIVE (handling MISSING)", "",
        "| Day | Flagged (DX active span, UTC) | CFD gap (UTC) | Gap min | DX active min | DX volume |",
        "|---|---|---|---|---|---|",
        *[f"| {c['key'].split('/')[1]} | {d['start'][11:16]}→{d['end'][11:16]} | {d['cfd_gap_start'][11:16]}→"
          f"{d['cfd_gap_end'][11:16]} | {d['cfd_gap_minutes']} | {d['dx_active_minutes']} | {d['dx_volume']:.0f} |"
          for c in r["fixtures"]["candles"] + r["samples"]["candles"] for d in c.get("dxy_missing_while_dx_active", [])],
        "",
        "## Candle high/low construction (hard safeguard before Phase 14; OQ-25)", "",
        ("Candle files: `hl_method = SIDE_EXTREME_MEAN`. Tick-built bars: `TICK_MID`. Artificial = candle extreme beyond "
         "the tick-mid extreme by more than the tolerance. The error bound is checked on every tick-window minute (AC-06)."),
        "",
        "| Tick window | Minutes | Artificial | Max high over | Max low under | Suspect flagged | Artificial & suspect |",
        "|---|---|---|---|---|---|---|",
        *[f"| {w['key']} | {w['candle_extrema']['minutes']} | {w['candle_extrema']['artificial_minutes']} | "
          f"{w['candle_extrema']['max_high_overstatement']} | {w['candle_extrema']['max_low_overstatement']} | "
          f"{w['candle_extrema']['suspect_flagged']} | {w['candle_extrema']['artificial_and_suspect']} |"
          for w in r["fixtures"]["tick_windows"] + r["samples"]["tick_windows"] if "candle_extrema" in w],
        "",
        "## Decoder parity", "", f"{r['decoder_parity']}", "",
        "## Sample days (AC-11A): coverage and feed agreement", "",
        "| Sample | Date | Instrument | Bars | Unexpected gap min | XAU-GC corr | lag | basis jump | DXY-DX corr | lag |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in r["samples"]["candles"]:
        d = c["key"].split("/")[1]
        feeds = r["samples"]["feeds"].get(f"{c['label']} {d}", {})
        g, x = feeds.get("XAUUSD vs GC", {}), feeds.get("DXY CFD vs DX", {})
        lines.append(f"| {c['label']} | {d} | {c['key'].split('/')[0]} | {c.get('bars', '—')} | "
                     f"{c.get('missing_unexpected', '—')} | {g.get('return_corr_lag0', '—')} | {g.get('best_lag_min', '—')} | "
                     f"{g.get('max_basis_jump_ex_roll', '—')} | {x.get('return_corr_lag0', '—')} | {x.get('best_lag_min', '—')} |")
    lines += ["", "## Fixture feed comparison", ""]
    for d, feeds in r["fixtures"]["feeds"].items():
        for pair, rec in feeds.items():
            lines.append(f"- {d} {pair}: {rec}")
    lines += ["", "## Tick windows", ""]
    for w in r["fixtures"]["tick_windows"] + r["samples"]["tick_windows"]:
        lines.append(f"- {w['key']} ({w['label']}): status {w['status']}, ticks {w.get('ticks', '—')}, "
                     f"5s bars {w.get('bars_5s', '—')}, candle reconciliation {w.get('candle_reconciliation', '—')}")
    lines += ["", "## Tom chart points (AC-10)", "", *[f"- {p}" for p in r["tom_chart_points"]], "",
              "## AC-11B: deferred full spot history (2018-2024)", "",
              *[f"- {k}: {v['days_present']} / {v['trading_days_required']} trading days" for k, v in r["history_ac11b"].items()],
              ""]
    return "\n".join(lines)


def main() -> None:
    r = evaluate()
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(r, indent=2, default=str) + "\n")
    REPORT_MD.write_text(render_md(r))
    print("VERDICT:", r["result"]["verdict"])
    for k, v in r["result"]["criteria_status"].items():
        print(f"  {k}: {v}")
    print(f"failures: {len(r['failures'])} (unclassified {sum(f['class'] == 'UNCLASSIFIED' for f in r['failures'])})")


if __name__ == "__main__":
    main()
