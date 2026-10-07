# Runs past day 3, the night's own minute, and Q2 once per pair per day

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, and days 3 to 5 were answered by
fake clients. No cache was written: `cache/v16` and `cache/v18` were read through temp copies, and `cache/v18`'s
sha256s are unchanged (§5.4). Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\df4e0891-227a-421a-8e99-2ece5be8c3a7\scratchpad`.

The three changes:
1. **`morning.py --days N`** (default 3, as before). Days 3 to N are quiet days. Each but the last is followed by its
   night and night mind, and the run ends at day N's bedtime.
2. **The night's own minute.** After a quiet day, the night's answers keep 21:00 (minute 840), not 90. So every
   minute of the day is the day's: an afternoon act carried into the next day reads "yesterday". A night event is
   written as "tonight" or "last night", never as a clock time.
3. **Q2 fires at most once per pair per day.**

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The tests for 1 to 3 fail before and pass after | **PASS** | §3. Before: 2 errors and 2 failures, then a fifth failure for the suspicion line. One guard passed (default run stops at day 3). After: all pass. |
| 2 | A fake-client run with `--days 5` from v16 seed 2 reaches day 5's bedtime and exits 0. No day-4/5 prompt calls a day-3 afternoon act "last night". No night event shows a clock time. | **PASS** | §4. Exit 0, and day 5's last span ends at 21:00. In 80 day-4/5 prompts, 0 lines put a minute after a night word. Every day-3 afternoon anger still held on day 4 reads "yesterday at …" with its clock. 99 tagged grudge events, 0 with a scene that does not match their minute. The only "21:00" outside a span's end is in 10 day records (D3, D4) of spans that ended at bedtime. |
| 3 | A no-API replay of v18 from a copy of `cache/v18` matches `runs/v18` up to the first Q2 change 3 removes; v16 through night 2 and v9–v14 IDENTICAL; the full suite passes | **PASS** | Removed Q2s: **seed 1 at 13:00**, **seed 2 at 12:18**, **seed 3 at 12:48**. Before each: played turns, Q1/Q2 checks and spans begun all equal `runs/v18`'s (§5.1). v16: byte-identical to HEAD, 3 of 3. Frozen: 18 of 18. Suite: `Ran 236 tests`, `OK`. |

## 1. The change

| File | Change |
|---|---|
| `morning.py` | `run(…, days=3)` (`morning.py:100`). After day 3, for each k from 4 to `days`: scenes `night{k-1}`, `mind{k-1}` and `day{k}` (`morning.py:217`). The story appends each night, mind and day. The transcript gains `night{k-1}`, `mind{k-1}` and `day{k}`, before `chronicle`. The meta gains `days`, `night{k-1}`, `mind{k-1}`, `day{k}` and `day{k}_quiet` (`later_meta`, `morning.py:348`); none of these for a 3-day run. `--days` (`morning.py:375`; below 3 is refused). The module docstring, which is `--help`'s text, describes it. |
| `world.py` | `Morning.night_minute()` (`world.py:456`): 90 after days 1 and 2, 21:00 (840) after a quiet day. `night_from()` (`world.py:463`): that minute on a quiet day, else None. `grudge_facts` takes `night_from` (`world.py:244`): on a quiet day an anger at or after it is "tonight", never a minute (`world.py:258`, `world.py:266`). The suspicion line does the same (`world.py:924`). |
| `night.py` | The night's answers keep `self.m.night_minute()` (`night.py:211`). `tag_events` and the suspicion split at the next morning use the night minute of the day that ended (`night.py:780`, `night.py:788`, `night.py:794`, `night.py:838`). |
| `quiet.py` | `q2_met` (`quiet.py:157`): each pair's first Q2 minute that day. A later meeting gives "they met this way at 11:20 already today" (`quiet.py:385`, `quiet.py:402`). `Q2_EVERY` is gone. The log entry's `within_2h` is now `met_today`. |
| `story.py` | The grudge facts at a day's end pass `night_from` (`story.py:365`). |
| `test_morning.py` | 4 new tests and 2 changed ones (§3). |

**Choices, and why:**
- **21:00, not another number, for a quiet day's night.** On days 1 and 2 the night's minute, 90, already comes after
  every minute of the day. 21:00 keeps that: it is bedtime, after every played minute, and the gap before a fall
  (`FALL_EVERY`) counts forward from the day's last change. With 90, a grudge that last changed after 08:30 could not
  fall that night, because the gap from its last change was negative.
- **Night events as "tonight" and "last night", never as minutes.** That is what `grudge_facts` already did for
  nights 1 and 2 once they were tagged (`when_words`). On days 1 and 2 the untagged night anger still reads "at
  minutes 51, 57, 63 and 90" (v15/v16's mind 1). It is kept so their prompts do not change: `night_from` is None
  there.
- **The last day has no night.** "Through day N", like today's run ending at day 3.
- **Once per pair per day** replaces "once in 2 hours". `q2_met` lives on the day's `Quiet`, so each day starts
  empty.

**Seen, not changed:**
- **The chronicle's G event before a night still has minute 90** (`chronicle.py:215`), and so does its N events'
  minute (`chronicle.py:226`). No prompt writes them with a minute: records write night events as "tonight: …".
- **Afternoon headings and lines still say "this morning"**, as before: for example the suspicion line "you
  thought Daniel took it, this morning at 17:00, and tonight".

## 2. Day-4 block A, from the fake run (§4)

Leo's first day-4 prompt (`runs/multiday_fake/prompts.json`, scene `day4`), lines 29–41. The day-3 times are the
fake client's.
```
Yesterday and last night:
- Yesterday morning the shelf held 0 portions.
- Accusations: you accused Daniel; Mara accused Daniel.
- Confrontations: you confronted Elena twice; Mara confronted you.
- About going to the neighbour's house last night, where it was left: Mara offered to go (10:21); you said nobody should go (20:27); Daniel said you are the one who should go (20:30).
- After the morning: you lay on your bed in the brothers room (min 12 to 09:36); you sat in the kitchen with Elena (09:36 to 11:36); you lay on your bed in the brothers room (11:36 to 11:42); you sat in the kitchen with Daniel (11:57 to 13:42); you lay on your bed in the brothers room (13:42 to 15:45); you sat in the kitchen with Daniel, Elena and Mara (15:45 to 21:00). Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
- In the night Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).
- You went with him.
- You got inside the neighbour's house and found no food there. Nothing troubled you in the street.
- You came back in by the front door before dawn.
- In the night you heard the front door being opened. You did not see who.
- Before dawn you heard the front door again. You did not see who.
```
- **The same prompt's grudge line** keeps day 3's afternoon apart from the night: "Against Daniel (a little): … you
  were angry with Daniel the night before last; and yesterday at 10:24 and 11:51; and last night."
- **Mara's block A** dates both of day 3's lists by the clock: "Accusations: you accused Daniel (20:24)." and
  "Confrontations: Leo confronted Elena twice (10:21, 10:24); you confronted Leo (10:24)."

## 3. The tests

| Fix | Test | What it holds |
|---|---|---|
| 1 | `test_a_run_goes_on_to_day_5` | `run(days=5)` from v16 seed 2 with `HushFake`. Exit 0. The transcript has day3, night3, mind3, day4, night4, mind4, day5 and no night5. Each quiet day's last span ends at 21:00, and its day asks are ≤ 40. `meta["days"] == 5`. The story has the titles of days 6, 7, 8 and nights 3, 4, in order. |
| 1 | `test_a_run_stops_after_day_3_by_default` | Without `days`, the transcript's keys are exactly today's, and the meta has no `days`. A guard: it passed before too. |
| 2 | `test_a_day_3_afternoon_act_is_yesterday_and_a_night_event_has_no_clock` | Leo's day-3 anger at 17:00, a suspicion at 17:00 and a guilt event of Daniel's at 17:00 are added. On night 3, the night's angry answers keep minute ≥ 840. During the night his line reads "… 17:00; and tonight", with no 08:30 or 21:. On day 4: "yesterday at … 17:00; and last night", no "last night at", no 21:00. The 17:00 events are tagged ("D", 3), the night's ("N", 3); likewise the suspicion and the guilt event. `night_minute()` is 840 on day 3 and 90 on day 2. |
| 2 | `test_a_night_suspicion_is_tonight_not_a_clock` | On a quiet day's night, suspicions at 17:00 and 21:00 read "this morning at 17:00, and tonight". |
| 3 | `test_q2_once_per_pair_per_day` (was `test_q2_once_per_pair_in_2_hours`) | After a Q2 at 11:20, the same pair's arrivals at 13:17, 13:20 and 18:40 fire nothing: "they met this way at 11:20 already today". |
| 3 | `test_every_q2_of_the_day_came_after_an_hour_apart` (changed) | On a played day, `fired` holds exactly when an hour apart, not `met_today`, and not over budget; and no pair fires twice. |

**RED, before any production change** (`$S/multi_red.txt`, then `$S/multi_red2.txt`):
```
ERROR: test_a_run_goes_on_to_day_5
TypeError: run() got an unexpected keyword argument 'days'
ERROR: test_every_q2_of_the_day_came_after_an_hour_apart
KeyError: 'met_today'
FAIL: test_a_day_3_afternoon_act_is_yesterday_and_a_night_event_has_no_clock
AssertionError: [] is not true : the night's answers keep a minute after the day
FAIL: test_q2_once_per_pair_per_day
AssertionError: Lists differ: [0, 1, 1] != [0, 0, 0]
Ran 5 tests in 1.866s
FAILED (failures=2, errors=2)
FAIL: test_a_night_suspicion_is_tonight_not_a_clock
AssertionError: 'you thought Daniel took it, this morning at 17:00, and tonight' not found in 'About the can (some): you thought Daniel took it, this morning at 17:00 and 21:00.'
FAILED (failures=1)
```
The guard `test_a_run_stops_after_day_3_by_default` passed in that run.

**Corrections to the tests, before they first passed:**
- **Reordering.** The first RED run failed two tests on names not yet written (`night_minute`, `met_today`). The
  checks were moved so that each fails on behaviour first.
- **The meta key.** The day-5 test read `meta[k]["asks"]`; a day's asks are `meta[f"{k}_quiet"]["day_asks"]`, as
  for day 3.
- **The minute.** The Q2 test expected "10:20", but minute 260 is 11:20.

**GREEN:**
```
$ T=test_morning.QuietDayTest; env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest $T.test_a_run_goes_on_to_day_5 $T.test_a_run_stops_after_day_3_by_default $T.test_a_day_3_afternoon_act_is_yesterday_and_a_night_event_has_no_clock $T.test_a_night_suspicion_is_tonight_not_a_clock $T.test_q2_once_per_pair_per_day $T.test_every_q2_of_the_day_came_after_an_hour_apart < /dev/null
Ran 6 tests in 4.967s
OK
```
The first GREEN attempt failed with `KeyError: -1` in `later_meta`: my list of extra days reused the name `later`,
which `run()` already uses for the scene counts. It was renamed `more_days`.

## 4. DONE 2: the fake run to day 5 (`runs/multiday_fake/fake_run.py`)

`morning.run(2, days=5)`: days 1–2 and nights 1–2 come from a temp copy of `cache/v16`; day 3 on comes from
`gemini.FakeClient` (`invalid_every=0`). Every prompt is kept with its scene (`runs/multiday_fake/prompts.json`); the
run itself is in `runs/multiday_fake/run/`. The "API requests" in its log are the fake client's.
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/multiday_fake/fake_run.py > runs/multiday_fake/fake_run.stdout.txt
  api_requests: 134   answers_live: 134   answers_from_cache: 96
  day3 day_asks: 34 … night3 asks: 8; mind3 asks: 4; mind3 memories kept 4 … (day 4 and 5 lines in the file)
exit code 0
prompts sent to the fake client, by scene: {'day3': 34, 'night3': 8, 'mind3': 4, 'day4': 40, 'night4': 4, 'mind4': 4, 'day5': 40}
days in the transcript: ['day1', 'day2', 'day3', 'day4', 'day5']; day 5's last span ends at 21:00; meta days 5
day-3 model acts from 08:30 on naming someone as angry_at: 14
day-4 and day-5 prompts: 80; lines with a night word followed by 'at' (a minute): 0
  Elena -> Mara, last afternoon anger 20:24: day-4 line has 'yesterday at … 20:24': True
  Leo -> Daniel, last afternoon anger 11:51: day-4 line has 'yesterday at … 11:51': True
  Daniel -> Leo, last afternoon anger 11:39: day-4 line has 'yesterday at … 11:39': True
  Mara -> Elena, last afternoon anger 11:36: day-4 line has 'yesterday at … 11:36': True
  Leo -> Elena, last afternoon anger 10:21: day-4 line has 'yesterday at … 10:21': True
  (5 more pairs: "no such line (no grudge held at 07:00)": the grudge had fallen to 0 by day 4)
prompts from night 3 to day 5: 100; lines with 21:00 outside a span's end: 10; days with a played turn at 08:30: []; lines with 08:30: 0
tagged grudge events at the end of day 5: 99; with a scene that does not match their minute: 0
minutes by scene, days and nights 3-4: D3: 0..807 (21); D4: 3..237 (19); N3: 840..840 (6); N4: 840..840 (2)
```
- **The 10 "21:00" lines** are all mind-3 and mind-4 records of day events (`runs/multiday_fake/stray_2100.txt`). For
  example, "[D3-058] 21:00: Daniel was sitting in the kitchen at 21:00." is a span that ended at bedtime, recorded
  for a witness who saw only its end (`reports/quiet_day_fixes.md`, fix 4). None is a night event.
