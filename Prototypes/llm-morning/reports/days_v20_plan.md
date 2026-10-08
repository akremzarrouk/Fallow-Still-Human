# v20 plan: v16 seeds 2 and 3, days 3 to 5, on the outings facts, household knowledge and the evening moment

Mode: run. v16's seeds 2 and 3, played on to day 5 (`--days 5`), on the code at HEAD `361eb30`
(`reports/facts_and_evening.md`, `reports/household_knowledge.md`). Output `v20`: `runs/v20`, `cache/v20`.

**Why:** to see whether false statements about the past drop, whether the evening brings planning talk, and whether
the family acts on the houses further along, compared with v19 (`reports/days_v19.md`,
`reports/v19_contradictions.md`).

**How it runs:**
- **The cache.** `cache/v20` starts as a copy of `cache/v16` (seeds 2 and 3). Days 1–2, nights 1–2 and both night
  minds are answered from it.
- **The check before.** A no-API replay with `--days 5` must show seeds 2 and 3 going live first at day 3, min 00. If
  not, the run stops and is reported. The replay records the first prompt with no cached answer: its scene, speaker
  and "Now" line.
- **The runs.** Seed 2 runs live, then seed 3, each with `--days 5`, the second started after the first has exited.
  No seed is rerun or resumed. If a seed stops part way (exit 3), the run stops and is reported.
- **360 live asks in total.**
  - Each quiet day has its 40 day asks and Q5's own 8, so at most 48.
  - Nights 3–4 and minds 3–4 add the rest: at most about 2 × (144 + 24) = 336 for both seeds.
  - Each turn's stdout line prints "so far N live". If the two seeds' live count reaches 360, the running process is
    stopped by its own PID and the run is reported.
- **No edits after this plan is recorded.** Once it is recorded (sha256 and time, `runs/v20/plan_frozen.txt`), no
  code, test or line of this plan is edited.

## Predictions (frozen verbatim)

- H1: false statements about past events on days 3 to 5, counted by
  the method of reports/v19_contradictions.md, are at most 6 across
  both seeds (v19: 12).
- H2: Q5 fires on at least 3 of the 6 days, and at least one Q5 stretch
  contains a trip position act.
- H3: in at least 1 of the 2 seeds, someone chooses go_further at a
  bedtime on night 3 or 4.
- H4: from day 3 on, no prompt line shows a far act as "says he will not
  go" or "says she will not go", and no outings line says nobody has
  gone out to anyone in a seed where a trip happened before that day.
- H5: if a trip brings food home, the next day has at least 1 model act
  that eats, shares or gives; if someone does not come back, on the
  next day at least 2 of the others speak a line that names them (each
  part NOT TESTED if it does not happen).
- H6: in every seed where night 3 had any trip, at least half of day 4's
  morning speech acts use an (act kind, target) pair not used in day
  3's morning.
- H7: live asks at most 360 in total; every day at most 48 asks.

## Counting rules (fixed with the plan)

All from `runs/v20/daniel_ate_it-seed{2,3}.transcript.json` and `.meta.json`, and from a no-API replay of `cache/v20`
that records every prompt with its scene. They are read by `runs/v20/scoring/h_score.py`, written before any live
call.

**Common terms:** as in `reports/days_v19_plan.md`.
- **A model act:** a day act with `mode == "model"`.
- **A speech act:** a model act with non-empty `words`.
- **(act kind, target):** `talk.act_of(option)`.
- **A day's morning:** `quiet.stretches[0]`.
- **A bedtime choice:** a night decision with `ask == "bedtime"`.
- **A trip:** an entry of `night<k>.groups`.
- **Food comes home:** a group with `took ≥ 1` and `lost` null.
- **Someone does not come back on night k:** a person in `night<k>.away` and not in `night<k-1>.away`.
- **A trip position act:** a model act whose `act_of` kind is in `world.TRIP_KINDS`: propose, volunteer, object, back,
  decline, propose_far, volunteer_far.

**The rules:**
- **H1** is read by hand, as in `reports/v19_contradictions.md`.
  - **What is read.** Every speech act of days 3–5 in both seeds, against the chronicle (the transcript's
    `chronicle`) and the days' and nights' records.
  - **What counts.** A statement counts if it states something false about a past event: who did what, where, when,
    how often, or with what outcome. That includes a past event it implies that did not happen ("just like before"
    for a first trip).
  - **What does not count.** As in `reports/v19_contradictions.md` §4.3, idioms and characterizations are read and
    listed apart, not counted: "behind our backs" when the speaker saw it, "the empty houses" for an unsearched
    street, "without anyone saying a word".
  - **Repeats.** Each speech act counts once, however many false parts it has. The same false statement by the same
    speaker at different minutes counts each time, as in v19 (S2-3, S2-4, S2-5).
  - **The verdict.** PASS if the count is ≤ 6.
- **H2**, both parts needed for PASS:
  - Q5 fires on a day when that day's `quiet.log` has an entry with `kind == "Q5"` and `fired`. The first part holds
    if that is ≥ 3 of the 6 days (3 days × 2 seeds).
  - A Q5 stretch is a `quiet.stretches` entry with `trigger == "Q5"`. It contains an act if `start ≤ minute < end`.
    The second part holds if at least one such stretch contains a trip position act.
- **H3:** a bedtime choice of `go_further` on night 3 or 4. PASS if ≥ 1 seed has one.
- **H4:** every prompt sent from day 3 on (scenes day3, night3, mind3, day4, night4, mind4, day5), from the replay.
  - **Part 1.** A line matching `<Name> says (he|she) will not go: "<words>"` whose words are those of a
    `propose_far` or `volunteer_far` act in the transcript.
  - **Part 2.** A line beginning "About going out at night:" that contains "nobody has gone out", in a prompt of day k
    or night k, in a seed with a trip on any night before k.
  - PASS if both counts are 0.
- **H5:** as `reports/days_v19_plan.md` G3 and G4.
  - **Food.** For each night k (3 or 4) where food comes home, the next day holds if it has ≥ 1 model act whose
    option is `eat`, `eat_given`, `share` or begins `give_`.
  - **Loss.** For each person X who does not come back on night 3 or 4, the next day holds if ≥ 2 of the others in
    the house have a speech act naming X: X's name or the speaker's address for X, as a whole word,
    case-insensitive. NOT TESTED if fewer than 2 others are in the house.
  - Each part is PASS if every case holds, NOT TESTED if it has no case. H5 is PASS if neither part fails.
- **H6:** as G5. For each seed whose `night3.groups` is not empty, the day-4 morning's speech acts count when their
  pair is not the pair of any day-3 morning speech act. The seed holds if day 4's morning has ≥ 1 speech act and
  counted ≥ half. PASS if every such seed holds; NOT TESTED if neither seed had a trip on night 3.
- **H7:** from meta. The sum of `answers_live` ≤ 360, and each of `day3_quiet`, `day4_quiet` and `day5_quiet`
  `day_asks` ≤ 48.
