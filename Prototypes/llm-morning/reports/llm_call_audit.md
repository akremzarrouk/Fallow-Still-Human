# LLM call audit: where the Gemini requests go

Prototypes/llm-morning, audited 2026-09-26. Read-only: nothing was run and no API call was made.
Sources are the code, `config.json`, `runs/**` (stdout, meta, transcripts), `cache/**` and
`REPORT*.md`. All paths are relative to `Prototypes/llm-morning/`.

## 1. Call sites

| # | call site | path:line | trigger | calls per run | retries | cached? | batched? |
|---|---|---|---|---|---|---|---|
| A | `GeminiClient.generate` → `self._client.models.generate_content(...)`. This is **the only request a morning sends**. It is reached only through `Oracle.ask` (gemini.py:245), which is reached only through `Morning.ask_model` (world.py:739). | gemini.py:111 | via A1 or A2 below | sum of A1 + A2 + failed attempts | up to `max_retries`=6 per decision (config.json:6), on 429 without "PerDay" and on any 5xx (gemini.py:120). A 429 with "PerDay" stops at once, with no retry (gemini.py:118-119). Any other error stops at once (gemini.py:121-123). Every attempt counts as a request (gemini.py:109). | yes (see §3) | no (see §4) |
| A1 | `Morning.decide` → `ask_model` | world.py:789 (called from `Morning.turn`, world.py:678) | Every person, every turn: a model call fires when that person has a social trigger (`social_triggers`, world.py:604-612) or an inner moment (a level rose, at most once per 9 min per person: world.py:53, 781-787). Otherwise the rules decide (`routine`, world.py:793). At minute 00 all four people get the opening trigger (world.py:267). | from code: 0 to 120. From logs (current code, Flash Lite): 37 to 93 answers. See §5. | as A. An unusable answer is **not** re-asked; the rules fall back (world.py:790-791). | yes | no |
| A2 | `Morning.decide_aside` → `ask_model` | world.py:809 (called from `Morning.turn`, world.py:685) | Someone chose an `aside_*` option. The person taken aside is always asked, and this replaces their decision for the turn (world.py:683). | from code: 0 to 120, within the same 120 as A1. From logs: **0 in every saved run** (no `accept_aside`/`refuse_aside` prompt in any cache). | as A | yes | no |
| B | `probe_model.py` `main` → `client.models.generate_content` | probe_model.py:32 | Run by hand, outside a morning. Sends Daniel's minute-00 prompt once. | not part of a run. Logged: 1 + 4 = 5 requests (runs/probe-gemma-1.stdout.txt, runs/probe-gemma-2.stdout.txt) | none | no (the answer is not stored) | no |
| C | `probe_prompt.py` `main` → `client.models.generate_content` | probe_prompt.py:44 | Run by hand. Replays a cache with no requests up to the first unanswered prompt, then sends that prompt once. | not part of a run. Logged: 3 requests (runs/v5/probe-gemma-seed2.stdout.txt) | none | reads the cache; does not write the answer | no |
| D | `list_models.py` `main` → `client.models.list()` | list_models.py:17 | Run by hand. This is not a `generate_content` request. | not part of a run. Logged: 2 invocations (runs/list_models.stdout.txt, runs/v5/gemma-models.stdout.txt). Page requests per invocation: NOT FOUND | none | no | n/a |
| E | Archived copies (runnable, each with its own `morning.py`) | v1/gemini.py:109 via v1/world.py:279 (`Morning.turn`, one call per person with a trigger); v2/gemini.py:109 via v2/world.py:476 (`decide`); v3/gemini.py:111 via v3/world.py:661 (`ask_model` ← `decide` :691, `decide_aside` :711); v4/gemini.py:111 via v4/world.py:735 (`ask_model` ← `decide` :785, `decide_aside` :805) | same shape as A. v1 asks every person who has a trigger each turn, with no inner moments. | logs in §5.3 | same loop (v1/v2 :103-129, v3/v4 :105-131) | yes (cache/, cache/v2..v4) | no |
| — | `test_morning.py` | test_morning.py:103-115, :845 | Tests use `StubApi` or `FakeClient`. Every `quiet_run` in the tests passes `client=` or `fake=True` (test_morning.py:812, 878, 886, 893). | 0 real requests | — | — | — |

