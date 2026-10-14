# No thought field; Leo's night line as a conclusion he holds

Mode: implement. No API was called and no morning was run against the model.
- **Runs made.** The only mornings were the fake-model mornings inside the tests, and replays
  from saved caches (0 requests).
- **Paths.** They are relative to `Prototypes/llm-morning/`.

**Commit: `fd2583b`** (`fd2583b9fa82610ec5969593375414d78151157f`, "LLM morning: no thought
field; Leo's night line says what follows from it").
- **A commit before it.** `abf031e` committed the v7 runs, their caches and
  reports/witness_v7.md, which were untracked. Without it git status would not be clean. This
  follows `fa54a48` (the v6 witness runs) and `d2e7f99` (before the thought-field change).
- **This report** is committed after the change, so that it can name the commit.

## Result

| Done when | Result |
|---|---|
| The new tests fail before the change | **22 fail** (20 FAIL, 2 ERROR). Each fails because the thought field is still required or the note is still v7's (§3). |
| ... and pass after | **69 of 69 pass** (§4) |
| The full suite passes | **OK**, 69 tests: 71 before, less the 9 thought-field tests, plus 7 new (§2) |
| The v6 replay is identical with 0 requests | **3 of 3 IDENTICAL**, `api_requests: 0`, `answers_live: 0`, story hashes as in baseline_v6.md (§5) |
| Leo's minute-00 prompt loses no line | **Yes**, in seeds 1–3 paired with the v6 answers and in a fresh morning: 1356, 1397, 1398 and 1361 of 1400 (§6) |
| git status is clean apart from the three old replay.md files | **Yes** (§8) |

**Something to know: the budget margin is thin in seeds 2 and 3.**
- **Where it is thin.** Paired with the v6 answers, Leo acts last at minute 00 in seeds 2 and 3.
  His witness prompt then has only **11 and 7 characters to spare** under the 1,400-token budget.
- **What would push it over.** The margin depends on the minute-00 lines the others say before
  him. In a new baseline those lines could be longer than v6's.
  - If they are longer by more than the margin, the first cut drops Leo's oldest backstory line
    ("Day 1: Daniel boards the front windows…") and adds "- (earlier things, left out here)".
  - The same happened in witness_v7 seeds 2 and 3 (its R5).
- **What was not changed.** Nothing, because the brief keeps the budget and the text as they
  are. T9 checks the v6 condition only.

**The note stays on every form of the line.** As in v7, the sentence is added at the end of
whichever "About the can:" line Leo gets (world.py `inside_lines`), not only the unsettled form
the brief quotes. For example, after a confession:

    About the can: Daniel admitted taking it at minute 18. Last night you woke and heard someone open a can in the kitchen, so someone in this house took it in the night. You did not see who.

T5 pins the three forms.

---

## 1. What changed

**0. v7/ freeze** (the same way v6/ was frozen in 177e300).
- **The copies.** v7/ holds copies of data, gemini, metrics, metrics3, metrics4, metrics5,
  morning, story, talk and world. Each is byte-identical to 427868b, the code that made the v7
  runs (§5).
- **v7/check.py** is v6/check.py with v7 put in place of v6: the docstring, the cache and runs
  folders, and the comment. Its `RUNS` list is the same six runs (§7).
- **New runs default to v8** (morning.py docstring, `run(out="v8")`, `--out` default).
  .gitignore ignores `runs/v8/fake/` and `cache/v8/fake-*`.

**1. The decision format is v6's again.**
- **gemini.py** is v6/gemini.py again, byte for byte:
  - `RESPONSE_SCHEMA` has no `thought` and no `property_ordering`;
  - `FakeClient` answers without a thought.
- **world.py:**
  - `SYSTEM` loses the `thought` sentence, so it is v6's again;
  - `Morning.parse` no longer requires or keeps a `thought`;
  - transcript entries have no `thought` key.
- **story.py:**
  - the decision line is `… Feeling: *…*. Reason: “…” …` again;
  - the "Chose" legend is v6's.
- **What stays against v6.** Only the witness code: `Person.can_note` and its use in
  `inside_lines` (world.py), and the cast table's "Knows about the can" cell (story.py). The full
  difference is in §5.

**2. The belief line** (daniel_ate_it_leo_heard only).
- **data.py.** `about_the_can["leo"]` is now: "Last night you woke and heard someone open a can in
  the kitchen, so someone in this house took it in the night. You did not see who." (132
  characters)
- **What Leo's minute-00 line reads**, with the existing "About the can: you have not settled on
  who took it.":

  > About the can: you have not settled on who took it. Last night you woke and heard someone open a can in the kitchen, so someone in this house took it in the night. You did not see who.

  This is exactly the brief's line (T1 checks it).
- **The data comment** now says why the conclusion is given.
- **No other prompt text, option, rule or config changed.**

**3. The token budget.** See §6.

## 2. Tests (written first)

**Removed: `ThoughtFieldTest` (9 tests)**, together with its schema and sentence constants. Its
tests required the field that this change removes.

**New class `DecisionFormatTest`: 6 tests.** `frozen(version, module)` loads a vN/ module on
its own.

| Test | Checks |
|---|---|
| `test_the_schema_is_v6s` | `RESPONSE_SCHEMA` equals v6/gemini.py's; no "thought" in it |
| `test_the_system_instruction_is_v6s` | `SYSTEM` equals v6/world.py's; no "thought" in it |
| `test_the_parser_is_v6s` | `Morning.parse` gives the same result as v6's `Morning.parse` for 11 answers. They include one without a thought, one with a thought, one with an empty thought, a missing reason, a line said while silent, speech without words, an option not offered, a bad `suspects`, not JSON, not an object, and a fenced answer. |
| `test_the_fake_client_answers_as_v6s` | 12 answers from `FakeClient` equal v6's `FakeClient`, broken ones included |
| `test_the_story_and_the_transcript_carry_no_thought` | a fake morning: no "Thought:" in the story; its "Chose" legend equals runs/v6's; its transcript acts have exactly the keys of a runs/v6 transcript |
| `test_the_v6_baseline_replays_byte_for_byte_with_no_requests` | runs/v6 daniel_ate_it seeds 1–3, replayed by the current code from a copy of cache/v6: the story bytes equal runs/v6/…md, the transcript equals the saved one, `api_requests` 0 and `live` 0 |

**T1 to T8 (`WitnessScenarioTest`), updated.**
- **Constants.** NOTE is the new sentence and BELIEF_LINE is the brief's whole line. OLD_NOTE is
  v7's sentence and HEARD is v6's.

