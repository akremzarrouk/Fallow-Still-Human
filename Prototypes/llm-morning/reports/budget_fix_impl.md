# The budget: a reserved stretch no longer spends the ordinary day

Mode: implement. From `reports/door_memory_impl.md` §5.2's finding: after the door's 9 reserved asks, the day's 40
were spent by 10:33 and the afternoon went silent. Branch `quiet-day-stage-a`, on HEAD `63bb8fe`. Paths are relative to
`Prototypes/llm-morning/`. No API call was made: every command ran with `GEMINI_API_KEY` removed from the environment.
Evidence is in `runs/budget_fix/`.

## Summary

| # | Asked | Done |
|---|---|---|
| 1 | Asks in a reserved stretch (Q5, Q6, Q7) count toward DAY_MAX (56) only, not the ordinary 40 | `quiet.py:236` (`reserved_asks`), `:415-424` (`ordinary`, `counted`), `:431`, `:438`, `:466`; `world.py:1488` |
| 2 | An ordinary trigger is also refused if the day's asks plus the evening's still-owed asks would reach 56, saying which limit | `quiet.py:462-472` (`budget`) |
| 3 | A knock inside a running stretch: +18 as now; 2 turns after the visit, the cap goes back to its own (or to the asks made, if more) | `quiet.py:263`, `:459`, `:558`, `:951-964` (`knock_back`), `:1555-1558` (in `play`) |
| – | Tests | `BudgetFixTest`, 2 tests (`test_morning.py:8032-8102`), each seen failing first (§2) |
| – | Trace (c) | Q1 and Q2 fired from 10:00 to 19:00: **0 before, 3 after**. Day 3's asks: **56** (§3) |
| – | Full suite, run alone | 317 tests OK (§4) |

Not changed: `DAY_MAX` (56), `QUIET_ASKS` (12), the 40 (`DAY_ASKS`), Q5's 8, the door's 18, the knock rule
(`knock_short`), and how a visit ends.

**A finding, not changed (outside the brief): the evening got 7 of its 8 in the trace.** Item 2 checks the trigger
only, not the stretch it starts. At 17:39 a Q1 fired with 41 asks spent (41 + 8 = 49, under 56); its stretch then made
8 asks, to 49. At 19:00 Q5's stretch reached the day's 56 after 7 asks: Leo was not asked at 19:03
(`runs/budget_fix/full_scene1.stdout.txt:286-290`; 24 morning + 9 Q7 + 8 Q2 + 8 Q1 + 7 Q5 = 56). An ordinary
stretch's asks can still take from what the evening is owed. Whether the cap of an ordinary stretch should also stop at
56 minus the evening's owed asks is for the user to decide.

## 1. The changes

### 1.1 Reserved asks count toward the 56 only (item 1)

- `quiet.py:236`: `Quiet.reserved_asks`, the asks made while a reserved stretch is under way. `Quiet.asks` is still
  the day's total.
- `quiet.py:415-417`: `ordinary()` = `asks − reserved_asks`, which is what the 40 hold.
- `quiet.py:419-424`: `counted()`, one ask made: `asks += 1`, and `reserved_asks += 1` if `self.reserved`.
  `world.py:1488` calls it in place of `self.quiet.asks += 1`. This is the only place an ask is counted.
- `quiet.py:431` (`spent`), `:438` (`spent_why`), `:466` (`budget`): the 40 are checked against `ordinary()`, not
  `asks`. `DAY_MAX` is still checked against `asks`, the total.
- "Reserved" is `self.reserved`, as before: true in a Q5, Q6 or Q7 stretch (`begin(..., reserved=True)`,
  `quiet.py:1572-1576`), and while the door's 18 are on in a stretch a knock came into (`quiet.py:561`, and §1.3).
- `quiet.py:238`: the comment on `reserved` said "Q5's"; it now says Q5, Q6, Q7.
- `quiet.py:1522`: the transcript's `asks` also gives `"reserved"`.

