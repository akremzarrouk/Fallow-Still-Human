# Knowledge wins fix: what a person knows about the can beats what they guessed

Prototypes/llm-morning, 2026-09-27. MODE: implement. The Gemini API was not called and no real morning was run. Every command below ran with `GEMINI_API_KEY` removed from the environment. Nothing in v1/ to v5/ was edited. Paths are relative to `Prototypes/llm-morning/` unless they start with the repo root.

## What changed

| | before | after |
|---|---|---|
| Culprit whose answers named someone else | `About the can (some): you thought Leo took it, at minutes 69 and 72.` (prompt_truth_fix.md, "Found, not changed", seed 1) | `About the can: you ate it yourself.` |
| Someone who heard the confession, whose later answers named someone else | `About the can (a little): you thought Elena took it, at minute 78.` (same section, seed 11) | `About the can: Mara admitted taking it at minute 06.` |
| No knowledge, some suspicion | "you thought X took it" line | unchanged |
| No knowledge, no suspicion | "you have not settled on who took it." | unchanged |

- **The change.** In `Morning.inside_lines`, the two knowledge branches now come before the suspicion branch (world.py:431-442).
- **Not changed.** How suspicion is stored and updated (`Suspicion.report`, world.py:117; `ask_model`, world.py:755-762) is untouched. Suspicion still rises and falls from the person's answers. It is no longer shown while `knows_culprit` is set. The wording of every line is the same as before.
- **New tests.** They are in `PromptTruthTest` and use the scripted fake model (`Scripted`, test_morning.py:285):
  - `test_the_culprit_who_names_someone_else_is_still_told_they_ate_it` (test_morning.py:865). Covers daniel_ate_it and mara_ate_it. The culprit's answers name Leo for 20 turns. The test checks that their suspicion reaches Leo 3/3, and that the prompt at minute 60 has the "you ate it yourself" line and no "you thought".
  - `test_after_hearing_a_confession_a_guess_does_not_replace_it` (test_morning.py:877). Covers mara_ate_it. Mara confesses at minute 09. Afterwards Daniel's answers name Elena, Elena's name Leo and Leo's name Daniel, for minutes 12 to 57. The test checks that each suspicion reaches 3/3, and that each prompt at minute 60 has "Mara admitted taking it at minute 09." and no "you thought".

## Commits

```
$ git log --oneline -4
ca89e9b Add the housekeeping report for da649da
2a41179 LLM morning: what a person knows about the can wins over what they guessed
a609ec7 LLM morning: tell a person what they know about the can; opening says what was seen
da649da Back up untracked work; add standing rules to CLAUDE.md
```

- **a609ec7: step 1.** It holds exactly the step 1 working tree from prompt_truth_fix.md: .gitignore, data.py, morning.py, the step 1 parts of world.py and test_morning.py, v5/ (10 frozen modules plus check.py) and reports/prompt_truth_fix.md.
  - world.py and test_morning.py held both steps in the working tree. For this commit, their step 1 versions were staged with `git hash-object -w` and `git update-index --cacheinfo`. The step 1 version of world.py is the file with this fix's branch order reversed. The step 1 version of test_morning.py is the file without the two new tests.
  - Staged diff: world.py +8, test_morning.py +53. These match the step 1 report's diff.
  - The staged tree was checked out to a temporary folder and its suite was run there: `Ran 52 tests ... OK`.
- **2a41179: this fix.** world.py and test_morning.py only.
- **ca89e9b: reports/housekeeping.md (repo root).** It was untracked before this work, and git status could not be clean without it. It is the report of da649da and was committed as it was, unedited.
- **This report** is committed after these. It cannot hold its own hash.

## Diff (2a41179)

