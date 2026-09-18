"""Phase 13C runner tests: the frozen rules must be enforced by code, not by discipline (D31-17 STEP 2)."""

from __future__ import annotations

import copy

import pandas as pd
import pytest

from cbr.engine import phase13c_run as p13c


def test_frozen_hashes_are_the_ones_the_owner_named():
    assert p13c.EXPECTED_HASHES["pc3_spec"].startswith("7032f400")
    assert p13c.EXPECTED_HASHES["pc2_spec"].startswith("4dadc8b9")
    assert p13c.EXPECTED_HASHES["parity_manifest"].startswith("a3ee0bd6")


def test_live_specs_still_match_the_frozen_hashes():
    from cbr.engine.params import spec_hash
    from cbr.engine.params_pc3 import spec_hash_pc3

    assert spec_hash_pc3() == p13c.EXPECTED_HASHES["pc3_spec"]
    assert spec_hash() == p13c.EXPECTED_HASHES["pc2_spec"]
    assert p13c.load_set()["manifest_hash"] == p13c.EXPECTED_HASHES["parity_manifest"]


def test_run_id_is_new():
    assert p13c.RUN_ID == "CBR-RUN-013C-1"
    assert p13c.RUN_ID not in {"CBR-RUN-013B-1", "CBR-RUN-013B-2"}


def test_p3_equivalence_window():
    within = pd.Timestamp("2025-10-21T01:39:35+00:00")      # 20s after Tom's entry, same 15m candle
    assert p13c.p3_equivalent(within, "CX-LT1-1", True)
    assert not p13c.p3_equivalent(within, "CX-LT1-1", False)            # wrong direction is never equivalent
    assert not p13c.p3_equivalent(pd.Timestamp("2025-10-21T01:29:00+00:00"), "CX-LT1-1", True)   # other 15m candle
    assert not p13c.p3_equivalent(pd.Timestamp("2025-10-21T01:44:00+00:00"), "CX-LT1-1", True)   # > 3 minutes
    assert not p13c.p3_equivalent(None, "CX-LT1-1", True)


def test_timing_bucket_and_condition_mappings_are_the_frozen_ones():
    assert p13c.TIMING_BUCKET == {37: (30, 45), 52: (45, 60)}           # M-5
    assert p13c.JOURNAL_CONDITION["Volume"] is None                     # M-4: Volume is NOT_SCORED
    assert p13c.JOURNAL_CONDITION["Trending"] == ["TRENDING_RANGE", "RANGE"]


def _stub_entry(hard_ok: bool, hours: int = 3) -> dict:
    case = {"case_id": "CX-LT1-1", "scoring_level": "ENTRY_LEVEL", "positive_or_negative": "POSITIVE",
            "scored_candidate": {"signal_id": "x"}, "scored_candidate_eligible": hard_ok,
            "dimensions": [{"n": i, "name": f"d{i}", "status": "MATCH", "class": None, "engine": None,
                            "expected": None, "note": None} for i in range(1, 10)],
            "hard_dimensions": {"model_family": True, "direction": True, "extension_direction": True,
                                "core_structural_trigger": hard_ok},
            "selection": {"structural_event_exists": hard_ok, "matching_ids": [], "frozen_selection_ids": [],
                          "p3_equivalent_candidates_any_eligibility": [], "classification": None},
            "per_variant": {}}
    hour = {"case_id": "JM", "scoring_level": "HOUR_LEVEL", "verdict": "HOUR_MATCH", "fields": [], "journal": {},
            "eligible_ids": [], "all_candidates": [], "scored_candidate": None, "frozen_selection": {}}
    cases = {}
    for cid in ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2"):
        cases[cid] = {**copy.deepcopy(case), "case_id": cid}
    cases["CX-LT3-1"] = {"case_id": "CX-LT3-1", "scoring_level": "ENTRY_LEVEL", "positive_or_negative": "NEGATIVE",
                         "result": "NO_ELIGIBLE_CANONICAL_SIGNAL", "eligible_signals": [],
                         "candidates_with_shift_in_window": [], "window_utc": ["", ""]}
    for i, cid in enumerate(("JM-2025-10-16", "JM-2025-10-17", "JM-2025-10-29")):
        cases[cid] = {**copy.deepcopy(hour), "case_id": cid,
                      "verdict": "HOUR_MATCH" if i < hours else "HOUR_MISMATCH"}
    return {"result_hash": "h", "payload": {"cases": cases}}


@pytest.mark.parametrize(("hard_ok", "hours", "expected"), [
    (True, 3, "PASS"),
    (True, 2, "PASS WITH CONCERNS"),        # D31-8: 2/3 caps at PASS WITH CONCERNS
    (True, 1, "FAIL"),                      # D31-8: 1/3 is a FAIL
    (True, 0, "FAIL"),
    (False, 3, "FAIL"),                     # A-1: the core trigger is a hard dimension
])
def test_verdict_rules_are_the_frozen_ones(hard_ok, hours, expected):
    run = _stub_entry(hard_ok, hours)
    assert p13c.verdict(run, run)["verdict"] == expected


def test_determinism_failure_is_a_fail():
    a, b = _stub_entry(True, 3), _stub_entry(True, 3)
    b["result_hash"] = "other"
    v = p13c.verdict(a, b)
    assert v["verdict"] == "FAIL" and not v["deterministic"]


def test_negative_control_signal_is_a_fail():
    run = _stub_entry(True, 3)
    run["payload"]["cases"]["CX-LT3-1"]["result"] = "ELIGIBLE_CANONICAL_SIGNAL_PRODUCED"
    assert p13c.verdict(run, run)["verdict"] == "FAIL"


def test_classified_mismatch_downgrades_but_does_not_fail():
    run = _stub_entry(True, 3)
    run["payload"]["cases"]["CX-TE1-1"]["dimensions"][4].update(status="MISMATCH", class_=None,
                                                                **{"class": "OWNER_BASELINE_CHOICE"})
    assert p13c.verdict(run, run)["verdict"] == "PASS WITH CONCERNS"


def test_eligibility_uses_the_engines_own_signal_rule():
    cands = pd.DataFrame([{"variant": "A", "event_at_trigger": "ARMED_AT_TRIGGER", "signal_id": "a"},
                          {"variant": "A", "event_at_trigger": "REJECTED_AT_TRIGGER", "signal_id": "b"},
                          {"variant": "B", "event_at_trigger": "ARMED_AT_TRIGGER", "signal_id": "c"}])
    assert list(p13c.eligible(cands, "A")["signal_id"]) == ["a"]
    assert list(p13c.eligible(cands, "B")["signal_id"]) == ["c"]


def test_narrative_set_is_qualitative_only():
    assert {a for a, _ in p13c.NARRATIVE_ASSESSMENT.values()} <= {"CONSISTENT", "INCONSISTENT", "NOT_DETERMINABLE"}
    assert len(p13c.NARRATIVE_ASSESSMENT) == 7
