# intention-formation: all documents

Merged by `merge-slice-docs.py` from the 4 Markdown files in `Docs/experiments/intention-formation/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)

---

## report.md

### Intention formation

*Can Fallow generate a plausible intention from an existing motivation and the
character's context, without a universal hardcoded Want -> Intention table?*

#### 1. Hypothesis

**H1.** A want should **constrain** the space of intentions a person might form,
and should not **determine** which one they form. Which intention they settle on
should depend on who they are — their traits, values, beliefs, memories and
current feelings — and on the circumstances they are standing in.

Three things are kept apart throughout, and the experiment fails if any two
collapse:

| | | Example |
|---|---|---|
| **Motivation** | what the person is driven toward | `restore_standing` |
| **Intention** | what they take themselves to be accomplishing | `assert_authority` |
| **Physical action** | what they do | `check_pantry` |

The previous experiment proved the third is independent of the second. This one
asks whether the second is independent of the first.

#### 2. What was implemented, and what was not

**No production change.** Not one file under `Assets/_Project/Scripts/Core` was
touched, and no shipped data file was edited. `IntentOfAct` remains what it was:
a hook, null by default.

**Everything hand-authored is one file**,
`Assets/_Project/Data/Experiments/intentions.json`, which nothing in
`Fallow.Core` loads. It contains **ten candidate rules**. That is the entire
authored surface of the experiment and it is listed in full in `measurements.md`.

**The selector is about thirty lines** in the test fixture, over shipped
machinery. It has no randomness of any kind.

#### 3. The candidate mechanism

A candidate rule says an intention is *available* to a set of wants, in given
circumstances, weighing an amount that depends on the person:

```json
{ "id": "...", "motives": ["restore_standing", "find_out"],
  "intent": "assert_authority",
  "when": { "others_present_min": 1 },
  "base": 0.10,
  "scaled_by": [ { "kind": "trait", "name": "dominant", "factor": 0.45 }, ... ] }
```

Selection: gather the candidates in scope for the want; drop those whose
circumstance does not hold; weigh each by `base + Σ scaler terms`; sum the
weights of rules speaking for the same intention, exactly as interpretation rules
speaking for the same reading are summed; take the heaviest, breaking ties
ordinally. If nothing matches, form no intention.

Three properties are **structural rather than promised**:

1. **A circumstance can gate a candidate but can never be the reason one wins.**
   `when` is the shipped `SituationCondition`, which has six fields — alone, in
   my own room, in somebody else's, the room holds food, I have searched here,
   how many others are present — and no field for a trait, a value, a feeling or
   a need. That is the type, not a convention I am following.
2. **Everything about the person is a scaler**, evaluated by the shipped
   `ScalerEval`: the same code that weighs an interpretation rule and prices an
   action. So an intention's weight decomposes into the same named terms as every
   other weight in the system, and appears in the trace the same way.
3. **No randomness.** Any variation observed is therefore attributable to the
   context or to the person, and to nothing else.

#### 4. Was a lookup table used? Yes, partly — and here is exactly where

The `motives` list on each rule is hand-authored. It is a table of **which
intentions a want may express**. Pretending otherwise would be the easiest way to
make this experiment look better than it is, so: it is there, it is ten lines
long, and it is printed in full in the measurements.

The claim under test is that it is a **constraint** and not a **mapping**, and
that claim is falsifiable two ways, both measured:

| Test | Result |
|---|---|
| Does any want have only one *reachable* intention? | **No.** Every want reaches 2 or 3 |
| Does any want produce only one intention *in practice*? | **Yes, one: `look_after`.** See section 8 |

Nothing else is tabulated. There is no table keyed on (want, act), none keyed on
(want, person), and none keyed on the want alone that returns an intention.

#### 5. How authoring was kept honest

The rules were written **blind**: from the shipped character sheets, the shipped
rule files and the shipped vocabulary, before a single case had been run. They
were committed in the same commit as `predictions.md`, and were not edited
afterwards. So every case in the experiment — all 3,826 live decisions and every
probe — is held out from authoring.

This is checkable rather than asserted: `git log -p` on the rule file shows one
commit, dated before the fixture that reads it existed.

There was **one authoring pass and no tuning pass.** No weight was adjusted after
seeing a result. The two things the measurements show to be wrong (section 8) are
still wrong in the file.

#### 6. Design and controls

| | |
|---|---|
| Controlled probes | 4 people x 7 wants x 4 contexts, on real profiles with their real seeded beliefs, in the real house |
| Context varied by | `Percept.Imagine`, the shipped counterfactual-percept method |
| Live mornings | 5 conditions x 10 seeds = 50; the selector installed on `IntentOfAct`, forming the intention from the circumstances at the moment the person **decided**, not the moment the act finished |
| Decisions | 3,826 |

| | Control | Result |
|---|---|---|
| C1 | Selector off reproduces the shipped baseline | **50 of 50** |
| C2 | Selector installed but returning null | **50 of 50** |
| C3 | Same state and seed replayed | 140 of 140 identical, plus a whole morning twice |
| C4 | Perturbing a circumstance no rule reads | **0 of 28** |
| C5 | Character substitution | all four, N3 |
| C6 | Held out from authoring | all of it |

#### 7. Results

##### The core contrast, and it is one trace

Two men, the same minute, the same room, the same company, the same want, and the
same physical act:

```
m1  daniel in kitchen with elena, leo, mara     m1  leo in kitchen with daniel, elena, mara
  want       find_out 0.808                       want       find_out 0.437
  act        check_pantry                         act        check_pantry
  candidates assert_authority   1.200             candidates take_responsibility 0.910
             take_responsibility 0.575                       share_information   0.665
             share_information   0.320                       assert_authority    0.333
    dominant 0.850 x 0.450 = 0.383                  honest 0.800 x 0.300 = 0.240
    control  1.000 x 0.350 = 0.350                  family_safety 1.000 x 0.350 = 0.350
    role_claim(daniel,leads_family) 0.800 x 0.300   cautious 0.700 x 0.200 = 0.140
    proud    0.850 x 0.150 = 0.128
  INTENTION  assert_authority                     INTENTION  take_responsibility
