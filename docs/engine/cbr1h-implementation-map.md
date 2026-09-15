# CBR1H_BASELINE_V1: Implementation Map (Phase 12, updated for D19 / PC1)

**Doc:** CBR-ENG-001H · **Version:** v2.0 (D19) · 2026-09-15 · **Code:** `src/cbr/engine/cbr1h.py` (+ `common.py`, `params.py`)
· **Spec:** `docs/strategy/1h-cbr-machine-spec.md` + primitives rev 1.2 (D16, D17) · **Params:** `config/strategy.yaml`
(D8 `oe_origin = HOUR_OPEN`, D9 `early_shift_guard = NONE` baseline; switches for STRICT COURSE parity) · **Price role:** STRUCTURE only

## Architecture

```
STRUCTURE bars (tick mid) ──require_structure──▶ run_cbr1h(s1m, s5s, start, end, variant ∈ {A, B, A-AOI, B-AOI})
  context (causal):  5m/15m/1h roll-ups · ATR(1m,14), ATR(1h,14) · MTF zig-zag on 5m · LTF zig-zag on 1m
                     · track_type3(LTF 1m) · S5 zig-zag + track_type3(S5, latest_pair_only) · 30m/1h levels (AOI)
  per hour H:        hour rules at H.t0 (condition on MTF, 8 h TRADABLE window; TR direction; H open present)
  per candidate:     one 5s type 3 sweep opposite H's extension (the ENTRY TRIGGER, D19-2), decided at the sweep close
                       A: parent = HVCS running into the shift (end bar = extension-extreme bar; indecision bars keep
                          the respected side); Q−1 broken by Q (or Q−1 closed in trade direction); new extreme in Q
                       B: parent = LTF 1m type 3 known at its break-bar close → ≥ 50% pullback on closed 5s bars (not
                          beyond the sweep extreme) → 5s sweep inside the pullback (most recent live parent)
                     decision rules on data closed at the sweep close; trigger-time fields at the 5s shift;
                     cancellation / anchor path are lifecycle
  prior setups:      raw setups (every rule except M1H-COND-04) FORMED in [H.t0 − 10 h, H.t0); no outcome resolution
  outputs:           candidates (ledger) · hours · ARMED signals (cbr-signal.v1 + entry_structure) ·
                     hourly_state / htf_provider (signal + fill state) for CBR15
```

## Rule-by-rule map

