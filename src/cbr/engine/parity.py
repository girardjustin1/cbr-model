"""Phase 13 parity machinery (docs/governance/phase13-parity-protocol.md v0.2; owner rulings D18, D19-7…14).

Library only. The final parity run against the course examples is refused (`main`) until V-1 is loaded, the independent
calibration is complete and the numeric tolerances in `config/phase13_tolerances.yaml` are FROZEN.

  * Views (§2): BASELINE_SPEC runs the parity-candidate spec as frozen; STRICT_COURSE switches on ONE pre-registered
    D8/D9 alternative from `config/strategy.yaml → ablations` at a time. Scores are never merged.
  * Candidate selection (§5): engine information only; never Tom's entry price, time or outcome.
  * Mismatch taxonomy (§3): exactly one primary class per mismatch, first applicable in the approved order; other
    applicable classes are kept as secondary tags, and an implementation defect is never hidden behind an earlier class.
  * Calibration (§4): offset-adjusted FOREXCOM vs Dukascopy tolerance from non-course calibration days only.
"""

from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from cbr.engine.params import ROOT, STRATEGY

TOLERANCES = ROOT / "config" / "phase13_tolerances.yaml"
V1_DIR = ROOT / "data" / "raw" / "tradingview"
V1_FILES = ["v1_CX-LT1-1.csv", "v1_CX-TE1-1.csv", "v1_CX-LT3-2.csv", "v1_cal_2025-10-22.csv", "v1_cal_2025-11-11.csv"]

BASELINE_SPEC, STRICT_COURSE = "BASELINE_SPEC", "STRICT_COURSE"
DATA_LIMITATION, FEED_DIFFERENCE, EXECUTION_DEPENDENT = "DATA_LIMITATION", "FEED_DIFFERENCE", "EXECUTION_DEPENDENT"
OWNER_BASELINE_CHOICE, UNRESOLVED_SPEC_AMBIGUITY = "OWNER_BASELINE_CHOICE", "UNRESOLVED_SPEC_AMBIGUITY"
IMPLEMENTATION_BUG, CANON_MISMATCH = "IMPLEMENTATION_BUG", "CANON_MISMATCH"
MISMATCH_ORDER = [DATA_LIMITATION, FEED_DIFFERENCE, EXECUTION_DEPENDENT, OWNER_BASELINE_CHOICE,
                  UNRESOLVED_SPEC_AMBIGUITY, IMPLEMENTATION_BUG, CANON_MISMATCH]
PRE_BUG_CLASSES = set(MISMATCH_ORDER[:5])


# ------------------------------------------------------------------ views (§2)

def strict_course_ablations() -> list[dict]:
    """Every pre-registered single-rule alternative, one per run (never combined)."""
    ab = yaml.safe_load(STRATEGY.read_text())["ablations"]
    return [{name: option} for name, node in ab.items() for option in node["research_range"] if option != node["value"]]


def view_params(params, view: str, ablation: dict | None = None):
    """Parameters for a parity view. BASELINE_SPEC takes no ablation; STRICT_COURSE takes exactly one pre-registered one."""
    if view == BASELINE_SPEC:
        if ablation:
            raise ValueError("BASELINE_SPEC parity runs the frozen spec without ablations")
        return params
    if view != STRICT_COURSE:
        raise ValueError(f"unknown parity view {view!r}")
    if not ablation or len(ablation) != 1 or ablation not in strict_course_ablations():
        raise ValueError(f"STRICT_COURSE needs exactly one pre-registered D8/D9 alternative, got {ablation!r}")
    return dataclasses.replace(params, **ablation)


# ------------------------------------------------------------------ selection (§5)

_TIER_RANK = {"5s": 0, "1m": 1, "5m": 2}
_KIND_RANK = {"prior": 0, "same": 1}


def _t(value):
    return None if value is None or (not isinstance(value, pd.Timestamp) and pd.isna(value)) else pd.Timestamp(value)


def selection_key(row: pd.Series) -> tuple:
    """Frozen order: canonical 5s shift time first (candidates without a shift last), then decision time, activation
    time, structural tier, prior/same, signal id. Engine fields only."""
    shift = _t(row.get("five_second_shift_time"))
    activation = _t(row.get("activation_time", row.get("entry_trigger_time")))
    far = pd.Timestamp.max.tz_localize("UTC")
    return (shift is None, shift or far, _t(row["timestamp"]), activation or far,
            _TIER_RANK.get(row.get("hilo_tier", "5s"), 9), _KIND_RANK.get(row.get("hilo_kind", "prior"), 9),
            str(row["signal_id"]))


