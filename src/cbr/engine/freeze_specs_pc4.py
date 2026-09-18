"""Freeze the PC4 parity-candidate spec (owner ruling D34 §14) -> docs/strategy/parity-candidates/<model>-PC4.yaml.

Usage:
    .venv/bin/python -m cbr.engine.freeze_specs_pc4          # writes the record (refuses to overwrite)

The record pins every file the PC4 engine reads and lists **every difference from PC3** with its D34 classification.
No undocumented behavioural change is allowed (D34 §14). PC2's and PC3's records are untouched and still guarded by
`tests/engine/test_parity_candidate_specs.py` and `test_parity_candidate_specs_pc3.py`.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import yaml

from cbr.engine.params import ROOT, STRATEGY
from cbr.engine.params_pc3 import STRATEGY_PC3
from cbr.engine.params_pc4 import SPEC_FILES_PC4, STRATEGY_PC4, spec_hash_pc4

OUT_DIR = ROOT / "docs" / "strategy" / "parity-candidates"
VERSION, SUPERSEDES = "PC4", "PC3"
EVIDENCE_FILES = [
    "docs/decisions/oq48-hvcs-duration-evidence.md", "docs/decisions/oq50-previous-15m-evaluation-time.md",
    "docs/decisions/mtf-model-taxonomy.md", "docs/decisions/oq49-journal-generalization.md",
    "docs/decisions/hvcs-continuity-evidence.md", "research/evidence/strategy_evidence.jsonl",
    "reports/oq48-independent-examples.md", "reports/phase13c-evaluation-instant.md",
]
RULING_RECORDS = ["docs/governance/d31-pc3-scored-parity-authorization.md",
                  "docs/governance/d32-phase13c-failure-diagnosis.md",
                  "docs/governance/d33-evidence-resolution.md",
                  "docs/governance/d34-pc4-authorization.md",
                  "docs/governance/f1-max-violations-implementation-plan.md"]
DECISIONS = ["D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32", "D33", "D34"]

CHANGES = [
    {"id": "F-1", "rule": "M1H-6A-1-HVCS-INTO-SHIFT conforming run", "classification": "IMPLEMENTATION_FIX",
     "ruling": "D34-2",
     "from_pc3": "the run breaks at the first candle that fails the structural respect test; `hvcs.max_violations` is "
                 "configured and loaded but never passed to the measurement",
     "to_pc4": "the configured `hvcs.max_violations` = 1 tolerance is applied again, exactly as PC2 applied it; the "
               "value is unchanged and untested at other values",
     "evidence": ["E1H-003", "E1H-034", "HX-1", "HX-2"],
     "evidence_note": "two dated Level-1 examples outside the parity set (2025-10-23, 2025-10-29) each contain exactly "
                      "one structural violation; PC3 measures 1 conforming minute on both, PC4 measures 9 and 10",
     "code": "src/cbr/structure/shifts_pc4.py"},
    {"id": "F-9", "rule": "M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q evaluation instant",
     "classification": "CANON_CORRECTION", "ruling": "D34-5",
     "from_pc3": "both are decision-time rules, evaluated when the lower-timeframe type 3 arms",
     "to_pc4": "both are trigger-time rules, evaluated at the final canonical 5s shift; no other rule moves",
     "evidence": ["E1H-003", "E1H-034", "E1H-017"],
     "evidence_note": "every Level-1 statement makes the take a precondition of the entry; the type-3 arm has no "
                      "counterpart in the course vocabulary",
     "code": "src/cbr/engine/cbr1h_pc4.py"},
    {"id": "F-10", "rule": "Q anchor for the two previous-15m rules", "classification": "ASSUMPTION",
     "ruling": "D34-6",
     "from_pc3": "Q is the 15m candle containing the decision instant",
     "to_pc4": "Q is the 15m candle containing the final canonical 5s shift; Q-1 is the previous completed 15m candle; "
               "judged only from bars closed at or before the shift decision instant",
     "evidence": ["E1H-034"], "code": "src/cbr/engine/cbr1h_pc4.py"},
    {"id": "F-11", "rule": "OQ-48 anchor, counting convention and unit", "classification": "ASSUMPTION_CHANGE",
     "ruling": "D34-4",
     "from_pc3": "implicit in the implementation, not stated in the spec record",
     "to_pc4": "recorded explicitly as ASSUMPTIONS in config/strategy_pc4.yaml; OQ-48 stays "
               "UNRESOLVED_SPEC_AMBIGUITY and no alternate convention may be used during a scored run",
     "evidence": ["OQ-48"], "code": "config/strategy_pc4.yaml"},
    {"id": "A-1", "rule": "HVCS endpoint", "classification": "NO_CHANGE", "ruling": "D34-3",
     "from_pc3": "the run ends at the extension-extreme bar known at the 5s shift",
     "to_pc4": "unchanged. HVCS_TO_SHIFT is computed as a diagnostic (`hvcs_to_shift_minutes`) and never gates a "
               "signal; it was not adopted and must not be adopted because it yields 3/3",
     "evidence": ["E1H-003"], "code": "src/cbr/engine/cbr1h_pc4.py"},
    {"id": "A-2", "rule": "type-3 re-anchoring, sweep-extreme timer, whole-extension pullback, PRE_EXTENSION / "
                          "EXTENSION_ACTIVE, minute-7 activation, Q1 qualifier, HOUR_OPEN, k = 3, directionless "
                          "trending range -> RANGE, candidate selection, tradable-time window, prior-setup gate removal",
     "classification": "NO_CHANGE", "ruling": "D34-13",
     "from_pc3": "as implemented in PC3", "to_pc4": "unchanged; these recovered Tom's trigger geometry and are "
                                                    "outside the current failure scope",
     "evidence": [], "code": None},
    {"id": "A-3", "rule": "M1H-LOC-*, M1H-OE-*, M1H-COND-* evaluation instant", "classification": "NO_CHANGE",
     "ruling": "D34-5",
     "from_pc3": "decision-time", "to_pc4": "unchanged. D34 §5 forbids moving rules as a bundle merely because they "
                                            "share an evaluation timestamp; no evidence requires shift-time "
                                            "evaluation for these",
     "evidence": [], "code": None},
]

UNRESOLVED = [
    {"item": "HVCS run anchor", "detail": "the run ends at the extension-extreme bar known at the shift",
     "label": "ASSUMPTION", "open_question": "OQ-48; the shift-anchored reading stays a diagnostic only"},
    {"item": "HVCS counting convention", "detail": "completed 1m candles, first candle not counted",
     "label": "ASSUMPTION", "open_question": "OQ-48; inclusive counting and the minute-clock origin are undefined"},
    {"item": "HVCS duration unit", "detail": "candle count, not elapsed wall-clock time", "label": "ASSUMPTION",
     "open_question": "OQ-48"},
    {"item": "extension origin price", "detail": "most adverse price between the hour open and activation",
     "label": "ASSUMPTION", "open_question": "carried from PC3, unchanged"},
    {"item": "earliest activation minute", "detail": "minute 7", "label": "ASSUMPTION",
     "open_question": "carried from PC3, unchanged"},
    {"item": "swing definition", "detail": "ATR zig-zag k = 3", "label": "ASSUMPTION",
     "open_question": "OQ-01; JM-2025-10-16 adds a second instance of the classifier disagreeing with the source"},
    {"item": "Q anchor at a 15m boundary", "detail": "Q follows the shift, so a shift early in a new candle moves Q",
     "label": "ASSUMPTION", "open_question": "OQ-50 §5; frequency is measurable only under an authorized run"},
    {"item": "FS / IFS middle-timeframe model", "detail": "not implemented in any candidate", "label": "OPEN",
     "open_question": "OQ-51; Tom trades three MTF models, the engine implements two"},
]

MODELS = {
    "CBR1H_BASELINE_V1": {
        "spec": "docs/strategy/1h-cbr-machine-spec.md",
        "engine": "src/cbr/engine/cbr1h_pc4.py",
        "implementation_status": "IMPLEMENTED",
        "changes": [c["id"] for c in CHANGES],
        "open_blockers": ["PC4_SCORING_NOT_AUTHORIZED", "CBR_PROT_013D_NOT_APPROVED",
                          "CORRECTED_PARITY_SET_NOT_FROZEN"],
    },
    "CBR15_BASELINE_V1": {
        "spec": "docs/strategy/15min-cbr-machine-spec.md",
        "engine": None,
        "implementation_status": "SPEC_ONLY: unchanged from PC3. The F-1 tolerance is a CBR1H HVCS rule and CBR15 has "
                                 "no hvcs block; the previous-15m evaluation-instant correction is a CBR1H Variant-A "
                                 "path and is not transferred by analogy",
        "changes": ["F-11", "A-2"],
        "unchanged_rules": ["M15-COND-03 prior setup", "M15 entry tier", "M15-HTF-01 split"],
        "open_blockers": ["CBR15_PC4_ENGINE_NOT_IMPLEMENTED", "NO_CBR15_MACHINE_EXAMPLE"],
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
        "status": "PARITY-CANDIDATE (created under D34; scoring NOT authorized; NOT a validated strategy spec)",
        "frozen_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "ruling": "D34", "implementation_status": m["implementation_status"],
        "machine_spec": m["spec"], "engine": m["engine"],
        "decisions": DECISIONS,
        "ruling_records": {f: sha(f) for f in RULING_RECORDS},
        "spec_hash": spec_hash_pc4(),
        "spec_files": {f: sha(f) for f in SPEC_FILES_PC4},
        "evidence": {f: sha(f) for f in EVIDENCE_FILES},
        "config": {"pc2": str(STRATEGY.relative_to(ROOT)), "pc3_additions": str(STRATEGY_PC3.relative_to(ROOT)),
                   "pc4_additions": str(STRATEGY_PC4.relative_to(ROOT)),
                   "pc2_values_unchanged": True, "pc3_values_unchanged": True},
        "changes_from_pc3": changes,
        "classification_summary": {c: sorted(x["id"] for x in changes if x["classification"] == c)
                                   for c in ("CANON_CORRECTION", "ASSUMPTION", "ASSUMPTION_CHANGE",
                                             "IMPLEMENTATION_FIX", "PARITY_SET_CORRECTION", "NO_CHANGE")},
        "unresolved": UNRESOLVED,
        "open_blockers": m["open_blockers"],
        "predecessors": {
            "PC2": {"verdict": "FAIL", "run": "CBR-RUN-013B-2", "frozen": True},
            "PC3": {"verdict": "FAIL", "run": "CBR-RUN-013C-1", "frozen": True},
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        path = OUT_DIR / f"{model}-{VERSION}.yaml"
        if path.exists():
            raise SystemExit(f"{path.relative_to(ROOT)} exists: a frozen record is never overwritten")
        path.write_text(yaml.safe_dump(record(model), sort_keys=False, width=120, allow_unicode=True))
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"PC4 spec hash: {spec_hash_pc4()}")


if __name__ == "__main__":
    main()
