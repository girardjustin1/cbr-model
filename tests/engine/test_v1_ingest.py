"""V-1 ingestion readiness (D20-10) on synthetic files in a temp dir: never real exports, never course scoring."""

import pandas as pd
import pytest

from cbr.engine import parity, v1_ingest

T = lambda s: pd.Timestamp(s, tz="UTC")


def _write(path, start, end, *, drop=None, iso=False):
    idx = pd.date_range(T(start), T(end), freq="1min", inclusive="left")
    if drop is not None:
        idx = idx[(idx < T(drop[0])) | (idx >= T(drop[1]))]
    time = [t.isoformat() for t in idx] if iso else (idx - T("1970-01-01")) // pd.Timedelta("1s")
    pd.DataFrame({"time": time, "open": 1.0, "high": 1.5, "low": 0.5, "close": 1.2}).to_csv(path, index=False)


@pytest.fixture
def v1dir(tmp_path, monkeypatch):
    monkeypatch.setattr(v1_ingest, "V1_DIR", tmp_path)
    monkeypatch.setattr(v1_ingest, "SCREENSHOT_DIR", tmp_path / "screenshots")
    monkeypatch.setattr(v1_ingest, "ROOT", tmp_path)
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


def test_inspect_exports_rejects_other_symbols_and_short_1m_history(tmp_path):
    _write(tmp_path / "FX_XAUUSD, 1.csv", "2025-10-20 00:00", "2025-11-12 00:00")          # right span, wrong symbol
    _write(tmp_path / "FOREXCOM_XAUUSD, 1.csv", "2026-09-08 08:00", "2026-09-15 12:00")    # right symbol, short history
    _write(tmp_path / "FOREXCOM_XAUUSD, 60.csv", "2025-10-20 00:00", "2025-11-12 00:00")   # covers, but not 1m
    out = v1_ingest.inspect_exports(tmp_path)
    assert out["usable_as_v1"] == [] and out["verdict"].startswith("DATA_LIMITATION")
    by = {r["file"]: r for r in out["exports"]}
    assert by["FX_XAUUSD, 1.csv"]["symbol"] == "FX:XAUUSD" and not by["FX_XAUUSD, 1.csv"]["is_required_symbol"]
    assert not any(by["FOREXCOM_XAUUSD, 1.csv"]["covers_v1_windows"].values())
    _write(tmp_path / "FOREXCOM_XAUUSD, 1.csv", "2025-10-20 00:00", "2025-11-12 00:00")
    assert v1_ingest.inspect_exports(tmp_path)["usable_as_v1"] == ["FOREXCOM_XAUUSD, 1.csv"]