| # | Now checks |
|---|---|
| T1 | `about_the_can(WITNESS, "leo")` is NOTE; `CAN_LINE + " " + NOTE` is the brief's line; NOTE has no family name; its capitalised words are "Last" and "You"; no "eats a can" |
| T2 | as before, and no backstory line holds NOTE |
| T3 | minute 00, seeds 1–3: Daniel, Elena and Mara prompts equal; Leo's `sure` and options equal; his diff is `- ` CAN_LINE / `+ ` BELIEF_LINE |
| T4 | no Daniel prompt holds NOTE, OLD_NOTE, HEARD, "woke and heard", "wakes and hears", "open a can", "did not see who", "does not see who", "heard someone" or **"someone in this house took it"**; the conscience line still says "and nobody saw" |
| T5 | as before (NOTE ends Leo's one "About the can" line, after one of the three rules-made forms; no other prompt holds it; "open a can" nowhere outside it), and **no prompt holds OLD_NOTE** |
| T6 | unchanged |
| T7 | unchanged (NOTE is the new sentence) |
| T8 | unchanged (the cast row quotes NOTE, the new sentence) |

**New: T9, `test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers`.**
- **What it runs.** For seeds 1–3, the current code runs minute 00 of both scenarios with a
  `PairedOracle`.
- **What `PairedOracle` does.** It answers from cache/v6's daniel_ate_it cache whenever the prompt
  is the same, as a witness run paired with a baseline would (design §4, R3). Any other prompt
  gets a silent answer and is recorded.
- **What it checks:**
  - the daniel_ate_it morning is answered from the cache throughout;
  - Leo's two prompts differ only by `- ` CAN_LINE / `+ ` BELIEF_LINE;
  - the witness prompt has no "(earlier things, left out here)";
  - `estimate_tokens(SYSTEM + prompt)` is within `PROMPT_TOKEN_BUDGET`.

**Test helpers restored to v6's format.**
- The scripted client `Scripted` answers without a `thought`.
- `StubApi` no longer keeps the config it was sent, which only the removed schema-order test read.

**Diff of test_morning.py** (`git diff fd2583b^ fd2583b -- test_morning.py`):

```diff
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 229fb3d..6409409 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -18,7 +18,9 @@ import metrics
 import gemini
 from gemini import Cache, FakeClient, GeminiClient, Oracle
 from morning import run
-from world import QUIET_TURNS, SYSTEM, Grudge, Morning, Option, Person, Track, estimate_tokens
+from story import render
+from world import (PROMPT_TOKEN_BUDGET, QUIET_TURNS, SYSTEM, Grudge, Morning, Option, Person, Track,
+                   estimate_tokens)
 
 # What the third version's prompts said about guilt, suspicion and grudges: verdicts, which
 # the prompts must no longer contain.
@@ -136,7 +138,6 @@ class StubApi:
 
     def generate_content(self, model, contents, config):
         self.calls += 1
-        self.config = config
         step = self.script.pop(0) if self.script else "ok"
         if isinstance(step, Exception):
             raise step
@@ -309,9 +310,8 @@ class Scripted:
         option, say = answer[:2]
         suspects, angry_at = answer[2:] if len(answer) == 4 else ("nobody", "nobody")
         self.asked.append((minute, who))
-        return json.dumps({"thought": f"Scripted thought {self.requests}.", "option": option, "say": say,
-                           "feeling": "tense", "reason": "Scripted.", "suspects": suspects,
-                           "angry_at": angry_at})
+        return json.dumps({"option": option, "say": say, "feeling": "tense", "reason": "Scripted.",
+                           "suspects": suspects, "angry_at": angry_at})
 
 
 def scripted(policy, dirs, seed=1, turns=None):
@@ -912,145 +912,135 @@ class PromptTruthTest(unittest.TestCase):
                 self.assertNotIn("A can that should be on the shelf is not", prompt, (scenario, pid))
 
 
-THOUGHT_SENTENCE = ("`thought` is what goes through their mind first, in two or three sentences, before "
-                    "they choose. ")
-FIELDS = ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"]
-# Variant C of reports/witness_probe2.md, section 3.
-THOUGHT_SCHEMA = {
-    "type": "object",
-    "properties": {
-        "thought": {"type": "string"},
-        "option": {"type": "string"},
-        "say": {"type": "string", "nullable": True},
-        "feeling": {"type": "string"},
-        "reason": {"type": "string"},
-        "suspects": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
-        "angry_at": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
-    },
-    "required": FIELDS,
-    "property_ordering": FIELDS,
-}
-
-
-def frozen_world(version):
-    """vN/world.py, loaded on its own (its SYSTEM is what vN sent)."""
-    spec = importlib.util.spec_from_file_location(f"{version}_world", os.path.join(HERE, version, "world.py"))
-    module = importlib.util.module_from_spec(spec)
-    spec.loader.exec_module(module)
-    return module
-
-
-class ThoughtFieldTest(unittest.TestCase):
-    """Every model decision carries a `thought`, written first (reports/witness_probe2.md,
-    variant C). It is kept and told in the story, and never shown in a prompt."""
+def frozen(version, module):
+    """vN/<module>.py, loaded on its own (what vN ran)."""
+    spec = importlib.util.spec_from_file_location(f"{version}_{module}",
+                                                  os.path.join(HERE, version, f"{module}.py"))
+    loaded = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(loaded)
+    return loaded
+
+
+V6_RUNS = os.path.join(HERE, "runs", "v6")
+V6_CACHE = os.path.join(HERE, "cache", "v6")
+V6_MODEL = "gemini-3.5-flash-lite"
+
+
+class DecisionFormatTest(unittest.TestCase):
+    """The decision format is v6's again (reports/belief_line_impl.md): no `thought` in the
+    schema, the system instruction, the parser, the fake answers, the story or the transcript."""
 
     def setUp(self):
         self.dirs = Dirs()
+        self.v6_world, self.v6_gemini = frozen("v6", "world"), frozen("v6", "gemini")
 
     def tearDown(self):
         self.dirs.cleanup()
 
-    def answer(self, **over):
-        ans = {"thought": "  Someone   took it.\nI wonder who. ", "option": "silent", "say": None,
-               "feeling": "tense", "reason": "I wait.", "suspects": "nobody", "angry_at": "nobody"}
-        ans.update(over)
-        return json.dumps({k: v for k, v in ans.items() if v is not ...})
-
-    def test_the_schema_asks_for_a_thought_first(self):
-        self.assertEqual(gemini.RESPONSE_SCHEMA, THOUGHT_SCHEMA)
-        self.assertEqual(list(gemini.RESPONSE_SCHEMA["properties"])[0], "thought")
-
-    def test_the_client_sends_the_schema_with_its_order(self):
-        old = os.environ.get("GEMINI_API_KEY")
-        os.environ["GEMINI_API_KEY"] = SECRET
-        try:
-            api = StubApi([])
-            GeminiClient(gemini.load_config(CONFIG), 1, api=api, sleep=lambda s: None,
-                         clock=lambda: 0.0).generate(SYSTEM, "- silent: stay put")
-        finally:
-            if old is None:
-                os.environ.pop("GEMINI_API_KEY", None)
-            else:
-                os.environ["GEMINI_API_KEY"] = old
-        schema = api.config.response_schema
-        ordering = schema["property_ordering"] if isinstance(schema, dict) else schema.property_ordering
-        self.assertEqual(ordering, FIELDS)
-
-    def test_the_system_instruction_adds_one_sentence_before_the_reply_line(self):
-        old = frozen_world("v6").SYSTEM
-        self.assertEqual(old.count("Reply with JSON only"), 1)
-        self.assertEqual(SYSTEM, old.replace("Reply with JSON only", THOUGHT_SENTENCE + "Reply with JSON only"))
-        # The JSON example at its end is unchanged: it does not list `thought`.
-        self.assertEqual(SYSTEM.split("Reply with JSON only")[1], old.split("Reply with JSON only")[1])
-        self.assertNotIn("thought", SYSTEM.split("Reply with JSON only")[1])
-
-    def test_the_parser_keeps_the_thought(self):
-        opts = [Option("silent", "stay put", kind="silent")]
-        choice, why = Morning.parse(self.answer(), opts)
-        self.assertIsNone(why)
-        self.assertEqual(choice["thought"], "Someone took it. I wonder who.")
-
-    def test_the_parser_refuses_an_answer_without_a_thought(self):
-        opts = [Option("silent", "stay put", kind="silent")]
-        for bad in (..., "", "   ", None, 3, ["a"]):
-            self.assertEqual(Morning.parse(self.answer(thought=bad), opts), (None, "no `thought`"), bad)
-
-    def test_the_fake_client_gives_a_thought_first(self):
-        text = FakeClient(invalid_every=0).generate("", "Your options:\n- silent: stay put")
-        ans = json.loads(text)
-        self.assertEqual(list(ans)[0], "thought")
-        self.assertTrue(isinstance(ans["thought"], str) and ans["thought"].strip())
-
-    def test_the_decision_and_the_transcript_keep_the_thought(self):
-        m, client = scripted(lambda who, minute, options, c: ("silent", None), self.dirs, turns=3)
-        model = [d for rec in m.log for d in rec["decisions"] if d["mode"] == "model"]
-        self.assertTrue(model)
-        thoughts = [d["thought"] for d in model]
-        self.assertEqual(sorted(thoughts), sorted(f"Scripted thought {i}." for i in range(1, client.requests + 1)))
-        acts = [a for tt in m.transcript["turns"] for a in tt["acts"]]
-        self.assertEqual([a["thought"] for a in acts if a["mode"] == "model"], thoughts)
-        self.assertEqual({a["thought"] for a in acts if a["mode"] != "model"}, {None})
-
-    def test_no_prompt_shows_a_thought(self):
-        (meta, code), out = fake_morning(self.dirs, seed=1)
-        self.assertEqual(code, 0, out)
-        entries = [e for name in os.listdir(self.dirs.cache)
-                   for e in json.loads(read(os.path.join(self.dirs.cache, name))).values()]
-        thoughts = [json.loads(e["response"])["thought"] for e in entries
-                    if e["response"].startswith("{") and "thought" in json.loads(e["response"])]
-        self.assertTrue(thoughts)
-        for e in entries:
-            self.assertNotIn("Fake thought", e["prompt"])
-            for t in thoughts:
-                self.assertNotIn(t, e["prompt"])
-        m, client = scripted(lambda who, minute, options, c: ("silent", None), self.dirs, turns=6)
-        self.assertTrue(client.prompts)
-        for _, _, prompt in client.prompts:
-            self.assertNotIn("Scripted thought", prompt)
-
-    def test_the_story_tells_the_thought_next_to_the_reason(self):
+    def test_the_schema_is_v6s(self):
+        self.assertEqual(gemini.RESPONSE_SCHEMA, self.v6_gemini.RESPONSE_SCHEMA)
+        self.assertNotIn("thought", json.dumps(gemini.RESPONSE_SCHEMA))
+
+    def test_the_system_instruction_is_v6s(self):
+        self.assertEqual(SYSTEM, self.v6_world.SYSTEM)
+        self.assertNotIn("thought", SYSTEM)
+
+    def test_the_parser_is_v6s(self):
+        base = {"option": "deny", "say": " I  did not. ", "feeling": " Tense ", "reason": "I  wait.",
+                "suspects": "leo", "angry_at": "nobody"}
+        answers = [base, {**base, "thought": "Someone took it."}, {**base, "thought": ""},
+                   {k: v for k, v in base.items() if k != "reason"}, {**base, "option": "silent"},
+                   {**base, "say": None}, {**base, "option": "fly"}, {**base, "suspects": "the dog"}]
+        texts = ([json.dumps(a) for a in answers]
+                 + ["not json", "[1]", "```json\n" + json.dumps(base) + "\n```"])
+
+        def opts(option):
+            return [option("silent", "stay put", kind="silent"), option("deny", "deny taking it", True, kind="deny")]
+        for text in texts:
+            self.assertEqual(Morning.parse(text, opts(Option)),
+                             self.v6_world.Morning.parse(text, opts(self.v6_world.Option)), text)
+
+    def test_the_fake_client_answers_as_v6s(self):
+        now, then = FakeClient(), self.v6_gemini.FakeClient()
+        for i in range(12):
+            prompt = f"Your options:\n- silent: stay put\n- deny: (speech) deny taking it\n- search: look\n{i}"
+            self.assertEqual(now.generate("", prompt), then.generate("", prompt), i)
+
+    def test_the_story_and_the_transcript_carry_no_thought(self):
         (meta, code), out = fake_morning(self.dirs, seed=1)
         self.assertEqual(code, 0, out)
         story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
-        pairs = re.findall(r"Thought: “Fake thought (\d+)\.” Reason: “Fake reason (\d+)\.”", story)
-        self.assertEqual(len(pairs), meta["model_decisions"])
-        self.assertTrue(all(a == b for a, b in pairs))
-        self.assertEqual(story.count("Reason: “"), meta["model_decisions"])
+        self.assertNotIn("Thought:", story)
+
+        def legend(text):
+            return next(x for x in text.splitlines() if x.startswith("- **Chose**"))
+        self.assertEqual(legend(story), legend(read(os.path.join(V6_RUNS, "daniel_ate_it-seed1.md"))))
+
+        def keys(path):
+            tr = json.loads(read(path))
+            return {k for turn in tr["turns"] for a in turn["acts"] for k in a}
+        self.assertEqual(keys(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")),
+                         keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")))
+
+    def test_the_v6_baseline_replays_byte_for_byte_with_no_requests(self):
+        for seed in (1, 2, 3):
+            name = f"daniel_ate_it-seed{seed}"
+            path = os.path.join(self.dirs.root, f"{name}.json")
+            shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
+            oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
+            m = Morning(oracle, seed)
+            try:
+                for t in range(m.turns):
+                    m.turn(t)
+            except gemini.StopMorning as stop:
+                self.fail(f"seed {seed}: {stop}")
+            m.finish()
+            text = render(m, seed, V6_MODEL, f"python morning.py --seed {seed}")
+            self.assertTrue(text.encode("utf-8") == read(os.path.join(V6_RUNS, name + ".md"), "rb"),
+                            f"seed {seed}: the story differs from runs/v6/{name}.md")
+            self.assertTrue(json.loads(json.dumps(m.transcript))
+                            == json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json"))),
+                            f"seed {seed}: the transcript differs")
+            self.assertEqual((oracle.api_requests, oracle.live), (0, 0), seed)
+
+
+class PairedOracle:
+    """Answers from a saved cache when the prompt is the same as there, as a run paired with it
+    would; keeps every prompt, and gives each one it cannot answer a silent answer."""
+
+    def __init__(self, path, model, seed):
+        self.entries = json.loads(read(path))
+        self.model, self.seed = model, seed
+        self.asked, self.missed = [], []
+
+    def ask(self, system, prompt):
+        self.asked.append(prompt)
+        entry = self.entries.get(Cache.key(self.model, self.seed, system, prompt))
+        if entry:
+            return entry["response"]
+        self.missed.append(prompt)
+        return json.dumps({"option": "silent", "say": None, "feeling": "calm", "reason": "Waiting.",
+                           "suspects": "nobody", "angry_at": "nobody"})
 
 
 WITNESS = "daniel_ate_it_leo_heard"
-# Where the line was until v6: a backstory event of Leo's (reports/witness_design.md, section 1).
+# Where the line was in v6: a backstory event of Leo's (reports/witness_design.md, section 1).
 HEARD = ("In the night Leo wakes and hears someone in the kitchen open a can. "
          "He does not get up and does not see who.")
-# Where it is now: appended to Leo's "About the can:" line (reports/witness_probe.md, variant B).
-NOTE = "Last night you woke and heard someone in the kitchen open a can; you did not see who."
+# Where it was in v7: what he heard, at the end of his "About the can:" line (witness_probe.md, B).
+OLD_NOTE = "Last night you woke and heard someone in the kitchen open a can; you did not see who."
+# Now: what he heard and what follows from it, in the same place (reports/belief_line_impl.md).
+NOTE = ("Last night you woke and heard someone open a can in the kitchen, so someone in this house "
+        "took it in the night. You did not see who.")
 CAN_LINE = "About the can: you have not settled on who took it."
+BELIEF_LINE = ("About the can: you have not settled on who took it. Last night you woke and heard someone "
+               "open a can in the kitchen, so someone in this house took it in the night. You did not see who.")
 
 
 class WitnessScenarioTest(unittest.TestCase):
     """daniel_ate_it_leo_heard: daniel_ate_it, and Leo heard the night but did not see who
-    (reports/witness_design.md, sections 1 to 3). What he heard is told in his "About the can:"
-    line, not in his backstory."""
+    (reports/witness_design.md, sections 1 to 3). What he heard, and that it means someone in
+    the house took the can, is told in his "About the can:" line, not in his backstory."""
 
     def setUp(self):
         self.assertIn(WITNESS, data.SCENARIOS)
@@ -1074,9 +1064,10 @@ class WitnessScenarioTest(unittest.TestCase):
     # T1
     def test_the_sentence_names_nobody_leo_heard(self):
         self.assertEqual(data.about_the_can(WITNESS, "leo"), NOTE)
+        self.assertEqual(CAN_LINE + " " + NOTE, BELIEF_LINE)
         for name in ("Daniel", "Elena", "Leo", "Mara"):
             self.assertNotIn(name, NOTE)
-        self.assertEqual(set(re.findall(r"\b[A-Z]\w*", NOTE)), {"Last"})
+        self.assertEqual(set(re.findall(r"\b[A-Z]\w*", NOTE)), {"Last", "You"})
         self.assertNotIn("eats a can", NOTE)
 
     # T2
@@ -1084,7 +1075,8 @@ class WitnessScenarioTest(unittest.TestCase):
         for pid in data.ORDER:
             self.assertEqual(Person(pid, WITNESS).backstory, Person(pid, "daniel_ate_it").backstory, pid)
         self.assertEqual(data.backstory(WITNESS), data.backstory("daniel_ate_it"))
-        self.assertFalse([x for x in Person("leo", WITNESS).backstory if "Daniel eats" in x or HEARD in x])
+        self.assertFalse([x for x in Person("leo", WITNESS).backstory
+                          if "Daniel eats" in x or HEARD in x or NOTE in x])
 
     # T3
     def test_at_minute_00_only_leos_prompt_differs_by_his_can_line(self):
@@ -1100,7 +1092,7 @@ class WitnessScenarioTest(unittest.TestCase):
                     self.assertEqual(b, a, (seed, pid))
                     continue
                 diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
-                self.assertEqual([d for d in diff if d.startswith("+ ")], ["+ " + CAN_LINE + " " + NOTE], seed)
+                self.assertEqual([d for d in diff if d.startswith("+ ")], ["+ " + BELIEF_LINE], seed)
                 self.assertEqual([d for d in diff if d.startswith("- ")], ["- " + CAN_LINE], seed)
 
     # T4
@@ -1108,8 +1100,9 @@ class WitnessScenarioTest(unittest.TestCase):
         daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
         self.assertTrue(daniel)
         for p in daniel:
-            for words in (NOTE, HEARD, "woke and heard", "wakes and hears", "open a can", "did not see who",
-                          "does not see who", "heard someone"):
+            for words in (NOTE, OLD_NOTE, HEARD, "woke and heard", "wakes and hears", "open a can",
+                          "did not see who", "does not see who", "heard someone",
+                          "someone in this house took it"):
                 self.assertNotIn(words, p)
             if "On your conscience" in p:
                 self.assertIn("and nobody saw", p)
@@ -1122,6 +1115,7 @@ class WitnessScenarioTest(unittest.TestCase):
         self.assertTrue(leo)
         for p in prompts:
             self.assertNotIn(HEARD, p)
+            self.assertNotIn(OLD_NOTE, p)
             if p.startswith("You are Leo,"):
                 # The note ends his one "About the can" line, whatever that line says before it.
                 lines = [x for x in p.splitlines() if NOTE in x]
@@ -1166,6 +1160,27 @@ class WitnessScenarioTest(unittest.TestCase):
         self.assertIn("| Knows about the can | ate it in the night; nobody saw | only that it is missing | "
                       "only that it is missing | only that it is missing |", story)
 
+    # T9
+    def test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers(self):
+        """Paired with the v6 baseline answers, as a witness run would be (design §4, R3), Leo's
+        first prompt differs from his daniel_ate_it one by the can line alone and fits the budget."""
+        for seed in (1, 2, 3):
+            prompts = {}
+            for scenario in ("daniel_ate_it", WITNESS):
+                oracle = PairedOracle(os.path.join(V6_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"),
+                                      V6_MODEL, seed)
+                Morning(oracle, seed, scenario).turn(0)
+                if scenario == "daniel_ate_it":
+                    self.assertEqual(oracle.missed, [], seed)
+                leo = [p for p in oracle.asked if p.startswith("You are Leo,")]
+                self.assertEqual(len(leo), 1, (seed, scenario))
+                prompts[scenario] = leo[0]
+            old, new = prompts["daniel_ate_it"], prompts[WITNESS]
+            diff = [d for d in difflib.ndiff(old.splitlines(), new.splitlines()) if d[:2] in ("+ ", "- ")]
+            self.assertEqual(diff, ["- " + CAN_LINE, "+ " + BELIEF_LINE], seed)
+            self.assertNotIn("(earlier things, left out here)", new, seed)
+            self.assertLessEqual(estimate_tokens(SYSTEM + new), PROMPT_TOKEN_BUDGET, seed)
+
 
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
```

## 3. Test output before the change

The tests above were run against the unchanged code (427868b plus the new test file):

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest -v test_morning < /dev/null
```

The 22 failing tests, and the error line of each.
- **What is left out.** The 47 lines for passing tests and the tracebacks are not shown.
- **Long lines are cut.** Error lines over 300 characters stop at 300 and end with "…[cut here]".

```
ERROR: PressureTest.test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster
    KeyError: 'daniel'
ERROR: SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn
    KeyError: ''
FAIL: DecisionFormatTest.test_the_fake_client_answers_as_v6s
    : 0
FAIL: DecisionFormatTest.test_the_parser_is_v6s
    +  None) : {"option": "deny", "say": " I  did not. ", "feeling": " Tense ", "reason": "I  wait.", "suspects": "leo", "angry_at": "nobody"}