### 1.2 An ordinary trigger leaves the evening its 8 (item 2)

`quiet.py:462-472`, `budget(pid)`, used by Q1 (`ask_q1`) and Q2 (`meet`), in this order:
1. `ordinary() >= 40`: "the day's 40 asks are spent" (unchanged text).
2. New: `asks + owed >= 56`, where `owed` is `EVENING_ASKS` (8) until Q5 has been checked (`evening_done`), else 0.
   The refusal: "`<asks>` asks spent and the evening's 8 still owed reach the day's 56". After Q5 has been checked:
   "the day's 56 asks are spent".
3. `spent()`: now returns `spent_why()` (was `cap_why`). Without this, a day at 56 asks with fewer than 40 ordinary
   ones would return `cap_why`, which is `None` between stretches, and the trigger would not be refused. After step 2,
   this line can only be reached for a stretch's own cap.

The 12 quiet asks and the 4 asks of one person are unchanged.

### 1.3 A knock inside a running stretch (item 3)

- `quiet.py:558`, `hear_knock` (played): before the cap grows by 18 (unchanged, `:559-561`), `knock_in` records the
  visit, the cap and `reserved` as they were.
- `quiet.py:1555-1558`, `play`: after each played turn, if `knock_in`'s visit has ended (`sc["end"]`) and
  `t × 3 ≥ end + AFTER_VISIT × 3`, `knock_back` runs. This is the same test as the Q7 stretch's
  (`quiet.py:1552-1554`): a visit ends at the first turn after its last, so this is the end of the 2nd turn after the
  visit's last turn.
- `quiet.py:951-964`, `knock_back`: `cap = max(cap before the knock, asks)`, `reserved` = what it was before. If the
  stretch is then spent, its talk ends as in `after_turn` (`convos.log`: `ended`, `spent_why()`), and the stretch
  closes on the existing test.
- `quiet.py:459`, `close`: `knock_in` is cleared with the stretch.
- `quiet.py:99-100`: the comment on the constants states the rule.

Asks made while the door's 18 are on count as reserved (§1.1). This includes ordinary talk in that stretch during the
visit and its 2 turns after: the same window a Q7 stretch has.

## 2. Tests (`test_morning.py:8021-8102`)

| Test | Line | What it does |
|---|---|---|
| `RefuseTalkFake` | 8021 | `TalkFake` that picks `door_refuse` whenever it is offered, so a visit ends in its first turn |
| `test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8` | 8044 | `QuietDayTest.meeting` (v16 seed 2, day 3), Daniel comes into the kitchen at 11:20. 35 ordinary + 9 reserved: Q2 fires (Leo). 35 + 14: refused, the reason names "the evening's 8" and 56. 40 + 0: refused, "the day's 40 asks are spent" |
| `test_b_a_knock_inside_a_running_stretch_gives_it_18_until_2_turns_after_the_visit` | 8068 | v16 seed 2, day 3, with `RefuseTalkFake`. The Q2 stretch from 10:27 (own cap 24 + 8 = 32); a knock at 10:30; refused, so the visit is 10:30 to 10:33. Real constants: cap 50 to the end of 10:36; the asks made then are reserved; the asks made by 10:36 (40) exceed 32, so the cap goes back to 40 and the stretch ends at 10:39 on 16 asks. `STRETCH_ASKS` patched to 20 (own cap 44): the cap is 62 to 10:36, then exactly 44 and not reserved at 10:39, and the stretch goes on, on at most 20 asks |

### 2.1 Failing first

