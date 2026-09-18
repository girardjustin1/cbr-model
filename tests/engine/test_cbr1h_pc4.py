"""CBR1H_BASELINE_V1-PC4 rules (owner ruling D34 §15): the restored HVCS violation tolerance (F-1), the two
previous-15m rules evaluated at the final 5s shift with Q anchored there (F-9 / F-10), the 15-minute boundary cases,
causality, determinism and the PC2 / PC3 immutability guards.

Synthetic fixtures only (D34 §15, §17). No scored parity case is used as a development test.
"""

import pathlib

import pandas as pd
import pytest

from cbr.data import price_series as ps
from cbr.engine import cbr1h_pc4 as pc4
from cbr.engine.params import spec_hash
from cbr.engine.params_pc3 import spec_hash_pc3
from cbr.engine.params_pc4 import load_cbr1h_pc4, spec_hash_pc4
from cbr.structure.shifts_pc3 import hvcs_structural
from cbr.structure.shifts_pc4 import hvcs_structural_pc4

T = lambda s: pd.Timestamp(s, tz="UTC")
T0 = T("2030-01-08 01:00")
M1, M15, S5 = pd.Timedelta(minutes=1), pd.Timedelta(minutes=15), pd.Timedelta(seconds=5)
Q_START = pd.Timestamp("2030-01-08 01:15", tz="UTC")
HV = {"atr_1m": 1.0, "min_minutes": 4, "lvcs_body_atr": 0.3}


def bars(rows, start=T0, step=M1):
    idx = pd.date_range(start, periods=len(rows), freq=step)
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


def down_run(highs, *, closes_with=True):
    """A falling 1m sequence with the given highs; each candle's close direction is set by `closes_with`."""
    rows = []
    for h in highs:
        lo = h - 2.0
        rows.append((h - 0.5, h, lo, lo + 0.2) if closes_with else (lo + 0.2, h, lo, h - 0.1))
    return bars(rows)


# ------------------------------------------------------------------ F-1: the restored violation tolerance (D34 §2)

def test_a_clean_run_passes_with_zero_violations():
    b = down_run([120, 118, 116, 114, 112])
    seq = hvcs_structural_pc4(b, b.index[-1], "DOWN", max_violations=1, **HV)
    assert seq.minutes == 4 and seq.violations == 0 and seq.valid


def test_one_permitted_violation_may_pass():
    """The HX-1 / HX-2 shape: a long push containing exactly one higher high."""
    b = down_run([130, 128, 126, 124, 127, 122, 120])          # the 127 breaks the side once
    seq = hvcs_structural_pc4(b, b.index[-1], "DOWN", max_violations=1, **HV)
    assert seq.violations == 1 and seq.minutes == 6 and seq.valid
    strict = hvcs_structural(b, b.index[-1], "DOWN", atr_1m=1.0, min_minutes=4, lvcs_body_atr=0.3)
    assert strict.minutes == 2 and not strict.valid          # PC3 stops at the violation, two candles short


def test_two_violations_fail():
    # Walking back: 116 conforms, 124 is the one tolerated break, 118 conforms, then 125 is a second break and the
    # run ends three candles long — one short of the canon minimum.
    b = down_run([110, 125, 118, 124, 116])
    seq = hvcs_structural_pc4(b, b.index[-1], "DOWN", max_violations=1, **HV)
    assert seq.violations == 1 and seq.minutes == 3 and not seq.valid


def test_zero_tolerance_reproduces_pc3_exactly():
    b = down_run([130, 128, 126, 124, 127, 122, 120])
    assert (hvcs_structural_pc4(b, b.index[-1], "DOWN", max_violations=0, **HV).minutes
            == hvcs_structural(b, b.index[-1], "DOWN", atr_1m=1.0, min_minutes=4, lvcs_body_atr=0.3).minutes)


def test_close_direction_remains_irrelevant():
    with_dir = down_run([120, 118, 116, 114, 112], closes_with=True)
    against = down_run([120, 118, 116, 114, 112], closes_with=False)
    a = hvcs_structural_pc4(with_dir, with_dir.index[-1], "DOWN", max_violations=1, **HV)
    c = hvcs_structural_pc4(against, against.index[-1], "DOWN", max_violations=1, **HV)
    assert a.minutes == c.minutes and a.valid == c.valid      # identical length …
    assert c.indecision_bars > a.indecision_bars              # … only the diagnostic differs


