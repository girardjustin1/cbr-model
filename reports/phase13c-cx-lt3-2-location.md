# CX-LT3-2 — location / previous-15m mismatch diagnosis

**Ruling:** D32 §8 · **Status:** DIAGNOSTIC ONLY. No rule was changed, no corrective run was made, and no trade
outcome was read. Source: `reports/phase13c-evaluation-instant.md`, `data/phase13c/run-1.json`.

## The mismatch being diagnosed

Phase 13C scored CX-LT3-2 dimension 6 (`location_or_previous_candle_event`) as a mismatch, classified
CANON_MISMATCH, on candidate `…/A/20251110T0100/SELL/3` — the candidate whose 5s shift (01:39:40) is
D25-P3-equivalent to Tom's stated 01:40:00 entry. Two rules failed: `M1H-6A-2-PREV-15M-BROKEN-BY-Q` and
`M1H-6A-3-NEW-EXTREME-IN-Q`. `M1H-LOC-01` passed.

## The facts

Hourly extension **UP**, activation 01:10, trade direction SELL. Entry 15m candle **Q = 01:30-01:45**; previous
candle **Q−1 = 01:15-01:30**, high **4052.0115**, low 4027.195, open 4027.24, close 4047.84 (so Q−1 closed *up*, i.e.
not in the trade direction, which is why the D19-4 exception does not apply).

| Instant | Q's high so far | Takes Q−1's high (4052.01)? | Extension extreme known | In Q? | `M1H-6A-2` | `M1H-6A-3` | `M1H-OE-01` |
|---|---|---|---|---|---|---|---|
| Decision **01:34:45** (what PC3 scores) | 4049.61 | no | 01:26 | no | **FAIL** | **FAIL** | **FAIL** (16 min) |
| 5s shift **01:39:40** | 4053.43 | yes | 01:37 | yes | PASS | PASS | PASS (27 min) |

Q first exceeds Q−1's high during the **01:35** minute (high 4052.70). The extension then extends to its extreme at
**01:37** (4053.43). Both events fall between candidate 3's decision instant and its shift.

## Answering each possibility in D32 §8

| Possibility | Verdict |
|---|---|
| Q−1 is wrong | **No.** Q−1 = 01:15-01:30 under D19-4, and its high 4052.0115 is exactly the level the push takes out. |
| Q's take is wrong | **No.** Q does take Q−1's high, by Q's own 5s bars, inside the entry candle — precisely what E1H-034 describes ("you want this current 15 minute candle to push and take out the previous high"). |
| **The event occurs after the engine's required timestamp** | **Yes — this is the cause.** PC3 writes `M1H-6A-2` and `M1H-6A-3` into the *decision* ledger, evaluated when the 5s type 3 arms (01:34:45). The take (01:35) and the new extreme (01:37) happen after that instant and before the shift (01:39:40), so the rules are evaluated one push too early. |
| The course example uses another previous-candle interpretation | **Not needed.** The standard interpretation is satisfied on this hour; only the instant differs. |
| The report is evaluating the wrong candidate | **No.** Candidate 3 is the only one whose shift matches Tom's stated entry (01:39:40 vs 01:40:00). Candidate 4 does satisfy both rules — its decision instant is 01:43:35, after the take — but its shift is 01:45:45, roughly six minutes after Tom's entry and outside D25-P3 equivalence. Scoring candidate 4 instead would have replaced a location mismatch with a trigger-time mismatch. |
| Another rule is responsible | **Partly.** `M1H-OE-01` (extension ≥ 20 minutes) also fails at the decision instant (16 min) and passes at the shift (27 min), from the same cause. `M1H-6A-1-HVCS-INTO-SHIFT` fails at **both** instants and is a separate defect (OQ-48). |

## Reading against canon

The master slide E1H-003 orders the model: HVCS (4+ mins) → **goes beyond prev LTF/MTF high** → *after the 15m
opens, price creates a wick / pushes a bit more* → HILO beyond structure → **entry on the break of structure**. Every
one of those steps is allowed to complete before the trade exists. PC3 instead requires steps 2 and 3 to be already
complete at the moment the type 3 *arms*, which in this hour is 4 minutes 55 seconds before the entry.

D29-11 (change H-3) already recognised this class of defect and moved the HVCS rule to trigger-time evaluation. The
same reasoning was not applied to `M1H-LOC-*`, `M1H-6A-2`, `M1H-6A-3` or `M1H-OE-01`.

## Important counter-evidence, so this is not read as a clean fix

On **JM-2025-10-17** the same move runs the other way: `M1H-LOC-01` flips FAIL → PASS at the shift, but `M1H-6A-2`
and `M1H-6A-3` flip PASS → **FAIL**, because that shift (01:46:35) lands 1.6 minutes inside a *new* 15m candle, so
`Q` becomes 01:45-02:00 and the take is no longer inside it. Which 15m candle anchors `Q` when the shift lands early
in a new quarter is not settled by any source. A rule-instant change is therefore **not** a safe mechanical fix, and
none is proposed here.

## Classification

**UNRESOLVED_SPEC_AMBIGUITY**, upgraded from the run's provisional CANON_MISMATCH. PC3's rules reproduce canon's
*content* on this hour; what is unresolved is *when* canon evaluates them, and the JM-2025-10-17 counter-example shows
the answer is not simply "at the shift". The Phase 13C verdict is unaffected: this dimension was never one of the
four hard dimensions, and CX-LT3-2 fails its core-trigger dimension on eligibility regardless.
