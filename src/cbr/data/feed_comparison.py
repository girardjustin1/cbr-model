"""Recent FOREXCOM vs Dukascopy feed comparison and higher-timeframe fidelity (CBR-PROT-013B §7; owner ruling D25).

Supporting evidence only (D24-7/8, D25-P2/P4). Nothing here selects parameters, tunes thresholds or feeds the signal
engine: FOREXCOM bars have a reference role. The structure primitives (swings, condition, overextension, type 3, HILO)
run on both feeds with the frozen PC2 parameters; `run_cbr1h` never sees FOREXCOM bars. Both feeds are restricted to the
same comparison minutes, so coverage differences can't masquerade as structure differences.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from cbr.data.sessions import expected_closed_mask, tradable_window_start
from cbr.engine import parity
from cbr.engine.common import _atr_at, _er
from cbr.engine.params import Cbr1hParams
from cbr.structure import condition as cond_mod
from cbr.structure import overextension as oe_mod
from cbr.structure.indicators import atr
from cbr.structure.shifts import hilo, track_type3
from cbr.structure.swings import legs, usable, zigzag

M1, M5, M15, H1 = (pd.Timedelta(minutes=1), pd.Timedelta(minutes=5), pd.Timedelta(minutes=15), pd.Timedelta(hours=1))
OHLC = ["open", "high", "low", "close"]
Z95 = 1.96
HOUR_RULES = ["M1H-COND-01", "M1H-COND-02", "M1H-COND-03", "M1H-LOC-01", "M1H-LOC-02", "M1H-LOC-03", "M1H-OE-01",
              "M1H-OE-02", "M1H-OE-04a", "M1H-OE-04b", "M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"]


# ------------------------------------------------------------------ basics

def wilson(k: int, n: int, z: float = Z95) -> list[float] | None:
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(centre - half, 6), round(centre + half, 6)]


def rate(k: int, n: int) -> dict:
    return {"agree": int(k), "n": int(n), "rate": None if n == 0 else round(k / n, 6), "wilson95": wilson(k, n)}


def comparison_minutes(days: list[str], start: pd.Timestamp) -> pd.DatetimeIndex:
    """Scheduled-open minutes of the given UTC days, from `start`."""
    out = pd.DatetimeIndex([], tz="UTC")
    for d in days:
        m = pd.date_range(pd.Timestamp(d, tz="UTC"), periods=24 * 60, freq="1min")
        out = out.append(m[~expected_closed_mask(m)])
    return out[out >= start]


def ns(frame: pd.DataFrame) -> pd.DataFrame:
    """Same frame with a nanosecond index in one UTC tz object. Exports load in seconds with `datetime.timezone.utc`,
    stored bars in milliseconds with `ZoneInfo("UTC")`; joining the two gives a plain Index."""
    out = frame.copy()
    out.index = pd.DatetimeIndex(out.index).tz_convert("UTC").as_unit("ns")
    return out


def restrict(bars: pd.DataFrame, minutes: pd.DatetimeIndex) -> pd.DataFrame:
    return ns(bars[bars.index.isin(minutes)][OHLC].astype(float))


def rollup(bars_1m: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Clock-aligned OHLC roll-up with the count of 1m bars per interval (same arithmetic as `rollup_structure`)."""
    g = bars_1m.resample(freq, label="left", closed="left")
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                        "close": g["close"].last(), "bars": g["open"].count()})
    return out[out["bars"] > 0]


