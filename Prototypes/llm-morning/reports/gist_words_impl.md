# Own lines without their words (variant B), implemented

Mode: implement. A person's own spoken lines now reach their later prompts as variant B of
reports/repetition_probe.md does: minute and verb, no quoted words. Other people's lines keep
their words. No API was called. Paths are relative to `Prototypes/llm-morning/`.

## Commits

| Commit | What |
|---|---|
| `fced993` | reports/repetition_audit.md and reports/repetition_probe.md, on their own |
| `bf3a372` | **The v9 freeze**: the current code copied to v9/, with v9/check.py replaying runs/v9. morning.py's default `--out` goes to v10, and .gitignore gets `runs/v10/fake/` and `cache/v10/fake-*`, as the v8 freeze (`c6fdcc4`) did. |
| **`a09c499`** | **The change: world.py and test_morning.py** |
| (the commit that adds this report) | reports/gist_words_impl.md |

After the last commit, `git status --short` shows only the three old untracked
`runs/v6/daniel_ate_it-seed{1,2,3}.replay.md`.

**About the v9 freeze.**
- runs/v9 were made at `1c50d44` with `LULL_QUIET = 9`. The code that was current, and was
  frozen, has `LULL_QUIET = None`.
- That constant is the only difference. Every other file is identical to its `1c50d44` version
  (command 2).
- So v9/check.py sets `world.LULL_QUIET = 9` before it imports `story` (story.py copies the
  value when it is imported).
- It reports all three mornings IDENTICAL, with 0 API calls (command 3).
- A first version set the constant after importing `story`, so the three stories differed only
  in the key line, which read "None minutes" (command 3).

## The change

world.py, in `apply`, where a spoken line is recorded for the speaker (world.py:983-989):

| | Before | After |
|---|---|---|
| Memory | `you reassured everyone: "<words>". You felt anxious.` | `you reassured everyone. You felt anxious.` |
| "Your own last words this morning:" (`said_lines`) | `min 51, you reassured everyone: "<words>"` | `min 51, you reassured everyone.` |

- Both are rendered by the unchanged `prompt_for` (world.py:539-542). In the prompt they read
  `- min 51: you reassured everyone. You felt anxious.` and `- min 51, you reassured everyone.`,
  which is variant B's line.
- The verb is still `mine` (world.py:983-985): "asked who took it", "denied taking it", "accused
  <name>", "admitted taking it", "reassured <name/everyone>", or "said" for any other line.
- The comment on `said_lines` (world.py:212) now says "without the words".
- **Unchanged**, as the brief requires:
  - other people's lines everywhere: memory through `perceive` and `line_text` (world.py:936-938),
    and this turn's "Said and done";
  - the confession `sure` lines;
  - the pattern block;
  - options, rules and config.

**The change on a real prompt.** This is from the fake model, seed 1: Daniel at minute 03, the
first prompt of someone who has already spoken, against the frozen v9 code. The 5 prompts
before it are identical (command 6):

```
--- v9 (frozen)
+++ now
@@ -24,6 +24,6 @@
 Your own last words this morning:
-- min 00, you reassured everyone: "[fake line 1]"
+- min 00, you reassured everyone.
 What else happened this morning, most recent last:
 - (earlier things, left out here)
-- min 00: you reassured everyone: "[fake line 1]". You felt afraid.
+- min 00: you reassured everyone. You felt afraid.
 - min 00: Leo reassures Elena: "[fake line 2]"
```

## Tests

**New, in `OwnWordsTest`:**

| Brief | Test | What it checks |
|---|---|---|
| A person's own words never appear in their later prompts | `test_own_words_never_appear_in_their_later_prompts` | Fake seeds 1–5, every prompt sent: none of the person's earlier words appear in it. The fake words are unique (`[fake line N]`). |
| … and the new form | `test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words` | Scripted. The first actor at minute 0 says "FIRST-WORDS" (`reassure_all`) and the second reassures them, "SECOND-WORDS". At minute 3 the first actor's prompt has no "FIRST-WORDS". It has `Your own last words this morning:` / `- min 00, you reassured everyone.` and `- min 00: you reassured everyone. You felt tense.`, and the second's line with its words, `- min 00: <name> reassures you: "SECOND-WORDS"`. |
| Other people's words still appear | `test_others_words_still_reach_the_prompt` | Fake seeds 1–5: other people's earlier words, in quotes, appear in later prompts (count > 0). |
| A prompt from before the person has spoken is unchanged | `test_prompts_before_someone_has_spoken_are_unchanged` | Fake seeds 1–5, against the frozen v9 code with the same fake model (see below). |

