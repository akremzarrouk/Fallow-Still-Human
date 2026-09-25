# LLM morning prototype, step 3: inner pressure and lasting grudges

Each person now carries hunger, a suspicion and a grudge, and Daniel carries guilt. The rules keep them, the model's answers move them, and the model sees them in words. When one rises during silence, the person gets an *inner moment*: a model decision with nothing social happening. People can take someone aside, and a conversation now ends after two quiet turns instead of one. The earlier reports, [REPORT.md](REPORT.md) and [REPORT-2.md](REPORT-2.md), and their runs are left as they were; this step's runs are in `runs/v3/`. Model: `gemini-3.5-flash-lite`, unchanged.

## Done when

| Condition | Result |
|---|---|
| all tests pass | 37 of 37, against the fake model and a stubbed API |
| 3 fresh mornings (seeds 1, 2, 3) under 150 real calls each | 37, 36, 30 API requests; all reached minute 90 |
| `--replay` of seed 1 byte-identical with 0 calls | IDENTICAL, 0 API requests, run with `GEMINI_API_KEY` unset; `cmp` and SHA-256 agree |
| REPORT-3.md has the metrics table for the v2 runs and the new ones | below |

## Metrics

| Run | Model calls | Lines spoken | Longest stretch with no model decision (minutes) | Inner moments (what rose) | Conversations restarted by an inner moment | Private talks (accepted / refused) | Daniel confessed | Food eaten or shared |
|---|---|---|---|---|---|---|---|---|
| v2, seed 1 | 7 | 6 | 84 (min 06–90) | 0 (none in v2) | 0 (none in v2) | 0 / 0 (none in v2) | no | no |
| v2, seed 2 | 25 | 13 | 63 (min 27–90) | 0 (none in v2) | 0 (none in v2) | 0 / 0 (none in v2) | no | no |
| v2, seed 3 | 11 | 8 | 81 (min 09–90) | 0 (none in v2) | 0 (none in v2) | 0 / 0 (none in v2) | no | no |
| v3, seed 1 | 37 | 23 | 18 (min 42–60) | 6 (hunger 5, suspicion 1, grudge 1) | 0 | 0 / 0 | yes, min 03 | Daniel ate (min 12); Daniel shared (min 15) |
| v3, seed 2 | 36 | 19 | 15 (min 39–54) | 10 (hunger 7, suspicion 4) | 2 | 0 / 0 | yes, min 03 | Daniel ate (min 33); Mara ate (min 54) |
| v3, seed 3 | 30 | 21 | 18 (min 36–54) | 8 (hunger 6, suspicion 2) | 0 | 0 / 0 | yes, min 03 | no |

Suspicion and grudge at minute 90 (a person and a strength out of 3, or none), and Daniel's guilt. The v2 rules kept none of these:

| Run | Daniel: suspects / grudge | Elena: suspects / grudge | Leo: suspects / grudge | Mara: suspects / grudge | Daniel's guilt |
|---|---|---|---|---|---|
| v2, seed 1 | not tracked | not tracked | not tracked | not tracked | not tracked |
| v2, seed 2 | not tracked | not tracked | not tracked | not tracked | not tracked |
| v2, seed 3 | not tracked | not tracked | not tracked | not tracked | not tracked |
| v3, seed 1 | none / none | Daniel 3/3 / none | Daniel 3/3 / Daniel 3/3 | Daniel 3/3 / Daniel 3/3 | 3/3 |
| v3, seed 2 | none / none | Daniel 3/3 / none | Daniel 3/3 / none | none / none | 3/3 |
| v3, seed 3 | none / none | Daniel 3/3 / none | Daniel 3/3 / none | Daniel 3/3 / Daniel 3/3 | 3/3 |

`metrics3.py` computes both tables from the runs' transcripts, the same way for v2 and v3.

- **Model calls**: decisions the model made, a take-aside reply included. In all six runs this equals the API requests; there were no retries.
- **Lines spoken**: every line said aloud, including a line said while doing something else.
- **Longest stretch with no model decision**: the longest run of 3-minute turns in which the model decided nothing for anyone in the house.
- **Inner moments**: model decisions with nothing social happening, because something had risen. The brackets count what rose; one moment can have two causes.
- **Conversations restarted by an inner moment**: conversation starts caused by what someone did in an inner moment, directly or by walking into a room.
- **Private talks**: take-aside requests, split by whether the other person went.

### Every inner moment, and every conversation it started

For each: seed, minute, who, what rose, and the option they chose.

```
Inner moments, one by one:
- v3, seed 1, min 15, Leo: hunger, suspicion -> accuse_daniel
- v3, seed 1, min 24, Leo: grudge -> accuse_daniel
- v3, seed 1, min 27, Mara: hunger -> accuse_daniel
- v3, seed 1, min 39, Leo: hunger -> silent
- v3, seed 1, min 60, Elena: hunger -> silent
- v3, seed 1, min 81, Mara: hunger -> accuse_daniel
- v3, seed 2, min 12, Leo: suspicion -> silent
- v3, seed 2, min 12, Elena: suspicion -> silent
- v3, seed 2, min 21, Leo: hunger, suspicion -> silent
- v3, seed 2, min 21, Elena: suspicion -> silent
- v3, seed 2, min 30, Elena: hunger -> reassure_all
- v3, seed 2, min 33, Daniel: hunger -> eat
- v3, seed 2, min 54, Mara: hunger -> eat
- v3, seed 2, min 63, Leo: hunger -> silent
- v3, seed 2, min 75, Elena: hunger -> reassure_all
- v3, seed 2, min 78, Daniel: hunger -> reassure_elena
- v3, seed 3, min 12, Elena: suspicion -> reassure_all
- v3, seed 3, min 21, Elena: suspicion -> reassure_all
- v3, seed 3, min 30, Elena: hunger -> reassure_all
- v3, seed 3, min 33, Daniel: hunger -> reassure_all
- v3, seed 3, min 54, Mara: hunger -> accuse_daniel
- v3, seed 3, min 63, Leo: hunger -> silent
- v3, seed 3, min 66, Daniel: hunger -> reassure_mara
- v3, seed 3, min 75, Elena: hunger -> reassure_all

Conversations started by an inner moment:
- v3, seed 2, min 33, kitchen: Daniel ate one of the portions
- v3, seed 2, min 54, kitchen: Mara ate one of the portions
```

## What stands out

These are observations; the judge is a person reading the stories below.

- **The house no longer freezes.** The longest stretch with no model decision fell from 63 to 84 minutes (v2) to 15 to 18. Model calls rose from 7 to 25 to between 30 and 37. There were 24 inner moments across the three runs:
  - 18 of their 26 causes were hunger crossing into *very hungry* or *starving*; 7 were suspicion, 1 grudge, and none guilt;
  - they ended in reassurance 9 times, silence 8, accusing Daniel 5, and eating 2;
  - only the two meals started the kitchen's talk again (seed 2: Daniel eats at minute 33, Mara at minute 54). Leo's accusation at minute 15 (seed 1) came while the kitchen was still talking; the other four accusations repeated ones already made, which the rules do not count as new;
  - so the gaps between moments are still quiet.
- **Daniel confesses at minute 3 in all three runs.** That makes the same story every time, which the target calls a script. Nothing forces it: the model chose it each time, but the path is the same:
  - Elena reassures everyone at minute 0 or 3 in every run, and under the rules each reassurance adds a step of guilt;
  - so does his own denial;
  - by minute 3 his prompt says what he did "weighs on you heavily" (seeds 1 and 2) or that the guilt "is crushing you" (seed 3), and he admits it. His reasons: "I cannot lie anymore while my family tears themselves apart", "The weight of my lie is too much to bear".

  Before this step he confessed in 2 of 3 old v1 runs (minutes 18 and 42) and in none of the v2 runs. His guilt ends at 3 of 3 in every run; it never falls. As the brief asked, I did not tune this after seeing it.
- **Grudges last, but not everywhere.**
  - Seed 1: Mara accuses Daniel at minutes 9, 12, 15, 21 and 27, and again at 81 in an inner moment ("You're the reason we're all sitting here starving, Daniel"). She and Leo end at a grudge of 3 of 3 against him.
  - Seed 3: Mara ends at 3 of 3, and Elena turns on him at minute 9.
  - Seed 2: all three forgive him within three minutes of the confession ("It is okay, Daniel"), and nobody holds a grudge at minute 90. That is the target's Never item "Someone who was wronged forgives within minutes, with no lasting cost". Leo does the same in seed 3 ("It's alright, Daniel. We all reach our limit sometimes.").
- **Nobody took anyone aside.** The option was offered in 73 of the 103 real prompts and never chosen.
- **Food.** In seed 1 Daniel eats a portion at minute 12, nine minutes after confessing ("I need to keep my strength up to protect you all"). At minute 15 he shares out the last one, as Leo and Mara accuse him. In seed 2 Daniel and Mara each eat one in inner moments of hunger. In seed 3 nobody touches the food.
- **After the confession the talk narrows.** It becomes Daniel promising to fix things and Elena saying they will get through it together. One slip: in seed 3 at minute 15, Mara tells Daniel "you need to admit it right now", twelve minutes after she heard him admit it.
- Everyone who heard the confession ends up sure Daniel took it (3 of 3), as expected.

