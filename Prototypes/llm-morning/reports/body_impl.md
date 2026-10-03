# Implementation: the promise line at bedtime and the body's food moment (v13)

Mode: implement. Built as `reports/body_design.md` specifies. No API was called: every command
ran with `GEMINI_API_KEY` unset, or in replay mode, which has no client.
- Paths are relative to `Prototypes/llm-morning/`.
- `$S` is the session scratchpad (`…/scratchpad/impl`). Its two read-only scripts are in §7.

## Result

| | |
|---|---|
| Commits | **`99f03d7`** freeze v12, new runs default to v13. **`db317c7`** the promise line and the food moment, with their tests. This report is committed on its own after them. |
| New tests | **12** (B-T1 to B-T12, class `BodyTest`). Before the change: **10 fail** (5 failures, 5 errors), and 2 pass. After: **12 pass**. |
| The 2 that passed before | B-T1 (day 1 replays from a copy of the v12 cache) and B-T12 (`v12/check.py` replays). They check that nothing old moved, so they cannot fail before the change. B-T12 needed the freeze, which came first. |
| Full suite | **158 tests, OK** in 75.6 s (before: 146, OK in 74.0 s). |
| Existing test changed | **1.** night_design's T3 pinned seed 1 Daniel's exact bedtime prompt. It now expects the promise line before the options, which is the change §1 of the design specifies. |
| Day 1 from the v11 caches | **55, 53, 45 answers, 0 API requests; story and transcript IDENTICAL** to `runs/v11` (§4). |
| v12 night and day 2 from the frozen copy | `v12/check.py`: **113, 96, 100 answers, 0 API calls; story and transcript IDENTICAL** to `runs/v12` (§4). `v11`, `v10` and `v9` checks: IDENTICAL. |
| git status | Clean apart from the three old `runs/v6/*.replay.md` files. |

**The paired start works as the design computed** (B-T10, run against the real `cache/v12`):
- Seed 2's first food moment is at minute 00, for Daniel, 3rd to act, with chance 0.077.
- Seed 3's is at minute 09, for Mara, 3rd to act, with chance 0.084.
- In both seeds every earlier prompt is a cache hit: the night's, and day 2's up to the moment.
- Seed 1 has no moment, because its shelf is empty all morning.

## 1. What was built, by the design's sections

| Design | Where | What |
|---|---|---|
| Housekeeping (§4) | `v12/`, `v12/check.py`, `morning.py`, `.gitignore` | The code at `94eca1e`, copied unchanged into `v12/` (§5). `v12/check.py` replays day 1, the night and day 2 as `morning.run` does. The default `--out` is `v13`. |
| §1 the promise line | `night.py` `PROMISE`, bedtime loop | The last `Now` line when the person's own latest trip position has the kind `volunteer` (day 1's `volunteer`, day 2's `volunteer` or `still_going`). |
| §2.1 F1–F9 | `world.py` `food_due` | Checked in this order: day 2; kitchen; shelf; someone else there; starving; nothing eaten this morning; 30 minutes; one a turn; the draw. `decide` calls it first. Aside and give answers never reach it. |
| §2.2 the chance | `food_band`, `food_chance`, `FOOD_RATE`, `FOOD_EVERY` | `round(rate × (0.5 + impulsive), 4)`. The rounding reproduces the design's table to the digit (B-T5). The band comes from `ate_yesterday`, set at `next_day` from the last day-1 meal: an eat, a share part, or a given portion. |
| §2.1 F9 the draw | `food_draw` | `random.Random(f"{seed}:day2:food:{t}:{pid}")`. |
| §2.4 the prompt | `food_options`, `food_moment_line`, `decide_food`; `prompt_for(extra=)`, `ask_model(extra=)` | Options `eat`, `give_<q>` (family order), `share`. The line is the last `Now` line, after the pattern block. |
| §2.5 giving | `turn`, `decide_given`, `apply` (`give`, `eat_given`, `refuse_given`) | Q answers at once. If Q had not acted, it is Q's turn; otherwise it is an extra answer. |
| §2.6 perception | `apply` | The table's turn lines, pinned lines, triggers (new) and grudge. Nothing through walls but words. Nobody perceives the moment itself. |
| §2.7 fallbacks, records, story | `decide_food`, `decide_given`, `act`, `story.decision_line`, `morning.run` | A fallback at a moment is `silent`, and the food stays; a fallback from Q is `refuse_given`. The decision and the act carry `food_moment` (`band`, `chance`, `draw`, `portions`). The meta for day 2 has `food_moments` and `give_answers`. The story line is §2.7's. |
| `talk.act_of` | `talk.py` | `give_<q>` → `("give", q)`, aimed at nobody. |

**What the code needed that the design does not word.** These are the only strings and rules
added beyond it, each the plainest fit with the code around it:
- **`KIND_DONE` entries** for the pattern block: `give` → "given someone a portion", `eat_given`
  → "eaten", `refuse_given` → "refused a portion". Without them, a person whose latest act is
  one of these would crash `pattern()`.
- **Activity labels**, as others see them in "<Name> is here, …":
  - giver: `handing <Q> a portion`;
  - Q after `eat_given`: `eating`, as `eat`;
  - Q after `refuse_given`: `standing`.
- **The giver's words, if any,** are heard as "… while handing <Q> a portion". The design gives
  the doing texts for Q only (`eating`, `putting the portion back on the shelf`).
- **Q's own pinned line after a refusal:**
  `min MM: <P> gave you one of the portions, and you put it back on the shelf.`
  The design's table gives Q's line for `eat_given` only.
- **The story:**
  - the "yesterday" band is written `last ate: yesterday`, because `food_moment` keeps no minute;
  - `ORDINAL` gains `5th`, for an extra answer;
  - "came of it" texts follow the existing ones.
- **The new-fact texts** behind the triggers: `<Q> ate the portion <P> gave <him/her>` and
  `<Q> put back the portion <P> gave <him/her>`.
- **`Person.last_meal`:** the minute they last ate in the current scene. It feeds
  `ate_yesterday` and touches no prompt, so day 1 stays byte-identical.

**One thing the design left as it is, which a reader of the run should know.** While Q decides,
the portion is in Q's hands and off the shelf (§2.5). Q's prompt therefore shows the shelf one
lower: "About food: the shelf holds 0 portions … so there is nothing to eat today" in seed 2. That
is true of the shelf, but it does not count the portion in Q's hand.

## 2. Tests before the change

The new tests were written first, into `test_morning.py`, after the freeze commit and before any
code change. `before.txt` is shown in full, except that the long assertion messages, which
print whole prompts, are cut at 240 characters:

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.BodyTest
test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache (test_morning.BodyTest.test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache) ... ERROR
test_b_t11_records_and_the_story (test_morning.BodyTest.test_b_t11_records_and_the_story) ... ERROR
test_b_t12_v12_still_replays (test_morning.BodyTest.test_b_t12_v12_still_replays) ... ok
test_b_t1_day1_replays_from_a_copy_of_the_v12_cache (test_morning.BodyTest.test_b_t1_day1_replays_from_a_copy_of_the_v12_cache) ... ok
test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go (test_morning.BodyTest.test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go) ... FAIL
test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line (test_morning.BodyTest.test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line) ... FAIL
test_b_t4_when_a_food_moment_can_fire (test_morning.BodyTest.test_b_t4_when_a_food_moment_can_fire) ... ERROR
test_b_t5_the_chance_and_the_draw (test_morning.BodyTest.test_b_t5_the_chance_and_the_draw) ... ERROR
test_b_t6_the_moments_prompt_exactly (test_morning.BodyTest.test_b_t6_the_moments_prompt_exactly) ... ERROR
test_b_t7_giving_and_the_answer (test_morning.BodyTest.test_b_t7_giving_and_the_answer) ... FAIL
test_b_t8_what_the_others_perceive (test_morning.BodyTest.test_b_t8_what_the_others_perceive) ... FAIL
test_b_t9_fallbacks_never_eat_for_anyone (test_morning.BodyTest.test_b_t9_fallbacks_never_eat_for_anyone) ... FAIL

