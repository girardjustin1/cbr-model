"""D38 §33: execution must not import CBR strategy-rule modules, in any module of the package."""

from __future__ import annotations

import ast
import pathlib

PKG = pathlib.Path(__file__).resolve().parents[2] / "src" / "cbr" / "execution"
# The only strategy-side imports allowed: the promotion gate (read-only) and repo paths.
ALLOWED = {"cbr.engine.baseline_v1", "cbr.engine.params", "cbr.data.price_series", "cbr.structure.levels"}
FORBIDDEN_PREFIXES = ("cbr.engine.cbr1h", "cbr.engine.cbr15", "cbr.engine.parity", "cbr.engine.phase13",
                      "cbr.structure.shifts", "cbr.structure.overextension", "cbr.structure.condition",
                      "cbr.structure.swings")


def _imports(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text())
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def test_no_execution_module_imports_a_strategy_rule_module():
    offenders = {}
    for path in sorted(PKG.glob("*.py")):
        bad = [m for m in _imports(path) if m.startswith(FORBIDDEN_PREFIXES)]
        if bad:
            offenders[path.name] = bad
    assert not offenders, f"execution imported strategy rules: {offenders}"


def test_strategy_side_imports_are_on_the_allowed_list():
    for path in sorted(PKG.glob("*.py")):
        for module in _imports(path):
            if module.startswith("cbr."):
                assert module in ALLOWED or module.startswith("cbr.execution"), f"{path.name} imports {module}"


def test_execution_never_recomputes_a_cbr_rule():
    """A crude but useful canary: no rule id may appear anywhere in the package."""
    for path in sorted(PKG.glob("*.py")):
        text = path.read_text()
        assert "M1H-" not in text, f"{path.name} references a CBR rule id"
