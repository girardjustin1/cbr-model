"""Levels, AOI zones and canonical no-trade windows: CBR_PRIMITIVES_V1 §5 and §7."""

from __future__ import annotations

from datetime import time
from zoneinfo import ZoneInfo

import pandas as pd

NEW_YORK = ZoneInfo("America/New_York")


def candle_close_levels(candles: pd.DataFrame, candle_length: pd.Timedelta) -> pd.DataFrame:
    """A level forms when candle close direction flips (P1F-49, EP1-002). Price = the flipping candle's open;
    usable from that candle's close. Doji candles (close == open) neither form nor break a flip."""
    direction = (candles["close"] - candles["open"]).apply(lambda d: 1 if d > 0 else -1 if d < 0 else 0)
    rows, last = [], 0
    for t, d, o in zip(candles.index, direction, candles["open"], strict=True):
        if d != 0:
            if last != 0 and d != last:
                rows.append({"price": float(o), "candle_time": t, "formed_at": t + candle_length})
            last = d
    return pd.DataFrame(rows, columns=["price", "candle_time", "formed_at"])


def aoi_tap(levels: pd.DataFrame, price: float, as_of: pd.Timestamp, *, zone: float,
            lookback: pd.Timedelta) -> bool:
    known = levels[(levels["formed_at"] <= as_of) & (levels["formed_at"] >= as_of - lookback)]
    return bool(((known["price"] - price).abs() <= zone).any())


def in_sydney_session(ts: pd.Timestamp, *, reopen: time = time(18, 0)) -> bool:
    """Sydney-only hours: from the daily reopen (18:00 New York) until the next Tokyo open at 00:00 UTC
    (EP1-015…017). 18:00 New York is 22:00 or 23:00 UTC, so the window always ends at the following UTC midnight."""
    utc = ts.tz_convert("UTC")
    ny = utc.tz_convert(NEW_YORK)
    start = ny.replace(hour=reopen.hour, minute=reopen.minute, second=0, microsecond=0, nanosecond=0)
    end = start.tz_convert("UTC").normalize() + pd.Timedelta(days=1)
    return start <= ny and utc < end


def in_rollover(ts: pd.Timestamp, *, pre_min: int, post_min: int, rollover: time = time(17, 0)) -> bool:
    """No new entries within [17:00 - pre, 17:00 + post] New York time, DST-aware (EP1-018)."""
    ny = ts.tz_convert(NEW_YORK)
    anchor = ny.replace(hour=rollover.hour, minute=rollover.minute, second=0, microsecond=0, nanosecond=0)
    return anchor - pd.Timedelta(minutes=pre_min) <= ny <= anchor + pd.Timedelta(minutes=post_min)
