# Implementation: the neutral food moment line, and `confront_<name>`

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, or in replay
mode, which has no client.
- Paths are relative to `Prototypes/llm-morning/`.
- `$S` is the session scratchpad (`…/scratchpad`). Its read-only replay scripts are in §6.

## Result

| | |
|---|---|
| Commits | **`7b899e5`** freeze v13, new runs default to v14. **`90133b4`** the neutral line and `confront_<name>`, with their tests. This report is committed on its own after them. |
| New tests | 4, in class `FoodConfrontTest`. Before the change: **3 fail, 1 passes**. After: **4 pass**. |
| The 1 that passed before | `test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches`. It guards against the change reaching day 1, so it can only pass before the change. |
| Full suite | **163 tests, OK** in 83.2 s, on the committed code (before: 159). |
| Existing tests changed | **5** (§2). All are in `BodyTest`, and each pinned the old moment line or the v12 pairing that this change ends. |
| Day 1 from the v11 caches | 55, 53, 45 answers, 0 API requests; story and transcript **IDENTICAL** to `runs/v11` (§4). |
| Frozen versions | **v1 to v13 all IDENTICAL**, 0 API calls (§4). |
| git status | Clean apart from the three old `runs/v6/*.replay.md` files. |

## 1. What was built

**The food moment's line** (`world.py` `FOOD_MOMENT_LINE`, `food_moment_line`). It is now exactly
food_wording_probe.md's variant B, the same for everyone:

```
You are starving, and there is food on the shelf in front of everyone.
```

- It replaces body_design §2.4's line, which named when the person last ate ("you have not eaten
  since before yesterday" or "you last ate yesterday, at minute NN") and ended "You cannot leave
  it there any longer."
- The band still sets the chance (§2.2 of the design), but the prompt no longer says it.
- The options keep their order: `eat`, `give_<q>` in family order, `share`. Nothing else in the
  moment changed: when it fires, its chance, its draws, the give answer, perception and records.

**`confront_<name>`** (`world.py` `options_for`, `line_text`, `heard_verb`, `apply`, `KIND_DONE`;
`talk.py`).
- **Offered:** one per person present, labelled `(speech) confront <Name> about something they
  did`. It comes after the accusation and confession options and before the reassurances.
  - It is offered only when the morning is not day 1 (`self.day != 4`), so day-1 prompts are
    unchanged.
- **"From the night onward",** read as: every day-2 decision (`options_for`).
  - The night's own asks (bedtime, reactions, answers) have fixed option sets of their own (night_design
    §3.2–§3.5), and are not changed.
  - So the v12 and v13 night prompts are byte-identical, and the night still pairs with their
    caches (B-T10, §2).
- **What it is:**
  - a speech kind, `confront`, aimed at the person (`talk.SPEECH`, `act_of`, `aimed_at`);
  - like every speech kind, it is held back after three turns in a row;
  - the person confronted is "just spoken to", so they act next.
- **What others hear:** `<Name> confronts <Q>: "<words>"`, or `<Name> confronts you: "<words>"`
  for the one confronted. It is in their memory lines, in the turn's "Said and done", in
  `morning.said` (to: `<Q>`), and in the story's "What was said".
- **What the speaker keeps:** `you confronted <Q>.` with their feeling, in memory, and
  `min MM, you confronted <Q>.` in "Your own last words". The words are not kept, as for every
  speech kind.
