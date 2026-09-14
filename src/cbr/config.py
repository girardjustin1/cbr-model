"""Read parameters from config/strategy.yaml. Code never hard-codes a trading number."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


@cache
def strategy() -> dict[str, Any]:
    return yaml.safe_load((ROOT / "config" / "strategy.yaml").read_text())


def param(path: str) -> Any:
    """Value of a labelled parameter, e.g. param("primitives.swing.LTF.k")."""
    node: Any = strategy()
    for key in path.split("."):
        node = node[key]
    if not isinstance(node, dict) or "value" not in node:
        raise KeyError(f"{path} is not a labelled parameter")
    return node["value"]
