"""Phase 13C failure diagnosis (owner ruling D32). DIAGNOSTIC ONLY.

Nothing here changes PC3, PC2, the parity manifest or any scoring rule: the module re-runs the frozen PC3 engine
read-only and reconstructs what happened minute by minute. No trade outcomes, fills or P&L are read (D32).

    .venv/bin/python -m cbr.engine.phase13c_diagnosis hvcs      # reports/phase13c-hvcs-reconstruction.md
    .venv/bin/python -m cbr.engine.phase13c_diagnosis location  # reports/phase13c-cx-lt3-2-location.md
    .venv/bin/python -m cbr.engine.phase13c_diagnosis journal   # reports/phase13c-journal-reconstruction.md
"""

from __future__ import annotations

import json
import sys

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.engine import cbr1h_pc3 as pc3
from cbr.engine.common import prev_15m_break
from cbr.engine.params import ROOT
from cbr.engine.params_pc3 import load_cbr1h_pc3
from cbr.engine.phase13c_run import RUN_DIR, load_set
from cbr.structure.shifts_pc3 import hvcs_structural

M1, M15, H1, S5 = (pd.Timedelta(minutes=1), pd.Timedelta(minutes=15), pd.Timedelta(hours=1),
                   pd.Timedelta(seconds=5))
REPORTS = ROOT / "reports"
CASES = ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2")


def _t(v):
    return None if v is None or (not isinstance(v, pd.Timestamp) and pd.isna(v)) else pd.Timestamp(v)


