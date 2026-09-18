# Phase 13C — journal-hour reconstruction (OQ-49)

**Ruling:** D32 §9-13 · **Status:** DIAGNOSTIC ONLY. No rule was changed, no entry price or stop was inferred, and no outcome column of the journal was read.

## First divergence per case

| Case | Journal | Engine gate | Detail |
|---|---|---|---|
| JM-2025-10-16 | SELL · TRR CT · Trending · CB 37 | **condition** | the hour is classified UNDEFINED (2 MTF legs in the condition window), so no CBR1H setup of any kind can arm; the journal records 'Trending' |
| JM-2025-10-17 | BUY · IFS · Volume · CB 52 | **eligibility** | a same-direction candidate reached the trigger but failed IMPL-REWARD, M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-LOC-01, M1H-OE-01 |
| JM-2025-10-29 | BUY · TRR PT · Trending · CB 37 | **direction** | the engine produced no BUY candidate in the hour (6 candidates, all ['SELL']) |

## MTF model labels (D32 §13)

Tom names five middle-timeframe models — "you have TR CT, R, and you have IFS, and you have FS… those are the five types of middle time frame models" (V1H-mastering_entry_timing… 00:19:52, L1; E1H-010, E1H-011). PC2 and PC3 classify only `RANGE`, `TRENDING_RANGE` (with a direction) and `TREND`/`UNDEFINED` as no-trade. There is no fractal-shift or inverse-fractal-shift condition class in either engine.

| Journal label | Meaning in the course | Status against the implemented model |
|---|---|---|
| TRR PT | trending range, traded pro-trend | in scope: TRENDING_RANGE + M1H-LOC-02 |
| TRR CT | trending range, traded counter-trend | in scope: TRENDING_RANGE + M1H-LOC-03 |
| R | plain range | in scope: RANGE + M1H-LOC-01 |
| IFS | inverse fractal shift: trade the correction back toward 50% of an MTF impulse (E1H-011) | OUT OF SCOPE: no PC2/PC3 condition class exists for FS/IFS |
| FS | fractal shift: continuation at ~50% of an MTF impulse (E1H-011) | OUT OF SCOPE: no PC2/PC3 condition class exists for FS/IFS |

## JM-2025-10-16

