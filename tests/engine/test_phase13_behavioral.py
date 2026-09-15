"""Phase 13 behavioral-parity run machinery (CBR-PROT-013B, D25) on synthetic inputs only: no course-example scoring."""

import inspect
import json

import pandas as pd
import pytest
import yaml

from cbr.engine import parity
from cbr.engine import phase13_behavioral as pb
from cbr.engine.params import load_cbr1h, spec_hash
from cbr.structure import overextension as oe_mod

T = lambda s: pd.Timestamp(s, tz="UTC")


def test_run_spec_freezes_the_d25_rulings():
    spec = pb.load_spec()
    assert spec["recent_feed_comparison"]["days"] == ["2026-09-09", "2026-09-10", "2026-09-11", "2026-09-14"]
    assert {k: v["role"] for k, v in spec["examples"].items()} == {
        "CX-LT1-1": "POSITIVE", "CX-TE1-1": "POSITIVE", "CX-LT3-2": "POSITIVE", "CX-LT3-1": "NEGATIVE_CONTROL"}
    pc2 = yaml.safe_load((pb.ROOT / spec["spec_under_test"]["record"]).read_text())
    assert spec["spec_under_test"]["spec_hash"] == pc2["spec_hash"] == spec_hash()
    assert spec["views"]["STRICT_COURSE"] == parity.strict_course_ablations()           # pre-registered D8/D9 only
    assert spec["structural_event_match"]["max_abs_time_difference_minutes"] == 3
    assert (spec["feed_band"]["floor_usd"], spec["feed_band"]["residual_percentile"], spec["feed_band"]["round_up_to_usd"]) == (0.02, 95, 0.05)
    assert spec["examples"]["CX-LT3-2"]["accepted_conditions"] == [{"condition": "TRENDING_RANGE", "direction": "UP"}]
    assert spec["examples"]["CX-LT3-1"]["control_window_utc"] == ["2025-11-10T01:28:00+00:00", "2025-11-10T01:36:00+00:00"]
    order = spec["classification"]["order"]
    assert order.index("FEED_DEPENDENT_SIGNAL_DIFFERENCE") == order.index("FEED_DIFFERENCE") + 1
    assert [c for c in order if c != "FEED_DEPENDENT_SIGNAL_DIFFERENCE"] == parity.MISMATCH_ORDER[:4] + parity.MISMATCH_ORDER[4:]


def test_frozen_files_exist_and_include_selection_and_run_code():
    for f in pb.FROZEN_FILES:
        assert (pb.ROOT / f).exists(), f
    assert "src/cbr/engine/parity.py" in pb.FROZEN_FILES and "config/phase13_behavioral_run.yaml" in pb.FROZEN_FILES


def _cand(sid, ts, event, shift=None, variant="A", failed=()):
    return {"signal_id": sid, "timestamp": T(ts), "event": event, "variant": variant, "activation_time": T(ts),
            "five_second_shift_time": None if shift is None else T(shift), "rules_failed": list(failed)}


def test_evaluated_candidate_follows_the_protocol_order_without_course_input():
    assert list(inspect.signature(pb.evaluated_candidate).parameters) == ["cands", "variant", "params"]
    p = load_cbr1h("A")
    c = pd.DataFrame([_cand("A/0", "2030-01-08 01:30", "REJECTED", "2030-01-08 01:31", failed=["M1H-COND-01"]),
                      _cand("A/1", "2030-01-08 01:35", "ARMED", "2030-01-08 01:37")])
    assert pb.evaluated_candidate(c, "A", p)[0]["signal_id"] == "A/1" and pb.evaluated_candidate(c, "A", p)[1] == "SELECTED_ARMED"
    d = pd.DataFrame([_cand("A/0", "2030-01-08 01:30", "REJECTED", "2030-01-08 01:31", failed=["M1H-COND-01"]),
                      _cand("A/1", "2030-01-08 01:35", "REJECTED", "2030-01-08 01:37", failed=["M1H-6A-1-HVCS-INTO-SHIFT"])])
    assert pb.evaluated_candidate(d, "A", p)[1] == "DIAGNOSTIC_ONLY" and pb.evaluated_candidate(d, "A", p)[0]["signal_id"] == "A/1"
    e = d.assign(rules_failed=[["M1H-COND-01"], ["M1H-LOC-01"]])
    assert pb.evaluated_candidate(e, "A", p)[1] == "DIAGNOSTIC_FIRST_IN_ORDER" and pb.evaluated_candidate(e, "A", p)[0]["signal_id"] == "A/0"
    assert pb.evaluated_candidate(e, "B", p) == (None, "NO_CANDIDATE")


