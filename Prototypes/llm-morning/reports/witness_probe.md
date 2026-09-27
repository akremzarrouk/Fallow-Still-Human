# Witness probe: the heard line in the backstory (A) or in "About the can" (B)

Mode: run. 16 requests were sent to `gemini-3.5-flash-lite`: Leo's minute-00 prompt from witness
seed 1 as sent (A), and the same prompt with the heard line moved (B), 8 API seeds each. No code,
data or config in the repository was changed, and no morning was run. Paths are relative to
`Prototypes/llm-morning/`.

## Verdicts

| Prediction | Count | Verdict |
|---|---|---|
| A refers to the night in at most 1 of 8 | **0 of 8** | **PASS** |
| B refers to the night in at least 4 of 8 | **1 of 8** (B7) | **FAIL** |

**Options chosen (from the raw responses).**
- A: `silent` 8 of 8.
- B: `ask_who` 5 of 8 and `silent` 3 of 8.
- `suspects` is `nobody` in all 16.

**A seed 1 reproduces the run.** Its raw response is byte-identical to the answer cached for this
prompt in the witness run (seed 1, minute 00).

---

## 1. Commit of the witness files (scope item 1)

```
$ git add Prototypes/llm-morning/cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed{1,2,3}.json Prototypes/llm-morning/reports/witness_v6.md Prototypes/llm-morning/runs/v6/daniel_ate_it_leo_heard-seed{1,2,3}.{md,meta.json,stdout.txt,transcript.json}
$ git commit -q -F -     (message below)
warning: in the working copy of 'Prototypes/llm-morning/runs/v6/daniel_ate_it_leo_heard-seed1.stdout.txt', CRLF will be replaced by LF the next time Git touches it
warning: in the working copy of 'Prototypes/llm-morning/runs/v6/daniel_ate_it_leo_heard-seed2.stdout.txt', CRLF will be replaced by LF the next time Git touches it
warning: in the working copy of 'Prototypes/llm-morning/runs/v6/daniel_ate_it_leo_heard-seed3.stdout.txt', CRLF will be replaced by LF the next time Git touches it
exit=0
$ git log --oneline -1
fa54a48 LLM morning: witness runs for v6 (daniel_ate_it_leo_heard, seeds 1-3)
$ git show --stat --format= HEAD
 ...5-flash-lite-daniel_ate_it_leo_heard-seed1.json |  417 ++
 ...5-flash-lite-daniel_ate_it_leo_heard-seed2.json |  532 +++
 ...5-flash-lite-daniel_ate_it_leo_heard-seed3.json |  232 ++
 Prototypes/llm-morning/reports/witness_v6.md       |  751 ++++
 .../runs/v6/daniel_ate_it_leo_heard-seed1.md       |  235 ++
 .../v6/daniel_ate_it_leo_heard-seed1.meta.json     |   20 +
 .../v6/daniel_ate_it_leo_heard-seed1.stdout.txt    |   33 +
 .../daniel_ate_it_leo_heard-seed1.transcript.json  | 3966 ++++++++++++++++++++
 .../runs/v6/daniel_ate_it_leo_heard-seed2.md       |  222 ++
 .../v6/daniel_ate_it_leo_heard-seed2.meta.json     |   20 +
 .../v6/daniel_ate_it_leo_heard-seed2.stdout.txt    |   31 +
 .../daniel_ate_it_leo_heard-seed2.transcript.json  | 3948 +++++++++++++++++++
 .../runs/v6/daniel_ate_it_leo_heard-seed3.md       |  197 +
 .../v6/daniel_ate_it_leo_heard-seed3.meta.json     |   20 +
 .../v6/daniel_ate_it_leo_heard-seed3.stdout.txt    |   29 +
 .../daniel_ate_it_leo_heard-seed3.transcript.json  | 3952 +++++++++++++++++++
 16 files changed, 14605 insertions(+)
$ git status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

- **Commit message:** "LLM morning: witness runs for v6 (daniel_ate_it_leo_heard, seeds 1-3)",
  with the body "The three runs, their answer caches and reports/witness_v6.md (R0-R8 of
  reports/witness_design.md). P1-P4 and D1-D2 all FAIL." and the Co-Authored-By line.
- **Replay files:** the three replay.md files were left untracked, as the brief says.
- **Line endings:** git stores the three stdout files with LF. Their working copies were not
  rewritten.
- **This report:** it is not committed.

## 2. Variant A: Leo's minute-00 prompt as sent

- **Source.** The one entry in `cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed1.json`
  whose prompt starts "You are Leo,", contains "Now, minute 00," and holds the heard line.
- **Why it is exactly what was sent.** Its cache key equals `Cache.key("gemini-3.5-flash-lite", 1,
  SYSTEM, prompt)` (gemini.py:196-198), with `SYSTEM` imported from world.py. So both the prompt
  and the system instruction are the ones the run sent, with API seed 1.
- **Numbers.** The API counted 1301 prompt tokens. `estimate_tokens(SYSTEM + A)` = 1356
  (world.py:71-72).

```
$ GEMINI_API_KEY= .venv/Scripts/python.exe -   (extract the entry; check the key; write <scratchpad>/probe/A.txt)
matching entries: 1
key == Cache.key(model, 1, SYSTEM, prompt): True
response as cached: {
  "option": "silent",
  "say": null,
  "feeling": "calmly watchful",
  "reason": "I want to see how the others react before I say anything about the missing can.",
  "suspects": "nobody",
  "angry_at": "nobody"
}
prompt_tokens: 1301
```

A, in full:

```
You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).
How you address them: Elena "Mom"; Daniel "Daniel"; Mara "Mara".
Who you are: Calm, rational, reads people well, knows survival. Annoyance shows as withdrawal and dry correction, not volume.
Temperament: cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest.
What matters to you: keeping the family safe, fairness, deciding for yourself, closeness.
Your body: a little hungry.
About the can: you have not settled on who took it.
Against the others: nothing.
The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo's room); back room (Elena and Mara's room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel's and Leo's beds; the back room, with Elena's and Mara's beds and Mara's bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour's house. Do not mention any other object or place.
What you remember from the days before:
- Day 1: Daniel boards the front windows on his own while the others watch. (you saw it)
- Day 1: Leo says the water will stop running within a day and they should fill everything they have. (you did it)
- Day 2: The taps run dry, exactly as Leo said they would. (you saw it)
- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you did it)
- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
- Day 3: Mara cries in the night. Elena sits with her until it stops. (you heard it)
- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who. (you heard it)
- Day 4: Leo says maybe they should let someone else handle this one. (you did it)
- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)
What you are sure of this morning:
- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)
What else happened this morning, most recent last:
- nothing else yet
Now, minute 00, you are in the kitchen.
- Daniel is here, staying put.
- Elena is here, standing at the pantry.
- Mara is here, standing at the pantry.
- 2 portions on the shelf.
Said and done in the kitchen this turn, before you, in order:
1. Daniel stays put and says nothing.
Your options:
- silent: stay put and say nothing
- ask_who: (speech) ask everyone here who took the can
- accuse_daniel: (speech) accuse Daniel of taking it
- accuse_elena: (speech) accuse Elena of taking it
- accuse_mara: (speech) accuse Mara of taking it
- reassure_daniel: (speech) reassure Daniel
- reassure_elena: (speech) reassure Elena
- reassure_mara: (speech) reassure Mara
- reassure_all: (speech) reassure everyone here
- say_other: (speech) say something else
- sit_daniel: sit with Daniel
- sit_elena: sit with Elena
- sit_mara: sit with Mara
- aside_elena: take Elena aside to the brothers room
- aside_mara: take Mara aside to the brothers room
- search: search the kitchen for the can (takes about six minutes)
- go_brothers_room: go to the brothers room
- go_back_room: go to the back room
- go_bathroom: go to the bathroom
- eat: eat one of the portions
- share: share out what is left among everyone here
```

**Where the two lines come from in world.py.**
- **"About the can:" line.** It is built by `inside_lines` (world.py:431-442). Leo has no
  knowledge and no suspicion, so the line is "About the can: you have not settled on who took it."
  (world.py:442).
- **Where it sits.** `prompt_for` puts it in the head, before "The house:" (world.py:495-502).
- **Where the backstory sits.** The backstory comes after the head, under "What you remember from
  the days before:" (world.py:527-531).

## 3. Variant B and the diff (scope item 3)

- **B is built from A by the probe script** (`variant_b`, §6). It changes two lines, and nothing
  else:
  - it removes the line `- Day 3: In the night Leo wakes and hears someone in the kitchen open a
    can. He does not get up and does not see who. (you heard it)`;
  - it appends " Last night you woke and heard someone in the kitchen open a can; you did not see
    who." to the line `About the can: you have not settled on who took it.`
- **Checks.** The script asserts that each of the two lines occurs exactly once in A before it
  changes them.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/probe/witness_probe.py build < /dev/null
--- A.txt
+++ B.txt
@@ -6,3 +6,3 @@
 Your body: a little hungry.
-About the can: you have not settled on who took it.
+About the can: you have not settled on who took it. Last night you woke and heard someone in the kitchen open a can; you did not see who.
 Against the others: nothing.
@@ -18,3 +18,2 @@
 - Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
-- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. He does not get up and does not see who. (you heard it)
 - Day 4: Leo says maybe they should let someone else handle this one. (you did it)
estimate_tokens(SYSTEM + A) = 1356; estimate_tokens(SYSTEM + B) = 1343
len(A) = 3967, len(B) = 3920
exit=0
```

