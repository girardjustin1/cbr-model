"""Phase 14A.1 real-data integration (owner ruling D39 §8-9).

**Synthetic signals injected into real historical Dukascopy quotes.** No PC4 signal outcome is used, and no
performance statistic of any kind is computed: the orders here are constructed from the observed quote range so the
mechanics can be proven without exposing strategy performance (D39 §8, §13).

Windows are existing stored development/validation days, chosen for calendar properties (DST, rollover) and data
availability — never for favourable outcomes.
"""

from __future__ import annotations

import pandas as pd
import pytest

from cbr.execution import ledger, market_data
from cbr.execution.replay import adapt, execution_config_hash, replay, signal_hash
from cbr.execution.simulate import ExecutionParams
from tests.execution.test_simulator import signal

PARAMS = ExecutionParams()
# Stored tick days. 2025-10-21 is EDT; 2025-11-10 is EST (US DST ended 2025-11-02).
EDT_DAY = pd.Timestamp("2025-10-21", tz="UTC")
EST_DAY = pd.Timestamp("2025-11-10", tz="UTC")
WINDOW = (pd.Timestamp("2025-10-21T01:00Z"), pd.Timestamp("2025-10-21T02:00Z"))


@pytest.fixture(scope="module")
def real_quotes():
    quotes, prov = market_data.load_quotes(*WINDOW)
    assert prov.tick_count > 1000, "the integration tests need a populated real window"
    return quotes, prov


def _levels(quotes: pd.DataFrame) -> dict:
    """Order levels derived from the window's own quote range, not from any strategy or outcome."""
    return {"ask_lo": float(quotes["ask_close"].min()), "ask_hi": float(quotes["ask_close"].max()),
            "bid_lo": float(quotes["bid_close"].min()), "bid_hi": float(quotes["bid_close"].max()),
            "first_ask": float(quotes["ask_close"].iloc[0]), "first_bid": float(quotes["bid_close"].iloc[0])}


# ------------------------------------------------------------------ A, B: sides come from real quotes

