# merged: all documents

Merged by `merge-slice-docs.py` from the 2 Markdown files in `Prototypes/llm-morning/runs/w2a_fixes/merged/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`w2a_impl.md`](#w2a_implmd)

---

## report.md

### NOT READY FOR LIVE RUN

**With the bin set out on day 6 at 07:00 and never brought in, seed 2 still has 1 visit on days 3 to 10 (day 6,
09:27, from no. 6, water), not 3.** The street now sees the yard: by 12:00 on day 6, all three households that overlook
no. 9's yard believe no. 9 is lived in and has water to spare. None of them goes to its door by day 10. One is never
short of water. One runs dry on days 9 and 10 and searches empty houses instead, as a guarded household's weights make
it do. The third becomes short only on day 10 (§3).

### W2a fixes: the yard seen, the reasoned rate, the door stretch, true lines

Mode: implement. The brief's four fixes, each with a failing test first. The parent commit is `b1599e4` (W2a,
`reports/w2a_impl.md`). No API call was made, no cache was written, and no frozen version was touched. Paths are relative
to `Prototypes/llm-morning/`. Raw outputs are in `runs/w2a_fixes/`. Nothing of the family's minds, bodies, water,
bedtime or trips changed, and nothing else of W2b to W2f was built.

#### Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| 1 | The four new tests fail before and pass after | **yes** | `red.stdout.txt`: 4 failures, each on its own assertion; `green.stdout.txt`: 4 OK (§1) |
| 2 | The full suite passes; v9 to v14 replays identical | **yes**; **18 of 18** | **301 tests OK** in 354 s, exit 0 (`unittest.stdout.txt`): 297 before plus the 4 new; `frozen.stdout.txt`: 18 × story and transcript IDENTICAL, 6 × exit 0 |
| 3 | The v16 seed 2 no-API replay still goes live first at day 3, min 00 | **yes** | `premiss.stdout.txt`: first miss at scene index 6, Leo, `Now, minute 00, you are in the kitchen.`; cache/v16 unchanged |
| 4 | The report opens with READY if seed 2's bin-out schedule has at least 3 visits, else NOT READY | **NOT READY**: 1 visit | `schedules.stdout.txt` (§3) |
| 5 | One commit with the changes, the tests and this report, no API key | see the reply | the hash cannot be inside the file it commits; the hash, the key search and `git status` are in the reply |

#### 0. The four fixes

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

#### 1. The tests, red and green

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

#### 2. Who overlooks no. 9's yard, and what each believes when

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

#### 3. The schedules, seeds 1 to 10, days 3 to 10, factor 1.0, no knock answered

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

#### 4. The replays

**Frozen versions** (`runs/w2a_fixes/frozen.stdout.txt`): `v14/check.py` to `v9/check.py`, seeds 1 to 3 each: **18 of
18** "story IDENTICAL, transcript IDENTICAL"; six exits 0.

**v16 seed 2, no API, `--days 10`, a temp copy of cache/v16** (`runs/w2a_impl/premiss.py`, output in
`runs/w2a_fixes/premiss.stdout.txt`):
```
  street day 6 09:27: a visit to the front door from no. 6 (ask water)
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']
exit 3; cache/v16 sha256 before d79a49396e91a3be, after d79a49396e91a3be: unchanged
```

#### 5. The full suite

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

#### 6. Commands and output

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

---

## w2a_impl.md

### NOT READY FOR LIVE RUN

**Seed 2 has 1 visit on days 3 to 10 (day 6, 09:27), not 3.** The knock factor is capped at 2.0x (amendment 1). At the
cap the median over seeds 1 to 10 is 1 knock, not the design's 4 (§2.7). The build is finished; the live run is not
planned (amendment 2).

### W2a, the knock: implementation

Mode: implement. The design is `reports/w2_design.md`, built as its §7.2 says with the four amendments of the brief. The
parent commit is `da9b0d7`. No API call was made, no cache was written, and no frozen version (v1 to v14) was touched.
Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/w2a_impl/`. O1 to O4 are at the design's
defaults (§0.4). No scorer and no run plan were written (amendment 4).

#### Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| 1 | T1 to T9 each failed before its code and pass after | **yes** | §1: `red_all.stdout.txt` (9 failures before any production code), the per-test reds, and `green.stdout.txt` (9 OK) |
| 2 | The full suite passes | **yes** | **297 tests OK** in 389 s, exit 0, on the first run (`runs/w2a_impl/unittest.stdout.txt`); 288 before plus the 9 of `KnockTest` |
| 3 | v9 to v14 frozen replays identical | **yes, 18 of 18** | `frozen.stdout.txt`: story and transcript IDENTICAL for seeds 1 to 3 of each version; 6 exits 0 |
| 4 | A no-API replay of v16 seed 2 goes live first at day 3, min 00 | **yes** | `premiss.stdout.txt`: first miss at scene index 6 (day 3), Leo, `Now, minute 00, you are in the kitchen.`; cache/v16 unchanged (sha256 `d79a49396e91a3be…`) |
| 5 | A fake 10-day run of seed 2 exits 0, at least one door scene, no Q7 stretch over 6 asks, no day over 56 | **yes** | `fake10.summary.txt`: exit 0; 1 door scene (day 6, 09:27 to 09:45); the Q7 stretch used 6 asks; the busiest day asked 48 |
| 6 | One commit with the design, the code, the data files, the tests and this report, no API key | see the reply | Its hash cannot be inside the file it commits (as `reports/v22_fixes.md` §6); the hash, the key check and `git status` are given in the reply |

