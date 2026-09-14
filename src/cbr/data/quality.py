"""Data-quality detectors (owner ruling D12). They flag; they never fill, interpolate or synthesize prices.

- dxy_cfd_missing_while_dx_active: periods where DX futures trade but the Dukascopy DXY CFD has no observations.
- candle_hl_bounds / suspect_candle_extrema: candle-file mid high/low are means of per-side extremes that may come
  from different ticks (method SIDE_EXTREME_MEAN); these give each minute's exact overstatement bound and a flag.
- artificial_extrema_vs_ticks: exact comparison against tick-built bars where those exist.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "config" / "data_quality.yaml"
DXY_MISSING = "DXY_CFD_MISSING_WHILE_DX_ACTIVE"
HL_SUSPECT = "CANDLE_HL_SYNTHETIC_EXTREME_SUSPECT"
HL_CANDLE_FILE = "SIDE_EXTREME_MEAN"
HL_TICK_BARS = "TICK_MID"


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text())


def dxy_cfd_missing_while_dx_active(cfd_index: pd.DatetimeIndex, dx: pd.DataFrame, start: pd.Timestamp,
                                    end: pd.Timestamp, cfg: dict | None = None) -> list[dict]:
    """Runs of >= min_missing_run_minutes UTC minutes in [start, end) with no CFD row, containing
    >= min_dx_active_minutes DX bars with volume > 0. dx: 1m bars indexed by open time, with a 'volume' column."""
    p = (cfg or load_config())["dxy_cfd_missing_while_dx_active"]
    minutes = pd.date_range(start, end, freq="1min", inclusive="left")
    missing = minutes.difference(cfd_index)
    dx_active = dx.index[(dx["volume"] > 0) & (dx.index >= start) & (dx.index < end)]
    out, run = [], []
    for m in [*missing, None]:
        if m is not None and run and m - run[-1] == pd.Timedelta(minutes=1):
            run.append(m)
            continue
        if len(run) >= p["min_missing_run_minutes"]:
            active = dx_active[(dx_active >= run[0]) & (dx_active <= run[-1])]
            if len(active) >= p["min_dx_active_minutes"]:
                sel = dx[(dx.index >= run[0]) & (dx.index <= run[-1])]
                # flagged span = first..last active DX minute inside the CFD gap; the full gap is kept alongside
                out.append({"reason_code": DXY_MISSING, "start": active[0], "end": active[-1] + pd.Timedelta(minutes=1),
                            "cfd_gap_start": run[0], "cfd_gap_end": run[-1] + pd.Timedelta(minutes=1),
                            "cfd_gap_minutes": len(run), "dx_active_minutes": len(active),
                            "dx_volume": float(sel["volume"].sum()), "handling": "MISSING"})
        run = [m] if m is not None else []
    return out


def candle_hl_bounds(c: pd.DataFrame) -> pd.DataFrame:
    """Exact per-minute bounds on how far candle mid high/low can overstate true tick-mid extremes."""
    sync_half_spread = pd.concat([c["ask_open"] - c["bid_open"], c["ask_close"] - c["bid_close"]], axis=1).min(axis=1) / 2
    return pd.DataFrame({"hl_err_bound_high": (c["ask_high"] - c["bid_high"]) / 2,
                         "hl_err_bound_low": (c["ask_low"] - c["bid_low"]) / 2,
                         "sync_half_spread": sync_half_spread}, index=c.index)


def suspect_candle_extrema(c: pd.DataFrame, cfg: dict | None = None) -> pd.Series:
    ratio = (cfg or load_config())["candle_extrema"]["suspect_ratio"]
    b = candle_hl_bounds(c)
    return (b[["hl_err_bound_high", "hl_err_bound_low"]].max(axis=1) > ratio * b["sync_half_spread"]).rename(HL_SUSPECT)


def artificial_extrema_vs_ticks(candles: pd.DataFrame, tick_bars: pd.DataFrame, tolerance: float) -> pd.DataFrame:
    """Minutes (present in both) where candle mid high exceeds, or mid low undercuts, the tick-mid extreme."""
    j = tick_bars[["high", "low"]].join(candles[["high", "low", "bid_high", "ask_high", "bid_low", "ask_low"]],
                                        rsuffix="_c", how="inner")
    j["high_overstatement"] = j["high_c"] - j["high"]
    j["low_overstatement"] = j["low"] - j["low_c"]
    j = j.join(candle_hl_bounds(candles.loc[j.index]))
    j["artificial"] = (j["high_overstatement"] > tolerance) | (j["low_overstatement"] > tolerance)
    j["within_bound"] = ((j["high_overstatement"] <= j["hl_err_bound_high"] + 1e-9)
                         & (j["low_overstatement"] <= j["hl_err_bound_low"] + 1e-9))
    return j
