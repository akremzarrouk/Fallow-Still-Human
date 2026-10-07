# Stage B fixes: who knows next door is empty, a lighter near street, and "today" in the suspicion line

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, and `cache/v16` was read through
temp copies only. Its sha256s are unchanged (§5.2). Paths are relative to `Prototypes/llm-morning/`. `$S` is the
session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\161307dd-9080-42e6-a245-c5c49c9042bd\scratchpad`.

From `reports/stage_b.md` §1 and §4: in both fake runs, Leo went next door alone on night 3 and was lost. His own
prompt said next door was empty. On his shifted near table, the seed's draw 0.914 was `not_back`. These are the two
corrections, plus the suspicion line that §1 left out of amendment 5:
1. **Knowing next door is empty** also comes from your own neighbour's-house line, when it says a trip there came back
   with nothing. W5 follows from that.
2. **The weakness shift on the near street table** is half of what it is on the far table. Far is unchanged.
3. **The suspicion line says "today at"** from minute 90 on a quiet day, and at its night, like the grudge lines.

Not changed: the far table, the house draws, the doze, Q2.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The tests for 1 to 3 fail before and pass after | **PASS** | §3. Before: 3 failures, each on the missing behaviour. After: all pass. |
| 2 | v16 seed 2, day 3: everyone whose neighbour's-house line says Daniel came back with nothing is offered W5; Elena (there may be food there) is not | **PASS** | Leo and Mara: the street line, `propose_far` and `volunteer_far` by day, and `go_further` at bedtime. Elena: none of these (test 1, §3; replay, §5.1). |
| 3 | A no-API replay of v16 matches `runs/v16` up to the first prompt where someone knows next door is empty; v9 to v14 IDENTICAL; the full suite passes | **PASS** | The points per seed, below (§5.1). Frozen: 18 of 18 IDENTICAL (§5.3). Suite: `Ran 246 tests`, `OK` (§5.4). |

### Who knows next door is empty, in each v16 seed, and from when

| Seed | Who | From | Why: their own neighbour's-house line |
|---|---|---|---|
| 1 | Daniel | day 2 | "you went in last night and found no food there" (night 1) |
| 1 | Elena, Leo, Mara | day 2 (**new**) | "Daniel went there last night and came back with nothing" |
| 2 | Daniel | day 3 | "you went in last night and found no food there" (night 2) |
| 2 | Leo, Mara | day 3 (**new**) | "Daniel went there last night and came back with nothing" |
| 2 | (not Elena) | — | "its people left in the first days, so there may be food there" |
| 3 | Daniel | day 3 | as seed 2 |
| 3 | Leo, Mara | day 3 (**new**) | as seed 2 |
| 3 | (not Elena) | — | as seed 2 |

On day 2 of seeds 2 and 3, nobody knows: nobody went out on night 1.

### The first prompt where someone knows next door is empty (DONE 3)

| Seed | The first prompt with no cached answer | Its speaker knows | Matches `runs/v16` before it |
|---|---|---|---|
| 1 | day 2, min 00, Daniel, after 67 cached answers | yes. Everyone knows from day 2, so day 2's first prompt is the point. | day 1, night 1, mind 1 |
| 2 | day 3, min 00, Leo, after 96 cached answers | yes, **new**. Stage B's Leo here had no W5 lines. | day 1 to mind 2 |
| 3 | day 3, min 00, Daniel, after 135 cached answers | yes | day 1 to mind 2 |

These are the same prompts as stage B's points (`reports/stage_b.md`, DONE 4). In seed 2, Leo's prompt now carries
the street line, the far house line and the two day options. Before, it carried none of them.

## 1. The change

| File | Change |
|---|---|
| `night.py` | **Fix 1:** `knows_next_door_empty(history, pid, away)` (`night.py:143`). It keeps the old rule: they got inside and left nothing. Failing that, it is true when they made no visit of their own and `heard_trip` gives a trip that came back (not in `away`) having taken nothing. That is exactly when their line ends "and came back with nothing". `heard_trip` (`night.py:976`) is the hearsay half of `neighbour_line` (`night.py:945`), moved out unchanged so the line and the knowing read the same trip. The caller passes `m.away` (`night.py:1025`). **Fix 2:** `NEAR_SHIFT = 0.5` (`night.py:81`). `street_table` adds the shift at full size on the far table and at half size on the near one (`night.py:118`–`124`). |
| `world.py` | **Fix 3:** the suspicion line's own day is "today" when the prompt's `today` flag is set (`world.py:958`). That is the flag amendment 5 already gives the grudge lines: a quiet day, from minute 90 on, and at its night. The night's own answers still read "tonight". |
| `test_morning.py` | 3 new tests and 3 existing tests changed (§3). |

**Choices made, and why:**
- **Fix 1 follows the line, not the night.** The rule is whatever their own neighbour's-house line says.
  - **Own visit first.** Someone with a visit of their own has that visit as their line. So if they went and did not
    get inside, hearing that someone else came back with nothing does not make them a knower. Their line says "you
    did not get inside".
  - **"Came back with nothing" includes a trip scared off before the door** (`scare_there`, took 0). The line does
    not tell those apart, and the people who saw it do not know the difference.
  - **"Has not come back"** does not make anyone a knower.
- **Fix 2 halves the shift in `street_table`,** so a near group takes half of its half-sized weakest shift. The fix
  says the near shift is half of what it is on the far table, and the far group shift is already half the weakest.
  - Near, alone, weak: (.60, .14, .18, .08). It was (.58, .14, .18, .10).
  - Far, alone, weak: (.41, .17, .23, .19). Unchanged.
- **Stage B's Leo, on the new table.** His night-3 table, (.56, .14, .18, .12), was weak and exhausted. Halved, it is
  (.59, .14, .18, .09). **The seed's draw 0.914 is still `not_back` on it,** because .59 + .14 + .18 = .91. On the
  plain table it would be `scare_back` (cut at .94). Fix 2 alone would not have brought him back that night. Fix 1
  changes what he is offered: in seed 2 he now knows next door is empty, so he also has `go_further`, the street
  line and the far day options. Computed with:
  ```
  $ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -c "import night as n; ..."
  (1, 2) [0.59, 0.14, 0.18, 0.09] not_back
  (2, 0) [0.56, 0.14, 0.19, 0.11] not_back
  (2, 2) [0.55, 0.14, 0.19, 0.12] not_back
  plain scare_back
  old weak+exhausted not_back
  ```
  `(fast_stage, debt_stage)`, and the draw 0.9140448836121682 on each one's alone table.
- **Fix 3 has the same reach as the grudge lines.** It changes only the word for the day's own minutes. A
  suspicion from an earlier day keeps its day words.

**Not rerun:** the stage B fake runs (`runs/stage_b_fake/`). Their night 3 used the old near table, and their bedtime
offers used the old knowers.

## 2. The neighbour's-house lines, before the change (`$S/lines.py`)

These lines did not change. Only who counts as knowing did. Run on the code before the change:
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/lines.py
1 day2 daniel True | About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
1 day2 elena False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
1 day2 leo False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
1 day2 mara False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
1 day3 daniel True | About the neighbour's house: you went in the night before last and found no food there. Outside is dangerous.
1 day3 elena False | About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
1 day3 leo False | About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
1 day3 mara False | About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
2 day2 daniel False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
2 day2 elena False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
2 day2 leo False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
2 day2 mara False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
2 day3 daniel True | About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
2 day3 elena False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
2 day3 leo False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
2 day3 mara False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
3 day2 daniel False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
3 day2 elena False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
3 day2 leo False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
3 day2 mara False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
3 day3 daniel True | About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
3 day3 elena False | About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
3 day3 leo False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
3 day3 mara False | About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
```
Seed 1 reaches day 3 on HushFake answers (no API): its day 2 misses v16's cache since stage B. The script skips the
fixture's "comes from its cache" check for seed 1 only.

