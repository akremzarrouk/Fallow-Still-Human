# Playing Leo, fix 1: speech heard as words, say_to, no deny for who knows, the screen's order, the food line

Mode: implement. The fix answers what the first play session showed (`runs/play/daniel_ate_it-seed2-20261014T143852Z/`,
`shown.md` and `play.jsonl`):
- Daniel's "Leo, you have no right to blame her" (act `accuse_leo`) was shown as "Daniel accuses you of taking it".
- Mara's anger at Leo came out as `accuse_daniel`.
- Nobody could answer Leo's question.
- "deny taking it" was offered after Daniel confessed.
- Lines of the same minute were out of order, and the confession was shown twice.

No live call was made. Every run here used the fake model, with `GEMINI_API_KEY` cleared. Paths are relative to
`Prototypes/llm-morning/`. Raw outputs are in `runs/play_fix1/`.

## Result

- **The five new tests (`test_morning.PlayFix1Test`) were seen failing, and pass after the change** (§3).
- **The full suite passes:** 345 tests, OK (skipped=145), with 0 failures and 0 errors (§5).
- **145 replay tests are retired as skipped, by the user's decision** (§5, §8). The change alters day 1's prompts, so
  these tests miss the caches of earlier real runs (v6, v10, v11, v12, v16) that they replay. One more compares with the
  frozen v9 code's prompts. No live call can re-record them here.
- **The fake 4-day run** (`morning.py --seed 1 --fake --days 4`) **exits 0** (§6). Its story and transcript sha256 are
  the new baseline for later steps:
  - story `b1bbe7f29147bec5d46abe97761c378790f008eee51cb21085d4ed62e1e09160`;
  - transcript `6656351aacc3bee941097b56a6ca91044bf850c600459e40f90e0c0d2371d1c1`.
  They differ from S3's (`949bd5ab…`, `7d20b518…`), as expected.

## 1. What changed

**1. Speech is heard as words** (`world.py:1791-1816`, `spoken_to` and `line_text`). Every line a speech act writes
shows who spoke, to whom and the words. This covers a hearer's memory, the "Said and done … this turn" list in a prompt
and on Leo's screen, the transcript's `said` text and the story built from it. The act's gist is never shown:
- `Daniel, to you: "Leo, you have no right to blame her."`
- `Daniel, to Leo: "…"` (to a third person)
- `Elena, to everyone: "…"`

The addressee is decided as follows:
- **An aimed act** (accuse, reassure, confront, back, object, say_to) names its target.
- **A tell** names its listeners.
- **At the front door:** `door_call` is "through the front door", or "to the person on the step" when the door is open.
  `door_refuse` is "to the person at the front door".
- **Everything else** is "to everyone".

The act still drives every code effect: addressed, `accused_by`, `heard_question`, Newness, guilt, grudges, the trip
record, `knows_culprit` and the chronicle. The C1 test still asserts `accused_by == {"leo": 3}`, and fix 1's test
asserts `accused_by == {"daniel": 0}`.

Other details:
- **"Said and done … this turn"** is now kept per hearer (`world.py:1893-1898`, read at `world.py:1257`). The one spoken
  to reads "to you", where before they read their own name.
- **Non-speech acts with words** keep their form: `Mara says to everyone, while searching: "…"`.
- **Removed:** the old gists (`FAR_GIST`, `trip_gist`, the per-kind branches of `line_text`). Nothing else used them.
- **Leo's echo on his screen** follows the same form: `you, to everyone: "…"`, `you, to Mara: "…"` (`player.py:90-104`).
  A non-speech act keeps `you searched, saying: "…"`.
- **Not changed:**
  - The speaker's own memory line, without words, as before: `you accused Mara.` (`reports/repetition_probe.md`,
    variant B). It is the speaker's record of their own act, not something heard.
  - The night's low-voice lines, which already show the words.
  - The code's own summaries: the pattern block's "In that time: Daniel accused you", the grudge facts, "About going
    there tonight: …", and the "What you know" line "Daniel admitted taking it at minute 15". These are conclusions the
    code draws from the act, not lines the act writes.

**2. `say_to_<p>`** (`world.py:643-645`, `talk.py:35-36`, `talk.aimed_at`). Each other person in the room gets
`say_to_<p>`, labelled "say something to <name>", right after `say_other`. It is offered to everyone, the player
included. Its kind is `say` with a target, so:
- the addressee is spoken to: `addressed` is set, so they are ordered first next ("just spoken to by Leo");
- the line is a trigger for them, and counts like a reassurance: not new (Newness `say`);
- it carries no meaning about the can, so no `accused_by`, `heard_question`, guilt or grudge;
- the speaker's own line is `you spoke to Mara.`;
- the chronicle's gist is "speaking to Mara" (`chronicle.py:34-35`);
- the repetition guard treats it as `say`, as `say_other` is.

**3. No deny for who knows** (`world.py:613`). `deny` is no longer offered to anyone who knows *someone else* took the
can (`knows_culprit` set to another person). In the code, the one who took it "knows who took it" from the start
(`world.py:345`). Read literally, the request would have taken his lie away before he confesses. He keeps `deny` until
he confesses, as before. The argument against: would someone who heard Daniel admit it say "I didn't take it"? Only if
accused, and once they know, accusations are only offered against the one who took it (`world.py:616-617`).

**4. The screen's order and a heard confession once** (`world.py:320-354`, `player.py:126-147`).
- Each person's `sure` is now a `Sure` list. It records, for each line, how many memory lines came before it (`after`),
  and keeps that through `copy.copy` and `copy.deepcopy`. `Person.sure` is a property whose setter wraps any list, so
  `night.py`'s two assignments keep working.
