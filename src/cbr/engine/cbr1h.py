"""CBR1H_BASELINE_V1 reference engine (docs/strategy/1h-cbr-machine-spec.md, CBR_PRIMITIVES_V1 rev 1.2).

Signal logic only, on STRUCTURE bars (tick-derived mid, D16); never reads bid/ask. Fills, spread, the one-position rule
and one-fill-per-hour belong to the Phase 14A execution layer.

For every hourly candle H the engine evaluates every candidate entry-trigger arm in the direction opposite H's
overextension:
  HVCS_HILO  (variants A, A-AOI): a HILO armed on B1m, or on B5m when the HVCS is low-volume (§6A)
  FRACTAL_1M (variants B, B-AOI): after a completed LTF type 3, a ≥ 50% pullback of the impulse, then a HILO armed
                                  inside the pullback (§6B)
A HILO "arms" when its stop order becomes placeable (primitives §4.2):
  prior variant: at the close of bar j−1 when (j−1) broke (j−2)'s opposite extreme; order at (j−1)'s extreme ± tick,
                 valid during bar j
  same variant:  inside bar j, at the first 5s close after j took out (j−1)'s opposite extreme while its entry side
                 is still unbroken; valid until j closes
Every rule is evaluated on data closed at the arm time; later events (trigger touch, cancellation) are lifecycle.

M1H-COND-04 counts raw setups (every rule except COND-04) resolved TARGET before STOP on STRUCTURE 5s bars before the
decision (spec §2; resolution basis flagged with OQ-36). `hourly_state` exposes causal state for CBR15 M15-HTF-01.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import pandas as pd

from cbr.data.price_series import require_structure, rollup_structure
from cbr.data.sessions import expected_closed_mask
from cbr.engine.common import M1, M15, S5, _anchor_path, _atr_at, _er, _minutes_complete, anchor_at
from cbr.engine.params import Cbr1hParams, load_cbr1h, spec_hash
from cbr.structure import condition as cond_mod
from cbr.structure import overextension as oe_mod
from cbr.structure.indicators import atr
from cbr.structure.levels import aoi_tap, candle_close_levels, in_rollover, in_sydney_session
from cbr.structure.shifts import hvcs, track_type3
from cbr.structure.swings import legs, usable, zigzag

H1, M5 = pd.Timedelta(hours=1), pd.Timedelta(minutes=5)
TREND_DIRECTION_UNRESOLVED = "TREND_DIRECTION_UNRESOLVED"
STOP_ANCHOR_SOURCE = "STRUCTURE_TICK_MID_5S_EXTENSION_EXTREME"
BLOCKER_PRIOR = "PRIOR_SETUP_RESOLUTION_BASIS (OQ-36 scope)"
BLOCKER_ENTRY = "ENTRY_TRIGGER_VS_COURSE_EXAMPLES (OQ-39)"
DECISION_FIELDS = ["signal_id", "hour_open_utc", "timestamp", "direction", "entry_model", "hilo_tier", "hilo_kind",
                   "event", "rules_failed", "entry_trigger_time", "entry_reference_price", "valid_until",
                   "ext_extreme_at_decision", "condition", "c_med", "n_legs", "cond_direction", "oe_duration_min",
                   "oe_size", "hvcs_minutes", "prior_played_out"]


@dataclass(frozen=True)
class Cbr1hResult:
    candidates: pd.DataFrame
    hours: pd.DataFrame
    signals: list[dict]
    spec_hash: str
    variant: str


# ------------------------------------------------------------------ HILO arms (STRUCTURE bars)

def hilo_arms(bars: pd.DataFrame, s5s: pd.DataFrame, tf: pd.Timedelta, side: str, start: pd.Timestamp,
              end: pd.Timestamp, tick: float) -> list[dict]:
    """Stop-order arms of a HILO in `side` (BUY/SELL) for bars j opening in [start, end) on timeframe `tf`."""
    idx = bars.index
    pos = {t: i for i, t in enumerate(idx)}
    out = []
    for tj in pd.date_range(start.ceil(tf), end, freq=tf, inclusive="left"):
        i1, i2 = pos.get(tj - tf), pos.get(tj - 2 * tf)
        if i1 is None or i2 is None:
            continue                                       # missing constituent bar: not armable (NT_INCOMPLETE)
        h1, l1 = float(bars["high"].iat[i1]), float(bars["low"].iat[i1])
        h2, l2 = float(bars["high"].iat[i2]), float(bars["low"].iat[i2])
        buy = side == "BUY"
        trigger = h1 + tick if buy else l1 - tick
        prior = (l1 < l2) if buy else (h1 > h2)
        valid_until = tj + tf
        if prior:
            out.append({"arm_time": tj, "trigger": trigger, "valid_until": valid_until, "kind": "prior",
                        "bar_open": tj, "stop_ref": l1 if buy else h1})
            continue
        inside = s5s[(s5s.index >= tj) & (s5s.index < valid_until)]
        if not len(inside):
            continue
        opp = inside["low"].cummin() if buy else inside["high"].cummax()
        ent = inside["high"].cummax() if buy else inside["low"].cummin()
        took = (opp < l1) if buy else (opp > h1)
        entry_broken = (ent > h1) if buy else (ent < l1)
        ok = took & ~entry_broken
        if ok.any():
            t = ok.idxmax()
            out.append({"arm_time": t + S5, "trigger": trigger, "valid_until": valid_until, "kind": "same",
                        "bar_open": tj, "stop_ref": float(opp.loc[t])})
    return out


def _touch(s5s: pd.DataFrame, side: str, trigger: float, start: pd.Timestamp, end: pd.Timestamp):
    w = s5s[(s5s.index >= start) & (s5s.index < end)]
    hit = w.index[(w["high"] >= trigger) if side == "BUY" else (w["low"] <= trigger)]
    return hit[0] if len(hit) else None


# ------------------------------------------------------------------ engine

def run_cbr1h(s1m: pd.DataFrame, s5s: pd.DataFrame, *, start: pd.Timestamp, end: pd.Timestamp, variant: str = "A",
              params: Cbr1hParams | None = None) -> Cbr1hResult:
    """Evaluate hourly candles opening in [start, end). Earlier bars are warm-up (ATR, swings, prior setups)."""
    require_structure(s1m)
    require_structure(s5s)
    p = params or load_cbr1h(variant)
    ctx = _Context(s1m, s5s, p)
    hours = pd.date_range(max((start - p.prior_lookback).floor("1h"), s1m.index[0].ceil("1h")), end, freq="1h",
                          inclusive="left")
    hour_rows, cand_rows = [], []
    for h0 in hours:
        mins = pd.date_range(h0, h0 + H1, freq="1min", inclusive="left")
        if expected_closed_mask(mins).all():
            continue
        hrow, cands = _evaluate_hour(h0, ctx, p)
        hour_rows.append(hrow)
        cand_rows += cands
    cand = pd.DataFrame(cand_rows)
    if len(cand):
        _resolve_raw(cand, ctx, p)
        _apply_prior(cand, p)
        cand = cand[cand["hour_open_utc"] >= start].reset_index(drop=True)
    hours_df = pd.DataFrame(hour_rows)
    if len(hours_df):
        hours_df = hours_df[hours_df["hour_open_utc"] >= start].reset_index(drop=True)
    shash = spec_hash()
    signals = [_signal(r, p, shash) for _, r in cand.iterrows() if r["event"] == "ARMED"] if len(cand) else []
    if len(cand):
        cand["spec_hash"] = shash
    return Cbr1hResult(cand, hours_df, signals, shash, p.variant)


class _Context:
    def __init__(self, s1m, s5s, p: Cbr1hParams):
        self.s1m, self.s5s = s1m, s5s
        self.b5 = rollup_structure(s1m, "5min")
        self.b15 = rollup_structure(s1m, "15min")
        self.b1h = rollup_structure(s1m, "1h")
        self.atr1m = atr(s1m, p.atr_length)
        self.atr1h = atr(self.b1h, p.atr_length)
        self.sw_mtf = zigzag(self.b5, atr(self.b5, p.atr_length), p.k_mtf, M5)
        self.sw_ltf = zigzag(s1m, self.atr1m, p.k_ltf, M1)
        self.t3_ltf = track_type3(s1m, self.sw_ltf, max_reversal=p.max_reversal_ltf, tick=p.tick, latest_pair_only=True)
        self.levels = pd.concat([candle_close_levels(rollup_structure(s1m, f), pd.Timedelta(f)) for f in ("30min", "1h")],
                                ignore_index=True) if p.aoi_required else None


def _oe(ctx: _Context, h0, h_open, as_of, p: Cbr1hParams):
    q0 = (as_of - pd.Timedelta(microseconds=1)).floor("15min")
    prev = ctx.b15.loc[q0 - M15] if (q0 - M15) in ctx.b15.index else None
    a1 = _atr_at(ctx.atr1m, M1, as_of)
    oe = oe_mod.evaluate(ctx.s1m, h0, h_open, as_of, atr_1m=a1 or 0.0, activation_atr=p.activation_atr,
                         pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac,
                         prev_candle_high=None if prev is None else float(prev["high"]),
                         prev_candle_low=None if prev is None else float(prev["low"]))
    return oe, a1, q0


def _evaluate_hour(h0, ctx: _Context, p: Cbr1hParams):
    h_end = h0 + H1
    h_open = float(ctx.s1m.loc[h0, "open"]) if h0 in ctx.s1m.index else None
    cond = cond_mod.classify(ctx.sw_mtf, ctx.s1m, h0, p.window, min_legs=p.min_legs, range_min=p.range_min,
                             trend_max=p.trend_max, correction_cap=p.correction_cap, aggregate=p.aggregate)
    hour_rules = {
        "M1H-COND-01": cond.condition in (cond_mod.RANGE, cond_mod.TRENDING_RANGE),
        "M1H-COND-02": cond.condition not in (cond_mod.TREND, cond_mod.UNDEFINED),
        "M1H-COND-03": not (cond.condition == cond_mod.TRENDING_RANGE and cond.direction == "NONE"),
        "NT_INCOMPLETE_H_OPEN": h_open is not None,
    }
    hrow = {"hour_open_utc": h0, "h_open": h_open, "condition": cond.condition, "c_med": cond.c_med,
            "n_legs": cond.n_legs, "cond_direction": cond.direction, "range_high": cond.range_high,
            "range_low": cond.range_low, "rules_failed": [k for k, v in hour_rules.items() if not v],
            "context_reason": None if hour_rules["M1H-COND-03"] else TREND_DIRECTION_UNRESOLVED, "candidates": 0}
    if h_open is None:
        return hrow, []
    window_start, window_end = h0 + pd.Timedelta(minutes=p.start_min), h0 + pd.Timedelta(minutes=p.end_min)
    arms = []
    for side in ("BUY", "SELL"):
        if p.entry_model == "HVCS_HILO":
            for tier, bars, tf in (("1m", ctx.s1m, M1), ("5m", ctx.b5, M5)):
                for a in hilo_arms(bars, ctx.s5s, tf, side, h0, min(h_end, window_end), p.tick):
                    arms.append({**a, "side": side, "tier": tier, "fractal": None})
        else:
            arms += _fractal_arms(ctx, h0, h_end, window_end, side, p)
    rows = []
    for a in sorted(arms, key=lambda x: (x["arm_time"], x["side"], x["tier"])):
        as_of = a["arm_time"]
        if as_of >= min(h_end, window_end):
            continue
        oe, a1, q0 = _oe(ctx, h0, h_open, as_of, p)
        if oe.direction == "NONE":
            continue
        d = "SELL" if oe.direction == "UP" else "BUY"
        if a["side"] != d:
            continue                                     # a trigger in the extension's own direction isn't a candidate
        hrow["candidates"] += 1
        rows.append(_evaluate_candidate(h0, h_open, cond, hour_rules, oe, a1, q0, a, as_of, d, window_start,
                                        window_end, ctx, p))
    return hrow, rows


def _fractal_arms(ctx: _Context, h0, h_end, window_end, side, p: Cbr1hParams) -> list[dict]:
    """§6B: completed LTF type 3 inside H → impulse → ≥ 50% pullback (not beyond the sweep extreme) → HILO arms."""
    out = []
    t3_side = side                                        # a SELL entry follows a bearish (SELL) type 3
    for t3 in ctx.t3_ltf:
        if t3.direction != t3_side or t3.end != "BREAK" or not (h0 <= t3.end_time < h_end):
            continue
        broke_at = t3.end_time + M1                        # the break bar's close
        sweep = t3.extreme_before_end
        after = ctx.s1m[(ctx.s1m.index >= t3.end_time) & (ctx.s1m.index < min(h_end, window_end))]
        impulse = None
        reached_at = None
        for t, row in after.iterrows():
            if side == "SELL":
                impulse = row["low"] if impulse is None else min(impulse, row["low"])
                if row["high"] > sweep:
                    break                                    # pullback beyond the sweep extreme: pattern invalid
                if t > t3.end_time and reached_at is None and row["high"] >= impulse + p.fractal_pullback_min * (sweep - impulse):
                    reached_at = t + M1
            else:
                impulse = row["high"] if impulse is None else max(impulse, row["high"])
                if row["low"] < sweep:
                    break
                if t > t3.end_time and reached_at is None and row["low"] <= impulse - p.fractal_pullback_min * (impulse - sweep):
                    reached_at = t + M1
            if reached_at is not None:
                invalid_at = None
                tail = after[after.index >= reached_at]
                beyond = tail.index[(tail["high"] > sweep) if side == "SELL" else (tail["low"] < sweep)]
                if len(beyond):
                    invalid_at = beyond[0]
                stop = min(h_end, window_end) if invalid_at is None else invalid_at
                for a in hilo_arms(ctx.s1m, ctx.s5s, M1, side, reached_at, stop, p.tick):
                    if a["arm_time"] >= reached_at:
                        out.append({**a, "side": side, "tier": "1m",
                                    "fractal": {"t3_sweep_time": t3.sweep_time, "t3_break_time": t3.end_time,
                                                "t3_break_close": broke_at, "sweep_extreme": sweep,
                                                "pullback_reached_at": reached_at, "pattern_invalid_at": invalid_at}})
                break
    return out


def _evaluate_candidate(h0, h_open, cond, hour_rules, oe, a1, q0, arm, as_of, d, window_start, window_end,
                        ctx: _Context, p: Cbr1hParams) -> dict:
    rules: dict[str, bool | None] = dict(hour_rules)
    rules["M1H-COND-04"] = None                                   # resolved after raw setups
    known = usable(ctx.sw_mtf, as_of)
    pos = cond.pos(oe.extreme)
    er_pro = beyond = None
    if cond.condition == cond_mod.RANGE:
        rules["M1H-LOC-01"] = pos is not None and (pos >= p.range_extreme if d == "SELL" else pos <= 1 - p.range_extreme)
    elif cond.condition == cond_mod.TRENDING_RANGE and cond.direction != "NONE":
        if (d == "SELL") == (cond.direction == "UP"):
            kind = "H" if d == "SELL" else "L"
            last = known[known["kind"] == kind]
            beyond = bool(len(last)) and ((oe.extreme > last["price"].iloc[-1]) if d == "SELL"
                                          else (oe.extreme < last["price"].iloc[-1]))
            rules["M1H-LOC-02"] = beyond
        else:
            lg = legs(known)
            lg = lg[lg["dir"] == (1 if cond.direction == "UP" else -1)]
            er_pro = _er(oe.extreme, lg.iloc[-1]) if len(lg) else None
            rules["M1H-LOC-03"] = er_pro is not None and p.pro_er_min <= er_pro <= p.pro_er_max
    if p.aoi_required:
        rules["M1H-LOC-04"] = aoi_tap(ctx.levels, oe.extreme, h0, zone=p.aoi_zone_atr * (a1 or 0.0),
                                      lookback=p.aoi_lookback)
    a1h = _atr_at(ctx.atr1h, H1, as_of)
    rules["M1H-OE-01"] = oe.duration_min >= p.oe_min_minutes
    rules["M1H-OE-02"] = oe.no_pullback
    rules["M1H-OE-04a"] = not oe.two_sided
    rules["M1H-OE-04b"] = a1h is not None and oe.size >= p.oe_min_size_atr * a1h

    hv_best = None
    if a1:
        closed = ctx.s1m[ctx.s1m.index + M1 <= as_of]
        for e in closed.index[closed.index >= h0]:
            hv = hvcs(closed, e, oe.direction, atr_1m=a1, min_minutes=p.hvcs_min_minutes,
                      max_violations=p.hvcs_max_violations, lvcs_body_atr=p.hvcs_lvcs_body_atr)
            if hv_best is None or hv.minutes > hv_best.minutes:
                hv_best = hv
    if p.entry_model == "HVCS_HILO":
        rules["M1H-6A-1-HVCS"] = bool(hv_best and hv_best.valid)
        rules["M1H-6A-2-PREV-BREAK"] = bool(oe.prev_candle_break)
        rules["M1H-6A-3-NEW-EXTREME-IN-Q"] = oe.extreme_time is not None and oe.extreme_time >= q0
        want_tier = "5m" if (hv_best and hv_best.low_volume) else "1m"
        rules["M1H-6A-4-HILO-TIER"] = arm["tier"] == want_tier
    else:
        fr = arm["fractal"]
        rules["M1H-6B-1-T3-AFTER-OE"] = fr["t3_break_time"] >= oe.extreme_time
        rules["M1H-6B-3-PULLBACK"] = fr["pullback_reached_at"] <= as_of and (fr["pattern_invalid_at"] is None
                                                                             or fr["pattern_invalid_at"] >= as_of)

    active_from = max(as_of, window_start)
    active_until = min(arm["valid_until"], window_end)
    rules["M1H-TIME-01"] = active_from < active_until
    # M1H-TIME-02 (q30 veto), evaluated for orders whose fill window lies in the :30 15m candle, on data before as_of
    q30_evaluated = False
    if h0 + pd.Timedelta(minutes=30) <= active_from < h0 + pd.Timedelta(minutes=45):
        q30_evaluated = True
        c30 = ctx.s1m[(ctx.s1m.index >= h0 + pd.Timedelta(minutes=30)) & (ctx.s1m.index + M1 <= as_of)]
        o30 = float(c30["open"].iloc[0]) if len(c30) else None
        push = None if o30 is None else ((c30["high"].max() - o30) if oe.direction == "UP" else (o30 - c30["low"].min()))
        pushed = push is not None and a1 is not None and push >= p.q30_push_atr * a1
        c15 = ctx.b15.loc[h0 + M15] if (h0 + M15) in ctx.b15.index else None
        exception = c15 is not None and ((c15["close"] < c15["open"]) if d == "SELL" else (c15["close"] > c15["open"]))
        rules["M1H-TIME-02"] = pushed or exception
    rules["NT_SYDNEY"] = not (in_sydney_session(active_from) or in_sydney_session(max(active_from, active_until - S5)))
    rules["NT_ROLLOVER"] = not any(in_rollover(t, pre_min=p.rollover_pre_min, post_min=p.rollover_post_min)
                                   for t in (active_from, max(active_from, active_until - S5)))
    complete, missing = _minutes_complete(ctx.s1m.index, h0, as_of.floor("1min"))
    rules["NT_INCOMPLETE_H"] = complete
    trigger = arm["trigger"]
    target_dec = oe.extreme - 0.5 * (oe.extreme - h_open)
    rules["IMPL-REWARD"] = (trigger > target_dec) if d == "SELL" else (trigger < target_dec)

    touch = _touch(ctx.s5s, d, trigger, active_from, active_until) if active_from < active_until else None
    cancel_time, cancel_reason = active_until, ("HILO_BAR_CLOSED" if arm["valid_until"] <= window_end else "WINDOW_END")
    if touch is not None:
        cancel_time = touch
    # OE re-evaluated at each 1m close before the touch (§4): failure cancels the order
    horizon = touch if touch is not None else cancel_time
    for t in pd.date_range(as_of.floor("1min") + M1, horizon, freq="1min", inclusive="both"):
        later, _, _ = _oe(ctx, h0, h_open, t, p)
        if later.direction != oe.direction or not later.no_pullback:
            if t < cancel_time:
                cancel_time, cancel_reason = t, "OE_PULLBACK"
                touch = None if (touch is not None and touch >= t) else touch
            break
    anchor, anchor_time, path = _anchor_path(ctx.s5s, h0, active_from, cancel_time if touch is None else touch + S5, d)
    buffer_price = p.buffer_atr * (a1 or 0.0)
    return {
        "hour_open_utc": h0, "timestamp": as_of, "direction": d, "variant": p.variant, "entry_model": p.entry_model,
        "hilo_tier": arm["tier"], "hilo_kind": arm["kind"], "rules": rules, "h_open": h_open,
        "condition": cond.condition, "c_med": cond.c_med, "n_legs": cond.n_legs, "cond_direction": cond.direction,
        "range_high": cond.range_high, "range_low": cond.range_low, "pos_oe_extreme": pos, "er_pro": er_pro,
        "beyond_external": beyond, "oe_dir": oe.direction, "ext_extreme_at_decision": oe.extreme,
        "oe_extreme_time": oe.extreme_time, "oe_size": oe.size, "oe_size_atr1h": (oe.size / a1h) if a1h else None,
        "oe_duration_min": oe.duration_min, "oe_no_pullback": oe.no_pullback, "oe_two_sided": oe.two_sided,
        "oe_opposite_wick": oe.opposite_wick, "oe_prev_candle_break": oe.prev_candle_break, "atr_1m": a1,
        "atr_1h": a1h, "hvcs_minutes": hv_best.minutes if hv_best else None,
        "hvcs_body_atr": hv_best.body_atr if hv_best else None, "lvcs": bool(hv_best and hv_best.low_volume),
        "entry_reference_price": trigger, "entry_trigger_time": active_from, "valid_until": active_until,
        "hilo_stop_ref": arm["stop_ref"], "q30_veto_evaluated": q30_evaluated,
        "fractal": arm["fractal"], "mih_decision": (as_of - h0) / M1,
        "candle_open_price": h_open, "structure_stop_anchor": anchor, "stop_anchor_time": anchor_time,
        "stop_anchor_source": STOP_ANCHOR_SOURCE, "stop_anchor_path": path, "stop_buffer_price": buffer_price,
        "target_at_decision": target_dec,
        "target_at_activation": None if anchor is None else anchor - 0.5 * (anchor - h_open),
        "structure_trigger_touch_time": touch, "cancel_time": cancel_time, "cancel_reason": cancel_reason,
        "h_missing_minutes": missing,
    }


def _resolve_raw(cand: pd.DataFrame, ctx: _Context, p: Cbr1hParams) -> None:
    outcome, resolved = [], []
    for _, r in cand.iterrows():
        raw = all(v is True for k, v in r["rules"].items() if k != "M1H-COND-04" and v is not None)
        if not raw:
            outcome.append(None)
            resolved.append(None)
            continue
        o, t = _raw_outcome(r, ctx.s5s, p)
        outcome.append(o)
        resolved.append(t)
    cand["raw_setup"] = [o is not None for o in outcome]
    cand["raw_outcome"] = outcome
    cand["raw_resolved_utc"] = pd.to_datetime(pd.Series(resolved, index=cand.index, dtype="object"), utc=True)


def _raw_outcome(r, s5s: pd.DataFrame, p: Cbr1hParams):
    """Spec §2: simulated with the same stop/target, TARGET before STOP; STRUCTURE 5s touches, stop first (OQ-36 scope).
    Stop anchor and target taken at the touch (D17-2; M1H-TP-01 'fixed at fill')."""
    touch = r["structure_trigger_touch_time"]
    if touch is None or pd.isna(touch):
        return "NO_TOUCH", r["cancel_time"]
    sell = r["direction"] == "SELL"
    anchor = anchor_at(r, touch + S5)
    if anchor is None:
        return "NO_ANCHOR", touch
    stop = anchor + (r["stop_buffer_price"] if sell else -r["stop_buffer_price"])
    target = anchor - 0.5 * (anchor - r["h_open"])
    for t, row in s5s[s5s.index >= touch].iterrows():
        if (row["high"] >= stop) if sell else (row["low"] <= stop):
            return "STOP", t + S5
        if (row["low"] <= target) if sell else (row["high"] >= target):
            return "TARGET", t + S5
        if in_rollover(t, pre_min=p.rollover_flat_before_min, post_min=0):
            return "FORCED_FLAT", t + S5
    return "UNRESOLVED", None


def _apply_prior(cand: pd.DataFrame, p: Cbr1hParams) -> None:
    raw = cand[cand["raw_setup"] & (cand["raw_outcome"] == "TARGET")]

    def count(as_of: pd.Timestamp) -> int:
        return int(((raw["timestamp"] >= as_of - p.prior_lookback) & (raw["timestamp"] < as_of)
                    & (raw["raw_resolved_utc"] <= as_of)).sum())

    prior, failed, events = [], [], []
    for _, r in cand.iterrows():
        n = count(r["timestamp"])
        prior.append(n)
        r["rules"]["M1H-COND-04"] = n >= p.prior_min_count
        bad = sorted(k for k, v in r["rules"].items() if v is False)
        failed.append(bad)
        events.append("ARMED" if not bad else "REJECTED")
    cand["prior_played_out"] = prior
    cand["rules_failed"] = failed
    cand["rules_not_evaluated"] = [sorted(k for k, v in rr.items() if v is None) for rr in cand["rules"]]
    cand["event"] = events
    cand["reject_reasons"] = [sorted({TREND_DIRECTION_UNRESOLVED if k == "M1H-COND-03" else k for k in f}) for f in failed]
    cand["eligibility_blockers"] = [[BLOCKER_PRIOR, BLOCKER_ENTRY]] * len(cand)
    cand["baseline_eligible"] = False
    seq = cand.groupby(["hour_open_utc", "direction"]).cumcount()
    cand["signal_id"] = [f"CBR1H_BASELINE_V1/{r['variant']}/{r['hour_open_utc']:%Y%m%dT%H%M}/{r['direction']}/{s}"
                         for (_, r), s in zip(cand.iterrows(), seq, strict=True)]


def _iso(t):
    return None if t is None or (not isinstance(t, pd.Timestamp) and pd.isna(t)) else pd.Timestamp(t).isoformat()


def _signal(r: pd.Series, p: Cbr1hParams, shash: str) -> dict:
    long = r["direction"] == "BUY"
    return {
        "signal_id": r["signal_id"], "model": p.model, "variant": p.variant, "price_role": "STRUCTURE",
        "timestamp": _iso(r["timestamp"]), "direction": "LONG" if long else "SHORT",
        "entry_trigger_time": _iso(r["entry_trigger_time"]), "entry_expiry_time": _iso(r["valid_until"]),
        "entry_order_type": "STOP", "entry_reference_price": r["entry_reference_price"],
        "stop_rule": {"extension_extreme": r["ext_extreme_at_decision"], "extension_extreme_source": "TICK_MID",
                      "candle_open_price": r["candle_open_price"],
                      "extension_extreme_at_decision": r["ext_extreme_at_decision"], "sweep_extreme": None,
                      "structure_stop_anchor": r["structure_stop_anchor"], "stop_anchor_time": _iso(r["stop_anchor_time"]),
                      "stop_anchor_source": r["stop_anchor_source"],
                      "stop_anchor_path": [[_iso(t), v] for t, v in r["stop_anchor_path"]],
                      "structure_extreme_at_fill": None, "final_execution_stop": None, "direction": "LONG" if long else "SHORT",
                      "buffer": {"param": "stop.buffer_atr", "value": p.buffer_atr, "unit": "ATR(1m,14)",
                                 "atr_at_decision": r["atr_1m"], "label": "ASSUMPTION", "source": ["OQ-11"]},
                      "spread_policy": "ADD_SPREAD_AT_FILL",
                      "execution_inputs": {"spread_at_decision": None, "spread_source": None}},
        "stop_price": None, "target_price": r["target_at_activation"],
        "extension_high": max(r["ext_extreme_at_decision"], r["h_open"]),
        "extension_low": min(r["ext_extreme_at_decision"], r["h_open"]), "extremes_source": "TICK_MID",
        "range_high": r["range_high"], "range_low": r["range_low"],
        "context_state": {"condition": r["condition"], "c_med": r["c_med"], "n_legs": r["n_legs"],
                          "cond_direction": r["cond_direction"], "pos_oe_extreme": r["pos_oe_extreme"],
                          "oe_duration_min": r["oe_duration_min"], "hvcs_minutes": r["hvcs_minutes"],
                          "prior_played_out": int(r["prior_played_out"]), "entry_model": r["entry_model"],
                          "hilo_tier": r["hilo_tier"], "hilo_kind": r["hilo_kind"]},
        "dxy_state": {"availability": "MISSING", "direction_15m": None, "direction_1h": None, "reason_codes": ["NOT_PROVIDED"]},
        "session_state": {"nt_sydney": False, "nt_rollover": False},
        "source_feed": {"feed_id": "dukascopy_ticks:xauusd", "manifest_hash": None},
        "data_confidence": {"level": "FULL", "reason_codes": []}, "reason_code": "ARMED", "spec_hash": shash,
        "eligibility": {"baseline_eligible": False, "blockers": list(r["eligibility_blockers"])},
        "lifecycle": {"cancel_time": _iso(r["cancel_time"]), "cancel_reason": r["cancel_reason"],
                      "structure_trigger_touch_time": _iso(r["structure_trigger_touch_time"])},
    }


# ------------------------------------------------------------------ hourly state for CBR15 (M15-HTF-01)

def hourly_state(result: Cbr1hResult, as_of: pd.Timestamp) -> list[dict]:
    """Causal view of the current hour's raw CBR1H setups at `as_of`: only candidates decided at or before `as_of`, and
    only lifecycle events that happened at or before it. `FILLED` needs the execution layer: a setup whose trigger was
    touched on STRUCTURE prices is reported as `TRIGGER_TOUCHED_FILL_UNKNOWN`."""
    c = result.candidates
    if not len(c):
        return []
    h0 = (as_of - pd.Timedelta(microseconds=1)).floor("1h")        # the hour containing as_of (a boundary belongs to the ending hour)
    sel = c[(c["hour_open_utc"] == h0) & (c["timestamp"] <= as_of) & c["raw_setup"]]
    out = []
    for _, r in sel.iterrows():
        touched = r["structure_trigger_touch_time"] is not None and not pd.isna(r["structure_trigger_touch_time"]) \
            and r["structure_trigger_touch_time"] <= as_of
        ended = r["cancel_time"] <= as_of
        state = ("TRIGGER_TOUCHED_FILL_UNKNOWN" if touched else "ENDED" if ended
                 else "ACTIVE" if r["entry_trigger_time"] <= as_of else "PENDING")
        out.append({"signal_id": r["signal_id"], "decision_time": r["timestamp"], "direction": r["direction"],
                    "state": state, "entry_model": r["entry_model"], "oe_dir": r["oe_dir"],
                    "oe_duration_min": r["oe_duration_min"], "mih_decision": r["mih_decision"],
                    "end_reason": r["cancel_reason"] if (ended or touched) else None,
                    "h_missing_minutes": r["h_missing_minutes"], "confidence": "FULL" if r["h_missing_minutes"] == 0 else "REDUCED"})
    return out


def htf_provider(result: Cbr1hResult):
    """M15-HTF-01 for CBR15: VETO if a raw CBR1H-A setup opposite to the 15m direction is ACTIVE/PENDING in the current
    hour at as_of; NOT_EVALUATED if one had its trigger touched (the FILLED part needs Phase 14A); else CLEAR."""
    if result.variant != "A":
        raise ValueError("M15-HTF-01 is defined on CBR1H_BASELINE_V1-A")

    def provider(as_of: pd.Timestamp, d15: str) -> str:
        opposite = "BUY" if d15 == "SELL" else "SELL"
        states = [s["state"] for s in hourly_state(result, as_of) if s["direction"] == opposite]
        if any(s in ("ACTIVE", "PENDING") for s in states):
            return "VETO"
        if "TRIGGER_TOUCHED_FILL_UNKNOWN" in states:
            return "NOT_EVALUATED"
        return "CLEAR"
    return provider


def decision_frame(result: Cbr1hResult) -> pd.DataFrame:
    c = result.candidates
    if not len(c):
        return pd.DataFrame(columns=DECISION_FIELDS)
    out = c[DECISION_FIELDS].copy()
    out["rules_failed"] = out["rules_failed"].map(lambda x: ",".join(x))
    return out


def result_hash(result: Cbr1hResult) -> str:
    payload = json.dumps({"candidates": decision_frame(result).astype(str).to_dict("records"),
                          "signals": result.signals}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
