"""PC4 HVCS measurement (owner ruling D34 §2, change F-1). IMPLEMENTATION_FIX.

Additive module: `structure/shifts_pc3.py` is pinned by the frozen PC3 record and is **not** modified. The only
difference from PC3 is that the configured `hvcs.max_violations` tolerance is applied again, exactly as PC2's
`structure/shifts.py` applied it. The conformity test itself is PC3's (D29-10, H-1/H-2): structural respect only, the
candle's close direction is irrelevant, and the run may end on the bar that set the extension extreme.

The tolerance value is **not** a PC4 choice: it is `hvcs.max_violations = 1` in `config/strategy.yaml`, labelled
ASSUMPTION (OQ-08), which PC3's rewrite stopped passing without a ruling (D32 §5.2, D33 §2).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HvcsPC4:
    minutes: int
    body_atr: float
    valid: bool
    low_volume: bool
    indecision_bars: int
    violations: int                         # new diagnostic: how many tolerated breaks are inside the run
    invalidated: bool


def hvcs_structural_pc4(bars_1m: pd.DataFrame, end_time: pd.Timestamp, direction: str, *, atr_1m: float,
                        min_minutes: int, max_violations: int, lvcs_body_atr: float) -> HvcsPC4:
    """Longest run of 1m candles ending at `end_time` that respects its side, tolerating `max_violations` breaks.

    DOWN: a candle conforms while its high does not exceed the previous candle's high; UP mirrors on lows. The close
    direction is not required, so indecision and opposing-close candles sit inside the run (D29-10). A run may never
    **start** on a violation; a violating candle inside the run is counted, as PC2 counted it; the walk stops when the
    tolerance is exceeded.

    Only bars at or before `end_time` are read, so the verdict cannot change when later bars arrive.
    """
    upto = bars_1m.loc[:end_time]
    o, h, lo, c = (upto[col].to_numpy(dtype=float) for col in ("open", "high", "low", "close"))
    n = len(upto)
    length = indecision = violations = 0
    for i in range(n - 1, 0, -1):
        respects = (h[i] <= h[i - 1]) if direction == "DOWN" else (lo[i] >= lo[i - 1])
        if not respects:
            if length == 0:
                break                                   # the run may not start on a break
            violations += 1
            if violations > max_violations:
                violations -= 1                         # the candle that exceeded the tolerance is not in the run
                break
        progresses = (c[i] < o[i]) if direction == "DOWN" else (c[i] > o[i])
        indecision += 0 if progresses else 1
        length += 1
    body = float(np.mean(np.abs(c[n - length:] - o[n - length:]))) if length else 0.0
    body_atr = body / atr_1m if atr_1m else 0.0
    return HvcsPC4(length, body_atr, length >= min_minutes, body_atr < lvcs_body_atr, indecision, violations,
                   length == 0)
