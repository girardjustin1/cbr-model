# Holdout Access Log

Holdout period: **2025-01-01 → 2026-08-31**. Single use (CBR-GOV-001 §7).

Every access to holdout-period data is appended here, whether it's for parity or evaluation.

| Date | Who | Purpose | Data / days | Performance inspected? | Approval ref |
|---|---|---|---|---|---|
| 2026-09-14 | Claude Code | Implementation parity: structure primitives vs course example CX-LT1-1 (Tom's 2025-10-21 gold buy). Found type 3 pairing bug F-0; raised F-1/F-2 (now OQ-22/OQ-23). | XAUUSD 1m/5s, 2025-10-20 → 2025-10-22 | **No.** Only signal structure compared to the taught trade; no trade simulation, P&L or statistics | Parity use permitted by data-requirements §6 |
| 2026-09-14 | Claude Code | Phase 9 data acquisition + integrity and feed comparison for parity fixture days | XAUUSD / DOLLARIDXUSD ticks, GC/DX 1m, 2025-10-20 → 2025-11-11 fixture days | **No.** Data integrity and feed differences only | Parity use permitted |
| 2026-09-14 | Claude Code | Phase 9 AC-11A sample-day acquisition + integrity/feed comparison (recorded for audit: all 16 sample days fall in dev 2018-2022 / validation 2023-2024, **none in the holdout**) | XAUUSD / DOLLARIDXUSD 1m candles + 4 tick windows; GC/DX 1m | **No.** Integrity and feed differences only | CBR-ACC-009 v2 (D11) |
| 2026-09-14 | Claude Code | Phase 10 DXY context acceptance (CBR-ACC-010): causal DXY context, causality/determinism checks, direction agreement vs DX on fixture days (holdout period) and sample days | DOLLARIDXUSD 1m candles + DX 1m volume/open/close, fixture days 2025-10-20…2025-11-11 | **No.** Context integrity only; no XAU trades, P&L or signal statistics | Parity/integrity use permitted; D14 |
| 2026-09-15 | Claude Code | OQ-25 extremes study (CBR-DEC-025): candle-file vs tick-derived highs/lows and structure consequences (swings, ranges, takes, sweeps, extensions, stop-level touches); no entries or trades | XAUUSD full-day ticks + candles + GC 1m, 2025-10-21…24 and 2025-11-10 (plus 16 dev/val sample days) | **No.** Data fidelity only; no trades, P&L or signal statistics | D15-4 (owner-directed OQ-25 package) |
| 2026-09-15 | Claude Code | Phase 11 CBR15 engine runs (implementation parity): rule outcomes, candidates and ARMED signals on the three course-example windows; engine causality/determinism tests on CX-TE1-1; warm-up ticks fetched for 2025-11-07 and 2025-11-09 | XAUUSD STRUCTURE bars 2025-10-20…24, 2025-11-07…10 | **No.** No fills, trade outcomes, P&L or aggregate raw-setup outcomes reported | D16-5 |
| 2026-09-15 | Claude Code | Phase 12 CBR1H engine and course-example parity (context, direction, extension, timing, structure trigger, entry time, stop-anchor and target inputs, acceptance); CBR15 rerun with the hourly veto; engine causality/determinism tests | XAUUSD STRUCTURE bars 2025-10-20…24, 2025-11-07…10 | **No.** No fills, trade outcomes, P&L or aggregate raw-setup outcomes reported | D17-7 |
