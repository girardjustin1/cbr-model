"""D38 §31: a hand-computed execution example the simulator must reproduce exactly.

Every number below is calculated by hand first, then asserted. Nothing here is copied from simulator output.

SIGNAL (LONG)
    trigger price        2000.00
    structure anchor     1996.00
    buffer               stop.buffer_atr 0.1 x ATR(1m,14) 2.00 = 0.20
    spread policy        ADD_SPREAD_AT_FILL
    target               2006.00
    activation           10:00:00

QUOTES (ticks, five seconds apart)
    10:00:00   bid 1999.50 / ask 1999.70    ask < 2000.00, no trigger
    10:00:05   bid 2000.20 / ask 2000.40    ask >= 2000.00  -> TRIGGER, fill on the ask
    10:00:10   bid 2003.00 / ask 2003.20    between the levels
    10:00:15   bid 2006.10 / ask 2006.30    bid >= 2006.00  -> TARGET

HAND CALCULATION
    fill price       = 2000.40                       (the ask that triggered, not the trigger price)
    entry gap        = 2000.40 - 2000.00 = 0.40
    spread at fill   = 2000.40 - 2000.20 = 0.20
    final stop       = 1996.00 - 0.20 - 0.20 = 1995.60
    initial risk     = 2000.40 - 1995.60 = 4.80
    exit price       = 2006.00                       (limit exit AT the target; the 2006.10 bid is not awarded)
    gross R          = (2006.00 - 2000.40) / 4.80 = 5.60 / 4.80 = 7/6 = 1.1666666666666667
    net R            = gross R                       (additional slippage 0, commission 0, spread not double-counted)
"""

from __future__ import annotations

from fractions import Fraction

import pandas as pd
import pytest

from cbr.execution import ledger
from cbr.execution.simulate import ExecutionParams, simulate
from tests.execution.test_simulator import quotes, signal

T = pd.Timestamp("2030-03-12 10:00:00", tz="UTC")
HAND_GROSS_R = float(Fraction(56, 10) / Fraction(48, 10))       # 5.60 / 4.80, computed as an exact fraction


def test_simulator_reproduces_the_hand_calculation():
    q = quotes([(1999.50, 1999.70), (2000.20, 2000.40), (2003.00, 2003.20), (2006.10, 2006.30)], start=T)
    sig = signal(trigger=2000.00, target=2006.00, anchor=1996.00, buffer_atr=0.1, atr=2.0, activation=T)
    records = simulate([sig], q, params=ExecutionParams())
    assert len(records) == 1
    r = records[0]

    assert r.execution_status == ledger.CLOSED
    assert r.exit_reason == ledger.TARGET
    assert r.fill_time == str(T + pd.Timedelta(seconds=5))
    assert r.fill_price == pytest.approx(2000.40)
    assert r.entry_gap == pytest.approx(0.40)
    assert r.fill_spread == pytest.approx(0.20)
    assert r.stop_buffer == pytest.approx(0.20)
    assert r.fill_time_stop_anchor == pytest.approx(1996.00)
    assert r.final_execution_stop == pytest.approx(1995.60)
    assert r.initial_risk == pytest.approx(4.80)
    assert r.exit_time == str(T + pd.Timedelta(seconds=15))
    assert r.exit_price == pytest.approx(2006.00)
    assert r.gross_r == pytest.approx(HAND_GROSS_R)
    assert r.gross_r == pytest.approx(1.1666666666666667)
    assert r.net_r == pytest.approx(r.gross_r)
