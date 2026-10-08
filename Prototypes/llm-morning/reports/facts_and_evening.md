# Facts about outings, and an evening moment (Q5)

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset. `cache/v16` and `cache/v19` were
read through temp copies only, and their sha256s are unchanged (§5.5). Paths are relative to `Prototypes/llm-morning/`.
Raw outputs are in `runs/facts_evening/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\ba344a5c-5509-4487-aefe-3209becb4468\scratchpad\fe`.

From `reports/v19_contradictions.md` §1, §2 and §4, and `reports/days_v19.md` §1–§2:
1. **Far positions are heard as what they are,** not as "says he will not go".
2. **The street line says which houses further along were searched,** when, by whom, and what they held. It uses the
   neighbour's-house line's knowledge rule.
3. **An outings line** in every quiet-day and quiet-night prompt lists each trip the person knows of. It sits in the
   trip block, outside the 1400 budget.
4. **The carried-in trip positions** are named as said yesterday about last night.
5. **Q5, the evening:** at 19:00, with its own 8 asks on top of the day's 40.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The tests for 1 to 5 fail before and pass after | **PASS** | 7 new tests (§3). RED on HEAD's code: 6 failures and 1 error, each on the missing behaviour (§5.1). After: all pass. |
| 2 | Built from v19 seed 3's recorded state, no API: (a) Leo's day-5 prompt carries both of Daniel's trips; (b) Leo's day-4 prompts show Daniel's far offer as an offer; (c) Mara's day-4 street line says one house was searched and held nothing | **PASS** | (a) 11 of 11 of Leo's day-5 prompts. (b) 5 of Leo's 11 day-4 prompts carry "Daniel offers to go further along the street tonight"; 0 carry "Daniel says he will not go". (c) Quoted below (§2). |
| 3 | A fake run with `--days 5`: Q5 fires at 19:00 on a day with a trip position, and not on a day without one; no day over 48 asks | **PASS** | Run A, the plain fake: Q5 fired at 19:00 on days 3, 4 and 5; day asks 45, 48, 48. Run B, no trip position on day 4: Q5 fired at 19:00 on days 3 and 5; on day 4 "no trip position today"; day asks 45, 33, 48 (§5.3). |
| 4 | v16 seeds 2 and 3 replay through night 2 as at HEAD; v9 to v14 IDENTICAL; the full suite passes | **PASS** | Story and transcripts through mind 2 are byte-identical between HEAD's code and the new code, for both seeds. Frozen: 18 of 18 IDENTICAL. Suite: `Ran 253 tests`, `OK` (§5.4–§5.6). |

## 1. The change

