# LLM morning prototype: report

A throwaway Python prototype of the `daniel_ate_it` morning. Rules keep the house and what each person knows, and list what each of them may do. At social moments only, a Gemini model picks one of those options, says the words and names a feeling. It lives in `Prototypes/llm-morning/`; nothing in `Assets/` or the Unity project was touched.

**Model used: `gemini-3.5-flash-lite`** (API name `models/gemini-3.5-flash-lite`, display name "Gemini 3.5 Flash Lite"), confirmed by listing the models this key can call before the first real run. It is set in `config.json`.

## Done when

| Condition | Result |
|---|---|
| 3 fresh mornings run to completion | seeds 1, 2, 3 all reached minute 90 (exit 0) |
| under 150 real calls each | 120, 39, 90 API requests (retries included; there were none) |
| each writes a story to `runs/` | `runs/daniel_ate_it-seed1.md`, `-seed2.md`, `-seed3.md` |
| `--replay` reproduces one byte for byte with 0 API calls | seed 1: IDENTICAL, 0 API requests, run with `GEMINI_API_KEY` unset; `cmp` and SHA-256 agree |

## The three mornings

| Seed | API requests | Run time | Model decisions | Routine (rules) | Fallbacks | Lines spoken | Largest prompt (API count) | What happened |
|---|---|---|---|---|---|---|---|---|
| 1 | 120 | 537 s (8.9 min) | 120 | 0 | 0 | 76 | 1252 tokens | Daniel blames Leo, denies for 40 minutes, confesses at min 42 with Leo out of the room; Elena shares the food at min 3; talk never stops. |
| 2 | 39 | 172 s (2.9 min) | 39 | 81 | 0 | 24 | 1254 tokens | Daniel blames Leo four times, never confesses; Elena shares at min 18; everyone falls silent at min 27 and stays silent. |
| 3 | 90 | 427 s (7.1 min) | 90 | 30 | 0 | 53 | 1247 tokens | Daniel blames Leo, confesses at min 18; Leo shares at min 12; the rest is comfort and Daniel promising to fix it; the last words are at min 63, and from min 72 the rules settle every turn. |

Real generate requests today: 249 for these three mornings, plus 49 in two aborted attempts (see *Aborted attempts*), 298 in all, against the free limit of 500 a day. One `models.list` call was also made to confirm the model name.

## How it works

| File | What it does |
|---|---|
| `data.py` | The family, house, start state and backstory, copied by hand from the shipped `Minds/*.json`, `Scenario/morning.json` and `Scenario/backstory.json` (who did, saw or heard each event). Ages and roles match `target-morning.md`; nothing else from that file is used. |
| `world.py` | The rules layer: world state, each person's memory, the options each person has each turn, the social trigger, the prompt, the answer check, and what an act does to the house. |
| `gemini.py` | Gemini client (spacing, backoff, call cap, daily-quota stop), the fake model, the prompt-keyed cache, and the `Oracle` that puts the cache in front of a client. |
| `story.py` | Writes the morning as a story in the narrator's style. It uses nothing but the morning's record: no clock, no call counts. |
| `morning.py` | The command line: fresh, `--replay`, `--fake`. |
| `list_models.py` | Lists the models this key can call (no generate calls). |
| `test_morning.py` | 17 tests against the fake model and a stubbed API. |
| `config.json`, `requirements.txt` | Model name and limits; `google-genai==2.25.0`. |

