# Prompt truth fix: what the person knows about the can, and what the opening says

Prototypes/llm-morning, 2026-09-27. MODE: implement. The Gemini API was not called, no morning was run and nothing in v1/ to v4/ was edited. Every morning below used the fake model or a cache-only replay, and each ran with `GEMINI_API_KEY` removed from the environment. Paths are relative to `Prototypes/llm-morning/`.

## What changed

| # | before | after |
|---|---|---|
| 1 | A person who knows who took the can got "About the can: you have not settled on who took it." (knowledge_audit.md §6, §8 i). | The culprit gets "About the can: you ate it yourself." Someone who heard the confession gets "About the can: Mara admitted taking it at minute 09." (world.py:435-439). |
| 2 | The opening said "A can that should be on the shelf is not." in every scenario, miscount included (knowledge_audit.md §4, §8 f). | The opening now reads "Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left." (data.py:167-170). |

- **Change 1.** The new lines replace only the "not settled" branch. If the person's own answers have given them a suspicion (strength 1 to 3), the existing "About the can (…): you thought X took it…" line still shows, as before. See "Found, not changed" below.
- **The confession minute.** It comes from a new field, `Person.confession_heard_at` (world.py:213). It is set the first time the person hears the culprit admit it (world.py:913-914).
- **Change 2.** The sure line keeps its form, `min 00: {OPENING} (you did it / saw it)` (world.py:265). The opening is true in all three scenarios. In daniel_ate_it and mara_ate_it a can was eaten. In miscount there were only ever two (data.py:113), so Elena's count still comes out one below what she expected.
- **The story also changes.** story.py:235 prints `data.OPENING` in the backstory table, so the story of any new run carries the new wording.
- **Old cached answers no longer match.** Every prompt holds the opening, so no prompt built by the new code matches a cached v5 prompt. Every prompt in a new real run would be a live call.

The freeze, as v4/ was frozen:
- `v5/` holds a copy of `data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py story.py talk.py world.py`, taken before any edit. That is the module set of v4/ plus metrics5.py.
- `v5/check.py` replays the 11 runs in runs/v5/.
- The live code's default output moved from v5 to v6 (morning.py:11-12, 35, 41, 138). As a result, a new run can no longer overwrite runs/v5/*.md or add answers to cache/v5.
- .gitignore got the matching `runs/v6/fake/` and `cache/v6/fake-*` lines.

## Diff

`v5/` is new: 10 files copied byte for byte, plus `v5/check.py` (56 lines). The diff of the tracked files:

