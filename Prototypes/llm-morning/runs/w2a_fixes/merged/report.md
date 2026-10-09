# NOT READY FOR LIVE RUN

**With the bin set out on day 6 at 07:00 and never brought in, seed 2 still has 1 visit on days 3 to 10 (day 6,
09:27, from no. 6, water), not 3.** The street now sees the yard: by 12:00 on day 6, all three households that overlook
no. 9's yard believe no. 9 is lived in and has water to spare. None of them goes to its door by day 10. One is never
short of water. One runs dry on days 9 and 10 and searches empty houses instead, as a guarded household's weights make
it do. The third becomes short only on day 10 (§3).

# W2a fixes: the yard seen, the reasoned rate, the door stretch, true lines

Mode: implement. The brief's four fixes, each with a failing test first. The parent commit is `b1599e4` (W2a,
`reports/w2a_impl.md`). No API call was made, no cache was written, and no frozen version was touched. Paths are relative
to `Prototypes/llm-morning/`. Raw outputs are in `runs/w2a_fixes/`. Nothing of the family's minds, bodies, water,
bedtime or trips changed, and nothing else of W2b to W2f was built.

## Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| 1 | The four new tests fail before and pass after | **yes** | `red.stdout.txt`: 4 failures, each on its own assertion; `green.stdout.txt`: 4 OK (§1) |
| 2 | The full suite passes; v9 to v14 replays identical | **yes**; **18 of 18** | **301 tests OK** in 354 s, exit 0 (`unittest.stdout.txt`): 297 before plus the 4 new; `frozen.stdout.txt`: 18 × story and transcript IDENTICAL, 6 × exit 0 |
| 3 | The v16 seed 2 no-API replay still goes live first at day 3, min 00 | **yes** | `premiss.stdout.txt`: first miss at scene index 6, Leo, `Now, minute 00, you are in the kitchen.`; cache/v16 unchanged |
| 4 | The report opens with READY if seed 2's bin-out schedule has at least 3 visits, else NOT READY | **NOT READY**: 1 visit | `schedules.stdout.txt` (§3) |
| 5 | One commit with the changes, the tests and this report, no API key | see the reply | the hash cannot be inside the file it commits; the hash, the key search and `git status` are in the reply |

## 0. The four fixes

**1. The yard seen** (`street.py:569-635`, `truth.py:67-70`, `truth.py:127`, `quiet.py` `tick`).
- **Which houses overlook which yard** is in `streetdata/street.json` (`overlook`, every house): the two houses on each
  side, on the same side of the street. Est.: beyond the second yard, a terrace's yard walls and back extensions hide
  the ground of a yard from an upstairs window. The houses across face the front. A window is `yard_depth_m` 5 m (est.)
  behind the yard line.
  - **No. 9's yard is overlooked by nos. 5, 7, 11 and 13** (16.8, 9.4, 9.4 and 16.8 m, all within the 30 m sight
    range of `w2_design.md` §3.2). No. 7 is the empty neighbour, so at most three households see it.
- **The sight rule** (`street.sees`): seen if it is light and within range; the viewpoint is one of the `overlook`
  houses (§3.1). The daylight runs 07:01 to 18:37 on day 1, with sunset 2 minutes earlier each day (§3.2, N11; est.):
  `population.json` `sight`.
- **When**: at the start of each part of the day, before the plans (`see_yard`, from `advance`), each overlooking
  household sees what was in the yard during the daylight of the part just ended:
  - **The bin**, if it was out at any daylight minute of it. The household believes no. 9 is occupied (1.0) and has
    water to spare: `has_surplus` 0.8 (`population.json` `yard`, est.: a bin under a drainpipe says water, not how much
    nor whether they would share; the prior is 0.5).
  - **Anyone in the yard** at a daylight minute: occupied (1.0); the water is not judged from that.
  - Each sighting is logged (`saw_yard`).
