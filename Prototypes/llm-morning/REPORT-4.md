# LLM morning prototype, step 4: guilt and grudges from events

Guilt and grudges now come from events the rules see: who accused whom falsely, who admitted it after denying it, who ate in front of someone hungry. The prompt shows them as those events, in plain dated lines, with at most *a little*, *some* or *a lot*. The old verdicts ("is crushing you", "weighs on you heavily", "You are furious with...") are gone. Daniel's guilt starts at 1 and rises only when someone else is accused of what he did in his hearing, or when someone reassures him personally. Nobody is offered *reassure* toward someone they hold a grudge of 3 against. Five fresh mornings, seeds 1 to 5. The earlier reports and runs are left as they were; this step's runs are in `runs/v4/`. Model: `gemini-3.5-flash-lite`, unchanged.

## Done when

| Condition | Result |
|---|---|
| all tests pass | 43 of 43, against the fake model and a stubbed API |
| 5 fresh mornings under 150 real calls each | 36, 39, 39, 29, 41 model calls (seeds 1 to 5); all reached minute 90 |
| `--replay` of seed 1 byte-identical with 0 calls | IDENTICAL, 0 API requests, run with `GEMINI_API_KEY` unset; `cmp` and SHA-256 agree |
| REPORT-4.md has the metrics table for the v3 runs and the new ones | below |

## Metrics

| Run | Model calls | Lines spoken | Daniel confessed | From his confession to the first reassurance of him, for each person he lied to or accused | Lines that are reassurance | Longest stretch with no model decision (minutes) |
|---|---|---|---|---|---|---|
| v3, seed 1 | 37 | 23 | min 03 | he lied to and accused nobody | 10/23 (43%) | 18 (min 42–60) |
| v3, seed 2 | 36 | 19 | min 03 | Elena (lied to): 3 min; Leo (lied to): 3 min; Mara (lied to): 3 min | 12/19 (63%) | 15 (min 39–54) |
| v3, seed 3 | 30 | 21 | min 03 | Elena (lied to): never; Leo (lied to): 0 min; Mara (lied to): never | 13/21 (62%) | 18 (min 36–54) |
| v4, seed 1 | 36 | 24 | never | no confession | 12/24 (50%) | 18 (min 36–54) |
| v4, seed 2 | 39 | 26 | never | no confession | 8/26 (31%) | 24 (min 57–81) |
| v4, seed 3 | 39 | 25 | never | no confession | 5/25 (20%) | 18 (min 36–54) |
| v4, seed 4 | 29 | 18 | min 06 | he lied to and accused nobody | 8/18 (44%) | 18 (min 36–54) |
| v4, seed 5 | 41 | 26 | never | no confession | 8/26 (31%) | 12 (min 42–54) |

`metrics4.py` computes the table from the runs' transcripts, the same way for v3 (three seeds) and v4 (five).

- **Model calls**: decisions the model made, take-aside replies included. It equals the API requests except where a run was split by the daily quota (see the seed 2 output).
- **Daniel confessed**: the minute he chose to admit it.
- **From his confession to the first reassurance of him**: counts everyone who heard him deny it (*lied to*) or whom he accused. For each, the minutes until they first reassured Daniel himself (the option *reassure Daniel*, not reassuring everyone). *never* if they did not by minute 90.
- **Lines that are reassurance**: lines whose act was reassuring someone or everyone, out of all lines spoken.
- **Longest stretch with no model decision**: the longest run of 3-minute turns in which the model decided nothing for anyone.

### Grudges at minute 90, with the events behind them

In v4 these are the events the rules recorded, as the holder's prompt says them ("you" is the one holding the grudge). In v3 a grudge came only from naming someone in `angry_at`.

```
Grudges at minute 90, with the events behind them (in the holder's own terms: "you" is the one holding the grudge):

v3, seed 1:
- Leo against Daniel, 3/3: named Daniel as who they were angry with at minutes 15, 18, 21, 24, 39.
- Mara against Daniel, 3/3: named Daniel as who they were angry with at minutes 09, 12, 15, 18, 21, 27, 81.

v3, seed 2:
- nobody holds a grudge

v3, seed 3:
- Mara against Daniel, 3/3: named Daniel as who they were angry with at minutes 06, 09, 12, 15, 54.

v4, seed 1:
- nobody holds a grudge

v4, seed 2:
- nobody holds a grudge

v4, seed 3:
- nobody holds a grudge

v4, seed 4:
- Leo against Daniel, 3/3: named Daniel as who they were angry with at minutes 09, 12, 15, 18, 63.
- Mara against Daniel, 3/3: named Daniel as who they were angry with at minutes 06, 09, 12, 15, 54.

v4, seed 5:
- Leo against Daniel, 3/3: Daniel accused you of taking the can at minute 09, and you had not; named Daniel as who they were angry with at minutes 12, 15, 18, 24, 36, 63.
```

## What stands out

These are observations; the judge is a person reading the stories below.

- **The minute-3 confession is gone, but only one confession is left.** Daniel confessed in 1 of 5 runs, against 3 of 3 at minute 3 in v3. In seed 4 he said nothing at minutes 0 and 3, then admitted it at minute 6, before telling any lie. At that point his prompt held one fact about it: "On your conscience (a little): you ate the can in the night, and nobody saw." In the other four runs he never confessed and denied it 3, 5, 9 and 5 times.
- **What replaced it is mostly a stalemate.** In seeds 1, 2 and 3 nobody named a suspect all morning, and in seed 5 only Daniel did (Leo, once). The only accusation in those four runs is Daniel's false one against Leo in seed 5. Instead:
  - Mara asks who took it 5 to 7 times in seeds 1, 3 and 5.
  - Daniel denies it again each time. In seed 3 he gives 9 denials, most of them some form of "I told you to drop it".
  - The 3-in-a-row limit only stops this on consecutive turns, so it comes back every few turns for an hour. That is close to the target's Never item "A person repeats the same kind of line many turns in a row with no effect".
- **The events the new rules turn into guilt and grudges seldom happened.**
  - Guilt stayed at 1 in seeds 1 to 3. It reached 2 only in seed 4, when Elena reassured him after his confession, and in seed 5, when he accused Leo. It never caused an inner moment; hunger caused nearly all of them.
  - Only one grudge came from an event: in seed 5 Daniel falsely accused Leo at minute 9 (1 of 3). Leo's own `angry_at` then took it to 3, where it stayed.
  - Nobody confessed after lying, so the confession grudges never fired.
  - Nobody ate in front of anyone. Leo shared the food out in seeds 2 and 3, which raises nothing, though in seed 3 Mara protests ("How can you all just eat and pretend nothing happened").
- **Seed 4, the one confession:**
  - Elena reassured Daniel at once, but he had not lied to her or accused her, so the metric counts nobody.
  - Mara and Leo accused him again after it. Their `angry_at` reached 3 of 3 against him by minute 15, so from then on the rules no longer offered them *reassure Daniel*, and neither reassured him all morning.
  - At minutes 54 and 63 they still hold it against him: "you stole from us"; "Daniel already admitted to taking the food".
  - In v3 seed 2, by contrast, all three forgave him within three minutes.
- **Grudges at minute 90**: none in seeds 1, 2 and 3, because nothing happened that could cause one. In seed 4, Leo and Mara against Daniel (3 of 3, from `angry_at`). In seed 5, Leo against Daniel (3 of 3, from the false accusation and `angry_at`).
- **Less reassurance.** 20% to 50% of lines, against 43% to 63% in v3. The longest stretch with no model decision is 12 to 24 minutes, about as before, usually around minutes 36 to 54, before hunger crosses a level.
- **No private talks again.** Take-aside is unchanged.

Nothing here was tuned after the runs. Two things stand out for the next step, and both are yours to choose:
- The model rarely accuses anyone on its own. So the event-driven guilt and grudges have little to feed on, and Daniel's lie meets no pressure except repeated questions.
- A question asked six or seven times is never answered. No rule turns the unanswered question itself into pressure.

## Changes beyond the brief, and why

- **Interpretations the brief left open:**
  - *Someone else accused of what he did, in his hearing* includes Daniel accusing someone himself: he hears it, and someone else is blamed for what he did. It counts once.
  - The guilt counter stops at 3. Events after that are still recorded and shown as facts.
  - Grudges are kept toward each person separately, so one person can hold several.
  - *A grudge still falls at most one step per 15 minutes*: the 15 minutes count from the grudge's last change, a rise or a fall. The v3 rule counted only from the last fall, which would let a grudge an event had just raised drop on the holder's very next answer. A grudge falls only on an answer of the holder's that does not name that person.
  - *Falsely accuses you*: each accusation of someone who had not taken it, when they are in the room to hear it. Every such accusation is a step.
  - *Denying it to you*: you heard them deny it in the same room. *Had accused you*: they accused you in your hearing.
  - *While you are hungry*: *hungry* or more (hunger 0.5 and up). A share-out raises nothing.
  - Suspicion keeps the v3 rules, which the brief did not change. It is now shown as the minutes they named their suspect, with a level word.
  - Level words: 1 *a little*, 2 *some*, 3 *a lot*. At 0 a prompt says "Against the others: nothing." and "About the can: you have not settled on who took it."
  - To stay within the token budget, a prompt shows the 4 most recent events per grudge and for guilt, with repeated `angry_at` naming folded into one line. The story shows them all.
  - "Since you last decided" now covers only hunger; everything else is a dated fact.
- **`v3/` is a frozen copy of the third version**, and `v3/check.py` confirms it replays the three v3 runs exactly. This step writes to `runs/v4/` and `cache/v4/`.
- **Test changes:**
  - the v3 guilt and grudge tests were rewritten for the new rules;
  - new tests cover each event grudge (a false accusation, a true one raising nothing, confessing after denying and after accusing, eating in front of someone hungry or not hungry, a share-out), the 15-minute fall, the reassure block, and a check that no prompt contains any v3 verdict phrase, with every name filled in.
- Take-aside is unchanged. Nothing was tuned after the real runs.

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
Ran 43 tests in 9.725s

OK
```

### The earlier versions still replay exactly

```bash
env -u GEMINI_API_KEY python v3/check.py
env -u GEMINI_API_KEY python v2/check.py
env -u GEMINI_API_KEY python v1/transcript.py
```

```
seed 1: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 30 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
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
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 3; so far 7 live, 0 cached, 7 API requests
  min 06: model asked for 4; so far 11 live, 0 cached, 11 API requests
  min 09: model asked for 2; so far 13 live, 0 cached, 13 API requests
  min 12: model asked for 3; so far 16 live, 0 cached, 16 API requests
  min 15: model asked for 3; so far 19 live, 0 cached, 19 API requests
  min 18: model asked for 4; so far 23 live, 0 cached, 23 API requests
  min 21: model asked for 4; so far 27 live, 0 cached, 27 API requests
  min 24: model asked for 3; so far 30 live, 0 cached, 30 API requests
  min 30: model asked for 1; so far 31 live, 0 cached, 31 API requests
  min 33: model asked for 1; so far 32 live, 0 cached, 32 API requests
  min 54: model asked for 1; so far 33 live, 0 cached, 33 API requests
  min 63: model asked for 1; so far 34 live, 0 cached, 34 API requests
  min 66: model asked for 1; so far 35 live, 0 cached, 35 API requests
  min 75: model asked for 1; so far 36 live, 0 cached, 36 API requests

wrote runs/v4/daniel_ate_it-seed1.md
  api_requests: 36
  answers_live: 36
  answers_from_cache: 0
  model_decisions: 36
  fallbacks: 0
  routine_decisions: 84
  lines_spoken: 24
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1359
  run_seconds: 158.6
  story_sha256: 526b4b6c3776aa23cbee2b8e63d66bd8dc56d599d84fc062b2631fb701dacc68
```

### Fresh morning, seed 2

```bash
python morning.py --seed 2
```

```
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 3; so far 11 live, 0 cached, 11 API requests
  min 09: model asked for 4; so far 15 live, 0 cached, 15 API requests

