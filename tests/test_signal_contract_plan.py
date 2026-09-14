"""Planning guards for Phase 14 (CBR-ARCH-014, D13). No execution code exists yet; these tests keep the plan honest."""

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "architecture" / "schemas" / "cbr-signal.v1.schema.json"
OWNER_MINIMUM = {  # owner instruction, 2026-09-14
    "signal_id", "model", "timestamp", "direction", "entry_trigger_time", "entry_reference_price", "stop_price",
    "target_price", "extension_high", "extension_low", "range_high", "range_low", "context_state", "dxy_state",
    "session_state", "source_feed", "data_confidence", "reason_code",
}


def test_signal_schema_is_valid_json_and_covers_owner_minimum():
    schema = json.loads(SCHEMA.read_text())
    required = set(schema["required"])
    assert OWNER_MINIMUM <= required
    assert required <= set(schema["properties"])


def test_backtesting_py_not_added_before_phase_14b():
    deps = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    names = [d.lower() for d in deps["dependencies"] + sum(deps.get("optional-dependencies", {}).values(), [])]
    assert not any(n.startswith(("backtesting", "bokeh")) for n in names)


def test_no_optimizer_calls_in_source():
    offenders = [p for p in (ROOT / "src").rglob("*.py") if ".optimize(" in p.read_text()]
    assert offenders == []
