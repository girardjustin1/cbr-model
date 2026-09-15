"""V-1 FOREXCOM:XAUUSD ingestion (owner rulings D16-3, D19-13/14, D20-10). Data fidelity only.

Usage:
    .venv/bin/python -m cbr.engine.v1_ingest status       # what is present / valid; V1_WAITING_FOR_OWNER_DATA if absent
    .venv/bin/python -m cbr.engine.v1_ingest calibrate    # calibration days only -> reports/v1-calibration.{json,md}
    .venv/bin/python -m cbr.engine.v1_ingest inspect DIR  # any TradingView exports: symbol, timeframe, V-1 coverage

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


def inspect_exports(directory: Path) -> dict:
    """Describe TradingView exports named '<PREFIX>_<SYMBOL>, <TF>.csv': symbol, timeframe, span, and whether each required
    V-1 window is covered. Read-only; nothing is renamed, copied or substituted (D19-13, D20-10)."""
    rows = []
    for path in sorted(Path(directory).glob("*.csv")):
        stem, _, tf = path.stem.partition(", ")
        prefix, _, symbol = stem.partition("_")
        try:
            bars = parity.load_tradingview_csv(path)
        except (ValueError, KeyError) as exc:
            rows.append({"file": path.name, "problem": f"unreadable: {exc}"})
            continue
        tv_symbol = f"{prefix}:{symbol}" if symbol else stem
        covers = {name: bool(bars.index.min() <= a and bars.index.max() >= b - pd.Timedelta("1min"))
                  for name, (a, b, _) in WINDOWS.items()}
        rows.append({"file": path.name, "symbol": tv_symbol, "timeframe": tf, "rows": len(bars),
                     "first": str(bars.index.min()), "last": str(bars.index.max()),
                     "is_required_symbol": tv_symbol == REQUIRED_SYMBOL, "is_1m": tf == REQUIRED_TIMEFRAME,
                     "covers_v1_windows": covers})
    usable = [r for r in rows if r.get("is_required_symbol") and r.get("is_1m") and all(r["covers_v1_windows"].values())]
    return {"directory": str(directory), "exports": rows, "usable_as_v1": [r["file"] for r in usable],
            "verdict": "V1_EXPORT_FOUND" if usable else "DATA_LIMITATION: no FOREXCOM:XAUUSD 1m export covers the V-1 windows"}


def calibrate() -> dict:
    """Tolerance inputs from the two NON-course calibration days only. Nothing is frozen."""
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
    fx = pd.concat([parity.load_tradingview_csv(V1_DIR / n) for n in cal]).sort_index()
    dk = pd.concat([load_structure(WINDOWS[n][0], WINDOWS[n][1], "1m") for n in cal]).sort_index()
    windows = pd.Series(False, index=fx.index)
    for n in cal:
        windows |= (fx.index >= WINDOWS[n][0]) & (fx.index < WINDOWS[n][1])
    result = parity.calibrate(fx[windows.to_numpy()], dk, floor=method["price_floor"],
                              percentile=method["residual_percentile"], round_to=method["round_up_to"],
                              feed_near_multiple=method["feed_near_multiple"])
    report = {"calibration_files": {n: st["files"][n]["sha256"] for n in cal}, "method": method, "result": result,
              "status": "PROPOSED (owner must approve before config/phase13_tolerances.yaml is FROZEN)"}
    REPORT_JSON.write_text(json.dumps(report, indent=2, default=str) + "\n")
    REPORT_MD.write_text(_render(report))
    return report


def _render(r: dict) -> str:
    x = r["result"]
    lines = ["# V-1 Feed Calibration (non-course days)", "", f"Status: **{r['status']}**", "",
             "| Quantity | Value |", "|---|---|",
             f"| Minutes compared | {x['n_minutes']} |", f"| Residual samples (high/low/close) | {x['n_residuals']} |",
             f"| Median offset δ (FOREXCOM − Dukascopy close) | {x['delta_median_offset']:.4f} |",
             f"| Per-day δ | {x['delta_per_day']} |", f"| Residual quantiles | {x['residual_quantiles']} |",
             f"| p{x['residual_percentile']} residual | {x['residual_p']:.4f} |", f"| Max residual | {x['residual_max']:.4f} |",
             f"| Proposed τ_price | {x['tau_price']} |", f"| FEED_NEAR band | {x['feed_near']} |",
             f"| Best lag (minutes) | {x['best_lag_minutes']} |", f"| Zero lag confirmed | {x['zero_lag_confirmed']} |", "",
             f"Calibration file hashes: {r['calibration_files']}", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    cmd = (argv or sys.argv[1:] or ["status"])[0]
    if cmd == "status":
        print(json.dumps(status(), indent=2, default=str))
    elif cmd == "inspect":
        args = argv or sys.argv[1:]
        print(json.dumps(inspect_exports(Path(args[1]) if len(args) > 1 else V1_DIR), indent=2, default=str))
    elif cmd == "calibrate":
        print(json.dumps(calibrate()["result"], indent=2, default=str))
    else:
        raise SystemExit("usage: python -m cbr.engine.v1_ingest [status|calibrate|inspect DIR]")


if __name__ == "__main__":
    main()
