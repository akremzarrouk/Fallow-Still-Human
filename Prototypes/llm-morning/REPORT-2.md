# LLM morning prototype, step 2: sequential conversation

The people in a room now act one after another within a turn. Each one sees what was already said there, and who it was aimed at. A speech act used three turns in a row is not offered a fourth time, and a room's conversation ends after a full turn with nothing new. The first report, [REPORT.md](REPORT.md), and its runs in `runs/` are left as they were; this step's runs are in `runs/v2/`. Model: `gemini-3.5-flash-lite`, unchanged.

## Done when

| Condition | Result |
|---|---|
| all tests pass | 27 of 27, against the fake model and a stubbed API |
| 3 fresh mornings (seeds 1, 2, 3) under 150 real calls each | 7, 25, 11 API requests; all reached minute 90 |
| `--replay` of seed 1 byte-identical with 0 calls | IDENTICAL, 0 API requests, run with `GEMINI_API_KEY` unset; `cmp` and SHA-256 agree |
| REPORT-2.md has the metrics table for old and new runs | below |

## Metrics

| Run | Model calls | Lines spoken | Longest run of one speech act by one person | Lines that answer the line before them | Conversations ended (room, minute) | Daniel confessed | References to things not in the house |
|---|---|---|---|---|---|---|---|
| old, seed 1 | 120 | 76 | 14 (Daniel, reassure, min 48–87) | 13/74 (18%) | kitchen 24; kitchen 48; brothers room 60; brothers room 72 | yes, min 42 | 0 |
| old, seed 2 | 39 | 24 | 4 (Daniel, deny, min 15–24) | 3/23 (13%) | kitchen 09; kitchen 27 | no | 2 |
| old, seed 3 | 90 | 53 | 7 (Elena, reassure, min 21–39) | 9/51 (18%) | kitchen 18; kitchen 24; brothers room 45; brothers room 51; brothers room 60 | yes, min 18 | 0 |
| new, seed 1 | 7 | 6 | 1 (Daniel, accuse, min 00–00) | 3/5 (60%) | kitchen 06 | no | 1 |
| new, seed 2 | 25 | 13 | 3 (Daniel, accuse, min 03–09) | 3/11 (27%) | kitchen 12; kitchen 18; back room 27 | no | 0 |
| new, seed 3 | 11 | 8 | 3 (Daniel, deny, min 00–06) | 6/7 (86%) | kitchen 09 | no | 0 |

The same code, `metrics.py`, computes every column for both versions from the runs' transcripts. For the old runs, the frozen first-version code in `v1/` replays each morning from its cache (0 API calls). Each replayed story comes out byte-identical to the one in `runs/`, so the old transcripts are exact.

- **Model calls**: decisions the model made. In all six runs this equals the API requests; there were no retries.
- **Lines spoken**: every line said aloud, including a line said while doing something else.
- **Longest run of one speech act**: the most turns in a row one person used the same kind of speech act. The kinds are ask, deny, accuse, confess, reassure and say something else; reassuring one person or everyone counts as one kind, and so does accusing anyone.
- **Lines that answer the line before them**: counts only lines with an earlier line in the same room. A line answers that earlier line when its speaker had heard it before choosing, and the line either:
  - is aimed at the earlier speaker,
  - comes from the person the earlier line was aimed at,
  - joins an accusation against the same person,
  - answers a question with a denial, confession or accusation, or
  - answers a denial with a question or accusation.

  In the old runs everyone chose at once, so nobody had heard a line from their own turn; only a line answering the previous turn's last line could count.
- **Conversations ended**: the minute a room's conversation ended, by the rule in `talk.py`: a full turn with nothing new, or fewer than two people left in the room. The minute is the end of the quiet turn. The old code had no such rule; for the old runs it is applied after the fact to their transcripts. A room can end, start again (something new) and end again.
- **Daniel confessed**: the minute he chose to admit it.
- **References to things not in the house**: words in spoken lines naming a thing or place the house does not have (the list is `NOT_IN_HOUSE` in `metrics.py`, built by reading every line of the six runs). Every hit:

- old, seed 2, min 09, Daniel: "pockets" in “Check his pockets, he's the one who's been acting shady this whole time.”
- old, seed 2, min 12, Daniel: "jacket" in “Open your jacket again Leo, you're hiding something and I know it.”
- new, seed 1, min 00, Daniel: "pockets" in “Check your own pockets, Leo, before you start looking at the rest of us.”

*Correction to REPORT.md:* it said the model invented "checking the front window" and "a door to knock on". Both are in the house: the backstory has Daniel boarding the front windows and Mara in the front doorway, and the new list of the house's things includes them. The jacket and the pockets were real inventions. REPORT.md itself is left unedited.

## What stands out

These are observations; the judge is a person reading the stories below.

