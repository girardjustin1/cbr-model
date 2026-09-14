# Signal parity: working notes (pre-engine)

Exploratory checks of the structure primitives on real data against course examples, run before the full
state machines exist. Formal results go to `reports/signal-parity.md` in Phase 13. Findings here propose spec
amendments; **nothing below changes a rule until the owner approves it**.

Data: Dukascopy XAUUSD ticks → 1m/5s mid bars (`data/normalized/xauusd/`), parameters from `config/strategy.yaml`.

---

## CX-LT1-1 · 2025-10-21 · XAUUSD BUY (V1H-live_trade_1_gold_win)

**Tom's trade:** entry 4340.13, stop 4332.96, target 4351.59, "39 minutes into the hour", range condition,
hour pushed bearish into the range low, 5-second shift "low then take out a high", won ~1.3R.

| Check | Tom | Primitives on Dukascopy data | Result |
|---|---|---|---|
| Chart timezone | chart 12:39 local (unconfirmed) | 01:39 UTC bar O 4335.44 H 4341.23 C 4340.58 | **UTC+11 confirmed** for this video |
| Feed agreement | stop 4332.96 | hour low 4332.955 at 01:38 | matches to 0.005 |
| Condition | "range bound over the past 5-12 plus hours" | RANGE, median correction 0.813, 3 legs (MTF, 8 h) | ✅ |
| Location | "into the low of the range" | extension extreme below the 8 h range low (pos −0.10) | ✅ |
| OE direction / previous-15m break / two-sided | bearish push, broke the low | DOWN, prev 15m low broken, not two-sided | ✅ |
| OE no-pullback | "immediately push bearish", clean | **fails**: 85% retrace around minute 10 (running extension 10.36, bounce 8.78) | ❌ see F-1 |
| Entry trigger | 4340.13 on 5s shift | 5s type 3 BUY: swept 4335.21 → extreme 4332.95 → broke 4340.18, **trigger 4340.19** (01:39:35) | ✅ after fix F-0 |
| 1m HILO | n/a | BUY HILO at 01:39, trigger 4340.19 | ✅ (agrees) |
| Stop anchor | 4332.96 | type 3 sweep extreme 4332.95 | ✅ |
| Target | 4351.59 | 50% of extension from hour open 4368.73: 4350.84 | ≈ (0.75 apart) |
| First signal in window | trade at ~:39 | **earlier 5s BUY type 3 at 01:29:05, trigger 4352.61** | ❌ see F-2 |

### F-0 · Type 3 swing pairing was inverted (bug, fixed)

Primitives spec §4.1 said the swing to break is the one **before** the swept swing. Phase 1 (EP1-008) and this
trade show it is the swing **after** it: higher high → higher low → take out the high → break that higher low
(sell); mirror for buy. The synthetic unit test encoded the same misreading, so it passed. Fixed in
`src/cbr/structure/shifts.py`, spec §4.1 and tests (a new test reproduces this trade's swing shape).

### F-1 · Overextension measured strictly from the hour open (proposed amendment)

The hour opened at 4368.73, chopped and retraced 85% by minute 10, then pushed with no 50% pullback for ~26 minutes
into 4332.95. Tom calls it a clean overextension.
- **Level 1:** "if the hourly candle opens and kind of … for a bit and then pushes. Sometimes you can have the reversal
  happen a little bit later on" (E1H-025).
- **Level 2:** "a big pullback restarts the count" (LR-41).
- **Proposed:** the no-pullback test and the minimum-duration test run from the **last reset point** (the start of
  the push after the most recent ≥ 50% pullback). Direction, stop anchor and the 50%-of-extension target still use
  the hour open. Needs owner decision; would become `oe_origin: LAST_RESET` in a new primitives version.

### F-2 · An earlier shift in the window would fire first (proposed amendment)

At 01:28:50-01:29:05 a valid 5s type 3 BUY exists (trigger 4352.61). V1 takes the first valid signal in :22-:52,
so it would enter ~12 points higher and be stopped out as price fell to 4332.95. Tom waited for the **third 15m
candle (:30) to continue against the trade and take the previous 15m low, then reverse near :37-:39**. That is the
15m-alignment rule E1H-021 ("my best setups"), classified OPTIONAL and recorded only as a diagnostic in V1.
- **Proposed options:** (a) make E1H-021 a required filter for hourly entries after :30; (b) require the entry's type
  3 sweep to set the hour's extension extreme (the shift must reverse the *final* push, not an intermediate one);
  (c) keep V1 as is and test (a)/(b) as ablations. Needs owner decision.
