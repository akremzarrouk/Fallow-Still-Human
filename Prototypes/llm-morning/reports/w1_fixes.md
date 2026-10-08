# W1 fixes: eating resets fasting; a water haul and what the house knows

Mode: implement. These are two fixes to W1 (`reports/w1_impl.md`) before its live run, and then the commit of W1. No
API call was made, no cache was written, and no frozen version was touched. Paths are relative to
`Prototypes/llm-morning/`. Raw outputs are in `runs/w1_fixes/`.

## Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| 1 | Both tests fail before and pass after | **yes** | Before: 2 failures (`runs/w1_fixes/red.stdout.txt`). Each fix taken out again: each test fails, and every file is restored with its sha256 (`runs/w1_fixes/red_check.stdout.txt`). After: OK. |
| 2 | No-API replay of v16 seed 2 through night 2 is IDENTICAL | **yes** | Story and transcript are byte for byte those of before W1 (§3, command 4). |
| 3 | v9 to v14 replays IDENTICAL; the full suite passes | **yes** | 18 replays, each with story and transcript IDENTICAL; 6 exits 0. **284 tests OK** (W1's 282 + 2). |
| 4 | Nothing modified; only the runs/v6 replay files untracked | **yes** | `git status --short` after the commit (given in the reply). |

## 1. The fixes

**Fix 1: eating resets fasting at that minute.**
- **What was wrong:** `quiet.Quiet.fast` counts from `p.needs["ate_at"]`, which only `quiet.setup` set, each morning,
  from the chronicle's eat events. A meal during a quiet day changed nothing until the next morning, so the body line
  still said "…for days now" after it. The W1 fake run had 13 such lines ("hungry, for days now: …").
- **The fix:** `Quiet.ate(p, minute)` sets their `ate_at` to that minute and their fasting stage at once (and the
  stage the next tick compares with). Cold from fasting follows too; wet stays wet. `world.Morning.apply` calls it
  for `eat`, `eat_given`, and every eater of a `share`, from day 3 on.
- **Nothing else moves:** the next morning still counts from the chronicle, which records the same meal.
- **In the fake run:** the 10-day fake run of seed 2 now has no "hungry, for days now" line, and still no body line
  that forbids an act (§3, command 5).

**Fix 2: a trip next door that brought water and no food.**
- **What I checked first: knowing next door is empty was already right.** `night.knows_next_door_empty` reads the
  food, never the water: the own visit's `found - took == 0`, or the heard trip's `took`.
- **The check, before any change** (`runs/w1_fixes/knows_empty_before.stdout.txt`): v16 seed 2, night 3, Daniel next
  door, clean, 9 L of water and no food. On day 4 all four know next door is empty, and all four are offered
  `volunteer_far`. So the far options did not vanish after a water haul.
- **What was wrong was what the record said came home.**
  - The night's outcome (`night.outcome_class`) was "back with nothing" for a water haul. The chronicle's street
    event keeps it.
  - Block C's line for an older night (`memory.person_line`, `went_out`) turned it into "…and came back with nothing".
  - The day lines, written from the group's own `water` (`seen_outcome`, the neighbour's-house, outings and street
    lines), already said "came back with water".
- **The fix:**
  - The outcome now includes the water: "back with water", "back with food and water", "back shaken, with water".
    "Back shaken, with nothing", "back with food" and the rest are unchanged.
  - Block C's line says "came back with water" or "came back with food and water".
  - Nights 1 and 2 carry no water, so their outcomes are as before.
- **The test** holds the rule and the lines together: knowing it is empty, the far option for all four, the
  neighbour's-house lines, the street event's outcome, and block C's line seen from day 5.

