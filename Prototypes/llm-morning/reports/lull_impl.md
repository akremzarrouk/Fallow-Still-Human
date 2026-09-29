# Implementation: lull moments (v9)

Mode: implement. Built as reports/lull_design.md §1–§3 specifies, with its tests T1–T11 (§5).
No API was called. Paths are relative to `Prototypes/llm-morning/`.

## Commits

| Commit | What |
|---|---|
| `4b63c42` | reports/kitchen_audit.md, on its own |
| `c6fdcc4` | v8/ freeze: the current code copied to v8/, with v8/check.py replaying runs/v8. morning.py's default `--out` goes to v9, and .gitignore gets `runs/v9/fake/` and `cache/v9/fake-*`, as the v7 freeze did (`fd2583b`). |
| **`1c50d44`** | **Lull moments: world.py, story.py, morning.py, test_morning.py** |
| (the commit that adds this report) | reports/lull_impl.md |

After the last commit, `git status --short` shows only the three old untracked
`runs/v6/daniel_ate_it-seed{1,2,3}.replay.md`.

## What was built, against the design

| Design | Where (after `1c50d44`) |
|---|---|
| §1 `LULL_QUIET = 9`, `LULL_EVERY = 12`, and `LULL_QUIET = None` switches lulls off (the switch T5 uses) | world.py:59-60 |
| §1 `p.last_asked`, set in `ask_model`, so every model decision counts: social, inner, go-aside answer, lull, and fallback | world.py:234, world.py:762 |
| §1 `last_stir`, starting at `{"kitchen": 0}` | world.py:271-273 |
| §1 a stir: every act except `silent` and staying seated with the same person, set as the act is applied | world.py:894-897 |
| §1 an arrival stirs the destination at that turn's minute | world.py:721 |
| §1 the rule: no trigger, no inner moment, room still ≥ 9, not asked for ≥ 12 | world.py:812-814, world.py:825-831 (`lull_due`) |
| §2 the line, in the "Now" block after the people and portions lines, before "Said and done…" or "You are the first…" | world.py:526-527 |
| §2 nothing else in the prompt changes: `prompt_for` gains a `lull` argument, `None` except for a lull | world.py:502-503, world.py:761 |
| §3 recording: `d["lull"]` | world.py:813 |
| §3 recording: a `"lull"` key on every transcript act | world.py:685 |
| §3 recording: the story line `**Lull**, nothing said or done in the <room> since minute <MM>` | story.py:68-69 |
| §3 recording: the story key line | story.py:193-196 |
| §3 recording: meta `lull_moments`, also printed | morning.py:98, morning.py:108 |
| §3 the conversation, inner-moment and acting-order paths | unchanged (no edits there) |

**Numbers and the line.** The numbers (9, 12) and the line are the design's, unchanged. The
line is `Nothing has been said or done in the <room> since minute <MM>.`

**One addition the design does not spell out.** `lull_due` returns `False` for a room missing
from `last_stir` (world.py:828). Every occupied room has an entry: the kitchen from the start,
any other room from its first arrival. So this never decides anything; it only avoids a
`KeyError`.

## Tests

The design's T-numbers map to these tests in test_morning.py `LullTest`:

| Design | Test(s) |
|---|---|
| T1 | `test_t1_the_numbers`, `test_t1a_…` to `test_t1i_…`, one per case (a)–(i) of the design, with (g) and (h) in one test |
| T2 | `test_t2_a_still_room_is_never_talking` (fake seeds 1–5, checked at the moment of each lull decision) |
| T3, T7 | `test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place` |
| T4 | `test_t4_nothing_else_in_the_prompt_changes` |
| T5 | `test_t5_nothing_changes_before_the_first_lull` (fake seeds 1–5, lulls off against on) |
| T6 | `test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull` (the real v6 caches, replay mode, no client) |
| T8 | `test_t1e_t8_t9_alone_after_leaving` (scripted: Leo goes to the back room at 0) and `test_t8_nobody_is_alone_more_than_3_turns_without_being_asked` (fake seeds 1–5), both using P3's count from design §7 |
| T9 | in `test_t1e_t8_t9_alone_after_leaving` |
| T10 | `test_t10_lulls_are_recorded` |
| T11 | `test_t11_v8_still_replays`, which runs v8/check.py in a subprocess with `GEMINI_API_KEY` removed |
| T12 | the full suite, below |

**T4's state.** The design says "one state, well under budget". Leo's minute-12 prompt in a
fresh morning is the one with the most room: 1,324 estimated tokens, 1,341 with the line. The
other three are 1,364–1,394 (command 6). Daniel's, the first one tried, is at 1,394, so the
existing trimming cut a backstory line to fit the new one.

**Existing tests whose expectations changed (T12).** There are two. The other 67 existing
tests are unchanged and pass.

1. **`test_the_v6_baseline_replays_byte_for_byte_with_no_requests`** is replaced by
   `test_with_lulls_off_the_v6_baseline_replays_with_no_requests`.
   - With lulls on, the v6 baseline can no longer replay in full: it reaches the first lull,
     which T6 now checks.
   - The new test switches lulls off. It checks that the v6 baseline still replays with 0
     requests.
   - The transcript must equal v6's apart from the `lull` key.
   - The story must equal v6's apart from exactly one added line, the key's `- **Lull**` line.
2. **`test_the_story_and_the_transcript_carry_no_thought`**: the transcript key set must now
   equal v6's plus `lull`.
   - It also ignores `aside`, an existing key (world.py:712) that is written only on acts that
     take someone aside.
   - Lulls changed the fake seed-1 morning, and it now contains an aside. v6's seed-1 story had
     none.
   - Its check that no `thought` appears is unchanged.