def full_intervals(minutes: pd.DatetimeIndex, present: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    """Interval opens whose every scheduled-open minute in `minutes` is present in `present`."""
    s = pd.Series(minutes.isin(present), index=minutes)
    ok = s.groupby(minutes.floor(freq)).all()
    return pd.DatetimeIndex(ok[ok].index)


def direction(bars: pd.DataFrame) -> pd.Series:
    return np.sign(bars["close"] - bars["open"])


# ------------------------------------------------------------------ event matching

def match_events(a: pd.DataFrame, b: pd.DataFrame, key: list[str], tol: pd.Timedelta) -> pd.DataFrame:
    """One-to-one matching of events with equal `key` columns and |time difference| ≤ tol, greedy in time order of `a`
    (each `a` event takes the nearest still-unmatched `b` event; ties → the earlier one). Deterministic."""
    rows = []
    groups = {}
    for k, g in (b.groupby(key, sort=True) if len(b) else []):
        g = g.sort_values(["time"], kind="stable")
        groups[k if isinstance(k, tuple) else (k,)] = (g.index.to_numpy(), g["time"].to_numpy(dtype="datetime64[ns]"),
                                                       np.zeros(len(g), dtype=bool))
    tol_ns = np.timedelta64(int(tol.value), "ns")
    for ia, ea in a.sort_values(["time", *key], kind="stable").iterrows():
        grp = groups.get(tuple(ea[k] for k in key))
        if grp is None:
            continue
        idx, times, used = grp
        t = np.datetime64(pd.Timestamp(ea["time"]).tz_convert("UTC").tz_localize(None), "ns")
        lo, hi = np.searchsorted(times, t - tol_ns, "left"), np.searchsorted(times, t + tol_ns, "right")
        free = [j for j in range(lo, hi) if not used[j]]
        if not free:
            continue
        j = min(free, key=lambda x: (abs(times[x] - t), x))
        used[j] = True
        rows.append({"a_time": ea["time"], "b_time": b.loc[idx[j], "time"], **{k: ea[k] for k in key},
                     "a_index": ia, "b_index": idx[j]})
    return pd.DataFrame(rows, columns=["a_time", "b_time", *key, "a_index", "b_index"])


def membership(a: pd.DataFrame, b: pd.DataFrame, key: list[str], tol: pd.Timedelta, window: tuple) -> dict:
    """Matched / FOREXCOM-only / Dukascopy-only counts inside the count window (a = FOREXCOM, b = Dukascopy)."""
    lo, hi = window
    inside = lambda t: (t >= lo) & (t < hi)
    m = match_events(a, b, key, tol)
    matched = int((inside(m["a_time"]) | inside(m["b_time"])).sum()) if len(m) else 0
    a_only = int(inside(a.drop(index=m["a_index"])["time"]).sum()) if len(a) else 0
    b_only = int(inside(b.drop(index=m["b_index"])["time"]).sum()) if len(b) else 0
    lag = (m["b_time"] - m["a_time"]).dt.total_seconds() if len(m) else pd.Series(dtype=float)
    return {"matched": matched, "forexcom_only": a_only, "dukascopy_only": b_only,
            **rate(matched, matched + a_only + b_only),
            "matched_time_difference_s": {"median": float(lag.median()) if len(lag) else None,
                                          "exact_share": float((lag == 0).mean()) if len(lag) else None},
            "_pairs": m}


# ------------------------------------------------------------------ per-feed structure context

class FeedContext:
    """Swings, roll-ups and ATRs of one feed, built with the frozen PC2 parameters (reference role; no signal engine)."""

    def __init__(self, bars_1m: pd.DataFrame, p: Cbr1hParams):
        self.s1m = bars_1m
        self.b5, self.b15, self.b1h = rollup(bars_1m, "5min"), rollup(bars_1m, "15min"), rollup(bars_1m, "1h")
        self.atr1m, self.atr1h = atr(bars_1m, p.atr_length), atr(self.b1h, p.atr_length)
        self.sw_ltf = zigzag(bars_1m, self.atr1m, p.k_ltf, M1)
        self.sw_mtf = zigzag(self.b5, atr(self.b5, p.atr_length), p.k_mtf, M5)
        self.t3 = [a for a in track_type3(bars_1m, self.sw_ltf, max_reversal=p.max_reversal_ltf, tick=p.tick,
                                          latest_pair_only=True) if a.end == "BREAK"]
        self.p = p


def swing_events(sw: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"kind": sw["kind"].astype(str).to_numpy(), "time": sw["time"].to_numpy(),
                         "price": sw["price"].to_numpy()}).assign(time=lambda d: pd.to_datetime(d["time"], utc=True))


def type3_events(ctx: FeedContext) -> pd.DataFrame:
    return pd.DataFrame({"direction": [a.direction for a in ctx.t3], "time": [a.end_time for a in ctx.t3]},
                        columns=["direction", "time"]).assign(time=lambda d: pd.to_datetime(d["time"], utc=True))


def hilo_events(bars_1m: pd.DataFrame, tick: float) -> pd.DataFrame:
    h = hilo(bars_1m, tick=tick)
    return pd.DataFrame({"direction": h["direction"].to_numpy(), "kind": h["kind"].to_numpy(),
                         "time": pd.to_datetime(h["time"], utc=True)})


