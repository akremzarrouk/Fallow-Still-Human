# The quiet day, stage A: implementation

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, and day 3 was answered by fake
clients. No cache was regenerated or written: `cache/v16` was copied to temp folders and read from there (its files
are unchanged, last written 2026-10-06). Nothing before day 3 changed (§4.3).

Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\f39d3e9a-4b34-40fb-bd99-b95ba7bb6eed\scratchpad`.

**What was built,** from `reports/quiet_day_design.md`:
- §1.1 fasting and §1.2 sleep debt, with their body lines;
- §2.1 withdraw and §2.2 rest, with sit in the kitchen as the default (§2.5);
- §3 the clock and time skipping, with spans recorded in the chronicle, in block A and at bedtime;
- §4 triggers Q1 and Q2, and the day budget;
- §6.1's starting values.

**The brief's amendments, all built:**
1. No doze draw.
2. Each rest lasts a seeded 2 to 4 hours (`quiet.py:95`, `REST_LENGTH` at `quiet.py:33`).
3. From minute 90 on, records, block A's summary and the bedtime summary say the clock ("10:21") (`quiet.py:54`).
4. Only Q1 and Q2; at most 12 quiet asks (4 of one person) and 40 day asks.

**Not built (out of scope):** keep watch, watch the street, Q3, Q4, W2 shifts, W5 and the doze draw.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | From v16 seed 2's state after night 2, with a fake client: ≥ 1 rest span per person; return times differ; a withdraw only when all §2.1 conditions hold; Q2 fires on an arrival after 60 quiet minutes and not before; the budget caps hold when the fake keeps talking | **PASS** | The §2.1, §2.2, §4 and budget tests of §3.1. Sample day: §5. |
| 2 | Fasting and debt match §6's hand-computed values at 07:00 on day 3 | **PASS** | Fasting 59.8 / 60 / 44.745 / 20.4; debt 25 / 22 / 22 / 19 (Daniel / Leo / Mara / Elena). `test_fasting_at_day_3_0700_is_section_6s`, `test_sleep_debt_at_day_3_0700_is_section_6s`. |
| 3 | No-API replay of v16 seeds 1 to 3 through night 2 is IDENTICAL | **PASS** | Story and transcript are byte-identical to the same replay at HEAD, 3 of 3 (§6.3). Against the original runs: seeds 2 and 3 are IDENTICAL. Seed 1 already differed at HEAD by two verdict lines (S4/S8 now warn, commit 543e325), and this change adds nothing to that. |
| 4 | v9 to v14 replays IDENTICAL; the full suite passes | **PASS** | 18 of 18 IDENTICAL (§6.4). `Ran 217 tests`, `OK` (§6.5). |

## 1. The change

| File | Change |
|---|---|
| `quiet.py` (new) | The layer, in five groups. **Needs:** `fast`, `debt`, `tick` (stage crossings), `setup` (values at 07:00 from the chronicle and the nights). **Spans:** `start`, `end`, `arrive`, `assign`, `rest_end`, `rest_due`. **Triggers and budget:** `meet` (Q2), `ask_q1`, `budget`. **The day loop:** `play`, `step`, `next_event`, `advance`, `turn`, `after_turn`, `withdraw_why`. **Records:** `views`, `items` (the chronicle events), `transcript`, and `gap_line` (block A's Y8 and the bedtime line). |
| `world.py` | `Person.needs` (None before day 3). `levels()` gains `fast` and `debt` from day 3 on. `risen()` and `rise_words()` know them. `inside_lines()` writes the new body line and "Since you last decided, you have grown weaker." / "…more tired." `decide()` takes a pending quiet ask; it asks nobody once the 40 asks are spent; it gives no inner moment to someone resting or outside every talking room. `ask_model()` counts the day's asks. A silent turn keeps a routine's activity. `pattern()` does not count across a routine. `finish()` writes `transcript["quiet"]`. Every branch is guarded by `needs`/`quiet` being set, which happens only from day 3. |
| `night.py` | `next_day` calls `quiet.setup` for house day ≥ 6 (`night.py:814`). After a quiet day, a night adds no afternoon hunger, and its bedtime line is "Now it is night. " + the summary (`night.py:225`, `night.py:249`). Block A's Y8 is `quiet.gap_line` (`night.py:740`), which is `data.GAP` on a day not played to bedtime. |
| `chronicle.py` | `add_day` merges the spans and need crossings with the acts, by minute. `routine`/`until` and `need`/`stage` are kept on those events only (`QUIET_KEYS`). `gist` names a routine. |
| `mind.py` | `records()` stamps each record with `clock(minute)`. Below 90 that is the old "min 18" text. |
| `story.py` | `render_day2` adds "## After the morning" on a quiet day. Its end-of-day lines say "21:00" there. `fold_runs` does not fold across a jump. Days 1 and 2 render byte for byte as before (§6.3). |
| `morning.py` | Day 3 is played by `quiet.play`. The run log prints each Q1/Q2 check and its outcome. `meta["day3_quiet"]` holds the asks, spans, triggers and withdrawals. |
| `test_morning.py` | New `QuietDayTest` (27 tests). Three existing tests were updated for what this stage changes on day 3 (§3.3). |

**How a quiet day runs** (`quiet.play`, `quiet.py:631`):
1. **Played turns.** Turns are played until no room's conversation is active. A rest whose time is up ends even inside played turns (`quiet.py:490`).
2. **Quiet mode** at minute *t* (`step`):
   - the needs are ticked;
   - rests that ran out end;
   - everyone without a routine takes one, in family order (`assign`): rest if it is due, else sit in the kitchen. Each move is an arrival, checked for Q2. A sitter whose rest falls due goes to rest. Whoever keeps to their room stays;
   - Q1 is checked for the needs that crossed a line at *t*.
3. **A fired trigger** queues an ask for the person and starts that room's conversation. Played turns resume at *t*. A routine begun at *t* in that room is dropped: that person is in the talk.
4. **Otherwise the day jumps** to `next_event`: the earliest of a rest running out, a fasting or debt line, a rest falling due for a sitter, and 21:00. Every jump lands on the 3-minute grid. Hunger is advanced across the jump; fasting and debt are counted from the clock.
5. **At 21:00** every span is closed, with "bedtime" as its end.

## 2. Spec points not built as written, and why

Each item gives the spec, then what was built and why.

1. **§1.2, "paid back by the night's choice."** The debt uses the bedtime choice.
   - On v16 night 2, Mara got up and waited by the front door (`get_up_and_look`). She still counts as `lie_awake` (3).
   - That is what §6's hand values assume (Mara 22), and DONE 2 requires them. A real Mara slept less than that.
2. **§1.1, weak: "rest is preferred when quiet".** §2.2's rule is built as written: rest starts at debt ≥ 16 or fasting ≥ 96. Weakness alone starts no rest. §6.1's timeline agrees: Elena, not tired, sits.
3. **§2.2, "until debt < 12".**
   - A rest begun with debt already below 12 can only come from fasting ≥ 96. Such a rest lasts its seeded length; read literally, it would end at once.
   - Days 3 to 7 only; no day-3 case reaches it.
4. **§2.2, "at most twice a day and at least 2 hours apart".** The 2 hours run from the end of one rest to the start of the next. A rest cut short still counts. One that ended the minute it began does not.
5. **§2.1, the trait gate.** It is written as thresholds, `dominant ≥ 0.8` or `empathetic ≥ 0.85` (`quiet.py:37`). That keeps exactly Daniel (0.85) and Elena (0.9) in the room.
6. **§2.1, "they chose `silent`".** This means a model decision of `silent`. A routine silence, when the model was not asked, is not a choice.
7. **§2.2, the interruptions of a rest:**
   - **An arrival with a Q2 grievance:** it wakes the person asked.
   - **"Voices of a new line through the wall":** the existing trigger asks the resting person in the played turn, and the rest ends only if they then speak or move. A real person woken by voices may lie still.
   - **"The front door": NOT BUILT.** The front door never opens by day in stage A, since keep watch, watch the street and day trips are out of scope.
8. **§2.1, the interruptions of a withdraw.** Anyone coming in ends it, whether a routine or a model move brings them, as §6.1 has it (Leo's withdraw ends when Daniel comes in to rest). Voices work as for a rest.
9. **Spans outside the played room.** They go on through a played stretch. Any act other than `silent` ends them. A rest still ends on time inside the stretch, but that person's next routine waits until quiet mode.
10. **§3, witnesses.** The rule is "in the room at its start or its end". Added to it: whoever saw the person leave for it. §2.1 itself says "The others see 'Leo goes to the brothers room'", and those people perceived the move. Someone resting is asleep, so they are not a witness and do not count as awake company for Q1.
11. **§4 Q1.**
    - Reaching debt 16 is recorded only, since Q1 lists only 24.
    - A crossing during played turns is that person's inner moment, as §6.1 says for Mara, and never a Q1 afterwards.
    - A crossing while the person is resting is recorded as "asleep".
    - "Once per person per threshold" counts fired asks.
12. **§4 Q2.**
    - "Exchanged a line" means a spoken line by either one with the other in the room; voices through a wall do not count.
    - Simultaneous arrivals are taken in family order, so one who came in earlier at the same minute counts as already there (B).
    - A fired Q1 or Q2 starts that room's conversation, as an arrival does today. That is what lets the addressed reply be played (§4: "the existing addressed-first order plays the reply").
13. **§4, the budget.**
    - A quiet ask counts toward 12 (and 4 each) when the trigger lets it through. So the cap holds even if that person ends up not asked.
    - Day asks count every model call by day, aside and give answers included. Once 40 are spent, those answers fall back with "the day's asks are spent".
14. **Amendment 3, scope.** The clock is in records, block A's summary line and the bedtime line. **NOT changed:**
    - prompts ("Now, minute 201", "min 201: …" memory lines, "admitted taking it at minute 162");
    - block A's minute lists in Y3 to Y6 ("(min 03, 06)").
    - Both keep today's format above minute 99.
15. **§3, block A and bedtime.** Built and tested on a fake night 3 (`test_block_a_and_bedtime_say_the_day_after_the_morning`). `morning.py` still stops after day 3, so no live run reaches a night 3. The chronicle still adds a G event ("The afternoon and evening passed…") before a night that follows a quiet day. No prompt reads G events.
16. **Added, not in the spec: a routine breaks a run** (`world.py:938`, `quiet.py` `start`). Without it, a prompt after a 2½-hour rest said "you have stayed put and said nothing, 8 turns in a row", counting turns from before the rest. A speech act held back after three turns was also still held back hours later. Now a routine ends the run.
17. **Added: whoever a routine moves gets their own line** ("you went to the kitchen."). Without it, Elena's prompt went from "you got up from your bed" straight to being in the kitchen.

## 3. The tests

### 3.1 New: `QuietDayTest` (27)

Every day-3 test starts from v16 seed 2, replayed from its own answers through night 2 and mind 2. The harness asserts 0 live answers and 0 fake requests before day 3. Fakes:
- `HushFake`: silent two times in three, so the morning's talk ends;
- `TalkFake`: always a speech option it has not used yet, optionally from a given minute on;
- `PolicyFake`: a scripted policy.

| Spec | Test |
|---|---|
| §1.1, §6 | `test_fasting_at_day_3_0700_is_section_6s` |
| §1.2, §6 | `test_sleep_debt_at_day_3_0700_is_section_6s` |
| §1.1, §1.2 | `test_the_body_line_states_each_stage` |
| amendment 3 | `test_records_show_the_clock_from_minute_90` |
| §2.2, §3, DONE 1 | `test_the_quiet_day_runs_to_bedtime_with_a_rest_for_everyone` (≥ 1 and ≤ 2 rests each, in their own room; first return times differ; 2 hours apart; no empty span; every jump on the grid; nothing after 21:00) |
| amendment 2 | `test_rest_lengths_are_seeded_between_2_and_4_hours` |
| §2.2 | `test_a_rest_ends_once_debt_is_below_12` |
| §3 | `test_needs_advance_exactly_across_the_jumps` (debt at 21:00 = start + awake hours − 1.5 × rest hours) |
| §3 (added, §2 items 16 and 17) | `test_a_routine_breaks_a_run_and_its_move_is_remembered` |
| §2.1, DONE 1 | `test_leo_withdraws_after_his_say_when_he_falls_silent`, `test_a_withdraw_into_a_room_with_a_grievance_is_a_meeting`, `test_no_withdraw_without_a_grudge_of_3`, `test_no_withdraw_when_the_one_held_against_is_not_in_the_room`, `test_daniel_and_elena_never_withdraw`, `test_every_withdraw_of_the_day_had_every_condition` (Mara, who stayed silent without having spoken, does not withdraw in the first one) |
| §4 Q2, DONE 1 | `test_q2_fires_on_an_arrival_after_60_quiet_minutes_and_not_before` (57 minutes: no; 60: yes), `test_q2_once_per_pair_in_2_hours` (117: no; 120: yes), `test_q2_asks_the_higher_grudge_and_the_one_already_there_on_a_tie`, `test_every_q2_of_the_day_came_after_an_hour_apart` |
| §4 Q1 | `test_q1_asks_only_with_someone_awake_there_and_once` (Mara weak at 10:27: alone, no; with Elena resting, no; with Elena awake, yes; again, no) |
| §4 budget, DONE 1 | `test_the_day_budget_holds_when_the_fake_keeps_talking` (exactly 40; the conversation ends with "the day's asks are spent"; routines run to 21:00), `test_the_quiet_asks_hold_at_12_and_4_each` |
| §4 | `test_quiet_mode_asks_the_model_only_through_a_trigger` (every played turn is in a stretch; every stretch after the morning starts at a fired trigger in its room; nobody starts a routine there at that minute) |
| §3 | `test_each_span_is_a_chronicle_event_with_its_witnesses`, `test_block_a_and_bedtime_say_the_day_after_the_morning`, `test_the_story_shows_the_quiet_day` |
| DONE 3 | `test_v16_through_night_2_is_unchanged` (a guard: it passed before the change too, §4.1) |

### 3.2 RED first

- **The 25 first tests** were run against an empty `quiet.py` (docstring only), so each failure is the missing behaviour, not an import error (§4.1):
  - 23 ERROR: `Morning` has no `quiet`, or `quiet` has no `play`, `clock` or `rest_length`;
  - 1 FAIL: the old body line;
  - 1 ok: the DONE 3 guard.
- **Four later tests** came from reading the sample day (§4.2). Each was seen failing on the defect first:
  - an empty span;
  - a routine begun in the room where the talk started;
  - a Q2 that a withdraw fired but `after_turn` dropped;
  - a run counted across a rest.

### 3.3 Existing tests changed, and why

- `DaysTest.test_n_t2_the_cycle`: day 3 had `30` turns. It is now a quiet day, so the test asserts its last span ends at 840 and its day asks are ≤ 40.
- `DaysTest.test_n_t9_the_chronicle`: event keys were capped at `EVENT_KEYS`. §3 adds `routine` and `until` to span events, so the cap is widened for `routine`/`need` events only.
- `WitnessScenarioTest.test_no_prompt_says_who_leo_heard`: a regex assumed two-digit minutes ("at minute \d\d"). A confession in an afternoon stretch reads "at minute 162", so it now allows 2 or 3 digits.

## 4. RED, GREEN and the defects the sample day showed

### 4.1 RED: the first 25 tests against an empty `quiet.py`

```
$ printf '"""The quiet day (reports/quiet_day_design.md): not built yet."""\n' > quiet.py
$ timeout 900 env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.QuietDayTest < /dev/null
test_a_rest_ends_once_debt_is_below_12 ... ERROR
test_block_a_and_bedtime_say_the_day_after_the_morning ... ERROR
test_daniel_and_elena_never_withdraw ... ERROR
test_each_span_is_a_chronicle_event_with_its_witnesses ... ERROR
test_every_q2_of_the_day_came_after_an_hour_apart ... ERROR
test_every_withdraw_of_the_day_had_every_condition ... ERROR
test_fasting_at_day_3_0700_is_section_6s ... ERROR
test_leo_withdraws_after_his_say_when_he_falls_silent ... ERROR
test_needs_advance_exactly_across_the_jumps ... ERROR
test_no_withdraw_when_the_one_held_against_is_not_in_the_room ... ERROR
test_no_withdraw_without_a_grudge_of_3 ... ERROR
test_q1_asks_only_with_someone_awake_there_and_once ... ERROR
test_q2_asks_the_higher_grudge_and_the_one_already_there_on_a_tie ... ERROR
test_q2_fires_on_an_arrival_after_60_quiet_minutes_and_not_before ... ERROR
test_q2_once_per_pair_in_2_hours ... ERROR
test_quiet_mode_asks_the_model_only_through_a_trigger ... ERROR
test_records_show_the_clock_from_minute_90 ... ERROR
test_rest_lengths_are_seeded_between_2_and_4_hours ... ERROR
test_sleep_debt_at_day_3_0700_is_section_6s ... ERROR
test_the_body_line_states_each_stage ... FAIL
test_the_day_budget_holds_when_the_fake_keeps_talking ... ERROR
test_the_quiet_asks_hold_at_12_and_4_each ... ERROR
test_the_quiet_day_runs_to_bedtime_with_a_rest_for_everyone ... ERROR
test_the_story_shows_the_quiet_day ... ERROR
test_v16_through_night_2_is_unchanged ... ok
Ran 25 tests in 4.574s
FAILED (failures=1, errors=23)
      1 AssertionError: {'dan[21 chars]rving.', 'elena': 'Your body: starving.', 'leo[53 chars]ng.'} != {'dan[21 chars]rving, and weak from it: standing up makes you[306 chars]pt.'}
     11 AttributeError: 'Morning' object has no attribute 'quiet'
      1 AttributeError: module 'quiet' has no attribute 'clock'
     10 AttributeError: module 'quiet' has no attribute 'play'
      1 AttributeError: module 'quiet' has no attribute 'rest_length'
