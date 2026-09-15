# CBR1H_BASELINE_V1: Implementation Map (Phase 12)

**Doc:** CBR-ENG-001H · **Version:** v1.0 · 2026-09-15 · **Code:** `src/cbr/engine/cbr1h.py` (+ `common.py`, `params.py`)
· **Spec:** `docs/strategy/1h-cbr-machine-spec.md` + primitives rev 1.2 (D16, D17) · **Params:** `config/strategy.yaml`
(values unchanged; D8 `oe_origin = HOUR_OPEN`, D9 `early_shift_guard = NONE`) · **Price role:** STRUCTURE only

## Architecture

```
STRUCTURE bars (tick mid) ──require_structure──▶ run_cbr1h(s1m, s5s, start, end, variant ∈ {A, B, A-AOI, B-AOI})
  context (causal):  5m/15m/1h roll-ups · ATR(1m,14), ATR(1h,14) · MTF zig-zag on 5m · LTF zig-zag on 1m
                     · track_type3(LTF 1m, latest_pair_only) · 30m/1h close-flip levels (AOI variants)
  per hour H:        hour rules at H.t0 (condition on MTF, 8 h window; TR direction; H open present)
  per candidate:     a stop-order arm opposite H's extension
                       A: HILO arms on 1m and 5m (prior: at bar j−1 close; same: first 5s close after j took j−1's
                          opposite extreme with its entry side unbroken)
                       B: completed LTF type 3 inside H → ≥ 50% pullback of the impulse (not beyond the sweep extreme)
                          → 1m HILO arms inside the pullback
                     every rule on data closed at the arm time; trigger touch / cancellation are lifecycle
  raw setups:        every rule except M1H-COND-04, resolved on STRUCTURE 5s (anchor + target taken at the touch)
  outputs:           candidates (ledger) · hours · ARMED signals (cbr-signal.v1) · hourly_state / htf_provider for CBR15
```

## Rule-by-rule map

| Spec rule | Implementation | Evidence / label | Notes |
|---|---|---|---|
| §2 condition | `classify(MTF 5m swings, window 8 h, as_of = H.t0, min_legs 3)` | CANON thresholds; window/min_legs ASSUMPTION OQ-02/03 | window crosses weekend closures in clock hours (**OQ-40**) |
| M1H-COND-01 / 02 | RANGE or TR required; TREND / UNDEFINED fail | CANON | hour-level |
| M1H-COND-03 | TR with direction NONE → `TREND_DIRECTION_UNRESOLVED` | ASSUMPTION; consistent with D17-4 | hour-level `context_reason` |
| M1H-COND-04 | ≥ 1 raw setup, signal time in [decision − 10 h, decision), TARGET resolved ≤ decision | CANON rule; counts ASSUMPTION OQ-05; resolution basis OQ-36 scope | blocker `PRIOR_SETUP_RESOLUTION_BASIS` |
| M1H-LOC-01 | RANGE: `pos(oe_extreme)` ≥ 0.75 SELL / ≤ 0.25 BUY | CANON E15-015, E1H-002 | range from STRUCTURE 1m |
| M1H-LOC-02 | TR counter: `oe_extreme` beyond last usable MTF swing in OE direction | CANON | |
| M1H-LOC-03 | TR pro: `er(oe_extreme, last MTF leg in cond.direction) ∈ [0.50, 0.75]` | CANON | |
| M1H-LOC-04 | AOI variants: `aoi_tap(H)` | OQ-07 | |
| M1H-OE-01 | `oe_duration_min ≥ 20` | CANON E1H-018 | |
| M1H-OE-02 | `oe_no_pullback` from the hour open (D8 baseline) | CANON; activation ASSUMPTION | re-evaluated each 1m close after arming → `OE_PULLBACK` |
| M1H-OE-04 | `M1H-OE-04a` not two-sided; `M1H-OE-04b` size ≥ 0.5 × ATR(1h,14) | CANON rule; thresholds ASSUMPTION OQ-08 | |
| M1H-OE-05 | opposite wick, size/ATR recorded | diagnostic | |
| M1H-TIME-01 | order active in [max(arm, :22), min(bar end, :52)); must be non-empty | CANON E1H-024 | |
| M1H-TIME-02 | q30 veto for orders active from the :30 candle: pushed ≥ 0.25 × ATR(1m) beyond its open in OE direction before the decision, or :15 candle closed in trade direction | CANON E1H-023; push ASSUMPTION | spec says "fill occurs"; evaluated at decision (**OQ-42**) |
| M1H-TIME-03 | `mih_decision`, `q30_veto_evaluated` recorded | diagnostic | |
| 6A (1) HVCS | longest HVCS in OE direction ending at any closed 1m bar of H up to the decision; valid ≥ 4 min | CANON E1H-034; violations ASSUMPTION | "end_bar ≤ as_of" reading (**OQ-43**) |
| 6A (2) | `oe_prev_candle_break` vs the 15m candle before the one containing the decision | CANON E1H-017 | reference candle (**OQ-41**) |
| 6A (3) | `oe_extreme_time ≥` open of the 15m candle containing the decision | CANON E1H-003 | |
| 6A (4) | HILO arm on 1m, or 5m when the HVCS is LVCS (`M1H-6A-4-HILO-TIER`) | CANON EP2-001…005 | Tom's examples: 5s shift (**OQ-39**) |
| 6B (1) | LTF type 3 BREAK inside H at/after `oe_extreme_time` | CANON E1H-031 | |
| 6B (2-3) | impulse extreme since the break; pullback ≥ 50% and not beyond the sweep extreme | CANON E1H-031 | |
| 6B (4) | 1m HILO arms after the pullback is reached, before invalidation | CANON | |
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
- `state`: `PENDING` (decided, order not yet active) / `ACTIVE` / `ENDED` (cancelled by `as_of`, with `end_reason`) / `TRIGGER_TOUCHED_FILL_UNKNOWN` (STRUCTURE trigger touched by `as_of`; whether it filled needs Phase 14A)
- `confidence`: FULL / REDUCED (missing minutes)

Lifecycle facts appear only once their time is ≤ `as_of`; a truncation test proves the state equals the state computed
from data known at `as_of`.

`htf_provider(result_A)` → `VETO` (opposite raw setup PENDING/ACTIVE) · `NOT_EVALUATED` (opposite raw setup touched:
FILLED unknown) · `CLEAR`. It refuses non-A results.

## Causality protections

STRUCTURE-only guard; rules use bars closed at the arm time; HILO "same" arms use 5s sequencing and never an unseen 5s
bar; lifecycle separated; COND-04 counts outcomes resolved before the decision; truncation + future-mutation tests; the
hourly state is causal (test).

## Implementation readings recorded as open questions

OQ-39 entry trigger vs course examples · OQ-40 condition window across closures · OQ-41 previous-15m reference for
`oe_prev_candle_break` · OQ-42 q30 veto at decision vs at fill · OQ-43 HVCS "end_bar ≤ as_of".
