"""D34 §9-12: the corrected parity set is frozen, carries every required field, and only CONFIRMED_CBR1H binds.

The v1 manifest that CBR-RUN-013C-1 was scored against must stay byte-identical.
"""

import hashlib
import json
from pathlib import Path

import pytest

from cbr.engine.parity_set import MANIFEST as MANIFEST_V1
from cbr.engine.parity_set_v2 import MANIFEST_V2, REQUIRED, V1_HASH

ROOT = Path(__file__).resolve().parents[2]
FROZEN_V2_HASH = "e12f3882f01b8ac4655520f00d5cd19829da989a371a1feb15b070d1a718804e"


def v2() -> dict:
    return json.loads(MANIFEST_V2.read_text())


def test_v1_manifest_is_untouched():
    assert json.loads(MANIFEST_V1.read_text())["manifest_hash"] == V1_HASH


def test_v2_manifest_is_frozen():
    m = v2()
    assert m["manifest_version"] == "v2" and m["supersedes"]["hash"] == V1_HASH
    body = {k: v for k, v in m.items() if k != "manifest_hash"}
    assert hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest() == m["manifest_hash"]
    assert m["manifest_hash"] == FROZEN_V2_HASH


def test_every_binding_case_has_the_required_fields():
    for case in v2()["cases"]:
        if not case["binds_verdict"]:
            continue
        for field in REQUIRED:
            assert case.get(field) not in (None, {}, []), f"{case['case_id']} missing {field}"


def test_only_confirmed_cbr1h_binds():
    for case in v2()["cases"]:
        if case["binds_verdict"]:
            assert case["model_scope"] == "CONFIRMED_CBR1H", case["case_id"]


def test_the_binding_set_is_exactly_what_d34_approved():
    m = v2()
    assert m["binding_case_ids"] == ["CX-LT1-1", "CX-TE1-1", "CX-LT3-2", "CX-LT3-1", "JM-2025-10-16"]
    assert m["counts"] == {"binding_entry_level": 4, "binding_hour_level": 1, "narrative_only": 11}


@pytest.mark.parametrize(("case_id", "scope"), [("JM-2025-10-17", "IFS_NOT_IMPLEMENTED"),
                                                ("JM-2025-10-29", "SOURCE_AMBIGUITY")])
def test_the_removed_journal_cases_are_preserved_not_deleted(case_id, scope):
    case = next(c for c in v2()["cases"] if c["case_id"] == case_id)
    assert case["binds_verdict"] is False and case["model_scope"] == scope
    assert case["correction"]["classification"] == "PARITY_SET_CORRECTION"
    assert case["correction"]["reason"] and case["correction"]["preserved_for"]
    assert case["stated"], "the source material must be preserved"


def test_the_oq48_evidence_examples_never_bind():
    """HX-1 / HX-2 resolved OQ-48; scoring the rule they settled would be circular."""
    for case_id in ("HX-1", "HX-2"):
        case = next(c for c in v2()["cases"] if c["case_id"] == case_id)
        assert case["binds_verdict"] is False and case["scoring_level"] == "NARRATIVE_ONLY"
        assert case["why_not_binding"]


def test_pinned_files_have_not_changed():
    for case in v2()["cases"]:
        for path, digest in {**case["market_data_hashes"], **case["source_hashes"],
                             **case["evidence_hashes"]}.items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
