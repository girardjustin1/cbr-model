"""config/strategy.yaml contract: no unlabelled numbers, every CANON value traceable to evidence,
every ASSUMPTION tied to an open question with a pre-declared research range."""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "config" / "strategy.yaml").read_text())
EVIDENCE_IDS = {json.loads(line)["evidence_id"]
                for line in (ROOT / "research" / "evidence" / "strategy_evidence.jsonl").read_text().splitlines()
                if line.strip()}
OPEN_QUESTIONS = set(re.findall(r"### (OQ-\d+)", (ROOT / "docs" / "strategy" / "open-questions.md").read_text()))


def _parameters(node, path=""):
    """Yield (path, dict) for every leaf parameter, i.e. a mapping that carries a 'value'."""
    if isinstance(node, dict):
        if "value" in node:
            yield path, node
            return
        for key, child in node.items():
            yield from _parameters(child, f"{path}.{key}" if path else str(key))


PARAMS = list(_parameters(CONFIG))


def test_config_has_parameters():
    assert len(PARAMS) > 30


def test_every_parameter_is_labelled():
    for path, p in PARAMS:
        assert p.get("label") in {"CANON", "ASSUMPTION", "IMPL"}, path


def test_canon_parameters_cite_existing_evidence():
    for path, p in PARAMS:
        if p["label"] == "CANON":
            assert p.get("source"), path
            missing = [s for s in p["source"] if s not in EVIDENCE_IDS]
            assert not missing, f"{path}: unknown evidence {missing}"


def test_assumptions_cite_open_questions_and_declare_range():
    for path, p in PARAMS:
        if p["label"] == "ASSUMPTION":
            assert p.get("source") and all(s in OPEN_QUESTIONS for s in p["source"]), path
            assert p.get("research_range") and p["value"] in p["research_range"], path


def test_impl_parameters_give_reason():
    for path, p in PARAMS:
        if p["label"] == "IMPL":
            assert p.get("reason"), path


def test_condition_thresholds_are_ordered():
    c = CONFIG["primitives"]["condition"]
    assert 0 < c["trend_max"]["value"] < c["range_min"]["value"] <= 1


def test_machine_specs_exist():
    for model in CONFIG["models"].values():
        assert (ROOT / model["spec"]).exists()
