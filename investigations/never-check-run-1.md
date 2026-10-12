# Never check: run 1

MODE: implement. Spec: `design/never-checker-design.md`, committed alone before any code.
Date 2026-10-12, branch `quiet-day-stage-a`.

## Result

- **Design-doc commit:** `6d6abc158c8a762d263e8e79cf1589e303969bb8`
  ("Never checker: design (frozen spec and predictions before any code)"). It contains
  `design/never-checker-design.md` only (1 file, 338 insertions).
- **18 of 18 replay verdicts match the frozen predictions.** No disagreement, so `DISAGREEMENTS` in the test
  file is empty and no test is marked as an expected failure.
- **All 17 synthetic-trace tests pass:** 10 that must fail an item, 6 mirrors that must pass, and 1 loader test.
  Together with the 18 replay tests, 35 tests run, OK.
- **Three checks have no input in some replays** (see "What the passes rest on"): N4 in all three, N2 in S1
  and N3 in S3. Those passes come from absence, and only the synthetic traces exercise those checks'
  failing path.

## Files

| File | What |
|---|---|
| `Prototypes/llm-morning/never_check.py` | new. N2, N3, N4, N6, N8, N11 as specified in design §3. It reads `day1` or the top level, uses `talk.act_of` and `talk.SPEECH` for speech kinds and `data.ORDER` for cast ids, and prints each item's verdict and triggering acts (minute, who, option). |
| `Prototypes/llm-morning/test_never_check.py` | new. `ReplayVerdicts`: 18 tests, one per (replay, item), asserting design §3's frozen verdict. `SyntheticTraces`: 17 tests. |
| `investigations/never-check-run-1/*.txt` | raw outputs: `1-before-no-module.txt`, `2-before-stub.txt` (595 lines), `3-after.txt`, `4-checker.txt`. |

Nothing else was changed: not the design doc, the replays, the simulation code or any `.md` story. The checker
reads no `.md` file. N9, N12 and the judgment screens are not implemented. The new files are not committed.

**Replays** (design §2):
- **S1** = `runs/v18/daniel_ate_it-seed1.transcript.json`
- **S2** = `runs/v22/daniel_ate_it-seed2.transcript.json`
- **S3** = `runs/v20/daniel_ate_it-seed3.transcript.json`

## Order of work

1. Committed the design doc alone (`6d6abc1`).
2. Wrote `test_never_check.py`. Ran it with no `never_check` module: import error (run A below).
3. To see each test fail on its own rather than at import, added a stub `never_check.py` whose three
   functions raise `NotImplementedError`. Ran it: 35 errors (run B).
4. Replaced the stub with the implementation. Ran the tests: 35 OK (run C). Ran the checker on S1–S3.
5. Removed one unused constant (`ITEMS`) from `never_check.py`. Re-ran the tests: output identical to run C
   apart from the timing line (`diff` printed nothing).

**Spec points read as follows**, with nothing added beyond the design's sentences:
- **Act order.** Acts are ordered by `said_at` (minute, sequence).
- **N2 timing.** "Within 3 turns (9 minutes) after" means a later act at most 9 minutes after the finishing
  act.
- **N4 leaving.** "Leaving" means q's act with non-null `moved_to` in the same minute, said before the sit.
- **N11 sequence.** Only `mode` = `model` acts form the sequence. Routine acts are skipped. A model act that is
  not a speech kind (`silent`, `search`, `eat`…) breaks a run, and a speech act of another kind starts a new
  one. `fallback` acts are not model-decided, so they are skipped like routine acts. The spec names only
  routine, and none of the three replays has a fallback act.
- **N8 cast ids.** "Names a person" means the option starts with `reassure_`, `accuse_`, `sit_`, `back_`,
  `object_` or `aside_` followed by an id in `data.ORDER`. "`suspects` names someone" means a value other
  than `None` or `"nobody"`.

## Test command and output

Command, run from `Prototypes/llm-morning/`, for all three runs:

```
env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_never_check
```

### A. Before implementation: no module (full output, exit 1)

```
test_never_check (unittest.loader._FailedTest.test_never_check) ... ERROR

======================================================================
ERROR: test_never_check (unittest.loader._FailedTest.test_never_check)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_never_check
Traceback (most recent call last):
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_never_check.py", line 15, in <module>
    import never_check
ModuleNotFoundError: No module named 'never_check'


----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```

### B. Before implementation: stub raising NotImplementedError (exit 1)

The full output is 595 lines, in `investigations/never-check-run-1/2-before-stub.txt`. Below are every result
line, one of the 35 tracebacks (all have the same shape) and the summary.

