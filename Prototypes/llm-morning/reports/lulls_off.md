# Lull moments off

Mode: implement. Lull moments are switched off by one constant, `LULL_QUIET = None`. Their code
is kept. No API was called. Paths are relative to `Prototypes/llm-morning/`.

**Why.** reports/lull_v9.md found that lulls mostly replaced silence with repeated reassurance,
three times word for word, which is less human than the silence.

## Commits

| Commit | What |
|---|---|
| `dc3f42d` | reports/lull_v9.md, runs/v9/ and cache/v9/, on their own |
| **`79e1e8a`** | **`LULL_QUIET = None`, plus the tests that assumed lulls were on** |
| (the commit that adds this report) | reports/lulls_off.md |

**Another session committed in between.** `a7bffab` (CLAUDE.md and
Docs/understanding/target-morning.md, "the inactivity Never item judges frozen silence") landed
6 seconds after `dc3f42d`. This session did not make it. It also created
`reports/never_item_update.md`, which this session did not touch. That session committed it
itself as `175670e`, while this report was being committed.

## What changed

**world.py.** One line: `LULL_QUIET = 9` became `LULL_QUIET = None`, with a comment saying
when it was switched off and what the design's value was (world.py:59-60).

- With `None`, `lull_due` returns `False` (world.py:829), so no decision is ever a lull.
- No prompt gets the line.
- Everything else of the lull code runs exactly as before, but nothing comes of it:
  - `last_stir` and `last_asked` are still kept;
  - every transcript act still has `"lull": None`;
  - meta still has `lull_moments: 0`;
  - the story still prints its key line.
- No lull code was deleted.

**test_morning.py.** Two kinds of lull test:

- **Tests that switch lulls on themselves are kept as lull tests**: T2, T3/T7, T5 and T8. They
  run through the `fake(seed, lulls=True)` helper, which patched `LULL_QUIET` to the module's
  own value; that value is now `None`. So the helper now patches in the design's 9, as
  `DESIGN_LULL_QUIET = 9`. Their assertions are unchanged, and they still test the mechanism
  with lulls on.
- **Tests that assumed the default was on now check the off state:**

  | Test before | Test after | What it checks now |
  |---|---|---|
  | `test_t1_the_numbers`: (9, 12) | same name | `(LULL_QUIET, LULL_EVERY) == (None, 12)` |
  | `test_t1a_the_room_must_be_still_for_9_minutes` | `test_t1a_off_a_room_still_for_9_minutes_gives_no_lull` | Room still 9, not asked for 12: `lull_due` is `False`, the decision is routine, and `last_asked` is untouched. |
  | `test_t1b_the_person_must_not_have_been_asked_for_12_minutes` | `test_t1b_off_never_asked_in_a_room_still_all_morning_gives_no_lull` | Minute 87, room still since 00, never asked: routine, no lull. |
  | `test_t1e_t8_t9_alone_after_leaving` | `test_t1e_t9_off_alone_after_leaving_no_lull_asks_him` | Leo alone in the back room from minute 3: routine at 3, 6, 9 and 12. No lull anywhere, no prompt has the line, and his alone-and-routine stretch is at least 4 turns. The T9 part (his leaving is no trigger for the others) is unchanged. |
  | `test_t1i_a_fallback_counts_as_asked` | same name | It used a lull to reach the model. It now uses a social trigger: a fallback still sets `last_asked`, and there is no lull. |
  | `test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull` | `test_t6_off_the_v6_baseline_caches_replay_to_the_end` | The v6 baseline caches carry each morning to its end, where with lulls on they stopped at minute 42, 51 and 15. 45, 66 and 25 answers come from the cache, with 0 requests. No prompt has the line. Every act has `lull: None`. The transcript is v6's once the `lull` key is removed. |
  | `test_t10_lulls_are_recorded` | `test_t10_off_no_lull_is_recorded` | Fake seeds 1–3: every act has `"lull": None`, `lull_moments` is 0 and printed as `lull_moments: 0`, and the story has no `**Lull**, nothing said…` line. |

- **Unchanged, and still passing:**
  - T1c, T1d, T1f, T1g/h (lull state is still kept), T4 (`prompt_for` given a lull minute
    directly) and T11 (v8 replays);
  - `test_with_lulls_off_the_v6_baseline_replays_with_no_requests`, which sets `None` itself;
  - `test_the_story_and_the_transcript_carry_no_thought`;
  - all the older tests.