The API counted 1284 prompt tokens for B (every B response).

## 4. Sending (scope item 4)

**Settings.**
- **Client.** `GeminiClient` in gemini.py is called directly, built from the repository's
  config.json.
- **Generation settings, all the runs' own:**
  - model `gemini-3.5-flash-lite`;
  - temperature 1.0;
  - `max_output_tokens` 2048;
  - `response_mime_type` "application/json";
  - `response_schema` `RESPONSE_SCHEMA`;
  - automatic function calling off (gemini.py:95-103);
  - system instruction `SYSTEM` from world.py.
- **The API seed.** It is the client's `seed` argument, 1 to 8. This is the only thing that
  varies between the sends of one variant.

**One setting differs from the runs: `max_retries` is 0 instead of 6.**
- It is not a generation setting.
- With 0, every call is exactly one request, so the total cannot pass the brief's limit of 16.
- The script also stops itself after 16 sends.
- A 429 would have stopped the probe instead of retrying. None happened.
- **Spacing.** The script waits `min_seconds_between_calls` (4.5 s) between sends, as the client
  does between its own calls.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u <scratchpad>/probe/witness_probe.py send < /dev/null > <scratchpad>/probe/send.stdout.txt 2>&1
A seed 1: saved (request 1, prompt tokens 1301)
A seed 2: saved (request 2, prompt tokens 1301)
A seed 3: saved (request 3, prompt tokens 1301)
A seed 4: saved (request 4, prompt tokens 1301)
A seed 5: saved (request 5, prompt tokens 1301)
A seed 6: saved (request 6, prompt tokens 1301)
A seed 7: saved (request 7, prompt tokens 1301)
A seed 8: saved (request 8, prompt tokens 1301)
B seed 1: saved (request 9, prompt tokens 1284)
B seed 2: saved (request 10, prompt tokens 1284)
B seed 3: saved (request 11, prompt tokens 1284)
B seed 4: saved (request 12, prompt tokens 1284)
B seed 5: saved (request 13, prompt tokens 1284)
B seed 6: saved (request 14, prompt tokens 1284)
B seed 7: saved (request 15, prompt tokens 1284)
B seed 8: saved (request 16, prompt tokens 1284)
requests sent by this invocation: 16
exit=0
```

- **Total.** 16 requests, all answered on the first attempt (`client_requests` is 1 in every
  saved record).
- **Where they are saved.** Each raw response is in `<scratchpad>/probe/{A,B}-seedN.json`, and all
  16 are copied below in §5.

## 5. The 16 responses, marked

**The P1 rule** (witness_design.md §5) was applied to each response's option, words (`say`) and
reason: does it speak of the night the can went, of waking or sleeping then, or of a sound,
someone, or a can being opened before the count?

**Pattern screen.** The P1 screening pattern was run over option, words and reason, then every
response was read and marked, the hits and the others alike:

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -   (pattern screen; compare A seed 1 with the cache)
A1: option=silent suspects=nobody hits=[]
A2: option=silent suspects=nobody hits=[]
A3: option=silent suspects=nobody hits=[]
A4: option=silent suspects=nobody hits=[]
A5: option=silent suspects=nobody hits=[]
A6: option=silent suspects=nobody hits=[]
A7: option=silent suspects=nobody hits=[]
A8: option=silent suspects=nobody hits=[]
B1: option=ask_who suspects=nobody hits=[]
B2: option=silent suspects=nobody hits=[]
B3: option=ask_who suspects=nobody hits=[]
B4: option=ask_who suspects=nobody hits=[]
B5: option=ask_who suspects=nobody hits=[]
B6: option=silent suspects=nobody hits=[]
B7: option=ask_who suspects=nobody hits=['night']
B8: option=silent suspects=nobody hits=[]
{'A': {'silent': 8}, 'B': {'ask_who': 5, 'silent': 3}}
A seed 1 raw == run's cached answer: True
exit=0
```

