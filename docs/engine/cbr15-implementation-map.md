# CBR15_BASELINE_V1: Implementation Map (Phase 11)

**Doc:** CBR-ENG-015 · **Version:** v1.1 (owner ruling D17) · 2026-09-15 · **Code:** `src/cbr/engine/cbr15.py`, `src/cbr/engine/params.py`
· **Spec:** `docs/strategy/15min-cbr-machine-spec.md` + `cbr-primitives-machine-spec.md` rev 1.2 · **Params:**
`config/strategy.yaml` (values unchanged) · **Price role:** STRUCTURE only (D16)

## Architecture

```
canonical STRUCTURE bars (tick mid, D16) ──require_structure──▶ run_cbr15(s1m, s5s, start, end, variant, htf, dxy_context)
  precompute (causal):  ATR(1m,14) · LTF zig-zag swings on 1m · S5 zig-zag swings on 5s · ATR(15m,14) on 15m roll-up
                        · track_type3(S5, latest_pair_only=True) → every 5s sweep ("arm") and how it ended
  per 15m candle Q:     candle rules at Q.t0 (condition, legs, completeness)
  per candidate:        a 5s type 3 sweep inside Q in the direction opposite Q's overextension
                        decision time = close of the sweeping 5s bar; every rule evaluated on data closed at that time
                        lifecycle (after the decision): break-before-window, T3 timeout/new swing, OE pullback, window end
  raw setups:           candidates passing everything except COND-03 (and HTF when not evaluated), resolved on STRUCTURE
                        5s bars (touch → target vs stop, stop first) for M15-COND-03 only
  outputs:              candidates (ledger: every rule outcome) · candles · ARMED signals (cbr-signal.v1 shape)
```

Not in the engine (by design): fills, spread, slippage, stop/target touches for trades, one-position and one-fill-per-
candle enforcement (Phase 14A execution layer; EXECUTION bars). The engine never reads bid/ask; a static test enforces it.

## Rule-by-rule map

| Spec rule | Implementation | Evidence / label | Notes |
|---|---|---|---|
| §0 bars, causality | `require_structure`; `usable()`; `_atr_at` (bar close ≤ as_of); `DECISION_FIELDS` | IMPL; D16 | Truncation + future-mutation tests on real data |
| §1 swings (LTF 1m, S5 5s) | `zigzag` with k = 3.0 × ATR(14) | ASSUMPTION OQ-01 | unchanged primitive |
| §2 condition classifier | `condition.classify(tier LTF, W = 2 h, as_of = Q.t0)` | CANON thresholds E1H-007/008, E15-014; ASSUMPTION median, window OQ-02/03 | range_high/low from STRUCTURE 1m |
| M15-COND-01 | `condition ∈ {RANGE, TRENDING_RANGE}` | CANON | candle-level |
| M15-COND-02 | `3 ≤ n_legs ≤ 6`; reason RANGE_TOO_BIG / LOWER_TF_RANGE | CANON E15-048 | candle-level |
| M15-COND-03 | ≥ 1 raw setup, signal time in [Q.t0 − 60 min, Q.t0), TARGET resolved ≤ Q.t0 (stop from the anchor through the touch); 120 min count recorded | CANON E15-049; **interpretation not approved (D17-3, OQ-36)** | unchanged; blocker `COND03_INTERPRETATION_UNAPPROVED (OQ-36)`; `baseline_eligible = False` |
| M15-COND-04 | `n_legs + 1 ≥ 3` | CANON E15-050 | upper bound diagnostic (OQ-06) |
| M15-COND-05 | not implemented as a rule (diagnostic in spec) | diagnostic | n/a |
| M15-LOC-01 | RANGE: SELL `pos(oe_extreme) ≥ 0.75`, BUY `≤ 0.25` | CANON E15-015 | |
| M15-LOC-02 | TR counter: `oe_extreme` beyond last usable LTF swing in OE direction | CANON | |
| M15-LOC-03 | TR pro: `er(oe_extreme, last LTF leg in cond.direction) ∈ [0.50, 0.75]` | CANON E15-015 | |
| M15-COND-06 (TR, direction NONE) | candle rule `M15-COND-TR-DIRECTION`; `context_reason` / `reject_reasons` = `TREND_DIRECTION_UNRESOLVED` | owner ruling D17-4 (OQ-37 resolved) | no inferred direction |
| M15-LOC-04 | `oe_prev_candle_break` vs previous 15m STRUCTURE candle | CANON E15-034 | |
| M15-LOC-05 | asserted invariant | CANON (OQ-14 reading) | |
| M15-LOC-06 | AOI variant: `aoi_tap` on 30m/1h close-flip levels | variant OQ-07 | only `AOI` variant |
| M15-OE-01 | `oe_duration_min ≥ 4` (1m bar of the extreme − Q.t0) | CANON E15-021/022 | |
| M15-OE-02 | `oe_no_pullback` from Q.open (candle open origin) | CANON E1H-018 inherited; activation ASSUMPTION OQ-08 | re-evaluated each 1m close after arming → lifecycle `OE_PULLBACK` |
| M15-OE-03 | `M15-OE-03a` not two-sided; `M15-OE-03b` size ≥ 0.5 × ATR(15m,14) | rule CANON; thresholds ASSUMPTION OQ-08 | |
| M15-OE-04 | HVCS minutes/body, recorded | diagnostic | |
| M15-TIME-01 | decision: fill window 7.5 ≤ mic < 15 still open; order active from max(decision, Q.t0 + 7.5 min) to Q close | CANON E15-027; D17-5 | lifecycle `TYPE3_RESOLVED_TOO_EARLY` if the structure break precedes 7.5 min; never resurrected |
| M15-TIME-02 | only canonical no-trade windows (`NT_SYDNEY`, `NT_ROLLOVER`) at activation and window end | CANON E15-026, EP1-017/018, D3 | |
| M15-TIME-03 | `mic_structure_touch` recorded | diagnostic | |
| M15-HTF-01 | injected `htf(as_of, d)`; default `NOT_EVALUATED` → rule `None` (`rules_not_evaluated`, never `rules_failed`), blocker `HTF_NOT_EVALUATED (OQ-34)` | CANON rule; D17-1 | rerun with the CBR1H state after Phase 12 |
| §7 ARM / type 3 | `track_type3` sweeps; candidate direction must oppose OE; `M15-T3-01` sweep at/after `oe_extreme_time` | CANON E15-037, EP1-008 | latest-pair reading **F-3** |
| M15-ENTRY-02 | breakout only | declared simplification | |
| M15-SL-01 | `_anchor_path`: `structure_stop_anchor` = most adverse STRUCTURE 5s extreme of the extension through activation, `stop_anchor_time`, `stop_anchor_source`, `stop_anchor_path` until the order ends (`anchor_at(t)`); kept apart: `candle_open_price`, `extension_extreme_at_decision`, `sweep_extreme`, `structure_extreme_at_fill` (execution), `final_execution_stop` (14A); buffer 0.1 × ATR(1m,14) | CANON; buffer ASSUMPTION OQ-11; anchor D17-2 | OQ-28 open |
| M15-TP-01 | `target = oe_extreme − 0.5 × (oe_extreme − Q.open)` | CANON E15-039 | |
| M15-EXIT-01 | forced flat: execution layer; raw-setup resolution stops at the rollover flat window | CANON EP1-018 | |
| §8 reward check | `IMPL-REWARD`: trigger must be on the reward side of the target | IMPL | |
| §8 one position / one fill per candle | not in engine; every candidate is emitted | IMPL, execution layer | |
| NT_INCOMPLETE | Q open bar present; previous 15m candle complete; Q complete up to the decision | IMPL | |

