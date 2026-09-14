"""Phase 9 exception register and verdict rule (CBR-ACC-009 v2.1, owner ruling D12). Needs no market data."""

from cbr.data import phase9_acceptance as acc

CRITERIA = [f"AC-{i:02d}" for i in range(1, 11)] + ["AC-11A"]
HISTORY = {"xauusd": {"days_present": 16, "trading_days_required": 2192}}
DAY = "dollaridxusd/2020-03-09"
RULED = {"id": f"AC-07/unexpected_gaps/{DAY}", "class": "DATA_ERROR", "cause_status": "UNKNOWN", "explanation": "x",
         "owner_ruling": "D12-1", "handling": "MISSING", "detector": "DXY_CFD_MISSING_WHILE_DX_ACTIVE",
         "ruled_interval_utc": ["2020-03-09T20:00:00+00:00", "2020-03-09T21:00:00+00:00"]}
FLAG = {"reason_code": "DXY_CFD_MISSING_WHILE_DX_ACTIVE", "start": "2020-03-09 20:00:00+00:00",
        "end": "2020-03-09 21:00:00+00:00"}


def _run(monkeypatch, entries, detections):
    monkeypatch.setattr(acc, "_register", lambda: {"exceptions": entries})
    failures = [{"id": e["id"], "criterion": e["id"].split("/")[0], "observed": None, "expected": None} for e in entries]
    failures, meta = acc.classify(failures, detections)
    return acc.verdict(failures, CRITERIA, HISTORY, meta["register_errors"])


def test_committed_register_is_well_formed():
    reg = acc._register()
    assert reg["exceptions"] and acc.register_errors(reg) == []
    ids = [e["id"] for e in reg["exceptions"]]
    assert len(ids) == len(set(ids))


def test_ruled_data_error_is_non_blocking_only_when_detected(monkeypatch):
    detected = _run(monkeypatch, [RULED], {DAY: [FLAG]})
    assert detected["verdict"] == "PASS WITH CONCERNS" and detected["criteria_status"]["AC-07"] == "MET WITH CONCERNS"
    assert detected["concerns"] == [RULED["id"]]                     # preserved as a concern, not dropped
    undetected = _run(monkeypatch, [RULED], {DAY: []})
    assert undetected["verdict"] == "FAIL" and undetected["blocking"] == [RULED["id"]]
    elsewhere = {DAY: [{**FLAG, "start": "2020-03-09 22:00:00+00:00", "end": "2020-03-09 23:00:00+00:00"}]}
    assert _run(monkeypatch, [RULED], elsewhere)["verdict"] == "FAIL"   # flag must intersect the ruled interval


def test_unruled_blocking_classes_and_register_errors_fail(monkeypatch):
    unruled = {k: v for k, v in RULED.items() if k in ("id", "class", "cause_status", "explanation")}
    assert _run(monkeypatch, [unruled], {DAY: [FLAG]})["verdict"] == "FAIL"
    missing_cause = {**unruled, "class": "EXPECTED_FEED_DIFFERENCE", "cause_status": None}
    assert _run(monkeypatch, [missing_cause], {})["verdict"] == "FAIL"
    ok = {**missing_cause, "class": "REFERENCE_UNAVAILABLE", "cause_status": "ESTABLISHED"}
    assert _run(monkeypatch, [ok], {})["verdict"] == "PASS WITH CONCERNS"
