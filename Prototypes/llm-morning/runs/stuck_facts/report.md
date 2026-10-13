# Stuck facts: what in the prompt keeps each person on the same act

Mode: investigate. Read-only: no file outside `runs/stuck_facts/` was changed (this report, `reports/stuck_facts.md`, is the
deliverable), no live call was made, and no key was set for any script (each ran under `env -u GEMINI_API_KEY`; the two scripts that replay a
cache, `collect.py` and `collect_v22.py`, assert that the variable is unset, and `state_probe.py` removes it). Paths are from `Prototypes/llm-morning/`.
Scripts and raw outputs are in `runs/stuck_facts/`. No opinions: counts, quotes, and `path:line`.

## Differences from the brief, and what was used

- **The guard is at `world.py:626-629`, not 611-614.** Lines 611-614 hold the `search` option and the start of the `go_<room>` options
  (`opts.append(Option("search", f"search the {room} for the can (takes about six minutes)", ...`). The guard is Q5.
- **"The live answers in cache/talk_probe".** `cache/talk_probe/scene<k>.json` holds the replayed asks and the night asks
  as well (206 entries in scene 1). The live day asks were read from `runs/talk_probe/scene<k>.json` (`asks[]` with
  `source == "live"`, `phase == "day"`), and each was checked against the cache: **72 of 72** prompts are in
  `cache/talk_probe/scene<k>.json` with the same option (`collect.stdout.txt`). Same check for `cache/calm_variants`
  (46 of 46) and `cache/calm_probe` (18 of 18).
- **v22 was replayed with the code it ran on.** The prompts of v22 are not stored per ask, only in `cache/v22` (hash-keyed).
  The replay at HEAD `a24ae82` stops at exit 3 after 100 asks (a replayed prompt missed the cache; `head_replay_check.stdout.txt`),
  because the talk and tell-fix commits changed day-3 prompts. So `collect_v22.py` replays `cache/v22` from a temp copy
  with a `git archive` of `a4edf84`, the commit `runs/v22/plan_frozen.txt` records: exit 1 (as `runs/v22/scoring/replay_max.txt`
  records for the same replay), **498 asks in all, every one answered from the cache**. The replay's day asks equal the
  transcript's model acts, per person and day, in the same order, **for days 3 to 10** (`q1_repetition.stdout.txt`, "check v22 day N",
  8 of 8). Days 3 to 10 were live (`reports/days_v22.md`, section 1); days 1 and 2 came from an older cache and are left out.
- **The asks counted:** day-phase asks only (the prompts that end on "Your options:" with the day's option list; the night
  and night-mind asks have no such block).

| Set | Asks | Where from | Unit |
|---|---|---|---|
| talk_probe | 72 | `runs/talk_probe/scene{1,3,4}.json`, day 3 (24 each) | person, scene |
| calm_variants | 46 | `runs/calm_variants/scene{1,3}.json`, rows with `how == live` | person, scene, version T / O / TO |
| calm_probe | 18 | `runs/calm_probe/scene{1,3}.json` (the 4th version, "P") | person, scene |
| v22 | 342 | replay of `cache/v22`, days 3 to 10 | person, day |
| **all** | **478** | | |

---

## 1. Repetition, measured

**Method** (`q1_repetition.py`, `q1_summary.py`; output `q1_repetition.stdout.txt`, `q1_summary.md`, `q1_units.json`):

- **Unit.** One person's live day asks of one day in one scene (and, for calm_variants, one version), in the order asked.
  The probes' asks are sorted by minute; v22's are in the replay's order.
- **Share of asks taken by the most-chosen option.** Count of the commonest `option` id over the unit's asks. Option
  ids, not kinds: `reassure_all` and `reassure_mara` are two options.
- **Longest run.** The most consecutive asks in the unit with the same `option` id. (The kind-level run, where
  `reassure_*` is one kind, is also computed; it is in `q1_units.json` as `kind_run`.)
- **Pairs sharing 60% of their words.** All pairs of the unit's answers that have words (`silent` has none and is not
  paired). Words: the `say` text lower-cased, split on letters, digits and apostrophes, as a set of distinct words. A pair
  counts when `|A ∩ B| / max(|A|, |B|) >= 0.6`, i.e. at least 60% of each answer's words are in the other. Two other
  readings are in the raw output as well: Jaccard `>= 0.6` and `|A ∩ B| / min(|A|, |B|) >= 0.6`. "Word-for-word equal" is
  the same `say` after lower-casing and trimming.
- **Caveat on the probes.** The probes' units hold 3 to 8 asks. In talk_probe the live asks come in bursts (scene 1: 09:45-09:48,
  11:45-11:51, 16:54-17:00; scene 3: the same to 16:57; scene 4: 09:45-09:48, 11:45-11:51, 14:51-14:57, 17:39), so consecutive asks can be hours
  apart. In calm_variants a unit's three asks are 30 minutes apart.

### v22, days 3 to 10 (342 asks, 32 person-days)

Per person and day: top option, its count over the day's asks (share), longest run, pairs sharing 60% / all pairs.

| person | day 3 | day 4 | day 5 | day 6 | day 7 | day 8 | day 9 | day 10 |
|---|---|---|---|---|---|---|---|---|
| elena | reassure_all 9/10 (90%); run 6; 2/36 | reassure_all 4/9 (44%); run 2; 0/36 | reassure_all 3/8 (38%); run 2; 4/28 | reassure_all 4/9 (44%); run 2; 0/36 | reassure_all 7/8 (88%); run 5; 2/21 | keep_daniel_home 4/12 (33%); run 3; 4/55 | nobody_goes 5/13 (38%); run 2; 3/78 | nobody_goes 3/8 (38%); run 1; 2/28 |
| leo | confront_daniel 6/8 (75%); run 4; 1/15 | confront_daniel 5/9 (56%); run 4; 0/28 | confront_daniel 3/10 (30%); run 1; 2/45 | confront_daniel 5/9 (56%); run 3; 1/21 | confront_daniel 6/9 (67%); run 2; 6/15 | keep_daniel_home 4/12 (33%); run 2; 3/55 | keep_daniel_home 5/13 (38%); run 1; 6/66 | confront_daniel 5/11 (45%); run 2; 3/45 |
| mara | confront_daniel 10/11 (91%); run 7; 36/55 | accuse_daniel 7/11 (64%); run 3; 0/55 | accuse_daniel 10/11 (91%); run 8; 1/55 | confront_daniel 6/11 (55%); run 3; 5/45 | accuse_daniel 7/11 (64%); run 3; 2/55 | accuse_daniel 9/12 (75%); run 7; 3/66 | accuse_daniel 5/10 (50%); run 3; 6/36 | accuse_daniel 7/11 (64%); run 3; 0/55 |
| daniel | reassure_all 7/11 (64%); run 2; 3/55 | reassure_all 4/11 (36%); run 3; 2/55 | still_going 6/11 (55%); run 4; 6/55 | confront_leo 3/11 (27%); run 2; 3/55 | confront_mara 7/14 (50%); run 4; 1/91 | still_going 7/12 (58%); run 7; 6/66 | still_going 7/12 (58%); run 5; 1/66 | still_going 10/14 (71%); run 8; 12/91 |

Per person over the 8 days:

| person | asks | days with top share >= 50% | highest day share | longest run | pairs >= 60% / all pairs | word-for-word equal pairs |
|---|---|---|---|---|---|---|
| elena | 77 | 2 of 8 | 90% (day 3, reassure_all 9/10) | 6 (day 3, reassure_all) | 17 / 318 | 1 |
| leo | 81 | 4 of 8 | 75% (day 3, confront_daniel 6/8) | 4 (day 3, confront_daniel) | 22 / 290 | 6 |
| mara | 88 | 8 of 8 | 91% (day 3, confront_daniel 10/11) | 8 (day 5, accuse_daniel) | 53 / 422 | 14 |
| daniel | 96 | 6 of 8 | 71% (day 10, still_going 10/14) | 8 (day 10, still_going) | 34 / 534 | 2 |
| all | 342 | 20 of 32 | | 8 | 126 / 1564 | 23 |

- **Share >= 80%:** 4 of 32 person-days: Elena day 3 (90%) and day 7 (88%); Mara day 3 (91%) and day 5 (91%).
- **Runs of 6 or more:** Mara day 5, `accuse_daniel` 8; Daniel day 10, `still_going` 8; Mara day 3, `confront_daniel` 7; Daniel day 8,
  `still_going` 7; Mara day 8, `accuse_daniel` 7; Elena day 3, `reassure_all` 6.
- **Daniel's `still_going`:** 32 of his 96 live day asks in days 3 to 10 (day 4: 2, day 5: 6, day 8: 7, day 9: 7, day 10: 10).
- **Other readings of "shares 60%":** Jaccard >= 0.6 gives 86 pairs of 1564; the overlap against the shorter answer gives 203.
- **Examples of the equal answers** (`q1_repetition.py` pairs; `say` counts over the day): Mara day 3, "You went out into the dark
  and came back with nothing, Daniel. Why did you even go?" 4 times and the same with "night" 3 times, in 11 asks; Leo day 7,
  "Risking your life doesn't give you the right to put everyone else in danger by sneaking out without a word, Daniel." 4 times,
  in 9 asks; Daniel day 10, "I am the eldest, and I am going to the neighbour's house tonight whether you like it or not." twice.