Ways to change the confession or the forgiving would change the rules you set, so they are yours to choose. For example:
- start guilt higher but let only direct reassurance of Daniel raise it;
- let a grudge lower how readily someone reassures the person it is against;
- make a grudge's words stronger in the prompt.

## Changes beyond the brief, and why

- **Interpretations the brief left open:**
  - *"Risen since their last decision"* compares with the levels their last model prompt showed them. A rise that their own answer caused, such as naming Leo again, counts at their next quiet moment. Suspicion and grudge change only through answers, so without this they could never cause an inner moment.
  - Naming someone other than the current target counts as a step down, under the same 15-minute limit. Once at 0, the new name takes it at 1. Naming yourself counts as "nobody".
  - Guilt starts at 0 and never falls. Daniel's own accusation counts once, not also as "someone accused in his hearing". "Someone reassures him" includes reassuring everyone while he hears it. Being accused himself does not raise it.
  - Take aside is offered only for someone who has not acted yet this turn. Their answer is their one model call for the turn, which keeps the one-call-per-person limit.
  - The room for a talk aside: the taker's own room if empty, then another empty private room, then the kitchen, then the bathroom.
  - An unusable answer to a take-aside counts as a refusal. After a talk aside the taker acts first next turn; after a refusal, the taker is "spoken to" and acts first.
  - The model's `suspects` and `angry_at` are limited by the response schema to the four names or "nobody". Anything else would be an unusable answer; none occurred.
  - Each prompt says what has risen since the person last decided ("Since you last decided: ..."), at social moments as well as inner ones.
  - Hunger's thresholds are unchanged (0.5, 0.7, 0.85); its top word is now *starving*.
- **The 150-call cap now counts answers already cached for the same morning**, so a morning resumed after the daily quota still stays under 150. A test covers it. No run needed a resume.
- **`v2/` is a frozen copy of the second version**, like `v1/`, and `v2/check.py` confirms it replays the three v2 runs exactly, stories and transcripts. This step writes to `runs/v3/` and `cache/v3/`.
- **`talk.py`** takes the number of quiet turns as a parameter (v3 uses 2). Step 2's `metrics.py` still gives exactly REPORT-2's table (checked); it also learned to read moves from take-aside acts. `metrics3.py` is new.
- **A bug found by the tests before any real run:** the reply option `go_aside` matched the `go_` prefix, so going aside was treated as walking to a room called "aside". The replies are now `accept_aside` and `refuse_aside`.
- **Test changes:**
  - the scripted test model returns the two new fields;
  - the conversation-end test now expects two quiet turns;
  - the test where a finished search restarts talk became one where an inner moment (hunger set directly) restarts it;
  - new tests cover the slow fall, guilt, the 9-minute limit, take-aside (accepted, refused, and when it is offered) and the call cap across a resume.
- Nothing was tuned after the real runs.

## Commands and their output

All commands run in `Prototypes/llm-morning/`, using the venv's Python (`.venv/Scripts/python`).

### Tests (fake model and stubbed API only)

```bash
python -m unittest -v test_morning
```

```
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
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
ok
test_repeated_429_gives_up_cleanly (test_morning.GeminiClientTest.test_repeated_429_gives_up_cleanly) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
ok
test_the_key_is_never_printed_or_saved (test_morning.GeminiClientTest.test_the_key_is_never_printed_or_saved) ... ok
test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes (test_morning.PressureTest.test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes) ... ok
test_daniel_accusing_someone_counts_once (test_morning.PressureTest.test_daniel_accusing_someone_counts_once) ... ok
test_daniels_guilt_rises_by_the_rules (test_morning.PressureTest.test_daniels_guilt_rises_by_the_rules) ... ok
test_inner_moments_come_at_most_once_every_9_minutes (test_morning.PressureTest.test_inner_moments_come_at_most_once_every_9_minutes) ... ok
test_naming_yourself_counts_as_nobody (test_morning.PressureTest.test_naming_yourself_counts_as_nobody) ... ok
test_take_aside_accepted (test_morning.PressureTest.test_take_aside_accepted) ... ok
test_take_aside_needs_someone_yet_to_act_and_an_empty_room (test_morning.PressureTest.test_take_aside_needs_someone_yet_to_act_and_an_empty_room) ... ok
test_take_aside_refused (test_morning.PressureTest.test_take_aside_refused) ... ok
test_the_answers_move_the_grudge_and_the_prompt_says_it_in_words (test_morning.PressureTest.test_the_answers_move_the_grudge_and_the_prompt_says_it_in_words) ... ok
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

----------------------------------------------------------------------
Ran 37 tests in 7.934s

OK
```

### The earlier versions still replay exactly

```bash
env -u GEMINI_API_KEY python v2/check.py
env -u GEMINI_API_KEY python v1/transcript.py
```

```
seed 1: replayed 7 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 11 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL

seed 1: replayed 120 answers from the cache, 0 API calls; story IDENTICAL to runs/daniel_ate_it-seed1.md; wrote runs\daniel_ate_it-seed1.transcript.json
seed 2: replayed 39 answers from the cache, 0 API calls; story IDENTICAL to runs/daniel_ate_it-seed2.md; wrote runs\daniel_ate_it-seed2.transcript.json
seed 3: replayed 90 answers from the cache, 0 API calls; story IDENTICAL to runs/daniel_ate_it-seed3.md; wrote runs\daniel_ate_it-seed3.transcript.json
```

### Fresh morning, seed 1

```bash
python morning.py --seed 1
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v3\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 4; so far 20 live, 0 cached, 20 API requests
  min 15: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 18: model asked for 4; so far 28 live, 0 cached, 28 API requests
  min 21: model asked for 4; so far 32 live, 0 cached, 32 API requests
  min 24: model asked for 1; so far 33 live, 0 cached, 33 API requests
  min 27: model asked for 1; so far 34 live, 0 cached, 34 API requests
  min 39: model asked for 1; so far 35 live, 0 cached, 35 API requests
  min 60: model asked for 1; so far 36 live, 0 cached, 36 API requests
  min 81: model asked for 1; so far 37 live, 0 cached, 37 API requests

wrote runs/v3/daniel_ate_it-seed1.md
  api_requests: 37
  answers_live: 37
  answers_from_cache: 0
  model_decisions: 37
  fallbacks: 0
  routine_decisions: 83
  lines_spoken: 23
  inner_moments: 6
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1359
  run_seconds: 163.3
  story_sha256: 265aa38cc89cd71ea0bafaf9e4f3e617d9853a352d0c50bbb518487814516c73
```

### Fresh morning, seed 2

```bash
python morning.py --seed 2
```

```
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v3\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 3; so far 11 live, 0 cached, 11 API requests
  min 09: model asked for 4; so far 15 live, 0 cached, 15 API requests
  min 12: model asked for 2; so far 17 live, 0 cached, 17 API requests
  min 21: model asked for 2; so far 19 live, 0 cached, 19 API requests
  min 30: model asked for 1; so far 20 live, 0 cached, 20 API requests
  min 33: model asked for 1; so far 21 live, 0 cached, 21 API requests
  min 36: model asked for 3; so far 24 live, 0 cached, 24 API requests
  min 54: model asked for 2; so far 26 live, 0 cached, 26 API requests
  min 57: model asked for 4; so far 30 live, 0 cached, 30 API requests
  min 60: model asked for 3; so far 33 live, 0 cached, 33 API requests
  min 63: model asked for 1; so far 34 live, 0 cached, 34 API requests
  min 75: model asked for 1; so far 35 live, 0 cached, 35 API requests
  min 78: model asked for 1; so far 36 live, 0 cached, 36 API requests

wrote runs/v3/daniel_ate_it-seed2.md
  api_requests: 36
  answers_live: 36
  answers_from_cache: 0
  model_decisions: 36
  fallbacks: 0
  routine_decisions: 84
  lines_spoken: 19
  inner_moments: 10
  private_talks: 0
  max_prompt_tokens_estimated: 1399
  max_prompt_tokens_counted_by_api: 1377
  run_seconds: 158.6
  story_sha256: 16bf12886a50854ef4ac0e607f61a48b4f6ba40a4f788a6e185c4ce6dfcd45ca
```

### Fresh morning, seed 3

```bash
python morning.py --seed 3
```

