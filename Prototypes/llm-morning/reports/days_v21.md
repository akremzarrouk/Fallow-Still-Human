# v21: v16 seed 2, days 3 to 10, the first 10-day live run

Mode: run. The plan is `reports/days_v21_plan.md`, recorded before any live call (`runs/v21/plan_frozen.txt`). The code
is HEAD `91380e4` (`reports/ten_days_prep.md`). No code, test or plan line was edited. Paths are relative to
`Prototypes/llm-morning/`. Raw outputs are in `runs/v21/`, and the scoring outputs in `runs/v21/scoring/`. Clock stamps
are the run's own ("min 75", "10:24"), as in the transcript.

## Result

| # | Prediction | Verdict | Evidence |
|---|---|---|---|
| T1 | Someone goes out on at least one of nights 3–9 | **FAIL** | **0 trips** on nights 3–9. One attempt: night 5, Daniel chose `go_next_door` at bedtime, got up, and Leo stopped him (§2, night 5). |
| T2 | No prompt estimate over 2600; the memory bound removes no line of A, B or C on any morning | **FAIL** | **Part 1 holds:** largest estimate **2435** (mind 5, Leo). **Part 2 does not:** on day 6 the bound shortened Leo's block A to its second variant (§6). No C or B line was removed, and no line of A was dropped: two lines lost their minute lists. |
| T3 | False statements about past events, days 3–10, ≤ 10 | **FAIL** | **11** (§4). Within one or two judgment calls of the threshold: drop the two weakest and it is 9. |
| T4 | On ≥ 3 of days 4–10, ≥ half of the morning's speech acts use a pair new to the previous morning | **FAIL** | **0 of 7 days.** Fresh share: 3/20, 10/24, 3/20, 0/10, 2/19, 0/16, 0/15 (§5). |
| T5 | Someone reaches the third fasting stage; nobody uses the body words in 3 of their own speech acts in a row | **PASS** | Stage 3: Daniel (day 6), Leo (day 6), Mara (day 7), Elena (day 9). Longest run of body-word speech acts: Daniel 1, Elena 1, Leo 0, Mara 0 (§7). |
| T6 | Food home → next day eats, shares or gives; someone not back → ≥ 2 others name them | **NOT TESTED** | Both parts: nobody went out, nothing was brought home, nobody was away. |
| T7 | Live asks ≤ 450; every day ≤ 48 | **PASS** | **337** live asks; the cap (450) was not reached. Day asks 35, 38, 40, 31, 30, 36, 35, 34. |

**DONE:**
- **The plan.** Recorded at **2026-10-08T13:35:21Z**, sha256 `859df508…b277c2bd`. The run was started at 13:39:31Z, and
  its first live ask was day 3, min 00. At the end (14:14:36Z) the sha256 is the same, and the 20 code and config
  sha256s of `plan_frozen.txt` are unchanged (20 OK, §9). `git diff --stat` is empty.
- **The exit.** The run was started with `Start-Process`, so its exit code was not read directly. `morning.run`
  returns 0 only after it has written the transcript and meta; both exist, and the stdout holds no "stopped" line,
  no retry wait and no traceback (§9). The run ended with all of day 10's turns played.
- **The cap.** 337 live asks; no cap stop.
- **Verdicts.** All 7 predictions have one: 2 PASS, 4 FAIL, 1 NOT TESTED.

**What differed from the plan's wording:**
- **The key.** The run used an API key the user gave in chat for this one run, set as `GEMINI_API_KEY` for that process
  only. It is in no file. v20 had spent 275 of the day's 500 free requests earlier the same day, on the previous key.
- **The start.** The run was started through `runs/v21/run_capped.py` (the plan says so): `morning.main()` with the
  arguments `--seed 2 --out v21 --days 10`, plus a counter that would have stopped the 451st ask. It never did.

**Against v20** (`reports/days_v20.md`, seed 2 and 3 over days 3–5; not the same question, as that run was 5 days):

| | v20 (days 3–5) | v21 (days 3–10) |
|---|---|---|
| Trips on nights 3 and later | 2 (seed 3, nights 3 and 4) | 0 on nights 3–9 |
| `go_further` at a bedtime | 2 (seed 3) | 0 |
| False statements about the past | 5 in 6 seed-days | 11 in 8 days |

## 1. Asks per day

