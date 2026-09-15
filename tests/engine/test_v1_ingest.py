"""V-1 ingestion readiness (D20-10) on synthetic files in a temp dir: never real exports, never course scoring."""

import numpy as np
import pandas as pd
import pytest

from cbr.engine import parity, v1_ingest

T = lambda s: pd.Timestamp(s, tz="UTC")


def _write(path, start, end, *, drop=None, iso=False, freq="1min"):
    idx = pd.date_range(T(start), T(end), freq=freq, inclusive="left")
    if drop is not None:
        idx = idx[(idx < T(drop[0])) | (idx >= T(drop[1]))]
    time = [t.isoformat() for t in idx] if iso else (idx - T("1970-01-01")) // pd.Timedelta("1s")
    pd.DataFrame({"time": time, "open": 1.0, "high": 1.5, "low": 0.5, "close": 1.2}).to_csv(path, index=False)


@pytest.fixture
def v1dir(tmp_path, monkeypatch):
    monkeypatch.setattr(v1_ingest, "V1_DIR", tmp_path)
    monkeypatch.setattr(v1_ingest, "SCREENSHOT_DIR", tmp_path / "screenshots")
    monkeypatch.setattr(v1_ingest, "ROOT", tmp_path)
    monkeypatch.setattr(v1_ingest, "PROVENANCE", tmp_path / "v1_provenance.json")
    return tmp_path


def test_absent_files_report_waiting_for_owner_data(v1dir):
    st = v1_ingest.status()
    assert st["state"] == v1_ingest.WAITING and st["missing_files"] == parity.V1_FILES
    with pytest.raises(SystemExit, match=v1_ingest.WAITING):
        v1_ingest.calibrate()


def test_complete_valid_files_and_screenshots_are_recognised(v1dir):
    for name, (a, b, _) in v1_ingest.WINDOWS.items():
        _write(v1dir / name, str(a.tz_localize(None)), str(b.tz_localize(None)))
    shots = v1dir / "screenshots"
    shots.mkdir()
    (shots / "forexcom_xauusd_symbol_info.png").write_bytes(b"\x89PNG")
    st = v1_ingest.status()
    assert st["state"] == v1_ingest.WAITING and not st["screenshots"]["complete"]      # timezone screenshot missing
    (shots / "chart_timezone_utc.png").write_bytes(b"\x89PNG")
    st = v1_ingest.status()
    assert all(f["valid"] for f in st["files"].values()), st["files"]
    assert st["state"] in ("V1_READY_FOR_CALIBRATION", "V1_WAITING_FOR_DUKASCOPY_CALIBRATION_DAYS")
    assert all(len(f["sha256"]) == 64 for f in st["files"].values())


def test_coverage_gaps_and_naive_iso_times_are_flagged(tmp_path):
    a, b = T("2025-10-22 00:00"), T("2025-10-23 00:00")
    gap = tmp_path / "gap.csv"
    _write(gap, "2025-10-22 00:00", "2025-10-23 00:00", drop=("2025-10-22 10:00", "2025-10-22 10:20"))
    out = v1_ingest.validate_file(gap, a, b)
    assert not out["valid"] and out["missing_open_minutes"] == 20
    short = tmp_path / "short.csv"
    _write(short, "2025-10-22 06:00", "2025-10-23 00:00")
    assert any("does not cover" in x for x in v1_ingest.validate_file(short, a, b)["problems"])
    naive = tmp_path / "naive.csv"
    pd.DataFrame({"time": ["2025-10-22T00:00:00"], "open": [1], "high": [1], "low": [1], "close": [1]}).to_csv(naive, index=False)
    assert "unreadable" in v1_ingest.validate_file(naive, a, b)["problems"][0]
    iso = tmp_path / "iso.csv"
    _write(iso, "2025-10-22 00:00", "2025-10-23 00:00", iso=True)
    assert v1_ingest.validate_file(iso, a, b)["valid"]


def test_calibration_reads_only_calibration_files():
    import inspect

    src = inspect.getsource(v1_ingest.calibrate)
    assert 'kind == "calibration"' in src and "CX-" not in src
    assert set(v1_ingest.WINDOWS) == set(parity.V1_FILES)