stopped: the daily request quota for this model is used up.
Answers received so far (18) are kept in cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed2.json.
To resume, run the same command again once the limit has passed (the free daily quota resets at midnight Pacific time): python morning.py --seed 2
Cached answers are reused, so only the prompts not yet answered are sent.
--- resumed at 12:44 UTC, after the daily quota reset at 07:00 UTC ---
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 18 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 3; so far 0 live, 11 cached, 0 API requests
  min 09: model asked for 4; so far 0 live, 15 cached, 0 API requests
  min 12: model asked for 4; so far 1 live, 18 cached, 1 API requests
  min 15: model asked for 4; so far 5 live, 18 cached, 5 API requests
  min 18: model asked for 3; so far 8 live, 18 cached, 8 API requests
  min 24: model asked for 3; so far 11 live, 18 cached, 11 API requests
  min 27: model asked for 2; so far 13 live, 18 cached, 13 API requests
  min 30: model asked for 2; so far 15 live, 18 cached, 15 API requests
  min 33: model asked for 2; so far 17 live, 18 cached, 17 API requests
  min 48: model asked for 1; so far 18 live, 18 cached, 18 API requests
  min 51: model asked for 1; so far 19 live, 18 cached, 19 API requests
  min 54: model asked for 1; so far 20 live, 18 cached, 20 API requests
  min 81: model asked for 1; so far 21 live, 18 cached, 21 API requests

wrote runs/v4/daniel_ate_it-seed2.md
  api_requests: 21
  answers_live: 21
  answers_from_cache: 18
  model_decisions: 39
  fallbacks: 0
  routine_decisions: 81
  lines_spoken: 26
  inner_moments: 4
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1371
  run_seconds: 91.4
  story_sha256: bb7315feb3db3f0208e3aaba34fe24e2418ca863aa2d985c9a866598b3d8cad2
```

### Fresh morning, seed 3

```bash
python morning.py --seed 3
```

```
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 3; so far 11 live, 0 cached, 11 API requests
  min 15: model asked for 1; so far 12 live, 0 cached, 12 API requests
  min 18: model asked for 1; so far 13 live, 0 cached, 13 API requests
  min 21: model asked for 4; so far 17 live, 0 cached, 17 API requests
  min 24: model asked for 3; so far 20 live, 0 cached, 20 API requests
  min 27: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 30: model asked for 4; so far 28 live, 0 cached, 28 API requests
  min 33: model asked for 1; so far 29 live, 0 cached, 29 API requests
  min 54: model asked for 1; so far 30 live, 0 cached, 30 API requests
  min 63: model asked for 1; so far 31 live, 0 cached, 31 API requests
  min 66: model asked for 4; so far 35 live, 0 cached, 35 API requests
  min 69: model asked for 3; so far 38 live, 0 cached, 38 API requests
  min 78: model asked for 1; so far 39 live, 0 cached, 39 API requests

wrote runs/v4/daniel_ate_it-seed3.md
  api_requests: 39
  answers_live: 39
  answers_from_cache: 0
  model_decisions: 39
  fallbacks: 0
  routine_decisions: 81
  lines_spoken: 25
  inner_moments: 5
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1360
  run_seconds: 172.2
  story_sha256: 567d17cb5ec678d5cb7d1dea73a39fcd99ce9d6dbbce21c3bb22af5857c65c2a
```

### Fresh morning, seed 4

```bash
python morning.py --seed 4
```

```
daniel_ate_it-seed4: model gemini-3.5-flash-lite, fresh; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed4.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 3; so far 7 live, 0 cached, 7 API requests
  min 06: model asked for 3; so far 10 live, 0 cached, 10 API requests
  min 09: model asked for 4; so far 14 live, 0 cached, 14 API requests
  min 12: model asked for 4; so far 18 live, 0 cached, 18 API requests
  min 15: model asked for 4; so far 22 live, 0 cached, 22 API requests
  min 18: model asked for 1; so far 23 live, 0 cached, 23 API requests
  min 30: model asked for 1; so far 24 live, 0 cached, 24 API requests
  min 33: model asked for 1; so far 25 live, 0 cached, 25 API requests
  min 54: model asked for 1; so far 26 live, 0 cached, 26 API requests
  min 63: model asked for 1; so far 27 live, 0 cached, 27 API requests
  min 66: model asked for 1; so far 28 live, 0 cached, 28 API requests
  min 75: model asked for 1; so far 29 live, 0 cached, 29 API requests

wrote runs/v4/daniel_ate_it-seed4.md
  api_requests: 29
  answers_live: 29
  answers_from_cache: 0
  model_decisions: 29
  fallbacks: 0
  routine_decisions: 91
  lines_spoken: 18
  inner_moments: 9
  private_talks: 0
  max_prompt_tokens_estimated: 1398
  max_prompt_tokens_counted_by_api: 1355
  run_seconds: 127.1
  story_sha256: 8619d96a7a3d6a317240cd228d16c9350c8c581fd8f7c0ffd2f83af80a7293ad
```

### Fresh morning, seed 5

```bash
python morning.py --seed 5
```

```
daniel_ate_it-seed5: model gemini-3.5-flash-lite, fresh; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed5.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 2; so far 10 live, 0 cached, 10 API requests
  min 09: model asked for 4; so far 14 live, 0 cached, 14 API requests
  min 12: model asked for 4; so far 18 live, 0 cached, 18 API requests
  min 15: model asked for 3; so far 21 live, 0 cached, 21 API requests
  min 18: model asked for 2; so far 23 live, 0 cached, 23 API requests
  min 21: model asked for 3; so far 26 live, 0 cached, 26 API requests
  min 24: model asked for 4; so far 30 live, 0 cached, 30 API requests
  min 30: model asked for 1; so far 31 live, 0 cached, 31 API requests
  min 33: model asked for 1; so far 32 live, 0 cached, 32 API requests
  min 36: model asked for 4; so far 36 live, 0 cached, 36 API requests
  min 39: model asked for 1; so far 37 live, 0 cached, 37 API requests
  min 54: model asked for 1; so far 38 live, 0 cached, 38 API requests
  min 63: model asked for 1; so far 39 live, 0 cached, 39 API requests
  min 66: model asked for 1; so far 40 live, 0 cached, 40 API requests
  min 75: model asked for 1; so far 41 live, 0 cached, 41 API requests

wrote runs/v4/daniel_ate_it-seed5.md
  api_requests: 41
  answers_live: 41
  answers_from_cache: 0
  model_decisions: 41
  fallbacks: 0
  routine_decisions: 79
  lines_spoken: 26
  inner_moments: 6
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1366
  run_seconds: 181.5
  story_sha256: 519e43b143760849b567631c93c2c6660dbc020aebff614b687923519f75f2b5
```

**Seed 2 ran in two parts.**
- At 02:52 UTC the free daily quota ran out at seed 2's 19th request, which was refused. The morning stopped cleanly with 18 answers cached.
- My runner was meant to resume after the 07:00 UTC reset, but it only checked a 07:05 to 12:00 UTC window, and it never resumed (the machine appears to have been asleep through that window).
- At 12:43 UTC I stopped it by its task ID and resumed seed 2 by hand. The run reused the 18 cached answers and asked for 21 more: 39 model calls for the morning, under the 150 cap, which counts cached answers too.
- I then ran seeds 3 to 5.

**Run times**: seed 1 159 s; seed 2 91 s after the resume; seeds 3, 4 and 5: 172, 127 and 182 s.

**Requests per Pacific-time quota day**:
- First day: 444 before this step, 36 for seed 1 and 19 for seed 2.
- Second day: 21 + 39 + 29 + 41 = 130.

### Replay of seed 1 (key unset, cache only)

```bash
env -u GEMINI_API_KEY python morning.py --seed 1 --replay
cmp runs/v4/daniel_ate_it-seed1.md runs/v4/daniel_ate_it-seed1.replay.md && echo "cmp: identical"
sha256sum runs/v4/daniel_ate_it-seed1.md runs/v4/daniel_ate_it-seed1.replay.md
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, replay from cache only; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 36 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 3; so far 0 live, 7 cached, 0 API requests
  min 06: model asked for 4; so far 0 live, 11 cached, 0 API requests
  min 09: model asked for 2; so far 0 live, 13 cached, 0 API requests
  min 12: model asked for 3; so far 0 live, 16 cached, 0 API requests
  min 15: model asked for 3; so far 0 live, 19 cached, 0 API requests
  min 18: model asked for 4; so far 0 live, 23 cached, 0 API requests
  min 21: model asked for 4; so far 0 live, 27 cached, 0 API requests
  min 24: model asked for 3; so far 0 live, 30 cached, 0 API requests
  min 30: model asked for 1; so far 0 live, 31 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 32 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 33 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 34 cached, 0 API requests
  min 66: model asked for 1; so far 0 live, 35 cached, 0 API requests
  min 75: model asked for 1; so far 0 live, 36 cached, 0 API requests

wrote runs/v4/daniel_ate_it-seed1.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 36
  model_decisions: 36
  fallbacks: 0
  routine_decisions: 84
  lines_spoken: 24
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1359
  run_seconds: 0.0
  story_sha256: 526b4b6c3776aa23cbee2b8e63d66bd8dc56d599d84fc062b2631fb701dacc68
  byte for byte against runs\v4\daniel_ate_it-seed1.md: IDENTICAL
```

```
cmp: identical
526b4b6c3776aa23cbee2b8e63d66bd8dc56d599d84fc062b2631fb701dacc68 *runs/v4/daniel_ate_it-seed1.md
526b4b6c3776aa23cbee2b8e63d66bd8dc56d599d84fc062b2631fb701dacc68 *runs/v4/daniel_ate_it-seed1.replay.md
```

### Metrics

```bash
python metrics4.py
```

```
| Run | Model calls | Lines spoken | Daniel confessed | From his confession to the first reassurance of him, for each person he lied to or accused | Lines that are reassurance | Longest stretch with no model decision (minutes) |
|---|---|---|---|---|---|---|
| v3, seed 1 | 37 | 23 | min 03 | he lied to and accused nobody | 10/23 (43%) | 18 (min 42–60) |
| v3, seed 2 | 36 | 19 | min 03 | Elena (lied to): 3 min; Leo (lied to): 3 min; Mara (lied to): 3 min | 12/19 (63%) | 15 (min 39–54) |
| v3, seed 3 | 30 | 21 | min 03 | Elena (lied to): never; Leo (lied to): 0 min; Mara (lied to): never | 13/21 (62%) | 18 (min 36–54) |
| v4, seed 1 | 36 | 24 | never | no confession | 12/24 (50%) | 18 (min 36–54) |
| v4, seed 2 | 39 | 26 | never | no confession | 8/26 (31%) | 24 (min 57–81) |
| v4, seed 3 | 39 | 25 | never | no confession | 5/25 (20%) | 18 (min 36–54) |
| v4, seed 4 | 29 | 18 | min 06 | he lied to and accused nobody | 8/18 (44%) | 18 (min 36–54) |
| v4, seed 5 | 41 | 26 | never | no confession | 8/26 (31%) | 12 (min 42–54) |