**Amendments 1 to 3:**

| | Asked | Result |
|---|---|---|
| 1 | Uncalibrated schedule of seeds 1 to 10; calibrate as §2.7 (median 4 knocks on days 3 to 10, no seed over 8), factor at most 2.0x; both schedules and the factor | Uncalibrated (1.0): counts 1, 1, 1, 0, 0, 0, 1, 2, 0, 0; median 0.5. **No factor up to 2.0 meets §2.7.** Chosen: **2.0**, the cap, as the closest: counts 3, 1, 1, 1, 0, 0, 3, 4, 0, 1; median 1; max 4 (§3) |
| 2 | Seed 2's schedule for days 3 to 10 with each visit's purpose; fewer than 3 visits → NOT READY | **1 visit**: day 6, 09:27, from no. 6 (2 people, helper), a woman of about forty, **water**. Hence the heading |
| 3 | At least 8 variants per slot, every line listed, by slot | 11 slots, **8 to 10 lines each**, every slot with at least 8 lines any household may use; 98 lines in all (§4) |

#### 0. What was built

**New files.**
- `street.py`: pure functions over plain dicts, every draw by a string of its own:
  - `generate(seed, street, pop, draw)`: the 30 houses, 8 empty by a balanced draw, 20 households (§1).
  - `consume`, `plan`, `search`, `resolve`, `advance(state, to, wet)`: the four parts of the day; plans `stay`, `search`, `ask`; the exchange between two households (§2.2 to §2.5, §2.7).
  - `make_visit`, `due`, `defer`, `end_visit`, `schedule(seed, days, factor)`: the visit to no. 9 by day and its printed schedule (§4.2).
  - `perceive`, `wake_chance`, `wakes`: the noticing rule, sound only (§3.1).
  - `line`, `who_words`, `looks`: the stranger's words from the pool, and what an eye and an ear get of the envoy (§4.3, §4.6).
- `streetdata/street.json`: the houses, positions, no. 9 and no. 7, and where in the house a knock is heard from.
- `streetdata/population.json`: every table and weight in one place.
- `streetdata/lines.json`: the pool, written once by `runs/w2a_impl/write_lines.py`.

**Existing files touched** (`git diff --stat`: 11 files, 851 insertions, 11 deletions).

| File | Change |
|---|---|
| `truth.py` | `World.street` (drawn at `World()`; Guarded like the rest, so a prompt builder that reads it raises `TruthLeak`); `World.given` and `give_away` (the tap water, then the bin); `ahead()`: the look-ahead copy of `next_change` without the street |
| `quiet.py` | `DOOR_ASKS, DAY_MAX, KNOCK_UNDER = 6, 56, 52` (`quiet.py:93`); `tick` advances the street; `spent` holds the 56 for every stretch, reserved or not (`:403`); `hear_knock` (Q7, `:462`), `knock_heard` (`:520`), `door_views` (`:565`), `door_before` (`:604`), `door_act` (`:656`), `door_after` (`:687`), `door_end` (`:721`); `step`, `turn`, `play`, `world_events`, `items`, `transcript` |
| `world.py` | `Person.door`; `door_options` (`world.py:618`) in `options_for`; the door's `Now` lines (`:1155`) and the house line (`:1139`); the door acts in `apply` (`:1713`), `KIND_DONE`, `line_text`; `last_block`; the trip block no longer counts the door's words in the house line as outside the budget |
| `talk.py` | `door_call`, `door_refuse` in `SPEECH`; `Newness`: an answer at the door is new the first time in a scene (`forget_door`) |
| `data.py` | `DOOR` and `with_door`: while someone is at the door, the house line names the gap and the person there |
| `chronicle.py` | gists for `knock`, `door_line`, `door_end` and the five door acts |
| `memory.py` | `WEIGHT` `door_give` 4, `door_open` 3; their block C lines |
| `night.py` | `carry_in_later`: one block A line for each door scene of yesterday that the person heard or was at |
| `story.py` | the knock, the stranger's words, the visit's end and the Q7 rows |
| `morning.py` | prints the seed's first-visit schedule beside the weather; Q7 in the run log and `quiet_meta` |
| `test_morning.py` | `KnockTest`, T1 to T9 |

**What W2a does not build**, as §7.2 says: perception of the family by the street, `trade`, `offer`, `warn`, `take`,
`leave`, night visits, rumours, word between households, trips among people, a model-written stranger, a standing
line, and any change to the family's minds, bodies, water rules, bedtime or trip tables.

##### 0.1 Choices the design left open, and the ones made here

Each is in the code with a comment.

1. **A food visit gets no `door_give`.** §4.2.5 says `door_give` is "only if the visitor asked for water". So a visitor
   who asks for food can be called to, opened to or sent away, but nothing in the house is offered. Judged by what a real
   family would do, a family with portions on the shelf could hand one over. This is the design's rule, kept as written,
   and an open question. In the schedules only 1 of 18 calibrated visits asks for food (seed 8, day 3).
