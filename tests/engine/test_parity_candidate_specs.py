"""D19-18 / D20-7: the current PARITY-CANDIDATE specs still match every pinned file, and superseded versions are kept
unchanged for audit. A failure means a pinned spec, code, evidence, ruling or selection file changed after freezing:
create a new spec version and a new parity run."""

import hashlib
from pathlib import Path

import pytest
import yaml

from cbr.engine.freeze_specs import MODELS, OUT_DIR, SUPERSEDES, VERSION
from cbr.engine.params import SPEC_FILES, spec_hash

ROOT = Path(__file__).resolve().parents[2]


def _sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


@pytest.mark.parametrize("model", list(MODELS))
def test_current_parity_candidate_spec_is_frozen_and_unchanged(model):
    rec = yaml.safe_load((OUT_DIR / f"{model}-{VERSION}.yaml").read_text())
    assert rec["spec_version"] == f"{model}-{VERSION}" and rec["status"].startswith("PARITY-CANDIDATE")
    assert rec["supersedes"] == f"{model}-{SUPERSEDES}"
    assert set(rec["spec_files"]) == set(SPEC_FILES)
    pinned = {**rec["spec_files"], **rec["evidence"], **rec["selection_protocol"]["files"], **rec["ruling_records"]}
    changed = [f for f, h in pinned.items() if _sha(f) != h]
    assert not changed, f"pinned files changed after freezing {rec['spec_version']}: {changed}"
    assert rec["spec_hash"] == spec_hash()
    assert {"D19", "D20"} <= set(rec["decisions"]) and rec["parameters"]["CANON"] and rec["parameters"]["ASSUMPTION"]
    assert rec["interpretation_assumptions"] and rec["execution_dependent_rules"]
    assert not any("OQ-44" in str(b) for b in rec["open_eligibility_blockers"])


@pytest.mark.parametrize("model", list(MODELS))
def test_superseded_spec_is_preserved_for_audit(model):
    old = yaml.safe_load((OUT_DIR / f"{model}-{SUPERSEDES}.yaml").read_text())
    assert old["spec_version"] == f"{model}-{SUPERSEDES}"
    assert old["spec_hash"] != spec_hash()                      # superseded, not silently re-pinned