### Before the change (tests written, world.py untouched)

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning
exit=1
Ran 86 tests in 16.943s
FAILED (failures=2, errors=16)
```

Each failing test with the last line of its traceback:

```
ERROR: DecisionFormatTest.test_with_lulls_off_the_v6_baseline_replays_with_no_requests -> AttributeError: <module 'world' …> does not have the attribute 'LULL_QUIET'
ERROR: LullTest.test_t10_lulls_are_recorded -> KeyError: 'lull'
ERROR: LullTest.test_t1_the_numbers -> AttributeError: module 'world' has no attribute 'LULL_QUIET'
ERROR: LullTest.test_t1a_the_room_must_be_still_for_9_minutes -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t1b_the_person_must_not_have_been_asked_for_12_minutes -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t1c_a_social_trigger_comes_first -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t1d_an_inner_moment_comes_first -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t1e_t8_t9_alone_after_leaving -> KeyError: 'lull'
ERROR: LullTest.test_t1f_carrying_on_searching_stirs_the_room -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t1i_a_fallback_counts_as_asked -> AttributeError: 'Morning' object has no attribute 'last_stir'
ERROR: LullTest.test_t2_a_still_room_is_never_talking -> AttributeError: module 'world' has no attribute 'LULL_QUIET'
ERROR: LullTest.test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place -> AttributeError: module 'world' has no attribute 'LULL_QUIET'
ERROR: LullTest.test_t4_nothing_else_in_the_prompt_changes -> TypeError: Morning.prompt_for() takes 4 positional arguments but 5 were given
ERROR: LullTest.test_t5_nothing_changes_before_the_first_lull -> AttributeError: <module 'world' …> does not have the attribute 'LULL_QUIET'
ERROR: LullTest.test_t8_nobody_is_alone_more_than_3_turns_without_being_asked -> AttributeError: module 'world' has no attribute 'LULL_QUIET'
FAIL: DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought -> AssertionError: Items in the second set but not the first: 'lull'
FAIL: LullTest.test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull -> AssertionError: CacheMiss not raised
```

- **Every new test failed except T11**, `test_t11_v8_still_replays`. It passed before the
  change because the v8 freeze (`c6fdcc4`) came first. It guards that freeze, so it has nothing
  to fail on before the lull code.
- **T6 failed on the real caches for the right reason.** With no lulls, the v6 baseline
  replays to the end, so no `CacheMiss` is raised.

### After the change

A first run after the implementation had 2 failures:
- T4, on Daniel's near-budget prompt (see "T4's state" above);
- the transcript-keys test, which met the `aside` key (see change 2 above).

Both were fixed in the tests only. The final run:

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning
exit=0
…
test_with_lulls_off_the_v6_baseline_replays_with_no_requests (…) … ok
test_t10_lulls_are_recorded (test_morning.LullTest.test_t10_lulls_are_recorded) ... ok
test_t11_v8_still_replays (test_morning.LullTest.test_t11_v8_still_replays) ... ok
test_t1_the_numbers (test_morning.LullTest.test_t1_the_numbers) ... ok
test_t1a_the_room_must_be_still_for_9_minutes (test_morning.LullTest.test_t1a_the_room_must_be_still_for_9_minutes) ... ok
test_t1b_the_person_must_not_have_been_asked_for_12_minutes (…) ... ok
test_t1c_a_social_trigger_comes_first (test_morning.LullTest.test_t1c_a_social_trigger_comes_first) ... ok
test_t1d_an_inner_moment_comes_first (test_morning.LullTest.test_t1d_an_inner_moment_comes_first) ... ok
test_t1e_t8_t9_alone_after_leaving (…) … ok
test_t1f_carrying_on_searching_stirs_the_room (…) ... ok
test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not (…) ... ok
test_t1i_a_fallback_counts_as_asked (test_morning.LullTest.test_t1i_a_fallback_counts_as_asked) ... ok
test_t2_a_still_room_is_never_talking (test_morning.LullTest.test_t2_a_still_room_is_never_talking) ... ok
test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place (…) ... ok
test_t4_nothing_else_in_the_prompt_changes (test_morning.LullTest.test_t4_nothing_else_in_the_prompt_changes) ... ok
test_t5_nothing_changes_before_the_first_lull (…) ... ok
test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull (…) … ok
test_t8_nobody_is_alone_more_than_3_turns_without_being_asked (…) ... ok
----------------------------------------------------------------------
Ran 86 tests in 36.267s

OK
```

All 86 result lines in the verbose output end in `ok` (command 4). The suite takes about 36 s,
up from 17 s, mostly from T2, T3, T5 and T8's fake mornings and T11's subprocess.

## T6: where the paired v6 baseline stops

`t6_show.py` (scratchpad, reproduced below) does what T6 does and prints it:
- it copies each `cache/v6/gemini-3.5-flash-lite-daniel_ate_it-seedN.json` to a temp directory;
- it replays it with the v9 code in replay mode, with no client;
- it prints where the morning stops and the prompt's "Now" block.

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe "$S/t6_show.py"
seed 1: stopped at minute 42, Mara: CacheMiss
   line: Nothing has been said or done in the kitchen since minute 33.
   answers from the v6 cache: 41; API requests: 0
   completed turns identical to runs/v6/daniel_ate_it-seed1.transcript.json: True (14 turns)
   , you are in the kitchen.
   - Daniel is here, staying put.
   - Elena is here, staying put.
   - Leo is here, staying put.
   - 2 portions on the shelf.
   Nothing has been said or done in the kitchen since minute 33.
   You are the first to act in the kitchen this turn.
   What you have been doing: you have stayed put and said nothing, 3 turns in a row.
   In that time nobody has said anything to you or to everyone.
seed 2: stopped at minute 51, Elena: CacheMiss
   line: Nothing has been said or done in the kitchen since minute 42.
   answers from the v6 cache: 53; API requests: 0
   completed turns identical to runs/v6/daniel_ate_it-seed2.transcript.json: True (17 turns)
   , you are in the kitchen.
   - Daniel is here, staying put.
   - Leo is here, staying put.
   - Mara is here, staying put.
   - 2 portions on the shelf.
   Nothing has been said or done in the kitchen since minute 42.
   You are the first to act in the kitchen this turn.
   What you have been doing: you have stayed put and said nothing, 3 turns in a row.
   In that time nobody has said anything to you or to everyone.
