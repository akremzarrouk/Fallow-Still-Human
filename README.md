# Fallow: Still Human

A human-life simulation under changing circumstances. The apocalypse is the
pressure placed on people; the game is the people.

This repository contains **slices S0, S1, S1.1, S1.2, S1.3, S1.4 and S1.5**: the causal
spine of the social simulation, a morning in a house where four people decide for
themselves what to do, a counterfactual experiment on whether something that happens to a
person changes what that person wants and does, a pass on the deliberation layer that
stands between the two, two tests of what acting on a want does to it (one for a need, one
for a social want), and a diagnostic experiment on whether traits and values should be
wants at all. No dialogue, no player, no 3D.

- `Docs/slices/S0/review.md` — one event, four people, four different experiences.
- `Docs/slices/S1/review.md` — what they do about it, and where that fails.
- `Docs/slices/S1.1/report.md` — whether a night can change the same person, measured
  against a control that differs only in that night.
- `Docs/slices/S1.2/report.md` — whether a changed want now reaches the choice, and what
  still stands in the way.
- `Docs/slices/S1.3/report.md` — what eating does to wanting food, why nobody in the house
  eats, and what failing to eat leaves behind.
- `Docs/slices/S1.4/report.md` — what sitting with somebody does to wanting to look after
  them, and what the house looks like once that want can be answered.
- `Docs/slices/S1.5/report.md` — traits and values as always-on wants against traits and
  values as dispositions that shape a response, and what each hides.

Where those documents disagree with the code, the code is right and the reviews say when
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
summary. Takes about forty minutes, most of it counterfactual pairs of mornings and the
S1.5 comparisons, which run the house three ways.
Two tests fail since S1.4, the pacing gate and one check in the emergent-moment test.
Both are regressions that slice caused, explained in its report section 9 and left
failing rather than loosened.
Re-running it regenerates everything under `Docs/slices/*/traces` and
`Docs/slices/S1/batch`.

    python merge-slice-docs.py S1.5

Merges every Markdown file of a slice into `Docs/slices/<slice>/<slice>-all.md`, report
first. The separate files stay the sources; run it again after they change.

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

Recorded in `Docs/slices/S1/review.md` section 5, `Docs/slices/S1.1/report.md` section G,
`Docs/slices/S1.2/report.md` section 6, `Docs/slices/S1.3/report.md` section 9,
`Docs/slices/S1.4/report.md` section 9 and `Docs/slices/S1.5/report.md` section 5, and
pinned by characterisation tests that say in their names that they should be turned round
when fixed. The largest now: traits and values raise wants at every moment with nothing
calling for them (53 % of all urgency, S1.5). That is the wrong model, and it is still
shipped because the alternative S1.5 tested exposes what it was hiding. With traits and
values only shaping responses, people walk back and forth between ends they have already
found not worth pursuing: nothing registers that a walk's end was declined on arrival, and
the memory of the opening count never fades. And for two of the four, no amount of hunger
can ever outweigh what taking food costs them.

`Comfort` still softens another person's feelings directly, as technical debt, and is
not evidence that the social pipeline works. S1.4 found that people come right about as
often without it, from their own reading of being sat with, but did not isolate that further.
