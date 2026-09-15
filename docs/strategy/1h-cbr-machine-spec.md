# CBR1H_BASELINE_V1: Machine Specification

**Model id:** `CBR1H_BASELINE_V1` · **Primitives:** `CBR_PRIMITIVES_V1` (`cbr-primitives-machine-spec.md`) ·
**Parameters:** `config/strategy.yaml → models.CBR1H_BASELINE_V1` · **Status:** PARITY-CANDIDATE `PC2` (not a validated strategy spec) · **Date:** 2026-09-14 (price roles D16; D19, D20 rulings 2026-09-15)

**D19 changes (Phase 13 readiness).** 5-second shift is the canonical entry trigger (OQ-39); setup structure and entry
trigger are separate; Q−1 must be broken by Q (OQ-41); :30 timing evaluated at the shift, diagnostic only (OQ-42); HVCS
runs directly into the shift (OQ-43, indecision limit OQ-44); prior-setup EXISTENCE, not outcome (OQ-36); condition
window in tradable time (OQ-40, ASSUMPTION). **D20:** "formed" = `raw_setup_armed` (non-recursive); prior window ends at
H.t0; HVCS continuity approved as ASSUMPTION (OQ-44) with diagnostics only. Frozen record:
`docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC2.yaml` (PC1 kept for audit).

**Price roles (D16).** All rules in §2-§6 read STRUCTURE (tick-mid) bars; fills and stop/target touches belong to the execution layer (EXECUTION bid/ask bars). The engine never reads bid/ask.

**Scope.** Only rules marked `in` in `rule-matrix.md`, the Phase 1/2 definitions, and user decisions D1-D7.
**Excluded** (D1 / ablations): fractal-shift & inverse-fractal-shift models, DXY, sessions beyond canonical no-trade
windows, adaptive targets, aggressive stops, trade management, daily-candle bias.

**Variants run as separate, pre-declared configurations** (not a parameter search):