FAIL: DecisionFormatTest.test_the_schema_is_v6s
    Diff is 1485 characters long. Set self.maxDiff to None to see it.
FAIL: DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought
    AssertionError: 'Thought:' unexpectedly found in '# The morning as a story: daniel_ate_it, rules and a language model, seed 1\n\nGenerated by `python morning.py --seed 1 --fake` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person\'s memory, and lis …[cut here]
FAIL: DecisionFormatTest.test_the_system_instruction_is_v6s
    Diff is 2766 characters long. Set self.maxDiff to None to see it.
FAIL: DecisionFormatTest.test_the_v6_baseline_replays_byte_for_byte_with_no_requests
    AssertionError: seed 1: stopped: replay found a prompt with no cached answer, so this morning cannot be replayed from the cache.
FAIL: PressureTest.test_inner_moments_come_at_most_once_every_9_minutes
    AssertionError: False is not true : {'leo': [15], 'elena': [30], 'daniel': [33]}
FAIL: PressureTest.test_take_aside_accepted
    + ('brothers_room', 'brothers_room')
FAIL: PressureTest.test_take_aside_refused
    + refuse_aside
FAIL: PromptTruthTest.test_after_hearing_a_confession_a_guess_does_not_replace_it
    AssertionError: 0 != 3 : daniel
