"""D29-18: the PC3 records pin every file the PC3 engine reads, and PC2 stays byte-identical.

A failure means a pinned PC3 file changed after freezing (create PC4 and a new parity run), or that PC3 work touched a
PC2 file, which is not allowed.
"""

import hashlib
from pathlib import Path

import pytest
import yaml

from cbr.engine.freeze_specs_pc3 import CHANGES, MODELS, OUT_DIR, SUPERSEDES, VERSION
from cbr.engine.params import spec_hash
from cbr.engine.params_pc3 import SPEC_FILES_PC3, spec_hash_pc3

ROOT = Path(__file__).resolve().parents[2]
CLASSES = {"CANON_CORRECTION", "ASSUMPTION_CHANGE", "IMPLEMENTATION_FIX", "DIAGNOSTIC_ONLY", "NO_CHANGE"}


def _sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


@pytest.mark.parametrize("model", list(MODELS))
def test_pc3_record_is_frozen_and_unchanged(model):
    rec = yaml.safe_load((OUT_DIR / f"{model}-{VERSION}.yaml").read_text())
    assert rec["spec_version"] == f"{model}-{VERSION}" and rec["supersedes"] == f"{model}-{SUPERSEDES}"
    assert set(rec["spec_files"]) == set(SPEC_FILES_PC3)
    pinned = {**rec["spec_files"], **rec["evidence"], **rec["ruling_records"]}
    changed = [f for f, h in pinned.items() if _sha(f) != h]
    assert not changed, f"pinned files changed after freezing {rec['spec_version']}: {changed}"
    assert rec["spec_hash"] == spec_hash_pc3()
    assert rec["ruling"] == "D29" and rec["unresolved_assumptions"]
    assert "PHASE13C_PARITY_NOT_RUN" in rec["open_eligibility_blockers"]


@pytest.mark.parametrize("model", list(MODELS))
def test_every_pc3_change_is_classified_with_evidence(model):
    rec = yaml.safe_load((OUT_DIR / f"{model}-{VERSION}.yaml").read_text())
    ids = {c["id"] for c in rec["changes_from_pc2"]}
    assert ids == set(MODELS[model]["changes"])
    for c in rec["changes_from_pc2"]:
        assert c["classification"] in CLASSES and c["ruling"].startswith("D29")
        assert c["from_pc2"] and c["to_pc3"] and c["evidence"]
    flat = [i for v in rec["classification_summary"].values() for i in v]
    assert sorted(flat) == sorted(ids)


def test_pc2_records_are_untouched_by_pc3():
    for model in MODELS:
        pc2 = yaml.safe_load((OUT_DIR / f"{model}-PC2.yaml").read_text())
        assert pc2["spec_hash"] == spec_hash()                       # PC2's pinned files are byte-identical
        assert pc2["spec_version"].endswith("PC2")
    assert spec_hash() != spec_hash_pc3()                            # and the two candidates are distinct specs


def test_pc3_changes_cover_the_approved_rulings():
    """Every D29 rule decision appears in the change list with the classification the owner gave it."""
    expected = {"T3-1": "CANON_CORRECTION", "OE-2": "CANON_CORRECTION", "H-1": "CANON_CORRECTION",
                "H-2": "CANON_CORRECTION", "C04-1": "CANON_CORRECTION", "OQ-46": "CANON_CORRECTION",
                "ACT-1": "ASSUMPTION_CHANGE", "ACT-2": "ASSUMPTION_CHANGE", "ACT-3": "ASSUMPTION_CHANGE",
                "H-3": "IMPLEMENTATION_FIX", "OQ-09": "IMPLEMENTATION_FIX", "C04-D": "DIAGNOSTIC_ONLY",
                "D8": "NO_CHANGE", "W-1": "NO_CHANGE", "OQ-01": "NO_CHANGE", "OQ-47": "NO_CHANGE", "S-1": "NO_CHANGE"}
    got = {c["id"]: c["classification"] for c in CHANGES}
    assert got == expected
