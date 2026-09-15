"""Frozen parameter view for the reference engines (config/strategy.yaml; values only, labels stay in the yaml)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[3]
STRATEGY = ROOT / "config" / "strategy.yaml"
SPEC_FILES = ["docs/strategy/cbr-primitives-machine-spec.md", "docs/strategy/15min-cbr-machine-spec.md",
              "config/strategy.yaml", "config/data_sources.yaml", "src/cbr/engine/cbr15.py", "src/cbr/engine/params.py",
              "src/cbr/structure/swings.py", "src/cbr/structure/condition.py", "src/cbr/structure/overextension.py",
              "src/cbr/structure/shifts.py", "src/cbr/structure/levels.py", "src/cbr/structure/indicators.py",
              "src/cbr/data/price_series.py", "src/cbr/engine/common.py", "docs/strategy/1h-cbr-machine-spec.md",
              "src/cbr/engine/cbr1h.py"]


def _v(node):
    return node["value"] if isinstance(node, dict) and "value" in node else node


@dataclass(frozen=True)
class Cbr15Params:
    model: str
    variant: str
    aoi_required: bool
    tick: float
    atr_length: int
    k_s5: float
    k_ltf: float
    range_min: float
    trend_max: float
    correction_cap: float
    aggregate: str
    pullback_frac: float
    activation_atr: float
    two_sided_frac: float
    max_reversal_s5: pd.Timedelta
    buffer_atr: float
    min_rr: float
    rollover_pre_min: int
    rollover_post_min: int
    rollover_flat_before_min: int
    aoi_zone_atr: float
    aoi_lookback: pd.Timedelta
    window: pd.Timedelta
    min_legs: int
    max_legs: int
    min_leg_index: int
    prior_hard_lookback: pd.Timedelta
    prior_hard_min: int
    prior_soft_lookback: pd.Timedelta
    range_extreme: float
    pro_er_min: float
    pro_er_max: float
    oe_min_minutes: float
    oe_min_size_atr: float
    start_mic: float
    hvcs_min_minutes: int
    hvcs_max_violations: int
    hvcs_lvcs_body_atr: float


def load_cbr15(variant: str = "base") -> Cbr15Params:
    cfg = yaml.safe_load(STRATEGY.read_text())
    p, m = cfg["primitives"], cfg["models"]["CBR15_BASELINE_V1"]
    if variant not in m["variants"]:
        raise ValueError(f"unknown CBR15 variant {variant!r}")
    return Cbr15Params(
        model="CBR15_BASELINE_V1", variant=variant, aoi_required=bool(m["variants"][variant]["aoi_required"]),
        tick=_v(p["tick"]), atr_length=_v(p["atr_length"]), k_s5=_v(p["swing"]["S5"]["k"]),
        k_ltf=_v(p["swing"]["LTF"]["k"]), range_min=_v(p["condition"]["range_min"]),
        trend_max=_v(p["condition"]["trend_max"]), correction_cap=_v(p["condition"]["correction_cap"]),
        aggregate=_v(p["condition"]["aggregate"]), pullback_frac=_v(p["oe"]["pullback_frac"]),
        activation_atr=_v(p["oe"]["activation_atr"]), two_sided_frac=_v(p["oe"]["two_sided_frac"]),
        max_reversal_s5=pd.Timedelta(minutes=_v(p["t3"]["max_reversal_minutes"]["S5"])),
        buffer_atr=_v(p["stop"]["buffer_atr"]), min_rr=_v(p["min_rr"]),
        rollover_pre_min=_v(p["no_trade"]["rollover_pre_min"]), rollover_post_min=_v(p["no_trade"]["rollover_post_min"]),
        rollover_flat_before_min=_v(p["no_trade"]["rollover_flat_before_min"]),
        aoi_zone_atr=_v(p["aoi"]["zone_atr"]), aoi_lookback=pd.Timedelta(hours=_v(p["aoi"]["lookback_hours"])),
        window=pd.Timedelta(hours=_v(m["cond"]["window_hours"])), min_legs=_v(m["cond"]["min_legs"]),
        max_legs=_v(m["cond"]["max_legs"]), min_leg_index=_v(m["cond"]["min_leg_index"]),
        prior_hard_lookback=pd.Timedelta(minutes=_v(m["prior"]["hard_lookback_min"])),
        prior_hard_min=_v(m["prior"]["hard_min_count"]),
        prior_soft_lookback=pd.Timedelta(minutes=_v(m["prior"]["soft_lookback_min"])),
        range_extreme=_v(m["loc"]["range_extreme"]), pro_er_min=_v(m["loc"]["pro_er_min"]),
        pro_er_max=_v(m["loc"]["pro_er_max"]), oe_min_minutes=_v(m["oe"]["min_minutes"]),
        oe_min_size_atr=_v(m["oe"]["min_size_atr"]), start_mic=_v(m["timing"]["start_mic"]),
        hvcs_min_minutes=_v(p["hvcs"]["min_minutes"]), hvcs_max_violations=_v(p["hvcs"]["max_violations"]),
        hvcs_lvcs_body_atr=_v(p["hvcs"]["lvcs_body_atr"]))


def spec_hash() -> str:
    h = hashlib.sha256()
    for f in SPEC_FILES:
        h.update(f.encode())
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()


@dataclass(frozen=True)
class Cbr1hParams:
    model: str
    variant: str
    entry_model: str                 # HVCS_HILO / FRACTAL_1M
    aoi_required: bool
    tick: float
    atr_length: int
    k_mtf: float
    k_ltf: float
    range_min: float
    trend_max: float
    correction_cap: float
    aggregate: str
    pullback_frac: float
    activation_atr: float
    two_sided_frac: float
    max_reversal_ltf: pd.Timedelta
    hvcs_min_minutes: int
    hvcs_max_violations: int
    hvcs_lvcs_body_atr: float
    buffer_atr: float
    rollover_pre_min: int
    rollover_post_min: int
    rollover_flat_before_min: int
    aoi_zone_atr: float
    aoi_lookback: pd.Timedelta
    oe_origin: str                   # D8 baseline HOUR_OPEN
    early_shift_guard: str           # D9 baseline NONE
    window: pd.Timedelta
    min_legs: int
    prior_min_count: int
    prior_lookback: pd.Timedelta
    range_extreme: float
    pro_er_min: float
    pro_er_max: float
    oe_min_minutes: float
    oe_min_size_atr: float
    start_min: float
    end_min: float
    q30_push_atr: float
    fractal_pullback_min: float


def load_cbr1h(variant: str = "A") -> Cbr1hParams:
    cfg = yaml.safe_load(STRATEGY.read_text())
    p, m, ab = cfg["primitives"], cfg["models"]["CBR1H_BASELINE_V1"], cfg["ablations"]
    if variant not in m["variants"]:
        raise ValueError(f"unknown CBR1H variant {variant!r}")
    v = m["variants"][variant]
    return Cbr1hParams(
        model="CBR1H_BASELINE_V1", variant=variant, entry_model=v["entry_model"], aoi_required=bool(v["aoi_required"]),
        tick=_v(p["tick"]), atr_length=_v(p["atr_length"]), k_mtf=_v(p["swing"]["MTF"]["k"]),
        k_ltf=_v(p["swing"]["LTF"]["k"]), range_min=_v(p["condition"]["range_min"]),
        trend_max=_v(p["condition"]["trend_max"]), correction_cap=_v(p["condition"]["correction_cap"]),
        aggregate=_v(p["condition"]["aggregate"]), pullback_frac=_v(p["oe"]["pullback_frac"]),
        activation_atr=_v(p["oe"]["activation_atr"]), two_sided_frac=_v(p["oe"]["two_sided_frac"]),
        max_reversal_ltf=pd.Timedelta(minutes=_v(p["t3"]["max_reversal_minutes"]["LTF"])),
        hvcs_min_minutes=_v(p["hvcs"]["min_minutes"]), hvcs_max_violations=_v(p["hvcs"]["max_violations"]),
        hvcs_lvcs_body_atr=_v(p["hvcs"]["lvcs_body_atr"]), buffer_atr=_v(p["stop"]["buffer_atr"]),
        rollover_pre_min=_v(p["no_trade"]["rollover_pre_min"]), rollover_post_min=_v(p["no_trade"]["rollover_post_min"]),
        rollover_flat_before_min=_v(p["no_trade"]["rollover_flat_before_min"]),
        aoi_zone_atr=_v(p["aoi"]["zone_atr"]), aoi_lookback=pd.Timedelta(hours=_v(p["aoi"]["lookback_hours"])),
        oe_origin=_v(ab["oe_origin"]), early_shift_guard=_v(ab["early_shift_guard"]),
        window=pd.Timedelta(hours=_v(m["cond"]["window_hours"])), min_legs=_v(m["cond"]["min_legs"]),
        prior_min_count=_v(m["prior"]["min_count"]), prior_lookback=pd.Timedelta(hours=_v(m["prior"]["lookback_hours"])),
        range_extreme=_v(m["loc"]["range_extreme"]), pro_er_min=_v(m["loc"]["pro_er_min"]),
        pro_er_max=_v(m["loc"]["pro_er_max"]), oe_min_minutes=_v(m["oe"]["min_minutes"]),
        oe_min_size_atr=_v(m["oe"]["min_size_atr"]), start_min=_v(m["timing"]["start_min"]),
        end_min=_v(m["timing"]["end_min"]), q30_push_atr=_v(m["timing"]["q30_push_atr"]),
        fractal_pullback_min=_v(m["fractal"]["pullback_min"]))