```
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v3\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 4; so far 20 live, 0 cached, 20 API requests
  min 15: model asked for 3; so far 23 live, 0 cached, 23 API requests
  min 21: model asked for 1; so far 24 live, 0 cached, 24 API requests
  min 30: model asked for 1; so far 25 live, 0 cached, 25 API requests
  min 33: model asked for 1; so far 26 live, 0 cached, 26 API requests
  min 54: model asked for 1; so far 27 live, 0 cached, 27 API requests
  min 63: model asked for 1; so far 28 live, 0 cached, 28 API requests
  min 66: model asked for 1; so far 29 live, 0 cached, 29 API requests
  min 75: model asked for 1; so far 30 live, 0 cached, 30 API requests

wrote runs/v3/daniel_ate_it-seed3.md
  api_requests: 30
  answers_live: 30
  answers_from_cache: 0
  model_decisions: 30
  fallbacks: 0
  routine_decisions: 90
  lines_spoken: 21
  inner_moments: 8
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1352
  run_seconds: 131.6
  story_sha256: 997635e099477daa68792990a7746600daa3b4191051035aa8b0f58105090cff
```

Run times: seed 1 163 s, seed 2 159 s, seed 3 132 s. Real generate requests in this Pacific-time quota day: 298 (step 1) + 43 (step 2) + 103 (here) = 444 of 500.

### Replay of seed 1 (key unset, cache only)

```bash
env -u GEMINI_API_KEY python morning.py --seed 1 --replay
cmp runs/v3/daniel_ate_it-seed1.md runs/v3/daniel_ate_it-seed1.replay.md && echo "cmp: identical"
sha256sum runs/v3/daniel_ate_it-seed1.md runs/v3/daniel_ate_it-seed1.replay.md
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, replay from cache only; cache cache\v3\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 37 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 4; so far 0 live, 12 cached, 0 API requests
  min 09: model asked for 4; so far 0 live, 16 cached, 0 API requests
  min 12: model asked for 4; so far 0 live, 20 cached, 0 API requests
  min 15: model asked for 4; so far 0 live, 24 cached, 0 API requests
  min 18: model asked for 4; so far 0 live, 28 cached, 0 API requests
  min 21: model asked for 4; so far 0 live, 32 cached, 0 API requests
  min 24: model asked for 1; so far 0 live, 33 cached, 0 API requests
  min 27: model asked for 1; so far 0 live, 34 cached, 0 API requests
  min 39: model asked for 1; so far 0 live, 35 cached, 0 API requests
  min 60: model asked for 1; so far 0 live, 36 cached, 0 API requests
  min 81: model asked for 1; so far 0 live, 37 cached, 0 API requests

wrote runs/v3/daniel_ate_it-seed1.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 37
  model_decisions: 37
  fallbacks: 0
  routine_decisions: 83
  lines_spoken: 23
  inner_moments: 6
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1359
  run_seconds: 0.0
  story_sha256: 265aa38cc89cd71ea0bafaf9e4f3e617d9853a352d0c50bbb518487814516c73
  byte for byte against runs\v3\daniel_ate_it-seed1.md: IDENTICAL
```

```
cmp: identical
265aa38cc89cd71ea0bafaf9e4f3e617d9853a352d0c50bbb518487814516c73 *runs/v3/daniel_ate_it-seed1.md
265aa38cc89cd71ea0bafaf9e4f3e617d9853a352d0c50bbb518487814516c73 *runs/v3/daniel_ate_it-seed1.replay.md
```

### Metrics

```bash
python metrics3.py
```

```
| Run | Model calls | Lines spoken | Longest stretch with no model decision (minutes) | Inner moments (what rose) | Conversations restarted by an inner moment | Private talks (accepted / refused) | Daniel confessed | Food eaten or shared |
|---|---|---|---|---|---|---|---|---|
| v2, seed 1 | 7 | 6 | 84 (min 06–90) | 0 (none in v2) | 0 (none in v2) | 0 / 0 (none in v2) | no | no |
| v2, seed 2 | 25 | 13 | 63 (min 27–90) | 0 (none in v2) | 0 (none in v2) | 0 / 0 (none in v2) | no | no |
| v2, seed 3 | 11 | 8 | 81 (min 09–90) | 0 (none in v2) | 0 (none in v2) | 0 / 0 (none in v2) | no | no |
| v3, seed 1 | 37 | 23 | 18 (min 42–60) | 6 (hunger 5, suspicion 1, grudge 1) | 0 | 0 / 0 | yes, min 03 | Daniel ate (min 12); Daniel shared (min 15) |
| v3, seed 2 | 36 | 19 | 15 (min 39–54) | 10 (hunger 7, suspicion 4) | 2 | 0 / 0 | yes, min 03 | Daniel ate (min 33); Mara ate (min 54) |
| v3, seed 3 | 30 | 21 | 18 (min 36–54) | 8 (hunger 6, suspicion 2) | 0 | 0 / 0 | yes, min 03 | no |

Suspicion and grudge at minute 90, and Daniel's guilt (the rules kept none of these in v2):

| Run | Daniel: suspects / grudge | Elena: suspects / grudge | Leo: suspects / grudge | Mara: suspects / grudge | Daniel's guilt |
|---|---|---|---|---|---|
| v2, seed 1 | not tracked | not tracked | not tracked | not tracked | not tracked |
| v2, seed 2 | not tracked | not tracked | not tracked | not tracked | not tracked |
| v2, seed 3 | not tracked | not tracked | not tracked | not tracked | not tracked |
| v3, seed 1 | none / none | Daniel 3/3 / none | Daniel 3/3 / Daniel 3/3 | Daniel 3/3 / Daniel 3/3 | 3/3 |
| v3, seed 2 | none / none | Daniel 3/3 / none | Daniel 3/3 / none | none / none | 3/3 |
| v3, seed 3 | none / none | Daniel 3/3 / none | Daniel 3/3 / none | Daniel 3/3 / Daniel 3/3 | 3/3 |

Inner moments, one by one:
- v3, seed 1, min 15, Leo: hunger, suspicion -> accuse_daniel
- v3, seed 1, min 24, Leo: grudge -> accuse_daniel
- v3, seed 1, min 27, Mara: hunger -> accuse_daniel
- v3, seed 1, min 39, Leo: hunger -> silent
- v3, seed 1, min 60, Elena: hunger -> silent
- v3, seed 1, min 81, Mara: hunger -> accuse_daniel
- v3, seed 2, min 12, Leo: suspicion -> silent
- v3, seed 2, min 12, Elena: suspicion -> silent
- v3, seed 2, min 21, Leo: hunger, suspicion -> silent
- v3, seed 2, min 21, Elena: suspicion -> silent
- v3, seed 2, min 30, Elena: hunger -> reassure_all
- v3, seed 2, min 33, Daniel: hunger -> eat
- v3, seed 2, min 54, Mara: hunger -> eat
- v3, seed 2, min 63, Leo: hunger -> silent
- v3, seed 2, min 75, Elena: hunger -> reassure_all
- v3, seed 2, min 78, Daniel: hunger -> reassure_elena
- v3, seed 3, min 12, Elena: suspicion -> reassure_all
- v3, seed 3, min 21, Elena: suspicion -> reassure_all
- v3, seed 3, min 30, Elena: hunger -> reassure_all
- v3, seed 3, min 33, Daniel: hunger -> reassure_all
- v3, seed 3, min 54, Mara: hunger -> accuse_daniel
- v3, seed 3, min 63, Leo: hunger -> silent
- v3, seed 3, min 66, Daniel: hunger -> reassure_mara
- v3, seed 3, min 75, Elena: hunger -> reassure_all

Conversations started by an inner moment:
- v3, seed 2, min 33, kitchen: Daniel ate one of the portions
- v3, seed 2, min 54, kitchen: Mara ate one of the portions
```

## The stories

Each is included in full, exactly as written to `runs/v3/`, with its headings moved down two levels to fit this report.

### The morning as a story: daniel_ate_it, rules and a language model, seed 1