def test_inspect_exports_classifies_symbol_timeframe_and_coverage(tmp_path, v1dir):
    src = tmp_path / "exports"
    src.mkdir()
    _write(src / "FX_XAUUSD, 1.csv", "2025-10-20 00:00", "2025-11-12 00:00")          # right span, wrong symbol
    _write(src / "FOREXCOM_XAUUSD, 1.csv", "2026-09-08 08:15", "2026-09-15 12:00")    # right symbol, short history
    _write(src / "FOREXCOM_XAUUSD, 60.csv", "2025-10-20 00:00", "2025-11-12 00:00", freq="1h")
    _write(src / "TVC_DXY, 1.csv", "2026-09-08 00:00", "2026-09-09 00:00")
    out = v1_ingest.inspect_exports(src)
    by = {r["file"]: r for r in out["exports"]}
    fx = by["FX_XAUUSD, 1.csv"]
    assert fx["tradingview_symbol"] == "FX:XAUUSD" and fx["exchange"] == "FX" and fx["timeframe"] == "1"
    assert not fx["v1_eligible"] and fx["classification"] == "REFERENCE_ONLY"
    assert all(c["coverage"] == "FULL" for c in fx["v1_windows"].values())
    assert fx["timestamp_basis"].startswith("unix epoch seconds") and fx["ohlc_columns"]
    short = by["FOREXCOM_XAUUSD, 1.csv"]
    assert any("ONE_MINUTE_HISTORY_INSUFFICIENT" in r for r in short["reasons"])
    assert short["one_minute_days_short"]["v1_cal_2025-11-11.csv"] == 301
    h1 = by["FOREXCOM_XAUUSD, 60.csv"]
    assert h1["v1_windows"]["v1_CX-LT1-1.csv"]["coverage"] == "FULL" and "TRADINGVIEW_REFERENCE_FIXTURE" in h1["classification"]
    assert by["TVC_DXY, 1.csv"]["instrument"] == "DXY" and not by["TVC_DXY, 1.csv"]["v1_eligible"]
    assert out["usable_as_v1"] == [] and out["state"] == "V1_ONE_MINUTE_HISTORY_INSUFFICIENT"


def test_v1_state_symbol_mismatch_partial_and_waiting(tmp_path, v1dir):
    only_fx = tmp_path / "fx"
    only_fx.mkdir()
    _write(only_fx / "FX_XAUUSD, 1.csv", "2026-09-08 08:15", "2026-09-15 12:00")
    assert v1_ingest.inspect_exports(only_fx)["state"] == "V1_SYMBOL_MISMATCH"
    empty = tmp_path / "empty"
    empty.mkdir()
    assert v1_ingest.inspect_exports(empty)["state"] == v1_ingest.WAITING
    part = tmp_path / "part"
    part.mkdir()
    _write(part / "FOREXCOM_XAUUSD, 1.csv", "2025-10-21 00:00", "2025-10-25 00:00")        # covers 10/22 and TE1-1 only
    assert v1_ingest.inspect_exports(part)["state"] == "V1_PARTIALLY_READY"


def test_slicing_preserves_original_records_hashes_and_refuses_wrong_symbol(tmp_path, v1dir):
    src = tmp_path / "src"
    src.mkdir()
    wrong = src / "FX_XAUUSD, 1.csv"
    _write(wrong, "2025-10-20 00:00", "2025-11-12 00:00")
    with pytest.raises(SystemExit, match="SYMBOL_MISMATCH"):
        v1_ingest.derive_slices(wrong)
    good = src / "FOREXCOM_XAUUSD, 1.csv"
    _write(good, "2025-10-21 00:00", "2025-10-25 00:00")
    before = good.read_bytes()
    written = v1_ingest.derive_slices(good)
    assert set(written) == {"v1_CX-TE1-1.csv", "v1_cal_2025-10-22.csv"} and good.read_bytes() == before
    rec = written["v1_cal_2025-10-22.csv"]
    assert rec["rows"] == 1440 and len(rec["slice_sha256"]) == 64
    assert v1_ingest.validate_file(v1dir / "v1_cal_2025-10-22.csv", T("2025-10-22"), T("2025-10-23"))["valid"]
    assert v1_ingest.derive_slices(good) == written                                          # deterministic rerun
    (v1dir / "v1_CX-TE1-1.csv").write_text("time,open,high,low,close\n")
    with pytest.raises(SystemExit, match="not overwritten"):
        v1_ingest.derive_slices(good)


