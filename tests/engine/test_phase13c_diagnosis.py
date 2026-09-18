"""Diagnosis-tool tests (D32). Synthetic fixtures only, per the D32 §16 governance rule."""

from __future__ import annotations

import pandas as pd

from cbr.engine.phase13c_diagnosis import conforming_tolerant
from cbr.structure.shifts_pc3 import hvcs_structural


def bars(highs: list[float], lows: list[float]) -> pd.DataFrame:
    idx = pd.date_range("2025-01-01", periods=len(highs), freq="1min", tz="UTC")
    return pd.DataFrame({"open": highs, "high": highs, "low": lows, "close": lows}, index=idx)


def test_tolerance_extends_a_run_through_one_violation():
    # DOWN: highs 10, 9, 8, 9, 7, 6 — the 9 at index 3 breaks the run.
    b = bars([10, 9, 8, 9, 7, 6], [9, 8, 7, 8, 6, 5])
    end = b.index[-1]
    strict = hvcs_structural(b, end, "DOWN", atr_1m=1.0, min_minutes=4, lvcs_body_atr=0.3).minutes
    assert strict == 2                                        # 7 and 6 only: PC3 stops at the 9
    assert conforming_tolerant(b, end, "DOWN", 1) == 5        # one violation absorbed, run reaches the start
    assert conforming_tolerant(b, end, "DOWN", 0) == strict   # zero tolerance reproduces PC3 exactly


def test_two_violations_still_stop_a_one_tolerance_run():
    b = bars([10, 11, 8, 9, 7, 6], [9, 10, 7, 8, 6, 5])
    end = b.index[-1]
    # Backwards from the end: 6, 7 conform, the 9 is absorbed as the one allowed violation, the 8 conforms,
    # and the 11 is a second violation, which ends the run — the violating candle itself is counted, as in PC2.
    assert conforming_tolerant(b, end, "DOWN", 1) == 4


def test_up_direction_mirrors_on_lows():
    b = bars([5, 6, 7, 6, 8, 9], [4, 5, 6, 5, 7, 8])
    end = b.index[-1]
    assert hvcs_structural(b, end, "UP", atr_1m=1.0, min_minutes=4, lvcs_body_atr=0.3).minutes == 2
    assert conforming_tolerant(b, end, "UP", 1) == 5


def test_a_run_never_starts_on_a_violation():
    b = bars([10, 9, 8, 7, 6, 12], [9, 8, 7, 6, 5, 11])       # last candle breaks the side
    assert conforming_tolerant(b, b.index[-1], "DOWN", 1) == 0
