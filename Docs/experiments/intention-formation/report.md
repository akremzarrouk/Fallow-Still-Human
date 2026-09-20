# Intention formation

*Can Fallow generate a plausible intention from an existing motivation and the
character's context, without a universal hardcoded Want -> Intention table?*

## 1. Hypothesis

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

## 2. What was implemented, and what was not

**No production change.** Not one file under `Assets/_Project/Scripts/Core` was
touched, and no shipped data file was edited. `IntentOfAct` remains what it was:
a hook, null by default.

**Everything hand-authored is one file**,
`Assets/_Project/Data/Experiments/intentions.json`, which nothing in
`Fallow.Core` loads. It contains **ten candidate rules**. That is the entire
authored surface of the experiment and it is listed in full in `measurements.md`.

**The selector is about thirty lines** in the test fixture, over shipped
machinery. It has no randomness of any kind.

## 3. The candidate mechanism

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

## 4. Was a lookup table used? Yes, partly — and here is exactly where

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

## 5. How authoring was kept honest

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

## 6. Design and controls

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

## 7. Results

### The core contrast, and it is one trace

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

### The prediction table

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

### Is the belief doing the work, or the rule?

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

## 8. Failures

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

## 9. Limitations and overfitting risks

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

## 10. Classification

| | |
|---|---|
| **PROVEN** | A want does not determine an intention: 6 of 7 wants many-valued over 3,826 held-out decisions. Context changes it (12 of 28 pairs on the audience alone). The person changes it (5 of 7 wants, four characters, identical circumstances). It is exactly reproducible (140 of 140). It is counterfactually specific (0 of 28 on an unread circumstance). The mapping is many-to-many both ways (all 6 intentions from 2+ wants). The act stays independent (`check_pantry`: 4 intentions; `wait`: 6). The controls are exact (C1, C2 both 50 of 50). **And none of it required a universal Want -> Intention table, new engine code, a new action, a new want, a new trait, a new emotion, a planner or an LLM.** |
| **PLAUSIBLE** | That the variation is of the *right kind* and not merely of the right shape. The traces read as defensible — Daniel pulls rank where Leo gets on with it — but "defensible" is a judgement, and the brief is right that it is not evidence |
| **UNPROVEN** | Generalisation beyond this cast, this house and this morning. That the approach survives a vocabulary larger than six. That ten rules scale. That the intentions formed are the *correct* ones rather than merely consistent ones |
| **FAILED** | `look_after` -> `protect`, 851 of 851: for that want the mechanism is a lookup table. And an intention about the past was formed five times by somebody with no belief they did anything |
| **UNKNOWN** | Whether an observer could infer any of this — the previous experiment showed the witness is given nothing to infer from, and nothing here changes that. Whether intentions formed this way would remain stable across a day rather than a morning |

## 11. Verdict

# KEEP

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

## 12. The question the brief asks to answer explicitly

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