### talk_probe, day 3 (72 asks): per scene and person

| scene | person | asks | top option | share | longest run | pairs >= 60% / all | equal |
|---|---|---|---|---|---|---|---|
| 1 | elena | 4 | reassure_all | 2/4 = 50% | 1 | 0 / 6 | 0 |
| 1 | leo | 7 | silent | 2/7 = 29% | 2 | 0 / 10 | 0 |
| 1 | mara | 5 | accuse_daniel | 2/5 = 40% | 1 | 0 / 3 | 0 |
| 1 | daniel | 8 | reassure_leo | 3/8 = 38% | 2 | 0 / 28 | 0 |
| 3 | elena | 5 | reassure_all | 4/5 = 80% | 2 | 6 / 10 | 0 |
| 3 | leo | 7 | confront_daniel | 4/7 = 57% | 3 | 0 / 21 | 0 |
| 3 | mara | 5 | accuse_daniel | 3/5 = 60% | 2 | 0 / 6 | 0 |
| 3 | daniel | 7 | confront_leo | 4/7 = 57% | 3 | 0 / 21 | 0 |
| 4 | elena | 4 | reassure_all | 2/4 = 50% | 2 | 0 / 6 | 0 |
| 4 | leo | 7 | confront_daniel | 3/7 = 43% | 2 | 0 / 10 | 0 |
| 4 | mara | 5 | accuse_daniel | 4/5 = 80% | 4 | 1 / 10 | 0 |
| 4 | daniel | 8 | confront_mara | 3/8 = 38% | 3 | 1 / 28 | 0 |

All talk_probe: 8 pairs of 159 share 60% of their words, 0 are equal.

### calm_probe + calm_variants, day 3, 10:00 / 10:30 / 11:00, scenes 1 and 3 (64 live asks)

| person | version | live asks | options chosen | longest run, per scene |
|---|---|---|---|---|
| elena | P | 6 | reassure_all 6 | 3, 3 |
| elena | T | 6 | reassure_all 6 | 3, 3 |
| elena | O | 6 | reassure_all 6 | 3, 3 |
| elena | TO | 6 | reassure_all 6 | 3, 3 |
| mara | P | 6 | accuse_daniel 6 | 3, 3 |
| mara | T | 6 | accuse_daniel 6 | 3, 3 |
| mara | O | 4 | accuse_daniel 4 | 3, 1 |
| mara | TO | 4 | accuse_daniel 4 | 3, 1 |
| leo | P | 6 | silent 4, accuse_daniel 2 | 3, 1 |
| leo | T | 6 | silent 5, accuse_daniel 1 | 3, 2 |
| leo | O | 4 | tell_daniel_visit 3, accuse_daniel 1 | 1, 2 |
| leo | TO | 4 | tell_daniel_visit 4 | 1, 3 |

(P = calm_probe; T, O, TO = calm_variants.)

- **Elena:** `reassure_all` in **24 of 24** live asks. **Mara:** `accuse_daniel` in **20 of 20** live asks; the 24 of 24 of
  `reports/calm_variants.md` counts 4 rows that reuse an answer to an identical prompt (Mara, scene 3, O and TO, at 10:00 and 10:30).
  **Leo:** `silent` 9 of 20, `tell_daniel_visit` 7, `accuse_daniel` 4.
- **Pairs sharing 60%, pooled over a person's live answers** (all versions and both scenes): Elena 37 of 276 (1 equal); Mara 44 of 190 (6 equal);
  Leo 12 of 55 (0 equal). Inside one unit of three asks: Elena 0 or 1 of 3 pairs in each of 8 units; Mara 0 to 3 of 3 (scene 1: T 0, O 3, TO 3, P 1).
- **Words** (substring counts over the `say` text): Mara, "went out" in 17 of 20 answers and "nothing" in 14 of 20; Elena,
  "together", "tear" or "fight" in 21 of 24.

---

## 2. "What you have been doing"

**Where it is built.** `World.pattern`, `world.py:1083-1108`. Called from `_prompt_for`, `world.py:1188` (`now += self.pattern(p)`),
after the "Said and done in the {room} this turn, before you, in order:" lines (`world.py:1182-1187`) and before the options block.
The count it uses is `World.repeating`, `world.py:540-549`: the kind of the person's latest entry in `p.history` and the number of
consecutive entries of that kind.

**Exact wording rules** (code, `world.py:1086-1107`):

```
if not n or kind == "routine":      # nothing done since a routine began (quiet.py)      world.py:1087
    return []
first = p.history[-n]["seq"]
out = [f"What you have been doing: you have {KIND_DONE[kind]}, {n} turn{'s' if n > 1 else ''} in a row."]   world.py:1090
```

- `KIND_DONE` (`world.py:99-124`) maps the act's kind to its phrase: `reassure` "reassured someone", `accuse` "accused someone of taking
  it", `confront` "confronted someone", `silent` "stayed put and said nothing", `volunteer` "offered to go there tonight", `object`
  "said someone should not go", `door_refuse` "told the person at the door to go away", `talk` "talked about something that happened
  earlier", and so on. The kind comes from `act_of` (`talk.py:17-`), so `reassure_all` and `reassure_mara` are both "reassured someone".
- "1 turn" is singular; 2 or more is "turns". **Every line states a count of turns**, from 1 up.
- A second line follows (`world.py:1092-1107`): the lines others said since the first of those turns, aimed at the person or at everyone
  (`h["seq"] > first and h["who"] != p.id and h["target"] in (p.id, None)`):
  - none: `In that time nobody has said anything to you or to everyone.`
  - some: `In that time: <Name> <verb>[, then <verb>...]; <Name> ...` (verbs from `heard_verb`, `world.py:1110-1121`), then either
    `Answered you differently from one time to the next: <names>.` or `Nobody answered you differently from one time to the next.`

**When it is shown.**

- Day prompts only. A night prompt returns at `world.py:1160-1161` before the line is built.
- Not when `p.history` is empty. `night.py:1231` (in `next_day`, `night.py:1166`) empties it when the next day begins (`p.history = []`), so each
  person's first ask of a day has no line (v22, the asks at minute 00 of days 3 to 10: 32 of 32 have none).
- Not when the latest history entry is `routine`. `quiet.py:1041` appends `{"kind": "routine", "seq": None}` whenever a quiet routine
  begins (sit, withdraw, rest), with the comment "Hours pass in a routine: what they did before it is not 'in a row' with what they do after".
- What `p.history` counts: `world.py:1728` appends one entry for every act applied (`apply`), whether the person was asked or took the
  unasked turn's default (`World.routine`, `world.py:868-875`: `keep_searching`, `sit_*` or `silent`).

**Share of the asks in (1) that carried it** (`q2_pattern_line.py`, `q2_pattern_line.stdout.txt`):

| Set | Asks with the line | Of | Share | n = 1 / 2 / 3 |
|---|---|---|---|---|
| talk_probe | 51 | 72 | 71% | 43 / 7 / 1 |
| calm_variants | **0** | 46 | 0% | |
| calm_probe | **0** | 18 | 0% | |
| v22, days 3 to 10 | 247 | 342 | 72% | 169 / 58 / 20 |
| all | 298 | 478 | 62% | 212 / 65 / 21 |

- No shown line has n above 3 (`n > 3`: 0 asks of 478).
- Second line, in the 298: "nobody has said anything" 31; "Nobody answered you differently" 223; "Answered you differently" 44.
- v22 by day: day 3 28 of 40, day 4 31 of 40, day 5 29 of 40, day 6 29 of 40, day 7 31 of 42, day 8 32 of 48, day 9 34 of 48, day 10 33 of 44.
- In the 64 calm prompts the lines just above "Your options:" are "You are the first to act in the kitchen this turn." (64 of 64).

**Five examples** (and one more), as sent (`q2_examples.stdout.txt`; "from end" counts the last line of the prompt as 1):

1. talk_probe scene 4, Mara, 14:51 (chose `accuse_daniel`), 28 from the end:
   `What you have been doing: you have stayed put and said nothing, 3 turns in a row.` /
   `In that time nobody has said anything to you or to everyone.`
2. talk_probe scene 4, Leo, 11:51 (chose `silent`), 21 from the end:
   `What you have been doing: you have confronted someone, 2 turns in a row.` /
   `In that time: Daniel reassured you, then confronted you.` / `Answered you differently from one time to the next: Daniel.`
3. talk_probe scene 1, Daniel, 09:45 (chose `go_kitchen`), 7 from the end:
   `What you have been doing: you have stayed put and said nothing, 1 turn in a row.` /
   `In that time nobody has said anything to you or to everyone.`
