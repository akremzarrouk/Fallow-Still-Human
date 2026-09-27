# Design: one uncertain witness (`daniel_ate_it_leo_heard`)

Mode: design. No code was written or changed, no scenario was changed, and no API was called.
The only file this step adds is this one. Paths are relative to `Prototypes/llm-morning/`.

**Question.** In `daniel_ate_it` nobody has a reason to suspect Daniel (baseline_v6.md: Leo names
`nobody` as his suspect in all 31 of his model acts across the three seeds). If Leo half-heard the
night, does he handle the uncertain memory like a person would (hold back, hint, ask), or does he
ignore it or accuse at once?

**What is compared.** The new scenario `daniel_ate_it_leo_heard`, seeds 1–3, against
`runs/v6/daniel_ate_it-seed1..3` (reports/baseline_v6.md). One thing differs between them: one
perception of Leo's.

---

## 1. The sentence

```
In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who.
```

108 characters. In Leo's prompt it appears as this line:

```
- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who. (you heard it)
```

What it contains, against the brief: he woke; he heard someone in the kitchen; he heard a can
being opened; he did not get up; he did not see who. The only name in it is Leo's. The only
pronoun ("He") refers to Leo.

### Where it enters: the backstory, as its own event

It goes into Leo's **backstory**, as a separate event `(3, <sentence>, {"leo": "heard"})` placed
right after the scenario's night. It does **not** go into `sure`, and it is **not** made by
adding `"leo": "heard"` to the existing night event.

1. **Not by adding Leo to the night event.** Backstory lines are rendered as
   `f"Day {day}: {text} (you {how} it)"` for every event whose `who` map names the person
   (world.py:201-202). The text is the same summary for everyone (knowledge_audit.md §8 row e).
   If `"leo": "heard"` were added to the night event, Leo would get
   "Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you heard it)".
   That line names the person he did not see.
2. **Its own event solves this.** A separate event is shown only to the people in its `who` map,
   and here that is Leo alone. So its sentence can say only what Leo perceived. It is the first
   backstory sentence written from what one person perceived rather than as a summary for
   everyone. The rendering code does not change.
3. **Backstory, not `sure`.**
   - The event happened in the night of day 3, the same day the culprit's night line uses
     (data.py:105). The backstory section is headed "What you remember from the days before"
     (world.py:529), which fits it.
   - `sure` is headed "What you are sure of this morning" (world.py:524). Every `sure` line is
     timed "min NN:" except the culprit's knowledge line (world.py:265-267).
   - A night event heard in bed already has a precedent: "Day 3: Mara cries in the night. …
     (you heard it)" is in Leo's backstory (data.py:144-145).
4. **The cost: backstory lines can be trimmed; `sure` lines cannot** (world.py:528-545).
   - Order of cuts: memory down to 8 entries, then backstory down to 4 lines, then all of
     memory, then more backstory.
   - With the event added, Leo has 11 backstory lines. The new line is 3rd from last: Mara
     freezes, **the new line**, Day 4 Leo, Day 4 Elena. It survives the cut to 4 lines. It can
     only be cut after all of the morning's memory has been cut.
   - In cache/v6, every Leo prompt kept at least 4 backstory lines (min 4, max 10, in 31 prompts;
     §9, command 3).
   - Test T5 below checks that the line is in every Leo prompt, and run check R4 checks the same
     on the real prompts.

### Length: why the sentence is 108 characters

The prompt budget is 1,400 estimated tokens, where `estimate_tokens` = `int(len/3.6) + 1`
(world.py:51, 71-72). Leo's minute-00 prompts in cache/v6 are already close to it, because in
seeds 2 and 3 he acts last and three lines of what was said come before his turn. The table
shows each candidate wording inserted after "Day 3: Mara freezes…" in the real baseline Leo
minute-00 prompt (§9, command 4):

