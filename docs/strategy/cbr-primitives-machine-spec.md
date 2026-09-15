# CBR Shared Primitives: Machine Specification

**Version:** `CBR_PRIMITIVES_V1` (spec rev 1.4: D20 CBR15 window basis TRADABLE, HVCS continuity ASSUMPTION; rev 1.3: D19 window basis, HILO role, HVCS end bar; rev 1.2: price roles per D16; rev 1.1: type 3 pairing fix F-0) · **Status:** PARITY-CANDIDATE PC2 · **Date:** 2026-09-15

Deterministic definitions used by `CBR1H_BASELINE_V1` and `CBR15_BASELINE_V1`. Every numeric value lives in
`config/strategy.yaml`; this document refers to parameters by name (`param.*`). Each definition cites its
evidence; anything not fixed by the sources is marked **ASSUMPTION** and its value is a declared placeholder with
a research range, never an optimized number.

**Label legend.** `CANON` = directly specified by Level 1 source · `ASSUMPTION` = unspecified by sources, value
chosen for implementability (linked OQ) · `IMPL` = engineering necessity with no trading content (e.g. causality).

---

## 0. Global conventions (IMPL)

| Item | Definition |
|---|---|
| Time | All timestamps UTC, `timestamp[ns, UTC]`, bar **open** time. A bar with open `t` and length `Δ` is *closed* at `t+Δ` and usable only for decisions at or after `t+Δ`. |
| Price roles (D16) | **STRUCTURE** price = tick-derived mid `(bid+ask)/2` (`hl_method = TICK_MID`, `price_role = STRUCTURE`). Every primitive in §1-§7 reads STRUCTURE bars only. **EXECUTION** price = tick-derived bid and ask OHLC (`price_role = EXECUTION`), read only by §8 execution semantics (fills, stop/target touches, spread). One OHLC series is never used for both; enforced by access guards (`cbr.data.price_series`). Dukascopy candle-file mid highs/lows (`SIDE_EXTREME_MEAN`) and GC futures are never canonical extremes (CBR-DEC-025). |
| Bars | STRUCTURE `B5s`, `B1m` built from Dukascopy ticks (D2); `B5m`, `B15m`, `B1h`, `B1d` rolled up from STRUCTURE `B1m`, clock-aligned (15m at :00/:15/:30/:45; 1h on the hour). EXECUTION `B5s` (bid/ask) built from the same ticks. |
| Minute-in-hour | `mih(t) = minutes(t) + seconds(t)/60` of UTC clock time. Timezone-invariant for whole-hour offsets. |
| Gaps | A candle with any missing constituent `B1m` bar is `INCOMPLETE`; no setup may use an incomplete candle (missing data lowers confidence, never silently filled). |
| Causality | Every function below takes `as_of` time and may read only bars closed at or before `as_of`. Enforced by a lookahead test (future bars mutated → identical outputs). |
| ATR | `ATR(tf, n)` = Wilder ATR on closed bars of timeframe `tf`, length `n`. |
| Tick | XAUUSD tick size `param.tick` (0.01). |

---

## 1. Swing points (OQ-01)

No source gives an objective pivot rule. Tom: swing choice is "intuitive" (P2G-16). The only definitional
statements are "SWING occurs when price breaks an old High or Low" (P1F-3) and "only external breaks are shifts"
(EP2-018).

**Definition. Causal ATR zig-zag per tier** (`ASSUMPTION`, OQ-01)

For tier `τ ∈ {LTF, MTF, S5}` with bar series `B_τ`, threshold `R_τ(t) = param.swing.<τ>.k × ATR(<τ tf>, 14)`:

```
state: dir ∈ {UP, DOWN}, ext_price, ext_time
on each closed bar b:
  if dir == UP:
     if b.high > ext_price: ext_price, ext_time = b.high, b.open_time
     elif ext_price - b.low >= R_τ:                      # reversal threshold reached
          emit SwingHigh(price=ext_price, time=ext_time, confirmed_at=b.close_time)
          dir = DOWN; ext_price, ext_time = b.low, b.open_time
  else: mirror (SwingLow on ext_price - ... ; uses b.high - ext_price >= R_τ)
```