`gemini.py:69` builds the `genai.Client`. The request is sent at `:111`.

## 2. How often A fires, from code

- **Turns:** `morning.py:65` loops `morning.turns` = 90 / 3 = **30 turns** (data.py:76-77).
- **People:** `world.py:668` loops rooms and `world.py:673` loops the people present, so each of the 4 people (data.py:14) decides **exactly once per turn**. An aside reply takes the target's place (world.py:683). That gives **at most 4 model decisions per turn and 120 per run.**
- **Per decision:** one `Oracle.ask`. It sends 0 requests if the answer is cached. Otherwise it sends 1 request, plus up to 6 retries. The backoff is 5·2ⁿ s, capped at 120 s, and at least the server's `retryDelay` + 1 (gemini.py:127-130, config.json:7-8).
- **Who is asked each turn:** while a room's conversation is active and at least 2 people are in it (`talking`, world.py:283-286), every trigger counts, old ones included (world.py:607). So everyone present is asked. A conversation ends after `QUIET_TURNS` = 2 turns with nothing new (world.py:52), or when fewer than 2 people are left.
- **Caps:**
  - `Oracle` refuses a new prompt once cached answers + this process's requests reach 150 (`max_calls_per_morning`, gemini.py:242). Retries count toward that number.
  - `GeminiClient` stops at 150 requests per process, retries included (gemini.py:106).
  - Requests sent by an earlier process that stopped are not counted by a resumed one.
- **Spacing** (throughput, not count): 4.5 s between calls (config.json:4); 6.5 s for `--model gemma` (config.json:13).

## 3. Caching, memoization, record/replay

- **Disk cache, per morning:** `Cache` (gemini.py:185-209).
  - Key = sha256(model, seed, system, prompt) (gemini.py:196-198).
  - Checked before any request (gemini.py:231-238). Written after every live answer (gemini.py:250), including answers that later fail to parse.
  - File: `cache/<out>/<model>-<scenario>[-<modelkey>]-seed<N>.json` (morning.py:43-47).
- **Replay:** `--replay` gives the Oracle no client and raises `CacheMiss` on a miss instead of calling (gemini.py:239-241, morning.py:49-52). Logged replays sent 0 requests: runs/v4/earlier.stdout.txt, runs/v5/v4-replay.stdout.txt, runs/cmp.stdout.txt.
- **Resume:** a fresh run with a partly filled cache sends only the unanswered prompts (morning.py:77). The resumed logs show "0 API requests" through the cached turns.
- **Other memoization:** NOT FOUND. API-side context caching (`cached_content`): NOT FOUND. The 913-character system instruction (world.py:27) goes with every request.

## 4. Batching

None. Each `generate_content` call carries one person's prompt as `contents` (gemini.py:111-112). The response schema is one object with one `option` (gemini.py:47-58). There are no multi-decision requests and no Batch API use (grep in §8).

## 5. Requests per run, from logs

Sources:
- `runs/**/*.meta.json` records `api_requests` for the **last process only**.
- `runs/**/*.stdout.txt` covers every process. Each `[code STATUS] waiting…` line is one failed request that was retried.
- Transcripts give the split by caller and trigger: acts with `mode` ≠ routine; aside = option `accept_aside`/`refuse_aside`; inner = `inner` set.
- Caches give the sizes.

### 5.1 Current code (runs/v5), by call site

