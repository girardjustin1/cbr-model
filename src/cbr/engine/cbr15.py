"""CBR15_BASELINE_V1 reference engine (docs/strategy/15min-cbr-machine-spec.md, CBR_PRIMITIVES_V1 rev 1.2).

Signal logic only. Reads STRUCTURE bars (tick-derived mid, D16) through `require_structure`; never reads bid/ask.
Fills, stop/target touches, spread and the one-position rule belong to the Phase 14A execution layer.

For every 15m candle Q the engine evaluates every candidate: a 5-second type 3 sweep (S5 tier, spec §4.1 read
literally, finding F-3) in the direction opposite to Q's overextension. Each candidate gets every rule's outcome, so the
ledger explains every rejection. Candidates passing every rule are ARMED signals in the `cbr-signal.v1` contract shape.

Causality: all rule inputs at a candidate's decision time `timestamp` (close of the sweeping 5s bar) come from bars
closed at or before it. Lifecycle fields (`cancel_time`, `cancel_reason`, `structure_trigger_touch_time`) describe
what happened later and are kept apart from decision fields (`DECISION_FIELDS`).

M15-COND-03 needs "prior setups that played out". Raw setups (candidates passing every rule except COND-03 and the
HTF veto when it is not evaluated) are resolved on STRUCTURE 5s bars: trigger touch, then target vs stop touch, stop
first on the same bar (OQ-05 reading, recorded in OQ-36). Only outcomes resolved before Q's open are counted. These
per-setup outcomes are rule inputs only; no aggregate outcome statistic is produced.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from cbr.data.price_series import require_structure, rollup_structure
from cbr.data.sessions import expected_closed_mask
from cbr.engine.params import Cbr15Params, load_cbr15, spec_hash
from cbr.structure import condition as cond_mod
from cbr.structure import overextension as oe_mod
from cbr.structure.indicators import atr
from cbr.structure.levels import aoi_tap, candle_close_levels, in_rollover, in_sydney_session
from cbr.structure.shifts import Type3Arm, hvcs, track_type3
from cbr.structure.swings import legs, usable, zigzag

M1, S5, M15 = pd.Timedelta(minutes=1), pd.Timedelta(seconds=5), pd.Timedelta(minutes=15)
HTF_CLEAR, HTF_VETO, HTF_NOT_EVALUATED = "CLEAR", "VETO", "NOT_EVALUATED"

# Decision fields: fully determined by data known at `timestamp` (causality tests compare these).
DECISION_FIELDS = ["signal_id", "candle_open_utc", "timestamp", "direction", "event", "rules_failed",
                   "entry_trigger_time", "entry_reference_price", "target_price", "stop_extension_extreme",
                   "stop_buffer_price", "extension_high", "extension_low", "range_high", "range_low", "condition",
                   "c_med", "n_legs", "cond_direction", "oe_duration_min", "oe_size", "prior_played_out_60m",
                   "htf_state", "sweep_bar_extreme", "sweep_beyond_oe_extreme"]


@dataclass(frozen=True)
class Cbr15Result:
    candidates: pd.DataFrame        # one row per candidate (ARMED or REJECTED), every rule outcome
    candles: pd.DataFrame           # one row per evaluated 15m candle, candle-level rules
    signals: list[dict]             # ARMED candidates in cbr-signal.v1 shape
    spec_hash: str


def _atr_at(series: pd.Series, bar_len: pd.Timedelta, as_of: pd.Timestamp) -> float | None:
    known = series[series.index + bar_len <= as_of].dropna()
    return float(known.iloc[-1]) if len(known) else None


def _minutes_complete(index: pd.DatetimeIndex, start: pd.Timestamp, end: pd.Timestamp) -> tuple[bool, int]:
    """All expected-open minutes in [start, end) have a STRUCTURE 1m bar."""
    if end <= start:
        return True, 0
    mins = pd.date_range(start, end, freq="1min", inclusive="left")
    expected = mins[~expected_closed_mask(mins)]
    missing = expected.difference(index)
    return len(missing) == 0, len(missing)


def _er(price: float, leg: pd.Series) -> float | None:
    return abs(price - leg["p_end"]) / leg["size"] if leg["size"] else None


def run_cbr15(s1m: pd.DataFrame, s5s: pd.DataFrame, *, start: pd.Timestamp, end: pd.Timestamp,
              variant: str = "base", params: Cbr15Params | None = None,
              htf: Callable[[pd.Timestamp, str], str] | None = None,
              dxy_context: pd.DataFrame | None = None) -> Cbr15Result:
    """Evaluate 15m candles opening in [start, end). Bars before `start` serve as warm-up (ATR, swings, prior setups).

    htf(as_of, direction) → CLEAR / VETO / NOT_EVALUATED implements M15-HTF-01; it needs the Phase 12 CBR1H engine
    (OQ-34), so the default is NOT_EVALUATED. dxy_context: Phase 10 causal context indexed by decision time
    (diagnostic only; CBR15 V1 excludes DXY rules)."""
    require_structure(s1m)
    require_structure(s5s)
    p = params or load_cbr15(variant)
    htf = htf or (lambda _t, _d: HTF_NOT_EVALUATED)

    atr1m = atr(s1m, p.atr_length)
    sw_ltf = zigzag(s1m, atr1m, p.k_ltf, M1)
    sw_s5 = zigzag(s5s, atr(s5s, p.atr_length), p.k_s5, S5)
    arms = track_type3(s5s, sw_s5, max_reversal=p.max_reversal_s5, tick=p.tick, latest_pair_only=True)
    b15 = rollup_structure(s1m, "15min")
    atr15 = atr(b15, p.atr_length)
    levels = pd.concat([candle_close_levels(rollup_structure(s1m, f), pd.Timedelta(f)) for f in ("30min", "1h")],
                       ignore_index=True) if p.aoi_required else None
    shash = spec_hash()

    candle_times = pd.date_range(start, end, freq="15min", inclusive="left")
    first_q = (candle_times[0] - p.prior_soft_lookback) if len(candle_times) else start
    all_q = pd.date_range(max(first_q.floor("15min"), s1m.index[0].floor("15min")), end, freq="15min",
                          inclusive="left")
    by_q: dict[pd.Timestamp, list[Type3Arm]] = {}
    for a in arms:
        by_q.setdefault(a.sweep_time.floor("15min"), []).append(a)

    candle_rows, cand_rows = [], []
    for q0 in all_q:
        mins = pd.date_range(q0, q0 + M15, freq="1min", inclusive="left")
        if expected_closed_mask(mins).all():
            continue
        crow, cands = _evaluate_candle(q0, s1m, s5s, atr1m, sw_ltf, b15, atr15, levels, by_q.get(q0, []), p, htf)
        candle_rows.append(crow)
        cand_rows += cands

    cand = pd.DataFrame(cand_rows)
    if len(cand):
        _resolve_raw_outcomes(cand, s5s, p)
        _apply_prior_rule(cand, p)
        cand = cand[cand["candle_open_utc"] >= start].reset_index(drop=True)
    candles = pd.DataFrame(candle_rows)
    if len(candles):
        candles = candles[candles["candle_open_utc"] >= start].reset_index(drop=True)
    signals = [_signal(r, p, shash, dxy_context) for _, r in cand.iterrows() if r["event"] == "ARMED"] if len(cand) else []
    if len(cand):
        cand["spec_hash"] = shash
    return Cbr15Result(cand, candles, signals, shash)


def _evaluate_candle(q0, s1m, s5s, atr1m, sw_ltf, b15, atr15, levels, arms, p: Cbr15Params, htf):
    q_end = q0 + M15
    q_bar = s1m.loc[q0] if q0 in s1m.index else None
    q_open = float(q_bar["open"]) if q_bar is not None else None
    prev = b15.loc[q0 - M15] if (q0 - M15) in b15.index else None
    prev_complete, prev_missing = _minutes_complete(s1m.index, q0 - M15, q0)
    cond = cond_mod.classify(sw_ltf, s1m, q0, p.window, min_legs=p.min_legs, range_min=p.range_min,
                             trend_max=p.trend_max, correction_cap=p.correction_cap, aggregate=p.aggregate)
    candle_rules = {
        "M15-COND-01": cond.condition in (cond_mod.RANGE, cond_mod.TRENDING_RANGE),
        "M15-COND-02": p.min_legs <= cond.n_legs <= p.max_legs,
        "M15-COND-04": cond.n_legs + 1 >= p.min_leg_index,
        "NT_INCOMPLETE_Q_OPEN": q_open is not None,
        "NT_INCOMPLETE_PREV_15M": prev is not None and prev_complete,
    }
    cond_reason = None
    if not candle_rules["M15-COND-02"]:
        cond_reason = "RANGE_TOO_BIG" if cond.n_legs < p.min_legs else "LOWER_TF_RANGE"
    crow = {"candle_open_utc": q0, "condition": cond.condition, "c_med": cond.c_med, "n_legs": cond.n_legs,
            "cond_direction": cond.direction, "range_high": cond.range_high, "range_low": cond.range_low,
            "q_open": q_open, "prev_missing_minutes": prev_missing, "cond_02_reason": cond_reason,
            "candidates": 0, "rules_failed": [k for k, v in candle_rules.items() if not v]}
    rows = []
    for a in arms:
        if q_open is None:
            continue
        as_of = a.sweep_time + S5
        a1 = _atr_at(atr1m, M1, as_of)
        oe = oe_mod.evaluate(s1m, q0, q_open, as_of, atr_1m=a1 or 0.0, activation_atr=p.activation_atr,
                             pullback_frac=p.pullback_frac, two_sided_frac=p.two_sided_frac,
                             prev_candle_high=None if prev is None else float(prev["high"]),
                             prev_candle_low=None if prev is None else float(prev["low"]))
        if oe.direction == "NONE":
            continue
        d = "SELL" if oe.direction == "UP" else "BUY"
        if a.direction != d:
            continue                                   # not a candidate: shift in the extension's direction
        crow["candidates"] += 1
        rows.append(_evaluate_candidate(q0, q_end, q_open, cond, candle_rules, oe, a, as_of, a1, d, s1m, atr1m,
                                        sw_ltf, atr15, levels, p, htf))
    return crow, rows


def _evaluate_candidate(q0, q_end, q_open, cond, candle_rules, oe, a: Type3Arm, as_of, a1, d, s1m, atr1m, sw_ltf,
                        atr15, levels, p: Cbr15Params, htf) -> dict:
    rules: dict[str, bool | None] = dict(candle_rules)
    rules["M15-COND-03"] = None                                     # set after raw setups are resolved
    rules["M15-T3-01"] = a.sweep_time >= oe.extreme_time             # §7: sweep at/after oe_extreme_time
    rules["M15-OE-01"] = oe.duration_min >= p.oe_min_minutes
    rules["M15-OE-02"] = oe.no_pullback
    a15 = _atr_at(atr15, M15, as_of)
    rules["M15-OE-03a"] = not oe.two_sided
    rules["M15-OE-03b"] = (a15 is not None) and oe.size >= p.oe_min_size_atr * a15
    known = usable(sw_ltf, as_of)
    pos = cond.pos(oe.extreme)
    er_pro = beyond = None
    if cond.condition == cond_mod.RANGE:
        rules["M15-LOC-01"] = pos is not None and (pos >= p.range_extreme if d == "SELL" else pos <= 1 - p.range_extreme)
    elif cond.condition == cond_mod.TRENDING_RANGE:
        if cond.direction == "NONE":
            rules["M15-LOC-TR-NODIR"] = False                         # OQ-37
        elif (d == "SELL") == (cond.direction == "UP"):             # counter-trend
            kind = "H" if d == "SELL" else "L"
            last = known[known["kind"] == kind]
            beyond = bool(len(last)) and ((oe.extreme > last["price"].iloc[-1]) if d == "SELL"
                                          else (oe.extreme < last["price"].iloc[-1]))
            rules["M15-LOC-02"] = beyond
        else:                                                         # pro-trend
            lg = legs(known)
            want = 1 if cond.direction == "UP" else -1
            lg = lg[lg["dir"] == want]
            er_pro = _er(oe.extreme, lg.iloc[-1]) if len(lg) else None
            rules["M15-LOC-03"] = er_pro is not None and p.pro_er_min <= er_pro <= p.pro_er_max
    rules["M15-LOC-04"] = bool(oe.prev_candle_break)
    assert (oe.extreme > q_open) if d == "SELL" else (oe.extreme < q_open), "M15-LOC-05 invariant"
    if p.aoi_required:
        rules["M15-LOC-06"] = aoi_tap(levels, oe.extreme, q0, zone=p.aoi_zone_atr * (a1 or 0.0), lookback=p.aoi_lookback)

    target = oe.extreme - 0.5 * (oe.extreme - q_open)
    window_start = q0 + pd.Timedelta(minutes=p.start_mic)
    active_from = max(as_of, window_start)
    # decision rules (known at as_of)
    rules["M15-TIME-01"] = active_from < q_end                         # fill window 7.5 <= mic < 15 still open
    htf_state = htf(as_of, d)
    rules["M15-HTF-01"] = None if htf_state == HTF_NOT_EVALUATED else htf_state == HTF_CLEAR
    rules["NT_SYDNEY"] = not (in_sydney_session(active_from) or in_sydney_session(q_end - S5))
    rules["NT_ROLLOVER"] = not any(in_rollover(t, pre_min=p.rollover_pre_min, post_min=p.rollover_post_min)
                                   for t in (active_from, q_end - S5))
    q_complete, q_missing = _minutes_complete(s1m.index, q0, as_of.floor("1min"))
    rules["NT_INCOMPLETE_Q"] = q_complete
    rules["IMPL-REWARD"] = (a.trigger_price > target) if d == "SELL" else (a.trigger_price < target)

    # lifecycle after the decision (not decision inputs): order ends at the first of these
    cancel_time, cancel_reason = q_end, "WINDOW_END"
    touch_time = a.end_time if a.end == "BREAK" else None
    if touch_time is not None and touch_time < window_start:
        cancel_time, cancel_reason = touch_time, "T3_BREAK_BEFORE_WINDOW"          # OQ-38
    if a.end in ("TIMEOUT", "NEW_SWING") and a.end_time is not None and a.end_time < cancel_time:
        cancel_time, cancel_reason = a.end_time, f"T3_{a.end}"
    horizon = min(cancel_time, touch_time) if touch_time is not None else cancel_time
    for t in pd.date_range(as_of.floor("1min") + M1, horizon, freq="1min", inclusive="both"):
        later = oe_mod.evaluate(s1m, q0, q_open, t, atr_1m=_atr_at(atr1m, M1, t) or 0.0,
                                activation_atr=p.activation_atr, pullback_frac=p.pullback_frac,
                                two_sided_frac=p.two_sided_frac)
        if later.direction != oe.direction or not later.no_pullback:
            if t < cancel_time:
                cancel_time, cancel_reason = t, "OE_PULLBACK"
            break

    buffer_price = p.buffer_atr * (a1 or 0.0)
    hv = hvcs(s1m[s1m.index + M1 <= as_of], (as_of - M1).floor("1min"), oe.direction, atr_1m=a1,
              min_minutes=p.hvcs_min_minutes, max_violations=p.hvcs_max_violations,
              lvcs_body_atr=p.hvcs_lvcs_body_atr) if a1 else None
    return {
        "candle_open_utc": q0, "timestamp": as_of, "direction": d, "variant": p.variant,
        "rules": rules, "q_open": q_open, "condition": cond.condition, "c_med": cond.c_med, "n_legs": cond.n_legs,
        "cond_direction": cond.direction, "range_high": cond.range_high, "range_low": cond.range_low,
        "pos_oe_extreme": pos, "er_pro": er_pro, "beyond_ltf_swing": beyond,
        "oe_dir": oe.direction, "oe_extreme": oe.extreme, "oe_extreme_time": oe.extreme_time, "oe_size": oe.size,
        "oe_size_atr15": (oe.size / a15) if a15 else None, "oe_duration_min": oe.duration_min,
        "oe_no_pullback": oe.no_pullback, "oe_two_sided": oe.two_sided, "oe_opposite_wick": oe.opposite_wick,
        "oe_prev_candle_break": oe.prev_candle_break, "atr_1m": a1, "atr_15m": a15,
        "t3_swept_price": a.swept_price, "t3_broken_price": a.broken_price, "t3_sweep_time": a.sweep_time,
        "t3_end": a.end, "t3_pair_was_latest": a.pair_was_latest, "sweep_bar_extreme": a.sweep_bar_extreme,
        "sweep_beyond_oe_extreme": (a.sweep_bar_extreme > oe.extreme) if d == "SELL" else (a.sweep_bar_extreme < oe.extreme),
        "entry_reference_price": a.trigger_price, "entry_trigger_time": active_from, "entry_expiry_time": q_end,
        "target_price": target, "stop_extension_extreme": oe.extreme, "stop_buffer_price": buffer_price,
        "extension_high": max(oe.extreme, q_open), "extension_low": min(oe.extreme, q_open),
        "cancel_time": cancel_time, "cancel_reason": cancel_reason, "structure_trigger_touch_time": touch_time,
        "t3_extreme_before_end": a.extreme_before_end,                # lifecycle: sweep extreme up to the break (OQ-35)
        "htf_state": htf_state, "q_missing_minutes": q_missing,
        "hvcs_minutes": hv.minutes if hv else None, "hvcs_body_atr": hv.body_atr if hv else None,
        "mic_structure_touch": ((touch_time - q0) / M1) if touch_time is not None else None,
        "s5_break_size_atr1m": (abs(a.broken_price - a.trigger_price) / a1) if a1 else None,
    }


def _resolve_raw_outcomes(cand: pd.DataFrame, s5s: pd.DataFrame, p: Cbr15Params) -> None:
    """Raw setups (every rule true except COND-03; HTF true or not evaluated) resolved on STRUCTURE 5s bars."""
    outcome, resolved = [], []
    for _, r in cand.iterrows():
        rules = {k: v for k, v in r["rules"].items() if k not in ("M15-COND-03", "M15-HTF-01")}
        raw = all(v is True for v in rules.values()) and r["rules"].get("M15-HTF-01") is not False
        if not raw:
            outcome.append(None)
            resolved.append(pd.NaT)
            continue
        o, t = _structure_outcome(r, s5s, p)
        outcome.append(o)
        resolved.append(t)
    cand["raw_setup"] = [o is not None for o in outcome]
    cand["raw_outcome"] = outcome
    cand["raw_resolved_utc"] = pd.to_datetime(pd.Series(resolved, index=cand.index, dtype="object"), utc=True)


def _structure_outcome(r, s5s: pd.DataFrame, p: Cbr15Params) -> tuple[str, pd.Timestamp | None]:
    sell = r["direction"] == "SELL"
    win = s5s[(s5s.index >= r["entry_trigger_time"]) & (s5s.index < r["cancel_time"])]
    hit = win.index[(win["low"] <= r["entry_reference_price"]) if sell else (win["high"] >= r["entry_reference_price"])]
    if not len(hit):
        return "NO_TOUCH", r["cancel_time"]
    stop = r["stop_extension_extreme"] + (r["stop_buffer_price"] if sell else -r["stop_buffer_price"])
    after = s5s[s5s.index >= hit[0]]
    for t, row in after.iterrows():
        ny_flat = in_rollover(t, pre_min=p.rollover_flat_before_min, post_min=0)
        if (row["high"] >= stop) if sell else (row["low"] <= stop):
            return "STOP", t + S5
        if (row["low"] <= r["target_price"]) if sell else (row["high"] >= r["target_price"]):
            return "TARGET", t + S5
        if ny_flat:
            return "FORCED_FLAT", t + S5
    return "UNRESOLVED", None


def _apply_prior_rule(cand: pd.DataFrame, p: Cbr15Params) -> None:
    """M15-COND-03: ≥ 1 raw setup with signal time in [Q.t0 − 60 min, Q.t0) that reached TARGET before Q.t0."""
    raw = cand[cand["raw_setup"] & (cand["raw_outcome"] == "TARGET")]
    hard, soft, events, failed = [], [], [], []
    def count(q0: pd.Timestamp, lookback: pd.Timedelta) -> int:
        return int(((raw["timestamp"] >= q0 - lookback) & (raw["timestamp"] < q0) & (raw["raw_resolved_utc"] <= q0)).sum())

    for _, r in cand.iterrows():
        q0 = r["candle_open_utc"]
        h = count(q0, p.prior_hard_lookback)
        hard.append(h)
        soft.append(count(q0, p.prior_soft_lookback))
        rules = dict(r["rules"])
        rules["M15-COND-03"] = h >= p.prior_hard_min
        r["rules"].update(rules)
        bad = sorted(k for k, v in rules.items() if v is False)
        failed.append(bad)
        events.append("ARMED" if not bad else "REJECTED")
    cand["prior_played_out_60m"] = hard
    cand["prior_played_out_120m"] = soft
    cand["rules_failed"] = failed
    cand["rules_not_evaluated"] = [sorted(k for k, v in r.items() if v is None) for r in cand["rules"]]
    cand["event"] = events
    seq = cand.groupby(["candle_open_utc", "direction"]).cumcount()
    cand["signal_id"] = [f"CBR15_BASELINE_V1/{r['variant']}/{r['candle_open_utc']:%Y%m%dT%H%M}/{r['direction']}/{s}"
                         for (_, r), s in zip(cand.iterrows(), seq, strict=True)]


def _signal(r: pd.Series, p: Cbr15Params, shash: str, dxy: pd.DataFrame | None) -> dict:
    long = r["direction"] == "BUY"
    dxy_state = {"availability": "MISSING", "direction_15m": None, "direction_1h": None, "reason_codes": ["NOT_PROVIDED"]}
    if dxy is not None:
        known = dxy[dxy.index <= r["timestamp"]]
        if len(known):
            row = known.iloc[-1]
            ok = bool(row["dxy_available"])
            dxy_state = {"availability": "AVAILABLE" if ok else "MISSING",
                         "direction_15m": row["dxy_15m_last_direction"] if isinstance(row["dxy_15m_last_direction"], str) else None,
                         "direction_1h": row["dxy_1h_last_direction"] if isinstance(row["dxy_1h_last_direction"], str) else None,
                         "reason_codes": [c for c in str(row["dxy_reason_codes"]).split(";") if c and c != "nan"]}
    reasons = ["HTF_NOT_EVALUATED"] if r["htf_state"] == HTF_NOT_EVALUATED else []
    return {
        "signal_id": r["signal_id"], "model": p.model, "variant": p.variant, "price_role": "STRUCTURE",
        "timestamp": r["timestamp"].isoformat(), "direction": "LONG" if long else "SHORT",
        "entry_trigger_time": r["entry_trigger_time"].isoformat(), "entry_expiry_time": r["entry_expiry_time"].isoformat(),
        "entry_order_type": "STOP", "entry_reference_price": r["entry_reference_price"],
        "stop_rule": {"extension_extreme": r["stop_extension_extreme"], "extension_extreme_source": "TICK_MID",
                      "direction": "LONG" if long else "SHORT",
                      "buffer": {"param": "stop.buffer_atr", "value": p.buffer_atr, "unit": "ATR(1m,14)",
                                 "atr_at_decision": r["atr_1m"], "label": "ASSUMPTION", "source": ["OQ-11"]},
                      "spread_policy": "ADD_SPREAD_AT_FILL",
                      "execution_inputs": {"spread_at_decision": None, "spread_source": None}},
        "stop_price": r["stop_extension_extreme"] + (-r["stop_buffer_price"] if long else r["stop_buffer_price"]),
        "target_price": r["target_price"], "extension_high": r["extension_high"], "extension_low": r["extension_low"],
        "extremes_source": "TICK_MID", "range_high": r["range_high"], "range_low": r["range_low"],
        "context_state": {"condition": r["condition"], "c_med": r["c_med"], "n_legs": r["n_legs"],
                          "cond_direction": r["cond_direction"], "pos_oe_extreme": r["pos_oe_extreme"],
                          "er_pro": r["er_pro"], "oe_duration_min": r["oe_duration_min"], "oe_size": r["oe_size"],
                          "prior_played_out_60m": int(r["prior_played_out_60m"]),
                          "prior_played_out_120m": int(r["prior_played_out_120m"])},
        "dxy_state": dxy_state,
        "session_state": {"nt_sydney": False, "nt_rollover": False},
        "source_feed": {"feed_id": "dukascopy_ticks:xauusd", "manifest_hash": None},
        "data_confidence": {"level": "REDUCED" if reasons else "FULL", "reason_codes": reasons},
        "reason_code": "ARMED", "spec_hash": shash,
        "lifecycle": {"cancel_time": r["cancel_time"].isoformat(), "cancel_reason": r["cancel_reason"],
                      "structure_trigger_touch_time": None if pd.isna(r["structure_trigger_touch_time"])
                      else r["structure_trigger_touch_time"].isoformat()},
        "diagnostics": {"sweep_bar_extreme": r["sweep_bar_extreme"], "sweep_beyond_oe_extreme": bool(r["sweep_beyond_oe_extreme"]),
                        "hvcs_minutes": r["hvcs_minutes"], "oe_opposite_wick": r["oe_opposite_wick"],
                        "mic_structure_touch": r["mic_structure_touch"], "t3_end": r["t3_end"]},
    }


def decision_frame(result: Cbr15Result) -> pd.DataFrame:
    c = result.candidates
    if not len(c):
        return pd.DataFrame(columns=DECISION_FIELDS)
    out = c[DECISION_FIELDS].copy()
    out["rules_failed"] = out["rules_failed"].map(lambda x: ",".join(x))
    return out


def result_hash(result: Cbr15Result) -> str:
    payload = json.dumps({"candidates": decision_frame(result).astype(str).to_dict("records"),
                          "signals": result.signals}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


