# Phase 14B — TradingView research track

**Status:** compile-ready draft, **not yet compiled in TradingView** · **Ruling:** D42 §17-21

`cbr1h-pc4-research-strategy.pine` — Pine Script v6 strategy **CBR1H PC4 Research Strategy**.

---

## What this is, and what it is not

| | |
|---|---|
| **Authoritative** | frozen PC4 Python + the Phase 14A simulator + Phase 14A.1 tick replay |
| **This file** | **NON-AUTHORITATIVE / EXPLORATORY** — visual human review, Strategy Tester exploration, Python ↔ Pine signal-parity work, and groundwork for an eventual indicator and alerts |

Strategy Tester output from this script is **not a performance result** and may not alter PC4, the 2022 protocol,
the execution semantics or the Python pilot result. Parameters are copied from the frozen config and are **not
optimized** from tester output (D42 §19).

## First objective

**COMPILE + VISUALIZE.** Not "maximize Strategy Tester performance."

1. Open a XAUUSD chart. Use **5 seconds** if the plan allows it, otherwise **1 minute** (see TD-1).
2. Paste the script into the Pine editor and add it to the chart.
3. Fix compile errors; do not change a rule to make one go away — record what was changed and why.
4. Check the status table in the top right. It names the trigger tier actually in use and the **first failing
   rule**, so a chart with no signals still explains itself.
5. Step through a few hours visually: condition shading, the extension extreme, the extension-activation triangle,
   the previous-15m diamond, HVCS bar colouring, the ARM label, and the stop/target lines.

## Translation differences, declared before any comparison

These are in the file header as TD-1…TD-7 and are expected. None is a strategy change.

| Id | Difference | Consequence |
|---|---|---|
| **TD-1** | TradingView has no Dukascopy XAUUSD tick feed, and seconds bars need a paid plan. PC4's trigger is a **5-second type 3**; on a 5s chart the script approximates it on chart bars, and on anything coarser it degrades to a 1-minute type 3 | the trigger fires at different instants, so entry times and counts will differ. The status table always says which tier is in use |
| **TD-2** | STRUCTURE prices here are the broker's chart OHLC, not Dukascopy tick-mid | extremes differ slightly; any rule comparing an extreme to a level can differ at the margin (D16) |
| **TD-3** | The condition window basis is CLOCK here; PC4 uses TRADABLE, where scheduled closures do not consume the window | the classifier can see a different leg set across a weekend or daily break |
| **TD-4** | EXECUTION in PC4 is real bid/ask with the historical spread; Strategy Tester fills on chart prices with no spread and no gap semantics | fills, R values and any tester statistic are not comparable to the Python result |
| **TD-5** | The HVCS scan is bounded to `hvcsScan` bars (default 90); PC4's run is unbounded | a very long HVCS is truncated here |
| **TD-6** | Prior-setup count (`M1H-COND-04`) is not implemented — it needs recursive setup evaluation | the rule is shown as `N/A`, never as passing. This is the largest **known** functional gap |
| **TD-7** | TradingView's feed applies its own session and holiday handling, so a closure arrives as absent bars rather than as data to classify. The Python side distinguishes a `VERIFIED_MARKET_DATA_CLOSURE` from a true `DATA_GAP` (D43); this script cannot | around holidays the two implementations see different bar sets, and Pine has no unprovable-outcome concept at all |

## Python ↔ Pine hierarchy (D42 §18, §20)

Frozen PC4 Python is authoritative. If the two disagree, **assume a Pine translation difference first** and
investigate, in this order:

1. timeframe availability (is the 5s trigger actually available on this plan and symbol?);
2. lower-timeframe sequencing (`request.security` returns a higher-timeframe value only after that bar closes);
3. `request.security` semantics (repainting, `lookahead`, the `[1]` offsets used for Q−1);
4. chart feed differences (broker, session template, holiday handling);
5. broker-emulator behaviour in Strategy Tester (intrabar fill assumptions);
6. an implementation mistake in this file.

**Do not change PC4** unless the discrepancy independently demonstrates a real strategy-definition defect.

## Pre-compile static fix log

Changes made to the Pine **before** its first compile. They are Pine-language defects in the translation;
none changes a CBR rule, and PC4 was not touched.

| # | Fix | Why it mattered |
|---|---|---|
| P-1 | The condition-classifier leg loop is now guarded by `if n >= 2` instead of `for i = 0 to (n >= 2 ? n - 2 : -1)` | Pine's `for a to b` counts **downward** when `b < a`, so an empty leg window would have run the body twice and indexed an empty array — a runtime error on every early bar |
| P-2 | The HVCS scan computes `last` first and runs only `if last >= endOffset` | same downward-iteration hazard once `endOffset` exceeded the 4999-bar cap |
| P-3 | `timestamp(...)` now passes an explicit seconds argument | removes reliance on an optional-argument default for the rollover instant |
| P-4 | `max_bars_back = 5000` added to the `strategy()` header | the bounded HVCS scan reads deep history inside a `request.security` call |

## Known risks for the first compile

Static review only — this file has never been through the TradingView compiler. Most likely to need attention:

* the `Zig` user-defined type and the mutation of its fields inside `zigStep`;
* `f_hvcs`'s `for` loop with `break`, executed inside a `request.security` call, and its history depth
  (`max_bars_back = 5000` is set for this reason);
* dynamic-length `ta.highest` / `ta.lowest` in `f_continuity`;
* the multi-branch `if` **expression** assigned to `locOk`;
* `strategy.entry(..., stop = ...)` order behaviour versus PC4's stop-order semantics;
* execution limits on a 5-second chart over a long history.

## What is deliberately absent

No `strategy.optimize`-style parameter search, no input sweeping, no "best settings" note. Backtesting.py remains
optional and is not a blocker (D42 §21); if this track gives the owner the visual review environment they want,
Backtesting.py may be skipped entirely. The authoritative Python simulator does not change either way.