**Both, before any production change** (`runs/budget_fix/red.stdout.txt`):
```
FAIL: test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8
    self.assertEqual([(f["kind"], f["asked"]) for f in fired], [("Q2", "leo")], q.log[-1])
AssertionError: Lists differ: [] != [('Q2', 'leo')]
... 'fired': False, 'asked': None, 'why': "the day's 40 asks are spent", 'budget': "the day's 40 asks are spent"}
FAIL: test_b_a_knock_inside_a_running_stretch_gives_it_18_until_2_turns_after_the_visit
    self.assertEqual(seen[216][3], seen[216][0] - seen[207][0], seen)
AssertionError: None != 12 : {0: (4, 24, False, None), ... 207: (28, 32, False, None), 210: (32, 50, True, None),
213: (36, 50, True, None), 216: (40, 50, True, None), 219: (44, 50, True, None), 222: (48, 50, True, None),
225: (50, 50, True, None), 720: (54, 58, True, None), 723: (56, 58, True, None)}
Ran 2 tests in 1.932s
FAILED (failures=2)
exit 1
```

**(b) after items 1 and 2, before item 3** (`runs/budget_fix/red2.stdout.txt`): (a) passes; (b) fails on the cap:
```
test_a_a_q2_before_the_evening_... ... ok
test_b_a_knock_inside_a_running_stretch_... ... FAIL
    self.assertEqual((s["end"], s["asks"]), (219, seen[216][0] - 24), s)
AssertionError: Tuples differ: (228, 26) != (219, 16)
- (228, 26)
+ (219, 16) : {'start': 207, 'end': 228, 'room': 'kitchen', 'trigger': 'Q2', 'asks': 26}
Ran 2 tests in 2.545s
FAILED (failures=1)
exit 1
```

**(a) with item 2 alone taken out** (`runs/budget_fix/red_a_item2.stdout.txt`). In the first run, (a) failed before it
reached item 2's assertion. To show that assertion failing, `quiet.py` was copied aside, item 2's four lines in
`budget` were removed, and (a) was run. The copy was then put back; `sha256sum -c` reported `quiet.py: OK`.
```
FAIL: test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8
    self.assertEqual(fired, [])
AssertionError: Lists differ: [{'kind': 'Q2', 'minute': 260, ... 'fired': True, 'asked': 'leo', 'why': None}] != []
Ran 1 test in 0.656s
FAILED (failures=1)
exit 1
```

### 2.2 Passing (`runs/budget_fix/green.stdout.txt`)

`BudgetFixTest`, `DoorAfterTest`, `KnockTest`, `KnockFixTest`, `DoorHeardTest`, `DoorMemoryTest`:
```
test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8 ... ok
test_b_a_knock_inside_a_running_stretch_gives_it_18_until_2_turns_after_the_visit ... ok
...
Ran 29 tests in 23.427s
OK
exit 0
```
No existing test was changed.

## 3. The trace (c): `runs/door_after/trace.py full 1`, to `runs/budget_fix/`

The script was run unchanged. It writes `runs/door_after/full_scene1.json`, so that file was copied aside first. The
new one was moved to `runs/budget_fix/full_scene1.json` and the old one put back (`cmp`: identical; `git status`
shows nothing changed in `runs/door_after/`). Stdout is in `runs/budget_fix/full_scene1.stdout.txt`; stderr is empty.
The 09:42 answers are the live ones from `cache/probe_door2/scene1.json`, and every answer after them is the fake
model's.

**Q1 and Q2 fired from 10:00 to 19:00** (the trace's quiet log, `--- quiet log from the knock`; counted by
`runs/budget_fix/count_q1_q2.py`, output in `runs/budget_fix/count_q1_q2.stdout.txt`):

| | Checked | Fired | Day 3's asks |
|---|---|---|---|
| Before: `runs/door_memory/full_scene1.stdout.txt:250-266` | 11 | **0** | 50 |
| After: `runs/budget_fix/full_scene1.stdout.txt:272-285` | 7 | **3** (Q2 10:27 Leo, Q2 10:27 Mara, Q1 17:39 Daniel) | **56** |

Before: 9 of the 11 were refused for the 40, and 2 for "a line between them" 12 and 3 minutes before. After, the 4 not
fired: 3 "they met this way at 10:27 already today", 1 "a line between them 9 minutes before". None was refused for
the budget.