```
S1 N11: predicted pass ... ERROR
S1 N2: predicted pass ... ERROR
S1 N3: predicted pass ... ERROR
S1 N4: predicted pass ... ERROR
S1 N6: predicted pass ... ERROR
S1 N8: predicted pass ... ERROR
S2 N11: predicted fail ... ERROR
S2 N2: predicted pass ... ERROR
S2 N3: predicted pass ... ERROR
S2 N4: predicted pass ... ERROR
S2 N6: predicted pass ... ERROR
S2 N8: predicted pass ... ERROR
S3 N11: predicted fail ... ERROR
S3 N2: predicted pass ... ERROR
S3 N3: predicted pass ... ERROR
S3 N4: predicted pass ... ERROR
S3 N6: predicted pass ... ERROR
S3 N8: predicted pass ... ERROR
test_load_reads_day1_or_the_top_level (...) ... ERROR
test_n11_a_new_line_or_a_model_silence_breaks_it (...) ... ERROR
test_n11_reassure_all_and_one_person_are_one_kind (...) ... ERROR
test_n11_three_same_kind_none_new_fail (...) ... ERROR
test_n2_searching_what_you_just_watched_fail (...) ... ERROR
test_n2_the_culprit_or_later_than_nine_minutes_passes (...) ... ERROR
test_n3_an_unfinished_search_may_be_started_again (...) ... ERROR
test_n3_ask_after_hearing_a_confession_fail (...) ... ERROR
test_n3_deny_after_own_confession_fail (...) ... ERROR
test_n3_own_finished_search_again_fail (...) ... ERROR
test_n4_sitting_with_someone_leaving_fail (...) ... ERROR
test_n4_sitting_with_someone_searching_fail (...) ... ERROR
test_n4_sitting_with_someone_who_finished_searching_passes (...) ... ERROR
test_n6_one_line_at_minute_0_passes (...) ... ERROR
test_n6_silence_at_the_discovery_fail (...) ... ERROR
test_n8_a_target_chosen_outside_the_model_fail (...) ... ERROR
test_n8_routine_silence_and_model_targets_pass (...) ... ERROR

======================================================================
ERROR: test_S1_N2 (test_never_check.ReplayVerdicts.test_S1_N2)
S1 N2: predicted pass
----------------------------------------------------------------------
Traceback (most recent call last):
  File "...\test_never_check.py", line 53, in test
    verdict, hits = self.result(replay)[item]
  File "...\test_never_check.py", line 47, in result
    cls._results[replay] = never_check.check(never_check.load(REPLAYS[replay]))
  File "...\never_check.py", line 9, in load
    raise NotImplementedError
NotImplementedError
...
----------------------------------------------------------------------
Ran 35 tests in 0.024s

FAILED (errors=35)
```

### C. After implementation (full output, exit 0)