| run | model | A1 decide, social trigger | A1 decide, inner moment | A2 decide_aside | answers | failed requests | extra | **total requests, all processes** | meta `api_requests` | processes |
|---|---|---|---|---|---|---|---|---|---|---|
| mara_ate_it seed1 | flash-lite | 41 | 5 | 0 | 46 | 0 | 0 | **46** | 46 | 1 |
| mara_ate_it seed2 | flash-lite | 29 | 8 | 0 | 37 | 0 | 0 | **37** | 37 | 1 |
| mara_ate_it seed3 | flash-lite | 26 | 11 | 0 | 37 | 0 | 0 | **37** | 37 | 1 |
| miscount seed1 | flash-lite | 48 | 8 | 0 | 56 | 0 | 0 | **56** | 56 | 1 |
| miscount seed2 | flash-lite | 84 | 9 | 0 | 93 | 0 | 1 answer lost ¹ | **94** | 84 | 2 |
| miscount seed3 | flash-lite | 59 | 11 | 0 | 70 | 0 | 0 | **70** | 70 | 1 |
| **Flash Lite, 6 runs** | | **287** | **52** | **0** | 339 | 0 | 1 | **340** | | |
| daniel_ate_it gemma seed1 | gemma-4-31b-it | 13 | 8 | 0 | 21 | 24 | 0 | **45** | 45 | 1 |
| daniel_ate_it gemma seed2 | gemma-4-31b-it | 6 | 7 | 0 | 13 | 33 + 3 ² | 0 | **49** | 4 | 4 |
| daniel_ate_it gemma seed3 | gemma-4-31b-it | 13 | 7 | 0 | 20 | 16 | 0 | **36** | 36 | 1 |
| daniel_ate_it gemma seed4 | gemma-4-31b-it | 12 | 7 | 0 | 19 | 22 | 0 | **41** | 41 | 1 |
| daniel_ate_it gemma seed5 | gemma-4-31b-it | 7 | 7 | 0 | 14 | 31 | 0 | **45** | 45 | 1 |
| **Gemma, 5 runs** | | **51** | **36** | **0** | 87 | 129 | 0 | **216** | | |

**Per-run totals:**
- Flash Lite: 340 / 6 = 56.7 requests per run (range 37–94). This matches REPORT-5.md:973 ("340 requests for its six runs").
- Gemma: 216 / 5 = 43.2 requests per run (range 36–49). REPORT-5.md:138 and :974 say **213**; the gap of 3 is note ².

Notes:
- ¹ **miscount seed2.** The first process sent 10 requests. 9 answers were cached. The 10th was answered, but the cache write crashed (PermissionError at gemini.py:209, runs/v5/miscount-seed2.stdout.txt:4-25). That 10th decision was Elena at minute 06, a social trigger (10th model act in the transcript). The resumed process sent that prompt again: 9 cached + 84 live. Split by call site, that makes A1 social 85 requests (84 + 1 re-sent) and inner 9.
- ² **gemma seed2.** It took four processes: 31 requests (11 answers + 13 retried + 7 on the prompt that stopped it), then 7, then 7, then 4. The 33 retry lines count only attempts 1-6 of each prompt. A prompt that exhausts its retries also sends a 7th attempt that prints no line: `requests += 1` at gemini.py:109, then it raises at :124-126. There are 3 such stops (stdout lines 29, 49, 69), so 3 requests that no retry line shows. 87 + 126 retry lines + 3 = 216. REPORT-5 counts 87 + 126 = 213.
- The failed requests are 81 × 500 INTERNAL and 48 × 503 UNAVAILABLE: 80 + 46 retry lines plus the 3 final attempts (503, 500, 503). No Flash Lite run in runs/v5 has a retry line.

### 5.2 Current code, by character and by turn (from transcripts)

| run | Daniel | Elena | Leo | Mara | turns with ≥1 call | turns where all 4 were asked |
|---|---|---|---|---|---|---|
| mara_ate_it s1 | 12 | 11 | 11 | 12 | 14/30 | 10 |
| mara_ate_it s2 | 10 | 8 | 10 | 9 | 14/30 | 6 |
| mara_ate_it s3 | 11 | 8 | 8 | 10 | 14/30 | 5 |
| miscount s1 | 14 | 13 | 15 | 14 | 20/30 | 10 |
| miscount s2 | 24 (+1 re-sent: Elena) | 24 | 24 | 21 | 27/30 | 19 |
| miscount s3 | 19 | 17 | 18 | 16 | 24/30 | 13 |
| Flash Lite sum | 90 | 81 (+1) | 86 | 82 | | |
| gemma s1–s5 sum | 22 | 24 | 21 | 20 | | |

