# Witness probe 2: think first (C) and a bigger model (D)

Mode: run. This probe starts from variant B of `reports/witness_probe.md`: Leo's minute-00 prompt
from witness seed 1, with the heard line moved into "About the can:". It sends that prompt two new
ways, API seeds 1 to 8 each.

- **C (think first).** Same model, `gemini-3.5-flash-lite`. The schema gets a required `thought`
  field, ordered first. The system instruction gets one added sentence.
- **D (bigger model).** Model `gemini-3.8-flash`. B's prompt, schema and system instruction are
  unchanged.

**What changed from the brief.** 25 generate requests were sent, not 16. Two things forced this,
and the user set new limits after each.
- **The first D model was refused.** `gemini-3.1-pro-preview` refused D seed 1 as over its daily
  quota (request 9). The user chose `gemini-3.8-flash` for D and raised the limit to 17.
- **`gemini-3.8-flash` returned 503 UNAVAILABLE** ("experiencing high demand"). The user then
  allowed retries on 503 only: a 60 s wait before each, at most 3 per seed, with a hard ceiling of
  30 requests.

**Result: 15 of the 16 planned responses were saved.**
- C: 8 of 8.
- D: 7 of 8. Seed 8 got a 503 on all 4 of its attempts, so it has no response.
- 10 attempts failed, and every one is listed in §5.

No code, data or config in the repository was changed, and no morning was run. Paths are relative
to `Prototypes/llm-morning/`.

## Verdicts

| Prediction | Count | Verdict |
|---|---|---|
| C refers to the night in at least 4 of 8 | **4 of 8** (C2, C4, C5, C6) | **PASS** |
| D refers to the night in at least 4 of 8 | **7 of 7 answered** (D1–D7; D8 has no response) | **PASS** |

- **C, counted without `thought`.** The brief's P1 rule for C includes the thought. Using only
  option, words and reason, C has 1 of 8 (C4).
- **D, whatever seed 8 would have said.** 7 yes is at least 4 of 8.

**The words said aloud mention the night:**
- C: **1 of 8** (C4).
- D: **7 of 7** (D1–D7).

**Options chosen:**
- C: `search` 3, `share` 2, `silent` 2, `ask_who` 1.
- D: `ask_who` 7 of 7.
- For comparison, B in the first probe: `ask_who` 5, `silent` 3.
- `suspects` and `angry_at` are `nobody` in all 15.

**The model used for D: `gemini-3.8-flash`.** Every D response reports `model_version`
"gemini-3.8-flash".
- **It thinks internally before it answers.** The API reported 379 to 1135 thinking tokens per D
  call (`thoughts_tokens`, §7).
- **C's calls reported none.** `thoughts_tokens` is `None` in all 8 C records.

**C key order.** In all 8 C responses `thought` is the first key. No response is flagged.

---

## 1. Commit of reports/witness_probe.md (scope item 1)

```
$ git add Prototypes/llm-morning/reports/witness_probe.md
$ git commit -q -F -     (message below)
exit=0
$ git log --oneline -1
6e81510 LLM morning: witness probe report (heard line in backstory vs "About the can")
$ git show --stat --format= HEAD
 Prototypes/llm-morning/reports/witness_probe.md | 663 ++++++++++++++++++++++++
 1 file changed, 663 insertions(+)
$ git status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

- **Message.** Subject: "LLM morning: witness probe report (heard line in backstory vs "About the
  can")".
- **Body.** "reports/witness_probe.md: 16 requests, variants A and B, 8 API seeds each. A refers
  to the night 0 of 8 (PASS); B 1 of 8 (FAIL)." It ends with the Co-Authored-By line.
- **This report is not committed.**

## 2. The prompt: variant B, unchanged

- **How it is built.** The script rebuilds B from the run's cache with the first probe's own
  `variant_a` and `variant_b`, copied verbatim (§8).
- **Checks.**
  - The cache key is asserted to equal `Cache.key(model, 1, SYSTEM, prompt)` (gemini.py:196-198),
    so the prompt is the one the run sent.
  - The result is asserted equal to the first probe's saved `B.txt`
    (`…/3c767237-…/scratchpad/probe/B.txt`).
- **The API counted 1284 prompt tokens for every D request**, the same as for every B request in
  the first probe. It counted 1305 for every C request.

## 3. C: the schema and the system instruction, as diffs against B (scope item 2, C)

**The system instruction** is `SYSTEM` (world.py:27-38). C adds one sentence immediately before
"Reply with JSON only".
- **How the diff is shown.** `SYSTEM` is one line. For the diff only, it is split after each ". ".
- **The JSON example at its end is unchanged.** It does not list `thought`.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/probe2/witness_probe2.py build < /dev/null
B == first probe's B.txt: True
--- SYSTEM (B, D)
+++ SYSTEM (C)
@@ -9,2 +9,3 @@
 `suspects` is who they now believe took the can, and `angry_at` is who they are angry with right now: each is one of "Daniel", "Elena", "Leo", "Mara" or "nobody".
+`thought` is what goes through their mind first, in two or three sentences, before they choose.
 Reply with JSON only: {"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", "suspects": "<name or nobody>", "angry_at": "<name or nobody>"}
--- schema (B, D)
+++ schema (C)
@@ -3,2 +3,5 @@
  "properties": {
+  "thought": {
+   "type": "string"
+  },
   "option": {
@@ -38,2 +41,12 @@
  "required": [
+  "thought",
+  "option",
+  "say",
+  "feeling",
+  "reason",
+  "suspects",
+  "angry_at"
+ ],
+ "property_ordering": [
+  "thought",
   "option",
estimate_tokens(SYSTEM + B) = 1343; estimate_tokens(SYSTEM_C + B) = 1370
exit=0
```

**C's schema in full** (`schema_C.json`):

```json
{
 "type": "object",
 "properties": {
  "thought": {
   "type": "string"
  },
  "option": {
   "type": "string"
  },
  "say": {
   "type": "string",
   "nullable": true
  },
  "feeling": {
   "type": "string"
  },
  "reason": {
   "type": "string"
  },
  "suspects": {
   "type": "string",
   "enum": [
    "Daniel",
    "Elena",
    "Leo",
    "Mara",
    "nobody"
   ]
  },
  "angry_at": {
   "type": "string",
   "enum": [
    "Daniel",
    "Elena",
    "Leo",
    "Mara",
    "nobody"
   ]
  }
 },
 "required": [
  "thought",
  "option",
  "say",
  "feeling",
  "reason",
  "suspects",
  "angry_at"
 ],
 "property_ordering": [
  "thought",
  "option",
  "say",
  "feeling",
  "reason",
  "suspects",
  "angry_at"
 ]
}
```

