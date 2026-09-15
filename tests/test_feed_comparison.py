"""Recent feed comparison and higher-timeframe fidelity helpers (CBR-PROT-013B §7, D25) on synthetic data only."""

from datetime import UTC
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from cbr.data import feed_comparison as fc
from cbr.data import price_series as ps
from cbr.engine import cbr1h
from cbr.engine.params import load_cbr1h

T = lambda s: pd.Timestamp(s, tz="UTC")
DAYS = ["2030-01-08", "2030-01-09"]                      # Tuesday, Wednesday


def _walk(start: str, periods: int, seed: int = 7) -> pd.DataFrame:
    """Synthetic STRUCTURE 5s bars (random walk with trending bursts) on scheduled-open time only."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(T(start), periods=periods, freq="5s")
    drift = np.repeat(rng.normal(0, 0.06, periods // 240 + 1), 240)[:periods]
    close = 2000 + np.cumsum(rng.normal(0, 0.12, periods) + drift)
    open_ = np.concatenate([[close[0]], close[:-1]])
    wig = np.abs(rng.normal(0, 0.05, periods))
    b = pd.DataFrame({"open": open_, "high": np.maximum(open_, close) + wig, "low": np.minimum(open_, close) - wig,
                      "close": close}, index=idx)
    minutes = b.index.floor("1min")
    b = b[~fc.expected_closed_mask(pd.DatetimeIndex(minutes))]
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


@pytest.fixture(scope="module")
def synthetic():
    s5 = _walk("2030-01-08 00:00", 2 * 24 * 720)
    s1 = ps.rollup_structure(s5, "1min")
    return s5, s1[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]


def test_wilson_interval_and_rate():
    lo, hi = fc.wilson(8, 10)
    assert lo == pytest.approx(0.4902, abs=1e-3) and hi == pytest.approx(0.9433, abs=1e-3)
    assert fc.rate(0, 0) == {"agree": 0, "n": 0, "rate": None, "wilson95": None}


def test_comparison_minutes_are_scheduled_open_only_from_the_start():
    m = fc.comparison_minutes(["2026-09-11", "2026-09-14"], T("2026-09-11 01:00"))
    assert m[0] == T("2026-09-11 01:00") and T("2026-09-11 21:00") not in m          # Friday close 17:00 New York
    assert T("2026-09-14 21:30") not in m and T("2026-09-14 22:00") in m              # daily break
    assert len(m) == (21 * 60 - 60) + (23 * 60)


def test_match_events_is_one_to_one_within_tolerance_and_key():
    a = pd.DataFrame({"kind": ["H", "H", "L"], "time": [T("2030-01-08 01:00"), T("2030-01-08 01:01"), T("2030-01-08 01:05")]})
    b = pd.DataFrame({"kind": ["H", "L", "L"], "time": [T("2030-01-08 01:01"), T("2030-01-08 01:07"), T("2030-01-08 01:06")]})
    m = fc.match_events(a, b, ["kind"], pd.Timedelta(minutes=1))
    assert len(m) == 2                                                              # one b "H" for two a "H"
    assert m.iloc[0]["a_time"] == T("2030-01-08 01:00") and m.iloc[1]["b_time"] == T("2030-01-08 01:06")
    mem = fc.membership(a, b, ["kind"], pd.Timedelta(minutes=1), (T("2030-01-08 00:00"), T("2030-01-09 00:00")))
    assert (mem["matched"], mem["forexcom_only"], mem["dukascopy_only"]) == (2, 1, 1) and mem["rate"] == 0.5


def _study(fx1m, dk1m, minutes):
    p = load_cbr1h("A")
    band = {"floor_usd": 0.02, "residual_percentile": 95, "round_up_to_usd": 0.05}
    exports = {"5m": fc.rollup(fx1m, "5min"), "15m": fc.rollup(fx1m, "15min")}
    return fc.compare_recent(fx1m, dk1m, minutes, p, exports=exports, band=band, hour_minutes=[25, 35, 45],
                             count_margin=pd.Timedelta(hours=2))


def test_identical_and_offset_feeds_agree_everywhere(synthetic):
    _, s1 = synthetic
    minutes = fc.comparison_minutes(DAYS, T("2030-01-08 01:00"))
    dk1m = fc.restrict(s1, minutes)
    for offset in (0.0, 0.37):                                           # a constant level offset changes no structure
        study = _study(dk1m + offset, dk1m, minutes)
        assert study["alignment"]["zero_lag_confirmed"] and study["feed_band"]["tau_usd"] == 0.05
        assert study["offsets"]["delta_median_close_offset"] == pytest.approx(offset)
        for tier in ("ltf_1m", "mtf_5m"):
            assert study["swings"][tier]["rate"] == 1.0 and study["swings"][tier]["n"] > 0
        assert study["takes_15m"]["pooled"]["rate"] == 1.0
        assert study["hour_extension"]["direction"]["rate"] == 1.0
        assert study["condition_at_hour_open"]["condition"]["rate"] == 1.0
        assert study["hour_level_state"]["membership"]["rate"] == 1.0 and study["hour_level_state"]["evaluations"] > 0
        assert study["type3_1m"]["rate"] == 1.0 and study["hilo_1m"]["rate"] == 1.0
        assert all(v["identical"] == v["bars"] for v in study["export_vs_1m_rollup"].values())
        c9 = fc.criterion_9(study, ["ltf_swing_membership", "mtf_swing_membership", "takes_15m", "hour_extension_direction",
                                    "condition_at_hour_open", "type3_1m", "hour_level_membership"], 0.5, 0.8)
        assert c9["status"] == "MET"


def test_noise_lowers_agreement_and_widens_the_band(synthetic):
    _, s1 = synthetic
    minutes = fc.comparison_minutes(DAYS, T("2030-01-08 01:00"))
    dk1m = fc.restrict(s1, minutes)
    rng = np.random.default_rng(3)
    noise = pd.DataFrame(rng.normal(0, 0.3, (len(dk1m), 4)), index=dk1m.index, columns=["open", "high", "low", "close"])
    fx1m = dk1m + noise
    fx1m["high"] = fx1m[["open", "high", "low", "close"]].max(axis=1)
    fx1m["low"] = fx1m[["open", "high", "low", "close"]].min(axis=1)
    study = _study(fx1m, dk1m, minutes)
    assert study["feed_band"]["tau_usd"] > 0.05
    assert study["swings"]["ltf_1m"]["rate"] < 1.0


def test_hour_state_reproduces_the_engine_hour_level_rules(synthetic):
    """The FOREXCOM-side hour state uses the engine's formulas: on the same STRUCTURE bars every hour-level rule of every
    engine candidate is identical (the previous-15m take is compared only where Q's 5s and 1m views coincide)."""
    s5, s1 = synthetic
    p = load_cbr1h("A")
    res = cbr1h.run_cbr1h(s1, s5, start=T("2030-01-09 06:00"), end=T("2030-01-09 12:00"), variant="A", params=p)
    cands = res.candidates
    assert len(cands) > 5
    ctx = fc.FeedContext(s1[["open", "high", "low", "close"]], p)
    checked = 0
    for _, c in cands.iterrows():
        st = fc.hour_state(ctx, c["hour_open_utc"], c["timestamp"])
        assert st["direction"] == c["direction"]
        for rule in fc.HOUR_RULES:
            if rule == "M1H-6A-2-PREV-15M-BROKEN-BY-Q":
                continue
            assert st["rules"].get(rule) == c["rules"].get(rule), (c["signal_id"], rule)
        checked += 1
    assert checked == len(cands)


def test_export_intervals_are_capped_at_the_nominal_length():
    ex = pd.DataFrame({"open": [1, 2, 3]}, index=pd.DatetimeIndex([T("2030-01-07 22:00"), T("2030-01-08 22:00"),
                                                                   T("2030-01-10 22:00")]))
    ends = fc.export_intervals(ex, pd.Timedelta(days=1))
    assert list(ends) == [T("2030-01-08 22:00"), T("2030-01-09 22:00"), T("2030-01-11 22:00")]


def test_interval_bar_requires_full_coverage(synthetic):
    _, s1 = synthetic
    full = fc.interval_bar(s1, T("2030-01-08 03:00"), T("2030-01-08 04:00"))
    assert full["coverage"] == 1.0 and full["high"] >= full["low"]
    gap = fc.interval_bar(s1.drop(T("2030-01-08 03:10")), T("2030-01-08 03:00"), T("2030-01-08 04:00"))
    assert gap == {"coverage": pytest.approx(59 / 60)}
    fx = pd.Series({"open": full["open"] + 1, "high": full["high"] + 1, "low": full["low"] + 1, "close": full["close"] + 1})
    rec = fc.compare_bar(fx, full)
    assert rec["offsets"] == {k: pytest.approx(1.0) for k in ("open", "high", "low", "close")} and rec["direction_agree"]
    assert fc.compare_bar(fx, gap)["class"] == "DATA_LIMITATION"


def test_criterion_9_thresholds():
    study = {"swings": {"ltf_1m": fc.rate(9, 10), "mtf_5m": fc.rate(7, 10)}, "takes_15m": {"pooled": fc.rate(10, 10)},
             "hour_extension": {"direction": fc.rate(10, 10)}, "condition_at_hour_open": {"condition": fc.rate(4, 10)},
             "type3_1m": fc.rate(10, 10), "hour_level_state": {"membership": fc.rate(10, 10)}}
    c9 = fc.criterion_9(study, ["ltf_swing_membership", "mtf_swing_membership", "condition_at_hour_open"], 0.5, 0.8)
    assert c9["status"] == "FAIL_EVIDENCE" and c9["fail_evidence"] == ["condition_at_hour_open"]
    assert c9["concerns"] == ["mtf_swing_membership"]
    assert fc.criterion_9(study, ["ltf_swing_membership", "mtf_swing_membership"], 0.5, 0.8)["status"] == "CONCERN"


def test_mixed_timestamp_units_are_normalized(synthetic):
    """Regression (CBR-RUN-013B-1 incident): FOREXCOM exports load with second-unit, timezone.utc indexes and stored bars with
    ms, ZoneInfo("UTC");
    the study must not lose the DatetimeIndex when joining them."""
    _, s1 = synthetic
    minutes = fc.comparison_minutes(DAYS, T("2030-01-08 01:00"))
    dk1m = fc.restrict(s1, minutes)
    dk_ms = dk1m.drop(dk1m.index[100:103])
    dk_ms.index = dk_ms.index.tz_convert(ZoneInfo("UTC")).as_unit("ms")
    fx_s = (dk1m + 0.1).drop(dk1m.index[500:502])
    fx_s.index = fx_s.index.tz_convert(UTC).as_unit("s")
    raw = fx_s[["close"]].join(dk_ms[["close"]], how="inner", lsuffix="_fx", rsuffix="_dk")
    assert not isinstance(raw.index, pd.DatetimeIndex)                     # the failure mode, reproduced
    study = _study(fx_s, dk_ms, minutes)
    assert study["alignment"]["matched_minutes"] == len(dk1m) - 5
