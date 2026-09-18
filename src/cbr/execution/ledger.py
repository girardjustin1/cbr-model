"""Execution ledger: states, reasons, R arithmetic and the run manifest (owner ruling D38 §22-23, §27-28).

No CBR strategy rule is imported or re-derived anywhere in `cbr.execution` (D38 §33). This module owns the closed
enumerations, so a status can never be invented as free text downstream.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

import pandas as pd

SIMULATOR_VERSION = "14A.1"

# --- execution status (D38 §27): what happened to the signal, not why
NOT_EXECUTED, PENDING, FILLED, CANCELLED, CLOSED, UNPROVABLE = (
    "NOT_EXECUTED", "PENDING", "FILLED", "CANCELLED", "CLOSED", "UNPROVABLE")
STATUSES = (NOT_EXECUTED, PENDING, FILLED, CANCELLED, CLOSED, UNPROVABLE)

# --- exit reasons (D38 §28): only a CLOSED trade may carry one of these
TARGET, STOP, ROLLOVER_EXIT, DATASET_END_EXIT = "TARGET", "STOP", "ROLLOVER_EXIT", "DATASET_END_EXIT"
EXIT_REASONS = (TARGET, STOP, ROLLOVER_EXIT, DATASET_END_EXIT)
CANONICAL_EXITS = (TARGET, STOP)                    # ROLLOVER_EXIT / DATASET_END_EXIT are administrative (D38 §4)

# --- non-exit reason codes: these never pretend to be trade exits
ENTRY_NOT_TRIGGERED = "ENTRY_NOT_TRIGGERED"
SIBLING_ORDER_CANCELLED_ON_FILL = "SIBLING_ORDER_CANCELLED_ON_FILL"
POSITION_ALREADY_OPEN = "POSITION_ALREADY_OPEN"
ROLLOVER_CANCEL = "ROLLOVER_CANCEL"
EXECUTION_DATA_UNAVAILABLE = "EXECUTION_DATA_UNAVAILABLE"
ENTRY_FILL_UNPROVABLE_DATA_GAP = "ENTRY_FILL_UNPROVABLE_DATA_GAP"
TRADE_OUTCOME_UNPROVABLE_DATA_GAP = "TRADE_OUTCOME_UNPROVABLE_DATA_GAP"
EXECUTION_UNPROVABLE_INTRABAR = "EXECUTION_UNPROVABLE_INTRABAR"
EXECUTION_INVALID_RISK = "EXECUTION_INVALID_RISK"
INELIGIBLE_BLOCKER = "INELIGIBLE_BLOCKER"
REASON_CODES = (ENTRY_NOT_TRIGGERED, SIBLING_ORDER_CANCELLED_ON_FILL, POSITION_ALREADY_OPEN, ROLLOVER_CANCEL,
                EXECUTION_DATA_UNAVAILABLE, ENTRY_FILL_UNPROVABLE_DATA_GAP, TRADE_OUTCOME_UNPROVABLE_DATA_GAP,
                EXECUTION_UNPROVABLE_INTRABAR, EXECUTION_INVALID_RISK, INELIGIBLE_BLOCKER)
UNPROVABLE_REASONS = (ENTRY_FILL_UNPROVABLE_DATA_GAP, TRADE_OUTCOME_UNPROVABLE_DATA_GAP,
                      EXECUTION_UNPROVABLE_INTRABAR)


@dataclass
class ExecutionRecord:
    """One row per frozen signal (D38 §27). Every signal consumed appears exactly once, filled or not."""

    signal_id: str
    model: str
    variant: str
    direction: str
    signal_time: str | None
    activation_time: str | None
    trigger_price: float | None
    execution_status: str
    reason_code: str | None = None
    fill_time: str | None = None
    fill_price: float | None = None
    entry_gap: float | None = None
    signal_stop_anchor: float | None = None
    fill_time_stop_anchor: float | None = None
    stop_buffer: float | None = None
    fill_spread: float | None = None
    final_execution_stop: float | None = None
    target_price: float | None = None
    initial_risk: float | None = None
    exit_time: str | None = None
    exit_price: float | None = None
    exit_reason: str | None = None
    stop_trigger_time: str | None = None
    stop_gap: float | None = None
    gross_r: float | None = None
    net_r: float | None = None
    additional_slippage: float = 0.0
    explicit_commission: float = 0.0
    tick_resolved: bool | None = None
    data_confidence: dict = field(default_factory=dict)
    source_hashes: dict = field(default_factory=dict)
    simulator_version: str = SIMULATOR_VERSION

    def validate(self) -> None:
        if self.execution_status not in STATUSES:
            raise ValueError(f"unknown execution_status {self.execution_status!r}")
        if self.reason_code is not None and self.reason_code not in REASON_CODES:
            raise ValueError(f"unknown reason_code {self.reason_code!r}")
        if self.exit_reason is not None and self.exit_reason not in EXIT_REASONS:
            raise ValueError(f"unknown exit_reason {self.exit_reason!r}")
        if self.exit_reason is not None and self.execution_status != CLOSED:
            raise ValueError("only a CLOSED record may carry an exit_reason (D38 §28)")
        if self.execution_status == CLOSED and self.exit_reason is None:
            raise ValueError("a CLOSED record must carry an exit_reason")
        if self.execution_status == UNPROVABLE and self.reason_code not in UNPROVABLE_REASONS:
            raise ValueError("an UNPROVABLE record must carry an unprovable reason code")

    def as_dict(self) -> dict:
        self.validate()
        return asdict(self)


def initial_risk(direction: str, fill_price: float, stop: float) -> float:
    """D38 §22. Risk is measured from the actual filled trade; a non-positive risk is never executed."""
    return (fill_price - stop) if direction == "LONG" else (stop - fill_price)


def gross_r(direction: str, fill_price: float, exit_price: float, risk: float) -> float:
    """D38 §22."""
    move = (exit_price - fill_price) if direction == "LONG" else (fill_price - exit_price)
    return move / risk


def net_r(gross: float, risk: float, *, additional_slippage: float = 0.0, explicit_commission: float = 0.0) -> float:
    """D38 §23. Spread is already inside the bid/ask fills and is never subtracted again."""
    if additional_slippage == 0.0 and explicit_commission == 0.0:
        return gross                                     # nothing further is modelled at the 14A baseline
    return gross - (additional_slippage + explicit_commission) / risk


def frame(records: list[ExecutionRecord]) -> pd.DataFrame:
    rows = [r.as_dict() for r in records]
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=[f.name for f in ExecutionRecord.__dataclass_fields__.values()])


def result_hash(records: list[ExecutionRecord]) -> str:
    payload = json.dumps([r.as_dict() for r in records], sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def manifest(records: list[ExecutionRecord], *, provenance: dict, semantics: dict, extra: dict | None = None) -> dict:
    """The run manifest (acceptance D-5): baseline provenance, execution semantics, counts and the result hash."""
    df = frame(records)
    counts = {} if not len(df) else df["execution_status"].value_counts().to_dict()
    exits = {} if not len(df) else df["exit_reason"].value_counts(dropna=True).to_dict()
    return {
        "simulator_version": SIMULATOR_VERSION,
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "baseline_provenance": provenance,
        "execution_semantics": semantics,
        "signals": len(records), "by_status": counts, "by_exit_reason": exits,
        "administrative_exits": {k: exits.get(k, 0) for k in (ROLLOVER_EXIT, DATASET_END_EXIT)},
        "result_hash": result_hash(records),
        **(extra or {}),
    }
