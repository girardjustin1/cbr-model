"""Historical acquisition accounting and the availability pilot check (owner ruling D40 §4-8).

Data quality only: no signals, no fills, no P&L. Nothing here downloads — it reports on what the fetcher produced,
reading the per-hour artefact cache, the day manifest and the stored tick files.

    .venv/bin/python -m cbr.data.acquisition_status pilot            # D40 §5 per-day acceptance
    .venv/bin/python -m cbr.data.acquisition_status span 2018 2024   # D40 §8 completeness accounting
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.data import dukascopy_fetch as dk
from cbr.data import price_series as ps
from cbr.data.sessions import expected_closed

# Predeclared in D40 §4 and committed before any byte was fetched.
PILOT_DAYS = [date(2018, 2, 14), date(2018, 9, 12), date(2019, 3, 13),
              date(2019, 10, 16), date(2020, 3, 18), date(2020, 9, 16)]
REPORTS = dk.ROOT / "reports"


def _cache_hours(instrument: str, day: date) -> dict[int, int]:
    """Hour → cached artefact size. An empty artefact is Dukascopy's 404: no file for that hour."""
    out = {}
    for h in range(24):
        p = dk.CACHE / instrument / f"{day.isoformat()}_{h:02d}.bi5"
        if p.exists():
            out[h] = p.stat().st_size
    return out


def _scheduled_closed(day: date, hour: int) -> bool:
    return bool(expected_closed(pd.Timestamp(datetime(day.year, day.month, day.day, hour, tzinfo=UTC))))


def day_report(day: date, instrument: str = "xauusd") -> dict:
    """D40 §5 acceptance for one day. Every check is observable from stored artefacts."""
    key = f"{instrument}/{day.isoformat()}"
    manifest = json.loads(dk.MANIFEST.read_text()) if dk.MANIFEST.exists() else {"days": {}}
    entry = manifest["days"].get(key)
    tick_path = dk.RAW / instrument / "ticks" / f"{day.isoformat()}.parquet"
    cached = _cache_hours(instrument, day)
    empty_hours = sorted(h for h, size in cached.items() if size == 0)
    data_hours = sorted(h for h, size in cached.items() if size > 0)
    unexpected_empty = [h for h in empty_hours if not _scheduled_closed(day, h)]
    checks: dict[str, bool | None] = {
        "hourly_files_attempted": len(cached) == 24,
        "decoder_succeeded": tick_path.exists(),
        "manifest_entry": entry is not None,
    }
    out = {"day": day.isoformat(), "instrument": instrument, "hours_cached": len(cached),
           "hours_with_data": len(data_hours), "hours_empty": len(empty_hours),
           "empty_hours_scheduled_closed": [h for h in empty_hours if _scheduled_closed(day, h)],
           "empty_hours_unexpected": unexpected_empty, "checks": checks}
    if not tick_path.exists():
        out["verdict"] = "FAIL"
        out["reason"] = "no decoded tick file"
        return out
    ticks = pd.read_parquet(tick_path)
    ts = pd.DatetimeIndex(ticks["ts"])
    checks.update({
        "monotonic": bool(ts.is_monotonic_increasing),
        "no_non_positive_prices": bool((ticks["bid"] > 0).all() and (ticks["ask"] > 0).all()),
        "ask_gt_bid": bool((ticks["ask"] > ticks["bid"]).all()),
        "duplicate_policy_matches_phase9": entry is not None
        and entry.get("tick_checks", {}).get("duplicate_ts") == int(ts.duplicated().sum()),
        "source_hashes_present": bool(entry and entry.get("files")),
    })
    # Deterministic derived artefacts, rebuilt here and compared to the stored ones.
    s5 = ps.structure_bars(ticks, "5s")
    s1 = ps.structure_bars(ticks, "1min")
    ex5 = ps.execution_bars(ticks, "5s")
    checks.update({
        "structure_5s_builds": len(s5) > 0,
        "structure_1m_builds": len(s1) > 0,
        "execution_stream_builds": len(ex5) > 0,
        "structure_5s_deterministic": ps.structure_bars(ticks, "5s").equals(s5),
        "structure_1m_deterministic": ps.structure_bars(ticks, "1min").equals(s1),
    })
    stored_1m = cb.OUT / "structure_1m" / f"{day.isoformat()}.parquet"
    checks["canonical_bars_built"] = stored_1m.exists()
    # "No unexplained large missing period": a run of >= 2 consecutive unexpected empty hours.
    runs, run = [], []
    for h in range(24):
        if h in unexpected_empty:
            run.append(h)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    large = [r for r in runs if len(r) >= 2]
    checks["no_unexplained_large_missing_period"] = not large
    out.update({"ticks": len(ticks), "duplicate_ts": int(ts.duplicated().sum()),
                "bad_spreads": int((ticks["ask"] <= ticks["bid"]).sum()),
                "first_ts": str(ts.min()), "last_ts": str(ts.max()),
                "structure_5s_rows": len(s5), "structure_1m_rows": len(s1), "execution_5s_rows": len(ex5),
                "unexplained_missing_runs": [[r[0], r[-1]] for r in large]})
    failed = [k for k, v in checks.items() if v is False]
    concerns = [k for k, v in checks.items() if v is None]
    out["failed_checks"] = failed
    out["verdict"] = "FAIL" if failed else ("PASS WITH CONCERNS" if concerns else "PASS")
    return out