The counts are answers (model decisions). Gemma retries are not attributed to a character in the logs.

### 5.3 Earlier versions (same call-site shape), from meta and stdout

| version | runs (seed: requests) | retries | notes |
|---|---|---|---|
| v1 (runs/, cache/) | s1: 120, s2: 39, s3: 90 | 0 | Aborted attempts, caches only: 10 + 4 + 35 = 49 (cache/aborted/, REPORT.md:51). REPORT.md:24 gives 298 for the day. |
| v2 | s1: 7, s2: 25, s3: 11 | 0 | |
| v3 | s1: 37, s2: 36, s3: 30 | 0 | |
| v4 | s1: 36, s2: 19 + 21 = 40, s3: 39, s4: 29, s5: 41 | 0 | seed2 process 1: 18 answers, then its 19th request got a 429 PerDay (runs/v4/daniel_ate_it-seed2.stdout.txt:7). |

Requests per Pacific-time quota day, as logged:
- **Day 1:** 298 (v1) + 43 (v2) + 103 (v3) + 36 + 19 (v4) = **499**. The quota stop came on the 499th request counted client-side (REPORT-2.md:237, REPORT-3.md:325, runs/v4/quota-note.txt).
- **Day 2:** 130 (v4) + 340 (v5 Flash Lite) = **470** (REPORT-5.md:973). Gemma's 216 run requests + 8 probe requests are reported separately (REPORT-5.md:974).

## 6. Do repeat runs resend identical prompts?

- **Same out dir, model, scenario and seed:** no. Every prompt is found in the cache, so 0 requests (§3).
- **A resumed run:** it re-sends the prompt that failed or whose answer was lost. It is the same prompt text by construction, since the state is rebuilt from the same cached answers. Logged: 1 re-send in miscount s2, and the gemma s2 stopping prompt re-sent across 4 processes.
- **Different seed:** yes, when the text happens to match. The seed is in both the cache file name and the key, so an identical text is sent again. It is also sent with a different API `seed` (gemini.py:98, temperature 1.0). Logged, all of them minute-00 kitchen prompts:

| cache group | prompts | distinct texts | texts in ≥2 seeds (occurrences) |
|---|---|---|---|
| cache/ v1 daniel_ate_it s1-3 | 249 | 241 | 4 (12) |
| cache/v2 daniel_ate_it s1-3 | 43 | 43 | 0 |
| cache/v3 daniel_ate_it s1-3 | 103 | 103 | 0 |
| cache/v4 daniel_ate_it s1-5 | 184 | 181 | 3 (6) |
| cache/v5 flash-lite mara_ate_it s1-3 | 120 | 120 | 0 |
| cache/v5 flash-lite miscount s1-3 | 219 | 219 | 0 |
| cache/v5 gemma daniel_ate_it s1-5 | 87 | 85 | 2 (4) |

- **Different version or model:** each `--out` has its own cache directory (morning.py:43), and the model is in the key. Identical texts shared between groups: v4 ∩ v5 Flash Lite 4, v4 ∩ v5 Gemma 3, v5 Flash Lite ∩ v5 Gemma 2.

## 7. Prompt and response size per call site

- **Prompt tokens:** as counted by the API (`usage_metadata.prompt_token_count`, gemini.py:114), stored per cache entry. They include the system instruction.
- **Response tokens:** NOT logged in runs or caches. The only record is in runs/probe-gemma-2.stdout.txt (86 and 80 answer tokens).
- **Response characters:** taken from the cached text.
- **Limits:** the prompt budget is 1,400 estimated tokens (world.py:51), with trimming at world.py:521-537. `max_output_tokens` is 2048 (config.json:9).
- **A2 (decide_aside):** no prompts were logged, so there are no sizes for it. Every row below is A1.

