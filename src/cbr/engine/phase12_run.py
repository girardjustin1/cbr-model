"""Phase 12 CBR1H parity on the hourly course examples -> reports/phase12-cbr1h-parity.{json,md}.

Usage:
    .venv/bin/python -m cbr.engine.phase12_run

Implementation parity only (holdout-period days, logged). Compares engine context, direction, extension, timing,
structure trigger, entry time, stop-anchor and target inputs, and acceptance with Tom's recorded trade. No fills, trade
outcomes or P&L. Also reruns CBR15 on the same hours with M15-HTF-01 fed by the CBR1H-A hourly state.

Tolerances (declared in this file before this report was first generated; set after an exploratory look at engine
output on these windows, so they are NOT pre-registered): price MATCH ≤ $0.50; FEED_NEAR ≤ $2.00 (Phase 9 measured
FOREX.com vs Dukascopy offsets up to $1.76); time MATCH ≤ 2 minutes.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime

import pandas as pd

from cbr.data.canonical_bars import load_structure
from cbr.data.dukascopy_fetch import ROOT
from cbr.engine import cbr1h, cbr15
from cbr.engine.common import anchor_at

REPORT_JSON = ROOT / "reports" / "phase12-cbr1h-parity.json"
REPORT_MD = ROOT / "reports" / "phase12-cbr1h-parity.md"
T = lambda s: pd.Timestamp(s, tz="UTC")
PRICE_MATCH, PRICE_NEAR, TIME_MATCH_MIN = 0.50, 2.00, 2.0

# Rule failure → mismatch class (with the governing decision / open question)
RULE_CLASS = {
    "M1H-OE-02": ("DECLARED_BASELINE_CHOICE", "D8 / OQ-22: V1 measures no-pullback from the hour open; LAST_RESET is a pre-registered ablation"),
    "M1H-COND-04": ("UNRESOLVED_INTERPRETATION", "OQ-36 scope: prior played-out setups (resolution basis not approved)"),
    "M1H-6A-4-HILO-TIER": ("SPEC_VS_EXAMPLE_CONFLICT", "OQ-39: this HILO's tier isn't the one spec 6A prescribes for the HVCS volume (1m normally, 5m when low-volume); Tom enters on a 5-second shift"),
    "M1H-COND-01": ("SOURCE_AMBIGUITY", "OQ-40: 8 h condition window measured in clock hours reaches into the weekend closure"),
    "M1H-COND-02": ("SOURCE_AMBIGUITY", "OQ-40: as above"),
    "M1H-TIME-01": ("EXPECTED", "order window already closed at the arm time"),
    "IMPL-REWARD": ("EXPECTED", "trigger beyond the 50% target"),
}

EXAMPLES = {
    "CX-LT1-1": {"span": ("2025-10-20 00:00", "2025-10-21 06:00", "2025-10-21 01:00"), "tom_entry_utc": "2025-10-21 01:39:15",
                 "direction": "BUY", "entry": 4340.13, "stop": 4332.96, "target": 4351.59,
                 "context": "RANGE", "context_quote": "relatively range bound over the past five to 12 plus hours",
                 "entry_model": "5s seconds shift", "target_note": "tool target; closed manually at ~1.3R"},
    "CX-TE1-1": {"span": ("2025-10-23 00:00", "2025-10-24 07:00", "2025-10-24 04:00"), "tom_entry_utc": "2025-10-24 04:37:30",
                 "direction": "BUY", "entry": 4105.58, "stop": 4102.80, "target": 4109.71,
                 "context": "TRENDING_RANGE (bearish, counter) or RANGE",
                 "context_quote": "Identified the condition as a trending range, a bearish trending range ... which is fine if it's more range bound, which it is",
                 "entry_model": "5s seconds shift ('a bit of a high low entry')",
                 "target_note": "tool levels may be illustrative (tool R:R 1.49 vs stated 2.3R)"},
    "CX-LT3-2": {"span": ("2025-11-07 00:00", "2025-11-10 04:00", "2025-11-10 01:00"), "tom_entry_utc": "2025-11-10 01:40:00",
                 "direction": "SELL", "entry": 4050.71, "stop": 4053.30, "target": 4043.80,
                 "context": "unclear: 'very bullish, a little bit trendy'", "context_quote": "So very bullish, um, a little bit trendy.",
                 "entry_model": "5s seconds shift with correlation", "target_note": "initial TP at a nearer level; 50% described as most aggressive"},
}


def _price_class(diff: float | None) -> str:
    if diff is None:
        return "NOT_AVAILABLE"
    a = abs(diff)
    return "MATCH" if a <= PRICE_MATCH else "FEED_NEAR" if a <= PRICE_NEAR else "MISMATCH"


def _nearest_candidate(c: pd.DataFrame, direction: str, tom: pd.Timestamp) -> pd.Series | None:
    sel = c[(c["direction"] == direction) & (c["timestamp"] >= tom - pd.Timedelta(minutes=5))
            & (c["timestamp"] <= tom + pd.Timedelta(minutes=1))].copy()
    if not len(sel):
        return None
    touch = sel["structure_trigger_touch_time"].map(lambda t: t if isinstance(t, pd.Timestamp) else pd.NaT)
    sel["dt"] = (pd.to_datetime(touch, utc=True) - tom).abs()
    sel = sel.sort_values(["dt", "timestamp"], na_position="last")
    return sel.iloc[0]


def parity(name: str, ex: dict, variant: str, s1, s5) -> tuple[dict, cbr1h.Cbr1hResult]:
    h0 = T(ex["span"][2])
    r = cbr1h.run_cbr1h(s1, s5, start=h0, end=h0 + pd.Timedelta(hours=1), variant=variant)
    tom = T(ex["tom_entry_utc"])
    hour = r.hours.iloc[0].to_dict() if len(r.hours) else {}
    oe, _, _ = cbr1h._oe(cbr1h._Context(s1, s5, r_params(variant)), h0, hour.get("h_open"), tom.floor("5s"),
                         r_params(variant)) if hour.get("h_open") is not None else (None, None, None)
    rows: dict = {"example": name, "variant": variant, "tom": ex, "hour": {k: hour.get(k) for k in
                  ("condition", "c_med", "n_legs", "cond_direction", "rules_failed", "context_reason", "h_open")}}
    comp = []
    comp.append({"dimension": "context", "engine": hour.get("condition"), "tom": ex["context"],
                 "class": ("MATCH" if hour.get("condition") and hour.get("condition") in ex["context"] else "MISMATCH")})
    if oe is not None:
        d = "SELL" if oe.direction == "UP" else "BUY"
        comp.append({"dimension": "direction", "engine": d, "tom": ex["direction"],
                     "class": "MATCH" if d == ex["direction"] else "MISMATCH"})
        comp.append({"dimension": "extension", "engine": {"dir": oe.direction, "duration_min": oe.duration_min,
                     "no_pullback": oe.no_pullback, "extreme": oe.extreme, "two_sided": oe.two_sided},
                     "tom": "hour pushed one way ~20-30 min into the range extreme",
                     "class": "MATCH" if (oe.duration_min >= 20 and oe.no_pullback and not oe.two_sided)
                     else "MISMATCH"})
    mih = (tom - h0) / pd.Timedelta(minutes=1)
    comp.append({"dimension": "timing_window", "engine": "22 ≤ mih ≤ 52", "tom": round(mih, 2),
                 "class": "MATCH" if 22 <= mih <= 52 else "MISMATCH"})
    c = r.candidates
    best = _nearest_candidate(c, ex["direction"], tom) if len(c) else None
    if best is None:
        comp.append({"dimension": "structure_trigger", "engine": None, "tom": ex["entry"], "class": "NOT_REPRODUCED"})
    else:
        touch = best["structure_trigger_touch_time"]
        touch = touch if isinstance(touch, pd.Timestamp) else None
        anchor_touch = anchor_at(best, touch + pd.Timedelta(seconds=5)) if touch is not None else None
        tdiff = None if touch is None else (touch - tom) / pd.Timedelta(minutes=1)
        target_touch = None if anchor_touch is None else anchor_touch - 0.5 * (anchor_touch - best["h_open"])
        comp += [
            {"dimension": "structure_trigger", "engine": {"trigger": best["entry_reference_price"], "tier": best["hilo_tier"],
             "kind": best["hilo_kind"], "decision": best["timestamp"]}, "tom": ex["entry"],
             "diff": round(best["entry_reference_price"] - ex["entry"], 3),
             "class": _price_class(best["entry_reference_price"] - ex["entry"])},
            {"dimension": "entry_time", "engine": touch, "tom": tom, "diff_min": None if tdiff is None else round(tdiff, 2),
             "class": "NOT_TOUCHED" if tdiff is None else ("MATCH" if abs(tdiff) <= TIME_MATCH_MIN else "MISMATCH")},
            {"dimension": "stop_anchor", "engine": {"at_activation": best["structure_stop_anchor"], "at_touch": anchor_touch},
             "tom": ex["stop"], "diff": None if anchor_touch is None else round(anchor_touch - ex["stop"], 3),
             "class": _price_class(None if anchor_touch is None else anchor_touch - ex["stop"])},
            {"dimension": "target_inputs", "engine": {"h_open": best["h_open"], "target_at_touch": target_touch},
             "tom": ex["target"], "diff": None if target_touch is None else round(target_touch - ex["target"], 3),
             "class": _price_class(None if target_touch is None else target_touch - ex["target"]), "note": ex["target_note"]},
            {"dimension": "acceptance", "engine": best["event"], "tom": "taken",
             "class": "MATCH" if best["event"] == "ARMED" else "MISMATCH",
             "failed_rules": [{"rule": k, "class": RULE_CLASS.get(k, ("UNCLASSIFIED", ""))[0],
                               "reason": RULE_CLASS.get(k, ("", "no classification"))[1]} for k in best["rules_failed"]]},
        ]
    for x in comp:
        x["mismatch_class"] = _dimension_class(name, variant, x)
    if len(c):
        near = c[(c["direction"] == ex["direction"]) & (c["timestamp"] >= tom - pd.Timedelta(minutes=3))
                 & (c["timestamp"] <= tom + pd.Timedelta(minutes=1))]
        rows["neighbours"] = [{"decision": str(n["timestamp"]), "tier": n["hilo_tier"], "kind": n["hilo_kind"],
                               "trigger": round(n["entry_reference_price"], 3),
                               "trigger_minus_tom": round(n["entry_reference_price"] - ex["entry"], 3),
                               "touch": None if not isinstance(n["structure_trigger_touch_time"], pd.Timestamp)
                               else str(n["structure_trigger_touch_time"]), "rules_failed": n["rules_failed"]}
                              for _, n in near.iterrows()]
    else:
        rows["neighbours"] = []
    rows["comparisons"] = comp
    rows["candidates_in_hour"] = len(c)
    rows["armed"] = len(r.signals)
    rows["rule_failures"] = Counter(x for f in c["rules_failed"] for x in f).most_common() if len(c) else []
    rows["hourly_state_at_tom_entry"] = [{k: (str(v) if isinstance(v, pd.Timestamp) else v) for k, v in s.items()}
                                         for s in cbr1h.hourly_state(r, tom)] if variant == "A" else None
    return rows, r


def _dimension_class(name: str, variant: str, x: dict) -> str | None:
    """Classification of a non-matching dimension (every mismatch gets one; none silently dropped)."""
    cls, dim = x["class"], x["dimension"]
    if cls == "MATCH":
        return None
    if cls == "FEED_NEAR":
        return "DATA_DIFFERENCE (feed/level offset within $2; Phase 9)"
    if dim == "extension":
        return "DECLARED_BASELINE_CHOICE (D8 / OQ-22: no-pullback measured from the hour open)"
    if dim == "context":
        return "SOURCE_AMBIGUITY (OQ-40: condition window across the weekend closure)"
    if dim == "structure_trigger" and cls == "NOT_REPRODUCED":
        return "SPEC_VS_EXAMPLE_CONFLICT (OQ-39: Tom's entry is a 5s shift; FRACTAL_1M found no completed 1m type 3)"
    if dim == "target_inputs":
        return "EXAMPLE_TARGET_NOT_SPEC_TARGET (" + EXAMPLES[name]["target_note"] + ")"
    if dim == "acceptance":
        return "COMPOSITE (see failed-rule classes)"
    return "UNCLASSIFIED"


def r_params(variant):
    from cbr.engine.params import load_cbr1h
    return load_cbr1h(variant)


def main() -> None:
    out = {"generated_utc": datetime.now(UTC).isoformat(), "tolerances": {"price_match": PRICE_MATCH,
           "price_feed_near": PRICE_NEAR, "time_match_min": TIME_MATCH_MIN, "pre_registered": False}, "examples": [],
           "cbr15_with_htf": []}
    for name, ex in EXAMPLES.items():
        a, b, h = (T(x) for x in ex["span"])
        s1, s5 = load_structure(a, b, "1m"), load_structure(a, b, "5s")
        for variant in ("A", "B"):
            rows, res = parity(name, ex, variant, s1, s5)
            out["examples"].append(rows)
            if variant == "A":
                c15 = cbr15.run_cbr15(s1, s5, start=h, end=h + pd.Timedelta(hours=1), htf=cbr1h.htf_provider(res))
                out["cbr15_with_htf"].append({"example": name, "candidates": len(c15.candidates),
                                              "htf_states": Counter(c15.candidates["htf_state"]).most_common()
                                              if len(c15.candidates) else [],
                                              "armed": len(c15.signals)})
    REPORT_JSON.write_text(json.dumps(out, indent=2, default=str) + "\n")
    REPORT_MD.write_text(render(out))
    for e in out["examples"]:
        print(e["example"], e["variant"], [(x["dimension"], x["class"]) for x in e["comparisons"]])
    print(out["cbr15_with_htf"])


def render(out: dict) -> str:
    L = ["# Phase 12: CBR1H Course-Example Parity", "",
         (f"Generated {out['generated_utc']} by `src/cbr/engine/phase12_run.py`. Implementation parity only: no fills, "
          "trade outcomes or P&L. Tolerances: price MATCH ≤ $0.50, FEED_NEAR ≤ $2.00, entry time MATCH ≤ 2 min "
          "(**not pre-registered**: set after an exploratory look at engine output on these windows)."), ""]
    for e in out["examples"]:
        L += [f"## {e['example']} · variant {e['variant']}", "",
              f"Hour context: {e['hour']} · candidates {e['candidates_in_hour']} · ARMED {e['armed']}", "",
              "| Dimension | Engine | Tom | Diff | Class | Mismatch classification |", "|---|---|---|---|---|---|"]
        for x in e["comparisons"]:
            diff = x.get("diff", x.get("diff_min", ""))
            L.append(f"| {x['dimension']} | {x['engine']} | {x['tom']} | {diff} | {x['class']} | {x.get('mismatch_class') or ''} |")
        acc = [x for x in e["comparisons"] if x["dimension"] == "acceptance"]
        if acc and acc[0].get("failed_rules"):
            L += ["", "Failed rules on the nearest candidate:", ""]
            L += [f"- `{f['rule']}` → **{f['class']}**: {f['reason']}" for f in acc[0]["failed_rules"]]
        if e["neighbours"]:
            L += ["", ("All candidates in the trade direction decided within [Tom − 3 min, Tom + 1 min] (selection "
                       "rule: closest structure touch to Tom's entry time, fixed before comparison):"), "",
                  "| Decision | Tier | Kind | Trigger | Trigger − Tom | Touch | Failed rules |", "|---|---|---|---|---|---|---|"]
            L += [f"| {n['decision'][11:19]} | {n['tier']} | {n['kind']} | {n['trigger']} | {n['trigger_minus_tom']} | "
                  f"{(n['touch'] or '—')[11:19] or '—'} | {', '.join(n['rules_failed'])} |" for n in e["neighbours"]]
        L += ["", f"Rule failures in the hour: {e['rule_failures']}", ""]
    L += ["## CBR15 rerun with M15-HTF-01 fed by CBR1H-A hourly state", ""]
    L += [f"- {x['example']}: {x['candidates']} candidates, HTF states {x['htf_states']}, ARMED {x['armed']}"
          for x in out["cbr15_with_htf"]]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
