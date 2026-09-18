"""PC4 parameter view: the frozen PC3 parameters plus the PC4 settings (owner ruling D34).

Additive module. `config/strategy.yaml`, `config/strategy_pc3.yaml`, `engine/params.py` and `engine/params_pc3.py`
are pinned by the PC2 and PC3 records and are not modified; the PC4 values live in `config/strategy_pc4.yaml`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import yaml

from cbr.engine.params import ROOT, Cbr1hParams
from cbr.engine.params_pc3 import Cbr1hPC3Params, load_cbr1h_pc3

STRATEGY_PC4 = ROOT / "config" / "strategy_pc4.yaml"
SPEC_FILES_PC4 = [
    "docs/strategy/cbr-primitives-machine-spec.md", "docs/strategy/15min-cbr-machine-spec.md",
    "docs/strategy/1h-cbr-machine-spec.md", "config/strategy.yaml", "config/strategy_pc3.yaml",
    "config/strategy_pc4.yaml", "config/data_sources.yaml", "src/cbr/engine/params.py",
    "src/cbr/engine/params_pc3.py", "src/cbr/engine/params_pc4.py", "src/cbr/engine/cbr1h.py",
    "src/cbr/engine/cbr1h_pc3.py", "src/cbr/engine/cbr1h_pc4.py", "src/cbr/engine/common.py",
    "src/cbr/structure/swings.py", "src/cbr/structure/condition.py", "src/cbr/structure/condition_pc3.py",
    "src/cbr/structure/overextension.py", "src/cbr/structure/overextension_pc3.py", "src/cbr/structure/shifts.py",
    "src/cbr/structure/shifts_pc3.py", "src/cbr/structure/shifts_pc4.py", "src/cbr/structure/levels.py",
    "src/cbr/structure/indicators.py", "src/cbr/data/price_series.py", "src/cbr/data/sessions.py",
]


def _v(node):
    return node["value"] if isinstance(node, dict) and "value" in node else node


@dataclass(frozen=True)
class Cbr1hPC4Params:
    """PC3 parameters (`base`) plus the PC4 rule settings. PC2 and PC3 values stay reachable unchanged."""

    base: Cbr1hPC3Params
    hvcs_violation_tolerance: str
    hvcs_endpoint: str
    hvcs_counting_convention: str
    previous_15m_evaluation_instant: str
    previous_15m_q_anchor: str
    previous_15m_data_horizon: str
    previous_15m_scope: tuple[str, ...]

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "base"), name)


def load_cbr1h_pc4(variant: str = "A", base: Cbr1hParams | None = None) -> Cbr1hPC4Params:
    cfg = yaml.safe_load(STRATEGY_PC4.read_text())
    hv, p15 = cfg["hvcs"], cfg["previous_15m"]
    return Cbr1hPC4Params(
        base=load_cbr1h_pc3(variant, base=base),
        hvcs_violation_tolerance=_v(hv["violation_tolerance"]), hvcs_endpoint=_v(hv["endpoint"]),
        hvcs_counting_convention=_v(hv["counting_convention"]),
        previous_15m_evaluation_instant=_v(p15["evaluation_instant"]), previous_15m_q_anchor=_v(p15["q_anchor"]),
        previous_15m_data_horizon=_v(p15["data_horizon"]),
        previous_15m_scope=tuple(p15["evaluation_instant"]["scope"]))


def spec_hash_pc4() -> str:
    h = hashlib.sha256()
    for f in SPEC_FILES_PC4:
        h.update(f.encode())
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()
