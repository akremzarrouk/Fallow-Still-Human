# Implementation: the trip concern (v11)

Mode: implement. This builds reports/trip_design.md, sections 1 to 4, with the trip block kept
outside the prompt budget (§2.5), and the tests of §8. No API was called. Every command ran
with `GEMINI_API_KEY` unset. Paths are relative to `Prototypes/llm-morning/`. `$S` is the
session scratchpad (`…/scratchpad/trip`).

## Result

| Done when | Status |
|---|---|
| The new tests fail before the change | **Yes.** 23 of the 24 new tests fail or error on the code before the change (§3). T13 passes there, as it should: it guards the v10 freeze, which was committed first. |
| …and pass after | **Yes.** 24 of 24 (§4). |
| The full suite passes | **Yes.** `Ran 114 tests`, `OK`, exit 0 (§4). That is the 90 earlier tests plus 24 new ones. |
| The v10 runs replay identically from their frozen copy with 0 requests | **Yes.** `v10/check.py`: 3 × "story IDENTICAL, transcript IDENTICAL", 0 API calls (§5). `v9/check.py` also still replays. |
| The pairing tests pass | **Yes.** T3 (the v10 caches pair until the trigger) and the existing v6 pairing test both pass (§4). §5 shows the first post-trigger prompt of each seed against v10. |
| git status clean apart from the three old replay.md files | **Yes** (§6). |

**Commits:**
- `9e3009e`: freeze v10; new runs default to v11.
- `fc572d7`: the implementation and its tests.


## 1. What was built, against the design

| Design | Where |
|---|---|
| §1 trigger | `TRIP_HUNGER = 2`. `Morning.start_trip`, called first in `turn`, before anyone acts. On an empty shelf it asks everyone in the kitchen; on hunger, whoever is very hungry. It fires once. |
| §1 trip moment | `decide` sets `d["trip_moment"]` (the trigger minute) for whoever it asks, and asks them whatever the inner-moment spacing. An inner moment that is due is still recorded. A lull cannot land on a trip moment. |
| §2.1 lines | `data.ABOUT_FOOD`, `data.ABOUT_NEIGHBOUR`, placed by `trip_lines` after the "About the can:" line. The plan line (`heard_plan`) appears only once the person has heard a trip act. |
| §2.2 house | `data.HOUSE_THINGS_AFTER_TRIP`: "not to be gone to this morning:", used after the trigger. |
| §2.3 day-2 memories | `data.TRIP_MEMORIES` (backstory events 4–6) and `Person.trip_memories`. After the trigger, trimming removes the oldest other events, down to the same 4. |
| §2.5 budget | `prompt_for` counts the block's characters (its lines, its option lines, the three day-2 lines and the 13 characters of " this morning"). It checks `estimate_tokens(SYSTEM + text, less=block)` against the budget. Before the trigger the block is 0, so the check is the same as before. |
| §3.1 options | `trip_options`, inserted between `reassure_all` and `say_other`. `named_to_go` gives the `object_<q>` rule. |
| §3.2 effects | `apply`: the record (`trip_acts`, `trip_heard`, `proposed`, `trip_raised`), the line each listener hears (`line_text`), and the speaker's own line without the words (`mine`). Nothing else changes. |
| §3.2 pattern | `KIND_DONE` and `heard_verb` entries. |
| §3.3 talk | `SPEECH` gains five kinds. `act_of`, `aimed_at`, and `Newness.line` (with `TRIP_WHY`). |
| §4.1 record | `transcript["trip"]` with `acts` and `plan` (or `null`), `"trip_moment"` on every act, meta `trip_minute` and `trip_acts`, printed in the console summary. |
| §4.3 story | A "**The food**: …" decision line, a key line, and the two closing bullets: "The food" and "The plan for tonight". |
| §8 tests | `TripTest` (T1–T13) and the changes to existing tests listed in §2 below. |

## 2. Choices the design left open, and where this differs from it

These are listed so they can be checked. None changes what the design specifies.

1. **The test switch.** The design mentions one (T2). It is `world.TRIP_ON` (True). Tests set it
   False with `mock.patch`.
2. **`d["trip_why"]`.** This is the trigger's reasons, kept on a trip-moment decision so the
   story can write "**The food**: …". It is output only.
3. **The story's decision line** when a trip moment coincides with an inner moment or a social
   trigger: "**The food**: <why>; also an inner moment: …" or "…; also a social moment: …". The
   design said only "written like an inner moment".
4. **The story key line** (my wording): "- **The food** (once per morning): at the start of the
   first turn when the shelf is empty or someone is very hungry, everyone learns … What brought
   it on is listed." It does not contain "**The food**: ", so T10 can count decision lines by
   that string.
5. **The plan line with three or more volunteers.** The design gives "one" and "two or more:
   `<A> and <B> have both offered to go`". The code writes "both" for two and "`<A>, <B> and <C>`
   have all offered to go" for three or four.
6. **One mismatch inside §4.3.** Its clause table says `<X> said someone should go`, and its
   second example says "Leo said someone should". The code and T9 follow the table.
7. **The budget is exact only when the backstory is cut down to 4.** §2.5 says the rest of the
   prompt keeps exactly the memory it would have kept.
   - That holds when the backstory is trimmed to its 4 most recent events. That was the case
     in every v10 prompt after minute 21 (trip_design.md §13 command 2), and §5 below shows
     every morning line kept in all three first post-trigger prompts.
   - When a prompt is not cut that far, the three day-2 lines no longer count against the
     budget. A post-trigger prompt can then keep an older backstory line that the same
     prompt without the trip would have dropped. The first draft of T12 hit this case.
   - It never keeps less than it would have. T12 now tests the case the design describes.
8. **`estimate_tokens(text, less=0)`.** It gains an optional argument for the block's
   characters. With `less=0` it is the old function.

**Existing tests changed**, with the reason for each:

| Test | Change | Why |
|---|---|---|
| `FakeMorningTest.test_prompts_are_short` | `< 1450` now applies to the prompt without its trip block. The full prompt must be `< 1450 + 380`. | §2.5 and §8 T12, which say these two bounds change. |
| `FakeMorningTest.test_an_admission_cannot_be_taken_back` | The same two bounds. | The same. |
| `without_lull` (helper) | Also removes `trip_moment` from each act. | Every act has the new key (§4.1). It is used to compare with the v6 and v10 transcripts. |
| `DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought` | The expected act keys gain `trip_moment`. | The same new key. It failed before the change, as it should (§3). |
| `OwnWordsTest.test_prompts_before_someone_has_spoken_are_unchanged` | The new side runs with `TRIP_ON = False`. | It compares with frozen v9 code, which has no trip. In fake seed 5 both portions are eaten at minute 00, so the trip starts at minute 03, the very turn it compares (command in §4). It failed in the first full run after the change and passes with the switch. The test is about hidden own words, not the trip. |

**Mistakes in my own new tests, fixed before the final "before" run:**
- T4 searched pre-trigger prompts for "this morning:", which also matches the existing heading
  "What you are sure of this morning:". It now searches for "to be gone to this morning:".
- T5 and T12 used filler lines too short to force the backstory down to 4.
- T8 set `knows_culprit` without `confession_heard_at`, a state the code never makes.

The "before" output in §3 is a second run of the corrected tests, on the stashed pre-change
code.

## 3. Tests before the change

The corrected tests were run on the code as it stood before the change. The implementation
files were stashed and `test_morning.py` kept, then the stash was restored:

```
$ git stash push -q -- world.py talk.py data.py story.py morning.py
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.TripTest test_morning.FakeMorningTest.test_prompts_are_short test_morning.FakeMorningTest.test_an_admission_cannot_be_taken_back test_morning.DecisionFormatTest
test_t10_recording (test_morning.TripTest.test_t10_recording) ... ERROR
test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger (test_morning.TripTest.test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger) ... ERROR
test_t12_the_block_sits_outside_the_budget (test_morning.TripTest.test_t12_the_block_sits_outside_the_budget) ... ERROR
test_t13_v10_and_v9_still_replay (test_morning.TripTest.test_t13_v10_and_v9_still_replay) ... ok
test_t1_the_numbers (test_morning.TripTest.test_t1_the_numbers) ... ERROR
test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen (test_morning.TripTest.test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen) ... ERROR
test_t1b_one_person_very_hungry_asks_only_them (test_morning.TripTest.test_t1b_one_person_very_hungry_asks_only_them) ... ERROR
test_t1c_both_at_once (test_morning.TripTest.test_t1c_both_at_once) ... ERROR
test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next (test_morning.TripTest.test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next) ... ERROR
test_t1e_hungry_is_not_enough (test_morning.TripTest.test_t1e_hungry_is_not_enough) ... ERROR
test_t1f_it_fires_once (test_morning.TripTest.test_t1f_it_fires_once) ... ERROR
test_t1g_the_can_neither_brings_it_on_nor_holds_it_back (test_morning.TripTest.test_t1g_the_can_neither_brings_it_on_nor_holds_it_back) ... ERROR
test_t2_nothing_changes_before_the_trigger (test_morning.TripTest.test_t2_nothing_changes_before_the_trigger) ... ERROR
test_t3_the_v10_caches_pair_up_to_the_trigger (test_morning.TripTest.test_t3_the_v10_caches_pair_up_to_the_trigger) ... FAIL
test_t4_the_lines_exactly_and_only_after_the_trigger (test_morning.TripTest.test_t4_the_lines_exactly_and_only_after_the_trigger) ... ERROR
test_t4_the_plan_line_as_each_person_heard_it (test_morning.TripTest.test_t4_the_plan_line_as_each_person_heard_it) ... ERROR
test_t5_the_day2_memories_are_kept_after_the_trigger (test_morning.TripTest.test_t5_the_day2_memories_are_kept_after_the_trigger) ... ERROR
test_t6_when_each_option_is_offered (test_morning.TripTest.test_t6_when_each_option_is_offered) ... ERROR
test_t7_heard_verbs_in_the_pattern_block (test_morning.TripTest.test_t7_heard_verbs_in_the_pattern_block) ... ERROR
test_t7_talk_kinds (test_morning.TripTest.test_t7_talk_kinds) ... FAIL
test_t7_what_each_option_does (test_morning.TripTest.test_t7_what_each_option_does) ... ERROR
test_t8_no_link_in_code (test_morning.TripTest.test_t8_no_link_in_code) ... ERROR
test_t9_the_plan_line (test_morning.TripTest.test_t9_the_plan_line) ... ERROR
test_t9_the_story_ends_with_the_food_and_the_plan (test_morning.TripTest.test_t9_the_story_ends_with_the_food_and_the_plan) ... FAIL
test_prompts_are_short (test_morning.FakeMorningTest.test_prompts_are_short) ... ok
test_an_admission_cannot_be_taken_back (test_morning.FakeMorningTest.test_an_admission_cannot_be_taken_back) ... ok
test_the_fake_client_answers_as_v6s (test_morning.DecisionFormatTest.test_the_fake_client_answers_as_v6s) ... ok
test_the_parser_is_v6s (test_morning.DecisionFormatTest.test_the_parser_is_v6s) ... ok
test_the_schema_is_v6s (test_morning.DecisionFormatTest.test_the_schema_is_v6s) ... ok
test_the_story_and_the_transcript_carry_no_thought (test_morning.DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought) ... FAIL
test_the_system_instruction_is_v6s (test_morning.DecisionFormatTest.test_the_system_instruction_is_v6s) ... ok
The v6 answers carry each morning, unchanged, up to the first prompt of someone who has ... ok
Ran 32 tests in 2.513s
FAILED (failures=4, errors=20)
exit=1
$ git stash pop -q
```

Why each one failed (the last line of each traceback):