FAIL: PromptTruthTest.test_the_culprit_who_names_someone_else_is_still_told_they_ate_it
    + ('leo', 3)
FAIL: SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again
    + ['reassure_all', 'reassure_all', 'reassure_all']
FAIL: SequentialTalkTest.test_an_inner_moment_can_start_the_talk_again
    + eat
FAIL: SequentialTalkTest.test_the_one_just_accused_acts_next
    + mara
FAIL: WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_his_can_line
    +  'it in the night. You did not see who.'] : 1
FAIL: WitnessScenarioTest.test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers
    Diff is 17821 characters long. Set self.maxDiff to None to see it. : 1
FAIL: WitnessScenarioTest.test_no_prompt_says_who_leo_heard
    AssertionError: 'Last night you woke and heard someone in the kitchen open a can; you did not see who.' unexpectedly found in 'You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).\nHow you address them: Elena "Mom"; Daniel "Daniel"; Mara "Mara".\nWho …[cut here]
FAIL: WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence
    : ('daniel_ate_it_leo_heard', 'leo')
FAIL: WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard
    + Last night you woke and heard someone open a can in the kitchen, so someone in this house took it in the night. You did not see who.
FAIL: WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard
    AssertionError: '| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing; told: “Last night you woke and heard someone open a can in the kitchen, so someone in this house took it in the night. You did not see who.” | only that it is missing |' not  …[cut here]