======================================================================
ERROR: test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache (test_morning.BodyTest.test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3428, in test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache
    self.assertEqual((first[0], first[1]["person"], first[2]), (minute, who, place), seed)
                      ~~~~~^^^
TypeError: 'NoneType' object is not subscriptable

======================================================================
ERROR: test_b_t11_records_and_the_story (test_morning.BodyTest.test_b_t11_records_and_the_story)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3438, in test_b_t11_records_and_the_story
    with mock.patch.object(world.Morning, "food_draw", lambda self, t, pid: 0.0):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\unittest\mock.py", line 1467, in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\unittest\mock.py", line 1437, in get_original
    raise AttributeError(
AttributeError: <class 'world.Morning'> does not have the attribute 'food_draw'

======================================================================
ERROR: test_b_t4_when_a_food_moment_can_fire (test_morning.BodyTest.test_b_t4_when_a_food_moment_can_fire)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3181, in test_b_t4_when_a_food_moment_can_fire
    self.assertTrue(due())                                       # all of F1-F9 hold
                    ^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3180, in due
    return day2.food_due(mara, t)
           ^^^^^^^^^^^^^
AttributeError: 'Morning' object has no attribute 'food_due'. Did you mean: 'food_draw'?

======================================================================
ERROR: test_b_t5_the_chance_and_the_draw (test_morning.BodyTest.test_b_t5_the_chance_and_the_draw)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3234, in test_b_t5_the_chance_and_the_draw
    self.assertEqual((world.FOOD_RATE, world.FOOD_EVERY), ({"before yesterday": 0.07, "yesterday": 0.035}, 30))
                      ^^^^^^^^^^^^^^^
AttributeError: module 'world' has no attribute 'FOOD_RATE'

======================================================================
ERROR: test_b_t6_the_moments_prompt_exactly (test_morning.BodyTest.test_b_t6_the_moments_prompt_exactly)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3278, in test_b_t6_the_moments_prompt_exactly
    day2.turn(0)
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\world.py", line 1026, in turn
    d = self.decide(p, t)
        ^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\world.py", line 1155, in decide
    choice, why = self.ask_model(p, t, opts, d)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3276, in spy
    return orig(q, t, opts, d, extra)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Morning.ask_model() takes 5 positional arguments but 6 were given

======================================================================
FAIL: test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go (test_morning.BodyTest.test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3141, in test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go
    self.assertEqual(now_lines(prompt)[-1] == PROMISE, gets, heard)
AssertionError: False != True : {'daniel': (36, 'volunteer', None, 1)}

======================================================================
FAIL: test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line (test_morning.BodyTest.test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3165, in test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line
    self.assertEqual(paired.missed, [bedtime[0]])
AssertionError: Lists differ: [] != ['You are Daniel, 25, the eldest son of th[4815 chars]use']

Second list contains 1 additional elements.
First extra element 0:
'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not be … [4621 more characters of the same message]

Diff is 5386 characters long. Set self.maxDiff to None to see it.

======================================================================
FAIL: test_b_t7_giving_and_the_answer (test_morning.BodyTest.test_b_t7_giving_and_the_answer)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3307, in test_b_t7_giving_and_the_answer
    self.assertEqual([d["person"] for d in ds], [giver, q, o[1], o[2]])
AssertionError: Lists differ: ['mara', 'elena', 'daniel', 'leo'] != ['mara', 'leo', 'elena', 'daniel']

First differing element 1:
'elena'
'leo'

- ['mara', 'elena', 'daniel', 'leo']
?                           -------

+ ['mara', 'leo', 'elena', 'daniel']
?          +++++++


======================================================================
FAIL: test_b_t8_what_the_others_perceive (test_morning.BodyTest.test_b_t8_what_the_others_perceive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3344, in test_b_t8_what_the_others_perceive
    self.assertIn(f"Said and done in the kitchen this turn, before you, in order:\n1. {line}.\n", later)
AssertionError: 'Said and done in the kitchen this turn, before you, in order:\n1. Mara gives one of the portions to Leo, and Leo eats it.\n' not found in 'You are Elena, 42, the mother of the family (Elena, 42, the mother; Daniel, 25; Leo, … [5098 more characters of the same message]

======================================================================
FAIL: test_b_t9_fallbacks_never_eat_for_anyone (test_morning.BodyTest.test_b_t9_fallbacks_never_eat_for_anyone)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3395, in test_b_t9_fallbacks_never_eat_for_anyone
    self.assertEqual((d["person"], d["mode"], d["option"]), (giver, "fallback", "silent"))
AssertionError: Tuples differ: ('mara', 'model', 'silent') != ('mara', 'fallback', 'silent')

First differing element 1:
'model'
'fallback'

- ('mara', 'model', 'silent')
?           ^^^^

+ ('mara', 'fallback', 'silent')
?           ^^ +++++


----------------------------------------------------------------------
Ran 12 tests in 2.004s

FAILED (failures=5, errors=5)
exit=1
```

## 3. Tests after the change

The `BodyTest` lines and night_design's T3, then the summary, from the full run (`$S/after_full.txt`; every other test line reads `ok`):

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning
…
test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache (test_morning.BodyTest.test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache) ... ok
test_b_t11_records_and_the_story (test_morning.BodyTest.test_b_t11_records_and_the_story) ... ok
test_b_t12_v12_still_replays (test_morning.BodyTest.test_b_t12_v12_still_replays) ... ok
test_b_t1_day1_replays_from_a_copy_of_the_v12_cache (test_morning.BodyTest.test_b_t1_day1_replays_from_a_copy_of_the_v12_cache) ... ok
test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go (test_morning.BodyTest.test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go) ... ok
test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line (test_morning.BodyTest.test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line) ... ok
test_b_t4_when_a_food_moment_can_fire (test_morning.BodyTest.test_b_t4_when_a_food_moment_can_fire) ... ok
test_b_t5_the_chance_and_the_draw (test_morning.BodyTest.test_b_t5_the_chance_and_the_draw) ... ok
test_b_t6_the_moments_prompt_exactly (test_morning.BodyTest.test_b_t6_the_moments_prompt_exactly) ... ok
test_b_t7_giving_and_the_answer (test_morning.BodyTest.test_b_t7_giving_and_the_answer) ... ok
test_b_t8_what_the_others_perceive (test_morning.BodyTest.test_b_t8_what_the_others_perceive) ... ok
test_b_t9_fallbacks_never_eat_for_anyone (test_morning.BodyTest.test_b_t9_fallbacks_never_eat_for_anyone) ... ok
test_t3_the_bedtime_prompt_exactly (test_morning.NightTest.test_t3_the_bedtime_prompt_exactly) ... ok
Ran 158 tests in 75.592s

OK
exit=0
```

The baseline, before any change in this session:

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
…
Ran 146 tests in 73.961s

OK
exit=0
```

## 4. Replays

**Day 1 with the new code, from `cache/v11`** (`$S/replay_day1.py`, §7; replay mode has no client):

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/replay_day1.py
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
```

**The frozen versions**, the v12 night and day 2 included:

```
$ python v12/check.py
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v11/check.py
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v10/check.py
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

## 5. The freeze

`v12/` holds the code at `94eca1e`, the last commit before the freeze, byte for byte:

```
$ for f in data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py night.py story.py talk.py world.py; do git show 94eca1e:Prototypes/llm-morning/$f | cmp -s - v12/$f && echo "v12/$f = $f at 94eca1e" || echo "v12/$f DIFFERS"; done
v12/data.py = data.py at 94eca1e
v12/gemini.py = gemini.py at 94eca1e
v12/metrics.py = metrics.py at 94eca1e
v12/metrics3.py = metrics3.py at 94eca1e
v12/metrics4.py = metrics4.py at 94eca1e
v12/metrics5.py = metrics5.py at 94eca1e
v12/morning.py = morning.py at 94eca1e
v12/night.py = night.py at 94eca1e
v12/story.py = story.py at 94eca1e
v12/talk.py = talk.py at 94eca1e
v12/world.py = world.py at 94eca1e
```

```
$ git show 99f03d7 --stat
commit 99f03d7690780ead56ad2eab0249970f6b635a91
LLM morning: freeze v12, new runs default to v13

 Prototypes/llm-morning/.gitignore      |    2 +
 Prototypes/llm-morning/morning.py      |   12 +-
 Prototypes/llm-morning/v12/check.py    |   65 ++
 Prototypes/llm-morning/v12/data.py     |  208 +++++
 Prototypes/llm-morning/v12/gemini.py   |  270 ++++++
 Prototypes/llm-morning/v12/metrics.py  |  182 ++++
 Prototypes/llm-morning/v12/metrics3.py |  141 +++
 Prototypes/llm-morning/v12/metrics4.py |  149 +++
 Prototypes/llm-morning/v12/metrics5.py |  152 ++++
 Prototypes/llm-morning/v12/morning.py  |  227 +++++
 Prototypes/llm-morning/v12/night.py    |  661 ++++++++++++++
 Prototypes/llm-morning/v12/story.py    |  535 +++++++++++
 Prototypes/llm-morning/v12/talk.py     |  132 +++
 Prototypes/llm-morning/v12/world.py    | 1549 ++++++++++++++++++++++++++++++++
 14 files changed, 4279 insertions(+), 6 deletions(-)
```

Its diff, without the eleven copied files:

```diff
diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index d3af01d..d890b42 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -25,3 +25,5 @@ runs/v11/fake/
 cache/v11/fake-*
 runs/v12/fake/
 cache/v12/fake-*
+runs/v13/fake/
+cache/v13/fake-*
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index f1af2fe..a517ec6 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -9,9 +9,9 @@ writes them as one story (reports/night_design.md).
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v12; v4 replays
-                      the fourth version's runs; v5/check.py to v11/check.py replay the
-                      fifth's to eleventh's)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v13; v4 replays
+                      the fourth version's runs; v5/check.py to v12/check.py replay the
+                      fifth's to twelfth's)
 
 Day 1 is the morning of the count; then the night; then day 2. The model names and call limits
 are in config.json; the call limit counts each of the three apart. The key is read from
@@ -80,13 +80,13 @@ def day_meta(m, scene):
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v12"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v13"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v11/ can still replay.
+    # cache/vN after), which v1/ to v12/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -216,7 +216,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v12")
+    ap.add_argument("--out", default="v13")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/v12/check.py b/Prototypes/llm-morning/v12/check.py
new file mode 100644
index 0000000..c232833
--- /dev/null
+++ b/Prototypes/llm-morning/v12/check.py
@@ -0,0 +1,65 @@
+"""Replays the three twelfth-version runs from their cache and checks their stories.
+
+    python v12/check.py
+
+v12/ is a frozen copy of the code that made the runs reports/night_v12.md describes
+(daniel_ate_it: day 1 from the v11 answers, then the night and day 2 of reports/night_design.md).
+Replaying makes no API calls. Each replayed story must come out byte for byte as runs/v12/<name>.md,
+and its transcript (day 1, the night and day 2) as the one saved beside it.
+"""
+import json
+import os
+import sys
+
+HERE = os.path.dirname(os.path.abspath(__file__))
+ROOT = os.path.dirname(HERE)
+sys.path.insert(0, HERE)
+
+from gemini import Cache, Oracle                         # noqa: E402  (v12's own modules)
+from night import Night                                  # noqa: E402
+from story import render, render_day2, render_night      # noqa: E402
+from world import Morning                                # noqa: E402
+
+# (scenario, model key, model name, seeds), as the runs in runs/v12 were made.
+RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3))]
+
+
+def main():
+    ok = True
+    for scenario, key, model, seeds in RUNS:
+        for seed in seeds:
+            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
+            cache = Cache(os.path.join(ROOT, "cache", "v12", f"{model}-{name}.json"))
+            oracle = Oracle(cache, model, seed, client=None, replay=True)
+            command = ("python morning.py"
+                       + (f" --scenario {scenario}" if scenario != "daniel_ate_it" else "")
+                       + (f" --model {key}" if key else "") + f" --seed {seed}")
+            # As morning.run does it: day 1, its story, then the night and day 2.
+            morning = Morning(oracle, seed, scenario)
+            for t in range(morning.turns):
+                morning.turn(t)
+            morning.finish()
+            day1_text = render(morning, seed, model, command)
+            oracle.new_scene()
+            night = Night(morning, oracle).run()
+            oracle.new_scene()
+            day2 = Morning.next_day(morning, night, oracle)
+            for t in range(day2.turns):
+                day2.turn(t)
+            day2.finish()
+            text = day1_text + render_night(night) + render_day2(day2)
+            transcript = {"day1": morning.transcript, "night": night.transcript(), "day2": day2.transcript}
+            base = os.path.join(ROOT, "runs", "v12", name)
+            with open(base + ".md", "rb") as f:
+                same_story = f.read() == text.encode("utf-8")
+            with open(base + ".transcript.json", encoding="utf-8") as f:
+                same_transcript = json.load(f) == json.loads(json.dumps(transcript))
+            ok &= same_story and same_transcript
+            print(f"{name}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
+                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
+                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
+    return 0 if ok else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main())
```

## 6. The diff of the change

```
$ git show db317c7 --stat
commit db317c72b70d9e21b10baedd4a83d3c7b1ef7a8f
LLM morning: the promise line at bedtime and the body's food moment (v13)

 Prototypes/llm-morning/morning.py      |   7 +-
 Prototypes/llm-morning/night.py        |   7 +
 Prototypes/llm-morning/story.py        |  10 +-
 Prototypes/llm-morning/talk.py         |   5 +-
 Prototypes/llm-morning/test_morning.py | 423 ++++++++++++++++++++++++++++++++-
 Prototypes/llm-morning/world.py        | 192 ++++++++++++++-
 6 files changed, 631 insertions(+), 13 deletions(-)
