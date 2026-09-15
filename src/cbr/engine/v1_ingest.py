"""V-1 FOREXCOM:XAUUSD ingestion (owner rulings D16-3, D19-13/14, D20-10). Data fidelity only.

Usage:
    .venv/bin/python -m cbr.engine.v1_ingest status       # what is present / valid; V1_WAITING_FOR_OWNER_DATA if absent
    .venv/bin/python -m cbr.engine.v1_ingest calibrate    # calibration days only -> reports/v1-calibration.{json,md}
    .venv/bin/python -m cbr.engine.v1_ingest inspect DIR  # any TradingView exports: symbol, timeframe, V-1 coverage
    .venv/bin/python -m cbr.engine.v1_ingest slice FILE   # FOREXCOM:XAUUSD 1m export -> V-1 window files + provenance

The owner supplies the TradingView exports and screenshots; nothing here creates, substitutes or downloads them. The
calibration command reads ONLY the two non-course calibration files and Dukascopy STRUCTURE bars for those days, reports
the tolerance inputs (D19-11) and never freezes anything: freezing `config/phase13_tolerances.yaml` is an owner decision.
Course-window files are validated for coverage and hashed, never compared with engine output here.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from cbr.data.sessions import expected_closed_mask
from cbr.engine import parity
from cbr.engine.params import ROOT

T = lambda s: pd.Timestamp(s, tz="UTC")
V1_DIR = parity.V1_DIR
SCREENSHOT_DIR = V1_DIR / "screenshots"
SCREENSHOT_TOPICS = {"symbol": "symbol = FOREXCOM:XAUUSD (symbol info / feed identity)",
                     "timezone": "chart timezone = UTC"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
WINDOWS = {
    "v1_CX-LT1-1.csv": (T("2025-10-20 15:00"), T("2025-10-21 03:00"), "course"),
    "v1_CX-TE1-1.csv": (T("2025-10-23 18:00"), T("2025-10-24 06:00"), "course"),
    "v1_CX-LT3-2.csv": (T("2025-11-07 12:00"), T("2025-11-10 04:00"), "course"),
    "v1_cal_2025-10-22.csv": (T("2025-10-22 00:00"), T("2025-10-23 00:00"), "calibration"),
    "v1_cal_2025-11-11.csv": (T("2025-11-11 00:00"), T("2025-11-12 00:00"), "calibration"),
}
WAITING = "V1_WAITING_FOR_OWNER_DATA"
REQUIRED_SYMBOL, REQUIRED_TIMEFRAME = "FOREXCOM:XAUUSD", "1"
STRUCTURE_1M = ROOT / "data" / "normalized" / "xauusd" / "structure_1m"
REPORT_JSON, REPORT_MD = ROOT / "reports" / "v1-calibration.json", ROOT / "reports" / "v1-calibration.md"
assert list(WINDOWS) == parity.V1_FILES


def validate_file(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    """Load, hash and check coverage of one export against its required window."""
    out = {"file": path.name, "present": path.exists(), "valid": False, "problems": []}
    if not path.exists():
        out["problems"].append("missing")
        return out
    out["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        bars = parity.load_tradingview_csv(path)
    except (ValueError, KeyError) as exc:
        out["problems"].append(f"unreadable: {exc}")
        return out
    inside = bars[(bars.index >= start) & (bars.index < end)]
    expected = pd.date_range(start, end, freq="1min", inclusive="left")
    expected = expected[~expected_closed_mask(expected)]
    missing = expected.difference(inside.index)
    step = inside.index.to_series().diff().dropna()
    out.update({"rows": len(bars), "rows_in_window": len(inside), "first": str(bars.index.min()),
                "last": str(bars.index.max()), "expected_open_minutes": len(expected),
                "missing_open_minutes": len(missing), "non_1m_steps_within_session": int((step < pd.Timedelta("1min")).sum())})
    if bars.index.min() > start or bars.index.max() < end - pd.Timedelta("1min"):
        out["problems"].append(f"does not cover the required window {start} → {end}")
    if out["non_1m_steps_within_session"]:
        out["problems"].append("bar spacing below 1 minute: not a 1m export")
    if len(missing):
        out["problems"].append(f"{len(missing)} scheduled-open minutes absent (DATA_LIMITATION candidate)")
    out["valid"] = not out["problems"]
    return out


def screenshots() -> dict:
    found = {topic: sorted(p.name for p in SCREENSHOT_DIR.glob("*") if p.suffix.lower() in IMAGE_SUFFIXES
                           and topic in p.name.lower()) if SCREENSHOT_DIR.exists() else []
             for topic in SCREENSHOT_TOPICS}
    return {"dir": str(SCREENSHOT_DIR.relative_to(ROOT)), "required": SCREENSHOT_TOPICS, "found": found,
            "complete": all(found.values())}


def dukascopy_days() -> dict:
    days = sorted({d.date().isoformat() for name, (a, b, kind) in WINDOWS.items() if kind == "calibration"
                   for d in pd.date_range(a.floor("D"), b, freq="D", inclusive="left")})
    return {d: (STRUCTURE_1M / f"{d}.parquet").exists() for d in days}


def status() -> dict:
    files = {name: validate_file(V1_DIR / name, a, b) | {"kind": kind} for name, (a, b, kind) in WINDOWS.items()}
    shots, duk = screenshots(), dukascopy_days()
    absent = [n for n, f in files.items() if not f["present"]]
    state = WAITING if (absent or not shots["complete"]) else (
        "V1_FILES_INVALID" if not all(f["valid"] for f in files.values()) else
        "V1_READY_FOR_CALIBRATION" if all(duk.values()) else "V1_WAITING_FOR_DUKASCOPY_CALIBRATION_DAYS")
    return {"state": state, "files": files, "missing_files": absent, "screenshots": shots,
            "dukascopy_calibration_days": duk,
            "note": "Files come from the owner's TradingView export; never fabricated or substituted (D20-10)."}


# ------------------------------------------------------------------ export inspection (D22)

TIMEFRAMES = {"1": "1min", "5": "5min", "15": "15min", "60": "1h", "240": "4h", "1D": "1D"}
OCT_NOV_2025 = (T("2025-10-01"), T("2025-12-01"))
GOLD_TICKERS, DXY_TICKERS = {"XAUUSD", "GOLD"}, {"DXY"}
REQUIRED_MISSING = "SYMBOL_MISMATCH"


def parse_export_name(name: str) -> dict:
    """TradingView's default export name is '<EXCHANGE>_<TICKER>, <interval>.csv' (e.g. 'FOREXCOM_XAUUSD, 1.csv')."""
    stem = name[:-4] if name.lower().endswith(".csv") else name
    sym, _, tf = stem.partition(", ")
    exchange, _, ticker = sym.partition("_")
    return {"exchange": exchange if ticker else None, "ticker": ticker or sym, "timeframe": tf or None,
            "tradingview_symbol": f"{exchange}:{ticker}" if ticker else None}


