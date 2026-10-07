# Stage B: further along the street, weakness on the street, dozing on watch

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, and the nights and days past
night 2 were answered by fake clients. No cache was written: `cache/v16` was read through temp copies, and its
sha256s are unchanged (§6.3). Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\df4e0891-227a-421a-8e99-2ece5be8c3a7\scratchpad`.

Built from `reports/quiet_day_design.md` §5 (W2, W5) and §1.2 (the doze draw), with the brief's amendments:
1. **W5 for whoever knows next door is empty:** a bedtime choice, two day trip options, a fact line, and the
   houses further along in their house line.
2. **Each further house's food is drawn once, when first entered:** 45% none, 30% 2, 18% 4, 7% 6. A searched house
   is empty afterwards, and the next trip reaches the next house.
3. **W2's weakness shifts** on the near and the far street tables, and the doze draw for exhausted watchers.
4. **Someone who does not come back** is not asked and in no room from then on. Each person's prompts say what they
   know of it.
5. **From minute 90 on a quiet day, and at its night,** a grudge line says "today at", not "this morning at".

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The tests for 1 to 5 fail before and pass after | **PASS** | §3. Before: 4 errors and 2 failures, each on the missing behaviour. After: all pass. |
| 2 | A fake `--days 5` run where a far trip brings food back: the next morning the shelf holds those portions, and eat options appear | **PASS** | Night 3: Daniel goes further along alone; street clean; the first house holds 4; he takes 4. Shelf 0 → 4. Day 4's opening: "this morning it holds 4 portions". `eat` is offered in 11 of 30 day-4 prompts; Mara eats at min 06, Elena shares at 11:00 (minute 240). Exit 0, day 5 to bedtime (§4.1). |
| 3 | A fake `--days 5` run that forces a far trip not to come back reaches day 5's bedtime with exit 0, and the missing person is never asked after that night | **PASS** | Night 3: Daniel goes further along alone and is lost. Exit 0. Day 5's last span ends at 21:00. Prompts to Daniel after he went out (mind 3 to day 5): **0**. On days 4 and 5 he has 0 acts, is in 0 rooms, and has no needs log or spans. Night 4 and mind 4 ask only Elena and Mara (§4.2). |
| 4 | A no-API replay of v16 from a copy of `cache/v16` matches `runs/v16` up to the first prompt where someone knows next door is empty; v9 to v14 IDENTICAL; the full suite passes | **PASS** | The points per seed, below. Every scene before them equals `runs/v16`'s transcript (§6.1). Frozen: 18 of 18 (§6.2). Suite: `Ran 243 tests`, `OK` (§6.4). |

**DONE 4, the points.** In each seed only Daniel knows next door is empty: he got inside it and found 0 portions.

| Seed | He learned it | The first prompt with no cached answer | Matches `runs/v16` before it |
|---|---|---|---|
| 1 | night 1 | day 2, min 00, Daniel. It carries the street line, the far house line and both day options. | day 1, night 1, mind 1 |
| 2 | night 2 | day 3, min 00, Leo, asked before Daniel that turn. Every day-3 prompt misses v16's cache since stage A, because v16's day 3 was not a quiet day. | day 1 to mind 2 |
| 3 | night 2 | day 3, min 00, Daniel, with all three W5 additions. | day 1 to mind 2 |

## 1. The change

| File | Change |
|---|---|
| `night.py` | **W5:** `FAR`, `BEDTIME_FAR` (`night.py:67`), `FAR_HOUSE` (`night.py:71`), `STREET_UNSEARCHED` (`night.py:72`), `far_house_portions` (`night.py:96`). `Night.far` holds the houses drawn so far and how many were searched (`night.py:259`). It travels in `house_state()["far"]` from night to night. **The trip** (`night.py:641`): the next unsearched house, its food drawn by `far_house:<i>` when first entered, all of it taken, and the house counted searched. Its lines are `far_line` (`night.py:755`). **W2:** `SHIFTS` (`night.py:80`), `body_shift`, `group_shift`, `street_table`, `pick_street` (`night.py:101`–`123`). **The doze:** `doze_chance` (`night.py:132`), drawn at bedtime (`night.py:390`). A dozer is skipped at the roommate, door-watch, front-door and return checks (`night.py:447`, `477`, `502`, `733`). **Who knows, who is missing:** `knows_next_door_empty` (`night.py:139`), `how_known` (`night.py:144`), `missing_opening` (`night.py:158`), `street_line` (`night.py:171`). These are set in `next_day` (`night.py:1009`) and used in its opening line (`night.py:1072`). The neighbour's line counts only trips next door (`night.py:956`). |
| `world.py` | `Person.knows_empty` and `Person.missing` (`world.py:305`). `Morning.street` (`world.py:380`). `trip_options_day2` adds `propose_far` and `volunteer_far` for a knower (`world.py:635`). `named_to_go`, `heard_plan`, the speaker's own line and `trip_raised` know the two (`world.py:650`, `685`, `1682`). `missing_lines` writes the "About X:" lines (`world.py:717`). Amendment 5 is the `today` flag (`world.py:1042`). The knower's house line (`world.py:1054`). `KIND_DONE` names the two kinds (`world.py:105`). |
| `talk.py` | `propose_far` and `volunteer_far` join `SPEECH` and `TRIP_WHY` (`talk.py:10`, `talk.py:59`), so they are trip kinds. |
| `chronicle.py` | Gists for the far positions and a far `went_out` (`chronicle.py:50`). The neighbour's house is fixed only from trips next door. Each further house is fixed when first entered (`fixed["far_house_<i>"]`). |
| `memory.py` | Block C's standing line for someone gone says "has been gone since …" to whoever is not a witness of their going out (`memory.py:94`). |
| `story.py` | A group's street cut is written from its table when it has one, and a far group is named "further along the street (house N)" (`story.py:486`). |
| `test_morning.py` | 7 new tests, and 3 existing ones or helpers changed (§3). |

**Choices made, and why:**
- **"Knows next door is empty"** means they got inside it on some night and left nothing there (`found − took == 0`).
  - The code knows only what each one perceived. Someone who saw Daniel come back with nothing does not know he got
    inside: the night tells them nothing about it, and the code does not read words.
  - So in v16's seeds only Daniel gets W5. The others can still answer his far positions: `trip_raised` opens
    `nobody_goes`, and `named_to_go` opens `keep_daniel_home`.
- **A far trip takes everything it finds.** Amendment 2 says a searched house is empty afterwards. The neighbour's
  carry limit (3 a person) is not applied there.
- **The draws.**
  - A further house's food: `far_house:<i>`, one fact per seed, like `house`.
  - The far street: `trip_far:<leader>`, per night.
  - The doze: `doze:<who>`, per night.
- **The shift applies when every member has needs**, that is on a night after a quiet day. It applies to near trips
  too. Each body's stages are those set at the day's bedtime.
  - **Nights 1 and 2 have no needs:** they keep §4.2's tables and their exact draws.
  - **A group takes the shift of the member with the largest not_back shift, at half size.**
  - **Weak or very weak (fasting) and exhausted (debt) add up.**
- **The doze,** as §1.2 specifies:
  - It is for an exhausted (debt ≥ 24 at bedtime) `watch_door` or `lie_awake` choice.
  - A dozer counts as asleep: they wake for nothing, hear no voices, and see no return.
  - Their own line ends "You dozed off in the night, and woke by the door at dawn." or "You dozed off in the night."
- **What each one knows of a loss** (`how_known`), in order:
  - **with:** they were in the group;
  - **saw:** they saw the getting up or the front door, as roommate or door watcher;
  - **heard:** they heard the front door;
  - **gone:** none of these.
  The morning after says it in the opening line. Every later prompt has an "About X:" line, and later mornings say
  "X is still not here".
- **Kept as before only where no prompt shows them:** the night's records keep minute 90 internally
  (`reports/multiday.md`).
- **Amendment 5 is grudge lines only, as the brief says.** The suspicion line can still say "this morning at 17:00"
  on a quiet day's afternoon.
- **Seen, not changed:** `talk.act_of("go_further")` reads it as the `go` kind (prefix `go_`). Night choices never go
  through `apply`, so nothing uses that kind.

## 2. The first person offered W5: Daniel's bedtime prompt, night 3, the fake run

From `runs/stage_b_fake/food/first_w5_bedtime_prompt.txt`. The day-3 events in it are the fake client's. Lines
1–12 are quoted whole. Line 13 (conscience), the long house line and the middle are cut where marked.
```
You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).
How you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".
Who you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.
Temperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.
What matters to you: being in control, being respected, keeping the family safe.
Your body: starving, and weak from it: standing up makes your head spin; and you have hardly slept.
About the can: you ate it yourself, and you admitted it two days ago.
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
About the street: the houses further along it have not been searched; nobody knows what is left in them, and it is further and more dangerous than next door.
About going there tonight: you said Mara is the one who should go (min 06); Mara said you are the one who should go (min 06); Elena said Mara is the one who should go (10:42).
Against the others: nothing.
On your conscience (a lot): you ate the can in the night, and nobody saw; two days ago, you accused Leo of what you did, at minute 03; …
The house: … the front door and the front windows, boarded up. Outside: the street, the neighbour's house and the houses further along the street. Do not mention any other object or place.
… (the days before, earlier days, yesterday and last night, what yesterday left in him: lines 15–55 of the file)
What you are sure of from today:
- min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
Your own last words today:
- min 00, you said.
- min 06, you said Mara is the one who should go.
What else happened today, most recent last:
- (earlier things, left out here)
- 10:48: Elena comes into the kitchen.
- 10:48: Leo comes into the kitchen.
- 11:48: Elena goes to the back room.
- 11:57: Leo goes to the brothers room.
- 11:57: Mara goes to the back room.
- 12:42: you went to the brothers room.
- 12:42: you lay down on your bed.
- 15:39: you got up from your bed.
- 15:39: you went to the kitchen.
Now it is night. After the morning: you lay on your bed in the brothers room (min 33 to 10:42); you sat in the kitchen with Mara (10:48 to 12:42); you lay on your bed in the brothers room (12:42 to 15:39); you sat in the kitchen with Elena, Leo and Mara (15:39 to 21:00). Nobody ate.
Everyone has gone to bed in their own room: Daniel and Leo in the brothers room, Elena and Mara in the back room.
You are in the brothers room, in your bed. Leo is in his bed.
The kitchen is dark. The shelf holds 0 portions.
Your options:
- sleep: go to sleep
- lie_awake: lie awake in your bed and listen
- watch_door: sit up in the kitchen by the front door until morning, so nobody goes out without you knowing
- go_next_door: wait until the others are asleep, then go out by the front door to the neighbour's house
- go_further: wait until the others are asleep, then go out by the front door, past the neighbour's house, to the houses further along the street
```

## 3. The tests

| # | Test | What it holds |
|---|---|---|
| 1 | `test_w5_is_offered_once_someone_knows_next_door_is_empty` | v16 seed 2 on day 3: only Daniel `knows_empty`, and nobody on day 2. His 10:30 prompt has the street line, "the street, the neighbour's house and the houses further along the street", and `propose_far` and `volunteer_far`. Mara's has none of these. At night 3, his bedtime options end with `go_further` and his house line names the houses further along; Mara's has no `go_further`. |
| 2 | `test_far_houses_are_drawn_once_and_a_searched_house_is_empty` | The draw table at its edges. A clean far trip: house 0 holds 4, all 4 taken, the shelf +4, and `far` is `{houses: [4], us: [0.8], searched: 1}`. The next trip reaches house 1, drawn then (0 portions), and house 0 is not drawn again. Scared on the way there: no house searched. |
| 3 | `test_weakness_shifts_the_street_tables` | The near and far tables, weak, very weak, exhausted, and a group at half of its weakest. On night 3, Daniel's table is the one his bedtime needs give. The draw 0.6, clean on the plain table, is not clean on his. Night 2's groups have no table. |
| 3 | `test_an_exhausted_watcher_may_doze_and_then_notices_nothing` | `doze_chance` at 23.9, 24, 30 and 40 is 0, 0.3, 0.6 and 0.7. Elena at debt 30 watching the door with draw 0.5: dozes, notices nothing, and her line says so. With draw 0.65: awake, and she sees Daniel go. Not exhausted, with draw 0: no doze. |
| 4 | `test_someone_who_does_not_come_back_is_gone_and_each_knows_it_their_way` | Daniel goes further along alone and is lost. On day 4 he is in no room. The opening lines and the "About Daniel:" lines differ: Leo saw him go, Elena heard the door, Mara slept. Day 4 played: no decision of his, and no needs of his. |
| 5 | `test_grudge_lines_say_today_from_minute_90` | Leo's grudge line: "this morning at minute 60" at min 87; "today at minute 60" at min 90 and at night. |
| DONE 4 | `test_v16_seed_1_until_w5` (new); `test_v16_through_night_2_is_unchanged` (now seeds 2 and 3) | Seed 1's day 1, night 1 and mind 1 come from the cache. Its first miss is Daniel's day-2 min-00 prompt, with the street line. Seeds 2 and 3 through night 2 are as in v16. |

**Existing tests changed, and why:**
- **`NightTest.test_t10_someone_not_back_is_away`:** Leo slept through Daniel's going. His opening now reads "… his
  bed is empty and he is nowhere in the house, and you do not know where he went." (amendment 4).
- **`test_v16_through_night_2_is_unchanged`:** seed 1 now diverges at day 2, by DONE 4's own rule. It is held by the
  new `test_v16_seed_1_until_w5`.
- **`without_blocks`, the helper of `NightTest.test_t12_the_budget`:** it strips the trip block before measuring.
  It now also strips W5's lines: "About the street:", `propose_far` and `volunteer_far`, and the far places in the
  house line.
  - `prompt_parts` budgets those outside the 1450, as part of the trip block: in `trip_lines`, under `TRIP_KINDS`,
    and in the house line's extra length.
  - Without this, the test failed at 1490 (`$S/b_full1.txt`).

**RED, before any production change** (`$S/b_red.txt`):
```
ERROR: test_w5_is_offered_once_someone_knows_next_door_is_empty
AttributeError: 'Person' object has no attribute 'knows_empty'
ERROR: test_far_houses_are_drawn_once_and_a_searched_house_is_empty
AttributeError: module 'night' has no attribute 'far_house_portions'. Did you mean: 'house_portions'?
ERROR: test_weakness_shifts_the_street_tables
AttributeError: module 'night' has no attribute 'street_table'
ERROR: test_an_exhausted_watcher_may_doze_and_then_notices_nothing
AttributeError: module 'night' has no attribute 'doze_chance'
FAIL: test_someone_who_does_not_come_back_is_gone_and_each_knows_it_their_way
AssertionError: Items in the second set but not the first:          (n3.away: nobody was lost; go_further did not exist)
FAIL: test_grudge_lines_say_today_from_minute_90
AssertionError: 'today at minute 60' not found in 'Against Daniel (a lot): two days ago, …'
Ran 6 tests in 1.041s
FAILED (failures=2, errors=4)
```
**Corrections to the tests before they first passed:**
- **The weakness test** now computes Daniel's expected table from his own bedtime needs, not from numbers I had
  assumed.
- **The doze test** had a garbled assertion, rewritten as `assertNotIn("daniel", n3.knows["elena"])`.
- **The W5 test** expected a newline after `go_further`, the prompt's last line.

**The first full run after the change** (`$S/b_full1.txt`) failed on two causes, each fixed in code or helper above:
- 8 tests with `KeyError: 'propose_far'` in `pattern`: `KIND_DONE` lacked the two kinds;
- T12 at 1490.

## 4. DONE 2 and 3: the fake runs (`runs/stage_b_fake/fake_run.py`)

`morning.run(2, days=5)`: days 1–2 and nights 1–2 come from a temp copy of `cache/v16`, and day 3 on from
`gemini.FakeClient`. The script forces night 3's draws by wrapping `Night.u`; no production code changes.
- The first time anyone is offered `go_further` at bedtime, they take it. That night they keep to it: they let a
  leaver go, go later, or go all the same.
- Every other answer is the fake client's.
- In both runs Leo also went next door alone on night 3 and did not come back. That draw was the seed's, 0.914, on
  his shifted table (.56/.14/.18/.12, so not_back from 0.88). On the plain table it would have been scare_back.

### 4.1 Food (`runs/stage_b_fake/food.stdout.txt`)
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/stage_b_fake/fake_run.py food
exit code 0
prompts by scene: {'day3': 40, 'night3': 7, 'mind3': 3, 'day4': 30, 'night4': 5, 'mind4': 3, 'day5': 26}
first offered go_further at bedtime: Daniel (night3)
night 3 group: members ['leo'], far None, street not_back (u 0.9140448836121682), found None, took 0, lost leo, table [0.56, 0.14, 0.18, 0.12]
night 3 group: members ['daniel'], far True, street clean (u 0.0), found 4, took 4, lost None, table [0.41000000000000003, 0.17, 0.23, 0.19]
night 3 group: members ['elena'], far None, street clean (u 0.18064725233327417), found 0, took 0, lost None, table [0.62, 0.14, 0.18, 0.06]
night 3: shelf 0 -> 4; away ['leo']; far {'houses': [4], 'us': [0.8], 'searched': 1}
day 5 reaches bedtime: last span ends 834, last played stretch ends 840 (bedtime is 840); meta days 5
day 4 opening line (first day-4 prompt): - min 00: Everyone else gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 4 portions. So someone brought food into the house in the night. Leo is not here: his bed is empty and he is nowhere in the house. In the night you heard the front door; he has not come back. (you saw it)
day-4 prompts offering eat: 11 of 30
day-4 food acts: [(6, 'mara', 'eat'), (240, 'elena', 'share')]; …
```
Day 5's last span ends at 834 because a Q1 talk was played from 834 to bedtime. The played stretch closes at 840.

