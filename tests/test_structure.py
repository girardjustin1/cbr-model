"""Unit tests for CBR_PRIMITIVES_V1 building blocks on synthetic bars with known answers."""

from datetime import time
from itertools import pairwise

import numpy as np
import pandas as pd
import pytest

from cbr.structure.condition import RANGE, TREND, TRENDING_RANGE, UNDEFINED, classify
from cbr.structure.indicators import atr
from cbr.structure.levels import aoi_tap, candle_close_levels, in_rollover, in_sydney_session
from cbr.structure.overextension import evaluate
from cbr.structure.shifts import find_type3, hilo, hvcs, same_candle_order_ok
from cbr.structure.swings import legs, usable, zigzag

M1 = pd.Timedelta(minutes=1)
T0 = pd.Timestamp("2025-11-10 01:00", tz="UTC")


def bars(ohlc, start=T0, step=M1):
    idx = pd.date_range(start, periods=len(ohlc), freq=step)
    return pd.DataFrame(ohlc, columns=["open", "high", "low", "close"], index=idx, dtype=float)


def path(prices, start=T0):
    """Bars that move from one price to the next: open=prev, close=next, high/low = extremes."""
    rows = [(a, max(a, b), min(a, b), b) for a, b in pairwise(prices)]
    return bars(rows, start)


# ---------- ATR ----------

def test_atr_wilder_first_value_and_recursion():
    b = bars([(10, 12, 9, 11), (11, 13, 10, 12), (12, 12, 8, 9), (9, 15, 9, 14)])
    a = atr(b, 3)
    assert np.isnan(a.iloc[0]) and np.isnan(a.iloc[1])
    assert a.iloc[2] == pytest.approx((3 + 3 + 4) / 3)           # TR: 3, max(3,2,1)=3, max(4,0,4)=4
    assert a.iloc[3] == pytest.approx((a.iloc[2] * 2 + 6) / 3)   # TR bar3 = max(6, 6, 0) = 6


# ---------- swings ----------

ZIG = [100 + i for i in range(11)] + [110 - i for i in range(1, 11)] + [100 + i for i in range(1, 9)]


def test_zigzag_confirms_swings_after_threshold():
    b = path(ZIG)
    s = zigzag(b, pd.Series(1.0, index=b.index), k=3, bar_length=M1)
    assert list(s["kind"]) == ["L", "H", "L"]
    assert list(s["price"]) == [100, 110, 100]
    # swing high at 110 (bar 9 closes at 110) confirmed when a bar's low is <= 107: bar 12 (opens 108, low 107)
    assert s.iloc[1]["time"] == b.index[9]
    assert s.iloc[1]["confirmed_at"] == b.index[12] + M1


def test_zigzag_is_causal():
    b = path(ZIG)
    a = pd.Series(1.0, index=b.index)
    full = zigzag(b, a, k=3, bar_length=M1)
    for i in range(len(b)):
        as_of = b.index[i] + M1
        partial = zigzag(b.iloc[: i + 1], a.iloc[: i + 1], k=3, bar_length=M1)
        pd.testing.assert_frame_equal(partial.reset_index(drop=True), usable(full, as_of).reset_index(drop=True))


def test_legs_sizes_and_directions():
    b = path(ZIG)
    lg = legs(zigzag(b, pd.Series(1.0, index=b.index), k=3, bar_length=M1))
    assert list(lg["size"]) == [10, 10] and list(lg["dir"]) == [1, -1]


# ---------- condition ----------

def swings_from_sizes(sizes, start_price=100.0):
    rows, price, t = [], start_price, T0
    kinds = ["L", "H"]
    rows.append((kinds[0], price, t, t + M1))
    for i, size in enumerate(sizes):
        price = price + size if i % 2 == 0 else price - size
        t = t + pd.Timedelta(minutes=30)
        rows.append((kinds[(i + 1) % 2], price, t, t + M1))
    return pd.DataFrame(rows, columns=["kind", "price", "time", "confirmed_at"])


@pytest.mark.parametrize(("sizes", "expected"), [
    ([10, 8, 9, 7], RANGE),              # corrections 0.8, 1.125, 0.78 -> median 0.8
    ([10, 6, 10, 6], TRENDING_RANGE),    # 0.6, 1.67, 0.6 -> 0.6
    ([10, 3, 10, 3], TREND),             # 0.3, capped 2.0, 0.3 -> 0.3
    ([10, 8], UNDEFINED),                # fewer than 3 legs
])
def test_condition_thresholds(sizes, expected):
    sw = swings_from_sizes(sizes)
    as_of = sw["confirmed_at"].max() + M1
    b1 = bars([(100, 100, 100, 100)], start=T0)
    c = classify(sw, b1, as_of, pd.Timedelta(hours=8), min_legs=3, range_min=0.75, trend_max=0.5,
                 correction_cap=2.0)
    assert c.condition == expected