```diff
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 8a61742..0d32b03 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -862,6 +862,36 @@ class PromptTruthTest(unittest.TestCase):
         prompt = m.prompt_for(mara, 20, m.options_for(mara))
         self.assertIn("About the can: you ate it yourself.", prompt)
 
+    def test_the_culprit_who_names_someone_else_is_still_told_they_ate_it(self):
+        for scenario, culprit in (("daniel_ate_it", "daniel"), ("mara_ate_it", "mara")):
+            # Their answers name Leo, which gives them a suspicion of Leo.
+            m = self.morning(scenario, lambda who, minute, options, c: ("silent", None, "Leo", "nobody"))
+            p = m.people[culprit]
+            for t in range(20):                # minutes 00 to 57
+                m.ask_model(p, t, m.options_for(p), {})
+            self.assertEqual((p.suspicion.target, p.suspicion.strength), ("leo", 3))
+            prompt = m.prompt_for(p, 20, m.options_for(p))
+            self.assertIn("About the can: you ate it yourself.", prompt)
+            self.assertNotIn("you thought", prompt)
+
+    def test_after_hearing_a_confession_a_guess_does_not_replace_it(self):
+        # After Mara's confession their answers name someone other than Mara.
+        other = {"daniel": "Elena", "elena": "Leo", "leo": "Daniel"}
+        m = self.morning("mara_ate_it", lambda who, minute, options, c: ("silent", None, other[who], "nobody"))
+        mara = m.people["mara"]
+        in_turn(m)
+        opt = next(o for o in m.options_for(mara) if o.id == "confess")
+        m.apply(mara, opt, {"mode": "model", "say": "It was me.", "feeling": "ashamed"}, 3, [], new_record())
+        out_of_turn(m)
+        for pid in ("daniel", "elena", "leo"):
+            p = m.people[pid]
+            for t in range(4, 20):             # minutes 12 to 57
+                m.ask_model(p, t, m.options_for(p), {})
+            self.assertEqual(p.suspicion.strength, 3, pid)
+            prompt = m.prompt_for(p, 20, m.options_for(p))
+            self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
+            self.assertNotIn("you thought", prompt)
+
     def test_the_opening_says_what_was_seen_in_every_scenario(self):
         seen = ("Elena counts the pantry with everyone standing there. She finds one can fewer than "
                 "she expected and says so. 2 portions are left.")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 14407e3..69e9bac 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -428,15 +428,16 @@ class Morning:
         if "hunger" in self.risen(p):
             out.append("Since you last decided, you have grown hungrier.")
         s = p.suspicion
-        if s.strength:
-            out.append(f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
-                       f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
-                       f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
-        elif p.knows_culprit == p.id:
+        # What they know about the can wins over what their answers guessed.
+        if p.knows_culprit == p.id:
             out.append("About the can: you ate it yourself.")
         elif p.knows_culprit:
             out.append(f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
                        f"{p.confession_heard_at:02d}.")
+        elif s.strength:
+            out.append(f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
+                       f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
+                       f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
         else:
             out.append("About the can: you have not settled on who took it.")
         held = [(t, p.grudges[t]) for t in data.ORDER if t in p.grudges and p.grudges[t].strength]
```

## Tests before the change

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.PromptTruthTest
test_after_hearing_a_confession_a_guess_does_not_replace_it (test_morning.PromptTruthTest.test_after_hearing_a_confession_a_guess_does_not_replace_it) ... FAIL
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... ok
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... ok
test_the_culprit_who_names_someone_else_is_still_told_they_ate_it (test_morning.PromptTruthTest.test_the_culprit_who_names_someone_else_is_still_told_they_ate_it) ... FAIL
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... ok

======================================================================
FAIL: test_after_hearing_a_confession_a_guess_does_not_replace_it (test_morning.PromptTruthTest.test_after_hearing_a_confession_a_guess_does_not_replace_it)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 892, in test_after_hearing_a_confession_a_guess_does_not_replace_it
    self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
AssertionError: 'About the can: Mara admitted taking it at minute 09.' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can (a lot): you thought Elena took it, at minutes 48, 51, 54 and 57.\nAgainst the others: nothing.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)\n- min 09: Mara admitted taking the can: "It was me." (you heard it)\nWhat else happened this morning, most recent last:\n- min 09: Mara admits taking it, to everyone: "It was me."\nNow, minute 60, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, talking.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_mara: (speech) accuse Mara of taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here'

