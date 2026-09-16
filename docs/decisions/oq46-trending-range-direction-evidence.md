# OQ-46 Evidence Review: Direction in a Contracting Range

**Doc:** CBR-EVD-046 · **Version:** v1.0 · **Date:** 2026-09-16 · **Ruling:** D28 §16 (from D27) · **Status:** FOR OWNER DECISION
PC2 frozen; no trend classifier invented (D27 §16); not decided from CX-LT3-2 alone. Quotes verified mechanically.

---

## 1. The problem

`condition._direction` returns `UP` only when the last two MTF highs **and** the last two lows both rise (mirror for
`DOWN`), else `NONE`. `M1H-COND-03` then blocks every candidate when the condition is `TRENDING_RANGE` with
`direction = NONE`. On CX-LT3-2 the highs descend (4027.53 → 4009.29) while the lows ascend (3992.47 → 3994.55) — a
contracting range — so direction is `NONE` and the hour is blocked.

## 2. Evidence

| Id | Level | Source · time | Verbatim | Reading |
|---|---|---|---|---|
| NEW | L1 | V1H-what_direction_condition · 00:01:26 | "we identify a range by it **correcting over 50 of its previous move on average**" | the **condition** comes from the correction ratio |
| NEW | L1 | same · 00:01:58 | "this is more of a **trending range because we're making high highs and high lows**" | a trending range **requires** the directional swing sequence |
| NEW | L1 | same · 00:03:04 | "this is where you're still kind of correcting over some of the first move **but you're making clear** [higher lows, higher highs]" | both conditions must hold together |
| E1H-007 / E1H-008 | L1 | V1H-defining_mtf_ranges · 00:02:26-00:04:09 | "if you're correcting around you know 50 or more of the previous move … more of a trending range. If you're [correcting less] … more of a trend" | the correction ratio orders range / trending range / trend |
| E1H-046 | L1 | V1H-what_direction_condition · 00:08:33 | "high volume trendy this is just gonna you know ideally don't want to be trading this condition" | the untradeable case is **trendy**, not directionless |

**Finding.** Tom's "trending range" is the conjunction of two properties: corrections of roughly 50% **and** a clear
higher-high / higher-low (or lower-low / lower-high) sequence. He never describes a "trending range with no direction".
In PC2 the two properties are computed separately, and their disagreement produces a state Tom's taxonomy does not
contain, which then blocks the hour.

## 3. Options

| Id | Concept | Machine definition | Evidence | Note |
|---|---|---|---|---|
| **A** | current (last two swing pairs) + block | unchanged | the HH/HL wording | produces a state outside Tom's taxonomy |
| **B** | **fallback to RANGE** when the correction ratio says trending range but no clear direction exists | if `c_med` ∈ trending-range band **and** direction = NONE → classify `RANGE` | both properties must hold for a trending range (00:01:58, 00:03:04); a directionless market with ~50% corrections is a range | no new parameter |
| **C** | dominant displacement | direction = sign of the net move across the window | none found | would be an invented classifier |
| **D** | latest leg | direction = direction of the most recent MTF leg | none found | invented |
| **E** | relationship to the range extreme | direction inferred from where price sits | conflates location with direction | — |
| **F** | breakout direction | direction = side of the range most recently broken | no L1 wording | invented |

Only **A** and **B** are expressible from the course wording; C, D, E and F would each be a new classifier, which D27
§16 forbids.

## 4. Effect on CX-LT3-2 under option B (diagnostic)

If the hour is classified `RANGE` instead of `TRENDING_RANGE`/`NONE`:

- `M1H-COND-01/02` pass (RANGE is tradeable), `M1H-COND-03` becomes inapplicable;
- `M1H-LOC-01` applies: range 3990.09-4027.53, extension extreme 4053.43 → position **1.69**, far beyond the 0.75
  threshold for a sell — **passes**.

So option B removes the hour-level blocker and the location rule is then satisfied on its own terms.

**Caveat the owner should note:** under the frozen Phase 13 accepted set (D25-P6), CX-LT3-2's accepted condition was
`TRENDING_RANGE UP` only, so a `RANGE` classification would still be scored as a condition mismatch in a rerun. That is
a scoring question for the next parity protocol, not an argument for or against B.

## 5. Effect on the other examples (diagnostic)

CX-LT1-1 is classified `RANGE` already and CX-TE1-1 `RANGE` with direction `UP`; neither is affected by option B, since
B only changes hours where the ratio says trending range **and** direction is NONE. Across the 194 stored hours,
hours currently classified `TRENDING_RANGE` with `direction = NONE` are the only ones B reclassifies.

## 6. Conclusion

**Recommend option B.** It is the only reading that follows Tom's own definition ("a trending range because we're
making higher highs and higher lows") without inventing a classifier: if the directional sequence is absent, the market
is a range, not a directionless trending range. It introduces no parameter and removes a state the taxonomy does not
contain.

**Classification if adopted: CANON_CORRECTION** (condition taxonomy), affecting `M1H-COND-03`'s applicability rather
than deleting the rule: `TRENDING_RANGE` still requires a direction, but a hour that fails that test is reclassified
rather than blocked.

**Not resolved here:** whether the swing-pair test is the right *direction* test at all (OQ-01/OQ-02 adjacent). B makes
the failure mode harmless without settling that question.
