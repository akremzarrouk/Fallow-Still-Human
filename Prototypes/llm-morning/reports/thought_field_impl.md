# A thought field on every decision; Leo's night line in "About the can"

Mode: implement. No API was called and no real morning was run. The only morning run outside the
tests was the fake-client run §6 asks for (`--fake`: FakeClient, no network). Paths are relative
to `Prototypes/llm-morning/`.

**Commit: `177e300`** ("LLM morning: a thought before every decision; Leo's night line in
"About the can""). Before it, `d2e7f99` committed `reports/witness_probe3.md`, which was
untracked; without it git status would not be clean.

## Result

| Done when | Result |
|---|---|
| The new tests fail before the change | **15 fail** (11 FAIL, 4 ERROR), each because the feature is missing (§3) |
| ... and pass after | **71 of 71 pass** (§4) |
| The full suite passes | **OK**, 71 tests (62 before this change; §4) |
| The v6 runs replay identically from v6/ with 0 requests | **6 of 6 IDENTICAL**, story and transcript, 0 API calls (§5) |
| git status is clean apart from the three old replay.md files | **Yes** (§7) |

**Something to decide: the longer system instruction trips the prompt budget more often (§8).**
- The added sentence raises `estimate_tokens(SYSTEM)` from 254 to 281.
- `PROMPT_TOKEN_BUDGET` is still 1400 (world.py:52), because the brief says not to change the
  config or rules. So prompts near the limit now lose one more memory or backstory line.
- The v6 runs' own prompts, measured against the new SYSTEM: 183 of 252 are over 1400.
- **At minute 00 this breaks the design's one-line difference for Leo in seeds 2 and 3.** His
  witness prompt estimates 1411 and 1412, against 1387 and 1388 for daniel_ate_it. It would drop
  its oldest backstory line and add "- (earlier things, left out here)".
- **What stays true.** At minute 00 only Leo's prompt differs between the two scenarios.
- **Why T3 still passes.** T3 builds fresh mornings in which nobody has acted yet. Those prompts
  estimate 1351 to 1400, and Leo's witness prompt 1374 (§8), so nothing is cut and the difference
  is exactly the one line.
- **Raising the budget by about 27, to 1427,** would restore the old cut points. That is your
  call; nothing was changed.

---

## 1. What changed

**0. v6/ freeze.**
- v6/ holds copies of data, gemini, metrics, metrics3, metrics4, metrics5, morning, story, talk
  and world. These are the same modules v5/ holds. Each is byte-identical to HEAD before the
  change (§5).
- v6/check.py is v5/check.py with `RUNS` set to the six v6 runs: daniel_ate_it and
  daniel_ate_it_leo_heard, seeds 1 to 3, gemini-3.5-flash-lite.
- As in the v5 freeze (a609ec7), new runs default to v7 (morning.py:11-13, 36, 139), and
  .gitignore ignores `runs/v7/fake/` and `cache/v7/fake-*`.

**1. Schema and system instruction.** These are exactly variant C of probe 2, §3.
- **Schema.** `RESPONSE_SCHEMA` (gemini.py:47-62) gets `thought` as its first property
  (gemini.py:52). It is first in `required` (gemini.py:60), and there is an explicit
  `property_ordering` (gemini.py:61). The dict equals probe 2's schema_C.json
  (test `test_the_schema_asks_for_a_thought_first`).
- **System instruction.** `SYSTEM` (world.py:27-40) gets one sentence immediately before
  "Reply with JSON only": "`thought` is what goes through their mind first, in two or three
  sentences, before they choose."
- **The JSON example is unchanged.** The test compares SYSTEM against v6/world.py's SYSTEM.
- **What the SDK receives.** The config handed to the (stubbed) API carries the ordering
  `thought, option, say, feeling, reason, suspects, angry_at`
  (test `test_the_client_sends_the_schema_with_its_order`).

**2. Parser, decision, transcript, story.**
- **Parser.** `Morning.parse` checks `thought` first among the required strings
  (world.py:564). A missing, empty, whitespace-only or non-string `thought` gives
  "no `thought`" and a FALLBACK.
- **Stored.** The whitespace-normalised thought goes into the choice, and so into the decision
  (world.py:589). It is also in each transcript entry: `"thought"`, or `null` for routine and
  fallback decisions (world.py:673).
- **Story.** The decision line reads `Thought: “…” Reason: “…”` (story.py:84). The "Chose"
  legend now names the thought, and says no prompt shows it (story.py:155-157).
- **Prompts.** `prompt_for` was not touched. No prompt holds a thought: see the tests in §2 and
  the fake run in §6.

**3. Fake and stub clients.**
- `FakeClient` answers with `"thought": "Fake thought N."` as its first key (gemini.py:167).
- `StubApi` answers through FakeClient, so it gets the thought too. It now also keeps the
  config it was sent.
- The test policy client `Scripted` answers with `"Scripted thought N."`.
- FakeClient's four broken kinds are unchanged.

**4. daniel_ate_it_leo_heard.**
- **The backstory event is gone.** The scenario's `after_night` event is removed. Its data is
  now `"about_the_can": {"leo": "Last night you woke and heard someone in the kitchen open a
  can; you did not see who."}` (data.py:118-125), read by `data.about_the_can` (data.py:178-181).
- **Where the sentence goes.** `Person.can_note` holds it (world.py:214). `inside_lines`
  appends it, after one space, to whichever "About the can" line the person gets
  (world.py:427-445):
  - "you have not settled…";
  - "(level): you thought X took it…";
  - "X admitted taking it…".
- **Probe variant B** appended it to the only form Leo had at minute 00, "you have not
  settled…". Here the note stays on every later form of the line as well. §6 shows it on
  Leo's suspicion lines.
- **Story.** The backstory table loses its Leo "heard it" row. The cast table's "Knows about
  the can" cell for Leo now reads `only that it is missing; told: “<the sentence>”`
  (story.py:217-222).
- **Left in place.** `backstory()` still reads an optional `after_night` (data.py:169), but no
  scenario uses it now.

**Not changed.**
- Any other prompt text, the options, the rules, config.json, v1/ to v5/, and runs/ and cache/.
- `PROMPT_TOKEN_BUDGET` (see §8).

## 2. Tests (written first)

**New class `ThoughtFieldTest`: 9 tests.**

| Test | Checks |
|---|---|
| `test_the_schema_asks_for_a_thought_first` | `RESPONSE_SCHEMA` equals variant C's schema; `thought` is its first property |
| `test_the_client_sends_the_schema_with_its_order` | the config GeminiClient sends carries that property ordering |
| `test_the_system_instruction_adds_one_sentence_before_the_reply_line` | SYSTEM = v6/world.py's SYSTEM with the one sentence before "Reply with JSON only"; the text from "Reply with JSON only" on is unchanged and has no `thought` |
| `test_the_parser_keeps_the_thought` | whitespace-normalised thought in the choice |
| `test_the_parser_refuses_an_answer_without_a_thought` | missing, `""`, `"   "`, `null`, `3`, `["a"]` → `(None, "no `thought`")` |
| `test_the_fake_client_gives_a_thought_first` | FakeClient's JSON starts with a non-empty `thought` |
| `test_the_decision_and_the_transcript_keep_the_thought` | every model decision holds its answer's thought; transcript entries hold the same, `null` for the rest |
| `test_no_prompt_shows_a_thought` | a fake morning: no cached prompt holds "Fake thought" or any returned thought; a scripted morning: no prompt holds "Scripted thought" |
| `test_the_story_tells_the_thought_next_to_the_reason` | one `Thought: “Fake thought N.” Reason: “Fake reason N.”` per model decision, N matching |

**T1 to T8 (`WitnessScenarioTest`), updated for the move.** NOTE is the appended sentence. HEARD
is the old backstory sentence.

| # | Now checks |
|---|---|
| T1 | `about_the_can(WITNESS, "leo")` is NOTE; NOTE contains no family name, its only capitalised word is "Last", no "eats a can" |
| T2 | every backstory, Leo's included, equals daniel_ate_it's; no Leo line holds "Daniel eats" or HEARD (renamed `test_no_backstory_differs`) |
| T3 | minute 00, seeds 1–3: Daniel, Elena, Mara prompts equal; Leo's `sure` and options equal, and his diff is exactly `- About the can: you have not settled on who took it.` / `+ …same… ` + NOTE (renamed `…differs_by_his_can_line`) |
| T4 | no Daniel prompt holds NOTE, HEARD, "woke and heard", "wakes and hears", "open a can", "did not see who", "does not see who" or "heard someone"; the conscience line still says "and nobody saw" |
| T5 | no prompt holds HEARD. Every Leo prompt has NOTE on exactly one line, his only "About the can" line, which ends with it; what comes before it is one of the three rules-made forms; no "Daniel eats a can", "you ate it yourself", "On your conscience". No other prompt holds NOTE. "open a can" occurs nowhere outside NOTE |
| T6 | unchanged |
| T7 | backstory lengths 13, 13, 12, **13** (was 14); no backstory line holds HEARD or NOTE; `about_the_can` is NOTE only for (WITNESS, leo), `None` for every other scenario and person |
| T8 | the witness story's cast row reads `… \| only that it is missing; told: “NOTE” \| …` and holds no HEARD; daniel_ate_it's row is unchanged |

- **What T5(d) checks now.** It used to say no prompt line holds both "Daniel" and "open a can".
  Leo's line can now be "you thought Daniel took it, … . <NOTE>", so that check was replaced: the
  can being opened appears only inside NOTE, and T1 shows NOTE names nobody.
- **"Daniel" on that line is not new information.** It comes from Leo's own suspicion, which
  the rules print.

**Diff of test_morning.py** (`git diff d2e7f99 177e300 -- test_morning.py`):

```diff
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index bc6a10e..229fb3d 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -4,6 +4,7 @@
 """
 import contextlib
 import difflib
+import importlib.util
 import io
 import json
 import os
@@ -17,7 +18,7 @@ import metrics
 import gemini
 from gemini import Cache, FakeClient, GeminiClient, Oracle
 from morning import run
-from world import QUIET_TURNS, SYSTEM, Grudge, Morning, Person, Track, estimate_tokens
+from world import QUIET_TURNS, SYSTEM, Grudge, Morning, Option, Person, Track, estimate_tokens
 
 # What the third version's prompts said about guilt, suspicion and grudges: verdicts, which
 # the prompts must no longer contain.
@@ -135,6 +136,7 @@ class StubApi:
 
     def generate_content(self, model, contents, config):
         self.calls += 1
+        self.config = config
         step = self.script.pop(0) if self.script else "ok"
         if isinstance(step, Exception):
             raise step
@@ -307,8 +309,9 @@ class Scripted:
         option, say = answer[:2]
         suspects, angry_at = answer[2:] if len(answer) == 4 else ("nobody", "nobody")
         self.asked.append((minute, who))
-        return json.dumps({"option": option, "say": say, "feeling": "tense", "reason": "Scripted.",
-                           "suspects": suspects, "angry_at": angry_at})
+        return json.dumps({"thought": f"Scripted thought {self.requests}.", "option": option, "say": say,
+                           "feeling": "tense", "reason": "Scripted.", "suspects": suspects,
+                           "angry_at": angry_at})
 
 
 def scripted(policy, dirs, seed=1, turns=None):
@@ -909,15 +912,145 @@ class PromptTruthTest(unittest.TestCase):
                 self.assertNotIn("A can that should be on the shelf is not", prompt, (scenario, pid))
 
 
+THOUGHT_SENTENCE = ("`thought` is what goes through their mind first, in two or three sentences, before "
+                    "they choose. ")
+FIELDS = ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"]
+# Variant C of reports/witness_probe2.md, section 3.
+THOUGHT_SCHEMA = {
+    "type": "object",
+    "properties": {
+        "thought": {"type": "string"},
+        "option": {"type": "string"},
+        "say": {"type": "string", "nullable": True},
+        "feeling": {"type": "string"},
+        "reason": {"type": "string"},
+        "suspects": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
+        "angry_at": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
+    },
+    "required": FIELDS,
+    "property_ordering": FIELDS,
+}
+
+
+def frozen_world(version):
+    """vN/world.py, loaded on its own (its SYSTEM is what vN sent)."""
+    spec = importlib.util.spec_from_file_location(f"{version}_world", os.path.join(HERE, version, "world.py"))
+    module = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(module)
+    return module
+
+
+class ThoughtFieldTest(unittest.TestCase):
+    """Every model decision carries a `thought`, written first (reports/witness_probe2.md,
+    variant C). It is kept and told in the story, and never shown in a prompt."""
+
+    def setUp(self):
+        self.dirs = Dirs()
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def answer(self, **over):
+        ans = {"thought": "  Someone   took it.\nI wonder who. ", "option": "silent", "say": None,
+               "feeling": "tense", "reason": "I wait.", "suspects": "nobody", "angry_at": "nobody"}
+        ans.update(over)
+        return json.dumps({k: v for k, v in ans.items() if v is not ...})
+
+    def test_the_schema_asks_for_a_thought_first(self):
+        self.assertEqual(gemini.RESPONSE_SCHEMA, THOUGHT_SCHEMA)
+        self.assertEqual(list(gemini.RESPONSE_SCHEMA["properties"])[0], "thought")
+
+    def test_the_client_sends_the_schema_with_its_order(self):
+        old = os.environ.get("GEMINI_API_KEY")
+        os.environ["GEMINI_API_KEY"] = SECRET
+        try:
+            api = StubApi([])
+            GeminiClient(gemini.load_config(CONFIG), 1, api=api, sleep=lambda s: None,
+                         clock=lambda: 0.0).generate(SYSTEM, "- silent: stay put")
+        finally:
+            if old is None:
+                os.environ.pop("GEMINI_API_KEY", None)
+            else:
+                os.environ["GEMINI_API_KEY"] = old
+        schema = api.config.response_schema
+        ordering = schema["property_ordering"] if isinstance(schema, dict) else schema.property_ordering
+        self.assertEqual(ordering, FIELDS)
+
+    def test_the_system_instruction_adds_one_sentence_before_the_reply_line(self):
+        old = frozen_world("v6").SYSTEM
+        self.assertEqual(old.count("Reply with JSON only"), 1)
+        self.assertEqual(SYSTEM, old.replace("Reply with JSON only", THOUGHT_SENTENCE + "Reply with JSON only"))
+        # The JSON example at its end is unchanged: it does not list `thought`.
+        self.assertEqual(SYSTEM.split("Reply with JSON only")[1], old.split("Reply with JSON only")[1])
+        self.assertNotIn("thought", SYSTEM.split("Reply with JSON only")[1])
+
+    def test_the_parser_keeps_the_thought(self):
+        opts = [Option("silent", "stay put", kind="silent")]
+        choice, why = Morning.parse(self.answer(), opts)
+        self.assertIsNone(why)
+        self.assertEqual(choice["thought"], "Someone took it. I wonder who.")
+
+    def test_the_parser_refuses_an_answer_without_a_thought(self):
+        opts = [Option("silent", "stay put", kind="silent")]
+        for bad in (..., "", "   ", None, 3, ["a"]):
+            self.assertEqual(Morning.parse(self.answer(thought=bad), opts), (None, "no `thought`"), bad)
+
+    def test_the_fake_client_gives_a_thought_first(self):
+        text = FakeClient(invalid_every=0).generate("", "Your options:\n- silent: stay put")
+        ans = json.loads(text)
+        self.assertEqual(list(ans)[0], "thought")
+        self.assertTrue(isinstance(ans["thought"], str) and ans["thought"].strip())
+
+    def test_the_decision_and_the_transcript_keep_the_thought(self):
+        m, client = scripted(lambda who, minute, options, c: ("silent", None), self.dirs, turns=3)
+        model = [d for rec in m.log for d in rec["decisions"] if d["mode"] == "model"]
+        self.assertTrue(model)
+        thoughts = [d["thought"] for d in model]
+        self.assertEqual(sorted(thoughts), sorted(f"Scripted thought {i}." for i in range(1, client.requests + 1)))
+        acts = [a for tt in m.transcript["turns"] for a in tt["acts"]]
+        self.assertEqual([a["thought"] for a in acts if a["mode"] == "model"], thoughts)
+        self.assertEqual({a["thought"] for a in acts if a["mode"] != "model"}, {None})
+
+    def test_no_prompt_shows_a_thought(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        self.assertEqual(code, 0, out)
+        entries = [e for name in os.listdir(self.dirs.cache)
+                   for e in json.loads(read(os.path.join(self.dirs.cache, name))).values()]
+        thoughts = [json.loads(e["response"])["thought"] for e in entries
+                    if e["response"].startswith("{") and "thought" in json.loads(e["response"])]
+        self.assertTrue(thoughts)
+        for e in entries:
+            self.assertNotIn("Fake thought", e["prompt"])
+            for t in thoughts:
+                self.assertNotIn(t, e["prompt"])
+        m, client = scripted(lambda who, minute, options, c: ("silent", None), self.dirs, turns=6)
+        self.assertTrue(client.prompts)
+        for _, _, prompt in client.prompts:
+            self.assertNotIn("Scripted thought", prompt)
+
+    def test_the_story_tells_the_thought_next_to_the_reason(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        self.assertEqual(code, 0, out)
+        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
+        pairs = re.findall(r"Thought: “Fake thought (\d+)\.” Reason: “Fake reason (\d+)\.”", story)
+        self.assertEqual(len(pairs), meta["model_decisions"])
+        self.assertTrue(all(a == b for a, b in pairs))
+        self.assertEqual(story.count("Reason: “"), meta["model_decisions"])
+
+
 WITNESS = "daniel_ate_it_leo_heard"
+# Where the line was until v6: a backstory event of Leo's (reports/witness_design.md, section 1).
 HEARD = ("In the night Leo wakes and hears someone in the kitchen open a can. "
          "He does not get up and does not see who.")
-HEARD_LINE = "Day 3: " + HEARD + " (you heard it)"
+# Where it is now: appended to Leo's "About the can:" line (reports/witness_probe.md, variant B).
+NOTE = "Last night you woke and heard someone in the kitchen open a can; you did not see who."
+CAN_LINE = "About the can: you have not settled on who took it."
 
 
 class WitnessScenarioTest(unittest.TestCase):
     """daniel_ate_it_leo_heard: daniel_ate_it, and Leo heard the night but did not see who
-    (reports/witness_design.md, sections 1 to 3)."""
+    (reports/witness_design.md, sections 1 to 3). What he heard is told in his "About the can:"
+    line, not in his backstory."""
 
     def setUp(self):
         self.assertIn(WITNESS, data.SCENARIOS)
@@ -940,25 +1073,21 @@ class WitnessScenarioTest(unittest.TestCase):
 
     # T1
     def test_the_sentence_names_nobody_leo_heard(self):
-        added = [e for e in data.backstory(WITNESS) if e not in data.backstory("daniel_ate_it")]
-        self.assertEqual(added, [(3, HEARD, {"leo": "heard"})])
-        text = added[0][1]
-        for name in ("Daniel", "Elena", "Mara"):
-            self.assertNotIn(name, text)
-        self.assertEqual(set(re.findall(r"\b[A-Z]\w*", text)) - {"In", "He"}, {"Leo"})
-        self.assertNotIn("eats a can", text)
+        self.assertEqual(data.about_the_can(WITNESS, "leo"), NOTE)
+        for name in ("Daniel", "Elena", "Leo", "Mara"):
+            self.assertNotIn(name, NOTE)
+        self.assertEqual(set(re.findall(r"\b[A-Z]\w*", NOTE)), {"Last"})
+        self.assertNotIn("eats a can", NOTE)
 
     # T2
-    def test_only_leos_backstory_differs(self):
-        for pid in ("daniel", "elena", "mara"):
+    def test_no_backstory_differs(self):
+        for pid in data.ORDER:
             self.assertEqual(Person(pid, WITNESS).backstory, Person(pid, "daniel_ate_it").backstory, pid)
-        old, new = Person("leo", "daniel_ate_it").backstory, Person("leo", WITNESS).backstory
-        at = next(i for i, x in enumerate(old) if x.startswith("Day 3: Mara freezes")) + 1
-        self.assertEqual(new, old[:at] + [HEARD_LINE] + old[at:])
-        self.assertFalse([x for x in new if "Daniel eats" in x])
+        self.assertEqual(data.backstory(WITNESS), data.backstory("daniel_ate_it"))
+        self.assertFalse([x for x in Person("leo", WITNESS).backstory if "Daniel eats" in x or HEARD in x])
 
     # T3
-    def test_at_minute_00_only_leos_prompt_differs_by_the_one_line(self):
+    def test_at_minute_00_only_leos_prompt_differs_by_his_can_line(self):
         for seed in (1, 2, 3):
             old, new = self.morning("daniel_ate_it", seed), self.morning(WITNESS, seed)
             for pid in data.ORDER:
@@ -971,15 +1100,16 @@ class WitnessScenarioTest(unittest.TestCase):
                     self.assertEqual(b, a, (seed, pid))
                     continue
                 diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
-                self.assertEqual([d for d in diff if d.startswith("+ ")], ["+ - " + HEARD_LINE], seed)
-                self.assertEqual([d for d in diff if d.startswith("- ")], [], seed)
+                self.assertEqual([d for d in diff if d.startswith("+ ")], ["+ " + CAN_LINE + " " + NOTE], seed)
+                self.assertEqual([d for d in diff if d.startswith("- ")], ["- " + CAN_LINE], seed)
 
     # T4
     def test_daniels_prompt_never_mentions_being_heard(self):
         daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
         self.assertTrue(daniel)
         for p in daniel:
-            for words in (HEARD, "wakes and hears", "open a can", "does not see who", "heard someone"):
+            for words in (NOTE, HEARD, "woke and heard", "wakes and hears", "open a can", "did not see who",
+                          "does not see who", "heard someone"):
                 self.assertNotIn(words, p)
             if "On your conscience" in p:
                 self.assertIn("and nobody saw", p)
@@ -991,13 +1121,23 @@ class WitnessScenarioTest(unittest.TestCase):
         leo = [p for p in prompts if p.startswith("You are Leo,")]
         self.assertTrue(leo)
         for p in prompts:
+            self.assertNotIn(HEARD, p)
             if p.startswith("You are Leo,"):
-                self.assertEqual([x for x in p.splitlines() if HEARD in x], ["- " + HEARD_LINE])
+                # The note ends his one "About the can" line, whatever that line says before it.
+                lines = [x for x in p.splitlines() if NOTE in x]
+                self.assertEqual(len(lines), 1)
+                self.assertTrue(lines[0].endswith(" " + NOTE), lines[0])
+                self.assertEqual([x for x in p.splitlines() if x.startswith("About the can")], lines)
+                self.assertRegex(lines[0][:-len(" " + NOTE)],
+                                 r"^About the can(: you have not settled on who took it\."
+                                 r"| \([a-z ]+\): you thought \w+ took it, at minutes? [\d, and]+\."
+                                 r"|: \w+ admitted taking it at minute \d\d\.)$")
                 for words in ("Daniel eats a can", "you ate it yourself", "On your conscience"):
                     self.assertNotIn(words, p)
             else:
-                self.assertNotIn(HEARD, p)
-            self.assertFalse([x for x in p.splitlines() if "Daniel" in x and "open a can" in x])
+                self.assertNotIn(NOTE, p)
+            # The can being opened is told only in the note, which names nobody (T1).
+            self.assertNotIn("open a can", p.replace(NOTE, ""))
 
     # T6
     def test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning(self):
@@ -1005,18 +1145,26 @@ class WitnessScenarioTest(unittest.TestCase):
 
     # T7
     def test_the_other_scenarios_do_not_have_the_sentence(self):
-        lengths = {"daniel_ate_it": 13, "mara_ate_it": 13, "miscount": 12, WITNESS: 14}
+        lengths = {"daniel_ate_it": 13, "mara_ate_it": 13, "miscount": 12, WITNESS: 13}
         self.assertEqual({s: len(data.backstory(s)) for s in data.SCENARIOS}, lengths)
         for scenario in data.SCENARIOS:
-            has = [e for e in data.backstory(scenario) if HEARD in e[1]]
-            self.assertEqual(len(has), scenario == WITNESS, scenario)
+            self.assertFalse([e for e in data.backstory(scenario) if HEARD in e[1] or NOTE in e[1]], scenario)
+            for pid in data.ORDER:
+                note = data.about_the_can(scenario, pid)
+                self.assertEqual(note, NOTE if (scenario, pid) == (WITNESS, "leo") else None, (scenario, pid))
 
     # T8
     def test_the_witness_morning_runs_and_its_story_shows_who_heard(self):
         (meta, code), out = fake_morning(self.dirs, seed=1, scenario=WITNESS)
         self.assertEqual(code, 0, out)
         story = read(os.path.join(self.dirs.runs, f"{WITNESS}-seed1.md"))
-        self.assertIn(f"| 3 | {HEARD} | not there | not there | heard it | not there |", story)
+        self.assertIn("| Knows about the can | ate it in the night; nobody saw | only that it is missing | "
+                      f"only that it is missing; told: “{NOTE}” | only that it is missing |", story)
+        self.assertNotIn(HEARD, story)
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
+        self.assertIn("| Knows about the can | ate it in the night; nobody saw | only that it is missing | "
+                      "only that it is missing | only that it is missing |", story)
 
 
 class GeminiClientTest(unittest.TestCase):
```

## 3. Test output before the change

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest -v test_morning < /dev/null
```

The 15 failing tests, and the error line of each.
- **What is left out.** The full verbose output is 56 KB. The 56 lines for passing tests and the
  tracebacks are not shown.
- **Long lines are cut.** Error lines over 400 characters stop at 400 and end with "…[cut here]".

```
ERROR: test_the_client_sends_the_schema_with_its_order (test_morning.ThoughtFieldTest.test_the_client_sends_the_schema_with_its_order)
    KeyError: 'property_ordering'

ERROR: test_the_decision_and_the_transcript_keep_the_thought (test_morning.ThoughtFieldTest.test_the_decision_and_the_transcript_keep_the_thought)
    KeyError: 'thought'

ERROR: test_the_parser_keeps_the_thought (test_morning.ThoughtFieldTest.test_the_parser_keeps_the_thought)
    KeyError: 'thought'

ERROR: test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard)
    AttributeError: module 'data' has no attribute 'about_the_can'