======================================================================
FAIL: test_the_culprit_who_names_someone_else_is_still_told_they_ate_it (test_morning.PromptTruthTest.test_the_culprit_who_names_someone_else_is_still_told_they_ate_it)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 874, in test_the_culprit_who_names_someone_else_is_still_told_they_ate_it
    self.assertIn("About the can: you ate it yourself.", prompt)
AssertionError: 'About the can: you ate it yourself.' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can (a lot): you thought Leo took it, at minutes 48, 51, 54 and 57.\nAgainst the others: nothing.\nOn your conscience (a little): you ate the can in the night, and nobody saw.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)\n- You know where the can went: you ate it yourself in the night, and nobody saw.\nWhat else happened this morning, most recent last:\n- (earlier things, left out here)\nNow, minute 60, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, standing at the pantry.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_elena: (speech) accuse Elena of taking it\n- accuse_leo: (speech) accuse Leo of taking it\n- accuse_mara: (speech) accuse Mara of taking it\n- confess: (speech) admit taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- search: search the kitchen for the can (takes about six minutes)\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here'

----------------------------------------------------------------------
Ran 5 tests in 0.211s

FAILED (failures=2)
exit 1
```

Both new tests fail on the "About the can" line. It shows "you thought Leo took it" for the culprit (Daniel), and "you thought Elena took it" for the first listener (Daniel). The three step 1 tests pass.

## Tests after the change

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.PromptTruthTest
test_after_hearing_a_confession_a_guess_does_not_replace_it (test_morning.PromptTruthTest.test_after_hearing_a_confession_a_guess_does_not_replace_it) ... ok
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... ok
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... ok
test_the_culprit_who_names_someone_else_is_still_told_they_ate_it (test_morning.PromptTruthTest.test_the_culprit_who_names_someone_else_is_still_told_they_ate_it) ... ok
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.366s

OK
exit 0
```