seed 3: stopped at minute 15, Daniel: CacheMiss
   line: Nothing has been said or done in the kitchen since minute 03.
   answers from the v6 cache: 10; API requests: 0
   completed turns identical to runs/v6/daniel_ate_it-seed3.transcript.json: True (5 turns)
   , you are in the kitchen.
   - Elena is here, staying put.
   - Leo is here, staying put.
   - Mara is here, staying put.
   - 2 portions on the shelf.
   Nothing has been said or done in the kitchen since minute 03.
   Said and done in the kitchen this turn, before you, in order:
   1. Elena stays put and says nothing.
   2. Mara stays put and says nothing.
   What you have been doing: you have stayed put and said nothing, 3 turns in a row.
   In that time nobody has said anything to you or to everyone.
exit=0
```

Against the design (§4, T6):

| Seed | Stops at | Answers from the cache | Line |
|---|---|---|---|
| 1 | minute 42, Mara | 41 | since minute 33 |
| 2 | minute 51, Elena | 53 | since minute 42 |
| 3 | minute 15, Daniel | 10 | since minute 03 |

- Every one matches the design, and the minutes match `lull_sim.py`'s still-since values.
- Every completed turn before the stop equals v6's.
- In seed 3, Elena and Mara acted before Daniel in the stopping turn. Both were silent in v6,
  and his prompt shows exactly that.

## v8 still replays

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe v8/check.py
daniel_ate_it_leo_heard-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

## Commands run

No command called the API: every test and script ran with `GEMINI_API_KEY` unset, the test
clients are fakes or scripted, and every replay has no client. `$S` is the session scratchpad.

1. `git add reports/kitchen_audit.md && git commit` gave `4b63c42`.
2. **The freeze:**
   - `cp data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py story.py talk.py world.py v8/`.
   - v8/check.py was made from v7/check.py, with its version, paths and RUNS changed to
     runs/v8's three `daniel_ate_it_leo_heard` mornings.
   - `v8/check.py` then reported 3 × IDENTICAL, exit 0.
   - morning.py `--out` default changed from v8 to v9, and `.gitignore` got two lines.
   - `unittest` gave "Ran 69 tests … OK".
   - `git commit` gave `c6fdcc4`.
3. **Tests written**, then the suite was run: see "Before the change".
4. **world.py, story.py and morning.py edited**, then the suite was run (2 test fixes, see
   above), then `unittest -v`: see "After the change".
   - `grep -E "(ok|ERROR|FAIL)$" after.txt | wc -l` gave `86`.
5. `t6_show.py`: see the T6 section.
6. **T4's state, the minute-12 prompt sizes in a fresh morning,** from
   `estimate_tokens(SYSTEM + prompt_for(p, 4, opts))` without and with the line:
   ```
   daniel 1394 1391
   elena 1364 1382
   leo 1324 1341
   mara 1373 1391
   ```
   Daniel's goes down with the line because trimming cut a backstory line to make room.
7. `git commit` gave `1c50d44`.
8. `v8/check.py`: see above.
9. `git status --short` gave only the three `runs/v6/daniel_ate_it-seed*.replay.md`.

### Script: `$S/t6_show.py`
```python
"""T6, shown: replays the v6 baseline caches (copies, in a temp dir) with the v9 code in replay
mode (no client), and prints where each morning stops. No API, no files written in the repo."""
import json, os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
import gemini
from gemini import Cache, Oracle
from world import Morning

MODEL = "gemini-3.5-flash-lite"
tmp = tempfile.mkdtemp()
for seed in (1, 2, 3):
    name = f"daniel_ate_it-seed{seed}"
    path = os.path.join(tmp, name + ".json")
    shutil.copy(os.path.join("cache", "v6", f"{MODEL}-{name}.json"), path)
    oracle = Oracle(Cache(path), MODEL, seed, client=None, replay=True)
    prompts = []

    class Rec:
        def ask(self, system, prompt):
            prompts.append(prompt)
            return oracle.ask(system, prompt)
    m = Morning(Rec(), seed)
    try:
        for t in range(m.turns):
            m.turn(t)
        print(f"seed {seed}: no stop")
    except gemini.CacheMiss as stop:
        last = prompts[-1]
        who = re.match(r"You are (\w+),", last).group(1)
        minute = re.search(r"^Now, minute (\d+)", last, flags=re.M).group(1)
        line = next(x for x in last.splitlines() if x.startswith("Nothing has been said"))
        v6 = json.load(open(os.path.join("runs", "v6", name + ".transcript.json"), encoding="utf-8"))
        tr = json.loads(json.dumps(m.transcript))
        for turn in tr["turns"]:
            for a in turn["acts"]:
                a.pop("lull")
        done = [t for t in v6["turns"] if t["minute"] < int(minute)]
        print(f"seed {seed}: stopped at minute {minute}, {who}: {type(stop).__name__}")
        print(f"   line: {line}")
        print(f"   answers from the v6 cache: {oracle.from_cache}; API requests: {oracle.api_requests}")
        print(f"   completed turns identical to runs/v6/{name}.transcript.json: "
              f"{tr['turns'] == done} ({len(done)} turns)")
        block = last.split(f"Now, minute {minute}")[1].split("Your options:")[0].strip().splitlines()
        print("   " + "\n   ".join(block))
shutil.rmtree(tmp)
```

## The diff

`git diff c6fdcc4 1c50d44`: world.py, story.py and morning.py, then test_morning.py.

```diff
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 2403916..81a2d6d 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -95,6 +95,7 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         "routine_decisions": sum(d["mode"] == "routine" for d in all_d),
         "lines_spoken": len(morning.said),
         "inner_moments": sum(1 for d in all_d if d.get("inner")),