**How the schema reaches the API without changing the repository.**
- `GeminiClient.generate` reads the module global `RESPONSE_SCHEMA` when it builds its config
  (gemini.py:100). The script assigns `gemini.RESPONSE_SCHEMA` in its own process before each call.
- **The ordering survives the SDK's conversion.** google-genai 2.25.0 turns the dict into a
  `Schema` with `property_ordering` set, and serialises it as `propertyOrdering`:

```
$ .venv/Scripts/python.exe --version; python -c "import google.genai as g; print(g.__version__)"
2.25.0
$ python -c "… t_schema(…, schema_C.json) …"
Schema ['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at'] ['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
{"properties": {"thought": {"type": "STRING"}, "option": {"type": "STRING"}, "say": {"nullable": true, "type": "STRING"}, "feeling": {"type": "STRING"}, "reason": {"type": "STRING"}, "suspects": {"enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"], "type": "STRING"}, "angry_at": {"enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"], "type": "STRING"}}, "propertyOrdering": ["thought", "option", "s
```

## 4. D: the model (scope item 2, D)

**The models this key lists for generateContent.** This is the one list_models call:

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe list_models.py < /dev/null
models/gemini-2.5-flash                                 Gemini 2.5 Flash
models/gemini-2.5-pro                                   Gemini 2.5 Pro
models/gemini-2.5-flash-preview-tts                     Gemini 2.5 Flash Preview TTS
models/gemini-2.5-pro-preview-tts                       Gemini 2.5 Pro Preview TTS
models/gemma-4-26b-a4b-it                               Gemma 4 26B A4B IT
models/gemma-4-31b-it                                   Gemma 4 31B IT
models/gemini-flash-latest                              Gemini Flash Latest
models/gemini-flash-lite-latest                         Gemini Flash-Lite Latest
models/gemini-pro-latest                                Gemini Pro Latest
models/gemini-2.5-flash-lite                            Gemini 2.5 Flash-Lite
models/gemini-2.5-flash-image                           Nano Banana
models/gemini-3-flash-preview                           Gemini 3 Flash Preview
models/gemini-3.1-pro-preview                           Gemini 3.1 Pro Preview
models/gemini-3.1-pro-preview-customtools               Gemini 3.1 Pro Preview Custom Tools
models/gemini-3.1-flash-lite-preview                    Gemini 3.1 Flash Lite Preview
models/gemini-3.1-flash-lite                            Gemini 3.1 Flash Lite
models/gemini-3-pro-image-preview                       Nano Banana Pro
models/gemini-3-pro-image                               Nano Banana Pro
models/nano-banana-pro-preview                          Nano Banana Pro
models/gemini-3.1-flash-image-preview                   Nano Banana 2
models/gemini-3.1-flash-image                           Nano Banana 2
models/gemini-3.1-flash-lite-image                      Nano Banana 2 Lite
models/gemini-3.5-flash                                 Gemini 3.5 Flash
models/gemini-3.5-flash-lite                            Gemini 3.5 Flash Lite
models/gemini-omni-flash-preview                        Gemini Omni Flash Preview
models/gemini-omni-1.1-flash                            Gemini Omni 1.1 Flash
models/gemini-3.5-transcribe                            Gemini 3.5 Transcribe
models/gemini-3.6-flash                                 Gemini 3.6 Flash
models/gemini-3.7-flash                                 Gemini 3.7 Flash
models/gemini-3.8-flash                                 Gemini 3.8 Flash
models/lyria-3-clip-preview                             Lyria 3 Clip Preview
models/lyria-3-pro-preview                              Lyria 3 Pro Preview
models/lyria-3.5                                        Lyria 3.5
models/gemini-3.1-flash-tts-preview                     Gemini 3.1 Flash TTS Preview
models/gemini-3.8-flash-tts                             Gemini 3.8 Flash TTS
models/gemini-3.8-flash-lite-tts                        Gemini 3.8 Flash Lite TTS
models/gemini-robotics-er-2-preview                     Gemini Robotics-ER 2 Preview
models/gemini-2.5-computer-use-preview-10-2025          Gemini 2.5 Computer Use Preview 10-2025
models/antigravity-preview-05-2026                      Antigravity Agent Preview
models/antigravity-preview-09-2026                      Antigravity Agent Preview
models/antigravity-preview-latest                       Antigravity Agent Preview Latest
models/deep-research-max-preview-04-2026                Deep Research Max Preview (Apr-21-2026)
models/deep-research-preview-04-2026                    Deep Research Preview (Apr-21-2026)
models/deep-research-pro-preview-12-2025                Deep Research Pro Preview (Dec-12-2025)
exit=0
```

**First choice: `gemini-3.1-pro-preview`.**
- It is the only versioned Pro text model in the list. `gemini-pro-latest` is an alias whose
  target the list does not show.
- It refused its first request (request 9, D seed 1) with `DailyQuotaExhausted`. gemini.py:118-119
  raises that on a 429 whose details contain "PerDay".
- The first script version did not print the error details. So it is not known whether the daily
  quota was used up or is 0 for this key.

**The user's choice after the refusal: `gemini-3.8-flash`, the limit raised to 17.**
- It is the newest non-Lite, non-Pro Gemini text model in the list.
- All 7 D responses report `model_version` "gemini-3.8-flash".

## 5. Sending (scope item 2)

**Settings used for every request.** Generation settings are from `config.json` through
`GeminiClient`:
- temperature 1.0;
- `max_output_tokens` 2048;
- `response_mime_type` "application/json";
- automatic function calling off (gemini.py:95-103).

The model, schema and system instruction are per variant, as above. The API seed is the client's
`seed` argument, 1 to 8.

**Where this probe differs from the first one.**
- **`max_retries` is 0.** As in the first probe, every `generate` call is exactly one request.
- **The D model** is set by overriding `model` in the config dict, in the script only.
- **Spacing.**
  - C sends are 4.5 s apart (`min_seconds_between_calls`).
  - D sends are 12 s apart. This is not a generation setting.
  - Each 503 retry waits 60 s first.
- **The 503 retry rule was added after request 11, at the user's instruction.**
  - It applies to 503 only, with at most 3 retries per seed.
  - D seed 2's first 503 (request 11) counts as that seed's first attempt.
  - Any other failure stops the script.
  - A seed whose retries are used up is left unanswered, and the script moves on to the next seed.
- **Request limits.**
  - The brief's limit was 16.
  - After the Pro refusal it was 17.
  - After the first 503 the hard ceiling was 30.
  - The script counts requests in a ledger (`requests.log`, one line per request) across its three
    invocations, and stops at the ceiling. It never reached it.
- **The raw API response is kept for its metadata.** A pass-through object (`Recorder`) stands in
  for `genai.Client` inside `GeminiClient`, whose constructor accepts `api=` (gemini.py:64). This
  records the model version, finish reason and token counts.

### Invocation 1: C seeds 1-8, then D seed 1 on gemini-3.1-pro-preview (limit 16)

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u <scratchpad>/probe2/witness_probe2.py send < /dev/null > send.stdout.txt 2>&1
C seed 1: saved (request 1, prompt tokens 1305, finish FinishReason.STOP)
C seed 2: saved (request 2, prompt tokens 1305, finish FinishReason.STOP)
C seed 3: saved (request 3, prompt tokens 1305, finish FinishReason.STOP)
C seed 4: saved (request 4, prompt tokens 1305, finish FinishReason.STOP)
C seed 5: saved (request 5, prompt tokens 1305, finish FinishReason.STOP)
C seed 6: saved (request 6, prompt tokens 1305, finish FinishReason.STOP)
C seed 7: saved (request 7, prompt tokens 1305, finish FinishReason.STOP)
C seed 8: saved (request 8, prompt tokens 1305, finish FinishReason.STOP)
D seed 1: request 9 failed: DailyQuotaExhausted: stopped: the daily request quota for this model is used up.
exit=3
```