def hour_extension(ctx: FeedContext, h0: pd.Timestamp, as_of: pd.Timestamp) -> oe_mod.Overextension | None:
    if h0 not in ctx.s1m.index:
        return None
    q0 = (as_of - pd.Timedelta(microseconds=1)).floor("15min")
    prev = ctx.b15.loc[q0 - M15] if (q0 - M15) in ctx.b15.index else None
    a1 = _atr_at(ctx.atr1m, M1, as_of)
    p = ctx.p
    return oe_mod.evaluate(ctx.s1m, h0, float(ctx.s1m.loc[h0, "open"]), as_of, atr_1m=a1 or 0.0,
                           activation_atr=p.activation_atr, pullback_frac=p.pullback_frac,
                           two_sided_frac=p.two_sided_frac,
                           prev_candle_high=None if prev is None else float(prev["high"]),
                           prev_candle_low=None if prev is None else float(prev["low"]), origin=p.oe_origin)


def hour_condition(ctx: FeedContext, h0: pd.Timestamp) -> cond_mod.Condition:
    p = ctx.p
    start = tradable_window_start(h0, int(p.window / M1)) if p.window_basis == "TRADABLE" else h0 - p.window
    return cond_mod.classify(ctx.sw_mtf, ctx.s1m, h0, p.window, min_legs=p.min_legs, range_min=p.range_min,
                             trend_max=p.trend_max, correction_cap=p.correction_cap, aggregate=p.aggregate,
                             window_start=start)


