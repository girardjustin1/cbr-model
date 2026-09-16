"""D30-11: the expanded parity set is frozen, complete and honest about what each case may score.

A failure means the manifest, a source or a market-data file changed after freezing; that needs a new manifest version,
not an edit.
"""

import json

import pytest

from cbr.engine.parity_set import MANIFEST, build

LEVELS = {"ENTRY_LEVEL", "HOUR_LEVEL", "NARRATIVE_ONLY"}
REQUIRED = {"case_id", "source", "evidence_level", "instrument", "model", "direction", "positive_or_negative",
            "session", "start_time", "end_time", "scoring_level", "source_hashes", "market_data_hashes",
            "fields_allowed_for_scoring"}
FROZEN_HASH = "a3ee0bd6ba225ce6b89d8bc61fbefd227ce8097a3f6bfac2f9414e19cd81ea9c"


@pytest.fixture(scope="module")
def manifest():
    return json.loads(MANIFEST.read_text())


def test_manifest_is_frozen_and_reproducible(manifest):
    assert manifest["manifest_hash"] == FROZEN_HASH
    assert build()["manifest_hash"] == FROZEN_HASH          # sources and market data unchanged since the freeze


def test_every_case_carries_the_required_fields(manifest):
    for c in manifest["cases"]:
        assert REQUIRED <= c.keys(), c["case_id"]
        assert c["scoring_level"] in LEVELS
        assert c["source_hashes"] and all(len(h) == 64 for h in c["source_hashes"].values())


def test_machine_cases_have_market_data_and_narrative_cases_do_not(manifest):
    for c in manifest["cases"]:
        if c["scoring_level"] == "NARRATIVE_ONLY":
            assert c["market_data_status"] == "NOT_REQUIRED" and not c["market_data_hashes"]
            assert c["fields_allowed_for_scoring"] == ["geometry_consistency_only"]
            assert "why_narrative" in c
        else:
            assert c["market_data_status"] == "COMPLETE", f"{c['case_id']} would be a DATA_LIMITATION case (D30-18)"
            assert c["market_data_hashes"] and c["data_span_utc"]


def test_hour_level_cases_never_claim_entry_level_fields(manifest):
    """D30-7: journal rows carry no entry, stop, target or 5s trigger, so those fields may not be scored."""
    forbidden = {"trigger_time", "trigger_price", "stop_anchor_concept", "target_concept", "type3_5s_trigger"}
    for c in manifest["cases"]:
        if c["scoring_level"] == "HOUR_LEVEL":
            assert not (set(c["fields_allowed_for_scoring"]) & forbidden), c["case_id"]
            assert not ({"entry", "stop", "target"} & c["stated"].keys()), c["case_id"]


def test_set_composition(manifest):
    assert manifest["counts"] == {"ENTRY_LEVEL": 4, "HOUR_LEVEL": 3, "NARRATIVE_ONLY": 7}
    machine = [c for c in manifest["cases"] if c["scoring_level"] != "NARRATIVE_ONLY"]
    assert sum(1 for c in machine if c["positive_or_negative"] == "NEGATIVE") == 1
    assert {c["instrument"] for c in machine} == {"XAUUSD"}          # no instrument entered research scope
    assert {c["session"] for c in machine} == {"ASIA", "LONDON"}     # the journal rows added a second session
