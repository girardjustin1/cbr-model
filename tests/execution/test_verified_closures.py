"""Verified closure vs true data gap in execution (owner ruling D43 §3, §5-7).

A proven closure holds no executable quote stream, so no fill can have occurred inside it and there is nothing to
call unprovable. An interval the evidence does not establish as closed keeps its D38/D39 unprovable semantics
untouched. Nothing here fabricates a quote or interpolates a price.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from cbr.data import market_closures as mc
from cbr.execution import market_data as md
from cbr.execution import prices as px


@pytest.fixture
def cache(tmp_path, monkeypatch):
    root = tmp_path / "cache"
    (root / "xauusd").mkdir(parents=True)
    monkeypatch.setattr(mc.dk, "CACHE", root)
    monkeypatch.setattr(mc, "REGISTRY", tmp_path / "closures.json")
    return root / "xauusd"


def _hours(cache, day: date, *, data, empty):
    for h in data:
        (cache / f"{day.isoformat()}_{h:02d}.bi5").write_bytes(b"ticks")
    for h in empty:
        (cache / f"{day.isoformat()}_{h:02d}.bi5").write_bytes(b"")


def _quotes(times) -> pd.DataFrame:
    idx = pd.DatetimeIndex(times)
    return pd.DataFrame({"bid": [1990.0] * len(idx), "ask": [1990.4] * len(idx)}, index=idx)


def _prov(missing_days=()):
    return md.TickProvenance(
        instrument="xauusd", requested_window=("", ""), loaded_window=("", ""), tick_count=0,
        source_file_ids=[], source_hashes={}, missing_days=list(missing_days), duplicate_timestamps=0,
        gap_manifest_version=None, day_manifest_sha256=None)


def _classify(start, end, quotes, registry):
    return md.classify_intervals(pd.Timestamp(start), pd.Timestamp(end), quotes, _prov(),
                                 rollover_pre_min=15, rollover_post_min=60, closures=registry)


# ─── A. a verified closure is not an unprovable outcome (D43 §5) ──────────────────────────────────────────────────
def test_a_verified_full_closure_produces_no_gap(cache):
    """Thanksgiving's proven closure: classified, and never handed to the simulator as a gap."""
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    reg = mc.load(mc.build(2022)["year"] and mc.REGISTRY)
    assert reg.closures, "the evidence should establish this closure"

    start, end = pd.Timestamp("2022-11-24 20:00", tz="UTC"), pd.Timestamp("2022-11-24 22:00", tz="UTC")
    gaps, counts = _classify(start, end, _quotes([]), reg)
    assert counts.get(md.VERIFIED_MARKET_DATA_CLOSURE, 0) > 0
    assert md.DATA_GAP not in counts
    assert gaps == [], "a proven closure must not reach the simulator as px.Gap"


def test_no_quote_is_fabricated_inside_a_closure(cache):
    """The clock simply holds no executable event: the quote stream stays empty, not filled in."""
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    mc.build(2022)
    reg = mc.load()
    quotes = _quotes([])
    gaps, _counts = _classify("2022-11-24 20:00", "2022-11-24 21:00", quotes, reg)
    assert len(quotes) == 0 and gaps == []


# ─── B. a true data gap is unchanged (D43 §6) ─────────────────────────────────────────────────────────────────────
def test_an_isolated_missing_active_market_hour_is_still_a_data_gap(cache):
    """No holiday, trading either side: the D38/D39 unprovable protections must be untouched."""
    day = date(2022, 3, 9)
    _hours(cache, day, data=[h for h in range(24) if h != 10], empty=[10])
    mc.build(2022)
    reg = mc.load()
    assert reg.closures == []

    gaps, counts = _classify("2022-03-09 10:00", "2022-03-09 11:00", _quotes([]), reg)
    assert counts[md.DATA_GAP] == 60
    assert len(gaps) == 1 and gaps[0].kind == px.DATA_GAP


def test_a_data_gap_inside_a_closure_day_outside_the_closure_still_blocks(cache):
    """A verified closure covers only its own proven interval; an unexplained hole elsewhere stays a gap."""
    day = date(2022, 11, 24)
    _hours(cache, day, data=[h for h in range(20) if h != 5] + [23], empty=[5, 20, 21, 22])
    mc.build(2022)
    reg = mc.load()
    closed = {(s, e) for s, e in reg.intervals()}
    assert closed, "the afternoon closure is still established"
    _gaps, counts = _classify("2022-11-24 05:00", "2022-11-24 06:00", _quotes([]), reg)
    assert counts[md.DATA_GAP] == 60          # 05:00 is not inside any verified closure


