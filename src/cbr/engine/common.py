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


def condition_window(index: pd.DatetimeIndex, as_of: pd.Timestamp, window: pd.Timedelta, basis: str) -> dict:
    """Condition-window start and its three durations, recorded separately (OQ-40 ruling D19-3).

    CLOCK: [as_of − window, as_of). TRADABLE: the window holds `window` scheduled-tradable minutes, so scheduled closures
    don't consume it; minutes that were scheduled open but have no bar (vendor gaps) still count as time."""
    from cbr.data.sessions import tradable_window_start

    if basis == "CLOCK":
        start = as_of - window
    elif basis == "TRADABLE":
        start = tradable_window_start(as_of, int(window / M1))
    else:
        raise ValueError(f"unknown condition window basis {basis!r}")
    mins = pd.date_range(start, as_of, freq="1min", inclusive="left")
    scheduled_open = mins[~expected_closed_mask(mins)]
    return {"condition_window_start": start, "condition_window_basis": basis,
            "condition_elapsed_clock_minutes": int((as_of - start) / M1),
            "condition_tradable_minutes": len(scheduled_open),
            "condition_missing_minutes": len(scheduled_open.difference(index))}


def prev_15m_break(s5s: pd.DataFrame, b15: pd.DataFrame, q0: pd.Timestamp, as_of: pd.Timestamp, d: str) -> dict:
    """OQ-41 ruling D19-4. Q = the 15m candle opening at q0, Q−1 = the previous completed 15m candle. The break must be
    made by Q itself: STRUCTURE 5s bars of Q closed by `as_of` take Q−1's high (SELL setups, an up-extension) or low
    (BUY). Exception (E1H-023, V1H-1m_fractal_shift 00:03:23): Q−1 closed in the trade direction."""
    prev_open = q0 - M15
    out = {"q_open_utc": q0, "q_prev_open_utc": prev_open, "q_prev_high": None, "q_prev_low": None,
           "q_break_by_q": None, "q_prev_closed_in_trade_direction": None}
    if prev_open not in b15.index:
        return out
    prev = b15.loc[prev_open]
    inside = s5s[(s5s.index >= q0) & (s5s.index + S5 <= as_of)]
    sell = d == "SELL"
    broke = bool(len(inside)) and (float(inside["high"].max()) > float(prev["high"]) if sell
                                   else float(inside["low"].min()) < float(prev["low"]))
    out.update({"q_prev_high": float(prev["high"]), "q_prev_low": float(prev["low"]), "q_break_by_q": broke,
                "q_prev_closed_in_trade_direction": bool(prev["close"] < prev["open"]) if sell
                else bool(prev["close"] > prev["open"])})
    return out