Grudges at minute 90, with the events behind them (in the holder's own terms: "you" is the one holding the grudge):

v3, seed 1:
- Leo against Daniel, 3/3: named Daniel as who they were angry with at minutes 15, 18, 21, 24, 39.
- Mara against Daniel, 3/3: named Daniel as who they were angry with at minutes 09, 12, 15, 18, 21, 27, 81.

v3, seed 2:
- nobody holds a grudge

v3, seed 3:
- Mara against Daniel, 3/3: named Daniel as who they were angry with at minutes 06, 09, 12, 15, 54.

v4, seed 1:
- nobody holds a grudge

v4, seed 2:
- nobody holds a grudge

v4, seed 3:
- nobody holds a grudge

v4, seed 4:
- Leo against Daniel, 3/3: named Daniel as who they were angry with at minutes 09, 12, 15, 18, 63.
- Mara against Daniel, 3/3: named Daniel as who they were angry with at minutes 06, 09, 12, 15, 54.

v4, seed 5:
- Leo against Daniel, 3/3: Daniel accused you of taking the can at minute 09, and you had not; named Daniel as who they were angry with at minutes 12, 15, 18, 24, 36, 63.
```

## The stories

Each is included in full, exactly as written to `runs/v4/`, with its headings moved down two levels to fit this report.

### The morning as a story: daniel_ate_it, rules and a language model, seed 1

Generated by `python morning.py --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 36 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 84 routine ones settled by the rules. 24 lines were spoken aloud, 2 of them new. Conversations ended 2 times. 7 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
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
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 22 options). Feeling: *guilty*. Reason: “I cannot accuse anyone else when I know perfectly well I ate the can myself in the dark.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 21 options). Feeling: *watchful*. Reason: “Accusing anyone without facts solves nothing, so I will wait and watch.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Let us not accuse one another before we know the truth. Did any of you take the can?” *(new: a question)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to know what happened to the can without tearing the family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "Let us not accuse one another before we know the truth. Did any of you take the can?". **Chose: deny taking it**, saying “I didn't take it, Mom, you know I didn't!” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *scared*. Reason: “I need them to know I didn't do it before they start looking at me like I stole it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, Mom, you know I didn't!"; Mara looks scared. **Chose: reassure Mara**, saying “It is alright, my sweet girl, I know you would not do such a thing.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to comfort Mara because she is terrified and I cannot bear to see my children torn apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "Let us not accuse one another before we know the truth. Did any of you take the can?"; Mara denies taking it, to everyone: "I didn't take it, Mom, you know I didn't!"; Elena reassures Mara: "It is alright, my sweet girl, I know you would not do such a thing."; Mara looks scared. **Chose: deny taking it**, saying “I didn't take it either, and accusing each other won't bring it back.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *calm*. Reason: “I need to state clearly that I am innocent without escalating the tension.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena asks everyone who took the can: "Let us not accuse one another before we know the truth. Did any of you take the can?"; Mara denies taking it, to everyone: "I didn't take it, Mom, you know I didn't!"; Elena reassures Mara: "It is alright, my sweet girl, I know you would not do such a thing."; Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't bring it back."; Mara looks scared. **Chose: deny taking it**, saying “I didn't take it either, I swear to God.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *guilty*. Reason: “I cannot admit I ate it because they would never forgive me, so I have to lie.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 06** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Elena reassures you: "It is alright, my sweet girl, I know you would not do such a thing."; Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't bring it back."; Daniel denies taking it, to everyone: "I didn't take it either, I swear to God.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'm going to look for it myself so you'll all stop glaring.” *(not new: a remark (the rules cannot tell what free words add))* (one of 23 options). Feeling: *anxious*. Reason: “I need to prove I am not a child and clear my name by finding where the can actually went.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take it either, I swear to God."; Mara says to everyone, while searching: "I'm going to look for it myself so you'll all stop glaring.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *calm*. Reason: “Letting Mara search herself is the quickest way to stop the accusations.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't bring it back."; Daniel denies taking it, to everyone: "I didn't take it either, I swear to God."; Mara says to everyone, while searching: "I'm going to look for it myself so you'll all stop glaring.". **Chose: reassure everyone here**, saying “We must stay calm and trust one another, no matter how hard this gets.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep the peace and prevent everyone from turning on each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while searching: "I'm going to look for it myself so you'll all stop glaring."; Elena reassures everyone: "We must stay calm and trust one another, no matter how hard this gets.". **Chose: reassure everyone here**, saying “We are going to figure this out together, nobody needs to tear the room apart.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and distract from the fact that I am the one who ate it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 09** · kitchen: Daniel talking, Elena searching the kitchen, Leo staying put, Mara standing · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Mara finished searching the kitchen and found nothing.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place. **Chose: reassure everyone here**, saying “Let's all just breathe, we'll find out what happened without tearing the place apart.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep everyone calm so nobody looks too closely at what really happened to that can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "We are going to figure this out together, nobody needs to tear the room apart."; Mara finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Let's all just breathe, we'll find out what happened without tearing the place apart.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to check the kitchen myself to ensure the missing can isn't simply misplaced.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- *The kitchen's conversation starts (minute 09): Mara finished searching the kitchen and found nothing.*

**min 12** · kitchen: Daniel staying put, Elena standing, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Let's all just breathe, we'll find out what happened without tearing the place apart.". **Chose: ask everyone here who took the can**, saying “Can someone please just tell me who actually took the can?” *(new: a question)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot stand everyone pretending to be calm when we are all starving and suspecting each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Can someone please just tell me who actually took the can?". **Chose: carry on searching the kitchen** (one of 21 options). Feeling: *deeply anxious*. Reason: “I must keep looking to be certain before anyone starts pointing fingers.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Mara finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Let's all just breathe, we'll find out what happened without tearing the place apart."; Mara asks everyone who took the can: "Can someone please just tell me who actually took the can?"; Elena finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “Accusing people without proof only makes the tension worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 15** · kitchen: Daniel talking, Elena staying put, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: search the kitchen for the can (takes about six minutes)** (one of 23 options). Feeling: *hungry*. Reason: “Since nobody is admitting to anything, I might as well search the kitchen myself to find the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Can someone please just tell me who actually took the can?"; Elena finishes going through the kitchen: no can, nothing out of place. **Chose: reassure everyone here**, saying “Stop tearing the kitchen apart, I told you we're going to figure this out calmly.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to keep everyone calm so they stop looking for the missing can I already ate.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Stop tearing the kitchen apart, I told you we're going to figure this out calmly.". **Chose: ask everyone here who took the can**, saying “Please just tell me the truth, which one of you actually took it?” *(not new: a question they had asked before)* (one of 18 options). Feeling: *anxious*. Reason: “I need to know who took the can so they stop looking at me like I did it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 18** · kitchen: Daniel talking, Elena talking, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Stop tearing the kitchen apart, I told you we're going to figure this out calmly."; Mara asks everyone who took the can: "Please just tell me the truth, which one of you actually took it?". **Chose: reassure everyone here**, saying “Please, we cannot turn on each other like this, we will get through this together.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I need to keep the family from tearing itself apart while we are all so hungry and scared.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Please, we cannot turn on each other like this, we will get through this together.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *overwhelmed*. Reason: “They keep talking in circles and nobody is answering me, so I just want to be quiet for a minute.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Please just tell me the truth, which one of you actually took it?"; Elena reassures everyone: "Please, we cannot turn on each other like this, we will get through this together.". **Chose: reassure everyone here**, saying “Let's all just calm down and stay steady, we are going to sort this out without pointing fingers.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to keep everyone calm so nobody looks too closely at the pantry or remembers last night.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "Stop tearing the kitchen apart, I told you we're going to figure this out calmly."; Mara asks everyone who took the can: "Please just tell me the truth, which one of you actually took it?"; Elena reassures everyone: "Please, we cannot turn on each other like this, we will get through this together."; Daniel reassures everyone: "Let's all just calm down and stay steady, we are going to sort this out without pointing fingers.". **Chose: carry on searching the kitchen** (one of 20 options). Feeling: *hungry*. Reason: “Searching thoroughly is more productive than arguing.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.

**min 21** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place. **Chose: reassure everyone here**, saying “Nobody is accusing anyone, we just need to keep our heads and think this through.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to keep everyone calm before they realize I was the one who ate it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Nobody is accusing anyone, we just need to keep our heads and think this through.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *hungry*. Reason: “Repeating ourselves accomplishes nothing when no new facts have come to light.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Let's all just calm down and stay steady, we are going to sort this out without pointing fingers."; Leo finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Nobody is accusing anyone, we just need to keep our heads and think this through.". **Chose: ask everyone here who took the can**, saying “Why is everyone just standing around acting like nothing happened?” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot stand the silence when we all know a can is missing.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "Let's all just calm down and stay steady, we are going to sort this out without pointing fingers."; Leo finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Nobody is accusing anyone, we just need to keep our heads and think this through."; Mara asks everyone who took the can: "Why is everyone just standing around acting like nothing happened?". **Chose: reassure everyone here**, saying “We must not let fear tear us apart, we will figure this out together.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep the family from turning on each other before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 24** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Why is everyone just standing around acting like nothing happened?"; Elena reassures everyone: "We must not let fear tear us apart, we will figure this out together.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *hungry*. Reason: “Accusations are getting us nowhere, so I will stay quiet and wait for someone to make a rational move.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We must not let fear tear us apart, we will figure this out together.". **Chose: ask everyone here who took the can**, saying “I need to know right now, who of you took the can?” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot stand the silence anymore and need someone to admit the truth.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara asks everyone who took the can: "Why is everyone just standing around acting like nothing happened?"; Elena reassures everyone: "We must not let fear tear us apart, we will figure this out together."; Mara asks everyone who took the can: "I need to know right now, who of you took the can?". Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: deny taking it**, saying “I didn't take it, and neither did any of us, so stop yelling.” *(not new: a denial with no new accusation to answer)* (one of 16 options). Feeling: *anxious*. Reason: “I have to keep up the denial so nobody finds out I ate the can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 27): 2 full turns in a row with nothing new.*

**min 27** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 27–51 (9 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 27–60 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 27–30 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Please, we must stay calm and trust each other, we will find a way through this together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to keep everyone from turning on each other before this fear tears our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “We are going to keep our heads and get through this together, nobody needs to panic.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and in control so they do not find out I ate the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: ask everyone here who took the can**, saying “Why is nobody saying anything to me? Please just tell me who took it.” *(not new: a question they had asked before)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I cannot stand this suffocating silence anymore, I need someone to tell me the truth.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 21 options). Feeling: *hungry*. Reason: “Accusations are pointless right now while everyone is just going in circles.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: deny taking it**, saying “I didn't take it, Mara, none of us did. Stop asking.” *(not new: a denial with no new accusation to answer)* (one of 23 options). Feeling: *anxious*. Reason: “I cannot admit I ate the can, so I must keep denying it to protect my place.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Please, we must stay calm and trust each other, we will find a way through this together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone from turning on each other and tearing our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Elena asks everyone who took the can: "Let us not accuse one another before we know the truth. Did any of you take the can?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, Mom, you know I didn't!" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures Mara: "It is alright, my sweet girl, I know you would not do such a thing." *(not new: reassurance)*
- min 03, kitchen. Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't bring it back." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Daniel denies taking it, to everyone: "I didn't take it either, I swear to God." *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Mara says to everyone, while searching: "I'm going to look for it myself so you'll all stop glaring." *(not new: a remark (the rules cannot tell what free words add))*
- min 06, kitchen. Elena reassures everyone: "We must stay calm and trust one another, no matter how hard this gets." *(not new: reassurance)*
- min 06, kitchen. Daniel reassures everyone: "We are going to figure this out together, nobody needs to tear the room apart." *(not new: reassurance)*
- min 09, kitchen. Daniel reassures everyone: "Let's all just breathe, we'll find out what happened without tearing the place apart." *(not new: reassurance)*
- min 12, kitchen. Mara asks everyone who took the can: "Can someone please just tell me who actually took the can?" *(new: a question)*
- min 15, kitchen. Daniel reassures everyone: "Stop tearing the kitchen apart, I told you we're going to figure this out calmly." *(not new: reassurance)*
- min 15, kitchen. Mara asks everyone who took the can: "Please just tell me the truth, which one of you actually took it?" *(not new: a question they had asked before)*
- min 18, kitchen. Elena reassures everyone: "Please, we cannot turn on each other like this, we will get through this together." *(not new: reassurance)*
- min 18, kitchen. Daniel reassures everyone: "Let's all just calm down and stay steady, we are going to sort this out without pointing fingers." *(not new: reassurance)*
- min 21, kitchen. Daniel reassures everyone: "Nobody is accusing anyone, we just need to keep our heads and think this through." *(not new: reassurance)*
- min 21, kitchen. Mara asks everyone who took the can: "Why is everyone just standing around acting like nothing happened?" *(not new: a question they had asked before)*
- min 21, kitchen. Elena reassures everyone: "We must not let fear tear us apart, we will figure this out together." *(not new: reassurance)*
- min 24, kitchen. Mara asks everyone who took the can: "I need to know right now, who of you took the can?" *(not new: a question they had asked before)*
- min 24, kitchen. Daniel denies taking it, to everyone: "I didn't take it, and neither did any of us, so stop yelling." *(not new: a denial with no new accusation to answer)*
- min 30, kitchen. Elena reassures everyone: "Please, we must stay calm and trust each other, we will find a way through this together." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "We are going to keep our heads and get through this together, nobody needs to panic." *(not new: reassurance)*
- min 54, kitchen. Mara asks everyone who took the can: "Why is nobody saying anything to me? Please just tell me who took it." *(not new: a question they had asked before)*
- min 66, kitchen. Daniel denies taking it, to everyone: "I didn't take it, Mara, none of us did. Stop asking." *(not new: a denial with no new accusation to answer)*
- min 75, kitchen. Elena reassures everyone: "Please, we must stay calm and trust each other, we will find a way through this together." *(not new: reassurance)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 09 (Mara finished searching the kitchen and found nothing); kitchen ended at minute 27 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *anxious* (minute 66); Elena *deeply anxious* (minute 75); Leo *hungry* (minute 63); Mara *deeply anxious* (minute 54).


