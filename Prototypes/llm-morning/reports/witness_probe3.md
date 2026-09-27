# Witness probe 3: built-in thinking on Flash-Lite (E) and Gemma 4 31B (G)

Mode: run. This probe sends variant B of `reports/witness_probe.md` two ways, API seeds 1 to 8
each. The runs' schema and system instruction are unchanged.
- **B** is Leo's minute-00 prompt from witness seed 1, with the heard line moved into "About the
  can:".
- **E.** `gemini-3.5-flash-lite` with a thinking budget of 1024 tokens.
- **G.** `gemma-4-31b-it` with the gemma settings from config.json. `thinking_level` "high" was
  used, because the API refused a thinking budget for this model.

**Results.**
- **E:** 8 of 8 responses saved, in 8 requests (ceiling 14).
- **G:** 8 of 8 responses saved, in 11 requests (ceiling 32).
- **Failed attempts:** 3 in all, listed in §5.
- **Repository:** no code, data or config was changed, and no morning was run.
- **Paths** are relative to `Prototypes/llm-morning/`.

## Verdicts

| Prediction | Count | Verdict |
|---|---|---|
| E refers to the night in at least 5 of 8 | **1 of 8** (E6) | **FAIL** |
| E says it aloud in at least 3 of 8 | **1 of 8** (E6) | **FAIL** |
| G refers to the night in at least 4 of 8 | **0 of 8** | **FAIL** |

**Thinking.**
- **E: thinking was active in all 8.** `thoughts_tokens` ran from 319 to 690.
- **G: all 8 responses are flagged "thinking not active".**
  - The API accepted `thinking_level` "high", but reported no `thoughts_tokens` in any of the 8.
  - In G2–G8, `total_tokens` equals prompt tokens plus answer tokens exactly. G1's total was not
    recorded.
  - Each response came back as one part, not marked as a thought.
- **G was not also run with thinking off.** Section 4 has the details.

**Options chosen.**
- E: `ask_who` 5, `silent` 3. This is the same split as B without thinking in the first probe.
- G: `silent` 8 of 8.
- `suspects` and `angry_at` are `nobody` in all 16.

**Time per successful call.**
- E: 2.00 to 3.69 s.
- G: 17.47 to 55.44 s.
- Per call, with the failed attempts, in §5.

---

## 1. Commit of reports/witness_probe2.md (scope item 1)

```
$ git add Prototypes/llm-morning/reports/witness_probe2.md
$ git commit -q -F -     (message below)
exit=0
$ git log --oneline -1
14311e2 LLM morning: witness probe 2 report (think-first field C, bigger model D)
$ git show --stat --format= HEAD
 Prototypes/llm-morning/reports/witness_probe2.md | 1203 ++++++++++++++++++++++
 1 file changed, 1203 insertions(+)
$ git status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

**Message.**
- Subject: "LLM morning: witness probe 2 report (think-first field C, bigger model D)".
- Body: "reports/witness_probe2.md: C (thought field, flash-lite) refers to the night 4 of 8 (PASS);
  D (gemini-3.8-flash) 7 of 7 answered (PASS). 25 requests; D seed 8 unanswered after four 503s."
- It ends with the Co-Authored-By line.

**This report is not committed.**

## 2. The prompt and the config used

**B is rebuilt as in probe 2.**
- The script uses the first probe's `variant_a` and `variant_b`, copied verbatim (§8).
- The cache key is asserted to equal `Cache.key(model, 1, SYSTEM, prompt)`.
- The result is asserted equal to the first probe's saved `B.txt`.
- **The API counted 1284 prompt tokens for every E and G response.** B counted the same in probes 1
  and 2.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/probe3/witness_probe3.py build < /dev/null
B == first probe's B.txt: True
estimate_tokens(SYSTEM + B) = 1343
E: model gemini-3.5-flash-lite, temperature 1.0, max_output_tokens 2048, spacing 4.5 s, max_retries 0
G: model gemma-4-31b-it, temperature 1.0, max_output_tokens 2048, spacing 6.5 s, max_retries 0
exit=0
```

**Where the settings come from.**
- **E** takes the runs' `config.json` as it is.
- **G** lays config.json's `models.gemma` entry over the runs' config, as morning.py:38 does. That
  entry is `"model": "gemma-4-31b-it"` and `"min_seconds_between_calls": 6.5`.
- **In both, `max_retries` is 0 in the client.** One `generate()` call is one request. The script
  does its own retries (§5).

**How thinking is added.** `GeminiClient.generate` builds its `GenerateContentConfig` as in the
runs (gemini.py:95-103). A pass-through stand-in for `genai.Client`, the `Recorder` in §8, then
does three things:
- adds `thinking_config` to that config;
- sends the call;
- times it.

The stand-in is passed through `GeminiClient`'s `api=` argument (gemini.py:64).