4. talk_probe scene 1, Elena, 09:45 (chose `reassure_all`), 27 from the end:
   `What you have been doing: you have told the person at the door to go away, 1 turn in a row.` /
   `In that time: Mara spoke to everyone; Leo spoke to everyone.` / `Nobody answered you differently from one time to the next.`
5. v22 day 3, Mara, minute 09 (chose `accuse_daniel`), 28 from the end:
   `What you have been doing: you have confronted someone, 3 turns in a row.` /
   `In that time: Elena reassured everyone, then reassured everyone, then reassured everyone; Daniel reassured everyone, then reassured everyone.` /
   `Nobody answered you differently from one time to the next.`
6. v22 day 10, Daniel, minute 09 (chose `still_going`), 31 from the end:
   `What you have been doing: you have offered to go there tonight, 2 turns in a row.` /
   `In that time: Mara said you should not be the one to go, then confronted you; Leo said you should not be the one to go, then confronted you; Elena said nobody should go, then said you should not be the one to go.` /
   `Answered you differently from one time to the next: Mara, Leo, Elena.`

---

## 3. What stays fixed in Elena's and Mara's calm prompts at 10:00, 10:30 and 11:00

Method (`q3_fixed.py`, `q3_table.py`; `q3_fixed.stdout.txt`, `q3_table.md`): for each of 16 groups (scenes 1 and 3; versions P, T, O, TO;
Elena and Mara) the three prompts were split into lines, each line was given a section, and a line counts as fixed if its text is in
all three prompts. "From end": the last line of the prompt is 1. The full line-by-line listing for scene 1, version P, is
**Appendix A**; the 16 groups' differences are in `q3_table.md` (last table).

**Word for word the same at all three minutes** (scene 1, version P; the other groups differ as noted below):