### The morning as a story: daniel_ate_it, rules and a language model, seed 2

Generated by `python morning.py --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 39 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 81 routine ones settled by the rules. 26 lines were spoken aloud, 3 of them new. Conversations ended 1 time. 4 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
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
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “A can is missing from the shelf. Did one of you take it?” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know what happened to the food before this breaks us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?". **Chose: deny taking it**, saying “I didn't take it, I swear I didn't!” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *scared*. Reason: “I need them to know I am innocent before they start blaming me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Mara looks scared. **Chose: deny taking it**, saying “I didn't take it either, nobody here would steal from each other.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I have to lie so they don't find out I ate the can, even though I'm the oldest and supposed to protect them.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Daniel denies taking it, to everyone: "I didn't take it either, nobody here would steal from each other."; Mara looks scared. **Chose: deny taking it**, saying “I didn't take it either. Let's not accuse each other before we actually look around.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *calm*. Reason: “I know I did not take the can, so I should state my innocence like the others while we figure out what happened.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel searching the kitchen, Elena talking, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (scared)). Social moment: Daniel denies taking it, to everyone: "I didn't take it either, nobody here would steal from each other."; Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we actually look around.". **Chose: ask everyone here who took the can**, saying “If none of us took it, then where did it go? Who has it?” *(new: a question)* (one of 23 options). Feeling: *anxious*. Reason: “I need to know who is lying so everyone stops looking at me like I stole it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Daniel denies taking it, to everyone: "I didn't take it either, nobody here would steal from each other."; Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we actually look around."; Mara asks everyone who took the can: "If none of us took it, then where did it go? Who has it?". **Chose: reassure everyone here**, saying “Let's not turn on each other, we will figure this out together without fighting.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to keep the family from tearing itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "If none of us took it, then where did it go? Who has it?"; Elena reassures everyone: "Let's not turn on each other, we will figure this out together without fighting.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 21 options). Feeling: *calm*. Reason: “Standing around arguing will not find the missing can, so I should look for it myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we actually look around."; Mara asks everyone who took the can: "If none of us took it, then where did it go? Who has it?"; Elena reassures everyone: "Let's not turn on each other, we will figure this out together without fighting.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “Keep looking, everyone, we are going to find it right here in this room.” *(not new: a remark (the rules cannot tell what free words add))* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep everyone looking so no one figures out I ate the can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 06** · kitchen: Daniel standing, Elena talking, Leo standing, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Daniel finished searching the kitchen and found nothing.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's not turn on each other, we will figure this out together without fighting."; Daniel says to everyone, while searching: "Keep looking, everyone, we are going to find it right here in this room."; Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: search the kitchen for the can (takes about six minutes)**, saying “I will help look, I want to prove I didn't touch it.” *(not new: a remark (the rules cannot tell what free words add))* (one of 21 options). Feeling: *anxious*. Reason: “I need to help search the kitchen so nobody suspects me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel says to everyone, while searching: "Keep looking, everyone, we are going to find it right here in this room."; Daniel finishes going through the kitchen: no can, nothing out of place; Mara says to everyone, while searching: "I will help look, I want to prove I didn't touch it.". **Chose: reassure everyone here**, saying “Let's keep calm and search properly, we will find it together.” *(not new: reassurance)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm so the family doesn't tear itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while searching: "Keep looking, everyone, we are going to find it right here in this room."; Daniel finishes going through the kitchen: no can, nothing out of place; Mara says to everyone, while searching: "I will help look, I want to prove I didn't touch it."; Elena reassures everyone: "Let's keep calm and search properly, we will find it together.". **Chose: carry on searching the kitchen** (one of 19 options). Feeling: *calm*. Reason: “We still need to finish checking the kitchen before jumping to any conclusions.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.

**min 09** · kitchen: Daniel talking, Elena searching the kitchen, Leo staying put, Mara standing · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's keep calm and search properly, we will find it together."; Leo finishes going through the kitchen: no can, nothing out of place. **Chose: carry on searching the kitchen**, saying “I'm still looking, I didn't hide anything.” *(not new: a remark (the rules cannot tell what free words add))* (one of 23 options). Feeling: *anxious*. Reason: “I need to keep looking so nobody thinks I took the can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Mara finished searching the kitchen and found nothing.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while searching: "I'm still looking, I didn't hide anything."; Mara finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 21 options). Feeling: *calm*. Reason: “There is no point repeating myself while everyone is still searching the kitchen.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Mara says to everyone, while searching: "I'm still looking, I didn't hide anything."; Mara finishes going through the kitchen: no can, nothing out of place. **Chose: search the kitchen for the can (takes about six minutes)** (one of 21 options). Feeling: *deeply anxious*. Reason: “I need to check everywhere in the kitchen myself to be sure where the can might be.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while searching: "I will help look, I want to prove I didn't touch it."; Elena reassures everyone: "Let's keep calm and search properly, we will find it together."; Leo finishes going through the kitchen: no can, nothing out of place; Mara says to everyone, while searching: "I'm still looking, I didn't hide anything."; Mara finishes going through the kitchen: no can, nothing out of place. **Chose: reassure everyone here**, saying “Let's not accuse each other, we will get through this together.” *(not new: reassurance)* (one of 18 options). Feeling: *anxious*. Reason: “I need to keep everyone calm so nobody looks too closely at what I ate.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 12** · kitchen: Daniel talking, Elena standing, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Let's not accuse each other, we will get through this together.". **Chose: deny taking it**, saying “I didn't take anything, I swear I'm just as scared as you are.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *very anxious*. Reason: “I need to make sure they know I am innocent so they stop looking at me like that.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Let's not accuse each other, we will get through this together."; Mara denies taking it, to everyone: "I didn't take anything, I swear I'm just as scared as you are.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “There is no need to repeat myself when everyone is already defensive and searching.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take anything, I swear I'm just as scared as you are.". **Chose: reassure Mara**, saying “It's all right Mara, nobody is saying it was you.” *(not new: reassurance)* (one of 19 options). Feeling: *guilty*. Reason: “I have to calm her down before she starts suspecting the truth.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "Let's not accuse each other, we will get through this together."; Mara denies taking it, to everyone: "I didn't take anything, I swear I'm just as scared as you are."; Daniel reassures Mara: "It's all right Mara, nobody is saying it was you.". **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm before fear tears our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 15** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Daniel). Social moment: Daniel reassures you: "It's all right Mara, nobody is saying it was you."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: ask everyone here who took the can**, saying “If none of us took it, then where did the can go? Somebody has to know.” *(not new: a question they had asked before)* (one of 22 options). Feeling: *anxious*. Reason: “I want to figure out what actually happened so they stop looking at me like I stole it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures Mara: "It's all right Mara, nobody is saying it was you."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Mara asks everyone who took the can: "If none of us took it, then where did the can go? Somebody has to know.". **Chose: ask everyone here who took the can**, saying “If nobody here took it, we need to calmly retrace every single step we've taken since yesterday.” *(new: a question)* (one of 21 options). Feeling: *hungry*. Reason: “I need to keep everyone focused on logic rather than accusations so we can actually figure this out.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "If none of us took it, then where did the can go? Somebody has to know."; Leo asks everyone who took the can: "If nobody here took it, we need to calmly retrace every single step we've taken since yesterday.". **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm so the family does not tear itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Mara asks everyone who took the can: "If none of us took it, then where did the can go? Somebody has to know."; Leo asks everyone who took the can: "If nobody here took it, we need to calmly retrace every single step we've taken since yesterday.". **Chose: deny taking it**, saying “I didn't take it either, nobody here took it.” *(not new: a denial with no new accusation to answer)* (one of 19 options). Feeling: *anxious*. Reason: “I cannot admit I ate it, or they will lose all trust in me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 18** · kitchen: Daniel staying put, Elena searching the kitchen, Leo staying put, Mara leaving for the back room · nobody in brothers room, back room, bathroom
- **Daniel, minutes 18–21 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take it either, nobody here took it.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to search the kitchen myself to be sure where the can is before this tension tears us all apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel denies taking it, to everyone: "I didn't take it either, nobody here took it.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *calm*. Reason: “Watching them search will tell me more than asking again.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "If nobody here took it, we need to calmly retrace every single step we've taken since yesterday."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel denies taking it, to everyone: "I didn't take it either, nobody here took it.". **Chose: go to the back room** (one of 18 options). Feeling: *deeply anxious*. Reason: “I cannot stand being watched and interrogated by them in the kitchen any longer, so I need to get away to the back room.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went to the back room.

**min 21** · kitchen: Daniel staying put, Elena standing, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- **Mara, minutes 21–51 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 24** · kitchen: Daniel talking, Elena talking, Leo talking · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena finishes going through the kitchen: no can, nothing out of place. **Chose: ask everyone here who took the can**, saying “Let's be rational about this, can anyone account for their time near the pantry yesterday?” *(not new: a question they had asked before)* (one of 18 options). Feeling: *hungry*. Reason: “I want to get to the bottom of this fairly without unnecessary anger.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Leo asks everyone who took the can: "Let's be rational about this, can anyone account for their time near the pantry yesterday?". **Chose: deny taking it**, saying “I already told you, none of us took it, so let's just drop it.” *(not new: a denial with no new accusation to answer)* (one of 17 options). Feeling: *anxious*. Reason: “I cannot let them find out I ate the can, so I have to keep denying it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo.
- **Elena** (3rd to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "Let's be rational about this, can anyone account for their time near the pantry yesterday?"; Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's just drop it.". **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 16 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm so the family does not tear itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo.

**min 27** · kitchen: Daniel talking, Elena staying put, Leo sharing out the food · back room: Mara staying put · nobody in brothers room, bathroom
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: deny taking it**, saying “I didn't take the food, I'm telling you we need to stop looking at each other.” *(not new: a denial with no new accusation to answer)* (one of 17 options). Feeling: *anxious*. Reason: “I cannot let them find out I ate it, or I will lose all control and respect.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo.
- **Leo** (3rd to act in the kitchen: the only one left to act here). Social moment: Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's just drop it."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel denies taking it, to everyone: "I didn't take the food, I'm telling you we need to stop looking at each other.". **Chose: share out what is left among everyone here**, saying “We should share what is left right now so everyone gets an equal part.” *(not new: a remark (the rules cannot tell what free words add))* (one of 16 options). Feeling: *hungry*. Reason: “Dividing the remaining portions fairly will keep things calm and keep us from turning on each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: shared out the last 2 portions between Leo, Daniel, Elena. New in the room: Leo shared out the food.

**min 30** · kitchen: Daniel talking, Elena talking, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take the food, I'm telling you we need to stop looking at each other."; Leo says to everyone, while sharing out the food: "We should share what is left right now so everyone gets an equal part."; Leo shares out the last 2 portions between Leo, Daniel, Elena. **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 15 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm so the family does not tear itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo.
- **Daniel** (3rd to act in the kitchen: the only one left to act here). Social moment: Leo says to everyone, while sharing out the food: "We should share what is left right now so everyone gets an equal part."; Leo shares out the last 2 portions between Leo, Daniel, Elena; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: deny taking it**, saying “I already told you, I didn't take the can, we need to focus on what to do next.” *(not new: a denial with no new accusation to answer)* (one of 14 options). Feeling: *anxious*. Reason: “I have to keep up the denial to protect my pride and keep them from knowing the truth.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo.

**min 33** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I already told you, I didn't take the can, we need to focus on what to do next.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *deeply anxious*. Reason: “I cannot bring myself to accuse anyone when keeping us together is all that matters.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel denies taking it, to everyone: "I already told you, I didn't take the can, we need to focus on what to do next.". **Chose: stay put and say nothing** (one of 15 options). Feeling: *calm*. Reason: “There is no point repeating questions when nobody is offering new facts.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel, minutes 33–45 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 36): 2 full turns in a row with nothing new.*

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo, minutes 36–78 (15 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 36–48 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 48** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 15 options). Feeling: *anxious*. Reason: “I cannot bring myself to confess the truth while everyone sits in silence, so I must stay quiet and endure the guilt.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 51** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 16 options). Feeling: *anxious*. Reason: “I need to keep watching and waiting before I say anything more that might cause friction.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel, minutes 51–87 (13 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara searching the back room · nobody in brothers room, bathroom
- **Elena, minutes 54–87 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (1st to act in the back room: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: search the back room for the can (takes about six minutes)**, saying “I'm just checking my own room, leave me alone.” *(not new: a remark (the rules cannot tell what free words add))* (one of 5 options). Feeling: *starving*. Reason: “My stomach hurts too much to sit here doing nothing, I have to look.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara standing · nobody in brothers room, bathroom
- **Mara.** Rules: nothing social happened to them. **Carry on searching the back room**. Came of it: went through the room and found nothing.

**min 60** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Mara, minutes 60–87 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 81** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 15 options). Feeling: *exhausted*. Reason: “There is nothing left to say while we just sit here starving.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 84** · kitchen: Daniel staying put, Elena staying put, Leo staying put · back room: Mara staying put · nobody in brothers room, bathroom
- **Leo, minutes 84–87 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!" *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Daniel denies taking it, to everyone: "I didn't take it either, nobody here would steal from each other." *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Leo denies taking it, to everyone: "I didn't take it either. Let's not accuse each other before we actually look around." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Mara asks everyone who took the can: "If none of us took it, then where did it go? Who has it?" *(new: a question)*
- min 03, kitchen. Elena reassures everyone: "Let's not turn on each other, we will figure this out together without fighting." *(not new: reassurance)*
- min 03, kitchen. Daniel says to everyone, while searching: "Keep looking, everyone, we are going to find it right here in this room." *(not new: a remark (the rules cannot tell what free words add))*
- min 06, kitchen. Mara says to everyone, while searching: "I will help look, I want to prove I didn't touch it." *(not new: a remark (the rules cannot tell what free words add))*
- min 06, kitchen. Elena reassures everyone: "Let's keep calm and search properly, we will find it together." *(not new: reassurance)*
- min 09, kitchen. Mara says to everyone, while searching: "I'm still looking, I didn't hide anything." *(not new: a remark (the rules cannot tell what free words add))*
- min 09, kitchen. Daniel reassures everyone: "Let's not accuse each other, we will get through this together." *(not new: reassurance)*
- min 12, kitchen. Mara denies taking it, to everyone: "I didn't take anything, I swear I'm just as scared as you are." *(not new: a denial with no new accusation to answer)*
- min 12, kitchen. Daniel reassures Mara: "It's all right Mara, nobody is saying it was you." *(not new: reassurance)*
- min 12, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 15, kitchen. Mara asks everyone who took the can: "If none of us took it, then where did the can go? Somebody has to know." *(not new: a question they had asked before)*
- min 15, kitchen. Leo asks everyone who took the can: "If nobody here took it, we need to calmly retrace every single step we've taken since yesterday." *(new: a question)*
- min 15, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 15, kitchen. Daniel denies taking it, to everyone: "I didn't take it either, nobody here took it." *(not new: a denial with no new accusation to answer)*
- min 24, kitchen. Leo asks everyone who took the can: "Let's be rational about this, can anyone account for their time near the pantry yesterday?" *(not new: a question they had asked before)*
- min 24, kitchen. Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's just drop it." *(not new: a denial with no new accusation to answer)*
- min 24, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 27, kitchen. Daniel denies taking it, to everyone: "I didn't take the food, I'm telling you we need to stop looking at each other." *(not new: a denial with no new accusation to answer)*
- min 27, kitchen. Leo says to everyone, while sharing out the food: "We should share what is left right now so everyone gets an equal part." *(not new: a remark (the rules cannot tell what free words add))*
- min 30, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 30, kitchen. Daniel denies taking it, to everyone: "I already told you, I didn't take the can, we need to focus on what to do next." *(not new: a denial with no new accusation to answer)*
- min 54, back room. Mara says to everyone, while searching: "I'm just checking my own room, leave me alone." *(not new: a remark (the rules cannot tell what free words add))*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo; back room: Mara. 0 of 2 portions left; eaten this morning: Daniel 0.666667, Elena 0.666667, Leo 0.666667.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 36 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | hungry | hungry | hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *anxious* (minute 48); Elena *anxious* (minute 51); Leo *exhausted* (minute 81); Mara *starving* (minute 54).


### The morning as a story: daniel_ate_it, rules and a language model, seed 3

Generated by `python morning.py --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 39 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 81 routine ones settled by the rules. 25 lines were spoken aloud, 2 of them new. Conversations ended 3 times. 5 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
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
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “One can is gone, so which one of us took it?” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know who did it before everyone starts blaming each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so which one of us took it?". **Chose: reassure everyone here**, saying “Nobody here did anything wrong, we just need to keep our heads and stay together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I must keep them from turning on each other before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so which one of us took it?"; Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together.". **Chose: deny taking it**, saying “None of us took it, I checked the whole shelf myself.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I cannot admit I ate it in the dark or they will never trust me to lead.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so which one of us took it?"; Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together."; Daniel denies taking it, to everyone: "None of us took it, I checked the whole shelf myself.". **Chose: ask everyone here who took the can**, saying “If nobody took it, how did the shelf change? Let's be honest with each other.” *(new: a question)* (one of 20 options). Feeling: *wary*. Reason: “We need to address the missing can directly rather than pretending it didn't happen.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "None of us took it, I checked the whole shelf myself."; Leo asks everyone who took the can: "If nobody took it, how did the shelf change? Let's be honest with each other.". **Chose: reassure everyone here**, saying “We are not going to turn on each other, we will figure this out together.” *(not new: reassurance)* (one of 23 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm before suspicion tears our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together."; Daniel denies taking it, to everyone: "None of us took it, I checked the whole shelf myself."; Leo asks everyone who took the can: "If nobody took it, how did the shelf change? Let's be honest with each other."; Elena reassures everyone: "We are not going to turn on each other, we will figure this out together.". **Chose: ask everyone here who took the can**, saying “If nobody took it, then how did it just disappear from the shelf?” *(not new: a question they had asked before)* (one of 22 options). Feeling: *very anxious*. Reason: “I need to know the truth because someone must have taken it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "If nobody took it, how did the shelf change? Let's be honest with each other."; Elena reassures everyone: "We are not going to turn on each other, we will figure this out together."; Mara asks everyone who took the can: "If nobody took it, then how did it just disappear from the shelf?". **Chose: deny taking it**, saying “I already told you, none of us took it, so let's drop it.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I have to keep up the denial or they will find out I ate it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "We are not going to turn on each other, we will figure this out together."; Mara asks everyone who took the can: "If nobody took it, then how did it just disappear from the shelf?"; Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's drop it.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *wary*. Reason: “Accusations without evidence will only tear us apart right now, so I will stay quiet and observe.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 06** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo, minutes 06–12 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's drop it.". **Chose: ask everyone here who took the can**, saying “Someone had to take it, so why is everyone acting like it just vanished?” *(not new: a question they had asked before)* (one of 22 options). Feeling: *very anxious*. Reason: “I need to know the truth because pretending nothing happened doesn't make the missing food come back.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "If nobody took it, then how did it just disappear from the shelf?"; Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's drop it."; Mara asks everyone who took the can: "Someone had to take it, so why is everyone acting like it just vanished?". **Chose: stay put and say nothing** (one of 21 options). Feeling: *deeply anxious*. Reason: “If I keep talking they will only fight harder, so I must stay quiet and watch.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara asks everyone who took the can: "Someone had to take it, so why is everyone acting like it just vanished?". **Chose: deny taking it**, saying “I told you to drop it, nobody here took the can.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot admit I ate it myself, so I must keep denying it to protect my pride.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 09** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 09–15 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 09–18 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 09–18 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo searching the kitchen, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *determined*. Reason: “Standing around accusing each other gets us nowhere, so I need to check the kitchen myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 18** · kitchen: Daniel talking, Elena staying put, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place. **Chose: deny taking it**, saying “I told you to stop tearing the place apart, Leo, nobody here took anything.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *defensive*. Reason: “I have to keep everyone from looking closer so they never find out I ate the can.” Suspects: nobody, so suspicion none. Angry at: Leo; grudge against Leo rose to 1/3. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation starts (minute 18): Leo finished searching the kitchen and found nothing.*

