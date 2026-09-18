"""Stop resolution and position lifecycle (owner ruling D38 §2, §4-6, §14-15, §22).

The stop is resolved **at the entry fill** from the latest canonical STRUCTURE anchor available causally through the
fill timestamp, then frozen: it is never trailed because later structure makes a new extreme.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from cbr.execution.contract import ExecutionSignal


@dataclass(frozen=True)
class StopResolution:
    signal_anchor: float | None          # the anchor known at the decision
    fill_anchor: float                   # the anchor available causally through the fill
    buffer: float
    spread: float
    stop: float

    def parts(self) -> dict:
        return {"signal_stop_anchor": self.signal_anchor, "fill_time_stop_anchor": self.fill_anchor,
                "stop_buffer": self.buffer, "fill_spread": self.spread, "final_execution_stop": self.stop}


def anchor_through(signal: ExecutionSignal, fill_time: pd.Timestamp) -> float | None:
    """D38 §2: SHORT takes the highest applicable structure extreme through fill, LONG the lowest.

    Only path points at or before the fill are read, so the anchor can never use later structure.
    """
    seen = [px for t, px in signal.stop_anchor_path if t <= fill_time]
    if signal.stop_anchor is not None:
        seen.append(signal.stop_anchor)
    if not seen:
        return None
    return min(seen) if signal.is_long else max(seen)


def resolve_stop(signal: ExecutionSignal, *, fill_time: pd.Timestamp, spread: float) -> StopResolution | None:
    """structure anchor (through fill) + approved buffer + the signal's frozen spread policy (D38 §2)."""
    anchor = anchor_through(signal, fill_time)
    if anchor is None:
        return None
    widen = signal.stop_buffer + (spread if signal.spread_policy == "ADD_SPREAD_AT_FILL" else 0.0)
    stop = anchor - widen if signal.is_long else anchor + widen
    return StopResolution(signal.stop_anchor, anchor, signal.stop_buffer, spread, stop)


@dataclass
class OpenPosition:
    signal: ExecutionSignal
    fill_time: pd.Timestamp
    fill_price: float
    stop: StopResolution
    target: float | None
    initial_risk: float


class PositionBook:
    """One open CBR1H position per instrument (D38 §14). Variants A and B are never concurrent trades."""

    def __init__(self) -> None:
        self.open: OpenPosition | None = None
        self.opened_at: pd.Timestamp | None = None
        self.closed_at: pd.Timestamp | None = None

    def is_open_at(self, when: pd.Timestamp) -> bool:
        if self.opened_at is None:
            return False
        return self.opened_at <= when and (self.closed_at is None or when < self.closed_at)

    def occupied(self) -> bool:
        return self.open is not None