| Section | Elena: lines, same in all three | Elena: from end at 10:00 / 10:30 / 11:00 | Mara: lines, same in all three | Mara: from end at 10:00 / 10:30 / 11:00 |
|---|---|---|---|---|
| sheet (`You are`, `How you address them`, `Who you are`, `Temperament`, `What matters to you`) | 5 of 5 | 89-85 / 89-85 / 91-87 | 5 of 5 | 88-84 / 88-84 / 91-87 |
| body and "About" lines (`Your body`, can, food, neighbour's house, street, going out at night, water) | 7 of 7 | 84-78 / 84-78 / 86-80 | 7 of 7 | 83-77 / 83-77 / 86-80 |
| **grudge lines** | 1 of 1 (`Against the others: nothing.`) | 77 / 77 / 79 | 2 of 2 (`Against Daniel (a lot): ...`, `Against Leo (a little): ...`) | 76-75 / 76-75 / 79-78 |
| house | 1 of 1 | 76 / 76 / 78 | 1 of 1 | 74 / 74 / 77 |
| days before (`What you remember from the days before:` + 7 lines) | 8 of 8 | 75-68 / 75-68 / 77-70 | 8 of 8 | 73-66 / 73-66 / 76-69 |
| carry-in: earlier days (`What stays with you from earlier days:` + 3) | 4 of 4 | 67-64 / 67-64 / 69-66 | 4 of 4 | 65-62 / 65-62 / 68-65 |
| carry-in: yesterday and last night (header + 7; Mara header + 10) | 8 of 8 | 63-56 / 63-56 / 65-58 | 11 of 11 | 61-51 / 61-51 / 64-54 |
| carry-in: what yesterday left in you (header + 3) | 4 of 4 | 55-52 / 55-52 / 57-54 | 4 of 4 | 50-47 / 50-47 / 53-50 |
| **sure lines** (`What you are sure of today:` + 2) | 3 of 3 | 51-49 / 51-49 / 53-51 | 3 of 3 | 46-44 / 46-44 / 49-47 |
| own last words (header + 3) | 4 of 4 | 48-45 / 48-45 / 50-47 | 4 of 4 | 43-40 / 43-40 / 46-43 |
| **memory** (`What else happened today, most recent last:`, `(earlier things, left out here)`, then the day's lines) | 8 of 9 at 10:00 (11:00 holds 8 lines) | 44-36 / 44-36 / 46-39 | 5 of 5 | 39-35 / 39-35 / 42-38 |
| now: `Now, ...` and the "is here" / portions / "first to act" lines | 5 of 6 (the `Now` line differs) | 35-30 / 35-30 / 35-30 | 5 of 6 (the `Now` line differs) | 34-29 / 34-29 / 34-29 |
| options (`Your options:` and the option lines) | 29 of 29 | 29-1 at all three | 28 of 28 | 28-1 at all three |
| **pattern line** | not in any of the three | | not in any of the three | |

- **The pattern line:** **NOT FOUND** in any of the 48 Elena and Mara prompts, nor in the other 16 calm prompts (Leo): 0 of 64.
  Cause in the state: at each of the 24 person-minutes (all four people, both scenes, 10:00 / 10:30 / 11:00) the last `history` entry
  is `routine`, `repeating(p) == ("routine", 1)` and `pattern(p) == []` (`state_probe.json`, from a rebuild of the replayed world
  with the code of `76edaa9`, the commit that ran calm_variants; fake model, 0 live; `q5_guard.stdout.txt`, part 5).
  Elena's history tail, scene 1: `reassure, silent, routine, routine, door_refuse, reassure, reassure, routine` (t = 4, 5, 6, 54, 54, 55, 56, 57).
  Mara's: `accuse, accuse, routine, routine, door_give, confront, accuse, routine`.
- **What is not fixed**, across all 16 groups:
  1. the `Now, HH:MM, you are in the kitchen.` line (16 of 16);
  2. three lines `You last spoke with <Name> at 09:48.` that exist at 11:00 only (16 of 16; `world.py:1166`, `quiet.meeting_lines`), placed right before the "Now" line;
  3. in T and TO, the line `Nobody in the kitchen has said anything since 09:48, N minutes ago; you have all stayed sitting here.` with N = 12, 42, 72 (8 of 16), right before the "Now" line (the probe's line; not in production code);
  4. Elena (8 groups): `- 09:45: Voices from the brothers room.` is in the 10:00 and 10:30 prompts and not in the 11:00 prompt;
  5. Mara, scene 3 (4 groups): `- 09:48: Elena reassures everyone: "We are all together here and we will get through this."` is in 10:00 and 10:30 and not at 11:00;
  6. Mara, scene 3 (4 groups): the option `tell_daniel_visit` is in the 11:00 prompt only.
- Items 4 and 5 are each the first line after `(earlier things, left out here)` that is missing at 11:00. The trim loop at
  `world.py:1241-1259` pops the oldest memory line while the estimate is over `PROMPT_TOKEN_BUDGET`; whether that is what removed them
  was not measured.

---

## 4. What names the chosen act, before the options

Method (`q4_names.py`, `q4_table.py`, `q4_themes.py`; `q4_names.stdout.txt`, `q4_table.md`): the 10:30 calm_probe prompt of each of Elena and Mara, scenes 1 and 3
(the other minutes and versions hold the same lines, section 3). Every line before `Your options:` was tested against five regular expressions:
**DANIEL** the word Daniel; **NIGHT** Daniel's night out (went there / out / to the neighbour; the neighbour's house tonight; going out; cross; should go; means to go;
into the night; came back; the front door being opened; nothing in his hands; bed was empty); **CAN** (the can; taking it; took the can; denied taking; denying it);
**FIGHT** (accus-, confront-, angry, fight-, quarrel, argu-); **TOGETHER** (together; apart; family whole / safe; keeping the family; closeness; reassur-; stay calm; stay together).

| Prompt | Lines before the options | Match NIGHT, CAN, FIGHT or TOGETHER | Name Daniel (any theme) |
|---|---|---|---|
| Elena (`reassure_all`), scene 1 | 60 | 17 | 23 |
| Elena, scene 3 | 60 | 18 | 24 |
| Mara (`accuse_daniel`), scene 1 | 60 | 21 | 25 |
| Mara, scene 3 | 61 | 21 | 26 |

Every line, quoted with its section and its position from the end, is in **Appendix B** (all four prompts). By section, scene 1:

**Mara (`accuse_daniel`)**
- *sheet:* `What matters to you: closeness, deciding for yourself, fairness.` (84 from end; TOGETHER). Lines 1 and 2 name Daniel as a family member only.
- *body and "About" lines:* `About the can: Daniel admitted taking it two days ago, at minute 33.` (82); `About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.` (80); `About going out at night: Daniel went to the neighbour's house last night and came back with nothing.` (78).
- *grudge lines:* `Against Daniel (a lot): two days ago, Daniel admitted taking it at minute 33, after denying it to you at minute 06; you were angry with Daniel today at minutes 12 and 15, and at 09:42 and 09:48.` (76); `Against Leo (a little): you were angry with Leo at 09:45.` (75).
- *days before:* `- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)` (72).
- *carry-in, earlier days:* `... Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us all morning and only confessed because he had no other choice."` (64); `... Leo denied taking the can 4 times.` (63).
- *carry-in, yesterday and last night:* `- Accusations: you accused Daniel 5 times (min 00, 03, 09, 12, 15).` (59); `- Confrontations: Leo confronted Daniel twice (min 09, 12).` (58); the "what was said yesterday about going out last night" line (56); `- In the night you heard the front door being opened. ... Daniel's bed was empty. You waited up by the front door.` (52); `- Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).` (51).
- *carry-in, what yesterday left in you:* `"Daniel said he meant to go out, and I told him he had to be the one to do it."` (49); `"Daniel went out into the night and came back before dawn with nothing in his hands."` (48).
- *own last words:* `- 09:45, you confronted Leo.` (41); `- 09:48, you accused Daniel.` (40).
- *memory:* `- 09:48: Elena reassures Leo: "...we just need to stay calm together."` (37); `- 09:48: you accused Daniel. You felt bitter hunger.` (36); `- 09:48: Daniel confronts you: "Mara, stop accusing me when I went out there to try and fix this for all of us."` (35).
- *sure lines:* 0 of 3; *now:* `- Daniel is here, sitting in the kitchen.` (33; names Daniel only).

**Elena (`reassure_all`)**
- *sheet:* `Who you are: Mother. ... Will lie to keep the family whole. Fears the household breaking apart more than she fears the outside.` (87); `What matters to you: keeping the family safe, closeness, fairness.` (85).
- *body and "About" lines:* the same can, neighbour's house and going-out lines as Mara's (83, 81, 79).
- *days before:* the same Day 2 line (74). *carry-in, earlier days:* 66, 65. *carry-in, yesterday and last night:* accusations 61, confrontations 60, the "going out last night" line 58.
- *carry-in, what yesterday left in you:* `- About saying nobody should go and saying Daniel must stay home: "I said nobody should go out into the street, we stay together here, and Daniel must stay home."` (53).
- *own last words:* `- 09:45, you reassured everyone.` (46); `- 09:48, you reassured Leo.` (45).
- *memory:* `- 09:48: you reassured Leo. You felt weary.` (38); `- 09:48: Mara accuses Daniel of taking it: "You brought back nothing last night, Daniel, and we're all starving because of your lies."` (37); `- 09:48: Daniel confronts Mara: "Mara, stop accusing me when I went out there to try and fix this for all of us."` (36).
- *sure lines:* 0 of 3 (the knock line names the woman, Mara and the water, not fighting or staying together).

Scene 3 differs only in the memory lines (Appendix B): Mara's and Elena's blocks carry `Mara accuses Daniel of taking it: "You went out there last night and you still have nothing to show for it. You took everything from us."`, `Daniel confronts Mara: "...I went out there to find something for all of us..."` and `Leo accuses Daniel of taking it: "Daniel, you went out last night against what we agreed and came back empty-handed."`.

---

## 5. The existing guards

**The guard** (`world.py:626-629`, last lines of `options_for`):

```
# A speech act used three turns in a row is not offered a fourth time.
kind, n = self.repeating(p)
if kind in SPEECH and n >= 3:
    opts = [o for o in opts if act_of(o.id)[0] != kind]
```

- **What it counts: turns (history entries), not asks.** `repeating` (`world.py:540-549`) counts consecutive `p.history` entries of the
  same kind; `p.history` gets one entry per applied act (`world.py:1728`), asked or not, and one `routine` entry whenever a quiet
  routine begins (`quiet.py:1041`), and it is emptied each night (`night.py:1231`). A `routine` entry ends the run: `repeating` then
  returns `("routine", 1)`.
- **What "kind" is.** `act_of` (`talk.py:17-`): `reassure_all`, `reassure_leo`, `reassure_mara` and `reassure_daniel` are all `reassure`; `accuse_<q>` is
  `accuse`. `SPEECH` (`talk.py:8-14`) lists the guarded kinds (ask, deny, accuse, confess, reassure, say, propose, volunteer, object, back,
  decline, propose_far, volunteer_far, confront, save_water, ration_water, door_call, door_refuse, talk, tell). **`silent` is not in `SPEECH`**
  and is never held back. `volunteer_far` is its own kind (`act_of` returns the option id for it).
- **When it fired in the data** (`q5_guard.py`, `q5_guard.stdout.txt`, part 1): 21 prompts say "3 turns in a row"; 17 are of a `SPEECH`
  kind (all in v22) and in **17 of 17** no option of that kind is offered; the other 4 (v22 3, talk_probe 1) are `silent`, which stays offered. No prompt
  shows more than 3.
- **Why it did not stop Elena's `reassure_all` run in v22 day 3** (`q5_guard.stdout.txt`, part 4): her six `reassure_all` in a row came as three
  pairs of asks, hours apart, and the third ask of the first burst *was* held back.

| Elena, v22 day 3 | chose | line shown | reassure options offered |
|---|---|---|---|
| minute 00 | reassure_all | none (history empty at the day's start) | 4 |
| minute 03 | reassure_all | reassured someone, 1 turn in a row | 4 |
| minute 06 | reassure_all | reassured someone, 2 turns in a row | 4 |
| minute 09 | **silent** | reassured someone, **3 turns in a row** | **0** |
| minute 12 | reassure_all | stayed put and said nothing, 1 turn in a row | 3 |
| minute 15 | reassure_all | reassured someone, 1 turn in a row | 3 |
| (minute 18) | unasked: `routine`, `silent` (transcript) | | |
| 10:30 | reassure_all | none (last history entry is `routine`) | 4 |
| 10:33 | reassure_all | reassured someone, 1 turn in a row | 4 |
| 17:39 | reassure_all | none (last history entry is `routine`) | 4 |
| 17:42 | reassure_all | reassured someone, 1 turn in a row | 4 |

  The six `reassure_all` in a row by asks are minutes 12 and 15, then 10:30 and 10:33, then 17:39 and 17:42. Counted in turns: the ask at minute 09
  was held back (3 turns of `reassure`, 0 reassure options) and she chose `silent`; minutes 12 and 15 then show "1 turn" each; the transcript has an unasked
  `routine` act, `silent`, at minute 18; the 10:30 and 17:39 prompts carry no line (the latest history entry is `routine`), and 10:33 and 17:42 show "1 turn".
  So each pair starts counting again at 1. The same pattern is in Mara's run of 8 `accuse_daniel` on day 5 (shown n: `1 1 2 - 1 2 - 1`) and in
  Daniel's run of 8 `still_going` on day 10 (`- 1 2 - 1 2 - 1`) (`q5_guard.stdout.txt`, part 2; `-` = no line). Runs of 4 or more of one option: 13
  (talk_probe 1, v22 12); the largest n any of their prompts showed is 3, once, in talk_probe scene 4 at 14:51 (for `silent`, which the guard does not cover).

- **In the calm probe** (the 6 `reassure_all` per version; 24 of 24 over four versions): at all 24 person-minutes the history ends on `routine`, so `repeating` is
  `("routine", 1)` and the guard cannot apply (`state_probe.json`: `guard_would_apply` false 24 of 24). Before the `routine` entry the tail holds two `reassure`
  entries for Elena (09:45, 09:48) and `confront, accuse` for Mara, under the threshold of 3. The probe does not apply answers (`reports/calm_probe.md`), so the history is the same at 10:00, 10:30 and 11:00.
  At HEAD `a24ae82` this state cannot be rebuilt: the replay stops, "a replayed ask missed the talk probe's cache" (`head_state_probe_check.stdout.txt`).
- **In talk_probe scene 3** Elena's five answers are all of the kind `reassure` (`reassure_all` x2, `reassure_mara`, `reassure_all` x2; 09:45, 09:48, 11:45, 16:54, 16:57); the lines shown
  are 1 turn, 1 turn, none, none, 1 turn (`q5_guard.stdout.txt`, part 6).
- **Where the held-back kind is recorded:** `held_back` in the in-memory decision (`world.py:1573-1575`); the run transcript's acts do not carry it
  (`runs/v22/daniel_ate_it-seed2.transcript.json`: no `held_back` key).

**Any other guard against one person repeating one option: NOT FOUND for the day options.**
`q5_grep.stdout.txt`:
- `world.py:629` is the only line that removes options by what the person did before (`grep -n "opts = \[o for o in opts"` over world, quiet, topics, night: one match).
- The words "repeat" / "in a row" appear only at `world.py:626-627, 1084-1090, 1573` (the guard, the pattern line, `held_back`), `quiet.py:1040` (the routine comment), `talk.py:135, 168` (a room's conversation ends after full turns with nothing new; this ends the conversation, it does not filter an option) and `mind.py:322` (`S9 a repeat`: the night mind rejects a memory line equal to one already carried; not an option).
- **Topic options only** (`talk_*`, `tell_*`): `topics.py:20-22, 125, 127, 133` hold F2 (`COOLDOWN = 60` minutes after the person chose them), F3 (`PER_DAY = 2`) and F4 (`ROOM_QUIET = 30` minutes per room).
- The prompt shows the last three of the person's own spoken lines (`world.py:1209`, `p.said_lines[-3:]`): it is text, not a filter.
- The system instruction (`SYSTEM` and `NIGHT_SYSTEM`, `world.py:41-62`): no match for "repeat" (`sed -n 40,62p world.py | grep -i repeat`: NOT FOUND).

---

## What was not determined

- Which of the two reasons (empty history at the day's start, or a last entry of `routine`) applies to each of the 180 asks with no pattern line in
  v22 and talk_probe: both give no line, and the prompts do not say. For the calm probe the state shows `routine` in all 24 person-minutes.
- Whether the trim loop (`world.py:1241-1259`) removed the two memory lines missing at 11:00 (section 3, items 4 and 5).
- The pair measure of Q1 is one reading of "share 60% or more of their words"; the two others are in the raw output.

## Commands run, and their output

All from `Prototypes/llm-morning/` with `env -u GEMINI_API_KEY .venv/Scripts/python.exe`, except where a `git archive` copy is the working directory.

```
$ git archive a4edf84 Prototypes/llm-morning | tar -x -C <scratchpad>/v22code      (the code v22 ran on)
$ git archive 76edaa9 Prototypes/llm-morning | tar -x -C <scratchpad>/calmcode     (the code calm_variants ran on)

$ runs/stuck_facts/collect.py                       -> collect.stdout.txt  (136 probe asks; "in cache with same option": 72/72, 46/46, 18/18)
records 136
('talk_probe', 1, 'live day asks', 24, 'in cache with same option', 24)   (scenes 3 and 4 likewise: 24 and 24)
('calm_variants', 1, 'live asks', 23, 'in cache with same option', 23)    (scene 3: 23 and 23)
('calm_probe', 1, 'live asks', 9, 'in cache with same option', 9)         (scene 3: 9 and 9)

$ (cwd = git archive of a4edf84) runs/stuck_facts/collect_v22.py cache/v22/... asks_v22.json   -> collect_v22.stdout.txt
replay exit 1 asks 498

$ (cwd = HEAD) runs/stuck_facts/collect_v22.py ... -> head_replay_check.stdout.txt
replay exit 3 asks 100

$ runs/stuck_facts/q1_repetition.py                  -> q1_repetition.stdout.txt  (the 8 transcript checks, 79 units, sequences, pooled calm)
check v22 day 3: transcript model acts 40, replay asks 40, same order per person: True   ... (days 4 to 10 likewise)
check v22 days that differ: 0

$ runs/stuck_facts/q1_summary.py                     -> q1_summary.md
$ runs/stuck_facts/q2_pattern_line.py                -> q2_pattern_line.stdout.txt
ALL            298 of 478 = 62%
$ runs/stuck_facts/q2_examples.py                    -> q2_examples.stdout.txt
$ (cwd = git archive of 76edaa9) runs/stuck_facts/state_probe.py state_probe.json   -> state_probe.stdout.txt
scene 1 replay {'live': 0, 'from_cache': 131, 'api_requests': 0} calm (fake) {'live': 9, ...} live ledger 9   (the "live" here is the fake model's count)
scene 3 replay {'live': 0, 'from_cache': 131, 'api_requests': 0} calm (fake) {'live': 9, ...}
rows 24
$ runs/stuck_facts/q3_fixed.py, q3_table.py          -> q3_fixed.stdout.txt, q3_table.md
$ runs/stuck_facts/q4_names.py, q4_table.py          -> q4_names.stdout.txt, q4_table.md
$ runs/stuck_facts/q5_guard.py                       -> q5_guard.stdout.txt
asks with n=3: 21; of them with an option of that kind still offered: 4
  those still offered, by kind: {'silent': 4} | kinds in SPEECH ... ['accuse', 'confront', 'object', 'reassure', 'volunteer'] | kinds not in SPEECH: ['silent']
  asks with n=3 of a SPEECH kind: 17 | of them with an option of that kind still offered: 0
asks with n > 3:  0
n shown, all asks: {1: 212, 2: 65, 3: 21, None: 180}
rows: 24 | last history entry is 'routine': 24 | repeating(p) = ('routine', 1): 24 | pattern(p) is empty: 24 | guard would apply: 0
$ grep ... (Q5)                                      -> q5_grep.stdout.txt
```

The scripts, in the order they were run, are in `runs/stuck_facts/`: `collect.py`, `collect_v22.py`, `q1_repetition.py`, `q1_summary.py`, `q2_pattern_line.py`,
`q2_examples.py`, `state_probe.py`, `sections.py`, `q3_fixed.py`, `q3_table.py`, `q4_themes.py`, `q4_names.py`, `q4_table.py`, `q5_guard.py`. `end_checks.txt` holds the final checks. Run order: `collect.py`, `collect_v22.py` (in the `a4edf84` copy), `q1_repetition.py` (writes `asks_all.json` from `asks.json` and
`asks_v22.json`), then `q1_summary.py`, `q2_*.py`, `q3_*.py`, `q4_*.py`, `q5_guard.py`; `state_probe.py` in the `76edaa9` copy. `asks_all.json` and `q2_rows.json` are derived
(3.9 MB and 0.2 MB) and are kept out of git by `runs/stuck_facts/.gitignore`.
`python merge-slice-docs.py Prototypes/llm-morning/runs/stuck_facts` (from the repository root) wrote `runs/stuck_facts/stuck_facts-all.md`.

---

## Appendix A: every line before the options in Elena's and Mara's calm prompts (scene 1, calm_probe), with its section, its position from the end at 10:00 / 10:30 / 11:00, and whether the same text is in all three

(`runs/stuck_facts/q3_table.md` holds this and, after it, the table of what is not fixed in all 16 groups. The option lines are listed in
`runs/stuck_facts/q3_fixed.stdout.txt`, with their positions from the end.)

#### Elena, scene 1, calm_probe prompts at 10:00 / 10:30 / 11:00 (lines before the options: 60, 60 at 10:00 and 10:30, 62 at 11:00)

| # (10:00) | section | from end 10:00 / 10:30 / 11:00 | same in all three | text |
|---|---|---|---|---|
| 1 | sheet | 89/89/91 | yes | You are Elena, 42, the mother of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17). |
| 2 | sheet | 88/88/90 | yes | How you address them: Daniel "Daniel"; Leo "Leo"; Mara "Mara". |
| 3 | sheet | 87/87/89 | yes | Who you are: Mother. Reads everyone, says little, holds it in. Will lie to keep the family whole. Fears the househo... |
| 4 | sheet | 86/86/88 | yes | Temperament: cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest. |
| 5 | sheet | 85/85/87 | yes | What matters to you: keeping the family safe, closeness, fairness. |
| 6 | body and 'About' lines | 84/84/86 | yes | Your body: starving, and you have hardly slept. |
| 7 | body and 'About' lines | 83/83/85 | yes | About the can: Daniel admitted taking it two days ago, at minute 33. |
| 8 | body and 'About' lines | 82/82/84 | yes | About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today. |
| 9 | body and 'About' lines | 81/81/83 | yes | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous. |
| 10 | body and 'About' lines | 80/80/82 | yes | About the street: the houses further along it have not been searched; nobody knows what is left in them, and it is ... |
| 11 | body and 'About' lines | 79/79/81 | yes | About going out at night: Daniel went to the neighbour's house last night and came back with nothing. |
| 12 | body and 'About' lines | 78/78/80 | yes | About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litre... |
| 13 | grudge lines | 77/77/79 | yes | Against the others: nothing. |
| 14 | house | 76/76/78 | yes | The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food ... |
| 15 | days before | 75/75/77 | yes | What you remember from the days before: |
| 16 | days before | 74/74/76 | yes | - Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it) |
| 17 | days before | 73/73/75 | yes | - Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it.... |
| 18 | days before | 72/72/74 | yes | - Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you ... |
| 19 | days before | 71/71/73 | yes | - Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her insid... |
| 20 | days before | 70/70/72 | yes | - Day 4: Leo says maybe they should let someone else handle this one. (you saw it) |
| 21 | days before | 69/69/71 | yes | - Day 4: Daniel empties Mara's bag onto the bed while she is standing there. (you saw it) |
| 22 | days before | 68/68/70 | yes | - Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you did it) |
| 23 | carry-in: earlier days | 67/67/69 | yes | What stays with you from earlier days: |
| 24 | carry-in: earlier days | 66/66/68 | yes | - Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel took the can in ... |
| 25 | carry-in: earlier days | 65/65/67 | yes | - Two days ago, Leo denied taking the can 4 times. |
| 26 | carry-in: earlier days | 64/64/66 | yes | - Two days ago, Mara ate a portion in front of you. |
| 27 | carry-in: yesterday and last night | 63/63/65 | yes | Yesterday and last night: |
| 28 | carry-in: yesterday and last night | 62/62/64 | yes | - Yesterday morning the shelf held 1 portion. |
| 29 | carry-in: yesterday and last night | 61/61/63 | yes | - Accusations: Mara accused Daniel 5 times (min 00, 03, 09, 12, 15). |
| 30 | carry-in: yesterday and last night | 60/60/62 | yes | - Confrontations: Leo confronted Daniel twice (min 09, 12). |
| 31 | carry-in: yesterday and last night | 59/59/61 | yes | - Daniel gave you a portion at minute 00, and you ate it. |
| 32 | carry-in: yesterday and last night | 58/58/60 | yes | - What was said yesterday about going out last night, where it was left: Mara said Daniel is the one who should go ... |
| 33 | carry-in: yesterday and last night | 57/57/59 | yes | - The afternoon and evening passed in the house. Nobody ate. |
| 34 | carry-in: yesterday and last night | 56/56/58 | yes | - Last night you slept in the back room with Mara. You went to sleep. |
| 35 | carry-in: what yesterday left in you | 55/55/57 | yes | What yesterday left in you (your own thoughts, last night): |
| 36 | carry-in: what yesterday left in you | 54/54/56 | yes | - About Daniel giving you a portion and eating a portion handed over: "Daniel gave me the portion and I ate it beca... |
| 37 | carry-in: what yesterday left in you | 53/53/55 | yes | - About saying nobody should go and saying Daniel must stay home: "I said nobody should go out into the street, we ... |
| 38 | carry-in: what yesterday left in you | 52/52/54 | yes | - How it left you: anxious and weary. |
| 39 | sure lines | 51/51/53 | yes | What you are sure of today: |
| 40 | sure lines | 50/50/52 | yes | - min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds ... |
| 41 | sure lines | 49/49/51 | yes | - 09:45: at 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away, and Mara ha... |
| 42 | own last words | 48/48/50 | yes | Your own last words today: |
| 43 | own last words | 47/47/49 | yes | - 09:42, you told the person at the door to go away. |
| 44 | own last words | 46/46/48 | yes | - 09:45, you reassured everyone. |
| 45 | own last words | 45/45/47 | yes | - 09:48, you reassured Leo. |
| 46 | memory (what else happened) | 44/44/46 | yes | What else happened today, most recent last: |
| 47 | memory (what else happened) | 43/43/45 | yes | - (earlier things, left out here) |
| 48 | memory (what else happened) | 42/42/- | NO | - 09:45: Voices from the brothers room. |
| 49 | memory (what else happened) | 41/41/44 | yes | - 09:45: Daniel comes into the kitchen. |
| 50 | memory (what else happened) | 40/40/43 | yes | - 09:45: Daniel gets up from his bed. |
| 51 | memory (what else happened) | 39/39/42 | yes | - 09:48: Leo says the water must be shared out by the cup from now on: "We gave three litres away and we have no fo... |
| 52 | memory (what else happened) | 38/38/41 | yes | - 09:48: you reassured Leo. You felt weary. |
| 53 | memory (what else happened) | 37/37/40 | yes | - 09:48: Mara accuses Daniel of taking it: "You brought back nothing last night, Daniel, and we're all starving bec... |
| 54 | memory (what else happened) | 36/36/39 | yes | - 09:48: Daniel confronts Mara: "Mara, stop accusing me when I went out there to try and fix this for all of us." |
| 55 | now | 35/-/- | NO | Now, 10:00, you are in the kitchen. |
| 56 | now | 34/34/34 | yes | - Daniel is here, sitting in the kitchen. |
| 57 | now | 33/33/33 | yes | - Leo is here, sitting in the kitchen. |
| 58 | now | 32/32/32 | yes | - Mara is here, sitting in the kitchen. |
| 59 | now | 31/31/31 | yes | - 0 portions on the shelf. |
| 60 | now | 30/30/30 | yes | You are the first to act in the kitchen this turn. |
| (11:00 only) | now: meeting lines (world.py:1166) | -/-/38 | NO | You last spoke with Daniel at 09:48. |
| (11:00 only) | now: meeting lines (world.py:1166) | -/-/37 | NO | You last spoke with Leo at 09:48. |
| (11:00 only) | now: meeting lines (world.py:1166) | -/-/36 | NO | You last spoke with Mara at 09:48. |
| (11:00 only) | now | -/-/35 | NO | Now, 11:00, you are in the kitchen. |

The options: 'Your options:' is 29 from the end at every minute, and the 28 option lines under it are the same, in the same order, at 10:00, 10:30 and 11:00.

#### Mara, scene 1, calm_probe prompts at 10:00 / 10:30 / 11:00 (lines before the options: 60, 60 at 10:00 and 10:30, 63 at 11:00)

| # (10:00) | section | from end 10:00 / 10:30 / 11:00 | same in all three | text |
|---|---|---|---|---|
| 1 | sheet | 88/88/91 | yes | You are Mara, 17, the youngest, the daughter of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17). |
| 2 | sheet | 87/87/90 | yes | How you address them: Elena "Mom"; Daniel "Daniel"; Leo "Leo". |
| 3 | sheet | 86/86/89 | yes | Who you are: Younger sister. Frightened and easy to read, but old enough to resent being handled like a child. Ever... |
| 4 | sheet | 85/85/88 | yes | Temperament: somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest. |
| 5 | sheet | 84/84/87 | yes | What matters to you: closeness, deciding for yourself, fairness. |
| 6 | body and 'About' lines | 83/83/86 | yes | Your body: starving; hunger comes in waves; and you have hardly slept. |
| 7 | body and 'About' lines | 82/82/85 | yes | About the can: Daniel admitted taking it two days ago, at minute 33. |
| 8 | body and 'About' lines | 81/81/84 | yes | About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today. |
| 9 | body and 'About' lines | 80/80/83 | yes | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous. |
| 10 | body and 'About' lines | 79/79/82 | yes | About the street: the houses further along it have not been searched; nobody knows what is left in them, and it is ... |
| 11 | body and 'About' lines | 78/78/81 | yes | About going out at night: Daniel went to the neighbour's house last night and came back with nothing. |
| 12 | body and 'About' lines | 77/77/80 | yes | About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litre... |
| 13 | grudge lines | 76/76/79 | yes | Against Daniel (a lot): two days ago, Daniel admitted taking it at minute 33, after denying it to you at minute 06;... |
| 14 | grudge lines | 75/75/78 | yes | Against Leo (a little): you were angry with Leo at 09:45. |
| 15 | house | 74/74/77 | yes | The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food ... |
| 16 | days before | 73/73/76 | yes | What you remember from the days before: |
| 17 | days before | 72/72/75 | yes | - Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it) |
| 18 | days before | 71/71/74 | yes | - Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it.... |
| 19 | days before | 70/70/73 | yes | - Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you ... |
| 20 | days before | 69/69/72 | yes | - Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her insid... |
| 21 | days before | 68/68/71 | yes | - Day 4: Leo says maybe they should let someone else handle this one. (you saw it) |
| 22 | days before | 67/67/70 | yes | - Day 4: Daniel empties Mara's bag onto the bed while she is standing there. (you saw it) |
| 23 | days before | 66/66/69 | yes | - Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it) |
| 24 | carry-in: earlier days | 65/65/68 | yes | What stays with you from earlier days: |
| 25 | carry-in: earlier days | 64/64/67 | yes | - Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us all m... |
| 26 | carry-in: earlier days | 63/63/66 | yes | - Two days ago, Leo denied taking the can 4 times. |
| 27 | carry-in: earlier days | 62/62/65 | yes | - Two days ago, you ate a portion in front of the others. |
| 28 | carry-in: yesterday and last night | 61/61/64 | yes | Yesterday and last night: |
| 29 | carry-in: yesterday and last night | 60/60/63 | yes | - Yesterday morning the shelf held 1 portion. |
| 30 | carry-in: yesterday and last night | 59/59/62 | yes | - Accusations: you accused Daniel 5 times (min 00, 03, 09, 12, 15). |
| 31 | carry-in: yesterday and last night | 58/58/61 | yes | - Confrontations: Leo confronted Daniel twice (min 09, 12). |
| 32 | carry-in: yesterday and last night | 57/57/60 | yes | - Daniel gave Elena a portion at minute 00, and Elena ate it (you saw it). |
| 33 | carry-in: yesterday and last night | 56/56/59 | yes | - What was said yesterday about going out last night, where it was left: you said Daniel is the one who should go (... |
| 34 | carry-in: yesterday and last night | 55/55/58 | yes | - The afternoon and evening passed in the house. Nobody ate. |
| 35 | carry-in: yesterday and last night | 54/54/57 | yes | - Last night you slept in the back room with Elena. You lay awake and listened. |
| 36 | carry-in: yesterday and last night | 53/53/56 | yes | - In the night you heard low voices from the brothers room. |
| 37 | carry-in: yesterday and last night | 52/52/55 | yes | - In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You ... |
| 38 | carry-in: yesterday and last night | 51/51/54 | yes | - Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). |
| 39 | carry-in: what yesterday left in you | 50/50/53 | yes | What yesterday left in you (your own thoughts, last night): |
| 40 | carry-in: what yesterday left in you | 49/49/52 | yes | - About saying Daniel should go and Daniel saying he still means to go: "Daniel said he meant to go out, and I told... |
| 41 | carry-in: what yesterday left in you | 48/48/51 | yes | - About the front door opening in the night and Daniel coming back in before dawn: "Daniel went out into the night ... |
| 42 | carry-in: what yesterday left in you | 47/47/50 | yes | - How it left you: anxious and exhausted. |
| 43 | sure lines | 46/46/49 | yes | What you are sure of today: |
| 44 | sure lines | 45/45/48 | yes | - min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds ... |
| 45 | sure lines | 44/44/47 | yes | - 09:45: at 09:42 someone knocked at the front door: Elena told a woman, who asked for water, to go away, and you h... |
| 46 | own last words | 43/43/46 | yes | Your own last words today: |
| 47 | own last words | 42/42/45 | yes | - 09:42, you handed water out at the front door. |
| 48 | own last words | 41/41/44 | yes | - 09:45, you confronted Leo. |
| 49 | own last words | 40/40/43 | yes | - 09:48, you accused Daniel. |
| 50 | memory (what else happened) | 39/39/42 | yes | What else happened today, most recent last: |
| 51 | memory (what else happened) | 38/38/41 | yes | - (earlier things, left out here) |
| 52 | memory (what else happened) | 37/37/40 | yes | - 09:48: Elena reassures Leo: "Leo is right to be careful with what is left, we just need to stay calm together." |
| 53 | memory (what else happened) | 36/36/39 | yes | - 09:48: you accused Daniel. You felt bitter hunger. |
| 54 | memory (what else happened) | 35/35/38 | yes | - 09:48: Daniel confronts you: "Mara, stop accusing me when I went out there to try and fix this for all of us." |
| 55 | now | 34/-/- | NO | Now, 10:00, you are in the kitchen. |
| 56 | now | 33/33/33 | yes | - Daniel is here, sitting in the kitchen. |
| 57 | now | 32/32/32 | yes | - Elena is here, sitting in the kitchen. |
| 58 | now | 31/31/31 | yes | - Leo is here, sitting in the kitchen. |
| 59 | now | 30/30/30 | yes | - 0 portions on the shelf. |
| 60 | now | 29/29/29 | yes | You are the first to act in the kitchen this turn. |
| (11:00 only) | now: meeting lines (world.py:1166) | -/-/37 | NO | You last spoke with Daniel at 09:48. |
| (11:00 only) | now: meeting lines (world.py:1166) | -/-/36 | NO | You last spoke with Elena at 09:48. |
| (11:00 only) | now: meeting lines (world.py:1166) | -/-/35 | NO | You last spoke with Leo at 09:48. |
| (11:00 only) | now | -/-/34 | NO | Now, 11:00, you are in the kitchen. |