The full suite (test_morning.py is the prototype's only test file):

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning
...............    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
.    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
......................................
----------------------------------------------------------------------
Ran 54 tests in 13.071s

OK
exit 0
```

The `[429 RESOURCE_EXHAUSTED]` lines come from `GeminiClientTest` (test_morning.py:944-960). It raises scripted 429 errors through `StubApi` (test_morning.py:102), which stands in for the API client. No request left the machine.

## The freeze replays

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe v5/check.py; echo "exit $?"
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
exit 0
```

## The seed 1 to 20 scan

The step 1 report's `scan_seeds.py` is not in the repo or anywhere on disk. It was recreated outside the repo, at `<scratchpad>/scan_seeds.py`. It runs the fake model (`FakeClient`) on mara_ate_it for seeds 1 to 20, each with a fresh temporary cache. It stops before the last turn and prints each person's "About the can" line, which is the state their minute 87 prompt shows. It takes the code folder as its argument, and its last line counts people with `knows_culprit` set whose line says "you thought".

```python
"""The four "About the can" lines at minute 87, mara_ate_it, fake model, seeds 1-20.

    python scan_seeds.py CODE_DIR

A final CHECK line counts people with knows_culprit whose line says "you thought".
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(sys.argv[1]))

import data
from gemini import Cache, FakeClient, Oracle, StopMorning
from world import Morning

bad = 0
with tempfile.TemporaryDirectory() as tmp:
    for seed in range(1, 21):
        oracle = Oracle(Cache(os.path.join(tmp, f"fake-{seed}.json")), "fake", seed,
                        client=FakeClient(max_calls=150), max_calls=150)
        m = Morning(oracle, seed, "mara_ate_it")
        try:
            for t in range(m.turns - 1):            # up to the prompt of minute 87
                m.turn(t)
        except StopMorning as stop:
            print(seed, "stopped:", stop)
            continue
        cells = []
        for pid in data.ORDER:
            p = m.people[pid]
            line = next(l for l in m.inside_lines(p) if l.startswith("About the can"))
            cells.append(f"{p.name}: {line[len('About the can'):]}")
            if p.knows_culprit and "you thought" in line:
                bad += 1
        print(seed, " | ".join(cells))
print(f"CHECK knows_culprit with a 'you thought' line: {bad}")
```

**Checking the recreation.** The script was run on a copy of the step 1 code, the working tree with this fix's branch order reversed. Its 20 lines are the same as the scan in prompt_truth_fix.md. The only difference is line endings:

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe <scratchpad>/scan_seeds.py <scratchpad>/prefix
1 Daniel: : Mara admitted taking it at minute 66. | Elena:  (some): you thought Leo took it, at minutes 78 and 84. | Leo:  (a little): you thought Elena took it, at minute 78. | Mara:  (some): you thought Leo took it, at minutes 69 and 72.
2 Daniel:  (a little): you thought Elena took it, at minute 66. | Elena: : Mara admitted taking it at minute 12. | Leo:  (a lot): you thought Mara took it, at minutes 06, 15, 24 and 69. | Mara:  (a little): you thought Elena took it, at minutes 36 and 42.
3 Daniel: : you have not settled on who took it. | Elena: : you have not settled on who took it. | Leo:  (a little): you thought Daniel took it, at minutes 00, 03, 12 and 78. | Mara:  (a little): you thought Daniel took it, at minute 72.
4 Daniel:  (a little): you thought Leo took it, at minute 75. | Elena: : you have not settled on who took it. | Leo:  (a little): you thought Mara took it, at minutes 03, 15, 21 and 36. | Mara: : you ate it yourself.
5 Daniel:  (a little): you thought Elena took it, at minute 69. | Elena:  (a lot): you thought Leo took it, at minutes 60, 66 and 78. | Leo:  (some): you thought Mara took it, at minutes 66 and 72. | Mara:  (a little): you thought Leo took it, at minutes 09, 30, 36 and 51.
6 Daniel:  (a little): you thought Leo took it, at minutes 12 and 15. | Elena:  (a little): you thought Leo took it, at minute 75. | Leo: : you have not settled on who took it. | Mara: : you ate it yourself.
7 Daniel: : you have not settled on who took it. | Elena:  (a little): you thought Mara took it, at minutes 06, 12 and 30. | Leo: : you have not settled on who took it. | Mara: : you ate it yourself.
8 Daniel: : you have not settled on who took it. | Elena:  (a little): you thought Mara took it, at minutes 00, 03 and 42. | Leo:  (a little): you thought Elena took it, at minute 63. | Mara:  (a little): you thought Leo took it, at minute 54.
9 Daniel:  (a little): you thought Elena took it, at minute 48. | Elena:  (a little): you thought Leo took it, at minute 75. | Leo:  (a little): you thought Mara took it, at minute 81. | Mara:  (a little): you thought Daniel took it, at minute 72.
10 Daniel: : Mara admitted taking it at minute 06. | Elena:  (a little): you thought Leo took it, at minute 84. | Leo: : Mara admitted taking it at minute 06. | Mara:  (a little): you thought Daniel took it, at minute 84.
11 Daniel:  (a little): you thought Elena took it, at minute 78. | Elena:  (a little): you thought Daniel took it, at minute 84. | Leo: : Mara admitted taking it at minute 06. | Mara: : you ate it yourself.
12 Daniel:  (a little): you thought Elena took it, at minute 78. | Elena: : you have not settled on who took it. | Leo:  (some): you thought Elena took it, at minutes 00, 03, 12 and 63. | Mara:  (some): you thought Leo took it, at minutes 06 and 54.
13 Daniel:  (a little): you thought Mara took it, at minute 66. | Elena:  (a little): you thought Daniel took it, at minutes 00, 03 and 18. | Leo:  (some): you thought Elena took it, at minutes 51 and 60. | Mara:  (a little): you thought Daniel took it, at minutes 36 and 48.
14 Daniel:  (a little): you thought Leo took it, at minutes 45, 48 and 57. | Elena:  (a little): you thought Leo took it, at minute 81. | Leo:  (a little): you thought Elena took it, at minute 84. | Mara:  (a little): you thought Daniel took it, at minutes 54 and 63.
15 Daniel:  (some): you thought Mara took it, at minutes 69 and 72. | Elena:  (a little): you thought Leo took it, at minute 72. | Leo:  (a little): you thought Mara took it, at minute 81. | Mara:  (a little): you thought Elena took it, at minute 84.
16 Daniel: : Mara admitted taking it at minute 12. | Elena:  (some): you thought Leo took it, at minutes 09, 12 and 15. | Leo:  (some): you thought Elena took it, at minutes 81 and 84. | Mara:  (a little): you thought Leo took it, at minutes 03, 12 and 15.
17 Daniel: : you have not settled on who took it. | Elena: : you have not settled on who took it. | Leo:  (a little): you thought Elena took it, at minutes 00, 03, 12 and 57. | Mara: : you ate it yourself.
18 Daniel: : Mara admitted taking it at minute 51. | Elena: : you have not settled on who took it. | Leo:  (a little): you thought Mara took it, at minutes 33, 48 and 60. | Mara:  (some): you thought Elena took it, at minutes 48 and 51.
19 Daniel:  (a little): you thought Mara took it, at minute 84. | Elena:  (a little): you thought Mara took it, at minute 84. | Leo:  (a little): you thought Elena took it, at minute 78. | Mara:  (a little): you thought Daniel took it, at minute 84.
20 Daniel:  (a little): you thought Elena took it, at minute 48. | Elena:  (a little): you thought Leo took it, at minute 75. | Leo:  (a little): you thought Mara took it, at minute 81. | Mara:  (a little): you thought Daniel took it, at minute 72.
CHECK knows_culprit with a 'you thought' line: 29
exit 0
$ head -20 scan_before.txt | diff --strip-trailing-cr - scan_step1.txt && echo SAME_AS_STEP1_REPORT
SAME_AS_STEP1_REPORT
```

**After the fix:**

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe <scratchpad>/scan_seeds.py .
1 Daniel:  (a little): you thought Leo took it, at minute 66. | Elena: : Mara admitted taking it at minute 54. | Leo: : Mara admitted taking it at minute 54. | Mara: : you ate it yourself.
2 Daniel: : you have not settled on who took it. | Elena:  (a little): you thought Leo took it, at minute 60. | Leo:  (a little): you thought Mara took it, at minute 63. | Mara: : you ate it yourself.
3 Daniel:  (a little): you thought Leo took it, at minutes 60 and 75. | Elena: : Mara admitted taking it at minute 66. | Leo: : Mara admitted taking it at minute 66. | Mara: : you ate it yourself.
4 Daniel:  (a little): you thought Leo took it, at minute 84. | Elena: : you have not settled on who took it. | Leo:  (a little): you thought Elena took it, at minute 27. | Mara: : you ate it yourself.
5 Daniel:  (a little): you thought Leo took it, at minute 84. | Elena: : Mara admitted taking it at minute 15. | Leo:  (a little): you thought Daniel took it, at minute 63. | Mara: : you ate it yourself.
6 Daniel:  (a lot): you thought Leo took it, at minutes 12, 15, 39 and 78. | Elena: : you have not settled on who took it. | Leo:  (some): you thought Daniel took it, at minutes 45, 51 and 75. | Mara: : you ate it yourself.
7 Daniel:  (a little): you thought Leo took it, at minute 81. | Elena:  (a lot): you thought Mara took it, at minutes 27, 39, 54 and 69. | Leo:  (some): you thought Elena took it, at minutes 30, 63 and 81. | Mara: : you ate it yourself.
8 Daniel:  (some): you thought Elena took it, at minutes 06, 09 and 33. | Elena:  (some): you thought Leo took it, at minutes 03, 12, 18 and 69. | Leo:  (a little): you thought Daniel took it, at minutes 03, 15 and 75. | Mara: : you ate it yourself.
9 Daniel:  (a little): you thought Mara took it, at minute 69. | Elena:  (some): you thought Leo took it, at minutes 57 and 63. | Leo:  (some): you thought Mara took it, at minutes 45 and 51. | Mara: : you ate it yourself.
10 Daniel:  (a lot): you thought Mara took it, at minutes 33, 42, 60 and 81. | Elena:  (a little): you thought Leo took it, at minute 81. | Leo:  (a little): you thought Mara took it, at minutes 57 and 66. | Mara: : you ate it yourself.
11 Daniel:  (a little): you thought Elena took it, at minute 78. | Elena:  (some): you thought Mara took it, at minutes 66, 72 and 78. | Leo:  (a little): you thought Mara took it, at minute 81. | Mara: : you ate it yourself.
12 Daniel:  (some): you thought Mara took it, at minutes 06, 33, 78 and 84. | Elena:  (a little): you thought Leo took it, at minute 75. | Leo:  (a little): you thought Mara took it, at minutes 21 and 78. | Mara: : you ate it yourself.
13 Daniel: : Mara admitted taking it at minute 06. | Elena: : Mara admitted taking it at minute 06. | Leo: : Mara admitted taking it at minute 06. | Mara: : you ate it yourself.
14 Daniel:  (some): you thought Leo took it, at minutes 45 and 48. | Elena:  (some): you thought Daniel took it, at minutes 75 and 84. | Leo: : you have not settled on who took it. | Mara: : you ate it yourself.
15 Daniel: : Mara admitted taking it at minute 12. | Elena:  (some): you thought Leo took it, at minutes 30, 39, 75 and 81. | Leo: : Mara admitted taking it at minute 12. | Mara: : you ate it yourself.
16 Daniel:  (a little): you thought Leo took it, at minutes 12, 15 and 66. | Elena: : Mara admitted taking it at minute 18. | Leo:  (a little): you thought Elena took it, at minutes 39, 51 and 72. | Mara: : you ate it yourself.
17 Daniel: : Mara admitted taking it at minute 39. | Elena: : Mara admitted taking it at minute 39. | Leo: : Mara admitted taking it at minute 39. | Mara: : you ate it yourself.
18 Daniel: : Mara admitted taking it at minute 24. | Elena: : you have not settled on who took it. | Leo: : Mara admitted taking it at minute 24. | Mara: : you ate it yourself.
19 Daniel:  (a little): you thought Leo took it, at minutes 00, 06, 21 and 63. | Elena: : Mara admitted taking it at minute 60. | Leo: : you have not settled on who took it. | Mara: : you ate it yourself.
20 Daniel:  (some): you thought Mara took it, at minutes 69 and 75. | Elena:  (some): you thought Mara took it, at minutes 24, 27 and 36. | Leo:  (a little): you thought Mara took it, at minute 72. | Mara: : you ate it yourself.
CHECK knows_culprit with a 'you thought' line: 0
exit 0
```

- **Result.** Before the fix, 29 people with `knows_culprit` set had a "you thought" line. After the fix, 0 did.
- **These are different mornings.** The fake model picks its answer by a hash of the whole prompt (gemini.py:159-160). Once a person's "About the can" line changes, their answers change, and so does the rest of the morning. A seed's row after the fix is therefore not the same morning as that seed's row before it.

## Not run

`merge-slice-docs.py` was not run, for the same reason as in step 1: this work produced one document, and the only folder the script could merge, `reports/`, holds unrelated audits.

## git status

Before this report was written, after ca89e9b:

```
$ git status --short; echo "exit $?"
exit 0
```

The output is empty. The only change after that is this report, which is committed next.
