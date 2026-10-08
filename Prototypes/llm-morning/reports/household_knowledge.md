# Household knowledge: a night trip is the whole house's by morning, and far offers read as offers on every day

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset. `cache/v16` and `cache/v19` were
read through temp copies only; their sha256s are unchanged (§4.4). Paths are relative to `Prototypes/llm-morning/`.
Raw outputs are in `runs/household/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\ba344a5c-5509-4487-aefe-3209becb4468\scratchpad\fe`.

From `reports/facts_and_evening.md` §1–§2. Elena was told "as far as you know, nobody has gone out", while her
children accused Daniel of going out in front of her and she had heard the door twice. In a house of four, who went
out and what came home cannot stay secret past breakfast. What happened out there can.

1. **From the morning after a trip, everyone in the house knows** who went, where, which night, and what could be seen:
   came back with nothing, came back with food, or has not come back. The outings line, the neighbour's-house line,
   the street line and knowing next door is empty follow from that. A scare, and what a house held beyond what came
   home, stay with whoever went.
2. **Far offers read as offers on every day,** not only on quiet days.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The tests fail before and pass after | **PASS** | 2 new tests. Before (the code of `reports/facts_and_evening.md`): 2 failures, each on the missing behaviour (§4.1). After: pass. |
| 2 | v19 seed 3 rebuilt, no API: on day 4 Elena's outings line lists both of Daniel's trips, she knows next door is empty, and she is offered the far options | **PASS** | Her day-4 outings line lists both trips. Her neighbour's-house line says Daniel came back with nothing. All 12 of her day-4 prompts offer `propose_far` and `volunteer_far`, which only someone who knows next door is empty is offered (`world.py:639`). Her night-4 bedtime offers `go_further` (§2). |
| 3 | v16 seeds 2 and 3 replay through night 2 as at HEAD; v9 to v14 IDENTICAL; the full suite passes | **PASS** | Story and transcripts through mind 2 are byte-identical between HEAD's code and the new code, both seeds. Frozen: 18 of 18 IDENTICAL. Suite: `Ran 255 tests`, `OK` (§4.3–§4.5). |
| 4 | git status shows nothing modified and only the runs/v6 replay files untracked | **PASS** | §4.6. |

## 1. The change

| File | Change |
|---|---|
| `night.py` | **Who went is the house's.** `trips_known` (`night.py:181`) lists every trip of the nights so far, for everyone; it no longer reads `night.knows`. `heard_trip` (`night.py:1048`), behind the neighbour's-house line and `knows_next_door_empty` (`night.py:143`), takes the latest trip next door by anyone else. **What could be seen:** `seen_outcome` (`night.py:194`): "came back with food", "came back with nothing", "has not come back", or "came back with …; X has not come back" for a group that lost one. It does not say whether they got inside, were scared, or what the house held. **The street line** (`night.py:212`), each far trip oldest first: their own, as before ("you searched one house … and it held no food", "you went along it … but did not get inside any house further along"); another's, by `seen_outcome` ("Daniel went further along it last night and came back with nothing"). **The outings line** (`night.py:245`) gives another's trip by `seen_outcome`. It no longer reads who is away now, so an earlier trip of someone lost later does not read "has not come back". **Someone not back:** `p.missing` also keeps where they went (`night.py:1106`). For whoever only found them gone, the opening no longer says "and you do not know where he went" (`night.py:178`). |
| `world.py` | **Fix 2:** `FAR_GIST` on every day (`world.py:1517`). **Not back:** the "About X:" line of whoever only found them gone reads "About Daniel: he went further along the street last night and has not come back." (`world.py:727-738`). |
| `test_morning.py` | 2 new tests; 6 existing tests changed (§3). |

**Choices, and why:**
- **What the house knows by morning is the trip, not what happened out there.**
  - Someone who saw Daniel come back empty-handed does not know whether he got inside or was scared off. So they are
    no longer told "Daniel searched one house further along it last night, and it held no food". Fix 2 of
    `reports/facts_and_evening.md` gave that to anyone who knew of the trip; now only Daniel has it. The others have
    "Daniel went further along it last night and came back with nothing".
  - Food that came home is seen as food, not as an amount: what the house held stays with Daniel.
- **"Came back with nothing" still makes them know next door is empty,** as `reports/stage_b_fixes.md` fix 1 set it
  for those who saw it. Now that holds for the whole house.
