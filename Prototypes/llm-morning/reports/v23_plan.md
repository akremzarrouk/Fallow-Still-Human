# v23 plan: a week of family life at HEAD, against v22

Mode: run. Written before any live call. Paths are relative to `Prototypes/llm-morning/`.

**Goal.** See what a week of family life looks like now, against v22.

**Why.** `reports/stuck_facts.md`: in v22 (days 3 to 10) Mara's most-chosen option took half or more of her asks on all
8 days, 23 answer pairs were word for word equal, and Daniel said he was going 32 times and went once; the probes since
showed the loop is not held by any one prompt line. Since v22 the door, telling and the budget fixes were built, but no
full run has been seen.

## 1. The run

- **Code:** HEAD `cda05a22473a7d9f3042c2606afb710bb94c357c`, unchanged. No production code, test, prediction or seed
  is changed.
- **Seed and days:** v16 seed 2, `--days 10`, `--out v23`, the street on as the code has it (`morning.run` draws the
  street from day 3 when `days >= 3`; the seed's schedule if no knock is answered: one visit, day 6 09:27, no. 6,
  ask water).
- **Days 1 and 2, nights 1 and 2, minds 1 and 2:** replayed from `cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed2.json`,
  copied to `cache/v23/` (sha256 checked before and after). 0 live asks. Two guards:
  1. before the run, a replay with no key (`runs/v23/premiss.py`) must stop at its first miss in scene index 6
     (day 3), not earlier;
  2. the runner (`runs/v23/run_capped.py`) raises before any request if a live ask comes in day 1, night 1, mind 1,
     day 2, night 2 or mind 2. If either guard trips, the run stops and that is reported.
- **Days 3 to 10:** live at HEAD (`gemini-3.5-flash-lite`, config.json as it is).
- **Cap: 450 live asks.** The runner counts live asks and raises `CallCapReached` before the 451st request. If the cap
  stops the run, the report says where (day, minute).
- **Quota:** if the free quota stops the run (429 / quota), the stop is recorded (day, minute, live asks so far) and the
  run is resumed the next day from `cache/v23` with the same command; the cached answers replay, the cap counts the
  earlier session's live asks (`runs/v23/asks_live_before.txt`).
- **Key:** `GEMINI_API_KEY` from the environment, for the run's process only; it is written to no file.
- **The fake model first:** `runs/v23/run_capped.py --fake` (no API) runs the whole 10 days into `runs/v23/fake/` and
  `cache/v23/fake-…json`, and the scorer is run on it, before the plan is recorded.
- **Record before any live call** (`runs/v23/plan_frozen.txt`): this file's sha256, the UTC time, HEAD,
  `git status --short`, `git diff --stat`, and the sha256 of every `*.py` and `config.json`.

## 2. Predictions (word for word from the brief)

P1: the person-days whose most-chosen option takes at least 50% of that day's asks are fewer than v22's 20 of 32.

P2: at least 2 events from the street reach someone in the house (a knock heard, or words from outside) on days 3 to 10.

P3: word-for-word equal answer pairs (same person, same day) are fewer than v22's 23.

P4: whenever someone missed a visit, they are told of it by the end of the next day.

## 3. Counting rules

- **P1 and P3: as `reports/stuck_facts.md` section 1 counts them.** Unit: one person's asks in the day scene of one day
  (days 3 to 10), in the order asked; every ask of the day scene is counted (the door asks of a visit and the topic
  options included, as they are asks of the day with an option list). The most-chosen option is the commonest
  `option` id (ids, not kinds). A person-day counts for P1 when that count / the day's asks is >= 50%. P3: pairs of the
  unit's answers that have words (`silent` has no words and is not paired) whose `say`, lower-cased and trimmed, is the
  same. The asks are read from the runner's record (`runs/v23/asks*.json`) and checked, per day and person and in
  order, against the transcript's model acts (as `runs/stuck_facts/q1_repetition.py` checks v22). The scorer must
  reproduce v22's 20 of 32 and 23 from `runs/stuck_facts/asks_v22.json` before it scores v23.
  P1 holds if the count is under 20 (the number of person-days is reported beside it); P3 holds if the count is under 23.
- **P2.** An event from the street is a chronicle event of a day scene, days 3 to 10, of kind `knock` (a knock at the
  front door) or `door_line` (the visitor's words from outside), with at least one of the family among its witnesses.
  Each such event counts once, whatever the number of witnesses. P2 holds at 2 or more. The number of visits behind
  them is reported beside it.
- **P4.** A visit's events are the chronicle events of its day scene from the visit's start to its end of kind
  `knock`, `door_line`, `door_end` or `door_*`. Someone **missed** the visit if they are among none of those events'
  witnesses. They are **told** of it by the end of the next day if they hold a belief (`chronicle.beliefs`) whose
  `topic` is that visit, made on the visit's day or the next day. P4 holds if every one who missed a visit is told;
  it fails if any one is not. Someone away from the house at the visit (on a night trip, not back) and still away on
  the next day cannot be told, and is not counted (they are listed beside the verdict); someone away at the visit and
  home the next day is counted. **NOT TESTED if no one missed a visit** (including if no visit happens).
- **The scorer** is `runs/v23/scoring/score.py`. Before the record it reproduced v22's 20 of 32 and 23
  (`--control`) and ran on the fake run (`runs/v23/scoring/fake_score.txt`).

## 4. The report

`reports/v23.md`: the verdicts; a table per day (events from the world, trips, tells, the top option and its share per
person, equal pairs); for each day a short reading of whether a real family would live that day, and the worst
moment of the week, quoted; v22 beside v23; the commands with their outputs and the end checks (plan hash, `git diff`
empty, the key in no file). `merge-slice-docs.py` is run for `runs/v23`, then a commit.
