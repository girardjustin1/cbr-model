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
