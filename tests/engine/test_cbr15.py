"""CBR15_BASELINE_V1 reference engine (Phase 11): guards, causality, determinism, ledger completeness, contract shape.

Synthetic tests need no market data. Fixture tests run on stored STRUCTURE bars for the CX-TE1-1 window (holdout
period, implementation parity use only) and skip when the gitignored data isn't present.
"""

import dataclasses
import json
from pathlib import Path

import pandas as pd
import pytest

from cbr.data import price_series as ps
from cbr.engine import cbr15
from cbr.engine.params import load_cbr15

ROOT = Path(__file__).resolve().parents[2]
UTC = "UTC"
T = lambda s: pd.Timestamp(s, tz=UTC)
FIXTURE = (T("2025-10-23 20:00"), T("2025-10-24 06:00"), T("2025-10-24 03:30"), T("2025-10-24 05:00"))


def _ticks(start="2025-10-21 00:00", minutes=30):
    ts = pd.date_range(T(start), periods=minutes * 12, freq="5s")
    price = 100 + (pd.Series(range(len(ts))) % 37) * 0.1
    return pd.DataFrame({"ts": ts, "bid": price.values - 0.1, "ask": price.values + 0.1, "bid_vol": 1.0, "ask_vol": 1.0})


def test_engine_refuses_non_structure_bars():
    ticks = _ticks()
    s1, s5 = ps.structure_bars(ticks, "1min"), ps.structure_bars(ticks, "5s")
    with pytest.raises(ps.PriceRoleError):
        cbr15.run_cbr15(ps.execution_bars(ticks, "1min"), s5, start=T("2025-10-21 00:15"), end=T("2025-10-21 00:30"))
    with pytest.raises(ps.PriceRoleError):
        cbr15.run_cbr15(s1.assign(hl_method="SIDE_EXTREME_MEAN"), s5, start=T("2025-10-21 00:15"),
                        end=T("2025-10-21 00:30"))


def _bars5(rows, start="2025-10-21 00:08"):
    idx = pd.date_range(T(start), periods=len(rows), freq="5s")
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


def _cand(q, ts, raw, htf=True, outcome=None):
    rules = {"M15-COND-01": raw, "M15-HTF-01": htf}
    return {"candle_open_utc": T(q), "timestamp": T(ts), "direction": "SELL", "variant": "base", "rules": rules,
            "raw_outcome": outcome}


def test_prior_rule_counts_setups_formed_in_the_last_hour_never_outcomes():
    """D19-1 (OQ-36 C′): formation only. A setup that never reached target still counts; one formed before the 60-min
    window, after Q.t0, failing another rule, or vetoed by the hourly signal state doesn't."""
    p = load_cbr15()
    cand = pd.DataFrame([
        _cand("2025-10-20 23:45", "2025-10-20 23:52", raw=True),                  # 68 min before Q: outside the hour
        _cand("2025-10-21 00:15", "2025-10-21 00:20", raw=True, outcome="STOP"),  # formed; outcome irrelevant
        _cand("2025-10-21 00:30", "2025-10-21 00:35", raw=False),                 # not a qualifying setup
        _cand("2025-10-21 00:45", "2025-10-21 00:50", raw=True, htf=False),       # hourly VETO: not qualifying
        _cand("2025-10-21 01:00", "2025-10-21 01:09", raw=True),                  # the candidate itself (Q = 01:00)
        _cand("2025-10-21 01:15", "2025-10-21 01:20", raw=True),
    ])
    cbr15._apply_prior_rule(cand, p)
    q = cand.iloc[4]
    assert q["prior_setup_count"] == 1 and bool(q["prior_setup_exists"]) and q["rules"]["M15-COND-03"] is True
    assert q["prior_setup_latest_time"] == T("2025-10-21 00:20") and q["prior_setup_count_120m"] == 2
    assert (cand["prior_setup_played_out_status"] == cbr15.PLAYED_OUT_UNKNOWN).all()
    assert "raw_outcome" not in {k for r in cand["rules"] for k in r}
    first = cand.iloc[0]
    assert first["prior_setup_count"] == 0 and first["rules"]["M15-COND-03"] is False and first["event"] == "REJECTED"
    assert cand.iloc[5]["prior_setup_count"] == 2                               # 00:20 and 01:09 (00:50 vetoed)