```

```
----------------------------------------------------------------------
Ran 69 tests in 13.494s

FAILED (failures=20, errors=2)
exit=1
```

**Why each fails.**
- **12 are the new or changed tests**, each failing because the feature is missing:
  - 6 `DecisionFormatTest`: the schema, the SYSTEM text, the parser and the fake client differ
    from v6's; the story holds "Thought:"; the v6 replay hits a prompt with no cached answer.
  - 6 `WitnessScenarioTest`: T1, T3, T5, T7, T8 and T9 find v7's note, not the new one. T9 also
    finds that no v6 answer is reused, since the SYSTEM text differs.
- **The other 10 are older tests driven by `Scripted`:** 8 FAILs in `PressureTest` (3),
  `PromptTruthTest` (2) and `SequentialTalkTest` (3), and 2 ERRORs (a KeyError each, in
  `PressureTest` and `SequentialTalkTest`).
  - `Scripted` now answers in v6's format, without a thought.
  - The unchanged parser refuses those answers ("no `thought`"), so the rules decide instead and
    the scripted policy never takes effect.
  - They pass again once the parser is v6's.
- **Passing before the change.** T2, T4 and T6 of the witness tests. They hold for the old note
  as well.

## 4. Test output after the change

Run on the committed tree (`fd2583b`):

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m unittest -v test_morning < /dev/null
test_the_fake_client_answers_as_v6s (test_morning.DecisionFormatTest.test_the_fake_client_answers_as_v6s) ... ok
test_the_parser_is_v6s (test_morning.DecisionFormatTest.test_the_parser_is_v6s) ... ok
test_the_schema_is_v6s (test_morning.DecisionFormatTest.test_the_schema_is_v6s) ... ok
test_the_story_and_the_transcript_carry_no_thought (test_morning.DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought) ... ok
test_the_system_instruction_is_v6s (test_morning.DecisionFormatTest.test_the_system_instruction_is_v6s) ... ok
test_the_v6_baseline_replays_byte_for_byte_with_no_requests (test_morning.DecisionFormatTest.test_the_v6_baseline_replays_byte_for_byte_with_no_requests) ... ok
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
test_at_minute_00_only_leos_prompt_differs_by_his_can_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_his_can_line) ... ok
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... ok
test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers (test_morning.WitnessScenarioTest.test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers)
Paired with the v6 baseline answers, as a witness run would be (design §4, R3), Leo's ... ok
test_no_backstory_differs (test_morning.WitnessScenarioTest.test_no_backstory_differs) ... ok
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... ok
test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning) ... ok
test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence) ... ok
test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard) ... ok
test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard) ... ok

----------------------------------------------------------------------
Ran 69 tests in 15.036s

OK
exit=0
```

(The four 429 lines come from the scripted clients in `GeminiClientTest`, not from the API.)

## 5. The replay check

**runs/v6 daniel_ate_it, seeds 1–3, replayed by the current code** through morning.py, key unset:

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 1 --replay --out v6
daniel_ate_it-seed1: model gemini-3.5-flash-lite, replay from cache only; cache cache\v6\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 45 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 4; so far 0 live, 12 cached, 0 API requests
  min 09: model asked for 2; so far 0 live, 14 cached, 0 API requests
  min 12: model asked for 4; so far 0 live, 18 cached, 0 API requests
  min 15: model asked for 4; so far 0 live, 22 cached, 0 API requests
  min 18: model asked for 4; so far 0 live, 26 cached, 0 API requests
  min 21: model asked for 2; so far 0 live, 28 cached, 0 API requests
  min 24: model asked for 4; so far 0 live, 32 cached, 0 API requests
  min 27: model asked for 4; so far 0 live, 36 cached, 0 API requests
  min 30: model asked for 4; so far 0 live, 40 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 41 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 42 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 43 cached, 0 API requests
  min 66: model asked for 1; so far 0 live, 44 cached, 0 API requests
  min 75: model asked for 1; so far 0 live, 45 cached, 0 API requests

wrote runs/v6/daniel_ate_it-seed1.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 45
  model_decisions: 45
  fallbacks: 0
  routine_decisions: 75
  lines_spoken: 28
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1354
  run_seconds: 0.0
  story_sha256: facdcf437f38666fb6892f836973d9d38a2bc9e487faabb87139b52755fdae0c
  byte for byte against runs\v6\daniel_ate_it-seed1.md: IDENTICAL
exit=0
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 2 --replay --out v6
daniel_ate_it-seed2: model gemini-3.5-flash-lite, replay from cache only; cache cache\v6\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 66 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 3; so far 0 live, 11 cached, 0 API requests
  min 09: model asked for 2; so far 0 live, 13 cached, 0 API requests
  min 12: model asked for 4; so far 0 live, 17 cached, 0 API requests
  min 15: model asked for 4; so far 0 live, 21 cached, 0 API requests
  min 18: model asked for 4; so far 0 live, 25 cached, 0 API requests
  min 21: model asked for 3; so far 0 live, 28 cached, 0 API requests
  min 24: model asked for 4; so far 0 live, 32 cached, 0 API requests
  min 27: model asked for 4; so far 0 live, 36 cached, 0 API requests
  min 30: model asked for 4; so far 0 live, 40 cached, 0 API requests
  min 33: model asked for 4; so far 0 live, 44 cached, 0 API requests
  min 36: model asked for 4; so far 0 live, 48 cached, 0 API requests
  min 39: model asked for 4; so far 0 live, 52 cached, 0 API requests
  min 42: model asked for 1; so far 0 live, 53 cached, 0 API requests
  min 51: model asked for 1; so far 0 live, 54 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 55 cached, 0 API requests
  min 63: model asked for 2; so far 0 live, 57 cached, 0 API requests
  min 66: model asked for 4; so far 0 live, 61 cached, 0 API requests
  min 69: model asked for 4; so far 0 live, 65 cached, 0 API requests
  min 78: model asked for 1; so far 0 live, 66 cached, 0 API requests

wrote runs/v6/daniel_ate_it-seed2.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 66
  model_decisions: 66
  fallbacks: 0
  routine_decisions: 54
  lines_spoken: 48
  inner_moments: 5
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1371
  run_seconds: 0.1
  story_sha256: 1ee05b8e272e58a3937ba7364dd85d39c6b6db064462df489ff8e1583b4e3d3b
  byte for byte against runs\v6\daniel_ate_it-seed2.md: IDENTICAL
exit=0
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 3 --replay --out v6
daniel_ate_it-seed3: model gemini-3.5-flash-lite, replay from cache only; cache cache\v6\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 25 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 2; so far 0 live, 10 cached, 0 API requests
  min 15: model asked for 1; so far 0 live, 11 cached, 0 API requests
  min 30: model asked for 3; so far 0 live, 14 cached, 0 API requests
  min 33: model asked for 2; so far 0 live, 16 cached, 0 API requests
  min 39: model asked for 3; so far 0 live, 19 cached, 0 API requests
  min 42: model asked for 1; so far 0 live, 20 cached, 0 API requests
  min 45: model asked for 2; so far 0 live, 22 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 23 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 24 cached, 0 API requests
  min 78: model asked for 1; so far 0 live, 25 cached, 0 API requests

wrote runs/v6/daniel_ate_it-seed3.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 25
  model_decisions: 25
  fallbacks: 0
  routine_decisions: 95
  lines_spoken: 9
  inner_moments: 6
  private_talks: 0
  max_prompt_tokens_estimated: 1398
  max_prompt_tokens_counted_by_api: 1365
  run_seconds: 0.0
  story_sha256: a5958d3ada0ffad1e12c1f50d5b682e897e412d13ecdea74b4627345fa489462
  byte for byte against runs\v6\daniel_ate_it-seed3.md: IDENTICAL