```diff
diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index d6f71dc..61658fb 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -11,3 +11,5 @@ runs/v4/fake/
 cache/v4/fake-*
 runs/v5/fake/
 cache/v5/fake-*
+runs/v6/fake/
+cache/v6/fake-*
diff --git a/Prototypes/llm-morning/data.py b/Prototypes/llm-morning/data.py
index 61b8f0f..08dffd0 100644
--- a/Prototypes/llm-morning/data.py
+++ b/Prototypes/llm-morning/data.py
@@ -164,4 +164,7 @@ def culprit(scenario):
     """Who took the can in this scenario, or None."""
     return SCENARIOS[scenario]["culprit"]
 
-OPENING = "Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left."
+# What everyone saw at the start: Elena's count and what she said about it. It is true in every
+# scenario, miscount included, where nothing was taken.
+OPENING = ("Elena counts the pantry with everyone standing there. She finds one can fewer than she "
+           "expected and says so. 2 portions are left.")
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index a1c7cf1..94f2a38 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -8,8 +8,8 @@
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v5; v4 replays
-                      the fourth version's runs)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v6; v4 replays
+                      the fourth version's runs; v5/check.py replays the fifth's)
 
 The model names and call limits are in config.json. The key is read from GEMINI_API_KEY.
 
@@ -32,13 +32,13 @@ HERE = os.path.dirname(os.path.abspath(__file__))
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v5"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v6"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v4/ can still replay.
+    # cache/vN after), which v1/ to v5/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -135,7 +135,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v5")
+    ap.add_argument("--out", default="v6")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index cdd72b6..8a61742 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -821,6 +821,59 @@ class ScenarioTest(unittest.TestCase):
         self.assertEqual((config["model"], config["min_seconds_between_calls"]), ("gemma-4-31b-it", 6.5))
 
 
+class PromptTruthTest(unittest.TestCase):
+    """Every line of a prompt is true for the person reading it."""
+
+    def setUp(self):
+        self.dirs = Dirs()
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def morning(self, scenario, policy=None):
+        client = Scripted(policy or (lambda who, minute, options, c: ("silent", None)))
+        return Morning(Oracle(Cache(os.path.join(self.dirs.root, f"{scenario}.json")), "fake", 1,
+                              client=client), 1, scenario)
+
+    def test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled(self):
+        for scenario, culprit in (("daniel_ate_it", "daniel"), ("mara_ate_it", "mara")):
+            name = data.PEOPLE[culprit]["name"]
+            # They name themselves as the one who took it, which counts as nobody.
+            m = self.morning(scenario, lambda who, minute, options, c: ("silent", None, name, "nobody"))
+            p = m.people[culprit]
+            for t in range(20):                # minutes 00 to 57
+                m.ask_model(p, t, m.options_for(p), {})
+            prompt = m.prompt_for(p, 20, m.options_for(p))
+            self.assertIn("About the can: you ate it yourself.", prompt)
+            self.assertNotIn("you have not settled on who took it", prompt)
+
+    def test_hearing_a_confession_is_what_they_know_about_the_can(self):
+        m = self.morning("mara_ate_it")
+        mara = m.people["mara"]
+        in_turn(m)
+        opt = next(o for o in m.options_for(mara) if o.id == "confess")
+        m.apply(mara, opt, {"mode": "model", "say": "It was me.", "feeling": "ashamed"}, 3, [], new_record())
+        out_of_turn(m)
+        for pid in ("daniel", "elena", "leo"):
+            p = m.people[pid]
+            prompt = m.prompt_for(p, 20, m.options_for(p))
+            self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
+            self.assertNotIn("you have not settled on who took it", prompt)
+        prompt = m.prompt_for(mara, 20, m.options_for(mara))
+        self.assertIn("About the can: you ate it yourself.", prompt)
+
+    def test_the_opening_says_what_was_seen_in_every_scenario(self):
+        seen = ("Elena counts the pantry with everyone standing there. She finds one can fewer than "
+                "she expected and says so. 2 portions are left.")
+        for scenario in data.SCENARIOS:
+            m = self.morning(scenario)
+            for pid, p in m.people.items():
+                prompt = m.prompt_for(p, 0, m.options_for(p))
+                how = "did it" if pid == "elena" else "saw it"
+                self.assertIn(f"- min 00: {seen} (you {how})", prompt, (scenario, pid))
+                self.assertNotIn("A can that should be on the shelf is not", prompt, (scenario, pid))
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 9f9244f..14407e3 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -210,6 +210,7 @@ class Person:
         self.aside_lead = None      # whom they took aside last turn, if the other came
         self.searched = set()
         self.knows_culprit = culprit if pid == culprit else None
+        self.confession_heard_at = None     # minute they first heard the culprit admit it
         self.heard_question = False
         self.confessed = False
         self.eaten = 0.0
@@ -431,6 +432,11 @@ class Morning:
             out.append(f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
                        f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
                        f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
+        elif p.knows_culprit == p.id:
+            out.append("About the can: you ate it yourself.")
+        elif p.knows_culprit:
+            out.append(f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
+                       f"{p.confession_heard_at:02d}.")
         else:
             out.append("About the can: you have not settled on who took it.")
         held = [(t, p.grudges[t]) for t in data.ORDER if t in p.grudges and p.grudges[t].strength]
@@ -904,6 +910,8 @@ class Morning:
                 if kind in ("ask", "accuse"):
                     q.heard_question = True
                 if kind == "confess":
+                    if q.knows_culprit is None:
+                        q.confession_heard_at = minute
                     q.knows_culprit = p.id
                     q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
                                   "(you heard it)")
```

The copy, checked against the originals before any edit:

```
$ mkdir v5 && cp data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py story.py talk.py world.py v5/
$ for f in v5/*.py; do cmp $f $(basename $f) && echo "same $(basename $f)"; done
same data.py
same gemini.py
same metrics.py
same metrics3.py
same metrics4.py
same metrics5.py
same morning.py
same story.py
same talk.py
same world.py
```

## The freeze replays

This was run once before the fix and once after it. The output was the same both times:

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

## Tests before the change

The three new tests are in `PromptTruthTest` (test_morning.py:824-874):
- `test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled`
  - Both culprit scenarios.
  - The culprit names themselves as suspect for 20 turns, which counts as nobody.
  - Their prompt is then checked at minute 60.