def test_q_minus_1_must_be_broken_by_q_itself():
    """D19-4 (OQ-41): the previous candle's high must be taken by Q's own extension; an older candle's level doesn't do."""
    from cbr.structure import overextension as oe_mod

    q0 = T("2025-10-21 00:15")
    rows = [(100.0, 100.4, 99.9, 100.3), (100.3, 100.9, 100.2, 100.8), (100.8, 101.2, 100.7, 101.1)]
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=pd.date_range(q0, periods=3, freq="1min"))
    kw = {"atr_1m": 1.0, "activation_atr": 0.5, "pullback_frac": 0.5, "two_sided_frac": 0.5}
    breaks = oe_mod.evaluate(b, q0, 100.0, q0 + pd.Timedelta(minutes=3), prev_candle_high=101.0, prev_candle_low=99.0, **kw)
    assert breaks.prev_candle_break is True                                   # Q (high 101.2) takes Q−1's 101.0
    older_only = oe_mod.evaluate(b, q0, 100.0, q0 + pd.Timedelta(minutes=3), prev_candle_high=101.5,
                                 prev_candle_low=99.0, **kw)
    assert older_only.prev_candle_break is False                              # Q−2's 101.1 is irrelevant: Q−1 = 101.5


def _fixture():
    from cbr.data.canonical_bars import load_structure
    try:
        s1, s5 = load_structure(FIXTURE[0], FIXTURE[1], "1m"), load_structure(FIXTURE[0], FIXTURE[1], "5s")
    except FileNotFoundError:
        pytest.skip("stored STRUCTURE bars for the fixture window not present")
    return s1, s5


def test_engine_is_deterministic_on_fixture_window():
    s1, s5 = _fixture()
    a = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3])
    b = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3])
    assert len(a.candidates) > 0 and cbr15.result_hash(a) == cbr15.result_hash(b)


def test_engine_decisions_are_causal_truncation_and_future_mutation():
    s1, s5 = _fixture()
    full = cbr15.decision_frame(cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3]))
    for cut in (T("2025-10-24 04:10"), T("2025-10-24 04:26"), T("2025-10-24 04:40")):
        k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= cut], s5[s5.index + pd.Timedelta(seconds=5) <= cut]
        trunc = cbr15.decision_frame(cbr15.run_cbr15(k1, k5, start=FIXTURE[2], end=FIXTURE[3]))
        m1, m5 = s1.copy(), s5.copy()
        for m in (m1, m5):
            later = m.index >= cut
            m.loc[later, ["open", "high", "low", "close"]] = m.loc[later, ["open", "high", "low", "close"]] * 1.004
        mutated = cbr15.decision_frame(cbr15.run_cbr15(m1, m5, start=FIXTURE[2], end=FIXTURE[3]))
        want = full[full["timestamp"] <= cut].reset_index(drop=True)
        assert len(want) > 0
        for other in (trunc, mutated):
            got = other[other["timestamp"] <= cut].reset_index(drop=True)
            pd.testing.assert_frame_equal(got, want)


def test_every_rejection_is_explained_and_armed_rows_fail_nothing():
    s1, s5 = _fixture()
    r = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3])
    c = r.candidates
    assert (c.loc[c["event"] == "REJECTED", "rules_failed"].map(len) > 0).all()
    assert (c.loc[c["event"] == "ARMED", "rules_failed"].map(len) == 0).all()
    needed = {"M15-COND-01", "M15-COND-02", "M15-COND-03", "M15-COND-04", "M15-T3-01", "M15-OE-01", "M15-OE-02",
              "M15-OE-03a", "M15-OE-03b", "M15-LOC-04", "M15-TIME-01", "M15-HTF-01", "NT_SYDNEY", "NT_ROLLOVER",
              "NT_INCOMPLETE_Q", "IMPL-REWARD"}
    assert all(needed <= set(rules) for rules in c["rules"])
    assert (c["htf_signal_state"] == "NOT_EVALUATED").all() and (c["htf_fill_state"] == "NOT_EVALUATED").all()


def test_signal_contract_shape_with_prior_rule_relaxed_for_shape_only():
    """Contract-shape check only: prior_hard_min=0 is NOT a baseline setting; it just forces ARMED rows to exist."""
    s1, s5 = _fixture()
    p = dataclasses.replace(load_cbr15(), prior_hard_min=0)
    r = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3], params=p)
    assert r.signals, "expected at least one ARMED row with the prior rule relaxed"
    schema = json.loads((ROOT / "docs" / "architecture" / "schemas" / "cbr-signal.v1.schema.json").read_text())
    for sig in r.signals:
        assert set(schema["required"]) <= set(sig)
        assert sig["extremes_source"] == "TICK_MID" and sig["price_role"] == "STRUCTURE"
        assert set(schema["properties"]["stop_rule"]["required"]) <= set(sig["stop_rule"])
        assert sig["data_confidence"]["reason_codes"] == ["HTF_NOT_EVALUATED"]
        assert sig["stop_rule"]["execution_inputs"]["spread_at_decision"] is None        # engine never reads spread


# ---- owner ruling D17 (Phase 11 review) ----