- **No night event has a clock.** The N3 and N4 events carry 840 internally and are written "tonight" or "last
  night".

## 5. Commands and raw output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. Every result below is from the final code.

### 5.1 DONE 3: v18 from a copy of `cache/v18` (`$S/replay_v18.py`)

The replay plays days 1–2, nights 1–2 and both minds from a temp copy, then day 3 until bedtime or a miss. It finds
v18's first Q2 that fired for a pair that had already fired that day, and compares everything before that minute.
```
$ sha256sum cache/v18/*.json > $S/v18cache.sha
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/replay_v18.py "$PWD"
daniel_ate_it-seed1: v18's first repeated Q2 is at 13:00 (leo into the brothers_room, where daniel is; the pair ['daniel', 'leo'] had fired earlier); replay played to bedtime, 0 live
  before 13:00: played turns 11 (v18 11), equal: True; Q1/Q2 checks 5 (v18 5), equal but for the rule's fields: True, why equal: True; spans begun 17, equal: True
  at 13:00: now [(False, 'they met this way at 11:00 already today')]; in v18 fired True
daniel_ate_it-seed2: v18's first repeated Q2 is at 12:18 (daniel into the brothers_room, where leo is; the pair ['daniel', 'leo'] had fired earlier); replay stopped at a cache miss (after 124 cached answers), 0 live
  before 12:18: played turns 7 (v18 7), equal: True; Q1/Q2 checks 4 (v18 4), equal but for the rule's fields: True, why equal: True; spans begun 18, equal: True
  at 12:18: now [(False, 'they met this way at 10:18 already today')]; in v18 fired True
daniel_ate_it-seed3: v18's first repeated Q2 is at 12:48 (daniel into the brothers_room, where leo is; the pair ['daniel', 'leo'] had fired earlier); replay played to bedtime, 0 live
  before 12:48: played turns 8 (v18 8), equal: True; Q1/Q2 checks 3 (v18 3), equal but for the rule's fields: True, why equal: True; spans begun 14, equal: True
  at 12:48: now [(False, 'they met this way at 10:48 already today')]; in v18 fired True
```
- **"The rule's fields"** are `within_2h` (v18) and `met_today` (now). They are compared apart: the `why` lines before
  each minute are equal too.