def test_classify_inserts_feed_dependent_after_feed_difference():
    ev = parity.MismatchEvidence(owner_baseline_choice="x", canon_evidence="E1H-018")
    assert pb.classify(ev)["primary"] == parity.classify_mismatch(ev)["primary"] == parity.OWNER_BASELINE_CHOICE
    k = pb.classify(ev, "margin within τ", ["UNVERIFIED", "DATA_LIMITATION"])
    assert k["primary"] == pb.FDSD and k["secondary"] == [parity.OWNER_BASELINE_CHOICE, parity.CANON_MISMATCH]
    assert k["tags"] == ["UNVERIFIED", "DATA_LIMITATION"]
    assert pb.classify(parity.MismatchEvidence(feed_difference="p3"), "m")["primary"] == parity.FEED_DIFFERENCE
    bug = pb.classify(parity.MismatchEvidence(data_limitation="d", failing_spec_test="test_x"), "m")
    assert bug["primary"] == parity.DATA_LIMITATION and bug["implementation_bug"]              # never concealed


EX = {"direction": "BUY", "tom_time_utc": ["2030-01-08T01:39:15+00:00", "2030-01-08T01:39:15+00:00"], "time_tolerance_s": 15,
      "entry_15m_candle_utc": "2030-01-08T01:30:00+00:00"}


def test_shift_time_tolerance_and_p3_equivalence():
    spec = pb.load_spec()
    assert pb.time_status(T("2030-01-08 01:39:30"), EX) and not pb.time_status(T("2030-01-08 01:39:31"), EX)
    eq = pb.p3_equivalent(T("2030-01-08 01:42:15"), EX, True, spec)
    assert eq["equivalent"] and eq["distance_to_tom_interval_s"] == 180
    assert not pb.p3_equivalent(T("2030-01-08 01:42:16"), EX, True, spec)["equivalent"]           # > 3 min
    assert not pb.p3_equivalent(T("2030-01-08 01:29:59"), {**EX, "tom_time_utc": ["2030-01-08T01:31:00+00:00"] * 2},
                                True, spec)["equivalent"]                                        # other 15m candle
    assert not pb.p3_equivalent(T("2030-01-08 01:40:00"), EX, False, spec)["equivalent"]          # direction
    assert pb.p3_equivalent(None, EX, True, spec) == {"equivalent": False, "reason": "no completed shift"}


def _dim(n, status, klass=None):
    return {"dim": n, "status": status, "class": {pb.MATCH: pb.BM, pb.FEED: pb.FEED}.get(status, klass)}


def test_core_structural_trigger_needs_shift_type_and_equivalent_time():
    base = [_dim(1, pb.MATCH), _dim(2, pb.MATCH), _dim(5, pb.MATCH), _dim(8, pb.MATCH)]
    assert pb.hard_dimensions(base + [_dim(9, pb.FEED)])["core_structural_trigger"]["met"]
    miss = pb.hard_dimensions(base + [_dim(9, pb.MISMATCH, parity.OWNER_BASELINE_CHOICE)])["core_structural_trigger"]
    assert not miss["met"] and miss["class"] == parity.OWNER_BASELINE_CHOICE
    no_shift = pb.hard_dimensions([_dim(1, pb.MATCH), _dim(2, pb.MATCH), _dim(5, pb.MATCH),
                                   _dim(8, pb.MISMATCH, parity.UNRESOLVED_SPEC_AMBIGUITY), _dim(9, pb.MISMATCH, "x")])
    assert no_shift["core_structural_trigger"] == {"met": False, "class": parity.UNRESOLVED_SPEC_AMBIGUITY}


