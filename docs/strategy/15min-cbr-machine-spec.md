# CBR15_BASELINE_V1: Machine Specification

**Model id:** `CBR15_BASELINE_V1` · **Primitives:** `CBR_PRIMITIVES_V1` · **Parameters:**
`config/strategy.yaml → models.CBR15_BASELINE_V1` · **Status:** PARITY-CANDIDATE `PC2` (not a validated strategy spec) · **Date:** 2026-09-14 (price roles D16; D19, D20 rulings 2026-09-15)

**D19 changes.** Prior-setup EXISTENCE (OQ-36 C′); M15-HTF-01 signal state separate from fill state (D18-11, D19-15);
trigger-time fields (D19-16); Q−1 broken by Q confirmed (OQ-41). **D20:** "formed" = `raw_setup_armed` (non-recursive);
no Q−1 trade-direction exception; condition window in tradable-market time (OQ-45, ASSUMPTION). Frozen record:
`docs/strategy/parity-candidates/CBR15_BASELINE_V1-PC2.yaml` (PC1 kept for audit).

**Price roles (D16).** All rules in §2-§7 read STRUCTURE (tick-mid) bars; fills and stop/target touches belong to the execution layer (EXECUTION bid/ask bars). The engine never reads bid/ask.

**Scope.** Core reversal Model D (`15min-cbr-spec.md` §6) with `in` rows of the rule matrix, Phase 1/2 definitions
and user decisions D1-D7. **Excluded:** Models A-C (hourly-structure, 15m-structure, continuation), DXY, 5m-candle
confluence, adaptive/external targets, management, pullback entries.

| Variant | `aoi_required` | Why |
|---|---|---|
| `CBR15_BASELINE_V1` | false | 15m course: levels "not as important" (E15-019) |
| `CBR15_BASELINE_V1-AOI` | true | Phase 2 AOI requirement (EP2-023), OQ-07 |

---

## 1. Decision cycle

Evaluated for every 15m candle `Q` (open `Q.t0`, open price `Q.open`); `mic(t)` = minutes since `Q.t0`.

```
IDLE ─(Q opens)─▶ WATCH ─(condition, location, OE, HTF pass; 5s type 3 armed; mic in window)─▶ ARMED
ARMED ─(fill)─▶ IN_TRADE ─(stop | target | forced exit)─▶ CLOSED
ARMED ─(invalidated | Q ends)─▶ WATCH / EXPIRED           any ─(no-trade rule)─▶ BLOCKED(reason)
```

At most one filled trade per 15m candle (IMPL).

## 2. Condition (what)

