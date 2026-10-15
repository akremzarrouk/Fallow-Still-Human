# Model probe 2: gemma-4-31b-it, gemini-3.5-flash, gemini-3.7-flash on the play session's 17 prompts

Run 2026-10-15 (UTC 15:58 to 17:03), MODE run. Script: `model_probe2.py` (new; reuses `model_probe.py` for the prompts and the request settings; no production code or prompt changed, nothing more sent to gemini-3.8-flash). Same 17 prompts, same settings and seed as `reports/model_probe_play.md`, once each.
Raw answers: `runs/model_probe/<model>/NN.json`; refused asks `NN.refused2.json`; every request of this run one line in `runs/model_probe/requests2.jsonl`; the run's stdout in `runs/model_probe/run2.log`.

## Result

| model | answers of 17 | what stopped it | requests used |
|---|---|---|---|
| gemma-4-31b-it | **0** | ask 1: `500 INTERNAL` four times (the first try and 3 retries, 60 s apart) | 4 |
| gemini-3.5-flash | **9** | ask 10: `429 RESOURCE_EXHAUSTED`, free-tier requests per day, limit 20 (message below) | 21 (9 answers, 11 `503`, 1 `429`) |
| gemini-3.7-flash | **0** | ask 1: `503`, then a call with no answer for 42 minutes, then `504 DEADLINE_EXCEEDED`, then `ReadTimeout`; four attempts | 4 |
| gemini-3.8-flash | 17 (from `reports/model_probe_play.md`; nothing sent now) | - | 0 |
| **all (this run)** | | | **29 of 80** |

No model but gemini-3.8-flash reached 17 answers.

## Seconds per answer

| model | median | range | how |
|---|---|---|---|
| gemini-3.8-flash | **8.5 s** | 4 to 33 s (16 answers) | estimated: `requests.jsonl` stores only start times, so each answer's time is the next request's start minus the 7 s pause the script makes between requests (`model_probe.py` `GAP`), for the 16 answers followed by another request (not ask 17); includes about a second of script overhead |
| gemini-3.5-flash | **9.9 s** | 5.1 to 10.9 s (9 answers) | measured around the call (`requests2.jsonl` `seconds`) |
| gemma-4-31b-it | no answer | its four `500`s came back in 1.0 to 1.6 s | measured |
| gemini-3.7-flash | no answer | the `503` in 2.9 s; one call with no reply in 42 min (stopped by PID); `504` after 119.9 s and `ReadTimeout` after 120.5 s (the 120 s limit was set after the hang) | measured |

Thinking tokens per answer (`thought_tokens`): gemini-3.8-flash median 636 (239 to 1,623), gemini-3.5-flash median 678 (515 to 1,204). Answer tokens: 3.8-flash 59 to 97, 3.5-flash 46 to 81. All 9 answers of 3.5-flash and all 17 of 3.8-flash finished `STOP` as valid JSON with an option of the list.

## Daily limit: the message

gemini-3.5-flash, ask 10, attempt 4, 2026-10-15T16:15:48Z (`runs/model_probe/gemini-3.5-flash/10.refused2.json`), verbatim:

```
{'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.6-flash\nPlease retry in 7h44m10.324992325s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.6-flash'}, 'quotaValue': '20'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '27850s'}]}}
```