- **The transcript act:** the option `confront_<q>` and its words.
- **Newness:** a confrontation is new the first time the speaker confronts that person ("a
  confrontation"), and not new after ("a confrontation they had made before"), as an accusation
  is. The brief does not say; without it, a confrontation would count as a remark that never
  keeps a conversation going.
- **Never an accusation about the can:**
  - it sets no `accused_by` and no `heard_question`;
  - it raises no grudge for a false accusation, and no guilt for the culprit;
  - it is not listed under the story's "Accusations";
  - it is not in the day-2 carry-in's accusation line (C4, built from `accuse_*` only).
  - The test checks each of these (§3).

**What a v14 run would see because of this.** Every day-2 prompt now lists the `confront_*`
options. So:
- a v14 run cannot answer any day-2 prompt from the v12 or v13 caches: all of day 2 is live;
- the night still pairs.

## 2. Existing tests changed

| Test | Why | Change |
|---|---|---|
| `BodyTest.test_b_t6_the_moments_prompt_exactly` | Pinned the old line in both band forms. | Expects the neutral line, the same for seed 2's Mara, who ate yesterday. |
| `BodyTest.test_b_t8_what_the_others_perceive` | Found the chooser's prompt by the old line. | Finds it by the new line. |
| `BodyTest.test_b_t9_fallbacks_never_eat_for_anyone` | Broke the answer to the prompt holding the old line. | Breaks the answer to the prompt holding the new line. |
| `BodyTest.test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache` | Expected day 2's first missed prompt to be the moment's: day 2 paired with the v12 cache until then. Every day-2 prompt now offers `confront_*`, so day 2's first prompt is already a miss. | Still checks the night pairs fully (0 misses), and that the first moment falls at seed 2 min 00 (Daniel, 3rd) and seed 3 min 09 (Mara, 3rd) with its chance. Now expects day 2's first miss to hold `confront_`, and exactly one missed prompt to hold the moment's line. |
| The constants above `BodyTest` | `FOOD_BEFORE` and `FOOD_YESTERDAY` held the old line. | Replaced by `NEUTRAL_FOOD`. |

## 3. Tests

**Before the change** (written first, on the code at `7b899e5`):

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.FoodConfrontTest
test_a_confrontation_is_recorded_and_remembered_as_one (test_morning.FoodConfrontTest.test_a_confrontation_is_recorded_and_remembered_as_one) ... FAIL
test_confront_is_offered_on_day2_and_not_on_day1 (test_morning.FoodConfrontTest.test_confront_is_offered_on_day2_and_not_on_day1) ... FAIL
test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches (test_morning.FoodConfrontTest.test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches) ... ok
test_the_food_moment_line_is_the_neutral_one (test_morning.FoodConfrontTest.test_the_food_moment_line_is_the_neutral_one) ... FAIL

======================================================================
FAIL: test_a_confrontation_is_recorded_and_remembered_as_one (test_morning.FoodConfrontTest.test_a_confrontation_is_recorded_and_remembered_as_one)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3571, in test_a_confrontation_is_recorded_and_remembered_as_one
    self.assertEqual(act["option"], "confront_daniel")
AssertionError: 'silent' != 'confront_daniel'
- silent
+ confront_daniel


======================================================================
FAIL: test_confront_is_offered_on_day2_and_not_on_day1 (test_morning.FoodConfrontTest.test_confront_is_offered_on_day2_and_not_on_day1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3550, in test_confront_is_offered_on_day2_and_not_on_day1
    self.assertEqual([i for i in opts if CONFRONT_IDS.match(i)], [f"confront_{q}" for q in others], p.id)
AssertionError: Lists differ: [] != ['confront_elena', 'confront_leo', 'confront_mara']

Second list contains 3 additional elements.
First extra element 0:
'confront_elena'

- []
+ ['confront_elena', 'confront_leo', 'confront_mara'] : daniel

======================================================================
FAIL: test_the_food_moment_line_is_the_neutral_one (test_morning.FoodConfrontTest.test_the_food_moment_line_is_the_neutral_one)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3519, in test_the_food_moment_line_is_the_neutral_one
    self.assertEqual(self.last_now_line(prompt), NEUTRAL_FOOD)
AssertionError: 'Your hunger has the better of you: you have [113 chars]ger.' != 'You are starving, and there is food on the s[22 chars]one.'
- Your hunger has the better of you: you have not eaten since before yesterday, and the food is on the shelf in front of you. You cannot leave it there any longer.
+ You are starving, and there is food on the shelf in front of everyone.


----------------------------------------------------------------------
Ran 4 tests in 0.552s

FAILED (failures=3)
exit=1
```

**After the change** (the full suite on the committed code, `90133b4`): the new tests, the changed tests, and the summary. Every other test line reads `ok`.

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning
…
test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache (test_morning.BodyTest.test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache) ... ok
test_b_t6_the_moments_prompt_exactly (test_morning.BodyTest.test_b_t6_the_moments_prompt_exactly) ... ok
test_b_t8_what_the_others_perceive (test_morning.BodyTest.test_b_t8_what_the_others_perceive) ... ok
test_b_t9_fallbacks_never_eat_for_anyone (test_morning.BodyTest.test_b_t9_fallbacks_never_eat_for_anyone) ... ok
test_a_confrontation_is_recorded_and_remembered_as_one (test_morning.FoodConfrontTest.test_a_confrontation_is_recorded_and_remembered_as_one) ... ok
test_confront_is_offered_on_day2_and_not_on_day1 (test_morning.FoodConfrontTest.test_confront_is_offered_on_day2_and_not_on_day1) ... ok
test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches (test_morning.FoodConfrontTest.test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches) ... ok
test_the_food_moment_line_is_the_neutral_one (test_morning.FoodConfrontTest.test_the_food_moment_line_is_the_neutral_one) ... ok
Ran 163 tests in 83.178s

OK
exit=0
```

**On the way** (§7): the first full run after the change had **4 failures**: B-T6, B-T8, B-T9 and B-T10, as §2 says. After the test updates of §2, the suite passed.

## 4. Replays

**Day 1 with the new code, from `cache/v11`** (`$S/impl/replay_day1.py`, §6), and every frozen version's `check.py`:

```
$ python $S/impl/replay_day1.py
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
$ python v13/check.py
daniel_ate_it-seed1: replayed 91 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 87 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
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
$ python v8/check.py
daniel_ate_it_leo_heard-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v7/check.py
daniel_ate_it-seed1: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 48 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 33 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 18 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v6/check.py
daniel_ate_it-seed1: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 66 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 44 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 43 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v5/check.py
daniel_ate_it-gemma-seed1: replayed 21 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed2: replayed 13 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed3: replayed 20 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed4: replayed 19 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed5: replayed 14 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
mara_ate_it-seed1: replayed 46 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
mara_ate_it-seed2: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
mara_ate_it-seed3: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
miscount-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
miscount-seed2: replayed 93 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
miscount-seed3: replayed 70 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

```
$ python v4/check.py
seed 1: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 4: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 5: replayed 41 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v3/check.py
seed 1: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 30 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v2/check.py
seed 1: replayed 7 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 11 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

**v1** has no `check.py`. Its `morning.py --replay` writes a `.replay.md` beside the run. So `$S/confront/v1_replay.py` calls v1's own `run(replay=True)` against a temporary copy of `runs/daniel_ate_it-seedN.md` and the first version's `cache/`:

```
$ env -u GEMINI_API_KEY python $S/confront/v1_replay.py
v1 seed 1: exit 0; api_requests 0; byte for byte against ..\..\..\..\..\..\AppData\Local\Temp\v1-replay-4cs68n4l\daniel_ate_it-seed1.md: IDENTICAL
v1 seed 2: exit 0; api_requests 0; byte for byte against ..\..\..\..\..\..\AppData\Local\Temp\v1-replay-4cs68n4l\daniel_ate_it-seed2.md: IDENTICAL
v1 seed 3: exit 0; api_requests 0; byte for byte against ..\..\..\..\..\..\AppData\Local\Temp\v1-replay-4cs68n4l\daniel_ate_it-seed3.md: IDENTICAL
```

## 5. The diffs

**The freeze** (`7b899e5`). `v13/` holds the code at `73430ce`, byte for byte: each copied file was compared with `cmp` against the working tree before the change, with no difference, and `v13/morning.py` against `git show HEAD:…/morning.py`. `v13/check.py` replays its three runs IDENTICAL (§4).

```
$ git show 7b899e5 --stat
commit 7b899e518b79776deb55497bc647c0fc06843c91
LLM morning: freeze v13, new runs default to v14

 Prototypes/llm-morning/.gitignore      |    2 +
 Prototypes/llm-morning/morning.py      |   12 +-
 Prototypes/llm-morning/v13/check.py    |   66 ++
 Prototypes/llm-morning/v13/data.py     |  208 ++++
 Prototypes/llm-morning/v13/gemini.py   |  270 +++++
 Prototypes/llm-morning/v13/metrics.py  |  182 ++++
 Prototypes/llm-morning/v13/metrics3.py |  141 +++
 Prototypes/llm-morning/v13/metrics4.py |  149 +++
 Prototypes/llm-morning/v13/metrics5.py |  152 +++
 Prototypes/llm-morning/v13/morning.py  |  230 +++++
 Prototypes/llm-morning/v13/night.py    |  668 ++++++++++++
 Prototypes/llm-morning/v13/story.py    |  541 ++++++++++
 Prototypes/llm-morning/v13/talk.py     |  133 +++
 Prototypes/llm-morning/v13/world.py    | 1740 ++++++++++++++++++++++++++++++++
 14 files changed, 4488 insertions(+), 6 deletions(-)
```

Without the eleven copied files:

```diff
diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index d890b42..f306f41 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -27,3 +27,5 @@ runs/v12/fake/
 cache/v12/fake-*
 runs/v13/fake/
 cache/v13/fake-*
+runs/v14/fake/
+cache/v14/fake-*
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 18f2a42..96c450a 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -9,9 +9,9 @@ writes them as one story (reports/night_design.md).
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v13; v4 replays
-                      the fourth version's runs; v5/check.py to v12/check.py replay the
-                      fifth's to twelfth's)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v14; v4 replays
+                      the fourth version's runs; v5/check.py to v13/check.py replay the
+                      fifth's to thirteenth's)
 
 Day 1 is the morning of the count; then the night; then day 2. The model names and call limits
 are in config.json; the call limit counts each of the three apart. The key is read from
@@ -80,13 +80,13 @@ def day_meta(m, scene):
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v13"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v14"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v12/ can still replay.
+    # cache/vN after), which v1/ to v13/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -219,7 +219,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v13")
+    ap.add_argument("--out", default="v14")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/v13/check.py b/Prototypes/llm-morning/v13/check.py
new file mode 100644
index 0000000..fed208a
--- /dev/null
+++ b/Prototypes/llm-morning/v13/check.py
@@ -0,0 +1,66 @@
+"""Replays the three thirteenth-version runs from their cache and checks their stories.
+
+    python v13/check.py
+
+v13/ is a frozen copy of the code that made the runs reports/body_v13.md describes
+(daniel_ate_it: day 1 from the v11 answers, then the night and day 2 with the promise line and the food
+moment of reports/body_design.md).
+Replaying makes no API calls. Each replayed story must come out byte for byte as runs/v13/<name>.md,
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
+from gemini import Cache, Oracle                         # noqa: E402  (v13's own modules)
+from night import Night                                  # noqa: E402
+from story import render, render_day2, render_night      # noqa: E402
+from world import Morning                                # noqa: E402
+
+# (scenario, model key, model name, seeds), as the runs in runs/v13 were made.
+RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3))]
+
+
+def main():
+    ok = True
+    for scenario, key, model, seeds in RUNS:
+        for seed in seeds:
+            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
+            cache = Cache(os.path.join(ROOT, "cache", "v13", f"{model}-{name}.json"))
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
+            base = os.path.join(ROOT, "runs", "v13", name)
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

**The change** (`90133b4`):

```
$ git show 90133b4 --stat
commit 90133b4012dd42e727c9ce1d711752266b7cce06
LLM morning: the neutral food moment line, and confront_<name> from the night on

 Prototypes/llm-morning/talk.py         |  18 +++--
 Prototypes/llm-morning/test_morning.py | 130 ++++++++++++++++++++++++++++++---
 Prototypes/llm-morning/world.py        |  20 +++--
 3 files changed, 145 insertions(+), 23 deletions(-)
```

```diff
diff --git a/Prototypes/llm-morning/talk.py b/Prototypes/llm-morning/talk.py
index d49d224..2d21866 100644
--- a/Prototypes/llm-morning/talk.py
+++ b/Prototypes/llm-morning/talk.py
@@ -6,7 +6,8 @@ Knows nothing about the house beyond room names and option ids.
 """
 
 SPEECH = ("ask", "deny", "accuse", "confess", "reassure", "say",
-          "propose", "volunteer", "object", "back", "decline")     # the last five: the trip
+          "propose", "volunteer", "object", "back", "decline",     # these five: the trip
+          "confront")       # from the night on (reports/food_confront_impl.md)
 
 
 def act_of(option):
@@ -17,7 +18,8 @@ def act_of(option):
     to it or to one person going, backing one person to go, and declining to go. Day 2 words them
     anew (reports/night_design.md, §6) with the same kinds: nobody_goes, keep_<q>_home, send_<q>,
     still_going (a restated offer) and refuse_to_go. Giving a portion to one person at a food
-    moment (reports/body_design.md, §2.4) is `give`, aimed at nobody."""
+    moment (reports/body_design.md, §2.4) is `give`, aimed at nobody. Confronting one person about
+    something they did, other than taking the can, is `confront` (reports/food_confront_impl.md)."""
     if option == "ask_who":
         return "ask", None
     if option == "propose_trip":
@@ -38,7 +40,7 @@ def act_of(option):
         return "object", option[len("keep_"):-len("_home")]
     if option.startswith("send_"):
         return "back", option[len("send_"):]
-    for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object", "give"):
+    for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object", "give", "confront"):
         if option.startswith(prefix + "_"):
             return prefix, option[len(prefix) + 1:]
     return option, None     # silent, deny, confess, search, eat, share, volunteer, decline
@@ -47,7 +49,7 @@ def act_of(option):
 def aimed_at(option):
     """The person a line is aimed at, or None for a line to everyone in the room."""
     kind, target = act_of(option)
-    return target if kind in ("accuse", "reassure", "aside", "back", "object") else None
+    return target if kind in ("accuse", "reassure", "aside", "back", "object", "confront") else None
 
 
 # What a position on the trip is, for the story (reports/trip_design.md, §3.3).
@@ -58,8 +60,8 @@ TRIP_WHY = {"propose": "a proposal", "volunteer": "an offer to go", "object": "a
 class Newness:
     """Decides whether a spoken line adds something. New: a question, an accusation, a
     denial of a new accusation, a confession, a position on the trip the speaker has not
-    taken before. Not new: reassurance, a stance the speaker has taken before this morning,
-    and any other remark (the rules cannot read what free words add). New facts and people coming in are handled by the caller."""
+    taken before, a confrontation of someone they had not confronted before. Not new:
+    reassurance, a stance the speaker has taken before this morning, and any other remark (the rules cannot read what free words add). New facts and people coming in are handled by the caller."""
 
     def __init__(self):
         self.stances = {}        # speaker -> stances already taken this morning
@@ -84,6 +86,10 @@ class Newness:
             pending = self.unanswered.pop(speaker, set())
             return (bool(pending), "a denial of a new accusation" if pending
                     else "a denial with no new accusation to answer")
+        if kind == "confront":          # new the first time toward that person, as an accusation
+            new = ("confront", target) not in taken
+            taken.add(("confront", target))
+            return new, "a confrontation" if new else "a confrontation they had made before"
         if kind == "reassure":
             return False, "reassurance"
         if kind in TRIP_WHY:
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 8036700..ec4c0de 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -3052,10 +3052,9 @@ class NightTest(unittest.TestCase):
 
 V12_CACHE = os.path.join(HERE, "cache", "v12")
 PROMISE = "You said you would go to the neighbour's house tonight. If you are going, it is now."
-FOOD_BEFORE = ("Your hunger has the better of you: you have not eaten since before yesterday, and the food is on the "
-               "shelf in front of you. You cannot leave it there any longer.")
-FOOD_YESTERDAY = ("Your hunger has the better of you: you last ate yesterday, at minute {mm}, and the food is on the "
-                  "shelf in front of you. You cannot leave it there any longer.")
+# The food moment's line: food_wording_probe.md's variant B, the same for everyone (food_confront_impl.md).
+# body_design §2.4's line, which named when they last ate, was replaced by it.
+NEUTRAL_FOOD = "You are starving, and there is food on the shelf in front of everyone."
 # The design's table (reports/body_design.md, §2.2): (not since before yesterday, ate yesterday).
 FOOD_CHANCES = {"daniel": (0.077, 0.0385), "elena": (0.0525, 0.0263), "leo": (0.049, 0.0245), "mara": (0.084, 0.042)}
 
@@ -3284,19 +3283,19 @@ class BodyTest(unittest.TestCase):
                          + [f"- give_{q}: give one of the portions to {data.PEOPLE[q]['name']}" for q in others]
                          + ["- share: share out what is left among everyone here"])
         head = prompt.split("\nYour options:\n")[0]
-        self.assertEqual(head, ordinary[who].split("\nYour options:\n")[0] + "\n" + FOOD_BEFORE)
-        self.assertEqual(head.split("\n")[-1], FOOD_BEFORE)
+        self.assertEqual(head, ordinary[who].split("\nYour options:\n")[0] + "\n" + NEUTRAL_FOOD)
+        self.assertEqual(head.split("\n")[-1], NEUTRAL_FOOD)
         d = next(x for x in day2.log[0]["decisions"] if x["person"] == who)
         self.assertEqual(d["offered"], 5)
         self.assertEqual(d["food_moment"]["band"], "before yesterday")
-        # The yesterday form, with the minute of the meal: seed 2's Mara ate at minute 54.
+        # Seed 2's Mara ate yesterday, at minute 54: the line is the same.
         day2, client = self.day2_of(2, draws=only("mara", 0))
         day2.people["mara"].hunger = 1.0
         day2.turn(0)
         prompt = next(x for w, q, x in client.prompts if q == "mara" and w == 0)
-        self.assertEqual(prompt.split("\nYour options:\n")[0].split("\n")[-1], FOOD_YESTERDAY.format(mm=54))
+        self.assertEqual(prompt.split("\nYour options:\n")[0].split("\n")[-1], NEUTRAL_FOOD)
         # Nobody else's prompt holds the line.
-        self.assertEqual([q for w, q, x in client.prompts if "Your hunger has the better of you" in x], ["mara"])
+        self.assertEqual([q for w, q, x in client.prompts if NEUTRAL_FOOD in x], ["mara"])
 
     # B-T7
     def test_b_t7_giving_and_the_answer(self):
@@ -3359,7 +3358,7 @@ class BodyTest(unittest.TestCase):
         # Nobody perceives the moment itself.
         for who, p in day2.people.items():
             self.assertFalse([x for x in p.memory + p.sure if "hunger" in str(x).lower()], who)
-        self.assertEqual([who for w, who, x in client.prompts if "Your hunger has the better of you" in x], [giver])
+        self.assertEqual([who for w, who, x in client.prompts if NEUTRAL_FOOD in x], [giver])
         # A gift refused: back on the shelf, no grudge.
         day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["refuse_given"]}, only(giver, 0))
         day2.turn(0)