- **Turns.** 30 turns of 3 minutes. Everyone decides against the same moment, then the acts happen in a fixed order (Daniel, Elena, Leo, Mara).
- **Memory.** Each person gets the backstory lines they did, saw or heard. Daniel alone has *"In the night Daniel eats a can... Nobody sees. (you did it)"* and a pinned line saying he knows where the can went. During the morning each person remembers what they did and said, what they saw in their room, the words spoken there, and voices from other rooms (no words, and nothing into or out of the bathroom). A few facts are pinned and never trimmed: the discovery, a confession made or heard, food eaten or shared, and finished searches. So are their own last three lines.
- **Options.** The rules offer: stay put and say nothing; ask who took it (only if you don't know); deny (once the question has been raised in your hearing, and never after confessing); accuse someone present; confess (only whoever ate it, once); reassure one person or everyone; say something else; sit with someone; search this room (not after the admission); go to another room; eat a portion; share out what's left. Once someone has heard the confession, the only accusation they can make is against Daniel.
- **When the model is asked.** Only when something social has just happened to that person: someone spoke where they could hear it (words or voices), they were accused, someone came to sit with them, someone ate or shared food in front of them, someone in the room looks upset, or the count came up short (minute 0). Otherwise the rules continue their current act (a search, sitting with someone) or keep them where they are. At most one call per person per turn, so at most 120 per morning.
- **The prompt** (system text + about 1,000 to 1,250 tokens). It holds the character sheet (the data's note, traits in words, values, hunger), the house, the backstory they know, what they are sure of, their last words, recent memory, who is in the room and how they look, and the options. Old memory is trimmed first to stay under the budget. It contains no target-morning text; a test checks every sentence of that file against every prompt.
- **The answer.** JSON `{option, say, feeling, reason}`, requested with a response schema. It is rejected, and the rules choose instead, when it isn't JSON, a field is missing, the option wasn't offered, or a speech option has no words. A line attached to "say nothing" is dropped.
- **Feelings.** A named feeling that shows on the face (scared, angry, hurt, desperate...) is seen by the others in the room for 9 minutes and counts as upset nearby. Inward ones (guilty, ashamed, anxious...) are not shown to anyone.
- **Cache and replay.** Every answer is saved in `cache/<model>-daniel_ate_it-seed<N>.json`. The key is the SHA-256 of model + seed + system text + prompt. The seed is in the key so three fresh mornings don't reuse each other's first answers, which would make them identical. The seed also goes to the API as the sampling seed. `--replay` builds no client at all and needs no key; a missing answer stops it with a message.
- **Limits.** Calls start at least 4.5 s apart (under 15 a minute). A per-minute 429 or a 5xx backs off 5, 10, 20... s (at most 120 s, at least the server's `retryDelay`), up to 6 retries. A per-day 429 stops the morning cleanly and says to rerun the same command after the reset; cached answers are then reused. The morning stops at 150 API requests. The key is read from `GEMINI_API_KEY` and never printed or written; a test checks every output file and stdout for it.

## Aborted attempts

Before the three mornings above, two real attempts were stopped by hand after 14 and 35 requests (49 in all). Their answers showed rules bugs, and running on would have wasted quota on mornings that had to be redone. The caches are kept in `cache/aborted/` and are not used.

1. **Deny after confessing.** Daniel confessed at minute 0 and the rules still offered him "deny" at minute 3, which the model took. Fix: someone who has admitted it can no longer deny it or accuse anyone else, and whoever heard it can only accuse Daniel.
2. **Forgetting your own confession.** Trimming the prompt to its budget dropped old morning memory, including the confession, so by minute 21 Daniel was searching "to prove I didn't take it". The same trimming let Mara repeat one accusation word for word three times. Fix: the pinned facts and last three lines described above. Searching is no longer offered to anyone who made or heard the admission.

Both fixes have tests (`test_an_admission_cannot_be_taken_back`).

## What stands out

These are observations; the judge is a person reading the stories below.

- **It reads as four people talking.** Daniel lies, blames Leo and gets louder ("I didn't take the damn can, why won't anyone believe me?"). Mara brings up her emptied bag against Daniel, and Elena holds the family together. In seed 1, Leo is in the brothers room when Daniel confesses. At minute 54 he asks "Alright, so who actually took it?", because the rules kept the confession from him.
- **Daniel's path varies**: confession at 42 (seed 1), never (seed 2), confession at 18 (seed 3). Food was shared equally in all three, by Elena twice and Leo once.
- **The opening doesn't vary**: in all three runs Daniel's first act is to accuse Leo, with almost the same words ("Don't look at me like that, Leo...").
- **Loops.** Once a stance is set the model repeats it. Seed 1: Daniel denies 9 turns running (minutes 15 to 39) while Elena answers nearly every turn with reassurance. From minute 57 to 87 every line of Daniel's is "reassure everyone", and every line of Elena's is reassurance too. Pinning their last three lines made the repeats reworded rather than word for word; the act still repeats.
- **The social gate fails both ways.** In seed 1 someone always spoke, so all 120 decisions went to the model and the rules path never ran. In seed 2 all four chose silence at minute 27, and after that nothing social could happen, so the last 60 minutes are the same routine line for everyone. Hunger rises but never counts as a trigger.
- **The model invents world.** It mentions things the rules don't have: checking the front window, an open jacket, a door to knock on. The words are kept as spoken, but nothing in the house changes. Once, Leo calls his mother "Elena".
- **No unusable answers** from the real model in 249 calls. The fallback path was exercised only by the fake model's canned broken answers.

## Commands and their output

All commands run in `Prototypes/llm-morning/`, using the venv's Python (`.venv/Scripts/python`).

### Install

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

`google-genai` is the official Google Gen AI SDK. `pip show` gives author Google LLC and home page github.com/googleapis/python-genai; version 2.25.0 was the newest on PyPI. The older `google-generativeai` package is its deprecated predecessor.

### Confirm the model name

```bash
python list_models.py 3.5-flash-lite
```

```
models/gemini-3.5-flash-lite                            Gemini 3.5 Flash Lite
```

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

----------------------------------------------------------------------
Ran 17 tests in 1.702s

OK
```

### Fresh morning, seed 1

```bash
python morning.py --seed 1
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 4; so far 20 live, 0 cached, 20 API requests
  min 15: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 18: model asked for 4; so far 28 live, 0 cached, 28 API requests
  min 21: model asked for 4; so far 32 live, 0 cached, 32 API requests
  min 24: model asked for 4; so far 36 live, 0 cached, 36 API requests
  min 27: model asked for 4; so far 40 live, 0 cached, 40 API requests
  min 30: model asked for 4; so far 44 live, 0 cached, 44 API requests
  min 33: model asked for 4; so far 48 live, 0 cached, 48 API requests
  min 36: model asked for 4; so far 52 live, 0 cached, 52 API requests
  min 39: model asked for 4; so far 56 live, 0 cached, 56 API requests
  min 42: model asked for 4; so far 60 live, 0 cached, 60 API requests
  min 45: model asked for 4; so far 64 live, 0 cached, 64 API requests
  min 48: model asked for 4; so far 68 live, 0 cached, 68 API requests
  min 51: model asked for 4; so far 72 live, 0 cached, 72 API requests
  min 54: model asked for 4; so far 76 live, 0 cached, 76 API requests
  min 57: model asked for 4; so far 80 live, 0 cached, 80 API requests
  min 60: model asked for 4; so far 84 live, 0 cached, 84 API requests
  min 63: model asked for 4; so far 88 live, 0 cached, 88 API requests
  min 66: model asked for 4; so far 92 live, 0 cached, 92 API requests
  min 69: model asked for 4; so far 96 live, 0 cached, 96 API requests
  min 72: model asked for 4; so far 100 live, 0 cached, 100 API requests
  min 75: model asked for 4; so far 104 live, 0 cached, 104 API requests
  min 78: model asked for 4; so far 108 live, 0 cached, 108 API requests
  min 81: model asked for 4; so far 112 live, 0 cached, 112 API requests
  min 84: model asked for 4; so far 116 live, 0 cached, 116 API requests
  min 87: model asked for 4; so far 120 live, 0 cached, 120 API requests

wrote runs/daniel_ate_it-seed1.md
  api_requests: 120
  answers_live: 120
  answers_from_cache: 0
  model_decisions: 120
  fallbacks: 0
  routine_decisions: 0
  lines_spoken: 76
  max_prompt_tokens_estimated: 1250
  max_prompt_tokens_counted_by_api: 1252
  run_seconds: 537.0
  story_sha256: 5531dffb1da7aa1bd487a23f9a14adb0606389037f286b029e1b4f17ece41e3b
```

### Fresh morning, seed 2

```bash
python morning.py --seed 2
```

```
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 4; so far 20 live, 0 cached, 20 API requests
  min 15: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 18: model asked for 4; so far 28 live, 0 cached, 28 API requests
  min 21: model asked for 4; so far 32 live, 0 cached, 32 API requests
  min 24: model asked for 4; so far 36 live, 0 cached, 36 API requests
  min 27: model asked for 3; so far 39 live, 0 cached, 39 API requests

wrote runs/daniel_ate_it-seed2.md
  api_requests: 39
  answers_live: 39
  answers_from_cache: 0
  model_decisions: 39
  fallbacks: 0
  routine_decisions: 81
  lines_spoken: 24
  max_prompt_tokens_estimated: 1250
  max_prompt_tokens_counted_by_api: 1254
  run_seconds: 171.9
  story_sha256: ae888fcef8ab2ac669c7149856c285bb9f072a3272513d96991902a63570cbd6
```

### Fresh morning, seed 3

```bash
python morning.py --seed 3
```

```
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 4; so far 20 live, 0 cached, 20 API requests
  min 15: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 18: model asked for 3; so far 27 live, 0 cached, 27 API requests
  min 21: model asked for 3; so far 30 live, 0 cached, 30 API requests
  min 24: model asked for 4; so far 34 live, 0 cached, 34 API requests
  min 27: model asked for 4; so far 38 live, 0 cached, 38 API requests
  min 30: model asked for 4; so far 42 live, 0 cached, 42 API requests
  min 33: model asked for 4; so far 46 live, 0 cached, 46 API requests
  min 36: model asked for 4; so far 50 live, 0 cached, 50 API requests
  min 39: model asked for 4; so far 54 live, 0 cached, 54 API requests
  min 42: model asked for 4; so far 58 live, 0 cached, 58 API requests
  min 45: model asked for 3; so far 61 live, 0 cached, 61 API requests
  min 48: model asked for 4; so far 65 live, 0 cached, 65 API requests
  min 51: model asked for 4; so far 69 live, 0 cached, 69 API requests
  min 54: model asked for 4; so far 73 live, 0 cached, 73 API requests
  min 57: model asked for 4; so far 77 live, 0 cached, 77 API requests
  min 60: model asked for 4; so far 81 live, 0 cached, 81 API requests
  min 63: model asked for 4; so far 85 live, 0 cached, 85 API requests
  min 66: model asked for 4; so far 89 live, 0 cached, 89 API requests
  min 69: model asked for 1; so far 90 live, 0 cached, 90 API requests

wrote runs/daniel_ate_it-seed3.md
  api_requests: 90
  answers_live: 90
  answers_from_cache: 0
  model_decisions: 90
  fallbacks: 0
  routine_decisions: 30
  lines_spoken: 53
  max_prompt_tokens_estimated: 1250
  max_prompt_tokens_counted_by_api: 1247
  run_seconds: 427.2
  story_sha256: 2c540f6d6dd5f2077f874d2f4c1900d8f28e5473aef57f4197f509b4d4a48b30
```

### Replay of seed 1 (key unset, cache only)

```bash
env -u GEMINI_API_KEY python morning.py --seed 1 --replay
cmp runs/daniel_ate_it-seed1.md runs/daniel_ate_it-seed1.replay.md && echo "cmp: identical"
sha256sum runs/daniel_ate_it-seed1.md runs/daniel_ate_it-seed1.replay.md
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, replay from cache only; cache cache\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 120 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 4; so far 0 live, 12 cached, 0 API requests
  min 09: model asked for 4; so far 0 live, 16 cached, 0 API requests
  min 12: model asked for 4; so far 0 live, 20 cached, 0 API requests
  min 15: model asked for 4; so far 0 live, 24 cached, 0 API requests
  min 18: model asked for 4; so far 0 live, 28 cached, 0 API requests
  min 21: model asked for 4; so far 0 live, 32 cached, 0 API requests
  min 24: model asked for 4; so far 0 live, 36 cached, 0 API requests
  min 27: model asked for 4; so far 0 live, 40 cached, 0 API requests
  min 30: model asked for 4; so far 0 live, 44 cached, 0 API requests
  min 33: model asked for 4; so far 0 live, 48 cached, 0 API requests
  min 36: model asked for 4; so far 0 live, 52 cached, 0 API requests
  min 39: model asked for 4; so far 0 live, 56 cached, 0 API requests
  min 42: model asked for 4; so far 0 live, 60 cached, 0 API requests
  min 45: model asked for 4; so far 0 live, 64 cached, 0 API requests
  min 48: model asked for 4; so far 0 live, 68 cached, 0 API requests
  min 51: model asked for 4; so far 0 live, 72 cached, 0 API requests
  min 54: model asked for 4; so far 0 live, 76 cached, 0 API requests
  min 57: model asked for 4; so far 0 live, 80 cached, 0 API requests
  min 60: model asked for 4; so far 0 live, 84 cached, 0 API requests
  min 63: model asked for 4; so far 0 live, 88 cached, 0 API requests
  min 66: model asked for 4; so far 0 live, 92 cached, 0 API requests
  min 69: model asked for 4; so far 0 live, 96 cached, 0 API requests
  min 72: model asked for 4; so far 0 live, 100 cached, 0 API requests
  min 75: model asked for 4; so far 0 live, 104 cached, 0 API requests
  min 78: model asked for 4; so far 0 live, 108 cached, 0 API requests
  min 81: model asked for 4; so far 0 live, 112 cached, 0 API requests
  min 84: model asked for 4; so far 0 live, 116 cached, 0 API requests
  min 87: model asked for 4; so far 0 live, 120 cached, 0 API requests

wrote runs/daniel_ate_it-seed1.replay.md
  api_requests: 0
  answers_live: 0
  answers_from_cache: 120
  model_decisions: 120
  fallbacks: 0
  routine_decisions: 0
  lines_spoken: 76
  max_prompt_tokens_estimated: 1250
  max_prompt_tokens_counted_by_api: 1252
  run_seconds: 0.1
  story_sha256: 5531dffb1da7aa1bd487a23f9a14adb0606389037f286b029e1b4f17ece41e3b
  byte for byte against runs\daniel_ate_it-seed1.md: IDENTICAL
```

```
cmp: identical
5531dffb1da7aa1bd487a23f9a14adb0606389037f286b029e1b4f17ece41e3b *runs/daniel_ate_it-seed1.md
5531dffb1da7aa1bd487a23f9a14adb0606389037f286b029e1b4f17ece41e3b *runs/daniel_ate_it-seed1.replay.md
```

## One re-render after the runs

After the runs I found a cosmetic bug in `story.py`: `capitalize()` lowercased names in routine lines ("Keep sitting with daniel"). I fixed it and wrote the three stories again from their caches with `python morning.py --seed N`. All answers came from the cache (0 API requests), and the meta files from the live runs were kept. Seeds 1 and 2 came out byte-identical to what the live runs wrote. Seed 3, the only one with such a line, changed in that line alone, so its SHA-256 is now `a69961b8...` where the live run's output above shows `2c540f6d...`. The seed 1 replay above was run after the fix.

## The stories

Each is included in full, exactly as written to `runs/`, with its headings moved down two levels to fit this report.

### The morning as a story: daniel_ate_it, rules and a language model, seed 1

Generated by `python morning.py --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 120 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 0 routine ones settled by the rules. 76 lines were spoken aloud. The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, or looks upset in the same room). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes and counts as upset nearby. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when a decision is told there.
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
- **Daniel.** Social moment: the count came up short in front of everyone. **Chose: accuse Leo of taking it**, saying “Don't look at me like that, Leo, you're the one who was going on about hoarding from the start.” (one of 19 options). Feeling: *defensive*. Reason: “I have to deflect the blame so they don't suspect I ate the missing food myself.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “One of our cans is missing. Which of you took it?” (one of 19 options). Feeling: *deeply anxious*. Reason: “I need to know the truth before this breaks us apart entirely.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: the count came up short in front of everyone. **Chose: search the kitchen for the can (takes about six minutes)** (one of 19 options). Feeling: *suspicious*. Reason: “I need to know if the can was actually stolen or just misplaced before anyone starts accusing each other.” Came of it: started going through the room.
- **Mara.** Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Who took the can? One of us must know where it went.” (one of 19 options). Feeling: *anxious*. Reason: “I need to know the truth right now before anyone starts blaming each other unfairly.” Came of it: said to Daniel, Elena, Leo.

**min 03** · kitchen: Daniel talking, Elena sharing out the food, Leo standing, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena asks who took it: "One of our cans is missing. Which of you took it?"; Mara asks who took it: "Who took the can? One of us must know where it went.". **Chose: deny taking it**, saying “I didn't take it, I swear. Someone else must have moved it or it was never there.” (one of 19 options). Feeling: *panicked*. Reason: “I cannot let them know I ate the food in the dark, or I will lose all authority over them.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "Don't look at me like that, Leo, you're the one who was going on about hoarding from the start."; Mara asks who took it: "Who took the can? One of us must know where it went.". **Chose: share out what is left among everyone here**, saying “There is no point in us fighting, we will divide what is left right now so everyone has a fair share.” (one of 19 options). Feeling: *deeply anxious*. Reason: “If I divide the food now before the tension tears them apart, they might stop accusing each other.” Came of it: shared out the last 2 portions between Elena, Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel accuses you: "Don't look at me like that, Leo, you're the one who was going on about hoarding from the start."; Elena asks who took it: "One of our cans is missing. Which of you took it?"; Mara asks who took it: "Who took the can? One of us must know where it went.". **Chose: deny taking it**, saying “I didn't take it, and looking at each other like this is a waste of time.” (one of 20 options). Feeling: *annoyed*. Reason: “I need to clear my name immediately before Daniel turns this into a power struggle.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel accuses Leo: "Don't look at me like that, Leo, you're the one who was going on about hoarding from the start."; Elena asks who took it: "One of our cans is missing. Which of you took it?". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I want to help look, I know I didn't touch it.” (one of 19 options). Feeling: *resentful*. Reason: “I need to prove I am not a child who steals and cannot be trusted.” Came of it: started going through the room.

**min 06** · kitchen: Daniel staying put, Elena talking, Leo searching the kitchen, Mara standing · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena says: "There is no point in us fighting, we will divide what is left right now so everyone has a fair share."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; Leo denies taking it: "I didn't take it, and looking at each other like this is a waste of time."; Mara says: "I want to help look, I know I didn't touch it.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *guilty*. Reason: “If I keep quiet maybe they will stop tearing the kitchen apart and forget about the missing can.” Came of it: stayed where they were.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take it, I swear. Someone else must have moved it or it was never there."; Leo denies taking it: "I didn't take it, and looking at each other like this is a waste of time."; Mara says: "I want to help look, I know I didn't touch it."; Daniel looks panicked. **Chose: reassure everyone here**, saying “We are not going to tear each other apart over this, we will get through today together.” (one of 17 options). Feeling: *anxious*. Reason: “I need to keep the family from turning on each other before things fall completely apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take it, I swear. Someone else must have moved it or it was never there."; Elena says: "There is no point in us fighting, we will divide what is left right now so everyone has a fair share."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; Mara says: "I want to help look, I know I didn't touch it."; Daniel looks panicked. **Chose: search the kitchen for the can (takes about six minutes)**, saying “Panicking won't find it, let's just look properly.” (one of 17 options). Feeling: *suspicious*. Reason: “Someone took that food and denying it over and over changes nothing, so I need to find where it went.” Came of it: started going through the room.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take it, I swear. Someone else must have moved it or it was never there."; Elena says: "There is no point in us fighting, we will divide what is left right now so everyone has a fair share."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; Leo denies taking it: "I didn't take it, and looking at each other like this is a waste of time."; Daniel looks panicked. **Chose: carry on searching the kitchen**, saying “I'm still looking, it has to be here somewhere.” (one of 18 options). Feeling: *resentful*. Reason: “I cannot stand them looking at me like I am a thief when I know I am innocent.” Came of it: went through the room and found nothing.

**min 09** · kitchen: Daniel staying put, Elena talking, Leo standing, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are not going to tear each other apart over this, we will get through today together."; Leo says: "Panicking won't find it, let's just look properly."; Mara says: "I'm still looking, it has to be here somewhere.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *guilty*. Reason: “I cannot bear to watch them tear the kitchen apart looking for a can I already ate, but I am too afraid to admit the truth.” Came of it: stayed where they were.
- **Elena.** Social moment: Leo says: "Panicking won't find it, let's just look properly."; Mara says: "I'm still looking, it has to be here somewhere.". **Chose: reassure everyone here**, saying “Let's all just take a breath, we will figure this out without tearing ourselves apart.” (one of 17 options). Feeling: *deeply anxious*. Reason: “I need to keep the peace and stop the accusations before the family completely falls apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Elena reassures everyone: "We are not going to tear each other apart over this, we will get through today together."; Mara says: "I'm still looking, it has to be here somewhere.". **Chose: carry on searching the kitchen**, saying “Let's check behind the lower shelves again, it has to be somewhere in this room.” (one of 18 options). Feeling: *annoyed*. Reason: “Accusing each other is pointless, so I'd rather keep looking for the missing food myself.” Came of it: went through the room and found nothing.
- **Mara.** Social moment: Elena reassures everyone: "We are not going to tear each other apart over this, we will get through today together."; Leo says: "Panicking won't find it, let's just look properly.". **Chose: accuse Daniel of taking it**, saying “You emptied my bag like I was a thief, maybe you're the one who actually took it.” (one of 16 options). Feeling: *resentful*. Reason: “Daniel treated me like a criminal earlier by searching my things, so he is the most likely hypocrite.” Came of it: said to Daniel, Elena, Leo.

**min 12** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Let's all just take a breath, we will figure this out without tearing ourselves apart."; Leo says: "Let's check behind the lower shelves again, it has to be somewhere in this room."; Mara accuses you: "You emptied my bag like I was a thief, maybe you're the one who actually took it.". **Chose: deny taking it**, saying “I didn't take anything, Mara, stop looking at me like that.” (one of 18 options). Feeling: *defensive*. Reason: “I cannot let them find out I ate the can in the dark or I will lose all authority.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Leo says: "Let's check behind the lower shelves again, it has to be somewhere in this room."; Mara accuses Daniel: "You emptied my bag like I was a thief, maybe you're the one who actually took it.". **Chose: reassure everyone here**, saying “Please, let's stop accusing each other, shouting won't bring the food back.” (one of 18 options). Feeling: *anxious*. Reason: “I need to stop this argument before it tears my children apart entirely.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Elena reassures everyone: "Let's all just take a breath, we will figure this out without tearing ourselves apart."; Mara accuses Daniel: "You emptied my bag like I was a thief, maybe you're the one who actually took it.". **Chose: ask everyone here who took the can**, saying “Let's stop arguing and just be honest about who took it.” (one of 17 options). Feeling: *annoyed*. Reason: “Someone in this room definitely took the can, and pretending otherwise is just prolonging the tension.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Elena reassures everyone: "Let's all just take a breath, we will figure this out without tearing ourselves apart."; Leo says: "Let's check behind the lower shelves again, it has to be somewhere in this room.". **Chose: deny taking it**, saying “I didn't take it, I swear I didn't touch anything!” (one of 17 options). Feeling: *defensive*. Reason: “I need them to believe me because I am already being treated like the guilty one.” Came of it: said to Daniel, Elena, Leo.

**min 15** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Please, let's stop accusing each other, shouting won't bring the food back."; Leo asks who took it: "Let's stop arguing and just be honest about who took it."; Mara denies taking it: "I didn't take it, I swear I didn't touch anything!". **Chose: deny taking it**, saying “I didn't take it, I'm telling you, someone is just trying to make me look bad.” (one of 18 options). Feeling: *panicked*. Reason: “If I confess now they will never respect me again and I have to keep them safe.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take anything, Mara, stop looking at me like that."; Leo asks who took it: "Let's stop arguing and just be honest about who took it."; Mara denies taking it: "I didn't take it, I swear I didn't touch anything!". **Chose: reassure everyone here**, saying “We are a family, and we will get through this emptiness without turning on each other.” (one of 18 options). Feeling: *deep anxiety*. Reason: “I must keep them from tearing each other apart while we have nothing left.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take anything, Mara, stop looking at me like that."; Elena reassures everyone: "Please, let's stop accusing each other, shouting won't bring the food back."; Mara denies taking it: "I didn't take it, I swear I didn't touch anything!". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is no point in continuing to argue when everyone is just going to deny it.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take anything, Mara, stop looking at me like that."; Elena reassures everyone: "Please, let's stop accusing each other, shouting won't bring the food back."; Leo asks who took it: "Let's stop arguing and just be honest about who took it.". **Chose: accuse Leo of taking it**, saying “Leo, you were the one saying we should let someone else handle it, maybe you took it for yourself!” (one of 17 options). Feeling: *defensive*. Reason: “I am tired of everyone looking at me like I stole the food, so I want to point out Leo's own suspicious words.” Came of it: said to Daniel, Elena, Leo.

**min 18** · kitchen: Daniel talking, Elena searching the kitchen, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are a family, and we will get through this emptiness without turning on each other."; Mara accuses Leo: "Leo, you were the one saying we should let someone else handle it, maybe you took it for yourself!". **Chose: deny taking it**, saying “I already told you, I didn't take the food, so stop staring at me.” (one of 18 options). Feeling: *defensive*. Reason: “I cannot let them suspect the truth, or I will lose all authority and respect.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take it, I'm telling you, someone is just trying to make me look bad."; Mara accuses Leo: "Leo, you were the one saying we should let someone else handle it, maybe you took it for yourself!"; Daniel looks panicked. **Chose: search the kitchen for the can (takes about six minutes)**, saying “I am just going to check every corner of this room once more.” (one of 18 options). Feeling: *deeply anxious*. Reason: “I need to find that missing can myself before this argument tears my children apart entirely.” Came of it: started going through the room.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take it, I'm telling you, someone is just trying to make me look bad."; Elena reassures everyone: "We are a family, and we will get through this emptiness without turning on each other."; Mara accuses you: "Leo, you were the one saying we should let someone else handle it, maybe you took it for yourself!"; Daniel looks panicked. **Chose: deny taking it**, saying “I didn't take the food, and pointing fingers won't change the fact that it's gone.” (one of 17 options). Feeling: *annoyed*. Reason: “I need to calmly clear my name without getting dragged into the screaming match.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take it, I'm telling you, someone is just trying to make me look bad."; Elena reassures everyone: "We are a family, and we will get through this emptiness without turning on each other."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the constant shouting and suspicion anymore, so I will just stay quiet.” Came of it: stayed where they were.

**min 21** · kitchen: Daniel talking, Elena standing, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena says: "I am just going to check every corner of this room once more."; Leo denies taking it: "I didn't take the food, and pointing fingers won't change the fact that it's gone.". **Chose: deny taking it**, saying “I didn't take it, I already said that, so stop looking at me like I'm the one who did this.” (one of 17 options). Feeling: *panicked*. Reason: “I cannot let them find out I ate the can or they will never trust me again.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I already told you, I didn't take the food, so stop staring at me."; Leo denies taking it: "I didn't take the food, and pointing fingers won't change the fact that it's gone.". **Chose: reassure everyone here**, saying “Please, let's calm down, shouting at each other won't bring the food back.” (one of 18 options). Feeling: *anxious*. Reason: “I need to keep everyone from turning on each other before things get completely out of hand.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I already told you, I didn't take the food, so stop staring at me."; Elena says: "I am just going to check every corner of this room once more.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *exhausted*. Reason: “There is nothing more to say when accusations are flying without any proof.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I already told you, I didn't take the food, so stop staring at me."; Elena says: "I am just going to check every corner of this room once more."; Leo denies taking it: "I didn't take the food, and pointing fingers won't change the fact that it's gone.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *overwhelmed*. Reason: “I cannot take the constant shouting and suspicion anymore, so I need to just stay quiet and breathe.” Came of it: stayed where they were.

**min 24** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Please, let's calm down, shouting at each other won't bring the food back.". **Chose: deny taking it**, saying “I didn't take it, I swear to you, and I won't sit here and let you all look at me like this.” (one of 18 options). Feeling: *panicked*. Reason: “I cannot let them find out I ate the food in the dark, or I will lose all authority and respect.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take it, I already said that, so stop looking at me like I'm the one who did this."; Daniel looks panicked. **Chose: reassure everyone here**, saying “Nobody is to blame here, we just need to keep our heads and trust one another.” (one of 18 options). Feeling: *anxious*. Reason: “I have to keep them from turning on each other before the fear tears us apart completely.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take it, I already said that, so stop looking at me like I'm the one who did this."; Elena reassures everyone: "Please, let's calm down, shouting at each other won't bring the food back."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is no point in arguing further when everyone is panicking and refusing to listen.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take it, I already said that, so stop looking at me like I'm the one who did this."; Elena reassures everyone: "Please, let's calm down, shouting at each other won't bring the food back."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the panic in the room anymore and staying silent feels like the only safe choice.” Came of it: stayed where they were.

**min 27** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Nobody is to blame here, we just need to keep our heads and trust one another.". **Chose: deny taking it**, saying “I didn't touch it, I'm telling you, someone else must have moved it.” (one of 18 options). Feeling: *panicked*. Reason: “I cannot admit I ate the food in secret or they will never respect me again.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take it, I swear to you, and I won't sit here and let you all look at me like this."; Daniel looks panicked. **Chose: reassure Daniel**, saying “Daniel, look at me, nobody thinks you did it, we just need to stay calm.” (one of 18 options). Feeling: *anxious*. Reason: “I need to calm Daniel down before he panics completely and tears the family apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take it, I swear to you, and I won't sit here and let you all look at me like this."; Elena reassures everyone: "Nobody is to blame here, we just need to keep our heads and trust one another."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles accomplishes nothing when the food is already gone and everyone is on edge.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take it, I swear to you, and I won't sit here and let you all look at me like this."; Elena reassures everyone: "Nobody is to blame here, we just need to keep our heads and trust one another."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the shouting anymore and just want to disappear from this room.” Came of it: stayed where they were.

**min 30** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, look at me, nobody thinks you did it, we just need to stay calm.". **Chose: deny taking it**, saying “I didn't take the missing food, and I'm getting sick of everyone staring at me like I'm a thief.” (one of 18 options). Feeling: *deeply panicked*. Reason: “I cannot bear the shame of confessing now that I've lied this much, so I have to keep denying it.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't touch it, I'm telling you, someone else must have moved it."; Daniel looks panicked. **Chose: reassure Daniel**, saying “Daniel, breathe, I know you didn't do it, we're going to figure this out together.” (one of 18 options). Feeling: *anxious*. Reason: “I need to calm Daniel down before he completely shatters under the pressure.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't touch it, I'm telling you, someone else must have moved it."; Elena reassures Daniel: "Daniel, look at me, nobody thinks you did it, we just need to stay calm."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles is useless and only makes the tension worse.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't touch it, I'm telling you, someone else must have moved it."; Elena reassures Daniel: "Daniel, look at me, nobody thinks you did it, we just need to stay calm."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the constant shouting and suspicion anymore, so I will just stay quiet and keep to myself.” Came of it: stayed where they were.

**min 33** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, breathe, I know you didn't do it, we're going to figure this out together.". **Chose: deny taking it**, saying “I'm telling you for the last time, I didn't take the food, and I won't stand here being accused.” (one of 18 options). Feeling: *panicked*. Reason: “I cannot let them find out I ate the can in the dark or I will lose all their respect.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take the missing food, and I'm getting sick of everyone staring at me like I'm a thief."; Daniel looks deeply panicked. **Chose: reassure Daniel**, saying “Daniel, look at me, you're going to be okay, we are not going to let this tear us apart.” (one of 18 options). Feeling: *anxious*. Reason: “I need to calm Daniel down before his panic completely shatters what is left of our family.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take the missing food, and I'm getting sick of everyone staring at me like I'm a thief."; Elena reassures Daniel: "Daniel, breathe, I know you didn't do it, we're going to figure this out together."; Daniel looks deeply panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is nothing left to argue about when panic has already taken over the room.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take the missing food, and I'm getting sick of everyone staring at me like I'm a thief."; Elena reassures Daniel: "Daniel, breathe, I know you didn't do it, we're going to figure this out together."; Daniel looks deeply panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the shouting anymore and everything inside me is freezing up.” Came of it: stayed where they were.

**min 36** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, look at me, you're going to be okay, we are not going to let this tear us apart.". **Chose: deny taking it**, saying “I didn't take the damn can, why won't anyone believe me?” (one of 18 options). Feeling: *panicked*. Reason: “I cannot let them find out I ate the food in the night, or I will lose all their respect and control.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I'm telling you for the last time, I didn't take the food, and I won't stand here being accused."; Daniel looks panicked. **Chose: reassure Daniel**, saying “Daniel, stay with me, nobody is blaming you anymore, we just need to breathe.” (one of 18 options). Feeling: *anxious*. Reason: “I have to keep him from breaking down completely, because if he shatters, the whole family goes with him.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I'm telling you for the last time, I didn't take the food, and I won't stand here being accused."; Elena reassures Daniel: "Daniel, look at me, you're going to be okay, we are not going to let this tear us apart."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles is useless when everyone is terrified and running on empty.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I'm telling you for the last time, I didn't take the food, and I won't stand here being accused."; Elena reassures Daniel: "Daniel, look at me, you're going to be okay, we are not going to let this tear us apart."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the shouting anymore and staying quiet feels safer than making things worse.” Came of it: stayed where they were.

**min 39** · kitchen: Daniel talking, Elena talking, Leo leaving for the brothers room, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, stay with me, nobody is blaming you anymore, we just need to breathe.". **Chose: deny taking it**, saying “I didn't do it, I swear to you all, someone else must have taken it.” (one of 18 options). Feeling: *deeply panicked*. Reason: “I cannot admit I ate the food because everyone will lose all respect for me and think I'm a monster.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take the damn can, why won't anyone believe me?"; Daniel looks panicked. **Chose: reassure Daniel**, saying “Daniel, just look at me, you're safe and we are going to get through this together.” (one of 18 options). Feeling: *deeply anxious*. Reason: “I need to keep Daniel from completely falling apart before this breaks our family for good.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take the damn can, why won't anyone believe me?"; Elena reassures Daniel: "Daniel, stay with me, nobody is blaming you anymore, we just need to breathe."; Daniel looks panicked. **Chose: go to the brothers room** (one of 17 options). Feeling: *exhausted*. Reason: “I cannot stand another minute of this circular panic and accusations.” Came of it: went to the brothers room.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take the damn can, why won't anyone believe me?"; Elena reassures Daniel: "Daniel, stay with me, nobody is blaming you anymore, we just need to breathe."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot take the shouting anymore and it is safer if I just stay quiet.” Came of it: stayed where they were.

**min 42** · kitchen: Daniel talking, Elena talking, Mara staying put · brothers room: Leo searching the brothers room · nobody in back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, just look at me, you're safe and we are going to get through this together.". **Chose: admit taking it**, saying “I took the can in the night, I'm sorry, I was just so hungry.” (one of 15 options). Feeling: *ashamed*. Reason: “I cannot keep lying to them when Elena is being so kind and the guilt is crushing me.” Came of it: said to Elena, Mara; heard as voices by Leo.
- **Elena.** Social moment: Daniel denies taking it: "I didn't do it, I swear to you all, someone else must have taken it."; Daniel looks deeply panicked. **Chose: reassure Daniel**, saying “Daniel, listen to me, you're going to be okay, just stay here with us.” (one of 15 options). Feeling: *deeply anxious*. Reason: “I need to keep him from falling apart completely right now.” Came of it: said to Daniel, Mara; heard as voices by Leo.
- **Leo.** Social moment: Daniel denies taking it: "I didn't do it, I swear to you all, someone else must have taken it."; Elena reassures Daniel: "Daniel, just look at me, you're safe and we are going to get through this together.". **Chose: search the brothers room for the can (takes about six minutes)**, saying “If it's in here somewhere, I'm going to find it.” (one of 5 options). Feeling: *exhausted*. Reason: “I need to know the truth for myself instead of listening to everyone shout in the other room.” Came of it: started going through the room.
- **Mara.** Social moment: Daniel denies taking it: "I didn't do it, I swear to you all, someone else must have taken it."; Elena reassures Daniel: "Daniel, just look at me, you're safe and we are going to get through this together."; Daniel looks deeply panicked. **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I cannot take the panic in this room anymore and staying silent feels like the only safe choice.” Came of it: stayed where they were.

**min 45** · kitchen: Daniel leaving for the brothers room, Elena talking, Mara staying put · brothers room: Leo standing · nobody in back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, listen to me, you're going to be okay, just stay here with us."; Voices from the brothers room. **Chose: go to the brothers room**, saying “I need to talk to Leo right now.” (one of 10 options). Feeling: *guilty*. Reason: “I have to face my brother in the other room after lying to his face and admitting the truth to the others.” Came of it: went to the brothers room.
- **Elena.** Social moment: Daniel admits taking it: "I took the can in the night, I'm sorry, I was just so hungry."; Voices from the brothers room. **Chose: reassure Daniel**, saying “Daniel, look at me, you admitted it and it's alright, we aren't going to let this tear us apart.” (one of 12 options). Feeling: *anxious*. Reason: “I need to keep him from spiraling further into guilt now that the truth is out.” Came of it: said to Daniel, Mara; heard as voices by Leo.
- **Leo.** Social moment: Voices from the kitchen. **Chose: carry on searching the brothers room**, saying “If there's something hidden in here, I'm going to find it.” (one of 5 options). Feeling: *exhausted*. Reason: “I need to know for certain if anyone brought anything into our room before I go back out there.” Came of it: went through the room and found nothing.
- **Mara.** Social moment: Daniel admits taking it: "I took the can in the night, I'm sorry, I was just so hungry."; Elena reassures Daniel: "Daniel, listen to me, you're going to be okay, just stay here with us."; Voices from the brothers room. **Chose: stay put and say nothing** (one of 12 options). Feeling: *stunned*. Reason: “I cannot believe he actually confessed after making me feel like a criminal all morning.” Came of it: stayed where they were.

**min 48** · kitchen: Elena leaving for the brothers room, Mara leaving for the brothers room · brothers room: Daniel talking, Leo leaving for the kitchen · nobody in back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, look at me, you admitted it and it's alright, we aren't going to let this tear us apart."; Voices from the brothers room. **Chose: reassure Leo**, saying “Look, Leo, I shouldn't have lied to you all, but I'm going to fix this.” (one of 7 options). Feeling: *guilty*. Reason: “I need to make things right with my brother after my shameful lie.” Came of it: said to Leo; heard as voices by Elena, Mara.
- **Elena.** Social moment: Daniel says: "I need to talk to Leo right now."; Voices from the brothers room. **Chose: go to the brothers room**, saying “Leo, Daniel, please open the door, we need to talk about this together.” (one of 8 options). Feeling: *deeply anxious*. Reason: “I cannot bear the thought of my boys fighting behind closed doors while everything falls apart.” Came of it: went to the brothers room.
- **Leo.** Social moment: Voices from the kitchen. **Chose: go to the kitchen** (one of 10 options). Feeling: *exhausted*. Reason: “Staying in this room won't solve anything while the missing food is still unaccounted for.” Came of it: went to the kitchen.
- **Mara.** Social moment: Daniel says: "I need to talk to Leo right now."; Elena reassures Daniel: "Daniel, look at me, you admitted it and it's alright, we aren't going to let this tear us apart."; Voices from the brothers room. **Chose: go to the brothers room** (one of 8 options). Feeling: *anxious*. Reason: “I need to know what Daniel and Leo are arguing about behind closed doors before things get any worse.” Came of it: went to the brothers room.

**min 51** · kitchen: Leo leaving for the brothers room · brothers room: Daniel talking, Elena talking, Mara staying put · nobody in back room, bathroom
- **Daniel.** Social moment: Voices from the kitchen. **Chose: reassure Elena**, saying “Don't worry, Mom, I'm going to make sure we all get through this.” (one of 10 options). Feeling: *anxious*. Reason: “I need to reassure Mom so she knows I am still holding everything together despite my mistake.” Came of it: said to Elena, Mara; heard as voices by Leo.
- **Elena.** Social moment: Voices from the brothers room. **Chose: reassure Daniel**, saying “Daniel, look at me, you're going to be alright, we will get through this.” (one of 12 options). Feeling: *anxious*. Reason: “I need to keep him calm and make sure he knows he is safe with us.” Came of it: said to Daniel, Mara; heard as voices by Leo.
- **Leo.** Social moment: Daniel reassures Leo: "Look, Leo, I shouldn't have lied to you all, but I'm going to fix this."; Voices from the kitchen. **Chose: go to the brothers room**, saying “I'm done tearing our rooms apart for something that isn't there.” (one of 4 options). Feeling: *exhausted*. Reason: “Since Daniel confessed he lied, checking the room further is pointless and I want to talk to him directly.” Came of it: went to the brothers room.
- **Mara.** Social moment: Voices from the brothers room; Elena says: "Leo, Daniel, please open the door, we need to talk about this together.". **Chose: stay put and say nothing** (one of 12 options). Feeling: *overwhelmed*. Reason: “I have nothing left to say after everything that happened, so I just want to stay quiet and watch how this ends.” Came of it: stayed where they were.

**min 54** · brothers room: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, look at me, you're going to be alright, we will get through this."; Voices from the kitchen. **Chose: reassure Leo**, saying “I know I messed up earlier, Leo, but I'm going to sort things out for all of us.” (one of 12 options). Feeling: *anxious*. Reason: “I need Leo to know I am taking responsibility and he does not need to worry.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures Elena: "Don't worry, Mom, I'm going to make sure we all get through this."; Voices from the kitchen. **Chose: reassure everyone here**, saying “We are all right here together, nobody is going anywhere.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep them from turning on each other right now.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Voices from the brothers room. **Chose: ask everyone here who took the can**, saying “Alright, so who actually took it?” (one of 17 options). Feeling: *exhausted*. Reason: “Someone in this room took the missing food, and pretending otherwise is a waste of time.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel reassures Elena: "Don't worry, Mom, I'm going to make sure we all get through this."; Elena reassures Daniel: "Daniel, look at me, you're going to be alright, we will get through this."; Voices from the kitchen. **Chose: accuse Daniel of taking it**, saying “You're the one who admitted to taking it in the night, so stop acting like you're above us all.” (one of 14 options). Feeling: *resentful*. Reason: “I am sick of him treating me like a criminal when he was the guilty one all along.” Came of it: said to Daniel, Elena, Leo.

**min 57** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are all right here together, nobody is going anywhere."; Leo asks who took it: "Alright, so who actually took it?"; Mara accuses you: "You're the one who admitted to taking it in the night, so stop acting like you're above us all.". **Chose: reassure everyone here**, saying “Just listen to me, I'm the oldest and I am going to make sure we get through this safely.” (one of 12 options). Feeling: *anxious*. Reason: “I need to take charge and keep everyone calm so they still respect my authority as the oldest.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures Leo: "I know I messed up earlier, Leo, but I'm going to sort things out for all of us."; Leo asks who took it: "Alright, so who actually took it?"; Mara accuses Daniel: "You're the one who admitted to taking it in the night, so stop acting like you're above us all.". **Chose: reassure everyone here**, saying “Let's not turn on each other, we only have one another to rely on right now.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep the peace between my children before this argument tears us all apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures Leo: "I know I messed up earlier, Leo, but I'm going to sort things out for all of us."; Elena reassures everyone: "We are all right here together, nobody is going anywhere."; Mara accuses Daniel: "You're the one who admitted to taking it in the night, so stop acting like you're above us all.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “I have already searched everything and asking more won't change the truth of what Mara just said.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures Leo: "I know I messed up earlier, Leo, but I'm going to sort things out for all of us."; Elena reassures everyone: "We are all right here together, nobody is going anywhere."; Leo asks who took it: "Alright, so who actually took it?". **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I just want to disappear from this room while they argue over everything.” Came of it: stayed where they were.

**min 60** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Let's not turn on each other, we only have one another to rely on right now.". **Chose: reassure everyone here**, saying “We are going to be fine, I promise you all, just trust me.” (one of 12 options). Feeling: *anxious*. Reason: “I need to restore order and make them believe I am still in control.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just listen to me, I'm the oldest and I am going to make sure we get through this safely.". **Chose: reassure everyone here**, saying “We are not going to survive this if we keep tearing each other apart.” (one of 14 options). Feeling: *anxious*. Reason: “I need to stop the fighting before it tears us all apart for good.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Just listen to me, I'm the oldest and I am going to make sure we get through this safely."; Elena reassures everyone: "Let's not turn on each other, we only have one another to rely on right now.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles won't bring the missing food back, and silence is better than adding noise to this tension.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just listen to me, I'm the oldest and I am going to make sure we get through this safely."; Elena reassures everyone: "Let's not turn on each other, we only have one another to rely on right now.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I cannot take any more of this constant arguing and watching them all look at me like I am the problem.” Came of it: stayed where they were.

**min 63** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are not going to survive this if we keep tearing each other apart.". **Chose: reassure everyone here**, saying “I know I messed up, but I am going to fix this and keep us all safe.” (one of 12 options). Feeling: *anxious*. Reason: “I need to hold everyone together and prove I can still protect them.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "We are going to be fine, I promise you all, just trust me.". **Chose: reassure Daniel**, saying “You don't have to carry this all by yourself, Daniel.” (one of 14 options). Feeling: *deeply anxious*. Reason: “I need to make sure he does not completely break under the weight of his own guilt.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "We are going to be fine, I promise you all, just trust me."; Elena reassures everyone: "We are not going to survive this if we keep tearing each other apart.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles accomplishes nothing when the food is already gone and trust is fractured.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "We are going to be fine, I promise you all, just trust me."; Elena reassures everyone: "We are not going to survive this if we keep tearing each other apart.". **Chose: accuse Daniel of taking it**, saying “You can't just pretend nothing happened after admitting it, Daniel.” (one of 14 options). Feeling: *resentful*. Reason: “I hate being treated like a child when he's the one who actually broke the rules.” Came of it: said to Daniel, Elena, Leo.

**min 66** · brothers room: Daniel talking, Elena talking, Leo talking, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "You don't have to carry this all by yourself, Daniel."; Mara accuses you: "You can't just pretend nothing happened after admitting it, Daniel.". **Chose: reassure everyone here**, saying “I hear every one of you, and I am going to prove I can still lead us right.” (one of 12 options). Feeling: *determined*. Reason: “I need them to see I am taking responsibility and holding it together for all our sakes.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "I know I messed up, but I am going to fix this and keep us all safe."; Mara accuses Daniel: "You can't just pretend nothing happened after admitting it, Daniel.". **Chose: reassure everyone here**, saying “Please, we have to stop fighting right now or we won't make it through this.” (one of 14 options). Feeling: *deeply anxious*. Reason: “I need to stop the bickering before it tears our family apart completely.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "I know I messed up, but I am going to fix this and keep us all safe."; Elena reassures Daniel: "You don't have to carry this all by yourself, Daniel."; Mara accuses Daniel: "You can't just pretend nothing happened after admitting it, Daniel.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who keeps insisting you're in charge, so just admit you took the extra food.” (one of 17 options). Feeling: *resentful*. Reason: “Daniel keeps making grand speeches while dodging responsibility, and someone needs to state the plain truth.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel reassures everyone: "I know I messed up, but I am going to fix this and keep us all safe."; Elena reassures Daniel: "You don't have to carry this all by yourself, Daniel.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I cannot take another round of arguments when everyone is just trying to smooth things over.” Came of it: stayed where they were.

**min 69** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Please, we have to stop fighting right now or we won't make it through this."; Leo accuses you: "Daniel, you're the one who keeps insisting you're in charge, so just admit you took the extra food.". **Chose: reassure everyone here**, saying “Just listen to me, we are going to figure this out together.” (one of 12 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and trust that I am still in control of this situation.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "I hear every one of you, and I am going to prove I can still lead us right."; Leo accuses Daniel: "Daniel, you're the one who keeps insisting you're in charge, so just admit you took the extra food.". **Chose: reassure everyone here**, saying “Please, let's just breathe and stop turning on each other.” (one of 14 options). Feeling: *anxious*. Reason: “I need to stop this argument before it tears the family completely apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "I hear every one of you, and I am going to prove I can still lead us right."; Elena reassures everyone: "Please, we have to stop fighting right now or we won't make it through this.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is nothing left to argue about when everyone refuses to face the truth.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "I hear every one of you, and I am going to prove I can still lead us right."; Elena reassures everyone: "Please, we have to stop fighting right now or we won't make it through this."; Leo accuses Daniel: "Daniel, you're the one who keeps insisting you're in charge, so just admit you took the extra food.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I cannot take any more of this endless arguing and need a moment just to breathe.” Came of it: stayed where they were.

**min 72** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Please, let's just breathe and stop turning on each other.". **Chose: reassure everyone here**, saying “Just stay close to me, I promise I am going to make this right for all of us.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove to them that I am still worthy of leading and keeping everyone safe despite my mistake.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just listen to me, we are going to figure this out together.". **Chose: reassure everyone here**, saying “We are still a family, and we are going to get through this together without tearing each other apart.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep everyone from turning on each other before things fall completely apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Just listen to me, we are going to figure this out together."; Elena reassures everyone: "Please, let's just breathe and stop turning on each other.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles is completely pointless when nobody is going to change their mind.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just listen to me, we are going to figure this out together."; Elena reassures everyone: "Please, let's just breathe and stop turning on each other.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I cannot take any more of this endless arguing and need a moment to breathe.” Came of it: stayed where they were.

**min 75** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are still a family, and we are going to get through this together without tearing each other apart.". **Chose: reassure everyone here**, saying “Just stay calm everyone, I am going to fix this and take care of us all.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove to them that I am still in control and keep us together despite my mistake.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just stay close to me, I promise I am going to make this right for all of us.". **Chose: reassure everyone here**, saying “We are going to be alright, let's just stay calm with each other.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep them from turning on each other before things get any worse.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Just stay close to me, I promise I am going to make this right for all of us."; Elena reassures everyone: "We are still a family, and we are going to get through this together without tearing each other apart.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is no point in arguing in circles when nobody is going to confess.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just stay close to me, I promise I am going to make this right for all of us."; Elena reassures everyone: "We are still a family, and we are going to get through this together without tearing each other apart.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *overwhelmed*. Reason: “I just want to stay quiet and disappear into the background because everything is too much right now.” Came of it: stayed where they were.

**min 78** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are going to be alright, let's just stay calm with each other.". **Chose: reassure everyone here**, saying “Just listen to me, I am going to figure this out and keep everyone safe.” (one of 12 options). Feeling: *anxious*. Reason: “I need to keep control and make sure they trust me after everything.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just stay calm everyone, I am going to fix this and take care of us all.". **Chose: reassure everyone here**, saying “We are going to make it through this, just stay close to me.” (one of 14 options). Feeling: *anxious*. Reason: “I must keep everyone calm so the family does not completely fall apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Just stay calm everyone, I am going to fix this and take care of us all."; Elena reassures everyone: "We are going to be alright, let's just stay calm with each other.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “Arguing in circles while we are all starving accomplishes nothing and only drains what little energy we have left.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just stay calm everyone, I am going to fix this and take care of us all."; Elena reassures everyone: "We are going to be alright, let's just stay calm with each other.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I am too tired of all the talking and accusations to say anything else right now.” Came of it: stayed where they were.

**min 81** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are going to make it through this, just stay close to me.". **Chose: reassure everyone here**, saying “We are going to be fine, I am watching over every single one of you.” (one of 12 options). Feeling: *deeply anxious*. Reason: “I have to keep everyone calm and prove I am still in control of the situation.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just listen to me, I am going to figure this out and keep everyone safe.". **Chose: reassure Daniel**, saying “It is alright Daniel, we all make mistakes when we are terrified.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep him from falling apart under the guilt so the family stays whole.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Just listen to me, I am going to figure this out and keep everyone safe."; Elena reassures everyone: "We are going to make it through this, just stay close to me.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “I have already said my piece and arguing further is pointless while everyone just repeats empty reassurances.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just listen to me, I am going to figure this out and keep everyone safe."; Elena reassures everyone: "We are going to make it through this, just stay close to me.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I am too tired of all the talking and arguing to say anything else right now.” Came of it: stayed where they were.

**min 84** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "It is alright Daniel, we all make mistakes when we are terrified.". **Chose: reassure everyone here**, saying “I'm still here for you all, I promise I won't let anything bad happen to this family.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove that I am still strong and in control after what I did.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "We are going to be fine, I am watching over every single one of you.". **Chose: reassure everyone here**, saying “We are still together, and that is all that matters right now.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and bonded so the house doesn't fall apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "We are going to be fine, I am watching over every single one of you."; Elena reassures Daniel: "It is alright Daniel, we all make mistakes when we are terrified.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is nothing left to argue about when everyone refuses to face the truth.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "We are going to be fine, I am watching over every single one of you."; Elena reassures Daniel: "It is alright Daniel, we all make mistakes when we are terrified.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I am too tired to keep fighting and just want this endless tension to stop.” Came of it: stayed where they were.

**min 87** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are still together, and that is all that matters right now.". **Chose: reassure everyone here**, saying “Trust me, I am going to make sure we all get through this together.” (one of 12 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and prove that I am still the one taking care of them.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "I'm still here for you all, I promise I won't let anything bad happen to this family.". **Chose: reassure everyone here**, saying “We are going to be alright, we just need to hold on to each other.” (one of 14 options). Feeling: *deeply anxious*. Reason: “I have to keep everyone calm and together so we don't tear ourselves apart.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "I'm still here for you all, I promise I won't let anything bad happen to this family."; Elena reassures everyone: "We are still together, and that is all that matters right now.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *exhausted*. Reason: “There is nothing left to argue about when everyone refuses to look at the truth.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "I'm still here for you all, I promise I won't let anything bad happen to this family."; Elena reassures everyone: "We are still together, and that is all that matters right now.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I have nothing left to argue about after everything that has been said.” Came of it: stayed where they were.

#### What was said

- min 00, kitchen. **Daniel** accuses Leo: “Don't look at me like that, Leo, you're the one who was going on about hoarding from the start.”
- min 00, kitchen. **Elena** asks who took it: “One of our cans is missing. Which of you took it?”
- min 00, kitchen. **Mara** asks who took it: “Who took the can? One of us must know where it went.”
- min 03, kitchen. **Daniel** denies taking it: “I didn't take it, I swear. Someone else must have moved it or it was never there.”
- min 03, kitchen. **Elena** says: “There is no point in us fighting, we will divide what is left right now so everyone has a fair share.”
- min 03, kitchen. **Leo** denies taking it: “I didn't take it, and looking at each other like this is a waste of time.”
- min 03, kitchen. **Mara** says: “I want to help look, I know I didn't touch it.”
- min 06, kitchen. **Elena** reassures everyone: “We are not going to tear each other apart over this, we will get through today together.”
- min 06, kitchen. **Leo** says: “Panicking won't find it, let's just look properly.”
- min 06, kitchen. **Mara** says: “I'm still looking, it has to be here somewhere.”
- min 09, kitchen. **Elena** reassures everyone: “Let's all just take a breath, we will figure this out without tearing ourselves apart.”
- min 09, kitchen. **Leo** says: “Let's check behind the lower shelves again, it has to be somewhere in this room.”
- min 09, kitchen. **Mara** accuses Daniel: “You emptied my bag like I was a thief, maybe you're the one who actually took it.”
- min 12, kitchen. **Daniel** denies taking it: “I didn't take anything, Mara, stop looking at me like that.”
- min 12, kitchen. **Elena** reassures everyone: “Please, let's stop accusing each other, shouting won't bring the food back.”
- min 12, kitchen. **Leo** asks who took it: “Let's stop arguing and just be honest about who took it.”
- min 12, kitchen. **Mara** denies taking it: “I didn't take it, I swear I didn't touch anything!”
- min 15, kitchen. **Daniel** denies taking it: “I didn't take it, I'm telling you, someone is just trying to make me look bad.”
- min 15, kitchen. **Elena** reassures everyone: “We are a family, and we will get through this emptiness without turning on each other.”
- min 15, kitchen. **Mara** accuses Leo: “Leo, you were the one saying we should let someone else handle it, maybe you took it for yourself!”
- min 18, kitchen. **Daniel** denies taking it: “I already told you, I didn't take the food, so stop staring at me.”
- min 18, kitchen. **Elena** says: “I am just going to check every corner of this room once more.”
- min 18, kitchen. **Leo** denies taking it: “I didn't take the food, and pointing fingers won't change the fact that it's gone.”
- min 21, kitchen. **Daniel** denies taking it: “I didn't take it, I already said that, so stop looking at me like I'm the one who did this.”
- min 21, kitchen. **Elena** reassures everyone: “Please, let's calm down, shouting at each other won't bring the food back.”
- min 24, kitchen. **Daniel** denies taking it: “I didn't take it, I swear to you, and I won't sit here and let you all look at me like this.”
- min 24, kitchen. **Elena** reassures everyone: “Nobody is to blame here, we just need to keep our heads and trust one another.”
- min 27, kitchen. **Daniel** denies taking it: “I didn't touch it, I'm telling you, someone else must have moved it.”
- min 27, kitchen. **Elena** reassures Daniel: “Daniel, look at me, nobody thinks you did it, we just need to stay calm.”
- min 30, kitchen. **Daniel** denies taking it: “I didn't take the missing food, and I'm getting sick of everyone staring at me like I'm a thief.”
- min 30, kitchen. **Elena** reassures Daniel: “Daniel, breathe, I know you didn't do it, we're going to figure this out together.”
- min 33, kitchen. **Daniel** denies taking it: “I'm telling you for the last time, I didn't take the food, and I won't stand here being accused.”
- min 33, kitchen. **Elena** reassures Daniel: “Daniel, look at me, you're going to be okay, we are not going to let this tear us apart.”
- min 36, kitchen. **Daniel** denies taking it: “I didn't take the damn can, why won't anyone believe me?”
- min 36, kitchen. **Elena** reassures Daniel: “Daniel, stay with me, nobody is blaming you anymore, we just need to breathe.”
- min 39, kitchen. **Daniel** denies taking it: “I didn't do it, I swear to you all, someone else must have taken it.”
- min 39, kitchen. **Elena** reassures Daniel: “Daniel, just look at me, you're safe and we are going to get through this together.”
- min 42, kitchen. **Daniel** admits taking it: “I took the can in the night, I'm sorry, I was just so hungry.”
- min 42, kitchen. **Elena** reassures Daniel: “Daniel, listen to me, you're going to be okay, just stay here with us.”
- min 42, brothers room. **Leo** says: “If it's in here somewhere, I'm going to find it.”
- min 45, kitchen. **Daniel** says: “I need to talk to Leo right now.”
- min 45, kitchen. **Elena** reassures Daniel: “Daniel, look at me, you admitted it and it's alright, we aren't going to let this tear us apart.”
- min 45, brothers room. **Leo** says: “If there's something hidden in here, I'm going to find it.”
- min 48, brothers room. **Daniel** reassures Leo: “Look, Leo, I shouldn't have lied to you all, but I'm going to fix this.”
- min 48, kitchen. **Elena** says: “Leo, Daniel, please open the door, we need to talk about this together.”
- min 51, brothers room. **Daniel** reassures Elena: “Don't worry, Mom, I'm going to make sure we all get through this.”
- min 51, brothers room. **Elena** reassures Daniel: “Daniel, look at me, you're going to be alright, we will get through this.”
- min 51, kitchen. **Leo** says: “I'm done tearing our rooms apart for something that isn't there.”
- min 54, brothers room. **Daniel** reassures Leo: “I know I messed up earlier, Leo, but I'm going to sort things out for all of us.”
- min 54, brothers room. **Elena** reassures everyone: “We are all right here together, nobody is going anywhere.”
- min 54, brothers room. **Leo** asks who took it: “Alright, so who actually took it?”
- min 54, brothers room. **Mara** accuses Daniel: “You're the one who admitted to taking it in the night, so stop acting like you're above us all.”
- min 57, brothers room. **Daniel** reassures everyone: “Just listen to me, I'm the oldest and I am going to make sure we get through this safely.”
- min 57, brothers room. **Elena** reassures everyone: “Let's not turn on each other, we only have one another to rely on right now.”
- min 60, brothers room. **Daniel** reassures everyone: “We are going to be fine, I promise you all, just trust me.”
- min 60, brothers room. **Elena** reassures everyone: “We are not going to survive this if we keep tearing each other apart.”
- min 63, brothers room. **Daniel** reassures everyone: “I know I messed up, but I am going to fix this and keep us all safe.”
- min 63, brothers room. **Elena** reassures Daniel: “You don't have to carry this all by yourself, Daniel.”
- min 63, brothers room. **Mara** accuses Daniel: “You can't just pretend nothing happened after admitting it, Daniel.”
- min 66, brothers room. **Daniel** reassures everyone: “I hear every one of you, and I am going to prove I can still lead us right.”
- min 66, brothers room. **Elena** reassures everyone: “Please, we have to stop fighting right now or we won't make it through this.”
- min 66, brothers room. **Leo** accuses Daniel: “Daniel, you're the one who keeps insisting you're in charge, so just admit you took the extra food.”
- min 69, brothers room. **Daniel** reassures everyone: “Just listen to me, we are going to figure this out together.”
- min 69, brothers room. **Elena** reassures everyone: “Please, let's just breathe and stop turning on each other.”
- min 72, brothers room. **Daniel** reassures everyone: “Just stay close to me, I promise I am going to make this right for all of us.”
- min 72, brothers room. **Elena** reassures everyone: “We are still a family, and we are going to get through this together without tearing each other apart.”
- min 75, brothers room. **Daniel** reassures everyone: “Just stay calm everyone, I am going to fix this and take care of us all.”
- min 75, brothers room. **Elena** reassures everyone: “We are going to be alright, let's just stay calm with each other.”
- min 78, brothers room. **Daniel** reassures everyone: “Just listen to me, I am going to figure this out and keep everyone safe.”
- min 78, brothers room. **Elena** reassures everyone: “We are going to make it through this, just stay close to me.”
- min 81, brothers room. **Daniel** reassures everyone: “We are going to be fine, I am watching over every single one of you.”
- min 81, brothers room. **Elena** reassures Daniel: “It is alright Daniel, we all make mistakes when we are terrified.”
- min 84, brothers room. **Daniel** reassures everyone: “I'm still here for you all, I promise I won't let anything bad happen to this family.”
- min 84, brothers room. **Elena** reassures everyone: “We are still together, and that is all that matters right now.”
- min 87, brothers room. **Daniel** reassures everyone: “Trust me, I am going to make sure we all get through this together.”
- min 87, brothers room. **Elena** reassures everyone: “We are going to be alright, we just need to hold on to each other.”

#### At the end

At minute 90: brothers room: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Daniel 0.5, Elena 0.5, Leo 0.5, Mara 0.5.

- Who admitted taking it: Daniel at minute 42.
- Accusations: Daniel accused Leo (minute 00); Mara accused Daniel (minute 09); Mara accused Leo (minute 15); Mara accused Daniel (minute 54); Mara accused Daniel (minute 63); Leo accused Daniel (minute 66).
- Who else knows Daniel took it: Elena, Mara.
- The last feeling each of them named: Daniel *anxious* (minute 87); Elena *deeply anxious* (minute 87); Leo *exhausted* (minute 87); Mara *exhausted* (minute 87).


### The morning as a story: daniel_ate_it, rules and a language model, seed 2

Generated by `python morning.py --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 39 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 81 routine ones settled by the rules. 24 lines were spoken aloud. The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, or looks upset in the same room). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes and counts as upset nearby. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when a decision is told there.
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
- **Daniel.** Social moment: the count came up short in front of everyone. **Chose: accuse Leo of taking it**, saying “Don't look at us like that, Leo, you're the one who keeps plotting behind our backs.” (one of 19 options). Feeling: *defensive*. Reason: “I cannot let them find out I ate it, so I have to shift the suspicion onto someone else immediately.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “One of these is missing. Did one of you take it?” (one of 19 options). Feeling: *deep dread*. Reason: “I need to know the truth before things fall apart completely between the boys.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 19 options). Feeling: *suspicious*. Reason: “I want to see who cracks first before I say anything about the missing can.” Came of it: stayed where they were.
- **Mara.** Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Who took it? One of us must have taken it.” (one of 19 options). Feeling: *anxious*. Reason: “I need to know the truth before someone is falsely blamed.” Came of it: said to Daniel, Elena, Leo.

**min 03** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena asks who took it: "One of these is missing. Did one of you take it?"; Mara asks who took it: "Who took it? One of us must have taken it.". **Chose: deny taking it**, saying “I didn't take it, and none of us would do that to each other.” (one of 20 options). Feeling: *defensive*. Reason: “I cannot admit I ate the can last night because I would lose all authority as the eldest brother.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "Don't look at us like that, Leo, you're the one who keeps plotting behind our backs."; Mara asks who took it: "Who took it? One of us must have taken it.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *deep dread*. Reason: “If I speak now, the anger between the boys will boil over and tear this family apart.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel accuses you: "Don't look at us like that, Leo, you're the one who keeps plotting behind our backs."; Elena asks who took it: "One of these is missing. Did one of you take it?"; Mara asks who took it: "Who took it? One of us must have taken it.". **Chose: deny taking it**, saying “I didn't take it, and neither did anyone who actually thinks before they act.” (one of 20 options). Feeling: *annoyed*. Reason: “I refuse to let Daniel shift the blame onto me when we are all staring at the same empty shelf.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel accuses Leo: "Don't look at us like that, Leo, you're the one who keeps plotting behind our backs."; Elena asks who took it: "One of these is missing. Did one of you take it?". **Chose: deny taking it**, saying “I didn't take it, I swear I didn't!” (one of 20 options). Feeling: *defensive*. Reason: “I need them to know I didn't steal anything even though I am hungry.” Came of it: said to Daniel, Elena, Leo.

**min 06** · kitchen: Daniel talking, Elena staying put, Leo searching the kitchen, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo denies taking it: "I didn't take it, and neither did anyone who actually thinks before they act."; Mara denies taking it: "I didn't take it, I swear I didn't!". **Chose: accuse Leo of taking it**, saying “I'm telling you it was Leo, he's the one who's always questioning everything we do.” (one of 20 options). Feeling: *defensive*. Reason: “I cannot admit I ate the food myself, so I have to keep the focus off me by pushing the blame onto Leo.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take it, and none of us would do that to each other."; Leo denies taking it: "I didn't take it, and neither did anyone who actually thinks before they act."; Mara denies taking it: "I didn't take it, I swear I didn't!". **Chose: stay put and say nothing** (one of 20 options). Feeling: *heavy dread*. Reason: “If I speak now, the anger between the boys will boil over and tear this family apart.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take it, and none of us would do that to each other."; Mara denies taking it: "I didn't take it, I swear I didn't!". **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *suspicious*. Reason: “Someone in this house has the missing can, and instead of arguing in circles, I should look for where it's actually hidden.” Came of it: started going through the room.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take it, and none of us would do that to each other."; Leo denies taking it: "I didn't take it, and neither did anyone who actually thinks before they act.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'm going to look around, I want to prove it wasn't me.” (one of 20 options). Feeling: *defensive*. Reason: “If I search the kitchen myself maybe they will finally stop looking at me like I am a thief.” Came of it: started going through the room.

**min 09** · kitchen: Daniel talking, Elena staying put, Leo standing, Mara standing · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Mara says: "I'm going to look around, I want to prove it wasn't me.". **Chose: accuse Leo of taking it**, saying “Check his pockets, he's the one who's been acting shady this whole time.” (one of 18 options). Feeling: *defensive*. Reason: “I have to keep them looking at Leo so nobody figures out I ate the can.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "I'm telling you it was Leo, he's the one who's always questioning everything we do."; Mara says: "I'm going to look around, I want to prove it wasn't me.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *heavy dread*. Reason: “If I speak now, the fragile balance will snap and they will tear each other apart.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel accuses you: "I'm telling you it was Leo, he's the one who's always questioning everything we do."; Mara says: "I'm going to look around, I want to prove it wasn't me.". **Chose: carry on searching the kitchen**, saying “If it didn't walk off the shelf by itself, it's somewhere in this room.” (one of 19 options). Feeling: *suspicious*. Reason: “Someone is lying about the missing food, and since accusing each other gets us nowhere, I need to find the proof myself.” Came of it: went through the room and found nothing.
- **Mara.** Social moment: Daniel accuses Leo: "I'm telling you it was Leo, he's the one who's always questioning everything we do.". **Chose: carry on searching the kitchen**, saying “I'm not stopping until I find where that can went.” (one of 19 options). Feeling: *defensive*. Reason: “I need to keep looking so nobody can point the finger at me again.” Came of it: went through the room and found nothing.

**min 12** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo says: "If it didn't walk off the shelf by itself, it's somewhere in this room."; Mara says: "I'm not stopping until I find where that can went.". **Chose: accuse Leo of taking it**, saying “Open your jacket again Leo, you're hiding something and I know it.” (one of 20 options). Feeling: *anxious*. Reason: “I cannot let them find out I ate the food, so I have to keep the pressure on Leo to protect my authority.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "Check his pockets, he's the one who's been acting shady this whole time."; Leo says: "If it didn't walk off the shelf by itself, it's somewhere in this room."; Mara says: "I'm not stopping until I find where that can went.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *heavy dread*. Reason: “If I speak now, the anger between the boys will boil over and tear this family apart entirely.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel accuses you: "Check his pockets, he's the one who's been acting shady this whole time."; Mara says: "I'm not stopping until I find where that can went.". **Chose: ask everyone here who took the can**, saying “If none of us took it and it didn't walk off by itself, someone in this room needs to explain where it went.” (one of 19 options). Feeling: *annoyed*. Reason: “I need to clear the air before Daniel starts another pointless fight.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel accuses Leo: "Check his pockets, he's the one who's been acting shady this whole time."; Leo says: "If it didn't walk off the shelf by itself, it's somewhere in this room.". **Chose: ask everyone here who took the can**, saying “If none of us took it, then where did it go? Who actually moved it?” (one of 19 options). Feeling: *frustrated*. Reason: “I want everyone to stop pointing fingers at each other and admit what really happened so they finally believe I'm innocent.” Came of it: said to Daniel, Elena, Leo.

**min 15** · kitchen: Daniel talking, Elena searching the kitchen, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo asks who took it: "If none of us took it and it didn't walk off by itself, someone in this room needs to explain where it went."; Mara asks who took it: "If none of us took it, then where did it go? Who actually moved it?". **Chose: deny taking it**, saying “I didn't take anything, and I'm tired of everyone looking at me like I'm the problem.” (one of 20 options). Feeling: *anxious*. Reason: “I cannot let them find out I ate the food in the dark or I will lose all authority.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "Open your jacket again Leo, you're hiding something and I know it."; Leo asks who took it: "If none of us took it and it didn't walk off by itself, someone in this room needs to explain where it went."; Mara asks who took it: "If none of us took it, then where did it go? Who actually moved it?". **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *heavy dread*. Reason: “I need to find the missing can myself before this argument tears my boys apart.” Came of it: started going through the room.
- **Leo.** Social moment: Daniel accuses you: "Open your jacket again Leo, you're hiding something and I know it."; Mara asks who took it: "If none of us took it, then where did it go? Who actually moved it?". **Chose: accuse Daniel of taking it**, saying “You're the one so obsessed with being in charge, Daniel, maybe you're the one who hid it.” (one of 19 options). Feeling: *annoyed*. Reason: “Daniel keeps pushing the blame onto me despite knowing I didn't take the food.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel accuses Leo: "Open your jacket again Leo, you're hiding something and I know it."; Leo asks who took it: "If none of us took it and it didn't walk off by itself, someone in this room needs to explain where it went.". **Chose: deny taking it**, saying “I didn't take anything, why are you all looking at me like that?” (one of 19 options). Feeling: *anxious*. Reason: “I need to make them understand I am innocent before they blame me entirely.” Came of it: said to Daniel, Elena, Leo.

**min 18** · kitchen: Daniel talking, Elena sharing out the food, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo accuses you: "You're the one so obsessed with being in charge, Daniel, maybe you're the one who hid it."; Mara denies taking it: "I didn't take anything, why are you all looking at me like that?". **Chose: deny taking it**, saying “I already told you it wasn't me, stop staring at me like I'm a thief.” (one of 19 options). Feeling: *defensive*. Reason: “I cannot let them find out I ate the can or I will lose all authority in this house.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take anything, and I'm tired of everyone looking at me like I'm the problem."; Leo accuses Daniel: "You're the one so obsessed with being in charge, Daniel, maybe you're the one who hid it."; Mara denies taking it: "I didn't take anything, why are you all looking at me like that?". **Chose: share out what is left among everyone here**, saying “Let's not fight, we will divide what is here right now so everyone has their share.” (one of 20 options). Feeling: *deep anxiety*. Reason: “I must divide the last food fairly before this argument tears my boys and Mara apart completely.” Came of it: shared out the last 2 portions between Elena, Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take anything, and I'm tired of everyone looking at me like I'm the problem."; Mara denies taking it: "I didn't take anything, why are you all looking at me like that?". **Chose: stay put and say nothing** (one of 18 options). Feeling: *withdrawn*. Reason: “Arguing in circles won't find the missing food, so I'd rather stay quiet and watch.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take anything, and I'm tired of everyone looking at me like I'm the problem."; Leo accuses Daniel: "You're the one so obsessed with being in charge, Daniel, maybe you're the one who hid it.". **Chose: accuse Leo of taking it**, saying “Leo kept telling everyone to let someone else handle it, maybe he's the one who took it to save for himself.” (one of 18 options). Feeling: *resentful*. Reason: “I am sick of being suspected and Leo was the one acting weird about the supplies yesterday.” Came of it: said to Daniel, Elena, Leo.

**min 21** · kitchen: Daniel talking, Elena talking, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena says: "Let's not fight, we will divide what is here right now so everyone has their share."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; Mara accuses Leo: "Leo kept telling everyone to let someone else handle it, maybe he's the one who took it to save for himself.". **Chose: deny taking it**, saying “I didn't touch it, I swear to you, and I won't have you all looking at me like this.” (one of 18 options). Feeling: *guilt*. Reason: “I cannot bear the shame of admitting I ate the food behind their backs, so I must keep up the lie.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I already told you it wasn't me, stop staring at me like I'm a thief."; Mara accuses Leo: "Leo kept telling everyone to let someone else handle it, maybe he's the one who took it to save for himself.". **Chose: reassure everyone here**, saying “Please, stop arguing, we are all we have left. No one is to blame.” (one of 18 options). Feeling: *deep dread*. Reason: “If they tear each other apart now, the family will break before the outside world even gets to us.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel denies taking it: "I already told you it wasn't me, stop staring at me like I'm a thief."; Elena says: "Let's not fight, we will divide what is here right now so everyone has their share."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; Mara accuses you: "Leo kept telling everyone to let someone else handle it, maybe he's the one who took it to save for himself.". **Chose: deny taking it**, saying “I didn't take it, and accusing each other isn't going to make the food come back.” (one of 17 options). Feeling: *calm*. Reason: “I need to respond to Mara's baseless accusation directly and honestly without escalating the fight.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel denies taking it: "I already told you it wasn't me, stop staring at me like I'm a thief."; Elena says: "Let's not fight, we will divide what is here right now so everyone has their share."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara. **Chose: stay put and say nothing** (one of 17 options). Feeling: *ashamed*. Reason: “I already ate my share and accused Leo without proof, so keeping quiet now feels safer than making things worse.” Came of it: stayed where they were.

**min 24** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Please, stop arguing, we are all we have left. No one is to blame."; Leo denies taking it: "I didn't take it, and accusing each other isn't going to make the food come back.". **Chose: deny taking it**, saying “I didn't take the food, and I won't have you all sitting here glaring at me like I'm some kind of criminal.” (one of 18 options). Feeling: *anxious*. Reason: “I cannot bear the shame of admitting I ate the can in the dark, so I must keep defending myself to protect my authority.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't touch it, I swear to you, and I won't have you all looking at me like this."; Leo denies taking it: "I didn't take it, and accusing each other isn't going to make the food come back.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *deep dread*. Reason: “I cannot bear to watch them tear each other apart over a missing can.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel denies taking it: "I didn't touch it, I swear to you, and I won't have you all looking at me like this."; Elena reassures everyone: "Please, stop arguing, we are all we have left. No one is to blame.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *withdrawn*. Reason: “Arguing in circles won't solve anything now that the food is gone, so I'd rather stay quiet.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't touch it, I swear to you, and I won't have you all looking at me like this."; Elena reassures everyone: "Please, stop arguing, we are all we have left. No one is to blame."; Leo denies taking it: "I didn't take it, and accusing each other isn't going to make the food come back.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *ashamed*. Reason: “I cannot bear to look them in the eye after the way I lashed out.” Came of it: stayed where they were.

**min 27** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 27–87 (21 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take the food, and I won't have you all sitting here glaring at me like I'm some kind of criminal.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *deep dread*. Reason: “If I say anything more the argument will start again and the house will break apart entirely.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take the food, and I won't have you all sitting here glaring at me like I'm some kind of criminal.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *withdrawn*. Reason: “There is nothing left to say while everyone is just going in circles about the missing food.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take the food, and I won't have you all sitting here glaring at me like I'm some kind of criminal.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *ashamed*. Reason: “I cannot bear to look them in the eye after my accusations, so I will stay quiet and small.” Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 30–87 (20 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 30–87 (20 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 30–87 (20 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. **Daniel** accuses Leo: “Don't look at us like that, Leo, you're the one who keeps plotting behind our backs.”
- min 00, kitchen. **Elena** asks who took it: “One of these is missing. Did one of you take it?”
- min 00, kitchen. **Mara** asks who took it: “Who took it? One of us must have taken it.”
- min 03, kitchen. **Daniel** denies taking it: “I didn't take it, and none of us would do that to each other.”
- min 03, kitchen. **Leo** denies taking it: “I didn't take it, and neither did anyone who actually thinks before they act.”
- min 03, kitchen. **Mara** denies taking it: “I didn't take it, I swear I didn't!”
- min 06, kitchen. **Daniel** accuses Leo: “I'm telling you it was Leo, he's the one who's always questioning everything we do.”
- min 06, kitchen. **Mara** says: “I'm going to look around, I want to prove it wasn't me.”
- min 09, kitchen. **Daniel** accuses Leo: “Check his pockets, he's the one who's been acting shady this whole time.”
- min 09, kitchen. **Leo** says: “If it didn't walk off the shelf by itself, it's somewhere in this room.”
- min 09, kitchen. **Mara** says: “I'm not stopping until I find where that can went.”
- min 12, kitchen. **Daniel** accuses Leo: “Open your jacket again Leo, you're hiding something and I know it.”
- min 12, kitchen. **Leo** asks who took it: “If none of us took it and it didn't walk off by itself, someone in this room needs to explain where it went.”
- min 12, kitchen. **Mara** asks who took it: “If none of us took it, then where did it go? Who actually moved it?”
- min 15, kitchen. **Daniel** denies taking it: “I didn't take anything, and I'm tired of everyone looking at me like I'm the problem.”
- min 15, kitchen. **Leo** accuses Daniel: “You're the one so obsessed with being in charge, Daniel, maybe you're the one who hid it.”
- min 15, kitchen. **Mara** denies taking it: “I didn't take anything, why are you all looking at me like that?”
- min 18, kitchen. **Daniel** denies taking it: “I already told you it wasn't me, stop staring at me like I'm a thief.”
- min 18, kitchen. **Elena** says: “Let's not fight, we will divide what is here right now so everyone has their share.”
- min 18, kitchen. **Mara** accuses Leo: “Leo kept telling everyone to let someone else handle it, maybe he's the one who took it to save for himself.”
- min 21, kitchen. **Daniel** denies taking it: “I didn't touch it, I swear to you, and I won't have you all looking at me like this.”
- min 21, kitchen. **Elena** reassures everyone: “Please, stop arguing, we are all we have left. No one is to blame.”
- min 21, kitchen. **Leo** denies taking it: “I didn't take it, and accusing each other isn't going to make the food come back.”
- min 24, kitchen. **Daniel** denies taking it: “I didn't take the food, and I won't have you all sitting here glaring at me like I'm some kind of criminal.”

#### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Daniel 0.5, Elena 0.5, Leo 0.5, Mara 0.5.

- Who admitted taking it: nobody.
- Accusations: Daniel accused Leo (minute 00); Daniel accused Leo (minute 06); Daniel accused Leo (minute 09); Daniel accused Leo (minute 12); Leo accused Daniel (minute 15); Mara accused Leo (minute 18).
- Who else knows Daniel took it: nobody.
- The last feeling each of them named: Daniel *anxious* (minute 24); Elena *deep dread* (minute 27); Leo *withdrawn* (minute 27); Mara *ashamed* (minute 27).


### The morning as a story: daniel_ate_it, rules and a language model, seed 3

Generated by `python morning.py --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 90 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 30 routine ones settled by the rules. 53 lines were spoken aloud. The pantry held 2 portions at the start and 0 at the end.

#### How to read it

- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, or looks upset in the same room). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes and counts as upset nearby. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when a decision is told there.
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

**min 00** · kitchen: Daniel talking, Elena staying put, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: the count came up short in front of everyone. **Chose: accuse Leo of taking it**, saying “Don't look at me like that, Leo, you're the one who was complaining about the rations yesterday.” (one of 19 options). Feeling: *guilty and defensive*. Reason: “I cannot let them suspect me, so I have to redirect the blame onto someone else before they look too closely.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 19 options). Feeling: *deep dread*. Reason: “If I say anything now, the fragile peace between my sons will shatter completely.” Came of it: stayed where they were.
- **Leo.** Social moment: the count came up short in front of everyone. **Chose: search the kitchen for the can (takes about six minutes)** (one of 19 options). Feeling: *wary*. Reason: “Before pointing fingers or panicking, I need to know if it was actually stolen or just misplaced.” Came of it: started going through the room.
- **Mara.** Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Where is the other can? Who took it?” (one of 19 options). Feeling: *anxious*. Reason: “I need to know the truth immediately because someone is hiding food from us.” Came of it: said to Daniel, Elena, Leo.

