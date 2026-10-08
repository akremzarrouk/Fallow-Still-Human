# W1, the physical layer: implementation

Mode: implement. The spec is `reports/world_design.md` (committed alone as `86b3c74`), §1, §2, §3.1, §4.1–§4.3, §5
(Q6), §6 (W1) and §7, with the brief's three amendments. No API call was made, no cache was written, and no frozen
version (v1/ to v14/) was touched. Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in
`runs/w1_impl/`.

## Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| 1 | Every new rule has a test that failed before and passes after | **yes** | 25 new tests. The first 21 were written before any code: 21 errors (`ModuleNotFoundError: No module named 'truth'`). The 4 added while building fail with their rule taken out (`runs/w1_impl/red_late.stdout.txt`). All 25 pass (§5). |
| 2 | No-API replay of v16 seed 2 through night 2 is IDENTICAL | **yes** | Story and transcript are byte for byte the same as before the change; 96 answers from the cache, 0 live (§5, command 4). |
| 3 | Fake run of seed 2, `--days 10`, exits 0 and prints the weather, the water each morning, the stages each evening and every Q6 | **yes** | Exit 0; the printout is in §3. Days 7 and 9 have daytime rain, and Q6 fired on both. The rain tests also force rain on day 3. |
| 4 | No "Your body:" line of the fake run matches `impossible\|cannot\|can't\|unable\|barely (stand\|walk\|move)` | **yes** | 581 prompts, 581 body lines, 12 distinct: **0** match (§3). |
| 5 | v9 to v14 replays IDENTICAL; the full suite passes | **yes** | 18 IDENTICAL, 6 exits 0. **282 tests OK** (257 before W1, plus 25). |

## 1. What was built

**New modules:**
- **`truth.py`: `World`, the single owner of truth for the weather and the water.** It holds the stored tap water,
  the bin's rain water, the house's water rule, each person's water deficit, who is wet until when, the water of the
  neighbour's house and of each house further along (fixed once, when first needed), and every fact it fixed.
  - **It advances minute by minute.** `next_change` runs a copy forward to find when the tap water runs out or a
    thirst stage changes, so a quiet day can jump straight to that minute.
  - **The guard:** `World` reads raise `TruthLeak` while any prompt is being built. `Morning.prompt_for` (day and
    night) and `NightMind.prompt_for` run inside `truth.prompting()`.
  - **Where it lives:** it is made the first time a quiet day needs it (day 3) and kept on the chronicle
    (`chronicle.world`). The quiet day and the night after it hold it for the code alone.
- **`weather.py`: the Richardson-type generator of §4.1.**
  - Kew normals for September and October, interpolated from 1 October.
  - Wet days by `P(W|W)` 0.5 and `P(W|D)` from the wet-day share; exponential amounts; one or two spells of 2 to 6
    hours.
  - Temperatures with noise and the wet-day shift; indoors is the daily mean + 4 °C.
  - Every draw has its own string, `"{seed}:weather:day{k}:..."`. `force()` fixes a day, for tests.
- **`water.py`: the numbers of §4.2 and §4.3.2.**
  - The fill (bath 150, kitchen 46.5), the dry minute (house day 2, 12:00).
  - The three levels (24, 10 and 5 L a day for four people) and the net loss of 1.2 L a day.
  - Body masses and the thirst stages at 2, 5, 8 and 10% of body mass.
  - The catchment (25 m² × 0.85 = 21.25 L per mm), the 240 L bin, the 10 L a person carries.
  - The empty-house rule (a bath full with chance 0.5, a 6 L cistern, 0 to 4 bottles of 1.5 L).
  - The "About water:" line, rounded to what an eye sees: the bath to 10 L, the kitchen to 5, the bin to 10.

**Changed files:**
- **`quiet.py`:**
  - Fasting stages in days: `FAST_LINES = (24, 72, 168, 336, 672)`.
  - The new body line with thirst and cold; the new need views (fasting 1–5, thirst 1–4).
  - Thirst as a need with crossings and Q1 (from T2). Cold from F2 under 18 °C indoors, or "wet" for 2 hours after
    the yard.
  - World brought to every tick, and what each person perceives written into them (`rain_since`, `water`).
  - Rain onsets heard by everyone awake; **Q6**.
  - The water rules and `collect_rain` applied by code.
  - `next_event` jumps to rain starts and ends, the tap running dry and thirst crossings.
  - Q6's stretch has 8 asks of its own, on top of the day's 40, like Q5's.
