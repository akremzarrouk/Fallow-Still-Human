# Plan: the door probe, second

Mode: run. Written, hashed and recorded before any live call (`runs/probe_door2/plan_frozen.txt`). Not changed after.
Paths are relative to `Prototypes/llm-morning/`.

## What it asks

What the real model does when a stranger at the door says what they need, and whether they have a child.
`reports/probe_door.md` could not test this: the visitor was silent until sent away. `reports/door_heard_impl.md`
changed that: the visitor speaks through the shut door in the minute of each knock (a child named with their age at
the first), and everyone who perceives the door is asked every turn of the visit, up to 18 door asks.

## How

`runs/probe_door2/probe.py --live` (code at HEAD; no production file is changed). It is `runs/probe_door/probe.py`
with these differences only:

- **The same 8 visitors and the same knock rule.** v16 seed 2, days 1 and 2, nights 1 and 2 and both night minds from
  the cache. Day 3 as the code is at HEAD. The street's own visits are taken away and its asks stopped; one probe visit
  is put at the front door, at the first minute from 07:30 at which someone awake is in the kitchen.
- **Phase 0** uses the run's seed (2) and reuses `cache/probe_door`'s phase-0 cache:
  `cache/probe_door2/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` starts as a copy of
  `cache/probe_door/gemini-3.5-flash-lite-daniel_ate_it-seed2.json`. The fake check found every ask of phase 0 in it
  (0 asked, 120 from the cache) and the knock at 09:42.
- **Scene k** uses client seed 100+k (101 to 108) and its own cache, `cache/probe_door2/scene<k>.json`, a copy of the
  phase-0 cache. The cache key keeps the run's seed (2), so the day to the knock is found there; every ask from the
  knock on is the scene's own and is sent with seed 100+k. (`reports/probe_door.md` §0: `gemini.py:101` sends the
  client's seed, so one seed made the knock's first turn one sample repeated.)
- **Validity check.** After scenes 1 and 2, if their answers at the knock minute are identical, the probe stops before
  scene 3 and the report says the seed is not reaching the model. The probe writes the comparison to the ledger.
- **Cap: 300 live asks** in all (phase 0 and the eight scenes). The probe stops cleanly there.
- **The end** of a scene: the visit ends (given, refused, or gone after 6 turns with nothing from the house).
- **The record** (`runs/probe_door2/scene<k>.json`): the visitor; every line said at the door and who heard it
  (`said`, `heard_said`, `by_knock`, `saw`); every decision from the knock (option, words, feeling, reason), each
  marked with whether its person perceived the door when asked (`at_door`); every prompt and answer from the knock on;
  the visit's door asks; the outcome. `runs/probe_door2/ledger.json` counts the live asks.
- No scene is run twice (a phase recorded in the ledger is skipped). The key is the process's `GEMINI_API_KEY` only,
  written to no file.

**The visitors** (as in `reports/probe_door_plan.md`):

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

**Checked with the fake model first** (`runs/probe_door2/fake.stdout.txt`, `probe.py --fake`, in a temp folder):
exit 0. Phase 0: 0 asked, 120 from the cache, the knock at 09:42. The 8 scenes each ended; 122 fake answers in all;
the validity check ran after scene 2 (prompts not identical, answers not identical) and let scene 3 go on.

## Predictions

Copied word for word from the brief:

  P1: at least 1 door_give in the 6 water scenes (1 to 6).
  P2: in at least 3 of the 8 scenes, someone at the door chooses an ordinary option (not door_* and not silent) while the visitor is there.
  P3: in at least 3 of the water scenes where Elena speaks to the visitor, her words say or imply the house has no water to spare.

**Counting rules** (fixed here, before the run):

| # | Counting rule |
|---|---|
| P1 | a scene counts if `door_give` is in its `scene.acts`, scenes 1 to 6 |
| P2 | a scene counts if it has a decision with `mode` "model", `at_door` true, and an option that does not begin with `door_` and is not `silent`, at a minute from the knock to the visit's end |
| P3 | the scenes counted are the water scenes (1 to 6) in which Elena chose `door_call` or `door_refuse` (her speech through or at the door). Each of her lines is quoted, and read: does it say or imply the house has no water to spare. The verdict holds if at least 3 such scenes have such a line. If she speaks to the visitor in fewer than 3 water scenes, P3 is NOT TESTED, with the count. |

Each gets a verdict: holds, fails, or NOT TESTED with the reason. If the cap or the validity check stops the run, the
scenes not run make a prediction NOT TESTED for what they would have added, and the verdicts are given on the scenes
run.

**The reading** (`CLAUDE.md:16-19`), not a number: every scene is read in full in `reports/probe_door2.md`. For each,
the report says whether a real family in that room, that hungry, would have done this, and why.

## Commands

From `Prototypes/llm-morning/`:
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/probe_door2/probe.py --fake        -> runs/probe_door2/fake.stdout.txt
$ sha256sum reports/probe_door2_plan.md runs/probe_door2/probe.py; date -u; git rev-parse HEAD   -> runs/probe_door2/plan_frozen.txt
$ .venv/Scripts/python.exe runs/probe_door2/probe.py --live        (GEMINI_API_KEY from the environment)
$ sha256sum reports/probe_door2_plan.md                                                  (must equal the frozen one)
```