| File | Change |
|---|---|
| `world.py` | **Fix 1:** `FAR_GIST` (`world.py:89`). `line_text` uses it on a quiet day (`world.py:1516`); days 1 and 2 keep `trip_gist`. **Fix 3:** `Morning.outings` (`world.py:384`); `trip_lines` adds the outings line after the street line (`world.py:719`), so the budget's trip block counts it (`world.py:1114-1116`). **Fix 2:** the house line's far places also go to whoever has a street line (`world.py:1062`). **Fix 5:** the evening line just before "Now" (`world.py:1072`). |
| `night.py` | **Fixes 2 and 3:** `trips_known` (`night.py:181`): their own trips, and those whose members they know went out (`night.knows`, heard_trip's rule). `street_line` is rewritten (`night.py:205`); `outings_line` is new (`night.py:231`). `next_day` gives the street line to knowers as before, and to anyone whose line is not `STREET_UNSEARCHED` (`night.py:1092`). It sets the outings line on a quiet day (`night.py:1095`). **Fix 4:** block A's Y7 heading (`night.py:1003`). Day 2's carry-in (`carry_in`) is unchanged. |
| `quiet.py` | **Fix 5:** `EVENING`, `EVENING_ASKS`, `EVENING_LINE`, `EVENING_TEXT` (`quiet.py:45-47`). `reserved` (`quiet.py:171`): `spent` (`quiet.py:222`) ignores the day's 40 during Q5's stretch, whose own cap is 8 (`begin`, `quiet.py:231`). `evening` (`quiet.py:449`) is checked in `step` (`quiet.py:547`). `next_event` makes 19:00 an event (`quiet.py:558`). `play` begins a Q5 stretch with its 8, reserved (`quiet.py:796`). `evening_lines` (`quiet.py:662`). |
| `morning.py`, `story.py` | A Q5 log entry's progress line (`morning.py:170`), its story row (`story.py:609`), and `q5_fired` in the meta (`morning.py:97`). |
| `test_morning.py` | 7 new tests, and 4 existing tests and a helper changed (§3). |

**The lines, as written:**
- **Fix 1:** `Daniel offers to go further along the street tonight: "…"` and `Daniel says someone should try the houses
  further along the street tonight: "…"`.
- **Fix 2:** one house:
  `About the street: Daniel searched one house further along it last night, and it held no food; the houses past it have not been searched: nobody knows what is left in them, and they are further and more dangerous than next door.`
  For their own trip, "you searched". For two or more houses: "two houses further along it have been searched: one by
  Daniel the night before last, which held no food; one by you last night, which held 4 portions, all brought back;
  the houses past them have not been searched: …".
- **Fix 3:**
  - One item per trip they know of, oldest first, in the form `About going out at night: <who> went <to the neighbour's house | further along the street> <night> <outcome>; …`.
  - **Outcome of their own trip** (from the group's record): "got inside and found no food", "got inside, found N
    portions and brought back K", "turned back before getting inside", or "lost sight of X in the street, and he has
    not come back"; a far trip says "got inside a house there".
  - **Outcome of another's trip** (the neighbour's-house line's three): "and came back with food", "came back with
    nothing", or "has not come back".
  - **With none:** `About going out at night: as far as you know, nobody has gone out.`
- **Fix 4:** `- What was said yesterday about going out last night, where it was left: Mara said Daniel is the one who should go (min 06); …`
- **Fix 5:**
  - At Q5's minute, everyone awake in that room has `It is evening; in two hours everyone goes to bed.` in their memory.
  - It is also shown just before "Now" to whoever acts at that minute: a prompt lists its own minute's records only
    from the next minute on (`world.py:1101`).
  - The asked person's trigger is "it is evening, and in two hours everyone goes to bed".

**Choices, and why:**
- **Fix 1 holds from day 3 on only.** The brief says not to change any prompt of days 1 and 2. A far position on day
  2 can happen only where someone knows next door is empty by then: v16 seed 1, whose day 2 already misses the cache.
  There it still reads "says he will not go".
- **A far trip scared off before the door searched no house** (`found` is None). The street line counts only trips
  that got inside, so for Leo it stays `STREET_UNSEARCHED` (test 2). The outings line still lists such a trip: "came
  back with nothing", or for the goer "turned back before getting inside".
- **The street line goes to anyone who knows of a far trip that got inside,** as fix 2 says "anyone". If they do not
  know next door is empty, they get the far places in their house line too, so the line does not name a place the
  house line forbids. They do not get `propose_far`, `volunteer_far` or `go_further`; those stay W5's, for knowers.
- **Q5's check:**
  - It happens once, at the first quiet minute from 19:00, so after a played stretch that runs through 19:00.
  - Candidates are the people awake (not resting) in a room with at least one other awake person.
  - Of those, the one whose last trip act today has the latest `decided_at` is asked.
- **Q5's ask is not held by the 12 and 4 quiet-ask caps,** because its 8 are reserved. It is recorded in
  `quiet_asked`, so it counts toward those caps for any Q1 or Q2 after it.
- **The evening line is a "Now" line,** so it counts against the 1400 budget. In DONE 2's run it cost Daniel's 19:00
  prompt one more of the day's oldest lines (§4).

**Seen, not changed:**
- **Elena (seed 3) is told "as far as you know, nobody has gone out".** She heard the front door on nights 2 and 3,
  but hearing the door does not put anyone in `night.knows`. Her neighbour's-house line says the same: "so there may
  be food there". This is the rule fix 3 asks for.
- **An aside's answer after Q5's 8 are spent** becomes the code's `refuse_aside`, with "could not be used (the
  evening's 8 asks are spent)". This is the same fallback `reports/stage_b_fixes.md` records for the day's cap.
- **The asked person's answer is open.** In the fake runs Q5's asked person chose `sit_elena`, `aside_elena`,
  `reassure_elena` and others: the line states the evening, not an act.

## 2. DONE 2: v19 seed 3 on the new code (`runs/facts_evening/done2.py`)

**How it runs:**
- Days 1–2, nights 1–2 and minds 1–2 come from a temp copy of `cache/v19`: 135 answers, their prompts unchanged.
- From day 3 on, each prompt is answered with v19's own recorded answer for the same scene and speaker, by minute
  by day and by options at night. The 132 recorded answers are in `runs/facts_evening/v19_seed3_answers.json`, from
  `reports/v19_contradictions.md`'s traced replay.
- All 132 were used. The only asks with no recorded answer are Q5's stretch at 19:00 on days 3, 4 and 5, 10 in all,
  answered `silent`.
- The trips come out as in v19: night 2, Daniel next door, nothing; night 3, Daniel further along, house 1 held 0.

**(a) Leo's day-5 outings line** (all 11 of his day-5 prompts):
```
About going out at night: Daniel went to the neighbour's house three nights ago and came back with nothing; Daniel went further along the street the night before last and came back with nothing.
```
**(b) Leo's day-4 prompts**, every line with Daniel's far offer (5 of 11 prompts; "Daniel says he will not go": 0):
```
- 09:57: Daniel offers to go further along the street tonight: "I went out last night and I am telling you I can find something further down the street."
1. Daniel offers to go further along the street tonight: "I already went out there and I'm going back tonight to find something for us."
1. Daniel offers to go further along the street tonight: "I went out last night and I am going to check the houses further down the street again tonight."
1. Daniel offers to go further along the street tonight: "I went out last night and I am telling you I can find something further down the street."
1. Daniel offers to go further along the street tonight: "I went out past the neighbour's house last night to look further down the street, and I will go again tonight if we need to."
```
**(c) Mara's day-4 street line:**
```
About the street: Daniel searched one house further along it last night, and it held no food; the houses past it have not been searched: nobody knows what is left in them, and they are further and more dangerous than next door.
```
**Everyone's day-4 lines** (day 5 the same, with "three nights ago" and "the night before last"; `done2.stdout.txt`):
```
day4 Daniel: About going out at night: you went to the neighbour's house the night before last, got inside and found no food; you went further along the street last night, got inside a house there and found no food.
day4 Daniel: About the street: you searched one house further along it last night, and it held no food; the houses past it have not been searched: …
day4 Elena: About going out at night: as far as you know, nobody has gone out.
day4 Leo: About going out at night: Daniel went to the neighbour's house the night before last and came back with nothing; Daniel went further along the street last night and came back with nothing.
day4 Leo: About the street: Daniel searched one house further along it last night, and it held no food; the houses past it have not been searched: …
day4 Mara: (the same two lines as Leo)
```

## 3. The tests

| Fix | Test (`test_morning.QuietDayTest`) | What it holds |
|---|---|---|
| 1 | `test_far_positions_are_heard_as_what_they_are` | v16 seed 2, day 3: `line_text` of `volunteer_far` and `propose_far` gives the two gists; a `refuse_to_go` still gives "says he will not go". Played: Daniel's `volunteer_far` at min 00 is in Leo's memory as "Daniel offers to go further along the street tonight: …". |
| 2 | `test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it` | Night 3: Daniel goes further along; clean; house 0 holds 0. Leo (awake in his room) and Mara (by the door) know; Elena slept. Day 4: Daniel "you searched one house …"; Leo and Mara "Daniel searched one house further along it last night, and it held no food; …"; Elena has none. Mara's line is in her prompt. Scared off before the door (`scare_there`): Leo's line is `STREET_UNSEARCHED`. |
| 3 | `test_every_quiet_prompt_carries_the_outings_line` | Day 3: each one's line, exactly; it is in `trip_lines` (the budget's trip block), and in day prompts at min 00 and at 03:30. On day 2: none. Night 3: every bedtime prompt carries it. Day 4: Leo and Mara list both trips; Daniel his two own; Elena "as far as you know, nobody has gone out". |
| 4 | `test_yesterdays_positions_are_named_as_said_yesterday_about_last_night` | Leo's day-3 block A has "- What was said yesterday about going out last night, where it was left: Mara said …"; no "About going to the neighbour's house last night". |
| 5 | `test_q5_at_19_asks_whoever_took_a_trip_position_last` | Daniel offers at min 00; Leo answers whenever he can (min 03 and 10:21). One Q5 entry, at 19:00, fired. Leo is asked, his act being the most recent, and the test computes this from the transcript. The stretch begins at 19:00 with 1 to 8 asks. Leo's decision there is `quiet: Q5`, `mode: model`. The evening line is in his memory and in his 19:00 prompt, just before "Now". |
| 5 | `test_q5_has_8_asks_on_top_of_the_days_40` | With `DAY_ASKS` set to 30 (this day spends 32 by 19:00), 30 asks before 19:00, then Q5 fires and its stretch has 1 to 8; the day's total is 30 + those. |
| 5 | `test_no_q5_without_a_trip_position` | An always-silent fake: no trip act all day; Q5's entry says "no trip position today"; no Q5 stretch. |

**Existing tests changed, because fix 5 or fix 3 overturns their expectations:**
- **`QuietDayTest.test_a_run_goes_on_to_day_5` and `DaysTest.test_n_t2_the_cycle`.** "day asks ≤ 40" becomes "Q5's
  stretch ≤ 8, and the rest ≤ 40". Their first run failed with day 3 at 42 and at 48.
- **`QuietDayTest.test_the_day_budget_holds_when_the_fake_keeps_talking`.**
  - **Before:** it expected 40 asks and a talk ended by "the day's asks are spent".
  - **Now:** this day spends 32 by 19:00, and Q5's 8 bring it to 40. So the test sets `DAY_ASKS` to 30. The asks
    outside Q5's stretch are then exactly 30, and the "spent" line still appears.
- **`DaysTest.test_n_t13_counting`.** It subtracts decisions made after a cap was spent. Its regex now also knows
  "the evening's 8 asks are spent". It failed with 48 != 49, and the one is an aside's answer after Q5's 8 (§1).
- **`without_blocks`, the helper of `NightTest.test_t12_the_budget`.** It strips the trip block before measuring the
  1450, and now also strips "About going out at night:", as stage B did for the street line. Without it, T12 failed
  at 1452.

**The fixture's first form, before it first passed.** The Q5 test first had Mara propose at min 03. She was not asked
then, so only Daniel had a position, and the test could not tell "the most recent" from "the only". It now has Leo
answer Daniel, and pins Leo.

## 4. The asked person's 19:00 prompt (DONE 2, day 3, Daniel), its end

The evening line was added after a first green run showed it missing from this prompt: the asked person's own minute
is not listed (§5.1).
```
What else happened today, most recent last:
- (earlier things, left out here)
- 12:48: you lay down on your bed.
- 16:45: you got up from your bed.
- 16:45: you went to the kitchen.
You last spoke with Elena at 10:51. Since then you sat in the kitchen until 12:48, then lay on your bed until 16:45.
You last spoke with Leo at 10:51. Since then you sat in the kitchen until 12:48, then lay on your bed until 16:45.
You last spoke with Mara at 10:51. Since then you sat in the kitchen until 12:48, then lay on your bed until 16:45.
It is evening; in two hours everyone goes to bed.
Now, 19:00, you are in the kitchen.
- Elena is here, sitting in the kitchen.
- Leo is here, sitting in the kitchen.
- Mara is here, sitting in the kitchen.
- 0 portions on the shelf.
You are the first to act in the kitchen this turn.
```
Its trip block, above, has: `About going out at night: you went to the neighbour's house last night, got inside and
found no food.` and `About going there tonight: Leo said you must stay home (min 03); Elena said you must stay home
(min 15); you said you still mean to go (10:51).`

## 5. Commands and raw output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. Every result is from the final code.

### 5.1 RED and GREEN
```
$ git stash push -- world.py night.py quiet.py morning.py story.py      # HEAD's code, the final tests
$ T=test_morning.QuietDayTest; env -u GEMINI_API_KEY … -m unittest $T.test_far_positions_are_heard_as_what_they_are $T.test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it $T.test_every_quiet_prompt_carries_the_outings_line $T.test_yesterdays_positions_are_named_as_said_yesterday_about_last_night $T.test_q5_at_19_asks_whoever_took_a_trip_position_last $T.test_q5_has_8_asks_on_top_of_the_days_40 $T.test_no_q5_without_a_trip_position < /dev/null > runs/facts_evening/red.stdout.txt 2>&1
exit 1
ERROR: test_q5_has_8_asks_on_top_of_the_days_40 — IndexError: list index out of range
FAIL: test_far_positions_are_heard_as_what_they_are — 'Daniel says he will not go: "I\'ll go."' != 'Daniel offers to go further along the street tonight: "I\'ll go."'
FAIL: test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it — 'Abou[13 chars] you got inside the next house further along l[135 chars]oor.' != 'Abou[13 chars] you searched one house further along it last [157 chars]oor.'
FAIL: test_every_quiet_prompt_carries_the_outings_line — {'daniel': [], 'elena': [], 'leo': [], 'mara': []} != {'daniel': ["About going out at night: you went to th[369 chars]g."]}
FAIL: test_yesterdays_positions_are_named_as_said_yesterday_about_last_night — '- What was said yesterday about going out last night, …' not found in […]
FAIL: test_q5_at_19_asks_whoever_took_a_trip_position_last — AssertionError: 0 != 1
FAIL: test_no_q5_without_a_trip_position — Lists differ: [] != [(False, 'no trip position today')]
Ran 7 tests in 2.848s
FAILED (failures=6, errors=1)
$ git stash pop                       # world.py, night.py, quiet.py, morning.py, story.py: cmp equal to the copies taken before
```
- **The evening line.** The Q5 test's last assertion (the evening line in Leo's 19:00 prompt) was added after the
  first green run and failed first (`runs/facts_evening/red_evening.stdout.txt`):
  `AssertionError: '\nIt is evening; in two hours everyone goes to bed.\nNow, 19:00, ' not found in 'You are Leo, …'`.
  `evening_lines` then made it pass.