### 4.2 Lost (`runs/stage_b_fake/lost.stdout.txt`)
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/stage_b_fake/fake_run.py lost
exit code 0
prompts by scene: {'day3': 40, 'night3': 7, 'mind3': 2, 'day4': 5, 'night4': 5, 'mind4': 2, 'day5': 6}
first offered go_further at bedtime: Daniel (night3)
night 3 group: members ['leo'], far None, street not_back (u 0.9140448836121682), …, lost leo, table [0.56, 0.14, 0.18, 0.12]
night 3 group: members ['daniel'], far True, street not_back (u 0.99), found None, took 0, lost daniel, table [0.41000000000000003, 0.17, 0.23, 0.19]
night 3 group: members ['elena'], far None, street clean (u 0.18064725233327417), found 0, took 0, lost None, table [0.62, 0.14, 0.18, 0.06]
night 3: shelf 0 -> 0; away ['daniel', 'leo']; far None
day 5 reaches bedtime: last span ends 840, last played stretch ends 837 (bedtime is 840); meta days 5
Daniel's night-3 prompts: 2 (bedtime, before he went)
prompts to Daniel after he went out on night 3 (mind 3 to day 5): 0
day4: Daniel's acts 0, rooms holding him 0, in its needs log False, spans of his 0
day5: Daniel's acts 0, rooms holding him 0, in its needs log False, spans of his 0
night4: asked ['elena', 'mara']; mind4: asked ['elena', 'mara']
  elena's first day-4 prompt: About Daniel: last night you heard the front door, and by morning he was gone; he has not come back. | - min 00: … Daniel is not here: his bed is empty and he is nowhere in the house. In the night you heard the front door; he has not come back. Leo is not here: …
  mara's first day-4 prompt: About Daniel: last night you heard the front door, and by morning he was gone; he has not come back. | …
