# CX-LT3-2 Event Reconstruction: Where PC2 and Tom First Disagree

**Doc:** CBR-REC-LT32 · **Date:** 2026-09-15 · **Ruling:** D26 §9 · **Status:** FOR OWNER REVIEW
Causal STRUCTURE data (Dukascopy tick-mid, D16) and the frozen PC2 primitives. Tom's entry time is an evaluation point,
never a selector. No parameters were varied, no outcomes or P&L, no PC2 change.

**Example.** XAUUSD 2025-11-10, hour 01:00-02:00 UTC ("second hour of Asia"), SELL. Tom: entry 4050.71 at ~01:40:00,
stop 4053.30 "just above the high", previous high taken "36 minutes in", "might potentially enter around 38, 39 minutes
into the hour" (V1H-live_trade_3_gold_win 00:12:24, 00:15:11).

---

## 1. The hour as the engine measures it

| Item | Value |
|---|---|
| Hour open | 4020.43 |
| Extension direction | UP (matches Tom) |
| Extension extreme | **4053.43 at 01:37:35** (5s) / 01:37 bar (1m) |
| Duration to the extreme, anchor A (hour open) | 37 min |
| Duration, anchor B (last reset, origin 01:09) | 28 min |
| No-pullback (anchor A) | **false** — first failing retrace 01:01, $4.01 against a $4.27 running extension |
| No-pullback (anchor B) | true |
| Tom's stop 4053.30 vs engine extension extreme 4053.43 | −0.13 (well inside the $0.20 feed band) |

The engine's extension extreme is Tom's stop level to within $0.13, at the minute he describes. The **extension is
identified correctly**.

## 2. 15-minute candle behaviour

| 15m candle | Open | High | Low | Close |
|---|---|---|---|---|
| 01:00 | 4020.43 | 4029.43 | 4019.17 | 4027.22 |
| 01:15 (Q−1) | 4027.24 | **4052.01** | 4027.20 | 4047.84 |
| 01:30 (Q) | 4047.86 | **4053.43** | 4045.64 | 4050.93 |

Q takes Q−1's high at **01:37:35** — Tom's "taken out previous high, 36 minutes in". At Tom's entry time the
previous-candle rule `M1H-6A-2` is **satisfied** (take present, Q−1 did not close in the trade direction, so the
exception is not needed). The rule only fails on the engine's *later* evaluated candidate at 01:50, whose Q is the
01:45 candle. **No disagreement here at Tom's time.**

## 3. The 5-second structure around the entry

S5 swings (ATR zig-zag, k = 3, PC2):

| Kind | Price | Time | Confirmed |
|---|---|---|---|
| L | 4045.78 | 01:34:05 | 01:34:25 |
| **H** | **4053.43** | **01:37:35** | 01:37:50 |
| **L** | **4050.97** | **01:37:50** | 01:38:40 |
| H | 4052.98 | 01:38:35 | 01:39:40 |
| L | 4049.82 | 01:40:15 | 01:40:40 |

**Tom's sequence.** Price takes the previous 15m high (4053.43, a liquidity sweep), then breaks the low that formed
after it (4050.97) — "take out this low" — and he is short at 4050.71 around 01:40:00, stop just above 4053.30.

**The engine's sequence.** `track_type3` (5s tier, `latest_pair_only`) arms a pair only when the **second** swing of the
pair confirms, and then waits for a **new sweep of the first swing**. Every 5s type-3 arm whose sweep falls in
01:25-01:50:

| Direction | Sweep | Swept price (swing) | Trigger | Ended |
|---|---|---|---|---|
| SELL | 01:34:40 | 4049.61 (01:32:35) | 4045.76 | TIMEOUT 01:37:45 |
| **BUY** | **01:39:40** | **4050.97 (01:37:50)** | 4052.99 | NEW_SWING 01:41:30 |
| BUY | 01:41:30 | 4049.82 (01:40:15) | 4051.91 | BREAK 01:43:30 |
| SELL | 01:43:30 | 4051.90 (01:40:45) | 4048.53 | NEW_SWING 01:44:25 |