```
ERROR: test_t10_recording (test_morning.TripTest.test_t10_recording)
    KeyError: 'trip_minute'
ERROR: test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger (test_morning.TripTest.test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger)
    AttributeError: <module 'world' from 'C:\\Users\\Akrem\\Desktop\\Projects\\Fallow\\Prototypes\\llm-morning\\world.py'> does not have the attribute 'TRIP_ON'
ERROR: test_t12_the_block_sits_outside_the_budget (test_morning.TripTest.test_t12_the_block_sits_outside_the_budget)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1_the_numbers (test_morning.TripTest.test_t1_the_numbers)
    AttributeError: module 'world' has no attribute 'TRIP_HUNGER'
ERROR: test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen (test_morning.TripTest.test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1b_one_person_very_hungry_asks_only_them (test_morning.TripTest.test_t1b_one_person_very_hungry_asks_only_them)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1c_both_at_once (test_morning.TripTest.test_t1c_both_at_once)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next (test_morning.TripTest.test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1e_hungry_is_not_enough (test_morning.TripTest.test_t1e_hungry_is_not_enough)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1f_it_fires_once (test_morning.TripTest.test_t1f_it_fires_once)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t1g_the_can_neither_brings_it_on_nor_holds_it_back (test_morning.TripTest.test_t1g_the_can_neither_brings_it_on_nor_holds_it_back)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t2_nothing_changes_before_the_trigger (test_morning.TripTest.test_t2_nothing_changes_before_the_trigger)
    AttributeError: <module 'world' from 'C:\\Users\\Akrem\\Desktop\\Projects\\Fallow\\Prototypes\\llm-morning\\world.py'> does not have the attribute 'TRIP_ON'
ERROR: test_t4_the_lines_exactly_and_only_after_the_trigger (test_morning.TripTest.test_t4_the_lines_exactly_and_only_after_the_trigger)
    AttributeError: <module 'world' from 'C:\\Users\\Akrem\\Desktop\\Projects\\Fallow\\Prototypes\\llm-morning\\world.py'> does not have the attribute 'TRIP_ON'
ERROR: test_t4_the_plan_line_as_each_person_heard_it (test_morning.TripTest.test_t4_the_plan_line_as_each_person_heard_it)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t5_the_day2_memories_are_kept_after_the_trigger (test_morning.TripTest.test_t5_the_day2_memories_are_kept_after_the_trigger)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t6_when_each_option_is_offered (test_morning.TripTest.test_t6_when_each_option_is_offered)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t7_heard_verbs_in_the_pattern_block (test_morning.TripTest.test_t7_heard_verbs_in_the_pattern_block)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t7_what_each_option_does (test_morning.TripTest.test_t7_what_each_option_does)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t8_no_link_in_code (test_morning.TripTest.test_t8_no_link_in_code)
    AttributeError: 'Morning' object has no attribute 'trip'
ERROR: test_t9_the_plan_line (test_morning.TripTest.test_t9_the_plan_line)
    AttributeError: 'Morning' object has no attribute 'plan_text'. Did you mean: 'line_text'?
FAIL: test_t3_the_v10_caches_pair_up_to_the_trigger (test_morning.TripTest.test_t3_the_v10_caches_pair_up_to_the_trigger)
    AssertionError: CacheMiss not raised : seed 1
FAIL: test_t7_talk_kinds (test_morning.TripTest.test_t7_talk_kinds)
    AssertionError: False is not true
FAIL: test_t9_the_story_ends_with_the_food_and_the_plan (test_morning.TripTest.test_t9_the_story_ends_with_the_food_and_the_plan)
    AssertionError: '\n- The food: never came up.\n- The plan for tonight: no plan.\n' not found in "# The morning as a story: daniel_ate_it, rules and a language model, seed 1\n\nGenerated by `python mor
FAIL: test_the_story_and_the_transcript_carry_no_thought (test_morning.DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought)
    AssertionError: Items in the second set but not the first:
```

- The two changed size bounds pass before the change. They are looser checks on prompts that
  had no trip block yet.
- T13 passes before the change. It checks the v10 freeze, which was committed before any
  implementation.

## 4. Tests after the change

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning
test_the_fake_client_answers_as_v6s (test_morning.DecisionFormatTest.test_the_fake_client_answers_as_v6s) ... ok
test_the_parser_is_v6s (test_morning.DecisionFormatTest.test_the_parser_is_v6s) ... ok
test_the_schema_is_v6s (test_morning.DecisionFormatTest.test_the_schema_is_v6s) ... ok
test_the_story_and_the_transcript_carry_no_thought (test_morning.DecisionFormatTest.test_the_story_and_the_transcript_carry_no_thought) ... ok
test_the_system_instruction_is_v6s (test_morning.DecisionFormatTest.test_the_system_instruction_is_v6s) ... ok
The v6 answers carry each morning, unchanged, up to the first prompt of someone who has ... ok
test_a_morning_completes_and_writes_a_story (test_morning.FakeMorningTest.test_a_morning_completes_and_writes_a_story) ... ok
test_an_admission_cannot_be_taken_back (test_morning.FakeMorningTest.test_an_admission_cannot_be_taken_back) ... ok
test_at_most_one_call_per_person_per_turn (test_morning.FakeMorningTest.test_at_most_one_call_per_person_per_turn) ... ok
test_every_kind_of_broken_answer_falls_back_to_the_rules (test_morning.FakeMorningTest.test_every_kind_of_broken_answer_falls_back_to_the_rules) ... ok
test_nothing_from_target_morning_reaches_a_prompt (test_morning.FakeMorningTest.test_nothing_from_target_morning_reaches_a_prompt) ... ok
test_only_daniel_knows_and_only_daniel_may_confess (test_morning.FakeMorningTest.test_only_daniel_knows_and_only_daniel_may_confess) ... ok
test_prompts_are_short (test_morning.FakeMorningTest.test_prompts_are_short) ... ok
test_replay_is_byte_for_byte_with_no_client_reached (test_morning.FakeMorningTest.test_replay_is_byte_for_byte_with_no_client_reached) ... ok
test_replay_without_a_cache_stops_cleanly (test_morning.FakeMorningTest.test_replay_without_a_cache_stops_cleanly) ... ok
test_seeds_do_not_share_answers (test_morning.FakeMorningTest.test_seeds_do_not_share_answers) ... ok
test_the_call_cap_counts_answers_from_an_earlier_run (test_morning.FakeMorningTest.test_the_call_cap_counts_answers_from_an_earlier_run) ... ok
test_the_call_cap_stops_the_morning_cleanly (test_morning.FakeMorningTest.test_the_call_cap_stops_the_morning_cleanly) ... ok
test_calls_are_spaced (test_morning.GeminiClientTest.test_calls_are_spaced) ... ok
test_daily_quota_stops_keeps_the_cache_and_resumes (test_morning.GeminiClientTest.test_daily_quota_stops_keeps_the_cache_and_resumes) ... ok
test_missing_key_stops_with_a_clear_message (test_morning.GeminiClientTest.test_missing_key_stops_with_a_clear_message) ... ok
test_per_minute_429_backs_off_and_retries (test_morning.GeminiClientTest.test_per_minute_429_backs_off_and_retries) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
test_repeated_429_gives_up_cleanly (test_morning.GeminiClientTest.test_repeated_429_gives_up_cleanly) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
test_the_key_is_never_printed_or_saved (test_morning.GeminiClientTest.test_the_key_is_never_printed_or_saved) ... ok
test_t10_off_no_lull_is_recorded (test_morning.LullTest.test_t10_off_no_lull_is_recorded) ... ok
test_t11_v8_still_replays (test_morning.LullTest.test_t11_v8_still_replays) ... ok
test_t1_the_numbers (test_morning.LullTest.test_t1_the_numbers) ... ok
test_t1a_off_a_room_still_for_9_minutes_gives_no_lull (test_morning.LullTest.test_t1a_off_a_room_still_for_9_minutes_gives_no_lull) ... ok
test_t1b_off_never_asked_in_a_room_still_all_morning_gives_no_lull (test_morning.LullTest.test_t1b_off_never_asked_in_a_room_still_all_morning_gives_no_lull) ... ok
test_t1c_a_social_trigger_comes_first (test_morning.LullTest.test_t1c_a_social_trigger_comes_first) ... ok
test_t1d_an_inner_moment_comes_first (test_morning.LullTest.test_t1d_an_inner_moment_comes_first) ... ok
Leo goes to the back room at minute 0 and then stays silent: with lulls off, nothing ... ok
test_t1f_carrying_on_searching_stirs_the_room (test_morning.LullTest.test_t1f_carrying_on_searching_stirs_the_room) ... ok
test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not (test_morning.LullTest.test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not) ... ok
test_t1i_a_fallback_counts_as_asked (test_morning.LullTest.test_t1i_a_fallback_counts_as_asked) ... ok
test_t2_a_still_room_is_never_talking (test_morning.LullTest.test_t2_a_still_room_is_never_talking) ... ok
test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place (test_morning.LullTest.test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place) ... ok
test_t4_nothing_else_in_the_prompt_changes (test_morning.LullTest.test_t4_nothing_else_in_the_prompt_changes) ... ok
test_t5_nothing_changes_before_the_first_lull (test_morning.LullTest.test_t5_nothing_changes_before_the_first_lull) ... ok
With lulls off, a whole morning on the v6 answers (a silent answer wherever a prompt is ... ok
test_t8_nobody_is_alone_more_than_3_turns_without_being_asked (test_morning.LullTest.test_t8_nobody_is_alone_more_than_3_turns_without_being_asked) ... ok
test_others_words_still_reach_the_prompt (test_morning.OwnWordsTest.test_others_words_still_reach_the_prompt) ... ok
test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words (test_morning.OwnWordsTest.test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words) ... ok
test_own_words_never_appear_in_their_later_prompts (test_morning.OwnWordsTest.test_own_words_never_appear_in_their_later_prompts) ... ok
Against the frozen v9 code, with the same fake model: the same prompts up to the first ... ok
test_a_false_accusation_raises_a_grudge_toward_the_accuser (test_morning.PressureTest.test_a_false_accusation_raises_a_grudge_toward_the_accuser) ... ok
test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed (test_morning.PressureTest.test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed) ... ok
test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes (test_morning.PressureTest.test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes) ... ok
test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster (test_morning.PressureTest.test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster) ... ok
test_confessing_after_denying_it_and_after_accusing (test_morning.PressureTest.test_confessing_after_denying_it_and_after_accusing) ... ok
test_daniel_accusing_someone_counts_once (test_morning.PressureTest.test_daniel_accusing_someone_counts_once) ... ok
test_daniels_guilt_rises_by_the_rules (test_morning.PressureTest.test_daniels_guilt_rises_by_the_rules) ... ok
test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not (test_morning.PressureTest.test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not) ... ok
test_inner_moments_come_at_most_once_every_9_minutes (test_morning.PressureTest.test_inner_moments_come_at_most_once_every_9_minutes) ... ok
test_naming_yourself_counts_as_nobody (test_morning.PressureTest.test_naming_yourself_counts_as_nobody) ... ok
test_no_prompt_holds_the_old_verdicts (test_morning.PressureTest.test_no_prompt_holds_the_old_verdicts) ... ok
test_reassure_is_not_offered_toward_a_grudge_of_3 (test_morning.PressureTest.test_reassure_is_not_offered_toward_a_grudge_of_3) ... ok
test_take_aside_accepted (test_morning.PressureTest.test_take_aside_accepted) ... ok
test_take_aside_needs_someone_yet_to_act_and_an_empty_room (test_morning.PressureTest.test_take_aside_needs_someone_yet_to_act_and_an_empty_room) ... ok
test_take_aside_refused (test_morning.PressureTest.test_take_aside_refused) ... ok
test_after_hearing_a_confession_a_guess_does_not_replace_it (test_morning.PromptTruthTest.test_after_hearing_a_confession_a_guess_does_not_replace_it) ... ok
test_hearing_a_confession_is_what_they_know_about_the_can (test_morning.PromptTruthTest.test_hearing_a_confession_is_what_they_know_about_the_can) ... ok
test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled (test_morning.PromptTruthTest.test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled) ... ok
test_the_culprit_who_names_someone_else_is_still_told_they_ate_it (test_morning.PromptTruthTest.test_the_culprit_who_names_someone_else_is_still_told_they_ate_it) ... ok
test_the_opening_says_what_was_seen_in_every_scenario (test_morning.PromptTruthTest.test_the_opening_says_what_was_seen_in_every_scenario) ... ok
test_a_second_model_from_the_config (test_morning.ScenarioTest.test_a_second_model_from_the_config) ... ok
test_each_scenario_runs_with_the_fake_model (test_morning.ScenarioTest.test_each_scenario_runs_with_the_fake_model) ... ok
test_in_miscount_every_accusation_is_false (test_morning.ScenarioTest.test_in_miscount_every_accusation_is_false) ... ok
test_mara_as_the_culprit_carries_the_guilt (test_morning.ScenarioTest.test_mara_as_the_culprit_carries_the_guilt) ... ok
test_the_culprit_comes_from_the_scenario (test_morning.ScenarioTest.test_the_culprit_comes_from_the_scenario) ... ok
test_the_story_speaks_of_the_culprit (test_morning.ScenarioTest.test_the_story_speaks_of_the_culprit) ... ok
test_a_conversation_ends_after_two_full_turns_with_nothing_new (test_morning.SequentialTalkTest.test_a_conversation_ends_after_two_full_turns_with_nothing_new) ... ok
test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again (test_morning.SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again) ... ok
test_an_inner_moment_can_start_the_talk_again (test_morning.SequentialTalkTest.test_an_inner_moment_can_start_the_talk_again) ... ok
test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn (test_morning.SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn) ... ok
test_metrics_work_out_the_same_conversations_as_the_morning (test_morning.SequentialTalkTest.test_metrics_work_out_the_same_conversations_as_the_morning) ... ok
test_no_speech_act_runs_past_three_turns_in_any_fake_morning (test_morning.SequentialTalkTest.test_no_speech_act_runs_past_three_turns_in_any_fake_morning) ... ok
test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to (test_morning.SequentialTalkTest.test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to) ... ok
test_the_one_just_accused_acts_next (test_morning.SequentialTalkTest.test_the_one_just_accused_acts_next) ... ok
test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house (test_morning.SequentialTalkTest.test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house) ... ok
test_ties_are_broken_by_the_seed (test_morning.SequentialTalkTest.test_ties_are_broken_by_the_seed) ... ok
test_t10_recording (test_morning.TripTest.test_t10_recording) ... ok
test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger (test_morning.TripTest.test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger) ... ok
test_t12_the_block_sits_outside_the_budget (test_morning.TripTest.test_t12_the_block_sits_outside_the_budget) ... ok
test_t13_v10_and_v9_still_replay (test_morning.TripTest.test_t13_v10_and_v9_still_replay) ... ok
test_t1_the_numbers (test_morning.TripTest.test_t1_the_numbers) ... ok
test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen (test_morning.TripTest.test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen) ... ok
test_t1b_one_person_very_hungry_asks_only_them (test_morning.TripTest.test_t1b_one_person_very_hungry_asks_only_them) ... ok
test_t1c_both_at_once (test_morning.TripTest.test_t1c_both_at_once) ... ok
test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next (test_morning.TripTest.test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next) ... ok
test_t1e_hungry_is_not_enough (test_morning.TripTest.test_t1e_hungry_is_not_enough) ... ok
test_t1f_it_fires_once (test_morning.TripTest.test_t1f_it_fires_once) ... ok
test_t1g_the_can_neither_brings_it_on_nor_holds_it_back (test_morning.TripTest.test_t1g_the_can_neither_brings_it_on_nor_holds_it_back) ... ok
test_t2_nothing_changes_before_the_trigger (test_morning.TripTest.test_t2_nothing_changes_before_the_trigger) ... ok
test_t3_the_v10_caches_pair_up_to_the_trigger (test_morning.TripTest.test_t3_the_v10_caches_pair_up_to_the_trigger) ... ok
test_t4_the_lines_exactly_and_only_after_the_trigger (test_morning.TripTest.test_t4_the_lines_exactly_and_only_after_the_trigger) ... ok
test_t4_the_plan_line_as_each_person_heard_it (test_morning.TripTest.test_t4_the_plan_line_as_each_person_heard_it) ... ok
test_t5_the_day2_memories_are_kept_after_the_trigger (test_morning.TripTest.test_t5_the_day2_memories_are_kept_after_the_trigger) ... ok
test_t6_when_each_option_is_offered (test_morning.TripTest.test_t6_when_each_option_is_offered) ... ok
test_t7_heard_verbs_in_the_pattern_block (test_morning.TripTest.test_t7_heard_verbs_in_the_pattern_block) ... ok
test_t7_talk_kinds (test_morning.TripTest.test_t7_talk_kinds) ... ok
test_t7_what_each_option_does (test_morning.TripTest.test_t7_what_each_option_does) ... ok
test_t8_no_link_in_code (test_morning.TripTest.test_t8_no_link_in_code) ... ok
test_t9_the_plan_line (test_morning.TripTest.test_t9_the_plan_line) ... ok
test_t9_the_story_ends_with_the_food_and_the_plan (test_morning.TripTest.test_t9_the_story_ends_with_the_food_and_the_plan) ... ok
test_at_minute_00_only_leos_prompt_differs_by_his_can_line (test_morning.WitnessScenarioTest.test_at_minute_00_only_leos_prompt_differs_by_his_can_line) ... ok
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... ok
Paired with the v6 baseline answers, as a witness run would be (design §4, R3), Leo's ... ok
test_no_backstory_differs (test_morning.WitnessScenarioTest.test_no_backstory_differs) ... ok
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... ok
test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning (test_morning.WitnessScenarioTest.test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning) ... ok
test_the_other_scenarios_do_not_have_the_sentence (test_morning.WitnessScenarioTest.test_the_other_scenarios_do_not_have_the_sentence) ... ok
test_the_sentence_names_nobody_leo_heard (test_morning.WitnessScenarioTest.test_the_sentence_names_nobody_leo_heard) ... ok
test_the_witness_morning_runs_and_its_story_shows_who_heard (test_morning.WitnessScenarioTest.test_the_witness_morning_runs_and_its_story_shows_who_heard) ... ok
Ran 114 tests in 49.904s
OK
exit=0
```