```

```diff
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index a517ec6..18f2a42 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -167,7 +167,10 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
                   "max_prompt_tokens_estimated": night.m.max_prompt_tokens},
         "day2_asks": day2_counts["answers_live"] + day2_counts["answers_from_cache"],
         "day2_api_requests": day2_counts["api_requests"],
-        "day2": day_meta(day2, scenes["day2"]),
+        # The body's food moments, and the answers of those handed a portion (reports/body_design.md, §2.7).
+        "day2": {**day_meta(day2, scenes["day2"]),
+                 "food_moments": sum(1 for rec in day2.log for d in rec["decisions"] if d.get("food_moment")),
+                 "give_answers": sum(1 for rec in day2.log for d in rec["decisions"] if d.get("given_by"))},
         "max_prompt_tokens_estimated": max(morning.max_prompt_tokens, night.m.max_prompt_tokens,
                                            day2.max_prompt_tokens),
         "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
@@ -183,7 +186,7 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
     for k in ("night_asks", "night_api_requests", "leavers", "outcome"):
         say(f"  {k}: {meta[k]}")
     say(f"  night house: {night.house}; away: {meta['night']['away']}")
-    for k in DAY_KEYS:
+    for k in DAY_KEYS + ("food_moments", "give_answers"):
         say(f"  day2 {k}: {meta['day2'][k]}")
     for k in ("day2_asks", "day2_api_requests", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api",
               "run_seconds", "story_sha256"):
diff --git a/Prototypes/llm-morning/night.py b/Prototypes/llm-morning/night.py
index 164c426..e01ec4a 100644
--- a/Prototypes/llm-morning/night.py
+++ b/Prototypes/llm-morning/night.py
@@ -43,6 +43,8 @@ BEDTIME = [("sleep", "go to sleep"),
 BED_LINE = {"sleep": "You went to sleep.", "lie_awake": "You lay awake and listened.",
             "watch_door": "You sat up in the kitchen by the front door.",
             "go_next_door": "You meant to go to the neighbour's house once the others were asleep."}
+# At bedtime, for whoever's latest word on the trip was that they would go (reports/body_design.md, §1).
+PROMISE = "You said you would go to the neighbour's house tonight. If you are going, it is now."
 TONIGHT = {"sleep": "you went to sleep.", "lie_awake": "you lay awake and listened.",
            "watch_door": "you sat up in the kitchen by the front door.",
            "go_next_door": "you meant to go to the neighbour's house once the others were asleep."}
@@ -201,6 +203,9 @@ class Night:
                    f"Everyone has gone to bed in their own room: {BEDS}.",
                    f"You are in the {data.ROOMS[room]}, in your bed. {NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.",
                    f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]
+            own = self.people[q].trip_heard.get(q)
+            if own and own[1] == "volunteer":           # `volunteer`, or day 2's `still_going`
+                now.append(PROMISE)
             opts = [Option(i, label) for i, label in BEDTIME]
             choice, _ = self.ask(q, "bedtime", now, opts, "sleep")
             self.choices[q] = choice
@@ -630,6 +635,8 @@ def next_day(day1, n, oracle):
         p.trip_heard, p.proposed, p.trip_raised = {}, False, False
         p.addressed = p.aside_lead = None
         p.eaten = 0.0
+        # The food moment's band (reports/body_design.md, §2.2): yesterday's last meal, if any.
+        p.ate_yesterday, p.last_meal, p.last_food = p.last_meal, None, None
         p.last_inner = p.last_asked = None
         p.feeling, p.feeling_until = (("shaken", world.FEELING_SHOWS_FOR_TURNS - 1) if q in shaken else (None, -1))
         p.activity = {"kind": "idle", "label": "just got up"}
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index 06446cf..7e9fd50 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -8,7 +8,7 @@ from world import (FALL_EVERY, FEELING_SHOWS_FOR_TURNS, INNER_EVERY, KIND_DONE,
                    QUIET_TURNS, grudge_facts, hunger_words, trait_words)
 
 DAYS_KNOWN = {"did": "did it", "saw": "saw it", "heard": "heard it"}
-ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
+ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}   # 5th: an extra answer to a give (body_design §2.5)
 
 
 def fold_runs(log):
@@ -63,7 +63,13 @@ def decision_line(d, fold=None):
         return (f"- **{name}.** Rules: nothing social happened to them. **{cap(d['label'])}**. "
                 f"Came of it: {d['came_of_it']}{fact}")
     order = f" ({ORDINAL[d['place']]} to act in the {data.ROOMS[d['room']]}: {d['order_reason']})"
-    if d.get("trip_moment") is not None:
+    if d.get("food_moment"):
+        f = d["food_moment"]
+        last = "not since before yesterday" if f["band"] == "before yesterday" else f["band"]
+        because = (f"**Food moment**, starving in the kitchen with {f['portions']} portion"
+                   f"{'s' if f['portions'] != 1 else ''} on the shelf; last ate: {last} (chance {f['chance']:g} a "
+                   f"turn, draw {f['draw']:.4f})")
+    elif d.get("trip_moment") is not None:
         because = f"**The food**: {d['trip_why']}"
         if d.get("inner"):
             because += "; also an inner moment: " + "; ".join(d["inner"])