- The view carries `sure_after`. The screen sorts by (minute, place among the memory lines), so a minute's lines appear
  in the order they happened. Day 1's count, added before any memory line, stays first.
- A heard confession's sure line (`… admitted taking the can: "…" (you heard it)`) is left off the screen, since the
  heard line shows it. It stays in `p.sure`, in the prompts and in the `l` view, and `night.py` still parses it.
- Beliefs still come first at their minute (days 1 and 2 have none).
- The "Said and done in the kitchen this turn" list under Now still repeats this turn's lines, as §1.2 of the design
  has it.

**5. The food line** (`data.py:181-182`). It was "About food: there is no food in the house for tomorrow." next to "2
portions on the shelf". It is now "About food: there is no food in the house but what is on the shelf; once it is
eaten, there is nothing." This is true whatever the shelf holds, 0 included. Day 2 and later keep `food_line`, which
already counts the shelf.

## 2. The five tests (`test_morning.PlayFix1Test`)

Day 1, seed 1. A scripted player plays Leo; the others are a `ScriptedClient`. A player answer the screen refuses fails
the test (`once`), where it would otherwise ask again forever. The first run of fix 2's test before this guard had to
be stopped (§7).

1. `test_fix1_speech_is_heard_as_who_to_whom_and_the_words`:
   - at minute 00, Elena asks, Daniel plays `accuse_leo` with "Leo, you have no right to blame her.", and Mara searches
     with words;
   - Leo's memory has `Daniel, to you: "…"` and `Elena, to everyone: "…"`, and Elena's has `Daniel, to Leo: "…"`;
   - Mara's line keeps `says to everyone, while searching`;
   - `accused_by == {"daniel": 0}`;
   - Leo's screens show the new line and never "accuses you";
   - Elena's minute-03 prompt holds `Daniel, to Leo: "…"`, and no prompt says "accuses Leo/you of taking it".
2. `test_fix2_say_to_one_person_is_offered_to_all_and_speaks_to_them`:
   - `act_of("say_to_mara") == ("say", "mara")`;
   - the three `say_to_*` come right after `say_other`, labelled "say something to Mara", and Elena's prompts offer
     `say_to_leo`;
   - Leo plays `say_to_mara`: Mara hears `Leo, to you: "…"` and Elena hears `Leo, to Mara: "…"`;
   - Mara has no `accused_by`, her next decision's `order_reason` is "just spoken to by Leo", and its triggers hold the
     line.
3. `test_fix3_no_deny_for_anyone_who_knows_who_took_it`:
   - Elena asks at 00 and Daniel confesses at 03;
   - deny was on Leo's screen before;
   - from minute 06 no screen of Leo's offers `deny`, and no prompt but Daniel's has `- deny:`.
4. `test_fix4_same_minute_lines_in_order_and_a_heard_confession_once`:
   - Leo says words at 03, and Daniel confesses after him in the same turn;
   - day 1's count is the first line of the first screen;
   - on the screen that shows the confession, its words appear once in "Since you last chose", after Leo's own line;
   - the lines read `you, to everyone: "…"` and `Daniel, to everyone: "…"`.
5. `test_fix5_the_food_line_is_true_next_to_the_shelf`: the trip concern starts on day 1 with 2 portions on the shelf,
   and the "About food:" line is the new one.

## 3. Failing before, passing after

```
$ timeout 300 .venv/Scripts/python.exe -m unittest test_morning.PlayFix1Test.<test> > runs/play_fix1/fail_<n>.txt 2>&1    # exit 1 each
```

**fix1** (`runs/play_fix1/fail_fix1.txt`):
```
FAIL: test_fix1_speech_is_heard_as_who_to_whom_and_the_words (test_morning.PlayFix1Test.test_fix1_speech_is_heard_as_who_to_whom_and_the_words)
    self.assertIn((0, f'Daniel, to you: "{blame}"'), P["leo"].memory)
AssertionError: (0, 'Daniel, to you: "Leo, you have no right to blame her."') not found in [(0, 'Daniel accuses you of taking it: "Leo, you have no right to blame her."'), (0, 'you stayed where you were and said nothing.'), (0, 'Elena asks everyone who took the can: "Did one of you take it?"'), (0, 'Mara says to everyone, while searching: "I will look."'), …
Ran 1 test in 0.102s
FAILED (failures=1)
```

**fix2** (`runs/play_fix1/fail_fix2.txt`), from the guard, since `say_to_mara` was not an option:
```
FAIL: test_fix2_say_to_one_person_is_offered_to_all_and_speaks_to_them (test_morning.PlayFix1Test.test_fix2_say_to_one_person_is_offered_to_all_and_speaks_to_them)
  File "…\test_morning.py", line 8951, in once
    raise AssertionError(f"refused at {screen.kind} {screen.minute}: {screen.message}")
AssertionError: refused at turn 0: Choose one of the options
Ran 1 test in 0.023s
FAILED (failures=1)
```

**fix3** (`runs/play_fix1/fail_fix3.txt`):
```
FAIL: test_fix3_no_deny_for_anyone_who_knows_who_took_it (test_morning.PlayFix1Test.test_fix3_no_deny_for_anyone_who_knows_who_took_it)
    self.assertNotIn("deny", s.options, s.minute)
AssertionError: 'deny' unexpectedly found in ['silent', 'deny', 'accuse_daniel', 'reassure_daniel', 'reassure_elena', 'reassure_mara', 'reassure_all', 'say_other', 'sit_daniel', 'sit_elena', 'sit_mara', 'aside_daniel', 'aside_elena', 'aside_mara', 'go_brothers_room', 'go_back_room', 'go_bathroom', 'eat', 'share'] : 6
Ran 1 test in 0.088s
FAILED (failures=1)
```

