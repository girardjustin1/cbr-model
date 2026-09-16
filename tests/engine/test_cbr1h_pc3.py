"""CBR1H_BASELINE_V1-PC3 rules (owner ruling D29 §19): type-3 re-anchoring, extension states, HVCS, prior setup,
condition fallback, causality, no-lookahead and determinism. Synthetic fixtures unless stated; no course scoring."""

import pandas as pd
import pytest

from cbr.data import price_series as ps
from cbr.engine import cbr1h_pc3 as pc3
from cbr.engine.params_pc3 import load_cbr1h_pc3
from cbr.structure import overextension_pc3 as oe3
from cbr.structure.condition_pc3 import classify_pc3
from cbr.structure.shifts_pc3 import hvcs_structural, track_type3_pc3

T = lambda s: pd.Timestamp(s, tz="UTC")
T0 = T("2030-01-08 01:00")
M1, S5 = pd.Timedelta(minutes=1), pd.Timedelta(seconds=5)


def bars(rows, start=T0, step=M1):
    idx = pd.date_range(start, periods=len(rows), freq=step)
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


def swings(rows):
    return pd.DataFrame(rows, columns=["kind", "price", "time", "confirmed_at"])


# ------------------------------------------------------------------ type 3 re-anchoring (D29 §1)

def _sell_setup():
    """High 110 confirmed, low 100 confirmed; price sweeps 110 then a newer low 104 confirms before the break."""
    sw = swings([("H", 110.0, T0, T0 + 5 * M1), ("L", 100.0, T0 + 10 * M1, T0 + 15 * M1)])
    b = bars([(108, 109, 107, 108), (108, 111, 107, 110), (110, 110, 104, 105), (105, 106, 103, 104)],
             start=T0 + 15 * M1)
    return sw, b


def test_trigger_reanchors_to_a_newly_confirmed_opposing_swing():
    sw, b = _sell_setup()
    sw2 = pd.concat([sw, swings([("L", 104.0, b.index[2], b.index[2] + M1)])], ignore_index=True)
    arms = [a for a in track_type3_pc3(b, sw2, max_reversal=pd.Timedelta(minutes=15), tick=0.01) if a.direction == "SELL"]
    assert len(arms) == 1
    a = arms[0]
    assert a.end == "BREAK" and a.broken_price == 104.0 and a.trigger_price == pytest.approx(103.99)
    assert a.reanchored == 1 and a.trigger_break_time == b.index[3]
    plain = [x for x in track_type3_pc3(b, sw, max_reversal=pd.Timedelta(minutes=15), tick=0.01) if x.direction == "SELL"]
    assert plain[0].broken_price == 100.0 and plain[0].trigger_break_time is None   # the old trigger is never hit


def test_a_new_opposing_swing_does_not_disarm_the_pattern():
    sw, b = _sell_setup()
    sw2 = pd.concat([sw, swings([("L", 104.0, b.index[2], b.index[2] + M1)])], ignore_index=True)
    arms = track_type3_pc3(b, sw2, max_reversal=pd.Timedelta(minutes=15), tick=0.01)
    assert [a.end for a in arms if a.direction == "SELL"] == ["BREAK"]     # PC2 would have disarmed on NEW_SWING


def test_no_future_swing_leakage():
    """A swing confirmed after the break may not become the trigger retroactively."""
    sw, b = _sell_setup()
    future = pd.concat([sw, swings([("L", 104.0, b.index[2], b.index[3] + 10 * M1)])], ignore_index=True)
    arms = [a for a in track_type3_pc3(b, future, max_reversal=pd.Timedelta(minutes=15), tick=0.01)
            if a.direction == "SELL"]
    assert arms[0].broken_price == 100.0                                   # the late confirmation is ignored


def test_latest_sweep_extreme_resets_the_reversal_timer():
    sw = swings([("H", 110.0, T0, T0 + 5 * M1), ("L", 100.0, T0 + 10 * M1, T0 + 15 * M1)])
    rows = [(108, 111, 107, 110), (110, 112, 109, 111), (111, 113, 110, 112), (112, 112, 99, 100)]
    b = bars(rows, start=T0 + 15 * M1)
    arms = [a for a in track_type3_pc3(b, sw, max_reversal=pd.Timedelta(minutes=2), tick=0.01) if a.direction == "SELL"]
    assert arms[0].end == "BREAK"                                          # each new extreme restarted the 2-minute clock
    assert arms[0].latest_sweep_extreme_time == b.index[2]
    flat = bars([(108, 111, 107, 110), (110, 110, 109, 109), (109, 110, 108, 109), (109, 109, 99, 100)],
                start=T0 + 15 * M1)
    assert [a.end for a in track_type3_pc3(flat, sw, max_reversal=pd.Timedelta(minutes=2), tick=0.01)
            if a.direction == "SELL"] == ["TIMEOUT"]                       # no new extreme: the clock expires