diff --git a/Prototypes/llm-morning/talk.py b/Prototypes/llm-morning/talk.py
index 6c47db6..d49d224 100644
--- a/Prototypes/llm-morning/talk.py
+++ b/Prototypes/llm-morning/talk.py
@@ -16,7 +16,8 @@ def act_of(option):
     The trip's options (reports/trip_design.md, §3.3): proposing it, volunteering, objecting
     to it or to one person going, backing one person to go, and declining to go. Day 2 words them
     anew (reports/night_design.md, §6) with the same kinds: nobody_goes, keep_<q>_home, send_<q>,
-    still_going (a restated offer) and refuse_to_go."""
+    still_going (a restated offer) and refuse_to_go. Giving a portion to one person at a food
+    moment (reports/body_design.md, §2.4) is `give`, aimed at nobody."""
     if option == "ask_who":
         return "ask", None
     if option == "propose_trip":
@@ -37,7 +38,7 @@ def act_of(option):
         return "object", option[len("keep_"):-len("_home")]
     if option.startswith("send_"):
         return "back", option[len("send_"):]
-    for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object"):
+    for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object", "give"):
         if option.startswith(prefix + "_"):
             return prefix, option[len(prefix) + 1:]
     return option, None     # silent, deny, confess, search, eat, share, volunteer, decline
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index cd774b8..bf799b4 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -2421,7 +2421,9 @@ class NightTest(unittest.TestCase):
             "\nNow it is night. " + GAP + "\n"
             "Everyone has gone to bed in their own room: Daniel and Leo in the brothers room, Elena and Mara in the "
             "back room.\nYou are in the brothers room, in your bed. Leo is in his bed.\n"
-            "The kitchen is dark. The shelf holds 0 portions.\n" + BEDTIME_OPTIONS), bedtime["daniel"])
+            "The kitchen is dark. The shelf holds 0 portions.\n"
+            # Seed 1's Daniel last said he would go (min 36), so the promise line comes last (body_design §1).
+            + PROMISE + "\n" + BEDTIME_OPTIONS), bedtime["daniel"])
         self.assertIn("\nYou are in the back room, in your bed. Mara is in her bed.\n", bedtime["elena"])
         self.assertIn("\nYou are in the back room, in your bed. Elena is in her bed.\n", bedtime["mara"])
         for p in bedtime.values():
@@ -3048,6 +3050,425 @@ class NightTest(unittest.TestCase):
             self.assertIn("0 API calls", done.stdout)
 
 