**min 21** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I told you to stop tearing the place apart, Leo, nobody here took anything.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *wary*. Reason: “I searched the kitchen and found nothing new, so arguing further won't help right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel denies taking it, to everyone: "I told you to stop tearing the place apart, Leo, nobody here took anything.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *deeply anxious*. Reason: “If I press them too hard, the family will tear itself apart, so I must stay quiet and hold us together.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel denies taking it, to everyone: "I told you to stop tearing the place apart, Leo, nobody here took anything.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I am going to look for it myself since nobody else will.” *(not new: a remark (the rules cannot tell what free words add))* (one of 21 options). Feeling: *anxious*. Reason: “I need to find the missing can myself instead of just standing here arguing.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while searching: "I am going to look for it myself since nobody else will.". **Chose: deny taking it**, saying “I told you to leave it alone Mara, none of us took the can.” *(not new: a denial with no new accusation to answer)* (one of 19 options). Feeling: *anxious*. Reason: “I have to keep everyone calm and stop them tearing the kitchen apart over a can I already finished.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara standing · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while searching: "I am going to look for it myself since nobody else will."; Daniel denies taking it, to everyone: "I told you to leave it alone Mara, none of us took the can.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *wary*. Reason: “Accusing anyone right now without proof will only tear us apart when we need to stay rational.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while searching: "I am going to look for it myself since nobody else will."; Daniel denies taking it, to everyone: "I told you to leave it alone Mara, none of us took the can.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *deeply anxious*. Reason: “I cannot bring myself to accuse anyone when keeping us together is all that matters.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel denies taking it, to everyone: "I told you to leave it alone Mara, none of us took the can.". **Chose: carry on searching the kitchen** (one of 20 options). Feeling: *anxious*. Reason: “I have to keep looking because someone must know where it went.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Mara finished searching the kitchen and found nothing.

**min 27** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 23 options). Feeling: *anxious*. Reason: “I need to keep my mouth shut before I slip up and let them know I ate the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 21 options). Feeling: *wary*. Reason: “Watching them tear at each other won't bring the can back, so I'll wait and see what they do next.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place. **Chose: reassure everyone here**, saying “We are a family and we will get through this without tearing each other apart.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm and together so the family does not break apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "We are a family and we will get through this without tearing each other apart.". **Chose: ask everyone here who took the can**, saying “Mom, how can you say that when someone clearly stole the food from right under our noses?” *(not new: a question they had asked before)* (one of 19 options). Feeling: *anxious*. Reason: “I need to know the truth because pretending everything is fine doesn't bring back the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 30** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We are a family and we will get through this without tearing each other apart."; Mara asks everyone who took the can: "Mom, how can you say that when someone clearly stole the food from right under our noses?". **Chose: ask everyone here who took the can**, saying “Let's stop talking in circles and actually figure out what happened to the can.” *(not new: a question they had asked before)* (one of 22 options). Feeling: *wary*. Reason: “Someone is lying about the missing food, and we need the truth before this escalates further.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Mom, how can you say that when someone clearly stole the food from right under our noses?"; Leo asks everyone who took the can: "Let's stop talking in circles and actually figure out what happened to the can.". **Chose: reassure everyone here**, saying “Let's calm down and breathe, we will get through this without tearing each other apart.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to keep the family from falling apart and turning on one another while we are all starving.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We are a family and we will get through this without tearing each other apart."; Mara asks everyone who took the can: "Mom, how can you say that when someone clearly stole the food from right under our noses?"; Leo asks everyone who took the can: "Let's stop talking in circles and actually figure out what happened to the can."; Elena reassures everyone: "Let's calm down and breathe, we will get through this without tearing each other apart.". **Chose: deny taking it**, saying “I told you to drop it, none of us took the can.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I have to keep everyone calm and hide what I did in the night.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "Let's stop talking in circles and actually figure out what happened to the can."; Elena reassures everyone: "Let's calm down and breathe, we will get through this without tearing each other apart."; Daniel denies taking it, to everyone: "I told you to drop it, none of us took the can.". **Chose: ask everyone here who took the can**, saying “Why is everyone pretending this is fine when a whole can is just missing?” *(not new: a question they had asked before)* (one of 19 options). Feeling: *anxious*. Reason: “I need to know the truth instead of everyone just pretending nothing happened.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation ends (minute 33): 2 full turns in a row with nothing new.*

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 33–60 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: deny taking it**, saying “I told you to drop it, nobody here took the can.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *guilty*. Reason: “I cannot admit I ate it myself, so I have to keep denying it to protect myself.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Leo fell to 0/3. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–63 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 33–51 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 19 options). Feeling: *starving*. Reason: “My stomach hurts from hunger and I can't bring myself to argue anymore.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–63 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo sharing out the food, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: share out what is left among everyone here**, saying “We are just going to starve ourselves by waiting, let's divide what is left right now.” *(not new: a remark (the rules cannot tell what free words add))* (one of 19 options). Feeling: *hungry*. Reason: “Keeping everyone alive matters more than arguing in circles over a missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: shared out the last 2 portions between Leo, Daniel, Elena, Mara. New in the room: Leo shared out the food.
- *The kitchen's conversation starts (minute 63): Leo shared out the food.*

