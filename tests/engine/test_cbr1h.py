"""CBR1H_BASELINE_V1 reference engine: guards, causality, determinism, ledger, hourly state (Phase 12) and the D19
rulings (5s trigger, Q−1 broken by Q, HVCS into the shift, :30 diagnostic, prior-setup existence, tradable window,
D8/D9 switches)."""

import dataclasses

import pandas as pd
import pytest

from cbr.data import price_series as ps
from cbr.data.sessions import tradable_window_start
from cbr.engine import cbr1h
from cbr.engine.common import condition_window, prev_15m_break
from cbr.engine.params import load_cbr1h
from cbr.structure import overextension as oe_mod

T = lambda s: pd.Timestamp(s, tz="UTC")
SPAN = (T("2025-10-23 00:00"), T("2025-10-24 07:00"), T("2025-10-24 04:00"), T("2025-10-24 05:00"))   # CX-TE1-1


def _bars(rows, start, freq):
    idx = pd.date_range(T(start), periods=len(rows), freq=freq)
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


def test_hilo_prior_arm_is_placed_at_the_previous_bar_close():
    m1 = _bars([(10, 10.5, 9.8, 10.2), (10.2, 10.4, 9.6, 9.9), (9.9, 10.6, 9.9, 10.5)], "2025-10-21 01:00", "1min")
    s5 = _bars([(10, 10, 10, 10)] * 36, "2025-10-21 01:00", "5s")
    arms = cbr1h.hilo_arms(m1, s5, pd.Timedelta(minutes=1), "BUY", T("2025-10-21 01:00"), T("2025-10-21 01:03"), 0.01)
    assert arms == [{"arm_time": T("2025-10-21 01:02"), "trigger": pytest.approx(10.41), "valid_until": T("2025-10-21 01:03"),
                     "kind": "prior", "bar_open": T("2025-10-21 01:02"), "stop_ref": 9.6}]


def test_hilo_same_candle_arm_requires_opposite_break_first_on_5s():
    m1 = _bars([(10, 10.5, 9.8, 10.2), (10.2, 10.4, 9.9, 10.0), (10.0, 10.6, 9.7, 10.5)], "2025-10-21 01:00", "1min")
    rows = [(10, 10.1, 9.95, 10)] * 12 + [(10, 10.05, 9.7, 9.8)] + [(9.8, 10.2, 9.8, 10.1)] * 11
    s5 = _bars(rows, "2025-10-21 01:01", "5s")
    arms = cbr1h.hilo_arms(m1, s5, pd.Timedelta(minutes=1), "BUY", T("2025-10-21 01:02"), T("2025-10-21 01:03"), 0.01)
    assert len(arms) == 1 and arms[0]["kind"] == "same"
    assert arms[0]["arm_time"] == T("2025-10-21 01:02:05") and arms[0]["trigger"] == pytest.approx(10.41)
    broken_first = [(10, 10.5, 9.95, 10.4)] + [(10.4, 10.4, 9.7, 9.8)] * 11            # entry side broken before the low
    s5b = _bars([(10, 10.1, 9.95, 10)] * 12 + broken_first, "2025-10-21 01:01", "5s")
    assert cbr1h.hilo_arms(m1, s5b, pd.Timedelta(minutes=1), "BUY", T("2025-10-21 01:02"), T("2025-10-21 01:03"), 0.01) == []


def test_engine_refuses_non_structure_bars():
    m1 = _bars([(10, 10.5, 9.8, 10.2)] * 5, "2025-10-21 01:00", "1min")
    bad = m1.assign(hl_method="SIDE_EXTREME_MEAN")
    with pytest.raises(ps.PriceRoleError):
        cbr1h.run_cbr1h(bad, m1, start=T("2025-10-21 01:00"), end=T("2025-10-21 02:00"))


