"""PC3 structure primitives: re-anchored type 3 and structural HVCS (owner rulings D29 §1, §4, §10).

Additive module: PC2's `structure/shifts.py` is pinned by the frozen PC2 records and is **not** modified. Everything
here is causal — a bar is read only after it closes, a swing only at its `confirmed_at`.

Differences from PC2 (`track_type3`):
  * TRIGGER RE-ANCHORING (D29-1, CANON_CORRECTION). The trigger is the most recently confirmed opposing swing available
    causally. A newly confirmed opposing swing re-anchors the trigger; it never disarms the pattern.
  * REVERSAL TIMER (D29-4). `max_reversal` runs from the latest update of the sweep extreme: while price keeps making
    new sweep-direction extremes the reversal has not begun, so each new extreme resets the timer.
  * DIAGNOSTICS. `first_sweep_time`, `latest_sweep_extreme_time`, `trigger_confirmation_time`, `trigger_break_time`.

HVCS (D29 §10, §11): a candle conforms on structural respect and directional progression; its close direction is not
required, indecision candles are allowed and no maximum count is imposed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Type3ArmPC3:
    """One sweep run and how it ended. `broken_price` is the trigger in force when the run ended."""

    direction: str                          # SELL (bearish shift) / BUY (bullish shift)
    swept_price: float                      # the confirmed swing taken out in the sweep direction
    swept_swing_time: pd.Timestamp
    first_sweep_time: pd.Timestamp          # open time of the first bar beyond the swept swing
    latest_sweep_extreme_time: pd.Timestamp  # open time of the bar that last extended the sweep
    sweep_bar_extreme: float                 # most extreme price reached by the sweep run
    broken_price: float                     # opposing swing the trigger sits at
    broken_swing_time: pd.Timestamp
    trigger_confirmation_time: pd.Timestamp  # when that opposing swing became usable
    trigger_price: float
    end: str                                # BREAK / TIMEOUT / DATA_END
    end_time: pd.Timestamp | None
    trigger_break_time: pd.Timestamp | None
    reanchored: int                         # how many times the trigger moved while the run was live
    trigger_history: tuple                  # ((usable_from, trigger_price), ...): the trigger in force at any time

    def trigger_at(self, as_of: pd.Timestamp) -> float | None:
        """The trigger in force at `as_of` — what a causal reader knew then, not the final one."""
        live = [px for t, px in self.trigger_history if t <= as_of]
        return live[-1] if live else None


def track_type3_pc3(bars: pd.DataFrame, swings: pd.DataFrame, *, max_reversal: pd.Timedelta,
                    tick: float) -> list[Type3ArmPC3]:
    """Every re-anchored type-3 sweep on one tier, in order (D29 §1).

    A run in direction `d` starts when a bar's extreme goes beyond the most recent confirmed swing of the sweep kind
    (high for SELL, low for BUY) while an opposing confirmed swing exists. While the run is live the trigger is the most
    recently confirmed opposing swing, one tick beyond it. The run ends on the first later bar that breaks the trigger
    (BREAK), or when `max_reversal` has elapsed since the latest sweep-extreme update (TIMEOUT).
    """
    kinds = swings["kind"].to_numpy()
    prices = swings["price"].to_numpy(dtype=float)
    stimes = list(swings["time"])
    ctimes = list(swings["confirmed_at"])
    confirmed = pd.DatetimeIndex(swings["confirmed_at"]).as_unit("ns").asi8
    n, ptr = len(swings), 0
    live: dict[str, dict] = {}
    out: list[Type3ArmPC3] = []
    bar_ns = bars.index.as_unit("ns").asi8
    for t, t64, high, low in zip(bars.index, bar_ns, bars["high"].to_numpy(), bars["low"].to_numpy(), strict=True):
        while ptr < n and confirmed[ptr] <= t64:                 # swings become usable at their confirmation
            i, ptr = ptr, ptr + 1
            for d, opposing in (("SELL", "L"), ("BUY", "H")):
                st = live.get(d)
                if st is not None and kinds[i] == opposing and stimes[i] >= st["first_sweep_time"]:
                    new_trigger = float(prices[i]) - tick if d == "SELL" else float(prices[i]) + tick
                    st.update(broken_price=float(prices[i]), broken_swing_time=stimes[i],
                              trigger_confirmation_time=ctimes[i], trigger=new_trigger,
                              reanchored=st["reanchored"] + 1)
                    st["history"].append((ctimes[i], new_trigger))
        last: dict[str, int | None] = {"H": None, "L": None}
        for i in range(ptr):
            last[str(kinds[i])] = i
        for d, sweep_kind, opposing in (("SELL", "H", "L"), ("BUY", "L", "H")):
            si, oi = last[sweep_kind], last[opposing]
            st = live.get(d)
            beyond = si is not None and (high > prices[si] if d == "SELL" else low < prices[si])
            if st is None and beyond and oi is not None:
                live[d] = {"swept_price": float(prices[si]), "swept_swing_time": stimes[si], "first_sweep_time": t,
                           "latest_sweep_extreme_time": t, "extreme": float(high if d == "SELL" else low),
                           "broken_price": float(prices[oi]), "broken_swing_time": stimes[oi],
                           "trigger_confirmation_time": ctimes[oi],
                           "trigger": float(prices[oi]) - tick if d == "SELL" else float(prices[oi]) + tick,
                           "reanchored": 0,
                           "history": [(ctimes[oi], float(prices[oi]) - tick if d == "SELL"
                                        else float(prices[oi]) + tick)]}
            elif st is not None:
                extended = (high > st["extreme"]) if d == "SELL" else (low < st["extreme"])
                if extended:                                      # a new sweep extreme restarts the reversal timer
                    st["extreme"] = float(high if d == "SELL" else low)
                    st["latest_sweep_extreme_time"] = t
        for d in ("SELL", "BUY"):
            st = live.get(d)
            if st is None:
                continue
            if t - st["latest_sweep_extreme_time"] > max_reversal:
                out.append(_arm(d, st, "TIMEOUT", t, None))
                del live[d]
                continue
            broke = (low < st["trigger"]) if d == "SELL" else (high > st["trigger"])
            if broke and t > st["first_sweep_time"]:
                out.append(_arm(d, st, "BREAK", t, t))
                del live[d]
    for d, st in live.items():
        out.append(_arm(d, st, "DATA_END", None, None))
    out.sort(key=lambda a: (a.first_sweep_time, a.direction))
    return out


def _arm(direction: str, st: dict, end: str, end_time, break_time) -> Type3ArmPC3:
    return Type3ArmPC3(direction, st["swept_price"], st["swept_swing_time"], st["first_sweep_time"],
                       st["latest_sweep_extreme_time"], st["extreme"], st["broken_price"], st["broken_swing_time"],
                       st["trigger_confirmation_time"], st["trigger"], end, end_time, break_time, st["reanchored"],
                       tuple(st["history"]))


@dataclass(frozen=True)
class HvcsPC3:
    minutes: int
    body_atr: float
    valid: bool
    low_volume: bool
    indecision_bars: int
    invalidated: bool


def hvcs_structural(bars_1m: pd.DataFrame, end_time: pd.Timestamp, direction: str, *, atr_1m: float,
                    min_minutes: int, lvcs_body_atr: float) -> HvcsPC3:
    """Longest run of 1m candles ending at `end_time` that respects its side and progresses (D29 §10).

    DOWN: a candle conforms while its high does not exceed the previous candle's high. UP: while its low does not fall
    below the previous candle's low. The candle's close direction is **not** required (PC2 required `close < open`), so
    indecision candles sit inside the run and the run may end on the bar that set the extension extreme. The run stops
    at the first candle that breaks the respected side (structural invalidation). No maximum count is imposed.
    """
    upto = bars_1m.loc[:end_time]
    o, h, lo, c = (upto[col].to_numpy(dtype=float) for col in ("open", "high", "low", "close"))
    n = len(upto)
    length, indecision = 0, 0
    for i in range(n - 1, 0, -1):
        respects = (h[i] <= h[i - 1]) if direction == "DOWN" else (lo[i] >= lo[i - 1])
        if not respects:
            break
        progresses = (c[i] < o[i]) if direction == "DOWN" else (c[i] > o[i])
        indecision += 0 if progresses else 1
        length += 1
    body = float(np.mean(np.abs(c[n - length:] - o[n - length:]))) if length else 0.0
    body_atr = body / atr_1m if atr_1m else 0.0
    return HvcsPC3(length, body_atr, length >= min_minutes, body_atr < lvcs_body_atr, indecision, length == 0)
