"""The deterministic execution driver (owner ruling D38). Frozen signals in, execution ledger out.

No CBR strategy rule is imported, re-derived or reinterpreted here (D38 §1, §33): the simulator decides only whether
and at what price an order fills, and what the resulting record says.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yaml

from cbr.engine.baseline_v1 import provenance
from cbr.engine.params import ROOT
from cbr.execution import fills, ledger, orders
from cbr.execution import prices as px
from cbr.execution.contract import ExecutionSignal, eligible, parse
from cbr.execution.position import PositionBook, resolve_stop

EXECUTION_CONFIG = ROOT / "config" / "execution.yaml"


@dataclass(frozen=True)
class ExecutionParams:
    """Every value here is frozen by D38 and may not be tuned from outcomes."""

    additional_slippage: float = 0.0
    explicit_commission: float = 0.0
    rollover_pre_min: int = 15
    rollover_post_min: int = 60
    rollover_ny_time: str = "17:00"

    @classmethod
    def frozen(cls) -> ExecutionParams:
        cfg = yaml.safe_load(EXECUTION_CONFIG.read_text())
        costs = cfg["costs"]
        return cls(additional_slippage=float(costs["additional_slippage"]["value"]),
                   explicit_commission=float(costs["explicit_commission"]["value"]))


def semantics() -> dict:
    cfg = yaml.safe_load(EXECUTION_CONFIG.read_text())
    return {"spec_version": cfg["spec_version"], "ruling": cfg["ruling"],
            "stop_resolution": cfg["stop"]["resolution_instant"]["value"],
            "entry_trigger": cfg["entry"]["trigger"]["value"],
            "stop_fill": cfg["exit"]["stop_fill"]["value"], "target_fill": cfg["exit"]["target_fill"]["value"],
            "forced_exit": cfg["exit"]["forced_exit"]["value"], "sequencing": cfg["sequencing"]["authority"]["value"],
            "additional_slippage": cfg["costs"]["additional_slippage"]["value"],
            "explicit_commission": cfg["costs"]["explicit_commission"]["value"],
            "position_scope": cfg["position"]["scope"]["value"],
            "spread_fallback": cfg["data"]["spread_fallback"]["value"]}


def _rec(sig: ExecutionSignal, status: str, reason: str | None = None, **kw) -> ledger.ExecutionRecord:
    return ledger.ExecutionRecord(
        signal_id=sig.signal_id, model=sig.model, variant=sig.variant, direction=sig.direction,
        signal_time=str(sig.signal_time), activation_time=None if sig.activation_time is None
        else str(sig.activation_time), trigger_price=sig.trigger_price, target_price=sig.target_price,
        execution_status=status, reason_code=reason,
        data_confidence=sig.raw.get("data_confidence", {}),
        source_hashes={"spec_hash": sig.raw.get("spec_hash")}, **kw)


def _entry_candidate(sig: ExecutionSignal, quotes: pd.DataFrame, gaps: list[px.Gap], p: ExecutionParams,
                     data_end: pd.Timestamp, *, not_before: pd.Timestamp | None):
    """The order's first executable trigger, or a terminal record explaining why there is none."""
    win = orders.window(sig, data_end=data_end, pre_min=p.rollover_pre_min, post_min=p.rollover_post_min,
                        ny_time=p.rollover_ny_time)
    if win.empty():
        if win.rollover_cancelled:
            return None, _rec(sig, ledger.CANCELLED, ledger.ROLLOVER_CANCEL)
        return None, _rec(sig, ledger.NOT_EXECUTED, ledger.EXECUTION_DATA_UNAVAILABLE)
    start = win.start if not_before is None else max(win.start, not_before)
    live = px.window(quotes, start, win.end)
    if not len(live):
        return None, _rec(sig, ledger.NOT_EXECUTED, ledger.EXECUTION_DATA_UNAVAILABLE)
    event = fills.entry_touch(live, is_long=sig.is_long, trigger=sig.trigger_price)
    if event is not None and not event.resolved:
        return None, _rec(sig, ledger.UNPROVABLE, ledger.EXECUTION_UNPROVABLE_INTRABAR)
    horizon = win.end if event is None else event.time
    if any(g.covers(start, horizon) for g in gaps):
        return None, _rec(sig, ledger.UNPROVABLE, ledger.ENTRY_FILL_UNPROVABLE_DATA_GAP)
    if event is None:
        return None, _rec(sig, ledger.CANCELLED if win.rollover_cancelled else ledger.NOT_EXECUTED,
                          ledger.ROLLOVER_CANCEL if win.rollover_cancelled else ledger.ENTRY_NOT_TRIGGERED)
    return (event, win), None