**Files changed:** `quiet.py` (`Quiet.ate`), `world.py` (the three calls), `night.py` (`outcome_class` with water, and
its call), `memory.py` (block C's line), `test_morning.py` (the two tests). Nothing else.

**Seen, not changed** (out of this scope): block C's `went_out` line says "went out to the neighbour's house" for a trip
further along too (`memory.py`, `person_line`). This predates W1.

## 2. Test names

In `test_morning.PhysicalLayerTest`:
- `test_eating_on_a_quiet_day_resets_fasting_at_that_minute`: eat, share (every eater) and eat_given at a food
  moment. Each resets `ate_at` to that minute, and the stage to 0; the body line has no fasting words.
- `test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food`: as in fix 2 above.

## 3. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. `$S` is the session scratchpad.

**1. Red** (`runs/w1_fixes/red.stdout.txt`)
```
$ ... .venv/Scripts/python.exe -m unittest $T.test_eating_on_a_quiet_day_resets_fasting_at_that_minute $T.test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food < /dev/null
exit 1
FAIL: test_eating_on_a_quiet_day_resets_fasting_at_that_minute (test_morning.PhysicalLayerTest.test_eating_on_a_quiet_day_resets_fasting_at_that_minute)
AssertionError: -1920 != 2880
FAIL: test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food (test_morning.PhysicalLayerTest.test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food)
AssertionError: 'back with nothing' != 'back with water'
Ran 2 tests in 1.691s
FAILED (failures=2)
```
After the fixes, the second test's block C wording was corrected in the test: night 3 seen from day 5 is "The night
before last", not "Two nights ago". The red check below runs the corrected test.

**2. Knowing next door is empty, before fix 2** (`runs/w1_fixes/knows_empty_before.stdout.txt`)
```
$ ... .venv/Scripts/python.exe runs/w1_fixes/knows_empty_before.py < /dev/null
exit 0
night 3: clean food 0 water 9.0 outcome 'back with nothing'
day 4 knows_empty: {'daniel': True, 'elena': True, 'leo': True, 'mara': True}
day 4 volunteer_far offered: {'daniel': True, 'elena': True, 'leo': True, 'mara': True}
```

**3. Each fix taken out, and green** (`runs/w1_fixes/red_check.stdout.txt`, `runs/w1_fixes/green.stdout.txt`)
```
$ ... .venv/Scripts/python.exe runs/w1_fixes/red_check.py < /dev/null
exit 0
fix 1 out: eating does not move ate_at (quiet.py): test_eating_on_a_quiet_day_resets_fasting_at_that_minute: exit 1; AssertionError: -1920 != 2880 | FAILED (failures=1)
  quiet.py restored: sha256 same
fix 2 out: the outcome without the water (night.py): test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food: exit 1; AssertionError: 'back with nothing' != 'back with water' | FAILED (failures=1)
  night.py restored: sha256 same
fix 2 out: block C's line without the water (memory.py): test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food: exit 1; AssertionError: "The [25 chars] went out to the neighbour's house and came back with nothing." != "The [25 chars] went out to the neighbour's house and came bac | FAILED (failures=1)
  memory.py restored: sha256 same
every one failed without its rule, and every file is restored
$ ... .venv/Scripts/python.exe -m unittest $T.test_eating_on_a_quiet_day_resets_fasting_at_that_minute $T.test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food < /dev/null
exit 0
Ran 2 tests in 2.337s
OK
```

**4. DONE 2** (`runs/w1_fixes/done2.stdout.txt`; compared with the replay saved before W1, `reports/w1_impl.md` §5)
```
$ ... .venv/Scripts/python.exe runs/facts_evening/prefix.py . $S/w1/prefix_fix 2 < /dev/null
daniel_ate_it-seed2: through night 2 and mind 2: 96 answers from the cache, 0 live
exit 0
daniel_ate_it-seed2.md: before W1 vs after the fixes: IDENTICAL
daniel_ate_it-seed2.transcript.json: before W1 vs after the fixes: IDENTICAL
```

**5. The 10-day fake run of seed 2 again** (`runs/w1_fixes/fake10.py`, which is `runs/w1_impl/done3.py` writing here;
`runs/w1_fixes/fake10_summary.stdout.txt`; full stdout `runs/w1_fixes/fake10.stdout.txt`)
```
$ ... .venv/Scripts/python.exe runs/w1_fixes/fake10.py < /dev/null
exit 0
morning.run(2, fake=True, days=10): exit 0; asks 540 (fake)
DONE 4: prompts 540; 'Your body:' lines 540 (13 distinct); matching "impossible|cannot|can't|unable|barely (stand|walk|move)": 0
    24 × Your body: a little hungry.
    47 × Your body: hungry.
     3 × Your body: starving, and you have hardly slept.
    53 × Your body: starving, for days now: you are thin and weak; stairs and carrying things tire you fast; and you feel cold, even indoors.
     7 × Your body: starving, for days now: you are thin and weak; stairs and carrying things tire you fast; you feel cold, even indoors; and you have hardly slept.
   146 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; and you feel cold, even indoors.
     5 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; and you have hardly slept.
     3 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; you are wet and cold; and you have hardly slept.
    74 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; you feel cold, even indoors; and you have hardly slept.
    75 × Your body: starving.
    17 × Your body: starving; hunger comes in waves.
    53 × Your body: starving; hunger comes in waves; and you have hardly slept.
    33 × Your body: very hungry.
```
- **No body line says "hungry, for days now"** after a meal; W1's run had 13 (`reports/w1_impl.md` §3).
- **The fake's path differs from W1's** (540 asks, against 581), since its prompts changed.

**6. DONE 3** (`runs/w1_fixes/frozen.stdout.txt`, `runs/w1_fixes/unittest.stdout.txt`)
```
$ for v in v14 v13 v12 v11 v10 v9; do ... .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done
18 replays (seeds 1-3 of each version): story IDENTICAL and transcript IDENTICAL on every one; DIFFERS: 0
      6 exit 0
$ ( time ... .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" )
Ran 284 tests in 299.517s
OK
real	5m0.977s
exit 0
```

**7. Before the commit**
```
$ git status --short
 M chronicle.py
 M data.py
 M memory.py
 M mind.py
 M morning.py
 M night.py
 M quiet.py
 M story.py
 M talk.py
 M test_morning.py
 M world.py
?? reports/w1_impl.md
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
?? runs/w1_fixes/
?? runs/w1_impl/
?? truth.py
?? water.py
?? weather.py
```
The commit holds W1, these fixes, `reports/w1_impl.md`, `runs/w1_impl/`, this report and `runs/w1_fixes/`. Its
`git log --oneline` line and the `git status` after it are in the reply.
