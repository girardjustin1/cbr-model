"""Phase 10 DXY context module (CBR-ACC-010) on synthetic data with known answers."""

import numpy as np
import pandas as pd
import pytest

from cbr.dxy import context as ctxmod

CFG = {"version": "TEST", "timeframes": {"15m": 15, "1h": 60}, "flat_epsilon": 0.0, "max_quote_age_minutes": 10,
       "min_coverage_full": 0.5, "run_minutes": 30, "dx_active_minutes": 15}
# Wednesday 2024-03-20 (EDT): 17:00 New York = 21:00 UTC daily break.
LO, HI = pd.Timestamp("2024-03-20 12:00", tz="UTC"), pd.Timestamp("2024-03-21 00:00", tz="UTC")
VENDOR_GAP = (pd.Timestamp("2024-03-20 14:00", tz="UTC"), pd.Timestamp("2024-03-20 15:00", tz="UTC"))
QUIET = (pd.Timestamp("2024-03-20 22:00", tz="UTC"), pd.Timestamp("2024-03-20 23:00", tz="UTC"))
DX_RANGE = (pd.Timestamp("2018-12-26 01:00", tz="UTC"), pd.Timestamp("2030-01-01", tz="UTC"))


def _dxy() -> pd.DataFrame:
    idx = pd.date_range(LO, HI, freq="1min", inclusive="left")
    rng = np.random.default_rng(7)
    keep = ((idx < VENDOR_GAP[0]) | (idx >= VENDOR_GAP[1])) & ((idx < QUIET[0]) | (idx >= QUIET[1]))
    keep &= ~(idx.hour == 21)                       # daily break
    keep &= ~np.isin(idx.minute, [7, 23, 41]) | (idx.hour != 13)  # thin minutes
    idx = idx[keep]
    opens = 104 + np.cumsum(rng.normal(0, 0.01, len(idx)))
    closes = opens + rng.normal(0, 0.005, len(idx))
    return pd.DataFrame({"open": opens, "close": closes}, index=idx)


def _dx() -> pd.DataFrame:
    idx = pd.date_range(LO, HI, freq="1min", inclusive="left")
    vol = np.where((idx.hour == 21) | ((idx >= QUIET[0]) & (idx < QUIET[1])), 0.0, 5.0)
    return pd.DataFrame({"volume": vol, "open": 104.0, "close": 104.1}, index=idx)


