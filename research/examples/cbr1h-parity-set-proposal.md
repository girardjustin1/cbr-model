# Corrected CBR1H parity-set proposal

**Doc:** CBR-SET-002 · **Version:** v1.0 (PROPOSAL) · **Date:** 2026-09-16 · **Ruling:** D33 §14
**Status:** FOR OWNER APPROVAL. Nothing here is frozen, nothing is scored, no case is deleted, and the frozen
manifest `a3ee0bd6…` that CBR-RUN-013C-1 used is untouched. Every entry-level case remains **unseen** by any future
candidate until that candidate is frozen and authorized (D33 §18).

`model_scope` is the new required field: a case may bind a CBR1H verdict only at `CONFIRMED_CBR1H`.

---

## A. Machine set — ENTRY_LEVEL (may bind a verdict)

| case_id | Source | Evidence | model_scope | Pos/Neg | Dir | Source-supported fields | Data | Binds |
|---|---|---|---|---|---|---|---|---|
| CX-LT1-1 | `V1H-live_trade_1_gold_win` | L1_VIDEO | CONFIRMED_CBR1H | POSITIVE | BUY | entry time + price, stop, target, condition, extension, HVCS→HILO narration | held (10-20…21) | yes |
| CX-TE1-1 | `V1H-trade_example_1` | L1_VIDEO | CONFIRMED_CBR1H | POSITIVE | BUY | entry interval + price, stop, target | held (10-20…24) | yes |
| CX-LT3-2 | `V1H-live_trade_3_gold_win` | L1_VIDEO | CONFIRMED_CBR1H | POSITIVE | SELL | entry time + price, stop, target | held (11-07…10) | yes |
| CX-LT3-1 | `V1H-live_trade_3_gold_win` | L1_VIDEO | CONFIRMED_CBR1H | **NEGATIVE** | SELL | rejected window + stated reasons | held | yes |

Unchanged from the frozen set. These four have never been altered and are the only entry-level cases with a stated
entry.

## B. Machine set — HOUR_LEVEL (may bind a verdict)

| case_id | Source | Evidence | model_scope | Dir | Source-supported fields | Data | Binds |
|---|---|---|---|---|---|---|---|
| JM-2025-10-16 | Journal Master 2025 row, L1 frame | L1_FRAME_JOURNAL_TABLE | **CONFIRMED_CBR1H** (TRR CT = counter trending range) | SELL | hour, direction, MTF label, CB bucket | held (10-15…16) | yes |

One case, not three. Its dating is corroborated by price action inside the frozen hour (high 4 227.32 at 00:40,
reversing), independently of the journal's time column.

## C. Candidate examples promoted from the evidence search (NOT yet machine cases)

Found during the OQ-48 search (`reports/oq48-independent-examples.md`). Both are XAUUSD with 1m and 5s data held,
and both are Level-1 lessons in which Tom points at the sequence and calls it valid.

| case_id | Source | Evidence | model_scope | Source-supported fields | Missing | Proposed level |
|---|---|---|---|---|---|---|
| HX-1 | `V1H-seconds_shift_1m_hilo_hvcs` @ 00:02:06, 2025-10-23 ≈ 05:18-05:27 UTC | L1_VIDEO | CONFIRMED_CBR1H (HVCS→HILO, variant A) | HVCS sequence, extension direction, approximate shift minute, previous-15m take | **no stated entry time or price**; arm/sweep times not derivable without a run | HOUR_LEVEL or SEQUENCE_LEVEL |
| HX-2 | `V1H-candle_behavior_extension` @ 00:03:38, 2025-10-29 ≈ 02:29-02:37 UTC | L1_VIDEO | CONFIRMED_CBR1H (HVCS→HILO at the 15m midpoint) | same | same | HOUR_LEVEL or SEQUENCE_LEVEL |

**Recommendation:** admit them only as a new **SEQUENCE_LEVEL** scoring level whose scored fields are exactly
*"an HVCS of ≥ 4 minutes is recognised over the stated window, in the stated direction"* — the only thing the source
states. They must not be given an entry-level dimension table, and they must not be scored until frozen, because
they were used as evidence in the OQ-48 review. Using them to score the same rule they helped resolve would be
circular; the owner may prefer to keep them as evidence only. **They are excluded from any verdict-binding set in
this proposal.**

## D. Preserved, not deleted — moved out of the CBR1H machine set

| case_id | Why | New home |
|---|---|---|
| JM-2025-10-17 | **IFS** — a middle-timeframe model the engine does not implement (`mtf-model-taxonomy.md` §4) | `future_model_validation`, tagged `IFS_NOT_IMPLEMENTED` |
| JM-2025-10-29 | **SOURCE_AMBIGUITY** — the time column (minute 14) and the CB column (37) disagree; the frozen hour contains no down-extension for a BUY | NARRATIVE / REFERENCE ONLY |

## E. Narrative / geometry set (never binds, unchanged)

CX-LT2-2, CX-LT2-1, T3-VP1-A, T3-VP1-B, T3-VP2-HILO, OE-GOOD-BAD, V15-SEM-2026-05 — as frozen, plus HX-3, HX-4 and
HX-6 from the OQ-48 search as additional geometry references, and HX-5 recorded as **excluded** (it appears to be the
same market event as CX-TE1-1, so it is not independent).

## F. What this set can and cannot support

- **Can:** four entry-level cases (3 positive, 1 negative) and one hour-level case, all XAUUSD, all CBR1H, two
  sessions plus one.
- **Cannot:** any claim about FS/IFS contexts, CBR15, USDJPY, or generalization across sessions. The hour-level
  evidence is now a single case, which is weaker than the three the frozen set claimed — an honest reduction, not a
  loss of information.
- **Unresolved before this set is frozen:** whether HX-1/HX-2 may be scored at all (§C), and the journal column
  semantics (`mtf-model-taxonomy.md` §7).

## G. Process requirements for the next freeze

1. Add `model_scope` to every manifest record; refuse to score anything that is not `CONFIRMED_CBR1H`.
2. Pre-declare the STRICT / DESCRIPTIVE two-layer reporting before execution (D32 §7.1).
3. Synthetic fixtures only for pre-freeze smoke tests (D32 §7.2).
4. Keep the previous manifest hash on record: the corrected set is a **new** manifest, not an edit of `a3ee0bd6…`.
