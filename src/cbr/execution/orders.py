"""Entry-order lifecycle: when an order is live, and what ends it (owner ruling D38 §11, §16, §19).

An order is live from its activation time until the earliest of its expiry, its frozen cancel time, and the start of
the canonical rollover exclusion window. Quotes outside that window can never fill it.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from cbr.execution import prices as px
from cbr.execution.contract import ExecutionSignal


@dataclass(frozen=True)
class OrderWindow:
    start: pd.Timestamp
    end: pd.Timestamp
    rollover_cancelled: bool             # the window was cut short by the rollover exclusion (D38 §16)
    valid: bool

    def empty(self) -> bool:
        return not self.valid or self.end < self.start


def rollover_start_after(when: pd.Timestamp, until: pd.Timestamp, *, pre_min: int, post_min: int,
                         ny_time: str) -> pd.Timestamp | None:
    """The first minute at or after `when` that falls inside the exclusion window, if one occurs before `until`."""
    if until < when:
        return None
    for t in pd.date_range(when.floor("1min"), until.ceil("1min"), freq="1min", tz="UTC"):
        if px.in_rollover_window(t, pre_min=pre_min, post_min=post_min, ny_time=ny_time):
            return max(t, when)
    return None


def window(signal: ExecutionSignal, *, data_end: pd.Timestamp, pre_min: int, post_min: int,
           ny_time: str) -> OrderWindow:
    """D38 §11 and §16: live from activation, ended by expiry, cancel or the rollover exclusion."""
    start = signal.activation_time
    if start is None:
        return OrderWindow(pd.NaT, pd.NaT, False, False)
    ends = [e for e in (signal.expiry_time, signal.cancel_time, data_end) if e is not None]
    end = min(ends) if ends else data_end
    if px.in_rollover_window(start, pre_min=pre_min, post_min=post_min, ny_time=ny_time):
        return OrderWindow(start, start, True, False)          # may not even activate inside the window
    if end < start:
        return OrderWindow(start, end, False, False)       # no executable window at all: not a rollover cancel
    roll = rollover_start_after(start, end, pre_min=pre_min, post_min=post_min, ny_time=ny_time)
    if roll is not None:
        return OrderWindow(start, roll, True, True)
    return OrderWindow(start, end, False, True)
