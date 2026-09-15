"""Phase 13 readiness diagnostics (owner ruling D18): what each competing interpretation changes on the three hourly
course examples. -> reports/phase13-readiness-diagnostics.{json,md}

Usage:
    .venv/bin/python -m cbr.engine.readiness_diagnostics

Structure facts only (STRUCTURE bars, D16): no fills, trade outcomes, P&L or rule selection. Tom's entry time is used only
as the point at which each interpretation is evaluated, never to choose an interpretation or a candidate. Canonical specs
and engines are unchanged; the alternatives are computed here, side by side, for the owner.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from cbr.data.canonical_bars import load_structure
from cbr.data.dukascopy_fetch import ROOT
from cbr.data.price_series import rollup_structure
from cbr.data.sessions import expected_closed_mask
from cbr.engine import cbr1h
from cbr.engine.common import M1, M15, S5
from cbr.engine.params import load_cbr1h, load_cbr15
from cbr.structure import condition as cond_mod
from cbr.structure import overextension as oe_mod
from cbr.structure.indicators import atr
from cbr.structure.shifts import hvcs, track_type3
from cbr.structure.swings import zigzag

REPORT_JSON = ROOT / "reports" / "phase13-readiness-diagnostics.json"
REPORT_MD = ROOT / "reports" / "phase13-readiness-diagnostics.md"
T = lambda s: pd.Timestamp(s, tz="UTC")
H1 = pd.Timedelta(hours=1)
EXAMPLES = {
    "CX-LT1-1": ("2025-10-20 00:00", "2025-10-21 06:00", "2025-10-21 01:00", "2025-10-21 01:39:15", "BUY"),
    "CX-TE1-1": ("2025-10-23 00:00", "2025-10-24 07:00", "2025-10-24 04:00", "2025-10-24 04:37:30", "BUY"),
    "CX-LT3-2": ("2025-11-07 00:00", "2025-11-10 04:00", "2025-11-10 01:00", "2025-11-10 01:40:00", "SELL"),
}


def _cond(sw, s1m, as_of, window, p):
    c = cond_mod.classify(sw, s1m, as_of, window, min_legs=p.min_legs, range_min=p.range_min, trend_max=p.trend_max,
                          correction_cap=p.correction_cap, aggregate=p.aggregate)
    ok = c.condition in (cond_mod.RANGE, cond_mod.TRENDING_RANGE) and not (
        c.condition == cond_mod.TRENDING_RANGE and c.direction == "NONE")
    return {"window_start": str(as_of - window), "window_hours": round(window / H1, 2), "condition": c.condition,
            "c_med": None if c.c_med is None else round(c.c_med, 3), "n_legs": c.n_legs, "direction": c.direction,
            "range_high": c.range_high, "range_low": c.range_low, "hour_rules_pass": ok}


def oq40(s1m, h0, p):
    """A clock hours · B tradable (expected-open) hours · C populated 5m bars · D since the weekly/daily reopen."""
    b5 = rollup_structure(s1m, "5min")
    sw = zigzag(b5, atr(b5, p.atr_length), p.k_mtf, pd.Timedelta(minutes=5))
    hours = p.window / H1
    out = {"A_clock_hours": _cond(sw, s1m, h0, p.window, p)}
    mins = pd.date_range(h0 - pd.Timedelta(days=5), h0, freq="1min", inclusive="left")
    open_mins = mins[~expected_closed_mask(mins)]
    need = int(hours * 60)
    start_b = open_mins[-need] if len(open_mins) >= need else open_mins[0]
    out["B_tradable_hours"] = _cond(sw, s1m, h0, h0 - start_b, p)
    need_bars = int(hours * 12)
    prior5 = b5[b5.index < h0]
    start_c = prior5.index[-need_bars] if len(prior5) >= need_bars else prior5.index[0]
    out["C_populated_5m_bars"] = _cond(sw, s1m, h0, h0 - start_c, p)
    closed = mins[expected_closed_mask(mins)]
    last_closed = closed[closed < h0]
    reopen = (last_closed[-1] + M1) if len(last_closed) else mins[0]
    d = _cond(sw, s1m, h0, max(h0 - reopen, pd.Timedelta(minutes=5)), p)
    d["segment"] = f"since the last expected closure ended ({reopen})"
    out["D_session_segment"] = d
    return out


def oq41(ctx, h0, h_open, at, p):
    """oe_prev_candle_break at Tom's entry time under different reference candles."""
    oe = oe_mod.evaluate(ctx.s1m, h0, h_open, at.floor("1min"), atr_1m=1.0, activation_atr=p.activation_atr,
                         pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac)
    refs = {}
    q_at = (at - pd.Timedelta(microseconds=1)).floor("15min")
    refs["R1_15m_before_candle_containing_decision"] = q_at - M15
    refs["R2_15m_before_candle_containing_oe_extreme"] = oe.extreme_time.floor("15min") - M15
    refs["R3_last_15m_of_previous_hour"] = h0 - M15
    out = {"oe_direction": oe.direction, "oe_extreme": oe.extreme, "oe_extreme_time": str(oe.extreme_time)}
    for name, q in refs.items():
        if q in ctx.b15.index:
            hi, lo = float(ctx.b15.loc[q, "high"]), float(ctx.b15.loc[q, "low"])
            brk = oe.extreme > hi if oe.direction == "UP" else oe.extreme < lo
            out[name] = {"candle_open": str(q), "high": hi, "low": lo, "break": bool(brk)}
    if (h0 - H1) in ctx.b1h.index:
        hi, lo = float(ctx.b1h.loc[h0 - H1, "high"]), float(ctx.b1h.loc[h0 - H1, "low"])
        out["R4_previous_hourly_candle"] = {"candle_open": str(h0 - H1), "high": hi, "low": lo,
                                            "break": bool(oe.extreme > hi if oe.direction == "UP" else oe.extreme < lo)}
    return out


