"""Unexpected-gap classification registry (owner ruling D42 §3, §20C).

Phase 9 AC-07 calls a market-open minute with no data an *unexpected gap*. The canonical session calendar
(`cbr.data.sessions`) encodes only the weekend and the daily 17:00 New York break, so a genuine holiday closure also
arrives here as "unexpected". Every such hour must be investigated and classified before the completeness gate can
report COMPLETE; an unclassified hour **blocks**, and nothing is interpolated, forward-filled, invented or silently
marked complete.

    .venv/bin/python -m cbr.data.gap_registry            # classify the 2022 gaps and print the register

Classifications come from the existing data-quality taxonomy:

| Class | Meaning | Blocks? |
|---|---|---|
| `SCHEDULED_CLOSURE` | the canonical calendar already establishes the closure | no (never reaches this module) |
| `DATA_LIMITATION` | the feed holds no ticks and the canonical calendar cannot establish the closure; the reason is recorded with evidence (Phase 13 protocol row 1, D30-18) | no |
| `DATA_GAP` | market-open data is missing and unexplained | **yes** |
| `NOT_LOADED` | the hour was never fetched | **yes** |

**A `DATA_LIMITATION` hour is not repaired.** Its minutes still reach the simulator as `px.Gap`, so D38's unprovable
outcomes fire exactly as they would for any other gap. The classification changes what the acquisition gate may
call complete; it never changes what the execution layer is allowed to assume.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data import market_closures as mc
from cbr.data.sessions import expected_closed

REGISTRY = dk.ROOT / "research" / "data_quality" / "unexpected_gaps_2022.json"

SCHEDULED_CLOSURE = "SCHEDULED_CLOSURE"
DATA_LIMITATION = "DATA_LIMITATION"
DATA_GAP = "DATA_GAP"
NOT_LOADED = "NOT_LOADED"
CLASSIFICATIONS = (SCHEDULED_CLOSURE, DATA_LIMITATION, DATA_GAP, NOT_LOADED)
BLOCKING = (DATA_GAP, NOT_LOADED)

# US market holidays observed by COMEX/CME metals in 2022. Declared as *dates only*: this list never decides that an
# hour was closed, it only makes a closure explicable. The measured evidence still has to agree (see `_classify`).
# Source: CME Group 2022 holiday calendar (metals), cross-checked against the NYSE 2022 calendar.
US_MARKET_HOLIDAYS_2022 = {
    date(2022, 1, 17):  "Martin Luther King Jr. Day",
    date(2022, 2, 21):  "Presidents' Day",
    date(2022, 4, 15):  "Good Friday",
    date(2022, 5, 30):  "Memorial Day",
    date(2022, 6, 20):  "Juneteenth (first observance)",
    date(2022, 7, 4):   "Independence Day",
    date(2022, 9, 5):   "Labor Day",
    date(2022, 11, 24): "Thanksgiving Day",
    date(2022, 12, 26): "Christmas Day (observed)",
}


@dataclass
class GapEntry:
    """Both classifications are carried, and neither replaces the other (D43 §4).

    `classification` is `source_quality_classification`: what Phase 9 / Phase 15A saw in the stored data.
    `execution_market_state` is what the evidence-based closure registry established about the market itself.
    Keeping both means the record stays auditable without pretending the original calendar knew about a closure.
    """

    hour: str
    classification: str                     # source_quality_classification
    reason: str
    evidence: dict
    blocks: bool
    classified_utc: str
    execution_market_state: str = mc.ACTIVE_MARKET


def _hour_bytes(instrument: str, day: date, h: int) -> int | None:
    """Artefact size, or None when the hour was never fetched. 0 bytes is the feed's 404: no file for that hour."""
    p = dk.CACHE / instrument / f"{day.isoformat()}_{h:02d}.bi5"
    return p.stat().st_size if p.exists() else None


def _day_profile(instrument: str, day: date) -> dict:
    """Byte size per hour for a day, plus which hours the canonical calendar already calls closed."""
    sizes, closed = {}, {}
    for h in range(24):
        sizes[h] = _hour_bytes(instrument, day, h)
        closed[h] = bool(expected_closed(pd.Timestamp(datetime(day.year, day.month, day.day, h, tzinfo=UTC))))
    return {"sizes": sizes, "closed": closed}


def trading_day(hour: datetime) -> date:
    """The metals trading day an hour belongs to: the session rolls at 17:00 New York, so an hour after the daily
    break belongs to the next calendar day's session. This is what makes a holiday's closure start the evening
    before (Good Friday 2022 begins at 17:00 New York on 2022-04-14)."""
    ny = pd.Timestamp(hour).tz_convert("America/New_York")
    return (ny + pd.Timedelta(days=1)).date() if ny.hour >= 18 else ny.date()