- `test_hearing_a_confession_is_what_they_know_about_the_can`
  - mara_ate_it. Mara confesses at minute 09.
  - The other three prompts are checked at minute 60, and so is Mara's.
- `test_the_opening_says_what_was_seen_in_every_scenario`
  - All three scenarios, all four people, at minute 00.

They use the scripted fake model (`Scripted`, test_morning.py:285), so no API is involved.

```
$ .venv/Scripts/python.exe -m unittest -v test_morning.PromptTruthTest; echo "exit $?"
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... FAIL
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... FAIL
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... FAIL

======================================================================
FAIL: test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 860, in test_hearing_a_confession_is_what_they_know_about_the_can
    self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
AssertionError: 'About the can: Mara admitted taking it at minute 09.' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can: you have not settled on who took it.\nAgainst the others: nothing.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)\n- min 09: Mara admitted taking the can: "It was me." (you heard it)\nWhat else happened this morning, most recent last:\n- min 09: Mara admits taking it, to everyone: "It was me."\nNow, minute 60, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, talking.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_mara: (speech) accuse Mara of taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here'

======================================================================
FAIL: test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 847, in test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled
    self.assertIn("About the can: you ate it yourself.", prompt)
AssertionError: 'About the can: you ate it yourself.' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can: you have not settled on who took it.\nAgainst the others: nothing.\nOn your conscience (a little): you ate the can in the night, and nobody saw.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)\n- You know where the can went: you ate it yourself in the night, and nobody saw.\nWhat else happened this morning, most recent last:\n- nothing else yet\nNow, minute 60, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, standing at the pantry.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_elena: (speech) accuse Elena of taking it\n- accuse_leo: (speech) accuse Leo of taking it\n- accuse_mara: (speech) accuse Mara of taking it\n- confess: (speech) admit taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- search: search the kitchen for the can (takes about six minutes)\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here'

======================================================================
FAIL: test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 873, in test_the_opening_says_what_was_seen_in_every_scenario
    self.assertIn(f"- min 00: {seen} (you {how})", prompt, (scenario, pid))
AssertionError: '- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can: you have not settled on who took it.\nAgainst the others: nothing.\nOn your conscience (a little): you ate the can in the night, and nobody saw.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)\n- You know where the can went: you ate it yourself in the night, and nobody saw.\nWhat else happened this morning, most recent last:\n- nothing else yet\nNow, minute 00, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, standing at the pantry.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_elena: (speech) accuse Elena of taking it\n- accuse_leo: (speech) accuse Leo of taking it\n- accuse_mara: (speech) accuse Mara of taking it\n- confess: (speech) admit taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- search: search the kitchen for the can (takes about six minutes)\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here' : ('daniel_ate_it', 'daniel')

----------------------------------------------------------------------
Ran 3 tests in 0.065s

FAILED (failures=3)
exit 1
```

