# Phase 13C — evaluation instant: decision vs shift

**Ruling:** D32 §5-8 · **Status:** DIAGNOSTIC ONLY. Both columns are causal — the 5s shift is later than every bar close either reading uses — so this asks only where in the course's sequence each rule belongs. PC3 is unchanged and no corrective run was made.

PC3 writes every extension-derived rule into the decision ledger at the instant the type-3 arms, and moves only the HVCS rule to the trigger (D29-11 / H-3). The master slide E1H-003 orders the model differently: HVCS (4+ mins) → beyond the previous LTF/MTF high → **after the 15m opens, price wicks / pushes a bit more** → HILO beyond structure → entry on the break. Everything up to the entry is allowed to complete before the trade exists.

## CX-LT1-1 — `3` BUY, decision 2025-10-21 01:35:35+00:00, shift 2025-10-21 01:39:35+00:00

| Rule | At decision (PC3) | At shift | Detail at decision | Detail at shift |
|---|---|---|---|---|
| `M1H-LOC-01` | PASS | PASS | extension extreme 4341.62 at 01:30 → range position 0.098 | extension extreme 4332.95 at 01:38 → range position -0.098 |
| `M1H-OE-01` | PASS | PASS | 23 min from activation (needs ≥ 20) | 31 min from activation (needs ≥ 20) |
| `M1H-OE-02` | PASS | PASS | deepest retracement ratio 0.286 | deepest retracement ratio 0.223 |
| `M1H-6A-2-PREV-15M-BROKEN-BY-Q` | PASS | PASS | Q 01:30 takes Q−1's low: True; Q−1 closed in trade direction: False | Q 01:30 takes Q−1's low: True; Q−1 closed in trade direction: False |
| `M1H-6A-3-NEW-EXTREME-IN-Q` | PASS | PASS | extension extreme 01:30 vs Q open 01:30 | extension extreme 01:38 vs Q open 01:30 |
| `M1H-6A-1-HVCS-INTO-SHIFT` | **FAIL** | **FAIL** | 1 conforming minutes ending 01:30 (needs ≥ 4) | 3 conforming minutes ending 01:38 (needs ≥ 4) |

## CX-TE1-1 — `3` BUY, decision 2025-10-24 04:33:25+00:00, shift 2025-10-24 04:38:55+00:00

| Rule | At decision (PC3) | At shift | Detail at decision | Detail at shift |
|---|---|---|---|---|
| `M1H-LOC-01` | PASS | PASS | extension extreme 4103.76 at 04:30 → range position -0.060 | extension extreme 4102.88 at 04:37 → range position -0.083 |
| `M1H-OE-01` | PASS | PASS | 23 min from activation (needs ≥ 20) | 30 min from activation (needs ≥ 20) |
| `M1H-OE-02` | PASS | PASS | deepest retracement ratio 0.217 | deepest retracement ratio 0.208 |
| `M1H-6A-2-PREV-15M-BROKEN-BY-Q` | PASS | PASS | Q 04:30 takes Q−1's low: True; Q−1 closed in trade direction: False | Q 04:30 takes Q−1's low: True; Q−1 closed in trade direction: False |
| `M1H-6A-3-NEW-EXTREME-IN-Q` | PASS | PASS | extension extreme 04:30 vs Q open 04:30 | extension extreme 04:37 vs Q open 04:30 |
| `M1H-6A-1-HVCS-INTO-SHIFT` | **FAIL** | **FAIL** | 0 conforming minutes ending 04:30 (needs ≥ 4) | 2 conforming minutes ending 04:37 (needs ≥ 4) |

## CX-LT3-2 — `3` SELL, decision 2025-11-10 01:34:45+00:00, shift 2025-11-10 01:39:40+00:00

| Rule | At decision (PC3) | At shift | Detail at decision | Detail at shift |
|---|---|---|---|---|
| `M1H-LOC-01` | PASS | PASS | extension extreme 4052.01 at 01:26 → range position 1.654 | extension extreme 4053.43 at 01:37 → range position 1.691 |
| `M1H-OE-01` | **FAIL** | PASS | 16 min from activation (needs ≥ 20) | 27 min from activation (needs ≥ 20) |
| `M1H-OE-02` | PASS | PASS | deepest retracement ratio 0.129 | deepest retracement ratio 0.186 |
| `M1H-6A-2-PREV-15M-BROKEN-BY-Q` | **FAIL** | PASS | Q 01:30 takes Q−1's high: False; Q−1 closed in trade direction: False | Q 01:30 takes Q−1's high: True; Q−1 closed in trade direction: False |
| `M1H-6A-3-NEW-EXTREME-IN-Q` | **FAIL** | PASS | extension extreme 01:26 vs Q open 01:30 | extension extreme 01:37 vs Q open 01:30 |
| `M1H-6A-1-HVCS-INTO-SHIFT` | **FAIL** | **FAIL** | 1 conforming minutes ending 01:26 (needs ≥ 4) | 0 conforming minutes ending 01:37 (needs ≥ 4) |

## JM-2025-10-17 — `3` BUY, decision 2025-10-17 01:38:20+00:00, shift 2025-10-17 01:46:35+00:00

| Rule | At decision (PC3) | At shift | Detail at decision | Detail at shift |
|---|---|---|---|---|
| `M1H-LOC-01` | **FAIL** | PASS | extension extreme 4317.99 at 01:33 → range position 0.477 | extension extreme 4279.07 at 01:44 → range position 0.148 |
| `M1H-OE-01` | PASS | PASS | 26 min from activation (needs ≥ 20) | 37 min from activation (needs ≥ 20) |
| `M1H-OE-02` | PASS | PASS | deepest retracement ratio 0.384 | deepest retracement ratio 0.205 |
| `M1H-6A-2-PREV-15M-BROKEN-BY-Q` | PASS | **FAIL** | Q 01:30 takes Q−1's low: True; Q−1 closed in trade direction: False | Q 01:45 takes Q−1's low: False; Q−1 closed in trade direction: False |
| `M1H-6A-3-NEW-EXTREME-IN-Q` | PASS | **FAIL** | extension extreme 01:33 vs Q open 01:30 | extension extreme 01:44 vs Q open 01:45 |
| `M1H-6A-1-HVCS-INTO-SHIFT` | **FAIL** | PASS | 3 conforming minutes ending 01:33 (needs ≥ 4) | 4 conforming minutes ending 01:44 (needs ≥ 4) |
