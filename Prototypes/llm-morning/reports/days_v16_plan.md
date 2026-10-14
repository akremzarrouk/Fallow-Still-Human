# Three days, v16: the plan, frozen before the first live call

Mode: run. Live test of the two fixes committed at `b72f758` (block C pattern lines, `reports/c_patterns.md`; the
four night-mind check errors, `reports/check_errors.md`) on the three v15 seeds of `daniel_ate_it`, output `v16`.

**Why:** both pass offline, but only a live run shows whether day 1 now reaches day-3 speech, and whether "you
denied 6 times" pulls Daniel back into denying.

## Predictions (verbatim from the brief)

- P1: Seed 3, day 3: people referring to a day-1 event (M1's rule) rise from 1 to at least 2.
- P2: Seed 3: Daniel makes 0 deny acts on day 3.
- P3: Each of the 4 restored memories that its seed produces again reaches the next day's prompt.
- P4: No kept memory says someone found food on a trip that came back with nothing.
- P5: M1 to M6, scored with v15's rules, give the same verdicts as v15 except M1.
- P6: Live asks for all 3 seeds total at most 200.

## How each is read (fixed now, before any run)

- **P1:** v15's M1 hand reading (`reports/days_v15.md` §6, M1), applied to seed 3's day-3 acts (words and reasons),
  counted by person. v15's count was 1 (Leo).
- **P2:** day-3 acts of Daniel in seed 3 whose option is `deny`, from the transcript.
- **P3:** the 4 are seed 1 mind 1 Elena ("…found Daniel's bed empty…"), seed 1 mind 1 Mara's intent ("…ask Daniel
  why he went out…"), seed 1 mind 2 Daniel ("I lay awake in the dark with Leo…"), seed 3 mind 2 Elena ("…I stayed in
  bed while my children took risks."). "Produces again" means the same text is proposed again by that night mind.
  Each one produced again must be kept and appear in at least one of that person's next-day prompts (`cache/v16`).
  One not produced again is NOT TESTED.
- **P4:** every kept memory of v16 (minds 1 and 2, seeds 1–3) read for a find of food (or any food word after
  "found"/"find") by someone whose trip that night came back with nothing.
- **P5:** M2 to M6 scored with v15's counting rules and scripts; PASS if each equals v15's verdict (M2 FAIL, M3 PASS,
  M4 PASS, M5 PASS, M6 PASS). M1 is scored and reported, but not part of P5.
- **P6:** sum of `answers_live` in the three `runs/v16/*.meta.json`.

## How it runs

1. This plan is committed before the first live call.
2. HEAD clean (tracked files) and the full suite passes, with `GEMINI_API_KEY` unset.
3. `cp cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v16/` for N = 1, 2, 3, so a prompt identical to
   a v15 prompt is answered from v15's answer and only changed prompts go live.
4. `python morning.py --seed N --out v16`, for N = 1, then 2, then 3, each started only after the one before exited.
   No seed is rerun. If total live asks reach 250, the run stops and this is reported.
5. Scored with the v15 scripts (`reports/days_v15.md` §12) and counting rules, unchanged except the run folder
   (`v15` → `v16`). No code, test, counting rule or prediction is edited after this commit.