```

Same want, same act, same room, same moment. Daniel is checking the pantry to
establish that checking it is his to do. Leo is checking it because somebody has
to. Nothing in the selector knows either of those sentences; the difference is
`dominant` 0.85 against 0.35 and a `role_claim` one of them holds.

##### The prediction table

All ten predictions passed. Detail in `results.md`; the load-bearing numbers:

| | |
|---|---|
| (person, want) pairs whose intention changed on the audience alone | **12 of 28** |
| Wants on which the four characters disagreed in identical circumstances | **5 of 7** |
| Wants many-valued across 3,826 held-out decisions | **6 of 7** |
| Intentions reachable from more than one want | **6 of 6** |
| Distinct intentions carried by `check_pantry` | **4**, from 4 wants, over 257 uses |
| Distinct intentions carried by `wait` | **6**, over 1,706 uses |
| Replays identical | **140 of 140** |
| Cells moved by a circumstance the rules read | 12 of 28 |
| Cells moved by a circumstance no rule reads | **0 of 28** |
| Formations contested by a runner-up | 90.6 % |
| ...decided by less than 0.10 | 3.9 % |

That last pair is the shape the brief asked for: a winner that is almost always
contested but almost never a coin-flip. **Predictable character logic,
unpredictable circumstances** — not a table, and not noise.

##### Is the belief doing the work, or the rule?

`took_what_was_not_mine` is the one intention whose heaviest scaler is a belief —
that I am answerable for the missing can. If the belief carries it, only people
who hold it should form it.

| | |
|---|---|
| Times formed | 157 |
| By somebody who believes they are answerable | **152** |
| By somebody holding no such belief at all | **5** |
| Decisions in reach of it taken by an answerable person | 152 — **all of which formed it** |

So the belief is doing the work, 97 % of the time, and the five exceptions are a
real defect rather than noise (section 8).

#### 8. Failures

**`look_after` produced `protect` in 851 of 851 decisions.** For that one want the
mechanism *is* a lookup table, which is precisely the failure mode the brief
names. The cause is legible in the file and is not a tuning accident: `protect`
has two candidate rules and one of them needs no circumstance at all, while its
two competitors have one rule each. Two rules beat one.

> **Refined by a later measurement, not retracted.** The generalization experiment
> separated the two things this sentence runs together. Cloning a rule (more rules,
> double the weight) changed 2,898 outcomes; splitting a rule in half (more rules,
> the same weight) changed **0**. So what beats one rule is the total weight, and a
> second rule is only one way of adding it. The description of this case stands; the
> mechanism it names does not. See `Docs/experiments/intention-generalization/`.

This is the same pathology the previous experiment found one layer down, where an
intention's effect size tracked how many appraisal rules happened to name it.
**It followed me from the reader layer into the selector layer**, which is worth
more than the local failure: any mechanism that sums rules per label inherits it.

**Five innocent people read their own act as a theft.** Where nothing else in
scope matched, `what_you_did_in_the_night` could win on its honesty and fairness
terms alone, without the belief that gives it its meaning. It is left in the file
as written.

**`protect` dominates** — 1,599 of 3,826 formations, from four wants. Three of
the four characters are highly empathetic and the morning keeps everybody
anxious, so a scaler meant to separate people ended up agreeing about most of
them. The variation is real but it is not evenly distributed.

#### 9. Limitations and overfitting risks

**Overfitting risks, stated against myself:**

- Ten rules is a small mechanism, and I chose every scaler and every base weight
  in them. Blind authoring and held-out evaluation limit the damage; they do not
  eliminate it.
- The `motives` scoping is a hand-authored constraint, however it is described.
- I authored rules knowing this cast well from five previous experiments. That
  knowledge is a form of fitting that no procedure here controls for.
- What it would take to rule this out: a cast and a scenario I have not seen.
  Neither exists.

**Limitations:**

- **Six intentions.** The brief's own examples for `restore_standing` — assert
  authority, demonstrate competence, avoid appearing weak, quietly prove
  themselves right, seek recognition — are five distinctions and the vocabulary
  can make one of them. The experiment is bounded by the word list, exactly as
  predicted in advance.
- **Six circumstances.** `SituationCondition` can ask about company, rooms and
  whether I have searched here. It cannot ask whether anybody is looking at me,
  whether this has just happened before, or how long I have been at it.
- **Three readers.** Only three of the six intentions are read by anything
  downstream, so the fact that formed intentions changed behaviour in 50 of 50
  mornings travels through a very narrow door.
- **One house, one cast, one morning shape.** Generalisation beyond that is
  untested.
- **Nothing in production forms an intention.** The selector lives in a test.

#### 10. Classification

| | |
|---|---|
| **PROVEN** | A want does not determine an intention: 6 of 7 wants many-valued over 3,826 held-out decisions. Context changes it (12 of 28 pairs on the audience alone). The person changes it (5 of 7 wants, four characters, identical circumstances). It is exactly reproducible (140 of 140). It is counterfactually specific (0 of 28 on an unread circumstance). The mapping is many-to-many both ways (all 6 intentions from 2+ wants). The act stays independent (`check_pantry`: 4 intentions; `wait`: 6). The controls are exact (C1, C2 both 50 of 50). **And none of it required a universal Want -> Intention table, new engine code, a new action, a new want, a new trait, a new emotion, a planner or an LLM.** |
| **PLAUSIBLE** | That the variation is of the *right kind* and not merely of the right shape. The traces read as defensible — Daniel pulls rank where Leo gets on with it — but "defensible" is a judgement, and the brief is right that it is not evidence |
| **UNPROVEN** | Generalisation beyond this cast, this house and this morning. That the approach survives a vocabulary larger than six. That ten rules scale. That the intentions formed are the *correct* ones rather than merely consistent ones |
| **FAILED** | `look_after` -> `protect`, 851 of 851: for that want the mechanism is a lookup table. And an intention about the past was formed five times by somebody with no belief they did anything |
| **UNKNOWN** | Whether an observer could infer any of this — the previous experiment showed the witness is given nothing to infer from, and nothing here changes that. Whether intentions formed this way would remain stable across a day rather than a morning |

#### 11. Verdict

### KEEP

Kept: **the hypothesis and the approach.** A want constraining a space of
intentions, resolved by the person's own traits, values, beliefs, memories and
feelings through the machinery the simulation already has, with circumstances
gating candidates and never deciding between them. It produced the right kind of
variation for the right reasons on cases it had never seen, and it did so with
ten rules and no engine.

Not kept, and not proposed: anything in production. No intention system is being
built, no rule is being promoted out of the experiment folder, and the two
defects in section 8 are left in the file exactly as authored.

The two things that would have to be settled before any of this could be more
than an experiment are both already named: the **vocabulary**, which can make six
distinctions where the hypothesis needs more, and the **reader set**, which reads
three of those six. Neither is addressed here.

#### 12. The question the brief asks to answer explicitly

> Can Fallow currently derive a context-sensitive intention from an existing
> motivation without relying on a universal hardcoded Want -> Intention mapping?

**Yes.**

**What was demonstrated.** Ten authored candidates, no universal mapping, no
engine change, and on 3,826 decisions it had never seen: six of seven wants
produced more than one intention; four characters in identical circumstances
formed different intentions on five of seven wants; the same want flipped on the
presence of other people in twelve of twenty-eight probes; every one of the six
intentions was reached from at least two different wants; one physical act
carried four intentions and another carried all six; the result is exactly
reproducible and provably insensitive to circumstances the rules do not read; and
removing the mechanism restores the shipped baseline in fifty mornings out of
fifty.

**What remains unproven.** That the intentions are *right* rather than merely
varied — the experiment measures causal dependence, not psychological truth.
That it generalises past one cast and one house. That it survives a vocabulary
big enough for the hypothesis, since six words cannot make the distinctions the
brief's own example asks for.

**The bottleneck, named and not solved.** It is not the mechanism and it is not
the action layer. It is that **there are six intentions and three of them are
read by nothing.** `look_after` collapsed to one intention not because the
mechanism cannot vary but because `protect` had two rules and its rivals had one
— the same rule-counting pathology the previous experiment found downstream. A
system that decides what a reason means by counting the rules that mention it
will keep producing this, at every layer it is applied to.

That is left exactly where it is, for review.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter IntentionFormationExperimentTests`. It
takes about a minute. Suite: PENDING.

---

## measurements.md

### Intention formation: measurements

Generated by `IntentionFormationExperimentTests` on the primary baseline. The candidate rules in `Assets/_Project/Data/Experiments/intentions.json` were authored blind and committed before any case here was run, so every case is held out from authoring. The selector has no randomness.

#### N1. The whole of the hand-authored surface

Counted from the file, not asserted. Every rule is listed; there is nothing else.