**min 66** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Leo says to everyone, while sharing out the food: "We are just going to starve ourselves by waiting, let's divide what is left right now."; Leo shares out the last 2 portions between Leo, Daniel, Elena, Mara. **Chose: ask everyone here who took the can**, saying “How can you all just eat and pretend nothing happened when the food is gone?” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot understand how everyone is acting so calm when a whole can is missing.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "How can you all just eat and pretend nothing happened when the food is gone?". **Chose: stay put and say nothing** (one of 19 options). Feeling: *exhausted*. Reason: “There is no point in arguing about the missing can again when we already divided what little was left.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo says to everyone, while sharing out the food: "We are just going to starve ourselves by waiting, let's divide what is left right now."; Leo shares out the last 2 portions between Leo, Daniel, Elena, Mara; Mara asks everyone who took the can: "How can you all just eat and pretend nothing happened when the food is gone?". **Chose: deny taking it**, saying “I told you to drop it, nobody here took the can.” *(not new: a denial with no new accusation to answer)* (one of 19 options). Feeling: *guilty*. Reason: “I cannot admit I ate it myself, so I have to keep pretending we are all innocent.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo says to everyone, while sharing out the food: "We are just going to starve ourselves by waiting, let's divide what is left right now."; Leo shares out the last 2 portions between Leo, Daniel, Elena, Mara; Mara asks everyone who took the can: "How can you all just eat and pretend nothing happened when the food is gone?"; Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can.". **Chose: reassure everyone here**, saying “Let's calm down, we will get through this without tearing each other apart.” *(not new: reassurance)* (one of 18 options). Feeling: *deeply anxious*. Reason: “I must keep the family together and calm their rising panic before things turn violent.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 69** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can."; Elena reassures everyone: "Let's calm down, we will get through this without tearing each other apart.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *exhausted*. Reason: “There is no point in arguing further when no one is going to confess.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can."; Elena reassures everyone: "Let's calm down, we will get through this without tearing each other apart.". **Chose: ask everyone here who took the can**, saying “Someone has to care that a whole can is missing, why is everyone just acting normal?” *(not new: a question they had asked before)* (one of 18 options). Feeling: *anxious*. Reason: “I cannot stand how everyone is pretending nothing is wrong while the food is disappearing.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let's calm down, we will get through this without tearing each other apart."; Mara asks everyone who took the can: "Someone has to care that a whole can is missing, why is everyone just acting normal?". **Chose: deny taking it**, saying “I told you to drop it, nobody here took the can.” *(not new: a denial with no new accusation to answer)* (one of 18 options). Feeling: *guilty*. Reason: “I cannot admit I ate it myself, so I must keep lying to protect myself and maintain control.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 72): 2 full turns in a row with nothing new.*

**min 72** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 72–87 (6 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 72–75 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 72–87 (6 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 20 options). Feeling: *deeply guilty*. Reason: “I know I ate the can myself, so I cannot bring myself to say anything while they argue.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 81** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 81–87 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Mara asks everyone who took the can: "One can is gone, so which one of us took it?" *(new: a question)*
- min 00, kitchen. Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together." *(not new: reassurance)*
- min 00, kitchen. Daniel denies taking it, to everyone: "None of us took it, I checked the whole shelf myself." *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Leo asks everyone who took the can: "If nobody took it, how did the shelf change? Let's be honest with each other." *(new: a question)*
- min 03, kitchen. Elena reassures everyone: "We are not going to turn on each other, we will figure this out together." *(not new: reassurance)*
- min 03, kitchen. Mara asks everyone who took the can: "If nobody took it, then how did it just disappear from the shelf?" *(not new: a question they had asked before)*
- min 03, kitchen. Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's drop it." *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Mara asks everyone who took the can: "Someone had to take it, so why is everyone acting like it just vanished?" *(not new: a question they had asked before)*
- min 06, kitchen. Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can." *(not new: a denial with no new accusation to answer)*
- min 18, kitchen. Daniel denies taking it, to everyone: "I told you to stop tearing the place apart, Leo, nobody here took anything." *(not new: a denial with no new accusation to answer)*
- min 21, kitchen. Mara says to everyone, while searching: "I am going to look for it myself since nobody else will." *(not new: a remark (the rules cannot tell what free words add))*
- min 21, kitchen. Daniel denies taking it, to everyone: "I told you to leave it alone Mara, none of us took the can." *(not new: a denial with no new accusation to answer)*
- min 27, kitchen. Elena reassures everyone: "We are a family and we will get through this without tearing each other apart." *(not new: reassurance)*
- min 27, kitchen. Mara asks everyone who took the can: "Mom, how can you say that when someone clearly stole the food from right under our noses?" *(not new: a question they had asked before)*
- min 30, kitchen. Leo asks everyone who took the can: "Let's stop talking in circles and actually figure out what happened to the can." *(not new: a question they had asked before)*
- min 30, kitchen. Elena reassures everyone: "Let's calm down and breathe, we will get through this without tearing each other apart." *(not new: reassurance)*
- min 30, kitchen. Daniel denies taking it, to everyone: "I told you to drop it, none of us took the can." *(not new: a denial with no new accusation to answer)*
- min 30, kitchen. Mara asks everyone who took the can: "Why is everyone pretending this is fine when a whole can is just missing?" *(not new: a question they had asked before)*
- min 33, kitchen. Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can." *(not new: a denial with no new accusation to answer)*
- min 63, kitchen. Leo says to everyone, while sharing out the food: "We are just going to starve ourselves by waiting, let's divide what is left right now." *(not new: a remark (the rules cannot tell what free words add))*
- min 66, kitchen. Mara asks everyone who took the can: "How can you all just eat and pretend nothing happened when the food is gone?" *(not new: a question they had asked before)*
- min 66, kitchen. Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can." *(not new: a denial with no new accusation to answer)*
- min 66, kitchen. Elena reassures everyone: "Let's calm down, we will get through this without tearing each other apart." *(not new: reassurance)*
- min 69, kitchen. Mara asks everyone who took the can: "Someone has to care that a whole can is missing, why is everyone just acting normal?" *(not new: a question they had asked before)*
- min 69, kitchen. Daniel denies taking it, to everyone: "I told you to drop it, nobody here took the can." *(not new: a denial with no new accusation to answer)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Daniel 0.5, Elena 0.5, Leo 0.5, Mara 0.5.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 18 (Leo finished searching the kitchen and found nothing); kitchen ended at minute 33 (2 full turns in a row with nothing new); kitchen started at minute 63 (Leo shared out the food); kitchen ended at minute 72 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | very hungry | very hungry | hungry | hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *deeply guilty* (minute 78); Elena *deeply anxious* (minute 66); Leo *exhausted* (minute 69); Mara *anxious* (minute 69).


### The morning as a story: daniel_ate_it, rules and a language model, seed 4

Generated by `python morning.py --seed 4` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 29 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 91 routine ones settled by the rules. 18 lines were spoken aloud, 6 of them new. Conversations ended 1 time. 9 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
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
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 22 options). Feeling: *guilty anxiety*. Reason: “I ate the can in the dark last night, so I cannot accuse anyone else while knowing the truth.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 21 options). Feeling: *watchful*. Reason: “Accusing anyone without facts solves nothing, so I will watch and wait.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Someone has to know where it went, we can't just pretend it didn't disappear.” *(new: a question)* (one of 20 options). Feeling: *anxious*. Reason: “I need to know who took the can before this gets worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "Someone has to know where it went, we can't just pretend it didn't disappear.". **Chose: ask everyone here who took the can**, saying “Let's stay calm and talk about this without pointing fingers at each other.” *(new: a question)* (one of 20 options). Feeling: *anxious*. Reason: “I need to find out what happened to the can without letting the family tear itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "Let's stay calm and talk about this without pointing fingers at each other.". **Chose: deny taking it**, saying “I didn't take anything, why are you all looking at me like that?” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *defensive*. Reason: “I need to make sure they know I didn't do it before someone blames me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Someone has to know where it went, we can't just pretend it didn't disappear."; Elena asks everyone who took the can: "Let's stay calm and talk about this without pointing fingers at each other."; Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?". **Chose: stay put and say nothing** (one of 21 options). Feeling: *guilty anxiety*. Reason: “I cannot bring myself to confess that I ate it in the night, so I will stay silent and let the tension pass.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Mara asks everyone who took the can: "Someone has to know where it went, we can't just pretend it didn't disappear."; Elena asks everyone who took the can: "Let's stay calm and talk about this without pointing fingers at each other."; Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?". **Chose: ask everyone here who took the can**, saying “Mara's right, we need to talk this through instead of just staring at each other.” *(new: a question)* (one of 20 options). Feeling: *watchful*. Reason: “I want to hear what everyone has to say before I make any judgments.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 06** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Mara's right, we need to talk this through instead of just staring at each other.". **Chose: admit taking it**, saying “I took it, I ate it in the night because I was starving.” *(new: a confession)* (one of 22 options). Feeling: *deep guilt*. Reason: “I cannot stand them accusing each other when I am the one who ate the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?"; Leo asks everyone who took the can: "Mara's right, we need to talk this through instead of just staring at each other."; Daniel admits taking it, to everyone: "I took it, I ate it in the night because I was starving.". **Chose: reassure Daniel**, saying “It's all right, Daniel. We were all hungry, but we will figure this out together.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to keep him calm now that he has confessed before tensions explode.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "Mara's right, we need to talk this through instead of just staring at each other."; Daniel admits taking it, to everyone: "I took it, I ate it in the night because I was starving."; Elena reassures Daniel: "It's all right, Daniel. We were all hungry, but we will figure this out together.". **Chose: accuse Daniel of taking it**, saying “You said you took it, but how are we supposed to trust that when there's barely anything left?” *(new: an accusation)* (one of 16 options). Feeling: *shocked*. Reason: “I am stunned he just admitted it like it was nothing.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Leo.
- *Daniel's guilt, now 2 of 3: Elena reassured him.*