```
- **"Daniel's night-3 prompts: 2"** are his bedtime, and his answer to Leo leaving before him. Both came before he
  went out.
- **Elena and Mara both "heard"** the front door, awake. The fake had them both choose `go_next_door` that night,
  and only Elena went.

## 5. What each one knows of a loss, from the unit test (§3, test 4)

```
leo:   About Daniel: you saw him go out last night, and he has not come back.
elena: About Daniel: last night you heard the front door, and by morning he was gone; he has not come back.
mara:  About Daniel: he has been gone since last night; you do not know where he went.
```

## 6. Commands and raw output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. Every result below is from the final code.

### 6.1 DONE 4: v16 from a copy of `cache/v16` (`$S/replay_v16_b.py`)
```
$ sha256sum cache/v16/*.json > $S/v16cache.sha
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/replay_v16_b.py "$PWD"
daniel_ate_it-seed1: first prompt with no cached answer: day2, Daniel, minute 00 (after 67 cached answers, 0 live: True)
  who knows next door is empty at that point: ['daniel']; the prompt carries the street line: True, the far house line: True, the two day options: True
  scenes finished before it, equal to runs/v16's transcript: {'day1': True, 'night': True, 'mind1': True}
daniel_ate_it-seed2: first prompt with no cached answer: day3, Leo, minute 00 (after 96 cached answers, 0 live: True)
  who knows next door is empty at that point: ['daniel']; the prompt carries the street line: False, the far house line: False, the two day options: False
  scenes finished before it, equal to runs/v16's transcript: {'day1': True, 'night': True, 'mind1': True, 'day2': True, 'night2': True, 'mind2': True}
daniel_ate_it-seed3: first prompt with no cached answer: day3, Daniel, minute 00 (after 135 cached answers, 0 live: True)
  who knows next door is empty at that point: ['daniel']; the prompt carries the street line: True, the far house line: True, the two day options: True
  scenes finished before it, equal to runs/v16's transcript: {'day1': True, 'night': True, 'mind1': True, 'day2': True, 'night2': True, 'mind2': True}
```
The first version of this script compared the live transcript with the JSON one and reported seed 2's day 2 as
different: tuples against lists. A field-by-field walk of both (`$S/diff_day2.py`) found no difference. The script
now compares both as JSON.

### 6.2 The frozen versions
```
$ for v in v14 v13 v12 v11 v10 v9; do env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done > $S/b_frozen.txt
frozen IDENTICAL: 18          (3 seeds × 6 versions; 6 × "exit 0")
```

### 6.3 The cache, after
```
$ sha256sum -c $S/v16cache.sha        # seed1, seed2, seed3: OK
```

### 6.4 The full suite
```
$ ( time env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" ) > $S/b_full3.txt 2>&1
Ran 243 tests in 167.837s
OK
real	2m48.999s
exit 0
```
- **243 tests:** 236 before, plus the 7 new ones.
- **The last code changes** before this run wrapped two over-long lines in `night.py`, with the same strings. The
  fake runs, the replay and the frozen checks above were all rerun after that, with the outputs shown.
