# Fallow: Still Human

A human-life simulation under changing circumstances. The apocalypse is the
pressure placed on people; the game is the people.

This repository currently contains **slice S0** only: the causal spine of the
social simulation, with no decisions, no dialogue and no 3D. See
`Docs/slices/S0/review.md` for what it does and what it proved.

## Layout

    Assets/_Project/Scripts/Core   Fallow.Core - the simulation, no engine dependency
    Assets/_Project/Tests/EditMode Tests, including the slice S0 experiment
    Assets/_Project/Data           Characters, event script, rules, vocabulary
    Docs/slices/S0                 Review and generated traces

## Running the tests

    ./run-tests.sh

Runs the EditMode suite headlessly through the Unity CLI and prints a per-test
summary. Takes about two minutes. Re-running it also regenerates the reports
under `Docs/slices/S0/traces/`.

## The two rules that keep it honest

Nothing in `Fallow.Core` and nothing in `Data/Rules/rules.json` may name a
member of the cast. Characters differ only in their data. Rule conditions may
ask about circumstances only; anything about a person enters as a weight, never
as a threshold. Both are enforced by tests.