## Implementation findings

- **F-3 · Type 3 pairing across newer swings.** `find_type3` (Phase 8) kept an unswept swing pair armed after newer
  swings confirmed. Spec §4.1 says "the last two confirmed swings". `track_type3(latest_pair_only=True)` applies the spec
  literally for the engine. `find_type3` keeps its historical behaviour, verified identical (same events, same order) on
  4 real days × 2 reversal settings, so the Phase 9 parity notes aren't silently changed.
- **Performance.** The type 3 tracker is ~70× faster than the Phase 8 loop; a 12 h window runs in under a second.

## Causality protections

1. STRUCTURE-only access guard at the engine entry.
2. Every rule input uses bars with close ≤ decision time (`usable`, `_atr_at`, OE on closed 1m, 15m roll-up ATR on closed candles, previous-candle completeness).
3. Post-decision events are lifecycle fields, never rule inputs.
4. COND-03 counts only raw setups resolved at or before the candle open.
5. Tests: decision frames unchanged under data truncation and under price mutation after the cut (3 cut times, real data); report runner repeats truncation checks per window.

## Open questions (status after D17)

OQ-34 open until Phase 12 · OQ-35 resolved (D17-2) · OQ-36 open, evidence package required · OQ-37 resolved (D17-4) ·
OQ-38 resolved (D17-5). **CBR15 is not baseline-eligible** (`docs/governance/g11-approval.md`).

## D19 update (Phase 13 readiness, parity-candidate PC1)

| Spec rule | Implementation | Evidence / label |
|---|---|---|
| M15-COND-03 | `_apply_prior_rule`: raw setups (every rule except COND-03; hourly signal state not VETO) FORMED with decision time in [Q.t0 − 60 min, Q.t0); `prior_setup_exists`, `prior_setup_count`, `prior_setup_count_120m`, `prior_setup_latest_time`, `prior_setup_played_out_status = UNKNOWN`. Raw-setup outcome resolution (`_resolve_raw_outcomes`, `_structure_outcome`) removed | CANON E15-049; D19-1 (OQ-36 C′) |
| M15-HTF-01 | `htf(as_of, d)` → `{"signal", "fill"}`; rule = signal state (`htf_signal_state`); `htf_fill_state` recorded, never a rule; blocker `HTF_FILL_STATE_EXECUTION_DEPENDENT` on every candidate | D18-11, D19-15 |
| M15-TIME-01 at the trigger | `five_second_shift_time`, `trigger_mic`, `trigger_timing_state` (IN_WINDOW / TYPE3_RESOLVED_TOO_EARLY / NO_SHIFT); `TRIGGER_FIELDS` with their own causality test | D19-16 |
| M15-LOC-04 | unchanged: Q's own extreme vs Q−1 (`q_prev_high/low` recorded); no exception for CBR15 | D19-4 |
| condition window | CLOCK (unchanged; OQ-45) | ASSUMPTION |

Eligibility blockers now: `HTF_SIGNAL_STATE_NOT_EVALUATED` (only without the hourly engine), `HTF_FILL_STATE_EXECUTION_DEPENDENT`,
`PHASE13_PARITY_NOT_RUN`. The OQ-36 blocker is gone (resolved).