| Tier | Bars | Purpose | `k` default | Research range |
|---|---|---|---|---|
| `S5` | `B5s` | seconds-chart shifts (15m entry trigger) | `param.swing.S5.k` | see yaml |
| `LTF` | `B1m` | internal structure, 1m type 3, 15m-model condition | `param.swing.LTF.k` | see yaml |
| `MTF` | `B5m` | external structure, hourly-model condition | `param.swing.MTF.k` | see yaml |

- A swing is usable only after `confirmed_at` (IMPL).
- **External vs internal** (EP2-018, P1F-23): a swing is *external* at a given decision if it belongs to the
  MTF series; LTF swings between two consecutive MTF swings are *internal*.
- A robustness alternative (fractal pivots with strength n ∈ {2,3,5}) is kept for Phase 20 comparison only.

**Legs.** A leg is the segment between two consecutive confirmed swings; `leg.size = |p_end − p_start|`,
`leg.dir = sign(p_end − p_start)`, `leg.duration = t_end − t_start`.

---

## 2. Condition classifier (CANON thresholds, ASSUMPTION aggregation; OQ-02)

Input: tier `τ`, window `W` ending at `as_of`. Legs = completed legs with `t_start ≥ window_start`, where `window_start = as_of − W` (basis `CLOCK`) or the start of the last `W` scheduled-tradable minutes (basis `TRADABLE`: weekend and daily-break closures don't consume the window; vendor gaps do). Basis per model: `param.cond.window_basis` (both TRADABLE: CBR1H D19-3, CBR15 D20-5; ASSUMPTION). Clock, tradable and missing minutes are recorded.

```
corrections = [ legs[i+1].size / legs[i].size  for consecutive legs i ]      # "correction of the previous move"
c_med       = median(corrections)                                           # ASSUMPTION: median, not mean
n_legs      = len(legs)
```

| Output | Rule | Evidence |
|---|---|---|
| `condition = RANGE` | `c_med ≥ param.condition.range_min` (0.75) | E1H-007, E1H-008, E15-014 |
| `condition = TRENDING_RANGE` | `param.condition.trend_max (0.50) ≤ c_med < 0.75` | same |
| `condition = TREND` | `c_med < 0.50` | E1H-007, E1H-046 |
| `condition = UNDEFINED` | `n_legs < model.cond.min_legs` | E1H-010 ("none identifiable → no trade") |
| `direction` (TR only) | `UP` if the last two swing highs and lows **of the classifier tier** (MTF for CBR1H, LTF for CBR15) are both higher; `DOWN` if both lower; else `NONE` | E1H-007 (HH/HL), EP2-017 |
| `range_high`, `range_low` | max high / min low of `B1m` in window | E15-012 |
| `pos(price)` | `(price − range_low) / (range_high − range_low)` | E15-012, E15-015 |

`c_med` values are capped at 2.0 before the median (IMPL: one breakout leg must not dominate).

---

## 3. Candle state and overextension (OE)

For a candle `C` of timeframe `T ∈ {15m, 1h}` with open time `C.open_time` and open price `C.open`, evaluated on
`B1m` closed within the candle (IMPL).

```
up_ext(t)   = max(high of B1m in [C.open_time, t]) − C.open
down_ext(t) = C.open − min(low  of B1m in [C.open_time, t])
oe_dir      = UP if up_ext ≥ down_ext else DOWN              (evaluated at shift time)
oe_extreme  = the max high (UP) / min low (DOWN); oe_extreme_time = its bar time
oe_size     = |oe_extreme − C.open|
```

| Primitive | Definition | Label / evidence |
|---|---|---|
| `oe_duration` | `oe_extreme_time − C.open_time` | CANON: E1H-018 ("extending in one direction… 20-30 min"), E15-021 |
| `oe_no_pullback` | For every `B1m` bar between `C.open_time` and `oe_extreme_time`, the retracement from the running extreme never reached `param.oe.pullback_frac` (0.50) of the running extension (`running_ext ≥ param.oe.activation_atr × ATR(1m,14)` before the check applies) | CANON 50%: E1H-018. Activation floor is `ASSUMPTION` (IMPL guard against noise at the open) |
| `oe_opposite_wick` | `down_ext(oe_extreme_time)/oe_size` for UP (mirror for DOWN): size of the wick against the extension formed before the extreme | CANON as quality (E1H-020); **diagnostic only** in V1 |
| `oe_two_sided` | `min(up_ext, down_ext) ≥ param.oe.two_sided_frac × max(up_ext, down_ext)` | CANON invalid "wicks both ways" (E1H-026); fraction `ASSUMPTION` |
| `oe_size_atr` | `oe_size / ATR(T, 14)` | diagnostic proxy for "decisive/high volume" (OQ-08) |
| `oe_prev_candle_break` | UP: `oe_extreme > high` of the previous candle of timeframe 15m; DOWN: `< low` | CANON: E1H-017, E1H-034, E15-034 |

---

## 4. Shifts

### 4.1 Type 3 (Phase 1 definition)

On tier `τ` with confirmed swings (Section 1), evaluated on bars of that tier.

**Bearish type 3 at bar `b`** (sell), CANON EP1-008, EP1-009 (pairing corrected in v1.1 after parity finding F-0):
1. Let the last two confirmed swings be `SH` then `SL`, where `SL` is the swing low that formed **after** `SH`
   (higher high → higher low). The pattern is armed once `SL` is confirmed.
2. Price takes out `SH`: some bar `a` has `a.high > SH.price`.
3. Then price breaks `SL`: bar `b` (after `a`) has `b.low < SL.price`, with no new swing low confirmed after the sweep
   (the reversal is immediate) and `b.open_time − a.open_time ≤ param.t3.max_reversal_minutes.<τ>` (`ASSUMPTION`).
   New swing highs confirmed after the sweep (the sweep extreme itself) do not disarm the pattern.
4. `t3.trigger_price = SL.price − tick`, `t3.trigger_time` = the bar where the level traded (sequenced on the next
   finer tier where available).
5. `t3.sweep_extreme` = highest high between `a` and `b` (the stop anchor, EP1-012).
6. Quality (diagnostic in V1): `t3.close_beyond`, `t3.break_size_atr`.

Bullish type 3 mirrors. **CHoCH** (EP1-010) is recorded when step 3 happens without step 2; not an entry in V1.

**Step 1 read literally (F-3, D17-6).** The reference engines disarm an unswept pair as soon as a newer swing is confirmed (`track_type3(latest_pair_only=True)`). The legacy primitive `find_type3` kept older unswept pairs armed; it is preserved unchanged for existing callers.

### 4.2 HILO (Phase 2 definition, frame-confirmed)

On `B1m` (or `B5m` when `hvcs_state == LVCS`, EP2-005). CANON EP2-001…003. **Role (D19-2):** for CBR1H a 1m HILO is an observable equivalent of the lower-timeframe seconds shift (EP2-001 "an even lower time frame shift"); the entry trigger is the 5s type 3 (§4.1 on S5).

**Bullish HILO at candle `j`:**
- `j.high > (j−1).high` (the entry break), **and**
- either `(j−1).low < (j−2).low` (candle prior to the BOS broke its previous candle's low) **or**
  `j.low < (j−1).low` with the low break occurring **before** the high break inside `j` (sequenced on `B5s`) (same
  candle breaks both).
- `hilo.trigger_price = (j−1).high + tick`; `hilo.stop_ref = min((j−1).low, j.low up to trigger)` (EP2-007).
- `hilo.break_size = low break distance / ATR(1m,14)`, diagnostic (EP2-004 "bigger the better").

Bearish mirrors.

### 4.3 HVCS (high-volume candle sequence)

On `B1m`. CANON structure EP2-005 (frame-confirmed), duration E1H-034.

```
hvcs(dir, end_bar) = the longest run of consecutive B1m bars ending at end_bar such that for every bar i in run:
     dir=DOWN: i.high ≤ (i−1).high  and  i.close < i.open            ("respecting highs", bearish bodies)
     dir=UP  : i.low  ≥ (i−1).low   and  i.close > i.open
   allowing up to param.hvcs.max_violations bars that break the rule   (ASSUMPTION)
hvcs.duration = run length in minutes;  valid if ≥ param.hvcs.min_minutes (4)          CANON E1H-034
hvcs.body_atr = mean(|close−open|)/ATR(1m,14) over run;  LVCS if < param.hvcs.lvcs_body_atr   ASSUMPTION (OQ-08)
```

**End bar for CBR1H (D19-6, OQ-43).** The HVCS must run directly into the shift: `end_bar` = the closed `B1m` bar that set the extension extreme (final displacement bar). Closed bars after it are indecision bars; the sequence is continuous while each keeps the respected side (DOWN: `high ≤ end_bar.high`; UP: `low ≥ end_bar.low`). No maximum indecision count. The continuity reading is an ASSUMPTION (OQ-44, D20-4); bar counts between the HVCS and the shift are diagnostics, never filters.

---

## 5. Levels and AOI (Phase 1/2)

| Primitive | Definition | Label / evidence |
|---|---|---|
| `level` | For timeframe `T ∈ {30m, 1h}`: when candle `i−1` and candle `i` close in opposite directions, a level at `i.open` (≈ `(i−1).close`). | CANON: "A new level forms when there is a shift in candle close direction" (P1F-49, frame-checked); EP1-002 |
| `aoi_zone` | `[level − w, level + w]`, `w = param.aoi.zone_atr × ATR(1m,14)` | zone CANON (P1F-50, EP2-023 "general zone"); width `ASSUMPTION` (OQ-07) |
| `aoi_tap(C)` | the OE extreme of candle `C` lies inside an `aoi_zone` from a level formed before `C.open_time` and within `param.aoi.lookback_hours` | EP2-022, EP2-023 |

In baseline V1, AOI is a **variant flag** (`aoi_required`), not a default filter (OQ-07 two-baseline plan).

---

## 6. Entry relativity

`er(price, leg)` = retracement of `leg` at `price`: `|price − leg.p_end| / leg.size` measured from the leg's
extreme back toward its origin (E1H-015). Bucketed `25 / 50 / 75` at boundaries `[0.375, 0.625]` (IMPL rounding
to the nearest named bucket). Diagnostic in V1 except where a model rule uses a numeric band.

---

## 7. Canonical no-trade windows (gold)

| Rule | Definition | Evidence |
|---|---|---|
| `NT_SYDNEY` | No new entries from the daily market reopen until **00:00 UTC** (Tokyo open, Asia hour 1) | EP1-017 ("don't trade gold in Sydney session"); Asia hour 1 = 00:00 UTC (EP1-015, EP1-016, frame-checked; CAND-015) |
| `NT_ROLLOVER` | No new entries in `[17:00 − param.no_trade.rollover_pre_min, 17:00 + param.no_trade.rollover_post_min]` **America/New_York** (DST-aware); open positions are closed at `17:00 − param.no_trade.rollover_flat_before_min` | EP1-018 (no trading or holding through rollover); clock time 17:00 NY is IMPL; buffers `ASSUMPTION` |
| `NT_INCOMPLETE` | Any required candle `INCOMPLETE` (Section 0) | IMPL |

No other session filter in V1 (D3).

---

## 8. Execution semantics shared by both models (IMPL + CANON)

Price role (D16): fills and stop/target **touches** use EXECUTION bars (buy at ask, sell at bid; long exits observed on bid, short exits on ask). Stop **anchors** and target **levels** are STRUCTURE prices (`oe_extreme`, `C.open`).

| Item | Definition | Evidence |
|---|---|---|
| Entry order | Stop order at the trigger price (`t3.trigger_price` / `hilo.trigger_price`), placed when the trigger pattern becomes possible, filled on the first `B5s` bar trading through it at `max(trigger, bar.open)` + slippage (buys; mirror sells) | Break entries: E1H-035, E15-038 |
| Order expiry | Unfilled at window end (`timing.end`) → cancelled, logged `EXPIRED` | IMPL |
| Stop | Conservative: beyond the stop anchor by `param.stop.buffer_atr × ATR(1m,14)` + current spread. **Stop anchor (D17-2)** = most adverse STRUCTURE extreme of the active extension observed causally up to entry activation / fill | CANON E1H-036, E15-039, E15-040 ("breathing room"); buffer `ASSUMPTION` (OQ-11); anchor instant owner ruling (OQ-35) |
| Target | `oe_extreme − 0.5 × (oe_extreme − C.open)` (sell; mirror buy), where `C` is the model's candle | CANON E1H-037, E15-039 |
| Reward check | Skip if entry is already at or beyond the target, or `reward/risk < param.min_rr` (default 0 = only a positive-reward requirement) | IMPL (prevents negative-reward orders; `min_rr` is not a strategy rule) |
| Same-bar stop & target | Stop assumed first | IMPL (conservative) |
| One position | At most one open position per model; signals while in a trade are logged `SKIPPED_IN_TRADE` | IMPL |
| Management | None in V1 (all management rules are ablations) | Rule matrix |
| Forced exit | `NT_ROLLOVER` flat time | EP1-018 |