```
test_S1_N11 (test_never_check.ReplayVerdicts.test_S1_N11)
S1 N11: predicted pass ... ok
test_S1_N2 (test_never_check.ReplayVerdicts.test_S1_N2)
S1 N2: predicted pass ... ok
test_S1_N3 (test_never_check.ReplayVerdicts.test_S1_N3)
S1 N3: predicted pass ... ok
test_S1_N4 (test_never_check.ReplayVerdicts.test_S1_N4)
S1 N4: predicted pass ... ok
test_S1_N6 (test_never_check.ReplayVerdicts.test_S1_N6)
S1 N6: predicted pass ... ok
test_S1_N8 (test_never_check.ReplayVerdicts.test_S1_N8)
S1 N8: predicted pass ... ok
test_S2_N11 (test_never_check.ReplayVerdicts.test_S2_N11)
S2 N11: predicted fail ... ok
test_S2_N2 (test_never_check.ReplayVerdicts.test_S2_N2)
S2 N2: predicted pass ... ok
test_S2_N3 (test_never_check.ReplayVerdicts.test_S2_N3)
S2 N3: predicted pass ... ok
test_S2_N4 (test_never_check.ReplayVerdicts.test_S2_N4)
S2 N4: predicted pass ... ok
test_S2_N6 (test_never_check.ReplayVerdicts.test_S2_N6)
S2 N6: predicted pass ... ok
test_S2_N8 (test_never_check.ReplayVerdicts.test_S2_N8)
S2 N8: predicted pass ... ok
test_S3_N11 (test_never_check.ReplayVerdicts.test_S3_N11)
S3 N11: predicted fail ... ok
test_S3_N2 (test_never_check.ReplayVerdicts.test_S3_N2)
S3 N2: predicted pass ... ok
test_S3_N3 (test_never_check.ReplayVerdicts.test_S3_N3)
S3 N3: predicted pass ... ok
test_S3_N4 (test_never_check.ReplayVerdicts.test_S3_N4)
S3 N4: predicted pass ... ok
test_S3_N6 (test_never_check.ReplayVerdicts.test_S3_N6)
S3 N6: predicted pass ... ok
test_S3_N8 (test_never_check.ReplayVerdicts.test_S3_N8)
S3 N8: predicted pass ... ok
test_load_reads_day1_or_the_top_level (test_never_check.SyntheticTraces.test_load_reads_day1_or_the_top_level) ... ok
test_n11_a_new_line_or_a_model_silence_breaks_it (test_never_check.SyntheticTraces.test_n11_a_new_line_or_a_model_silence_breaks_it) ... ok
test_n11_reassure_all_and_one_person_are_one_kind (test_never_check.SyntheticTraces.test_n11_reassure_all_and_one_person_are_one_kind) ... ok
test_n11_three_same_kind_none_new_fail (test_never_check.SyntheticTraces.test_n11_three_same_kind_none_new_fail) ... ok
test_n2_searching_what_you_just_watched_fail (test_never_check.SyntheticTraces.test_n2_searching_what_you_just_watched_fail) ... ok
test_n2_the_culprit_or_later_than_nine_minutes_passes (test_never_check.SyntheticTraces.test_n2_the_culprit_or_later_than_nine_minutes_passes) ... ok
test_n3_an_unfinished_search_may_be_started_again (test_never_check.SyntheticTraces.test_n3_an_unfinished_search_may_be_started_again) ... ok
test_n3_ask_after_hearing_a_confession_fail (test_never_check.SyntheticTraces.test_n3_ask_after_hearing_a_confession_fail) ... ok
test_n3_deny_after_own_confession_fail (test_never_check.SyntheticTraces.test_n3_deny_after_own_confession_fail) ... ok
test_n3_own_finished_search_again_fail (test_never_check.SyntheticTraces.test_n3_own_finished_search_again_fail) ... ok
test_n4_sitting_with_someone_leaving_fail (test_never_check.SyntheticTraces.test_n4_sitting_with_someone_leaving_fail) ... ok
test_n4_sitting_with_someone_searching_fail (test_never_check.SyntheticTraces.test_n4_sitting_with_someone_searching_fail) ... ok
test_n4_sitting_with_someone_who_finished_searching_passes (test_never_check.SyntheticTraces.test_n4_sitting_with_someone_who_finished_searching_passes) ... ok
test_n6_one_line_at_minute_0_passes (test_never_check.SyntheticTraces.test_n6_one_line_at_minute_0_passes) ... ok
test_n6_silence_at_the_discovery_fail (test_never_check.SyntheticTraces.test_n6_silence_at_the_discovery_fail) ... ok
test_n8_a_target_chosen_outside_the_model_fail (test_never_check.SyntheticTraces.test_n8_a_target_chosen_outside_the_model_fail) ... ok
test_n8_routine_silence_and_model_targets_pass (test_never_check.SyntheticTraces.test_n8_routine_silence_and_model_targets_pass) ... ok

----------------------------------------------------------------------
Ran 35 tests in 0.052s

OK
```

The synthetic traces that must fail, one per item (the mirrors and the loader test are in the file):

| Item | Hand-built morning | Required triggering acts |
|---|---|---|
| N2 | Mara searches the kitchen to the end at 06 (found nothing); Leo, there to see it, searches it at 09 | `(9, leo, search)` |
| N3 | three cases: Mara searches the kitchen to the end, then again at 12; Daniel confesses at 03, denies at 06; Leo hears the 03 confession, asks who at 06 | `(12, mara, search)`; `(6, daniel, deny)`; `(6, leo, ask_who)` |
| N4 | two cases: Elena sits with Mara while Mara is searching; Leo sits with Daniel in the minute Daniel leaves | `(3, elena, sit_mara)`; `(3, leo, sit_daniel)` |
| N6 | all four silent at minute 0 | the four minute-0 acts |
| N8 | a `fallback` `reassure_mara`, and a `routine` silence whose `suspects` is "Daniel" | both acts |
| N11 | Daniel denies at 03, 09, 12 (routine silence at 06 between), all not new; and Elena `reassure_all`, `reassure_mara`, `reassure_all`, all not new | the three acts of each |

## Checker output

```
$ PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe never_check.py runs/v18/daniel_ate_it-seed1.transcript.json runs/v22/daniel_ate_it-seed2.transcript.json runs/v20/daniel_ate_it-seed3.transcript.json
runs/v18/daniel_ate_it-seed1.transcript.json
  N2   pass
  N3   pass
  N4   pass
  N6   pass
  N8   pass
  N11  pass
runs/v22/daniel_ate_it-seed2.transcript.json
  N2   pass
  N3   pass
  N4   pass
  N6   pass
  N8   pass
  N11  fail: 03 elena reassure_all; 06 elena reassure_all; 12 elena reassure_all; 30 elena reassure_all
runs/v20/daniel_ate_it-seed3.transcript.json
  N2   pass
  N3   pass
  N4   pass
  N6   pass
  N8   pass
  N11  fail: 00 daniel deny; 03 daniel deny; 06 daniel deny; 09 mara ask_who; 18 daniel deny; 21 mara ask_who; 21 daniel deny; 24 mara ask_who; 33 daniel deny; 54 mara ask_who
exit=0
```