| Wording (length) | seed 1 | seed 2 | seed 3 |
|---|---|---|---|
| baseline, no line | 1319 | 1360 | 1361 |
| first draft, 132 chars ("…, then a can being opened. He does not get up, and he does not see who it is.") | 1363 | **1404** | **1405** |
| 117 chars ("…He stays in bed and does not see who.") | 1359 | 1400 | **1401** |
| **chosen, 108 chars** | 1356 | 1397 | 1398 |

Over 1,400, the first cut would remove Leo's oldest backstory line ("Day 1: Daniel boards the front
windows…") and add the marker "- (earlier things, left out here)". That would be a **second**
difference at minute 00. The chosen wording stays under the budget in all three seeds, with 2
tokens to spare in seed 3.

Leo's minute-00 memory section, built from the seed-3 baseline prompt with the line inserted
(§9, command 5):

```
What you remember from the days before:
- Day 1: Daniel boards the front windows on his own while the others watch. (you saw it)
- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you did it)
- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)
- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you did it)
- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
- Day 3: Mara cries in the night. Elena sits with her until it stops. (you heard it)
- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who. (you heard it)   <-- added
- Day 4: Leo says maybe they should let someone else handle this one. (you did it)
- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)
```

---

## 2. The scenario

`daniel_ate_it_leo_heard` is `daniel_ate_it` plus one event.

| | `daniel_ate_it` (data.py:103-107) | `daniel_ate_it_leo_heard` |
|---|---|---|
| culprit | `"daniel"` | `"daniel"` |
| night | `(3, "In the night Daniel eats a can standing at the counter in the dark. Nobody sees.", {"daniel": "did"})` | the same tuple, unchanged |
| added event | — | `(3, "<the sentence>", {"leo": "heard"})`, placed immediately after the night |

- **Unchanged.** Everything else: people, house, opening, portions, options, rules, the story
  renderer.
- **Daniel's own lines stay the same and stay true.** "Nobody sees." (data.py:105), "you ate it
  yourself in the night, and nobody saw" (world.py:267), and "On your conscience: you ate the can
  in the night, and nobody saw" (world.py:450) are all still true, because Leo did not see.
  Daniel is not told he was heard.
- **Where the event goes.** `backstory(scenario)` (data.py:157-160) puts the event directly after
  the night, which is where NIGHT sits in `_BACKSTORY` (data.py:148). The other three scenarios
  have no such event, so their backstories are unchanged.
- **CLI.** morning.py builds `--scenario` choices from `data.SCENARIOS` (morning.py:136), so the
  new name needs no CLI change.
- **Output files.** Runs are named `daniel_ate_it_leo_heard-seedN` (morning.py:46), in runs/v6/.
  The cache is `cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seedN.json` (morning.py:47).
- **Story.** The story's backstory table (story.py:233) gets one more row. In column order Daniel,
  Elena, Leo, Mara it reads
  `| 3 | In the night Leo wakes … does not see who. | not there | not there | heard it | not there |`.
  story.py:10 already maps "heard" to "heard it".
- **Seeding.**
  - Turn order is drawn from `random.Random(f"{seed}:{t}:{room}")` (world.py:677). The scenario
    is not part of it, so the minute-00 order is the same as the baseline: seed 1 Daniel, Leo,
    Elena, Mara; seed 2 Elena, Mara, Daniel, Leo; seed 3 Mara, Elena, Daniel, Leo (§9, command 3).
  - The cache key is model, seed, SYSTEM and prompt (gemini.py:196-198). The scenario name is not
    in it.

---

## 3. Tests

All tests run with the fake model or a scripted one, and with `GEMINI_API_KEY` unset. SENTENCE is
the sentence in §1. LINE is `"Day 3: " + SENTENCE + " (you heard it)"`.

