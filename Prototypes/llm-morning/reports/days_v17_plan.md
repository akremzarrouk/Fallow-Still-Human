# v17 plan: the first live run of the quiet day

Mode: run. v16 seeds 1 to 3, day 3 only, on the quiet day's stage A with its four fixes
(`reports/quiet_day_impl.md`, `reports/quiet_day_fixes.md`). Output `v17`: `runs/v17`, `cache/v17`.

**Why:** fakes cannot show whether a whole day reads human, or whether 40 asks leave the afternoon silent with the
real model.

**How it runs:**
- `cache/v17` starts as a copy of `cache/v16`. Days 1 and 2, nights 1 and 2 and both night minds come from it;
  only day 3 goes live.
- A no-API replay of each seed on `cache/v17` must stop at day 3 and nowhere earlier. If it does not, the run stops
  and is reported.
- Seeds 1, 2 and 3 run live one at a time, each started only after the one before has exited.
- No seed is rerun. At 150 live asks in total the run stops and is reported.
- Once this plan is recorded (sha256 and time, `runs/v17/plan_frozen.txt`), no code, test or line of this plan is
  edited.

## Predictions (frozen verbatim)

- D1: In every seed, at least one triggered stretch after the morning
  contains a model speech act.
- D2 (not a replay): in at least 2 of 3 seeds, at least half the speech
  acts of the first triggered stretch after the morning have an (act
  kind, target) pair not used in that seed's day-3 morning.
- D3: A model act at or after 16:00 happens in at most 1 of 3 seeds.
- D4: Of all model acts whose feeling, reason or words contain weak,
  dizzy, faint or "head spin", at least 90% are by someone with fasting
  of 48 or more at that minute.
- D5: No person uses tired, exhausted, weary, sleep, weak, dizzy or faint
  in the spoken words of 3 of their own model acts in a row.
- D6: N11, by the counting rule of the design's P2, appears on at most 2
  of the 3 days (v16: 3 of 3).
- D7: Each seed's day 3 uses at most 40 asks; live asks total at most
  130.

## Counting rules (fixed with the plan)

All from `runs/v17/<name>.transcript.json` (`day3`), `runs/v17/<name>.meta.json` and the entries of
`cache/v17/<model>-<name>.json` that are not in `cache/v16`.

**Common terms:**
- **A model act** is a day-3 act with `mode == "model"`. That includes a model-chosen `silent`.
- **A model speech act** is a model act with spoken `words`.
- **The morning** is the first played stretch, `day3.quiet.stretches[0]` (from min 00 to `morning_end`).
- **A triggered stretch** is any later stretch; its trigger is Q1 or Q2. An act is in a stretch if
  `start <= minute < end`.
- **(act kind, target)** is `talk.act_of(option)`. A target of `None` means "everyone".
- **A word list** matches case-insensitively, as a substring. So "sleep" matches "asleep" and "sleepless", and
  "weak" matches "weakness".

**The rules:**
- **D1.** Per seed: some triggered stretch holds ≥ 1 model speech act. PASS if all 3 seeds do.
- **D2.** Per seed, take the first triggered stretch and its model speech acts.
  - An act counts if its (act kind, target) is not the pair of any model speech act in that seed's day-3 morning,
    by anyone.
  - The seed holds if the stretch has ≥ 1 speech act and counted acts ≥ half of them.
  - A seed with no triggered stretch, or none with speech, does not hold.
  - PASS if ≥ 2 seeds hold.
- **D3.** Per seed: some model act at minute ≥ 540 (16:00). PASS if at most 1 seed has one.
- **D4.**
  - **The answers:** each new cache answer's `feeling`, `reason` and `say` are read from its response. The answer
    is matched to its model act by speaker ("You are X,"), by the prompt's "Now" minute, and by option.
  - **The acts:** those where one of the three fields contains weak, dizzy, faint or "head spin".
  - **Fasting at the act's minute:** the last `day3.quiet.needs[pid]` entry at or before that minute, plus
    (minutes since) / 60 × the person's hunger rate. If they ate in between, it is counted from the meal.
  - **Verdict:** PASS if ≥ 90% of those acts have fasting ≥ 48. NOT TESTED if there are no such acts.
- **D5.**
  - **The sequence:** each person's model acts in order, `decided_at`. A model act with no words breaks a run.
  - **The words:** tired, exhausted, weary, sleep, weak, dizzy or faint, in the act's spoken words.
  - **Verdict:** FAIL if any person has 3 consecutive model acts whose words all contain one of them.
- **D6.** P2's rule (`reports/quiet_day_design.md` §7) on each seed's day 3, with `days_v15.md` §8's groupings.
  - **The kinds:** accuse, confront, reassure, ask and deny. Also one volunteer kind (`volunteer`, `still_going`,
    `propose_trip`) and one against kind (`nobody_goes`, `keep_*_home`, the `object` kind).
  - **A run:** one person's ≥ 3 consecutive model acts (a model `silent` breaks it) of one kind, at one target (or
    all at everyone).
  - **One conversation:** every act in the run falls between the same `started` and the next `ended` of its room
    in `convo_log`.
  - **The target clause:** for a run aimed at one person, that person's model acts with `decided_at` between the
    run's first and last act are all of one kind (true if there are none). A run at everyone has no target clause.
  - **Verdict:** PASS if ≤ 2 of the 3 days have such a run. The same script is run on v16's day 3s first, as a check
    that it gives v16's 3 of 3.
- **D7.** From meta: `day3_asks` ≤ 40 in each seed, and the sum of `answers_live` over the three seeds ≤ 130.
