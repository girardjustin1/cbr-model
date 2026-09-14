"""Swing points and legs: CBR_PRIMITIVES_V1 §1 (causal ATR zig-zag, ASSUMPTION per OQ-01).

A swing high is confirmed on the first closed bar whose low is at least R = k x ATR below the running high
of the current up-leg (mirror for swing lows). A swing is usable only at/after `confirmed_at`.
"""

from __future__ import annotations

import math

import pandas as pd

SWING_COLUMNS = ["kind", "price", "time", "confirmed_at"]


def zigzag(bars: pd.DataFrame, atr: pd.Series, k: float, bar_length: pd.Timedelta) -> pd.DataFrame:
    """Confirmed swings, in order. kind 'H' or 'L'; time = open time of the extreme bar;
    confirmed_at = close time of the confirming bar. Bars without a defined ATR confirm nothing.

    Within one bar, a new extreme is taken before any reversal test (IMPL: OHLC has no intrabar order),
    so a bar that both extends and reverses confirms on a later bar.
    """
    rows = []
    direction = None
    hi = lo = None           # (price, time) running extremes before the first swing
    ext = None               # (price, time) running extreme of the current leg
    for t, high, low, a in zip(bars.index, bars["high"], bars["low"], atr.reindex(bars.index), strict=True):
        close_time = t + bar_length
        if direction is None:
            hi = (high, t) if hi is None or high > hi[0] else hi
            lo = (low, t) if lo is None or low < lo[0] else lo
            if a is None or math.isnan(a):
                continue
            r = k * a
            drop, rise = hi[0] - low, high - lo[0]
            if drop >= r and (rise < r or hi[1] < lo[1]):
                rows.append(("H", hi[0], hi[1], close_time))
                direction, ext = "DOWN", (low, t)
            elif rise >= r:
                rows.append(("L", lo[0], lo[1], close_time))
                direction, ext = "UP", (high, t)
            continue
        if a is None or math.isnan(a):
            continue
        r = k * a
        if direction == "UP":
            if high > ext[0]:
                ext = (high, t)
            elif ext[0] - low >= r:
                rows.append(("H", ext[0], ext[1], close_time))
                direction, ext = "DOWN", (low, t)
        else:
            if low < ext[0]:
                ext = (low, t)
            elif high - ext[0] >= r:
                rows.append(("L", ext[0], ext[1], close_time))
                direction, ext = "UP", (high, t)
    return _frame(rows, bars.index.dtype)


def _frame(rows: list[tuple], time_dtype) -> pd.DataFrame:
    """Explicit dtypes so an empty result is identical in schema to a populated one."""
    kinds, prices, times, confirmed = zip(*rows, strict=True) if rows else ((), (), (), ())
    return pd.DataFrame({
        "kind": pd.array(list(kinds), dtype="string"),
        "price": pd.array(list(prices), dtype="float64"),
        "time": pd.DatetimeIndex(list(times), dtype=time_dtype),
        "confirmed_at": pd.DatetimeIndex(list(confirmed), dtype=time_dtype),
    })


def usable(swings: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Swings known at `as_of` (IMPL causality)."""
    return swings[swings["confirmed_at"] <= as_of]


def legs(swings: pd.DataFrame) -> pd.DataFrame:
    """Segments between consecutive swings: start/end price and time, size, direction (+1 up, -1 down)."""
    if len(swings) < 2:
        return pd.DataFrame(columns=["t_start", "t_end", "p_start", "p_end", "size", "dir", "confirmed_at"])
    s, e = swings.iloc[:-1].reset_index(drop=True), swings.iloc[1:].reset_index(drop=True)
    out = pd.DataFrame({
        "t_start": s["time"], "t_end": e["time"], "p_start": s["price"], "p_end": e["price"],
        "confirmed_at": e["confirmed_at"],
    })
    out["size"] = (out["p_end"] - out["p_start"]).abs()
    out["dir"] = (out["p_end"] > out["p_start"]).map({True: 1, False: -1})
    return out
