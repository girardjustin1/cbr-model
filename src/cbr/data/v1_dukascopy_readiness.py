"""Dukascopy-side readiness of the V-1 calibration days (owner ruling D21). Data integrity only.

Usage:
    .venv/bin/python -m cbr.data.v1_dukascopy_readiness     # -> reports/v1-dukascopy-calibration-days.{json,md}

For each pre-registered calibration day (protocol §6.2: 2025-10-22, 2025-11-11) the stored XAUUSD ticks and canonical
STRUCTURE 1m/5s bars are checked for: duplicate ticks, non-positive prices, bad spreads (ask ≤ bid), monotonic
timestamps, expected session gaps (bars vs the scheduled-open calendar), deterministic rebuild from ticks, STRUCTURE
price role and manifest hashes. No FOREXCOM data, no engine, no course window, no outcomes.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.data import dukascopy_fetch as dk
from cbr.data import price_series as ps
from cbr.data.sessions import expected_closed_mask

CALIBRATION_DAYS = ["2025-10-22", "2025-11-11"]
REPORT_JSON = dk.ROOT / "reports" / "v1-dukascopy-calibration-days.json"
REPORT_MD = dk.ROOT / "reports" / "v1-dukascopy-calibration-days.md"


def tick_checks(ticks: pd.DataFrame) -> dict:
    spread = ticks["ask"] - ticks["bid"]
    return {
        "rows": len(ticks),
        "monotonic_timestamps": bool(ticks["ts"].is_monotonic_increasing),
        "duplicate_ticks_exact": int(ticks.duplicated(["ts", "bid", "ask", "bid_vol", "ask_vol"]).sum()),
        "duplicate_timestamps": int(ticks["ts"].duplicated().sum()),
        "non_positive_prices": int(((ticks["bid"] <= 0) | (ticks["ask"] <= 0)).sum()),
        "bad_spreads_ask_le_bid": int((spread <= 0).sum()),
        "spread_quantiles": {q: round(float(spread.quantile(q / 100)), 4) for q in (50, 99, 100)},
        "first_ts": str(ticks["ts"].min()), "last_ts": str(ticks["ts"].max()),
    }


def session_gaps(bars_1m: pd.DataFrame, day: str) -> dict:
    """1m STRUCTURE bars vs the scheduled calendar: missing scheduled-open minutes (vendor gaps) and bars inside a
    scheduled closure (would contradict the calendar)."""
    minutes = pd.date_range(pd.Timestamp(day, tz="UTC"), periods=24 * 60, freq="1min")
    closed = expected_closed_mask(minutes)
    scheduled_open = minutes[~closed]
    missing = scheduled_open.difference(bars_1m.index)
    in_closure = bars_1m.index.intersection(minutes[closed])
    runs = []
    if len(missing):
        s = missing.to_series()
        grp = (s.diff() != pd.Timedelta("1min")).cumsum()
        runs = [[str(g.iloc[0]), len(g)] for _, g in s.groupby(grp)]
    return {"scheduled_open_minutes": len(scheduled_open), "scheduled_closed_minutes": int(closed.sum()),
            "bars_1m": len(bars_1m), "missing_scheduled_open_minutes": len(missing), "missing_runs": runs[:20],
            "bars_inside_scheduled_closure": len(in_closure)}


def day_readiness(day: str) -> dict:
    tick_path = dk.RAW / "xauusd" / "ticks" / f"{day}.parquet"
    out = {"day": day, "ticks_present": tick_path.exists(), "problems": []}
    if not tick_path.exists():
        out["problems"].append("ticks not stored")
        out["ready"] = False
        return out
    raw_manifest = json.loads(dk.MANIFEST.read_text())
    canon = json.loads(cb.MANIFEST.read_text()) if cb.MANIFEST.exists() else {"files": {}}
    ticks = pd.read_parquet(tick_path)
    tick_sha = dk._sha256(tick_path)
    out["ticks"] = tick_checks(ticks)
    entry = raw_manifest["days"].get(f"xauusd/{day}", {})
    out["raw_manifest_hash_matches"] = entry.get("files", {}).get(str(tick_path.relative_to(dk.ROOT))) == tick_sha
    out["tick_sha256"] = tick_sha
    bars = {}
    for tag, freq in (("1m", "1min"), ("5s", "5s")):
        path = cb.OUT / f"structure_{tag}" / f"{day}.parquet"
        rel = str(path.relative_to(dk.ROOT))
        info = {"present": path.exists()}
        if path.exists():
            stored = pd.read_parquet(path)
            rebuilt_a, rebuilt_b = ps.structure_bars(ticks, freq), ps.structure_bars(ticks, freq)
            try:
                ps.require_structure(stored)
                role_ok = True
            except ps.PriceRoleError:
                role_ok = False
            m = canon["files"].get(rel, {})
            info.update({
                "rows": len(stored),
                "price_role_structure": role_ok and bool((stored["price_role"] == ps.STRUCTURE).all())
                and bool((stored["hl_method"] == ps.TICK_MID).all()),
                "deterministic_rebuild": rebuilt_a.equals(rebuilt_b) and rebuilt_a.equals(stored),
                "manifest_sha_matches": m.get("sha256") == dk._sha256(path),
                "manifest_source_tick_sha_matches": m.get("source_sha256") == tick_sha,
                "manifest_role": m.get("price_role"),
            })
            bars[tag] = stored
        out[f"structure_{tag}"] = info
    if "1m" in bars:
        out["session"] = session_gaps(bars["1m"], day)
    t, p = out["ticks"], out["problems"]
    if not t["monotonic_timestamps"]:
        p.append("timestamps not monotonic")
    if t["duplicate_ticks_exact"]:
        p.append(f"{t['duplicate_ticks_exact']} exact duplicate ticks")
    if t["non_positive_prices"]:
        p.append(f"{t['non_positive_prices']} non-positive prices")
    if t["bad_spreads_ask_le_bid"]:
        p.append(f"{t['bad_spreads_ask_le_bid']} ticks with ask ≤ bid")
    if not out["raw_manifest_hash_matches"]:
        p.append("tick file hash differs from the raw manifest")
    for tag in ("1m", "5s"):
        info = out[f"structure_{tag}"]
        if not info["present"]:
            p.append(f"STRUCTURE {tag} bars not built")
            continue
        for key in ("price_role_structure", "deterministic_rebuild", "manifest_sha_matches",
                    "manifest_source_tick_sha_matches"):
            if not info[key]:
                p.append(f"STRUCTURE {tag}: {key} failed")
    s = out.get("session", {})
    if s.get("bars_inside_scheduled_closure"):
        p.append(f"{s['bars_inside_scheduled_closure']} bars inside a scheduled closure")
    out["vendor_gap_minutes"] = s.get("missing_scheduled_open_minutes")          # reported, not a failure (D19-3)
    out["ready"] = not p
    return out


def main() -> None:
    days = [day_readiness(d) for d in CALIBRATION_DAYS]
    report = {"generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(), "decision": "D21",
              "days": days, "all_ready": all(d["ready"] for d in days)}
    REPORT_JSON.write_text(json.dumps(report, indent=2, default=str) + "\n")
    REPORT_MD.write_text(render(report))
    print(json.dumps({d["day"]: {"ready": d["ready"], "problems": d["problems"]} for d in days}, indent=2))


def render(r: dict) -> str:
    L = ["# V-1 Calibration Days: Dukascopy Readiness", "",
         (f"Generated {r['generated_utc']} by `python -m cbr.data.v1_dukascopy_readiness` (owner ruling D21). Data "
          "integrity only: no FOREXCOM data, no engine output, no course windows, no outcomes."), "",
         f"**All calibration days ready: {r['all_ready']}**", "",
         "| Check | " + " | ".join(d["day"] for d in r["days"]) + " |", "|---|" + "---|" * len(r["days"])]

    def row(label, fn):
        vals = []
        for d in r["days"]:
            try:
                vals.append(str(fn(d)))
            except (KeyError, TypeError):
                vals.append("—")
        L.append(f"| {label} | " + " | ".join(vals) + " |")
    row("Ticks stored", lambda d: d["ticks_present"])
    row("Tick rows", lambda d: f"{d['ticks']['rows']:,}")
    row("First / last tick (UTC)", lambda d: f"{d['ticks']['first_ts'][11:23]} / {d['ticks']['last_ts'][11:23]}")
    row("Monotonic timestamps", lambda d: d["ticks"]["monotonic_timestamps"])
    row("Exact duplicate ticks", lambda d: d["ticks"]["duplicate_ticks_exact"])
    row("Duplicate timestamps (distinct quotes)", lambda d: d["ticks"]["duplicate_timestamps"])
    row("Non-positive prices", lambda d: d["ticks"]["non_positive_prices"])
    row("Bad spreads (ask ≤ bid)", lambda d: d["ticks"]["bad_spreads_ask_le_bid"])
    row("Spread p50 / p99 / max (USD)", lambda d: " / ".join(str(v) for v in d["ticks"]["spread_quantiles"].values()))
    row("Tick hash matches raw manifest", lambda d: d["raw_manifest_hash_matches"])
    for tag in ("1m", "5s"):
        row(f"STRUCTURE {tag} rows", lambda d, tag=tag: d[f"structure_{tag}"]["rows"])
        row(f"STRUCTURE {tag} price role / TICK_MID", lambda d, tag=tag: d[f"structure_{tag}"]["price_role_structure"])
        row(f"STRUCTURE {tag} deterministic rebuild = stored", lambda d, tag=tag: d[f"structure_{tag}"]["deterministic_rebuild"])
        row(f"STRUCTURE {tag} manifest sha / source tick sha", lambda d, tag=tag:
            f"{d[f'structure_{tag}']['manifest_sha_matches']} / {d[f'structure_{tag}']['manifest_source_tick_sha_matches']}")
    row("Scheduled-open / closed minutes", lambda d: f"{d['session']['scheduled_open_minutes']} / {d['session']['scheduled_closed_minutes']}")
    row("Missing scheduled-open minutes (vendor gaps)", lambda d: d["session"]["missing_scheduled_open_minutes"])
    row("Bars inside scheduled closure", lambda d: d["session"]["bars_inside_scheduled_closure"])
    row("Ready", lambda d: d["ready"])
    row("Problems", lambda d: "; ".join(d["problems"]) or "none")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
