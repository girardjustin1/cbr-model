"""Market-session calendar shared by data checks and context modules (UTC in, New York schedule, DST-aware)."""

from __future__ import annotations

from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

NY = ZoneInfo("America/New_York")


def expected_closed(ts: pd.Timestamp) -> str | None:
    """Weekend (Fri 17:00 → Sun 18:00 New York) or the daily 17:00-18:00 New York break; else None."""
    ny = ts.tz_convert(NY)
    if ny.weekday() == 5 or (ny.weekday() == 4 and ny.hour >= 17) or (ny.weekday() == 6 and ny.hour < 18):
        return "weekend"
    if ny.hour == 17:
        return "daily_break"
    return None


def expected_closed_mask(minutes: pd.DatetimeIndex) -> np.ndarray:
    """Vectorized expected_closed for minute open times (UTC)."""
    ny = minutes.tz_convert(NY)
    wd, hr = ny.weekday, ny.hour
    return np.asarray((wd == 5) | ((wd == 4) & (hr >= 17)) | ((wd == 6) & (hr < 18)) | (hr == 17))


MAX_WINDOW_LOOKBACK = pd.Timedelta(days=7)


def tradable_window_start(as_of: pd.Timestamp, minutes: int, *, max_lookback: pd.Timedelta = MAX_WINDOW_LOOKBACK):
    """Start of a window holding `minutes` scheduled-tradable minutes before `as_of` (OQ-40 ruling D19-3, ASSUMPTION).

    Scheduled closures (weekend, daily break) don't consume the window. Unexpected vendor gaps inside scheduled-open
    time do: they stay in the timeline as missing data. Returns the open time of the earliest counted minute."""
    mins = pd.date_range((as_of - max_lookback).floor("1min"), as_of, freq="1min", inclusive="left")
    open_minutes = mins[~expected_closed_mask(mins)]
    if len(open_minutes) < minutes:
        return mins[0]
    return open_minutes[-minutes]
