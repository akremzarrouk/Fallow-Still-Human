# Calm variants: plan (frozen before any live call)

Mode: run. The question: which prompt change, if any, lets people tell Daniel about the visit in a quiet moment?

`reports/calm_probe.md` found 0 tells in 14 offers. Each person's 10:00 and 10:30 prompts differed only in the "Now"
line, and every prompt ended on the 09:48 quarrel, so the moment never read as quiet. `tell_daniel_visit` sat 18th
or 19th of 27 or 28 options. This probe changes the two things that report points at, one at a time and together.

## Predictions (word for word, as given)

P1: in T, a tell_*_visit option is chosen in at least 3 of the asks that offered one.

P2: in O, a tell_*_visit option is chosen in at least 5 of the asks that offered one.

P3: in T, at least 6 of the 18 answers choose a different option than calm_probe's answer for the same person and minute.

P4 (validity): no answer chooses an option that was not offered.

Decision rule: if T meets P1, the fix is the time line; if only O meets P2, option order is needed; if neither, telling needs another route. A variant where tells are chosen in 12 or more of 14 is flagged as over-steered.

The baseline is calm_probe's 18 answers (`runs/calm_probe/scene1.json`, `scene3.json`).

## The probe (`runs/calm_variants/probe.py`)

- **Replay.** As `runs/calm_probe/probe.py`: scenes 1 and 3 of the talk probe, each played again from a copy of
  `cache/talk_probe/scene<k>.json`. The replay's client refuses every ask (0 live asks in the replay).
- **The 18 calm prompts.** At 10:00, 10:30 and 11:00, each awake person in Daniel's room who knows the visit
  first-hand. Each prompt is rebuilt as calm_probe built it (`World.prompt_for(p, t, World.options_for(p))`) and
  checked equal to the prompt calm_probe recorded for that person and minute. If one differs, the scene stops.
- **The client seeds:** 201 for scene 1, 202 for scene 3 (calm_probe's).
- **The three variants**, changed in the probe only:
  - **T.** One line is added right before the line that starts "Now, ":
    `Nobody in the kitchen has said anything since 09:48, <n> minutes ago; you have all stayed sitting here.`
    It is built from the replay's state:
    - the last minute at which anyone in that room spoke: the latest act in the room, in the replay's transcript,
      whose option is speech or which has words;
    - n is the ask's minute minus that minute (12 at 10:00, 42 at 10:30, 72 at 11:00).
    It is checked true before use, or the scene stops:
    - no act of any kind after that minute;
    - everyone now in the room acted in it at that minute;
    - at every quiet step and quiet jump since, each of them was in the room and not resting;
    - each of them is now "sitting in the kitchen".
    It names no act, option or person to speak to. Nothing else in the prompt changes.
  - **O.** The topic options (ids starting `talk_` or `tell_`) are moved to the top of the option list, in their
    order; the rest follow in their order. The probe checks that only the order of the option lines changed. In
    these prompts the only topic option is `tell_daniel_visit`, which goes from 18th or 19th to 1st.
  - **TO.** The T line added to the O prompt.
- **No prompt is asked twice.** Four of the 18 calm prompts offer no topic option (Leo in scene 1 at 10:00 and
  10:30; Mara in scene 3 at 10:00 and 10:30: F2 holds the visit back). There:
  - the O prompt is calm_probe's prompt, so calm_probe's answer (same client seed) is taken and not asked again;
  - the TO prompt is the T prompt, so T's answer is taken.
  So the 54 rows hold **46 live asks** (18 T, 14 O, 14 TO) and 8 answers taken from an identical prompt.
- **Answers are not applied.** The answer is recorded and never applied, as in calm_probe; the scene stops after
  11:00's asks.
- **The fake run** (`runs/calm_variants/fake.stdout.txt`): exit 0, 0 live asks in the replay. All 18 prompts are equal
  to calm_probe's. The T line holds in all 18, and `tell_daniel_visit` is 1st in every O and TO prompt that offers
  it. 46 fake asks.

## How P1 to P4 are counted

- **P1.** In T, take the asks whose offered options include an option `tell_<names>_visit` (14). Count those whose
  answer's `option` is one of them. P1 holds at 3 or more.
- **P2.** The same count in O (14 asks). P2 holds at 5 or more.
- **P3.** Of T's 18 answers, count those whose `option` differs from calm_probe's answer for the same scene, person
  and minute. P3 holds at 6 or more.
- **P4.** For all 54 rows, the answer's `option` is in that row's offered options. An answer that cannot be parsed
  counts as choosing nothing offered, and P4 fails.
- **Over-steered.** Any of T, O or TO where a tell is chosen in 12 or more of its 14 asks that offered one.
- **The decision rule** is applied as written. TO is reported beside it and carries no prediction.

## Order of work and limits

1. `probe.py --fake`: done before this plan was frozen.
2. Record this plan's sha256 and the probe's, the UTC time and HEAD (`runs/calm_variants/plan_frozen.txt`).
3. `probe.py --live`. Cap: 60 live asks. The key comes from `GEMINI_API_KEY` and is written to no file. Each scene
   runs once (the ledger), and no prompt is asked twice.
4. Read the records. Then the end checks: the plan's hash, `git diff` empty, and a search for the key in every file.