| # | What it checks | How |
|---|---|---|
| T1 | **The sentence names nobody Leo heard** | SENTENCE contains no "Daniel", "Elena" or "Mara". Its only capitalised name is "Leo". It does not contain "eats a can", so the existing filters at test_morning.py:227 and :763 still find no night line for Leo. |
| T2 | **Only Leo's backstory differs** | For Daniel, Elena and Mara, `Person(pid, "daniel_ate_it_leo_heard").backstory == Person(pid, "daniel_ate_it").backstory`. For Leo, the new list equals the old one with exactly one line inserted: LINE, directly after the line starting "Day 3: Mara freezes". No Leo line contains "Daniel eats". |
| T3 | **At minute 00, only Leo's prompt differs from `daniel_ate_it`** | Build a fresh `Morning` for each scenario with the same seed. For every person, compare `prompt_for(p, 0, options_for(p))`, `p.sure` and the option ids. They must be equal for Daniel, Elena and Mara. For Leo, `sure` and the options are equal. The line diff of the two prompts (`difflib.ndiff`) has exactly one added line, `"- " + LINE`, and no removed line. |
| T4 | **Daniel's prompt never mentions being heard** | Fake-model mornings of `daniel_ate_it_leo_heard`, seeds 1, 2 and 3. No prompt starting "You are Daniel," contains SENTENCE, "wakes and hears", "open a can", "does not see who" or "heard someone". Every Daniel prompt that has the conscience line still contains "and nobody saw". (Fake words are `[fake line N]`, gemini.py:164, so any such text could only have come from the rules.) |
| T5 | **No prompt says who Leo heard** | Same fake mornings. (a) SENTENCE appears in every prompt starting "You are Leo," and in no other prompt. (b) In each Leo prompt, the line holding SENTENCE is exactly `"- " + LINE`, with nothing added. (c) No Leo prompt contains "Daniel eats a can", "you ate it yourself" or "On your conscience". (d) No prompt contains "Daniel" and "open a can" on the same line. |
| T6 | **Nothing from target-morning reaches the new prompts** | Run the check of test_morning.py:199-222 over the fake prompts of the new scenario as well as the default one. |
| T7 | **The existing scenarios are unchanged** | For `daniel_ate_it`, `mara_ate_it` and `miscount`, no backstory line contains SENTENCE, and `backstory(s)` has the same length as before the change (13, 13, 12). The full suite passes. |
| T8 | **The scenario runs end to end** | `test_each_scenario_runs_with_the_fake_model` (test_morning.py:746) already loops over `data.SCENARIOS`, so it covers the new name. Add a check that the story holds the table row given in §2. |

---

## 4. Run plan

Run mode only. Run from `Prototypes/llm-morning/`, one seed at a time, on the default model
(`gemini-3.5-flash-lite`, config.json `model`), output `v6`.

**Before any API call**

- **R0.** HEAD holds the implementation of §2 and the tests of §3. `git status --porcelain` shows
  nothing tracked as modified. The untracked baseline files (runs/v6/, cache/v6/,
  reports/baseline_v6.md) are present. No `runs/v6/daniel_ate_it_leo_heard-*` or
  `cache/v6/*daniel_ate_it_leo_heard*` exists yet.
- **R1.** Run `env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning` and expect
  exit 0.
- **R2. Is the baseline still reproduced?** For N = 1, 2, 3, run
  `.venv/Scripts/python.exe morning.py --seed N --replay`. Expect exit 0, "IDENTICAL", and 0 API
  requests. Delete the three `runs/v6/daniel_ate_it-seedN.replay.md` files the check writes.
- **R3. Paired start.** Copy the baseline answers into the new run's cache:
  `cp cache/v6/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seedN.json`.
  - **Why.** The cache key is model, seed, SYSTEM and prompt. Any prompt identical to a baseline
    prompt then gets the baseline's answer instead of a fresh draw at temperature 1.0 (config.json).
    The two runs therefore match exactly until Leo's knowledge first changes something, and differ
    only from there. Without this, the minute-00 acts of Daniel, Elena and Mara would be fresh
    draws and could differ from the baseline by chance alone.
  - **What it costs.** The meta's `answers_from_cache` becomes non-zero. That count is reported
    as the length of the shared start.
  - **If a fully fresh run is wanted instead.** Skip R3. That costs about 7 more requests and
    loses the pairing.

**Runs**

