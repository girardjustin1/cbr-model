"""Data-quality detectors (owner ruling D12): DXY CFD missing while DX active; artificial candle extrema."""

import pandas as pd
import pytest

from cbr.data import dukascopy_fetch as dk
from cbr.data import quality as q

CFG = {"dxy_cfd_missing_while_dx_active": {"min_missing_run_minutes": 30, "min_dx_active_minutes": 15},
       "candle_extrema": {"suspect_ratio": 3.0}}
START = pd.Timestamp("2020-03-09 18:00", tz="UTC")


def _dx(active_minutes: pd.DatetimeIndex, span_end: pd.Timestamp) -> pd.DataFrame:
    idx = pd.date_range(START, span_end, freq="1min", inclusive="left")
    return pd.DataFrame({"volume": [20.0 if t in active_minutes else 0.0 for t in idx]}, index=idx)


def test_flags_cfd_hole_while_dx_trades_and_reports_active_span():
    end = START + pd.Timedelta(hours=4)
    all_minutes = pd.date_range(START, end, freq="1min", inclusive="left")
    hole = pd.date_range("2020-03-09 20:00", "2020-03-09 21:00", freq="1min", inclusive="left", tz="UTC")
    cfd = all_minutes.difference(hole)
    dx = _dx(hole[5:45], end)
    [r] = q.dxy_cfd_missing_while_dx_active(cfd, dx, START, end, CFG)
    assert r["reason_code"] == "DXY_CFD_MISSING_WHILE_DX_ACTIVE" and r["handling"] == "MISSING"
    assert (r["start"], r["end"]) == (hole[5], hole[44] + pd.Timedelta(minutes=1))
    assert (r["cfd_gap_minutes"], r["dx_active_minutes"]) == (60, 40)


def test_no_flag_when_dx_also_quiet_or_gap_short():
    end = START + pd.Timedelta(hours=4)
    all_minutes = pd.date_range(START, end, freq="1min", inclusive="left")
    closed = pd.date_range("2020-03-09 20:00", "2020-03-09 21:00", freq="1min", inclusive="left", tz="UTC")
    assert q.dxy_cfd_missing_while_dx_active(all_minutes.difference(closed), _dx(closed[:10], end),
                                             START, end, CFG) == []          # session closed: DX thin too
    short = closed[:20]                                                     # 20-minute hole, DX fully active
    assert q.dxy_cfd_missing_while_dx_active(all_minutes.difference(short), _dx(short, end), START, end, CFG) == []


def _ticks(rows):
    ts = pd.to_datetime([r[0] for r in rows], utc=True)
    return pd.DataFrame({"ts": ts, "bid": [r[1] for r in rows], "ask": [r[2] for r in rows],
                         "bid_vol": 1.0, "ask_vol": 1.0})


def _candle_from_ticks(ticks: pd.DataFrame) -> pd.DataFrame:
    """Per-side OHLC per minute (how the vendor candle files are built), then the pipeline's mid construction."""
    t = ticks.set_index("ts")
    sides = {s: t[s].resample("1min").ohlc().add_prefix(f"{s}_") for s in ("bid", "ask")}
    c = pd.concat(sides.values(), axis=1)
    for col in ("open", "high", "low", "close"):
        c[col] = (c[f"bid_{col}"] + c[f"ask_{col}"]) / 2
    c["hl_method"] = q.HL_CANDLE_FILE
    return c


def test_non_synchronous_side_extremes_create_artificial_candle_extreme():
    # Bid high and ask high come from different ticks; the tick-mid high is 100.10 at both ticks.
    ticks = _ticks([("2025-10-21 01:00:05", 99.95, 100.05), ("2025-10-21 01:00:10", 100.00, 100.20),
                    ("2025-10-21 01:00:20", 99.80, 100.40), ("2025-10-21 01:00:50", 99.95, 100.05)])
    candle, tick_bar = _candle_from_ticks(ticks), dk._bars(ticks, "1min")
    assert candle["high"].iloc[0] == pytest.approx(100.20)       # (100.00 + 100.40) / 2
    assert tick_bar["high"].iloc[0] == pytest.approx(100.10)
    assert (candle["hl_method"].iloc[0], tick_bar["hl_method"].iloc[0]) == ("SIDE_EXTREME_MEAN", "TICK_MID")
    j = q.artificial_extrema_vs_ticks(candle, tick_bar, tolerance=0.05)
    assert bool(j["artificial"].iloc[0]) and j["high_overstatement"].iloc[0] == pytest.approx(0.10)
    assert bool(j["within_bound"].iloc[0])                        # 0.10 < (100.40 - 100.00) / 2
    assert bool(q.suspect_candle_extrema(candle, CFG).iloc[0])    # bound 0.20 > 3 x synchronous half-spread 0.05


def test_synchronous_extremes_are_not_artificial_or_suspect():
    ticks = _ticks([("2025-10-21 01:00:05", 99.95, 100.05), ("2025-10-21 01:00:10", 100.15, 100.25),
                    ("2025-10-21 01:00:50", 99.95, 100.05)])
    candle, tick_bar = _candle_from_ticks(ticks), dk._bars(ticks, "1min")
    j = q.artificial_extrema_vs_ticks(candle, tick_bar, tolerance=0.05)
    assert not bool(j["artificial"].iloc[0]) and j["high_overstatement"].iloc[0] == pytest.approx(0.0)
    assert not bool(q.suspect_candle_extrema(candle, CFG).iloc[0])


def test_spread_spike_tick_is_flagged_suspect():
    # 2018-01-17 02:10 DXY pattern: one quote with a 1.76 spread inflates both candle extremes.
    ticks = _ticks([("2018-01-17 02:10:00", 88.735, 90.496), ("2018-01-17 02:10:01", 89.287, 89.735),
                    ("2018-01-17 02:10:30", 89.372, 89.459)])
    candle = _candle_from_ticks(ticks)
    assert bool(q.suspect_candle_extrema(candle, CFG).iloc[0])