def _span():
    from cbr.data.canonical_bars import load_structure
    try:
        return load_structure(SPAN[0], SPAN[1], "1m"), load_structure(SPAN[0], SPAN[1], "5s")
    except FileNotFoundError:
        pytest.skip("stored STRUCTURE bars not present")


@pytest.fixture(scope="module")
def run_a():
    s1, s5 = _span()
    return s1, s5, cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], variant="A")


def test_deterministic(run_a):
    s1, s5, r = run_a
    assert len(r.candidates) > 0
    assert cbr1h.result_hash(r) == cbr1h.result_hash(cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], variant="A"))


def test_causal_truncation_and_future_mutation(run_a):
    s1, s5, r = run_a
    full = cbr1h.decision_frame(r)
    cut = T("2025-10-24 04:36:35")                                  # mid-minute: the 1m bar containing cut isn't closed
    k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= cut], s5[s5.index + pd.Timedelta(seconds=5) <= cut]
    m1, m5 = s1.copy(), s5.copy()
    for m in (m1, m5):
        later = m.index >= cut
        m.loc[later, ["open", "high", "low", "close"]] *= 1.003
    want = full[full["timestamp"] <= cut].reset_index(drop=True)
    assert len(want) > 0
    for data in ((k1, k5), (m1, m5)):
        got = cbr1h.decision_frame(cbr1h.run_cbr1h(*data, start=SPAN[2], end=SPAN[3], variant="A"))
        pd.testing.assert_frame_equal(got[got["timestamp"] <= cut].reset_index(drop=True), want)


def test_every_rejection_explained_and_no_bid_ask(run_a):
    _, _, r = run_a
    c = r.candidates
    assert (c.loc[c["event"] == "REJECTED", "rules_failed"].map(len) > 0).all()
    assert (~c["baseline_eligible"]).all()
    needed = {"M1H-COND-01", "M1H-COND-02", "M1H-COND-03", "M1H-COND-04", "M1H-OE-01", "M1H-OE-02", "M1H-OE-04a",
              "M1H-OE-04b", "M1H-6A-1-HVCS-INTO-SHIFT", "M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q",
              "M1H-TIME-01", "NT_SYDNEY", "NT_ROLLOVER", "NT_INCOMPLETE_H", "IMPL-REWARD"}
    assert all(needed <= set(rules) for rules in c["rules"])
    assert not any(k in rules for rules in c["rules"] for k in ("M1H-TIME-02", "M1H-6A-4-HILO-TIER"))   # D19-5, D19-2
    for col in ("entry_model", "parent_structure_type", "parent_structure_time", "five_second_shift_time",
                "five_second_shift_level", "activation_time", "timing30_state", "prior_setup_exists",
                "prior_setup_count", "prior_setup_latest_time", "prior_setup_played_out_status",
                "condition_elapsed_clock_minutes", "condition_tradable_minutes", "condition_missing_minutes"):
        assert col in c.columns, col
    assert (c["entry_model"] == "HVCS_S5_SHIFT").all() and (c["parent_structure_type"] == cbr1h.PARENT_HVCS).all()
    assert set(c["timing30_state"]) <= {cbr1h.T30_PASS, cbr1h.T30_CONCERN, cbr1h.T30_NA, cbr1h.T30_UNRESOLVED}


def test_hourly_state_is_causal_and_drives_the_15m_veto(run_a):
    s1, s5, r = run_a
    as_of = T("2025-10-24 04:30")
    states = cbr1h.hourly_state(r, as_of)
    assert all(s["decision_time"] <= as_of for s in states)
    k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= as_of], s5[s5.index + pd.Timedelta(seconds=5) <= as_of]
    trunc = cbr1h.run_cbr1h(k1, k5, start=SPAN[2], end=SPAN[3], variant="A")
    ids = lambda xs: sorted((s["signal_id"], s["state"]) for s in xs)
    assert ids(cbr1h.hourly_state(trunc, as_of)) == ids(states)             # same state from data known at as_of
    assert all(s["fill_state"] == ("NOT_EVALUATED" if s["state"] == "SHIFT_TRIGGERED" else "NOT_REQUIRED") for s in states)
    provider = cbr1h.htf_provider(r)
    out = provider(as_of, "SELL")
    assert out["signal"] in ("VETO", "CLEAR") and out["fill"] in ("NOT_EVALUATED", "NOT_REQUIRED")
    with pytest.raises(ValueError):
        cbr1h.htf_provider(cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], variant="B"))