def _pair(offsets=(0.40, 0.45, 0.35, 0.40), lag=0):
    rng = np.random.default_rng(3)
    idx = pd.date_range(T("2025-10-22 00:00"), T("2025-10-23 00:00"), freq="1min", inclusive="left")
    walk = 4000 + np.cumsum(rng.normal(0, 0.4, len(idx)))
    dk = pd.DataFrame({"open": walk, "high": walk + 0.5, "low": walk - 0.5, "close": walk + 0.1}, index=idx)
    noise = rng.uniform(-0.02, 0.02, (len(idx), 4))
    fx = pd.DataFrame({f: dk[f] + o + noise[:, i] for i, (f, o) in enumerate(zip(("open", "high", "low", "close"), offsets))},
                      index=idx)
    if lag:
        fx = fx.shift(lag).dropna()
    return fx.drop(fx.index[600:610]), dk.drop(dk.index[900:903])


def test_calibration_measurements_report_fields_missing_sources_blocks_and_regimes():
    fx, dk = _pair()
    method = parity.load_tolerances()["method"]
    rep = v1_ingest.run_calibration(fx, dk, [(T("2025-10-22"), T("2025-10-23"))], method)
    m, x = rep["measurements"], rep["result"]
    assert rep["status"].startswith("PROPOSED") and x["zero_lag_confirmed"] and x["tau_price"] is not None
    assert m["scheduled_open_minutes"] == 1380 and m["missing_minutes_forexcom"] == 10 and m["missing_minutes_dukascopy"] == 3
    assert m["per_field"]["open"]["offset_median"] == pytest.approx(0.40, abs=0.01)
    assert m["per_field"]["high"]["offset_median"] == pytest.approx(0.45, abs=0.01)
    for f in v1_ingest.FIELDS:
        assert {"p50", "p90", "p95", "p99", "max"} <= set(m["per_field"][f]["residual_after_delta"])
    assert set(m["time_blocks"]) == {b[0] for b in v1_ingest.TIME_BLOCKS} and list(m["per_day"]) == ["2025-10-22"]
    assert set(m["volatility_regimes_by_dukascopy_1m_range"]) == {"low", "mid", "high"}
    assert m["stability"]["ohlc_field_max_deviation"] == pytest.approx(0.05, abs=0.01)
    assert len(m["intraday_hourly_close_offset_median"]) == 23                                # daily break hour absent
    assert "Per OHLC field" in v1_ingest._render(rep)


def test_calibration_stops_without_zero_lag():
    fx, dk = _pair(lag=1)
    rep = v1_ingest.run_calibration(fx, dk, [(T("2025-10-22"), T("2025-10-23"))], parity.load_tolerances()["method"])
    assert rep["status"].startswith("STOPPED") and rep["result"]["tau_price"] is None and rep["result"]["feed_near"] is None


def test_inspection_report_has_gold_and_dxy_matrices(tmp_path, v1dir, monkeypatch):
    src = tmp_path / "exp"
    src.mkdir()
    _write(src / "FX_XAUUSD, 1.csv", "2026-09-08 08:15", "2026-09-09 00:00")
    _write(src / "TVC_DXY, 60.csv", "2025-09-08 00:00", "2025-11-20 00:00", freq="1h")
    monkeypatch.setattr(v1_ingest, "INSPECTION_JSON", tmp_path / "i.json")
    monkeypatch.setattr(v1_ingest, "INSPECTION_MD", tmp_path / "i.md")
    v1_ingest.write_inspection_report(src)
    md = (tmp_path / "i.md").read_text()
    assert "## Gold (XAUUSD)" in md and "## DXY (informational)" in md and "V1_SYMBOL_MISMATCH" in md
    assert "ONE_MINUTE_HISTORY_INSUFFICIENT" in md and "CAL 10/22" in md
