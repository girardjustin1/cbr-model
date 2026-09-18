# Phase 13D PC4 Parity Protocol

**Doc:** CBR-PROT-013D · **Version:** v1.1 **APPROVED** · **Date:** 2026-09-17 · **Rulings:** D34 §18, **D35**
**Status:** APPROVED for scored execution by owner ruling D35 (`d35-pc4-scored-parity-authorization.md`), which
settles decisions E-1…E-5 and freezes the E-2 hour-level threshold. Run id **CBR-RUN-013D-1**. Frozen with D35
before execution.

**Candidate under test:** `CBR1H_BASELINE_V1-PC4`, spec hash
`62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7`.
`CBR15_BASELINE_V1-PC4` is SPEC_ONLY and out of scope.
**Parity set:** `research/examples/parity_set_manifest_v2.json`, manifest hash
`e12f3882f01b8ac4655520f00d5cd19829da989a371a1feb15b070d1a718804e`.
**Predecessors, frozen and never re-run:** PC2 FAIL (CBR-RUN-013B-2) · PC3 FAIL (CBR-RUN-013C-1).

---

## 1. Binding machine cases (D34 §12)

Only `model_scope = CONFIRMED_CBR1H` may bind. Five cases:

| case_id | Level | Dir | Pos/Neg | Source-supported fields |
|---|---|---|---|---|
| CX-LT1-1 | ENTRY_LEVEL | BUY | positive | entry time and price, stop, target, condition, extension, HVCS→HILO narration |
| CX-TE1-1 | ENTRY_LEVEL | BUY | positive | entry interval and price, stop, target |
| CX-LT3-2 | ENTRY_LEVEL | SELL | positive | entry time and price, stop, target |
| CX-LT3-1 | ENTRY_LEVEL | SELL | **negative** | rejected window and stated reasons |
| JM-2025-10-16 | HOUR_LEVEL | SELL | positive | hour, direction, MTF label, CB bucket |

Non-binding and never counted: JM-2025-10-17 (`IFS_NOT_IMPLEMENTED`), JM-2025-10-29 (`SOURCE_AMBIGUITY`), HX-1 and
HX-2 (OQ-48 evidence: scoring the rule they resolved would be circular), and the seven narrative cases.

## 2. Scoring dimensions

**2.1 ENTRY_LEVEL — the nine dimensions inherited from CBR-PROT-013C §2.1**, unchanged: model family · direction ·
condition compatibility · extension direction · extension activation · location / previous-candle event · required
HVCS state · type-3 / 5s structural trigger (D25-P3 equivalence) · eligible candidate existence.

Hard dimensions, set by D35 §3 and not redefinable after execution: **model family · direction · extension
direction · extension activation · location / previous-15m event · HVCS eligibility under PC4 · 5-second type-3
structural shift · eligible candidate existence**. Condition compatibility (dimension 3) is scored and classified
but is **not** a hard dimension.

**2.2 HOUR_LEVEL — only source-supported fields**: setup exists in the hour · direction · model family if
source-defined · condition if source-defined · timing bucket if source-defined. Exact trigger, entry, stop and
target are never scored and never inferred from engine output.

**2.3 Negative** — CX-LT3-1: no eligible candidate whose 5s shift falls in the rejected window.

## 3. Strict / descriptive reporting, pre-declared (D34 §16)

Frozen **before** the run, not introduced during it:

| View | What it may do | What it may never do |
|---|---|---|
| **STRICT** | score only eligible signals (`ARMED_AT_TRIGGER`); this is the only view that touches acceptance | — |
| **DESCRIPTIVE** | show the closest structurally relevant candidate, eligible or not, and name the rule that blocked it | satisfy strict acceptance, or contribute to any count |

Every per-case table must label which view each row belongs to.

## 4. Mismatch taxonomy

Unchanged and applied in order: DATA_LIMITATION → FEED_DIFFERENCE → FEED_DEPENDENT_SIGNAL_DIFFERENCE →
EXECUTION_DEPENDENT → OWNER_BASELINE_CHOICE → UNRESOLVED_SPEC_AMBIGUITY → IMPLEMENTATION_BUG → CANON_MISMATCH, plus
CANDIDATE_SELECTION_MISMATCH and PARITY_SET_CORRECTION (D35 §6). Every scored mismatch receives exactly **one**
primary classification, and UNRESOLVED_SPEC_AMBIGUITY may not be used to conceal an implementation defect. A rule
whose failing quantity is a carried ASSUMPTION is not a canon mismatch. Every mismatch is classified; an
unclassified mismatch is a FAIL.

