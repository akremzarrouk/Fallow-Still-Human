# Two fixes from the after-the-door probe: the door give in S8, and the evening's 8 on a day with no trip talk

From `reports/probe_after.md` §3, findings 1 and 5. No live call was made; every test ran with `GEMINI_API_KEY` unset.

## Summary

1. **S8 matches a give at the front door.** The claim check's "give" family now matches events of kind `give` and
   `door_give` (`mind.py:219`). Elena's scene 1 memory of Mara's give (`[D3-030, D3-033]`) is kept with no warning; it
   had `S8 mara give: no such event`.
2. **The evening's 8 are owed only while Q5 could still fire.** The new `Quiet.evening_owed()` (`quiet.py:1171-1175`)
   returns 8 only if Q5 has not been checked and someone holds a trip position today, else 0. Q5's own list of trip
   positions is now the method `Quiet.trip_positions()` (`quiet.py:1162-1169`), so the owed rule and Q5 read the same
   thing. The positions are read from the day's transcript at each check, so a position taken later in the day makes
   the 8 owed again from that minute.
3. **Tests.** `TwoFixesTest` (`test_morning.py:8118-8179`): (a) and (b), each failing before the change and passing
   after. Three older tests assumed the 8 were always owed before 19:00. Each now gives its day a trip position first
   (§2.3).
4. **Full suite, run alone:** 319 tests OK (317 + 2), exit 0.

**Read this before accepting (decide):** the knock check (`knock_short`, `quiet.py:577`) uses the same owed amount
as the Q1/Q2 budget, so it changes too. On a day with no trip position, a knock is no longer deferred to keep 8 asks
for Q5. I counted this as part of item 2 ("the evening's 8 count as owed only while Q5 could still fire"), not as a
separate check. If you meant only Q1 and Q2, change line 577 back to `0 if self.evening_done else EVENING_ASKS`;
`DoorAfterTest` (b) and `KnockTest` t6 would then pass without the trip position this change gave them.

**Not changed (outside the brief):** Q5 can also be refused because nobody who holds a position is awake with
someone (`quiet.py:1196-1198`). On such a day the 8 are still owed, because the brief named only the trip position.

## 1. The changes

### 1.1 S8, the "give" family (`mind.py:218-220`)

```diff
-             "come back": ("return",), "give": ("give",), "share": ("share",), "search": ("search", "search_done"),
-             "stop": ("stop",), "offer": ("volunteer",), "hide": ()}[family]
+             "come back": ("return",), "give": ("give", "door_give"), "share": ("share",),
+             "search": ("search", "search_done"), "stop": ("stop",), "offer": ("volunteer",), "hide": ()}[family]
```

The only change in meaning is `door_give`. The rest of the line was rewrapped to stay within the file's 120
columns. A give still has to be by the named subject and perceived by the person (`matching`, `mind.py:199-221`,
unchanged). "Leo gave the stranger some water" still warns (test (a), second part).

### 1.2 The evening's owed asks (`quiet.py`)

| Where | What |
|---|---|
| `quiet.py:1162-1169` | New `trip_positions()`: person → (minute, seq) of their latest trip act today, taken unchanged from `evening()`. |
| `quiet.py:1171-1175` | New `evening_owed()`: `EVENING_ASKS if not self.evening_done and self.trip_positions() else 0`. |
| `quiet.py:1184` | `evening()` (Q5) calls `trip_positions()` instead of its own loop. It behaves exactly as before. |
| `quiet.py:468` | `budget()` (Q1, Q2): `owed = self.evening_owed()` (was `0 if self.evening_done else EVENING_ASKS`). |
| `quiet.py:577` | `knock_short()`: the same (see the decision above). |
| `quiet.py:95-96`, `464-465` | The comment and docstring now state the new rule. |

No number changed: `EVENING_ASKS` 8, `DAY_MAX` 56, `DAY_ASKS` 40 and `KNOCK_NEEDS` 6 are as they were, and so is
the refusal text.

## 2. Tests

### 2.1 Failing first (`runs/two_fixes/red.stdout.txt`)