## Test output

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning
exit=0
…
test_the_story_and_the_transcript_carry_no_thought (…) ... ok
test_with_lulls_off_the_v6_baseline_replays_with_no_requests (…) … ok
test_t10_off_no_lull_is_recorded (test_morning.LullTest.test_t10_off_no_lull_is_recorded) ... ok
test_t11_v8_still_replays (test_morning.LullTest.test_t11_v8_still_replays) ... ok
test_t1_the_numbers (test_morning.LullTest.test_t1_the_numbers) ... ok
test_t1a_off_a_room_still_for_9_minutes_gives_no_lull (…) ... ok
test_t1b_off_never_asked_in_a_room_still_all_morning_gives_no_lull (…) ... ok
test_t1c_a_social_trigger_comes_first (…) ... ok
test_t1d_an_inner_moment_comes_first (…) ... ok
test_t1e_t9_off_alone_after_leaving_no_lull_asks_him (…) … ok
test_t1f_carrying_on_searching_stirs_the_room (…) ... ok
test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not (…) ... ok
test_t1i_a_fallback_counts_as_asked (…) ... ok
test_t2_a_still_room_is_never_talking (…) ... ok
test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place (…) ... ok
test_t4_nothing_else_in_the_prompt_changes (…) ... ok
test_t5_nothing_changes_before_the_first_lull (…) ... ok
test_t6_off_the_v6_baseline_caches_replay_to_the_end (…) … ok
test_t8_nobody_is_alone_more_than_3_turns_without_being_asked (…) ... ok
----------------------------------------------------------------------
Ran 86 tests in 26.739s

OK
```

**Before the test updates.** With `LULL_QUIET = None` and the tests as they were, the suite had
7 failures and 4 errors. The last line of each traceback:

```
ERROR: LullTest.test_t1a_the_room_must_be_still_for_9_minutes -> KeyError: 'lull'
ERROR: LullTest.test_t1b_the_person_must_not_have_been_asked_for_12_minutes -> KeyError: 'lull'
ERROR: LullTest.test_t1e_t8_t9_alone_after_leaving -> KeyError: 'lull'
ERROR: LullTest.test_t1i_a_fallback_counts_as_asked -> KeyError: 'lull'
FAIL: LullTest.test_t10_lulls_are_recorded -> AssertionError: 0 not greater than 0
FAIL: LullTest.test_t1_the_numbers -> + (9, 12)
FAIL: LullTest.test_t2_a_still_room_is_never_talking -> AssertionError: 0 not greater than 0
FAIL: LullTest.test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place -> AssertionError: 0 not greater than 0
FAIL: LullTest.test_t5_nothing_changes_before_the_first_lull -> AssertionError: 0 not greater than 0
FAIL: LullTest.test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull -> AssertionError: CacheMiss not raised
FAIL: LullTest.test_t8_nobody_is_alone_more_than_3_turns_without_being_asked
Ran 86 tests in 26.027s
FAILED (failures=7, errors=4)
```

- These 11 are exactly the tests updated above.
- T2, T3/T7, T5 and T8 failed only because their helper took the module's value, now `None`.
  Their own assertions were not changed.

## v8 check

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe v8/check.py
daniel_ate_it_leo_heard-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

## Left as they are (outside this brief), for the user to decide

1. **The story's key line now reads "None minutes."** story.py:193-196 prints the lull key line
   from `LULL_QUIET` in every story. With lulls off it reads:

   ```
   - **Lull**: nothing social or inner, but nothing has been said or done in their room for at least None minutes (staying put in silence and staying seated do not count), and they have not been asked for at least 12 minutes; the model is asked, and told since when the room has been still.
   ```

   That line is from a fake morning rendered with the current code. Changing it is a story.py
   edit, and the brief allowed none.
2. **The next run would land on top of v9.** morning.py's default `--out` is still `v9`
   (morning.py:36, :139).
   - A run of `daniel_ate_it` with the default would write over the committed
     `runs/v9/daniel_ate_it-seedN.*`.
   - It would also reuse `cache/v9` answers wherever a prompt matches, which is every prompt
     before the v9 run's first lull.
   - Before any new run, the version needs moving on: freeze v9 and default to v10, as was
     done for v8.
3. **Git status.** When `79e1e8a` was made, git status also showed the other session's untracked
   `reports/never_item_update.md`, which was left for that session. That session has since
   committed it (`175670e`). After this report's commit, git status shows only the three old
   `runs/v6/daniel_ate_it-seed*.replay.md`.

## Commands run

No command called the API. Every test and script ran with `GEMINI_API_KEY` unset.

1. `git add reports/lull_v9.md runs/v9 cache/v9 && git commit` gave `dc3f42d`. git warned
   CRLF→LF for the three v9 stdout.txt files.
2. `LULL_QUIET` was set to `None` in world.py, then `unittest` was run: 7 failures, 4 errors
   (above).
3. The 11 tests were updated as the table says, then `unittest -v` was run: 86, OK (above).
4. `v8/check.py`: above.
5. **The story key line with lulls off:** a fake seed-1 morning was rendered with `render()`,
   and the lines starting `- **Lull**` were printed. The output is quoted in "Left as they
   are", item 1.
6. `git add world.py test_morning.py && git commit` gave `79e1e8a`.
7. `git status --short` gave the three `runs/v6/daniel_ate_it-seed*.replay.md` and
   `reports/never_item_update.md`, which is the other session's. After the other session's
   `175670e` and this report's commit, it gave only the three replay.md files.

## The diff

`git diff 79e1e8a~1 79e1e8a` (world.py and test_morning.py):

```diff
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 61c5022..6dda4ea 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -1205,6 +1205,9 @@ class WitnessScenarioTest(unittest.TestCase):
 LULL_LINE = re.compile(r"^Nothing has been said or done in the (kitchen|brothers room|back room|bathroom) "
                        r"since minute (\d\d)\.$", flags=re.M)
 HUNGRIER = "Since you last decided, you have grown hungrier."