- **What World holds of the yard** (`truth.py`): `bin_out_at` (the first time the bin was set out) and `yard_people`
  (each minute someone was out there), written by `put_bin_out`, which both `collect_rain` (day) and `rain_out`
  (bedtime) go through. `World.yard()` gives the street a value, as the weather does. No prompt builder reads it (it is
  World's, Guarded).
- *Arguing against it first.* Would a neighbour notice a wheelie bin under a drainpipe next door, and take it to mean
  water? In the second week with the taps dry, a bin set to catch the rain is the one change in a yard worth looking at,
  and an upstairs back window looks down on it. What they cannot know is how much is in it, which is why the belief is
  0.8 and not 1.

**2. The approach factor is 1.0 again** (`population.json` `approach.factor`; `factor_uncalibrated` 1.0 and
`factor_cap` 2.0 are kept for `runs/w2a_impl/schedule.py`). `reports/w2a_impl.md` §3 shows 2.0 did not change what
limited the knocks.

**3. The door stretch ends when nobody in its room perceives the door** (`quiet.py:778-806`, `play` at `quiet.py:1351`).
- At the start of each played turn of a Q7 stretch after its first, the door's percepts are delivered. If nobody awake
  in the stretch's room then has the door (`p.door`), the stretch is over:
  - its talk ends ("nobody in the room perceives the front door");
  - its pending asks are dropped;
  - the stretch closes, so its unused reserve is not held.
- The person outside goes on in quiet time, turn by turn (`door_quiet`; `next_event` steps 3 minutes while a scene is
  on): a second knock after 3 turns with nothing, heard and remembered; after 6, they go away.
- A scene's `asks` is now the asks of its Q7 stretches (or, for a knock inside another stretch, the asks since the
  knock, as before).
- **Tried and dropped:** asking again whoever perceives the door later in the scene. The routines seat everyone in the
  kitchen the minute the talk ends. In test F3's scene that re-asked, at 10:03, the three people who had walked away
  from the door at 10:00, and spent the rest of the reserve on the routine's placement (`f3_scene.stdout.txt` of that
  version, quoted in §1). The released asks stay released.

**4. The lines** (`street.says_true`, `streetdata/lines.json`, written by `runs/w2a_impl/write_lines.py`).
- The two "I heard voices, so I knocked" lines are tagged `heard_voices`: only for a household that heard the family's
  voices. No household perceives them in W2a, so they are never said. A new line for anyone takes the place of each:
  - "Hello? I'm sorry to trouble you. There's not a drop left in my house. Could you spare a little water?"
  - "Hello? I'm sorry to trouble you. There's nothing left in my house to eat. Could you spare a little?"
- A line that names a girl (or says "her") is tagged `girl`: only for a household with a girl. A line that names a boy
  ("him") is tagged `boy`. Beside each is a neutral line, tagged `child`:
  - voice_ask_water, *girl*: "Please, I've a little one at home and no water left to give her. Just a cup, if you can."
  - voice_ask_water, *child* (new): "Please, I've a little one at home and no water left. Just a cup, if you can."
  - open_ask_water, *girl*: "Thank you for opening. My little girl's had nothing to drink since this morning. Just a little water."
  - open_ask_water, *child* (new): "Thank you for opening. My little one's had nothing to drink since this morning. Just a little water."
  - open_ask_food, *boy*: "Thank you for opening. My boy hasn't had a proper meal in days. Anything at all, for him."
  - open_ask_food, *child* (new): "Thank you for opening. My little one hasn't had a proper meal in days. Anything at all."
- Every slot still has at least 8 lines any household may say: 102 lines in 11 slots.
- `test_t9` now allows the tags `girl`, `boy` and `heard_voices` beside `child` and `others`. That is its only change.

**Changed files** (`git diff --stat` before the commit): `quiet.py` 57, `street.py` 82, `truth.py` 12,
`streetdata/street.json` 174 (the `overlook` table), `streetdata/population.json` 4, `streetdata/lines.json` 26,
`runs/w2a_impl/write_lines.py` 24, `test_morning.py` 145: 8 files, 498 insertions, 26 deletions.

## 1. The tests, red and green

`.venv/Scripts/python.exe -m unittest test_morning.KnockFixTest`, `GEMINI_API_KEY` unset (`test_morning.py:7381-7530`).