- **People now answer each other.** In seed 1, Daniel accuses Leo; Leo, just accused, goes next and denies ("I didn't take it, Daniel. Check yours."). Elena asks who took it, and Mara answers "I didn't take it, Mom!". In seeds 1 and 3, 3 of 5 and 6 of 7 lines answer the line before them, against 13% to 18% in the old runs. Seed 2 scores 3 of 11. The misses are Mara's remarks while searching, a denial after a denial, a question after an accusation, and reassurance.
- **Repetition is capped.** No speech act runs past three turns: Daniel's accusations of Leo stop at three in seed 2. In the old runs the longest runs were 14, 4 and 7 turns.
- **Talk runs out almost at once.** The kitchen's conversation ended at minute 6 (seed 1) and minute 9 (seed 3). In seed 2 it lasted to minute 18, plus a short back-room conversation until minute 27. After that nothing new happens in any room, so nobody is asked again. The last 84, 63 and 81 minutes are everyone staying put in silence: the target's Never item "Long stretches where everyone does nothing". Three rules end the talk this fast:
  - a denial is new only if it answers a new accusation, so everyone's first "I didn't take it" in reply to a question is not new;
  - reassurance is never new;
  - "say something else" is never new, because the rules cannot read what free words add.

  Once people stay put, nothing in the rules makes anything new; hunger triggers and other activities are later steps.
- **Daniel never confesses.** He confessed in two of the three old runs, at minutes 18 and 42, after long questioning. Here the talk ends before that pressure builds. His deflections vary more than before:
  - seed 1: he blames Leo at once;
  - seed 2: he blames Leo three times;
  - seed 3: "it must have been an inventory mistake".
- **Forms of address.** No child calls Elena by name in the new lines; the one time a child speaks to her directly, Mara says "Mom". In the old runs Leo once called her "Elena". One thing outside the house appears ("Check your own pockets"), against two in the old runs.
- **Cost.** 43 model calls for three mornings, against 249 in the old runs. The largest prompt was 1,370 tokens by the API's own count.

Nothing here was tuned after seeing the runs. Ways to let talk last longer would change the rules you set, so they are yours to choose. For example: end a conversation after two quiet turns instead of one, count a person's first denial as new, or let a line that names someone new count.

## Changes beyond the brief, and why

- **`target-morning.md` was not changed.** The four "Never" lines were already in the list, word for word (lines 33 to 36). Appending them again would have duplicated them.
- **`CLAUDE.md` did not exist.** I created it at the repo root, holding only the requested line.
- **New files for measuring:**
  - `talk.py` holds the newness and conversation rules, shared by the simulation and the metrics, so old and new runs are judged by the same code;
  - `metrics.py` builds the table;
  - `v1/` is a frozen copy of the first version's code;
  - `v1/transcript.py` replays the old mornings from their caches with that copy, checks each story is byte-identical, and writes their transcripts.

  A test also checks that the metrics work out the same conversations as the simulation. It passes on five fake mornings, and a replay confirms the same for the three real runs.
- **This version writes to `runs/v2/` and `cache/v2/`**, so the old stories, caches and REPORT.md stay as they were. Each fresh run also writes a `.transcript.json` for the metrics.
- **Interpretations the brief left open:**
  - A stance (a question, or accusing a given person) is new only the first time that person takes it in the morning, in any room.
  - "Say something else" and a line said while doing something else are never new: the rules cannot read free words.
  - A finished search that others see counts as a new fact. So do food eaten or shared in front of others and someone coming into an occupied room. Each of these is now a social moment for those who see it; before, a finished search and an arrival were not.
  - Sitting with someone and looking upset stay social moments only while the room is talking.
  - "Strongest shown feeling" uses a fixed scale of the feeling words that show on a face (scared 2, terrified 3, "very" or "deeply" adds 1). Inward feelings (guilty, anxious...) count 0.
  - Among people who were spoken to, the most recently addressed goes first. The order within a room is worked out again after every act, so someone accused mid-turn answers next.
  - "Whether anyone responded differently" covers the lines aimed at the person or at everyone since their current run began. It names anyone whose kind of reply changed.
