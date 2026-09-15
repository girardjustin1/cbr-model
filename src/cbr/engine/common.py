"""Helpers shared by the CBR reference engines (STRUCTURE prices only, D16)."""

from __future__ import annotations

import pandas as pd

from cbr.data.sessions import expected_closed_mask

M1, S5, M15 = pd.Timedelta(minutes=1), pd.Timedelta(seconds=5), pd.Timedelta(minutes=15)


def _atr_at(series: pd.Series, bar_len: pd.Timedelta, as_of: pd.Timestamp) -> float | None:
    known = series[series.index + bar_len <= as_of].dropna()
    return float(known.iloc[-1]) if len(known) else None


def _minutes_complete(index: pd.DatetimeIndex, start: pd.Timestamp, end: pd.Timestamp) -> tuple[bool, int]:
    """All expected-open minutes in [start, end) have a STRUCTURE 1m bar."""
    if end <= start:
        return True, 0
    mins = pd.date_range(start, end, freq="1min", inclusive="left")
    expected = mins[~expected_closed_mask(mins)]
    missing = expected.difference(index)
    return len(missing) == 0, len(missing)


def _er(price: float, leg: pd.Series) -> float | None:
    return abs(price - leg["p_end"]) / leg["size"] if leg["size"] else None


def _anchor_path(s5s: pd.DataFrame, q0: pd.Timestamp, activation: pd.Timestamp, end: pd.Timestamp, d: str):
    """Most adverse STRUCTURE 5s extreme of the candle's extension since Q.t0: value (and bar close time) through
    `activation`, then each new extreme until `end` as [close_time, value] (lifecycle, causal at each time)."""
    sell = d == "SELL"
    col = "high" if sell else "low"
    bars = s5s[(s5s.index >= q0) & (s5s.index + S5 <= end)][col]
    if not len(bars):
        return None, None, []
    run = bars.cummax() if sell else bars.cummin()
    close = run.index + S5
    before = run[close <= activation]
    anchor = float(before.iloc[-1]) if len(before) else None
    anchor_time = None
    if len(before):
        hit = before[before == before.iloc[-1]]
        anchor_time = hit.index[0] + S5
    after = run[close > activation]
    changed = after[after != after.shift(1, fill_value=anchor if anchor is not None else float("nan"))]
    path = [[t + S5, float(v)] for t, v in changed.items()]
    return anchor, anchor_time, path


def anchor_at(row: pd.Series, t: pd.Timestamp) -> float | None:
    """Stop anchor in force at time t (latest path value with close ≤ t), for simulators and raw-setup resolution."""
    value = row["structure_stop_anchor"]
    for when, v in row["stop_anchor_path"]:
        if when <= t:
            value = v
    return value