## 5. Candidate selection

The frozen deterministic rule (`parity.select_candidate`) is unchanged and answer-independent. Each case reports
both whether the correct structural event exists anywhere in the eligible set, and which candidate the rule chose.
A divergence is `CANDIDATE_SELECTION_MISMATCH` and never a trigger failure.

## 6. Negative-control handling

CX-LT3-1 must produce no eligible candidate in 2025-11-10 01:28-01:36 UTC. A signal there is a FAIL unless it
classifies as an approved mismatch class. PC3 passed this control and PC4 changes nothing that loosens it in that
window, so a regression here would itself be a finding.

## 7. Acceptance rules (approved, D35 §9)

| Id | Rule |
|---|---|
| **D-1** | **ENTRY_LEVEL positives:** all three must agree on every §2.1 hard dimension unless a pre-existing approved non-failing classification applies (D35 §3) |
| **D-2** | **Condition (dimension 3)** and any non-hard difference: classified and reported; an unclassified mismatch is a FAIL |
| **D-3** | **HOUR_LEVEL (set by D35 §5, E-2):** `HOUR_MATCH` only when every source-supported field agrees. **1/1 allows a clean PASS** if every other requirement holds; **0/1 does not independently FAIL** but caps the verdict at PASS WITH CONCERNS, provided every binding entry-level hard gate and the negative control pass. The mismatch is still reported, classified, explained and retained as a concern. The hour-level case can never rescue an entry-level failure or a failed control |
| **D-4** | **Negative:** CX-LT3-1 produces no eligible candidate in its window |
| **D-5** | **Gates:** the complete run repeated with identical result hashes; PC2, PC3 and PC4 hashes unchanged; the full suite passing on the run commit |
| **D-6** | **Selection:** `CANDIDATE_SELECTION_MISMATCH` never counts as a trigger failure |
| **D-7** | **Verdict:** PASS only if D-1, D-4 and D-5 hold with no unclassified mismatch and no concern; PASS WITH CONCERNS if they hold with documented classified mismatches; FAIL if a hard dimension fails without an approved class, an implementation bug is open, or determinism fails |

## 8. Carried assumptions (passing does not convert any into CANON)

The OQ-48 anchor, counting convention and unit · minute-7 earliest activation · the Q1 qualifier · ATR zig-zag
k = 3 · the extension-origin choice · the tradable-time condition window · the F-10 Q anchor at a 15m boundary.

## 9. Prohibited during the run

No parameter change · no alternative HVCS anchor or counting convention · no `max_violations` other than 1 · no
alternative candidate ranking · no optimization · no P&L or outcome data · no post-hoc rule redefinition · no
answer-aware adjustment of PC4 · no use of a scored case as a development fixture.

## 10. Execution order

1. Freeze: protocol hash, PC4 spec hash, parity-manifest v2 hash, market-data hashes; full suite and lint.
2. Machine set (5 binding cases), twice, identical result hashes.
3. Narrative set assessed qualitatively.
4. Classification register, selection register, strict and descriptive tables.
5. Report, then **STOP** for the owner's Phase 13D verdict.

## 11. Known limits to state in the report

XAUUSD only · CBR1H only · five binding cases (three positive, one negative, one hour-level) · the hour-level
evidence is now a **single** case, weaker than the three D31 used · CBR15 unscored · `k = 3` fixed, and CX-LT3-2's
trigger is known to disappear at `k = 4` · PC4 carries the assumptions in §8 · FS/IFS contexts are not implemented.

## 12. Owner decisions (all settled)

| Id | Decision | Settled in D35 |
|---|---|---|
| E-1 | Approve this protocol and the §2 dimensions | approved; hard dimensions listed in D35 §3 |
| E-2 | Set the D-3 hour-level threshold | 1/1 clean PASS · 0/1 caps at PASS WITH CONCERNS, never an independent FAIL |
| E-3 | Confirm the corrected parity set as the scoring set | confirmed (`e12f3882…`) |
| E-4 | Confirm CBR15 stays out of scope | confirmed |
| E-5 | Authorize the scored run | **authorized** as CBR-RUN-013D-1 |

**All E-1…E-5 decisions were made in D35; this protocol is approved and executed as CBR-RUN-013D-1.**
