"""Frozen signal contract and the external eligibility gate (owner ruling D38 §1, §26).

Phase 14A consumes signals; it never derives them. This module validates a signal against the contract pinned in
`tests/engine/test_pc4_signal_contract.py` and applies the D37 promotion gate, without editing PC4 or its records.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from cbr.engine.baseline_v1 import CANDIDATE, FROZEN_SPEC_HASH

# PC4 was frozen before its own parity run, so every signal still carries this blocker. D37 promotes the model; the
# frozen artefact is never rewritten, so the gate lives here (D38 §26).
PROMOTION_BLOCKER = "PHASE13C_PARITY_NOT_RUN"
REQUIRED_FIELDS = ("signal_id", "model", "variant", "direction", "timestamp", "entry_trigger_time",
                   "entry_expiry_time", "entry_order_type", "entry_reference_price", "stop_rule", "target_price",
                   "eligibility", "lifecycle", "spec_hash", "price_role")


class ContractError(ValueError):
    """The signal does not match the frozen contract."""


@dataclass(frozen=True)
class ExecutionSignal:
    """The execution-facing view of a frozen signal. Nothing here is recomputed from market structure."""

    signal_id: str
    model: str
    variant: str
    direction: str                       # LONG / SHORT
    signal_time: pd.Timestamp
    activation_time: pd.Timestamp | None
    expiry_time: pd.Timestamp | None
    cancel_time: pd.Timestamp | None
    trigger_price: float
    target_price: float | None
    stop_anchor: float | None            # STRUCTURE anchor known at the decision
    stop_anchor_path: tuple                # [(time, price)] through activation, for the at-fill anchor (D38 §2)
    stop_buffer: float                   # absolute price buffer: buffer_atr x ATR(1m,14) at the decision
    spread_policy: str
    raw: dict

    @property
    def is_long(self) -> bool:
        return self.direction == "LONG"


def _ts(v):
    return None if v in (None, "") or (not isinstance(v, str) and pd.isna(v)) else pd.Timestamp(v)


def eligible(signal: dict) -> tuple[bool, str | None]:
    """D38 §26: executable only under the D37 promotion gate, with no blocker other than the expected one."""
    if signal.get("model") != CANDIDATE:
        return False, f"signal model {signal.get('model')!r} is not the promoted candidate {CANDIDATE}"
    if signal.get("spec_hash") != FROZEN_SPEC_HASH:
        return False, "signal spec_hash does not resolve to the frozen PC4 specification"
    blockers = list(signal.get("eligibility", {}).get("blockers", []))
    unexpected = [b for b in blockers if b != PROMOTION_BLOCKER]
    if unexpected:
        return False, f"unexpected eligibility blocker(s): {unexpected}"
    return True, None


def parse(signal: dict) -> ExecutionSignal:
    """Validate against the frozen contract and project it into the execution view."""
    missing = [f for f in REQUIRED_FIELDS if f not in signal]
    if missing:
        raise ContractError(f"signal missing contract fields: {missing}")
    if signal["price_role"] != "STRUCTURE":
        raise ContractError("signals are built on STRUCTURE bars; execution reads EXECUTION bars separately (D16)")
    if signal["entry_order_type"] != "STOP":
        raise ContractError(f"unsupported entry_order_type {signal['entry_order_type']!r}")
    if signal["direction"] not in ("LONG", "SHORT"):
        raise ContractError(f"unknown direction {signal['direction']!r}")
    stop_rule = signal["stop_rule"]
    if stop_rule.get("final_execution_stop") is not None or signal.get("stop_price") is not None:
        raise ContractError("the frozen contract must not carry an executable stop; execution resolves it (OQ-28)")
    buffer_node = stop_rule.get("buffer") or {}
    atr = buffer_node.get("atr_at_decision")
    value = buffer_node.get("value")
    if atr is None or value is None:
        raise ContractError("stop_rule.buffer must carry both its parameter value and the ATR at the decision")
    path = tuple((pd.Timestamp(t), float(p)) for t, p in (stop_rule.get("stop_anchor_path") or []) if t is not None)
    return ExecutionSignal(
        signal_id=signal["signal_id"], model=signal["model"], variant=signal["variant"],
        direction=signal["direction"], signal_time=pd.Timestamp(signal["timestamp"]),
        activation_time=_ts(signal["entry_trigger_time"]), expiry_time=_ts(signal["entry_expiry_time"]),
        cancel_time=_ts(signal["lifecycle"].get("cancel_time")),
        trigger_price=float(signal["entry_reference_price"]),
        target_price=None if signal["target_price"] is None else float(signal["target_price"]),
        stop_anchor=None if stop_rule.get("structure_stop_anchor") is None
        else float(stop_rule["structure_stop_anchor"]),
        stop_anchor_path=path, stop_buffer=float(value) * float(atr),
        spread_policy=stop_rule.get("spread_policy", ""), raw=signal)