```
.venv/Scripts/python.exe -u morning.py --scenario daniel_ate_it_leo_heard --seed 1 > runs/v6/daniel_ate_it_leo_heard-seed1.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --scenario daniel_ate_it_leo_heard --seed 2 > runs/v6/daniel_ate_it_leo_heard-seed2.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --scenario daniel_ate_it_leo_heard --seed 3 > runs/v6/daniel_ate_it_leo_heard-seed3.stdout.txt 2>&1
```

- A seed that exits 3 (quota, rate limit or call cap) is resumed with the same command once the
  limit has passed. The cache keeps its answers (morning.py:71-78).
- The next seed does not start until the current one has exited 0.

**Request estimate**

- **Baseline.** 45 + 66 + 25 = 136 requests (baseline_v6.md, table "Runs").
- **Reused at minute 00 by R3.** Every act before Leo's first act: 1 in seed 1, 3 in seed 2 and
  3 in seed 3, so 7 in all.
- **Expected.** About 130 requests for the three seeds. Plan for 70–250, since Leo's knowledge
  may start more talk (seed 2 of the baseline, with open accusations, used 66).
- **Hard ceiling.**
  - The Oracle stops a morning when cached answers plus requests reach 150 (config.json
    `max_calls_per_morning`, gemini.py:242-244). The client counts every attempt, retries
    included (gemini.py:105-109).
  - So at most 450 requests for the three seeds. The free quota is 500 a day.
  - Start only on a day when the quota has not been used for anything else.

**After each run**

- **R4.** Exit code, meta totals and the console output, in the same format as the baseline report.
- **R5. Minute-00 check on the real prompts.** Take Leo's minute-00 prompt from the new cache (the
  entry for "You are Leo," with "Now, minute 00,") and from the baseline cache. The line diff must
  be exactly one added line, `"- " + LINE`, with nothing removed.
  - This holds if Leo's minute-00 so_far matches the baseline, which R3 ensures.
  - If it fails, the seed is reported as not paired at minute 00, and the extra lines are shown.
- **R6. Was the line ever trimmed?** Every Leo prompt in the new cache that is not also in the
  baseline cache (in other words, every prompt Leo was sent in this run) contains SENTENCE. Report
  the count and any exceptions.
- **R7. Where the runs part.** The first act where the new transcript and the baseline transcript
  differ (minute, who, option, words), per seed.
- **R8. The counts.** P1–P4 and D1–D2, each as a PASS/FAIL line with the evidence rows.

**What run mode delivers:** runs/v6/daniel_ate_it_leo_heard-seed{1,2,3}.{md,transcript.json,meta.json,stdout.txt},
cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed{1,2,3}.json, and a report
reports/witness_v6.md.

---

## 5. Predictions (frozen, verbatim from the brief)

  P1. Leo refers to the night (in words or reason) in at least 2 of 3 seeds.
  P2. Someone questions or accuses Daniel directly in at least 2 of 3 seeds
      (baseline: 1 of 3). Define "directly" from the available options.
  P3. In at least 2 of the seeds where P1 holds, Leo's first act that refers
      to the night is not an accusation.
  P4. No seed has more target-morning "Never" items than the same seed in
      the baseline (baseline: 3, 3, 2).

### Terms used by every rule

- **Act.** A transcript act (`runs/v6/<scenario>-seedN.transcript.json`, `turns[].acts[]`) whose
  `mode` is not `routine`.
- **Order.** Acts are taken in `said_at` order.
- **Words.** The act's `words`.
- **Reason.** Taken from the matching decision line in the story `.md` (`Reason: “…”`), matched by
  minute, name and order, as in baseline_v6.md "Model-decided acts".
- **Fallback acts.** They have no model words or reason, so they can never "refer to the night".
  They still count by their option under P2 (A).
- **The reader.** The person who marks the lines that need reading. The run report drafts every
  mark with its quote. A mark stands unless the user changes it, and any change is recorded in the
  report.

### P1: counting rule

- **"The night".** The night the can went: day 3's night, before the morning count.
- **"Refers to the night".** The act's words or reason speak of that night, of waking or sleeping
  then, or of a sound, someone, or a can being opened before the count.