## Predicted vs actual

| Item | S1 predicted | S1 actual | S2 predicted | S2 actual | S3 predicted | S3 actual |
|---|---|---|---|---|---|---|
| N2 | pass | pass | pass | pass | pass | pass |
| N3 | pass | pass | pass | pass | pass | pass |
| N4 | pass | pass | pass | pass | pass | pass |
| N6 | pass | pass | pass | pass | pass | pass |
| N8 | pass | pass | pass | pass | pass | pass |
| N11 | pass | pass | **fail** | **fail** | **fail** | **fail** |

**Disagreements: none.** The two fails also name the same acts the design predicted in §3:
- S2: Elena `reassure` at 03, 06, 12 and 30.
- S3: Daniel `deny` at 00, 03, 06, 18, 21 and 33, and Mara `ask` at 09, 21, 24 and 54.

### What the passes rest on (inputs each check saw)

A pass with nothing to examine is weaker than a pass over candidates. This one-liner lists what each check
had to look at:

```
$ PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -c "import never_check as nc, talk; ... (per replay: searches, confessions, deny/ask_who after a confession, sit_ acts, moves, acts naming someone, same-kind model runs of 3+)"
S1
  N2/N3 inputs: searches []
  N3 inputs: confess [(3, 'daniel')] | deny/ask_who after first confess []
  N4 inputs: sit_ acts [] | moved_to 0
  N8 inputs: acts naming someone 39 | of them not model 0
  N11 inputs: same-kind runs >=3 (minute,new): [('leo', 'object', [(33, True), (36, False), (39, True)]), ('elena', 'object', [(24, True), (27, True), (30, True)]), ('mara', 'object', [(33, True), (36, True), (39, False)])]
S2
  N2/N3 inputs: searches [(9, 'mara', 'search', 'started going through th'), (9, 'leo', 'search', 'started going through th')]
  N3 inputs: confess [(33, 'daniel')] | deny/ask_who after first confess []
  N4 inputs: sit_ acts [] | moved_to 0
  N8 inputs: acts naming someone 29 | of them not model 0
  N11 inputs: same-kind runs >=3 (minute,new): [('elena', 'reassure', [(3, False), (6, False), (12, False), (30, False)])]
S3
  N2/N3 inputs: searches [(6, 'mara', 'search', ...), (15, 'leo', 'search', ...), (18, 'leo', 'keep_searching', 'went through the room an'), (72, 'mara', 'search', ...), (72, 'elena', 'search', ...), (75, 'mara', 'keep_searching', 'went through the room an'), (75, 'elena', 'keep_searching', 'went through the room an'), (75, 'daniel', 'search', ...), (78, 'daniel', 'keep_searching', 'went through the room an')]
  N3 inputs: confess [] | deny/ask_who after first confess []
  N4 inputs: sit_ acts [] | moved_to 0
  N8 inputs: acts naming someone 1 | of them not model 0
  N11 inputs: same-kind runs >=3 (minute,new): [('mara', 'ask', [(9, False), (21, False), (24, False), (54, False)]), ('daniel', 'deny', [(0, False), (3, False), (6, False), (18, False), (21, False), (33, False)])]
```

From this:
- **N4 passes by absence in all three.** No `sit_` act and no move.
- **N2.**
  - S1: passes by absence (no search).
  - S2: the two 09 searches never finish, so there is no finished check to watch.
  - S3, closest case: Daniel starts searching at 75, in the same turn Mara and Elena finished with nothing.
    The culprit is excluded by the spec ("someone other than the culprit").
  - S3, other searches: Elena's 72 search starts while Mara's is under way, not after a finish. Mara's 72
    search is 54 minutes after Leo's 18 finish.
- **N3.** It passes over real inputs in S1 and S2: a confession exists, and nobody denies or asks after it.
  In S3 there is no confession, and no own finished search is repeated.
- **N6.** Lines at minute 0 in all three (Elena asks in S1 and S2; Mara and Elena ask in S3).
- **N8.** It passes over 39, 29 and 1 acts that name someone: every one has `mode` = `model`.
- **N11.** In S1 the three runs of `object` acts each contain a `new` = true act, so none fails. That is the
  "borderline 1" of trip_v11.md §7, read by the spec's `new` rule.

## Not done (per scope)

- N9, N12 and the judgment screens (N1, N5, N7, N10, N13).
- No commit of the code, test or this report; only the design doc was committed, as step 1 asked.
- The existing `test_morning.py` suite was not run: no file it imports was changed.