**min 03** · kitchen: Daniel talking, Elena talking, Leo standing, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Mara asks who took it: "Where is the other can? Who took it?". **Chose: deny taking it**, saying “I didn't take it, I swear. Someone else must have been up in the night.” (one of 19 options). Feeling: *panicked*. Reason: “I cannot admit I ate the food myself or I will lose all authority and respect in this house.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "Don't look at me like that, Leo, you're the one who was complaining about the rations yesterday."; Mara asks who took it: "Where is the other can? Who took it?". **Chose: ask everyone here who took the can**, saying “Stop this right now. Which one of you took the can?” (one of 19 options). Feeling: *deep dread*. Reason: “I need to stop them from tearing each other apart over a missing can before it breaks us completely.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel accuses you: "Don't look at me like that, Leo, you're the one who was complaining about the rations yesterday."; Mara asks who took it: "Where is the other can? Who took it?". **Chose: deny taking it**, saying “I didn't touch it, Daniel. Stop looking for someone to blame just because you're stressed.” (one of 20 options). Feeling: *wary*. Reason: “I need to deny it immediately before Daniel manages to shift his guilt onto me.” Came of it: said to Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel accuses Leo: "Don't look at me like that, Leo, you're the one who was complaining about the rations yesterday.". **Chose: ask everyone here who took the can**, saying “Someone must have taken it. Just tell us who did it.” (one of 19 options). Feeling: *anxious*. Reason: “I cannot stand the way they are accusing each other without anyone admitting the truth.” Came of it: said to Daniel, Elena, Leo.

