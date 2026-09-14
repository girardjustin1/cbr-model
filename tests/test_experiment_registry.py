"""Experiment registry contract (CBR-GOV-001 §3): complete specs, Astra review, locked holdout, immutability."""

import hashlib
import json
import re
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = yaml.safe_load((ROOT / "research" / "experiments" / "registry.yaml").read_text()) or {}
EXPERIMENTS = REGISTRY.get("experiments") or []

REQUIRED = ["experiment_id", "title", "proposed_by", "reviewed_by", "status", "hypothesis", "economic_rationale",
            "classification", "variables", "parameter_ranges", "baseline_comparison", "primary_metric",
            "secondary_metrics", "development_period", "validation_period", "holdout_status", "failure_condition",
            "promotion_condition", "overfitting_risk", "implementation_notes", "astra_ruling", "owner_approval"]
MUTABLE = {"status", "result_ref", "closed_note", "spec_hash"}
DEV = (date(2018, 1, 1), date(2022, 12, 31))
VAL = (date(2023, 1, 1), date(2024, 12, 31))


def spec_hash(entry: dict) -> str:
    frozen = {k: v for k, v in entry.items() if k not in MUTABLE}
    return hashlib.sha256(json.dumps(frozen, sort_keys=True, default=str).encode()).hexdigest()


def _within(period: str, bounds: tuple[date, date]) -> bool:
    start, end = (date.fromisoformat(p.strip()) for p in period.split("→" if "→" in period else "/"))
    return bounds[0] <= start <= end <= bounds[1]


def test_registry_is_a_list():
    assert isinstance(EXPERIMENTS, list)


def test_ids_unique_and_well_formed():
    ids = [e["experiment_id"] for e in EXPERIMENTS]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"EXP-\d{3}", i) for i in ids)


def test_entries_complete_and_governed():
    for e in EXPERIMENTS:
        missing = [f for f in REQUIRED if f not in e or e[f] in (None, "", [])]
        assert not missing, f"{e.get('experiment_id')}: missing {missing}"
        assert "Astra" in e["reviewed_by"]
        assert e["astra_ruling"] in {"APPROVE", "APPROVE WITH CONSTRAINTS"}
        assert e["holdout_status"] == "LOCKED"
        assert e["status"] in {"REGISTERED", "RUNNING", "COMPLETED", "ABANDONED", "SUPERSEDED"}
        assert e["classification"] in {"CANON-ABLATION", "RESEARCH-DERIVED"}
        assert _within(e["development_period"], DEV) and _within(e["validation_period"], VAL)
        if e["classification"] == "RESEARCH-DERIVED":
            assert all(v.get("classification") == "RESEARCH-DERIVED" for v in e["variables"]), e["experiment_id"]


def test_running_or_closed_experiments_are_immutable():
    for e in EXPERIMENTS:
        if e["status"] != "REGISTERED":
            assert e.get("spec_hash") == spec_hash(e), f"{e['experiment_id']} changed after execution began"
