# v19: v16 seeds 2 and 3, days 3 to 5, with stage B

Mode: run. The plan is `reports/days_v19_plan.md`, recorded before any live call (`runs/v19/plan_frozen.txt`). The
code is HEAD `e49aadc` (stage B, stage B fixes, multi-day). No code, test or plan line was edited. Paths are
relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/v19/`, and the scoring outputs in
`runs/v19/scoring/`.

## Result

| # | Prediction | Verdict | Evidence |
|---|---|---|---|
| G1 | ≥ 1 of 2 seeds: someone chooses `go_further` at a bedtime on night 3 or 4 | **PASS** | Seed 3, night 3: Daniel (model). Seed 2: none. Every bedtime there was `lie_awake`. |
| G2 | ≥ 1 day speech act is `propose_far` or `volunteer_far` | **PASS** | 14 in all. Seed 2: 9 (day 4: 3; day 5: 6), by Daniel and Mara. Seed 3: 5 (day 3: 1; day 4: 4), all Daniel's. |
| G3 | A trip brings food home → the next day has ≥ 1 model act that eats, shares or gives | **NOT TESTED** | No food came home. Seed 3's one trip found house 1 empty: "Found 0 portions there; took 0". Seed 2 had no trip. The shelf held 0 portions every morning, days 3–5, in both seeds. |
| G4 | Someone does not come back → next day ≥ 2 others name them | **NOT TESTED** | Nobody was lost. `away` is empty after nights 3 and 4 in both seeds. |
| G5 | Every seed with a night-3 trip: ≥ half of day 4's morning speech acts use a pair new to day 3's morning | **FAIL** | Seed 3 only (seed 2 had no trip on night 3): **0 of 24**. Every day-4 morning pair was already used on day 3's morning. |
| G6 | Nobody who knows next door is empty chooses `go_next_door` | **PASS** | 12 knower bedtimes (Daniel, Leo and Mara, nights 3 and 4, both seeds). Choices: `lie_awake` 9, `go_further` 1, `sleep` 1, `watch_door` 1; `go_next_door` 0. |
| G7 | Live asks ≤ 360 in total; every day ≤ 40 asks | **PASS** | 136 + 132 = **268** live. Day asks: seed 2: 40, 40, 40; seed 3: 32, 40, 40. |

**DONE:**
- **The plan.** It was recorded at **2026-10-07T21:10:39Z**, sha256 `c8cb0219…2a65d49`. The first live call came
  after it: seed 2 started at 21:11:40Z. At the end (21:48:26Z) the sha256 is the same, and the 19 `*.py` sha256s are
  unchanged (§5).
- **Exit codes.** Both seeds exited 0.
- **Verdicts.** All 7 predictions have one: 4 PASS, 1 FAIL, 2 NOT TESTED.

## 1. Asks per day, per seed

From `runs/v19/daniel_ate_it-seed{2,3}.meta.json` (`runs/v19/scoring/asks.txt`). Days 1–2, nights 1–2 and minds 1–2
were all answered from the cache: 96 answers for seed 2, 135 for seed 3. Every ask from day 3 on was live.

| Seed | Day 3 | Night 3 | Mind 3 | Day 4 | Night 4 | Mind 4 | Day 5 | Live | API requests |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 40 | 4 | 4 | 40 | 4 | 4 | 40 | 136 | 141 (5 retries after a 503) |
| 3 | 32 | 8 | 4 | 40 | 4 | 4 | 40 | 132 | 132 |

**When each day's 40 asks ran out** (the first "day asks 40 of 40" line in each stdout), and the day's last model act:

| Seed | Day 3 | Day 4 | Day 5 |
|---|---|---|---|
| 2 | 20:12 | 19:00 | 11:09 |
| 3 | not reached (32); last act 10:51 | 11:00 | 11:57 |

- **After that minute, no one was asked again that day.** Seed 2's day 5 and seed 3's days 4 and 5 then run to 21:00
  with no model acts.
- **Seed 3's day 3** stopped at 32 asks because nothing fired after 10:54. Its later Q2s were "not asked (they met
  this way at 10:48 already today)", at 12:48 and 16:45 (`runs/v19/daniel_ate_it-seed3.stdout.txt`).

## 2. Seed 2

**Who knows next door is empty:** Daniel, Leo and Mara. Elena does not: her bedtimes offer 4 options, with no
`go_further`. Nobody went out on night 3 or 4.

### Day 3 (shelf 0; the morning to min 12; stretches at 10:21 Q2, 10:27 Q1, 20:09 Q1)
- **The talk.** All 40 speech acts are `accuse_daniel`, `confront_daniel`, `confront_leo` or `reassure_all`. They
  are about Daniel's trip next door on night 2, for example:
  - min 00, Leo: "Daniel went out in the night and came back with nothing, just like before."
  - 20:12, Leo: "You went out there last night and came back with nothing, Daniel. Stop pretending you have any idea how to fix this."
- **The houses further along:** no line mentions them, and nobody chose `propose_far` or `volunteer_far`.
- **Food:** none on the shelf, and no food act.

### Night 3
- **Bedtime: all four `lie_awake`.**
  - Daniel: "I am too weak and dizzy to go out again tonight, so I will lie here and listen to make sure everyone stays safe."
  - Elena: "… make sure no one tries to sneak out into the dangerous night."
  - Leo: "I cannot sleep while Daniel pretends nothing is wrong and our safety is at risk."
  - Mara: "I am too weak and dizzy to stand, so I will lie here in the dark and listen for anyone moving."
- **Trips: none.** The shelf stayed at 0; nobody was lost; nobody dozed.

### Day 4 (shelf 0; the morning to min 21; stretches at 11:00 Q2, 15:30 Q1, 19:00 Q1)
- **The morning.** It turns back to the can.
  - min 00, Mara: "Easy for you to say everything is fine when you were the one who took the food."
  - min 00, Daniel: "Mara, stop saying that, I already told you I didn't take anything."
  - min 00, Leo: "Daniel, you admitted taking it three days ago, so stop lying to her." Daniel's admission is on day 1:
    "I took it in the night, I'm sorry." (`runs/v19/daniel_ate_it-seed2.md:116`).
- **The houses further along**, quoted whole:
  - min 15, Daniel [`volunteer`, the next-door option]: "I will go out further along the street to find food for us tonight."
  - min 15, Mara [`propose_far`]: "We should go to the houses further along the street instead of just the neighbour's house."
  - 11:06, Daniel [`volunteer_far`]: "I told you I would go further down the street, and I am the one who is going."
  - 19:00, Daniel [`propose_far`]: "We can't just sit here and wait, someone has to try the houses further along the street tonight."
  - 19:00, Elena [`nobody_goes`]: "Nobody is going out into the street tonight, it is far too dangerous for us."
- **Food:** none, and no food act.

### Night 4
- **Bedtime: all four `lie_awake` again.**
  - Daniel: "I cannot rest while there is no food and Mom forbids us from going out, so I must stay awake and protect them."
  - Leo: "I am too weak to stand and going out into the dark is suicide, so I will stay here and listen."
  - Mara: "My head is spinning from hunger and I am too awake and angry to sleep while everyone else gives up."
- **Trips: none.** Shelf 0; nobody lost.

### Day 5 (shelf 0; the morning to min 18; stretches at 10:21 and 11:06, both Q2; asks spent at 11:09)
- **The houses further along**, quoted whole:
  - min 03, Daniel [`propose_far`]: "We cannot stay here doing nothing, someone has to try the houses further along the street."
  - min 06, Daniel [`volunteer_far`]: "I told you I'll go further along the street myself, and that's final."
  - min 06, Mara [`propose_far`]: "If nobody is going next door, someone should try the houses further along the street."
  - min 09, Daniel [`propose_far`]: "I am telling you, we have to look further down the street if we want to survive this."
  - min 09, Mara [`volunteer_far`]: "If no one else will do it, I will go look at the houses further down the street myself."
  - min 15, Daniel [`volunteer_far`]: "I told you, I am going further down the street to find us something, and that is final."
- **The answers:**
  - min 06, Elena [`keep_daniel_home`]: "Daniel, please listen to your brother and stay here with us."
  - min 09, Elena [`keep_mara_home`]: "Mara, you cannot go out there, it is far too dangerous for you."
  - min 15, Leo [`keep_daniel_home`]: "You are not going anywhere down the street, Daniel, because staying alive here is hard enough without your reckless plans."
- **From 10:21,** the talk is Daniel and Mara over the can. The last act is at 11:09, Mara: "Daniel, you took it and
  you know it, so stop acting like you care about any of us."
- **Food:** none, and no food act. Day 5 is the last day: there is no night 5.

## 3. Seed 3

**Who knows next door is empty:** Daniel, Leo and Mara. Elena's bedtimes have no `go_further`.

### Day 3 (shelf 0; the morning to min 18; one stretch at 10:48, Q2; 32 asks)
- **The talk is about Daniel going out again.** He volunteers and keeps to it (`volunteer`, `volunteer_far`,
  `still_going`). Elena answers `nobody_goes` and `keep_daniel_home`; Leo and Mara answer `confront_daniel` and
  `keep_daniel_home`.
- **The houses further along**, quoted whole:
  - min 06, Daniel [`volunteer_far`]: "I'll go further down the street tonight. We need to find something."
  - min 06, Elena [`keep_daniel_home`]: "Daniel, you are not going out into the street tonight, we cannot lose you."
  - min 09, Daniel [`volunteer`]: "I already went last night, so I'm the one who should go out further today."
  - 10:48, Leo [`confront_daniel`]: "You went out into the dark last night and came back empty handed, Daniel. Doing it again won't change the empty houses."
- **The last act** is at 10:51, Mara: "Daniel, you can't just sneak out and pretend nothing happened when we are all
  starving."
- **Food:** none, and no food act.

### Night 3 (`runs/v19/daniel_ate_it-seed3.md:997`)
- **Bedtime.**
  - Daniel: **`go_further`**: "I have to find food for my family further down the street since the neighbour's house had nothing."
  - Elena, Leo, Mara: `lie_awake`. Leo: "I cannot rest while Daniel continues to put us all at risk by sneaking out into the street."
- **In the night.**
  - Leo sees Daniel get up: `stop_daniel`, "Don't go out there, Daniel. It's suicide."
  - Daniel: `go_anyway`, "I have to do this, Leo, stay back."
  - Elena hears the front door: `stay_in_bed`.
  - Mara hears it: `get_up_and_look`, and waits by the front door. She sees who comes back.
- **The trip.** Daniel goes alone, further along the street (house 1, the first further house). Street draw 0.106 →
  clean. "Found 0 portions there; took 0. Outcome: **back with nothing**." `far` is
  `{houses: [0], searched: 1}`.
- **By morning:** shelf 0 → 0, nobody lost.

### Day 4 (shelf 0; the morning to min 18; stretches at 09:57 and 10:57, both Q2; asks spent at 11:00)
- **The houses further along**, quoted whole:
  - min 00, Daniel [`volunteer_far`]: "I went out past the neighbour's house last night to look further down the street, and I will go again tonight if we need to."
  - min 12, Daniel [`volunteer_far`]: "I already went out there and I'm going back tonight to find something for us."
  - 09:57, Daniel [`volunteer_far`]: "I went out last night and I am telling you I can find something further down the street."
  - 10:57, Daniel [`volunteer_far`]: "I went out last night and I am going to check the houses further down the street again tonight."
- **The others answer as on day 3:**
  - min 00, Mara [`confront_daniel`]: "You sneaked out into the dark street last night while we were sleeping, Daniel, and you came back with nothing."
  - min 03, Leo [`keep_daniel_home`]: "You stayed home last night because it was suicide, Daniel, and nothing has changed tonight." The record has
    Daniel going out on night 3 after Leo's "It's suicide".
  - min 15, Daniel [`volunteer`]: "I survived out there twice, and I'll do it again to keep us alive." He went out on nights 2 and 3.
  - 11:00, Elena [`keep_daniel_home`]: "Daniel, you must stay home tonight."
- **G5's count.** 24 morning speech acts: Daniel `volunteer_far`, `volunteer` and `still_going`; Elena
  `keep_daniel_home`, `nobody_goes` and `confront_daniel`; Leo `confront_daniel`, `keep_daniel_home` and
  `nobody_goes`; Mara `confront_daniel` and `accuse_daniel`. Every one of their pairs was used in day 3's morning.
- **Food:** none, and no food act.

### Night 4 (`runs/v19/daniel_ate_it-seed3.md:1387`)
- **Bedtime.**
  - Daniel: **`sleep`**: "My legs cannot carry me any further tonight and I have nothing left to give."
  - Elena: `lie_awake`.
  - Leo: `lie_awake`: "I am too weak to stop him if he sneaks out again, so I will listen in the dark."
  - Mara: **`watch_door`**: "I will not let Daniel sneak out into the dark again while we starve."
- **The night.** "Nobody got up. The night passed." Shelf 0; nobody lost.

### Day 5 (shelf 0; the morning to min 18; stretches at 09:57 Q2, 10:33 Q2, 11:57 Q1; asks spent at 11:57)
- **Daniel's offers are next door now** (`volunteer`, `propose_trip`, `still_going`). No line names the houses
  further along:
  - min 00, Daniel [`volunteer`]: "I am the oldest, so I will go out to the neighbour's house tonight and find us something."
  - min 09, Daniel [`propose_trip`]: "I am the eldest, and I will go to the neighbour's house tonight to find what we need."
- **The others refuse him** (`keep_daniel_home`, `nobody_goes`, `confront_daniel`):
  - min 03, Leo: "Daniel, you went three days ago and came back empty-handed, and you're not going again tonight."
    The record has his far trip on night 3, the night before last.
  - min 15, Leo: "Daniel, you nearly got Mara killed last time, and staying here is the only safe choice." No night's
    groups include Mara (nights 1–4, `runs/v19/daniel_ate_it-seed3.transcript.json`).
  - 11:57, Mara [`nobody_goes`]: "Mom is right, nobody is going out there tonight." This is the day's last act.
- **Food:** none, and no food act.

## 4. What the run shows, by the counts

- **Bedtimes.** Of 16 bedtime choices on nights 3–4, 1 went out (seed 3, Daniel, night 3). The others were 13
  `lie_awake`, 1 `sleep` (seed 3, Daniel, night 4) and 1 `watch_door` (seed 3, Mara, night 4). In seed 2, Daniel
  and Mara spoke for the houses further along by day on days 4 and 5 (`propose_far` or `volunteer_far`: 9 acts).
  Neither chose `go_further` at either bedtime.
- **The one far trip** drew an empty house (`far_house:0` gave 0). The shelf held 0 portions on every morning of
  days 3–5 in both seeds.
- **Food and loss.** No model act ate, shared or gave on days 3–5: no food was offered, because the shelf was empty.
  Nobody was lost, so G3 and G4 had nothing to test.
- **Day 4's morning in seed 3** repeated day 3's morning's act kinds and targets: 0 of 24 new pairs.
- **The asks.** Each day's 40 ran out at 11:00, 11:09 or 11:57 on three of the six days. On those days no one was
  asked again before bedtime.

## 5. Commands and output

All from `Prototypes/llm-morning/`. Only the two live runs had `GEMINI_API_KEY` set.

**1. The plan record** (`runs/v19/plan_frozen.txt`, which also holds `git status --short`, `git diff --stat`, empty,
and every `*.py` sha256):
```
recorded_utc: 2026-10-07T21:10:39Z
c8cb0219b5ebaf5a3ef100809156e62ed29041b3ec530ebd0ed427b0f2a65d49 *reports/days_v19_plan.md
$ git rev-parse HEAD
e49aadc2f8a4e9a1a7898b7189efb5c97b9dbc45
```
The scorer `runs/v19/scoring/g_score.py` was written next, before any live call. It was checked on the stage B
fake runs, with no API (`… g_score.py runs/stage_b_fake/food/run 2`, then `…/lost/run 2`). Both ran to their
SUMMARY.

**2. The copy, and where each seed first misses** (`runs/v19/cache_copy.sha256.txt`,
`runs/v19/premiss-seed{2,3}.stdout.txt`). `premiss.py` runs `morning.run(seed, replay=True, out="v19", days=5)`
and prints the first prompt with no cached answer.
```
$ mkdir -p cache/v19 && cp cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{2,3}.json cache/v19/
$ sha256sum cache/v16/*seed{2,3}.json cache/v19/*seed{2,3}.json      # pairwise equal: d79a4939…, 25e92cc7…
$ for n in 2 3; do env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v19/scoring/premiss.py $n > runs/v19/premiss-seed$n.stdout.txt 2>&1; echo "seed $n exit $?"; done
seed 2 exit 3
  night 2, the night mind: model asked for 4; so far 0 live, 96 cached, 0 API requests
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']; first 'min 00' line: ['- min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)']
stopped: replay found a prompt with no cached answer, so this morning cannot be replayed from the cache.
seed 3 exit 3
  night 2, the night mind: model asked for 4; so far 0 live, 135 cached, 0 API requests
FIRST MISS: scene index 6, speaker Daniel; Now line: ['Now, minute 00, you are in the kitchen.']; first 'min 00' line: [same]
$ sha256sum -c runs/v19/cache_copy.sha256.txt        # 4 OK
```
- **Scene index 6 is day 3.** The scenes are day1, night, mind1, day2, night2, mind2, day3, counted from 0.
- **These are stage B fixes' points** (`reports/stage_b_fixes.md`, DONE 3): Leo for seed 2, Daniel for seed 3.

**3. The runs,** one after the other (`runs/v19/daniel_ate_it-seed{2,3}.stdout.txt`; start times and exit codes
in `runs/v19/seed{2,3}.started_utc.txt`):
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u morning.py --seed 2 --out v19 --days 5 > runs/v19/daniel_ate_it-seed2.stdout.txt 2>&1
started 2026-10-07T21:11:40Z   exit 0
  api_requests: 141  answers_live: 136  answers_from_cache: 96  day3 day_asks: 40  day4 day_asks: 40  day5 day_asks: 40
    [503 UNAVAILABLE] waiting 5s, retry 1/6    (5 retries in all, each answered on its next try)
$ … morning.py --seed 3 --out v19 --days 5 > runs/v19/daniel_ate_it-seed3.stdout.txt 2>&1
started 2026-10-07T21:37:11Z   exit 0
  api_requests: 132  answers_live: 132  answers_from_cache: 135  day3 day_asks: 32  day4 day_asks: 40  day5 day_asks: 40
```
- **The quota question.** Before seed 3, I put it to you: by my count about 355 of the day's 500 requests were
  already used (v17 121, v18 62, probe_far 31, v19 seed 2 141). You chose to start seed 3 at once. It ran without a
  quota refusal.
- **The 360 watch.** Live asks reached 268 in total. No process was stopped.

**4. Scoring** (`runs/v19/scoring/score_v19.txt`; the day and night account in `runs/v19/scoring/account.txt`; the
lines on the houses further along in `runs/v19/scoring/far_lines.txt`; asks in `runs/v19/scoring/asks.txt`):
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v19/scoring/g_score.py > runs/v19/scoring/score_v19.txt
exit 0
seed 2:
  G1 []
  G2 [9 acts: day 4 min 15 Mara propose_far; 11:06 Daniel volunteer_far; 19:00 Daniel propose_far; day 5 min 03, 06, 06, 09, 09, 15]
  G3 []
  G4 []
  G5 null
  G6 {"knower_bedtimes": [[3, "Daniel", "lie_awake"], [3, "Leo", "lie_awake"], [3, "Mara", "lie_awake"], [4, "Daniel", "lie_awake"], [4, "Leo", "lie_awake"], [4, "Mara", "lie_awake"]], "violations": []}
  G7 {"answers_live": 136, "api_requests": 141, "day_asks": {"3": 40, "4": 40, "5": 40}}
seed 3:
  G1 [[3, "Daniel", "model"]]
  G2 [5 acts: day 3 min 06; day 4 min 00, min 12, 09:57, 10:57; all Daniel, volunteer_far]
  G3 []
  G4 []
  G5 {"day3_pairs": ["('accuse', 'daniel')", "('confront', 'daniel')", "('object', 'daniel')", "('object', None)", "('propose', None)", "('reassure', 'daniel')", "('volunteer', None)", "('volunteer_far', None)"], "of": 24, "fresh": 0, "holds": false, …}
  G6 {"knower_bedtimes": [[3, "Daniel", "go_further"], [3, "Leo", "lie_awake"], [3, "Mara", "lie_awake"], [4, "Daniel", "sleep"], [4, "Leo", "lie_awake"], [4, "Mara", "watch_door"]], "violations": []}
  G7 {"answers_live": 132, "api_requests": 132, "day_asks": {"3": 32, "4": 40, "5": 40}}

SUMMARY runs/v19
G1 PASS
G2 PASS
G3 NOT TESTED
G4 NOT TESTED
G5 FAIL
G6 PASS
G7 PASS
live asks in total 268
$ … g_score.py --account > runs/v19/scoring/account.txt                   exit 0
```
The G2 lists are shortened here; each act is quoted whole in §2 and §3, and in `score_v19.txt`.

**5. At the end** (`runs/v19/scoring/end_checks.txt`, `runs/v19/scoring/cachecheck.txt`):
```
checked_utc: 2026-10-07T21:48:26Z
$ sha256sum reports/days_v19_plan.md
c8cb0219b5ebaf5a3ef100809156e62ed29041b3ec530ebd0ed427b0f2a65d49 *reports/days_v19_plan.md      (as recorded)
$ (the *.py sha256s of plan_frozen.txt) | sha256sum -c     19 OK, 0 failed
$ sha256sum -c (cache/v16 lines of cache_copy.sha256.txt)    cache/v16 seed2: OK, seed3: OK
$ git status --short     ?? cache/v19/  ?? reports/days_v19_plan.md  ?? runs/v19/  (and runs/v6's three replay files, untracked before)
$ git diff --stat        (empty)
seed 2: v16 entries 147, v19 entries 283, all v16 kept unchanged True, new 136
seed 3: v16 entries 184, v19 entries 316, all v16 kept unchanged True, new 132
```