| Spec rule | Implementation | Evidence / label | Notes |
|---|---|---|---|
| §2 condition | `classify(MTF 5m swings, 8 h, as_of = H.t0, min_legs 3, window_start = condition_window(TRADABLE))` | CANON thresholds; window/min_legs ASSUMPTION OQ-02/03; basis ASSUMPTION D19-3 | clock, tradable and missing minutes recorded |
| M1H-COND-01 / 02 | RANGE or TR required; TREND / UNDEFINED fail | CANON | hour-level |
| M1H-COND-03 | TR with direction NONE → `TREND_DIRECTION_UNRESOLVED` | ASSUMPTION; consistent with D17-4 | hour-level `context_reason` |
| M1H-COND-04 | ≥ 1 raw setup FORMED with decision time in [H.t0 − 10 h, H.t0) (`_apply_prior`) | CANON existence D19-1; count/lookback ASSUMPTION OQ-05/36 | `prior_setup_*` fields; played-out status UNKNOWN |
| M1H-LOC-01 | RANGE: `pos(oe_extreme)` ≥ 0.75 SELL / ≤ 0.25 BUY | CANON E15-015, E1H-002 | range from STRUCTURE 1m |
| M1H-LOC-02 | TR counter: `oe_extreme` beyond last usable MTF swing in OE direction | CANON | |
| M1H-LOC-03 | TR pro: `er(oe_extreme, last MTF leg in cond.direction) ∈ [0.50, 0.75]` | CANON | |
| M1H-LOC-04 | AOI variants: `aoi_tap(H)` | OQ-07 | |
| M1H-OE-01 | `oe_duration_min ≥ 20` | CANON E1H-018 | |
| M1H-OE-02 | `oe_no_pullback` from the hour open (D8 baseline) | CANON; activation ASSUMPTION | re-evaluated each 1m close after arming → `OE_PULLBACK` |
| M1H-OE-04 | `M1H-OE-04a` not two-sided; `M1H-OE-04b` size ≥ 0.5 × ATR(1h,14) | CANON rule; thresholds ASSUMPTION OQ-08 | |
| M1H-OE-05 | opposite wick, size/ATR recorded | diagnostic | |
| M1H-TIME-01 | order active in [max(sweep close, :22), :52); a shift before :22 cancels (`S5_SHIFT_BEFORE_WINDOW`) | CANON E1H-024 | |
| M1H-TIME-02 | `_timing30` at `five_second_shift_time`: `timing30_state` PASS / QUALITY_CONCERN / NOT_APPLICABLE / UNRESOLVED | CANON timing point D19-5; veto semantics unresolved (OQ-42); push ASSUMPTION | diagnostic only, never a rule |
| 6A (1) | `M1H-6A-1-HVCS-INTO-SHIFT` via `hvcs_into_shift`: HVCS ending at the extension-extreme bar, ≥ 4 min, indecision bars keep the respected side | CANON E1H-034, D19-6; continuity reading OQ-44 | `hvcs_end_bar`, `hvcs_gap_bars`, blocker OQ-44 |
| 6A (2) | `M1H-6A-2-PREV-15M-BROKEN-BY-Q` via `common.prev_15m_break` (Q's closed 5s bars vs Q−1; exception Q−1 closed in trade direction) | CANON E1H-017, E1H-023; D19-4 | `q_*` fields |
| 6A (3) | `oe_extreme_time ≥` open of the 15m candle containing the decision | CANON E1H-003 | |
| trigger | 5s type 3 sweep in direction d (S5 k, max reversal as CBR15); stop at `t3.trigger_price` | CANON D19-2 (E1H-004, E1H-035) | `five_second_*`, `activation_time`, `m1_hilo_armed_at_decision` |
| 6B (1) | LTF type 3 BREAK inside H at/after `oe_extreme_time`, used from its break-bar close | CANON E1H-031 | `parent_known_at` |
| 6B (2-3) | impulse since the break bar; pullback ≥ 50% on closed 5s bars, not beyond the sweep extreme | CANON E1H-031 | `FRACTAL_PULLBACK_INVALID` |
| D8 / D9 switches | `oe_origin = LAST_RESET` (overextension origin reset) · `ABL-D9-FINAL-PUSH` · `ABL-D9-ALIGN-15M` | ASSUMPTION OQ-22/23 ablations | STRICT COURSE views only |
| M1H-SL-01 | `structure_stop_anchor` (most adverse STRUCTURE 5s extreme of H's extension through activation) + `stop_anchor_path` until the touch/cancel; buffer 0.1 × ATR(1m,14) | CANON; D17-2; buffer ASSUMPTION OQ-11 | fill value resolved by execution |
| M1H-TP-01 | `target_at_activation = anchor − 0.5 × (anchor − H.open)`; "fixed at fill" → execution uses the anchor at fill | CANON E1H-037 | |
| M1H-EXIT-01 | execution layer; raw setups stop at the rollover flat window | CANON EP1-018 | |
| §0/§7 no-trade | `NT_SYDNEY`, `NT_ROLLOVER` at activation and window end; `NT_INCOMPLETE_H` | CANON / IMPL | |
| §1 one fill per hour, one position | not in the engine | IMPL, execution layer | |
| reward check | `IMPL-REWARD` on the decision-time target | IMPL | |

## Hourly state interface for CBR15 (M15-HTF-01)

`hourly_state(result_A, as_of)` returns, for the hour containing `as_of`, every **raw** CBR1H-A setup decided at or
before `as_of`:
- `signal_id`, `decision_time`, `direction`, `entry_model`
- extension state: `oe_dir`, `oe_duration_min`
- timing: `mih_decision`
- `state` (signal state): `PENDING` (decided, order not yet active) / `ACTIVE` / `ENDED` (cancelled by `as_of`, with `end_reason`) / `SHIFT_TRIGGERED` (5s shift broke the trigger by `as_of`)
- `fill_state`: `NOT_EVALUATED` for `SHIFT_TRIGGERED` (whether it filled needs Phase 14A), else `NOT_REQUIRED`
- `confidence`: FULL / REDUCED (missing minutes)

Lifecycle facts appear only once their time is ≤ `as_of`; a truncation test proves the state equals the state computed
from data known at `as_of`.

`htf_provider(result_A)` → `{"signal": VETO | CLEAR, "fill": NOT_EVALUATED | NOT_REQUIRED}`: VETO when an opposite raw
setup is PENDING/ACTIVE; fill NOT_EVALUATED when an opposite setup's shift triggered. The fill state never becomes a
signal veto (D19-15). It refuses non-A results.

## Causality protections

STRUCTURE-only guard; decision rules use bars closed at the sweep close; a 1m bar (OE, HVCS, 1m type 3 parent, HILO
equivalent) is used only after its close; trigger-time fields use bars closed at the shift; lifecycle separated;
COND-04 counts setups formed before H.t0. Tests: truncation and future mutation at a mid-minute cut for decision AND
trigger fields (no 1m leakage into the 5s shift), determinism, ledger completeness, causal hourly state, D8/D9 switches
off by default (hash-identical).

## Implementation readings recorded as open questions

Resolved by D19: OQ-36, OQ-39, OQ-40 (ASSUMPTION), OQ-41, OQ-42 timing, OQ-43 principle. Open: OQ-42 hard veto,
OQ-44 HVCS indecision limit, OQ-45 CBR15 window basis.
