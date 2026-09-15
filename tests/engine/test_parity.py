"""Phase 13 parity machinery (D19-7…14) on synthetic inputs only: no course-example scoring."""

import inspect

import numpy as np
import pandas as pd
import pytest

from cbr.engine import parity
from cbr.engine.params import load_cbr1h

T = lambda s: pd.Timestamp(s, tz="UTC")


def _cand(sid, ts, event, shift=None, activation=None, failed=(), variant="A"):
    return {"signal_id": sid, "timestamp": T(ts), "event": event, "variant": variant,
            "five_second_shift_time": None if shift is None else T(shift),
            "activation_time": T(activation or ts), "rules_failed": list(failed)}


def test_selection_never_takes_course_information():
    params = inspect.signature(parity.select_candidate).parameters
    assert list(params) == ["candidates", "variant", "params"]
    for fn in (parity.select_candidate, parity.selection_key, parity.rule_class):
        body = inspect.getsource(fn).split('"""')[-1].lower()             # code after the docstring
        assert not any(word in body for word in ("tom", "course", "example", "entry_price"))


def test_selection_orders_by_5s_shift_then_decision_then_id_within_a_variant():
    c = pd.DataFrame([
        _cand("A/2", "2025-10-21 01:30:00", "ARMED", shift="2025-10-21 01:36:00"),
        _cand("A/1", "2025-10-21 01:31:00", "ARMED", shift="2025-10-21 01:33:00"),   # later decision, earlier shift
        _cand("A/0", "2025-10-21 01:25:00", "ARMED"),                                # never shifted: last
        _cand("B/0", "2025-10-21 01:20:00", "ARMED", shift="2025-10-21 01:21:00", variant="B"),
    ])
    assert parity.select_candidate(c, "A")["selected"] == "A/1"
    assert parity.select_candidate(c, "B")["selected"] == "B/0"                      # variants never merged
    tie = pd.DataFrame([_cand("A/9", "2025-10-21 01:30", "ARMED", shift="2025-10-21 01:33"),
                        _cand("A/3", "2025-10-21 01:30", "ARMED", shift="2025-10-21 01:33")])
    assert parity.select_candidate(tie, "A")["selected"] == "A/3"


def test_no_eligible_candidate_scores_no_signal_with_a_labelled_diagnostic():
    p = load_cbr1h("A")
    c = pd.DataFrame([
        _cand("A/0", "2025-10-21 01:25", "REJECTED", shift="2025-10-21 01:26", failed=["IMPL-REWARD"]),
        _cand("A/1", "2025-10-21 01:30", "REJECTED", shift="2025-10-21 01:31", failed=["M1H-OE-02", "NT_INCOMPLETE_H"]),
    ])
    out = parity.select_candidate(c, "A", p)
    assert out["selected"] is None
    assert out["diagnostic_only"] == {"signal_id": "A/1", "label": "DIAGNOSTIC_ONLY",
                                      "failed_rules": ["M1H-OE-02", "NT_INCOMPLETE_H"]}


def test_views_baseline_and_one_ablation_at_a_time():
    p = load_cbr1h("A")
    assert parity.view_params(p, parity.BASELINE_SPEC) is p
    alts = parity.strict_course_ablations()
    assert alts == [{"oe_origin": "LAST_RESET"}, {"early_shift_guard": "FINAL_PUSH"}, {"early_shift_guard": "ALIGN_15M"}]
    assert parity.view_params(p, parity.STRICT_COURSE, {"oe_origin": "LAST_RESET"}).oe_origin == "LAST_RESET"
    for bad in ({}, {"oe_origin": "LAST_RESET", "early_shift_guard": "FINAL_PUSH"}, {"early_shift_guard": "BOTH"}):
        with pytest.raises(ValueError):
            parity.view_params(p, parity.STRICT_COURSE, bad)
    with pytest.raises(ValueError):
        parity.view_params(p, parity.BASELINE_SPEC, {"oe_origin": "LAST_RESET"})


