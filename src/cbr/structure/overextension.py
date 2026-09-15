"""Candle overextension (OE): CBR_PRIMITIVES_V1 §3.

Evaluated from 1m bars that are inside the candle and closed at `as_of`.
CANON: 50% pullback definition (E1H-018), previous-15m-candle break (E1H-017, E15-034).
ASSUMPTION: activation floor and two-sided fraction (OQ-08).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

ONE_MINUTE = pd.Timedelta(minutes=1)


@dataclass(frozen=True)
class Overextension:
    direction: str                 # UP / DOWN / NONE
    extreme: float | None
    extreme_time: pd.Timestamp | None
    size: float                    # |extreme - open|
    duration_min: float            # minutes from candle open to the bar that set the extreme
    no_pullback: bool
    opposite_wick: float           # opposite excursion before the extreme, as a fraction of size
    two_sided: bool
    prev_candle_break: bool | None
    origin_time: pd.Timestamp | None = None      # start of the measured push (candle open unless LAST_RESET reset it)


def evaluate(bars_1m: pd.DataFrame, candle_open_time: pd.Timestamp, candle_open: float, as_of: pd.Timestamp, *,
             atr_1m: float, activation_atr: float, pullback_frac: float, two_sided_frac: float,
             prev_candle_high: float | None = None, prev_candle_low: float | None = None,
             origin: str = "HOUR_OPEN") -> Overextension:
    """origin HOUR_OPEN (V1 baseline, D8): duration and no-pullback measured from the candle open. LAST_RESET (the D8
    ablation, OQ-22): a ≥ 50% pullback restarts the count from its most adverse price, so duration runs from the start of
    the last push; direction, extreme, size, wick and the previous-candle break stay measured from the candle open."""
    if origin not in ("HOUR_OPEN", "LAST_RESET"):
        raise ValueError(f"unknown oe origin {origin!r}")
    inside = bars_1m[(bars_1m.index >= candle_open_time) & (bars_1m.index + ONE_MINUTE <= as_of)]
    if inside.empty:
        return Overextension("NONE", None, None, 0.0, 0.0, False, 0.0, False, None)

    up = float(inside["high"].max()) - candle_open
    down = candle_open - float(inside["low"].min())
    direction = "UP" if up >= down else "DOWN"
    sign = 1 if direction == "UP" else -1
    favour = inside["high"] if direction == "UP" else inside["low"]
    against = inside["low"] if direction == "UP" else inside["high"]

    extreme_time = favour.idxmax() if direction == "UP" else favour.idxmin()   # first bar reaching the extreme
    extreme = float(favour.loc[extreme_time])
    size = abs(extreme - candle_open)

    # 50% pullback test along the path to the extreme. For each bar, compare its adverse price with the running
    # extreme *before* the bar updates it (OHLC has no intrabar order; IMPL).
    no_pullback, running, base, origin_time = True, candle_open, candle_open, candle_open_time
    reset = False
    activation = activation_atr * atr_1m
    for t in inside.loc[:extreme_time].index:
        if reset and sign * (base - against.loc[t]) > 0:           # the pullback keeps extending: the push hasn't started
            base, running, origin_time = float(against.loc[t]), float(against.loc[t]), t
        ext_so_far = sign * (running - base)
        if ext_so_far >= activation and sign * (running - against.loc[t]) >= pullback_frac * ext_so_far:
            if origin == "HOUR_OPEN":
                no_pullback = False
                break
            base, running, origin_time, reset = float(against.loc[t]), float(against.loc[t]), t, True
        if sign * (favour.loc[t] - running) > 0:
            running = float(favour.loc[t])

    before = inside.loc[:extreme_time]
    opposite = (candle_open - float(before["low"].min())) if direction == "UP" else (float(before["high"].max()) - candle_open)
    opposite = max(opposite, 0.0)
    opposite_wick = opposite / size if size > 0 else 0.0

    prev_break = None
    if direction == "UP" and prev_candle_high is not None:
        prev_break = extreme > prev_candle_high
    if direction == "DOWN" and prev_candle_low is not None:
        prev_break = extreme < prev_candle_low

    return Overextension(
        direction=direction, extreme=extreme, extreme_time=extreme_time, size=size,
        duration_min=(extreme_time - origin_time) / ONE_MINUTE,
        no_pullback=no_pullback, opposite_wick=opposite_wick,
        two_sided=size > 0 and opposite >= two_sided_frac * size, prev_candle_break=prev_break, origin_time=origin_time,
    )
