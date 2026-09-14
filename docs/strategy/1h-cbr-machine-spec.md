# CBR1H_BASELINE_V1: Machine Specification

**Model id:** `CBR1H_BASELINE_V1` · **Primitives:** `CBR_PRIMITIVES_V1` (`cbr-primitives-machine-spec.md`) ·
**Parameters:** `config/strategy.yaml → models.CBR1H_BASELINE_V1` · **Status:** draft for review · **Date:** 2026-09-14

**Scope.** Only rules marked `in` in `rule-matrix.md`, the Phase 1/2 definitions, and user decisions D1-D7.
**Excluded** (D1 / ablations): fractal-shift & inverse-fractal-shift models, DXY, sessions beyond canonical no-trade
windows, adaptive targets, aggressive stops, trade management, daily-candle bias.

**Variants run as separate, pre-declared configurations** (not a parameter search):

| Variant | `entry_model` | `aoi_required` | Why |
|---|---|---|---|
| `CBR1H_BASELINE_V1-A` | `HVCS_HILO` | false | Entry model A (E1H-003), CBR-course AOI stance |
| `CBR1H_BASELINE_V1-B` | `FRACTAL_1M` | false | Entry model B (E1H-031); model choice by volume is discretionary (E1H-032) |
| `CBR1H_BASELINE_V1-A-AOI` | `HVCS_HILO` | true | Phase 2 AOI requirement (EP2-023), OQ-07 |
| `CBR1H_BASELINE_V1-B-AOI` | `FRACTAL_1M` | true | same |

---

## 1. Decision cycle

Evaluated for every hourly candle `H` (open time `H.t0`). All checks at `as_of` = the current `B5s`/`B1m` close.

```
IDLE ──(H opens)──────────────────────────────────────────────▶ WATCH
WATCH ──(condition + location + OE rules pass, mih ∈ timing window)──▶ ARMED (trigger pattern armed → stop order)
ARMED ──(stop order fills)──▶ IN_TRADE ──(stop | target | forced exit)──▶ CLOSED
ARMED ──(pattern invalidated | OE invalidated | window ends)──▶ back to WATCH or EXPIRED
any ──(no-trade rule)──▶ BLOCKED(reason)
```

At most **one filled trade per hourly candle** (IMPL). Every transition writes a ledger row with rule outcomes (Section 7).

---

## 2. Condition (what)

```
cond = condition_classifier(tier=MTF, W=param.cond.window_hours, as_of = H.t0)     # evaluated at candle open
```

| Rule id (machine) | Written rule | Logic | Label |
|---|---|---|---|
| M1H-COND-01 | CBR1H-COND-001/002 | `cond.condition ∈ {RANGE, TRENDING_RANGE}` | CANON |
| M1H-COND-02 | CBR1H-COND-003/004 | `cond.condition ∈ {TREND, UNDEFINED}` → **BLOCKED(COND_TREND/UNDEFINED)** | CANON |
| M1H-COND-03 | ASSUMPTION | `TRENDING_RANGE` with `direction == NONE` → BLOCKED(COND_TR_NO_DIR) | ASSUMPTION (OQ-02) |
| M1H-COND-04 | CBR1H-COND-006 | `prior_played_out ≥ param.prior.min_count` where `prior_played_out` = number of **raw setups** (setups passing every rule except M1H-COND-04 and the one-position rule, simulated with the same stop/target) whose outcome was **TARGET before STOP** and resolved before `as_of`, with signal time in `[as_of − param.prior.lookback_hours, as_of)` | CANON rule; counts/lookback ASSUMPTION (OQ-05) |

Raw setups use only past, closed outcomes, so there's no lookahead (IMPL).

## 3. Location (where)

Evaluated at arming time with the current `oe_extreme` of `H`. Trade direction `d = SELL if oe_dir == UP else BUY`.

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M1H-LOC-01 | CBR1H-LOC-001 | if `RANGE`: SELL requires `pos(oe_extreme) ≥ param.loc.range_extreme` (0.75); BUY requires `≤ 1 − 0.75` | CANON (E15-015, E1H-002) |
| M1H-LOC-02 | CBR1H-LOC-003 | if `TRENDING_RANGE` and `d` is **counter** to `cond.direction`: `oe_extreme` beyond the most recent **external (MTF) swing** in the OE direction (SELL: `> last MTF SwingHigh.price`) | CANON |
| M1H-LOC-03 | CBR1H-LOC-002 | if `TRENDING_RANGE` and `d` is **pro** `cond.direction`: `er(oe_extreme, last MTF leg in cond.direction) ∈ [param.loc.pro_er_min, param.loc.pro_er_max]` (0.50, 0.75) | CANON |
| M1H-LOC-04 | OQ-07 variant | if `aoi_required`: `aoi_tap(H)` true | CANON (Phase 2) as variant |

## 4. Overextension (how)

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M1H-OE-01 | CBR1H-OE-001 | `oe_duration ≥ param.oe.min_minutes` (20) | CANON |
| M1H-OE-02 | CBR1H-OE-002 | `oe_no_pullback` (50% of running extension) | CANON |
| M1H-OE-03 | CBR1H-OE-003 | covered by M1H-LOC-01/02/03 (extension into range extreme / beyond structure / into pullback zone) | CANON |
| M1H-OE-04 | CBR1H-OE-004 | not `oe_two_sided` **and** `oe_size ≥ param.oe.min_size_atr × ATR(1h,14)` ("sideways hour" invalid) | CANON rule; thresholds ASSUMPTION (OQ-08) |
| M1H-OE-05 | CBR1H-OE-005/006 | `oe_opposite_wick`, `oe_size_atr` recorded, **not filtered** | diagnostic |