@@ -3391,7 +3390,7 @@ class BodyTest(unittest.TestCase):
         o = self.order_at_0(3)
         giver, q = o[0], o[3]
         day2, _ = self.day2_of(3, draws=only(giver, 0))
-        day2.oracle.client = BrokenFor("Your hunger has the better of you")
+        day2.oracle.client = BrokenFor(NEUTRAL_FOOD)
         day2.turn(0)
         d = day2.log[0]["decisions"][0]
         self.assertEqual((d["person"], d["mode"], d["option"]), (giver, "fallback", "silent"))
@@ -3431,8 +3430,11 @@ class BodyTest(unittest.TestCase):
             self.assertEqual(first[1]["food_moment"]["chance"], chance)
             self.assertLess(first[1]["food_moment"]["draw"], chance)
             self.assertEqual(missed_at_night, 0, seed)
+            # Since food_confront_impl.md every day-2 prompt offers confront_*, so day 2 no longer pairs with
+            # the v12 cache: its first prompt is already a miss. The moment still falls where its draws put it.
             day2_missed = paired.missed[missed_at_night:]
-            self.assertTrue(day2_missed and "Your hunger has the better of you" in day2_missed[0], seed)
+            self.assertTrue(day2_missed and "\n- confront_" in day2_missed[0], seed)
+            self.assertEqual(sum(NEUTRAL_FOOD in p for p in day2_missed), 1, seed)
 
     # B-T11
     def test_b_t11_records_and_the_story(self):