From `runs/v21/daniel_ate_it-seed2.meta.json` (`runs/v21/scoring/tables.txt`). Days 1–2, nights 1–2 and minds 1–2 were
answered from the cache: 96 answers. Every ask from day 3 on was live: **337** (`api_requests` 337, `answers_live` 337,
`answers_from_cache` 96). No 429 or 503: no retry line in the stdout, and an empty stderr. Run time 1838 s (30.6 min).

| Day | Day asks | Night after | Mind after | Stretches (trigger: asks) | Morning ends |
|---|---|---|---|---|---|
| 3 | 35 | 4 | 4 | morning 19, Q2 8, Q1 8 | min 15 |
| 4 | 38 | 4 | 4 | morning 22, Q2 8, Q1 8 | min 18 |
| 5 | 40 | 6 | 4 | morning 24, Q2 8, Q5 8 | min 18 |
| 6 | 31 | 4 | 4 | morning 22, Q2 6, Q2 2, Q1 1 | min 18 |
| 7 | 30 | 4 | 4 | morning 11, Q2 3, Q2 8, Q1 8 | min 09 |
| 8 | 36 | 4 | 4 | morning 24, Q2 5, Q2 7 | min 18 |
| 9 | 35 | 4 | 4 | morning 19, Q2 8, Q2 8 | min 15 |
| 10 | 34 | — | — | morning 18, Q2 8, Q2 8 | min 15 |
| Sum | 279 | 30 | 28 | | |

279 + 30 + 28 = 337. Night 5 has 6 asks: its 4 bedtime choices, Leo's reaction and Daniel's answer. Q5 fired once, on
day 5. Q1 fired on days 3, 4, 6 and 7; Q2 fired twice on every day.

## 2. Each day and night

Shelf 0 portions every morning of days 3–10. Nobody ate, shared or gave on any day (`runs/v21/scoring/account.txt`: no
food act). Nobody was away on any day. Fasting at 21:00, hours:

| Day | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| 3 | 75.9 | 32.3 | 74.0 | 58.0 |
| 4 | 103.5 | 52.7 | 98.0 | 80.8 |
| 5 | 131.1 | 73.1 | 122.0 | 103.6 |
| 6 | 158.7 | 93.5 | 146.0 | 126.4 |
| 7 | 186.3 | 113.9 | 170.0 | 149.2 |
| 8 | 213.9 | 134.3 | 194.0 | 172.0 |
| 9 | 241.5 | 154.7 | 218.0 | 194.8 |
| 10 | 269.1 | 175.1 | 242.0 | 217.6 |

Stage crossings in the transcript's need events: Mara stage 1 (day 3, 10:27); Daniel stage 2 (day 4, 14:30); Elena stage
1 (day 4, 15:30); Leo stage 2 (day 4, 19:00); Mara stage 2 (day 5, 13:00); **Daniel stage 3** (day 6, min 75); **Leo
stage 3** (day 6, 19:00); **Mara stage 3** (day 7, 15:30); **Elena stage 3** (day 9, min 87).

**Day 3.** Morning to min 15; Q2 at 10:24; Q1 at 20:09 (Leo). The talk is Daniel's night-2 trip.
- Mara (min 00): "You went out into the night and came back with nothing, just like you always ruin everything."
- Daniel (min 12): "Mara, I know it was empty, but I had to check so we wouldn't starve wondering."
- Leo (10:27): "Daniel, sneaking out into the dark like that didn't help anyone, and you know it."
- Elena (min 12): "Let's not fight among ourselves; shouting won't put food on the shelf."
- Trip positions: none.

**Night 3.** Bedtimes: Daniel `sleep` ("I have no strength left to stay awake or go out again."), Elena `sleep`, Leo and
Mara `lie_awake`. All four were offered `go_next_door` and `go_further`. Nobody got up. No trip.

**Day 4.** Morning to min 18; Q2 at 10:57; Q1 at 19:00 (Leo). The talk turns to the can.
- Leo (min 00): "You took it yourself three days ago, Daniel, so stop pretending you are saving anyone."
- Daniel (min 03): "Leo, you have no right to throw that in my face when I am the only one risking my neck for this family."
- Mara (min 00): "You took everything already, Daniel, and now there is nothing left for any of us."
- Leo (19:00): "Daniel already admitted taking the can himself days ago, so let's stop pretending there's any mystery."
- Trip positions: none.