These are the final tests, run with `mind.py` and `quiet.py` stashed back to HEAD (`git stash push -- mind.py
quiet.py`, run, `git stash pop`):

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning.TwoFixesTest -v      exit 1
test_a_probe_after_scene1_elenas_memory_of_maras_door_give_gets_no_s8_warning ... FAIL
test_b_a_q1_at_17_39_with_50_spent_fires_with_no_trip_position_and_is_refused_with_one ... FAIL

FAIL: test_a_probe_after_scene1_elenas_memory_of_maras_door_give_gets_no_s8_warning
  File "...test_morning.py", line 8141, in test_a_probe_after_scene1_elenas_memory_of_maras_door_give_gets_no_s8_warning
    self.assertEqual((verdict, warnings), ("kept", []))
AssertionError: Tuples differ: ('kept', [{'of': 'memory', 'text': 'Mara gave some [156 chars]t'}]) != ('kept', [])
-  [{'of': 'memory',
-    'reason': 'S8 mara give: no such event',
-    'text': 'Mara gave some of our stored water to a stranger at the door '
-            'because she has a good heart, even though we have none left '
-            'ourselves.'}])

FAIL: test_b_a_q1_at_17_39_with_50_spent_fires_with_no_trip_position_and_is_refused_with_one
  File "...test_morning.py", line 8165, in test_b_a_q1_at_17_39_with_50_spent_fires_with_no_trip_position_and_is_refused_with_one
    self.assertEqual([(f["kind"], f["asked"]) for f in fired], [("Q1", "daniel")], q.log[-1])
AssertionError: Lists differ: [] != [('Q1', 'daniel')]
+ [('Q1', 'daniel')] : {'kind': 'Q1', 'minute': 639, 'room': 'kitchen', 'who': 'daniel', 'need': 'fast', 'stage': 2,
  'fired': False, 'asked': None, 'why': "50 asks spent and the evening's 8 still owed reach the day's 56",
  'budget': "50 asks spent and the evening's 8 still owed reach the day's 56"}

Ran 2 tests in 0.339s
FAILED (failures=2)
```

Each fails on the finding it is about: (a) on the probe's S8 warning, and (b) on the probe's refusal text at 17:39.
My first draft of (b) failed for another reason: 50 asks with none reserved hit the ordinary 40 first. I set 11 of
the 50 as reserved, as in scene 1's day 3 (`day 3 asks {'all': 51, 'reserved': 11}`), and re-ran it red as shown
above.

**What the tests check.**
- (a) `test_morning.py:8127-8146`: it loads `runs/probe_after/scene1.json`, builds a chronicle from its day-3 door
  events, and takes Elena's shown records from her night-mind input. It checks the memory as the night mind wrote it
  (`[D3-030, D3-033]`) with `mind.check_memory` and asserts `("kept", [])`. The premise is asserted too: D3-030 is
  Mara's `door_give`, and the run logged `S8 mara give: no such event`. Then it checks that a false give is still
  caught: "Leo gave the stranger some water." citing D3-030 and D3-031 gives `["S8 leo give: no such event"]`.
- (b) `test_morning.py:8149-8179`: v16 seed 2's day 3, everyone awake in the kitchen at 17:39 (minute 639), 50 asks
  spent (11 of them reserved), Q5 not yet checked. The premise is asserted first: nobody holds a trip position in the
  transcript. Then three checks:
  1. With no position, Q1 for Daniel fires.
  2. With Leo holding a position (`propose_trip` at 17:00), it is refused with "50 asks spent and the evening's 8
     still owed reach the day's 56".
  3. On a day where Q1 fires first and Leo takes a position at 17:42, a later Q1 for Leo at 17:45 (asks set back to
     50) is refused, naming the evening's 8.

  A position is recorded by `hold_trip_position(m, pid, minute)` (`test_morning.py:66-71`), which adds one turn to
  the day's transcript with one act shaped like `world.py:1380-1387`.

### 2.2 Passing (`runs/two_fixes/green.stdout.txt`)

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning.TwoFixesTest -v
test_a_probe_after_scene1_elenas_memory_of_maras_door_give_gets_no_s8_warning ... ok
test_b_a_q1_at_17_39_with_50_spent_fires_with_no_trip_position_and_is_refused_with_one ... ok

Ran 2 tests in 0.959s

OK
exit 0
```