- **`world.py`:**
  - Each `Person` gets `rain_since` and `water` (knowledge, never World).
  - The body line takes thirst and cold; the "About water:" line goes after the trip lines.
  - New options: `save_water` and `ration_water` (speech, after the trip options) and `collect_rain` (in the kitchen
    while it rains, if the bin is not out). Their gists, own lines and `KIND_DONE` entries.
  - From day 3: the yard in the house line, and "- Rain is falling: ..." in the `Now` lines.
  - The prompt guard.
  - **W1's lines sit outside the trimming budget**, as the trip block does (see §2, point 10).
  - Thirst in `levels`, `risen` and `rise_words`.
- **`night.py`:**
  - The bedtime line "It is raining: you hear it on the roof.", and the `rain_out` bedtime option (set the bin out,
    then sleep: paid back as sleep).
  - A rainy night (any spell from 22:00 to 06:00) halves the front-door and return wake chances.
  - Fasting stages mapped to the street shifts: F2 weak, F3 very weak, F4 and on barely standing.
  - **A trip that gets inside carries water home** (amendment 2): up to 10 L a person, bottles first, then the
    cistern, then the bath. The house sees it come home ("carrying water"). The return line, the morning opening, the
    neighbour's-house line, the outings and street lines, and yesterday's positions say so.
- **`data.py`:** `YARD` and `with_yard` (amendment 3). No stove.
- **`talk.py`:** `save_water` and `ration_water` are speech kinds, new the first time each person says them.
- **`chronicle.py`:** gists for the new kinds and for rain. World's fixed facts are copied into `fixed` when a night is
  added.
- **`mind.py`:** the night mind's prompt builder is inside the guard.
- **`story.py`:** rain and Q6 rows; the new need words.
- **`morning.py`:** prints the weather of every day played, the water at 07:00, the stages at 21:00, every Q6, and
  each night's rain, choices and water carried. `q6_fired`, `rain_heard` and `water` are in each quiet day's meta.

**Nothing before day 3 changes:**
- World is made at day 3's setup.
- The yard, the water line, the water options and the rain lines need `m.quiet`, which days 1 and 2 do not have.
- Nights 1 and 2 have no World, so they take no water; the neighbour's water is still unfixed on day 3, and nobody
  knows of it (amendment 2; `test_nights_1_and_2_took_no_water`).

## 2. Spec points not built as written, and why

