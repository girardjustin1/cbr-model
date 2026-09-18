"""Executable quote access (owner ruling D38 §3, §7-8, §17-21).

The simulator consumes a **quote stream**: a chronological sequence of executable events. A tick event is fully
resolved; a bar event is not, because its intrabar ordering and its gap behaviour cannot be recovered. Fills are
decided only against this stream — never against STRUCTURE (mid) bars, which remain the signal's own input (D16).

No synthetic spread is ever produced (D38 §17): where executable data is absent, callers get nothing and must
report `EXECUTION_DATA_UNAVAILABLE`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time

import pandas as pd

from cbr.data.price_series import require_execution
from cbr.structure.levels import in_rollover

QUOTE_COLUMNS = ("bid_low", "bid_high", "ask_low", "ask_high", "bid_close", "ask_close", "resolved")
SCHEDULED_CLOSURE, ROLLOVER_WINDOW, DATA_GAP = "SCHEDULED_CLOSURE", "ROLLOVER_WINDOW", "DATA_GAP"


@dataclass(frozen=True)
class Gap:
    """A classified absence of data. Only `DATA_GAP` makes an outcome unprovable (D38 §18, §21)."""

    start: pd.Timestamp
    end: pd.Timestamp
    kind: str

    def covers(self, lo: pd.Timestamp, hi: pd.Timestamp) -> bool:
        return self.kind == DATA_GAP and self.start < hi and lo < self.end


def quotes_from_ticks(ticks: pd.DataFrame) -> pd.DataFrame:
    """Tick-level quotes: fully resolved, so sequencing is authoritative (D38 §7)."""
    q = pd.DataFrame(index=pd.DatetimeIndex(ticks.index, name="time"))
    for side in ("bid", "ask"):
        q[f"{side}_low"] = q[f"{side}_high"] = q[f"{side}_close"] = ticks[side].astype(float).to_numpy()
    q["resolved"] = True
    return q[list(QUOTE_COLUMNS)].sort_index()


def quotes_from_execution_bars(bars: pd.DataFrame) -> pd.DataFrame:
    """Bar-level quotes: **unresolved**. Any execution event decided inside one is unprovable (D38 §8)."""
    require_execution(bars)
    q = pd.DataFrame(index=pd.DatetimeIndex(bars.index, name="time"))
    for side in ("bid", "ask"):
        q[f"{side}_low"] = bars[f"{side}_low"].astype(float)
        q[f"{side}_high"] = bars[f"{side}_high"].astype(float)
        q[f"{side}_close"] = bars[f"{side}_close"].astype(float)
    q["resolved"] = False
    return q[list(QUOTE_COLUMNS)].sort_index()


def validate(quotes: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in QUOTE_COLUMNS if c not in quotes.columns]
    if missing:
        raise ValueError(f"quote stream missing {missing}")
    if not quotes.index.is_monotonic_increasing:
        raise ValueError("quote stream must be chronological")
    if (quotes["ask_low"] < quotes["bid_low"]).any() or (quotes["ask_high"] < quotes["bid_high"]).any():
        raise ValueError("ask must not be below bid in the quote stream")
    return quotes


def window(quotes: pd.DataFrame, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    lo = quotes.index[0] if start is None else start
    hi = quotes.index[-1] if end is None else end
    return quotes.loc[(quotes.index >= lo) & (quotes.index <= hi)]


def spread_at(quotes: pd.DataFrame, when: pd.Timestamp) -> float | None:
    """Contemporaneous spread at a quote instant. Never interpolated or forward-filled (D38 §17-18)."""
    if when not in quotes.index:
        return None
    row = quotes.loc[when]
    row = row.iloc[0] if isinstance(row, pd.DataFrame) else row
    return float(row["ask_close"]) - float(row["bid_close"])


def in_rollover_window(ts: pd.Timestamp, *, pre_min: int, post_min: int, ny_time: str = "17:00") -> bool:
    """The canonical rollover exclusion, reused from the strategy config (D38 §5, §16). No new rule is invented."""
    h, m = (int(x) for x in ny_time.split(":"))
    return in_rollover(ts, pre_min=pre_min, post_min=post_min, rollover=time(h, m))


def last_quote_before(quotes: pd.DataFrame, when: pd.Timestamp) -> tuple[pd.Timestamp, pd.Series] | None:
    before = quotes[quotes.index < when]
    if not len(before):
        return None
    return before.index[-1], before.iloc[-1]
