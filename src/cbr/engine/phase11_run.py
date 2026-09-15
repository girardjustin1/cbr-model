"""Phase 11 CBR15 engine run on the course-example windows -> reports/phase11-cbr15-engine.{json,md}.

Usage:
    .venv/bin/python -m cbr.engine.phase11_run

Implementation parity use only (holdout-period days, logged). Reports rule outcomes, candidates and ARMED signals.
No fills, trade outcomes, P&L or aggregate raw-setup outcomes are reported. The course examples are CBR1H trades, so
CBR15 output on these windows is informational, not a parity verdict (Phase 13).
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime

import pandas as pd

from cbr.data.canonical_bars import load_structure
from cbr.data.dukascopy_fetch import ROOT
from cbr.engine import cbr15

REPORT_JSON = ROOT / "reports" / "phase11-cbr15-engine.json"
REPORT_MD = ROOT / "reports" / "phase11-cbr15-engine.md"
T = lambda s: pd.Timestamp(s, tz="UTC")
# (warm-up start, data end, first candle, end) per course example; warm-up covers ATR(15m,14), 2 h condition window,
# 120 min prior-setup lookback. Tom's reference prices from reports/signal-parity-notes.md / course_examples.jsonl.
WINDOWS = {
    "CX-LT1-1": {"span": ("2025-10-20 18:00", "2025-10-21 06:00", "2025-10-21 01:00", "2025-10-21 02:00"),
                 "tom": {"direction": "BUY", "entry_utc": "2025-10-21 01:39", "entry": 4340.13, "stop": 4332.96,
                         "target": 4351.59, "model": "CBR1H"}},
    "CX-TE1-1": {"span": ("2025-10-23 20:00", "2025-10-24 06:00", "2025-10-24 04:00", "2025-10-24 05:00"),
                 "tom": {"direction": "BUY", "entry_utc": "2025-10-24 04:37", "model": "CBR1H"}},
    "CX-LT3-2": {"span": ("2025-11-07 12:00", "2025-11-10 03:00", "2025-11-10 01:00", "2025-11-10 02:00"),
                 "tom": {"direction": "SELL", "entry_utc": "2025-11-10 01:40", "model": "CBR1H"}},
}
SHOW = ["signal_id", "timestamp", "direction", "event", "rules_failed", "rules_not_evaluated", "condition", "n_legs",
        "c_med", "oe_duration_min", "oe_size", "oe_extreme", "sweep_bar_extreme", "sweep_beyond_oe_extreme",
        "t3_extreme_before_end", "entry_reference_price", "target_price", "prior_setup_count", "cancel_reason",
        "structure_trigger_touch_time"]


def run_window(name: str, spec: dict) -> dict:
    a, b, c, d = (T(x) for x in spec["span"])
    s1, s5 = load_structure(a, b, "1m"), load_structure(a, b, "5s")
    res = cbr15.run_cbr15(s1, s5, start=c, end=d)
    again = cbr15.run_cbr15(s1, s5, start=c, end=d)
    full = cbr15.decision_frame(res)
    causal = []
    for cut in pd.date_range(c + pd.Timedelta(minutes=10), d, freq="20min"):
        k1, k5 = s1[s1.index + pd.Timedelta(minutes=1) <= cut], s5[s5.index + pd.Timedelta(seconds=5) <= cut]
        tr = cbr15.decision_frame(cbr15.run_cbr15(k1, k5, start=c, end=d))
        want = full[full["timestamp"] <= cut].reset_index(drop=True)
        got = tr[tr["timestamp"] <= cut].reset_index(drop=True)
        causal.append({"cut": cut.isoformat(), "decisions": len(want), "identical": want.equals(got)})
    cand = res.candidates
    return {
        "window": name, "span_utc": list(spec["span"]), "tom": spec["tom"], "spec_hash": res.spec_hash,
        "result_hash": cbr15.result_hash(res), "deterministic": cbr15.result_hash(res) == cbr15.result_hash(again),
        "causality_truncation": causal,
        "candles": json.loads(res.candles.to_json(orient="records", date_format="iso")),
        "candidates": json.loads(cand[SHOW].to_json(orient="records", date_format="iso")) if len(cand) else [],
        "rule_failures": Counter(x for f in cand["rules_failed"] for x in f).most_common() if len(cand) else [],
        "armed_signals": res.signals,
    }


def render(r: dict) -> str:
    L = ["# Phase 11: CBR15 Reference Engine Run (course-example windows)", "",
         (f"Generated {r['generated_utc']} by `src/cbr/engine/phase11_run.py`. Implementation parity use only: no "
          "fills, trade outcomes or P&L. The course examples are **CBR1H** trades; CBR15 output here is informational."),
         ""]
    for w in r["windows"]:
        L += [f"## {w['window']}", "",
              f"Tom (CBR1H): {w['tom']}. Candles {w['span_utc'][2]} → {w['span_utc'][3]} UTC, warm-up from {w['span_utc'][0]}.",
              (f"Deterministic: {w['deterministic']} · causality (truncation at {len(w['causality_truncation'])} cut "
               f"times): {all(x['identical'] for x in w['causality_truncation'])} · spec hash `{w['spec_hash'][:12]}`"),
              "",
              "| Candle | Condition | Legs | c_med | Candle-level failures | Candidates |", "|---|---|---|---|---|---|"]
        for c in w["candles"]:
            cm = "—" if c["c_med"] is None else f"{c['c_med']:.3f}"
            L.append(f"| {c['candle_open_utc'][11:16]} | {c['condition']} | {c['n_legs']} | {cm} | "
                     f"{', '.join(c['rules_failed']) or '—'} | {c['candidates']} |")
        L += ["", ("| Decision (UTC) | Dir | Event | Failed rules | Not evaluated | OE dur | OE extreme | 5s sweep bar | "
                   "Sweep beyond OE | Trigger | Target | Prior 60m | Cancel |"),
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in w["candidates"]:
            L.append(f"| {c['timestamp'][11:19]} | {c['direction']} | {c['event']} | {', '.join(c['rules_failed']) or '—'} | "
                     f"{', '.join(c['rules_not_evaluated'])} | {c['oe_duration_min']:.0f} | {c['oe_extreme']:.3f} | "
                     f"{c['sweep_bar_extreme']:.3f} | {c['sweep_beyond_oe_extreme']} | {c['entry_reference_price']:.3f} | "
                     f"{c['target_price']:.3f} | {c['prior_setup_count']} | {c['cancel_reason']} |")
        L += ["", f"Rule failure counts: {w['rule_failures']}", f"ARMED signals: {len(w['armed_signals'])}", ""]
    return "\n".join(L)


def main() -> None:
    r = {"generated_utc": datetime.now(UTC).isoformat(), "windows": [run_window(k, v) for k, v in WINDOWS.items()]}
    REPORT_JSON.write_text(json.dumps(r, indent=2, default=str) + "\n")
    REPORT_MD.write_text(render(r))
    for w in r["windows"]:
        print(w["window"], "candidates", len(w["candidates"]), "armed", len(w["armed_signals"]), "deterministic",
              w["deterministic"], "causal", all(x["identical"] for x in w["causality_truncation"]))


if __name__ == "__main__":
    main()
