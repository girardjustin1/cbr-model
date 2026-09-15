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


def _row(**kw):
    base = {"direction": "SELL", "entry_trigger_time": T("2025-10-21 00:08"), "cancel_time": T("2025-10-21 00:15"),
            "entry_reference_price": 99.9, "stop_extension_extreme": 101.0, "stop_buffer_price": 0.1,
            "target_price": 99.0}
    base.update(kw)
    return pd.Series(base)


def _bars5(rows, start="2025-10-21 00:08"):
    idx = pd.date_range(T(start), periods=len(rows), freq="5s")
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


def test_structure_outcome_touch_then_target_and_stop_first_on_same_bar():
    p = load_cbr15()
    target_first = _bars5([(100, 100, 99.85, 99.9), (99.9, 99.95, 99.5, 99.6), (99.6, 99.6, 98.9, 99.0)])
    assert cbr15._structure_outcome(_row(), target_first, p)[0] == "TARGET"
    both = _bars5([(100, 100, 99.85, 99.9), (99.9, 101.2, 98.9, 99.0)])
    assert cbr15._structure_outcome(_row(), both, p)[0] == "STOP"          # same bar: stop first (spec §8 IMPL)
    never = _bars5([(100, 100.2, 99.95, 100.1)] * 3)
    assert cbr15._structure_outcome(_row(), never, p)[0] == "NO_TOUCH"


def test_prior_rule_counts_only_setups_resolved_before_candle_open():
    p = load_cbr15()
    q = T("2025-10-21 01:00")
    ok_rules = {"M15-COND-01": True}
    cand = pd.DataFrame([
        {"candle_open_utc": T("2025-10-21 00:15"), "timestamp": T("2025-10-21 00:20"), "direction": "SELL",
         "variant": "base", "rules": dict(ok_rules), "raw_setup": True, "raw_outcome": "TARGET",
         "raw_resolved_utc": T("2025-10-21 00:40")},
        {"candle_open_utc": T("2025-10-21 00:30"), "timestamp": T("2025-10-21 00:35"), "direction": "SELL",
         "variant": "base", "rules": dict(ok_rules), "raw_setup": True, "raw_outcome": "TARGET",
         "raw_resolved_utc": T("2025-10-21 01:05")},                   # resolves after Q opens: not known yet
        {"candle_open_utc": q, "timestamp": T("2025-10-21 01:09"), "direction": "BUY", "variant": "base",
         "rules": dict(ok_rules), "raw_setup": False, "raw_outcome": None, "raw_resolved_utc": pd.NaT},
    ])
    cand["raw_resolved_utc"] = pd.to_datetime(cand["raw_resolved_utc"], utc=True)
    cbr15._apply_prior_rule(cand, p)
    last = cand.iloc[-1]
    assert last["prior_played_out_60m"] == 1 and last["rules"]["M15-COND-03"] is True and last["event"] == "ARMED"


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
    assert (c["htf_state"] == "NOT_EVALUATED").all()                  # Phase 12 dependency (OQ-34)


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
    assert c["eligibility_blockers"].map(lambda b: cbr15.BLOCKER_HTF in b and cbr15.BLOCKER_OQ36 in b).all()