def _close_open_position(sig: ExecutionSignal, entry, stop, quotes, gaps, p, data_end):
    """Walk the quotes after the fill and take the first of stop, target, rollover or data end (D38 §4-7, §12-13)."""
    after = px.window(quotes, entry.time, data_end)
    after = after[after.index >= entry.time]
    roll = orders.rollover_start_after(entry.time, data_end, pre_min=p.rollover_pre_min,
                                       post_min=p.rollover_post_min, ny_time=p.rollover_ny_time)
    horizon = min([t for t in (roll, data_end) if t is not None])
    live = after[after.index <= horizon]
    stop_ev = fills.stop_touch(live, is_long=sig.is_long, stop=stop.stop)
    target_ev = None if sig.target_price is None else fills.target_touch(live, is_long=sig.is_long,
                                                                        target=sig.target_price)
    event = fills.first_event(stop_ev, target_ev)
    if event is not None and not event.resolved:
        return None, ledger.EXECUTION_UNPROVABLE_INTRABAR
    # An unresolved bar sitting before a resolved event is equally fatal: the earlier bar may have contained it.
    edge = event.time if event is not None else horizon
    span = live[(live.index >= entry.time) & (live.index <= edge)]
    if (~span["resolved"].astype(bool)).any():
        return None, ledger.EXECUTION_UNPROVABLE_INTRABAR
    if any(g.covers(entry.time, edge) for g in gaps):
        return None, ledger.TRADE_OUTCOME_UNPROVABLE_DATA_GAP
    if event is not None:
        return event, None
    if roll is not None:                                      # D38 §5: never carry a position across rollover
        last = px.last_quote_before(after, roll)
        if last is None:
            return None, ledger.TRADE_OUTCOME_UNPROVABLE_DATA_GAP
        when, row = last
        price = float(row["bid_close"]) if sig.is_long else float(row["ask_close"])
        return fills.Event(ledger.ROLLOVER_EXIT, when, price, 0.0, True), None
    last_t = after.index[-1]                                  # D38 §6: ledger completeness only
    row = after.iloc[-1]
    price = float(row["bid_close"]) if sig.is_long else float(row["ask_close"])
    return fills.Event(ledger.DATASET_END_EXIT, last_t, price, 0.0, True), None