**Night 4.** Daniel `lie_awake` ("I need to stay alert and protect them, even when my body feels so weak."), Elena `sleep`,
Leo and Mara `lie_awake` (Mara: "I am too weak and dizzy to go anywhere"). No trip.

**Day 5.** Morning to min 18; Q2 at 10:03; **Q5 at 19:00** (Leo asked). **21 trip position acts**, the only ones in the run.
- Daniel (min 06, `volunteer`): "I will go back to the neighbour's house tonight myself to find something for us."
- Elena (min 06, `keep_daniel_home`): "Daniel, you are not going back out there tonight, we cannot risk losing you."
- Daniel (min 12, `still_going`): "I told you I am going tonight, and I mean it. Someone has to do something."
- Leo (min 03): "You figure out survival by blaming everyone else while you ate the only food we had."
- Daniel (19:03): "I have made my choice and I am going tonight, because someone has to." Elena (19:03): "Daniel, please, you
  must stay home tonight, I cannot bear the thought of losing you out there."
- Daniel `still_going` 5 times (min 09, min 12, 10:06, 19:00, 19:03).

**Night 5.** Bedtimes: **Daniel `go_next_door`** ("I am the oldest and it is my duty to provide for my family."), Elena
`watch_door`, Leo and Mara `lie_awake`. Daniel got up; Leo saw it.
- Leo, `stop_daniel`: "Daniel, stay where you are. You aren't going out there tonight."
- Daniel, `stay_home`: "I will stay, Leo. I am too weak anyway." His reason: "My legs are shaking too badly and I cannot
  risk dying out there when Mom told me to stay."
- No group; the house knew only that there were low voices (Elena, Mara). Daniel and Leo's lines say he went back to bed.

**Day 6.** Morning to min 18; Q2 at 09:36 and 10:33; Q1 at 19:00 (Leo). No trip positions. **Daniel and Leo reach stage 3.**
- Daniel (min 06): "Nobody is going anywhere today, we are going to stay right here and figure this out together."
- Elena (min 03): "Please stop arguing, we are all exhausted and we need to stay together."
- Elena (min 09): "Daniel, please do not shout at your sister when we are all this weak."
- Mara (09:36): "You are the one who took everything from us and you still just sit there like nothing happened."
- Leo (min 00): "You spent days lying about the can, Daniel, so nobody believes your promises now."

**Night 6.** Daniel `sleep` ("I am far too weak to go out tonight and have nothing left to prove."), Elena `watch_door`
("I must guard the door myself so no one wanders out into the darkness."), Leo and Mara `lie_awake`. No trip.

**Day 7.** The shortest morning (to min 09; 11 asks); 30 day asks; Q1 at 15:30 (Mara). **Mara reaches stage 3.**
- Mara (min 00): "You took the food, Daniel, and you've been lying to all of us this whole time."
- Daniel (min 00): "Stop saying that, Mara, you know I already told you the truth about it."
- Leo (15:33): "Daniel, you already admitted you took it six days ago, so stop acting like a victim now."
- Elena (15:33): "Please, we cannot fight amongst ourselves when we are this weak and have nothing left."

**Night 7.** Daniel `sleep`, Elena `watch_door`, **Leo `sleep`** ("I am too weak to stand or walk anywhere tonight."), Mara
`lie_awake`. No trip.

**Day 8.** 36 asks; Q2 twice; no Q1, no Q5. Mara says "took the can/it and left us with nothing" six times.
- Mara (min 00): "You are just sitting there acting innocent, Daniel. You took the can and left us with nothing."
- Leo (08:36): "Daniel, trying to assert authority won't magic food onto an empty shelf or undo what you already admitted to."
- Daniel (min 09): "Mara, stop bringing that up when we all know there is nothing left to fight about."
- Elena (min 03): "Please, children, stop this fighting. We have to stay together if we want to live through this."

**Night 8.** All four `lie_awake`; every reason says too weak ("My body is too weak to stand or walk anywhere safely"). No trip.

**Day 9.** 35 asks; Q2 twice. **Elena reaches stage 3** (min 87).
- Daniel (min 00): "Mara, stop accusing me when I already admitted it days ago and we have bigger problems."
- Leo (09:51): "Staring is all I have the energy for, Daniel, since you made sure there's nothing else left."
- Daniel (09:57): "Mom, you are right, we shouldn't fight when we need to stay together." Elena (09:57): "Daniel, thank
  you for saying that, we just need to hold on to each other right now."

