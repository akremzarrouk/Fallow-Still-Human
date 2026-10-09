# merged: all documents

Merged by `merge-slice-docs.py` from the 2 Markdown files in `Prototypes/llm-morning/runs/w2a_impl/merged/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`w2_design.md`](#w2_designmd)

---

## report.md

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

---

## w2_design.md

### Design: W2, the street and its people

Mode: design. No code was written or changed, the API was not called, and no cache, run, plan or frozen version was
touched. The only file added is this one. Paths are relative to `Prototypes/llm-morning/`. The code is HEAD `da9b0d7`.

- **Read first:** `reports/world_design.md` (§0.2 the architecture, §3 the boundary, §4.5 the population, §4.6–4.7 word
  and rumours, §6 the stages); `reports/days_v22.md`; `reports/v22_gaps.md`; `reports/v22_fixes.md`; `data.py`,
  `world.py`, `night.py`, `quiet.py`, `truth.py`; and, for what they hook into, `morning.py`, `chronicle.py`,
  `memory.py`, `mind.py`, `talk.py`, `water.py`, `weather.py`, `gemini.py`, `config.json`, and `CLAUDE.md:10-28`.
- **How numbers are marked:** `[W:S14]` is source 14 of `reports/world_design.md` §10. `[N3]` is a new source, in §10 here.
  `(est.)` is an estimate: a number with no source, chosen by reasoning, to be changed when a source or a run says
  otherwise. A number from the code cites `path:line`. A thing looked for and absent is **NOT FOUND**.
- **Baselines** for the predictions were counted from `runs/v22` by read-only scripts; the commands, their output and the
  script are in §11 and the appendix.
- **How the design argues.** `CLAUDE.md:18-19` says to argue against a mechanism before proposing it. Each mechanism has a
  paragraph "Arguing against X first". `CLAUDE.md:16-17` says a metric is a clue and not the goal, so §8 also has a
  reading check that is not a number.

#### Summary

| # | Question | The answer in one line |
|---|---|---|
| 1 | Who lives on the street | 30 houses; the family in no. 9, the empty neighbour (no. 7, fixed by `data.py:170`), and 28 others. 8 of the 28 are empty (est.), so **20 households, about 47 people**; 60% helpers, 33% guarded, 5% opportunists, 2% violent. Each holds food, water and a temperament drawn once from strings of its own. |
| 2 | How a household decides | Four times a day, in code only. Six plans (stay, search, trade, approach, take, leave) scored `urgency × gain × chance × temperament − (1 − urgency) × risk × caution`. Cooperation is in the score (ask, offer, trade); danger is in the score (take, fear). Eight findings from disaster research map to eight rules (§2.6). |
| 3 | The noticing rule | One function, `perceive(stimulus, observer)`, used both ways: sound by distance and walls, sight by viewpoint and distance. The family hears a knock, a shout, breaking wood; it sees through one gap in the boards. The street learns of the family only what leaves the house: voices, a door, a person in the yard, an answer at the door. W2a uses the knock only. |
| 4 | Meetings | A knock is a scene: code decides who, when and what they want; the **model decides what the family does** (five door options); the stranger's words come from a **hand-authored line pool chosen by code**, never from the model, in W2a. A person met on a trip is W2c; someone seen from the gap is W2b. |
| 5 | Word, rumours, trips | A deed is a fact that passes between households by `importance × ambiguity` and changes how they plan. A rumour of hope is a structured claim, true with chance 0.3 (est.), never confirmed by code. Trip risk is the people actually out, not `night.py:36-37` (32% scare, 6% not back, alone): about 3% a night trip at first (est.), rising as households run short. |
| 6 | Cost | Door scenes: **≤ 6 asks, ≤ 1 a day, taken from a hard day cap of 56**. v22 spent 402 live asks; W2a expects about 420 and is held to 450 by the run cap. W2a's prompt lines total **≤ 122 estimated tokens** and sit **inside** `PROMPT_TOKEN_BUDGET`. |
| 7 | Stages | W2a knock → W2b the street heard and seen → W2c trips among people → W2d danger at the house → W2e deeds and word → W2f rumours. Only W2a is specified: 1 new module, 3 data files, 11 existing files touched. |
| 8 | W2a predictions | Ten, each with a counting rule and a v22 baseline. **W2a-2: at least half of the heard knocks (and at least 2) are answered, v22 baseline 0 of 0.** The result that proves W2a wrong is in §8.3. |

---

#### 0. What W2 is, and what changes against `world_design.md`

##### 0.1 The evidence

- **The house moves nothing by itself.** 1 outward act on days 3–10: Daniel's `went_out` on night 5 (`reports/days_v22.md:13`; B2 in §11, which also shows `collect_rain` once, so 2 if it is counted).
  W1 made the body honest and put water and rain in the world; the three predictions about going out failed (`reports/days_v22.md:13,15,23`).
- **The talk goes round.** 115 trip-position acts on 5 days and no trip but one (`reports/days_v22.md:207-209`). Mara said one
  frame 7 times on day 3 (`reports/v22_gaps.md:33-68`). In all, 24 of 326 speech acts sit in a repeated text, 14 of them Mara's
  (B4 in §11; `reports/v22_gaps.md:117-123`).
- **Nothing from outside reaches the house.** `knock`, `visitor`, `stranger`, a `Household` and a `Street` are **NOT FOUND**
  in any `.py` (§11, command 2). The street is a four-outcome table (`night.py:36-37`, `79-83`) whose danger is the words
  "something was moving" with nobody in them (`night.py:844-853`). Every place outside is "not to be gone to"
  (`data.py:139`).
- **A line about stakes did not move the house** (`reports/probe_stakes.md:14`, as `reports/world_design.md:45-48`). A heard
  noise that needs no answer is a line of the same kind. What a family moves for is something in front of it that asks
  for an answer now (`reports/world_design.md:82-84`).

##### 0.2 The scope change

`reports/world_design.md:685-708` made W2 "heard and seen only, no contact" and put the knock in W3. This brief puts a reason
at the door first. W2 here is the whole of the street acting on the family; its first stage is the knock.

| `world_design.md` | This design | Why it moved |
|---|---|---|
| W2 the street, heard and seen only | **W2b** | A percept with nothing to answer is the kind of line `probe_stakes` found does nothing. It follows the knock, not the other way. |
| W3 the door (knock, door scene, visitor minds) | **W2a** (knock, five door options, stranger's lines from a pool); visitor minds → a gated option, §4.3 | The smallest slice that puts a reason at the door. |
| (trips: the table replaced by people, in W2) | **W2c** | Needs the street's people first. |
| (danger at the house, in W3) | **W2d** | Needs W2b's perception of the house by the street. |
| W4 word spreads | **W2e** | Unchanged. |
| W6 rumours of hope | **W2f** | Unchanged. |
| W5 sickness, W7 joining | **W5, W7** | Not W2. |

*Arguing against this move first.* The heard-only stage is cheaper and touches no option list. True, and it is W2b. The
case for putting the knock first is that it is the only street event that can be **answered**, so it is the only one whose
effect on the family's acts can be counted by a script (W2a-2 to W2a-5).

##### 0.3 The principles, and where each is kept (`CLAUDE.md:21-28`)

| Principle | In W2 |
|---|---|
| The code owns the truth: what happened, who perceived it, every number | The street, its stocks, plans, knock times, the visitor's need, the goods that change hands, the deeds: all `World` (`truth.py`), unreadable while a prompt is built (`truth.py:34-45`). |
| The AI never owns state | A `door_give` is applied by code and the amount is fixed by code. The family's words about it change no number. The stranger's words are never the model's in W2a. |
| The code draws conclusions from what people perceive; the AI decides what they do | Code writes "a woman's voice at the front door says: ...". The model chooses `door_look`, `door_call`, `door_open`, `door_give` or `door_refuse`. |
| A line that describes an act makes the small model do that act | The new `Now` lines state what is perceived (§4.6, table). Options are acts, as all options are, in a fixed order; which are offered depends on the scene (door shut or open, water in the house), not on how the family feels. |
| Mechanisms may be unhuman; the output must read as human | Plans are scores. What a stranger says is written by a person, in plain speech, and varies with temperament and urgency. |

##### 0.4 Facts the design needs that the data does not have

These are facts about the world, as the back door was in `reports/world_design.md:679-683`. Each has a default; the user may change it.

| # | Fact | Default used here | What it changes |
|---|---|---|---|
| O1 | Can the family see out? `data.py:139` says "the front door and the front windows, boarded up". | **A gap the width of a hand between two boards beside the front door, at eye height**, seeing the step, the pavement and the facing houses' ground floors (11–15 m). | `door_look`, and W2b's sight channel. |
| O2 | Does the family know its neighbours? | **W2a: no.** A visitor is a stranger unless they give a name. (W2b may add: the households within 3 doors on the family's side and 2 across are known by sight.) | How a visitor is described. |
| O3 | Is no. 7 (the neighbour's house) open to the street? | **Not searched by any street household in W2a**, so `night.py:35`'s draw and the family's trips stay as they are. | W2a's trips are unchanged; W2c lifts this. |
| O4 | Opening the front door | **Costs a turn** (it is boarded and barred from inside, `data.py:139`). | Scene timing (§4.2). |

---

#### 1. Who lives on the street

##### 1.1 The street

Built from `reports/world_design.md:526-575` (§4.5), kept where nothing new contradicts it.

| Quantity | Value | Basis |
|---|---|---|
| Houses | **30**: 15 on each side, odd numbers on the family's side | `reports/world_design.md:529` (est.) |
| Frontage | 8 m (est.) | `reports/world_design.md:529`. A narrower byelaw terrace would be 4–5 m, but no source gives the figure: **NOT FOUND** (§10). |
| Carriageway | 11 m between facing houses' pavements | The street width the 1858 Act required [N12] |
| The family | no. 9 | `reports/world_design.md:530` |
| The neighbour's house | no. 7: **empty, fixed by the fiction** | `data.py:170-171`, `world.py:253` |
| The other party wall | no. 11: drawn like any other house | no special case |
| Positions | along the street at 8 m a house; no. 9 at 32 m, no. 7 at 24 m, no. 11 at 40 m; no. 10 across at 32 m | arithmetic |

##### 1.2 Occupied and empty

- **28 houses are drawn**: all but nos. 9 and 7.
- **Empty: exactly 8** of the 28 (`round(0.30 × 28)`; 30% is est., `reports/world_design.md:539`). Which eight is a shuffle by the
  string `f"{seed}:street:empty:{n}"`. With no. 7, **9 houses are empty** at the start. The shuffle is **balanced**, not
  independent, so that every seed has 20 households and the cost of a run does not vary with the draw of the count.
- **Occupied: 20 households.**
- **Why 30% (est.).** With an evacuation order, 78–82% of Orleans Parish left before Katrina [W:S22]. There is no order
  here, so far fewer leave; one of the two houses beside the family, no. 7, already has (`data.py:170`).

| Household size | Share | Expected of 20 | Basis |
|---|---|---|---|
| 1 | 30% | 6.0 | ONS [W:S18], normalised |
| 2 | 35% | 7.0 | [W:S18] |
| 3 | 16% | 3.2 | [W:S18] |
| 4 or more (4: 60%, 5: 30%, 6: 10%, est.) | 19% | 3.8 | [W:S18] |
| **People** | | **46.7** (computed, §11 cmd 6) | arithmetic |

Each person has a sex, an age band (child 3–15, adult 20–64, over 65) and a body. A household has at least one adult;
the second adult has chance 0.7 when the size is 2 or more; the rest are children, and 12% of households have one person over 65 (all est.).
**An envoy** (the person who goes to a door) is the healthiest adult, or else the oldest child of 10 or more; a
household with neither does not send anyone.

##### 1.3 What a household holds

| Store | Draw | Basis |
|---|---|---|
| Food, in days at normal eating, **at the collapse**: under 3: 15%; 3–7: 18%; 7–14: 25%; 14 or more: 42% (uniform to 30) | `f"{seed}:street:food:{n}"` | 82–87% had 3 days; 41–44% had 14 days; about a third a week or less [W:S19]. The band edges are est. |
| Food at played day 1 | the draw less 3 days (floor 0) | three days passed by played day 1 (`reports/world_design.md:540`) |
| Water: bottles U(10, 40) L; a filled bath (150 L) in 50% | `f"{seed}:street:water:{n}"` | Ready.gov 3 gallons a person for 3 days [W:S3]; bath 150 L [W:S12]; the shares est. |
| Water use | the family's own levels `water.LEVELS` (`water.py:13-15`): `as_before`, `careful`, `rationed`, switched by code when the store falls under 3 days, then 1.5 days, of drinking | one set of levels for everyone |
| Taps dry at | `water.DRY_AT` (`water.py:11`) | one world |
| Body | the family's fasting and thirst functions (`quiet.py:108`, `water.py:29`), at household grain | `reports/world_design.md:418` |

Where this puts the street on day 3 (arithmetic, §11 cmd 6): **24% of households have no food left and 25% of the
no-bath households (about 12% of all) have no drinking water**; by day 10, 51% have no food. Nine empty houses hold about
675 L of bath water, 54 L in cisterns and 27 L in bottles, and about 21 portions of food between them (expected values of the empty-house
tables of `night.py:35` and `water.py:34-38`: 2.3 portions a house). That is enough water for the dry households (about 10, at 4.6 L a day)
for about two weeks, and almost no food for 47 people. So the first long-run shortage is **food**, and the first reason to knock on an occupied
house is more likely food than water. Both are drawn.

##### 1.4 Who they are

| Disposition (per adult) | Share | Expected of 20 households | Basis |
|---|---|---|---|
| `helper` | 60% | 12 | Most people in a disaster act prosocially [W:S21; N1; N2] |
| `guarded` | 33% | 6–7 | est. |
| `opportunist` | 5% | 1 | est.; burglary after Katrina may have risen, so not zero [N1, note] |
| `violent` | 2% | 0–1 | 3.9% of a Swedish cohort had a violent conviction; 1.0% had 63% of them [W:S20]; 2% is between |

- **A household's disposition** is that of its decision-maker, the adult with the highest `dominant` draw; a violent adult
  anywhere in the household sets a flag the plan reads (W2d).
- **Temperament** reuses the family's own trait names, drawn U(0.1, 0.9) (est.): `cautious`, `anxious`, `empathetic`,
  `impulsive` (`data.py:23-24`). `cautious` and `anxious` raise caution and fear; `empathetic` raises giving; `impulsive`
  widens the plan's noise.
- **Desperation drifts a disposition** as in `reports/world_design.md:553-557`: 0.05 a day, helper or guarded to
  opportunist, after 7 days without food or 1 without water. Kept slow because looting is rare in acute disasters and a
  long collapse is not acute [W:S21].

##### 1.5 Empty and abandoned houses

- **Abandoned houses** (the 8, and no. 7): `intact`, with a `left_on` (house day 1–3, uniform, est.) and contents drawn
  **when first needed**, once, from the house's own string (as `night.py:385-390`, `chronicle.py:1-4`): the existing
  food table (`night.py:35`: 0/2/4/6 portions at 30/35/25/10%) and `water.house_water` (`water.py:34-38`).
- **States** a house can be in: `intact`, `searched` (emptied), `forced` (W2d). A searched house is not searched twice.

##### 1.6 How it is seeded, and the files

- **One string per draw**, `f"{seed}:street:{purpose}:{house}"`, never a shared generator: a draw does not depend on how many
  came before (as `weather.py:51-52`, `water.py:36-37`). Adding a house changes no other house's draw.
- **Facts fixed once**: a household's size, members, disposition, traits, stores at the collapse. Everything after is a function of
  those and of the code.
- **Files** (plain JSON, no class): `streetdata/street.json` (houses, positions, viewpoints, which house is the family's and
  which the empty neighbour), `streetdata/population.json` (every table above and all weights of §2, one place),
  `streetdata/lines.json` (the stranger's lines, §4.3). The folder is `streetdata/` and not `world/`, because a `world/`
  folder beside `world.py` would be an import hazard (`reports/world_design.md:145` named `world/`).

An illustrative household record (the values are made up, the shape is the design):
```json
{"id": "h13", "home": 13, "members": [{"id": "h13a", "sex": "f", "age": 41, "role": "adult"},
                                       {"id": "h13b", "sex": "m", "age": 9, "role": "child"}],
 "disposition": "helper", "traits": {"cautious": 0.6, "empathetic": 0.8, "anxious": 0.5, "impulsive": 0.3},
 "stores": {"food_days": 4.5, "water_l": 31.0}, "fear": 0.2,
 "knowledge": [{"subject": "house:9", "predicate": "occupied", "value": true, "source": "knew", "at": -4320, "sure": true}]}