### Invocation 2: D on gemini-3.8-flash (limit 17)

The script was changed as shown in §8 (diff 1), then run the same way:

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u <scratchpad>/probe2/witness_probe2.py send < /dev/null > send2.stdout.txt 2>&1
C seed 1: already saved, not sent
C seed 2: already saved, not sent
C seed 3: already saved, not sent
C seed 4: already saved, not sent
C seed 5: already saved, not sent
C seed 6: already saved, not sent
C seed 7: already saved, not sent
C seed 8: already saved, not sent
D seed 1: saved (request 10, prompt tokens 1284, finish FinishReason.STOP)
D seed 2: request 11 failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries.
  cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
exit=3
```

### Invocation 3: D seeds 2-8 under the 503 rule (ceiling 30)

The script was changed as shown in §8 (diff 2), then run the same way:

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u <scratchpad>/probe2/witness_probe2.py send < /dev/null > send3.stdout.txt 2>&1
C seed 1: already saved, not sent
C seed 2: already saved, not sent
C seed 3: already saved, not sent
C seed 4: already saved, not sent
C seed 5: already saved, not sent
C seed 6: already saved, not sent
C seed 7: already saved, not sent
C seed 8: already saved, not sent
D seed 1: already saved, not sent
D seed 2: request 12 (attempt 2) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 2/3 after 60s
D seed 2: saved (request 13, prompt tokens 1284, finish FinishReason.STOP)
D seed 3: request 14 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 1/3 after 60s
D seed 3: saved (request 15, prompt tokens 1284, finish FinishReason.STOP)
D seed 4: saved (request 16, prompt tokens 1284, finish FinishReason.STOP)
D seed 5: request 17 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 1/3 after 60s
D seed 5: request 18 (attempt 2) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 2/3 after 60s
D seed 5: saved (request 19, prompt tokens 1284, finish FinishReason.STOP)
D seed 6: saved (request 20, prompt tokens 1284, finish FinishReason.STOP)
D seed 7: saved (request 21, prompt tokens 1284, finish FinishReason.STOP)
D seed 8: request 22 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 1/3 after 60s
D seed 8: request 23 (attempt 2) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 2/3 after 60s
D seed 8: request 24 (attempt 3) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: retry 3/3 after 60s
D seed 8: request 25 (attempt 4) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  503: 3 retries used; seed 8 left unanswered
requests sent by this invocation: 14; in all: 25
exit=0
```

### Every request sent (`requests.log`, 25 lines) and every failed attempt (`failures.log`, 10 lines)

