"""PC3 overextension: PRE_EXTENSION / EXTENSION_ACTIVE states and the whole-extension pullback test.

Additive module; PC2's `structure/overextension.py` is pinned and unmodified. Owner rulings D29 §5-§9.

  * STATES (D29-5). At the hour open the candle is `PRE_EXTENSION`: movements set context and extremes but can never
    fail the 50% pullback rule. `EXTENSION_ACTIVE` starts at the first qualifying directional push.
  * EARLIEST ACTIVATION (D29-5). Minute `earliest_activation_min` (7) — an ASSUMPTION implementing the Level-1 guidance
    that the overextension can begin about 7-15 minutes into the hour. It is the earliest permitted transition, never a
    required one, and there is no expiry.
  * QUALIFIER Q1 (D29-6). Activation is the first closed 1m bar at or after that minute whose extreme trades beyond the
    relevant extreme of the immediately previous completed 15m candle, in the extension direction.
  * ORIGIN (ASSUMPTION). The active extension is measured from the most adverse price reached between the hour open and
    activation: the base the qualifying push started from. The hour open stays the canonical hourly reference (D8) and
    is used for stops and targets, not here.
  * PULLBACK (D29-8, CANON_CORRECTION). The deepest opposing retracement before the running extreme, compared with the
    magnitude of the active extension **known at the evaluation time**. No permanent early latch.
  * NO LOOKAHEAD (D29-9). Every field is computed from bars closed at `as_of` only.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

ONE_MINUTE = pd.Timedelta(minutes=1)
PRE_EXTENSION, EXTENSION_ACTIVE = "PRE_EXTENSION", "EXTENSION_ACTIVE"


@dataclass(frozen=True)
class ExtensionPC3:
    state: str                              # PRE_EXTENSION / EXTENSION_ACTIVE
    direction: str                          # UP / DOWN / NONE (provisional while PRE_EXTENSION)
    extreme: float | None                   # running extension extreme known at as_of
    extreme_time: pd.Timestamp | None
    size: float                             # |extreme - origin| of the ACTIVE extension (0 while pre-extension)
    duration_min: float                     # minutes from activation to the extreme (0 while pre-extension, never negative)
    no_pullback: bool                       # deepest retracement < pullback_frac x size (True while pre-extension)
    deepest_retracement: float
    retracement_ratio: float | None
    two_sided: bool
    opposite_wick: float
    pre_extension_start: pd.Timestamp
    activation_time: pd.Timestamp | None
    activation_price: float | None
    activation_reason: str | None
    previous_15m_reference: float | None
    origin_price: float | None
    origin_time: pd.Timestamp | None
    extreme_before_activation: bool         # the running extreme predates activation: the push has not extended since
    extreme_path: list                      # [[bar close time, extreme], ...] of the active extension


def evaluate_pc3(bars_1m: pd.DataFrame, candle_open_time: pd.Timestamp, candle_open: float, as_of: pd.Timestamp, *,
                 pullback_frac: float, two_sided_frac: float, earliest_activation_min: int,
                 prev_candle_high: float | None, prev_candle_low: float | None) -> ExtensionPC3:
    """State of the hourly candle at `as_of`, from 1m bars closed by then."""
    inside = bars_1m[(bars_1m.index >= candle_open_time) & (bars_1m.index + ONE_MINUTE <= as_of)]
    base = ExtensionPC3(PRE_EXTENSION, "NONE", None, None, 0.0, 0.0, True, 0.0, None, False, 0.0,
                        candle_open_time, None, None, None, None, None, None, False, [])
    if inside.empty:
        return base
    up = float(inside["high"].max()) - candle_open
    down = candle_open - float(inside["low"].min())
    direction = "UP" if up >= down else "DOWN"
    sign = 1 if direction == "UP" else -1
    favour = inside["high"] if direction == "UP" else inside["low"]
    against = inside["low"] if direction == "UP" else inside["high"]
    ref = prev_candle_high if direction == "UP" else prev_candle_low
    earliest = candle_open_time + pd.Timedelta(minutes=earliest_activation_min)

    activation_time = activation_price = None
    if ref is not None:
        eligible = inside[inside.index >= earliest]
        beyond = eligible[(eligible["high"] > ref) if direction == "UP" else (eligible["low"] < ref)]
        if len(beyond):
            activation_time = beyond.index[0]
            activation_price = float(beyond["high"].iloc[0] if direction == "UP" else beyond["low"].iloc[0])
    if activation_time is None:
        return ExtensionPC3(PRE_EXTENSION, direction, None, None, 0.0, 0.0, True, 0.0, None, False, 0.0,
                            candle_open_time, None, None, None, ref, None, None, False, [])

    before = inside[inside.index <= activation_time]
    origin_time = against.loc[before.index].idxmin() if sign == 1 else against.loc[before.index].idxmax()
    origin_price = float(against.loc[origin_time])                      # most adverse price before activation

    active = inside[inside.index >= origin_time]
    extreme_time = favour.loc[active.index].idxmax() if sign == 1 else favour.loc[active.index].idxmin()
    extreme = float(favour.loc[extreme_time])
    size = abs(extreme - origin_price)

    to_extreme = active.loc[:extreme_time]
    running = to_extreme["high"].cummax() if sign == 1 else to_extreme["low"].cummin()
    # The retracement of a bar is measured against the extreme reached BEFORE it: OHLC carries no intrabar order, so a
    # single wide bar must not count as its own retracement (same IMPL rule as PC2's overextension).
    prior = running.shift(1).fillna(origin_price)
    retr = (prior - to_extreme["low"]) if sign == 1 else (to_extreme["high"] - prior)
    deepest = float(max(retr.max(), 0.0)) if len(retr) else 0.0
    ratio = (deepest / size) if size else None
    path = [[t + ONE_MINUTE, float(v)] for t, v in running.items()
            if t == running.index[0] or v != running.loc[:t].iloc[-2]]

    opposite = max(sign * (origin_price - float(against.loc[to_extreme.index].min() if sign == 1
                                                else against.loc[to_extreme.index].max())), 0.0)
    early = extreme_time < activation_time          # the extreme predates activation: no extension since activation
    return ExtensionPC3(
        EXTENSION_ACTIVE, direction, extreme, extreme_time, size,
        max((extreme_time - activation_time) / ONE_MINUTE, 0.0),
        deepest < pullback_frac * size if size else True, deepest, ratio,
        size > 0 and opposite >= two_sided_frac * size, opposite / size if size else 0.0,
        candle_open_time, activation_time, activation_price,
        f"took the previous 15m {'high' if direction == 'UP' else 'low'} {ref} at or after minute {earliest_activation_min}",
        ref, origin_price, origin_time, early, path)