@@ -3492,6 +3494,110 @@ class BodyTest(unittest.TestCase):
         self.assertIn("0 API calls", done.stdout)
 
 
+CONFRONT_IDS = re.compile(r"^confront_\w+$")
+
+
+class FoodConfrontTest(unittest.TestCase):
+    """The neutral food moment line (food_wording_probe.md, variant B) and confront_<q> from the night on
+    (reports/food_confront_impl.md)."""
+
+    setUp = NightTest.setUp
+    tearDown = NightTest.tearDown
+    path = NightTest.path
+    v11_day1 = NightTest.v11_day1
+    short_day1 = NightTest.short_day1
+    day2_of = BodyTest.day2_of
+    order_at_0 = BodyTest.order_at_0
+
+    def last_now_line(self, prompt):
+        return prompt.split("\nYour options:\n")[0].split("\n")[-1]
+
+    def test_the_food_moment_line_is_the_neutral_one(self):
+        who = self.order_at_0(3)[0]
+        day2, client = self.day2_of(3, draws=only(who, 0))
+        day2.turn(0)
+        prompt = next(x for w, q, x in client.prompts if q == who and w == 0)
+        self.assertEqual(self.last_now_line(prompt), NEUTRAL_FOOD)
+        self.assertNotIn("Your hunger has the better of you", prompt)
+        others = [q for q in data.ORDER if q != who]
+        self.assertEqual(option_lines(prompt), ["- eat: eat one of the portions"]          # the order is kept
+                         + [f"- give_{q}: give one of the portions to {data.PEOPLE[q]['name']}" for q in others]
+                         + ["- share: share out what is left among everyone here"])
+        # The same line whoever it is and whenever they last ate: seed 2's Mara ate yesterday.
+        day2, client = self.day2_of(2, draws=only("mara", 0))
+        day2.people["mara"].hunger = 1.0
+        day2.turn(0)
+        prompt = next(x for w, q, x in client.prompts if q == "mara" and w == 0)
+        self.assertEqual(self.last_now_line(prompt), NEUTRAL_FOOD)
+        self.assertEqual([q for w, q, x in client.prompts if NEUTRAL_FOOD in x], ["mara"])
+
+    def test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches(self):
+        for seed, served in V11_SERVED.items():
+            name = f"daniel_ate_it-seed{seed}"
+            oracle = Oracle(Cache(os.path.join(V11_CACHE, f"{V6_MODEL}-{name}.json")), V6_MODEL, seed, replay=True)
+            day1 = Morning(oracle, seed).run()          # replay mode: any changed prompt is a cache miss
+            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
+            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+            for p in day1.people.values():
+                self.assertFalse([o.id for o in day1.options_for(p) if CONFRONT_IDS.match(o.id)], (seed, p.id))
+
+    def test_confront_is_offered_on_day2_and_not_on_day1(self):
+        day2, _ = self.day2_of(3)
+        in_turn(day2)
+        for p in day2.people.values():
+            opts = {o.id: o for o in day2.options_for(p)}
+            others = [q for q in data.ORDER if q != p.id]
+            self.assertEqual([i for i in opts if CONFRONT_IDS.match(i)], [f"confront_{q}" for q in others], p.id)
+            for q in others:
+                o = opts[f"confront_{q}"]
+                self.assertEqual((o.label, o.speech), (f"confront {data.PEOPLE[q]['name']} about something they did",
+                                                       True))
+        out_of_turn(day2)
+        m, _ = scripted(silent, self.dirs, turns=1)
+        m.portions = 0
+        m.turn(1)                                           # day 1, with the trip open too
+        for p in m.people.values():
+            self.assertFalse([o.id for o in m.options_for(p) if CONFRONT_IDS.match(o.id)], p.id)
+
+    def test_a_confrontation_is_recorded_and_remembered_as_one(self):
+        day2, client = self.day2_of(1, {"mara": ["confront_daniel"]})
+        dan, mara, leo = day2.people["daniel"], day2.people["mara"], day2.people["leo"]
+        accused_before, guilt_before = dict(dan.accused_by), list(dan.guilt_events)
+        grudges_before = {t: g.strength for t, g in dan.grudges.items()}
+        day2.turn(0)
+        day2.finish()
+        act = next(a for a in day2.transcript["turns"][0]["acts"] if a["who"] == "mara")
+        words = act["words"]
+        self.assertEqual(act["option"], "confront_daniel")
+        self.assertTrue(words)
+        self.assertIn((0, f'Mara confronts you: "{words}"'), dan.memory)
+        self.assertIn((0, f'Mara confronts Daniel: "{words}"'), leo.memory)
+        self.assertIn((0, "you confronted Daniel. You felt tense."), mara.memory)
+        self.assertIn("min 00, you confronted Daniel.", mara.said_lines)
+        said = next(s for s in day2.said if s["who"] == "Mara")
+        self.assertEqual((said["to"], said["text"]), ("Daniel", f'Mara confronts Daniel: "{words}"'))
+        # Never an accusation about the can.
+        for p in day2.people.values():
+            self.assertFalse([x for x in p.memory if "accuses" in x[1] or "accused" in x[1]], p.id)
+        self.assertEqual(dan.accused_by, accused_before)
+        self.assertEqual(dan.guilt_events, guilt_before)
+        self.assertEqual({t: g.strength for t, g in dan.grudges.items()}, grudges_before)
+        self.assertNotIn("accus", day2.said[0]["text"])
+        story = render_day2_text(day2)
+        self.assertIn("- Accusations: none.", story)
+        self.assertIn('Mara confronts Daniel: "', story)
+        # The one confronted acts next, spoken to, not accused.
+        d = next(x for x in day2.log[0]["decisions"] if x["person"] == "daniel")
+        if d["place"] > [x for x in day2.log[0]["decisions"] if x["person"] == "mara"][0]["place"]:
+            self.assertEqual(d["order_reason"], "just spoken to by Mara")
+
+
+def render_day2_text(day2):
+    from story import render_day2
+    return render_day2(day2)
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index a93a7b1..5090863 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -89,6 +89,7 @@ TRIP_KINDS = tuple(TRIP_WHY)  # propose, volunteer, object, back, decline
 # by when they last ate; and the minutes between one person's moments.
 FOOD_RATE = {"before yesterday": 0.07, "yesterday": 0.035}
 FOOD_EVERY = 30