def _window_coverage(bars: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, tf: str | None) -> dict:
    """FULL / PARTIAL / NONE for [start, end). Intraday (≤ 1h): every bar interval that holds a scheduled-open minute
    must be present. 4h / 1D: bar alignment is session-based, so coverage is span-based (SPAN)."""
    inside = bars[(bars.index >= start) & (bars.index < end)]
    freq = TIMEFRAMES.get(tf or "")
    if freq is None:
        return {"coverage": "UNKNOWN_TIMEFRAME", "bars_in_window": len(inside)}
    step = pd.Timedelta(freq)
    if step > pd.Timedelta("1h"):
        spans = bool(len(bars)) and bars.index.min() <= start and bars.index.max() + step >= end
        return {"coverage": "SPAN" if spans else ("PARTIAL" if len(inside) else "NONE"), "bars_in_window": len(inside)}
    opens = pd.date_range(start.floor(freq), end, freq=freq, inclusive="left")
    mins = pd.date_range(start, end, freq="1min", inclusive="left")
    open_mins = mins[~expected_closed_mask(mins)]
    expected = opens[opens.isin(open_mins.floor(freq))]
    missing = expected.difference(inside.index)
    cov = "FULL" if len(expected) and not len(missing) else ("PARTIAL" if len(inside) else "NONE")
    return {"coverage": cov, "bars_in_window": len(inside), "expected_bars": len(expected), "missing_bars": len(missing)}