+        "lull_moments": sum(1 for d in all_d if d.get("lull") is not None),
         "private_talks": sum(1 for d in all_d if d["option"] in ("accept_aside", "refuse_aside")),
         "max_prompt_tokens_estimated": morning.max_prompt_tokens,
         "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
@@ -104,7 +105,7 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
     }
     say(f"\nwrote {meta['story']}")
     for k in ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
-              "routine_decisions", "lines_spoken", "inner_moments", "private_talks",
+              "routine_decisions", "lines_spoken", "inner_moments", "lull_moments", "private_talks",
               "max_prompt_tokens_estimated",
               "max_prompt_tokens_counted_by_api", "run_seconds",
               "story_sha256"):
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index 4b42ed0..3c6f3a2 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -4,8 +4,8 @@ Everything here comes from the morning's own record, so the same answers always
 the same bytes: no clock, no call counts, no run time.
 """
 import data
-from world import (FALL_EVERY, FEELING_SHOWS_FOR_TURNS, INNER_EVERY, KIND_DONE, QUIET_TURNS,
-                   grudge_facts, hunger_words, trait_words)
+from world import (FALL_EVERY, FEELING_SHOWS_FOR_TURNS, INNER_EVERY, KIND_DONE, LULL_EVERY, LULL_QUIET,
+                   QUIET_TURNS, grudge_facts, hunger_words, trait_words)
 
 DAYS_KNOWN = {"did": "did it", "saw": "saw it", "heard": "heard it"}
 ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
@@ -65,6 +65,8 @@ def decision_line(d, fold=None):
     order = f" ({ORDINAL[d['place']]} to act in the {data.ROOMS[d['room']]}: {d['order_reason']})"
     if d.get("inner"):
         because = "**Inner moment**, nothing social happening: " + "; ".join(d["inner"])
+    elif d.get("lull") is not None:
+        because = f"**Lull**, nothing said or done in the {data.ROOMS[d['room']]} since minute {d['lull']:02d}"
     else:
         because = "Social moment: " + "; ".join(d["triggers"])
     held = (f" Not offered: {KIND_DONE[d['held_back']]} three turns in a row, so no more of it "
@@ -188,6 +190,10 @@ def render(morning, seed, model_name, command):
     w(f"- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has "
       f"risen a level since they last decided with the model; the model is asked, at most once "
       f"every {INNER_EVERY} minutes per person. What rose is listed.")
+    w(f"- **Lull**: nothing social or inner, but nothing has been said or done in their room for at "
+      f"least {LULL_QUIET} minutes (staying put in silence and staying seated do not count), and they "
+      f"have not been asked for at least {LULL_EVERY} minutes; the model is asked, and told since when "
+      "the room has been still.")
     w("- **Take aside**: someone can ask a person in the room who has not acted yet this turn to "
       "come to an empty room. That person answers at once (their decision for the turn): go, and "
       "both move there and can talk alone; or refuse.")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index dadbbae..05da32a 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -13,6 +13,10 @@ Inside each person the rules keep hunger, a suspicion (a person and a strength f
 whoever took the can (the scenario says who, if anyone), guilt. The model is shown the
 events behind them as plain facts, with at most a
 neutral level word; the numbers themselves only decide when an inner moment comes.
+
+A lull moment asks the model for someone nothing social or inner has happened to, when the
+room they are in has been still for a while and they have not been asked for a while; their
+prompt says since when nothing has been said or done there (reports/lull_design.md).
 """
 import json
 import random
@@ -52,6 +56,8 @@ PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,370 at most in the s
 QUIET_TURNS = 2              # full turns with nothing new that end a conversation
 INNER_EVERY = 9              # minutes: an inner moment at most this often per person
 FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one step this often
+LULL_QUIET = 9               # minutes a room must be still before a lull (None: no lulls)
+LULL_EVERY = 12              # minutes since a person was last asked before a lull
 
 KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
     "ask": "asked who took the can", "deny": "denied taking it",
@@ -225,6 +231,7 @@ class Person:
         self.guilt_events = []      # (minute, fact)
         self.seen = None            # the levels they were shown when they last decided
         self.last_inner = None      # minute of their last inner moment
+        self.last_asked = None      # minute of their last model decision of any kind
 
     def grudge(self, against):
         return self.grudges.setdefault(against, Grudge())
@@ -261,6 +268,9 @@ class Morning:
         self.moved_by_inner = {}    # during a turn: person -> did an inner moment move them
         self.transcript = {"seed": seed, "scenario": scenario, "culprit": self.culprit, "turns": []}
         self.convo_told = 0         # how much of the conversation log the turn records hold
+        # room -> the minute something other than staying put in silence, or staying seated,
+        # was last done in it (the count at minute 00 was done in the kitchen)
+        self.last_stir = {"kitchen": 0}
         for p in self.people.values():
             how = "did it" if p.id == "elena" else "saw it"
             p.sure.append(f"min 00: {data.OPENING} (you {how})")
@@ -489,7 +499,8 @@ class Morning:
                 "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone"
                 }.get(h["kind"], "spoke to everyone")
 
-    def prompt_for(self, p, t, opts):
+    def prompt_for(self, p, t, opts, lull=None):
+        """lull: for a lull moment, the minute the room was last stirred; None otherwise."""
         s = p.sheet
         minute = t * data.MINUTES_PER_TURN
         calls = "; ".join(f"{self.people[q].name} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
@@ -512,6 +523,8 @@ class Morning:
             now.append(f"- {q.name} is here, {q.activity['label']}.{look}")
         if p.room == "kitchen":
             now.append(f"- {self.portions} portion{'s' if self.portions != 1 else ''} on the shelf.")
+        if lull is not None:
+            now.append(f"Nothing has been said or done in the {room} since minute {lull:02d}.")
         so_far = self.so_far[p.room] if self.so_far is not None else []
         if so_far:
             now.append(f"Said and done in the {room} this turn, before you, in order:")
@@ -669,7 +682,7 @@ class Morning:
                      "decided_at": [minute, d["seq"]], "said_at": [minute, d["seq"]],
                      "came_of_it": d["came_of_it"], "new": d.get("new"), "new_why": d.get("new_why"),
                      "inner": d.get("inner_families"), "suspects": d.get("suspects"),
-                     "angry_at": d.get("angry_at"),
+                     "angry_at": d.get("angry_at"), "lull": d.get("lull"),
                      "moved_to": opt.act["to"] if opt.act["kind"] in ("go", "accept_aside") else None}
             tturn["acts"].append(entry)
             return opt, entry
