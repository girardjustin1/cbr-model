"""Phase 10 DXY context module (CBR-ACC-010, config/dxy_context.yaml).

Deterministic, causal context primitives from Dukascopy DXY CFD 1m candles for any UTC decision-time grid:
quote context, and last-closed / forming 15m and 1h candle direction and move, each with state, confidence, coverage and
reason codes. No DXY trading rule, filter or veto lives here (D14); no highs/lows are used (OQ-25); no 1m/5s DXY
structure (D12-6).

Causality: a 1m row (open time m) is known at decision time t iff m + 1 min <= t. Every causal field at t is a
function of known rows, known DX activity and the static session calendar only. DX futures are used solely to flag CFD
vendor gaps (volume > 0), never as prices (D12-1). The `dq_hindsight_*` fields run the Phase 9 detector over the whole
loaded span, so they use future data by design and must never feed a signal engine (CBR-ACC-010 §2.2).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from cbr.data import quality as q
from cbr.data.sessions import expected_closed_mask

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "config" / "dxy_context.yaml"
MINUTE = pd.Timedelta(minutes=1)
FULL, REDUCED, UNAVAILABLE = "FULL", "REDUCED", "UNAVAILABLE"


def load_config() -> dict:
    cfg = yaml.safe_load(CONFIG.read_text())
    dq = q.load_config()["dxy_cfd_missing_while_dx_active"]
    return {"version": cfg["version"], "timeframes": cfg["timeframes"],
            "flat_epsilon": cfg["direction"]["flat_epsilon"]["value"],
            "max_quote_age_minutes": cfg["quote"]["max_quote_age_minutes"]["value"],
            "min_coverage_full": cfg["window"]["min_coverage_full"]["value"],
            "run_minutes": dq["min_missing_run_minutes"], "dx_active_minutes": dq["min_dx_active_minutes"]}


def _require_utc(idx: pd.Index, name: str) -> None:
    if not isinstance(idx, pd.DatetimeIndex) or idx.tz is None or str(idx.tz) != "UTC":
        raise ValueError(f"{name} must be a tz-aware UTC DatetimeIndex")


@dataclass(frozen=True)
class _Span:
    start: pd.Timestamp          # hour-aligned minute 0
    n: int
    loaded: np.ndarray           # minute inside the loaded CFD range
    has_row: np.ndarray
    open_px: np.ndarray
    close_px: np.ndarray
    closed: np.ndarray           # expected-closed schedule
    dx_active: np.ndarray        # DX volume > 0 (known once the DX minute closes)
    dx_ref: np.ndarray           # DX dataset covers the minute
    cum_row: np.ndarray
    cum_open_row: np.ndarray
    cum_open: np.ndarray
    cum_closed: np.ndarray
    cum_dx: np.ndarray
    cum_noref: np.ndarray
    cum_unloaded: np.ndarray
    run_start: np.ndarray        # for no-row minutes: first minute of their no-row run (runs restart at loaded start)
    run_end: np.ndarray          # exclusive end of the full (untruncated) run
    prev_row: np.ndarray         # index of the last row at or before minute m, -1 if none
    next_row: np.ndarray         # index of the first row at or after minute m, n if none


def _cum(a: np.ndarray) -> np.ndarray:
    return np.concatenate([[0], np.cumsum(a, dtype=np.int64)])


def _span(dxy: pd.DataFrame, loaded: tuple[pd.Timestamp, pd.Timestamp], dx: pd.DataFrame | None,
          dx_range: tuple[pd.Timestamp, pd.Timestamp] | None, grid_end: pd.Timestamp) -> _Span:
    lo, hi = (pd.Timestamp(x).tz_convert("UTC") for x in loaded)
    start = lo.floor("1h")
    end = max(hi, grid_end).ceil("1h")
    minutes = pd.date_range(start, end, freq="1min", inclusive="left", unit="ns")
    n = len(minutes)
    in_loaded = np.asarray((minutes >= lo) & (minutes < hi))
    rows = dxy[(dxy.index >= lo) & (dxy.index < hi)]
    pos = np.asarray(((rows.index.as_unit("ns") - start) // MINUTE), dtype=np.int64)
    has_row = np.zeros(n, bool)
    has_row[pos] = True
    open_px = np.full(n, np.nan)
    close_px = np.full(n, np.nan)
    open_px[pos], close_px[pos] = rows["open"].to_numpy(float), rows["close"].to_numpy(float)
    closed = expected_closed_mask(minutes)
    dx_active = np.zeros(n, bool)
    dx_ref = np.zeros(n, bool)
    if dx is not None:
        act = dx.index[((dx["volume"] > 0) & (dx.index >= start) & (dx.index < end)).to_numpy()]
        dx_active[np.asarray(((act.as_unit("ns") - start) // MINUTE), dtype=np.int64)] = True
        a, b = (pd.Timestamp(x).tz_convert("UTC") for x in dx_range)
        dx_ref = np.asarray((minutes >= a) & (minutes < b))
        dx_active &= dx_ref                                  # no activity is asserted outside the DX dataset
    no_row = in_loaded & ~has_row
    run_start = np.full(n, -1, np.int64)
    run_end = np.full(n, -1, np.int64)
    i = 0
    while i < n:
        if no_row[i]:
            j = i
            while j < n and no_row[j]:
                j += 1
            run_start[i:j], run_end[i:j] = i, j
            i = j
        else:
            i += 1
    idx = np.arange(n)
    prev_row = np.maximum.accumulate(np.where(has_row, idx, -1))
    next_row = np.minimum.accumulate(np.where(has_row, idx, n)[::-1])[::-1]
    return _Span(start, n, in_loaded, has_row, open_px, close_px, closed, dx_active, dx_ref,
                 _cum(has_row), _cum(has_row & ~closed), _cum(~closed), _cum(closed), _cum(dx_active),
                 _cum(~dx_ref), _cum(~in_loaded), run_start, run_end, prev_row, next_row)


def _flagged_runs(s: _Span, a: int, e: int, k: int, cfg: dict, hindsight: bool = False) -> tuple[bool, bool]:
    """(vendor-gap flag, unverified long gap) for no-row runs overlapping [a, e), truncated at k unless hindsight."""
    m = np.flatnonzero(s.run_start[a:e] >= 0)
    if not len(m):
        return False, False
    starts = np.unique(s.run_start[a:e][m])
    ends = s.run_end[starts] if hindsight else np.minimum(s.run_end[starts], k)
    length = ends - starts
    dx_count = s.cum_dx[ends] - s.cum_dx[starts]
    long_run = length >= cfg["run_minutes"]
    flag = bool(np.any(long_run & (dx_count >= cfg["dx_active_minutes"])))
    noref = (s.cum_noref[ends] - s.cum_noref[starts]) > 0
    return flag, bool(np.any(long_run & noref))


def _direction(move: float, eps: float) -> str:
    return "UP" if move > eps else "DOWN" if move < -eps else "FLAT"


def _window(s: _Span, a: int, b: int, k: int, cfg: dict) -> dict:
    """State of window [a, b) as known at minute boundary k (elapsed part [a, min(b, k)))."""
    e = min(b, k)
    out = {"open_utc": s.start + a * MINUTE, "elapsed_min": max(e - a, 0), "direction": None, "move": np.nan,
           "coverage": np.nan, "rows": 0, "state": None, "confidence": UNAVAILABLE, "reasons": []}
    if e <= a:
        out.update(state="NO_ELAPSED_TIME", reasons=["DXY_WINDOW_NOT_STARTED"])
        return out
    if a < 0 or s.cum_unloaded[e] - s.cum_unloaded[a] > 0:
        out.update(state="NOT_LOADED", reasons=["DXY_NOT_LOADED"])
        return out
    if s.cum_closed[e] - s.cum_closed[a] == e - a:
        out.update(state="CLOSED_SCHEDULE", reasons=["DXY_SESSION_CLOSED"])
        return out
    flag, unverified = _flagged_runs(s, a, e, k, cfg)
    rows = int(s.cum_row[e] - s.cum_row[a])
    out["rows"] = rows
    if flag:
        out.update(state="VENDOR_MISSING", reasons=[q.DXY_MISSING])
        return out
    if rows == 0:
        out.update(state="NO_QUOTES", reasons=["DXY_NO_QUOTES"])
        return out
    open_minutes = int(s.cum_open[e] - s.cum_open[a])
    coverage = (s.cum_open_row[e] - s.cum_open_row[a]) / open_minutes if open_minutes else 0.0
    first, last = s.next_row[a], s.prev_row[e - 1]
    move = float(s.close_px[last] - s.open_px[first])
    out.update(coverage=round(float(coverage), 6), move=move, direction=_direction(move, cfg["flat_epsilon"]))
    reasons = []
    if coverage < cfg["min_coverage_full"]:
        reasons.append("DXY_LOW_COVERAGE")
    if unverified:
        reasons.append("DX_REFERENCE_UNAVAILABLE")
    state = ("LOW_COVERAGE" if "DXY_LOW_COVERAGE" in reasons else "UNVERIFIED_GAP" if reasons else "OK")
    out.update(state=state, confidence=REDUCED if reasons else FULL, reasons=reasons)
    return out


def build_context(dxy: pd.DataFrame, grid: pd.DatetimeIndex, loaded: tuple[pd.Timestamp, pd.Timestamp],
                  dx: pd.DataFrame | None = None, dx_range: tuple[pd.Timestamp, pd.Timestamp] | None = None,
                  cfg: dict | None = None, hindsight: bool = True) -> pd.DataFrame:
    """Context per decision time in `grid`.

    dxy: DXY CFD 1m candles (index = open time UTC; columns open, close). loaded: [start, end) range the CFD data covers
    (minutes outside it are NOT_LOADED, never NO_QUOTES). dx: DX 1m bars (index = open time UTC; only 'volume' is read)
    with dx_range = [start, end) of the DX dataset. hindsight=False skips the dq_hindsight_* fields.
    """
    cfg = cfg or load_config()
    _require_utc(dxy.index, "dxy index")
    _require_utc(grid, "decision grid")
    if dx is not None:
        _require_utc(dx.index, "dx index")
        if dx_range is None:
            raise ValueError("dx_range is required with dx")
    s = _span(dxy, loaded, dx, dx_range, grid.max() if len(grid) else pd.Timestamp(loaded[1]))
    records = []
    for t in grid:
        k = int((t.as_unit("ns") - s.start) // MINUTE)
        if k < 0 or k > s.n:
            raise ValueError(f"decision time {t} outside the span")
        rec = {"decision_time_utc": t, "dxy_context_version": cfg["version"]}
        reasons: list[str] = []
        if k > 0 and not s.dx_ref[k - 1]:
            reasons.append("DX_REFERENCE_UNAVAILABLE")        # vendor gaps can't be verified at t (D12-3)
        last = s.prev_row[k - 1] if k > 0 else -1
        close, quote_time, age, conf = np.nan, pd.NaT, np.nan, UNAVAILABLE
        if last < 0 or not s.loaded[last]:
            reasons.append("DXY_NOT_LOADED")
        else:
            age_min = k - (last + 1)
            gap_closed = s.cum_closed[k] - s.cum_closed[last + 1] > 0
            flag, _ = _flagged_runs(s, last + 1, k, k, cfg) if age_min > 0 else (False, False)
            quote_time, age = s.start + (last + 1) * MINUTE, float(age_min * 60)
            if flag:
                reasons.append(q.DXY_MISSING)
            elif gap_closed:
                reasons.append("DXY_SESSION_CLOSED")
            elif age_min > cfg["max_quote_age_minutes"]:
                reasons.append("DXY_QUOTE_STALE")
            else:
                close, conf = float(s.close_px[last]), FULL if age_min == 0 else REDUCED
        rec.update(dxy_close=close, dxy_quote_close_utc=quote_time, dxy_quote_age_s=age,
                   dxy_available=not np.isnan(close), dxy_confidence=conf)
        for tf, minutes in cfg["timeframes"].items():
            a = (k // minutes) * minutes
            for kind, (wa, wb) in (("last", (a - minutes, a)), ("forming", (a, a + minutes))):
                w = _window(s, wa, wb, k, cfg)
                p = f"dxy_{tf}_{kind}_"
                rec.update({p + "open_utc": w["open_utc"], p + "direction": w["direction"], p + "move": w["move"],
                            p + "state": w["state"], p + "confidence": w["confidence"],
                            p + "coverage": w["coverage"], p + "rows": w["rows"]})
                if kind == "forming":
                    rec[p + "elapsed_min"] = w["elapsed_min"]
                reasons += [f"{tf}_{kind}:{r}" for r in w["reasons"]]
                if hindsight:
                    lo_, hi_ = max(wa, 0), min(wb, s.n)
                    rec[f"dq_hindsight_{tf}_{kind}_vendor_gap"] = (
                        _flagged_runs(s, lo_, hi_, s.n, cfg, hindsight=True)[0] if hi_ > lo_ else False)
        rec["dxy_reason_codes"] = ";".join(sorted(set(reasons)))
        if hindsight:
            rec["dq_hindsight_vendor_gap"] = bool(k > 0 and _flagged_runs(s, k - 1, k, s.n, cfg, hindsight=True)[0])
        records.append(rec)
    out = pd.DataFrame.from_records(records).set_index("decision_time_utc")
    text = [c for c in out.columns if c.endswith(("_direction", "_state", "_confidence", "_reason_codes", "_version"))]
    out[text] = out[text].astype("str")                      # one missing-value representation (NaN) for all
    stamps = [c for c in out.columns if c.endswith("_utc")]
    out[stamps] = out[stamps].apply(lambda col: pd.to_datetime(col, utc=True))   # keep UTC even when all NaT
    return out


def causal_columns(ctx: pd.DataFrame) -> list[str]:
    return [c for c in ctx.columns if not c.startswith("dq_hindsight_")]


def context_hash(ctx: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(ctx.astype(str), index=True).values.tobytes()).hexdigest()