Generated by `python morning.py --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 37 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 83 routine ones settled by the rules. 23 lines were spoken aloud, 4 of them new. Conversations ended 1 time. 6 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can) and a grudge (who they are angry with), each a person and a strength from 0 to 3; and for Daniel, guilt from 0 to 3. The model is shown them in words.
- **Suspects / Angry at**: every model answer names who they now believe took the can and who they are angry with, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Daniel's guilt** rises a step each time he denies or accuses someone, each time he hears someone else accused, and each time someone reassures him or everyone. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

#### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

##### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

#### The morning

**min 00** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 22 options). Feeling: *guilty*. Reason: “I know I ate the can myself in the dark, so I cannot accuse anyone else.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 21 options). Feeling: *calm*. Reason: “There is no proof yet, so I will stay quiet and observe rather than jump to conclusions.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: reassure everyone here**, saying “We are going to be fine, nobody needs to worry. We just need to stay together.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I must keep the family calm and prevent them from turning on each other.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena reassures everyone: "We are going to be fine, nobody needs to worry. We just need to stay together.". **Chose: ask everyone here who took the can**, saying “Wait, if a can is missing, who actually took it?” *(new: a question)* (one of 19 options). Feeling: *anxious*. Reason: “I need to know what is happening instead of everyone pretending everything is fine.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Leo.
- *Daniel's guilt rises to 1 of 3: Elena reassured everyone.*
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Wait, if a can is missing, who actually took it?". **Chose: reassure everyone here**, saying “Let us not turn on each other. We are all we have right now.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and prevent the tension from tearing our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We are going to be fine, nobody needs to worry. We just need to stay together."; Mara asks everyone who took the can: "Wait, if a can is missing, who actually took it?"; Elena reassures everyone: "Let us not turn on each other. We are all we have right now.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calm*. Reason: “There is no point in arguing when accusations solve nothing and only make the tension worse.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us not turn on each other. We are all we have right now.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “I feel completely overwhelmed by the tension and don't know what to say anymore.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "We are going to be fine, nobody needs to worry. We just need to stay together."; Mara asks everyone who took the can: "Wait, if a can is missing, who actually took it?"; Elena reassures everyone: "Let us not turn on each other. We are all we have right now.". **Chose: admit taking it**, saying “I took it, I ate it in the night. It was me.” *(new: a confession)* (one of 20 options). Feeling: *deeply guilty*. Reason: “I cannot let them accuse each other when I know the truth.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- *Daniel's guilt rises to 2 of 3: Elena reassured everyone.*

**min 06** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel admits taking it, to everyone: "I took it, I ate it in the night. It was me.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *calm*. Reason: “Daniel already confessed, so there is no need to make things worse or say anything right now.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel admits taking it, to everyone: "I took it, I ate it in the night. It was me.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *stunned*. Reason: “I cannot believe he actually did it, but at least we finally know the truth.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel admits taking it, to everyone: "I took it, I ate it in the night. It was me.". **Chose: reassure Daniel**, saying “Thank you for telling us the truth, Daniel. We are going to get through this together.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply worried*. Reason: “I need to support Daniel now that he confessed so he does not feel entirely broken by this.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: just spoken to by Elena). Social moment: Elena reassures you: "Thank you for telling us the truth, Daniel. We are going to get through this together.". **Chose: reassure everyone here**, saying “I am sorry, I should not have done it, but I promise we will figure this out.” *(not new: reassurance)* (one of 14 options). Feeling: *guilty*. Reason: “I need to reassure them all and prove I am still worthy of leading us through this.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- *Daniel's guilt rises to 3 of 3: Elena reassured him.*

**min 09** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures Daniel: "Thank you for telling us the truth, Daniel. We are going to get through this together."; Daniel reassures everyone: "I am sorry, I should not have done it, but I promise we will figure this out.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *calm*. Reason: “Daniel already admitted it, so there is nothing left for me to add right now.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures Daniel: "Thank you for telling us the truth, Daniel. We are going to get through this together."; Daniel reassures everyone: "I am sorry, I should not have done it, but I promise we will figure this out.". **Chose: accuse Daniel of taking it**, saying “You just said you took it, Daniel, but how can we even believe you now?” *(new: an accusation)* (one of 18 options). Feeling: *anxious*. Reason: “I want to believe him, but I can't shake the feeling he is lying or hiding something worse.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel, so grudge Daniel 1/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "You just said you took it, Daniel, but how can we even believe you now?". **Chose: reassure Mara**, saying “Mara, I know I messed up, but you have to believe I am telling you the truth now.” *(not new: reassurance)* (one of 15 options). Feeling: *guilty*. Reason: “I need to make Mara understand that I am being honest with them now, even after what I did.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "I am sorry, I should not have done it, but I promise we will figure this out."; Mara accuses Daniel of taking it: "You just said you took it, Daniel, but how can we even believe you now?"; Daniel reassures Mara: "Mara, I know I messed up, but you have to believe I am telling you the truth now.". Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 12 options). Feeling: *deeply worried*. Reason: “I need to keep the peace and stay quiet so things do not fall apart further.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 12** · kitchen: Daniel eating, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Daniel). Social moment: Daniel reassures you: "Mara, I know I messed up, but you have to believe I am telling you the truth now.". **Chose: accuse Daniel of taking it**, saying “You keep acting like this makes everything fine, Daniel, but it doesn't fix what you did.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *resentful*. Reason: “I cannot just let him off the hook like nothing happened when he took our food.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 2/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "You keep acting like this makes everything fine, Daniel, but it doesn't fix what you did.". **Chose: eat one of the portions**, saying “I need to keep my strength up to protect you all, I am taking this one.” *(not new: a remark (the rules cannot tell what free words add))* (one of 16 options). Feeling: *guilty*. Reason: “I cannot take the constant accusations when I am the one trying to fix this.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: ate a portion; 1 left. New in the room: Daniel ate one of the portions.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "You keep acting like this makes everything fine, Daniel, but it doesn't fix what you did."; Daniel says to everyone, while eating: "I need to keep my strength up to protect you all, I am taking this one."; Daniel eats one of the portions. **Chose: reassure everyone here**, saying “Let us calm down. Arguing will only tear us apart when we need each other most.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply worried*. Reason: “I need to keep the family together and stop the fighting before it destroys us.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "You just said you took it, Daniel, but how can we even believe you now?"; Daniel reassures Mara: "Mara, I know I messed up, but you have to believe I am telling you the truth now."; Mara accuses Daniel of taking it: "You keep acting like this makes everything fine, Daniel, but it doesn't fix what you did."; Daniel says to everyone, while eating: "I need to keep my strength up to protect you all, I am taking this one."; Daniel eats one of the portions; Elena reassures everyone: "Let us calm down. Arguing will only tear us apart when we need each other most.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *calm*. Reason: “There is no point in arguing further when he has already admitted it and is eating the food.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 15** · kitchen: Daniel sharing out the food, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry); suspicion of Daniel rose (now 3 of 3). **Chose: accuse Daniel of taking it**, saying “You already ate one, Daniel. There is only one left and it is not yours to take.” *(new: an accusation)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel has already taken one portion and needs to be called out before he takes the last one.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 1/3. Came of it: said to Daniel, Elena, Mara.
- **Daniel** (2nd to act in the kitchen: just accused by Leo). Social moment: Elena reassures everyone: "Let us calm down. Arguing will only tear us apart when we need each other most."; Leo accuses you of taking it: "You already ate one, Daniel. There is only one left and it is not yours to take.". **Chose: share out what is left among everyone here**, saying “There is only one portion left, but we will split it so no one goes without.” *(not new: a remark (the rules cannot tell what free words add))* (one of 16 options). Feeling: *deep guilt*. Reason: “I cannot take any more food while my family is starving because of my secret.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: shared out the last 1 portions between Daniel, Elena, Leo, Mara. New in the room: Daniel shared out the food.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo accuses Daniel of taking it: "You already ate one, Daniel. There is only one left and it is not yours to take."; Daniel says to everyone, while sharing out the food: "There is only one portion left, but we will split it so no one goes without."; Daniel shares out the last 1 portion between Daniel, Elena, Leo, Mara. **Chose: stay put and say nothing** (one of 15 options). Feeling: *anxious*. Reason: “I have already said enough to keep the peace, and now I just need to make sure we eat what is left without further fighting.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while eating: "I need to keep my strength up to protect you all, I am taking this one."; Daniel eats one of the portions; Elena reassures everyone: "Let us calm down. Arguing will only tear us apart when we need each other most."; Leo accuses Daniel of taking it: "You already ate one, Daniel. There is only one left and it is not yours to take."; Daniel says to everyone, while sharing out the food: "There is only one portion left, but we will split it so no one goes without."; Daniel shares out the last 1 portion between Daniel, Elena, Leo, Mara. **Chose: accuse Daniel of taking it**, saying “You think sharing this makes it better, Daniel, but you're the one who stole from us in the first place.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *resentful*. Reason: “He tries to act like a savior now, but he is the thief who caused all of this.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Leo.

**min 18** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "You think sharing this makes it better, Daniel, but you're the one who stole from us in the first place.". **Chose: reassure Mara**, saying “Mara, I am sorry, I know my sharing doesn't undo what I did.” *(not new: reassurance)* (one of 15 options). Feeling: *deep guilt*. Reason: “I need her to know I am truly sorry for stealing the food.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just spoken to by Daniel). Social moment: Daniel reassures you: "Mara, I am sorry, I know my sharing doesn't undo what I did.". Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 15 options). Feeling: *resentful*. Reason: “I have nothing more to say to Daniel after what he did.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "You think sharing this makes it better, Daniel, but you're the one who stole from us in the first place."; Daniel reassures Mara: "Mara, I am sorry, I know my sharing doesn't undo what I did.". **Chose: reassure Mara**, saying “Mara, please, let it go. We have shared what we have and we must stay united.” *(not new: reassurance)* (one of 15 options). Feeling: *anxious*. Reason: “I need Mara to stop fighting with Daniel so the family doesn't tear itself apart.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while sharing out the food: "There is only one portion left, but we will split it so no one goes without."; Daniel shares out the last 1 portion between Daniel, Elena, Leo, Mara; Mara accuses Daniel of taking it: "You think sharing this makes it better, Daniel, but you're the one who stole from us in the first place."; Daniel reassures Mara: "Mara, I am sorry, I know my sharing doesn't undo what I did."; Elena reassures Mara: "Mara, please, let it go. We have shared what we have and we must stay united.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *cold annoyance*. Reason: “There is nothing left to argue about since the food is gone and his apologies ring hollow.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 2/3. Came of it: stayed where they were.

**min 21** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Elena reassures you: "Mara, please, let it go. We have shared what we have and we must stay united.". **Chose: accuse Daniel of taking it**, saying “You can keep apologizing all you want, Daniel, but sorry doesn't bring back what you stole from us.” *(not new: an accusation they had made before)* (one of 17 options). Feeling: *furious*. Reason: “I cannot just pretend everything is fine when he is the one who put us all in this position.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena reassures Mara: "Mara, please, let it go. We have shared what we have and we must stay united."; Mara accuses you of taking it: "You can keep apologizing all you want, Daniel, but sorry doesn't bring back what you stole from us."; Mara looks furious. **Chose: reassure Mara**, saying “Mara, I know my apology is small, but I am trying to make it right for all of us.” *(not new: reassurance)* (one of 14 options). Feeling: *deep guilt*. Reason: “I have to absorb her anger because I am the one who caused this.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "You can keep apologizing all you want, Daniel, but sorry doesn't bring back what you stole from us."; Daniel reassures Mara: "Mara, I know my apology is small, but I am trying to make it right for all of us."; Mara looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, apologizing after the fact doesn't change the fact that you took what wasn't yours.” *(not new: an accusation they had made before)* (one of 15 options). Feeling: *cold annoyance*. Reason: “I cannot let his empty apologies gloss over the unfairness of what he did to us.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "You can keep apologizing all you want, Daniel, but sorry doesn't bring back what you stole from us."; Daniel reassures Mara: "Mara, I know my apology is small, but I am trying to make it right for all of us."; Leo accuses Daniel of taking it: "Daniel, apologizing after the fact doesn't change the fact that you took what wasn't yours."; Mara looks furious. **Chose: reassure Mara**, saying “Mara, please, let us not fight amongst ourselves when we need to be strong together.” *(not new: reassurance)* (one of 14 options). Feeling: *anxious*. Reason: “I must keep the peace between them before anger tears our family apart.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation ends (minute 24): 2 full turns in a row with nothing new.*

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel, minutes 24–87 (22 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 3 of 3). **Chose: accuse Daniel of taking it**, saying “Daniel, sitting in silence doesn't undo what you did to our supplies.” *(not new: an accusation they had made before)* (one of 15 options). Feeling: *furious*. Reason: “I cannot let him sit there pretending his selfishness is a closed matter.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena, minutes 24–57 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 27** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: accuse Daniel of taking it**, saying “You started all of this, Daniel, and you're just sitting there like none of it matters.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *furious*. Reason: “I cannot stand there and watch him act so calm after everything he has ruined.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo, minutes 27–36 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 30–78 (17 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 39** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 14 options). Feeling: *furious*. Reason: “There is nothing left to say to him after what he pulled.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: stayed where they were.

**min 42** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 42–87 (16 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 60** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 14 options). Feeling: *deeply exhausted*. Reason: “We have already survived the worst of the accusations, and staying quiet is the only way to keep the family from completely fracturing.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 63–87 (9 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 81** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Daniel of taking it**, saying “You're the reason we're all sitting here starving, Daniel, and you don't even care.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *furious*. Reason: “I cannot just sit here quietly while he acts like everything is fine after what he did.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Leo.

**min 84** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 84–87 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Elena reassures everyone: "We are going to be fine, nobody needs to worry. We just need to stay together." *(not new: reassurance)*
- min 00, kitchen. Mara asks everyone who took the can: "Wait, if a can is missing, who actually took it?" *(new: a question)*
- min 03, kitchen. Elena reassures everyone: "Let us not turn on each other. We are all we have right now." *(not new: reassurance)*
- min 03, kitchen. Daniel admits taking it, to everyone: "I took it, I ate it in the night. It was me." *(new: a confession)*
- min 06, kitchen. Elena reassures Daniel: "Thank you for telling us the truth, Daniel. We are going to get through this together." *(not new: reassurance)*
- min 06, kitchen. Daniel reassures everyone: "I am sorry, I should not have done it, but I promise we will figure this out." *(not new: reassurance)*
- min 09, kitchen. Mara accuses Daniel of taking it: "You just said you took it, Daniel, but how can we even believe you now?" *(new: an accusation)*
- min 09, kitchen. Daniel reassures Mara: "Mara, I know I messed up, but you have to believe I am telling you the truth now." *(not new: reassurance)*
- min 12, kitchen. Mara accuses Daniel of taking it: "You keep acting like this makes everything fine, Daniel, but it doesn't fix what you did." *(not new: an accusation they had made before)*
- min 12, kitchen. Daniel says to everyone, while eating: "I need to keep my strength up to protect you all, I am taking this one." *(not new: a remark (the rules cannot tell what free words add))*
- min 12, kitchen. Elena reassures everyone: "Let us calm down. Arguing will only tear us apart when we need each other most." *(not new: reassurance)*
- min 15, kitchen. Leo accuses Daniel of taking it: "You already ate one, Daniel. There is only one left and it is not yours to take." *(new: an accusation)*
- min 15, kitchen. Daniel says to everyone, while sharing out the food: "There is only one portion left, but we will split it so no one goes without." *(not new: a remark (the rules cannot tell what free words add))*
- min 15, kitchen. Mara accuses Daniel of taking it: "You think sharing this makes it better, Daniel, but you're the one who stole from us in the first place." *(not new: an accusation they had made before)*
- min 18, kitchen. Daniel reassures Mara: "Mara, I am sorry, I know my sharing doesn't undo what I did." *(not new: reassurance)*
- min 18, kitchen. Elena reassures Mara: "Mara, please, let it go. We have shared what we have and we must stay united." *(not new: reassurance)*
- min 21, kitchen. Mara accuses Daniel of taking it: "You can keep apologizing all you want, Daniel, but sorry doesn't bring back what you stole from us." *(not new: an accusation they had made before)*
- min 21, kitchen. Daniel reassures Mara: "Mara, I know my apology is small, but I am trying to make it right for all of us." *(not new: reassurance)*
- min 21, kitchen. Leo accuses Daniel of taking it: "Daniel, apologizing after the fact doesn't change the fact that you took what wasn't yours." *(not new: an accusation they had made before)*
- min 21, kitchen. Elena reassures Mara: "Mara, please, let us not fight amongst ourselves when we need to be strong together." *(not new: reassurance)*
- min 24, kitchen. Leo accuses Daniel of taking it: "Daniel, sitting in silence doesn't undo what you did to our supplies." *(not new: an accusation they had made before)*
- min 27, kitchen. Mara accuses Daniel of taking it: "You started all of this, Daniel, and you're just sitting there like none of it matters." *(not new: an accusation they had made before)*
- min 81, kitchen. Mara accuses Daniel of taking it: "You're the reason we're all sitting here starving, Daniel, and you don't even care." *(not new: an accusation they had made before)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Daniel 1.25, Elena 0.25, Leo 0.25, Mara 0.25.

- Who admitted taking it: Daniel at minute 03.
- Accusations: Mara accused Daniel (minute 09); Mara accused Daniel (minute 12); Leo accused Daniel (minute 15); Mara accused Daniel (minute 15); Mara accused Daniel (minute 21); Leo accused Daniel (minute 21); Leo accused Daniel (minute 24); Mara accused Daniel (minute 27); Mara accused Daniel (minute 81).
- Who else knows Daniel took it: Elena, Leo, Mara.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 24 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects Daniel 3/3 | suspects Daniel 3/3 | suspects Daniel 3/3 |
| Grudge | against none | against none | against Daniel 3/3 | against Daniel 3/3 |
| Hunger | a little hungry | very hungry | very hungry | very hungry |
| Guilt | 3/3 (The guilt over what you did in the night is crushing you.) | - | - | - |

- The last feeling each of them named: Daniel *deep guilt* (minute 21); Elena *deeply exhausted* (minute 60); Leo *furious* (minute 39); Mara *furious* (minute 81).


### The morning as a story: daniel_ate_it, rules and a language model, seed 2

Generated by `python morning.py --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 36 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 84 routine ones settled by the rules. 19 lines were spoken aloud, 2 of them new. Conversations ended 3 times. 10 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can) and a grudge (who they are angry with), each a person and a strength from 0 to 3; and for Daniel, guilt from 0 to 3. The model is shown them in words.
- **Suspects / Angry at**: every model answer names who they now believe took the can and who they are angry with, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Daniel's guilt** rises a step each time he denies or accuses someone, each time he hears someone else accused, and each time someone reassures him or everyone. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

#### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

##### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

#### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “A can is missing from the shelf. Did one of you take it?” *(new: a question)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to know what happened to our food before this breaks us apart.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?". **Chose: deny taking it**, saying “I didn't take it, why are you looking at me like that?” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *anxious*. Reason: “I am innocent and terrified they think I did it.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, why are you looking at me like that?". **Chose: deny taking it**, saying “I didn't take the can, nobody here did this.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I cannot admit I ate it in the dark or I will lose their respect entirely.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, why are you looking at me like that?"; Daniel denies taking it, to everyone: "I didn't take the can, nobody here did this.". **Chose: deny taking it**, saying “I didn't take it either. Let's not accuse each other before we think.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *calm*. Reason: “I need to deny it clearly so no one wastes energy blaming me, while keeping things level.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Mara.
- *Daniel's guilt rises to 1 of 3: he denied taking it.*
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, why are you looking at me like that?"; Daniel denies taking it, to everyone: "I didn't take the can, nobody here did this."; Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we think.". **Chose: reassure everyone here**, saying “Let's not tear ourselves apart over this. We will get through it together.” *(not new: reassurance)* (one of 23 options). Feeling: *deeply anxious*. Reason: “I must keep the family calm and prevent accusations from tearing us apart.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's not tear ourselves apart over this. We will get through it together.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calm*. Reason: “There is no point in arguing further when no one has any proof.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take the can, nobody here did this."; Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we think."; Elena reassures everyone: "Let's not tear ourselves apart over this. We will get through it together.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “I am too overwhelmed to say anything right now while everyone is staring.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we think."; Elena reassures everyone: "Let's not tear ourselves apart over this. We will get through it together.". **Chose: admit taking it**, saying “I took the can in the night, I'm the one who ate it.” *(new: a confession)* (one of 20 options). Feeling: *deeply guilty*. Reason: “I cannot lie anymore while my family tears themselves apart over my secret.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- *Daniel's guilt rises to 2 of 3: Elena reassured everyone.*

