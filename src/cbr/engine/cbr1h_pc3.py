"""CBR1H_BASELINE_V1-PC3 reference engine (owner ruling D29).

Additive module: PC2's `engine/cbr1h.py` is pinned by the frozen PC2 records and is **not** modified. Signal logic only,
on STRUCTURE bars (D16). Fills, spread and the one-position rule stay in Phase 14A.

Differences from PC2, each approved in D29 and listed in the PC3 spec record:
  * TYPE 3 (D29-1, CANON_CORRECTION): re-anchored trigger, reversal timer from the latest sweep extreme
    (`structure/shifts_pc3.py`). Both the 5s trigger and variant B's 1m parent use it.
  * EXTENSION (D29-5…9): PRE_EXTENSION / EXTENSION_ACTIVE with earliest activation at minute 7 and the Q1 qualifier;
    duration from activation; the 50% pullback measured against the whole active extension with no early latch
    (`structure/overextension_pc3.py`).
  * HVCS (D29-10, D29-11): structural conformity, indecision candles allowed, evaluated at the 5s shift decision time.
  * PRIOR SETUP (D29-12): `M1H-COND-04` is no longer a canonical rule; the diagnostics are kept.
  * CONDITION (D29-14): a directionless trending range is classified RANGE, so `M1H-COND-03` no longer blocks.
  * UNCHANGED (D29-15…17): hour-open reference for stop and target, tradable condition window, swing definition
    (ATR zig-zag, k = 3), candidate selection.

Causality: decision fields use only bars closed at the candidate's `timestamp` (the sweep bar's close); the HVCS rule
and the :30 diagnostic use only bars closed at the 5s shift. No field may use data after its own evaluation instant.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import pandas as pd

from cbr.data.price_series import require_structure, rollup_structure
from cbr.data.sessions import expected_closed_mask
from cbr.engine.common import (
    M1,
    M15,
    S5,
    _anchor_path,
    _atr_at,
    _er,
    _minutes_complete,
    condition_window,
    prev_15m_break,
)
from cbr.engine.params_pc3 import Cbr1hPC3Params, load_cbr1h_pc3, spec_hash_pc3
from cbr.structure import condition as cond_mod
from cbr.structure import overextension_pc3 as oe3
from cbr.structure.condition_pc3 import classify_pc3
from cbr.structure.indicators import atr
from cbr.structure.levels import aoi_tap, candle_close_levels, in_rollover, in_sydney_session
from cbr.structure.shifts_pc3 import Type3ArmPC3, hvcs_structural, track_type3_pc3
from cbr.structure.swings import legs, usable, zigzag

H1, M5, M30 = pd.Timedelta(hours=1), pd.Timedelta(minutes=5), pd.Timedelta(minutes=30)
STOP_ANCHOR_SOURCE = "STRUCTURE_TICK_MID_5S_EXTENSION_EXTREME"
PARENT_HVCS, PARENT_M1_T3 = "HVCS", "M1_TYPE3"
T30_PASS, T30_CONCERN, T30_NA, T30_UNRESOLVED = "PASS", "QUALITY_CONCERN", "NOT_APPLICABLE", "UNRESOLVED"
BLOCKER_PARITY = "PHASE13C_PARITY_NOT_RUN"
DECISION_FIELDS = ["signal_id", "hour_open_utc", "timestamp", "direction", "entry_model", "parent_structure_type",
                   "parent_structure_time", "event", "rules_failed", "activation_time", "five_second_shift_level",
                   "five_second_sweep_time", "valid_until", "ext_extreme_at_decision", "condition",
                   "condition_fallback_applied", "c_med", "n_legs", "cond_direction", "extension_state",
                   "extension_activation_time", "extension_origin_price", "oe_duration_min", "oe_size",
                   "oe_deepest_retracement", "oe_retracement_ratio", "q_break_by_q", "raw_setup_armed",
                   "prior_setup_count", "prior_setup_age_min"]
TRIGGER_FIELDS = ["signal_id", "five_second_shift_time", "five_second_shift_level_at_trigger", "hvcs_rule_state",
                  "hvcs_minutes", "hvcs_indecision_bars", "rules_failed_at_trigger", "event_at_trigger",
                  "timing30_state"]


@dataclass(frozen=True)
class Cbr1hPC3Result:
    candidates: pd.DataFrame
    hours: pd.DataFrame
    signals: list[dict]
    spec_hash: str
    variant: str


class _Context:
    def __init__(self, s1m, s5s, p: Cbr1hPC3Params):
        self.s1m, self.s5s = s1m, s5s
        self.b5 = rollup_structure(s1m, "5min")
        self.b15 = rollup_structure(s1m, "15min")
        self.b1h = rollup_structure(s1m, "1h")
        self.atr1m = atr(s1m, p.atr_length)
        self.atr1h = atr(self.b1h, p.atr_length)
        self.sw_mtf = zigzag(self.b5, atr(self.b5, p.atr_length), p.k_mtf, M5)
        self.sw_ltf = zigzag(s1m, self.atr1m, p.k_ltf, M1)
        self.t3_ltf = track_type3_pc3(s1m, self.sw_ltf, max_reversal=p.max_reversal_ltf, tick=p.tick)
        self.sw_s5 = zigzag(s5s, atr(s5s, p.atr_length), p.k_s5, S5)
        self.t3_s5 = track_type3_pc3(s5s, self.sw_s5, max_reversal=p.max_reversal_s5, tick=p.tick)
        self.levels = pd.concat([candle_close_levels(rollup_structure(s1m, f), pd.Timedelta(f)) for f in ("30min", "1h")],
                                ignore_index=True) if p.aoi_required else None


def run_cbr1h_pc3(s1m: pd.DataFrame, s5s: pd.DataFrame, *, start: pd.Timestamp, end: pd.Timestamp, variant: str = "A",
                  params: Cbr1hPC3Params | None = None) -> Cbr1hPC3Result:
    """Evaluate hourly candles opening in [start, end). Earlier bars are warm-up."""
    require_structure(s1m)
    require_structure(s5s)
    p = params or load_cbr1h_pc3(variant)
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
        _finalise(cand, p)
        cand = cand[cand["hour_open_utc"] >= start].reset_index(drop=True)
    hours_df = pd.DataFrame(hour_rows)
    if len(hours_df):
        hours_df = hours_df[hours_df["hour_open_utc"] >= start].reset_index(drop=True)
    shash = spec_hash_pc3()
    signals = [_signal(r, p, shash) for _, r in cand.iterrows()
               if r["event_at_trigger"] == "ARMED_AT_TRIGGER"] if len(cand) else []
    if len(cand):
        cand["spec_hash"] = shash
    return Cbr1hPC3Result(cand, hours_df, signals, shash, p.variant)


def _extension(ctx: _Context, h0, h_open, as_of, p: Cbr1hPC3Params):
    """Hourly extension state at `as_of`. The Q1 reference is the completed 15m candle before the hour (D29-6)."""
    prev = ctx.b15.loc[h0 - M15] if (h0 - M15) in ctx.b15.index else None
    return oe3.evaluate_pc3(ctx.s1m, h0, h_open, as_of, pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac,
                            earliest_activation_min=p.earliest_activation_min,
                            prev_candle_high=None if prev is None else float(prev["high"]),
                            prev_candle_low=None if prev is None else float(prev["low"]))


def _evaluate_hour(h0, ctx: _Context, p: Cbr1hPC3Params):
    h_end = h0 + H1
    h_open = float(ctx.s1m.loc[h0, "open"]) if h0 in ctx.s1m.index else None
    win = condition_window(ctx.s1m.index, h0, p.window, p.window_basis)
    cond, fallback = classify_pc3(ctx.sw_mtf, ctx.s1m, h0, p.window, min_legs=p.min_legs, range_min=p.range_min,
                                  trend_max=p.trend_max, correction_cap=p.correction_cap, aggregate=p.aggregate,
                                  window_start=win["condition_window_start"])
    hour_rules = {
        "M1H-COND-01": cond.condition in (cond_mod.RANGE, cond_mod.TRENDING_RANGE),
        "M1H-COND-02": cond.condition not in (cond_mod.TREND, cond_mod.UNDEFINED),
        "NT_INCOMPLETE_H_OPEN": h_open is not None,
    }
    hrow = {"hour_open_utc": h0, "h_open": h_open, "condition": cond.condition,
            "condition_fallback_applied": fallback, "c_med": cond.c_med, "n_legs": cond.n_legs,
            "cond_direction": cond.direction, "range_high": cond.range_high, "range_low": cond.range_low, **win,
            "rules_failed": [k for k, v in hour_rules.items() if not v], "candidates": 0}
    if h_open is None:
        return hrow, []
    window_start, window_end = h0 + pd.Timedelta(minutes=p.start_min), h0 + pd.Timedelta(minutes=p.end_min)
    scan_end = min(h_end, window_end)
    arms: list[tuple[Type3ArmPC3, dict | None]] = []
    s5_in_hour = [a for a in ctx.t3_s5 if h0 <= a.first_sweep_time and a.first_sweep_time + S5 < scan_end]
    if p.entry_model == "HVCS_S5_SHIFT":
        arms = [(a, None) for a in s5_in_hour]
    elif p.entry_model == "FRACTAL_1M_S5_SHIFT":
        for side in ("BUY", "SELL"):
            parents = _fractal_parents(ctx, h0, h_end, scan_end, side, p)
            for a in s5_in_hour:
                live = [x for x in parents if a.direction == side and x["pullback_reached_at"] <= a.first_sweep_time + S5
                        and (x["pattern_invalid_at"] is None or a.first_sweep_time + S5 < x["pattern_invalid_at"])]
                if live:
                    arms.append((a, max(live, key=lambda x: (x["parent_known_at"], x["t3_break_time"]))))
    else:
        raise ValueError(f"unknown CBR1H entry model {p.entry_model!r}")
    rows = []
    for a, parent in sorted(arms, key=lambda x: (x[0].first_sweep_time, x[0].direction, x[0].broken_swing_time,
                                                 "" if x[1] is None else str(x[1]["t3_break_time"]))):
        as_of = a.first_sweep_time + S5
        ext = _extension(ctx, h0, h_open, as_of, p)
        if ext.direction == "NONE":
            continue
        d = "SELL" if ext.direction == "UP" else "BUY"
        if a.direction != d:
            continue
        hrow["candidates"] += 1
        rows.append(_evaluate_candidate(h0, h_open, cond, fallback, win, hour_rules, ext, a, parent, as_of, d,
                                        window_start, window_end, ctx, p))
    return hrow, rows


def _fractal_parents(ctx: _Context, h0, h_end, scan_end, side, p: Cbr1hPC3Params) -> list[dict]:
    """§6B parent: a completed 1m type 3 (PC3 semantics) inside H, then a ≥ 50% pullback measured on closed 5s bars."""
    out = []
    for t3 in ctx.t3_ltf:
        if t3.direction != side or t3.end != "BREAK" or not (h0 <= t3.end_time < h_end):
            continue
        known_at = t3.end_time + M1
        sweep = t3.sweep_bar_extreme
        bars = ctx.s5s[(ctx.s5s.index >= t3.end_time) & (ctx.s5s.index + S5 <= scan_end)]
        impulse, reached_at, invalid_at = None, None, None
        for t, row in bars.iterrows():
            beyond = (row["high"] > sweep) if side == "SELL" else (row["low"] < sweep)
            if beyond and t + S5 > known_at:
                if reached_at is not None:
                    invalid_at = t + S5
                break
            if side == "SELL":
                impulse = row["low"] if impulse is None else min(impulse, row["low"])
                retrace = row["high"] >= impulse + p.fractal_pullback_min * (sweep - impulse)
            else:
                impulse = row["high"] if impulse is None else max(impulse, row["high"])
                retrace = row["low"] <= impulse - p.fractal_pullback_min * (impulse - sweep)
            if reached_at is None and t + S5 > known_at and retrace:
                reached_at = t + S5
        if reached_at is not None:
            out.append({"t3_sweep_time": t3.first_sweep_time, "t3_break_time": t3.end_time, "parent_known_at": known_at,
                        "sweep_extreme": sweep, "pullback_reached_at": reached_at, "pattern_invalid_at": invalid_at})
    return out


def _timing30(ctx: _Context, h0, t_b, d: str, p: Cbr1hPC3Params) -> dict:
    """OQ-42 diagnostic, unchanged from PC2: evaluated at the 5s shift, never a rejection."""
    out = {"timing30_state": T30_NA, "timing30_push": None, "timing30_threshold": None, "timing30_exception": None}
    if t_b is None or not (h0 + M30 <= t_b < h0 + M30 + M15):
        return out
    q30 = ctx.s5s[(ctx.s5s.index >= h0 + M30) & (ctx.s5s.index + S5 <= t_b)]
    a1 = _atr_at(ctx.atr1m, M1, t_b)
    c15 = ctx.b15.loc[h0 + M15] if (h0 + M15) in ctx.b15.index else None
    if not len(q30) or a1 is None or c15 is None:
        out["timing30_state"] = T30_UNRESOLVED
        return out
    o30 = float(q30["open"].iloc[0])
    push = (float(q30["high"].max()) - o30) if d == "SELL" else (o30 - float(q30["low"].min()))
    exception = bool(c15["close"] < c15["open"]) if d == "SELL" else bool(c15["close"] > c15["open"])
    threshold = p.q30_push_atr * a1
    out.update({"timing30_push": push, "timing30_threshold": threshold, "timing30_exception": exception,
                "timing30_state": T30_PASS if (push >= threshold or exception) else T30_CONCERN})
    return out


def _hvcs_at(ctx: _Context, h0, ext, as_of, p: Cbr1hPC3Params) -> dict:
    """HVCS evaluated at `as_of` (the 5s shift under D29-11). Only 1m bars closed at `as_of` are read."""
    out = {"hvcs_rule_state": None, "hvcs_minutes": None, "hvcs_indecision_bars": None, "hvcs_start_time": None,
           "hvcs_end_time": None, "hvcs_body_atr": None, "lvcs": None, "hvcs_evaluated_at": as_of}
    if as_of is None:
        return out
    closed = ctx.s1m[(ctx.s1m.index >= h0 - M30) & (ctx.s1m.index + M1 <= as_of)]
    a1 = _atr_at(ctx.atr1m, M1, as_of) or 0.0
    ext_now = _extension(ctx, h0, float(ctx.s1m.loc[h0, "open"]), as_of, p)
    end_bar = ext_now.extreme_time
    if end_bar is None or end_bar not in closed.index:
        return out | {"hvcs_rule_state": False}
    seq = hvcs_structural(closed, end_bar, ext_now.direction, atr_1m=a1, min_minutes=p.hvcs_min_minutes,
                          lvcs_body_atr=p.hvcs_lvcs_body_atr)
    return {"hvcs_rule_state": bool(seq.valid), "hvcs_minutes": seq.minutes, "hvcs_indecision_bars": seq.indecision_bars,
            "hvcs_start_time": end_bar - (seq.minutes - 1) * M1 if seq.minutes else None, "hvcs_end_time": end_bar,
            "hvcs_body_atr": seq.body_atr, "lvcs": seq.low_volume, "hvcs_evaluated_at": as_of}


def _evaluate_candidate(h0, h_open, cond, fallback, win, hour_rules, ext, a: Type3ArmPC3, parent, as_of, d,
                        window_start, window_end, ctx: _Context, p: Cbr1hPC3Params) -> dict:
    rules: dict[str, bool | None] = dict(hour_rules)
    known = usable(ctx.sw_mtf, as_of)
    pos = cond.pos(ext.extreme) if ext.extreme is not None else None
    er_pro = beyond = None
    if cond.condition == cond_mod.RANGE:
        rules["M1H-LOC-01"] = pos is not None and (pos >= p.range_extreme if d == "SELL" else pos <= 1 - p.range_extreme)
    elif cond.condition == cond_mod.TRENDING_RANGE and cond.direction != "NONE":
        if (d == "SELL") == (cond.direction == "UP"):
            kind = "H" if d == "SELL" else "L"
            last = known[known["kind"] == kind]
            beyond = bool(len(last)) and ext.extreme is not None and (
                (ext.extreme > last["price"].iloc[-1]) if d == "SELL" else (ext.extreme < last["price"].iloc[-1]))
            rules["M1H-LOC-02"] = beyond
        else:
            lg = legs(known)
            lg = lg[lg["dir"] == (1 if cond.direction == "UP" else -1)]
            er_pro = _er(ext.extreme, lg.iloc[-1]) if len(lg) and ext.extreme is not None else None
            rules["M1H-LOC-03"] = er_pro is not None and p.pro_er_min <= er_pro <= p.pro_er_max
    a1 = _atr_at(ctx.atr1m, M1, as_of)
    if p.aoi_required:
        rules["M1H-LOC-04"] = ext.extreme is not None and aoi_tap(ctx.levels, ext.extreme, h0,
                                                                  zone=p.aoi_zone_atr * (a1 or 0.0),
                                                                  lookback=p.aoi_lookback)
    a1h = _atr_at(ctx.atr1h, H1, as_of)
    rules["M1H-OE-00-ACTIVE"] = ext.state == oe3.EXTENSION_ACTIVE
    rules["M1H-OE-01"] = ext.state == oe3.EXTENSION_ACTIVE and ext.duration_min >= p.oe_min_minutes
    rules["M1H-OE-02"] = ext.no_pullback
    rules["M1H-OE-04a"] = not ext.two_sided
    rules["M1H-OE-04b"] = a1h is not None and ext.size >= p.oe_min_size_atr * a1h
    q0 = (as_of - pd.Timedelta(microseconds=1)).floor("15min")
    q = prev_15m_break(ctx.s5s, ctx.b15, q0, as_of, d)
    if parent is None:
        parent_type, parent_time, parent_known = PARENT_HVCS, ext.extreme_time, None
        rules["M1H-6A-1-HVCS-INTO-SHIFT"] = None                      # trigger-time rule (D29-11), set below
        rules["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] = bool(q["q_break_by_q"] or q["q_prev_closed_in_trade_direction"])
        rules["M1H-6A-3-NEW-EXTREME-IN-Q"] = ext.extreme_time is not None and ext.extreme_time >= q0
    else:
        parent_type, parent_time, parent_known = PARENT_M1_T3, parent["t3_break_time"], parent["parent_known_at"]
        rules["M1H-6B-1-T3-AFTER-OE"] = ext.extreme_time is not None and parent["t3_break_time"] >= ext.extreme_time
        rules["M1H-6B-3-PULLBACK"] = parent["pullback_reached_at"] <= as_of
    if p.early_shift_guard == "FINAL_PUSH":                            # D9 ablation, research only
        hour5 = ctx.s5s[(ctx.s5s.index >= h0) & (ctx.s5s.index + S5 <= as_of)]
        ext5 = float(hour5["high"].max()) if d == "SELL" else float(hour5["low"].min())
        rules["ABL-D9-FINAL-PUSH"] = (a.sweep_bar_extreme >= ext5) if d == "SELL" else (a.sweep_bar_extreme <= ext5)
    elif p.early_shift_guard == "ALIGN_15M":
        rules["ABL-D9-ALIGN-15M"] = bool(q["q_break_by_q"])
    elif p.early_shift_guard != "NONE":
        raise ValueError(f"unknown early_shift_guard {p.early_shift_guard!r}")

    active_from = max(as_of, window_start)
    rules["M1H-TIME-01"] = active_from < window_end
    rules["NT_SYDNEY"] = not (in_sydney_session(active_from) or in_sydney_session(max(active_from, window_end - S5)))
    rules["NT_ROLLOVER"] = not any(in_rollover(t, pre_min=p.rollover_pre_min, post_min=p.rollover_post_min)
                                   for t in (active_from, max(active_from, window_end - S5)))
    complete, missing = _minutes_complete(ctx.s1m.index, h0, as_of.floor("1min"))
    rules["NT_INCOMPLETE_H"] = complete
    # Under re-anchoring the trigger moves, so the decision-time ledger records the trigger in force AT THE DECISION;
    # the final trigger (after any re-anchor) is a trigger-time field.
    trigger = a.trigger_at(as_of)
    if trigger is None:
        trigger = a.trigger_price
    target_dec = None if ext.extreme is None else ext.extreme - 0.5 * (ext.extreme - h_open)
    rules["IMPL-REWARD"] = target_dec is not None and ((trigger > target_dec) if d == "SELL" else (trigger < target_dec))

    shift = a.trigger_break_time if a.end == "BREAK" else None
    cancel_time, cancel_reason = window_end, "WINDOW_END"
    if shift is not None and shift < window_start:
        cancel_time, cancel_reason, shift = shift, "S5_SHIFT_BEFORE_WINDOW", None
    elif shift is not None and shift >= window_end:
        shift = None
    if a.end == "TIMEOUT" and a.end_time is not None and a.end_time < cancel_time:
        cancel_time, cancel_reason = a.end_time, "S5_T3_TIMEOUT"
    if parent is not None and parent["pattern_invalid_at"] is not None and parent["pattern_invalid_at"] < cancel_time:
        cancel_time, cancel_reason = parent["pattern_invalid_at"], "FRACTAL_PULLBACK_INVALID"
    if shift is not None and shift >= cancel_time:
        shift = None
    horizon = shift if shift is not None else cancel_time
    for t in pd.date_range(as_of.floor("1min") + M1, horizon, freq="1min", inclusive="both"):
        later = _extension(ctx, h0, h_open, t, p)
        if later.direction != ext.direction or not later.no_pullback:
            if t < cancel_time and (shift is None or t <= shift):
                cancel_time, cancel_reason = t, "OE_INVALIDATED"
                shift = None
            break
    if shift is not None:
        cancel_time, cancel_reason = shift, "S5_SHIFT_TRIGGERED"
    hv = _hvcs_at(ctx, h0, ext, shift, p) if shift is not None else _hvcs_at(ctx, h0, ext, None, p)
    # D29-11: the HVCS rule is a TRIGGER-time rule. It must never enter the decision-time ledger, or a decision field
    # would depend on information that arrives after the decision.
    rules_at_trigger = dict(rules)
    if parent is None:
        rules_at_trigger["M1H-6A-1-HVCS-INTO-SHIFT"] = hv["hvcs_rule_state"] if shift is not None else None
    t30 = _timing30(ctx, h0, shift, d, p)
    anchor, anchor_time, path = _anchor_path(ctx.s5s, h0, active_from, cancel_time if shift is None else shift + S5, d)
    return {
        "hour_open_utc": h0, "timestamp": as_of, "direction": d, "variant": p.variant, "entry_model": p.entry_model,
        "oe_origin": p.oe_origin, "early_shift_guard": p.early_shift_guard,
        "parent_structure_type": parent_type, "parent_structure_time": parent_time, "parent_known_at": parent_known,
        "fractal": parent, "rules": rules, "rules_at_trigger": rules_at_trigger, "h_open": h_open,
        "condition": cond.condition, "condition_fallback_applied": fallback, "c_med": cond.c_med, "n_legs": cond.n_legs,
        "cond_direction": cond.direction,
        **{k: win[k] for k in ("condition_window_basis", "condition_elapsed_clock_minutes",
                               "condition_tradable_minutes", "condition_missing_minutes")},
        "range_high": cond.range_high, "range_low": cond.range_low, "pos_oe_extreme": pos, "er_pro": er_pro,
        "beyond_external": beyond,
        "extension_state": ext.state, "pre_extension_start": ext.pre_extension_start,
        "extension_activation_time": ext.activation_time, "extension_activation_price": ext.activation_price,
        "extension_activation_reason": ext.activation_reason, "previous_15m_reference": ext.previous_15m_reference,
        "extension_origin_price": ext.origin_price, "extension_origin_time": ext.origin_time,
        "extension_extreme_path": ext.extreme_path,
        "oe_dir": ext.direction, "ext_extreme_at_decision": ext.extreme, "oe_extreme_time": ext.extreme_time,
        "oe_size": ext.size, "oe_size_atr1h": (ext.size / a1h) if a1h else None, "oe_duration_min": ext.duration_min,
        "oe_no_pullback": ext.no_pullback, "oe_deepest_retracement": ext.deepest_retracement,
        "oe_retracement_ratio": ext.retracement_ratio, "oe_two_sided": ext.two_sided,
        "oe_opposite_wick": ext.opposite_wick, "atr_1m": a1, "atr_1h": a1h, **hv, **q,
        "five_second_sweep_time": a.first_sweep_time, "five_second_shift_level": trigger,
        "five_second_shift_level_at_trigger": a.trigger_price, "trigger_history": list(a.trigger_history),
        "five_second_shift_time": shift, "five_second_swept_price": a.swept_price,
        "five_second_broken_price": a.broken_price, "sweep_bar_extreme": a.sweep_bar_extreme,
        "first_sweep_time": a.first_sweep_time, "latest_sweep_extreme_time": a.latest_sweep_extreme_time,
        "trigger_confirmation_time": a.trigger_confirmation_time, "trigger_break_time": a.trigger_break_time,
        "trigger_reanchored": a.reanchored, "s5_t3_end": a.end,
        "entry_reference_price": trigger, "activation_time": active_from, "valid_until": window_end,
        **t30, "mih_decision": (as_of - h0) / M1,
        "candle_open_price": h_open, "structure_stop_anchor": anchor, "stop_anchor_time": anchor_time,
        "stop_anchor_source": STOP_ANCHOR_SOURCE, "stop_anchor_path": path, "stop_buffer_price": p.buffer_atr * (a1 or 0.0),
        "target_at_decision": target_dec,
        "target_at_activation": None if anchor is None else anchor - 0.5 * (anchor - h_open),
        "cancel_time": cancel_time, "cancel_reason": cancel_reason, "h_missing_minutes": missing,
    }


def _finalise(cand: pd.DataFrame, p: Cbr1hPC3Params) -> None:
    """Prior-setup diagnostics (D29-12: never an eligibility rule) and the ledger fields."""
    cand["raw_setup_armed"] = [all(v is not False for v in r.values()) for r in cand["rules"]]
    raw = cand[cand["raw_setup_armed"]]
    cand["prior_setup_window_start"] = cand["hour_open_utc"] - p.prior_lookback
    cand["prior_setup_window_end"] = cand["hour_open_utc"]
    counts, latest, ages, models = [], [], [], []
    for _, r in cand.iterrows():
        prior = raw[(raw["timestamp"] >= r["prior_setup_window_start"]) & (raw["timestamp"] < r["prior_setup_window_end"])]
        counts.append(len(prior))
        last = prior["timestamp"].max() if len(prior) else pd.NaT
        latest.append(last)
        ages.append(None if len(prior) == 0 else (r["hour_open_utc"] - last) / M1)
        models.append(r["entry_model"] if len(prior) else None)
    cand["prior_setup_count"] = counts
    cand["prior_setup_exists"] = [n >= 1 for n in counts]
    cand["prior_setup_latest_time"] = pd.to_datetime(pd.Series(latest, index=cand.index, dtype="object"), utc=True)
    cand["prior_setup_age_min"] = pd.to_numeric(pd.Series(ages, index=cand.index), errors="coerce")
    cand["prior_setup_model"] = models
    failed = [sorted(k for k, v in r.items() if v is False) for r in cand["rules"]]
    cand["rules_failed"] = failed
    cand["rules_not_evaluated"] = [sorted(k for k, v in rr.items() if v is None) for rr in cand["rules"]]
    cand["event"] = ["ARMED" if not bad else "REJECTED" for bad in failed]          # decision-time verdict
    trig_failed = [sorted(k for k, v in r.items() if v is False) for r in cand["rules_at_trigger"]]
    cand["rules_failed_at_trigger"] = trig_failed
    cand["event_at_trigger"] = [                                                    # trigger-time verdict (D29-11)
        "NO_TRIGGER" if t is None or pd.isna(t) else ("ARMED_AT_TRIGGER" if not bad else "REJECTED_AT_TRIGGER")
        for t, bad in zip(cand["five_second_shift_time"], trig_failed, strict=True)]
    cand["reject_reasons"] = [sorted(set(f)) for f in failed]
    cand["eligibility_blockers"] = [[BLOCKER_PARITY] for _ in range(len(cand))]
    cand["baseline_eligible"] = False
    seq = cand.groupby(["hour_open_utc", "direction"]).cumcount()
    cand["signal_id"] = [f"CBR1H_BASELINE_V1-PC3/{r['variant']}/{r['hour_open_utc']:%Y%m%dT%H%M}/{r['direction']}/{s}"
                         for (_, r), s in zip(cand.iterrows(), seq, strict=True)]


def _iso(t):
    return None if t is None or (not isinstance(t, pd.Timestamp) and pd.isna(t)) else pd.Timestamp(t).isoformat()


def _signal(r: pd.Series, p: Cbr1hPC3Params, shash: str) -> dict:
    long = r["direction"] == "BUY"
    return {
        "signal_id": r["signal_id"], "model": "CBR1H_BASELINE_V1-PC3", "variant": p.variant, "price_role": "STRUCTURE",
        "timestamp": _iso(r["timestamp"]), "direction": "LONG" if long else "SHORT",
        "entry_trigger_time": _iso(r["activation_time"]), "entry_expiry_time": _iso(r["valid_until"]),
        "entry_order_type": "STOP", "entry_reference_price": r["entry_reference_price"],
        "entry_structure": {"entry_model": r["entry_model"], "parent_structure_type": r["parent_structure_type"],
                            "parent_structure_time": _iso(r["parent_structure_time"]),
                            "first_sweep_time": _iso(r["first_sweep_time"]),
                            "latest_sweep_extreme_time": _iso(r["latest_sweep_extreme_time"]),
                            "trigger_confirmation_time": _iso(r["trigger_confirmation_time"]),
                            "trigger_reanchored": int(r["trigger_reanchored"]),
                            "five_second_shift_level": r["five_second_shift_level"]},
        "extension": {"state": r["extension_state"], "activation_time": _iso(r["extension_activation_time"]),
                      "activation_reason": r["extension_activation_reason"],
                      "origin_price": r["extension_origin_price"], "size": r["oe_size"],
                      "duration_min": r["oe_duration_min"], "deepest_retracement": r["oe_deepest_retracement"],
                      "retracement_ratio": r["oe_retracement_ratio"]},
        "stop_rule": {"extension_extreme": r["ext_extreme_at_decision"], "extension_extreme_source": "TICK_MID",
                      "candle_open_price": r["candle_open_price"], "structure_stop_anchor": r["structure_stop_anchor"],
                      "stop_anchor_time": _iso(r["stop_anchor_time"]), "stop_anchor_source": r["stop_anchor_source"],
                      "stop_anchor_path": [[_iso(t), v] for t, v in r["stop_anchor_path"]],
                      "final_execution_stop": None, "direction": "LONG" if long else "SHORT",
                      "buffer": {"param": "stop.buffer_atr", "value": p.buffer_atr, "unit": "ATR(1m,14)",
                                 "atr_at_decision": r["atr_1m"], "label": "ASSUMPTION", "source": ["OQ-11"]},
                      "spread_policy": "ADD_SPREAD_AT_FILL"},
        "stop_price": None, "target_price": r["target_at_activation"],
        "range_high": r["range_high"], "range_low": r["range_low"],
        "context_state": {"condition": r["condition"], "condition_fallback_applied": bool(r["condition_fallback_applied"]),
                          "c_med": r["c_med"], "n_legs": r["n_legs"], "cond_direction": r["cond_direction"],
                          "pos_oe_extreme": r["pos_oe_extreme"], "condition_window_basis": r["condition_window_basis"],
                          "prior_setup_exists": bool(r["prior_setup_exists"]),
                          "prior_setup_count": int(r["prior_setup_count"]),
                          "prior_setup_age_min": r["prior_setup_age_min"], "prior_setup_model": r["prior_setup_model"],
                          "hvcs_minutes": r["hvcs_minutes"], "hvcs_indecision_bars": r["hvcs_indecision_bars"]},
        "dxy_state": {"availability": "MISSING", "reason_codes": ["NOT_PROVIDED"]},
        "source_feed": {"feed_id": "dukascopy_ticks:xauusd", "manifest_hash": None},
        "data_confidence": {"level": "FULL", "reason_codes": []}, "reason_code": "ARMED", "spec_hash": shash,
        "eligibility": {"baseline_eligible": False, "blockers": list(r["eligibility_blockers"])},
        "lifecycle": {"cancel_time": _iso(r["cancel_time"]), "cancel_reason": r["cancel_reason"],
                      "five_second_shift_time": _iso(r["five_second_shift_time"]),
                      "timing30_state": r["timing30_state"]},
    }


def decision_frame(result: Cbr1hPC3Result) -> pd.DataFrame:
    c = result.candidates
    if not len(c):
        return pd.DataFrame(columns=DECISION_FIELDS)
    out = c[DECISION_FIELDS].copy()
    out["rules_failed"] = out["rules_failed"].map(lambda x: ",".join(x))
    return out


def trigger_frame(result: Cbr1hPC3Result) -> pd.DataFrame:
    c = result.candidates
    if not len(c):
        return pd.DataFrame(columns=TRIGGER_FIELDS)
    out = c[TRIGGER_FIELDS].copy()
    out["rules_failed_at_trigger"] = out["rules_failed_at_trigger"].map(lambda x: ",".join(x))
    return out


def result_hash(result: Cbr1hPC3Result) -> str:
    payload = json.dumps({"candidates": decision_frame(result).astype(str).to_dict("records"),
                          "triggers": trigger_frame(result).astype(str).to_dict("records"),
                          "signals": result.signals}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