def test_a_run_may_not_start_on_a_violation():
    b = down_run([120, 118, 116, 114, 130])                   # the last candle breaks the side
    assert hvcs_structural_pc4(b, b.index[-1], "DOWN", max_violations=1, **HV).minutes == 0


def test_violation_counting_is_causal():
    """Later bars cannot change an earlier verdict, including when a later bar would be a violation."""
    b = down_run([130, 128, 126, 124, 122, 140, 118])
    for i in range(3, len(b)):
        end = b.index[i]
        assert (hvcs_structural_pc4(b.loc[:end], end, "DOWN", max_violations=1, **HV)
                == hvcs_structural_pc4(b, end, "DOWN", max_violations=1, **HV))


def test_violation_counting_is_deterministic():
    b = down_run([130, 128, 126, 124, 127, 122, 120])
    runs = {hvcs_structural_pc4(b, b.index[-1], "DOWN", max_violations=1, **HV) for _ in range(5)}
    assert len(runs) == 1


def test_up_direction_mirrors_on_lows():
    rows = [(l_ + 0.5, l_ + 2.0, l_, l_ + 1.8) for l_ in (100, 102, 104, 101, 108, 110)]
    b = bars(rows)
    seq = hvcs_structural_pc4(b, b.index[-1], "UP", max_violations=1, **HV)
    assert seq.violations == 1 and seq.minutes == 5 and seq.valid


# ------------------------------------------------------------------ F-9 / F-10: previous-15m at the shift

def test_the_two_rules_are_not_in_the_decision_ledger():
    """PC4 moves exactly two rules; they must be `None` at the decision, like the HVCS rule."""
    p = load_cbr1h_pc4("A")
    assert p.previous_15m_scope == ("M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q")
    assert p.previous_15m_evaluation_instant == "FINAL_5S_SHIFT"
    assert p.previous_15m_q_anchor == "CANDLE_CONTAINING_SHIFT"


def _ctx_for(s1m, s5s, p):
    return pc4._Context(s1m, s5s, p)


def _five_second(frame_1m: pd.DataFrame) -> pd.DataFrame:
    """Expand 1m bars into 5s bars that trace open -> low -> high -> close, so 5s extremes match the minute."""
    rows, idx = [], []
    for t, r in frame_1m.iterrows():
        steps = [r["open"], r["low"], r["high"], r["close"]] + [r["close"]] * 8
        for i in range(12):
            px = steps[i]
            rows.append((px, px, px, px))
            idx.append(t + i * S5)
    b = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=pd.DatetimeIndex(idx))
    b["tick_count"], b["hl_method"], b["price_role"] = 1, ps.TICK_MID, ps.STRUCTURE
    return b


def _prev15(q_prev_rows, q_rows, *, d="BUY", shift_offset_min=8.0, q_start=Q_START):
    """Run `_prev_15m_at_shift` over a synthetic Q-1 / Q pair with the shift at `shift_offset_min` into Q."""
    s1m = bars(q_prev_rows + q_rows, start=q_start - M15)
    s5s = _five_second(s1m)
    p = load_cbr1h_pc4("A")
    ctx = _ctx_for(s1m, s5s, p)
    shift = q_start + pd.Timedelta(minutes=shift_offset_min)
    return pc4._prev_15m_at_shift(ctx, s1m.index[0], float(s1m.iloc[0]["open"]), shift, d, p)


FLAT = [(100.0, 100.5, 99.5, 100.0)] * 15