**The first full run after the change** had one failure,
`OwnWordsTest.test_prompts_before_someone_has_spoken_are_unchanged`, seed 5:

```
AssertionError: Lists differ: ["The house: The family has shut itself in[646 chars]ce."] != []
```

The reason, checked before the test was changed:

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -   # first ask of someone who had spoken, and the trip, in fake seeds 1-5
seed 1: first ask of someone who had spoken at min 3; trip started at min 30 (['Elena is very hungry'])
seed 2: first ask of someone who had spoken at min 15; trip started at min 30 (['Elena is very hungry'])
seed 3: first ask of someone who had spoken at min 3; trip started at min 9 (['the shelf is empty'])
seed 4: first ask of someone who had spoken at min 3; trip started at min 30 (['Elena is very hungry'])
seed 5: first ask of someone who had spoken at min 3; trip started at min 3 (['the shelf is empty'])
```

**Fake mornings, for scale** (not a test). The largest estimated prompt is 1,671–1,699, under
the design's 1,774 at most:

```
fake seed 1: trip 30 ['Elena is very hungry']; trip acts 8; max estimated prompt tokens 1671; plan: nobody has offered to go; Mara said someone should go; Leo wants Elena to go; Elena is against anyone going
fake seed 2: trip 30 ['Elena is very hungry']; trip acts 16; max estimated prompt tokens 1699; plan: Mara will go; Leo is against anyone going; Daniel wants Elena to go; Elena is against anyone going
fake seed 3: trip 9 ['the shelf is empty']; trip acts 7; max estimated prompt tokens 1673; plan: nobody has offered to go; Daniel said someone should go; Mara said someone should go; Elena is against Daniel going
fake seed 4: trip 30 ['Elena is very hungry']; trip acts 6; max estimated prompt tokens 1698; plan: Elena will go; Daniel wants Elena to go; Leo is against Elena going; Mara said someone should go
fake seed 5: trip 3 ['the shelf is empty']; trip acts 6; max estimated prompt tokens 1682; plan: Elena will go; Mara said someone should go; Daniel wants Elena to go
```

## 5. Replays and pairing

**The frozen copies:**

```
$ python v10/check.py
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

`v10/` is a byte-for-byte copy of the code at `3a14359`, the commit before this work:

```
$ for f in data gemini metrics metrics3 metrics4 metrics5 morning story talk world; do git show 3a14359:Prototypes/llm-morning/$f.py | diff -q - v10/$f.py ...; done
v10/data.py: identical to data.py at 3a14359
v10/gemini.py: identical to gemini.py at 3a14359
v10/metrics.py: identical to metrics.py at 3a14359
v10/metrics3.py: identical to metrics3.py at 3a14359
v10/metrics4.py: identical to metrics4.py at 3a14359
v10/metrics5.py: identical to metrics5.py at 3a14359
v10/morning.py: identical to morning.py at 3a14359
v10/story.py: identical to story.py at 3a14359
v10/talk.py: identical to talk.py at 3a14359
v10/world.py: identical to world.py at 3a14359
```

**The first post-trigger prompt of each seed** (`$S/first_post.py`). The v11 code runs on
copies of the v10 caches in replay mode, with no client. Its first prompt after the trigger is
diffed against the v10 prompt of the same person at the same minute. The house line is
shortened with "…" in the print; the only change in it is "this morning".

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/first_post.py
seed 1: trip {'minute': 24, 'why': ['the shelf is empty'], 'asked': ['daniel', 'elena', 'leo', 'mara']}; served from cache 22, API requests 0; first prompt after it: Leo at minute 24
  estimated tokens: v10 1382, v11 1629
  --- v10
  +++ v11
  @@ -7,0 +8,2 @@
  +About food: there is no food in the house for tomorrow.
  +About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.
  @@ -9 +11 @@
  -The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is k …  the street and the neighbour's house. Do not mention any other object or place.
  +The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is k …  the street and the neighbour's house. Do not mention any other object or place.
  @@ -10,0 +13,3 @@
  +- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
  +- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you did it)
  +- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
  @@ -49,0 +55,5 @@
  +- propose_trip: (speech) say someone should go to the neighbour's house tonight
  +- volunteer: (speech) offer to go there tonight yourself
  +- back_daniel: (speech) say Daniel should be the one to go
  +- back_elena: (speech) say Elena should be the one to go
  +- back_mara: (speech) say Mara should be the one to go
seed 2: trip {'minute': 30, 'why': ['Elena is very hungry'], 'asked': ['elena']}; served from cache 20, API requests 0; first prompt after it: Elena at minute 30
  estimated tokens: v10 1372, v11 1618
  --- v10
  +++ v11
  @@ -8,0 +9,2 @@
  +About food: there is no food in the house for tomorrow.
  +About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.
  @@ -10 +12 @@
  -The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is k …  the street and the neighbour's house. Do not mention any other object or place.
  +The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is k …  the street and the neighbour's house. Do not mention any other object or place.
  @@ -11,0 +14,3 @@
  +- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
  +- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)
  +- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
  @@ -49,0 +55,5 @@
  +- propose_trip: (speech) say someone should go to the neighbour's house tonight
  +- volunteer: (speech) offer to go there tonight yourself
  +- back_daniel: (speech) say Daniel should be the one to go
  +- back_leo: (speech) say Leo should be the one to go
  +- back_mara: (speech) say Mara should be the one to go
seed 3: trip {'minute': 30, 'why': ['Elena is very hungry'], 'asked': ['elena']}; served from cache 23, API requests 0; first prompt after it: Elena at minute 30
  estimated tokens: v10 1364, v11 1610
  --- v10
  +++ v11
  @@ -8,0 +9,2 @@
  +About food: there is no food in the house for tomorrow.
  +About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.
  @@ -10 +12 @@
  -The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is k …  the street and the neighbour's house. Do not mention any other object or place.
  +The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is k …  the street and the neighbour's house. Do not mention any other object or place.
  @@ -11,0 +14,3 @@
  +- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
  +- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)
  +- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
  @@ -48,0 +54,5 @@
  +- propose_trip: (speech) say someone should go to the neighbour's house tonight
  +- volunteer: (speech) offer to go there tonight yourself
  +- back_daniel: (speech) say Daniel should be the one to go
  +- back_leo: (speech) say Leo should be the one to go
  +- back_mara: (speech) say Mara should be the one to go