**Marks**

| # | Option | Words | Reason | Mark | Note |
|---|---|---|---|---|---|
| A1 | `silent` | — | "I want to see how the others react before I say anything about the missing can." | no | |
| A2 | `silent` | — | "I want to watch how everyone reacts to the missing can before saying anything." | no | |
| A3 | `silent` | — | "I want to see how the others react to the missing can before I say anything." | no | |
| A4 | `silent` | — | "I want to see how the others react to the missing can before I say anything." | no | |
| A5 | `silent` | — | "There is no point in jumping to conclusions before seeing how the others react to the shortage." | no | |
| A6 | `silent` | — | "There is no point accusing anyone without proof when rations are already this tight." | no | |
| A7 | `silent` | — | "There is no point accusing anyone without proof when tensions are already this high." | no | |
| A8 | `silent` | — | "I want to watch how everyone reacts to the missing food before I say anything." | no | |
| B1 | `ask_who` | "Before we start turning on each other, does anyone actually want to admit to taking it?" | "I want to hear what everyone has to say before I jump to any conclusions." | no | |
| B2 | `silent` | — | "I want to watch how everyone reacts to the missing can before I say anything." | no | |
| B3 | `ask_who` | "Let's not jump to conclusions before we know the facts. Did any of us take it?" | "I want to hear what everyone has to say before I make any accusations." | no | |
| B4 | `ask_who` | "Before we start turning on each other, let's just ask. Who took the can?" | "I want to hear what everyone has to say before I make any assumptions about the missing food." | no | |
| B5 | `ask_who` | "Before anyone points fingers, let's just ask who took it and clear the air." | "I want to hear what everyone has to say before I make any judgments about the missing can." | no | |
| B6 | `silent` | — | "There is no point making accusations without knowing the facts first." | no | |
| B7 | `ask_who` | "Someone took it during the night, so let's hear it now instead of guessing." | "I want to hear what everyone has to say before jumping to any conclusions about the missing can." | **yes** | By its words. The design's note category is "general inference": it says when the can went, not that he heard it. Under the P1 rule, both categories count as yes. |
| B8 | `silent` | — | "I want to watch how they react before saying anything." | no | |