- **GREEN:** the same 7 tests, `Ran 7 tests`, `OK`.

### 5.2 DONE 2
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/facts_evening/done2.py > runs/facts_evening/done2.stdout.txt 2>&1
exit 0; answers from cache/v19 (days 1-2, nights 1-2, minds 1-2): 135; sent to the recorded client: 142
  day3: 35 asks; v19's recorded answer: 32; not recorded in v19: [('daniel', 720, 'silent'), ('elena', 720, 'silent'), ('leo', 720, 'silent')]
  night3: 8 asks; v19's recorded answer: 8; not recorded in v19: []
  mind3: 4 asks; v19's recorded answer: 4; not recorded in v19: []
  day4: 44 asks; v19's recorded answer: 40; not recorded in v19: [('daniel', 720, 'silent'), ('mara', 720, 'silent'), ('leo', 720, 'silent'), ('elena', 720, 'silent')]
  night4: 4 asks; v19's recorded answer: 4; not recorded in v19: []
  mind4: 4 asks; v19's recorded answer: 4; not recorded in v19: []
  day5: 43 asks; v19's recorded answer: 40; not recorded in v19: [('mara', 720, 'silent'), ('elena', 720, 'silent'), ('daniel', 720, 'silent')]
  night2 groups: [(['daniel'], False, 'clean', 0, 0)]
  night3 groups: [(['daniel'], True, 'clean', 0, 0)]
  night4 groups: []
  Leo's day-5 prompts: 11; carrying both of Daniel's trips: 11
  Leo's day-4 prompts: 11; with 'Daniel offers to go further along the street tonight': 5; with 'Daniel says he will not go': 0