The options: 'Your options:' is 28 from the end at every minute, and the 27 option lines under it are the same, in the same order, at 10:00, 10:30 and 11:00.

---

## Appendix B: every line before the options that names the target or the subject of the act chosen (Elena `reassure_all`, Mara `accuse_daniel`; 10:30 prompts, scenes 1 and 3)

(`runs/stuck_facts/q4_table.md`, from `q4_table.py`; the regular expressions are in `q4_themes.py`.)

#### Elena (chose reassure_all), scene 1, 10:30 prompt (89 lines, 60 before the options)

17 lines match NIGHT, CAN, FIGHT or TOGETHER; 29 of the 60 name Daniel or match one of those.

| line | section | from end | themes | text |
|---|---|---|---|---|
| 3 | sheet | 87 | TOGETHER | Who you are: Mother. Reads everyone, says little, holds it in. Will lie to keep the family whole. Fears the household breaking apart more than she fears the outside. |
| 5 | sheet | 85 | TOGETHER | What matters to you: keeping the family safe, closeness, fairness. |
| 7 | body and 'About' lines | 83 | DANIEL, CAN | About the can: Daniel admitted taking it two days ago, at minute 33. |
| 9 | body and 'About' lines | 81 | DANIEL, NIGHT | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous. |
| 11 | body and 'About' lines | 79 | DANIEL, NIGHT | About going out at night: Daniel went to the neighbour's house last night and came back with nothing. |
| 16 | days before | 74 | DANIEL, NIGHT | - Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it) |
| 24 | carry-in: earlier days | 66 | DANIEL, CAN | - Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel took the can in the night and had to confess to us all." |
| 25 | carry-in: earlier days | 65 | CAN | - Two days ago, Leo denied taking the can 4 times. |
| 29 | carry-in: yesterday and last night | 61 | DANIEL, FIGHT | - Accusations: Mara accused Daniel 5 times (min 00, 03, 09, 12, 15). |
| 30 | carry-in: yesterday and last night | 60 | DANIEL, FIGHT | - Confrontations: Leo confronted Daniel twice (min 09, 12). |
| 32 | carry-in: yesterday and last night | 58 | DANIEL, NIGHT | - What was said yesterday about going out last night, where it was left: Mara said Daniel is the one who should go (min 06); Leo said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); you said nobody should go (min 12); then Daniel went to the neighbour's house anyway and came back with nothing. |
| 37 | carry-in: what yesterday left in you | 53 | DANIEL, NIGHT, TOGETHER | - About saying nobody should go and saying Daniel must stay home: "I said nobody should go out into the street, we stay together here, and Daniel must stay home." |
| 44 | own last words | 46 | TOGETHER | - 09:45, you reassured everyone. |
| 45 | own last words | 45 | TOGETHER | - 09:48, you reassured Leo. |
| 52 | memory (what else happened) | 38 | TOGETHER | - 09:48: you reassured Leo. You felt weary. |
| 53 | memory (what else happened) | 37 | DANIEL, CAN, FIGHT | - 09:48: Mara accuses Daniel of taking it: "You brought back nothing last night, Daniel, and we're all starving because of your lies." |
| 54 | memory (what else happened) | 36 | DANIEL, NIGHT, FIGHT | - 09:48: Daniel confronts Mara: "Mara, stop accusing me when I went out there to try and fix this for all of us." |

