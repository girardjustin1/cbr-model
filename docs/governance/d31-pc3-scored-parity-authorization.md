# D31 PC3 Scored Parity Authorization: Ruling Record

**Doc:** CBR-RULING-D31 · **Date:** 2026-09-16 · **Decided by:** Owner ("OWNER APPROVAL — PC3 SCORED PARITY / CBR-PROT-013C")

## Result

**PC3 is authorized for scored parity.** CBR-PROT-013C is approved subject to the acceptance rulings below. This is the
first scored parity run of PC3. PC3, the parity-set manifest and the scoring fields are not modified during the run. No
optimization, no P&L or trade outcomes. Phase 14 does not begin until the completed Phase 13C report is reviewed.

## Frozen inputs (D31-1)

| Input | Hash |
|---|---|
| PC3 spec | `7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453` |
| PC2 spec | `4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2` |
| Parity-set manifest | `a3ee0bd6ba225ce6b89d8bc61fbefd227ce8097a3f6bfac2f9414e19cd81ea9c` |

CBR-PROT-013C, the candidate-selection rules, the acceptance rules, every market-data input and every evidence source
are hashed in the run manifest before execution. **If any frozen hash changes before execution: STOP**, and never
regenerate or accept the changed input automatically.

## Rulings

| Id | Item | Ruling |
|---|---|---|
| D31-2 | Machine set | Exactly seven cases: ENTRY_LEVEL positives CX-LT1-1, CX-TE1-1, CX-LT3-2; ENTRY_LEVEL negative CX-LT3-1; HOUR_LEVEL JM-2025-10-16, JM-2025-10-17, JM-2025-10-29. No case may be added after scoring begins |
| D31-3 | Narrative set | Separate, qualitative only, no machine-pass contribution, never converted into machine cases after seeing results |
| D31-4 | Entry-level acceptance | Nine hard dimensions evaluated. The D25 principle stands: **model family 3/3, direction 3/3, extension direction 3/3, core structural trigger 3/3**. No unexplained implementation bug or canonical mismatch may affect them |
| D31-5 | Core trigger | Frozen per variant (A: context → extension active → extension quality → location → previous-15m take → valid HVCS → 5s type 3 → eligible candidate; B: context → extension active → 1m type-3 parent → required pullback → 5s type 3 → eligible candidate). Never redefined after execution |
| D31-6 | Negative control | CX-LT3-1 must not produce the specifically rejected eligible canonical setup; expected `NO_ELIGIBLE_CANONICAL_SIGNAL`. If one exists, report it, classify the exact rule path that admitted it, and do not change PC3 |
| D31-7 | Hour-level acceptance | The journal cases bind the verdict under their own threshold. `HOUR_MATCH` only if **every** source-supported field agrees; fields absent from the source are not scored and never inferred |
| D31-8 | Hour-level threshold | 3/3 supports a clean PASS; 2/3 caps the verdict at PASS WITH CONCERNS; 0/3 or 1/3 is a **FAIL**. Not modifiable after execution |
| D31-9 | Hour-level direction | Direction is source-supported in all three; a qualifying setup in the declared hour in the opposite direction is `HOUR_MISMATCH`, never "approximately correct" |
| D31-10 | Hour-level existence | No qualifying setup in the declared hour is `HOUR_MISMATCH`; neighbouring hours are not searched unless the frozen source metadata permits a broader bucket |
| D31-11 | Model labels | Score model family only to the specificity the frozen source supports; do not force an implementation subtype, and do not reinterpret the frozen mapping after seeing results |
| D31-12 | Candidate selection | For every ENTRY_LEVEL case report both whether the expected structural event exists anywhere in the eligible set and which candidate the frozen rule selects. Divergence is `CANDIDATE_SELECTION_MISMATCH`, not a type-3 failure; selection is never changed during the run |
| D31-13 | Assumptions | Minute-7 activation, Q1 qualifier, k = 3, swing confirmation, tradable window and the extension-origin choice keep their ASSUMPTION labels; passing parity does not convert them to CANON; no sensitivity testing during the run |
| D31-14 | No alternatives | No k = 2/4, activation minute, LAST_RESET, FINAL_PUSH, alternative max_reversal, pullback, selection or condition-window logic. One frozen PC3 configuration is tested |
| D31-15 | Taxonomy | Predeclared classes preserved, including `CANDIDATE_SELECTION_MISMATCH`; exactly one primary class per mismatch; secondary tags allowed; a broad class may never hide an implementation failure |
| D31-16 | Verdict | PASS requires all four entry-level hard gates on all three positives, the negative control clean, **3/3** hour-level matches, no unresolved implementation bug or unexplained canonical mismatch on signal membership, identical deterministic rerun, and causality/hash gates. PASS WITH CONCERNS allows exactly 2/3 hour-level with all entry-level gates and the control passing and every mismatch classified. FAIL on a hard-dimension failure without a pre-approved class, a rejected canonical signal in the control, 0/3 or 1/3 hour-level, an implementation bug affecting membership, an unexplained canonical mismatch on a hard gate, or a determinism/causality/hash failure. No aggregate percentage |
| D31-17 | Execution order | Ten steps: verify hashes → suite and lint → three entry-level positives → negative control → three hour-level cases → narrative set → classify → second complete run → verify identical hashes → report. No P&L at any point |
| D31-18 | Reporting | Per-case fields as specified, including expected vs engine values, every mismatch class, eligible and selected candidates, and the exact admitting path for any negative-control signal |
| D31-19 | Narrative reporting | CONSISTENT / INCONSISTENT / NOT_DETERMINABLE with reasons; cannot override machine parity; may raise concerns |
| D31-20 | Run id | New immutable id, not reusing CBR-RUN-013B-1/-2: **CBR-RUN-013C-1**. Record protocol, PC3, manifest, commit, market-data and result hashes |
| D31-21 | After the run | One verdict only; no Phase 14 even on PASS; no PC3 modification after seeing the result; no corrective run. On failure, preserve the run and return the evidence |
| D31-22 | Authorization | Scored execution authorized; this ruling is frozen with the protocol |

