# Intention formation, generalization: predictions

Written and committed **before the held-out people were run through the frozen
rules**, together with the file that declares them. Kept as written.

## The two questions, kept apart

The brief is right that these can come apart, and the report keeps them apart:

| | Question |
|---|---|
| **Generalization** | Do the rules work on cases they were not authored against? |
| **Scoring validity** | Do they rank intentions for psychologically meaningful reasons? |

A mechanism can generalize perfectly and still score for a bad reason. H2 below
is about the second and is measured independently of the first.

## What is frozen

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| git blob | `41112b95d75d75786ad4df442e25330c74c5d6b3` |
| Bytes | 6,956 |
| Commits touching it | one, `8ede500`, before the fixture that reads it existed |

Ten candidate rules. Not one byte changes. No rule is added for a held-out
person, no weight is altered, no intention is renamed. The rule-count experiment
(H2) builds its extra rules **in memory at run time**, so the file on disk stays
identical and is hashed again at the end of the run to prove it.

## Holdout design

**Option A, the declared four.** Four people whose traits, values and beliefs are
placed by a stated principle in a region the shipped cast does not occupy. The
cast is nowhere below 0.50 on empathetic or honest, nowhere above 0.70 on
cautious, and never high on dominant and empathetic together; each held-out
person breaks at least one of those. Declared in
`Data/Experiments/held-out-people.json` and committed before running.

**Option A+, the sweep, which is the real evidence.** Every combination of the
seven shipped traits at three levels: **2,187 profiles**, enumerated
mechanically, with values and beliefs rotating by index. Nobody designed them, so
nothing in them can have been fitted to. If the mechanism is a table fitted to
four people, a uniform sample of trait space is where that shows.

No character-specific rule is written, and the rules cannot contain one: they are
hashed, and searched for character names, and the search result is reported.

## Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | The frozen rules give a held-out profile at least two reachable intentions for at least some wants | every want is single-valued for every held-out profile |
| P2 | At least one meaningful contextual perturbation changes the intention for held-out people | no context ever moves it |
| P3 | At least one meaningful belief, trait or value perturbation changes it | no state change ever moves it |
| P4 | An irrelevant perturbation never changes it | one does |
| P5 | Changing the want changes the reachable intention space | the reachable set is the same for every want |
| P6 | Held-out intentions arise from generic state, not character-specific rules | any rule names or is keyed on a character |
| P7 | Deterministic under replay | any replay differs |
| P8 | The `look_after -> protect` collapse either reproduces outside the cast or does not; report which | not measured |
| P9 | The redundant-rule test settles whether rule count biases the result | not measured |
| P10 | No character-specific production code or data is required | any is |

**Committed in advance, and riskier:**

- **P8, my expectation:** the collapse **will** reproduce across the sweep, and
  for nearly every profile. `protect` has two candidates to its rivals' one, so
  its total is the sum of two positive contributions where theirs is one. A
  person would have to be very low on empathy *and* closeness to escape it. If
  I am right, the failure is structural rather than a property of this cast.
- **P9, and this is a correction I expect to have to make.** My last report said
  "two rules beat one". That is loose. Contributions are **summed**, so what beats
  one rule is not the *count* but the *total weight*, and a second rule is simply
  a way of adding weight. The sharp test separates them:

  | Condition | Rules | Total weight for that intention | Expect |
  |---|---|---|---|
  | A | frozen | unchanged | baseline |
  | B | A + an exact clone of one rule under a new id | **doubled** | flips often |
  | C | A with one rule split into two halves | **unchanged** | flips **never** |

  If B flips and C does not, then rule count as such is *not* the bias; additive
  weight is, and writing another rule is indistinguishable from raising a number.
  That is a worse finding than the one I reported, not a better one, because it
  means the pathology cannot be avoided by counting rules more carefully.

- I expect the sweep to show the mechanism is **strongly sensitive to two or
  three traits and nearly blind to the rest**, because ten rules cannot read
  seven traits evenly. If so, "it generalizes" and "it uses the person" are both
  true and still thinner than they sound.
- I expect **`empathetic` to be the most load-bearing trait** and `impulsive` to
  be read by nothing at all — no candidate rule names it.

**What would count as failure:** the sweep producing one intention per want
regardless of the person (a table), or held-out people producing nothing at all
(rules too narrow to transfer).
