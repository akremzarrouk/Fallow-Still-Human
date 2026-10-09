# Plan: the door probe

Mode: run. Written, hashed and recorded before any live call (`runs/probe_door/plan_frozen.txt`). Not changed after.
Paths are relative to `Prototypes/llm-morning/`.

## What it asks

What the real model does with a stranger at the door, before anything is built on the door scene. The street sends
almost no knocks (`reports/w2a_fixes.md` §3), so the door machinery has never met the real model. Eight scenes, each a
different visitor, each played once.

## How

`runs/probe_door/probe.py --live` (code at HEAD; no production file is changed):

- **The day.** v16 seed 2, days 1 and 2, nights 1 and 2 and both night minds from the cache. Day 3 is played live, as
  the code is at HEAD. The street's own visits are taken away and its asks stopped; one probe visit is put at the
  front door.
- **When the knock comes.** At 07:30 if someone awake is in the kitchen then; otherwise at the first minute after 07:30
  at which someone awake is in the kitchen.
  - This is the user's choice (2026-10-09), made before any live call. The brief said 07:30, but in v22's day 3 the
    family rested from 07:21 to 09:45. A knock into a sleeping house either wakes nobody (the visit is deferred) or
    wakes someone in a bedroom, who has no door options there. Fix 3 then ends the Q7 stretch as soon as they leave
    that room, and they are never asked at the door. So 07:30 would test the schedule, not the model.
  - The minute is found once (phase 0) and is the same in all eight scenes.
- **Phase 0.** `cache/probe_door/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` starts as a copy of cache/v16's. Day 3
  is played with no visit until that minute, and stops before anything at it is asked. Everything before the knock is
  the same in all eight scenes, so it is asked live once.
- **Scene k.** `cache/probe_door/scene<k>.json` starts as a copy of the phase-0 cache. So the day to the knock comes
  from the cache, and every ask from the knock on is the scene's own.
  - The knock's first prompt is word for word the same in all eight scenes, since nothing of the visitor is perceived
    until they speak or are seen. With one shared cache, scenes 2 to 8 would replay scene 1's first answer; this way
    each scene samples the model afresh (temperature 1.0, `config.json`).
- **The end.** The scene stops when the visit ends: given, refused, or gone after 6 turns with nothing from the house.
- **The record.** Each scene's record (`runs/probe_door/scene<k>.json`) holds the visitor, every line said at the door,
  every decision from the knock (option, words, feeling, reason), every prompt and answer from the knock on, and the
  outcome. `runs/probe_door/ledger.json` counts the live asks.

**The visitors** (households of seed 2's street; the stores the probe gives them at the knock):

| Scene | Household | Asks for | Child | Disposition | Need |
|---|---|---|---|---|---|
| 1 | h13 (no. 13, 2 people) | water | no | helper | one day of drinking water: urgency 0.67 |
| 2 | h29 (no. 29, 2) | water | no | helper | none: urgency 1.0 |
| 3 | h16 (no. 16, 3; a boy of 6) | water | yes | helper | urgency 0.67 |
| 4 | h23 (no. 23, 4; a girl and a boy of 5) | water | yes | helper | urgency 1.0 |
| 5 | h5 (no. 5, 1) | water | no | guarded | urgency 1.0 |
| 6 | h15 (no. 15, 2; a girl of 6) | water | yes | guarded | urgency 0.67 |
| 7 | h6 (no. 6, 2) | food | no | helper | water for 6 days; no food for 4 (thin): urgency 0.6 |
| 8 | h18 (no. 18, 3; a girl of 12) | food | yes | guarded | the same: urgency 0.6 |

Food urgency cannot reach 0.8 (food weighs 0.6, `w2_design.md` §2.1), so a food visitor never says an `insist` line.
What the visitor varies reaches the family only through what they perceive: the voice and words once the stranger
speaks (after a `door_call`), and who stands on the step once the door is open. What W2a lets the family do for a food
visitor is call, open and send away; `door_give` is for water only (`reports/w2a_impl.md` §0.1, 1).

**Limits:** at most 150 live asks in all (the probe stops cleanly there); no scene is run twice (a phase recorded in
the ledger is skipped); no production code, test or this plan changes after the hash. The key is the process's
`GEMINI_API_KEY` only, written to no file.

**Checked with the fake model first** (`runs/probe_door/fake.stdout.txt`, `probe.py --fake`, in a temp folder): exit 0.
The knock came at 09:42 after 21 asks; 8 scenes each ended, each with 6 Q7 asks; 69 asks in all.

## Predictions

| # | Prediction | Counting rule |
|---|---|---|
| **P1** | The door is answered in at least 5 of the 8 scenes. | a scene is answered if at least one `door_call` or `door_open` by a family member is in its scene record (`scene.acts`) |
| **P2** | At least 1 `door_give` in the 6 water scenes. | `door_give` in `scene.acts` of scenes 1 to 6 |
| **P3** | Live asks at most 120 in total. | `runs/probe_door/ledger.json` `live`: phase 0 and the eight scenes |

Each gets a verdict: holds or fails. If the cap stops the run, the scenes not run make P1 and P2 NOT TESTED for what
they would have added, and the verdicts are given on the scenes run.

**The reading** (`CLAUDE.md:16-19`), not a number: every scene is read in full in `reports/probe_door.md`. For each,
the report says whether a real family in that room, that hungry, would have done this, and why.

## Commands

From `Prototypes/llm-morning/`:
```
$ sha256sum reports/probe_door_plan.md; date -u; git rev-parse HEAD        -> runs/probe_door/plan_frozen.txt
$ GEMINI_API_KEY=<the user's key, for this process only> .venv/Scripts/python.exe runs/probe_door/probe.py --live
$ sha256sum reports/probe_door_plan.md                                    (must equal the frozen one)
```