| Variant | `entry_model` | `aoi_required` | Why |
|---|---|---|---|
| `CBR1H_BASELINE_V1-A` | `HVCS_S5_SHIFT` | false | Entry model A: HVCS → 5s shift (E1H-003, E1H-004, E1H-035; D19-2), CBR-course AOI stance |
| `CBR1H_BASELINE_V1-B` | `FRACTAL_1M_S5_SHIFT` | false | Entry model B: 1m type 3 → 50% pullback → 5s shift (E1H-031, E1H-003 slide; D19-2); model choice by volume is discretionary (E1H-032) |
| `CBR1H_BASELINE_V1-A-AOI` | `HVCS_S5_SHIFT` | true | Phase 2 AOI requirement (EP2-023), OQ-07 |
| `CBR1H_BASELINE_V1-B-AOI` | `FRACTAL_1M_S5_SHIFT` | true | same |

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
window basis = param.cond.window_basis (TRADABLE): W counts scheduled-tradable minutes only; scheduled closures
(weekend, daily break) don't consume it; vendor gaps inside scheduled-open time do (D19-3, ASSUMPTION, OQ-40).
Recorded: condition_elapsed_clock_minutes, condition_tradable_minutes, condition_missing_minutes.
```

| Rule id (machine) | Written rule | Logic | Label |
|---|---|---|---|
| M1H-COND-01 | CBR1H-COND-001/002 | `cond.condition ∈ {RANGE, TRENDING_RANGE}` | CANON |
| M1H-COND-02 | CBR1H-COND-003/004 | `cond.condition ∈ {TREND, UNDEFINED}` → **BLOCKED(COND_TREND/UNDEFINED)** | CANON |
| M1H-COND-03 | ASSUMPTION | `TRENDING_RANGE` with `direction == NONE` → BLOCKED(COND_TR_NO_DIR) | ASSUMPTION (OQ-02) |
| M1H-COND-04 | CBR1H-COND-006 | `prior_setup_count ≥ param.prior.min_count` where `prior_setup_count` = number of CBR1H setups **FORMED** (`raw_setup_armed`: every setup rule except the recursive M1H-COND-04 passes, D20-1) with decision time in `[H.t0 − param.prior.lookback_hours, H.t0)`; setups inside the current hour never count (D20-2); `prior_setup_window_start/end` recorded. No target, stop, touch, structure resolution or fill is read. Recorded: `prior_setup_exists`, `prior_setup_count`, `prior_setup_latest_time`, `prior_setup_played_out_status = UNKNOWN` (diagnostic, non-blocking) | CANON rule (existence, D19-1 / OQ-36 C′); count and lookback ASSUMPTION (OQ-05, OQ-36); CBR1H's own semantics, not CBR15's |

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
| M1H-TIME-01 | CBR1H-TIME-001 | the stop order is active only for `param.timing.start_min ≤ mih < param.timing.end_min` (22, 52); a 5s shift breaking before `start_min` cancels the candidate (`S5_SHIFT_BEFORE_WINDOW`); orders cancelled at `end_min` | CANON |
| M1H-TIME-02 | CBR1H-TIME-004 (+ exception TIME-005) | **Diagnostic only (D19-5).** Evaluated at `five_second_shift_time` t_b (never at arm time): if t_b is in the 15m candle opening at :30, `timing30_state = PASS` when that candle traded beyond its own open against the trade by ≥ `param.timing.q30_push_atr × ATR(1m,14)` in `[:30, t_b)` or the :15 candle closed in the trade direction (E1H-023); else `QUALITY_CONCERN`; `NOT_APPLICABLE` outside the :30 candle or without a shift; `UNRESOLVED` when inputs are missing. **Hard-veto semantics UNRESOLVED (OQ-42): never rejects a signal.** | CANON timing point; veto semantics unresolved; threshold ASSUMPTION |
| M1H-TIME-03 | CBR1H-TIME-002/003 | `mih` of fill, `took_prev_15m_extreme` of the trigger's 15m candle recorded | diagnostic |

## 6. Setup structure and entry trigger

**Separation (D19-2).** Every signal records its SETUP STRUCTURE (`entry_model`, `parent_structure_type`,
`parent_structure_time`) apart from its ENTRY TRIGGER (`five_second_sweep_time`, `five_second_shift_level`,
`activation_time`, `five_second_shift_time`). The trigger of both variants is a **5-second type 3** in direction `d` on
S5 swings (primitives §4.1, same S5 parameters as CBR15). A candidate is decided at the close of the 5s sweeping bar
(`timestamp`); its stop order sits at `t3.trigger_price`; the shift completes when a 5s bar breaks it. A 1m HILO is an
observable equivalent recorded as `m1_hilo_armed_at_decision` (closed bars only), never the trigger. A 1m bar is used only
after its close, so 1m information can't reveal the 5s shift earlier than the 5s bars do.

### 6A. `HVCS_S5_SHIFT` (E1H-003 slide card, E1H-004, E1H-034, E1H-035, EP2-001…005; D19-2, D19-4, D19-6)

```
ARM at the 5s sweep close (as_of) when ALL:
  (1) M1H-6A-1-HVCS-INTO-SHIFT: the HVCS runs directly into the shift. End bar = the closed 1m bar that set the extension
      extreme (final displacement bar); hvcs(dir = oe_dir, end = end bar) valid (≥ param.hvcs.min_minutes); every
      closed 1m bar after it up to as_of keeps the respected side (DOWN: high ≤ end-bar high; UP: low ≥ end-bar low).
      No maximum indecision-bar count. Continuity reading ASSUMPTION (OQ-44, D20-4). Diagnostics only, never filters:
      hvcs_start_time, hvcs_end_time, hvcs_extension_extreme_time, bars_between_hvcs_and_shift,
      indecision_bars_between, continuity_state. LVCS recorded, not a tier rule
  (2) M1H-6A-2-PREV-15M-BROKEN-BY-Q: Q = 15m candle containing as_of, Q−1 = previous completed 15m candle; Q's own 5s
      bars closed by as_of take Q−1's high (SELL) / low (BUY), OR Q−1 closed in the trade direction (exception,
      E1H-023, V1H-1m_fractal_shift 00:03:23). The hour-wide extreme taking an older level doesn't count
  (3) M1H-6A-3-NEW-EXTREME-IN-Q: Q has made a new oe_extreme after Q.open
  (4) a 5s type 3 in direction d is swept (the candidate)
  and Sections 2-5 pass
ORDER: stop at t3.trigger_price (five_second_shift_level)
```

The former tier rule (`HILO on B1m, or B5m when LVCS`) is superseded by the 5s trigger (D19-2).

### 6B. `FRACTAL_1M_S5_SHIFT` (E1H-031, E1H-003 slide "1m T3, 50% pullback, 5s T3 Fractal Shift"; D19-2)

```
(1) parent: a bearish (for SELL) type 3 on tier LTF breaks within H at t3.break_time ≥ oe_extreme_time; recognised at
    the break bar's close (parent_known_at)
(2) impulse = [t3.sweep_extreme → most extreme 5s price since the break bar]
(3) PULLBACK: closed 5s bars after parent_known_at retrace ≥ param.fractal.pullback_min (0.50) of the impulse, not beyond
    t3.sweep_extreme (else the pattern is invalid: FRACTAL_PULLBACK_INVALID)
