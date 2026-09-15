"""Type 3 shifts, HILO and HVCS: CBR_PRIMITIVES_V1 §4.

Type 3 (EP1-008, EP1-009): take out a swing high, immediately reverse, take out the swing low before it (sell);
mirror for buy. HILO (EP2-001…003, frame-confirmed). HVCS structure (EP2-005), duration (E1H-034).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Type3:
    direction: str               # SELL (bearish shift) / BUY (bullish shift)
    swept_swing_time: pd.Timestamp
    swept_price: float           # swing taken out first
    broken_price: float          # opposite swing broken second
    sweep_time: pd.Timestamp     # first bar taking out the swept swing
    break_time: pd.Timestamp     # first bar breaking the opposite swing (bar open time)
    sweep_extreme: float         # most extreme price between sweep and break (stop anchor, EP1-012)
    trigger_price: float


@dataclass(frozen=True)
class Type3Arm:
    """One swept pattern (the moment a type 3 becomes possible), with how it ended."""
    direction: str
    swept_swing_time: pd.Timestamp
    swept_price: float
    broken_swing_time: pd.Timestamp
    broken_price: float
    sweep_time: pd.Timestamp            # open time of the sweeping bar; the arm is known at its close
    sweep_bar_extreme: float            # high (SELL) / low (BUY) of the sweeping bar
    trigger_price: float
    end: str                            # BREAK / TIMEOUT / NEW_SWING / DATA_END
    end_time: pd.Timestamp | None       # open time of the bar where the end happened
    extreme_before_end: float           # most extreme price from the sweep up to (not incl.) the break bar
    pair_was_latest: bool               # the swept/broken pair were the last two confirmed swings at the sweep


def track_type3(bars: pd.DataFrame, swings: pd.DataFrame, *, max_reversal: pd.Timedelta, tick: float,
                latest_pair_only: bool = False) -> list[Type3Arm]:
    """Every type 3 sweep on one tier and how it ended (EP1-008, EP1-009; spec §4.1).

    With the last two confirmed swings X then Y (Y formed after X): X high → SELL (take out X, then break Y);
    X low → BUY. A pair is armed once Y is confirmed (swings usable at the bar's open). Ends: BREAK (a later bar breaks
    Y), TIMEOUT (bar more than `max_reversal` after the sweep), NEW_SWING (a new swing of Y's kind confirmed after the
    sweep), DATA_END. Swings of X's kind confirmed after the sweep don't disarm.

    `latest_pair_only=False` reproduces `find_type3`'s historical behaviour: an unswept pair stays armed after newer
    swings confirm. `latest_pair_only=True` applies spec §4.1 literally: an unswept pair is disarmed as soon as a newer
    swing is confirmed (finding F-3). `pair_was_latest` is recorded either way.
    """
    kinds = swings["kind"].to_numpy()
    prices = swings["price"].to_numpy(dtype=float)
    stimes = list(swings["time"])                # Timestamps with the swings' own timezone
    confirmed = pd.DatetimeIndex(swings["confirmed_at"]).as_unit("ns").asi8     # epoch ns (UTC when tz-aware)
    n_sw, ptr = len(swings), 0
    arms: list[Type3Arm] = []
    armed: dict[int, dict] = {}                 # keyed by the index of Y (the swing to break)
    seen: set[int] = set()
    bar_ns = bars.index.as_unit("ns").asi8
    for t, t64, high, low in zip(bars.index, bar_ns, bars["high"].to_numpy(), bars["low"].to_numpy(), strict=True):
        grew = False
        while ptr < n_sw and confirmed[ptr] <= t64:
            ptr, grew = ptr + 1, True
        if grew and latest_pair_only:
            for key in [k for k, st in armed.items() if st["sweep_time"] is None and k != ptr - 1]:
                del armed[key]
        y = ptr - 1
        if ptr >= 2 and kinds[y - 1] != kinds[y] and y not in seen:
            seen.add(y)
            armed[y] = {"side": "SELL" if kinds[y - 1] == "H" else "BUY", "x": y - 1, "y": y, "sweep_time": None,
                        "extreme": None, "sweep_bar_extreme": None, "latest": False}
        for key, st in list(armed.items()):
            side, x, yy = st["side"], st["x"], st["y"]
            if st["sweep_time"] is None:
                if (high > prices[x]) if side == "SELL" else (low < prices[x]):
                    st["sweep_time"], st["sweep_ns"] = t, t64
                    st["extreme"] = st["sweep_bar_extreme"] = float(high if side == "SELL" else low)
                    st["latest"] = yy == ptr - 1
                continue
            end = None
            if t - st["sweep_time"] > max_reversal:
                end = "TIMEOUT"
            else:
                later = np.arange(yy + 1, ptr)
                if len(later) and np.any((kinds[later] == kinds[yy])
                                         & (confirmed[later] > st["sweep_ns"])):
                    end = "NEW_SWING"
                elif (low < prices[yy]) if side == "SELL" else (high > prices[yy]):
                    end = "BREAK"
            if end:
                arms.append(_arm(st, prices, stimes, tick, end, t))
                del armed[key]
                continue
            st["extreme"] = max(st["extreme"], high) if side == "SELL" else min(st["extreme"], low)
    arms += [_arm(st, prices, stimes, tick, "DATA_END", None) for st in armed.values() if st["sweep_time"] is not None]
    arms.sort(key=lambda a: (a.sweep_time, a.broken_swing_time))
    return arms


def _arm(st: dict, prices, stimes, tick: float, end: str, end_time) -> Type3Arm:
    side, x, y = st["side"], st["x"], st["y"]
    trigger = prices[y] - tick if side == "SELL" else prices[y] + tick
    return Type3Arm(side, stimes[x], float(prices[x]), stimes[y], float(prices[y]), st["sweep_time"],
                    st["sweep_bar_extreme"], float(trigger), end, end_time, float(st["extreme"]), bool(st["latest"]))


def find_type3(bars: pd.DataFrame, swings: pd.DataFrame, *, max_reversal: pd.Timedelta, tick: float,
               bar_length: pd.Timedelta, latest_pair_only: bool = False) -> list[Type3]:
    """Completed type 3 shifts (BREAK) on one tier; see `track_type3`. The break must be on a later bar than the sweep
    (IMPL: OHLC has no intrabar order)."""
    return [Type3(a.direction, a.swept_swing_time, a.swept_price, a.broken_price, a.sweep_time, a.end_time,
                  a.extreme_before_end, a.trigger_price)
            for a in sorted((x for x in track_type3(bars, swings, max_reversal=max_reversal, tick=tick,
                                                    latest_pair_only=latest_pair_only) if x.end == "BREAK"),
                            key=lambda x: (x.end_time, x.broken_swing_time))]


def hilo(bars: pd.DataFrame, *, tick: float) -> pd.DataFrame:
    """HILO events per candle j (EP2-002, frame-confirmed).

    BUY  at j: high_j > high_{j-1} and (low_{j-1} < low_{j-2}  -> 'prior'
                                         or low_j < low_{j-1}     -> 'same', needs intrabar order check)
    SELL mirrors. trigger_price = previous candle's high + tick (BUY) / low - tick (SELL).
    """
    h, lo = bars["high"].to_numpy(), bars["low"].to_numpy()
    rows = []
    for j in range(2, len(bars)):
        for side in ("BUY", "SELL"):
            if side == "BUY":
                entry_break = h[j] > h[j - 1]
                prior_ok, same_ok = lo[j - 1] < lo[j - 2], lo[j] < lo[j - 1]
                trigger, stop_ref = h[j - 1] + tick, min(lo[j - 1], lo[j])
                break_size = (lo[j - 2] - lo[j - 1]) if prior_ok else (lo[j - 1] - lo[j])
            else:
                entry_break = lo[j] < lo[j - 1]
                prior_ok, same_ok = h[j - 1] > h[j - 2], h[j] > h[j - 1]
                trigger, stop_ref = lo[j - 1] - tick, max(h[j - 1], h[j])
                break_size = (h[j - 1] - h[j - 2]) if prior_ok else (h[j] - h[j - 1])
            if entry_break and (prior_ok or same_ok):
                rows.append({"time": bars.index[j], "direction": side, "kind": "prior" if prior_ok else "same",
                             "needs_intrabar_order": not prior_ok, "trigger_price": float(trigger),
                             "stop_ref": float(stop_ref), "break_size": float(break_size)})
    return pd.DataFrame(rows, columns=["time", "direction", "kind", "needs_intrabar_order", "trigger_price",
                                       "stop_ref", "break_size"])


def same_candle_order_ok(bars_5s: pd.DataFrame, candle_open: pd.Timestamp, candle_length: pd.Timedelta,
                         direction: str, first_level: float, second_level: float) -> bool | None:
    """For a 'same' HILO: did the first break (low for BUY, high for SELL) happen before the entry break?
    None when 5s data is missing or both breaks fall in the same 5s bar (order unknowable; lowers confidence)."""
    inside = bars_5s[(bars_5s.index >= candle_open) & (bars_5s.index < candle_open + candle_length)]
    if inside.empty:
        return None
    if direction == "BUY":
        first, second = inside.index[inside["low"] < first_level], inside.index[inside["high"] > second_level]
    else:
        first, second = inside.index[inside["high"] > first_level], inside.index[inside["low"] < second_level]
    if len(first) == 0 or len(second) == 0:
        return False
    if first[0] == second[0]:
        return None
    return bool(first[0] < second[0])


@dataclass(frozen=True)
class CandleSequence:
    minutes: int
    body_atr: float
    valid: bool                  # duration >= min_minutes
    low_volume: bool             # LVCS: mean body below threshold


def hvcs(bars_1m: pd.DataFrame, end_time: pd.Timestamp, direction: str, *, atr_1m: float, min_minutes: int,
         max_violations: int, lvcs_body_atr: float) -> CandleSequence:
    """Longest run of 1m candles ending at `end_time` moving in `direction` ('UP' / 'DOWN').
    DOWN: each candle's high <= previous high and closes bearish (mirror for UP). Up to `max_violations`
    candles in the run may break the rule, but the run must end on a conforming candle."""
    upto = bars_1m.loc[:end_time]
    o, h, lo, c = (upto[col].to_numpy() for col in ("open", "high", "low", "close"))
    n, violations, length = len(upto), 0, 0
    for i in range(n - 1, 0, -1):
        ok = (h[i] <= h[i - 1] and c[i] < o[i]) if direction == "DOWN" else (lo[i] >= lo[i - 1] and c[i] > o[i])
        if not ok:
            if length == 0:
                break
            violations += 1
            if violations > max_violations:
                break
        length += 1
    body = float(np.mean(np.abs(c[n - length:] - o[n - length:]))) if length else 0.0
    body_atr = body / atr_1m if atr_1m else 0.0
    return CandleSequence(length, body_atr, length >= min_minutes, body_atr < lvcs_body_atr)