- **The night's own lines are unchanged.** Block A ("Yesterday and last night") still holds only what each one
  noticed: T9 still checks that someone who slept has no night line about Daniel.
  - The morning opening at min 00 still says how each found it ("In the night you heard the front door", "you saw him
    go out"). It only loses "you do not know where he went", which the house knows by then.
  - The night mind, its checks, Q2 and Q5 are not touched.
- **Elena's lines would also follow for a trip on night 1.** No such trip occurs in v16 seeds 2 and 3, so their days 1
  and 2 are unchanged (DONE 3). In v16 seed 1 (Daniel next door on night 1), everyone already knew by day 2
  (`reports/stage_b_fixes.md`).
- **`runs/facts_evening/` and `reports/facts_and_evening.md` are committed as they were written.** Their DONE 2 lines
  for Elena ("as far as you know, nobody has gone out") and Leo's and Mara's street lines ("Daniel searched one house
  …") are the previous rule's, and are superseded by §2 below.

## 2. DONE 2: Elena's day 4, v19 seed 3 on the new code (`runs/household/done2.py`)

**How it runs:**
- As `runs/facts_evening/done2.py`: days 1–2, nights 1–2 and minds 1–2 come from a temp copy of `cache/v19` (135
  answers). From day 3 on, v19's own recorded answers are used.
- At night, a recorded answer now matches when all its recorded options are still offered: Elena's bedtimes now also
  offer `go_further`.
- All 132 recorded answers were used. The only asks with no recorded answer are Q5's at 19:00 (10), answered
  `silent`.
- The nights come out as in v19: night 2, Daniel next door, back with nothing; night 3, Daniel further along, clean,
  house 1 held 0. Elena chose `lie_awake` on night 3, as in v19.

Elena's day-4 lines (`runs/household/done2.stdout.txt`):
```
Elena's day-4 prompts: 12
  About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
  About the street: Daniel went further along it last night and came back with nothing; nobody knows what is left in the houses further along, and they are further and more dangerous than next door.
  About going out at night: Daniel went to the neighbour's house the night before last and came back with nothing; Daniel went further along the street last night and came back with nothing.
  ... Outside, and not to be gone to this morning: the street, the neighbour's house and the houses further along the street. Do not mention any other object or place.
  with propose_far and volunteer_far offered: 12 of 12
  - propose_far: (speech) say someone should try the houses further along the street tonight
  - volunteer_far: (speech) offer to go further along the street tonight yourself
  her night-4 bedtime offers go_further: [True]
```
In v19 her day-4 neighbour's-house line was "its people left in the first days, so there may be food there", and she
was offered none of these.

## 3. The tests

**New** (`test_morning.QuietDayTest`):
| Fix | Test | What it holds |
|---|---|---|
| 1 | `test_a_trip_is_known_to_the_whole_house_by_the_next_morning` | **Day 3 of v16 seed 2.** Elena slept through night 2, but she knows next door is empty: her neighbour's-house line is "Daniel went there last night and came back with nothing.", her outings line names the trip, and her prompt has `propose_far`, `volunteer_far` and the street line. **Night 3, Daniel further along, house 0 holds 0.** Elena (not in `n3.knows`), Leo and Mara all have both trips in their outings line. They know next door is empty, and their street line is "Daniel went further along it last night and came back with nothing; …". Elena's day-4 prompt offers `volunteer_far`. Daniel's own line still says the house he searched held no food. **Food:** house 0 holds 4. Elena's lines say "came back with food", never what the house held; Daniel's says "it held 4 portions, all brought back". **Scared off before the door:** Leo's street line is the same "came back with nothing"; Daniel's is "you went along it last night but did not get inside any house further along; …". **Not back:** Mara slept through it. Her opening has no "you do not know where he went"; her "About Daniel:" line is "he went further along the street last night and has not come back"; her outings line has night 2 "came back with nothing" and night 3 "has not come back". |
| 2 | `test_far_offers_read_as_offers_on_every_day` | `line_text` of `volunteer_far` and `propose_far` on days 1, 2 and 3 of v16 seed 2 gives "Daniel offers to go further along the street tonight" and "Daniel says someone should try the houses further along the street tonight". |

**Existing tests changed,** each because fix 1 overturns its expectation that only who saw or heard a trip knows of it:
- **`NightTest.test_t9_nobody_is_told_what_they_did_not_notice`.**
  - Unchanged: block A still has no night line about Daniel for those who slept.
  - Changed: their neighbour's-house line is now "Daniel went there last night and came back with nothing", not
    "its people left in the first days, so there may be food there".
- **`NightTest.test_t10_someone_not_back_is_away`.** Leo's opening loses "and you do not know where he went".
- **`QuietDayTest.test_w5_is_offered_once_someone_knows_next_door_is_empty`.**
  - On day 3 all four know next door is empty; Elena's night-3 bedtime offers `go_further`.
  - The prompt without W5 is now Elena's on day 2, when nobody knows.
- **`QuietDayTest.test_w5_is_known_from_a_neighbour_line_that_came_back_with_nothing`.** Elena's line too says "came
  back with nothing"; all four know, and all four bedtimes offer `go_further`.
- **`QuietDayTest.test_someone_who_does_not_come_back_is_gone_and_each_knows_it_their_way`.** Mara's opening and her
  "About Daniel:" line, as in the new test. Leo's ("you saw him go out") and Elena's ("you heard the front door") are
  unchanged.
- **`QuietDayTest.test_every_quiet_prompt_carries_the_outings_line`.** Elena's line on day 3 is the trip; on day 4,
  both trips.
- **`QuietDayTest.test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it`.** Elena, Leo and Mara get
  the seen line; Daniel's is unchanged. After a scare, Leo's is the seen line, not `STREET_UNSEARCHED`.

**On the way, one bug in my first change.** The new test's last part failed on the first run after the change:
- **The cause.** The outings line read "has not come back" from who is away now, so Daniel's night-2 trip read
  "Daniel went to the neighbour's house the night before last and has not come back".
- **The fix.** It now uses each trip's own outcome (`seen_outcome`), and the unused `away` argument is gone.

## 4. Commands and raw output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset.

### 4.1 RED (`runs/household/red.stdout.txt`), on the code of `reports/facts_and_evening.md`
```
$ T=test_morning.QuietDayTest; env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest $T.test_a_trip_is_known_to_the_whole_house_by_the_next_morning $T.test_far_offers_read_as_offers_on_every_day < /dev/null > runs/household/red.stdout.txt 2>&1
exit 1
FAIL: test_a_trip_is_known_to_the_whole_house_by_the_next_morning
AssertionError: {'daniel': True, 'elena': False, 'leo': True, 'mara': True} != {'daniel': True, 'elena': True, 'leo': True, 'mara': True}
FAIL: test_far_offers_read_as_offers_on_every_day
AssertionError: 'Daniel says to everyone: "I\'ll go."' != 'Daniel offers to go further along the street tonight: "I\'ll go."'
Ran 2 tests in 0.343s
FAILED (failures=2)
```
- **GREEN:** the same two tests, `Ran 2 tests`, `OK`.
- **The two classes they changed,** after the existing tests were updated:
  `-m unittest test_morning.QuietDayTest test_morning.NightTest`: `Ran 97 tests`, `OK`.
- **Since the RED run,** the two tests changed only by rewrapping four long lines.

### 4.2 DONE 2
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/household/done2.py > runs/household/done2.stdout.txt 2>&1
exit 0; answers from cache/v19 (days 1-2, nights 1-2, minds 1-2): 135; sent to the recorded client: 142; v19's recorded answers used: 132 of 132
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
  night3 bedtimes: {'daniel': 'go_further', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'}
(Elena's lines: §2)
```

### 4.3 DONE 3: v16 through night 2, HEAD's code against the new (`runs/facts_evening/prefix.py`)
`$S/head_code` holds HEAD's (`d7b3e78`) `*.py` and `config.json`, each checked equal to `git show HEAD:…`;
`$S/prefix_head` is its output.
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/facts_evening/prefix.py . "$S/prefix_hk" 2 3 > runs/household/prefix.stdout.txt
daniel_ate_it-seed2: through night 2 and mind 2: 96 answers from the cache, 0 live
daniel_ate_it-seed3: through night 2 and mind 2: 135 answers from the cache, 0 live
$ for f in daniel_ate_it-seed{2,3}.{md,transcript.json}; do cmp -s "$S/prefix_head/$f" "$S/prefix_hk/$f" && echo "$f: HEAD vs after: IDENTICAL"; done
daniel_ate_it-seed2.md: HEAD vs after: IDENTICAL
daniel_ate_it-seed2.transcript.json: HEAD vs after: IDENTICAL
daniel_ate_it-seed3.md: HEAD vs after: IDENTICAL
daniel_ate_it-seed3.transcript.json: HEAD vs after: IDENTICAL
```

### 4.4 The frozen versions, and the caches
```
$ for v in v14 v13 v12 v11 v10 v9; do env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done > runs/household/frozen.stdout.txt 2>&1
frozen IDENTICAL: 18; exits 0: 6
$ sha256sum -c "$S/caches.sha"          # cache/v16 (3) and cache/v19 (2): 5 OK
```

### 4.5 The full suite (`runs/household/unittest.stdout.txt`), on the final files
```
$ ( time env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" ) > runs/household/unittest.stdout.txt 2>&1
Ran 255 tests in 229.036s
OK
real	3m50.400s
exit 0
```
255 tests: the 253 of `reports/facts_and_evening.md`, plus the 2 new ones.

### 4.6 The commit
One commit holds:
- the code and tests of `reports/facts_and_evening.md` and of this change: `world.py`, `night.py`, `quiet.py`,
  `morning.py`, `story.py`, `test_morning.py`;
- both reports;
- `runs/facts_evening/` and `runs/household/`.

`runs/v6/*.replay.md` stays untracked. Nothing is pushed. The commit line and `git status` are in the reply that
delivered this report.