def oq43(ctx, h0, h_open, at, p):
    """HVCS at Tom's entry time under different end bars (1m bars closed by the entry minute)."""
    at_m = at.floor("1min")
    closed = ctx.s1m[(ctx.s1m.index + M1 <= at_m)]
    oe = oe_mod.evaluate(ctx.s1m, h0, h_open, at_m, atr_1m=1.0, activation_atr=p.activation_atr,
                         pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac)
    a1 = float(ctx.atr1m[ctx.atr1m.index + M1 <= at_m].dropna().iloc[-1])

    def run(end):
        if end is None or end not in closed.index:
            return None
        hv = hvcs(closed, end, oe.direction, atr_1m=a1, min_minutes=p.hvcs_min_minutes,
                  max_violations=p.hvcs_max_violations, lvcs_body_atr=p.hvcs_lvcs_body_atr)
        return {"end_bar": str(end), "minutes": hv.minutes, "valid": hv.valid, "lvcs": hv.low_volume,
                "hilo_tier": "5m" if hv.low_volume else "1m"}
    best = None
    for e in closed.index[closed.index >= h0]:
        r = run(e)
        if r and (best is None or r["minutes"] > best["minutes"]):
            best = r
    j = at_m                                                   # the minute in which the entry break happens
    return {"oe_direction": oe.direction, "E1_longest_run_in_hour_up_to_decision (implemented)": best,
            "E2_last_displacement_bar (oe extreme bar)": run(oe.extreme_time),
            "E3_bar_before_the_breaking_bar (j-1)": run(j - M1),
            "E4_bar_two_before_the_break (j-2, the HILO reference bar's predecessor)": run(j - 2 * M1)}


def oq39(ctx, s5s, h0, at, side, p):
    """Which trigger families exist near Tom's entry: 5s type 3 breaks, 1m/5m HILO arms, 1m type 3 (fractal)."""
    k_s5 = load_cbr15().k_s5                                   # S5 tier swing threshold (CBR15 / primitives config)
    sw5 = zigzag(s5s, atr(s5s, p.atr_length), k_s5, S5)
    lo, hi = at - pd.Timedelta(minutes=5), at + pd.Timedelta(minutes=2)
    s5_arms = [a for a in track_type3(s5s[(s5s.index >= h0 - H1) & (s5s.index < h0 + H1)], sw5,
                                      max_reversal=pd.Timedelta(minutes=3), tick=p.tick, latest_pair_only=True)
               if a.direction == side and a.end == "BREAK" and lo <= a.end_time <= hi]
    hilo = []
    for tier, bars, tf in (("1m", ctx.s1m, M1), ("5m", ctx.b5, pd.Timedelta(minutes=5))):
        for a in cbr1h.hilo_arms(bars, s5s, tf, side, lo.floor(tf), hi, p.tick):
            touch = cbr1h._touch(s5s, side, a["trigger"], a["arm_time"], a["valid_until"])
            hilo.append({"tier": tier, "kind": a["kind"], "arm_time": str(a["arm_time"]), "trigger": round(a["trigger"], 3),
                         "touch": None if touch is None else str(touch)})
    ltf = [a for a in ctx.t3_ltf if a.direction == side and a.end == "BREAK" and h0 <= a.end_time < h0 + H1]
    return {"s5_type3_breaks_near_entry": [{"sweep": str(a.sweep_time), "break": str(a.end_time),
                                            "trigger": round(a.trigger_price, 3), "sweep_extreme": round(a.extreme_before_end, 3)}
                                           for a in s5_arms],
            "hilo_arms_near_entry": hilo,
            "ltf_1m_type3_breaks_in_hour": [{"break": str(a.end_time), "trigger": round(a.trigger_price, 3)} for a in ltf]}