- **Voices through walls.** They now reach the other rooms at the end of the turn, including someone who left mid-turn. Only a new line is a social moment for someone hearing it through a wall; otherwise a quiet room would be kept "talking" by the next room.
- **Prompt budget.** Raised from about 1,250 to about 1,400 estimated tokens, to fit the turn so far, the pattern lines, the forms of address and the house list. The API counted at most 1,370. The prompt-size test now checks the calibrated estimate (under 1,450) instead of my earlier, stricter one-token-per-3-characters bound.
- **Test adjustments.** The call-cap and daily-quota tests now trip within minute 0, since a v2 morning can use very few calls. The fake model reads option ids only from the options block, since the new pattern lines could look like options.

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
test_a_conversation_ends_after_a_full_turn_with_nothing_new (test_morning.SequentialTalkTest.test_a_conversation_ends_after_a_full_turn_with_nothing_new) ... ok
test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again (test_morning.SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again) ... ok
test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn (test_morning.SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn) ... ok
test_metrics_work_out_the_same_conversations_as_the_morning (test_morning.SequentialTalkTest.test_metrics_work_out_the_same_conversations_as_the_morning) ... ok
test_no_speech_act_runs_past_three_turns_in_any_fake_morning (test_morning.SequentialTalkTest.test_no_speech_act_runs_past_three_turns_in_any_fake_morning) ... ok
test_something_new_starts_it_again (test_morning.SequentialTalkTest.test_something_new_starts_it_again) ... ok
test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to (test_morning.SequentialTalkTest.test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to) ... ok
test_the_one_just_accused_acts_next (test_morning.SequentialTalkTest.test_the_one_just_accused_acts_next) ... ok
test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house (test_morning.SequentialTalkTest.test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house) ... ok
test_ties_are_broken_by_the_seed (test_morning.SequentialTalkTest.test_ties_are_broken_by_the_seed) ... ok

----------------------------------------------------------------------
Ran 27 tests in 2.958s

OK
```

### The old runs' transcripts, from the frozen first version

```bash
env -u GEMINI_API_KEY python v1/transcript.py
```

```
seed 1: replayed 120 answers from the cache, 0 API calls; story IDENTICAL to runs/daniel_ate_it-seed1.md; wrote runs\daniel_ate_it-seed1.transcript.json
seed 2: replayed 39 answers from the cache, 0 API calls; story IDENTICAL to runs/daniel_ate_it-seed2.md; wrote runs\daniel_ate_it-seed2.transcript.json
seed 3: replayed 90 answers from the cache, 0 API calls; story IDENTICAL to runs/daniel_ate_it-seed3.md; wrote runs\daniel_ate_it-seed3.transcript.json
```

### Fresh morning, seed 1

```bash
python morning.py --seed 1
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v2\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 3; so far 7 live, 0 cached, 7 API requests

wrote runs/v2/daniel_ate_it-seed1.md
  api_requests: 7
  answers_live: 7
  answers_from_cache: 0
  model_decisions: 7
  fallbacks: 0
  routine_decisions: 113
  lines_spoken: 6
  max_prompt_tokens_estimated: 1392
  max_prompt_tokens_counted_by_api: 1359
  run_seconds: 28.1
  story_sha256: de2085ad6670612528bc7796242d69e560eed86342f3f59c6c1d7fc65f734a33
```

### Fresh morning, seed 2

```bash
python morning.py --seed 2
```

```
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v2\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 2; so far 18 live, 0 cached, 18 API requests
  min 15: model asked for 3; so far 21 live, 0 cached, 21 API requests
  min 18: model asked for 2; so far 23 live, 0 cached, 23 API requests
  min 21: model asked for 1; so far 24 live, 0 cached, 24 API requests
  min 24: model asked for 1; so far 25 live, 0 cached, 25 API requests

wrote runs/v2/daniel_ate_it-seed2.md
  api_requests: 25
  answers_live: 25
  answers_from_cache: 0
  model_decisions: 25
  fallbacks: 0
  routine_decisions: 95
  lines_spoken: 13
  max_prompt_tokens_estimated: 1399
  max_prompt_tokens_counted_by_api: 1370
  run_seconds: 109.3
  story_sha256: 45df43954d0521fb1df4d40c5f45e60516ed951f0e04a2f2aa35ad6bc7bf104d
```

### Fresh morning, seed 3

```bash
python morning.py --seed 3
```

```
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v2\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 3; so far 11 live, 0 cached, 11 API requests

wrote runs/v2/daniel_ate_it-seed3.md
  api_requests: 11
  answers_live: 11
  answers_from_cache: 0
  model_decisions: 11
  fallbacks: 0
  routine_decisions: 109
  lines_spoken: 8
  max_prompt_tokens_estimated: 1399
  max_prompt_tokens_counted_by_api: 1352
  run_seconds: 46.2
  story_sha256: 1d274085ac833d0a8bf9747a0817147509ffe4783e740677507254d7c6818295
```

Run times: seed 1 28 s, seed 2 109 s, seed 3 46 s. Real generate requests in this Pacific-time quota day: 298 from the first step plus 43 here, 341 of 500.

### Replay of seed 1 (key unset, cache only)

```bash
env -u GEMINI_API_KEY python morning.py --seed 1 --replay
cmp runs/v2/daniel_ate_it-seed1.md runs/v2/daniel_ate_it-seed1.replay.md && echo "cmp: identical"
sha256sum runs/v2/daniel_ate_it-seed1.md runs/v2/daniel_ate_it-seed1.replay.md
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, replay from cache only; cache cache\v2\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 7 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 3; so far 0 live, 7 cached, 0 API requests