FAIL: test_no_prompt_shows_a_thought (test_morning.ThoughtFieldTest.test_no_prompt_shows_a_thought)
    AssertionError: [] is not true

FAIL: test_the_fake_client_gives_a_thought_first (test_morning.ThoughtFieldTest.test_the_fake_client_gives_a_thought_first)
    AssertionError: 'option' != 'thought'

FAIL: test_the_parser_refuses_an_answer_without_a_thought (test_morning.ThoughtFieldTest.test_the_parser_refuses_an_answer_without_a_thought)
    AssertionError: Tuples differ: ({'option': 'silent', 'say': None, 'feelin[102 chars]None) != (None, 'no `thought`')

FAIL: test_the_schema_asks_for_a_thought_first (test_morning.ThoughtFieldTest.test_the_schema_asks_for_a_thought_first)
    AssertionError: {'typ[25 chars]': {'option': {'type': 'string'}, 'say': {'typ[337 chars]at']} != {'typ[25 chars]': {'thought': {'type': 'string'}, 'option': {[475 chars]at']}

FAIL: test_the_story_tells_the_thought_next_to_the_reason (test_morning.ThoughtFieldTest.test_the_story_tells_the_thought_next_to_the_reason)
    AssertionError: 0 != 40

FAIL: test_the_system_instruction_adds_one_sentence_before_the_reply_line (test_morning.ThoughtFieldTest.test_the_system_instruction_adds_one_sentence_before_the_reply_line)
    AssertionError: 'You [729 chars]dy". Reply with JSON only: {"option": "<id>", [130 chars]y>"}' != 'You [729 chars]dy". `thought` is what goes through their mind[226 chars]y>"}'

FAIL: test_at_minute_00_only_leos_prompt_differs_by_his_can_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_his_can_line)
    AssertionError: Lists differ: ['+ - Day 3: In the night Leo wakes and hears[88 chars]it)'] != ['+ About the can: you have not settled on wh[93 chars]ho.']

FAIL: test_no_backstory_differs (test_morning.WitnessScenarioTest.test_no_backstory_differs)
    AssertionError: Lists differ: ['Day[861 chars]'Day 3: In the night Leo wakes and hears someo[272 chars]it)'] != ['Day[861 chars]'Day 4: Leo says maybe they should let someone[138 chars]it)']

FAIL: test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard)
    AssertionError: 'In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who.' unexpectedly found in 'You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Daniel "Daniel"; Mara "Mara".\nWho you are: Calm, rational, reads people well, knows survival. Annoyance shows  …[cut here]

FAIL: test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence)
    AssertionError: {'dan[19 chars]ara_ate_it': 13, 'miscount': 12, 'daniel_ate_it_leo_heard': 14} != {'dan[19 chars]ara_ate_it': 13, 'miscount': 12, 'daniel_ate_it_leo_heard': 13}

FAIL: test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard)
    AssertionError: '| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing; told: “Last night you woke and heard someone in the kitchen open a can; you did not see who.” | only that it is missing |' not found in '# The morning as a story: daniel_ate_it_leo_heard, rules and a language model, seed 1\n\nGenerated by `python morning.py --scenario danie …[cut here]
```

```
----------------------------------------------------------------------
Ran 71 tests in 17.358s

FAILED (failures=11, errors=4)
exit=1
```

- **Before the new tests were written**, the suite ran 62 tests: `Ran 62 tests in 16.784s`, `OK`.
- **Two tests passed before the change:**
  - T4 (Daniel's prompts never mention being heard), which held before the move as well;
  - T6 (no target-morning text).

## 4. Test output after the change

Run on the committed tree:

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest -v test_morning < /dev/null
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
test_after_hearing_a_confession_a_guess_does_not_replace_it (test_morning.PromptTruthTest.test_after_hearing_a_confession_a_guess_does_not_replace_it) ... ok
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... ok
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... ok
test_the_culprit_who_names_someone_else_is_still_told_they_ate_it (test_morning.PromptTruthTest.test_the_culprit_who_names_someone_else_is_still_told_they_ate_it) ... ok
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
test_no_prompt_shows_a_thought (test_morning.ThoughtFieldTest.test_no_prompt_shows_a_thought) ... ok
test_the_client_sends_the_schema_with_its_order (test_morning.ThoughtFieldTest.test_the_client_sends_the_schema_with_its_order) ... ok
test_the_decision_and_the_transcript_keep_the_thought (test_morning.ThoughtFieldTest.test_the_decision_and_the_transcript_keep_the_thought) ... ok
test_the_fake_client_gives_a_thought_first (test_morning.ThoughtFieldTest.test_the_fake_client_gives_a_thought_first) ... ok
test_the_parser_keeps_the_thought (test_morning.ThoughtFieldTest.test_the_parser_keeps_the_thought) ... ok
test_the_parser_refuses_an_answer_without_a_thought (test_morning.ThoughtFieldTest.test_the_parser_refuses_an_answer_without_a_thought) ... ok
test_the_schema_asks_for_a_thought_first (test_morning.ThoughtFieldTest.test_the_schema_asks_for_a_thought_first) ... ok
test_the_story_tells_the_thought_next_to_the_reason (test_morning.ThoughtFieldTest.test_the_story_tells_the_thought_next_to_the_reason) ... ok
test_the_system_instruction_adds_one_sentence_before_the_reply_line (test_morning.ThoughtFieldTest.test_the_system_instruction_adds_one_sentence_before_the_reply_line) ... ok
test_at_minute_00_only_leos_prompt_differs_by_his_can_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_his_can_line) ... ok
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... ok
test_no_backstory_differs (test_morning.WitnessScenarioTest.test_no_backstory_differs) ... ok
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... ok
test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning) ... ok
test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence) ... ok
test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard) ... ok
test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard) ... ok

----------------------------------------------------------------------
Ran 71 tests in 15.501s

OK
exit=0
```

## 5. The v6 replay check

**The frozen copies are identical to the code that made the runs:**

```
$ for f in data gemini metrics metrics3 metrics4 metrics5 morning story talk world; do git show HEAD:Prototypes/llm-morning/$f.py | cmp -s - v6/$f.py && echo "v6/$f.py == HEAD:$f.py" || echo "v6/$f.py DIFFERS"; done
v6/data.py == HEAD:data.py
v6/gemini.py == HEAD:gemini.py
v6/metrics.py == HEAD:metrics.py
v6/metrics3.py == HEAD:metrics3.py
v6/metrics4.py == HEAD:metrics4.py
v6/metrics5.py == HEAD:metrics5.py
v6/morning.py == HEAD:morning.py
v6/story.py == HEAD:story.py
v6/talk.py == HEAD:talk.py
v6/world.py == HEAD:world.py
```

(HEAD was `14311e2` when this ran. The check compares the committed files, not the edited working tree.)

**Replay, run after the change was committed** (at `177e300`):

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe v6/check.py < /dev/null
daniel_ate_it-seed1: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 66 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 44 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 43 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

- **Why "0 API calls" holds.** v6/check.py builds its Oracle with `client=None, replay=True`. Any
  uncached prompt raises `CacheMiss` and makes no request (gemini.py `Oracle.ask`).
- **Nothing in runs/ or cache/ changed.** `git diff --quiet -- runs cache` succeeded, and git
  status shows only the three old replay.md files as untracked.
- **The same check before the edits** gave the same six IDENTICAL lines, exit 0.
- **v5/check.py still passes.** Run after the change, it printed 11 of 11 IDENTICAL lines, exit 0.

## 6. A fake-client run showing the thought

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe morning.py --fake --seed 1 --scenario daniel_ate_it_leo_heard < /dev/null
exit=0
```

It wrote `runs/v7/fake/daniel_ate_it_leo_heard-seed1.*` and
`cache/v7/fake-daniel_ate_it_leo_heard-seed1.json`, both git-ignored. The extract comes from a
read-only script (§9):

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/fake_extract.py
transcript entry (first model act of Leo's):
{"minute": 0, "who": "leo", "room": "kitchen", "option": "go_back_room", "words": null, "audience": ["daniel", "elena", "mara"], "mode": "model", "decided_at": [0, 3], "said_at": [0, 3], "came_of_it": "went to the back room.", "new": null, "new_why": null, "inner": null, "thought": "Fake thought 3.", "suspects": "Leo", "angry_at": "Mara", "moved_to": "back_room"}
story line:
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel reassures Mara: "[fake line 1]"; Mara came to sit with you. **Chose: go to the back room** (one of 20 options). Feeling: *calm*. Thought: “Fake thought 3.” Reason: “Fake reason 3.” Suspects: Leo, so suspicion none. Angry at: Mara; grudge against Mara rose to 1/3. Came of it: went to the back room.
story, cast table:
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing; told: “Last night you woke and heard someone in the kitchen open a can; you did not see who.” | only that it is missing |
75 prompts, 17 of them Leo's; distinct 'About the can' lines in Leo's:
  About the can (a little): you thought Daniel took it, at minute 45. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can (a little): you thought Daniel took it, at minutes 45 and 48. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can (a little): you thought Elena took it, at minute 12. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can (a lot): you thought Daniel took it, at minutes 45, 48, 60 and 63. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can (some): you thought Daniel took it, at minutes 45 and 48. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can (some): you thought Daniel took it, at minutes 45, 48 and 60. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can (some): you thought Daniel took it, at minutes 45, 48, 60 and 63. Last night you woke and heard someone in the kitchen open a can; you did not see who.
  About the can: you have not settled on who took it. Last night you woke and heard someone in the kitchen open a can; you did not see who.
prompts holding 'Fake thought': 0
answers holding a thought: 71 of 75
exit=0
```

- **The 4 answers with no thought** are FakeClient's deliberate "not json" answers. Every 5th
  answer is broken in turn, and 1 kind in 4 is not JSON.

## 7. git

```
$ git log --oneline -3
177e300 LLM morning: a thought before every decision; Leo's night line in "About the can"
d2e7f99 LLM morning: witness probe 3 report (built-in thinking on Flash-Lite E, Gemma G)
14311e2 LLM morning: witness probe 2 report (think-first field C, bigger model D)
$ git show --stat --format= 177e300
 Prototypes/llm-morning/.gitignore      |    2 +
 Prototypes/llm-morning/data.py         |   14 +-
 Prototypes/llm-morning/gemini.py       |    7 +-
 Prototypes/llm-morning/morning.py      |   11 +-
 Prototypes/llm-morning/story.py        |   16 +-
 Prototypes/llm-morning/test_morning.py |  206 +++++-
 Prototypes/llm-morning/v6/check.py     |   55 ++
 Prototypes/llm-morning/v6/data.py      |  180 ++++++
 Prototypes/llm-morning/v6/gemini.py    |  251 ++++++++
 Prototypes/llm-morning/v6/metrics.py   |  182 ++++++
 Prototypes/llm-morning/v6/metrics3.py  |  141 ++++
 Prototypes/llm-morning/v6/metrics4.py  |  149 +++++
 Prototypes/llm-morning/v6/metrics5.py  |  152 +++++
 Prototypes/llm-morning/v6/morning.py   |  146 +++++
 Prototypes/llm-morning/v6/story.py     |  331 ++++++++++
 Prototypes/llm-morning/v6/talk.py      |  105 +++
 Prototypes/llm-morning/v6/world.py     | 1109 ++++++++++++++++++++++++++++++++
 Prototypes/llm-morning/world.py        |   27 +-
 18 files changed, 3030 insertions(+), 54 deletions(-)
$ git status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

**The diff of commit 177e300, except test_morning.py (§2) and the nine copied v6/ modules
(§5).** `git diff d2e7f99 177e300 -- . ':!v6/<copied modules>' ':!test_morning.py'`:

```diff
diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index 61658fb..92e6b98 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -13,3 +13,5 @@ runs/v5/fake/
 cache/v5/fake-*
 runs/v6/fake/
 cache/v6/fake-*
+runs/v7/fake/
+cache/v7/fake-*
diff --git a/Prototypes/llm-morning/data.py b/Prototypes/llm-morning/data.py
index 0064975..8bb3e1e 100644
--- a/Prototypes/llm-morning/data.py
+++ b/Prototypes/llm-morning/data.py
@@ -116,12 +116,12 @@ SCENARIOS = {
     },
 }
 # Not in the shipped data: daniel_ate_it, and Leo heard the night from his bed but did not see
