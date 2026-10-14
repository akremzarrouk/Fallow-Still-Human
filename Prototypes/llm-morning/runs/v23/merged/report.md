# v23: a week at HEAD, against v22 (v16 seed 2, days 3 to 10)

Mode: run. The plan is `reports/v23_plan.md`, recorded before any live call (`runs/v23/plan_frozen.txt`). The code is
HEAD `cda05a2` (the door, telling and the budget fixes since v22); no code, test, prediction or seed was changed. The
control is v22 (`reports/days_v22.md`, `reports/stuck_facts.md` §1). Paths are relative to `Prototypes/llm-morning/`.
Raw outputs are in `runs/v23/`, the scorer and its outputs in `runs/v23/scoring/`. Clock stamps are the run's own.

## Result

| # | Prediction | v22 | v23 | Verdict |
|---|---|---|---|---|
| P1 | person-days whose most-chosen option takes ≥ 50% of that day's asks are fewer than v22's 20 of 32 | 20 of 32 | **25 of 32** | **FAIL** |
| P2 | ≥ 2 events from the street reach someone in the house (a knock heard, or words from outside), days 3 to 10 | 0 (no street) | **2**: the knock (day 6, 09:27) and the visitor's parting words (09:36), both heard by Elena alone; 1 visit | **PASS**, at the threshold |
| P3 | word-for-word equal answer pairs (same person, same day) are fewer than v22's 23 | 23 | **6** | **PASS** |
| P4 | whenever someone missed a visit, they are told of it by the end of the next day | no visit | by the frozen rule **no one missed the visit** (see below) | **NOT TESTED** |

**P4, read closely.** Only Elena heard the knock and the woman. Daniel, Leo and Mara are witnesses of one event of
the visit, Elena's refusal at 09:33 (`D6-032`), as `voices`: they heard her voice through the walls, not her words.
The plan's rule ("missed" = among none of the visit's events' witnesses) therefore counts nobody as having missed it,
and P4 is NOT TESTED. On the stricter reading (missed = heard neither the knock nor the visitor), all three missed it,
and **all three were told the same morning**: Daniel and Mara by Elena at 09:39, three minutes after the visit, and Leo
by Elena at 10:39 (`chronicle.beliefs`: `topic visit:v1`, `k 6`, minutes 159 and 219). The code agrees with that
reading: it offered `tell_*_visit` to Elena for those three, which F5 withholds from anyone who already knows.

**DONE:**
- **Days 3 to 10 ran**, in five sessions (§1). The run's last session exited **0**. **401 live asks** in all, under
  the 450 cap; days 1 and 2, nights 1 and 2 and minds 1 and 2 came from `cache/v16` (96 answers, 0 live, checked in all
  three ask records: "live in days1-2/nights1-2/minds1-2: 0").
- **The plan's hash is unchanged**: `0924e603…be60521c9d` at the record (2026-10-13T12:46:18Z) and at the end
  (2026-10-14T12:09:23Z); the 25 code and config sha256s of `plan_frozen.txt` are unchanged (25 OK). `git diff --stat` is
  empty. The key is in no file.
- **Each prediction has a verdict.** The scorer reproduced v22's 20 of 32 and 23 (`MATCH`) before it scored v23.

**What differed from the plan:**
- **Five sessions, not one.** The free API stopped the run three times and two sessions hung; §1 has each stop. The plan
  named only the quota. A `503 UNAVAILABLE` stop (session 1) was resumed the same day, as it is not the quota; the
  quota stop (session 3, day 9 min 06) was resumed after the reset at midnight Pacific.
- **Two sessions were stopped from outside.** Session 2 hung on a request for about eight hours and was stopped by its
  two process ids. Session 4 hung for 15 minutes in the night-9 night mind and its task was stopped by the user.
  Neither wrote its ask record; their answers (19 and 44) were already in the cache, which is written atomically per
  answer, and the next session replayed them.
- **The asks scored** are the final session's record (`runs/v23/asks3.json`). It replays every earlier answer
  from the cache, so it holds all 337 day asks of days 3 to 10 in order. It equals the transcript's model acts per day,
  person and order (8 of 8 days). The plan said `asks*.json`; the earlier records are subsets of it.

