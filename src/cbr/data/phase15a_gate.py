"""Phase 15A 2022 completeness gate (owner ruling D42 §9-10).

Performance does not run until the declared span is COMPLETE. This module reports the fifteen accounting fields the
ruling names, assembled from artefacts only — per-hour cache files, the monthly block manifests, the day manifest and
the decoded tick parquet. It downloads nothing, decodes nothing and computes no statistic about a trade.

    .venv/bin/python -m cbr.data.phase15a_gate            # the 2022 gate

The binding property is D42 §9: *no unresolved market-open hour may silently disappear.* Every **requested open**
hour lands in exactly one of `successful_hours`, `unexpected_gaps` or `unresolved_failures`. Hours the canonical
calendar already calls closed are never requested and are counted separately as `scheduled_closures`, so a closure
can never pad the open-hour accounting.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data import gap_registry, market_closures
from cbr.data import staged_acquisition as sa
from cbr.data.sessions import expected_closed

SPAN = (date(2022, 1, 1), date(2022, 12, 31))
REPORTS = dk.ROOT / "reports"


@dataclass
class Gate:
    span: tuple[str, str]
    instrument: str
    # The fifteen D42 §9 fields.
    requested_trading_days: int = 0
    requested_open_hours: int = 0
    successful_hours: int = 0
    scheduled_closures: int = 0
    legitimate_empty_hours: int = 0
    unresolved_failures: int = 0
    retry_count: int = 0
    http_429: int = 0
    http_5xx: int = 0
    bytes: int = 0
    tick_count: int = 0
    duplicates: int = 0
    bad_spreads: int = 0
    non_positive_prices: int = 0
    unexpected_gaps: int = 0
    # Accounting context.
    cached_scheduled_closure_hours: int = 0
    blocks_written: int = 0
    blocks_complete: int = 0
    days_with_tick_file: int = 0
    days_missing_tick_file: list = field(default_factory=list)
    unresolved_hours: list = field(default_factory=list)
    unexpected_gap_hours: list = field(default_factory=list)
    hours_accounted: bool = False
    gaps_resolved: bool = False
    gap_registry_hash: str = ""
    unclassified_gap_hours: list = field(default_factory=list)
    blocking_gap_hours: list = field(default_factory=list)
    gap_classifications: dict = field(default_factory=dict)
    verified_closure_hours: int = 0
    true_data_gap_hours: int = 0
    closure_registry_hash: str = ""
    complete: bool = False
    verdict: str = "INCOMPLETE"


def _months(span: tuple[date, date]) -> list[str]:
    return [str(p) for p in pd.period_range(span[0], span[1], freq="M")]


def gate(instrument: str = "xauusd", span: tuple[date, date] = SPAN) -> dict:
    first, last = span
    g = Gate(span=(first.isoformat(), last.isoformat()), instrument=instrument)

    # 1. What the transport layer recorded per month block. The hour counts are derived below from the same
    # calendar the fetcher used, so the accounting cannot disagree with the span actually being gated.
    months = _months(span)
    for block in months:
        path = sa.BLOCKS / f"{instrument}_{block}.json"
        if path.exists():
            m = json.loads(path.read_text())
            g.blocks_written += 1
            g.blocks_complete += int(m["complete"])
            g.retry_count += m["retry_count"]
            g.http_429 += m["http_429"]
            g.http_5xx += m["http_5xx"]

    # 2. What is actually on disk, hour by hour. An empty artefact is Dukascopy's 404 for that hour.
    days = [d.date() for d in pd.bdate_range(first, last)]
    g.requested_trading_days = len(days)
    for day in days:
        for h in range(24):
            hour = datetime(day.year, day.month, day.day, h, tzinfo=UTC)
            p = dk.CACHE / instrument / f"{day.isoformat()}_{h:02d}.bi5"
            closed = bool(expected_closed(pd.Timestamp(hour)))
            if closed:
                g.scheduled_closures += 1
            else:
                g.requested_open_hours += 1
            if not p.exists():
                if not closed:
                    g.unresolved_failures += 1
                    g.unresolved_hours.append(hour.isoformat())
                continue
            size = p.stat().st_size
            g.bytes += size
            if closed:
                # Not a requested hour: the calendar already established it as closed, so it is accounted for in
                # `scheduled_closures` and never in the open-hour buckets. Cached ones come from earlier
                # whole-day fixture fetches.
                g.cached_scheduled_closure_hours += 1
                g.legitimate_empty_hours += int(size == 0)
            elif size:
                g.successful_hours += 1
            else:
                # The feed holds no file for an hour the calendar says was open: Phase 9 AC-07's unexpected gap.
                # It is reported, never absorbed into "empty".
                g.unexpected_gaps += 1
                g.unexpected_gap_hours.append(hour.isoformat())

    # 3. Decoded tick quality, from the day manifest written by the decoder.
    manifest = json.loads(dk.MANIFEST.read_text()) if dk.MANIFEST.exists() else {"days": {}}
    for day in days:
        tick_path = dk.RAW / instrument / "ticks" / f"{day.isoformat()}.parquet"
        if not tick_path.exists():
            g.days_missing_tick_file.append(day.isoformat())
            continue
        g.days_with_tick_file += 1
        checks = manifest["days"].get(f"{instrument}/{day.isoformat()}", {}).get("tick_checks", {})
        g.tick_count += int(checks.get("rows", 0))
        g.duplicates += int(checks.get("duplicate_ts", 0))
        g.bad_spreads += int(checks.get("non_positive_spread", 0))

    # 4. Non-positive prices are not in the manifest; they are read back from the stored ticks.
    for day in days:
        tick_path = dk.RAW / instrument / "ticks" / f"{day.isoformat()}.parquet"
        if tick_path.exists():
            t = pd.read_parquet(tick_path, columns=["bid", "ask"])
            g.non_positive_prices += int(((t["bid"] <= 0) | (t["ask"] <= 0)).sum())

    # 5. D42 §9: every requested open hour lands in exactly one bucket, and none disappears.
    accounted = g.successful_hours + g.unexpected_gaps + g.unresolved_failures
    g.hours_accounted = accounted == g.requested_open_hours
    # D42 §3 / §20C: every unexpected gap must carry a classification, and none may be a blocking one. An
    # unclassified gap keeps the span INCOMPLETE — a gap is never resolved by being counted.
    gaps = gap_registry.status(g.unexpected_gap_hours)
    g.gaps_resolved = gaps["resolved"]
    g.gap_registry_hash = gaps["registry_hash"]
    g.unclassified_gap_hours = gaps["unclassified_hours"]
    g.blocking_gap_hours = gaps["blocking_hours"]
    g.gap_classifications = gaps["counts"]
    # D43 §12: the two counts are reported separately and never summed into one "gaps" number.
    reg = json.loads(gap_registry.REGISTRY.read_text()) if gap_registry.REGISTRY.exists() else {}
    states = reg.get("execution_market_state_counts", {})
    g.verified_closure_hours = int(states.get(market_closures.VERIFIED_MARKET_DATA_CLOSURE, 0))
    g.true_data_gap_hours = g.unexpected_gaps - g.verified_closure_hours
    g.closure_registry_hash = reg.get("closure_registry_hash", "")
    g.complete = (g.unresolved_failures == 0 and g.hours_accounted and g.gaps_resolved
                  and g.blocks_complete == len(months) and not g.days_missing_tick_file)
    g.verdict = "COMPLETE" if g.complete else "INCOMPLETE"
    out = asdict(g)
    out["hours_accounted_detail"] = {"accounted": accounted, "requested_open_hours": g.requested_open_hours}
    out["generated_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    return out


def main() -> None:
    out = gate()
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1))
    else:
        fields = ["requested_trading_days", "requested_open_hours", "successful_hours", "scheduled_closures",
                  "legitimate_empty_hours", "unresolved_failures", "retry_count", "http_429", "http_5xx",
                  "bytes", "tick_count", "duplicates", "bad_spreads", "non_positive_prices", "unexpected_gaps"]
        for f in fields:
            print(f"{f:26s} {out[f]:>14,}")
        print(f"{'blocks complete':26s} {out['blocks_complete']:>14}/12")
        print(f"{'days with tick file':26s} {out['days_with_tick_file']:>14}/{out['requested_trading_days']}")
        print(f"{'hours fully accounted':26s} {out['hours_accounted']!s:>14}")
        print(f"{'gaps resolved':26s} {out['gaps_resolved']!s:>14}   {out['gap_classifications']}")
        print(f"{'verified closure hours':26s} {out['verified_closure_hours']:>14,}")
        print(f"{'true data-gap hours':26s} {out['true_data_gap_hours']:>14,}")
        print(f"\n2022 gate: {out['verdict']}")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "phase15a-2022-completeness.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