-# who (reports/witness_design.md). The event is Leo's alone, so its sentence names nobody he
-# did not see; it goes in right after the night.
+# who (reports/witness_design.md). It is told to Leo alone, at the end of his "About the can:"
+# line (reports/witness_probe.md, variant B), so it names nobody he did not see.
 SCENARIOS["daniel_ate_it_leo_heard"] = {
     **SCENARIOS["daniel_ate_it"],
-    "after_night": [(3, "In the night Leo wakes and hears someone in the kitchen open a can. "
-                        "He does not get up and does not see who.", {"leo": "heard"})],
+    "about_the_can": {"leo": "Last night you woke and heard someone in the kitchen open a can; "
+                             "you did not see who."},
 }
 DEFAULT_SCENARIO = "daniel_ate_it"
 
@@ -174,6 +174,12 @@ def culprit(scenario):
     """Who took the can in this scenario, or None."""
     return SCENARIOS[scenario]["culprit"]
 
+
+def about_the_can(scenario, pid):
+    """What else this person knows of the night in this scenario, told after their "About the
+    can:" line; or None."""
+    return SCENARIOS[scenario].get("about_the_can", {}).get(pid)
+
 # What everyone saw at the start: Elena's count and what she said about it. It is true in every
 # scenario, miscount included, where nothing was taken.
 OPENING = ("Elena counts the pantry with everyone standing there. She finds one can fewer than she "
diff --git a/Prototypes/llm-morning/gemini.py b/Prototypes/llm-morning/gemini.py
index 2194cfc..fedcfe0 100644
--- a/Prototypes/llm-morning/gemini.py
+++ b/Prototypes/llm-morning/gemini.py
@@ -44,9 +44,12 @@ def load_config(path):
         return json.load(f)
 
 
+# `thought` comes first, and the order is given explicitly, so that it is written before the
+# choice (reports/witness_probe2.md, variant C).
 RESPONSE_SCHEMA = {
     "type": "object",
     "properties": {
+        "thought": {"type": "string"},
         "option": {"type": "string"},
         "say": {"type": "string", "nullable": True},
         "feeling": {"type": "string"},
@@ -54,7 +57,8 @@ RESPONSE_SCHEMA = {
         "suspects": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
         "angry_at": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
     },
-    "required": ["option", "say", "feeling", "reason", "suspects", "angry_at"],
+    "required": ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"],
+    "property_ordering": ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"],
 }
 
 
@@ -160,6 +164,7 @@ class FakeClient:
         pick = options[h % len(options)] if options else "stay"
         speaking = re.search(rf"^- {pick}: \(speech\)", block, flags=re.M) is not None
         answer = {
+            "thought": f"Fake thought {self.requests}.",
             "option": pick,
             "say": f"[fake line {self.requests}]" if speaking else None,
             "feeling": ["afraid", "calm", "ashamed", "angry", "tired"][h % 5],
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 94f2a38..7cb5bde 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -8,8 +8,9 @@
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v6; v4 replays
-                      the fourth version's runs; v5/check.py replays the fifth's)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v7; v4 replays
+                      the fourth version's runs; v5/check.py and v6/check.py replay the
+                      fifth's and sixth's)
 
 The model names and call limits are in config.json. The key is read from GEMINI_API_KEY.
 
@@ -32,13 +33,13 @@ HERE = os.path.dirname(os.path.abspath(__file__))
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v6"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v7"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v5/ can still replay.
+    # cache/vN after), which v1/ to v6/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -135,7 +136,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v6")
+    ap.add_argument("--out", default="v7")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index 00006e0..00ba349 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -81,7 +81,8 @@ def decision_line(d, fold=None):
               f"Angry at: {d['angry_at']}; {d['grudge_note']}.")
     return (f"- **{name}**{order}. {because}.{held} **Chose: {d['label']}**{said}"
             f"{newness(d)} (one of {d['offered']} options). Feeling: *{d['feeling']}*. "
-            f"Reason: {quoted(d['reason'])}{inside} Came of it: {d['came_of_it']}{fact}")
+            f"Thought: {quoted(d['thought'])} Reason: {quoted(d['reason'])}{inside} "
+            f"Came of it: {d['came_of_it']}{fact}")
 
 
 def room_line(rec):