# ─── C. the holiday name alone establishes nothing (D43 §3) ───────────────────────────────────────────────────────
def test_a_holiday_name_alone_does_not_create_a_verified_closure(cache):
    """An isolated hole on Independence Day, with trading either side, is not a closure."""
    day = date(2022, 7, 4)
    _hours(cache, day, data=[h for h in range(24) if h != 8], empty=[8])
    body = mc.build(2022, holiday_context={date(2022, 7, 4): "Independence Day"})
    assert body["closures"] == []
    _gaps, counts = _classify("2022-07-04 08:00", "2022-07-04 09:00", _quotes([]), mc.load())
    assert counts[md.DATA_GAP] == 60


def test_a_single_missing_hour_never_reaches_the_minimum(cache):
    """One hour is never a closure, whatever the date and whatever it touches."""
    day = date(2022, 5, 30)
    _hours(cache, day, data=[h for h in range(20)] + [22, 23], empty=[20])
    assert mc.build(2022)["closures"] == []
    assert mc.MIN_CLOSURE_HOURS == 2


# ─── D43 §4: both classifications are preserved ───────────────────────────────────────────────────────────────────
def test_both_classifications_are_recorded_side_by_side(cache):
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    body = mc.build(2022, holiday_context={date(2022, 11, 24): "Thanksgiving Day"})
    c = body["closures"][0]
    assert c["source_quality_classification"] == "DATA_LIMITATION"
    assert c["execution_market_state"] == mc.VERIFIED_MARKET_DATA_CLOSURE
    assert c["classification_version"] == mc.CLASSIFICATION_VERSION
    assert set(c["evidence_rules_met"]) == set(mc.EVIDENCE_RULES)
    assert c["holiday_context"] == "Thanksgiving Day"     # context, not evidence
    for key in ("date", "start_utc", "end_utc", "evidence", "source_files"):
        assert c[key], key


def test_the_registry_records_source_file_evidence(cache):
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    c = mc.build(2022)["closures"][0]
    assert len(c["source_files"]) == c["hours"]
    assert all(s == "FEED_404_EMPTY" for s in c["evidence"]["artefact_states"].values())
    assert c["evidence"]["preceding_hour"]["state"] == "HAS_DATA"


# ─── F. causality and determinism (D43 §7F) ───────────────────────────────────────────────────────────────────────
def test_classification_is_deterministic_and_registry_order_independent(cache):
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    first = mc.build(2022)
    second = mc.build(2022)
    assert first["registry_hash"] == second["registry_hash"]
    a = _classify("2022-11-24 19:00", "2022-11-24 23:00", _quotes([]), mc.load())
    b = _classify("2022-11-24 19:00", "2022-11-24 23:00", _quotes([]), mc.load())
    assert a[1] == b[1] and [g.kind for g in a[0]] == [g.kind for g in b[0]]


def test_a_closure_never_consumes_a_minute_that_has_quotes(cache):
    """A live minute is live: the registry can never overrule observed data."""
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    mc.build(2022)
    live = pd.Timestamp("2022-11-24 20:30", tz="UTC")
    _gaps, counts = _classify("2022-11-24 20:00", "2022-11-24 21:00", _quotes([live]), mc.load())
    assert counts[md.VALID_SPARSE_QUOTES] == 1
    assert counts[md.VERIFIED_MARKET_DATA_CLOSURE] == 59


def test_the_registry_is_not_consulted_when_a_caller_passes_an_empty_one(cache):
    """Execution behaviour is explicit: with no registry the interval is a DATA_GAP, exactly as before D43."""
    empty = mc.Registry(year=2022, instrument="xauusd", closures=[])
    _gaps, counts = _classify("2022-11-24 20:00", "2022-11-24 21:00", _quotes([]), empty)
    assert counts[md.DATA_GAP] == 60


def test_the_registry_file_round_trips(cache):
    day = date(2022, 11, 24)
    _hours(cache, day, data=[*range(20), 23], empty=[20, 21, 22])
    body = mc.build(2022)
    on_disk = json.loads(mc.REGISTRY.read_text())
    assert on_disk["registry_hash"] == body["registry_hash"]
    assert mc.closed_at(datetime(2022, 11, 24, 20, 30, tzinfo=UTC), mc.load()) is True
    assert mc.closed_at(datetime(2022, 11, 24, 10, 30, tzinfo=UTC), mc.load()) is False
    assert mc.closure_state(datetime(2022, 11, 24, 10, 30, tzinfo=UTC), mc.load()) == mc.ACTIVE_MARKET
