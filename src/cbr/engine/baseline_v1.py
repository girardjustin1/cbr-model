"""CBR1H_BASELINE_V1 — the research baseline alias (owner decision D37 §7).

**This module adds no behaviour.** It is a name that resolves to the frozen PC4 specification and refuses to resolve
to anything else. Phase 14A consumes signals through this alias so that a future candidate cannot silently become
"the baseline" by being imported instead.

    from cbr.engine.baseline_v1 import BASELINE, run_baseline
    result = run_baseline(s1m, s5s, start=..., end=..., variant="A")

D37 §7 and §10: the alias must point at the exact frozen PC4 hash, and no strategy behaviour may change before the
untouched baseline. `verify()` is called on every run, so a drifted spec stops the caller rather than producing
silently different signals.
"""

from __future__ import annotations

import pandas as pd

from cbr.engine import cbr1h_pc4 as pc4
from cbr.engine.params_pc4 import Cbr1hPC4Params, load_cbr1h_pc4, spec_hash_pc4

BASELINE = "CBR1H_BASELINE_V1"
CANDIDATE = "CBR1H_BASELINE_V1-PC4"
FROZEN_SPEC_HASH = "62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7"
PARITY_RUN = "CBR-RUN-013D-1"
PARITY_VERDICT = "FAIL"                 # never restate this as PASS (D37 §8)
GOVERNANCE_STATUS = "RESEARCH-SUFFICIENT WITH DOCUMENTED FIDELITY CONCERNS"
PROMOTION_RULING = "D37"
# Carried into every baseline result so no downstream report can present the model as validated.
FIDELITY_CONCERNS = (
    "OQ-48: HVCS counting/anchor semantics are not uniquely specified by the corpus",
    "OQ-50: previous-15m evaluation semantics are resolved for research use, not uniquely proven",
    "OQ-52: the MTF condition is classified once at the hour open, which can reject a setup the source took",
    "OQ-53: the ~20-minute extension figure is canonical guidance, implemented as a hard floor",
    "CX-LT3-2 is a DISCRETIONARY_REFERENCE_CASE the frozen model does not reproduce",
)


class BaselineDrift(RuntimeError):
    """The alias no longer resolves to the frozen specification."""


def verify() -> str:
    live = spec_hash_pc4()
    if live != FROZEN_SPEC_HASH:
        raise BaselineDrift(
            f"{BASELINE} must resolve to the frozen {CANDIDATE} spec {FROZEN_SPEC_HASH}, got {live}. "
            "A strategy-rule change before the untouched baseline invalidates the baseline designation and "
            "requires a new version (D37 §10).")
    return live


def params(variant: str = "A") -> Cbr1hPC4Params:
    verify()
    return load_cbr1h_pc4(variant)


def run_baseline(s1m: pd.DataFrame, s5s: pd.DataFrame, *, start: pd.Timestamp, end: pd.Timestamp,
                 variant: str = "A", params_override: Cbr1hPC4Params | None = None) -> pc4.Cbr1hPC4Result:
    """Frozen PC4 signal generation, reached by its baseline name. Signal logic is never modified here."""
    verify()
    return pc4.run_cbr1h_pc4(s1m, s5s, start=start, end=end, variant=variant,
                             params=params_override or load_cbr1h_pc4(variant))


def provenance() -> dict:
    """What every Phase 14A artefact must carry, so the promotion is never mistaken for a parity pass."""
    return {"baseline": BASELINE, "candidate": CANDIDATE, "spec_hash": verify(),
            "parity_run": PARITY_RUN, "parity_verdict": PARITY_VERDICT,
            "governance_status": GOVERNANCE_STATUS, "promotion_ruling": PROMOTION_RULING,
            "fidelity_concerns": list(FIDELITY_CONCERNS)}