Lines that name Daniel and match no other theme: 1 (sheet, 89 from end); 2 (sheet, 88 from end); 14 (house, 76 from end); 17 (days before, 73 from end); 18 (days before, 72 from end); 19 (days before, 71 from end); 21 (days before, 69 from end); 31 (carry-in: yesterday and last night, 59 from end); 36 (carry-in: what yesterday left in you, 54 from end); 49 (memory (what else happened), 41 from end); 50 (memory (what else happened), 40 from end); 56 (now, 34 from end).

#### Elena (chose reassure_all), scene 3, 10:30 prompt (89 lines, 60 before the options)

18 lines match NIGHT, CAN, FIGHT or TOGETHER; 30 of the 60 name Daniel or match one of those.

| line | section | from end | themes | text |
|---|---|---|---|---|
| 3 | sheet | 87 | TOGETHER | Who you are: Mother. Reads everyone, says little, holds it in. Will lie to keep the family whole. Fears the household breaking apart more than she fears the outside. |
| 5 | sheet | 85 | TOGETHER | What matters to you: keeping the family safe, closeness, fairness. |
| 7 | body and 'About' lines | 83 | DANIEL, CAN | About the can: Daniel admitted taking it two days ago, at minute 33. |
| 9 | body and 'About' lines | 81 | DANIEL, NIGHT | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous. |
| 11 | body and 'About' lines | 79 | DANIEL, NIGHT | About going out at night: Daniel went to the neighbour's house last night and came back with nothing. |
| 16 | days before | 74 | DANIEL, NIGHT | - Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it) |
| 24 | carry-in: earlier days | 66 | DANIEL, CAN | - Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel took the can in the night and had to confess to us all." |
| 25 | carry-in: earlier days | 65 | CAN | - Two days ago, Leo denied taking the can 4 times. |
| 29 | carry-in: yesterday and last night | 61 | DANIEL, FIGHT | - Accusations: Mara accused Daniel 5 times (min 00, 03, 09, 12, 15). |
| 30 | carry-in: yesterday and last night | 60 | DANIEL, FIGHT | - Confrontations: Leo confronted Daniel twice (min 09, 12). |
| 32 | carry-in: yesterday and last night | 58 | DANIEL, NIGHT | - What was said yesterday about going out last night, where it was left: Mara said Daniel is the one who should go (min 06); Leo said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); you said nobody should go (min 12); then Daniel went to the neighbour's house anyway and came back with nothing. |
| 37 | carry-in: what yesterday left in you | 53 | DANIEL, NIGHT, TOGETHER | - About saying nobody should go and saying Daniel must stay home: "I said nobody should go out into the street, we stay together here, and Daniel must stay home." |
| 44 | own last words | 46 | TOGETHER | - 09:45, you reassured everyone. |
| 45 | own last words | 45 | TOGETHER | - 09:48, you reassured everyone. |
| 51 | memory (what else happened) | 39 | TOGETHER | - 09:48: you reassured everyone. You felt anxious. |
| 52 | memory (what else happened) | 38 | DANIEL, NIGHT, CAN, FIGHT | - 09:48: Mara accuses Daniel of taking it: "You went out there last night and you still have nothing to show for it. You took everything from us." |
| 53 | memory (what else happened) | 37 | DANIEL, NIGHT, FIGHT | - 09:48: Daniel confronts Mara: "Mara, I went out there to find something for all of us, not to take anything from you." |
| 54 | memory (what else happened) | 36 | DANIEL, NIGHT, CAN, FIGHT | - 09:48: Leo accuses Daniel of taking it: "Daniel, you went out last night against what we agreed and came back empty-handed." |