+V12_CACHE = os.path.join(HERE, "cache", "v12")
+PROMISE = "You said you would go to the neighbour's house tonight. If you are going, it is now."
+FOOD_BEFORE = ("Your hunger has the better of you: you have not eaten since before yesterday, and the food is on the "
+               "shelf in front of you. You cannot leave it there any longer.")
+FOOD_YESTERDAY = ("Your hunger has the better of you: you last ate yesterday, at minute {mm}, and the food is on the "
+                  "shelf in front of you. You cannot leave it there any longer.")
+# The design's table (reports/body_design.md, §2.2): (not since before yesterday, ate yesterday).
+FOOD_CHANCES = {"daniel": (0.077, 0.0385), "elena": (0.0525, 0.0263), "leo": (0.049, 0.0245), "mara": (0.084, 0.042)}
+
+
+def never(t, pid):
+    return 0.99
+
+
+def only(who, at=None):
+    """A food draw that fires for `who` (at turn `at`, or any turn) and for nobody else."""
+    return lambda t, pid: 0.0 if pid == who and (at is None or t == at) else 0.99
+
+
+class BrokenFor(NightScripted):
+    """NightScripted, but the answers to prompts that hold `marker` are not JSON."""
+
+    def __init__(self, marker, prefs=None):
+        super().__init__(prefs)
+        self.marker = marker
+
+    def generate(self, system, prompt):
+        text = super().generate(system, prompt)
+        return "not json" if self.marker in prompt else text
+
+
+class BodyTest(unittest.TestCase):
+    """The promise line at bedtime and the body's food moment on day 2 (reports/body_design.md;
+    tests B-T1 to B-T12 of §4)."""
+
+    setUp = NightTest.setUp
+    tearDown = NightTest.tearDown
+    path = NightTest.path
+    v11_day1 = NightTest.v11_day1
+    short_day1 = NightTest.short_day1
+    night_of = NightTest.night_of
+    act = NightTest.act
+
+    def day2_of(self, seed, prefs=None, draws=never):
+        """Day 2 of seed N after v11's day 1 and a scripted night (everyone sleeps), its food draws forced."""
+        client = NightScripted(prefs)
+        day1, oracle = self.v11_day1(seed, client)
+        n = self.night.Night(day1, oracle).run()
+        day2 = Morning.next_day(day1, n, oracle)
+        day2.food_draw = draws
+        return day2, client
+
+    def bedtime_prompt(self, trip_heard, who="daniel"):
+        """The bedtime prompt of `who` when their trip record is `trip_heard`."""
+        client = NightScripted()
+        day1, oracle = self.short_day1(client)
+        day1.people[who].trip_heard = dict(trip_heard)
+        self.night.Night(day1, oracle).run()
+        return client.night_prompts(who)[0]
+
+    def order_at_0(self, seed):
+        day2, _ = self.day2_of(seed)
+        day2.turn(0)
+        return [d["person"] for d in day2.log[0]["decisions"]]
+
+    # B-T1
+    def test_b_t1_day1_replays_from_a_copy_of_the_v12_cache(self):
+        for seed, served in V11_SERVED.items():
+            name = f"daniel_ate_it-seed{seed}"
+            path = self.path(f"v12-{seed}")
+            shutil.copy(os.path.join(V12_CACHE, f"{V6_MODEL}-{name}.json"), path)
+            oracle = Oracle(Cache(path), V6_MODEL, seed, replay=True)
+            day1 = Morning(oracle, seed).run()
+            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
+            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+
+    # B-T2
+    def test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go(self):
+        cases = [
+            ({"daniel": (36, "volunteer", None, 1)}, True),                         # day 1's offer
+            ({"daniel": (9, "volunteer", None, 4, "still_going")}, True),           # day 2's restatement
+            ({"daniel": (6, "volunteer", None, 3, "volunteer")}, True),             # day 2's offer
+            ({"daniel": (39, "decline", None, 7)}, False),                          # offered, then declined
+            ({"daniel": (39, "object", None, 7)}, False),                           # offered, then objected
+            ({"leo": (30, "back", "daniel", 2)}, False),                            # only named by others
+            ({}, False),                                                            # no position
+        ]
+        for heard, gets in cases:
+            prompt = self.bedtime_prompt(heard)
+            self.assertEqual(now_lines(prompt)[-1] == PROMISE, gets, heard)
+            self.assertEqual(prompt.count(PROMISE), int(gets), heard)
+        # Never in a reaction or an answer, and never to anyone but the one who said it.
+        client = NightScripted({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"]})
+        day1, oracle = self.short_day1(client)
+        day1.people["daniel"].trip_heard = {"daniel": (36, "volunteer", None, 1)}
+        n = self.night.Night(day1, oracle, draws=QUIET).run()
+        self.assertIn(("leo", "reaction"), [(d["person"], d["ask"]) for d in n.decisions])
+        self.assertIn(("daniel", "answer"), [(d["person"], d["ask"]) for d in n.decisions])
+        prompts = client.night_prompts()
+        self.assertEqual(sum(PROMISE in p for p in prompts), 1)
+        self.assertIn(PROMISE, client.night_prompts("daniel")[0])
+
+    # B-T3
+    def test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line(self):
+        for seed in (1, 2, 3):
+            day1, _ = self.v11_day1(seed)
+            paired = PairedOracle(os.path.join(V12_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"), V6_MODEL, seed)
+            self.night.Night(day1, paired).run()
+            bedtime = [p for p in paired.asked if "\nNow it is night. " in p][:4]
+            self.assertEqual(len(bedtime), 4)
+            if seed != 1:
+                self.assertEqual(paired.missed, [], seed)
+                continue
+            self.assertEqual(paired.missed, [bedtime[0]])
+            new = bedtime[0]
+            self.assertTrue(new.startswith("You are Daniel,"))
+            old = next(e["prompt"] for e in paired.entries.values()
+                       if e["prompt"].startswith("You are Daniel,") and "\nNow it is night. " in e["prompt"])
+            self.assertEqual(new, old.replace("\nYour options:\n", f"\n{PROMISE}\nYour options:\n", 1))
+            self.assertEqual(now_lines(new)[-2:], ["The kitchen is dark. The shelf holds 0 portions.", PROMISE])
+
+    # B-T4
+    def test_b_t4_when_a_food_moment_can_fire(self):
+        day2, _ = self.day2_of(3, draws=lambda t, pid: 0.0)
+        mara = day2.people["mara"]
+        in_turn(day2)
+
+        def due(t=0):
+            return day2.food_due(mara, t)
+        self.assertTrue(due())                                       # all of F1-F9 hold
+        mara.room = "back_room"
+        self.assertFalse(due())                                      # F2: not in the kitchen
+        mara.room = "kitchen"
+        day2.portions = 0
+        self.assertFalse(due())                                      # F2: empty shelf
+        day2.portions = 2
+        day2.present["kitchen"] = ["mara"]
+        self.assertFalse(due())                                      # F3: alone
+        in_turn(day2)
+        mara.hunger = 0.849
+        self.assertFalse(due())                                      # F4: very hungry
+        mara.hunger = 0.85
+        self.assertTrue(due())
+        for eaten in (1.0, 0.25):                                    # F5: a portion, or a part of a share
+            mara.eaten = eaten
+            self.assertFalse(due())
+        mara.eaten = 0.0
+        mara.last_food = 0
+        self.assertFalse(due(9))                                     # F6: 27 minutes after her last
+        self.assertTrue(due(10))                                     # 30 minutes after
+        mara.last_food = None
+        day2.food_turn = 0
+        self.assertFalse(due(0))                                     # F7: one a turn in the house
+        self.assertTrue(due(1))
+        day2.food_turn = None
+        chance = day2.food_chance(mara)
+        day2.food_draw = lambda t, pid: chance
+        self.assertFalse(due())                                      # F9: at the chance
+        day2.food_draw = lambda t, pid: chance - 1e-9
+        self.assertTrue(due())
+        out_of_turn(day2)
+        # F1: never on day 1, whatever the body and the draw.
+        day1, _ = self.v11_day1(3)
+        day1.food_draw = lambda t, pid: 0.0
+        in_turn(day1)
+        for p in day1.people.values():
+            p.hunger = 1.0
+            self.assertFalse(day1.food_due(p, 0), p.id)
+        out_of_turn(day1)
+        # F1: never in the night; F8: an aside's answer is not a moment.
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake"]}, QUIET)
+        for p in client.night_prompts():
+            self.assertNotIn("\n- eat:", p)
+        day2, client = self.day2_of(3, draws=lambda t, pid: 0.0)
+        in_turn(day2)
+        d = day2.decide_aside(mara, day2.people["leo"], "back_room", 0)
+        self.assertNotIn("food_moment", d)
+        self.assertEqual(d["option"], "accept_aside" if d["mode"] == "model" else "refuse_aside")
+        out_of_turn(day2)
+
+    # B-T5
+    def test_b_t5_the_chance_and_the_draw(self):
+        self.assertEqual((world.FOOD_RATE, world.FOOD_EVERY), ({"before yesterday": 0.07, "yesterday": 0.035}, 30))
+        day2, _ = self.day2_of(2)
+        self.assertEqual({p: q.ate_yesterday for p, q in day2.people.items()},
+                         {"daniel": None, "elena": None, "leo": None, "mara": 54})
+        for pid, (before, yesterday) in FOOD_CHANCES.items():
+            p = day2.people[pid]
+            p.ate_yesterday = None
+            self.assertEqual((day2.food_band(p), day2.food_chance(p)), ("before yesterday", before), pid)
+            p.ate_yesterday = 54
+            self.assertEqual((day2.food_band(p), day2.food_chance(p)), ("yesterday", yesterday), pid)
+            p.eaten = 0.25
+            self.assertEqual((day2.food_band(p), day2.food_chance(p)), ("this morning", 0), pid)
+        day2, _ = self.day2_of(1)                                    # Leo and Mara ate at minute 21
+        self.assertEqual({p: q.ate_yesterday for p, q in day2.people.items()},
+                         {"daniel": None, "elena": None, "leo": 21, "mara": 21})
+        day2, _ = self.day2_of(3)
+        self.assertEqual({q.ate_yesterday for q in day2.people.values()}, {None})
+        # A share's part on day 1 counts as eating yesterday.
+        day1, oracle = self.short_day1(NightScripted())
+        self.act(day1, day1.people["elena"], "share", None, t=1)
+        n = self.night.Night(day1, oracle).run()
+        day2 = Morning.next_day(day1, n, oracle)
+        self.assertEqual({q.ate_yesterday for q in day2.people.values()}, {3})
+        # The draw string, and the frequency over 100,000 draws.
+        day2, _ = self.day2_of(3)
+        del day2.food_draw
+        self.assertEqual(day2.food_draw(7, "leo"), random.Random("3:day2:food:7:leo").random())
+        for chance in (0.077, 0.0245):
+            hits = sum(random.Random(f"{s}:day2:food:4:daniel").random() < chance for s in range(100000))
+            self.assertLess(abs(hits / 100000 - chance), 0.003, chance)
+
+    # B-T6
+    def test_b_t6_the_moments_prompt_exactly(self):
+        order = self.order_at_0(3)
+        who = order[0]
+        day2, client = self.day2_of(3, draws=only(who, 0))
+        p = day2.people[who]
+        ordinary, orig = {}, day2.ask_model
+
+        def spy(q, t, opts, d, extra=None):
+            if d.get("food_moment"):
+                ordinary[q.id] = day2.prompt_for(q, t, day2.options_for(q), d.get("lull"))
+            return orig(q, t, opts, d, extra)
+        day2.ask_model = spy
+        day2.turn(0)
+        prompt = next(x for w, q, x in client.prompts if q == who and w == 0)
+        others = [q for q in data.ORDER if q != who]
+        self.assertEqual(option_lines(prompt), ["- eat: eat one of the portions"]
+                         + [f"- give_{q}: give one of the portions to {data.PEOPLE[q]['name']}" for q in others]
+                         + ["- share: share out what is left among everyone here"])
+        head = prompt.split("\nYour options:\n")[0]
+        self.assertEqual(head, ordinary[who].split("\nYour options:\n")[0] + "\n" + FOOD_BEFORE)
+        self.assertEqual(head.split("\n")[-1], FOOD_BEFORE)
+        d = next(x for x in day2.log[0]["decisions"] if x["person"] == who)
+        self.assertEqual(d["offered"], 5)
+        self.assertEqual(d["food_moment"]["band"], "before yesterday")
+        # The yesterday form, with the minute of the meal: seed 2's Mara ate at minute 54.
+        day2, client = self.day2_of(2, draws=only("mara", 0))
+        day2.people["mara"].hunger = 1.0
+        day2.turn(0)
+        prompt = next(x for w, q, x in client.prompts if q == "mara" and w == 0)
+        self.assertEqual(prompt.split("\nYour options:\n")[0].split("\n")[-1], FOOD_YESTERDAY.format(mm=54))
+        # Nobody else's prompt holds the line.
+        self.assertEqual([q for w, q, x in client.prompts if "Your hunger has the better of you" in x], ["mara"])
+
+    # B-T7
+    def test_b_t7_giving_and_the_answer(self):
+        o = self.order_at_0(3)
+        # Q had not acted yet: the answer is Q's turn.
+        giver, q = o[0], o[3]
+        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["eat_given"]}, only(giver, 0))
+        day2.turn(0)
+        ds = day2.log[0]["decisions"]
+        self.assertEqual([d["person"] for d in ds], [giver, q, o[1], o[2]])
+        self.assertEqual((ds[1]["option"], ds[1]["given_by"]), ("eat_given", giver))
+        name = data.PEOPLE[giver]["name"]
+        prompt = next(x for w, w2, x in client.prompts if w2 == q and w == 0)
+        self.assertEqual(prompt.split("\nYour options:\n")[0].split("\n")[-1],
+                         f"{name} has just handed you one of the portions.")
+        self.assertEqual(option_lines(prompt), [f"- eat_given: eat the portion {name} gave you",
+                                                "- refuse_given: refuse it, and put it back on the shelf"])
+        self.assertIn(f"{name} hands you one of the portions", ds[1]["triggers"])
+        Q = day2.people[q]
+        self.assertEqual(day2.portions, 1)
+        self.assertAlmostEqual(Q.hunger, 0.6 + 0.012 * data.PEOPLE[q]["hunger_rate"], places=9)
+        self.assertEqual(Q.eaten, 1)
+        self.assertEqual(day2.food_band(Q), "this morning")
+        # Q had already acted: an extra answer, and Q does not act again.
+        giver, q = o[3], o[0]
+        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["refuse_given"]}, only(giver, 0))
+        day2.turn(0)
+        ds = day2.log[0]["decisions"]
+        self.assertEqual([d["person"] for d in ds], [o[0], o[1], o[2], giver, q])
+        self.assertEqual(ds[4]["option"], "refuse_given")
+        self.assertEqual(day2.portions, 2)
+        self.assertEqual(day2.people[q].eaten, 0)
+        self.assertIn((f"{data.PEOPLE[q]['name']} puts the portion you gave back on the shelf", True),
+                      day2.people[giver].triggers)
+
+    # B-T8
+    def test_b_t8_what_the_others_perceive(self):
+        o = self.order_at_0(3)
+        names = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
+        # A gift eaten.
+        giver, q, w1, w2 = o[0], o[3], o[1], o[2]
+        G, Q = names[giver], names[q]
+        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["eat_given"]}, only(giver, 0))
+        day2.turn(0)
+        line = f"{G} gives one of the portions to {Q}, and {Q} eats it"
+        later = next(x for w, who, x in client.prompts if who == w1 and w == 0)
+        self.assertIn(f"Said and done in the kitchen this turn, before you, in order:\n1. {line}.\n", later)
+        ds = {d["person"]: d for d in day2.log[0]["decisions"]}
+        for w in (w1, w2):
+            self.assertIn(line, ds[w]["triggers"])
+            self.assertIn(f"min 00: {G} gave one of the portions to {Q}, and {Q} ate it (you saw it).",
+                          day2.people[w].sure)
+            g = day2.people[w].grudges[q]
+            him = data.PRONOUNS[q]["him"]
+            self.assertEqual(g.events[-1][1], f"{Q} ate a portion {G} gave {him}, in front of you at minute 00, "
+                                              f"while you were hungry")
+        self.assertNotIn(q, day2.people[giver].grudges)
+        self.assertIn(f"min 00: you gave one of the portions to {Q}, and {Q} ate it. 1 left.", day2.people[giver].sure)
+        self.assertIn(f"min 00: {G} gave you one of the portions, and you ate it. 1 left.", day2.people[q].sure)
+        # Nobody perceives the moment itself.
+        for who, p in day2.people.items():
+            self.assertFalse([x for x in p.memory + p.sure if "hunger" in str(x).lower()], who)
+        self.assertEqual([who for w, who, x in client.prompts if "Your hunger has the better of you" in x], [giver])
+        # A gift refused: back on the shelf, no grudge.
+        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["refuse_given"]}, only(giver, 0))
+        day2.turn(0)
+        for w in (w1, w2):
+            self.assertIn(f"min 00: {G} gave one of the portions to {Q}, and {Q} put it back on the shelf (you saw it).",
+                          day2.people[w].sure)
+            self.assertNotIn(q, day2.people[w].grudges)
+        self.assertIn(f"min 00: you gave one of the portions to {Q}, and {Q} put it back on the shelf.",
+                      day2.people[giver].sure)
+        later = next(x for w, who, x in client.prompts if who == w1 and w == 0)
+        self.assertIn(f"1. {G} gives one of the portions to {Q}; {Q} puts it back on the shelf.\n", later)
+        # Eating at a moment is eating as now; through a wall, nothing.
+        day2, client = self.day2_of(3, {giver: ["eat"]}, only(giver, 0))
+        day2.people[w2].room = "back_room"
+        day2.turn(0)
+        self.assertIn(f"min 00: {G} ate one of the portions (you saw it).", day2.people[w1].sure)
+        self.assertIn(giver, day2.people[w1].grudges)
+        self.assertFalse([x for x in day2.people[w2].memory if "kitchen" in x[1]])
+        self.assertNotIn(giver, day2.people[w2].grudges)
+        # A share at a moment is a share as now.
+        day2, client = self.day2_of(3, {giver: ["share"]}, only(giver, 0))
+        day2.turn(0)
+        self.assertEqual(day2.portions, 0)
+        self.assertIn(f"min 00: {G} shares out the last 2 portions between {', '.join(names[x] for x in [giver] + [y for y in data.ORDER if y != giver])}; "
+                      "you had your part.", day2.people[w1].sure)
+
+    # B-T9
+    def test_b_t9_fallbacks_never_eat_for_anyone(self):
+        o = self.order_at_0(3)
+        giver, q = o[0], o[3]
+        day2, _ = self.day2_of(3, draws=only(giver, 0))
+        day2.oracle.client = BrokenFor("Your hunger has the better of you")
+        day2.turn(0)
+        d = day2.log[0]["decisions"][0]
+        self.assertEqual((d["person"], d["mode"], d["option"]), (giver, "fallback", "silent"))
+        self.assertIn("food_moment", d)
+        self.assertEqual(day2.portions, 2)
+        self.assertEqual(day2.people[giver].last_food, 0)
+        G = data.PEOPLE[giver]["name"]
+        day2, _ = self.day2_of(3, draws=only(giver, 0))
+        day2.oracle.client = BrokenFor(f"{G} has just handed you one of the portions.", {giver: [f"give_{q}"]})
+        day2.turn(0)
+        dq = day2.log[0]["decisions"][1]
+        self.assertEqual((dq["person"], dq["mode"], dq["option"]), (q, "fallback", "refuse_given"))
+        self.assertEqual(day2.portions, 2)
+        self.assertEqual(day2.people[q].eaten, 0)
+
+    # B-T10
+    def test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache(self):
+        expected = {2: (0, "daniel", 3, 0.077), 3: (9, "mara", 3, 0.084)}
+        for seed in (1, 2, 3):
+            day1, _ = self.v11_day1(seed)
+            paired = PairedOracle(os.path.join(V12_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"), V6_MODEL, seed)
+            n = self.night.Night(day1, paired).run()
+            missed_at_night = len(paired.missed)
+            day2 = Morning.next_day(day1, n, paired)
+            first = None
+            for t in range(day2.turns):
+                day2.turn(t)
+                moments = [d for d in day2.log[-1]["decisions"] if d.get("food_moment")]
+                if moments:
+                    first = (t * 3, moments[0], day2.log[-1]["decisions"].index(moments[0]) + 1)
+                    break
+            if seed == 1:
+                self.assertIsNone(first)                                  # an empty shelf all morning
+                continue
+            minute, who, place, chance = expected[seed]
+            self.assertEqual((first[0], first[1]["person"], first[2]), (minute, who, place), seed)
+            self.assertEqual(first[1]["food_moment"]["chance"], chance)
+            self.assertLess(first[1]["food_moment"]["draw"], chance)
+            self.assertEqual(missed_at_night, 0, seed)
+            day2_missed = paired.missed[missed_at_night:]
+            self.assertTrue(day2_missed and "Your hunger has the better of you" in day2_missed[0], seed)
+
+    # B-T11
+    def test_b_t11_records_and_the_story(self):
+        prefs = {p: ["give_leo", "give_mara", "eat_given"] for p in data.ORDER}
+        with mock.patch.object(world.Morning, "food_draw", lambda self, t, pid: 0.0):
+            (meta, code), out = quiet_run(2, fake=True, config_path=CONFIG, runs_dir=self.dirs.runs,
+                                          cache_dir=self.dirs.cache, client=NightScripted(prefs))
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
+        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.md"))
+        acts = [a for t in tr["day2"]["turns"] for a in t["acts"]]
+        moments = [a for a in acts if a.get("food_moment")]
+        self.assertTrue(moments)
+        self.assertEqual(meta["day2"]["food_moments"], len(moments))
+        self.assertEqual(meta["day2"]["give_answers"], sum(a["option"] in ("eat_given", "refuse_given") for a in acts))
+        self.assertGreater(meta["day2"]["give_answers"], 0)
+        self.assertEqual(set(moments[0]["food_moment"]), {"band", "chance", "draw", "portions"})
+        self.assertIn(f"day2 food_moments: {len(moments)}", out)
+        self.assertIn(f"day2 give_answers: {meta['day2']['give_answers']}", out)
+        self.assertFalse([a for t in tr["day1"]["turns"] for a in t["acts"] if "food_moment" in a])
+        m = moments[0]["food_moment"]
+        n = m["portions"]
+        self.assertIn(f"**Food moment**, starving in the kitchen with {n} portion{'s' if n != 1 else ''} on the shelf; "
+                      f"last ate: not since before yesterday (chance {m['chance']:g} a turn, draw {m['draw']:.4f}).",
+                      story)
+        self.assertEqual(story.count("**Food moment**"), len(moments))
+        self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for a in acts))
+
+    # B-T12
+    def test_b_t12_v12_still_replays(self):
+        done = run_check("v12")
+        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
+        self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
+        self.assertIn("0 API calls", done.stdout)
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index a349da0..1ad9d54 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -85,6 +85,10 @@ LULL_EVERY = 12              # minutes since a person was last asked before a lu
 TRIP_HUNGER = 2              # the hunger level ("very hungry") that starts the trip concern
 TRIP_ON = True               # the trip concern (reports/trip_design.md); off only in tests
 TRIP_KINDS = tuple(TRIP_WHY)  # propose, volunteer, object, back, decline