| Rule | Intention | Wants it is available to | Circumstance it needs | Base | Weighed by |
|---|---|---|---|---|---|
| `pulling_rank_needs_an_audience` | `assert_authority` | `restore_standing`, `find_out`, `guard_supplies` | at least 1 present | 0.100 | trait dominant x 0.450; value control x 0.350; belief role_claim($self,leads_family) x 0.300; trait proud x 0.150 |
| `being_the_one_who_decides_it` | `assert_authority` | `restore_standing`, `guard_supplies` | any | 0.050 | value control x 0.250; belief role_claim($self,leads_family) x 0.250; feeling anger toward anyone x 0.300 |
| `somebody_has_to_do_it` | `take_responsibility` | `restore_standing`, `find_out`, `guard_supplies`, `get_food` | any | 0.180 | trait honest x 0.300; value family_safety x 0.350; trait cautious x 0.200 |
| `doing_it_where_nobody_is_watching` | `take_responsibility` | `restore_standing`, `find_out` | alone | 0.220 | trait proud x 0.250; value respect x 0.200 |
| `so_that_they_know_too` | `share_information` | `find_out`, `look_after`, `keep_peace` | at least 1 present | 0.120 | trait honest x 0.400; value closeness x 0.300; value fairness x 0.200 |
| `standing_between_them_and_it` | `protect` | `look_after`, `keep_peace`, `avoid_exposure` | at least 1 present | 0.150 | trait empathetic x 0.400; value family_safety x 0.350; feeling anxiety toward anyone x 0.300 |
| `keeping_it_off_them` | `protect` | `look_after`, `guard_supplies` | any | 0.100 | trait empathetic x 0.300; value closeness x 0.250 |
| `not_making_a_scene_of_it` | `prevent_argument` | `keep_peace`, `avoid_exposure`, `look_after` | at least 1 present | 0.150 | trait cautious x 0.350; value closeness x 0.300; trait dominant x -0.250 |
| `letting_it_go_for_now` | `prevent_argument` | `keep_peace`, `restore_standing` | alone | 0.080 | trait cautious x 0.250; trait anxious x 0.200 |
| `what_you_did_in_the_night` | `took_what_was_not_mine` | `get_food`, `avoid_exposure` | any | 0.050 | belief answerable_for($self,missing_can) x 0.600; trait honest x 0.300; value fairness x 0.250; feeling shame toward anyone x 0.300 |

**10 rules, 6 intentions, 7 wants.**

The test that separates a constraint from a mapping: how many intentions each want can reach at all.

| Want | Intentions reachable | Which |
|---|---|---|
| `avoid_exposure` | 3 | `prevent_argument`, `protect`, `took_what_was_not_mine` |
| `find_out` | 3 | `assert_authority`, `share_information`, `take_responsibility` |
| `get_food` | 2 | `take_responsibility`, `took_what_was_not_mine` |
| `guard_supplies` | 3 | `assert_authority`, `protect`, `take_responsibility` |
| `keep_peace` | 3 | `prevent_argument`, `protect`, `share_information` |
| `look_after` | 3 | `prevent_argument`, `protect`, `share_information` |
| `restore_standing` | 3 | `assert_authority`, `prevent_argument`, `take_responsibility` |

**Wants with only one reachable intention (which would be a lookup table): 0.**

And the other direction, which is what P5 asks about:

| Intention | Wants that can express it |
|---|---|
| `assert_authority` | `find_out`, `guard_supplies`, `restore_standing` |
| `prevent_argument` | `avoid_exposure`, `keep_peace`, `look_after`, `restore_standing` |
| `protect` | `avoid_exposure`, `guard_supplies`, `keep_peace`, `look_after` |
| `share_information` | `find_out`, `keep_peace`, `look_after` |
| `take_responsibility` | `find_out`, `get_food`, `guard_supplies`, `restore_standing` |
| `took_what_was_not_mine` | `avoid_exposure`, `get_food` |

A circumstance can gate a candidate but can never be the reason one beats another: `SituationCondition` has six fields and none of them is a trait, a value, a feeling or a need. That is the type, not a convention. Everything about the person is in the scalers, which the shipped `ScalerEval` evaluates.

#### N2. The same want, in company and alone

One person, one want, one room, one moment. The only difference is whether anybody else is standing there. Nothing about the person changes between the two columns.

##### daniel

| Want | With the others in the room | Alone | Changed |
|---|---|---|---|
| `avoid_exposure` | protect 0.525 over took_what_was_not_mine 0.200 | took_what_was_not_mine 0.200 | **yes** |
| `find_out` | assert_authority 1.200 over take_responsibility 0.575 | take_responsibility 1.158 | **yes** |
| `get_food` | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.575 over took_what_was_not_mine 0.200 | no |
| `guard_supplies` | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 0.575 over assert_authority 0.500 | **yes** |
| `keep_peace` | protect 0.525 over share_information 0.320 | prevent_argument 0.298 | **yes** |
| `look_after` | protect 0.775 over share_information 0.320 | protect 0.250 | no |
| `restore_standing` | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 1.158 over assert_authority 0.500 | **yes** |

##### elena

| Want | With the others in the room | Alone | Changed |
|---|---|---|---|
| `avoid_exposure` | protect 0.860 over prevent_argument 0.495 | took_what_was_not_mine 0.385 | **yes** |
| `find_out` | take_responsibility 0.880 over share_information 0.725 | take_responsibility 1.188 | no |
| `get_food` | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.880 over took_what_was_not_mine 0.385 | no |
| `guard_supplies` | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 0.880 over protect 0.558 | no |
| `keep_peace` | protect 0.860 over share_information 0.725 | prevent_argument 0.405 | **yes** |
| `look_after` | protect 1.418 over share_information 0.725 | protect 0.558 | no |
| `restore_standing` | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 1.188 over prevent_argument 0.405 | no |

##### leo

| Want | With the others in the room | Alone | Changed |
|---|---|---|---|
| `avoid_exposure` | protect 0.780 over took_what_was_not_mine 0.478 | took_what_was_not_mine 0.478 | **yes** |
| `find_out` | take_responsibility 0.910 over share_information 0.665 | take_responsibility 1.255 | no |
| `get_food` | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.910 over took_what_was_not_mine 0.478 | no |
| `guard_supplies` | take_responsibility 0.910 over assert_authority 0.383 | take_responsibility 0.910 over protect 0.373 | no |
| `keep_peace` | protect 0.780 over share_information 0.665 | prevent_argument 0.305 | **yes** |
| `look_after` | protect 1.153 over share_information 0.665 | protect 0.373 | no |
| `restore_standing` | take_responsibility 0.910 over assert_authority 0.383 | take_responsibility 1.255 over prevent_argument 0.305 | no |

##### mara

| Want | With the others in the room | Alone | Changed |
|---|---|---|---|
| `avoid_exposure` | prevent_argument 0.563 over protect 0.450 | took_what_was_not_mine 0.340 | **yes** |
| `find_out` | share_information 0.740 over take_responsibility 0.445 | take_responsibility 0.803 | **yes** |
| `get_food` | take_responsibility 0.445 over took_what_was_not_mine 0.340 | take_responsibility 0.445 over took_what_was_not_mine 0.340 | no |
| `guard_supplies` | protect 0.575 over take_responsibility 0.445 | protect 0.575 over take_responsibility 0.445 | no |
| `keep_peace` | share_information 0.740 over prevent_argument 0.563 | prevent_argument 0.365 | **yes** |
| `look_after` | protect 1.025 over share_information 0.740 | protect 0.575 | no |
| `restore_standing` | take_responsibility 0.445 over assert_authority 0.345 | take_responsibility 0.803 over prevent_argument 0.365 | no |

**12 of 28 (person, want) pairs formed a different intention with an audience than without one.**

The want is identical in both columns, and so is everything about the person. Where the intention moved, the only thing that moved it was who else was in the room.

#### N3. The same want, the same room, four different people

Everything circumstantial is held identical: the same room, the same company, the same minute, the same urgency. Only the person differs, and they differ only by what the shipped character sheets say they are.

| Want | daniel | elena | leo | mara | Distinct |
|---|---|---|---|---|---|
| `avoid_exposure` | protect 0.525 over took_what_was_not_mine 0.200 | protect 0.860 over prevent_argument 0.495 | protect 0.780 over took_what_was_not_mine 0.478 | prevent_argument 0.563 over protect 0.450 | 2 |
| `find_out` | assert_authority 1.200 over take_responsibility 0.575 | take_responsibility 0.880 over share_information 0.725 | take_responsibility 0.910 over share_information 0.665 | share_information 0.740 over take_responsibility 0.445 | 3 |
| `get_food` | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.445 over took_what_was_not_mine 0.340 | 1 |
| `guard_supplies` | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 0.910 over assert_authority 0.383 | protect 0.575 over take_responsibility 0.445 | 3 |
| `keep_peace` | protect 0.525 over share_information 0.320 | protect 0.860 over share_information 0.725 | protect 0.780 over share_information 0.665 | share_information 0.740 over prevent_argument 0.563 | 2 |
| `look_after` | protect 0.775 over share_information 0.320 | protect 1.418 over share_information 0.725 | protect 1.153 over share_information 0.665 | protect 1.025 over share_information 0.740 | 1 |
| `restore_standing` | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 0.910 over assert_authority 0.383 | take_responsibility 0.445 over assert_authority 0.345 | 2 |

