"""Phase 13D runner tests (D35): the frozen acceptance rules are enforced by code, not by discipline."""

from __future__ import annotations

import copy

import pytest

from cbr.engine import phase13d_run as p13d


def test_frozen_hashes_are_the_ones_the_owner_named():
    assert p13d.EXPECTED_HASHES["pc4_spec"].startswith("62a2310e")
    assert p13d.EXPECTED_HASHES["parity_manifest_v2"].startswith("e12f3882")
    assert p13d.EXPECTED_HASHES["pc3_spec"].startswith("7032f400")
    assert p13d.EXPECTED_HASHES["pc2_spec"].startswith("4dadc8b9")


def test_live_inputs_still_match_the_frozen_hashes():
    assert p13d.live_hashes() == p13d.EXPECTED_HASHES


def test_run_id_is_new():
    assert p13d.RUN_ID == "CBR-RUN-013D-1"
    assert p13d.RUN_ID not in {"CBR-RUN-013B-1", "CBR-RUN-013B-2", "CBR-RUN-013C-1"}


def test_binding_set_is_exactly_what_d35_approved():
    assert p13d.BINDING == ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2", "CX-LT3-1", "JM-2025-10-16")
    assert "JM-2025-10-17" not in p13d.BINDING and "JM-2025-10-29" not in p13d.BINDING


def test_hard_dimensions_are_the_eight_d35_named():
    assert p13d.HARD == ("model_family", "direction", "extension_direction", "extension_activation",
                         "location_or_previous_candle_event", "hvcs_state", "type3_5s_structural_trigger",
                         "eligible_candidate")
    assert "condition" not in p13d.HARD          # scored and classified, but not hard


def _stub(hard_ok: bool = True, hour_match: bool = True, negative_ok: bool = True, soft_mismatch: bool = False):
    entry = {"case_id": "X", "scoring_level": "ENTRY_LEVEL", "positive_or_negative": "POSITIVE", "view": "STRICT",
             "scored_candidate": {"signal_id": "x"}, "scored_candidate_eligible": hard_ok,
             "dimensions": [{"n": i, "name": n, "status": "MATCH", "class": None, "engine": None, "expected": None,
                             "note": None, "hard": n in p13d.HARD}
                            for i, n in enumerate(["model_family", "direction", "condition", "extension_direction",
                                                   "extension_activation", "location_or_previous_candle_event",
                                                   "hvcs_state", "type3_5s_structural_trigger",
                                                   "eligible_candidate"], start=1)],
             "hard_dimensions": dict.fromkeys(p13d.HARD, True),
             "selection": {"a_structural_event_exists": True, "b_eligible_expected_event_exists": True,
                           "c_frozen_selection": [], "matching_ids": [], "classification": None},
             "per_variant": {}}
    if not hard_ok:
        entry["hard_dimensions"]["eligible_candidate"] = False
    if soft_mismatch:
        entry["dimensions"][2].update(status="MISMATCH", **{"class": "OWNER_BASELINE_CHOICE"})
    cases = {cid: {**copy.deepcopy(entry), "case_id": cid} for cid in p13d.ENTRY_POSITIVES}
    cases[p13d.NEGATIVE] = {"case_id": p13d.NEGATIVE, "scoring_level": "ENTRY_LEVEL",
                            "positive_or_negative": "NEGATIVE", "view": "STRICT",
                            "result": "NO_ELIGIBLE_CANONICAL_SIGNAL" if negative_ok
                            else "ELIGIBLE_CANONICAL_SIGNAL_PRODUCED",
                            "eligible_signals": [], "candidates_with_shift_in_window": [], "window_utc": ["", ""]}
    cases[p13d.HOUR_CASE] = {"case_id": p13d.HOUR_CASE, "scoring_level": "HOUR_LEVEL", "view": "STRICT",
                             "verdict": "HOUR_MATCH" if hour_match else "HOUR_MISMATCH",
                             "fields": [{"field": "direction", "status": "MATCH" if hour_match else "MISMATCH",
                                         "engine": None, "expected": None, "note": None}],
                             "journal": {}, "eligible_ids": [], "all_candidates": [], "scored_candidate": None,
                             "frozen_selection": {}}
    return {"result_hash": "h", "payload": {"cases": cases}}


@pytest.mark.parametrize(("hard_ok", "hour_match", "negative_ok", "expected"), [
    (True, True, True, "PASS"),
    (True, False, True, "PASS WITH CONCERNS"),     # E-2: 0/1 caps but never fails on its own
    (False, True, True, "FAIL"),                   # an entry-level hard gate fails
    (False, False, True, "FAIL"),
    (True, True, False, "FAIL"),                   # the control admits the rejected setup
])
def test_verdict_rules_are_the_frozen_ones(hard_ok, hour_match, negative_ok, expected):
    run = _stub(hard_ok=hard_ok, hour_match=hour_match, negative_ok=negative_ok)
    assert p13d.verdict(run, run)["verdict"] == expected


def test_the_journal_case_can_never_rescue_an_entry_level_failure():
    """D35 §5: a 1/1 journal match does not compensate for an entry-level or control failure."""
    assert p13d.verdict(*(2 * [_stub(hard_ok=False, hour_match=True)]))["verdict"] == "FAIL"
    assert p13d.verdict(*(2 * [_stub(negative_ok=False, hour_match=True)]))["verdict"] == "FAIL"


def test_a_classified_non_hard_mismatch_downgrades_but_does_not_fail():
    run = _stub(soft_mismatch=True)
    v = p13d.verdict(run, run)
    assert v["verdict"] == "PASS WITH CONCERNS" and v["concerns"]


def test_determinism_failure_is_a_fail():
    a, b = _stub(), _stub()
    b["result_hash"] = "other"
    v = p13d.verdict(a, b)
    assert v["verdict"] == "FAIL" and not v["deterministic"]


def test_hour_mismatch_is_reported_classified_and_retained():
    run = _stub(hour_match=False)
    v = p13d.verdict(run, run)
    assert any("HOUR_MISMATCH" in c for c in v["concerns"])
    assert v["hour_level"] == "0/1 HOUR_MATCH"