@@ -152,7 +153,8 @@ def render(morning, seed, model_name, command):
       "looks upset in the same room, or someone came in). Only then is the model asked. What "
       "happened is listed.")
     w("- **Chose**: the option the model picked from those the rules offered. Its words are in "
-      "quotes. The feeling and the one-sentence reason are the model's, as it wrote them.")
+      "quotes. The thought (written first, before the choice), the feeling and the one-sentence "
+      "reason are the model's, as it wrote them. Nobody's prompt ever shows a thought.")
     w("- **New / not new**: a line is new if it is a question, an accusation, a denial of a new "
       "accusation, or a confession, and the speaker has not taken that stance before. "
       "Reassurance, repeated stances and other remarks are not new. Something eaten, shared or "
@@ -211,14 +213,20 @@ def render(morning, seed, model_name, command):
     names = [data.PEOPLE[p]["name"] for p in data.ORDER]
     w("| | " + " | ".join(names) + " |")
     w("|---|" + "---|" * len(names))
+
+    def knows(p):
+        pid = next(q for q in data.ORDER if data.PEOPLE[q] is p)
+        if pid == culprit:
+            return "ate it in the night; nobody saw"
+        note = data.about_the_can(morning.scenario, pid)
+        return "only that it is missing" + (f"; told: {quoted(note)}" if note else "")
     rows = [
         ("Age", lambda p: str(p["age"])),
         ("Role in the family", lambda p: p["role_short"]),
         ("Where, how hungry", lambda p: f"kitchen, hunger {p['hunger']:.2f} ({hunger_words(p['hunger'])})"),
         ("Temperament", lambda p: trait_words(p["traits"])),
         ("What matters to them", lambda p: ", ".join(p["values"])),
-        ("Knows about the can", lambda p: "ate it in the night; nobody saw" if culprit and p is data.PEOPLE[culprit]
-         else "only that it is missing"),
+        ("Knows about the can", knows),
     ]
     for label, f in rows:
         w(f"| {label} | " + " | ".join(f(data.PEOPLE[p]) for p in data.ORDER) + " |")
diff --git a/Prototypes/llm-morning/v6/check.py b/Prototypes/llm-morning/v6/check.py
new file mode 100644
index 0000000..67f8b82
--- /dev/null
+++ b/Prototypes/llm-morning/v6/check.py
@@ -0,0 +1,55 @@
+"""Replays the six sixth-version mornings from their cache and checks their stories.
+
+    python v6/check.py
+
+v6/ is a frozen copy of the code that made the runs reports/baseline_v6.md and
+reports/witness_v6.md describe (daniel_ate_it, and daniel_ate_it_leo_heard). Replaying makes
+no API calls. Each replayed story must come out byte for byte as
+runs/v6/<name>.md, and its transcript as the one saved beside it.
+"""
+import json
+import os
+import sys
+
+HERE = os.path.dirname(os.path.abspath(__file__))
+ROOT = os.path.dirname(HERE)
+sys.path.insert(0, HERE)
+
+from gemini import Cache, Oracle             # noqa: E402  (v6's own modules)
+from story import render                     # noqa: E402
+from world import Morning                    # noqa: E402
+
+# (scenario, model key, model name, seeds), as the runs in runs/v6 were made.
+RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3)),
+        ("daniel_ate_it_leo_heard", None, "gemini-3.5-flash-lite", (1, 2, 3))]
+
+
+def main():
+    ok = True
+    for scenario, key, model, seeds in RUNS:
+        for seed in seeds:
+            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
+            cache = Cache(os.path.join(ROOT, "cache", "v6", f"{model}-{name}.json"))
+            oracle = Oracle(cache, model, seed, client=None, replay=True)
+            morning = Morning(oracle, seed, scenario)
+            for t in range(morning.turns):
+                morning.turn(t)
+            morning.finish()
+            command = ("python morning.py"
+                       + (f" --scenario {scenario}" if scenario != "daniel_ate_it" else "")
+                       + (f" --model {key}" if key else "") + f" --seed {seed}")
+            text = render(morning, seed, model, command)
+            base = os.path.join(ROOT, "runs", "v6", name)
+            with open(base + ".md", "rb") as f:
+                same_story = f.read() == text.encode("utf-8")
+            with open(base + ".transcript.json", encoding="utf-8") as f:
+                same_transcript = json.load(f) == json.loads(json.dumps(morning.transcript))
+            ok &= same_story and same_transcript
+            print(f"{name}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
+                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
+                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
+    return 0 if ok else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 69e9bac..774b12b 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -33,7 +33,8 @@ SYSTEM = (
     "doing it, or null. `feeling` names what they feel right now in one or two words. "
     "`reason` is their reason in one sentence, as they would think it. `suspects` is who they "
     "now believe took the can, and `angry_at` is who they are angry with right now: each is "
-    'one of "Daniel", "Elena", "Leo", "Mara" or "nobody". Reply with JSON only: '
+    'one of "Daniel", "Elena", "Leo", "Mara" or "nobody". `thought` is what goes through their '
+    "mind first, in two or three sentences, before they choose. Reply with JSON only: "
     '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
     '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
 )
@@ -210,6 +211,7 @@ class Person:
         self.aside_lead = None      # whom they took aside last turn, if the other came
         self.searched = set()
         self.knows_culprit = culprit if pid == culprit else None
+        self.can_note = data.about_the_can(scenario, pid)  # what else they know of the night, if anything
         self.confession_heard_at = None     # minute they first heard the culprit admit it
         self.heard_question = False
         self.confessed = False
@@ -430,16 +432,17 @@ class Morning:
         s = p.suspicion
         # What they know about the can wins over what their answers guessed.
         if p.knows_culprit == p.id:
-            out.append("About the can: you ate it yourself.")
+            about = "About the can: you ate it yourself."
         elif p.knows_culprit:
-            out.append(f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
-                       f"{p.confession_heard_at:02d}.")
+            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
+                     f"{p.confession_heard_at:02d}.")
         elif s.strength:
