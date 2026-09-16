# Expanded Parity-Set Inventory

**Doc:** CBR-SET-001 · **Version:** v2.0 · **Date:** 2026-09-16 · **Ruling:** D29 §21-24 · **Status:** INVENTORY, FOR OWNER REVIEW
Extraction performed before any data fetch (D29-21). No example has been scored against PC3 (D29-20). No outcomes or
P&L are recorded for any row. Labels per D29 §17: instrument · model · direction · positive/negative · source level ·
`data_available` · `machine_testable` · `narrative_only`.

---

## A. MACHINE PARITY SET

### A.1 Entry-level examples (date, time, direction, prices; data stored)

| Id | Instrument | Model | Dir | Pos/Neg | Level | Hour (UTC) | Entry | data_available | machine_testable |
|---|---|---|---|---|---|---|---|---|---|
| CX-LT1-1 | XAUUSD | CBR1H | BUY | positive | L1 video | 2025-10-21 01:00 | 01:39:15, 4340.13 | yes | yes |
| CX-TE1-1 | XAUUSD | CBR1H | BUY | positive | L1 video | 2025-10-24 04:00 | ~04:37-04:39, 4105.58 | yes | yes |
| CX-LT3-2 | XAUUSD | CBR1H | SELL | positive | L1 video | 2025-11-10 01:00 | 01:40:00, 4050.71 | yes | yes |
| CX-LT3-1 | XAUUSD | CBR1H | SELL | **negative** | L1 video | 2025-11-10 01:00 | rejected ~01:31-01:33 | yes | yes |

### A.2 Hour-level examples (extracted 2026-09-16; no entry price recorded in the source)

Source: Tom's "Journal Master 2025" table, visible in the Level-1 frame
`research/frames/V1H-defining_a_good_extension/slides/00-02-42.jpg`. Times are journal-local (UTC+11, the convention
confirmed by two rows that match existing examples). Outcome columns exist in that table and were **not** read.

| Id | Journal time (local) | Hour (UTC) | Dir | MTF model | Condition | CB hour | Shifts | AOI | data_available | machine_testable |
|---|---|---|---|---|---|---|---|---|---|---|
| JM-2025-10-29 | 2025-10-29 7:14 PM | 2025-10-29 **08:00** | BUY | TRR PT (pro trending range) | Trending | 37 | LLTF (seconds) | 4h | **yes** | hour-level |
| JM-2025-10-17 | 2025-10-17 12:53 PM | 2025-10-17 **01:00** | BUY | IFS (inverse fractal shift) | Volume | 52 | LLTF (seconds) + LTF (1m) | 1hr, 30m | **yes** | hour-level |
| JM-2025-10-16 | 2025-10-16 11:41 AM | 2025-10-16 **00:00** | SELL | TRR CT (trending range counter) | Trending | 37 | LLTF (seconds) | — | **yes** | hour-level |

**Corroboration:** the same table's rows "textbook · October 24, 2025 3:38 PM · XAU/USD · TRR CT · Ranging" and
"new · October 21, 2025 12:39 PM · XAU/USD · TRR CT · Ranging" match CX-TE1-1 and CX-LT1-1 exactly, which is what
establishes the timezone convention used above.

**Scoring note (see CBR-PROT-013C §4):** these are hour-level cases. Expected: an eligible PC3 candidate in the stated
hour, in the stated direction, triggered by a seconds shift. No price match is expected, because none is recorded.

What they add to the set: two new sessions (08:00 UTC London morning; 00:00-01:00 UTC Asia on different days), a new
direction mix, and three MTF model families the current set lacks (TRR PT, IFS, TRR CT trending).

## B. NARRATIVE / GEOMETRY SET (never contributes to machine-pass counts)