```
cond = condition_classifier(tier=LTF, W=param.cond.window_hours, as_of=Q.t0)
window basis = param.cond.window_basis (TRADABLE, D20-5, ASSUMPTION): W counts scheduled-tradable minutes; scheduled
closures don't consume it; vendor gaps inside scheduled-open time do. Recorded: condition_elapsed_clock_minutes,
condition_tradable_minutes, condition_missing_minutes.
```

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M15-COND-01 | CBR15-COND-003 | `cond.condition ∈ {RANGE, TRENDING_RANGE}`; `TREND/UNDEFINED` → BLOCKED | CANON |
| M15-COND-02 | CBR15-COND-002 | `param.cond.min_legs (3) ≤ cond.n_legs ≤ param.cond.max_legs (6)`; `< 3` → BLOCKED(RANGE_TOO_BIG); `> 6` → BLOCKED(LOWER_TF_RANGE) | CANON (E15-048) |
| M15-COND-03 | CBR15-COND-004 | `prior_setup_count ≥ param.prior.hard_min_count (1)` where `prior_setup_count` = qualifying CBR15 setups **FORMED** (raw setups: every rule except COND-03 passes and the hourly signal state isn't VETO) with decision time in `[Q.t0 − 60 min, Q.t0)` (`prior_setup_window_start/end`); formed = `raw_setup_armed`, never requiring the setup's own COND-03 (D20-1); else BLOCKED(NO_SETUPS_LAST_HOUR). `prior_setup_count_120m` recorded (slide: "3+ = good"). No outcome is read; `prior_setup_played_out_status = UNKNOWN` (diagnostic) | CANON (E15-049); formation reading owner ruling D19-1 (OQ-36 C′) |
| M15-COND-04 | CBR15-COND-005 | current leg index `cond.n_legs + 1 ≥ 3` (not leg 1 or 2). Upper bound "leg 5" recorded, not filtered (range start undefined) | CANON lower bound; upper diag (OQ-06) |
| M15-COND-05 | CBR15-COND-006/007 | recorded only (hourly setups present? / clarity) | diagnostic |
| M15-COND-06 | D17-4 (OQ-37) | `TRENDING_RANGE` whose direction the classifier can't determine → context failure `TREND_DIRECTION_UNRESOLVED` (no inferred direction) | owner ruling |

## 3. Location (where)

`d = SELL if oe_dir == UP else BUY`.

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M15-LOC-01 | CBR15-LOC-001 | `RANGE`: SELL `pos(oe_extreme) ≥ 0.75`; BUY `≤ 0.25` | CANON |
| M15-LOC-02 | CBR15-LOC-002 (counter) | `TRENDING_RANGE`, `d` counter: `oe_extreme` beyond the most recent **LTF** swing in OE direction ("sells only after taking out highs") | CANON |
| M15-LOC-03 | CBR15-LOC-002 (pro) | `TRENDING_RANGE`, `d` pro: `er(oe_extreme, last LTF leg in cond.direction) ∈ [0.50, 0.75]` | CANON |
| M15-LOC-04 | CBR15-LOC-003 | `oe_prev_candle_break`: Q's own extension extreme takes Q−1's high/low (Q−1 = previous completed 15m candle; an older candle's level doesn't count). No trade-direction exception for CBR15: exceptions aren't transferred between models by analogy; reopen only on CBR15 Level 1 evidence (`q_takes_prev_candle`) | CANON (E15-034); D19-4, D20-3 |
| M15-LOC-05 | CBR15-LOC-005 | SELL above `Q.open`, BUY below | CANON (OQ-14 reading). Satisfied by construction of `oe_dir`; asserted as an invariant test |
| M15-LOC-06 | OQ-07 variant | if `aoi_required`: `aoi_tap(Q)` | variant |

## 4. Overextension (how)

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M15-OE-01 | CBR15-OE-001/002 | `oe_duration ≥ param.oe.min_minutes` (4) | CANON (E15-021, E15-022) |
| M15-OE-02 | CBR15-OE-006 | `oe_no_pullback` | CANON (inherited) |
| M15-OE-03 | CBR15-OE-003/004 | not `oe_two_sided`; `oe_size ≥ param.oe.min_size_atr × ATR(15m,14)` | rule CANON; thresholds ASSUMPTION |
| M15-OE-04 | CBR15-OE-003 | slowing profile, structure formation (`hvcs` on 1m, speed ratio first/second half) recorded | diagnostic (OQ-08) |

## 5. Timing (when)

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M15-TIME-01 | CBR15-TIME-003 | fill at `param.timing.start_mic (7.5) ≤ mic < 15`; orders cancelled at candle close. Evaluated at the actual 5s shift (D19-16): `five_second_shift_time`, `trigger_mic`, `trigger_timing_state` ∈ {IN_WINDOW, TYPE3_RESOLVED_TOO_EARLY, NO_SHIFT}. A type 3 that resolves before mic 7.5 is not a valid entry and is cancelled at the break; a later, independent type 3 is evaluated normally (D17-5, OQ-38) | CANON (E15-027); owner ruling |
| M15-TIME-02 | CBR15-TIME-001 | no session filter beyond canonical no-trade windows | CANON (E15-026) + D3 |
| M15-TIME-03 | CBR15-TIME-004/005 | `mih` anchor (:07/:22/:37/:52), "new 5m candle created the break" flag recorded | diagnostic |

## 6. Higher-timeframe alignment

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M15-HTF-01 | CBR15-HTF-001 | Split (D18-11, D19-15). **SIGNAL state** (the rule): VETO if, in the current hour `H`, a raw `CBR1H_BASELINE_V1-A` setup with direction opposite to `d` is ACTIVE or PENDING at `as_of`; CLEAR otherwise; `NOT_EVALUATED` without the hourly engine (neither pass nor fail). **FILL state** (`htf_fill_state`): `NOT_EVALUATED` when such a setup's 5s shift already triggered (a FILLED hourly trade needs Phase 14A), else `NOT_REQUIRED`. The fill component is `EXECUTION_DEPENDENT`: never a rejection, never part of signal-detection parity; signals carry the blocker `HTF_FILL_STATE_EXECUTION_DEPENDENT` until it is resolved (D17-1, OQ-34) | CANON rule; "active hourly CBR" operationalised by the hourly machine spec (IMPL) |

## 7. Entry, stop, target

```
ARM when Sections 2-6 pass and a type 3 in direction d is armed on tier S5 (B5s) with
    SH (sell) / SL (buy) taken out after Q.t0 and t3 step 2 occurring at or after oe_extreme_time
ORDER: stop at t3.trigger_price                                   # breakout entry on the 5s shift
```

| Rule id | Written rule | Logic | Label |
|---|---|---|---|
| M15-ENTRY-01 | CBR15-ENTRY-001 | 5-second type 3 (Phase 1 definition on `S5` swings) | CANON (E15-037, EP1-008) |
| M15-ENTRY-02 | CBR15-ENTRY-002 | breakout entry only; "wait for 50% pullback on bigger shifts" is **not** implemented in V1 | declared simplification |
| M15-SL-01 | CBR15-SL-001/002 | stop beyond the **stop anchor** + `param.stop.buffer_atr × ATR(1m,14)` + spread. Stop anchor (D17-2, OQ-35) = most adverse STRUCTURE extreme of the active extension (since `Q.open`, 5s bars) observed up to entry activation / fill; spread and the final executable stop are execution-layer. Recorded separately: candle open, extreme at decision, sweep extreme, anchor at activation (+ path), extreme at fill, final stop | CANON; buffer ASSUMPTION; anchor instant owner ruling |
| M15-TP-01 | CBR15-TP-001 | target = `oe_extreme − 0.5 × (oe_extreme − Q.open)` (SELL; mirror BUY) | CANON |
| M15-EXIT-01 | EP1-018 | forced flat at rollover | CANON |

## 8. Ledger row

Same schema as `1h-cbr-machine-spec.md` §7 with `candle_open_utc` for the 15m candle, plus
`n_legs_window, prior_played_out_60m, prior_played_out_120m, leg_index, hourly_opposite_active, mic_fill,
mih_anchor, s5_t3_break_size_atr`.

## 9. Known simplifications (declared)

1. Pullback entry variant on larger 5s shifts not implemented (E15-038).
2. "Decisive extension" and "slowing into the halfway point" are diagnostics only (OQ-08).
3. Leg-number upper bound not enforced (OQ-06).
4. The 15m-vs-hourly veto uses variant A of the hourly model as the definition of an "active hourly CBR".
5. Pine version (later) uses 1m type 3 instead of 5s (`SIMPLIFIED-ENTRY`, D2).