**fix4** (`runs/play_fix1/fail_fix4.txt`). The bug as the session showed it: the sure line first, Leo's line second, and
the confession twice.
```
FAIL: test_fix4_same_minute_lines_in_order_and_a_heard_confession_once (test_morning.PlayFix1Test.test_fix4_same_minute_lines_in_order_and_a_heard_confession_once)
    self.assertEqual(sum(confession in x for x in block), 1, "\n".join(block))
AssertionError: 2 != 1 : min 03  Daniel admitted taking the can: "I took it, I ate it in the night." (you heard it)
min 03  you said: "Somebody here knows."
min 03  Daniel admits taking it, to everyone: "I took it, I ate it in the night."
Ran 1 test in 0.099s
FAILED (failures=1)
```

**fix5** (`runs/play_fix1/fail_fix5.txt`):
```
FAIL: test_fix5_the_food_line_is_true_next_to_the_shelf (test_morning.PlayFix1Test.test_fix5_the_food_line_is_true_next_to_the_shelf)
AssertionError: 'Abou[33 chars]ouse for tomorrow.' != 'Abou[33 chars]ouse but what is on the shelf; once it is eate[16 chars]ing.'
- About food: there is no food in the house for tomorrow.
+ About food: there is no food in the house but what is on the shelf; once it is eaten, there is nothing.
Ran 1 test in 0.010s
FAILED (failures=1)
```

After the change:
```
$ timeout 300 .venv/Scripts/python.exe -m unittest -v test_morning.PlayFix1Test.<test> > runs/play_fix1/pass_<n>.txt 2>&1   # exit 0 each
test_fix1_speech_is_heard_as_who_to_whom_and_the_words (…) ... ok                      Ran 1 test in 0.111s  OK
test_fix2_say_to_one_person_is_offered_to_all_and_speaks_to_them (…) ... ok           Ran 1 test in 0.090s  OK
test_fix3_no_deny_for_anyone_who_knows_who_took_it (…) ... ok                         Ran 1 test in 0.097s  OK
test_fix4_same_minute_lines_in_order_and_a_heard_confession_once (…) ... ok           Ran 1 test in 0.106s  OK
test_fix5_the_food_line_is_true_next_to_the_shelf (…) ... ok                          Ran 1 test in 0.016s  OK
```
(One line per file, `runs/play_fix1/pass_fix<1-5>.txt`.)

## 4. Tests updated to the new form