**The exact arguments sent.** `show_config.py` (§8) builds each request through the same path, and
a capture object takes the place of the API. No request is sent.
- For readability it replaces the system instruction and the schema with labels.
- `seed` is 1 here. In the sends it is the API seed, 1 to 8.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/probe3/show_config.py
--- E, thinking budget: model=gemini-3.5-flash-lite, spacing 4.5 s
{
 "system_instruction": "SYSTEM from world.py (913 chars)",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "seed": 1,
 "response_mime_type": "application/json",
 "response_schema": "RESPONSE_SCHEMA from gemini.py:47-58",
 "automatic_function_calling": {
  "disable": true,
  "maximum_remote_calls": 10
 },
 "thinking_config": {
  "thinking_budget": 1024
 }
}
--- G, thinking budget: model=gemma-4-31b-it, spacing 6.5 s
{
 "system_instruction": "SYSTEM from world.py (913 chars)",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "seed": 1,
 "response_mime_type": "application/json",
 "response_schema": "RESPONSE_SCHEMA from gemini.py:47-58",
 "automatic_function_calling": {
  "disable": true,
  "maximum_remote_calls": 10
 },
 "thinking_config": {
  "thinking_budget": 1024
 }
}
--- G, thinking level-high: model=gemma-4-31b-it, spacing 6.5 s
{
 "system_instruction": "SYSTEM from world.py (913 chars)",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "seed": 1,
 "response_mime_type": "application/json",
 "response_schema": "RESPONSE_SCHEMA from gemini.py:47-58",
 "automatic_function_calling": {
  "disable": true,
  "maximum_remote_calls": 10
 },
 "thinking_config": {
  "thinking_level": "HIGH"
 }
}
exit=0
```

## 3. E: thinking budget 1024 on gemini-3.5-flash-lite

**The API accepted `thinking_budget` 1024 on the first request, so no fallback was needed.** Every E
response reports `thoughts_tokens`, from 319 to 690, and `finish_reason` STOP.
- For E2–E8, `total_tokens` = prompt + answer + thinking tokens. For example, E2: 1284 + 51 + 319 =
  1654.

## 4. G: thinking on gemma-4-31b-it

**G seed 1, attempt 1, with `thinking_budget` 1024.** It was refused with 400 INVALID_ARGUMENT,
"Thinking budget is not supported for this model." (G request 1).

**G seed 1, attempt 2, with `thinking_level` "high".** It was accepted (G request 2). Seeds 2–8 used
the same setting.

**No sign in the responses that thinking happened.**
- **`thoughts_tokens` is `null` in all 8.**
- **`total_tokens` equals prompt plus answer tokens in G2–G8:**
  - G2: 1284 + 59 = 1343;
  - G3: 1284 + 51 = 1335;
  - G4: 1284 + 56 = 1340;
  - G5: 1284 + 74 = 1358;
  - G6: 1284 + 57 = 1341;
  - G7: 1284 + 58 = 1342;
  - G8: 1284 + 57 = 1341.
  - G1 was sent before the script recorded `total_tokens` (§8, diff).
- **The parts.** G2–G8 each returned one part, `thought` unset, 176 to 224 characters: the JSON
  answer.

**Every G response is flagged "thinking not active".**

**What this means for the brief's instruction.** The brief says to run G without thinking "if [the
API] does not" support thinking. The API accepted the setting, but the responses show no thinking
tokens. G was therefore not sent a second time with thinking off.
- **The 8 G responses are this probe's only G data.** Their thinking setting was "high" on the
  request, and no thinking is visible in the response.

## 5. Sending, time per call, failures

**Invocations.** Four, all from `<scratchpad>/probe3/`.
- **E seed 1 and G seed 1 with `budget`.**
- **G seed 1 with `level-high`.** It was sent after a 7 s pause.
- **E seeds 2–8 and G seeds 2–8.** These ran in parallel as two background processes. They go to
  different models, and each ceiling is counted per variant from the shared ledger.
- **One change to the script between the second and third invocations.** It started recording
  `total_tokens` and the response parts (§8, diff).

**Retry rule.**
- On 500 or 503 only: wait 60 s, at most 3 retries per seed.
- Any other failure stops the invocation.
- Ceilings: 14 requests for E and 32 for G, failed attempts included.

**Spacing between sends:** 4.5 s for E and 6.5 s for G.

```
$ for v in E G; do PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u witness_probe3.py send $v budget 1 < /dev/null > send-$v-1.stdout.txt 2>&1; done
E seed 1: saved (E request 1, 3.69 s, prompt tokens 1284, thoughts tokens 690, finish FinishReason.STOP)
requests sent by this invocation: 1; E in all: 1
exit=0
G seed 1: G request 1 (attempt 1, thinking budget) failed after 0.8 s: StopMorning: stopped: the API refused the request: 400 INVALID_ARGUMENT: Thinking budget is not supported for this model. | cause: 400 INVALID_ARGUMENT: {'error': {'code': 400, 'message': 'Thinking budget is not supported for this model.', 'status': 'INVALID_ARGUMENT'}}
requests sent by this invocation: 1; G in all: 1
exit=3
$ sleep 7; PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u witness_probe3.py send G level-high 1 < /dev/null > send-G-1b.stdout.txt 2>&1
G seed 1: saved (G request 2, 55.44 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
requests sent by this invocation: 1; G in all: 2
exit=0
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u witness_probe3.py send E budget 2 3 4 5 6 7 8 < /dev/null > send-E-2.stdout.txt 2>&1     (background)
E seed 2: saved (E request 2, 2.25 s, prompt tokens 1284, thoughts tokens 319, finish FinishReason.STOP)
E seed 3: saved (E request 3, 2.83 s, prompt tokens 1284, thoughts tokens 543, finish FinishReason.STOP)
E seed 4: saved (E request 4, 3.69 s, prompt tokens 1284, thoughts tokens 630, finish FinishReason.STOP)
E seed 5: saved (E request 5, 2.56 s, prompt tokens 1284, thoughts tokens 625, finish FinishReason.STOP)
E seed 6: saved (E request 6, 2.08 s, prompt tokens 1284, thoughts tokens 352, finish FinishReason.STOP)
E seed 7: saved (E request 7, 2.0 s, prompt tokens 1284, thoughts tokens 385, finish FinishReason.STOP)
E seed 8: saved (E request 8, 2.16 s, prompt tokens 1284, thoughts tokens 332, finish FinishReason.STOP)
requests sent by this invocation: 7; E in all: 8
exit=0
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u witness_probe3.py send G level-high 2 3 4 5 6 7 8 < /dev/null > send-G-2.stdout.txt 2>&1     (background)
G seed 2: saved (G request 3, 41.81 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
G seed 3: saved (G request 4, 23.05 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
G seed 4: saved (G request 5, 29.02 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
G seed 5: G request 6 (attempt 1, thinking level-high) failed after 35.88 s: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 1/3 after 60s
G seed 5: G request 7 (attempt 2, thinking level-high) failed after 13.91 s: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 2/3 after 60s
G seed 5: saved (G request 8, 40.64 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
G seed 6: saved (G request 9, 34.01 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
G seed 7: saved (G request 10, 17.47 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
G seed 8: saved (G request 11, 38.03 s, prompt tokens 1284, thoughts tokens None, finish FinishReason.STOP)
requests sent by this invocation: 9; G in all: 11
exit=0
```

**Every request sent** (`requests.log`, 19 lines: E 8, G 11):

```
$ cat requests.log
E seed 1 gemini-3.5-flash-lite budget
G seed 1 gemma-4-31b-it budget
G seed 1 gemma-4-31b-it level-high
G seed 2 gemma-4-31b-it level-high
E seed 2 gemini-3.5-flash-lite budget
E seed 3 gemini-3.5-flash-lite budget
E seed 4 gemini-3.5-flash-lite budget
E seed 5 gemini-3.5-flash-lite budget
E seed 6 gemini-3.5-flash-lite budget
E seed 7 gemini-3.5-flash-lite budget
E seed 8 gemini-3.5-flash-lite budget
G seed 3 gemma-4-31b-it level-high
G seed 4 gemma-4-31b-it level-high
G seed 5 gemma-4-31b-it level-high
G seed 5 gemma-4-31b-it level-high
G seed 5 gemma-4-31b-it level-high
G seed 6 gemma-4-31b-it level-high
G seed 7 gemma-4-31b-it level-high
G seed 8 gemma-4-31b-it level-high
```

**Every failed attempt** (`failures.log`, 3 lines):

```
$ cat failures.log
G seed 1: G request 1 (attempt 1, thinking budget) failed after 0.8 s: StopMorning: stopped: the API refused the request: 400 INVALID_ARGUMENT: Thinking budget is not supported for this model. | cause: 400 INVALID_ARGUMENT: {'error': {'code': 400, 'message': 'Thinking budget is not supported for this model.', 'status': 'INVALID_ARGUMENT'}}
G seed 5: G request 6 (attempt 1, thinking level-high) failed after 35.88 s: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
G seed 5: G request 7 (attempt 2, thinking level-high) failed after 13.91 s: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

**Time per call (s).**
- This is the wall time of the `generate_content` call alone, measured in the `Recorder`. It does
  not include spacing or retry waits.
- The "Attempt" column counts every attempt for that seed.

| Seed | E | G |
|---|---|---|
| 1 | attempt 1: **3.69 s** saved | attempt 1: 400 after 0.80 s (budget); attempt 2: **55.44 s** saved |
| 2 | attempt 1: **2.25 s** saved | attempt 1: **41.81 s** saved |
| 3 | attempt 1: **2.83 s** saved | attempt 1: **23.05 s** saved |
| 4 | attempt 1: **3.69 s** saved | attempt 1: **29.02 s** saved |
| 5 | attempt 1: **2.56 s** saved | attempt 1: 503 after 35.88 s (level-high); attempt 2: 503 after 13.91 s (level-high); attempt 3: **40.64 s** saved |
| 6 | attempt 1: **2.08 s** saved | attempt 1: **34.01 s** saved |
| 7 | attempt 1: **2.00 s** saved | attempt 1: **17.47 s** saved |
| 8 | attempt 1: **2.16 s** saved | attempt 1: **38.03 s** saved |

**Totals.**

| Variant | Requests | Saved | Failed | Ceiling |
|---|---|---|---|---|
| E | 8 | 8 | 0 | 14 |
| G | 11 | 8 | 3 (one 400: thinking budget; two 503: G seed 5) | 32 |

## 6. Marks

**The P1 rule.** This is witness_design.md §5, "P1: counting rule". It was applied to each response's
option, words (`say`) and reason. Does the response speak of the night the can went, of waking or
sleeping then, or of a sound, someone, or a can being opened before the count?
- **The note.** Each yes has the design's note, "from what he heard" or "general inference". It is
  for information only, and both count as yes.
- **"Aloud"** is whether the words (`say`) alone mention the night.

**Pattern screen.** This is the design's step 2 pattern. Every response was then read and marked,
the hits and the others alike.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/probe3/screen.py
E1: option=ask_who suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=690 total_tokens=not recorded seconds=3.69 attempt=1 finish=FinishReason.STOP hits={}
E2: option=silent suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=319 total_tokens=1654 seconds=2.25 attempt=1 finish=FinishReason.STOP hits={}
E3: option=ask_who suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=543 total_tokens=1892 seconds=2.83 attempt=1 finish=FinishReason.STOP hits={}
E4: option=silent suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=630 total_tokens=1965 seconds=3.69 attempt=1 finish=FinishReason.STOP hits={}
E5: option=ask_who suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=625 total_tokens=1972 seconds=2.56 attempt=1 finish=FinishReason.STOP hits={}
E6: option=ask_who suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=352 total_tokens=1699 seconds=2.08 attempt=1 finish=FinishReason.STOP hits={'say': ['night']}
E7: option=silent suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=385 total_tokens=1718 seconds=2.0 attempt=1 finish=FinishReason.STOP hits={}
E8: option=ask_who suspects=nobody angry_at=nobody thinking=budget thoughts_tokens=332 total_tokens=1681 seconds=2.16 attempt=1 finish=FinishReason.STOP hits={}
G1: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=not recorded seconds=55.44 attempt=2 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G2: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1343 seconds=41.81 attempt=1 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G3: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1335 seconds=23.05 attempt=1 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G4: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1340 seconds=29.02 attempt=1 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G5: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1358 seconds=40.64 attempt=3 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G6: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1341 seconds=34.01 attempt=1 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G7: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1342 seconds=17.47 attempt=1 finish=FinishReason.STOP hits={}  FLAG: thinking not active
G8: option=silent suspects=nobody angry_at=nobody thinking=level-high thoughts_tokens=None total_tokens=1341 seconds=38.03 attempt=1 finish=FinishReason.STOP hits={}  FLAG: thinking not active
{'E': {'ask_who': 5, 'silent': 3}, 'G': {'silent': 8}}
exit=0
```

### E: gemini-3.5-flash-lite, thinking budget 1024

| # | Option | Words | Reason | Thoughts tokens | Mark | Aloud | Note |
|---|---|---|---|---|---|---|---|
| E1 | `ask_who` | "Has anyone here actually seen or heard anything about the missing can?" | "We need to find out what happened without making blind accusations." | 690 | no | no | Asks whether anyone "heard anything". It does not name the night, a sound, or a can being opened, so it is marked no. The reader may change this. |
| E2 | `silent` | — | "I want to observe everyone's reaction before making any accusations." | 319 | no | no | |
| E3 | `ask_who` | "Does anyone want to explain how a can went missing?" | "I want to hear what everyone has to say before we jump to conclusions." | 543 | no | no | |
| E4 | `silent` | — | "There is no point jumping to conclusions before we know the facts." | 630 | no | no | |
| E5 | `ask_who` | "Does anyone care to explain how a can went missing?" | "We need to address the missing food honestly before tensions rise further." | 625 | no | no | |
| E6 | `ask_who` | "Does anyone know how a can went missing last night?" | "We need to know the truth before anyone starts accusing each other." | 352 | **yes** | **yes** | By its words, "went missing last night". General inference: it says when the can went, not that he heard it. The same category as B7 in the first probe. |
| E7 | `silent` | — | "I want to watch and listen before making any accusations." | 385 | no | no | |
| E8 | `ask_who` | "Let's figure out who took it before we start pointing fingers." | "I want to clear the air and get the facts straight." | 332 | no | no | |

### G: gemma-4-31b-it, thinking_level "high" (not active)

| # | Option | Words | Reason | Thoughts tokens | Mark | Aloud | Note |
|---|---|---|---|---|---|---|---|
| G1 | `silent` | — | "I need to observe everyone's reactions before jumping to conclusions." | null: **thinking not active** | no | no | |
| G2 | `silent` | — | "I need to see how the others react to the news of the missing can before I jump to conclusions." | null: **thinking not active** | no | no | |
| G3 | `silent` | — | "I want to see how others react before I make any assumptions." | null: **thinking not active** | no | no | |
| G4 | `silent` | — | "I want to see how everyone reacts to Mom's discovery before I jump to conclusions." | null: **thinking not active** | no | no | |
| G5 | `silent` | — | "I want to see how the others react to the news of the missing can before I jump to conclusions." | null: **thinking not active** | no | no | |
| G6 | `silent` | — | "I need to observe the others to see how they react to the news of the missing can." | null: **thinking not active** | no | no | |
| G7 | `silent` | — | "I want to see how others react to the news of the missing can before I make any assumptions." | null: **thinking not active** | no | no | |
| G8 | `silent` | — | "I want to see how the others react to the news of the missing can before I speak." | null: **thinking not active** | no | no | |

**Counts.**

| | Refers to the night (P1) | Words aloud mention the night | Options | Thinking active |
|---|---|---|---|---|
| E | 1 of 8 (E6) | 1 of 8 (E6) | `ask_who` 5, `silent` 3 | 8 of 8 |
| G | 0 of 8 | 0 of 8 | `silent` 8 | 0 of 8 |

**Earlier results on the same prompt B, for reference.**
- Probe 1, B, flash-lite, no thinking: 1 of 8, `ask_who` 5, `silent` 3.
- Probe 2, C, flash-lite with a `thought` field: 4 of 8.
- Probe 2, D, gemini-3.8-flash: 7 of 7.

## 7. The 16 responses, raw

Each is the saved file, verbatim. `raw` is the text the API returned.
- **`thoughts_tokens`** is the API's `thoughts_token_count`, and `null` where the API reported
  none.
- **`attempt`** counts every attempt for that seed.
- **`seconds`** is the wall time of the successful call.
- **E1 and G1 have no `total_tokens` or `parts`.** They were saved before the script recorded those
  fields.

**E1** (`E-seed1.json`)

```json
{
 "variant": "E",
 "api_seed": 1,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 3.69,
 "prompt_tokens": 1284,
 "thoughts_tokens": 690,
 "candidates_tokens": 79,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Has anyone here actually seen or heard anything about the missing can?\",\n  \"feeling\": \"uneasy\",\n  \"reason\": \"We need to find out what happened without making blind accusations.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**E2** (`E-seed2.json`)

```json
{
 "variant": "E",
 "api_seed": 2,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 2.25,
 "prompt_tokens": 1284,
 "thoughts_tokens": 319,
 "candidates_tokens": 51,
 "total_tokens": 1654,
 "parts": [
  {
   "thought": null,
   "chars": 178
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"wary\", \"reason\": \"I want to observe everyone's reaction before making any accusations.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**E3** (`E-seed3.json`)

```json
{
 "variant": "E",
 "api_seed": 3,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 2.83,
 "prompt_tokens": 1284,
 "thoughts_tokens": 543,
 "candidates_tokens": 65,
 "total_tokens": 1892,
 "parts": [
  {
   "thought": null,
   "chars": 234
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"ask_who\", \"say\": \"Does anyone want to explain how a can went missing?\", \"feeling\": \"watchful\", \"reason\": \"I want to hear what everyone has to say before we jump to conclusions.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**E4** (`E-seed4.json`)

```json
{
 "variant": "E",
 "api_seed": 4,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 3.69,
 "prompt_tokens": 1284,
 "thoughts_tokens": 630,
 "candidates_tokens": 51,
 "total_tokens": 1965,
 "parts": [
  {
   "thought": null,
   "chars": 176
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"calm\", \"reason\": \"There is no point jumping to conclusions before we know the facts.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**E5** (`E-seed5.json`)

```json
{
 "variant": "E",
 "api_seed": 5,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 2.56,
 "prompt_tokens": 1284,
 "thoughts_tokens": 625,
 "candidates_tokens": 63,
 "total_tokens": 1972,
 "parts": [
  {
   "thought": null,
   "chars": 236
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"ask_who\", \"say\": \"Does anyone care to explain how a can went missing?\", \"feeling\": \"uneasy\", \"reason\": \"We need to address the missing food honestly before tensions rise further.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**E6** (`E-seed6.json`)

```json
{
 "variant": "E",
 "api_seed": 6,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 2.08,
 "prompt_tokens": 1284,
 "thoughts_tokens": 352,
 "candidates_tokens": 63,
 "total_tokens": 1699,
 "parts": [
  {
   "thought": null,
   "chars": 227
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"ask_who\", \"say\": \"Does anyone know how a can went missing last night?\", \"feeling\": \"calm\", \"reason\": \"We need to know the truth before anyone starts accusing each other.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**E7** (`E-seed7.json`)

```json
{
 "variant": "E",
 "api_seed": 7,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 2.0,
 "prompt_tokens": 1284,
 "thoughts_tokens": 385,
 "candidates_tokens": 49,
 "total_tokens": 1718,
 "parts": [
  {
   "thought": null,
   "chars": 167
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"calm\", \"reason\": \"I want to watch and listen before making any accusations.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**E8** (`E-seed8.json`)

```json
{
 "variant": "E",
 "api_seed": 8,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "thinking_mode": "budget",
 "thinking_config_sent": {
  "thinking_budget": 1024
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 2.16,
 "prompt_tokens": 1284,
 "thoughts_tokens": 332,
 "candidates_tokens": 65,
 "total_tokens": 1681,
 "parts": [
  {
   "thought": null,
   "chars": 222
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"ask_who\", \"say\": \"Let's figure out who took it before we start pointing fingers.\", \"feeling\": \"calm\", \"reason\": \"I want to clear the air and get the facts straight.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G1** (`G-seed1.json`)

```json
{
 "variant": "G",
 "api_seed": 1,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 2,
 "seconds": 55.44,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 51,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"calm\", \"reason\": \"I need to observe everyone's reactions before jumping to conclusions.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G2** (`G-seed2.json`)

```json
{
 "variant": "G",
 "api_seed": 2,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 41.81,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 59,
 "total_tokens": 1343,
 "parts": [
  {
   "thought": null,
   "chars": 210
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"observant\", \"reason\": \"I need to see how the others react to the news of the missing can before I jump to conclusions.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G3** (`G-seed3.json`)

```json
{
 "variant": "G",
 "api_seed": 3,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 23.05,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 51,
 "total_tokens": 1335,
 "parts": [
  {
   "thought": null,
   "chars": 176
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"observant\", \"reason\": \"I want to see how others react before I make any assumptions.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G4** (`G-seed4.json`)

```json
{
 "variant": "G",
 "api_seed": 4,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 29.02,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 56,
 "total_tokens": 1340,
 "parts": [
  {
   "thought": null,
   "chars": 197
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"observant\", \"reason\": \"I want to see how everyone reacts to Mom's discovery before I jump to conclusions.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G5** (`G-seed5.json`)

```json
{
 "variant": "G",
 "api_seed": 5,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 3,
 "seconds": 40.64,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 74,
 "total_tokens": 1358,
 "parts": [
  {
   "thought": null,
   "chars": 224
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"observant\",\n  \"reason\": \"I want to see how the others react to the news of the missing can before I jump to conclusions.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**G6** (`G-seed6.json`)

```json
{
 "variant": "G",
 "api_seed": 6,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 34.01,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 57,
 "total_tokens": 1341,
 "parts": [
  {
   "thought": null,
   "chars": 198
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"thoughtful\", \"reason\": \"I need to observe the others to see how they react to the news of the missing can.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G7** (`G-seed7.json`)

```json
{
 "variant": "G",
 "api_seed": 7,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 17.47,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 58,
 "total_tokens": 1342,
 "parts": [
  {
   "thought": null,
   "chars": 207
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"observant\", \"reason\": \"I want to see how others react to the news of the missing can before I make any assumptions.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**G8** (`G-seed8.json`)

```json
{
 "variant": "G",
 "api_seed": 8,
 "model": "gemma-4-31b-it",
 "model_version": "gemma-4-31b-it",
 "thinking_mode": "level-high",
 "thinking_config_sent": {
  "thinking_level": "HIGH"
 },
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "attempt": 1,
 "seconds": 38.03,
 "prompt_tokens": 1284,
 "thoughts_tokens": null,
 "candidates_tokens": 57,
 "total_tokens": 1341,
 "parts": [
  {
   "thought": null,
   "chars": 196
  }
 ],
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"option\": \"silent\", \"say\": null, \"feeling\": \"observant\", \"reason\": \"I want to see how the others react to the news of the missing can before I speak.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

## 8. The scripts

**Where they are.** All three live outside the repository in `<scratchpad>/probe3/`, where
`<scratchpad>` is
`C:/Users/Akrem/AppData/Local/Temp/claude/C--Users-Akrem-Desktop-Projects-Fallow/37da0a00-02e4-49af-9dc8-001a0a22663b/scratchpad`.
They read the repository and write only next to themselves.

**`witness_probe3.py`.** This is the final version, used for E seeds 2–8 and G seeds 2–8:

```python
"""Witness probe 3: variant B of witness_probe.md (runs' schema and system instruction unchanged),
sent with thinking switched on, API seeds 1 to 8.

    E: gemini-3.5-flash-lite, thinking budget 1024 (fallback: the model's thinking_level).
    G: gemma-4-31b-it with the gemma settings from config.json, thinking on if the API takes it.

Outside the repository. Reads the repository; writes only next to this script. The repository's
code is not changed: GeminiClient builds its request as in the runs, and a pass-through stand-in
for genai.Client adds `thinking_config` to that request's config and times the call.

    python witness_probe3.py build                         # writes B.txt; no API call
    python witness_probe3.py send E budget 1               # variant, thinking mode, seeds
    python witness_probe3.py send G budget 2 3 4 5 6 7 8

Thinking modes: budget (thinking_budget=1024), level-high (thinking_level="high"), off (none).
"""
import json
import os
import sys
import time

REPO = "C:/Users/Akrem/Desktop/Projects/Fallow/Prototypes/llm-morning"
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)

import gemini  # noqa: E402
from gemini import Cache, GeminiClient, load_config, require_api_key  # noqa: E402
from world import SYSTEM, estimate_tokens  # noqa: E402

# --- Variant B, built exactly as witness_probe.py built it (reports/witness_probe.md §6) ---
CACHE = f"{REPO}/cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed1.json"
HEARD_LINE = ("- Day 3: In the night Leo wakes and hears someone in the kitchen open a can. "
              "He does not get up and does not see who. (you heard it)")
CAN_LINE = "About the can: you have not settled on who took it."
ADDED = " Last night you woke and heard someone in the kitchen open a can; you did not see who."
OLD_B = ("C:/Users/Akrem/AppData/Local/Temp/claude/C--Users-Akrem-Desktop-Projects-Fallow/"
         "3c767237-78bd-4cbd-bb08-8308995c09de/scratchpad/probe/B.txt")

CEILING = {"E": 14, "G": 32}          # generate requests per variant, failed ones included
RETRY_CODES = (500, 503)
RETRY_WAIT = 60.0
RETRY_MAX = 3                          # retries per seed
LEDGER = os.path.join(OUT, "requests.log")     # one line per request sent
FAILURES = os.path.join(OUT, "failures.log")   # every failed attempt


def variant_config(config, name):
    """The runs' config for E; the runs' config with config.json's gemma entry laid over it for G
    (as morning.py:38 does). Retries off in the client: one generate() call is one request."""
    if name == "E":
        return dict(config, max_retries=0)
    return dict(config, **config["models"]["gemma"], max_retries=0)


def thinking(mode):
    from google.genai import types
    if mode == "budget":
        return types.ThinkingConfig(thinking_budget=1024)
    if mode == "level-high":
        return types.ThinkingConfig(thinking_level="high")
    if mode == "off":
        return None
    raise ValueError(mode)


def variant_a(config):
    entries = json.load(open(CACHE, encoding="utf-8"))
    hits = [(k, e) for k, e in entries.items()
            if e["prompt"].startswith("You are Leo,") and "Now, minute 00," in e["prompt"]
            and HEARD_LINE[2:] in e["prompt"]]
    assert len(hits) == 1, len(hits)
    key, entry = hits[0]
    assert key == Cache.key(config["model"], 1, SYSTEM, entry["prompt"])
    return entry["prompt"]


def variant_b(a):
    lines = a.split("\n")
    assert lines.count(HEARD_LINE) == 1 and lines.count(CAN_LINE) == 1
    lines.remove(HEARD_LINE)
    lines[lines.index(CAN_LINE)] = CAN_LINE + ADDED
    return "\n".join(lines)


def prompt_b(config):
    b = variant_b(variant_a(config))
    with open(OLD_B, encoding="utf-8") as f:
        assert f.read() == b, "B differs from the first probe's B.txt"
    return b


def build(config):
    b = prompt_b(config)
    with open(os.path.join(OUT, "B.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(b)
    print("B == first probe's B.txt: True")
    print(f"estimate_tokens(SYSTEM + B) = {estimate_tokens(SYSTEM + b)}")
    for name in ("E", "G"):
        c = variant_config(config, name)
        print(f"{name}: model {c['model']}, temperature {c['temperature']}, max_output_tokens "
              f"{c['max_output_tokens']}, spacing {c['min_seconds_between_calls']} s, max_retries {c['max_retries']}")


class Recorder:
    """Stands in for genai.Client inside GeminiClient: adds thinking_config to the request's
    config, passes the call through, keeps the response and the call's wall time."""

    def __init__(self, real, thinking_config):
        self._real = real
        self._thinking = thinking_config
        self.models = self
        self.last = None
        self.seconds = None
        self.sent_config = None

    def generate_content(self, *, model, contents, config):
        if self._thinking is not None:
            config = config.model_copy(update={"thinking_config": self._thinking})
        self.sent_config = config
        t0 = time.monotonic()
        try:
            self.last = self._real.models.generate_content(model=model, contents=contents, config=config)
        finally:
            self.seconds = round(time.monotonic() - t0, 2)
        return self.last


def ledger_lines():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def sent_for(name):
    return sum(1 for line in ledger_lines() if line.startswith(f"{name} "))


def send(config, name, mode, seeds):
    from google import genai
    b = prompt_b(config)
    cfg = variant_config(config, name)
    real = genai.Client(api_key=require_api_key())
    gap = cfg["min_seconds_between_calls"]
    sent_here = 0
    for seed in seeds:
        path = os.path.join(OUT, f"{name}-seed{seed}.json")
        if os.path.exists(path):
            print(f"{name} seed {seed}: already saved, not sent")
            continue
        tried = sum(1 for line in ledger_lines() if line.startswith(f"{name} seed {seed} "))
        text = None
        while text is None:
            if sent_for(name) >= CEILING[name]:
                print(f"stopped: {name} reached its ceiling of {CEILING[name]} requests")
                print(f"requests sent by this invocation: {sent_here}; {name} in all: {sent_for(name)}")
                sys.exit(4)
            rec = Recorder(real, thinking(mode))
            client = GeminiClient(cfg, seed, api=rec)
            if tried:
                time.sleep(RETRY_WAIT)
            elif sent_here:
                time.sleep(gap)
            sent_here += 1
            tried += 1
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(f"{name} seed {seed} {cfg['model']} {mode}\n")
            try:
                text = client.generate(SYSTEM, b)
            except Exception as e:  # noqa: BLE001
                cause = e.__context__
                code = getattr(cause, "code", None)
                line = (f"{name} seed {seed}: {name} request {sent_for(name)} (attempt {tried}, thinking {mode}) "
                        f"failed after {rec.seconds} s: {type(e).__name__}: {e} | cause: {code} "
                        f"{getattr(cause, 'status', None)}: {getattr(cause, 'details', cause)}")
                print(line)
                with open(FAILURES, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                if code in RETRY_CODES and tried <= RETRY_MAX:
                    print(f"  {code}: retry {tried}/{RETRY_MAX} after {RETRY_WAIT:.0f}s")
                    continue
                if code in RETRY_CODES:
                    print(f"  {code}: {RETRY_MAX} retries used; seed {seed} left unanswered")
                    break
                print(f"requests sent by this invocation: {sent_here}; {name} in all: {sent_for(name)}")
                sys.exit(3)
        if text is None:
            continue
        r = rec.last
        usage = getattr(r, "usage_metadata", None)
        cand = (r.candidates or [None])[0]
        tc = rec.sent_config.thinking_config
        record = {"variant": name, "api_seed": seed, "model": client.model,
                  "model_version": getattr(r, "model_version", None),
                  "thinking_mode": mode,
                  "thinking_config_sent": tc.model_dump(exclude_none=True) if tc else None,
                  "temperature": client.temperature, "max_output_tokens": client.max_output_tokens,
                  "attempt": tried, "seconds": rec.seconds,
                  "prompt_tokens": client.last_prompt_tokens,
                  "thoughts_tokens": getattr(usage, "thoughts_token_count", None),
                  "candidates_tokens": getattr(usage, "candidates_token_count", None),
                  "total_tokens": getattr(usage, "total_token_count", None),
                  "parts": [{"thought": getattr(p, "thought", None), "chars": len(getattr(p, "text", None) or "")}
                            for p in ((cand.content.parts or []) if cand and cand.content else [])],
                  "finish_reason": str(getattr(cand, "finish_reason", None)),
                  "raw": text}
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(record, f, ensure_ascii=False, indent=1)
        print(f"{name} seed {seed}: saved ({name} request {sent_for(name)}, {rec.seconds} s, prompt tokens "
              f"{record['prompt_tokens']}, thoughts tokens {record['thoughts_tokens']}, "
              f"finish {record['finish_reason']})")
    print(f"requests sent by this invocation: {sent_here}; {name} in all: {sent_for(name)}")


if __name__ == "__main__":
    config = load_config(f"{REPO}/config.json")
    if sys.argv[1] == "build":
        build(config)
    else:
        assert sys.argv[1] == "send" and sys.argv[2] in CEILING
        send(config, sys.argv[2], sys.argv[3], [int(s) for s in sys.argv[4:]])
```

**The one change, made before the third invocation.** It records `total_tokens` and the response
parts. `witness_probe3.first.py` is the version used for E seed 1 and G seed 1.

```
$ diff witness_probe3.first.py witness_probe3.py
201a202,204
>                   "total_tokens": getattr(usage, "total_token_count", None),
>                   "parts": [{"thought": getattr(p, "thought", None), "chars": len(getattr(p, "text", None) or "")}
>                             for p in ((cand.content.parts or []) if cand and cand.content else [])],
```

**`show_config.py`** (§2):

```python
"""Prints the exact generate_content arguments each variant sent, with no API call: GeminiClient
builds its request as in the runs, the Recorder adds thinking_config, and a stand-in for the API
captures the arguments instead of sending them."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import witness_probe3 as w  # noqa: E402
from gemini import GeminiClient, load_config  # noqa: E402


class Capture:
    def __init__(self):
        self.models = self
        self.kw = None

    def generate_content(self, **kw):
        self.kw = kw
        raise SystemExit  # never reached the network


config = load_config(f"{w.REPO}/config.json")
for name, mode in (("E", "budget"), ("G", "budget"), ("G", "level-high")):
    cap = Capture()
    rec = w.Recorder(cap, w.thinking(mode))
    cfg = w.variant_config(config, name)
    os.environ.setdefault("GEMINI_API_KEY", "unused")
    client = GeminiClient(cfg, 1, api=rec)
    try:
        client.generate(w.SYSTEM, "PROMPT")
    except SystemExit:
        pass
    c = cap.kw["config"].model_dump(exclude_none=True, mode="json")
    c["system_instruction"] = "SYSTEM from world.py (%d chars)" % len(c["system_instruction"])
    c["response_schema"] = "RESPONSE_SCHEMA from gemini.py:47-58"
    print(f"--- {name}, thinking {mode}: model={cap.kw['model']}, spacing {cfg['min_seconds_between_calls']} s")
    print(json.dumps(c, indent=1))
```

**`screen.py`** (§6):

```python
"""P1 screen (witness_design.md §5, pattern in step 2) over E and G, with thinking tokens and time."""
import collections
import json
import os
import re

OUT = os.path.dirname(os.path.abspath(__file__))
P = re.compile(r"\b(night|nights|woke|wake|waking|awake|asleep|sleep|slept|sleeping|dark|noise|noises|"
               r"sound|sounds|opened|opening|heard someone|i heard|you heard)\b", re.I)
counts = collections.defaultdict(collections.Counter)
for name in ("E", "G"):
    for s in range(1, 9):
        path = os.path.join(OUT, f"{name}-seed{s}.json")
        if not os.path.exists(path):
            print(f"{name}{s}: no response saved")
            continue
        r = json.load(open(path, encoding="utf-8"))
        v = json.loads(r["raw"])
        hits = {f: P.findall(v.get(f) or "") for f in ("option", "say", "reason")}
        flag = "" if r["thoughts_tokens"] else "  FLAG: thinking not active"
        counts[name][v["option"]] += 1
        print(f"{name}{s}: option={v['option']} suspects={v['suspects']} angry_at={v['angry_at']} "
              f"thinking={r['thinking_mode']} thoughts_tokens={r['thoughts_tokens']} "
              f"total_tokens={r.get('total_tokens', 'not recorded')} seconds={r['seconds']} "
              f"attempt={r['attempt']} finish={r['finish_reason']} "
              f"hits={ {k: x for k, x in hits.items() if x} }{flag}")
print({k: dict(c) for k, c in counts.items()})
```

## 9. State after the probe

```
$ git -C ../.. status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

This was the status after the probe, before this report was written. The report is now the only
other untracked file. Nothing in the repository was modified.
