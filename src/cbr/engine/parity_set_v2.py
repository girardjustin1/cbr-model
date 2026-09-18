"""Corrected CBR1H parity set, v2 (owner ruling D34 §9-12) -> research/examples/parity_set_manifest_v2.json.

Usage:
    .venv/bin/python -m cbr.engine.parity_set_v2            # writes the manifest (refuses to overwrite)

Built from the v1 manifest (`a3ee0bd6…`, frozen and untouched) plus the D34 corrections. The v1 file is **not**
edited: CBR-RUN-013C-1 was scored against it and stays reproducible.

What changed, and why (D34 §9-11):
  * every binding machine case now carries `model_scope`, and only `CONFIRMED_CBR1H` may bind a verdict (§12);
  * JM-2025-10-17 leaves the machine set — it is an inverse fractal shift, a middle-timeframe model no CBR1H engine
    implements — and is preserved for its correct future model, not deleted;
  * JM-2025-10-29 moves to NARRATIVE / REFERENCE: its journal time column and its CB-hour column disagree, and
    nothing about it may be inferred from engine output;
  * JM-2025-10-16 stays, scored no further than the journal source states.

Nothing here reads engine output, and no case is scored.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from cbr.engine.params import ROOT
from cbr.engine.parity_set import MANIFEST as MANIFEST_V1
from cbr.engine.parity_set import market_data_hashes

MANIFEST_V2 = ROOT / "research" / "examples" / "parity_set_manifest_v2.json"
V1_HASH = "a3ee0bd6ba225ce6b89d8bc61fbefd227ce8097a3f6bfac2f9414e19cd81ea9c"
REQUIRED = ["case_id", "source", "evidence_level", "model_scope", "direction", "positive_or_negative",
            "scoring_level", "source_supported_fields", "market_data_hashes", "evidence_hashes"]

CONFIRMED, NOT_IMPLEMENTED, AMBIGUOUS = "CONFIRMED_CBR1H", "IFS_NOT_IMPLEMENTED", "SOURCE_AMBIGUITY"
# The D34 corrections, keyed by case. Everything not named here keeps its v1 scoping.
CORRECTIONS = {
    "JM-2025-10-17": {
        "model_scope": NOT_IMPLEMENTED, "scoring_level": "NARRATIVE_ONLY", "binds_verdict": False,
        "classification": "PARITY_SET_CORRECTION", "ruling": "D34-9",
        "reason": "the journal records an IFS (inverse fractal shift). Level 1 names three middle-timeframe models "
                  "and the engine implements two: there is no FS/IFS condition class in PC2, PC3 or PC4, so the "
                  "engine cannot express the model this row records.",
        "preserved_for": "future FS/IFS model validation set",
        "evidence": "docs/decisions/mtf-model-taxonomy.md",
    },
    "JM-2025-10-29": {
        "model_scope": AMBIGUOUS, "scoring_level": "NARRATIVE_ONLY", "binds_verdict": False,
        "classification": "PARITY_SET_CORRECTION", "ruling": "D34-10",
        "reason": "the row's own columns disagree: the journal time maps to minute 14 of the hour while the CB-hour "
                  "column reads 37, and the frozen hour contains no down-extension for the recorded BUY. Entry time, "
                  "candle-behaviour time, direction semantics and model membership may not be inferred from engine "
                  "output (D34-10).",
        "preserved_for": "reference; re-admissible only if the source ambiguity is resolved independently",
        "evidence": "docs/decisions/mtf-model-taxonomy.md",
    },
    "JM-2025-10-16": {
        "model_scope": CONFIRMED, "binds_verdict": True, "classification": "NO_CHANGE", "ruling": "D34-11",
        "reason": "TRR CT is the counter-trending-range variant the engine implements (TRENDING_RANGE + "
                  "M1H-LOC-03). Its dating is corroborated inside the frozen hour, independently of the journal "
                  "time column. Scored no further than the journal states.",
        "evidence": "docs/decisions/mtf-model-taxonomy.md",
    },
}
# Located during the OQ-48 evidence review; deliberately NOT admitted as binding cases (D33 §C): they were used as
# evidence to resolve the rule they would score, which would be circular.
EVIDENCE_ONLY = [
    {"case_id": "HX-1", "source": "research/transcripts/hourly/V1H-seconds_shift_1m_hilo_hvcs.json",
     "source_detail": "V1H-seconds_shift_1m_hilo_hvcs 00:02:06, chart dated Thu 23 Oct '25 GMT+11",
     "evidence_level": "L1_VIDEO", "model_scope": CONFIRMED, "direction": "BUY", "positive_or_negative": "POSITIVE",
     "scoring_level": "NARRATIVE_ONLY", "binds_verdict": False,
     "source_supported_fields": ["hvcs_sequence", "extension_direction", "approximate_shift_minute",
                                 "previous_15m_take"],
     "why_not_binding": "used as evidence to resolve OQ-48; scoring the rule it helped settle would be circular",
     "data_span_utc": ["2025-10-23T00:00:00+00:00", "2025-10-24T00:00:00+00:00"]},
    {"case_id": "HX-2", "source": "research/transcripts/hourly/V1H-candle_behavior_extension.json",
     "source_detail": "V1H-candle_behavior_extension 00:03:38, chart dated Wed 29 Oct '25 GMT+11",
     "evidence_level": "L1_VIDEO", "model_scope": CONFIRMED, "direction": "BUY", "positive_or_negative": "POSITIVE",
     "scoring_level": "NARRATIVE_ONLY", "binds_verdict": False,
     "source_supported_fields": ["hvcs_sequence", "extension_direction", "approximate_shift_minute",
                                 "previous_15m_take"],
     "why_not_binding": "same reason as HX-1",
     "data_span_utc": ["2025-10-29T00:00:00+00:00", "2025-10-30T00:00:00+00:00"]},
]
EVIDENCE_FILES = ["docs/governance/d34-pc4-authorization.md", "docs/decisions/mtf-model-taxonomy.md",
                  "docs/decisions/oq49-journal-generalization.md", "docs/decisions/oq48-hvcs-duration-evidence.md",
                  "research/examples/cbr1h-parity-set-proposal.md"]


def _sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def build() -> dict:
    v1 = json.loads(MANIFEST_V1.read_text())
    if v1["manifest_hash"] != V1_HASH:
        raise SystemExit(f"STOP: the v1 manifest changed ({v1['manifest_hash'][:12]}…); it is frozen")
    evidence_hashes = {f: _sha(f) for f in EVIDENCE_FILES}
    cases = []
    for c in v1["cases"]:
        fix = CORRECTIONS.get(c["case_id"], {})
        machine = c["scoring_level"] in ("ENTRY_LEVEL", "HOUR_LEVEL")
        case = {
            "case_id": c["case_id"], "source": c["source"], "source_detail": c["source_detail"],
            "evidence_level": c["evidence_level"], "instrument": c["instrument"], "model": c["model"],
            "model_scope": fix.get("model_scope", CONFIRMED if machine else "NARRATIVE"),
            "direction": c["direction"], "positive_or_negative": c["positive_or_negative"],
            "scoring_level": fix.get("scoring_level", c["scoring_level"]),
            "binds_verdict": fix.get("binds_verdict", machine),
            "start_time": c.get("start_time"), "end_time": c.get("end_time"),
            "data_span_utc": c.get("data_span_utc"), "stated": c["stated"],
            "source_supported_fields": c.get("fields_allowed_for_scoring", ["geometry_consistency_only"]),
            "market_data_hashes": c.get("market_data_hashes", {}),
            "source_hashes": c.get("source_hashes", {}),
            "evidence_hashes": evidence_hashes,
        }
        if fix:
            case["correction"] = {k: fix[k] for k in ("classification", "ruling", "reason", "evidence") if k in fix}
            if "preserved_for" in fix:
                case["correction"]["preserved_for"] = fix["preserved_for"]
        cases.append(case)
    for e in EVIDENCE_ONLY:
        cases.append({**e, "instrument": "XAUUSD", "model": "CBR1H", "stated": {},
                      "market_data_hashes": market_data_hashes(e["data_span_utc"]),
                      "source_hashes": {e["source"]: _sha(e["source"])}, "evidence_hashes": evidence_hashes,
                      "start_time": None, "end_time": None})
    binding = [c for c in cases if c["binds_verdict"]]
    manifest = {
        "manifest_version": "v2", "supersedes": {"manifest": "parity_set_manifest.json", "hash": V1_HASH},
        "ruling": "D34 §9-12", "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "scope": "CBR1H only. Every binding machine case satisfies model_scope = CONFIRMED_CBR1H (D34 §12). "
                 "No case is scored by this file and no engine output was read.",
        "counts": {
            "binding_entry_level": sum(1 for c in binding if c["scoring_level"] == "ENTRY_LEVEL"),
            "binding_hour_level": sum(1 for c in binding if c["scoring_level"] == "HOUR_LEVEL"),
            "narrative_only": sum(1 for c in cases if not c["binds_verdict"]),
        },
        "binding_case_ids": [c["case_id"] for c in binding],
        "corrections": {k: v["classification"] for k, v in CORRECTIONS.items()},
        "cases": cases,
    }
    manifest["manifest_hash"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, default=str).encode()).hexdigest()
    return manifest


def main() -> None:
    if MANIFEST_V2.exists():
        raise SystemExit(f"{MANIFEST_V2.relative_to(ROOT)} exists: a frozen manifest is never overwritten")
    m = build()
    MANIFEST_V2.write_text(json.dumps(m, indent=1, sort_keys=False, default=str) + "\n")
    print(json.dumps({"counts": m["counts"], "binding": m["binding_case_ids"],
                      "manifest_hash": m["manifest_hash"]}, indent=2))


if __name__ == "__main__":
    main()