-            out.append(f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
-                       f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
-                       f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
+            about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
+                     f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
+                     f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
         else:
-            out.append("About the can: you have not settled on who took it.")
+            about = "About the can: you have not settled on who took it."
+        out.append(f"{about} {p.can_note}" if p.can_note else about)
         held = [(t, p.grudges[t]) for t in data.ORDER if t in p.grudges and p.grudges[t].strength]
         if not held:
             out.append("Against the others: nothing.")
@@ -558,7 +561,7 @@ class Morning:
             return None, "not JSON"
         if not isinstance(ans, dict):
             return None, "not a JSON object"
-        for field in ("option", "feeling", "reason"):
+        for field in ("thought", "option", "feeling", "reason"):
             if not isinstance(ans.get(field), str) or not ans[field].strip():
                 return None, f"no `{field}`"
         if "say" not in ans or not (ans["say"] is None or isinstance(ans["say"], str)):
@@ -583,7 +586,8 @@ class Morning:
         if opt.id == "silent" and say:
             say, dropped = None, True
         return {"option": opt.id, "say": say, "feeling": " ".join(ans["feeling"].split()).lower(),
-                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped, **named}, None
+                "thought": " ".join(ans["thought"].split()), "reason": " ".join(ans["reason"].split()),
+                "dropped_line": dropped, **named}, None
 
     # ---------- one turn ----------
     def run(self):