| cache (current code, A1 only) | entries | prompt tokens min/mean/max | prompt chars mean | response chars min/mean/max |
|---|---|---|---|---|
| v5 flash-lite mara_ate_it s1 | 46 | 1277/1342/1374 | 4055 | 181/260/354 |
| v5 flash-lite mara_ate_it s2 | 37 | 1313/1346/1375 | 4068 | 187/263/360 |
| v5 flash-lite mara_ate_it s3 | 37 | 1282/1350/1388 | 4060 | 177/259/318 |
| v5 flash-lite miscount s1 | 56 | 1277/1339/1374 | 4071 | 184/254/306 |
| v5 flash-lite miscount s2 | 93 | 1298/1341/1381 | 4067 | 182/269/331 |
| v5 flash-lite miscount s3 | 70 | 1304/1338/1383 | 4066 | 180/262/349 |
| v5 gemma s1 / s2 / s3 / s4 / s5 | 21/13/20/19/14 | means 1346/1340/1341/1351/1331; overall 1263–1386 | ≈4040–4070 | means 217/227/213/214/232 |

Earlier versions: v1 mean ≈1,200 tokens (996–1,254). v2–v4 means are 1,273–1,343 tokens (1,173–1,377).

## 8. Search commands and output

Run from `Prototypes/llm-morning/` in Git Bash.

