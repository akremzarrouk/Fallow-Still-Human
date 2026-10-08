# v22 plan: W1's live run, v16 seed 2, days 3 to 10

Mode: run. v16's seed 2, played on to day 10 (`--days 10`), on the W1 code (HEAD `a4edf84`, clean tree apart from three
untracked `runs/v6` replay files). Output `v22`: `runs/v22`, `cache/v22`. The control is v21 (`reports/days_v21.md`,
`runs/v21/daniel_ate_it-seed2.transcript.json`), the same seed from the same state on the code before W1.

**Why:** to see whether honest bodies, water and rain change what the house does over ten days, compared with v21,
where it never moved (0 trips on nights 3–9; 16 of 28 bedtime reasons that say they cannot stand, walk or go).

**How it runs:**
- **The cache.** `cache/v22` starts as a copy of `cache/v16`'s seed 2 file. Days 1–2, nights 1–2 and minds 1–2 are
  answered from it.
- **The check before.** A no-API replay with `--days 10` must go live first at day 3, min 00. If not, the run stops
  and is reported.
- **The run.** Seed 2 runs live once, `--days 10`, out `v22`. It is not rerun or resumed. If it stops part way, it is
  reported with how far it got.
- **The 470 cap.** The run is started through `runs/v22/run_capped.py` (as v21's, cap 470): when 470 live asks have
  been sent, the next one raises `gemini.CallCapReached` before any request goes out. No prompt, option or answer
  is changed. If that happens the run is reported with how far it got. W1-8's own limit (450) is a prediction; the
  cap (470) is the stop.
- **The key.** The run uses an API key the user gave in chat for this one run, as the process's `GEMINI_API_KEY`
  only. It is written nowhere.
- **No edits after this plan is recorded.** Once it is recorded (sha256 and time, `runs/v22/plan_frozen.txt`), no
  code, test or line of this plan is edited. The scorer `runs/w22/scoring/w1_score.py` and `run_capped.py` are new
  files, written after the plan and before the first live call; they are checked on a fake 10-day run and the
  scorer on v21.

## The seeded weather of days 1 to 10 (no API; `runs/v22/weather_days1_10.txt`)

Printed by `weather.Weather(2)`, the generator the run uses (`morning.py` prints the same lines):
```
  weather day 1: wet, 2.5 mm (09:00 to 13:09); 7.7 to 14.2 C outdoors, 15.0 C indoors
  weather day 2: dry; 11.2 to 15.2 C outdoors, 17.2 C indoors
  weather day 3: dry; 12.6 to 16.1 C outdoors, 18.4 C indoors
  weather day 4: dry; 7.1 to 19.4 C outdoors, 17.2 C indoors
  weather day 5: wet, 12.3 mm (22:03 to 03:42 the next day); 7.1 to 14.3 C outdoors, 14.7 C indoors
  weather day 6: wet, 4.5 mm (05:27 to 11:03, 06:30 to 10:45); 11.6 to 13.6 C outdoors, 16.6 C indoors
  weather day 7: wet, 1.2 mm (04:36 to 10:09, 17:18 to 20:21); 11.8 to 13.3 C outdoors, 16.6 C indoors
  weather day 8: dry; 8.0 to 19.1 C outdoors, 17.5 C indoors
  weather day 9: wet, 17.8 mm (11:30 to 16:30); 7.8 to 14.0 C outdoors, 14.9 C indoors
  weather day 10: dry; 8.6 to 18.6 C outdoors, 17.6 C indoors
```
- **Rain spells that start between 07:00 and 21:00 on days 3–10 (W1-5's spells): two.** Day 7 at 17:18 (to 20:21) and
  day 9 at 11:30 (to 16:30). The first is day 7 at 17:18.
- **Rain at other times** (not W1-5's spells, but the house hears or meets it): day 5, 22:03 to 03:42 (a rainy night 5:
  the bedtime rain option is offered, and the front-door draws are halved); day 6, 05:27 to 11:03 and 06:30 to 10:45
  (it is already raining at 07:00 of day 6, so "Rain is falling" is in the day's lines, with no onset in the day);
  day 7, 04:36 to 10:09 (the same, day 7 morning).
- **Days 3 and 4 are dry**, with 18.4 and 17.2 °C indoors; days 8 and 10 are dry. Days 5, 6, 7 and 9 are wet.

## Predictions (frozen)

W1's section 8 (`reports/world_design.md:785-819`), verbatim, with the changes marked **[changed]** or **[added]** (W1-1, W1-5, W1-11; W1-8 is restated as the design has it).

**The run:**
- v16 seed 2, `--days 10`, W1 code, scored on days 3–10 and nights 3–9.
- The control is v21 (`runs/v21/daniel_ate_it-seed2.transcript.json`).
- The script is `runs/w22/scoring/w1_score.py` (the design said `runs/w1/scoring/w1_score.py`), written and run on a
  fake run before the live one.

**Regexes (case-insensitive) used below:**
- `FROZEN = (too weak|cannot|can't|can not|unable|barely|no strength)\b[^.;]{0,40}?\b(stand|walk|move|go|make it|get up|leave|carry)\b`
- `WATER = \b(water|thirst\w*|drink\w*|rain\w*|bath)\b`
- `NOWATER = \bno (more )?water\b|\bwater is (gone|finished)\b|\bout of water\b|\bwater (has )?run out\b`
- `CAN = \bthe can\b|\btook\b|\bstole\b|\bstolen\b|\bsteal\w*|\blie[ds]?\b|\blying\b|\bliar\b`

**"Speech act":** a day act with words (`a["words"]`), as `runs/v21/scoring/lines.txt`.

| # | Prediction | Counting rule | v21 |
|---|---|---|---|
| **W1-1** | **The house acts on its own more often than in v21: ≥ 3 outward acts, on ≥ 2 different days or nights.** | **[changed]** Count only chronicle events of nights 3–9 that are `went_out`, and `got_up` or `at_door` with no `went_out` for that leaver that night (once per leaver per night). `collect_rain` and `rain_out` do not count. Code acts (bringing containers in) are not counted. | **1** (N5 `got_up`; §11, B4) |
| W1-2 | The body no longer forbids: ≤ 8 of the 28 bedtime reasons of nights 3–9 match FROZEN. | Every `night{n}` decision with `ask == "bedtime"`, n = 3–9; `reason` matched by FROZEN. | 16 of 28 |
| W1-3 | Going out is chosen at bedtime at least twice. | Bedtime options `go_next_door` or `go_further`, nights 3–9: ≥ 2. | 1 |
| W1-4 | The world reaches their words. | Speech acts matching WATER on ≥ 4 of the 8 days 3–10. | 0 acts, 0 days |
| W1-5 | Rain reaches the house, and the house answers it. | (a) For each rain spell start between 07:00 and 21:00 on days 3–10 (from the weather record), every person in the house and not asleep at that minute has a `heard` percept event of it: must be 100%. (b) The first such spell's Q6 stretch holds ≥ 1 act that is `collect_rain`, or a speech act matching `\b(rain|catch|bucket|bin|pots?)\b`. NOT TESTED if no spell starts by day in days 3–10. **[added]** Also reported: how many `collect_rain` and `rain_out` acts there were (day acts and bedtime choices). | no weather |
| W1-6 | Water claims are true. | Speech acts and reasons (day and night) matching NOWATER at a minute when the code's drinking store is > 0: ≤ 1. | 0 (no claims; v15 had 1, `reports/quiet_day_design.md:146-148`) |
| W1-7 | Rationing comes when the end is visible. | If the drinking store falls below 50 L (half of its 100 L on day 3, 07:00) at a minute of day k ≤ 9, then a `ration_water` or `save_water` act occurs by 21:00 of day k + 1. NOT TESTED if it never falls below 50 L by day 9. | no water |
| W1-8 | Cost stays bounded. | **[restated: the design already has these figures]** Live asks of days 3–10 ≤ 450; each day's asks ≤ 56 (40 + Q5 8 + Q6 8); largest `estimate_tokens` of any prompt ≤ 2600 (as v21's T2). | 337; days ≤ 40; 2435 |
| W1-9 | No body line forbids an act. | Every "Your body:" line of every prompt of days 3–10 and nights 3–9 (replayed, no API): 0 matches of `impossible\|cannot\|can't\|unable\|barely (stand\|walk\|move)`. | stage 3 lines match (`quiet.py:54`) |
| W1-10 | The can is not the whole talk. | Speech acts of days 3–10 matching CAN ≤ 20%. | 63 of 245 = 25.7% |
| **W1-11** | **[added]** The world is in the leaver's own reasons. | At least one `went_out` night (nights 3–9) has a leaver whose bedtime reason, or whose trip position spoken that day, matches WATER. | no trip |

**What would make W1 wrong, by the counts:**
- W1-1 and W1-3 both fail, and W1-2 holds: honest words alone do not move the house, and W1-4's water talk is talk
  without acts. The next step is then the world's people (W2), not more body wording.
- W1-2 fails: the model is reading weakness into any body line. The wording is the first thing to cut, as
  `reports/quiet_day_design.md:115-117` already said of the stage lines.

## Counting rules (fixed with the plan; they spell out the table, they change no prediction)

All from `runs/v22/daniel_ate_it-seed2.transcript.json` and `.meta.json`, `cache/v22`'s seed 2 file (its prompts), and
`weather.Weather(2)`. They are read by `runs/w22/scoring/w1_score.py`, which gives the same rules for v21
(`runs/v21`, `cache/v21`) as the control column. Days 3–10 = the transcript's `day3` to `day10`; nights 3–9 = `night3`
to `night9`. Clock: day minute 0 is 07:00; 21:00 is minute 840.

- **A model act:** a day act with `mode == "model"`. **A speech act:** a model act with non-empty `words`.
- **W1-1.** The chronicle events (`chronicle.events`) with scene `N3` to `N9`. For each night and each leaver
  (`actor`, and every name in `members` of a `went_out`): 1 if the leaver has a `went_out` that night, else 1 if the
  leaver has a `got_up` or `at_door` that night, else 0. The sum is the count; the nights with any 1 are the
  different nights. PASS if the count ≥ 3 and the nights ≥ 2.
- **W1-2, W1-3.** As the table, from `night{n}["decisions"]`, `ask == "bedtime"`. W1-3 counts `option`.
- **W1-4.** The `words` of each speech act of day k, matched by WATER; PASS if ≥ 4 of the days 3–10 have ≥ 1.
- **W1-5.**
  - **(a)** For each qualifying spell (start between 07:00 and 21:00 of day k, k = 3–10, from `Weather(2)`), the set
    that must have heard it: the people not in `away` and not in a rest span (`quiet.spans`, routine `rest`, covering
    that minute) at the spell's start minute. The set that heard it: the `heard` list of the `quiet.rain` entry at
    that minute. 100% = every one of the first set is in the second. All such spells are checked.
  - **(b)** The "Q6 stretch" is the stretch (`quiet.stretches`) whose trigger is Q6 and whose start is that of the
    first qualifying spell. If Q6 did not fire for that spell (it was in played turns, it had fired today, nobody was
    awake: the Q6 entry in `quiet.log`), the acts from the spell's start to 30 minutes later are read instead, and
    the report says so. Its acts hold (b) if any is `collect_rain` or a speech act matching the regex.
  - **Reported:** the count of day acts `collect_rain` (days 3–10) and of bedtime decisions `rain_out` (nights 3–9).
- **W1-6.** The text read: the `words` of speech acts of days 3–10, and the `reason` and `say` of each decision of
  nights 3–9. The code's drinking store at a minute = `tap + rain` of `quiet.water` (the World's log: 07:00, each
  water rule, each bin set out, bedtime). A claim at a minute is a violation when the log entry at or before it shows
  `tap + rain` > 0 and the first entry after it (if any) does too. A claim between two entries that disagree is listed
  as unsure and not counted. A night's reason is read at that day's bedtime entry. PASS if violations ≤ 1.
- **W1-7.** The first `quiet.water` entry (by day and minute) with `tap + rain` < 50 gives day k. NOT TESTED if there is
  none by day 9 (k ≤ 9). Otherwise PASS if some model act with option `ration_water` or `save_water` has its
  `decided_at` at or before day k + 1, minute 840. When it was said, and by whom, is reported.
- **W1-8.** `answers_live` from the meta (the cap stop: 470 reported with how far it got); `day{k}_quiet.day_asks` for
  k = 3–10; the largest `estimate_tokens(system + prompt)` over every live prompt (the system of its scene: day,
  night or night mind), read from the cache file's entries after the 147 of `cache/v16`.
- **W1-9.** Every line starting "Your body:" in those same live prompts (day, night and night-mind prompts alike: a
  superset of the days and nights the table names). Matched by the pattern; every distinct line is listed with its count.
- **W1-10.** The CAN share of all speech acts of days 3–10; PASS if ≤ 20%.
- **W1-11.** The nights of 3–9 with a `went_out` event. For each leaver of each such night: their bedtime decision's
  `reason` in that night, or their speech act on the day before it (day k, for night k) whose option is a trip
  kind (`talk.act_of(option)[0] in world.TRIP_KINDS`), matched by WATER. PASS if any does. NOT TESTED if no night has
  a `went_out`.
- **Verdicts:** PASS / FAIL / NOT TESTED for each, with the evidence. If the run stops before it writes a transcript,
  the predictions that need it are NOT TESTED, and the report says how far the cache shows it got.