The full suite before the change. Only the three new tests fail, and their failure text is the same as above:

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning; echo "exit $?"
test_a_morning_completes_and_writes_a_story (test_morning.FakeMorningTest.test_a_morning_completes_and_writes_a_story) ... ok
test_an_admission_cannot_be_taken_back (test_morning.FakeMorningTest.test_an_admission_cannot_be_taken_back) ... ok
test_at_most_one_call_per_person_per_turn (test_morning.FakeMorningTest.test_at_most_one_call_per_person_per_turn) ... ok
test_every_kind_of_broken_answer_falls_back_to_the_rules (test_morning.FakeMorningTest.test_every_kind_of_broken_answer_falls_back_to_the_rules) ... ok
test_nothing_from_target_morning_reaches_a_prompt (test_morning.FakeMorningTest.test_nothing_from_target_morning_reaches_a_prompt) ... ok
test_only_daniel_knows_and_only_daniel_may_confess (test_morning.FakeMorningTest.test_only_daniel_knows_and_only_daniel_may_confess) ... ok
test_prompts_are_short (test_morning.FakeMorningTest.test_prompts_are_short) ... ok
test_replay_is_byte_for_byte_with_no_client_reached (test_morning.FakeMorningTest.test_replay_is_byte_for_byte_with_no_client_reached) ... ok
test_replay_without_a_cache_stops_cleanly (test_morning.FakeMorningTest.test_replay_without_a_cache_stops_cleanly) ... ok
test_seeds_do_not_share_answers (test_morning.FakeMorningTest.test_seeds_do_not_share_answers) ... ok
test_the_call_cap_counts_answers_from_an_earlier_run (test_morning.FakeMorningTest.test_the_call_cap_counts_answers_from_an_earlier_run) ... ok
test_the_call_cap_stops_the_morning_cleanly (test_morning.FakeMorningTest.test_the_call_cap_stops_the_morning_cleanly) ... ok
test_calls_are_spaced (test_morning.GeminiClientTest.test_calls_are_spaced) ... ok
test_daily_quota_stops_keeps_the_cache_and_resumes (test_morning.GeminiClientTest.test_daily_quota_stops_keeps_the_cache_and_resumes) ... ok
test_missing_key_stops_with_a_clear_message (test_morning.GeminiClientTest.test_missing_key_stops_with_a_clear_message) ... ok
test_per_minute_429_backs_off_and_retries (test_morning.GeminiClientTest.test_per_minute_429_backs_off_and_retries) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
ok
test_repeated_429_gives_up_cleanly (test_morning.GeminiClientTest.test_repeated_429_gives_up_cleanly) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
ok
test_the_key_is_never_printed_or_saved (test_morning.GeminiClientTest.test_the_key_is_never_printed_or_saved) ... ok
test_a_false_accusation_raises_a_grudge_toward_the_accuser (test_morning.PressureTest.test_a_false_accusation_raises_a_grudge_toward_the_accuser) ... ok
test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed (test_morning.PressureTest.test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed) ... ok
test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes (test_morning.PressureTest.test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes) ... ok
test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster (test_morning.PressureTest.test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster) ... ok
test_confessing_after_denying_it_and_after_accusing (test_morning.PressureTest.test_confessing_after_denying_it_and_after_accusing) ... ok
test_daniel_accusing_someone_counts_once (test_morning.PressureTest.test_daniel_accusing_someone_counts_once) ... ok
test_daniels_guilt_rises_by_the_rules (test_morning.PressureTest.test_daniels_guilt_rises_by_the_rules) ... ok
test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not (test_morning.PressureTest.test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not) ... ok
test_inner_moments_come_at_most_once_every_9_minutes (test_morning.PressureTest.test_inner_moments_come_at_most_once_every_9_minutes) ... ok
test_naming_yourself_counts_as_nobody (test_morning.PressureTest.test_naming_yourself_counts_as_nobody) ... ok
test_no_prompt_holds_the_old_verdicts (test_morning.PressureTest.test_no_prompt_holds_the_old_verdicts) ... ok
test_reassure_is_not_offered_toward_a_grudge_of_3 (test_morning.PressureTest.test_reassure_is_not_offered_toward_a_grudge_of_3) ... ok
test_take_aside_accepted (test_morning.PressureTest.test_take_aside_accepted) ... ok
test_take_aside_needs_someone_yet_to_act_and_an_empty_room (test_morning.PressureTest.test_take_aside_needs_someone_yet_to_act_and_an_empty_room) ... ok
test_take_aside_refused (test_morning.PressureTest.test_take_aside_refused) ... ok
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... FAIL
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... FAIL
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... FAIL
test_a_second_model_from_the_config (test_morning.ScenarioTest.test_a_second_model_from_the_config) ... ok
test_each_scenario_runs_with_the_fake_model (test_morning.ScenarioTest.test_each_scenario_runs_with_the_fake_model) ... ok
test_in_miscount_every_accusation_is_false (test_morning.ScenarioTest.test_in_miscount_every_accusation_is_false) ... ok
test_mara_as_the_culprit_carries_the_guilt (test_morning.ScenarioTest.test_mara_as_the_culprit_carries_the_guilt) ... ok
test_the_culprit_comes_from_the_scenario (test_morning.ScenarioTest.test_the_culprit_comes_from_the_scenario) ... ok
test_the_story_speaks_of_the_culprit (test_morning.ScenarioTest.test_the_story_speaks_of_the_culprit) ... ok
test_a_conversation_ends_after_two_full_turns_with_nothing_new (test_morning.SequentialTalkTest.test_a_conversation_ends_after_two_full_turns_with_nothing_new) ... ok
test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again (test_morning.SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again) ... ok
test_an_inner_moment_can_start_the_talk_again (test_morning.SequentialTalkTest.test_an_inner_moment_can_start_the_talk_again) ... ok
test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn (test_morning.SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn) ... ok
test_metrics_work_out_the_same_conversations_as_the_morning (test_morning.SequentialTalkTest.test_metrics_work_out_the_same_conversations_as_the_morning) ... ok
test_no_speech_act_runs_past_three_turns_in_any_fake_morning (test_morning.SequentialTalkTest.test_no_speech_act_runs_past_three_turns_in_any_fake_morning) ... ok
test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to (test_morning.SequentialTalkTest.test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to) ... ok
test_the_one_just_accused_acts_next (test_morning.SequentialTalkTest.test_the_one_just_accused_acts_next) ... ok
test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house (test_morning.SequentialTalkTest.test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house) ... ok
test_ties_are_broken_by_the_seed (test_morning.SequentialTalkTest.test_ties_are_broken_by_the_seed) ... ok