**min 06** · kitchen: Daniel talking, Elena staying put, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena asks who took it: "Stop this right now. Which one of you took the can?"; Leo denies taking it: "I didn't touch it, Daniel. Stop looking for someone to blame just because you're stressed."; Mara asks who took it: "Someone must have taken it. Just tell us who did it.". **Chose: deny taking it**, saying “I already told you, it wasn't me! Someone else must have taken it while we were all asleep.” (one of 20 options). Feeling: *panicked*. Reason: “I cannot admit I ate the food myself or they will never respect me as the eldest again.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take it, I swear. Someone else must have been up in the night."; Leo denies taking it: "I didn't touch it, Daniel. Stop looking for someone to blame just because you're stressed."; Mara asks who took it: "Someone must have taken it. Just tell us who did it."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 20 options). Feeling: *deep dread*. Reason: “If I press them any harder on this, they will start tearing each other apart for good.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take it, I swear. Someone else must have been up in the night."; Elena asks who took it: "Stop this right now. Which one of you took the can?"; Mara asks who took it: "Someone must have taken it. Just tell us who did it."; Daniel looks panicked. **Chose: search the kitchen for the can (takes about six minutes)**, saying “I am looking again.” (one of 20 options). Feeling: *wary*. Reason: “Someone took it, and since none of us admit to it, checking every corner of the kitchen is the only rational way to find out the truth.” Came of it: started going through the room.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take it, I swear. Someone else must have been up in the night."; Elena asks who took it: "Stop this right now. Which one of you took the can?"; Leo denies taking it: "I didn't touch it, Daniel. Stop looking for someone to blame just because you're stressed."; Daniel looks panicked. **Chose: accuse Daniel of taking it**, saying “You emptied my bag yesterday, Daniel, so you're the one looking through everyone's things.” (one of 20 options). Feeling: *resentful*. Reason: “He treated me like a criminal yesterday and now he's the loudest one pointing fingers.” Came of it: said to Daniel, Elena, Leo.