def oq42(ctx, h0, h_open, at, side, p, candidate_decision):
    """:30 veto inputs evaluated at Tom's entry (fill-time reading) and at the engine decision (arm-time reading)."""
    def evaluate(t):
        oe = oe_mod.evaluate(ctx.s1m, h0, h_open, t.floor("1min"), atr_1m=1.0, activation_atr=p.activation_atr,
                             pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac)
        c30 = ctx.s1m[(ctx.s1m.index >= h0 + pd.Timedelta(minutes=30)) & (ctx.s1m.index + M1 <= t)]
        a1 = float(ctx.atr1m[ctx.atr1m.index + M1 <= t].dropna().iloc[-1])
        if not len(c30):
            return {"at": str(t), "in_30_candle": False}
        o30 = float(c30["open"].iloc[0])
        push = (c30["high"].max() - o30) if oe.direction == "UP" else (o30 - c30["low"].min())
        c15 = ctx.b15.loc[h0 + M15]
        exception = bool((c15["close"] < c15["open"]) if side == "SELL" else (c15["close"] > c15["open"]))
        pushed = bool(push >= p.q30_push_atr * a1)
        return {"at": str(t), "in_30_candle": h0 + pd.Timedelta(minutes=30) <= t < h0 + pd.Timedelta(minutes=45),
                "push_beyond_open": round(float(push), 3), "push_threshold": round(p.q30_push_atr * a1, 3),
                "pushed": pushed, "q15_closed_in_trade_direction": exception, "vetoed": not (pushed or exception)}
    return {"fill_time_reading (Tom's entry)": evaluate(at),
            "arm_time_reading (engine decision)": None if candidate_decision is None else evaluate(candidate_decision)}


def main() -> None:
    p = load_cbr1h("A")
    out = {"generated_utc": datetime.now(UTC).isoformat(), "examples": {}}
    for name, (a, b, h, tom, side) in EXAMPLES.items():
        s1, s5 = load_structure(T(a), T(b), "1m"), load_structure(T(a), T(b), "5s")
        ctx = cbr1h._Context(s1, s5, p)
        h0, at = T(h), T(tom)
        h_open = float(s1.loc[h0, "open"])
        res = cbr1h.run_cbr1h(s1, s5, start=h0, end=h0 + H1, variant="A")
        c = res.candidates
        first = c[c["direction"] == side].sort_values("timestamp")
        decision = None
        near = first[(first["timestamp"] <= at) & (first["timestamp"] >= at - pd.Timedelta(minutes=3))]
        if len(near):
            decision = near["timestamp"].iloc[-1]
        out["examples"][name] = {"hour_open": str(h0), "tom_entry": str(at), "side": side,
                                 "OQ-39": oq39(ctx, s5, h0, at, side, p), "OQ-40": oq40(s1, h0, p),
                                 "OQ-41": oq41(ctx, h0, h_open, at, p), "OQ-42": oq42(ctx, h0, h_open, at, side, p, decision),
                                 "OQ-43": oq43(ctx, h0, h_open, at, p)}
    REPORT_JSON.write_text(json.dumps(out, indent=2, default=str) + "\n")
    lines = ["# Phase 13 Readiness Diagnostics", "",
             (f"Generated {out['generated_utc']} by `src/cbr/engine/readiness_diagnostics.py`. STRUCTURE facts only; no fills, "
              "outcomes or P&L. Tom's entry time is only the evaluation point; nothing is selected by it."), ""]
    for name, e in out["examples"].items():
        lines += [f"## {name} ({e['side']}, entry {e['tom_entry']})", ""]
        for oq in ("OQ-39", "OQ-40", "OQ-41", "OQ-42", "OQ-43"):
            lines += [f"### {oq}", "", "```json", json.dumps(e[oq], indent=1, default=str), "```", ""]
    REPORT_MD.write_text("\n".join(lines))
    for name, e in out["examples"].items():
        print(name, {k: (v["condition"], v["n_legs"], v["hour_rules_pass"]) for k, v in e["OQ-40"].items()})


if __name__ == "__main__":
    main()