## 1. The run, session by session

| Session | Started (UTC) | Live asks | API requests | Stopped | Where |
|---|---|---|---|---|---|
| 1 | 2026-10-13 12:46:25 | 152 | 199 | 14:13:37, exit 3: `still refused (503 UNAVAILABLE) after 6 retries` | day 6 min 00 (its 4 answers were in) |
| 2 | 14:14:06 | 19 | 43 | hung after 14:42:45; stopped by PID about 23:03:40 | day 6 min 15 |
| 3 | 23:04:06 | 148 | 148 | 23:15:22, exit 3: `the daily request quota for this model is used up` | day 9 min 06 |
| 4 | 2026-10-14 11:43:01 | 44 | 44 | hung after 11:49:02 (night-9 night mind); task stopped by the user about 12:04 | night 9, mind |
| 5 | 12:04:50 | 38 | 38 | 12:07:46, **exit 0** | the end of day 10 |
| **All** | | **401** | 472 | | |

81 `503` retry lines in sessions 1 and 2, none after. Each session's stdout, stderr and stamps are in
`runs/v23/session{1..4}.*` and `runs/v23/daniel_ate_it-seed2.*` (session 5); `runs/v23/asks_live_before.txt` carried the
running count for the cap. Every resumed session replayed the earlier answers with 0 live asks before its first new
prompt ("day 6 min 00: … so far 0 live, 248 cached"; "day 6 min 15: … 0 live, 267 cached"; "day 9 min 03: … 0 live,
415 cached"). v22's 402 live asks ran in one 31-minute session.

Asks: day asks 337 (40, 32, 48, 47, 40, 48, 46, 36 on days 3 to 10; v22 342), nights and night minds 64. No answer was
invalid (0 fallback acts in the transcript).

## 2. The week, day by day

| Day | From the world | Night after | Tells | Elena | Leo | Mara | Daniel | Equal pairs |
|---|---|---|---|---|---|---|---|---|
| 3 | dry; tap 105.5 L; Daniel and Leo reach fasting stage 2 | all lie awake | — | reassure_all 8/10 (80%) | accuse_daniel 7/10 (70%) | accuse_daniel 8/10 (80%) | reassure_all 7/10 (70%) | 0 |
| 4 | dry; tap 81.5 L | all lie awake | — | reassure_all 5/8 (62%) | accuse_daniel 6/8 (75%) | accuse_daniel 7/8 (88%) | reassure_all 4/8 (50%) | 0 |
| 5 | dry by day, rain from 22:03; tap 57.5 L | **Daniel next door**: Leo `stop_daniel`, Daniel `go_anyway`; back shaken, **9 L water** | — | reassure_all 6/11 (55%) | accuse_daniel 5/11 (45%) | accuse_daniel 11/12 (92%) | still_going 7/14 (50%) | 2 (Mara 1, Daniel 1) |
| 6 | raining at 07:00 (Daniel `collect_rain`); tap 42.5 L; **knock 09:27**, a woman asks for water, heard by Elena, refused | all lie awake | **Elena → Daniel, Mara 09:39; Elena → Leo 10:39** | reassure_all 4/14 (29%) | confront_daniel 5/10 (50%) | accuse_daniel 6/11 (55%) | reassure_all 5/12 (42%) | 0 |
| 7 | rain 17:18, heard by all four; bin 66.0 L, tap 34.5 L; Leo stage 3 | **Daniel next door**: Leo `stop_daniel`, Daniel `go_anyway`; back with nothing | — | reassure_all 6/9 (67%) | confront_daniel 5/10 (50%) | accuse_daniel 4/9 (44%) | confront_leo 5/12 (42%) | 1 (Elena) |
| 8 | dry; bin 69.9 L, tap 26.5 L; Mara stage 3 | Daniel `sleep`, Mara `watch_door`; no trip | — | keep_daniel_home 5/11 (45%) | confront_daniel 6/10 (60%) | accuse_daniel 10/13 (77%) | still_going 11/14 (79%) | 2 (Elena) |
| 9 | rain 11:30–16:30, heard by Elena, Leo, Mara (Daniel resting); bin 53.9 → 230.3 L; tap 18.5 L | Mara `watch_door`; no trip | — | keep_daniel_home 4/11 (36%) | confront_daniel 8/10 (80%) | accuse_daniel 10/11 (91%) | confront_mara 7/14 (50%) | 1 (Daniel) |
| 10 | dry; tap 10.5 L, bin 230.3 L; Elena stage 3 (12:39) | — | — | reassure_all 5/6 (83%) | confront_daniel 7/10 (70%) | accuse_daniel 5/8 (62%) | confront_leo 7/12 (58%) | 0 |

Top option and its share are over the person's asks in the day scene (`runs/v23/scoring/score_v23.txt`). The shares of
50% or more are the P1 count: 25 of the 32 cells. Nobody ate on any day (shelf 0); thirst stayed at stage 0 for all four (the tap plus the
bin). No `ration_water` or `save_water` was said (v22: Leo's `ration_water`, day 9).

**Day 3.** The morning after Daniel's night-2 trip. For 15 minutes Mara accuses him, Leo accuses him, Elena asks for calm
and Daniel promises safety; at 10:27 and 17:39 the four say the same things again ("You went out last night and came back
with nothing, Daniel, after all that talk." — Leo, 10:27). A real family would be this angry the morning after; it would
not hold the same four positions at three separate meetings with nothing else said all day: no search, no water, no
food.

**Day 4.** The quarrel moves from the trip to the can ("You already admitted taking the can behind our backs, Daniel, so
stop acting like our savior now." — Leo, 11:00). After 11:03 nobody speaks again (32 asks, the fewest of the week). The
silence after a morning row is the most lived-in part of the day; the morning itself is day 3 again, word-alike.

**Day 5.** Daniel offers to go next door ("Fine, I will go out there myself tonight so you can all stop blaming me." —
10:03). Mara and Leo first tell him to go as a punishment ("You stole the food and you're the one who should go out,
Daniel." — Mara; Leo `send_daniel` at 19:03), then at 19:45 Leo and Elena beg him to stay. That night Leo tries to stop
him, he goes anyway and brings back 9 L. A real family could live this day: the turn from "go, then" to "stay" is
human. Mara's 11 `accuse_daniel` in 12 asks are not: the same charge, word for word twice ("You only offered to go
because you want everyone to feel sorry for you after what you did.", 10:03 and 10:06).

**Day 6.** The week's most varied day. Daniel puts the bin under the drainpipe in the rain at 07:00; the family splits
over his trip ("Hush, Mara, he went for the water we needed so badly." — Elena). At 09:27 a woman knocks and asks for
water; Elena, alone in the kitchen, looks through the gap in the boards twice and sends her away ("Please go away, we have
nothing for you and it is not safe here."), with 42.5 L in the tap and rain falling. Three minutes later she tells Daniel and
Mara ("Someone came to the front door a few minutes ago. I told her to go away."), and Leo an hour later; Daniel repeats it
correctly at 10:36 ("…A woman about forty, she said, and she turned her away."). A real family would live this day,
the refusal included. After Elena's tell at 10:39 nobody speaks of the visit again, on any day.

**Day 7.** Back to the can at breakfast ("You took the food days ago and you're still lying about it now." — Leo).
Between 10:03 and 10:36 Daniel and Leo bicker in a way that sounds like brothers ("You think you can just wander in here
after everything like nothing's wrong, Leo?" / "I was just in the other room, Daniel, not wandering anywhere."). The rain
at 17:18 is heard by all four and spoken of by none. At 19:00 Daniel says he will go again; Elena and Leo say no; that
night he goes and comes back with nothing. Partly lived: the bickering yes, the rain unheard no.

**Day 8.** The day after a wasted trip, Daniel says he is going again 11 times in 14 asks (`still_going`), 8 of them with "I am
the oldest" ("I don't care what any of you say, I am the oldest and I am going out there tonight." — 10:12). Elena and Leo
answer `keep_daniel_home` or `nobody_goes` 12 times; Elena twice word for word ("Nobody is going out tonight, we stay
together."). 27 trip-position acts. At bedtime Daniel sleeps: "I have no strength left to go out tonight and my body
simply cannot take another fruitless trip." Mara sits by the front door all night. A family would have this argument once
or twice in a day, not 27 times; the bedtime turn (exhaustion beating bluster) is the human part.

**Day 9.** Rain from 11:30 to 16:30 fills the bin from 53.9 to 230.3 L; Elena, Leo and Mara hear it start; nobody speaks
of it (the log: "Q6 skipped: no rain action"; the bin was already out). The same at day 7's 17:18. The morning is the can and Daniel's going ("Mara, stop accusing me when you know
you ate your own share in front of everyone." — Daniel, min 06, the only new thing said). From 12:12 to 12:18 Mara and
Daniel, alone in the kitchen, say the same exchange three times (the worst moment, below). No.

**Day 10.** Elena reaches fasting stage 3 at 12:39. The morning is the can once more ("You took it before and you're going
to try it again, Daniel. Don't think we forgot." — Mara); 09:18 to 09:57 Leo and Daniel on the can. From 09:57 to 21:00
nobody is asked (no stretch fires; Q5 at 19:00 is not asked: "no trip position today"). On their tenth day without food,
with 230 L of rain water caught, the family's last words are a quarrel about a can opened on day 1. No.

### The worst moment of the week

Day 9, 12:12 to 12:18. Rain has been falling for 40 minutes; nobody has eaten for nine days; Mara and Daniel are at fasting stage 3.

> 12:12 Mara: "You think you can just take everything and ruin it all."
> 12:12 Daniel: "You have no right to talk to me like that after everything I do for us."
> 12:15 Mara: "You think you can just take everything and act like we owe you."
> 12:15 Daniel: "You have no right to talk to me that way, Mara."
> 12:18 Mara: "You think you can just take everything and act like we owe you, Daniel. You took the can and you won't even admit it honestly."
> 12:18 Daniel: "Stop talking to me like that, Mara, I am the oldest and I won't take this from you."

It is not word-for-word equal (P3 does not count it), and it is the loop `reports/stuck_facts.md` measured: the same
charge and the same answer, six lines in six minutes, about a can opened eight days earlier, while the first rain in two
days falls on the bin outside.

## 3. Against v22

| | v22 | v23 |
|---|---|---|
| Live asks; sessions | 402; 1 | 401; 5 |
| Day asks (days 3–10) | 342 | 337 |
| Person-days with top share ≥ 50% (P1) | 20 of 32 | **25 of 32** |
| … per person (Elena, Leo, Mara, Daniel) | 2, 4, 8, 6 | 5, 7, 7, 6 |
| Person-days with top share ≥ 80% | 4 (Elena 3, 7; Mara 3, 5) | 7 (Elena days 3, 10; Leo 9; Mara 3, 4, 5, 9) |
| Longest run of one option | 8 (Mara day 5; Daniel day 10) | 9 (Daniel day 8, `still_going`) |
| Word-for-word equal pairs (P3) | 23 (Mara 14, Leo 6, Daniel 2, Elena 1) | **6** (Elena 3, Daniel 2, Mara 1) |
| Pairs sharing ≥ 60% of words | 126 of 1564 | 86 of 1420 |
| Mara `accuse_daniel` + `confront_daniel` / her asks | 75 / 88 | 75 / 82 |
| Leo `accuse_daniel` + `confront_daniel` / his asks | 38 / 81 | **57 / 79** |
| Trip-position acts | 115 (days 4, 5, 8, 9, 10) | 63 (days 5, 7, 8, 9) |
| Daniel `still_going` | 32 | 25 |
| Trips (went out) | 1 (N5: water 9 L) | **2** (N5: water 9 L; N7: nothing) |
| Street: visits; events that reached someone | — | 1; 2 (knock and parting words, Elena) |
| Tells | — | 2 (Elena, day 6: 3 listeners) |
| `collect_rain` / `ration_water` | 1 / 1 | 1 / 0 |
| Silent choices | 16 | 27 |
| Bedtimes, nights 3–9 (28) | `lie_awake` 22, `sleep` 4, `go_next_door` 1, `watch_door` 1 | `lie_awake` 23, `go_next_door` 2 (Daniel N5, N7), `watch_door` 2 (Mara N8, N9), `sleep` 1 (Daniel N8) |

By the counts: fewer word-for-word repeats (23 → 6) and fewer near-repeats (126 → 86 pairs), but **more** days held by one
option (20 → 25), because Leo moved onto Daniel (57 of 79 asks against 38 of 81) and Elena's `reassure_all` held 5 days
(2 in v22). The house went out twice instead of once, and a stranger came to the door once. Mara is where she was: 75
of her asks are against Daniel in both runs.

## 4. Commands and output

All from `Prototypes/llm-morning/`, with `.venv/Scripts/python.exe` (written `python` below).

**1. The fake run, first** (`runs/v23/fake_run.stdout.txt`):
```
$ env -u GEMINI_API_KEY python -u runs/v23/run_capped.py --fake
  street day 6 09:27: a visit to the front door from no. 6 (ask water)
  …
asks recorded: 381 (381 live) -> runs\v23\fake\asks.json
exit 0
```

**2. The scorer on v22, and on the fake** (`runs/v23/scoring/control_v22.txt`, `fake_score.txt`):
```
$ env -u GEMINI_API_KEY python runs/v23/scoring/score.py --control
check day 3: transcript model acts 40, recorded asks 40, same order per person: True      (days 4 to 10 likewise)
check days that differ: 0
v22 control: P1 20 of 32 (stuck_facts: 20 of 32) | P3 23 (stuck_facts: 23) | MATCH
$ env -u GEMINI_API_KEY python runs/v23/scoring/score.py runs/v23/fake/daniel_ate_it-seed2.transcript.json runs/v23/fake/asks.json
check days that differ: 0
P1 PASS (3 of 22 person-days with top share >= 50%)
P2 PASS (2 street events reached someone (1 visits))
P3 PASS (0 word-for-word equal pairs)
P4 NOT TESTED (no one missed a visit; away through the next day, not counted: [(6, 'v1', 'daniel')])
```

**3. The copy and the check before any live call** (`runs/v23/cache_copy.sha256.txt`, `premiss-seed2.stdout.txt`):
```
$ cp cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed2.json cache/v23/
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v16/…seed2.json
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v23/…seed2.json
$ env -u GEMINI_API_KEY python runs/v23/premiss.py 2
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']; …; answered from the cache before it: 96
exit 3
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v23/…seed2.json   (unchanged)
```

**4. The record** (`runs/v23/plan_frozen.txt`):
```
recorded_utc: 2026-10-13T12:46:18Z
0924e6030841de35f86a5306726119958891e4211ec086fe0819f0be60521c9d *reports/v23_plan.md
$ git rev-parse HEAD
cda05a22473a7d9f3042c2606afb710bb94c357c
$ git diff --stat
(empty)
(+ git status --short and the sha256 of every *.py and config.json)
```

**5. The run** (sessions 1 to 5; `GEMINI_API_KEY` from the environment, that process only):
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -u runs/v23/run_capped.py > runs/v23/daniel_ate_it-seed2.stdout.txt 2> …stderr.txt
session 1: … day 6 min 00: model asked for 4; … so far 152 live, 96 cached, 199 API requests
           stopped: still refused (503 UNAVAILABLE) after 6 retries.       exit 3
session 2: … day 6 min 15: … so far 19 live, 248 cached, 43 API requests   (hung; stopped by PID 34364, 11204)
session 3: … day 9 min 03: … so far 148 live, 267 cached, 148 API requests
           stopped: the daily request quota for this model is used up.     exit 3
session 4: … night 9: … so far 42 live, 415 cached, 42 API requests        (hung in the night-9 mind; stopped by the user)
session 5: night 9, the night mind: model asked for 4; so far 2 live, 459 cached, 2 API requests
           wrote runs/v23/daniel_ate_it-seed2.md
             api_requests: 38   answers_live: 38   answers_from_cache: 459   run_seconds: 172.3
             story_sha256: b2cae6037513a47d08f87c6ef1ef41a2f6c74485b8d28ae23e7aba4c68aacf09
           asks recorded: 497 (38 live) -> runs\v23\asks3.json             exit 0
```
Nights as printed: `night 5: rainy; bedtime Daniel go_next_door, Elena lie_awake, Leo lie_awake, Mara lie_awake; Daniel out
(back shaken, with water), water 9 L` and `night 7: dry; bedtime Daniel go_next_door, …; Daniel out (back with nothing), water 0 L`.

**6. Days 1 and 2 cached only** (from the three ask records):
```
asks.json  248 live 152 live in days1-2/nights1-2/minds1-2: 0 first live scene: day3
asks2.json 415 live 148 live in days1-2/nights1-2/minds1-2: 0 first live scene: day6
asks3.json 497 live 38 live in days1-2/nights1-2/minds1-2: 0 first live scene: mind9
```

**7. Scoring** (`runs/v23/scoring/score_v23.txt`, `lines.txt`, `summary.txt`):
```
$ env -u GEMINI_API_KEY python runs/v23/scoring/score.py runs/v23/daniel_ate_it-seed2.transcript.json runs/v23/asks3.json
check day 3: transcript model acts 40 + fallback 0, recorded asks 40, same order per person: True   (days 4 to 10 likewise)
check days that differ: 0
P1 FAIL (25 of 32 person-days with top share >= 50%)
P2 PASS (2 street events reached someone (1 visits))
P3 PASS (6 word-for-word equal pairs)
P4 NOT TESTED (no one missed a visit)
street events:
  D6-028 09:27 knock witnesses {'elena': 'heard'}: a knock at the front door (h6, ask_water)
  D6-033 09:36 door_line witnesses {'elena': 'heard'}: the person at the door (refused_polite): "Right. I'm sorry. I'll try somewhere else."
$ env -u GEMINI_API_KEY python runs/v23/scoring/lines.py runs/v23/daniel_ate_it-seed2.transcript.json > runs/v23/scoring/lines.txt
$ env -u GEMINI_API_KEY python runs/v23/scoring/summary.py > runs/v23/scoring/summary.txt
== v22: 342 day asks, 32 person-days … all: >=50% 20; >=80% 4; longest 8; >=60% 126/1564; equal 23
== v23: 337 day asks, 32 person-days … all: >=50% 25; >=80% 7; longest 9; >=60% 86/1420; equal 6
```
The visit's witnesses (P4), from the transcript's chronicle:
```
D6-028 147 knock        {'elena': 'heard'}
D6-029 147 door_line    {}
D6-030 147 door_look    {'elena': 'did'}
D6-031 150 door_look    {'elena': 'did'}
D6-032 153 door_refuse  {'elena': 'did', 'daniel': 'voices', 'leo': 'voices', 'mara': 'voices'}
D6-033 156 door_line    {'elena': 'heard'}
D6-034 156 door_end     {'elena': 'saw'}
beliefs: daniel, mara (source elena, k 6, minute 159); leo (source elena, k 6, minute 219); all topic visit:v1
```

**8. At the end** (`runs/v23/end_checks.txt`):
```
checked_utc: 2026-10-14T12:09:23Z
0924e6030841de35f86a5306726119958891e4211ec086fe0819f0be60521c9d *reports/v23_plan.md
(recorded: 0924e6030841de35f86a5306726119958891e4211ec086fe0819f0be60521c9d)
     25 OK
$ git rev-parse HEAD
cda05a22473a7d9f3042c2606afb710bb94c357c
$ git diff --stat
(empty)
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v16/…seed2.json   (unchanged)
$ key search (grep -rlF over the repository, but .venv, __pycache__, .git, Library, node_modules)
files containing the key: 0
```
`git status --short` lists only untracked files (`cache/v23/`, `reports/v23_plan.md`, `runs/v23/`, and the earlier
`cache/n9_cause/`, `runs/n9_cause/`, `runs/v6/*.replay.md`, `investigations/`, not part of this work).

`python merge-slice-docs.py Prototypes/llm-morning/runs/v23/merged` (from the repository root) wrote
`runs/v23/merged/merged-all.md` from copies of this report and the plan.
