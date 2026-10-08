# v21 plan: v16 seed 2, days 3 to 10, the first 10-day live run

Mode: run. v16's seed 2, played on to day 10 (`--days 10`), on the code at HEAD `91380e4` (`reports/ten_days_prep.md`:
yesterday's positions end with what happened that night, and a third fasting stage at 144). Output `v21`: `runs/v21`,
`cache/v21`.

**Why:** to learn what happens to a family over ten days: whether desperation ever moves a quiet house, whether false
statements grow, whether days keep repeating, and whether prompts stay bounded in a live run.

**How it runs:**
- **The cache.** `cache/v21` starts as a copy of `cache/v16`'s seed 2 file. Days 1–2, night 1–2 and minds 1–2 are
  answered from it.
- **The check before.** A no-API replay with `--days 10` must show seed 2 going live first at day 3, min 00. If not,
  the run stops and is reported. The replay records the first prompt with no cached answer: its scene, speaker and
  "Now" line.
- **The run.** Seed 2 runs live once, `--days 10`, out `v21`. It is not rerun or resumed. If it stops part way (exit
  3), the run stops and is reported with how far it got.
- **The 450 cap.** The run is started through `runs/v21/run_capped.py`, which sets `sys.argv` to
  `morning.py --seed 2 --out v21 --days 10` and calls `morning.main()`. Its one addition is a counter on
  `GeminiClient.generate`: when 450 live asks have been sent, the next one raises `gemini.CallCapReached` (a
  `StopMorning`) before any request goes out. No prompt, option or answer is changed. If that happens the run exits 3
  and is reported with how far it got. Nothing is killed.
- **The key.** The run uses an API key the user gave in chat for this one run, as the process's `GEMINI_API_KEY`. It is
  written nowhere.
- **No edits after this plan is recorded.** Once it is recorded (sha256 and time, `runs/v21/plan_frozen.txt`), no
  code, test or line of this plan is edited. The scorer `runs/v21/scoring/t_score.py` and `run_capped.py` are new
  files, written after the plan and before the first live call; they are checked on a no-API fake run.

## Predictions (frozen verbatim)

- T1: someone goes out on at least one of nights 3 to 9.
- T2: no prompt's size estimate exceeds 2600, and the memory bound
  removes no line of blocks A, B or C on any morning.
- T3: false statements about past events on days 3 to 10, counted by
  the method of reports/v19_contradictions.md, are at most 10.
- T4: on at least 3 of days 4 to 10, at least half of the morning's
  speech acts use an (act kind, target) pair not used in the previous
  day's morning.
- T5: someone reaches the third fasting stage, and nobody uses tired,
  exhausted, weary, sleep, weak, dizzy, faint or "stand" in the spoken
  words of 3 of their own model acts in a row.
- T6: if a trip brings food home, the next day has at least 1 model act
  that eats, shares or gives; if someone does not come back, on the
  next day at least 2 of the others speak a line that names them (each
  part NOT TESTED if it does not happen).
- T7: live asks at most 450; every day at most 48 asks.

## Counting rules (fixed with the plan)

All from `runs/v21/daniel_ate_it-seed2.transcript.json` and `.meta.json`, and from a no-API replay of `cache/v21`
(a temp copy, `--days 10`) that records every prompt with its scene and every call of the memory bound. They are read
by `runs/v21/scoring/t_score.py`. If the run stops before it writes a transcript (exit 3), the predictions that need
it are NOT TESTED, and the report says how far the cache shows it got.

**Common terms:** as in `reports/days_v20_plan.md`.
- **A model act:** a day act with `mode == "model"`.
- **A speech act:** a model act with non-empty `words`.
- **(act kind, target):** `talk.act_of(option)`.
- **A day's morning:** `quiet.stretches[0]`.
- **A trip:** an entry of `night<k>.groups` (night 1 is the key `night`).
- **Food comes home:** a group with `took ≥ 1` and `lost` null.
- **Someone does not come back on night k:** a person in `night<k>.away` and not in `night<k-1>.away`.

**The rules:**
- **T1.** PASS if any of `night3` to `night9` has a non-empty `groups`. (Night 10 does not exist: day 10 is the
  last.) Reported: for each night, the bedtime choices and the groups.
- **T2**, both parts needed for PASS.
  - **Part 1, size.** For every prompt asked from day 3 on (scenes day3 to day10, night3 to night9, mind3 to mind9),
    the size estimate is `world.estimate_tokens(system + prompt)`, as `max_prompt_tokens` counts it. PASS if the
    largest is ≤ 2600. Cross-check: the meta's `max_prompt_tokens_estimated`.
  - **Part 2, the memory bound.** Every call of `memory.bounded` during a morning scene (day3 to day10), one per
    person per morning. It removes a line if block A is not its first (longest) variant, or if any C thought, C line
    or B line was removed. PASS if no call removes a line.
- **T3** is read by hand, as in `reports/v19_contradictions.md` and `reports/days_v20_plan.md` H1.
  - **What is read.** Every speech act of days 3–10, against the chronicle (the transcript's `chronicle`) and the days'
    and nights' records.
  - **What counts.** A statement counts if it states something false about a past event: who did what, where, when,
    how often, or with what outcome, including a past event it implies that did not happen. A false number counts, as
    v20 counted "You took everything" (H1 #1 and #2).
  - **What does not count.** Idioms, characterizations, causes and claims about the present are read and listed apart,
    as in `reports/v19_contradictions.md` §4.3 and `reports/days_v20.md` §4.
  - **Repeats.** Each speech act counts once, however many false parts it has; the same false statement at different
    minutes counts each time.
  - **The verdict.** PASS if the count is ≤ 10. Each counted statement is listed with the true fact.
- **T4.** For each day k from 4 to 10 that exists: day k's morning speech acts count when their pair is not the pair of
  any speech act of day k−1's morning. Day k holds if its morning has ≥ 1 speech act and 2 × counted ≥ the speech
  acts. PASS if ≥ 3 of the days 4 to 10 hold. A day the run did not reach does not hold.
- **T5**, both parts needed for PASS.
  - **Part 1.** Someone reaches the third fasting stage: a `quiet.need_events` entry with `need == "fast"` and
    `stage == 3`, on any of days 3–10.
  - **Part 2.** For each person, their speech acts (model acts with words) from day 3 on, in order of `decided_at`
    across all days. A word of the list is matched as a whole word that begins with one of: tired, exhaust, weary,
    sleep, weak, dizz, faint, stand (so "sleeping" and "standing" count; "understand" does not), case-insensitive.
    FAIL if any person has 3 of these speech acts in a row, each with such a word.
- **T6:** as `reports/days_v20_plan.md` H5.
  - **Food.** For each night k (3 to 9) where food comes home, the next day holds if it has ≥ 1 model act whose option
    is `eat`, `eat_given`, `share` or begins `give_`.
  - **Loss.** For each person X who does not come back on night k (3 to 9), the next day holds if ≥ 2 of the others in
    the house (not away) have a speech act naming X: X's name or the speaker's address for X, as a whole word,
    case-insensitive. NOT TESTED if fewer than 2 others are in the house.
  - Each part is PASS if every case holds, FAIL if one does not, NOT TESTED if it has no case. T6 is PASS if neither
    part fails, NOT TESTED if both are.
- **T7:** from the meta. `answers_live` ≤ 450 (also reported: `api_requests`), and each of `day3_quiet` to
  `day10_quiet` has `day_asks` ≤ 48. If the cap stops the run, T7's first part holds at exactly 450 and the report
  says how far the run got.