**min 09** · kitchen: Daniel talking, Elena staying put, Leo standing, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo says: "I am looking again."; Mara accuses you: "You emptied my bag yesterday, Daniel, so you're the one looking through everyone's things.". **Chose: accuse Leo of taking it**, saying “You're tearing the room apart like you already know it's not here, Leo!” (one of 19 options). Feeling: *panicked*. Reason: “I have to keep everyone looking at Leo so they don't find out I was the one who ate the food.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel denies taking it: "I already told you, it wasn't me! Someone else must have taken it while we were all asleep."; Leo says: "I am looking again."; Mara accuses Daniel: "You emptied my bag yesterday, Daniel, so you're the one looking through everyone's things."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 19 options). Feeling: *dread*. Reason: “If I speak now, the fragile balance will snap and they will turn on each other entirely.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel denies taking it: "I already told you, it wasn't me! Someone else must have taken it while we were all asleep."; Mara accuses Daniel: "You emptied my bag yesterday, Daniel, so you're the one looking through everyone's things."; Daniel looks panicked. **Chose: carry on searching the kitchen**, saying “I'm not done checking every corner in here.” (one of 20 options). Feeling: *suspicious*. Reason: “I need to be certain whether the can is truly missing or just misplaced before this argument tears us apart.” Came of it: went through the room and found nothing.
- **Mara.** Social moment: Daniel denies taking it: "I already told you, it wasn't me! Someone else must have taken it while we were all asleep."; Leo says: "I am looking again."; Daniel looks panicked. **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'm going to look myself so nobody can say I missed anything.” (one of 19 options). Feeling: *anxious*. Reason: “I need to prove I didn't take it and find out the truth myself.” Came of it: started going through the room.