- **Seed 2's miss** comes after 12:18, where the day has already left v18's path.

### 5.2 v16 through night 2, and the frozen versions
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/replay_prefix.py" "$PWD" "$S/after_multi"
daniel_ate_it-seed1: 98 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: DIFFERS
daniel_ate_it-seed2: 96 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: IDENTICAL
daniel_ate_it-seed3: 135 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: IDENTICAL
exit 0
$ for f in daniel_ate_it-seed{1,2,3}; do for x in md transcript.json; do cmp -s "$S/before/$f.$x" "$S/after_multi/$f.$x" && echo "$f.$x: before (HEAD) vs after: IDENTICAL" || echo "$f.$x: DIFFERS"; done; done
(all six: IDENTICAL)
$ for v in v14 v13 v12 v11 v10 v9; do env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done > $S/multi_frozen.txt
frozen IDENTICAL: 18; exits: 6
```
- **Seed 1's "DIFFERS"** against the original is the two S4/S8 verdict lines already at HEAD
  (`reports/quiet_day_fixes.md` §6.1). `$S/before` is the HEAD replay.

### 5.3 The `--days` flag
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --help | grep -A1 -- --days
  --days DAYS           the last day to play (3 to N, each a quiet day)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 2 --fake --days 2; echo "exit $?"
morning.py: error: --days must be 3 or more
exit 2
```

### 5.4 The full suite, and the cache
```
$ ( time env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" ) > $S/multi_full.txt 2>&1
Ran 236 tests in 162.397s
OK
real	2m43.584s
exit 0
$ sha256sum -c $S/v18cache.sha            # seed1, seed2, seed3: OK
```
- **236 tests:** 232 before, plus the 4 new ones. The 2 changed ones replace their old forms.
- **Changes after the suite:** the module docstring of `morning.py` gained the `--days` lines, which are `--help`'s
  text. The two run tests were rerun after that: `OK`.
