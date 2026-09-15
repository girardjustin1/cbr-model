"""Condition classifier: CBR_PRIMITIVES_V1 §2.

Thresholds are CANON (E1H-007, E1H-008, E15-014); median aggregation and the window point value are
ASSUMPTIONS (OQ-02, OQ-03). All inputs are filtered to what is known at `as_of`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from cbr.structure.swings import legs, usable

RANGE, TRENDING_RANGE, TREND, UNDEFINED = "RANGE", "TRENDING_RANGE", "TREND", "UNDEFINED"


@dataclass(frozen=True)
class Condition:
    condition: str
    c_med: float | None
    n_legs: int
    direction: str            # UP / DOWN / NONE, from the classifier tier's swings
    range_high: float | None
    range_low: float | None

    def pos(self, price: float) -> float | None:
        if self.range_high is None or self.range_high == self.range_low:
            return None
        return (price - self.range_low) / (self.range_high - self.range_low)


def _direction(known: pd.DataFrame) -> str:
    highs, lows = known[known["kind"] == "H"]["price"], known[known["kind"] == "L"]["price"]
    if len(highs) < 2 or len(lows) < 2:
        return "NONE"
    hh, hl = highs.iloc[-1] > highs.iloc[-2], lows.iloc[-1] > lows.iloc[-2]
    lh, ll = highs.iloc[-1] < highs.iloc[-2], lows.iloc[-1] < lows.iloc[-2]
    return "UP" if hh and hl else "DOWN" if lh and ll else "NONE"


def classify(swings: pd.DataFrame, bars_1m: pd.DataFrame, as_of: pd.Timestamp, window: pd.Timedelta, *,
             min_legs: int, range_min: float, trend_max: float, correction_cap: float,
             aggregate: str = "median", window_start: pd.Timestamp | None = None) -> Condition:
    """`window_start` overrides the clock window start `as_of − window` (tradable-time basis, OQ-40)."""
    start = as_of - window if window_start is None else window_start
    known = usable(swings, as_of)
    window_legs = legs(known)
    window_legs = window_legs[window_legs["t_start"] >= start]
    n = len(window_legs)

    in_window = bars_1m[(bars_1m.index >= start) & (bars_1m.index + pd.Timedelta(minutes=1) <= as_of)]
    r_high = float(in_window["high"].max()) if len(in_window) else None
    r_low = float(in_window["low"].min()) if len(in_window) else None
    direction = _direction(known)

    if n < min_legs:
        return Condition(UNDEFINED, None, n, direction, r_high, r_low)
    sizes = window_legs["size"].to_numpy()
    corrections = pd.Series(sizes[1:] / sizes[:-1]).clip(upper=correction_cap)
    c = float(corrections.median() if aggregate == "median" else corrections.mean())
    label = RANGE if c >= range_min else TRENDING_RANGE if c >= trend_max else TREND
    return Condition(label, c, n, direction, r_high, r_low)