+# The body's food moment on day 2 (reports/body_design.md, §2): the chance a turn, at impulsive 0.5,
+# by when they last ate; and the minutes between one person's moments.
+FOOD_RATE = {"before yesterday": 0.07, "yesterday": 0.035}
+FOOD_EVERY = 30
 
 KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
     "ask": "asked who took the can", "deny": "denied taking it",
@@ -97,6 +101,7 @@ KIND_DONE = {   # what a run of one kind of act looks like, told to the person w
     "propose": "said someone should go to the neighbour's house tonight",
     "volunteer": "offered to go there tonight", "object": "said someone should not go",
     "back": "said someone should be the one to go", "decline": "said you will not be the one to go",
+    "give": "given someone a portion", "eat_given": "eaten", "refuse_given": "refused a portion",
 }
 
 HUNGER_WORDS = ["a little hungry", "hungry", "very hungry", "starving"]
@@ -303,6 +308,11 @@ class Person:
         # prompts; and on day 2, what of day 1 still counts as yesterday's (None on day 1).
         self.tonight = []
         self.yesterday = None
+        # The food moment (reports/body_design.md, §2): the minute they last ate this morning; on day 2,
+        # the minute of yesterday's last meal (None: not since before yesterday); their last moment.
+        self.last_meal = None
+        self.ate_yesterday = None
+        self.last_food = None
 
     def grudge(self, against):
         return self.grudges.setdefault(against, Grudge())