def load_case(case: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    a, b = (pd.Timestamp(x) for x in case["data_span_utc"])
    return cb.load_structure(a, b, "1m"), cb.load_structure(a, b, "5s")


def scored_row(case: dict, want_shift: pd.Timestamp | None = None) -> tuple[pd.Series, str]:
    """The candidate the Phase 13C run scored, taken from the frozen run file so diagnosis studies the same event."""
    scored = json.loads((RUN_DIR / "run-1.json").read_text())["payload"]["cases"][case["case_id"]]
    sid = (scored.get("scored_candidate") or {}).get("signal_id")
    h0 = pd.Timestamp(case["start_time"])
    s1m, s5s = load_case(case)
    for variant in ("A", "B"):
        res = pc3.run_cbr1h_pc3(s1m, s5s, start=h0, end=h0 + H1, variant=variant,
                                params=load_cbr1h_pc3(variant))
        if not len(res.candidates):
            continue
        hit = res.candidates[res.candidates["signal_id"] == sid]
        if len(hit):
            return hit.iloc[0], variant
    raise SystemExit(f"scored candidate {sid} not reproducible for {case['case_id']}")


# ------------------------------------------------------------------ A/B/C: HVCS

def conforming(bars: pd.DataFrame, end: pd.Timestamp, direction: str, p) -> int:
    """Length of the PC3 conforming run ending at `end` (the reference candle is NOT counted)."""
    if end is None or end not in bars.index:
        return 0
    return int(hvcs_structural(bars.loc[:end], end, direction, atr_1m=1.0, min_minutes=p.hvcs_min_minutes,
                               lvcs_body_atr=p.hvcs_lvcs_body_atr).minutes)


def conforming_tolerant(bars: pd.DataFrame, end: pd.Timestamp, direction: str, max_violations: int) -> int:
    """PC3 structural conformity with PC2's violation tolerance, which PC3's rewrite dropped without a ruling."""
    if end is None or end not in bars.index:
        return 0
    upto = bars.loc[:end]
    h, lo = (upto[c].to_numpy(dtype=float) for c in ("high", "low"))
    length = violations = 0
    for i in range(len(upto) - 1, 0, -1):
        ok = (h[i] <= h[i - 1]) if direction == "DOWN" else (lo[i] >= lo[i - 1])
        if not ok:
            if length == 0:
                break
            violations += 1
            if violations > max_violations:
                break
        length += 1
    return length


def run_membership(bars: pd.DataFrame, direction: str, extreme: pd.Timestamp, shift: pd.Timestamp,
                   q_open: pd.Timestamp, p) -> dict[pd.Timestamp, list[str]]:
    """Which 1m bars each reading counts toward the duration, so the table can show it bar by bar."""
    closed_shift = bars[bars.index + M1 <= shift]
    last_shift = closed_shift.index[-1] if len(closed_shift) else None
    closed_q = bars[bars.index + M1 <= q_open]
    last_q = closed_q.index[-1] if len(closed_q) else None
    out: dict[pd.Timestamp, list[str]] = {}
    spans = [("H-A", extreme, conforming(bars, extreme, direction, p)),
             ("H-D", last_shift, conforming(bars, last_shift, direction, p)),
             ("H-F", last_q, conforming(bars, last_q, direction, p)),
             ("H-G", extreme, conforming_tolerant(bars, extreme, direction, p.hvcs_max_violations)),
             ("H-H", last_shift, conforming_tolerant(bars, last_shift, direction, p.hvcs_max_violations))]
    for name, end, n in spans:
        for i in range(n):
            if end is not None:
                out.setdefault(end - i * M1, []).append(name)
    return out


def interpretations(bars: pd.DataFrame, direction: str, extreme: pd.Timestamp, shift: pd.Timestamp,
                    q_open: pd.Timestamp, p) -> dict:
    """Every duration reading that Level-1 evidence can justify. None is preferred here; all are reported."""
    closed_before_shift = bars[bars.index + M1 <= shift]
    last_before_shift = closed_before_shift.index[-1] if len(closed_before_shift) else None
    closed_before_q = bars[bars.index + M1 <= q_open]
    last_before_q = closed_before_q.index[-1] if len(closed_before_q) else None
    a = conforming(bars, extreme, direction, p)
    d = conforming(bars, last_before_shift, direction, p)
    f = conforming(bars, last_before_q, direction, p)
    start_a = extreme - (a - 1) * M1 if a else None
    return {
        "H-A": {"value": a, "unit": "conforming 1m candles",
                "anchor": f"run ends at the extension-extreme bar {extreme:%H:%M}" if extreme is not None else "—",
                "note": "PC3 as implemented; the first candle of the sequence is the reference and is not counted"},
        "H-B": {"value": a + 1 if a else 0, "unit": "1m candles, inclusive",
                "anchor": "same run as H-A", "note": "counts the first candle of the sequence as minute 1"},
        "H-C": {"value": round((shift - start_a) / M1, 2) if start_a is not None else 0.0,
                "unit": "elapsed minutes", "anchor": f"first H-A candle open → 5s shift {shift:%H:%M:%S}",
                "note": "elapsed wall-clock reading of 'push for at least four minutes'"},
        "H-D": {"value": d, "unit": "conforming 1m candles",
                "anchor": f"run ends at the last 1m bar closed before the shift "
                          f"({last_before_shift:%H:%M})" if last_before_shift is not None else "—",
                "note": "'HVCS runs directly into the shift' (D19-6) read as the anchor, not the extension extreme"},
        "H-E": {"value": d + 1 if d else 0, "unit": "1m candles, inclusive", "anchor": "same run as H-D",
                "note": "H-D with the first candle counted"},
        "H-G": {"value": conforming_tolerant(bars, extreme, direction, p.hvcs_max_violations),
                "unit": "1m candles, ≤ 1 violation",
                "anchor": f"run ends at the extension-extreme bar {extreme:%H:%M}" if extreme is not None else "—",
                "note": f"PC3 conformity with PC2's `hvcs.max_violations` = {p.hvcs_max_violations} restored; PC3's "
                        "H-1 rewrite dropped that tolerance without D29 ruling on it"},
        "H-H": {"value": conforming_tolerant(bars, last_before_shift, direction, p.hvcs_max_violations),
                "unit": "1m candles, ≤ 1 violation",
                "anchor": f"run ends at the last 1m bar closed before the shift "
                          f"({last_before_shift:%H:%M})" if last_before_shift is not None else "—",
                "note": "H-G anchored at the shift instead of the extension extreme"},
        "H-F": {"value": f, "unit": "conforming 1m candles",
                "anchor": f"run ends at the last 1m bar closed before the entry 15m candle opens "
                          f"({last_before_q:%H:%M})" if last_before_q is not None else "—",
                "note": "master-slide order E1H-003: HVCS (4+ mins) and the take of the previous LTF/MTF extreme come "
                        "BEFORE 'after 15m open, PA create wick/pushes a bit more'"},
    }


def hvcs_table(case: dict) -> dict:
    row, variant = scored_row(case)
    s1m, s5s = load_case(case)
    p = load_cbr1h_pc3(variant)
    h0 = pd.Timestamp(case["start_time"])
    direction = row["oe_dir"]
    shift = _t(row["five_second_shift_time"])
    # PC3 re-evaluates the extension at the shift inside `_hvcs_at`, so the HVCS run is anchored to the extreme as
    # known then, not to the decision-time extreme. Reconstruct with the same anchor or the numbers will not match.
    ctx = pc3._Context(s1m, s5s, p)
    ext_at_shift = pc3._extension(ctx, h0, float(s1m.loc[h0, "open"]), shift, p)
    extreme = _t(ext_at_shift.extreme_time)
    extreme_at_decision = _t(row["oe_extreme_time"])
    activation = _t(row["extension_activation_time"])
    sweep = _t(row["five_second_sweep_time"])
    q_open = _t(row["q_open_utc"])
    q_prev = _t(row["q_prev_open_utc"])
    first = (extreme or shift) - 10 * M1
    win = s1m.loc[min(first, q_prev or first) - 5 * M1: shift]
    prev15 = s1m.loc[q_prev: q_open - M1] if q_prev is not None else None
    prev_hi = float(prev15["high"].max()) if prev15 is not None and len(prev15) else None
    prev_lo = float(prev15["low"].min()) if prev15 is not None and len(prev15) else None
    members = run_membership(s1m, direction, extreme, shift, q_open, p)
    rows, prev_bar, running = [], None, None
    for t, r in win.iterrows():
        respects = None if prev_bar is None else (bool(r["high"] <= prev_bar["high"]) if direction == "DOWN"
                                                  else bool(r["low"] >= prev_bar["low"]))
        progresses = bool(r["close"] < r["open"]) if direction == "DOWN" else bool(r["close"] > r["open"])
        new_ext = False
        active = activation is not None and t >= activation.floor("1min")
        if active and (running is None or ((r["low"] < running) if direction == "DOWN"
                                           else (r["high"] > running))):
            running, new_ext = (r["low"] if direction == "DOWN" else r["high"]), True
        prev_bar = r
        took_prev = None
        if prev_lo is not None and t >= q_open:
            took_prev = bool(r["low"] < prev_lo) if direction == "DOWN" else bool(r["high"] > prev_hi)
        marks = []
        if activation is not None and t <= activation < t + M1:
            marks.append("extension activation")
        if extreme is not None and t == extreme:
            marks.append("extension extreme")
        if q_open is not None and t == q_open:
            marks.append("entry 15m candle opens")
        if sweep is not None and t <= sweep < t + M1:
            marks.append("5s sweep")
        if shift is not None and t <= shift < t + M1:
            marks.append("5s shift / decision")
        rows.append({"time": f"{t:%H:%M}", "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]),
                     "close": float(r["close"]), "dir": "up" if r["close"] > r["open"] else
                     ("down" if r["close"] < r["open"] else "flat"), "new_extreme": new_ext, "respects": respects,
                     "conforming": bool(respects) if respects is not None else None, "progresses": progresses,
                     "counted_by": ", ".join(sorted(members.get(t, []))), "took_previous_15m": took_prev,
                     "marks": ", ".join(marks)})
    return {"case_id": case["case_id"], "variant": variant, "direction_of_extension": direction,
            "hour_open": str(h0), "activation": str(activation), "extreme": str(extreme),
            "extreme_at_decision": str(extreme_at_decision), "sweep": str(sweep),
            "shift": str(shift), "entry_15m_open": str(q_open), "previous_15m": [str(q_prev), str(q_open)],
            "previous_15m_high": prev_hi, "previous_15m_low": prev_lo,
            "pc3_hvcs_minutes": None if pd.isna(row["hvcs_minutes"]) else float(row["hvcs_minutes"]),
            "pc3_hvcs_state": bool(row["hvcs_rule_state"]) if row["hvcs_rule_state"] is not None else None,
            "min_minutes_required": p.hvcs_min_minutes,
            "interpretations": interpretations(s1m, direction, extreme, shift, q_open, p), "bars": rows}


def write_hvcs() -> dict:
    cases = {c["case_id"]: c for c in load_set()["cases"]}
    out = {cid: hvcs_table(cases[cid]) for cid in CASES}
    (REPORTS / "phase13c-hvcs-reconstruction.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13c-hvcs-reconstruction.md").write_text(hvcs_markdown(out))
    return {cid: {k: v["value"] for k, v in d["interpretations"].items()} for cid, d in out.items()}


def hvcs_markdown(out: dict) -> str:
    L = ["# Phase 13C — HVCS reconstruction and counting comparison", "",
         ("**Ruling:** D32 §4-7 · **Status:** DIAGNOSTIC ONLY. PC3 is unchanged and nothing here selects an "
          "interpretation. No trade outcomes were read."), "",
         "## Counting comparison (D32 §6)", "",
         "| Reading | " + " | ".join(CASES) + " | passes ≥ 4 |", "|---|---|---|---|---|"]
    keys = list(out[CASES[0]]["interpretations"])
    for k in keys:
        vals = [out[c]["interpretations"][k]["value"] for c in CASES]
        L.append(f"| **{k}** | " + " | ".join(str(v) for v in vals) + " | "
                 + f"{sum(1 for v in vals if v >= 4)}/3 |")
    L += ["", "| Reading | Anchor | What it means |", "|---|---|---|"]
    for k in keys:
        d = out[CASES[0]]["interpretations"][k]
        L.append(f"| {k} | {d['anchor'].split('(')[0].strip()} | {d['note']} |")
    L += ["", "Anchors differ per case; the anchor column shows CX-LT1-1's. Full per-case anchors are in the JSON.", ""]
    for cid in CASES:
        d = out[cid]
        L += [f"## {cid}", "",
              (f"Extension {d['direction_of_extension']} · activation {d['activation']} · extreme {d['extreme']} · "
               f"5s sweep {d['sweep']} · 5s shift {d['shift']} · entry 15m candle opens {d['entry_15m_open']}."),
              (f"Previous 15m candle {d['previous_15m'][0]} → {d['previous_15m'][1]}: "
               f"high {d['previous_15m_high']}, low {d['previous_15m_low']}."),
              (f"PC3 measured {d['pc3_hvcs_minutes']} conforming minutes against a required "
               f"{d['min_minutes_required']} → rule state {d['pc3_hvcs_state']}."), "",
              ("| Time | O | H | L | C | Dir | New extreme | Respects (Tom's test) | Progresses | Counted by | "
               "Took prev 15m | Markers |"), "|---|---|---|---|---|---|---|---|---|---|---|"]
        for b in d["bars"]:
            def fmt(x):
                return "—" if x is None else ("yes" if x else "no")
            L.append(f"| {b['time']} | {b['open']:.2f} | {b['high']:.2f} | {b['low']:.2f} | {b['close']:.2f} | "
                     f"{b['dir']} | {fmt(b['new_extreme'])} | {fmt(b['respects'])} | {fmt(b['progresses'])} | "
                     f"{b['counted_by'] or '—'} | {fmt(b['took_previous_15m'])} | {b['marks'] or ''} |")
        L += ["", "| Reading | Value | Anchor |", "|---|---|---|"]
        for k, v in d["interpretations"].items():
            L.append(f"| {k} | {v['value']} {v['unit']} | {v['anchor']} |")
        L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------ E: journal hours (OQ-49)

JOURNAL = ("JM-2025-10-16", "JM-2025-10-17", "JM-2025-10-29")
# Tom's five MTF models (E1H-010, V1H-mastering… 00:19:52). The engine implements the first three only.
MTF_MODELS = {
    "TRR PT": ("trending range, traded pro-trend", "in scope: TRENDING_RANGE + M1H-LOC-02"),
    "TRR CT": ("trending range, traded counter-trend", "in scope: TRENDING_RANGE + M1H-LOC-03"),
    "R": ("plain range", "in scope: RANGE + M1H-LOC-01"),
    "IFS": ("inverse fractal shift: trade the correction back toward 50% of an MTF impulse (E1H-011)",
            "OUT OF SCOPE: no PC2/PC3 condition class exists for FS/IFS"),
    "FS": ("fractal shift: continuation at ~50% of an MTF impulse (E1H-011)",
           "OUT OF SCOPE: no PC2/PC3 condition class exists for FS/IFS"),
}


def journal_case(case: dict) -> dict:
    h0 = pd.Timestamp(case["start_time"])
    s1m, s5s = load_case(case)
    want = case["direction"]
    hour_row, cands = None, []
    for variant in ("A", "B"):
        p = load_cbr1h_pc3(variant)
        res = pc3.run_cbr1h_pc3(s1m, s5s, start=h0, end=h0 + H1, variant=variant, params=p)
        hrows = res.hours[res.hours["hour_open_utc"] == h0]
        if hour_row is None and len(hrows):
            hour_row = hrows.iloc[0]
        if not len(res.candidates):
            continue
        for _, r in res.candidates[res.candidates["variant"] == variant].iterrows():
            cands.append({
                "signal_id": r["signal_id"], "variant": variant, "direction": r["direction"],
                "decision": str(_t(r["timestamp"])), "condition": r["condition"],
                "cond_direction": r["cond_direction"], "extension_state": r["extension_state"],
                "oe_dir": r["oe_dir"], "activation": str(_t(r["extension_activation_time"])),
                "oe_duration_min": None if pd.isna(r["oe_duration_min"]) else float(r["oe_duration_min"]),
                "oe_retracement_ratio": None if pd.isna(r["oe_retracement_ratio"]) else
                float(r["oe_retracement_ratio"]),
                "shift": str(_t(r["five_second_shift_time"])), "event": r["event"],
                "event_at_trigger": r["event_at_trigger"],
                "failed_decision": sorted(k for k, v in r["rules"].items() if v is False),
                "failed_trigger": sorted(k for k, v in r["rules_at_trigger"].items() if v is False),
            })
    same = [c for c in cands if c["direction"] == want]
    # Ordered divergence walk: the first gate at which the engine and the journal part company.
    if hour_row is not None and hour_row["condition"] in ("UNDEFINED", "TREND"):
        first = ("condition", (f"the hour is classified {hour_row['condition']} "
                               f"({int(hour_row['n_legs'])} MTF legs in the condition window), so no CBR1H setup of "
                               f"any kind can arm; the journal records '{case['stated']['condition']}'"))
    elif not same:
        first = ("direction", (f"the engine produced no {want} candidate in the hour ({len(cands)} candidates, "
                               f"all {sorted({c['direction'] for c in cands}) or '—'})"))
    elif all("M1H-OE-00-ACTIVE" in c["failed_decision"] for c in same):
        first = ("extension activation", "no same-direction candidate reached EXTENSION_ACTIVE")
    elif all(any(r.startswith("M1H-LOC") for r in c["failed_decision"]) for c in same):
        first = ("location", "every same-direction candidate fails a location rule")
    elif all(any(r.startswith(("M1H-6A-2", "M1H-6A-3")) for r in c["failed_decision"]) for c in same):
        first = ("previous-candle take", "every same-direction candidate fails the previous-15m rules")
    elif all(c["shift"] == "None" for c in same):
        first = ("structural trigger", "no same-direction candidate produced a 5s type-3 shift in the window")
    else:
        blocking = sorted({r for c in same for r in c["failed_trigger"]})
        first = ("eligibility", f"a same-direction candidate reached the trigger but failed {', '.join(blocking)}")
    model = case["stated"]["mtf_model"]
    return {"case_id": case["case_id"], "journal": case["stated"], "journal_direction": want,
            "hour": None if hour_row is None else {
                "condition": hour_row["condition"], "cond_direction": hour_row["cond_direction"],
                "n_legs": int(hour_row["n_legs"]), "c_med": None if pd.isna(hour_row["c_med"]) else
                float(hour_row["c_med"]), "range_high": float(hour_row["range_high"]),
                "range_low": float(hour_row["range_low"]),
                "window_start": str(_t(hour_row["condition_window_start"])),
                "window_basis": hour_row["condition_window_basis"],
                "tradable_minutes": int(hour_row["condition_tradable_minutes"]),
                "missing_minutes": int(hour_row["condition_missing_minutes"]),
                "hour_rules_failed": sorted(hour_row["rules_failed"])},
            "mtf_model_label": model, "mtf_model_meaning": MTF_MODELS.get(model, ("unmapped", "unmapped")),
            "candidates": cands, "same_direction_candidates": len(same),
            "first_divergence": {"gate": first[0], "detail": first[1]}}


def write_journal() -> dict:
    cases = {c["case_id"]: c for c in load_set()["cases"]}
    out = {cid: journal_case(cases[cid]) for cid in JOURNAL}
    (REPORTS / "phase13c-journal-reconstruction.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13c-journal-reconstruction.md").write_text(journal_markdown(out))
    return {cid: d["first_divergence"] for cid, d in out.items()}


def journal_markdown(out: dict) -> str:
    L = ["# Phase 13C — journal-hour reconstruction (OQ-49)", "",
         ("**Ruling:** D32 §9-13 · **Status:** DIAGNOSTIC ONLY. No rule was changed, no entry price or stop was "
          "inferred, and no outcome column of the journal was read."), "",
         "## First divergence per case", "", "| Case | Journal | Engine gate | Detail |", "|---|---|---|---|"]
    for cid, d in out.items():
        j = d["journal"]
        L.append(f"| {cid} | {d['journal_direction']} · {j['mtf_model']} · {j['condition']} · CB {j['cb_hour']} | "
                 f"**{d['first_divergence']['gate']}** | {d['first_divergence']['detail']} |")
    L += ["", "## MTF model labels (D32 §13)", "",
          ("Tom names five middle-timeframe models — \"you have TR CT, R, and you have IFS, and you have FS… those "
           "are the five types of middle time frame models\" (V1H-mastering_entry_timing… 00:19:52, L1; E1H-010, "
           "E1H-011). PC2 and PC3 classify only `RANGE`, `TRENDING_RANGE` (with a direction) and `TREND`/`UNDEFINED` "
           "as no-trade. There is no fractal-shift or inverse-fractal-shift condition class in either engine."), "",
          "| Journal label | Meaning in the course | Status against the implemented model |", "|---|---|---|"]
    for k, (meaning, status) in MTF_MODELS.items():
        L.append(f"| {k} | {meaning} | {status} |")
    L.append("")
    for cid, d in out.items():
        j, h = d["journal"], d["hour"]
        L += [f"## {cid}", "",
              (f"Journal row: {j['journal_time_local']} · {d['journal_direction']} · {j['mtf_model']} · "
               f"{j['condition']} · CB {j['cb_hour']} · {j['shifts']} · AOI {j['aoi']}. "
               f"Source level L1_FRAME_JOURNAL_TABLE (Tom's own record; no prices, no outcomes read)."), ""]
        if h:
            L += [(f"Engine hour: condition **{h['condition']}** (direction {h['cond_direction']}, "
                   f"{h['n_legs']} MTF legs, correction median "
                   f"{'—' if h['c_med'] is None else round(h['c_med'], 3)}), range {h['range_low']:.2f}-"
                   f"{h['range_high']:.2f}, condition window from {h['window_start']} ({h['window_basis']}, "
                   f"{h['tradable_minutes']} tradable minutes, {h['missing_minutes']} missing). "
                   f"Hour rules failed: {', '.join(h['hour_rules_failed']) or 'none'}."), ""]
        L += [f"**First divergence — {d['first_divergence']['gate']}:** {d['first_divergence']['detail']}", "",
              ("| Candidate | Var | Dir | Decision | Condition | Ext | Activation | Shift | Trigger verdict | "
               "Failing rules at trigger |"), "|---|---|---|---|---|---|---|---|---|---|"]
        for c in d["candidates"]:
            L.append(f"| `{c['signal_id'].split('/')[-1]}` | {c['variant']} | {c['direction']} | {c['decision']} | "
                     f"{c['condition']} | {c['oe_dir']} {c['extension_state']} | {c['activation']} | {c['shift']} | "
                     f"{c['event_at_trigger']} | {', '.join(c['failed_trigger']) or '—'} |")
        L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------ D + cross-case: evaluation instant

INSTANT_CASES = ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2", "JM-2025-10-17")


def instant_case(case: dict, signal_suffix: str | None = None) -> dict:
    """Every extension-derived rule evaluated at the decision instant (what PC3 does) and at the 5s shift instant.

    Both instants are causal: the shift is later than every bar close either reading uses. This only asks WHERE in
    canon's sequence the rule belongs. Nothing is changed.
    """
    h0 = pd.Timestamp(case["start_time"])
    s1m, s5s = load_case(case)
    if signal_suffix is None:
        row, variant = scored_row(case)
    else:
        variant = "A"
        res = pc3.run_cbr1h_pc3(s1m, s5s, start=h0, end=h0 + H1, variant=variant, params=load_cbr1h_pc3(variant))
        row = res.candidates[res.candidates["signal_id"].str.endswith(signal_suffix)].iloc[0]
    p = load_cbr1h_pc3(variant)
    ctx = pc3._Context(s1m, s5s, p)
    d, h_open = row["direction"], float(s1m.loc[h0, "open"])
    decision, shift = _t(row["timestamp"]), _t(row["five_second_shift_time"])
    rng_hi, rng_lo = float(row["range_high"]), float(row["range_low"])
    out = {"case_id": case["case_id"], "signal_id": row["signal_id"], "direction": d,
           "decision": str(decision), "shift": str(shift), "condition": row["condition"], "rules": {}}
    for label, as_of in (("decision", decision), ("shift", shift)):
        if as_of is None:
            continue
        ext = pc3._extension(ctx, h0, h_open, as_of, p)
        q0 = (as_of - pd.Timedelta(microseconds=1)).floor("15min")
        q = prev_15m_break(ctx.s5s, ctx.b15, q0, as_of, d)
        pos = None if ext.extreme is None else (ext.extreme - rng_lo) / (rng_hi - rng_lo)
        loc = None if pos is None else (pos >= p.range_extreme if d == "SELL" else pos <= 1 - p.range_extreme)
        hv = pc3._hvcs_at(ctx, h0, ext, as_of, p)
        vals = {
            "M1H-LOC-01": {"pass": bool(loc) if loc is not None else None,
                           "detail": f"extension extreme {ext.extreme:.2f} at "
                                     f"{ext.extreme_time:%H:%M} → range position {pos:.3f}"
                                     if pos is not None else "no extreme"},
            "M1H-OE-01": {"pass": bool(ext.state == "EXTENSION_ACTIVE" and ext.duration_min >= p.oe_min_minutes),
                          "detail": f"{ext.duration_min:.0f} min from activation (needs ≥ {p.oe_min_minutes})"},
            "M1H-OE-02": {"pass": bool(ext.no_pullback),
                          "detail": f"deepest retracement ratio "
                                    f"{'—' if ext.retracement_ratio is None else round(ext.retracement_ratio, 3)}"},
            "M1H-6A-2-PREV-15M-BROKEN-BY-Q": {
                "pass": bool(q["q_break_by_q"] or q["q_prev_closed_in_trade_direction"]),
                "detail": f"Q {q0:%H:%M} takes Q−1's "
                          f"{'high' if d == 'SELL' else 'low'}: {q['q_break_by_q']}; "
                          f"Q−1 closed in trade direction: {q['q_prev_closed_in_trade_direction']}"},
            "M1H-6A-3-NEW-EXTREME-IN-Q": {
                "pass": bool(ext.extreme_time is not None and ext.extreme_time >= q0),
                "detail": f"extension extreme {ext.extreme_time:%H:%M} vs Q open {q0:%H:%M}"
                          if ext.extreme_time is not None else "no extreme"},
            "M1H-6A-1-HVCS-INTO-SHIFT": {
                "pass": bool(hv["hvcs_rule_state"]),
                "detail": f"{hv['hvcs_minutes']} conforming minutes ending "
                          f"{'—' if hv['hvcs_end_time'] is None else format(hv['hvcs_end_time'], '%H:%M')} "
                          f"(needs ≥ {p.hvcs_min_minutes})"},
        }
        for rule, v in vals.items():
            out["rules"].setdefault(rule, {})[label] = v
    return out


def write_instant() -> dict:
    cases = {c["case_id"]: c for c in load_set()["cases"]}
    out = {}
    for cid in INSTANT_CASES:
        suffix = "/3" if cid == "JM-2025-10-17" else None
        out[cid] = instant_case(cases[cid], suffix)
    (REPORTS / "phase13c-evaluation-instant.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13c-evaluation-instant.md").write_text(instant_markdown(out))
    return {cid: {r: f"{v.get('decision', {}).get('pass')}→{v.get('shift', {}).get('pass')}"
                  for r, v in d["rules"].items()} for cid, d in out.items()}


def instant_markdown(out: dict) -> str:
    L = ["# Phase 13C — evaluation instant: decision vs shift", "",
         ("**Ruling:** D32 §5-8 · **Status:** DIAGNOSTIC ONLY. Both columns are causal — the 5s shift is later than "
          "every bar close either reading uses — so this asks only where in the course's sequence each rule belongs. "
          "PC3 is unchanged and no corrective run was made."), "",
         ("PC3 writes every extension-derived rule into the decision ledger at the instant the type-3 arms, and moves "
          "only the HVCS rule to the trigger (D29-11 / H-3). The master slide E1H-003 orders the model differently: "
          "HVCS (4+ mins) → beyond the previous LTF/MTF high → **after the 15m opens, price wicks / pushes a bit "
          "more** → HILO beyond structure → entry on the break. Everything up to the entry is allowed to complete "
          "before the trade exists."), ""]
    for cid, d in out.items():
        L += [(f"## {cid} — `{d['signal_id'].split('/')[-1]}` {d['direction']}, decision {d['decision']}, "
               f"shift {d['shift']}"), "",
              "| Rule | At decision (PC3) | At shift | Detail at decision | Detail at shift |",
              "|---|---|---|---|---|"]
        for rule, v in d["rules"].items():
            dec, sh = v.get("decision", {}), v.get("shift", {})
            def fmt(x):
                return "—" if x is None else ("PASS" if x else "**FAIL**")

            L.append(f"| `{rule}` | {fmt(dec.get('pass'))} | {fmt(sh.get('pass'))} | {dec.get('detail', '—')} | "
                     f"{sh.get('detail', '—')} |")
        L.append("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "hvcs":
        print(json.dumps(write_hvcs(), indent=2))
    elif cmd == "instant":
        print(json.dumps(write_instant(), indent=2))
    elif cmd == "journal":
        print(json.dumps(write_journal(), indent=2))
    else:
        raise SystemExit("usage: python -m cbr.engine.phase13c_diagnosis [hvcs|location|journal]")


if __name__ == "__main__":
    main()