# ---- owner ruling D19 ----

def test_five_second_shift_isnt_revealed_by_unclosed_1m_information(run_a):
    """D19-17: rows whose 5s shift completed by a mid-minute cut get identical decision and trigger fields when the 1m bar
    containing the cut (and everything later) is removed or mutated."""
    s1, s5, r = run_a
    shifts = r.candidates["five_second_shift_time"].dropna().sort_values()
    if not len(shifts):
        pytest.skip("no 5s shift in the fixture hour")
    cut = shifts.iloc[0] + pd.Timedelta(seconds=10)
    assert cut.second != 0
    k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= cut], s5[s5.index + pd.Timedelta(seconds=5) <= cut]
    m1, m5 = s1.copy(), s5.copy()
    m1.loc[m1.index + pd.Timedelta(minutes=1) > cut, ["open", "high", "low", "close"]] *= 0.997
    m5.loc[m5.index + pd.Timedelta(seconds=5) > cut, ["open", "high", "low", "close"]] *= 0.997

    def known(res):
        t = cbr1h.trigger_frame(res)
        keep = pd.to_datetime(t["five_second_shift_time"], utc=True) + pd.Timedelta(seconds=5) <= cut
        d = cbr1h.decision_frame(res)
        return t[keep].reset_index(drop=True), d[d["timestamp"] <= cut].reset_index(drop=True)
    want_t, want_d = known(r)
    assert len(want_t) > 0
    for data in ((k1, k5), (m1, m5)):
        got_t, got_d = known(cbr1h.run_cbr1h(*data, start=SPAN[2], end=SPAN[3], variant="A"))
        pd.testing.assert_frame_equal(got_t, want_t)
        pd.testing.assert_frame_equal(got_d, want_d)


def test_variant_b_keeps_its_own_parent_structure():
    s1, s5 = _span()
    r = cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], variant="B")
    c = r.candidates
    if len(c):
        assert (c["parent_structure_type"] == cbr1h.PARENT_M1_T3).all() and (c["entry_model"] == "FRACTAL_1M_S5_SHIFT").all()
        assert (c["parent_known_at"] <= c["timestamp"]).all()                   # 1m parent used only after its close
        assert not c["rules"].map(lambda x: "M1H-6A-1-HVCS-INTO-SHIFT" in x).any()


def _m15(rows, start):
    idx = pd.date_range(T(start), periods=len(rows), freq="15min")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)


def test_previous_15m_candle_broken_by_q_three_cases():
    """D19-4: Q breaks Q−1 → pass; Q breaks only an older candle's level → fail; Q−1 closed in the trade direction → the
    exception applies."""
    b15 = _m15([(100, 103.0, 99, 102), (102, 101.0, 99.5, 100.5)], "2025-10-21 01:00")   # Q−2, Q−1 (bearish close)
    q0 = T("2025-10-21 01:30")
    s5_break = _bars([(100.5, 101.2, 100.4, 101.1)] * 6, "2025-10-21 01:30", "5s")
    s5_older = _bars([(100.5, 100.9, 100.4, 100.8)] * 6, "2025-10-21 01:30", "5s")
    as_of = q0 + pd.Timedelta(seconds=30)
    hit = prev_15m_break(s5_break, b15, q0, as_of, "SELL")
    assert hit["q_break_by_q"] is True and hit["q_prev_high"] == 101.0
    miss = prev_15m_break(s5_older, b15, q0, as_of, "SELL")
    assert miss["q_break_by_q"] is False
    assert miss["q_prev_closed_in_trade_direction"] is True                    # SELL: Q−1 closed bearish → exception
    bull_prev = _m15([(100, 103.0, 99, 102), (100.0, 101.0, 99.5, 100.9)], "2025-10-21 01:00")
    no_exc = prev_15m_break(s5_older, bull_prev, q0, as_of, "SELL")
    assert no_exc["q_break_by_q"] is False and no_exc["q_prev_closed_in_trade_direction"] is False
    later = prev_15m_break(s5_break, b15, q0, q0 + pd.Timedelta(seconds=5), "SELL")
    assert later["q_break_by_q"] is True                                        # uses only 5s bars closed by as_of
    none_yet = prev_15m_break(s5_break, b15, q0, q0, "SELL")
    assert none_yet["q_break_by_q"] is False