```
$ grep -rn --include='*.py' --exclude-dir=.venv -E 'generate_content|genai\.Client|models\.list|\.generate\(|\.ask\(' .
./gemini.py:69:        self._client = api if api is not None else genai.Client(api_key=key)
./gemini.py:111:                response = self._client.models.generate_content(
./gemini.py:245:        text = self.client.generate(system, prompt)
./list_models.py:15:    client = genai.Client(api_key=key)
./list_models.py:17:    for m in client.models.list():
./probe_model.py:28:    client = genai.Client(api_key=require_api_key())
./probe_model.py:32:        r = client.models.generate_content(model=model, contents=contents,
./probe_prompt.py:16:            return super().ask(system, prompt)
./probe_prompt.py:43:        client = genai.Client(api_key=require_api_key())
./probe_prompt.py:44:        r = client.models.generate_content(model=model, contents=prompt, config=config)
./test_morning.py:103:    """Stands in for genai.Client: .models.generate_content runs through a script."""
./test_morning.py:110:    def generate_content(self, model, contents, config):
./test_morning.py:115:        return FakeResponse(FakeClient(invalid_every=0).generate("", contents))
./test_morning.py:273:        self.assertEqual(oracle.ask("s", "p1"), "earlier answer")
./test_morning.py:275:            oracle.ask("s", "p2")
./test_morning.py:855:        c.generate(SYSTEM, "- silent: stay put")
./test_morning.py:856:        c.generate(SYSTEM, "- silent: stay put")
./test_morning.py:863:        text = c.generate(SYSTEM, "- silent: stay put")
./test_morning.py:872:            c.generate(SYSTEM, "- silent: stay put")
./v1/gemini.py:67:        self._client = api if api is not None else genai.Client(api_key=key)
./v1/gemini.py:109:                response = self._client.models.generate_content(
./v1/gemini.py:236:        text = self.client.generate(system, prompt)
./v1/world.py:279:                text = self.oracle.ask(SYSTEM, prompt)
./v2/gemini.py:67:        self._client = api if api is not None else genai.Client(api_key=key)
./v2/gemini.py:109:                response = self._client.models.generate_content(
./v2/gemini.py:237:        text = self.client.generate(system, prompt)
./v2/world.py:476:            text = self.oracle.ask(SYSTEM, prompt)
./v3/gemini.py:69:        self._client = api if api is not None else genai.Client(api_key=key)
./v3/gemini.py:111:                response = self._client.models.generate_content(
./v3/gemini.py:245:        text = self.client.generate(system, prompt)
./v3/world.py:661:        text = self.oracle.ask(SYSTEM, prompt)
./v4/gemini.py:69:        self._client = api if api is not None else genai.Client(api_key=key)
./v4/gemini.py:111:                response = self._client.models.generate_content(
./v4/gemini.py:245:        text = self.client.generate(system, prompt)
./v4/world.py:735:        text = self.oracle.ask(SYSTEM, prompt)
./world.py:739:        text = self.oracle.ask(SYSTEM, prompt)

$ grep -rn --include=*.py --exclude-dir=.venv -E "import (requests|urllib|http|aiohttp|httpx)|from (requests|urllib|http|httpx)" .
(no output, exit 1)

$ grep -rn --include=*.py --exclude-dir=.venv -i -E "batch|cached_content|count_tokens|asyncio|lru_cache|functools\.cache" .
(no output, exit 1)

$ grep -n -E "self\.(decide|decide_aside|ask_model)\(|def (decide|decide_aside|ask_model|turn)\b|for room in data.ROOMS|while remaining" world.py
636:    def turn(self, t):
668:        for room in data.ROOMS:
673:            while remaining:
678:                d = self.decide(p, t)
685:                    dq = self.decide_aside(q, p, opt.act["to"], t)
733:    def ask_model(self, p, t, opts, d):
773:    def decide(self, p, t):
789:            choice, why = self.ask_model(p, t, opts, d)
799:    def decide_aside(self, q, p, to, t):
809:        choice, why = self.ask_model(q, t, opts, d)

$ grep -n -E "for t in range\(morning.turns\)|morning.turn\(t\)" morning.py
65:        for t in range(morning.turns):
66:            morning.turn(t)

$ grep -n -E 'MINUTES|ORDER\s*=' data.py
14:ORDER = ["daniel", "elena", "leo", "mara"]
76:MINUTES = 90
77:MINUTES_PER_TURN = 3

$ grep -c -E "^\s+\[[0-9]{3} " runs/v5/*-seed*.stdout.txt
runs/v5/daniel_ate_it-gemma-seed1.stdout.txt:24
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:33
runs/v5/daniel_ate_it-gemma-seed3.stdout.txt:16
runs/v5/daniel_ate_it-gemma-seed4.stdout.txt:22
runs/v5/daniel_ate_it-gemma-seed5.stdout.txt:31
runs/v5/mara_ate_it-seed1.stdout.txt:0
runs/v5/mara_ate_it-seed2.stdout.txt:0
runs/v5/mara_ate_it-seed3.stdout.txt:0
runs/v5/miscount-seed1.stdout.txt:0
runs/v5/miscount-seed2.stdout.txt:0
runs/v5/miscount-seed3.stdout.txt:0
runs/v5/probe-gemma-seed2.stdout.txt:0

$ grep -hoE "\[[0-9]{3} [A-Z_]+\]" runs/v5/*-seed*.stdout.txt | sort | uniq -c
     80 [500 INTERNAL]
     46 [503 UNAVAILABLE]

$ grep -rn -E '\[[0-9]{3} ' runs/*unittest* runs/*/unittest*
(20 lines, all [429 RESOURCE_EXHAUSTED] from test_per_minute_429_backs_off_and_retries and
 test_repeated_429_gives_up_cleanly, which run against StubApi, not the API)

$ grep -n -E "^stopped:|^Traceback|^--- resumed|^--- resume" runs/*.stdout.txt runs/v*/*.stdout.txt
runs/v4/daniel_ate_it-seed2.stdout.txt:7:stopped: the daily request quota for this model is used up.
runs/v4/daniel_ate_it-seed2.stdout.txt:11:--- resumed at 12:44 UTC, after the daily quota reset at 07:00 UTC ---
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:29:stopped: still refused (503 UNAVAILABLE) after 6 retries.
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:33:--- resumed at 14:47 UTC, after the stop above (Gemma's service still refusing after 6 retries); the 11 cached answers are reused ---
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:49:stopped: still refused (500 INTERNAL) after 6 retries.
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:53:--- resumed again at 14:56 UTC (a probe showed the same prompt is accepted now); the 11 cached answers are reused ---
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:69:stopped: still refused (503 UNAVAILABLE) after 6 retries.
runs/v5/daniel_ate_it-gemma-seed2.stdout.txt:73:--- resume attempt 1 at 15:03 UTC; the cached answers are reused ---
runs/v5/miscount-seed2.stdout.txt:4:Traceback (most recent call last):
runs/v5/miscount-seed2.stdout.txt:26:--- resumed at 13:53 UTC after the crash above (a Windows file lock on the cache file); the 8 cached answers are reused ---

$ grep -n -i -E 'of 500|quota day|Real generate requests' REPORT*.md
REPORT-2.md:237: ... Real generate requests in this Pacific-time quota day: 298 from the first step plus 43 here, 341 of 500.
REPORT-3.md:325: ... Real generate requests in this Pacific-time quota day: 298 (step 1) + 43 (step 2) + 103 (here) = 444 of 500.
REPORT-4.md:420:**Requests per Pacific-time quota day**:
REPORT.md:24:Real generate requests today: 249 for these three mornings, plus 49 in two aborted attempts (see *Aborted attempts*), 298 in all, against the free limit of 500 a day. ...

$ grep -n -E '^- (Flash Lite|Gemma): ' REPORT-5.md
REPORT-5.md:973:- Flash Lite: 340 requests for its six runs. That includes the answer lost when miscount seed 2 crashed: ... 470 of the free 500 for the Pacific-time day.
REPORT-5.md:974:- Gemma: 213 requests for 87 answers in its five runs, plus 8 probe requests.
```

