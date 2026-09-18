"""OQ-48 / OQ-50 independent-example measurement (owner ruling D33 §3-5, §8). EVIDENCE MEASUREMENT ONLY.

This module reads stored 1-minute STRUCTURE bars and measures candle geometry. It does **not** run PC3, PC4 or any
candidate engine, it touches no parity case, and it reads no outcome, fill or P&L. The examples it measures were
located in Level-1 course frames and are independent of CX-LT1-1, CX-TE1-1 and CX-LT3-2.

    .venv/bin/python -m cbr.engine.oq48_examples      # reports/oq48-independent-examples.{md,json}
"""

from __future__ import annotations

import json

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.engine.params import ROOT
from cbr.engine.phase13c_diagnosis import conforming_tolerant
from cbr.structure.shifts_pc3 import hvcs_structural

M1 = pd.Timedelta(minutes=1)
REPORTS = ROOT / "reports"

# Located by reading Level-1 course frames; every field here comes from the frame or from stored bars, never from a
# model run. `shift_visual` is what the frame shows and is marked APPROXIMATE in the report.
EXAMPLES = [
    {"id": "HX-1", "video": "V1H-seconds_shift_1m_hilo_hvcs", "frame": "00:02:06-00:02:19",
     "quote": ("i want this sort of high volume uh candle sequence so you see we're respecting all the all the highs "
               "we're just you know consistently moving bearish … and then we have a shift, take out a low into "
               "taking out a high"),
     "chart_date_local": "Thu 23 Oct '25, GMT+11", "instrument": "XAUUSD", "extension_direction": "DOWN",
     "trade_direction": "BUY", "valid": True,
     "window": ("2025-10-23T05:05:00Z", "2025-10-23T05:35:00Z"),
     "sequence_visual": ("2025-10-23T05:18:00Z", "2025-10-23T05:26:00Z"),
     "extreme": "2025-10-23T05:26:00Z", "shift_visual": "2025-10-23T05:27:00Z",
     "q_open": "2025-10-23T05:15:00Z"},
    {"id": "HX-2", "video": "V1H-candle_behavior_extension", "frame": "00:03:38-00:03:47",
     "quote": ("around the halfway point of this of this 15 minute candle you have the high volume counter sequence "
               "into a high low entry this would be like a second shift"),
     "chart_date_local": "Wed 29 Oct '25, GMT+11", "instrument": "XAUUSD", "extension_direction": "DOWN",
     "trade_direction": "BUY", "valid": True,
     "window": ("2025-10-29T02:15:00Z", "2025-10-29T02:45:00Z"),
     "sequence_visual": ("2025-10-29T02:29:00Z", "2025-10-29T02:36:00Z"),
     "extreme": "2025-10-29T02:36:00Z", "shift_visual": "2025-10-29T02:37:00Z",
     "q_open": "2025-10-29T02:30:00Z"},
]
MIN_MINUTES = 4          # CANON (E1H-003, E1H-034); never varied here
MAX_VIOLATIONS = 1       # the configured ASSUMPTION PC3 stopped applying (F-1)


def bars(day_window: tuple[str, str]) -> pd.DataFrame:
    a, b = (pd.Timestamp(x) for x in day_window)
    return cb.load_structure(a.floor("1D"), b.ceil("1D"), "1m")


def measure(ex: dict) -> dict:
    s = bars(ex["window"])
    lo, hi = (pd.Timestamp(x) for x in ex["window"])
    d = ex["extension_direction"]
    extreme = pd.Timestamp(ex["extreme"])
    shift = pd.Timestamp(ex["shift_visual"])
    q_open = pd.Timestamp(ex["q_open"])
    last_before_shift = s[s.index + M1 <= shift].index[-1]
    last_before_q = s[s.index + M1 <= q_open].index[-1]

    def strict(end):
        return int(hvcs_structural(s.loc[:end], end, d, atr_1m=1.0, min_minutes=MIN_MINUTES,
                                   lvcs_body_atr=0.3).minutes)

    a = strict(extreme)
    dd = strict(last_before_shift)
    f = strict(last_before_q)
    g = conforming_tolerant(s, extreme, d, MAX_VIOLATIONS)
    h = conforming_tolerant(s, last_before_shift, d, MAX_VIOLATIONS)
    start_a = extreme - (a - 1) * M1 if a else None
    # The sequence as Tom circles it in the frame, described bar by bar.
    s0, s1 = (pd.Timestamp(x) for x in ex["sequence_visual"])
    seq = s.loc[s0:s1]
    prev = s.loc[:s0].iloc[-2] if len(s.loc[:s0]) > 1 else None
    violations = indecision = opposing = 0
    rows = []
    for t, r in seq.iterrows():
        respects = None if prev is None else (bool(r["high"] <= prev["high"]) if d == "DOWN"
                                              else bool(r["low"] >= prev["low"]))
        progresses = bool(r["close"] < r["open"]) if d == "DOWN" else bool(r["close"] > r["open"])
        if respects is False:
            violations += 1
        if r["close"] == r["open"]:
            indecision += 1
        elif not progresses:
            opposing += 1
        rows.append({"time": f"{t:%H:%M}", "open": float(r["open"]), "high": float(r["high"]),
                     "low": float(r["low"]), "close": float(r["close"]), "respects": respects,
                     "progresses": progresses})
        prev = r
    prev15 = s.loc[q_open - pd.Timedelta(minutes=15):q_open - M1]
    ref = float(prev15["low"].min()) if d == "DOWN" else float(prev15["high"].max())
    after = s.loc[q_open:shift]
    took = after[after["low"] < ref] if d == "DOWN" else after[after["high"] > ref]
    return {
        **{k: ex[k] for k in ("id", "video", "frame", "quote", "chart_date_local", "instrument",
                              "extension_direction", "trade_direction", "valid")},
        "window_utc": [str(lo), str(hi)],
        "sequence_visual_utc": [str(s0), str(s1)],
        "visible_candle_count": len(seq),
        "first_qualifying_candle": f"{start_a:%H:%M}" if start_a is not None else "UNKNOWN",
        "extension_extreme_candle": f"{extreme:%H:%M}",
        "shift_time": f"{shift:%H:%M} (APPROXIMATE, read from the frame)",
        "type3_arm_time": "UNKNOWN (determining it would require running a candidate engine, which is not authorized)",
        "type3_sweep_time": "UNKNOWN (same reason)",
        "entry_time": "UNKNOWN (no entry price or time is stated in the lesson)",
        "elapsed_minutes_sequence": (s1 - s0) / M1 + 1,
        "structural_violations_in_visible_sequence": violations,
        "indecision_bars": indecision,
        "opposing_close_bars": opposing,
        "previous_15m_window": [str(q_open - pd.Timedelta(minutes=15)), str(q_open)],
        "previous_15m_reference": ref,
        "q_takes_previous_15m_at": f"{took.index[0]:%H:%M}" if len(took) else "not before the shift",
        "readings": {"H-A": a, "H-B": a + 1 if a else 0,
                     "H-C": round((shift - start_a) / M1, 2) if start_a is not None else 0.0,
                     "H-D": dd, "H-E": dd + 1 if dd else 0, "H-F": f, "H-G": g, "H-H": h},
        "bars": rows,
    }


