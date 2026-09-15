"""Two-price-series rule (owner ruling D16): builders tag roles; guards refuse the wrong series."""

import re
from pathlib import Path

import pandas as pd
import pytest

from cbr.data import price_series as ps

ROOT = Path(__file__).resolve().parents[1]


def _ticks():
    ts = pd.to_datetime(["2025-10-21 01:00:01", "2025-10-21 01:00:20", "2025-10-21 01:00:40",
                         "2025-10-21 01:01:05", "2025-10-21 01:01:50"], utc=True)
    return pd.DataFrame({"ts": ts, "bid": [100.0, 100.4, 99.8, 100.1, 100.2],
                         "ask": [100.2, 100.6, 100.4, 100.3, 100.4], "bid_vol": 1.0, "ask_vol": 1.0})


def test_structure_bars_are_tick_mid_and_tagged():
    b = ps.structure_bars(_ticks(), "1min")
    first = b.iloc[0]
    assert (first["open"], first["high"], first["low"], first["close"]) == pytest.approx((100.1, 100.5, 100.1, 100.1))
    assert set(b["price_role"]) == {"STRUCTURE"} and set(b["hl_method"]) == {"TICK_MID"}
    assert not [c for c in b.columns if c.startswith(("bid", "ask", "spread"))]
    ps.require_structure(b)


def test_execution_bars_are_bid_ask_and_tagged():
    b = ps.execution_bars(_ticks(), "1min")
    first = b.iloc[0]
    assert (first["bid_high"], first["bid_low"], first["ask_high"], first["ask_low"]) == pytest.approx(
        (100.4, 99.8, 100.6, 100.2))
    assert set(b["price_role"]) == {"EXECUTION"} and not set(ps.OHLC) & set(b.columns)
    ps.require_execution(b)


def test_structure_guard_refuses_execution_candle_and_untagged_frames():
    with pytest.raises(ps.PriceRoleError):
        ps.require_structure(ps.execution_bars(_ticks(), "1min"))
    candle = ps.structure_bars(_ticks(), "1min").assign(hl_method="SIDE_EXTREME_MEAN")
    with pytest.raises(ps.PriceRoleError):
        ps.require_structure(candle)                              # averaged candle-file mids are never canonical
    with pytest.raises(ps.PriceRoleError):
        ps.require_structure(ps.structure_bars(_ticks(), "1min").drop(columns=["price_role"]))
    leaked = ps.structure_bars(_ticks(), "1min").assign(bid_high=1.0)
    with pytest.raises(ps.PriceRoleError):
        ps.require_structure(leaked)                              # no silent bid/ask inside structure bars


def test_execution_guard_refuses_mid_bars():
    with pytest.raises(ps.PriceRoleError):
        ps.require_execution(ps.structure_bars(_ticks(), "1min"))
    mixed = ps.execution_bars(_ticks(), "1min").assign(high=1.0)
    with pytest.raises(ps.PriceRoleError):
        ps.require_execution(mixed)                               # no mid substitute for fills


def test_rollup_keeps_role_and_equals_direct_resample():
    ticks = _ticks()
    rolled = ps.rollup_structure(ps.structure_bars(ticks, "5s"), "1min")
    direct = ps.structure_bars(ticks, "1min")
    pd.testing.assert_frame_equal(rolled[ps.OHLC], direct[ps.OHLC])
    assert set(rolled["price_role"]) == {"STRUCTURE"}


def test_engine_code_never_reads_execution_fields():
    """Signal/structure packages must not reference bid/ask/spread columns (execution belongs to Phase 14A)."""
    offenders = []
    for pkg in ("structure", "engine"):
        for f in (ROOT / "src" / "cbr" / pkg).rglob("*.py"):
            for n, line in enumerate(f.read_text().splitlines(), 1):
                code = line.split("#", 1)[0]
                if re.search(r"""["'](bid|ask)(_\w+)?["']|["']spread\w*["']|execution_bars""", code):
                    offenders.append(f"{f.relative_to(ROOT)}:{n}")
    assert offenders == []


def test_execution_code_never_builds_structure_series():
    exec_dir = ROOT / "src" / "cbr" / "execution"
    if not exec_dir.exists():
        pytest.skip("Phase 14A execution package not built yet")
    offenders = [str(f) for f in exec_dir.rglob("*.py") if re.search(r"structure_bars|require_structure|TICK_MID",
                                                                     f.read_text())]
    assert offenders == []


def test_signal_contract_requires_structure_extremes():
    import json
    schema = json.loads((ROOT / "docs" / "architecture" / "schemas" / "cbr-signal.v1.schema.json").read_text())
    assert schema["properties"]["extremes_source"]["enum"] == ["TICK_MID"]
    assert schema["properties"]["stop_rule"]["properties"]["extension_extreme_source"]["enum"] == ["TICK_MID"]
    assert schema["properties"]["price_role"]["const"] == "STRUCTURE"