The meta files were tabulated with this loop (output condensed into §5):

```
$ for f in $(find runs -name '*.meta.json' | sort); do printf '%s\t' "$f"; python -c "import json,sys;m=json.load(open(sys.argv[1]));print('\t'.join(str(m.get(k)) for k in ['model','api_requests','answers_live','answers_from_cache','model_decisions','fallbacks','routine_decisions','max_prompt_tokens_estimated','max_prompt_tokens_counted_by_api','run_seconds']))" "$f"; done
```

The transcripts and caches (§5.1 split, §5.2, §6, §7) were tallied by a read-only script kept outside the repo. It opens the JSON files only, imports nothing from the prototype and calls nothing:
- **Transcripts:** for each `runs/v[2-5]/*.transcript.json`, count the acts with `mode != "routine"`. Split them into aside (option `accept_aside`/`refuse_aside`), inner (`inner` set) and social (the rest), then count by `who` and per turn.
- **Caches:** for each `cache/**/*.json`, take the min/mean/max of `len(prompt)`, `len(response)` and `prompt_tokens`, and count prompts containing `- accept_aside:`. Group by directory + scenario and count prompt texts that appear in more than one seed's file.

One more command imported `world.py` to read a constant, and sent no request:
`python -c "import world; print(len(world.SYSTEM))"` gives 913.

## 9. NOT FOUND

- Any request that carries more than one decision (batching), and any use of the Gemini Batch API.
- API-side context caching (`cached_content`), and any in-memory memoization beyond the disk cache.
- Any network path other than `google-genai`: no `requests`, `urllib`, `http`, `httpx` or `aiohttp` imports.
- Any `decide_aside` (A2) request in any saved run: 0 aside prompts in every cache.
- Retries in any Flash Lite run: no retry lines in runs/, v2–v5.
- Response token counts for run requests: only prompt tokens are stored.
- A per-call-site request counter in the code or meta. The split above is derived from transcripts.
- Requests from earlier, stopped processes in `meta.json`: meta holds the last process only. They are recovered here from stdout.
- stdout logs for the 49 aborted v1 requests: only their caches exist (cache/aborted/).
- The number of HTTP page requests made by `models.list()` (list_models.py:17).
- Any server-side record of the counted quota. The only server signal is the 429 PerDay on day 1, at client-counted request 499.