exit=0
```

- **The hashes match.** The three story hashes are the ones baseline_v6.md records
  (`facdcf43…`, `1ee05b8e…`, `a5958d3a…`).
- **The replay files.** `--replay` writes `runs/v6/daniel_ate_it-seedN.replay.md`. These are the
  three old untracked files, rewritten with the same bytes (morning.py compares them with the
  story).
- **The transcripts** are compared too, by the unit test
  `test_the_v6_baseline_replays_byte_for_byte_with_no_requests` (§2).

**The frozen versions still replay** (v5/, v6/, v7/, each on its own modules):

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe v5/check.py
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
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe v6/check.py
daniel_ate_it-seed1: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 66 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 44 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 43 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe v7/check.py
daniel_ate_it-seed1: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 48 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 33 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 18 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

**v7/ is the code that made the v7 runs:**

```
$ for f in data gemini metrics metrics3 metrics4 metrics5 morning story talk world; do git show 427868b:Prototypes/llm-morning/$f.py | cmp -s - v7/$f.py && echo "v7/$f.py == 427868b:$f.py" || echo "v7/$f.py DIFFERS"; done
v7/data.py == 427868b:data.py
v7/gemini.py == 427868b:gemini.py
v7/metrics.py == 427868b:metrics.py
v7/metrics3.py == 427868b:metrics3.py
v7/metrics4.py == 427868b:metrics4.py
v7/metrics5.py == 427868b:metrics5.py
v7/morning.py == 427868b:morning.py
v7/story.py == 427868b:story.py
v7/talk.py == 427868b:talk.py
v7/world.py == 427868b:world.py
```

**What is left of the difference from v6** (current code against v6/):

```
$ for f in data gemini metrics metrics3 metrics4 metrics5 morning story talk world; do cmp -s $f.py v6/$f.py && echo "$f.py == v6/$f.py" || echo "$f.py differs from v6/$f.py"; done
data.py differs from v6/data.py
gemini.py == v6/gemini.py
metrics.py == v6/metrics.py
metrics3.py == v6/metrics3.py
metrics4.py == v6/metrics4.py
metrics5.py == v6/metrics5.py
morning.py differs from v6/morning.py
story.py differs from v6/story.py
talk.py == v6/talk.py
world.py differs from v6/world.py
$ diff v6/world.py world.py; echo "---- story.py"; diff v6/story.py story.py
212a213
>         self.can_note = data.about_the_can(scenario, pid)  # what else they know of the night, if anything
433c434
<             out.append("About the can: you ate it yourself.")
---
>             about = "About the can: you ate it yourself."
435,436c436,437
<             out.append(f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
<                        f"{p.confession_heard_at:02d}.")
---
>             about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
>                      f"{p.confession_heard_at:02d}.")
438,440c439,441
<             out.append(f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
<                        f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
<                        f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
---
>             about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
>                      f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
>                      f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
442c443,444
<             out.append("About the can: you have not settled on who took it.")
---
>             about = "About the can: you have not settled on who took it."
>         out.append(f"{about} {p.can_note}" if p.can_note else about)
---- story.py
213a214,220
> 
>     def knows(p):
>         pid = next(q for q in data.ORDER if data.PEOPLE[q] is p)
>         if pid == culprit:
>             return "ate it in the night; nobody saw"
>         note = data.about_the_can(morning.scenario, pid)
>         return "only that it is missing" + (f"; told: {quoted(note)}" if note else "")
220,221c227
<         ("Knows about the can", lambda p: "ate it in the night; nobody saw" if culprit and p is data.PEOPLE[culprit]
<          else "only that it is missing"),
---
>         ("Knows about the can", knows),
```

- **data.py and morning.py** differ from v6 by the witness scenario and the v7→v8 output default
  (§7).
- **world.py and story.py** differ by the witness code only. None of it applies to daniel_ate_it:
  `can_note` is `None` there, and the cast cell reads "only that it is missing" as before.

## 6. The token-budget check

- **The script.** `budget8.py` (§9) builds Leo's minute-00 prompt with the current code in both
  scenarios, two ways:
  - (a) paired with the v6 baseline answers, as T9 does;
  - (b) in a fresh morning, as T3 does.
- **What it prints.** `estimate_tokens(SYSTEM + prompt)` (world.py, `int(len/3.6) + 1`) against
  `PROMPT_TOKEN_BUDGET`; how many more characters would fit; whether the cut marker is there;
  and how many lines changed.

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/budget8.py < /dev/null
estimate_tokens(SYSTEM) = 254; the longest SYSTEM + prompt within the budget is 5039 characters
note (132 chars): Last night you woke and heard someone open a can in the kitchen, so someone in this house took it in the night. You did not see who.
seed 1, paired with the v6 answers (Leo acts 2 of 4): daniel_ate_it 1319, witness 1356 (budget 1400); witness length 4880 chars, 159 more would fit; cut marker: False; lines changed: 2
seed 2, paired with the v6 answers (Leo acts 4 of 4): daniel_ate_it 1360, witness 1397 (budget 1400); witness length 5028 chars, 11 more would fit; cut marker: False; lines changed: 2
seed 3, paired with the v6 answers (Leo acts 4 of 4): daniel_ate_it 1361, witness 1398 (budget 1400); witness length 5032 chars, 7 more would fit; cut marker: False; lines changed: 2
fresh morning (seeds 1-3 alike): daniel_ate_it 1324, witness 1361 (budget 1400); witness length 4897 chars, 142 more would fit; cut marker: False; lines changed: 2

seed 3, Leo's minute-00 witness prompt, from his memory to the room:
What you remember from the days before:
- Day 1: Daniel boards the front windows on his own while the others watch. (you saw it)
- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you did it)
- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)
- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you did it)
- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
- Day 3: Mara cries in the night. Elena sits with her until it stops. (you heard it)
- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
- Day 4: Leo says maybe they should let someone else handle this one. (you did it)
- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)
What you are sure of this morning:
- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)
What else happened this morning, most recent last:
- nothing else yet
exit=0
```

| | daniel_ate_it | witness | budget | characters to spare | lines cut |
|---|---|---|---|---|---|
| seed 1, paired (Leo acts 2nd) | 1319 | 1356 | 1400 | 159 | 0 |
| seed 2, paired (Leo acts 4th) | 1360 | 1397 | 1400 | 11 | 0 |
| seed 3, paired (Leo acts 4th) | 1361 | 1398 | 1400 | 7 | 0 |
| fresh morning | 1324 | 1361 | 1400 | 142 | 0 |

- **What the table shows.**
  - "Lines changed: 2" is the one can line, removed and added back with the note.
  - The printed memory section of seed 3 keeps all 10 backstory lines and "nothing else yet".
- **Why it fits again.** Removing the thought sentence brings `estimate_tokens(SYSTEM)` back from
  281 to 254 (thought_field_impl.md §8).
  - The new note (132 characters) is about as long as v6's heard line with its "Day 3: … (you
    heard it)" wrapping.
  - So the estimates are the ones witness_design.md §1 computed for v6: 1356, 1397 and 1398.

## 7. The diff

**Everything but test_morning.py and the ten copied v7/ modules**
(`git diff fd2583b^ fd2583b -- . ':!v7' ':!test_morning.py'`):