1. **Death** from thirst (§4.3.2, each person's point in 10–12%) and from starvation (§4.3.1, 40–60 days) is **not
   built**.
   - The thirst stages up to T4 and their words are built.
   - No 10-day run reaches either death: the fake run never went below T0, and starvation death is weeks away.
   - A dead person needs a state every scene respects. That is its own small stage.
2. **A rest falls due at F2 (72), not F3** (§4.3.1 said F3 "so the day's rests keep their timing"). 72 is the stage
   nearest the old 96. F3 (168) would have moved every fasting rest days later.
3. **Q1 fires for fasting from F2**, not F1. F1 at 24 hours is ordinary hunger. Q1 fires for thirst from T2, and for
   debt at exhausted as before.
4. **The rain's start is heard by everyone awake, not by those resting.** Resting counts as asleep, as Q1 counts it.
   Whoever is asked while it rains still gets the "Rain is falling" line.
5. **Q6 asks everyone awake in the room with the most people awake** (ties: the house's room order). When the rain
   begins during played turns, it is a new trigger for everyone awake, and Q6 is logged as not fired ("the house was
   already talking").
6. **`collect_rain` sets out the bin only** (§4.2.3 said "the empty buckets and the bin"). The buckets still hold
   stored tap water then, and one bin under a 21 L/mm drainpipe catches more than all the pans. The design's
   "bringing them in" step is not built: a bin under a drainpipe stays there.
7. **Thirst repayment:** someone short of water drinks what they lack at once, from whatever is stored, even under
   rationing (est.). The design said drinking is "spread over the waking hours". Drinking is spread per minute; only
   the repayment is immediate.
8. **The "About water:" line is refreshed for everyone in the house at every tick,** not only "when they are in the
   room". The house is small, and everyone passes the kitchen.
9. **Carried water is in words rounded to 5 L** ("about 10 litres"; "a few litres" under 2.5). Seed 2's neighbour
   holds 9 L: an empty bath, the cistern, two bottles.
10. **Not in the spec: W1's lines are outside the trimming budget** (`world.py`, `prompt_parts`), as the trip block is.
    Without this, the water and rain lines pushed memory lines out (`test_w1_lines_sit_outside_the_budget_...`).
11. **§1.2's test is a guard, not a planted truth.** The spec asked for a fake run "with a World whose truth differs
    from every person's Knowledge", checking no prompt holds a truth-only value. What was built:
    - a guard that raises if any prompt builder reads World (`test_world_cannot_be_read_while_a_prompt_is_built`,
      day, night and night-mind prompts);
    - a 10-day fake run with the guard on throughout, in which every litre figure in every prompt is a multiple of 5,
      as the eye-rounded line allows and the exact store never is.
12. **The weather is printed in every run**, replays included (`morning.py`). It changes no story or transcript.

**Old tests changed** (15), each because the spec changed what they check, or because changed prompts moved a fake's
path:
- **Fasting in days:**
  - `test_fasting_at_day_3_0700_is_section_6s`: Mara is F1 at 44.7.
  - `test_the_body_line_states_each_stage`: the new words.
  - `test_q1_asks_only_with_someone_awake_there_and_once`: Mara crosses 72 at 10:27.
  - `test_a_third_fasting_stage_at_144` is replaced by `test_a_third_fasting_stage_at_168`.
  - `test_weakness_shifts_the_street_tables` and `test_weakness_shifts_the_near_table_by_half_of_the_far`: the same
    tables, with the stages renumbered.
- **Water carried home** (amendment 2: every empty house has at least its cistern):
  - `test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it`
  - `test_every_quiet_prompt_carries_the_outings_line`
  - `test_a_trip_is_known_to_the_whole_house_by_the_next_morning`
  - `test_yesterdays_positions_end_with_what_happened_that_night`
  - In each, "came back with nothing" became "came back with water" for a trip that got inside.
- **Q5 and Q6 have 8 asks each on top of the day's 40:** `test_n_t2_the_cycle` and
  `test_the_morning_stops_at_24_asks_and_a_triggered_stretch_at_8` leave both out of the 40.
- **`test_q5_at_19_asks_whoever_took_a_trip_position_last`:** Leo's fasting now reaches 72 at exactly 19:00 on day 3
  (60 + 12), so his Q1 took Q5's minute. His last meal is moved two hours earlier in the test.
- **`test_a_day_3_afternoon_act_is_yesterday_and_a_night_event_has_no_clock`:** the test sets Leo's suspicion itself.
  It now also sets its strength (2), since the new stage lines ask him more often and his suspicion had fallen to 0
  by night.
- **`test_t12_the_budget`:**
  - `without_blocks` strips W1's lines and the yard.
  - A quiet-day prompt whose untrimmable part (meeting lines, the turn's lines, grudges) exceeds 1450 must have been
    trimmed to the end and stay under v21's 2600 (T2).
  - In the three fake runs, one prompt falls under this rule: 1574 (`runs/w1_impl/t12_over.stdout.txt`). It is a
    day-3 Leo prompt with nothing left to trim; its W1 lines are already counted out.

**Found, not fixed (pre-existing, flagged as a separate task):** eating during a quiet day does not reset fasting
until the next morning.
- `p.needs["ate_at"]` is set only in `quiet.setup` (`quiet.py:188`, and `quiet.py:148` at HEAD).
- In the fake run this gives 13 body lines that read "hungry, for days now: ..." after a meal.

## 3. The fake run's printouts (DONE 3 and 4)

`runs/w1_impl/done3.stdout.txt` (the full stdout of the run is `runs/w1_impl/fake10.stdout.txt`, 542 lines):
```
morning.run(2, fake=True, days=10): exit 0; asks 581 (fake)
  weather day 1: wet, 2.5 mm (09:00 to 13:09); 7.7 to 14.2 °C outdoors, 15.0 °C indoors
  weather day 2: dry; 11.2 to 15.2 °C outdoors, 17.2 °C indoors
  weather day 3: dry; 12.6 to 16.1 °C outdoors, 18.4 °C indoors
  weather day 4: dry; 7.1 to 19.4 °C outdoors, 17.2 °C indoors
  weather day 5: wet, 12.3 mm (22:03 to 03:42 the next day); 7.1 to 14.3 °C outdoors, 14.7 °C indoors
  weather day 6: wet, 4.5 mm (05:27 to 11:03, 06:30 to 10:45); 11.6 to 13.6 °C outdoors, 16.6 °C indoors
  weather day 7: wet, 1.2 mm (04:36 to 10:09, 17:18 to 20:21); 11.8 to 13.3 °C outdoors, 16.6 °C indoors
  weather day 8: dry; 8.0 to 19.1 °C outdoors, 17.5 °C indoors
  weather day 9: wet, 17.8 mm (11:30 to 16:30); 7.8 to 14.0 °C outdoors, 14.9 °C indoors
  weather day 10: dry; 8.6 to 18.6 °C outdoors, 17.6 °C indoors
  day 3 07:00 water: tap 105.5 L (bath 59.0, kitchen 46.5), bin 0.0 L, level as_before
  day 3 21:00 stages: Daniel F1 T0 (fast 70.7, short of water 0.00 L); Elena F1 T0 (fast 52.2, short of water 0.00 L); Leo F2 T0 (fast 74.0, short of water 0.00 L); Mara F1 T0 (fast 58.4, short of water 0.00 L)
  night 3: dry; bedtime Daniel go_next_door, Elena sleep, Leo sleep, Mara sleep; Daniel, Leo out (back with nothing), water 9 L
  day 4 07:00 water: tap 109.3 L (bath 62.8, kitchen 46.5), bin 0.0 L, level rationed
  day 4 21:00 stages: Daniel F2 T0, cold (fast 98.3, short of water 0.00 L); Elena F2 T0, cold (fast 72.6, short of water 0.00 L); Leo F2 T0, cold (fast 98.0, short of water 0.00 L); Mara F2 T0, cold (fast 81.2, short of water 0.00 L)
  night 4: dry; bedtime Daniel sleep, Elena go_next_door, Leo lie_awake, Mara go_next_door; Elena out (back with nothing), water 0 L; Mara out (back with nothing), water 0 L
  day 5 07:00 water: tap 104.3 L (bath 57.8, kitchen 46.5), bin 0.0 L, level rationed
  day 5 21:00 stages: Daniel F2 T0, cold (fast 125.9, short of water 0.00 L); Elena F2 T0, cold (fast 93.0, short of water 0.00 L); Leo F2 T0, cold (fast 122.0, short of water 0.00 L); Mara F2 T0, cold (fast 104.0, short of water 0.00 L)
  night 5: rainy; bedtime Daniel sleep, Elena go_further, Leo lie_awake, Mara watch_door; Elena, Mara out (back with food), water 12 L
  day 6 07:00 water: tap 111.3 L (bath 64.8, kitchen 46.5), bin 0.0 L, level rationed
  day 6 21:00 stages: Daniel F2 T0, cold (fast 153.5, short of water 0.00 L); Elena F2 T0, cold (fast 113.4, short of water 0.00 L); Leo F2 T0, cold (fast 146.0, short of water 0.00 L); Mara F2 T0, cold (fast 126.8, short of water 0.00 L)
  night 6: rainy; bedtime Daniel go_further, Elena sleep, Leo lie_awake, Mara go_further; Mara, Daniel out (back shaken, with food), water 10.5 L
  day 7 07:00 water: tap 116.8 L (bath 70.3, kitchen 46.5), bin 81.0 L (under the drainpipe), level rationed
  day 7 17:18: Q6, rain began: Daniel, Elena, Leo, Mara asked in the kitchen
  day 7 21:00 stages: Daniel F1 T0 (fast 39.4, short of water 0.00 L); Elena F2 T0, cold (fast 133.8, short of water 0.00 L); Leo F1 T0 (fast 34.2, short of water 0.00 L); Mara F1 T0 (fast 32.5, short of water 0.00 L)
  night 7: dry; bedtime Daniel go_further, Elena go_next_door, Leo sleep, Mara go_next_door; Elena, Mara, Daniel out (back shaken, with nothing), water 0 L
  day 8 07:00 water: tap 111.8 L (bath 65.3, kitchen 46.5), bin 100.9 L (under the drainpipe), level rationed
  day 8 21:00 stages: Daniel F1 T0 (fast 43.4, short of water 0.00 L); Elena F1 T0 (fast 32.1, short of water 0.00 L); Leo F1 T0 (fast 37.8, short of water 0.00 L); Mara F1 T0 (fast 35.9, short of water 0.00 L)
  night 8: dry; bedtime Daniel sleep, Elena sleep, Leo sleep, Mara go_next_door; Mara out (back with nothing), water 0 L
  day 9 07:00 water: tap 106.8 L (bath 60.3, kitchen 46.5), bin 100.9 L (under the drainpipe), level rationed
  day 9 11:30: Q6, rain began: Daniel, Elena, Leo, Mara asked in the kitchen
  day 9 21:00 stages: Daniel F1 T0 (fast 71.0, short of water 0.00 L); Elena F1 T0 (fast 52.5, short of water 0.00 L); Leo F1 T0 (fast 61.8, short of water 0.00 L); Mara F1 T0 (fast 58.7, short of water 0.00 L)
  night 9: dry; bedtime Daniel go_next_door, Elena go_further, Leo lie_awake, Mara sleep; Daniel, Elena out (back shaken, with nothing), water 0 L
  day 10 07:00 water: tap 101.8 L (bath 55.3, kitchen 46.5), bin 240.0 L (under the drainpipe), level rationed
  day 10 21:00 stages: Daniel F2 T0, cold (fast 98.6, short of water 0.00 L); Elena F2 T0, cold (fast 72.9, short of water 0.00 L); Leo F2 T0, cold (fast 85.8, short of water 0.00 L); Mara F2 T0, cold (fast 81.5, short of water 0.00 L)
DONE 4: prompts 581; 'Your body:' lines 581 (12 distinct); matching "impossible|cannot|can't|unable|barely (stand|walk|move)": 0
    24 × Your body: a little hungry.
    13 × Your body: hungry, for days now: you feel light and slow, and standing up fast greys your sight for a moment; and you feel cold, even indoors.
    50 × Your body: hungry.
    14 × Your body: starving, and you have hardly slept.
   110 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; and you feel cold, even indoors.
     5 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; and you have hardly slept.
     4 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; you are wet and cold; and you have hardly slept.
    61 × Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; you feel cold, even indoors; and you have hardly slept.
    70 × Your body: starving.
   119 × Your body: starving; hunger comes in waves.
   100 × Your body: starving; hunger comes in waves; and you have hardly slept.
    11 × Your body: very hungry.
exit 0
```

**How to read it** (a fake model, so its choices are not behaviour):
- **The water:**
  - Day 3 starts at 105.5 L of tap water, as fixed.
  - The fake said `ration_water` on day 3, so 5 L a day from day 4.
  - Trips carried in 9, 12 and 10.5 L.
  - The bin went under the drainpipe on day 6 (`collect_rain`, while it rained in the morning) and filled to its
    240 L on day 9's 17.8 mm.
  - Nobody went short of water: T0 throughout.
- **The rain:** day 3 is dry and 18.4 °C indoors, so no Q6 and no cold that day. Q6 fired at 17:18 on day 7 and at
  11:30 on day 9. The forced-rain tests show Q6 on day 3.
- **The night:** nights 5 and 6 were rainy (rain between 22:00 and 06:00), so their door draws were halved.

## 4. Test names

**New (25), in `test_morning.PhysicalLayerTest`.** The first 21 were red before any code:
- `test_world_cannot_be_read_while_a_prompt_is_built`
- `test_a_ten_day_fake_run_never_reads_world_in_a_prompt`
- `test_the_weather_is_seeded_by_string_and_follows_the_kew_normals`
- `test_the_store_at_day_3_0700_is_105_5_litres_of_tap_water`
- `test_each_level_uses_its_litres_a_day`
- `test_thirst_grows_only_without_water_and_its_stages_are_2_5_8_10_percent`
- `test_the_about_water_line_says_what_an_eye_sees`
- `test_fasting_stages_are_in_days`
- `test_no_body_line_forbids_an_act`
- `test_cold_at_f2_under_18_indoors_and_wet_after_the_yard`
- `test_rain_in_a_quiet_stretch_reaches_everyone_awake_and_q6_plays_their_room`
- `test_q6_once_a_day_and_rain_in_played_turns_is_a_trigger`
- `test_a_prompt_while_it_rains_says_so`
- `test_the_back_door_and_the_yard_from_day_3_only`
- `test_collect_rain_sets_the_bin_under_the_drainpipe_and_it_fills_by_catchment`
- `test_save_and_ration_water_set_the_level_from_when_they_are_said`
- `test_the_neighbours_water_is_fixed_when_first_needed_and_carried_home`
- `test_a_house_further_along_holds_water_fixed_once`
- `test_nights_1_and_2_took_no_water`
- `test_the_bedtime_rain_option_and_rain_masking_the_front_door`
- `test_a_run_prints_the_weather_the_water_the_stages_and_every_q6`

The 4 added while building, each red without its rule (`runs/w1_impl/red_late.py`):
- `test_w1_lines_sit_outside_the_budget_and_cut_no_memory_line`
- `test_q1_asks_when_thirst_reaches_badly_thirsty`
- `test_the_chronicle_keeps_the_water_fixed_once`
- `test_the_story_shows_rain_and_q6`

**Replaced:** `test_a_third_fasting_stage_at_144` → `test_a_third_fasting_stage_at_168`.

## 5. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. `$S` is the session scratchpad.

**1. Before any change: the suite, and the replay saved for DONE 2**
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/facts_evening/prefix.py . $S/w1/prefix_before 2
daniel_ate_it-seed2: through night 2 and mind 2: 96 answers from the cache, 0 live
exit 0
$ time ... .venv/Scripts/python.exe -m unittest test_morning < /dev/null
Ran 257 tests in 222.990s
OK
real	3m44.383s
```

**2. Red: the 21 W1 tests, before any code** (`runs/w1_impl/red.stdout.txt`)
```
$ ... .venv/Scripts/python.exe -m unittest test_morning.PhysicalLayerTest < /dev/null
exit 1
     21 ModuleNotFoundError: No module named 'truth'
      1 Ran 21 tests in 0.066s
      1 FAILED (errors=21)
```

**3. Red: the 4 added while building** (`runs/w1_impl/red_late.stdout.txt`)
```
$ ... .venv/Scripts/python.exe runs/w1_impl/red_late.py < /dev/null
exit 0
without the W1 block (world.py): test_w1_lines_sit_outside_the_budget_and_cut_no_memory_line: exit 1; AssertionError: Lists differ: ['Wha[80 chars]ere)'] != ['Wha[80 chars]ere)', '- min 00: filler line number 199 about[304 chars]ll '] | FAILED (failures=1)
  world.py restored: sha256 same
Q1 for fasting and debt only (quiet.py): test_q1_asks_when_thirst_reaches_badly_thirsty: exit 1; AssertionError: Lists differ: [] != [('Q1', 'leo', 'thirst', 2)] | FAILED (failures=1)
  quiet.py restored: sha256 same
the chronicle not keeping World's facts (chronicle.py): test_the_chronicle_keeps_the_water_fixed_once: exit 1; KeyError: 'neighbour_water' | FAILED (errors=1)
  chronicle.py restored: sha256 same
the story without rain and Q6 (story.py): test_the_story_shows_rain_and_q6: exit 1; AssertionError: '- 12:00: rain begins (heard by ' not found in '# The third morning (day 6)\n\nThe same rules as day 1, from the people as the night left them.  | FAILED (failures=1)
  story.py restored: sha256 same
every one failed without its rule, and every file is restored
```

**4. DONE 2** (`runs/w1_impl/done2.stdout.txt`)
```
$ env -u GEMINI_API_KEY ... .venv/Scripts/python.exe runs/facts_evening/prefix.py . $S/w1/prefix_after 2
daniel_ate_it-seed2: through night 2 and mind 2: 96 answers from the cache, 0 live
exit 0
daniel_ate_it-seed2.md: before vs after: IDENTICAL
daniel_ate_it-seed2.transcript.json: before vs after: IDENTICAL
bdaa0a9f3e69062f380480bd98e04d508bf6c2206549ddb1a6bf2bdf64a859fc *$S/w1/prefix_before/daniel_ate_it-seed2.md
c6ea7695baa98b4ddb5f1ccc390d6e22e3286df0992a5e62e0494ec45be5ff52 *$S/w1/prefix_before/daniel_ate_it-seed2.transcript.json
bdaa0a9f3e69062f380480bd98e04d508bf6c2206549ddb1a6bf2bdf64a859fc *$S/w1/prefix_after/daniel_ate_it-seed2.md
c6ea7695baa98b4ddb5f1ccc390d6e22e3286df0992a5e62e0494ec45be5ff52 *$S/w1/prefix_after/daniel_ate_it-seed2.transcript.json
```

**5. DONE 3 and 4** (`runs/w1_impl/done3.stdout.txt`; output in §3)
```
$ time ... .venv/Scripts/python.exe runs/w1_impl/done3.py < /dev/null
real	0m19.444s
exit 0
```

**6. The budget's one exception** (`runs/w1_impl/t12_over.stdout.txt`: day and night prompts of `test_t12`'s three fake
runs estimated at 1400 or more without their blocks; 18 lines; the first five)
```
$ ... .venv/Scripts/python.exe runs/w1_impl/t12_over.py | sort -rn
1574 day You are Leo, 21, the younger son of the  | 83 | cut
1448 day You are Leo, 21, the younger son of the  | 81 | cut
1444 day You are Elena, 42, the mother of the fam | 81 | cut
1415 day You are Mara, 17, the youngest, the daug | 76 | cut
1400 day You are Mara, 17, the youngest, the daug | 83 | cut
```

**7. DONE 5: the frozen versions** (`runs/w1_impl/frozen.stdout.txt`)
```
$ for v in v14 v13 v12 v11 v10 v9; do ... .venv/Scripts/python.exe $v/check.py; echo "exit $?"; done
IDENTICAL: 18 (story and transcript, seeds 1-3, each version); DIFFERS: 0
      6 exit 0
```

**8. DONE 5: the full suite** (`runs/w1_impl/unittest.stdout.txt`)
```
$ ( time ... .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?" )
Ran 282 tests in 307.194s
OK
real	5m8.478s
exit 0
```

**9. At the end**
```
$ git log --oneline -1          (the design, committed alone before any code)
86b3c74 LLM morning: the world design (reports/world_design.md): World as the owner of truth, three architecture angles, weather, water, honest bodies, the population, word and rumours, the staged plan W1 to W7, and W1's frozen predictions
$ git status --short
 M chronicle.py
 M data.py
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
?? runs/w1_impl/
?? truth.py
?? water.py
?? weather.py
$ git diff --stat
 Prototypes/llm-morning/chronicle.py    |  10 +-
 Prototypes/llm-morning/data.py         |  12 +
 Prototypes/llm-morning/mind.py         |   7 +-
 Prototypes/llm-morning/morning.py      |  51 ++-
 Prototypes/llm-morning/night.py        | 107 +++++-
 Prototypes/llm-morning/quiet.py        | 230 ++++++++++--
 Prototypes/llm-morning/story.py        |  15 +-
 Prototypes/llm-morning/talk.py         |  7 +-
 Prototypes/llm-morning/test_morning.py | 634 ++++++++++++++++++++++++++++++---
 Prototypes/llm-morning/world.py        |  81 ++++-
 10 files changed, 1034 insertions(+), 120 deletions(-)
```
No cache file, no frozen version and no `runs/v*` file changed (`git status` shows none). W1 is not committed; the
design is.