@@ -666,7 +670,8 @@ class Morning:
                      "words": d.get("say"), "audience": audience, "mode": d["mode"],
                      "decided_at": [minute, d["seq"]], "said_at": [minute, d["seq"]],
                      "came_of_it": d["came_of_it"], "new": d.get("new"), "new_why": d.get("new_why"),
-                     "inner": d.get("inner_families"), "suspects": d.get("suspects"),
+                     "inner": d.get("inner_families"), "thought": d.get("thought"),
+                     "suspects": d.get("suspects"),
                      "angry_at": d.get("angry_at"),
                      "moved_to": opt.act["to"] if opt.act["kind"] in ("go", "accept_aside") else None}
             tturn["acts"].append(entry)
```

## 8. The budget effect

**What was measured.** Each v6 run was replayed through v6/ (0 API calls), and every prompt it
sends was captured.
- Each prompt was measured as `estimate_tokens(new SYSTEM + prompt)`.
- For Leo's witness prompts, the prompt was first given variant B's move: the heard line out,
  the note on "About the can".

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/budget.py < /dev/null
estimate_tokens(SYSTEM): v6 254, now 281; budget 1400
daniel_ate_it-seed1: 45 prompts; over 1400 with the new SYSTEM: 36; minute 00: Daniel 1394->1421, Leo 1319->1346, Elena 1355->1382, Mara 1383->1409
daniel_ate_it-seed2: 66 prompts; over 1400 with the new SYSTEM: 52; minute 00: Elena 1364->1391, Mara 1399->1426, Daniel 1372->1399, Leo 1360->1387
daniel_ate_it-seed3: 25 prompts; over 1400 with the new SYSTEM: 17; minute 00: Mara 1373->1400, Elena 1386->1412, Daniel 1371->1398, Leo 1361->1388
daniel_ate_it_leo_heard-seed1: 44 prompts; over 1400 with the new SYSTEM: 28; minute 00: Daniel 1394->1421, Leo 1356->1370, Elena 1355->1382, Mara 1383->1409
daniel_ate_it_leo_heard-seed2: 43 prompts; over 1400 with the new SYSTEM: 30; minute 00: Elena 1364->1391, Mara 1399->1426, Daniel 1372->1399, Leo 1397->1411
daniel_ate_it_leo_heard-seed3: 29 prompts; over 1400 with the new SYSTEM: 20; minute 00: Mara 1373->1400, Elena 1386->1412, Daniel 1371->1398, Leo 1398->1412
exit=0
```