======================================================================
FAIL: test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 860, in test_hearing_a_confession_is_what_they_know_about_the_can
    self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
AssertionError: 'About the can: Mara admitted taking it at minute 09.' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can: you have not settled on who took it.\nAgainst the others: nothing.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)\n- min 09: Mara admitted taking the can: "It was me." (you heard it)\nWhat else happened this morning, most recent last:\n- min 09: Mara admits taking it, to everyone: "It was me."\nNow, minute 60, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, talking.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_mara: (speech) accuse Mara of taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here'

======================================================================
FAIL: test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 847, in test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled
    self.assertIn("About the can: you ate it yourself.", prompt)
AssertionError: 'About the can: you ate it yourself.' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can: you have not settled on who took it.\nAgainst the others: nothing.\nOn your conscience (a little): you ate the can in the night, and nobody saw.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)\n- You know where the can went: you ate it yourself in the night, and nobody saw.\nWhat else happened this morning, most recent last:\n- nothing else yet\nNow, minute 60, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, standing at the pantry.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_elena: (speech) accuse Elena of taking it\n- accuse_leo: (speech) accuse Leo of taking it\n- accuse_mara: (speech) accuse Mara of taking it\n- confess: (speech) admit taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- search: search the kitchen for the can (takes about six minutes)\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here'

======================================================================
FAIL: test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 873, in test_the_opening_says_what_was_seen_in_every_scenario
    self.assertIn(f"- min 00: {seen} (you {how})", prompt, (scenario, pid))
AssertionError: '- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)' not found in 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".\nWho you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.\nTemperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.\nWhat matters to you: being in control, being respected, keeping the family safe.\nYour body: hungry.\nAbout the can: you have not settled on who took it.\nAgainst the others: nothing.\nOn your conscience (a little): you ate the can in the night, and nobody saw.\nThe house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo\'s room); back room (Elena and Mara\'s room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel\'s and Leo\'s beds; the back room, with Elena\'s and Mara\'s beds and Mara\'s bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour\'s house. Do not mention any other object or place.\nWhat you remember from the days before:\n- Day 1: Daniel boards the front windows on his own while the others watch. (you did it)\n- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you saw it)\n- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)\n- Day 2: Daniel says they should cross to the neighbour\'s house tonight and see what is left there. (you did it)\n- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)\n- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you did it)\n- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you did it)\n- Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you did it)\n- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)\n- Day 4: Daniel empties Mara\'s bag onto the bed while she is standing there. (you did it)\n- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)\nWhat you are sure of this morning:\n- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)\n- You know where the can went: you ate it yourself in the night, and nobody saw.\nWhat else happened this morning, most recent last:\n- nothing else yet\nNow, minute 00, you are in the kitchen.\n- Elena is here, standing at the pantry.\n- Leo is here, standing at the pantry.\n- Mara is here, standing at the pantry.\n- 2 portions on the shelf.\nYou are the first to act in the kitchen this turn.\nYour options:\n- silent: stay put and say nothing\n- accuse_elena: (speech) accuse Elena of taking it\n- accuse_leo: (speech) accuse Leo of taking it\n- accuse_mara: (speech) accuse Mara of taking it\n- confess: (speech) admit taking it\n- reassure_elena: (speech) reassure Elena\n- reassure_leo: (speech) reassure Leo\n- reassure_mara: (speech) reassure Mara\n- reassure_all: (speech) reassure everyone here\n- say_other: (speech) say something else\n- sit_elena: sit with Elena\n- sit_leo: sit with Leo\n- sit_mara: sit with Mara\n- aside_elena: take Elena aside to the brothers room\n- aside_leo: take Leo aside to the brothers room\n- aside_mara: take Mara aside to the brothers room\n- search: search the kitchen for the can (takes about six minutes)\n- go_brothers_room: go to the brothers room\n- go_back_room: go to the back room\n- go_bathroom: go to the bathroom\n- eat: eat one of the portions\n- share: share out what is left among everyone here' : ('daniel_ate_it', 'daniel')