def test_anchor_path_tracks_most_adverse_extension_extreme_through_activation():
    rows = [(100, 100.5, 99.9, 100.4), (100.4, 101.0, 100.2, 100.8), (100.8, 100.9, 100.1, 100.2),
            (100.2, 101.4, 100.0, 101.3), (101.3, 101.2, 100.5, 100.6)]
    b = _bars5(rows, start="2025-10-21 00:07:40")
    q0, act, end = T("2025-10-21 00:07:40"), T("2025-10-21 00:07:55"), T("2025-10-21 00:08:05")
    anchor, when, path = cbr15._anchor_path(b, q0, act, end, "SELL")
    assert anchor == 101.0 and when == T("2025-10-21 00:07:50")          # highest high through activation
    assert path == [[T("2025-10-21 00:08:00"), 101.4]]                   # new extreme after activation
    row = pd.Series({"structure_stop_anchor": anchor, "stop_anchor_path": path})
    assert cbr15.anchor_at(row, T("2025-10-21 00:07:59")) == 101.0 and cbr15.anchor_at(row, T("2025-10-21 00:08:00")) == 101.4
    long_anchor, _, _ = cbr15._anchor_path(b, q0, act, end, "BUY")
    assert long_anchor == 99.9


def _window(a, b):
    from cbr.data.canonical_bars import load_structure
    try:
        return load_structure(a, b, "1m"), load_structure(a, b, "5s")
    except FileNotFoundError:
        pytest.skip("stored STRUCTURE bars not present")


def test_unresolved_trend_direction_is_a_recorded_context_failure():
    s1, s5 = _window(T("2025-10-20 18:00"), T("2025-10-21 05:00"))
    r = cbr15.run_cbr15(s1, s5, start=T("2025-10-21 03:30"), end=T("2025-10-21 04:00"))
    tr_none = r.candles[(r.candles["condition"] == "TRENDING_RANGE") & (r.candles["cond_direction"] == "NONE")]
    assert len(tr_none) > 0
    assert (tr_none["context_reason"] == cbr15.TREND_DIRECTION_UNRESOLVED).all()
    c = r.candidates[r.candidates["cond_direction"] == "NONE"]
    assert len(c) and c["reject_reasons"].map(lambda x: cbr15.TREND_DIRECTION_UNRESOLVED in x).all()


def test_type3_resolved_before_second_half_is_not_kept_armed():
    s1, s5 = _window(T("2025-10-20 18:00"), T("2025-10-21 01:00"))
    r = cbr15.run_cbr15(s1, s5, start=T("2025-10-21 00:00"), end=T("2025-10-21 00:15"))
    early = r.candidates[r.candidates["cancel_reason"] == cbr15.TYPE3_RESOLVED_TOO_EARLY]
    assert len(early) > 0
    assert (early["cancel_time"] == early["structure_trigger_touch_time"]).all()
    assert (early["structure_trigger_touch_time"] < early["candle_open_utc"] + pd.Timedelta(minutes=7.5)).all()


def test_htf_not_evaluated_is_neither_pass_nor_fail_and_blocks_eligibility():
    s1, s5 = _fixture()
    r = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3])
    c = r.candidates
    assert not c["rules_failed"].map(lambda f: "M15-HTF-01" in f).any()
    assert c["rules_not_evaluated"].map(lambda f: "M15-HTF-01" in f).all()
    assert (~c["baseline_eligible"]).all()
    assert c["eligibility_blockers"].map(lambda b: cbr15.BLOCKER_HTF in b and cbr15.BLOCKER_HTF_FILL in b).all()


# ---- owner ruling D19 (Phase 13 readiness) ----

def test_htf_signal_state_and_fill_state_are_separate():
    """D19-15: fill state NOT_EVALUATED never rejects nor enters the signal rule; a signal VETO does reject."""
    s1, s5 = _fixture()
    fill_unknown = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3],
                                   htf=lambda _t, _d: {"signal": "CLEAR", "fill": "NOT_EVALUATED"}).candidates
    base = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3],
                           htf=lambda _t, _d: {"signal": "CLEAR", "fill": "NOT_REQUIRED"}).candidates
    assert fill_unknown["rules"].map(lambda r: r["M15-HTF-01"] is True).all()
    assert list(fill_unknown["event"]) == list(base["event"])                  # fill state doesn't touch signals
    assert fill_unknown["eligibility_blockers"].map(lambda b: cbr15.BLOCKER_HTF_FILL in b).all()
    veto = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3],
                           htf=lambda _t, _d: {"signal": "VETO", "fill": "NOT_REQUIRED"}).candidates
    assert (veto["event"] == "REJECTED").all() and veto["rules_failed"].map(lambda f: "M15-HTF-01" in f).all()