def rule_class(rule: str, params) -> str | None:
    """Which of classes 1-5 a failed rule belongs to on its own, if any (used only for the DIAGNOSTIC_ONLY row)."""
    if rule.startswith("NT_INCOMPLETE"):
        return DATA_LIMITATION
    if rule in ("M1H-OE-01", "M1H-OE-02") and getattr(params, "oe_origin", None) == "HOUR_OPEN":
        return OWNER_BASELINE_CHOICE                                     # D8: LAST_RESET is the pre-registered alternative
    if rule == "M1H-6A-1-HVCS-INTO-SHIFT":
        return UNRESOLVED_SPEC_AMBIGUITY                                 # OQ-44 indecision limit
    return None


def select_candidate(candidates: pd.DataFrame, variant: str, params=None) -> dict:
    """One engine-selected candidate per example and variant. `course` information is not an argument by design."""
    c = candidates[candidates["variant"] == variant] if len(candidates) else candidates
    if not len(c):
        return {"variant": variant, "selected": None, "diagnostic_only": None}
    ordered = sorted((r for _, r in c.iterrows()), key=selection_key)
    armed = [r for r in ordered if r["event"] == "ARMED"]
    if armed:
        return {"variant": variant, "selected": armed[0]["signal_id"], "diagnostic_only": None}
    near = [r for r in ordered if r["rules_failed"] and all(rule_class(x, params) in PRE_BUG_CLASSES
                                                           for x in r["rules_failed"])]
    return {"variant": variant, "selected": None,
            "diagnostic_only": None if not near else {"signal_id": near[0]["signal_id"], "label": "DIAGNOSTIC_ONLY",
                                                       "failed_rules": list(near[0]["rules_failed"])}}


# ------------------------------------------------------------------ mismatch taxonomy (§3)

@dataclass(frozen=True)
class MismatchEvidence:
    data_limitation: str | None = None             # why the dimension can't be evaluated from stored data
    feed_difference: str | None = None             # within frozen V-1 tolerance, or gone on FOREXCOM bars
    execution_dependent: str | None = None         # needs fill information (e.g. HTF_FILL_STATE)
    owner_baseline_choice: str | None = None       # disappears under exactly one pre-registered D8/D9 alternative
    open_question: str | None = None               # deciding rule governed by an open question
    failing_spec_test: str | None = None           # a failing unit test reproducing a contradiction of the frozen spec
    canon_evidence: str | None = None              # evidence that the engine follows the spec while the example differs


def classify_mismatch(ev: MismatchEvidence) -> dict:
    applicable = [cls for cls, flag in ((DATA_LIMITATION, ev.data_limitation), (FEED_DIFFERENCE, ev.feed_difference),
                                        (EXECUTION_DEPENDENT, ev.execution_dependent),
                                        (OWNER_BASELINE_CHOICE, ev.owner_baseline_choice),
                                        (UNRESOLVED_SPEC_AMBIGUITY, ev.open_question),
                                        (IMPLEMENTATION_BUG, ev.failing_spec_test)) if flag]
    if not applicable:
        if not ev.canon_evidence:
            raise ValueError("a CANON_MISMATCH needs cited evidence for the rule and the example")
        applicable = [CANON_MISMATCH]
    return {"primary": applicable[0], "secondary": applicable[1:],
            "implementation_bug": ev.failing_spec_test is not None,             # never concealed by an earlier class
            "blocks_gate": ev.failing_spec_test is not None,
            "evidence": {k: v for k, v in dataclasses.asdict(ev).items() if v}}


# ------------------------------------------------------------------ V-1 calibration (§4)

def load_tradingview_csv(path: Path) -> pd.DataFrame:
    """TradingView 'Export chart data' CSV (time as unix seconds or ISO, chart timezone UTC) → 1m OHLC, UTC index."""
    raw = pd.read_csv(path)
    raw.columns = [c.strip().lower() for c in raw.columns]
    t = raw["time"]
    if pd.api.types.is_numeric_dtype(t):
        idx = pd.to_datetime(t, unit="s", utc=True)                      # unix seconds are UTC by definition
    else:
        parsed = pd.to_datetime(t, format="ISO8601")
        if getattr(parsed.dt, "tz", None) is None:
            raise ValueError(f"{path.name}: ISO times without a UTC offset are ambiguous; export with ISO time + offset")
        idx = parsed.dt.tz_convert("UTC")
    out = raw[["open", "high", "low", "close"]].astype(float)
    out.index = pd.DatetimeIndex(idx, name="ts")
    if not out.index.is_monotonic_increasing or out.index.has_duplicates:
        raise ValueError(f"{path.name}: timestamps not strictly increasing")
    return out