| Id | Instrument | Model | Dir | Pos/Neg | Level | Source | Use |
|---|---|---|---|---|---|---|---|
| CX-LT2-2 | USDJPY | CBR1H | SELL | positive | L1 video | V1H-live_trade_2_uj_loss, 2025-10-23 | "sell at the break of that low": sweep → break geometry |
| CX-LT2-1 | USDJPY | CBR1H | SELL | **negative** | L1 video | same | rejected at ~22 minutes on **timing**, not geometry |
| T3-VP1-A | XAUUSD | type-3 lesson | — | positive | L1 frame | VP1-1_4_shifts_type_3_choch 00:03:04 | ranging type 3: take the range high, then the low, then shift |
| T3-VP1-B | XAUUSD | type-3 lesson | BUY | positive | L1 frame | same, 00:03:38 | swept low marked and extended as a level |
| T3-VP2-HILO | XAUUSD | HILO / seconds shift | both | positive + invalid | L1 frames | VP2-1m_hilo_entries 00:02:44-00:05:25 | valid vs invalid HILO; levels re-anchor per candle (the T3-1 evidence) |
| OE-GOOD / OE-BAD | XAUUSD | extension | — | positive **and** negative | L1 video | V1H-defining_a_good_extension 00:03:19, 00:05:03, 00:05:16 | "didn't correct 50% at all" vs "on average correcting 50%": direct OE-2 checks |
| V15-SEM-2026-05 | XAUUSD | **CBR15** | — | instructional | L1 video + frame | V15-seconds_entry_model, chart ~2026-05-01 | **not extractable as a dated trade**: the walkthrough is illustrative ("let's say if we have…"), with no stated entry time or price |

## C. Extraction outcomes against the D29 §24 target

| Required | Status |
|---|---|
| CX-LT1-1, CX-TE1-1, CX-LT3-2 positives | present (entry-level) |
| CX-LT3-1 negative | present |
| 2025-10-16, 2025-10-17, 2025-10-29 XAUUSD | **extracted** (hour-level); data acquired and validated |
| 2026-05 CBR15 example | **not extractable**: no stated entry; kept as narrative only |
| CX-LT2-2 positive, CX-LT2-1 negative narrative | present |
| Drawn type-3, HILO, extension good/bad | present |

## D. Data acquisition (D29-22)

| Day | Purpose |
|---|---|
| 2025-10-15 | warm-up for JM-2025-10-16 (condition window, ATR(1h), prior candles) |
| 2025-10-16 | JM-2025-10-16 example day; warm-up for JM-2025-10-17 |
| 2025-10-17 | JM-2025-10-17 example day |
| 2025-10-28 | warm-up for JM-2025-10-29 |
| 2025-10-29 | JM-2025-10-29 example day |

**Acquisition complete (2026-09-16):** all five days, 24/24 hours each, 0 unresolved failures after 38 retries; the only empty hours are the daily break (21h UTC) and Friday's weekend close. Integrity: 0 duplicate timestamps, 0 bad spreads, monotonic, 0 missing scheduled-open minutes, deterministic rebuild and manifest hashes verified on every day.

Five XAUUSD tick days, chosen as the minimum that still covers the 8-hour tradable condition window, ATR(1h,14)
warm-up, the previous 15m candle and the 5-second trigger. No unrelated history. These dates sit inside the holdout
window and are parity fixtures only, logged in `research/holdout-access-log.md`.

## E. Honest limits

- The machine set remains **XAUUSD-only**; USDJPY stays narrative by instrument scope (D29-21).
- The three new cases are **hour-level**, so they test signal existence, direction and timing — not entry prices.
- Their source is Tom's own journal table (his record) captured in a Level-1 frame, which is weaker than a video
  walkthrough narrating the trade. They should be labelled as such in any report.
- **No CBR15 machine example exists**, so CBR15-PC3 stays unscored.

## F. Frozen manifest

`research/examples/parity_set_manifest.json` · manifest hash `a3ee0bd6ba225ce6b89d8bc61fbefd227ce8097a3f6bfac2f9414e19cd81ea9c`
· 4 ENTRY_LEVEL, 3 HOUR_LEVEL, 7 NARRATIVE_ONLY · guarded by `tests/engine/test_parity_set_manifest.py`, which fails if
any source or market-data file changes after the freeze.