def test_example_verdict_takes_the_most_severe_class_and_ignores_dxy():
    spec = pb.load_spec()
    dims = [_dim(1, pb.MATCH), _dim(9, pb.FEED), {"dim": 12, "status": pb.MISMATCH, "class": parity.CANON_MISMATCH,
                                                   "descriptive": True}]
    assert pb.example_verdict(dims, [], spec) == pb.BMFD
    acc = [{"rule": "M1H-COND-04", "classification": {"primary": parity.UNRESOLVED_SPEC_AMBIGUITY}}]
    assert pb.example_verdict(dims, acc, spec) == parity.UNRESOLVED_SPEC_AMBIGUITY
    dl = [{"dim": 10, "status": pb.MISMATCH, "class": parity.DATA_LIMITATION}]
    assert pb.example_verdict(dims + dl, [], spec) == parity.UNRESOLVED_SPEC_AMBIGUITY
    assert pb.example_verdict(dims + [{"dim": 3, "status": pb.MISMATCH, "class": pb.FDSD}], acc, spec) == pb.FDSD


def test_oe_pullback_margin_sign_agrees_with_the_overextension_rule():
    from cbr.data import price_series as ps
    from tests.test_feed_comparison import _walk
    s5 = _walk("2030-01-08 00:00", 720 * 6, seed=11)
    s1 = ps.rollup_structure(s5, "1min")
    p = load_cbr1h("A")
    agree = 0
    for h in pd.date_range(T("2030-01-08 02:00"), T("2030-01-08 05:00"), freq="1h", inclusive="left"):
        for mm in (20, 30, 40, 50):
            as_of = h + pd.Timedelta(minutes=mm)
            oe = oe_mod.evaluate(s1, h, float(s1.loc[h, "open"]), as_of, atr_1m=1.0, activation_atr=p.activation_atr,
                                 pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac)
            m = pb.oe_pullback_margin(s1, h, float(s1.loc[h, "open"]), as_of, 1.0, p)
            if m is not None:
                assert (m >= 0) == oe.no_pullback or m == 0, (h, mm, m, oe.no_pullback)
                agree += 1
    assert agree > 5


def _payload(hard_met=True, hard_class=pb.BM, dims_class=pb.BM, event="ARMED", neg="NO_ELIGIBLE_CANONICAL_SIGNAL",
             c9="MET"):
    hard = {h: {"met": hard_met, "class": hard_class} for h in pb.HARD}
    v = {"dimensions": [{"dim": 3, "name": "condition", "class": dims_class, "status": "x"}],
         "acceptance": {"event": event, "failed_rules": []}, "causality": {"checked": True, "all_identical": True}}
    ex = {"scored_variant": "A", "hard_met": hard, "variants": {"A": v}}
    return {"payload": {"engine_run_determinism": {"k": {"identical": True}}, "pc2_spec_hash": spec_hash(),
                        "examples": {"CX-LT1-1": ex}, "negative_control": {"result": neg, "eligible_signals": []},
                        "recent_feed_comparison": {"criterion_9": {"status": c9, "fail_evidence": [], "concerns": []}}},
            "result_hash": "h"}


def test_verdict_rules():
    spec = pb.load_spec()
    assert pb.verdict(_payload(), _payload(), spec)["verdict"] == "PASS"
    assert pb.verdict(_payload(), {**_payload(), "result_hash": "other"}, spec)["verdict"] == "FAIL"
    assert pb.verdict(_payload(dims_class=pb.FEED), _payload(), spec)["verdict"] == "PASS WITH CONCERNS"
    assert pb.verdict(_payload(event="REJECTED"), _payload(), spec)["verdict"] == "PASS WITH CONCERNS"
    obc = _payload(hard_met=False, hard_class=parity.OWNER_BASELINE_CHOICE)
    assert pb.verdict(obc, obc, spec)["verdict"] == "OWNER_DETERMINATION_REQUIRED"
    canon = _payload(hard_met=False, hard_class=parity.CANON_MISMATCH)
    assert pb.verdict(canon, canon, spec)["verdict"] == "FAIL"
    assert pb.verdict(_payload(c9="FAIL_EVIDENCE"), _payload(), spec)["verdict"] == "FAIL"
    assert pb.verdict(_payload(c9="CONCERN"), _payload(), spec)["verdict"] == "PASS WITH CONCERNS"
    neg = _payload(neg="ELIGIBLE_CANONICAL_SIGNAL_PRODUCED")
    assert pb.verdict(neg, neg, spec)["verdict"] == "PASS WITH CONCERNS"


