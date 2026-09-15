"""OQ-25 evidence study: candle-file vs tick-derived price extremes (D14-3, D15-4).

Usage:
    .venv/bin/python -m cbr.data.oq25_extrema_study

Data fidelity only. No entries, trades, P&L or signal statistics. Compares per-minute highs/lows and five structure
consequences (swing points, range boundaries, sweeps/takes, extension extremes, stop-level touches) between:
    candle_mid  Dukascopy candle file, mid = mean of per-side extremes (SIDE_EXTREME_MEAN)
    candle_bid / candle_ask   Dukascopy candle file, one side
    tick_mid    tick-derived mid OHLC (TICK_MID)
    tick_bid / tick_ask       tick-derived one-side OHLC
    gc          Databento GC front month 1m (timing comparisons only; basis differs)
Structure parameters are the frozen V1 config values (swing k = 3.0 on ATR(1m,14), stop buffer 0.1 ATR); no parameter
is varied. Holdout-period fixture days are used for data fidelity only (logged).
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import yaml

from cbr.data import dukascopy_fetch as dk
from cbr.data.futures import load_front
from cbr.structure.indicators import atr
from cbr.structure.swings import zigzag

ROOT = dk.ROOT
REPORT_JSON = ROOT / "reports" / "oq25-extrema-evidence.json"
REPORT_MD = ROOT / "reports" / "oq25-extrema-evidence.md"
MIN = pd.Timedelta(minutes=1)
FULL_DAYS_FIXTURE = [date(2025, 10, 21), date(2025, 10, 22), date(2025, 10, 23), date(2025, 10, 24), date(2025, 11, 10)]
TOL = {"xauusd": 0.05, "dollaridxusd": 0.005}
TICK = {"xauusd": 0.01, "dollaridxusd": 0.001}
SWING_MATCH_BARS = 2
STOP_LOOKAHEAD_BARS = 30
RANGE_HOURS = 5
STOP_ARTIFACT = "artificial extremes only: candle_mid vs tick_mid (structure and touches on the same series)"
STOP_SIDE = "execution side only: tick_mid structure, bid/ask touches vs mid touches"
STOP_ONE_STREAM = "one stream vs two concepts: candle_mid for everything vs tick_mid structure + bid/ask touches"
STOP_EXEC_SOURCE = "execution source: tick bid/ask vs candle-file bid/ask touches (same tick_mid structure)"
SERIES = ["candle_mid", "tick_mid", "tick_bid", "tick_ask", "candle_bid", "candle_ask"]


def _cfg() -> dict:
    s = yaml.safe_load((ROOT / "config" / "strategy.yaml").read_text())
    root = s.get("primitives", s)
    return {"k": root["swing"]["LTF"]["k"]["value"], "atr_len": root["atr_length"]["value"],
            "buffer_atr": root["stop"]["buffer_atr"]["value"]}


def _side_bars(ticks: pd.DataFrame, side: str, freq: str = "1min") -> pd.DataFrame:
    s = ticks.set_index("ts")[side]
    b = s.resample(freq, label="left", closed="left").ohlc()
    return b.dropna()


def _series(ticks: pd.DataFrame, candles: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tm = dk._bars(ticks, "1min")[["open", "high", "low", "close"]]
    out = {"tick_mid": tm, "tick_bid": _side_bars(ticks, "bid"), "tick_ask": _side_bars(ticks, "ask"),
           "candle_mid": candles[["open", "high", "low", "close"]],
           "candle_bid": candles[["bid_open", "bid_high", "bid_low", "bid_close"]].set_axis(
               ["open", "high", "low", "close"], axis=1),
           "candle_ask": candles[["ask_open", "ask_high", "ask_low", "ask_close"]].set_axis(
               ["open", "high", "low", "close"], axis=1)}
    common = tm.index
    for v in out.values():
        common = common.intersection(v.index)
    return {k: v.loc[common] for k, v in out.items()}


def _q(x: pd.Series) -> dict:
    x = x.abs()
    return {"p50": round(float(x.quantile(.5)), 4), "p90": round(float(x.quantile(.9)), 4),
            "p99": round(float(x.quantile(.99)), 4), "max": round(float(x.max()), 4)}


def minute_diffs(ser: dict, inst: str) -> dict:
    tol = TOL[inst]
    pairs = [("candle_mid", "tick_mid"), ("candle_bid", "tick_bid"), ("candle_ask", "tick_ask"),
             ("tick_bid", "tick_mid"), ("tick_ask", "tick_mid")]
    out = {}
    for a, b in pairs:
        dh, dl = ser[a]["high"] - ser[b]["high"], ser[a]["low"] - ser[b]["low"]
        out[f"{a}-{b}"] = {"minutes": len(dh), "high_mismatch_share": round(float((dh.abs() > tol).mean()), 4),
                           "low_mismatch_share": round(float((dl.abs() > tol).mean()), 4),
                           "high_abs": _q(dh), "low_abs": _q(dl),
                           "high_mean_signed": round(float(dh.mean()), 4), "low_mean_signed": round(float(dl.mean()), 4)}
    return out


def _swings(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    return zigzag(bars, atr(bars, cfg["atr_len"]), cfg["k"], MIN)


def swing_compare(ref: pd.DataFrame, other: pd.DataFrame, cfg: dict, tol: float) -> dict:
    a, b = _swings(ref, cfg), _swings(other, cfg)
    matched, same_time, price_diff, confirm_shift = 0, 0, [], []
    used = set()
    for _, s in a.iterrows():
        cand = b[(b["kind"] == s["kind"]) & ((b["time"] - s["time"]).abs() <= SWING_MATCH_BARS * MIN)]
        cand = cand[~cand.index.isin(used)]
        if len(cand):
            j = (cand["time"] - s["time"]).abs().idxmin()
            used.add(j)
            matched += 1
            same_time += int(b.loc[j, "time"] == s["time"])
            price_diff.append(abs(b.loc[j, "price"] - s["price"]))
            confirm_shift.append((b.loc[j, "confirmed_at"] - s["confirmed_at"]) / MIN)
    pd_ = pd.Series(price_diff, dtype=float)
    return {"ref_swings": len(a), "other_swings": len(b), "matched": matched,
            "unmatched_ref": len(a) - matched, "unmatched_other": len(b) - matched,
            "same_extreme_minute": same_time, "price_diff_gt_tol": int((pd_ > tol).sum()),
            "price_abs": _q(pd_) if len(pd_) else None,
            "confirm_shift_min_nonzero": int(sum(1 for x in confirm_shift if x != 0))}


def range_compare(ref: pd.DataFrame, other: pd.DataFrame, tol: float) -> dict:
    n = level = argt = 0
    for t in ref.index[ref.index.minute == 0]:
        lo = t - pd.Timedelta(hours=RANGE_HOURS)
        if lo < ref.index[0]:
            continue
        r, o = ref[(ref.index >= lo) & (ref.index < t)], other[(other.index >= lo) & (other.index < t)]
        if len(r) < 60:
            continue
        n += 2
        level += int(abs(r["high"].max() - o["high"].max()) > tol) + int(abs(r["low"].min() - o["low"].min()) > tol)
        argt += int(r["high"].idxmax() != o["high"].idxmax()) + int(r["low"].idxmin() != o["low"].idxmin())
    return {"boundaries": n, "level_diff_gt_tol": level, "extreme_minute_differs": argt}


def _candles(bars: pd.DataFrame, freq: str) -> pd.DataFrame:
    g = bars.resample(freq, label="left", closed="left")
    c = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                      "t_high": g["high"].apply(lambda s: s.idxmax() if len(s) else pd.NaT),
                      "t_low": g["low"].apply(lambda s: s.idxmin() if len(s) else pd.NaT)}).dropna(subset=["open"])
    return c


def takes_compare(ref: pd.DataFrame, other: pd.DataFrame, tick: float) -> dict:
    out = {}
    for freq in ("15min", "1h"):
        a, b = _candles(ref, freq), _candles(other, freq)
        idx = a.index.intersection(b.index)
        a, b = a.loc[idx], b.loc[idx]
        ta_h = a["high"] >= a["high"].shift() + tick
        tb_h = b["high"] >= b["high"].shift() + tick
        ta_l = a["low"] <= a["low"].shift() - tick
        tb_l = b["low"] <= b["low"].shift() - tick
        valid = a["high"].shift().notna()
        out[freq] = {"candles": int(valid.sum()),
                     "take_high_disagree": int((ta_h != tb_h)[valid].sum()),
                     "take_low_disagree": int((ta_l != tb_l)[valid].sum()),
                     "takes_ref": int((ta_h | ta_l)[valid].sum())}
    return out


def swing_sweeps_compare(ref: pd.DataFrame, other: pd.DataFrame, cfg: dict, tick: float) -> dict:
    """Minutes whose high (low) exceeds the latest usable swing high (low) of the same series."""
    def events(bars):
        sw = _swings(bars, cfg)
        ev = set()
        for t, row in bars.iterrows():
            usable = sw[sw["confirmed_at"] <= t]
            if not len(usable):
                continue
            h, lo = usable[usable["kind"] == "H"], usable[usable["kind"] == "L"]
            if len(h) and row["high"] >= h["price"].iloc[-1] + tick and h["time"].iloc[-1] < t:
                ev.add(("H", h["time"].iloc[-1]))
            if len(lo) and row["low"] <= lo["price"].iloc[-1] - tick and lo["time"].iloc[-1] < t:
                ev.add(("L", lo["time"].iloc[-1]))
        return ev
    a, b = events(ref), events(other)
    return {"swept_swings_ref": len(a), "swept_swings_other": len(b), "only_ref": len(a - b), "only_other": len(b - a)}


def extension_compare(ref: pd.DataFrame, other: pd.DataFrame, tol: float) -> dict:
    out = {}
    for freq in ("15min", "1h"):
        a, b = _candles(ref, freq), _candles(other, freq)
        idx = a.index.intersection(b.index)
        a, b = a.loc[idx], b.loc[idx]
        dir_a = np.where(a["high"] - a["open"] >= a["open"] - a["low"], "UP", "DOWN")
        dir_b = np.where(b["high"] - b["open"] >= b["open"] - b["low"], "UP", "DOWN")
        ext_a = np.where(dir_a == "UP", a["high"], a["low"])
        ext_b = np.where(dir_b == "UP", b["high"], b["low"])
        t_a = np.where(dir_a == "UP", a["t_high"], a["t_low"])
        t_b = np.where(dir_b == "UP", b["t_high"], b["t_low"])
        same = dir_a == dir_b
        out[freq] = {"candles": len(idx), "direction_disagree": int((~same).sum()),
                     "extreme_diff_gt_tol": int((np.abs(ext_a - ext_b)[same] > tol).sum()),
                     "extreme_minute_differs": int((t_a != t_b)[same].sum()),
                     "extreme_abs": _q(pd.Series(np.abs(ext_a - ext_b)[same]))}
    return out


def stop_compare(a: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame], b: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
                 cfg: dict) -> dict:
    """Each side is (structure bars, bars tested for stops ABOVE the extreme, bars tested for stops BELOW it).
    Stop levels sit beyond each closed 15m candle's high (+ buffer) and low (- buffer), buffer = 0.1 ATR(1m,14) of the
    structure series. Counts levels where A and B disagree on whether the stop is touched within the next 30 minutes.
    Stops above are touched by highs (a short's stop: ask side); stops below by lows (a long's stop: bid side). No trades."""
    (sa, up_a, dn_a), (sb, up_b, dn_b) = a, b
    a15, b15 = _candles(sa, "15min"), _candles(sb, "15min")
    at_a, at_b = atr(sa, cfg["atr_len"]), atr(sb, cfg["atr_len"])
    n = dis = 0
    for t in a15.index.intersection(b15.index):
        close = t + pd.Timedelta(minutes=15)
        ia, ib = at_a[at_a.index < close], at_b[at_b.index < close]
        if not len(ia) or np.isnan(ia.iloc[-1]) or not len(ib) or np.isnan(ib.iloc[-1]):
            continue
        end = close + STOP_LOOKAHEAD_BARS * MIN
        win = [x[(x.index >= close) & (x.index < end)] for x in (up_a, dn_a, up_b, dn_b)]
        if any(not len(w) for w in win):
            continue
        stop_up_a = a15.loc[t, "high"] + cfg["buffer_atr"] * ia.iloc[-1]
        stop_up_b = b15.loc[t, "high"] + cfg["buffer_atr"] * ib.iloc[-1]
        stop_dn_a = a15.loc[t, "low"] - cfg["buffer_atr"] * ia.iloc[-1]
        stop_dn_b = b15.loc[t, "low"] - cfg["buffer_atr"] * ib.iloc[-1]
        dis += int(bool((win[0]["high"] >= stop_up_a).any()) != bool((win[2]["high"] >= stop_up_b).any()))
        dis += int(bool((win[1]["low"] <= stop_dn_a).any()) != bool((win[3]["low"] <= stop_dn_b).any()))
        n += 2
    return {"stop_levels": n, "touch_disagree": dis}


def gc_compare(tick_mid: pd.DataFrame, gc: pd.DataFrame, cfg: dict) -> dict:
    g = gc[["open", "high", "low", "close"]]
    idx = tick_mid.index.intersection(g.index)
    if len(idx) < 120:
        return {"available": False}
    sw_s, sw_g = _swings(tick_mid.loc[idx], cfg), _swings(g.loc[idx], cfg)
    matched = 0
    for _, s in sw_s.iterrows():
        matched += int(((sw_g["kind"] == s["kind"]) & ((sw_g["time"] - s["time"]).abs() <= SWING_MATCH_BARS * MIN)).any())
    ex = extension_compare(tick_mid.loc[idx], g.loc[idx], tol=np.inf)
    return {"available": True, "minutes": len(idx), "spot_swings": len(sw_s), "gc_swings": len(sw_g),
            "spot_swings_matched_in_gc": matched,
            "ext_1h_direction_disagree": ex["1h"]["direction_disagree"],
            "ext_1h_extreme_minute_differs": ex["1h"]["extreme_minute_differs"], "ext_1h_candles": ex["1h"]["candles"],
            "ext_15m_direction_disagree": ex["15min"]["direction_disagree"],
            "ext_15m_extreme_minute_differs": ex["15min"]["extreme_minute_differs"],
            "ext_15m_candles": ex["15min"]["candles"],
            "iid_changes": int(gc.loc[idx, "instrument_id"].ne(gc.loc[idx, "instrument_id"].shift()).sum() - 1)}


def study_frame(inst: str, label: str, ticks: pd.DataFrame, candles: pd.DataFrame, gc: pd.DataFrame | None,
                cfg: dict, full: bool) -> dict:
    ser = _series(ticks, candles)
    tol, tick = TOL[inst], TICK[inst]
    rec = {"instrument": inst, "label": label, "minutes": len(ser["tick_mid"]), "full_day": full,
           "minute_diffs": minute_diffs(ser, inst),
           "extension": {p: extension_compare(ser["tick_mid"], ser[p], tol) for p in ("candle_mid", "tick_bid", "tick_ask")},
           "takes": {p: takes_compare(ser["tick_mid"], ser[p], tick) for p in ("candle_mid", "tick_bid", "tick_ask")}}
    if full:
        rec["swings"] = {p: swing_compare(ser["tick_mid"], ser[p], cfg, tol) for p in ("candle_mid", "tick_bid", "tick_ask")}
        rec["ranges"] = {p: range_compare(ser["tick_mid"], ser[p], tol) for p in ("candle_mid", "tick_bid", "tick_ask")}
        rec["swing_sweeps"] = {p: swing_sweeps_compare(ser["tick_mid"], ser[p], cfg, tick) for p in ("candle_mid", "tick_bid")}
        mid_all = (ser["tick_mid"], ser["tick_mid"], ser["tick_mid"])
        proper = (ser["tick_mid"], ser["tick_ask"], ser["tick_bid"])                           # structure tick_mid; short stops on ask, long stops on bid
        rec["stops"] = {
            STOP_ARTIFACT: stop_compare(mid_all, (ser["candle_mid"], ser["candle_mid"], ser["candle_mid"]), cfg),
            STOP_SIDE: stop_compare(proper, mid_all, cfg),
            STOP_ONE_STREAM: stop_compare(proper, (ser["candle_mid"], ser["candle_mid"], ser["candle_mid"]), cfg),
            STOP_EXEC_SOURCE: stop_compare(proper, (ser["tick_mid"], ser["candle_ask"], ser["candle_bid"]), cfg)}
        if gc is not None:
            rec["gc"] = gc_compare(ser["tick_mid"], gc, cfg)
    return rec


def evaluate() -> dict:
    cfg = _cfg()
    gc = load_front("gc_front_ohlcv1m")
    frames = []
    days = [(f"fixture {d}", d) for d in FULL_DAYS_FIXTURE] + [(f"{sid} {d}", d) for sid, d in dk.SAMPLE_DAYS.items()]
    for label, d in days:
        tick_path = dk.RAW / "xauusd" / "ticks" / f"{d.isoformat()}.parquet"
        ticks = pd.read_parquet(tick_path) if tick_path.exists() else dk._download_day("xauusd", d)
        if ticks.empty:
            continue
        ticks = ticks.sort_values("ts", kind="stable")
        candles = pd.read_parquet(dk.NORM / "xauusd" / "candles_1m" / f"{d.isoformat()}.parquet")
        start = pd.Timestamp(d, tz="UTC")
        g = gc[(gc.index >= start) & (gc.index < start + pd.Timedelta(days=1))]
        frames.append(study_frame("xauusd", label, ticks, candles, g, cfg, full=True))
        print("done", label, flush=True)
    for inst in ("dollaridxusd",):
        for wid in [*dk.FIXTURE_TICK_WINDOWS, *dk.SAMPLE_TICK_WINDOWS]:
            ticks = pd.read_parquet(dk.RAW / inst / "tick_windows" / f"{wid}.parquet")
            days_ = sorted({ts.date() for ts in ticks["ts"]})
            candles = pd.concat([pd.read_parquet(dk.NORM / inst / "candles_1m" / f"{x.isoformat()}.parquet")
                                 for x in days_ if (dk.NORM / inst / "candles_1m" / f"{x.isoformat()}.parquet").exists()])
            frames.append(study_frame(inst, f"window {wid}", ticks, candles, None, cfg, full=False))
    return {"generated_utc": datetime.now(UTC).isoformat(), "config": cfg, "tolerance": TOL,
            "frames": frames, "totals": totals(frames)}


def totals(frames: list[dict]) -> dict:
    xau = [f for f in frames if f["instrument"] == "xauusd"]
    t: dict = {"xau_days": len(xau), "xau_minutes": sum(f["minutes"] for f in xau)}

    def s(path):
        vals = []
        for f in xau:
            v = f
            for p in path:
                v = v.get(p) if isinstance(v, dict) else None
                if v is None:
                    break
            if v is not None:
                vals.append(v)
        return vals
    for pair in ("candle_mid-tick_mid", "candle_bid-tick_bid", "candle_ask-tick_ask", "tick_bid-tick_mid"):
        rows = s(["minute_diffs", pair])
        mins = sum(r["minutes"] for r in rows)
        t[f"minutes {pair}"] = {
            "high_mismatch_share": round(sum(r["high_mismatch_share"] * r["minutes"] for r in rows) / mins, 4),
            "low_mismatch_share": round(sum(r["low_mismatch_share"] * r["minutes"] for r in rows) / mins, 4),
            "high_abs_max": max(r["high_abs"]["max"] for r in rows), "low_abs_max": max(r["low_abs"]["max"] for r in rows)}
    for p in ("candle_mid", "tick_bid", "tick_ask"):
        sw = s(["swings", p])
        t[f"swings tick_mid vs {p}"] = {k: sum(r[k] for r in sw) for k in
                                        ("ref_swings", "other_swings", "matched", "unmatched_ref", "unmatched_other",
                                         "same_extreme_minute", "price_diff_gt_tol", "confirm_shift_min_nonzero")}
        rg = s(["ranges", p])
        t[f"ranges tick_mid vs {p}"] = {k: sum(r[k] for r in rg) for k in ("boundaries", "level_diff_gt_tol",
                                                                            "extreme_minute_differs")}
        for freq in ("15min", "1h"):
            ex = s(["extension", p, freq])
            t[f"extension {freq} tick_mid vs {p}"] = {k: sum(r[k] for r in ex) for k in
                                                      ("candles", "direction_disagree", "extreme_diff_gt_tol",
                                                       "extreme_minute_differs")}
            tk = s(["takes", p, freq])
            t[f"takes {freq} tick_mid vs {p}"] = {k: sum(r[k] for r in tk) for k in
                                                  ("candles", "take_high_disagree", "take_low_disagree", "takes_ref")}
    for p in ("candle_mid", "tick_bid"):
        sw = s(["swing_sweeps", p])
        t[f"swing sweeps tick_mid vs {p}"] = {k: sum(r[k] for r in sw) for k in
                                              ("swept_swings_ref", "swept_swings_other", "only_ref", "only_other")}
    for name in (STOP_ARTIFACT, STOP_SIDE, STOP_ONE_STREAM, STOP_EXEC_SOURCE):
        st = s(["stops", name])
        t[f"stops: {name}"] = {k: sum(r[k] for r in st) for k in ("stop_levels", "touch_disagree")}
    g = [x for x in s(["gc"]) if x.get("available")]
    t["gc vs tick_mid"] = {k: sum(r[k] for r in g) for k in
                           ("minutes", "spot_swings", "gc_swings", "spot_swings_matched_in_gc", "ext_1h_candles",
                            "ext_1h_direction_disagree", "ext_1h_extreme_minute_differs", "ext_15m_candles",
                            "ext_15m_direction_disagree", "ext_15m_extreme_minute_differs")}
    return t


def render_md(r: dict) -> str:
    lines = ["# OQ-25 Evidence: Candle-File vs Tick-Derived Price Extremes", "",
             (f"Generated {r['generated_utc']} by `src/cbr/data/oq25_extrema_study.py`. Data fidelity only: no "
              "trades, P&L or signal statistics."), "",
             (f"Frozen V1 parameters: swing k = {r['config']['k']} × ATR(1m,{r['config']['atr_len']}), stop buffer "
              f"{r['config']['buffer_atr']} ATR. Mismatch tolerance: {r['tolerance']}."), "",
             "## XAUUSD totals (full days)", ""]
    for k, v in r["totals"].items():
        lines.append(f"- **{k}**: {v}")
    lines += ["", "## Per frame", ""]
    for f in r["frames"]:
        lines.append(f"### {f['instrument']} · {f['label']} ({f['minutes']} min)")
        lines.append("")
        lines.append("| Pair | High mismatch | Low mismatch | High p50/p90/p99/max | Low p50/p90/p99/max |")
        lines.append("|---|---|---|---|---|")
        for pair, m in f["minute_diffs"].items():
            h, lo = m["high_abs"], m["low_abs"]
            lines.append(f"| {pair} | {m['high_mismatch_share']} | {m['low_mismatch_share']} | "
                         f"{h['p50']}/{h['p90']}/{h['p99']}/{h['max']} | {lo['p50']}/{lo['p90']}/{lo['p99']}/{lo['max']} |")
        lines.append("")
        for key in ("swings", "ranges", "extension", "takes", "swing_sweeps", "stops", "gc"):
            if key in f:
                lines.append(f"- {key}: {json.dumps(f[key], default=str)}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    r = evaluate()
    REPORT_JSON.write_text(json.dumps(r, indent=2, default=str) + "\n")
    REPORT_MD.write_text(render_md(r))
    print(json.dumps(r["totals"], indent=1, default=str))


if __name__ == "__main__":
    main()
