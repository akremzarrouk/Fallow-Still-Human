# v20: v16 seeds 2 and 3, days 3 to 5, on the outings facts, household knowledge and the evening moment

Mode: run. The plan is `reports/days_v20_plan.md`, recorded before any live call (`runs/v20/plan_frozen.txt`). The
code is HEAD `361eb30` (`reports/facts_and_evening.md`, `reports/household_knowledge.md`). No code, test or plan line
was edited. Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/v20/`, and the scoring outputs
in `runs/v20/scoring/`.

## Result

| # | Prediction | Verdict | Evidence |
|---|---|---|---|
| H1 | False statements about past events, days 3–5, ≤ 6 (v19: 12) | **PASS** | **5** (§4): seed 2 has 2, seed 3 has 3. Two of them, Mara's "You took everything", are counted under the rule for numbers that v19 used for S3-5; without them the count is 3. |
| H2 | Q5 fires on ≥ 3 of the 6 days, and ≥ 1 Q5 stretch has a trip position act | **PASS** | Q5 fired on 3 days: seed 2 day 5, seed 3 days 3 and 4. On the other 3 days nobody had taken a trip position: "no trip position today". All 3 Q5 stretches hold trip position acts, 9 in all (§3). |
| H3 | ≥ 1 seed: `go_further` at a bedtime on night 3 or 4 | **PASS** | Seed 3: Daniel on night 3 and on night 4 (model). Seed 2: none. |
| H4 | From day 3 on: no far act shown as "says he/she will not go"; no "nobody has gone out" after a trip | **PASS** | 275 prompts read: every one sent from day 3 on (seed 2: 134, seed 3: 141). Both counts 0. |
| H5 | Food home → next day eats, shares or gives; someone not back → next day ≥ 2 others name them | **PASS** | **Food:** seed 3, night 4, Daniel brought 4 portions home. Day 5, min 00: Daniel `eat`, Elena `share`. **Loss:** nobody was lost; NOT TESTED. |
| H6 | Every seed with a night-3 trip: ≥ half of day 4's morning speech acts use a pair new to day 3's morning | **FAIL** | Seed 3 only (seed 2 had no trip on night 3): **0 of 24**, as in v19. |
| H7 | Live asks ≤ 360; each day ≤ 48 | **PASS** | 134 + 141 = **275** live. Day asks: seed 2 40, 38, 40; seed 3 40, 48, 28. |

**DONE:**
- **The plan.** It was recorded at **2026-10-08T09:52:02Z**, sha256 `8a52064a…27e30dd98`. The first live call came
  after it: seed 2 started at 09:53:34Z. At the end (10:16:18Z) the sha256 is the same, and the 20 code and config
  sha256s are unchanged (§6).
- **Exit codes.** Both seeds exited 0.
- **Verdicts.** All 7 predictions have one: 6 PASS, 1 FAIL.

**Against v19** (`reports/days_v19.md`, `reports/v19_contradictions.md`):

| | v19 | v20 |
|---|---|---|
| False statements about the past, days 3–5 | 12 | 5 |
| Bedtime `go_further`, nights 3–4 | 1 (seed 3, night 3) | 2 (seed 3, nights 3 and 4) |
| Trips that brought food home | 0 | 1 (seed 3, night 4: 4 portions) |
| Days when someone ate, shared or gave | 0 | 1 (seed 3, day 5) |
| Q5 | did not exist | fired on 3 of 6 days; 24 asks |
| Day-4 morning pairs new to day 3's (seed 3) | 0 of 24 | 0 of 24 |
| Live asks | 268 | 275 |

## 1. Asks per day, per seed

From `runs/v20/daniel_ate_it-seed{2,3}.meta.json` (`runs/v20/scoring/asks.txt`). Days 1–2, nights 1–2 and minds 1–2
were answered from the cache: 96 answers for seed 2, 135 for seed 3. Every ask from day 3 on was live, with no 503
or 429 in either stdout.

| Seed | Day 3 | Night 3 | Mind 3 | Day 4 | Night 4 | Mind 4 | Day 5 | Live |
|---|---|---|---|---|---|---|---|---|
| 2 | 40 | 4 | 4 | 38 | 4 | 4 | 40 (Q5: 8) | 134 |
| 3 | 40 (Q5: 8) | 8 | 4 | 48 (Q5: 8) | 9 | 4 | 28 | 141 |

**The day's last ask**, from each stdout's last "day asks" line:

| Seed | Day 3 | Day 4 | Day 5 |
|---|---|---|---|
| 2 | 20:12 | 19:06 | 19:06 |
| 3 | 19:03 | 19:03 | 14:33 |

- **v19 ran out at 11:00, 11:09 and 11:57 on three of six days.** In v20, every day but seed 3's day 5 has an ask at
  or after 19:00: Q5, or a Q1 there.
- **Seed 3's day 4** spent its 40 by 11:00, and Q5's 8 came on top at 19:00.

## 2. Each seed, day by day

### Seed 2 (`runs/v20/scoring/account.txt`)

Everyone knows next door is empty from day 3: Daniel went next door on night 2 and came back with nothing. All four
bedtimes on nights 3 and 4 offered `go_further`. Nobody went out on night 3 or 4.

- **Day 3** (shelf 0; morning to min 18; Q2 at 10:27; Q1 at 20:09).
  - **The talk.** Mara, Leo and Elena answer Daniel's night-2 trip ("You snuck out last night like a coward and came
    back with nothing at all!", Mara, min 00). Daniel and Elena reassure.
  - **Trip positions:** none. Q5 at 19:00: "no trip position today".
- **Night 3:** Daniel `sleep` ("I have no strength left to stay awake…"); Elena `watch_door`; Leo and Mara
  `lie_awake`. No trip.
- **Day 4** (shelf 0; morning to min 12; Q2 at 10:51; Q1 at 15:30 and 19:00).
  - **The talk** turns to the can: "Daniel, we all know you took the food, so stop pretending you are protecting
    anyone." (Leo, min 00).
  - **Trip positions:** none. Q5: "no trip position today".
- **Night 4:** all four `lie_awake`. No trip.
- **Day 5** (shelf 0; morning to min 18; Q2 at 10:03; Q5 at 19:00).
  - **The morning has trip positions:**
    - min 06, Leo `propose_trip`: "Daniel went last time and found nothing, but maybe we should look at the
      neighbour's house again tonight instead of arguing."
    - min 06, Elena `nobody_goes`.
    - Leo volunteers at min 09 and 15. Daniel `keep_leo_home` at min 12, and volunteers at min 15.
    - min 12, Leo and Mara `send_daniel`.
    - 10:06, Leo and Daniel both `still_going`; Mara `keep_daniel_home`.
  - **Day 5 is the last day:** there is no night 5.
- **Food:** none, and no food act.

### Seed 3

Everyone knows next door is empty from day 3: Daniel went next door on night 2 and came back with nothing.

- **Day 3** (shelf 0; morning to min 18; Q2 at 10:48; Q5 at 19:00).
  - **Daniel volunteers,** for next door first (min 00), then further along (`propose_far` min 06; `volunteer_far`
    min 09, 10:48 and 19:00).
  - **The others say no.** Elena `nobody_goes` and `keep_daniel_home`; Leo `keep_daniel_home` and `nobody_goes`;
    Mara `confront_daniel`.
- **Night 3.**
  - **Bedtime:** Daniel `go_further` ("I have to find food for my family no matter the risk."); Elena, Leo and Mara
    `lie_awake`.
  - **In the night:** Leo `stop_daniel` ("Daniel, stay in this room. You are not going out there again tonight.");
    Daniel `go_anyway` ("I have to find something for us, Leo, stay back."). Elena and Mara `get_up_and_look`.
  - **The trip:** further along, clean; house 1 held 0. Back with nothing. Shelf 0 → 0.
- **Day 4** (shelf 0; morning to min 18; Q2 at 09:57 and 10:57; Q5 at 19:00).
  - **The same positions as day 3:** Daniel `volunteer_far`, `volunteer` and `still_going`; Elena, Leo and Mara
    `keep_daniel_home`, `nobody_goes` and `confront_daniel`.
  - **The 40 were spent by 11:00,** and Q5 had its own 8 at 19:00.
- **Night 4.**
  - **Bedtime:** Daniel `go_further` ("I am the eldest and I must keep searching the houses further down the street
    until I find food for them."); Elena and Mara `watch_door`; Leo `lie_awake`.
  - **In the night, all three try to stop him:**
    - Leo: "Daniel, stay in this room. You are not going out there again tonight."
    - Elena: "Daniel, please don't go out there into the dark."
    - Mara: "Daniel, please don't go out there again, it accomplishes nothing."
    - He answers twice, `go_anyway`: "I have to keep trying, Leo, I am the eldest." and "I have to keep trying, I am
      the oldest and I cannot just sit here and do nothing."
  - **The trip:** further along, clean; house 2 held 4; he took 4. **Back with food. Shelf 0 → 4.**
- **Day 5** (shelf 4; morning to min 09; Q2 at 09:48 and 14:27; 28 asks).
  - **min 00, the food:** Daniel `eat`: "I brought it back, and I need this to stand." Elena `share`: "Let us share
    what we have and eat together quietly."
  - **Then the talk** is about his going out against them and his lying: "You think you can just sneak out and act
    like a hero after lying to us all?" (Mara, min 00). Daniel answers with the food: "I brought back four portions
    when nobody else would, Leo, so don't lecture me." (09:48).
  - **Trip positions:** none. Q5: "no trip position today".
- **Nobody was lost** in either seed.

## 3. Every Q5 stretch, its lines

Rooms and who was awake are from each day's `quiet.log`, Q5 entry; the acts are from the transcript
(`runs/v20/scoring/account.txt`). Each was in the kitchen with all four awake.

**Seed 2, day 5, 19:00–19:09** (8 asks). Asked: Daniel, whose last trip act was latest (`still_going`, 10:09).
```
19:00 Leo [silent, routine]
19:00 Elena [silent, routine]
19:00 Mara [accuse_daniel]: You took everything and you know it, Daniel.
19:00 Daniel [confront_mara]: Stop accusing me, Mara, I am trying to keep us all alive.
19:03 Mara [accuse_daniel]: You are the one who took it, Daniel, and you are the reason we have nothing left.
19:03 Daniel [confront_mara]: You have no right to talk to me that way, Mara.
19:03 Leo [accuse_daniel]: Daniel, stop deflecting and admit you are the reason our pantry is empty.
19:03 Elena [reassure_all]: Please stop fighting, we will get through this evening if we stay calm.
19:06 Daniel [still_going]: I told you, I am still going to the neighbour's house tonight.
19:06 Mara [accuse_daniel]: You can't just go out there like it's nothing after what you stole from us, Daniel.
19:06 Elena [silent, routine]
19:06 Leo [silent, routine]
```
Daniel, the one asked, did not speak first at 19:00: Mara's turn came before his in the room's order.

**Seed 3, day 3, 19:00–19:06** (8 asks). Asked: Daniel.
```
19:00 Daniel [volunteer_far]: I'll go further down the street tonight and check the other houses myself.
19:00 Mara [confront_daniel]: You went out last night and came back with nothing, Daniel. You shouldn't go out again.
19:00 Elena [keep_daniel_home]: Daniel, you must stay home tonight. We cannot afford to lose you out there.
19:00 Leo [keep_daniel_home]: Mom is right, Daniel. Going out further tonight is just asking to get killed.
19:03 Daniel [confront_leo]: Leo, you cannot just tell me what to do when we are starving.
19:03 Leo [confront_daniel]: Daniel, you stole the food and lied about it for days, so spare me the lecture on what we can or cannot do.
19:03 Mara [confront_daniel]: Daniel, you started all of this by lying and stealing, and now you want to risk your life out there again?
19:03 Elena [reassure_all]: We are all safe here together, and we will get through this without any more fighting.
```

**Seed 3, day 4, 19:00–19:06** (8 asks). Asked: Elena, whose last trip act was latest (`nobody_goes`, 11:00).
```
19:00 Daniel [still_going]: I am the eldest, and I will go out there again tonight to find us something.
19:00 Mara [confront_daniel]: Daniel, you went out last night and came back with nothing, going out again is just insane.
19:00 Leo [keep_daniel_home]: Daniel, you went out last night and found nothing, so staying home is the only rational choice.
19:00 Elena [keep_daniel_home]: Daniel, you cannot go out there again tonight, you must stay home where it is safe.
19:03 Daniel [still_going]: I have to go because it is my duty to keep you all alive.
19:03 Mara [confront_daniel]: Daniel, risking your life out there again accomplishes nothing and puts us all through hell.
19:03 Leo [confront_daniel]: Daniel, walking out into the dark again is not duty, it is just reckless.
19:03 Elena [nobody_goes]: Nobody is going out into the dark tonight, we stay safe together here.
```

**Trip position acts in Q5 stretches (H2):**
- seed 2, day 5: Daniel `still_going` (19:06);
- seed 3, day 3: Daniel `volunteer_far`, Elena and Leo `keep_daniel_home` (19:00);
- seed 3, day 4: Daniel `still_going` ×2, Leo and Elena `keep_daniel_home`, Elena `nobody_goes`.

## 4. H1: the false statements about the past

All 222 speech acts of days 3–5 (seed 2: 110, seed 3: 112; `runs/v20/scoring/lines.txt`) were read against the
chronicle, by the method of `reports/v19_contradictions.md`.

| # | Seed, day, time, speaker | The statement | The true fact |
|---|---|---|---|
| 1 | 2, day 4, min 00, Mara | "You took everything and you are the reason we are starving." | Daniel took one can, before day 1's count (D1-001: "one can fewer"). The 2 portions left after the count went to Mara, who ate one (D1-044), and to Elena, whom Daniel gave one (D2-003, D2-004). |
| 2 | 2, day 5, 19:00, Mara | "You took everything and you know it, Daniel." | As 1. |
| 3 | 3, day 3, min 06, Leo | "Daniel, you nearly got yourself killed last night for nothing, we are not sending you out into the street again." | Night 2's street was clean (`night2.groups[0].street`). Daniel's own line: "Nothing troubled you in the street." No danger is recorded. |
| 4 | 3, day 3, min 09, Elena | "Daniel, you stayed home last night and you will stay home tonight. We are not losing you to the street." | Daniel went next door on night 2 (N2-11) and came back with nothing (N2-12). |
| 5 | 3, day 5, 14:33, Mara | "Daniel, you brought back food last night like you always do, but you still took that can from us days ago." | Night 4 was the first trip to bring food home. Nights 2 and 3 came back with nothing (N2-12, N3-12; N4-13 "back with food"). |

**What the speakers' prompts held** (the same prompts, from `cache/v20`):
- **4, Elena's.** It held `About going out at night: Daniel went to the neighbour's house last night and came back
  with nothing.` and `About the neighbour's house: Daniel went there last night and came back with nothing.`