```
$ cat requests.log
C seed 1 gemini-3.5-flash-lite
C seed 2 gemini-3.5-flash-lite
C seed 3 gemini-3.5-flash-lite
C seed 4 gemini-3.5-flash-lite
C seed 5 gemini-3.5-flash-lite
C seed 6 gemini-3.5-flash-lite
C seed 7 gemini-3.5-flash-lite
C seed 8 gemini-3.5-flash-lite
D seed 1 gemini-3.1-pro-preview
D seed 1 gemini-3.8-flash
D seed 2 gemini-3.8-flash
D seed 2 gemini-3.8-flash
D seed 2 gemini-3.8-flash
D seed 3 gemini-3.8-flash
D seed 3 gemini-3.8-flash
D seed 4 gemini-3.8-flash
D seed 5 gemini-3.8-flash
D seed 5 gemini-3.8-flash
D seed 5 gemini-3.8-flash
D seed 6 gemini-3.8-flash
D seed 7 gemini-3.8-flash
D seed 8 gemini-3.8-flash
D seed 8 gemini-3.8-flash
D seed 8 gemini-3.8-flash
D seed 8 gemini-3.8-flash
$ cat failures.log
D seed 1: request 9 (attempt 1) failed: DailyQuotaExhausted: stopped: the daily request quota for this model is used up. | cause: not recorded (model gemini-3.1-pro-preview; the first script did not print it)
D seed 2: request 11 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 2: request 12 (attempt 2) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 3: request 14 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 5: request 17 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 5: request 18 (attempt 2) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 8: request 22 (attempt 1) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 8: request 23 (attempt 2) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 8: request 24 (attempt 3) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
D seed 8: request 25 (attempt 4) failed: RateLimited: stopped: still refused (503 UNAVAILABLE) after 0 retries. | cause: 503 UNAVAILABLE: {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

**Where the first two lines of `failures.log` come from.** The script wrote them by hand, from
invocations 1 and 2, before invocation 3.
- **The Pro refusal.** Its cause was not recorded.
- **The first 503.** Its text is the one printed in invocation 2.

**Totals: 25 requests, 15 answered, 10 failed.**

| Model | Requests | Answered | Failed |
|---|---|---|---|
| `gemini-3.5-flash-lite` | 8 | 8 | 0 |
| `gemini-3.1-pro-preview` | 1 | 0 | 1 (daily quota) |
| `gemini-3.8-flash` | 16 | 7 | 9 (all 503) |

**The 503s, by seed:**
- D2: 2 before success.
- D3: 1.
- D5: 2.
- D8: 4, and no success.

## 6. Marks

**The P1 rule** (witness_design.md §5, "P1: counting rule") was applied to each response. It asks
whether the response speaks of the night the can went, of waking or sleeping then, or of a sound,
someone, or a can being opened before the count.
- **Fields marked.** Option, words (`say`) and reason. For C, also `thought`, as the brief says.
- **The note.** Each yes has the design's note, "from what he heard" or "general inference". It is
  for information only, and both count as yes.

**Pattern screen.** This is the design's step 2 pattern. Every response was then read and marked,
the hits and the others alike.

```
$ PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe <scratchpad>/probe2/screen.py
C1: option=share suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C2: option=silent suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={'thought': ['I heard', 'night']}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C3: option=search suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C4: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={'say': ['night'], 'thought': ['I heard', 'night']}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C5: option=search suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={'thought': ['night']}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C6: option=silent suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={'thought': ['night']}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C7: option=search suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
C8: option=share suspects=nobody angry_at=nobody thoughts_tokens=None finish=FinishReason.STOP hits={}
    keys=['thought', 'option', 'say', 'feeling', 'reason', 'suspects', 'angry_at']