def test_verify_freeze_detects_a_changed_input(tmp_path, monkeypatch):
    f = tmp_path / "frozen.txt"
    f.write_text("a")
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps({"files": {str(f): pb.sha(f)}, "pc2": {"spec_files": {}, "selection_protocol": {},
                                                                      "spec_hash": spec_hash()}, "forexcom_exports": {}}))
    monkeypatch.setattr(pb, "FREEZE_MANIFEST", man)
    assert pb.verify_freeze()["files"]
    f.write_text("b")
    with pytest.raises(SystemExit, match="changed after the freeze"):
        pb.verify_freeze()


def test_freeze_refuses_when_already_frozen(tmp_path, monkeypatch):
    man = tmp_path / "manifest.json"
    man.write_text("{}")
    monkeypatch.setattr(pb, "FREEZE_MANIFEST", man)
    monkeypatch.setattr(pb, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="already frozen"):
        pb.freeze(pytest_summary="n/a")


def test_js_is_deterministic_and_json_safe():
    obj = {"t": T("2030-01-08 01:00"), "nan": float("nan"), "l": (1, 2.5), "d": pd.Timedelta(seconds=90)}
    assert pb.js(obj) == {"t": "2030-01-08T01:00:00+00:00", "nan": None, "l": [1, 2.5], "d": 90.0}
    assert pb.payload_hash(obj) == pb.payload_hash(dict(reversed(list(obj.items()))))


def test_end_to_end_pipeline_on_synthetic_data(monkeypatch):
    """Engine runs → evaluated candidates → dimensions → classification → negative control → verdict → Markdown, on a
    synthetic series with a synthetic 'course' record (crash and schema check; no course window is touched)."""
    import copy

    from cbr.data import feed_comparison as fc
    from cbr.data import price_series as ps
    from cbr.engine import phase13_report as rep
    from tests.test_feed_comparison import _walk

    from zoneinfo import ZoneInfo

    s5 = _walk("2030-01-08 00:00", 2 * 24 * 720, seed=5)
    s1 = ps.rollup_structure(s5, "1min")[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]
    for frame in (s5, s1):                                           # stored parquet bars: ms unit, ZoneInfo("UTC")
        frame.index = frame.index.tz_convert(ZoneInfo("UTC")).as_unit("ms")
    monkeypatch.setattr(pb.cb, "load_structure", lambda a, b, bar: (s1 if bar == "1m" else s5)[
        lambda d: (d.index >= a) & (d.index < b)])
    course = {"example_id": "SYN-1", "mtf_model": {"value": "range", "timestamp": "0"}, "overextension": {"value": "x"},
              "fifteen_min_cb": {"value": "took low"}, "entry_model": {"value": "seconds shift"},
              "cb_hour_timing": {"value": "37"}, "target_description": {"value": "50%"}}
    monkeypatch.setattr(pb, "course_record", lambda ex_id: {**course, "example_id": ex_id})
    monkeypatch.setattr(pb, "dxy_at", lambda t, field, htf: {"time": str(t), "field": field, "value": "UP"})
    spec = copy.deepcopy(pb.load_spec())
    spec["engine_run_repeats"] = 1
    x = {**spec["examples"]["CX-LT1-1"], "hour_utc": "2030-01-09T09:00:00+00:00",
         "data_span_utc": ["2030-01-08T00:00:00+00:00", "2030-01-09T11:00:00+00:00"],
         "tom_time_utc": ["2030-01-09T09:39:15+00:00"] * 2, "entry_15m_candle_utc": "2030-01-09T09:30:00+00:00"}
    neg = {**spec["examples"]["CX-LT3-1"], "hour_utc": x["hour_utc"], "data_span_utc": x["data_span_utc"],
           "control_window_utc": ["2030-01-09T09:22:00+00:00", "2030-01-09T09:52:00+00:00"]}
    p = load_cbr1h("A")
    er = pb.engine_runs(x, spec)
    assert len(er["runs"]) == 8 and all(r["identical"] for r in er["runs"].values())
    ex = pb.evaluate_example("SYN-1", x, er, spec, p, 0.05, {"delta_h": 0.1, "dxy_1h": []})
    assert ex["scored_variant"] in ("A", "B") and set(ex["hard_met"]) == set(pb.HARD)
    for vv in ex["variants"].values():
        for d in vv["dimensions"]:
            assert d["status"] in (pb.MATCH, pb.FEED, pb.MISMATCH, pb.NA)
            assert d["status"] in (pb.MATCH, pb.FEED, pb.NA) or d["classification"]["primary"]
        for a in vv["acceptance"]["failed_rules"]:
            assert a["classification"]["primary"] in spec["classification"]["order"]
    nc = pb.negative_control("SYN-NEG", neg, er, spec)
    assert nc["result"] in ("NO_ELIGIBLE_CANONICAL_SIGNAL", "ELIGIBLE_CANONICAL_SIGNAL_PRODUCED")
    minutes = fc.comparison_minutes(["2030-01-08", "2030-01-09"], T("2030-01-08 01:00"))
    dk1m = fc.restrict(s1, minutes)
    study = fc.compare_recent(dk1m + 0.2, dk1m, minutes, p, exports={"5m": fc.rollup(dk1m, "5min"), "15m": fc.rollup(dk1m, "15min")},
                              band={"floor_usd": 0.02, "residual_percentile": 95, "round_up_to_usd": 0.05},
                              hour_minutes=[25, 35, 45], count_margin=pd.Timedelta(hours=2))
    study["data_validation"] = {}
    study["criterion_9"] = fc.criterion_9(study, spec["criterion_9"]["core_concepts"], 0.5, 0.8)
    payload = {"pc2_spec_hash": spec_hash(), "examples": {"SYN-1": ex}, "negative_control": nc,
               "engine_run_determinism": {"k": {"identical": True}}, "recent_feed_comparison": study}
    run = {"result_hash": pb.payload_hash(payload), "payload": pb.js(payload), "generated_utc": "t"}
    json.dumps(run)
    v = pb.verdict(run, run, spec)
    assert v["verdict"] in ("PASS", "PASS WITH CONCERNS", "FAIL", "OWNER_DETERMINATION_REQUIRED")
    head = {"run_id": "SYN", "generated_utc": "t", "freeze_commit": "0" * 40}
    manifest = {"protocol_sha256": "p", "run_spec_sha256": "r", "ruling_sha256": "d", "pc2": {"spec_hash": spec_hash()},
                "freeze_commit": "0" * 40, "frozen_utc": "t", "pre_execution_tests": "n/a",
                "data_hashes": {"course_structure_bars": {}, "recent_ticks": {}, "recent_structure_bars": {}, "dxy_candles": {}},
                "forexcom_exports": {}, "result_hashes": {"run-1": "h", "run-2": "h"}, "deterministic_rerun": True}
    md = rep.render_parity({**head, "verdict": v, **pb.js({"examples": {"SYN-1": ex}, "negative_control": nc,
                                                         "engine_run_determinism": {"k": {"identical": True}}})},
                           manifest, pb.js({**head, **study}), spec)
    assert "## 12. Verdict" in md and "SYN-1" in md
    assert "Criterion 9" in rep.render_feed(pb.js({**head, **study}), {**spec, "recent_feed_comparison": {
        **spec["recent_feed_comparison"], "days": ["2030-01-08"]}})


