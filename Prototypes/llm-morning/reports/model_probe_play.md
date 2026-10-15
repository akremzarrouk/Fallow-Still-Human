# Model probe: do stronger free models answer the play session's 17 prompts differently?

File name: `reports/model_probe.md` already holds the earlier probe of the v12 prompts (commit 973f9d2, left untouched), so this one is `reports/model_probe_play.md`.

Run 2026-10-15, MODE run. Script: `model_probe.py` (new file; no production code or prompt changed, no answer applied to a run).
Raw answers: `runs/model_probe/<model>/NN.json` (NN = the ask's number in the table), refusals as `NN.refused.json`, probes as `probe.json`, every request one line in `runs/model_probe/requests.jsonl`.

## Result in four lines

- **gemini-3.8-flash answered all 17 prompts** (19 requests: 17 answers and 2 refusals, both 503).
- **gemini-3.5-flash answered the minimal probe but none of the 17 prompts**: its 3 requests for ask 1 were refused with 503, and the 40-request cap no longer left room for 17 more (15 remained). It was stopped there.
- **gemma-4-31b-it** did not answer its one minimal request (500 INTERNAL). It was not tried again (scope: one request each).
- 25 of the 40 requests were used.

## The 17 prompts

The session is `runs/play/daniel_ate_it-seed2-20261014T225035Z` (started 2026-10-14T22:50:37Z, `session.log:1`; 17 live asks, 0 cached, `session.log:2`). Its prompts are the last 17 entries of `cache/play/gemini-3.5-flash-lite-daniel_ate_it-seed2.json`, in stored order. All 48 entries of that file hash (model, seed 2, `SYSTEM` of `world.py:42`, prompt) to their keys, so the prompts are byte for byte what was sent. Each was sent as `contents` with `system_instruction=SYSTEM`, `temperature=1.0`, `seed=2`, `response_mime_type=application/json`, `response_schema=RESPONSE_SCHEMA`, `max_output_tokens=2048`, automatic function calling off: the settings of `gemini.py:103-111`.

## Which models, and why those three

`list_models.py` lists these non-lite Flash models and these Gemma models (full output below): gemini-2.5-flash, gemini-3-flash-preview, gemini-3.5-flash, gemini-3.6-flash, gemini-3.7-flash, gemini-3.8-flash, gemma-4-26b-a4b-it, gemma-4-31b-it. Candidates sent a probe (the scope allows 3): **gemini-3.8-flash** (the newest non-lite Flash), **gemini-3.5-flash** (the non-lite model of the family flash-lite is in), **gemma-4-31b-it** (the largest Gemma). Not tried: gemini-3.6-flash, gemini-3.7-flash, gemini-3-flash-preview, gemini-2.5-flash, gemma-4-26b-a4b-it, and the Pro models.

## Probes (one minimal request each, no retry)

The minimal request carries the same system instruction, schema and settings, with the prompt `Options:\n- stay: (speech) You say nothing and stay.\nChoose "stay" and say "Hello".`

| model | answer | prompt / answer / thinking tokens |
|---|---|---|
| gemini-3.8-flash | answered: `{"option":"stay","say":"Hello.",...}` | 265 / 38 / 154 |
| gemini-3.5-flash | answered: `{"option":"stay","say":"Hello",...}` | 265 / 38 / 275 |
| gemma-4-31b-it | refused, 500 INTERNAL | - |

Limit/refusal message, verbatim (`runs/model_probe/gemma-4-31b-it/probe.json`):
`{'error': {'code': 500, 'message': 'Internal error encountered.', 'status': 'INTERNAL'}}`

## Requests used

| model | probe | asks sent | answers | refused asks | total |
|---|---|---|---|---|---|
| gemini-3.8-flash | 1 | 19 | 17 | 2 (503) | 20 |
| gemini-3.5-flash | 1 | 3 | 0 | 3 (503) | 4 |
| gemma-4-31b-it | 1 (refused, 500) | 0 | 0 | 0 | 1 |
| **all** | 3 | 22 | 17 | 5 | **25 of 40** |

No request was a repeat of an answered prompt. The refused asks were sent again after a pause (ask 1 and ask 10 of 3.8-flash, which then answered; ask 1 of 3.5-flash three times, always refused).

Refusals, verbatim, all the same (`runs/model_probe/gemini-3.8-flash/01.refused.json`, `10.refused.json`, `runs/model_probe/gemini-3.5-flash/01.refused.json`):
`{'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}`

Times (UTC, `requests.jsonl`): 3.8-flash ask 1 refused 00:05:28, answered 00:07:01; ask 10 refused 00:09:58, answered 00:11:37. 3.5-flash ask 1 refused 00:14:30, 00:16:41, 00:21:25. No daily-quota (`PerDay`) or 429 message came from any model. The earlier probe (`reports/model_probe.md:27`) met a 429 on its 21st request to gemini-3.8-flash in a day; this run sent 20 to it (1 probe, 19 asks) and met none. The 3.5-flash run stopped at 25 used requests because 15 remained and the 17 prompts need 17; it was not tried a fourth time.

## Side-by-side

Bold is the option id. "Flash-lite" is what the session got (from the cache, `v['response']`); 3.8-flash is `runs/model_probe/gemini-3.8-flash/NN.json`. Gemini-3.5-flash has no column: it answered none of the 17.

| # | who | min | situation | flash-lite (the session) | gemini-3.8-flash |
|---|---|---|---|---|---|
| 1 | Elena | 00 | Opening: first to act, nobody has spoken; Daniel, Leo, Mara at the pantry; 2 portions | **ask_who**: One can is missing from the shelf. Did one of you take it? | **reassure_all**: It is alright. We will manage this together, we just need to keep our heads. |
| 2 | Mara | 00 | Elena has just asked everyone who took the can | **deny**: I didn't take it, Mom! Why would I do that? | **deny**: I didn't take it, Mom. I swear I didn't touch it. |
| 3 | Daniel | 00 | Elena asked who took it; Mara has just denied it | **deny**: I didn't take any can. Nobody here would do that. | **deny**: It wasn't me, Mom. |
| 4 | Elena | 03 | Everyone has denied it or spoken; she is the first to act again | **reassure_all**: Nobody is accusing anyone, we just need to keep our heads and figure this out together. | **reassure_all**: It is alright. We are going to stay together and figure this out without turning on each other. |
| 5 | Mara | 03 | Elena has just said nobody is accusing anyone; Mara has denied once | **ask_who**: If none of us took it, then who actually did? | **search**: Maybe it just fell behind something, let me look. |
| 6 | Daniel | 03 | Elena reassured everyone, Leo stayed silent, Mara asked who took it; he denied once | **deny**: I told you, I didn't take it, and we shouldn't be pointing fingers at each other like this. | **reassure_all**: Mom's right, let's keep calm. I'll make sure we get through this with what we have. |
| 7 | Mara | 06 | Daniel stayed silent; she has asked who took it once | **ask_who**: Someone has to know where it went, we can't just pretend it didn't vanish. | **say_other**: Then where did it go? It couldn't have just disappeared on its own. |
| 8 | Elena | 06 | Mara has just said someone must know where it went; Daniel silent | **reassure_all**: We will figure this out together, nobody needs to worry. | **reassure_mara**: We are not ignoring it, Mara, but getting frantic will only tear us apart. We will manage this together. |
| 9 | Mara | 09 | She has asked who took it twice; first to act this turn | **search**: I am going to find out where it went. | **say_to_elena**: Mom, what are we going to do if nobody admits it? There are only two portions left. |
| 10 | Elena | 09 | Mara is searching the kitchen; Leo has just accused her (Elena) of eating it at night | **deny**: I did not take it, Leo. None of us would do that. | **deny**: I didn't take it, Leo. I would never hide food from my children. |
| 11 | Daniel | 09 | Leo has just accused Elena; Elena has just denied it and looks hurt; Mara searching | **accuse_leo**: Leo, you have no right to blame Mom like that when you are the one deflecting. | **say_to_leo**: Shut up, Leo. Don't you dare speak to Mom like that. |
| 12 | Elena | 12 | Leo has just said "Only mom did not deny it"; she has denied once | **deny**: I told you, I did not take the can, and I won't have you accusing me. | **deny**: I did deny it, Leo, and I am telling you again that I did not touch that can. Please stop trying to blame me. |
| 13 | Mara | 12 | Leo accused Elena again; Elena denied it, looks hurt; Mara had been searching | **ask_who**: Please, someone just tell the truth so we can stop fighting. | **reassure_elena**: Mom, I know you didn't take anything. Leo, stop trying to blame her. |
| 14 | Daniel | 12 | Leo, Elena (hurt) and Mara have just spoken; he accused someone last turn | **confess**: I took it, okay? I ate the can in the night, I'm sorry. | **say_to_leo**: Shut your mouth, Leo, don't you dare try to pin this on Mom. |
| 15 | Elena | 15 | Daniel has admitted taking it; she is the first to act; she has denied twice | **reassure_daniel**: It's alright, Daniel. Thank you for telling the truth. | **reassure_all**: It is alright now, Daniel told the truth. We are still together, and we will get through this. |
| 16 | Daniel | 15 | Elena has just said "Thank you for telling the truth" to him | **reassure_elena**: It's okay Mom, I've got this under control and I'm going to fix it. | **say_to_leo**: Leo, I'm sorry I blamed you. That was on me, and I shouldn't have done it. |
| 17 | Mara | 15 | Elena thanked Daniel, Daniel told Elena he has it under control | **accuse_daniel**: You lied to me before, Daniel, so why should I believe you now? | **say_to_daniel**: You lied right to my face when I asked you earlier, Daniel. How are you going to fix this? |

## What the table shows (counts and quotes only)

- Same option id as flash-lite on 5 of the 17 asks (2 `deny`, 3 `deny`, 4 `reassure_all`, 10 `deny`, 12 `deny`); the words differ in all 5.
- Every one of the 17 answers finished `STOP`, was valid JSON, and chose an option in its list. Thinking used 239 to 1,623 tokens; answers 59 to 97.
- Elena, the three asks after Leo accuses her (10, 12, 15):
  - Ask 10 (min 09, accused): both models `deny`, addressed to Leo.
  - Ask 12 (min 12, "Only mom did not deny it"): both models `deny`, 3.8-flash's words open "I did deny it, Leo".
  - Ask 15 (min 15, after Daniel confessed): flash-lite `reassure_daniel`: "Thank you for telling the truth." 3.8-flash `reassure_all`: "Daniel told the truth. We are still together". Neither mentions Leo's accusation. The ask's option list holds `say_to_leo`, `sit_leo` and `aside_leo` (no `accuse_leo`, no `reassure_leo`); neither model chose one. 3.8-flash's `angry_at` for her is Leo and `suspects` Daniel (`runs/model_probe/gemini-3.8-flash/15.json`); flash-lite's is `nobody`.
- Elena's opening (ask 1): flash-lite `ask_who`; 3.8-flash `reassure_all` ("we just need to keep our heads") with nobody having spoken.
- Daniel after his own confession (ask 16): flash-lite `reassure_elena` ("I've got this under control"); 3.8-flash `say_to_leo`: "Leo, I'm sorry I blamed you."
- Daniel at min 12 (ask 14): flash-lite `confess`; 3.8-flash `say_to_leo`: "Shut your mouth, Leo, don't you dare try to pin this on Mom." (no confession; `suspects` Daniel, `angry_at` Leo).
- Mara at min 12 (ask 13, Leo has accused Elena and Elena has denied it): flash-lite `ask_who`; 3.8-flash `reassure_elena` and speaks to Leo: "Leo, stop trying to blame her."
- Mara at min 09 (ask 9): flash-lite `search`; 3.8-flash `say_to_elena`: "what are we going to do if nobody admits it?". Mara at min 03 (ask 5): 3.8-flash `search`, flash-lite `ask_who`.
- `feeling` words: flash-lite repeats "deeply anxious"/"very anxious" for Elena and Mara in asks 1, 4, 5, 7, 8, 9; 3.8-flash uses "anxious" there, "stung" (ask 10), "distressed" (ask 13).

## Commands run and their output

```
$ .venv/Scripts/python.exe list_models.py     (no generate call; non-lite Flash and Gemma lines of the output)
models/gemini-2.5-flash                                 Gemini 2.5 Flash
models/gemma-4-26b-a4b-it                               Gemma 4 26B A4B IT
models/gemma-4-31b-it                                   Gemma 4 31B IT
models/gemini-3-flash-preview                           Gemini 3 Flash Preview
models/gemini-3.5-flash                                 Gemini 3.5 Flash
models/gemini-3.6-flash                                 Gemini 3.6 Flash
models/gemini-3.7-flash                                 Gemini 3.7 Flash
models/gemini-3.8-flash                                 Gemini 3.8 Flash
(also listed: gemini-2.5-pro, gemini-3.1-pro-preview, gemini-3.1-flash-lite, gemini-3.5-flash-lite, flash/pro "latest" aliases, image/TTS/music/agent models)

$ .venv/Scripts/python.exe model_probe.py probe gemini-3.8-flash gemini-3.5-flash gemma-4-31b-it
gemini-3.8-flash -> answered
gemini-3.5-flash -> answered
gemma-4-31b-it -> refused 500 INTERNAL

$ .venv/Scripts/python.exe model_probe.py run gemini-3.8-flash --first 1
1 refused 503 UNAVAILABLE
  stopped: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

$ .venv/Scripts/python.exe model_probe.py run gemini-3.8-flash --first 1 --wait 75
1 ok

$ .venv/Scripts/python.exe model_probe.py run gemini-3.8-flash
2 ok ... 9 ok
10 refused 503 UNAVAILABLE
  stopped: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

$ .venv/Scripts/python.exe model_probe.py run gemini-3.8-flash --wait 90
10 ok ... 17 ok

$ .venv/Scripts/python.exe model_probe.py run gemini-3.5-flash
1 refused 503 UNAVAILABLE   (stopped, same message)
$ .venv/Scripts/python.exe model_probe.py run gemini-3.5-flash --wait 120
1 refused 503 UNAVAILABLE   (stopped, same message)
$ .venv/Scripts/python.exe model_probe.py run gemini-3.5-flash --wait 270
1 refused 503 UNAVAILABLE   (stopped, same message)

$ wc -l runs/model_probe/requests.jsonl
25 runs/model_probe/requests.jsonl

$ .venv/Scripts/python.exe model_probe.py table gemini-3.8-flash > runs/model_probe/table.md
```

## Not done

- gemini-3.5-flash: 0 of 17 answered (503 on ask 1, three times). 15 requests of the cap of 40 are unused; they cannot cover 17 prompts.
- gemma-4-31b-it: 0 of 17 (probe refused 500; not retried).
- Single seed, single answer per prompt per model (temperature 1.0): one sample of each model's choice, not a rate.
