# calm_probe: all documents

Merged by `merge-slice-docs.py` from the 2 Markdown files in `Prototypes/llm-morning/runs/calm_probe/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`plan.md`](#planmd)

---

## report.md

### The calm probe: do people tell Daniel about the visit when asked in a calm moment?

Mode: run. The plan is `reports/calm_probe_plan.md`. Its sha256 `5bfc64eb…a5b` was recorded at 2026-10-12T16:29:51Z,
HEAD `b62e954`, before any live call, and it was the same at the end. The live run went from 16:29:59 to 16:31:18
UTC: **18 live asks** (cap 40), exit 0, stderr empty. The replay made 0 live asks: 131 from cache in each scene. Paths
are from `Prototypes/llm-morning/`. Raw outputs are in `runs/calm_probe/`. No production file, test or prediction was
changed, and no ask was run twice.

#### Verdicts

| # | Prediction (word for word) | Result | Verdict |
|---|---|---|---|
| P1 | a tell_*_visit option is chosen in at least 25% of the asks that offered one. | **0 of 14 (0%)** | **fails** |
| P2 | (validity) no answer chooses an option that was not offered. | 18 of 18 answers chose an offered option | **holds** |

**Decision rule** (word for word): "P1 at 25% or more points to a trigger for untold news; under 10% points to the
offer itself; between, the reading decides." **At 0%, it points to the offer itself.** Asked in a calm minute,
with Daniel sitting in the kitchen, nobody told him in 14 chances. With the talk probe's 21, that makes 35 offers and
no tell in scenes 1 and 3.

#### Every ask

- **Where everyone was:** at each minute, Daniel and all three others were awake, sitting in the kitchen. Daniel held
  no belief.
- **Where the tell sat:** `tell_daniel_visit` was 18th or 19th of 27 or 28 options.
- **Where it was not offered:** Leo in scene 1 at 10:00 and 10:30, and Mara in scene 3 at 10:00 and 10:30. Each had
  talked about the visit at 09:45, and F2 holds it back for 60 minutes.
- **The full record:** every ask's prompt, offered options with labels, feeling and reason is in
  `runs/calm_probe/read_calm.stdout.txt` and `scene<k>.json`.

| Scene, seed | Minute | Who | Tell offered | Chose | Words | Feeling |
|---|---|---|---|---|---|---|
| 1, 201 | 10:00 | Elena | yes | reassure_all | "We have survived this long by staying together, and we will get through today if we do not turn on each other." | anxious |
| 1, 201 | 10:00 | Leo | no | silent | none | exhausted |
| 1, 201 | 10:00 | Mara | yes | accuse_daniel | "You went out there and came back with nothing, just like you always do when you mess everything up." | bitter hunger |
| 1, 201 | 10:30 | Elena | yes | reassure_all | "We have no food left and water is short, but we will not survive by turning on each other." | anxious |
| 1, 201 | 10:30 | Leo | no | silent | none | exhausted |
| 1, 201 | 10:30 | Mara | yes | accuse_daniel | "You went out and came back with nothing, and you still have the nerve to lecture me." | |
| 1, 201 | 11:00 | Elena | yes | reassure_all | "We are going to stay together and we will get through this day. Please, let's not fight." | |
| 1, 201 | 11:00 | Leo | yes | silent | none | |
| 1, 201 | 11:00 | Mara | yes | accuse_daniel | "You went out there and came back with nothing, just like you always do." | |
| 3, 202 | 10:00 | Elena | yes | reassure_all | "We are going to stay right here together and we will get through this day safely." | |
| 3, 202 | 10:00 | Leo | yes | accuse_daniel | "Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules." | |
| 3, 202 | 10:00 | Mara | no | accuse_daniel | "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." | |
| 3, 202 | 10:30 | Elena | yes | reassure_all | "We are going to stay right here and look after each other, everything will be all right." | |
| 3, 202 | 10:30 | Leo | yes | silent | none | |
| 3, 202 | 10:30 | Mara | no | accuse_daniel | "Daniel, you didn't help anyone last night, you just made things worse for all of us." | |
| 3, 202 | 11:00 | Elena | yes | reassure_all | "We are going to stay right here together and we will get through this. No one is going out." | |
| 3, 202 | 11:00 | Leo | yes | accuse_daniel | "Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice." | |
| 3, 202 | 11:00 | Mara | yes | accuse_daniel | "You went out behind our backs and still couldn't bring anything back for us, Daniel." | |

Reasons, examples (all are in `read_calm.stdout.txt`):
- Elena, scene 1, 10:00: "I need to calm the bickering before it tears our family apart completely."
- Leo, scene 1, 10:00: "There is nothing to say that hasn't already been said, so I will stay quiet and conserve my
  strength."
- Mara, scene 1, 10:00: "Daniel keeps pretending he is helping while he is the one who caused all of this."

**What the "calm" prompt holds** (`runs/calm_probe/prompt_diffs.stdout.txt`):
- **10:00 to 10:30:** each person's prompt differs only in its "Now" line.
- **10:30 to 11:00:** it also gains "You last spoke with X at 09:48", and one or two old lines are trimmed. For Leo in
  scene 1 and Mara in scene 3, it also gains the tell option.
- **The most recent lines in every prompt are the 09:48 quarrel** (Mara accusing Daniel, Daniel confronting her).
  Nothing in it says an hour has passed quietly. So a "calm minute" reaches the model as the quarrel's next turn.

#### Reading, per person

- **Elena.**
  - She was offered the tell 6 times and reassured everyone each time, almost in the same words.
  - A real mother in that kitchen might well not tell her eldest, at the first quiet moment, that she turned a woman
    away and her daughter defied her. Her answers are all about keeping the peace, which is her sheet ("Fears the
    household breaking").
  - But six times in a row, over an hour, with the same sentence, is the prompt not moving, not a choice.
- **Mara.**
  - Offered it 4 times (and asked twice without it), she accused Daniel each time, about his night out.
  - A real seventeen-year-old who defied her mother to give water away might well not volunteer it to the brother she
    is furious with, and might even keep it from him.
  - Her accusations are in character, but they repeat one grievance six times.
- **Leo.**
  - Offered it 4 times, he was silent twice and accused Daniel twice.
  - He is the one with no act of his own at the door to hide, and the likeliest real teller ("You missed it: Mara gave
    water away").
  - That he never does reads as the model following his "Against Daniel" grudge lines and the last lines of the
    prompt, not as Leo.

**Taken together.** In a real kitchen, an hour after a stranger came and water was given against the mother's word,
someone would tell the brother who missed it. Most likely Leo; perhaps Mara, defensively. In these prompts nothing
tells them the moment has changed, and the tell is one option among 28, below the quarrel options. On this
evidence, timing alone does not bring the news.

#### Commands and output

All from `Prototypes/llm-morning/`.

- **Fake run first.**
  `env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/calm_probe/probe.py --fake` exits 0 (`fake.stdout.txt`). The
  replay made 0 live asks; there were 18 fake calm asks.
  - In a first draft only 10:00 was reached: quiet time jumps between events (`Quiet.next_event`, `Quiet.advance`).
    The probe now splits a jump at 10:30 and 11:00 and ticks the needs there. No need crossed a line.
- **The freeze** (`plan_frozen.txt`): plan `5bfc64eb83fb62952a230a3eda3945fbe2e74450023679e3e94f0e47d8b76a5b`, probe
  `66240842de5436095bc7c0c49f4b62a6c9e1b2a466bf093d747d29112f91fcea`, 2026-10-12T16:29:51Z, HEAD `b62e954`, git diff 0
  lines, no cache or ledger before.
- **The live run.** `.venv/Scripts/python.exe runs/calm_probe/probe.py --live` exits 0 (`live.stdout.txt`):
  ```
  scene 1 (client seed 201): replay {'live': 0, 'from_cache': 131, 'api_requests': 0}; calm asks {'live': 9, ...}; stopped None
  scene 3 (client seed 202): replay {'live': 0, 'from_cache': 131, 'api_requests': 0}; calm asks {'live': 9, ...}; stopped None
  live asks in all: 18
  ```
- **Reading.** `.venv/Scripts/python.exe runs/calm_probe/read_calm.py` exits 0, 215 lines (`read_calm.stdout.txt`):
  ```
  P1: asks offering a tell_*_visit option: 14; choosing one: 0; share 0.0
  P2: answers choosing an option not offered: [] (of 18 asks)
  ```
  An inline diff of the prompts across the three minutes: `prompt_diffs.stdout.txt`.
- **End checks** (`end_checks.txt`): plan sha256 unchanged (`5bfc64eb…`); probe unchanged; git diff `[]`; key search
  0 files; ledger 18 live asks, no stop.

---

## plan.md

### Calm probe: plan (frozen before any live call)

Mode: run. The question: do people tell Daniel about the visit when asked in a calm moment?

`reports/talk_probe.md` found that the tell was offered 21 times in scenes 1 and 3 and never taken. Every offer came
inside the door stretch or a grudge meeting. From 09:51 to 11:45 Daniel sat with the others, and nobody was asked at
all. The answer decides between two changes: a trigger for untold news (timing), or a change to how the option is
offered (choosing).

#### Predictions (word for word, as given)

P1: a tell_*_visit option is chosen in at least 25% of the asks that offered one.

P2 (validity): no answer chooses an option that was not offered.

Decision rule: P1 at 25% or more points to a trigger for untold news; under 10% points to the offer itself; between, the reading decides.

#### The probe (`runs/calm_probe/probe.py`)

- **Replay.** Scenes 1 and 3 of the talk probe are each played again from a copy of `cache/talk_probe/scene<k>.json`:
  v16 seed 2 to day 3, the talk probe's visitor at 09:42, and everything after it as the talk probe played it. The
  replay's client refuses every ask, so any ask that misses the cache stops the scene. The replay makes 0 live asks.
- **The calm asks.** At 10:00, 10:30 and 11:00, each awake person in Daniel's room who knows the visit first-hand
  gets the prompt they would get if asked at that minute:
  - It is `World.prompt_for(p, t, World.options_for(p))`, with no trigger, lull or extra line. `World.ask_model`
    builds a prompt the same way.
  - The minute's state is the replay's. 10:00 falls on a quiet step, and the asks come after it. 10:30 and 11:00 fall
    inside a quiet jump (`Quiet.next_event`): the jump is split at the minute and the needs are ticked there (no need
    crosses a line between events; the probe records any that does).
  - Each prompt is asked live once, on an oracle of its own (`cache/calm_probe/scene<k>.json`). The client seed is
    **201 for scene 1 and 202 for scene 3**: "client seeds 201 and 202" is read as one seed per scene, as the talk
    probe's 101, 103 and 104 were. The options offered, the choice, words, feeling and reason are recorded.
  - The answer is never applied: the replayed day goes on from the cache, and the scene stops after 11:00's asks.
- **What the fake run shows** (`runs/calm_probe/fake.stdout.txt`). The prompts are the replay's, so the live run asks
  the same 18 prompts:
  - At each minute, Elena, Leo and Mara are awake in the kitchen with Daniel, and all three know the visit first-hand.
  - `tell_daniel_visit` is offered in **14** of the 18 prompts. It is held back in four:
    - Leo in scene 1, at 10:00 and 10:30: he talked about it at 09:45, and F2 holds it for 60 minutes;
    - Mara in scene 3, at 10:00 and 10:30: the same.

#### How P1 and P2 are counted

- **P1.** Denominator: the live asks whose offered options include an option `tell_<names>_visit`. Numerator: those
  whose answer's `option` is one of them. Share = numerator / denominator.
- **P2.** Every live ask's answer has an `option` that is in that ask's offered options. An answer that cannot be
  parsed counts as choosing nothing offered, and P2 fails.

#### Order of work and limits

1. `probe.py --fake`: done before this plan was frozen (exit 0, 0 live asks in the replay, 18 fake calm asks).
2. Record this plan's sha256 and the probe's, the UTC time and HEAD (`runs/calm_probe/plan_frozen.txt`).
3. `probe.py --live`. Cap: 40 live asks. The key comes from `GEMINI_API_KEY` and is written to no file. No ask is run
   twice: each scene runs once (the ledger), and each prompt is asked once.
4. Read the records; then the end checks: the plan's hash, `git diff` empty, and a search for the key in every file.