def test_condition_ignores_swings_not_yet_confirmed():
    sw = swings_from_sizes([10, 8, 9, 7])
    as_of = sw.iloc[2]["confirmed_at"]          # swings 0-2 known -> 2 legs; later swings not yet confirmed
    c = classify(sw, bars([(100, 100, 100, 100)]), as_of, pd.Timedelta(hours=8), min_legs=3, range_min=0.75,
                 trend_max=0.5, correction_cap=2.0)
    assert c.condition == UNDEFINED and c.n_legs == 2


# ---------- overextension ----------

def push_up(n=25, dip=0.3, start=100.0):
    rows, prev_high = [], start
    for i in range(n):
        o = start + i
        rows.append((o, o + 1, max(start, prev_high - dip) if i else start, o + 1))
        prev_high = o + 1
    return bars(rows)


def test_oe_clean_push():
    b = push_up()
    oe = evaluate(b, T0, 100.0, T0 + pd.Timedelta(minutes=26), atr_1m=1.0, activation_atr=0.5,
                  pullback_frac=0.5, two_sided_frac=0.5, prev_candle_high=110.0)
    assert oe.direction == "UP" and oe.extreme == 125
    assert oe.duration_min == 24 and oe.no_pullback and not oe.two_sided and oe.prev_candle_break


def test_oe_detects_50pct_pullback():
    b = push_up()
    b.iloc[12, b.columns.get_loc("low")] = 104.0      # running high 112 (+12), dips to 104 = 8 >= 6
    oe = evaluate(b, T0, 100.0, T0 + pd.Timedelta(minutes=26), atr_1m=1.0, activation_atr=0.5,
                  pullback_frac=0.5, two_sided_frac=0.5)
    assert not oe.no_pullback


def test_oe_uses_only_closed_bars():
    b = push_up()
    oe = evaluate(b, T0, 100.0, T0 + pd.Timedelta(minutes=10), atr_1m=1.0, activation_atr=0.5,
                  pullback_frac=0.5, two_sided_frac=0.5)
    assert oe.extreme == 110 and oe.duration_min == 9


# ---------- type 3 ----------

def t3_setup():
    # bullish structure: swing high 110 (01:00), then higher low 100 (01:10), both confirmed by 01:15.
    # SELL type 3 (EP1-008): take out the high 110, then break the low 100 that formed after it.
    sw = pd.DataFrame([("H", 110.0, T0, T0 + pd.Timedelta(minutes=5)),
                       ("L", 100.0, T0 + pd.Timedelta(minutes=10), T0 + pd.Timedelta(minutes=15))],
                      columns=["kind", "price", "time", "confirmed_at"])
    start = T0 + pd.Timedelta(minutes=15)
    rows = [(108, 109, 107, 108), (108, 111, 107, 110),          # sweep of 110 at 01:16
            (110, 110, 104, 105), (105, 106, 99.5, 100)]         # break of 100 at 01:18
    return sw, bars(rows, start=start)


def test_type3_buy_matches_course_example_structure():
    # CX-LT1-1 shape (5s swings, 2025-10-21): low 4335.21, lower high 4340.18, sweep to 4332.95, break 4340.18.
    s5 = pd.Timedelta(seconds=5)
    t = T0
    sw = pd.DataFrame([("L", 4335.21, t, t + 7 * s5), ("H", 4340.18, t + 7 * s5, t + 11 * s5),
                       ("L", 4332.95, t + 14 * s5, t + 17 * s5)],        # the sweep low gets confirmed first
                      columns=["kind", "price", "time", "confirmed_at"])
    rows = ([(4338, 4338.5, 4337.5, 4338)] * 12 + [(4338, 4338, 4334, 4334.5), (4334.5, 4335, 4332.95, 4334)]
            + [(4334, 4336, 4333.8, 4336)] * 3 + [(4336, 4340.5, 4336, 4340.3)])
    b = bars(rows, start=t, step=s5)
    ev = [e for e in find_type3(b, sw, max_reversal=pd.Timedelta(minutes=3), tick=0.01, bar_length=s5)
          if e.direction == "BUY"]
    assert len(ev) == 1
    assert ev[0].swept_price == 4335.21 and ev[0].broken_price == 4340.18
    assert ev[0].trigger_price == pytest.approx(4340.19) and ev[0].sweep_extreme == pytest.approx(4332.95)


def test_type3_sell_detected():
    sw, b = t3_setup()
    ev = find_type3(b, sw, max_reversal=pd.Timedelta(minutes=15), tick=0.01, bar_length=M1)
    sells = [e for e in ev if e.direction == "SELL"]
    assert len(sells) == 1
    e = sells[0]
    assert e.sweep_time == b.index[1] and e.break_time == b.index[3]
    assert e.sweep_extreme == 111 and e.trigger_price == pytest.approx(99.99)


def test_type3_rejects_slow_reversal():
    sw, b = t3_setup()
    ev = find_type3(b, sw, max_reversal=pd.Timedelta(minutes=1), tick=0.01, bar_length=M1)
    assert not [e for e in ev if e.direction == "SELL"]