```

*Arguing against this first.* Would a real street look like this? Forty-odd people in twenty houses shut in for ten days, a third
of the houses empty: it is a guess at one kind of street. Three things limit the harm. The empty count is one
number in `population.json`. Every house is drawn the same way, so a different street is a different seed and not a different
code path. And no number here is read by a family: they meet one person at a time.

---

#### 2. How a household decides

##### 2.1 Its state

- **Needs**, counted by code from the stores:
  - `dw` = water left ÷ (people × 2.0 L), in days; `df` = food days left.
  - `need_w = clamp(1 − dw/3, 0, 1)` and `need_f = clamp(1 − df/7, 0, 1)` (3 days is the preparedness figure and the
    survival window for water [W:S3, S1]; 7 days is est.).
  - **Urgency** `u = max(need_w, 0.6 × need_f)`. Water counts fully because it is the faster clock [W:S1, S30].
- **Fear** `f` in [0, 1]: starts at `0.1 + 0.3 × anxious` (est.), rises with what it perceives (a forced door, shouting: W2b/W2d)
  and with deeds it hears of (W2e), falls 10% a day (est.).
- **Knowledge**: facts `{subject, predicate, value, source, at, sure}` (`reports/world_design.md:157-163`), here about places
  (`occupied`, `contents`, `searched`) and other households (`kind`, `weak`, `has_surplus`). Priors:
  - a household knows who lives within 5 doors of it on either side and across: *occupied* is true there;
  - beyond, *occupied* is 0.7 (est.);
  - *kind* is 0.6 for any house (the helper share, est.);
  - *contents* of an empty house is 0.5;
  - *surplus* of an occupied house is 0.5.

  A search sets *contents*; an answer at a door sets *kind*; a percept sets *occupied* or *weak* (W2b).

##### 2.2 The six plans

A plan is chosen at the start of each of four parts of the day, 00–06, 06–12, 12–18, 18–24 (est.; real households decide a few times a
day, `reports/world_design.md:187`), by one function with no ask and no World read except through its arguments.

| Plan | What the household does | Off-screen outcome | In W2a |
|---|---|---|---|
| `stay` | nothing | none | yes |
| `search` | goes to an empty house believed unsearched, within 80 m (est.) | takes what is there (stock moves; the house becomes `searched`) | yes |
| `trade` | goes to an occupied house with goods to swap for what it lacks | swap, if the target is willing | no (W2b) |
| `approach` | goes to an occupied house: `ask` (needs), `offer` (surplus, to a house it believes short), `warn` | see §2.5 | `ask` yes; `offer`, `warn` no |
| `take` | at night, to an occupied house believed weak or unwatched; **opportunist or violent only** | W2d | **no** (W2d) |
| `leave` | toward a rumour, or out of town | the household is gone; the house is abandoned | no (W2f) |

Which parts a plan is allowed in: 00–06 `take` only, and `search` when `u ≥ 0.8`; 06–18 all; 18–24 only when `u ≥ 0.6`. People kept to the
dark and to night trips in Sarajevo [W:S27], but only the desperate or the predatory went out in the dark by choice (est.).

##### 2.3 The score

`score(a) = u · G(a) · P(a) · w[d][kind] − (1 − u) · R(a) · r[d]`, and `score(stay) = (1 − u) · 0.3`. The highest wins; a draw of
N(0, 0.03 + 0.05 × impulsive) is added to each candidate by the string `f"{seed}:street:{household}:day{k}:part{p}:noise:{a}"`, so two
identical households differ (all est.). The risk term is multiplied by `(1 − u)` because people take more risk as need rises.

| Term | Meaning | Value |
|---|---|---|
| `G(a)` gain | the share of the household's two-day shortfall that success would cover, 0 to 1 | `search`: 1.0 if a bath is believed full, else 0.4; `ask`: 0.6; `trade`: 0.8 (est.) |
| `P(a)` chance | from **its knowledge**, never from World | `search`: *contents* (0.5 prior, 0.2 after a failed search); `ask`: *kind* × *surplus* (0.6 × 0.5 = 0.3 prior); `trade`: 0.5 |
| `R(a)` risk | base × time × body × (1 + fear) | base: `search` 0.10, `ask` 0.15, `trade` 0.15, `take` 0.5, `leave` 0.4; ×2 at night; ×0.5 in rain; ×1.3 from fasting stage F3 [W:S1] |
| `w[d][kind]` | what this temperament does | `helper`: ask 1.0, trade 1.0, search 0.8, leave 0.7; `guarded`: ask 0.4, trade 0.6, search 1.0, leave 0.5; `opportunist`: ask 0.5, search 1.0, take 1.0; `violent`: ask 0.3, search 0.8, take 1.2 |
| `r[d]` caution | `helper` 1.0, `guarded` 1.6, `opportunist` 0.8, `violent` 0.4, × (0.7 + 0.6 × `cautious`) | |

All weights are est. and live in one table in `population.json`; the first run tests what the street does, not these numbers.

**Worked example** (§11 cmd 6): a `helper` household of 2 with 8 L of water at 06:00. At 2.0 days left, `u` is 0.33: stay scores
0.20, search 0.05, ask −0.06, so it **stays**. At 1.0 day (`u` 0.67): stay 0.10, search 0.23, ask 0.06, so it **searches**. At 0.5 day
(`u` 0.83), after a failed search has taken *contents* from 0.5 to 0.2: stay 0.05, search 0.11, ask 0.12, so it **asks**
the nearest house it believes occupied. A person does not beg before looking for water, and does before dying of thirst.

##### 2.4 Cooperation and danger, in the same function

| Cooperation | Danger |
|---|---|
| `ask` is the usual first move toward an occupied house; a helper's weights are highest there | `take`: only opportunist and violent adults, at night, at a house believed weak or unwatched (off in W2a) |
| `offer`: a helper with a surplus (`dw ≥ 6` days and `df ≥ 10`) and a belief that a house is short, with score `0.4 × empathetic` in place of `u` | `fear`: raises `R` for everyone and, in W2d, turns a guarded household's reply to a stranger at its own door into a refusal or a threat |
| `warn`: tells a house of a danger it has perceived (W2b) | a violent adult's household is flagged and `ask` becomes `demand` at the door (W2d) |
| `trade`: goods for goods, at any temperament but `violent` | desperation drift (§1.4) |
| Acquaintances and neighbours get `+0.15` on `kind` (W2b) | refused twice by a house, `kind` falls to 0.1 for that household, so it stops asking there |

##### 2.5 How an off-screen approach ends

Between two street households, code resolves it at once, so stocks stay conserved and a house that was asked is poorer.
`P(give)` by the target's disposition: helper 0.7, guarded 0.3, opportunist 0.2, violent 0.05 (est.), raised by 0.1 if the asker has a
visible need (a child, thin). The amount is `min(request, 0.2 × the target's surplus beyond 5 days)` (est.). The asker's *kind* for the
target moves by ±0.3. Each outcome is a **deed** (§5.1). An approach **to the family's house** is not resolved by code: it
becomes the door scene (§4).

##### 2.6 What each rule rests on

| Research | What it found | Rule |
|---|---|---|
| Quarantelli; Rodríguez, Trainor and Quarantelli [W:S21; N1] | Prosocial, improvised response was the main response after Katrina, despite media reports of antisocial behaviour; panic and looting are rare | 60% helpers; `take` needs a flagged adult and darkness |
| Frailing and Harper, in the 2007 *Natural Hazards Observer* exchange [N1, note] | Burglary rates after Katrina fit looting being real | 5% opportunists, not 0 |
| Drury, Cocking and Reicher [N2] | In 21 interviews on 11 emergencies, survivors who felt a shared identity described more helping, including of strangers, and more order | A bonus for acquaintances and neighbours (W2b); a gift raises the pair's *kind* |
| Kaniasty and Norris [N3] | After Hugo, those hit hardest received the most help and the help was uneven; their deterioration model says expected support falls after a major event (titles and abstracts only) | `P(give)` rises with visible need; desperation drift; refusal lowers *kind* |
| Thompson [N8] | Residents of Algiers Point, afraid of outsiders, shot and threatened people; the shooters said they were defending against looters | `fear` raises refusal and, in W2d, challenge; ordinary people are dangerous when afraid |
| Lindell and Perry [N9] | A household decides from perceived threat, perceived options and perceived others, and acts if nothing blocks it | The household is the unit; it decides from knowledge and percepts, not truth |
| Sarajevo: FAMA survey; Andreas [N10; W:S27] | Neighbours shared a well and queued for water, traded small goods (that detail from a tour operator's page: illustrative), and kept to the dark | `trade`; night avoidance |
| Knapp; Allport and Postman [N5; W:S23] | Wish rumours, fear rumours and wedge rumours; fear travels more readily; detail is lost in retelling | §5.2 |

##### 2.7 What decides in W2a

`stay`, `search` and `ask` only, with `P(give)` in §2.5, and no perception of the family (the priors of §2.1 stand for
the family's house too). Everything else in this section is built in later stages.

*Arguing against this first.*
- **A clock is not how a person decides.** Real decisions are triggered by events (thirst, a noise). The four parts are an economy. An event
  (a perceived forced door, W2b) re-runs the plan at once; W2a has no such event.
- **Would a real household score?** It would weigh the same things in other words: how badly it needs the thing, how likely it is to get it, how
  safe it is. The numbers are the part nobody can source, so they are kept in one table and tested by what the street does.
- **Does `ask` target the family by luck or by design?** By the same score as every other occupied house; the family's house has no weight
  of its own in W2a, only the nearest-first effort of distance (the nearest doors are asked first, as people do).
- **Is the knock rate a dial?** One global factor, `approach_trips` (est. 0.3–0.5 a day per short household), is set **once**, over seeds
  1 to 10, so that the median is 4 knocks on days 3–10 and no seed exceeds 8 (§6). It never reads the family. The arithmetic before
  calibration gives 1–3 knocks in 8 days (§11 cmd 6, est.), so the calibration raises the street's rate to give the test at least three
  chances. This is a cost and a test-power decision and is recorded as such.

---

#### 3. The noticing rule

##### 3.1 One function, both ways

```
perceive(stimulus, observer) -> percept | None
stimulus = {t, from_place, sense: "sound" | "sight", level, kind, actor}        # actor is truth only
observer = {place, viewpoint, awake, ambient, anxious}
sound:  L = level − 20·log10(max(d, 1)) − Σ barriers − 0           heard if L ≥ ambient; words if L ≥ ambient + 10
sight:  seen if the observer's viewpoint sees from_place and d ≤ range(light); known if d ≤ 10 m by day
asleep: woken with chance min(0.9, 2 × (0.10 + 0.20 × anxious))  (a knock; `night.py:317-319` has the door's), else nothing
```

It serves the family and the street with the same code. The percept is **written by code in perception words** (what a
person hears or sees, never who it was), as `reports/world_design.md:253-259`.

##### 3.2 The constants

| Constant | Value | Basis |
|---|---|---|
| Spreading | 6 dB per doubling of distance | [W:S14] |
| Closed window (boarded: 25) | 27.8 dB(A) | [W:S14]; boarded 25 is est. |
| Party wall | **45 dB** (DnT,w + Ctr) | Approved Document E, new-build houses; 43 for conversions [N6]. An older solid-brick wall may be better (not found) |
| The barricaded front door | 25 dB (est.); a closed inner door 15 dB (est.) | est. |
| Ambient at the listener, indoors | day 25, night 20, **rain 35** (est.) | A quiet rural night is 30 dB(A) outdoors and moderate rain 50 [W:S14]; the roof and boards take about 15 off the rain (est.) |
| Speech at 1 m | normal **58**, raised **64**, loud **70**, shout **76** | the ESTA table of vocal effort; ANSI S3.5 gives higher overall levels; Pearsons et al. 55–66 dBA in homes [N7] |
| Footsteps 50; a knock **70**; forced door or breaking glass 85 | | est. (a shouting level and a knock level were looked for: only speech was found) |
| Light for sight | by day a figure's sex, age band and what it carries are seen to **30 m** (est.), who it is to **10 m** (est.) | Detail is lost with distance as with blur: eyes cannot be seen at 200 ft [N4]; the figures are est. |
| At night | by full moon (0.1–0.25 lux, [W:S16]) shapes to 20 m (est.); at new moon only a person's own light | est. |
| Daylight | sunrise 07:01 and sunset 18:37 on 1 Oct 2026; sunset about 18:18 on 10 Oct (est., 2 min a day) | [N11] |

##### 3.3 What the family hears and sees of the street

The levels come from §11 cmd 5. "Words" means ambient + 10 dB.

| Stimulus | At the listener | Result | The percept the family gets |
|---|---|---|---|
| A knock, from the kitchen (2 m, door 25) | 39 vs 25 by day | **words** | "Someone is knocking at the front door." |
| A knock, in a bedroom 6 m away, its door open / shut | 29 / 14 | heard / not | "You hear knocking at the front of the house." / nothing |
| Talk on the pavement 3 m from the gap | 48.5 | words | the words |
| Talk across the street, 10 m, boards | 13 | not heard | nothing |
| A shout 10 m away: day / night / rain | 31 vs 25 / 20 / 35 | heard / words / not | "a voice shouting outside" / "a man's voice shouting: ..." / nothing |
| A forced door three houses along: night / rain | 32 vs 20 / 35 | words / not | "wood splintering, a few houses along" / nothing |
| Footsteps 3 m outside the boards / at the gap | 15.5 / 40.5 vs 25 | not / words | nothing / "footsteps on the pavement" |
| A loud voice through the party wall, 3 m | 15.5 vs 20 | not heard | nothing |

- **By sight**, only through the gap (O1): the step, the pavement and the facing ground floors. A figure by day is seen with its sex, age
  band and what it carries within 30 m; it is known within 10 m.
- **Rain masks.** The ambient rises 10 dB, which removes the shout and the forced door above. That is one rule (§3.1) and it is
  already in the physics of W1 (`reports/world_design.md:326-329`).

##### 3.4 What the street learns of the family

| What leaves the house | Stimulus | The street, by the same function |
|---|---|---|
| Quarrelling voices (`confront`, `accuse`, `deny`, `object`: raised, 64; `reassure`, `say`: normal, 58; at night all low, 50) | sound | A neighbour 4 m from the boarded front window hears the raised voices by day (27 vs 25, no words); no. 11 through the party wall hears nothing. At night the family's low voices are not heard (13 vs 20). **The family's silence protects it.** |
| The front door opening at night | sound 60 (est.) | a neighbour awake in a house with a view hears "a door" |
| A figure in the yard (`collect_rain`, W1) | sight, from the back windows of houses behind | "no. 9 has a bin out": *has_surplus* up |
| A trip out and back, carrying water | sight, in daylight; rarely at night | *has_surplus*, *weak* |
| A candle through the gaps | sight, 30 m | **NOT FOUND** in the data: `data.py:135-141` lists no light, so the house is dark |
| An answer at the door | contact | *occupied*, *kind*, *has_surplus* (`door_give`), *weak* (what the envoy sees when it opens) |

**What W2a uses of this:** the knock (§3.3 row 1–2) and what the envoy sees when the door is opened. The household's belief about
the family's house is its prior (§2.1) plus the outcome of its own earlier visits. The other rows are W2b.

*Arguing against this first.* A single decibel rule for everything is crude; a real house hears a lot more than this, and sound
travels in a terrace better than 45 dB suggests (the 45 is a test figure for new walls and says nothing of flanking paths). Three limits
keep it honest: every constant is in one table; the rule can be switched on one sense at a time (W2a sound only); and the one place
where a mistake would matter, whether the family hears a knock, is tested directly (the kitchen hears it, a shut bedroom does not).

---

#### 4. Meetings

##### 4.1 What is code, what asks the model, who writes the stranger

| Meeting | Stage | Code decides | Asks the model | What the stranger says, and who writes it | Asks |
|---|---|---|---|---|---|
| **A knock at the door** | W2a | who comes, when, what they need, how they react, what changes hands | the family: five door options, plus the family's ordinary options | **A hand-authored line from a pool, chosen by code** by purpose, urgency and temperament (§4.3) | ≤ 6 a scene, ≤ 1 a day |
| **Someone seen from the gap** | W2b | whether anyone passes; what is seen (§3.3) | nobody, unless the house is already talking | nothing is said; a `Now` line of what is seen | 0 |
| **A person met on a trip** | W2c | who is out and where; the outcome | the leaver (and a companion): 2 options | from the same pool kind (`street` slots); model-written only after the gate in §4.3 | ≤ 2 an encounter |
| **A person at the back door, at night** | W2d | the approach, the noise | the sleepers and watchers | words only if the person speaks (`demand`, `plead` slots) | ≤ 4 an event |

##### 4.2 The knock, step by step (W2a)

1. **Before the day.** When the street is advanced to a day part (`street.advance`), a household whose plan is `ask` toward no. 9
   gets a **visit**: `{household, envoy, purpose (ask_water | ask_food), at, state}`, with `at` on the 3-minute grid inside 07:30–17:30
   (daylight, with an hour in hand), uniform within its part (the string `f"{seed}:street:{h}:day{k}:visit"`). The first visits of a
   seed are fixed by the seed alone in W2a (nothing the family does moves them), so they can be **printed before the run**, as the weather
   was (`reports/days_v22.md:308`).
2. **The minute `at`.** Only on a quiet day (day 3 on). Conditions: fewer than 52 asks spent, no visit yet today, someone awake or woken.
   Otherwise the visit is **deferred** to the next part (logged; W2a-1 counts deferrals).
3. **The knock** is a stimulus of 70 dB at the front door. For each person: awake and not in the bathroom, `perceive` (§3.3); resting, a wake draw
   (§3.1). Whoever perceives it gets `p.door = {"state": "knocking"}`, which adds the `Now` line (§6.3) and the door options for anyone
   **in the kitchen**; others have `go_kitchen` as always.
4. **Q7.** `Quiet.hear_knock`, the sibling of `hear_rain` (`quiet.py:342-381`): if the house is already playing a stretch, the knock is a trigger
   inside it and its cap grows by the reserved allowance; otherwise it plays the **kitchen** if anyone awake is in it (the door is there), else the room with most awake
   (whose people then choose whether to go to the door), `begin(stretch, 6, reserved=True)` (`quiet.py:393-397`) and `ask`s everyone awake in that room.
   Skipped, as Q6 is when `rain_action` is false for all (`world.py:738-740`; `reports/v22_fixes.md:79-83`), only if nobody is awake after the wake draws.
5. **Played turns (3 minutes each).** What each option does:
   - `door_look`: a sight percept to the actor (§3.3), nothing else changes.
   - `door_call` (speech): the words go through the door; the visitor replies **next turn** with a `voice` line.
   - `door_open`: this turn unbars it (O4); next turn the envoy is on the step, described, and says its `open` line.
   - `door_give`: only if the visitor asked for water and the house holds any; code moves `min(3 L, store)` out of the kitchen's tap water (then the bin,
     the order of `truth.py:91`) into the household's stock; the visitor says `given` and leaves.
   - `door_refuse` (speech): the words; the visitor says `refused` and leaves.
   - nothing for 3 turns: a second knock (heard again, same draws); nothing for 6: it stops, "footsteps go away along the street"; the visitor leaves.
6. **After.** The visit is a **deed** (§5.1) in `World`; the household's stock, *kind*, and *has_surplus* for no. 9 are updated; the chronicle gets
   `knock`, `door_line`, the family's door acts, and `door_end`; each person who was at the door gets one `sure` line of the outcome ("you handed a woman at
   the door two bottles of water"); the stretch closes.

##### 4.3 The stranger's words

- **Who writes them in W2a: a person, once, before the run.** `streetdata/lines.json` holds, for each **slot**, at least 8 variants (est.):

  | Slot | When | Example lines (to show the register; not the pool) |
  |---|---|---|
  | `voice_ask_water` | the door is shut | "Hello? Is anybody in? I'm sorry. We've run out of water, and I've a little one at home." |
  | `voice_ask_food` | the door is shut | "Hello? Have you anything to eat you could spare? Anything at all." |
  | `open_ask` | the door is open | "Thank you for opening. There's two of us, and we haven't had a drink since yesterday. A bottle would see us through." |
  | `insist` | `u ≥ 0.8`, a second ask | "Please. Just a cup. For the child." |
  | `given` | after `door_give` | "God bless you. I won't forget this." |
  | `refused_polite` / `refused_flat` | after `door_refuse`, by temperament | "I understand. I'm sorry to have bothered you. Look after yourselves." / "Right. Never mind." |

- **Rules for a line:** at most 25 words; no house number and no weekday; nothing outside the family's known world (no radio, no police);
  never says what the family should do or must feel (a request is allowed, a duty is not); it states a need the household really has
  (the envoy's `ask_water` means the household's `need_w` is above 0.5). A line is chosen by
  `f"{seed}:street:{h}:visit{n}:{slot}"`, so a seed always hears the same stranger.
- **Why not the model.** The principle is that the AI owns words (`CLAUDE.md:22-23`), and a stranger is a person. But in the first test the
  question is what the family does with a reason at the door, and a model-written stranger varies the reason from run to run, can
  invent state ("I have a gun"), and costs 2 more asks a scene. A pool keeps the stranger a fixed input and the family the only thing that varies.
- **The gate to model-written strangers** (called "visitor minds" in `reports/world_design.md:640`): switch a slot when a W2a or later run
  shows either (a) a stranger's line repeated word for word in a run, or (b) the family answering two different strangers in
  the same words. Then a stranger gets its own prompt: its sheet, its household's needs as situations, what it sees at the door, and options by
  disposition (`reports/world_design.md:640`); the code still owns what it wants and what it does.
- **Arguing against the pool first.** Would a real person speak like a table? No: that is why variants depend on temperament and urgency and why the pool
  is written by hand and read in the reading check (§8.4). A visitor who cannot answer what the family says is also unhuman: after a `door_call`, the
  stranger answers the *kind* of act (call, open, give, refuse, silence), because code does not read free words
  (`talk.py:68`), so a stranger never hears "go away" as different from "we cannot help".

##### 4.4 A person met on a trip (W2c)

At the night's trip (`night.py:766-858`), the table `ALONE/GROUP` (`night.py:36-37`) and the body shifts (`night.py:81-83`) go, and the
street's people who are out in that window and whose path comes within sight range are met in time order, at most 2. The leaver (and anyone with them)
is asked once, with options `hide`, `go_on`, `call_out`, `turn_back`, `run`; the other's act is its plan's (§5.3). One more ask if words are
exchanged. This reuses `Night.ask` (`night.py:427-448`), which already takes a `now` list and options.

##### 4.5 Someone seen from the gap (W2b)

A passer within 30 m of the gap in daylight becomes a `Now` line for whoever is awake in the kitchen, and a memory line (trimmable). It starts no stretch
and asks no one: it enters the talk when the house is already talking (as the rain does in played turns, `quiet.py:358-363`). Its cost is
the lines it displaces.

##### 4.6 What the prompt says, and what it does not

| Line | Says | Does not say |
|---|---|---|
| "- Someone is knocking at the front door." | a sound, where | what to do about it, who it is, that it is urgent |
| "- A woman's voice at the front door says: ..." | what was heard | who she is, what she wants beyond her words, that she is telling the truth |
| "- The front door is open. A woman of about forty stands on the step, thin, holding two empty bottles." | what is seen | that she is desperate, harmless or dangerous |
| Options: `door_look`, `door_call`, `door_open`, `door_give`, `door_refuse` | five acts, in a fixed order | which is right; they are offered whatever the family's state, except that `door_give` appears only if there is water to give and `door_open` only if the door is shut |

---

#### 5. Word, rumours, and risk on trips

##### 5.1 Word spreads (W2e)

- **A deed** `{t, from, to, kind (gave | refused | ignored | spoke | took | threatened), qty, place, witnesses}` is written by code whenever a
  household acts on another, and by W2a at every door. Its witnesses know it first-hand.
- **Households meet** when two are at the same place in the same part: next door through a wall once a day while both are home (est.), at a
  water source, on the street. At a meeting a household passes a fact about a third party with chance `i × a` (`importance × ambiguity`,
  after Allport and Postman [W:S23]): `i` = 1 for food, water and danger, 0.5 for kindness, 0.2 otherwise; `a` = 0.6 for a fact told on,
  0.3 for one seen (est.). A household stops passing a fact when it hears it from one who knew (Daley–Kendall [W:S24]).
- **Each hop** drops a detail with chance 0.2 and sharpens a number with chance 0.2 (est.; about 70% of details were lost in 5–6 retellings [W:S23]).
- **What a fact changes:** the hearer's beliefs (*kind*, *weak*, *has_surplus*), hence `P(a)` and `R(a)` in §2.3. A house known as kind gets more
  `ask` visits; one known as dangerous gets fewer; one known as weak and rich draws `take` (W2d).
- **What reaches the family:** only consequences. A visitor who says "they told me you gave the Okafors water" is speaking from its
  knowledge, which may be wrong in the ways above.

*Arguing against this first.* Do people really pass on who is kind? Yes: it is the main use of a neighbour's good opinion in a long
shortage. Does it make the family's kindness cost them? Yes, and that is what a real family would find: giving brings more knocks.

##### 5.2 Rumours: the only kind of hope (W2f)

- A rumour is a **structured claim** `{kind: aid_point | food_source | safe_route | exit, place, day}`, drawn at world creation from
  `streetdata/rumours.json`, with an origin household (one that heard a radio voice, saw a far light or met a passer; the family has no radio,
  `data.py:135-141`).
- **True with chance 0.3** (est., no source); drawn once. If true the place exists off the map at a distance (est. 3–10 km), a household that
  `leave`s toward it is out of the street for good, and whether it found anything is **never told** to anyone: hope stays hope.
- **How it spreads:** like word, with `i = 1`, but a *fear* rumour travels 1.5 times as readily as a *hope* rumour (est., from Knapp's finding that
  negative rumours were more likely to be passed on [N5]).
- **How it reaches the family:** a visitor's aside at the door ("they say there's bread at the church hall"), voices in the street heard
  (§3.3), or a household seen leaving with a handcart. Each is a `Now` line and a stranger's line; the family decides.
- **Not a reward:** no rule reads the family's state to send them a rumour (§2.2 of `reports/world_design.md`, "No storyteller").

##### 5.3 Risk and death on trips, from people (W2c, W2d)

The table at `night.py:36-37, 79-83` (alone, next door: 14% `scare_there`, 18% `scare_back`, 6% `not_back`, 62% clean) stands in for a street nobody
has drawn. With the street:

- **An encounter** needs a household member out in the same window within sight range of the leaver's path (§3.2). The street's people are out by plan: by
  day a household sends someone out on a trip about 0.4 times a day, for about 40 minutes (est.); at night only `take` plans and the desperate (§2.2).
- **The outcome** is the pair of choices: the leaver's (model) and the other's plan (code). A helper greets or asks; a guarded person avoids; an opportunist
  follows or demands; a violent one attacks. The leaver escapes with a chance that falls with the family's fasting stage (walking speed ×0.7 from F3, [W:S15, est.]).
- **Injury and death** come from the violence of an encounter and from the existing fall at night with no moon (3% a trip, `reports/world_design.md:519`),
  not from the table. Infection and care are W5.
- **What it comes to** (arithmetic, §11 cmd 6): about 0.44 street persons out at a daylight minute, so an encounter on a 20-minute daylight trip is about 0.3;
  at night, about 3% (est.), against the table's 38% of trips that are not clean. **The first days' trips become much safer than the table says and become dangerous as households run
  short.** That is a truth of the world the family has never been told, and it is W2c's to test, not W2a's.

*Arguing against this first.* If trips are safe, the family may go too readily. The table was not truth; it was a stand-in for a street nobody had made. If the street is
quiet, a family that stays in is afraid, not prudent, and the family can find that out, which a real family would.

---

#### 6. Cost

##### 6.1 Asks in a day

| Source | v22 | W2a | Rule |
|---|---|---|---|
| The morning's played turns | 24 | 24 | `quiet.py:44` |
| Q1/Q2 stretches, within the day's 40 | 8 each | 8 each | `quiet.py:43` |
| Q5 the evening, reserved | ≤ 8 | ≤ 8 | `quiet.py:48` |
| Q6 rain, reserved | ≤ 8 | ≤ 8 | `quiet.py:88` |
| **Q7 the door, reserved** | none | **≤ 6, ≤ 1 a day** | new |
| **Day cap** | implicit 56 | **`DAY_MAX = 56`**, checked in `spent()` (`quiet.py:384-388`) | new; priority by time |
| Worst case without the cap | 56 | 62 | |

- **Why 6.** The first turn asks everyone awake in the room, 2.16 persons on average at a daylight minute (B7 in §11), the second asks those still engaged, so a
  scene costs about 4.5 asks (est.). A reserve of 6 covers two turns of three.
- **Why Q7 is not starved.** A knock is only between 07:30 and 17:30; Q5 starts at 19:00 (`quiet.py:48`), so Q5 comes after it. Where Q6 and Q7 meet, whichever begins
  first has its asks first. A visit that would begin with fewer than 52 asks spent is deferred, not run with no one to ask (§4.2.2).
- **v22's busiest day** (day 9): morning 24, Q2 8, Q6 8 (= 40 by 14:00), a knock at 14:00 adds ≤ 6 → 46, Q5 adds 8 → 54 ≤ 56. No starvation (B3, B12).

##### 6.2 A 10-day run

| | v22 | W2a, expected | W2a, bound |
|---|---|---|---|
| Day-scene asks, days 3–10 | 342 | 342 + about 4 scenes × 4.5 = 360 | 342 + 8 × 6 = 390 |
| Night asks, nights 3–9 | 32 | 32 (nights untouched) | 32 |
| Night-mind asks, minds 3–9 | 28 | 28 | 28 |
| **Live total** | **402** | **about 420** | **450** |

The bound of 450 holds if the non-door asks do not exceed v22's. It is **enforced** by the run's own cap, set to 450, not 470 (`runs/v22/run_capped.py`); the run
stops cleanly there and resumes from its cache. The busiest calendar day in v22 was 56 asks (day + night + mind, days 8 and 9; B11), so the day cap of 56 and the run cap
are separate limits. A day scene stays far under the per-scene call cap of `config.json` (`max_calls_per_morning` 150).

##### 6.3 The prompt lines, and why each is inside the budget

`PROMPT_TOKEN_BUDGET = 1400` (`world.py:79`) counts everything except `block` (`world.py:1167-1183`): the trip block, the carry (blocks A, B, C, bounded to
560 by `memory.MEMORY_MAX`, `memory.py:9`) and W1's water line and options. The trimming loop then cuts "What else happened" lines and "days before" lines
until the rest fits (`world.py:1185-1203`). **None of W2a's lines is added to `block`.** They are `Now` lines (`world.py:1123-1124` is where the rain's is added)
and options, which `block` does not count unless their ids are in `W1_OPTIONS` or `TRIP_KINDS`.

| New line | Est. chars → tokens | When |
|---|---|---|
| "- Someone is knocking at the front door." | 40 → 12 | the knock, in the kitchen |
| "- You hear knocking at the front of the house." | 46 → 13 | elsewhere |
| the stranger's words line | 120 → 34 | after a call |
| "- The front door is open. A woman of about forty stands on the step, thin, holding two empty bottles." | 101 → 29 | door open |
| `door_look`, `door_call`, `door_open`, `door_give`, `door_refuse` | 69, 77, 42, 71, 85 chars → 20, 22, 12, 20, 24 | the options offered (4 at most at once) |
| **Closed door: knock + voice + 4 options** | 439 → **122** | |
| **Open door: open + voice + 2 options** | 381 → **106** | |

- **Where the room comes from.** At v22's largest prompt (day 9, Daniel; 2602) the trimmable part was the "What else happened" lines (55 tokens, 2 lines left)
  and the loose "days before" lines (117 tokens): **172 tokens** (`reports/v22_gaps.md:243,248`). A scene's 122 tokens fit inside that. The estimate does not grow; older memory is
  cut instead. Where nothing trimmable is left, the loop ends and the prompt overshoots (`world.py:1193`); that is why W2a-9 allows 2650.
- **No standing line.** A "people at the door" count line would sit in every later prompt (inside, not trimmable) at about 42 tokens; it is **left out** of W2a.
- **The next day.** A scene's lines reach block A as one `Yesterday` line and block C by `memory.WEIGHT` (`door_give` 4, est.), inside the existing 560-token bound
  (`memory.bounded`, `memory.py:234-265`): they displace, they do not add.
- **The night mind** sees a scene as up to 4 records among its limit of 1600 tokens (`mind.py:31`), with quoted words dropped from the oldest first.

---

#### 7. Stages

##### 7.1 All of W2, in order

| Stage | Adds | Answers | New asks | Live test |
|---|---|---|---|---|
| **W2a** the knock | the street (generated, planned, resolved in code), the knock by day, the door scene, five door options, the stranger's lines from a pool, deeds, Q7 | v22: nothing from outside reaches the house (§0.1) | ≤ 6 a scene, ≤ 1 a day | v16 seed 2, `--days 10` |
| **W2b** the street heard and seen | `perceive` both ways in full; the gap; rain masking; the street learns of the family (§3.4); `trade` and `offer`/`warn`; acquaintance (O2) | W2a's answer on whether a prior of "occupied" is enough; 24% of houses with no food (§1.3) | 0 | a run with forced passers in daylight and a forced shout at night |
| **W2c** trips among people | `night.py`'s tables and body shifts replaced by encounters; a person met on a trip | `night.py:36-37,79-83`; "something was moving" | ≤ 2 an encounter, ≤ 1 a night | a seeded run, plus a forced encounter |
| **W2d** danger at the house | `take`, the back door and the yard at night, fear and defence, `demand`; the family's night reactions; wounds (W5 stub) | the 5% and 2% of §1.4 | ≤ 4 an event, ≤ 1 a night | forced cases (a person in the yard at 02:00) |
| **W2e** deeds and word | meetings, `i × a` passing, reputation in plans | how the family's treatment of people travels (`reports/world_design.md:710-715`) | 0 | two runs differing in one forced deed on day 3 |
| **W2f** rumours of hope | §5.2 | no reason in `probe_stakes` speaks of a place to go (`reports/world_design.md:726-731`) | 0 | a seeded run |

The gates between them: W2b needs W2a's report to show at least one answered knock; W2c needs W2b's `perceive`; W2d needs W2b; W2e needs W2a's deeds and at least one given or refused
visit; W2f needs W2e's meetings. W5 (sickness) and W7 (joining) stay where `reports/world_design.md:718-738` put them.

##### 7.2 W2a, the smallest slice that puts a reason at the door

**What it builds:**
- The street of §1, generated once per seed, and advanced lazily in four parts of the day, from played day 1 in code. **Its percepts reach the family from day 3 on**,
  because days 1–2 replay from `cache/v16` (`reports/v22_fixes.md:18-19`), as W1 did.
- Plans `stay`, `search`, `ask` (§2.7); the off-screen exchange (§2.5); the visit (§4.2); deeds. Before day 3 no household may choose no. 9 as a target (its
  other plans run), so no visit is lost and none is half-made.
- Q7, the five door options, the pool of stranger's lines, the day cap.

**What it does not build:** the noticing of the family by the street, `trade`, `offer`, `warn`, `take`, `leave`, night visits, rumours, word between
households, trips among people, a model-written stranger, a standing line, a change to the family's minds, bodies or water (all out of scope).

**New files:**

| File | Holds |
|---|---|
| `street.py` | Pure functions over plain dicts: `generate(seed, street, pop)`, `advance(state, to_minute, weather)`, `plan(household, part, draw)`, `resolve(approach, state)`, `due_visits(state, window)`, `visit_step(visit, family_act, draw)`, `perceive(stimulus, observer, constants)`. Every random value comes from one argument, `draw(string) -> float`, so only one function would change in a port. The weather enters as a value (wet or dry), never as a `World` read. |
| `streetdata/street.json`, `population.json`, `lines.json` | §1.6; all constants and weights; the pool |
| `runs/w23/scoring/w2a_score.py`, `schedule.py`, `selfcheck.py` | the scorer, the no-API schedule print, checks on a fake run |

**Existing files touched:**

| File | Change |
|---|---|
| `truth.py` | `World.street` (the state, guarded by `Guarded`, `truth.py:34-45`); the street is advanced from `Quiet.tick`, **not** from `World.advance_to`, so the copy `next_change` makes (`truth.py:147-161`) stays cheap |
| `quiet.py` | `Quiet.tick` (`:255`) advances the street; `world_events` (`:740`) and `next_event` (`:718`) add the next visit; `step` (`:702`) calls `hear_knock`, new (sibling of `hear_rain`, `:342`); `turn` (`:760`) the played branch; `play` (`:961`) starts the Q7 stretch with 6 reserved; `spent` (`:384`) gets `DAY_MAX`; `sense` (`:295`) sets `p.door`; `items` (`:919`) and `transcript` (`:945`) record the knock and the street log |
| `world.py` | `Person.door` (`:304`); `options_for` (`:532`) the five door options (like the one at `:595-597`); `_prompt_for` (`:1086`) the door `Now` lines next to `:1123`; `apply` (`:1635`) the door kinds, with a case like `collect_rain`'s (`:1833-1844`); `KIND_DONE` (`:98`) and `line_text` (`:1577`) |
| `talk.py` | `SPEECH` (`:8`) gets `door_call`, `door_refuse`; `act_of` (`:15`) leaves the door ids as their own kinds; `Newness` (`:64`) treats a door act as new the first time in a scene |
| `data.py` | `HOUSE_THINGS` (`:135`): a variant for door scenes naming "the people at the door" (as `with_yard`, `:150`), because the house line says "Do not mention any other object or place" |
| `chronicle.py` | `gist` (`:24`) phrases for `knock`, `door_*`; `KEYS` (`:13`) unchanged |
| `memory.py` | `WEIGHT` (`:17`) and `person_line` (`:158`): the door deeds in block C |
| `night.py` | `carry_in_later` (`:1006`): one line for yesterday's door scene in block A. **Nothing else**: bedtime, trips and the street tables stay |
| `story.py` | the Q7 rows beside Q6's (`:604-611`) |
| `morning.py` | print the seeded first-visit schedule beside the weather (`:137-143`); `quiet_line` (`:197`) and `quiet_meta` (`:90`) know Q7 |
| `test_morning.py` | the tests below |

**Tests, written first:**
1. T1 `generate` is deterministic and independent of order; adding a house changes no other draw.
2. T2 stocks are conserved across every exchange and every `door_give`.
3. T3 a `TruthLeak` is raised if a prompt builder reads `World.street`.
4. T4 days 1–2, nights 1–2 and day 3's first ask replay byte for byte from `cache/v16` (the premiss script, `reports/days_v22.md:316-318`); frozen v9–v14 replays are identical (18 of 18).
5. T5 for any prompt, `block` is the same with and without a door state; the door lines total ≤ 140 tokens.
6. T6 a knock at 07:30–17:30 only; ≤ 1 a day; deferred when 52 asks are spent; never in the bathroom; a resting person wakes by the draw.
7. T7 the door options exist only in a scene, in the kitchen; `door_give` only with water to give; `door_open` only when shut.
8. T8 the Q7 stretch ≤ 6 asks, and the day ≤ 56.
9. T9 every stranger's line in the pool is ≤ 25 words, has no digit or weekday, and no word from a list of what the house does not have.

**The live test:** v16 seed 2, `--days 10`, `cache/v23` copied from `cache/v16` (as v22 did), through a capped runner at 450. The plan, with the printed first-visit
schedule and the scorer's sha256, is written and hashed **before** the first live ask, as `runs/v22/plan_frozen.txt` was. The user supplies the key for that run.

---

#### 8. W2a's frozen predictions

##### 8.1 The run and how it is counted

- **The run:** the live test of §7.2, scored on days 3–10 and nights 3–9.
- **The scorer** is `runs/w23/scoring/w2a_score.py`, built on `runs/w22/scoring/w1_score.py`'s rules, run on a fake run, and checked to reproduce v22's column.
- **Regexes (case-insensitive):**
  - `FOLK = \b(knock\w*|stranger\w*|visitor\w*|at the (front )?door|woman|that (man|boy|girl|child)|the (boy|girl|child)|whoever (knocked|is outside))\b`
  - exact repeat: the same person, the same day, the same words after lower-casing and stripping punctuation, at least twice (the rule of `reports/v22_gaps.md:101`).
- **"Heard"** is a chronicle event of kind `knock` with at least one witness `heard` or `saw`. **"A door act"** is one of `door_call`, `door_open`, `door_give`,
  once per person per scene. **"Answered"** is at least one `door_call` or `door_open` in the scene.
- **NOT TESTED:** if no knock is heard (W2a-1 fails), W2a-2 to W2a-5, W2a-7 and W2a-10 are NOT TESTED, not failed.

##### 8.2 The predictions

| # | Prediction | Counting rule | v22 baseline |
|---|---|---|---|
| **W2a-1** | **The street knocks by itself.** At least 3 knocks are heard, on at least 3 different days of 3–10. At most 1 knock is deferred. | `knock` events of scenes D3–D10 with a witness `heard`/`saw`; deferrals from the Q7 log | **0**: no such kind (B1; §11 cmd 2) |
| **W2a-2** | **Door events are answered.** At least half of the heard knocks, and at least 2, are answered. | per knock, at least one `door_call` or `door_open` by a family member in its scene | **0 of 0** |
| W2a-3 | **The door is opened.** | at least 1 `door_open` | **0** (B2) |
| W2a-4 | **Something crosses the threshold.** | at least 1 `door_give`, with `World` tap + bin down by the amount stated | **0** |
| **W2a-5** | **The house acts outward more than in v22.** At least 5 outward acts on at least 3 different days or nights, at least 3 of them door acts. | `went_out` and `got_up`/`at_door` once per leaver per night (`w1_score.py w11`), `collect_rain`, and the door acts above | **2** on 2 days (N5 `went_out`; D6 `collect_rain`), 1 by `w11` alone (B2) |
| W2a-6 | **The loop gives way** (jointly with the v22 fixes, §8.4). At most 4 of the 32 person-days have an exact repeat, and at most 12 acts sit in repeated texts. No stranger's line is repeated word for word in the run more than once. | the exact-repeat rule over the 326-or-so speech acts of days 3–10 | **7 of 32; 24 acts; 9 distinct texts** (B4; equal to `reports/v22_gaps.md:117-123`) |
| W2a-7 | **The talk reaches the person at the door.** On at least 60% of the days that follow or contain a heard knock, at least one speech act matches FOLK. | days d with a heard knock on d−1 or d; speech acts of d | **0 acts on 0 days** of 326 acts (B5b) |
| **W2a-8** | **Cost is bounded.** Live asks of days 3–10 ≤ 450; each day-scene's asks ≤ 56; each Q7 stretch ≤ 6 asks; at most 1 a day. | `meta.answers_live`; `quiet.asks.day`; Q7 stretches | **402**; days ≤ 48; none (B3; §11 cmd 3) |
| W2a-9 | **The prompt does not grow.** The largest estimate of any prompt ≤ 2650; the test T5 passes. | `estimate_tokens(system + prompt)` over the live prompts | **2602**, two prompts over 2600 (§11 cmd 3) |
| W2a-10 | **Truth.** Every `door_give` changes the stores by the exact amount; each visitor's stated need matches its household's computed need; no `TruthLeak`; days 1–2 replay as before (T4). | the street log against the chronicle; the run finishing | n/a (no door events) |

Why these thresholds: W2a-1's 3 is the least that gives W2a-2 to W2a-4 three chances; it is met by the calibration of §2.7, so it checks that the street works, not
that the family does. W2a-2's half is est.: a family afraid of a stranger on a boarded house may answer fewer than half, and that is what W2a-2 asks. W2a-5's 5 is the baseline
of 2 plus about half the answered scenes' door acts (4 knocks × 0.5 × 2.4 acts ≈ 5). W2a-6's 4 and 12 are about half of v22's 7 and 24, and the v22 fixes alone are meant to
move this number. W2a-9's 2650 is v22's 2602 plus 48 for the case in which nothing trimmable is left (§6.3).

##### 8.3 What would prove W2a wrong

| Result | What it means | What to do |
|---|---|---|
| W2a-1 holds and W2a-2 fails (fewer than half answered, or fewer than 2) | **A person at the door is ignored.** The reason does not move the house. The street was never the limit; the family's reading of its options is | Do not build W2b. Probe first, in the form of `reports/probe_stakes.md`: one door prompt asked 20 times, counting how often each door option is chosen. If the probe agrees with the run, change what the family is shown, not what the street does |
| W2a-2 holds, W2a-3 and W2a-4 fail | The family **talks to the door and keeps it shut**: a reason produces conversation, not an act. | The reason is too small, or the boards are too strong: a stranger who offers something (`trade`, W2b) is the next reason; read the scenes (§8.4) first |
| W2a-2, 3 and 4 hold, W2a-5 fails | The door moves the house and the rest of it stays put. This is **not** W2a wrong: W2a gives no reason to go out (§7.2). | W2c (trips among people), W2f (a place to go) |
| W2a-2 to W2a-5 hold, W2a-6 and W2a-7 fail | The door acts occur but do not displace the loop: the family keeps accusing | The reason is a side event. The loop is in the minds, and the next work is the memory (`reports/v22_gaps.md:262-269`), not more street |
| W2a-8 or W2a-9 fails | A cost limit, not a hypothesis. Cut the Q7 reserve to 4 or drop `door_look`. | |

**The hypothesis W2a tests:** *a stranger at the door with a stated need makes the house act at the door.* It is wrong if W2a-2, W2a-3 and W2a-4 all fail.

##### 8.4 Reading check, and what the baselines cannot say

- **Reading check (not a number; `CLAUDE.md:16-17`).** Every door scene is read in full. For each, the next report states: what the family did, and whether a
  real family in that room, that hungry, would have done it and for what reason; and whether the stranger said anything a person would not. A scene that passes
  every number and fails this is a failure.
- **The v22 fixes are in HEAD** (`reports/v22_fixes.md`), so a W2a run differs from v22 in two ways: the street and the three fixes (own words in the night mind, the stale intent,
  Q6's empty stretch). W2a-1 to W2a-5, W2a-7 and W2a-10 cannot be moved by the fixes (the fixes make no knock). **W2a-6 can**; it is labelled joint and no
  control run is planned (a control would cost a day's quota; `CLAUDE.md:5-6`). If W2a-6 holds, nobody can say which of the two did it.
- **A v22 baseline is a single seed of a single run.** A difference of 1 or 2 is inside what a re-run of the same seed gives (the model answers at temperature 1.0,
  `config.json`); the thresholds are set well away from the baselines for that reason.

---

#### 9. What this design does not decide

- **O1–O4** (§0.4), which are the user's.
- **Whether a model-written stranger is needed.** The gate is in §4.3; W2a does not run it.
- **The knock rate.** Fixed by one calibration, §2.7; the number 4 is est.
- **Night visitors.** None in W2a; the first is W2d.
- **A light in the house.** The data has none (`data.py:135-141`); whether the family may have a candle is a fact about the house.
- **Whether no. 7 is raided by the street.** O3; until then the street and the family's trips do not touch.
- **The C# port.** Not planned. Only the plain-data form of §7.2 keeps it possible.

---

#### 10. Sources

New sources of this design. `[W:Sn]` is `reports/world_design.md` §10. Where only an abstract or a secondary summary was reachable, it says so.

| # | Source | Used for |
|---|---|---|
| N1 | Rodríguez H., Trainor J., Quarantelli E.L. "Rising to the challenges of a catastrophe: The emergent and prosocial behavior following Hurricane Katrina." *Annals of the American Academy of Political and Social Science* 2006;604(1):82–101 (abstract, IDEAS/RePEc; full text not read). Natural Hazards Observer, March 2007 (Quarantelli and Frailing exchange; a summary only: Frailing and Harper compared burglary rates a month before and a month after the flood and report patterns they say contradict "looting is rare"; not read) | Prosocial response was the main response; looting rare; but burglary may have risen |
| N2 | Drury J., Cocking C., Reicher S. "Everyone for themselves? A comparative study of crowd solidarity among emergency survivors." *British Journal of Social Psychology* 2009;48:487–506, doi:10.1348/014466608X357893 (abstract and the BPS Digest summary; full PDF not read) | 21 interviews, 11 emergencies; shared identity linked to helping, including strangers |
| N3 | Kaniasty K., Norris F.H. "In search of altruistic community: Patterns of social support mobilization following Hurricane Hugo." *American Journal of Community Psychology* 1995;23:447–477, doi:10.1007/BF02506964 (abstract only: about 1,000 people; the hardest hit received most help and gave substantial help; help was uneven by race, education and age). The deterioration model: Kaniasty and Norris 1993, *Journal of Personality and Social Psychology* (title only, from a reference list), and a deterrence-model study with follow-ups 12 and 24 months after Hugo and 6 and 28 months after Andrew (samples 498 and 404; abstract only, authors and year not confirmed: probably Norris and Kaniasty 1996) | Help follows need, is uneven, and decays |
| N4 | Loftus G.R., Harley E.M. "Why is it easier to identify someone close than far away?" *Psychonomic Bulletin & Review* 2005;12:43–65 (University of Washington news summaries; paper not read): distance acts as blur; at 10 ft eyelashes are not seen, at 200 ft the eyes are not, at about 500 ft a head is a smudge | Detail is lost with distance (the 30 m and 10 m are est.) |
| N5 | Knapp R.H. "A psychology of rumor." *Public Opinion Quarterly* 1944;8(1):22–37 (secondary summaries only; over 1,000 rumours; pipe-dream, bogie and wedge-driving; negative ones were more readily passed on) | Hope and fear rumours |
| N6 | UK Building Regulations, Approved Document E (2003 edition), Table 2.1, as quoted in council reports and a manufacturer's guide: separating walls DnT,w + Ctr ≥ 45 dB for purpose-built houses, 43 dB for conversions; interior partitions Rw 40. The current gov.uk text was not found | Party wall 45 dB |
| N7 | Speech level at 1 m by vocal effort: normal 58, raised 64, loud 70, shout 76 dB (ESTA protocol table); ANSI S3.5 overall levels 62.4, 68.3, 74.9, 82.3 (SAGE entry; reference distance not stated); Pearsons K.S., Bennett R.L., Fidell S. *Speech levels in various noise environments*, EPA-600/1-77-025 (1977): 55–66 dBA in homes. The original tables were not retrieved | Voices |
| N8 | Thompson A.C. "Katrina's Hidden Race War" and follow-ups, *The Nation* and ProPublica, 2008–2010 (journalism; eyewitness accounts; at least 11 shot by the witnesses' count; the shooters said they defended against looters; no local investigation) | Afraid residents can be dangerous to outsiders |
| N9 | Lindell M.K., Perry R.W. "The Protective Action Decision Model: Theoretical modifications and additional evidence." *Risk Analysis* 2012;32(4):616–632, doi:10.1111/j.1539-6924.2011.01647.x (abstract only) | The household as the decider |
| N10 | FAMA Collection, Survival Questionnaire, Sarajevo (4,637 respondents; neighbours, friends and family as a pillar of endurance; water from a brewery, cisterns, rain); Andreas P. *Blue Helmets and Black Markets*, Cornell University Press, 2008 (summaries only) | Barter, wells, night movement |
| N11 | Sunrise and sunset for London, 1–3 October 2026: 07:01/18:37, 07:02/18:35, 07:04/18:33 (an Islington listing, via search). **10 October: NOT FOUND**; est. 18:18 | The knock window |
| N12 | "Byelaw terraced house", Wikipedia: the Local Government Act 1858 required a street of terraces about 36 ft (11 m) wide | The carriageway |

**Looked for and NOT FOUND:** a typical terraced-house frontage in metres; a measured knock level; a measured shouting level (the vocal-effort tables are for speech);
a rate at which neighbours knock on each other in a prolonged shortage; the current Approved Document E text; sunset on 10 October; a source for the probability that
a rumour of aid is true.

---

#### 11. Commands and output

All from `Prototypes/llm-morning/` unless stated. `$S` is the session scratchpad. No API key was used. No `morning.py` run was made. The scripts wrote only to `$S`.

**1. The state at the start** (repository root):
```
$ git rev-parse --short HEAD
da9b0d7
$ git status --short
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

**2. NOT FOUND in code:**
```
$ grep -n -i -E "knock|visitor|stranger|\bQ7\b|class Household|def household|class Street" *.py
(no output)    exit 1   (no line in any .py, tests included)
$ ls street.py streetdata world
ls: cannot access 'street.py': No such file or directory
ls: cannot access 'streetdata': No such file or directory
ls: cannot access 'world': No such file or directory
```

**3. The v22 cost baselines**, from the committed scorer, read only (`runs/w22/scoring/w1_score.py`, `GEMINI_API_KEY` unset; it wrote nothing in the repository):
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/w22/scoring/w1_score.py     exit 0
  W18 {"answers_live": 402, "api_requests": 405, "day_asks": {"3": 40, "4": 40, "5": 40, "6": 40, "7": 42, "8": 48, "9": 48, "10": 44}, ...
       "by_kind": {"day": 342, "night": 32, "mind": 28}, "largest": [2602, "day", "Daniel"], "largest_by_kind": {"day": [2602, "Daniel"], "night": [2407, "Daniel"], "mind": [2543, "Leo"]}, ...}
  W11 {"count": 1, "nights": [5], "items": [[5, "Daniel", "went_out"]]}
  W1-8 FAIL (live 402; day asks {3: 40, 4: 40, 5: 40, 6: 40, 7: 42, 8: 48, 9: 48, 10: 44}; largest estimate (2602, 'day', 'Daniel'))
```
(The prompts over 2600 are two, both Daniel, day 9: `reports/days_v22.md:382-386`.)

**4. The W2a baselines**, `$S/baseline_w2a.py`, read only, on the committed transcript. The output below is that script's, shortened where it listed rows.
The appendix is the same counting in condensed form; it was extracted from this file and run, and gave the same numbers (B2, B3, B4, B5b, B7, B9, B11):
```
$ PYTHONDONTWRITEBYTECODE=1 python -I $S/baseline_w2a.py runs/v22/daniel_ate_it-seed2.transcript.json     exit 0
B1 chronicle event kinds with 'door', 'knock', 'visit' or 'street' in them, all scenes:
    {'door': 2, 'street': 2}
   all kinds: 33 ; any kind 'knock' or 'visit': False
B2 outward acts (W1-1 rule), nights 3-9: 1 [(5, 'Daniel', 'went_out')] | nights: [5]
   collect_rain acts, days 3-10: 1 [(6, '07:00', 'Daniel')] | both kinds together: 2
   door options of any kind chosen (option ids starting door_, call_, open_): 0
B3 day-scene asks per day (quiet.asks.day), stretches by trigger:
   day 3: 40 asks; reserved (Q5+Q6)  0; not reserved 40; the morning 24, Q2 8, Q1 8
   day 4: 40 asks; reserved (Q5+Q6)  8; not reserved 32; the morning 24, Q2 8, Q5 8
   day 5: 40 asks; reserved (Q5+Q6)  8; not reserved 32; the morning 24, Q2 8, Q5 8
   day 6: 40 asks; reserved (Q5+Q6)  0; not reserved 40; the morning 24, Q2 16
   day 7: 42 asks; reserved (Q5+Q6)  8; not reserved 34; the morning 22, Q2 12, Q6 8
   day 8: 48 asks; reserved (Q5+Q6)  8; not reserved 40; the morning 24, Q2 8, Q1 8, Q5 8
   day 9: 48 asks; reserved (Q5+Q6) 16; not reserved 32; the morning 24, Q2 8, Q6 8, Q5 8
   day 10: 44 asks; reserved (Q5+Q6)  8; not reserved 36; the morning 24, Q2 12, Q5 8
   day asks sum: 342 | night decisions nights 3-9: 32 {3: 4, 4: 4, 5: 8, 6: 4, 7: 4, 8: 4, 9: 4}
B4 exact repeats, days 3-10: speech acts 326; in a repeated text 24; distinct repeated texts 9; person-days with a repeat 7 of 32; by person {'Elena': 2, 'Mara': 14, 'Leo': 4, 'Daniel': 4}
   (rows: day 3 Elena 2, Mara 7; day 6 Mara 3; day 7 Leo 4; day 8 Daniel 2; day 9 Mara 4; day 10 Daniel 2)
B5 speech acts naming people at the door or outside: 0 | naming neighbour / street / outside / out there: 69 of 326 (by day 2, 7, 7, 5, 6, 16, 12, 14)
B5b speech acts matching FOLK (W2a-7's regex), days 3-10: 0 {} | days: 0
B7 mean persons awake (not resting, not away) per minute, 07:30-17:30: 1.92, 1.65, 2.53, 2.15, 1.95, 2.54, 2.26, 2.24 (days 3-10); all days 2.16
B9 minutes of 07:30-17:30 inside a played stretch: 111 of 4808 (2.3%)
B11 asks per calendar day (day + night + mind): 48, 48, 52, 48, 50, 56, 56, 44 (days 3-10); largest 56
B12 reserved stretches: Q5 on days 4, 5, 8, 9, 10 at 19:00 (8 asks each); Q6 on day 7 at 17:18 and day 9 at 11:30 (8 asks each)
```
The B4 totals equal `reports/v22_gaps.md:117-123` (24 acts, 9 texts, 7 of 32 person-days; Mara 14, Leo 4, Daniel 4, Elena 2).

**5. The sound examples** (arithmetic only, `L = source − 20·log10(d) − walls`; ambient indoors day 25, night 20, rain 35):
```
 39.0 dB vs 25 (day  ): clearly (words)  knock (70 @1 m); listener in the kitchen, 2 m from the barricaded door (25)
 29.4 dB vs 25 (day  ): heard (no words) knock; listener in a bedroom 6 m away, its door open
 14.4 dB vs 25 (day  ): not heard        knock; same bedroom, its door closed (15)
 48.5 dB vs 25 (day  ): clearly (words)  conversation (58) on the pavement 3 m from the gap in the boards
 13.0 dB vs 25 (day  ): not heard        conversation (58) across the street, 10 m, boarded window (25)
 31.0 dB vs 25 (day  ): heard (no words) shout (76) 10 m away, boarded window (25)
 31.0 dB vs 20 (night): clearly (words)  shout (76) 10 m away, boarded window (25)
 31.0 dB vs 35 (rain ): not heard        shout (76) 10 m away, boarded window (25)
 32.4 dB vs 20 (night): clearly (words)  forced door or glass (85) 3 houses along (24 m), window (25)
 32.4 dB vs 35 (rain ): not heard        forced door or glass (85) 3 houses along (24 m), window (25)
 15.5 dB vs 25 (day  ): not heard        footsteps (50) 3 m outside the boarded door (25)
 40.5 dB vs 25 (day  ): clearly (words)  footsteps (50) 3 m from the gap in the boards
 15.5 dB vs 20 (night): not heard        loud voice (70) through the party wall (45), 3 m
 27.0 dB vs 25 (day  ): heard (no words) the family's raised voices (64), heard 4 m outside the boarded front window (25)
 20.9 dB vs 25 (day  ): not heard        the family's raised voices (64), heard at no. 11's door 8 m away through boards (25)
 13.0 dB vs 20 (night): not heard        the family's low voices at night (50), 4 m outside the boarded window (25)
```

**6. The population, stocks, plan and cost arithmetic** (a calculator, not a simulation of the design):
```
households by size: {1: 6.0, 2: 7.0, 3: 3.2, 4: 3.8}  people 46.7
P(out of food) by day 3: 0.24   by day 10: 0.51
days from taps dry to played day 3, 07:00: 3.79
 size 2.3: drinking-only use to day 3 = 17.4 L; a no-bath household (10-40 L, mean 25) has 7.6 L left on average => 1.64 days
no-bath households already dry on day 3 (size 2.3): 0.25
empty houses (9 incl. no. 7): baths expected 4.5 = 675.0 L; cisterns 54 L; bottles 27 L
persons out on the street at a random daylight minute (20 households x 0.4 trips x 40 min / 720): 0.44
knocks/day = short households within reach (2.8) x 0.3 trips x P(family's door) 0.17 = 0.14; 8 days 1.1     (0.3, 0.3: 2.0; 0.5, 0.17: 1.9; 0.5, 0.3: 3.4)
dw 2.0: u 0.33  stay 0.200  search(p.5) 0.053  search(p.2 after a failed search) -0.027  ask -0.060
dw 1.0: u 0.67  stay 0.100  search(p.5) 0.227  search(p.2 after a failed search)  0.067  ask  0.060
dw 0.5: u 0.83  stay 0.050  search(p.5) 0.313  search(p.2 after a failed search)  0.113  ask  0.120
 closed door, voice heard, 4 options offered: 439 chars = 122 tokens;  open door, 2 options + open line + voice: 381 chars = 106 tokens
```

**7. Web lookups** (WebSearch, standard mode): every source of §10. Each figure is given as found; where only an abstract or a secondary summary was reachable, §10 says so.

**8. At the end** (repository root):
```
$ git status --short
?? Prototypes/llm-morning/reports/w2_design.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
$ git diff --stat
(empty)
```

---

#### Appendix: `$S/baseline_w2a.py`

Read only; imports no project module; run as `python -I baseline_w2a.py runs/v22/daniel_ate_it-seed2.transcript.json` from `Prototypes/llm-morning/`.
```python
import collections, json, re, sys

t = json.load(open(sys.argv[1], encoding="utf-8"))
NAME = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ORDER = ["daniel", "elena", "leo", "mara"]
DAYS = range(3, 11)

def acts(day):
    return sorted((a for turn in day["turns"] for a in turn["acts"]), key=lambda a: tuple(a["decided_at"]))
def speech(day):
    return [a for a in acts(day) if a["mode"] == "model" and a["words"]]
def clock(m):
    h, mm = divmod(420 + m, 60); return f"{h:02d}:{mm:02d}"

ev = t["chronicle"]["events"]
kinds = collections.Counter(e["kind"] for e in ev)                                    # B1
print({k: v for k, v in kinds.items() if re.search("door|knock|visit|street", k)}, any(k in kinds for k in ("knock", "visit", "visitor")))

per = {}                                                                              # B2: w1_score.py's w11
for e in ev:
    if e["kind"] in ("went_out", "got_up", "at_door") and re.fullmatch(r"N\d+", e["scene"]):
        k = int(e["scene"][1:])
        if 3 <= k <= 9:
            who = set(e["members"] or []) | ({e["actor"]} if e["kind"] == "got_up" or not e["members"] else set())
            for q in who:
                per.setdefault((k, q), set()).add(e["kind"])
items = sorted((k, NAME[q], "went_out" if "went_out" in v else "got_up/at_door") for (k, q), v in per.items())
rain = [(k, clock(a["minute"]), NAME[a["who"]]) for k in DAYS for a in acts(t[f"day{k}"])
        if a["option"] == "collect_rain" and a["mode"] == "model"]
print(len(items), items, len(rain), rain)

for k in DAYS:                                                                        # B3
    q = t[f"day{k}"]["quiet"]; by = collections.Counter()
    for s in q["stretches"]:
        by[s["trigger"]] += s["asks"]
    print(k, q["asks"]["day"], by["Q5"] + by["Q6"], dict(by))

def norm(s): return " ".join(re.findall(r"[a-z0-9']+", s.lower()))
n_acts = in_rep = distinct = pdays = 0                                                # B4
for k in DAYS:
    sp = speech(t[f"day{k}"]); n_acts += len(sp)
    for p in ORDER:
        c = collections.Counter(norm(a["words"]) for a in sp if a["who"] == p)
        rep = {w: n for w, n in c.items() if n >= 2}
        if rep:
            pdays += 1; distinct += len(rep); in_rep += sum(rep.values())
print(n_acts, in_rep, distinct, pdays)

FOLK = re.compile(r"\b(knock\w*|stranger\w*|visitor\w*|at the (front )?door|woman|that (man|boy|girl|child)|"
                  r"the (boy|girl|child)|whoever (knocked|is outside))\b", re.I)    # B5b
print(sum(1 for k in DAYS for a in speech(t[f"day{k}"]) if FOLK.search(a["words"])))

tot = 0                                                                               # B7: awake at 07:30-17:30
for k in DAYS:
    d = t[f"day{k}"]; away = set(d.get("away", [])); rest = collections.defaultdict(list)
    for s in d["quiet"]["spans"]:
        if s["routine"] == "rest": rest[s["who"]].append((s["start"], s["end"]))
    tot += sum(1 for m in range(30, 631) for p in ORDER if p not in away and not any(a <= m < b for a, b in rest[p]))
print(tot / (601 * 8))

print(sum(max(0, min(s["end"], 631) - max(s["start"], 30)) for k in DAYS                # B9
          for s in t[f"day{k}"]["quiet"]["stretches"]), 601 * 8)
for k in DAYS:                                                                        # B11
    d = t[f"day{k}"]["quiet"]["asks"]["day"]
    n = len(t[f"night{k}"]["decisions"]) if k < 10 else 0
    print(k, d + n + (4 if k < 10 else 0))
```