def _classify(instrument: str, hour: datetime) -> GapEntry:
    """Classify one unexpected-gap hour from measured artefacts. Anything unexplained stays blocking."""
    day = hour.date()
    prof = _day_profile(instrument, day)
    sizes, closed = prof["sizes"], prof["closed"]
    size = sizes[hour.hour]
    session = trading_day(hour)
    holiday = US_MARKET_HOLIDAYS_2022.get(session)

    fetched = [h for h, s in sizes.items() if s is not None]
    empty = sorted(h for h, s in sizes.items() if s == 0)
    with_data = sorted(h for h, s in sizes.items() if s is not None and s > 0)

    # Is this hour part of a contiguous run of non-trading hours that reaches the daily break, or covers the whole
    # fetched day? A scheduled closure is never requested, so it has no artefact at all: an absent artefact at a
    # calendar-closed hour continues the run rather than ending it.
    def _non_trading(h: int) -> bool:
        return sizes[h] == 0 or (sizes[h] is None and closed[h])

    run = [hour.hour]
    h = hour.hour - 1
    while h >= 0 and _non_trading(h):
        run.insert(0, h)
        h -= 1
    h = hour.hour + 1
    while h < 24 and _non_trading(h):
        run.append(h)
        h += 1
    touches_break = any(closed[h] for h in run)
    whole_day_closed = len(with_data) == 0 and len(fetched) > 0

    evidence = {
        "artefact_bytes": size,
        "artefact_state": "NOT_FETCHED" if size is None else ("FEED_404_EMPTY" if size == 0 else "HAS_DATA"),
        "holiday": holiday,
        "trading_day": session.isoformat(),
        "contiguous_empty_run_hours_utc": run,
        "run_touches_daily_break": touches_break,
        "whole_fetched_day_empty": whole_day_closed,
        "hours_with_data_on_day": len(with_data),
        "empty_hours_on_day": empty,
        "preceding_hour_bytes": sizes.get(hour.hour - 1),
        "following_hour_bytes": sizes.get(hour.hour + 1),
    }

    if size is None:
        return GapEntry(hour.isoformat(), NOT_LOADED, "the hour was never fetched", evidence, True,
                        datetime.now(UTC).replace(microsecond=0).isoformat())

    # A holiday closure is accepted only when the measurement agrees with the calendar reason: the feed returned a
    # 404 for the hour, the date is a declared market holiday, and the empty hours form one run that either runs into
    # the daily break (an early close) or covers the entire day (a full closure).
    if size == 0 and holiday and (touches_break or whole_day_closed):
        reason = (f"{holiday}: the market was closed and the feed holds no file for this hour. The canonical "
                  "session calendar encodes only the weekend and the daily break, so a holiday closure surfaces "
                  "as an unexpected gap. No data is missing from the vendor and none is invented here.")
        return GapEntry(hour.isoformat(), DATA_LIMITATION, reason, evidence, False,
                        datetime.now(UTC).replace(microsecond=0).isoformat())

    return GapEntry(hour.isoformat(), DATA_GAP,
                    "market-open hour with no data and no established explanation", evidence, True,
                    datetime.now(UTC).replace(microsecond=0).isoformat())


def classify(hours: list[str], instrument: str = "xauusd") -> dict:
    """Classify every supplied unexpected-gap hour (ISO-8601 UTC strings) and write the register.

    The execution market state is read from the closure registry, which is built independently from the same
    artefacts. An hour with no closure entry stays `ACTIVE_MARKET`, so a gap is never resolved by this lookup.
    """
    closures = mc.load()
    entries = [_classify(instrument, datetime.fromisoformat(h)) for h in sorted(set(hours))]
    for e in entries:
        e.execution_market_state = mc.closure_state(datetime.fromisoformat(e.hour), closures)
    body = {
        "ruling": "D42 §3",
        "instrument": instrument,
        "taxonomy": list(CLASSIFICATIONS),
        "blocking_classifications": list(BLOCKING),
        "holiday_source": "CME Group 2022 metals holiday calendar, cross-checked against NYSE 2022",
        "entries": [asdict(e) for e in entries],
        "counts": {c: sum(1 for e in entries if e.classification == c) for c in CLASSIFICATIONS},
        "execution_market_state_counts": {
            mc.VERIFIED_MARKET_DATA_CLOSURE: sum(
                1 for e in entries if e.execution_market_state == mc.VERIFIED_MARKET_DATA_CLOSURE),
            mc.ACTIVE_MARKET: sum(1 for e in entries if e.execution_market_state == mc.ACTIVE_MARKET)},
        "closure_registry_hash": closures.registry_hash,
        "blocking_hours": [e.hour for e in entries if e.blocks],
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }
    body["registry_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in body.items() if k != "generated_utc"}, sort_keys=True).encode()).hexdigest()
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(body, indent=1) + "\n")
    return body


def load() -> dict:
    return json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {"entries": [], "blocking_hours": []}


def status(hours: list[str]) -> dict:
    """Does the register resolve every gap the gate found? Unclassified and blocking hours both block."""
    reg = load()
    classified = {e["hour"]: e for e in reg.get("entries", [])}
    wanted = sorted(set(hours))
    unclassified = [h for h in wanted if h not in classified]
    blocking = [h for h in wanted if h in classified and classified[h]["blocks"]]
    return {"registry_hash": reg.get("registry_hash"), "gaps": len(wanted),
            "classified": len(wanted) - len(unclassified), "unclassified_hours": unclassified,
            "blocking_hours": blocking, "resolved": not unclassified and not blocking,
            "counts": reg.get("counts", {})}


def main() -> None:
    from cbr.data.phase15a_gate import gate
    g = gate()
    body = classify(g["unexpected_gap_hours"])
    for e in body["entries"]:
        print(f"{e['hour']}  {e['classification']:16s} blocks={e['blocks']}  {e['evidence']['holiday'] or '-'}")
    print(f"\ncounts: {body['counts']}")
    print(f"registry hash: {body['registry_hash']}")
    print(f"blocking hours: {body['blocking_hours'] or 'none'}")


if __name__ == "__main__":
    main()