**Before any of the four fixes** (`runs/w2a_fixes/red.stdout.txt`):
```
FAIL: test_f1_a_bin_in_no_9s_yard_is_seen_by_day_from_the_houses_that_overlook_it
AssertionError: None is not true : street.json does not say which houses overlook no. 9's yard
FAIL: test_f2_the_approach_factor_is_back_to_1
AssertionError: 2.0 != 1.0
FAIL: test_f3_a_q7_stretch_ends_and_frees_its_reserve_when_nobody_in_its_room_perceives_the_door
AssertionError: 201 != 183 : [{'start': 180, 'end': 201, 'room': 'kitchen', 'trigger': 'Q7', 'asks': 6}]
FAIL: test_f4_a_strangers_line_says_only_what_its_household_is
AssertionError: None != 'heard_voices' : I heard voices, so I knocked. I've no water left. Anything you could spare, I'd be grateful.
Ran 4 tests in 1.524s
FAILED (failures=4)
```
F3's red is the fault itself: everyone at the door walked away at 10:00, and the Q7 stretch went on to 10:21 and spent
all 6 of its asks.

**After** (`runs/w2a_fixes/green.stdout.txt`):
```
test_f1_a_bin_in_no_9s_yard_is_seen_by_day_from_the_houses_that_overlook_it ... ok
test_f2_the_approach_factor_is_back_to_1 ... ok
test_f3_a_q7_stretch_ends_and_frees_its_reserve_when_nobody_in_its_room_perceives_the_door ... ok
test_f4_a_strangers_line_says_only_what_its_household_is ... ok
Ran 4 tests in 2.184s
OK
```
The nine W2a tests (`KnockTest`) also pass with the fixes in: `Ran 13 tests in 10.729s, OK` for the two classes
together.

| | Holds |
|---|---|
| F1 | street.json says who overlooks no. 9's yard; a bin out at 07:00 on day 6 is not seen before that day and is seen by 12:00: every occupied overlooking house then believes (occupied 1.0, has_surplus 0.8), with a `saw_yard` record; no other household's belief moves; a bin put out at 19:00 is not seen at midnight or 06:00 and is seen by 12:00 the next day; beyond the sight range nothing is seen, and nothing in the dark; someone in the yard by day with no bin makes no. 9 occupied and leaves has_surplus at its prior; in the run, `collect_rain` at 07:30 on day 3 sets World's `bin_out_at` and `yard_people`, and the street has the beliefs by 12:03 |
| F2 | `population.json` and a new street both have the factor 1.0 |
| F3 | v16 seed 2, day 3, a visit for water at 10:00; whoever is offered the door walks away from it, then confronts someone: the Q7 stretch ends at 10:03; every ask made in a Q7 stretch has the door in its prompt; the scene asks at most 6, ends "ignored", and nothing is reserved after it |
| F4 | the "heard voices" lines are tagged so; over seeds 1 to 10, every household, visits 1 to 5 and every slot: no line says it heard voices; a line with girl, her or she only for a household with a girl; boy, him or he only with a boy; little one or child only with a child |

**F3's scene, turn by turn** (`runs/w2a_fixes/f3_scene.py`, `f3_scene.stdout.txt`):
```
10:00 Q7: fired=True room=kitchen asked=['elena', 'leo', 'mara'] why=None left=None
stretch 10:00-10:03 Q7 in kitchen: 3 asks
  10:00 mara in kitchen: go_back_room [model]
  10:00 leo in kitchen: go_back_room [model]
  10:00 elena in kitchen: go_back_room [model]
scene 10:00-10:18: outcome ignored; Q7 asks 3; knocks ['10:00', '10:09']; heard {'elena': 'words', 'leo': 'words', 'mara': 'words', 'daniel': 'heard'}
day asks 24; reserved now False
```
The version that re-asked whoever perceived the door again (dropped, §0.3) gave, at the same point:
```
10:03 Q7: fired=True room=kitchen asked=['elena', 'leo', 'mara'] why=the door is perceived again left=3
stretch 10:03-10:06 Q7 in kitchen: 3 asks
  10:03 mara in kitchen: go_back_room [model]
  10:03 elena in kitchen: go_back_room [model]
  10:03 leo in kitchen: go_back_room [model]
```
The three had been seated in the kitchen by the routines at 10:03, three minutes after walking away from the door.

## 2. Who overlooks no. 9's yard, and what each believes when

