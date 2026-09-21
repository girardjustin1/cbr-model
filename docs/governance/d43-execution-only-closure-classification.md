# D43 — execution-only closure classification, separated from the strategy calendar

**Doc:** CBR-DEC-043 · **Date:** 2026-09-20 · **Status:** owner decision recorded
Phase 15A checkpoint 1 accepted. The 2022 acquisition continues. No performance was inspected, no partial-year
signals were run, and validation and holdout were not touched.

---

## 1. The strategy calendar does not change

US holiday closures are **not** added to `cbr.data.sessions.expected_closed` or to any calendar frozen PC4 reads.
PC4's **TRADABLE** condition-window basis is unchanged through the untouched 2022 pilot, because changing that
calendar would be a strategy behaviour change.

## 2. A separate execution / data closure registry

`cbr.data.market_closures` introduces `VERIFIED_MARKET_DATA_CLOSURE`. Its only purposes are historical-data
completeness, execution-data interpretation, and keeping a real market closure from being mistaken for corrupt or
missing data.

It is **never imported** by PC4 condition logic, PC4 tradable-time calculation, signal eligibility, extension logic
or any CBR rule. `tests/test_closure_registry_separation.py` walks the AST of every module under `cbr/engine`,
`cbr/structure` and `cbr/dxy` and fails if any of them imports it; `sessions.py` is separately asserted to contain
no holiday table and no reference to the registry.

## 3. Classification is evidence-based

A date being a US holiday is **not sufficient**. A period is a verified closure only when stored evidence
establishes that the feed was genuinely unavailable, through all four rules:

| Rule | Meaning |
|---|---|
| `SOURCE_404_NO_FILE` | the feed holds no file for every hour of the period |
| `CONTIGUOUS_EMPTY_INTERVAL` | the empty hours form one unbroken run |
| `CONNECTED_TO_CLOSURE_BOUNDARY` | the run reaches a known break or weekend boundary, or covers the whole session |
| `NO_ISOLATED_HOLE` | at least `MIN_CLOSURE_HOURS` (2); a single hour is never a closure, whatever the date |

An isolated missing hour on a holiday, with trading either side, stays a `DATA_GAP`. The holiday name is recorded
as `holiday_context` — context, never evidence.

## 4. Both classifications are preserved

Each record carries two fields, and neither replaces the other:

```
source_quality_classification = DATA_LIMITATION                 # what Phase 9 / Phase 15A saw
execution_market_state        = VERIFIED_MARKET_DATA_CLOSURE    # what the evidence established
```

The gap register now carries `execution_market_state` per hour alongside its original classification, so the record
stays auditable without pretending the original calendar knew about the closure.

## 5. Execution behaviour during a verified closure

A verified closure is **not** a `DATA_GAP`. During a proven closure there is no executable quote stream, so a fill
cannot have occurred inside the interval and there is nothing to call unprovable. `classify_intervals` labels those
minutes `VERIFIED_MARKET_DATA_CLOSURE` and does **not** hand them to the simulator as `px.Gap`.

No quote is fabricated and no price is interpolated. The clock simply holds no executable market event there.

## 6. True data gaps are unchanged

An interval where the market should have been active but the data is absent remains a `DATA_GAP` and keeps
`ENTRY_FILL_UNPROVABLE_DATA_GAP` and `TRADE_OUTCOME_UNPROVABLE_DATA_GAP` exactly as D38 and D39 defined them. The
missing-data protections are not weakened: with no registry, or with an empty one, behaviour is identical to before
D43.

## 7. The distinction is tested

Twenty-two tests across `tests/execution/test_verified_closures.py` and `tests/test_closure_registry_separation.py`:
a verified full closure creates no unprovable outcome (A); an isolated missing active-market hour still creates a
`DATA_GAP` (B); a holiday name alone creates nothing (C); the strategy calendar and `tradable_window_start` are
unchanged and still treat closure minutes as tradable (D); PC4's result hash is identical with a populated and an
empty registry (E); classification is deterministic and a live minute can never be overruled by the registry (F).

## 8. Later holidays

Labor Day, Christmas observed and any other 2022 holiday are classified the same way when acquisition reaches them
— from evidence, never pre-classified from the calendar. Every verified closure is recorded with date, start UTC,
end UTC, evidence, source files and 404 evidence, and `classification_version`.

## 9-11. Construction continues; nothing is executed on partial history

The historical runner, execution orchestrator, metrics/package writer and rerun harness are accepted and are **not**
run on partial 2022 history. Work continues on tests and documentation only. The Pine track may proceed to its
first TradingView compile; Strategy Tester output may never change PC4, the Phase 15A settings, the execution
assumptions or the 2022 protocol.

## 12. Next stop

Continue until every 2022 open hour is acquired or classified, all 260 days are decoded, the closure registry is
complete, the gap register holds no unresolved active-market hole, the completeness gate reads COMPLETE, the full
suite passes and every frozen hash verifies. Then **STOP BEFORE PERFORMANCE** and return the pre-run readiness
report, extended with the verified execution-only closure count, the true `DATA_GAP` count, proof the strategy
calendar did not change, the Pine compile status and any new translation differences.