----------------------------------------------------------------------
Ran 52 tests in 11.858s

FAILED (failures=3)
exit 1
```

## Tests after the change

```
$ .venv/Scripts/python.exe -m unittest -v test_morning.PromptTruthTest; echo "exit $?"
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... ok
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... ok
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.117s

OK
exit 0
```

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning; echo "exit $?"
test_a_morning_completes_and_writes_a_story (test_morning.FakeMorningTest.test_a_morning_completes_and_writes_a_story) ... ok
test_an_admission_cannot_be_taken_back (test_morning.FakeMorningTest.test_an_admission_cannot_be_taken_back) ... ok
test_at_most_one_call_per_person_per_turn (test_morning.FakeMorningTest.test_at_most_one_call_per_person_per_turn) ... ok
test_every_kind_of_broken_answer_falls_back_to_the_rules (test_morning.FakeMorningTest.test_every_kind_of_broken_answer_falls_back_to_the_rules) ... ok
test_nothing_from_target_morning_reaches_a_prompt (test_morning.FakeMorningTest.test_nothing_from_target_morning_reaches_a_prompt) ... ok
test_only_daniel_knows_and_only_daniel_may_confess (test_morning.FakeMorningTest.test_only_daniel_knows_and_only_daniel_may_confess) ... ok
test_prompts_are_short (test_morning.FakeMorningTest.test_prompts_are_short) ... ok
test_replay_is_byte_for_byte_with_no_client_reached (test_morning.FakeMorningTest.test_replay_is_byte_for_byte_with_no_client_reached) ... ok
test_replay_without_a_cache_stops_cleanly (test_morning.FakeMorningTest.test_replay_without_a_cache_stops_cleanly) ... ok
test_seeds_do_not_share_answers (test_morning.FakeMorningTest.test_seeds_do_not_share_answers) ... ok
test_the_call_cap_counts_answers_from_an_earlier_run (test_morning.FakeMorningTest.test_the_call_cap_counts_answers_from_an_earlier_run) ... ok
test_the_call_cap_stops_the_morning_cleanly (test_morning.FakeMorningTest.test_the_call_cap_stops_the_morning_cleanly) ... ok
test_calls_are_spaced (test_morning.GeminiClientTest.test_calls_are_spaced) ... ok
test_daily_quota_stops_keeps_the_cache_and_resumes (test_morning.GeminiClientTest.test_daily_quota_stops_keeps_the_cache_and_resumes) ... ok
test_missing_key_stops_with_a_clear_message (test_morning.GeminiClientTest.test_missing_key_stops_with_a_clear_message) ... ok
test_per_minute_429_backs_off_and_retries (test_morning.GeminiClientTest.test_per_minute_429_backs_off_and_retries) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
ok
test_repeated_429_gives_up_cleanly (test_morning.GeminiClientTest.test_repeated_429_gives_up_cleanly) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
ok
test_the_key_is_never_printed_or_saved (test_morning.GeminiClientTest.test_the_key_is_never_printed_or_saved) ... ok
test_a_false_accusation_raises_a_grudge_toward_the_accuser (test_morning.PressureTest.test_a_false_accusation_raises_a_grudge_toward_the_accuser) ... ok
test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed (test_morning.PressureTest.test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed) ... ok
test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes (test_morning.PressureTest.test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes) ... ok
test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster (test_morning.PressureTest.test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster) ... ok
test_confessing_after_denying_it_and_after_accusing (test_morning.PressureTest.test_confessing_after_denying_it_and_after_accusing) ... ok
test_daniel_accusing_someone_counts_once (test_morning.PressureTest.test_daniel_accusing_someone_counts_once) ... ok
test_daniels_guilt_rises_by_the_rules (test_morning.PressureTest.test_daniels_guilt_rises_by_the_rules) ... ok
test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not (test_morning.PressureTest.test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not) ... ok
test_inner_moments_come_at_most_once_every_9_minutes (test_morning.PressureTest.test_inner_moments_come_at_most_once_every_9_minutes) ... ok
test_naming_yourself_counts_as_nobody (test_morning.PressureTest.test_naming_yourself_counts_as_nobody) ... ok
test_no_prompt_holds_the_old_verdicts (test_morning.PressureTest.test_no_prompt_holds_the_old_verdicts) ... ok
test_reassure_is_not_offered_toward_a_grudge_of_3 (test_morning.PressureTest.test_reassure_is_not_offered_toward_a_grudge_of_3) ... ok
test_take_aside_accepted (test_morning.PressureTest.test_take_aside_accepted) ... ok
test_take_aside_needs_someone_yet_to_act_and_an_empty_room (test_morning.PressureTest.test_take_aside_needs_someone_yet_to_act_and_an_empty_room) ... ok
test_take_aside_refused (test_morning.PressureTest.test_take_aside_refused) ... ok
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... ok
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... ok
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... ok
test_a_second_model_from_the_config (test_morning.ScenarioTest.test_a_second_model_from_the_config) ... ok
test_each_scenario_runs_with_the_fake_model (test_morning.ScenarioTest.test_each_scenario_runs_with_the_fake_model) ... ok
test_in_miscount_every_accusation_is_false (test_morning.ScenarioTest.test_in_miscount_every_accusation_is_false) ... ok
test_mara_as_the_culprit_carries_the_guilt (test_morning.ScenarioTest.test_mara_as_the_culprit_carries_the_guilt) ... ok
test_the_culprit_comes_from_the_scenario (test_morning.ScenarioTest.test_the_culprit_comes_from_the_scenario) ... ok
test_the_story_speaks_of_the_culprit (test_morning.ScenarioTest.test_the_story_speaks_of_the_culprit) ... ok
test_a_conversation_ends_after_two_full_turns_with_nothing_new (test_morning.SequentialTalkTest.test_a_conversation_ends_after_two_full_turns_with_nothing_new) ... ok
test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again (test_morning.SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again) ... ok
test_an_inner_moment_can_start_the_talk_again (test_morning.SequentialTalkTest.test_an_inner_moment_can_start_the_talk_again) ... ok
test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn (test_morning.SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn) ... ok
test_metrics_work_out_the_same_conversations_as_the_morning (test_morning.SequentialTalkTest.test_metrics_work_out_the_same_conversations_as_the_morning) ... ok
test_no_speech_act_runs_past_three_turns_in_any_fake_morning (test_morning.SequentialTalkTest.test_no_speech_act_runs_past_three_turns_in_any_fake_morning) ... ok
test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to (test_morning.SequentialTalkTest.test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to) ... ok
test_the_one_just_accused_acts_next (test_morning.SequentialTalkTest.test_the_one_just_accused_acts_next) ... ok
test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house (test_morning.SequentialTalkTest.test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house) ... ok
test_ties_are_broken_by_the_seed (test_morning.SequentialTalkTest.test_ties_are_broken_by_the_seed) ... ok

----------------------------------------------------------------------
Ran 52 tests in 10.972s

OK
exit 0
```

