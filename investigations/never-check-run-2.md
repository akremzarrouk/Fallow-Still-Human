# Never check: run 2 (N9, frozen silence)

MODE: implement. Spec: `design/never-checker-design.md` (`6d6abc1`), N9 row. One decision fixed by the
brief: `turns[].showing` is the list of person ids for whom `world.shown(q, t)` is true at the end of the
turn, after all acts are applied. Date 2026-10-12, branch `quiet-day-stage-a`.

## Result

- **Commit before this work:** `b3f76e6edb985faee9c5110797513b3143a386e2` ("Never checker: N2, N3, N4, N6, N8,
  N11 and run 1"). It holds `never_check.py`, `test_never_check.py`, `investigations/never-check-run-1.md` and
  its 4 output files, exactly as left at the end of run 1.
- **The replay hashes match.** All three day-1 mornings replayed from the cache on the new code give, once
  `showing` is stripped, the same `day1.turns` sha256 as design §2. Every other `day1` key is also equal.
  0 live asks, 0 API requests, no cache miss.
- **Tests.** All 41 in `test_never_check.py` pass: the prior 35, plus 6 new N9 tests (5 asserting,
  1 printing).
- **`test_morning.py`: 4 of 319 now fail.** All four compare a freshly replayed transcript with an old stored
  one, and the new `showing` key is the only difference. With the world.py change stashed, the same four pass.
  Not fixed here; see §7.
- **N9 fails all three mornings, as predicted.** The stretches are the same as the hand-made sheet H
  (trip_v11.md §7):

  | Replay | Stretches |
  |---|---|
  | S1 | 45–63 (7 turns), 69–87 (7 turns) |
  | S2 | 57–72 (6 turns) |
  | S3 | 36–51 (6 turns) |

- **The design's conditional predictions for S2 and S3 held.** `showing` is empty at every turn of S2 54–72
  and of S3 33–51. Neither Mara's minute-54 feeling nor Daniel's minute-33 feeling shows. Details below.

## 1. The world.py diff (recording only)

```
$ git diff Prototypes/llm-morning/world.py
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index a499226..450002b 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -1472,6 +1472,9 @@ class Morning:
             p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
         record["portions"] = self.portions
         self.log.append(record)
+        # Whose feeling shows at the end of the turn, all acts applied (recorded only; for the N9 check,
+        # design/never-checker-design.md).
+        tturn["showing"] = [q.id for q in self.people.values() if self.shown(q, t)]
         self.transcript["turns"].append(tturn)
 
     def ask_model(self, p, t, opts, d, extra=None):
```

- **Where it runs.** The line is the last thing `Morning.turn` does before appending the turn. That is after
  every act, the moves, voices, arrivals, the conversation's end-of-turn and the hunger rise.
- **Why it cannot change anything.** `shown` (`world.py:512`) is a pure read:
  `outward(q.feeling) and q.feeling_until >= t`. Nothing reads `tturn["showing"]`.
- **Order.** `self.people` is built in `data.ORDER` (`world.py:417`), so the list is in cast order.
- **Scope.** Every day's turns get the key, not only day 1's.

## 2. Offline replay and hash comparison

**What runs.** `Prototypes/llm-morning/runs/n9_showing/replay_day1.py` (new) does this for each seed:
1. Copies the seed's cache into `cache/n9_showing/`.
2. Builds `Oracle(Cache(copy), "gemini-3.5-flash-lite", seed, client=None, replay=True)`, so there is no
   client and a miss raises `gemini.CacheMiss` and stops the script.
3. Runs `Morning(oracle, seed, "daniel_ate_it").run()`, the same object and calls as `morning.py`'s day 1.
4. Writes `runs/n9_showing/daniel_ate_it-seed<k>.transcript.json` as `{"day1": ...}`.
5. Compares hashes. The hash is design §7 command 2's:
   `sha256(json.dumps(turns, sort_keys=True))[:10]`, with `showing` removed from each turn.

**Why not `morning.py --replay`.** It writes no transcript in replay mode (`morning.py:390`, which returns
before the transcript is written). It also always plays on to day 3. Days 2–3 of these caches no longer pair
with the current code: `test_morning.py` notes "Since food_confront_impl.md every day-2 prompt offers
confront_*".

The script refuses to start if `GEMINI_API_KEY` is set, and was run with it unset:

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/n9_showing/replay_day1.py
S1 seed 1: from cache 55, live 0, API 0
  day1.turns sha256 stripped cf9f5f36c4 | runs/v18 cf9f5f36c4 | design §2 cf9f5f36c4 | MATCH
  every turn has showing: True; other day1 keys equal to runs/v18: {'seed': True, 'scenario': True, 'culprit': True, 'final_rooms': True, 'final_state': True, 'convo_log': True, 'trip': True}
S2 seed 2: from cache 53, live 0, API 0
  day1.turns sha256 stripped db5de15235 | runs/v22 db5de15235 | design §2 db5de15235 | MATCH
  every turn has showing: True; other day1 keys equal to runs/v22: {'seed': True, 'scenario': True, 'culprit': True, 'final_rooms': True, 'final_state': True, 'convo_log': True, 'trip': True}
S3 seed 3: from cache 45, live 0, API 0
  day1.turns sha256 stripped 36b4a4a0ff | runs/v20 36b4a4a0ff | design §2 36b4a4a0ff | MATCH
  every turn has showing: True; other day1 keys equal to runs/v20: {'seed': True, 'scenario': True, 'culprit': True, 'final_rooms': True, 'final_state': True, 'convo_log': True, 'trip': True}
ALL MATCH
exit=0
```

The answers taken from the cache (55, 53, 45) equal each morning's model-decided acts (design §7 command 1:
`model` 55, 53, 45).

The originals were only read:
```
$ cmp cache/<v>/gemini-3.5-flash-lite-daniel_ate_it-seed<k>.json cache/n9_showing/gemini-3.5-flash-lite-daniel_ate_it-seed<k>.json
cache copy seed 1 identical to cache/v18
cache copy seed 2 identical to cache/v22
cache copy seed 3 identical to cache/v20
$ git status --short cache runs/v18 runs/v20 runs/v22
?? cache/n9_showing/
```

## 3. Tests

Command, from `Prototypes/llm-morning/`, for both runs:

```
env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_never_check
```

**The new tests** (class `FrozenSilence` in `test_never_check.py`):

| Test | Asserts |
|---|---|
| `test_S1_N9_fails` | S1's showing replay: N9 `fail` |
| `test_S2_S3_showing_across_the_silent_stretches` | no verdict; every turn in S2 54–72 and S3 33–51 has `showing`; prints them with each act |
| `test_five_silent_turns_with_no_face_showing_fail` | synthetic: minutes 3–15 all silent, nobody showing → `("fail", [(3, 15, 5)])` |
| `test_a_face_that_shows_breaks_the_stretch` | synthetic: the same with Mara showing at 9 → `("pass", [])` |
| `test_keeping_seated_and_a_silent_lull_count_as_silence` | synthetic: Elena sits with Mara at 3, keeps seated 6–18, and a silent lull at 12 → `("fail", [(6, 18, 5)])` (sitting down at 3 is not "keeps sitting") |
| `test_a_transcript_without_showing_is_not_decided` | the old S1 transcript (no `showing`) → `("n/a", [])` |

**N9 as implemented** (`never_check.n9`, the design row's sentence):
- (a) A turn is quiet when every act, in `said_at` order, is `silent` or a `sit_<q>` equal to that person's
  previous act. A silent lull is `silent`.
- (b) The turn's `showing` is empty.
- Fail when 5 or more consecutive turns meet (a) and (b). The hits are the stretches, as
  (first minute, last minute, turns).
- A transcript with any turn lacking `showing` gets `("n/a", [])`. Without this, the 18 run-1 replay tests
  would have hit a KeyError on the old transcripts. No other check was touched.

### Before N9 existed (exit 1; full output in `investigations/never-check-run-2/1-before.txt`, 128 lines)

```
test_S1_N9_fails (test_never_check.FrozenSilence.test_S1_N9_fails) ... ERROR
test_S2_S3_showing_across_the_silent_stretches (test_never_check.FrozenSilence.test_S2_S3_showing_across_the_silent_stretches)
No verdict asserted: prints each turn of the stretch, its acts' options and whose feeling shows. ... ok
test_a_face_that_shows_breaks_the_stretch (test_never_check.FrozenSilence.test_a_face_that_shows_breaks_the_stretch) ... ERROR
test_a_transcript_without_showing_is_not_decided (test_never_check.FrozenSilence.test_a_transcript_without_showing_is_not_decided) ... ERROR
test_five_silent_turns_with_no_face_showing_fail (test_never_check.FrozenSilence.test_five_silent_turns_with_no_face_showing_fail) ... ERROR
test_keeping_seated_and_a_silent_lull_count_as_silence (test_never_check.FrozenSilence.test_keeping_seated_and_a_silent_lull_count_as_silence) ... ERROR
S1 N11: predicted pass ... ok
... (all 18 ReplayVerdicts and all 17 SyntheticTraces: ok)

======================================================================
ERROR: test_S1_N9_fails (test_never_check.FrozenSilence.test_S1_N9_fails)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "...\test_never_check.py", line 243, in test_S1_N9_fails
    verdict, hits = never_check.check(never_check.load(SHOWING_REPLAYS["S1"]))["N9"]
KeyError: 'N9'
(the other four errors: the same KeyError: 'N9')
----------------------------------------------------------------------
Ran 41 tests in 0.065s

FAILED (errors=5)
```

### After N9 (exit 0; full output in `investigations/never-check-run-2/2-after.txt`)

```
test_S1_N9_fails (test_never_check.FrozenSilence.test_S1_N9_fails) ... ok
test_S2_S3_showing_across_the_silent_stretches (test_never_check.FrozenSilence.test_S2_S3_showing_across_the_silent_stretches)
No verdict asserted: prints each turn of the stretch, its acts' options and whose feeling shows. ... ok
test_a_face_that_shows_breaks_the_stretch (test_never_check.FrozenSilence.test_a_face_that_shows_breaks_the_stretch) ... ok
test_a_transcript_without_showing_is_not_decided (test_never_check.FrozenSilence.test_a_transcript_without_showing_is_not_decided) ... ok
test_five_silent_turns_with_no_face_showing_fail (test_never_check.FrozenSilence.test_five_silent_turns_with_no_face_showing_fail) ... ok
test_keeping_seated_and_a_silent_lull_count_as_silence (test_never_check.FrozenSilence.test_keeping_seated_and_a_silent_lull_count_as_silence) ... ok
S1 N11: predicted pass ... ok
S1 N2: predicted pass ... ok
S1 N3: predicted pass ... ok
S1 N4: predicted pass ... ok
S1 N6: predicted pass ... ok
S1 N8: predicted pass ... ok
S2 N11: predicted fail ... ok
S2 N2: predicted pass ... ok
S2 N3: predicted pass ... ok
S2 N4: predicted pass ... ok
S2 N6: predicted pass ... ok
S2 N8: predicted pass ... ok
S3 N11: predicted fail ... ok
S3 N2: predicted pass ... ok
S3 N3: predicted pass ... ok
S3 N4: predicted pass ... ok
S3 N6: predicted pass ... ok
S3 N8: predicted pass ... ok
(all 17 SyntheticTraces: ok)
----------------------------------------------------------------------
Ran 41 tests in 0.062s

OK

S2 minutes 54-72:
  54 showing [] | daniel silent, leo silent, mara eat (model), elena silent (model)
  57 showing [] | mara silent, daniel silent (model), elena silent, leo silent (model)
  60 showing [] | leo silent, daniel silent, elena silent, mara silent
  63 showing [] | mara silent, elena silent, leo silent (model), daniel silent
  66 showing [] | mara silent, elena silent, daniel silent (model), leo silent
  69 showing [] | elena silent, mara silent, leo silent, daniel silent
  72 showing [] | leo silent, elena silent, daniel silent, mara silent

S3 minutes 33-51:
  33 showing [] | leo silent, daniel deny (model), elena silent, mara silent
  36 showing [] | elena silent, daniel silent, mara silent, leo silent
  39 showing [] | leo silent, elena silent, mara silent, daniel silent
  42 showing [] | leo silent, elena silent, mara silent, daniel silent
  45 showing [] | leo silent, elena silent, daniel silent, mara silent
  48 showing [] | leo silent, mara silent, elena silent, daniel silent
  51 showing [] | leo silent, mara silent, daniel silent, elena silent
```

(Acts marked "(model)" were decided by the model; the rest are routine.)

## 4. Checker output on the showing replays

```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe never_check.py runs/n9_showing/daniel_ate_it-seed1.transcript.json runs/n9_showing/daniel_ate_it-seed2.transcript.json runs/n9_showing/daniel_ate_it-seed3.transcript.json
runs/n9_showing/daniel_ate_it-seed1.transcript.json
  N2   pass
  N3   pass
  N4   pass
  N6   pass
  N8   pass
  N9   fail: 45-63 (7 turns); 69-87 (7 turns)
  N11  pass
runs/n9_showing/daniel_ate_it-seed2.transcript.json
  N2   pass
  N3   pass
  N4   pass
  N6   pass
  N8   pass
  N9   fail: 57-72 (6 turns)
  N11  fail: 03 elena reassure_all; 06 elena reassure_all; 12 elena reassure_all; 30 elena reassure_all
runs/n9_showing/daniel_ate_it-seed3.transcript.json
  N2   pass
  N3   pass
  N4   pass
  N6   pass
  N8   pass
  N9   fail: 36-51 (6 turns)
  N11  fail: 00 daniel deny; 03 daniel deny; 06 daniel deny; 09 mara ask_who; 18 daniel deny; 21 mara ask_who; 21 daniel deny; 24 mara ask_who; 33 daniel deny; 54 mara ask_who
```

The six run-1 checks give the same verdicts and acts as on the original transcripts
(`investigations/never-check-run-1.md`).

**Every turn of each morning in which anyone's feeling shows:**
```
$ python -c "... print([(t['minute'], t['showing']) for t in m['turns'] if t['showing']]) ..."
S1 turns with a feeling showing: [(30, ['elena'])]
S2 turns with a feeling showing: [(48, ['mara'])]
S3 turns with a feeling showing: []
```

One face showing per morning at most. A feeling shows only until that person's next model decision with a
feeling that does not show (`world.py:1688` sets `feeling_until` to -1). Elena and Mara both decide again in
the next turn.

## 5. Did the design's conditional predictions hold?

The design (§3, N9 row) predicted **fail** for S2 and S3 on two conditions, resting on H's reading:
- S2: "if Mara's 54 feeling showed through 60, only 63–72 (4 turns) would remain, a pass";
- S3: "if Daniel's 33 feeling showed, only 42–51 (4 turns) would remain, a pass".

- **S2: held.** `showing` is `[]` at 54, 57, 60, 63, 66, 69 and 72. Mara's `eat` at 54 breaks condition (a)
  at 54 itself. From 57 to 72 every act is silent and nobody's feeling shows. That is the stretch 57–72,
  6 turns, so the verdict is **fail**, as predicted, with the stretch H named.
- **S3: held.** `showing` is `[]` at 33 and at every turn to 51. Daniel's `deny` at 33 breaks (a) at 33.
  From 36 to 51 every act is silent and no feeling shows. That is the stretch 36–51, 6 turns, so the verdict
  is **fail**, as predicted, with the stretch H named.
- **S1** (not conditional in the design): **fail**, 45–63 and 69–87, the stretches H named. The one face in
  S1 (Elena at 30) falls inside the trip argument, which is not silent anyway.

## 6. Files

| File | Status |
|---|---|
| `Prototypes/llm-morning/world.py` | modified, +3 lines (§1) |
| `Prototypes/llm-morning/never_check.py` | modified: `n9` added to `CHECKS`; `check` gives `("n/a", [])` when a check returns None; `main` prints N9 hits as stretches. N2–N11's functions are unchanged. |
| `Prototypes/llm-morning/test_never_check.py` | modified: `FrozenSilence` (6 tests) appended; nothing above it changed |
| `Prototypes/llm-morning/runs/n9_showing/` | new: `replay_day1.py`, its stdout, and the three day-1 transcripts with `showing` |
| `Prototypes/llm-morning/cache/n9_showing/` | new: byte-identical copies of the three caches |
| `investigations/never-check-run-2/` | new: `0-hashes.txt`, `1-before.txt`, `2-after.txt`, `3-checker.txt`, `4-test_morning.txt` (full suite output) |

Not touched: the design doc, the old replays and caches, the frozen `v1/`–`v14/` copies, every check other
than N9. N12 is not implemented. Nothing after `b3f76e6` is committed.

## 7. The full `test_morning.py` suite: 4 failures caused by the new key

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
FAIL: test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone (test_morning.DaysTest...)
FAIL: test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked (test_morning.DecisionFormatTest...)
FAIL: test_t1_day1_replays_from_the_v11_caches_byte_for_byte (test_morning.NightTest...)
FAIL: test_t3_the_v10_caches_pair_up_to_the_trigger (test_morning.TripTest...)
Ran 319 tests in 296.988s
FAILED (failures=4)
```

Every one fails on the same difference. The new turn has `'showing': []` and the stored one does not, for
example:
```
AssertionError: Lists differ: [{'mi[1559 chars]ody', 'angry_at': 'nobody', 'moved_to': None}], 'showing': []}] != [{'mi[1559 chars]ody', 'angry_at': 'nobody', 'moved_to': None}]}]
```

The same four tests with the world.py change stashed (restored right after; `git diff --stat` shows the
3 lines back):
```
$ git stash push -q world.py
$ env -u GEMINI_API_KEY ... -m unittest test_morning.DaysTest.test_n_t1_... test_morning.DecisionFormatTest.test_v6_... test_morning.NightTest.test_t1_... test_morning.TripTest.test_t3_...
Ran 4 tests in 0.497s
OK
$ git stash pop -q
```

So the moves and minutes are unchanged (§2 shows that by hash too). What breaks is that these tests compare
whole turns. The suite already handles keys added after a stored transcript was made: `without_lull`
(`test_morning.py:979`) drops `lull` and `trip_moment` before comparing.

**Proposed fix, not applied:** also drop `showing` from each turn, in `without_lull` and in the two
`json.loads(json.dumps(day1.transcript))` comparisons. This edits existing tests the brief did not cover,
so it is left for your decision. The 315 other tests pass. The 429 RESOURCE_EXHAUSTED lines in the run's
output come from the suite's stubbed-API retry tests; no request leaves the machine (the module docstring:
"Tests against the fake model and a stubbed API").