+FOOD_MOMENT_LINE = "You are starving, and there is food on the shelf in front of everyone."
 
 KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
     "ask": "asked who took the can", "deny": "denied taking it",
@@ -102,6 +103,7 @@ KIND_DONE = {   # what a run of one kind of act looks like, told to the person w
     "volunteer": "offered to go there tonight", "object": "said someone should not go",
     "back": "said someone should be the one to go", "decline": "said you will not be the one to go",
     "give": "given someone a portion", "eat_given": "eaten", "refuse_given": "refused a portion",
+    "confront": "confronted someone",
 }
 
 HUNGER_WORDS = ["a little hungry", "hungry", "very hungry", "starving"]
@@ -446,6 +448,12 @@ class Morning:
                                    kind="accuse", target=q.id))
             if p.id == self.culprit and not p.confessed:
                 opts.append(Option("confess", "admit taking it", True, kind="confess"))
+            # From the night on, something someone did other than taking the can can be put to them
+            # (reports/food_confront_impl.md); day 1 keeps its options, so it replays.
+            if self.day != 4:
+                for q in others:
+                    opts.append(Option(f"confront_{q.id}", f"confront {q.name} about something they did", True,
+                                       kind="confront", target=q.id))
             for q in others:
                 if q.id in p.grudges and p.grudges[q.id].strength >= 3:
                     continue