(the lines themselves: §2)
```

### 5.3 DONE 3 (`runs/facts_evening/done3.py`; runs in `runs/facts_evening/fake_A`, `fake_B`)
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/facts_evening/done3.py > runs/facts_evening/done3.stdout.txt 2>&1
A: exit 0; api_requests 354; days 5
  A day3: trip positions 9; day asks 45; Q5 [('19:00', True, 'daniel', None, 'kitchen')]; Q5 stretch [('19:00', '19:06', 8)]
  A day4: trip positions 11; day asks 48; Q5 [('19:00', True, 'leo', None, 'kitchen')]; Q5 stretch [('19:00', '19:06', 8)]
  A day5: trip positions 14; day asks 48; Q5 [('19:00', True, 'daniel', None, 'kitchen')]; Q5 stretch [('19:00', '19:09', 8)]
B: exit 0; api_requests 339; days 5; day-4 answers turned from a trip act to another: 10
  B day3: trip positions 9; day asks 45; Q5 [('19:00', True, 'daniel', None, 'kitchen')]; Q5 stretch [('19:00', '19:06', 8)]
  B day4: trip positions 0 (last None); day asks 33; Q5 [('19:00', False, None, 'no trip position today', None)]; Q5 stretch []
  B day5: trip positions 16; day asks 48; Q5 [('19:00', True, 'leo', None, 'kitchen')]; Q5 stretch [('19:00', '19:06', 8)]
```
- **The two runs.** A is `morning.run(2, fake=True, days=5)`, as `morning.py --seed 2 --fake --days 5` runs it, into a
  temp cache. B uses the same fake, except that on day 4 an answer picking a trip act is turned into `silent`.
