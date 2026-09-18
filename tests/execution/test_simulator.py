"""Phase 14A execution mechanics (owner ruling D38 §30). Synthetic fixtures only; no historical data, no outcomes.

Numbering follows the D38 §30 inventory so each required case is locatable.
"""

from __future__ import annotations

import pandas as pd
import pytest

from cbr.execution import ledger
from cbr.execution import prices as px
from cbr.execution.contract import ContractError, eligible, parse
from cbr.execution.simulate import ExecutionParams, run_manifest, simulate

T0 = pd.Timestamp("2030-03-12 10:00:00", tz="UTC")          # far from any rollover window
S = pd.Timedelta(seconds=5)
PARAMS = ExecutionParams()


def quotes(rows, *, start=T0, step=S, resolved=True) -> pd.DataFrame:
    """rows = [(bid, ask), ...] as tick-level quotes unless `resolved=False`."""
    idx = pd.date_range(start, periods=len(rows), freq=step, tz="UTC")
    df = pd.DataFrame({"bid_low": [b for b, _ in rows], "bid_high": [b for b, _ in rows],
                       "bid_close": [b for b, _ in rows], "ask_low": [a for _, a in rows],
                       "ask_high": [a for _, a in rows], "ask_close": [a for _, a in rows],
                       "resolved": resolved}, index=idx)
    df.index.name = "time"
    return df


def bar_quotes(rows, *, start=T0, step=S) -> pd.DataFrame:
    """rows = [(bid_low, bid_high, ask_low, ask_high), ...] as *unresolved* aggregated bars."""
    idx = pd.date_range(start, periods=len(rows), freq=step, tz="UTC")
    df = pd.DataFrame({"bid_low": [r[0] for r in rows], "bid_high": [r[1] for r in rows],
                       "ask_low": [r[2] for r in rows], "ask_high": [r[3] for r in rows],
                       "bid_close": [r[1] for r in rows], "ask_close": [r[3] for r in rows],
                       "resolved": False}, index=idx)
    df.index.name = "time"
    return df


def signal(*, sid="S1", direction="LONG", trigger=100.0, target=104.0, anchor=98.0, buffer_atr=0.1, atr=2.0,
           activation=T0, expiry=None, cancel=None, path=(), variant="A") -> dict:
    return {
        "signal_id": sid, "model": "CBR1H_BASELINE_V1-PC4", "variant": variant, "price_role": "STRUCTURE",
        "timestamp": str(activation), "direction": direction, "entry_trigger_time": str(activation),
        "entry_expiry_time": None if expiry is None else str(expiry), "entry_order_type": "STOP",
        "entry_reference_price": trigger,
        "entry_structure": {}, "extension": {},
        "stop_rule": {"structure_stop_anchor": anchor, "stop_anchor_path": [[str(t), p] for t, p in path],
                      "final_execution_stop": None, "spread_policy": "ADD_SPREAD_AT_FILL",
                      "buffer": {"param": "stop.buffer_atr", "value": buffer_atr, "unit": "ATR(1m,14)",
                                 "atr_at_decision": atr, "label": "ASSUMPTION", "source": ["OQ-11"]}},
        "stop_price": None, "target_price": target, "range_high": None, "range_low": None,
        "context_state": {}, "dxy_state": {}, "source_feed": {},
        "data_confidence": {"level": "FULL", "reason_codes": []}, "reason_code": "ARMED",
        "spec_hash": "62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7",
        "eligibility": {"baseline_eligible": False, "blockers": ["PHASE13C_PARITY_NOT_RUN"]},
        "lifecycle": {"cancel_time": None if cancel is None else str(cancel), "cancel_reason": None,
                      "five_second_shift_time": None, "timing30_state": None},
    }


def one(records):
    assert len(records) == 1
    return records[0]


# ------------------------------------------------------------------ 1-4: the four basic outcomes