def _grid(start="2024-03-20 12:00", end="2024-03-21 00:00", freq="1min"):
    return pd.date_range(pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC"), freq=freq)


def _build(dxy=None, dx="default", grid=None, hindsight=True):
    dx = _dx() if isinstance(dx, str) else dx
    return ctxmod.build_context(_dxy() if dxy is None else dxy, _grid() if grid is None else grid, (LO, HI),
                                dx=dx, dx_range=DX_RANGE if dx is not None else None, cfg=CFG, hindsight=hindsight)


def test_rejects_non_utc_inputs():
    dxy = _dxy()
    with pytest.raises(ValueError):
        ctxmod.build_context(dxy.tz_localize(None), _grid(), (LO, HI), cfg=CFG)
    with pytest.raises(ValueError):
        ctxmod.build_context(dxy.tz_convert("America/New_York"), _grid(), (LO, HI), cfg=CFG)
    with pytest.raises(ValueError):
        ctxmod.build_context(dxy, _grid().tz_localize(None), (LO, HI), cfg=CFG)


def test_truncation_equivalence_every_minute():
    full = _build()
    dxy, dx = _dxy(), _dx()
    cols = ctxmod.causal_columns(full)
    for t in _grid("2024-03-20 12:00", "2024-03-21 00:00", "1min")[::7]:
        known = ctxmod.build_context(dxy[dxy.index + pd.Timedelta(minutes=1) <= t], pd.DatetimeIndex([t]), (LO, HI),
                                     dx=dx[dx.index + pd.Timedelta(minutes=1) <= t], dx_range=DX_RANGE, cfg=CFG,
                                     hindsight=False)
        pd.testing.assert_frame_equal(known[cols], full.loc[[t], cols], check_dtype=False)


def test_future_mutation_does_not_change_the_past():
    t = pd.Timestamp("2024-03-20 14:40", tz="UTC")
    base = _build(grid=pd.DatetimeIndex([t]), hindsight=False)
    dxy, dx = _dxy(), _dx()
    future = dxy.index + pd.Timedelta(minutes=1) > t
    dxy.loc[future, ["open", "close"]] *= 1.05
    dxy = dxy.drop(dxy.index[future][::3])
    dx.loc[dx.index + pd.Timedelta(minutes=1) > t, "volume"] = 0.0
    mutated = _build(dxy=dxy, dx=dx, grid=pd.DatetimeIndex([t]), hindsight=False)
    pd.testing.assert_frame_equal(base, mutated)


def test_vendor_gap_is_missing_not_forward_filled():
    c = _build()
    at = lambda s: c.loc[pd.Timestamp(f"2024-03-20 {s}", tz="UTC")]
    early = at("14:05")                          # 5 min into the gap: causally indistinguishable from thin quoting
    assert early["dxy_available"] and early["dxy_confidence"] == "REDUCED"
    assert early["dxy_15m_forming_state"] == "NO_QUOTES" and pd.isna(early["dxy_15m_forming_direction"])
    stale = at("14:20")                          # quote never carried beyond max age
    assert not stale["dxy_available"] and np.isnan(stale["dxy_close"]) and "DXY_QUOTE_STALE" in stale["dxy_reason_codes"]
    fired = at("14:40")                          # run >= 30 min with >= 15 active DX minutes -> causal flag
    assert fired["dxy_1h_forming_state"] == "VENDOR_MISSING"     # partial hour with quotes before the gap
    assert pd.isna(fired["dxy_1h_forming_direction"]) and np.isnan(fired["dxy_1h_forming_move"])
    after = at("15:05")
    assert after["dxy_1h_last_state"] == "VENDOR_MISSING" and after["dxy_1h_last_confidence"] == "UNAVAILABLE"
    assert at("14:30")["dq_hindsight_vendor_gap"] and at("14:01")["dq_hindsight_vendor_gap"]
    assert at("14:05")["dq_hindsight_1h_forming_vendor_gap"]      # hindsight knows; causal fields don't
    assert not at("13:30")["dq_hindsight_vendor_gap"]


def test_hindsight_fields_do_not_touch_causal_fields():
    with_mask, without = _build(), _build(hindsight=False)
    pd.testing.assert_frame_equal(with_mask[ctxmod.causal_columns(with_mask)], without)


def test_dx_never_substitutes_values():
    base = _build()
    dx = _dx()
    dx[["open", "close"]] = 999.0                # DX prices must be irrelevant
    pd.testing.assert_frame_equal(base, _build(dx=dx))
    no_dx = _build(dx=None, hindsight=False)
    for col in ("dxy_close", "dxy_15m_last_move", "dxy_1h_forming_move"):
        a, b = base[col], no_dx[col]
        assert ((a == b) | a.isna()).all()       # with DX a value can only disappear, never appear or change


def test_session_closure_vs_unscheduled_no_quotes():
    c = _build()
    brk = c.loc[pd.Timestamp("2024-03-20 22:00", tz="UTC")]
    assert brk["dxy_1h_last_state"] == "CLOSED_SCHEDULE"          # 21:00-22:00 UTC = 17:00-18:00 New York
    quiet = c.loc[pd.Timestamp("2024-03-20 23:00", tz="UTC")]
    assert quiet["dxy_1h_last_state"] == "NO_QUOTES"               # no quotes, DX idle, not on the schedule
    assert quiet["dxy_1h_last_confidence"] == "UNAVAILABLE"


def test_direction_move_and_coverage_use_only_rows_inside_the_window():
    dxy = _dxy()
    t = pd.Timestamp("2024-03-20 13:15", tz="UTC")
    row = _build(grid=pd.DatetimeIndex([t])).iloc[0]
    w = dxy[(dxy.index >= pd.Timestamp("2024-03-20 13:00", tz="UTC")) & (dxy.index < t)]
    move = w["close"].iloc[-1] - w["open"].iloc[0]
    assert row["dxy_15m_last_move"] == pytest.approx(move)
    assert row["dxy_15m_last_direction"] == ("UP" if move > 0 else "DOWN" if move < 0 else "FLAT")
    assert row["dxy_15m_last_rows"] == 14 and row["dxy_15m_last_coverage"] == pytest.approx(14 / 15)
    assert row["dxy_15m_last_state"] == "OK" and row["dxy_15m_last_confidence"] == "FULL"


def test_low_coverage_and_unverified_reference():
    dxy = _dxy()
    sparse = dxy.drop(dxy[(dxy.index >= pd.Timestamp("2024-03-20 16:00", tz="UTC"))
                          & (dxy.index < pd.Timestamp("2024-03-20 16:15", tz="UTC"))].index[1:12])
    row = _build(dxy=sparse, grid=pd.DatetimeIndex([pd.Timestamp("2024-03-20 16:15", tz="UTC")])).iloc[0]
    assert row["dxy_15m_last_state"] == "LOW_COVERAGE" and row["dxy_15m_last_confidence"] == "REDUCED"
    gap = dxy[(dxy.index >= pd.Timestamp("2024-03-20 16:15", tz="UTC"))
              & (dxy.index < pd.Timestamp("2024-03-20 16:45", tz="UTC"))].index      # 30-min hole, 30/60 quoted
    no_ref = ctxmod.build_context(dxy.drop(gap), pd.DatetimeIndex([pd.Timestamp("2024-03-20 17:00", tz="UTC")]), (LO, HI),
                                  dx=_dx(), dx_range=(pd.Timestamp("2025-01-01", tz="UTC"),
                                                      pd.Timestamp("2026-01-01", tz="UTC")), cfg=CFG).iloc[0]
    assert no_ref["dxy_1h_last_state"] == "UNVERIFIED_GAP" and no_ref["dxy_1h_last_confidence"] == "REDUCED"
    assert "DX_REFERENCE_UNAVAILABLE" in no_ref["dxy_reason_codes"]


def test_sub_minute_grid_uses_only_closed_minutes():
    t = pd.Timestamp("2024-03-20 13:30:35", tz="UTC")
    row = _build(grid=pd.DatetimeIndex([t])).iloc[0]
    assert row["dxy_quote_close_utc"] == pd.Timestamp("2024-03-20 13:30", tz="UTC")
    assert row["dxy_15m_forming_open_utc"] == pd.Timestamp("2024-03-20 13:30", tz="UTC")
    assert row["dxy_15m_forming_elapsed_min"] == 0 and row["dxy_15m_forming_state"] == "NO_ELAPSED_TIME"


def test_not_loaded_is_distinct_from_no_quotes_and_output_is_deterministic():
    row = _build(grid=pd.DatetimeIndex([LO + pd.Timedelta(minutes=5)])).iloc[0]
    assert row["dxy_1h_last_state"] == "NOT_LOADED"
    assert ctxmod.context_hash(_build()) == ctxmod.context_hash(_build())


def test_timestamps_stay_utc_even_without_any_quotes():
    empty = _dxy().iloc[:0]
    c = ctxmod.build_context(empty, _grid("2024-03-20 13:00", "2024-03-20 14:00"), (LO, HI), cfg=CFG)
    for col in [x for x in c.columns if x.endswith("_utc")]:
        assert str(c[col].dt.tz) == "UTC"
    assert str(c.index.tz) == "UTC"


def test_reference_unavailable_is_visible_at_every_decision_time_without_dx_coverage():
    c = ctxmod.build_context(_dxy(), _grid("2024-03-20 23:00", "2024-03-21 00:00"), (LO, HI), dx=_dx(),
                             dx_range=(pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
                             cfg=CFG)
    assert c["dxy_reason_codes"].str.contains("DX_REFERENCE_UNAVAILABLE").all()
    assert not _build()["dxy_reason_codes"].str.contains("DX_REFERENCE_UNAVAILABLE").any()