```

- **Triggers and cache answers:** minute 24 (shelf, all four asked), 30 (Elena) and 30 (Elena).
  The cache served 22, 20 and 23 answers with 0 API requests. These are the figures the design
  gives (§1, §7, §9 R5).
- **What changed:** only the block's lines. No morning line was dropped or added in any of the
  three prompts, which is the §2.5 proposal working on real prompts.
- **Size:** 1,629, 1,618 and 1,610 estimated tokens. trip_design.md §2.4 predicted 1,618 for
  seed 2.

## 6. git status

```
$ git status --short
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
```

## 7. The diff

### 7.1 The freeze (`9e3009e`)

`v10/*.py` are the copies verified in §5. Here is everything else in that commit:

```diff
diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index 09914c7..fecac6e 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -21,3 +21,5 @@ runs/v9/fake/
 cache/v9/fake-*
 runs/v10/fake/
 cache/v10/fake-*
+runs/v11/fake/
+cache/v11/fake-*
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 7203363..ccdc03f 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -8,9 +8,9 @@
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v10; v4 replays
-                      the fourth version's runs; v5/check.py to v9/check.py replay the
-                      fifth's to ninth's)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v11; v4 replays
+                      the fourth version's runs; v5/check.py to v10/check.py replay the
+                      fifth's to tenth's)
 
 The model names and call limits are in config.json. The key is read from GEMINI_API_KEY.
 
@@ -33,13 +33,13 @@ HERE = os.path.dirname(os.path.abspath(__file__))
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v10"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v11"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v9/ can still replay.
+    # cache/vN after), which v1/ to v10/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -137,7 +137,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v10")
+    ap.add_argument("--out", default="v11")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/v10/check.py b/Prototypes/llm-morning/v10/check.py
new file mode 100644
index 0000000..0bd263e
--- /dev/null
+++ b/Prototypes/llm-morning/v10/check.py
@@ -0,0 +1,54 @@
+"""Replays the three tenth-version mornings from their cache and checks their stories.
+
+    python v10/check.py
+
+v10/ is a frozen copy of the code that made the runs reports/gist_words_v10.md describes
+(daniel_ate_it, a person's own spoken lines reaching them without the words). Replaying makes
+no API calls. Each replayed story must come out byte for byte as runs/v10/<name>.md, and its
+transcript as the one saved beside it.
+"""
+import json
+import os
+import sys
+
+HERE = os.path.dirname(os.path.abspath(__file__))
+ROOT = os.path.dirname(HERE)
+sys.path.insert(0, HERE)
+
+from gemini import Cache, Oracle             # noqa: E402  (v10's own modules)
+from story import render                     # noqa: E402
+from world import Morning                    # noqa: E402
+
+# (scenario, model key, model name, seeds), as the runs in runs/v10 were made.
+RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3))]
+
+
+def main():
+    ok = True
+    for scenario, key, model, seeds in RUNS:
+        for seed in seeds:
+            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
+            cache = Cache(os.path.join(ROOT, "cache", "v10", f"{model}-{name}.json"))
+            oracle = Oracle(cache, model, seed, client=None, replay=True)
+            morning = Morning(oracle, seed, scenario)
+            for t in range(morning.turns):
+                morning.turn(t)
+            morning.finish()
+            command = ("python morning.py"
+                       + (f" --scenario {scenario}" if scenario != "daniel_ate_it" else "")
+                       + (f" --model {key}" if key else "") + f" --seed {seed}")
+            text = render(morning, seed, model, command)
+            base = os.path.join(ROOT, "runs", "v10", name)
+            with open(base + ".md", "rb") as f:
+                same_story = f.read() == text.encode("utf-8")
+            with open(base + ".transcript.json", encoding="utf-8") as f:
+                same_transcript = json.load(f) == json.loads(json.dumps(morning.transcript))
+            ok &= same_story and same_transcript
+            print(f"{name}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
+                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
+                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
+    return 0 if ok else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main())
```

### 7.2 The implementation (`fc572d7`)

```diff
diff --git a/Prototypes/llm-morning/data.py b/Prototypes/llm-morning/data.py
index 22effa8..4d77657 100644
--- a/Prototypes/llm-morning/data.py
+++ b/Prototypes/llm-morning/data.py
@@ -88,6 +88,17 @@ HOUSE_THINGS = (
     "between the rooms; the front door and the front windows, boarded up. Outside, and not "
     "to be gone to: the street and the neighbour's house. Do not mention any other object "
     "or place.")
+# After the trip concern starts (reports/trip_design.md, §2.2): the trip the options speak of is
+# tonight, and nobody goes out this morning.
+HOUSE_THINGS_AFTER_TRIP = HOUSE_THINGS.replace("Outside, and not to be gone to:",
+                                               "Outside, and not to be gone to this morning:")
+assert HOUSE_THINGS_AFTER_TRIP != HOUSE_THINGS
+
+# What everyone learns when the trip concern starts (reports/trip_design.md, §2.1): conclusions
+# the code draws, told after their "About the can:" line.
+ABOUT_FOOD = "About food: there is no food in the house for tomorrow."
+ABOUT_NEIGHBOUR = ("About the neighbour's house: its people left in the first days and nobody has been "
+                   "inside since, so there may be food there. Outside is dangerous.")
 
 # How each of them speaks to the others.
 ADDRESS = {
@@ -161,6 +172,9 @@ _BACKSTORY = [
     (4, "Elena says she is quite sure nobody in this house would take food from the others.",
      {**EVERYONE_SAW, "elena": "did"}),
 ]
+# Day 2's argument about crossing to the neighbour's house. Once the trip concern has started,
+# trimming a prompt never drops these (reports/trip_design.md, §2.3).
+TRIP_MEMORIES = tuple(e[1] for e in _BACKSTORY[3:6])
 
 
 def backstory(scenario):
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index ccdc03f..5b5a43d 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -97,6 +97,8 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         "inner_moments": sum(1 for d in all_d if d.get("inner")),
         "lull_moments": sum(1 for d in all_d if d.get("lull") is not None),
         "private_talks": sum(1 for d in all_d if d["option"] in ("accept_aside", "refuse_aside")),
+        "trip_minute": morning.trip["minute"] if morning.trip else None,
+        "trip_acts": len(morning.trip_acts),
         "max_prompt_tokens_estimated": morning.max_prompt_tokens,
         "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
         "run_seconds": round(seconds, 1),
@@ -106,6 +108,7 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
     say(f"\nwrote {meta['story']}")
     for k in ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
               "routine_decisions", "lines_spoken", "inner_moments", "lull_moments", "private_talks",
+              "trip_minute", "trip_acts",
               "max_prompt_tokens_estimated",
               "max_prompt_tokens_counted_by_api", "run_seconds",
               "story_sha256"):
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index 3c6f3a2..c79e017 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -63,7 +63,13 @@ def decision_line(d, fold=None):
         return (f"- **{name}.** Rules: nothing social happened to them. **{cap(d['label'])}**. "
                 f"Came of it: {d['came_of_it']}{fact}")
     order = f" ({ORDINAL[d['place']]} to act in the {data.ROOMS[d['room']]}: {d['order_reason']})"
-    if d.get("inner"):
+    if d.get("trip_moment") is not None:
+        because = f"**The food**: {d['trip_why']}"
+        if d.get("inner"):
+            because += "; also an inner moment: " + "; ".join(d["inner"])
+        elif d["triggers"]:
+            because += "; also a social moment: " + "; ".join(d["triggers"])
+    elif d.get("inner"):
         because = "**Inner moment**, nothing social happening: " + "; ".join(d["inner"])
     elif d.get("lull") is not None:
         because = f"**Lull**, nothing said or done in the {data.ROOMS[d['room']]} since minute {d['lull']:02d}"
@@ -190,6 +196,11 @@ def render(morning, seed, model_name, command):
     w(f"- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has "
       f"risen a level since they last decided with the model; the model is asked, at most once "
       f"every {INNER_EVERY} minutes per person. What rose is listed.")
+    w("- **The food** (once per morning): at the start of the first turn when the shelf is empty or "
+      "someone is very hungry, everyone learns that there is no food for tomorrow and that the "
+      "neighbour's house may have some, and may then say whether someone should go there tonight. "
+      "Whoever is in the kitchen at the empty shelf, or whoever became very hungry, is asked the "
+      "model that turn. What brought it on is listed.")
     w(f"- **Lull**: nothing social or inner, but nothing has been said or done in their room for at "
       f"least {LULL_QUIET} minutes (staying put in silence and staying seated do not count), and they "
       f"have not been asked for at least {LULL_EVERY} minutes; the model is asked, and told since when "
@@ -300,6 +311,13 @@ def render(morning, seed, model_name, command):
         w("- Nobody took the can: the count was wrong from the start.")
     talk = [f"{data.ROOMS[r]} {what} at minute {m:02d} ({why})" for m, r, what, why in morning.convos.log]
     w("- Conversations: " + "; ".join(talk) + ".")
+    trip = morning.trip
+    if trip:
+        asked = ", ".join(data.PEOPLE[q]["name"] for q in trip["asked"])
+        w(f"- The food: came up at minute {trip['minute']:02d} ({'; '.join(trip['why'])}); asked then: {asked}.")
+    else:
+        w("- The food: never came up.")
+    w(f"- The plan for tonight: {morning.plan_text()}.")
     w("")
     w("What is inside each of them at minute 90:")
     w("")
diff --git a/Prototypes/llm-morning/talk.py b/Prototypes/llm-morning/talk.py
index e874611..0053aa9 100644
--- a/Prototypes/llm-morning/talk.py
+++ b/Prototypes/llm-morning/talk.py
@@ -5,38 +5,50 @@ metrics.py, which runs the old and new transcripts through the same rules afterw
 Knows nothing about the house beyond room names and option ids.
 """
 
-SPEECH = ("ask", "deny", "accuse", "confess", "reassure", "say")
+SPEECH = ("ask", "deny", "accuse", "confess", "reassure", "say",
+          "propose", "volunteer", "object", "back", "decline")     # the last five: the trip
 
 
 def act_of(option):
     """(kind, target) of an option id. Kinds group options that are the same kind of act:
     reassuring one person or everyone is `reassure`, starting or carrying on a search is
-    `search`. The target is a person for accuse, reassure and sit, a room for go."""
+    `search`. The target is a person for accuse, reassure, sit, back and object, a room for go.
+    The trip's options (reports/trip_design.md, §3.3): proposing it, volunteering, objecting
+    to it or to one person going, backing one person to go, and declining to go."""
     if option == "ask_who":
         return "ask", None
+    if option == "propose_trip":
+        return "propose", None
+    if option == "object_trip":
+        return "object", None
     if option == "say_other":
         return "say", None
     if option == "reassure_all":
         return "reassure", None
     if option == "keep_searching":
         return "search", None
-    for prefix in ("accuse", "reassure", "sit", "go", "aside"):
+    for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object"):
         if option.startswith(prefix + "_"):
             return prefix, option[len(prefix) + 1:]
-    return option, None     # silent, deny, confess, search, eat, share
+    return option, None     # silent, deny, confess, search, eat, share, volunteer, decline
 
 
 def aimed_at(option):
     """The person a line is aimed at, or None for a line to everyone in the room."""
     kind, target = act_of(option)
-    return target if kind in ("accuse", "reassure", "aside") else None
+    return target if kind in ("accuse", "reassure", "aside", "back", "object") else None
+
+
+# What a position on the trip is, for the story (reports/trip_design.md, §3.3).
+TRIP_WHY = {"propose": "a proposal", "volunteer": "an offer to go", "object": "an objection",
+            "back": "backing someone to go", "decline": "a refusal to go"}
 
 
 class Newness:
     """Decides whether a spoken line adds something. New: a question, an accusation, a
-    denial of a new accusation, a confession. Not new: reassurance, a stance the speaker
-    has taken before this morning, and any other remark (the rules cannot read what free
-    words add). New facts and people coming in are handled by the caller."""
+    denial of a new accusation, a confession, a position on the trip the speaker has not
+    taken before. Not new: reassurance, a stance the speaker has taken before this morning,
+    and any other remark (the rules cannot read what free words add). New facts and people coming in are handled by the caller."""
 
     def __init__(self):
         self.stances = {}        # speaker -> stances already taken this morning
@@ -63,6 +75,11 @@ class Newness:
                     else "a denial with no new accusation to answer")
         if kind == "reassure":
             return False, "reassurance"
+        if kind in TRIP_WHY:
+            stance = (kind, target)
+            new = stance not in taken
+            taken.add(stance)
+            return new, TRIP_WHY[kind] if new else TRIP_WHY[kind] + " they had made before"
         return False, "a remark (the rules cannot tell what free words add)"
 
 
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index be27b82..fd7ac49 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -94,6 +94,39 @@ def cached_prompts(dirs):
     return prompts
 
 
+# The trip concern (reports/trip_design.md): its two lines, the day-2 memories it keeps from
+# trimming, and the most its block can add to a prompt (§2.5: 374 estimated tokens at most).
+TRIP_FOOD = "About food: there is no food in the house for tomorrow."
+TRIP_HOUSE = ("About the neighbour's house: its people left in the first days and nobody has been "
+              "inside since, so there may be food there. Outside is dangerous.")
+TRIP_DAY2 = ["Daniel says they should cross to the neighbour's house tonight and see what is left there.",
+             "Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. "
+             "Daniel drops it.",
+             "Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his."]
+TRIP_BLOCK_MAX = 380
+TRIP_IDS = re.compile(r"^(propose_trip|volunteer|object_trip|object_\w+|back_\w+|decline)$")
+TRIP_OPTION_LINE = re.compile(r"^- (propose_trip|volunteer|object_\w+|back_\w+|decline): ")
+
+
+def trip_ids(opts):
+    return [o.id for o in opts if TRIP_IDS.match(o.id)]
+
+
+def without_trip_block(prompt):
+    """A prompt without what the trip concern adds to it after the trigger (§2.5): its lines,
+    its options, the day-2 memories it keeps, and "this morning" in the house line."""
+    if TRIP_FOOD not in prompt:
+        return prompt
+    out = []
+    for line in prompt.split("\n"):
+        if line.startswith(("About food:", "About the neighbour's house:", "About going there tonight:")):
+            continue
+        if TRIP_OPTION_LINE.match(line) or any(line.startswith(f"- Day 2: {s} (") for s in TRIP_DAY2):
+            continue
+        out.append(line.replace("Outside, and not to be gone to this morning:", "Outside, and not to be gone to:"))
+    return "\n".join(out)
+
+
 def assert_no_target_text(test, prompts):
     """No sentence of target-morning.md (nor its merged copy) is in any of the prompts."""
     target = target_text()
@@ -226,8 +259,10 @@ class FakeMorningTest(unittest.TestCase):
         self.assertTrue(prompts)
         for p in prompts:
             # The estimate tracked the API's own count closely in the first runs (1,250 against
-            # 1,252); the real counts of the real runs are reported with them.
-            self.assertLess(estimate_tokens(SYSTEM + p), 1450)
+            # 1,252); the real counts of the real runs are reported with them. The trip block
+            # sits outside the budget (reports/trip_design.md, §2.5).
+            self.assertLess(estimate_tokens(SYSTEM + without_trip_block(p)), 1450)
+            self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX)
 
     def test_nothing_from_target_morning_reaches_a_prompt(self):
         fake_morning(self.dirs)
@@ -274,7 +309,8 @@ class FakeMorningTest(unittest.TestCase):
         for q in (daniel, leo):
             prompt = m.prompt_for(q, 20, m.options_for(q))
             self.assertIn("admitted", prompt)
-            self.assertLess(estimate_tokens(SYSTEM + prompt), 1450)
+            self.assertLess(estimate_tokens(SYSTEM + without_trip_block(prompt)), 1450)
+            self.assertLess(estimate_tokens(SYSTEM + prompt), 1450 + TRIP_BLOCK_MAX)
         self.assertIn("you admitted aloud that you took the can",
                       m.prompt_for(daniel, 20, m.options_for(daniel)))
 
@@ -926,11 +962,13 @@ def frozen(version, module):
 
 
 def without_lull(transcript):
-    """A transcript as JSON would hold it, without the `lull` key that every act has since v9."""
+    """A transcript as JSON would hold it, without the `lull` key that every act has since v9
+    and the `trip_moment` key that every act has since v11."""
     tr = json.loads(json.dumps(transcript))
     for turn in tr["turns"]:
         for a in turn["acts"]:
             a.pop("lull", None)
+            a.pop("trip_moment", None)
     return tr
 
 
@@ -1007,10 +1045,11 @@ class DecisionFormatTest(unittest.TestCase):
         def keys(path):
             tr = json.loads(read(path))
             return {k for turn in tr["turns"] for a in turn["acts"] for k in a}
-        # v9 adds one key to every act, `lull` (reports/lull_design.md, §3). `aside` is an older
-        # key, on acts that take someone aside only (world.py, act()); the v6 story had none.
+        # v9 adds one key to every act, `lull` (reports/lull_design.md, §3), and v11 another,
+        # `trip_moment` (reports/trip_design.md, §4.1). `aside` is an older key, on acts that take
+        # someone aside only (world.py, act()); the v6 story had none.
         self.assertEqual(keys(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")) - {"aside"},
-                         keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")) | {"lull"})
+                         keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")) | {"lull", "trip_moment"})
 
     def test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked(self):
         """The v6 answers carry each morning, unchanged, up to the first prompt of someone who has
@@ -1602,11 +1641,13 @@ class OwnWordsTest(unittest.TestCase):
         """Against the frozen v9 code, with the same fake model: the same prompts up to the first
         prompt of someone who has already spoken, and that one differs only in their own lines,
         which lose their words (and, being shorter, may let the trimming keep an older memory or
-        backstory line, world.py prompt_for)."""
+        backstory line, world.py prompt_for). The trip concern is off on the new side: v9 has
+        none, and in seed 5 it starts at minute 03, the turn compared (reports/trip_impl.md)."""
         old_world = frozen("v9", "world")
         for seed in range(1, 6):
             old, old_rec = self.fake(seed, old_world, "old")
-            new, new_rec = self.fake(seed)
+            with mock.patch.object(world, "TRIP_ON", False):
+                new, new_rec = self.fake(seed)
             decisions = [d for r in old.log for d in r["decisions"] if d["mode"] != "routine"]
             spoke = set()
             for i, d in enumerate(decisions):
@@ -1626,6 +1667,536 @@ class OwnWordsTest(unittest.TestCase):
             self.assertTrue(all(x.startswith(("- min ", "- Day ")) for x in extra), (seed, extra))
 
 
+V10_RUNS = os.path.join(HERE, "runs", "v10")
+V10_CACHE = os.path.join(HERE, "cache", "v10")
+
+
+def silent(*a):
+    return "silent", None
+
+
+def run_check(version):
+    env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
+    env["PYTHONDONTWRITEBYTECODE"] = "1"
+    return subprocess.run([sys.executable, os.path.join(HERE, version, "check.py")], cwd=HERE, env=env,
+                          capture_output=True, text=True, timeout=600)
+
+
+def strip_trip_moment(acts):
+    return [{k: v for k, v in a.items() if k != "trip_moment"} for a in acts]
+
+
+class TripTest(unittest.TestCase):
+    """The second concern: whether someone goes to the neighbour's house tonight
+    (reports/trip_design.md, sections 1 to 4; tests T1 to T13 of section 8)."""
+
+    def setUp(self):
+        self.dirs = Dirs()
+
+    def tearDown(self):
+        self.dirs.cleanup()
+
+    def still(self, policy=silent, seed=1):
+        """A morning after its first turn, everyone silent at minute 00."""
+        m, client = scripted(policy, self.dirs, seed=seed, turns=1)
+        return m, client
+
+    def triggered(self, seed=1):
+        """A morning whose concern started at minute 03, from the empty shelf."""
+        m, client = self.still(seed=seed)
+        m.portions = 0
+        m.turn(1)
+        self.assertIsNotNone(m.trip)
+        return m, client
+
+    def act(self, m, p, option, words, t=2):
+        in_turn(m)
+        opt = next((o for o in m.options_for(p) if o.id == option), None)
+        self.assertIsNotNone(opt, f"{option} not offered to {p.id}: {[o.id for o in m.options_for(p)]}")
+        out = m.apply(p, opt, {"mode": "model", "say": words, "feeling": "tense"}, t, [], new_record())
+        out_of_turn(m)
+        return out
+
+    def fake(self, seed, on=True):
+        rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"trip{seed}-{on}.json")), "fake", seed,
+                              client=FakeClient()))
+        with mock.patch.object(world, "TRIP_ON", on):
+            m = Morning(rec, seed).run()
+        return m, rec
+
+    # T1
+    def test_t1_the_numbers(self):
+        self.assertEqual((world.TRIP_HUNGER, world.TRIP_ON), (2, True))
+        self.assertEqual(data.TRIP_MEMORIES, tuple(TRIP_DAY2))
+
+    def test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen(self):
+        m, _ = self.still()
+        self.assertIsNone(m.trip)
+        m.portions = 0
+        m.turn(1)
+        self.assertEqual(m.trip, {"minute": 3, "why": ["the shelf is empty"], "asked": list(data.ORDER)})
+        moments = {d["person"]: d for d in m.log[1]["decisions"] if d.get("trip_moment") is not None}
+        self.assertEqual(set(moments), set(data.ORDER))
+        for d in moments.values():
+            self.assertEqual((d["trip_moment"], d["mode"]), (3, "model"))
+
+    def test_t1b_one_person_very_hungry_asks_only_them(self):
+        m, _ = self.still()
+        m.people["mara"].hunger = 0.72
+        m.turn(1)
+        self.assertEqual(m.trip, {"minute": 3, "why": ["Mara is very hungry"], "asked": ["mara"]})
+        self.assertEqual([d["person"] for d in m.log[1]["decisions"] if d.get("trip_moment") is not None],
+                         ["mara"])
+
+    def test_t1c_both_at_once(self):
+        m, _ = self.still()
+        m.portions = 0
+        m.people["leo"].room = "back_room"
+        m.people["leo"].hunger = 0.75
+        m.turn(1)
+        self.assertEqual(m.trip, {"minute": 3, "why": ["the shelf is empty", "Leo is very hungry"],
+                                  "asked": ["daniel", "elena", "leo", "mara"]})
+
+    def test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next(self):
+        def policy(who, minute, options, client):
+            return ("eat", None) if minute == 0 and who in ("daniel", "leo") and "eat" in options else ("silent", None)
+        m, _ = scripted(policy, self.dirs, turns=1)
+        self.assertEqual(m.portions, 0)
+        self.assertIsNone(m.trip)
+        m.turn(1)
+        self.assertEqual((m.trip["minute"], m.trip["why"]), (3, ["the shelf is empty"]))
+
+    def test_t1e_hungry_is_not_enough(self):
+        m, _ = scripted(silent, self.dirs, turns=6)               # minutes 00 to 15
+        self.assertEqual(world.hunger_level(m.people["daniel"].hunger), 1)
+        self.assertIsNone(m.trip)
+        self.assertFalse([p for _, _, p in m.oracle.client.prompts if TRIP_FOOD in p])
+
+    def test_t1f_it_fires_once(self):
+        m, _ = self.still()
+        m.people["mara"].hunger = 0.72
+        m.turn(1)
+        before = json.loads(json.dumps(m.trip))
+        m.portions = 0
+        for p in m.people.values():
+            p.hunger = 0.9
+        m.turn(2)
+        m.turn(3)
+        self.assertEqual(m.trip, before)
+        self.assertFalse([d for rec in m.log[2:] for d in rec["decisions"] if d.get("trip_moment") is not None])
+
+    def test_t1g_the_can_neither_brings_it_on_nor_holds_it_back(self):
+        def policy(who, minute, options, client):
+            if minute == 0 and who == "daniel":
+                return "confess", "It was me."
+            for o in options:
+                if o.startswith("accuse_"):
+                    return o, "You did it.", "Daniel", "Daniel"
+            return "silent", None
+        m, _ = scripted(policy, self.dirs, turns=5)
+        self.assertTrue(m.people["daniel"].confessed)
+        self.assertIsNone(m.trip)
+        m.people["leo"].hunger = 0.72
+        m.turn(5)
+        self.assertEqual(m.trip, {"minute": 15, "why": ["Leo is very hungry"], "asked": ["leo"]})
+
+    # T2
+    def test_t2_nothing_changes_before_the_trigger(self):
+        for seed in range(1, 6):
+            off, rec_off = self.fake(seed, on=False)
+            on, rec_on = self.fake(seed)
+            self.assertIsNone(off.trip, seed)
+            self.assertIsNotNone(on.trip, seed)
+            first = next(i for i, p in enumerate(rec_on.prompts) if TRIP_FOOD in p)
+            self.assertEqual(rec_on.prompts[:first], rec_off.prompts[:first], seed)
+            T = on.trip["minute"]
+            before = lambda m: [a for turn in m.transcript["turns"] if turn["minute"] < T for a in turn["acts"]]
+            self.assertEqual(strip_trip_moment(before(on)), strip_trip_moment(before(off)), seed)
+            self.assertTrue(all(a["trip_moment"] is None for a in before(on)), seed)
+
+    # T3
+    def test_t3_the_v10_caches_pair_up_to_the_trigger(self):
+        expected = {1: (24, None, 22), 2: (30, "Elena", 20), 3: (30, "Elena", 23)}
+        for seed, (minute, who, served) in expected.items():
+            name = f"daniel_ate_it-seed{seed}"
+            path = os.path.join(self.dirs.root, f"{name}.json")
+            shutil.copy(os.path.join(V10_CACHE, f"{V6_MODEL}-{name}.json"), path)
+            oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
+            rec = Recorder(oracle)
+            m = Morning(rec, seed)
+            with self.assertRaises(gemini.CacheMiss, msg=f"seed {seed}"):
+                for t in range(m.turns):
+                    m.turn(t)
+            last = rec.prompts[-1]
+            self.assertIn(f"\nNow, minute {minute:02d}, you are in the kitchen.\n", last, seed)
+            self.assertIn(TRIP_FOOD, last, seed)
+            if who:
+                self.assertTrue(last.startswith(f"You are {who},"), seed)
+            self.assertEqual(m.trip["minute"], minute, seed)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+            v10 = json.loads(read(os.path.join(V10_RUNS, name + ".transcript.json")))
+            self.assertEqual(without_lull(m.transcript)["turns"],
+                             without_lull({"turns": [t for t in v10["turns"] if t["minute"] < minute]})["turns"],
+                             seed)
+
+    # T4
+    def test_t4_the_lines_exactly_and_only_after_the_trigger(self):
+        post = 0
+        for seed in (1, 2, 3):
+            m, rec = self.fake(seed)
+            minutes = [rec_["minute"] for rec_ in m.log for d in rec_["decisions"] if d["mode"] != "routine"]
+            self.assertEqual(len(minutes), len(rec.prompts), seed)
+            for minute, prompt in zip(minutes, rec.prompts):
+                if minute < m.trip["minute"]:
+                    for words in ("About food:", "neighbour's house:", "About going there tonight:",
+                                  "to be gone to this morning:"):
+                        self.assertNotIn(words, prompt, (seed, minute))
+                    continue
+                post += 1
+                lines = prompt.split("\n")
+                self.assertEqual(lines.count(TRIP_FOOD), 1)
+                self.assertEqual(lines.count(TRIP_HOUSE), 1)
+                i = lines.index(TRIP_FOOD)
+                self.assertTrue(lines[i - 1].startswith("About the can"), lines[i - 1])
+                self.assertEqual(lines[i + 1], TRIP_HOUSE)
+                self.assertIn("Outside, and not to be gone to this morning: the street and the neighbour's house.",
+                              prompt)
+                self.assertNotIn("Outside, and not to be gone to: ", prompt)
+        self.assertGreater(post, 0)
+
+    def test_t4_the_plan_line_as_each_person_heard_it(self):
+        m, _ = self.triggered()
+        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
+        for p in m.people.values():
+            self.assertNotIn("About going there tonight:", m.prompt_for(p, 2, m.options_for(p)))
+        mara.room = "back_room"
+        self.act(m, dan, "volunteer", "I'll go.", t=2)
+        self.act(m, leo, "object_trip", "Nobody goes.", t=3)
+        self.act(m, ele, "back_leo", "Leo should go.", t=4)
+        self.act(m, dan, "object_leo", "Not Leo.", t=5)
+        self.act(m, leo, "decline", "Not me.", t=6)
+        self.act(m, dan, "propose_trip", "Someone must go.", t=7)
+
+        def line(p):
+            return next((x for x in m.prompt_for(p, 8, m.options_for(p)).split("\n")
+                         if x.startswith("About going there tonight:")), None)
+        self.assertEqual(line(leo), "About going there tonight: Elena said you should go (min 12); "
+                                    "you said you will not go (min 18); Daniel said someone should go (min 21).")
+        self.assertEqual(line(ele), "About going there tonight: you said Leo should go (min 12); "
+                                    "Leo said he will not go (min 18); Daniel said someone should go (min 21).")
+        self.assertIsNone(line(mara))           # in the back room: heard nothing of it
+        self.act(m, ele, "volunteer", "Then I will.", t=8)
+        self.assertEqual(line(dan), "About going there tonight: Leo said he will not go (min 18); "
+                                    "you said someone should go (min 21); Elena offered to go (min 24).")
+        self.act(m, dan, "object_elena", "Not you, Mom.", t=9)
+        self.act(m, leo, "object_trip", "Nobody.", t=10)
+        self.assertEqual(line(ele), "About going there tonight: you offered to go (min 24); "
+                                    "Daniel said you should not go (min 27); Leo said nobody should go (min 30).")
+
+    # T5
+    def test_t5_the_day2_memories_are_kept_after_the_trigger(self):
+        filler = [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
+        fresh, _ = self.still()
+        fresh.people["elena"].memory += filler
+        before = fresh.prompt_for(fresh.people["elena"], 2, fresh.options_for(fresh.people["elena"]))
+        self.assertIn("(earlier things, left out here)", before)
+        days = [x for x in before.split("\n") if x.startswith("- Day ")]
+        self.assertEqual(len(days), 4)
+        self.assertFalse([x for x in days if x.startswith("- Day 2:")])
+        m, _ = self.triggered()
+        m.people["elena"].memory += filler
+        after = m.prompt_for(m.people["elena"], 2, m.options_for(m.people["elena"]))
+        self.assertIn("(earlier things, left out here)", after)
+        days = [x for x in after.split("\n") if x.startswith("- Day ")]
+        self.assertEqual(days[:3], [f"- Day 2: {s} (you saw it)" for s in TRIP_DAY2])
+        self.assertEqual(days[3:], [x for x in before.split("\n") if x.startswith("- Day ")])
+        # Daniel and Leo keep them too, with what they did.
+        dan = m.people["daniel"]
+        dan.memory += filler
+        days = [x for x in m.prompt_for(dan, 2, m.options_for(dan)).split("\n") if x.startswith("- Day 2:")]
+        self.assertEqual(days, [f"- Day 2: {TRIP_DAY2[0]} (you did it)", f"- Day 2: {TRIP_DAY2[1]} (you saw it)",
+                                f"- Day 2: {TRIP_DAY2[2]} (you did it)"])
+
+    # T6
+    def test_t6_when_each_option_is_offered(self):
+        fresh, _ = self.still()
+        for p in fresh.people.values():
+            self.assertEqual(trip_ids(fresh.options_for(p)), [], p.id)
+        m, _ = self.triggered()
+        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
+        ids = [o.id for o in m.options_for(dan)]
+        self.assertEqual(trip_ids(m.options_for(dan)),
+                         ["propose_trip", "volunteer", "back_elena", "back_leo", "back_mara"])
+        start = ids.index("propose_trip")
+        self.assertEqual(ids[start - 1], "reassure_all")
+        self.assertEqual(ids[start + 5], "say_other")
+        # Alone: none.
+        ele.room = "back_room"
+        self.assertEqual(trip_ids(m.options_for(ele)), [])
+        ele.room = "kitchen"
+        self.act(m, dan, "propose_trip", "Someone has to go.")
+        self.assertNotIn("propose_trip", trip_ids(m.options_for(dan)))
+        self.assertIn("object_trip", trip_ids(m.options_for(dan)))        # made a proposal: may now object
+        self.assertEqual(trip_ids(m.options_for(leo)),
+                         ["propose_trip", "volunteer", "object_trip", "back_daniel", "back_elena", "back_mara"])
+        self.act(m, dan, "volunteer", "I'll go.", t=3)
+        self.assertEqual(trip_ids(m.options_for(dan)),
+                         ["object_trip", "back_elena", "back_leo", "back_mara", "decline"])
+        self.assertEqual(trip_ids(m.options_for(leo)),
+                         ["propose_trip", "volunteer", "object_trip", "back_daniel", "back_elena", "back_mara",
+                          "object_daniel"])
+        self.act(m, dan, "decline", "No, not me.", t=4)
+        self.assertEqual(trip_ids(m.options_for(dan)),
+                         ["volunteer", "object_trip", "back_elena", "back_leo", "back_mara"])
+        self.assertNotIn("object_daniel", trip_ids(m.options_for(leo)))
+        self.act(m, mara, "back_daniel", "Daniel should go.", t=5)
+        self.assertIn("object_daniel", trip_ids(m.options_for(leo)))
+        self.assertNotIn("back_daniel", trip_ids(m.options_for(mara)))
+        self.assertIn("back_leo", trip_ids(m.options_for(mara)))
+        self.assertNotIn("decline", trip_ids(m.options_for(dan)))         # already his position
+        self.act(m, leo, "object_daniel", "Not Daniel.", t=6)
+        self.assertNotIn("object_daniel", trip_ids(m.options_for(leo)))
+        self.act(m, ele, "back_mara", "Mara should go.", t=7)
+        self.assertIn("decline", trip_ids(m.options_for(mara)))           # backed in her hearing
+        # No option is ever the person's current position.
+        for p in m.people.values():
+            pos = p.trip_heard.get(p.id)
+            if pos:
+                kind, target = pos[1], pos[2]
+                current = {"propose": "propose_trip", "volunteer": "volunteer", "decline": "decline",
+                           "object": f"object_{target}" if target else "object_trip",
+                           "back": f"back_{target}"}[kind]
+                self.assertNotIn(current, trip_ids(m.options_for(p)), p.id)
+
+    # T7
+    def test_t7_what_each_option_does(self):
+        m, _ = self.triggered()
+        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
+        mara.room = "back_room"
+        state = lambda: json.dumps({p.id: [p.hunger, p.guilt, p.suspicion.state(), p.heard_question,
+                                           p.knows_culprit, p.room, {t: g.strength for t, g in p.grudges.items()}]
+                                    for p in m.people.values()} | {"portions": m.portions})
+        before = state()
+        said = [
+            (dan, "propose_trip", "W1", "Daniel says someone should go to the neighbour's house tonight",
+             "you said someone should go to the neighbour's house tonight.", ("propose", None), True, "a proposal"),
+            (leo, "volunteer", "W2", "Leo offers to go to the neighbour's house tonight",
+             "you offered to go there tonight.", ("volunteer", None), True, "an offer to go"),
+            (ele, "object_trip", "W3", "Elena says nobody should go out tonight",
+             "you said nobody should go out tonight.", ("object", None), True, "an objection"),
+            (ele, "object_leo", "W4", "Elena says {Leo} should not be the one to go",
+             "you said Leo should not be the one to go.", ("object", "leo"), True, "an objection"),
+            (dan, "back_leo", "W5", "Daniel says {Leo} should be the one to go",
+             "you said Leo should be the one to go.", ("back", "leo"), True, "backing someone to go"),
+            (leo, "decline", "W6", "Leo says he will not be the one to go",
+             "you said you will not be the one to go.", ("decline", None), True, "a refusal to go"),
+            (leo, "volunteer", "W7", "Leo offers to go to the neighbour's house tonight",
+             "you offered to go there tonight.", ("volunteer", None), False, "an offer to go they had made before"),
+        ]
+        for t, (p, option, words, gist, own, pos, new, why) in enumerate(said, start=2):
+            minute = t * 3
+            self.act(m, p, option, words, t=t)
+            for q in (dan, ele, leo):
+                if q is p:
+                    continue
+                g = gist.replace("{Leo}", "you" if q is leo else "Leo")
+                self.assertIn((minute, f'{g}: "{words}"'), q.memory, (option, q.id))
+                self.assertEqual(q.trip_heard[p.id][:3], (minute,) + pos, (option, q.id))
+            self.assertIn(f"min {minute:02d}, {own}", p.said_lines)
+            self.assertIn((minute, f"{own[:-1]}. You felt tense."), p.memory)
+            self.assertNotIn(words, "\n".join(x for _, x in p.memory))
+            self.assertEqual(m.trip_acts[-1], (minute, p.id, pos[0], pos[1], words))
+            self.assertEqual(p.trip_heard[p.id][:3], (minute,) + pos)
+            self.assertEqual((m.said[-1]["new"], m.said[-1]["why"]), (new, why), option)
+            self.assertNotIn(p.id, mara.trip_heard)                   # the back room heard no words
+            if pos[1]:
+                self.assertEqual(m.people[pos[1]].addressed["who"], p.id)
+        self.assertEqual(state(), before)
+        self.assertTrue(dan.proposed)
+        self.assertFalse(ele.proposed)
+        # Nobody ever leaves the house.
+        for seed in range(1, 6):
+            mm, _ = self.fake(seed)
+            for turn in mm.transcript["turns"]:
+                for a in turn["acts"]:
+                    self.assertIn(a["moved_to"], [None] + list(data.ROOMS), (seed, a))
+
+    def test_t7_talk_kinds(self):
+        from talk import SPEECH, Newness, act_of, aimed_at
+        self.assertTrue({"propose", "volunteer", "object", "back", "decline"} <= set(SPEECH))
+        self.assertEqual([act_of(x) for x in ("propose_trip", "volunteer", "object_trip", "object_leo",
+                                              "back_mara", "decline")],
+                         [("propose", None), ("volunteer", None), ("object", None), ("object", "leo"),
+                          ("back", "mara"), ("decline", None)])
+        self.assertEqual([aimed_at(x) for x in ("propose_trip", "object_trip", "object_leo", "back_mara", "decline")],
+                         [None, None, "leo", "mara", None])
+        n = Newness()
+        self.assertEqual(n.line("leo", "object_daniel", []), (True, "an objection"))
+        self.assertEqual(n.line("leo", "object_mara", []), (True, "an objection"))
+        self.assertEqual(n.line("leo", "object_daniel", []), (False, "an objection they had made before"))
+        self.assertEqual(n.line("leo", "back_mara", []), (True, "backing someone to go"))
+        self.assertEqual(n.line("leo", "back_mara", []), (False, "backing someone to go they had made before"))
+        self.assertEqual(n.line("mara", "propose_trip", []), (True, "a proposal"))
+        self.assertEqual(n.line("mara", "propose_trip", []), (False, "a proposal they had made before"))
+        self.assertEqual(n.line("mara", "decline", []), (True, "a refusal to go"))
+        self.assertEqual(n.line("mara", "decline", []), (False, "a refusal to go they had made before"))
+        for kind, done in (("propose", "said someone should go to the neighbour's house tonight"),
+                           ("volunteer", "offered to go there tonight"), ("object", "said someone should not go"),
+                           ("back", "said someone should be the one to go"),
+                           ("decline", "said you will not be the one to go")):
+            self.assertEqual(world.KIND_DONE[kind], done)
+
+    def test_t7_heard_verbs_in_the_pattern_block(self):
+        m, _ = self.triggered()
+        dan, leo = m.people["daniel"], m.people["leo"]
+        verbs = [m.heard_verb({"kind": k, "target": tgt}, dan) for k, tgt in
+                 (("propose", None), ("volunteer", None), ("object", None), ("object", "daniel"),
+                  ("back", "daniel"), ("decline", None))]
+        self.assertEqual(verbs, ["said someone should go to the neighbour's house tonight", "offered to go there tonight",
+                                 "said nobody should go", "said you should not be the one to go",
+                                 "said you should be the one to go", "said they will not be the one to go"])
+
+    # T8
+    def test_t8_no_link_in_code(self):
+        m, _ = self.triggered()
+        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
+
+        def can_ids(p):
+            return [o.id for o in m.options_for(p) if not TRIP_IDS.match(o.id)]
+        before = {p.id: can_ids(p) for p in m.people.values()}
+        self.act(m, dan, "volunteer", "I'll go.")
+        self.act(m, leo, "back_daniel", "Daniel goes.", t=3)
+        self.act(m, ele, "object_daniel", "Not Daniel.", t=4)
+        self.act(m, mara, "object_trip", "Nobody goes.", t=5)
+        self.assertEqual({p.id: can_ids(p) for p in m.people.values()}, before)
+        trip_before = {p.id: trip_ids(m.options_for(p)) for p in m.people.values()}
+        dan.confessed = True
+        for p in m.people.values():
+            p.heard_question = True
+            p.knows_culprit, p.confession_heard_at = "daniel", 15
+            p.suspicion.target, p.suspicion.strength = "daniel", 3
+            if p is not dan:
+                p.grudge("daniel").rise(15, "something", "event")
+        self.assertEqual({p.id: trip_ids(m.options_for(p)) for p in m.people.values()}, trip_before)
+        texts = [TRIP_FOOD, TRIP_HOUSE, m.plan_text()] + [world.KIND_DONE[k] for k in
+                                                          ("propose", "volunteer", "object", "back", "decline")]
+        texts += [o.label for p in m.people.values() for o in m.options_for(p) if TRIP_IDS.match(o.id)]
+        texts += [x for p in m.people.values() for x in m.prompt_for(p, 6, m.options_for(p)).split("\n")
+                  if x.startswith("About going there tonight:")]
+        for text in texts:
+            self.assertFalse(re.search(r"\b(can|took|guilt)\b", text), text)
+
+    # T9
+    def test_t9_the_plan_line(self):
+        m, _ = self.still()
+        self.assertEqual(m.plan_text(), "no plan")
+        m.trip = {"minute": 30, "why": ["Elena is very hungry"], "asked": ["elena"]}
+        self.assertEqual(m.plan_text(), "no plan")
+        cases = [
+            ([(33, "daniel", "volunteer", None), (36, "mara", "back", "daniel"), (39, "elena", "object", None)],
+             "Daniel will go; Mara wants Daniel to go; Elena is against anyone going"),
+            ([(33, "leo", "propose", None), (36, "mara", "object", "leo")],
+             "nobody has offered to go; Leo said someone should go; Mara is against Leo going"),
+            ([(33, "daniel", "volunteer", None), (36, "leo", "volunteer", None)],
+             "Daniel and Leo have both offered to go"),
+            ([(33, "daniel", "volunteer", None), (36, "leo", "volunteer", None), (39, "mara", "volunteer", None)],
+             "Daniel, Leo and Mara have all offered to go"),
+            ([(33, "elena", "back", "leo"), (36, "leo", "decline", None)],
+             "nobody has offered to go; Elena wants Leo to go; Leo will not go"),
+            ([(33, "daniel", "volunteer", None), (39, "daniel", "object", None)],
+             "nobody has offered to go; Daniel is against anyone going"),
+        ]
+        for acts, plan in cases:
+            m.trip_acts = [(minute, who, kind, target, "words") for minute, who, kind, target in acts]
+            self.assertEqual(m.plan_text(), plan, acts)
+
+    def test_t9_the_story_ends_with_the_food_and_the_plan(self):
+        m, _ = self.still()
+        m.finish()
+        story = render(m, 1, "fake", "python morning.py --seed 1")
+        self.assertIn("\n- The food: never came up.\n- The plan for tonight: no plan.\n", story)
+        m, _ = self.still()
+        m.people["elena"].hunger = 0.72
+        m.turn(1)
+        self.act(m, m.people["daniel"], "volunteer", "I'll go.")
+        m.finish()
+        story = render(m, 1, "fake", "python morning.py --seed 1")
+        self.assertIn("\n- The food: came up at minute 03 (Elena is very hungry); asked then: Elena.\n"
+                      "- The plan for tonight: Daniel will go.\n", story)
+        m, _ = self.triggered()
+        m.finish()
+        story = render(m, 1, "fake", "python morning.py --seed 1")
+        self.assertIn("\n- The food: came up at minute 03 (the shelf is empty); asked then: Daniel, Elena, Leo, "
+                      "Mara.\n", story)
+
+    # T10
+    def test_t10_recording(self):
+        acts_seen = 0
+        for seed in (1, 2, 3):
+            (meta, code), out = fake_morning(self.dirs, seed=seed)
+            self.assertEqual(code, 0, out)
+            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))
+            story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
+            self.assertEqual(meta["trip_minute"], tr["trip"]["minute"])
+            acts = [a for turn in tr["turns"] for a in turn["acts"]]
+            trips = [a for a in acts if TRIP_IDS.match(a["option"])]
+            self.assertEqual(meta["trip_acts"], len(trips))
+            self.assertEqual(tr["trip"]["acts"], [[a["minute"], a["who"], a["option"], a["words"]] for a in trips])
+            acts_seen += len(trips)
+            moments = [(turn["minute"], a) for turn in tr["turns"] for a in turn["acts"]
+                       if a.get("trip_moment") is not None]
+            self.assertTrue(moments, seed)
+            for minute, a in moments:
+                self.assertEqual((minute, a["trip_moment"]), (tr["trip"]["minute"],) * 2)
+                self.assertIn(a["mode"], ("model", "fallback"))
+                self.assertIn(a["who"], tr["trip"]["asked"])
+            self.assertEqual(story.count("**The food**: "), len(moments), seed)
+            self.assertIn(f"- The plan for tonight: {tr['trip']['plan']}.", story)
+            self.assertIn(f"trip_minute: {meta['trip_minute']}", out)
+            self.assertIn(f"trip_acts: {meta['trip_acts']}", out)
+        self.assertGreater(acts_seen, 0)
+
+    # T11
+    def test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger(self):
+        prompts = []
+        for seed in (1, 2, 3):
+            _, rec = self.fake(seed)
+            prompts += [p for p in rec.prompts if TRIP_FOOD in p]
+        self.assertTrue(prompts)
+        assert_no_target_text(self, prompts)
+
+    # T12
+    def test_t12_the_block_sits_outside_the_budget(self):
+        filler = [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
+        m, _ = self.triggered()
+        self.act(m, m.people["daniel"], "volunteer", "I'll go.")
+        ele = m.people["elena"]
+        ele.memory += filler
+        with_trip = m.prompt_for(ele, 3, m.options_for(ele))
+        trip, m.trip = m.trip, None
+        plain = m.prompt_for(ele, 3, m.options_for(ele))
+        m.trip = trip
+
+        def morning_lines(prompt):
+            lines = prompt.split("\n")
+            return lines[lines.index("What else happened this morning, most recent last:"):
+                         next(i for i, x in enumerate(lines) if x.startswith("Now, minute"))]
+        self.assertIn("- (earlier things, left out here)", morning_lines(plain))
+        self.assertEqual(morning_lines(with_trip), morning_lines(plain))
+        self.assertEqual(without_trip_block(with_trip), plain)
+        self.assertLessEqual(estimate_tokens(SYSTEM + without_trip_block(with_trip)), PROMPT_TOKEN_BUDGET)
+        self.assertGreater(estimate_tokens(SYSTEM + with_trip), PROMPT_TOKEN_BUDGET)
+        self.assertLess(estimate_tokens(SYSTEM + with_trip), 1450 + TRIP_BLOCK_MAX)
+
+    # T13
+    def test_t13_v10_and_v9_still_replay(self):
+        for version in ("v10", "v9"):
+            done = run_check(version)
+            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
+            self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
+            self.assertIn("0 API calls", done.stdout)
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 1bffaeb..866f57b 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -17,13 +17,18 @@ neutral level word; the numbers themselves only decide when an inner moment come
 A lull moment asks the model for someone nothing social or inner has happened to, when the
 room they are in has been still for a while and they have not been asked for a while; their
 prompt says since when nothing has been said or done there (reports/lull_design.md).
+
+The trip concern (reports/trip_design.md): once the shelf is empty or someone first becomes very
+hungry, everyone is told there is no food for tomorrow and that the neighbour's house may have
+some, and each of them may take a position on whether someone goes there tonight. The rules
+record the positions and decide nothing; nobody leaves the house.
 """
 import json
 import random
 import re
 
 import data
-from talk import SPEECH, Conversations, Newness, act_of, aimed_at
+from talk import SPEECH, TRIP_WHY, Conversations, Newness, act_of, aimed_at
 
 NAMES = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
 CHOICES = [NAMES[p] for p in data.ORDER] + ["nobody"]
@@ -59,6 +64,9 @@ FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one
 LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
                              # off since reports/lull_v9.md, 9 in reports/lull_design.md
 LULL_EVERY = 12              # minutes since a person was last asked before a lull
+TRIP_HUNGER = 2              # the hunger level ("very hungry") that starts the trip concern
+TRIP_ON = True               # the trip concern (reports/trip_design.md); off only in tests
+TRIP_KINDS = tuple(TRIP_WHY)  # propose, volunteer, object, back, decline
 
 KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
     "ask": "asked who took the can", "deny": "denied taking it",
@@ -68,6 +76,9 @@ KIND_DONE = {   # what a run of one kind of act looks like, told to the person w
     "sit": "sat with someone", "eat": "eaten", "share": "shared out the food",
     "aside": "taken someone aside", "accept_aside": "gone aside with someone",
     "refuse_aside": "refused to go aside",
+    "propose": "said someone should go to the neighbour's house tonight",
+    "volunteer": "offered to go there tonight", "object": "said someone should not go",
+    "back": "said someone should be the one to go", "decline": "said you will not be the one to go",
 }
 
 HUNGER_WORDS = ["a little hungry", "hungry", "very hungry", "starving"]
@@ -75,8 +86,9 @@ LEVEL_WORDS = {1: "a little", 2: "some", 3: "a lot"}   # the only words a level
 EVENTS_SHOWN = 4             # most recent events shown per grudge and for guilt
 
 
-def estimate_tokens(text):
-    return int(len(text) / 3.6) + 1
+def estimate_tokens(text, less=0):
+    """less: characters of `text` that do not count (the trip block, reports/trip_design.md §2.5)."""
+    return int((len(text) - less) / 3.6) + 1
 
 
 def strength(feeling):
@@ -190,6 +202,13 @@ def grudge_facts(name, events, limit=None):
     return facts
 
 
+def trip_option(kind, target):
+    """The option id of a position on the trip."""
+    if kind in ("propose", "volunteer", "decline"):
+        return {"propose": "propose_trip"}.get(kind, kind)
+    return f"{kind}_{target}" if target else "object_trip"
+
+
 class Option:
     def __init__(self, id, label, speech=False, **act):
         self.id, self.label, self.speech, self.act = id, label, speech, act
@@ -233,6 +252,15 @@ class Person:
         self.seen = None            # the levels they were shown when they last decided
         self.last_inner = None      # minute of their last inner moment
         self.last_asked = None      # minute of their last model decision of any kind
+        # The trip: each speaker's latest position they heard (their own included), as
+        # (minute, kind, target, seq); whether they have proposed it; whether they have heard or
+        # made a proposal, an offer or a backing; and the day-2 memories never trimmed once it
+        # has started.
+        self.trip_heard = {}
+        self.proposed = False
+        self.trip_raised = False
+        self.trip_memories = {x for x in self.backstory
+                              if any(x.startswith(f"Day 2: {m} (") for m in data.TRIP_MEMORIES)}
 
     def grudge(self, against):
         return self.grudges.setdefault(against, Grudge())
@@ -272,6 +300,9 @@ class Morning:
         # room -> the minute something other than staying put in silence, or staying seated,
         # was last done in it (the count at minute 00 was done in the kitchen)
         self.last_stir = {"kitchen": 0}
+        self.trip = None            # the trip concern once started: {"minute", "why", "asked"}
+        self.trip_acts = []         # (minute, who, kind, target, words), every position taken
+        self.trip_now = set()       # during the turn it starts: who is asked because of it
         for p in self.people.values():
             how = "did it" if p.id == "elena" else "saw it"
             p.sure.append(f"min 00: {data.OPENING} (you {how})")
@@ -351,6 +382,7 @@ class Morning:
                                    kind="reassure", target=q.id))
             if len(others) > 1:
                 opts.append(Option("reassure_all", "reassure everyone here", True, kind="reassure_all"))
+            opts += self.trip_options(p, others)
             opts.append(Option("say_other", "say something else", True, kind="say"))
             for q in others:
                 if q.activity["kind"] in ("searching", "walking"):
@@ -385,6 +417,122 @@ class Morning:
             opts = [o for o in opts if act_of(o.id)[0] != kind]
         return opts
 
+    def trip_options(self, p, others):
+        """The positions on the trip open to them (reports/trip_design.md, §3.1): none before it
+        has started; never the position they already hold."""
+        if self.trip is None:
+            return []
+        pos = p.trip_heard.get(p.id)
+        own = pos[1:3] if pos else None
+        out = []
+        if not p.proposed:
+            out.append(Option("propose_trip", "say someone should go to the neighbour's house tonight", True,
+                              kind="propose"))
+        if own != ("volunteer", None):
+            out.append(Option("volunteer", "offer to go there tonight yourself", True, kind="volunteer"))
+        if p.trip_raised and own != ("object", None):
+            out.append(Option("object_trip", "say nobody should go out tonight", True, kind="object"))
+        for q in others:
+            if own != ("back", q.id):
+                out.append(Option(f"back_{q.id}", f"say {q.name} should be the one to go", True,
+                                  kind="back", target=q.id))
+        for q in others:
+            if self.named_to_go(p, q.id) and own != ("object", q.id):
+                out.append(Option(f"object_{q.id}", f"say {q.name} should not be the one to go", True,
+                                  kind="object", target=q.id))
+        backed = any(v[1:3] == ("back", p.id) for w, v in p.trip_heard.items() if w != p.id)
+        if (backed or own == ("volunteer", None)) and own != ("decline", None):
+            out.append(Option("decline", "say you will not be the one to go", True, kind="decline"))
+        return out
+
+    @staticmethod
+    def named_to_go(p, q):
+        """As far as p has heard: q offered to go, or someone backed q since q last said they
+        will not go."""
+        pos = p.trip_heard.get(q)
+        if pos and pos[1] == "volunteer":
+            return True
+        declined = pos[3] if pos and pos[1] == "decline" else -1
+        return any(v[1:3] == ("back", q) and v[3] > declined for w, v in p.trip_heard.items() if w != q)
+
+    def start_trip(self, minute):
+        """At the start of a turn: the trip concern starts if the shelf is empty or someone is
+        very hungry, once per morning. Returns who is asked because of it this turn."""
+        if not TRIP_ON or self.trip is not None:
+            return set()
+        why, asked = [], set()
+        if self.portions == 0:
+            why.append("the shelf is empty")
+            asked |= {q for q in data.ORDER if self.people[q].room == "kitchen"}
+        for q in data.ORDER:
+            if hunger_level(self.people[q].hunger) >= TRIP_HUNGER:
+                why.append(f"{NAMES[q]} is {HUNGER_WORDS[TRIP_HUNGER]}")
+                asked.add(q)
+        if not why:
+            return set()
+        self.trip = {"minute": minute, "why": why, "asked": [q for q in data.ORDER if q in asked]}
+        return asked
+
+    def heard_plan(self, p):
+        """The positions on the trip they heard, each speaker's latest, oldest first; None if
+        they have heard none (reports/trip_design.md, §4.2)."""
+        if not p.trip_heard:
+            return None
+        parts = []
+        for who, (minute, kind, target, _) in sorted(p.trip_heard.items(), key=lambda kv: kv[1][3]):
+            x = "you" if who == p.id else NAMES[who]
+            q = None if target is None else "you" if target == p.id else NAMES[target]
+            if kind == "propose":
+                said = f"{x} said someone should go"
+            elif kind == "volunteer":
+                said = f"{x} offered to go"
+            elif kind == "object":
+                said = f"{x} said nobody should go" if q is None else f"{x} said {q} should not go"
+            elif kind == "back":
+                said = f"{x} said {q} should go"
+            else:
+                said = f"{x} said {'you' if who == p.id else data.PRONOUNS[who]['he']} will not go"
+            parts.append(f"{said} (min {minute:02d})")
+        return "About going there tonight: " + "; ".join(parts) + "."
+
+    def trip_lines(self, p):
+        """What the trip concern adds after their "About the can:" line."""
+        if self.trip is None:
+            return []
+        plan = self.heard_plan(p)
+        return [data.ABOUT_FOOD, data.ABOUT_NEIGHBOUR] + ([plan] if plan else [])
+
+    def plan_text(self):
+        """The state of the plan for tonight, from every position taken (reports/trip_design.md,
+        §4.3): who has offered to go, then each other person's latest position."""
+        if not self.trip_acts:
+            return "no plan"
+        latest = {}
+        for _, who, kind, target, _ in self.trip_acts:
+            latest.pop(who, None)
+            latest[who] = (kind, target)
+        going = [NAMES[w] for w, (kind, _) in latest.items() if kind == "volunteer"]
+        if len(going) == 1:
+            parts = [f"{going[0]} will go"]
+        elif len(going) == 2:
+            parts = [f"{going[0]} and {going[1]} have both offered to go"]
+        elif going:
+            parts = [f"{', '.join(going[:-1])} and {going[-1]} have all offered to go"]
+        else:
+            parts = ["nobody has offered to go"]
+        for who, (kind, target) in latest.items():
+            x = NAMES[who]
+            if kind == "propose":
+                parts.append(f"{x} said someone should go")
+            elif kind == "back":
+                parts.append(f"{x} wants {NAMES[target]} to go")
+            elif kind == "object":
+                parts.append(f"{x} is against anyone going" if target is None else
+                             f"{x} is against {NAMES[target]} going")
+            elif kind == "decline":
+                parts.append(f"{x} will not go")
+        return "; ".join(parts)
+
     def routine(self, p, opts):
         """No model: carry on with what they were doing, or stay put."""
         ids = {o.id for o in opts}
@@ -453,6 +601,7 @@ class Morning:
         else:
             about = "About the can: you have not settled on who took it."
         out.append(f"{about} {p.can_note}" if p.can_note else about)
+        out += self.trip_lines(p)
         held = [(t, p.grudges[t]) for t in data.ORDER if t in p.grudges and p.grudges[t].strength]
         if not held:
             out.append("Against the others: nothing.")
@@ -497,7 +646,11 @@ class Morning:
         target = "you" if h["target"] == listener.id else None
         return {"ask": "asked who took the can", "deny": "denied taking it",
                 "accuse": f"accused {target or 'someone'}", "confess": "admitted taking it",
-                "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone"
+                "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone",
+                "propose": "said someone should go to the neighbour's house tonight",
+                "volunteer": "offered to go there tonight",
+                "object": "said you should not be the one to go" if target else "said nobody should go",
+                "back": "said you should be the one to go", "decline": "said they will not be the one to go",
                 }.get(h["kind"], "spoke to everyone")
 
     def prompt_for(self, p, t, opts, lull=None):
@@ -513,7 +666,8 @@ class Morning:
             f"Who you are: {s['note']}",
             f"Temperament: {trait_words(s['traits'])}.",
             f"What matters to you: {', '.join(s['values'])}.",
-        ] + inside + [f"The house: {data.HOUSE} {data.HOUSE_THINGS}"]
+        ] + inside + [f"The house: {data.HOUSE} "
+                      f"{data.HOUSE_THINGS_AFTER_TRIP if self.trip else data.HOUSE_THINGS}"]
         room = data.ROOMS[p.room]
         now = [f"Now, minute {minute:02d}, you are in the {room}."]
         others = self.others_here(p)
@@ -540,6 +694,16 @@ class Morning:
         pinned = ["What you are sure of this morning:"] + [f"- {x}" for x in p.sure]
         if p.said_lines:
             pinned += ["Your own last words this morning:"] + [f"- {x}" for x in p.said_lines[-3:]]
+        # Once the trip concern has started, its block sits outside the budget
+        # (reports/trip_design.md, §2.5): its lines, its options, the day-2 memories it keeps from
+        # trimming, and "this morning" in the house line. `block` counts its characters.
+        keep = p.trip_memories if self.trip else set()
+        block = 0
+        if self.trip:
+            block += sum(len(x) + 1 for x in self.trip_lines(p))
+            block += sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in TRIP_KINDS)
+            block += sum(len(f"- {x}") + 1 for x in keep)
+            block += len(data.HOUSE_THINGS_AFTER_TRIP) - len(data.HOUSE_THINGS)
         cut = False
         while True:
             parts = head + ["What you remember from the days before:"] + [f"- {x}" for x in back]
@@ -548,17 +712,18 @@ class Morning:
             parts += [f"- {x}" for x in morning] or ([] if cut else ["- nothing else yet"])
             parts += now + tail
             text = "\n".join(parts)
-            if estimate_tokens(SYSTEM + text) <= PROMPT_TOKEN_BUDGET or (not morning and not back):
+            loose = [x for x in back if x not in keep]      # all of them, before the trip
+            if estimate_tokens(SYSTEM + text, block) <= PROMPT_TOKEN_BUDGET or (not morning and not loose):
                 break
             cut = True
             if len(morning) > 8:
                 morning.pop(0)
-            elif len(back) > 4:
-                back.pop(0)
+            elif len(loose) > 4:
+                back.remove(loose[0])
             elif morning:
                 morning.pop(0)
             else:
-                back.pop(0)
+                back.remove(loose[0])
         self.max_prompt_tokens = max(self.max_prompt_tokens, estimate_tokens(SYSTEM + text))
         return text
 
@@ -623,6 +788,11 @@ class Morning:
             {"minute": m, "room": r, "what": what, "why": why,
              "by_inner": next(by_inner) if what == "started" else None}
             for m, r, what, why in self.convos.log]
+        # The trip concern (reports/trip_design.md, §4.1), or None if it never started.
+        self.transcript["trip"] = None if self.trip is None else {
+            **self.trip,
+            "acts": [[m, who, trip_option(kind, target), words] for m, who, kind, target, words in self.trip_acts],
+            "plan": self.plan_text()}
 
     def social_triggers(self, p, t):
         """What counts now: anything new; anything else only while the room is talking."""
@@ -660,6 +830,7 @@ class Morning:
         minute = t * data.MINUTES_PER_TURN
         record = {"minute": minute, "decisions": [], "events": [], "convo": [], "guilt": [],
                   "grudges": []}
+        self.trip_now = self.start_trip(minute)     # before anyone acts (reports/trip_design.md, §1)
         for room, name, by_inner in self.arrivals:
             self.started(room, minute, f"{name} came in", by_inner)
         self.arrivals = []
@@ -684,6 +855,7 @@ class Morning:
                      "came_of_it": d["came_of_it"], "new": d.get("new"), "new_why": d.get("new_why"),
                      "inner": d.get("inner_families"), "suspects": d.get("suspects"),
                      "angry_at": d.get("angry_at"), "lull": d.get("lull"),
+                     "trip_moment": d.get("trip_moment"),
                      "moved_to": opt.act["to"] if opt.act["kind"] in ("go", "accept_aside") else None}
             tturn["acts"].append(entry)
             return opt, entry
@@ -748,6 +920,7 @@ class Morning:
         self.convo_told = len(self.convos.log)
         self.present, self.so_far, self.acted, self.moves = None, None, None, None
         self.moved_by_inner = {}
+        self.trip_now = set()
         for p in self.people.values():
             p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
         record["portions"] = self.portions
@@ -810,9 +983,14 @@ class Morning:
                 d["inner_kinds"] = rose
                 d["inner_families"] = list(dict.fromkeys(k.split(":")[0] for k in rose))
                 d["inner"] = self.rise_words(p, rose)
-        if not triggers and not d.get("inner_kinds") and self.lull_due(p, minute):
+        # The turn the trip concern starts, whoever it names is asked (reports/trip_design.md, §1),
+        # whatever the inner-moment spacing; an inner moment is still recorded if it is due.
+        if p.id in self.trip_now:
+            d["trip_moment"] = self.trip["minute"]
+            d["trip_why"] = "; ".join(self.trip["why"])
+        if not triggers and not d.get("inner_kinds") and "trip_moment" not in d and self.lull_due(p, minute):
             d["lull"] = self.last_stir[p.room]
-        if triggers or d.get("inner_kinds") or "lull" in d:
+        if triggers or d.get("inner_kinds") or "trip_moment" in d or "lull" in d:
             choice, why = self.ask_model(p, t, opts, d)
             if not choice:
                 d.update(mode="fallback", invalid=why, option=self.routine(p, opts), say=None)
@@ -868,6 +1046,17 @@ class Morning:
             gist = f"{p.name} admits taking it, to everyone"
         elif kind == "reassure":
             gist = f"{p.name} reassures {aimed or 'everyone'}"
+        elif kind == "propose":
+            gist = f"{p.name} says someone should go to the neighbour's house tonight"
+        elif kind == "volunteer":
+            gist = f"{p.name} offers to go to the neighbour's house tonight"
+        elif kind == "object":
+            gist = (f"{p.name} says {aimed} should not be the one to go" if aimed
+                    else f"{p.name} says nobody should go out tonight")
+        elif kind == "back":
+            gist = f"{p.name} says {aimed} should be the one to go"
+        elif kind == "decline":
+            gist = f"{p.name} says {data.PRONOUNS[p.id]['he']} will not be the one to go"
         elif while_doing:
             gist = f"{p.name} says to {aimed or 'everyone'}, while {while_doing}"
         else:
@@ -982,7 +1171,24 @@ class Morning:
             voices.append((room, new, {p.id} | {q.id for q in seen}))
             mine = {"ask": "asked who took it", "deny": "denied taking it",
                     "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
-                    "reassure": f"reassured {target.name if aimed else 'everyone'}"}.get(kind, "said")
+                    "reassure": f"reassured {target.name if aimed else 'everyone'}",
+                    "propose": "said someone should go to the neighbour's house tonight",
+                    "volunteer": "offered to go there tonight",
+                    "object": (f"said {target.name} should not be the one to go" if target
+                               else "said nobody should go out tonight"),
+                    "back": f"said {target.name if target else ''} should be the one to go",
+                    "decline": "said you will not be the one to go"}.get(kind, "said")
+            if kind in TRIP_KINDS:
+                # The plan record (reports/trip_design.md, §4.1): every position taken, and each
+                # speaker's latest one for everyone who heard it, the speaker included.
+                aim = target_id if aimed else None
+                self.trip_acts.append((minute, p.id, kind, aim, words))
+                for x in [p] + seen:
+                    x.trip_heard[p.id] = (minute, kind, aim, self.seq)
+                    if kind in ("propose", "volunteer", "back"):
+                        x.trip_raised = True
+                if kind == "propose":
+                    p.proposed = True
             # Their own lines reach them without the words: minute and verb only
             # (reports/repetition_probe.md, variant B). The others hear the words.
             p.memory.append((minute, f"you {mine}.{feel}"))
```

## 8. Scripts

### `$S/first_post.py`

```python
"""The v11 code on copies of the v10 caches (replay, no client): the first prompt after the
trigger in each seed, diffed against the v10 prompt of the same person at the same minute."""
import difflib, json, os, shutil, sys, tempfile
sys.path.insert(0, '.')
import gemini
from gemini import Cache, Oracle
from world import Morning, SYSTEM, estimate_tokens


class Recorder:
    def __init__(self, oracle):
        self.oracle, self.prompts = oracle, []

    def ask(self, system, prompt):
        self.prompts.append(prompt)
        return self.oracle.ask(system, prompt)


for seed in (1, 2, 3):
    src = f'cache/v10/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json'
    path = os.path.join(tempfile.mkdtemp(), 'c.json')
    shutil.copy(src, path)
    oracle = Oracle(Cache(path), 'gemini-3.5-flash-lite', seed, client=None, replay=True)
    rec = Recorder(oracle)
    m = Morning(rec, seed)
    try:
        for t in range(m.turns):
            m.turn(t)
    except gemini.CacheMiss:
        pass
    new = rec.prompts[-1]
    head = new.split('\n')[0].split(',')[0]
    minute = new.split('Now, minute ')[1][:2]
    old = next(e['prompt'] for e in json.load(open(src, encoding='utf-8')).values()
               if e['prompt'].startswith(head + ',') and f'Now, minute {minute},' in e['prompt'])
    print(f'seed {seed}: trip {m.trip}; served from cache {oracle.from_cache}, API requests {oracle.api_requests}; '
          f'first prompt after it: {head[8:]} at minute {minute}')
    print(f'  estimated tokens: v10 {estimate_tokens(SYSTEM + old)}, v11 {estimate_tokens(SYSTEM + new)}')
    for line in difflib.unified_diff(old.split('\n'), new.split('\n'), 'v10', 'v11', lineterm='', n=0):
        print('  ' + (line if len(line) < 200 else line[:120] + ' … ' + line[-80:]))
```