Lines that name Daniel and match no other theme: 1 (sheet, 89 from end); 2 (sheet, 88 from end); 14 (house, 76 from end); 17 (days before, 73 from end); 18 (days before, 72 from end); 19 (days before, 71 from end); 21 (days before, 69 from end); 31 (carry-in: yesterday and last night, 59 from end); 36 (carry-in: what yesterday left in you, 54 from end); 49 (memory (what else happened), 41 from end); 50 (memory (what else happened), 40 from end); 56 (now, 34 from end).

#### Mara (chose accuse_daniel), scene 1, 10:30 prompt (88 lines, 60 before the options)

21 lines match NIGHT, CAN, FIGHT or TOGETHER; 30 of the 60 name Daniel or match one of those.

| line | section | from end | themes | text |
|---|---|---|---|---|
| 5 | sheet | 84 | TOGETHER | What matters to you: closeness, deciding for yourself, fairness. |
| 7 | body and 'About' lines | 82 | DANIEL, CAN | About the can: Daniel admitted taking it two days ago, at minute 33. |
| 9 | body and 'About' lines | 80 | DANIEL, NIGHT | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous. |
| 11 | body and 'About' lines | 78 | DANIEL, NIGHT | About going out at night: Daniel went to the neighbour's house last night and came back with nothing. |
| 13 | grudge lines | 76 | DANIEL, CAN, FIGHT | Against Daniel (a lot): two days ago, Daniel admitted taking it at minute 33, after denying it to you at minute 06; you were angry with Daniel today at minutes 12 and 15, and at 09:42 and 09:48. |
| 14 | grudge lines | 75 | FIGHT | Against Leo (a little): you were angry with Leo at 09:45. |
| 17 | days before | 72 | DANIEL, NIGHT | - Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it) |
| 25 | carry-in: earlier days | 64 | DANIEL, CAN | - Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us all morning and only confessed because he had no other choice." |
| 26 | carry-in: earlier days | 63 | CAN | - Two days ago, Leo denied taking the can 4 times. |
| 30 | carry-in: yesterday and last night | 59 | DANIEL, FIGHT | - Accusations: you accused Daniel 5 times (min 00, 03, 09, 12, 15). |
| 31 | carry-in: yesterday and last night | 58 | DANIEL, FIGHT | - Confrontations: Leo confronted Daniel twice (min 09, 12). |
| 33 | carry-in: yesterday and last night | 56 | DANIEL, NIGHT | - What was said yesterday about going out last night, where it was left: you said Daniel is the one who should go (min 06); Leo said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); Elena said nobody should go (min 12); then Daniel went to the neighbour's house anyway and came back with nothing. |
| 37 | carry-in: yesterday and last night | 52 | DANIEL, NIGHT | - In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door. |
| 38 | carry-in: yesterday and last night | 51 | DANIEL, NIGHT | - Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). |
| 40 | carry-in: what yesterday left in you | 49 | DANIEL, NIGHT | - About saying Daniel should go and Daniel saying he still means to go: "Daniel said he meant to go out, and I told him he had to be the one to do it." |
| 41 | carry-in: what yesterday left in you | 48 | DANIEL, NIGHT | - About the front door opening in the night and Daniel coming back in before dawn: "Daniel went out into the night and came back before dawn with nothing in his hands." |
| 48 | own last words | 41 | FIGHT | - 09:45, you confronted Leo. |
| 49 | own last words | 40 | DANIEL, FIGHT | - 09:48, you accused Daniel. |
| 52 | memory (what else happened) | 37 | TOGETHER | - 09:48: Elena reassures Leo: "Leo is right to be careful with what is left, we just need to stay calm together." |
| 53 | memory (what else happened) | 36 | DANIEL, FIGHT | - 09:48: you accused Daniel. You felt bitter hunger. |
| 54 | memory (what else happened) | 35 | DANIEL, NIGHT, FIGHT | - 09:48: Daniel confronts you: "Mara, stop accusing me when I went out there to try and fix this for all of us." |