## 3. The tests

| Fix | Test | What it holds |
|---|---|---|
| 1 | `test_w5_is_known_from_a_neighbour_line_that_came_back_with_nothing` (`test_morning.py:5843`) | v16 seed 2, day 3: Leo's and Mara's lines end "and came back with nothing. Outside is dangerous."; Elena's says "so there may be food there". `knows_empty` is Daniel, Leo, Mara. At 10:30, Leo's and Mara's prompts carry `STREET_UNSEARCHED`, `propose_far` and `volunteer_far`; Elena's has none of them, nor "further along". At night 3, Daniel's, Leo's and Mara's bedtime options have `go_further`; Elena's does not. |
| 2 | `test_weakness_shifts_the_near_table_by_half_of_the_far` (`test_morning.py:5871`) | Near alone: weak (.60, .14, .18, .08), very weak (.56, .14, .19, .11), exhausted (.61, .14, .18, .07), very weak and exhausted (.55, .14, .19, .12). Near group at its weakest very weak: (.67, .12, .155, .055). Far, as before: weak alone (.41, .17, .23, .19), very weak and exhausted alone (.31, .17, .25, .27), the group (.49, .15, .23, .13). |
| 3 | `test_the_suspicion_line_says_today_from_minute_90` (`test_morning.py:5889`) | v16 seed 2, day 3. Mara is made to suspect Leo, with a mention at minute 60 and no known culprit. Her "About the can" line reads "this morning at minute 60" at min 87, and "today at minute 60" at min 90 and at night, with no "this morning". |