**How the last test works.**
- Every prompt is identical up to the first prompt of someone who has already spoken.
- That prompt must differ, only in that person's own lines, which lose their words.
- Being shorter, it may let the existing trimming (world.py:551-561) keep an older memory or
  backstory line.

**Existing tests whose expectations changed.** There are two. Both replayed the v6 baseline
caches in full. A person who has spoken now gets a new prompt, so those caches can only answer
up to that person's first prompt after speaking.

1. `test_with_lulls_off_the_v6_baseline_replays_with_no_requests` is replaced by
   `test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked`.
   - Where it stops is computed from the v6 transcript: the first model decision by someone who
     had already spoken. In all three seeds that is **minute 03, Elena, after 4 answers** from
     the cache (command 4).
   - The test checks that the replay stops there with `CacheMiss` and 0 requests.
   - It checks that every completed turn equals v6's.
   - It checks that none of Elena's earlier words are in that prompt.
   - This replaces the byte-for-byte story check that the old test did. That check is now
     carried by v6/check.py, which runs the frozen v6 code.
2. `test_t6_off_the_v6_baseline_caches_replay_to_the_end` is replaced by
   `test_t6_off_no_lull_in_a_whole_morning_on_the_v6_answers`.
   - It runs a whole morning on the v6 answers with `PairedOracle`, which gives a silent answer
     wherever a prompt is not in the cache.
   - It checks that no prompt has the lull line and no act is a lull, so lulls are still off.

The other 84 tests are unchanged and pass.

**One fix to a new test after the change.**
- The first run after the change failed `test_prompts_before_someone_has_spoken_are_unchanged`
  in seed 3.
- The shorter prompt had kept an older **backstory** line, `- Day 2: Daniel says they should
  cross to the neighbour's house tonight…`, and the test allowed only an extra memory line.
- Under the trimming order, backstory lines go before memory once memory is down to 8 lines
  (world.py:554-557).
- The test now allows an extra `- min ` or `- Day ` line. Its other checks are unchanged.

### Before the change (tests written, world.py untouched)

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning
exit=1
FAIL: DecisionFormatTest.test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked -> AssertionError: CacheMiss not raised : seed 1
FAIL: OwnWordsTest.test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words -> AssertionError: 'FIRST-WORDS' unexpectedly found in 'You are Daniel, 25, the eldest son of the family …'
FAIL: OwnWordsTest.test_own_words_never_appear_in_their_later_prompts -> AssertionError: '[fake line 1]' unexpectedly found in 'You are Daniel, 25, the eldest son of the family …'
FAIL: OwnWordsTest.test_prompts_before_someone_has_spoken_are_unchanged -> AssertionError: '<Daniel's minute-03 prompt, with "[fake line 1]">' == '<the same>' : 1
Ran 90 tests in 25.650s
FAILED (failures=4)
```

- The three new tests that test the change failed, as did the changed v6 pairing test.
- The last one failed because Daniel's minute-03 prompt was still identical to the frozen v9
  one, with his `"[fake line 1]"` in it. The full prompt is in the saved output.
- **Two guards passed before the change**, as they should:
  - `test_others_words_still_reach_the_prompt`: nothing removed others' words before;
  - `test_t6_off_no_lull_in_a_whole_morning_on_the_v6_answers`: lulls were already off.

### After the change

First run: one failure, the backstory line above, then the test fix. Final run:

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning
exit=0
…
test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked (…) … ok
test_t6_off_no_lull_in_a_whole_morning_on_the_v6_answers (…) … ok
test_others_words_still_reach_the_prompt (test_morning.OwnWordsTest.test_others_words_still_reach_the_prompt) ... ok
test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words (…) ... ok
test_own_words_never_appear_in_their_later_prompts (…) ... ok
test_prompts_before_someone_has_spoken_are_unchanged (…) … ok
----------------------------------------------------------------------
Ran 90 tests in 32.741s

OK
```