+# Lull moments are off (world.LULL_QUIET is None, reports/lulls_off.md). The tests that switch
+# them on themselves use the design's value (reports/lull_design.md, §1).
+DESIGN_LULL_QUIET = 9
 
 
 class Recorder:
@@ -1253,7 +1256,9 @@ def longest_alone_routine(transcript):
 
 
 class LullTest(unittest.TestCase):
-    """Lull moments (reports/lull_design.md, sections 1 to 3; tests T1 to T11 of section 5)."""
+    """Lull moments (reports/lull_design.md, sections 1 to 3; tests T1 to T11 of section 5).
+    They are off (reports/lulls_off.md): the tests that do not switch them on themselves check
+    that nothing comes of them."""
 
     def setUp(self):
         self.dirs = Dirs()
@@ -1262,10 +1267,11 @@ class LullTest(unittest.TestCase):
         self.dirs.cleanup()
 
     def fake(self, seed, lulls=True):
-        """A fake-model morning; with lulls=False, lull moments are switched off."""
+        """A fake-model morning; with lulls=True, lull moments are switched on at the design's 9
+        minutes, and with lulls=False, off."""
         rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"f{seed}-{lulls}.json")), "fake", seed,
                               client=FakeClient()))
-        with mock.patch.object(world, "LULL_QUIET", world.LULL_QUIET if lulls else None):
+        with mock.patch.object(world, "LULL_QUIET", DESIGN_LULL_QUIET if lulls else None):
             m = Watched(rec, seed).run()
         return m, rec
 
@@ -1281,31 +1287,27 @@ class LullTest(unittest.TestCase):
 
     # T1
     def test_t1_the_numbers(self):
-        self.assertEqual((world.LULL_QUIET, world.LULL_EVERY), (9, 12))
+        self.assertEqual((world.LULL_QUIET, world.LULL_EVERY), (None, 12))
 
-    def test_t1a_the_room_must_be_still_for_9_minutes(self):
+    def test_t1a_off_a_room_still_for_9_minutes_gives_no_lull(self):
         m = self.still_kitchen()
         mara = m.people["mara"]
-        m.last_stir["kitchen"], mara.last_asked = 9, 3
-        d = m.decide(mara, 5)                                   # minute 15: still for 6
+        m.last_stir["kitchen"], mara.last_asked = 6, 3          # minute 15: still for 9, not asked for 12
+        self.assertFalse(m.lull_due(mara, 15))
+        d = m.decide(mara, 5)
         self.assertEqual(d["mode"], "routine")
         self.assertNotIn("lull", d)
         self.assertEqual(mara.last_asked, 3)
-        m.last_stir["kitchen"] = 6                              # still for 9
-        d = m.decide(mara, 5)
-        self.assertEqual((d["mode"], d["lull"], d["triggers"]), ("model", 6, []))
-        self.assertNotIn("inner", d)
-        self.assertEqual(mara.last_asked, 15)
 
-    def test_t1b_the_person_must_not_have_been_asked_for_12_minutes(self):
+    def test_t1b_off_never_asked_in_a_room_still_all_morning_gives_no_lull(self):
         m = self.still_kitchen()
         mara = m.people["mara"]