def test_type3_rejects_when_new_swing_low_forms_first():
    sw, b = t3_setup()
    sw = pd.concat([sw, pd.DataFrame([("H", 111.0, b.index[1], b.index[1] + M1),
                                      ("L", 104.0, b.index[2], b.index[2] + M1)], columns=sw.columns)],
                   ignore_index=True)
    ev = find_type3(b, sw, max_reversal=pd.Timedelta(minutes=15), tick=0.01, bar_length=M1)
    assert not [e for e in ev if e.direction == "SELL" and e.broken_price == 100.0]


def test_type3_is_causal():
    sw, b = t3_setup()
    full = find_type3(b, sw, max_reversal=pd.Timedelta(minutes=15), tick=0.01, bar_length=M1)
    for i in range(len(b)):
        partial = find_type3(b.iloc[: i + 1], sw, max_reversal=pd.Timedelta(minutes=15), tick=0.01, bar_length=M1)
        assert partial == [e for e in full if e.break_time <= b.index[i]]


# ---------- HILO ----------

def test_hilo_buy_prior_candle_broke_low():
    b = bars([(105, 106, 104, 105), (105, 105.5, 103, 104), (104, 106, 103.5, 105.8)])
    ev = hilo(b, tick=0.01)
    buy = ev[ev["direction"] == "BUY"].iloc[0]
    assert buy["time"] == b.index[2] and buy["kind"] == "prior" and not buy["needs_intrabar_order"]
    assert buy["trigger_price"] == pytest.approx(105.51)


def test_hilo_rejects_plain_pullback():
    # candle 1 does NOT break candle 0's low, candle 2 does not break candle 1's low: just a pullback
    b = bars([(105, 106, 104, 105), (105, 105.5, 104.5, 105), (105, 106, 104.8, 105.8)])
    assert hilo(b, tick=0.01).query("direction == 'BUY'").empty


def test_hilo_same_candle_requires_intrabar_order():
    b = bars([(105, 106, 104, 105), (105, 105.5, 104.5, 105), (105, 106, 104.0, 105.8)])
    buy = hilo(b, tick=0.01).query("direction == 'BUY'").iloc[0]
    assert buy["kind"] == "same" and buy["needs_intrabar_order"]
    s5 = pd.Timedelta(seconds=5)
    low_first = bars([(105, 105, 104.2, 104.3)] + [(104.3, 104.6, 104.2, 104.5)] * 5 + [(104.5, 105.9, 104.5, 105.8)],
                     start=b.index[2], step=s5)
    assert same_candle_order_ok(low_first, b.index[2], M1, "BUY", 104.5, 105.5) is True
    high_first = bars([(105, 105.9, 105, 105.8)] + [(105.8, 105.8, 104.2, 104.3)], start=b.index[2], step=s5)
    assert same_candle_order_ok(high_first, b.index[2], M1, "BUY", 104.5, 105.5) is False


# ---------- HVCS ----------

def test_hvcs_counts_bearish_lower_high_run():
    rows = [(100, 101, 99, 100.5)] + [(100 - i, 100 - i, 99 - i, 99.2 - i) for i in range(5)]
    b = bars(rows)
    seq = hvcs(b, b.index[-1], "DOWN", atr_1m=1.0, min_minutes=4, max_violations=0, lvcs_body_atr=0.3)
    assert seq.minutes == 5 and seq.valid and not seq.low_volume


# ---------- levels & windows ----------

def test_levels_form_on_close_direction_flip():
    h1 = pd.Timedelta(hours=1)
    c = bars([(100, 101, 99, 101), (101, 102, 99, 100), (100, 101, 98, 99), (99, 102, 98, 101)], step=h1)
    lv = candle_close_levels(c, h1)
    assert list(lv["price"]) == [101, 99]
    assert lv.iloc[0]["formed_at"] == c.index[1] + h1
    assert aoi_tap(lv, 101.2, c.index[3] + h1, zone=0.5, lookback=pd.Timedelta(hours=24))
    assert not aoi_tap(lv, 101.2, c.index[1], zone=0.5, lookback=pd.Timedelta(hours=24))   # not formed yet


@pytest.mark.parametrize(("ts", "sydney", "rollover"), [
    ("2026-01-15 23:30", True, False),     # EST: 18:30 NY
    ("2026-01-15 22:30", False, True),     # EST: 17:30 NY -> rollover window (post 60)
    ("2026-01-16 00:30", False, False),    # Tokyo open passed
    ("2026-07-15 22:30", True, False),     # EDT: 18:30 NY
    ("2026-07-15 21:10", False, True),     # EDT: 17:10 NY
    ("2026-07-16 01:30", False, False),    # Asia hour 2
])
def test_no_trade_windows_are_dst_aware(ts, sydney, rollover):
    t = pd.Timestamp(ts, tz="UTC")
    assert in_sydney_session(t) is sydney
    assert in_rollover(t, pre_min=15, post_min=60, rollover=time(17, 0)) is rollover