def test_mismatch_gets_one_primary_class_in_order_and_bugs_stay_visible():
    E = parity.MismatchEvidence
    assert parity.classify_mismatch(E(data_limitation="gap", open_question="OQ-44"))["primary"] == "DATA_LIMITATION"
    out = parity.classify_mismatch(E(feed_difference="within tau", failing_spec_test="tests/x::y"))
    assert out["primary"] == "FEED_DIFFERENCE" and out["secondary"] == ["IMPLEMENTATION_BUG"]
    assert out["implementation_bug"] and out["blocks_gate"]
    assert parity.classify_mismatch(E(owner_baseline_choice="D8 LAST_RESET"))["primary"] == "OWNER_BASELINE_CHOICE"
    assert parity.classify_mismatch(E(canon_evidence="E1H-023 vs example"))["primary"] == "CANON_MISMATCH"
    with pytest.raises(ValueError):
        parity.classify_mismatch(E())
    assert parity.MISMATCH_ORDER == ["DATA_LIMITATION", "FEED_DIFFERENCE", "EXECUTION_DEPENDENT", "OWNER_BASELINE_CHOICE",
                                     "UNRESOLVED_SPEC_AMBIGUITY", "IMPLEMENTATION_BUG", "CANON_MISMATCH"]


def test_calibration_reports_offset_distribution_rounding_and_zero_lag():
    rng = np.random.default_rng(7)
    idx = pd.date_range(T("2030-01-02 00:00"), periods=600, freq="1min")
    walk = 2000 + np.cumsum(rng.normal(0, 0.5, len(idx)))
    dk = pd.DataFrame({"close": walk, "high": walk + 0.3, "low": walk - 0.3}, index=idx)
    noise = rng.uniform(-0.03, 0.03, (len(idx), 3))
    fx = pd.DataFrame({"close": walk + 0.40 + noise[:, 0], "high": walk + 0.70 + noise[:, 1],
                       "low": walk + 0.10 + noise[:, 2]}, index=idx)
    out = parity.calibrate(fx, dk, floor=0.02, percentile=95, round_to=0.05, feed_near_multiple=3)
    assert out["n_minutes"] == 600 and out["delta_median_offset"] == pytest.approx(0.40, abs=0.01)
    assert out["residual_max"] <= 0.061 and out["tau_price"] == pytest.approx(0.05)
    assert out["feed_near"] == pytest.approx(0.15) and out["zero_lag_confirmed"] is True
    lagged = fx.shift(1).dropna()
    assert parity.calibrate(lagged, dk, floor=0.02, percentile=95, round_to=0.05,
                            feed_near_multiple=3)["zero_lag_confirmed"] is False


def test_comparisons_and_final_run_is_refused_until_frozen():
    assert parity.compare_price(100.0, 100.43, delta=0.40, tau=0.05, feed_near=0.15) == "MATCH"
    assert parity.compare_price(100.0, 100.52, delta=0.40, tau=0.05, feed_near=0.15) == "FEED_NEAR"
    assert parity.compare_time(T("2025-10-21 01:39:30"), T("2025-10-21 01:39:15"), course_has_seconds=True) == "MATCH"
    assert parity.compare_time(T("2025-10-21 01:39:35"), T("2025-10-21 01:39:15"), course_has_seconds=True) == "MISMATCH"
    assert parity.compare_time(T("2025-10-21 01:39:59"), T("2025-10-21 01:39:02"), course_has_seconds=False,
                               one_minute_event=True) == "MATCH"
    tol = parity.load_tolerances()
    assert tol["status"] == "NOT_FROZEN" and tol["final_run_authorized"] is False
    assert all(v is None for v in tol["values"].values())
    with pytest.raises(SystemExit):
        parity.main()


def test_tradingview_csv_loader(tmp_path):
    f = tmp_path / "v.csv"
    f.write_text("time,open,high,low,close,Volume\n1761010740,1,2,0.5,1.5,3\n1761010800,1.5,2.5,1,2,4\n")
    out = parity.load_tradingview_csv(f)
    assert out.index[0] == T("2025-10-21 01:39") and list(out.columns) == ["open", "high", "low", "close"]