**Frozen versions still replay** (command 5):

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe v8/check.py
daniel_ate_it_leo_heard-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
```

## Before the next run (not done; outside this brief)

1. **Pairing with v6 now covers minute 00 only.**
   - A v10 run paired with the v6 baseline caches (as the witness and lull run plans did) would
     share only minute 00.
   - Each seed parts at minute 03, Elena, after 4 answers.
   - So most of a v10 morning is live requests.
2. **The story's key line still says "None minutes" for lulls** (story.py:193-196;
   reports/lulls_off.md, "Left as they are", item 1).
3. **Nothing tells a person that their earlier words are gone.**
   - Their own block says only "you reassured everyone." The "What you have been doing" block
     is unchanged.
   - repetition_probe.md tested this form at one moment only, 6 answers per case.
   - What it does over a whole morning is not yet measured: for example, the frozen-silence
     Never item, or the same new line twice.

## Commands run

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. `$S` is the session scratchpad.

1. `git add reports/repetition_audit.md reports/repetition_probe.md && git commit` gave
   `fced993`. git warned CRLF→LF for both files.
2. **Was the v9 runs' code the current code?**
   ```
   $ for f in data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py story.py talk.py world.py; do git diff --quiet 1c50d44 HEAD -- $f && echo "$f: same as at 1c50d44" || …; done
   data.py: same as at 1c50d44
   gemini.py: same as at 1c50d44
   metrics.py: same as at 1c50d44
   metrics3.py: same as at 1c50d44
   metrics4.py: same as at 1c50d44
   metrics5.py: same as at 1c50d44
   morning.py: same as at 1c50d44
   story.py: same as at 1c50d44
   talk.py: same as at 1c50d44
   world.py differs:
   -LULL_QUIET = 9               # minutes a room must be still before a lull (None: no lulls)
   +LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
   +                             # off since reports/lull_v9.md, 9 in reports/lull_design.md
   ```
3. **The freeze.**
   - `cp data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py story.py talk.py world.py v9/`.
   - v9/check.py was made from v8/check.py, with its version, paths and RUNS changed, and
     `LULL_QUIET = 9`.
   - First `v9/check.py` run, with the constant set after `story` was imported: 3 × "story
     DIFFERS, transcript IDENTICAL", exit 1.
   - After moving it before the import: 3 × "story IDENTICAL, transcript IDENTICAL", exit 0.
   - morning.py `--out` was changed v9 → v10, and the docstring and comment updated.
     `.gitignore` got two lines.
   - `unittest` gave "Ran 86 tests … OK". `git commit` gave `bf3a372`.
4. **Where the v6 pairing now stops**, from the v6 transcripts:
   ```
   seed 1: first prompt of someone who has spoken: min 03 elena; answers before it: 4
   seed 2: first prompt of someone who has spoken: min 03 elena; answers before it: 4
   seed 3: first prompt of someone who has spoken: min 03 elena; answers before it: 4
   ```
5. **The tests and the change.**
   - The tests were written (`$S/gist_tests_edit.py`, a one-off edit of test_morning.py), then
     the suite was run: 4 failures, shown above.
   - world.py was edited, then the suite was run: 1 failure (the backstory line), then the test
     fix.
   - `unittest -v`: 90, OK.
   - `v9/check.py` and `v8/check.py`: shown above.
   - `git commit` gave `a09c499`.
6. **The example diff:** `$S/gist_example.py` runs fake seed 1 for 2 turns with the frozen v9
   world and with the current one, and diffs the first prompt of someone who had spoken:
   ```
   prompt 6: You are Daniel, 25, the eldest son of th ... Now, minute 03, you are in the kitchen.
   prompts before it identical: True (5 prompts)
   (the diff shown under "The change")
   ```

## The diff

`git diff a09c499~1 a09c499` (world.py and test_morning.py):

```diff
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 6dda4ea..be27b82 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -934,6 +934,21 @@ def without_lull(transcript):
     return tr
 
 
