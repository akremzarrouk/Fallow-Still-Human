# Preparing a 10-day run: yesterday's positions end with what happened, and a third fasting stage

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset. `cache/v16` and `cache/v20` were
read through temp copies only (§4.5). Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in
`runs/ten_days/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\ba344a5c-5509-4487-aefe-3209becb4468\scratchpad`.

From `reports/days_v20.md` §2 and §4, and `reports/quiet_day_design.md` §1.1:
1. **The carried-in positions line ends with what happened that night,** as the house knows it. In v19 and v20, "you
   stayed home last night" was said with the truth in the prompt. That line lists "X said Daniel must stay home"
   beside "last night", without the outcome.
2. **A third fasting stage at 144,** so the bodies keep changing to day 10. It has its own body line, a Q1 crossing,
   and a street shift beyond very weak.

Then a fake run of seed 3 to day 10.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The tests for 1 and 2 fail before and pass after | **PASS** | 2 new tests. Before: 2 failures, each on the missing behaviour (§4.1). After: pass. |
| 2 | v20 seed 3 rebuilt, no API: Leo's day-4 positions line ends with Daniel going further along anyway on night 3 and coming back with nothing | **PASS** | "…; then Daniel went further along anyway and came back with nothing." (§2). v20 seed 3 was rebuilt whole: all 141 of its answers were used, and the trips came out as in v20. |
| 3 | A fake run of seed 3 with `--days 10`: exit 0, day 10's bedtime, someone at the third stage, each day's largest prompt and the lines cut | **PASS** | Exit 0; day 10's last span ends at 21:00. The third stage: Daniel on day 6 (12:21), Mara and Elena on day 7. Size table §3. |
| 4 | v16 seeds 2 and 3 replay through night 2 as at HEAD; v9 to v14 IDENTICAL; the full suite passes | **PASS** | Story and transcripts through mind 2 are byte-identical between HEAD's code and the new code, both seeds. Frozen: 18 of 18 IDENTICAL. Suite: `Ran 257 tests`, `OK` (§4.4–§4.6). |
| 5 | git status: nothing modified, only the runs/v6 replay files untracked | **PASS** | After the commit (in the reply that delivered this report). |

## 1. The change

| File | Change |
|---|---|
| `night.py` | **Fix 1:** `night_came_to` (`night.py:1020`). Block A's positions line (Y7, `night.py:1011`) ends with "; then …": each group of that night, who went (with "you" for themself), next door or further along, "anyway" when a position they heard said nobody should go or that one of them must stay home, and what the house saw (`seen_outcome`: back with nothing, back with food, not back). With no trip: "then nobody went out". **Fix 2:** `SHIFTS["barely standing"]` (`night.py:82`), very weak plus the step from weak to very weak: (−0.20, 0, +0.04, +0.16). `body_shift` takes it at fasting stage 3 (`night.py:108`). |
| `quiet.py` | **Fix 2:** `BARELY = 144` (`quiet.py:26`); `fast_stage` gives 3 from it (`quiet.py:81`). Its body words, a situation with no act (`quiet.py:54`): ", and so weak you can barely stand: walking any distance feels impossible". Its record (`quiet.py:59`): "You had grown so weak you could barely stand; walking any distance felt impossible." Q1's word, "barely able to stand" (`quiet.py:447`). 144 is an event of the quiet day's clock, like 48 and 96 (`quiet.py:569`). |
| `world.py`, `story.py` | The word for the stage in an inner moment (`world.py:114`, `world.py:912`) and in the story (`story.py:564`). |
| `test_morning.py` | 2 new tests, and 1 existing test changed (§4.1). |

**Choices, and why:**
- **The line's end is what the house knows by morning** (`reports/household_knowledge.md`): who went, where, and
  food, nothing or not back. Not whether they got in or were scared. The goer gets "you"; their line says the same
  outcome, as the house saw it.