Journal row: 2025-10-16 11:41 AM (UTC+11) · SELL · TRR CT · Trending · CB 37 · LLTF (Seconds) · AOI None. Source level L1_FRAME_JOURNAL_TABLE (Tom's own record; no prices, no outcomes read).

Engine hour: condition **UNDEFINED** (direction UP, 2 MTF legs, correction median —), range 4179.69-4216.08, condition window from 2025-10-15 15:00:00+00:00 (TRADABLE, 480 tradable minutes, 0 missing). Hour rules failed: M1H-COND-01, M1H-COND-02.

**First divergence — condition:** the hour is classified UNDEFINED (2 MTF legs in the condition window), so no CBR1H setup of any kind can arm; the journal records 'Trending'

| Candidate | Var | Dir | Decision | Condition | Ext | Activation | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|---|---|---|---|---|
| `0` | A | BUY | 2025-10-16 00:02:15+00:00 | UNDEFINED | DOWN PRE_EXTENSION | None | None | NO_TRIGGER | IMPL-REWARD, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-COND-01, M1H-COND-02, M1H-OE-00-ACTIVE, M1H-OE-01, M1H-OE-04b |
| `0` | A | SELL | 2025-10-16 00:19:00+00:00 | UNDEFINED | UP EXTENSION_ACTIVE | 2025-10-16 00:09:00+00:00 | None | NO_TRIGGER | M1H-COND-01, M1H-COND-02, M1H-OE-01 |
| `1` | A | SELL | 2025-10-16 00:36:10+00:00 | UNDEFINED | UP EXTENSION_ACTIVE | 2025-10-16 00:09:00+00:00 | None | NO_TRIGGER | M1H-COND-01, M1H-COND-02 |
| `2` | A | SELL | 2025-10-16 00:39:45+00:00 | UNDEFINED | UP EXTENSION_ACTIVE | 2025-10-16 00:09:00+00:00 | 2025-10-16 00:41:20+00:00 | REJECTED_AT_TRIGGER | M1H-6A-1-HVCS-INTO-SHIFT, M1H-COND-01, M1H-COND-02 |
| `3` | A | SELL | 2025-10-16 00:50:50+00:00 | UNDEFINED | UP EXTENSION_ACTIVE | 2025-10-16 00:09:00+00:00 | None | NO_TRIGGER | IMPL-REWARD, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-COND-01, M1H-COND-02 |

## JM-2025-10-17

Journal row: 2025-10-17 12:53 PM (UTC+11) · BUY · IFS · Volume · CB 52 · LLTF (Seconds) + LTF (1m) · AOI 1hr, 30m. Source level L1_FRAME_JOURNAL_TABLE (Tom's own record; no prices, no outcomes read).

Engine hour: condition **RANGE** (direction NONE, 6 MTF legs, correction median 0.985), range 4261.51-4379.93, condition window from 2025-10-16 16:00:00+00:00 (TRADABLE, 480 tradable minutes, 0 missing). Hour rules failed: none.

**First divergence — eligibility:** a same-direction candidate reached the trigger but failed IMPL-REWARD, M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-LOC-01, M1H-OE-01

| Candidate | Var | Dir | Decision | Condition | Ext | Activation | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|---|---|---|---|---|
| `0` | A | BUY | 2025-10-17 01:13:30+00:00 | RANGE | DOWN EXTENSION_ACTIVE | 2025-10-17 01:07:00+00:00 | None | NO_TRIGGER | IMPL-REWARD, M1H-LOC-01, M1H-OE-01 |
| `1` | A | BUY | 2025-10-17 01:26:30+00:00 | RANGE | DOWN EXTENSION_ACTIVE | 2025-10-17 01:07:00+00:00 | 2025-10-17 01:30:25+00:00 | REJECTED_AT_TRIGGER | M1H-LOC-01, M1H-OE-01 |
| `2` | A | BUY | 2025-10-17 01:31:40+00:00 | RANGE | DOWN EXTENSION_ACTIVE | 2025-10-17 01:07:00+00:00 | None | NO_TRIGGER | M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-LOC-01, M1H-OE-01 |
| `3` | A | BUY | 2025-10-17 01:38:20+00:00 | RANGE | DOWN EXTENSION_ACTIVE | 2025-10-17 01:07:00+00:00 | 2025-10-17 01:46:35+00:00 | REJECTED_AT_TRIGGER | M1H-LOC-01 |
| `4` | A | BUY | 2025-10-17 01:50:55+00:00 | RANGE | DOWN EXTENSION_ACTIVE | 2025-10-17 01:07:00+00:00 | None | NO_TRIGGER | M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q |

## JM-2025-10-29

Journal row: 2025-10-29 7:14 PM (UTC+11) · BUY · TRR PT · Trending · CB 37 · LLTF (Seconds) · AOI 4h. Source level L1_FRAME_JOURNAL_TABLE (Tom's own record; no prices, no outcomes read).

Engine hour: condition **RANGE** (direction NONE, 3 MTF legs, correction median 0.745), range 3944.07-4001.67, condition window from 2025-10-29 00:00:00+00:00 (TRADABLE, 480 tradable minutes, 0 missing). Hour rules failed: none.

**First divergence — direction:** the engine produced no BUY candidate in the hour (6 candidates, all ['SELL'])

| Candidate | Var | Dir | Decision | Condition | Ext | Activation | Shift | Trigger verdict | Failing rules at trigger |
|---|---|---|---|---|---|---|---|---|---|
| `0` | A | SELL | 2025-10-29 08:09:40+00:00 | RANGE | UP EXTENSION_ACTIVE | 2025-10-29 08:07:00+00:00 | None | NO_TRIGGER | M1H-OE-01, M1H-OE-04b |
| `1` | A | SELL | 2025-10-29 08:19:45+00:00 | RANGE | UP EXTENSION_ACTIVE | 2025-10-29 08:07:00+00:00 | None | NO_TRIGGER | IMPL-REWARD, M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-OE-01, M1H-OE-04b |
| `2` | A | SELL | 2025-10-29 08:23:50+00:00 | RANGE | UP EXTENSION_ACTIVE | 2025-10-29 08:07:00+00:00 | None | NO_TRIGGER | IMPL-REWARD, M1H-OE-01, M1H-OE-02, M1H-OE-04b |
| `3` | A | SELL | 2025-10-29 08:30:25+00:00 | RANGE | UP EXTENSION_ACTIVE | 2025-10-29 08:07:00+00:00 | 2025-10-29 08:33:00+00:00 | REJECTED_AT_TRIGGER | M1H-6A-1-HVCS-INTO-SHIFT, M1H-6A-2-PREV-15M-BROKEN-BY-Q, M1H-6A-3-NEW-EXTREME-IN-Q, M1H-OE-01, M1H-OE-02, M1H-OE-04b |
| `4` | A | SELL | 2025-10-29 08:40:50+00:00 | RANGE | UP EXTENSION_ACTIVE | 2025-10-29 08:07:00+00:00 | 2025-10-29 08:49:55+00:00 | REJECTED_AT_TRIGGER | IMPL-REWARD, M1H-6A-1-HVCS-INTO-SHIFT |
| `5` | A | SELL | 2025-10-29 08:51:30+00:00 | RANGE | UP EXTENSION_ACTIVE | 2025-10-29 08:07:00+00:00 | None | NO_TRIGGER | — |
