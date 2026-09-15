"""Databento continuous front-month 1m bars, filtered as in Phase 9 (primary publisher, positive prices, unique index)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATABENTO = ROOT / "data" / "raw" / "databento"


def load_front(name: str) -> pd.DataFrame:
    """name: 'gc_front_ohlcv1m' or 'dx_front_ohlcv1m'."""
    f = pd.read_parquet(DATABENTO / f"{name}.parquet")
    f = f[(f["publisher_id"] == f["publisher_id"].mode().iloc[0]) & (f["close"] > 0)]
    return f[~f.index.duplicated()]