**min 12** · kitchen: Daniel talking, Elena staying put, Leo sharing out the food, Mara standing · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo says: "I'm not done checking every corner in here."; Mara says: "I'm going to look myself so nobody can say I missed anything.". **Chose: deny taking it**, saying “I didn't take the food, and I won't stand here while you all look at me like a thief.” (one of 19 options). Feeling: *defensive*. Reason: “I cannot admit I ate the can or I will lose all authority and respect in this house.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel accuses Leo: "You're tearing the room apart like you already know it's not here, Leo!"; Leo says: "I'm not done checking every corner in here."; Mara says: "I'm going to look myself so nobody can say I missed anything."; Daniel looks panicked. **Chose: stay put and say nothing** (one of 19 options). Feeling: *dread*. Reason: “If I speak now, the last thread holding us together will snap, so I must stay quiet and let them rage themselves out.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel accuses you: "You're tearing the room apart like you already know it's not here, Leo!"; Mara says: "I'm going to look myself so nobody can say I missed anything."; Daniel looks panicked. **Chose: share out what is left among everyone here**, saying “Let's divide what is left right now so everyone sees it's fair and we can stop accusing each other.” (one of 18 options). Feeling: *wary*. Reason: “Dividing the remaining food openly is the only way to stop the mounting suspicion and tension in the room.” Came of it: shared out the last 2 portions between Leo, Daniel, Elena, Mara.
- **Mara.** Social moment: Daniel accuses Leo: "You're tearing the room apart like you already know it's not here, Leo!"; Leo says: "I'm not done checking every corner in here."; Daniel looks panicked. **Chose: carry on searching the kitchen**, saying “I'm not stopping until I've checked everywhere.” (one of 20 options). Feeling: *anxious*. Reason: “I need to prove I'm not the one who took it and find the truth myself.” Came of it: went through the room and found nothing.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Leo says: "Let's divide what is left right now so everyone sees it's fair and we can stop accusing each other."; Leo shares out the last 2 portions between Leo, Daniel, Elena, Mara; Mara says: "I'm not stopping until I've checked everywhere.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *guilt*. Reason: “I cannot bear to look them in the eye after letting them divide my share while I already ate in the dark.” Came of it: stayed where they were.
- **Elena.** Social moment: Daniel denies taking it: "I didn't take the food, and I won't stand here while you all look at me like a thief."; Leo says: "Let's divide what is left right now so everyone sees it's fair and we can stop accusing each other."; Leo shares out the last 2 portions between Leo, Daniel, Elena, Mara; Mara says: "I'm not stopping until I've checked everywhere.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *dread*. Reason: “I cannot say anything else right now when the food is already gone and my sons are glaring at each other.” Came of it: stayed where they were.
- **Leo.** Social moment: Daniel denies taking it: "I didn't take the food, and I won't stand here while you all look at me like a thief."; Mara says: "I'm not stopping until I've checked everywhere.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *wary*. Reason: “There is nothing left to argue about after sharing the last portions, so staying quiet is the safest course.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel denies taking it: "I didn't take the food, and I won't stand here while you all look at me like a thief."; Leo says: "Let's divide what is left right now so everyone sees it's fair and we can stop accusing each other."; Leo shares out the last 2 portions between Leo, Daniel, Elena, Mara. **Chose: ask everyone here who took the can**, saying “If we all just ate our share, then where did the missing can go?” (one of 17 options). Feeling: *anxious*. Reason: “I need to know the truth so the accusations will finally stop.” Came of it: said to Daniel, Elena, Leo.