Lines that name Daniel and match no other theme: 1 (sheet, 88 from end); 2 (sheet, 87 from end); 15 (house, 74 from end); 18 (days before, 71 from end); 19 (days before, 70 from end); 20 (days before, 69 from end); 22 (days before, 67 from end); 32 (carry-in: yesterday and last night, 57 from end); 56 (now, 33 from end).

#### Mara (chose accuse_daniel), scene 3, 10:30 prompt (88 lines, 61 before the options)

21 lines match NIGHT, CAN, FIGHT or TOGETHER; 30 of the 61 name Daniel or match one of those.

| line | section | from end | themes | text |
|---|---|---|---|---|
| 5 | sheet | 84 | TOGETHER | What matters to you: closeness, deciding for yourself, fairness. |
| 7 | body and 'About' lines | 82 | DANIEL, CAN | About the can: Daniel admitted taking it two days ago, at minute 33. |
| 9 | body and 'About' lines | 80 | DANIEL, NIGHT | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous. |
| 11 | body and 'About' lines | 78 | DANIEL, NIGHT | About going out at night: Daniel went to the neighbour's house last night and came back with nothing. |
| 13 | grudge lines | 76 | DANIEL, CAN, FIGHT | Against Daniel (a lot): two days ago, Daniel admitted taking it at minute 33, after denying it to you at minute 06; you were angry with Daniel today at minutes 12 and 15, and at 09:42 and 09:48. |
| 14 | grudge lines | 75 | FIGHT | Against Leo (a little): you were angry with Leo at 09:45. |
| 17 | days before | 72 | DANIEL, NIGHT | - Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it) |
| 25 | carry-in: earlier days | 64 | DANIEL, CAN | - Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us all morning and only confessed because he had no other choice." |
| 26 | carry-in: earlier days | 63 | CAN | - Two days ago, Leo denied taking the can 4 times. |
| 30 | carry-in: yesterday and last night | 59 | DANIEL, FIGHT | - Accusations: you accused Daniel 5 times (min 00, 03, 09, 12, 15). |
| 31 | carry-in: yesterday and last night | 58 | DANIEL, FIGHT | - Confrontations: Leo confronted Daniel twice (min 09, 12). |
| 33 | carry-in: yesterday and last night | 56 | DANIEL, NIGHT | - What was said yesterday about going out last night, where it was left: you said Daniel is the one who should go (min 06); Leo said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); Elena said nobody should go (min 12); then Daniel went to the neighbour's house anyway and came back with nothing. |
| 37 | carry-in: yesterday and last night | 52 | DANIEL, NIGHT | - In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door. |
| 38 | carry-in: yesterday and last night | 51 | DANIEL, NIGHT | - Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). |
| 40 | carry-in: what yesterday left in you | 49 | DANIEL, NIGHT | - About saying Daniel should go and Daniel saying he still means to go: "Daniel said he meant to go out, and I told him he had to be the one to do it." |
| 41 | carry-in: what yesterday left in you | 48 | DANIEL, NIGHT | - About the front door opening in the night and Daniel coming back in before dawn: "Daniel went out into the night and came back before dawn with nothing in his hands." |
| 49 | own last words | 40 | DANIEL, FIGHT | - 09:48, you accused Daniel. |
| 52 | memory (what else happened) | 37 | TOGETHER | - 09:48: Elena reassures everyone: "We are all together here and we will get through this." |
| 53 | memory (what else happened) | 36 | DANIEL, FIGHT | - 09:48: you accused Daniel. You felt angry. |
| 54 | memory (what else happened) | 35 | DANIEL, NIGHT, FIGHT | - 09:48: Daniel confronts you: "Mara, I went out there to find something for all of us, not to take anything from you." |
| 55 | memory (what else happened) | 34 | DANIEL, NIGHT, CAN, FIGHT | - 09:48: Leo accuses Daniel of taking it: "Daniel, you went out last night against what we agreed and came back empty-handed." |

Lines that name Daniel and match no other theme: 1 (sheet, 88 from end); 2 (sheet, 87 from end); 15 (house, 74 from end); 18 (days before, 71 from end); 19 (days before, 70 from end); 20 (days before, 69 from end); 22 (days before, 67 from end); 32 (carry-in: yesterday and last night, 57 from end); 57 (now, 32 from end).
