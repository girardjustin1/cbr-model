"""Deterministic historical replay of frozen signals against real quotes (owner ruling D39 §7).

The driver asks one question only — *what happened to this already-valid research signal under the frozen D38
execution semantics?* It never asks whether a signal should exist. No CBR rule module is imported here, and the
architecture guard enforces that for the whole package.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import pandas as pd

from cbr.engine.params import ROOT
from cbr.execution import ledger, market_data
from cbr.execution.contract import ContractError, parse
from cbr.execution.simulate import EXECUTION_CONFIG, ExecutionParams, semantics, simulate
from cbr.execution.simulate import run_manifest as _base_manifest


@dataclass(frozen=True)
class ReplayResult:
    records: list[ledger.ExecutionRecord]
    provenance: dict

    def frame(self) -> pd.DataFrame:
        return ledger.frame(self.records)


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def signal_hash(signals: list[dict]) -> str:
    return _sha_text(json.dumps(signals, sort_keys=True, default=str))


def execution_config_hash() -> str:
    return _sha_text(EXECUTION_CONFIG.read_text())


def adapt(signal: dict) -> tuple[object | None, str | None]:
    """Frozen contract → execution order (D39 §11). A missing required input refuses; nothing is invented."""
    try:
        sig = parse(signal)
    except ContractError as exc:
        return None, str(exc)
    if sig.activation_time is None:
        return None, "signal carries no activation time"
    if sig.trigger_price is None:
        return None, "signal carries no entry reference price"
    if sig.stop_anchor is None and not sig.stop_anchor_path:
        return None, "signal carries neither a stop anchor nor an anchor path"
    if not sig.spread_policy:
        return None, "signal carries no spread policy"
    return sig, None


def replay(signals: list[dict], start: pd.Timestamp, end: pd.Timestamp, *, instrument: str = "xauusd",
           params: ExecutionParams | None = None) -> ReplayResult:
    """Load real quotes for the window, classify its intervals, and run the frozen simulator over them."""
    p = params or ExecutionParams.frozen()
    quotes, prov = market_data.load_quotes(start, end, instrument=instrument)
    gaps, counts = market_data.classify_intervals(
        start, end, quotes, prov, rollover_pre_min=p.rollover_pre_min, rollover_post_min=p.rollover_post_min,
        rollover_ny_time=p.rollover_ny_time)
    records: list[ledger.ExecutionRecord] = []
    executable: list[dict] = []
    for raw in signals:
        sig, why = adapt(raw)
        if sig is None:
            records.append(ledger.ExecutionRecord(
                signal_id=raw.get("signal_id", "UNKNOWN"), model=raw.get("model", ""), variant=raw.get("variant", ""),
                direction=raw.get("direction", ""), signal_time=str(raw.get("timestamp")),
                activation_time=None, trigger_price=None,
                execution_status=ledger.NOT_EXECUTED, reason_code=ledger.EXECUTION_DATA_UNAVAILABLE,
                data_confidence={"adapter": why}))
        else:
            executable.append(raw)
    if len(quotes):
        records += simulate(executable, quotes, gaps=gaps, params=p)
    else:
        for raw in executable:
            sig = parse(raw)
            records.append(ledger.ExecutionRecord(
                signal_id=sig.signal_id, model=sig.model, variant=sig.variant, direction=sig.direction,
                signal_time=str(sig.signal_time),
                activation_time=None if sig.activation_time is None else str(sig.activation_time),
                trigger_price=sig.trigger_price, execution_status=ledger.NOT_EXECUTED,
                reason_code=ledger.EXECUTION_DATA_UNAVAILABLE))
    provenance = {
        **_base_manifest(records),
        "market_data": {**prov.as_dict(), "classified_intervals": counts},
        "execution_config_hash": execution_config_hash(),
        "execution_semantics": semantics(),
        "signal_hash": signal_hash(signals),
        "repo_root": str(ROOT.name),
    }
    return ReplayResult(records, provenance)


def execute_signal(signal: dict, start: pd.Timestamp, end: pd.Timestamp, **kw) -> ReplayResult:
    """Single-signal convenience wrapper with the same semantics (D39 §7)."""
    return replay([signal], start, end, **kw)


def gap_kinds() -> tuple[str, ...]:
    return (market_data.SCHEDULED_CLOSURE, market_data.ROLLOVER_EXCLUSION, market_data.DATA_GAP,
            market_data.VALID_SPARSE_QUOTES, market_data.NOT_LOADED)


__all__ = ["ReplayResult", "adapt", "execute_signal", "execution_config_hash", "gap_kinds", "replay", "signal_hash"]