wrote runs/v2/daniel_ate_it-seed1.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 7
  model_decisions: 7
  fallbacks: 0
  routine_decisions: 113
  lines_spoken: 6
  max_prompt_tokens_estimated: 1392
  max_prompt_tokens_counted_by_api: 1359
  run_seconds: 0.0
  story_sha256: de2085ad6670612528bc7796242d69e560eed86342f3f59c6c1d7fc65f734a33
  byte for byte against runs\v2\daniel_ate_it-seed1.md: IDENTICAL
```

```
cmp: identical
de2085ad6670612528bc7796242d69e560eed86342f3f59c6c1d7fc65f734a33 *runs/v2/daniel_ate_it-seed1.md
de2085ad6670612528bc7796242d69e560eed86342f3f59c6c1d7fc65f734a33 *runs/v2/daniel_ate_it-seed1.replay.md
```

### Metrics

```bash
python metrics.py
```

```
| Run | Model calls | Lines spoken | Longest run of one speech act by one person | Lines that answer the line before them | Conversations ended (room, minute) | Daniel confessed | References to things not in the house |
|---|---|---|---|---|---|---|---|
| old, seed 1 | 120 | 76 | 14 (Daniel, reassure, min 48–87) | 13/74 (18%) | kitchen 24; kitchen 48; brothers room 60; brothers room 72 | yes, min 42 | 0 |
| old, seed 2 | 39 | 24 | 4 (Daniel, deny, min 15–24) | 3/23 (13%) | kitchen 09; kitchen 27 | no | 2 |
| old, seed 3 | 90 | 53 | 7 (Elena, reassure, min 21–39) | 9/51 (18%) | kitchen 18; kitchen 24; brothers room 45; brothers room 51; brothers room 60 | yes, min 18 | 0 |
| new, seed 1 | 7 | 6 | 1 (Daniel, accuse, min 00–00) | 3/5 (60%) | kitchen 06 | no | 1 |
| new, seed 2 | 25 | 13 | 3 (Daniel, accuse, min 03–09) | 3/11 (27%) | kitchen 12; kitchen 18; back room 27 | no | 0 |
| new, seed 3 | 11 | 8 | 3 (Daniel, deny, min 00–06) | 6/7 (86%) | kitchen 09 | no | 0 |

References to things not in the house:
- old, seed 2, min 09, Daniel: "pockets" in “Check his pockets, he's the one who's been acting shady this whole time.”
- old, seed 2, min 12, Daniel: "jacket" in “Open your jacket again Leo, you're hiding something and I know it.”
- new, seed 1, min 00, Daniel: "pockets" in “Check your own pockets, Leo, before you start looking at the rest of us.”
```

## The stories

Each is included in full, exactly as written to `runs/v2/`, with its headings moved down two levels to fit this report.

### The morning as a story: daniel_ate_it, rules and a language model, seed 1

Generated by `python morning.py --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 7 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 113 routine ones settled by the rules. 6 lines were spoken aloud, 3 of them new. Conversations ended 1 time. The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after a full turn with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
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
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: accuse Leo of taking it**, saying “Check your own pockets, Leo, before you start looking at the rest of us.” *(new: an accusation)* (one of 19 options). Feeling: *anxious*. Reason: “I have to shift the blame right now so no one realizes I ate the missing food myself.” Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: just accused by Daniel). Social moment: the count came up short in front of everyone; Daniel accuses you of taking it: "Check your own pockets, Leo, before you start looking at the rest of us.". **Chose: deny taking it**, saying “I didn't take it, Daniel. Check yours.” *(new: a denial of a new accusation)* (one of 20 options). Feeling: *annoyed*. Reason: “I refuse to be falsely accused when I know I played fair.” Came of it: said to Daniel, Elena, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel accuses Leo of taking it: "Check your own pockets, Leo, before you start looking at the rest of us."; Leo denies taking it, to everyone: "I didn't take it, Daniel. Check yours.". **Chose: ask everyone here who took the can**, saying “Please, stop this right now. Did any of you take it?” *(new: a question)* (one of 20 options). Feeling: *anxious*. Reason: “I need to know what happened to the can without letting the boys tear each other apart.” Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Daniel accuses Leo of taking it: "Check your own pockets, Leo, before you start looking at the rest of us."; Leo denies taking it, to everyone: "I didn't take it, Daniel. Check yours."; Elena asks everyone who took the can: "Please, stop this right now. Did any of you take it?". **Chose: deny taking it**, saying “I didn't take it, Mom! Why would I do that?” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *hurt*. Reason: “I am innocent and it hurts that they would even suspect me.” Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 03–87 (29 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, Mom! Why would I do that?"; Mara looks hurt. **Chose: reassure everyone here**, saying “Nobody here did it, we are safe. We will figure this out together.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to stop them from tearing each other apart before there is nothing left of us.” Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "Please, stop this right now. Did any of you take it?"; Mara denies taking it, to everyone: "I didn't take it, Mom! Why would I do that?"; Elena reassures everyone: "Nobody here did it, we are safe. We will figure this out together."; Mara looks hurt. **Chose: stay put and say nothing** (one of 20 options). Feeling: *annoyed*. Reason: “Arguing in circles solves nothing when the food is gone and trust is already frayed.” Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo denies taking it, to everyone: "I didn't take it, Daniel. Check yours."; Elena asks everyone who took the can: "Please, stop this right now. Did any of you take it?"; Mara denies taking it, to everyone: "I didn't take it, Mom! Why would I do that?"; Elena reassures everyone: "Nobody here did it, we are safe. We will figure this out together."; Mara looks hurt. **Chose: deny taking it**, saying “I didn't take it either, and neither did any of us.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *defensive*. Reason: “I cannot admit I ate it in the dark or I will lose all authority.” Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 06): a full turn with nothing new.*