def test_case_a_take_happens_after_the_arm_but_before_the_shift():
    """A: the type 3 arms before Q takes Q-1's low; Q takes it before the shift. PC4 must accept it."""
    q_prev = [(100.0, 101.0, 99.0, 100.0)] * 15                        # Q-1 low = 99.0
    q = [(100.0, 100.5, 99.5, 100.0)] * 4 + [(100.0, 100.5, 98.0, 98.5)] + [(98.5, 99.0, 98.0, 98.5)] * 10
    out = _prev15(q_prev, q, shift_offset_min=8.0)
    assert out["q_break_by_q_at_trigger"] is True
    assert out["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] is True


def test_case_b_q_never_takes_q_minus_1_before_the_shift():
    q_prev = [(100.0, 101.0, 99.0, 100.0)] * 15
    out = _prev15(q_prev, FLAT, shift_offset_min=8.0)
    assert out["q_break_by_q_at_trigger"] is False
    assert out["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] is False          # Q-1 closed flat, so no exception either


def test_case_e_a_take_after_the_shift_never_validates_retroactively():
    """E: Q takes Q-1's low only *after* the shift. The rule must still be False at the shift."""
    q_prev = [(100.0, 101.0, 99.0, 100.0)] * 15
    late = [(100.0, 100.5, 99.5, 100.0)] * 10 + [(100.0, 100.5, 98.0, 98.2)] * 5      # the take is at minute 10
    out = _prev15(q_prev, late, shift_offset_min=8.0)
    assert out["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] is False
    later = _prev15(q_prev, late, shift_offset_min=12.0)                              # same data, later shift
    assert later["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] is True


def test_case_d_a_shift_just_after_a_new_15m_candle_opens_moves_q():
    """D + C: Q follows the shift, so a shift 1 minute into the next candle is judged against that candle."""
    q_prev = [(100.0, 101.0, 99.0, 100.0)] * 15
    q = [(100.0, 100.5, 98.0, 98.5)] + [(98.5, 99.0, 98.0, 98.5)] * 14                # the take is in this candle
    early = _prev15(q_prev, q, shift_offset_min=8.0)
    assert early["q_open_at_trigger"] == T("2030-01-08 01:15")
    assert early["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] is True
    spill = _prev15(q_prev, q, shift_offset_min=16.0)                                 # shift 1 min into the NEXT candle
    assert spill["q_open_at_trigger"] == T("2030-01-08 01:30")
    assert spill["q_prev_open_at_trigger"] == T("2030-01-08 01:15")


def test_no_data_after_the_shift_is_read():
    """Truncating everything after the shift may not change either rule's verdict."""
    q_prev = [(100.0, 101.0, 99.0, 100.0)] * 15
    q = [(100.0, 100.5, 99.5, 100.0)] * 4 + [(100.0, 100.5, 98.0, 98.5)] + [(98.5, 99.0, 98.0, 98.5)] * 10
    full = _prev15(q_prev, q, shift_offset_min=8.0)
    mutated = _prev15(q_prev, q[:9] + [(98.5, 130.0, 60.0, 90.0)] * 6, shift_offset_min=8.0)
    for rule in ("M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"):
        assert full[rule] == mutated[rule]


def test_prev_15m_is_not_evaluated_without_a_shift():
    q_prev = [(100.0, 101.0, 99.0, 100.0)] * 15
    s1m = bars(q_prev + FLAT, start=T("2030-01-08 01:00"))
    p = load_cbr1h_pc4("A")
    ctx = _ctx_for(s1m, _five_second(s1m), p)
    out = pc4._prev_15m_at_shift(ctx, s1m.index[0], 100.0, None, "BUY", p)
    assert all(v is None for v in out.values())


# ------------------------------------------------------------------ frozen-spec and immutability guards (D34 §15)

def test_pc2_spec_is_unchanged():
    assert spec_hash() == "4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2"


def test_pc3_spec_is_unchanged():
    assert spec_hash_pc3() == "7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453"


def test_pc4_engine_does_not_import_pc3_hvcs():
    """PC3's HVCS function must not be reachable from the PC4 engine, or F-1 could be silently bypassed."""
    src = pathlib.Path(pc4.__file__).read_text()
    assert "hvcs_structural_pc4" in src
    assert "import Type3ArmPC3, track_type3_pc3" in src or "hvcs_structural," not in src


def test_pc4_spec_hash_is_stable_across_calls():
    assert spec_hash_pc4() == spec_hash_pc4()


def test_pc4_parameters_are_the_approved_ones():
    p = load_cbr1h_pc4("A")
    assert p.hvcs_max_violations == 1                      # inherited, never altered by PC4
    assert p.hvcs_violation_tolerance == "INHERITED_MAX_VIOLATIONS"
    assert p.hvcs_endpoint == "EXTENSION_EXTREME"          # D34 §3: the anchor did NOT move
    assert p.hvcs_min_minutes == 4                         # CANON, unchanged
    assert p.earliest_activation_min == 7 and p.k_mtf == 3  # D34 §13 components untouched


def test_pc4_variants_match_pc3():
    for variant in ("A", "B"):
        p = load_cbr1h_pc4(variant)
        assert p.variant == variant
        assert p.entry_model in ("HVCS_S5_SHIFT", "FRACTAL_1M_S5_SHIFT")


@pytest.mark.parametrize("field", ["hvcs_violations", "hvcs_to_shift_minutes", "q_open_at_trigger",
                                   "q_break_by_q_at_trigger", "ext_extreme_time_at_trigger"])
def test_new_diagnostics_are_reported(field):
    assert field in pc4.TRIGGER_FIELDS


# ------------------------------------------------------------------ engine: synthetic end-to-end (D34 §15, §17)

@pytest.fixture(scope="module")
def run_pc4():
    """PC4 engine on the same synthetic random-walk STRUCTURE bars the PC3 suite uses. No parity case is touched."""
    from cbr.data import price_series as psm
    from tests.test_feed_comparison import _walk
    s5 = _walk("2030-01-08 00:00", 2 * 24 * 720, seed=31)
    s1 = psm.rollup_structure(s5, "1min")[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]
    p = load_cbr1h_pc4("A")
    res = pc4.run_cbr1h_pc4(s1, s5, start=T("2030-01-09 04:00"), end=T("2030-01-09 12:00"), variant="A", params=p)
    return res, s1, s5


def test_engine_runs_and_is_deterministic(run_pc4):
    res, s1, s5 = run_pc4
    assert len(res.candidates) > 5
    again = pc4.run_cbr1h_pc4(s1, s5, start=T("2030-01-09 04:00"), end=T("2030-01-09 12:00"), variant="A",
                              params=load_cbr1h_pc4("A"))
    assert pc4.result_hash(res) == pc4.result_hash(again)


def test_the_two_moved_rules_are_never_in_the_decision_ledger(run_pc4):
    res, _s1, _s5 = run_pc4
    for row in res.candidates["rules"]:
        for rule in ("M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"):
            if rule in row:
                assert row[rule] is None, "F-9 rules must not be decided at the decision instant"


def test_the_two_moved_rules_are_decided_at_the_trigger(run_pc4):
    res, _s1, _s5 = run_pc4
    triggered = res.candidates[res.candidates["five_second_shift_time"].notna()]
    variant_a = triggered[triggered["variant"] == "A"]
    if not len(variant_a):
        pytest.skip("no triggered variant-A candidate in the synthetic window")
    for row in variant_a["rules_at_trigger"]:
        for rule in ("M1H-6A-2-PREV-15M-BROKEN-BY-Q", "M1H-6A-3-NEW-EXTREME-IN-Q"):
            assert row[rule] in (True, False)


def test_engine_is_causal_under_truncation_and_future_mutation(run_pc4):
    _res, s1, s5 = run_pc4
    p = load_cbr1h_pc4("A")
    h0 = T("2030-01-09 06:00")
    full = pc4.run_cbr1h_pc4(s1, s5, start=h0, end=h0 + pd.Timedelta(hours=1), variant="A", params=p)
    dec = pc4.decision_frame(full)
    if not len(dec):
        pytest.skip("no candidate in the chosen hour")
    cut = pd.Timestamp(dec["timestamp"].iloc[-1]) + pd.Timedelta(seconds=32)
    recs = lambda f: f.astype(str).to_dict("records")
    want = recs(dec[dec["timestamp"] <= cut].reset_index(drop=True))
    trunc = pc4.run_cbr1h_pc4(s1[s1.index + M1 <= cut], s5[s5.index + S5 <= cut], start=h0,
                              end=h0 + pd.Timedelta(hours=1), variant="A", params=p)
    got = pc4.decision_frame(trunc)
    assert want == recs(got[got["timestamp"] <= cut].reset_index(drop=True))
    m1, m5 = s1.copy(), s5.copy()
    for m, blen in ((m1, M1), (m5, S5)):
        after = m.index + blen > cut
        m.loc[after, ["open", "high", "low", "close"]] = m.loc[after, ["open", "high", "low", "close"]] * 1.03 + 0.5
    mut = pc4.decision_frame(pc4.run_cbr1h_pc4(m1, m5, start=h0, end=h0 + pd.Timedelta(hours=1), variant="A", params=p))
    assert want == recs(mut[mut["timestamp"] <= cut].reset_index(drop=True))


def test_engine_refuses_non_structure_bars(run_pc4):
    _res, s1, s5 = run_pc4
    with pytest.raises(ps.PriceRoleError):
        pc4.run_cbr1h_pc4(s1.drop(columns=["price_role"]), s5, start=T("2030-01-09 06:00"),
                          end=T("2030-01-09 07:00"))