@@ -718,11 +726,9 @@ class Morning:
 
     @staticmethod
     def food_moment_line(p):
-        """The moment's last `Now` line (§2.4)."""
-        when = (f"you last ate yesterday, at minute {p.ate_yesterday:02d}" if p.ate_yesterday is not None
-                else "you have not eaten since before yesterday")
-        return (f"Your hunger has the better of you: {when}, and the food is on the shelf in front of you. "
-                "You cannot leave it there any longer.")
+        """The moment's last `Now` line: only the situation, so the choice stays the person's
+        (reports/food_wording_probe.md, variant B; reports/food_confront_impl.md)."""
+        return FOOD_MOMENT_LINE
 
     def decide_food(self, p, t):
         """A food moment: it takes the place of their decision this turn. An answer that cannot be used
@@ -885,6 +891,7 @@ class Morning:
         target = "you" if h["target"] == listener.id else None
         return {"ask": "asked who took the can", "deny": "denied taking it",
                 "accuse": f"accused {target or 'someone'}", "confess": "admitted taking it",
+                "confront": f"confronted {target or 'someone'}",
                 "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone",
                 "propose": "said someone should go to the neighbour's house tonight",
                 "volunteer": "offered to go there tonight",
@@ -1334,6 +1341,8 @@ class Morning:
             gist = f"{p.name} denies taking it, to everyone"
         elif kind == "accuse":
             gist = f"{p.name} accuses {aimed} of taking it"
+        elif kind == "confront":
+            gist = f"{p.name} confronts {aimed}"
         elif kind == "confess":
             gist = f"{p.name} admits taking it, to everyone"
         elif kind == "reassure":
@@ -1490,6 +1499,7 @@ class Morning:
             voices.append((room, new, {p.id} | {q.id for q in seen}))
             mine = {"ask": "asked who took it", "deny": "denied taking it",
                     "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
+                    "confront": f"confronted {target.name if target else ''}",
                     "reassure": f"reassured {target.name if aimed else 'everyone'}",
                     "propose": "said someone should go to the neighbour's house tonight",
                     "volunteer": "offered to go there tonight",
```

## 6. Scratch scripts

`$S/impl/replay_day1.py` is reproduced in body_impl.md §7. `$S/confront/v1_replay.py`:

```python
"""Read-only: replays v1's three runs (runs/daniel_ate_it-seedN.md, cache/…seedN.json) with v1's own code in
replay mode. Its replay.md is written into a scratch copy of the run folder, never into the repo."""
import io, contextlib, os, shutil, sys, tempfile
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "v1"))
from morning import run                                       # v1's own
tmp = tempfile.mkdtemp(prefix="v1-replay-")
for seed in (1, 2, 3):
    shutil.copy(os.path.join(ROOT, "runs", f"daniel_ate_it-seed{seed}.md"), tmp)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = run(seed, replay=True, config_path=os.path.join(ROOT, "config.json"), runs_dir=tmp,
                     cache_dir=os.path.join(ROOT, "cache"))
    meta, code = result if isinstance(result, tuple) else (result, None)
    out = buf.getvalue()
    line = next((x.strip() for x in out.split("\n") if "byte for byte" in x), out.strip().split("\n")[-1])
    print(f"v1 seed {seed}: exit {code}; api_requests {meta.get('api_requests') if isinstance(meta, dict) else '?'}; {line}")
shutil.rmtree(tmp)
```

## 7. Commands, in order

From `Prototypes/llm-morning/`, all with `GEMINI_API_KEY` unset:
1. `git status --short`, `git rev-parse --short HEAD` (`73430ce`): clean apart from the three replay files.
2. `mkdir v13 && cp data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py night.py story.py talk.py world.py v13/`; `v13/check.py` made from `v12/check.py` by `sed` (paths and wording); `python v13/check.py`: IDENTICAL ×3.
3. `morning.py` default `--out v14`, `.gitignore` for v14's fake runs; commit `7b899e5`.
4. `FoodConfrontTest` written; `python -m unittest -v test_morning.FoodConfrontTest`: 3 fail, 1 ok (§3).
5. The change in `talk.py` and `world.py`; `FoodConfrontTest`: 4 ok.
6. The full suite: 4 failures (B-T6, B-T8, B-T9: the old line; B-T10: the day-2 pairing). The tests were updated as §2 says. A first attempt to edit them by script stopped on its own check, wrote nothing, and was redone. The full suite: 163, OK.
7. The replays (§4); the `Newness` docstring rewrapped; `FoodConfrontTest` and `SequentialTalkTest`: 14, OK; commit `90133b4`; the full suite again on the commit: 163, OK (§3).
