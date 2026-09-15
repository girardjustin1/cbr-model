"""CBR1H_BASELINE_V1 reference engine (docs/strategy/1h-cbr-machine-spec.md rev PC1, CBR_PRIMITIVES_V1 rev 1.2).

Signal logic only, on STRUCTURE bars (tick-derived mid, D16); never reads bid/ask. Fills, spread, the one-position rule
and one-fill-per-hour belong to the Phase 14A execution layer.

Owner ruling D19 (Phase 13 readiness):
  * ENTRY TRIGGER (OQ-39): the canonical trigger of both variants is a 5-second type 3 shift in the trade direction
    (primitives §4.1 on S5 swings). A candidate is one 5s sweep; its stop order sits at the type 3 trigger and the shift
    completes when a 5s bar breaks it (`five_second_shift_time`). The variants keep separate PARENT SETUP STRUCTURES:
      A  HVCS_S5_SHIFT        a valid HVCS in the extension direction that runs directly into the shift (OQ-43)
      B  FRACTAL_1M_S5_SHIFT  a completed 1m type 3 (known at its bar close) → ≥ 50% pullback → the 5s shift inside it
    A 1m HILO is recorded only as an observable equivalent (`m1_hilo_armed_at_decision`), never as the trigger.
  * PREVIOUS 15m CANDLE (OQ-41): Q−1 must be broken by the current candle Q itself; exception: Q−1 closed in the trade
    direction.
  * :30 TIMING (OQ-42): evaluated at the 5s shift time as the diagnostic `timing30_state`; hard-veto semantics are
    unresolved, so it never rejects a signal.
  * PRIOR SETUPS (OQ-36): M1H-COND-04 counts qualifying CBR1H setups FORMED (raw setups: every rule except COND-04) with
    decision time in [H.t0 − lookback, H.t0); outcomes are never used. `prior_setup_played_out_status` = UNKNOWN.
  * CONDITION WINDOW (OQ-40): measured in scheduled-tradable time (ASSUMPTION).

Causality: decision fields (`DECISION_FIELDS`) use only bars closed at the candidate's `timestamp` (the sweeping 5s bar's
close); trigger-time fields (`TRIGGER_FIELDS`) use only bars closed at the 5s shift. A 1m bar is used only after its
close, so 1m information can't reveal a 5s shift earlier than the 5s bars do.

D8/D9 switches (`oe_origin`, `early_shift_guard`) exist for STRICT COURSE parity views (protocol §2); the baseline
values (HOUR_OPEN, NONE) add no rule.
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
from cbr.engine.params import Cbr1hParams, load_cbr1h, spec_hash
from cbr.structure import condition as cond_mod
from cbr.structure import overextension as oe_mod
from cbr.structure.indicators import atr
from cbr.structure.levels import aoi_tap, candle_close_levels, in_rollover, in_sydney_session
from cbr.structure.shifts import CandleSequence, Type3Arm, hvcs, track_type3
from cbr.structure.swings import legs, usable, zigzag

H1, M5, M30 = pd.Timedelta(hours=1), pd.Timedelta(minutes=5), pd.Timedelta(minutes=30)
TREND_DIRECTION_UNRESOLVED = "TREND_DIRECTION_UNRESOLVED"
STOP_ANCHOR_SOURCE = "STRUCTURE_TICK_MID_5S_EXTENSION_EXTREME"
PARENT_HVCS, PARENT_M1_T3 = "HVCS", "M1_TYPE3"
T30_PASS, T30_CONCERN, T30_NA, T30_UNRESOLVED = "PASS", "QUALITY_CONCERN", "NOT_APPLICABLE", "UNRESOLVED"
PLAYED_OUT_UNKNOWN = "UNKNOWN"
# Eligibility blockers still open after D19 (Phase 13 parity-candidate, not a validated baseline)
BLOCKER_PARITY = "PHASE13_PARITY_NOT_RUN"
BLOCKER_HVCS_GAP = "HVCS_INDECISION_LIMIT_UNRESOLVED (OQ-44)"

DECISION_FIELDS = ["signal_id", "hour_open_utc", "timestamp", "direction", "entry_model", "parent_structure_type",
                   "parent_structure_time", "event", "rules_failed", "activation_time", "five_second_shift_level",
                   "five_second_sweep_time", "valid_until", "ext_extreme_at_decision", "condition", "c_med", "n_legs",
                   "cond_direction", "condition_tradable_minutes", "condition_elapsed_clock_minutes",
                   "condition_missing_minutes", "oe_duration_min", "oe_size", "hvcs_minutes", "hvcs_end_bar",
                   "hvcs_gap_bars", "q_break_by_q", "q_prev_closed_in_trade_direction", "prior_setup_count",
                   "m1_hilo_armed_at_decision"]
TRIGGER_FIELDS = ["signal_id", "five_second_shift_time", "timing30_state", "timing30_push", "timing30_threshold"]


@dataclass(frozen=True)
class Cbr1hResult:
    candidates: pd.DataFrame
    hours: pd.DataFrame
    signals: list[dict]
    spec_hash: str
    variant: str


# ------------------------------------------------------------------ HILO arms (observable equivalent only)

def hilo_arms(bars: pd.DataFrame, s5s: pd.DataFrame, tf: pd.Timedelta, side: str, start: pd.Timestamp,
              end: pd.Timestamp, tick: float) -> list[dict]:
    """Stop-order arms of a HILO in `side` (BUY/SELL) for bars j opening in [start, end) on timeframe `tf`.
    prior: known at the close of bar j−1; same: at the first 5s close inside j after j took (j−1)'s opposite extreme
    while its entry side is unbroken."""
    idx = bars.index
    pos = {t: i for i, t in enumerate(idx)}
    out = []
    for tj in pd.date_range(start.ceil(tf), end, freq=tf, inclusive="left"):
        i1, i2 = pos.get(tj - tf), pos.get(tj - 2 * tf)
        if i1 is None or i2 is None:
            continue
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


# ------------------------------------------------------------------ HVCS leading into the shift (OQ-43)

def hvcs_into_shift(closed_1m: pd.DataFrame, end_bar: pd.Timestamp | None, direction: str, *, atr_1m: float,
                    min_minutes: int, max_violations: int, lvcs_body_atr: float
                    ) -> tuple[CandleSequence | None, int, bool]:
    """HVCS that runs directly into the shift (D19-6, OQ-43). `end_bar` is the final displacement bar: the closed 1m bar
    that set the extension extreme. The sequence is the HVCS run ending there. Closed bars after it are indecision bars;
    the sequence stays continuous into the shift while none of them breaks the side it respected (DOWN: a high above the
    end bar's high; UP: a low below its low). No maximum indecision count is imposed: none is sourced (OQ-44).
    Returns (sequence, indecision bar count, continuous)."""
    if end_bar is None or end_bar not in closed_1m.index or not atr_1m:
        return None, 0, False
    gap = closed_1m[closed_1m.index > end_bar]
    ref = closed_1m.loc[end_bar]
    continuous = bool((gap["high"] <= ref["high"]).all()) if direction == "DOWN" else bool((gap["low"] >= ref["low"]).all())
    seq = hvcs(closed_1m, end_bar, direction, atr_1m=atr_1m, min_minutes=min_minutes, max_violations=max_violations,
               lvcs_body_atr=lvcs_body_atr)
    return seq, len(gap), continuous


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
        self.sw_s5 = zigzag(s5s, atr(s5s, p.atr_length), p.k_s5, S5)
        self.t3_s5 = track_type3(s5s, self.sw_s5, max_reversal=p.max_reversal_s5, tick=p.tick, latest_pair_only=True)
        self.levels = pd.concat([candle_close_levels(rollup_structure(s1m, f), pd.Timedelta(f)) for f in ("30min", "1h")],
                                ignore_index=True) if p.aoi_required else None


def _oe(ctx: _Context, h0, h_open, as_of, p: Cbr1hParams):
    q0 = (as_of - pd.Timedelta(microseconds=1)).floor("15min")
    prev = ctx.b15.loc[q0 - M15] if (q0 - M15) in ctx.b15.index else None
    a1 = _atr_at(ctx.atr1m, M1, as_of)
    oe = oe_mod.evaluate(ctx.s1m, h0, h_open, as_of, atr_1m=a1 or 0.0, activation_atr=p.activation_atr,
                         pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac,
                         prev_candle_high=None if prev is None else float(prev["high"]),
                         prev_candle_low=None if prev is None else float(prev["low"]), origin=p.oe_origin)
    return oe, a1, q0


def _evaluate_hour(h0, ctx: _Context, p: Cbr1hParams):
    h_end = h0 + H1
    h_open = float(ctx.s1m.loc[h0, "open"]) if h0 in ctx.s1m.index else None
    win = condition_window(ctx.s1m.index, h0, p.window, p.window_basis)
    cond = cond_mod.classify(ctx.sw_mtf, ctx.s1m, h0, p.window, min_legs=p.min_legs, range_min=p.range_min,
                             trend_max=p.trend_max, correction_cap=p.correction_cap, aggregate=p.aggregate,
                             window_start=win["condition_window_start"])
    hour_rules = {
        "M1H-COND-01": cond.condition in (cond_mod.RANGE, cond_mod.TRENDING_RANGE),
        "M1H-COND-02": cond.condition not in (cond_mod.TREND, cond_mod.UNDEFINED),
        "M1H-COND-03": not (cond.condition == cond_mod.TRENDING_RANGE and cond.direction == "NONE"),
        "NT_INCOMPLETE_H_OPEN": h_open is not None,
    }
    hrow = {"hour_open_utc": h0, "h_open": h_open, "condition": cond.condition, "c_med": cond.c_med,
            "n_legs": cond.n_legs, "cond_direction": cond.direction, "range_high": cond.range_high,
            "range_low": cond.range_low, **win, "rules_failed": [k for k, v in hour_rules.items() if not v],
            "context_reason": None if hour_rules["M1H-COND-03"] else TREND_DIRECTION_UNRESOLVED, "candidates": 0}
    if h_open is None:
        return hrow, []
    window_start, window_end = h0 + pd.Timedelta(minutes=p.start_min), h0 + pd.Timedelta(minutes=p.end_min)
    scan_end = min(h_end, window_end)
    arms: list[tuple[Type3Arm, dict | None]] = []
    s5_in_hour = [a for a in ctx.t3_s5 if h0 <= a.sweep_time and a.sweep_time + S5 < scan_end]
    if p.entry_model == "HVCS_S5_SHIFT":
        arms = [(a, None) for a in s5_in_hour]
    elif p.entry_model == "FRACTAL_1M_S5_SHIFT":
        for side in ("BUY", "SELL"):
            parents = _fractal_parents(ctx, h0, h_end, scan_end, side, p)
            for a in s5_in_hour:
                live = [x for x in parents if a.direction == side and x["pullback_reached_at"] <= a.sweep_time + S5
                        and (x["pattern_invalid_at"] is None or a.sweep_time + S5 < x["pattern_invalid_at"])]
                if live:                                     # the most recent parent pattern known at the sweep
                    arms.append((a, max(live, key=lambda x: (x["parent_known_at"], x["t3_break_time"]))))
    else:
        raise ValueError(f"unknown CBR1H entry model {p.entry_model!r}")
    rows = []
    for a, parent in sorted(arms, key=lambda x: (x[0].sweep_time, x[0].direction, x[0].broken_swing_time,
                                                 "" if x[1] is None else str(x[1]["t3_break_time"]))):
        as_of = a.sweep_time + S5
        oe, a1, q0 = _oe(ctx, h0, h_open, as_of, p)
        if oe.direction == "NONE":
            continue
        d = "SELL" if oe.direction == "UP" else "BUY"
        if a.direction != d:
            continue                                     # a shift in the extension's own direction isn't a candidate
        hrow["candidates"] += 1
        rows.append(_evaluate_candidate(h0, h_open, cond, win, hour_rules, oe, a1, q0, a, parent, as_of, d,
                                        window_start, window_end, ctx, p))
    return hrow, rows


def _fractal_parents(ctx: _Context, h0, h_end, scan_end, side, p: Cbr1hParams) -> list[dict]:
    """§6B parent: a completed 1m type 3 in `side` inside H, recognised at its break bar's close; impulse from the break
    bar; ≥ 50% pullback measured on closed 5s bars after that close, not beyond the sweep extreme."""
    out = []
    for t3 in ctx.t3_ltf:
        if t3.direction != side or t3.end != "BREAK" or not (h0 <= t3.end_time < h_end):
            continue
        known_at = t3.end_time + M1
        sweep = t3.extreme_before_end
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
            out.append({"t3_sweep_time": t3.sweep_time, "t3_break_time": t3.end_time, "parent_known_at": known_at,
                        "sweep_extreme": sweep, "pullback_reached_at": reached_at, "pattern_invalid_at": invalid_at})
    return out


def _timing30(ctx: _Context, h0, t_b, d: str, p: Cbr1hParams) -> dict:
    """OQ-42 (D19-5): evaluated at the 5s shift time t_b. PASS if the :30 candle traded beyond its open against the trade
    by ≥ q30_push_atr × ATR(1m) before t_b, or the :15 candle closed in the trade direction; else QUALITY_CONCERN."""
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


def _evaluate_candidate(h0, h_open, cond, win, hour_rules, oe, a1, q0, a: Type3Arm, parent, as_of, d, window_start,
                        window_end, ctx: _Context, p: Cbr1hParams) -> dict:
    rules: dict[str, bool | None] = dict(hour_rules)
    rules["M1H-COND-04"] = None                                   # resolved after all setups are formed
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

    closed = ctx.s1m[(ctx.s1m.index + M1 <= as_of) & (ctx.s1m.index >= h0 - M30)]
    hv_end = oe.extreme_time
    hv, hv_gap, hv_continuous = hvcs_into_shift(
        closed, hv_end, oe.direction, atr_1m=a1 or 0.0, min_minutes=p.hvcs_min_minutes,
        max_violations=p.hvcs_max_violations, lvcs_body_atr=p.hvcs_lvcs_body_atr)
    q = prev_15m_break(ctx.s5s, ctx.b15, q0, as_of, d)
    if parent is None:                                             # variant A: HVCS → 5s shift
        parent_type, parent_time, parent_known = PARENT_HVCS, hv_end, (None if hv_end is None else hv_end + M1)
        rules["M1H-6A-1-HVCS-INTO-SHIFT"] = bool(hv and hv.valid and hv_continuous)
        rules["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] = bool(q["q_break_by_q"] or q["q_prev_closed_in_trade_direction"])
        rules["M1H-6A-3-NEW-EXTREME-IN-Q"] = oe.extreme_time is not None and oe.extreme_time >= q0
    else:                                                          # variant B: 1m type 3 → pullback → 5s shift
        parent_type, parent_time, parent_known = PARENT_M1_T3, parent["t3_break_time"], parent["parent_known_at"]
        rules["M1H-6B-1-T3-AFTER-OE"] = oe.extreme_time is not None and parent["t3_break_time"] >= oe.extreme_time
        rules["M1H-6B-3-PULLBACK"] = parent["pullback_reached_at"] <= as_of
    if p.early_shift_guard == "FINAL_PUSH":                        # D9 ablation (STRICT COURSE view only)
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
    trigger = a.trigger_price
    target_dec = oe.extreme - 0.5 * (oe.extreme - h_open)
    rules["IMPL-REWARD"] = (trigger > target_dec) if d == "SELL" else (trigger < target_dec)
    m1_hilo = any(x["arm_time"] <= as_of < x["valid_until"]                     # observable 1m equivalent, closed bars only
                  for x in hilo_arms(ctx.s1m[ctx.s1m.index + M1 <= as_of], ctx.s5s[ctx.s5s.index + S5 <= as_of],
                                     M1, d, as_of.floor("1min") - M1, as_of.floor("1min") + M1, p.tick))

    # lifecycle (after the decision): the order ends at the first of these
    cancel_time, cancel_reason = window_end, "WINDOW_END"
    shift = a.end_time if a.end == "BREAK" else None
    if shift is not None and shift < window_start:
        cancel_time, cancel_reason, shift = shift, "S5_SHIFT_BEFORE_WINDOW", None
    elif shift is not None and shift >= window_end:
        shift = None
    if a.end in ("TIMEOUT", "NEW_SWING") and a.end_time is not None and a.end_time < cancel_time:
        cancel_time, cancel_reason = a.end_time, f"S5_T3_{a.end}"
    if parent is not None and parent["pattern_invalid_at"] is not None and parent["pattern_invalid_at"] < cancel_time:
        cancel_time, cancel_reason = parent["pattern_invalid_at"], "FRACTAL_PULLBACK_INVALID"
    if shift is not None and shift >= cancel_time:
        shift = None
    horizon = shift if shift is not None else cancel_time
    for t in pd.date_range(as_of.floor("1min") + M1, horizon, freq="1min", inclusive="both"):
        later, _, _ = _oe(ctx, h0, h_open, t, p)
        if later.direction != oe.direction or not later.no_pullback:
            if t < cancel_time and (shift is None or t <= shift):
                cancel_time, cancel_reason = t, "OE_PULLBACK"
                shift = None
            break
    if shift is not None:
        cancel_time, cancel_reason = shift, "S5_SHIFT_TRIGGERED"
    t30 = _timing30(ctx, h0, shift, d, p)
    anchor, anchor_time, path = _anchor_path(ctx.s5s, h0, active_from, cancel_time if shift is None else shift + S5, d)
    buffer_price = p.buffer_atr * (a1 or 0.0)
    return {
        "hour_open_utc": h0, "timestamp": as_of, "direction": d, "variant": p.variant, "entry_model": p.entry_model,
        "oe_origin": p.oe_origin, "early_shift_guard": p.early_shift_guard,
        "parent_structure_type": parent_type, "parent_structure_time": parent_time, "parent_known_at": parent_known,
        "fractal": parent, "rules": rules, "h_open": h_open,
        "condition": cond.condition, "c_med": cond.c_med, "n_legs": cond.n_legs, "cond_direction": cond.direction,
        **{k: win[k] for k in ("condition_window_basis", "condition_elapsed_clock_minutes",
                               "condition_tradable_minutes", "condition_missing_minutes")},
        "range_high": cond.range_high, "range_low": cond.range_low, "pos_oe_extreme": pos, "er_pro": er_pro,
        "beyond_external": beyond, "oe_dir": oe.direction, "ext_extreme_at_decision": oe.extreme,
        "oe_extreme_time": oe.extreme_time, "oe_origin_time": oe.origin_time, "oe_size": oe.size,
        "oe_size_atr1h": (oe.size / a1h) if a1h else None, "oe_duration_min": oe.duration_min,
        "oe_no_pullback": oe.no_pullback, "oe_two_sided": oe.two_sided, "oe_opposite_wick": oe.opposite_wick,
        "oe_prev_candle_break": oe.prev_candle_break, "atr_1m": a1, "atr_1h": a1h,
        "hvcs_minutes": hv.minutes if hv else None, "hvcs_body_atr": hv.body_atr if hv else None,
        "hvcs_end_bar": hv_end, "hvcs_gap_bars": hv_gap, "hvcs_continuous": hv_continuous,
        "lvcs": bool(hv and hv.low_volume), **q,
        "five_second_sweep_time": a.sweep_time, "five_second_shift_level": trigger, "five_second_shift_time": shift,
        "five_second_swept_price": a.swept_price, "five_second_broken_price": a.broken_price,
        "sweep_bar_extreme": a.sweep_bar_extreme, "s5_t3_end": a.end, "m1_hilo_armed_at_decision": m1_hilo,
        "entry_reference_price": trigger, "activation_time": active_from, "valid_until": window_end,
        **t30, "mih_decision": (as_of - h0) / M1,
        "candle_open_price": h_open, "structure_stop_anchor": anchor, "stop_anchor_time": anchor_time,
        "stop_anchor_source": STOP_ANCHOR_SOURCE, "stop_anchor_path": path, "stop_buffer_price": buffer_price,
        "target_at_decision": target_dec,
        "target_at_activation": None if anchor is None else anchor - 0.5 * (anchor - h_open),
        "cancel_time": cancel_time, "cancel_reason": cancel_reason, "h_missing_minutes": missing,
    }


def _apply_prior(cand: pd.DataFrame, p: Cbr1hParams) -> None:
    """M1H-COND-04 (D19-1, OQ-36 C′): ≥ prior.min_count qualifying CBR1H setups FORMED with decision time in
    [H.t0 − prior.lookback_hours, H.t0). A qualifying setup is a raw setup: every rule except COND-04 passes. Formation
    only: no target, stop, touch, structure resolution or fill is read."""
    cand["raw_setup"] = [all(v is True for k, v in r.items() if k != "M1H-COND-04" and v is not None)
                         for r in cand["rules"]]
    raw = cand[cand["raw_setup"]]
    counts, latest, failed, events = [], [], [], []
    for _, r in cand.iterrows():
        h0 = r["hour_open_utc"]
        prior = raw[(raw["timestamp"] >= h0 - p.prior_lookback) & (raw["timestamp"] < h0)]
        counts.append(len(prior))
        latest.append(prior["timestamp"].max() if len(prior) else pd.NaT)
        r["rules"]["M1H-COND-04"] = len(prior) >= p.prior_min_count
        bad = sorted(k for k, v in r["rules"].items() if v is False)
        failed.append(bad)
        events.append("ARMED" if not bad else "REJECTED")
    cand["prior_setup_count"] = counts
    cand["prior_setup_exists"] = [n >= 1 for n in counts]
    cand["prior_setup_latest_time"] = pd.to_datetime(pd.Series(latest, index=cand.index, dtype="object"), utc=True)
    cand["prior_setup_played_out_status"] = PLAYED_OUT_UNKNOWN
    cand["rules_failed"] = failed
    cand["rules_not_evaluated"] = [sorted(k for k, v in rr.items() if v is None) for rr in cand["rules"]]
    cand["event"] = events
    cand["reject_reasons"] = [sorted({TREND_DIRECTION_UNRESOLVED if k == "M1H-COND-03" else k for k in f}) for f in failed]
    cand["eligibility_blockers"] = [
        [BLOCKER_PARITY] + ([BLOCKER_HVCS_GAP] if r["parent_structure_type"] == PARENT_HVCS else [])
        for _, r in cand.iterrows()]
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
        "entry_trigger_time": _iso(r["activation_time"]), "entry_expiry_time": _iso(r["valid_until"]),
        "entry_order_type": "STOP", "entry_reference_price": r["entry_reference_price"],
        "entry_structure": {"entry_model": r["entry_model"], "parent_structure_type": r["parent_structure_type"],
                            "parent_structure_time": _iso(r["parent_structure_time"]),
                            "five_second_sweep_time": _iso(r["five_second_sweep_time"]),
                            "five_second_shift_level": r["five_second_shift_level"],
                            "activation_time": _iso(r["activation_time"])},
        "stop_rule": {"extension_extreme": r["ext_extreme_at_decision"], "extension_extreme_source": "TICK_MID",
                      "candle_open_price": r["candle_open_price"],
                      "extension_extreme_at_decision": r["ext_extreme_at_decision"],
                      "sweep_extreme": r["sweep_bar_extreme"],
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
                          "condition_window_basis": r["condition_window_basis"],
                          "condition_tradable_minutes": int(r["condition_tradable_minutes"]),
                          "condition_elapsed_clock_minutes": int(r["condition_elapsed_clock_minutes"]),
                          "condition_missing_minutes": int(r["condition_missing_minutes"]),
                          "oe_duration_min": r["oe_duration_min"], "hvcs_minutes": r["hvcs_minutes"],
                          "prior_setup_exists": bool(r["prior_setup_exists"]),
                          "prior_setup_count": int(r["prior_setup_count"]),
                          "prior_setup_played_out_status": r["prior_setup_played_out_status"]},
        "dxy_state": {"availability": "MISSING", "direction_15m": None, "direction_1h": None, "reason_codes": ["NOT_PROVIDED"]},
        "session_state": {"nt_sydney": False, "nt_rollover": False},
        "source_feed": {"feed_id": "dukascopy_ticks:xauusd", "manifest_hash": None},
        "data_confidence": {"level": "FULL", "reason_codes": []}, "reason_code": "ARMED", "spec_hash": shash,
        "eligibility": {"baseline_eligible": False, "blockers": list(r["eligibility_blockers"])},
        "lifecycle": {"cancel_time": _iso(r["cancel_time"]), "cancel_reason": r["cancel_reason"],
                      "five_second_shift_time": _iso(r["five_second_shift_time"]),
                      "timing30_state": r["timing30_state"]},
    }


# ------------------------------------------------------------------ hourly state for CBR15 (M15-HTF-01)

def hourly_state(result: Cbr1hResult, as_of: pd.Timestamp) -> list[dict]:
    """Causal view of the current hour's raw CBR1H setups at `as_of`: only candidates decided at or before `as_of` and
    lifecycle events at or before it. SIGNAL state: PENDING (decided, not yet active), ACTIVE (stop order live), ENDED
    (cancelled). A setup whose 5s shift broke its trigger on STRUCTURE prices is `SHIFT_TRIGGERED`: whether it FILLED is
    execution state, reported separately as `fill_state = NOT_EVALUATED` (Phase 14A)."""
    c = result.candidates
    if not len(c):
        return []
    h0 = (as_of - pd.Timedelta(microseconds=1)).floor("1h")        # the hour containing as_of (a boundary belongs to the ending hour)
    sel = c[(c["hour_open_utc"] == h0) & (c["timestamp"] <= as_of) & c["raw_setup"]]
    out = []
    for _, r in sel.iterrows():
        shift = r["five_second_shift_time"]
        triggered = isinstance(shift, pd.Timestamp) and shift <= as_of
        ended = r["cancel_time"] <= as_of
        state = ("SHIFT_TRIGGERED" if triggered else "ENDED" if ended
                 else "ACTIVE" if r["activation_time"] <= as_of else "PENDING")
        out.append({"signal_id": r["signal_id"], "decision_time": r["timestamp"], "direction": r["direction"],
                    "state": state, "fill_state": "NOT_EVALUATED" if triggered else "NOT_REQUIRED",
                    "entry_model": r["entry_model"], "oe_dir": r["oe_dir"], "oe_duration_min": r["oe_duration_min"],
                    "mih_decision": r["mih_decision"], "end_reason": r["cancel_reason"] if (ended or triggered) else None,
                    "h_missing_minutes": r["h_missing_minutes"],
                    "confidence": "FULL" if r["h_missing_minutes"] == 0 else "REDUCED"})
    return out


def htf_provider(result: Cbr1hResult):
    """M15-HTF-01 for CBR15, split per D18-11 / D19-15. Returns {"signal": VETO | CLEAR, "fill": NOT_EVALUATED |
    NOT_REQUIRED}. signal = VETO when a raw CBR1H-A setup opposite to the 15m direction is ACTIVE or PENDING in the
    current hour at as_of. fill = NOT_EVALUATED when such a setup's 5s shift already triggered (a fill may exist, which
    only Phase 14A can decide); it is never converted into a signal-state veto."""
    if result.variant != "A":
        raise ValueError("M15-HTF-01 is defined on CBR1H_BASELINE_V1-A")

    def provider(as_of: pd.Timestamp, d15: str) -> dict:
        opposite = "BUY" if d15 == "SELL" else "SELL"
        states = [s["state"] for s in hourly_state(result, as_of) if s["direction"] == opposite]
        return {"signal": "VETO" if any(s in ("ACTIVE", "PENDING") for s in states) else "CLEAR",
                "fill": "NOT_EVALUATED" if "SHIFT_TRIGGERED" in states else "NOT_REQUIRED"}
    return provider


def decision_frame(result: Cbr1hResult) -> pd.DataFrame:
    c = result.candidates
    if not len(c):
        return pd.DataFrame(columns=DECISION_FIELDS)
    out = c[DECISION_FIELDS].copy()
    out["rules_failed"] = out["rules_failed"].map(lambda x: ",".join(x))
    return out


def trigger_frame(result: Cbr1hResult) -> pd.DataFrame:
    c = result.candidates
    if not len(c):
        return pd.DataFrame(columns=TRIGGER_FIELDS)
    return c[TRIGGER_FIELDS].copy()


def result_hash(result: Cbr1hResult) -> str:
    payload = json.dumps({"candidates": decision_frame(result).astype(str).to_dict("records"),
                          "triggers": trigger_frame(result).astype(str).to_dict("records"),
                          "signals": result.signals}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