- **Over 1400 means one more cut.** A prompt over the budget, rebuilt by the new code, would
  lose one more item before it is sent: an older memory entry, or else a backstory line.
- **How often.** 183 of the 252 prompts are over.
- **The same prompts were already near the limit.** In v6 they had already been cut before
  sending.
- **At minute 00 the cut takes a backstory line.** Morning memory is empty then, so the first
  cut removes the oldest backstory line, "Day 1: Daniel boards the front windows…", and adds the
  marker (world.py:530-548).
  - **Both scenarios, the same way:** Daniel in seed 1 (1421), Mara in seeds 1 and 2 (1409,
    1426), Elena in seed 3 (1412). These cuts do not separate the scenarios.
  - **The witness scenario only:** Leo in seeds 2 and 3 (1411, 1412). In daniel_ate_it his
    prompts are 1387 and 1388 and keep the line.
- **What the numbers assume.** They take the v6 turn order and the v6 lines said before each
  person. A new run's answers will differ, so these are the v6 conditions, not a forecast.

**The fresh minute-00 prompts T3 compares**, with the new code (nobody has acted yet):

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -c "<builds a fresh Morning per scenario and seed; prints estimate_tokens(SYSTEM + prompt_for(p, 0, options_for(p))) per person>"
daniel_ate_it 1 {'Daniel': 1369, 'Elena': 1391, 'Leo': 1351, 'Mara': 1400}
daniel_ate_it 2 {'Daniel': 1369, 'Elena': 1391, 'Leo': 1351, 'Mara': 1400}
daniel_ate_it 3 {'Daniel': 1369, 'Elena': 1391, 'Leo': 1351, 'Mara': 1400}
daniel_ate_it_leo_heard 1 {'Daniel': 1369, 'Elena': 1391, 'Leo': 1374, 'Mara': 1400}
daniel_ate_it_leo_heard 2 {'Daniel': 1369, 'Elena': 1391, 'Leo': 1374, 'Mara': 1400}
daniel_ate_it_leo_heard 3 {'Daniel': 1369, 'Elena': 1391, 'Leo': 1374, 'Mara': 1400}
```

- **All are at or under 1400, so none is cut.**
- **Mara's first prompt is exactly at the budget.**

## 9. Scripts used (scratchpad, not in the repository)

**fake_extract.py**

```python
"""Read-only: one Leo transcript entry and its story line from the fake run, and Leo's
"About the can" lines in that run's prompts."""
import json