**min 06** · kitchen: Daniel staying put, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel admits taking it, to everyone: "I took the can in the night, I'm the one who ate it.". **Chose: reassure Daniel**, saying “It is okay, Daniel, I am just glad you said something.” *(not new: reassurance)* (one of 18 options). Feeling: *relieved*. Reason: “I want Daniel to know I am not mad at him for eating.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel admits taking it, to everyone: "I took the can in the night, I'm the one who ate it."; Mara reassures Daniel: "It is okay, Daniel, I am just glad you said something.". **Chose: reassure Daniel**, saying “Thank you for being honest, Daniel. We are going to be fine.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply anxious*. Reason: “I need to keep him from feeling completely isolated after admitting what he did.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel admits taking it, to everyone: "I took the can in the night, I'm the one who ate it."; Mara reassures Daniel: "It is okay, Daniel, I am just glad you said something."; Elena reassures Daniel: "Thank you for being honest, Daniel. We are going to be fine.". **Chose: reassure Daniel**, saying “It takes courage to admit it, Daniel. We are all still standing.” *(not new: reassurance)* (one of 16 options). Feeling: *relieved*. Reason: “Daniel admitted to taking the can and honesty is what matters most for keeping us together.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Mara.
- *Daniel's guilt rises to 3 of 3: Mara reassured him.*

**min 09** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just spoken to by Leo). Social moment: Mara reassures you: "It is okay, Daniel, I am just glad you said something."; Elena reassures you: "Thank you for being honest, Daniel. We are going to be fine."; Leo reassures you: "It takes courage to admit it, Daniel. We are all still standing.". **Chose: reassure everyone here**, saying “Thank you for understanding me, we will get through this together.” *(not new: reassurance)* (one of 17 options). Feeling: *guilty*. Reason: “I need to reassure everyone that I am sorry and we will get through this despite my shameful mistake.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures Daniel: "Thank you for being honest, Daniel. We are going to be fine."; Leo reassures Daniel: "It takes courage to admit it, Daniel. We are all still standing."; Daniel reassures everyone: "Thank you for understanding me, we will get through this together.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *anxious*. Reason: “I have already said what I needed to, so I will just stay quiet while everyone sorts this out.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Thank you for understanding me, we will get through this together.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *calm*. Reason: “There is nothing more that needs to be said right now after everything has been brought to light.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures Daniel: "It takes courage to admit it, Daniel. We are all still standing."; Daniel reassures everyone: "Thank you for understanding me, we will get through this together.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *deeply anxious*. Reason: “I need to keep the peace and let us settle down after the confession.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 12): 2 full turns in a row with nothing new.*

**min 12** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 12–33 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3). **Chose: stay put and say nothing** (one of 18 options). Feeling: *calm*. Reason: “Since Daniel already confessed and we are settling down, there is no need to push further right now.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Daniel, minutes 12–30 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3). **Chose: stay put and say nothing** (one of 16 options). Feeling: *deeply anxious*. Reason: “I need to keep the peace and let the tension settle before I speak again.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 15–18 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 15–18 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 21** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry); suspicion of Daniel rose (now 3 of 3). **Chose: stay put and say nothing** (one of 19 options). Feeling: *hungry*. Reason: “There is nothing more to discuss right now while we wait.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3). **Chose: stay put and say nothing** (one of 17 options). Feeling: *deeply anxious*. Reason: “I cannot bring myself to speak while the tension hangs so heavy between us all.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 24–33 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “We are still a family, and we will get through this hunger together.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and united while our food runs low.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel eating, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: eat one of the portions**, saying “I need to eat this portion now, my stomach is burning.” *(not new: a remark (the rules cannot tell what free words add))* (one of 14 options). Feeling: *starving*. Reason: “I am terribly hungry and the guilt won't stop unless I keep my strength up.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: ate a portion; 1 left. New in the room: Daniel ate one of the portions.
- *The kitchen's conversation starts (minute 33): Daniel ate one of the portions.*

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel says to everyone, while eating: "I need to eat this portion now, my stomach is burning."; Daniel eats one of the portions. **Chose: stay put and say nothing** (one of 19 options). Feeling: *anxious*. Reason: “I am too hungry and overwhelmed to speak right now, so I will just stay quiet.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Daniel, minutes 36–54 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel says to everyone, while eating: "I need to eat this portion now, my stomach is burning."; Daniel eats one of the portions. **Chose: stay put and say nothing** (one of 17 options). Feeling: *hungry*. Reason: “There is nothing new that needs saying right now.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while eating: "I need to eat this portion now, my stomach is burning."; Daniel eats one of the portions. **Chose: stay put and say nothing** (one of 16 options). Feeling: *deeply anxious*. Reason: “I cannot bring myself to speak while the hunger gnaws at us and the remaining food sits right there on the shelf.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 39** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 39–51 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 39–54 (6 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 39–51 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 42): 2 full turns in a row with nothing new.*

**min 54** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara eating · nobody in brothers room, back room, bathroom
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: eat one of the portions**, saying “I am so hungry, I have to eat this.” *(not new: a remark (the rules cannot tell what free words add))* (one of 17 options). Feeling: *starving*. Reason: “My stomach is burning from hunger and I need to eat the last portion.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: ate a portion; 0 left. New in the room: Mara ate one of the portions.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while eating: "I am so hungry, I have to eat this."; Mara eats one of the portions. **Chose: reassure Mara**, saying “Eat slowly, Mara, we will find a way through this.” *(not new: reassurance)* (one of 14 options). Feeling: *deeply anxious*. Reason: “She is so young and hungry, I must make sure she knows she is safe.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation starts (minute 54): Mara ate one of the portions.*

