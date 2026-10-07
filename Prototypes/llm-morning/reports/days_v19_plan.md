# v19 plan: v16 seeds 2 and 3, days 3 to 5, with stage B

Mode: run. v16's seeds 2 and 3, played on to day 5 (`--days 5`), on the code at HEAD `e49aadc` (`reports/stage_b.md`,
`reports/stage_b_fixes.md`, `reports/multiday.md`). Output `v19`: `runs/v19`, `cache/v19`.

**Why:** to see whether the family's story moves over several days now that bodies weaken, the houses further along
exist, and food or loss can change the house.

**How it runs:**
- `cache/v19` starts as a copy of `cache/v16` (seeds 2 and 3). Days 1–2, nights 1–2 and both night minds are answered
  from it.
- A no-API replay with `--days 5` must show seeds 2 and 3 going live first at day 3, min 00. If it does not, the run
  stops and is reported. The replay records the first prompt with no cached answer: its scene, speaker and "Now" line.
- Seed 2 runs live, then seed 3, each with `--days 5`, the second started after the first has exited. No seed is
  rerun or resumed. If a seed stops part way (exit 3: quota, rate limit, call cap), the run stops and is reported.
- **360 live asks in total.** The code caps each quiet day at 40 day asks (`quiet.DAY_ASKS`), so days 3–5 give at
  most 120 a seed; nights 3–4 and minds 3–4 add the rest. Each turn's stdout line prints "so far N live". If the two
  seeds' live count reaches 360, the running process is stopped by its own PID and the run is reported.
- Once this plan is recorded (sha256 and time, `runs/v19/plan_frozen.txt`), no code, test or line of this plan is
  edited.

## Predictions (frozen verbatim)

- G1: in at least 1 of the 2 seeds, someone chooses go_further at a
  bedtime on night 3 or night 4.
- G2: across both seeds, at least 1 day speech act is propose_far or
  volunteer_far.
- G3: if a trip brings food home, the next day has at least 1 model act
  that eats, shares or gives (NOT TESTED if no food comes home).
- G4: if someone does not come back, on the next day at least 2 of the
  others speak a line that names them (NOT TESTED if nobody is lost).
- G5: in every seed where night 3 had any trip, at least half of day 4's
  morning speech acts use an (act kind, target) pair not used in day
  3's morning.
- G6: nobody who knows next door is empty chooses go_next_door.
- G7: live asks at most 360 in total; every day at most 40 asks.

## Counting rules (fixed with the plan)

All from `runs/v19/daniel_ate_it-seed{2,3}.transcript.json` and `.meta.json`, read by
`runs/v19/scoring/g_score.py`, written before any live call.

**Common terms:**
- **The live part:** days 3, 4 and 5 and nights 3 and 4 (transcript keys `day3`, `night3`, `day4`, `night4`, `day5`).
- **A model act:** a day act (`day<k>.turns[*].acts[*]`) with `mode == "model"`.
- **A speech act:** a model act with non-empty `words`.
- **(act kind, target):** `talk.act_of(option)`.
- **A day's morning:** minutes in `[quiet.stretches[0].start, quiet.stretches[0].end)` of that day.
- **A bedtime choice:** a night decision with `ask == "bedtime"`; its choice is its `option`.
- **A trip on night k:** an entry of `night<k>.groups`.
- **Food comes home on night k:** a group of `night<k>` with `took ≥ 1` whose `lost` is null. Its next day is
  `day<k+1>`.
- **Someone does not come back on night k:** a person in `night<k>.away` who was not in `night<k-1>.away` (night 2 is
  `night2`). Their next day is `day<k+1>`.
- **Knows next door is empty, at a bedtime:** that person's bedtime decision offers `go_further` among its options.
  The code offers it exactly when `knows_empty` is set (`night.py:392`).

**The rules:**
- **G1:** a bedtime choice of `go_further` on night 3 or 4, in a seed. PASS if ≥ 1 of the 2 seeds has one.
- **G2:** model acts on days 3–5, both seeds, whose `option` is `propose_far` or `volunteer_far`. PASS if ≥ 1.
- **G3:** for each seed and night k (3 or 4) where food comes home, its next day holds if it has ≥ 1 model act whose
  option is `eat`, `eat_given`, `share` or begins `give_`. PASS if every such case holds; NOT TESTED if there are
  none.
- **G4:** for each seed, night k (3 or 4) and person X who does not come back that night: the others are the people
  in the house on the next day (not X, not in that night's `away`). A speaker counts if they have ≥ 1 speech act on
  the next day whose words name X: X's first name, or the address the speaker uses for X (`data.ADDRESS`, so "Mom"
  for Elena), as a whole word, case-insensitive. The case holds if ≥ 2 speakers count. If fewer than 2 others are in
  the house, the case is NOT TESTED. PASS if every tested case holds; NOT TESTED if nobody is lost.
- **G5:** for each seed whose `night3.groups` is not empty: the day-4 morning's speech acts count when their pair is
  not the pair of any day-3 morning speech act, by anyone. The seed holds if day 4's morning has ≥ 1 speech act and
  counted ≥ half of them. PASS if every such seed holds; NOT TESTED if neither seed had a trip on night 3.
- **G6:** bedtime choices on nights 3 and 4, both seeds, by someone who knows next door is empty (above), whose choice
  is `go_next_door`. PASS if there are 0. NOT TESTED if no bedtime decision offered `go_further`.
- **G7:** from meta: the sum of the two seeds' `answers_live` ≤ 360, and each day's asks ≤ 40: `day3_asks`,
  `day4_quiet.day_asks`, `day5_quiet.day_asks`. PASS if all hold.