def calibrate(forexcom: pd.DataFrame, dukascopy: pd.DataFrame, *, floor: float, percentile: float, round_to: float,
              feed_near_multiple: float, max_lag: int = 3) -> dict:
    """Offset-adjusted price tolerance from NON-course calibration minutes (§4.3). Reports sample count, distribution,
    median offset, pth percentile, max, per-day offsets and the lag check; nothing is frozen here."""
    j = forexcom[["high", "low", "close"]].join(dukascopy[["high", "low", "close"]], how="inner", lsuffix="_fx",
                                                 rsuffix="_dk")
    if not len(j):
        raise ValueError("no overlapping minutes")
    delta = float((j["close_fx"] - j["close_dk"]).median())
    per_day = (j["close_fx"] - j["close_dk"]).groupby(j.index.floor("1D")).median()
    resid = pd.concat([((j[f"{f}_fx"] - j[f"{f}_dk"]) - delta).abs() for f in ("high", "low", "close")])
    p_value = float(np.percentile(resid, percentile))
    tau = math.ceil(round(max(floor, p_value) / round_to, 9)) * round_to
    r_fx, r_dk = j["close_fx"].diff(), j["close_dk"].diff()
    lags = {lag: float(r_fx.corr(r_dk.shift(-lag))) for lag in range(-max_lag, max_lag + 1)}
    best = max(lags, key=lambda k: -math.inf if math.isnan(lags[k]) else lags[k])
    return {"n_minutes": len(j), "n_residuals": len(resid), "delta_median_offset": delta,
            "delta_per_day": {str(k.date()): float(v) for k, v in per_day.items()},
            "residual_quantiles": {q: float(np.percentile(resid, q)) for q in (50, 75, 90, 95, 99)},
            "residual_percentile": percentile, "residual_p": p_value, "residual_max": float(resid.max()),
            "tau_price": round(tau, 10), "feed_near": round(feed_near_multiple * tau, 10),
            "lag_correlations": lags, "best_lag_minutes": best, "zero_lag_confirmed": best == 0}


def compare_price(engine: float | None, course: float | None, *, delta: float, tau: float, feed_near: float) -> str:
    if engine is None or course is None:
        return "NOT_AVAILABLE"
    d = abs((course - delta) - engine)
    return "MATCH" if d <= tau else "FEED_NEAR" if d <= feed_near else "MISMATCH"


def compare_time(engine: pd.Timestamp | None, course: pd.Timestamp | None, *, course_has_seconds: bool,
                 one_minute_event: bool = False) -> str:
    """1m structural events: same canonical 1m bar. Tom timestamps: ±15 s with seconds, ±60 s without (D19-12)."""
    if engine is None or course is None:
        return "NOT_AVAILABLE"
    if one_minute_event:
        return "MATCH" if engine.floor("1min") == course.floor("1min") else "MISMATCH"
    tol = pd.Timedelta(seconds=15 if course_has_seconds else 60)
    return "MATCH" if abs(engine - course) <= tol else "MISMATCH"


def load_tolerances() -> dict:
    return yaml.safe_load(TOLERANCES.read_text())


def final_run_blockers() -> list[str]:
    """What still prevents the final Phase 13 parity run."""
    tol = load_tolerances()
    out = [f"V-1 file missing: data/raw/tradingview/{f}" for f in V1_FILES if not (V1_DIR / f).exists()]
    if tol.get("status") != "FROZEN":
        out.append(f"numeric tolerances not frozen (config/phase13_tolerances.yaml status {tol.get('status')})")
    if not tol.get("final_run_authorized"):
        out.append("final Phase 13 parity run not authorized by the owner")
    return out


def main() -> None:
    blockers = final_run_blockers()
    if blockers:
        raise SystemExit("Phase 13 final parity refused:\n- " + "\n- ".join(blockers))
    raise SystemExit("final scoring run not implemented before the protocol and tolerances are frozen")


if __name__ == "__main__":
    main()