```diff
diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index 92e6b98..81c0b99 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -15,3 +15,5 @@ runs/v6/fake/
 cache/v6/fake-*
 runs/v7/fake/
 cache/v7/fake-*
+runs/v8/fake/
+cache/v8/fake-*
diff --git a/Prototypes/llm-morning/data.py b/Prototypes/llm-morning/data.py
index 8bb3e1e..22effa8 100644
--- a/Prototypes/llm-morning/data.py
+++ b/Prototypes/llm-morning/data.py
@@ -117,11 +117,12 @@ SCENARIOS = {
 }
 # Not in the shipped data: daniel_ate_it, and Leo heard the night from his bed but did not see
 # who (reports/witness_design.md). It is told to Leo alone, at the end of his "About the can:"
-# line (reports/witness_probe.md, variant B), so it names nobody he did not see.
+# line (reports/witness_probe.md, variant B), so it names nobody he did not see. It says what
+# follows from it too, so the model is not left to work that out (reports/belief_line_impl.md).
 SCENARIOS["daniel_ate_it_leo_heard"] = {
     **SCENARIOS["daniel_ate_it"],
-    "about_the_can": {"leo": "Last night you woke and heard someone in the kitchen open a can; "
-                             "you did not see who."},
+    "about_the_can": {"leo": "Last night you woke and heard someone open a can in the kitchen, so "
+                             "someone in this house took it in the night. You did not see who."},
 }
 DEFAULT_SCENARIO = "daniel_ate_it"
 
diff --git a/Prototypes/llm-morning/gemini.py b/Prototypes/llm-morning/gemini.py
index fedcfe0..2194cfc 100644
--- a/Prototypes/llm-morning/gemini.py
+++ b/Prototypes/llm-morning/gemini.py
@@ -44,12 +44,9 @@ def load_config(path):
         return json.load(f)
 
 
-# `thought` comes first, and the order is given explicitly, so that it is written before the
-# choice (reports/witness_probe2.md, variant C).
 RESPONSE_SCHEMA = {
     "type": "object",
     "properties": {
-        "thought": {"type": "string"},
         "option": {"type": "string"},
         "say": {"type": "string", "nullable": True},
         "feeling": {"type": "string"},
@@ -57,8 +54,7 @@ RESPONSE_SCHEMA = {
         "suspects": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
         "angry_at": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
     },
-    "required": ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"],
-    "property_ordering": ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"],
+    "required": ["option", "say", "feeling", "reason", "suspects", "angry_at"],
 }
 
 
@@ -164,7 +160,6 @@ class FakeClient:
         pick = options[h % len(options)] if options else "stay"
         speaking = re.search(rf"^- {pick}: \(speech\)", block, flags=re.M) is not None
         answer = {
-            "thought": f"Fake thought {self.requests}.",
             "option": pick,
             "say": f"[fake line {self.requests}]" if speaking else None,
             "feeling": ["afraid", "calm", "ashamed", "angry", "tired"][h % 5],
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 7cb5bde..426f808 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -8,9 +8,9 @@
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v7; v4 replays
-                      the fourth version's runs; v5/check.py and v6/check.py replay the
-                      fifth's and sixth's)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v8; v4 replays
+                      the fourth version's runs; v5/check.py, v6/check.py and v7/check.py
+                      replay the fifth's, sixth's and seventh's)
 
 The model names and call limits are in config.json. The key is read from GEMINI_API_KEY.
 
@@ -33,13 +33,13 @@ HERE = os.path.dirname(os.path.abspath(__file__))
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v7"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v8"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v6/ can still replay.
+    # cache/vN after), which v1/ to v7/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -136,7 +136,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v7")
+    ap.add_argument("--out", default="v8")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index 00ba349..4b42ed0 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -81,8 +81,7 @@ def decision_line(d, fold=None):
               f"Angry at: {d['angry_at']}; {d['grudge_note']}.")
     return (f"- **{name}**{order}. {because}.{held} **Chose: {d['label']}**{said}"
             f"{newness(d)} (one of {d['offered']} options). Feeling: *{d['feeling']}*. "
-            f"Thought: {quoted(d['thought'])} Reason: {quoted(d['reason'])}{inside} "
-            f"Came of it: {d['came_of_it']}{fact}")
+            f"Reason: {quoted(d['reason'])}{inside} Came of it: {d['came_of_it']}{fact}")
 
 
 def room_line(rec):
@@ -153,8 +152,7 @@ def render(morning, seed, model_name, command):
       "looks upset in the same room, or someone came in). Only then is the model asked. What "
       "happened is listed.")
     w("- **Chose**: the option the model picked from those the rules offered. Its words are in "
-      "quotes. The thought (written first, before the choice), the feeling and the one-sentence "
-      "reason are the model's, as it wrote them. Nobody's prompt ever shows a thought.")
+      "quotes. The feeling and the one-sentence reason are the model's, as it wrote them.")
     w("- **New / not new**: a line is new if it is a question, an accusation, a denial of a new "
       "accusation, or a confession, and the speaker has not taken that stance before. "
       "Reassurance, repeated stances and other remarks are not new. Something eaten, shared or "
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 774b12b..dadbbae 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -33,8 +33,7 @@ SYSTEM = (
     "doing it, or null. `feeling` names what they feel right now in one or two words. "
     "`reason` is their reason in one sentence, as they would think it. `suspects` is who they "
     "now believe took the can, and `angry_at` is who they are angry with right now: each is "
-    'one of "Daniel", "Elena", "Leo", "Mara" or "nobody". `thought` is what goes through their '
-    "mind first, in two or three sentences, before they choose. Reply with JSON only: "
+    'one of "Daniel", "Elena", "Leo", "Mara" or "nobody". Reply with JSON only: '
     '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
     '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
 )
@@ -561,7 +560,7 @@ class Morning:
             return None, "not JSON"
         if not isinstance(ans, dict):
             return None, "not a JSON object"
-        for field in ("thought", "option", "feeling", "reason"):
+        for field in ("option", "feeling", "reason"):
             if not isinstance(ans.get(field), str) or not ans[field].strip():
                 return None, f"no `{field}`"
         if "say" not in ans or not (ans["say"] is None or isinstance(ans["say"], str)):
@@ -586,8 +585,7 @@ class Morning:
         if opt.id == "silent" and say:
             say, dropped = None, True
         return {"option": opt.id, "say": say, "feeling": " ".join(ans["feeling"].split()).lower(),
-                "thought": " ".join(ans["thought"].split()), "reason": " ".join(ans["reason"].split()),
-                "dropped_line": dropped, **named}, None
+                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped, **named}, None
 
     # ---------- one turn ----------
     def run(self):
@@ -670,8 +668,7 @@ class Morning:
                      "words": d.get("say"), "audience": audience, "mode": d["mode"],
                      "decided_at": [minute, d["seq"]], "said_at": [minute, d["seq"]],
                      "came_of_it": d["came_of_it"], "new": d.get("new"), "new_why": d.get("new_why"),
-                     "inner": d.get("inner_families"), "thought": d.get("thought"),
-                     "suspects": d.get("suspects"),
+                     "inner": d.get("inner_families"), "suspects": d.get("suspects"),
                      "angry_at": d.get("angry_at"),
                      "moved_to": opt.act["to"] if opt.act["kind"] in ("go", "accept_aside") else None}
             tturn["acts"].append(entry)
```

**v7/check.py** (new; `git diff fd2583b^ fd2583b -- v7/check.py`):

```diff
diff --git a/Prototypes/llm-morning/v7/check.py b/Prototypes/llm-morning/v7/check.py
new file mode 100644
index 0000000..10f879e
--- /dev/null
+++ b/Prototypes/llm-morning/v7/check.py
@@ -0,0 +1,55 @@
+"""Replays the six seventh-version mornings from their cache and checks their stories.
+
+    python v7/check.py
+
+v7/ is a frozen copy of the code that made the runs reports/witness_v7.md describes
+(daniel_ate_it, and daniel_ate_it_leo_heard, with the thought field). Replaying makes
+no API calls. Each replayed story must come out byte for byte as
+runs/v7/<name>.md, and its transcript as the one saved beside it.
+"""
+import json
+import os
+import sys
+
+HERE = os.path.dirname(os.path.abspath(__file__))
+ROOT = os.path.dirname(HERE)
+sys.path.insert(0, HERE)
+
+from gemini import Cache, Oracle             # noqa: E402  (v7's own modules)
+from story import render                     # noqa: E402
+from world import Morning                    # noqa: E402
+
+# (scenario, model key, model name, seeds), as the runs in runs/v7 were made.
+RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3)),
+        ("daniel_ate_it_leo_heard", None, "gemini-3.5-flash-lite", (1, 2, 3))]
+
+
+def main():
+    ok = True
+    for scenario, key, model, seeds in RUNS:
+        for seed in seeds:
+            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
+            cache = Cache(os.path.join(ROOT, "cache", "v7", f"{model}-{name}.json"))
+            oracle = Oracle(cache, model, seed, client=None, replay=True)
+            morning = Morning(oracle, seed, scenario)
+            for t in range(morning.turns):
+                morning.turn(t)
+            morning.finish()
+            command = ("python morning.py"
+                       + (f" --scenario {scenario}" if scenario != "daniel_ate_it" else "")
+                       + (f" --model {key}" if key else "") + f" --seed {seed}")
+            text = render(morning, seed, model, command)
+            base = os.path.join(ROOT, "runs", "v7", name)
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
```

