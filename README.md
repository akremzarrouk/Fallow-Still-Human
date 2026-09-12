# Fallow: Still Human

A human-life simulation under changing circumstances. The apocalypse is the
pressure placed on people; the game is the people.

This repository contains **slices S0 and S1**: the causal spine of the social
simulation, and a morning in a house where four people decide for themselves what
to do. No dialogue, no player, no 3D.

- `Docs/slices/S0/review.md` — one event, four people, four different experiences.
- `Docs/slices/S1/review.md` — what they do about it, and where that fails.

Where those two disagree with the code, the code is right and the reviews say when
they were written.

## What it does so far

```
world event -> access -> interpretation -> experience -> belief
                                        -> appraisal   -> emotion
                                                            |
   world consequence <- action <- deliberation <- motivation +
            |                                                 (values, traits,
            +------------------> back into the pipeline        beliefs, ledger,
                                                               hunger)
```

Four people who share every rule and differ only in their data spend a morning
visibly differently: one turns the house over looking for what went missing, one
holds the family together, one rations, one looks after whoever is nearest. None
of that is written down anywhere as a fact about them.

## Layout

    Assets/_Project/Scripts/Core    Fallow.Core - the simulation, no engine dependency
    Assets/_Project/Tests/EditMode  Tests, including the S0 and S1 experiments
    Assets/_Project/Data            Characters, event script, rules, the house
    Docs/slices/S0, S1              Reviews, generated traces, batch output

## Running the tests

    ./run-tests.sh

Runs the EditMode suite headlessly through the Unity CLI and prints a per-test
summary. Takes about two minutes, of which one is 200 simulated mornings.
Re-running it regenerates everything under `Docs/slices/*/traces` and
`Docs/slices/S1/batch`.

## The rules that keep it honest

**Nothing may name a member of the cast** — not a line of `Fallow.Core`, not a
rule in any data file. Characters differ only in their data.

**A rule condition may ask about circumstances only.** Anything about a person
enters as a weight, never as a threshold, so nobody has a number they flip at.

**Nothing reads world truth except the world.** Deciding is done from a Percept
containing only what that person can currently know, so a fact absent from it
cannot influence anything.

**Randomness settles ties and nothing else.** Where two options are closer than
the ambiguity band the seed decides and the trace says so. Everywhere else the
same person in the same state does the same thing.

**Every want has more than one way to be served.** A want with a single action is
that action under another name, and the validator rejects it.

All five are enforced by tests, not by discipline.

## Known defects

Recorded in `Docs/slices/S1/review.md` section 5, and pinned by characterisation
tests that say in their names that they should be turned round when fixed. The
largest: what happened in the night barely reaches what anybody does about it.
