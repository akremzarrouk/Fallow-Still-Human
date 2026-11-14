# The code-brain prototype as built

Written 14 Nov 2026 for whoever works on this next (a person, or a smaller model). It describes the code as it is
at commit `714fcd8` on branch `quiet-day-stage-a`, not the plan. The plan and its reasons are in
`Docs/fable-audit-2026-11.md` (sections 7 to 9 and the changelog); the day-by-day record is `reports/journal.md`.

## 1. What it is

A week in a shut house, four people (Elena 42, Daniel 25, Leo 21, Mara 17), a can missing from the shelf. **No
model is called anywhere while the game runs.** Code decides what every person does; what they say is read from a
file. The player is Leo.

```
python week.py --seed 2          # plays a week by code alone, prints one line per act
python diary.py --seed 2         # the same week as a page a day: runs/week/week-seed2.md
python hour.py --seed 2          # play the week as Leo in a terminal
python hour.py --seed 2 --script kind     # a script plays Leo; prints the end page
```

Use the project's interpreter: `.venv/Scripts/python.exe`. The same seed gives the same week, byte for byte; with
a player, the same seed and the same choices do.

## 2. The layers

| Layer | Files | What it owns |
|---|---|---|
| **Truth** | `world.py` (the day's turns, options, what an act does), `quiet.py` (the full day: routines, rest, the beats, the door), `night.py` (bedtime, the door at night, the trip and its odds), `truth.py`, `water.py`, `weather.py`, `street.py`, `health.py` | What happened, who perceived it, bodies, water, the shelf, the street. Nothing here decides for a person in code mode. |
| **The brain** | `brain.py` | What a person does: every offered move scored from facts about that person; the best open one taken. Also the day's mood, the topics of lines, and the night step. |
| **The heart** | `heart.py` | What each person remembers of each other (acts with a weight and a day), trust as their sum, suspicion from clues, one intention each. |
| **Content** | `content/weights.json`, `lines.json`, `practices.json`, `chances.json`, `voices.md` | All numbers and all words. Behaviour is changed here before it is changed in code. |
| **The week** | `week.py` | Seven days and six nights in order; reading a week (its acts, its empty days, its world events). |
| **The diary** | `diary.py` | A played week as text. Invents nothing: every sentence is built from the record. |
| **The player** | `hour.py`, `player.py` | Leo's screen, his choices, saving, the end page. |

**Code mode** is switched on by giving the run a `CodeBrain`: `Morning.brain()` then returns it, and the three
places that used to ask a model (`world.Morning.ask_model`, `night.Night.ask`, `mind.NightMind.run`) ask the brain
instead. `brain.full_days = True` (set by `week.run`) makes every day a full day with beats.

## 3. One decision, step by step

1. **The engine offers moves.** `world.Morning.options_for(p)` lists what `p` could do now (speak, sit with
   someone, search, eat, set out the meal, take a task, go to a room …). Each is an `Option` with an id
   (`reassure_mara`), a label, whether it is speech, and its `act` fields.
2. **The brain builds what `p` can see.** `CodeBrain.context_of` makes a `ctx` with the World out of reach
   (`truth.prompting()`): the day, the minute, the room, who is there and how they look, the shelf as `p` last saw
   it, who is missing, the hour's business (`beat`). The brain never reads who took the can, or another person's
   inside.
3. **Facts.** `facts(p, ctx)` gives numbers from 0 to 1 about `p` (traits, hunger, what was asked, whether they
   took it, whether they have slept …). `target_facts` adds the ones that depend on whom the move is aimed at
   (trust, a fresh hurt, thanks due, whether they are angry with them today …).
4. **The rule.** For each option, `key_of` names its move (`reassure`, `say_to`, `meal_small` …). The first rule
   of that move in `weights.json` whose `when` facts all hold is used. Score = `base` + Σ weight × product of the
   named facts, plus a small tilt from the day's mood. No rule: the default score. Staying as they are: `stay`.
5. **Open or not.** A move is closed if it has been made as often as its `once` rule allows (`day`, `week`,
   `accuser`, `convo`, or `cause`: open again only when what stands behind it has changed, and the record names
   the change), or twice already today.
6. **The choice** (`choose`). The best open move; a seeded draw only among moves within `band` of the best;
   staying wins outright when it is the best. A *spoken* move is skipped if every way of saying it has been used in
   this scene by someone else, or by the speaker today.
7. **The words.** `topic_of` says what the line is about (`confront:lied`, `say_to:thanks`, `object:resigned`)
   and marks what has now been said. `line` picks a variant from `lines.json`: the speaker's own before the
   default, the topic before the plain move.
8. **The act happens.** `world.Morning.apply` changes the world and tells everyone in the room what they saw.
   `CodeBrain.saw` then records what each of them will remember (`heart.remember`) and notes for tomorrow's mood.
9. **The record.** Each act in the transcript carries `why`: its three largest terms in plain words
   (`weights.json`, `words`), a `new_cause` if it was a repeat, and its `topic`. The diary and Leo's screen read
   this.

Once a night `CodeBrain.night_step` settles things: who defied whom, who brought food, grudges nobody renewed
dropping a step, intentions renewed or dropped (with a line), guilt growing when unsaid, sickness taking its course.

## 4. `content/weights.json`

- `stay`, `default`, `band`, `tilt`, `cap_per_day`: the five numbers of the choice.
- `scenario`: 16 portions, how far a portion pushes hunger back, how fast hunger rises.
- `keeper` (`elena`): whose it is to set out the food. `keeps_going`: who does not sleep off one night without
  sleep.
- `moves`: for each move, a list of rules. A rule has `when` (facts that must hold; `!fact` for must not),
  `base`, `terms` (`[weight, fact, fact…]`), and optionally `once` with `once_key`, `subject` (for `once:
  "cause"`), `limit`, `limit_short_handed`, `topic` (which line family it speaks), `cause_named` (a repeat's own
  condition is its new cause, said in the record), `subject_of` (the move counts for another rule's once-is-enough).
- `quirks`: one person's own additions to one move.
- `heart`: the acts people remember and their weights (a `mark` does not fade), the clues, the intentions, whom
  each would confide in.
- `causes`, `moods`, `words`: the plain words for a new cause; what each mood tilts; the plain words of each fact.

A new fact needs code (`facts` or `target_facts`); a new weighing of existing facts does not.

## 5. The day and the night

- **Beats** (`quiet.BEATS`): 07:00 the morning, 10:00 the work, 15:00 the afternoon, 19:00 the evening. At a beat
  everyone who is up comes to the kitchen and the room is played turn by turn (3 minutes a turn) until its talk
  ends. Between beats people follow routines (sit, rest, keep to their room).
- **Meals:** at the morning and the evening, a share each (half a portion; a quarter when the shares are cut);
  when the shelf is empty, a cup of water each. Everyone served decides at once what to do with their share.
- **The work** (`practices.json`): boards, water, watch, stores, and looking after whoever is sick or hurt. Some
  work can hurt (`chances.json`, all estimates).
- **Rest:** sleep debt makes people lie down (`quiet.py`). Whoever was up all night sleeps through the work
  (`CodeBrain.sleeps_through`).
- **The night** (`night.py`): each chooses at bedtime (sleep, lie awake, sit up by the door, go out). Someone who
  sees or hears another leave reacts. The street decides from its own table (`NEAR_ALONE`, `FAR_ALONE` …). Leo is
  never lost: if he draws "not back" he comes back hurt, and the record says so (`g["spared"]`).

## 6. The house's rules, as built (steps 4b and 4c)

These are in `brain.py` and `weights.json`, each because a real family would:

- Told in private who took the can, a person tells the others; each has it out in their own words.
- In an hour in which a blow fell, small talk waits. Nobody thanks, tends or feeds someone they are angry with.
- The food is Elena's to set out; another does it to make amends, or when she is worn out.
- She cuts the shares when less than three days of full meals are left, and says so.
- The one who took the can does not take from the shelf again, and does not scold anyone for it.
- An offer to go out is tied to the can once it is owned up to; with someone missing, it is to look for them.
- Nobody forbids the same person twice by day. Whoever said no that day and sees them go says so at the door;
  whoever was walked past at the door once goes with them the next time.
- With someone missing, one person watches the street in the morning.
- Nobody searches, or looks out at a knock, where they just watched someone do it.
- One voice is enough for a wrong, except the lie, which each was told to their own face.
- Comfort among the people in a room: once in a part of the day, unless there is news for the whole house.
- No sentence is said by two people in one scene.

## 7. Leo's hour (`hour.py`)

`HourPlayer` builds each screen from the engine's own view of Leo (`world.Morning.player_view`) and
`CodeBrain.rank` (the offered moves, best first, each with the words Leo would say). It shows at most seven
choices; asks Leo only when the moment calls on him (`calls`); hides what a sick or hurt body cannot do
(`limits`); and adds "Because of what you did" from the others' `why`. Choices are saved to
`runs/hour/seed<N>.json`; resuming replays them. `end_page` reads the heart.

## 8. Tests

Run **one at a time**; the machine once crashed from memory. `capped.py` stops a run that goes over a time or
a memory limit (Windows only):

```
python capped.py . 300 600 test test_brain test_heart     # unittest modules, 300 s, 600 MB
python capped.py . 120 400 run diary.py --seed 2          # a script
```

The output of the last full run is in `reports/handoff_tests.txt`.

| File | What it holds | Time |
|---|---|---|
| `test_brain.py` | Section 10's frozen cases B1 to B17. **Not to be edited** to make them pass. | 20 s |
| `test_heart.py` | Step 2's cases H1 to H25. | 5 s |
| `test_llm_off.py` | The LLM-off test, L1 to L13, on the week. Must stay under 60 s. | 30 s |
| `test_diary.py` | D1 to D5. | 8 s |
| `test_hour.py` | Leo's hour, and L9 on three seeds. | 30 s |
| `test_morning.py` | The old suite (the model path, with a fake client): 349 pass, 141 skipped. | 150 s |

`python week.py --count 50` counts empty days over 50 weeks (about 90 s).

## 9. What is old, and still runs

`gemini.py`, the prompt text in `world.py` (`prompt_for`, `inside_lines`, `now_lines`), `mind.py`'s night mind,
`morning.py`, `play.py`, `story.py`, `memory.py`, the `metrics*.py` and probe scripts, `v1/` and later frozen
copies, and the retired tests in `test_morning.py` belong to the model path. In code mode some of it still runs
for nothing (the day's carry-in text is built every morning). `CLAUDE.md` forbids editing the frozen copies and
asks for the retired tests of an area to be ported before that area changes; in this work the model path was
left as it was and the old suite kept passing.

## 10. Traps

1. **Leo's own acts do not pass through `choose`.** The others remember them (`saw`), but the once-is-enough
   rules, the "forbade" record and the topic marks are not kept for the player's Leo. A script or a player can
   repeat what a code person could not.
2. **A line must not state what the record might not hold.** Lines say what the move is. "I know which way" was
   written and taken out. Slots (`{to}`, `{gone}`, `{left}`, `{culprit}`, `{He}`) are the only facts in a line.
3. **Some text is parsed.** `night.carry_in` looks for " admitted taking the can: " in a person's sure lines; a
   differently worded line crashed a run.
4. **The weak-body shift never applied.** `night.body_shift` moves the street's odds for a weak or exhausted
   body; over 115 trips in 50 weeks it applied to none. Not looked into.
5. **`weights.json`'s words name Elena** in two places ("it is Elena's to set out").
6. **`diary.KNOWN`** is a module-level flag reset by `render`; calling `sentence` or `why_of` outside `render`
   reads a stale value.
7. **A Windows console** cannot print the screens' quotes in cp1252; `hour.main` switches stdout to UTF-8.
8. **Bash heredocs with apostrophes** fail in this shell: write a script file and run it.
9. **A quarrelsome Leo is asked far more often** (up to 179 choices in a week by script), because each quarrel
   calls for answers.
