# Implementation: time passing, the night and day 2 (v12)

Mode: implement. Builds reports/night_design.md, §1–§8, with the tests of §9. No API was called:
every command ran with `GEMINI_API_KEY` unset, or in replay mode (no client). Paths are relative
to `Prototypes/llm-morning/`. `$S` is the session scratchpad (`…/scratchpad/impl`).

## Result

| Done when | Status |
|---|---|
| The new tests fail before the change | **Yes.** All 32 new `NightTest` tests error on the code before the change (`ModuleNotFoundError: No module named 'night'`). So do 5 existing tests that now read the new meta and transcript shape (§3). |
| …and pass after | **Yes.** 32 of 32 (§4). |
| The full suite passes | **Yes.** `Ran 146 tests`, `OK`, exit 0. That is 114 earlier tests plus 32 new ones. |
| Day 1 replays from the v11 caches with 0 requests, story part byte for byte | **Yes** (§5): 55, 53 and 45 answers, 0 API requests, story IDENTICAL, transcript IDENTICAL. The night then stops cleanly at its first prompt, because no cache holds it. |
| All earlier frozen versions still replay identically | **Yes.** `v2/check.py` to `v11/check.py`: every line "story IDENTICAL, transcript IDENTICAL", all exit 0 (§5). |
| git status clean apart from the three old replay.md files | **Yes** (§6). |

**Commits:**
- `b09595d`: freeze v11 (`v11/` is byte-identical to the code at `976dc73`); new runs default to v12.
- `060b192`: the implementation and its tests.
- The commit that adds this report: see `git log`.

## 1. What was built