def test_a_long_trigger_fills_from_the_ask(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    trigger = lv["first_ask"] + 0.50                      # somewhere the real ask actually goes
    sig = signal(trigger=trigger, target=trigger + 500.0, anchor=lv["bid_lo"] - 100.0,
                 activation=quotes.index[0])
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    if r.execution_status == ledger.NOT_EXECUTED:
        pytest.skip("the real window never reached the constructed trigger")
    at_fill = quotes.loc[pd.Timestamp(r.fill_time)]
    assert r.fill_price == pytest.approx(float(at_fill["ask_close"]))      # filled on the ASK
    assert r.fill_price >= trigger


def test_b_short_trigger_fills_from_the_bid(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    trigger = lv["first_bid"] - 0.50
    sig = signal(direction="SHORT", trigger=trigger, target=trigger - 500.0, anchor=lv["ask_hi"] + 100.0,
                 activation=quotes.index[0])
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    if r.execution_status == ledger.NOT_EXECUTED:
        pytest.skip("the real window never reached the constructed trigger")
    at_fill = quotes.loc[pd.Timestamp(r.fill_time)]
    assert r.fill_price == pytest.approx(float(at_fill["bid_close"]))      # filled on the BID
    assert r.fill_price <= trigger


# ------------------------------------------------------------------ C: real tick sequencing resolves two events

def test_c_tick_sequencing_picks_whichever_level_the_real_ticks_reach_first(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    entry_at = quotes.index[0]
    fill_ask = lv["first_ask"]
    # Both levels are inside the window's real range, so the tick order alone decides which is hit first.
    sig = signal(trigger=fill_ask, target=fill_ask + 1.0, anchor=fill_ask - 1.0 - 0.4, buffer_atr=0.1, atr=2.0,
                 activation=entry_at)
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    assert r.execution_status == ledger.CLOSED
    assert r.exit_reason in (ledger.TARGET, ledger.STOP)
    after = quotes[quotes.index > pd.Timestamp(r.fill_time)]
    target_first = after[after["bid_high"] >= r.target_price]
    stop_first = after[after["bid_low"] <= r.final_execution_stop]
    t_time = target_first.index[0] if len(target_first) else None
    s_time = stop_first.index[0] if len(stop_first) else None
    expected = ledger.TARGET if (s_time is None or (t_time is not None and t_time <= s_time)) else ledger.STOP
    assert r.exit_reason == expected                                  # decided by the real tick order, nothing else


# ------------------------------------------------------------------ D: real time-varying spread survives

def test_d_real_spread_is_time_varying_and_preserved(real_quotes):
    quotes, _ = real_quotes
    spreads = (quotes["ask_close"] - quotes["bid_close"]).round(6)
    assert spreads.nunique() > 5, "the real window should show a varying spread"
    lv = _levels(quotes)
    sig = signal(trigger=lv["first_ask"], target=lv["first_ask"] + 500.0, anchor=lv["bid_lo"] - 100.0,
                 activation=quotes.index[0])
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    at_fill = quotes.loc[pd.Timestamp(r.fill_time)]
    assert r.fill_spread == pytest.approx(float(at_fill["ask_close"]) - float(at_fill["bid_close"]))
    assert r.fill_spread > 0


# ------------------------------------------------------------------ E, F: real quote jumps

def test_e_entry_uses_the_executable_quote_not_the_trigger(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    sig = signal(trigger=lv["ask_lo"] - 5.0, target=lv["ask_hi"] + 500.0, anchor=lv["bid_lo"] - 100.0,
                 activation=quotes.index[0])                       # already through the trigger at the first quote
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    assert r.fill_price == pytest.approx(lv["first_ask"])
    assert r.entry_gap == pytest.approx(lv["first_ask"] - sig["entry_reference_price"])
    assert r.entry_gap > 0                                          # the theoretical trigger was never granted


def test_f_stop_uses_the_executable_quote_after_the_breach(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    sig = signal(trigger=lv["first_ask"], target=lv["ask_hi"] + 500.0,
                 anchor=lv["first_bid"] - 0.10, buffer_atr=0.0, atr=0.0, activation=quotes.index[0])
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    assert r.exit_reason == ledger.STOP
    at_exit = quotes.loc[pd.Timestamp(r.exit_time)]
    assert r.exit_price == pytest.approx(float(at_exit["bid_close"]))
    assert r.exit_price <= r.final_execution_stop                   # filled at or worse than the stop
    assert r.stop_gap == pytest.approx(r.final_execution_stop - r.exit_price)


# ------------------------------------------------------------------ G: target stays limit-priced

def test_g_target_is_limit_priced_on_real_quotes(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    target = lv["first_bid"] + 1.0
    sig = signal(trigger=lv["first_ask"], target=target, anchor=lv["bid_lo"] - 100.0, activation=quotes.index[0])
    r = replay([sig], *WINDOW, params=PARAMS).records[0]
    if r.exit_reason != ledger.TARGET:
        pytest.skip("the real window stopped out before reaching the constructed target")
    assert r.exit_price == pytest.approx(target)                    # never better than the target
    at_exit = quotes.loc[pd.Timestamp(r.exit_time)]
    assert float(at_exit["bid_high"]) >= target


# ------------------------------------------------------------------ H: real rollover calendar, EST and EDT

@pytest.mark.parametrize(("day", "label", "ny_hour_utc"), [(EDT_DAY, "EDT", 21), (EST_DAY, "EST", 22)])
def test_h_rollover_calendar_is_dst_aware_on_real_dates(day, label, ny_hour_utc):
    """17:00 New York is 21:00 UTC in EDT and 22:00 UTC in EST; the window must move with it."""
    inside = day + pd.Timedelta(hours=ny_hour_utc)                  # exactly 17:00 New York
    outside = day + pd.Timedelta(hours=ny_hour_utc - 2)
    from cbr.execution import prices as px
    assert px.in_rollover_window(inside, pre_min=15, post_min=60, ny_time="17:00"), label
    assert not px.in_rollover_window(outside, pre_min=15, post_min=60, ny_time="17:00"), label


def test_h2_pending_order_in_the_real_rollover_window_is_cancelled():
    start = EST_DAY + pd.Timedelta(hours=21, minutes=50)            # 16:50 New York, inside the window
    end = start + pd.Timedelta(minutes=20)
    quotes, prov = market_data.load_quotes(start, end)
    if not prov.tick_count:
        pytest.skip("no stored ticks in the chosen rollover window")
    sig = signal(trigger=float(quotes["ask_close"].iloc[0]), target=float(quotes["ask_close"].iloc[0]) + 100.0,
                 anchor=float(quotes["bid_close"].min()) - 50.0, activation=quotes.index[0])
    r = replay([sig], start, end, params=PARAMS).records[0]
    assert r.execution_status == ledger.CANCELLED
    assert r.reason_code == ledger.ROLLOVER_CANCEL


# ------------------------------------------------------------------ I, J: classification of real intervals

def test_i_scheduled_closure_is_not_a_data_gap():
    """The daily break on a real stored day must classify as SCHEDULED_CLOSURE, never DATA_GAP."""
    start = EST_DAY + pd.Timedelta(hours=22)                        # 17:00 New York in EST: the daily break
    end = start + pd.Timedelta(minutes=45)
    quotes, prov = market_data.load_quotes(start, end)
    gaps, counts = market_data.classify_intervals(start, end, quotes, prov, rollover_pre_min=15, rollover_post_min=60)
    assert counts.get(market_data.DATA_GAP, 0) == 0
    assert counts.get(market_data.SCHEDULED_CLOSURE, 0) or counts.get(market_data.ROLLOVER_EXCLUSION, 0)
    assert not [g for g in gaps if g.kind == market_data.DATA_GAP]


def test_i2_a_populated_hour_has_no_gaps(real_quotes):
    quotes, prov = real_quotes
    gaps, counts = market_data.classify_intervals(*WINDOW, quotes, prov, rollover_pre_min=15, rollover_post_min=60)
    assert counts.get(market_data.VALID_SPARSE_QUOTES) == 60 and not gaps


def test_j_a_day_that_was_never_loaded_produces_an_unprovable_outcome():
    """2025-10-14 (a Tuesday) is not in the stored tick set: NOT_LOADED, and the signal cannot be executed."""
    start, end = pd.Timestamp("2025-10-14T01:00Z"), pd.Timestamp("2025-10-14T02:00Z")
    quotes, prov = market_data.load_quotes(start, end)
    assert prov.tick_count == 0 and prov.missing_days == ("2025-10-14",)
    _gaps, counts = market_data.classify_intervals(start, end, quotes, prov, rollover_pre_min=15, rollover_post_min=60)
    assert counts.get(market_data.NOT_LOADED) == 60
    r = replay([signal(activation=start)], start, end, params=PARAMS).records[0]
    assert r.execution_status == ledger.NOT_EXECUTED
    assert r.reason_code == ledger.EXECUTION_DATA_UNAVAILABLE


def test_j2_a_classified_gap_over_real_quotes_makes_the_outcome_unprovable(real_quotes):
    """Injecting a classified DATA_GAP over a real window must suppress the fill, not reinterpret it."""
    quotes, _prov = real_quotes
    lv = _levels(quotes)
    sig = signal(trigger=lv["first_ask"], target=lv["ask_hi"] + 500.0, anchor=lv["bid_lo"] - 100.0,
                 activation=quotes.index[0])
    from cbr.execution import prices as px
    from cbr.execution.simulate import simulate
    gap = px.Gap(quotes.index[0], quotes.index[-1], px.DATA_GAP)
    r = simulate([sig], quotes, gaps=[gap], params=PARAMS)[0]
    assert r.execution_status == ledger.UNPROVABLE
    assert r.reason_code in (ledger.ENTRY_FILL_UNPROVABLE_DATA_GAP, ledger.TRADE_OUTCOME_UNPROVABLE_DATA_GAP)


# ------------------------------------------------------------------ K, L: determinism and provenance

def test_k_repeated_replay_is_identical(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    sig = signal(trigger=lv["first_ask"], target=lv["first_ask"] + 2.0, anchor=lv["bid_lo"] - 5.0,
                 activation=quotes.index[0])
    a = replay([sig], *WINDOW, params=PARAMS)
    b = replay([sig], *WINDOW, params=PARAMS)
    assert a.provenance["result_hash"] == b.provenance["result_hash"]
    assert ledger.result_hash(a.records) == ledger.result_hash(b.records)


def test_l_source_hashes_and_provenance_travel_with_the_result(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    sig = signal(trigger=lv["first_ask"], target=lv["first_ask"] + 2.0, anchor=lv["bid_lo"] - 5.0,
                 activation=quotes.index[0])
    res = replay([sig], *WINDOW, params=PARAMS)
    md = res.provenance["market_data"]
    assert md["instrument"] == "xauusd"
    assert md["tick_count"] > 1000 and md["source_file_ids"]
    assert all(len(h) == 64 for h in md["source_hashes"].values())
    assert md["day_manifest_sha256"] and md["gap_manifest_version"]
    assert res.provenance["execution_config_hash"] == execution_config_hash()
    assert res.provenance["signal_hash"] == signal_hash([sig])
    assert res.provenance["baseline_provenance"]["parity_verdict"] == "FAIL"
    assert res.provenance["simulator_version"] and res.provenance["result_hash"]


# ------------------------------------------------------------------ adapter and eligibility gate

def test_the_adapter_refuses_a_signal_missing_a_required_input():
    bad = signal()
    bad["entry_trigger_time"] = None
    sig, why = adapt(bad)
    assert sig is None and "activation" in why


def test_the_adapter_refuses_a_signal_with_no_stop_inputs():
    bad = signal(anchor=None)
    bad["stop_rule"]["structure_stop_anchor"] = None
    sig, why = adapt(bad)
    assert sig is None and "stop anchor" in why


def test_the_promotion_gate_still_applies_on_real_data(real_quotes):
    quotes, _ = real_quotes
    lv = _levels(quotes)
    bad = signal(trigger=lv["first_ask"], target=lv["first_ask"] + 2.0, anchor=lv["bid_lo"] - 5.0,
                 activation=quotes.index[0])
    bad["eligibility"]["blockers"] = ["PHASE13C_PARITY_NOT_RUN", "UNAPPROVED_BLOCKER"]
    r = replay([bad], *WINDOW, params=PARAMS).records[0]
    assert r.execution_status == ledger.NOT_EXECUTED and r.reason_code == ledger.INELIGIBLE_BLOCKER


def test_real_quotes_are_bid_ask_never_midpoint(real_quotes):
    quotes, _ = real_quotes
    assert (quotes["ask_close"] > quotes["bid_close"]).all()
    assert quotes["resolved"].all()                                  # tick-resolved, so sequencing is authoritative