```
(Before that, with no `quiet.py` at all: `25 ModuleNotFoundError: No module named 'quiet'`, `FAILED (errors=25)`.)

### 4.2 Four defects found by reading the sample day, each a failing test first

**1. Empty spans.** Someone who walked into a room as a trigger started the talk got a span "10:18 to 10:18".
```
FAIL: test_the_quiet_day_runs_to_bedtime_with_a_rest_for_everyone
AssertionError: Lists differ: [{'who': 'daniel', 'routine': 'sit', 'room[383 chars]one}] != []
-   'end': 198, 'ended': 'acted', ... 'routine': 'sit', ... 'start': 198, 'who': 'daniel'},
```

**2. A routine in the talking room.** Daniel lay down at min 09 in the room where Leo's Q2 had just started the talk, because the assignment loop picked him up again.
```
FAIL: test_quiet_mode_asks_the_model_only_through_a_trigger
{'who': 'daniel', 'routine': 'rest', 'room': 'brothers_room', 'start': 9, 'end': 198, ...} : {'start': 9, 'end': 18, 'room': 'brothers_room', 'trigger': 'Q2'}
```
After the first fix, the same test caught a second form: Leo sat down in the kitchen just before Mara's arrival fired a Q2 there. Now any routine begun at the minute its room starts talking is dropped (`step`).

**3. A withdraw's Q2 was dropped.** The withdraw fired the Q2, but `after_turn` cleared pending asks after the withdraw loop.
```
ERROR: test_a_withdraw_into_a_room_with_a_grievance_is_a_meeting
KeyError: 'mara'
```
The first run of this test failed for a reason in the test itself: its hand-made grudge had no `last_change`, so it fell at once. That was fixed in the test before this run.

**4. A run counted across a rest, and a move nobody remembered making.**
```
FAIL: test_a_routine_breaks_a_run_and_its_move_is_remembered
AssertionError: (30, 'you went to the brothers room.') not found in []
```

### 4.3 GREEN

```
$ timeout 900 env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning.QuietDayTest < /dev/null
Ran 27 tests in 11.334s
OK
```

## 5. A sample fake day 3 (v16 seed 2, after night 2)

Made by `$S/sample_day3.py` (§6.6), with `HushFake`.
- **The opening is the v16 state.** Leo → Daniel 3, Mara → Daniel 3. All four are tired; Daniel is exhausted; Daniel and Leo are weak.
- **The fake adds grudges.** Its `angry_at` answers are random, which is where Elena's and Mara's grudges against each other come from.
- **What it shows:** rests ending at different times, both Q2 outcomes ("asked" and "a line between them 3 minutes before", "they met this way 9/27 minutes before"), a Q1 asked, need crossings, and the 40-ask cap.

**The run log** (`$S/sample/hush.log`; "(Q2)" marks the asks a trigger made):
```
daniel_ate_it-seed2: days 1-2, nights 1-2 and minds 1-2 from the cache: 96 answers, 0 live, 0 fake requests
  day 3 min 00: model asked for 4: leo, daniel, mara, elena; day asks 4
  day 3 min 03: model asked for 3: mara, elena, daniel; day asks 7
  day 3 min 06: model asked for 3: mara, daniel, elena; day asks 10
  day 3 min 09: model asked for 3: leo (Q2), daniel, mara (Q2); day asks 13
  day 3 min 12: model asked for 2: elena, mara; day asks 15
  day 3 min 15: model asked for 2: daniel, leo; day asks 17
  day 3 09:42: model asked for 3: elena (Q2), mara (Q2), leo; day asks 20
  day 3 09:45: model asked for 3: leo, elena, mara; day asks 23
  day 3 09:48: model asked for 3: mara, elena, daniel; day asks 26
  day 3 09:51: model asked for 2: elena, daniel; day asks 28
  day 3 09:54: model asked for 3: elena, leo, daniel; day asks 31
  day 3 09:57: model asked for 2: elena, leo; day asks 33
  day 3 10:00: model asked for 1: mara; day asks 34
  day 3 10:27: model asked for 3: mara (Q1), leo, elena; day asks 37
  day 3 10:30: model asked for 3: mara, daniel, elena; day asks 40
  morning ended min 09; asks: {'day': 40, 'quiet': 5, 'quiet_by_person': {'daniel': 0, 'elena': 1, 'leo': 1, 'mara': 3}, 'quiet_let_through': 5}
  daniel: After the morning: you lay on your bed in the brothers room (min 18 to 09:51); you sat in the kitchen (10:09 to 11:51); you lay on your bed in the brothers room (11:51 to 14:48); you sat in the kitchen with Elena and Leo (14:48 to 21:00). Nobody ate.
  elena: After the morning: you lay on your bed in the back room (min 18 to 09:42); you sat in the kitchen with Daniel (10:09 to 11:42); you lay on your bed in the back room (11:42 to 14:36); you sat in the kitchen with Leo (14:36 to 21:00). Nobody ate.
  leo: After the morning: you lay on your bed in the brothers room (min 18 to 09:42); you sat in the kitchen with Daniel and Elena (10:09 to 11:42); you lay on your bed in the brothers room (11:42 to 13:45); you sat in the kitchen (13:45 to 21:00). Nobody ate.
  mara: After the morning: you lay on your bed in the back room (min 18 to 09:42); you sat in the kitchen with Daniel, Elena and Leo (10:09 to 11:42); you lay on your bed in the back room (11:42 to 14:51); you sat in the kitchen with Daniel, Elena and Leo (14:51 to 21:00). Nobody ate.
```
The last four lines are `gap_line`. On the next day they become block A's Y8 line, and at bedtime they follow "Now it is night.".

**The story's new section** (`$S/sample/daniel_ate_it-seed2-hush.day3.md`):
```
## After the morning

The morning's talk ended at min 09.

- min 00 to min 09: played turns (the morning, in the kitchen).
- min 09: **Q2**, Daniel comes into the brothers room, where Leo is (no line between them yet today; Daniel holds 0, Leo holds 3): Leo is asked.
- min 09: **Q2**, Mara comes into the back room, where Elena is (no line between them yet today; Mara holds 2, Elena holds 1): Mara is asked.
- min 09 to min 18: played turns (Q2, in the brothers room).
- min 18 to 09:51: Daniel lies on his bed in the brothers room (until he spoke or moved).
- min 18 to 09:42: Elena lies on her bed in the back room (from the bathroom; up when its time was out).
- min 18 to 09:42: Leo lies on his bed in the brothers room (up when its time was out).
- min 18 to 09:42: Mara lies on her bed in the back room (up when its time was out).
- min 18: **Q2**, Elena comes into the back room, where Mara is (no line between them yet today; Elena holds 1, Mara holds 2): not asked: they met this way 9 minutes before.
- 09:42: **Q2**, Leo comes into the kitchen, where Elena is (no line between them yet today; Leo holds 0, Elena holds 2): Elena is asked.
- 09:42: **Q2**, Mara comes into the kitchen, where Elena is (no line between them yet today; Mara holds 2, Elena holds 1): Mara is asked.
- 09:42 to 10:09: played turns (Q2, in the kitchen).
- 10:03: Elena's sleep debt reaches 16.05: tired.
- 10:09 to 10:30: Daniel sits in the kitchen (until he spoke or moved).
- 10:09 to 10:30: Elena sits in the kitchen (from the brothers room; until she spoke or moved).
- 10:09 to 11:42: Leo sits in the kitchen (from the bathroom; until he went to rest).
- 10:09 to 10:27: Mara sits in the kitchen (from the brothers room; until she spoke or moved).
- 10:09: **Q2**, Mara comes into the kitchen, where Elena is (no line between them yet today; Mara holds 0, Elena holds 3): not asked: they met this way 27 minutes before.
- 10:27: Mara's fasting reaches 48.022: weak.
- 10:27: **Q1**, Mara has grown weak, in the kitchen: Mara is asked.
- 10:27 to 10:33: played turns (Q1, in the kitchen).
- 10:33 to 11:51: Daniel sits in the kitchen (from the brothers room; until he went to rest).
- 10:33 to 11:42: Elena sits in the kitchen (from the bathroom; until she went to rest).
- 10:33 to 11:42: Mara sits in the kitchen (until she went to rest).
- 10:33: **Q2**, Elena comes into the kitchen, where Daniel is (no line between them yet today; Elena holds 3, Daniel holds 0): not asked: the day's 40 asks are spent.
- 10:33: **Q2**, Elena comes into the kitchen, where Mara is (their last line at 10:30; Elena holds 2, Mara holds 1): not asked: a line between them 3 minutes before.
- 11:42 to 14:36: Elena lies on her bed in the back room (from the kitchen; up when its time was out).
- 11:42 to 13:45: Leo lies on his bed in the brothers room (from the kitchen; up when its time was out).
- 11:42 to 14:51: Mara lies on her bed in the back room (from the kitchen; up when its time was out).
- 11:42: **Q2**, Mara comes into the back room, where Elena is (their last line at 10:30; Mara holds 1, Elena holds 2): not asked: the day's 40 asks are spent.
- 11:51 to 14:48: Daniel lies on his bed in the brothers room (from the kitchen; up when its time was out).
- 13:45 to 21:00: Leo sits in the kitchen (from the brothers room; until bedtime).
- 14:36 to 21:00: Elena sits in the kitchen (from the back room; until bedtime).
- 14:48 to 21:00: Daniel sits in the kitchen (from the brothers room; until bedtime).
- 14:48: **Q2**, Daniel comes into the kitchen, where Elena is (no line between them yet today; Daniel holds 0, Elena holds 3): not asked: the day's 40 asks are spent.
- 14:51 to 21:00: Mara sits in the kitchen (from the back room; until bedtime).
- 14:51: **Q2**, Mara comes into the kitchen, where Elena is (their last line at 10:30; Mara holds 1, Elena holds 2): not asked: the day's 40 asks are spent.
- 14:54: Mara's sleep debt reaches 16.025: tired.
- 17:15: Elena's sleep debt reaches 16: tired.
- 19:45: Daniel's sleep debt reaches 24: exhausted.
- 19:45: **Q1**, Daniel has grown exhausted, in the kitchen: not asked: the day's 40 asks are spent.
- 20:09: Leo's sleep debt reaches 24.025: exhausted.
- 20:09: **Q1**, Leo has grown exhausted, in the kitchen: not asked: the day's 40 asks are spent.

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Fasting at 07:00 | 59.8 | 20.4 | 60 | 44.745 |
| Sleep debt at 07:00 | 25 | 19 | 22 | 22 |
| Fasting at 21:00 | 75.9 | 32.3 | 74 | 58.045 |
| Sleep debt at 21:00 | 25.25 | 19.75 | 24.875 | 22.125 |

Asks this day: 40 of 40; quiet asks 5 of 12 (Daniel 0, Elena 1, Leo 1, Mara 3).
```

**`morning.py`'s own run log** for a fresh fake run (seed 1, temp folders; `$S/fakerun.log`) shows both Q2 outcomes live:
```
  day 3 min 24: Q2, Elena comes into the back room, where Leo is: not asked (a line between them 9 minutes before)
  day 3 min 24: Q2, Leo comes into the brothers room, where Daniel is: not asked (a line between them 18 minutes before)
  day 3 09:00: Q2, Mara comes into the back room, where Elena is: Elena is asked
  day 3 09:00: model asked for 1, Q2 for Elena; day asks 25 of 40; so far 218 live, 0 cached, 218 API requests
  ...
  day3 day_asks: 40
  day3 quiet_asks: 2
  day3 q2_fired: 2
  day3 spans: 17
  day3 rests: 8
  day3 stretches: 3
```
("API requests" here are the fake client's requests: the run used `fake=True`.)

**What a hand reading of these days shows.** These are clues to judge, not results.
- **The 40 asks are spent by mid-morning.** It happened at 10:30 in the sample and at 09:15 in the seed-1 run, after which the day is routines only.
  - A played stretch asks everyone in the talking room who heard a line, as the morning does. One Q2 stretch cost 10 to 21 asks with these fakes.
  - With a real model this may differ, but P6 (a model act at or after 16:00 on ≥ 10 of 15 days) is at risk.
- **A sulking person bounces.** In an earlier sample, Mara withdrew at 10:36, a grudge of 3 against Daniel. Elena came in to lie down at 11:33. That ended the withdraw (§2 item 8). Rest was not allowed yet (2 hours since her last), so §2.5 sent her to sit in the kitchen with Daniel, and 9 minutes later she went back to bed.
  - A real girl who walked out on her brother would not walk back to him because her mother came in.
  - The rules do it because §2.5's default is the kitchen. That chain is the spec's; it is reported, not changed.
- **Records stamp a span at its start.** A witness who saw only its end reads, for example, "10:09: Leo was sitting in the kitchen at 11:42." The line says when they saw it, but the stamp is the start (§2 item 10).

## 6. Commands and raw output

All from `Prototypes/llm-morning/`.

### 6.1 The HEAD baseline, before any change (`$S/replay_prefix.py`)

The script replays v16 day 1, night 1, mind 1, day 2, night 2 and mind 2 from a copy of `cache/v16`, with `replay=True`, so a miss would stop it. It writes the story and transcript of those scenes, and compares the story with the original's text before "# The third morning (day 6)".
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/replay_prefix.py" "$PWD" "$S/before"; echo "exit $?"
daniel_ate_it-seed1: 98 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: DIFFERS
daniel_ate_it-seed2: 96 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: IDENTICAL
daniel_ate_it-seed3: 135 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: IDENTICAL
exit 0
```
Seed 1 differs from the original by the S4/S8 change (543e325), already at HEAD:
```
$ .venv/Scripts/python.exe - "$S"   (difflib of runs/v16 seed 1's prefix against $S/before)
--- original
+++ replay at HEAD
@@ -571 +571 @@
-  - D2-004, D2-014: "Mom told me not to go out into the dark again and that we will get through this together inside." **rejected: S8 elena stop: not twice**
+  - D2-004, D2-014: "Mom told me not to go out into the dark again and that we will get through this together inside." **kept**
@@ -580 +580 @@
-  - D2-003, D2-012: "Daniel thinks grand promises make up for reckless risks, but coming back empty-handed solves nothing." **rejected: S8 daniel give: no such event**
+  - D2-003, D2-012: "Daniel thinks grand promises make up for reckless risks, but coming back empty-handed solves nothing." **kept**
```

### 6.2 The quiet-day tests

§4.1 to §4.3.

### 6.3 DONE 3: the same replay after the change

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/replay_prefix.py" "$PWD" "$S/after"; echo "exit $?"
daniel_ate_it-seed1: 98 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: DIFFERS
daniel_ate_it-seed2: 96 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: IDENTICAL
daniel_ate_it-seed3: 135 answers from the cache, 0 live, 0 API requests; story through night 2 against the original's prefix: IDENTICAL
exit 0
$ for f in daniel_ate_it-seed{1,2,3}; do for x in md transcript.json; do cmp -s "$S/before/$f.$x" "$S/after/$f.$x" && echo "$f.$x: before (HEAD) vs after: IDENTICAL" || echo "$f.$x: DIFFERS"; done; done
daniel_ate_it-seed1.md: before (HEAD) vs after: IDENTICAL
daniel_ate_it-seed1.transcript.json: before (HEAD) vs after: IDENTICAL
daniel_ate_it-seed2.md: before (HEAD) vs after: IDENTICAL
daniel_ate_it-seed2.transcript.json: before (HEAD) vs after: IDENTICAL
daniel_ate_it-seed3.md: before (HEAD) vs after: IDENTICAL
daniel_ate_it-seed3.transcript.json: before (HEAD) vs after: IDENTICAL
$ sha256sum "$S"/before/*.md "$S"/after/*.md
c31c0c57a32c1cd8a54fc0bfd2bdba65b67d78b712901d88a83d1f54892d1c87 *before/daniel_ate_it-seed1.md
bdaa0a9f3e69062f380480bd98e04d508bf6c2206549ddb1a6bf2bdf64a859fc *before/daniel_ate_it-seed2.md
12d14885bb295acccb429bf0c632d084dca488ea0dc7588e589154917f2bfa45 *before/daniel_ate_it-seed3.md
c31c0c57a32c1cd8a54fc0bfd2bdba65b67d78b712901d88a83d1f54892d1c87 *after/daniel_ate_it-seed1.md
bdaa0a9f3e69062f380480bd98e04d508bf6c2206549ddb1a6bf2bdf64a859fc *after/daniel_ate_it-seed2.md
12d14885bb295acccb429bf0c632d084dca488ea0dc7588e589154917f2bfa45 *after/daniel_ate_it-seed3.md
$ ls -l --time-style=full-iso cache/v16/
... 2026-10-06 10:19:49 gemini-3.5-flash-lite-daniel_ate_it-seed1.json
... 2026-10-06 10:24:17 gemini-3.5-flash-lite-daniel_ate_it-seed2.json
... 2026-10-06 10:32:41 gemini-3.5-flash-lite-daniel_ate_it-seed3.json
$ git status --short cache runs
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
```
The three `runs/v6` files were untracked before this session began, as the session's opening git status shows. `cache/` shows no change.

### 6.4 DONE 4: the frozen versions, v14 to v9

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v14/check.py; echo "exit $?"
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v13/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 91 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 87 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v12/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v11/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v10/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v9/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
```
18 of 18 are IDENTICAL, so there are no differences to list.

### 6.5 DONE 4: the full suite

```
$ time env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning < /dev/null; echo "exit $?"
.................................................................    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
.    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
.......................................................................................................……
Ran 217 tests in 183.518s

OK

real	3m4.667s
exit 0
```
- **The `[429 RESOURCE_EXHAUSTED]` lines** come from `GeminiClientTest`'s stub API, not from real requests.
- **217 tests, up from 190:** the 27 new ones.
- **Earlier full runs,** kept in `$S/full1.txt` to `$S/full3.txt`, failed and were fixed before this one:
  - 30 errors: the `quiet` parameter of `morning.run` shadowed the module;
  - N-T9's key cap;
  - the witness regex (§3.3).

### 6.6 The sample days

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/sample_day3.py" "$PWD" "$S/sample" 2 hush   > "$S/sample/hush.log"     # exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/sample_day3.py" "$PWD" "$S/sample" 2 talk   > "$S/sample/talk.log"     # exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/sample_day3.py" "$PWD" "$S/sample" 2 talk60 > "$S/sample/talk60.log"   # exit 0
$ grep "morning ended" "$S/sample/talk.log" "$S/sample/talk60.log"
talk.log:  morning ended min 30; asks: {'day': 40, 'quiet': 0, 'quiet_by_person': {'daniel': 0, 'elena': 0, 'leo': 0, 'mara': 0}, 'quiet_let_through': 0}
talk60.log:  morning ended min 09; asks: {'day': 40, 'quiet': 4, 'quiet_by_person': {'daniel': 1, 'elena': 1, 'leo': 1, 'mara': 1}, 'quiet_let_through': 4}
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -c "import sys; from morning import run; meta, code = run(1, fake=True, runs_dir=sys.argv[1], cache_dir=sys.argv[2]); print('exit', code)" "$S/fakerun/runs" "$S/fakerun/cache" > "$S/fakerun.log"   # exit 0
```
- **`talk`:** the fake talks from minute 00, so the morning itself spends the 40 asks, and its conversation ends with "the day's asks are spent".
- **`talk60`:** the fake is silent until minute 60, so the asks are spent in Q2 stretches instead, with 4 quiet asks let through. Both stay within 40 and 12.
