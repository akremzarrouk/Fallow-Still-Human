# v22: W1's live run, v16 seed 2, days 3 to 10

Mode: run. The plan is `reports/days_v22_plan.md`, recorded before any live call (`runs/v22/plan_frozen.txt`). The code is
HEAD `a4edf84` (W1, its fixes, and block C's went_out line). No code, test or plan line was edited. The control is v21
(`reports/days_v21.md`). Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/v22/`, the scoring
outputs in `runs/v22/scoring/`, the scorer and its checks in `runs/w22/scoring/`. Clock stamps are the run's own
("min 75", "10:24"), as in the transcript.

## Result

| # | Prediction | v21 | v22 | Verdict |
|---|---|---|---|---|
| W1-1 | ≥ 3 outward acts, on ≥ 2 different nights | 1 (N5 `got_up`) | **1**: N5, Daniel `went_out`. One night. | **FAIL** |
| W1-2 | ≤ 8 of 28 bedtime reasons match FROZEN | 16 of 28 | **6 of 28** (nights 3, 4, 7, 8, 8, 9) | **PASS** |
| W1-3 | ≥ 2 bedtime `go_next_door` / `go_further` | 1 | **1** (N5 Daniel `go_next_door`) | **FAIL** |
| W1-4 | WATER speech acts on ≥ 4 of 8 days | 0 acts, 0 days | **12 acts on 4 days** (days 6, 7, 8, 9: 8, 2, 1, 1) | **PASS**, at the threshold |
| W1-5 | (a) every awake person hears each rain start, 100%; (b) the first spell's Q6 stretch holds a `collect_rain` or a rain word | no weather | (a) **100%** over 2 spells (day 7 17:18, day 9 11:30); (b) **does not hold**; `collect_rain` 1, `rain_out` 0 | **FAIL** |
| W1-6 | ≤ 1 "no water" claim while the store is > 0 | 0 | **0** claims | **PASS** |
| W1-7 | store < 50 L on day k ≤ 9 → a ration or save act by 21:00 of day k + 1 | no water | below 50 L on **day 5**; first act **day 9, 11:33** (Leo `ration_water`) | **FAIL** |
| W1-8 | live asks ≤ 450; each day ≤ 56; largest estimate ≤ 2600 | 337; ≤ 40; 2435 | **402**; ≤ 48; **2602** | **FAIL**, by 2 tokens |
| W1-9 | 0 "Your body:" lines match `impossible\|cannot\|can't\|unable\|barely (stand\|walk\|move)` | stage 3 lines match (141 of 337) | **0 of 402** | **PASS** |
| W1-10 | CAN ≤ 20% of speech acts | 63 of 245 = 25.7% | **38 of 326 = 11.7%** | **PASS** |
| W1-11 | a `went_out` night has a leaver whose bedtime reason or trip words that day match WATER | no trip | N5, Daniel: reason and trip words have no water word | **FAIL** |

**5 PASS (W1-2, 4, 6, 9, 10), 6 FAIL (W1-1, 3, 5, 7, 8, 11), 0 NOT TESTED.**

**The section-8 test of the idea, by the counts:** W1-1 and W1-3 both fail and W1-2 holds. That is the case
`reports/world_design.md:814-816` names ("honest words alone do not move the house, and W1-4's water talk is talk
without acts"). In W1-4's 12 acts, 9 are about the 9 L Daniel carried home on night 5, and 3 about the house's own
water or rain (§8).

**DONE:**
- **The plan.** Recorded at **2026-10-08T19:59:11Z**, sha256 `eb3758cc…a3a6bf` (full in §9). The first live ask was at
  day 3 min 00, the run started at **20:04:14Z**. At the end (20:35:48Z) the sha256 is the same, and the 23 code and
  config sha256s of `plan_frozen.txt` are unchanged (23 OK). `git diff --stat` is empty; no tracked file is modified.
- **The scorer.** It reproduces v21's column on all 11 rows (`ALL MATCH`, §9, command 3). A fake 10-day run exercises
  it, and 35 checks on edited copies of that fake exercise the rules the fake never reaches (§9, command 4).
- **The exit.** The run exited **0** (`echo "exit $?"` after the process, `runs/v22/seed2.exit.txt`). The cap (470) was
  not reached: **402** live asks. Stderr is empty.
- **Verdicts.** All 11 predictions have one.

**What differed from the plan's wording:**
- **The key.** The run used an API key the user gave in chat for this one run, as `GEMINI_API_KEY` for that process
  only. `grep -rl` for it over the repository finds it in no file.
- **The start.** Through `runs/v22/run_capped.py` (cap 470), `morning.main()` with `--seed 2 --out v22 --days 10`. The cap
  was not reached.
- **Three 503s.** `[503 UNAVAILABLE]` three times (stdout lines 180, 181, 192), each retried; `api_requests` 405 for 402
  answers. No 429; no ask lost.
- **The scorer's path.** `runs/w22/scoring/w1_score.py`, as the brief says (the design said `runs/w1/scoring/`).
- **W1-8's marker.** The plan marks it "restated": the design already had 56 a day.
- **W1-9's prompts.** Read from the cache file's 402 live prompts (day, night and night-mind), not from a replay: a
  superset of the plan's day and night prompts, with the same body lines. A replay (`runs/v22/scoring/replay_max.txt`)
  gives the same 402 prompts from day 3 on and the same largest estimate.

## 1. Asks per day

From `runs/v22/daniel_ate_it-seed2.meta.json`. Days 1–2, nights 1–2 and minds 1–2 came from the cache: 96 answers. Every
ask from day 3 on was live: **402** (`answers_live` 402, `answers_from_cache` 96, `api_requests` 405). Run time 1875 s
(31.3 min).

| Day | Day asks | Night after | Mind after | Stretches (trigger: asks) | Morning ends |
|---|---|---|---|---|---|
| 3 | 40 | 4 | 4 | morning 24, Q2 8, Q1 8 | min 21 |
| 4 | 40 | 4 | 4 | morning 24, Q2 8, Q5 8 | min 21 |
| 5 | 40 | 8 | 4 | morning 24, Q2 8, Q5 8 | min 18 |
| 6 | 40 | 4 | 4 | morning 24, Q2 8, Q2 8 | min 21 |
| 7 | 42 | 4 | 4 | morning 22, Q2 6, Q2 6, **Q6 8** | min 18 |
| 8 | 48 | 4 | 4 | morning 24, Q2 8, Q1 8, Q5 8 | min 18 |
| 9 | 48 | 4 | 4 | morning 24, Q2 8, **Q6 8**, Q5 8 | min 18 |
| 10 | 44 | — | — | morning 24, Q2 6, Q2 6, Q5 8 | min 18 |
| Sum | 342 | 32 | 28 | | |

342 + 32 + 28 = 402. Night 5 has 8 asks: its 4 bedtime choices, Leo's `stop_daniel`, Daniel's `go_anyway`, and
Elena's and Mara's reactions. Q6 fired twice (days 7 and 9). The day that had the most asks has 48, under the 56 of
W1-8. Day asks by day in v21 were 30 to 40.

## 2. Each day and night

**The bodies, every day.** Nobody ate, shared or gave on any day (`runs/v22/scoring/account.txt`: no food act), and the
shelf was 0. The fasting hours are therefore v21's table (`reports/days_v21.md` §2), e.g. Daniel 75.9 at 21:00 on day 3 and
269.1 on day 10. **Thirst: every person was at stage 0, "short 0.00 L", at 21:00 on every day.** Stage crossings from
the transcript's need events:

| Fasting stage (hours) | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| 2 ("light and slow", ≥ 72 h) | day 3, 17:39 | day 5, 19:45 | day 3, 19:00 | day 4, 11:42 |
| 3 ("thin and weak", ≥ 168 h) | night 6 (170.2 h at 07:00 of day 7) | day 10, 12:39 | day 7, 19:00 | day 8, 16:45 |

"You feel cold, even indoors" is in the body lines from night 4 (17.2 °C indoors, under 18) for those at stage 2.

**The water, every day** (the World's log, `quiet.water`, litres; tap = the stored tap water, bin = rain water):

| Day | Weather | Tap, 07:00 → 21:00 | Bin | Level |
|---|---|---|---|---|
| 3 | dry, 18.4 °C indoors | 105.5 → 91.5 | — | as_before |
| 4 | dry, 17.2 | 81.5 → 67.5 | — | as_before |
| 5 | wet 12.3 mm from 22:03 | 57.5 → 43.5 | — | as_before |
| 6 | wet 4.5 mm, raining at 07:00 | 42.5 → 37.8 | set out at 07:00; 67.1 at 21:00 | as_before |
| 7 | wet 1.2 mm (04:36–10:09, 17:18–20:21) | 34.5 → 29.8 | 66.0 → 76.6 | as_before |
| 8 | dry, 17.5 | 26.5 → 21.8 | 69.9 → 60.6 | as_before |
| 9 | wet 17.8 mm (11:30–16:30) | 18.5 → 15.0 | 53.9 → **240.0** (full) | **rationed at 11:33** |
| 10 | dry, 17.6 | 12.9 → 10.0 | 240.0 | rationed |

The drinking store (tap + bin) first read below 50 L at day 5, 21:00 (43.5 L), and after day 6's rain it was 104.9 L at
21:00.

**Day 3.** Dry. Morning to min 21; Q2 at 10:30; Q1 at 17:39 (Daniel). The talk is Daniel's night-2 trip. No water, rain
or trip words.
- Mara (min 00): "You went out into the night and came back with nothing, Daniel. Why did you even go?" (the same
  line 7 times in the morning).
- Daniel (min 03): "I went to see what was there so we wouldn't have to guess, and I will keep us safe."
- Leo (10:33): "You snuck out alone last night and came back empty-handed just like I knew you would, Daniel."

**Night 3.** Daniel `lie_awake`, Elena `sleep`, Leo and Mara `lie_awake`. All four were offered `go_next_door` and
`go_further`. Nobody got up. Leo's reason (FROZEN): "I am too weak to go out again, but I need to stay alert if Daniel
tries to leave in the dark once more." Mara: "I cannot sleep knowing Daniel might sneak out again into the dark."

**Day 4.** Dry. Q2 at 11:00, Q5 at 19:00 (Mara). **Trip talk begins: 12 trip-position acts** (v21 had none on day 4).
- Mara (min 06, `propose_trip`): "Daniel went into the dark before, so one of us has to check the neighbour's house
  tonight."
- Daniel (min 09, `still_going`): "I am the oldest, and I am going whether you like it or not."
- Leo (min 09): "You are not going anywhere tonight, Daniel, because it is suicide and you know it."
- Daniel (min 15, `volunteer_far`): "I will go further down the street myself to find what we need."

**Night 4.** All four `lie_awake`. Leo (FROZEN): "I have no strength left to go out tonight, so I will lie awake and
listen." Daniel: "I cannot sleep while my family is starving and I carry the weight of what I did." No trip.

**Day 5.** Wet from 22:03 that night. Q2 at 10:03, Q5 at 19:00 (Daniel). **21 trip-position acts** (v21's 21).
Daniel `still_going` 6 times.
- Daniel (min 06): "I will go out tonight to check the neighbor's house again, because I am the oldest and it's my duty to
  keep us safe."
- Elena (min 06): "Daniel, you must stay home tonight. We cannot risk losing you out there in the dark."
- Leo (19:00): "Daniel, you went before and found nothing, and going out again will just get you killed."
- Daniel (19:03): "I have to go out and find something for us, no matter what you all say."

**Night 5: the one trip.** A rainy night (22:03 to 03:42; the front-door draws are halved). Bedtimes: **Daniel
`go_next_door`** ("I must go out to find food tonight because I am the oldest and it is my duty to protect them."),
Elena, Leo and Mara `lie_awake`. Daniel got up. The house answered, in order:
- Leo, `stop_daniel`: "Daniel, stop. You are not going out there."
- Daniel, **`go_anyway`**: "I have to do this, Leo, so move aside and let me go." (v21: `stay_home`, "I am too weak
  anyway".)
- Elena, `stay_in_bed`: reason "I will lie here and pray he turns back before the dark takes him." Mara,
  `get_up_and_look`.
- The street: `scare_back`. Nothing found; **9 L of water carried home** (seed 2's neighbour holds 9 L: an empty bath,
  the cistern, two bottles). Outcome: "back shaken, with water". No food came home.

**Day 6.** Rain already falling at 07:00. **The one `collect_rain` of the run**, the first ask of the day:
- Daniel (min 00, `collect_rain`): "It's raining out, I'm setting the bin under the drainpipe to catch water."
  The bin caught 67.1 L by 21:00. No other prompt of the run offered `collect_rain` (the option goes when the bin is out).
- Leo (min 00): "You brought back water in the dark while everyone was asleep, Daniel, so don't pretend you were just
  resting."
- Daniel (min 03): "I risked my life in the dark for that water, Leo, so stop accusing me when you stayed safely in bed."
- Elena (min 06): "Leo, your brother came back safe with the water, so let us try to calm down and listen to each other."
- Leo (min 15, `go_kitchen`): "I heard rain on the roof, so we should check the yard bin before it misses any water."
- No trip positions. 8 of the run's 12 WATER acts are here.

**Night 6.** All four `lie_awake`. Elena: "I need to listen through the night to protect my children from slipping out into
the dark again." No trip.

**Day 7.** Wet: 04:36–10:09 (already falling when the day began) and **17:18–20:21**. Q6 at 17:18, **4 asked**. Leo
reaches stage 3 (19:00). Daniel's body line has changed to "thin and weak".
- Daniel (min 09): "Mara, stop accusing me when I'm the one who went out into the dark to bring back water for all of us."
- The Q6 stretch (17:18–17:24, 8 asks) is the day's argument continuing: Mara "You took the can, Daniel, and you're the
  reason we have nothing left."; Elena "Please, let us not fight anymore…"; Leo "Risking your life doesn't give you the
  right to put everyone else in danger by sneaking out without a word, Daniel." **No rain word, no `collect_rain`** (the
  bin was already out).
- Daniel (17:21): "Leo, you weren't out there in the dark risking your neck to bring back water for us."

**Night 7.** Daniel, Elena, Mara `lie_awake`; Leo `sleep` ("I have no strength left to stay awake, so I need to sleep and
save what little energy I have."). Mara (FROZEN): "I am too weak and cold to get up, so I will lie here in the dark and
listen." No trip.

**Day 8.** Dry. Q2 at 09:51, Q1 at 16:45 (Mara, stage 3), Q5 at 19:00 (Elena). **24 trip-position acts**, Daniel
`still_going` 7 times.
- Leo (min 09): "Bringing back water doesn't erase the fact that you lied to us and stole the food."
- Daniel (min 12, `volunteer`): "I will go out there myself tonight and find us something to eat."
- Leo (16:45): "You are not going out there tonight, Daniel. We agreed on this."
- Daniel (19:03): "I am the oldest, and I am the one who is going out there tonight."

**Night 8.** Daniel `sleep` (FROZEN): "I am too weak and tired to make it out there tonight." Elena, Leo, Mara `lie_awake`
(Mara, FROZEN: "I am too weak and tired to go out, but I will lie here awake and listen in the dark."). No trip.

**Day 9.** Wet 11:30–16:30, 17.8 mm. **31 trip-position acts**, Daniel `still_going` 7 times. Q6 at 11:30: **3 asked**
(Elena, Leo, Mara; Daniel was resting from 10:27 to 11:33). The bin reaches its 240 L.
- Daniel (min 06, `propose_trip`): "We can't just sit here arguing while we starve; I say someone has to check the
  neighbour's house again tonight."
- Q6 (11:30): Leo, Mara, Elena all `nobody_goes`: "We are not going out there, and neither is Daniel."
- **Leo (11:33, `ration_water`)**: "We need to ration what is left in the pans and the bin so it actually lasts." The
  level goes to `rationed` at 11:33. Elena: "You are right to look after the water, Leo, we will make it last together."
- Leo (11:36): "You are not going anywhere tonight, Daniel. We stay inside."

**Night 9.** Daniel `sleep` (FROZEN): "My starving body is too weak to stand, so I cannot go out tonight." Elena
`watch_door`; Leo and Mara `lie_awake`. No trip. There is no night 10.

**Day 10.** Dry. Elena reaches stage 3 (12:39). **27 trip-position acts**, Daniel `still_going` 10 times. Q5 at 19:00 (Daniel).
- Daniel (min 03, `volunteer`): "I am the oldest, so I will go out to the neighbour's house tonight to find what we need."
- Leo (min 06): "You nearly got yourself killed last time, Daniel. Going out again is just stupid."
- Mara (min 03): "You are not going anywhere, Daniel. You have no right to decide this for us."
- Daniel (19:03): "I have to go, Mom, because someone has to find something for us."

## 3. W1-1, W1-3, W1-11 by the counts

- **Bedtime choices, nights 3–9 (28):** v22: `lie_awake` 22, `sleep` 4, `go_next_door` 1, `watch_door` 1, `go_further` 0.
  v21: `lie_awake` 17, `sleep` 7, `watch_door` 3, `go_next_door` 1, `go_further` 0.
- **The one trip** is night 5, as in v21. In v21 Leo's `stop_daniel` ended it ("I am too weak anyway"); in v22 Daniel
  answered `go_anyway` and went. Groups on every other night: none.
- **Trip talk:** 115 trip-position acts on days 4, 5, 8, 9 and 10 (12, 21, 24, 31, 27), Daniel `still_going` 32 times
  (2, 6, 7, 7, 10). v21: 21 acts, on day 5 only, `still_going` 5. After night 5 Daniel said on 3 of the 5 days left (8, 9, 10) that he was
  going that night. His bedtimes on nights 6, 7, 8, 9 were `lie_awake`, `lie_awake`, `sleep`, `sleep`.
- **W1-11:** the one leaver is Daniel. His night-5 reason ("I must go out to find food…") and his day-5 trip words (his nine
  `volunteer`, `propose_trip` and `still_going` acts) have no WATER word. He did not go for water, and came back
  with it.
- **W1-1's two ways to count:** the plan counts `went_out`, and `got_up` or `at_door` with no `went_out`. `collect_rain`
  (1, day 6) and `rain_out` (0) do not count. With `collect_rain` added the count would be 2, still under 3.

## 4. W1-2 and W1-9: the body

- **W1-2: 6 of 28 reasons match FROZEN** (v21: 16). The six: Leo night 3, Leo night 4, Mara night 7, Daniel night 8, Mara
  night 8, Daniel night 9 (all quoted in §2). By the looser count of "weak, dizzy, tired or stand" in a reason: 6 of 28 (v21: 16).
- **The reasons became about Daniel, not the body:** 9 of the 28 name Daniel together with sneaking, slipping or going
  out ("…listen to make sure Daniel does not try to slip out into the dark again"). In v21: 4.
- **W1-9: 0 of 402 body lines** match. The distinct lines are in `runs/v22/scoring/score_v22.txt` (W19). The stage 2
  line is "you feel light and slow, and standing up fast greys your sight for a moment"; the stage 3 line is "you are thin
  and weak; stairs and carrying things tire you fast".

## 5. W1-4, W1-5, W1-6, W1-7: water and rain

- **W1-4 (12 acts, 4 days):** by day 0, 0, 0, 8, 2, 1, 1, 0. The 12 lines (`runs/v22/scoring/score_v22.txt`, W14):
  **9 are about the 9 L Daniel carried home** (day 6: 6 acts, day 7: 2, day 8: 1), **2 about rain on the bin** (Daniel's `collect_rain`, Leo's "check the yard bin") and
  **1 about the stored water** (Elena after Leo's rationing). Days 3, 4, 5 and 10 have none.
- **W1-5 (a):** both qualifying spells were heard by every person awake. Day 7 at 17:18: Daniel, Elena, Leo, Mara. Day 9
  at 11:30: Elena, Leo, Mara (Daniel was resting). **(b):** the first spell is day 7 at 17:18; its Q6 stretch had 8
  speech acts and none of the words rain, catch, bucket, bin or pot, and no `collect_rain` (not offered: the bin had been out since
  day 6). By the plan's rule this is a FAIL. The house's one answer to rain came a spell earlier, on day 6 at min 00 (§2),
  which the plan's rule does not read.
- **`rain_out`: 0.** No bedtime prompt of nights 3–9 says it is raining (0 of 32 night prompts), because no rain fell at
  21:00 on any of those nights (night 5's started at 22:03). The option was never offered.
- **Day lines:** 80 day prompts carry "Rain is falling". The "About water:" line is in every day prompt.
- **W1-6: 0 claims** that match NOWATER in 326 speech acts and the nights' reasons and words.
- **W1-7:** the store fell below 50 L on day 5 (57.5 L at 07:00, 43.5 L at 21:00), so the deadline was 21:00 of day 6. The
  `ration_water` option (with `save_water`) was listed in 280 of the 402 prompts; the first act is Leo's, day 9 at 11:33
  (the store then: tap 17.0 + bin 54.6 = 71.6 L, with 17.8 mm falling). `save_water` was never said. By 21:00 of day 6
  the bin had 67.1 L (store 104.9 L), so by the plan's rule this is a FAIL while the store was not short.
- **Thirst never began:** stage 0 for all four at 21:00 on all 8 days. The tap fell from 105.5 to 10.0 L, and the bin
  (rain water, drawn first for washing and the toilet) covered the rest. The thirst words, the thirst need events and
  the thirst-stage Q1 were therefore not exercised.

## 6. W1-8: cost

- **Live asks 402** (≤ 450); the cap (470) was not reached. **Day asks** 40, 40, 40, 40, 42, 48, 48, 44 (≤ 56).
- **Largest estimate 2602** (day 9, Daniel); a second prompt of day 9 has 2601; the next are 2599 and 2597 (day 8). Under
  the plan's rule (`estimate_tokens(system + prompt)` ≤ 2600) this is a FAIL by 2 tokens. Two prompts exceed 2600.
  Largest by kind: day 2602, night 2407 (night 9), mind 2543 (mind 9). v21: day 2358, night 2193, mind 2435.
- **The API's own count** is higher: largest 3000 (mind 9), against 2854 in v21. The day 9 Daniel prompt counted 2567 by
  the API. In that prompt the W1 lines are the "About water:" line (277 characters), the two water-rule options
  (96 and 80), and the body line (132); W1's lines sit outside the trimming budget by design (`reports/w1_impl.md` §2,
  point 10).
- **The meta's `max_prompt_tokens_estimated` (2453)** covers only the scenes up to day 3, as in v21.

## 7. Against v21

| | v21 | v22 |
|---|---|---|
| Trips, nights 3–9 | 0 (1 attempt, N5) | 1 (N5) |
| Bedtime `go_next_door` / `go_further` | 1 / 0 | 1 / 0 |
| Bedtime reasons FROZEN | 16 of 28 | 6 of 28 |
| Trip-position acts, by day | 21 on day 5 | 12, 21, 0, 0, 24, 31, 27 on days 4–10 |
| Daniel `still_going` | 5 | 32 |
| WATER speech acts | 0 | 12 |
| CAN share | 25.7% | 11.7% |
| `ration_water` / `save_water` said | no water line | 1 (day 9) / 0 |
| `collect_rain` / `rain_out` | — | 1 / 0 |
| Stage 3 reached | Daniel, Leo (day 6), Mara (7), Elena (9) | Daniel (night 6), Leo (7), Mara (8), Elena (10) |
| Live asks, largest estimate | 337, 2435 | 402, 2602 |

## 8. What the run shows, by the counts

- **The body no longer forbids, and the house still stays home.** FROZEN reasons fell from 16 to 6 and the body lines
  contain no forbidding word. Bedtime choices did not move toward going out: 1 of 28, as in v21.
- **The trip talk came back, but not the trips.** After Daniel's successful trip the house spoke of trips on 3 of the 5
  following days (8, 9, 10), and nobody went; `still_going` is 32 over the run. The reasons at bedtime were mostly about watching Daniel.
- **The talk about water is the talk about the haul.** 9 of 12 acts. The water in the house (a tap falling from 105.5 to
  10 L) was in every prompt and was spoken of once, on day 9, by Leo, and rationing began then.
- **The weather reached the house and the house hardly spoke of it.** All rain onsets from 07:00 to 21:00 were heard; one
  act answered the rain (Daniel's `collect_rain`, a day before the first qualifying spell).
- **Thirst and the water acts' consequences were not tested**: no one was ever short, so the thirst stages, the
  rain-water drinking and the cold-and-wet word did not matter. A run with a smaller store, or a drier week, is needed for that.
- **Cost:** the largest prompt grew by 167 tokens against v21 (2435 → 2602) and is 2 over the line W1-8 drew.

## 9. Commands and output

All from `Prototypes/llm-morning/`.

**1. The plan record** (`runs/v22/plan_frozen.txt`: time, sha256, HEAD, `git status --short`, `git diff --stat`, every `*.py`
and `config.json` sha256):
```
recorded_utc: 2026-10-08T19:59:11Z
eb3758cc599b9967e8d918d917e42ed1ac51bebb17f66c7e0fc8418ba2c3a6bf *reports/days_v22_plan.md
$ git rev-parse HEAD
a4edf849aff12bad1bfa0daa31258878375cf686
$ git status --short
?? reports/days_v22_plan.md
?? runs/v22/
?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
$ git diff --stat
(empty)
```
The seeded weather of days 1–10 is in the plan and in `runs/v22/weather_days1_10.txt`; the run's own stdout prints the
same ten lines (`runs/v22/daniel_ate_it-seed2.stdout.txt`, lines 2–11).

**2. The copy and the check** (`runs/v22/cache_copy.sha256.txt`, `runs/v22/premiss-seed2.stdout.txt`):
```
$ mkdir -p cache/v22 && cp cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed2.json cache/v22/
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v16/…seed2.json
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v22/…seed2.json
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/w22/scoring/premiss.py 2
  day 3 07:00 water: tap 105.5 L (bath 59.0, kitchen 46.5), bin 0.0 L, level as_before
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']; first 'min 00' line: ['- min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)']
exit 3
```
Scene index 6 is day 3, min 00. The cache file was unchanged by the check (same sha256).

**3. The scorer on v21** (`runs/w22/scoring/control_v21.txt`):
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/w22/scoring/w1_score.py --control
W1-1: table '1' | scorer '1' | MATCH
W1-2: table '16 of 28' | scorer '16 of 28' | MATCH
W1-3: table '1' | scorer '1' | MATCH
W1-4: table '0 acts, 0 days' | scorer '0 acts, 0 days' | MATCH
W1-5: table 'no weather' | scorer 'no weather' | MATCH
W1-6: table '0 (no claims)' | scorer '0 (no claims)' | MATCH
W1-7: table 'no water' | scorer 'no water' | MATCH
W1-8: table '337; days <= 40; 2435' | scorer '337; days <= 40; 2435' | MATCH
W1-9: table 'stage 3 lines match' | scorer 'stage 3 lines match' | MATCH
W1-10: table '63 of 245 = 25.7%' | scorer '63 of 245 = 25.7%' | MATCH
W1-11: table 'no trip' | scorer 'no trip' | MATCH
ALL MATCH
```

**4. The scorer, checked before the run** (no API):
```
$ … runs/w22/scoring/make_fake.py       exit 0 asks 525      (a fake 10-day run, runs/w22/fake/)
$ … runs/w22/scoring/w1_score.py runs/w22/fake runs/w22/fake/cache/fake-daniel_ate_it-seed2.json 0
                                        exit 0; every rule computed (runs/w22/scoring/fake_score.txt)
$ … runs/w22/scoring/selfcheck.py       35 ok lines; "all checks ok"; exit 0 (runs/w22/scoring/selfcheck.txt)
$ … runs/w22/scoring/cap_check.py       cap raised: stopped: the 3-ask cap … (3 live asks sent). | requests sent to api: 3
```
`selfcheck.py` edits copies of the fake run to test W1-1, 2, 4, 5, 6, 7, 9, 10 and 11 where the fake model's own words never reach.

**5. The run** (`runs/v22/daniel_ate_it-seed2.stdout.txt`, `.stderr.txt` (empty), `seed2.started_utc.txt`, `seed2.ended_utc.txt`,
`seed2.exit.txt`):
```
$ GEMINI_API_KEY=<the one-off key, process only> PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 \
    .venv/Scripts/python.exe -u runs/v22/run_capped.py > runs/v22/daniel_ate_it-seed2.stdout.txt 2> …stderr.txt
started 2026-10-08T20:04:14Z    ended 2026-10-08T20:35:39Z    exit 0
  day 3 min 00: model asked for 4; day asks 4 of 40; so far 4 live, 96 cached, 4 API requests
  night 5: rainy; bedtime Daniel go_next_door, Elena lie_awake, Leo lie_awake, Mara lie_awake; Daniel out (back shaken, with water), water 9 L
  day 7 17:18: Q6, rain began: Daniel, Elena, Leo, Mara asked in the kitchen
  day 9 11:30: Q6, rain began: Elena, Leo, Mara asked in the kitchen
  api_requests 405   answers_live 402   answers_from_cache 96   run_seconds 1875.4
  story_sha256: cff2506323eea49af0cc07d1186ffc8072f084b25bc4800d27047bde09617f11
```
The story is `runs/v22/daniel_ate_it-seed2.md`; transcript and meta beside it. The run was started in the background by this
session; nothing was stopped.

**6. Scoring** (`runs/v22/scoring/score_v22.txt`; the account in `account.txt`; the lines in `lines.txt`):
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/w22/scoring/w1_score.py > runs/v22/scoring/score_v22.txt
exit 0
W1-1 FAIL (1 outward acts on nights [5]: [(5, 'Daniel', 'went_out')])
W1-2 PASS (6 of 28 bedtime reasons match FROZEN)
W1-3 FAIL (1 bedtime go_next_door or go_further: [(5, 'Daniel', 'go_next_door')])
W1-4 PASS (12 WATER speech acts on 4 of 8 days; by day {3: 0, 4: 0, 5: 0, 6: 8, 7: 2, 8: 1, 9: 1, 10: 0})
W1-5 FAIL ((a) 100% over 2 spells; (b) does not hold; collect_rain 1, rain_out 0)
W1-6 PASS (0 NOWATER claims; 0 while the store was > 0; 0 unsure)
W1-7 FAIL (below 50 L at ((5, 840), 43.5); water-rule acts [(9, 273, '11:33', 'Leo', 'ration_water', 'We need to ration what is left in the pans and the bin so it actually lasts.')])
W1-8 FAIL (live 402; day asks {3: 40, 4: 40, 5: 40, 6: 40, 7: 42, 8: 48, 9: 48, 10: 44}; largest estimate (2602, 'day', 'Daniel'))
W1-9 PASS (0 of 402 body lines match)
W1-10 PASS (38 of 326 = 11.7%)
W1-11 FAIL (went_out nights [5])
```
**The largest estimate, by a replay** (`runs/v22/scoring/replay_max.txt`; `runs/w22/scoring/replay_max.py`, no API, a temp
copy of `cache/v22`):
```
replay exit 1 prompts 498 from day 3 on 402
('day9', 'Daniel', 2602)  ('day9', 'Daniel', 2601)  ('day8', 'Daniel', 2599)  ('day8', 'Daniel', 2597)  ('day9', 'Daniel', 2597)
```
The replay's "exit 1" is `morning.py:326-328` (its temp folder has no original story to compare with), as in v21. 498 =
96 + 402.

**7. At the end** (`runs/v22/end_checks.txt`):
```
checked_utc: 2026-10-08T20:35:48Z
eb3758cc599b9967e8d918d917e42ed1ac51bebb17f66c7e0fc8418ba2c3a6bf *reports/days_v22_plan.md   (as recorded)
     23 OK                                                    (the *.py and config.json sha256s of plan_frozen.txt)
git status --short:  ?? cache/v22/  ?? reports/days_v22_plan.md  ?? runs/v22/  ?? runs/w22/  (and runs/v6's three replay files)
git diff --stat:     (empty)
cache/v16 seed2:     d79a4939… (unchanged)
```