The OE is re-evaluated continuously; if `oe_no_pullback` fails before a fill, the setup returns to WATCH (a new
extension may start only if all OE rules pass again with the same `H.open`).

## 5. Timing (when)

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M1H-TIME-01 | CBR1H-TIME-001 | entry fill time satisfies `param.timing.start_min ≤ mih ≤ param.timing.end_min` (22, 52); orders cancelled at `end_min` | CANON |
| M1H-TIME-02 | CBR1H-TIME-004 (+ exception TIME-005) | **Veto** if the fill occurs in the 15m candle opening at :30 and that candle, before the trigger, never traded beyond its own open in the OE direction by at least `param.timing.q30_push_atr × ATR(1m,14)` (it "opened straight in the trade direction"). **Exception:** not vetoed if the 15m candle opening at :15 closed in the trade direction (E1H-023). | CANON rule; push threshold ASSUMPTION |
| M1H-TIME-03 | CBR1H-TIME-002/003 | `mih` of fill, `took_prev_15m_extreme` of the trigger's 15m candle recorded | diagnostic |

## 6. Entry models, stop, target

### 6A. `HVCS_HILO` (E1H-003 slide card, E1H-034, E1H-035, EP2-001…005)

```
ARM when ALL at as_of:
  (1) hvcs(dir = oe_dir, end_bar ≤ as_of) valid (duration ≥ param.hvcs.min_minutes)          # "HVCS, 4+ mins"
  (2) oe_prev_candle_break                                                                   # "beyond prev LTF/MTF high"
  (3) the current 15m candle Q (containing as_of) has made a new oe_extreme after Q.open     # "after 15m open, PA
                                                                                               #  creates wick / pushes a bit more"
  (4) a HILO in direction d is armed on B1m (or B5m if hvcs.body_atr < lvcs threshold)       # "HILO beyond structure"
  and Sections 2-5 pass
ORDER: stop at hilo.trigger_price
```

### 6B. `FRACTAL_1M` (E1H-031)

```
(1) Bearish (for SELL) type 3 on tier LTF completes at t3.trigger_time within H, after oe_extreme_time
(2) impulse = [t3.sweep_extreme → lowest low from t3.trigger_time to now]
(3) PULLBACK: price retraces ≥ param.fractal.pullback_min (0.50) of impulse          # "pullback towards 50%"
    and not beyond t3.sweep_extreme (else pattern invalid)
(4) REACTION: a HILO in direction d arms on B1m inside the pullback                  # "reaction… 1m high low"
ARM at (4) and Sections 2-5 pass
ORDER: stop at hilo.trigger_price
```

### 6C. Stop, target, exit (both models)

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M1H-SL-01 | CBR1H-SL-001 | stop = `oe_extreme (at fill) ± param.stop.buffer_atr × ATR(1m,14) ± spread` (beyond the extreme) | CANON; buffer ASSUMPTION (OQ-11) |
| M1H-TP-01 | CBR1H-TP-001 | target = `oe_extreme − 0.5 × (oe_extreme − H.open)` (SELL; mirror BUY), fixed at fill | CANON |
| M1H-EXIT-01 | EP1-018 | forced flat at rollover time | CANON |
| M1H-EXIT-02 | none | no other exits in V1 | Scope |

## 7. Signal ledger row (every ARMED, FILLED, EXPIRED, BLOCKED event)

`signal_id, model_id, variant, event, event_time_utc, hour_open_utc, direction, entry_model,
cond.condition, cond.c_med, cond.n_legs, cond.direction, pos_oe_extreme, er_pro, beyond_external,
oe_dir, oe_size, oe_size_atr, oe_duration_min, oe_opposite_wick, oe_two_sided, oe_prev_candle_break,
aoi_tap, aoi_level_tf, hvcs_minutes, hvcs_body_atr, lvcs_fallback_5m, hilo_break_size, t3_close_beyond,
t3_break_size_atr, mih_fill, q30_veto_evaluated, took_prev_15m_extreme, prior_played_out,
entry, stop, target, risk, reward, rr, spread_at_fill, rules_passed[], rules_failed[], blocked_reason,
outcome, exit_time, exit_price, r_multiple, mfe_r, mae_r, data_quality_flags[]`

Diagnostics exist so Phase 17-18 can test whether they add information. They are never used as filters in V1.

## 8. Known simplifications (declared)

1. Model selection by volume (E1H-032) is replaced by running both entry models as separate variants.
2. "Decisive / high volume" (E1H-019, OQ-08) only enters through the `min_size_atr` floor and HVCS structure; its
   richer meaning is diagnostic.
3. Swing detection is an ATR zig-zag (OQ-01); results must be checked for sensitivity to `swing.*.k`.
4. Adaptive targets, aggressive stops, trailing, time stops, scaling, DXY, daily bias, TIME-003 as a filter:
   **out**, tested as single-rule ablations.

## 9. Parity checkpoints (Phase 13)

Course examples the V1 engine must be evaluated against (`research/examples/course_examples.jsonl`):
CX-LT1-1 (2025-10-21 ~01:39 UTC, BUY), CX-TE1-1 (2025-10-24 ~04:37 UTC, BUY), CX-LT3-2 (2025-11-10 01:40 UTC, SELL).
Each outcome is classified as: reproduced / code bug / data difference / declared simplification / source ambiguity.