| Test | Old expected | New expected |
|---|---|---|
| `FakeMorningTest.test_an_admission_cannot_be_taken_back` | `(3, 'Daniel admits taking it, to everyone: "It was me."')` | `(3, 'Daniel, to everyone: "It was me."')` |
| `SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn` | `1. <first> accuses <accused> of taking it: "LINE-ONE"`; `2\. \w+ (asks everyone who took the can\|says to everyone): "LINE-TWO"` | `1\. <first>, to (<accused>\|you): "LINE-ONE"` (the list is now per hearer); `2\. \w+, to everyone: "LINE-TWO"` |
| `OwnWordsTest.test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words` | `- min 00: <second> reassures you: "SECOND-WORDS"` | `- min 00: <second>, to you: "SECOND-WORDS"` |
| `TripTest.test_t7_what_each_option_does` (W1-W7) | `Daniel says someone should go to the neighbour's house tonight`; `Leo offers to go to the neighbour's house tonight` (W2, W7); `Elena says nobody should go out tonight`; `Elena says {Leo} should not be the one to go`; `Daniel says {Leo} should be the one to go`; `Leo says he will not be the one to go` | `Daniel, to everyone`; `Leo, to everyone` (W2, W7); `Elena, to everyone`; `Elena, to {Leo}`; `Daniel, to {Leo}`; `Leo, to everyone` (each then `: "<words>"`) |
| `NightTest.test_t11_the_day2_options` | `(3, 'Daniel says he still means to go tonight: "I still mean it."')`; `(6, 'Elena says you are the one who should go: "Leo should."')`; `(9, 'Leo says Daniel must stay home tonight: "Not Daniel."')`; `(12, 'Leo says he will not go: "Not me."')` | `(3, 'Daniel, to everyone: "I still mean it."')`; `(6, 'Elena, to you: "Leo should."')`; `(9, 'Leo, to Daniel: "Not Daniel."')`; `(12, 'Leo, to everyone: "Not me."')` |
| `FoodConfrontTest.test_a_confrontation_is_recorded_and_remembered_as_one` | `Mara confronts you: "<words>"` (Daniel); `Mara confronts Daniel: "<words>"` (Leo, `said` text, story) | `Mara, to you: "<words>"`; `Mara, to Daniel: "<words>"` |
| `PlayerS1Test.test_c1_leo_accuses_daniel_at_minute_03_and_who_hears_it` | `Leo accuses you of taking it: "<words>"` (Daniel's memory, his trigger); `Leo accuses Daniel of taking it: "<words>"` (Elena) | `Leo, to you: "<words>"`; `Leo, to Daniel: "<words>"` |
| `PlayerS1Test.test_c4_the_act_decides_and_the_words_are_heard` | `(0, 'Leo reassures you: "Nobody thinks it was you, Mara."')`; `(12, "Leo says to everyone: \"He said 'no'\"")` | `(0, 'Leo, to you: "Nobody thinks it was you, Mara."')`; `(12, "Leo, to everyone: \"He said 'no'\"")` |
| `PlayS3Test.test_play_py_on_scripted_stdin_reaches_night_1_bedtime` | `, saying: "Who took the can?"` | `you, to everyone: "Who took the can?"` |
| `TRIP_FOOD` (used by `without_trip_block` and the trip tests) | `About food: there is no food in the house for tomorrow.` | `About food: there is no food in the house but what is on the shelf; once it is eaten, there is nothing.` |
| `WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_his_can_line` | added `[BELIEF_LINE]`; removed `[CAN_LINE]` | added `[BELIEF_LINE, "- (earlier things, left out here)"]`; removed `[CAN_LINE, "- Day 1: Daniel boards the front windows on his own while the others watch. (you saw it)", "- nothing else yet"]` |

On the last row: the three `say_to_*` lines take some of the prompt budget, so with the witness's longer can line, Leo's
minute-00 prompt now trims his oldest backstory line, and says so. This is a consequence of fix 2, not a speech line.

Four more tests got the new form but are retired (§5), because they also replay a real cache:
- `QuietDayTest.test_far_positions_are_heard_as_what_they_are`: `line_text` of `volunteer_far`, `propose_far` and
  `decline` (`refuse_to_go`) now gives `Daniel, to everyone: "…"`. It gave `Daniel offers to go further along the street
  tonight: "…"`, `Daniel says someone should try the houses further along the street tonight: "…"` and `Daniel says he
  will not go: "…"`. The heard line `Daniel offers to go further along the street tonight: "Words of daniel at 0."`
  becomes `Daniel, to everyone: "Words of daniel at 0."`.
- `QuietDayTest.test_far_offers_read_as_offers_on_every_day`: the same two `line_text` lines.
- `DaysTest.test_n_t3_the_night_minds_prompt_exactly`: `min 03: Daniel accuses you of taking it: ".+" Then 2 more times`
  becomes `min 03: Daniel, to you: ".+" Then 2 more times`.

## 5. The suite, and the retired tests

```
$ .venv/Scripts/python.exe -m unittest test_morning > runs/play_fix1/suite.txt 2>&1
Ran 345 tests in 273.715s

OK (skipped=145)
```

How the retired tests were found:
1. **The first suite run** after the change (`runs/play_fix1/suite_first.txt`) gave 345 tests, 143 failures and 17
   errors.
2. **`runs/play_fix1/classify.py`** ran each of those 160 tests alone, with `gemini.Oracle.ask` and
   `test_morning.PairedOracle.ask` watched. It counted every prompt asked of a real model's cache (model name not
   "fake") that the cache did not hold, and every prompt a `PairedOracle` could not answer (`runs/play_fix1/
   classify_first.txt`).
3. **A second suite run**, with §4's updates, gave 130 failures and 16 errors (`runs/play_fix1/suite_second.txt`).
4. **Of those 146:**
   - 144 missed a real-run cache;
   - `OwnWordsTest.test_prompts_before_someone_has_spoken_are_unchanged` misses nothing, but asserts day-1 prompts byte
     for byte equal to the frozen v9 code's (with the same fake model). This is the same kind of guard, broken the same
     way, so it is retired with them. This goes one step past the user's words ("each replay test that misses the
     cache"), and is flagged here;
   - the witness test was updated (§4).
5. **Two tests miss a real cache and still pass**, because a fake client answers the misses. They stay in:
   - `FoodConfrontTest.test_a_confrontation_is_recorded_and_remembered_as_one` (19 misses);
   - `NightTest.test_t11_the_day2_options` (15 misses).

The 145 retired tests carry `@unittest.skip(PLAY_FIX1_RETIRED)`. The reason, at the top of `test_morning.py`, reads
"replays prompts that reports/play_fix1.md changed; no cached answer for them, and no live call to re-record". They were
marked by `runs/play_fix1/retire.py runs/play_fix1/retired.txt PLAY_FIX1_RETIRED`. A new replay cache will come from
the next live session. Each one is listed in §8, with its outcome in the first run and its misses.