- **What does not count.** References to Leo's other backstory lines that contain "night". These
  are "Mara cries in the night" and "why crossing at night gets someone killed".
- **Procedure.**
  1. List **every** Leo act in the seed with its words and reason. There are 10, 15 and 6 in the
     baseline.
  2. Screen with this case-insensitive pattern:
     `\b(night|nights|woke|wake|waking|awake|asleep|sleep|slept|sleeping|dark|noise|noises|sound|sounds|opened|opening|heard someone|i heard|you heard)\b`
  3. The reader marks each Leo act yes or no, the pattern hits and all the others alike. Each mark
     is recorded with the quote and one of two notes: "from what he heard" or "general inference"
     (for example "someone must have taken it in the night"). The note is for information only.
     Both count as yes.
- **A seed holds P1** if at least one Leo act is marked yes.
- **PASS** if P1 holds in at least 2 of 3 seeds.
- **Calibration on the baseline.** The pattern gives 0 hits in each of seeds 1, 2 and 3 (§9,
  command 3).

### P2: what "directly" means, and the counting rule

There is no option to ask one person a question. Options are listed at world.py:316-374. Every
option aimed at a single person is `accuse_<x>`, `reassure_<x>`, `sit_<x>` or `aside_<x>`. Only
`accuse_daniel` is about the can. A question to Daniel can therefore be carried only by the words
of a speech option. "Directly" is either of these:

- **(A) Accusing.** Any act with option `accuse_daniel`. Mechanical.
- **(B) Questioning.**
  - The act has option `ask_who` or `say_other`, by anyone other than Daniel.
  - Its words contain "?".
  - Its words are aimed at Daniel alone: they contain "Daniel", or the act's `audience` is
    exactly `["daniel"]`, as in a talk taken aside.
  - The reader confirms the question is about the can, the food or the night. This screens out,
    for example, "Daniel, can you calm down?".
  - `deny` and `reassure_*` are excluded, because their words defend or comfort. An example is
    Mara's baseline deny "…Daniel, why do you keep blaming me for everything?" (seed 2, min 21).
- **A seed holds P2** if it has at least one (A) act or at least one confirmed (B) act.
- **PASS** if P2 holds in at least 2 of 3 seeds.
- **Calibration on the baseline.** Seed 1: 0. Seed 2: 10 (A) acts, all by Mara (first at
  min 12). Seed 3: 0. That is 1 of 3, which matches the brief's baseline figure (§9, command 3).

### P3: counting rule

- **Which seeds.** Only the seeds where P1 holds.
- **Which act.** In each, take the **first** Leo act (in `said_at` order) marked yes under P1.
- **When that act is an accusation.**
  - Its option is `accuse_<anyone>`.
  - Or its option is `say_other` and its words state as fact that a named person took or ate the
    can, with no question mark. The reader confirms this case.
- **A seed counts toward P3** if that first act is not an accusation.
- **PASS** if at least 2 seeds count.
- If P1 holds in fewer than 2 seeds, P3 cannot reach 2 and is reported as **FAIL (fewer than 2
  P1 seeds)**.

### P4: counting rule

- **Scoring.** A reader scores each new story against the 13 items of target-morning.md §1
  "Never", using one sheet with one row per item.
  - Each row says present or absent.
  - For each item present, the row gives at least one minute and quote.
- **The count** is the number of items present (0–13). An item counts once however often it
  appears.
- **PASS** if the count for seed N is at most the baseline figure for seed N, for every N, where
  the baseline is 3, 3, 2 as frozen in the brief.
- **The baseline breakdown is not in the repository.** Which items make up 3, 3 and 2 is
  **NOT FOUND** (§9, command 6). So the run report also scores the three baseline stories with the
  same sheet in the same pass, and prints both.
  - The verdict uses the frozen 3, 3, 2.
  - If the rescored baseline differs from 3, 3, 2, the difference is reported next to the verdict.
    It does not change the verdict.

## 6. Designer's additional predictions (not part of the frozen set)