def inspect_export(path: Path) -> dict:
    """Metadata, timestamp basis and V-1 coverage of one TradingView export. Read-only."""
    meta = parse_export_name(path.name)
    raw = pd.read_csv(path, nrows=5)
    cols = [c.strip() for c in raw.columns]
    out = {"file": path.name, "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), **meta,
           "columns": cols, "ohlc_columns": all(c in [x.lower() for x in cols] for c in ("open", "high", "low", "close"))}
    time_numeric = pd.api.types.is_numeric_dtype(raw[cols[0]]) if cols else False
    out["timestamp_basis"] = ("unix epoch seconds (UTC by definition; chart timezone setting doesn't alter them)"
                              if time_numeric else "ISO text (needs an explicit UTC offset)")
    try:
        bars = parity.load_tradingview_csv(path)
    except (ValueError, KeyError) as exc:
        out["problem"] = f"unreadable: {exc}"
        return out
    full = pd.read_csv(path)
    vol_col = next((c for c in full.columns if c.strip().lower() == "volume"), None)
    step = bars.index.to_series().diff().dropna()
    out.update({"timezone": "UTC", "rows": len(bars), "first": str(bars.index.min()), "last": str(bars.index.max()),
                "modal_bar_spacing": str(step.mode().iloc[0]) if len(step) else None,
                "volume_column": vol_col, "volume_non_null": int(full[vol_col].notna().sum()) if vol_col else 0,
                "extra_columns": [c for c in cols if c.lower() not in ("time", "open", "high", "low", "close", "volume")]})
    in_octnov = bars[(bars.index >= OCT_NOV_2025[0]) & (bars.index < OCT_NOV_2025[1])]
    out["oct_nov_2025"] = {"bars": len(in_octnov),
                           "fully_spanned": bool(bars.index.min() <= OCT_NOV_2025[0] and bars.index.max() >= OCT_NOV_2025[1] - pd.Timedelta("1D"))}
    out["v1_windows"] = {name: _window_coverage(bars, a, b, meta["timeframe"]) for name, (a, b, _) in WINDOWS.items()}
    ticker = (meta["ticker"] or "").upper()
    out["instrument"] = "GOLD" if ticker in GOLD_TICKERS else "DXY" if ticker in DXY_TICKERS else "OTHER"
    reasons = []
    if out["instrument"] == "GOLD":
        if meta["tradingview_symbol"] != REQUIRED_SYMBOL:
            reasons.append(f"{REQUIRED_MISSING}: {meta['tradingview_symbol']} is not {REQUIRED_SYMBOL}")
        if meta["timeframe"] != REQUIRED_TIMEFRAME:
            reasons.append("not a 1-minute export (V-1 needs 1m OHLC)")
        not_full = [n for n, c in out["v1_windows"].items() if c["coverage"] != "FULL"]
        if meta["timeframe"] == REQUIRED_TIMEFRAME and not_full:
            reasons.append("ONE_MINUTE_HISTORY_INSUFFICIENT for " + ", ".join(not_full))
            out["one_minute_days_short"] = {n: max(0, (bars.index.min() - WINDOWS[n][0]).days) for n in not_full}
        out["v1_eligible"] = not reasons
        out["classification"] = ("V1_SOURCE" if not reasons else
                                 "REFERENCE_ONLY" if any(REQUIRED_MISSING in r for r in reasons) else "TRADINGVIEW_REFERENCE_FIXTURE")
        if meta["timeframe"] != REQUIRED_TIMEFRAME and "TRADINGVIEW_REFERENCE_FIXTURE" not in out["classification"]:
            out["classification"] += "; TRADINGVIEW_REFERENCE_FIXTURE"
    else:
        out["v1_eligible"] = False
        reasons.append("not XAUUSD (V-1 is XAUUSD feed fidelity); informational")
        out["classification"] = "TRADINGVIEW_REFERENCE_FIXTURE (informational)"
    out["reasons"] = reasons
    return out


def inspect_exports(directory: Path) -> dict:
    """Inspect every CSV export in `directory`. Read-only; nothing renamed, copied or substituted (D19-13, D20-10)."""
    rows = [inspect_export(p) for p in sorted(Path(directory).glob("*.csv"))]
    eligible = [r["file"] for r in rows if r.get("v1_eligible")]
    return {"directory": str(directory), "exports": rows, "usable_as_v1": eligible, "state": v1_state(rows, status())}


def v1_state(exports: list[dict], st: dict) -> str:
    """One project V-1 state (D22-10). Order: ready > partially ready > symbol mismatch > 1m history insufficient > waiting."""
    files_ok = all(f["valid"] for f in st["files"].values())
    if files_ok and st["screenshots"]["complete"] and all(st["dukascopy_calibration_days"].values()):
        return "V1_READY_FOR_CALIBRATION"
    gold = [e for e in exports if e.get("instrument") == "GOLD"]
    sliceable = [e for e in gold if e.get("tradingview_symbol") == REQUIRED_SYMBOL and e.get("timeframe") == REQUIRED_TIMEFRAME
                 and any(c["coverage"] == "FULL" for c in e.get("v1_windows", {}).values())]
    if sliceable or any(f["valid"] for f in st["files"].values()):
        return "V1_PARTIALLY_READY"
    if gold and not any(e.get("tradingview_symbol") == REQUIRED_SYMBOL for e in gold):
        return "V1_SYMBOL_MISMATCH"
    if any(e.get("tradingview_symbol") == REQUIRED_SYMBOL for e in gold):
        return "V1_ONE_MINUTE_HISTORY_INSUFFICIENT"
    return WAITING