**Night 9.** Daniel `sleep` ("I am too weak to stand or protect anyone tonight, so I must finally rest."), Elena, Leo and
Mara `lie_awake`. No trip. There is no night 10.

**Day 10.** 34 asks; Q2 twice.
- Mara (min 00): "You took the can, Daniel, and you're the reason we have nothing left."
- Leo (09:18): "Daniel, keeping score implies there is a game, and this is just survival."
- Daniel (09:21): "Leo, I am sorry, I am just trying to keep us all alive."
- Elena (09:21): "Mara, my sweet girl, please try to rest and let us hold onto each other."

## 3. T1 and T6, by the counts

- **T1.** Bedtime choices on nights 3–9: 28. `lie_awake` 17, `sleep` 7, `watch_door` 3, `go_next_door` 1, `go_further` 0
  (each night's four are in `runs/v21/scoring/score_v21.txt`, T1). Groups on every night: none (`night3` to `night9`,
  `groups` empty).
- **The one attempt.** Night 5 (§2). It ended at Leo's `stop_daniel` and Daniel's `stay_home`.
- **Trip position acts:** day 5 only, 21 (§1). Days 3, 4 and 6–10: 0. After night 5 nobody offered, objected, or asked
  to go, on any of the 5 days left.
- **T6.** Food home: no case. Not back: no case. NOT TESTED, both parts.

## 4. T3: the false statements about the past

All 245 speech acts of days 3–10 (`runs/v21/scoring/lines.txt`) were read against the chronicle (the transcript's
`chronicle`; non-speech events in `runs/v21/scoring/chronicle_nonspeech.txt`), by the rules of the plan.

**The facts the lines are read against:**
- Daniel took one can before day 1's count (D1-001: "one can fewer", 2 portions left). He denied it on day 1 only
  (D1-004, D1-010), accused Leo (D1-008, 015, 018), and **admitted it on day 1, min 33** (D1-022): "I took it in the
  night, I'm sorry." No denial on day 2 or later.
- Mara ate one of the 2 portions (D1-044). Daniel handed Elena the other on day 2 (D2-003, D2-004).
- Daniel went next door on night 2 and came back with nothing (N2-10 to N2-12). Nobody else ever went out.
- Night 5: Daniel got up, Leo stopped him, he stayed (N5-05 to N5-07).

