"""D19-18: the frozen PARITY-CANDIDATE specs still match every pinned file. A failure means a pinned spec, code,
evidence or selection file changed after freezing: create a new spec version and a new parity run."""

import hashlib
from pathlib import Path

import pytest
import yaml

from cbr.engine.freeze_specs import MODELS, OUT_DIR, VERSION
from cbr.engine.params import SPEC_FILES, spec_hash

ROOT = Path(__file__).resolve().parents[2]


def _sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


@pytest.mark.parametrize("model", list(MODELS))
def test_parity_candidate_spec_is_frozen_and_unchanged(model):
    rec = yaml.safe_load((OUT_DIR / f"{model}-{VERSION}.yaml").read_text())
    assert rec["spec_version"] == f"{model}-{VERSION}" and rec["status"].startswith("PARITY-CANDIDATE")
    assert set(rec["spec_files"]) == set(SPEC_FILES)
    changed = [f for f, h in {**rec["spec_files"], **rec["evidence"], **rec["selection_protocol"]["files"]}.items()
               if _sha(f) != h]
    assert not changed, f"pinned files changed after freezing {rec['spec_version']}: {changed}"
    assert rec["spec_hash"] == spec_hash()
    assert "D19" in rec["decisions"] and rec["parameters"]["CANON"] and rec["parameters"]["ASSUMPTION"]
    assert rec["unresolved_rules"] and rec["execution_dependent_rules"]