-        m.last_stir["kitchen"], mara.last_asked = 6, 6
-        d = m.decide(mara, 5)                                   # asked 9 minutes ago
+        m.last_stir["kitchen"], mara.last_asked = 0, None       # minute 87: still for 87, never asked
+        self.assertFalse(m.lull_due(mara, 87))
+        d = m.decide(mara, 29)
         self.assertEqual(d["mode"], "routine")
         self.assertNotIn("lull", d)
-        mara.last_asked = 3                                     # 12 minutes ago
-        self.assertEqual(m.decide(mara, 5)["lull"], 6)
+        self.assertIsNone(mara.last_asked)
 
     def test_t1c_a_social_trigger_comes_first(self):
         m = self.still_kitchen()
@@ -1325,27 +1327,19 @@ class LullTest(unittest.TestCase):
         self.assertEqual(d["inner_kinds"], ["hunger"])
         self.assertNotIn("lull", d)
 
-    def test_t1e_t8_t9_alone_after_leaving(self):
-        """Leo goes to the back room at minute 0 and then stays silent: routine at 3, 6 and 9,
-        a lull at 12; his leaving is no trigger for the others."""
+    def test_t1e_t9_off_alone_after_leaving_no_lull_asks_him(self):
+        """Leo goes to the back room at minute 0 and then stays silent: with lulls off, nothing
+        asks him at 12 (routine at 3, 6, 9 and 12); his leaving is no trigger for the others."""
         def policy(who, minute, options, client):
             return ("go_back_room", None) if (who, minute) == ("leo", 0) else ("silent", None)
         m, client = scripted(policy, self.dirs)
+        self.assertEqual(m.people["leo"].room, "back_room")
         leo = [(rec["minute"], d) for rec in m.log for d in rec["decisions"] if d["person"] == "leo"]
-        self.assertEqual([d["mode"] for _, d in leo[1:4]], ["routine"] * 3)
-        self.assertEqual((leo[4][0], leo[4][1]["mode"], leo[4][1]["lull"]), (12, "model", 0))
-        self.assertIn("Nothing has been said or done in the back room since minute 00.",
-                      next(p for minute, who, p in client.prompts if (minute, who) == (12, "leo")))
-        # Every lull, anyone's, comes 12 or more minutes after that person was last asked.
-        last = {}
-        for rec in m.log:
-            for d in rec["decisions"]:
-                if d.get("lull") is not None:
-                    self.assertGreaterEqual(rec["minute"] - last[d["person"]], 12, d["person"])
-                if d["mode"] != "routine":
-                    last[d["person"]] = rec["minute"]
-        # T8: P3's count.
-        self.assertEqual(longest_alone_routine(m.transcript), 3)
+        self.assertEqual([(minute, d["mode"]) for minute, d in leo[1:5]],
+                         [(3, "routine"), (6, "routine"), (9, "routine"), (12, "routine")])
+        self.assertFalse([d for rec in m.log for d in rec["decisions"] if d.get("lull") is not None])
+        self.assertFalse([p for _, _, p in client.prompts if "Nothing has been said or done in the" in p])
+        self.assertGreaterEqual(longest_alone_routine(m.transcript), 4)
         # T9: the others were told he left, and it was no trigger for them.
         for pid in ("daniel", "elena", "mara"):
             self.assertIn((0, "Leo leaves for the back room."), m.people[pid].memory)
@@ -1388,8 +1382,10 @@ class LullTest(unittest.TestCase):
         m = self.still_kitchen(client=Broken())
         mara = m.people["mara"]
         m.last_stir["kitchen"] = 0
+        mara.triggers = [("Elena asks everyone who took the can", True)]   # lulls are off: a trigger asks
         d = m.decide(mara, 5)
-        self.assertEqual((d["mode"], d["lull"]), ("fallback", 0))
+        self.assertEqual(d["mode"], "fallback")
+        self.assertNotIn("lull", d)
         self.assertEqual(mara.last_asked, 15)
 
     # T2
@@ -1459,41 +1455,27 @@ class LullTest(unittest.TestCase):
         self.assertGreater(lulls, 0)
 
     # T6