| # | Day, time, speaker | The statement | The true fact |
|---|---|---|---|
| 1 | 3, min 03, Leo | "…you went out there last night and came back with nothing, just like you always do." | One trip, night 2. Nothing before it (v19's S2-2 was counted for the same words). |
| 2 | 4, min 00, Mara | "You took everything already, Daniel…" | One can (D1-001). The 2 portions left went to Mara and Elena. Counted as v20's #1 and #2 were. |
| 3 | 4, 11:00, Leo | "…we all know who took the last of it." | Daniel did not take the last: the last 2 portions were eaten by Mara and Elena (D1-044, D2-004). The weakest counted. |
| 4 | 5, min 03, Leo | "…while you ate the only food we had." | One can. Two portions were left after the count. |
| 5 | 5, min 15, Mara | "…you just lied to us for days about the can!" | He denied for the first 15 minutes of day 1 and admitted at min 33 of day 1 (D1-004 to D1-022). |
| 6 | 5, min 15, Leo | "You spent days lying about the can, Daniel…" | As 5. |
| 7 | 6, min 00, Leo | "You spent days lying about the can, Daniel, so nobody believes your promises now." | As 5. |
| 8 | 6, min 03, Leo | "…lying about them for days is another." | As 5. |
| 9 | 6, min 12, Mara | "…after everything you stole." | One can. |
| 10 | 6, 09:36, Mara | "You are the one who took everything from us…" | One can. |
| 11 | 7, min 00, Mara | "…you've been lying to all of us this whole time." | He lied for 33 minutes of day 1 and admitted it (D1-022). |

**By day:** day 3: 1; day 4: 2; day 5: 3; day 6: 4; day 7: 1; days 8–10: **0**.

**What the speakers' prompts held** was not replayed line by line for this run; v20 found the true fact in most
speakers' prompts as a standing line (`reports/days_v20.md` §4). Not checked here.

**Read and not counted** (each with why):
- **"Left us with nothing."** 13 lines of Mara (days 8, 9, 10: 6, 4, 3), "You took the can and left us with nothing",
  and Leo's "the reason we have nothing" (days 8, 9). A cause, not an event, as in `reports/days_v20.md` §4. The shelf was 0 from day
  2; the can was taken before day 1.
- **Present-tense claims.** Mara, day 10, min 09: "…you won't even own up to it, Daniel!" (he had admitted it, D1-022).
  Mara, day 10, min 12: "…when you lie and take everything" (habitual). Mara, day 7, 15:33 and day 8, min 03 and 15:
  "Don't pretend you didn't."
- **Recency.** Mara, day 4, 10:57: "you just came back from the dark with nothing"; 11:00: "you just brought back nothing".
  The last trip was night 2, two nights before. "Just" read as an idiom.
- **Day 4, Mara, min 06:** "you're the one who stole what we had."
- **Characterizations.** "You always promise things you can't deliver", "You always blame everyone else" (Daniel did
  accuse Leo on day 1), "everything you've pulled".
- **Day 10, Daniel, 09:15:** "I didn't mean to snap at you earlier" (Leo). No earlier line of that day is to Leo; "earlier"
  can be a previous day.

**Sensitivity.** Counted 11. Dropping the two weakest (3 and 11) gives 9: PASS. Counting the four borderline
statements above (Mara day 10 twice, day 4 twice) gives 15. The verdict sits on these calls.

## 5. T4: new pairs in the morning

From `runs/v21/scoring/score_v21.txt` (T4). A speech act counts if its (act kind, target) is not that of any speech
act of the previous day's morning. A day holds with ≥ 1 speech act and ≥ half counted.

| Day | Morning speech acts | New pair | Holds |
|---|---|---|---|
| 4 | 20 | 3 | no |
| 5 | 24 | 10 | no (the trip positions are the new pairs) |
| 6 | 20 | 3 | no |
| 7 | 10 | 0 | no |
| 8 | 19 | 2 | no |
| 9 | 16 | 0 | no |
| 10 | 15 | 0 | no |

**Repetition, by the counts** (all 245 speech acts, days 3–10):
- 233 distinct (speaker, text); 12 exact repeats of a line already said. Most repeated: Mara's "You went out into the
  night and came back with nothing, Daniel. Why did you even go?" (day 3, 3 times), Mara's "You took the can, Daniel,
  and you're the reason we have nothing left." (3), Daniel's "Mara, stop accusing me when I am trying to keep us all
  alive." (3), one Elena line (3).
- Openings: Daniel "Mara, stop accusing me when…" 8 times; Mara "You think you can just…" 8, "You went out into the…" 7.
- Mara: 53 of her 71 lines name the can, the taking, the stealing or the lying. Elena: 45 of her 58 are `reassure_all`.
- Distinct pairs a day: 6, 5, 10, 8, 6, 6, 7, 7 (days 3–10). Silent model acts a day: 4, 2, 0, 6, 6, 7, 4, 5.

## 6. T2: the prompts

Size estimate = `world.estimate_tokens(system + prompt)`, as `max_prompt_tokens` counts it, for every prompt of days 3–10
(337 prompts; the replay saw 433 with days 1–2). From `runs/v21/scoring/score_v21.txt`.

| Day | Prompts | Largest day estimate (who) | Largest night | Largest mind | Budget, most / over 1400 | Most cut, today / before |
|---|---|---|---|---|---|---|
| 3 | 35 | 2315 (Mara) | 2156 (Leo) | 1904 (Mara) | 1399 / 0 | 43 / 5 |
| 4 | 38 | 2321 (Leo) | 2168 (Leo) | 1998 (Leo) | 1400 / 0 | 45 / 5 |
| 5 | 40 | 2358 (Elena) | 2187 (Daniel) | **2435 (Leo)** | 1400 / 0 | 54 / 6 |
| 6 | 31 | 2349 (Mara) | 2193 (Mara) | 1773 (Daniel) | 1399 / 0 | 37 / 5 |
| 7 | 30 | 2269 (Elena) | 2101 (Elena) | 1847 (Daniel) | 1399 / 0 | 41 / 5 |
| 8 | 36 | 2266 (Mara) | 2109 (Mara) | 1914 (Daniel) | 1399 / 0 | 32 / 5 |
| 9 | 35 | 2304 (Daniel) | 2149 (Daniel) | 1937 (Daniel) | 1400 / 0 | 33 / 5 |
| 10 | 34 | 2279 (Daniel) | — | — | 1400 / 0 | 33 / 5 |

- **Largest overall: 2435** (mind 5, Leo), under 2600. The largest day or night prompt is **2358** (day 5, Elena). The
  meta's top-level `max_prompt_tokens_estimated` (2315) covers only the scenes up to day 3 (`morning.py`, the `max(...)`
  of the meta), so it is not a run-wide figure.
