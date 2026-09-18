"""PC3 parameter view: the frozen PC2 parameters plus the PC3 additions (owner ruling D29).

Additive module. `config/strategy.yaml` and `engine/params.py` are pinned by the PC2 records and are not modified; the
PC3 values live in `config/strategy_pc3.yaml` and are attached here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import yaml

from cbr.engine.params import ROOT, Cbr1hParams, load_cbr1h

STRATEGY_PC3 = ROOT / "config" / "strategy_pc3.yaml"
SPEC_FILES_PC3 = [
    "docs/strategy/cbr-primitives-machine-spec.md", "docs/strategy/15min-cbr-machine-spec.md",
    "docs/strategy/1h-cbr-machine-spec.md", "config/strategy.yaml", "config/strategy_pc3.yaml",
    "config/data_sources.yaml", "src/cbr/engine/params.py", "src/cbr/engine/params_pc3.py",
    "src/cbr/engine/cbr1h.py", "src/cbr/engine/cbr1h_pc3.py", "src/cbr/engine/common.py",
    "src/cbr/structure/swings.py", "src/cbr/structure/condition.py", "src/cbr/structure/condition_pc3.py",
    "src/cbr/structure/overextension.py", "src/cbr/structure/overextension_pc3.py", "src/cbr/structure/shifts.py",
    "src/cbr/structure/shifts_pc3.py", "src/cbr/structure/levels.py", "src/cbr/structure/indicators.py",
    "src/cbr/data/price_series.py", "src/cbr/data/sessions.py",
]


def _v(node):
    return node["value"] if isinstance(node, dict) and "value" in node else node


@dataclass(frozen=True)
class Cbr1hPC3Params:
    """PC2 parameters (`base`) plus the PC3 rule settings."""

    base: Cbr1hParams
    earliest_activation_min: int
    qualifier: str
    origin: str
    pullback_reference: str
    duration_from: str
    trigger_rule: str
    reversal_timer_anchor: str
    hvcs_conforming: str
    hvcs_evaluation_instant: str
    prior_setup_cbr1h: str
    condition_fallback: str

    def __getattr__(self, name):                       # PC2 parameters stay reachable unchanged
        return getattr(object.__getattribute__(self, "base"), name)


def load_cbr1h_pc3(variant: str = "A", base: Cbr1hParams | None = None) -> Cbr1hPC3Params:
    cfg = yaml.safe_load(STRATEGY_PC3.read_text())
    e, t3, hv = cfg["extension"], cfg["type3"], cfg["hvcs"]
    return Cbr1hPC3Params(
        base=base or load_cbr1h(variant),
        earliest_activation_min=int(_v(e["earliest_activation_min"])), qualifier=_v(e["qualifier"]),
        origin=_v(e["origin"]), pullback_reference=_v(e["pullback_reference"]), duration_from=_v(e["duration_from"]),
        trigger_rule=_v(t3["trigger"]), reversal_timer_anchor=_v(t3["reversal_timer_anchor"]),
        hvcs_conforming=_v(hv["conforming_candle"]), hvcs_evaluation_instant=_v(hv["evaluation_instant"]),
        prior_setup_cbr1h=_v(cfg["prior_setup"]["cbr1h_gate"]),
        condition_fallback=_v(cfg["condition"]["directionless_trending_range"]))


def spec_hash_pc3() -> str:
    h = hashlib.sha256()
    for f in SPEC_FILES_PC3:
        h.update(f.encode())
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()