@@ -354,6 +364,7 @@ class Morning:
         self.trip = None            # the trip concern once started: {"minute", "why", "asked"}
         self.trip_acts = []         # (minute, who, kind, target, words), every position taken
         self.trip_now = set()       # during the turn it starts: who is asked because of it
+        self.food_turn = None       # day 2: the turn of the house's last food moment
         if day != 4:
             return                  # day 2's opening is set up by next_day
         for p in self.people.values():
@@ -656,6 +667,93 @@ class Morning:
             return f"sit_{p.activity['with']}"
         return "silent"
 
+    # ---------- the body's food moment (reports/body_design.md, §2) ----------
+    def food_band(self, p):
+        """When they last ate, from their own records: "this morning", "yesterday" or "before yesterday"."""
+        if p.eaten > 0:
+            return "this morning"
+        return "yesterday" if p.ate_yesterday is not None else "before yesterday"
+
+    def food_chance(self, p):
+        """The chance a turn: the band's rate × (0.5 + impulsive) (§2.2); 0 once they have eaten this morning."""
+        band = self.food_band(p)
+        if band == "this morning":
+            return 0
+        return round(FOOD_RATE[band] * (0.5 + p.sheet["traits"]["impulsive"]), 4)
+
+    def food_draw(self, t, pid):
+        """This person's draw for this turn (F9): a string of its own, so no draw depends on order."""
+        return random.Random(f"{self.seed}:day2:food:{t}:{pid}").random()
+
+    def food_due(self, p, t):
+        """F1-F9 (§2.1): day 2, in the kitchen with food on the shelf and someone else there, starving,
+        nothing eaten this morning, no moment of theirs in FOOD_EVERY minutes or of anyone's this turn,
+        and their draw under their chance. Answers to an aside or a give never come here (F8)."""
+        if self.day == 4 or p.room != "kitchen" or self.portions <= 0 or not self.others_here(p):
+            return False
+        if hunger_level(p.hunger) < 3 or p.eaten > 0:
+            return False
+        minute = t * data.MINUTES_PER_TURN
+        if p.last_food is not None and minute - p.last_food < FOOD_EVERY:
+            return False
+        if self.food_turn == t:
+            return False
+        return self.food_draw(t, p.id) < self.food_chance(p)
+
+    def food_options(self, p):
+        """Food only (§2.4): eat, give a portion to each person here in the family's order, share."""
+        return ([Option("eat", "eat one of the portions", kind="eat")]
+                + [Option(f"give_{q.id}", f"give one of the portions to {q.name}", kind="give", target=q.id)
+                   for q in self.others_here(p)]
+                + [Option("share", "share out what is left among everyone here", kind="share")])
+
+    @staticmethod
+    def food_moment_line(p):
+        """The moment's last `Now` line (§2.4)."""
+        when = (f"you last ate yesterday, at minute {p.ate_yesterday:02d}" if p.ate_yesterday is not None
+                else "you have not eaten since before yesterday")
+        return (f"Your hunger has the better of you: {when}, and the food is on the shelf in front of you. "
+                "You cannot leave it there any longer.")
+
+    def decide_food(self, p, t):
+        """A food moment: it takes the place of their decision this turn. An answer that cannot be used
+        leaves them where they are and the food on the shelf (§2.7)."""
+        minute = t * data.MINUTES_PER_TURN
+        opts = self.food_options(p)
+        triggers = self.social_triggers(p, t)
+        p.triggers = []
+        d = {"person": p.id, "triggers": triggers, "offered": len(opts), "held_back": None,
+             "food_moment": {"band": self.food_band(p), "chance": self.food_chance(p),
+                             "draw": self.food_draw(t, p.id), "portions": self.portions}}
+        p.last_food = minute
+        self.food_turn = t
+        choice, why = self.ask_model(p, t, opts, d, self.food_moment_line(p))
+        if not choice:
+            opts = opts + [Option("silent", "stay put and say nothing", kind="silent")]
+            d.update(mode="fallback", invalid=why, option="silent", say=None)
+        opt = next(o for o in opts if o.id == d["option"])
+        d["label"] = opt.label
+        d["_opt"] = opt
+        return d
+
+    def decide_given(self, q, p, t):
+        """q has just been handed a portion by p: eat it, or put it back (§2.5). Always a model decision;
+        an answer that cannot be used puts it back."""
+        opts = [Option("eat_given", f"eat the portion {p.name} gave you", kind="eat_given", partner=p.id),
+                Option("refuse_given", "refuse it, and put it back on the shelf", kind="refuse_given", partner=p.id)]
+        handed = f"{p.name} hands you one of the portions"
+        triggers = [handed] + [text for text, new in q.triggers if text != handed]
+        q.triggers = []
+        d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts),
+             "held_back": None, "given_by": p.id}
+        choice, why = self.ask_model(q, t, opts, d, f"{p.name} has just handed you one of the portions.")
+        if not choice:
+            d.update(mode="fallback", invalid=why, option="refuse_given", say=None)
+        opt = next(o for o in opts if o.id == d["option"])
+        d["label"] = opt.label
+        d["_opt"] = opt
+        return d
+
     # ---------- what is inside them ----------
     def risen(self, p):
         """What has risen a level since they last decided with the model: "hunger", "guilt",
@@ -783,10 +881,12 @@ class Morning:
                 "back": "said you should be the one to go", "decline": "said they will not be the one to go",
                 }.get(h["kind"], "spoke to everyone")
 
-    def prompt_for(self, p, t, opts, lull=None, night=None):
+    def prompt_for(self, p, t, opts, lull=None, night=None, extra=None):
         """lull: for a lull moment, the minute the room was last stirred; None otherwise.
         night: the night's `Now` lines (reports/night_design.md, §3.2), which take the place of the
-        room, the turn and the pattern block; None by day."""
+        room, the turn and the pattern block; None by day.
+        extra: by day, a last `Now` line (a food moment's, or a handed portion's: reports/body_design.md,
+        §2.4-§2.5); None otherwise."""
         s = p.sheet
         minute = None if night is not None else t * data.MINUTES_PER_TURN
         system = SYSTEM if night is None else NIGHT_SYSTEM
@@ -824,6 +924,8 @@ class Morning:
         elif others:
             now.append(f"You are the first to act in the {room} this turn.")
         now += self.pattern(p)
+        if extra:
+            now.append(extra)
         return self.prompt_parts(p, opts, head, now, system, "this morning", minute)
 
     def prompt_parts(self, p, opts, head, now, system, when, minute):
@@ -1010,6 +1112,8 @@ class Morning:
                      "angry_at": d.get("angry_at"), "lull": d.get("lull"),
                      "trip_moment": d.get("trip_moment"),
                      "moved_to": opt.act["to"] if opt.act["kind"] in ("go", "accept_aside") else None}
+            if d.get("food_moment"):
+                entry["food_moment"] = d["food_moment"]
             tturn["acts"].append(entry)
             return opt, entry
 
@@ -1038,6 +1142,17 @@ class Morning:
                     entry["aside"] = {"with": q.id, "accepted": went}
                     if went:
                         entry["moved_to"] = opt.act["to"]
+                elif opt.act["kind"] == "give":
+                    # The one handed a portion answers now (reports/body_design.md, §2.5): their decision
+                    # for this turn if they had not acted yet, otherwise an extra answer.
+                    q = self.people[opt.act["target"]]
+                    if q.id in remaining:
+                        remaining.remove(q.id)
+                    place += 1
+                    dq = self.decide_given(q, p, t)
+                    qopt, _ = act(q, dq, room, place, f"handed a portion by {p.name}")
+                    d["came_of_it"] += f" {q.name} {'ate it' if qopt.id == 'eat_given' else 'put it back on the shelf'}."
+                    entry["came_of_it"] = d["came_of_it"]
         record["rooms"] = {r: [(q.name, q.activity["label"]) for q in self.people.values()
                                if start_room[q.id] == r] for r in data.ROOMS}
 
@@ -1082,12 +1197,12 @@ class Morning:
         self.log.append(record)
         self.transcript["turns"].append(tturn)
 