def test_htf_example_on_synthetic_exports():
    from cbr.data import feed_comparison as fc
    from cbr.data import price_series as ps
    from cbr.engine import phase13_report as rep
    from tests.test_feed_comparison import _walk

    s5 = _walk("2030-01-08 00:00", 2 * 24 * 720, seed=9)
    s1 = ps.rollup_structure(s5, "1min")[["open", "high", "low", "close"]]
    h1 = fc.rollup(s1, "1h") + 0.3
    four = fc.rollup(s1.shift(freq="2h"), "4h").shift(freq="-2h") + 0.3                 # 22/02/06… UTC alignment
    day = fc.rollup(s1.shift(freq="2h"), "1D").shift(freq="-2h") + 0.3
    out = fc.htf_example(T("2030-01-09 09:00"), s1, {"1h": h1, "4h": four, "1D": day}, 3, 12)
    assert out["delta_h"] == pytest.approx(0.3)
    assert all(r["offsets"]["high"] == pytest.approx(0.3) for r in out["1h"] if "offsets" in r)
    full4 = [r for r in out["4h"] if "offsets" in r]
    assert full4 and all(r["extreme_hours_agree"] is True for r in full4)
    out["dxy_1h"] = fc.dxy_example(T("2030-01-09 09:00"), h1, s1, 3)
    md = rep.render_htf(pb.js({"run_id": "SYN", "generated_utc": "t", "examples": {"SYN": out}}))
    assert "SYN" in md and "4h bars" in md
