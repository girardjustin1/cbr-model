# Proposed TradingView Architecture

Status: **proposal**. The indicator is built only after rules are validated (Phase 26). This document fixes the
structure early so baseline strategies and the future indicator share logic and can't drift.

## 1. Artifacts

| File | Type | Purpose | Phase |
|---|---|---|---|
| `strategies/pine/cbr1h_baseline_v1.pine` | `strategy()` | canonical hourly rules, backtest | 12 |
| `strategies/pine/cbr15_baseline_v1.pine` | `strategy()` | canonical 15m rules, backtest | 11 |
| `strategies/pine/lib/cbr_core.pine` | `library()` | shared rule functions (swings, shifts, candle behavior, condition, OE) | 11 |
| `indicators/cbr_signals.pine` | `indicator()` | live signals, panel, alerts | 26-27 |

Rule functions live in one Pine **library** so strategy and indicator call identical code. The library version
is pinned in each script; a library change = new model version.

## 2. Non-repainting rules (enforced by review checklist)

- `request.security(..., lookahead = barmerge.lookahead_off)` only, and read higher-timeframe values with `[1]`
  (last *closed* HTF candle) unless the rule is explicitly about the *current forming* candle (candle behavior
  is. See below).
- Candle-behavior rules need the **forming** hour/15m candle (its open, extension so far, minutes elapsed). These
  are computed from lower-timeframe bars that have already closed (e.g. `request.security_lower_tf` or native 1m
  chart with time math). Never from the HTF bar's current high/low on a realtime tick.
- Swing points are confirmed only after their right-side bars close. Plots and labels are placed at confirmation
  time, not back-dated. (A label may point *at* the pivot bar but is created on the confirming bar.)
- Signals fire on `barstate.isconfirmed` of the chart's base timeframe.
- `calc_on_every_tick = false`, `process_orders_on_close = false` in strategies. Stop-entry orders for break
  entries.
- Explicit timezone: all session math with IANA names (`"Asia/Tokyo"`, `"Europe/London"`,
  `"America/New_York"`), never the chart's timezone.

## 3. Base timeframe and data

- **Chart timeframe: 1 minute** on XAUUSD (`OANDA:XAUUSD` or your broker feed, matched to parity data).
- HTF context (15m, 1h, 4h, D) derived inside the script from the 1m series or via `request.security` with the
  rules above.
- DXY: `request.security("TVC:DXY", "1", …)` for same-candle inverse-extension state; missing DXY → state
  `UNAVAILABLE` (never "confirmed").
- Seconds (5s) entries need a TradingView plan with seconds charts and are limited in history. V1 Pine uses 1m
  shifts (`SIMPLIFIED-ENTRY`). A seconds variant is a later, separately-versioned script.

## 4. Indicator design (Phase 26, sketch)

**On chart:** OE start/end markers on the forming candle · range high/low/mid of the condition window ·
entry-relativity levels (50/75%) · signal label at confirmation (direction, model, minute-in-hour) ·
entry / stop / TP lines · invalidation marker with reason code.

**Panel (table):**

```
CBR 15M        LONG      ← last signal, or WATCHING / NONE
1H             OE ↓ 24m  ← hourly candle-behavior state
CONDITION      RANGE 82% ← correction %, swings 4
DXY            INVERSE ✓ ← or SAME-DIR ✗ / UNAVAILABLE
SETUP          VALID     ← or INVALID: <rule id>
QUALITY        —         ← only after validated weights exist (Phase 25)
ENTRY / SL / TP  xxxx / xxxx / xxxx
SIGNAL TIME    2026-09-14 07:37 UTC
MODEL          CBR15_BASELINE_V1
```

`QUALITY` stays blank until score weights are validated out-of-sample. No invented weights.

## 5. Alerts (Phase 27)

`alertcondition` / `alert()` events: `CBR15_LONG`, `CBR15_SHORT`, `CBR1H_LONG`, `CBR1H_SHORT`, `CBR_15M_1H_ALIGN`,
`DXY_INVERSE_CONFIRMED`. JSON payload:

```json
{"symbol":"{{ticker}}","ts_utc":"{{timenow}}","model":"CBR15_BASELINE_V1","direction":"LONG",
 "entry":0,"stop":0,"target":0,"condition":"RANGE","dxy":"INVERSE","rules_passed":["CBR15-OE-001","…"]}
```

Alerts feed the signal ledger (Phase 28): every alert becomes a ledger row, whether or not a trade is taken.

## 6. Parity chain

Python reference (5s/1m) ⇄ Pine strategy in PineTS ⇄ Pine strategy in TradingView Strategy Tester.
Each arrow has a parity report: signal time, direction, entry/stop/target within one tick, with every mismatch
classified as code bug, data difference, simplified entry, or source ambiguity.
