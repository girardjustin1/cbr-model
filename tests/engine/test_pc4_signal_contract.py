"""D37 §22.1: the frozen PC4 signal contract Phase 14A consumes.

These tests pin the emitted signal's shape so the execution simulator can be written against a stable contract, and
so any future change to the emitter is caught here rather than in a baseline result. Synthetic fixtures only.
"""

import pandas as pd
import pytest

from cbr.data import price_series as psm
from cbr.engine import cbr1h_pc4 as pc4
from cbr.engine.params_pc4 import load_cbr1h_pc4, spec_hash_pc4
from tests.test_feed_comparison import _walk

TOP_LEVEL = ["signal_id", "model", "variant", "price_role", "timestamp", "direction", "entry_trigger_time",
             "entry_expiry_time", "entry_order_type", "entry_reference_price", "entry_structure", "extension",
             "stop_rule", "stop_price", "target_price", "range_high", "range_low", "context_state", "dxy_state",
             "source_feed", "data_confidence", "reason_code", "spec_hash", "eligibility", "lifecycle"]
STOP_RULE = ["extension_extreme", "extension_extreme_source", "candle_open_price", "structure_stop_anchor",
             "stop_anchor_time", "stop_anchor_source", "stop_anchor_path", "final_execution_stop", "direction",
             "buffer", "spread_policy"]


@pytest.fixture(scope="module")
def signal():
    s5 = _walk("2030-01-08 00:00", 2 * 24 * 720, seed=31)
    s1 = psm.rollup_structure(s5, "1min")[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]
    p = load_cbr1h_pc4("A")
    res = pc4.run_cbr1h_pc4(s1, s5, start=pd.Timestamp("2030-01-09 04:00", tz="UTC"),
                            end=pd.Timestamp("2030-01-09 12:00", tz="UTC"), variant="A", params=p)
    assert len(res.candidates), "the synthetic fixture must produce candidates"
    return pc4._signal(res.candidates.iloc[0], p, spec_hash_pc4())


def test_top_level_contract(signal):
    assert list(signal) == TOP_LEVEL


def test_the_signal_names_the_candidate_and_its_spec_hash(signal):
    assert signal["model"] == "CBR1H_BASELINE_V1-PC4"
    assert signal["spec_hash"] == spec_hash_pc4()
    assert signal["price_role"] == "STRUCTURE"          # signals are built on tick-mid bars (D16)


def test_direction_is_execution_facing(signal):
    assert signal["direction"] in ("LONG", "SHORT")


def test_entry_is_a_stop_order_with_a_validity_window(signal):
    assert signal["entry_order_type"] == "STOP"
    assert signal["entry_reference_price"] is not None
    assert signal["entry_trigger_time"] and signal["entry_expiry_time"]


def test_the_stop_is_a_rule_not_a_price(signal):
    """Phase 14A must resolve the stop; the signal deliberately carries inputs, not an executable level (OQ-28)."""
    assert list(signal["stop_rule"]) == STOP_RULE
    assert signal["stop_price"] is None
    assert signal["stop_rule"]["final_execution_stop"] is None
    assert signal["stop_rule"]["stop_anchor_source"]
    assert signal["stop_rule"]["spread_policy"] == "ADD_SPREAD_AT_FILL"
    b = signal["stop_rule"]["buffer"]
    assert b["param"] == "stop.buffer_atr" and b["unit"] == "ATR(1m,14)" and b["label"] == "ASSUMPTION"


def test_the_contract_carries_no_exit_time(signal):
    """Canon's trade management is discretionary, so no forced-exit time is emitted: it is an owner decision."""
    assert "exit_time" not in signal and "forced_exit" not in signal
    assert set(signal["lifecycle"]) == {"cancel_time", "cancel_reason", "five_second_shift_time", "timing30_state"}


def test_eligibility_blocker_is_inherited_and_must_be_gated_externally(signal):
    """PC4 is frozen, so it still emits its pre-run blocker. D37 promotes the model; the flag is not edited."""
    assert signal["eligibility"]["baseline_eligible"] is False
    assert signal["eligibility"]["blockers"] == ["PHASE13C_PARITY_NOT_RUN"]


def test_target_is_resolved_but_stop_is_not(signal):
    assert "target_price" in signal
    assert signal["stop_price"] is None


def test_dxy_and_feed_state_are_declared(signal):
    assert set(signal["dxy_state"]) == {"availability", "reason_codes"}
    assert set(signal["source_feed"]) == {"feed_id", "manifest_hash"}
    assert set(signal["data_confidence"]) == {"level", "reason_codes"}