**The ten copied modules** are the files of 427868b, byte for byte (§5).

## 8. git

```
$ git log --oneline -4
fd2583b LLM morning: no thought field; Leo's night line says what follows from it
abf031e LLM morning: baseline and witness runs for v7 (thought field), seeds 1-3
427868b LLM morning: report for the thought field and Leo's moved night line
177e300 LLM morning: a thought before every decision; Leo's night line in "About the can"
$ git show --stat --format= fd2583b
 Prototypes/llm-morning/.gitignore      |    2 +
 Prototypes/llm-morning/data.py         |    7 +-
 Prototypes/llm-morning/gemini.py       |    7 +-
 Prototypes/llm-morning/morning.py      |   12 +-
 Prototypes/llm-morning/story.py        |    6 +-
 Prototypes/llm-morning/test_morning.py |  273 ++++----
 Prototypes/llm-morning/v7/check.py     |   55 ++
 Prototypes/llm-morning/v7/data.py      |  186 ++++++
 Prototypes/llm-morning/v7/gemini.py    |  256 ++++++++
 Prototypes/llm-morning/v7/metrics.py   |  182 ++++++
 Prototypes/llm-morning/v7/metrics3.py  |  141 ++++
 Prototypes/llm-morning/v7/metrics4.py  |  149 +++++
 Prototypes/llm-morning/v7/metrics5.py  |  152 +++++
 Prototypes/llm-morning/v7/morning.py   |  147 +++++
 Prototypes/llm-morning/v7/story.py     |  339 ++++++++++
 Prototypes/llm-morning/v7/talk.py      |  105 +++
 Prototypes/llm-morning/v7/world.py     | 1114 ++++++++++++++++++++++++++++++++
 Prototypes/llm-morning/world.py        |   11 +-
 18 files changed, 2989 insertions(+), 155 deletions(-)
$ git status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

(Taken after `fd2583b` and before this report was written. The report is committed next, on its
own.)

## 9. Commands run, in order

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset for everything that imports the
client. `<scratchpad>` is the session scratchpad, which is not in the repository.
1. `git status --porcelain`, `git log --oneline -3`; `git show --stat fa54a48`.
2. `git add runs/v7 cache/v7 reports/witness_v7.md` and `git commit` → `abf031e`.
3. v7/: `git show HEAD:Prototypes/llm-morning/<f>.py > v7/<f>.py` for the ten modules; `cmp`
   against the working tree (all equal); `sed` over v6/check.py → v7/check.py;
   `python v7/check.py` → 6 of 6 IDENTICAL, exit 0.
4. A read-only one-liner over cache/v6 that estimates Leo's minute-00 witness prompt with the new
   note (1356, 1397, 1398), before any test was written.
5. The new tests spliced into test_morning.py (a scratchpad script). The suite was then run →
   22 fail (§3).
6. `cp v6/gemini.py gemini.py`; edits to world.py, story.py, data.py and morning.py; two lines
   added to .gitignore.
7. The suite → 69 OK. `morning.py --seed N --replay --out v6` for N = 1, 2, 3; v5/, v6/ and v7/
   check.py; `budget8.py`.
8. `git add` and `git commit` → `fd2583b`. The suite again on the commit → 69 OK.
9. `git diff fd2583b^ fd2583b …` for §2 and §7.

**budget8.py**

```python
"""Read-only: Leo's minute-00 prompt in daniel_ate_it and daniel_ate_it_leo_heard, built by the
current code. (a) paired with the v6 baseline answers (cache/v6), as a witness run paired with a
baseline would be; (b) in a fresh morning (nobody has acted yet), as test T3 builds it.
Prints estimate_tokens(SYSTEM + prompt) against PROMPT_TOKEN_BUDGET, the length in characters
and how many more characters would fit, and whether any line was cut."""
import difflib
import json
import os
import sys

ROOT = "C:/Users/Akrem/Desktop/Projects/Fallow/Prototypes/llm-morning"
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import data                                                        # noqa: E402
from gemini import Cache, FakeClient, Oracle                       # noqa: E402
from world import PROMPT_TOKEN_BUDGET, SYSTEM, Morning, estimate_tokens  # noqa: E402

WITNESS = "daniel_ate_it_leo_heard"
MODEL = "gemini-3.5-flash-lite"
MAX_LEN = max(n for n in range(4000, 6000) if int(n / 3.6) + 1 <= PROMPT_TOKEN_BUDGET)


class Paired:
    def __init__(self, seed):
        with open(f"cache/v6/{MODEL}-daniel_ate_it-seed{seed}.json", encoding="utf-8") as f:
            self.entries = json.load(f)
        self.seed, self.asked, self.missed = seed, [], []

    def ask(self, system, prompt):
        self.asked.append(prompt)
        entry = self.entries.get(Cache.key(MODEL, self.seed, system, prompt))
        if entry:
            return entry["response"]
        self.missed.append(prompt)
        return json.dumps({"option": "silent", "say": None, "feeling": "calm", "reason": "Waiting.",
                           "suspects": "nobody", "angry_at": "nobody"})


def show(label, old, new):
    t_old, t_new = estimate_tokens(SYSTEM + old), estimate_tokens(SYSTEM + new)
    diff = [d for d in difflib.ndiff(old.splitlines(), new.splitlines()) if d[:2] in ("+ ", "- ")]
    print(f"{label}: daniel_ate_it {t_old}, witness {t_new} (budget {PROMPT_TOKEN_BUDGET}); "
          f"witness length {len(SYSTEM + new)} chars, {MAX_LEN - len(SYSTEM + new)} more would fit; "
          f"cut marker: {'(earlier things, left out here)' in new}; lines changed: {len(diff)}")


print(f"estimate_tokens(SYSTEM) = {estimate_tokens(SYSTEM)}; the longest SYSTEM + prompt within "
      f"the budget is {MAX_LEN} characters")
print(f"note ({len(data.about_the_can(WITNESS, 'leo'))} chars): {data.about_the_can(WITNESS, 'leo')}")
for seed in (1, 2, 3):
    leo = {}
    for scenario in ("daniel_ate_it", WITNESS):
        o = Paired(seed)
        Morning(o, seed, scenario).turn(0)
        leo[scenario] = [p for p in o.asked if p.startswith("You are Leo,")][0]
        if scenario == "daniel_ate_it":
            assert not o.missed, seed
        position = [p.split(",")[0][8:] for p in o.asked].index("Leo") + 1
    show(f"seed {seed}, paired with the v6 answers (Leo acts {position} of 4)", leo["daniel_ate_it"], leo[WITNESS])
for seed in (1,):
    fresh = {}
    for scenario in ("daniel_ate_it", WITNESS):
        m = Morning(Oracle(Cache(os.devnull + ".none"), "fake", seed, client=FakeClient()), seed, scenario)
        p = m.people["leo"]
        fresh[scenario] = m.prompt_for(p, 0, m.options_for(p))
    show("fresh morning (seeds 1-3 alike)", fresh["daniel_ate_it"], fresh[WITNESS])
o = Paired(3)
Morning(o, 3, WITNESS).turn(0)
p = [x for x in o.asked if x.startswith("You are Leo,")][0]
lines = p.splitlines()
i = lines.index("What you remember from the days before:")
j = next(k for k, x in enumerate(lines) if x.startswith("Now, minute 00"))
print("\nseed 3, Leo's minute-00 witness prompt, from his memory to the room:")
print("\n".join(lines[i:j]))
```
