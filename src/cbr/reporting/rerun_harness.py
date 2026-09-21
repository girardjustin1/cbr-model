"""Deterministic rerun harness (owner ruling D42 §12).

The first Phase 15A run must be repeated from identical frozen inputs and must reproduce itself. This harness runs
the pipeline twice and compares the four things that must not move:

| Compared | How |
|---|---|
| signal-ledger hash | `SignalLedger.ledger_hash()` |
| execution-ledger hash | `ExecutionLedger.execution_ledger_hash()` |
| metrics hash | `Metrics.metrics_hash()` |
| report package | byte hash where the file is deterministic, **semantic-content hash** where it is not |

Two of the eight package files legitimately differ byte-for-byte between runs: `run_manifest.json` and
`phase15a_report.md` both carry a generation timestamp. For those the harness strips the volatile fields and
compares the semantic content instead of pretending a timestamp is a result. Everything else is compared byte for
byte, and **any substantive divergence is a FAIL**.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

HARNESS_VERSION = "15A.1"

# Fields whose value is expected to change between two runs of the same inputs and which carry no result content.
VOLATILE_MANIFEST_FIELDS = ("generated_utc", "package_files")
VOLATILE_LINE_PATTERN = re.compile(r"generated_utc|\*\*Date:\*\*")


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _strip(obj):
    """Drop volatile keys anywhere in the manifest tree so the comparison is about content, not clocks."""
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in VOLATILE_MANIFEST_FIELDS}
    if isinstance(obj, list):
        return [_strip(v) for v in obj]
    return obj


def semantic_hash(path: Path) -> str:
    """Content hash that ignores generation timestamps for the two files that legitimately carry them."""
    if path.name == "run_manifest.json":
        return _sha_bytes(json.dumps(_strip(json.loads(path.read_text())), sort_keys=True, default=str).encode())
    if path.suffix == ".md":
        kept = [ln for ln in path.read_text().splitlines() if not VOLATILE_LINE_PATTERN.search(ln)]
        return _sha_bytes("\n".join(kept).encode())
    return _sha_bytes(path.read_bytes())


def package_hashes(directory: Path) -> dict:
    return {p.name: semantic_hash(p) for p in sorted(Path(directory).iterdir()) if p.is_file()}


@dataclass
class RerunComparison:
    first: dict = field(default_factory=dict)
    second: dict = field(default_factory=dict)
    differences: list = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "FAIL" if self.differences else "PASS"

    def as_dict(self) -> dict:
        return {"harness_version": HARNESS_VERSION, "verdict": self.verdict, "differences": self.differences,
                "first": self.first, "second": self.second}


def compare(first: dict, second: dict) -> RerunComparison:
    """Compare two runs' hash sets. Any substantive divergence is a FAIL (D42 §12)."""
    out = RerunComparison(first=first, second=second)
    for key in ("signal_ledger_hash", "execution_ledger_hash", "metrics_hash", "result_hash"):
        a, b = first.get(key), second.get(key)
        if a != b:
            out.differences.append({"field": key, "first": a, "second": b})
    fa, fb = first.get("package", {}), second.get("package", {})
    for name in sorted(set(fa) | set(fb)):
        if fa.get(name) != fb.get(name):
            out.differences.append({"field": f"package/{name}", "first": fa.get(name), "second": fb.get(name)})
    return out


def run_twice(pipeline, *, directories: tuple[Path, Path]) -> RerunComparison:
    """`pipeline(directory) -> dict` must execute the whole run and return its hash set plus the package directory.

    The harness never mutates the pipeline or its inputs: it calls it twice into two separate directories and
    compares what comes back, so a difference is always the pipeline's, never the harness's.
    """
    runs = []
    for d in directories:
        d = Path(d)
        d.mkdir(parents=True, exist_ok=True)
        result = dict(pipeline(d))
        result.setdefault("package", package_hashes(d))
        runs.append(result)
    return compare(runs[0], runs[1])
