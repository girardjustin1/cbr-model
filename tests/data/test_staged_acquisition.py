"""Staged acquisition behaviour (owner ruling D41 §3-7). Offline: the network is never touched."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from cbr.data import staged_acquisition as sa


def test_scheduled_closures_are_never_requested():
    """D41 §6: an hour the canonical calendar calls closed is manifested, not fetched."""
    request, skipped = sa.block_hours("2019-06")
    assert skipped, "June 2019 must contain scheduled closures"
    assert all(sa.scheduled_closed(h) for h in skipped)
    assert not any(sa.scheduled_closed(h) for h in request)


def test_no_uncertain_hour_is_skipped():
    """Only definite closures are skipped; every other weekday hour is requested."""
    request, skipped = sa.block_hours("2020-03")
    hours = {h.isoformat() for h in request} | {h.isoformat() for h in skipped}
    weekday_hours = sum(24 for d in range(1, 32)
                        if datetime(2020, 3, d, tzinfo=UTC).weekday() < 5) if True else 0
    assert len(hours) == weekday_hours


def test_the_plan_reports_the_request_budget_without_network():
    p = sa.plan(2018, 2024)
    assert p["blocks"] == 84
    assert p["naive_hours"] == p["request_hours"] + p["scheduled_closure_hours_avoided"]
    assert 0 < p["saved_fraction"] < 0.2
    assert p["request_hours"] > 40_000


def test_a_cached_hour_is_never_refetched(tmp_path, monkeypatch):
    monkeypatch.setattr(sa.dk, "CACHE", tmp_path)
    hour = datetime(2018, 5, 2, 10, tzinfo=UTC)
    target = sa._cached("xauusd", hour)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"cached-bytes")

    def explode(*_a, **_k):
        raise AssertionError("resume must not issue a request for a cached hour")

    monkeypatch.setattr(sa.urllib.request, "urlopen", explode)
    out = sa.fetch_hour("xauusd", hour)
    assert out.state == "DATA" and out.bytes == len(b"cached-bytes") and out.attempts == 0


def test_a_404_is_recorded_as_a_legitimate_empty_hour(tmp_path, monkeypatch):
    import urllib.error
    monkeypatch.setattr(sa.dk, "CACHE", tmp_path)

    def not_found(*_a, **_k):
        raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)

    monkeypatch.setattr(sa.urllib.request, "urlopen", not_found)
    out = sa.fetch_hour("xauusd", datetime(2018, 5, 2, 11, tzinfo=UTC), sleep=lambda _s: None)
    assert out.state == "EMPTY" and out.bytes == 0
    assert sa._cached("xauusd", datetime(2018, 5, 2, 11, tzinfo=UTC)).exists()   # cached so it is never refetched


def test_a_429_triggers_the_long_cooldown_and_is_counted(tmp_path, monkeypatch):
    import urllib.error
    monkeypatch.setattr(sa.dk, "CACHE", tmp_path)
    waits = []
    calls = {"n": 0}

    def limited(*_a, **_k):
        calls["n"] += 1
        raise urllib.error.HTTPError("u", 429, "Too Many Requests", {}, None)

    monkeypatch.setattr(sa.urllib.request, "urlopen", limited)
    out = sa.fetch_hour("xauusd", datetime(2018, 5, 2, 12, tzinfo=UTC), sleep=waits.append)
    assert out.state == "FAILED" and out.http_429 == sa.MAX_ATTEMPTS
    assert calls["n"] == sa.MAX_ATTEMPTS                       # bounded retries
    assert all(w >= sa.RATE_LIMIT_COOLDOWN_SEC for w in waits)  # long cooldown, not a short retry
    assert len(set(waits)) > 1                                  # jittered


def test_a_5xx_uses_exponential_backoff(tmp_path, monkeypatch):
    import urllib.error
    monkeypatch.setattr(sa.dk, "CACHE", tmp_path)
    waits = []
    monkeypatch.setattr(sa.urllib.request, "urlopen",
                        lambda *_a, **_k: (_ for _ in ()).throw(urllib.error.HTTPError("u", 503, "x", {}, None)))
    out = sa.fetch_hour("xauusd", datetime(2018, 5, 2, 13, tzinfo=UTC), sleep=waits.append)
    assert out.state == "FAILED" and out.http_5xx == sa.MAX_ATTEMPTS
    assert waits[1] > waits[0]                                  # grows with attempts


def test_the_retry_queue_survives_a_restart(tmp_path, monkeypatch):
    monkeypatch.setattr(sa, "RETRY_QUEUE", tmp_path / "retry_queue.json")
    sa._save_queue({"pending": ["2018-05-02T14:00:00+00:00"]})
    assert sa._load_queue()["pending"] == ["2018-05-02T14:00:00+00:00"]
    assert json.loads((tmp_path / "retry_queue.json").read_text())["pending"]


def test_block_manifest_carries_the_required_accounting(tmp_path, monkeypatch):
    monkeypatch.setattr(sa, "BLOCKS", tmp_path)
    stats = sa.BlockStats(block="2018-01", requested_open_hours=10, successful_hours=9,
                          scheduled_closures=3, legitimate_empty_files=1, retry_count=2,
                          http_429=1, http_5xx=0, unresolved_failures=0, bytes=1234)
    body = sa.write_block_manifest(stats, [], "xauusd")
    for field in ("requested_open_hours", "successful_hours", "scheduled_closures", "legitimate_empty_files",
                  "retry_count", "http_429", "http_5xx", "unresolved_failures", "bytes", "manifest_hash"):
        assert field in body
    assert body["complete"] is True


def test_a_block_with_unresolved_hours_is_not_complete():
    stats = sa.BlockStats(block="2018-01", unresolved_failures=1)
    assert not stats.complete()


@pytest.mark.parametrize("block", ["2018-01", "2021-12", "2024-07"])
def test_block_hours_cover_only_weekdays(block):
    request, skipped = sa.block_hours(block)
    for h in request + skipped:
        assert h.weekday() < 5