**Wants on which the four disagreed: 5 of 7.**

##### Why they disagree, taken apart

`restore_standing` in company, every candidate and every term:

**daniel** -> `assert_authority`

- `assert_authority` 1.700 from pulling_rank_needs_an_audience 1.200, being_the_one_who_decides_it 0.500
  - trait dominant 0.850 x 0.450 = 0.383
  - value control 1.000 x 0.350 = 0.350
  - belief role_claim(daniel,leads_family) 0.800 x 0.300 = 0.240
  - trait proud 0.850 x 0.150 = 0.128
  - value control 1.000 x 0.250 = 0.250
  - belief role_claim(daniel,leads_family) 0.800 x 0.250 = 0.200
- `take_responsibility` 0.575 from somebody_has_to_do_it 0.575
  - trait honest 0.500 x 0.300 = 0.150
  - value family_safety 0.500 x 0.350 = 0.175
  - trait cautious 0.350 x 0.200 = 0.070

**elena** -> `take_responsibility`

- `take_responsibility` 0.880 from somebody_has_to_do_it 0.880
  - trait honest 0.700 x 0.300 = 0.210
  - value family_safety 1.000 x 0.350 = 0.350
  - trait cautious 0.700 x 0.200 = 0.140
- `assert_authority` 0.758 from pulling_rank_needs_an_audience 0.558, being_the_one_who_decides_it 0.200
  - trait dominant 0.500 x 0.450 = 0.225
  - belief role_claim(elena,leads_family) 0.600 x 0.300 = 0.180
  - trait proud 0.350 x 0.150 = 0.053
  - belief role_claim(elena,leads_family) 0.600 x 0.250 = 0.150

**leo** -> `take_responsibility`

- `take_responsibility` 0.910 from somebody_has_to_do_it 0.910
  - trait honest 0.800 x 0.300 = 0.240
  - value family_safety 1.000 x 0.350 = 0.350
  - trait cautious 0.700 x 0.200 = 0.140
- `assert_authority` 0.383 from pulling_rank_needs_an_audience 0.333, being_the_one_who_decides_it 0.050
  - trait dominant 0.350 x 0.450 = 0.158
  - trait proud 0.500 x 0.150 = 0.075

**mara** -> `take_responsibility`

- `take_responsibility` 0.445 from somebody_has_to_do_it 0.445
  - trait honest 0.550 x 0.300 = 0.165
  - trait cautious 0.500 x 0.200 = 0.100
- `assert_authority` 0.345 from pulling_rank_needs_an_audience 0.295, being_the_one_who_decides_it 0.050
  - trait dominant 0.250 x 0.450 = 0.113
  - trait proud 0.550 x 0.150 = 0.083


#### N4. What moves it and what does not

Three perturbations against the same baseline moment. Two of them change something a rule reads; one changes something no rule in the file reads at all.

| Person | Want | Baseline (alone, kitchen) | +company (read) | in her own room (read by no rule here) | hungry (read by no rule here) |
|---|---|---|---|---|---|
| daniel | `avoid_exposure` | took_what_was_not_mine 0.200 | protect 0.525 over took_what_was_not_mine 0.200 | took_what_was_not_mine 0.200 | took_what_was_not_mine 0.200 |
| daniel | `find_out` | take_responsibility 1.158 | assert_authority 1.200 over take_responsibility 0.575 | take_responsibility 1.158 | take_responsibility 1.158 |
| daniel | `get_food` | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.575 over took_what_was_not_mine 0.200 |
| daniel | `guard_supplies` | take_responsibility 0.575 over assert_authority 0.500 | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 0.575 over assert_authority 0.500 | take_responsibility 0.575 over assert_authority 0.500 |
| daniel | `keep_peace` | prevent_argument 0.298 | protect 0.525 over share_information 0.320 | prevent_argument 0.298 | prevent_argument 0.298 |
| daniel | `look_after` | protect 0.250 | protect 0.775 over share_information 0.320 | protect 0.250 | protect 0.250 |
| daniel | `restore_standing` | take_responsibility 1.158 over assert_authority 0.500 | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 1.158 over assert_authority 0.500 | take_responsibility 1.158 over assert_authority 0.500 |
| elena | `avoid_exposure` | took_what_was_not_mine 0.385 | protect 0.860 over prevent_argument 0.495 | took_what_was_not_mine 0.385 | took_what_was_not_mine 0.385 |
| elena | `find_out` | take_responsibility 1.188 | take_responsibility 0.880 over share_information 0.725 | take_responsibility 1.188 | take_responsibility 1.188 |
| elena | `get_food` | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.880 over took_what_was_not_mine 0.385 |
| elena | `guard_supplies` | take_responsibility 0.880 over protect 0.558 | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 0.880 over protect 0.558 | take_responsibility 0.880 over protect 0.558 |
| elena | `keep_peace` | prevent_argument 0.405 | protect 0.860 over share_information 0.725 | prevent_argument 0.405 | prevent_argument 0.405 |
| elena | `look_after` | protect 0.558 | protect 1.418 over share_information 0.725 | protect 0.558 | protect 0.558 |
| elena | `restore_standing` | take_responsibility 1.188 over prevent_argument 0.405 | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 1.188 over prevent_argument 0.405 | take_responsibility 1.188 over prevent_argument 0.405 |
| leo | `avoid_exposure` | took_what_was_not_mine 0.478 | protect 0.780 over took_what_was_not_mine 0.478 | took_what_was_not_mine 0.478 | took_what_was_not_mine 0.478 |
| leo | `find_out` | take_responsibility 1.255 | take_responsibility 0.910 over share_information 0.665 | take_responsibility 1.255 | take_responsibility 1.255 |
| leo | `get_food` | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.910 over took_what_was_not_mine 0.478 |
| leo | `guard_supplies` | take_responsibility 0.910 over protect 0.373 | take_responsibility 0.910 over assert_authority 0.383 | take_responsibility 0.910 over protect 0.373 | take_responsibility 0.910 over protect 0.373 |
| leo | `keep_peace` | prevent_argument 0.305 | protect 0.780 over share_information 0.665 | prevent_argument 0.305 | prevent_argument 0.305 |
| leo | `look_after` | protect 0.373 | protect 1.153 over share_information 0.665 | protect 0.373 | protect 0.373 |
| leo | `restore_standing` | take_responsibility 1.255 over prevent_argument 0.305 | take_responsibility 0.910 over assert_authority 0.383 | take_responsibility 1.255 over prevent_argument 0.305 | take_responsibility 1.255 over prevent_argument 0.305 |
| mara | `avoid_exposure` | took_what_was_not_mine 0.340 | prevent_argument 0.563 over protect 0.450 | took_what_was_not_mine 0.340 | took_what_was_not_mine 0.340 |
| mara | `find_out` | take_responsibility 0.803 | share_information 0.740 over take_responsibility 0.445 | take_responsibility 0.803 | take_responsibility 0.803 |
| mara | `get_food` | take_responsibility 0.445 over took_what_was_not_mine 0.340 | take_responsibility 0.445 over took_what_was_not_mine 0.340 | take_responsibility 0.445 over took_what_was_not_mine 0.340 | take_responsibility 0.445 over took_what_was_not_mine 0.340 |
| mara | `guard_supplies` | protect 0.575 over take_responsibility 0.445 | protect 0.575 over take_responsibility 0.445 | protect 0.575 over take_responsibility 0.445 | protect 0.575 over take_responsibility 0.445 |
| mara | `keep_peace` | prevent_argument 0.365 | share_information 0.740 over prevent_argument 0.563 | prevent_argument 0.365 | prevent_argument 0.365 |
| mara | `look_after` | protect 0.575 | protect 1.025 over share_information 0.740 | protect 0.575 | protect 0.575 |
| mara | `restore_standing` | take_responsibility 0.803 over prevent_argument 0.365 | take_responsibility 0.445 over assert_authority 0.345 | take_responsibility 0.803 over prevent_argument 0.365 | take_responsibility 0.803 over prevent_argument 0.365 |

