# Holdout Access Log

Holdout period: **2025-01-01 → 2026-08-31**. Single use (CBR-GOV-001 §7).

Every access to holdout-period data is appended here, whether it's for parity or evaluation.

| Date | Who | Purpose | Data / days | Performance inspected? | Approval ref |
|---|---|---|---|---|---|
| 2026-09-14 | Claude Code | Implementation parity: structure primitives vs course example CX-LT1-1 (Tom's 2025-10-21 gold buy). Found type 3 pairing bug F-0; raised F-1/F-2 (now OQ-22/OQ-23). | XAUUSD 1m/5s, 2025-10-20 → 2025-10-22 | **No.** Only signal structure compared to the taught trade; no trade simulation, P&L or statistics | Parity use permitted by data-requirements §6 |
| 2026-09-14 | Claude Code | Phase 9 data acquisition + integrity and feed comparison for parity fixture days | XAUUSD / DOLLARIDXUSD ticks, GC/DX 1m, 2025-10-20 → 2025-11-11 fixture days | **No.** Data integrity and feed differences only | Parity use permitted |
| 2026-09-14 | Claude Code | Phase 9 AC-11A sample-day acquisition + integrity/feed comparison (recorded for audit: all 16 sample days fall in dev 2018-2022 / validation 2023-2024, **none in the holdout**) | XAUUSD / DOLLARIDXUSD 1m candles + 4 tick windows; GC/DX 1m | **No.** Integrity and feed differences only | CBR-ACC-009 v2 (D11) |