- **"Anyway"** depends on what the person heard: someone who heard "nobody should go" or "Daniel must stay home"
  reads "Daniel went … anyway". Someone who heard only Daniel's offer reads "Daniel went …".
- **Only from day 3's block A on.** Day 2's carry-in (`carry_in`, "About going to the neighbour's house last night,
  where it was left") is unchanged, so days 1 and 2 of v16 replay as before (DONE 4).
- **The third stage is fasting only.** It leaves Q2, Q5, rest (still due from very weak, `quiet.py:368`) and every
  option as they were: going out stays their choice, as at very weak (§1.1).
- **The street shift.** "The same size as the step from weak to very weak" gives (−0.08, 0, +0.02, +0.06) added to
  very weak's (−0.12, 0, +0.02, +0.10). Alone, far: (0.25, 0.17, 0.27, 0.31), against very weak's (0.33, 0.17,
  0.25, 0.25). Next door takes half, as before.

**Seen, not changed:**
- **Prompts over the 1400 budget after every cut.** In the fake 10-day run, 11 of 460 day and night prompts are still
  over the budget once the day's lines and every loose backstory line are gone: 1401 to 1529 (§3). 7 of the 11 are in
  Q5's stretch at 19:00, where the "Now" block holds a meeting line for each of the others and Q5's evening line.
  The other 4 are morning or mid-morning turns of days 4 and 6. The budget does not cut the "Now" block, the standing lines or the
  trip block.
- **The fake run loses two of the four.** Leo was lost on night 5 and Daniel on night 7, both far trips on the fake
  model's answers. From day 8, two people ask 4 to 10 times a day.

## 2. DONE 2: Leo's day-4 line, v20 seed 3 on the new code (`runs/ten_days/done2.py`)

**How it runs:**
- **The answers.** `runs/ten_days/v20_answers.py` replays `cache/v20` on HEAD's code (`361eb30`, v20's own,
  exported to `$S/head361`). It keeps every answer from day 3 on with its scene, speaker, minute and options: 141, as
  v20 seed 3's live asks (`runs/ten_days/v20_seed3_answers.json`).
- **The rebuild on the new code.**
  - Days 1–2, nights 1–2 and minds 1–2 come from a temp copy of `cache/v20`.
  - Each later prompt is answered with v20's recorded answer for the same scene and speaker: by minute by day, and by
    options at night.
  - All 141 were used: 133 sent to the recorded client, and both night minds' 8 straight from the cache, their
    prompts unchanged.
  - The nights came out as in v20: night 3 further along, clean, back with nothing; night 4 further along, back with
    4.

**Leo's day-4 line** (`runs/ten_days/done2.stdout.txt`):
```
- What was said yesterday about going out last night, where it was left: Daniel offered to go further along the street (19:00); Elena said Daniel must stay home (19:00); you said Daniel must stay home (19:00); then Daniel went further along anyway and came back with nothing.
```
The others' day-4 lines end the same way: Daniel's with "then you went further along anyway and came back with
nothing". Day 5's lines, all four, end "then Daniel went further along anyway and came back with food".

## 3. DONE 3: a fake run of seed 3 to day 10 (`runs/ten_days/done3.py`)

