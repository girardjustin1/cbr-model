# Expanded Parity-Set Inventory

**Doc:** CBR-SET-001 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §17-18 (from D27) · **Status:** INVENTORY, FOR OWNER REVIEW
Built under the authorization to assemble an expanded evidence-based parity set. **No data was fetched and no example
was scored.** Other instruments are **not** added to backtest research scope; USDJPY examples appear for
strategy-definition parity only. No outcomes or P&L are recorded for any row.

Labels per D28 §17: instrument · model · direction · positive/negative · source level · `data_available` ·
`machine_testable` · `narrative_only`.

---

## 1. MACHINE PARITY SET (data stored, testable today)

| Id | Instrument | Model | Dir | Pos/Neg | Level | Date · hour (UTC) | data_available | machine_testable |
|---|---|---|---|---|---|---|---|---|
| CX-LT1-1 | XAUUSD | CBR1H | BUY | positive | L1 | 2025-10-21 01:00 | yes | yes |
| CX-TE1-1 | XAUUSD | CBR1H | BUY | positive | L1 | 2025-10-24 04:00 | yes | yes |
| CX-LT3-2 | XAUUSD | CBR1H | SELL | positive | L1 | 2025-11-10 01:00 | yes | yes |
| CX-LT3-1 | XAUUSD | CBR1H | SELL | **negative** (rejected early shift) | L1 | 2025-11-10 01:28-01:36 | yes | yes |

**Current machine set: 3 positive, 1 negative, one instrument, one model, one session family (Asia), two directions.**

## 2. NARRATIVE / GEOMETRY CONSISTENCY SET (no market data; qualitative geometry only)

| Id | Instrument | Model | Dir | Pos/Neg | Level | Source | narrative_only | Use |
|---|---|---|---|---|---|---|---|---|
| CX-LT2-2 | USDJPY | CBR1H | SELL | positive | L1 | V1H-live_trade_2_uj_loss (2025-10-23 12:00 local) | yes | "sell at the break of that low" — sweep/break geometry |
| CX-LT2-1 | USDJPY | CBR1H | SELL | **negative** (not taken, ~22 min in) | L1 | same video | yes | rejection on **timing**, not geometry |
| T3-VP1-A | XAUUSD | type-3 lesson | BUY | positive (instructional) | L1 | VP1-1_4_shifts_type_3_choch · 00:03:04, frame `slides/00-03-04.jpg` (chart ~2025-01-20/21) | yes | the drawn "ranging type 3": take the range high, then the range low, then shift |
| T3-VP1-B | XAUUSD | type-3 lesson | BUY | positive (instructional) | L1 | same · 00:03:38, frame `slides/00-03-38.jpg` | yes | swept low marked with a level extending right |
| T3-VP2-HILO | XAUUSD | HILO / seconds shift | both | positive + invalid pair | L1 | VP2-1m_hilo_entries · 00:02:44-00:05:25, frames | yes | valid vs invalid HILO (EP2-002 prior-candle rule); levels re-anchor per candle |
| OE-GOOD/BAD | XAUUSD | CBR1H extension | n/a | positive **and** negative extensions | L1 | V1H-defining_a_good_extension · 00:03:19, 00:05:03, 00:05:16 | yes | "didn't correct 50% at all" vs "on average correcting 50%" — direct OE-2 tests |

## 3. IDENTIFIED CANDIDATES FOR ACQUISITION (dated, data not stored)

From Tom's "Journal Master 2025" table, visible in frame `V1H-defining_a_good_extension/slides/00-02-42.jpg`. Times are
journal-local (UTC+11, the convention already established for CX-TE1-1); UTC conversion shown for planning only.
Outcome columns exist in that table and are **not** recorded here.

| Candidate | Instrument | Journal time (local) | ≈ UTC | Journal labels | Confidence | data_available | machine_testable |
|---|---|---|---|---|---|---|---|
| JM-2025-10-29a | XAU/USD | 2025-10-29 7:14 PM | 2025-10-29 08:14 | TRR PT · Trending · 3 | legible | no (fetchable) | potential |
| JM-2025-10-17 | XAU/USD | 2025-10-17 12:53 PM | 2025-10-17 01:53 | IFS · Volume · 3 | legible | no (fetchable) | potential |
| JM-2025-10-16 | XAU/USD | 2025-10-16 11:41 AM | 2025-10-16 00:41 | TRR CT · Trending · 1 | legible | no (fetchable) | potential |
| V15-SEM-2026-05 | XAUUSD | ~2026-05-01/02 (5s chart, FOREX.com) | — | **CBR15** seconds-entry walkthrough | chart date legible in frame `V15-seconds_entry_model/slides/00-00-22.jpg`; entry not yet extracted | no (fetchable) | potential |

Two of the same table's rows independently corroborate the existing examples (Oct 24 3:38 PM "textbook" = CX-TE1-1;
Oct 21 12:39 PM "new" = CX-LT1-1), which supports the time-zone convention used above.

## 4. Gap analysis against the D28 §18 target

| Target | Status |
|---|---|
| 3 positive CBR1H examples | **met** (machine set) |
| CX-LT3-1 negative | **met** |
| CX-LT2-2 positive narrative | **met** |
| CX-LT2-1 negative narrative | **met** |
| ≥ 2 additional type-3 instructional examples | **met narratively** (T3-VP1-A, T3-VP1-B, T3-VP2-HILO) |
| ≥ 1 CBR15 positive example from L1 | **candidate identified** (V15-SEM-2026-05); needs entry extraction and a data fetch |
| ≥ 1 additional no-trade / rejected example | **met** (CX-LT2-1); OE-BAD adds a rejected *extension* |

## 5. What would be needed to grow the machine set

1. **Extraction work:** for each acquisition candidate, pull entry time, direction, stop and target references from the
   video frames the way the existing course examples were built (no outcomes).
2. **Data acquisition:** Dukascopy XAUUSD ticks for 2025-10-16, 2025-10-17, 2025-10-29 (each ~24 hour-files) and for
   the CBR15 example's date once identified. All are XAUUSD, so no new instrument enters research scope. The 2025 dates
   sit inside the holdout window and would be parity-use-only, logged as usual.
3. **Owner authorization** for those fetches, which this package does **not** assume.

## 6. Honest limits

- The machine set is still **one instrument, one model, one session family**. Adding the three journal dates would give
  different sessions (London and pre-London hours) and a different MTF model family (TRR PT, IFS) but stays XAUUSD.
- USDJPY examples cannot become machine-testable without adding an instrument, which D28 §17 excludes.
- Journal rows are Level 2 for rule purposes; they are usable as *dated pointers* to Level-1-quality video walkthroughs
  only where a video covers the same trade.