- **D1.** Leo's `suspects` is someone other than `nobody` in at least one of his acts, in at least
  2 of 3 seeds.
  - Baseline: 0 of 3, with `nobody` in all 31 of Leo's acts (§9, command 3).
  - Counted from the transcript `suspects` field for `who` = `leo`.
- **D2.** In at least 1 seed, Leo speaks of the night aloud: an act marked yes under P1 because of
  its **words**, not only its reason.
  - Counted from the P1 sheet.

## 7. What this design does not decide

- **The baseline files are untracked.** `git status` shows runs/v6/, cache/v6/ and
  reports/baseline_v6.md as untracked. This design depends on them (R2, R3, R5) but does not
  commit them, because the brief scopes this step to the design file.
- **Leo's prompts grow by about 37 estimated tokens** (the 133-character line / 3.6; 1319 to 1356 in seed 1) for the whole morning. So
  when his prompt is over budget, one more memory entry may be trimmed than in the baseline. This
  is part of the difference being tested and is not separated out.

## 8. Existing code this design relies on

| What | Where |
|---|---|
| backstory lines rendered with "(you did/saw/heard it)" | world.py:201-202 |
| opening and culprit `sure` lines | world.py:263-267 |
| conscience line "…and nobody saw" | world.py:449-452 |
| prompt assembly and trimming order | world.py:522-545 |
| option list | world.py:316-374 |
| turn order draw | world.py:677 |
| budget and estimate | world.py:51, 71-72 |
| scenarios, backstory, night placement | data.py:102-117, 128-160 |
| cache key | gemini.py:196-198 |
| call cap counting cached answers | gemini.py:242-244 |
| requests counted per attempt | gemini.py:105-109 |
| fake words | gemini.py:164 |
| run file names | morning.py:46-47 |
| `--scenario` choices | morning.py:136 |
| story's "heard it" | story.py:10 |
| story's backstory table | story.py:233 |

---

## 9. Commands run and output

All commands were read-only. The two scratchpad scripts are not in the repository.

**1. Files read and their sizes**
```
$ wc -l reports/baseline_v6.md reports/knowledge_audit.md data.py ../../Docs/understanding/target-morning.md
  437 reports/baseline_v6.md
  550 reports/knowledge_audit.md
  170 data.py
   71 ../../Docs/understanding/target-morning.md
 1228 total
```

**2. How the scenario reaches seeding and the story**
```
$ grep -n -E "random|Random|seed" world.py | head -20
18:import random
240:    def __init__(self, oracle, seed=0, scenario=data.DEFAULT_SCENARIO):
242:        self.seed = seed
261:        self.transcript = {"seed": seed, "scenario": scenario, "culprit": self.culprit, "turns": []}
641:        return pid, "drawn by the seed among equals"
677:            rng = random.Random(f"{self.seed}:{t}:{room}")
678:            draw = {q: rng.random() for q in data.ORDER}
$ grep -n "heard it\|(you heard" world.py story.py
world.py:918:                                  "(you heard it)")
story.py:10:DAYS_KNOWN = {"did": "did it", "saw": "saw it", "heard": "heard it"}
```
(The seed grep also printed line 7, a docstring line; the heard grep also printed world.py:325, a comment. Both are omitted here.)

**3. Calibration of the counting rules on the baseline, and Leo's backstory kept**

