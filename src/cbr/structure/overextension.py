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


def evaluate(bars_1m: pd.DataFrame, candle_open_time: pd.Timestamp, candle_open: float, as_of: pd.Timestamp, *,
             atr_1m: float, activation_atr: float, pullback_frac: float, two_sided_frac: float,
             prev_candle_high: float | None = None, prev_candle_low: float | None = None) -> Overextension:
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
    no_pullback, running = True, candle_open
    activation = activation_atr * atr_1m
    for t in inside.loc[:extreme_time].index:
        ext_so_far = sign * (running - candle_open)
        if ext_so_far >= activation and sign * (running - against.loc[t]) >= pullback_frac * ext_so_far:
            no_pullback = False
            break
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
        duration_min=(extreme_time - candle_open_time) / ONE_MINUTE,
        no_pullback=no_pullback, opposite_wick=opposite_wick,
        two_sided=size > 0 and opposite >= two_sided_frac * size, prev_candle_break=prev_break,
    )