-    def ask_model(self, p, t, opts, d):
+    def ask_model(self, p, t, opts, d, extra=None):
         """One model decision: the prompt, the answer, and what it does to their suspicion and
-        grudge. They have now seen the levels their prompt showed."""
+        grudge. They have now seen the levels their prompt showed. extra: a last `Now` line."""
         minute = t * data.MINUTES_PER_TURN
         seen = p.levels()
-        prompt = self.prompt_for(p, t, opts, d.get("lull"))
+        prompt = self.prompt_for(p, t, opts, d.get("lull"), extra=extra)
         p.last_asked = minute
         text = self.oracle.ask(SYSTEM, prompt)
         p.seen = seen
@@ -1131,6 +1246,9 @@ class Morning:
 
     def decide(self, p, t):
         minute = t * data.MINUTES_PER_TURN
+        # The body's food moment comes before anything else (reports/body_design.md, §2.1).
+        if self.food_due(p, t):
+            return self.decide_food(p, t)
         opts = self.options_for(p)
         triggers = self.social_triggers(p, t)
         p.triggers = []
@@ -1260,6 +1378,7 @@ class Morning:
         target_id = aimed_at(opt.id) or (opt.act.get("target") if kind == "sit" else None)
         target = self.people[target_id] if target_id else None
         partner = self.people[opt.act["partner"]] if "partner" in opt.act else None
+        given_to = self.people[opt.act["target"]] if kind == "give" else None
         # Anything but staying put in silence, or staying seated with the same person, stirs the room.
         if not (kind == "silent" or (kind == "sit" and p.activity["kind"] == "sitting"
                                      and p.activity["with"] == target_id)):
@@ -1287,7 +1406,9 @@ class Morning:
                      "eat": "eating", "share": "sharing out the food",
                      "aside": f"asking {target.name if target else ''} to come aside",
                      "accept_aside": f"going aside with {partner.name if partner else ''}",
-                     "refuse_aside": "refusing to go aside"}.get(kind)
+                     "refuse_aside": "refusing to go aside",
+                     "give": f"handing {given_to.name if given_to else ''} a portion",
+                     "eat_given": "eating", "refuse_given": "putting the portion back on the shelf"}.get(kind)
             spoken_kind = kind if kind in SPEECH else "say"
             aimed = aimed_at(opt.id)
             new, why = self.newness.line(p.id, opt.id, [q.id for q in seen])
@@ -1513,6 +1634,7 @@ class Morning:
             self.portions -= 1
             p.hunger = max(0.0, p.hunger - 0.4)
             p.eaten += 1
+            p.last_meal = minute
             so_far.append(f"{p.name} eats one of the portions.")
             for q in seen:
                 q.sure.append(f"min {minute:02d}: {p.name} ate one of the portions (you saw it).")
@@ -1537,6 +1659,7 @@ class Morning:
             for q in eaters:
                 q.hunger = max(0.0, q.hunger - 0.4 * each)
                 q.eaten += each
+                q.last_meal = minute
             n, self.portions = self.portions, 0
             trig = f"{p.name} shares out the last {n} portion{'s' if n != 1 else ''} between {names}"
             so_far.append(trig + ".")
@@ -1546,4 +1669,61 @@ class Morning:
             p.sure.append(f"min {minute:02d}: you shared out the last {n} portions between {names}.")
             record["events"].append(f"{p.name} shared out {n} portions between {names}")
             return f"shared out the last {n} portions between {names}."
+        # A food moment's gift (reports/body_design.md, §2.5-§2.6): the portion leaves the shelf for
+        # the hands of the one it is given to, who answers at once; what the room sees is written then.
+        if kind == "give":
+            p.activity = {"kind": "idle", "label": f"handing {given_to.name} a portion"}
+            self.portions -= 1
+            record["events"].append(f"{p.name} gave a portion to {given_to.name}")
+            return f"gave one of the portions to {given_to.name}."
+        if kind == "eat_given":
+            giver, him = partner, data.PRONOUNS[p.id]["him"]
+            p.activity = {"kind": "idle", "label": "eating"}
+            p.hunger = max(0.0, p.hunger - 0.4)
+            p.eaten += 1
+            p.last_meal = minute
+            line = f"{giver.name} gives one of the portions to {p.name}, and {p.name} eats it"
+            so_far.append(line + ".")
+            for q in seen:
+                if q is giver:
+                    q.sure.append(f"min {minute:02d}: you gave one of the portions to {p.name}, and {p.name} ate it. "
+                                  f"{self.portions} left.")
+                    continue
+                q.sure.append(f"min {minute:02d}: {giver.name} gave one of the portions to {p.name}, and {p.name} "
+                              f"ate it (you saw it).")
+                # Watching someone eat while hungry, as for `eat`; not the giver, who chose it.
+                if hunger_level(q.hunger) >= 1:
+                    self.add_grudge(q, p, minute,
+                                    f"{p.name} ate a portion {giver.name} gave {him}, in front of you at minute "
+                                    f"{minute:02d}, while you were hungry",
+                                    f"{p.name} ate the portion {giver.name} gave {him} in front of {q.name}, "
+                                    f"who was hungry", record)
+            fact(f"{p.name} ate the portion {giver.name} gave {him}", line)
+            p.sure.append(f"min {minute:02d}: {giver.name} gave you one of the portions, and you ate it. "
+                          f"{self.portions} left.")
+            record["events"].append(f"{p.name} ate the portion {giver.name} gave {him}")
+            return f"ate the portion {giver.name} gave {him}; {self.portions} left."
+        if kind == "refuse_given":
+            giver, him = partner, data.PRONOUNS[p.id]["him"]
+            p.activity = {"kind": "idle", "label": "standing"}
+            self.portions += 1
+            line = f"{giver.name} gives one of the portions to {p.name}; {p.name} puts it back on the shelf"
+            so_far.append(line + ".")
+            why = f"{p.name} put back the portion {giver.name} gave {him}"
+            self.started_by(room, minute, why, d)
+            d["new_fact"] = why
+            for q in seen:
+                if q is giver:
+                    q.sure.append(f"min {minute:02d}: you gave one of the portions to {p.name}, and {p.name} put it "
+                                  f"back on the shelf.")
+                    self.perceive(q, minute, None, remember=False,
+                                  trigger=(f"{p.name} puts the portion you gave back on the shelf", True))
+                else:
+                    q.sure.append(f"min {minute:02d}: {giver.name} gave one of the portions to {p.name}, and "
+                                  f"{p.name} put it back on the shelf (you saw it).")
+                    self.perceive(q, minute, None, remember=False, trigger=(line, True))
+            p.sure.append(f"min {minute:02d}: {giver.name} gave you one of the portions, and you put it back on "
+                          f"the shelf.")
+            record["events"].append(f"{p.name} put back the portion {giver.name} gave {him}")
+            return f"put the portion {giver.name} gave {him} back on the shelf; {self.portions} left."
         return ""
```

## 7. Scratch scripts

`$S/replay_day1.py`:

```python
"""Read-only: day 1 of seeds 1-3 with the current code, replayed from cache/v11 (replay mode: no client, so
no API call can be made). Its story and transcript are compared with runs/v11 byte for byte."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from gemini import Cache, Oracle
from story import render
from world import Morning

MODEL = "gemini-3.5-flash-lite"
for seed in (1, 2, 3):
    name = f"daniel_ate_it-seed{seed}"
    oracle = Oracle(Cache(os.path.join("cache", "v11", f"{MODEL}-{name}.json")), MODEL, seed, client=None, replay=True)
    m = Morning(oracle, seed).run()
    text = render(m, seed, MODEL, f"python morning.py --seed {seed}")
    same = open(os.path.join("runs", "v11", name + ".md"), "rb").read() == text.encode("utf-8")
    tr = json.load(open(os.path.join("runs", "v11", name + ".transcript.json"), encoding="utf-8"))
    same_tr = tr == json.loads(json.dumps(m.transcript))
    print(f"{name}: day 1 replayed {oracle.from_cache} answers from cache/v11, {oracle.api_requests} API requests; "
          f"story {'IDENTICAL' if same else 'DIFFERS'} to runs/v11, transcript {'IDENTICAL' if same_tr else 'DIFFERS'}")
```

The before-output trimmer, `before_short.txt` from `before.txt`: each line over 240 characters is cut there, with the count of characters left out.

## 8. Commands, in order

From `Prototypes/llm-morning/`, all with `GEMINI_API_KEY` unset:
1. The baseline suite (146, OK).
2. `mkdir v12 && cp data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py night.py story.py talk.py world.py v12/`; `v12/check.py` written; `python v12/check.py` (IDENTICAL ×3).
3. `morning.py` default `--out v13`, `.gitignore` for v13's fake runs; commit `99f03d7`.
4. `BodyTest` written; `python -m unittest -v test_morning.BodyTest`: 10 fail (§2).
5. The change in `talk.py`, `world.py`, `night.py`, `story.py`, `morning.py`. `BodyTest`: one error. The story had no ordinal for a 5th decision in a turn, so `ORDINAL` gained `5th`. Then 12 OK.
6. The full suite: 1 failure, night_design's T3 (the promise line, §1). Its expected text was updated; the full suite then passed: 158, OK (§3).
7. The replays (§4) and the freeze check (§5); commit `db317c7`.