+def first_ask_after_speaking(transcript):
+    """(minute, person, model answers before it) of the first decision in a saved transcript
+    that asked the model for someone who had already spoken that morning."""
+    spoke, served = set(), 0
+    for turn in transcript["turns"]:
+        for a in turn["acts"]:
+            if a["mode"] != "routine":
+                if a["who"] in spoke:
+                    return turn["minute"], a["who"], served
+                served += 1
+            if a["words"]:
+                spoke.add(a["who"])
+    return None
+
+
 V6_RUNS = os.path.join(HERE, "runs", "v6")
 V6_CACHE = os.path.join(HERE, "cache", "v6")
 V6_MODEL = "gemini-3.5-flash-lite"
@@ -997,32 +1012,34 @@ class DecisionFormatTest(unittest.TestCase):
         self.assertEqual(keys(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")) - {"aside"},
                          keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")) | {"lull"})
 
-    def test_with_lulls_off_the_v6_baseline_replays_with_no_requests(self):
-        """With lull moments switched off, the v6 baseline still replays in full: the transcript
-        is v6's apart from the `lull` key on each act, and the story is v6's apart from the key's
-        one line about lulls (reports/lull_design.md, §3 and T12)."""
+    def test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked(self):
+        """The v6 answers carry each morning, unchanged, up to the first prompt of someone who has
+        already spoken: from there their own lines show no words (reports/gist_words_impl.md), so
+        that prompt is not in the cache. Lulls off, as now."""
         for seed in (1, 2, 3):
             name = f"daniel_ate_it-seed{seed}"
+            v6 = json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json")))
+            minute, who, served = first_ask_after_speaking(v6)
             path = os.path.join(self.dirs.root, f"{name}.json")
             shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
             oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
+            rec = Recorder(oracle)
             with mock.patch.object(world, "LULL_QUIET", None):
-                m = Morning(oracle, seed)
-                try:
+                m = Morning(rec, seed)
+                with self.assertRaises(gemini.CacheMiss, msg=f"seed {seed}"):
                     for t in range(m.turns):
                         m.turn(t)
-                except gemini.StopMorning as stop:
-                    self.fail(f"seed {seed}: {stop}")
-            m.finish()
-            text = render(m, seed, V6_MODEL, f"python morning.py --seed {seed}")
-            old = read(os.path.join(V6_RUNS, name + ".md"))
-            extra = [x for x in text.splitlines() if x not in old.splitlines()]
-            self.assertEqual([x[:10] for x in extra], ["- **Lull**"], seed)
-            self.assertEqual([x for x in text.splitlines() if x not in extra], old.splitlines(), seed)
-            self.assertEqual(without_lull(m.transcript),
-                             json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json"))), seed)
-            self.assertEqual((oracle.api_requests, oracle.live), (0, 0), seed)
-
+            last = rec.prompts[-1]
+            self.assertTrue(last.startswith(f"You are {data.PEOPLE[who]['name']},"), seed)
+            self.assertIn(f"\nNow, minute {minute:02d}, you are in the kitchen.\n", last)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+            self.assertEqual(without_lull(m.transcript)["turns"],
+                             [turn for turn in v6["turns"] if turn["minute"] < minute], seed)
+            spoken = [a["words"] for turn in v6["turns"] for a in turn["acts"]
+                      if a["who"] == who and a["words"] and turn["minute"] < minute]
+            self.assertTrue(spoken, seed)
+            for words in spoken:
+                self.assertNotIn(words, last, seed)
 
 class PairedOracle:
     """Answers from a saved cache when the prompt is the same as there, as a run paired with it
@@ -1455,27 +1472,17 @@ class LullTest(unittest.TestCase):
         self.assertGreater(lulls, 0)
 
     # T6
-    def test_t6_off_the_v6_baseline_caches_replay_to_the_end(self):
-        """With lulls off, the v6 answers carry each morning to its end, where with lulls on they
-        stopped at the first lull (seed 1 min 42, seed 2 min 51, seed 3 min 15): every answer
-        from the cache, 0 requests, v6's transcript but for the `lull` key, which is None."""
-        for seed, served in ((1, 45), (2, 66), (3, 25)):
-            name = f"daniel_ate_it-seed{seed}"
-            path = os.path.join(self.dirs.root, f"{name}.json")
-            shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
-            oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
-            rec = Recorder(oracle)
-            m = Morning(rec, seed)
-            try:
-                for t in range(m.turns):
-                    m.turn(t)
-            except gemini.StopMorning as stop:
-                self.fail(f"seed {seed}: {stop}")
-            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
-            self.assertFalse([p for p in rec.prompts if "Nothing has been said or done in the" in p], seed)
+    def test_t6_off_no_lull_in_a_whole_morning_on_the_v6_answers(self):
+        """With lulls off, a whole morning on the v6 answers (a silent answer wherever a prompt is
+        not in the v6 cache, as own lines now show no words) has no lull line and no lull act.
+        With lulls on, the v6 answers met their first lull at min 42, 51 and 15."""
+        for seed in (1, 2, 3):
+            oracle = PairedOracle(os.path.join(V6_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"),
+                                  V6_MODEL, seed)
+            m = Morning(oracle, seed).run()
+            self.assertEqual(len(m.transcript["turns"]), m.turns, seed)
+            self.assertFalse([p for p in oracle.asked if "Nothing has been said or done in the" in p], seed)
             self.assertTrue(all(a["lull"] is None for turn in m.transcript["turns"] for a in turn["acts"]))
-            self.assertEqual(without_lull(m.transcript)["turns"],
-                             json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json")))["turns"], seed)
 
     # T8 on fake mornings
     def test_t8_nobody_is_alone_more_than_3_turns_without_being_asked(self):
@@ -1505,6 +1512,120 @@ class LullTest(unittest.TestCase):
         self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
 
 
+OWN_BLOCK_LINE = re.compile(r'^(- min \d\d, you [^:"]+): ".*"$')
+OWN_MEMORY_LINE = re.compile(r'^(- min \d\d: you [^:"]+): ".*"\.(.*)$')
+
+
+def without_own_words(prompt):
+    """A prompt as the code before gist words wrote it, with the person's own lines turned into
+    what they are now: minute and verb, no words; memory keeps "You felt ..."."""
+    out = []
+    for line in prompt.splitlines():
+        line = OWN_BLOCK_LINE.sub(r"\1.", line)
+        line = OWN_MEMORY_LINE.sub(r"\1.\2", line)
+        out.append(line)
+    return out
+
+
+class OwnWordsTest(unittest.TestCase):
+    """A person's own spoken lines reach their later prompts without the words, as variant B of
+    reports/repetition_probe.md: in "Your own last words this morning:" and in memory, minute and
+    verb only (memory keeps "You felt <feeling>."). Other people's lines keep their words."""
+
+    def setUp(self):
+        self.dirs = Dirs()
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def fake(self, seed, module=world, tag="new"):
+        rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"{tag}{seed}.json")), "fake", seed,
+                              client=FakeClient()))
+        m = module.Morning(rec, seed)
+        for t in range(m.turns):
+            m.turn(t)
+        return m, rec
+
+    def test_own_words_never_appear_in_their_later_prompts(self):
+        checked = 0
+        for seed in range(1, 6):
+            m, rec = self.fake(seed)
+            decisions = [(r["minute"], d) for r in m.log for d in r["decisions"] if d["mode"] != "routine"]
+            self.assertEqual(len(decisions), len(rec.prompts), seed)
+            said = {p: [] for p in data.ORDER}
+            for (minute, d), prompt in zip(decisions, rec.prompts):
+                for words in said[d["person"]]:
+                    self.assertNotIn(words, prompt, (seed, minute, d["person"]))
+                    checked += 1
+                if d.get("say"):
+                    said[d["person"]].append(d["say"])
+        self.assertGreater(checked, 0)
+
+    def test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words(self):
+        def policy(who, minute, options, client):
+            if minute == 0 and client.requests == 1:
+                client.first = who
+                return "reassure_all", "FIRST-WORDS"
+            if minute == 0 and client.requests == 2:
+                client.second = who
+                return f"reassure_{client.first}", "SECOND-WORDS"
+            return "silent", None
+        m, client = scripted(policy, self.dirs, turns=2)
+        second = data.PEOPLE[client.second]["name"]
+        later = [p for minute, who, p in client.prompts if (minute, who) == (3, client.first)]
+        self.assertEqual(len(later), 1)              # just reassured, so asked at minute 3
+        prompt = later[0]
+        self.assertNotIn("FIRST-WORDS", prompt)
+        self.assertIn("\nYour own last words this morning:\n- min 00, you reassured everyone.\n", prompt)
+        self.assertIn("\n- min 00: you reassured everyone. You felt tense.\n", prompt)
+        self.assertIn(f'\n- min 00: {second} reassures you: "SECOND-WORDS"\n', prompt)
+        # The second, if asked at 3, sees the first's words and not their own.
+        for minute, who, p in client.prompts:
+            if (minute, who) == (3, client.second):
+                self.assertIn('"FIRST-WORDS"', p)
+                self.assertNotIn("SECOND-WORDS", p)
+                self.assertIn(f"- min 00, you reassured {data.PEOPLE[client.first]['name']}.", p)
+
+    def test_others_words_still_reach_the_prompt(self):
+        seen = 0
+        for seed in range(1, 6):
+            m, rec = self.fake(seed)
+            decisions = [(r["minute"], d) for r in m.log for d in r["decisions"] if d["mode"] != "routine"]
+            said = []
+            for (minute, d), prompt in zip(decisions, rec.prompts):
+                seen += sum(1 for who, words in said if who != d["person"] and f'"{words}"' in prompt)
+                if d.get("say"):
+                    said.append((d["person"], d["say"]))
+        self.assertGreater(seen, 0)
+
+    def test_prompts_before_someone_has_spoken_are_unchanged(self):
+        """Against the frozen v9 code, with the same fake model: the same prompts up to the first
+        prompt of someone who has already spoken, and that one differs only in their own lines,
+        which lose their words (and, being shorter, may let the trimming keep an older memory or
+        backstory line, world.py prompt_for)."""
+        old_world = frozen("v9", "world")
+        for seed in range(1, 6):
+            old, old_rec = self.fake(seed, old_world, "old")
+            new, new_rec = self.fake(seed)
+            decisions = [d for r in old.log for d in r["decisions"] if d["mode"] != "routine"]
+            spoke = set()
+            for i, d in enumerate(decisions):
+                if d["person"] in spoke:
+                    break
+                self.assertEqual(new_rec.prompts[i], old_rec.prompts[i], (seed, i))
+                if d.get("say"):
+                    spoke.add(d["person"])
+            else:
+                self.fail(f"seed {seed}: nobody who had spoken was asked again")
+            a, b = old_rec.prompts[i], new_rec.prompts[i]
+            self.assertNotEqual(a, b, seed)
+            expected, got = without_own_words(a), b.splitlines()
+            missing = [x for x in expected if x not in got and x != "- (earlier things, left out here)"]
+            extra = [x for x in got if x not in expected]
+            self.assertEqual(missing, [], seed)
+            self.assertTrue(all(x.startswith(("- min ", "- Day ")) for x in extra), (seed, extra))
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 12c0aa8..1bffaeb 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -209,7 +209,7 @@ class Person:
                           if (how := who.get(pid))]
         self.memory = []            # (minute, text) this morning, oldest first; trimmed to fit
         self.sure = []              # this morning's facts that are never trimmed
-        self.said_lines = []        # their own words, oldest first
+        self.said_lines = []        # their own spoken lines, oldest first, without the words
         self.triggers = []          # (text, is it new) social things since they last acted
         self.history = []           # one {"t", "kind", "seq"} per turn: what they did
         self.heard = []             # lines they heard: {"seq", "who", "kind", "target"}
@@ -983,8 +983,10 @@ class Morning:
             mine = {"ask": "asked who took it", "deny": "denied taking it",
                     "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
                     "reassure": f"reassured {target.name if aimed else 'everyone'}"}.get(kind, "said")
-            p.memory.append((minute, f"you {mine}: \"{words}\".{feel}"))
-            p.said_lines.append(f"min {minute:02d}, you {mine}: \"{words}\"")
+            # Their own lines reach them without the words: minute and verb only
+            # (reports/repetition_probe.md, variant B). The others hear the words.
+            p.memory.append((minute, f"you {mine}.{feel}"))
+            p.said_lines.append(f"min {minute:02d}, you {mine}.")
             if kind in ("ask", "accuse"):
                 p.heard_question = True
             if kind == "confess":
```
