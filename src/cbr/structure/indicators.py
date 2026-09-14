"""Causal indicators on OHLC bars (index = bar open time, UTC)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def atr(bars: pd.DataFrame, length: int) -> pd.Series:
    """Wilder ATR. The value at bar i uses bars 0..i only (known at bar i's close).

    First value (bar length-1) is the mean true range of the first `length` bars; NaN before that.
    """
    high, low, close = bars["high"].to_numpy(), bars["low"].to_numpy(), bars["close"].to_numpy()
    prev_close = np.concatenate(([np.nan], close[:-1]))
    tr = np.nanmax(np.vstack([high - low, np.abs(high - prev_close), np.abs(low - prev_close)]), axis=0)
    out = np.full(len(tr), np.nan)
    if len(tr) >= length:
        out[length - 1] = tr[:length].mean()
        for i in range(length, len(tr)):
            out[i] = (out[i - 1] * (length - 1) + tr[i]) / length
    return pd.Series(out, index=bars.index, name=f"atr{length}")