| | Count | Share of 28 |
|---|---|---|
| Adding company changed the intention | 12 | 42.9 % |
| Making them hungry changed the intention | **0** | 0.0 % |

Hunger is a real scaler kind that the shipped motivation rules use heavily. No rule in the candidate file reads it, and the measurement confirms it never moves an intention. Moving the person to another room changes the room and the tags on it; the column is there so that a circumstance which *is* structurally available but unread by these rules can be seen not to matter either, except where being in a different room changes who is present.

#### N5. Reproducibility

The selector draws no random number, so this should be exact rather than probable.

**140 of 140 replays identical**, intention and weight, to full precision.

A whole morning run twice with the selector installed: **identical**, and the intentions formed: **identical**.

#### N6. Fifty mornings, all of them held out from authoring

The candidate rules were committed before any of this ran. Every decision below is a case the rules were not written against.

**3826 decisions across 50 mornings.**

| | Count | Share |
|---|---|---|
| Decisions with a leading want | 3826 | 100.0 % |
| ...that formed an intention | 3826 | 100.0 % |
| ...that formed none | 0 | 0.0 % |

##### What each want turned into

| Want | Decisions | Distinct intentions | Distribution |
|---|---|---|---|
| `guard_supplies` | 1232 | 3 | `take_responsibility` 695 (56.4 %), `protect` 384 (31.2 %), `assert_authority` 153 (12.4 %) |
| `find_out` | 969 | 3 | `take_responsibility` 516 (53.3 %), `assert_authority` 365 (37.7 %), `share_information` 88 (9.1 %) |
| `look_after` | 851 | 1 | `protect` 851 (100.0 %) |
| `keep_peace` | 429 | 3 | `protect` 360 (83.9 %), `share_information` 56 (13.1 %), `prevent_argument` 13 (3.0 %) |
| `get_food` | 210 | 2 | `take_responsibility` 141 (67.1 %), `took_what_was_not_mine` 69 (32.9 %) |
| `avoid_exposure` | 104 | 3 | `took_what_was_not_mine` 88 (84.6 %), `prevent_argument` 12 (11.5 %), `protect` 4 (3.8 %) |
| `restore_standing` | 31 | 2 | `assert_authority` 16 (51.6 %), `take_responsibility` 15 (48.4 %) |

**Wants that produced more than one intention in practice: 6 of 7.** Single-valued in practice: `look_after`.

##### The same want, split by who wanted it

| Want | daniel | elena | leo | mara |
|---|---|---|---|---|
| `guard_supplies` | assert_authority 153, take_responsibility 29 | take_responsibility 209 | take_responsibility 457 | protect 384 |
| `find_out` | assert_authority 365, take_responsibility 260 | take_responsibility 116 | take_responsibility 129 | share_information 88, take_responsibility 11 |
| `look_after` | - | protect 308 | protect 283 | protect 260 |
| `keep_peace` | protect 65 | protect 219, prevent_argument 2 | protect 76, prevent_argument 2 | share_information 56, prevent_argument 9 |
| `get_food` | took_what_was_not_mine 37, take_responsibility 30 | take_responsibility 80, took_what_was_not_mine 10 | - | take_responsibility 31, took_what_was_not_mine 22 |
| `avoid_exposure` | took_what_was_not_mine 43 | - | - | took_what_was_not_mine 45, prevent_argument 12, protect 4 |
| `restore_standing` | - | take_responsibility 1 | - | assert_authority 16, take_responsibility 14 |

##### The same act, carrying different intentions

| Physical action | Times chosen | Wants behind it | Distinct intentions | Which |
|---|---|---|---|---|
| `wait` | 1706 | 3 | 6 | `assert_authority`, `prevent_argument`, `protect`, `share_information`, `take_responsibility`, `took_what_was_not_mine` |
| `search_room` | 520 | 2 | 3 | `assert_authority`, `share_information`, `take_responsibility` |
| `comfort:daniel` | 432 | 1 | 1 | `protect` |
| `check_pantry` | 257 | 4 | 4 | `assert_authority`, `share_information`, `take_responsibility`, `took_what_was_not_mine` |
| `comfort:mara` | 242 | 1 | 1 | `protect` |
| `comfort:elena` | 177 | 1 | 1 | `protect` |
| `observe:mara` | 87 | 1 | 1 | `assert_authority` |
| `go_to->kitchen` | 85 | 1 | 2 | `take_responsibility`, `took_what_was_not_mine` |
| `go_to->back_room` | 82 | 2 | 5 | `assert_authority`, `prevent_argument`, `share_information`, `take_responsibility`, `took_what_was_not_mine` |
| `go_to->bathroom` | 58 | 1 | 2 | `assert_authority`, `take_responsibility` |
| `observe:elena` | 58 | 1 | 1 | `assert_authority` |
| `go_to->brothers_room` | 50 | 1 | 1 | `take_responsibility` |
| `observe:leo` | 37 | 1 | 1 | `assert_authority` |
| `go_to->hallway` | 22 | 1 | 3 | `prevent_argument`, `protect`, `took_what_was_not_mine` |
| `go_to->living_room` | 13 | 1 | 2 | `protect`, `took_what_was_not_mine` |

##### Intentions reached from more than one want

| Intention | Times formed | Wants it came from |
|---|---|---|
| `protect` | 1599 | 4: `avoid_exposure`, `guard_supplies`, `keep_peace`, `look_after` |
| `take_responsibility` | 1367 | 4: `find_out`, `get_food`, `guard_supplies`, `restore_standing` |
| `assert_authority` | 534 | 3: `find_out`, `guard_supplies`, `restore_standing` |
| `took_what_was_not_mine` | 157 | 2: `avoid_exposure`, `get_food` |
| `share_information` | 144 | 2: `find_out`, `keep_peace` |
| `prevent_argument` | 25 | 2: `avoid_exposure`, `keep_peace` |

**Intentions reached from more than one want: 6.**

##### Is the belief doing the work, or the rule

`took_what_was_not_mine` is the one intention whose heaviest scaler is a belief: that I am answerable for the missing can. If the belief is carrying it, only people who hold that belief should form it. If the rule's other terms were carrying it, innocent people would form it too. This is measurable rather than arguable.

| | Value |
|---|---|
| Times `took_what_was_not_mine` was formed | 157 |
| ...by somebody who believes they are answerable | 152 |
| ...**by somebody who holds no such belief at all** | **5** |
| Lowest belief among those who formed it | 0.000 |
| Highest | 0.900 |

Of the 314 decisions where that intention was even reachable, 152 were taken by somebody who believes they are answerable, and 152 of those formed it.

##### How close the competition was

| | Count | Share of 3826 |
|---|---|---|
| Formations with a runner-up at all | 3466 | 90.6 % |
| ...decided by less than 0.10 | 149 | 3.9 % |

A mechanism whose winner is never contested is a table with extra steps. One whose winner is usually a coin-flip is noise. This is neither.

##### Eight traces, taken in order from the first morning