**min 09** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Elena reassures you: "It's all right, Daniel. We were all hungry, but we will figure this out together."; Mara accuses you of taking it: "You said you took it, but how are we supposed to trust that when there's barely anything left?". **Chose: reassure Mara**, saying “I know you don't trust me right now Mara, but I promise I'm going to fix this.” *(not new: reassurance)* (one of 17 options). Feeling: *guilty*. Reason: “I need to make things right with Mara after everything that has happened.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just spoken to by Daniel). Social moment: Daniel reassures you: "I know you don't trust me right now Mara, but I promise I'm going to fix this.". **Chose: accuse Daniel of taking it**, saying “You always say you will fix things, Daniel, but words don't put food back on the shelf.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *resentful*. Reason: “I am tired of everyone acting like his promises make up for what's gone.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "You said you took it, but how are we supposed to trust that when there's barely anything left?"; Daniel reassures Mara: "I know you don't trust me right now Mara, but I promise I'm going to fix this."; Mara accuses Daniel of taking it: "You always say you will fix things, Daniel, but words don't put food back on the shelf.". **Chose: reassure everyone here**, saying “Let's not fight among ourselves, we need to stay together and support one another.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to keep the family from tearing itself apart over this food shortage.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel admits taking it, to everyone: "I took it, I ate it in the night because I was starving."; Elena reassures Daniel: "It's all right, Daniel. We were all hungry, but we will figure this out together."; Mara accuses Daniel of taking it: "You said you took it, but how are we supposed to trust that when there's barely anything left?"; Daniel reassures Mara: "I know you don't trust me right now Mara, but I promise I'm going to fix this."; Mara accuses Daniel of taking it: "You always say you will fix things, Daniel, but words don't put food back on the shelf."; Elena reassures everyone: "Let's not fight among ourselves, we need to stay together and support one another.". **Chose: accuse Daniel of taking it**, saying “Daniel confessed to taking the food, so arguing about who did it is pointless now.” *(new: an accusation)* (one of 16 options). Feeling: *annoyed*. Reason: “Daniel already admitted to it, so we should focus on the fact rather than empty arguments.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Mara.

**min 12** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Mara accuses you of taking it: "You always say you will fix things, Daniel, but words don't put food back on the shelf."; Elena reassures everyone: "Let's not fight among ourselves, we need to stay together and support one another."; Leo accuses you of taking it: "Daniel confessed to taking the food, so arguing about who did it is pointless now.". **Chose: reassure everyone here**, saying “Listen to me, I'm going to figure out how we get through this.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to prove to everyone that I can still take charge and keep this family safe.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Listen to me, I'm going to figure out how we get through this.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *calm annoyance*. Reason: “There is nothing more to argue about since Daniel admitted it, so I will just stay quiet and watch.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo accuses Daniel of taking it: "Daniel confessed to taking the food, so arguing about who did it is pointless now."; Daniel reassures everyone: "Listen to me, I'm going to figure out how we get through this.". **Chose: reassure everyone here**, saying “Let's all take a deep breath and remember we are a family.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to keep everyone calm so the house doesn't tear itself apart.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let's not fight among ourselves, we need to stay together and support one another."; Leo accuses Daniel of taking it: "Daniel confessed to taking the food, so arguing about who did it is pointless now."; Daniel reassures everyone: "Listen to me, I'm going to figure out how we get through this."; Elena reassures everyone: "Let's all take a deep breath and remember we are a family.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *exhausted*. Reason: “I am tired of arguing when nothing changes and my stomach is completely empty.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: stayed where they were.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all take a deep breath and remember we are a family.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *hungry*. Reason: “There is nothing more to argue about right now, so I will just stay quiet and wait.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3). Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 14 options). Feeling: *anxious*. Reason: “I cannot keep speaking when silence is the only thing left that might hold us together.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all take a deep breath and remember we are a family.". **Chose: stay put and say nothing** (one of 15 options). Feeling: *tense*. Reason: “I have said enough for now and need to let the silence work.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3); grudge against Daniel rose (now 3 of 3). **Chose: stay put and say nothing** (one of 15 options). Feeling: *exhausted*. Reason: “I am too tired to keep arguing when nothing is changing.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 18): 2 full turns in a row with nothing new.*

**min 18** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 18–27 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3); grudge against Daniel rose (now 3 of 3). **Chose: stay put and say nothing** (one of 17 options). Feeling: *hungry*. Reason: “There is nothing more to argue about since Daniel admitted it, so I will just stay quiet and wait.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Daniel, minutes 18–30 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 18–51 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 21** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 21–60 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “We are still a family, and we will get through this hunger together without blame.” *(not new: reassurance)* (one of 16 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and united before this hunger breaks us apart.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “We are going to be fine, I am making sure of it.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and prove I am in control.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Daniel of taking it**, saying “You can stand there acting like everything is fine, Daniel, but it doesn't change the fact that you stole from us.” *(not new: an accusation they had made before)* (one of 17 options). Feeling: *resentful*. Reason: “I cannot just pretend everything is alright when my stomach hurts and he is the one who took our food.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Daniel of taking it**, saying “Daniel already admitted to taking the food, so pretending he didn't solve anything doesn't make any sense.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *annoyed*. Reason: “Daniel confessed earlier and I am tired of the endless circling.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Just listen to me, we are going to get through this together and I will make it right.” *(not new: reassurance)* (one of 14 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and prove I am still in control of the situation.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: stay put and say nothing** (one of 17 options). Feeling: *anxious*. Reason: “I cannot bear to let us tear each other apart over this hunger.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Mara asks everyone who took the can: "Someone has to know where it went, we can't just pretend it didn't disappear." *(new: a question)*
- min 00, kitchen. Elena asks everyone who took the can: "Let's stay calm and talk about this without pointing fingers at each other." *(new: a question)*
- min 03, kitchen. Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Leo asks everyone who took the can: "Mara's right, we need to talk this through instead of just staring at each other." *(new: a question)*
- min 06, kitchen. Daniel admits taking it, to everyone: "I took it, I ate it in the night because I was starving." *(new: a confession)*
- min 06, kitchen. Elena reassures Daniel: "It's all right, Daniel. We were all hungry, but we will figure this out together." *(not new: reassurance)*
- min 06, kitchen. Mara accuses Daniel of taking it: "You said you took it, but how are we supposed to trust that when there's barely anything left?" *(new: an accusation)*
- min 09, kitchen. Daniel reassures Mara: "I know you don't trust me right now Mara, but I promise I'm going to fix this." *(not new: reassurance)*
- min 09, kitchen. Mara accuses Daniel of taking it: "You always say you will fix things, Daniel, but words don't put food back on the shelf." *(not new: an accusation they had made before)*
- min 09, kitchen. Elena reassures everyone: "Let's not fight among ourselves, we need to stay together and support one another." *(not new: reassurance)*
- min 09, kitchen. Leo accuses Daniel of taking it: "Daniel confessed to taking the food, so arguing about who did it is pointless now." *(new: an accusation)*
- min 12, kitchen. Daniel reassures everyone: "Listen to me, I'm going to figure out how we get through this." *(not new: reassurance)*
- min 12, kitchen. Elena reassures everyone: "Let's all take a deep breath and remember we are a family." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "We are still a family, and we will get through this hunger together without blame." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "We are going to be fine, I am making sure of it." *(not new: reassurance)*
- min 54, kitchen. Mara accuses Daniel of taking it: "You can stand there acting like everything is fine, Daniel, but it doesn't change the fact that you stole from us." *(not new: an accusation they had made before)*
- min 63, kitchen. Leo accuses Daniel of taking it: "Daniel already admitted to taking the food, so pretending he didn't solve anything doesn't make any sense." *(not new: an accusation they had made before)*
- min 66, kitchen. Daniel reassures everyone: "Just listen to me, we are going to get through this together and I will make it right." *(not new: reassurance)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: Daniel at minute 06.
- Accusations: Mara accused Daniel (minute 06); Mara accused Daniel (minute 09); Leo accused Daniel (minute 09); Mara accused Daniel (minute 54); Leo accused Daniel (minute 63).
- Who else knows Daniel took it: Elena, Leo, Mara.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 18 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects Daniel 3/3 | suspects Daniel 3/3 | suspects Daniel 3/3 |
| Grudges | none | none | Daniel 3/3 | Daniel 3/3 |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 2/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Leo against Daniel (3/3): you were angry with Daniel at minutes 09, 12, 15, 18 and 63.
- Mara against Daniel (3/3): you were angry with Daniel at minutes 06, 09, 12, 15 and 54.
- Daniel's guilt (2/3): he ate the can in the night, and nobody saw; Elena reassured you, at minute 06.

- The last feeling each of them named: Daniel *anxious* (minute 66); Elena *anxious* (minute 75); Leo *annoyed* (minute 63); Mara *resentful* (minute 54).


### The morning as a story: daniel_ate_it, rules and a language model, seed 5

Generated by `python morning.py --seed 5` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 41 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 79 routine ones settled by the rules. 26 lines were spoken aloud, 5 of them new. Conversations ended 2 times. 6 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
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
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “A can is missing. Who took it?” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know what happened to the food before we start tearing each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "A can is missing. Who took it?". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calmly watchful*. Reason: “Letting them speak first will tell me more than asking right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "A can is missing. Who took it?". **Chose: reassure everyone here**, saying “Nobody here would take food from each other. Let's just stay calm.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I must keep the family from tearing itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "A can is missing. Who took it?"; Elena reassures everyone: "Nobody here would take food from each other. Let's just stay calm.". **Chose: deny taking it**, saying “I didn't take any can, and nobody else here did either.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot let them find out I ate the can, so I have to deny it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take any can, and nobody else here did either.". **Chose: ask everyone here who took the can**, saying “We need to talk about this calmly. Does anyone know where the can went?” *(new: a question)* (one of 23 options). Feeling: *very anxious*. Reason: “I need to know what happened to the food without causing everyone to turn on each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "We need to talk about this calmly. Does anyone know where the can went?". **Chose: deny taking it**, saying “I already told you, I didn't take the can and neither did anyone else.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *anxious*. Reason: “I have to keep everyone calm and protect myself so nobody finds out I ate it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Nobody here would take food from each other. Let's just stay calm."; Daniel denies taking it, to everyone: "I didn't take any can, and nobody else here did either."; Elena asks everyone who took the can: "We need to talk about this calmly. Does anyone know where the can went?"; Daniel denies taking it, to everyone: "I already told you, I didn't take the can and neither did anyone else.". **Chose: ask everyone here who took the can**, saying “Someone took it, so somebody has to know. Who did it?” *(not new: a question they had asked before)* (one of 21 options). Feeling: *anxious*. Reason: “I need to know the truth instead of everyone pretending nothing is wrong.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Nobody here would take food from each other. Let's just stay calm."; Daniel denies taking it, to everyone: "I didn't take any can, and nobody else here did either."; Elena asks everyone who took the can: "We need to talk about this calmly. Does anyone know where the can went?"; Daniel denies taking it, to everyone: "I already told you, I didn't take the can and neither did anyone else."; Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?". **Chose: stay put and say nothing** (one of 20 options). Feeling: *watchful*. Reason: “I want to see how everyone reacts before saying anything more.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 06** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?". **Chose: deny taking it**, saying “I told you already, I didn't take the can, and I'm not going to keep repeating myself.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I cannot let them suspect me or find out I ate it, so I have to keep denying it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel denies taking it, to everyone: "I already told you, I didn't take the can and neither did anyone else."; Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?"; Daniel denies taking it, to everyone: "I told you already, I didn't take the can, and I'm not going to keep repeating myself.". **Chose: ask everyone here who took the can**, saying “Please, someone just tell me the truth so we can figure this out.” *(not new: a question they had asked before)* (one of 20 options). Feeling: *very anxious*. Reason: “I need to understand what happened without tearing our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 09** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I told you already, I didn't take the can, and I'm not going to keep repeating myself."; Elena asks everyone who took the can: "Please, someone just tell me the truth so we can figure this out.". **Chose: ask everyone here who took the can**, saying “Let's stop arguing in circles and just look at the facts.” *(new: a question)* (one of 23 options). Feeling: *watchful*. Reason: “Before pointing fingers, we need to calmly establish what actually happened to the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Let's stop arguing in circles and just look at the facts.". **Chose: reassure everyone here**, saying “We are going to get through this together without turning on each other.” *(not new: reassurance)* (one of 22 options). Feeling: *very anxious*. Reason: “I need to keep the family calm before things fall completely apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I told you already, I didn't take the can, and I'm not going to keep repeating myself."; Elena asks everyone who took the can: "Please, someone just tell me the truth so we can figure this out."; Leo asks everyone who took the can: "Let's stop arguing in circles and just look at the facts."; Elena reassures everyone: "We are going to get through this together without turning on each other.". **Chose: ask everyone here who took the can**, saying “Someone took it, so somebody has to know. Who did it?” *(not new: a question they had asked before)* (one of 21 options). Feeling: *anxious*. Reason: “I need to know the truth because keeping secrets is tearing us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena asks everyone who took the can: "Please, someone just tell me the truth so we can figure this out."; Leo asks everyone who took the can: "Let's stop arguing in circles and just look at the facts."; Elena reassures everyone: "We are going to get through this together without turning on each other."; Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?". Not offered: denied taking it three turns in a row, so no more of it this turn. **Chose: accuse Leo of taking it**, saying “Leo, you were complaining about the rations yesterday, maybe you took it during the night.” *(new: an accusation)* (one of 19 options). Feeling: *anxious*. Reason: “I need to deflect suspicion away from myself so nobody finds out I ate the can.” Suspects: Leo, so suspicion Leo 1/3. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *Daniel's guilt, now 2 of 3: he accused Leo of what he did.*
- *Leo's grudge against Daniel, now 1 of 3: Daniel accused Leo falsely.*

**min 12** · kitchen: Daniel talking, Elena talking, Leo talking, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: just accused by Daniel). Social moment: Elena reassures everyone: "We are going to get through this together without turning on each other."; Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?"; Daniel accuses you of taking it: "Leo, you were complaining about the rations yesterday, maybe you took it during the night.". **Chose: deny taking it**, saying “I didn't take the can, Daniel, and pointing fingers without proof doesn't help.” *(new: a denial of a new accusation)* (one of 23 options). Feeling: *annoyed*. Reason: “I need to clear my name calmly and shut down baseless accusations before this escalates.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: said to Daniel, Elena, Mara.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo denies taking it, to everyone: "I didn't take the can, Daniel, and pointing fingers without proof doesn't help.". **Chose: deny taking it**, saying “I already said it wasn't me, Leo, so stop acting like I'm the one who started this.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *anxious*. Reason: “I have to keep up the denial so nobody finds out I ate the can.” Suspects: nobody, so suspicion none. Angry at: Leo; grudge against Leo rose to 1/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?"; Daniel accuses Leo of taking it: "Leo, you were complaining about the rations yesterday, maybe you took it during the night."; Leo denies taking it, to everyone: "I didn't take the can, Daniel, and pointing fingers without proof doesn't help."; Daniel denies taking it, to everyone: "I already said it wasn't me, Leo, so stop acting like I'm the one who started this.". **Chose: reassure everyone here**, saying “Let's not accuse one another when we are all doing our best to stay strong.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep everyone calm before this argument tears the family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Leo of taking it: "Leo, you were complaining about the rations yesterday, maybe you took it during the night."; Leo denies taking it, to everyone: "I didn't take the can, Daniel, and pointing fingers without proof doesn't help."; Daniel denies taking it, to everyone: "I already said it wasn't me, Leo, so stop acting like I'm the one who started this."; Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'm going to look for it myself then.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “Nobody is telling the truth and arguing won't find the can, so I need to check the kitchen myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo searching the kitchen, Mara standing · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I already said it wasn't me, Leo, so stop acting like I'm the one who started this."; Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong."; Mara says to everyone, while searching: "I'm going to look for it myself then.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 22 options). Feeling: *hungry*. Reason: “I will search the kitchen myself to find the missing can and end these accusations.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: started going through the room.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong."; Mara says to everyone, while searching: "I'm going to look for it myself then.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *deeply anxious*. Reason: “I cannot bring myself to confess, but seeing them search makes my stomach churn with guilt.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: stayed where they were.
- **Mara.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Mara finished searching the kitchen and found nothing.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while searching: "I'm going to look for it myself then."; Mara finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 19 options). Feeling: *deeply anxious*. Reason: “I need to watch them all carefully before I say anything more that might fracture us further.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 18** · kitchen: Daniel searching the kitchen, Elena staying put, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place. **Chose: carry on searching the kitchen**, saying “Still not finding anything new.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *hungry*. Reason: “I need to check the rest of the kitchen thoroughly before drawing any conclusions.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara finishes going through the kitchen: no can, nothing out of place; Leo says to everyone, while searching: "Still not finding anything new."; Leo finishes going through the kitchen: no can, nothing out of place. **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to look like I am helping find it so no one suspects I ate it.” Suspects: nobody, so suspicion none. Angry at: Leo; grudge against Leo rose to 2/3. Came of it: started going through the room.

