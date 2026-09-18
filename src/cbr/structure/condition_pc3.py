"""PC3 condition classification: a directionless trending range is a RANGE (owner ruling D29 §14, OQ-46).

Additive wrapper; PC2's `structure/condition.py` is pinned and unmodified. The correction-ratio classifier is unchanged.
Only the taxonomy gap is closed: Tom defines a trending range as correcting ~50% **and** making higher highs and higher
lows (V1H-what_direction_condition 00:01:58, 00:03:04), so a hour whose ratio says trending range while no directional
swing sequence exists is a RANGE, not an undefined trending range. No trend direction is inferred and no new classifier
is introduced.
"""

from __future__ import annotations

import dataclasses

import pandas as pd

from cbr.structure import condition as cond_mod


def classify_pc3(swings: pd.DataFrame, bars_1m: pd.DataFrame, as_of: pd.Timestamp, window: pd.Timedelta, *,
                 min_legs: int, range_min: float, trend_max: float, correction_cap: float,
                 aggregate: str = "median", window_start: pd.Timestamp | None = None) -> tuple[cond_mod.Condition, bool]:
    """PC2 classification, then the OQ-46 fallback. Returns (condition, fallback_applied)."""
    c = cond_mod.classify(swings, bars_1m, as_of, window, min_legs=min_legs, range_min=range_min,
                          trend_max=trend_max, correction_cap=correction_cap, aggregate=aggregate,
                          window_start=window_start)
    if c.condition == cond_mod.TRENDING_RANGE and c.direction == "NONE":
        return dataclasses.replace(c, condition=cond_mod.RANGE), True
    return c, False