**min 57** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara leaving for the back room · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Elena reassures you: "Eat slowly, Mara, we will find a way through this.". **Chose: go to the back room** (one of 17 options). Feeling: *exhausted*. Reason: “I just need to go lie down in the back room for a little while.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: went to the back room.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while eating: "I am so hungry, I have to eat this."; Mara eats one of the portions; Elena reassures Mara: "Eat slowly, Mara, we will find a way through this.". **Chose: reassure Elena**, saying “Don't worry, Mom, I'm going to figure out how we get more food.” *(not new: reassurance)* (one of 12 options). Feeling: *anxious*. Reason: “I need to comfort Mom and show her I am taking charge of our situation.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo.
- **Elena** (3rd to act in the kitchen: just spoken to by Daniel). Social moment: Daniel reassures you: "Don't worry, Mom, I'm going to figure out how we get more food.". **Chose: reassure Daniel**, saying “Thank you, Daniel, just be careful and stay close to home.” *(not new: reassurance)* (one of 13 options). Feeling: *deeply anxious*. Reason: “I want to comfort Daniel and keep him from doing anything reckless outside.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while eating: "I am so hungry, I have to eat this."; Mara eats one of the portions; Elena reassures Mara: "Eat slowly, Mara, we will find a way through this."; Daniel reassures Elena: "Don't worry, Mom, I'm going to figure out how we get more food."; Elena reassures Daniel: "Thank you, Daniel, just be careful and stay close to home.". **Chose: stay put and say nothing** (one of 12 options). Feeling: *hungry*. Reason: “There is nothing more to argue about now that the food is completely gone.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 60** · kitchen: Daniel talking, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Daniel** (1st to act in the kitchen: just spoken to by Elena). Social moment: Elena reassures you: "Thank you, Daniel, just be careful and stay close to home.". **Chose: reassure Elena**, saying “Mom, please don't worry, I'll take care of everything we need.” *(not new: reassurance)* (one of 12 options). Feeling: *anxious*. Reason: “I need to keep Mom calm even though my guilt is crushing me.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo.
- **Elena** (2nd to act in the kitchen: just spoken to by Daniel). Social moment: Daniel reassures you: "Mom, please don't worry, I'll take care of everything we need.". **Chose: stay put and say nothing** (one of 13 options). Feeling: *deeply anxious*. Reason: “I cannot keep reassuring him when there is nothing left and we are all starving.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: the only one left to act here). Social moment: Daniel reassures Elena: "Mom, please don't worry, I'll take care of everything we need.". **Chose: stay put and say nothing** (one of 12 options). Feeling: *hungry*. Reason: “There is nothing more to add while we have no food left.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara, minutes 60–87 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 63): 2 full turns in a row with nothing new.*

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Elena, minutes 63–72 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 13 options). Feeling: *very hungry*. Reason: “There is nothing left to say right now, and my empty stomach demands focus.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Daniel, minutes 63–75 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 66** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Elena** (3rd to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “We are still together, and we will find a way through this hunger.” *(not new: reassurance)* (one of 12 options). Feeling: *starving*. Reason: “I must keep the family together and calm despite our empty stomachs.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo.

**min 78** · kitchen: Daniel talking, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: reassure Elena**, saying “Mom, I promise you I will keep everyone safe.” *(not new: reassurance)* (one of 11 options). Feeling: *anxious*. Reason: “I need to reassure Mom so she knows I am in control and everything will be fine.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo.
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 81** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Daniel, minutes 81–87 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, why are you looking at me like that?" *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Daniel denies taking it, to everyone: "I didn't take the can, nobody here did this." *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we think." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "Let's not tear ourselves apart over this. We will get through it together." *(not new: reassurance)*
- min 03, kitchen. Daniel admits taking it, to everyone: "I took the can in the night, I'm the one who ate it." *(new: a confession)*
- min 06, kitchen. Mara reassures Daniel: "It is okay, Daniel, I am just glad you said something." *(not new: reassurance)*
- min 06, kitchen. Elena reassures Daniel: "Thank you for being honest, Daniel. We are going to be fine." *(not new: reassurance)*
- min 06, kitchen. Leo reassures Daniel: "It takes courage to admit it, Daniel. We are all still standing." *(not new: reassurance)*
- min 09, kitchen. Daniel reassures everyone: "Thank you for understanding me, we will get through this together." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "We are still a family, and we will get through this hunger together." *(not new: reassurance)*
- min 33, kitchen. Daniel says to everyone, while eating: "I need to eat this portion now, my stomach is burning." *(not new: a remark (the rules cannot tell what free words add))*
- min 54, kitchen. Mara says to everyone, while eating: "I am so hungry, I have to eat this." *(not new: a remark (the rules cannot tell what free words add))*
- min 54, kitchen. Elena reassures Mara: "Eat slowly, Mara, we will find a way through this." *(not new: reassurance)*
- min 57, kitchen. Daniel reassures Elena: "Don't worry, Mom, I'm going to figure out how we get more food." *(not new: reassurance)*
- min 57, kitchen. Elena reassures Daniel: "Thank you, Daniel, just be careful and stay close to home." *(not new: reassurance)*
- min 60, kitchen. Daniel reassures Elena: "Mom, please don't worry, I'll take care of everything we need." *(not new: reassurance)*
- min 75, kitchen. Elena reassures everyone: "We are still together, and we will find a way through this hunger." *(not new: reassurance)*
- min 78, kitchen. Daniel reassures Elena: "Mom, I promise you I will keep everyone safe." *(not new: reassurance)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo; back room: Mara. 0 of 2 portions left; eaten this morning: Daniel 1, Mara 1.

- Who admitted taking it: Daniel at minute 03.
- Accusations: none.
- Who else knows Daniel took it: Elena, Leo, Mara.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 12 (2 full turns in a row with nothing new); kitchen started at minute 33 (Daniel ate one of the portions); kitchen ended at minute 42 (2 full turns in a row with nothing new); kitchen started at minute 54 (Mara ate one of the portions); kitchen ended at minute 63 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects Daniel 3/3 | suspects Daniel 3/3 | suspects none |
| Grudge | against none | against none | against none | against none |
| Hunger | hungry | starving | very hungry | a little hungry |
| Guilt | 3/3 (The guilt over what you did in the night is crushing you.) | - | - | - |

- The last feeling each of them named: Daniel *anxious* (minute 78); Elena *starving* (minute 75); Leo *very hungry* (minute 63); Mara *exhausted* (minute 57).


### The morning as a story: daniel_ate_it, rules and a language model, seed 3

Generated by `python morning.py --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 30 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 90 routine ones settled by the rules. 21 lines were spoken aloud, 4 of them new. Conversations ended 1 time. 8 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can) and a grudge (who they are angry with), each a person and a strength from 0 to 3; and for Daniel, guilt from 0 to 3. The model is shown them in words.
- **Suspects / Angry at**: every model answer names who they now believe took the can and who they are angry with, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Daniel's guilt** rises a step each time he denies or accuses someone, each time he hears someone else accused, and each time someone reassures him or everyone. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

#### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

##### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

#### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Someone tell me who took it, please. We have to be honest with each other.” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know what happened so we don't start fighting in the dark.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "Someone tell me who took it, please. We have to be honest with each other.". **Chose: reassure everyone here**, saying “Nobody here would take food from the others, I am quite sure of it.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I must keep the peace before this tension tears us all apart.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "Someone tell me who took it, please. We have to be honest with each other."; Elena reassures everyone: "Nobody here would take food from the others, I am quite sure of it.". **Chose: deny taking it**, saying “I didn't take it, and none of us would do that.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *guilty*. Reason: “I cannot admit I ate the can in the dark without losing their respect completely.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "Someone tell me who took it, please. We have to be honest with each other."; Elena reassures everyone: "Nobody here would take food from the others, I am quite sure of it."; Daniel denies taking it, to everyone: "I didn't take it, and none of us would do that.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “There is no point in arguing until we actually look for the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- *Daniel's guilt rises to 1 of 3: Elena reassured everyone.*
- *Daniel's guilt rises to 2 of 3: he denied taking it.*
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take it, and none of us would do that.". **Chose: reassure everyone here**, saying “We must not turn on each other, we will get through this together.” *(not new: reassurance)* (one of 23 options). Feeling: *deeply anxious*. Reason: “I need to keep the peace and prevent everyone from falling apart.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Nobody here would take food from the others, I am quite sure of it."; Daniel denies taking it, to everyone: "I didn't take it, and none of us would do that."; Elena reassures everyone: "We must not turn on each other, we will get through this together.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I do not want to accuse anyone when I don't know the truth.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We must not turn on each other, we will get through this together.". **Chose: admit taking it**, saying “I took the can in the night. I am sorry, I couldn't help myself.” *(new: a confession)* (one of 21 options). Feeling: *guilty*. Reason: “The weight of my lie is too much to bear while everyone trusts me.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "We must not turn on each other, we will get through this together."; Daniel admits taking it, to everyone: "I took the can in the night. I am sorry, I couldn't help myself.". **Chose: reassure Daniel**, saying “It's alright, Daniel. We all reach our limit sometimes.” *(not new: reassurance)* (one of 16 options). Feeling: *calm*. Reason: “Daniel is admitting a mistake and apologizing, so he needs understanding rather than anger.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Elena, Mara.
- *Daniel's guilt rises to 3 of 3: Elena reassured everyone.*

**min 06** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just spoken to by Leo). Social moment: Leo reassures you: "It's alright, Daniel. We all reach our limit sometimes.". **Chose: reassure everyone here**, saying “We are going to be fine, I will make sure we get through this.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply guilty*. Reason: “I need to fix what I broke and keep my family from falling apart.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "We are going to be fine, I will make sure we get through this.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *calm*. Reason: “Since he already admitted it and apologized, there is no need to keep talking about the food right now.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel admits taking it, to everyone: "I took the can in the night. I am sorry, I couldn't help myself."; Leo reassures Daniel: "It's alright, Daniel. We all reach our limit sometimes."; Daniel reassures everyone: "We are going to be fine, I will make sure we get through this.". **Chose: accuse Daniel of taking it**, saying “Daniel, you just said you took it, how can you pretend everything is fine now?” *(new: an accusation)* (one of 17 options). Feeling: *confused*. Reason: “I need to know what is real when he keeps changing his story.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel, so grudge Daniel 1/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel admits taking it, to everyone: "I took the can in the night. I am sorry, I couldn't help myself."; Leo reassures Daniel: "It's alright, Daniel. We all reach our limit sometimes."; Daniel reassures everyone: "We are going to be fine, I will make sure we get through this."; Mara accuses Daniel of taking it: "Daniel, you just said you took it, how can you pretend everything is fine now?". **Chose: reassure everyone here**, saying “Let us focus on what matters and support each other through this.” *(not new: reassurance)* (one of 16 options). Feeling: *anxious*. Reason: “I need to keep the family together and prevent any more fighting.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 09** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, you just said you took it, how can you pretend everything is fine now?"; Elena reassures everyone: "Let us focus on what matters and support each other through this.". **Chose: reassure Mara**, saying “Mara, I know I messed up, but I promise I will make it right for all of us.” *(not new: reassurance)* (one of 17 options). Feeling: *guilty*. Reason: “I need to make sure my little sister knows I am truly sorry and she can trust me.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just spoken to by Daniel). Social moment: Elena reassures everyone: "Let us focus on what matters and support each other through this."; Daniel reassures you: "Mara, I know I messed up, but I promise I will make it right for all of us.". **Chose: accuse Daniel of taking it**, saying “Daniel, your promises don't bring the food back when you're the one who stole it.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *resentful*. Reason: “I am sick of Daniel acting like everything is fine after he already admitted to taking the food.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel, so grudge Daniel 2/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel, you just said you took it, how can you pretend everything is fine now?"; Elena reassures everyone: "Let us focus on what matters and support each other through this."; Daniel reassures Mara: "Mara, I know I messed up, but I promise I will make it right for all of us."; Mara accuses Daniel of taking it: "Daniel, your promises don't bring the food back when you're the one who stole it.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *calm*. Reason: “There is no need to add to the noise when Daniel already confessed and Mara is sorting it out.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures Mara: "Mara, I know I messed up, but I promise I will make it right for all of us."; Mara accuses Daniel of taking it: "Daniel, your promises don't bring the food back when you're the one who stole it.". Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: accuse Daniel of taking it**, saying “Daniel, you took the can and you have to own up to what you did.” *(new: an accusation)* (one of 12 options). Feeling: *deeply anxious*. Reason: “I need to address the truth so the family does not tear itself apart over lies.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 12** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Elena). Social moment: Mara accuses you of taking it: "Daniel, your promises don't bring the food back when you're the one who stole it."; Elena accuses you of taking it: "Daniel, you took the can and you have to own up to what you did.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *deep guilt*. Reason: “I cannot keep pretending everything is fine when I am the one who destroyed our trust.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena accuses Daniel of taking it: "Daniel, you took the can and you have to own up to what you did.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *calm*. Reason: “There is no need to keep arguing when Daniel already admitted it and we are trying to stay steady.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena accuses Daniel of taking it: "Daniel, you took the can and you have to own up to what you did.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *bitter silence*. Reason: “I have said enough and nobody cares that we are starving.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3). **Chose: reassure everyone here**, saying “We are still a family and we cannot let hunger tear us apart now.” *(not new: reassurance)* (one of 16 options). Feeling: *anxious*. Reason: “I must keep everyone calm and prevent the family from breaking down completely.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 15** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena, minutes 15–18 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We are still a family and we cannot let hunger tear us apart now.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who took it and you need to admit it right now.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *furious*. Reason: “I cannot stay quiet while he acts like nothing happened.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: just accused by Mara). Social moment: Elena reassures everyone: "We are still a family and we cannot let hunger tear us apart now."; Mara accuses you of taking it: "Daniel, you're the one who took it and you need to admit it right now."; Mara looks furious. **Chose: reassure Mara**, saying “Mara, please listen to me, I am going to fix this for us.” *(not new: reassurance)* (one of 15 options). Feeling: *guilty*. Reason: “I need to calm her down and take responsibility for my actions.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "We are still a family and we cannot let hunger tear us apart now."; Mara accuses Daniel of taking it: "Daniel, you're the one who took it and you need to admit it right now."; Daniel reassures Mara: "Mara, please listen to me, I am going to fix this for us."; Mara looks furious. **Chose: stay put and say nothing** (one of 16 options). Feeling: *calm*. Reason: “Daniel already confessed, so arguing further serves no purpose.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 18): 2 full turns in a row with nothing new.*

**min 18** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 18–51 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 18–60 (15 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 18–30 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 21** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3). **Chose: reassure everyone here**, saying “We must stay calm and not let anger divide us further.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to keep the peace between them before things escalate.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “We must stay calm and not let hunger divide us further.” *(not new: reassurance)* (one of 18 options). Feeling: *very anxious*. Reason: “I need to keep the family together and prevent any more fighting.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Mom, Leo, Mara, we will figure this out together and I will keep us safe.” *(not new: reassurance)* (one of 16 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and prove I am still the one looking after them.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who stole it and pretending you didn't doesn't change anything.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *furious*. Reason: “I cannot stand there silently while he acts like he didn't ruin everything for us.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel, so grudge Daniel 3/3. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 16 options). Feeling: *hungry*. Reason: “There is nothing left to argue about since Daniel already confessed.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure Mara**, saying “Mara, I know you are angry at me for what happened, but I swear I will make it up to you.” *(not new: reassurance)* (one of 15 options). Feeling: *guilty*. Reason: “I have to face the truth she threw at me and reassure my sister that I am truly sorry.” Suspects: nobody, so suspicion none. Angry at: nobody, so grudge none. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “We must stay calm and keep together through this.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to keep the peace between them before hunger tears us apart.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody, so grudge none. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Mara asks everyone who took the can: "Someone tell me who took it, please. We have to be honest with each other." *(new: a question)*
- min 00, kitchen. Elena reassures everyone: "Nobody here would take food from the others, I am quite sure of it." *(not new: reassurance)*
- min 00, kitchen. Daniel denies taking it, to everyone: "I didn't take it, and none of us would do that." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "We must not turn on each other, we will get through this together." *(not new: reassurance)*
- min 03, kitchen. Daniel admits taking it, to everyone: "I took the can in the night. I am sorry, I couldn't help myself." *(new: a confession)*
- min 03, kitchen. Leo reassures Daniel: "It's alright, Daniel. We all reach our limit sometimes." *(not new: reassurance)*
- min 06, kitchen. Daniel reassures everyone: "We are going to be fine, I will make sure we get through this." *(not new: reassurance)*
- min 06, kitchen. Mara accuses Daniel of taking it: "Daniel, you just said you took it, how can you pretend everything is fine now?" *(new: an accusation)*
- min 06, kitchen. Elena reassures everyone: "Let us focus on what matters and support each other through this." *(not new: reassurance)*
- min 09, kitchen. Daniel reassures Mara: "Mara, I know I messed up, but I promise I will make it right for all of us." *(not new: reassurance)*
- min 09, kitchen. Mara accuses Daniel of taking it: "Daniel, your promises don't bring the food back when you're the one who stole it." *(not new: an accusation they had made before)*
- min 09, kitchen. Elena accuses Daniel of taking it: "Daniel, you took the can and you have to own up to what you did." *(new: an accusation)*
- min 12, kitchen. Elena reassures everyone: "We are still a family and we cannot let hunger tear us apart now." *(not new: reassurance)*
- min 15, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who took it and you need to admit it right now." *(not new: an accusation they had made before)*
- min 15, kitchen. Daniel reassures Mara: "Mara, please listen to me, I am going to fix this for us." *(not new: reassurance)*
- min 21, kitchen. Elena reassures everyone: "We must stay calm and not let anger divide us further." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "We must stay calm and not let hunger divide us further." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "Mom, Leo, Mara, we will figure this out together and I will keep us safe." *(not new: reassurance)*
- min 54, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who stole it and pretending you didn't doesn't change anything." *(not new: an accusation they had made before)*
- min 66, kitchen. Daniel reassures Mara: "Mara, I know you are angry at me for what happened, but I swear I will make it up to you." *(not new: reassurance)*
- min 75, kitchen. Elena reassures everyone: "We must stay calm and keep together through this." *(not new: reassurance)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: Daniel at minute 03.
- Accusations: Mara accused Daniel (minute 06); Mara accused Daniel (minute 09); Elena accused Daniel (minute 09); Mara accused Daniel (minute 15); Mara accused Daniel (minute 54).
- Who else knows Daniel took it: Elena, Leo, Mara.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 18 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects Daniel 3/3 | suspects Daniel 3/3 | suspects Daniel 3/3 |
| Grudge | against none | against none | against none | against Daniel 3/3 |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 3/3 (The guilt over what you did in the night is crushing you.) | - | - | - |

- The last feeling each of them named: Daniel *guilty* (minute 66); Elena *anxious* (minute 75); Leo *hungry* (minute 63); Mara *furious* (minute 54).

