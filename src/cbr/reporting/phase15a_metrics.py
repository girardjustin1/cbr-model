"""Phase 15A metric calculator (owner ruling D42 §10-11, protocol CBR-ACC-015A §8-9).

Computes the metrics the frozen protocol predeclares, from an execution ledger. It defines no new metric, and the
primary metric stays **net expectancy in R per executed canonical trade**; win rate is secondary and is never
optimized for.

The separation the protocol demands is enforced here rather than remembered:

* **canonical completed trades** — `CLOSED` with exit reason `TARGET` or `STOP` — are the only rows in win/loss and
  expectancy statistics;
* **administrative exits** — `ROLLOVER_EXIT`, `DATASET_END_EXIT` — are reported separately with their own counts and
  R, and never merged in;
* **unprovable outcomes** carry no inferred win or loss, and their rate over eligible signals is a data-quality
  metric;
* every statistic carries its denominator.

Nothing here reads a strategy rule, and nothing tunes: the breakdowns by month, direction, variant and session are
descriptive output only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import pandas as pd

from cbr.execution import ledger as el

METRICS_VERSION = "15A.1"
PRIMARY_METRIC = "net_expectancy_r"

SESSION_BUCKETS = (("ASIA", 0, 7), ("LONDON", 7, 12), ("NY_OVERLAP", 12, 16), ("NY_PM", 16, 21), ("LATE", 21, 24))


def _bucket(hour: int) -> str:
    for name, lo, hi in SESSION_BUCKETS:
        if lo <= hour < hi:
            return name
    return "LATE"


@dataclass
class Metrics:
    values: dict = field(default_factory=dict)
    breakdowns: dict = field(default_factory=dict)
    funnel: dict = field(default_factory=dict)
    execution_quality: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"metrics_version": METRICS_VERSION, "primary_metric": PRIMARY_METRIC, "metrics": self.values,
                "funnel": self.funnel, "breakdowns": self.breakdowns, "execution_quality": self.execution_quality}

    def metrics_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.as_dict(), sort_keys=True, default=str).encode()).hexdigest()


def _f(x):
    return None if x is None or (isinstance(x, float) and pd.isna(x)) else float(x)


def canonical(frame: pd.DataFrame) -> pd.DataFrame:
    """The only rows permitted in win/loss and expectancy statistics."""
    if not len(frame):
        return frame
    return frame[(frame["execution_status"] == el.CLOSED) & (frame["exit_reason"].isin(el.CANONICAL_EXITS))]


def administrative(frame: pd.DataFrame) -> pd.DataFrame:
    if not len(frame):
        return frame
    return frame[(frame["execution_status"] == el.CLOSED)
                 & (frame["exit_reason"].isin([el.ROLLOVER_EXIT, el.DATASET_END_EXIT]))]


def _core(t: pd.DataFrame) -> dict:
    """The §10 metric list over a set of canonical completed trades. Empty input yields None, never zero."""
    n = len(t)
    if n == 0:
        return {k: None for k in (
            "trade_count", "wins", "losses", "win_rate", "planned_rr_mean", "planned_rr_median", "gross_r", "net_r",
            "average_winner", "average_loser", "median_r", "net_expectancy_r", "profit_factor", "max_drawdown_r",
            "longest_losing_streak", "total_net_r")} | {"trade_count": 0}
    net = t["net_r"].astype(float)
    gross = t["gross_r"].astype(float)
    wins, losses = net[net > 0], net[net <= 0]
    equity = net.cumsum()
    drawdown = equity - equity.cummax()
    streak = best = 0
    for r in net:
        streak = streak + 1 if r <= 0 else 0
        best = max(best, streak)
    gain, pain = float(wins.sum()), float(-losses.sum())
    planned = t["planned_rr"].astype(float) if "planned_rr" in t else pd.Series(dtype=float)
    return {
        "trade_count": n,
        "wins": int((net > 0).sum()),
        "losses": int((net <= 0).sum()),
        "win_rate": float((net > 0).mean()),
        "planned_rr_mean": _f(planned.mean()) if len(planned.dropna()) else None,
        "planned_rr_median": _f(planned.median()) if len(planned.dropna()) else None,
        "gross_r": _f(gross.sum()),
        "net_r": _f(net.sum()),
        "average_winner": _f(wins.mean()) if len(wins) else None,
        "average_loser": _f(losses.mean()) if len(losses) else None,
        "median_r": _f(net.median()),
        "net_expectancy_r": _f(net.mean()),          # the primary metric: net R per executed canonical trade
        "profit_factor": (_f(gain / pain) if pain > 0 else None),
        "max_drawdown_r": _f(drawdown.min()),
        "longest_losing_streak": int(best),
        "total_net_r": _f(net.sum()),
        "denominator": n,
    }


def _planned_rr(frame: pd.DataFrame) -> pd.Series:
    """Planned reward:risk at fill, from the frozen ledger fields. No assumption is substituted when inputs are absent."""
    if not len(frame):
        return pd.Series(dtype=float)
    fill = frame["fill_price"].astype(float)
    stop = frame["final_execution_stop"].astype(float)
    target = frame["target_price"].astype(float)
    risk = (fill - stop).abs()
    reward = (target - fill).abs()
    return (reward / risk).where(risk > 0)


def compute(execution_ledger, *, eligible_signals: int | None = None) -> Metrics:
    """All predeclared Phase 15A metrics. `execution_ledger` is an `ExecutionLedger` or a DataFrame of its rows."""
    frame = execution_ledger if isinstance(execution_ledger, pd.DataFrame) else execution_ledger.frame()
    m = Metrics()
    if not len(frame):
        m.values = _core(pd.DataFrame())
        m.funnel = {"signals": 0}
        return m

    frame = frame.copy()
    frame["planned_rr"] = _planned_rr(frame)
    t = canonical(frame)
    admin = administrative(frame)
    unprovable = frame[frame["execution_status"] == el.UNPROVABLE]

    m.values = _core(t)

    # The signal funnel: every row lands in exactly one bucket, and the buckets sum to the signal count.
    reasons = frame["reason_code"].fillna("-")
    m.funnel = {
        "signals": len(frame),
        "canonical_completed_trades": len(t),
        "administrative_exits": len(admin),
        "unprovable": len(unprovable),
        "not_executed": int((frame["execution_status"] == el.NOT_EXECUTED).sum()),
        "cancelled": int((frame["execution_status"] == el.CANCELLED).sum()),
        "still_open": int(frame["execution_status"].isin([el.PENDING, el.FILLED]).sum()),
        "by_reason_code": {k: int(v) for k, v in reasons.value_counts().items()},
        "eligible_signals": eligible_signals if eligible_signals is not None else len(frame),
    }
    denom = m.funnel["eligible_signals"] or 1
    m.funnel["unprovable_rate"] = len(unprovable) / denom
    m.funnel["fill_rate"] = int(frame["fill_time"].notna().sum()) / denom
    buckets = (m.funnel["canonical_completed_trades"] + m.funnel["administrative_exits"] + m.funnel["unprovable"]
               + m.funnel["not_executed"] + m.funnel["cancelled"] + m.funnel["still_open"])
    m.funnel["every_signal_accounted"] = buckets == len(frame)

    # Descriptive breakdowns (D42 §10: never tuned from during the pilot).
    if len(t):
        ts = pd.to_datetime(t["fill_time"], utc=True, errors="coerce")
        m.breakdowns = {
            "month": {str(k): _core(g) for k, g in t.groupby(ts.dt.strftime("%Y-%m"))},
            "direction": {str(k): _core(g) for k, g in t.groupby(t["direction"])},
            "variant": {str(k): _core(g) for k, g in t.groupby(t["variant"])},
            "session_bucket": {str(k): _core(g) for k, g in t.groupby(ts.dt.hour.map(_bucket))},
        }
        m.breakdowns["_note"] = "DESCRIPTIVE ONLY — no rule, parameter or filter may be selected from these."
        eq = t["net_r"].astype(float).cumsum()
        m.values["equity_curve"] = [[str(a), _f(b)] for a, b in zip(t["exit_time"], eq, strict=False)]

    # Execution quality over everything that reached the market.
    filled = frame[frame["fill_time"].notna()]
    def dist(s: pd.Series) -> dict:
        s = pd.to_numeric(s, errors="coerce").dropna()
        if not len(s):
            return {"count": 0}
        return {"count": len(s), "mean": _f(s.mean()), "median": _f(s.median()), "p90": _f(s.quantile(0.9)),
                "max": _f(s.max()), "min": _f(s.min())}
    m.execution_quality = {
        "spread": dist(filled["fill_spread"]) if len(filled) else {"count": 0},
        "entry_gap": dist(filled["entry_gap"]) if len(filled) else {"count": 0},
        "stop_gap": dist(frame["stop_gap"]),
        "rollover_exits": int((frame["exit_reason"] == el.ROLLOVER_EXIT).sum()),
        "dataset_end_exits": int((frame["exit_reason"] == el.DATASET_END_EXIT).sum()),
        "unprovable_count": len(unprovable),
        "unprovable_rate": len(unprovable) / denom,
        "unprovable_by_reason": {k: int(v) for k, v in
                                 unprovable["reason_code"].value_counts().items()} if len(unprovable) else {},
        "administrative_r": {"net_r": _f(admin["net_r"].astype(float).sum()) if len(admin) else None,
                             "count": len(admin)},
        "tick_resolved": int(frame["tick_resolved"].fillna(False).astype(bool).sum()),
        "additional_slippage_assumption": 0.0,
        "explicit_commission_assumption": 0.0,
    }
    return m


def drawdowns(execution_ledger) -> pd.DataFrame:
    """Peak-to-trough drawdown episodes in R over canonical completed trades, for the review package."""
    frame = execution_ledger if isinstance(execution_ledger, pd.DataFrame) else execution_ledger.frame()
    t = canonical(frame)
    if not len(t):
        return pd.DataFrame(columns=["start_time", "trough_time", "end_time", "depth_r", "trades", "recovered"])
    t = t.sort_values("exit_time")
    eq = t["net_r"].astype(float).cumsum().to_numpy()
    times = t["exit_time"].to_numpy()
    rows, peak, peak_i = [], eq[0], 0
    trough, trough_i, open_dd = eq[0], 0, False
    for i, v in enumerate(eq):
        if v >= peak:
            if open_dd:
                rows.append({"start_time": str(times[peak_i]), "trough_time": str(times[trough_i]),
                             "end_time": str(times[i]), "depth_r": float(trough - peak),
                             "trades": int(i - peak_i), "recovered": True})
                open_dd = False
            peak, peak_i = v, i
        else:
            if not open_dd or v < trough:
                trough, trough_i = v, i
            open_dd = True
    if open_dd:
        rows.append({"start_time": str(times[peak_i]), "trough_time": str(times[trough_i]),
                     "end_time": None, "depth_r": float(trough - peak),
                     "trades": int(len(eq) - 1 - peak_i), "recovered": False})
    return pd.DataFrame(rows)