At 01:39:40 — the moment Tom is selling the break of 4050.97 — the engine classifies the **same price event** as the
**sweep of a BUY type 3** (take the low, then break the high above). No SELL type 3 is ever armed on the 4053.43 high,
because that high is the hour's extreme: nothing trades above it afterwards, so it is never "swept" in the engine's
sense.

## 4. First semantic disagreement

> **The engine requires a type-3 *sweep* to be a new excursion beyond an already-confirmed swing, after the opposite
> swing has also confirmed. Tom treats the move that *creates* the extension extreme — the take of the previous 15m
> high — as the sweep, and the break of the low formed after it as the shift.**

Formally, at 01:37:35-01:39:40:
- Tom: sweep = the new high 4053.43 (which took the previous 15m high, `M1H-6A-2` satisfied at that moment);
  shift = the break of 4050.97 at ~01:39:40-01:40:00; stop above 4053.43; entry 4050.71.
- PC2: 4053.43 is swing **X** of a pair, not a sweep. For a SELL arm, PC2 waits for price to exceed 4053.43 *again*
  after the following low confirms. That never happens, so no SELL candidate exists at Tom's entry. The same tick data
  instead arms a BUY.

Everything downstream follows from this: the earliest SELL candidate with a completed shift in the hour is at
**01:50:40** ($0.25 above Tom's entry, ten minutes late), which is what the frozen selection evaluated, and which then
fails `M1H-6A-2` on a different 15m candle.

**Rule where the sequences diverge:** the 5s type-3 arming semantics in `CBR_PRIMITIVES_V1 §4.1` as implemented by
`structure/shifts.py::track_type3` — specifically what counts as the **sweep** leg. This is upstream of
`M1H-6A-1/2/3`, of candidate selection, and of the D8 anchor.

## 5. Second, independent blocker at the hour level

`M1H-COND-03` fails for **every** candidate in this hour: condition `TRENDING_RANGE` with `cond_direction = NONE`.

| Item | Value |
|---|---|
| Condition window (8 h **tradable**, OQ-40) | starts **2025-11-07 16:00** — Friday |
| Last MTF (5m) swings in the window | H 4007.38 (07 14:20), L 3984.13, H 4027.53, L 3992.47, H 4009.29, L 3994.55 (07 20:25) |
| Direction test | last two highs 4027.53 → 4009.29 (lower high); last two lows 3992.47 → 3994.55 (higher low) → **NONE** |
| Tom | "So very bullish, um, a little bit trendy" (00:01:07) |

Because the hour is the second hour after the weekend reopen, eight *tradable* hours reach back into **Friday**. The
engine's condition therefore describes Friday's structure, while Tom is describing the Sunday-night/Monday rally in
front of him. Two questions follow, both already registered: the window basis (OQ-40, ASSUMPTION) and the swing
definition that yields `direction = NONE` (OQ-01/OQ-02).

## 6. Summary for the owner

| Layer | Agreement at Tom's time |
|---|---|
| Model family, direction, extension direction | ✓ |
| Extension extreme (price and minute) | ✓ ($0.13 from Tom's stop level) |
| Previous 15m candle take | ✓ (01:37:35) |
| **5s type-3 arming (the sweep)** | ✗ **first divergence** |
| Hour condition / TR direction | ✗ second, independent blocker (weekend window) |
| Candidate selection, `M1H-6A-1`, `M1H-COND-04` | not reached — they act on candidates that only exist after the divergence |

CX-LT3-2 is **not** explained by D8: under `LAST_RESET` the same candidate still never completes a shift
(`S5_T3_NEW_SWING`). It is a structural-definition disagreement about what a type-3 sweep is, plus a condition-window
question.

No change is proposed here; candidate interpretations are listed in `docs/strategy/pc3-proposed-change-set.md` under
T3-1 and W-1.
