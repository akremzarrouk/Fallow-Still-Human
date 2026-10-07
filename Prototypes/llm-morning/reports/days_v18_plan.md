# v18 plan: day 3 again, with the meeting lines and cooling

Mode: run. v17's three seeds, day 3 only, on the code of `reports/meeting_fixes.md`: meeting lines, cooling after a
rest of an hour or more, "today" headings from minute 90, short rests not counted. Output `v18`: `runs/v18`,
`cache/v18`.

**Why:** v17 failed D2 in all 3 seeds. `reports/v17_meetings.md` traced it to meetings the prompt never described,
and to a grudge of 3 that fed itself all day. Both are now changed.

**How it runs:**
- `cache/v18` starts as a copy of `cache/v17`. Days 1–2, nights 1–2, both night minds and each seed's day-3 morning
  are answered from it.
- A no-API replay must show each seed going live first at its first ask after the morning. If it does not, the run
  stops and is reported.
- Seeds 1, 2 and 3 run live one at a time, each started after the one before has exited. No seed is rerun.
- At 100 live asks in total, the run stops and is reported. By the code, at most 18 + 28 + 16 = 62 can go live:
  each seed's 40 day-3 asks, less its cached morning (22, 12, 24).
- Once this plan is recorded (sha256 and time, `runs/v18/plan_frozen.txt`), no code, test or line of this plan is
  edited.

## Predictions (frozen verbatim)

- E1 (D2 again): in at least 2 of 3 seeds, at least half the speech acts
  of the first triggered stretch after the morning use an (act kind,
  target) pair not used in that seed's day-3 morning.
- E2: among spoken lines after the morning, the share containing any of
  "snuck", "sneak", "went out", "came back", "with nothing",
  "empty-handed", "took the food", "promise" (case-insensitive) falls by
  at least a third from v17's share.
- E3: at most 80% of Leo's and Mara's answers after the morning name
  Daniel as angry_at (v17: 59 of 59).
- E4: in at least 1 seed, a speech act after the morning is of a kind
  other than confront, accuse or reassure.
- E5: live asks total at most 100, and each seed's day 3 at most 40.

## The v17 baselines, computed before any live call

From `runs/v18/scoring/scripts/e_score.py v17` (`runs/v18/scoring/baseline_v17.txt`):

| | Seed 1 | Seed 2 | Seed 3 | All |
|---|---|---|---|---|
| E1: first triggered stretch, speech acts with a pair new to the morning | 1 of 8 | 2 of 8 | 0 of 8 | 0 of 3 seeds hold |
| **E2: spoken lines after the morning with an E2 phrase** | 7 of 16 | 16 of 27 | 7 of 15 | **30 of 58 = 0.5172** |
| E3: Leo's and Mara's answers after the morning naming Daniel | 8 of 8 | 15 of 15 | 8 of 8 | 31 of 31 |
| E4: speech acts after the morning of another kind | none | none | none | 0 of 3 seeds |
| E5: live asks; day-3 asks | 40; 40 | 40; 40 | 40; 40 | 120 |

**E2 passes if v18's pooled share is at most 2/3 × 0.5172 = 0.3448.**

**On E3's "v17: 59 of 59":** that figure (`reports/v17_meetings.md` §4) counts all of Leo's and Mara's day-3 answers,
the morning's included. After the morning, as E3 counts, v17 is 31 of 31. The prediction is kept verbatim; its 80%
threshold does not depend on the baseline.

## Counting rules (fixed with the plan)

All from `runs/v18/<name>.transcript.json` (`day3`), `runs/v18/<name>.meta.json` and the entries of
`cache/v18/<model>-<name>.json` not in `cache/v17`. The same script scores v17 and v18: `e_score.py`.

**Common terms:**
- **After the morning:** minute ≥ `day3.quiet.morning_end`.
- **A spoken line, or speech act:** a day-3 act with `mode == "model"` and spoken `words`.
- **(act kind, target):** `talk.act_of(option)`.

**The rules:**
- **E1:** as v17's D2 (`reports/days_v17_plan.md`).
  - The first triggered stretch is `stretches[1]`. Its speech acts count when their pair is not the pair of any
    speech act in the morning (`stretches[0]`), by anyone.
  - A seed holds if that stretch has ≥ 1 speech act and counted ≥ half. PASS if ≥ 2 seeds hold.
- **E2:** pooled over the three seeds.
  - A line counts if its words, lower-cased, contain any of the eight phrases as a substring. So "sneak" matches
    "sneaking", "promise" matches "promised", and "empty handed" without the hyphen does not match.
  - PASS if v18's share ≤ 0.3448.
- **E3:** pooled. The answers are the new cache entries whose prompt begins "You are Leo," or "You are Mara," and
  whose "Now" minute is after the morning. Each answer's `angry_at` is read from its response.
  - PASS if those naming "Daniel" are ≤ 80% of them. NOT TESTED if there are none.
- **E4:** a speech act after the morning whose `act_of` kind is not confront, accuse or reassure (`reassure_all` is
  reassure). PASS if ≥ 1 seed has one.
- **E5:** from meta: the sum of `answers_live` ≤ 100, and each `day3_asks` ≤ 40.