RUN = "runs/v7/fake/daniel_ate_it_leo_heard-seed1"
tr = json.load(open(RUN + ".transcript.json", encoding="utf-8"))
acts = [a for t in tr["turns"] for a in t["acts"] if a["who"] == "leo" and a["mode"] == "model"]
print("transcript entry (first model act of Leo's):")
print(json.dumps(acts[0], ensure_ascii=False))
story = open(RUN + ".md", encoding="utf-8").read().splitlines()
print("story line:")
print(next(x for x in story if x.startswith("- **Leo**") and "Thought: “Fake thought 3.”" in x))
print("story, cast table:")
print(next(x for x in story if x.startswith("| Knows about the can")))
c = json.load(open("cache/v7/fake-daniel_ate_it_leo_heard-seed1.json", encoding="utf-8"))
prompts = [e["prompt"] for e in c.values()]
leo = [p for p in prompts if p.startswith("You are Leo,")]
print(f"{len(prompts)} prompts, {len(leo)} of them Leo's; distinct 'About the can' lines in Leo's:")
for x in sorted({x for p in leo for x in p.splitlines() if x.startswith("About the can")}):
    print("  " + x)
print("prompts holding 'Fake thought':", sum("Fake thought" in p for p in prompts))
print("answers holding a thought:", sum('"thought": "Fake thought' in e["response"] for e in c.values()),
      "of", len(c))
```

**budget.py**

```python
"""Read-only: the v6 runs' own prompts (replayed through v6/, 0 API calls), measured against the
new SYSTEM with world.py's estimate and budget. Leo's witness prompts get the move of variant B."""
import importlib.util
import os
import sys

ROOT = "C:/Users/Akrem/Desktop/Projects/Fallow/Prototypes/llm-morning"
sys.path.insert(0, ROOT + "/v6")
from gemini import Cache, Oracle          # noqa: E402  v6's
from world import Morning, SYSTEM as OLD, estimate_tokens, PROMPT_TOKEN_BUDGET  # noqa: E402

src = open(ROOT + "/world.py", encoding="utf-8").read()
start = src.index("SYSTEM = (")
ns = {}
exec(src[start:src.index("\n)\n", start) + 3], ns)
NEW = ns["SYSTEM"]
HEARD = ("- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. "
         "He does not get up and does not see who. (you heard it)")
NOTE = " Last night you woke and heard someone in the kitchen open a can; you did not see who."
print(f"estimate_tokens(SYSTEM): v6 {estimate_tokens(OLD)}, now {estimate_tokens(NEW)}; "
      f"budget {PROMPT_TOKEN_BUDGET}")

for scenario in ("daniel_ate_it", "daniel_ate_it_leo_heard"):
    for seed in (1, 2, 3):
        name = f"{scenario}-seed{seed}"
        oracle = Oracle(Cache(f"{ROOT}/cache/v6/gemini-3.5-flash-lite-{name}.json"),
                        "gemini-3.5-flash-lite", seed, client=None, replay=True)
        asked = []
        ask = oracle.ask
        oracle.ask = lambda system, prompt: (asked.append(prompt), ask(system, prompt))[1]
        m = Morning(oracle, seed, scenario)
        for t in range(m.turns):
            m.turn(t)
        over, m0 = 0, []
        for p in asked:
            b = p
            if HEARD in p.split("\n"):
                lines = p.split("\n")
                lines.remove(HEARD)
                i = next(i for i, x in enumerate(lines) if x.startswith("About the can"))
                lines[i] += NOTE
                b = "\n".join(lines)
            new = estimate_tokens(NEW + b)
            over += new > PROMPT_TOKEN_BUDGET
            if "Now, minute 00," in p:
                m0.append(f"{p.split(',')[0][8:]} {estimate_tokens(OLD + p)}->{new}")
        print(f"{name}: {len(asked)} prompts; over {PROMPT_TOKEN_BUDGET} with the new SYSTEM: {over}; "
              f"minute 00: " + ", ".join(m0))
```
