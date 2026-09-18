"""D34-14: the PC4 records pin every file the PC4 engine reads, and PC2 and PC3 stay byte-identical.

A failure means a pinned PC4 file changed after freezing (which needs a new candidate and a new ruling), or that PC4
work touched a PC2 or PC3 file, which is not allowed.
"""

import hashlib
from pathlib import Path

import pytest
import yaml

from cbr.engine.freeze_specs_pc4 import CHANGES, MODELS, OUT_DIR, SUPERSEDES, VERSION
from cbr.engine.params import spec_hash
from cbr.engine.params_pc3 import spec_hash_pc3
from cbr.engine.params_pc4 import SPEC_FILES_PC4, spec_hash_pc4

ROOT = Path(__file__).resolve().parents[2]
CLASSES = {"CANON_CORRECTION", "ASSUMPTION", "ASSUMPTION_CHANGE", "IMPLEMENTATION_FIX", "PARITY_SET_CORRECTION",
           "NO_CHANGE"}
PC4_SPEC_HASH = "62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7"
PC3_SPEC_HASH = "7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453"
PC2_SPEC_HASH = "4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2"


def _sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


@pytest.mark.parametrize("model", list(MODELS))
def test_pc4_record_is_frozen_and_unchanged(model):
    rec = yaml.safe_load((OUT_DIR / f"{model}-{VERSION}.yaml").read_text())
    assert rec["spec_version"] == f"{model}-{VERSION}" and rec["supersedes"] == f"{model}-{SUPERSEDES}"
    assert set(rec["spec_files"]) == set(SPEC_FILES_PC4)
    pinned = {**rec["spec_files"], **rec["evidence"], **rec["ruling_records"]}
    changed = [f for f, h in pinned.items() if _sha(f) != h]
    assert not changed, f"pinned files changed after freezing {rec['spec_version']}: {changed}"
    assert rec["spec_hash"] == spec_hash_pc4() == PC4_SPEC_HASH
    assert rec["ruling"] == "D34" and rec["unresolved"]
    assert rec["open_blockers"]                      # every record carries its own blockers
    if model == "CBR1H_BASELINE_V1":                 # CBR15 is SPEC_ONLY and blocks earlier, on its engine
        assert "PC4_SCORING_NOT_AUTHORIZED" in rec["open_blockers"]


def test_pc2_and_pc3_remain_byte_identical():
    """PC4 is additive: neither predecessor's spec hash may move."""
    assert spec_hash() == PC2_SPEC_HASH
    assert spec_hash_pc3() == PC3_SPEC_HASH


def test_predecessor_verdicts_are_recorded_as_frozen_fails():
    rec = yaml.safe_load((OUT_DIR / f"CBR1H_BASELINE_V1-{VERSION}.yaml").read_text())
    assert rec["predecessors"]["PC2"] == {"verdict": "FAIL", "run": "CBR-RUN-013B-2", "frozen": True}
    assert rec["predecessors"]["PC3"] == {"verdict": "FAIL", "run": "CBR-RUN-013C-1", "frozen": True}


@pytest.mark.parametrize("model", list(MODELS))
def test_every_pc4_change_is_classified(model):
    rec = yaml.safe_load((OUT_DIR / f"{model}-{VERSION}.yaml").read_text())
    for change in rec["changes_from_pc3"]:
        assert change["classification"] in CLASSES, change
        assert change["ruling"].startswith("D34"), change
        assert change["from_pc3"] and change["to_pc4"], change


def test_the_approved_change_set_is_exactly_what_d34_authorized():
    """No undocumented behavioural change (D34 §14): the behavioural ids are F-1, F-9, F-10 only."""
    behavioural = {c["id"] for c in CHANGES if c["classification"] not in ("NO_CHANGE", "ASSUMPTION_CHANGE")}
    assert behavioural == {"F-1", "F-9", "F-10"}
    by_id = {c["id"]: c for c in CHANGES}
    assert by_id["F-1"]["classification"] == "IMPLEMENTATION_FIX"
    assert by_id["F-9"]["classification"] == "CANON_CORRECTION"
    assert by_id["F-10"]["classification"] == "ASSUMPTION"
    assert by_id["F-11"]["classification"] == "ASSUMPTION_CHANGE"
    assert by_id["A-1"]["classification"] == "NO_CHANGE"          # the HVCS anchor did not move


def test_f9_scope_is_exactly_two_rules():
    """D34 §5 forbids moving four rules as a bundle."""
    rec = yaml.safe_load((ROOT / "config" / "strategy_pc4.yaml").read_text())
    scope = rec["previous_15m"]["evaluation_instant"]["scope"]
    assert scope == ["M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"]
    not_in = rec["previous_15m"]["evaluation_instant"]["not_in_scope"]
    for rule in ("M1H-OE-01", "M1H-OE-02", "M1H-LOC-01", "M1H-COND-01"):
        assert rule in not_in


def test_oq48_stays_visible_as_unresolved():
    """D34 §4: PC4 may not claim the course defines the counting convention."""
    cfg = yaml.safe_load((ROOT / "config" / "strategy_pc4.yaml").read_text())
    assert cfg["hvcs"]["counting_convention"]["unresolved"] is True
    assert cfg["hvcs"]["counting_convention"]["open_question"] == "OQ-48"
    rec = yaml.safe_load((OUT_DIR / f"CBR1H_BASELINE_V1-{VERSION}.yaml").read_text())
    assert any("OQ-48" in str(u.get("open_question", "")) for u in rec["unresolved"])