REPORTS_DIR = ROOT / "reports"
_SHORT = {"v1_cal_2025-10-22.csv": "CAL 10/22", "v1_cal_2025-11-11.csv": "CAL 11/11", "v1_CX-LT1-1.csv": "CX-LT1-1",
          "v1_CX-TE1-1.csv": "CX-TE1-1", "v1_CX-LT3-2.csv": "CX-LT3-2"}


def write_inspection_report(directory: Path) -> dict:
    """Coverage matrices for every export in `directory` (Gold: V-1 eligibility; DXY: informational). Metadata only."""
    from datetime import UTC, datetime

    d = inspect_exports(directory)
    d["generated_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    stem = f"tradingview-exports-inspection-{Path(directory).name}"
    (REPORTS_DIR / f"{stem}.json").write_text(json.dumps(d, indent=2, default=str) + "\n")
    cols = list(_SHORT)
    head = "| File | Symbol | TF | Rows | Start (UTC) | End (UTC) | " + " | ".join(_SHORT[c] for c in cols)
    L = ["# TradingView Exports: Inspection and V-1 Coverage", "",
         (f"Generated {d['generated_utc']} by `python -m cbr.engine.v1_ingest inspect {directory} --report`. File and "
          "metadata inspection only: no prices reproduced, no engine output, no comparison with course examples."), "",
         f"**V-1 state: `{d['state']}`** · usable as V-1: {d['usable_as_v1'] or 'none'}", "",
         ("Coverage: FULL = every bar holding a scheduled-open minute is present; SPAN = 4h/1D bars span the window; "
          "NONE = no bars in the window."), ""]
    for inst, title in (("GOLD", "Gold (XAUUSD)"), ("DXY", "DXY (informational)")):
        rows = [r for r in d["exports"] if r.get("instrument") == inst]
        if not rows:
            continue
        extra = " | V-1 eligible | Classification | Reason |" if inst == "GOLD" else " | Classification |"
        L += [f"## {title}", "", head + extra, "|" + "---|" * (6 + len(cols) + (3 if inst == "GOLD" else 1))]
        for r in rows:
            cov = " | ".join(r["v1_windows"][c]["coverage"] for c in cols)
            base = f"| {r['file']} | {r['tradingview_symbol']} | {r['timeframe']} | {r['rows']} | {r['first'][:16]} | {r['last'][:16]} | {cov}"
            L.append(base + (f" | {'yes' if r['v1_eligible'] else 'no'} | {r['classification']} | {'; '.join(r['reasons'])} |"
                             if inst == "GOLD" else f" | {r['classification']} |"))
        L += ["", "| File | Timestamp basis | OHLC | Volume | Extra columns | Oct–Nov 2025 bars | SHA-256 |", "|---|---|---|---|---|---|---|"]
        L += [f"| {r['file']} | {r['timestamp_basis']} | {r['ohlc_columns']} | {r['volume_column']} ({r['volume_non_null']} non-null) | "
              f"{', '.join(r['extra_columns']) or '—'} | {r['oct_nov_2025']['bars']} | `{r['sha256'][:16]}…` |" for r in rows]
        short = [r for r in rows if r.get("one_minute_days_short")]
        if short:
            L += ["", "**ONE_MINUTE_HISTORY_INSUFFICIENT**", ""]
            L += [f"- {r['file']}: earliest {r['first']}, latest {r['last']}; days short of each window start: "
                  + ", ".join(f"{_SHORT[k]} {v}" for k, v in r["one_minute_days_short"].items()) for r in short]
        L.append("")
    (REPORTS_DIR / f"{stem}.md").write_text("\n".join(L))
    return d


# ------------------------------------------------------------------ source families and identity (D23)

SOURCE_MANIFEST = ROOT / "reports" / "tradingview-source-manifest.json"
FAMILY_TOM, FAMILY_OWNER = "A_TOM_CHART_DATA", "B_OWNER_TRADINGVIEW_REFERENCE"


def identity_class(info: dict, screenshots_complete: bool) -> str:
    """Identity standard (D23). TradingView names exports from the chart symbol, but a CSV carries no symbol field:
    the file name alone gives PROBABLE_<source>; CONFIRMED needs independent identity evidence (symbol-info screenshot).
    Another symbol → DIFFERENT_SOURCE; no parseable symbol → SOURCE_UNVERIFIABLE."""
    sym = info.get("tradingview_symbol")
    if not sym:
        return "SOURCE_UNVERIFIABLE"
    expected = {"GOLD": REQUIRED_SYMBOL, "DXY": "TVC:DXY"}.get(info.get("instrument"))
    if expected is None:
        return "SOURCE_UNVERIFIABLE"
    label = "FOREXCOM" if info["instrument"] == "GOLD" else "TVC_DXY"
    if sym != expected:
        return "DIFFERENT_SOURCE"
    return f"CONFIRMED_{label}" if screenshots_complete else f"PROBABLE_{label}"


def purposes(info: dict) -> list[str]:
    """Allowed uses by coverage and identity. Calibration windows and course windows are listed separately and never
    share a purpose: course-window data can't set tolerances (D23-7)."""
    out = []
    windows = info.get("v1_windows", {})
    if info.get("instrument") == "GOLD":
        if info.get("tradingview_symbol") != REQUIRED_SYMBOL:
            return ["REFERENCE_ONLY"]
        if info.get("timeframe") == REQUIRED_TIMEFRAME:
            cal = [n for n, (_, _, k) in WINDOWS.items() if k == "calibration" and windows[n]["coverage"] == "FULL"]
            course = [n for n, (_, _, k) in WINDOWS.items() if k == "course" and windows[n]["coverage"] == "FULL"]
            out += (["V1_CALIBRATION"] if cal else []) + (["COURSE_PARITY"] if course else [])
            if len(cal) + len(course) < len(WINDOWS):
                out.append("INSUFFICIENT_COVERAGE")
        out.append("MULTITIMEFRAME_REFERENCE")
    elif info.get("instrument") == "DXY":
        out += ["DXY_REFERENCE", "MULTITIMEFRAME_REFERENCE"]
    return out


def compare_exports(a: Path, b: Path, *, exclude_windows: bool = True) -> dict:
    """Bar-by-bar agreement of two exports on overlapping timestamps (source-identity evidence only). V-1 course and
    calibration windows are excluded by default."""
    x, y = parity.load_tradingview_csv(a), parity.load_tradingview_csv(b)
    j = x.join(y, how="inner", lsuffix="_a", rsuffix="_b")
    if exclude_windows:
        keep = pd.Series(True, index=j.index)
        for s0, e0, _ in WINDOWS.values():
            keep &= ~((j.index >= s0) & (j.index < e0))
        j = j[keep.to_numpy()]
    if not len(j):
        return {"a": a.name, "b": b.name, "overlap_bars": 0}
    diff = (j["close_a"] - j["close_b"]).abs()
    return {"a": a.name, "b": b.name, "overlap_bars": len(j), "first": str(j.index.min()), "last": str(j.index.max()),
            "identical_fraction": {f: float((j[f"{f}_a"].round(6) == j[f"{f}_b"].round(6)).mean())
                                   for f in ("open", "high", "low", "close")},
            "close_abs_diff_median": float(diff.median()), "close_abs_diff_max": float(diff.max())}


def build_source_manifest(families: dict[str, Path]) -> dict:
    """Immutable-source manifest (D23-8): one record per original export, never modifying it."""
    from datetime import UTC, datetime

    shots = screenshots()["complete"]
    records = []
    for family, directory in families.items():
        for path in sorted(Path(directory).glob("*.csv")):
            info = inspect_export(path)
            records.append({
                "family": family, "source_path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                "filename": path.name, "sha256": info["sha256"], "symbol": info.get("tradingview_symbol"),
                "provider": info.get("exchange"), "instrument": info.get("instrument"), "timeframe": info.get("timeframe"),
                "start": info.get("first"), "end": info.get("last"), "timezone": info.get("timezone"),
                "timestamp_basis": info.get("timestamp_basis"), "row_count": info.get("rows"),
                "volume_non_null": info.get("volume_non_null"), "identity": identity_class(info, shots),
                "classification": info.get("classification"), "purpose": purposes(info),
                "v1_window_coverage": {n: c["coverage"] for n, c in info.get("v1_windows", {}).items()},
                "derived_slices": []})
    out = {"generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(), "decision": "D23",
           "families": {k: str(Path(v).relative_to(ROOT)) if Path(v).is_relative_to(ROOT) else Path(v).name
                        for k, v in families.items()}, "records": records}
    SOURCE_MANIFEST.write_text(json.dumps(out, indent=2, default=str) + "\n")
    return out


# ------------------------------------------------------------------ deterministic slicing (D22-8)

PROVENANCE = V1_DIR / "v1_provenance.json"


def derive_slices(source: Path) -> dict:
    """Create the V-1 logical window files from ONE immutable FOREXCOM:XAUUSD 1m export: each covered window is written
    as the original CSV rows whose time falls in [start, end), with source hash, slice hash and row range recorded in
    `v1_provenance.json`. Refuses any other symbol or timeframe; never overwrites a different existing slice."""
    info = inspect_export(source)
    if info.get("tradingview_symbol") != REQUIRED_SYMBOL or info.get("timeframe") != REQUIRED_TIMEFRAME:
        raise SystemExit(f"{REQUIRED_MISSING}: {source.name} is {info.get('tradingview_symbol')} "
                         f"timeframe {info.get('timeframe')}; V-1 slices need {REQUIRED_SYMBOL} 1m")
    raw = pd.read_csv(source)
    tcol = raw.columns[0]
    t = pd.to_datetime(raw[tcol], unit="s", utc=True) if pd.api.types.is_numeric_dtype(raw[tcol]) \
        else pd.to_datetime(raw[tcol], format="ISO8601").dt.tz_convert("UTC")
    lines = source.read_text().splitlines(keepends=True)
    prov = json.loads(PROVENANCE.read_text()) if PROVENANCE.exists() else {"slices": {}}
    written = {}
    for name, (a, b, _) in WINDOWS.items():
        if info["v1_windows"][name]["coverage"] != "FULL":
            continue
        idx = [i for i, ok in enumerate(((t >= a) & (t < b)).to_numpy()) if ok]
        body = lines[0] + "".join(lines[i + 1] for i in idx)
        target = V1_DIR / name
        digest = hashlib.sha256(body.encode()).hexdigest()
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"{target.name} exists with different content; not overwritten")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
        written[name] = {"source_file": source.name, "source_sha256": info["sha256"], "slice_sha256": digest,
                         "rows": len(idx), "window": [str(a), str(b)]}
    prov["slices"].update(written)
    PROVENANCE.write_text(json.dumps(prov, indent=2) + "\n")
    return written