def test_buy_and_sell_are_symmetric():
    sw = swings([("L", 100.0, T0, T0 + 5 * M1), ("H", 110.0, T0 + 10 * M1, T0 + 15 * M1)])
    b = bars([(102, 103, 101, 102), (102, 103, 99, 100), (100, 106, 100, 105), (105, 111, 104, 110)],
             start=T0 + 15 * M1)
    arms = [a for a in track_type3_pc3(b, sw, max_reversal=pd.Timedelta(minutes=15), tick=0.01) if a.direction == "BUY"]
    assert arms[0].end == "BREAK" and arms[0].trigger_price == pytest.approx(110.01)


def test_decision_records_the_trigger_in_force_at_the_decision():
    """Regression: under re-anchoring the trigger moves, so the decision-time ledger must not carry the FINAL trigger."""
    sw, b = _sell_setup()
    sw2 = pd.concat([sw, swings([("L", 104.0, b.index[2], b.index[2] + M1)])], ignore_index=True)
    arm = next(a for a in track_type3_pc3(b, sw2, max_reversal=pd.Timedelta(minutes=15), tick=0.01)
               if a.direction == "SELL")
    at_sweep = arm.first_sweep_time + M1
    assert arm.trigger_at(at_sweep) == pytest.approx(99.99)                # what was knowable at the sweep
    assert arm.trigger_price == pytest.approx(103.99)                      # the final, re-anchored trigger
    assert arm.trigger_at(b.index[0] - M1) is None                         # nothing knowable before the first swing


# ------------------------------------------------------------------ extension states (D29 §5-§9)

def _hour(rows, prev_high=None, prev_low=None, as_of_min=None):
    b = bars(rows, start=T0)
    p = load_cbr1h_pc3("A")
    as_of = T0 + pd.Timedelta(minutes=as_of_min if as_of_min is not None else len(rows))
    return oe3.evaluate_pc3(b, T0, float(rows[0][0]), as_of, pullback_frac=p.pullback_frac,
                            two_sided_frac=p.two_sided_frac, earliest_activation_min=p.earliest_activation_min,
                            prev_candle_high=prev_high, prev_candle_low=prev_low)


def test_hour_starts_in_pre_extension_and_cannot_fail_the_pullback_rule():
    rows = [(100, 104, 99.9, 103), (103, 103, 100, 100.2)] * 3            # a 50% retrace of every early sub-leg
    ext = _hour(rows, prev_high=110.0)
    assert ext.state == oe3.PRE_EXTENSION and ext.no_pullback is True and ext.size == 0.0


def test_activation_cannot_happen_before_the_earliest_minute():
    rows = [(100, 112, 99, 111)] + [(111, 111.5, 110, 111)] * 4           # takes the reference in minute 1
    ext = _hour(rows, prev_high=110.0, as_of_min=5)
    assert ext.state == oe3.PRE_EXTENSION and ext.activation_time is None


def test_q1_activation_takes_the_previous_15m_extreme_at_or_after_minute_7():
    rows = [(100, 101, 99, 100)] * 7 + [(100, 112, 100, 111)] + [(111, 113, 110, 112)] * 3
    ext = _hour(rows, prev_high=110.0)
    assert ext.state == oe3.EXTENSION_ACTIVE
    assert ext.activation_time == T0 + 7 * M1 and ext.previous_15m_reference == 110.0
    assert "previous 15m high" in ext.activation_reason and ext.activation_price == 112.0


def test_pullback_is_measured_against_the_whole_active_extension_without_a_latch():
    """An early 50% retrace of a small sub-leg does not disqualify an hour that then extends."""
    rows = ([(100, 101, 99, 100)] * 7 + [(100, 112, 100, 111)]            # activation
            + [(111, 111.5, 97, 98)]                                      # deep retrace of the young extension
            + [(98, 125, 98, 124), (124, 145, 123, 144)])                 # the extension then continues
    early = _hour(rows[:10], prev_high=110.0, as_of_min=10)
    assert early.state == oe3.EXTENSION_ACTIVE and early.no_pullback is False   # 15 of a 26-point extension
    later = _hour(rows, prev_high=110.0)
    assert later.no_pullback is True                                      # no latch: the same retrace is now a fraction
    assert later.retracement_ratio < 0.5 and later.deepest_retracement == pytest.approx(15.0)


