"""Verified market-data closures (owner ruling D43 §1-5).

A closure the **canonical strategy calendar does not know about**. `cbr.data.sessions.expected_closed` encodes only
the weekend and the daily 17:00 New York break, and it must stay that way: it feeds PC4's TRADABLE condition-window
basis, so adding holidays to it would be a strategy behaviour change (D43 §1). This module is the separate concept.

Its only purposes are:

* historical-data **completeness** — an hour the feed never had is accounted for, not counted as a failure;
* execution-data **interpretation** — a proven closure contains no executable quote stream, so no fill can have
  occurred inside it;
* keeping a real market closure from being mistaken for corrupt or missing data.

**It is never imported by strategy logic** — not by PC4 condition logic, tradable-time calculation, signal
eligibility, extension logic or any CBR rule. `tests/test_closure_registry_separation.py` enforces that.

Two classifications are carried side by side and neither replaces the other (D43 §4):

    source_quality_classification = DATA_LIMITATION              # what Phase 9 / Phase 15A saw
    execution_market_state        = VERIFIED_MARKET_DATA_CLOSURE # what the evidence established

so the record stays auditable without pretending the original calendar knew about the closure.

    .venv/bin/python -m cbr.data.market_closures 2022      # build the registry from stored artefacts
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, timedelta
from functools import lru_cache

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data.sessions import expected_closed

CLASSIFICATION_VERSION = "D43.1"
REGISTRY = dk.ROOT / "research" / "data_quality" / "verified_market_closures_2022.json"

# execution_market_state values
VERIFIED_MARKET_DATA_CLOSURE = "VERIFIED_MARKET_DATA_CLOSURE"
ACTIVE_MARKET = "ACTIVE_MARKET"

# Evidence rules a period must satisfy to be called a verified closure (D43 §3). A holiday name is never one of
# them: the calendar can explain a closure, it can never establish one.
EVIDENCE_RULES = (
    "SOURCE_404_NO_FILE",             # the feed holds no file for every hour of the period
    "CONTIGUOUS_EMPTY_INTERVAL",      # the empty hours form one unbroken run
    "CONNECTED_TO_CLOSURE_BOUNDARY",  # the run reaches a known break/weekend boundary, or covers the whole session
    "NO_ISOLATED_HOLE",               # never an isolated hour inside otherwise active trading
)
MIN_CLOSURE_HOURS = 2                 # a single missing hour is never a closure, whatever the date


@dataclass
class Closure:
    date: str
    start_utc: str
    end_utc: str
    hours: int
    execution_market_state: str
    source_quality_classification: str
    evidence: dict
    evidence_rules_met: list
    source_files: list
    classification_version: str = CLASSIFICATION_VERSION
    holiday_context: str | None = None          # context only; never evidence


@dataclass
class Registry:
    year: int
    instrument: str
    closures: list = field(default_factory=list)
    generated_utc: str = ""
    registry_hash: str = ""

    def intervals(self) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
        return [(pd.Timestamp(c["start_utc"]), pd.Timestamp(c["end_utc"])) for c in self.closures]


def _artefact(instrument: str, hour: datetime):
    return dk.CACHE / instrument / f"{hour:%Y-%m-%d_%H}.bi5"


def _rel(path) -> str:
    """Repo-relative where possible; the artefact cache may legitimately sit outside the repository."""
    try:
        return str(pathlib.Path(path).relative_to(dk.ROOT))
    except ValueError:
        return str(path)


def _state(instrument: str, hour: datetime) -> str:
    """What the stored artefact says about this hour, with no interpretation layered on."""
    p = _artefact(instrument, hour)
    if not p.exists():
        return "NOT_FETCHED"
    return "FEED_404_EMPTY" if p.stat().st_size == 0 else "HAS_DATA"


def _runs(instrument: str, year: int) -> list[list[datetime]]:
    """Maximal runs of consecutive non-trading hours: a feed 404, or an hour the canonical calendar already closes.

    A calendar-closed hour is never requested and so has no artefact; treating its absence as a break would split
    every early close in two at the daily break.
    """
    hours = pd.date_range(datetime(year, 1, 1, tzinfo=UTC), datetime(year + 1, 1, 1, tzinfo=UTC),
                          freq="h", inclusive="left")
    runs, run = [], []
    for ts in hours:
        h = ts.to_pydatetime()
        state = _state(instrument, h)
        closed = bool(expected_closed(ts))
        non_trading = state == "FEED_404_EMPTY" or (state == "NOT_FETCHED" and closed)
        if non_trading:
            run.append(h)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    return runs


def _weekend(hour: datetime) -> bool:
    return expected_closed(pd.Timestamp(hour)) == "weekend"


def _classify_run(instrument: str, run: list[datetime]) -> Closure | None:
    """Assess one run of non-trading hours. Returns a Closure only when the evidence establishes one."""
    observed = [h for h in run if _state(instrument, h) == "FEED_404_EMPTY" and not expected_closed(pd.Timestamp(h))]
    if not observed:
        return None                       # nothing beyond what the canonical calendar already covers
    # A closure is judged over the hours the feed actually 404'd outside the known calendar.
    start, end = observed[0], observed[-1] + timedelta(hours=1)
    calendar_boundary = any(bool(expected_closed(pd.Timestamp(h))) for h in run)
    contiguous = [h.isoformat() for h in run]
    day = observed[0].date()
    day_states = {h: _state(instrument, datetime(day.year, day.month, day.day, h, tzinfo=UTC)) for h in range(24)}
    whole_day = not any(s == "HAS_DATA" for s in day_states.values()) and "FEED_404_EMPTY" in day_states.values()

    met = []
    if all(_state(instrument, h) == "FEED_404_EMPTY" for h in observed):
        met.append("SOURCE_404_NO_FILE")
    if len(run) == len(observed) + sum(1 for h in run if expected_closed(pd.Timestamp(h))):
        met.append("CONTIGUOUS_EMPTY_INTERVAL")
    if calendar_boundary or whole_day:
        met.append("CONNECTED_TO_CLOSURE_BOUNDARY")
    if len(observed) >= MIN_CLOSURE_HOURS:
        met.append("NO_ISOLATED_HOLE")

    prev_h = observed[0] - timedelta(hours=1)
    next_h = observed[-1] + timedelta(hours=1)
    evidence = {
        "observed_hours_utc": [h.isoformat() for h in observed],
        "run_hours_utc": contiguous,
        "artefact_states": {h.isoformat(): _state(instrument, h) for h in observed},
        "preceding_hour": {"hour": prev_h.isoformat(), "state": _state(instrument, prev_h),
                           "bytes": _artefact(instrument, prev_h).stat().st_size
                           if _artefact(instrument, prev_h).exists() else None},
        "following_hour": {"hour": next_h.isoformat(), "state": _state(instrument, next_h),
                           "bytes": _artefact(instrument, next_h).stat().st_size
                           if _artefact(instrument, next_h).exists() else None},
        "reaches_calendar_boundary": calendar_boundary,
        "whole_session_empty": whole_day,
        "weekend_adjacent": any(_weekend(h) for h in run),
    }
    if set(EVIDENCE_RULES) - set(met):
        return None                       # not proven; the hours stay whatever the gap registry called them
    return Closure(
        date=day.isoformat(), start_utc=start.isoformat(), end_utc=end.isoformat(), hours=len(observed),
        execution_market_state=VERIFIED_MARKET_DATA_CLOSURE,
        source_quality_classification="DATA_LIMITATION",
        evidence=evidence, evidence_rules_met=met,
        source_files=[_rel(_artefact(instrument, h)) for h in observed],
    )


def build(year: int = 2022, instrument: str = "xauusd", *, holiday_context: dict | None = None) -> dict:
    """Build the registry from stored artefacts. Evidence decides; a holiday name is recorded as context only."""
    closures = []
    for run in _runs(instrument, year):
        c = _classify_run(instrument, run)
        if c is None:
            continue
        if holiday_context:
            # Context only, never evidence. A closure that starts the evening before belongs to the next
            # session, so both days are consulted (Good Friday begins at 17:00 New York on the Thursday).
            d = date.fromisoformat(c.date)
            c.holiday_context = holiday_context.get(d) or holiday_context.get(d + timedelta(days=1))
        closures.append(asdict(c))
    body = {
        "ruling": "D43 §2-4",
        "classification_version": CLASSIFICATION_VERSION,
        "year": year,
        "instrument": instrument,
        "purpose": ["historical-data completeness", "execution-data interpretation",
                    "a real closure is not mistaken for corrupt or missing data"],
        "never_used_by": ["PC4 condition logic", "PC4 tradable-time calculation", "signal eligibility",
                          "extension logic", "CBR rules"],
        "evidence_rules": list(EVIDENCE_RULES),
        "min_closure_hours": MIN_CLOSURE_HOURS,
        "closures": closures,
        "closure_count": len(closures),
        "closed_hours": sum(c["hours"] for c in closures),
    }
    body["registry_hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    body["generated_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(body, indent=1) + "\n")
    return body


@lru_cache(maxsize=8)
def _load_cached(path: str, mtime: float) -> Registry:
    body = json.loads(pathlib.Path(path).read_text())
    return Registry(year=body["year"], instrument=body["instrument"], closures=body["closures"],
                    generated_utc=body.get("generated_utc", ""), registry_hash=body.get("registry_hash", ""))


def load(path=None) -> Registry:
    """The registry, cached on (path, mtime) so a year-scale replay does not re-read it per session."""
    p = pathlib.Path(path or REGISTRY)
    if not p.exists():
        return Registry(year=0, instrument="", closures=[])
    return _load_cached(str(p), p.stat().st_mtime)


def closed_at(ts, registry: Registry | None = None) -> bool:
    """Is this instant inside a verified closure? Execution-side only; never a strategy input."""
    reg = registry if registry is not None else load()
    t = pd.Timestamp(ts)
    return any(s <= t < e for s, e in reg.intervals())


def closure_state(ts, registry: Registry | None = None) -> str:
    return VERIFIED_MARKET_DATA_CLOSURE if closed_at(ts, registry) else ACTIVE_MARKET


def main() -> None:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2022
    from cbr.data.gap_registry import US_MARKET_HOLIDAYS_2022
    body = build(year, holiday_context=US_MARKET_HOLIDAYS_2022)
    for c in body["closures"]:
        print(f"{c['date']}  {c['start_utc'][11:16]}-{c['end_utc'][11:16]}  {c['hours']:2d}h  "
              f"{c['execution_market_state']}  rules={len(c['evidence_rules_met'])}/4  "
              f"{c['holiday_context'] or '-'}")
    print(f"\n{body['closure_count']} verified closures, {body['closed_hours']} hours")
    print(f"registry hash: {body['registry_hash']}")


if __name__ == "__main__":
    main()