def test_trigger_time_fields_are_causal_at_the_shift():
    s1, s5 = _fixture()
    full = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3])
    shifts = full.candidates["five_second_shift_time"].dropna()
    assert len(shifts) > 0
    cut = shifts.iloc[0] + pd.Timedelta(seconds=25)                            # mid-minute: the 1m bar isn't closed
    k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= cut], s5[s5.index + pd.Timedelta(seconds=5) <= cut]
    trunc = cbr15.run_cbr15(k1, k5, start=FIXTURE[2], end=FIXTURE[3])

    def known(r):
        f = cbr15.trigger_frame(r)
        t = pd.to_datetime(f["five_second_shift_time"], utc=True)
        return f[t + pd.Timedelta(seconds=5) <= cut].reset_index(drop=True)
    pd.testing.assert_frame_equal(known(trunc), known(full))
    assert set(full.candidates["trigger_timing_state"]) <= {"IN_WINDOW", cbr15.TYPE3_RESOLVED_TOO_EARLY, "NO_SHIFT"}


# ---- D19 follow-up ruling (D20) ----

def test_prior_setup_formed_without_its_own_prior_requirement_cbr15():
    """D20-8A: raw_setup_armed ignores the setup's own COND-03, so the first setup of a session still counts later."""
    p = load_cbr15()
    cand = pd.DataFrame([_cand("2025-10-21 00:00", "2025-10-21 00:09", raw=True),
                         _cand("2025-10-21 00:30", "2025-10-21 00:40", raw=True)])
    cbr15._apply_prior_rule(cand, p)
    first, later = cand.iloc[0], cand.iloc[1]
    assert first["rules"]["M15-COND-03"] is False and bool(first["raw_setup_armed"]) is True
    assert later["prior_setup_count"] == 1 and later["rules"]["M15-COND-03"] is True
    assert later["prior_setup_window_start"] == T("2025-10-20 23:30") and later["prior_setup_window_end"] == T("2025-10-21 00:30")


def test_cbr15_q_minus_1_has_no_trade_direction_exception():
    """D20-3: the CBR1H exception (Q−1 closed in the trade direction) must not leak into CBR15."""
    import inspect

    from cbr.structure import overextension as oe_mod

    q0 = T("2025-10-21 00:15")
    rows = [(100.0, 100.4, 99.9, 100.3), (100.3, 100.9, 100.2, 100.8)]
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=pd.date_range(q0, periods=2, freq="1min"))
    oe = oe_mod.evaluate(b, q0, 100.0, q0 + pd.Timedelta(minutes=2), atr_1m=1.0, activation_atr=0.5, pullback_frac=0.5,
                         two_sided_frac=0.5, prev_candle_high=101.0, prev_candle_low=99.0)
    # SELL setup (up-extension); Q−1 (high 101.0) closed bearish = in the trade direction; Q never took 101.0
    assert cbr15.q_takes_prev_candle(oe) is False
    assert list(inspect.signature(cbr15.q_takes_prev_candle).parameters) == ["oe"]
    src = inspect.getsource(cbr15)
    assert "prev_15m_break" not in src and "q_prev_closed_in_trade_direction" not in src


def test_cbr15_condition_window_uses_tradable_time_and_keeps_vendor_gaps():
    """D20-5, D20-8E/F: the daily break doesn't consume the 2 h window; a vendor gap inside open time stays missing."""
    from cbr.engine.common import condition_window

    p = load_cbr15()
    assert p.window_basis == "TRADABLE"
    as_of = T("2025-10-21 22:30")                                         # daily break 21:00-22:00 UTC (17:00 New York, EDT)
    full = pd.date_range(T("2025-10-21 18:00"), as_of, freq="1min", inclusive="left")
    w = condition_window(full, as_of, p.window, p.window_basis)
    assert w["condition_window_start"] == T("2025-10-21 19:30")
    assert w["condition_tradable_minutes"] == 120 and w["condition_elapsed_clock_minutes"] == 180
    assert w["condition_missing_minutes"] == 0
    clock = condition_window(full, as_of, p.window, "CLOCK")
    assert clock["condition_tradable_minutes"] == 60                      # the 1 h closure would have eaten 60 min
    gap = full[(full < T("2025-10-21 20:00")) | (full >= T("2025-10-21 20:15"))]        # unexpected 15-min vendor gap
    wg = condition_window(gap, as_of, p.window, p.window_basis)
    assert wg["condition_window_start"] == w["condition_window_start"]   # the gap is not treated as a closure
    assert wg["condition_tradable_minutes"] == 120 and wg["condition_missing_minutes"] == 15


def test_cbr15_engine_records_condition_durations():
    s1, s5 = _fixture()
    r = cbr15.run_cbr15(s1, s5, start=FIXTURE[2], end=FIXTURE[3])
    for frame in (r.candles, r.candidates):
        assert {"condition_elapsed_clock_minutes", "condition_tradable_minutes", "condition_missing_minutes"} <= set(frame)
    assert (r.candles["condition_tradable_minutes"] == 120).all()
    assert (r.candidates["prior_setup_window_end"] == r.candidates["candle_open_utc"]).all()