def test_hvcs_into_shift_requires_the_respected_side_to_hold_after_the_end_bar():
    rows = [(10.0, 10.3, 9.9, 10.2), (10.2, 10.5, 10.1, 10.4), (10.4, 10.7, 10.3, 10.6), (10.6, 10.9, 10.5, 10.8),
            (10.8, 11.1, 10.7, 11.0), (11.0, 11.0, 10.8, 10.85), (10.85, 10.95, 10.75, 10.8)]
    m1 = _bars(rows, "2025-10-21 01:00", "1min")
    end = T("2025-10-21 01:04")
    seq, gap, cont = cbr1h.hvcs_into_shift(m1, end, "UP", atr_1m=1.0, min_minutes=4, max_violations=1, lvcs_body_atr=0.3)
    assert seq.minutes == 4 and seq.valid and gap == 2 and cont is True       # indecision bars keep lows ≥ 10.7
    broken = m1.copy()
    broken.iloc[6, broken.columns.get_loc("low")] = 10.6                        # an indecision bar breaks the respected low
    _, _, cont2 = cbr1h.hvcs_into_shift(broken, end, "UP", atr_1m=1.0, min_minutes=4, max_violations=1, lvcs_body_atr=0.3)
    assert cont2 is False
    early = cbr1h.hvcs_into_shift(m1, T("2025-10-21 01:01"), "UP", atr_1m=1.0, min_minutes=4, max_violations=1,
                                  lvcs_body_atr=0.3)
    assert early[0].valid is False                                              # an earlier, unrelated run isn't the HVCS


def test_prior_setups_count_formation_in_own_lookback_never_outcomes():
    p = load_cbr1h("A")
    def cand(h, ts, ok):
        return {"hour_open_utc": T(h), "timestamp": T(ts), "direction": "SELL", "variant": "A",
                "parent_structure_type": cbr1h.PARENT_HVCS, "rules": {"M1H-COND-01": ok}}
    c = pd.DataFrame([cand("2025-10-20 14:00", "2025-10-20 14:30", True),             # 11 h before: outside 10 h
                      cand("2025-10-20 20:00", "2025-10-20 20:30", True),
                      cand("2025-10-20 22:00", "2025-10-20 22:40", False),
                      cand("2025-10-21 01:00", "2025-10-21 01:25", True),             # same hour: not "prior"
                      cand("2025-10-21 01:00", "2025-10-21 01:40", True)])
    cbr1h._apply_prior(c, p)
    last = c.iloc[-1]
    assert last["prior_setup_count"] == 1 and last["prior_setup_latest_time"] == T("2025-10-20 20:30")
    assert last["rules"]["M1H-COND-04"] is True and last["prior_setup_played_out_status"] == "UNKNOWN"
    assert c.iloc[0]["rules"]["M1H-COND-04"] is False
    assert c["eligibility_blockers"].map(lambda b: cbr1h.BLOCKER_HVCS_GAP in b).all()