def test_1_long_entry_target():
    q = quotes([(99.0, 99.2), (100.1, 100.3), (103.9, 104.1), (104.2, 104.4)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.execution_status == ledger.CLOSED and r.exit_reason == ledger.TARGET
    assert r.fill_price == 100.3                       # filled on the ask that triggered
    assert r.exit_price == 104.0                       # target fill is AT the target (D38 §13)
    assert r.gross_r == pytest.approx((104.0 - 100.3) / r.initial_risk)


def test_2_long_entry_stop():
    q = quotes([(100.1, 100.3), (99.0, 99.2), (97.0, 97.2)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.execution_status == ledger.CLOSED and r.exit_reason == ledger.STOP
    assert r.final_execution_stop == pytest.approx(98.0 - 0.2 - 0.2)     # anchor - buffer - spread
    assert r.exit_price == 97.0 and r.gross_r < 0      # a long stop fills on the BID


def test_3_short_entry_target():
    q = quotes([(100.0, 100.2), (99.8, 100.0), (96.1, 96.3), (95.8, 96.0)])
    r = one(simulate([signal(direction="SHORT", trigger=100.0, target=96.2, anchor=102.0)], q, params=PARAMS))
    assert r.execution_status == ledger.CLOSED and r.exit_reason == ledger.TARGET
    assert r.fill_price == 100.0                        # short fills on the bid
    assert r.exit_price == 96.2


def test_4_short_entry_stop():
    q = quotes([(100.0, 100.2), (102.3, 102.5), (103.0, 103.2)])
    r = one(simulate([signal(direction="SHORT", trigger=100.0, target=96.0, anchor=102.0)], q, params=PARAMS))
    assert r.execution_status == ledger.CLOSED and r.exit_reason == ledger.STOP
    assert r.final_execution_stop == pytest.approx(102.0 + 0.2 + 0.2)
    assert r.exit_price == 102.5                        # short stop fills on the ask


# ------------------------------------------------------------------ 5-7: gaps through levels

def test_5_entry_gaps_through_the_trigger():
    q = quotes([(99.0, 99.2), (101.8, 102.0), (104.0, 104.2)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.fill_price == 102.0 and r.entry_gap == pytest.approx(2.0)   # never the theoretical trigger


def test_6_stop_gap_fills_worse_than_the_stop():
    q = quotes([(100.1, 100.3), (90.0, 90.2)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.exit_reason == ledger.STOP and r.exit_price == 90.0
    assert r.stop_gap == pytest.approx(r.final_execution_stop - 90.0)


def test_7_target_gap_never_awards_improvement():
    q = quotes([(100.1, 100.3), (108.0, 108.2)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.exit_reason == ledger.TARGET and r.exit_price == 104.0      # conservative by ruling


# ------------------------------------------------------------------ 8-9: tick sequencing decides

def test_8_same_bar_target_before_stop():
    q = quotes([(100.1, 100.3), (104.2, 104.4), (97.0, 97.2)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.exit_reason == ledger.TARGET


def test_9_same_bar_stop_before_target():
    q = quotes([(100.1, 100.3), (97.0, 97.2), (104.2, 104.4)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.exit_reason == ledger.STOP


def test_unresolved_bar_containing_both_levels_is_unprovable():
    """D38 §8: no favourable convention where tick sequencing is unavailable."""
    q = pd.concat([quotes([(100.1, 100.3)]),
                   bar_quotes([(96.0, 105.0, 96.2, 105.2)], start=T0 + S)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.execution_status == ledger.UNPROVABLE
    assert r.reason_code == ledger.EXECUTION_UNPROVABLE_INTRABAR


# ------------------------------------------------------------------ 10: one position per instrument

def test_10_sibling_order_is_cancelled_on_the_first_fill():
    a = signal(sid="A", variant="A", trigger=100.0)
    b = signal(sid="B", variant="B", trigger=101.0)
    q = quotes([(99.0, 99.2), (100.1, 100.3), (101.5, 101.7), (104.2, 104.4)])
    recs = {r.signal_id: r for r in simulate([a, b], q, params=PARAMS)}
    assert recs["A"].execution_status == ledger.CLOSED
    assert recs["B"].execution_status == ledger.CANCELLED
    assert recs["B"].reason_code == ledger.SIBLING_ORDER_CANCELLED_ON_FILL


def test_a_signal_activating_while_a_position_is_open_is_logged_not_executed():
    a = signal(sid="A", trigger=100.0)
    later = signal(sid="B", trigger=100.0, activation=T0 + 2 * S)
    q = quotes([(100.1, 100.3), (100.4, 100.6), (100.5, 100.7), (104.2, 104.4)])
    recs = {r.signal_id: r for r in simulate([a, later], q, params=PARAMS)}
    assert recs["A"].execution_status == ledger.CLOSED
    assert recs["B"].execution_status == ledger.NOT_EXECUTED
    assert recs["B"].reason_code == ledger.POSITION_ALREADY_OPEN


def test_a_signal_after_the_position_closes_may_trade():
    a = signal(sid="A", trigger=100.0, target=101.0, anchor=99.0)
    b = signal(sid="B", trigger=103.0, target=104.0, anchor=102.0, activation=T0 + 3 * S)
    q = quotes([(100.1, 100.3), (101.2, 101.4), (103.1, 103.3), (103.2, 103.4), (104.1, 104.3)])
    recs = {r.signal_id: r for r in simulate([a, b], q, params=PARAMS)}
    assert recs["A"].exit_reason == ledger.TARGET
    assert recs["B"].execution_status == ledger.CLOSED


# ------------------------------------------------------------------ 11-12: rollover

ROLL = pd.Timestamp("2030-03-12 20:50:00", tz="UTC")        # 16:50 New York, inside [17:00-15m, 17:00+60m]


def test_11_pending_order_inside_the_rollover_window_is_cancelled():
    q = quotes([(99.0, 99.2), (100.1, 100.3)], start=ROLL)
    r = one(simulate([signal(activation=ROLL)], q, params=PARAMS))
    assert r.execution_status == ledger.CANCELLED and r.reason_code == ledger.ROLLOVER_CANCEL


def test_12_open_position_is_closed_before_rollover_begins():
    start = ROLL - pd.Timedelta(minutes=8)                  # activation before the window, exit forced at its start
    q = quotes([(100.1, 100.3)] + [(100.5, 100.7)] * 200, start=start, step=pd.Timedelta(seconds=5))
    r = one(simulate([signal(activation=start)], q, params=PARAMS))
    assert r.execution_status == ledger.CLOSED and r.exit_reason == ledger.ROLLOVER_EXIT
    assert pd.Timestamp(r.exit_time) < ROLL
    assert r.exit_price == 100.5                            # long exits on the bid


# ------------------------------------------------------------------ 13-15: data problems

def test_13_missing_executable_data_is_never_synthesised():
    q = quotes([(99.0, 99.2)], start=T0 - pd.Timedelta(hours=1))
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.execution_status == ledger.NOT_EXECUTED
    assert r.reason_code == ledger.EXECUTION_DATA_UNAVAILABLE


def test_14_data_gap_while_the_order_is_pending():
    q = quotes([(99.0, 99.2), (99.1, 99.3), (104.2, 104.4)])
    gap = px.Gap(T0 + S, T0 + 2 * S, px.DATA_GAP)
    r = one(simulate([signal()], q, gaps=[gap], params=PARAMS))
    assert r.execution_status == ledger.UNPROVABLE
    assert r.reason_code == ledger.ENTRY_FILL_UNPROVABLE_DATA_GAP


def test_15_data_gap_while_a_position_is_open():
    q = quotes([(100.1, 100.3), (100.2, 100.4), (104.2, 104.4)])
    gap = px.Gap(T0 + S, T0 + 2 * S, px.DATA_GAP)
    r = one(simulate([signal()], q, gaps=[gap], params=PARAMS))
    assert r.execution_status == ledger.UNPROVABLE
    assert r.reason_code == ledger.TRADE_OUTCOME_UNPROVABLE_DATA_GAP


def test_scheduled_closure_and_sparse_quotes_are_not_data_gaps():
    """D38 §21: only an established data gap makes an outcome unprovable."""
    q = quotes([(100.1, 100.3), (104.2, 104.4)])
    closure = px.Gap(T0 + S, T0 + 2 * S, px.SCHEDULED_CLOSURE)
    r = one(simulate([signal()], q, gaps=[closure], params=PARAMS))
    assert r.execution_status == ledger.CLOSED


# ------------------------------------------------------------------ 16-18: risk, costs, dataset end

def test_16_non_positive_risk_is_refused():
    r = one(simulate([signal(anchor=101.0)], quotes([(100.1, 100.3), (104.2, 104.4)]), params=PARAMS))
    assert r.execution_status == ledger.NOT_EXECUTED
    assert r.reason_code == ledger.EXECUTION_INVALID_RISK
    assert r.initial_risk <= 0


def test_17_spread_is_not_double_counted():
    q = quotes([(100.1, 100.3), (104.2, 104.4)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.additional_slippage == 0.0 and r.explicit_commission == 0.0
    assert r.net_r == r.gross_r                                     # spread already lives in the bid/ask fills
    assert r.fill_spread == pytest.approx(0.2)


def test_18_open_position_at_dataset_end():
    q = quotes([(100.1, 100.3), (101.0, 101.2)])
    r = one(simulate([signal()], q, params=PARAMS))
    assert r.execution_status == ledger.CLOSED and r.exit_reason == ledger.DATASET_END_EXIT
    assert r.exit_price == 101.0


# ------------------------------------------------------------------ 19-20: determinism and causality

def test_19_repeat_runs_are_identical():
    q = quotes([(99.0, 99.2), (100.1, 100.3), (104.2, 104.4)])
    a = simulate([signal()], q, params=PARAMS)
    b = simulate([signal()], q, params=PARAMS)
    assert ledger.result_hash(a) == ledger.result_hash(b)


def test_20_future_quotes_never_change_an_earlier_fill():
    base = [(99.0, 99.2), (100.1, 100.3), (104.2, 104.4)]
    a = one(simulate([signal()], quotes(base), params=PARAMS))
    mutated = one(simulate([signal()], quotes([*base, (5.0, 5.2), (500.0, 500.2)]), params=PARAMS))
    assert (a.fill_time, a.fill_price, a.exit_reason, a.exit_price) == \
           (mutated.fill_time, mutated.fill_price, mutated.exit_reason, mutated.exit_price)


def test_quotes_before_activation_cannot_fill_the_order():
    """D38 §11: a pre-activation crossing never fabricates a fill."""
    q = quotes([(101.0, 101.2), (99.0, 99.2)])
    r = one(simulate([signal(activation=T0 + S)], q, params=PARAMS))
    assert r.execution_status == ledger.NOT_EXECUTED and r.reason_code == ledger.ENTRY_NOT_TRIGGERED


def test_the_stop_is_resolved_at_fill_and_then_frozen():
    """D38 §2: the anchor may evolve until the fill; afterwards later structure never moves the stop."""
    path = ((T0, 98.0), (T0 + S, 97.0), (T0 + 5 * S, 90.0))          # the 90.0 arrives after the fill
    q = quotes([(99.0, 99.2), (100.1, 100.3), (96.5, 96.7), (96.0, 96.2), (95.0, 95.2), (94.0, 94.2)])
    r = one(simulate([signal(path=path, target=120.0)], q, params=PARAMS))
    assert r.fill_time_stop_anchor == 97.0                          # lowest through the fill, not the later 90.0
    assert r.final_execution_stop == pytest.approx(97.0 - 0.2 - 0.2)
    assert r.exit_reason == ledger.STOP


# ------------------------------------------------------------------ contract and eligibility gate

def test_an_unexpected_blocker_refuses_execution():
    bad = signal()
    bad["eligibility"]["blockers"] = ["PHASE13C_PARITY_NOT_RUN", "SOMETHING_ELSE"]
    r = one(simulate([bad], quotes([(100.1, 100.3), (104.2, 104.4)]), params=PARAMS))
    assert r.execution_status == ledger.NOT_EXECUTED and r.reason_code == ledger.INELIGIBLE_BLOCKER


def test_the_promotion_blocker_alone_is_executable():
    ok, why = eligible(signal())
    assert ok and why is None


def test_a_signal_carrying_an_executable_stop_is_refused():
    bad = signal()
    bad["stop_rule"]["final_execution_stop"] = 98.0
    with pytest.raises(ContractError):
        parse(bad)


def test_every_signal_gets_exactly_one_ledger_row():
    sigs = [signal(sid=f"S{i}", trigger=100.0 + i) for i in range(4)]
    recs = simulate(sigs, quotes([(99.0, 99.2), (100.1, 100.3), (104.2, 104.4)]), params=PARAMS)
    assert sorted(r.signal_id for r in recs) == ["S0", "S1", "S2", "S3"]
    for r in recs:
        r.validate()


def test_manifest_carries_the_promotion_provenance():
    q = quotes([(100.1, 100.3), (104.2, 104.4)])
    m = run_manifest(simulate([signal()], q, params=PARAMS))
    assert m["baseline_provenance"]["parity_verdict"] == "FAIL"
    assert m["execution_semantics"]["forced_exit"] == "NONE"
    assert m["by_status"] == {ledger.CLOSED: 1}
    assert m["administrative_exits"] == {ledger.ROLLOVER_EXIT: 0, ledger.DATASET_END_EXIT: 0}