## Pre-declared scoring mappings (frozen before execution)

These resolve, in advance, the judgement calls the protocol would otherwise leave to the evaluator.

| Id | Mapping |
|---|---|
| M-1 | **Accepted conditions (entry-level)** stay as frozen in D25-P6: CX-LT1-1 `RANGE` or `TRENDING_RANGE`; CX-TE1-1 `TRENDING_RANGE DOWN` or `RANGE`; CX-LT3-2 `TRENDING_RANGE UP` only |
| M-2 | **OQ-46 interaction, declared in advance:** PC3's approved fallback can classify a directionless trending range as `RANGE`. If that happens on CX-LT3-2, dimension 3 scores MISMATCH with primary class `CANON_MISMATCH`, evidence "PC3 follows the approved OQ-46 correction (D29-14) while the D25-P6 accepted set names TRENDING_RANGE UP". Dimension 3 is **not** one of the four 3/3 hard dimensions (D31-4), so this cannot by itself fail the run; it is reported and counts as a concern |
| M-3 | **Hour-level model family:** the journal rows are hourly CBR entries, so the source supports only "a CBR1H setup". Scored as: an eligible CBR1H candidate exists (any variant). The MTF labels TRR CT / TRR PT / IFS are recorded, not scored as implementation subtypes (D31-11) |
| M-4 | **Hour-level condition:** journal `Trending` maps to engine condition ∈ {`TRENDING_RANGE`, `RANGE`} (the trending-range family, including the approved OQ-46 fallback). Journal `Volume` describes volume, not the range condition, and is **NOT_SCORED** |
| M-5 | **Hour-level timing bucket:** journal CB hour 37 maps to the 30-45 minute bucket; 52 maps to the 45-60 minute bucket. Measured on the eligible candidate's 5s shift minute-in-hour |
| M-6 | **Hour-level direction:** journal Buy/Sell must equal the eligible candidate's direction (D31-9) |
| M-7 | **Structural-event existence (A):** for entry-level positives, "the expected structural event exists" means an eligible candidate whose 5s shift is D25-P3 equivalent to the course entry (same direction, same 15m candle, \|Δt\| ≤ 3 min) exists anywhere in the eligible set for either variant |

## Disclosure

Earlier reconciliation work (D26-D28) measured component diagnostics on CX-LT1-1, CX-TE1-1 and CX-LT3-2 — including
that a re-anchored trigger reproduces the three course entries and that the OQ-46 fallback reclassifies CX-LT3-2's hour.
Those diagnostics informed the approved PC3 corrections. This run is nonetheless the **first end-to-end scored
execution** of PC3 under a protocol and acceptance rules frozen beforehand, and no PC3 rule, parameter or mapping was
changed after any result of this run was seen.