Script: `<scratchpad>/witness_calibrate.py`. It reads runs/v6 and cache/v6 only.
```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/witness_calibrate.py .
== seed 1
  min 00 order: ['daniel', 'leo', 'elena', 'mara']
  P1 Leo night-pattern hits: 0
  P2 direct acts at Daniel: 0
  Leo suspects values: ['nobody']
  asides: []
== seed 2
  min 00 order: ['elena', 'mara', 'daniel', 'leo']
  P1 Leo night-pattern hits: 0
  P2 direct acts at Daniel: 10
    (12, 'mara', 'accuse_daniel', 'A', "You went through my bag like I was a criminal, Daniel, maybe you're the one who hid it.")
    (15, 'mara', 'accuse_daniel', 'A', 'You think you can just search my things and act innocent, Daniel, but I know it was you.')
    (24, 'mara', 'accuse_daniel', 'A', 'You keep accusing me when you are the one hiding things, Daniel.')
    (27, 'mara', 'accuse_daniel', 'A', "You always pin it on me because you think I won't fight back, Daniel.")
    (30, 'mara', 'accuse_daniel', 'A', 'You are the one who took it, Daniel, I know you did.')
    (36, 'mara', 'accuse_daniel', 'A', 'You always blame me for everything, Daniel, and I am sick of it.')
    (39, 'mara', 'accuse_daniel', 'A', "You can't prove a single thing, Daniel, stop looking at me like that.")
    (54, 'mara', 'accuse_daniel', 'A', 'You keep accusing me because you are trying to hide what you did, Daniel.')
    (66, 'mara', 'accuse_daniel', 'A', 'You keep accusing me because you are trying to hide what you did, Daniel.')
    (69, 'mara', 'accuse_daniel', 'A', 'You keep accusing me because you are trying to hide what you did, Daniel.')
  Leo suspects values: ['nobody']
  asides: []
== seed 3
  min 00 order: ['mara', 'elena', 'daniel', 'leo']
  P1 Leo night-pattern hits: 0
  P2 direct acts at Daniel: 0
  Leo suspects values: ['nobody']
  asides: []
== Leo backstory lines kept per cached prompt (cache/v6)
  seed 1: Leo prompts 10, backstory lines kept min 4 max 10, prompts with fewer than 3 kept: 0
  seed 2: Leo prompts 15, backstory lines kept min 4 max 10, prompts with fewer than 3 kept: 0
  seed 3: Leo prompts 6, backstory lines kept min 4 max 10, prompts with fewer than 3 kept: 0
exit=0
```
The script's (B) screen covered `ask_who` and `say_other` only, as the P2 rule does.

**4. Token estimate of Leo's minute-00 prompt with each wording**
```
$ grep -n "def estimate_tokens" -A2 world.py
71:def estimate_tokens(text):
72-    return int(len(text) / 3.6) + 1
73-
$ .venv/Scripts/python.exe -c "<insert each wording after '- Day 3: Mara freezes' in the baseline Leo min-00 prompt; print estimate_tokens(SYSTEM+prompt) before and after>"
132 [(1319, 1363), (1360, 1404), (1361, 1405)] In the night Leo wakes and hears someone in the kitchen, then a can being opened. He does not get up, and he does not see who it is.
117 [(1319, 1359), (1360, 1400), (1361, 1401)] In the night Leo wakes and hears someone in the kitchen and a can being opened. He stays in bed and does not see who.
108 [(1319, 1356), (1360, 1397), (1361, 1398)] In the night Leo wakes, hears someone in the kitchen and a can being opened, and does not get up to see who.
108 [(1319, 1356), (1360, 1397), (1361, 1398)] In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who.
```
The last wording was chosen. Of the two 108-character wordings, it is the one that states "does
not see who" outright.

**5. Leo's minute-00 memory section with the line inserted (seed 3)**

The output is the block shown in §1, followed by `108`, the length of the sentence.

**6. Is a per-item Never count for the baseline recorded anywhere?**
```
$ grep -rn -E "Never" --include=*.md Prototypes/llm-morning/reports Docs | grep -v "target-morning.md" | head -20
(20 lines. None is a count for runs/v6. The llm-morning ones are reports/state/05_results_quality.md,
which quotes target-morning and records Never items for REPORT-2/3/4 runs, and
reports/state/04_decision_pipeline.md:84, "Never falls.")
$ grep -rln "3, 3, 2" Prototypes/llm-morning Docs
Prototypes/llm-morning/.venv/Lib/site-packages/pyasn1_modules/rfc5639.py
$ git status --porcelain
?? Prototypes/llm-morning/cache/v6/
?? Prototypes/llm-morning/reports/baseline_v6.md
?? Prototypes/llm-morning/runs/v6/
```
The per-item breakdown of the baseline's 3, 3, 2 is NOT FOUND. The only file containing "3, 3, 2"
is a library file in .venv.