**Existing tests changed, because the fixes overturn their expectations:**
- **`test_w5_is_offered_once_someone_knows_next_door_is_empty`** (`test_morning.py:5696`): seed 2's day-3 knowers are
  Daniel, Leo and Mara, not Daniel alone. The prompt without W5, by day and at bedtime, is now Elena's, not Mara's.
- **`test_weakness_shifts_the_street_tables`** (`test_morning.py:5749`): the near numbers are the halved ones, the
  same as test 2. Its night-3 part computes Daniel's table through `street_table`, so it is unchanged. Draw 0.6 is
  still not clean on his table.
- **`test_v16_seed_1_until_w5`** (`test_morning.py:5927`): on day 2, all four know. Its first miss is still Daniel's
  day-2 min-00 prompt.
- **`WitnessScenarioTest.test_no_prompt_says_who_leo_heard`** (T5, `test_morning.py:1199`): its regex for the "About
  the can" line knew "this morning at …" as a suspicion's own day. It now also accepts "today at …" (fix 3). It
  failed on "About the can (a little): you thought Daniel took it, today at 10:54." That is fix 3's intended
  output.
- **`DaysTest.test_n_t13_counting`** (N-T13, `test_morning.py:4232`): it assumed every non-routine act on day 3 was
  one ask.
  - **Why it fails now.** Fix 1 changed seed 1's fake run: from day 2, all four know next door is empty, so their
    options differ. On day 3 of that run, the stretch cap fires and then Elena is asked aside in the same turn, at
    minute 135. `ask_model` returns without asking (`world.py:1380`), and `decide_aside` records the fallback
    `refuse_aside` (`world.py:1494`). Result: 40 asks against 41 non-routine acts.
  - **The test's change.** It now subtracts the decisions the story file shows as "could not be used (this stretch's N
    asks are spent)" or "(the day's N asks are spent)". Day 2, with no budget, keeps the exact count.
  - **How it was found.** A wrapper around `ask_model` in `$S/t13b.py`:
    `day3_asks 40 | decisions with no ask: [(6, 135, 'elena', "this stretch's 8 asks are spent")]`.

**The first full run after the change** (`$S/full.txt`) failed on these two:
```
FAIL: test_n_t13_counting (test_morning.DaysTest.test_n_t13_counting)
AssertionError: 40 != 41
FAIL: test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard)
AssertionError: Regex didn't match: '^About the can(…' not found in 'About the can (a little): you thought Daniel took it, today at 10:54.'
Ran 246 tests in 176.634s
FAILED (failures=2)
```

**Seen, not changed:** the refusal above.
- **What happens.** When a stretch's asks run out mid-turn, a person asked aside refuses: the rules choose
  `refuse_aside` without asking the model. The story says "the model's answer could not be used", but no answer was
  asked for.
- **Why it matters.** It is a choice made by the code, not the AI. That is against the North Star's "the AI owns
  judgment".
- **Where it comes from.** It predates these fixes: it comes with the quiet day's budget caps.

**RED, before any production change** (`$S/red.txt`, stack frames left out):
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning.QuietDayTest.test_w5_is_known_from_a_neighbour_line_that_came_back_with_nothing test_morning.QuietDayTest.test_weakness_shifts_the_near_table_by_half_of_the_far test_morning.QuietDayTest.test_the_suspicion_line_says_today_from_minute_90 < /dev/null
exit 1
FAIL: test_w5_is_known_from_a_neighbour_line_that_came_back_with_nothing
AssertionError: {'daniel': True, 'elena': False, 'leo': False, 'mara': False} != {'daniel': True, 'elena': False, 'leo': True, 'mara': True}
FAIL: test_weakness_shifts_the_near_table_by_half_of_the_far
AssertionError: Tuples differ: (0.58, 0.14, 0.18, 0.1) != (0.6, 0.14, 0.18, 0.08)
FAIL: test_the_suspicion_line_says_today_from_minute_90
AssertionError: 'today at minute 60' not found in 'About the can (some): you thought Leo took it, two days ago at minutes 45, 48, 51 and 54, and the night before last, and yesterday at minutes 06, 09, 12 and 15, and last night, and this morning at minute 60.'
Ran 3 tests in 0.300s
FAILED (failures=3)
```

**After the three fixes, before the old tests were updated** (`$S/green.txt`). The 3 new tests pass. The 3 failures
are the expectations listed above:
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning.QuietDayTest < /dev/null
exit 1
FAIL: test_v16_seed_1_until_w5
AssertionError: {'daniel': True, 'elena': True, 'leo': True, 'mara': True} != {'daniel': True, 'elena': False, 'leo': False, 'mara': False}
FAIL: test_w5_is_offered_once_someone_knows_next_door_is_empty
AssertionError: {'daniel': True, 'elena': False, 'leo': True, 'mara': True} != {'daniel': True, 'elena': False, 'leo': False, 'mara': False}
FAIL: test_weakness_shifts_the_street_tables
AssertionError: Tuples differ: (0.6, 0.14, 0.18, 0.08) != (0.58, 0.14, 0.18, 0.1)
Ran 56 tests in 25.528s
FAILED (failures=3)
```

**After they were updated** (`$S/green2.txt`):
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning.QuietDayTest < /dev/null
exit 0
Ran 56 tests in 27.108s
OK
```

## 4. What a real family would do

- **Fix 1.** Leo and Mara saw or heard Daniel come back from next door empty-handed. A real family would take that as
  "there is nothing left next door". They would not send someone back there alone, and would talk about the houses
  further along instead. Elena slept through it and was told nothing, so for her there may still be food next door.
- **Fix 2.** A weak body slows you down most on a long walk in the open. A few steps to the neighbour's door cost far
  less. Against it: a dizzy person is clumsy at any distance. Half the shift, rather than none, keeps that.

## 5. Commands and raw output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. Every result below is from the final code.

### 5.1 DONE 2 and 3: v16 from a copy of `cache/v16` (`$S/replay_v16_fix.py`)
This is stage B's `replay_v16_b.py`, plus each scene's knowers with their lines, and whether the first prompt's
speaker knows.
```
$ sha256sum cache/v16/*.json > $S/v16cache.sha
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/replay_v16_fix.py "$PWD"
daniel_ate_it-seed1: first prompt with no cached answer: day2, Daniel, minute 00 (after 67 cached answers, 0 live: True)
  who knows next door is empty at that point: ['daniel', 'elena', 'leo', 'mara']; the prompt carries the street line: True, the far house line: True, the two day options: True
  day2: knows next door is empty: ['daniel', 'elena', 'leo', 'mara']
    daniel: About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
    elena: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
    leo: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
    mara: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
  the prompt's speaker knows: True
  scenes finished before it, equal to runs/v16's transcript: {'day1': True, 'night': True, 'mind1': True}
daniel_ate_it-seed2: first prompt with no cached answer: day3, Leo, minute 00 (after 96 cached answers, 0 live: True)
  who knows next door is empty at that point: ['daniel', 'leo', 'mara']; the prompt carries the street line: True, the far house line: True, the two day options: True
  day2: knows next door is empty: []
  day3: knows next door is empty: ['daniel', 'leo', 'mara']
    daniel: About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
    leo: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
    mara: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
  the prompt's speaker knows: True
  scenes finished before it, equal to runs/v16's transcript: {'day1': True, 'night': True, 'mind1': True, 'day2': True, 'night2': True, 'mind2': True}
daniel_ate_it-seed3: first prompt with no cached answer: day3, Daniel, minute 00 (after 135 cached answers, 0 live: True)
  who knows next door is empty at that point: ['daniel', 'leo', 'mara']; the prompt carries the street line: True, the far house line: True, the two day options: True
  day2: knows next door is empty: []
  day3: knows next door is empty: ['daniel', 'leo', 'mara']
    daniel: About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
    leo: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
    mara: About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
  the prompt's speaker knows: True
  scenes finished before it, equal to runs/v16's transcript: {'day1': True, 'night': True, 'mind1': True, 'day2': True, 'night2': True, 'mind2': True}
```

### 5.2 The cache, after
```
$ sha256sum -c $S/v16cache.sha
cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed1.json: OK
cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed2.json: OK
cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed3.json: OK
```

### 5.3 The frozen versions
```
$ for v in v14 v13 v12 v11 v10 v9; do env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done > $S/frozen.txt 2>&1
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
daniel_ate_it-seed1: replayed 91 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 87 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ grep -c IDENTICAL $S/frozen.txt
18
```

### 5.4 The full suite
```
$ ( time env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" ) > $S/full.txt 2>&1
Ran 246 tests in 174.057s
OK
real	2m55.244s
user	0m0.030s
sys	0m0.045s
exit 0
```
