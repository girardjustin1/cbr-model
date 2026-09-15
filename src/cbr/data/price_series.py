"""Canonical price series with explicit price roles (owner ruling D16, CBR-DEC-025).

STRUCTURE bars: tick-derived mid OHLC (`hl_method = TICK_MID`), the only input to swings, ranges, extensions, takes/sweeps,
stop anchors and target construction. They carry no bid/ask/spread fields.
EXECUTION bars: tick-derived bid and ask OHLC (`hl_method = BID_ASK`), the only input to fills, stop/target touches,
spread and execution costs. They carry no mid OHLC fields.

One OHLC series is never used for both. `require_structure` / `require_execution` are the access guards every engine
and simulator entry point calls; they raise `PriceRoleError` instead of silently accepting the wrong series.
"""

from __future__ import annotations

import pandas as pd

STRUCTURE, EXECUTION = "STRUCTURE", "EXECUTION"
TICK_MID, BID_ASK = "TICK_MID", "BID_ASK"
OHLC = ["open", "high", "low", "close"]
SIDE_COLUMNS = [f"{side}_{c}" for side in ("bid", "ask") for c in OHLC]
_EXECUTION_MARKERS = ("bid", "ask", "spread")


class PriceRoleError(ValueError):
    """A bar frame was offered to code that requires a different price role."""


def _clean(ticks: pd.DataFrame) -> pd.Series:
    if not {"ts", "bid", "ask"} <= set(ticks.columns):
        raise ValueError("ticks need ts, bid, ask columns")
    t = ticks.sort_values("ts", kind="stable").set_index("ts")
    if t.index.tz is None or str(t.index.tz) != "UTC":
        raise ValueError("tick timestamps must be tz-aware UTC")
    return t


def structure_bars(ticks: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Mid OHLC + tick_count per interval (open time, UTC). Empty intervals produce no bar."""
    t = _clean(ticks)
    mid = (t["bid"] + t["ask"]) / 2
    g = mid.resample(freq, label="left", closed="left")
    bars = g.ohlc()
    bars["tick_count"] = g.count()
    bars = bars[bars["tick_count"] > 0].copy()
    bars["hl_method"], bars["price_role"] = TICK_MID, STRUCTURE
    bars.index.name = "open_time"
    return bars


def execution_bars(ticks: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Bid OHLC and ask OHLC + tick_count per interval (open time, UTC). Empty intervals produce no bar."""
    t = _clean(ticks)
    parts = {}
    for side in ("bid", "ask"):
        g = t[side].resample(freq, label="left", closed="left")
        o = g.ohlc()
        parts.update({f"{side}_{c}": o[c] for c in OHLC})
        parts["tick_count"] = g.count()
    bars = pd.DataFrame(parts)
    bars = bars[bars["tick_count"] > 0].copy()
    bars["hl_method"], bars["price_role"] = BID_ASK, EXECUTION
    bars.index.name = "open_time"
    return bars[[*SIDE_COLUMNS, "tick_count", "hl_method", "price_role"]]


def rollup_structure(bars: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Clock-aligned roll-up of STRUCTURE bars (e.g. 1m → 5m/15m/1h). A rolled bar is usable only at its close."""
    require_structure(bars)
    g = bars.resample(freq, label="left", closed="left")
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                        "close": g["close"].last(), "tick_count": g["tick_count"].sum(),
                        "bars": g["open"].count()})
    out = out[out["bars"] > 0].copy()
    out["hl_method"], out["price_role"] = TICK_MID, STRUCTURE
    out.index.name = "open_time"
    return out


def _role_ok(bars: pd.DataFrame, role: str, method: str) -> bool:
    return ("price_role" in bars.columns and "hl_method" in bars.columns
            and bool((bars["price_role"] == role).all()) and bool((bars["hl_method"] == method).all()))


def require_structure(bars: pd.DataFrame) -> pd.DataFrame:
    """Access guard for signal/structure code. Returns the frame unchanged when it is canonical STRUCTURE data."""
    if not isinstance(bars, pd.DataFrame) or not _role_ok(bars, STRUCTURE, TICK_MID):
        raise PriceRoleError("structure code requires STRUCTURE bars (price_role=STRUCTURE, hl_method=TICK_MID); "
                             "candle-file mids, bid/ask bars and untagged frames are refused (D16)")
    leaked = [c for c in bars.columns if c.startswith(_EXECUTION_MARKERS)]
    if leaked:
        raise PriceRoleError(f"STRUCTURE bars must not carry execution fields: {leaked}")
    if not set(OHLC) <= set(bars.columns):
        raise PriceRoleError("STRUCTURE bars need open/high/low/close")
    return bars


def require_execution(bars: pd.DataFrame) -> pd.DataFrame:
    """Access guard for execution code. Returns the frame unchanged when it is canonical EXECUTION data."""
    if not isinstance(bars, pd.DataFrame) or not _role_ok(bars, EXECUTION, BID_ASK):
        raise PriceRoleError("execution code requires EXECUTION bars (price_role=EXECUTION, hl_method=BID_ASK); "
                             "mid/structure bars are refused for fills and touches (D16)")
    if set(OHLC) & set(bars.columns):
        raise PriceRoleError("EXECUTION bars must not carry mid open/high/low/close fields")
    missing = [c for c in SIDE_COLUMNS if c not in bars.columns]
    if missing:
        raise PriceRoleError(f"EXECUTION bars missing {missing}")
    return bars
