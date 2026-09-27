# Implementation: the `daniel_ate_it_leo_heard` scenario

Mode: implement. Built from reports/witness_design.md, sections 1 to 3. No API call was made and
no morning was run. `GEMINI_API_KEY` was unset (`env -u`) for every test run. The sentence, the
existing scenarios and config.json are unchanged. Paths are relative to `Prototypes/llm-morning/`.

## Commits

| # | Hash | What |
|---|---|---|
| 1 | `f80e72d` | Baseline files, committed on their own: runs/v6/ (12 files), cache/v6/ (3 files), reports/baseline_v6.md. reports/witness_design.md was already tracked (commit 4b572cf), so it is not in this commit. |
| 2 | `0d42eed` | The scenario (data.py) and tests T1–T8 (test_morning.py). |

This report is committed after them, in a third commit.

Notes on commit 1:
- It was first made as `7afaf8e`, with the subject and body run together on one line. I amended
  the message only, which gave `f80e72d`. The files are the same and nothing was pushed.
- On `git add`, git printed "CRLF will be replaced by LF" for reports/baseline_v6.md and the three
  runs/v6/*.stdout.txt files. So those four are stored with LF line endings. The working copies
  were not rewritten. No other baseline file printed the warning.

## What changed

**data.py**
- data.py:118-125 adds `SCENARIOS["daniel_ate_it_leo_heard"]`. It is `daniel_ate_it`'s dict
  (the same `culprit` and the same `night` tuple) plus the key `after_night`. That key holds one
  event: `(3, <the sentence>, {"leo": "heard"})`.
- data.py:165-170: `backstory()` now puts a scenario's `after_night` events directly after its
  night. The three existing scenarios have no `after_night`, so their backstories are the same as
  before (T7).
- The existing entries at data.py:102-117 are not edited. The new scenario is added after the dict.

**test_morning.py**
- test_morning.py:90-111: the target-morning check that was inside
  `test_nothing_from_target_morning_reaches_a_prompt` is moved into the helper
  `assert_no_target_text`, so T6 can run it on the new scenario. That test (test_morning.py:225-227)
  now calls the helper. The check itself is the same code.
- test_morning.py:912-1019: `WitnessScenarioTest`, with T1–T8. The table maps each design test to
  the test that implements it:

| Design | Test | Line |
|---|---|---|
| T1 | `test_the_sentence_names_nobody_leo_heard` | 941 |
| T2 | `test_only_leos_backstory_differs` | 951 |
| T3 | `test_at_minute_00_only_leos_prompt_differs_by_the_one_line` (seeds 1, 2, 3) | 960 |
| T4 | `test_daniels_prompt_never_mentions_being_heard` | 977 |
| T5 | `test_no_prompt_says_who_leo_heard` | 988 |
| T6 | `test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning` | 1002 |
| T7 | `test_the_other_scenarios_do_not_have_the_sentence` | 1006 |
| T8 | `test_the_witness_morning_runs_and_its_story_shows_who_heard` | 1014 |

Differences from the wording in the design's section 3:
- **T1** takes the sentence from data.py (the one event the new backstory has and
  `daniel_ate_it`'s does not), checks that it equals the design's sentence with
  `{"leo": "heard"}`, and then runs the name checks on it.
- **T7** also checks that the new scenario's backstory has 14 events and holds the sentence once.
  Without that part, T7 would have passed before the change.
- **T8.** `test_each_scenario_runs_with_the_fake_model` (test_morning.py:751) already loops over
  `data.SCENARIOS`. T8 also runs the new scenario with the fake model, seed 1, and checks the
  story row.
- **The gate.** `setUp` asserts that the scenario exists (test_morning.py:923). This makes every
  test FAIL, rather than ERROR, when the scenario is missing.

Not changed:
- **morning.py:9** is the `--scenario` help in the module docstring. It still reads
  "daniel_ate_it (default), mara_ate_it or miscount". The CLI choices come from `data.SCENARIOS`
  (morning.py:136), so `--scenario daniel_ate_it_leo_heard` is accepted.
- **Run check R2** (replay of the baseline) was not run. It runs a morning, and this prompt's
  MODE is implement.

## The call cap: what it counts

**It counts only the cached answers used in this run. It does not count every entry in the cache
file.**

- gemini.py:242 checks `self.from_cache + self.client.requests >= self.max_calls`.
- `from_cache` is set to 0 when the Oracle is built (gemini.py:222).
- It goes up by 1 only in `ask()`, when the key of a prompt asked in this run is found in the
  cache (gemini.py:231-234). The key is model, seed, SYSTEM and prompt (gemini.py:196-198).
- The file's entries are loaded into `Cache.entries` (gemini.py:190-193). The cap check never
  reads them. `len(cache.entries)` is used only in console messages (morning.py:61, morning.py:73).
- `self.client.requests` counts every attempt the client makes, retries included (gemini.py:106-109).
- The same limit, `config["max_calls_per_morning"]`, is passed to the Oracle (morning.py:52-53) and
  to the client (morning.py:50 for the fake client, gemini.py:75 for GeminiClient).
- `from_cache` goes up once per hit, so if one prompt were asked twice in a run it would count
  twice.
- The existing test test_morning.py:274-281 has a cache with one entry. It asks that prompt once,
  and the cap of 1 is then reached with 0 requests.

What this means for run step R3: copying a baseline cache file into the new scenario's cache adds
nothing to the cap by itself. Only the entries whose prompts come up again in the new run count.

Commands:
```
$ grep -n "from_cache\|max_calls\|\.entries\|requests += 1\|self.requests" gemini.py morning.py world.py
gemini.py:75:        self.max_calls = config["max_calls_per_morning"]
gemini.py:80:        self.requests = 0
gemini.py:106:            if self.requests >= self.max_calls:
gemini.py:107:                raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
gemini.py:109:            self.requests += 1
gemini.py:144:    def __init__(self, invalid_every=5, fail_with=None, max_calls=150):
gemini.py:147:        self.max_calls = max_calls
gemini.py:148:        self.requests = 0
gemini.py:152:        if self.requests >= self.max_calls:
gemini.py:153:            raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
gemini.py:154:        self.requests += 1
gemini.py:155:        if self.requests in self.fail_with:
gemini.py:156:            raise self.fail_with[self.requests]
gemini.py:164:            "say": f"[fake line {self.requests}]" if speaking else None,
gemini.py:166:            "reason": f"Fake reason {self.requests}.",
gemini.py:170:        if self.invalid_every and self.requests % self.invalid_every == 0:
gemini.py:171:            kind = self.BROKEN[(self.requests // self.invalid_every - 1) % len(self.BROKEN)]
gemini.py:190:        self.entries = {}
gemini.py:193:                self.entries = json.load(f)
gemini.py:201:        entry = self.entries.get(key)
gemini.py:205:        self.entries[key] = {"prompt": prompt, "response": response, "prompt_tokens": prompt_tokens}
gemini.py:208:            json.dump(self.entries, f, ensure_ascii=False, indent=1)
gemini.py:215:    def __init__(self, cache, model_name, seed, client=None, replay=False, max_calls=None):
gemini.py:217:        self.max_calls = max_calls      # for the whole morning, answers already cached included
gemini.py:222:        self.from_cache = 0
gemini.py:234:            self.from_cache += 1
gemini.py:235:            tokens = self.cache.entries[key].get("prompt_tokens")
gemini.py:242:        if self.max_calls is not None and self.from_cache + self.client.requests >= self.max_calls:
gemini.py:243:            raise CallCapReached(f"stopped: this morning reached {self.max_calls} model calls "
gemini.py:244:                                 f"({self.from_cache} of them answered in an earlier run).")
morning.py:50:        client = (FakeClient(max_calls=config["max_calls_per_morning"]) if fake
morning.py:53:                    max_calls=config["max_calls_per_morning"])
morning.py:61:        f"cache {os.path.relpath(cache_path, HERE)} holds {len(cache.entries)} answers")
morning.py:70:                    f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
morning.py:73:        say(f"Answers received so far ({len(cache.entries)}) are kept in {os.path.relpath(cache_path, HERE)}.")
morning.py:91:        "answers_from_cache": oracle.from_cache,
morning.py:105:    for k in ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
```

## Test output before the change

Tests written, data.py not yet changed. Command:
`env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.WitnessScenarioTest`

```
test_at_minute_00_only_leos_prompt_differs_by_the_one_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_the_one_line) ... FAIL
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... FAIL
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... FAIL
test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning) ... FAIL
test_only_leos_backstory_differs (test_morning.WitnessScenarioTest.test_only_leos_backstory_differs) ... FAIL
test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence) ... FAIL
test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard) ... FAIL
test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard) ... FAIL

======================================================================
FAIL: test_at_minute_00_only_leos_prompt_differs_by_the_one_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_the_one_line)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_only_leos_backstory_differs (test_morning.WitnessScenarioTest.test_only_leos_backstory_differs)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

======================================================================
FAIL: test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 923, in setUp
    self.assertIn(WITNESS, data.SCENARIOS)
AssertionError: 'daniel_ate_it_leo_heard' not found in {'daniel_ate_it': {'culprit': 'daniel', 'night': (3, 'In the night Daniel eats a can standing at the counter in the dark. Nobody sees.', {'daniel': 'did'})}, 'mara_ate_it': {'culprit': 'mara', 'night': (3, 'In the night Mara eats a can sitting on the kitchen floor. Nobody sees.', {'mara': 'did'})}, 'miscount': {'culprit': None, 'night': None}}

----------------------------------------------------------------------
Ran 8 tests in 0.009s

FAILED (failures=8)
exit=1
```

All 8 FAIL at the `setUp` gate, because the scenario is not in `data.SCENARIOS`.

The same 8 tests were also run from a scratchpad copy of test_morning.py with the gate line
removed (and `HERE` pointed at this folder). This shows that each test fails in its own body too.
The repository file was not touched. Command and summary:
```
$ grep -v "self.assertIn(WITNESS, data.SCENARIOS)" test_morning.py | sed 's|^HERE = .*|HERE = "C:/Users/Akrem/Desktop/Projects/Fallow/Prototypes/llm-morning"|' > <scratchpad>/nogate/test_nogate.py
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -c "<load test_nogate.WitnessScenarioTest, run verbosity 2>" | grep -E "^(FAIL|ERROR):|Error:|^Ran|^FAILED|exit="
ERROR: test_at_minute_00_only_leos_prompt_differs_by_the_one_line (test_nogate.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_the_one_line)
KeyError: 'daniel_ate_it_leo_heard'
ERROR: test_daniels_prompt_never_mentions_being_heard (test_nogate.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard)
KeyError: 'daniel_ate_it_leo_heard'
ERROR: test_no_prompt_says_who_leo_heard (test_nogate.WitnessScenarioTest.test_no_prompt_says_who_leo_heard)
KeyError: 'daniel_ate_it_leo_heard'
ERROR: test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_nogate.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning)
KeyError: 'daniel_ate_it_leo_heard'
ERROR: test_only_leos_backstory_differs (test_nogate.WitnessScenarioTest.test_only_leos_backstory_differs)
KeyError: 'daniel_ate_it_leo_heard'
ERROR: test_the_sentence_names_nobody_leo_heard (test_nogate.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard)
KeyError: 'daniel_ate_it_leo_heard'
ERROR: test_the_witness_morning_runs_and_its_story_shows_who_heard (test_nogate.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard)
KeyError: 'daniel_ate_it_leo_heard'
FAIL: test_the_other_scenarios_do_not_have_the_sentence (test_nogate.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence)
AssertionError: {'dan[19 chars]ara_ate_it': 13, 'miscount': 12} != {'dan[19 chars]ara_ate_it': 13, 'miscount': 12, 'daniel_ate_it_leo_heard': 14}
Ran 8 tests in 0.035s
FAILED (failures=1, errors=7)
exit=1
```
There are 7 ERROR (KeyError on the missing scenario) and 1 FAIL. The FAIL is T7: the backstory
lengths have no entry for the new scenario.

## Test output after the change

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.WitnessScenarioTest
test_at_minute_00_only_leos_prompt_differs_by_the_one_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_the_one_line) ... ok
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... ok
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... ok
test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning) ... ok
test_only_leos_backstory_differs (test_morning.WitnessScenarioTest.test_only_leos_backstory_differs) ... ok
test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence) ... ok
test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard) ... ok
test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard) ... ok

----------------------------------------------------------------------
Ran 8 tests in 3.064s

OK
exit=0
```

## Full suite after the change

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning
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
test_at_minute_00_only_leos_prompt_differs_by_the_one_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_the_one_line) ... ok
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... ok
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... ok
test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning) ... ok
test_only_leos_backstory_differs (test_morning.WitnessScenarioTest.test_only_leos_backstory_differs) ... ok
test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence) ... ok
test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard) ... ok
test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard) ... ok

----------------------------------------------------------------------
Ran 62 tests in 16.013s

OK
exit=0
```

62 tests, OK. That is 54 existing tests and 8 new ones. No test was skipped.

## The diff (commit 0d42eed)

```diff
diff --git a/Prototypes/llm-morning/data.py b/Prototypes/llm-morning/data.py
index 08dffd0..0064975 100644
--- a/Prototypes/llm-morning/data.py
+++ b/Prototypes/llm-morning/data.py
@@ -115,6 +115,14 @@ SCENARIOS = {
         "night": None,
     },
 }
+# Not in the shipped data: daniel_ate_it, and Leo heard the night from his bed but did not see
+# who (reports/witness_design.md). The event is Leo's alone, so its sentence names nobody he
+# did not see; it goes in right after the night.
+SCENARIOS["daniel_ate_it_leo_heard"] = {
+    **SCENARIOS["daniel_ate_it"],
+    "after_night": [(3, "In the night Leo wakes and hears someone in the kitchen open a can. "
+                        "He does not get up and does not see who.", {"leo": "heard"})],
+}
 DEFAULT_SCENARIO = "daniel_ate_it"
 
 # How the story speaks of each of them (as the shipped data's notes do).
@@ -155,9 +163,11 @@ _BACKSTORY = [
 
 
 def backstory(scenario):
-    """The days before, with this scenario's night in its place (or no night at all)."""
-    night = SCENARIOS[scenario]["night"]
-    return [night if e is NIGHT else e for e in _BACKSTORY if e is not NIGHT or night]
+    """The days before, with this scenario's night in its place (or no night at all), followed
+    by the scenario's own events of that night, if it has any."""
+    s = SCENARIOS[scenario]
+    night = ([s["night"]] if s["night"] else []) + s.get("after_night", [])
+    return [x for e in _BACKSTORY for x in (night if e is NIGHT else [e])]
 
 
 def culprit(scenario):
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index 0d32b03..bc6a10e 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -3,6 +3,7 @@
     python -m unittest -v test_morning
 """
 import contextlib
+import difflib
 import io
 import json
 import os
@@ -16,7 +17,7 @@ import metrics
 import gemini
 from gemini import Cache, FakeClient, GeminiClient, Oracle
 from morning import run
-from world import QUIET_TURNS, SYSTEM, Grudge, Morning, Track, estimate_tokens
+from world import QUIET_TURNS, SYSTEM, Grudge, Morning, Person, Track, estimate_tokens
 
 # What the third version's prompts said about guilt, suspicion and grudges: verdicts, which
 # the prompts must no longer contain.
@@ -86,6 +87,31 @@ def cached_prompts(dirs):
     return prompts
 
 
+def assert_no_target_text(test, prompts):
+    """No sentence of target-morning.md (nor its merged copy) is in any of the prompts."""
+    target = target_text()
+    if target is None:
+        test.skipTest("neither target-morning.md nor its copy in understanding-all.md was found")
+    pieces = []
+    for line in target.splitlines():
+        line = re.sub(r"^[#\-\d. ]+", "", line).strip()
+        for piece in re.split(r"(?<=[.:;!?])\s+|\(|\)", line):
+            piece = piece.strip(" .,:;\"'*")
+            if len(piece.split()) >= 5:
+                pieces.append(piece)
+    pieces += ["nobody eats alone", "don't look at me", "look innocent", "turning point",
+               "weighed down", "believable", "Possible", "Never"]
+    # The four Never lines of the second step's brief (the merged copy predates them).
+    pieces += ["Everyone speaks at once and nobody answers the line before theirs",
+               "A person repeats the same kind of line many turns in a row with no effect",
+               "Someone who was wronged forgives within minutes, with no lasting cost",
+               "A person mentions objects or places the house does not have"]
+    test.assertGreater(len(pieces), 40)
+    for p in prompts:
+        for piece in pieces:
+            test.assertNotIn(piece.lower(), p.lower(), f"target-morning text in a prompt: {piece!r}")
+
+
 class Exploding:
     requests = 0
 
@@ -198,28 +224,7 @@ class FakeMorningTest(unittest.TestCase):
 
     def test_nothing_from_target_morning_reaches_a_prompt(self):
         fake_morning(self.dirs)
-        prompts = [SYSTEM] + cached_prompts(self.dirs)
-        target = target_text()
-        if target is None:
-            self.skipTest("neither target-morning.md nor its copy in understanding-all.md was found")
-        pieces = []
-        for line in target.splitlines():
-            line = re.sub(r"^[#\-\d. ]+", "", line).strip()
-            for piece in re.split(r"(?<=[.:;!?])\s+|\(|\)", line):
-                piece = piece.strip(" .,:;\"'*")
-                if len(piece.split()) >= 5:
-                    pieces.append(piece)
-        pieces += ["nobody eats alone", "don't look at me", "look innocent", "turning point",
-                   "weighed down", "believable", "Possible", "Never"]
-        # The four Never lines of the second step's brief (the merged copy predates them).
-        pieces += ["Everyone speaks at once and nobody answers the line before theirs",
-                   "A person repeats the same kind of line many turns in a row with no effect",
-                   "Someone who was wronged forgives within minutes, with no lasting cost",
-                   "A person mentions objects or places the house does not have"]
-        self.assertGreater(len(pieces), 40)
-        for p in prompts:
-            for piece in pieces:
-                self.assertNotIn(piece.lower(), p.lower(), f"target-morning text in a prompt: {piece!r}")
+        assert_no_target_text(self, [SYSTEM] + cached_prompts(self.dirs))
 
     def test_only_daniel_knows_and_only_daniel_may_confess(self):
         m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "c.json")), "fake", 1, client=FakeClient()), 1)
@@ -904,6 +909,116 @@ class PromptTruthTest(unittest.TestCase):
                 self.assertNotIn("A can that should be on the shelf is not", prompt, (scenario, pid))
 
 
+WITNESS = "daniel_ate_it_leo_heard"
+HEARD = ("In the night Leo wakes and hears someone in the kitchen open a can. "
+         "He does not get up and does not see who.")
+HEARD_LINE = "Day 3: " + HEARD + " (you heard it)"
+
+
+class WitnessScenarioTest(unittest.TestCase):
+    """daniel_ate_it_leo_heard: daniel_ate_it, and Leo heard the night but did not see who
+    (reports/witness_design.md, sections 1 to 3)."""
+
+    def setUp(self):
+        self.assertIn(WITNESS, data.SCENARIOS)
+        self.dirs = Dirs()
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def morning(self, scenario, seed):
+        return Morning(Oracle(Cache(os.path.join(self.dirs.root, f"{scenario}-{seed}.json")), "fake", seed,
+                              client=FakeClient()), seed, scenario)
+
+    def fake_prompts(self):
+        for seed in (1, 2, 3):
+            (meta, code), out = fake_morning(self.dirs, seed=seed, scenario=WITNESS)
+            self.assertEqual(code, 0, out)
+        prompts = cached_prompts(self.dirs)
+        self.assertTrue(prompts)
+        return prompts
+
+    # T1
+    def test_the_sentence_names_nobody_leo_heard(self):
+        added = [e for e in data.backstory(WITNESS) if e not in data.backstory("daniel_ate_it")]
+        self.assertEqual(added, [(3, HEARD, {"leo": "heard"})])
+        text = added[0][1]
+        for name in ("Daniel", "Elena", "Mara"):
+            self.assertNotIn(name, text)
+        self.assertEqual(set(re.findall(r"\b[A-Z]\w*", text)) - {"In", "He"}, {"Leo"})
+        self.assertNotIn("eats a can", text)
+
+    # T2
+    def test_only_leos_backstory_differs(self):
+        for pid in ("daniel", "elena", "mara"):
+            self.assertEqual(Person(pid, WITNESS).backstory, Person(pid, "daniel_ate_it").backstory, pid)
+        old, new = Person("leo", "daniel_ate_it").backstory, Person("leo", WITNESS).backstory
+        at = next(i for i, x in enumerate(old) if x.startswith("Day 3: Mara freezes")) + 1
+        self.assertEqual(new, old[:at] + [HEARD_LINE] + old[at:])
+        self.assertFalse([x for x in new if "Daniel eats" in x])
+
+    # T3
+    def test_at_minute_00_only_leos_prompt_differs_by_the_one_line(self):
+        for seed in (1, 2, 3):
+            old, new = self.morning("daniel_ate_it", seed), self.morning(WITNESS, seed)
+            for pid in data.ORDER:
+                p, q = old.people[pid], new.people[pid]
+                self.assertEqual(q.sure, p.sure, (seed, pid))
+                self.assertEqual([o.id for o in new.options_for(q)], [o.id for o in old.options_for(p)], (seed, pid))
+                a = old.prompt_for(p, 0, old.options_for(p))
+                b = new.prompt_for(q, 0, new.options_for(q))
+                if pid != "leo":
+                    self.assertEqual(b, a, (seed, pid))
+                    continue
+                diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
+                self.assertEqual([d for d in diff if d.startswith("+ ")], ["+ - " + HEARD_LINE], seed)
+                self.assertEqual([d for d in diff if d.startswith("- ")], [], seed)
+
+    # T4
+    def test_daniels_prompt_never_mentions_being_heard(self):
+        daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
+        self.assertTrue(daniel)
+        for p in daniel:
+            for words in (HEARD, "wakes and hears", "open a can", "does not see who", "heard someone"):
+                self.assertNotIn(words, p)
+            if "On your conscience" in p:
+                self.assertIn("and nobody saw", p)
+        self.assertTrue([p for p in daniel if "On your conscience" in p])
+
+    # T5
+    def test_no_prompt_says_who_leo_heard(self):
+        prompts = self.fake_prompts()
+        leo = [p for p in prompts if p.startswith("You are Leo,")]
+        self.assertTrue(leo)
+        for p in prompts:
+            if p.startswith("You are Leo,"):
+                self.assertEqual([x for x in p.splitlines() if HEARD in x], ["- " + HEARD_LINE])
+                for words in ("Daniel eats a can", "you ate it yourself", "On your conscience"):
+                    self.assertNotIn(words, p)
+            else:
+                self.assertNotIn(HEARD, p)
+            self.assertFalse([x for x in p.splitlines() if "Daniel" in x and "open a can" in x])
+
+    # T6
+    def test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning(self):
+        assert_no_target_text(self, [SYSTEM] + self.fake_prompts())
+
+    # T7
+    def test_the_other_scenarios_do_not_have_the_sentence(self):
+        lengths = {"daniel_ate_it": 13, "mara_ate_it": 13, "miscount": 12, WITNESS: 14}
+        self.assertEqual({s: len(data.backstory(s)) for s in data.SCENARIOS}, lengths)
+        for scenario in data.SCENARIOS:
+            has = [e for e in data.backstory(scenario) if HEARD in e[1]]
+            self.assertEqual(len(has), scenario == WITNESS, scenario)
+
+    # T8
+    def test_the_witness_morning_runs_and_its_story_shows_who_heard(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1, scenario=WITNESS)
+        self.assertEqual(code, 0, out)
+        story = read(os.path.join(self.dirs.runs, f"{WITNESS}-seed1.md"))
+        self.assertIn(f"| 3 | {HEARD} | not there | not there | heard it | not there |", story)
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
```

## git status

```
(empty: nothing modified or untracked after commit 0d42eed)
```
