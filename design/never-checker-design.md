# Never checker: design

MODE: design. No code was written and no existing file was edited; this file is the only one added.
Branch `quiet-day-stage-a`, HEAD `65fee7c`. Written 2026-10-12.

**Frozen predictions.** Every predicted verdict below was written before any checker exists. The predictions
come from reading the three day-1 mornings act by act (§2). No check was run to produce them. The one prior
artefact that scores these same mornings is the hand-made Never sheet in
`Prototypes/llm-morning/reports/trip_v11.md` §7. It is shown next to each prediction as **H**
(present = fail, absent = pass), so a reviewer can see where this design reads an item differently.

## 1. What the checker reads

- **The trace.** `Prototypes/llm-morning/runs/<version>/daniel_ate_it-seed<k>.transcript.json`. The checker
  reads its `day1` object, or the top level for single-morning transcripts (v11–v15 have no `day1` key).
  The target morning is the discovery morning, which is day 1.
- **Fields used** (all verified in §7):
  - Day level: `culprit` and `final_state.<person>.grudges.<target>.{strength, events[[minute, text, kind]]}`.
  - Turn level: `turns[].minute`, `turns[].rooms`, `turns[].acts[]`.
  - Act level: `who`, `room`, `option`, `words`, `mode` (`model` / `routine` / `fallback`), `new`, `came_of_it`,
    `moved_to`, `audience`, `said_at`, `suspects`, `lull`.
- **Speech kinds** come from the existing `talk.act_of(option)[0]` (`Prototypes/llm-morning/talk.py:16`). For
  example `reassure_all` and `reassure_daniel` are both `reassure`, and `ask_who` is `ask`. The speech kinds
  are `talk.SPEECH` (`talk.py:8`).