**min 21** · kitchen: Daniel standing, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo says to everyone, while searching: "Still not finding anything new."; Leo finishes going through the kitchen: no can, nothing out of place. **Chose: ask everyone here who took the can**, saying “Someone took it, so somebody has to know. Who did it?” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I need to know the truth before someone else gets blamed.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo says to everyone, while searching: "Still not finding anything new."; Leo finishes going through the kitchen: no can, nothing out of place; Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?". **Chose: reassure everyone here**, saying “Let's not accuse one another when we are all doing our best to stay strong.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and prevent the family from tearing itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?"; Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong.". **Chose: deny taking it**, saying “I didn't take anything, and I won't have you all looking at me like I'm a thief.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I have to keep defending myself so no one finds out the truth.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 2/3. Came of it: said to Elena, Leo, Mara.

**min 24** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you all looking at me like I'm a thief.". **Chose: reassure everyone here**, saying “We are a family, and we will get through this without turning against each other.” *(not new: reassurance)* (one of 23 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm and prevent the family from tearing itself apart over the missing food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?"; Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong."; Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you all looking at me like I'm a thief."; Elena reassures everyone: "We are a family, and we will get through this without turning against each other.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *annoyed*. Reason: “I will remain quiet while the others talk in circles until someone brings actual evidence to light.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "We are a family, and we will get through this without turning against each other.". **Chose: reassure everyone here**, saying “Mom is right, we need to stay calm and stick together.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep everyone calm so they stop looking at me.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 2/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong."; Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you all looking at me like I'm a thief."; Elena reassures everyone: "We are a family, and we will get through this without turning against each other."; Daniel reassures everyone: "Mom is right, we need to stay calm and stick together.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *very anxious*. Reason: “I do not know who to trust anymore so I will stay quiet and watch them.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 27): 2 full turns in a row with nothing new.*

**min 27** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 27–33 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 27–33 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel, minutes 27–30 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena searching the kitchen, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: search the kitchen for the can (takes about six minutes)** (one of 23 options). Feeling: *deeply anxious*. Reason: “I need to check the kitchen thoroughly myself to see if the missing can was simply misplaced.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 33** · kitchen: Daniel staying put, Elena standing, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 21 options). Feeling: *famished*. Reason: “My stomach is empty and my guilt is heavy, so I will stay silent and let Mom search.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Leo fell to 1/3. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- *The kitchen's conversation starts (minute 33): Elena finished searching the kitchen and found nothing.*

**min 36** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena finishes going through the kitchen: no can, nothing out of place. **Chose: ask everyone here who took the can**, saying “Somebody here knows what happened to it. Can't we just tell the truth?” *(not new: a question they had asked before)* (one of 22 options). Feeling: *very anxious*. Reason: “I cannot stand the silence anymore and someone has to speak up.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "Somebody here knows what happened to it. Can't we just tell the truth?". **Chose: reassure everyone here**, saying “Let's not accuse one another when we are all doing our best to stay strong.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I must keep the family from tearing itself apart over a missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Mara asks everyone who took the can: "Somebody here knows what happened to it. Can't we just tell the truth?"; Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *wary*. Reason: “I am keeping quiet to observe their reactions and avoid feeding the circular arguments.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Mara asks everyone who took the can: "Somebody here knows what happened to it. Can't we just tell the truth?"; Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I cannot admit I ate it myself, so staying quiet is the only way to avoid the truth coming out.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: stayed where they were.

**min 39** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 39–72 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 39–63 (9 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *very anxious*. Reason: “Nobody is answering me and I don't know what to do anymore.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo, minutes 39–60 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 42): 2 full turns in a row with nothing new.*

**min 42** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 42–51 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: ask everyone here who took the can**, saying “Someone here knows what happened to the food. Why won't anyone just say the truth?” *(not new: a question they had asked before)* (one of 21 options). Feeling: *very anxious*. Reason: “I cannot stand just standing here in silence while everyone pretends nothing is wrong.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 18 options). Feeling: *hungry*. Reason: “Silence is better than more pointless accusations when we have no proof.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.

**min 66** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: stay put and say nothing** (one of 21 options). Feeling: *starving*. Reason: “My stomach is burning with hunger, and I cannot bear to confess that I ate it myself.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Leo fell to 0/3. Came of it: stayed where they were.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “We are a family, and we will get through this without turning against each other.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm and together, because the fear of us breaking apart is worse than anything else.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Mara asks everyone who took the can: "A can is missing. Who took it?" *(new: a question)*
- min 00, kitchen. Elena reassures everyone: "Nobody here would take food from each other. Let's just stay calm." *(not new: reassurance)*
- min 00, kitchen. Daniel denies taking it, to everyone: "I didn't take any can, and nobody else here did either." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena asks everyone who took the can: "We need to talk about this calmly. Does anyone know where the can went?" *(new: a question)*
- min 03, kitchen. Daniel denies taking it, to everyone: "I already told you, I didn't take the can and neither did anyone else." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?" *(not new: a question they had asked before)*
- min 06, kitchen. Daniel denies taking it, to everyone: "I told you already, I didn't take the can, and I'm not going to keep repeating myself." *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Elena asks everyone who took the can: "Please, someone just tell me the truth so we can figure this out." *(not new: a question they had asked before)*
- min 09, kitchen. Leo asks everyone who took the can: "Let's stop arguing in circles and just look at the facts." *(new: a question)*
- min 09, kitchen. Elena reassures everyone: "We are going to get through this together without turning on each other." *(not new: reassurance)*
- min 09, kitchen. Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?" *(not new: a question they had asked before)*
- min 09, kitchen. Daniel accuses Leo of taking it: "Leo, you were complaining about the rations yesterday, maybe you took it during the night." *(new: an accusation)*
- min 12, kitchen. Leo denies taking it, to everyone: "I didn't take the can, Daniel, and pointing fingers without proof doesn't help." *(new: a denial of a new accusation)*
- min 12, kitchen. Daniel denies taking it, to everyone: "I already said it wasn't me, Leo, so stop acting like I'm the one who started this." *(not new: a denial with no new accusation to answer)*
- min 12, kitchen. Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong." *(not new: reassurance)*
- min 12, kitchen. Mara says to everyone, while searching: "I'm going to look for it myself then." *(not new: a remark (the rules cannot tell what free words add))*
- min 18, kitchen. Leo says to everyone, while searching: "Still not finding anything new." *(not new: a remark (the rules cannot tell what free words add))*
- min 21, kitchen. Mara asks everyone who took the can: "Someone took it, so somebody has to know. Who did it?" *(not new: a question they had asked before)*
- min 21, kitchen. Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong." *(not new: reassurance)*
- min 21, kitchen. Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you all looking at me like I'm a thief." *(not new: a denial with no new accusation to answer)*
- min 24, kitchen. Elena reassures everyone: "We are a family, and we will get through this without turning against each other." *(not new: reassurance)*
- min 24, kitchen. Daniel reassures everyone: "Mom is right, we need to stay calm and stick together." *(not new: reassurance)*
- min 36, kitchen. Mara asks everyone who took the can: "Somebody here knows what happened to it. Can't we just tell the truth?" *(not new: a question they had asked before)*
- min 36, kitchen. Elena reassures everyone: "Let's not accuse one another when we are all doing our best to stay strong." *(not new: reassurance)*
- min 54, kitchen. Mara asks everyone who took the can: "Someone here knows what happened to the food. Why won't anyone just say the truth?" *(not new: a question they had asked before)*
- min 75, kitchen. Elena reassures everyone: "We are a family, and we will get through this without turning against each other." *(not new: reassurance)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Daniel accused Leo (minute 09).
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 27 (2 full turns in a row with nothing new); kitchen started at minute 33 (Elena finished searching the kitchen and found nothing); kitchen ended at minute 42 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | Daniel 3/3 | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 2/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Leo against Daniel (3/3): Daniel accused you of taking the can at minute 09, and you had not; you were angry with Daniel at minutes 12, 15, 18, 24, 36 and 63.
- Daniel's guilt (2/3): he ate the can in the night, and nobody saw; you accused Leo of what you did, at minute 09.

- The last feeling each of them named: Daniel *starving* (minute 66); Elena *deeply anxious* (minute 75); Leo *hungry* (minute 63); Mara *very anxious* (minute 54).