```
m1  daniel in kitchen with elena, leo, mara
  want        find_out at urgency 0.808
  competing   find_out 0.808, avoid_exposure 0.710, look_after:elena 0.575, look_after:mara 0.575
  beliefs     answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120
  feelings    anxiety 0.916, fear 0.874, shame 0.506
  memories    m1 concern, m1 concern, m0 threat
  act         check_pantry
  candidates  assert_authority 1.200 [pulling_rank_needs_an_audience 1.200]; take_responsibility 0.575 [somebody_has_to_do_it 0.575]; share_information 0.320 [so_that_they_know_too 0.320]
      assert_authority: trait dominant 0.850 x 0.450 = 0.383
      assert_authority: value control 1.000 x 0.350 = 0.350
      assert_authority: belief role_claim(daniel,leads_family) 0.800 x 0.300 = 0.240
      assert_authority: trait proud 0.850 x 0.150 = 0.128
      take_responsibility: trait honest 0.500 x 0.300 = 0.150
      take_responsibility: value family_safety 0.500 x 0.350 = 0.175
      take_responsibility: trait cautious 0.350 x 0.200 = 0.070
      share_information: trait honest 0.500 x 0.400 = 0.200
  INTENTION   assert_authority by 0.625 over take_responsibility
```

```
m1  elena in kitchen with daniel, leo, mara
  want        look_after about daniel at urgency 0.764
  competing   look_after:daniel 0.764, look_after:mara 0.764, keep_peace 0.612, get_food 0.603
  beliefs     more_knowledgeable(leo,survival) 0.738, role_claim(elena,leads_family) 0.600, supplies_short 0.550, tendency(daniel,needs_to_be_in_charge) 0.700
  feelings    anxiety 0.958, fear 0.805, gratitude:daniel 0.224
  memories    m1 concern, m1 concern, m0 take_responsibility
  act         comfort:daniel -> daniel
  candidates  protect 1.705 [standing_between_them_and_it 1.147 + keeping_it_off_them 0.558]; share_information 0.725 [so_that_they_know_too 0.725]; prevent_argument 0.495 [not_making_a_scene_of_it 0.495]
      protect: trait empathetic 0.900 x 0.400 = 0.360
      protect: value family_safety 1.000 x 0.350 = 0.350
      protect: feeling anxiety toward anyone 0.958 x 0.300 = 0.287
      protect: trait empathetic 0.900 x 0.300 = 0.270
      protect: value closeness 0.750 x 0.250 = 0.188
      share_information: trait honest 0.700 x 0.400 = 0.280
      share_information: value closeness 0.750 x 0.300 = 0.225
      share_information: value fairness 0.500 x 0.200 = 0.100
      prevent_argument: trait cautious 0.700 x 0.350 = 0.245
      prevent_argument: value closeness 0.750 x 0.300 = 0.225
      prevent_argument: trait dominant 0.500 x -0.250 = -0.125
  INTENTION   protect by 0.980 over share_information
```

```
m1  leo in kitchen with daniel, elena, mara
  want        find_out at urgency 0.437
  competing   keep_peace 0.605, look_after:daniel 0.601, look_after:elena 0.601, look_after:mara 0.601
  beliefs     more_knowledgeable(leo,survival) 0.850, supplies_short 0.550, tendency(daniel,does_not_respect_me) 0.180, tendency(daniel,makes_risky_calls) 0.450, tendency(daniel,needs_to_be_in_charge) 0.550, tendency(daniel,treats_me_like_a_child) 0.120
  feelings    anxiety 0.980, fear 0.700, gratitude:daniel 0.086
  memories    m1 concern, m1 concern, m1 concern
  act         check_pantry
  candidates  take_responsibility 0.910 [somebody_has_to_do_it 0.910]; share_information 0.665 [so_that_they_know_too 0.665]; assert_authority 0.333 [pulling_rank_needs_an_audience 0.333]
      take_responsibility: trait honest 0.800 x 0.300 = 0.240
      take_responsibility: value family_safety 1.000 x 0.350 = 0.350
      take_responsibility: trait cautious 0.700 x 0.200 = 0.140
      share_information: trait honest 0.800 x 0.400 = 0.320
      share_information: value closeness 0.250 x 0.300 = 0.075
      share_information: value fairness 0.750 x 0.200 = 0.150
      assert_authority: trait dominant 0.350 x 0.450 = 0.158
      assert_authority: trait proud 0.500 x 0.150 = 0.075
  INTENTION   take_responsibility by 0.245 over share_information
```

```
m1  mara in kitchen with daniel, elena, leo
  want        find_out at urgency 0.407
  competing   look_after:daniel 0.855, look_after:elena 0.835, avoid_exposure 0.553, get_food 0.504
  beliefs     more_knowledgeable(leo,survival) 0.200, supplies_short 0.550, tendency(daniel,does_not_respect_me) 0.205, tendency(daniel,treats_me_like_a_child) 0.604, tendency(elena,keeps_things_from_me) 0.350
  feelings    fear 0.910, anxiety 0.855, relief 0.506
  memories    m1 concern, m1 concern, m0 concern
  act         check_pantry
  candidates  share_information 0.740 [so_that_they_know_too 0.740]; take_responsibility 0.445 [somebody_has_to_do_it 0.445]; assert_authority 0.295 [pulling_rank_needs_an_audience 0.295]
      share_information: trait honest 0.550 x 0.400 = 0.220
      share_information: value closeness 1.000 x 0.300 = 0.300
      share_information: value fairness 0.500 x 0.200 = 0.100
      take_responsibility: trait honest 0.550 x 0.300 = 0.165
      take_responsibility: trait cautious 0.500 x 0.200 = 0.100
      assert_authority: trait dominant 0.250 x 0.450 = 0.113
      assert_authority: trait proud 0.550 x 0.150 = 0.083
  INTENTION   share_information by 0.295 over take_responsibility
```

```
m4  daniel in kitchen with elena, leo, mara
  want        find_out at urgency 0.757
  competing   find_out 0.757, restore_standing 0.615, get_food 0.568, avoid_exposure 0.542
  beliefs     answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120
  feelings    anxiety 0.698, fear 0.666, anger 0.611
  memories    m4 neutral, m4 neutral, m4 assert_authority
  act         search_room
  candidates  assert_authority 1.200 [pulling_rank_needs_an_audience 1.200]; take_responsibility 0.575 [somebody_has_to_do_it 0.575]; share_information 0.320 [so_that_they_know_too 0.320]
      assert_authority: trait dominant 0.850 x 0.450 = 0.383
      assert_authority: value control 1.000 x 0.350 = 0.350
      assert_authority: belief role_claim(daniel,leads_family) 0.800 x 0.300 = 0.240
      assert_authority: trait proud 0.850 x 0.150 = 0.128
      take_responsibility: trait honest 0.500 x 0.300 = 0.150
      take_responsibility: value family_safety 0.500 x 0.350 = 0.175
      take_responsibility: trait cautious 0.350 x 0.200 = 0.070
      share_information: trait honest 0.500 x 0.400 = 0.200
  INTENTION   assert_authority by 0.625 over take_responsibility
```

```
m4  leo in kitchen with daniel, elena, mara
  want        look_after about daniel at urgency 0.523
  competing   look_after:daniel 0.523, look_after:mara 0.523, get_food 0.466, guard_supplies 0.433
  beliefs     more_knowledgeable(leo,survival) 0.850, supplies_short 0.550, tendency(daniel,does_not_respect_me) 0.180, tendency(daniel,makes_risky_calls) 0.450, tendency(daniel,needs_to_be_in_charge) 0.550, tendency(daniel,treats_me_like_a_child) 0.120
  feelings    anxiety 0.649, fear 0.464, gratitude:daniel 0.057
  memories    m4 neutral, m4 take_responsibility, m4 neutral
  act         comfort:daniel -> daniel
  candidates  protect 1.347 [standing_between_them_and_it 0.975 + keeping_it_off_them 0.373]; share_information 0.665 [so_that_they_know_too 0.665]; prevent_argument 0.383 [not_making_a_scene_of_it 0.383]
      protect: trait empathetic 0.700 x 0.400 = 0.280
      protect: value family_safety 1.000 x 0.350 = 0.350
      protect: feeling anxiety toward anyone 0.649 x 0.300 = 0.195
      protect: trait empathetic 0.700 x 0.300 = 0.210
      protect: value closeness 0.250 x 0.250 = 0.063
      share_information: trait honest 0.800 x 0.400 = 0.320
      share_information: value closeness 0.250 x 0.300 = 0.075
      share_information: value fairness 0.750 x 0.200 = 0.150
      prevent_argument: trait cautious 0.700 x 0.350 = 0.245
      prevent_argument: value closeness 0.250 x 0.300 = 0.075
      prevent_argument: trait dominant 0.350 x -0.250 = -0.088
  INTENTION   protect by 0.682 over share_information
```