def classify(value: float) -> str:
    return "CONSISTENT" if value >= MIN_MINUTES else "INCONSISTENT"


def write() -> dict:
    out = [measure(e) for e in EXAMPLES]
    (REPORTS / "oq48-independent-examples.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    (REPORTS / "oq48-independent-examples.md").write_text(markdown(out))
    return {e["id"]: e["readings"] for e in out}


def markdown(out: list[dict]) -> str:
    keys = list(out[0]["readings"])
    L = ["# OQ-48 — independent Level-1 HVCS examples", "",
         ("**Ruling:** D33 §3-6 · **Status:** EVIDENCE MEASUREMENT ONLY. No engine, candidate or parity case was run; "
          "geometry is measured from stored Dukascopy 1-minute STRUCTURE bars. No outcome, fill or P&L was read. "
          "Neither example is CX-LT1-1, CX-TE1-1 or CX-LT3-2."), "",
         ("**Feed caveat.** The lesson charts are FOREX.com; the measurements below are Dukascopy. A marginal "
          "one-tick difference could move a single structural violation, which is why the tables report the "
          "violation positions rather than only a count."), "",
         "## Reading comparison across the independent examples", "",
         "| Reading | " + " | ".join(e["id"] for e in out) + " | verdict |", "|---|---|---|---|"]
    for k in keys:
        vals = [e["readings"][k] for e in out]
        verdicts = {classify(v) for v in vals}
        L.append(f"| {k} | " + " | ".join(str(v) for v in vals) + " | "
                 + ("CONSISTENT" if verdicts == {"CONSISTENT"} else
                    "INCONSISTENT" if verdicts == {"INCONSISTENT"} else "MIXED") + " |")
    L.append("")
    for e in out:
        L += [f"## {e['id']} — {e['video']} @ {e['frame']}", "",
              f"> {e['quote']}", "",
              (f"{e['instrument']} · chart date {e['chart_date_local']} · extension "
               f"{e['extension_direction']} · trade {e['trade_direction']} · Tom presents it as "
               f"{'VALID' if e['valid'] else 'REJECTED'}."), "",
              "| Field | Value |", "|---|---|",
              f"| Visible sequence (UTC) | {e['sequence_visual_utc'][0]} → {e['sequence_visual_utc'][1]} |",
              f"| Visible 1m candles | {e['visible_candle_count']} |",
              f"| First qualifying candle (PC3 run) | {e['first_qualifying_candle']} |",
              f"| Extension-extreme candle | {e['extension_extreme_candle']} |",
              f"| 5s / HILO shift | {e['shift_time']} |",
              f"| Type-3 arm time | {e['type3_arm_time']} |",
              f"| Type-3 sweep time | {e['type3_sweep_time']} |",
              f"| Entry time | {e['entry_time']} |",
              f"| Elapsed duration of the visible sequence | {e['elapsed_minutes_sequence']:.0f} min |",
              f"| Structural violations inside it | {e['structural_violations_in_visible_sequence']} |",
              f"| Indecision bars | {e['indecision_bars']} |",
              f"| Opposing-close bars | {e['opposing_close_bars']} |",
              f"| Previous 15m window | {e['previous_15m_window'][0]} → {e['previous_15m_window'][1]} |",
              f"| Previous 15m reference | {e['previous_15m_reference']:.2f} |",
              f"| Q takes it at | {e['q_takes_previous_15m_at']} |", "",
              "| Time | O | H | L | C | Respects | Progresses |", "|---|---|---|---|---|---|---|"]
        for b in e["bars"]:
            fmt = {True: "yes", False: "**no**", None: "—"}
            L.append(f"| {b['time']} | {b['open']:.2f} | {b['high']:.2f} | {b['low']:.2f} | {b['close']:.2f} | "
                     f"{fmt[b['respects']]} | {fmt[b['progresses']]} |")
        L += ["", "| Reading | Value | ≥ 4 |", "|---|---|---|"]
        for k in keys:
            v = e["readings"][k]
            L.append(f"| {k} | {v} | {'yes' if v >= MIN_MINUTES else '**no**'} |")
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    print(json.dumps(write(), indent=2))