# ------------------------------------------------------------------ calibration (D19-11, D21, D22-1)

TIME_BLOCKS = [("00-07 Asia", 0, 7), ("07-12 London", 7, 12), ("12-17 London/NY", 12, 17), ("17-21 New York", 17, 21),
               ("21-24 rollover/late", 21, 24)]           # IMPL reporting blocks (UTC hours); not a rule
FIELDS = ("open", "high", "low", "close")
QUANTILES = (50, 90, 95, 99)


def _q(x: pd.Series) -> dict:
    x = x.dropna()
    if not len(x):
        return {"n": 0}
    return {"n": len(x), **{f"p{q}": float(np.percentile(x, q)) for q in QUANTILES}, "max": float(x.max())}


def calibration_measurements(fx: pd.DataFrame, dk: pd.DataFrame, windows: list[tuple[pd.Timestamp, pd.Timestamp]],
                             *, delta: float, tau: float | None) -> dict:
    """Descriptive V-1 measurements beyond the approved tolerance formula (D22-1). δ is the approved close-median
    offset; nothing here changes the p95 / rounding / zero-lag rules."""
    mins = pd.DatetimeIndex([])
    for a, b in windows:
        m = pd.date_range(a, b, freq="1min", inclusive="left")
        mins = mins.append(m[~expected_closed_mask(m)])
    fx_w, dk_w = fx[fx.index.isin(mins)], dk[dk.index.isin(mins)]
    j = fx_w[list(FIELDS)].join(dk_w[list(FIELDS)], how="inner", lsuffix="_fx", rsuffix="_dk")
    diff = pd.DataFrame({f: j[f"{f}_fx"] - j[f"{f}_dk"] for f in FIELDS})
    resid = (diff - delta).abs()
    out = {
        "scheduled_open_minutes": len(mins), "matched_minutes": len(j),
        "missing_minutes_forexcom": len(mins.difference(fx_w.index)),
        "missing_minutes_dukascopy": len(mins.difference(dk_w.index)),
        "per_field": {f: {"offset_median": float(diff[f].median()), "offset_mean": float(diff[f].mean()),
                          "residual_after_delta": _q(resid[f]),
                          "residual_after_own_median": _q((diff[f] - diff[f].median()).abs())} for f in FIELDS},
        "pooled_hlc_residual_after_delta": _q(pd.concat([resid[f] for f in ("high", "low", "close")])),
        "pooled_ohlc_residual_after_delta": _q(pd.concat([resid[f] for f in FIELDS])),
    }
    days = diff.groupby(diff.index.floor("1D"))
    out["per_day"] = {str(d.date()): {"n": len(g), **{f"offset_median_{f}": float(g[f].median()) for f in FIELDS}}
                      for d, g in days}
    hours = diff["close"].groupby(diff.index.hour).median()
    out["intraday_hourly_close_offset_median"] = {int(h): float(v) for h, v in hours.items()}
    out["intraday_close_offset_range"] = float(hours.max() - hours.min()) if len(hours) else None
    blocks = {}
    for label, h0, h1 in TIME_BLOCKS:
        sel = (diff.index.hour >= h0) & (diff.index.hour < h1)
        g = diff[sel]
        blocks[label] = {"n": int(sel.sum()), "close_offset_median": float(g["close"].median()) if len(g) else None,
                         "hlc_residual_after_delta": _q(pd.concat([resid.loc[sel, f] for f in ("high", "low", "close")]))}
    out["time_blocks"] = blocks
    rng = (j["high_dk"] - j["low_dk"])
    terc = pd.qcut(rng.rank(method="first"), 3, labels=["low", "mid", "high"]) if len(rng) >= 3 else None
    out["volatility_regimes_by_dukascopy_1m_range"] = {} if terc is None else {
        str(lbl): {"n": int((terc == lbl).sum()), "dk_range_median": float(rng[terc == lbl].median()),
                   "close_offset_median": float(diff.loc[terc == lbl, "close"].median()),
                   "hlc_residual_after_delta": _q(pd.concat([resid.loc[terc == lbl, f] for f in ("high", "low", "close")]))}
        for lbl in ("low", "mid", "high")}
    medians = [b["close_offset_median"] for b in blocks.values() if b["close_offset_median"] is not None]
    day_meds = [v["offset_median_close"] for v in out["per_day"].values()]
    field_meds = [out["per_field"][f]["offset_median"] for f in FIELDS]
    regime_meds = [v["close_offset_median"] for v in out["volatility_regimes_by_dukascopy_1m_range"].values()]

    def dev(vals):
        return None if not vals else float(max(abs(v - delta) for v in vals))
    out["stability"] = {
        "reference": "max |group median offset − δ|, compared with the proposed τ_price (descriptive, not a rule)",
        "tau_price": tau,
        "time_block_max_deviation": dev(medians), "per_day_max_deviation": dev(day_meds),
        "ohlc_field_max_deviation": dev(field_meds), "volatility_regime_max_deviation": dev(regime_meds),
    }
    if tau is not None:
        for k in ("time_block", "per_day", "ohlc_field", "volatility_regime"):
            v = out["stability"][f"{k}_max_deviation"]
            out["stability"][f"{k}_within_tau"] = None if v is None else v <= tau
    return out


