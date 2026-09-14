"""Type 3 shifts, HILO and HVCS: CBR_PRIMITIVES_V1 §4.

Type 3 (EP1-008, EP1-009): take out a swing high, immediately reverse, take out the swing low before it (sell);
mirror for buy. HILO (EP2-001…003, frame-confirmed). HVCS structure (EP2-005), duration (E1H-034).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cbr.structure.swings import usable


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


def find_type3(bars: pd.DataFrame, swings: pd.DataFrame, *, max_reversal: pd.Timedelta, tick: float,
               bar_length: pd.Timedelta) -> list[Type3]:
    """All type 3 events on one tier (EP1-008): with the last two confirmed swings X then Y,
      X = swing high, Y = the higher/lower low after it  -> SELL: take out X, then break Y
      X = swing low,  Y = the high after it              -> BUY:  take out X, then break Y
    The swing to break is the one formed AFTER the swept swing. A pattern is armed once Y is confirmed, stays
    armed through later confirmations of X's kind (the sweep itself confirms a new extreme), and ends on the
    break, on timeout after the sweep, or when a new swing of Y's kind is confirmed after the sweep.
    Uses only swings confirmed at or before each bar's open; the break must be on a later bar than the sweep
    (IMPL: OHLC has no intrabar order)."""
    events: list[Type3] = []
    armed: dict[tuple, dict] = {}
    seen_pairs: set[tuple] = set()
    for t, high, low in zip(bars.index, bars["high"], bars["low"], strict=True):
        known = usable(swings, t)
        if len(known) >= 2:
            x, y = known.iloc[-2], known.iloc[-1]
            if x["kind"] != y["kind"]:
                key = (x["time"], y["time"])
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    side = "SELL" if x["kind"] == "H" else "BUY"
                    armed[key] = {"side": side, "swept": x, "broken": y, "sweep_time": None, "extreme": None}
        for key, st in list(armed.items()):
            side, swept, broken = st["side"], st["swept"], st["broken"]
            if st["sweep_time"] is None:
                if (high > swept["price"]) if side == "SELL" else (low < swept["price"]):
                    st["sweep_time"], st["extreme"] = t, (high if side == "SELL" else low)
                continue
            if t - st["sweep_time"] > max_reversal:
                del armed[key]
                continue
            new_same_as_broken = known[(known["kind"] == broken["kind"]) & (known["time"] > broken["time"])
                                       & (known["confirmed_at"] > st["sweep_time"])]
            if not new_same_as_broken.empty:     # structure moved on before the break: not an immediate reversal
                del armed[key]
                continue
            if (low < broken["price"]) if side == "SELL" else (high > broken["price"]):
                trigger = broken["price"] - tick if side == "SELL" else broken["price"] + tick
                events.append(Type3(side, swept["time"], float(swept["price"]), float(broken["price"]),
                                    st["sweep_time"], t, float(st["extreme"]), float(trigger)))
                del armed[key]
                continue
            st["extreme"] = max(st["extreme"], high) if side == "SELL" else min(st["extreme"], low)
    return events


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
