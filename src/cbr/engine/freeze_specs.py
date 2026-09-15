"""Freeze the Phase 13 PARITY-CANDIDATE specs (owner ruling D19-18) -> docs/strategy/parity-candidates/<model>-PC1.yaml.

Usage:
    .venv/bin/python -m cbr.engine.freeze_specs            # writes the records (refuses to overwrite)

A record pins the spec version, the hash of every spec/code file the engines read, the evidence register and packages,
the decision ids, CANON / ASSUMPTION / IMPL parameters, unresolved and execution-dependent rules, the D8/D9 switches and
the candidate-selection code. `tests/engine/test_parity_candidate_specs.py` fails if any pinned file changes: a change
needs a new spec version and a new parity run. These are parity candidates, not validated strategy specs.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import yaml

from cbr.engine.params import ROOT, SPEC_FILES, STRATEGY, spec_hash

OUT_DIR = ROOT / "docs" / "strategy" / "parity-candidates"
VERSION = "PC1"
EVIDENCE_FILES = ["research/evidence/strategy_evidence.jsonl", "docs/decisions/oq36-prior-setup-evidence.md",
                  "docs/decisions/oq39-hourly-entry-evidence.md", "docs/decisions/oq40-42-context-timing-evidence.md",
                  "docs/decisions/oq25-canonical-price-extremes.md"]
PROTOCOL_FILES = ["src/cbr/engine/parity.py", "docs/governance/phase13-parity-protocol.md"]
DECISIONS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D16", "D17", "D18", "D19"]

MODELS = {
    "CBR15_BASELINE_V1": {
        "spec": "docs/strategy/15min-cbr-machine-spec.md",
        "unresolved_rules": [
            {"rule": "M15-COND window basis across closures", "open_question": "OQ-45", "handling": "CLOCK (ASSUMPTION)"},
        ],
        "execution_dependent_rules": [
            {"rule": "M15-HTF-01 fill component (hourly setup FILLED)", "state": "HTF_FILL_STATE = NOT_EVALUATED",
             "class": "EXECUTION_DEPENDENT", "resolves_in": "Phase 14A"},
            {"rule": "fills, stop/target touches, one position, final executable stop", "class": "EXECUTION_DEPENDENT",
             "resolves_in": "Phase 14A"},
        ],
        "open_blockers": ["HTF_FILL_STATE_EXECUTION_DEPENDENT", "PHASE13_PARITY_NOT_RUN"],
    },
    "CBR1H_BASELINE_V1": {
        "spec": "docs/strategy/1h-cbr-machine-spec.md",
        "unresolved_rules": [
            {"rule": "M1H-TIME-02 :30 hard veto vs quality downgrade", "open_question": "OQ-42",
             "handling": "timing30_state diagnostic; never rejects"},
            {"rule": "M1H-6A-1 HVCS indecision-bar limit", "open_question": "OQ-44",
             "handling": "structural continuity (respected side), no count; eligibility blocker"},
        ],
        "execution_dependent_rules": [
            {"rule": "fills, one fill per hour, final executable stop, target fixed at fill", "class": "EXECUTION_DEPENDENT",
             "resolves_in": "Phase 14A"},
        ],
        "open_blockers": ["HVCS_INDECISION_LIMIT_UNRESOLVED (OQ-44)", "PHASE13_PARITY_NOT_RUN"],
    },
}


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def _params(node, path=""):
    if isinstance(node, dict):
        if "value" in node:
            yield path, node
            return
        for k, v in node.items():
            yield from _params(v, f"{path}.{k}" if path else str(k))


def record(model: str) -> dict:
    cfg = yaml.safe_load(STRATEGY.read_text())
    m = MODELS[model]
    scope = {"primitives": cfg["primitives"], f"models.{model}": {k: v for k, v in cfg["models"][model].items()
                                                                   if k not in ("spec", "variants")}}
    if model == "CBR1H_BASELINE_V1":
        scope["ablations"] = cfg["ablations"]
    params: dict[str, dict] = {"CANON": {}, "ASSUMPTION": {}, "IMPL": {}}
    for root, node in scope.items():
        for path, p in _params(node, root):
            entry = {"value": p["value"]}
            entry.update({k: p[k] for k in ("source", "research_range", "reason") if k in p})
            params[p["label"]][path] = entry
    return {
        "spec_version": f"{model}-{VERSION}",
        "status": "PARITY-CANDIDATE (frozen for the Phase 13 parity run; NOT a validated strategy spec)",
        "frozen_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "machine_spec": m["spec"],
        "variants": cfg["models"][model]["variants"],
        "decisions": DECISIONS,
        "spec_hash": spec_hash(),
        "spec_files": {f: sha(f) for f in SPEC_FILES},
        "evidence": {f: sha(f) for f in EVIDENCE_FILES},
        "selection_protocol": {"files": {f: sha(f) for f in PROTOCOL_FILES},
                               "key": "five_second_shift_time (missing last), decision time, activation time, tier, "
                                      "prior/same, signal_id; ARMED only; per variant; no course input"},
        "parameters": params,
        "unresolved_rules": m["unresolved_rules"],
        "execution_dependent_rules": m["execution_dependent_rules"],
        "open_eligibility_blockers": m["open_blockers"],
        "not_frozen_here": ["config/phase13_tolerances.yaml numeric values (need V-1 calibration, D19-11)"],
        "change_policy": "Any change to a pinned file requires a new spec version (PC2, ...) and a new parity run (D19-18).",
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        path = OUT_DIR / f"{model}-{VERSION}.yaml"
        if path.exists():
            raise SystemExit(f"{path.relative_to(ROOT)} already frozen; create a new version instead")
        path.write_text("# Generated by src/cbr/engine/freeze_specs.py. Do not edit.\n"
                        + yaml.safe_dump(record(model), sort_keys=False, allow_unicode=True, width=120))
        print("frozen", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