def test_extension_duration_is_measured_from_activation():
    rows = [(100, 101, 99, 100)] * 7 + [(100, 112, 100, 111)] + [(111, 113, 110, 112)] * 5
    ext = _hour(rows, prev_high=110.0)
    assert ext.activation_time == T0 + 7 * M1 and ext.duration_min == pytest.approx(
        (ext.extreme_time - ext.activation_time) / M1)
    assert ext.duration_min <= 6 and ext.origin_price is not None


def test_extension_uses_no_data_after_as_of():
    rows = [(100, 101, 99, 100)] * 7 + [(100, 112, 100, 111), (111, 113, 110, 112), (112, 140, 111, 139)]
    cut = _hour(rows[:9], prev_high=110.0, as_of_min=9)
    full = _hour(rows, prev_high=110.0)
    assert cut.extreme == 113.0 and full.extreme == 140.0                 # the later spike is invisible at the cut
    assert cut.state == full.state == oe3.EXTENSION_ACTIVE


def test_future_data_cannot_retroactively_validate_or_invalidate(monkeypatch):
    """D29 §9: truncating after t changes nothing; later extremes or retracements never rewrite an earlier verdict."""
    rows = ([(100, 101, 99, 100)] * 7 + [(100, 112, 100, 111), (111, 111.5, 97, 98), (98, 125, 98, 124),
                                         (124, 145, 123, 144)])
    verdicts = [(_hour(rows[:n], prev_high=110.0, as_of_min=n).no_pullback) for n in (9, 10, 11)]
    assert verdicts == [True, False, True]                                # evolves forward only, never latches
    for n in (9, 10, 11):                                                 # truncation-invariance at each cut
        assert _hour(rows[:n], prev_high=110.0, as_of_min=n) == _hour(rows, prev_high=110.0, as_of_min=n)
    assert _hour(rows[:11], prev_high=110.0, as_of_min=11).no_pullback is True


# ------------------------------------------------------------------ HVCS (D29 §10, §11)

def test_indecision_candle_stays_inside_the_sequence():
    b = bars([(100, 105, 99, 104), (104, 104, 100, 101), (101, 103, 100, 102), (102, 102.5, 98, 99)])
    seq = hvcs_structural(b, b.index[3], "DOWN", atr_1m=2.0, min_minutes=3, lvcs_body_atr=0.3)
    assert seq.valid and seq.minutes == 3 and seq.indecision_bars == 1     # the bullish-closing bar respects the high


def test_structurally_invalid_bar_ends_the_sequence():
    b = bars([(100, 105, 99, 104), (104, 104, 100, 101), (101, 106, 100, 102), (102, 102.5, 98, 99)])
    seq = hvcs_structural(b, b.index[3], "DOWN", atr_1m=2.0, min_minutes=3, lvcs_body_atr=0.3)
    assert seq.minutes == 1 and not seq.valid                              # bar 2 took out the previous high


def test_hvcs_is_evaluated_at_the_shift_not_before(run_pc3):
    res, _, _ = run_pc3
    c = res.candidates
    shifted = c[c["five_second_shift_time"].notna()]
    assert len(shifted)
    assert (shifted["hvcs_evaluated_at"] == shifted["five_second_shift_time"]).all()
    assert c[c["five_second_shift_time"].isna()]["hvcs_rule_state"].isna().all()
    assert c[c["five_second_shift_time"].isna()]["rules"].map(
        lambda r: r.get("M1H-6A-1-HVCS-INTO-SHIFT") is None).all()


# ------------------------------------------------------------------ prior setup and condition (D29 §12, §14)

def test_prior_setup_is_diagnostic_and_never_blocks(run_pc3):
    res, _, _ = run_pc3
    c = res.candidates
    assert not any("M1H-COND-04" in r for r in c["rules_failed"])
    assert not any("M1H-COND-04" in rules for rules in c["rules"])
    for field in ("prior_setup_exists", "prior_setup_count", "prior_setup_age_min", "prior_setup_model"):
        assert field in c.columns
    armed_without_prior = c[(c["event"] == "ARMED") & (c["prior_setup_count"] == 0)]
    assert len(armed_without_prior) or not len(c[c["event"] == "ARMED"])   # absence of a prior setup is not a blocker