| Design | Where |
|---|---|
| §1 day 1 | `Morning(day=4)` is v11's morning, unchanged. Every v12 difference is gated on `day != 4` or on night-only code. |
| §2 gap | `night.Night.run`: +0.3 × rate before bed, +0.1 × rate in the night (capped at 1.0); `data.GAP`. |
| §3 night | `night.Night`: bedtime asks (`NIGHT_SYSTEM`, `data.HOUSE_THINGS_NIGHT`, "today" headings, the `Now` lines and four options); `leave()` (roommate, door sitter, front door through the walls, low voices, the return); `react_seen`, `react_heard`, `answer`; the draw strings of §3.3, overridable by `draws=` in tests; wake thresholds `wake_room`, `wake_door`. |
| §4 outcome | `house_portions`, `street`, `outcome_class`, `Night.trip` (carrying 3 each, the house remainder, the loss draw for groups, the shaken face, the outcome lines). |
| §5 day 2 | `night.next_day` / `Morning.next_day`: what carries and what resets (§5.1), `carry_in` + `bounded_carry_in` (≤ 360, quotes dropped first, then the minutes of the accusations), the opening, `food_line`, `neighbour_line`, grudge and guilt facts as "yesterday", someone away. `prompt_parts` puts the carry-in outside the budget. |
| §6 option fix | `Morning.trip_options_day2`, `trip_gist`, the day-2 `mine` lines, `heard_plan` forms, and `talk.act_of` for `nobody_goes`, `keep_<q>_home`, `send_<q>`, `still_going`, `refuse_to_go`. |
| §8 records | `morning.run` runs three scenes. The story is day 1 (unchanged) + `render_night` + `render_day2`. The transcript is `{"day1","night","day2"}`. Meta has run totals, `day1`, `night_asks`, `night_api_requests`, `leavers`, `outcome`, `night`, `day2_asks`, `day2_api_requests` and `day2`. `Oracle.new_scene` (and the clients') makes the call caps count each scene apart. |

## 2. Choices the design left open, and differences

1. **Punctuation of quoted night words.**
   - `"<words>".` would give `"Don't go.".`, so a stop is added only when the words lack one.
   - The stopper's line names the leaver ("You told Daniel, …") rather than "him".
2. **A roommate who slept through the getting-up still gets a door draw.** §3.3 says the door step covers "everyone in a bedroom who has not yet noticed L".
3. **Night answers keep the existing suspicion and grudge rules at minute 90** (§3.2). So a bedtime answer that does not name someone can let a grudge fall one step, if 15 minutes have passed since it changed. This happened with the fake model (Leo's grudge against Mara). Day 2 then resets the clocks to 0.
4. **A suspicion named at night reads "last night" on day 2**, not "yesterday at minute 90". The witness test exposed this.
5. **Food line grammar:** "there are q portions each" when q ≥ 2.
6. **A day-2 confession** says "after denying it to you yesterday at minute DD" for a day-1 denial, and likewise for a day-1 accusation.
7. **Night fallbacks** (the design gave none):
   - bedtime → `sleep`
   - seen → `let_<q>_go`
   - heard → `stay_in_bed`
   - waiting leaver who heard → `go_later`
   - answer → `go_anyway`
8. **Lines the design's table lacks**, for the waiting leaver's choices: "You let him go, to go yourself later.", "You let him go, and stayed in bed after all.", "You waited, to go yourself later.", "You stayed in bed after all."
9. **"tonight:" memory lines.** Later night prompts carry `- tonight: you lay awake and listened.` and short reaction lines.
10. **Away on day 2:** the person's hunger does not rise and voices do not reach them. The story shows "away".
11. **`can_note`** (only in the leo_heard scenario) still says "Last night" on day 2. That scenario is not run.

**Test corrections after the tests were first written**, each made after seeing a failure:
- (a) The `QUIET` draws gained `door:daniel:leo` (see point 2).
- (b) T9 "not noticed" ignores the N1 line, which names the roommate by design.
- (c) T8's fate regex dropped `body|bodies`, which matched the prompt heading "Your body:", and added `corpse`.

**Existing tests changed**, with the reason:

| Test | Change | Why |
|---|---|---|
| `FakeMorningTest.test_a_morning_completes…`, `test_every_kind_of_broken…` | read `meta["day1"]` | §8: day 1's keys move under `day1` |
| `ScenarioTest.test_each_scenario_runs…` | `tr["day1"]` | §8 transcript shape |
| `DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought` | keys from `tr["day1"]` | same |
| `LullTest.test_t10_off_no_lull_is_recorded` | `tr["day1"]`, `meta["day1"]` | same |
| `TripTest.test_t10_recording` | `tr["day1"]`, `meta["day1"]`, story cut at `# The night` | same |
| `FakeMorningTest.test_prompts_are_short` | skips night and day-2 prompts | they have their own bounds (§9 T12, in `NightTest`) |
| `WitnessScenarioTest.test_no_prompt_says_who_leo_heard` | regex accepts the day-2 "yesterday / last night / this morning" forms | §5.3 |

## 3. Tests before the change

```
$ env -u GEMINI_API_KEY python -m unittest test_morning
ERROR: test_a_morning_completes_and_writes_a_story (FakeMorningTest)        KeyError: 'day1'
ERROR: test_every_kind_of_broken_answer_falls_back_to_the_rules (FakeMorningTest)
ERROR: test_t10_off_no_lull_is_recorded (LullTest)
ERROR: test_each_scenario_runs_with_the_fake_model (ScenarioTest)
ERROR: test_t10_recording (TripTest)                                        KeyError: 'day1'
ERROR: (all 32 NightTest tests)            ModuleNotFoundError: No module named 'night'
Ran 146 tests in 55.472s
FAILED (errors=37)
exit=1
```

## 4. Tests after the change

```
$ env -u GEMINI_API_KEY python -m unittest -v test_morning
… 146 tests, each "ok" …
Ran 146 tests in 69.787s
OK
exit=0
```

## 5. Replays

Day 1 by the v12 code, from copies of the v11 caches, in replay mode (`$S/day1_replay.py`):

```
daniel_ate_it-seed1: day 1 replayed 55 answers from the v11 cache, 0 API requests; story part IDENTICAL to runs/v11/daniel_ate_it-seed1.md, transcript IDENTICAL
  the night stops cleanly at its first prompt, which no cache holds: 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).' (0 API requests)
daniel_ate_it-seed2: day 1 replayed 53 answers from the v11 cache, 0 API requests; story part IDENTICAL to runs/v11/daniel_ate_it-seed2.md, transcript IDENTICAL
  the night stops cleanly at its first prompt, which no cache holds: 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).' (0 API requests)
daniel_ate_it-seed3: day 1 replayed 45 answers from the v11 cache, 0 API requests; story part IDENTICAL to runs/v11/daniel_ate_it-seed3.md, transcript IDENTICAL
  the night stops cleanly at its first prompt, which no cache holds: 'You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).' (0 API requests)
exit=0
```

`NightTest.test_t1_*` checks the same thing inside the suite, and also checks that a full v12 story begins with day 1's text followed by `# The night`.

**Frozen versions** (output of `vN/check.py` for v2–v11 is appended below the diff, §8).

**Fake runs** of seeds 1–5 (no API):

| Seed | Night asks | Day-2 asks | Leavers | Outcome | Max estimated prompt |
|---|---|---|---|---|---|
| 1 | 4 | 20 | — | — | 1896 |
| 2 | 6 | 42 | Mara | back with nothing | 1933 |
| 3 | 4 | 92 | — | — | 1928 |
| 4 | 4 | 75 | — | — | 1954 |
| 5 | 5 | 47 | Daniel | back with food | 1947 |

## 6. git status

```
$ git status --short
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

## 7. The freeze (`b09595d`)

`v11/*.py` were copied unchanged; `cmp` against `git show 976dc73:<file>` matches for all ten
modules. `v11/check.py` is `v10/check.py` with v10 → v11. `morning.py` defaults `--out` to v12,
and `.gitignore` gains `runs/v12/fake/` and `cache/v12/fake-*`.

## 8. The diff of the implementation (`060b192`), then the frozen replays

```diff
diff --git a/Prototypes/llm-morning/data.py b/Prototypes/llm-morning/data.py
index 4d77657..d9449e7 100644
--- a/Prototypes/llm-morning/data.py
+++ b/Prototypes/llm-morning/data.py
@@ -93,6 +93,13 @@ HOUSE_THINGS = (
 HOUSE_THINGS_AFTER_TRIP = HOUSE_THINGS.replace("Outside, and not to be gone to:",
                                                "Outside, and not to be gone to this morning:")
 assert HOUSE_THINGS_AFTER_TRIP != HOUSE_THINGS
+# At night (reports/night_design.md, §3.2): tonight is when the plan said someone might go, so the
+# line no longer forbids it.
+HOUSE_THINGS_NIGHT = HOUSE_THINGS.replace("Outside, and not to be gone to:", "Outside:")
+assert HOUSE_THINGS_NIGHT != HOUSE_THINGS
+
+# The afternoon, skipped (reports/night_design.md, §2).
+GAP = "The afternoon and evening passed in the house. Nobody ate."
 
 # What everyone learns when the trip concern starts (reports/trip_design.md, §2.1): conclusions
 # the code draws, told after their "About the can:" line.
diff --git a/Prototypes/llm-morning/gemini.py b/Prototypes/llm-morning/gemini.py
index 2194cfc..909e6df 100644
--- a/Prototypes/llm-morning/gemini.py
+++ b/Prototypes/llm-morning/gemini.py
@@ -78,6 +78,7 @@ class GeminiClient:
         self.backoff_max = config["backoff_max_seconds"]
         self.max_output_tokens = config["max_output_tokens"]
         self.requests = 0
+        self.scene_base = 0         # requests sent before the current scene
         self.last_prompt_tokens = None
         self._sleep = sleep
         self._clock = clock
@@ -103,7 +104,7 @@ class GeminiClient:
         )
         attempt = 0
         while True:
-            if self.requests >= self.max_calls:
+            if self.requests - self.scene_base >= self.max_calls:
                 raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
             self._space()
             self.requests += 1
@@ -133,6 +134,9 @@ class GeminiClient:
                 self._sleep(wait)
                 attempt += 1
 
+    def new_scene(self):
+        self.scene_base = self.requests
+
 
 class FakeClient:
     """Canned answers for building and testing. Reads the option ids back out of the
@@ -146,10 +150,14 @@ class FakeClient:
         self.fail_with = fail_with or {}
         self.max_calls = max_calls
         self.requests = 0
+        self.scene_base = 0
         self.model = "fake"
 
+    def new_scene(self):
+        self.scene_base = self.requests
+
     def generate(self, system, prompt):
-        if self.requests >= self.max_calls:
+        if self.requests - self.scene_base >= self.max_calls:
             raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
         self.requests += 1
         if self.requests in self.fail_with:
@@ -214,7 +222,7 @@ class Oracle:
 
     def __init__(self, cache, model_name, seed, client=None, replay=False, max_calls=None):
         self.cache = cache
-        self.max_calls = max_calls      # for the whole morning, answers already cached included
+        self.max_calls = max_calls      # for each scene, answers already cached included
         self.model_name = model_name
         self.seed = seed
         self.client = client
@@ -222,6 +230,16 @@ class Oracle:
         self.from_cache = 0
         self.live = 0
         self.prompt_tokens = []     # as counted by the API, where it said
+        # Day 1, the night and day 2 each count against max_calls apart (reports/night_design.md,
+        # §8): what was asked before the current scene began.
+        self.base = (0, 0)
+
+    def new_scene(self):
+        """The next scene starts: its asks count against max_calls from zero, and so do the
+        client's own requests."""
+        self.base = (self.from_cache, self.api_requests)
+        if self.client is not None and hasattr(self.client, "new_scene"):
+            self.client.new_scene()
 
     @property
     def api_requests(self):
@@ -239,9 +257,10 @@ class Oracle:
         if self.replay or self.client is None:
             raise CacheMiss("stopped: replay found a prompt with no cached answer, so this "
                             "morning cannot be replayed from the cache.")
-        if self.max_calls is not None and self.from_cache + self.client.requests >= self.max_calls:
+        if (self.max_calls is not None
+                and self.from_cache - self.base[0] + self.client.requests - self.base[1] >= self.max_calls):
             raise CallCapReached(f"stopped: this morning reached {self.max_calls} model calls "
-                                 f"({self.from_cache} of them answered in an earlier run).")
+                                 f"({self.from_cache - self.base[0]} of them answered in an earlier run).")
         text = self.client.generate(system, prompt)
         self.live += 1
         tokens = getattr(self.client, "last_prompt_tokens", None)
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 8cc5368..f1af2fe 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -1,7 +1,8 @@
-"""Runs a morning with rules plus a language model, and writes it as a story.
+"""Runs a morning, the night after it and the next morning, with rules plus a language model, and
+writes them as one story (reports/night_design.md).
 
-    python morning.py --seed 1              a fresh morning; answers not in the cache are asked of Gemini
-    python morning.py --seed 1 --replay     the same morning from the cache only, with no API calls;
+    python morning.py --seed 1              a fresh run; answers not in the cache are asked of Gemini
+    python morning.py --seed 1 --replay     the same run from the cache only, with no API calls;
                                             writes runs/<out>/<name>.replay.md and compares it with
                                             runs/<out>/<name>.md
     python morning.py --seed 1 --fake       the same, against the fake model (for building and testing)
@@ -12,7 +13,9 @@
                       the fourth version's runs; v5/check.py to v11/check.py replay the
                       fifth's to eleventh's)
 
-The model names and call limits are in config.json. The key is read from GEMINI_API_KEY.
+Day 1 is the morning of the count; then the night; then day 2. The model names and call limits
+are in config.json; the call limit counts each of the three apart. The key is read from
+GEMINI_API_KEY.
 
 Exit codes: 0 done (and, for --replay, identical); 1 replay differs; 3 stopped cleanly part way
 (quota, rate limit, call cap, or a replay cache miss): see the message.
@@ -26,10 +29,54 @@ import time
 
 import data
 from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config
-from story import render
+from night import Night
+from story import render, render_day2, render_night
 from world import Morning
 
 HERE = os.path.dirname(os.path.abspath(__file__))
+DAY_KEYS = ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
+            "routine_decisions", "lines_spoken", "inner_moments", "lull_moments", "private_talks",
+            "trip_minute", "trip_acts", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api")
+
+
+class Scene:
+    """What one scene asked of the oracle: the counts since it began."""
+
+    def __init__(self, oracle):
+        self.oracle = oracle
+        self.start = self.now()
+        self.end = None
+
+    def now(self):
+        o = self.oracle
+        return o.from_cache, o.live, o.api_requests, len(o.prompt_tokens)
+
+    def close(self):
+        self.end = self.now()
+
+    def counts(self):
+        (cached, live, api, tokens), (cached2, live2, api2, tokens2) = self.start, self.end or self.now()
+        return {"api_requests": api2 - api, "answers_live": live2 - live, "answers_from_cache": cached2 - cached,
+                "max_prompt_tokens_counted_by_api": max(self.oracle.prompt_tokens[tokens:tokens2], default=None)}
+
+
+def day_meta(m, scene):
+    """A morning's numbers (day 1's are v11's)."""
+    all_d = [d for rec in m.log for d in rec["decisions"]]
+    meta = {
+        **scene.counts(),
+        "model_decisions": sum(d["mode"] == "model" for d in all_d),
+        "fallbacks": sum(d["mode"] == "fallback" for d in all_d),
+        "routine_decisions": sum(d["mode"] == "routine" for d in all_d),
+        "lines_spoken": len(m.said),
+        "inner_moments": sum(1 for d in all_d if d.get("inner")),
+        "lull_moments": sum(1 for d in all_d if d.get("lull") is not None),
+        "private_talks": sum(1 for d in all_d if d["option"] in ("accept_aside", "refuse_aside")),
+        "trip_minute": m.trip["minute"] if m.trip else None,
+        "trip_acts": len(m.trip_acts),
+        "max_prompt_tokens_estimated": m.max_prompt_tokens,
+    }
+    return {k: meta[k] for k in DAY_KEYS}
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
@@ -61,14 +108,35 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
     say(f"{name}: model {model_name}, {'replay from cache only' if replay else 'fresh'}; "
         f"cache {os.path.relpath(cache_path, HERE)} holds {len(cache.entries)} answers")
     started = time.monotonic()
-    morning = Morning(oracle, seed, scenario)
-    try:
-        for t in range(morning.turns):
-            morning.turn(t)
-            asked = sum(d["mode"] != "routine" for d in morning.log[-1]["decisions"])
+
+    def morning_turns(m, tag):
+        for t in range(m.turns):
+            m.turn(t)
+            asked = sum(d["mode"] != "routine" for d in m.log[-1]["decisions"])
             if asked:
-                say(f"  min {t * 3:02d}: model asked for {asked}; so far {oracle.live} live, "
+                say(f"  {tag}min {t * 3:02d}: model asked for {asked}; so far {oracle.live} live, "
                     f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
+        m.finish()
+
+    scenes = {}
+    try:
+        scenes["day1"] = Scene(oracle)
+        morning = Morning(oracle, seed, scenario)
+        morning_turns(morning, "")
+        # Day 1's story is written as it ended, before the night touches anything.
+        day1_text = render(morning, seed, model_name, command)
+        scenes["day1"].close()
+        oracle.new_scene()
+        scenes["night"] = Scene(oracle)
+        night = Night(morning, oracle).run()
+        scenes["night"].close()
+        say(f"  night: model asked for {len(night.decisions)}; so far {oracle.live} live, "
+            f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
+        oracle.new_scene()
+        scenes["day2"] = Scene(oracle)
+        day2 = Morning.next_day(morning, night, oracle)
+        morning_turns(day2, "day 2 ")
+        scenes["day2"].close()
     except StopMorning as stop:
         say(f"\n{stop}")
         say(f"Answers received so far ({len(cache.entries)}) are kept in {os.path.relpath(cache_path, HERE)}.")
@@ -78,40 +146,47 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
             say("Cached answers are reused, so only the prompts not yet answered are sent.")
         return {"stopped": str(stop), "api_requests": oracle.api_requests}, 3
     seconds = time.monotonic() - started
-    morning.finish()
 
-    text = render(morning, seed, model_name, command)
+    text = day1_text + render_night(night) + render_day2(day2)
     story_path = os.path.join(runs_dir, f"{name}.md")
     out_path = os.path.join(runs_dir, f"{name}.replay.md") if replay else story_path
     with open(out_path, "w", encoding="utf-8", newline="\n") as f:
         f.write(text)
-    all_d = [d for rec in morning.log for d in rec["decisions"]]
+    night_counts = scenes["night"].counts()
+    day2_counts = scenes["day2"].counts()
     meta = {
         "model": model_name, "scenario": scenario, "seed": seed, "replay": replay,
         "api_requests": oracle.api_requests, "answers_live": oracle.live,
         "answers_from_cache": oracle.from_cache,
-        "model_decisions": sum(d["mode"] == "model" for d in all_d),
-        "fallbacks": sum(d["mode"] == "fallback" for d in all_d),
-        "routine_decisions": sum(d["mode"] == "routine" for d in all_d),
-        "lines_spoken": len(morning.said),
-        "inner_moments": sum(1 for d in all_d if d.get("inner")),
-        "lull_moments": sum(1 for d in all_d if d.get("lull") is not None),
-        "private_talks": sum(1 for d in all_d if d["option"] in ("accept_aside", "refuse_aside")),
-        "trip_minute": morning.trip["minute"] if morning.trip else None,
-        "trip_acts": len(morning.trip_acts),
-        "max_prompt_tokens_estimated": morning.max_prompt_tokens,
+        "day1": day_meta(morning, scenes["day1"]),
+        "night_asks": night_counts["answers_live"] + night_counts["answers_from_cache"],
+        "night_api_requests": night_counts["api_requests"],
+        "leavers": night.leavers,
+        "outcome": [g["outcome"] for g in night.groups],
+        "night": {**night_counts, "house": night.house, "away": [q for q in data.ORDER if q in night.away],
+                  "max_prompt_tokens_estimated": night.m.max_prompt_tokens},
+        "day2_asks": day2_counts["answers_live"] + day2_counts["answers_from_cache"],
+        "day2_api_requests": day2_counts["api_requests"],
+        "day2": day_meta(day2, scenes["day2"]),
+        "max_prompt_tokens_estimated": max(morning.max_prompt_tokens, night.m.max_prompt_tokens,
+                                           day2.max_prompt_tokens),
         "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
         "run_seconds": round(seconds, 1),
         "story": os.path.relpath(out_path, HERE).replace("\\", "/"),
         "story_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
     }
     say(f"\nwrote {meta['story']}")
-    for k in ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
-              "routine_decisions", "lines_spoken", "inner_moments", "lull_moments", "private_talks",
-              "trip_minute", "trip_acts",
-              "max_prompt_tokens_estimated",
-              "max_prompt_tokens_counted_by_api", "run_seconds",
-              "story_sha256"):
+    for k in ("api_requests", "answers_live", "answers_from_cache"):
+        say(f"  {k}: {meta[k]}")
+    for k in DAY_KEYS:
+        say(f"  day1 {k}: {meta['day1'][k]}")
+    for k in ("night_asks", "night_api_requests", "leavers", "outcome"):
+        say(f"  {k}: {meta[k]}")
+    say(f"  night house: {night.house}; away: {meta['night']['away']}")
+    for k in DAY_KEYS:
+        say(f"  day2 {k}: {meta['day2'][k]}")
+    for k in ("day2_asks", "day2_api_requests", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api",
+              "run_seconds", "story_sha256"):
         say(f"  {k}: {meta[k]}")
     if replay:
         if not os.path.exists(story_path):
@@ -123,8 +198,9 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         say(f"  byte for byte against {os.path.relpath(story_path, HERE)}: "
             f"{'IDENTICAL' if same else 'DIFFERS'}")
         return meta, 0 if same else 1
+    transcript = {"day1": morning.transcript, "night": night.transcript(), "day2": day2.transcript}
     with open(os.path.join(runs_dir, f"{name}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
-        json.dump(morning.transcript, f, ensure_ascii=False, indent=1)
+        json.dump(transcript, f, ensure_ascii=False, indent=1)
         f.write("\n")
     with open(os.path.join(runs_dir, f"{name}.meta.json"), "w", encoding="utf-8", newline="\n") as f:
         json.dump(meta, f, indent=1)
diff --git a/Prototypes/llm-morning/night.py b/Prototypes/llm-morning/night.py
new file mode 100644
index 0000000..164c426
--- /dev/null
+++ b/Prototypes/llm-morning/night.py
@@ -0,0 +1,661 @@
+"""The night between day 1 and day 2, and what day 2 starts from (reports/night_design.md, §2-§5).
+
+After one plain line for the afternoon, everyone goes to bed in their own room and makes one
+private decision. The rules work out who notices whom: from the rooms, from what carries through
+the walls, and, for whoever is asleep, from a draw weighted by how anxious they are. Whoever
+notices decides once more; a leaver who is stopped answers. The world decides each trip by two
+draws from the seed: what the neighbour's house holds (once per seed) and what the street does to
+whoever crosses it. Nothing in the night is asked of the model but those decisions.
+
+`next_day` then hands day 2 each person as the night left them, with what they carry in: a block
+of facts and conclusions the code writes from what they did, saw or heard.
+"""
+import copy
+import json
+import random
+
+import data
+import world
+from world import NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, estimate_tokens, portions_text
+
+GAP_HUNGER = 0.3            # × hunger_rate, the afternoon and evening (§2)
+NIGHT_HUNGER = 0.1          # × hunger_rate, the night
+CARRY = 3                   # portions one person carries (§4.1)
+CARRY_IN_MAX = 360          # estimated tokens of the carry-in block at most (§5.2)
+HOUSE = [(0.30, 0), (0.65, 2), (0.90, 4), (1.00, 6)]                       # §4.1
+ALONE = [(0.62, "clean"), (0.76, "scare_there"), (0.94, "scare_back"), (1.00, "not_back")]   # §4.2
+GROUP = [(0.70, "clean"), (0.82, "scare_there"), (0.97, "scare_back"), (1.00, "not_back")]
+ROOMMATE = {p: q for owners in data.OWNERS.values() for p in owners for q in owners if q != p}
+OWN_ROOM = {p: room for room, owners in data.OWNERS.items() for p in owners}
+BEDROOMS = tuple(data.OWNERS)
+# "Daniel and Leo in the brothers room, Elena and Mara in the back room", in the family's order.
+BEDS = ", ".join(" and ".join(NAMES[x] for x in data.ORDER if x in owners) + f" in the {data.ROOMS[room]}"
+                 for room, owners in sorted(data.OWNERS.items(),
+                                            key=lambda kv: min(data.ORDER.index(x) for x in kv[1])))
+TRIGGER = "the family is together in the kitchen for the first time since last night"
+
+BEDTIME = [("sleep", "go to sleep"),
+           ("lie_awake", "lie awake in your bed and listen"),
+           ("watch_door", "sit up in the kitchen by the front door until morning, so nobody goes out without "
+                          "you knowing"),
+           ("go_next_door", "wait until the others are asleep, then go out by the front door to the "
+                            "neighbour's house")]
+BED_LINE = {"sleep": "You went to sleep.", "lie_awake": "You lay awake and listened.",
+            "watch_door": "You sat up in the kitchen by the front door.",
+            "go_next_door": "You meant to go to the neighbour's house once the others were asleep."}
+TONIGHT = {"sleep": "you went to sleep.", "lie_awake": "you lay awake and listened.",
+           "watch_door": "you sat up in the kitchen by the front door.",
+           "go_next_door": "you meant to go to the neighbour's house once the others were asleep."}
+
+
+def pick(table, u):
+    return next(v for c, v in table if u < c)
+
+
+def house_portions(u):
+    """What the neighbour's house holds, from its draw."""
+    return pick(HOUSE, u)
+
+
+def street(u, size):
+    """What the street does to a group of `size`: clean, scare_there, scare_back or not_back."""
+    return pick(ALONE if size == 1 else GROUP, u)
+
+
+def outcome_class(st, found):
+    """The row of the outcome table (§4.3), from the street and what the house held when they got there."""
+    if st == "not_back":
+        return "not back by morning"
+    if st == "scare_there":
+        return "back shaken, with nothing"
+    if st == "clean":
+        return "back with food" if found else "back with nothing"
+    return "back shaken, with food" if found else "back shaken, with nothing"
+
+
+def wake_room(pid):
+    """The chance a sleeper wakes when their roommate gets up (§3.1)."""
+    return round(0.30 + 0.40 * data.PEOPLE[pid]["traits"]["anxious"], 3)
+
+
+def wake_door(pid):
+    """The chance a sleeper in a bedroom wakes at the front door, through a wall (§3.1)."""
+    return round(0.10 + 0.20 * data.PEOPLE[pid]["traits"]["anxious"], 3)
+
+
+def him(pid):
+    return data.PRONOUNS[pid]["him"]
+
+
+def he(pid):
+    return data.PRONOUNS[pid]["he"]
+
+
+def quoted(words):
+    """Words in quotes, ending a sentence: the closing stop is added only if the words lack one."""
+    return f'"{words}"' + ("" if words.rstrip()[-1:] in ".!?" else ".")
+
+
+def names(pids):
+    ns = [NAMES[q] for q in pids]
+    return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]
+
+
+class Night:
+    """One night. `draws` forces named draws (tests): "order" (a list of leavers), "house",
+    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed."""
+
+    def __init__(self, day1, oracle, draws=None):
+        self.day1 = day1
+        self.oracle = oracle
+        self.seed = day1.seed
+        self.draws = dict(draws or {})
+        # Day 1's rules and lines, on copies of its people: day 1 itself is left as it ended.
+        self.m = copy.copy(day1)
+        self.m.people = copy.deepcopy(day1.people)
+        self.m.max_prompt_tokens = 0
+        self.people = self.m.people
+        self.portions = day1.portions
+        self.house = self.house_left = self.house_u = None
+        self.decisions = []         # every night decision, in order
+        self.noticing = []          # every check of who notices whom, in order
+        self.story = []             # ("decision", d) | ("noticing", n) | ("text", line), in order
+        self.groups = []
+        self.away = set()
+        self.leavers = []           # everyone who went out, in order
+        self.lines = {p: [] for p in data.ORDER}          # night lines for the carry-in, with words
+        self.lines_short = {p: [] for p in data.ORDER}    # the same without quoted words
+        self.knows = {p: [] for p in data.ORDER}          # who they know went out, in order
+        self.visit = {}             # goer -> {"got_in", "found", "took"}
+        self.choices, self.where, self.awake, self.reacted = {}, {}, {}, set()
+        self.bedtime_hunger, self.rooms_at_bedtime, self.state_at_bedtime = {}, {}, {}
+        self.morning_hunger = {}
+
+    # ---------- chance ----------
+    def u(self, name):
+        if name in self.draws:
+            return self.draws[name]
+        return random.Random(f"{self.seed}:night:{name}").random()
+
+    def order(self):
+        """Everyone, in the order they would leave: lowest draw first."""
+        if "order" in self.draws:
+            return list(self.draws["order"])
+        rng = random.Random(f"{self.seed}:night:order")
+        draw = {q: rng.random() for q in data.ORDER}
+        return sorted(data.ORDER, key=draw.get)
+
+    # ---------- lines ----------
+    def line(self, pid, full, short=None):
+        self.lines[pid].append(full)
+        self.lines_short[pid].append(full if short is None else short)
+
+    def text(self, line):
+        self.story.append(("text", line))
+
+    # ---------- asking ----------
+    def ask(self, pid, kind, now, opts, fallback):
+        """One night decision. Returns (option id, words)."""
+        p = self.people[pid]
+        prompt = self.m.prompt_for(p, None, opts, night=now)
+        d = {"person": pid, "ask": kind, "where": self.where.get(pid, OWN_ROOM[pid]), "now": list(now),
+             "options": [o.id for o in opts]}
+        seen = p.levels()
+        text = self.oracle.ask(NIGHT_SYSTEM, prompt)
+        p.seen = seen
+        choice, why = self.m.parse(text, opts)
+        byid = {o.id: o for o in opts}
+        if choice is None:
+            d.update(mode="fallback", invalid=why, option=fallback, say=None)
+        else:
+            if not byid[choice["option"]].speech and choice["say"]:
+                choice["say"], choice["dropped_line"] = None, True     # words only for speech at night
+            d.update(mode="model", **choice)
+            self.m.take_answer(p, choice, NIGHT_MINUTE, d)
+        d["label"] = byid[d["option"]].label
+        self.decisions.append(d)
+        self.story.append(("decision", d))
+        return d["option"], d.get("say")
+
+    def notice(self, who, of, how, draw=None, under=None, noticed=True):
+        n = {"who": who, "of": of, "how": how, "awake": draw is None, "draw": draw, "under": under,
+             "noticed": noticed, "where": self.where[who]}
+        self.noticing.append(n)
+        self.story.append(("noticing", n))
+
+    # ---------- the night ----------
+    def run(self):
+        for p in self.people.values():                                  # the gap (§2)
+            p.hunger = min(1.0, p.hunger + GAP_HUNGER * p.sheet["hunger_rate"])
+            p.room = OWN_ROOM[p.id]
+            p.activity = {"kind": "idle", "label": "in bed"}
+        self.bedtime_hunger = {q: self.people[q].hunger for q in data.ORDER}
+        self.rooms_at_bedtime = {q: self.people[q].room for q in data.ORDER}
+        self.state_at_bedtime = {
+            q: [json.dumps({t: [g.strength, g.events] for t, g in p.grudges.items()}), p.suspicion.state(), p.guilt]
+            for q, p in self.people.items()}
+        for q in data.ORDER:                                            # bedtime (§3.2)
+            room = OWN_ROOM[q]
+            r = ROOMMATE[q]
+            now = ["Now it is night. " + data.GAP,
+                   f"Everyone has gone to bed in their own room: {BEDS}.",
+                   f"You are in the {data.ROOMS[room]}, in your bed. {NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.",
+                   f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]
+            opts = [Option(i, label) for i, label in BEDTIME]
+            choice, _ = self.ask(q, "bedtime", now, opts, "sleep")
+            self.choices[q] = choice
+            self.where[q] = "kitchen" if choice == "watch_door" else room
+            self.awake[q] = choice != "sleep"
+            self.people[q].tonight.append(TONIGHT[choice])
+            self.line(q, f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}")
+        self.house_u = self.u("house")
+        self.house = self.house_left = house_portions(self.house_u)
+        pending = [q for q in self.order() if self.choices[q] == "go_next_door"]
+        while pending:
+            self.leave(pending.pop(0), pending)
+        for p in self.people.values():                                  # the rest of the night
+            if p.id in self.away:
+                p.room = None
+                continue
+            p.hunger = min(1.0, p.hunger + NIGHT_HUNGER * p.sheet["hunger_rate"])
+            p.room = OWN_ROOM[p.id]
+        self.morning_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
+        return self
+
+    def leave(self, L, pending):
+        """L gets up to go: who notices, who stops or joins, the street, the return (§3.3)."""
+        room = OWN_ROOM[L]
+        group = [L]
+        before = {}                 # joiner -> where they were before joining
+        self.text(f"{NAMES[L]} gets up to go to the neighbour's house.")
+        seen_by = set()
+
+        def join(P):
+            before[P] = self.where[P]
+            group.append(P)
+            if P in pending:
+                pending.remove(P)
+            self.knows[P].append(L)
+
+        def back_to_bed():
+            self.where[L] = room
+            for P in group[1:]:
+                self.where[P] = before[P]
+            self.text(f"{NAMES[L]} goes back to bed" + (f", and {names(group[1:])} with {him(L)}." if group[1:] else "."))
+
+        # 1. L gets up: the roommate.
+        R = ROOMMATE[L]
+        if self.where.get(R) == room:
+            awake = self.awake[R]
+            if awake:
+                self.notice(R, L, "room")
+                noticed = True
+            else:
+                draw = self.u(f"wake:{L}:{R}")
+                noticed = draw < wake_room(R)
+                self.notice(R, L, "room", draw, wake_room(R), noticed)
+            if noticed:
+                self.awake[R] = True
+                seen_by.add(R)
+                self.knows[R].append(L)
+                self.line(R, f"In the night {NAMES[L]} got up in the dark and left the room toward the kitchen and the "
+                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).")
+                if R not in self.reacted:
+                    self.reacted.add(R)
+                    now = [f"Now it is night, in the {data.ROOMS[room]}. "
+                           + ("You were lying awake." if awake else "You were asleep and woke."),
+                           f"{NAMES[L]} has got up in the dark and is leaving the room quietly, toward the kitchen "
+                           f"and the front door."]
+                    stop = self.react_seen(R, L, now, pending, join)
+                    if stop and not self.answer(L, [stop], room, group):
+                        back_to_bed()
+                        return
+        # 2. L passes through the kitchen: whoever sits up by the front door.
+        stops = []
+        for S in data.ORDER:
+            if self.where.get(S) != "kitchen" or S in group:
+                continue
+            self.notice(S, L, "door watch")
+            seen_by.add(S)
+            self.knows[S] += [x for x in group if x not in self.knows[S]]
+            who = names(group)
+            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).")
+            if S not in self.reacted:
+                self.reacted.add(S)
+                now = ["Now it is night. You are sitting up in the kitchen by the front door.",
+                       f"{who} {'has' if len(group) == 1 else 'have'} come into the kitchen in the dark and "
+                       f"{'is' if len(group) == 1 else 'are'} going to the front door."]
+                stop = self.react_seen(S, L, now, pending, join)
+                if stop:
+                    stops.append(stop)
+        if stops and not self.answer(L, stops, "kitchen", group):
+            back_to_bed()
+            return
+        # 3. The front door opens: everyone in a bedroom who has not seen L go.
+        for P in data.ORDER:
+            if self.where.get(P) not in BEDROOMS or P in group or P in seen_by:
+                continue
+            awake = self.awake[P]
+            if awake:
+                self.notice(P, L, "front door")
+                heard = True
+            else:
+                draw = self.u(f"door:{L}:{P}")
+                heard = draw < wake_door(P)
+                self.notice(P, L, "front door", draw, wake_door(P), heard)
+            if not heard:
+                continue
+            self.awake[P] = True
+            self.line(P, f"In the night you {'' if awake else 'woke and '}heard the front door being opened. "
+                         f"You did not see who.")
+            if P in self.reacted:
+                continue
+            self.reacted.add(P)
+            now = [f"Now it is night, in the {data.ROOMS[self.where[P]]}. "
+                   + ("You were lying awake." if awake else "You were asleep and woke."),
+                   "From the kitchen comes the sound of the front door being opened. You cannot see who it is."]
+            self.react_heard(P, L, now, pending, join, group)
+        # 4. The street.
+        for P in group:
+            self.where[P] = "out"
+        self.leavers += group
+        self.trip(L, group)
+
+    def react_seen(self, P, L, now, pending, join):
+        """P sees L leave (roommate or door sitter). Returns (P, words) if P tells L not to go."""
+        n = NAMES[L]
+        if P in pending:            # P meant to go too
+            opts = [Option(f"go_with_{L}", f"get up and go with {n} to the neighbour's house"),
+                    Option(f"stop_{L}", f"tell {n}, low, to stay home, and go yourself instead", True),
+                    Option(f"let_{L}_go", f"let {n} go, and go yourself later, alone"),
+                    Option("stay_home", f"let {n} go, and stay in bed yourself after all")]
+            fallback = f"let_{L}_go"
+        else:
+            opts = [Option(f"let_{L}_go", f"stay where you are and let {n} go without a word"),
+                    Option(f"stop_{L}", f"tell {n}, low, not to go", True),
+                    Option(f"go_with_{L}", f"get up and go with {n} to the neighbour's house")]
+            fallback = f"let_{L}_go"
+        waiting = P in pending
+        choice, words = self.ask(P, "reaction", now, opts, fallback)
+        if choice == f"go_with_{L}":
+            join(P)
+            self.line(P, f"You went with {him(L)}.")
+            self.people[P].tonight.append(f"you went with {n}.")
+        elif choice == f"stop_{L}":
+            self.people[P].tonight.append(f"you told {n} not to go.")
+            return P, words
+        elif choice == "stay_home":
+            pending.remove(P)
+            self.line(P, f"You let {him(L)} go, and stayed in bed after all.")
+        elif waiting:
+            self.line(P, f"You let {him(L)} go, to go yourself later.")
+        else:
+            self.line(P, f"You let {him(L)} go without a word.")
+            self.people[P].tonight.append(f"you let {n} go.")
+        return None
+
+    def react_heard(self, P, L, now, pending, join, group):
+        """P hears the front door from a bedroom."""
+        if P in pending:
+            opts = [Option("go_after", "get up now and follow whoever it is out to the neighbour's house"),
+                    Option("go_later", "wait, then go yourself later, alone"),
+                    Option("stay_home", "stay in bed after all")]
+            choice, _ = self.ask(P, "reaction", now, opts, "go_later")
+            if choice == "go_after":
+                join(P)
+                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.")
+            elif choice == "stay_home":
+                pending.remove(P)
+                self.line(P, "You stayed in bed after all.")
+            else:
+                self.line(P, "You waited, to go yourself later.")
+            return
+        opts = [Option("stay_in_bed", "stay in bed"),
+                Option("get_up_and_look", "get up, see whose bed is empty, and wait up by the front door until morning")]
+        choice, _ = self.ask(P, "reaction", now, opts, "stay_in_bed")
+        if choice == "get_up_and_look":
+            gone = [x for x in group]
+            beds = (f"{NAMES[gone[0]]}'s bed was empty" if len(gone) == 1 else
+                    " and ".join(f"{NAMES[x]}'s" for x in gone) + " beds were empty")
+            full = self.lines[P][-1] + f" You got up: {beds}. You waited up by the front door."
+            self.lines[P][-1] = self.lines_short[P][-1] = full
+            self.where[P] = "kitchen"
+            self.knows[P] += [x for x in gone if x not in self.knows[P]]
+        else:
+            self.line(P, "You stayed in bed.")
+
+    def answer(self, L, stops, place, group):
+        """L, told not to go, answers once. Returns True if L goes all the same."""
+        where = (f"Now it is night, in the {data.ROOMS[place]}. You had got up to go to the neighbour's house."
+                 if place != "kitchen" else
+                 "Now it is night, in the kitchen, by the front door. You had got up to go to the neighbour's house.")
+        now = [where] + [f'{NAMES[S]} is up and says to you, low: "{w}"' if w else f"{NAMES[S]} is up and tells you, low, not to go."
+                         for S, w in stops]
+        who = names([S for S, _ in stops])
+        opts = [Option("go_anyway", f"answer {who}, and go out to the neighbour's house all the same", True),
+                Option("stay_home", f"answer {who}, and go back to bed", True)]
+        choice, a = self.ask(L, "answer", now, opts, "go_anyway")
+        goes = choice == "go_anyway"
+        went = "went all the same" if goes else "went back to bed"
+        said = f' You answered: "{a}", and {went}.' if a else f" You {went}."
+        told = " ".join(f"{NAMES[S]} told you, low, not to go: {quoted(w)}" if w else f"{NAMES[S]} told you, low, not to go."
+                        for S, w in stops)
+        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.")
+        He = he(L).capitalize()
+        for S, w in stops:
+            told = f"You told {NAMES[L]}, low, not to go" + (f": {quoted(w)}" if w else ".")
+            answered = f' {He} answered: "{a}", and {went}.' if a else f" {He} {went}."
+            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.")
+        # Low voices: heard, without words, by anyone awake elsewhere; nobody wakes for a whisper.
+        talkers = {L} | {S for S, _ in stops} | set(group)
+        for P in data.ORDER:
+            w = self.where.get(P)
+            if P in talkers or w in (None, "out", place) or not self.awake[P]:
+                continue
+            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.")
+        if not goes:
+            self.people[L].tonight.append("you went back to bed.")
+        return goes
+
+    def trip(self, L, group):
+        """The street and the house decide; then the return (§4)."""
+        u = self.u(f"trip:{L}")
+        st = street(u, len(group))
+        found = self.house_left
+        g = {"leader": L, "members": list(group), "u": u, "street": st, "found": None, "took": 0, "lost": None,
+             "lost_u": None, "shaken": [], "outcome": None}
+        if st in ("clean", "scare_back"):
+            g["found"] = found
+            g["took"] = min(found, CARRY * len(group))
+            self.house_left -= g["took"]
+        if st in ("scare_there", "scare_back"):
+            g["shaken"] = list(group)
+        if st == "not_back":
+            if len(group) == 1:
+                g["lost"] = L
+            else:
+                g["lost_u"] = self.u(f"lost:{L}")
+                g["lost"] = sorted(group)[int(g["lost_u"] * len(group))]
+                g["shaken"] = [x for x in group if x != g["lost"]]
+            self.away.add(g["lost"])
+        g["outcome"] = outcome_class(st, found)
+        self.groups.append(g)
+        back = [x for x in group if x != g["lost"]]
+        k, F = g["took"], g["found"]
+        for P in back:
+            if st == "clean" and F:
+                rest = F - k
+                took = (f"You took {k}; {rest} {'is' if rest == 1 else 'are'} still there." if rest else "You took all of it.")
+                self.line(P, f"You got inside the neighbour's house and found {portions_text(F)} of food. {took} "
+                             f"Nothing troubled you in the street.")
+            elif st == "clean":
+                self.line(P, "You got inside the neighbour's house and found no food there. Nothing troubled you in "
+                             "the street.")
+            elif st == "scare_there":
+                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.")
+            elif st == "scare_back":
+                got = (f"and found {portions_text(F)} of food and took {k}" if F else "but found no food")
+                self.line(P, f"You got inside the neighbour's house {got}. On the way back, something was moving in the "
+                             f"street, and you ran the rest of the way.")
+            else:
+                self.line(P, f"In the street, something was moving. You lost sight of {NAMES[g['lost']]} in the dark "
+                             f"and came back without {him(g['lost'])}.")
+            self.line(P, "You came back in by the front door before dawn"
+                      + (f" and put the {portions_text(k)} on the shelf." if k else "."))
+            self.visit[P] = {"got_in": st in ("clean", "scare_back"), "found": F, "took": k}
+        if not back:
+            return
+        self.portions += k
+        # The return: the front door again.
+        for P in back:
+            self.where[P] = OWN_ROOM[P]
+            self.awake[P] = True
+        carrying = ", carrying food" if k else f", with nothing in {'their' if len(back) > 1 else data.PRONOUNS[back[0]]['his']} hands"
+        shaken = ", and looked shaken" if g["shaken"] else ""
+        alone = " alone" if g["lost"] else ""
+        for P in data.ORDER:
+            w = self.where.get(P)
+            if P in group or w in (None, "out"):
+                continue
+            if w == "kitchen":
+                self.notice(P, L, "return")
+                self.knows[P] += [x for x in back if x not in self.knows[P]]
+                self.line(P, f"Before dawn {names(back)} came back in{alone} by the front door{carrying}{shaken} "
+                             f"(you saw it).")
+            elif self.awake[P]:
+                self.notice(P, L, "return")
+                self.line(P, "Before dawn you heard the front door again. You did not see who.")
+            else:
+                draw = self.u(f"return:{L}:{P}")
+                woke = draw < wake_door(P)
+                self.notice(P, L, "return", draw, wake_door(P), woke)
+                if woke:
+                    self.awake[P] = True
+                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.")
+
+    # ---------- the record ----------
+    def transcript(self):
+        return {"house": self.house, "house_u": self.house_u, "house_left": self.house_left,
+                "portions_before": self.day1.portions, "portions_after": self.portions,
+                "bedtime_hunger": self.bedtime_hunger, "morning_hunger": self.morning_hunger,
+                "choices": self.choices, "leavers": self.leavers, "away": [q for q in data.ORDER if q in self.away],
+                "decisions": [{k: v for k, v in d.items()} for d in self.decisions],
+                "noticing": self.noticing, "groups": self.groups,
+                "lines": self.lines}
+
+
+# ---------- day 2 ----------
+def carry_in(day1, n, p, short=False, minutes=True):
+    """What p carries into day 2 (§5.2): yesterday's facts as p had them, then their own night."""
+    out = [f"Yesterday morning Elena counted the pantry and found one can fewer than she expected "
+           f"({'you did it' if p.id == 'elena' else 'you saw it'})."]
+    c = day1.culprit
+    if p.confessed:
+        sure = next(x for x in p.sure if "you admitted aloud that you took the can" in x)
+        front = sure.split(", in front of ", 1)[1].rstrip(".").split(", ") if ", in front of " in sure else None
+        out.append(f"You admitted at minute {sure[4:6]} that you took the can"
+                   + (f", in front of {names([q for q in data.ORDER if NAMES[q] in front])}." if front else "."))
+    elif p.knows_culprit and p.knows_culprit != p.id:
+        sure = next(x for x in p.sure if " admitted taking the can: " in x)
+        words = sure.split(" admitted taking the can: ", 1)[1].rsplit(" (you heard it)", 1)[0]
+        after = ", after denying it to you" if p.knows_culprit in p.denials_heard else ""
+        out.append(f"{NAMES[p.knows_culprit]} admitted taking the can at minute {p.confession_heard_at:02d}{after}: "
+                   f"{words} (you heard it).")
+    elif c is not None and p.id == c:
+        accusers = [q for q in data.ORDER if q in p.accused_by]
+        out.append("Nobody found out that you ate the can" + (f"; {names(accusers)} accused you." if accusers
+                                                              else ", and nobody named you."))
+    else:
+        out.append("Nobody admitted taking the can, and it was not found.")
+    for x in p.sure:
+        if x[8:].startswith("you finished searching the "):
+            out.append(f"You searched the {x[8 + len('you finished searching the '):].split(':')[0]} at minute "
+                       f"{x[4:6]} and found nothing.")
+    acc = {}
+    for turn in day1.transcript["turns"]:
+        for a in turn["acts"]:
+            if a["option"].startswith("accuse_") and (a["who"] == p.id or p.id in a["audience"]):
+                acc.setdefault((a["who"], a["option"][len("accuse_"):]), []).append(turn["minute"])
+    if acc:
+        parts = []
+        for (a, t), ms in acc.items():
+            times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
+            when = f" (min {', '.join(f'{x:02d}' for x in ms)})" if minutes else ""
+            parts.append(f"{'you' if a == p.id else NAMES[a]} accused {'you' if t == p.id else NAMES[t]}{times}{when}")
+        text = "; ".join(parts)
+        out.append(f"Accusations: {text}.")
+    ate = {}
+    for x in p.sure:
+        if " ate one of the portions" in x:
+            mm, rest = x[4:6], x[8:]
+            ate.setdefault(mm, []).append("you" if rest.startswith("you ate") else rest.split(" ate one")[0])
+    for mm, who in ate.items():
+        mine = "you" in who
+        who = (["You"] if mine else []) + [w for w in who if w != "you"]
+        each = " each" if len(who) > 1 else ""
+        out.append(f"{' and '.join(who)} ate a portion{each} at minute {mm}" + ("." if mine else " (you saw it)."))
+    plan = day1.heard_plan(p)
+    if plan:
+        out.append("About going to the neighbour's house last night, where it was left: "
+                   + plan[len("About going there tonight: "):])
+    out.append(data.GAP)
+    out += (n.lines_short if short else n.lines)[p.id]
+    return ["Yesterday and last night:"] + [f"- {x}" for x in out]
+
+
+def bounded_carry_in(day1, n, p):
+    """The block within CARRY_IN_MAX: the quoted night words go first, then the accusations' minutes."""
+    for short, minutes in ((False, True), (True, True), (True, False)):
+        block = carry_in(day1, n, p, short, minutes)
+        if estimate_tokens("\n".join(block)) <= CARRY_IN_MAX:
+            break
+    return block
+
+
+def neighbour_line(n, pid):
+    """Their "About the neighbour's house:" line on day 2 (§5.3)."""
+    v = n.visit.get(pid)
+    if v:
+        if v["got_in"] and v["found"]:
+            rest = v["found"] - v["took"]
+            left = f", and {rest} {'is' if rest == 1 else 'are'} still there" if rest else ", and none are left there"
+            return (f"About the neighbour's house: you went in last night and found {portions_text(v['found'])}; "
+                    f"you brought back {v['took']}{left}. Outside is dangerous.")
+        if v["got_in"]:
+            return "About the neighbour's house: you went in last night and found no food there. Outside is dangerous."
+        return "About the neighbour's house: you did not get inside last night. Outside is dangerous."
+    known = [x for x in n.knows[pid] if x != pid]
+    if not known:
+        return NEIGHBOUR_UNKNOWN
+    x = known[0]
+    g = next(g for g in n.groups if x in g["members"])
+    if x in n.away:
+        how = " and has not come back"
+    else:
+        how = " and came back with food" if g["took"] else " and came back with nothing"
+    return f"About the neighbour's house: {NAMES[x]} went there last night{how}. Outside is dangerous."
+
+
+def next_day(day1, n, oracle):
+    """Day 2: a Morning of day 5 with each person as the night left them (§5.1)."""
+    m = world.Morning(oracle, day1.seed, day1.scenario, day=5)
+    m.people = n.people
+    m.portions = m.start_portions = n.portions
+    m.away = set(n.away)
+    m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}
+    present = [q for q in data.ORDER if q not in m.away]
+    before, after = n.day1.portions, n.portions
+    for q in data.ORDER:
+        p = m.people[q]
+        m.carry[q] = bounded_carry_in(day1, n, p)
+        m.neighbour[q] = neighbour_line(n, q)
+    brought = {P: g["took"] for g in n.groups for P in g["members"] if g["took"] and P not in m.away}
+    shaken = {P for g in n.groups for P in g["shaken"] if P not in m.away}
+    for q in data.ORDER:
+        p = m.people[q]
+        p.yesterday = {"confessed": p.confessed,
+                       "confession_heard": bool(p.knows_culprit and p.knows_culprit != p.id),
+                       "suspected_at": [mm for mm in p.suspected_at if mm < NIGHT_MINUTE],
+                       "suspected_last_night": any(mm >= NIGHT_MINUTE for mm in p.suspected_at),
+                       "denials": set(p.denials_heard),
+                       "accused_by": set(p.accused_by)}
+        for g in p.grudges.values():
+            g.events = [(e[0], ("yesterday, " + e[1]) if e[2] == "event" else e[1], e[2],
+                         "last night" if e[0] >= NIGHT_MINUTE else "yesterday") for e in g.events]
+            g.last_change = 0
+        p.suspicion.last_fall = 0
+        p.suspected_at = []
+        p.guilt_events = [(mm, "yesterday, " + fact) for mm, fact in p.guilt_events]
+        p.memory, p.said_lines, p.history, p.heard, p.triggers, p.tonight = [], [], [], [], [], []
+        p.trip_heard, p.proposed, p.trip_raised = {}, False, False
+        p.addressed = p.aside_lead = None
+        p.eaten = 0.0
+        p.last_inner = p.last_asked = None
+        p.feeling, p.feeling_until = (("shaken", world.FEELING_SHOWS_FOR_TURNS - 1) if q in shaken else (None, -1))
+        p.activity = {"kind": "idle", "label": "just got up"}
+        if q in m.away:
+            p.room, p.sure = None, []
+            continue
+        p.room = "kitchen"
+        opening = (f"Everyone{' else' if m.away else ''} gets up and comes into the kitchen. Last night the shelf "
+                   f"held {portions_text(before)}; this morning it holds {portions_text(after)}")
+        if q in brought:
+            opening += f": the {brought[q]} you brought back are on it."
+        elif after > before:
+            opening += ". So someone brought food into the house in the night."
+        else:
+            opening += "."
+        for x in data.ORDER:
+            if x in m.away:
+                pro = data.PRONOUNS[x]
+                opening += (f" {NAMES[x]} is not here: {pro['his']} bed is empty and {pro['he']} is nowhere in the "
+                            f"house, so {pro['he']} went out in the night and has not come back.")
+        p.sure = [f"min 00: {opening} (you saw it)"]
+        p.triggers.append((TRIGGER, True))
+        p.seen = p.levels()
+    for q in m.away:
+        m.people[q].seen = m.people[q].levels()
+    # For the story: what each of them had at minute 00 besides the block.
+    m.carried = {q: m.people[q].sure[:1] + m.trip_lines(m.people[q])[:2] for q in present}
+    m.started("kitchen", 0, TRIGGER, False)
+    return m
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index c79e017..06446cf 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -26,8 +26,8 @@ def fold_runs(log):
 
         prev = None
         for i, rec in enumerate(log):
-            d = next(x for x in rec["decisions"] if x["person"] == pid)
-            sig = (d["label"], d["came_of_it"]) if d["mode"] == "routine" else None
+            d = next((x for x in rec["decisions"] if x["person"] == pid), None)   # None: away on day 2
+            sig = (d["label"], d["came_of_it"]) if d and d["mode"] == "routine" else None
             if sig is None or sig != prev:
                 close()
             if sig is not None:
@@ -257,7 +257,15 @@ def render(morning, seed, model_name, command):
         w(f"| {day} | {text} | " + " | ".join(DAYS_KNOWN.get(knew.get(p), "not there") for p in data.ORDER) + " |")
     w(f"| 4 | {data.OPENING} | " + " | ".join("did it" if p == "elena" else "saw it" for p in data.ORDER) + " |")
     w("")
+    body(morning, out, all_d, names, culprit, who, pro)
+    return "\n".join(out)
+
 
+def body(morning, out, all_d, names, culprit, who, pro):
+    """The morning turn by turn, what was said, and how it ended: day 1's, and day 2's too
+    (reports/night_design.md, §8)."""
+    w = out.append
+    log = morning.log
     w("## The morning")
     w("")
     folds = fold_runs(log)
@@ -294,8 +302,10 @@ def render(morning, seed, model_name, command):
         people = [q.name for q in morning.people.values() if q.room == r]
         if people:
             where.append(f"{data.ROOMS[r]}: {', '.join(people)}")
+    if morning.away:
+        where.append("away: " + ", ".join(data.PEOPLE[q]["name"] for q in data.ORDER if q in morning.away))
     eaten = [f"{q.name} {q.eaten:g}" for q in morning.people.values() if q.eaten]
-    w(f"At minute {data.MINUTES}: {'; '.join(where)}. {morning.portions} of {data.PORTIONS} portions "
+    w(f"At minute {data.MINUTES}: {'; '.join(where)}. {morning.portions} of {morning.start_portions} portions "
       f"left; eaten this morning: {', '.join(eaten) if eaten else 'none'}.")
     w("")
     confessed = [d for d in all_d if d["option"] == "confess" and d["mode"] == "model"]
@@ -312,7 +322,9 @@ def render(morning, seed, model_name, command):
     talk = [f"{data.ROOMS[r]} {what} at minute {m:02d} ({why})" for m, r, what, why in morning.convos.log]
     w("- Conversations: " + "; ".join(talk) + ".")
     trip = morning.trip
-    if trip:
+    if morning.day != 4:
+        w("- The food: carried over from yesterday.")
+    elif trip:
         asked = ", ".join(data.PEOPLE[q]["name"] for q in trip["asked"])
         w(f"- The food: came up at minute {trip['minute']:02d} ({'; '.join(trip['why'])}); asked then: {asked}.")
     else:
@@ -358,4 +370,166 @@ def render(morning, seed, model_name, command):
                     else f"{name}: never asked")
     w("- The last feeling each of them named: " + "; ".join(last) + ".")
     w("")
+
+
+# ---------- the night and day 2 (reports/night_design.md, §8) ----------
+NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
+ASKED = {"bedtime": "at bedtime", "reaction": "noticing it", "answer": "told not to go"}
+
+
+def night_decision_line(d, where):
+    head = f"Bedtime, {NAME[d['person']]}" if d["ask"] == "bedtime" else NAME[d["person"]]
+    place = f" ({where}, {ASKED[d['ask']]})" if d["ask"] != "bedtime" else f" ({where})"
+    if d["mode"] == "fallback":
+        return (f"- **{head}**{place}. **FALLBACK**: the model's answer could not be used ({d['invalid']}), so "
+                f"the rules chose: **{d['label']}**.")
+    said = f", saying {quoted(d['say'])}" if d.get("say") else ""
+    dropped = " (its words were dropped: only speech has words at night)" if d.get("dropped_line") else ""
+    return (f"- **{head}**{place}. **Chose: {d['label']}**{said}{dropped} (one of {len(d['options'])} options). "
+            f"Feeling: *{d['feeling']}*. Reason: {quoted(d['reason'])} Suspects: {d['suspects']}, so "
+            f"{d['suspects_now']}. Angry at: {d['angry_at']}; {d['grudge_note']}.")
+
+
+def noticing_line(n):
+    who, of = NAME[n["who"]], NAME[n["of"]]
+    place = "by the front door" if n["where"] == "kitchen" else f"in the {data.ROOMS[n['where']]}"
+    draw = f" (draw {n['draw']:.3f}; wakes under {n['under']:.2f})" if n["draw"] is not None else ""
+    if n["how"] == "door watch":
+        return f"- Noticing: {who}, sitting up {place}, sees {of} come to the front door."
+    if n["how"] == "room":
+        if n["draw"] is None:
+            return f"- Noticing: {who}, awake {place}, sees {of} get up."
+        return f"- Noticing: {who}, asleep {place}, {'wakes and sees' if n['noticed'] else 'does not wake as'} {of} get{'' if n['noticed'] else 's'} up{draw}."
+    if n["how"] == "front door":
+        if n["draw"] is None:
+            return f"- Noticing: {who}, awake {place}, hears the front door open."
+        return f"- Noticing: {who}, asleep {place}, {'wakes at' if n['noticed'] else 'sleeps through'} the front door{draw}."
+    if n["where"] == "kitchen":
+        return f"- Noticing: {who}, {place}, sees who comes back."
+    if n["draw"] is None:
+        return f"- Noticing: {who}, awake {place}, hears the front door again."
+    return f"- Noticing: {who}, asleep {place}, {'wakes at' if n['noticed'] else 'sleeps through'} the front door again{draw}."
+
+
+def place_of(where):
+    return "by the front door" if where == "kitchen" else data.ROOMS[where]
+
+
+def render_night(n):
+    """The night: bedtime, who noticed whom with each draw, the street and the house."""
+    import night as night_mod
+    out = []
+    w = out.append
+    w("# The night")
+    w("")
+    w(f"{data.GAP} Before bed, hunger rose by {night_mod.GAP_HUNGER} × each person's hunger rate, and by "
+      f"{night_mod.NIGHT_HUNGER} × more in the night. Everyone went to bed in their own room: {night_mod.BEDS}. "
+      f"Each of them was asked one private decision. Whoever was awake saw or heard what happened near them; "
+      f"whoever was asleep woke only on a draw under their threshold (roommate getting up: 0.30 + 0.40 × "
+      f"anxious; the front door through a wall: 0.10 + 0.20 × anxious). Whoever noticed someone leave was "
+      f"asked once more, and a leaver told not to go answered. Nothing else in the night was asked of the model.")
+    w("")
+    w("| | " + " | ".join(NAME[p] for p in data.ORDER) + " |")
+    w("|---|" + "---|" * len(data.ORDER))
+    w("| Hunger at bedtime | " + " | ".join(f"{n.bedtime_hunger[p]:.2f} ({hunger_words(n.bedtime_hunger[p])})"
+                                           for p in data.ORDER) + " |")
+    w("| Wakes when the roommate gets up | " + " | ".join(f"{night_mod.wake_room(p):.2f}" for p in data.ORDER) + " |")
+    w("| Wakes at the front door | " + " | ".join(f"{night_mod.wake_door(p):.2f}" for p in data.ORDER) + " |")
+    w("")
+    w("## Bedtime")
+    w("")
+    items = list(n.story)
+    bedtime = [x for x in items if x[0] == "decision" and x[1]["ask"] == "bedtime"]
+    for _, d in bedtime:
+        w(night_decision_line(d, place_of(d["where"])))
+    w("")
+    w("## In the night")
+    w("")
+    rest = [x for x in items if not (x[0] == "decision" and x[1]["ask"] == "bedtime")]
+    if not rest:
+        w("Nobody got up. The night passed.")
+    order = n.order()
+    w("The order in which anyone who meant to go would get up: " + ", ".join(NAME[p] for p in order) + ".")
+    w("")
+    for kind, x in rest:
+        if kind == "text":
+            w(f"- {x}")
+        elif kind == "noticing":
+            w(noticing_line(x))
+        else:
+            w(night_decision_line(x, place_of(x["where"])))
+    w("")
+    w("## The neighbour's house and the street")
+    w("")
+    w(f"- The neighbour's house held {n.house} portion{'s' if n.house != 1 else ''} (draw {n.house_u:.3f}: 0 under "
+      f"0.30, 2 under 0.65, 4 under 0.90, else 6).")
+    if not n.groups:
+        w("- Nobody went out.")
+    for g in n.groups:
+        who = " and ".join(NAME[p] for p in g["members"])
+        alone = len(g["members"]) == 1
+        cut = ("clean under 0.62, scared on the way there under 0.76, scared on the way back under 0.94, else not "
+               "back" if alone else "clean under 0.70, scared on the way there under 0.82, scared on the way back "
+               "under 0.97, else one of them not back")
+        lost = (f" The lost draw {g['lost_u']:.3f} chose {NAME[g['lost']]}." if g.get("lost_u") is not None else "")
+        took = (f" Found {g['found']} portion{'s' if g['found'] != 1 else ''} there; took {g['took']}."
+                if g["found"] is not None else " Did not get inside.")
+        w(f"- {who}, {'alone' if alone else 'together'}: street draw {g['u']:.3f} → {g['street']} ({cut}).{took}{lost} "
+          f"Outcome: **{g['outcome']}**.")
+    w("")
+    w("## By morning")
+    w("")
+    away = ", ".join(NAME[p] for p in data.ORDER if p in n.away) or "nobody"
+    w(f"- The shelf held {n.day1.portions} portion{'s' if n.day1.portions != 1 else ''} last night and holds "
+      f"{n.portions} now. Not back: {away}.")
+    w("")
+    w("| | " + " | ".join(NAME[p] for p in data.ORDER) + " |")
+    w("|---|" + "---|" * len(data.ORDER))
+    w("| Hunger by morning | " + " | ".join("away" if n.morning_hunger[p] is None else
+                                            f"{n.morning_hunger[p]:.2f} ({hunger_words(n.morning_hunger[p])})"
+                                            for p in data.ORDER) + " |")
+    w("")
+    return "\n".join(out) + "\n"
+
+
+def render_day2(morning):
+    """Day 2 (house day 5): what each of them carried in, then the morning as day 1's."""
+    log = morning.log
+    for rec in log:
+        for d in rec["decisions"]:
+            d["minute"] = rec["minute"]
+    all_d = [d for rec in log for d in rec["decisions"]]
+    out = []
+    w = out.append
+    culprit = morning.culprit
+    who = data.PEOPLE[culprit]["name"] if culprit else None
+    pro = data.PRONOUNS[culprit] if culprit else None
+    names = [NAME[p] for p in data.ORDER]
+    n_model = sum(d["mode"] == "model" for d in all_d)
+    n_fall = sum(d["mode"] == "fallback" for d in all_d)
+    n_rout = sum(d["mode"] == "routine" for d in all_d)
+    w("# The next morning (day 5)")
+    w("")
+    w(f"The same rules as day 1, from the people as the night left them. **{len(all_d)} decisions**: {n_model} by "
+      f"the model, {n_fall} fallbacks, {n_rout} routine. {len(morning.said)} lines were spoken aloud. The shelf held "
+      f"{morning.start_portions} portion{'s' if morning.start_portions != 1 else ''} at minute 00.")
+    w("")
+    w("## What each of them carried in")
+    w("")
+    w("Each block is printed as their prompts carry it, with the opening of the morning and their lines about the "
+      "food and the neighbour's house.")
+    w("")
+    for p in data.ORDER:
+        if p in morning.away:
+            w(f"**{NAME[p]}**: away, not back from the night.")
+            w("")
+            continue
+        w(f"**{NAME[p]}**")
+        w("")
+        w("```")
+        out.extend(morning.carry[p])
+        out.extend(morning.carried[p])
+        w("```")
+        w("")
+    body(morning, out, all_d, names, culprit, who, pro)
     return "\n".join(out)
diff --git a/Prototypes/llm-morning/talk.py b/Prototypes/llm-morning/talk.py
index 0053aa9..6c47db6 100644
--- a/Prototypes/llm-morning/talk.py
+++ b/Prototypes/llm-morning/talk.py
@@ -14,12 +14,14 @@ def act_of(option):
     reassuring one person or everyone is `reassure`, starting or carrying on a search is
     `search`. The target is a person for accuse, reassure, sit, back and object, a room for go.
     The trip's options (reports/trip_design.md, §3.3): proposing it, volunteering, objecting
-    to it or to one person going, backing one person to go, and declining to go."""
+    to it or to one person going, backing one person to go, and declining to go. Day 2 words them
+    anew (reports/night_design.md, §6) with the same kinds: nobody_goes, keep_<q>_home, send_<q>,
+    still_going (a restated offer) and refuse_to_go."""
     if option == "ask_who":
         return "ask", None
     if option == "propose_trip":
         return "propose", None
-    if option == "object_trip":
+    if option in ("object_trip", "nobody_goes"):
         return "object", None
     if option == "say_other":
         return "say", None
@@ -27,6 +29,14 @@ def act_of(option):
         return "reassure", None
     if option == "keep_searching":
         return "search", None
+    if option == "still_going":
+        return "volunteer", None
+    if option == "refuse_to_go":
+        return "decline", None
+    if option.startswith("keep_") and option.endswith("_home"):
+        return "object", option[len("keep_"):-len("_home")]
+    if option.startswith("send_"):
+        return "back", option[len("send_"):]
     for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object"):
         if option.startswith(prefix + "_"):
             return prefix, option[len(prefix) + 1:]
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index fd7ac49..cd774b8 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -8,6 +8,7 @@ import importlib.util
 import io
 import json
 import os
+import random
 import re
 import shutil
 import subprocess
@@ -208,16 +209,16 @@ class FakeMorningTest(unittest.TestCase):
         self.assertIn("## The morning", story)
         self.assertIn("## What was said", story)
         self.assertLessEqual(meta["api_requests"], 150)
-        self.assertGreater(meta["model_decisions"], 0)
-        self.assertGreater(meta["routine_decisions"], 0)
+        self.assertGreater(meta["day1"]["model_decisions"], 0)
+        self.assertGreater(meta["day1"]["routine_decisions"], 0)
 
     def test_every_kind_of_broken_answer_falls_back_to_the_rules(self):
         # Every answer broken: the four kinds land at minute 0, where everyone can speak.
         (meta, code), _ = fake_morning(self.dirs, client=FakeClient(invalid_every=1))
         self.assertEqual(code, 0)
-        self.assertEqual(meta["model_decisions"], 0)
+        self.assertEqual(meta["day1"]["model_decisions"], 0)
         story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.md"))
-        self.assertGreater(meta["fallbacks"], 0)
+        self.assertGreater(meta["day1"]["fallbacks"], 0)
         for why in ("(not JSON)", "was not offered)", "(no `reason`)", "is speech but no words were given)"):
             self.assertIn(why, story)
 
@@ -258,6 +259,9 @@ class FakeMorningTest(unittest.TestCase):
         prompts = cached_prompts(self.dirs)
         self.assertTrue(prompts)
         for p in prompts:
+            # The night's and day 2's prompts have their own bounds (reports/night_design.md, §9 T12).
+            if "\nNow it is night" in p or CARRY_HEAD in p:
+                continue
             # The estimate tracked the API's own count closely in the first runs (1,250 against
             # 1,252); the real counts of the real runs are reported with them. The trip block
             # sits outside the budget (reports/trip_design.md, §2.5).
@@ -798,7 +802,7 @@ class ScenarioTest(unittest.TestCase):
             story = read(os.path.join(self.dirs.runs, f"{scenario}-seed1.md"))
             self.assertIn(f"# The morning as a story: {scenario}, rules and a language model, seed 1", story)
             tr = json.loads(read(os.path.join(self.dirs.runs, f"{scenario}-seed1.transcript.json")))
-            self.assertEqual((tr["scenario"], tr["culprit"]), (scenario, data.culprit(scenario)))
+            self.assertEqual((tr["day1"]["scenario"], tr["day1"]["culprit"]), (scenario, data.culprit(scenario)))
             if scenario != data.DEFAULT_SCENARIO:
                 self.assertIn(f"`python morning.py --scenario {scenario} --seed 1 --fake`", story)
 
@@ -1044,6 +1048,7 @@ class DecisionFormatTest(unittest.TestCase):
 
         def keys(path):
             tr = json.loads(read(path))
+            tr = tr.get("day1", tr)
             return {k for turn in tr["turns"] for a in turn["acts"] for k in a}
         # v9 adds one key to every act, `lull` (reports/lull_design.md, §3), and v11 another,
         # `trip_moment` (reports/trip_design.md, §4.1). `aside` is an older key, on acts that take
@@ -1198,10 +1203,13 @@ class WitnessScenarioTest(unittest.TestCase):
                 self.assertEqual(len(lines), 1)
                 self.assertTrue(lines[0].endswith(" " + NOTE), lines[0])
                 self.assertEqual([x for x in p.splitlines() if x.startswith("About the can")], lines)
+                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3).
                 self.assertRegex(lines[0][:-len(" " + NOTE)],
                                  r"^About the can(: you have not settled on who took it\."
                                  r"| \([a-z ]+\): you thought \w+ took it, at minutes? [\d, and]+\."
-                                 r"|: \w+ admitted taking it at minute \d\d\.)$")
+                                 r"| \([a-z ]+\): you thought \w+ took it(, (and )?(yesterday at minutes? [\d, and]+"
+                                 r"|last night|this morning at minutes? [\d, and]+))*\."
+                                 r"|: \w+ admitted taking it( yesterday,)? at minute \d\d\.)$")
                 for words in ("Daniel eats a can", "you ate it yourself", "On your conscience"):
                     self.assertNotIn(words, p)
             else:
@@ -1534,9 +1542,9 @@ class LullTest(unittest.TestCase):
         for seed in (1, 2, 3):
             (meta, code), out = fake_morning(self.dirs, seed=seed)
             self.assertEqual(code, 0, out)
-            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))
+            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))["day1"]
             self.assertTrue(all("lull" in a and a["lull"] is None for turn in tr["turns"] for a in turn["acts"]))
-            self.assertEqual(meta["lull_moments"], 0, seed)
+            self.assertEqual(meta["day1"]["lull_moments"], 0, seed)
             story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
             self.assertNotIn("**Lull**, nothing said or done in the ", story)
             self.assertIn("lull_moments: 0", out)
@@ -2135,8 +2143,10 @@ class TripTest(unittest.TestCase):
         for seed in (1, 2, 3):
             (meta, code), out = fake_morning(self.dirs, seed=seed)
             self.assertEqual(code, 0, out)
-            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))
+            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))["day1"]
             story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
+            story = story[:story.index("# The night\n")]
+            meta = meta["day1"]
             self.assertEqual(meta["trip_minute"], tr["trip"]["minute"])
             acts = [a for turn in tr["turns"] for a in turn["acts"]]
             trips = [a for a in acts if TRIP_IDS.match(a["option"])]
@@ -2197,6 +2207,847 @@ class TripTest(unittest.TestCase):
             self.assertIn("0 API calls", done.stdout)
 
 
+V11_RUNS = os.path.join(HERE, "runs", "v11")
+V11_CACHE = os.path.join(HERE, "cache", "v11")
+V11_SERVED = {1: 55, 2: 53, 3: 45}
+NIGHT_SYSTEM_TEXT = (
+    "You decide what one person in a family does tonight. You get who they are, what they remember, what they "
+    "know now, and the options open to them. They know only what is in their memory. Choose exactly one option "
+    "id from the list. If the option is marked (speech), `say` must hold the exact words they say, in a low "
+    "voice, in their own voice, one or two short sentences. For any other option `say` is null. `feeling` names "
+    "what they feel right now in one or two words. `reason` is their reason in one sentence, as they would think "
+    "it. `suspects` is who they now believe took the can, and `angry_at` is who they are angry with right now: "
+    "each is one of \"Daniel\", \"Elena\", \"Leo\", \"Mara\" or \"nobody\". Reply with JSON only: "
+    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
+    '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}')
+BEDTIME_OPTIONS = ("Your options:\n"
+                   "- sleep: go to sleep\n"
+                   "- lie_awake: lie awake in your bed and listen\n"
+                   "- watch_door: sit up in the kitchen by the front door until morning, so nobody goes out "
+                   "without you knowing\n"
+                   "- go_next_door: wait until the others are asleep, then go out by the front door to the "
+                   "neighbour's house")
+GAP = "The afternoon and evening passed in the house. Nobody ate."
+CARRY_HEAD = "Yesterday and last night:"
+CARRY_MAX = 360
+DAY2_TRIP_IDS = re.compile(r"^(propose_trip|volunteer|still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go)$")
+FATE = re.compile(r"\b(dead|die[sd]?|dying|kill\w*|hurt|wound\w*|blood\w*|corpse|injur\w*|bit(e|ten)|attack\w*|"
+                  r"taken)\b", flags=re.I)
+# Nobody wakes, and the house and the street are quiet, when Daniel goes (night_design.md §3.3 draws).
+QUIET = {"wake:daniel:leo": 0.9, "door:daniel:leo": 0.9, "door:daniel:elena": 0.9, "door:daniel:mara": 0.9,
+         "return:daniel:leo": 0.9,
+         "return:daniel:elena": 0.9, "return:daniel:mara": 0.9, "house": 0.1, "trip:daniel": 0.1}
+
+
+class NightScripted:
+    """A model for the night and day 2. prefs[who] lists option ids in order of preference: the
+    first one offered is chosen, with words if it is speech. Otherwise the first option of the
+    night (sleep, let them go, stay in bed, go anyway), or `silent` by day."""
+
+    def __init__(self, prefs=None, angry=None):
+        self.prefs, self.angry = prefs or {}, angry or {}
+        self.requests = 0
+        self.prompts = []           # (minute or "night", who, prompt)
+
+    def generate(self, system, prompt):
+        self.requests += 1
+        who = re.match(r"You are (\w+),", prompt).group(1).lower()
+        m = re.search(r"^Now, minute (\d+)", prompt, flags=re.M)
+        where = int(m.group(1)) if m else "night"
+        block = prompt.split("Your options:")[-1]
+        options = re.findall(r"^- (\w+):", block, flags=re.M)
+        speech = set(re.findall(r"^- (\w+): \(speech\)", block, flags=re.M))
+        self.prompts.append((where, who, prompt))
+        choice = next((o for o in self.prefs.get(who, []) if o in options),
+                      "silent" if "silent" in options else options[0])
+        return json.dumps({"option": choice, "say": f"Words of {who} {self.requests}." if choice in speech else None,
+                           "feeling": "tense", "reason": "Scripted.", "suspects": "nobody",
+                           "angry_at": self.angry.get(who, "nobody")})
+
+    def night_prompts(self, who=None):
+        return [p for w, x, p in self.prompts if w == "night" and (who is None or x == who)]
+
+
+def now_lines(prompt):
+    """The night's `Now` lines: from "Now it is night" to "Your options:"."""
+    lines = prompt.split("\n")
+    end = lines.index("Your options:")
+    start = max(i for i, x in enumerate(lines[:end]) if x.startswith("Now it is night"))
+    return lines[start:end]
+
+
+def option_lines(prompt):
+    return prompt.split("Your options:\n")[-1].split("\n")
+
+
+def without_blocks(prompt):
+    """A day-2 or night prompt without its trip block and its carry-in block."""
+    out, skipping = [], False
+    for line in prompt.split("\n"):
+        if line == CARRY_HEAD:
+            skipping = True
+            continue
+        if skipping and line.startswith("- "):
+            continue
+        skipping = False
+        if line.startswith(("About food:", "About the neighbour's house:", "About going there tonight:")):
+            continue
+        if (TRIP_OPTION_LINE.match(line)
+                or re.match(r"^- (still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go): ", line)
+                or any(line.startswith(f"- Day 2: {s} (") for s in TRIP_DAY2)):
+            continue
+        out.append(line.replace("Outside, and not to be gone to this morning:", "Outside, and not to be gone to:"))
+    return "\n".join(out)
+
+
+def not_pairs(labels):
+    """Pairs of labels whose word sets differ only by "not" or "n't"."""
+    def words(x):
+        return set(re.findall(r"[\w']+", x.lower().replace("n't", " not"))) - {"not"}
+    return [(a, b) for i, a in enumerate(labels) for b in labels[i + 1:] if a != b and words(a) == words(b)]
+
+
+class NightTest(unittest.TestCase):
+    """Time passing: the night after day 1, and day 2 (reports/night_design.md, sections 1 to 8;
+    tests T1 to T14 of section 9)."""
+
+    def setUp(self):
+        self.dirs = Dirs()
+        self.night = importlib.import_module("night")
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def path(self, tag):
+        return os.path.join(self.dirs.root, f"{tag}-{len(os.listdir(self.dirs.root))}.json")
+
+    def v11_day1(self, seed, client=None):
+        """Day 1 of seed N from a copy of its v11 cache; the night and day 2 go to `client`."""
+        path = self.path(f"v11-{seed}")
+        shutil.copy(os.path.join(V11_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"), path)
+        oracle = Oracle(Cache(path), V6_MODEL, seed, client=client, replay=client is None)
+        return Morning(oracle, seed).run(), oracle
+
+    def short_day1(self, client, seed=1):
+        """A day 1 of one silent turn (minute 00), everyone in the kitchen; then `client` answers."""
+        oracle = Oracle(Cache(self.path(f"short-{seed}")), "fake", seed, client=NightScripted())
+        m = Morning(oracle, seed)
+        m.turn(0)
+        m.finish()
+        oracle.client = client
+        return m, oracle
+
+    def night_of(self, prefs, draws=None, seed=1, angry=None):
+        client = NightScripted(prefs, angry)
+        day1, oracle = self.short_day1(client, seed)
+        n = self.night.Night(day1, oracle, draws=draws or {}).run()
+        return day1, n, client, oracle
+
+    def asked(self, n, ask=None):
+        return [(d["person"], d["ask"]) for d in n.decisions if ask is None or d["ask"] == ask]
+
+    def act(self, m, p, option, words, t=0):
+        in_turn(m)
+        opt = next((o for o in m.options_for(p) if o.id == option), None)
+        self.assertIsNotNone(opt, f"{option} not offered to {p.id}: {[o.id for o in m.options_for(p)]}")
+        out = m.apply(p, opt, {"mode": "model", "say": words, "feeling": "tense"}, t, [], new_record())
+        out_of_turn(m)
+        return out
+
+    # T1
+    def test_t1_day1_replays_from_the_v11_caches_byte_for_byte(self):
+        for seed, served in V11_SERVED.items():
+            name = f"daniel_ate_it-seed{seed}"
+            day1, oracle = self.v11_day1(seed)
+            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
+            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
+            self.assertEqual(json.loads(json.dumps(day1.transcript)),
+                             json.loads(read(os.path.join(V11_RUNS, name + ".transcript.json"))), seed)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+            rec = Recorder(oracle)
+            with self.assertRaises(gemini.CacheMiss, msg=seed):
+                self.night.Night(day1, rec).run()
+            self.assertEqual(len(rec.prompts), 1)
+            self.assertTrue(rec.prompts[0].startswith("You are Daniel,"))
+            self.assertIn("\nNow it is night. " + GAP + "\n", rec.prompts[0])
+
+    def test_t1_the_story_begins_with_day1_unchanged(self):
+        (meta, code), out = fake_morning(self.dirs, seed=2)
+        self.assertEqual(code, 0, out)
+        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.md"))
+        oracle = Oracle(Cache(os.path.join(self.dirs.cache, "fake-daniel_ate_it-seed2.json")), "fake", 2, replay=True)
+        day1 = Morning(oracle, 2).run()
+        text = render(day1, 2, "fake", "python morning.py --seed 2 --fake")
+        self.assertTrue(story.startswith(text))
+        self.assertTrue(story[len(text):].startswith("# The night\n"))
+        self.assertIn("\n# The next morning (day 5)\n", story)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
+        self.assertEqual(tr["day1"], json.loads(json.dumps(day1.transcript)))
+        self.assertEqual(set(tr), {"day1", "night", "day2"})
+
+    # T2
+    def test_t2_the_gap(self):
+        day1, oracle = self.v11_day1(1, NightScripted())
+        before = {p: (q.hunger, q.room, json.dumps({t: [g.strength, g.events] for t, g in q.grudges.items()}),
+                      q.suspicion.state(), q.guilt) for p, q in day1.people.items()}
+        n = self.night.Night(day1, oracle).run()
+        self.assertEqual(n.rooms_at_bedtime, {"daniel": "brothers_room", "leo": "brothers_room",
+                                              "elena": "back_room", "mara": "back_room"})
+        for pid in data.ORDER:
+            rate = data.PEOPLE[pid]["hunger_rate"]
+            bed = min(1.0, before[pid][0] + 0.3 * rate)
+            self.assertAlmostEqual(n.bedtime_hunger[pid], bed, places=9, msg=pid)
+            self.assertAlmostEqual(n.people[pid].hunger, min(1.0, bed + 0.1 * rate), places=9, msg=pid)
+        self.assertEqual((round(n.bedtime_hunger["leo"], 3), round(n.people["leo"].hunger, 3)), (0.710, 0.810))
+        self.assertEqual((n.bedtime_hunger["daniel"], n.bedtime_hunger["elena"]), (1.0, 1.0))
+        self.assertEqual(world.hunger_words(n.people["mara"].hunger), "very hungry")
+        self.assertEqual(n.portions, 0)
+        self.assertEqual(n.state_at_bedtime, {p: list(v[2:]) for p, v in before.items()})
+        for p in day1.people.values():                     # day 1 itself is untouched
+            self.assertEqual((p.room, p.hunger), ("kitchen", before[p.id][0]))
+
+    # T3
+    def test_t3_the_bedtime_prompt_exactly(self):
+        self.assertEqual(world.NIGHT_SYSTEM, NIGHT_SYSTEM_TEXT)
+        self.assertEqual(world.SYSTEM, frozen("v11", "world").SYSTEM)
+        self.assertEqual(data.HOUSE_THINGS_NIGHT,
+                         data.HOUSE_THINGS.replace("Outside, and not to be gone to:", "Outside:"))
+        client = NightScripted()
+        day1, oracle = self.v11_day1(1, client)
+        self.night.Night(day1, oracle).run()
+        bedtime = {who: p for w, who, p in client.prompts if w == "night"}
+        self.assertEqual(set(bedtime), set(data.ORDER))
+        self.assertTrue(bedtime["daniel"].endswith(
+            "\nNow it is night. " + GAP + "\n"
+            "Everyone has gone to bed in their own room: Daniel and Leo in the brothers room, Elena and Mara in the "
+            "back room.\nYou are in the brothers room, in your bed. Leo is in his bed.\n"
+            "The kitchen is dark. The shelf holds 0 portions.\n" + BEDTIME_OPTIONS), bedtime["daniel"])
+        self.assertIn("\nYou are in the back room, in your bed. Mara is in her bed.\n", bedtime["elena"])
+        self.assertIn("\nYou are in the back room, in your bed. Elena is in her bed.\n", bedtime["mara"])
+        for p in bedtime.values():
+            self.assertIn(f"The house: {data.HOUSE} {data.HOUSE_THINGS_NIGHT}\n", p)
+            for heading in ("What you are sure of from today:", "What else happened today, most recent last:"):
+                self.assertIn("\n" + heading + "\n", p)
+            self.assertNotIn("this morning:", p)
+            self.assertNotIn("What you have been doing", p)
+            self.assertNotIn("Said and done", p)
+            self.assertIn(TRIP_FOOD, p)                  # the inside lines as at minute 90
+        self.assertIn("\nYour own last words today:\n", bedtime["daniel"])
+        oracle = Oracle(Cache(self.path("one")), "fake", 1, client=FakeClient())
+        m = Morning(oracle, 1)
+        m.turn(0)
+        m.portions = 1
+        m.finish()
+        rec = Recorder(oracle)
+        self.night.Night(m, rec).run()
+        self.assertIn("\nThe kitchen is dark. The shelf holds 1 portion.\n", rec.prompts[0])
+
+    # T4
+    def test_t4_an_awake_roommate_sees_and_is_asked_once(self):
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake"]}, QUIET)
+        self.assertEqual(self.asked(n), [("daniel", "bedtime"), ("elena", "bedtime"), ("leo", "bedtime"),
+                                         ("mara", "bedtime"), ("leo", "reaction")])
+        prompt = client.night_prompts("leo")[-1]
+        self.assertEqual(now_lines(prompt), [
+            "Now it is night, in the brothers room. You were lying awake.",
+            "Daniel has got up in the dark and is leaving the room quietly, toward the kitchen and the front door."])
+        self.assertEqual(option_lines(prompt), ["- let_daniel_go: stay where you are and let Daniel go without a word",
+                                                "- stop_daniel: (speech) tell Daniel, low, not to go",
+                                                "- go_with_daniel: get up and go with Daniel to the neighbour's house"])
+        self.assertEqual(n.lines["mara"], ["Last night you slept in the back room with Elena. You went to sleep."])
+        self.assertEqual(n.lines["elena"], ["Last night you slept in the back room with Mara. You went to sleep."])
+        self.assertEqual(n.lines["leo"], [
+            "Last night you slept in the brothers room with Daniel. You lay awake and listened.",
+            "In the night Daniel got up in the dark and left the room toward the kitchen and the front door "
+            "(you saw it).",
+            "You let him go without a word.",
+            "Before dawn you heard the front door again. You did not see who."])
+
+    def test_t4_a_sleeping_roommate_wakes_only_under_the_threshold(self):
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "wake:daniel:leo": 0.39})
+        self.assertIn(("leo", "reaction"), self.asked(n))
+        self.assertEqual(now_lines(client.night_prompts("leo")[-1])[0],
+                         "Now it is night, in the brothers room. You were asleep and woke.")
+        self.assertIn("In the night Daniel got up in the dark and left the room toward the kitchen and the front "
+                      "door (you woke and saw it).", n.lines["leo"])
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "wake:daniel:leo": 0.41})
+        self.assertNotIn(("leo", "reaction"), self.asked(n))
+        self.assertEqual(n.lines["leo"], ["Last night you slept in the brothers room with Daniel. You went to sleep."])
+
+    def test_t4_the_door_sitter_always_sees(self):
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "elena": ["watch_door"]}, QUIET)
+        self.assertIn(("elena", "reaction"), self.asked(n))
+        self.assertEqual(now_lines(client.night_prompts("elena")[-1]), [
+            "Now it is night. You are sitting up in the kitchen by the front door.",
+            "Daniel has come into the kitchen in the dark and is going to the front door."])
+        self.assertIn("In the night Daniel came into the kitchen and went to the front door (you saw it).",
+                      n.lines["elena"])
+
+    def test_t4_the_front_door_through_a_wall(self):
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "door:daniel:mara": 0.25})
+        self.assertEqual(self.asked(n, "reaction"), [("mara", "reaction")])
+        prompt = client.night_prompts("mara")[-1]
+        self.assertEqual(now_lines(prompt), [
+            "Now it is night, in the back room. You were asleep and woke.",
+            "From the kitchen comes the sound of the front door being opened. You cannot see who it is."])
+        self.assertEqual(option_lines(prompt), ["- stay_in_bed: stay in bed",
+                                                "- get_up_and_look: get up, see whose bed is empty, and wait up by "
+                                                "the front door until morning"])
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "door:daniel:mara": 0.27})
+        self.assertEqual(self.asked(n, "reaction"), [])
+        # Nobody is ever in the bathroom at night, so nothing is heard there.
+        self.assertNotIn("bathroom", set(n.rooms_at_bedtime.values()))
+
+    def test_t4_low_voices_wake_nobody(self):
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"],
+                                    "elena": ["lie_awake"]}, QUIET)
+        self.assertEqual(self.asked(n), [("daniel", "bedtime"), ("elena", "bedtime"), ("leo", "bedtime"),
+                                         ("mara", "bedtime"), ("leo", "reaction"), ("daniel", "answer"),
+                                         ("elena", "reaction")])
+        self.assertIn("In the night you heard low voices from the brothers room.", n.lines["elena"])
+        self.assertFalse([x for x in n.lines["mara"] if "low voices" in x])
+        self.assertIn('You told Daniel, low, not to go: "Words of leo 5." He answered: "Words of daniel 6.", and '
+                      'went all the same.', n.lines["leo"])
+        self.assertIn('Leo told you, low, not to go: "Words of leo 5." You answered: "Words of daniel 6.", and '
+                      'went all the same.', n.lines["daniel"])
+
+    def test_t4_at_most_one_reaction_each(self):
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "elena": ["go_next_door", "go_later"],
+                                    "leo": ["lie_awake"]},
+                                   {**QUIET, "order": ["daniel", "elena"], "wake:elena:mara": 0.9,
+                                    "door:elena:mara": 0.9, "trip:elena": 0.1})
+        reactions = [p for p, _ in self.asked(n, "reaction")]
+        self.assertEqual(reactions.count("leo"), 1)
+        self.assertEqual(sum("heard the front door being opened" in x for x in n.lines["leo"]), 1)
+        for p in data.ORDER:
+            self.assertLessEqual(reactions.count(p), 1, p)
+
+    def test_t4_a_leaver_answers_once_per_stop_moment(self):
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"],
+                                         "elena": ["watch_door", "stop_daniel"]}, QUIET)
+        self.assertEqual([p for p, _ in self.asked(n, "answer")], ["daniel", "daniel"])
+        first, second = client.night_prompts("daniel")[1:3]
+        self.assertEqual(now_lines(first), ["Now it is night, in the brothers room. You had got up to go to the "
+                                            "neighbour's house.", 'Leo is up and says to you, low: "Words of leo 5."'])
+        self.assertEqual(now_lines(second), ["Now it is night, in the kitchen, by the front door. You had got up to "
+                                             "go to the neighbour's house.",
+                                             'Elena is up and says to you, low: "Words of elena 7."'])
+        self.assertEqual(option_lines(first), [
+            "- go_anyway: (speech) answer Leo, and go out to the neighbour's house all the same",
+            "- stay_home: (speech) answer Leo, and go back to bed"])
+
+    def test_t4_staying_home_cancels_the_trip(self):
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door", "stay_home"], "leo": ["lie_awake", "stop_daniel"],
+                                    "elena": ["watch_door"]}, QUIET)
+        self.assertEqual(n.groups, [])
+        self.assertNotIn(("elena", "reaction"), self.asked(n))
+        self.assertEqual(n.people["daniel"].room, "brothers_room")
+        self.assertEqual(n.away, set())
+        self.assertIn('Leo told you, low, not to go: "Words of leo 5." You answered: "Words of daniel 6.", and '
+                      'went back to bed.', n.lines["daniel"])
+
+    def test_t4_going_with_and_after_join_the_group(self):
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake", "go_with_daniel"]},
+                                   {**QUIET, "house": 0.5, "trip:daniel": 0.65})
+        self.assertEqual(len(n.groups), 1)
+        g = n.groups[0]
+        self.assertEqual((g["leader"], g["members"], g["street"]), ("daniel", ["daniel", "leo"], "clean"))
+        self.assertEqual((g["found"], g["took"]), (2, 2))      # alone, 0.65 would have been a scare
+        self.assertEqual(self.night.street(0.65, 1), "scare_there")
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_after"]},
+                                   {**QUIET, "order": ["daniel", "mara"]})
+        self.assertEqual([g["members"] for g in n.groups], [["daniel", "mara"]])
+
+    def test_t4_a_second_leaver_finds_what_the_first_left(self):
+        draws = {**QUIET, "order": ["daniel", "mara"], "trip:mara": 0.1, "wake:mara:elena": 0.9, "door:mara:leo": 0.9}
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_later"]},
+                                   {**draws, "house": 0.95})
+        self.assertEqual([(g["leader"], g["found"], g["took"]) for g in n.groups], [("daniel", 6, 3), ("mara", 3, 3)])
+        self.assertEqual((n.house, n.house_left, n.portions), (6, 0, 8))
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_later"]},
+                                   {**draws, "house": 0.8})
+        self.assertEqual([(g["found"], g["took"]) for g in n.groups], [(4, 3), (1, 1)])
+
+    def test_t4_a_leaver_who_was_waiting(self):
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["go_next_door", "let_daniel_go"]},
+                                        {**QUIET, "order": ["daniel", "leo"], "trip:leo": 0.1})
+        prompt = client.night_prompts("leo")[1]
+        self.assertEqual(now_lines(prompt)[0], "Now it is night, in the brothers room. You were lying awake.")
+        self.assertEqual(option_lines(prompt), [
+            "- go_with_daniel: get up and go with Daniel to the neighbour's house",
+            "- stop_daniel: (speech) tell Daniel, low, to stay home, and go yourself instead",
+            "- let_daniel_go: let Daniel go, and go yourself later, alone",
+            "- stay_home: let Daniel go, and stay in bed yourself after all"])
+        self.assertEqual([g["leader"] for g in n.groups], ["daniel", "leo"])
+        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_later"]},
+                                        {**QUIET, "order": ["daniel", "mara"], "trip:mara": 0.1,
+                                         "wake:mara:elena": 0.9, "door:mara:leo": 0.9})
+        self.assertEqual(option_lines(client.night_prompts("mara")[1]), [
+            "- go_after: get up now and follow whoever it is out to the neighbour's house",
+            "- go_later: wait, then go yourself later, alone", "- stay_home: stay in bed after all"])
+
+    # T5
+    def test_t5_every_night_option_set_passes_the_wording_rule(self):
+        for prefs in ({"daniel": ["go_next_door"], "leo": ["lie_awake"], "elena": ["watch_door"], "mara": ["lie_awake"]},
+                      {"daniel": ["go_next_door"], "leo": ["go_next_door"], "elena": ["go_next_door"]},
+                      {"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"]}):
+            _, n, client, _ = self.night_of(prefs, {"trip:daniel": 0.1, "trip:leo": 0.1, "trip:elena": 0.1})
+            for prompt in client.night_prompts():
+                labels = [x.split(": ", 1)[1].replace("(speech) ", "") for x in option_lines(prompt)]
+                self.assertEqual(not_pairs(labels), [], prompt)
+
+    # T6
+    def test_t6_the_draws_for_seeds_1_to_3(self):
+        expect = {
+            1: (0.050, ["leo", "daniel", "elena", "mara"],
+                {"daniel": 0.297, "elena": 0.955, "leo": 0.008, "mara": 0.456},
+                {"daniel": 0.573, "elena": 0.251, "leo": 0.051, "mara": 0.997}),
+            2: (0.105, ["leo", "elena", "mara", "daniel"],
+                {"daniel": 0.927, "elena": 0.625, "leo": 0.064, "mara": 0.101},
+                {"daniel": 0.777, "elena": 0.393, "leo": 0.185, "mara": 0.212}),
+            3: (0.257, ["leo", "mara", "daniel", "elena"],
+                {"daniel": 0.616, "elena": 0.108, "leo": 0.712, "mara": 0.995},
+                {"daniel": 0.914, "elena": 0.280, "leo": 0.750, "mara": 0.772}),
+        }
+        roommate = {"daniel": "leo", "leo": "daniel", "elena": "mara", "mara": "elena"}
+        for seed, (house, order, trip, wake) in expect.items():
+            day1, oracle = self.short_day1(NightScripted(), seed)
+            n = self.night.Night(day1, oracle)
+            self.assertAlmostEqual(n.u("house"), house, places=3)
+            self.assertEqual(self.night.house_portions(n.u("house")), 0)
+            self.assertEqual(n.order(), order)
+            for q in data.ORDER:
+                self.assertAlmostEqual(n.u(f"trip:{q}"), trip[q], places=3, msg=(seed, q))
+                self.assertAlmostEqual(n.u(f"wake:{q}:{roommate[q]}"), wake[q], places=3, msg=(seed, q))
+        self.assertAlmostEqual(n.u("door:daniel:elena"), 0.564, places=3)
+        self.assertAlmostEqual(n.u("return:daniel:elena"), 0.455, places=3)
+        self.assertAlmostEqual(n.u("lost:daniel"), 0.718, places=3)
+        self.assertEqual([self.night.street(u, 1) for u in (0.297, 0.955, 0.927, 0.625, 0.712)],
+                         ["clean", "not_back", "scare_back", "scare_there", "scare_there"])
+        self.assertEqual([self.night.street(u, 2) for u in (0.955, 0.625)], ["scare_back", "clean"])
+        self.assertEqual({p: (self.night.wake_room(p), self.night.wake_door(p)) for p in data.ORDER},
+                         {"daniel": (0.56, 0.23), "elena": (0.6, 0.25), "leo": (0.4, 0.15), "mara": (0.62, 0.26)})
+
+    def test_t6_the_same_seed_gives_the_same_night(self):
+        stories = []
+        for _ in range(2):
+            dirs = Dirs()
+            try:
+                (_, code), out = fake_morning(dirs, seed=4)
+                self.assertEqual(code, 0, out)
+                story = read(os.path.join(dirs.runs, "daniel_ate_it-seed4.md"))
+                stories.append(story[story.index("# The night\n"):])
+            finally:
+                dirs.cleanup()
+        self.assertEqual(stories[0], stories[1])
+
+    # T7
+    def test_t7_the_outcome_table(self):
+        night = self.night
+        table = {1: {"back with food": 0.434, "back with nothing": 0.186, "back shaken, with nothing": 0.194,
+                     "back shaken, with food": 0.126, "not back by morning": 0.06},
+                 2: {"back with food": 0.49, "back with nothing": 0.21, "back shaken, with nothing": 0.165,
+                     "back shaken, with food": 0.105, "not back by morning": 0.03}}
+        houses = [night.house_portions(random.Random(f"{s}:night:house").random()) for s in range(100000)]
+        trips = [random.Random(f"{s}:night:trip:daniel").random() for s in range(100000)]
+        self.assertAlmostEqual(houses.count(0) / 1e5, 0.30, delta=0.005)
+        for size, probs in table.items():
+            counts = {}
+            for h, u in zip(houses, trips):
+                c = night.outcome_class(night.street(u, size), h)
+                counts[c] = counts.get(c, 0) + 1
+            self.assertEqual(set(counts), set(probs))
+            for c, p in probs.items():
+                self.assertAlmostEqual(counts[c] / 1e5, p, delta=0.005, msg=(size, c))
+
+    def test_t7_carrying_loss_and_the_shelf(self):
+        _, n, _, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "house": 0.95})
+        self.assertEqual((n.groups[0]["found"], n.groups[0]["took"], n.portions, n.house_left), (6, 3, 5, 3))
+        # A pair loses one member, chosen by the lost draw; the other comes back shaken, empty-handed.
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake", "go_with_daniel"]},
+                                           {**QUIET, "house": 0.95, "trip:daniel": 0.98, "lost:daniel": 0.6})
+        g = n.groups[0]
+        self.assertEqual((g["street"], g["lost"], g["took"], g["shaken"]), ("not_back", "leo", 0, ["daniel"]))
+        self.assertEqual(n.away, {"leo"})
+        self.assertEqual(n.portions, 2)
+        day2 = Morning.next_day(day1, n, oracle)
+        self.assertIsNone(day2.people["leo"].room)
+        self.assertEqual(day2.away, {"leo"})
+        # Seeds 4 to 6 (houses 2, 2 and 6), Daniel going alone: seed 5 comes back with food.
+        got = {}
+        for seed in (4, 5, 6):
+            client = NightScripted({"daniel": ["go_next_door"]})
+            day1, oracle = self.short_day1(client, seed)
+            n = self.night.Night(day1, oracle).run()
+            got[seed] = (n.house, n.groups[0]["street"], n.groups[0]["took"], n.portions - day1.portions)
+        self.assertEqual(got, {4: (2, "scare_there", 0, 0), 5: (2, "clean", 2, 2), 6: (6, "scare_there", 0, 0)})
+
+    # T8
+    def test_t8_no_creature_no_fate(self):
+        cases = {
+            "back with food": ({"house": 0.8, "trip:daniel": 0.1},
+                               ["You got inside the neighbour's house and found 4 portions of food. You took 3; 1 is "
+                                "still there. Nothing troubled you in the street.",
+                                "You came back in by the front door before dawn and put the 3 portions on the shelf."]),
+            "all of it": ({"house": 0.5, "trip:daniel": 0.1},
+                          ["You got inside the neighbour's house and found 2 portions of food. You took all of it. "
+                           "Nothing troubled you in the street.",
+                           "You came back in by the front door before dawn and put the 2 portions on the shelf."]),
+            "back with nothing": ({"house": 0.1, "trip:daniel": 0.1},
+                                  ["You got inside the neighbour's house and found no food there. Nothing troubled you "
+                                   "in the street.", "You came back in by the front door before dawn."]),
+            "scared there": ({"house": 0.8, "trip:daniel": 0.7},
+                             ["On the way there, something was moving in the street. You ran back without getting "
+                              "inside.", "You came back in by the front door before dawn."]),
+            "scared back": ({"house": 0.8, "trip:daniel": 0.8},
+                            ["You got inside the neighbour's house and found 4 portions of food and took 3. On the way "
+                             "back, something was moving in the street, and you ran the rest of the way.",
+                             "You came back in by the front door before dawn and put the 3 portions on the shelf."]),
+            "scared back, empty house": ({"house": 0.1, "trip:daniel": 0.8},
+                                         ["You got inside the neighbour's house but found no food. On the way back, "
+                                          "something was moving in the street, and you ran the rest of the way.",
+                                          "You came back in by the front door before dawn."]),
+        }
+        texts = []
+        for name, (draws, lines) in cases.items():
+            day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, **draws})
+            self.assertEqual(n.lines["daniel"][1:], lines, name)
+            day2 = Morning.next_day(day1, n, oracle)
+            texts += [x for p in n.lines.values() for x in p]
+            texts += [x for p in day2.people.values() for x in day2.inside_lines(p) + p.sure]
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake", "go_with_daniel"]},
+                                           {**QUIET, "trip:daniel": 0.98, "lost:daniel": 0.6})
+        self.assertIn("In the street, something was moving. You lost sight of Leo in the dark and came back without "
+                      "him.", n.lines["daniel"])
+        day2 = Morning.next_day(day1, n, oracle)
+        texts += [x for p in n.lines.values() for x in p]
+        texts += [x for p in day2.people.values() if p.room for x in day2.inside_lines(p) + p.sure]
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "trip:daniel": 0.99})
+        self.assertEqual(n.away, {"daniel"})
+        day2 = Morning.next_day(day1, n, oracle)
+        texts += [x for p in day2.people.values() if p.room for x in day2.inside_lines(p) + p.sure]
+        self.assertTrue(texts)
+        for x in texts:
+            self.assertFalse(FATE.search(x), x)
+            if "moving" in x:
+                self.assertTrue("something was moving in the street" in x or "In the street, something was moving." in x,
+                                x)
+
+    # T9
+    def test_t9_the_carry_in_exactly(self):
+        blocks = {}
+        for seed in (1, 2, 3):
+            day1, oracle = self.v11_day1(seed, NightScripted())
+            n = self.night.Night(day1, oracle).run()
+            day2 = Morning.next_day(day1, n, oracle)
+            for p in data.ORDER:
+                blocks[seed, p] = day2.carry[p]
+        count = "- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it)."
+        positions3 = ("- About going to the neighbour's house last night, where it was left: you said nobody should go "
+                      "(min 66); Daniel said Leo should not go (min 66); Elena said nobody should go (min 66); Leo said "
+                      "he will not go (min 69).")
+        self.assertEqual(blocks[3, "mara"], [
+            CARRY_HEAD, count, "- Nobody admitted taking the can, and it was not found.",
+            "- You searched the kitchen at minute 75 and found nothing.", positions3, "- " + GAP,
+            "- Last night you slept in the back room with Elena. You went to sleep."])
+        self.assertEqual(blocks[3, "daniel"][2:4], ["- Nobody found out that you ate the can, and nobody named you.",
+                                                     "- You searched the kitchen at minute 78 and found nothing."])
+        self.assertEqual(blocks[2, "leo"], [
+            CARRY_HEAD, count,
+            "- Daniel admitted taking the can at minute 33, after denying it to you: \"I took it in the night, I'm "
+            "sorry.\" (you heard it).",
+            "- Accusations: Daniel accused you three times (min 03, 09, 12); Mara accused Daniel (min 36).",
+            "- Mara ate a portion at minute 54 (you saw it).",
+            "- About going to the neighbour's house last night, where it was left: Mara said Elena should not go "
+            "(min 48); you said Elena should not go (min 48); Elena said she will not go (min 51); Daniel said nobody "
+            "should go (min 51).",
+            "- " + GAP, "- Last night you slept in the brothers room with Daniel. You went to sleep."])
+        self.assertEqual(blocks[2, "daniel"][3], "- Accusations: you accused Leo three times (min 03, 09, 12); "
+                                                 "Mara accused you (min 36).")
+        self.assertEqual(blocks[1, "daniel"][2], "- You admitted at minute 03 that you took the can, in front of "
+                                                 "Elena, Leo and Mara.")
+        self.assertEqual(blocks[1, "elena"][1], "- Yesterday morning Elena counted the pantry and found one can fewer "
+                                                "than she expected (you did it).")
+        self.assertIn("- Leo and Mara ate a portion each at minute 21 (you saw it).", blocks[1, "elena"])
+        self.assertIn("- You and Mara ate a portion each at minute 21.", blocks[1, "leo"])
+        self.assertIn("- You and Leo ate a portion each at minute 21.", blocks[1, "mara"])
+        for b in blocks.values():
+            self.assertLessEqual(estimate_tokens("\n".join(b)), CARRY_MAX)
+        # Over the bound: the quoted night words go first.
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"]},
+                                           QUIET)
+        n.lines["leo"] = [x.replace("Words of leo 5.", "word " * 400) for x in n.lines["leo"]]
+        day2 = Morning.next_day(day1, n, oracle)
+        self.assertIn("- You told Daniel, low, not to go. He went all the same.", day2.carry["leo"])
+        self.assertLessEqual(estimate_tokens("\n".join(day2.carry["leo"])), CARRY_MAX)
+        self.assertIn('- Leo told you, low, not to go: "Words of leo 5." You answered: "Words of daniel 6.", and went '
+                      'all the same.', day2.carry["daniel"])
+
+    def test_t9_nobody_is_told_what_they_did_not_notice(self):
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, QUIET)
+        day2 = Morning.next_day(day1, n, oracle)
+        for p in ("elena", "leo", "mara"):
+            self.assertFalse([x for x in day2.carry[p][1:] if "Daniel" in x and not x.startswith("- Last night you slept")],
+                             p)
+            self.assertIn("About the neighbour's house: its people left in the first days, so there may be food there. "
+                          "Outside is dangerous.", day2.inside_lines(day2.people[p]))
+        self.assertIn("About the neighbour's house: you went in last night and found no food there. Outside is "
+                      "dangerous.", day2.inside_lines(day2.people["daniel"]))
+
+    # T10
+    def test_t10_what_day2_carries_and_resets(self):
+        client = NightScripted(angry={"leo": "Daniel", "mara": "Daniel"})
+        day1, oracle = self.v11_day1(2, client)
+        n = self.night.Night(day1, oracle).run()
+        day2 = Morning.next_day(day1, n, oracle)
+        for pid, p in day2.people.items():
+            q = n.people[pid]
+            self.assertEqual({t: g.strength for t, g in p.grudges.items()},
+                             {t: g.strength for t, g in q.grudges.items()})
+            for g in p.grudges.values():
+                self.assertEqual(g.last_change, 0)
+                for e in g.events:
+                    self.assertIn(e[3], ("yesterday", "last night"))
+                    if e[2] == "event":
+                        self.assertTrue(e[1].startswith("yesterday, "), e)
+            self.assertEqual(p.suspicion.state(), q.suspicion.state())
+            self.assertEqual(p.suspicion.last_fall, 0)
+            self.assertNotIn("ask_who", {o.id for o in day2.options_for(p)})
+            self.assertEqual((p.memory, p.said_lines, p.history, p.heard, p.trip_heard, p.proposed),
+                             ([], [], [], [], {}, False))
+            self.assertEqual(p.room, "kitchen")
+            self.assertEqual(p.sure, ["min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 "
+                                      "portion; this morning it holds 1 portion. (you saw it)"])
+        leo = day2.people["leo"]
+        text = day2.prompt_for(leo, 0, day2.options_for(leo))
+        self.assertIn("About the can: Daniel admitted taking it yesterday, at minute 33.", text)
+        self.assertIn("Against Daniel (a lot): yesterday, Daniel accused you of taking the can at minute", text)
+        self.assertIn("you were angry with Daniel yesterday at minutes", text)
+        self.assertIn("; and last night.", text)
+        dan = day2.people["daniel"]
+        self.assertIn("About the can: you ate it yourself, and you admitted it yesterday.", day2.inside_lines(dan))
+        self.assertIn("On your conscience (a lot): you ate the can in the night, and nobody saw; yesterday, you accused "
+                      "Leo of what you did, at minute 03", day2.prompt_for(dan, 0, day2.options_for(dan)))
+        self.assertEqual(day2.trip, {"minute": 0, "why": ["carried over from yesterday"], "asked": []})
+        day2.turn(0)
+        self.assertEqual({d["person"] for d in day2.log[0]["decisions"] if d["mode"] != "routine"}, set(data.ORDER))
+        self.assertIn("the family is together in the kitchen for the first time since last night",
+                      day2.log[0]["decisions"][0]["triggers"])
+
+    def test_t10_someone_not_back_is_away(self):
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "trip:daniel": 0.99})
+        day2 = Morning.next_day(day1, n, oracle)
+        self.assertIsNone(day2.people["daniel"].room)
+        leo = day2.people["leo"]
+        self.assertNotIn("daniel", [q.id for q in day2.others_here(leo)])
+        self.assertFalse([o.id for o in day2.options_for(leo) if "daniel" in o.id])
+        text = day2.prompt_for(leo, 0, day2.options_for(leo))
+        self.assertIn("You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; "
+                      "Mara, 17).", text)
+        self.assertNotIn("- Daniel is here", text)
+        self.assertEqual(leo.sure, ["min 00: Everyone else gets up and comes into the kitchen. Last night the shelf held "
+                                    "2 portions; this morning it holds 2 portions. Daniel is not here: his bed is empty "
+                                    "and he is nowhere in the house, so he went out in the night and has not come back. "
+                                    "(you saw it)"])
+        self.assertIn("About food: the shelf holds 2 portions, and there is no other food in the house, so there is "
+                      "not one portion each.", day2.inside_lines(leo))
+        for t in range(3):
+            day2.turn(t)
+            self.assertNotIn("daniel", [d["person"] for d in day2.log[-1]["decisions"]])
+        day2.finish()
+        self.assertEqual(day2.transcript["away"], ["daniel"])
+
+    def test_t10_a_shaken_face_shows_for_3_turns(self):
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "trip:daniel": 0.7})
+        day2 = Morning.next_day(day1, n, oracle)
+        dan = day2.people["daniel"]
+        self.assertEqual(dan.feeling, "shaken")
+        self.assertEqual([day2.shown(dan, t) for t in range(4)], [True, True, True, False])
+        self.assertEqual([day2.shown(q, 0) for q in day2.people.values() if q is not dan], [False] * 3)
+        leo = day2.people["leo"]
+        self.assertIn("- Daniel is here, just got up. Daniel looks shaken.", day2.prompt_for(leo, 0, day2.options_for(leo)))
+
+    def test_t10_food_lines_and_the_returners_opening(self):
+        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"], "elena": ["watch_door"]},
+                                           {**QUIET, "house": 0.95})
+        day2 = Morning.next_day(day1, n, oracle)
+        self.assertEqual(day2.people["daniel"].sure[0],
+                         "min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this "
+                         "morning it holds 5 portions: the 3 you brought back are on it. (you saw it)")
+        self.assertEqual(day2.people["mara"].sure[0],
+                         "min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this "
+                         "morning it holds 5 portions. So someone brought food into the house in the night. (you saw it)")
+        self.assertIn("About food: the shelf holds 5 portions, and there is no other food in the house, so there is one "
+                      "portion each, and nothing after that.", day2.inside_lines(day2.people["mara"]))
+        self.assertIn("About the neighbour's house: Daniel went there last night and came back with food. Outside is "
+                      "dangerous.", day2.inside_lines(day2.people["elena"]))
+        self.assertIn("About the neighbour's house: you went in last night and found 6 portions; you brought back 3, "
+                      "and 3 are still there. Outside is dangerous.", day2.inside_lines(day2.people["daniel"]))
+        self.assertIn("- Before dawn Daniel came back in by the front door, carrying food (you saw it).",
+                      day2.carry["elena"])
+
+    # T11
+    def test_t11_the_day2_options(self):
+        from talk import act_of, aimed_at
+        day1, oracle = self.v11_day1(3, NightScripted())
+        n = self.night.Night(day1, oracle).run()
+        day2 = Morning.next_day(day1, n, oracle)
+        dan, ele, leo, mara = (day2.people[p] for p in data.ORDER)
+
+        def trip(p):
+            return [o.id for o in day2.options_for(p) if DAY2_TRIP_IDS.match(o.id)]
+        self.assertEqual(trip(dan), ["propose_trip", "volunteer", "send_elena", "send_leo", "send_mara"])
+        labels = {o.id: o.label for o in day2.options_for(dan)}
+        self.assertEqual(labels["send_leo"], "say Leo is the one who should go there tonight")
+        self.assertEqual(labels["volunteer"], "offer to go there tonight yourself")
+        self.act(day2, dan, "volunteer", "I'll go.")
+        self.assertEqual(trip(dan), ["propose_trip", "still_going", "send_elena", "send_leo", "send_mara",
+                                     "nobody_goes", "refuse_to_go"])
+        self.assertEqual(trip(leo), ["propose_trip", "volunteer", "send_daniel", "send_elena", "send_mara",
+                                     "nobody_goes", "keep_daniel_home"])
+        labels = {o.id: o.label for p in day2.people.values() for o in day2.options_for(p)}
+        self.assertEqual((labels["still_going"], labels["nobody_goes"], labels["keep_daniel_home"],
+                          labels["refuse_to_go"]),
+                         ("say you still mean to go there tonight", "say nobody should go out tonight",
+                          "say Daniel must stay home tonight", "say you yourself will not go"))
+        self.act(day2, dan, "still_going", "I still mean it.", t=1)
+        self.assertEqual(day2.trip_acts[-1][2:4], ("volunteer", None))
+        self.assertEqual(day2.said[-1]["why"], "an offer to go they had made before")
+        self.assertIn((3, 'Daniel says he still means to go tonight: "I still mean it."'), leo.memory)
+        self.act(day2, ele, "send_leo", "Leo should.", t=2)
+        self.act(day2, leo, "keep_daniel_home", "Not Daniel.", t=3)
+        self.act(day2, leo, "refuse_to_go", "Not me.", t=4)
+        self.assertIn((6, 'Elena says you are the one who should go: "Leo should."'), leo.memory)
+        self.assertIn((9, 'Leo says Daniel must stay home tonight: "Not Daniel."'), ele.memory)
+        self.assertIn((12, 'Leo says he will not go: "Not me."'), ele.memory)
+        self.assertIn("min 09, you said Daniel must stay home tonight.", leo.said_lines)
+        plan = next(x for x in day2.inside_lines(ele) if x.startswith("About going there tonight:"))
+        self.assertEqual(plan, "About going there tonight: Daniel said he still means to go (min 03); you said Leo is "
+                               "the one who should go (min 06); Leo said he will not go (min 12).")
+        day2.finish()
+        self.assertEqual([a[2] for a in day2.transcript["trip"]["acts"]],
+                         ["volunteer", "still_going", "send_leo", "keep_daniel_home", "refuse_to_go"])
+        self.assertEqual([act_of(x) for x in ("nobody_goes", "keep_leo_home", "send_mara", "still_going",
+                                              "refuse_to_go", "keep_searching")],
+                         [("object", None), ("object", "leo"), ("back", "mara"), ("volunteer", None),
+                          ("decline", None), ("search", None)])
+        self.assertEqual([aimed_at(x) for x in ("keep_leo_home", "send_mara", "nobody_goes")], ["leo", "mara", None])
+        # The wording rule over every offered set; opposite kinds share no stem but a person's id.
+        for p in day2.people.values():
+            opts = [o for o in day2.options_for(p) if DAY2_TRIP_IDS.match(o.id)]
+            self.assertEqual(not_pairs([o.label for o in opts]), [], p.id)
+
+            def stems(kinds):
+                return {re.sub("|".join(data.ORDER), "", o.id) for o in opts if act_of(o.id)[0] in kinds}
+            self.assertFalse(stems({"propose", "volunteer", "back"}) & stems({"object", "decline"}), p.id)
+        # Day 1 keeps the v11 options and labels.
+        m, _ = scripted(silent, self.dirs, turns=1)
+        m.portions = 0
+        m.turn(1)
+        self.assertEqual([(o.id, o.label) for o in m.options_for(m.people["leo"]) if TRIP_IDS.match(o.id)],
+                         [("propose_trip", "say someone should go to the neighbour's house tonight"),
+                          ("volunteer", "offer to go there tonight yourself"),
+                          ("back_daniel", "say Daniel should be the one to go"),
+                          ("back_elena", "say Elena should be the one to go"),
+                          ("back_mara", "say Mara should be the one to go")])
+
+    # T12
+    def test_t12_the_budget(self):
+        night_n = day2_n = 0
+        for seed in (1, 2, 3):
+            (_, code), out = fake_morning(self.dirs, seed=seed)
+            self.assertEqual(code, 0, out)
+        for p in cached_prompts(self.dirs):
+            if "\nNow it is night" in p:
+                night_n += 1
+                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + without_blocks(p)), 1450)
+                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p), 1450 + TRIP_BLOCK_MAX)
+            elif CARRY_HEAD in p:
+                day2_n += 1
+                self.assertLess(estimate_tokens(SYSTEM + without_blocks(p)), 1450)
+                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + CARRY_MAX)
+        self.assertGreater(night_n, 0)
+        self.assertGreater(day2_n, 0)
+        # The carry-in costs this morning no line.
+        day1, oracle = self.v11_day1(2, NightScripted())
+        n = self.night.Night(day1, oracle).run()
+        day2 = Morning.next_day(day1, n, oracle)
+        ele = day2.people["elena"]
+        ele.memory += [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
+        with_carry = day2.prompt_for(ele, 1, day2.options_for(ele))
+        carry, day2.carry = day2.carry, {}
+        plain = day2.prompt_for(ele, 1, day2.options_for(ele))
+        day2.carry = carry
+
+        def morning_lines(prompt):
+            lines = prompt.split("\n")
+            return lines[lines.index("What else happened this morning, most recent last:"):
+                         next(i for i, x in enumerate(lines) if x.startswith("Now, minute"))]
+        self.assertIn(CARRY_HEAD, with_carry)
+        self.assertIn("- (earlier things, left out here)", morning_lines(plain))
+        self.assertEqual(morning_lines(with_carry), morning_lines(plain))
+
+    # T13
+    def test_t13_counting_and_the_story(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
+        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
+        self.assertEqual(meta["night_asks"], len(tr["night"]["decisions"]))
+        self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for t in tr["day2"]["turns"] for a in t["acts"]))
+        self.assertEqual(meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night_asks"]
+                         + meta["day2_asks"], meta["answers_live"] + meta["answers_from_cache"])
+        self.assertEqual(meta["leavers"], tr["night"]["leavers"])
+        for key in ("night_asks", "day2_asks", "night_api_requests", "day2_api_requests"):
+            self.assertIn(f"{key}: {meta[key]}", out)
+        night = story[story.index("# The night\n"):story.index("# The next morning (day 5)\n")]
+        self.assertEqual(night.count("\n- **Bedtime, "), 4)
+        noticing = [x for x in night.split("\n") if x.startswith("- Noticing: ")]
+        self.assertEqual(len(noticing), len(tr["night"]["noticing"]))
+        for x, e in zip(noticing, tr["night"]["noticing"]):
+            if e["draw"] is not None:
+                self.assertIn(f"draw {e['draw']:.3f}", x)
+        self.assertIn(f"- The neighbour's house held {tr['night']['house']} portion", night)
+        for g in tr["night"]["groups"]:
+            self.assertIn(f"street draw {g['u']:.3f}", night)
+        # The call cap counts each scene apart.
+        oracle = Oracle(Cache(self.path("cap")), "fake", 1, client=FakeClient(max_calls=2), max_calls=2)
+        oracle.ask("s", "p1")
+        oracle.ask("s", "p2")
+        with self.assertRaises(gemini.CallCapReached):
+            oracle.ask("s", "p3")
+        oracle.new_scene()
+        oracle.ask("s", "p3")
+        oracle.ask("s", "p4")
+        with self.assertRaises(gemini.CallCapReached):
+            oracle.ask("s", "p5")
+        self.assertEqual(oracle.api_requests, 4)
+
+    def test_t13_a_night_with_a_leaver_is_told_in_the_story(self):
+        dirs = Dirs()
+        try:
+            client = NightScripted({"daniel": ["go_next_door"], "leo": ["lie_awake", "stop_daniel"]})
+            (meta, code), out = quiet_run(1, fake=True, config_path=CONFIG, runs_dir=dirs.runs, cache_dir=dirs.cache,
+                                          client=client)
+            self.assertEqual(code, 0, out)
+            story = read(os.path.join(dirs.runs, "daniel_ate_it-seed1.md"))
+            tr = json.loads(read(os.path.join(dirs.runs, "daniel_ate_it-seed1.transcript.json")))
+            self.assertEqual(meta["leavers"], ["daniel"])
+            self.assertTrue(tr["night"]["noticing"])
+            self.assertIn("street draw ", story)
+            self.assertEqual(meta["outcome"], [g["outcome"] for g in tr["night"]["groups"]])
+        finally:
+            dirs.cleanup()
+
+    # T14
+    def test_t14_v11_v10_and_v9_still_replay(self):
+        for version in ("v11", "v10", "v9"):
+            done = run_check(version)
+            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
+            self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
+            self.assertIn("0 API calls", done.stdout)
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 866f57b..a349da0 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -22,6 +22,10 @@ The trip concern (reports/trip_design.md): once the shelf is empty or someone fi
 hungry, everyone is told there is no food for tomorrow and that the neighbour's house may have
 some, and each of them may take a position on whether someone goes there tonight. The rules
 record the positions and decide nothing; nobody leaves the house.
+
+Time passing (reports/night_design.md): a Morning is day 1 (house day 4) or day 2 (house day 5).
+Day 2 starts from the people as the night left them (night.py), with what each of them carries
+in as a block of facts outside the prompt budget, and words the trip's options anew.
 """
 import json
 import random
@@ -46,6 +50,20 @@ SYSTEM = (
     '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
     '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
 )
+# The night's own (reports/night_design.md, §3.2): the same answer, decided for tonight, in a low voice.
+NIGHT_SYSTEM = (
+    "You decide what one person in a family does tonight. You get who they are, what they "
+    "remember, what they know now, and the options open to them. They know only what is in their "
+    "memory. Choose exactly one option id from the list. If the option is marked (speech), `say` "
+    "must hold the exact words they say, in a low voice, in their own voice, one or two short "
+    "sentences. For any other option `say` is null. `feeling` names what they feel right now in "
+    "one or two words. `reason` is their reason in one sentence, as they would think it. "
+    "`suspects` is who they now believe took the can, and `angry_at` is who they are angry with "
+    "right now: each is one of \"Daniel\", \"Elena\", \"Leo\", \"Mara\" or \"nobody\". Reply with "
+    'JSON only: {"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": '
+    '"<sentence>", "suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
+)
+NIGHT_MINUTE = data.MINUTES     # the clock the night's answers keep (day 1 ends at minute 90)
 
 # Feelings that reach the face, by how strongly they show. Others in the room see them,
 # and someone who looks like this counts as upset nearby. Anything else (guilty, ashamed,
@@ -184,6 +202,16 @@ class Grudge:
         return False
 
 
+# Day 2, for whoever knows of no visit to the neighbour's house (reports/night_design.md, §5.3):
+# after a night when anyone could have gone, "nobody has been inside since" is no longer certain.
+NEIGHBOUR_UNKNOWN = ("About the neighbour's house: its people left in the first days, so there may be food "
+                     "there. Outside is dangerous.")
+
+
+def portions_text(n):
+    return f"{n} portion{'s' if n != 1 else ''}"
+
+
 def minutes_text(ms):
     ms = [f"{m:02d}" for m in ms]
     return ms[0] if len(ms) == 1 else ", ".join(ms[:-1]) + " and " + ms[-1]
@@ -191,14 +219,24 @@ def minutes_text(ms):
 
 def grudge_facts(name, events, limit=None):
     """The facts behind a grudge: each event the rules saw, then one line for the times the
-    person named them as who they were angry with."""
-    facts = [fact for _, fact, kind in events if kind == "event"]
-    angry = [m for m, _, kind in events if kind == "angry"]
+    person named them as who they were angry with. On day 2 an event carried from day 1 or the
+    night has a fourth element, "yesterday" or "last night" (reports/night_design.md, §5.3)."""
+    facts = [e[1] for e in events if e[2] == "event"]
+    angry = [e for e in events if e[2] == "angry"]
     if limit:
         facts, angry = facts[-limit:], angry[-limit:]
-    if angry:
-        facts.append(f"you were angry with {name} at minute{'s' if len(angry) > 1 else ''} "
-                     f"{minutes_text(angry)}")
+    if angry and all(len(e) == 3 for e in events):
+        ms = [e[0] for e in angry]
+        facts.append(f"you were angry with {name} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
+    elif angry:
+        parts = []
+        for when in ("yesterday", "last night", "this morning"):
+            ms = [e[0] for e in angry if (e[3] if len(e) > 3 else "this morning") == when]
+            if not ms:
+                continue
+            parts.append(when if when == "last night" else
+                         f"{when} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
+        facts.append(f"you were angry with {name} " + "; and ".join(parts))
     return facts
 
 
@@ -261,6 +299,10 @@ class Person:
         self.trip_raised = False
         self.trip_memories = {x for x in self.backstory
                               if any(x.startswith(f"Day 2: {m} (") for m in data.TRIP_MEMORIES)}
+        # Time passing (reports/night_design.md): what they did tonight, for the night's later
+        # prompts; and on day 2, what of day 1 still counts as yesterday's (None on day 1).
+        self.tonight = []
+        self.yesterday = None
 
     def grudge(self, against):
         return self.grudges.setdefault(against, Grudge())
@@ -274,13 +316,22 @@ class Person:
 
 
 class Morning:
-    def __init__(self, oracle, seed=0, scenario=data.DEFAULT_SCENARIO):
+    def __init__(self, oracle, seed=0, scenario=data.DEFAULT_SCENARIO, day=4):
+        """day 4: the morning of the count (day 1). day 5: the next morning (day 2), which
+        `Morning.next_day` sets up from day 1 and the night."""
         self.oracle = oracle
+        self.day = day
+        self.away = set()           # day 2: who did not come back in the night
+        self.carry = {}             # day 2: person -> the carry-in block (reports/night_design.md, §5.2)
+        self.neighbour = {}         # day 2: person -> their "About the neighbour's house:" line
+        self.carried = {}           # day 2: person -> their opening, food and neighbour lines at minute 00
+        self.trip_ids = []          # day 2: the option id of each trip act, in order
         self.seed = seed
         self.scenario = scenario
         self.culprit = data.culprit(scenario)       # who took the can, or None
         self.people = {p: Person(p, scenario) for p in data.ORDER}
         self.portions = data.PORTIONS
+        self.start_portions = self.portions     # day 2 starts from the night's shelf
         self.turns = data.MINUTES // data.MINUTES_PER_TURN
         self.log = []               # one record per turn
         self.said = []              # every line spoken, in order
@@ -303,6 +354,8 @@ class Morning:
         self.trip = None            # the trip concern once started: {"minute", "why", "asked"}
         self.trip_acts = []         # (minute, who, kind, target, words), every position taken
         self.trip_now = set()       # during the turn it starts: who is asked because of it
+        if day != 4:
+            return                  # day 2's opening is set up by next_day
         for p in self.people.values():
             how = "did it" if p.id == "elena" else "saw it"
             p.sure.append(f"min 00: {data.OPENING} (you {how})")
@@ -312,6 +365,12 @@ class Morning:
             p.seen = p.levels()
         self.started("kitchen", 0, "the count came up short", False)
 
+    @classmethod
+    def next_day(cls, day1, night, oracle):
+        """Day 2, from day 1 and the night that followed it (reports/night_design.md, §5)."""
+        import night as night_mod
+        return night_mod.next_day(day1, night, oracle)
+
     def started(self, room, minute, why, by_inner):
         if self.convos.new_thing(room, minute, why):
             self.start_by_inner.append(by_inner)
@@ -422,6 +481,8 @@ class Morning:
         has started; never the position they already hold."""
         if self.trip is None:
             return []
+        if self.day != 4:
+            return self.trip_options_day2(p, others)
         pos = p.trip_heard.get(p.id)
         own = pos[1:3] if pos else None
         out = []
@@ -445,6 +506,36 @@ class Morning:
             out.append(Option("decline", "say you will not be the one to go", True, kind="decline"))
         return out
 
+    def trip_options_day2(self, p, others):
+        """Day 2's wording of the same positions (reports/night_design.md, §6): ids that carry
+        their meaning, labels that share no verb, for going first and against after, and
+        `still_going` in place of `volunteer` while the offer is their position. When each is
+        offered is as on day 1."""
+        pos = p.trip_heard.get(p.id)
+        own = pos[1:3] if pos else None
+        out = []
+        if not p.proposed:
+            out.append(Option("propose_trip", "say someone should go to the neighbour's house tonight", True,
+                              kind="propose"))
+        if own != ("volunteer", None):
+            out.append(Option("volunteer", "offer to go there tonight yourself", True, kind="volunteer"))
+        else:
+            out.append(Option("still_going", "say you still mean to go there tonight", True, kind="volunteer"))
+        for q in others:
+            if own != ("back", q.id):
+                out.append(Option(f"send_{q.id}", f"say {q.name} is the one who should go there tonight", True,
+                                  kind="back", target=q.id))
+        if p.trip_raised and own != ("object", None):
+            out.append(Option("nobody_goes", "say nobody should go out tonight", True, kind="object"))
+        for q in others:
+            if self.named_to_go(p, q.id) and own != ("object", q.id):
+                out.append(Option(f"keep_{q.id}_home", f"say {q.name} must stay home tonight", True,
+                                  kind="object", target=q.id))
+        backed = any(v[1:3] == ("back", p.id) for w, v in p.trip_heard.items() if w != p.id)
+        if (backed or own == ("volunteer", None)) and own != ("decline", None):
+            out.append(Option("refuse_to_go", "say you yourself will not go", True, kind="decline"))
+        return out
+
     @staticmethod
     def named_to_go(p, q):
         """As far as p has heard: q offered to go, or someone backed q since q last said they
@@ -479,29 +570,52 @@ class Morning:
         if not p.trip_heard:
             return None
         parts = []
-        for who, (minute, kind, target, _) in sorted(p.trip_heard.items(), key=lambda kv: kv[1][3]):
+        for who, heard in sorted(p.trip_heard.items(), key=lambda kv: kv[1][3]):
+            minute, kind, target = heard[:3]
+            option = heard[4] if len(heard) > 4 else None       # day 2 keeps the option id
             x = "you" if who == p.id else NAMES[who]
+            he = "you" if who == p.id else data.PRONOUNS[who]["he"]
             q = None if target is None else "you" if target == p.id else NAMES[target]
             if kind == "propose":
                 said = f"{x} said someone should go"
+            elif option == "still_going":
+                said = f"{x} said {he} still {'mean' if who == p.id else 'means'} to go"
             elif kind == "volunteer":
                 said = f"{x} offered to go"
             elif kind == "object":
-                said = f"{x} said nobody should go" if q is None else f"{x} said {q} should not go"
+                said = (f"{x} said nobody should go" if q is None else f"{x} said {q} must stay home"
+                        if option else f"{x} said {q} should not go")
             elif kind == "back":
-                said = f"{x} said {q} should go"
+                said = f"{x} said {q} is the one who should go" if option else f"{x} said {q} should go"
             else:
-                said = f"{x} said {'you' if who == p.id else data.PRONOUNS[who]['he']} will not go"
+                said = f"{x} said {he} will not go"
             parts.append(f"{said} (min {minute:02d})")
         return "About going there tonight: " + "; ".join(parts) + "."
 
     def trip_lines(self, p):
-        """What the trip concern adds after their "About the can:" line."""
+        """What the trip concern adds after their "About the can:" line. On day 2 the food and
+        the neighbour's house are as the night left them (reports/night_design.md, §5.3)."""
         if self.trip is None:
             return []
         plan = self.heard_plan(p)
+        if self.day != 4:
+            return [self.food_line(), self.neighbour.get(p.id, NEIGHBOUR_UNKNOWN)] + ([plan] if plan else [])
         return [data.ABOUT_FOOD, data.ABOUT_NEIGHBOUR] + ([plan] if plan else [])
 
+    def food_line(self):
+        """Day 2's "About food:" line: what the shelf holds, and what that means for those here."""
+        n = self.portions
+        k = sum(q.room is not None for q in self.people.values())
+        if n == 0:
+            so = "there is nothing to eat today"
+        elif n < k:
+            so = "there is not one portion each"
+        elif n // k == 1:
+            so = "there is one portion each, and nothing after that"
+        else:
+            so = f"there are {n // k} portions each, and nothing after that"
+        return f"About food: the shelf holds {portions_text(n)}, and there is no other food in the house, so {so}."
+
     def plan_text(self):
         """The state of the plan for tonight, from every position taken (reports/trip_design.md,
         §4.3): who has offered to go, then each other person's latest position."""
@@ -588,12 +702,28 @@ class Morning:
         if "hunger" in self.risen(p):
             out.append("Since you last decided, you have grown hungrier.")
         s = p.suspicion
+        y = p.yesterday             # day 2 only (reports/night_design.md, §5.3)
         # What they know about the can wins over what their answers guessed.
         if p.knows_culprit == p.id:
-            about = "About the can: you ate it yourself."
+            about = ("About the can: you ate it yourself, and you admitted it yesterday." if y and y["confessed"]
+                     else "About the can: you ate it yourself.")
+        elif p.knows_culprit and y and y["confession_heard"]:
+            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it yesterday, at minute "
+                     f"{p.confession_heard_at:02d}.")
         elif p.knows_culprit:
             about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
                      f"{p.confession_heard_at:02d}.")
+        elif s.strength and y is not None:
+            when = []
+            for word, ms in (("yesterday", y["suspected_at"]), ("last night", y["suspected_last_night"]),
+                             ("this morning", p.suspected_at)):
+                if ms is True:
+                    when.append(word)
+                elif ms:
+                    ms = ms[-EVENTS_SHOWN:]
+                    when.append(f"{word} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
+            about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it"
+                     + (", " + ", and ".join(when) if when else "") + ".")
         elif s.strength:
             about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
                      f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
@@ -653,10 +783,13 @@ class Morning:
                 "back": "said you should be the one to go", "decline": "said they will not be the one to go",
                 }.get(h["kind"], "spoke to everyone")
 
-    def prompt_for(self, p, t, opts, lull=None):
-        """lull: for a lull moment, the minute the room was last stirred; None otherwise."""
+    def prompt_for(self, p, t, opts, lull=None, night=None):
+        """lull: for a lull moment, the minute the room was last stirred; None otherwise.
+        night: the night's `Now` lines (reports/night_design.md, §3.2), which take the place of the
+        room, the turn and the pattern block; None by day."""
         s = p.sheet
-        minute = t * data.MINUTES_PER_TURN
+        minute = None if night is not None else t * data.MINUTES_PER_TURN
+        system = SYSTEM if night is None else NIGHT_SYSTEM
         calls = "; ".join(f"{self.people[q].name} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
         inside = self.inside_lines(p)
         head = [
@@ -666,8 +799,12 @@ class Morning:
             f"Who you are: {s['note']}",
             f"Temperament: {trait_words(s['traits'])}.",
             f"What matters to you: {', '.join(s['values'])}.",
-        ] + inside + [f"The house: {data.HOUSE} "
-                      f"{data.HOUSE_THINGS_AFTER_TRIP if self.trip else data.HOUSE_THINGS}"]
+        ] + inside
+        house = (data.HOUSE_THINGS_NIGHT if night is not None
+                 else data.HOUSE_THINGS_AFTER_TRIP if self.trip else data.HOUSE_THINGS)
+        head += [f"The house: {data.HOUSE} {house}"]
+        if night is not None:
+            return self.prompt_parts(p, opts, head, list(night), system, "today", minute)
         room = data.ROOMS[p.room]
         now = [f"Now, minute {minute:02d}, you are in the {room}."]
         others = self.others_here(p)
@@ -687,33 +824,43 @@ class Morning:
         elif others:
             now.append(f"You are the first to act in the {room} this turn.")
         now += self.pattern(p)
+        return self.prompt_parts(p, opts, head, now, system, "this morning", minute)
+
+    def prompt_parts(self, p, opts, head, now, system, when, minute):
+        """The rest of the prompt, trimmed to the budget. when: "this morning", or "today" at
+        night (reports/night_design.md, §3.2)."""
         tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]
 
         back = list(p.backstory)
         morning = [f"min {m:02d}: {x}" for m, x in p.memory if m != minute]  # this turn is above
-        pinned = ["What you are sure of this morning:"] + [f"- {x}" for x in p.sure]
+        morning += [f"tonight: {x}" for x in p.tonight]
+        pinned = [f"What you are sure of {'from today' if when == 'today' else when}:"] + [f"- {x}" for x in p.sure]
         if p.said_lines:
-            pinned += ["Your own last words this morning:"] + [f"- {x}" for x in p.said_lines[-3:]]
+            pinned += [f"Your own last words {when}:"] + [f"- {x}" for x in p.said_lines[-3:]]
+        carry = self.carry.get(p.id, [])
         # Once the trip concern has started, its block sits outside the budget
         # (reports/trip_design.md, §2.5): its lines, its options, the day-2 memories it keeps from
-        # trimming, and "this morning" in the house line. `block` counts its characters.
+        # trimming, and "this morning" in the house line. `block` counts its characters. On day 2
+        # the carry-in block sits outside the budget too (reports/night_design.md, §5.4).
         keep = p.trip_memories if self.trip else set()
         block = 0
         if self.trip:
+            house = head[-1][len(f"The house: {data.HOUSE} "):]
             block += sum(len(x) + 1 for x in self.trip_lines(p))
             block += sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in TRIP_KINDS)
             block += sum(len(f"- {x}") + 1 for x in keep)
-            block += len(data.HOUSE_THINGS_AFTER_TRIP) - len(data.HOUSE_THINGS)
+            block += max(0, len(house) - len(data.HOUSE_THINGS))
+        block += sum(len(x) + 1 for x in carry)
         cut = False
         while True:
             parts = head + ["What you remember from the days before:"] + [f"- {x}" for x in back]
-            parts += pinned + ["What else happened this morning, most recent last:"]
+            parts += carry + pinned + [f"What else happened {when}, most recent last:"]
             parts += (["- (earlier things, left out here)"] if cut else [])
             parts += [f"- {x}" for x in morning] or ([] if cut else ["- nothing else yet"])
             parts += now + tail
             text = "\n".join(parts)
             loose = [x for x in back if x not in keep]      # all of them, before the trip
-            if estimate_tokens(SYSTEM + text, block) <= PROMPT_TOKEN_BUDGET or (not morning and not loose):
+            if estimate_tokens(system + text, block) <= PROMPT_TOKEN_BUDGET or (not morning and not loose):
                 break
             cut = True
             if len(morning) > 8:
@@ -724,7 +871,7 @@ class Morning:
                 morning.pop(0)
             else:
                 back.remove(loose[0])
-        self.max_prompt_tokens = max(self.max_prompt_tokens, estimate_tokens(SYSTEM + text))
+        self.max_prompt_tokens = max(self.max_prompt_tokens, estimate_tokens(system + text))
         return text
 
     # ---------- reading the answer ----------
@@ -789,10 +936,16 @@ class Morning:
              "by_inner": next(by_inner) if what == "started" else None}
             for m, r, what, why in self.convos.log]
         # The trip concern (reports/trip_design.md, §4.1), or None if it never started.
+        ids = (self.trip_ids if self.day != 4 else
+               [trip_option(kind, target) for _, _, kind, target, _ in self.trip_acts])
         self.transcript["trip"] = None if self.trip is None else {
             **self.trip,
-            "acts": [[m, who, trip_option(kind, target), words] for m, who, kind, target, words in self.trip_acts],
+            "acts": [[m, who, i, words] for (m, who, _, _, words), i in zip(self.trip_acts, ids)],
             "plan": self.plan_text()}
+        if self.day != 4:
+            # Day 2 (reports/night_design.md, §8): who is away, and what each person carried in.
+            self.transcript["away"] = [q for q in data.ORDER if q in self.away]
+            self.transcript["carry_in"] = {q: list(lines) for q, lines in self.carry.items()}
 
     def social_triggers(self, p, t):
         """What counts now: anything new; anything else only while the room is talking."""
@@ -897,7 +1050,7 @@ class Morning:
         # someone who hears it through a wall.
         for room, new, heard_it in voices:
             for q in self.people.values():
-                if q.id in heard_it or q.room == room or data.SOUNDPROOF & {room, q.room}:
+                if q.id in heard_it or q.room == room or q.room is None or data.SOUNDPROOF & {room, q.room}:
                     continue
                 line = f"Voices from the {data.ROOMS[room]}"
                 if (minute, line + ".") not in q.memory:
@@ -922,6 +1075,8 @@ class Morning:
         self.moved_by_inner = {}
         self.trip_now = set()
         for p in self.people.values():
+            if p.room is None:      # day 2: not back from the night, so not in the house
+                continue
             p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
         record["portions"] = self.portions
         self.log.append(record)
@@ -940,7 +1095,12 @@ class Morning:
         if not choice:
             return None, why
         d.update(mode="model", **choice)
+        self.take_answer(p, choice, minute, d)
+        return choice, None
 
+    def take_answer(self, p, choice, minute, d):
+        """What an answer does to their suspicion and grudges (the night's answers too, at
+        NIGHT_MINUTE)."""
         def named(field):
             who = next((q for q in data.ORDER if NAMES[q] == choice[field]), None)
             return None if who == p.id else who     # naming yourself counts as nobody
@@ -949,6 +1109,8 @@ class Morning:
         d["suspects_result"] = p.suspicion.report(suspect, minute)
         if p.suspicion.target != before:
             p.suspected_at = []
+            if p.yesterday is not None:
+                p.yesterday["suspected_at"], p.yesterday["suspected_last_night"] = [], False
         if suspect is not None and suspect == p.suspicion.target:
             p.suspected_at.append(minute)
         d["suspects_now"] = p.suspicion.short("suspicion")
@@ -966,7 +1128,6 @@ class Morning:
         if kept:
             changes.append("kept: " + ", ".join(f"{NAMES[t]} {p.grudges[t].strength}/3" for t in kept))
         d["grudge_note"] = "; ".join(changes) or "no grudges"
-        return choice, None
 
     def decide(self, p, t):
         minute = t * data.MINUTES_PER_TURN
@@ -1034,9 +1195,11 @@ class Morning:
         if trigger:
             q.triggers.append(trigger)
 
-    def line_text(self, p, kind, target, words, listener, while_doing=None):
+    def line_text(self, p, kind, target, words, listener, while_doing=None, option=None):
         aimed = ("you" if listener is not None and target is listener else target.name) if target else None
-        if kind == "ask":
+        if self.day != 4 and kind in TRIP_KINDS:
+            gist = self.trip_gist(p, kind, aimed, option)
+        elif kind == "ask":
             gist = f"{p.name} asks everyone who took the can"
         elif kind == "deny":
             gist = f"{p.name} denies taking it, to everyone"
@@ -1063,6 +1226,22 @@ class Morning:
             gist = f"{p.name} says to everyone"
         return f"{gist}: \"{words}\""
 
+    @staticmethod
+    def trip_gist(p, kind, aimed, option):
+        """What others hear of a position on day 2 (reports/night_design.md, §6)."""
+        he = data.PRONOUNS[p.id]["he"]
+        if kind == "propose":
+            return f"{p.name} says someone should go to the neighbour's house tonight"
+        if option == "still_going":
+            return f"{p.name} says {he} still means to go tonight"
+        if kind == "volunteer":
+            return f"{p.name} offers to go to the neighbour's house tonight"
+        if kind == "object":
+            return f"{p.name} says {aimed} must stay home tonight" if aimed else f"{p.name} says nobody should go out tonight"
+        if kind == "back":
+            return f"{p.name} says {aimed} {'are' if aimed == 'you' else 'is'} the one who should go"
+        return f"{p.name} says {he} will not go"
+
     def started_by(self, room, minute, why, d):
         self.started(room, minute, why, bool(d.get("inner_kinds")))
 
@@ -1116,14 +1295,14 @@ class Morning:
             if new:
                 self.started_by(room, minute, f"{p.name}: {why}", d)
             text = self.line_text(p, spoken_kind, target if aimed else None, words, None,
-                                  None if opt.speech else doing)
+                                  None if opt.speech else doing, opt.id)
             self.said.append({"minute": minute, "room": data.ROOMS[room], "who": p.name,
                               "to": target.name if aimed else "everyone", "text": text,
                               "words": words, "new": new, "why": why})
             so_far.append(text)
             for q in seen:
                 heard = self.line_text(p, spoken_kind, target if aimed else None, words, q,
-                                       None if opt.speech else doing)
+                                       None if opt.speech else doing, opt.id)
                 self.perceive(q, minute, heard, trigger=(heard, new))
                 q.heard.append({"seq": self.seq, "who": p.id, "kind": spoken_kind,
                                 "target": target_id if aimed else None})
@@ -1138,19 +1317,27 @@ class Morning:
                     q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
                                   "(you heard it)")
                     # Grudges: it was admitted after being denied to them, or after accusing them.
+                    # On day 2 a denial or accusation of day 1 is yesterday's (reports/night_design.md, §5.1).
+                    y = q.yesterday or {"denials": (), "accused_by": ()}
                     if p.id in q.denials_heard:
+                        when = "yesterday at" if p.id in y["denials"] else "at"
                         self.add_grudge(q, p, minute,
                                         f"{p.name} admitted taking it at minute {minute:02d}, after "
-                                        f"denying it to you at minute {q.denials_heard[p.id]:02d}",
+                                        f"denying it to you {when} minute {q.denials_heard[p.id]:02d}",
                                         f"{p.name} admitted it after denying it to {q.name}", record)
                     if p.id in q.accused_by:
+                        when = "yesterday at" if p.id in y["accused_by"] else "at"
                         self.add_grudge(q, p, minute,
-                                        f"{p.name} had accused you of it at minute {q.accused_by[p.id]:02d}",
+                                        f"{p.name} had accused you of it {when} minute {q.accused_by[p.id]:02d}",
                                         f"{p.name} had accused {q.name} of it", record)
                 if kind == "deny":
                     q.denials_heard[p.id] = minute
+                    if q.yesterday:
+                        q.yesterday["denials"].discard(p.id)
                 if kind == "accuse" and q is target:
                     q.accused_by[p.id] = minute
+                    if q.yesterday:
+                        q.yesterday["accused_by"].discard(p.id)
                     if q.id != self.culprit:        # a false accusation
                         self.add_grudge(q, p, minute,
                                         f"{p.name} accused you of taking the can at minute {minute:02d}, "
@@ -1178,13 +1365,26 @@ class Morning:
                                else "said nobody should go out tonight"),
                     "back": f"said {target.name if target else ''} should be the one to go",
                     "decline": "said you will not be the one to go"}.get(kind, "said")
+            if self.day != 4 and kind in TRIP_KINDS:
+                # Day 2's wording (reports/night_design.md, §6), for the speaker's own line.
+                mine = {"still_going": "said you still mean to go there tonight",
+                        "nobody_goes": "said nobody should go out tonight",
+                        "refuse_to_go": "said you will not go"}.get(opt.id, mine)
+                if target and kind == "back":
+                    mine = f"said {target.name} is the one who should go"
+                elif target and kind == "object":
+                    mine = f"said {target.name} must stay home tonight"
             if kind in TRIP_KINDS:
                 # The plan record (reports/trip_design.md, §4.1): every position taken, and each
-                # speaker's latest one for everyone who heard it, the speaker included.
+                # speaker's latest one for everyone who heard it, the speaker included. Day 2 also
+                # keeps the option id (reports/night_design.md, §6).
                 aim = target_id if aimed else None
                 self.trip_acts.append((minute, p.id, kind, aim, words))
+                heard = (minute, kind, aim, self.seq) + ((opt.id,) if self.day != 4 else ())
+                if self.day != 4:
+                    self.trip_ids.append(opt.id)
                 for x in [p] + seen:
-                    x.trip_heard[p.id] = (minute, kind, aim, self.seq)
+                    x.trip_heard[p.id] = heard
                     if kind in ("propose", "volunteer", "back"):
                         x.trip_raised = True
                 if kind == "propose":
```

### Frozen replays

```
$ python v2/check.py
seed 1: replayed 7 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 11 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v3/check.py
seed 1: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 30 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v4/check.py
seed 1: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 4: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 5: replayed 41 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
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
$ python v6/check.py
daniel_ate_it-seed1: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 66 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 44 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 43 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v7/check.py
daniel_ate_it-seed1: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 48 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 33 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 18 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v8/check.py
daniel_ate_it_leo_heard-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v10/check.py
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v11/check.py
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```