- **No prompt over the 1400 budget after cutting** (day and night prompts). The fake run of `reports/ten_days_prep.md`
  had 11 of 460.
- **The API's own count** (`prompt_token_count`) is higher than the estimate: largest **2854** (mind 5, Leo; estimate
  2435), 2400 for the largest day prompt (day 5), 2261 for the largest night (night 5). Under the plan's rule T2 uses
  the estimate; read as the API's count, the largest would exceed 2600.
- **The memory bound** (`memory.bounded`, 4 calls a morning, 32 in all; `runs/v21/scoring/bound_who.txt`): **one**
  removal. Day 6, **Leo**: block A went to its second variant (9 lines kept of 9; the minute lists of the Accusations
  and Confrontations lines were dropped). No C thought, C line or B line removed on any morning. By the plan's rule
  (block A not its first variant) this is a removal.

Memory bound per morning, as A shortened / C thoughts / C lines / B lines removed: days 3, 4, 5, 7, 8, 9, 10: 0 / 0 / 0 /
0; day 6: 1 / 0 / 0 / 0.

## 7. T5: the third fasting stage and the body words

- **Stage 3:** four crossings (above). Day 6: Daniel, Leo. Day 7: Mara. Day 9: Elena. Elena's stage-2 crossing has no
  need event in the transcript (fasting 93.5 h at 21:00 on day 6, 113.9 h on day 7); noted, not investigated.
- **Body words** (matched as whole words that begin with tired, exhaust, weary, sleep, weak, dizz, faint, stand) in
  spoken words: Daniel 1 of 79 speech acts (d3 min 06, "just stand there"), Elena 3 of 58 (d6 min 03 "exhausted"; d6 min 09
  "weak"; d7 15:33 "weak"), Leo 0 of 37, Mara 0 of 71. Longest run in a row: 1, 1, 0, 0.
- **In the bedtime reasons, not counted by the rule** (they are not spoken words): "weak", "stand", "dizzy" and the like are
  in the reasons of 16 of the 28 bedtime choices (night 3: 1, night 4: 3, nights 5, 6, 7, 9: 2 each, night 8: all 4).

## 8. What the run shows, by the counts

- **Desperation did not move the house.** One attempt in 7 nights. On day 5 the house spoke of the trip with 21 acts,
  Daniel `still_going` five times; the bedtime then had 1 `go_next_door` among 4 choices; Leo's `stop_daniel` ended it
  with "I am too weak anyway". On days 6–10 no one spoke of a trip.
- **False statements did not grow:** 1, 2, 3, 4, 1, 0, 0, 0 by day. All 11 are about the can (number or duration) or one
  "like you always do". Days 8–10 had none; the lines on those days are "took the can and left us with nothing" and
  the like (not counted, §4).
- **Days repeated:** 0 of 7 days had half of the morning in new pairs. The talk after day 5 is Mara accusing and
  Daniel answering, Elena reassuring.
- **Prompts stayed bounded:** 2435 at most, 337 live asks, day asks 30 to 40, none near the 48 cap.
- **The bodies kept changing to day 10:** the third stage in four of four by day 9.
- **No food and no losses:** the shelf was 0 for all 8 days, so the food half of T6 and the loss half could not be tested.

## 9. Commands and output

All from `Prototypes/llm-morning/`.