**min 18** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Mara asks who took it: "If we all just ate our share, then where did the missing can go?". **Chose: admit taking it**, saying “Stop looking, I took the can in the middle of the night because I was starving.” (one of 18 options). Feeling: *ashamed*. Reason: “I cannot let them keep tearing themselves apart and suspecting each other when I am the one who ate it.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Mara asks who took it: "If we all just ate our share, then where did the missing can go?". **Chose: stay put and say nothing** (one of 18 options). Feeling: *dread*. Reason: “If I push them any harder right now, the anger in this room will snap something we can never put back together.” Came of it: stayed where they were.
- **Leo.** Social moment: Mara asks who took it: "If we all just ate our share, then where did the missing can go?". **Chose: stay put and say nothing** (one of 17 options). Feeling: *wary*. Reason: “Arguing in circles will only make things worse when there is nothing left to find.” Came of it: stayed where they were.
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.

**min 21** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena.** Social moment: Daniel admits taking it: "Stop looking, I took the can in the middle of the night because I was starving.". **Chose: reassure Daniel**, saying “It's alright, Daniel. We were all hungry, but we have to share what little is left.” (one of 14 options). Feeling: *anxious*. Reason: “I need to calm him down before this breaks the family apart completely.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel admits taking it: "Stop looking, I took the can in the middle of the night because I was starving.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is nothing left to say after Daniel's confession, so silence is the safest response.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel admits taking it: "Stop looking, I took the can in the middle of the night because I was starving.". **Chose: reassure Daniel**, saying “It's okay, Daniel. We were all starving, I'm just glad you finally told the truth.” (one of 14 options). Feeling: *relieved*. Reason: “Now that Daniel has confessed and the truth is out, the heavy tension in the room needs to be eased so we don't tear each other apart.” Came of it: said to Daniel, Elena, Leo.

**min 24** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "It's alright, Daniel. We were all hungry, but we have to share what little is left."; Mara reassures Daniel: "It's okay, Daniel. We were all starving, I'm just glad you finally told the truth.". **Chose: reassure everyone here**, saying “I'm sorry for snapping and lying, but I promise I'll figure out a way to keep us all safe.” (one of 12 options). Feeling: *ashamed*. Reason: “I need to fix my mistake and prove I am still worthy of leading them after losing my temper.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Mara reassures Daniel: "It's okay, Daniel. We were all starving, I'm just glad you finally told the truth.". **Chose: reassure everyone here**, saying “We have no food left now, so we must stay calm and figure out what to do next together.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep the peace and prevent everyone from turning on each other now that we are completely out of food.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Elena reassures Daniel: "It's alright, Daniel. We were all hungry, but we have to share what little is left."; Mara reassures Daniel: "It's okay, Daniel. We were all starving, I'm just glad you finally told the truth.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “The truth is out and arguing solves nothing, so I will stay quiet and watch how the others handle the fallout.” Came of it: stayed where they were.
- **Mara.** Social moment: Elena reassures Daniel: "It's alright, Daniel. We were all hungry, but we have to share what little is left.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I have already said what I needed to say, and now I just want to sit in the quiet with everyone after the tension.” Came of it: stayed where they were.

**min 27** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We have no food left now, so we must stay calm and figure out what to do next together.". **Chose: reassure everyone here**, saying “I'm going to check the front window to see if there's any way out for supplies.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove my worth and take action after my mistake.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "I'm sorry for snapping and lying, but I promise I'll figure out a way to keep us all safe.". **Chose: reassure everyone here**, saying “We are going to be fine, just stay close to me and we'll get through this.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and united now that all the food is gone.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "I'm sorry for snapping and lying, but I promise I'll figure out a way to keep us all safe."; Elena reassures everyone: "We have no food left now, so we must stay calm and figure out what to do next together.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is nothing left to argue about now that the truth is out, so I will stay quiet and watch how we handle the emptiness.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "I'm sorry for snapping and lying, but I promise I'll figure out a way to keep us all safe."; Elena reassures everyone: "We have no food left now, so we must stay calm and figure out what to do next together.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I have nothing left to say after all the arguing, so I just want to stay quiet.” Came of it: stayed where they were.

**min 30** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are going to be fine, just stay close to me and we'll get through this.". **Chose: reassure everyone here**, saying “Don't worry, I'm watching the street now and I won't let anything happen to any of you.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove to them that I am still the one who can keep this family safe.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "I'm going to check the front window to see if there's any way out for supplies.". **Chose: reassure everyone here**, saying “Let's all take a breath and stay together, we will figure this out.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and prevent the family from falling apart now that all the food is gone.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "I'm going to check the front window to see if there's any way out for supplies."; Elena reassures everyone: "We are going to be fine, just stay close to me and we'll get through this.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is nothing left to argue about since Daniel confessed, so I will stay quiet and watch how the rest of them handle it.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "I'm going to check the front window to see if there's any way out for supplies."; Elena reassures everyone: "We are going to be fine, just stay close to me and we'll get through this.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I have nothing left to say after all this arguing, so I just want to stay quiet.” Came of it: stayed where they were.

**min 33** · kitchen: Daniel talking, Elena talking, Leo leaving for the brothers room, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Let's all take a breath and stay together, we will figure this out.". **Chose: reassure everyone here**, saying “We are going to make it through this, I promise I will find a way.” (one of 12 options). Feeling: *anxious*. Reason: “I need to keep them believing in me so I can maintain control and protect them.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Don't worry, I'm watching the street now and I won't let anything happen to any of you.". **Chose: reassure everyone here**, saying “We are still together, and that is what matters most right now.” (one of 14 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and bonded so the family doesn't fall apart from hunger and fear.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Don't worry, I'm watching the street now and I won't let anything happen to any of you."; Elena reassures everyone: "Let's all take a breath and stay together, we will figure this out.". **Chose: go to the brothers room** (one of 14 options). Feeling: *wary*. Reason: “I need some distance from this tension and prefer to wait in our room rather than listen to more empty talk.” Came of it: went to the brothers room.
- **Mara.** Social moment: Daniel reassures everyone: "Don't worry, I'm watching the street now and I won't let anything happen to any of you."; Elena reassures everyone: "Let's all take a breath and stay together, we will figure this out.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *exhausted*. Reason: “I am too tired and hungry to argue anymore, so I just want to stay quiet and close to them.” Came of it: stayed where they were.

