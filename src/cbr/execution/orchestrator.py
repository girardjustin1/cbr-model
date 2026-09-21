"""Historical execution orchestrator (owner ruling D42 §6).

Connects the frozen PC4 signal ledger to the Phase 14A authoritative simulator over Phase 14A.1 real Dukascopy tick
replay. It duplicates **no** strategy logic and **no** execution semantics: signals come from
`cbr.engine.historical_runner`, fills come from `cbr.execution.replay`, and this module only decides which window to
load for which signals, then concatenates what comes back.

    from cbr.execution import orchestrator
    ex = orchestrator.orchestrate(signal_ledger)

**Sessioning.** Quotes for a whole year do not fit in memory, so signals are grouped by *trading session* — the
metals day that rolls at 17:00 New York — and each session is replayed over its own window. A session is a sound
boundary because D38 forces every open position flat at rollover, so no position can cross one. Grouping by
calendar day instead would split a session at midnight UTC and let one position appear open in two chunks.

No summary statistic is computed here. Counting wins, averaging R or forming an expectancy is the metrics writer's
job, and it does not run during construction.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.execution import ledger as ex_ledger
from cbr.execution import replay as rp
from cbr.execution.simulate import ExecutionParams

ORCHESTRATOR_VERSION = "15A.1"
ORCHESTRATOR_FILES = ["src/cbr/execution/orchestrator.py"]

# Window around a session. The session runs 18:00 New York (previous day) to 17:00 New York, which is 22:00/23:00 UTC
# to 21:00/22:00 UTC depending on DST. These bounds cover both regimes plus the rollover exit with room to spare.
SESSION_LEAD = pd.Timedelta(hours=28)
SESSION_TAIL_UTC = pd.Timedelta(hours=24)


def orchestrator_hash() -> str:
    h = hashlib.sha256()
    for rel in ORCHESTRATOR_FILES:
        h.update((dk.ROOT / rel).read_bytes())
    return h.hexdigest()


def session_day(ts: pd.Timestamp) -> date:
    """The trading session an instant belongs to; the metals day rolls at 17:00 New York."""
    ny = pd.Timestamp(ts).tz_convert("America/New_York")
    return (ny + pd.Timedelta(days=1)).date() if ny.hour >= 18 else ny.date()


def session_window(day: date) -> tuple[pd.Timestamp, pd.Timestamp]:
    """[start, end) covering one session in both DST regimes, with room for the rollover exit."""
    end = pd.Timestamp(day, tz="UTC") + SESSION_TAIL_UTC
    return end - SESSION_LEAD, end


@dataclass
class ExecutionLedger:
    records: list = field(default_factory=list)
    provenance: dict = field(default_factory=dict)

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame([r.as_dict() for r in self.records])

    def execution_ledger_hash(self) -> str:
        rows = sorted((r.as_dict() for r in self.records), key=lambda d: (str(d["signal_id"]), str(d["variant"])))
        import json
        return hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()


def orchestrate(signal_ledger, *, instrument: str = "xauusd", params: ExecutionParams | None = None,
                replay_fn=rp.replay) -> ExecutionLedger:
    """Execute every signal in the ledger. One replay per trading session, in chronological order.

    `replay_fn` is injectable so construction tests can drive the orchestrator over fixture quotes without a
    canonical tick store; it defaults to the frozen Phase 14A.1 replay.
    """
    p = params or ExecutionParams.frozen()
    signals = list(signal_ledger.signals)
    by_session: dict[date, list] = {}
    undated: list = []
    for s in signals:
        ts = s.get("entry_trigger_time") or s.get("timestamp")
        if ts is None:
            undated.append(s)
            continue
        by_session.setdefault(session_day(pd.Timestamp(ts)), []).append(s)

    records: list = []
    sessions: list[dict] = []
    gap_counts: Counter = Counter()
    source_hashes: dict = {}
    missing_days: set = set()
    ticks = 0
    for day in sorted(by_session):
        start, end = session_window(day)
        res = replay_fn(by_session[day], start, end, instrument=instrument, params=p)
        records += list(res.records)
        prov = dict(res.provenance)
        ticks += int(prov.get("tick_count", 0) or 0)
        source_hashes.update(prov.get("source_hashes", {}) or {})
        missing_days.update(prov.get("missing_days", []) or [])
        gap_counts.update(prov.get("classified_intervals", {}) or {})
        sessions.append({"session": day.isoformat(), "window": [str(start), str(end)],
                         "signals": len(by_session[day]), "tick_count": prov.get("tick_count"),
                         "result_hash": prov.get("result_hash")})

    for s in undated:
        # A signal with no time cannot be placed in a session; it is recorded, never dropped.
        records.append(ex_ledger.ExecutionRecord(
            signal_id=s.get("signal_id", "UNKNOWN"), model=s.get("model", ""), variant=s.get("variant", ""),
            direction=s.get("direction", ""), signal_time=None, activation_time=None, trigger_price=None,
            execution_status=ex_ledger.NOT_EXECUTED, reason_code=ex_ledger.EXECUTION_DATA_UNAVAILABLE,
            data_confidence={"orchestrator": "NO_ACTIVATION_TIME"}))

    out = ExecutionLedger(records=records)
    seen = [r.signal_id for r in records]
    out.provenance = {
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "orchestrator_hash": orchestrator_hash(),
        "simulator_version": ex_ledger.SIMULATOR_VERSION,
        "instrument": instrument,
        "sessions": sessions,
        "session_count": len(sessions),
        "signals_in": len(signals),
        "records_out": len(records),
        "every_signal_recorded": len(seen) == len(signals) and set(seen) == {
            s.get("signal_id") for s in signals},
        "tick_count": ticks,
        "source_hashes": dict(sorted(source_hashes.items())),
        "missing_days": sorted(missing_days),
        "classified_intervals": dict(sorted(gap_counts.items())),
        "signal_ledger_hash": signal_ledger.provenance.get("signal_ledger_hash"),
        "execution_config_hash": rp.execution_config_hash(),
        "signal_hash": rp.signal_hash(signals),
    }
    out.provenance["execution_ledger_hash"] = out.execution_ledger_hash()
    if not out.provenance["every_signal_recorded"]:
        raise RuntimeError("the execution ledger does not hold exactly one record per signal; "
                           "a signal would be invisible in the result")
    return out