def calibrate() -> dict:
    """V-1 calibration from the two NON-course calibration days only (protocol §4.3, D21 order). Nothing is frozen.
    If the best lag isn't 0 minutes, calibration STOPS: no tolerance is proposed and no compensation is applied."""
    st = status()
    cal = [n for n, (_, _, kind) in WINDOWS.items() if kind == "calibration"]
    problems = [f"{n}: {st['files'][n]['problems']}" for n in cal if not st["files"][n]["valid"]]
    problems += [f"Dukascopy STRUCTURE 1m missing for {d}" for d, ok in st["dukascopy_calibration_days"].items() if not ok]
    if not st["screenshots"]["complete"]:
        problems.append("identity / timezone screenshots missing")
    if problems:
        raise SystemExit(f"{WAITING if st['missing_files'] else 'V1_NOT_CALIBRATABLE'}:\n- " + "\n- ".join(problems))
    from cbr.data.canonical_bars import load_structure

    method = parity.load_tolerances()["method"]
    windows = [(WINDOWS[n][0], WINDOWS[n][1]) for n in cal]
    fx = pd.concat([parity.load_tradingview_csv(V1_DIR / n) for n in cal]).sort_index()
    dk = pd.concat([load_structure(a, b, "1m") for a, b in windows]).sort_index()
    report = run_calibration(fx, dk, windows, method)
    report["calibration_files"] = {n: st["files"][n]["sha256"] for n in cal}
    REPORT_JSON.write_text(json.dumps(report, indent=2, default=str) + "\n")
    REPORT_MD.write_text(_render(report))
    return report


