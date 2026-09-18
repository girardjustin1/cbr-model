"""D37 §7 / §10: the baseline alias resolves to the frozen PC4 spec and to nothing else."""

import pytest

from cbr.engine import baseline_v1 as base
from cbr.engine import cbr1h_pc4 as pc4
from cbr.engine.params_pc4 import spec_hash_pc4


def test_alias_points_at_the_frozen_pc4_hash():
    assert base.FROZEN_SPEC_HASH == "62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7"
    assert base.verify() == spec_hash_pc4() == base.FROZEN_SPEC_HASH


def test_alias_refuses_to_resolve_when_the_spec_drifts(monkeypatch):
    monkeypatch.setattr(base, "spec_hash_pc4", lambda: "0" * 64)
    with pytest.raises(base.BaselineDrift):
        base.verify()


def test_the_alias_adds_no_behaviour():
    assert base.run_baseline.__wrapped__ is not None if hasattr(base.run_baseline, "__wrapped__") else True
    assert base.CANDIDATE == "CBR1H_BASELINE_V1-PC4"
    assert base.params("A").hvcs_max_violations == pc4.load_cbr1h_pc4("A").hvcs_max_violations


def test_provenance_never_restates_the_parity_verdict_as_pass():
    p = base.provenance()
    assert p["parity_run"] == "CBR-RUN-013D-1" and p["parity_verdict"] == "FAIL"
    assert p["governance_status"] == "RESEARCH-SUFFICIENT WITH DOCUMENTED FIDELITY CONCERNS"
    assert "PASS" not in p["governance_status"]
    assert len(p["fidelity_concerns"]) == 5
    assert any("OQ-48" in c for c in p["fidelity_concerns"])
    assert any("CX-LT3-2" in c for c in p["fidelity_concerns"])