## A prompt built with the fake model: Mara as culprit, minute 87

- The script runs a mara_ate_it morning against `FakeClient`, turns 0 to 28 (minutes 00 to 84).
- It prints each person's "About the can" line, then Mara's prompt for minute 87.
- The script was kept outside the repo. Its source:

```python
"""Builds Mara's prompt late in a mara_ate_it morning, against the fake model only.

    python mara_prompt.py <seed>      (run from Prototypes/llm-morning)
"""
import os, sys, tempfile
sys.path.insert(0, os.getcwd())
from gemini import Cache, FakeClient, Oracle
from world import Morning

SEED = int(sys.argv[1])
LAST = 28                                   # turns 0 to 28: minutes 00 to 84
tmp = tempfile.mkdtemp(prefix="mara-prompt-")
m = Morning(Oracle(Cache(os.path.join(tmp, "fake.json")), "fake", SEED, client=FakeClient()), SEED, "mara_ate_it")
for t in range(LAST + 1):
    m.turn(t)
t = LAST + 1                                # minute 87
for p in m.people.values():
    line = next(x for x in m.inside_lines(p) if x.startswith("About the can"))
    print(f"{p.name}: {line}")
print("-----")
mara = m.people["mara"]
print(m.prompt_for(mara, t, m.options_for(mara)))
```

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe mara_prompt.py 11; echo "exit $?"
Daniel: About the can (a little): you thought Elena took it, at minute 78.
Elena: About the can (a little): you thought Daniel took it, at minute 84.
Leo: About the can: Mara admitted taking it at minute 06.
Mara: About the can: you ate it yourself.
-----
You are Mara, 17, the youngest, the daughter of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).
How you address them: Elena "Mom"; Daniel "Daniel"; Leo "Leo".
Who you are: Younger sister. Frightened and easy to read, but old enough to resent being handled like a child. Everything she feels reaches her face before she decides to show it.
Temperament: somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest.
What matters to you: closeness, deciding for yourself, fairness.
Your body: hungry.
About the can: you ate it yourself.
Against Daniel (a little): you were angry with Daniel at minute 54.
Against Elena (some): you were angry with Elena at minutes 06, 45 and 48.
Against Leo (a lot): you were angry with Leo at minutes 12, 18, 63 and 66.
On your conscience (some): you ate the can in the night, and nobody saw; you accused Daniel of what you did, at minute 03.
The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo's room); back room (Elena and Mara's room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel's and Leo's beds; the back room, with Elena's and Mara's beds and Mara's bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour's house. Do not mention any other object or place.
What you remember from the days before:
- Day 2: Elena counts what is left in the pantry with Mara beside her. (you saw it)
- Day 3: Mara cries in the night. Elena sits with her until it stops. (you saw it)
- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
- Day 3: In the night Mara eats a can sitting on the kitchen floor. Nobody sees. (you did it)
- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)
- Day 4: Daniel empties Mara's bag onto the bed while she is standing there. (you saw it)
- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)
What you are sure of this morning:
- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)
- You know where the can went: you ate it yourself in the night, and nobody saw.
- min 00: Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; you had your part.
- min 06: you admitted aloud that you took the can, in front of Daniel, Elena, Leo.
Your own last words this morning:
- min 06, you admitted taking it: "[fake line 12]"
- min 12, you reassured Elena: "[fake line 19]"
- min 54, you said: "[fake line 39]"
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 48: Elena leaves for the brothers room.
- min 51: you stayed where you were and said nothing. You felt tired.
- min 54: you said: "[fake line 39]". You felt afraid.
- min 63: you asked Daniel to come aside to the back room. You felt angry.
- min 63: Daniel came with you to the back room.
- min 63: You and Daniel are in the back room, away from the others.
- min 66: you went to the kitchen. You felt ashamed.
- min 84: Elena comes into the kitchen.
Now, minute 87, you are in the kitchen.
- Elena is here, just come in. Elena looks afraid.
- 0 portions on the shelf.
You are the first to act in the kitchen this turn.
What you have been doing: you have stayed put and said nothing, 6 turns in a row.
In that time nobody has said anything to you or to everyone.
Your options:
- silent: stay put and say nothing
- reassure_elena: (speech) reassure Elena
- say_other: (speech) say something else
- sit_elena: sit with Elena
- aside_elena: take Elena aside to the back room
- go_brothers_room: go to the brothers room
- go_back_room: go to the back room
- go_bathroom: go to the bathroom
exit 0
```

The new lines:
- `About the can: you ate it yourself.` Before the fix, this was "About the can: you have not settled on who took it."
- `min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)`
- Leo, who heard the confession, gets `About the can: Mara admitted taking it at minute 06.`

Seed 11 was picked from a scan of seeds 1-20, shown below. It is the first seed where both new lines appear. At seed 1 Mara's line is a suspicion line instead.

## Found, not changed

A suspicion from the person's own answers still wins over what they know. This is outside the scope given ("do not change … any other prompt text"). In the fake morning the model names a random suspect, so it happens often:

- **Seed 1, Mara (the culprit):** `About the can (some): you thought Leo took it, at minutes 69 and 72.` She knows she ate it. The line contradicts her own sure line, "You know where the can went: you ate it yourself".
- **Seed 11, Daniel and Elena:** both heard Mara admit it at minute 06 ("you admitted aloud that you took the can, in front of Daniel, Elena, Leo"). Their lines are still `you thought Elena took it, at minute 78` and `you thought Daniel took it, at minute 84`.
- **In the saved real runs:** knowledge_audit.md §S5 counted 53 of 53 culprit prompts at suspicion 0, so the culprit case never occurred in cache/v5. The listener case is not counted there.

The scan (the four "About the can" lines at minute 87, seeds 1-20):

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe scan_seeds.py
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
```

To close this gap, the knowledge line would take precedence over the suspicion line whenever `knows_culprit` is set. That would change the suspicion text for those people, so it needs a decision.

The all-in-one merge (`merge-slice-docs.py`) was not run. This work produced one document, and the only folder the script could merge, `reports/`, holds unrelated audits.