### 2.3 Older tests that assumed the 8 were always owed (`runs/two_fixes/old_tests_with_fix.stdout.txt`)

With the fix and the test file as it was at HEAD (`git stash push -- test_morning.py`, run, `git stash pop`):

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning.BudgetFixTest test_morning.DoorAfterTest test_morning.KnockTest
FAIL: test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8 (BudgetFixTest)
  line 8057: AssertionError: Lists differ: [{'kind': 'Q2', 'minute': 260, 'room': 'ki[185 chars]one}] != []
FAIL: test_b_a_knock_is_deferred_unless_the_day_can_give_it_6_asks_beyond_the_evenings_owed_asks (DoorAfterTest)
  line 8009: AssertionError: [{'kind': 'Q7', 'minute': 120, ... 'fired': True, ...}] is not false : with 43 spent, the knock would take from the evening's 8
FAIL: test_t6_a_knock_comes_by_day_once_a_day_never_into_the_bathroom_and_wakes_by_the_draw (KnockTest)
  line 7256: AssertionError: 'the day cannot give a knock 6 asks' != "the day cannot give a knock 6 asks beyond the evening's 8"
Ran 13 tests in 12.980s
FAILED (failures=3)
exit 1
```

Each of these tests is about the 8 when they are owed, on a v16 seed 2 day-3 morning where nobody had taken a trip
position. So nothing was owed, and the Q2 or knock it expected to be held back went ahead. Each test now calls
`hold_trip_position` once before its checks, and its assertions are unchanged:

| Test | Line | Added |
|---|---|---|
| `KnockTest.test_t6_…` | `test_morning.py:7262` | `hold_trip_position(d.day3, "leo", 117)` |
| `DoorAfterTest.test_b_…` (`knock_with`) | `test_morning.py:8011` | `hold_trip_position(m, "leo", 117)` |
| `BudgetFixTest.test_a_…` (`q2_with`) | `test_morning.py:8060` | `hold_trip_position(m, "elena", 250)` |

With these, all 13 tests in the three classes pass (part of the full run below).

### 2.4 The full suite, run alone (`runs/two_fixes/suite.stdout.txt`)

This ran on the final code, after the last edit (the `mind.py` rewrap), from 08:28:23Z to 08:34:33Z
(`runs/two_fixes/suite.times.txt`), with nothing else running.

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning > runs/two_fixes/suite.stdout.txt 2>&1; echo "exit $?" >> runs/two_fixes/suite.stdout.txt
$ tail -5 runs/two_fixes/suite.stdout.txt
----------------------------------------------------------------------
Ran 319 tests in 368.042s

OK
exit 0
```

319 is the 317 of `budget_fix_impl.md` §4.1 plus the 2 of `TwoFixesTest`. The output has 4 `[429
RESOURCE_EXHAUSTED]` lines (`grep -c` gives 4). They come from the fake client in the retry tests, as in
`runs/budget_fix/suite.stdout.txt`. No API key was set.

## 3. Commands

All from `Prototypes/llm-morning/`.

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning.TwoFixesTest -v        # red, with mind.py and quiet.py stashed: exit 1 (§2.1)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning.TwoFixesTest -v        # green: exit 0 (§2.2)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning.BudgetFixTest test_morning.DoorAfterTest test_morning.KnockTest
                                                                                                 # old test file, with the fix: exit 1, 3 failures (§2.3)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning                       # full suite: 319 OK, exit 0 (§2.4)
$ git diff --stat
 Prototypes/llm-morning/mind.py         |  4 +-
 Prototypes/llm-morning/quiet.py        | 30 +++++++++----
 Prototypes/llm-morning/test_morning.py | 79 +++++++++++++++++++++++++++++++++-
 3 files changed, 101 insertions(+), 12 deletions(-)
```

Raw outputs in `runs/two_fixes/`: `red.stdout.txt`, `red.exit.txt`, `green.stdout.txt`,
`old_tests_with_fix.stdout.txt`, `suite.stdout.txt`, `suite.times.txt`, `report.md` (a copy of this report), and
`two_fixes-all.md` (merged).