@@ -705,6 +718,7 @@ class Morning:
         for p, to, partner in self.moves:
             p.room = to
             p.activity = {"kind": "idle", "label": "just come in"}
+            self.last_stir[to] = minute         # coming in is something done in the room
         # Voices carry to everyone who did not hear the words, wherever they are at the end of
         # the turn, never into or out of the bathroom. Only a new line is a social moment for
         # someone who hears it through a wall.
@@ -744,7 +758,8 @@ class Morning:
         grudge. They have now seen the levels their prompt showed."""
         minute = t * data.MINUTES_PER_TURN
         seen = p.levels()
-        prompt = self.prompt_for(p, t, opts)
+        prompt = self.prompt_for(p, t, opts, d.get("lull"))
+        p.last_asked = minute
         text = self.oracle.ask(SYSTEM, prompt)
         p.seen = seen
         choice, why = self.parse(text, opts)
@@ -794,7 +809,9 @@ class Morning:
                 d["inner_kinds"] = rose
                 d["inner_families"] = list(dict.fromkeys(k.split(":")[0] for k in rose))
                 d["inner"] = self.rise_words(p, rose)
-        if triggers or d.get("inner_kinds"):
+        if not triggers and not d.get("inner_kinds") and self.lull_due(p, minute):
+            d["lull"] = self.last_stir[p.room]
+        if triggers or d.get("inner_kinds") or "lull" in d:
             choice, why = self.ask_model(p, t, opts, d)
             if not choice:
                 d.update(mode="fallback", invalid=why, option=self.routine(p, opts), say=None)
@@ -805,6 +822,14 @@ class Morning:
         d["_opt"] = opt
         return d
 
+    def lull_due(self, p, minute):
+        """Their room has been still for LULL_QUIET minutes, and they have not been asked for
+        LULL_EVERY minutes."""
+        if LULL_QUIET is None or p.room not in self.last_stir:
+            return False
+        return (minute - self.last_stir[p.room] >= LULL_QUIET
+                and (p.last_asked is None or minute - p.last_asked >= LULL_EVERY))
+
     def decide_aside(self, q, p, to, t):
         """q has been asked aside by p: go with them or refuse. Always a model decision."""
         opts = [Option("accept_aside", f"go with {p.name} to the {data.ROOMS[to]}", kind="accept_aside",
@@ -866,6 +891,10 @@ class Morning:
         target_id = aimed_at(opt.id) or (opt.act.get("target") if kind == "sit" else None)
         target = self.people[target_id] if target_id else None
         partner = self.people[opt.act["partner"]] if "partner" in opt.act else None
+        # Anything but staying put in silence, or staying seated with the same person, stirs the room.
+        if not (kind == "silent" or (kind == "sit" and p.activity["kind"] == "sitting"
+                                     and p.activity["with"] == target_id)):
+            self.last_stir[room] = minute
         p.history.append({"t": t, "kind": kind, "seq": self.seq})
         p.addressed = None
         p.aside_lead = None
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 6409409..61c5022 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -10,12 +10,16 @@ import json
 import os
 import re
 import shutil
+import subprocess
+import sys
 import tempfile
 import unittest
+from unittest import mock
 
 import data
 import metrics
 import gemini
+import world
 from gemini import Cache, FakeClient, GeminiClient, Oracle
 from morning import run
 from story import render
@@ -921,6 +925,15 @@ def frozen(version, module):
     return loaded
 
 
+def without_lull(transcript):
+    """A transcript as JSON would hold it, without the `lull` key that every act has since v9."""
+    tr = json.loads(json.dumps(transcript))
+    for turn in tr["turns"]:
+        for a in turn["acts"]:
+            a.pop("lull", None)
+    return tr
+
+
 V6_RUNS = os.path.join(HERE, "runs", "v6")
 V6_CACHE = os.path.join(HERE, "cache", "v6")
 V6_MODEL = "gemini-3.5-flash-lite"
@@ -979,28 +992,35 @@ class DecisionFormatTest(unittest.TestCase):
         def keys(path):
             tr = json.loads(read(path))
             return {k for turn in tr["turns"] for a in turn["acts"] for k in a}
-        self.assertEqual(keys(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")),
-                         keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")))
-
-    def test_the_v6_baseline_replays_byte_for_byte_with_no_requests(self):
+        # v9 adds one key to every act, `lull` (reports/lull_design.md, §3). `aside` is an older
+        # key, on acts that take someone aside only (world.py, act()); the v6 story had none.
+        self.assertEqual(keys(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")) - {"aside"},
+                         keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")) | {"lull"})
+
+    def test_with_lulls_off_the_v6_baseline_replays_with_no_requests(self):
+        """With lull moments switched off, the v6 baseline still replays in full: the transcript
+        is v6's apart from the `lull` key on each act, and the story is v6's apart from the key's
+        one line about lulls (reports/lull_design.md, §3 and T12)."""
         for seed in (1, 2, 3):
             name = f"daniel_ate_it-seed{seed}"
             path = os.path.join(self.dirs.root, f"{name}.json")
             shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
             oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
-            m = Morning(oracle, seed)
-            try:
-                for t in range(m.turns):
-                    m.turn(t)
-            except gemini.StopMorning as stop:
-                self.fail(f"seed {seed}: {stop}")
+            with mock.patch.object(world, "LULL_QUIET", None):
+                m = Morning(oracle, seed)
+                try:
+                    for t in range(m.turns):
+                        m.turn(t)
+                except gemini.StopMorning as stop:
+                    self.fail(f"seed {seed}: {stop}")
             m.finish()
             text = render(m, seed, V6_MODEL, f"python morning.py --seed {seed}")
-            self.assertTrue(text.encode("utf-8") == read(os.path.join(V6_RUNS, name + ".md"), "rb"),
-                            f"seed {seed}: the story differs from runs/v6/{name}.md")
-            self.assertTrue(json.loads(json.dumps(m.transcript))
-                            == json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json"))),
-                            f"seed {seed}: the transcript differs")
+            old = read(os.path.join(V6_RUNS, name + ".md"))
+            extra = [x for x in text.splitlines() if x not in old.splitlines()]
+            self.assertEqual([x[:10] for x in extra], ["- **Lull**"], seed)
+            self.assertEqual([x for x in text.splitlines() if x not in extra], old.splitlines(), seed)
+            self.assertEqual(without_lull(m.transcript),
+                             json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json"))), seed)
             self.assertEqual((oracle.api_requests, oracle.live), (0, 0), seed)
 
 
@@ -1182,6 +1202,331 @@ class WitnessScenarioTest(unittest.TestCase):
             self.assertLessEqual(estimate_tokens(SYSTEM + new), PROMPT_TOKEN_BUDGET, seed)
 
 
+LULL_LINE = re.compile(r"^Nothing has been said or done in the (kitchen|brothers room|back room|bathroom) "
+                       r"since minute (\d\d)\.$", flags=re.M)
+HUNGRIER = "Since you last decided, you have grown hungrier."
+
+
+class Recorder:
+    """Passes each question on to an oracle, and keeps every prompt in the order it was asked."""
+
+    def __init__(self, oracle):
+        self.oracle, self.prompts = oracle, []
+
+    def ask(self, system, prompt):
+        self.prompts.append(prompt)
+        return self.oracle.ask(system, prompt)
+
+
+class Watched(Morning):
+    """Keeps, for every decision, whether it was a lull and whether its room was talking then."""
+
+    def decide(self, p, t):
+        d = super().decide(p, t)
+        self.__dict__.setdefault("at_decision", []).append((t, p.id, d.get("lull"), self.talking(p.room)))
+        return d
+
+
+class Broken:
+    requests = 0
+
+    def generate(self, system, prompt):
+        self.requests += 1
+        return "not json"
+
+
+def asked(m):
+    """The decisions the model was asked for, in the order they were asked."""
+    return [d for rec in m.log for d in rec["decisions"] if d["mode"] != "routine"]
+
+
+def longest_alone_routine(transcript):
+    """P3's count (reports/lull_design.md, §7): the longest run of turns, for any one person, in
+    which they start the turn alone in a room and act by routine."""
+    best, run = 0, {}
+    for turn in transcript["turns"]:
+        for a in turn["acts"]:
+            alone = turn["rooms"][a["room"]] == [a["who"]]
+            run[a["who"]] = run.get(a["who"], 0) + 1 if alone and a["mode"] == "routine" else 0
+            best = max(best, run[a["who"]])
+    return best
+
+
+class LullTest(unittest.TestCase):
+    """Lull moments (reports/lull_design.md, sections 1 to 3; tests T1 to T11 of section 5)."""
+
+    def setUp(self):
+        self.dirs = Dirs()
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def fake(self, seed, lulls=True):
+        """A fake-model morning; with lulls=False, lull moments are switched off."""
+        rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"f{seed}-{lulls}.json")), "fake", seed,
+                              client=FakeClient()))
+        with mock.patch.object(world, "LULL_QUIET", world.LULL_QUIET if lulls else None):
+            m = Watched(rec, seed).run()
+        return m, rec
+
+    def still_kitchen(self, client=None):
+        """Everyone in the kitchen, no talk, no triggers, nothing risen since they last decided."""
+        client = client or Scripted(lambda *a: ("silent", None))
+        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "still.json")), "fake", 1, client=client), 1)
+        m.convos.active["kitchen"] = False
+        for p in m.people.values():
+            p.triggers = []
+            p.seen = p.levels()
+        return m
+
+    # T1
+    def test_t1_the_numbers(self):
+        self.assertEqual((world.LULL_QUIET, world.LULL_EVERY), (9, 12))
+
+    def test_t1a_the_room_must_be_still_for_9_minutes(self):
+        m = self.still_kitchen()
+        mara = m.people["mara"]
+        m.last_stir["kitchen"], mara.last_asked = 9, 3
+        d = m.decide(mara, 5)                                   # minute 15: still for 6
+        self.assertEqual(d["mode"], "routine")
+        self.assertNotIn("lull", d)
+        self.assertEqual(mara.last_asked, 3)
+        m.last_stir["kitchen"] = 6                              # still for 9
+        d = m.decide(mara, 5)
+        self.assertEqual((d["mode"], d["lull"], d["triggers"]), ("model", 6, []))
+        self.assertNotIn("inner", d)
+        self.assertEqual(mara.last_asked, 15)
+
+    def test_t1b_the_person_must_not_have_been_asked_for_12_minutes(self):
+        m = self.still_kitchen()
+        mara = m.people["mara"]
+        m.last_stir["kitchen"], mara.last_asked = 6, 6
+        d = m.decide(mara, 5)                                   # asked 9 minutes ago
+        self.assertEqual(d["mode"], "routine")
+        self.assertNotIn("lull", d)
+        mara.last_asked = 3                                     # 12 minutes ago
+        self.assertEqual(m.decide(mara, 5)["lull"], 6)
+
+    def test_t1c_a_social_trigger_comes_first(self):
+        m = self.still_kitchen()
+        mara = m.people["mara"]
+        m.last_stir["kitchen"] = 0
+        mara.triggers = [("Elena says to everyone: \"Sit down.\"", True)]
+        d = m.decide(mara, 5)
+        self.assertEqual((d["mode"], d["triggers"]), ("model", ['Elena says to everyone: "Sit down."']))
+        self.assertNotIn("lull", d)
+
+    def test_t1d_an_inner_moment_comes_first(self):
+        m = self.still_kitchen()
+        mara = m.people["mara"]
+        m.last_stir["kitchen"], mara.last_inner = 0, 3
+        mara.hunger = 0.9                                       # risen since she last decided
+        d = m.decide(mara, 5)
+        self.assertEqual(d["inner_kinds"], ["hunger"])
+        self.assertNotIn("lull", d)
+
+    def test_t1e_t8_t9_alone_after_leaving(self):
+        """Leo goes to the back room at minute 0 and then stays silent: routine at 3, 6 and 9,
+        a lull at 12; his leaving is no trigger for the others."""
+        def policy(who, minute, options, client):
+            return ("go_back_room", None) if (who, minute) == ("leo", 0) else ("silent", None)
+        m, client = scripted(policy, self.dirs)
+        leo = [(rec["minute"], d) for rec in m.log for d in rec["decisions"] if d["person"] == "leo"]
+        self.assertEqual([d["mode"] for _, d in leo[1:4]], ["routine"] * 3)
+        self.assertEqual((leo[4][0], leo[4][1]["mode"], leo[4][1]["lull"]), (12, "model", 0))
+        self.assertIn("Nothing has been said or done in the back room since minute 00.",
+                      next(p for minute, who, p in client.prompts if (minute, who) == (12, "leo")))
+        # Every lull, anyone's, comes 12 or more minutes after that person was last asked.
+        last = {}
+        for rec in m.log:
+            for d in rec["decisions"]:
+                if d.get("lull") is not None:
+                    self.assertGreaterEqual(rec["minute"] - last[d["person"]], 12, d["person"])
+                if d["mode"] != "routine":
+                    last[d["person"]] = rec["minute"]
+        # T8: P3's count.
+        self.assertEqual(longest_alone_routine(m.transcript), 3)
+        # T9: the others were told he left, and it was no trigger for them.
+        for pid in ("daniel", "elena", "mara"):
+            self.assertIn((0, "Leo leaves for the back room."), m.people[pid].memory)
+        for rec in m.log[:2]:
+            for d in rec["decisions"]:
+                self.assertFalse([x for x in d["triggers"] if "leaves for" in x], d)
+
+    def test_t1f_carrying_on_searching_stirs_the_room(self):
+        def policy(who, minute, options, client):
+            return ("search", None) if (who, minute) == ("mara", 0) else ("silent", None)
+        m, _ = scripted(policy, self.dirs, turns=4)
+        self.assertEqual([d["option"] for d in m.log[1]["decisions"] if d["person"] == "mara"],
+                         ["keep_searching"])
+        self.assertEqual(m.last_stir["kitchen"], 3)
+        self.assertFalse([d for rec in m.log for d in rec["decisions"] if d.get("lull") is not None])
+
+    def test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not(self):
+        m = self.still_kitchen()
+        dan = m.people["daniel"]
+        m.last_stir["kitchen"] = 0
+
+        def do(option, t, mode):
+            in_turn(m)
+            opt = next(o for o in m.options_for(dan) if o.id == option)
+            m.apply(dan, opt, {"mode": mode, "say": None, "feeling": "calm"}, t, [], new_record())
+            out_of_turn(m)
+        do("sit_mara", 4, "model")                              # sits down: minute 12
+        self.assertEqual(m.last_stir["kitchen"], 12)
+        do("sit_mara", 5, "routine")                            # stays seated
+        do("silent", 6, "model")                                # a model's silence
+        do("silent", 7, "routine")
+        self.assertEqual(m.last_stir["kitchen"], 12)
+        in_turn(m)
+        opt = next(o for o in m.options_for(dan) if o.id == "reassure_all")
+        m.apply(dan, opt, {"mode": "model", "say": "It will be all right.", "feeling": "calm"}, 8, [],
+                new_record())
+        self.assertEqual(m.last_stir["kitchen"], 24)            # a line stirs it
+
+    def test_t1i_a_fallback_counts_as_asked(self):
+        m = self.still_kitchen(client=Broken())
+        mara = m.people["mara"]
+        m.last_stir["kitchen"] = 0
+        d = m.decide(mara, 5)
+        self.assertEqual((d["mode"], d["lull"]), ("fallback", 0))
+        self.assertEqual(mara.last_asked, 15)
+
+    # T2
+    def test_t2_a_still_room_is_never_talking(self):
+        lulls = 0
+        for seed in range(1, 6):
+            m, _ = self.fake(seed)
+            for t, pid, lull, talking in m.at_decision:
+                if lull is not None:
+                    lulls += 1
+                    self.assertFalse(talking, (seed, t, pid))
+        self.assertGreater(lulls, 0)
+
+    # T3, T7
+    def test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place(self):
+        lulls = 0
+        for seed in range(1, 6):
+            m, rec = self.fake(seed)
+            decisions = asked(m)
+            self.assertEqual(len(decisions), len(rec.prompts), seed)
+            for d, prompt in zip(decisions, rec.prompts):
+                if d.get("lull") is None:
+                    self.assertNotIn("Nothing has been said or done in the", prompt)
+                    continue
+                lulls += 1
+                self.assertEqual(LULL_LINE.findall(prompt), [(data.ROOMS[d["room"]], f"{d['lull']:02d}")])
+                self.assertEqual(prompt.count("Nothing has been said or done in the"), 1)
+                lines = prompt.splitlines()
+                i = next(k for k, x in enumerate(lines) if LULL_LINE.match(x))
+                self.assertRegex(lines[i - 1], r"^(- |Now, minute \d\d, you are in the )")
+                self.assertRegex(lines[i + 1], r"^(Said and done in the |You are the first to act in the |"
+                                               r"What you have been doing: |Your options:)")
+                self.assertTrue(any(x.startswith("Now, minute ") for x in lines[:i]))
+                self.assertNotIn(HUNGRIER, prompt)                        # T7
+        self.assertGreater(lulls, 0)
+
+    # T4
+    def test_t4_nothing_else_in_the_prompt_changes(self):
+        # Leo's first prompt has the most room under the budget (1,324 estimated tokens at minute 12).
+        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "t4.json")), "fake", 1, client=FakeClient()), 1)
+        leo = m.people["leo"]
+        opts = m.options_for(leo)
+        plain, lull = m.prompt_for(leo, 4, opts), m.prompt_for(leo, 4, opts, 0)
+        diff = [x for x in difflib.ndiff(plain.splitlines(), lull.splitlines()) if x[:2] in ("+ ", "- ")]
+        self.assertEqual(diff, ["+ Nothing has been said or done in the kitchen since minute 00."])
+        self.assertLessEqual(estimate_tokens(SYSTEM + lull), PROMPT_TOKEN_BUDGET)
+        for prompt in (plain, lull):
+            self.assertNotIn("(earlier things, left out here)", prompt)
+        self.assertEqual(plain.split("Your options:")[1], lull.split("Your options:")[1])
+
+    # T5
+    def test_t5_nothing_changes_before_the_first_lull(self):
+        lulls = 0
+        for seed in range(1, 6):
+            off, rec_off = self.fake(seed, lulls=False)
+            on, rec_on = self.fake(seed)
+            first = next((i for i, p in enumerate(rec_on.prompts) if "Nothing has been said or done in the" in p),
+                         len(rec_on.prompts))
+            lulls += first < len(rec_on.prompts)
+            self.assertEqual(rec_on.prompts[:first], rec_off.prompts[:first], seed)
+            acts_on = [a for turn in on.transcript["turns"] for a in turn["acts"]]
+            acts_off = [a for turn in off.transcript["turns"] for a in turn["acts"]]
+            self.assertTrue(all(a["lull"] is None for a in acts_off), seed)
+            j = next((k for k, a in enumerate(acts_on) if a["lull"] is not None), len(acts_on))
+            strip = lambda acts: [{k: v for k, v in a.items() if k != "lull"} for a in acts[:j]]
+            self.assertEqual(strip(acts_on), strip(acts_off), seed)
+        self.assertGreater(lulls, 0)
+
+    # T6
+    def test_t6_the_v6_baseline_caches_pair_up_to_the_first_lull(self):
+        """Replayed on the v6 answers with no client, the morning is v6's until the first lull,
+        whose prompt is not in the cache: seed 1 min 42 Mara, seed 2 min 51 Elena, seed 3 min 15
+        Daniel, after 41, 53 and 10 answers from the cache (reports/lull_design.md, §4)."""
+        expected = {1: (42, "mara", 41, 33), 2: (51, "elena", 53, 42), 3: (15, "daniel", 10, 3)}
+        for seed, (minute, who, served, since) in expected.items():
+            name = f"daniel_ate_it-seed{seed}"
+            path = os.path.join(self.dirs.root, f"{name}.json")
+            shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
+            oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
+            rec = Recorder(oracle)
+            m = Morning(rec, seed)
+            with self.assertRaises(gemini.CacheMiss):
+                for t in range(m.turns):
+                    m.turn(t)
+            last = rec.prompts[-1]
+            self.assertTrue(last.startswith(f"You are {data.PEOPLE[who]['name']},"), seed)
+            self.assertIn(f"\nNow, minute {minute:02d}, you are in the kitchen.\n", last)
+            self.assertEqual(LULL_LINE.findall(last), [("kitchen", f"{since:02d}")], seed)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+            v6 = json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json")))
+            self.assertEqual(without_lull(m.transcript)["turns"],
+                             [turn for turn in v6["turns"] if turn["minute"] < minute], seed)
+            # In the turn it stops, whoever acted before was silent in v6 too, as the prompt says.
+            now = next(turn for turn in v6["turns"] if turn["minute"] == minute)
+            before = []
+            for a in now["acts"]:
+                if a["who"] == who:
+                    break
+                before.append(a)
+            self.assertTrue(all(a["option"] == "silent" for a in before), seed)
+            for i, a in enumerate(before, 1):
+                self.assertIn(f"\n{i}. {data.PEOPLE[a['who']]['name']} stays put and says nothing.\n", last)
+            if not before:
+                self.assertIn("\nYou are the first to act in the kitchen this turn.\n", last)
+
+    # T8 on fake mornings
+    def test_t8_nobody_is_alone_more_than_3_turns_without_being_asked(self):
+        for seed in range(1, 6):
+            m, _ = self.fake(seed)
+            self.assertLessEqual(longest_alone_routine(m.transcript), 3, seed)
+
+    # T10
+    def test_t10_lulls_are_recorded(self):
+        total = 0
+        for seed in (1, 2, 3):
+            (meta, code), out = fake_morning(self.dirs, seed=seed)
+            self.assertEqual(code, 0, out)
+            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))
+            acts = [a for turn in tr["turns"] for a in turn["acts"] if a["lull"] is not None]
+            self.assertEqual(meta["lull_moments"], len(acts), seed)
+            self.assertTrue(all(a["mode"] in ("model", "fallback") for a in acts), seed)
+            story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
+            self.assertEqual(len(re.findall(r"\*\*Lull\*\*, nothing said or done in the ", story)), len(acts))
+            self.assertIn("lull_moments", out)
+            total += len(acts)
+        self.assertGreater(total, 0)
+
+    # T11
+    def test_t11_v8_still_replays(self):
+        env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
+        env["PYTHONDONTWRITEBYTECODE"] = "1"
+        done = subprocess.run([sys.executable, os.path.join(HERE, "v8", "check.py")], cwd=HERE, env=env,
+                              capture_output=True, text=True, timeout=300)
+        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
+        self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
```