## 8. Fix applied

The "Proposed fix" of §7, applied to `Prototypes/llm-morning/test_morning.py` only. A new helper
`without_showing` drops the `showing` key from each turn. `without_lull` now builds on it, which fixes the two
tests that go through `without_lull`. The two whole-transcript comparisons use `without_showing` in place of
`json.loads(json.dumps(day1.transcript))`. No assertion changed other than that key strip; `world.py`,
`never_check.py` and every stored transcript are untouched.

```
$ git diff Prototypes/llm-morning/test_morning.py
@@ -976,10 +976,19 @@ def frozen(version, module):
-def without_lull(transcript):
-    """A transcript as JSON would hold it, without the `lull` key that every act has since v9
-    and the `trip_moment` key that every act has since v11."""
+def without_showing(transcript):
+    """A transcript as JSON would hold it, without the `showing` key that every turn has since the N9 check
+    (design/never-checker-design.md): recorded only, it changes no act and no minute."""
     tr = json.loads(json.dumps(transcript))
+    for turn in tr["turns"]:
+        turn.pop("showing", None)
+    return tr
+
+
+def without_lull(transcript):
+    """A transcript as JSON would hold it, without the `lull` key that every act has since v9,
+    the `trip_moment` key that every act has since v11 and the `showing` key that every turn has since N9."""
+    tr = without_showing(transcript)
     for turn in tr["turns"]:
         for a in turn["acts"]:
             a.pop("lull", None)
@@ -2413,7 +2422,7 @@ class NightTest(unittest.TestCase):
-            self.assertEqual(json.loads(json.dumps(day1.transcript)),
+            self.assertEqual(without_showing(day1.transcript),
@@ -3748,7 +3757,7 @@ class DaysTest(unittest.TestCase):
-            self.assertEqual(json.loads(json.dumps(day1.transcript)),
+            self.assertEqual(without_showing(day1.transcript),
```

Both suites, offline (`env -u GEMINI_API_KEY`):

```
$ ... -m unittest test_morning
Ran 319 tests in 295.310s
OK

$ ... -m unittest test_never_check
Ran 41 tests in 0.060s
OK
```

The commit hash is given in the reply that delivered this section.