- **5, Mara's.** It held all three trips: `About going out at night: Daniel went to the neighbour's house three nights
  ago and came back with nothing; Daniel went further along the street the night before last and came back with
  nothing; Daniel went further along the street last night and came back with food.`
- **3, Leo's.** It held that Daniel came back with nothing, and "Outside is dangerous". Under household knowledge,
  whether the street troubled him is Daniel's alone.
- **1 and 2.** The day-1 and day-2 portions are earlier days' facts. Mara's block C on day 4 says she ate one.

**Counted as one judgment call:** 1 and 2 are exaggeration, counted because they are about a number, as v19 counted
S3-5 ("lied about the food once"). Without them, H1's count is 3.

**Read and not counted** (idioms, causes, or claims about the present), each with the record:
- **Seed 2, day 3, min 09, Mara, "You went out behind our backs".** Mara noticed his going out on night 2 (N2-09).
- **Seed 2, day 5, min 12, Leo, "volunteering to search the empty houses".** Only next door had been searched.
- **Seed 2, day 4, 10:51, Leo, "you are the only one who didn't respect the rules".** A characterization.
- **Seed 2, day 5, 19:03, Leo, "you are the reason our pantry is empty"; Mara, "the reason we have nothing left".**
  Causes, not events.
- **Seed 3, day 3, 19:03, Leo, "you stole the food and lied about it for days".** Daniel denied it on days 1 and 2,
  then admitted it (D2-022).
- **Seed 3, day 4, 11:00, Leo, "there is nothing left out there"; min 09, Elena, "when there is nothing left to
  find".** Present claims; the second house further along was not yet drawn. It held 4 on night 4.
- **Seed 3, day 4, 09:57, Elena, "we will not survive another night like the last one".** A characterization.
- **Seed 3, day 5, 09:54, Leo, "after we agreed nobody should".** Elena, Leo and Mara said nobody should go on day 4;
  Daniel did not agree.

**Not from v20:** `cache/v20` also holds a Leo answer with "just like you always do when you act on your own". It is
one of v16's entries (`in v16 cache: True`). v16's day 3 was not a quiet day, so no v20 prompt asked it, and it is not
in the transcript.

## 5. What the run shows, by the counts

- **False statements about the past fell from 12 to 5.** Of the 5, 2 had the true fact in the speaker's prompt as a
  standing line (Elena's, Mara's). The other 3 rest on facts the prompt did not hold, or only as older days' facts.
- **The evening.** Q5 fired only on days with trip positions: 3 of 6. Every Q5 stretch had trip positions. In seed 3
  they repeat the day's: Daniel offers, the others say no. Seed 2's day-5 Q5 is mostly about the can.
- **The houses further along.** Seed 3's Daniel went twice, against all three on night 4, and brought 4 portions
  home. Day 5 then shows the house eating and sharing.
- **Seed 2 took no trip position on days 3 and 4,** and none at bedtime. Its day 5 had next-door offers from Leo and
  Daniel, with no night after it.
- **Day 4's morning in seed 3 repeated day 3's pairs: 0 of 24,** as in v19 (H6).

## 6. Commands and output

All from `Prototypes/llm-morning/`. Only the two live runs had `GEMINI_API_KEY` set.

**1. The plan record** (`runs/v20/plan_frozen.txt`, with `git status --short`, `git diff --stat` (empty), and every
`*.py` and `config.json` sha256):
```
recorded_utc: 2026-10-08T09:52:02Z
8a52064aadb49ff71ea192d2c849356e0a222f25c53c85798aa1aab27e30dd98 *reports/days_v20_plan.md
$ git rev-parse HEAD
361eb300c434428131d423cf3b4ede61eb43b380
```
The scorer `runs/v20/scoring/h_score.py` was written next, before any live call. It was checked on a fake 5-day run
of both seeds, in a scratch folder with no API: exit 0, and every rule computed (a SUMMARY line for H2–H7).

**2. The copy, and where each seed first misses** (`runs/v20/cache_copy.sha256.txt`,
`runs/v20/premiss-seed{2,3}.stdout.txt`; `runs/v20/scoring/premiss.py` is v19's with `out="v20"`):
```
$ mkdir -p cache/v20 && cp cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{2,3}.json cache/v20/
$ sha256sum cache/v16/*seed{2,3}.json cache/v20/*seed{2,3}.json     # pairwise equal: d79a4939…, 25e92cc7…
$ for n in 2 3; do env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v20/scoring/premiss.py $n > runs/v20/premiss-seed$n.stdout.txt 2>&1; done
seed 2 exit 3
  night 2, the night mind: model asked for 4; so far 0 live, 96 cached, 0 API requests
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']; …
seed 3 exit 3
  night 2, the night mind: model asked for 4; so far 0 live, 135 cached, 0 API requests
FIRST MISS: scene index 6, speaker Daniel; Now line: ['Now, minute 00, you are in the kitchen.']; …
$ sha256sum -c runs/v20/cache_copy.sha256.txt        # 4 OK
```
Scene index 6 is day 3.

**3. The runs,** one after the other (`runs/v20/daniel_ate_it-seed{2,3}.stdout.txt`;
`runs/v20/seed{2,3}.started_utc.txt`):
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u morning.py --seed 2 --out v20 --days 5 > runs/v20/daniel_ate_it-seed2.stdout.txt 2>&1
started 2026-10-08T09:53:34Z   exit 0
  api_requests: 134  answers_live: 134  answers_from_cache: 96  day3 day_asks: 40  day4 day_asks: 38  day5 day_asks: 40
$ … morning.py --seed 3 --out v20 --days 5 > runs/v20/daniel_ate_it-seed3.stdout.txt 2>&1
started 2026-10-08T10:04:01Z   exit 0
  api_requests: 141  answers_live: 141  answers_from_cache: 135  day3 day_asks: 40  day4 day_asks: 48  day5 day_asks: 28
```
- **The 360 watch.** Live asks reached 275; no process was stopped.
- **Seed 3's night-3 mind** printed one warning: Elena's memory "Daniel went out into the dark again and came back
  before dawn with nothing in his hands while I waited by the door." was kept with S8 "daniel go out: not twice". It
  is in the stdout.

**4. Scoring** (`runs/v20/scoring/score_v20.txt`; account in `account.txt`; lines in `lines.txt`; asks in
`asks.txt`):
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v20/scoring/h_score.py > runs/v20/scoring/score_v20.txt 2>&1
exit 0
seed 2: replay for H4 exit 1, prompts 230
seed 3: replay for H4 exit 1, prompts 276
seed 2:
  H2_DAYS {"3": [["19:00", false, null, "no trip position today"]], "4": [["19:00", false, null, "no trip position today"]], "5": [["19:00", true, "daniel", null]]}
  H2_TRIP_ACTS {"3": [], "4": [], "5": [["19:06", "Daniel", "still_going"]]}
  H3 []
  H4 {"prompts_scanned": 134, "far_as_will_not_go": [], "nobody_after_a_trip": [], "trips_before": {"3": true, "4": true, "5": true}}
  H5_FOOD []   H5_LOSS []   H6 null
  H7 {"answers_live": 134, "api_requests": 134, "day_asks": {"3": 40, "4": 38, "5": 40}}
seed 3:
  H2_DAYS {"3": [["19:00", true, "daniel", null]], "4": [["19:00", true, "elena", null]], "5": [["19:00", false, null, "no trip position today"]]}
  H2_TRIP_ACTS {"3": [3 acts], "4": [5 acts], "5": []}
  H3 [[3, "Daniel", "model"], [4, "Daniel", "model"]]
  H4 {"prompts_scanned": 141, "far_as_will_not_go": [], "nobody_after_a_trip": [], "trips_before": {"3": true, "4": true, "5": true}}
  H5_FOOD [{"night": 4, "took": [[["daniel"], 4, true]], "food_acts": [["min 00", "Daniel", "eat"], ["min 00", "Elena", "share"]], "holds": true}]
  H5_LOSS []
  H6 {"of": 24, "fresh": 0, "holds": false, …}
  H7 {"answers_live": 141, "api_requests": 141, "day_asks": {"3": 40, "4": 48, "5": 28}}

SUMMARY runs/v20
H2 PASS (Q5 days 3 of 6; trip acts in Q5 9)
H3 PASS
H4 PASS (far as 'will not go': 0; 'nobody' after a trip: 0)
H5 PASS (food: PASS; loss: NOT TESTED)
H6 FAIL
H7 PASS (live 275)
$ … h_score.py --account > runs/v20/scoring/account.txt; … h_score.py --lines > runs/v20/scoring/lines.txt
```
- **The replay's "exit 1"** is `morning.py:326-328`: its temp folder holds no original story to compare with. It
  replayed every cached and live answer: 230 = 96 + 134, and 276 = 135 + 141.
- **H1** is the hand count of §4.

**5. At the end** (`runs/v20/scoring/end_checks.txt`, `runs/v20/scoring/cachecheck.txt`):
```
checked_utc: 2026-10-08T10:16:18Z
8a52064aadb49ff71ea192d2c849356e0a222f25c53c85798aa1aab27e30dd98 *reports/days_v20_plan.md      (as recorded)
(the *.py and config.json sha256s of plan_frozen.txt) | sha256sum -c     20 OK
cache/v16 seed2: OK, seed3: OK
git status --short: ?? cache/v20/  ?? reports/days_v20_plan.md  ?? runs/v20/  (and runs/v6's three replay files)
git diff --stat: (empty)
seed 2: v16 entries 147, v20 entries 281, all v16 kept unchanged True, new 134
seed 3: v16 entries 184, v20 entries 325, all v16 kept unchanged True, new 141
```
