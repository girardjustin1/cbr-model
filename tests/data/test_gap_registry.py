"""Unexpected-gap classification (owner ruling D42 §3). Offline: no network, no outcome, nothing interpolated."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from cbr.data import gap_registry as gr
from cbr.data import phase15a_gate as gate


@pytest.fixture
def cache(tmp_path, monkeypatch):
    """An isolated hourly-artefact cache. Writing b'' is exactly what the fetcher stores for a feed 404."""
    root = tmp_path / "cache"
    (root / "xauusd").mkdir(parents=True)
    monkeypatch.setattr(gr.dk, "CACHE", root)
    monkeypatch.setattr(gr, "REGISTRY", tmp_path / "gaps.json")
    return root / "xauusd"


def _day(cache, day: date, data_hours, empty_hours):
    for h in data_hours:
        (cache / f"{day.isoformat()}_{h:02d}.bi5").write_bytes(b"ticks")
    for h in empty_hours:
        (cache / f"{day.isoformat()}_{h:02d}.bi5").write_bytes(b"")


def test_the_trading_day_rolls_at_17_00_new_york():
    """Good Friday's closure starts the evening before, so 2022-04-14 22:00 UTC belongs to the 04-15 session."""
    assert gr.trading_day(datetime(2022, 4, 14, 22, tzinfo=UTC)) == date(2022, 4, 15)
    assert gr.trading_day(datetime(2022, 4, 14, 16, tzinfo=UTC)) == date(2022, 4, 14)
    assert gr.trading_day(datetime(2022, 11, 24, 20, tzinfo=UTC)) == date(2022, 11, 24)   # EST, 15:00 New York


def test_a_holiday_early_close_is_a_data_limitation_and_does_not_block(cache):
    """Thanksgiving 2022: the feed 404s the afternoon hours and the empty run reaches the daily break."""
    day = date(2022, 11, 24)
    _day(cache, day, data_hours=list(range(20)) + [23], empty_hours=[20, 21, 22])
    body = gr.classify([datetime(2022, 11, 24, 20, tzinfo=UTC).isoformat()])
    e = body["entries"][0]
    assert e["classification"] == gr.DATA_LIMITATION
    assert e["blocks"] is False
    assert "Thanksgiving" in e["reason"]
    assert e["evidence"]["artefact_state"] == "FEED_404_EMPTY"
    assert e["evidence"]["run_touches_daily_break"] is True
    assert body["blocking_hours"] == []


def test_a_fully_closed_holiday_classifies_without_touching_the_break(cache):
    """Good Friday: every fetched hour of the day is empty."""
    day = date(2022, 4, 15)
    _day(cache, day, data_hours=[], empty_hours=list(range(21)))
    body = gr.classify([datetime(2022, 4, 15, 10, tzinfo=UTC).isoformat()])
    e = body["entries"][0]
    assert e["classification"] == gr.DATA_LIMITATION
    assert e["evidence"]["whole_fetched_day_empty"] is True
    assert e["evidence"]["hours_with_data_on_day"] == 0


def test_an_ordinary_missing_market_hour_blocks(cache):
    """No holiday, data either side: unexplained missing market-open data stays a DATA_GAP and blocks."""
    day = date(2022, 3, 9)
    _day(cache, day, data_hours=[h for h in range(24) if h != 10], empty_hours=[10])
    body = gr.classify([datetime(2022, 3, 9, 10, tzinfo=UTC).isoformat()])
    e = body["entries"][0]
    assert e["classification"] == gr.DATA_GAP
    assert e["blocks"] is True
    assert body["blocking_hours"] == [e["hour"]]


def test_an_empty_hour_on_a_holiday_that_stands_alone_still_blocks(cache):
    """A holiday date is never enough on its own: an isolated hole with trading either side is not a closure."""
    day = date(2022, 7, 4)
    _day(cache, day, data_hours=[h for h in range(24) if h != 8], empty_hours=[8])
    body = gr.classify([datetime(2022, 7, 4, 8, tzinfo=UTC).isoformat()])
    assert body["entries"][0]["classification"] == gr.DATA_GAP
    assert body["entries"][0]["blocks"] is True


def test_an_unfetched_hour_is_not_loaded_and_blocks(cache):
    body = gr.classify([datetime(2022, 3, 9, 10, tzinfo=UTC).isoformat()])
    e = body["entries"][0]
    assert e["classification"] == gr.NOT_LOADED
    assert e["blocks"] is True


def test_an_unclassified_gap_keeps_the_span_incomplete(cache, monkeypatch):
    """D42 §3: a gap is never resolved by being counted. An absent register entry blocks."""
    gr.classify([])                                       # an empty register
    monkeypatch.setattr(gate.gap_registry, "REGISTRY", gr.REGISTRY)
    s = gr.status([datetime(2022, 3, 9, 10, tzinfo=UTC).isoformat()])
    assert s["resolved"] is False
    assert s["unclassified_hours"] == [datetime(2022, 3, 9, 10, tzinfo=UTC).isoformat()]


def test_every_entry_carries_its_evidence_and_the_register_is_hashed(cache):
    day = date(2022, 11, 24)
    _day(cache, day, data_hours=list(range(20)) + [23], empty_hours=[20, 21, 22])
    body = gr.classify([datetime(2022, 11, 24, 20, tzinfo=UTC).isoformat(),
                        datetime(2022, 11, 24, 21, tzinfo=UTC).isoformat()])
    assert len(body["registry_hash"]) == 64
    for e in body["entries"]:
        assert e["reason"] and e["classified_utc"]
        assert set(e["evidence"]) >= {"artefact_bytes", "artefact_state", "holiday", "trading_day",
                                      "contiguous_empty_run_hours_utc", "empty_hours_on_day"}
        assert e["classification"] in gr.CLASSIFICATIONS
    # The register is deterministic for the same measured inputs.
    assert gr.classify([e["hour"] for e in body["entries"]])["registry_hash"] == body["registry_hash"]