**min 06** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 06–87 (28 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 06–87 (28 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 06–87 (28 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Daniel accuses Leo of taking it: "Check your own pockets, Leo, before you start looking at the rest of us." *(new: an accusation)*
- min 00, kitchen. Leo denies taking it, to everyone: "I didn't take it, Daniel. Check yours." *(new: a denial of a new accusation)*
- min 00, kitchen. Elena asks everyone who took the can: "Please, stop this right now. Did any of you take it?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, Mom! Why would I do that?" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "Nobody here did it, we are safe. We will figure this out together." *(not new: reassurance)*
- min 03, kitchen. Daniel denies taking it, to everyone: "I didn't take it either, and neither did any of us." *(not new: a denial with no new accusation to answer)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Daniel accused Leo (minute 00).
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 06 (a full turn with nothing new).
- The last feeling each of them named: Daniel *defensive* (minute 03); Elena *anxious* (minute 03); Leo *annoyed* (minute 03); Mara *hurt* (minute 00).


### The morning as a story: daniel_ate_it, rules and a language model, seed 2

Generated by `python morning.py --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 25 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 95 routine ones settled by the rules. 13 lines were spoken aloud, 4 of them new. Conversations ended 3 times. The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after a full turn with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
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

**min 00** · kitchen: Daniel talking, Elena talking, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “A can is missing from the shelf. Who took it?” *(new: a question)* (one of 19 options). Feeling: *anxious*. Reason: “I need to know what happened to the food without causing everyone to turn on each other.” Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Who took it?". **Chose: deny taking it**, saying “I didn't take it, I swear I didn't!” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *panicked*. Reason: “I am innocent and terrified they will think I stole the missing food.” Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Who took it?"; Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Mara looks panicked. **Chose: deny taking it**, saying “I didn't touch it, nobody here took it.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot let them know I ate the food because I must keep their respect and prove I am in control.” Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Who took it?"; Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Daniel denies taking it, to everyone: "I didn't touch it, nobody here took it."; Mara looks panicked. **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *suspicious*. Reason: “Someone took the extra portion and lying about it solves nothing, so I need to check where it might be hidden.” Came of it: started going through the room.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena staying put, Leo standing, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (panicked)). Social moment: Daniel denies taking it, to everyone: "I didn't touch it, nobody here took it.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'll help you look, I want to find it too.” *(not new: a remark (the rules cannot tell what free words add))* (one of 19 options). Feeling: *anxious*. Reason: “I need to prove I didn't take it by helping them search the kitchen right now.” Came of it: started going through the room.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Daniel denies taking it, to everyone: "I didn't touch it, nobody here took it."; Mara says to everyone, while searching: "I'll help you look, I want to find it too.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *anxious*. Reason: “I cannot bear to accuse any of them when keeping us together is the only thing that matters.” Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while searching: "I'll help you look, I want to find it too.". **Chose: carry on searching the kitchen** (one of 19 options). Feeling: *suspicious*. Reason: “Someone took that can and I need to find where it is hidden before this gets worse.” Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara says to everyone, while searching: "I'll help you look, I want to find it too."; Leo finishes going through the kitchen: no can, nothing out of place. **Chose: accuse Leo of taking it**, saying “Leo, stop acting like you didn't see what's right in front of us.” *(new: an accusation)* (one of 19 options). Feeling: *defensive*. Reason: “I have to shift the focus off me so nobody suspects I ate the food.” Came of it: said to Elena, Leo, Mara.

**min 06** · kitchen: Daniel talking, Elena talking, Leo talking, Mara standing · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Leo, stop acting like you didn't see what's right in front of us.". **Chose: deny taking it**, saying “I didn't take the can, Daniel, and accusing me doesn't bring it back.” *(new: a denial of a new accusation)* (one of 18 options). Feeling: *annoyed*. Reason: “I need to deny Daniel's baseless accusation clearly and calmly before things escalate further.” Came of it: said to Daniel, Elena, Mara.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo denies taking it, to everyone: "I didn't take the can, Daniel, and accusing me doesn't bring it back.". **Chose: accuse Leo of taking it**, saying “Don't look at me like that, Leo, you're the one standing right next to the shelf.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *defensive*. Reason: “I cannot let them suspect me, so I have to keep the pressure on Leo.” Came of it: said to Elena, Leo, Mara.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel accuses Leo of taking it: "Leo, stop acting like you didn't see what's right in front of us."; Leo denies taking it, to everyone: "I didn't take the can, Daniel, and accusing me doesn't bring it back."; Daniel accuses Leo of taking it: "Don't look at me like that, Leo, you're the one standing right next to the shelf.". **Chose: ask everyone here who took the can**, saying “Please stop fighting, can we just figure out where it actually went?” *(new: a question)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot stand them arguing and accusing each other when we need to stay close.” Came of it: said to Daniel, Elena, Leo.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel accuses Leo of taking it: "Leo, stop acting like you didn't see what's right in front of us."; Leo denies taking it, to everyone: "I didn't take the can, Daniel, and accusing me doesn't bring it back."; Daniel accuses Leo of taking it: "Don't look at me like that, Leo, you're the one standing right next to the shelf."; Mara asks everyone who took the can: "Please stop fighting, can we just figure out where it actually went?". **Chose: reassure everyone here**, saying “Stop arguing, nobody here took anything, we are going to get through this together.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I must stop them from tearing each other apart over one can of food.” Came of it: said to Daniel, Leo, Mara.

**min 09** · kitchen: Daniel talking, Elena searching the kitchen, Leo staying put, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Don't look at me like that, Leo, you're the one standing right next to the shelf."; Mara asks everyone who took the can: "Please stop fighting, can we just figure out where it actually went?"; Elena reassures everyone: "Stop arguing, nobody here took anything, we are going to get through this together.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *annoyed*. Reason: “Arguing in circles accomplishes nothing and only wears us down further.” Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Stop arguing, nobody here took anything, we are going to get through this together.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'm going to look again, it has to be here somewhere.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “I need to prove I didn't take it by helping find where it went.” Came of it: started going through the room.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while searching: "I'm going to look again, it has to be here somewhere.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 19 options). Feeling: *anxious*. Reason: “I need to find the missing can myself before this argument tears the children apart.” Came of it: started going through the room.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara asks everyone who took the can: "Please stop fighting, can we just figure out where it actually went?"; Elena reassures everyone: "Stop arguing, nobody here took anything, we are going to get through this together."; Mara says to everyone, while searching: "I'm going to look again, it has to be here somewhere.". **Chose: accuse Leo of taking it**, saying “You keep quiet, Leo, but we all know you're just trying to hide what you did.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *anxious*. Reason: “I have to keep pushing the blame away from myself so nobody suspects I ate the food.” Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 12): a full turn with nothing new.*

**min 12** · kitchen: Daniel talking, Elena standing, Leo staying put, Mara standing · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Mara finished searching the kitchen and found nothing.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place. Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: deny taking it**, saying “I didn't touch it, and I won't be accused of something I had no part in.” *(not new: a denial with no new accusation to answer)* (one of 16 options). Feeling: *defensive*. Reason: “I cannot let them suspect the truth or I will lose all authority here.” Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Leo of taking it: "You keep quiet, Leo, but we all know you're just trying to hide what you did."; Mara finishes going through the kitchen: no can, nothing out of place; Daniel denies taking it, to everyone: "I didn't touch it, and I won't be accused of something I had no part in.". **Chose: carry on searching the kitchen** (one of 20 options). Feeling: *anxious*. Reason: “I need to find that missing can myself before this argument tears the family apart.” Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- *The kitchen's conversation starts (minute 12): Mara finished searching the kitchen and found nothing.*

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo leaving for the back room, Mara leaving for the back room · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't touch it, and I won't be accused of something I had no part in."; Elena finishes going through the kitchen: no can, nothing out of place. **Chose: go to the back room** (one of 19 options). Feeling: *anxious*. Reason: “I cannot stand them shouting and accusing each other over the missing food any longer.” Came of it: went to the back room.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara finishes going through the kitchen: no can, nothing out of place; Daniel denies taking it, to everyone: "I didn't touch it, and I won't be accused of something I had no part in."; Elena finishes going through the kitchen: no can, nothing out of place. **Chose: go to the back room** (one of 16 options). Feeling: *annoyed*. Reason: “I refuse to stay here and endure more of Daniel's baseless accusations while the food dwindles.” Came of it: went to the back room.
- **Elena, minutes 15–87 (25 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 13 options). Feeling: *anxious*. Reason: “I cannot admit I ate it, so I must stay quiet and let them keep looking elsewhere.” Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 18): a full turn with nothing new.*

**min 18** · kitchen: Daniel staying put, Elena staying put · back room: Leo searching the back room, Mara searching the back room · nobody in brothers room, bathroom
- **Daniel, minutes 18–87 (24 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (1st to act in the back room: drawn by the seed among equals). Social moment: Leo comes into the back room. **Chose: search the back room for the can (takes about six minutes)**, saying “I need to check my own space just to be sure.” *(not new: a remark (the rules cannot tell what free words add))* (one of 11 options). Feeling: *anxious*. Reason: “I have to search my room because I cannot stand being suspected.” Came of it: started going through the room.
- **Leo** (2nd to act in the back room: the only one left to act here). Social moment: Mara comes into the back room; Mara says to everyone, while searching: "I need to check my own space just to be sure.". **Chose: search the back room for the can (takes about six minutes)** (one of 10 options). Feeling: *annoyed*. Reason: “I will check the back room myself since everyone else is looking.” Came of it: started going through the room.
- *The back room's conversation starts (minute 18): Mara came in.*

**min 21** · kitchen: Daniel staying put, Elena staying put · back room: Leo standing, Mara standing · nobody in brothers room, bathroom
- **Leo.** Rules: nothing social happened to them. **Carry on searching the back room**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the back room and found nothing.
- **Mara** (2nd to act in the back room: the only one left to act here). Social moment: Leo finishes going through the back room: no can, nothing out of place. **Chose: carry on searching the back room** (one of 11 options). Feeling: *anxious*. Reason: “I have to keep looking in my own room because nobody else is going to find it for me.” Came of it: went through the room and found nothing. New in the room: Mara finished searching the back room and found nothing.

**min 24** · kitchen: Daniel staying put, Elena staying put · back room: Leo staying put, Mara staying put · nobody in brothers room, bathroom
- **Mara, minutes 24–87 (22 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the back room: the only one left to act here). Social moment: Mara finishes going through the back room: no can, nothing out of place. **Chose: stay put and say nothing** (one of 10 options). Feeling: *annoyed*. Reason: “I have already searched this room and there is no point in continuing to look through things that have already been checked.” Came of it: stayed where they were.
- *The back room's conversation ends (minute 27): a full turn with nothing new.*

**min 27** · kitchen: Daniel staying put, Elena staying put · back room: Leo staying put, Mara staying put · nobody in brothers room, bathroom
- **Leo, minutes 27–87 (21 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Elena asks everyone who took the can: "A can is missing from the shelf. Who took it?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!" *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Daniel denies taking it, to everyone: "I didn't touch it, nobody here took it." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Mara says to everyone, while searching: "I'll help you look, I want to find it too." *(not new: a remark (the rules cannot tell what free words add))*
- min 03, kitchen. Daniel accuses Leo of taking it: "Leo, stop acting like you didn't see what's right in front of us." *(new: an accusation)*
- min 06, kitchen. Leo denies taking it, to everyone: "I didn't take the can, Daniel, and accusing me doesn't bring it back." *(new: a denial of a new accusation)*
- min 06, kitchen. Daniel accuses Leo of taking it: "Don't look at me like that, Leo, you're the one standing right next to the shelf." *(not new: an accusation they had made before)*
- min 06, kitchen. Mara asks everyone who took the can: "Please stop fighting, can we just figure out where it actually went?" *(new: a question)*
- min 06, kitchen. Elena reassures everyone: "Stop arguing, nobody here took anything, we are going to get through this together." *(not new: reassurance)*
- min 09, kitchen. Mara says to everyone, while searching: "I'm going to look again, it has to be here somewhere." *(not new: a remark (the rules cannot tell what free words add))*
- min 09, kitchen. Daniel accuses Leo of taking it: "You keep quiet, Leo, but we all know you're just trying to hide what you did." *(not new: an accusation they had made before)*
- min 12, kitchen. Daniel denies taking it, to everyone: "I didn't touch it, and I won't be accused of something I had no part in." *(not new: a denial with no new accusation to answer)*
- min 18, back room. Mara says to everyone, while searching: "I need to check my own space just to be sure." *(not new: a remark (the rules cannot tell what free words add))*

#### At the end

At minute 90: kitchen: Daniel, Elena; back room: Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Daniel accused Leo (minute 03); Daniel accused Leo (minute 06); Daniel accused Leo (minute 09).
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 12 (a full turn with nothing new); kitchen started at minute 12 (Mara finished searching the kitchen and found nothing); kitchen ended at minute 18 (a full turn with nothing new); back room started at minute 18 (Mara came in); back room ended at minute 27 (a full turn with nothing new).
- The last feeling each of them named: Daniel *anxious* (minute 15); Elena *anxious* (minute 12); Leo *annoyed* (minute 24); Mara *anxious* (minute 21).


### The morning as a story: daniel_ate_it, rules and a language model, seed 3

Generated by `python morning.py --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 11 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 109 routine ones settled by the rules. 8 lines were spoken aloud, 4 of them new. Conversations ended 1 time. The pantry held 2 portions at the start and 2 at the end.

#### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after a full turn with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
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

**min 00** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “One can is gone, so who took it?” *(new: a question)* (one of 19 options). Feeling: *anxious*. Reason: “I need to know the truth right now before things get worse between us all.” Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so who took it?". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I cannot accuse any of my children when keeping us together matters more than a missing can.” Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so who took it?". **Chose: deny taking it**, saying “Nobody took it on purpose, it must have been an inventory mistake from the start.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot let them know I ate the food because I need to maintain my authority as the eldest.” Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so who took it?"; Daniel denies taking it, to everyone: "Nobody took it on purpose, it must have been an inventory mistake from the start.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *wary*. Reason: “Daniel is clearly lying about an inventory mistake, but making an accusation right now will only tear us apart.” Came of it: stayed where they were.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "Nobody took it on purpose, it must have been an inventory mistake from the start.". **Chose: ask everyone here who took the can**, saying “Someone took it from this shelf, so we need to know who did it.” *(new: a question)* (one of 20 options). Feeling: *anxious*. Reason: “I have to know the truth before things fall apart completely.” Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "Nobody took it on purpose, it must have been an inventory mistake from the start."; Elena asks everyone who took the can: "Someone took it from this shelf, so we need to know who did it.". **Chose: accuse Daniel of taking it**, saying “You emptied my bag yesterday, Daniel, so why shouldn't I think you took it?” *(new: an accusation)* (one of 20 options). Feeling: *resentful*. Reason: “He thinks he can treat me like a child and then lie about the food.” Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: just accused by Mara). Social moment: Elena asks everyone who took the can: "Someone took it from this shelf, so we need to know who did it."; Mara accuses you of taking it: "You emptied my bag yesterday, Daniel, so why shouldn't I think you took it?". **Chose: deny taking it**, saying “I didn't take it, and I won't have you accusing me in my own house.” *(new: a denial of a new accusation)* (one of 20 options). Feeling: *defensive*. Reason: “I must protect my authority and not let them suspect the truth.” Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena asks everyone who took the can: "Someone took it from this shelf, so we need to know who did it."; Mara accuses Daniel of taking it: "You emptied my bag yesterday, Daniel, so why shouldn't I think you took it?"; Daniel denies taking it, to everyone: "I didn't take it, and I won't have you accusing me in my own house.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *wary*. Reason: “Accusing one another only accelerates the fracture of the house.” Came of it: stayed where they were.

**min 06** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo, minutes 06–87 (28 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take it, and I won't have you accusing me in my own house.". **Chose: accuse Daniel of taking it**, saying “You treat me like a child while you're the one hiding things.” *(not new: an accusation they had made before)* (one of 20 options). Feeling: *resentful*. Reason: “I want him to stop acting like he is above suspicion just because he is older.” Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "You treat me like a child while you're the one hiding things.". **Chose: deny taking it**, saying “I didn't take it, and I am sick of all of you pointing fingers when I'm the one keeping us safe.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *defensive*. Reason: “I have to keep holding my ground so nobody finds out I ate the can.” Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "You emptied my bag yesterday, Daniel, so why shouldn't I think you took it?"; Daniel denies taking it, to everyone: "I didn't take it, and I won't have you accusing me in my own house."; Mara accuses Daniel of taking it: "You treat me like a child while you're the one hiding things."; Daniel denies taking it, to everyone: "I didn't take it, and I am sick of all of you pointing fingers when I'm the one keeping us safe.". **Chose: reassure everyone here**, saying “Stop shouting at each other, nobody is accusing anyone else right now.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I must stop them from tearing each other apart before the house breaks completely.” Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation ends (minute 09): a full turn with nothing new.*

**min 09** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 09–87 (27 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 09–87 (27 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 09–87 (27 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. Mara asks everyone who took the can: "One can is gone, so who took it?" *(new: a question)*
- min 00, kitchen. Daniel denies taking it, to everyone: "Nobody took it on purpose, it must have been an inventory mistake from the start." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena asks everyone who took the can: "Someone took it from this shelf, so we need to know who did it." *(new: a question)*
- min 03, kitchen. Mara accuses Daniel of taking it: "You emptied my bag yesterday, Daniel, so why shouldn't I think you took it?" *(new: an accusation)*
- min 03, kitchen. Daniel denies taking it, to everyone: "I didn't take it, and I won't have you accusing me in my own house." *(new: a denial of a new accusation)*
- min 06, kitchen. Mara accuses Daniel of taking it: "You treat me like a child while you're the one hiding things." *(not new: an accusation they had made before)*
- min 06, kitchen. Daniel denies taking it, to everyone: "I didn't take it, and I am sick of all of you pointing fingers when I'm the one keeping us safe." *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Elena reassures everyone: "Stop shouting at each other, nobody is accusing anyone else right now." *(not new: reassurance)*

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Mara accused Daniel (minute 03); Mara accused Daniel (minute 06).
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (a full turn with nothing new).
- The last feeling each of them named: Daniel *defensive* (minute 06); Elena *deeply anxious* (minute 06); Leo *wary* (minute 03); Mara *resentful* (minute 06).