def pilot(instrument: str = "xauusd") -> dict:
    days = [day_report(d, instrument) for d in PILOT_DAYS]
    verdicts = [d["verdict"] for d in days]
    overall = "FAIL" if "FAIL" in verdicts else ("PASS WITH CONCERNS" if "PASS WITH CONCERNS" in verdicts else "PASS")
    out = {"ruling": "D40 §4-6", "predeclared_days": [d.isoformat() for d in PILOT_DAYS],
           "instrument": instrument, "days": days, "overall_verdict": overall,
           "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat()}
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "oq24-availability-pilot.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    return out


def span_status(start_year: int, end_year: int, instrument: str = "xauusd") -> dict:
    """D40 §8 completeness accounting over a requested span. Reads artefacts only."""
    manifest = json.loads(dk.MANIFEST.read_text()) if dk.MANIFEST.exists() else {"days": {}}
    first, last = date(start_year, 1, 1), date(end_year, 12, 31)
    requested = [d.date() for d in pd.bdate_range(first, last)]
    totals = {"requested_trading_days": len(requested), "requested_hours": len(requested) * 24,
              "days_with_tick_file": 0, "successful_hours": 0, "scheduled_empty_hours": 0,
              "unresolved_failures": 0, "bytes": 0, "ticks": 0, "duplicate_timestamps": 0,
              "bad_spreads": 0, "non_positive_prices": 0, "unexpected_empty_hours": 0}
    for d in requested:
        cached = _cache_hours(instrument, d)
        totals["successful_hours"] += sum(1 for size in cached.values() if size > 0)
        for h, size in cached.items():
            if size == 0:
                if _scheduled_closed(d, h):
                    totals["scheduled_empty_hours"] += 1
                else:
                    totals["unexpected_empty_hours"] += 1
        totals["unresolved_failures"] += 24 - len(cached)
        p = dk.RAW / instrument / "ticks" / f"{d.isoformat()}.parquet"
        if p.exists():
            totals["days_with_tick_file"] += 1
            totals["bytes"] += p.stat().st_size
            entry = manifest["days"].get(f"{instrument}/{d.isoformat()}", {})
            checks = entry.get("tick_checks", {})
            totals["ticks"] += int(checks.get("rows", 0))
            totals["duplicate_timestamps"] += int(checks.get("duplicate_ts", 0))
            totals["bad_spreads"] += int(checks.get("non_positive_spread", 0))
    totals["complete"] = totals["unresolved_failures"] == 0 and totals["days_with_tick_file"] == len(requested)
    totals["span"] = [first.isoformat(), last.isoformat()]
    return totals


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    if cmd == "pilot":
        out = pilot()
        for d in out["days"]:
            print(f"{d['day']}  {d['verdict']:18s} ticks={d.get('ticks', 0):>9,}  "
                  f"hours data/empty={d['hours_with_data']}/{d['hours_empty']}  "
                  f"failed={d['failed_checks'] or '-'}")
        print(f"\noverall: {out['overall_verdict']}")
    elif cmd == "span":
        print(json.dumps(span_status(int(sys.argv[2]), int(sys.argv[3])), indent=2))
    else:
        raise SystemExit("usage: acquisition_status [pilot|span START_YEAR END_YEAR]")


if __name__ == "__main__":
    main()
