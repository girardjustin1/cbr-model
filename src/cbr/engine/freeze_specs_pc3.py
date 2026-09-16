"""Freeze the PC3 parity-candidate specs (owner ruling D29 §18) -> docs/strategy/parity-candidates/<model>-PC3.yaml.

Usage:
    .venv/bin/python -m cbr.engine.freeze_specs_pc3          # writes the records (refuses to overwrite)

Each record pins every file the PC3 engine reads, lists **every difference from PC2** with its D29 classification, and
carries the evidence references, decision ids, config changes and unresolved assumptions. PC2's records are untouched:
`tests/engine/test_parity_candidate_specs.py` still guards them.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import yaml

from cbr.engine.params import ROOT, STRATEGY
from cbr.engine.params_pc3 import SPEC_FILES_PC3, STRATEGY_PC3, spec_hash_pc3

OUT_DIR = ROOT / "docs" / "strategy" / "parity-candidates"
VERSION, SUPERSEDES = "PC3", "PC2"
EVIDENCE_FILES = [
    "docs/decisions/t3-1-type3-sweep-evidence.md", "docs/decisions/oq47-external-sweep-evidence.md",
    "docs/decisions/oq01-swing-confirmation-evidence.md", "docs/decisions/oq09-max-reversal-anchor.md",
    "docs/decisions/extension-activation-definition.md", "docs/decisions/extension-activation-evidence.md",
    "docs/decisions/oe2-pullback-reference-evidence.md", "docs/decisions/oq46-trending-range-direction-evidence.md",
    "docs/decisions/hvcs-continuity-evidence.md", "docs/decisions/cond04-prior-setup-evidence.md",
    "docs/decisions/d8-extension-anchor-evidence.md", "research/evidence/strategy_evidence.jsonl",
]
RULING_RECORDS = ["docs/governance/d26-phase13-fail-reconciliation.md",
                  "docs/governance/d27-phase13r-review-rulings.md",
                  "docs/governance/d28-phase13r-narrowing-rulings.md",
                  "docs/governance/d29-pc3-authorization.md"]
DECISIONS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D16", "D17", "D18", "D19", "D20", "D24", "D25",
             "D26", "D27", "D28", "D29"]

CHANGES = [
    {"id": "T3-1", "rule": "5s and 1m type 3", "classification": "CANON_CORRECTION", "ruling": "D29-1",
     "from_pc2": "the trigger is frozen to the opposing swing confirmed before the sweep; a newer opposing swing disarms",
     "to_pc3": "the trigger is the most recently confirmed opposing swing; a newer opposing swing re-anchors it",
     "evidence": ["EP1-008", "EP2-001", "EP2-002", "EP2-003"], "code": "src/cbr/structure/shifts_pc3.py"},
    {"id": "OQ-09", "rule": "type-3 reversal timer", "classification": "IMPLEMENTATION_FIX", "ruling": "D29-4",
     "from_pc2": "max_reversal runs from the first sweep bar",
     "to_pc3": "max_reversal runs from the latest sweep-extreme update",
     "evidence": ["EP1-008"], "code": "src/cbr/structure/shifts_pc3.py"},
    {"id": "OQ-47", "rule": "type-3 sweep external level", "classification": "NO_CHANGE", "ruling": "D29-2",
     "from_pc2": "no separate external level on the trigger", "to_pc3": "unchanged (option G)",
     "evidence": ["E1H-017", "E1H-021"], "code": None},
    {"id": "ACT-1", "rule": "extension state", "classification": "ASSUMPTION_CHANGE", "ruling": "D29-5",
     "from_pc2": "the extension is active from the hour open",
     "to_pc3": "PRE_EXTENSION until a qualifying push; earliest activation minute 7 (no expiry)",
     "evidence": ["E1H-CBT-0241"], "code": "src/cbr/structure/overextension_pc3.py"},
    {"id": "ACT-2", "rule": "qualifying directional push", "classification": "ASSUMPTION_CHANGE", "ruling": "D29-6",
     "from_pc2": "none (no concept)",
     "to_pc3": "Q1: the move takes the relevant extreme of the completed 15m candle before the hour",
     "evidence": ["E1H-021", "E1H-SS-0131"], "code": "src/cbr/structure/overextension_pc3.py"},
    {"id": "ACT-3", "rule": "M1H-OE-01 duration", "classification": "ASSUMPTION_CHANGE", "ruling": "D29-7",
     "from_pc2": "measured from the hour open", "to_pc3": "measured from extension_activation_time",
     "evidence": ["E1H-MET-4017"], "code": "src/cbr/structure/overextension_pc3.py"},
    {"id": "OE-2", "rule": "M1H-OE-02 pullback reference", "classification": "CANON_CORRECTION", "ruling": "D29-8",
     "from_pc2": "any retrace >= 50% of the running sub-extension fails, and the failure latches for the hour",
     "to_pc3": "the deepest retracement is compared with the active extension known at the decision time; no latch",
     "evidence": ["E1H-018", "E1H-DGE-0319"], "code": "src/cbr/structure/overextension_pc3.py"},
    {"id": "H-1", "rule": "M1H-6A-1 conforming candle", "classification": "CANON_CORRECTION", "ruling": "D29-10",
     "from_pc2": "every counted candle must close in the trade direction (max 1 violation)",
     "to_pc3": "structural respect and progression; indecision candles allowed; no maximum count",
     "evidence": ["E1H-SS-0206", "EP2-1M-0519", "EP2-1M-0449"], "code": "src/cbr/structure/shifts_pc3.py"},
    {"id": "H-2", "rule": "M1H-6A-1 run end", "classification": "CANON_CORRECTION", "ruling": "D29-10",
     "from_pc2": "the run must end on a candle closing in the trade direction",
     "to_pc3": "the run may end on the bar that set the extension extreme",
     "evidence": ["E1H-SS-0206"], "code": "src/cbr/structure/shifts_pc3.py"},
    {"id": "H-3", "rule": "M1H-6A-1 evaluation instant", "classification": "IMPLEMENTATION_FIX", "ruling": "D29-11",
     "from_pc2": "evaluated at the sweep decision, before the displacement bar has closed",
     "to_pc3": "evaluated at the 5s shift decision time; recorded as a trigger-time rule, never in the decision ledger",
     "evidence": ["OQ-43", "D19-6"], "code": "src/cbr/engine/cbr1h_pc3.py"},
    {"id": "C04-1", "rule": "M1H-COND-04", "classification": "CANON_CORRECTION", "ruling": "D29-12",
     "from_pc2": "hard gate: >= 1 raw setup formed in the previous 10 h (unsatisfiable in practice)",
     "to_pc3": "removed from canonical eligibility", "evidence": ["E15-008", "E15-009", "LR-28", "LR-48"],
     "code": "src/cbr/engine/cbr1h_pc3.py"},
    {"id": "C04-D", "rule": "prior-setup context", "classification": "DIAGNOSTIC_ONLY", "ruling": "D29-12",
     "from_pc2": "gate inputs", "to_pc3": "prior_setup_exists / count / age_min / model recorded, never eligibility",
     "evidence": ["LR-28", "LR-73"], "code": "src/cbr/engine/cbr1h_pc3.py"},
    {"id": "OQ-46", "rule": "condition taxonomy", "classification": "CANON_CORRECTION", "ruling": "D29-14",
     "from_pc2": "TRENDING_RANGE with direction NONE blocks the hour (M1H-COND-03)",
     "to_pc3": "such a hour is classified RANGE; no direction is inferred; M1H-COND-03 is not carried in PC3",
     "evidence": ["E1H-WDC-0158", "E1H-WDC-0304"], "code": "src/cbr/structure/condition_pc3.py"},
    {"id": "D8", "rule": "oe_origin", "classification": "NO_CHANGE", "ruling": "D29-15",
     "from_pc2": "HOUR_OPEN", "to_pc3": "HOUR_OPEN (stop and target references unchanged); LAST_RESET research-only",
     "evidence": ["E1H-003"], "code": None},
    {"id": "W-1", "rule": "condition window basis", "classification": "NO_CHANGE", "ruling": "D29-16",
     "from_pc2": "TRADABLE", "to_pc3": "TRADABLE", "evidence": ["E1H-005"], "code": None},
    {"id": "OQ-01", "rule": "swing definition", "classification": "NO_CHANGE", "ruling": "D29-3",
     "from_pc2": "ATR zig-zag, k = 3 (ASSUMPTION)", "to_pc3": "unchanged; sensitivity recorded as a known risk",
     "evidence": ["OQ-01"], "code": None},
    {"id": "S-1", "rule": "candidate selection", "classification": "NO_CHANGE", "ruling": "D29-17",
     "from_pc2": "parity.select_candidate (deterministic, answer-independent)",
     "to_pc3": "unchanged; a selection difference is reported as CANDIDATE_SELECTION_MISMATCH, never fixed during a run",
     "evidence": ["D19-10"], "code": "src/cbr/engine/parity.py"},
]

UNRESOLVED = [
    {"item": "extension origin price", "detail": "most adverse price between the hour open and activation",
     "label": "ASSUMPTION", "note": "no course wording; needed to measure the active extension"},
    {"item": "earliest activation minute", "detail": "minute 7", "label": "ASSUMPTION",
     "open_question": "range 7-15 quoted in V1H-candle_behavior_timing 00:02:41; research range declared in config"},
    {"item": "swing confirmation timing under re-anchoring", "detail": "ATR zig-zag k = 3", "label": "ASSUMPTION",
     "open_question": "OQ-01; CX-LT3-2's trigger disappears at k = 4"},
    {"item": "external sweep level", "detail": "none required", "label": "OPEN", "open_question": "OQ-47 option C/D/E"},
    {"item": "trending-range direction test", "detail": "last two swing pairs", "label": "OPEN",
     "open_question": "OQ-46 asks only that a directionless trending range reclassify as RANGE"},
    {"item": "activation expiry", "detail": "none", "label": "OPEN",
     "open_question": "no evidence supports minute 15 as an expiry"},
]

MODELS = {
    "CBR1H_BASELINE_V1": {
        "spec": "docs/strategy/1h-cbr-machine-spec.md",
        "engine": "src/cbr/engine/cbr1h_pc3.py",
        "implementation_status": "IMPLEMENTED",
        "changes": [c["id"] for c in CHANGES],
        "open_blockers": ["PHASE13C_PARITY_NOT_RUN", "EXPANDED_PARITY_SET_NOT_FROZEN"],
    },
    "CBR15_BASELINE_V1": {
        "spec": "docs/strategy/15min-cbr-machine-spec.md",
        "engine": None,
        "implementation_status": "SPEC_ONLY: the shared primitive corrections are recorded; the CBR15 engine binding is "
                                 "not implemented because no CBR15 example is in the machine parity set yet (D29-13 "
                                 "leaves the CBR15 prior-setup rule unchanged)",
        "changes": ["T3-1", "OQ-09", "H-1", "H-2", "OQ-46"],
        "unchanged_rules": ["M15-COND-03 prior setup (D29-13)", "M15 entry tier", "M15-HTF-01 split (D19-15)"],
        "open_blockers": ["CBR15_PC3_ENGINE_NOT_IMPLEMENTED", "PHASE13C_PARITY_NOT_RUN"],
    },
}


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def record(model: str) -> dict:
    m = MODELS[model]
    changes = [c for c in CHANGES if c["id"] in m["changes"]]
    return {
        "spec_version": f"{model}-{VERSION}",
        "supersedes": f"{model}-{SUPERSEDES}",
        "status": "PARITY-CANDIDATE (frozen for the Phase 13C parity run; NOT a validated strategy spec)",
        "frozen_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "ruling": "D29", "implementation_status": m["implementation_status"],
        "machine_spec": m["spec"], "engine": m["engine"],
        "decisions": DECISIONS,
        "ruling_records": {f: sha(f) for f in RULING_RECORDS},
        "spec_hash": spec_hash_pc3(),
        "spec_files": {f: sha(f) for f in SPEC_FILES_PC3},
        "evidence": {f: sha(f) for f in EVIDENCE_FILES},
        "config": {"pc2": str(STRATEGY.relative_to(ROOT)), "pc3_additions": str(STRATEGY_PC3.relative_to(ROOT)),
                   "pc2_values_unchanged": True},
        "changes_from_pc2": changes,
        "classification_summary": {c: sorted(x["id"] for x in changes if x["classification"] == c)
                                   for c in ("CANON_CORRECTION", "ASSUMPTION_CHANGE", "IMPLEMENTATION_FIX",
                                             "DIAGNOSTIC_ONLY", "NO_CHANGE")},
        "unresolved_assumptions": UNRESOLVED,
        "unchanged_rules": m.get("unchanged_rules", []),
        "open_eligibility_blockers": m["open_blockers"],
        "pc2_record_untouched": f"docs/strategy/parity-candidates/{model}-PC2.yaml",
        "change_policy": "Any change to a pinned file requires a new spec version (PC4, ...) and a new parity run.",
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        path = OUT_DIR / f"{model}-{VERSION}.yaml"
        if path.exists():
            raise SystemExit(f"{path.relative_to(ROOT)} already frozen; create a new version instead")
        path.write_text("# Generated by src/cbr/engine/freeze_specs_pc3.py. Do not edit.\n"
                        + yaml.safe_dump(record(model), sort_keys=False, allow_unicode=True, width=120))
        print("frozen", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
