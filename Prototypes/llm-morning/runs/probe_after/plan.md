# Plan: after the door

Mode: run. Written, hashed and recorded before any live call (`runs/probe_after/plan_frozen.txt`). Not changed after.
Paths are relative to `Prototypes/llm-morning/`.

## What it asks

What the family does after a stranger leaves: does Elena answer Mara's give over her refusal, and what does each keep
that night? `reports/probe_door2.md` stopped at the knock's minute. Everything after it in
`reports/door_after_facts.md` (and in the traces of `reports/door_memory_impl.md` and `reports/budget_fix_impl.md`)
was the fake model's.

## How

`runs/probe_after/probe.py --live`, code at HEAD; no production file, test or prediction is changed. It is
`runs/probe_door2/probe.py` (visitors, client seeds, cap, ledger) joined with the full mode of
`runs/door_after/trace.py` (the day to bedtime, night 3, the night minds, day 4's blocks).

- **Scenes 1, 3 and 4 only**, each with probe_door2's visitor and client seed:

  | Scene | Visitor | Client seed | probe_door2 at 09:42 |
  |---|---|---|---|
  | 1 | h13, a woman of about 45, no child, helper | 101 | Elena `door_refuse`; Mara `door_give`; Leo `save_water`: given |
  | 3 | h16, a woman of about 55, a boy of 6, helper | 103 | Elena `door_refuse`; Mara `door_give`; Leo `save_water`: given |
  | 4 | h23, a woman of about 45, a girl and a boy of 5, helper | 104 | Elena `door_refuse`; Mara `door_look`; Leo `silent`: refused |

- **The cache.** Scene k's cache, `cache/probe_after/scene<k>.json`, starts as a copy of
  `cache/probe_door2/scene<k>.json`. So days 1 and 2, nights 1 and 2, the morning of day 3 and the three asks at 09:42
  are probe_door2's answers. The cache key keeps the run's seed (2); the client sends seed 100+k.
- **No live ask before the visit ends (09:45).** The client refuses any ask until `door_end` has run; an ask before it
  that is not in the copied cache stops the scene. The fake check found all of them in the cache: 123 per scene
  (120 to the knock, 3 at 09:42).
- **Live from 09:45:** the rest of day 3, night 3 and the night minds. Then day 4 is set up (`night.next_day`) and its
  blocks A, B and C recorded. Day 4 is not played.
- **Cap: 200 live asks** in all three scenes. The probe stops cleanly there, keeping what the scene reached.
- **No scene is run twice.** A scene is written to `runs/probe_after/ledger.json` as it starts; a scene in the ledger
  is skipped, even if it stopped part way. The key is the process's `GEMINI_API_KEY` only, written to no file.
- **The record** (`runs/probe_after/scene<k>.json`): every decision from 09:42 (option, words, feeling, reason,
  triggers, quiet trigger, order); every ask from 09:42 with its prompt, answer and source (cache or live), night and
  night-mind asks included; the quiet log and the stretches; the door scene; each one's memory and sure lines; grudges,
  suspicion, guilt and feeling before the knock, at the visit's end and at the end of the day; day 3's door events in
  the chronicle; night 3's lines; each night mind's input, answer and kept memories; day 4's blocks; block C on house
  day 8.

**Checked with the fake model first** (`runs/probe_after/fake.stdout.txt`, `probe.py --fake`, in a temp folder, no
key): exit 0. Each scene reached day 4's blocks; 123 asks from the cache per scene; fake asks 39, 41 and 37 (117 in
all): in scene 1, 29 of day 3 from 09:45, 6 of night 3 and 4 night minds.

## Predictions

Copied word for word from the brief:

  P1: in at least 1 of scenes 1 and 3, Elena, between 09:45 and the Q7 stretch's end, chooses an option aimed at Mara, or says words to anyone that mention the water, the door or the woman.
  P2: in at least 1 of scenes 1 and 3, Elena's night mind keeps a memory citing one of the door events (the refusal, the give, or the visit's end).
  P3: in each of the 3 scenes, at least 1 Q1 or Q2 fires between 10:00 and 19:00.
  P4: in scene 4, Mara's words at any ask after 09:45, or her night mind's kept memories, mention the visitor or the children.

## How each is read (fixed before the run)

- **P1.** Elena's decisions asked of the model (`mode` model) at minutes from 09:45 up to and including the minute the
  scene's Q7 stretch ends (`stretches`, trigger Q7, `end`). "An option aimed at Mara": an option whose name ends in
  `_mara` (for example `confront_mara`, `aside_mara`, `reassure_mara`, `sit_mara`, `send_mara`). "Words that mention the
  water, the door or the woman": her `say` refers to the stored water, the front door, the visit, or the woman; each such
  `say` is quoted in the report. Holds if this is found in scene 1 or scene 3.
- **P2.** Elena's night-3 mind: a memory with verdict `kept` whose `ids` include the id of that scene's day-3
  chronicle event of kind `door_refuse`, `door_give` or `door_end`. Holds if found in scene 1 or scene 3.
- **P3.** In the scene's quiet log, an entry of kind Q1 or Q2 with `fired` true at a minute from 10:00 to 19:00
  (minutes 180 to 720). Holds if each of the 3 scenes has one.
- **P4.** Scene 4 only. Mara's `say` at any ask after 09:45 (day 3 and night 3), or the `meaning` of a kept night-3
  memory of hers, refers to the visitor (the woman, the person at the door, the stranger, the mother who asked) or to
  the children (a child, the children, the girl, the boy, the five-year-olds). Each such line is quoted in the report.
- **NOT TESTED**, with the reason, if a scene did not reach the point a prediction reads (the cap, a stop, a refusal of
  the API), or the thing it reads did not occur (for example, no ask of Elena in the stretch's window is still read:
  it is a fail, not NOT TESTED, if the stretch ran and she was not asked).

## Deliverable

`reports/probe_after.md`: the verdicts; for each scene every decision from 09:45 to the Q7 stretch's end in full
(option, words, feeling, reason), every later act that mentions the door, the water given or the visitor, each night
mind's kept memories, and day 4's block A and B door lines; for each scene a reading of whether a real family in that
room would do this, and why; the commands with their outputs; the end checks (plan hash, `git diff` empty, key in no
file). Then `merge-slice-docs.py` for `runs/probe_after`.