**Stretches.** Before (`runs/door_memory/full_scene1.stdout.txt:268-270`; this run predates
`door_memory_impl.md` §5): `09:42 to 10:03 Q7 asks 18`, `19:00 to 19:06 Q5 asks 8`. After
(`runs/budget_fix/full_scene1.stdout.txt:286-290`):
```
  09:42 to 09:51 room kitchen trigger Q7 asks 9
  10:27 to 10:33 room kitchen trigger Q2 asks 8
  17:39 to 17:48 room kitchen trigger Q1 asks 8
  19:00 to 19:06 room kitchen trigger Q5 asks 7
```
24 (morning) + 9 + 8 + 8 + 7 = 56: 40 ordinary and 16 reserved. The day's total is 56, which is at most 56. Q5
having 7, not 8, is the finding in the Summary.

## 4. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` removed.

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.BudgetFixTest      # no production change
FAILED (failures=2) exit 1                                                  # runs/budget_fix/red.stdout.txt
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.BudgetFixTest      # items 1 and 2
FAILED (failures=1) exit 1                                                  # runs/budget_fix/red2.stdout.txt
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.BudgetFixTest      # item 3
Ran 2 tests in 4.150s
OK
$ sha256sum quiet.py > $TMP/bf/sha_before; cp quiet.py $TMP/bf/quiet.py.keep    # then item 2's lines removed
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.BudgetFixTest.test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8
FAILED (failures=1) exit 1                                                  # runs/budget_fix/red_a_item2.stdout.txt
$ cp $TMP/bf/quiet.py.keep quiet.py && sha256sum -c $TMP/bf/sha_before
quiet.py: OK
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.BudgetFixTest test_morning.DoorAfterTest test_morning.KnockTest test_morning.KnockFixTest test_morning.DoorHeardTest test_morning.DoorMemoryTest
Ran 29 tests in 23.427s
OK exit 0                                                                   # runs/budget_fix/green.stdout.txt
$ cp runs/door_after/full_scene1.json $TMP/bf/full_scene1.facts.json
$ env -u GEMINI_API_KEY python runs/door_after/trace.py full 1 > runs/budget_fix/full_scene1.stdout.txt 2> runs/budget_fix/full_scene1.stderr.txt
exit 0                                                                      # stderr: 0 bytes
$ mv runs/door_after/full_scene1.json runs/budget_fix/full_scene1.json
$ cp $TMP/bf/full_scene1.facts.json runs/door_after/full_scene1.json
$ cmp runs/door_after/full_scene1.json $TMP/bf/full_scene1.facts.json && echo restored-identical
restored-identical
$ python runs/budget_fix/count_q1_q2.py runs/door_memory/full_scene1.json runs/budget_fix/full_scene1.json
... fired: 0 (Q1 0, Q2 0) ... day 3's asks: 50                             # runs/budget_fix/count_q1_q2.stdout.txt
... fired: 3 (Q1 1, Q2 2) ... day 3's asks: 56
```

### 4.1 The full suite, run alone (`runs/budget_fix/suite.stdout.txt`)

Started 22:42:54Z, ended 22:48:46Z (`runs/budget_fix/suite.times.txt`), with nothing else running.
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning > runs/budget_fix/suite.stdout.txt 2>&1; echo "exit $?" >> runs/budget_fix/suite.stdout.txt
$ tail -5 runs/budget_fix/suite.stdout.txt
----------------------------------------------------------------------
Ran 317 tests in 349.742s

OK
exit 0
```
317 is the 315 of `door_memory_impl.md` §5.5 plus the 2 of `BudgetFixTest`. The four `[429 RESOURCE_EXHAUSTED]` lines
in the output come from the fake client in the retry tests. They are also in `runs/door_after_fix/unittest.stdout.txt`
and `runs/door_memory/suite.stdout.txt`, 4 in each. No API key was set.