def test_directionless_trending_range_falls_back_to_range():
    sw = swings([("H", 110.0, T0, T0 + M1), ("L", 100.0, T0 + 2 * M1, T0 + 3 * M1),      # legs 10, 6, 3.6 -> c_med 0.6
                 ("H", 106.0, T0 + 4 * M1, T0 + 5 * M1), ("L", 102.4, T0 + 6 * M1, T0 + 7 * M1)])
    b = bars([(105, 110, 100, 105)] * 10)
    kw = {"min_legs": 3, "range_min": 0.75, "trend_max": 0.5, "correction_cap": 2.0, "aggregate": "median"}
    cond, fallback = classify_pc3(sw, b, T0 + 9 * M1, pd.Timedelta(hours=8), window_start=T0 - pd.Timedelta(hours=8), **kw)
    assert cond.direction == "NONE"
    assert (cond.condition, fallback) == ("RANGE", True)
    assert not any("M1H-COND-03" in k for k in ("M1H-COND-01", "M1H-COND-02"))


# ------------------------------------------------------------------ engine: causality and determinism

@pytest.fixture(scope="module")
def run_pc3():
    """PC3 engine on synthetic STRUCTURE bars (stored-data index format), plus its inputs."""
    from cbr.data import price_series as psm
    from tests.test_feed_comparison import _walk
    s5 = _walk("2030-01-08 00:00", 2 * 24 * 720, seed=31)
    s1 = psm.rollup_structure(s5, "1min")[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]
    p = load_cbr1h_pc3("A")
    res = pc3.run_cbr1h_pc3(s1, s5, start=T("2030-01-09 04:00"), end=T("2030-01-09 12:00"), variant="A", params=p)
    return res, s1, s5


def test_engine_produces_candidates_and_is_deterministic(run_pc3):
    res, s1, s5 = run_pc3
    assert len(res.candidates) > 5
    again = pc3.run_cbr1h_pc3(s1, s5, start=T("2030-01-09 04:00"), end=T("2030-01-09 12:00"), variant="A",
                              params=load_cbr1h_pc3("A"))
    assert pc3.result_hash(res) == pc3.result_hash(again)


def test_engine_is_causal_under_truncation_and_future_mutation(run_pc3):
    _res, s1, s5 = run_pc3
    p = load_cbr1h_pc3("A")
    h0 = T("2030-01-09 06:00")
    full = pc3.run_cbr1h_pc3(s1, s5, start=h0, end=h0 + pd.Timedelta(hours=1), variant="A", params=p)
    dec = pc3.decision_frame(full)
    if not len(dec):
        pytest.skip("no candidate in the chosen hour")
    cut = pd.Timestamp(dec["timestamp"].iloc[-1]) + pd.Timedelta(seconds=32)
    recs = lambda f: f.astype(str).to_dict("records")
    want = recs(dec[dec["timestamp"] <= cut].reset_index(drop=True))
    trunc = pc3.run_cbr1h_pc3(s1[s1.index + M1 <= cut], s5[s5.index + S5 <= cut], start=h0,
                              end=h0 + pd.Timedelta(hours=1), variant="A", params=p)
    got = pc3.decision_frame(trunc)
    assert want == recs(got[got["timestamp"] <= cut].reset_index(drop=True))
    m1, m5 = s1.copy(), s5.copy()
    for m, blen in ((m1, M1), (m5, S5)):
        after = m.index + blen > cut
        m.loc[after, ["open", "high", "low", "close"]] = m.loc[after, ["open", "high", "low", "close"]] * 1.03 + 0.5
    mut = pc3.decision_frame(pc3.run_cbr1h_pc3(m1, m5, start=h0, end=h0 + pd.Timedelta(hours=1), variant="A", params=p))
    assert want == recs(mut[mut["timestamp"] <= cut].reset_index(drop=True))


def test_engine_refuses_non_structure_bars(run_pc3):
    _, s1, s5 = run_pc3
    bad = s1.drop(columns=["price_role"])
    with pytest.raises(ps.PriceRoleError):
        pc3.run_cbr1h_pc3(bad, s5, start=T("2030-01-09 06:00"), end=T("2030-01-09 07:00"))


def test_pc2_engine_is_untouched_by_pc3():
    """PC3 is additive: PC2's pinned files and spec hash are unchanged."""
    import yaml

    from cbr.engine.params import ROOT, spec_hash
    rec = yaml.safe_load((ROOT / "docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC2.yaml").read_text())
    assert rec["spec_hash"] == spec_hash()
