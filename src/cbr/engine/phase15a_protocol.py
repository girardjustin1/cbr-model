"""Phase 15A protocol freeze (owner ruling D42 §11).

The 2022 pilot protocol is frozen *before* any historical signal is generated. This module pins the hash of the
acceptance document together with the specification hashes it declares, so that a protocol edit made after results
are seen is detectable rather than silent.

    .venv/bin/python -m cbr.engine.phase15a_protocol        # print the frozen hashes and any drift

Nothing here computes a statistic, and nothing here reads an outcome.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from cbr.engine import baseline_v1
from cbr.engine.params_pc4 import spec_hash_pc4

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "docs" / "acceptance" / "phase15a-2022-development-pilot.md"
EXECUTION_CONFIG = ROOT / "config" / "execution.yaml"

# Frozen 2026-09-19, before any 2022 signal was generated (D42 §3, §11).
PILOT_SPAN = ("2022-01-01", "2022-12-31")
FROZEN_PC4_SPEC_HASH = "62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7"
FROZEN_EXECUTION_CONFIG_HASH = "12be582e16b9fbf0fdec9322200446f539a8f2ae08efba8eb7d2ca83f22b0551"
FROZEN_PROTOCOL_HASH = "baba0fff090a331c7b9209d8fb41468d93473880304b2f64e3325a0b81389d09"   # hash of the document above, pinned at creation
SIMULATOR_VERSION = "14A.1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol_hash() -> str:
    return _sha(PROTOCOL)


def execution_config_hash() -> str:
    return _sha(EXECUTION_CONFIG)


@dataclass(frozen=True)
class Drift:
    protocol: bool
    pc4_spec: bool
    execution_config: bool

    def any(self) -> bool:
        return self.protocol or self.pc4_spec or self.execution_config


def drift() -> Drift:
    """True on a dimension means it no longer matches what was frozen."""
    return Drift(
        protocol=FROZEN_PROTOCOL_HASH not in ("PENDING", protocol_hash()),
        pc4_spec=spec_hash_pc4() != FROZEN_PC4_SPEC_HASH,
        execution_config=execution_config_hash() != FROZEN_EXECUTION_CONFIG_HASH,
    )


def provenance() -> dict:
    """The block every Phase 15A artefact carries."""
    return {
        "protocol": "CBR-ACC-015A v1.0",
        "ruling": "D42",
        "pilot_span": list(PILOT_SPAN),
        "protocol_hash": protocol_hash(),
        "frozen_protocol_hash": FROZEN_PROTOCOL_HASH,
        "pc4_spec_hash": spec_hash_pc4(),
        "execution_config_hash": execution_config_hash(),
        "simulator_version": SIMULATOR_VERSION,
        "result_status": "DEVELOPMENT_PILOT",
        "permitted_verdicts": ["PROMISING", "INCONCLUSIVE", "NEGATIVE"],
        "baseline_provenance": baseline_v1.provenance(),
        "drift": drift().__dict__,
    }


def main() -> None:
    print(json.dumps({k: v for k, v in provenance().items() if k != "baseline_provenance"}, indent=2))


if __name__ == "__main__":
    main()