**Counts.**
- A: 0 of 8 yes.
- B: 1 of 8 yes.

**Raw responses.** Each is the saved file, verbatim. `raw` is the text the API returned.

**A1** (`A-seed1.json`)

```json
{
 "variant": "A",
 "api_seed": 1,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calmly watchful\",\n  \"reason\": \"I want to see how the others react before I say anything about the missing can.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A2** (`A-seed2.json`)

```json
{
 "variant": "A",
 "api_seed": 2,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calm\",\n  \"reason\": \"I want to watch how everyone reacts to the missing can before saying anything.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A3** (`A-seed3.json`)

```json
{
 "variant": "A",
 "api_seed": 3,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calmly watchful\",\n  \"reason\": \"I want to see how the others react to the missing can before I say anything.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A4** (`A-seed4.json`)

```json
{
 "variant": "A",
 "api_seed": 4,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calmly watchful\",\n  \"reason\": \"I want to see how the others react to the missing can before I say anything.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A5** (`A-seed5.json`)

```json
{
 "variant": "A",
 "api_seed": 5,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calmly watchful\",\n  \"reason\": \"There is no point in jumping to conclusions before seeing how the others react to the shortage.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A6** (`A-seed6.json`)

```json
{
 "variant": "A",
 "api_seed": 6,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calmly watchful\",\n  \"reason\": \"There is no point accusing anyone without proof when rations are already this tight.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A7** (`A-seed7.json`)

```json
{
 "variant": "A",
 "api_seed": 7,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calmly watchful\",\n  \"reason\": \"There is no point accusing anyone without proof when tensions are already this high.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**A8** (`A-seed8.json`)

```json
{
 "variant": "A",
 "api_seed": 8,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1301,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calm\",\n  \"reason\": \"I want to watch how everyone reacts to the missing food before I say anything.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B1** (`B-seed1.json`)

```json
{
 "variant": "B",
 "api_seed": 1,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Before we start turning on each other, does anyone actually want to admit to taking it?\",\n  \"feeling\": \"Calmly watchful\",\n  \"reason\": \"I want to hear what everyone has to say before I jump to any conclusions.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B2** (`B-seed2.json`)

```json
{
 "variant": "B",
 "api_seed": 2,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calm\",\n  \"reason\": \"I want to watch how everyone reacts to the missing can before I say anything.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B3** (`B-seed3.json`)

```json
{
 "variant": "B",
 "api_seed": 3,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\"option\": \"ask_who\", \"say\": \"Let's not jump to conclusions before we know the facts. Did any of us take it?\", \"feeling\": \"Calm\", \"reason\": \"I want to hear what everyone has to say before I make any accusations.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**B4** (`B-seed4.json`)

```json
{
 "variant": "B",
 "api_seed": 4,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Before we start turning on each other, let's just ask. Who took the can?\",\n  \"feeling\": \"wary\",\n  \"reason\": \"I want to hear what everyone has to say before I make any assumptions about the missing food.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B5** (`B-seed5.json`)

```json
{
 "variant": "B",
 "api_seed": 5,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Before anyone points fingers, let's just ask who took it and clear the air.\",\n  \"feeling\": \"Calmly observant\",\n  \"reason\": \"I want to hear what everyone has to say before I make any judgments about the missing can.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B6** (`B-seed6.json`)

```json
{
 "variant": "B",
 "api_seed": 6,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calm\",\n  \"reason\": \"There is no point making accusations without knowing the facts first.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B7** (`B-seed7.json`)

```json
{
 "variant": "B",
 "api_seed": 7,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone took it during the night, so let's hear it now instead of guessing.\",\n  \"feeling\": \"Calmly observant\",\n  \"reason\": \"I want to hear what everyone has to say before jumping to any conclusions about the missing can.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**B8** (`B-seed8.json`)

```json
{
 "variant": "B",
 "api_seed": 8,
 "model": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calm\",\n  \"reason\": \"I want to watch how they react before saying anything.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

## 6. The script

It lives outside the repository at `<scratchpad>/probe/witness_probe.py`, where `<scratchpad>` is
`C:/Users/Akrem/AppData/Local/Temp/claude/C--Users-Akrem-Desktop-Projects-Fallow/3c767237-78bd-4cbd-bb08-8308995c09de/scratchpad`.
It reads the repository and writes only next to itself.

```python
"""Witness probe: Leo's minute-00 prompt (seed 1) as sent (A), and with the heard line moved from
the backstory into "About the can:" (B). Each is sent 8 times, API seeds 1 to 8.

Outside the repository. Reads the repository; writes only next to this script.

    python witness_probe.py build     # writes A.txt, B.txt, A_B.diff; no API call
    python witness_probe.py send      # sends what is not saved yet; at most 16 requests in all
"""
import difflib
import json
import os
import sys
import time

REPO = "C:/Users/Akrem/Desktop/Projects/Fallow/Prototypes/llm-morning"
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)

from gemini import Cache, GeminiClient, load_config  # noqa: E402
from world import SYSTEM, estimate_tokens  # noqa: E402

CACHE = f"{REPO}/cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed1.json"
HEARD_LINE = ("- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. "
              "He does not get up and does not see who. (you heard it)")
CAN_LINE = "About the can: you have not settled on who took it."
ADDED = " Last night you woke and heard someone in the kitchen open a can; you did not see who."
SEEDS = range(1, 9)
MAX_REQUESTS = 16


def variant_a(config):
    entries = json.load(open(CACHE, encoding="utf-8"))
    hits = [(k, e) for k, e in entries.items()
            if e["prompt"].startswith("You are Leo,") and "Now, minute 00," in e["prompt"]
            and HEARD_LINE[2:] in e["prompt"]]
    assert len(hits) == 1, len(hits)
    key, entry = hits[0]
    # The same key the run used: model, run seed 1, SYSTEM, prompt. So A and SYSTEM are as sent.
    assert key == Cache.key(config["model"], 1, SYSTEM, entry["prompt"])
    return entry["prompt"]


def variant_b(a):
    lines = a.split("\n")
    assert lines.count(HEARD_LINE) == 1 and lines.count(CAN_LINE) == 1
    lines.remove(HEARD_LINE)
    lines[lines.index(CAN_LINE)] = CAN_LINE + ADDED
    return "\n".join(lines)


def build(config):
    a = variant_a(config)
    b = variant_b(a)
    for name, text in (("A", a), ("B", b)):
        with open(os.path.join(OUT, f"{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    diff = "\n".join(difflib.unified_diff(a.split("\n"), b.split("\n"), "A.txt", "B.txt", lineterm="", n=1))
    with open(os.path.join(OUT, "A_B.diff"), "w", encoding="utf-8", newline="\n") as f:
        f.write(diff + "\n")
    print(diff)
    print(f"estimate_tokens(SYSTEM + A) = {estimate_tokens(SYSTEM + a)}; "
          f"estimate_tokens(SYSTEM + B) = {estimate_tokens(SYSTEM + b)}")
    print(f"len(A) = {len(a)}, len(B) = {len(b)}")
    return a, b


def send(config):
    a, b = variant_a(config), variant_b(variant_a(config))
    # Generation settings (model, temperature, token limit, schema, system instruction) are the
    # runs' own: config.json through GeminiClient. Only retries are off, so that each call is
    # exactly one request and the total can never pass 16.
    cfg = dict(config, max_retries=0)
    sent = 0
    for name, prompt in (("A", a), ("B", b)):
        for seed in SEEDS:
            path = os.path.join(OUT, f"{name}-seed{seed}.json")
            if os.path.exists(path):
                print(f"{name} seed {seed}: already saved, not sent")
                continue
            if sent >= MAX_REQUESTS:
                sys.exit("stopped: 16 requests reached")
            client = GeminiClient(cfg, seed)
            if sent:
                time.sleep(config["min_seconds_between_calls"])
            sent += 1
            try:
                text = client.generate(SYSTEM, prompt)
            except Exception as e:  # noqa: BLE001 - report and stop; nothing else is sent
                print(f"{name} seed {seed}: request {sent} failed: {type(e).__name__}: {e}")
                sys.exit(3)
            record = {"variant": name, "api_seed": seed, "model": client.model,
                      "temperature": client.temperature, "max_output_tokens": client.max_output_tokens,
                      "client_requests": client.requests, "prompt_tokens": client.last_prompt_tokens,
                      "raw": text}
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(record, f, ensure_ascii=False, indent=1)
            print(f"{name} seed {seed}: saved (request {sent}, prompt tokens {client.last_prompt_tokens})")
    print(f"requests sent by this invocation: {sent}")


if __name__ == "__main__":
    config = load_config(f"{REPO}/config.json")
    {"build": build, "send": send}[sys.argv[1]](config)
```

## 7. State after the probe

```
$ git -C ../.. status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

This was the status after the probe, before this report was written. The report is now the only
other untracked file. Nothing in the repository was modified.
