"""The frozen fill rules (owner ruling D38 §10, §12, §13, §7-8). One named function per rule, each tested.

Side semantics never vary (D38 §3):
    LONG  — entry on ASK, stop and target observed and executed against BID.
    SHORT — entry on BID, stop and target observed and executed against ASK.

A quote row that is not tick-resolved can decide nothing: its intrabar ordering and its gap behaviour are unknown,
so the caller reports `EXECUTION_UNPROVABLE_INTRABAR` rather than choosing a convention (D38 §8).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Event:
    kind: str                    # ENTRY / STOP / TARGET
    time: pd.Timestamp
    price: float
    gap: float                   # how far the executable quote moved through the level; 0.0 when it did not
    resolved: bool               # False => the caller must treat the outcome as unprovable


def _row(quotes: pd.DataFrame, when):
    r = quotes.loc[when]
    return r.iloc[0] if isinstance(r, pd.DataFrame) else r


def entry_touch(quotes: pd.DataFrame, *, is_long: bool, trigger: float) -> Event | None:
    """D38 §10-11. LONG triggers when ASK >= trigger and fills at that ASK; SHORT when BID <= trigger, fills at BID.

    The order never receives the theoretical trigger price when the first executable quote has moved through it.
    """
    side_high, side_low = ("ask_high", "ask_low") if is_long else ("bid_high", "bid_low")
    hit = quotes[quotes[side_high] >= trigger] if is_long else quotes[quotes[side_low] <= trigger]
    if not len(hit):
        return None
    when = hit.index[0]
    row = _row(quotes, when)
    if not bool(row["resolved"]):
        return Event("ENTRY", when, float("nan"), float("nan"), False)
    price = float(row["ask_close"]) if is_long else float(row["bid_close"])
    gap = (price - trigger) if is_long else (trigger - price)
    return Event("ENTRY", when, price, max(gap, 0.0), True)


def stop_touch(quotes: pd.DataFrame, *, is_long: bool, stop: float) -> Event | None:
    """D38 §12. LONG stops when BID <= stop and fills at that BID; SHORT when ASK >= stop, fills at that ASK.

    A jump through the stop fills at the worse executable quote; the theoretical stop price is never granted.
    """
    hit = quotes[quotes["bid_low"] <= stop] if is_long else quotes[quotes["ask_high"] >= stop]
    if not len(hit):
        return None
    when = hit.index[0]
    row = _row(quotes, when)
    if not bool(row["resolved"]):
        return Event("STOP", when, float("nan"), float("nan"), False)
    price = float(row["bid_close"]) if is_long else float(row["ask_close"])
    gap = (stop - price) if is_long else (price - stop)
    return Event("STOP", when, price, max(gap, 0.0), True)


def target_touch(quotes: pd.DataFrame, *, is_long: bool, target: float) -> Event | None:
    """D38 §13. Targets are LIMIT exits: LONG needs BID >= target, SHORT needs ASK <= target.

    The fill is **at the target price** even when the quote gapped past it: without order-book data, price
    improvement cannot be proven, so the baseline is deliberately conservative.
    """
    hit = quotes[quotes["bid_high"] >= target] if is_long else quotes[quotes["ask_low"] <= target]
    if not len(hit):
        return None
    when = hit.index[0]
    row = _row(quotes, when)
    if not bool(row["resolved"]):
        return Event("TARGET", when, float("nan"), float("nan"), False)
    crossing = float(row["bid_close"]) if is_long else float(row["ask_close"])
    improvement = (crossing - target) if is_long else (target - crossing)
    return Event("TARGET", when, target, max(improvement, 0.0), True)      # `gap` records the unclaimed improvement


def first_event(*events: Event | None) -> Event | None:
    """D38 §7: the first event actually observed wins, by tick sequence. Ties keep the order the caller passed."""
    live = [e for e in events if e is not None]
    if not live:
        return None
    return min(live, key=lambda e: (e.time, 0))