**1. The plan record** (`runs/v21/plan_frozen.txt`: time, sha256, HEAD, `git status --short`, `git diff --stat`, every `*.py`
and `config.json` sha256):
```
recorded_utc: 2026-10-08T13:35:21Z
859df50828ddb0f44f65c1e12f71d3aa23c4b1b86ba916e71a849030b277c2bd *reports/days_v21_plan.md
$ git rev-parse HEAD
91380e400577a96145faf773f2d347a8934d1387
$ git status --short
?? reports/days_v21_plan.md
?? runs/v21/
?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
$ git diff --stat
(empty)
```

**2. The copy and the check** (`runs/v21/cache_copy.sha256.txt`, `runs/v21/premiss-seed2.stdout.txt`; the script
`runs/v21/scoring/premiss.py` is v20's with `out="v21", days=10`):
```
$ mkdir -p cache/v21 && cp cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed2.json cache/v21/
$ sha256sum cache/v16/*seed2.json cache/v21/*seed2.json        # equal: d79a4939…
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v21/scoring/premiss.py 2
  night 2, the night mind: model asked for 4; so far 0 live, 96 cached, 0 API requests
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']; first 'min 00' line: ['- min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)']
exit 3
```
Scene index 6 is day 3, min 00.

**3. The cap and the scorer, checked before the run** (no API):
- `runs/v21/run_capped.py`, with a stub client and cap 3: "cap raised: stopped: the 3-ask cap … (3 live asks sent). | requests
  sent to api: 3 | client.requests: 3".
- `runs/v21/scoring/t_score.py` on a fake 10-day run of seed 2 (exit 0, 530 fake asks): every rule computed, SUMMARY T1–T7.

**4. The run** (`runs/v21/daniel_ate_it-seed2.stdout.txt`, `.stderr.txt` (empty), `runs/v21/seed2.started_utc.txt`):
```
$ GEMINI_API_KEY=<the one-off key, process only> PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 \
    .venv/Scripts/python.exe -u runs/v21/run_capped.py > runs/v21/daniel_ate_it-seed2.stdout.txt
started 2026-10-08T13:39:31Z   (pid 25188; ended before 14:10:13Z)
  day 3 min 00: model asked for 4; day asks 4 of 40; so far 4 live, 96 cached, 4 API requests
  api_requests: 337   answers_live: 337   answers_from_cache: 96   run_seconds: 1838.2
  max_prompt_tokens_estimated: 2315   max_prompt_tokens_counted_by_api: 2854
  story_sha256: 583aa6d4fe7ad30554cf9c1a86753c1fb75a7748a37b45e7fd1c582c53c9ec4d
```
The story is `runs/v21/daniel_ate_it-seed2.md`; the transcript and meta beside it. The run was waited on by process ID
(25188) only; nothing was stopped.

**5. Scoring** (`runs/v21/scoring/score_v21.txt`; account in `account.txt`; lines in `lines.txt`; tables in
`tables.txt`; the bound in `bound_who.txt`):
```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v21/scoring/t_score.py > runs/v21/scoring/score_v21.txt
exit 0
seed 2: replay exit 1, prompts 433, from day 3 on 337
SUMMARY runs/v21
T1 FAIL (nights with a trip: [])
T2 FAIL (largest 2435; bound calls 32, removals 1)
T4 FAIL (days that hold: [])
T5 PASS (stage 3: 4 crossings; longest runs {'Daniel': 1, 'Elena': 1, 'Leo': 0, 'Mara': 0})
T6 NOT TESTED (food: NOT TESTED; loss: NOT TESTED)
T7 PASS (live 337)
```
- **The replay's "exit 1"** is `morning.py:326-328`: its temp folder has no original story to compare with. It replayed
  every cached and live answer: 433 = 96 + 337.
- **T3** is the hand count of §4.

**6. At the end** (`runs/v21/scoring/end_checks.txt`):
```
checked_utc: 2026-10-08T14:14:36Z
859df50828ddb0f44f65c1e12f71d3aa23c4b1b86ba916e71a849030b277c2bd *reports/days_v21_plan.md      (as recorded)
(the *.py and config.json sha256s of plan_frozen.txt | sha256sum -c)     20 OK
cache/v16 seed2: OK
cache/v21 seed2: FAILED against the copy's sha256, as expected: it holds the 337 live answers
v16 entries 147, v21 entries 484, all v16 kept unchanged True, new 337
git status --short: ?? cache/v21/  ?? reports/days_v21_plan.md  ?? runs/v21/  (and runs/v6's three replay files)
git diff --stat: (empty)
```