From `runs/w2a_fixes/schedules.py` (`schedules.stdout.txt`), with the bin out from day 6, 07:00, no knock answered. In
every seed every occupied overlooking house first sees the bin in the 06:00–12:00 part of day 6 and believes it at
12:00. Before that each already believed no. 9 occupied (1.0: it is within 5 doors, §2.1) and has_surplus at the prior,
0.5. By the end of day 10 none of them has knocked: kind 0.6 and refused 0 throughout.

| Seed | No. 5 | No. 7 | No. 11 | No. 13 |
|---|---|---|---|---|
| 1 | 4 people, helper | the empty neighbour | 5, helper | 1, guarded |
| 2 | 1, guarded | the empty neighbour | 3, guarded | 2, helper |
| 3 | empty | the empty neighbour | 2, guarded | 2, helper |
| 4 | 2, helper | the empty neighbour | 2, helper | 1, helper |
| 5 | 2, helper | the empty neighbour | empty | 2, opportunist |
| 6 | 2, helper | the empty neighbour | 1, helper | 1, helper |
| 7 | empty | the empty neighbour | 2, opportunist | empty |
| 8 | empty | the empty neighbour | 2, helper | 2, helper |
| 9 | 3, guarded | the empty neighbour | 5, guarded | empty |
| 10 | 2, helper | the empty neighbour | 3, helper | empty |

Each occupied one: before day 6 (occupied 1.0, has_surplus 0.5); from day 6, 12:00 (occupied 1.0, has_surplus 0.8),
to the end of day 10. With the bin never out, none of them changes.

## 3. The schedules, seeds 1 to 10, days 3 to 10, factor 1.0, no knock answered

`runs/w2a_fixes/schedules.stdout.txt`:
```
BIN NEVER OUT:
  seed  1: 1 knock(s)  day 6 15:45 no. 10 ask water
  seed  2: 1 knock(s)  day 6 09:27 no. 6 ask water
  seed  3: 1 knock(s)  day 9 16:06 no. 3 ask water
  seed  4: 0 knock(s)
  seed  5: 0 knock(s)
  seed  6: 0 knock(s)
  seed  7: 1 knock(s)  day 9 08:51 no. 17 ask water
  seed  8: 2 knock(s)  day 3 08:15 no. 3 ask food; day 7 16:30 no. 11 ask water
  seed  9: 0 knock(s)
  seed 10: 0 knock(s)
  counts [1, 1, 1, 0, 0, 0, 1, 2, 0, 0]; median 0.5; max 2

BIN OUT FROM DAY 6, 07:00, NEVER BROUGHT IN:
  seed  1: 1 knock(s)  day 6 15:45 no. 10 ask water
  seed  2: 1 knock(s)  day 6 09:27 no. 6 ask water
  seed  3: 1 knock(s)  day 9 16:06 no. 3 ask water
  seed  4: 0 knock(s)
  seed  5: 0 knock(s)
  seed  6: 1 knock(s)  day 9 11:57 no. 11 ask food
  seed  7: 1 knock(s)  day 9 08:51 no. 17 ask water
  seed  8: 2 knock(s)  day 3 08:15 no. 3 ask food; day 7 16:30 no. 11 ask water
  seed  9: 0 knock(s)
  seed 10: 0 knock(s)
  counts [1, 1, 1, 0, 0, 1, 1, 2, 0, 0]; median 1.0; max 2

SEED 2, bin out: 1 visit(s) on days 3 to 10: NOT READY FOR LIVE RUN
```
The bin brings one knock in ten seeds: seed 6, day 9, from no. 11, an overlooking house. Its household asks for food,
because water is not its need.

**Seed 2, why not** (`runs/w2a_fixes/why_seed2.py`, `why_seed2.stdout.txt`: each overlooking household's plan and scores
in every part from day 5 on):

| House | Who | At the end of day 10 | What it did from day 6 |
|---|---|---|---|
| no. 5 | 1 person, guarded | water 10.5 L, food 3.0 days: need of water 0, of food 0.57, urgency 0.34 | stayed in every part: `stay` 0.19 to 0.34, `ask` −0.10 to −0.27 |
| no. 11 | 3 people, guarded | water 0, food 9.9 days: urgency 1.0 | stayed to day 8; from day 9, 06:00 to day 10, 18:00, **searched** empty houses (nos. 10, 17, 3, 19, 4, 1) in every part but one: `search` 0.09 to 0.34 against `ask` −0.14 to 0.06 |
| no. 13 | 2 people, helper | water 3.9 L: urgency 0.67 | stayed to day 9; searched once (day 10, 06:00: `search` 0.14 against `ask` 0.06) |