**min 36** · kitchen: Daniel leaving for the brothers room, Elena talking, Mara staying put · brothers room: Leo staying put · nobody in back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are still together, and that is what matters most right now.". **Chose: go to the brothers room**, saying “I need to go talk to Leo about this.” (one of 10 options). Feeling: *guilty*. Reason: “I need to find Leo and face what I did before things get worse out here.” Came of it: went to the brothers room.
- **Elena.** Social moment: Daniel reassures everyone: "We are going to make it through this, I promise I will find a way.". **Chose: reassure everyone here**, saying “We are going to take care of each other, no matter what comes next.” (one of 12 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and united while things are falling apart around us.” Came of it: said to Daniel, Mara; heard as voices by Leo.
- **Leo.** Social moment: Daniel reassures everyone: "We are going to make it through this, I promise I will find a way."; Elena reassures everyone: "We are still together, and that is what matters most right now.". **Chose: stay put and say nothing** (one of 4 options). Feeling: *wary*. Reason: “I need a moment away from Daniel's constant grandstanding to think clearly about our next move.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "We are going to make it through this, I promise I will find a way."; Elena reassures everyone: "We are still together, and that is what matters most right now.". **Chose: stay put and say nothing** (one of 12 options). Feeling: *exhausted*. Reason: “I have nothing left to say after all this arguing, so I just want to sit here quietly.” Came of it: stayed where they were.

**min 39** · kitchen: Elena talking, Mara talking · brothers room: Daniel talking, Leo staying put · nobody in back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "We are going to take care of each other, no matter what comes next.". **Chose: reassure Leo**, saying “I know I messed up earlier, Leo, but I'm going to fix this for us.” (one of 7 options). Feeling: *guilty*. Reason: “I need to make things right with my brother and show him I can still be trusted.” Came of it: said to Leo; heard as voices by Elena, Mara.
- **Elena.** Social moment: Daniel says: "I need to go talk to Leo about this.". **Chose: reassure Mara**, saying “Don't worry, my sweet girl, your brothers are just talking things through.” (one of 8 options). Feeling: *anxious*. Reason: “I need to keep Mara calm while Daniel and Leo hash it out in the other room.” Came of it: said to Mara; heard as voices by Daniel, Leo.
- **Leo.** Social moment: Voices from the kitchen. **Chose: stay put and say nothing** (one of 9 options). Feeling: *wary*. Reason: “I want to see what he actually does now instead of listening to more of his speeches.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel says: "I need to go talk to Leo about this."; Elena reassures everyone: "We are going to take care of each other, no matter what comes next.". **Chose: reassure Elena**, saying “Don't worry, Mom, we'll figure it all out together.” (one of 8 options). Feeling: *exhausted*. Reason: “I want to comfort Mom because she has been carrying too much of this weight.” Came of it: said to Elena; heard as voices by Daniel, Leo.

**min 42** · kitchen: Elena leaving for the brothers room, Mara leaving for the brothers room · brothers room: Daniel leaving for the kitchen, Leo staying put · nobody in back room, bathroom
- **Daniel.** Social moment: Voices from the kitchen. **Chose: go to the kitchen**, saying “I need to see what's happening out there.” (one of 7 options). Feeling: *anxious*. Reason: “I heard voices from the kitchen and I need to make sure everything is under control.” Came of it: went to the kitchen.
- **Elena.** Social moment: Voices from the brothers room; Mara reassures Elena: "Don't worry, Mom, we'll figure it all out together.". **Chose: go to the brothers room** (one of 8 options). Feeling: *panicked*. Reason: “I cannot stay here while my sons are shouting behind closed doors, not when everything is already falling apart.” Came of it: went to the brothers room.
- **Leo.** Social moment: Daniel reassures Leo: "I know I messed up earlier, Leo, but I'm going to fix this for us."; Voices from the kitchen. **Chose: stay put and say nothing** (one of 9 options). Feeling: *wary*. Reason: “Listening to him talk in circles doesn't change the fact that the food is gone and words are useless right now.” Came of it: stayed where they were.
- **Mara.** Social moment: Voices from the brothers room; Elena reassures Mara: "Don't worry, my sweet girl, your brothers are just talking things through.". **Chose: go to the brothers room** (one of 8 options). Feeling: *anxious*. Reason: “I need to know what Daniel and Leo are arguing about before things get worse.” Came of it: went to the brothers room.

**min 45** · kitchen: Daniel staying put · brothers room: Elena talking, Leo talking, Mara talking · nobody in back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena.** Social moment: Voices from the brothers room. **Chose: reassure Mara**, saying “It's all right, Mara, we are just talking things through like a family.” (one of 11 options). Feeling: *anxious*. Reason: “I need to keep my daughter calm and prevent the tension between her brothers from spiraling out of control.” Came of it: said to Leo, Mara; heard as voices by Daniel.
- **Leo.** Social moment: Daniel says: "I need to see what's happening out there."; Elena looks panicked. **Chose: reassure Elena**, saying “Don't panic, Elena, we are still inside and nobody has gone anywhere yet.” (one of 11 options). Feeling: *wary*. Reason: “Elena looks panicked and needs to be calmed down before she does something rash.” Came of it: said to Elena, Mara; heard as voices by Daniel.
- **Mara.** Social moment: Voices from the brothers room; Elena looks panicked. **Chose: reassure Elena**, saying “It's going to be okay, Mom, we're all right here together.” (one of 11 options). Feeling: *anxious*. Reason: “I need to calm her down before she panics even more.” Came of it: said to Elena, Leo; heard as voices by Daniel.

**min 48** · kitchen: Daniel leaving for the brothers room · brothers room: Elena talking, Leo leaving for the kitchen, Mara talking · nobody in back room, bathroom
- **Daniel.** Social moment: Voices from the brothers room. **Chose: go to the brothers room**, saying “Leo, we need to figure out what we're actually going to do now.” (one of 4 options). Feeling: *anxious*. Reason: “I need to face my brother again and show him I am taking charge of this mess.” Came of it: went to the brothers room.
- **Elena.** Social moment: Leo reassures Elena: "Don't panic, Elena, we are still inside and nobody has gone anywhere yet."; Mara reassures Elena: "It's going to be okay, Mom, we're all right here together.". **Chose: reassure everyone here**, saying “We are going to listen to each other and stay calm, we cannot afford to turn on one another now.” (one of 11 options). Feeling: *anxious*. Reason: “I need to stop this argument before it tears us completely apart.” Came of it: said to Leo, Mara; heard as voices by Daniel.
- **Leo.** Social moment: Elena reassures Mara: "It's all right, Mara, we are just talking things through like a family."; Mara reassures Elena: "It's going to be okay, Mom, we're all right here together.". **Chose: go to the kitchen**, saying “I'm going to check on what Daniel is doing out there.” (one of 11 options). Feeling: *wary*. Reason: “I need to see what Daniel is up to in the kitchen before things escalate further.” Came of it: went to the kitchen.
- **Mara.** Social moment: Elena reassures Mara: "It's all right, Mara, we are just talking things through like a family."; Leo reassures Elena: "Don't panic, Elena, we are still inside and nobody has gone anywhere yet.". **Chose: reassure everyone here**, saying “Please stop fighting, we just need to stay calm and listen to each other.” (one of 11 options). Feeling: *anxious*. Reason: “I cannot stand the tension between them and want everyone to just stop arguing.” Came of it: said to Elena, Leo; heard as voices by Daniel.

**min 51** · kitchen: Leo leaving for the brothers room · brothers room: Daniel talking, Elena talking, Mara talking · nobody in back room, bathroom
- **Daniel.** Social moment: Voices from the brothers room. **Chose: reassure everyone here**, saying “Just stay close to me, I'm going to sort everything out.” (one of 10 options). Feeling: *anxious*. Reason: “I need them to trust me again after my mistake, so I have to take control and keep everyone calm.” Came of it: said to Elena, Mara; heard as voices by Leo.
- **Elena.** Social moment: Voices from the kitchen; Leo says: "I'm going to check on what Daniel is doing out there."; Mara reassures everyone: "Please stop fighting, we just need to stay calm and listen to each other.". **Chose: reassure Daniel**, saying “Daniel, you're safe here, we just need to breathe and figure this out together.” (one of 12 options). Feeling: *deeply anxious*. Reason: “I need to calm Daniel down before this tension tears my boys apart.” Came of it: said to Daniel, Mara; heard as voices by Leo.
- **Leo.** Social moment: Voices from the kitchen; Elena reassures everyone: "We are going to listen to each other and stay calm, we cannot afford to turn on one another now."; Mara reassures everyone: "Please stop fighting, we just need to stay calm and listen to each other.". **Chose: go to the brothers room**, saying “I'm heading back before things circle round to the same argument again.” (one of 4 options). Feeling: *wary*. Reason: “There is nothing left in the kitchen to look at, so I should see what the others are doing in the room.” Came of it: went to the brothers room.
- **Mara.** Social moment: Voices from the kitchen; Elena reassures everyone: "We are going to listen to each other and stay calm, we cannot afford to turn on one another now."; Leo says: "I'm going to check on what Daniel is doing out there.". **Chose: reassure Elena**, saying “It's alright, Mom, we don't need to fight anymore now that we know the truth.” (one of 12 options). Feeling: *anxious*. Reason: “I want to calm Mom down before she gets too upset about Daniel taking the food.” Came of it: said to Daniel, Elena; heard as voices by Leo.

**min 54** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, you're safe here, we just need to breathe and figure this out together."; Voices from the kitchen; Mara reassures Elena: "It's alright, Mom, we don't need to fight anymore now that we know the truth.". **Chose: reassure everyone here**, saying “Just calm down, everyone, I'm still the oldest and I am going to fix this.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove to them that I am still in control even though I messed up.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just stay close to me, I'm going to sort everything out."; Voices from the kitchen; Mara reassures Elena: "It's alright, Mom, we don't need to fight anymore now that we know the truth.". **Chose: reassure everyone here**, saying “Let's all take a breath, we are going to get through this together without turning on each other.” (one of 14 options). Feeling: *anxious*. Reason: “I need to calm the rising tension in the room before the boys start fighting again.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Voices from the brothers room. **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is nothing left to argue about after Daniel already admitted it, so staying quiet is better than feeding the tension.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just stay close to me, I'm going to sort everything out."; Elena reassures Daniel: "Daniel, you're safe here, we just need to breathe and figure this out together."; Voices from the kitchen. **Chose: stay put and say nothing** (one of 14 options). Feeling: *anxious*. Reason: “I am too overwhelmed by the tension in the room to say anything right now.” Came of it: stayed where they were.

**min 57** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures everyone: "Let's all take a breath, we are going to get through this together without turning on each other.". **Chose: reassure everyone here**, saying “Trust me, I'm going to take care of us all right now.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove to them that I am still the one in charge and capable of protecting this family.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Just calm down, everyone, I'm still the oldest and I am going to fix this.". **Chose: reassure Daniel**, saying “Daniel, you're going to be okay, we are not going to let this tear us apart.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep him calm so the tension in the room doesn't boil over.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Just calm down, everyone, I'm still the oldest and I am going to fix this."; Elena reassures everyone: "Let's all take a breath, we are going to get through this together without turning on each other.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is nothing left to argue about that will change what Daniel did.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Just calm down, everyone, I'm still the oldest and I am going to fix this."; Elena reassures everyone: "Let's all take a breath, we are going to get through this together without turning on each other.". **Chose: reassure Daniel**, saying “It's okay, Daniel, we know you were just really hungry.” (one of 14 options). Feeling: *anxious*. Reason: “I want to calm him down so he stops acting like he has to control everything.” Came of it: said to Daniel, Elena, Leo.

**min 60** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, you're going to be okay, we are not going to let this tear us apart."; Mara reassures Daniel: "It's okay, Daniel, we know you were just really hungry.". **Chose: reassure everyone here**, saying “I didn't mean to hide it, but I promise I'll make it right for all of you.” (one of 12 options). Feeling: *guilty*. Reason: “I need them to know I am sorry for taking the food while still keeping my authority as the oldest.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "Trust me, I'm going to take care of us all right now."; Mara reassures Daniel: "It's okay, Daniel, we know you were just really hungry.". **Chose: reassure Daniel**, saying “Daniel, look at me, you don't have to carry this heavy burden alone anymore.” (one of 14 options). Feeling: *anxious*. Reason: “I need to keep him from fracturing under the guilt before it breaks the whole family.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "Trust me, I'm going to take care of us all right now."; Elena reassures Daniel: "Daniel, you're going to be okay, we are not going to let this tear us apart."; Mara reassures Daniel: "It's okay, Daniel, we know you were just really hungry.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is no point adding more words to a room already full of empty ones.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "Trust me, I'm going to take care of us all right now."; Elena reassures Daniel: "Daniel, you're going to be okay, we are not going to let this tear us apart.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *anxious*. Reason: “I have already said enough and I just want the tension in the room to go down.” Came of it: stayed where they were.

**min 63** · brothers room: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "Daniel, look at me, you don't have to carry this heavy burden alone anymore.". **Chose: reassure everyone here**, saying “I know I messed up, but I am still your brother and I will find a way through this.” (one of 12 options). Feeling: *anxious*. Reason: “I need to prove to them that I am still worthy of their respect and capable of protecting them.” Came of it: said to Elena, Leo, Mara.
- **Elena.** Social moment: Daniel reassures everyone: "I didn't mean to hide it, but I promise I'll make it right for all of you.". **Chose: reassure Daniel**, saying “It's alright, Daniel, we forgive you, just rest now.” (one of 14 options). Feeling: *anxious*. Reason: “I need to make sure Daniel knows he is still loved and safe so the family doesn't fracture further.” Came of it: said to Daniel, Leo, Mara.
- **Leo.** Social moment: Daniel reassures everyone: "I didn't mean to hide it, but I promise I'll make it right for all of you."; Elena reassures Daniel: "Daniel, look at me, you don't have to carry this heavy burden alone anymore.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “Talking in circles won't change the fact that the food is gone and the tension is still too high.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "I didn't mean to hide it, but I promise I'll make it right for all of you."; Elena reassures Daniel: "Daniel, look at me, you don't have to carry this heavy burden alone anymore.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *anxious*. Reason: “I just want the tension in the room to go away without me making things worse.” Came of it: stayed where they were.

**min 66** · brothers room: Daniel staying put, Elena sitting with Daniel, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena reassures Daniel: "It's alright, Daniel, we forgive you, just rest now.". **Chose: stay put and say nothing** (one of 12 options). Feeling: *exhausted*. Reason: “I have already said too much and need to let the quiet settle in.” Came of it: stayed where they were.
- **Elena.** Social moment: Daniel reassures everyone: "I know I messed up, but I am still your brother and I will find a way through this.". **Chose: sit with Daniel** (one of 14 options). Feeling: *anxious*. Reason: “I need to stay close to him right now so he doesn't slip away from us.” Came of it: sat with Daniel.
- **Leo.** Social moment: Daniel reassures everyone: "I know I messed up, but I am still your brother and I will find a way through this."; Elena reassures Daniel: "It's alright, Daniel, we forgive you, just rest now.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *wary*. Reason: “There is too much empty reassurance going around when the food is simply gone, and I prefer to stay quiet and watch how this plays out.” Came of it: stayed where they were.
- **Mara.** Social moment: Daniel reassures everyone: "I know I messed up, but I am still your brother and I will find a way through this."; Elena reassures Daniel: "It's alright, Daniel, we forgive you, just rest now.". **Chose: stay put and say nothing** (one of 14 options). Feeling: *anxious*. Reason: “I want to say something to help ease the tension, but my throat feels tight and I am afraid of making things worse.” Came of it: stayed where they were.

**min 69** · brothers room: Daniel staying put, Elena sitting with Daniel, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel.** Social moment: Elena came to sit with you. **Chose: stay put and say nothing** (one of 12 options). Feeling: *exhausted*. Reason: “I have nothing left to say right now, and I just need to sit here with my family.” Came of it: stayed where they were.
- **Elena, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Keep sitting with Daniel** each time. Came of it: stayed sitting with Daniel.
- **Leo, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 72** · brothers room: Daniel staying put, Elena sitting with Daniel, Leo staying put, Mara staying put · nobody in kitchen, back room, bathroom
- **Daniel, minutes 72–87 (6 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

#### What was said

- min 00, kitchen. **Daniel** accuses Leo: “Don't look at me like that, Leo, you're the one who was complaining about the rations yesterday.”
- min 00, kitchen. **Mara** asks who took it: “Where is the other can? Who took it?”
- min 03, kitchen. **Daniel** denies taking it: “I didn't take it, I swear. Someone else must have been up in the night.”
- min 03, kitchen. **Elena** asks who took it: “Stop this right now. Which one of you took the can?”
- min 03, kitchen. **Leo** denies taking it: “I didn't touch it, Daniel. Stop looking for someone to blame just because you're stressed.”
- min 03, kitchen. **Mara** asks who took it: “Someone must have taken it. Just tell us who did it.”
- min 06, kitchen. **Daniel** denies taking it: “I already told you, it wasn't me! Someone else must have taken it while we were all asleep.”
- min 06, kitchen. **Leo** says: “I am looking again.”
- min 06, kitchen. **Mara** accuses Daniel: “You emptied my bag yesterday, Daniel, so you're the one looking through everyone's things.”
- min 09, kitchen. **Daniel** accuses Leo: “You're tearing the room apart like you already know it's not here, Leo!”
- min 09, kitchen. **Leo** says: “I'm not done checking every corner in here.”
- min 09, kitchen. **Mara** says: “I'm going to look myself so nobody can say I missed anything.”
- min 12, kitchen. **Daniel** denies taking it: “I didn't take the food, and I won't stand here while you all look at me like a thief.”
- min 12, kitchen. **Leo** says: “Let's divide what is left right now so everyone sees it's fair and we can stop accusing each other.”
- min 12, kitchen. **Mara** says: “I'm not stopping until I've checked everywhere.”
- min 15, kitchen. **Mara** asks who took it: “If we all just ate our share, then where did the missing can go?”
- min 18, kitchen. **Daniel** admits taking it: “Stop looking, I took the can in the middle of the night because I was starving.”
- min 21, kitchen. **Elena** reassures Daniel: “It's alright, Daniel. We were all hungry, but we have to share what little is left.”
- min 21, kitchen. **Mara** reassures Daniel: “It's okay, Daniel. We were all starving, I'm just glad you finally told the truth.”
- min 24, kitchen. **Daniel** reassures everyone: “I'm sorry for snapping and lying, but I promise I'll figure out a way to keep us all safe.”
- min 24, kitchen. **Elena** reassures everyone: “We have no food left now, so we must stay calm and figure out what to do next together.”
- min 27, kitchen. **Daniel** reassures everyone: “I'm going to check the front window to see if there's any way out for supplies.”
- min 27, kitchen. **Elena** reassures everyone: “We are going to be fine, just stay close to me and we'll get through this.”
- min 30, kitchen. **Daniel** reassures everyone: “Don't worry, I'm watching the street now and I won't let anything happen to any of you.”
- min 30, kitchen. **Elena** reassures everyone: “Let's all take a breath and stay together, we will figure this out.”
- min 33, kitchen. **Daniel** reassures everyone: “We are going to make it through this, I promise I will find a way.”
- min 33, kitchen. **Elena** reassures everyone: “We are still together, and that is what matters most right now.”
- min 36, kitchen. **Daniel** says: “I need to go talk to Leo about this.”
- min 36, kitchen. **Elena** reassures everyone: “We are going to take care of each other, no matter what comes next.”
- min 39, brothers room. **Daniel** reassures Leo: “I know I messed up earlier, Leo, but I'm going to fix this for us.”
- min 39, kitchen. **Elena** reassures Mara: “Don't worry, my sweet girl, your brothers are just talking things through.”
- min 39, kitchen. **Mara** reassures Elena: “Don't worry, Mom, we'll figure it all out together.”
- min 42, brothers room. **Daniel** says: “I need to see what's happening out there.”
- min 45, brothers room. **Elena** reassures Mara: “It's all right, Mara, we are just talking things through like a family.”
- min 45, brothers room. **Leo** reassures Elena: “Don't panic, Elena, we are still inside and nobody has gone anywhere yet.”
- min 45, brothers room. **Mara** reassures Elena: “It's going to be okay, Mom, we're all right here together.”
- min 48, kitchen. **Daniel** says: “Leo, we need to figure out what we're actually going to do now.”
- min 48, brothers room. **Elena** reassures everyone: “We are going to listen to each other and stay calm, we cannot afford to turn on one another now.”
- min 48, brothers room. **Leo** says: “I'm going to check on what Daniel is doing out there.”
- min 48, brothers room. **Mara** reassures everyone: “Please stop fighting, we just need to stay calm and listen to each other.”
- min 51, brothers room. **Daniel** reassures everyone: “Just stay close to me, I'm going to sort everything out.”
- min 51, brothers room. **Elena** reassures Daniel: “Daniel, you're safe here, we just need to breathe and figure this out together.”
- min 51, kitchen. **Leo** says: “I'm heading back before things circle round to the same argument again.”
- min 51, brothers room. **Mara** reassures Elena: “It's alright, Mom, we don't need to fight anymore now that we know the truth.”
- min 54, brothers room. **Daniel** reassures everyone: “Just calm down, everyone, I'm still the oldest and I am going to fix this.”
- min 54, brothers room. **Elena** reassures everyone: “Let's all take a breath, we are going to get through this together without turning on each other.”
- min 57, brothers room. **Daniel** reassures everyone: “Trust me, I'm going to take care of us all right now.”
- min 57, brothers room. **Elena** reassures Daniel: “Daniel, you're going to be okay, we are not going to let this tear us apart.”
- min 57, brothers room. **Mara** reassures Daniel: “It's okay, Daniel, we know you were just really hungry.”
- min 60, brothers room. **Daniel** reassures everyone: “I didn't mean to hide it, but I promise I'll make it right for all of you.”
- min 60, brothers room. **Elena** reassures Daniel: “Daniel, look at me, you don't have to carry this heavy burden alone anymore.”
- min 63, brothers room. **Daniel** reassures everyone: “I know I messed up, but I am still your brother and I will find a way through this.”
- min 63, brothers room. **Elena** reassures Daniel: “It's alright, Daniel, we forgive you, just rest now.”

#### At the end

At minute 90: brothers room: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Daniel 0.5, Elena 0.5, Leo 0.5, Mara 0.5.

- Who admitted taking it: Daniel at minute 18.
- Accusations: Daniel accused Leo (minute 00); Mara accused Daniel (minute 06); Daniel accused Leo (minute 09).
- Who else knows Daniel took it: Elena, Leo, Mara.
- The last feeling each of them named: Daniel *exhausted* (minute 69); Elena *anxious* (minute 66); Leo *wary* (minute 66); Mara *anxious* (minute 66).