```
m4  mara in kitchen with daniel, elena, leo
  want        look_after about daniel at urgency 0.764
  competing   look_after:daniel 0.764, get_food 0.515, avoid_exposure 0.443, find_out 0.356
  beliefs     more_knowledgeable(leo,survival) 0.200, supplies_short 0.550, tendency(daniel,does_not_respect_me) 0.205, tendency(daniel,treats_me_like_a_child) 0.604, tendency(elena,keeps_things_from_me) 0.350
  feelings    fear 0.728, anxiety 0.684, relief 0.404
  memories    m4 share_information, m4 neutral, m4 neutral
  act         comfort:daniel -> daniel
  candidates  protect 1.230 [standing_between_them_and_it 0.655 + keeping_it_off_them 0.575]; share_information 0.740 [so_that_they_know_too 0.740]; prevent_argument 0.563 [not_making_a_scene_of_it 0.563]
      protect: trait empathetic 0.750 x 0.400 = 0.300
      protect: feeling anxiety toward anyone 0.684 x 0.300 = 0.205
      protect: trait empathetic 0.750 x 0.300 = 0.225
      protect: value closeness 1.000 x 0.250 = 0.250
      share_information: trait honest 0.550 x 0.400 = 0.220
      share_information: value closeness 1.000 x 0.300 = 0.300
      share_information: value fairness 0.500 x 0.200 = 0.100
      prevent_argument: trait cautious 0.500 x 0.350 = 0.175
      prevent_argument: value closeness 1.000 x 0.300 = 0.300
      prevent_argument: trait dominant 0.250 x -0.250 = -0.063
  INTENTION   protect by 0.490 over share_information
```

```
m9  daniel in kitchen with elena, leo, mara
  want        find_out at urgency 0.696
  competing   find_out 0.696, get_food 0.591, guard_supplies 0.426, restore_standing 0.392
  beliefs     answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120
  feelings    gratitude:elena 0.675, relief 0.426, anger 0.389
  memories    m9 reassurance, m9 support, m4 neutral
  act         search_room
  candidates  assert_authority 1.200 [pulling_rank_needs_an_audience 1.200]; take_responsibility 0.575 [somebody_has_to_do_it 0.575]; share_information 0.320 [so_that_they_know_too 0.320]
      assert_authority: trait dominant 0.850 x 0.450 = 0.383
      assert_authority: value control 1.000 x 0.350 = 0.350
      assert_authority: belief role_claim(daniel,leads_family) 0.800 x 0.300 = 0.240
      assert_authority: trait proud 0.850 x 0.150 = 0.128
      take_responsibility: trait honest 0.500 x 0.300 = 0.150
      take_responsibility: value family_safety 0.500 x 0.350 = 0.175
      take_responsibility: trait cautious 0.350 x 0.200 = 0.070
      share_information: trait honest 0.500 x 0.400 = 0.200
  INTENTION   assert_authority by 0.625 over take_responsibility
```


#### N7. Controls

The selector must be able to be taken away without trace, or nothing measured above is attributable to it.

| Condition | Seed | Selector off | Selector installed, returning null | Selector installed and forming |
|---|---|---|---|---|
| `daniel_ate_it` | 1 | identical | identical | differs |
| `daniel_hid_it` | 1 | identical | identical | differs |
| `mara_ate_it` | 1 | identical | identical | differs |
| `elena_fed_mara` | 1 | identical | identical | differs |
| `miscount` | 1 | identical | identical | differs |

| | Count | Share |
|---|---|---|
| C1: selector off reproduces the shipped baseline | 50 of 50 | 100.0 % |
| C2: selector installed but returning null does too | 50 of 50 | 100.0 % |
| Mornings the formed intentions changed | 50 of 50 | 100.0 % |

The last row is not a control but a consequence: it is how often intentions formed by this mechanism, and read by the three shipped appraisal rules that read any intention at all, went on to change what somebody did.

---

## predictions.md

### Intention formation: predictions

Written and committed **before a single case was run**, together with the
candidate rule file they are about. Kept as written.

#### The question

> Can Fallow derive a context-sensitive intention from an existing motivation
> without relying on a universal hardcoded Want -> Intention mapping?

#### The three things kept apart

| | | Example |
|---|---|---|
| **Motivation** | what the person is currently driven toward | `restore_standing` |
| **Intention** | what they take themselves to be accomplishing | `assert_authority` |
| **Physical action** | what they actually do | `check_pantry` |

The previous experiment proved the third is independent of the second. This one
tests whether the second is independent of the first.

#### How the candidate mechanism was authored, and when

The rules were written **blind**: from the shipped character sheets, the shipped
rule files and the shipped vocabulary, and from nothing else. No case of any
kind had been run, so no output could be fitted. The rule file is committed in
the same commit as this document and was not edited afterwards. Every case in the
experiment is therefore held out from authoring.

Whether that discipline held is checkable: `git log -p` on
`Assets/_Project/Data/Experiments/intentions.json` should show one commit, dated
before the fixture that reads it.

#### The mechanism, stated before it was run

A **candidate rule** says that a given intention is *available* to a given set of
wants, in given circumstances, with a weight that depends on the person.

```
{ id, motives: [...], intent, when: { circumstances only }, base, scaled_by: [...] }
```

Three properties are structural, not promises:

1. **`when` cannot ask about the person.** It is the shipped `SituationCondition`,
   which has six fields, all circumstantial (alone, in my own room, in somebody
   else's, the room holds food, I have searched here, how many others are
   present). It has no field for a trait, a value, a feeling or a need. That is
   not a rule I am following; it is the type.
2. **Everything about the person is a scaler**, evaluated by the shipped
   `ScalerEval` — the same code that weighs an interpretation rule and prices an
   action. Traits, values, beliefs, the ledger, live emotions, memories,
   perceptiveness, bodily need.
3. **No randomness anywhere.** The winner is the heaviest intention, ties broken
   ordinally. Any variation observed is therefore attributable to context or to
   the person, and to nothing else.

Rules speaking for the same intention add up, exactly as interpretation rules
speaking for the same reading do. If nothing matches, the mechanism returns
**null** and the act carries no intention, which is the shipped behaviour.

#### What is hand-authored, stated plainly

The `motives` list on each rule is a hand-authored table of **which intentions a
want may express**. I am not going to pretend otherwise. The claim being tested
is that it is a **constraint** table and not a **mapping** table, and that claim
is falsifiable in two ways, both of which are measured:

- if any want under test has only one reachable intention, it is a mapping;
- if any want produces the same intention in every context and for every person,
  it is a mapping in effect even if not in form.

The rule count, and the number of intentions each want can reach and does reach,
are reported as measurements rather than asserted.

#### Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | Motivation does not uniquely determine intention: the same want under different contexts produces different intentions | every want yields one intention everywhere |
| P2 | Context matters: changing one contextual factor, with motivation and person unchanged, changes the intention | no contextual change ever moves it |
| P3 | Person matters: two characters with the same want in the same circumstances form different intentions | all four characters agree everywhere |
| P4 | Motivation still constrains: no want produces an intention outside the set its rules allow | an unrelated intention appears |
| P5 | The same intention serves different motivations | each intention is reachable from one want only |
| P6 | Intention stays distinct from action: one physical action still carries different intentions | the action determines the intention |
| P7 | No universal Want -> Intention lookup is needed: at least two wants are observed producing two or more different intentions in live mornings | every want is single-valued in practice |
| P8 | Reproducible: same state, same seed, same intention, every time | any run differs |
| P9 | Counterfactually sensitive in the right places: a change to something a rule reads can change the intention; a change to something no rule reads never does | an irrelevant change moves it, or no relevant change does |
| P10 | Generalises: the rules were authored blind, so every live morning is a held-out case. They should produce intentions across wants and people without an empty or degenerate result | most decisions get no intention, or one intention dominates everything |