## 6. The fake 4-day run

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_fix1_check > runs/play_fix1/check.stdout.txt 2>&1   # exit 0
$ sha256sum runs/play_fix1_check/fake/daniel_ate_it-seed1.md runs/play_fix1_check/fake/daniel_ate_it-seed1.transcript.json
b1bbe7f29147bec5d46abe97761c378790f008eee51cb21085d4ed62e1e09160 *runs/play_fix1_check/fake/daniel_ate_it-seed1.md
6656351aacc3bee941097b56a6ca91044bf850c600459e40f90e0c0d2371d1c1 *runs/play_fix1_check/fake/daniel_ate_it-seed1.transcript.json
```

Ten lines of day 1 in the new form, from the story's "What was said" (`runs/play_fix1_check/fake/daniel_ate_it-seed1.md`):
```
- min 00, kitchen. Elena, to Mara: "[fake line 3]" *(not new: reassurance)*
- min 00, kitchen. Mara, to Elena: "[fake line 4]" *(new: an accusation)*
- min 03, kitchen. Leo, to Elena: "[fake line 6]" *(new: an accusation)*
- min 03, kitchen. Daniel, to Leo: "[fake line 8]" *(new: an accusation)*
- min 06, kitchen. Daniel, to Elena: "[fake line 11]" *(new: an accusation)*
- min 09, kitchen. Leo, to Daniel: "[fake line 14]" *(new: an accusation)*
- min 21, bathroom. Elena, to everyone: "[fake line 26]" *(new: a question)*
- min 24, kitchen. Mara, to Leo: "[fake line 29]" *(not new: a remark (the rules cannot tell what free words add))*
- min 36, bathroom. Elena, to Daniel: "[fake line 36]" *(not new: a remark (the rules cannot tell what free words add))*
- min 45, brothers room. Daniel, to Elena: "[fake line 41]" *(not new: reassurance)*
```
The min-24 and min-36 lines are `say_to_leo` and `say_to_daniel` chosen by the fake model: "a remark", aimed. The same
form reaches the hearers' triggers, for example at day 1, minute 03: "Social moment: Elena, to Mara: "[fake line 3]";
Mara, to Elena: "[fake line 4]"; Elena looks afraid."

## 7. What went wrong on the way

- **A hang, stopped.** The first run of fix 2's test, before `once`, repeated the refused answer `say_to_mara` forever:
  `player_choice` asks again until an answer can be used. The background task was stopped, and no python process
  running `PlayFix1Test` was left (checked by command line). `once` was added so a refused answer fails the test.
- **A stash, restored.** To compare a screen's day number with the code before the change, the change was stashed and a
  debug script run on the old code. The old code has no `say_to_mara`, so it hung the same way, and the `git stash pop`
  queued after it did not run. The task was stopped, no process was left running the script, and `git stash pop`
  restored all six files (diff stat checked).
- **A bug of mine, found by fix 2's test.** In `player.screen` the new loop reused `k`, which held the day, so the first
  screen said day 0. It was renamed. Fixes 1, 3, 4 and 5 passed in that state, and all five pass after.
- **After the suite and the fake run,** `chronicle.py`'s `phrases` entry for `say` was split over two lines (style
  only). The fake run and the five tests were run again after it (§9).

## 8. The retired tests

Outcome in the first suite run after the change; prompts asked of a real-run cache it did not hold; `PairedOracle`
misses.

| Test | First run | Real-cache misses | Paired misses |
|---|---|---|---|
| `BodyTest.test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache` | error | 1 | 0 |
| `BodyTest.test_b_t1_day1_replays_from_a_copy_of_the_v12_cache` | error | 1 | 0 |
| `BodyTest.test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line` | error | 1 | 0 |
| `BodyTest.test_b_t4_when_a_food_moment_can_fire` | error | 16 | 0 |
| `BodyTest.test_b_t5_the_chance_and_the_draw` | fail | 15 | 0 |
| `BodyTest.test_b_t6_the_moments_prompt_exactly` | fail | 38 | 0 |
| `BodyTest.test_b_t7_giving_and_the_answer` | fail | 38 | 0 |
| `BodyTest.test_b_t8_what_the_others_perceive` | fail | 38 | 0 |
| `BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it` | error | 38 | 0 |
| `BudgetFixTest.test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8` | fail | 93 | 0 |
| `BudgetFixTest.test_b_a_knock_inside_a_running_stretch_gives_it_18_until_2_turns_after_the_visit` | fail | 120 | 0 |
| `DaysTest.test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone` | error | 1 | 0 |
| `DaysTest.test_n_t3_the_night_minds_prompt_exactly` | fail | 31 | 0 |
| `DaysTest.test_n_t8_day_words` | fail | 33 | 0 |
| `DecisionFormatTest.test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked` | fail | 1 | 0 |
| `DoorAfterTest.test_a_after_a_visit_its_stretch_asks_for_2_turns_at_most_and_the_10_00_q2_is_not_refused_for_the_budget` | fail | 173 | 0 |
| `DoorAfterTest.test_b_a_knock_is_deferred_unless_the_day_can_give_it_6_asks_beyond_the_evenings_owed_asks` | fail | 39 | 0 |
| `DoorHeardTest.test_a_the_visitors_first_line_is_in_the_prompt_of_everyone_who_heard_the_knock_in_words` | fail | 39 | 0 |
| `DoorHeardTest.test_b_a_child_visitors_first_line_names_the_child_and_their_age` | fail | 39 | 0 |
| `DoorHeardTest.test_c2_someone_who_heard_the_ask_and_then_only_a_later_knock_keeps_the_ask_in_their_record` | fail | 39 | 0 |
| `DoorHeardTest.test_c_a_record_states_the_need_and_the_visitor_only_as_that_person_perceived_them` | fail | 39 | 0 |
| `DoorHeardTest.test_d_no_parting_line_that_refers_to_asking_without_an_ask` | fail | 39 | 0 |
| `DoorHeardTest.test_e_a_visitor_who_stays_6_turns_is_answered_after_the_second_knock_and_no_visit_asks_more_than_18` | fail | 39 | 0 |
| `DoorMemoryTest.test_a2_the_give_first_then_the_refusal_and_each_act_only_if_perceived` | fail | 39 | 0 |
| `DoorMemoryTest.test_a3_whoever_perceived_only_the_refusal_has_only_the_refusal` | fail | 39 | 0 |
| `DoorMemoryTest.test_a_a_give_over_a_refusal_is_in_each_summary_with_the_refusal_in_the_order_done` | fail | 39 | 0 |
| `DoorMemoryTest.test_b_a_give_alone_and_a_refusal_alone_keep_their_summaries` | fail | 39 | 0 |
| `DoorMemoryTest.test_c_maras_own_line_and_her_chronicle_view_of_her_give_say_she_handed_water_out` | fail | 39 | 0 |
| `FoodConfrontTest.test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches` | error | 1 | 0 |
| `FoodConfrontTest.test_the_food_moment_line_is_the_neutral_one` | fail | 38 | 0 |
| `KnockFixTest.test_f1_a_bin_in_no_9s_yard_is_seen_by_day_from_the_houses_that_overlook_it` | fail | 93 | 0 |
| `KnockFixTest.test_f3_a_q7_stretch_ends_and_frees_its_reserve_when_nobody_in_its_room_perceives_the_door` | fail | 39 | 0 |
| `KnockTest.test_t2_stocks_are_conserved_across_every_exchange_and_every_door_give` | fail | 39 | 0 |
| `KnockTest.test_t3_a_prompt_builder_that_reads_world_street_raises_truthleak` | fail | 93 | 0 |
| `KnockTest.test_t4_days_1_and_2_replay_and_the_street_makes_no_visit_before_day_3` | fail | 93 | 0 |
| `KnockTest.test_t5_the_block_is_the_same_with_and_without_a_door_and_the_door_lines_are_under_140_tokens` | fail | 39 | 0 |
| `KnockTest.test_t6_a_knock_comes_by_day_once_a_day_never_into_the_bathroom_and_wakes_by_the_draw` | fail | 39 | 0 |
| `KnockTest.test_t7_the_door_options_exist_only_in_a_scene_in_the_kitchen` | fail | 39 | 0 |
| `KnockTest.test_t8_a_visit_asks_at_most_18_at_the_door_and_a_day_at_most_56` | fail | 120 | 0 |
| `NightTest.test_t10_what_day2_carries_and_resets` | fail | 20 | 0 |
| `NightTest.test_t1_day1_replays_from_the_v11_caches_byte_for_byte` | error | 1 | 0 |
| `NightTest.test_t2_the_gap` | fail | 15 | 0 |
| `NightTest.test_t3_the_bedtime_prompt_exactly` | fail | 15 | 0 |
| `NightTest.test_t9_the_carry_in_exactly` | fail | 45 | 0 |
| `OwnWordsTest.test_prompts_before_someone_has_spoken_are_unchanged` | fail | 0 | 0 |
| `PhysicalLayerTest.test_a_house_further_along_holds_water_fixed_once` | fail | 98 | 0 |
| `PhysicalLayerTest.test_a_prompt_while_it_rains_says_so` | fail | 93 | 0 |
| `PhysicalLayerTest.test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food` | fail | 133 | 0 |
| `PhysicalLayerTest.test_block_c_names_where_a_trip_went` | fail | 132 | 0 |
| `PhysicalLayerTest.test_cold_at_f2_under_18_indoors_and_wet_after_the_yard` | fail | 93 | 0 |
| `PhysicalLayerTest.test_collect_rain_sets_the_bin_under_the_drainpipe_and_it_fills_by_catchment` | fail | 39 | 0 |
| `PhysicalLayerTest.test_eating_on_a_quiet_day_resets_fasting_at_that_minute` | fail | 35 | 0 |
| `PhysicalLayerTest.test_nights_1_and_2_took_no_water` | fail | 93 | 0 |
| `PhysicalLayerTest.test_q1_asks_when_thirst_reaches_badly_thirsty` | fail | 93 | 0 |
| `PhysicalLayerTest.test_q6_is_skipped_when_nobody_in_its_room_is_offered_a_rain_action` | fail | 39 | 0 |
| `PhysicalLayerTest.test_q6_once_a_day_and_rain_in_played_turns_is_a_trigger` | fail | 39 | 0 |
| `PhysicalLayerTest.test_rain_in_a_quiet_stretch_reaches_everyone_awake_and_q6_plays_their_room` | fail | 39 | 0 |
| `PhysicalLayerTest.test_save_and_ration_water_set_the_level_from_when_they_are_said` | fail | 39 | 0 |
| `PhysicalLayerTest.test_the_about_water_line_says_what_an_eye_sees` | fail | 93 | 0 |
| `PhysicalLayerTest.test_the_back_door_and_the_yard_from_day_3_only` | fail | 93 | 0 |
| `PhysicalLayerTest.test_the_bedtime_rain_option_and_rain_masking_the_front_door` | fail | 144 | 0 |
| `PhysicalLayerTest.test_the_chronicle_keeps_the_water_fixed_once` | fail | 144 | 0 |
| `PhysicalLayerTest.test_the_neighbours_water_is_fixed_when_first_needed_and_carried_home` | fail | 133 | 0 |
| `PhysicalLayerTest.test_the_store_at_day_3_0700_is_105_5_litres_of_tap_water` | fail | 93 | 0 |
| `PhysicalLayerTest.test_the_story_shows_rain_and_q6` | fail | 39 | 0 |
| `PhysicalLayerTest.test_w1_lines_sit_outside_the_budget_and_cut_no_memory_line` | fail | 93 | 0 |
| `PhysicalLayerTest.test_world_cannot_be_read_while_a_prompt_is_built` | fail | 93 | 0 |
| `PhysicalLayerTest.test_you_meant_to_is_shown_only_until_the_first_speech_act_of_the_day` | fail | 57 | 0 |
| `QuietDayTest.test_a_day_3_afternoon_act_is_yesterday_and_a_night_event_has_no_clock` | fail | 39 | 0 |
| `QuietDayTest.test_a_meeting_line_says_when_they_last_spoke_what_came_between_and_who_came_in` | fail | 93 | 0 |
| `QuietDayTest.test_a_night_suspicion_is_tonight_not_a_clock` | fail | 93 | 0 |
| `QuietDayTest.test_a_record_of_only_a_spans_end_is_stamped_at_its_end` | fail | 93 | 0 |
| `QuietDayTest.test_a_rest_ends_once_debt_is_below_12` | fail | 93 | 0 |
| `QuietDayTest.test_a_rest_of_an_hour_cools_a_grudge_of_3_to_2` | fail | 93 | 0 |
| `QuietDayTest.test_a_rest_under_an_hour_does_not_count_toward_the_two` | fail | 93 | 0 |
| `QuietDayTest.test_a_routine_breaks_a_run_and_its_move_is_remembered` | fail | 93 | 0 |
| `QuietDayTest.test_a_third_fasting_stage_at_168` | fail | 93 | 0 |
| `QuietDayTest.test_a_trigger_ask_ends_a_withdraw` | fail | 93 | 0 |
| `QuietDayTest.test_a_triggered_stretch_ends_as_when_the_budget_is_spent` | fail | 120 | 0 |
| `QuietDayTest.test_a_trip_is_known_to_the_whole_house_by_the_next_morning` | fail | 93 | 0 |
| `QuietDayTest.test_a_withdraw_ends_two_hours_after_it_began` | fail | 93 | 0 |
| `QuietDayTest.test_a_withdraw_into_a_room_with_a_grievance_is_a_meeting` | error | 14 | 0 |
| `QuietDayTest.test_an_exhausted_watcher_may_doze_and_then_notices_nothing` | fail | 111 | 0 |
| `QuietDayTest.test_block_a_and_bedtime_say_the_day_after_the_morning` | fail | 93 | 0 |
| `QuietDayTest.test_block_a_reads_the_clock_from_what_they_are_sure_of` | fail | 93 | 0 |
| `QuietDayTest.test_daniel_and_elena_never_withdraw` | error | 17 | 0 |
| `QuietDayTest.test_each_span_is_a_chronicle_event_with_its_witnesses` | fail | 93 | 0 |
| `QuietDayTest.test_every_q2_of_the_day_came_after_an_hour_apart` | fail | 93 | 0 |
| `QuietDayTest.test_every_quiet_prompt_carries_the_outings_line` | fail | 93 | 0 |
| `QuietDayTest.test_every_withdraw_of_the_day_had_every_condition` | fail | 93 | 0 |
| `QuietDayTest.test_far_houses_are_drawn_once_and_a_searched_house_is_empty` | fail | 98 | 0 |
| `QuietDayTest.test_far_offers_read_as_offers_on_every_day` | fail | 93 | 0 |
| `QuietDayTest.test_far_positions_are_heard_as_what_they_are` | fail | 93 | 0 |
| `QuietDayTest.test_fasting_at_day_3_0700_is_section_6s` | fail | 93 | 0 |
| `QuietDayTest.test_grudge_lines_say_today_from_minute_90` | fail | 93 | 0 |
| `QuietDayTest.test_leo_withdraws_after_his_say_when_he_falls_silent` | error | 14 | 0 |
| `QuietDayTest.test_needs_advance_exactly_across_the_jumps` | fail | 93 | 0 |
| `QuietDayTest.test_no_meeting_line_before_minute_90` | fail | 93 | 0 |
| `QuietDayTest.test_no_prompt_says_a_minute_of_90_or_later` | fail | 106 | 0 |
| `QuietDayTest.test_no_q5_without_a_trip_position` | fail | 39 | 0 |
| `QuietDayTest.test_no_withdraw_when_the_one_held_against_is_not_in_the_room` | error | 17 | 0 |
| `QuietDayTest.test_no_withdraw_without_a_grudge_of_3` | error | 12 | 0 |
| `QuietDayTest.test_prompt_headings_say_today_from_minute_90` | fail | 93 | 0 |
| `QuietDayTest.test_prompts_say_the_clock_from_minute_90` | fail | 93 | 0 |
| `QuietDayTest.test_q1_asks_only_with_someone_awake_there_and_once` | fail | 93 | 0 |
| `QuietDayTest.test_q2_asks_the_higher_grudge_and_the_one_already_there_on_a_tie` | fail | 93 | 0 |
| `QuietDayTest.test_q2_fires_on_an_arrival_after_60_quiet_minutes_and_not_before` | fail | 93 | 0 |
| `QuietDayTest.test_q2_once_per_pair_per_day` | fail | 93 | 0 |
| `QuietDayTest.test_q5_at_19_asks_whoever_took_a_trip_position_last` | fail | 39 | 0 |
| `QuietDayTest.test_q5_has_8_asks_on_top_of_the_days_40` | fail | 120 | 0 |
| `QuietDayTest.test_quiet_mode_asks_the_model_only_through_a_trigger` | fail | 93 | 0 |
| `QuietDayTest.test_sleep_debt_at_day_3_0700_is_section_6s` | fail | 93 | 0 |
| `QuietDayTest.test_someone_coming_in_does_not_end_a_withdraw` | fail | 93 | 0 |
| `QuietDayTest.test_someone_coming_in_during_played_turns_does_not_end_a_withdraw` | error | 14 | 0 |
| `QuietDayTest.test_someone_who_does_not_come_back_is_gone_and_each_knows_it_their_way` | fail | 134 | 0 |
| `QuietDayTest.test_the_body_line_states_each_stage` | fail | 93 | 0 |
| `QuietDayTest.test_the_day_budget_holds_when_the_fake_keeps_talking` | fail | 120 | 0 |
| `QuietDayTest.test_the_morning_stops_at_24_asks_and_a_triggered_stretch_at_8` | fail | 120 | 0 |
| `QuietDayTest.test_the_quiet_asks_hold_at_12_and_4_each` | fail | 106 | 0 |
| `QuietDayTest.test_the_quiet_day_runs_to_bedtime_with_a_rest_for_everyone` | fail | 93 | 0 |
| `QuietDayTest.test_the_story_shows_the_quiet_day` | fail | 93 | 0 |
| `QuietDayTest.test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it` | fail | 104 | 0 |
| `QuietDayTest.test_the_suspicion_line_says_today_from_minute_90` | fail | 93 | 0 |
| `QuietDayTest.test_v16_seed_1_until_w5` | error | 1 | 0 |
| `QuietDayTest.test_v16_through_night_2_is_unchanged` | fail | 93 | 0 |
| `QuietDayTest.test_w5_is_known_from_a_neighbour_line_that_came_back_with_nothing` | fail | 93 | 0 |
| `QuietDayTest.test_w5_is_offered_once_someone_knows_next_door_is_empty` | fail | 93 | 0 |
| `QuietDayTest.test_weakness_shifts_the_street_tables` | fail | 144 | 0 |
| `QuietDayTest.test_yesterdays_positions_are_named_as_said_yesterday_about_last_night` | fail | 93 | 0 |
| `QuietDayTest.test_yesterdays_positions_end_with_what_happened_that_night` | fail | 132 | 0 |
| `TalkTest.test_a_v16_replays_with_0_requests_and_no_topic_option_appears_before_a_visit_ends` | error | 1 | 0 |
| `TalkTest.test_b_each_fading_rule_f1_to_f5` | fail | 39 | 0 |
| `TalkTest.test_c_the_claims_for_daniel_are_section_2_2s_and_hold_nothing_their_teller_did_not_perceive` | fail | 39 | 0 |
| `TalkTest.test_d_after_a_tell_the_door_events_witnesses_are_unchanged_and_the_listener_holds_the_claim` | fail | 39 | 0 |
| `TalkTest.test_e_the_listeners_night_mind_shows_the_belief_and_a_memory_citing_it_is_not_warned` | fail | 39 | 0 |
| `TalkTest.test_f_the_next_mornings_block_a_holds_the_yesterday_at_line` | fail | 39 | 0 |
| `TalkTest.test_g_t1_warns_when_a_tells_words_name_nothing_of_the_topic` | fail | 39 | 0 |
| `TellFixTest.test_a_in_scene_1_at_0948_elenas_options_start_with_the_tell_and_the_rest_keep_their_order` | fail | 39 | 0 |
| `TellFixTest.test_b_leos_prompt_in_scene_3_holds_the_whereabouts_line_and_daniels_does_not` | fail | 39 | 0 |
| `TellFixTest.test_c_the_line_says_nothing_of_coming_in_when_the_teller_did_not_see_the_arrival` | fail | 39 | 0 |
| `TellFixTest.test_d_after_daniel_is_told_the_line_is_gone_and_his_claim_is_talk_impls` | fail | 39 | 0 |
| `TellFixTest.test_e_on_the_next_day_the_line_says_yesterday_and_gives_no_arrival_time` | fail | 39 | 0 |
| `TripTest.test_t3_the_v10_caches_pair_up_to_the_trigger` | fail | 1 | 0 |
| `TwoFixesTest.test_b_a_q1_at_17_39_with_50_spent_fires_with_no_trip_position_and_is_refused_with_one` | fail | 93 | 0 |
| `WitnessScenarioTest.test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers` | fail | 0 | 4 |

`OwnWordsTest.test_prompts_before_someone_has_spoken_are_unchanged` shows 0 and 0: it is the frozen-v9 comparison
(§5).

## 9. Checks after the last edit

`chronicle.py`'s `say` entry was split over two lines after the suite and the fake run had started. Both were run
again:
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_fix1_check2 > runs/play_fix1/check2.stdout.txt 2>&1   # exit 0
$ sha256sum runs/play_fix1_check2/fake/daniel_ate_it-seed1.md runs/play_fix1_check2/fake/daniel_ate_it-seed1.transcript.json
b1bbe7f29147bec5d46abe97761c378790f008eee51cb21085d4ed62e1e09160 *runs/play_fix1_check2/fake/daniel_ate_it-seed1.md
6656351aacc3bee941097b56a6ca91044bf850c600459e40f90e0c0d2371d1c1 *runs/play_fix1_check2/fake/daniel_ate_it-seed1.transcript.json
$ .venv/Scripts/python.exe -m unittest test_morning.PlayFix1Test > runs/play_fix1/pass_all5.txt 2>&1   # exit 0
Ran 5 tests in 0.340s

OK
```

## 10. Open points for the user

- **The night mind's record trimming** (`mind.bound_records`, R8) cuts quoted words to fit, keeping "the gist". A
  heard speech record is now `Elena, to you: "…"`, so a trimmed one reads `Elena, to you.` Its first two classes
  (reassurances, trip positions) are found by words of the old gists, so they no longer match heard speech; such
  records now fall to the third class. Nothing was changed here.
- **The code's own summaries still name the act:** the pattern block ("In that time: Daniel accused you"), the grudge
  facts ("Daniel accused you of taking the can at minute 09, and you had not"), and "About going there tonight". They
  are conclusions the code draws from the act. With `say_to_<p>` offered, fewer of the model's acts should need to be a
  wrong one to carry what it means. Whether they should follow the words is open.
- **The prompt budget:** each person in a room of four has three more option lines. In the witness scenario this trims
  Leo's oldest backstory line at minute 00 (§4, last row).