def test_condition_window_uses_tradable_time_across_the_weekend():
    as_of = T("2025-11-10 01:00")                                               # Monday; reopen Sunday 23:00 UTC
    start = tradable_window_start(as_of, 8 * 60)
    assert start.dayofweek == 4                                                 # reaches back into Friday
    idx = pd.date_range(start, as_of, freq="1min", inclusive="left")
    w = condition_window(idx.delete(slice(0, 30)), as_of, pd.Timedelta(hours=8), "TRADABLE")
    assert w["condition_tradable_minutes"] == 480 and w["condition_elapsed_clock_minutes"] > 480
    assert w["condition_missing_minutes"] == 30                                 # vendor gap stays missing, still time
    clock = condition_window(idx, as_of, pd.Timedelta(hours=8), "CLOCK")
    assert clock["condition_elapsed_clock_minutes"] == 480 and clock["condition_tradable_minutes"] == 120


def test_timing30_is_diagnostic_and_evaluated_at_the_shift(run_a):
    _, _, r = run_a
    c = r.candidates
    assert (c.loc[c["five_second_shift_time"].isna(), "timing30_state"] == cbr1h.T30_NA).all()
    in30 = c[c["five_second_shift_time"].notna()]
    in30 = in30[(in30["five_second_shift_time"] - in30["hour_open_utc"]).between(pd.Timedelta(minutes=30),
                                                                                  pd.Timedelta(minutes=45) - pd.Timedelta(seconds=1))]
    assert (in30["timing30_state"] != cbr1h.T30_NA).all()
    assert not c["rules_failed"].map(lambda f: any("TIME-02" in x for x in f)).any()


def test_last_reset_restarts_the_extension_count_after_a_50pct_pullback():
    h0 = T("2025-10-21 01:00")
    rows = [(100, 101, 99.9, 101), (101, 102, 100.9, 102), (102, 102, 100.8, 100.9),     # up 2, pullback 60%
            (100.9, 101.5, 100.6, 101.4), (101.4, 102.5, 101.3, 102.4), (102.4, 103.0, 102.3, 102.9)]
    b = _bars(rows, "2025-10-21 01:00", "1min")
    kw = {"atr_1m": 1.0, "activation_atr": 0.5, "pullback_frac": 0.5, "two_sided_frac": 0.9}
    hour_open = oe_mod.evaluate(b, h0, 100.0, h0 + pd.Timedelta(minutes=6), **kw)
    reset = oe_mod.evaluate(b, h0, 100.0, h0 + pd.Timedelta(minutes=6), origin="LAST_RESET", **kw)
    assert hour_open.no_pullback is False and hour_open.duration_min == 5
    assert reset.no_pullback is True and reset.origin_time == T("2025-10-21 01:03") and reset.duration_min == 2
    assert reset.extreme == hour_open.extreme and reset.size == hour_open.size   # stop/target inputs unchanged


def test_d8_d9_switches_are_off_by_default_and_add_one_rule_each(run_a):
    s1, s5, r = run_a
    p = load_cbr1h("A")
    assert (p.oe_origin, p.early_shift_guard) == ("HOUR_OPEN", "NONE")
    same = cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], params=dataclasses.replace(p))
    assert cbr1h.result_hash(same) == cbr1h.result_hash(r)
    for guard, rule in (("FINAL_PUSH", "ABL-D9-FINAL-PUSH"), ("ALIGN_15M", "ABL-D9-ALIGN-15M")):
        g = cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], params=dataclasses.replace(p, early_shift_guard=guard))
        assert g.candidates["rules"].map(lambda x, rule=rule: rule in x).all()
        assert (g.candidates["early_shift_guard"] == guard).all()
    lr = cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], params=dataclasses.replace(p, oe_origin="LAST_RESET"))
    assert (lr.candidates["oe_origin"] == "LAST_RESET").all()
    with pytest.raises(ValueError):
        cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], params=dataclasses.replace(p, early_shift_guard="BOTH"))