(4) TRIGGER: a 5s type 3 in direction d swept at or after the pullback and before invalidation (most recent live parent)
ARM at (4) and Sections 2-5 pass
ORDER: stop at t3.trigger_price
```

### 6D. Parity-view switches (D8/D9; STRICT COURSE parity only)

| Setting | Baseline (PC1) | Pre-registered alternative, one at a time |
|---|---|---|
| `oe_origin` | `HOUR_OPEN` | `LAST_RESET`: a ≥ 50% pullback restarts OE duration/no-pullback from its most adverse price; extreme, size and stop/target inputs stay from the hour open |
| `early_shift_guard` | `NONE` | `FINAL_PUSH`: rule `ABL-D9-FINAL-PUSH`, the sweep bar sets the hour's 5s extreme at decision · `ALIGN_15M`: rule `ABL-D9-ALIGN-15M`, Q took Q−1's high/low (no exception) |

### 6C. Stop, target, exit (both models)

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M1H-SL-01 | CBR1H-SL-001 | stop = stop anchor ± `param.stop.buffer_atr × ATR(1m,14)` ± spread; stop anchor = most adverse STRUCTURE extension extreme observed up to activation / fill (D17-2), carried as anchor at activation + path; spread and the final stop are execution-layer | CANON; buffer ASSUMPTION (OQ-11) |
| M1H-TP-01 | CBR1H-TP-001 | target = `oe_extreme − 0.5 × (oe_extreme − H.open)` (SELL; mirror BUY), fixed at fill | CANON |
| M1H-EXIT-01 | EP1-018 | forced flat at rollover time | CANON |
| M1H-EXIT-02 | none | no other exits in V1 | Scope |

## 7. Signal ledger row (every ARMED, FILLED, EXPIRED, BLOCKED event)

`signal_id, model_id, variant, event, event_time_utc, hour_open_utc, direction, entry_model, parent_structure_type,
parent_structure_time, five_second_sweep_time, five_second_shift_level, five_second_shift_time, activation_time,
m1_hilo_armed_at_decision, hvcs_start_time, hvcs_end_time, hvcs_extension_extreme_time, bars_between_hvcs_and_shift,
indecision_bars_between, continuity_state, raw_setup_armed, prior_setup_window_start, prior_setup_window_end, q_break_by_q, q_prev_closed_in_trade_direction, timing30_state,
prior_setup_exists, prior_setup_count, prior_setup_latest_time, prior_setup_played_out_status,
condition_elapsed_clock_minutes, condition_tradable_minutes, condition_missing_minutes, oe_origin, early_shift_guard,
cond.condition, cond.c_med, cond.n_legs, cond.direction, pos_oe_extreme, er_pro, beyond_external,
oe_dir, oe_size, oe_size_atr, oe_duration_min, oe_opposite_wick, oe_two_sided, oe_prev_candle_break,
aoi_tap, aoi_level_tf, hvcs_minutes, hvcs_body_atr, lvcs_fallback_5m, hilo_break_size, t3_close_beyond,
t3_break_size_atr, mih_fill, took_prev_15m_extreme,
entry, stop, target, risk, reward, rr, spread_at_fill, rules_passed[], rules_failed[], blocked_reason,
outcome, exit_time, exit_price, r_multiple, mfe_r, mae_r, data_quality_flags[]`

Diagnostics exist so Phase 17-18 can test whether they add information. They are never used as filters in V1.

## 8. Known simplifications (declared)

1. Model selection by volume (E1H-032) is replaced by running both entry models as separate variants.
5. Unresolved in PC2 (never silently affecting eligibility): `:30` hard veto (OQ-42). Assumptions: HVCS continuity
   (OQ-44), tradable-time window (OQ-40), 10 h prior lookback ending at H.t0 (OQ-05/36).
   Execution-dependent: fills, one fill per hour, final stop (Phase 14A).
2. "Decisive / high volume" (E1H-019, OQ-08) only enters through the `min_size_atr` floor and HVCS structure; its
   richer meaning is diagnostic.
3. Swing detection is an ATR zig-zag (OQ-01); results must be checked for sensitivity to `swing.*.k`.
4. Adaptive targets, aggressive stops, trailing, time stops, scaling, DXY, daily bias, TIME-003 as a filter:
   **out**, tested as single-rule ablations.

## 9. Parity checkpoints (Phase 13)

Course examples the V1 engine must be evaluated against (`research/examples/course_examples.jsonl`):
CX-LT1-1 (2025-10-21 ~01:39 UTC, BUY), CX-TE1-1 (2025-10-24 ~04:37 UTC, BUY), CX-LT3-2 (2025-11-10 01:40 UTC, SELL).
Each outcome is classified as: reproduced / code bug / data difference / declared simplification / source ambiguity.

**V-1 (owner ruling D16-3, hard requirement).** Phase 13 parity cannot be declared complete until tick-mid STRUCTURE has been compared against a representative TradingView FOREXCOM:XAUUSD export for the course-example windows (CBR-DEC-025 V-1). Material structure differences stop parity and reopen OQ-25. The source is never chosen by which produces better trades.
