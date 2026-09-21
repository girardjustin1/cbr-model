"""Phase 15A protocol freeze and 2022 completeness gate (owner ruling D42 §9-11). Offline: no network, no outcome."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pandas as pd

from cbr.data import phase15a_gate as gate
from cbr.engine import phase15a_protocol as protocol


def test_the_protocol_is_frozen_and_has_not_drifted():
    """D42 §11: the document and the specs it declares are pinned before any signal is generated."""
    assert protocol.FROZEN_PROTOCOL_HASH == protocol.protocol_hash()
    d = protocol.drift()
    assert not d.any(), f"protocol drift: {d}"


def test_the_frozen_span_is_2022_only():
    assert protocol.PILOT_SPAN == ("2022-01-01", "2022-12-31")
    assert gate.SPAN == (date(2022, 1, 1), date(2022, 12, 31))


def test_provenance_carries_the_failed_parity_verdict_and_pilot_status():
    """A pilot result may never present itself as a parity pass or a validated edge."""
    p = protocol.provenance()
    assert p["result_status"] == "DEVELOPMENT_PILOT"
    assert "VALIDATED EDGE" not in p["permitted_verdicts"]
    assert p["permitted_verdicts"] == ["PROMISING", "INCONCLUSIVE", "NEGATIVE"]
    assert p["baseline_provenance"]["parity_verdict"] == "FAIL"


def test_every_requested_open_hour_is_accounted_for(tmp_path, monkeypatch):
    """D42 §9: successful + unexpected gaps + unresolved failures == requested open hours, exactly."""
    monkeypatch.setattr(gate.dk, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(gate.dk, "RAW", tmp_path / "raw")
    monkeypatch.setattr(gate.dk, "MANIFEST", tmp_path / "raw" / "manifest.json")
    monkeypatch.setattr(gate.sa, "BLOCKS", tmp_path / "blocks")
    out = gate.gate(span=(date(2022, 3, 1), date(2022, 3, 31)))
    assert out["hours_accounted"] is True
    assert (out["successful_hours"] + out["unexpected_gaps"] + out["unresolved_failures"]
            == out["requested_open_hours"])
    # Nothing downloaded: every open hour is an unresolved failure, and none has vanished.
    assert out["unresolved_failures"] == out["requested_open_hours"]
    assert out["verdict"] == "INCOMPLETE"


def test_a_missing_open_hour_is_never_silently_dropped(tmp_path, monkeypatch):
    """One open hour present, the rest absent: the absent ones are listed, not merely counted."""
    cache = tmp_path / "cache" / "xauusd"
    cache.mkdir(parents=True)
    monkeypatch.setattr(gate.dk, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(gate.dk, "RAW", tmp_path / "raw")
    monkeypatch.setattr(gate.dk, "MANIFEST", tmp_path / "raw" / "manifest.json")
    monkeypatch.setattr(gate.sa, "BLOCKS", tmp_path / "blocks")
    day = date(2022, 3, 8)
    (cache / f"{day.isoformat()}_10.bi5").write_bytes(b"data")
    (cache / f"{day.isoformat()}_11.bi5").write_bytes(b"")          # a 404 at an open hour
    out = gate.gate(span=(day, day))
    assert out["successful_hours"] == 1
    assert out["unexpected_gaps"] == 1
    assert out["unexpected_gap_hours"] == [datetime(2022, 3, 8, 11, tzinfo=UTC).isoformat()]
    assert len(out["unresolved_hours"]) == out["unresolved_failures"] > 0
    assert out["hours_accounted"] is True


def test_a_scheduled_closure_never_pads_the_open_hour_accounting(tmp_path, monkeypatch):
    """A cached empty file at a calendar-closed hour is a closure, not a successful hour and not a gap."""
    cache = tmp_path / "cache" / "xauusd"
    cache.mkdir(parents=True)
    monkeypatch.setattr(gate.dk, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(gate.dk, "RAW", tmp_path / "raw")
    monkeypatch.setattr(gate.dk, "MANIFEST", tmp_path / "raw" / "manifest.json")
    monkeypatch.setattr(gate.sa, "BLOCKS", tmp_path / "blocks")
    day = date(2022, 3, 8)
    closed = [h for h in range(24)
              if gate.expected_closed(pd.Timestamp(datetime(day.year, day.month, day.day, h, tzinfo=UTC)))]
    assert closed, "the canonical calendar must close at least one hour of a weekday"
    for h in closed:
        (cache / f"{day.isoformat()}_{h:02d}.bi5").write_bytes(b"")
    out = gate.gate(span=(day, day))
    assert out["cached_scheduled_closure_hours"] == len(closed)
    assert out["successful_hours"] == 0
    assert out["unexpected_gaps"] == 0
    assert out["hours_accounted"] is True


def test_the_gate_blocks_performance_until_every_month_is_complete(tmp_path, monkeypatch):
    """D42 §10: an incomplete span may never be measured, even if every downloaded hour succeeded."""
    monkeypatch.setattr(gate.dk, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(gate.dk, "RAW", tmp_path / "raw")
    monkeypatch.setattr(gate.dk, "MANIFEST", tmp_path / "raw" / "manifest.json")
    blocks = tmp_path / "blocks"
    blocks.mkdir()
    monkeypatch.setattr(gate.sa, "BLOCKS", blocks)
    for m in range(1, 13):
        (blocks / f"xauusd_2022-{m:02d}.json").write_text(json.dumps(
            {"complete": m < 12, "retry_count": 1, "http_429": 0, "http_5xx": 2}))
    out = gate.gate()
    assert out["blocks_complete"] == 11
    assert out["retry_count"] == 12 and out["http_5xx"] == 24
    assert out["complete"] is False and out["verdict"] == "INCOMPLETE"
