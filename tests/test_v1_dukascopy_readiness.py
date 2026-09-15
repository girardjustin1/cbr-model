"""D21: Dukascopy calibration-day integrity checks on synthetic ticks and bars (no network, no real data needed)."""

import pandas as pd

from cbr.data import price_series as ps
from cbr.data import v1_dukascopy_readiness as r

T = lambda s: pd.Timestamp(s, tz="UTC")


def _ticks(rows):
    return pd.DataFrame(rows, columns=["ts", "bid", "ask", "bid_vol", "ask_vol"])


def test_tick_checks_flag_duplicates_bad_prices_spreads_and_order():
    good = _ticks([(T("2025-11-11 00:00:00.1"), 4000.0, 4000.5, 1.0, 1.0), (T("2025-11-11 00:00:00.2"), 4000.1, 4000.6, 1.0, 1.0)])
    c = r.tick_checks(good)
    assert c["monotonic_timestamps"] and c["duplicate_ticks_exact"] == 0 and c["bad_spreads_ask_le_bid"] == 0
    bad = _ticks([(T("2025-11-11 00:00:00.2"), 4000.1, 4000.6, 1.0, 1.0), (T("2025-11-11 00:00:00.2"), 4000.1, 4000.6, 1.0, 1.0),
                  (T("2025-11-11 00:00:00.1"), 0.0, 4000.0, 1.0, 1.0), (T("2025-11-11 00:00:00.3"), 4000.5, 4000.5, 1.0, 1.0)])
    c = r.tick_checks(bad)
    assert not c["monotonic_timestamps"] and c["duplicate_ticks_exact"] == 1 and c["duplicate_timestamps"] == 1
    assert c["non_positive_prices"] == 1 and c["bad_spreads_ask_le_bid"] == 1


def test_session_gaps_separate_vendor_gaps_from_scheduled_closures():
    day = "2025-11-11"                                                     # Tuesday; daily break 22:00-23:00 UTC (EST)
    minutes = pd.date_range(T(day), periods=1440, freq="1min")
    open_minutes = minutes[(minutes < T("2025-11-11 22:00")) | (minutes >= T("2025-11-11 23:00"))]
    ticks = _ticks([(t + pd.Timedelta("1s"), 4000.0, 4000.4, 1.0, 1.0) for t in open_minutes])
    bars = ps.structure_bars(ticks, "1min")
    s = r.session_gaps(bars, day)
    assert s["scheduled_closed_minutes"] == 60 and s["missing_scheduled_open_minutes"] == 0
    assert s["bars_inside_scheduled_closure"] == 0
    gap = bars[(bars.index < T("2025-11-11 10:00")) | (bars.index >= T("2025-11-11 10:07"))]
    s = r.session_gaps(gap, day)
    assert s["missing_scheduled_open_minutes"] == 7 and s["missing_runs"] == [["2025-11-11 10:00:00+00:00", 7]]
    extra = ps.structure_bars(_ticks([(T("2025-11-11 22:30:01"), 4000.0, 4000.4, 1.0, 1.0)]), "1min")
    assert r.session_gaps(pd.concat([bars, extra]), day)["bars_inside_scheduled_closure"] == 1


def test_missing_day_is_not_ready(monkeypatch, tmp_path):
    monkeypatch.setattr(r.dk, "RAW", tmp_path)
    out = r.day_readiness("2025-11-11")
    assert out["ready"] is False and out["problems"] == ["ticks not stored"]