Read as households, this is what the weights say people do. Someone with water does not beg, and a guarded household
with a bath to find in an empty house goes there before it asks a stranger. For no. 11, by the time water is short the
nearest empty houses have not yet been searched, and for a guarded household `ask` weighs 0.4 against `search`'s 1.0
(`w2_design.md` §2.3). So the bin raises the chance that asking no. 9 succeeds, from 0.6 × 0.5 to 0.6 × 0.8. But the
households that see it are not at the point where any ask wins, in the ten days of seed 2.

What would change it is again a design decision, not a fix:
- when the street runs short (the stores of §1.3);
- how a guarded household weighs `ask` against `search`;
- or whether a household that has seen water next door asks there before searching farther.

## 4. The replays

**Frozen versions** (`runs/w2a_fixes/frozen.stdout.txt`): `v14/check.py` to `v9/check.py`, seeds 1 to 3 each: **18 of
18** "story IDENTICAL, transcript IDENTICAL"; six exits 0.

**v16 seed 2, no API, `--days 10`, a temp copy of cache/v16** (`runs/w2a_impl/premiss.py`, output in
`runs/w2a_fixes/premiss.stdout.txt`):
```
  street day 6 09:27: a visit to the front door from no. 6 (ask water)
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']
exit 3; cache/v16 sha256 before d79a49396e91a3be, after d79a49396e91a3be: unchanged
```

## 5. The full suite

`runs/w2a_fixes/unittest.stdout.txt`, `unittest.time.txt`: one run, started after the last code change (only `runs/w2a_fixes/` and
this report changed while it ran):
```
$ $PY -m unittest test_morning
Ran 301 tests in 354.381s

OK
exit 0
real	5m55.997s
```
The only existing test changed is `test_t9` (the tags it allows, §0.4). The `[429 RESOURCE_EXHAUSTED]` lines in the output are
the stubbed API's scripted errors (`GeminiClientTest`), as in every earlier run.

## 6. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. `$PY` is `.venv/Scripts/python.exe`, run with
`PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1`.
```
$ $PY -m unittest test_morning.KnockFixTest                 (before) Ran 4 tests, FAILED (failures=4), exit 1     red.stdout.txt
$ $PY runs/w2a_impl/write_lines.py                          {'voice_ask_water': 12, 'voice_ask_food': 11, 'open_ask_water': 11, 'open_ask_food': 11, 'insist_water': 9, 'insist_food': 9, 'again_water': 8, 'again_food': 8, 'given': 8, 'refused_polite': 8, 'refused_flat': 8}
$ $PY -m unittest test_morning.KnockFixTest test_morning.KnockTest      Ran 13 tests in 10.729s, OK
$ $PY -m unittest -v test_morning.KnockFixTest              (after) Ran 4 tests in 2.184s, OK, exit 0     green.stdout.txt
$ $PY runs/w2a_fixes/f3_scene.py                            f3_scene.stdout.txt (§1)
$ $PY runs/w2a_fixes/schedules.py                           exit 0     schedules.stdout.txt (§2, §3)
$ $PY runs/w2a_fixes/why_seed2.py                           exit 0     why_seed2.stdout.txt (§3)
$ for v in v14 v13 v12 v11 v10 v9; do $PY $v/check.py; done  18 × IDENTICAL, 6 × exit 0     frozen.stdout.txt
$ $PY runs/w2a_impl/premiss.py                              exit 3 at day 3, min 00; cache unchanged     premiss.stdout.txt
$ $PY -m unittest test_morning                              Ran 301 tests in 354.381s, OK, exit 0     unittest.stdout.txt
$ git diff --stat (before the commit)                       8 files changed, 498 insertions(+), 26 deletions(-)
```
The commit adds this report, `runs/w2a_fixes/` and the changed files. Its hash, the search for a key in the staged files
and `git status` after it are given in the reply. The three old `runs/v6/daniel_ate_it-seed{1,2,3}.replay.md` stay
untracked.