`morning.run(3, fake=True, days=10)`, as `morning.py --seed 3 --fake --days 10` runs it, into a temp cache. The files
are in `runs/ten_days/fake10/`. Wrappers record, without changing anything:
- each day and night prompt's size: as `max_prompt_tokens` counts it, and against the 1400 budget;
- the lines the budget cut: "today" (the day's own lines) and "before" (backstory);
- once per person per morning, what the 560 memory bound trimmed.
```
exit 0; days 10; api_requests 488 (the fake client's)
day 10: last span ends 21:00; stretches [('min 00', 'the morning'), ('10:39', 'Q2'), ('19:00', 'Q5')]
```

**The third stage, and who is in the house.** Fasting is at 21:00, from each day's needs log.

| Day | Crossings to stage 3 | Q1 at it | Fasting at 21:00 | Day asks | Away |
|---|---|---|---|---|---|
| 3 | — | — | Daniel 71.2, Elena 62.9, Leo 61.9, Mara 58.8 | 47 | — |
| 4 | — | — | 98.8, 83.3, 85.9, 81.6 | 48 | — |
| 5 | — | — | 126.4, 103.7, 109.9, 104.4 | 48 | — |
| 6 | Daniel 12:21 | not asked (asleep) | Daniel 154.0, Elena 124.1, Mara 127.2 | 34 | Leo |
| 7 | Mara 14:42; Elena 20:27 | Mara not asked (asleep); **Elena asked** | 181.6, 144.5, 150.0 | 40 | Leo |
| 8 | — | — | Elena 164.9, Mara 172.8 | 4 | Leo, Daniel |
| 9 | — | — | 185.3, 195.6 | 10 | Leo, Daniel |
| 10 | — | — | 205.7, 218.4 | 8 | Leo, Daniel |

**Each day's largest prompt, and what the limits cut.**
- **Prompts:** how many prompts the scene asked.
- **Largest:** the size estimate as `max_prompt_tokens` counts it / the part counted against the 1400 budget, with whose
  prompt and when.
- **Most cut:** the budget's largest cut in any one prompt, today / before.
- **With a cut:** how many prompts lost any line.
- **Memory bound:** the 560 bound, as mornings with A shortened / C thoughts / C lines / B lines removed. "—" where there
  is no block A to bound (day 1, and the nights).

| Scene | Prompts | Largest (who, when) | Most cut | With a cut | Memory bound |
|---|---|---|---|---|---|
| day 1 | 71 | 1673 / 1399 (Mara, min 51) | 25 / 4 | 49 | — |
| night 1 | 4 | 1580 / 1383 (Mara) | 26 / 1 | 4 | — |
| day 2 | 107 | 1990 / 1379 (Mara, min 60) | 65 / 7 | 86 | 0 / 0 / 0 / 0 |
| night 2 | 4 | 1829 / 1389 (Daniel) | 65 / 2 | 4 | — |
| day 3 | 47 | 2118 / 1389 (Mara, 10:33) | 45 / 9 | 45 | 0 / 0 / 0 / 0 |
| night 3 | 6 | 1971 / 1384 (Mara) | 42 / 4 | 6 | — |
| day 4 | 48 | 2391 / 1382 (Elena, min 12) | 48 / 9 | 44 | 0 / 0 / 0 / 0 |
| night 4 | 4 | 2199 / 1395 (Elena) | 50 / 5 | 4 | — |
| day 5 | 48 | 2396 / 1529 (Leo, 19:00) | 49 / 9 | 40 | 0 / 0 / 0 / 0 |
| night 5 | 7 | 2124 / 1392 (Leo) | 49 / 5 | 7 | — |
| day 6 | 34 | 2407 / 1480 (Elena, 10:09) | 38 / 9 | 33 | 0 / 0 / 0 / 0 |
| night 6 | 5 | 2222 / 1397 (Daniel) | 36 / 5 | 5 | — |
| day 7 | 40 | 2410 / 1388 (Elena, 11:21) | 44 / 9 | 37 | 0 / 0 / 0 / 0 |
| night 7 | 7 | 2254 / 1397 (Elena) | 50 / 6 | 7 | — |
| day 8 | 4 | 2347 / 1377 (Elena, min 03) | 4 / 5 | 3 | 0 / 0 / 0 / 0 |
| night 8 | 3 | 2262 / 1397 (Mara) | 11 / 5 | 3 | — |
| day 9 | 10 | 2276 / 1396 (Elena, 10:45) | 17 / 5 | 8 | 0 / 0 / 0 / 0 |
| night 9 | 3 | 2149 / 1398 (Elena) | 19 / 5 | 3 | — |
| day 10 | 8 | 2354 / 1393 (Elena, 10:39) | 7 / 5 | 4 | 0 / 0 / 0 / 0 |

**Prompts over the 1400 budget after every cut** (§1, "Seen"), from the same run's records. The columns are scene,
person, when, estimate, budget, cut today, cut before:
```
day3 elena 19:00 2042 1415 41 9      day5 leo 19:00 2396 1529 47 7       day6 elena 19:00 2391 1464 27 9
day4 leo min 15 2260 1421 16 7      day5 mara 19:00 2315 1441 45 9      day6 elena 19:03 2347 1401 30 9
day4 elena 09:39 2379 1405 30 9     day5 daniel 19:00 2300 1461 42 8    day7 mara 19:00 2351 1425 30 9
day4 leo 09:39 2263 1403 28 7       day6 elena 10:09 2407 1480 17 9
```

## 4. Commands and raw output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset.

### 4.1 The tests (`test_morning.QuietDayTest`)

| Fix | Test | What it holds |
|---|---|---|
| 1 | `test_yesterdays_positions_end_with_what_happened_that_night` | **Night 3 (v16 seed 2):** Daniel goes further along; back with nothing. On day 3 everyone heard Daniel's `volunteer_far` (min 00) and Elena's "nobody should go" (min 15). Day 4: Leo's, Elena's ("you said nobody should go") and Daniel's ("then you went further along anyway") lines, exactly. **Daniel's offer only, food home:** "then Daniel went further along and came back with food" (no "anyway"). **Nobody went out:** "then nobody went out". |
| 2 | `test_a_third_fasting_stage_at_144` | `fast_stage` at 95.99, 96, 143.99, 144 and 300 is 1, 2, 2, 3, 3. The body line at stage 3. The shift is (−0.20, 0, +0.04, +0.16), equal to very weak plus the step from weak to very weak; very weak's own is unchanged. The far alone table at stage 3 is (0.25, 0.17, 0.27, 0.31). **Played:** Leo's last meal set so he crosses 144 at 12:00 of day 3. He has one need event at 12:00 with the stage's record, one Q1 check at 12:00, and his body line starts with stage 3's words. |

**Changed:** `test_yesterdays_positions_are_named_as_said_yesterday_about_last_night` (`reports/facts_and_evening.md`,
fix 4). Leo's day-3 line now ends "; then Daniel went to the neighbour's house anyway and came back with nothing." On
day 2, Elena said nobody should go, and Daniel went on night 2.

**RED** (`runs/ten_days/red.stdout.txt`), before any production change:
```
$ T=test_morning.QuietDayTest; env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest $T.test_yesterdays_positions_end_with_what_happened_that_night $T.test_a_third_fasting_stage_at_144 < /dev/null > runs/ten_days/red.stdout.txt 2>&1
exit 1
FAIL: test_yesterdays_positions_end_with_what_happened_that_night
AssertionError: Lists differ: ['- W[157 chars]n 15).'] != ['- W[157 chars]n 15); then Daniel went further along anyway a[23 chars]ng.']
FAIL: test_a_third_fasting_stage_at_144
AssertionError: Lists differ: [1, 2, 2, 2, 2] != [1, 2, 2, 3, 3]
Ran 2 tests in 0.764s
FAILED (failures=2)
```
**Corrections to the tests, before they first passed:**
- **Test 2's last assertion** assumed Leo's sleep debt at day's end ("hardly slept"). By then he is exhausted, so it
  checks the fasting part of the line only.
- **Some long lines** were rewrapped.

**GREEN:** the two tests, `OK`. Then `test_morning.QuietDayTest`: `Ran 67 tests`, `OK`
(`runs/ten_days/quietclass.txt`).

### 4.2 DONE 2
```
$ for f in $(git ls-tree --name-only HEAD | grep -E '\.py$|config\.json$'); do git show HEAD:Prototypes/llm-morning/$f > "$S/head361/$f"; done
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/ten_days/v20_answers.py "$S/head361" 3 runs/ten_days/v20_seed3_answers.json
seed 3: replay exit 1 (1: no original story in the temp folder); answers from day 3 on: 141; by scene {'day3': 40, 'night3': 8, 'mind3': 4, 'day4': 48, 'night4': 9, 'mind4': 4, 'day5': 28}
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/ten_days/done2.py > runs/ten_days/done2.stdout.txt 2>&1
exit 0; answers from cache/v20 (days 1-2, nights 1-2, minds 1-2): 143; sent to the recorded client: 133; v20's recorded answers used: 133 of 141
  day3: 40 asks; recorded 40; not recorded []
  night3: 8 asks; recorded 8; not recorded []
  mind3: 0 asks; recorded 0; not recorded []
  day4: 48 asks; recorded 48; not recorded []
  night4: 9 asks; recorded 9; not recorded []
  mind4: 0 asks; recorded 0; not recorded []
  day5: 28 asks; recorded 28; not recorded []
  night2 groups: [(['daniel'], False, 'clean', 0, 0)]
  night3 groups: [(['daniel'], True, 'clean', 0, 0)]
  night4 groups: [(['daniel'], True, 'clean', 4, 4)]
(each one's day-4 and day-5 positions lines follow in the file; Leo's day 4: §2)
```
- **The 143 from the cache** are v16's 135 and the night minds' 8. Their prompts are unchanged, so they are exact
  hits.
- **Altogether,** all 141 of v20's answers from day 3 on were used.

### 4.3 DONE 3
```
$ time env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/ten_days/done3.py > runs/ten_days/done3.stdout.txt 2>&1
real	0m14.826s
exit 0
(the tables of §3)
```

### 4.4 DONE 4: v16 through night 2, HEAD's code against the new (`runs/facts_evening/prefix.py`)
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/facts_evening/prefix.py "$S/head361" "$S/fe/prefix_td_head" 2 3 > runs/ten_days/prefix_head.stdout.txt
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/facts_evening/prefix.py . "$S/fe/prefix_td" 2 3 > runs/ten_days/prefix.stdout.txt
daniel_ate_it-seed2: through night 2 and mind 2: 96 answers from the cache, 0 live
daniel_ate_it-seed3: through night 2 and mind 2: 135 answers from the cache, 0 live
daniel_ate_it-seed2.md: HEAD vs after: IDENTICAL
daniel_ate_it-seed2.transcript.json: HEAD vs after: IDENTICAL
daniel_ate_it-seed3.md: HEAD vs after: IDENTICAL
daniel_ate_it-seed3.transcript.json: HEAD vs after: IDENTICAL
```

### 4.5 The frozen versions, and the caches
```
$ for v in v14 v13 v12 v11 v10 v9; do env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done > runs/ten_days/frozen.stdout.txt 2>&1
frozen IDENTICAL: 18; exits 0: 6
$ sha256sum -c "$S/fe/caches.sha"      # cache/v16 seeds 1-3, cache/v19 seeds 2-3: 5 OK
$ sha256sum -c runs/v20/cache_copy.sha256.txt     # cache/v16 seeds 2, 3: OK
```
`cache/v20`'s files were last written at the end of seed 3's run (10:14 UTC) and hold 281 and 325 entries, as in
`reports/days_v20.md`. The scripts above read temp copies.

### 4.6 The full suite (`runs/ten_days/unittest.stdout.txt`), on the final files
```
$ ( time env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" ) > runs/ten_days/unittest.stdout.txt 2>&1
Ran 257 tests
OK
exit 0
```
257 tests: the 255 of `reports/household_knowledge.md`, plus the 2 new ones.

### 4.7 The commit
One commit holds:
- the v20 run: `runs/v20`, `cache/v20`, `reports/days_v20_plan.md`, `reports/days_v20.md`;
- this change: `night.py`, `quiet.py`, `world.py`, `story.py`, `test_morning.py`;
- this report, and `runs/ten_days/`.

`runs/v6/*.replay.md` stays untracked. Nothing is pushed.