def run_calibration(fx: pd.DataFrame, dk: pd.DataFrame, windows: list, method: dict) -> dict:
    sel = pd.Series(False, index=fx.index)
    for a, b in windows:
        sel |= (fx.index >= a) & (fx.index < b)
    fx = fx[sel.to_numpy()]
    result = parity.calibrate(fx, dk, floor=method["price_floor"], percentile=method["residual_percentile"],
                              round_to=method["round_up_to"], feed_near_multiple=method["feed_near_multiple"])
    stopped = not result["zero_lag_confirmed"]
    if stopped:
        result = {**result, "tau_price": None, "feed_near": None}
    meas = calibration_measurements(fx, dk, windows, delta=result["delta_median_offset"], tau=result["tau_price"])
    return {"method": method, "result": result, "measurements": meas,
            "status": ("STOPPED: best lag ≠ 0 minutes; no tolerance proposed, no compensation (owner review)" if stopped
                       else "PROPOSED (owner must approve δ, τ_price, FEED_NEAR, zero-lag result and time tolerances "
                            "before config/phase13_tolerances.yaml is FROZEN)")}


def _render(r: dict) -> str:
    x, m = r["result"], r["measurements"]
    fmt = lambda v: "—" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))
    L = ["# V-1 Feed Calibration (non-course days)", "", f"Status: **{r['status']}**", "",
         "## Approved tolerance method (protocol §4.3)", "", "| Quantity | Value |", "|---|---|",
         f"| Matched minutes | {x['n_minutes']} |", f"| Median offset δ (close) | {fmt(x['delta_median_offset'])} |",
         f"| p{x['residual_percentile']} residual (high/low/close after δ) | {fmt(x['residual_p'])} |",
         f"| Max residual | {fmt(x['residual_max'])} |", f"| Proposed τ_price | {fmt(x['tau_price'])} |",
         f"| FEED_NEAR band | {fmt(x['feed_near'])} |", f"| Best lag (minutes) | {x['best_lag_minutes']} |",
         f"| Zero lag confirmed | {x['zero_lag_confirmed']} |", "",
         "## Coverage", "", (f"Scheduled-open minutes {m['scheduled_open_minutes']} · matched {m['matched_minutes']} · "
                             f"missing FOREXCOM {m['missing_minutes_forexcom']} · missing Dukascopy {m['missing_minutes_dukascopy']}"), "",
         "## Per OHLC field", "", "| Field | Offset median | p50 | p90 | p95 | p99 | max (after δ) |", "|---|---|---|---|---|---|---|"]
    for f in FIELDS:
        q = m["per_field"][f]["residual_after_delta"]
        L.append(f"| {f} | {fmt(m['per_field'][f]['offset_median'])} | " + " | ".join(fmt(q.get(k)) for k in ("p50", "p90", "p95", "p99", "max")) + " |")
    L += ["", "## Per day", "", "| Day | n | open | high | low | close (offset medians) |", "|---|---|---|---|---|---|"]
    L += [f"| {d} | {v['n']} | " + " | ".join(fmt(v[f'offset_median_{f}']) for f in FIELDS) + " |" for d, v in m["per_day"].items()]
    L += ["", "## Time blocks (UTC)", "", "| Block | n | close offset median | HLC p95 after δ |", "|---|---|---|---|"]
    L += [f"| {k} | {v['n']} | {fmt(v['close_offset_median'])} | {fmt(v['hlc_residual_after_delta'].get('p95'))} |"
          for k, v in m["time_blocks"].items()]
    L += ["", "## Volatility regimes (Dukascopy 1m range terciles)", "", "| Regime | n | range median | close offset median | HLC p95 after δ |", "|---|---|---|---|---|"]
    L += [f"| {k} | {v['n']} | {fmt(v['dk_range_median'])} | {fmt(v['close_offset_median'])} | {fmt(v['hlc_residual_after_delta'].get('p95'))} |"
          for k, v in m["volatility_regimes_by_dukascopy_1m_range"].items()]
    L += ["", "## Stability (descriptive)", "", f"Intraday hourly close-offset range: {fmt(m['intraday_close_offset_range'])}", ""]
    L += [f"- {k}: {fmt(v)}" for k, v in m["stability"].items()]
    L += ["", f"Calibration file hashes: {r.get('calibration_files')}", ""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> None:
    cmd = (argv or sys.argv[1:] or ["status"])[0]
    if cmd == "status":
        print(json.dumps(status(), indent=2, default=str))
    elif cmd == "inspect":
        args = argv or sys.argv[1:]
        target = Path(args[1]) if len(args) > 1 and not args[1].startswith("--") else V1_DIR
        out = write_inspection_report(target) if "--report" in args else inspect_exports(target)
        print(json.dumps({"state": out["state"], "usable_as_v1": out["usable_as_v1"],
                          "exports": {r["file"]: r.get("classification") for r in out["exports"]}}, indent=2))
    elif cmd == "sources":
        args = argv or sys.argv[1:]
        fams = dict(x.split("=", 1) for x in args[1:]) or {FAMILY_TOM: "references/tom-chart-data",
                                                            FAMILY_OWNER: "references/charts"}
        out = build_source_manifest({k: ROOT / v for k, v in fams.items()})
        print(json.dumps([[r["family"], r["filename"], r["identity"], r["purpose"]] for r in out["records"]], indent=1))
    elif cmd == "slice":
        args = argv or sys.argv[1:]
        print(json.dumps(derive_slices(Path(args[1])), indent=2))
    elif cmd == "calibrate":
        print(json.dumps(calibrate()["result"], indent=2, default=str))
    else:
        raise SystemExit("usage: python -m cbr.engine.v1_ingest [status|inspect DIR|slice FILE|calibrate]")


if __name__ == "__main__":
    main()
