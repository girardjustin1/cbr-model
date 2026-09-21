"""Historical PC4 signal-generation runner (owner ruling D42 §4-5).

Applies **frozen** `CBR1H_BASELINE_V1` (PC4) across a declared complete historical period and emits the signal
ledger. It contains no strategy logic of its own: every rule decision comes from `cbr.engine.cbr1h_pc4`, unchanged.

    .venv/bin/python -m cbr.engine.historical_runner check 2022-01-01 2022-12-31     # guards only, no execution

What this module is for is refusing to run when it must not:

* **frozen specs** — the PC4 spec hash, the execution-config hash and the Phase 15A protocol hash are verified
  before a single bar is loaded, and any drift raises;
* **completeness** — the Phase 15A gate must report COMPLETE for the *entire* frozen span. A subset of the year is
  refused outright, so month-by-month, quarterly and part-year performance are impossible rather than discouraged
  (D42 §5, §10);
* **restricted periods** — 2023-2024 validation and 2025-2026 holdout are refused unless an explicit owner
  authorization token is passed, and the token is recorded in provenance when it is.

Fixture mode (`fixture=True`, bars supplied by the caller) exists for construction tests. It bypasses the gate,
marks the provenance `FIXTURE_NON_PERFORMANCE`, and may never be used to produce a pilot result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.data import dukascopy_fetch as dk
from cbr.engine import cbr1h_pc4 as pc4
from cbr.engine import phase15a_protocol as protocol
from cbr.engine.params_pc4 import load_cbr1h_pc4, spec_hash_pc4

RUNNER_VERSION = "15A.1"
RUNNER_FILES = ["src/cbr/engine/historical_runner.py"]

DEVELOPMENT = (date(2018, 1, 1), date(2022, 12, 31))
VALIDATION = (date(2023, 1, 1), date(2024, 12, 31))
HOLDOUT_FROM = date(2025, 1, 1)
AUTHORIZATION_TOKEN = "OWNER_AUTHORIZED_RESTRICTED_PERIOD"

# Warm-up available to each chunk. The engine's longest lookback is the prior-setup window (10h) on top of the 8h
# condition window and ATR warm-up; ten days is far beyond all of them and keeps chunked runs equal to a single pass.
WARMUP_DAYS = 10
CHUNK_MONTHS = 1


class RunnerRefusal(RuntimeError):
    """The runner declined to execute. The message states which guard fired."""


class FrozenSpecDrift(RunnerRefusal):
    pass


class SpanIncomplete(RunnerRefusal):
    pass


class PartialSpanRefused(RunnerRefusal):
    pass


class RestrictedPeriod(RunnerRefusal):
    pass


@dataclass
class SignalLedger:
    span: tuple[str, str]
    variants: list
    signals: list = field(default_factory=list)
    decisions: pd.DataFrame = field(default_factory=pd.DataFrame)
    hours: pd.DataFrame = field(default_factory=pd.DataFrame)
    provenance: dict = field(default_factory=dict)

    def ledger_hash(self) -> str:
        payload = json.dumps({
            "signals": self.signals,
            "decisions": self.decisions.astype(str).to_dict("records") if len(self.decisions) else [],
            "hours": self.hours.astype(str).to_dict("records") if len(self.hours) else [],
        }, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()


def runner_hash() -> str:
    h = hashlib.sha256()
    for rel in RUNNER_FILES:
        h.update((dk.ROOT / rel).read_bytes())
    return h.hexdigest()


# ─── Guards ───────────────────────────────────────────────────────────────────────────────────────────────────────
def verify_frozen() -> dict:
    """D42 §4: specs are verified before execution, never after."""
    d = protocol.drift()
    if d.any():
        raise FrozenSpecDrift(f"frozen specification drift: {d}")
    return {"pc4_spec_hash": spec_hash_pc4(), "protocol_hash": protocol.protocol_hash(),
            "execution_config_hash": protocol.execution_config_hash()}


def check_period(start: date, end: date, authorization: str | None) -> str:
    """Development is open; validation and holdout are refused without an explicit owner token."""
    if end <= DEVELOPMENT[1]:
        return "DEVELOPMENT"
    period = "HOLDOUT" if end >= HOLDOUT_FROM else "VALIDATION"
    if authorization != AUTHORIZATION_TOKEN:
        raise RestrictedPeriod(
            f"{start}..{end} enters the {period} period; it is refused without an explicit owner authorization. "
            "Phase 15A does not access validation or holdout performance (D42 §5).")
    return period


def check_span(start: date, end: date, *, pilot_span: tuple[str, str] | None = None) -> None:
    """D42 §5 and §10: only the whole frozen span may run. A subset is refused, not truncated."""
    span = pilot_span or protocol.PILOT_SPAN
    p0, p1 = date.fromisoformat(span[0]), date.fromisoformat(span[1])
    if (start, end) != (p0, p1) and start >= p0 and end <= p1:
        raise PartialSpanRefused(
            f"{start}..{end} is a subset of the frozen pilot span {p0}..{p1}. Month-by-month, quarterly and "
            "part-year performance are not permitted; the first result must cover the entire span (D42 §10).")


def check_complete(gate_result: dict | None = None, span: tuple[date, date] | None = None) -> dict:
    """D42 §5: refuse unless the completeness gate reports COMPLETE for the whole span."""
    from cbr.data.phase15a_gate import SPAN, gate
    g = gate_result if gate_result is not None else gate(span=span or SPAN)
    if g["verdict"] != "COMPLETE":
        raise SpanIncomplete(
            f"the 2022 completeness gate reports {g['verdict']}: "
            f"{g['unresolved_failures']} unresolved hours, {len(g['days_missing_tick_file'])} days without a tick "
            f"file, gaps_resolved={g['gaps_resolved']}, blocks {g['blocks_complete']}/12. "
            "No signal is generated over an incomplete span.")
    return g


# ─── Execution ────────────────────────────────────────────────────────────────────────────────────────────────────
def _chunks(start: pd.Timestamp, end: pd.Timestamp):
    """Month chunks with warm-up. Each chunk evaluates only its own hours; the warm-up only feeds state."""
    edges = pd.date_range(start, end, freq=f"{CHUNK_MONTHS}MS", tz="UTC")
    edges = pd.DatetimeIndex([start]).append(edges[edges > start])
    for i, s in enumerate(edges):
        e = edges[i + 1] if i + 1 < len(edges) else end
        if s < e:
            yield s - pd.Timedelta(days=WARMUP_DAYS), s, e


def _load(bar: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return cb.load_structure(start, end, bar)


def run(start: str | date, end: str | date, *, variants: tuple = ("A", "B"), bars: dict | None = None,
        fixture: bool = False, gate_result: dict | None = None, authorization: str | None = None,
        pilot_span: tuple[str, str] | None = None) -> SignalLedger:
    """Generate the frozen PC4 signal ledger over [start, end] inclusive of the end date's hours.

    `bars` is `{"1m": DataFrame, "5s": DataFrame}` and is required in fixture mode; in normal mode the canonical
    store is read instead.
    """
    s_date = date.fromisoformat(start) if isinstance(start, str) else start
    e_date = date.fromisoformat(end) if isinstance(end, str) else end

    frozen = verify_frozen()
    period = check_period(s_date, e_date, authorization)
    gate_info: dict | None = None
    if fixture:
        if bars is None:
            raise RunnerRefusal("fixture mode requires bars; it never reads the canonical store")
    else:
        check_span(s_date, e_date, pilot_span=pilot_span)
        gate_info = check_complete(gate_result, span=(s_date, e_date))

    t0 = pd.Timestamp(s_date, tz="UTC")
    t1 = pd.Timestamp(e_date, tz="UTC") + pd.Timedelta(days=1)

    signals: list = []
    decisions: list = []
    hours: list = []
    for warm, c0, c1 in _chunks(t0, t1):
        if bars is not None:
            s1m = bars["1m"]
            s5s = bars["5s"]
            s1m = s1m[(s1m.index >= warm) & (s1m.index < c1)]
            s5s = s5s[(s5s.index >= warm) & (s5s.index < c1)]
        else:
            s1m = _load("1m", warm, c1)
            s5s = _load("5s", warm, c1)
        if not len(s1m) or not len(s5s):
            continue
        for variant in variants:
            p = load_cbr1h_pc4(variant)
            res = pc4.run_cbr1h_pc4(s1m, s5s, start=c0, end=c1, variant=variant, params=p)
            signals += res.signals
            if len(res.candidates):
                d = pc4.decision_frame(res)
                d["variant"] = variant
                decisions.append(d)
            if len(res.hours):
                h = res.hours.copy()
                h["variant"] = variant
                hours.append(h)

    ledger = SignalLedger(
        span=(s_date.isoformat(), e_date.isoformat()),
        variants=list(variants),
        signals=sorted(signals, key=lambda s: (s["timestamp"], s["variant"], s["signal_id"])),
        decisions=pd.concat(decisions, ignore_index=True) if decisions else pd.DataFrame(),
        hours=pd.concat(hours, ignore_index=True) if hours else pd.DataFrame(),
    )
    ids = [s["signal_id"] for s in ledger.signals]
    if len(ids) != len(set(ids)):
        raise RunnerRefusal("signal_id collision across chunks or variants; the ledger would not be traceable")
    ledger.provenance = {
        "runner_version": RUNNER_VERSION,
        "runner_hash": runner_hash(),
        "model": "CBR1H_BASELINE_V1",
        "period_class": period,
        "authorization": authorization,
        "mode": "FIXTURE_NON_PERFORMANCE" if fixture else "HISTORICAL",
        "warmup_days": WARMUP_DAYS,
        "warmup_source": "WITHIN_SPAN_ONLY",
        "chunk_months": CHUNK_MONTHS,
        "variants": list(variants),
        "signal_count": len(ledger.signals),
        "candidate_count": len(ledger.decisions),
        "hours_evaluated": len(ledger.hours),
        "source_hashes": {} if fixture else source_hashes(s_date, e_date),
        "completeness_manifest_hash": (gate_info or {}).get("gap_registry_hash"),
        "gate_verdict": (gate_info or {}).get("verdict"),
        **frozen,
    }
    ledger.provenance["signal_ledger_hash"] = ledger.ledger_hash()
    return ledger


def source_hashes(start: date, end: date, instrument: str = "xauusd") -> dict:
    """SHA-256 of every canonical STRUCTURE bar file the span reads, from the canonical manifest."""
    if not cb.MANIFEST.exists():
        return {}
    manifest = json.loads(cb.MANIFEST.read_text())
    out = {}
    for rel, meta in manifest.get("files", {}).items():
        if f"/{instrument}/structure_" not in rel.replace("\\", "/"):
            continue
        day = rel.rsplit("/", 1)[-1].removesuffix(".parquet")
        try:
            d = date.fromisoformat(day)
        except ValueError:
            continue
        if start <= d <= end:
            out[rel] = meta["sha256"]
    return dict(sorted(out.items()))


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 15A historical signal runner (guards only unless --execute)")
    ap.add_argument("command", choices=["check"])
    ap.add_argument("start")
    ap.add_argument("end")
    args = ap.parse_args()
    s, e = date.fromisoformat(args.start), date.fromisoformat(args.end)
    report = {"runner_version": RUNNER_VERSION, "runner_hash": runner_hash(), "span": [args.start, args.end]}
    try:
        report["frozen"] = verify_frozen()
        report["period_class"] = check_period(s, e, None)
        check_span(s, e)
        report["completeness"] = check_complete(span=(s, e))["verdict"]
        report["ready"] = True
    except RunnerRefusal as err:
        report["ready"] = False
        report["refusal"] = f"{type(err).__name__}: {err}"
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