def hour_state(ctx: FeedContext, h0: pd.Timestamp, as_of: pd.Timestamp) -> dict:
    """CBR1H rules evaluable without the 5s trigger at `as_of` (same formulas as `cbr1h._evaluate_hour` /
    `_evaluate_candidate` for these rules). The previous-15m take uses Q's 1m bars closed by `as_of` (no FOREXCOM 5s)."""
    p = ctx.p
    cond = hour_condition(ctx, h0)
    oe = hour_extension(ctx, h0, as_of)
    out = {"condition": cond.condition, "cond_direction": cond.direction, "oe_dir": None if oe is None else oe.direction}
    if oe is None or oe.direction == "NONE":
        return {**out, "direction": None, "rules": {}, "member": False}
    d = "SELL" if oe.direction == "UP" else "BUY"
    r: dict[str, bool | None] = {
        "M1H-COND-01": cond.condition in (cond_mod.RANGE, cond_mod.TRENDING_RANGE),
        "M1H-COND-02": cond.condition not in (cond_mod.TREND, cond_mod.UNDEFINED),
        "M1H-COND-03": not (cond.condition == cond_mod.TRENDING_RANGE and cond.direction == "NONE"),
    }
    known = usable(ctx.sw_mtf, as_of)
    pos = cond.pos(oe.extreme)
    if cond.condition == cond_mod.RANGE:
        r["M1H-LOC-01"] = pos is not None and (pos >= p.range_extreme if d == "SELL" else pos <= 1 - p.range_extreme)
    elif cond.condition == cond_mod.TRENDING_RANGE and cond.direction != "NONE":
        if (d == "SELL") == (cond.direction == "UP"):
            last = known[known["kind"] == ("H" if d == "SELL" else "L")]
            r["M1H-LOC-02"] = bool(len(last)) and ((oe.extreme > last["price"].iloc[-1]) if d == "SELL"
                                                   else (oe.extreme < last["price"].iloc[-1]))
        else:
            lg = legs(known)
            lg = lg[lg["dir"] == (1 if cond.direction == "UP" else -1)]
            er_pro = _er(oe.extreme, lg.iloc[-1]) if len(lg) else None
            r["M1H-LOC-03"] = er_pro is not None and p.pro_er_min <= er_pro <= p.pro_er_max
    a1h = _atr_at(ctx.atr1h, H1, as_of)
    r["M1H-OE-01"] = oe.duration_min >= p.oe_min_minutes
    r["M1H-OE-02"] = oe.no_pullback
    r["M1H-OE-04a"] = not oe.two_sided
    r["M1H-OE-04b"] = a1h is not None and oe.size >= p.oe_min_size_atr * a1h
    q0 = (as_of - pd.Timedelta(microseconds=1)).floor("15min")
    prev = ctx.b15.loc[q0 - M15] if (q0 - M15) in ctx.b15.index else None
    inside = ctx.s1m[(ctx.s1m.index >= q0) & (ctx.s1m.index + M1 <= as_of)]
    if prev is None:
        r["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] = False
    else:
        broke = bool(len(inside)) and (float(inside["high"].max()) > float(prev["high"]) if d == "SELL"
                                       else float(inside["low"].min()) < float(prev["low"]))
        closed_in_dir = bool(prev["close"] < prev["open"]) if d == "SELL" else bool(prev["close"] > prev["open"])
        r["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] = broke or closed_in_dir
    r["M1H-6A-3-NEW-EXTREME-IN-Q"] = oe.extreme_time is not None and oe.extreme_time >= q0
    return {**out, "direction": d, "rules": r, "member": all(v is True for v in r.values() if v is not None),
            "atr1h_defined": a1h is not None}


# ------------------------------------------------------------------ recent feed comparison (§7.1)

def compare_recent(fx1m: pd.DataFrame, dk1m: pd.DataFrame, minutes: pd.DatetimeIndex, p: Cbr1hParams, *,
                   exports: dict[str, pd.DataFrame], band: dict, hour_minutes: list[int], count_margin: pd.Timedelta,
                   lag_range: int = 3, report_percentile: int = 99) -> dict:
    """All §7.1 measurements. `fx1m` / `dk1m` are already restricted to `minutes`."""
    fx1m, dk1m, minutes = ns(fx1m), ns(dk1m), pd.DatetimeIndex(minutes).tz_convert("UTC").as_unit("ns")
    exports = {k: ns(v) for k, v in exports.items()}
    out: dict = {}
    # --- alignment, offsets, feed band (D25-P4 via parity.calibrate, the pinned D19-11 implementation)
    cal = parity.calibrate(fx1m, dk1m, floor=band["floor_usd"], percentile=band["residual_percentile"],
                           round_to=band["round_up_to_usd"], feed_near_multiple=3, max_lag=lag_range)
    j = fx1m.join(dk1m, how="inner", lsuffix="_fx", rsuffix="_dk")
    diff = pd.DataFrame({f: j[f"{f}_fx"] - j[f"{f}_dk"] for f in OHLC})
    resid = (diff - cal["delta_median_offset"]).abs()
    pooled = pd.concat([resid[f] for f in ("high", "low", "close")])
    out["alignment"] = {
        "comparison_minutes": len(minutes), "forexcom_minutes": len(fx1m), "dukascopy_minutes": len(dk1m),
        "matched_minutes": len(j), "missing_forexcom": len(minutes.difference(fx1m.index)),
        "missing_dukascopy": len(minutes.difference(dk1m.index)),
        "lag_correlations": {str(k): round(v, 6) for k, v in cal["lag_correlations"].items()},
        "best_lag_minutes": cal["best_lag_minutes"], "zero_lag_confirmed": cal["zero_lag_confirmed"]}
    out["offsets"] = {
        "delta_median_close_offset": cal["delta_median_offset"],
        "per_field_median_offset": {f: float(diff[f].median()) for f in OHLC},
        "per_day_median_close_offset": {str(k.date()): float(v) for k, v in
                                        diff["close"].groupby(diff.index.floor("1D")).median().items()},
        "residual_quantiles_hlc_after_delta": {f"p{q}": float(np.percentile(pooled, q)) for q in (50, 75, 90, 95, 99)},
        "residual_max_hlc_after_delta": float(pooled.max()),
        "per_field_residual_p95_after_delta": {f: float(np.percentile(resid[f], 95)) for f in OHLC}}
    out["feed_band"] = {"tau_usd": cal["tau_price"], "p95_residual": cal["residual_p"],
                        f"p{report_percentile}_residual": float(np.percentile(pooled, report_percentile)),
                        "formula": "max(floor, p95 |FX − DK − δ| over high/low/close), rounded up", **band}
    tau = cal["tau_price"]

    # --- exports vs 1m roll-ups, bar direction
    fx5, fx15 = rollup(fx1m, "5min"), rollup(fx1m, "15min")
    dk5, dk15 = rollup(dk1m, "5min"), rollup(dk1m, "15min")
    full = {"1m": minutes, "5m": full_intervals(minutes, fx1m.index.intersection(dk1m.index), "5min"),
            "15m": full_intervals(minutes, fx1m.index.intersection(dk1m.index), "15min")}
    consistency = {}
    for tf, roll in (("5m", fx5), ("15m", fx15)):
        ex = exports[tf]
        common = roll.index.intersection(ex.index).intersection(full[tf])
        eq = (ex.loc[common, OHLC].round(6) == roll.loc[common, OHLC].round(6)).all(axis=1)
        consistency[tf] = {"bars": len(common), "identical": int(eq.sum())}
    out["export_vs_1m_rollup"] = consistency
    bars_dir = {}
    for tf, a, b in (("1m", fx1m, dk1m), ("5m", fx5, dk5), ("15m", fx15, dk15)):
        idx = a.index.intersection(b.index).intersection(full[tf])
        bars_dir[tf] = rate(int((direction(a.loc[idx]) == direction(b.loc[idx])).sum()), len(idx))
    out["bar_direction"] = bars_dir

    # --- structure contexts
    fxc, dkc = FeedContext(fx1m, p), FeedContext(dk1m, p)
    window = (minutes[0] + count_margin, minutes[-1] + M1 - count_margin)
    swings = {}
    for tier, tol in (("ltf_1m", M1), ("mtf_5m", M5)):
        a = swing_events(fxc.sw_ltf if tier == "ltf_1m" else fxc.sw_mtf)
        b = swing_events(dkc.sw_ltf if tier == "ltf_1m" else dkc.sw_mtf)
        mem = membership(a, b, ["kind"], tol, window)
        pairs = mem.pop("_pairs")
        if len(pairs):
            px = a.loc[pairs["a_index"], "price"].to_numpy() - b.loc[pairs["b_index"], "price"].to_numpy()
            mem["matched_price_difference_after_delta"] = {
                "median_abs": float(np.median(np.abs(px - cal["delta_median_offset"]))),
                "p95_abs": float(np.percentile(np.abs(px - cal["delta_median_offset"]), 95))}
        mem["counts_total"] = {"forexcom": int(((a["time"] >= window[0]) & (a["time"] < window[1])).sum()),
                               "dukascopy": int(((b["time"] >= window[0]) & (b["time"] < window[1])).sum())}
        swings[tier] = mem
    out["swings"] = swings

    # --- 15m previous-candle takes
    both15 = full["15m"]
    rows = []
    for q in both15:
        if q - M15 not in both15:
            continue
        rec = {"q": q}
        for side in ("high", "low"):
            m_fx = (fx15.loc[q, "high"] - fx15.loc[q - M15, "high"]) if side == "high" else (fx15.loc[q - M15, "low"] - fx15.loc[q, "low"])
            m_dk = (dk15.loc[q, "high"] - dk15.loc[q - M15, "high"]) if side == "high" else (dk15.loc[q - M15, "low"] - dk15.loc[q, "low"])
            rec[f"{side}_fx"], rec[f"{side}_dk"], rec[f"{side}_margin_dk"] = bool(m_fx > 0), bool(m_dk > 0), float(m_dk)
        rows.append(rec)
    tk = pd.DataFrame(rows)
    takes = {}
    if len(tk):
        agree = [(tk[f"{s}_fx"] == tk[f"{s}_dk"]) for s in ("high", "low")]
        dis = pd.concat([tk.loc[~agree[i], f"{s}_margin_dk"] for i, s in enumerate(("high", "low"))])
        takes = {"high": rate(int(agree[0].sum()), len(tk)), "low": rate(int(agree[1].sum()), len(tk)),
                 "pooled": rate(int(agree[0].sum() + agree[1].sum()), 2 * len(tk)),
                 "disagreements": len(dis), "disagreements_with_abs_dukascopy_margin_le_tau": int((dis.abs() <= tau).sum()),
                 "take_rate_dukascopy": float((tk["high_dk"].sum() + tk["low_dk"].sum()) / (2 * len(tk)))}
    out["takes_15m"] = takes

    # --- hourly: extension, condition, hour-level state
    hours = sorted({t.floor("1h") for t in minutes})
    present = fx1m.index.intersection(dk1m.index)
    ext_rows, cond_rows, state_rows, excluded = [], [], [], []
    for h0 in hours:
        hm = minutes[(minutes >= h0) & (minutes < h0 + H1)]
        reason = None
        if len(hm.difference(present)) or h0 not in present:
            reason = "minutes_missing_on_a_feed"
        elif tradable_window_start(h0, int(p.window / M1)) < minutes[0]:
            reason = "condition_window_before_study_start"
        if reason:
            excluded.append({"hour": h0, "reason": reason})
            continue
        cf, cd = hour_condition(fxc, h0), hour_condition(dkc, h0)
        cond_rows.append({"hour": h0, "fx": cf.condition, "dk": cd.condition, "fx_dir": cf.direction, "dk_dir": cd.direction})
        for mm in hour_minutes:
            as_of = h0 + pd.Timedelta(minutes=mm)
            ef, ed = hour_extension(fxc, h0, as_of), hour_extension(dkc, h0, as_of)
            ext_rows.append({"hour": h0, "minute": mm, "fx_dir": ef.direction, "dk_dir": ed.direction,
                             "fx_time": ef.extreme_time, "dk_time": ed.extreme_time,
                             "fx_dur20": ef.duration_min >= p.oe_min_minutes, "dk_dur20": ed.duration_min >= p.oe_min_minutes,
                             "fx_nopb": ef.no_pullback, "dk_nopb": ed.no_pullback, "fx_two": ef.two_sided, "dk_two": ed.two_sided})
            sf, sd = hour_state(fxc, h0, as_of), hour_state(dkc, h0, as_of)
            if not (sf.get("atr1h_defined") and sd.get("atr1h_defined")):
                state_rows.append({"hour": h0, "minute": mm, "excluded": "atr1h_undefined"})
                continue
            state_rows.append({"hour": h0, "minute": mm, "fx_member": sf["member"], "dk_member": sd["member"],
                               "fx_rules": sf["rules"], "dk_rules": sd["rules"], "fx_dir": sf["direction"],
                               "dk_dir": sd["direction"]})
    ex = pd.DataFrame(ext_rows)
    ext = {}
    if len(ex):
        same_dir = ex["fx_dir"] == ex["dk_dir"]
        t_ok = same_dir & ((ex["fx_time"] - ex["dk_time"]).abs() <= M1)
        ext = {"direction": rate(int(same_dir.sum()), len(ex)),
               "extreme_time_within_1m_given_same_direction": rate(int(t_ok.sum()), int(same_dir.sum())),
               "duration_ge_min": rate(int((ex["fx_dur20"] == ex["dk_dur20"]).sum()), len(ex)),
               "no_pullback": rate(int((ex["fx_nopb"] == ex["dk_nopb"]).sum()), len(ex)),
               "two_sided": rate(int((ex["fx_two"] == ex["dk_two"]).sum()), len(ex)),
               "evaluations": len(ex), "hours": int(ex["hour"].nunique())}
    out["hour_extension"] = ext
    cd = pd.DataFrame(cond_rows)
    out["condition_at_hour_open"] = {} if not len(cd) else {
        "condition": rate(int((cd["fx"] == cd["dk"]).sum()), len(cd)),
        "cond_direction": rate(int((cd["fx_dir"] == cd["dk_dir"]).sum()), len(cd)),
        "dukascopy_counts": cd["dk"].value_counts().to_dict(), "forexcom_counts": cd["fx"].value_counts().to_dict()}
    st = [r for r in state_rows if "excluded" not in r]
    per_rule = {}
    for rule in HOUR_RULES:
        pairs = [(r["fx_rules"].get(rule), r["dk_rules"].get(rule)) for r in st
                 if r["fx_dir"] == r["dk_dir"] and (r["fx_rules"].get(rule) is not None or r["dk_rules"].get(rule) is not None)]
        per_rule[rule] = rate(sum(a == b for a, b in pairs), len(pairs))
    out["hour_level_state"] = {
        "membership": rate(sum(r["fx_member"] == r["dk_member"] for r in st), len(st)),
        "full_rule_vector_given_same_direction": rate(
            sum(r["fx_rules"] == r["dk_rules"] for r in st if r["fx_dir"] == r["dk_dir"]),
            sum(r["fx_dir"] == r["dk_dir"] for r in st)),
        "per_rule_given_same_direction": per_rule,
        "members_forexcom": sum(bool(r["fx_member"]) for r in st), "members_dukascopy": sum(bool(r["dk_member"]) for r in st),
        "evaluations": len(st), "excluded_atr1h_undefined": len(state_rows) - len(st)}
    out["hours_excluded"] = {"count": len(excluded),
                             "by_reason": pd.Series([e["reason"] for e in excluded]).value_counts().to_dict() if excluded else {}}

    # --- 1m type 3 and HILO
    t3 = membership(type3_events(fxc), type3_events(dkc), ["direction"], M1, window)
    t3.pop("_pairs")
    out["type3_1m"] = t3
    hl = membership(hilo_events(fx1m, p.tick), hilo_events(dk1m, p.tick), ["direction", "kind"], M1, window)
    hl.pop("_pairs")
    out["hilo_1m"] = hl
    out["five_second"] = "DATA_LIMITATION: no FOREXCOM 5s data"
    return out


def criterion_9(study: dict, concepts: list[str], fail_below: float, concern_below: float) -> dict:
    """D25 O-1 reading of criterion 9 (frozen before the study ran)."""
    pick = {"ltf_swing_membership": study["swings"]["ltf_1m"], "mtf_swing_membership": study["swings"]["mtf_5m"],
            "takes_15m": study["takes_15m"].get("pooled", rate(0, 0)),
            "hour_extension_direction": study["hour_extension"].get("direction", rate(0, 0)),
            "condition_at_hour_open": study["condition_at_hour_open"].get("condition", rate(0, 0)),
            "type3_1m": study["type3_1m"], "hour_level_membership": study["hour_level_state"]["membership"]}
    rows = {c: {k: pick[c][k] for k in ("agree", "n", "rate", "wilson95")} for c in concepts}
    fail = [c for c, r in rows.items() if r["rate"] is None or r["rate"] < fail_below]
    concern = [c for c, r in rows.items() if c not in fail and r["rate"] < concern_below]
    status = "FAIL_EVIDENCE" if fail else "CONCERN" if concern else "MET"
    return {"status": status, "concepts": rows, "fail_evidence": fail, "concerns": concern,
            "fail_evidence_if_rate_below": fail_below, "concern_if_rate_below": concern_below}


# ------------------------------------------------------------------ higher-timeframe fidelity (§7.2)

def export_intervals(ex: pd.DataFrame, nominal: pd.Timedelta) -> pd.Series:
    """Interval end per export bar: the next bar's time, capped at the nominal length."""
    nxt = pd.Series(ex.index[1:].append(pd.DatetimeIndex([ex.index[-1] + nominal])), index=ex.index)
    return nxt.where(nxt - ex.index.to_series() <= nominal, ex.index.to_series() + nominal)


def interval_bar(dk1m: pd.DataFrame, a: pd.Timestamp, b: pd.Timestamp) -> dict:
    """Dukascopy STRUCTURE roll-up of [a, b) with coverage of scheduled-open minutes and extreme minutes."""
    mins = pd.date_range(a, b, freq="1min", inclusive="left")
    sched = mins[~expected_closed_mask(mins)]
    w = dk1m[(dk1m.index >= a) & (dk1m.index < b)]
    cov = len(sched.intersection(w.index)) / len(sched) if len(sched) else None
    if not len(w) or cov != 1.0:
        return {"coverage": cov}
    return {"coverage": cov, "open": float(w["open"].iloc[0]), "high": float(w["high"].max()),
            "low": float(w["low"].min()), "close": float(w["close"].iloc[-1]),
            "high_time": w["high"].idxmax(), "low_time": w["low"].idxmin()}


def side_extended(o: float, h: float, lo: float) -> str:
    return "UP" if (h - o) >= (o - lo) else "DOWN"


def compare_bar(fx: pd.Series, dk: dict) -> dict:
    if "open" not in dk:
        return {"class": "DATA_LIMITATION", "coverage": dk["coverage"]}
    off = {f: round(float(fx[f]) - dk[f], 6) for f in OHLC}
    return {"offsets": off, "direction_fx": int(np.sign(fx["close"] - fx["open"])),
            "direction_dk": int(np.sign(dk["close"] - dk["open"])),
            "direction_agree": bool(np.sign(fx["close"] - fx["open"]) == np.sign(dk["close"] - dk["open"])),
            "side_extended_fx": side_extended(fx["open"], fx["high"], fx["low"]),
            "side_extended_dk": side_extended(dk["open"], dk["high"], dk["low"]),
            "side_extended_agree": side_extended(fx["open"], fx["high"], fx["low"]) == side_extended(dk["open"], dk["high"], dk["low"]),
            "dk_high_time": str(dk["high_time"]), "dk_low_time": str(dk["low_time"]), "coverage": 1.0}


def htf_example(hour: pd.Timestamp, dk1m: pd.DataFrame, fx: dict[str, pd.DataFrame], pm_hours: int,
                pm_4h: int) -> dict:
    """FOREXCOM 1h / 4h / 1D vs Dukascopy roll-ups around one course hour."""
    out: dict = {"hour_utc": str(hour)}
    h1 = fx["1h"]
    rows = []
    for t in pd.date_range(hour - pm_hours * H1, hour + pm_hours * H1, freq="1h"):
        if t not in h1.index:
            rows.append({"bar": str(t), "class": "NO_FOREXCOM_BAR"})
            continue
        rows.append({"bar": str(t), **compare_bar(h1.loc[t], interval_bar(dk1m, t, t + H1)),
                     "extreme_position_fx": "DATA_LIMITATION (1h OHLC has no intrabar order)"})
    out["1h"] = rows
    hb = h1.loc[hour] if hour in h1.index else None
    dh = interval_bar(dk1m, hour, hour + H1)
    out["delta_h"] = (None if hb is None or "open" not in dh else
                      round(((hb["open"] - dh["open"]) + (hb["close"] - dh["close"])) / 2, 6))
    for tf, nominal in (("4h", pd.Timedelta(hours=4)), ("1D", pd.Timedelta(days=1))):
        ex = fx[tf]
        ends = export_intervals(ex, nominal)
        if tf == "4h":
            idx = [t for t in ex.index if t < hour + pm_4h * H1 and ends[t] > hour - pm_4h * H1]
        else:
            cont = [t for t in ex.index if t <= hour < ends[t]]
            idx = []
            if cont:
                pos = ex.index.get_loc(cont[0])
                idx = [ex.index[pos - 1], cont[0]] if pos > 0 else [cont[0]]
        bars = []
        for t in idx:
            dk = interval_bar(dk1m, t, ends[t])
            rec = {"bar": str(t), "end": str(ends[t]), **compare_bar(ex.loc[t], dk)}
            if tf == "4h" and "open" in dk:                                   # which 1h bar holds each extreme
                inner = h1[(h1.index >= t) & (h1.index < ends[t])]
                mins = pd.date_range(t, ends[t], freq="1min", inclusive="left")
                open_hours = pd.DatetimeIndex(mins[~expected_closed_mask(mins)].floor("1h").unique())
                if len(inner) and open_hours.isin(inner.index).all():
                    rec["fx_high_hour"], rec["fx_low_hour"] = str(inner["high"].idxmax()), str(inner["low"].idxmin())
                    rec["dk_high_hour"], rec["dk_low_hour"] = str(dk["high_time"].floor("1h")), str(dk["low_time"].floor("1h"))
                    rec["extreme_hours_agree"] = (rec["fx_high_hour"] == rec["dk_high_hour"]
                                                  and rec["fx_low_hour"] == rec["dk_low_hour"])
                else:
                    rec["extreme_hours_agree"] = "DATA_LIMITATION"
            rec["contains_course_hour"] = bool(t <= hour < ends[t])
            bars.append(rec)
        out[tf] = bars
    return out


def dxy_example(hour: pd.Timestamp, tvc_1h: pd.DataFrame, cfd_1m: pd.DataFrame | None, pm_hours: int) -> list[dict]:
    """TVC:DXY 1h vs the Dukascopy DXY CFD (open/close only; index vs CFD, descriptive)."""
    rows = []
    for t in pd.date_range(hour - pm_hours * H1, hour + pm_hours * H1, freq="1h"):
        rec = {"bar": str(t)}
        if t not in tvc_1h.index:
            rec["class"] = "NO_TVC_BAR"
            rows.append(rec)
            continue
        tv = tvc_1h.loc[t]
        rec["tvc_direction"] = int(np.sign(tv["close"] - tv["open"]))
        w = None if cfd_1m is None else cfd_1m[(cfd_1m.index >= t) & (cfd_1m.index < t + H1)]
        if w is None or not len(w):
            rec["class"] = "DATA_LIMITATION"
        else:
            rec.update({"open_offset": round(float(tv["open"]) - float(w["open"].iloc[0]), 6),
                        "close_offset": round(float(tv["close"]) - float(w["close"].iloc[-1]), 6),
                        "cfd_direction": int(np.sign(float(w["close"].iloc[-1]) - float(w["open"].iloc[0]))),
                        "cfd_minutes": len(w)})
            rec["direction_agree"] = rec["tvc_direction"] == rec["cfd_direction"]
        rows.append(rec)
    return rows