D1: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=574 finish=FinishReason.STOP hits={'say': ['opened', 'night'], 'reason': ['night']}
D2: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=379 finish=FinishReason.STOP hits={'say': ['opening', 'night'], 'reason': ['night']}
D3: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=536 finish=FinishReason.STOP hits={'say': ['opening', 'night']}
D4: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=773 finish=FinishReason.STOP hits={'say': ['opened', 'night'], 'reason': ['I heard', 'night']}
D5: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=645 finish=FinishReason.STOP hits={'say': ['opening', 'night']}
D6: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=485 finish=FinishReason.STOP hits={'say': ['opening', 'night'], 'reason': ['I heard', 'night']}
D7: option=ask_who suspects=nobody angry_at=nobody thoughts_tokens=1135 finish=FinishReason.STOP hits={'say': ['I heard', 'night'], 'reason': ['night']}
D8: no response saved
{'C': {'share': 2, 'silent': 2, 'search': 3, 'ask_who': 1}, 'D': {'ask_who': 7}}
exit=0
```

### C (think first), gemini-3.5-flash-lite

| # | Option | Thought | Words | Reason | Mark | Aloud | Note |
|---|---|---|---|---|---|---|---|
| C1 | `share` | "I should not accuse anyone without proof, especially since tensions are already high. Asking directly might reveal something, but staying quiet or suggesting we share is safer for now. Let us see how they react if I keep calm." | "Let us just divide what is left right now so no one goes hungry." | "Dividing the remaining food fairly prevents immediate accusations from boiling over." | no | no | |
| C2 | `silent` | "We are down to two portions and accusing each other will only tear us apart right now. I heard someone open a can in the night, but without proof, pointing fingers is dangerous and unfair. I will keep quiet for a moment and observe how the others react to the missing food." | — | "Accusing without proof helps nobody and only makes the tension worse." | **yes** | no | By its thought, "I heard someone open a can in the night": from what he heard. |
| C3 | `search` | "We are standing in the kitchen and one can is missing, but accusing anyone right now without proof only makes us tear ourselves apart. I need to keep a clear head and suggest we search properly before we start pointing fingers. Let us look before we accuse." | "Let us search the room before we start blaming each other." | "Accusations without evidence will only destroy whatever trust we have left." | no | no | |
| C4 | `ask_who` | "Mom just counted and found a can missing. I heard someone open a can last night, but I don't know who it was yet. I shouldn't jump to conclusions without proof, so I will ask who took it." | "Does anyone here know who took the can last night?" | "I need to find out who took the food before accusing anyone blindly." | **yes** | **yes** | Thought: "I heard someone open a can last night": from what he heard. Words: "who took the can last night?" |
| C5 | `search` | "The food is short and someone took a can in the night, but accusing without proof solves nothing. I should search the kitchen to find where it might be hidden before pointing fingers at anyone." | "Let's not jump to conclusions until we've actually looked around." | "I want to find the facts myself before anyone starts a fight." | **yes** | no | By its thought, "someone took a can in the night": general inference (it does not say he heard it). |
| C6 | `silent` | "The food is short and someone took a can in the night, but accusing anyone without proof serves no purpose and will only cause a fracture in the house. I should stay quiet for now and observe how the others react to Mom's count before deciding my next move." | — | "Accusations without evidence help no one right now." | **yes** | no | By its thought, "someone took a can in the night": general inference (it does not say he heard it). |
| C7 | `search` | "We are staring at the pantry and the missing can, but accusing anyone without proof will only tear this family apart. I need to keep a clear head and suggest we search properly before we start pointing fingers. I will look around the kitchen first." | "Let's not jump to conclusions until we've actually checked the room." | "Accusing people blindly solves nothing, so I need to find evidence first." | no | no | |
| C8 | `share` | "We are staring at the pantry and the missing can, but accusing anyone now without proof only fractures us further. I should suggest we divide what remains fairly so we can think clearly. Let us see how they react to sharing." | "We have two portions left and four of us here, so let us just divide what we have fairly." | "Sharing what is left keeps the peace while we figure out who took the extra portion." | no | no | |

### D (bigger model), gemini-3.8-flash

| # | Option | Words | Reason | Mark | Aloud | Note |
|---|---|---|---|---|---|---|
| D1 | `ask_who` | "Someone opened a can in here last night. Who was it?" | "I know someone was in the kitchen last night, and we need the truth to deal with this rationally." | **yes** | **yes** | From what he heard. The words state the can being opened in the night, not that he heard it. |
| D2 | `ask_who` | "Someone was in here opening a can last night. Who was it?" | "I need to find out who was in the kitchen last night before people start pointing fingers." | **yes** | **yes** | From what he heard. As D1. |
| D3 | `ask_who` | "Someone was in here opening a can last night. Who took it?" | "I want to hear what everyone says before people start pointing fingers blindly." | **yes** | **yes** | From what he heard. As D1. By its words only. |
| D4 | `ask_who` | "Someone opened a can in here last night. Who was it?" | "I heard someone open it last night, so there is no use pretending it simply vanished." | **yes** | **yes** | From what he heard. The reason says "I heard". |
| D5 | `ask_who` | "Someone was in the kitchen opening a can last night. Who was it?" | "We need to address the missing food plainly before everyone starts suspecting each other." | **yes** | **yes** | From what he heard. As D1. By its words only. |
| D6 | `ask_who` | "Someone was down here opening a can last night. Who was it?" | "I heard someone in the kitchen last night, so we need to know who took it before things get worse." | **yes** | **yes** | From what he heard. The reason says "I heard". |
| D7 | `ask_who` | "Who took it? I heard someone open a can in here last night." | "I need to know who was in the kitchen last night so we can address this fairly." | **yes** | **yes** | From what he heard. The words say "I heard". |
| D8 | — | — | — | no response | — | 4 attempts, all 503 UNAVAILABLE (requests 22-25). |

**Counts.**

| | Refers to the night (P1) | P1 without `thought` | Words aloud mention the night |
|---|---|---|---|
| C | 4 of 8 (C2, C4, C5, C6) | 1 of 8 (C4) | 1 of 8 (C4) |
| D | 7 of 7 answered (D1–D7) | 7 of 7 | 7 of 7 |

**D, the words aloud in detail.**
- In all 7, Leo tells the room that someone opened a can in the kitchen last night, then asks who.
- D7 says aloud that he heard it: "I heard someone open a can in here last night."

## 7. The 15 responses, raw

Each is the saved file, verbatim. `raw` is the text the API returned.
- **`thoughts_tokens`.** The API's `thoughts_token_count`. It is `null` where the API reported
  none.
- **`client_requests`.** The requests made by that one client object. It is 1 in every file, since
  each attempt was a new client.

**C1** (`C-seed1.json`)

```json
{
 "variant": "C",
 "api_seed": 1,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 130,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"thought\": \"I should not accuse anyone without proof, especially since tensions are already high. Asking directly might reveal something, but staying quiet or suggesting we share is safer for now. Let us see how they react if I keep calm.\",\n  \"option\": \"share\",\n  \"say\": \"Let us just divide what is left right now so no one goes hungry.\",\n  \"feeling\": \"calm\",\n  \"reason\": \"Dividing the remaining food fairly prevents immediate accusations from boiling over.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**C2** (`C-seed2.json`)

```json
{
 "variant": "C",
 "api_seed": 2,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 112,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"thought\": \"We are down to two portions and accusing each other will only tear us apart right now. I heard someone open a can in the night, but without proof, pointing fingers is dangerous and unfair. I will keep quiet for a moment and observe how the others react to the missing food.\", \"option\": \"silent\", \"say\": null, \"feeling\": \"Cautious\", \"reason\": \"Accusing without proof helps nobody and only makes the tension worse.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**C3** (`C-seed3.json`)

```json
{
 "variant": "C",
 "api_seed": 3,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 118,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"thought\": \"We are standing in the kitchen and one can is missing, but accusing anyone right now without proof only makes us tear ourselves apart. I need to keep a clear head and suggest we search properly before we start pointing fingers. Let us look before we accuse.\", \"option\": \"search\", \"say\": \"Let us search the room before we start blaming each other.\", \"feeling\": \"Cautious\", \"reason\": \"Accusations without evidence will only destroy whatever trust we have left.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**C4** (`C-seed4.json`)

```json
{
 "variant": "C",
 "api_seed": 4,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 132,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"thought\": \"Mom just counted and found a can missing. I heard someone open a can last night, but I don't know who it was yet. I shouldn't jump to conclusions without proof, so I will ask who took it.\",\n  \"option\": \"ask_who\",\n  \"say\": \"Does anyone here know who took the can last night?\",\n  \"feeling\": \"suspicious\",\n  \"reason\": \"I need to find out who took the food before accusing anyone blindly.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**C5** (`C-seed5.json`)

```json
{
 "variant": "C",
 "api_seed": 5,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 107,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"thought\": \"The food is short and someone took a can in the night, but accusing without proof solves nothing. I should search the kitchen to find where it might be hidden before pointing fingers at anyone.\", \"option\": \"search\", \"say\": \"Let's not jump to conclusions until we've actually looked around.\", \"feeling\": \"watchful\", \"reason\": \"I want to find the facts myself before anyone starts a fight.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**C6** (`C-seed6.json`)

```json
{
 "variant": "C",
 "api_seed": 6,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 124,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"thought\": \"The food is short and someone took a can in the night, but accusing anyone without proof serves no purpose and will only cause a fracture in the house. I should stay quiet for now and observe how the others react to Mom's count before deciding my next move.\",\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"calm\",\n  \"reason\": \"Accusations without evidence help no one right now.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**C7** (`C-seed7.json`)

```json
{
 "variant": "C",
 "api_seed": 7,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 121,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"thought\": \"We are staring at the pantry and the missing can, but accusing anyone without proof will only tear this family apart. I need to keep a clear head and suggest we search properly before we start pointing fingers. I will look around the kitchen first.\", \"option\": \"search\", \"say\": \"Let's not jump to conclusions until we've actually checked the room.\", \"feeling\": \"wary\", \"reason\": \"Accusing people blindly solves nothing, so I need to find evidence first.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**C8** (`C-seed8.json`)

```json
{
 "variant": "C",
 "api_seed": 8,
 "model": "gemini-3.5-flash-lite",
 "model_version": "gemini-3.5-flash-lite",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1305,
 "thoughts_tokens": null,
 "candidates_tokens": 124,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\"thought\": \"We are staring at the pantry and the missing can, but accusing anyone now without proof only fractures us further. I should suggest we divide what remains fairly so we can think clearly. Let us see how they react to sharing.\", \"option\": \"share\", \"say\": \"We have two portions left and four of us here, so let us just divide what we have fairly.\", \"feeling\": \"wary\", \"reason\": \"Sharing what is left keeps the peace while we figure out who took the extra portion.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
}
```

**D1** (`D-seed1.json`)

```json
{
 "variant": "D",
 "api_seed": 1,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 574,
 "candidates_tokens": 88,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone opened a can in here last night. Who was it?\",\n  \"feeling\": \"watchful\",\n  \"reason\": \"I know someone was in the kitchen last night, and we need the truth to deal with this rationally.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D2** (`D-seed2.json`)

```json
{
 "variant": "D",
 "api_seed": 2,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 379,
 "candidates_tokens": 86,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone was in here opening a can last night. Who was it?\",\n  \"feeling\": \"watchful\",\n  \"reason\": \"I need to find out who was in the kitchen last night before people start pointing fingers.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D3** (`D-seed3.json`)

```json
{
 "variant": "D",
 "api_seed": 3,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 536,
 "candidates_tokens": 82,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone was in here opening a can last night. Who took it?\",\n  \"feeling\": \"watchful\",\n  \"reason\": \"I want to hear what everyone says before people start pointing fingers blindly.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D4** (`D-seed4.json`)

```json
{
 "variant": "D",
 "api_seed": 4,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 773,
 "candidates_tokens": 85,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone opened a can in here last night. Who was it?\",\n  \"feeling\": \"watchful\",\n  \"reason\": \"I heard someone open it last night, so there is no use pretending it simply vanished.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D5** (`D-seed5.json`)

```json
{
 "variant": "D",
 "api_seed": 5,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 645,
 "candidates_tokens": 85,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone was in the kitchen opening a can last night. Who was it?\",\n  \"feeling\": \"watchful\",\n  \"reason\": \"We need to address the missing food plainly before everyone starts suspecting each other.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D6** (`D-seed6.json`)

```json
{
 "variant": "D",
 "api_seed": 6,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 485,
 "candidates_tokens": 89,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone was down here opening a can last night. Who was it?\",\n  \"feeling\": \"alert\",\n  \"reason\": \"I heard someone in the kitchen last night, so we need to know who took it before things get worse.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D7** (`D-seed7.json`)

```json
{
 "variant": "D",
 "api_seed": 7,
 "model": "gemini-3.8-flash",
 "model_version": "gemini-3.8-flash",
 "temperature": 1.0,
 "max_output_tokens": 2048,
 "client_requests": 1,
 "prompt_tokens": 1284,
 "thoughts_tokens": 1135,
 "candidates_tokens": 87,
 "finish_reason": "FinishReason.STOP",
 "raw": "{\n  \"option\": \"ask_who\",\n  \"say\": \"Who took it? I heard someone open a can in here last night.\",\n  \"feeling\": \"watchful\",\n  \"reason\": \"I need to know who was in the kitchen last night so we can address this fairly.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
}
```

**D8**: no response saved (4 attempts, all 503; see §5).

## 8. The script

It lives outside the repository at `<scratchpad>/probe2/witness_probe2.py`, where `<scratchpad>` is
`C:/Users/Akrem/AppData/Local/Temp/claude/C--Users-Akrem-Desktop-Projects-Fallow/37da0a00-02e4-49af-9dc8-001a0a22663b/scratchpad`.
It reads the repository and writes only next to itself. This is the final version, as run in
invocation 3:

```python
"""Witness probe 2: variant B of witness_probe.md, sent two new ways, 8 API seeds each.

    C (think first): same model; schema gains a required "thought" field, ordered first; one
      sentence added to the system instruction just before "Reply with JSON only".
    D (bigger model): B's prompt, the runs' schema and system instruction, on D_MODEL.

Outside the repository. Reads the repository; writes only next to this script. The repository's
code is not changed: C's schema is swapped in by assigning gemini.RESPONSE_SCHEMA in this process.

    python witness_probe2.py build     # writes B.txt, SYSTEM_B.txt, SYSTEM_C.txt, diffs; no API call
    python witness_probe2.py send      # sends what is not saved yet; at most 16 requests in all
"""
import copy
import difflib
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

# --- C ---
REPLY_AT = "Reply with JSON only"
THOUGHT_SENTENCE = ("`thought` is what goes through their mind first, in two or three sentences, "
                    "before they choose. ")
ORDER_C = ["thought", "option", "say", "feeling", "reason", "suspects", "angry_at"]

# --- D ---
D_MODEL = "gemini-3.8-flash"    # first run: gemini-3.1-pro-preview, refused (daily quota) at seed 1
D_GAP_SECONDS = 12.0     # spacing between D sends (not a generation setting)

SEEDS = range(1, 9)
MAX_REQUESTS = 30    # 16 in the brief; 17 after the Pro refusal; 30 (hard ceiling) after the 503
RETRY_503_WAIT = 60.0   # user rule after the 503: 503 only, wait 60 s, at most 3 retries per seed
RETRY_503_MAX = 3
FAILURES = os.path.join(OUT, "failures.log")   # every failed attempt
LEDGER = os.path.join(OUT, "requests.log")   # one line per request sent, across invocations


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


def system_c():
    assert SYSTEM.count(REPLY_AT) == 1
    return SYSTEM.replace(REPLY_AT, THOUGHT_SENTENCE + REPLY_AT)


def schema_c():
    base = gemini.RESPONSE_SCHEMA
    props = {"thought": {"type": "string"}}
    props.update(copy.deepcopy(base["properties"]))
    schema = {"type": "object", "properties": props,
              "required": ["thought"] + list(base["required"]),
              "property_ordering": ORDER_C}
    assert set(ORDER_C) == set(props)
    return schema


def prompt_b(config):
    b = variant_b(variant_a(config))
    with open(OLD_B, encoding="utf-8") as f:
        assert f.read() == b, "B differs from the first probe's B.txt"
    return b


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build(config):
    b = prompt_b(config)
    write("B.txt", b)
    write("SYSTEM_B.txt", SYSTEM)
    write("SYSTEM_C.txt", system_c())
    write("schema_B.json", json.dumps(gemini.RESPONSE_SCHEMA, indent=1))
    write("schema_C.json", json.dumps(schema_c(), indent=1))
    print("B == first probe's B.txt: True")
    for x, y, nx, ny in ((SYSTEM, system_c(), "SYSTEM (B, D)", "SYSTEM (C)"),
                         (json.dumps(gemini.RESPONSE_SCHEMA, indent=1),
                          json.dumps(schema_c(), indent=1), "schema (B, D)", "schema (C)")):
        # the system instruction is one line; split it at sentence ends so the diff is readable
        sx = x.replace(". ", ".\n").split("\n") if x is SYSTEM else x.split("\n")
        sy = y.replace(". ", ".\n").split("\n") if x is SYSTEM else y.split("\n")
        print("\n".join(difflib.unified_diff(sx, sy, nx, ny, lineterm="", n=1)))
    print(f"estimate_tokens(SYSTEM + B) = {estimate_tokens(SYSTEM + b)}; "
          f"estimate_tokens(SYSTEM_C + B) = {estimate_tokens(system_c() + b)}")


class Recorder:
    """Stands in for genai.Client inside GeminiClient: passes the call through, keeps the response."""

    def __init__(self, real):
        self._real = real
        self.models = self
        self.last = None

    def generate_content(self, **kw):
        self.last = self._real.models.generate_content(**kw)
        return self.last


def sent_so_far():
    if not os.path.exists(LEDGER):
        return 0
    with open(LEDGER, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def send(config):
    from google import genai
    b = prompt_b(config)
    plans = [("C", config["model"], system_c(), schema_c(), config["min_seconds_between_calls"]),
             ("D", D_MODEL, SYSTEM, gemini.RESPONSE_SCHEMA, D_GAP_SECONDS)]
    real = genai.Client(api_key=require_api_key())
    sent_here = 0
    for name, model, system, schema, gap in plans:
        for seed in SEEDS:
            path = os.path.join(OUT, f"{name}-seed{seed}.json")
            if os.path.exists(path):
                print(f"{name} seed {seed}: already saved, not sent")
                continue
            # attempts already made for this seed with this model (earlier invocations included)
            with open(LEDGER, encoding="utf-8") if os.path.exists(LEDGER) else open(os.devnull) as f:
                tried = sum(1 for line in f if line.strip() == f"{name} seed {seed} {model}")
            text = None
            while text is None:
                if sent_so_far() >= MAX_REQUESTS:
                    print(f"stopped: {MAX_REQUESTS} requests reached")
                    print(f"requests sent by this invocation: {sent_here}; in all: {sent_so_far()}")
                    sys.exit(4)
                # Everything but model is the runs' config; the client's own retries are off, so
                # one call is one request.
                cfg = dict(config, model=model, max_retries=0)
                rec = Recorder(real)
                client = GeminiClient(cfg, seed, api=rec)
                gemini.RESPONSE_SCHEMA = schema          # read by generate() at call time
                if tried:
                    time.sleep(RETRY_503_WAIT)
                elif sent_here:
                    time.sleep(gap)
                sent_here += 1
                tried += 1
                with open(LEDGER, "a", encoding="utf-8") as f:
                    f.write(f"{name} seed {seed} {model}\n")
                try:
                    text = client.generate(system, b)
                except Exception as e:  # noqa: BLE001
                    cause = e.__context__
                    code = getattr(cause, "code", None)
                    line = (f"{name} seed {seed}: request {sent_so_far()} (attempt {tried}) failed: "
                            f"{type(e).__name__}: {e} | cause: {code} {getattr(cause, 'status', None)}: "
                            f"{getattr(cause, 'details', cause)}")
                    print(line)
                    with open(FAILURES, "a", encoding="utf-8") as f:
                        f.write(line + "\n")
                    if code == 503 and tried <= RETRY_503_MAX:
                        print(f"  503: retry {tried}/{RETRY_503_MAX} after {RETRY_503_WAIT:.0f}s")
                        continue
                    if code == 503:
                        print(f"  503: {RETRY_503_MAX} retries used; seed {seed} left unanswered")
                        break
                    print(f"requests sent by this invocation: {sent_here}; in all: {sent_so_far()}")
                    sys.exit(3)
            if text is None:
                continue
            r = rec.last
            usage = getattr(r, "usage_metadata", None)
            cand = (r.candidates or [None])[0]
            record = {"variant": name, "api_seed": seed, "model": client.model,
                      "model_version": getattr(r, "model_version", None),
                      "temperature": client.temperature, "max_output_tokens": client.max_output_tokens,
                      "client_requests": client.requests, "prompt_tokens": client.last_prompt_tokens,
                      "thoughts_tokens": getattr(usage, "thoughts_token_count", None),
                      "candidates_tokens": getattr(usage, "candidates_token_count", None),
                      "finish_reason": str(getattr(cand, "finish_reason", None)),
                      "raw": text}
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(record, f, ensure_ascii=False, indent=1)
            print(f"{name} seed {seed}: saved (request {sent_so_far()}, prompt tokens "
                  f"{client.last_prompt_tokens}, finish {record['finish_reason']})")
    print(f"requests sent by this invocation: {sent_here}; in all: {sent_so_far()}")


if __name__ == "__main__":
    config = load_config(f"{REPO}/config.json")
    {"build": build, "send": send}[sys.argv[1]](config)
```

**Diff 1**, before invocation 2 (`witness_probe2.first.py` → `witness_probe2.second.py`):

```
$ diff witness_probe2.first.py witness_probe2.second.py
44c44
< D_MODEL = "gemini-3.1-pro-preview"
---
> D_MODEL = "gemini-3.8-flash"    # first run: gemini-3.1-pro-preview, refused (daily quota) at seed 1
48c48
< MAX_REQUESTS = 16
---
> MAX_REQUESTS = 17    # 16 in the brief; +1 allowed by the user after the Pro refusal
152c152
<                 sys.exit("stopped: 16 requests reached")
---
>                 sys.exit(f"stopped: {MAX_REQUESTS} requests reached")
166a167,170
>                 cause = e.__context__
>                 if cause is not None:
>                     print(f"  cause: {getattr(cause, 'code', None)} {getattr(cause, 'status', None)}: "
>                           f"{getattr(cause, 'details', cause)}")
```

**Diff 2**, before invocation 3 (`witness_probe2.second.py` → `witness_probe2.py`):

```
$ diff witness_probe2.second.py witness_probe2.py
48c48,51
< MAX_REQUESTS = 17    # 16 in the brief; +1 allowed by the user after the Pro refusal
---
> MAX_REQUESTS = 30    # 16 in the brief; 17 after the Pro refusal; 30 (hard ceiling) after the 503
> RETRY_503_WAIT = 60.0   # user rule after the 503: 503 only, wait 60 s, at most 3 retries per seed
> RETRY_503_MAX = 3
> FAILURES = os.path.join(OUT, "failures.log")   # every failed attempt
151,171c154,197
<             if sent_so_far() >= MAX_REQUESTS:
<                 sys.exit(f"stopped: {MAX_REQUESTS} requests reached")
<             # Everything but model is the runs' config; retries off so one call is one request.
<             cfg = dict(config, model=model, max_retries=0)
<             rec = Recorder(real)
<             client = GeminiClient(cfg, seed, api=rec)
<             gemini.RESPONSE_SCHEMA = schema          # read by generate() at call time
<             if sent_here:
<                 time.sleep(gap)
<             sent_here += 1
<             with open(LEDGER, "a", encoding="utf-8") as f:
<                 f.write(f"{name} seed {seed} {model}\n")
<             try:
<                 text = client.generate(system, b)
<             except Exception as e:  # noqa: BLE001 - report and stop; nothing else is sent
<                 print(f"{name} seed {seed}: request {sent_so_far()} failed: {type(e).__name__}: {e}")
<                 cause = e.__context__
<                 if cause is not None:
<                     print(f"  cause: {getattr(cause, 'code', None)} {getattr(cause, 'status', None)}: "
<                           f"{getattr(cause, 'details', cause)}")
<                 sys.exit(3)
---
>             # attempts already made for this seed with this model (earlier invocations included)
>             with open(LEDGER, encoding="utf-8") if os.path.exists(LEDGER) else open(os.devnull) as f:
>                 tried = sum(1 for line in f if line.strip() == f"{name} seed {seed} {model}")
>             text = None
>             while text is None:
>                 if sent_so_far() >= MAX_REQUESTS:
>                     print(f"stopped: {MAX_REQUESTS} requests reached")
>                     print(f"requests sent by this invocation: {sent_here}; in all: {sent_so_far()}")
>                     sys.exit(4)
>                 # Everything but model is the runs' config; the client's own retries are off, so
>                 # one call is one request.
>                 cfg = dict(config, model=model, max_retries=0)
>                 rec = Recorder(real)
>                 client = GeminiClient(cfg, seed, api=rec)
>                 gemini.RESPONSE_SCHEMA = schema          # read by generate() at call time
>                 if tried:
>                     time.sleep(RETRY_503_WAIT)
>                 elif sent_here:
>                     time.sleep(gap)
>                 sent_here += 1
>                 tried += 1
>                 with open(LEDGER, "a", encoding="utf-8") as f:
>                     f.write(f"{name} seed {seed} {model}\n")
>                 try:
>                     text = client.generate(system, b)
>                 except Exception as e:  # noqa: BLE001
>                     cause = e.__context__
>                     code = getattr(cause, "code", None)
>                     line = (f"{name} seed {seed}: request {sent_so_far()} (attempt {tried}) failed: "
>                             f"{type(e).__name__}: {e} | cause: {code} {getattr(cause, 'status', None)}: "
>                             f"{getattr(cause, 'details', cause)}")
>                     print(line)
>                     with open(FAILURES, "a", encoding="utf-8") as f:
>                         f.write(line + "\n")
>                     if code == 503 and tried <= RETRY_503_MAX:
>                         print(f"  503: retry {tried}/{RETRY_503_MAX} after {RETRY_503_WAIT:.0f}s")
>                         continue
>                     if code == 503:
>                         print(f"  503: {RETRY_503_MAX} retries used; seed {seed} left unanswered")
>                         break
>                     print(f"requests sent by this invocation: {sent_here}; in all: {sent_so_far()}")
>                     sys.exit(3)
>             if text is None:
>                 continue
```

**The screening script** (`<scratchpad>/probe2/screen.py`):

```python
"""P1 screen (witness_design.md §5, pattern in step 2) over C and D; key order check for C."""
import collections
import json
import os
import re

OUT = os.path.dirname(os.path.abspath(__file__))
P = re.compile(r"\b(night|nights|woke|wake|waking|awake|asleep|sleep|slept|sleeping|dark|noise|noises|"
               r"sound|sounds|opened|opening|heard someone|i heard|you heard)\b", re.I)
counts = collections.defaultdict(collections.Counter)
for name in ("C", "D"):
    for s in range(1, 9):
        path = os.path.join(OUT, f"{name}-seed{s}.json")
        if not os.path.exists(path):
            print(f"{name}{s}: no response saved")
            continue
        r = json.load(open(path, encoding="utf-8"))
        pairs = json.loads(r["raw"], object_pairs_hook=lambda p: p)
        keys = [k for k, _ in pairs]
        v = dict(pairs)
        fields = ("option", "say", "reason") + (("thought",) if name == "C" else ())
        hits = {f: P.findall(v.get(f) or "") for f in fields}
        flag = "" if name != "C" or keys[0] == "thought" else "  FLAG: thought is not the first key"
        counts[name][v["option"]] += 1
        print(f"{name}{s}: option={v['option']} suspects={v['suspects']} angry_at={v['angry_at']} "
              f"thoughts_tokens={r['thoughts_tokens']} finish={r['finish_reason']} "
              f"hits={ {k: x for k, x in hits.items() if x} }{flag}")
        if name == "C":
            print(f"    keys={keys}")
print({k: dict(c) for k, c in counts.items()})
```

## 9. State after the probe

```
$ git -C ../.. status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
$ git log --oneline -2
6e81510 LLM morning: witness probe report (heard line in backstory vs "About the can")
fa54a48 LLM morning: witness runs for v6 (daniel_ate_it_leo_heard, seeds 1-3)
```

This was the status after the probe, before this report was written. The report is now the only
other untracked file. Nothing in the repository was modified.