- **Not in the trace today.** Per-act `feeling`, `reason` and grudge changes appear only in the rendered
  story `runs/<v>/daniel_ate_it-seed<k>.md` as prose ("Feeling: *calm*. Reason: “…”", "grudge against Leo
  fell to 0/3"). The turn record builds `record["grudges"]` (`world.py:993`, `world.py:1350`), but it is not
  written to the transcript turn, which has only `minute`, `rooms` and `acts` (`world.py:1360`). The checker
  must not parse the `.md`. Items that need these values are marked NEEDS-NEW-FIELD.

## 2. The replays used

Day 1 is byte-identical across versions from v11 on (sha256 of `day1.turns`, §7 command 2). That leaves
three distinct current discovery mornings. The latest copy of each is named:

| Name | File | Identical day 1 in | sha256 (first 10) |
|---|---|---|---|
| **S1** | `Prototypes/llm-morning/runs/v18/daniel_ate_it-seed1.transcript.json` | v11 v12 v13 v15 v16 v17 v18 | `cf9f5f36c4` |
| **S2** | `Prototypes/llm-morning/runs/v22/daniel_ate_it-seed2.transcript.json` | v11 v12 v13 v15 v16 v17 v18 v19 v20 v21 v22 | `db5de15235` |
| **S3** | `Prototypes/llm-morning/runs/v20/daniel_ate_it-seed3.transcript.json` | v11 v12 v13 v15 v16 v17 v18 v19 v20 | `36b4a4a0ff` |

Their caches are `Prototypes/llm-morning/cache/<v>/gemini-3.5-flash-lite-daniel_ate_it-seed<k>.json`.

**Not predicted.** These are older code with a different day 1, and some lack fields (v2 has no
`final_state`; v6–v10 have no `trip`):
- v2, v3, v6, v7, v9, v10 seeds 1–3, and v4 seeds 1–5 (§7 command 2);
- `runs/v5/daniel_ate_it-gemma-seed1..5` (Gemma, `cache/v5`);
- the `daniel_ate_it_leo_heard` variant (v6–v8).

The S1–S3 set is a design choice; predictions for the older mornings can be added if wanted.

**What the three mornings are** (read from §7 command 4's act listings):
- **S1.** Elena asks at 00. Daniel confesses at 03. Leo and Elena reassure him at 06. Leo and Mara eat at 21,
  and the shelf is empty. Trip argument 24–42. Then near-total silence 45–87.
- **S2.**
  - 00–15: four denials, Daniel accuses Leo three times, Mara and Leo start searching at 09, Elena
    reassures everyone again and again.
  - Silence 18–27, then Daniel confesses at 33.
  - Trip argument 36–51. Mara eats at 54. Silence 57–87, except one reassurance at 75.
- **S3.**
  - Daniel denies from 00 to 33. Mara keeps asking. Leo searches 15–18 and finds nothing.
  - Silence 36–51. Trip talk 63–69.
  - Mara and Elena search at 72–75 and find nothing. Daniel then searches at 75–78.
  - No confession.

## 3. The 13 Never items

Item text is quoted exactly from `Docs/understanding/target-morning.md:18-36`. Wrapped lines are joined with
one space. "Fail" means the item appears.

| # | Item (exact) | Class | Reads | Assertion (one sentence) | S1 | S2 | S3 |
|---|---|---|---|---|---|---|---|
| N1 | "A person acts as if they do not know what they did. Daniel does not try to "find out" what happened to the can he ate." | JUDGMENT-ONLY | screen only: `culprit`, `who`, `option`, `words` | No honest mechanical check. The culprit cannot be offered `ask_who` (`world.py:331`, `:545`), so the only find-out acts left are `search`/`keep_searching` and question words. The same act is a target-morning *Possible* when it is done to look innocent ("Daniel offers to search, to look innocent"). Only the reason (not in the trace) separates the two, and reading the reason is judgment. The screen lists the culprit's search acts and "?" lines for a reader. | **pass**. Confesses at 03; no search, no question. H: absent. | **pass**. Screen hit: 03 `accuse_leo` "Are you sure you didn't grab it?". It deflects (Possible "lies, deflects"), not a find-out. H: absent. | **pass**. Screen hit: 75 `search` while denying all morning. A culprit's search is covering (Possible). H: absent. |
| N2 | "A person checks something they just watched someone else check, for the same reason (three people counting the shelf Elena just counted)." | CHECKABLE-NOW | `option`, `room`, `minute`, `audience`, `came_of_it`, `culprit` | Fail if someone other than the culprit chooses `search` in a room within 3 turns (9 minutes) after another person's act in that room whose `came_of_it` is "went through the room and found nothing." and whose `audience` included them. | **pass**. No search all morning. H: absent. | **pass**. Mara and Leo both *start* at 09 and neither finishes (both choose something else at 12). No finished check is followed by a search. H: **present** (counts joining a search that is under way). | **pass**. Elena joins Mara's search at 72 (under way, not finished). At 75 Daniel searches right after both finish, but he is the culprit and his reason is not "the same reason". Mara's 72 search comes 54 min after Leo's 18 finish. H: **present** (counts 72 and 75). |
| N3 | "A person keeps a fact from their own earlier act as if it never happened (Elena counting again because her first count "does not count")." | CHECKABLE-NOW | `who`, `option`, `room`, `came_of_it`, `audience` | Fail if a person chooses any of the following: `search` in a room where their own earlier act's `came_of_it` was "went through the room and found nothing."; `deny` after their own `confess`; or `ask_who` after being in the `audience` of a `confess`. | **pass**. No search; Daniel never denies after 03; nobody asks after 03. H: absent. | **pass**. No finished own search is repeated; after the 33 confession nobody asks or denies. H: absent. | **pass**. Mara's 06 search was left unfinished (`ask_who` at 09), so her 72 search repeats no finished check. H: absent. |
| N4 | "A person sits with someone who is busy searching, walking or leaving." | CHECKABLE-NOW | `option`, `who`, `came_of_it`, `moved_to`, `minute` | Fail if a `sit_<q>` act happens while q is searching or leaving. Searching: q's latest act is `search`, or `keep_searching` whose `came_of_it` is not "…found nothing.". Leaving: q has an act with non-null `moved_to` earlier in the same turn. | **pass**. No `sit_*` act (none offered toward busy people either: `world.py:580`). H: absent. | **pass**. No `sit_*`. H: absent. | **pass**. No `sit_*`. H: absent. |
| N5 | "A person stops comforting someone because another family member joins them, instead of staying or joining." | JUDGMENT-ONLY | screen only: `option` (`sit_*`, `reassure_*`), `who`, `minute` | No honest mechanical check. In this prototype no rule ends a sitting when a third person joins; whether to keep sitting is the model's choice each turn. So the item's "because" lives only in the model's reason. The sequence "X sits with Y, Z sits with Y, X does something else next" also fits a real hand-over or a new need, such as hunger. The screen lists such sequences; with no `sit_*` act it returns nothing. | **pass**. No `sit_*`, screen empty. H: absent. | **pass**. No `sit_*`. H: absent. | **pass**. No `sit_*`. H: absent. |
| N6 | "After the missing can is discovered, nobody says anything." | CHECKABLE-NOW | `minute`, `words`; discovery = `convo_log[0]` "the count came up short" at minute 0 | Fail if no act at minute 0 has non-null `words`. | **pass**. 00 Elena `ask_who`, Mara `deny`. H: absent. | **pass**. 00 Elena asks, then three denials. H: absent. | **pass**. 00 Mara and Elena `ask_who`, Daniel `deny`. H: absent. |
| N7 | "A person pictures a room as empty when they left people in it." | JUDGMENT-ONLY | screen only: `moved_to`, `rooms`, `words` | No honest mechanical check. The code never describes another room to a person: a prompt names only the people in the person's own room (`world.py:1156-1161`). So a pictured empty room can arise only in the model's words or reason, and reading whether words "picture a room as empty" is judgment ("my stomach is empty" and "empty shelves" are not rooms). The screen lists words containing "empty", "nobody" or "no one" from a person who has moved. | **pass**. Nobody moves (all four in the kitchen 00–87). H: absent. | **pass**. Nobody moves. H: absent. | **pass**. Nobody moves. H: absent. |
| N8 | "An important social choice (who to comfort, who to suspect) is settled by chance alone when the people involved differ in ways that should matter." | CHECKABLE-NOW (code side) | `option`, `mode`, `suspects` | Fail if any act whose `option` names a person (`reassure_*`, `accuse_*`, `sit_*`, `back_*`, `object_<person>`, `aside_*`) or whose `suspects` names someone has `mode` other than `model`, because then the code, not the person, chose. | **pass**. All 65 non-model acts are `routine` `silent`. H: absent. | **pass**. All 67 non-model acts are `routine` `silent`. H: absent. | **pass**. Non-model acts: 72 `routine` `silent`, 3 `routine` `keep_searching`; none names a person. H: absent. |
| N9 | "Long stretches where nothing anyone does shows how they feel. Changed 29 Sep 2026: silence is normal; frozen silence is not." | NEEDS-NEW-FIELD | needs `turns[].showing` (ids whose feeling shows that turn: `world.py:512` `shown`, `outward(feeling)` within `FEELING_SHOWS_FOR_TURNS = 3`, `world.py:77`); or per-act `feeling` plus `feeling_shows` | Fail if at least 5 turns in a row (15 minutes) meet both conditions: (a) every act is `silent`, or keeps sitting with the same person, with a silent `lull` counted as silent; (b) `showing` is empty. This is gist_words_v10.md §4's reading of the new wording, unchanged. | **fail**. All-silent 45–63 (7 turns) and 69–87 (7 turns), with Elena's silent model act at 75 inside. Even if a feeling showed at 42–45, 51–63 is still 5 turns. H: **present** (45–63, 69–87). | **fail**. 57–72 (6 turns) all silent; Mara's 54 `eat` breaks before it. Condition (b) rests on H's reading that no feeling showed: if Mara's 54 feeling showed through 60, only 63–72 (4 turns) would remain, a pass. H: **present** (57–72). | **fail**. 36–51 (6 turns) all routine silence. Condition (b) rests on H: if Daniel's 33 feeling showed, only 42–51 (4 turns) would remain, a pass. H: **present** (36–51). |
| N10 | "Everyone speaks at once and nobody answers the line before theirs." | JUDGMENT-ONLY | screen only: turns with ≥ 3 acts with `words` in one room | No honest mechanical check. The "at once" half cannot happen: each person decides after the previous act in the room is applied (`world.py:1398-1404`), and `decided_at` equals `said_at` with a strictly rising sequence (§7 command 1). A check on those fields would pass every run by construction. "Nobody answers the line before" is about what the lines mean. The screen lists turns with 3 or more speakers for reading. | **pass**. 24–39 have 4 speakers each; each line answers the one before ("Leo is right…", "Daniel is right, he should go…"). H: absent. | **pass**. 36–48: the accusation answers the confession, the offers and objections answer each other. H: absent. | **pass**. 66: Mara objects, Leo answers her, Daniel answers Leo, Elena answers all. H: absent. |
| N11 | "A person repeats the same kind of line many turns in a row with no effect." | CHECKABLE-NOW | `who`, `option`, `mode`, `new`, `said_at` | Fail if one person has 3 or more consecutive model-decided acts of the same speech kind and every one has `new` = false. Speech kind is `talk.act_of`; routine acts are skipped; any other model act, `silent` included, breaks the run. | **pass**. Longest same-kind runs: three `object` acts each for Elena (24, 27, 30), Leo (33, 36, 39) and Mara (33, 36, 39). Each run has a `new` = true. H: absent (borderline 1). | **fail**. Elena `reassure` at 03, 06, 12, 30, all `new` = false. H: **present** (same run). | **fail**. Daniel `deny` at 00, 03, 06, 18, 21, 33, all false. Mara `ask` at 09, 21, 24, 54, all false. H: **present** (same runs). |
| N12 | "Someone who was wronged forgives within minutes, with no lasting cost." | NEEDS-NEW-FIELD | needs (1) `turns[].grudges`: the per-turn grudge changes the code already builds (`world.py:993`), written to the transcript; (2) a `wrong` subtype on grudge events: `false_accusation`, `lied_to`, `ate_in_front`. Today all three are kind `event`, told apart only by their text | Fail if a grudge holding a `false_accusation` or `lied_to` event rose to 1 or more and is at 0 before the morning ends (minute 87). | **pass**. The only grudges come from eating in front of someone (21). Those fall at 36, but `ate_in_front` is not counted (see §4). Mara's anger at Leo stays 3/3. H: absent. | **fail**. Elena's grudge against Daniel (`lied_to`: "admitted taking it at minute 33, after denying it to you at minute 06") rises at 33 and is 0 at 48, by the fall rule `FALL_EVERY = 15` (`world.py:82`, `:247`). Leo's (`false_accusation`) and Mara's (`lied_to`) stay at 3. H: absent (borderline 2: the earlier reading did not count a lie). | **pass**. No grudges at all (Daniel never confesses, so no lie is known). H: absent. |
| N13 | "A person mentions objects or places the house does not have." | JUDGMENT-ONLY | screen only: `words`, against `data.HOUSE_THINGS` (`data.py:135`) | No honest mechanical check. `words` is free text, so no closed list can decide it: plurals ("shelves"), idioms ("tearing the place apart") and times ("in the dark") must be read. The screen lists nouns not in `HOUSE_THINGS`. | **pass**. "make that crossing in the dark" (27) names a time, not a place. H: absent. | **pass**. Lines name the can, shelf, street, neighbour's house. H: absent. | **pass**. H: absent. |

**Predicted totals (fails).**

| Replay | This design | H (trip_v11.md §7) | Difference |
|---|---|---|---|
| S1 | 1 (N9) | 1 (N9) | none |
| S2 | 3 (N9, N11, N12) | 3 (N2, N9, N11) | N2 pass here, N12 fail here |
| S3 | 2 (N9, N11) | 3 (N2, N9, N11) | N2 pass here |

## 4. Choices argued against first (CLAUDE.md, "Judging changes")

- **N2: joining a search under way is not the Never.**
  - *Against:* the earlier reading (witness_v6.md, used in trip_v11.md) counts "starts searching … while
    another person is searching it".
  - *For this design:* the item says "just watched someone else check". A real family that sees one person
    start going through the kitchen often helps ("I'll do the counter"). That is not the target's example of
    re-counting a shelf already counted.
  - **Open for review:** this is the reason S2 and S3 differ from H.
- **N2: the culprit is excluded.** The item requires "the same reason". Daniel searching for a can he ate is
  never looking for it; target-morning lists exactly this as *Possible*. His searches belong to N1's reading.
- **N11: the effect is `new`, a three-act threshold.**
  - *Against:* a mother saying "we'll get through this" three times in an hour is human.
  - *For:* the item says "with no effect", and the code's own `new` already decides whether a line brought
    something new.
  - The code itself stops offering a speech kind after 3 turns in a row (`world.py:613`), so 3 is the
    longest run the code allows without a gap.
  - The earlier reading also asked whether the addressee changed. That is a judgment, not used here.
- **N12: only wrongs aimed at the person count, and the cost must last the morning.**
  - *Against:* eating a portion in front of a hungry family is also a wrong.
  - *For:* a mother letting go of her son eating when starving, within 15 minutes, is what real families
    do. Being lied to, or falsely accused, and holding nothing an hour later is not.
  - Counting `lied_to` is new compared with the earlier reading. It is why S2 differs from H.
  - The fall rule (`FALL_EVERY = 15`) makes every strength-1 grudge reach 0 15 minutes later unless the
    person keeps naming their anger. So a fail here points at a code rule, not at the model.
- **N8: only the code side.**
  - *Against:* the model's own choice could still ignore who the people are.
  - That part is the "Should vary" question (§5, personality), not a per-run fact. The per-run fact the code
    owns is whether anything but the person chose a target.
  - Turn order "drawn by the seed among equals" (`world.py:1345`) decides who speaks first, not whom to
    comfort or suspect.

## 5. The 4 "Should vary" items

A seed set is 3 or more `daniel_ate_it` mornings run on the same code. With only 3 seeds, "varies" means at
least 2 distinct values. Varying *by personality* needs runs with changed profiles, which no cached replay
has.

| Item (exact) | Measure (compared across seeds) | Threshold | Predicted on S1–S3 |
|---|---|---|---|
| "What Daniel does: silence, confession, or blaming someone." | Per seed, the culprit's class from his acts: **confession** (any `confess`), **blame** (any `accuse_<other>`), **silence/denial** (neither). A seed can be blame-then-confession. | ≥ 2 distinct classes across the seed set | S1 confession (03); S2 blame then confession (accuse_leo 03–12, confess 33); S3 silence/denial. 3 classes: **varies**. |
| "Who suspects whom, and whether anyone suspects Daniel at all." | Per seed, the set of (holder → named) pairs from `suspects` in model acts before the culprit's `confess` (all morning if none), plus whether any non-culprit names the culprit in that window. | the pair sets are not all identical, and "anyone suspects Daniel" is not the same answer in every seed | S1 window 00–03: nobody names anyone. S2 00–30: Daniel names Leo; nobody names Daniel. S3: nobody names anyone. Pair sets differ (S2), but "anyone suspects Daniel before a confession" is **no** in all three. **Partly varies** (whom: yes; Daniel at all: no). |
| "Whether and when the food is shared, and who decides." | Per seed, the first `eat`, `share` or `give` act: (minute, who, option), or none. | not identical across the seed set | S1 (21, Leo, `eat`); S2 (54, Mara, `eat`); S3 none. **Varies**. Nobody ever `share`s, so "who decides" never arises. |
| "Who comforts whom, for a reason the story can name." | Per seed, the set of (comforter → target) pairs from `reassure_<person>` and `sit_<person>` acts (`reassure_all` → everyone present). | pair sets not all identical | S1 {Leo→Daniel, Daniel→Leo, Elena→Daniel, Daniel→Mara, Daniel→all}; S2 {Elena→all, Daniel→all, Daniel→Elena}; S3 {Daniel→all}. **Varies**. The clause "for a reason the story can name" is **JUDGMENT-ONLY**: it needs the reason (not in the trace) read by a person. |

The closing test of target-morning.md ("If runs differ only by chance and not by who the people are, it is
noise") cannot be checked on any cached replay. Every one uses the same four profiles. It needs paired runs
with one profile changed, and is out of scope here.

## 6. The 10 "Possible" items: allowed set only, no checks

Copied from `target-morning.md:40-52`. A checker must not fail a run for any of these, and must not require
them.

1. Elena asks aloud who took the can.
2. Daniel lies, deflects or stays quiet, and shows it: avoids looking at people, avoids Elena, avoids the
   kitchen or the food.
3. Daniel offers to search, to look innocent rather than to find anything. (This is why N1 is judgment and
   N2 excludes the culprit.)
4. Leo gets defensive ("don't look at me") or suspects Daniel.
5. Mara is scared or upset; she may defend someone, cry, or ask them to stop.
6. Elena tries to hold the family together ("we share what's left, nobody eats alone").
7. Hunger is handled by a rule or an arrangement (Elena decides when and how portions are shared), not by
   everyone standing still.
8. Someone questions Daniel directly, and that becomes a turning point.
9. Daniel confesses (more likely if honest and weighed down by guilt).
10. Daniel blames Leo or someone else (more likely if proud and afraid).

**Out of scope (noted, not designed).** The C# morning (`Assets/_Project/Tests/EditMode/MorningTests.cs`,
`Docs/slices/S1/traces/morning-*.md`) has a different trace, and it has count and sit acts that the
prototype day 1 never shows.
- `Docs/slices/S1/traces/morning-daniel_ate_it.md:8` and `:12`: Daniel counts and searches "because needing
  to know what happened". That is an N1 reading.
- `:15` and `:17`: Elena and Mara count at 09 after Daniel and Leo counted at 01. That is N2.
- `:20`: Elena counts again at 12 after her own count at 09. That is N3.
- None of `MorningTests.cs`'s asserts reads a Never item. Its invariants are the closest thing:
  `NobodyLearnsAnythingFromARoomTheyAreNotIn` (line 213), `NobodyEverEatsAndThisRecordsWhyNot` (line 60).
- Existing mechanical *screens*, not pass/fail checkers: `Prototypes/llm-morning/runs/v16/scoring/scripts/analyze.py`
  (`analyze.py never`, used in trip_v11.md §7) and `never_v9.py` (printed in `reports/lull_v9.md`).

## 7. Commands run to verify each named field, with output

All from `Prototypes/llm-morning/` unless noted. Read-only.

**1. Fields of the three named replays** (day-1 keys, act keys, absent fields, `mode`, `new`, search
`came_of_it`, sit/go/aside acts, minute-0 lines, `decided_at`/`said_at` order, grudge event kinds).
```
$ python -c "import json,collections ... for s,p in R.items(): ..."   (one-liner; prints the lines below)
[1] runs/v18/daniel_ate_it-seed1.transcript.json
  day1 keys: ['convo_log', 'culprit', 'final_rooms', 'final_state', 'scenario', 'seed', 'trip', 'turns']
  culprit: daniel | turn keys: ['acts', 'minute', 'rooms'] | minutes 0 .. 87
  act keys: ['angry_at', 'audience', 'came_of_it', 'decided_at', 'inner', 'lull', 'minute', 'mode', 'moved_to', 'new', 'new_why', 'option', 'room', 'said_at', 'suspects', 'trip_moment', 'who', 'words']
  feeling/reason/grudges in act keys: []
  mode values: {'model': 55, 'routine': 65}
  options chosen in non-model modes: {('routine', 'silent'): 65}
  new values: {'None': 81, 'True': 20, 'False': 19}
  search came_of_it: []
  sit_/go_/aside_ acts: [] | moved_to non-null: 0
  minute-0 acts with words: [('elena', 'ask_who'), ('mara', 'deny')]
  decided_at==said_at all: True | seq strictly increasing per turn: True
  grudge event kinds: ['angry', 'event'] | suspicion e.g. ['daniel', 3]
[2] runs/v22/daniel_ate_it-seed2.transcript.json
  (same day1, turn and act keys)
  feeling/reason/grudges in act keys: []
  mode values: {'model': 53, 'routine': 67}
  options chosen in non-model modes: {('routine', 'silent'): 67}
  new values: {'True': 22, 'False': 19, 'None': 79}
  search came_of_it: ['started going through the room.']
  sit_/go_/aside_ acts: [] | moved_to non-null: 0
  minute-0 acts with words: [('elena', 'ask_who'), ('mara', 'deny'), ('daniel', 'deny'), ('leo', 'deny')]
  decided_at==said_at all: True | seq strictly increasing per turn: True
  grudge event kinds: ['angry', 'event'] | suspicion e.g. ['daniel', 3]
[3] runs/v20/daniel_ate_it-seed3.transcript.json
  (same day1, turn and act keys)
  feeling/reason/grudges in act keys: []
  mode values: {'model': 45, 'routine': 75}
  options chosen in non-model modes: {('routine', 'silent'): 72, ('routine', 'keep_searching'): 3}
  new values: {'True': 9, 'False': 14, 'None': 97}
  search came_of_it: ['started going through the room.', 'went through the room and found nothing.']
  sit_/go_/aside_ acts: [] | moved_to non-null: 0
  minute-0 acts with words: [('mara', 'ask_who'), ('elena', 'ask_who'), ('daniel', 'deny')]
  decided_at==said_at all: True | seq strictly increasing per turn: True
  grudge event kinds: [] | suspicion e.g. [None, 0]
```

**2. Which day-1 mornings are distinct** (sha256 of `day1.turns`, or the top-level `turns`).
```
$ python -c "import json,hashlib,glob,os ... glob('runs/v*/daniel_ate_it-seed{s}.transcript.json') ..."
seed 1 0dccca5e2d v10
seed 1 cf9f5f36c4 v11 v12 v13 v15 v16 v17 v18
seed 1 f012094802 v2
seed 1 662700d0eb v3
seed 1 54a460d4f1 v4
seed 1 d420dc1987 v6
seed 1 a2fcf6d4cd v7
seed 1 c8069e3c79 v9
seed 2 21e85a6810 v10
seed 2 db5de15235 v11 v12 v13 v15 v16 v17 v18 v19 v20 v21 v22
seed 2 6e5c707ec8 v2
seed 2 cbb85062f5 v3
seed 2 825a10ac88 v4
seed 2 983dbbda0f v6
seed 2 2572b8fb67 v7
seed 2 bf18131111 v9
seed 3 5f7c6e835a v10
seed 3 36b4a4a0ff v11 v12 v13 v15 v16 v17 v18 v19 v20
seed 3 63063a26e2 v2
seed 3 0f730604b4 v3
seed 3 6a0585f890 v4
seed 3 5a2cc2b96e v6
seed 3 42c37b29f9 v7
seed 3 20be9c32bc v9
```

**3. Where per-act feeling and reason exist today** (only in nights and night minds, not day-1 acts):
```
$ python -c "... walk(transcript) and print paths of keys 'feeling'/'reason' ..." | sort | uniq -c
      1 .mind1.daniel.feeling   (… elena, leo, mara; mind2 the same)
      1 .night.decisions[].feeling
      1 .night.decisions[].reason
      1 .night2.decisions[].feeling
      1 .night2.decisions[].reason
$ grep -c "Feeling: \*" runs/v18/daniel_ate_it-seed1.md     -> 138
$ grep -c "Reason: “" runs/v18/daniel_ate_it-seed1.md       -> 130
$ grep -o "grudge against [A-Za-z]* \(rose to\|fell to\) [0-9]/3" runs/v22/daniel_ate_it-seed2.md | head -3
grudge against Leo rose to 1/3
grudge against Daniel rose to 2/3
grudge against Leo rose to 2/3
```

**4. Reading the three mornings act by act** (the basis of every prediction; output, 150 and 167 lines, not
reproduced. It prints per turn: minute, rooms, and for each non-routine act `who option mode new | words |
came_of_it | suspects angry_at moved_to`; then final grudges and `convo_log`). Final grudge strengths and
events per seed:
```
$ python -c "... for p,st in final_state.items(): for q,g in st['grudges'].items(): print(...)"
1 daniel -> leo 0 [[21, 'Leo ate a portion in front of you at minute 21, while you were hungry', 'event']]
1 elena -> leo 0 [[21, 'Leo ate a portion in front of you at minute 21, while you were hungry', 'event']]
1 mara -> leo 3 [[21, '... ate a portion in front of you ...', 'event'], [21, 'you were angry with Leo', 'angry'], ...]
2 daniel -> leo 0 [[3, 'you were angry with Leo', 'angry'], [6, ...], [9, ...], [12, ...]]
2 elena -> daniel 0 [[33, 'Daniel admitted taking it at minute 33, after denying it to you at minute 06', 'event']]
2 leo -> daniel 3 [[3, 'Daniel accused you of taking the can at minute 03, and you had not', 'event'], ...]
2 mara -> daniel 3 [[33, 'Daniel admitted taking it at minute 33, after denying it to you at minute 06', 'event'], ...]
(seed 3: no grudges)
```
Day-1 grudge changes from the rendered stories (the value N12 needs and the transcript lacks):
```
$ sed -n '/^## The morning/,/^## What was said/p' runs/<v>/daniel_ate_it-seed<k>.md | grep -o '...grudge ... (fell|rose) ...'
seed 1 day 1: min 36 Elena grudge against Leo fell to 0/3; grudge against Mara fell to 0/3
              min 36 Daniel grudge against Leo fell to 0/3; grudge against Mara fell to 0/3
seed 2 day 1: min 03 Daniel grudge against Leo rose to 1/3 … min 09 rose to 3/3 … 33 fell to 2/3 … 48 fell to 1/3 … 66 fell to 0/3
              min 06 Leo grudge against Daniel rose to 2/3
              min 36 Mara grudge against Daniel rose to 2/3; min 39 rose to 3/3
              min 48 Elena grudge against Daniel fell to 0/3
              min 75 Elena grudge against Mara fell to 0/3
```

**5. Code lines cited for the classes** (`grep -n`, world.py unless named):
```
82:FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one step this often
247:    def may_fall(self, minute):
331:        self.knows_culprit = culprit if pid == culprit else None
545:            if not p.knows_culprit:
580:                if q.activity["kind"] in ("searching", "walking"):
593:        settled = p.confessed or (p.knows_culprit and p.knows_culprit != p.id)
613:        if kind in SPEECH and n >= 3:
1292:        self.transcript["final_state"] = {
1360:        tturn = {"minute": minute, "rooms": {r: list(v) for r, v in self.present.items()}, "acts": []}
1382:                     "decided_at": [minute, d["seq"]], "said_at": [minute, d["seq"]],
993:        record["grudges"].append((minute, holder.id, against.id, holder.grudges[against.id].strength, story))
1350:                  "grudges": []}
512:    def shown(self, q, t):
513-        return outward(q.feeling) and q.feeling_until >= t
world.py:77:FEELING_SHOWS_FOR_TURNS = 3
data.py:135:HOUSE_THINGS = (
talk.py:8:SPEECH = ("ask", "deny", "accuse", "confess", "reassure", "say",
talk.py:16:def act_of(option):
```
Prompt room lines (`world.py:1156-1161`, read with Read): "- Nobody else is here." or
"- {q.name} is here, {q.activity['label']}." for the person's own room only. Turn loop (`world.py:1393-1404`,
read): `decide` is called for the next person after the previous act is applied.

**6. Existing screens and the target folder**
```
$ git ls-files | grep -i "analyze.py\|never_v9\|w8.py"
Prototypes/llm-morning/runs/v16/scoring/scripts/analyze.py
$ ls design
ls: cannot access 'design': No such file or directory      (created for this file)
```

**7. C# trace lines cited in §6** (`grep -n` on `Docs/slices/S1/traces/morning-daniel_ate_it.md`):
```
8:- **01** Daniel, in the kitchen: opens the pantry and counts because needing to know what happened (0.98). Found 2 portions left
12:- **04** Daniel, in the kitchen: goes through the room because needing to know what happened (0.98). Went through the room
15:- **09** Elena, in the kitchen: opens the pantry and counts because it has to last (0.85). Found 2 portions left
17:- **09** Mara, in the kitchen: opens the pantry and counts because needing to know what happened (0.59). Found 2 portions left
20:- **12** Elena, in the kitchen: opens the pantry and counts because it has to last (0.85). Thought again, and carried on
```

## 8. Counts

- **CHECKABLE-NOW: 6** (N2, N3, N4, N6, N8, N11)
- **NEEDS-NEW-FIELD: 2** (N9: `turns[].showing` or per-act `feeling` + `feeling_shows`; N12: `turns[].grudges` and a `wrong` subtype on grudge events)
- **JUDGMENT-ONLY: 5** (N1, N5, N7, N10, N13)