2. **A visit deferred because a knock came today goes to the next day's first daylight part**, not to the next part.
   §4.2.2 says "the next part", but with one knock a day the next part of the same day can only defer it again.
3. **"Ignored" counts toward "refused twice".** A knock nobody answers lowers nothing else, but a household that is
   not answered twice stops coming (§2.4, `refused_twice`). A real person tries a door a second time, not a third.
4. **The first-visit schedule** is `street.schedule`: the visits the street makes when no knock is ever answered, with at
   most one a day (later ones that day go to the next day). §4.2.1 fixes only the first visits by the seed alone. Once
   the family answers, a later visit can move (a gift raises *kind* and the visitor's water).
5. **Search** goes to the nearest empty house the household knows of (within 5 doors, §2.1) that it has not searched,
   within 80 m, never no. 7 (O3). Gain is 1.0 when water is the household's main need (a bath may be full) and 0.4 for
   food. This is the reading of §2.3's "1.0 if a bath is believed full, else 0.4"; it reproduces §2.3's worked example.
6. **The ask target** is drawn among houses within 80 m that the household believes occupied, weighted by
   *occupied × kind × surplus / distance*. The score uses the drawn target's chance. Before day 3, and outside
   06:00 to 18:00, no. 9 is not a target (§7.2).
7. **The approach factor** is the chance that an `ask` plan becomes a trip in its part: `trips_a_part` 0.2 × factor.
   At 1.0 that is 0.4 a day over the two daylight parts, inside §2.7's 0.3 to 0.5.
8. **Households' bodies** (§1.3, "at household grain") are not built. W2a reads only their stores, as urgency.
9. **The knock in the rain.** Under rain (ambient 35 dB) the kitchen hears the knock (39 dB) but not as words
   (§3.3). Its line is "You hear knocking at the front of the house." The bedrooms hear nothing then. The stranger's
   words come through the gap (O1) to whoever is in the kitchen.
10. **Labels and the house line were shortened** to meet T5's 140 tokens (§1, T5). The design's §6.3 estimate of 122
    tokens did not count the house-line addition. Its first form, with all five options and the voice line, came to 152.

#### 1. The tests, red and green

All runs: `PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1`, `GEMINI_API_KEY` unset, `.venv/Scripts/python.exe -m unittest test_morning.KnockTest[.<test>]`.

**Before any production code**, all nine (`runs/w2a_impl/red_all.stdout.txt`):
```
FAIL: test_t1_the_street_is_drawn_by_string_and_adding_a_house_changes_no_other_draw
AssertionError: unexpectedly None : street.py is not built
FAIL: test_t2_stocks_are_conserved_across_every_exchange_and_every_door_give
AssertionError: unexpectedly None : street.py is not built
FAIL: test_t3_a_prompt_builder_that_reads_world_street_raises_truthleak
AssertionError: unexpectedly None : World.street is not built
FAIL: test_t4_days_1_and_2_replay_and_the_street_makes_no_visit_before_day_3
AssertionError: unexpectedly None : World.street is not built
FAIL: test_t5_the_block_is_the_same_with_and_without_a_door_and_the_door_lines_are_under_140_tokens
AssertionError: unexpectedly None : street.py is not built
FAIL: test_t6_a_knock_comes_by_day_once_a_day_never_into_the_bathroom_and_wakes_by_the_draw
AssertionError: unexpectedly None : street.py is not built
FAIL: test_t7_the_door_options_exist_only_in_a_scene_in_the_kitchen
AssertionError: unexpectedly None : street.py is not built
FAIL: test_t8_a_q7_stretch_asks_at_most_6_and_a_day_at_most_56
AssertionError: unexpectedly None : street.py is not built
FAIL: test_t9_every_strangers_line_is_short_plain_and_of_the_familys_world
AssertionError: False is not true : streetdata/lines.json is not written
Ran 9 tests in 0.375s
FAILED (failures=9)
```

**Built in this order.** Each test was run red, with the reason below, just before its own code went in.

| Test | Red, just before its code | Its code | Green |
|---|---|---|---|
| T9 | `red_t9`: `streetdata/lines.json is not written` | the pool | `green_t9`: OK |
| T1 | `red_all` (above) | `street.py`, `street.json`, `population.json` | `green_t1`: OK |
| T2 | `red_t2`: the street half passed; the door half failed: `World.street is not built` | `World.street`, then `door_act`'s give | in the final run |
| T3 | `red_all`: `World.street is not built` | `World.street`, `World.ahead` | `green_t3`: OK |
| T4 | `red_t4`: `[] is not true : the street has not been advanced to day 3` | `Quiet.tick` advances the street | `green_t4`: OK |
| T5, T7 | `red_t5_t7`: `AttributeError: 'Newness' object has no attribute 'forget_door'` (the scene code was in; the talk and options were not) | `talk.py`, `world.py`, `data.py` | first run: T5 `3771 != 3668` (the block grew by the door's house-line words); then `151.6 not less than or equal to 140`; both fixed in production code (§0.1, 10) |
| T6, T8 | `red_all` only: their code (`hear_knock`, `spent`) went in with the scene, before a per-test red was taken | `quiet.py` | T6 first ran red on its own premise (below) |

**Changes to tests before they first went green**, none to an assertion's meaning:
- T4: `parts[0]` raised `IndexError` (an error, not a failure). An `assertTrue(parts, …)` was put before it.
- T5: the voice-line regex had a stray backspace character from an edit. It was removed.
- T6: the one-a-day case first put its visits at 09:00 and 10:00. At 09:00 on v16 seed 2's day 3 everyone is resting
  and the knock woke nobody, so the visit was rightly deferred ("nobody awake heard it"). The visits were moved to
  10:00 and 11:00, when people are awake.

**After** (`runs/w2a_impl/green.stdout.txt`):
```
test_t1_the_street_is_drawn_by_string_and_adding_a_house_changes_no_other_draw ... ok
test_t2_stocks_are_conserved_across_every_exchange_and_every_door_give ... ok
test_t3_a_prompt_builder_that_reads_world_street_raises_truthleak ... ok
test_t4_days_1_and_2_replay_and_the_street_makes_no_visit_before_day_3 ... ok
test_t5_the_block_is_the_same_with_and_without_a_door_and_the_door_lines_are_under_140_tokens ... ok
test_t6_a_knock_comes_by_day_once_a_day_never_into_the_bathroom_and_wakes_by_the_draw ... ok
test_t7_the_door_options_exist_only_in_a_scene_in_the_kitchen ... ok
test_t8_a_q7_stretch_asks_at_most_6_and_a_day_at_most_56 ... ok
test_t9_every_strangers_line_is_short_plain_and_of_the_familys_world ... ok
Ran 9 tests in 10.044s
OK
```

What each test holds (`test_morning.py:7025-7380`):

| | Holds |
|---|---|
| T1 | the same seed gives the same street, another seed another; 30 houses, 20 households, 8 empty, no. 9 the family's, no. 7 the empty neighbour's; every household has an adult; the houses listed in reverse give the same households; with a 31st house, every household of a house occupied in both is drawn the same; every draw comes through the one `draw` argument, each by its own string starting `2:street:` |
| T2 | an ask between two households moves exactly what one loses to the other; a search moves all an empty house holds, once; over eight days the street's water and food change only by what it used and found; a `door_give` takes exactly min(3 L, the store) from World and adds exactly that to the visitor's household |
| T3 | `World.street` read while a prompt is built raises `TruthLeak`; a prompt builder that reads it does too; the look-ahead copy does not carry the street |
| T4 | days 1 and 2, nights 1 and 2 and minds 1 and 2 come from cache/v16; the street was advanced from day 1, 00:00, with plans; no visit and no deed reaches no. 9 before day 3; the no-API replay of v16 seed 2 to day 10 misses first at day 3, min 00 |
| T5 | a kitchen prompt in a scene, with 200 filler memory lines (so trimming runs), has the same `block` with and without the door; the door lines and the house-line addition are ≤ 140 estimated tokens; memory lines are cut instead |
| T6 | over seeds 1 to 10, every scheduled visit is on day 3 or later, 07:30 to 17:30, on the 3-minute grid; a second visit the same day is deferred to the next day ("a knock has come today already"); a visit with 52 asks spent is deferred; the bathroom hears nothing; the kitchen hears words, a bedroom hears knocking; someone resting wakes exactly by their draw, and their rest ends then; the wake chance is min(0.9, 2 × (0.10 + 0.20 × anxious)) |
| T7 | no door options outside a scene; in a scene, `door_look`, `door_call`, `door_open`, `door_refuse` in the kitchen and none in another room; `door_give` once a water need has been heard and only while there is water; `door_open` and `door_look` gone once the door is open; no `door_give` for a food visit |
| T8 | a Q7 stretch asks at most 6; a day at most 56, with the 56 holding even for a reserved stretch |
| T9 | the 11 slots; at least 8 lines per slot any household may use; every line ≤ 25 words, no digit, no weekday, no number word, no house number, nothing the family's world lacks, no "should" or "must"; water lines never speak of food and food lines never of water; a line that says "we", or speaks of a child, is tagged so that only a household that has one can say it |

#### 2. The door scene, as built

- **The visit.** At the start of a daylight part (06:00 or 12:00), a household whose plan is `ask` and whose target is
  no. 9 goes with chance 0.2 × factor. Its visit falls on the 3-minute grid in 07:30–12:00 or 12:00–17:30, by
  `<seed>:street:<household>:day<k>:visit`. The household waits on it and makes no other plan.
- **The minute it comes** (`Quiet.hear_knock`): it is deferred if a knock has come today, if 52 or more asks are spent,
  or if nobody awake hears it after the wake draws. Otherwise it is knocked: 70 dB at the door.
  - Who hears: the kitchen hears words (39 dB against 25); a bedroom hears knocking (29); the bathroom nothing; in rain
    the kitchen hears knocking and the bedrooms nothing.
  - Whoever hears gets a memory line, and the talk starts in their room.
  - In played turns the stretch's cap grows by 6 and is reserved. In a quiet stretch it is **Q7**: the kitchen is
    played if anyone awake is there, else the room with most awake; everyone awake there is asked; 6 reserved asks.
- **Each turn** (`door_before`, `door_after`): the person outside answers the kind of act it perceived, never its
  words (`talk.py:68`).
  - A give: the `given` line, then they leave.
  - A refusal: `refused_flat` (not a helper, or impulsive 0.6 or more) or `refused_polite`, then they leave.
  - An open: next turn the door is open, the envoy is described, and they say `open_ask_<good>`.
  - A call: the first reply is `voice_ask_<good>`; later ones are `insist_<good>` (urgency 0.8 or more) or
    `again_<good>`.
  - Three turns with nothing: a second knock, with new wake draws. Six: footsteps go away.
- **The lines a kitchen prompt gets** (written by code into `p.door`, never read from World), in order:
  - the open door and who stands there; or the knock; or "Someone is at the front door; there was a knock at HH:MM";
  - the stranger's last words, "says" in the turn they were said, "Earlier, at HH:MM, … said" after.
- **After** (`door_end`): the visit's outcome and a deed go into the street. Each person who was at the door or heard
  the words gets one sure line of it, and anyone who only heard knocking gets that. The next day's block A has the
  line, and the chronicle has `knock`, `door_line`, the family's door acts and `door_end`.

**The cost of the lines** (`runs/w2a_impl/door_tokens.py`, `door_tokens.stdout.txt`; T5's count): a knock with four
options, 88.6 estimated tokens; the voice line with all five options, 127.6; the open door with the voice and three
options, 129.6. All are inside the prompt budget: they displace memory lines and do not grow the prompt.

#### 3. The schedules and the factor (amendments 1 and 2)

`runs/w2a_impl/schedule.py` (`schedule.stdout.txt`), no API, the seed's own weather:
```
UNCALIBRATED (factor 1.0: an ask plan goes to a door with chance 0.2 a part):
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

THE CALIBRATION, factors 0.25 to the cap (median and max of knocks on days 3-10 over seeds 1-10):
  factor 0.25: counts [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; median 0.0; max 0
  factor 0.50: counts [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]; median 0.0; max 1
  factor 0.75: counts [1, 1, 1, 0, 0, 0, 1, 2, 0, 0]; median 0.5; max 2
  factor 1.00: counts [1, 1, 1, 0, 0, 0, 1, 2, 0, 0]; median 0.5; max 2
  factor 1.25: counts [1, 1, 2, 0, 0, 1, 2, 3, 0, 0]; median 1.0; max 3
  factor 1.50: counts [2, 1, 2, 0, 0, 1, 2, 3, 0, 1]; median 1.0; max 3
  factor 1.75: counts [2, 1, 1, 1, 0, 1, 3, 3, 0, 1]; median 1.0; max 3
  factor 2.00: counts [3, 1, 1, 1, 0, 0, 3, 4, 0, 1]; median 1.0; max 4

CHOSEN: factor 2.0 (no factor up to the cap meets §2.7 (median 4, none over 8); the cap is the closest); population.json has factor 2.0

CALIBRATED (factor 2.0):
  seed  1: 3 knock(s)  day 6 15:45 no. 10 ask water; day 7 11:06 no. 28 ask water; day 10 12:54 no. 26 ask water
  seed  2: 1 knock(s)  day 6 09:27 no. 6 ask water
  seed  3: 1 knock(s)  day 9 16:06 no. 3 ask water
  seed  4: 1 knock(s)  day 7 13:33 no. 6 ask water
  seed  5: 0 knock(s)
  seed  6: 0 knock(s)
  seed  7: 3 knock(s)  day 4 11:30 no. 1 ask water; day 9 08:51 no. 17 ask water; day 10 11:00 no. 23 ask water
  seed  8: 4 knock(s)  day 3 08:15 no. 3 ask food; day 7 16:30 no. 11 ask water; day 8 12:18 no. 20 ask water; day 9 07:51 no. 11 ask water (deferred 1x)
  seed  9: 0 knock(s)
  seed 10: 1 knock(s)  day 10 15:57 no. 8 ask water

SEED 2, days 3 to 10, factor 2.0:
  day 6 09:27: no. 6 (2 people, helper), a woman of about forty, purpose ask_water -> water
  1 visit(s): NOT READY FOR LIVE RUN (fewer than 3)
```

**The factor is 2.0**, the cap. The table shows that a factor is not what limits the knocks: past 1.25 the median
stays at 1. What limits them is whether a household's plan reaches `ask` toward no. 9 at all. The last part of
`schedule.stdout.txt` counts seed 2's street to the end of day 10:
```
  factor 1.0: plans {'ask': 133, 'search': 71, 'stay': 597}; asks that went to a door 29, to 15 houses; to no. 9: 1 (made before day 3 or at night: never)
  factor 2.0: plans {'ask': 131, 'search': 71, 'stay': 599}; asks that went to a door 45, to 20 houses; to no. 9: 1 (made before day 3 or at night: never)
```
(Here nobody answers no. 9's door and its visitor's household then waits on it to the end, so later asks from that household are not
counted.) Doubling the factor sends 16 more asks to doors, spread over 20 houses, and none more to no. 9. Three things set that,
all est. in `population.json`:
- `ask` beats `search` only at high urgency after a search found nothing (§2.3's worked example);
- the target is drawn over every house within reach;
- every household stops asking a house that refused it twice.

Reaching the median of 4 needs one of these changed, not the factor. That is a design decision, and is left to the
user.

**Seed 2's knock is 09:27 on day 6, when it rains** (day 6: 05:27 to 11:03): the kitchen hears knocking, not words
(§0.1, 9).

#### 4. The stranger's lines (amendment 3)

`streetdata/lines.json`, every line, by slot. A line tagged *with: child* is said only by a household with a child, and
*with: others* only by a household of two or more. Code chooses one by
`<seed>:street:<household>:visit<n>:<slot>`.

**voice_ask_water** (10: 8 for anyone, 1 only with a child, 1 only with others at home)

1. Hello? I'm sorry to knock. I've run out of water. Could you spare a little? Even a cup would help.
2. I'm sorry, I know nobody's opening doors. I haven't had a drink since yesterday. Have you any water at all?
3. Please, it's only water I'm after. A cup or a bottle, whatever you can spare.
4. I won't come in. I just need water. Mine ran out and the taps are dry.
5. Sorry to bother you. Is there any water in the house you could spare? I've nothing left.
6. Hello. I'm not here to cause trouble. I'm out of water, that's all. Could you spare some?
7. I heard voices, so I knocked. I've no water left. Anything you could spare, I'd be grateful.
8. It's water. I need water. A little, if you have it. I'm sorry to ask.
9. Please, I've a little one at home and no water left to give her. Just a cup, if you can. *(with: child)*
10. Hello? There's a few of us at home and the water's gone. Whatever you can spare. *(with: others)*

**voice_ask_food** (10: 8 for anyone, 1 only with a child, 1 only with others at home)

1. Hello? I'm sorry to knock. Have you anything to eat you could spare? Anything at all.
2. I haven't eaten in days. I'm not asking for much. A tin, a bit of bread, whatever you have.
3. Please, if there's any food you can spare, I'd be grateful. I won't come in.
4. Sorry to bother you. My food ran out. Is there anything at all you could let me have?
5. I'm not here for trouble. I'm hungry, that's all. Have you anything to spare?
6. I heard voices, so I knocked. I've nothing left to eat. Could you spare a little?
7. Is anybody in? I'm sorry. I've had nothing to eat for days. Anything would help.
8. It's food I'm asking for. Only a little. I'm sorry, I know it's hard for everyone.
9. Please, my little one hasn't eaten properly in days. Anything you could spare, for the child. *(with: child)*
10. Hello? There's a few of us at home and the food's gone. Could you spare anything at all? *(with: others)*

**open_ask_water** (10: 8 for anyone, 1 only with a child, 1 only with others at home)

1. Thank you for opening. I've had no water since yesterday. A bottle would see me through.
2. Thank you. I didn't think anyone would open. Could you spare some water? Only a little.
3. Oh, thank you. I won't keep you. It's water I need, whatever you can manage.
4. Thank you for opening the door. I'm out of water. A cup, a bottle, anything.
5. I'm grateful you opened. I've nothing left to drink. Could you fill one of these for me?
6. Thank you. I know what it costs to open a door now. I just need some water.
7. Hello. Thank you. I'm sorry, I'll be quick. Have you any water to spare?
8. Thank you for opening. My water's gone and the taps are dry. Anything would help.
9. Thank you for opening. My little girl's had nothing to drink since this morning. Just a little water. *(with: child)*
10. Thank you. There's a few of us at home with no water left. Whatever you can spare. *(with: others)*

**open_ask_food** (10: 8 for anyone, 1 only with a child, 1 only with others at home)

1. Thank you for opening. I've had nothing to eat in days. Anything you could spare.
2. Thank you. I didn't think anyone would open. Have you any food? Even a little.
3. Oh, thank you. I won't keep you. It's food I need, whatever you can manage.
4. Thank you for opening the door. I've run out of food. Anything at all would help.
5. I'm grateful you opened. I'm hungry, that's all. A tin, some bread, anything.
6. Thank you. I know what it costs to open a door now. I just need something to eat.
7. Hello. Thank you. I'm sorry, I'll be quick. Have you any food to spare?
8. Thank you for opening. My food's gone. I'm not asking for much, just something.
9. Thank you for opening. My boy hasn't had a proper meal in days. Anything at all, for him. *(with: child)*
10. Thank you. There's a few of us at home and nothing left to eat. Whatever you can spare. *(with: others)*

**insist_water** (9: 8 for anyone, 1 only with a child)

1. Please. Just a cup.
2. Please, I'm begging you. A little water. I won't ask again.
3. I'm asking once more, that's all. Please, any water.
4. Please. I'm so thirsty I can hardly think. Just a little.
5. Anything. A mouthful. Please.
6. I wouldn't ask if I had anywhere else to go. Please, some water.
7. Please. I've tried other doors. Nobody answers.
8. Just a cup, please. Then I'll go.
9. Please. Just a cup. For the child. *(with: child)*

**insist_food** (9: 8 for anyone, 1 only with a child)

1. Please. Anything at all.
2. Please, I'm begging you. A little food. I won't ask again.
3. I'm asking once more, that's all. Please, anything to eat.
4. Please. I'm so hungry I can hardly stand.
5. A crust. Anything. Please.
6. I wouldn't ask if I had anywhere else to go. Please, something to eat.
7. Please. I've tried other doors. Nobody answers.
8. Just a little, please. Then I'll go.
9. Please. Anything. For the child. *(with: child)*

**again_water** (8: 8 for anyone, )

1. I'm still here. I only want a little water, if you can spare it.
2. I'll wait a moment, if that's all right. Just some water.
3. I'm not going to cause trouble. It's only water I'm asking for.
4. Did you hear me? I'm asking for a little water, that's all.
5. Sorry. I'm still here. Any water at all?
6. I understand if you can't. I'm just asking for some water.
7. I'll not keep you long. A little water, if you have it.
8. Hello? I'm still at the door. It's water I need.

**again_food** (8: 8 for anyone, )

1. I'm still here. I only want a little food, if you can spare it.
2. I'll wait a moment, if that's all right. Just something to eat.
3. I'm not going to cause trouble. It's only food I'm asking for.
4. Did you hear me? I'm asking for a little food, that's all.
5. Sorry. I'm still here. Anything to eat at all?
6. I understand if you can't. I'm just asking for something to eat.
7. I'll not keep you long. A bite to eat, if you have it.
8. Hello? I'm still at the door. It's food I need.

**given** (8: 8 for anyone, )

1. God bless you. I won't forget this.
2. Thank you. Thank you. I'll not forget it.
3. Oh, thank you. You don't know what this means.
4. Thank you. Look after yourselves in there.
5. Bless you. I'll go now. Thank you.
6. Thank you. I'll not tell anyone where it came from.
7. That's more than I hoped for. Thank you.
8. Thank you, truly. Stay safe.

**refused_polite** (8: 8 for anyone, )

1. I understand. I'm sorry to have bothered you. Look after yourselves.
2. All right. I understand. Take care in there.
3. That's all right. I'm sorry I asked. Goodbye.
4. I understand. Everyone's in the same boat. I'll go.
5. Right. I'm sorry. I'll try somewhere else.
6. Of course. I'm sorry I knocked. Take care.
7. I understand. Good luck to you.
8. No, I understand. I'm sorry. I'll leave you be.

**refused_flat** (8: 8 for anyone, )

1. Right. Never mind.
2. Fine.
3. Right. Thanks for nothing.
4. I see. Well. I'll go, then.
5. Suit yourselves.
6. Right. I won't bother you again.
7. Fine. I'll find it somewhere else.
8. Right. Goodbye, then.

#### 5. The fake run's door scene

`runs/w2a_impl/fake10.py`: `morning.run(2, fake=True, days=10)` into a temp folder, as `morning.py --seed 2 --fake --days 10`.
Its stdout is `fake10.stdout.txt`, its story `fake10.story.md`, and the summary below `fake10.summary.txt`:
```
morning.run(2, fake=True, days=10): exit 0; asks 490 (fake)
  street day 6 09:27: a visit to the front door from no. 6 (ask water)
day 3: day asks 46; Q7 stretches []
day 4: day asks 48; Q7 stretches []
day 5: day asks 46; Q7 stretches []
day 6: day asks 40; Q7 stretches [('09:27', 6)]
  09:27 Q7 visit v1 (h6, ask_water): fired=True room=kitchen asked=['leo'] why=None
  DOOR SCENE day 6, 09:27 to 09:45: a woman of about forty from h6 (ask_water); heard {'leo': 'heard'}; woken []; outcome ignored; asks 6; give None
    09:27 leo kitchen: go_back_room [model]
    09:30 leo back_room: propose_trip "[fake line 327]" [model]
    09:30 elena back_room: confront_leo "[fake line 328]" [model]
    09:30 mara back_room: go_bathroom [model]
    09:33 leo back_room: silent [fallback]
    09:36 leo back_room: silent [model]
    leo's line of it: At 09:27 you heard knocking at the front of the house.
day 7: day asks 44; Q7 stretches []
day 8: day asks 23; Q7 stretches []
day 9: day asks 31; Q7 stretches []
day 10: day asks 24; Q7 stretches []
door scenes 1; largest Q7 stretch 6 asks; largest day 48 asks
```
The story has it (`fake10.story.md:2130-2132`):
```
- 09:27: a knock at the front door: a woman of about forty from no. 6, ask water (heard by Leo (heard)).
- 09:27: **Q7**, a knock at the front door: Leo asked, in the kitchen.
- 09:27 to 09:48: played turns (Q7, in the kitchen; 6 asks).
```
Leo's day-7 block A has the line `- At 09:27 you heard knocking at the front of the house.` (`fake10.story.md:2264`).

**What this scene shows, read as a scene** (`CLAUDE.md:16-17`), knowing the fake model chooses by a hash:
- Only Leo was awake in the kitchen. It was raining, so he heard knocking but no words, and he went to the back room.
  Nobody answered. Nine minutes later the second knock came, and nobody heard it (the rain masks it in the bedrooms, and
  nobody was in the kitchen); at eighteen minutes she went away.
- **The 6 reserved asks paid for talk in the back room** (a trip proposal, a confrontation), not for the door.
  `begin(stretch, 6, reserved=True)` reserves asks for a stretch, not for the door. If the person asked walks away from
  the door, the reserve goes to whatever the house talks about next. This is the design's Q7 as written (§4.2.4,
  "whose people then choose whether to go to the door"). It is recorded here because W2a-8 counts Q7 stretches, and this
  one counts 6 asks that did not touch the door.

The first fake run, made before the fixes of §6, had a different scene: Leo looked through the gap, then left. Every door
option works in T2, T5 and T7 (give, call, open, refuse, look) and in `door_tokens.py`. In this fake run the door was
never answered, so its lines were never said aloud.

#### 6. Fixes made while building

- **The trip block counted the door's words as outside the budget** (T5, first green attempt: `3771 != 3668`).
  `prompt_parts` counts any growth of the house line beyond `HOUSE_THINGS` into `block`. The door's words now come off
  that count, so they sit inside the budget as §6.3 says.
- **The door lines were 152 tokens, over T5's 140.** The option labels were shortened, and so was the house-line
  addition, to "with a gap in the boards by the front door; the person at the front door".
- **`morning.quiet_line` failed on a Q7 entry** (`TypeError: unhashable type: 'list'`, first fake run): Q7's `asked` is a
  list, as Q6's is. Q7 is now handled first.
- **The rain case** (second fake run): the kitchen in rain was shown "Someone is knocking at the front door" while it had
  only heard knocking. The line now follows what each person heard. The end-of-scene line said "whoever it was" to
  someone who had looked through the gap; it now names who they saw.

#### 7. The replays

**Frozen versions** (`runs/w2a_impl/frozen.stdout.txt`): `v14/check.py` to `v9/check.py`, seeds 1 to 3 each: **18 of 18
story IDENTICAL and transcript IDENTICAL**, six exits 0. Two of the lines:
```
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
```

**v16 seed 2, no API, `--days 10`, a temp copy of cache/v16** (`runs/w2a_impl/premiss.py`, `premiss.stdout.txt`):
```
  street day 6 09:27: a visit to the front door from no. 6 (ask water)
  day 3 07:00 water: tap 105.5 L (bath 59.0, kitchen 46.5), bin 0.0 L, level as_before
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']
exit 3; cache/v16 sha256 before d79a49396e91a3be, after d79a49396e91a3be: unchanged
```
This is the same first miss as v22's premiss (`reports/days_v22.md`, §2). Days 1 and 2, nights 1 and 2 and both night
minds replay from the cache. The street changes nothing before day 3.

#### 8. The full suite

`runs/w2a_impl/unittest.stdout.txt` and `unittest.time.txt`: one run, on the code as committed (after it started, only
`runs/w2a_impl/schedule.py` and this report changed):
```
$ $PY -m unittest test_morning
Ran 297 tests in 389.006s

OK
exit 0
real	6m30.606s
```
No existing test needed a change. The `[429 RESOURCE_EXHAUSTED]` lines in the output are the stubbed
API's scripted errors (`GeminiClientTest`), as in every earlier run; nothing reached the network.

#### 9. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. `$PY` is `.venv/Scripts/python.exe`, run with
`PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1`.
```
$ $PY -m unittest test_morning.KnockTest                       (before any code) Ran 9 tests, FAILED (failures=9), exit 1   red_all.stdout.txt
$ $PY runs/w2a_impl/write_lines.py                             {'voice_ask_water': 10, 'voice_ask_food': 10, 'open_ask_water': 10, 'open_ask_food': 10, 'insist_water': 9, 'insist_food': 9, 'again_water': 8, 'again_food': 8, 'given': 8, 'refused_polite': 8, 'refused_flat': 8}
$ $PY -m unittest -v test_morning.KnockTest                    Ran 9 tests in 10.044s, OK   green.stdout.txt
$ $PY runs/w2a_impl/schedule.py                                exit 0   schedule.stdout.txt (§3)
$ $PY runs/w2a_impl/fake10.py                                  exit 0   fake10.summary.txt (§5)
$ $PY runs/w2a_impl/door_tokens.py                             door_tokens.stdout.txt (§2)
$ $PY runs/w2a_impl/premiss.py                                 exit 3 at day 3, min 00; cache unchanged (§7)
$ for v in v14 v13 v12 v11 v10 v9; do $PY $v/check.py; done     18 × IDENTICAL; 6 × exit 0   frozen.stdout.txt
$ $PY -m unittest test_morning                                 Ran 297 tests in 389.006s, OK, exit 0   unittest.stdout.txt
$ git diff --stat (before the commit)
 chronicle.py 7 +-, data.py 12 +, memory.py 7 +, morning.py 17 +, night.py 4 +, quiet.py 350 +-, story.py 14 +, talk.py 14 +-,
 test_morning.py 356 +, truth.py 18 +-, world.py 63 +-: 11 files, 851 insertions, 11 deletions (plus the new street.py, streetdata/)
```

The commit adds `reports/w2_design.md`, this report, `street.py`, `streetdata/`, the eleven changed files,
`runs/w2a_impl/` and the merged copy of the two reports. Its hash cannot be inside the file it commits, so the hash, the
search for a key in the staged files and `git status` after it are given in the reply. The three old
`runs/v6/daniel_ate_it-seed{1,2,3}.replay.md` stay untracked, as before.