-    def test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull(self):
-        """Replayed on the v6 answers with no client, the morning is v6's until the first lull,
-        whose prompt is not in the cache: seed 1 min 42 Mara, seed 2 min 51 Elena, seed 3 min 15
-        Daniel, after 41, 53 and 10 answers from the cache (reports/lull_design.md, §4)."""
-        expected = {1: (42, "mara", 41, 33), 2: (51, "elena", 53, 42), 3: (15, "daniel", 10, 3)}
-        for seed, (minute, who, served, since) in expected.items():
+    def test_t6_off_the_v6_baseline_caches_replay_to_the_end(self):
+        """With lulls off, the v6 answers carry each morning to its end, where with lulls on they
+        stopped at the first lull (seed 1 min 42, seed 2 min 51, seed 3 min 15): every answer
+        from the cache, 0 requests, v6's transcript but for the `lull` key, which is None."""
+        for seed, served in ((1, 45), (2, 66), (3, 25)):
             name = f"daniel_ate_it-seed{seed}"
             path = os.path.join(self.dirs.root, f"{name}.json")
             shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
             oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
             rec = Recorder(oracle)
             m = Morning(rec, seed)
-            with self.assertRaises(gemini.CacheMiss):
+            try:
                 for t in range(m.turns):
                     m.turn(t)
-            last = rec.prompts[-1]
-            self.assertTrue(last.startswith(f"You are {data.PEOPLE[who]['name']},"), seed)
-            self.assertIn(f"\nNow, minute {minute:02d}, you are in the kitchen.\n", last)
-            self.assertEqual(LULL_LINE.findall(last), [("kitchen", f"{since:02d}")], seed)
+            except gemini.StopMorning as stop:
+                self.fail(f"seed {seed}: {stop}")
             self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
-            v6 = json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json")))
+            self.assertFalse([p for p in rec.prompts if "Nothing has been said or done in the" in p], seed)
+            self.assertTrue(all(a["lull"] is None for turn in m.transcript["turns"] for a in turn["acts"]))
             self.assertEqual(without_lull(m.transcript)["turns"],
-                             [turn for turn in v6["turns"] if turn["minute"] < minute], seed)
-            # In the turn it stops, whoever acted before was silent in v6 too, as the prompt says.
-            now = next(turn for turn in v6["turns"] if turn["minute"] == minute)
-            before = []
-            for a in now["acts"]:
-                if a["who"] == who:
-                    break
-                before.append(a)
-            self.assertTrue(all(a["option"] == "silent" for a in before), seed)
-            for i, a in enumerate(before, 1):
-                self.assertIn(f"\n{i}. {data.PEOPLE[a['who']]['name']} stays put and says nothing.\n", last)
-            if not before:
-                self.assertIn("\nYou are the first to act in the kitchen this turn.\n", last)
+                             json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json")))["turns"], seed)
 
     # T8 on fake mornings
     def test_t8_nobody_is_alone_more_than_3_turns_without_being_asked(self):
@@ -1502,20 +1484,16 @@ class LullTest(unittest.TestCase):
             self.assertLessEqual(longest_alone_routine(m.transcript), 3, seed)
 
     # T10
-    def test_t10_lulls_are_recorded(self):
-        total = 0
+    def test_t10_off_no_lull_is_recorded(self):
         for seed in (1, 2, 3):
             (meta, code), out = fake_morning(self.dirs, seed=seed)
             self.assertEqual(code, 0, out)
             tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))
-            acts = [a for turn in tr["turns"] for a in turn["acts"] if a["lull"] is not None]
-            self.assertEqual(meta["lull_moments"], len(acts), seed)
-            self.assertTrue(all(a["mode"] in ("model", "fallback") for a in acts), seed)
+            self.assertTrue(all("lull" in a and a["lull"] is None for turn in tr["turns"] for a in turn["acts"]))
+            self.assertEqual(meta["lull_moments"], 0, seed)
             story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
-            self.assertEqual(len(re.findall(r"\*\*Lull\*\*, nothing said or done in the ", story)), len(acts))
-            self.assertIn("lull_moments", out)
-            total += len(acts)
-        self.assertGreater(total, 0)
+            self.assertNotIn("**Lull**, nothing said or done in the ", story)
+            self.assertIn("lull_moments: 0", out)
 
     # T11
     def test_t11_v8_still_replays(self):
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 05da32a..12c0aa8 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -56,7 +56,8 @@ PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,370 at most in the s
 QUIET_TURNS = 2              # full turns with nothing new that end a conversation
 INNER_EVERY = 9              # minutes: an inner moment at most this often per person
 FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one step this often
-LULL_QUIET = 9               # minutes a room must be still before a lull (None: no lulls)
+LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
+                             # off since reports/lull_v9.md, 9 in reports/lull_design.md
 LULL_EVERY = 12              # minutes since a person was last asked before a lull
 
 KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
```