- **"api_requests"** are the fake client's.
- **The full lines,** with each Q5 turn's acts, are in `done3.stdout.txt`.

### 5.4 DONE 4: v16 through night 2, HEAD's code against the new (`runs/facts_evening/prefix.py`)
```
$ for f in $(git ls-tree --name-only HEAD | grep -E '\.py$|config\.json$'); do git show HEAD:Prototypes/llm-morning/$f > "$S/head_code/$f"; done
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/facts_evening/prefix.py "$S/head_code" "$S/prefix_head" 2 3
daniel_ate_it-seed2: through night 2 and mind 2: 96 answers from the cache, 0 live
daniel_ate_it-seed3: through night 2 and mind 2: 135 answers from the cache, 0 live
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/facts_evening/prefix.py . "$S/prefix_after" 2 3      # same two lines
$ for f in daniel_ate_it-seed{2,3}.{md,transcript.json}; do cmp -s "$S/prefix_head/$f" "$S/prefix_after/$f" && echo "$f: HEAD vs after: IDENTICAL"; done
daniel_ate_it-seed2.md: HEAD vs after: IDENTICAL
daniel_ate_it-seed2.transcript.json: HEAD vs after: IDENTICAL
daniel_ate_it-seed3.md: HEAD vs after: IDENTICAL
daniel_ate_it-seed3.transcript.json: HEAD vs after: IDENTICAL
```
The suite's `QuietDayTest.test_v16_through_night_2_is_unchanged` (seeds 2 and 3 against `runs/v16`) also passes (§5.6).

### 5.5 The frozen versions, and the caches
```
$ for v in v14 v13 v12 v11 v10 v9; do env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done > runs/facts_evening/frozen.stdout.txt 2>&1
frozen IDENTICAL: 18; exits 0: 6
$ sha256sum -c "$S/caches.sha"          # cache/v16 (3) and cache/v19 (2), taken before the DONE runs: 5 OK
```

### 5.6 The full suite
```
$ ( time env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" ) > runs/facts_evening/unittest.stdout.txt 2>&1
Ran 253 tests in 245.429s
OK
real	4m6.817s
exit 0
```
- **253 tests:** 246 before, plus the 7 new ones.
- **Earlier full runs on the way:**
  - The first failed 4: `test_a_run_goes_on_to_day_5`, `test_the_day_budget_holds_…`, `test_n_t2_the_cycle`, and T12
    at 1452.
  - After the evening line, one more failed: `test_n_t13_counting`, 48 != 49.
  - Each was changed as §3 says.
- **No code changed after this run.** DONE 2–4 and the frozen checks above were rerun after the last code change:
  DONE 2's output was byte-identical, and DONE 3's moved as fake answers do with their prompts.