def simulate(signals: list[dict], quotes: pd.DataFrame, *, gaps: list[px.Gap] | None = None,
             params: ExecutionParams | None = None) -> list[ledger.ExecutionRecord]:
    """Deterministic: the same signals and quotes always produce the same ledger."""
    p = params or ExecutionParams.frozen()
    gaps = gaps or []
    quotes = px.validate(quotes)
    data_end = quotes.index[-1]
    records: dict[str, ledger.ExecutionRecord] = {}
    live: list[ExecutionSignal] = []
    for raw in signals:
        sig = parse(raw)
        ok, why = eligible(raw)
        if not ok:
            rec = _rec(sig, ledger.NOT_EXECUTED, ledger.INELIGIBLE_BLOCKER)
            rec.data_confidence = {**rec.data_confidence, "eligibility": why}
            records[sig.signal_id] = rec
        else:
            live.append(sig)
    live.sort(key=lambda s: (s.activation_time or pd.Timestamp.max.tz_localize("UTC"), s.signal_id))

    book = PositionBook()
    unresolved = list(live)
    not_before: pd.Timestamp | None = None
    while unresolved:
        candidates, terminal = [], []
        for sig in unresolved:
            if not_before is not None and sig.activation_time is not None and sig.activation_time < not_before:
                terminal.append((sig, _rec(sig, ledger.NOT_EXECUTED, ledger.POSITION_ALREADY_OPEN)))
                continue
            got, rec = _entry_candidate(sig, quotes, gaps, p, data_end, not_before=not_before)
            if rec is not None:
                terminal.append((sig, rec))
            else:
                candidates.append((sig, got[0]))
        for sig, rec in terminal:
            records[sig.signal_id] = rec
            unresolved = [s for s in unresolved if s.signal_id != sig.signal_id]
        if not candidates:
            break
        winner, entry = min(candidates, key=lambda c: (c[1].time, c[0].signal_id))
        # D38 §15: only orders already pending at the winner's fill are cancelled as siblings. An order that
        # activates later is not a sibling; it meets the open position on the next pass (D38 §14).
        resolved_now = {winner.signal_id}
        for sig, _ev in candidates:
            if sig.signal_id == winner.signal_id:
                continue
            if sig.activation_time is not None and sig.activation_time <= entry.time:
                records[sig.signal_id] = _rec(sig, ledger.CANCELLED, ledger.SIBLING_ORDER_CANCELLED_ON_FILL)
                resolved_now.add(sig.signal_id)
        unresolved = [s for s in unresolved if s.signal_id not in resolved_now]
        records[winner.signal_id], closed_at = _run_trade(winner, entry, quotes, gaps, p, data_end)
        not_before = closed_at
        book.opened_at, book.closed_at = entry.time, closed_at
        if closed_at is None:
            break
    return list(records.values())


def _run_trade(sig: ExecutionSignal, entry, quotes, gaps, p: ExecutionParams, data_end):
    spread = px.spread_at(quotes, entry.time)
    if spread is None:
        return _rec(sig, ledger.NOT_EXECUTED, ledger.EXECUTION_DATA_UNAVAILABLE), None
    stop = resolve_stop(sig, fill_time=entry.time, spread=spread)
    if stop is None:
        return _rec(sig, ledger.NOT_EXECUTED, ledger.EXECUTION_DATA_UNAVAILABLE), None
    risk = ledger.initial_risk(sig.direction, entry.price, stop.stop)
    common = {"fill_time": str(entry.time), "fill_price": entry.price, "entry_gap": entry.gap,
              "initial_risk": risk, "tick_resolved": True,
              "additional_slippage": p.additional_slippage, "explicit_commission": p.explicit_commission,
              **stop.parts()}
    if risk <= 0:                                              # D38 §22: never executed
        return _rec(sig, ledger.NOT_EXECUTED, ledger.EXECUTION_INVALID_RISK, **common), None
    event, unprovable = _close_open_position(sig, entry, stop, quotes, gaps, p, data_end)
    if unprovable is not None:
        return _rec(sig, ledger.UNPROVABLE, unprovable, **common), None
    gross = ledger.gross_r(sig.direction, entry.price, event.price, risk)
    net = ledger.net_r(gross, risk, additional_slippage=p.additional_slippage,
                       explicit_commission=p.explicit_commission)
    extra = {"stop_trigger_time": str(event.time), "stop_gap": event.gap} if event.kind == ledger.STOP else {}
    return _rec(sig, ledger.CLOSED, None, exit_time=str(event.time), exit_price=event.price,
                exit_reason=event.kind, gross_r=gross, net_r=net, **common, **extra), event.time


def run_manifest(records: list[ledger.ExecutionRecord], extra: dict | None = None) -> dict:
    return ledger.manifest(records, provenance=provenance(), semantics=semantics(), extra=extra)