Read from it, without interpretation: the quota is `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, value 20, and the model it names is `gemini-3.6-flash`, not the `gemini-3.5-flash` that was called. 16:15:48 plus the retry delay of 7 h 44 min 10 s is 00:00:00 UTC on 2026-10-16. `reports/model_probe.md:27` met a 429 on the 21st request of a day to gemini-3.8-flash. Requests sent to gemini-3.5-flash since 00:00 UTC on 2026-10-15, counted from the two logs: 4 in `reports/model_probe_play.md`'s run (1 probe answered, 3 `503`) and 21 here, so 24 before the `429` and 25 with it; that does not equal 20, so which requests the quota counts is not settled by this run. gemini-3.7-flash gave no limit message.

## Requests used

| model | probe (earlier report) | asks sent | answers | refused | note |
|---|---|---|---|---|---|
| gemma-4-31b-it | 1 (500) | 4 | 0 | 4 `500` | stopped by the rule: a prompt refused 4 times stops its model |
| gemini-3.5-flash | 1 (answered) | 21 | 9 | 11 `503`, 1 `429` | `503`s on asks 1, 2 (three times), 3, 6, 8, 9, 10 (three times); each of asks 1 to 9 was answered within 3 retries |
| gemini-3.7-flash | 0 | 4 | 0 | 1 `503`, 1 hung, 1 `504`, 1 `ReadTimeout` | all four on ask 1 |
| gemini-3.8-flash | - | 0 | - | - | not asked |

The first process (PIDs 15384 and 8540) was stopped by those two IDs at 16:59 UTC, 42 minutes after its second request to gemini-3.7-flash (2026-10-15T16:16:49Z) got no reply (an open connection to Google, no timeout in the script). That request is line 27 of `requests2.jsonl`, written by hand. The script then got an `http_options` timeout of 120 s and `--prior N` (attempts already made on the first unanswered prompt, so the 4-attempt rule held across the restart), and `504` and timeouts were treated like `503`: wait 60 s, retry. The 504 rule was added mid-run, before the fourth attempt. No answered prompt was asked twice.

## Every error and limit message, verbatim

- gemma-4-31b-it, ask 1, at 15:58:25, 15:59:26, 16:00:27 and 16:01:28 UTC (`runs/model_probe/gemma-4-31b-it/01.refused2.json`):
  `{'error': {'code': 500, 'message': 'Internal error encountered.', 'status': 'INTERNAL'}}`
- gemini-3.5-flash, 11 times (asks 1, 2, 2, 2, 3, 6, 8, 9, 10, 10, 10):
  `{'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}`
  (the text was saved for the three on ask 10, `10.refused2.json`; the other eight are in `requests2.jsonl` as `503 UNAVAILABLE` only.)
- gemini-3.5-flash, once: the `429` above.
- gemini-3.7-flash, ask 1: `503 UNAVAILABLE` at 16:15:48 (the process was stopped before it saved the text; `requests2.jsonl` and `run2.log` hold code and status only); then no reply for 42 minutes (line 27 of `requests2.jsonl`, by hand); then, at 17:00:11 after 119.9 s: `504 DEADLINE_EXCEEDED: Deadline expired before operation could complete.` (`run2.log`); then, at 17:02:25 after 120.5 s: `ReadTimeout: The read operation timed out` (`runs/model_probe/gemini-3.7-flash/01.refused2.json`).

## Side-by-side

Bold is the option id; "(no answer)" is a prompt the model did not answer. The flash-lite and gemini-3.8-flash columns are those of `reports/model_probe_play.md`.

| # | who | min | situation | flash-lite (the session) | gemini-3.8-flash | gemini-3.5-flash | gemma-4-31b-it | gemini-3.7-flash |
|---|---|---|---|---|---|---|---|---|
| 1 | Elena | 00 | Opening: first to act, nobody has spoken; Daniel, Leo, Mara at the pantry; 2 portions | **ask_who**: One can is missing from the shelf. Did one of you take it? | **reassure_all**: It is alright. We will manage this together, we just need to keep our heads. | **reassure_all**: We will figure this out together, so let us all stay calm. | (no answer) | (no answer) |
| 2 | Mara | 00 | Elena has just asked everyone who took the can | **deny**: I didn't take it, Mom! Why would I do that? | **deny**: I didn't take it, Mom. I swear I didn't touch it. | **deny**: I didn't take it, Mom. I swear. | (no answer) | (no answer) |
| 3 | Daniel | 00 | Elena asked who took it; Mara has just denied it | **deny**: I didn't take any can. Nobody here would do that. | **deny**: It wasn't me, Mom. | **deny**: I didn't take anything, Mom. Let's keep our heads and figure this out together. | (no answer) | (no answer) |
| 4 | Elena | 03 | Everyone has denied it or spoken; she is the first to act again | **reassure_all**: Nobody is accusing anyone, we just need to keep our heads and figure this out together. | **reassure_all**: It is alright. We are going to stay together and figure this out without turning on each other. | **reassure_all**: I believe you all. We need to stay calm and figure this out together. | (no answer) | (no answer) |
| 5 | Mara | 03 | Elena has just said nobody is accusing anyone; Mara has denied once | **ask_who**: If none of us took it, then who actually did? | **search**: Maybe it just fell behind something, let me look. | **reassure_all**: Mom is right, we just need to stay calm and work together. | (no answer) | (no answer) |
| 6 | Daniel | 03 | Elena reassured everyone, Leo stayed silent, Mara asked who took it; he denied once | **deny**: I told you, I didn't take it, and we shouldn't be pointing fingers at each other like this. | **reassure_all**: Mom's right, let's keep calm. I'll make sure we get through this with what we have. | **reassure_all**: We just need to keep calm and focus on staying safe. I'll take care of us. | (no answer) | (no answer) |
| 7 | Mara | 06 | Daniel stayed silent; she has asked who took it once | **ask_who**: Someone has to know where it went, we can't just pretend it didn't vanish. | **say_other**: Then where did it go? It couldn't have just disappeared on its own. | **silent**: (none) | (no answer) | (no answer) |
| 8 | Elena | 06 | Mara has just said someone must know where it went; Daniel silent | **reassure_all**: We will figure this out together, nobody needs to worry. | **reassure_mara**: We are not ignoring it, Mara, but getting frantic will only tear us apart. We will manage this together. | **reassure_all**: We need to stay calm and trust each other, Mara. | (no answer) | (no answer) |
| 9 | Mara | 09 | She has asked who took it twice; first to act this turn | **search**: I am going to find out where it went. | **say_to_elena**: Mom, what are we going to do if nobody admits it? There are only two portions left. | **silent**: (none) | (no answer) | (no answer) |
| 10 | Elena | 09 | Mara is searching the kitchen; Leo has just accused her (Elena) of eating it at night | **deny**: I did not take it, Leo. None of us would do that. | **deny**: I didn't take it, Leo. I would never hide food from my children. | (no answer) | (no answer) | (no answer) |
| 11 | Daniel | 09 | Leo has just accused Elena; Elena has just denied it and looks hurt; Mara searching | **accuse_leo**: Leo, you have no right to blame Mom like that when you are the one deflecting. | **say_to_leo**: Shut up, Leo. Don't you dare speak to Mom like that. | (no answer) | (no answer) | (no answer) |
| 12 | Elena | 12 | Leo has just said "Only mom did not deny it"; she has denied once | **deny**: I told you, I did not take the can, and I won't have you accusing me. | **deny**: I did deny it, Leo, and I am telling you again that I did not touch that can. Please stop trying to blame me. | (no answer) | (no answer) | (no answer) |
| 13 | Mara | 12 | Leo said "Only mom did not deny it"; Elena denied it again and looks hurt; Mara had been searching | **ask_who**: Please, someone just tell the truth so we can stop fighting. | **reassure_elena**: Mom, I know you didn't take anything. Leo, stop trying to blame her. | (no answer) | (no answer) | (no answer) |
| 14 | Daniel | 12 | Leo, Elena (hurt) and Mara have just spoken; he accused someone last turn | **confess**: I took it, okay? I ate the can in the night, I'm sorry. | **say_to_leo**: Shut your mouth, Leo, don't you dare try to pin this on Mom. | (no answer) | (no answer) | (no answer) |
| 15 | Elena | 15 | Daniel has just admitted taking it; she is first to act; she had denied twice | **reassure_daniel**: It's alright, Daniel. Thank you for telling the truth. | **reassure_all**: It is alright now, Daniel told the truth. We are still together, and we will get through this. | (no answer) | (no answer) | (no answer) |
| 16 | Daniel | 15 | Elena has just said "Thank you for telling the truth" to him | **reassure_elena**: It's okay Mom, I've got this under control and I'm going to fix it. | **say_to_leo**: Leo, I'm sorry I blamed you. That was on me, and I shouldn't have done it. | (no answer) | (no answer) | (no answer) |
| 17 | Mara | 15 | Elena thanked Daniel, Daniel told Elena he has it under control | **accuse_daniel**: You lied to me before, Daniel, so why should I believe you now? | **say_to_daniel**: You lied right to my face when I asked you earlier, Daniel. How are you going to fix this? | (no answer) | (no answer) | (no answer) |


## What the 9 answers of gemini-3.5-flash show (counts and quotes only)

- Same option id as flash-lite on 4 of the 9 (asks 2, 3, 4, 8); same as gemini-3.8-flash on 5 of the 9 (asks 1, 2, 3, 4, 6).
- `reassure_all` on 5 of the 9 (asks 1, 4, 5, 6, 8): "We will figure this out together, so let us all stay calm" (1), "Mom is right, we just need to stay calm and work together" (5), "We need to stay calm and trust each other, Mara" (8). `silent` on asks 7 and 9 (Mara). `deny` on asks 2 and 3.
- Ask 3 (Daniel, min 0): `suspects` is Daniel (as with gemini-3.8-flash); flash-lite's was `nobody`.
- Asks 10 to 17, where Leo accuses Elena and Daniel confesses, were not answered by this model.

## Commands run

```
$ .venv/Scripts/python.exe model_probe2.py run gemma-4-31b-it gemini-3.5-flash gemini-3.7-flash   (background; run2.log)
  gemma-4-31b-it: 0 of 17 answered; 4 requests used in all
  gemini-3.5-flash: 9 of 17 answered; 25 requests used in all      (the count then included the 4 requests of gemma and the 21 of 3.5-flash)
  gemini-3.7-flash 1 attempt 1: 503 UNAVAILABLE      (then no output for 42 min; stopped by PID 8540 and 15384)
$ .venv/Scripts/python.exe model_probe2.py run gemini-3.7-flash --prior 2
  gemini-3.7-flash 1 attempt 3: 504 DEADLINE_EXCEEDED
  gemini-3.7-flash: 0 of 17 answered; 28 requests used in all
$ .venv/Scripts/python.exe model_probe2.py run gemini-3.7-flash --prior 3
  gemini-3.7-flash 1 attempt 4: None ReadTimeout
  gemini-3.7-flash: 0 of 17 answered; 29 requests used in all
$ .venv/Scripts/python.exe model_probe2.py table gemini-3.8-flash gemini-3.5-flash gemma-4-31b-it gemini-3.7-flash > runs/model_probe/table2.md
```

## Not done

- gemma-4-31b-it: 0 of 17. gemini-3.5-flash: asks 10 to 17 (the daily limit). gemini-3.7-flash: 0 of 17.
- 51 of the 80 requests are unused; by the arithmetic above gemini-3.5-flash's limit resets at 00:00 UTC on 2026-10-16.
- One sample per prompt per model (temperature 1.0).