**Controls, all of which must hold:**

| | Control |
|---|---|
| C1 | With the selector off, the morning is identical to the shipped baseline |
| C2 | With the selector installed but returning null, identically so |
| C3 | Same state and seed replayed gives the same intention |
| C4 | A perturbation of an unread circumstance changes nothing |
| C5 | The same probe run for four different characters |
| C6 | Every live morning is held out from authoring |

**Committed in advance, and riskier:**

- The clearest contrast should be **`restore_standing` with an audience against
  `restore_standing` alone**, for Daniel. Pulling rank needs somebody to pull it
  on. I expect `assert_authority` with company and `take_responsibility` alone.
- **Daniel and Leo should disagree** on `restore_standing` in identical
  circumstances — Daniel dominant 0.85 and holding `role_claim(daniel,
  leads_family)` at 0.80; Leo dominant 0.35, honest 0.80, and holding no such
  claim.
- I expect **`share_information` and `protect` to be reachable but rarely to
  win**, because the wants that can express them are not the wants that dominate
  these mornings.
- I expect the experiment to be **limited by the vocabulary, not by the
  mechanism**. Six intentions exist. The brief's own examples for
  `restore_standing` — demonstrate competence, avoid appearing weak, quietly
  prove themselves right, seek recognition — are four distinctions that the
  shipped vocabulary cannot make. If the result is thinner than the hypothesis
  deserves, I expect that to be why.

**What would count as failure**, in the brief's own terms: a constant mapping
(P1, P7 falsified) or arbitrary output (P8, P9 falsified). Both are measured
directly rather than judged by whether the intentions sound human.

---

## results.md

### Intention formation: results against the predictions

The measurements are in `measurements.md`, generated by
`IntentionFormationExperimentTests`. The predictions and the candidate rules
were committed together, in one commit, before any of it was run.

#### Runs

| | |
|---|---|
| Hand-authored surface | **10 candidate rules**, over the 6 shipped intentions and 7 shipped wants. Nothing else |
| Production changes | **none**. No file under `Scripts/Core` was touched, and no shipped data file was edited |
| Controlled probes | 4 people x 7 wants x 4 contexts |
| Live mornings | 5 conditions x 10 seeds = 50, **all held out from authoring** |
| Decisions measured | **3,826** |
| Randomness in the selector | none |

#### Predictions

| # | Prediction | Result | Evidence |
|---|---|---|---|
| P1 | Motivation does not uniquely determine intention | **PASS** | N2: 12 of 28 (person, want) pairs formed a different intention with an audience than without. N6: 6 of 7 wants produced more than one intention across 3,826 live decisions |
| P2 | Context matters | **PASS** | N2 and N4: adding company, with the want and the person unchanged, moved the intention in 42.9 % of cells |
| P3 | Person matters | **PASS** | N3: the four disagreed on 5 of 7 wants in identical circumstances. N6: `guard_supplies` became `assert_authority` for Daniel, `take_responsibility` for Leo and Elena, `protect` for Mara |
| P4 | Motivation still constrains | **PASS** | No formed intention was ever outside the set its want's rules allow. This is structural — the selector only weighs candidates in scope — and no arbitrary intention appeared in 3,826 decisions |
| P5 | The same intention serves different motivations | **PASS** | All 6 intentions were reached from 2 or more wants. `protect` from 4, `take_responsibility` from 4, `assert_authority` from 3 |
| P6 | Intention stays distinct from action | **PASS** | `check_pantry`, 257 times, from 4 wants, carrying **4 different intentions**. `wait`, 1,706 times, carrying **all 6** |
| P7 | No universal Want -> Intention lookup is needed | **PASS** | 6 of 7 wants are many-valued in practice. The one exception is recorded as a failure below |
| P8 | Reproducible | **PASS** | 140 of 140 replays identical in intention and weight to full precision; a whole morning run twice gives identical acts and identical intentions |
| P9 | Counterfactually sensitive in the right places | **PASS** | A circumstance the rules read moved the intention in 12 of 28 cells; hunger, which no candidate rule reads, moved it in **0 of 28** |
| P10 | Generalises to held-out cases | **PASS, with one degenerate want** | Every one of the 50 mornings is held out. 3,826 of 3,826 decisions formed an intention, spread over all 6, with 90.6 % of formations contested by a runner-up. But see `look_after` |

#### Controls

| | Control | Result |
|---|---|---|
| C1 | Selector off reproduces the shipped baseline | **50 of 50** mornings identical, every act and margin to full precision |
| C2 | Selector installed but returning null does too | **50 of 50** |
| C3 | Same state and seed replayed gives the same intention | 140 of 140, and a whole morning twice |
| C4 | An unread circumstance changes nothing | 0 of 28 |
| C5 | The same probe for four characters | N3, all four |
| C6 | Every live morning held out from authoring | one commit, before the fixture existed |

#### The two riskier claims, committed in advance

| Claim | Result |
|---|---|
| Daniel's clearest contrast should be `restore_standing` with an audience against alone: `assert_authority` in company, `take_responsibility` by himself | **HELD.** 1.700 to `assert_authority` with company; 1.158 to `take_responsibility` alone |
| Daniel and Leo should disagree on `restore_standing` in identical circumstances | **HELD.** Daniel `assert_authority` 1.700, Leo `take_responsibility` 0.910, and the terms say why: dominant 0.85 against 0.35, and a `role_claim` Leo does not hold |
| `share_information` and `protect` should be reachable but rarely win | **HALF WRONG.** `share_information` is rare as expected (144 of 3,826). `protect` is the **most formed intention of all** (1,599), which I did not expect |
| The experiment should be limited by the vocabulary rather than the mechanism | **HELD**, and it is the main limitation. See the report |

#### Failures

**`look_after` produced `protect` in 851 of 851 decisions.** For that one want the
mechanism behaved as a lookup table, which is the failure mode the brief names.
The cause is visible in the rules and is not a tuning accident: `protect` has two
candidates and one of them needs no circumstance at all, while its competitors
have one each. Two rules beat one (**refined later**: it is the summed weight and
not the count — see `Docs/experiments/intention-generalization/`), for the same reason the previous experiment
found an intention's effect size tracking its reader count. The pathology
followed me from one layer to the next.

**`took_what_was_not_mine` was formed 5 times by somebody who holds no belief
that they are answerable** for the missing can. 152 of the 157 formations were by
somebody who does, and every single one of the 152 decisions taken by an
answerable person in reach of that intention formed it — so the belief is doing
the work almost all of the time. But the rule's other terms can carry it alone
when nothing else in scope matches, and an innocent person then reads their own
act as a theft.

#### Surprises

- **`protect` dominates.** 1,599 of 3,826, reached from four different wants. Three
  of the four people are highly empathetic and the house is anxious all morning,
  so the scaler that was meant to distinguish people ended up agreeing about most
  of them.
- **Standing still has a reason.** `wait`, the act the Action Representation Audit
  singled out as carrying nothing, carried all six intentions across its 1,706
  uses.
- **`restore_standing` is almost absent.** 31 decisions of 3,826, consistent with
  the previous experiment finding it never led a single pantry-check.
- **The leading want is not always the strongest want.** Leo at m1 is led by
  `find_out` at 0.437 while `keep_peace` sits at 0.605, because the leading want
  is the one that best explains the act chosen, not the loudest one. Intentions
  are therefore formed from the want that won the act, which is the right choice
  but worth naming.

#### The one-line answer

**Yes.** A context-sensitive intention can be derived from an existing want, by
the person's own traits, values, beliefs, memories and feelings, with no
universal Want -> Intention mapping, using ten rules and no new engine code. What
remains unproven is whether it holds outside this cast, this house and six
available words.

