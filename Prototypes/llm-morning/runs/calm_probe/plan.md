# Calm probe: plan (frozen before any live call)

Mode: run. The question: do people tell Daniel about the visit when asked in a calm moment?

`reports/talk_probe.md` found that the tell was offered 21 times in scenes 1 and 3 and never taken. Every offer came
inside the door stretch or a grudge meeting. From 09:51 to 11:45 Daniel sat with the others, and nobody was asked at
all. The answer decides between two changes: a trigger for untold news (timing), or a change to how the option is
offered (choosing).

## Predictions (word for word, as given)

P1: a tell_*_visit option is chosen in at least 25% of the asks that offered one.

P2 (validity): no answer chooses an option that was not offered.

Decision rule: P1 at 25% or more points to a trigger for untold news; under 10% points to the offer itself; between, the reading decides.

## The probe (`runs/calm_probe/probe.py`)

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

## How P1 and P2 are counted

- **P1.** Denominator: the live asks whose offered options include an option `tell_<names>_visit`. Numerator: those
  whose answer's `option` is one of them. Share = numerator / denominator.
- **P2.** Every live ask's answer has an `option` that is in that ask's offered options. An answer that cannot be
  parsed counts as choosing nothing offered, and P2 fails.

## Order of work and limits

1. `probe.py --fake`: done before this plan was frozen (exit 0, 0 live asks in the replay, 18 fake calm asks).
2. Record this plan's sha256 and the probe's, the UTC time and HEAD (`runs/calm_probe/plan_frozen.txt`).
3. `probe.py --live`. Cap: 40 live asks. The key comes from `GEMINI_API_KEY` and is written to no file. No ask is run
   twice: each scene runs once (the ledger), and each prompt is asked once.
4. Read the records; then the end checks: the plan's hash, `git diff` empty, and a search for the key in every file.
