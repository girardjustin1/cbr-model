"""CBR1H_BASELINE_V1 reference engine (Phase 12): HILO arms, guards, causality, determinism, ledger, hourly state."""

import pandas as pd
import pytest

from cbr.data import price_series as ps
from cbr.engine import cbr1h

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
    cut = T("2025-10-24 04:36")
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
              "M1H-OE-04b", "M1H-6A-1-HVCS", "M1H-6A-2-PREV-BREAK", "M1H-6A-3-NEW-EXTREME-IN-Q", "M1H-6A-4-HILO-TIER",
              "M1H-TIME-01", "NT_SYDNEY", "NT_ROLLOVER", "NT_INCOMPLETE_H", "IMPL-REWARD"}
    assert all(needed <= set(rules) for rules in c["rules"])


def test_hourly_state_is_causal_and_drives_the_15m_veto(run_a):
    s1, s5, r = run_a
    as_of = T("2025-10-24 04:30")
    states = cbr1h.hourly_state(r, as_of)
    assert all(s["decision_time"] <= as_of for s in states)
    k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= as_of], s5[s5.index + pd.Timedelta(seconds=5) <= as_of]
    trunc = cbr1h.run_cbr1h(k1, k5, start=SPAN[2], end=SPAN[3], variant="A")
    ids = lambda xs: sorted((s["signal_id"], s["state"]) for s in xs)
    pick = [s for s in states if s["state"] in ("ACTIVE", "PENDING", "TRIGGER_TOUCHED_FILL_UNKNOWN", "ENDED")]
    assert ids([s for s in cbr1h.hourly_state(trunc, as_of)]) == ids(pick)   # same state from data known at as_of
    provider = cbr1h.htf_provider(r)
    assert provider(as_of, "SELL") in ("VETO", "CLEAR", "NOT_EVALUATED")
    with pytest.raises(ValueError):
        cbr1h.htf_provider(cbr1h.run_cbr1h(s1, s5, start=SPAN[2], end=SPAN[3], variant="B"))
