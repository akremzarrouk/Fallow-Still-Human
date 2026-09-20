# same-act-different-reason: all documents

Merged by `merge-slice-docs.py` from the 4 Markdown files in `Docs/experiments/same-act-different-reason/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)

---

## report.md

### Same act, different reason

*What, if anything, distinguishes the same physical act when it is chosen for
different reasons?*

#### 1. Why this was asked

The Action Representation Audit found that many wants converge on the same
physical acts, that the chosen act does not carry the want that produced it, and
that a person subsequently reads their own act as an outside event. The
intent-carrying experiment then showed that an intention, if supplied, can cross
act -> event -> perception -> memory -> appraisal -> motivation -> later act. The
accumulated-history experiment supplied the other half: repeated experience with
somebody can change what a later event **means** — Elena's reading of being
searched moved from `threat` to `disrespect`, and with it her whole emotional
and motivational state — and yet **her act did not change**, because `find_out`,
`restore_standing` and `get_food` all ask for the same things.

That left one question standing between the evidence and a redesign. A person can
perform the same physical movement for different reasons; a simulation does not
need a separate act for every motive. The question is whether it **loses the
causal meaning** of an act merely because the physical manifestation is shared.

This experiment tests that, and nothing else. It implements no solution.

#### 2. What was and was not done

**No production change of any kind.** Not one file under `Scripts/Core` or
`Data` was touched. No new action, want, rule, price, threshold, mapping,
relationship, psychology or reader was added. The experiment reuses the
`IntentOfAct` hook that the intent-carrying experiment introduced, which is null
by default and is set only inside the test.

The hook is a hook and not a rule on purpose. Which intention an act expresses is
a claim about people, and nothing in this codebase is entitled to make it. The
experiment supplies the intention explicitly so that one question can be isolated:

> If two otherwise identical physical acts are done with different intended
> meanings, can the existing pipeline tell them apart?

That is a different question from whether the simulation can *infer* the
intention, and this experiment does not test inference at all.

#### 3. Design

| | |
|---|---|
| The act | `check_pantry`, which four shipped proposals ask for: `see_what_there_is` (`get_food`, fit 0.40), `count_it_properly` (`guard_supplies`, 0.50), `look_at_the_shelf_yourself` (`find_out`, 0.60), `check_it_yourself` (`restore_standing`, 0.45) |
| Conditions | the five design conditions, seeds 1 to 10: 50 mornings |
| Acts found | 153 real pantry-checks that ran their course and became events |
| Intentions | all six in the shipped vocabulary |
| Controls | (a) no hook at all; (b) hook set, returning null; (c) hook set and then removed |
| Held fixed | actor, act, minute, room, world state, seed, random stream, and every circumstance up to the moment the act finishes |
| Varied | the intention on the event, and nothing else |

The arms are identical up to the completion minute **by construction**, not by
luck: the intention is attached at the instant the act becomes an event, and
nothing earlier can read it. The random stream is forked per person and per
minute from the seed, so an arm cannot draw a different number from an arm that
diverged later.

**Choosing the intentions.** The brief names three motivation contexts —
`find_out`, `restore_standing`, `get_food` — and asks for the intentions behind
them. Rather than invent labels, the experiment runs every intention the shipped
vocabulary has, and reports the fit problem as a result. See section 9.

#### 4. The three questions, kept apart

| | Question | Answer |
|---|---|---|
| 1 | **Representation** — can the same act carry different intentions? | **Yes.** 6 of 6, with the act, its event, its target, its valence and its sentence unchanged |
| 2 | **Propagation** — does the distinction survive to perception, appraisal, memory, belief? | **Partly.** It reaches the actor's own reading intact, and appraisal reads it. Nothing else does |
| 3 | **Behaviour** — can different intentions end in different acts? | **Yes.** 189 of 918 arms, 20.6 %, traceably |

A failure at 3 would not have been a failure at 1. As it happens there is no
failure at any of the three; the failure is narrower and more specific, and it is
at 2.

#### 5. The causal trace, with every boundary marked

##### A. `assert_authority` — an intention with a reader

```
want: find_out, urgency 0.808
    | PRESERVED on the decision (ScoredOption.Contributions keeps the motive)
selected act: check_pantry
    | DISCARDED: an ActionOption is a kind, a target and a destination. It does
    | not know which want asked for it
act completes
    | CREATED: the experiment supplies the intention here, at the one point in
    | the code where an act turns into an event
world event: count_supplies, actor daniel, target none, topic supplies,
             valence neutral, intent assert_authority
    | PRESERVED on the event. The physical event is byte-identical to the
    | baseline in every other field, including the sentence
access: daniel was there and saw it
    | PRESERVED
actor interpretation: "knew their own intention: assert_authority", weight 1.00
    | TRANSFORMED: the intention becomes the meaning
    | DISCARDED: the reading the rules would have given is not computed at all
appraisal: asserting_yourself_is_done_angry -> anger 0.61, aimed at nobody
    | PRESERVED. This is the only door in the system
memory: kept as `assert_authority`, salience 0.670
    | PRESERVED as a string, UNREADABLE in practice: no memory scaler names it
belief: no nudge fires
    | DISCARDED: no belief rule is keyed on any intention
motivation: restore_standing 0.392 -> 0.615
    | PRESERVED, through the emotion and not through the intention
later act: in 48 of 153 cases, a decision somewhere in the house differs
```

##### B. `take_responsibility` — an intention with no reader

Identical to A as far as memory, and then:

```
appraisal: no rule is keyed on take_responsibility
    | DISCARDED. Everything downstream is the baseline
memory: kept as `take_responsibility`
    | PRESERVED as a string, and never read again by anything
later act: 0 of 153
```

##### C. The witness

```
world event carries intent assert_authority
access: elena was there and saw it
    | PRESERVED
witness interpretation: the interpreter hands somebody their own intention only
    when the event's actor is the perceiver. Elena is not, so the rules run
    | DISCARDED at the perception boundary — correctly
witness reading: neutral, weight 0.00, felt nothing
    | identical in all seven arms
```

#### 6. Where the architecture drops causal information

Four boundaries, in order of how much they cost.

**1. The vocabulary boundary (new, and upstream of everything).** `motives` has
seven entries and `self_meanings` has six. They are disjoint sets and nothing
maps between them. So a want frequently *cannot be said* as an intention even in
principle: `get_food` has no label at all, and `find_out` has only an
approximation. This is not a missing mapping — it is a missing word. Every other
loss below is downstream of it.

**2. The act boundary (already known, confirmed).** `ActionOption` is a kind, a
target and a destination. The want that produced it is on the decision, not on
the act, and the audit already established this. Confirmed again here: all 153
pantry-checks produce **one distinct event shape**.

**3. The reader boundary (the main finding).** An intention reaches exactly one
kind of reader, appraisal, and only three of the six intentions have one:

| Intention | Interpretation | Belief nudges | Appraisal | Memory scalers | Readers |
|---|---|---|---|---|---|
| `assert_authority` | 0 | 0 | 1 | 0 | **1** |
| `protect` | 0 | 0 | 1 | 0 | **1** |
| `took_what_was_not_mine` | 0 | 0 | 2 | 0 | **2** |
| `prevent_argument` | 0 | 0 | 0 | 0 | **0** |
| `share_information` | 0 | 0 | 0 | 0 | **0** |
| `take_responsibility` | 0 | 0 | 0 | 0 | **0** |

For comparison, the meanings a person reads in somebody *else* have up to seven
(`disrespect`). An intention is a second-class meaning throughout: no attention
weight can even be placed on one, because attention weights are validated against
the other set.

**4. The displacement boundary.** The interpreter, handed an intention, returns
*before* consulting any rule. So an intention does not add to the rule reading —
it replaces it. An intention nothing reads can therefore leave a person with
**less** than no intention at all. The mechanism is certain from the code. Its
cost here is zero, for a reason worth stating: no interpretation rule matches
`count_supplies` at all unless the shelf is nearly bare, and in 50 mornings it
never was. There was nothing to displace.

#### 7. What the numbers say

918 arms. The separation is total:

| Readers | Intentions | Arms where a decision moved |
|---|---|---|
| 0 | `prevent_argument`, `share_information`, `take_responsibility` | **0 of 153, each** |
| 1 | `assert_authority`, `protect` | 48 and 61 of 153 |
| 2 | `took_what_was_not_mine` | 80 of 153 |

There is no partial credit and no leakage. Whether a reason matters is decided
entirely by whether somebody once happened to write an appraisal rule naming it —
and the ordering of effect sizes is the reader count, not the meaning.

That last point is the uncomfortable one, and it was predicted in advance.
`took_what_was_not_mine` — "I took what was not mine" — is the *worst* fit of the
six for a man counting his own family's pantry, and it produces the largest
effect of the six, because two rules name it and one names `assert_authority`.
The system's sense of how much a reason matters is a count of rules, not a
judgement about people.

#### 8. Actor against witness

The actor recovers the intention perfectly: his own reading of his own act **is**
the intention, at weight 1.00, with no runner-up and no rule consulted.

The witness receives **nothing**. One distinct witness reading across seven arms:
same access, same interpretation, same weight, same salience, same appraisal
(none), same belief nudges (none), same next decision. Elena standing in the room
while Daniel counts the food cannot tell "he is checking" from "he is pulling
rank" from "he is ashamed of what he did in the night".

**This is not a defect, and it should not be fixed by handing her the
intention.** Knowledge locality is working exactly as designed: the interpreter
gives somebody an intention only when they are the actor. A private intention
that leaks to observers would be worse than one that does not.

But the honest form of the finding is narrower than "intention is private". A
real person watching this would have evidence: how long he took, whether he had
already looked once, what his face did, whether he said anything, whether he
looked at *her* while doing it. **The simulation gives the witness none of that
either.** The event carries an action, a target, a topic, a valence and a
sentence. So the correct statement is not "the witness cannot infer the
intention" but "**the witness is given nothing from which anyone could infer
anything**". Whether that gap should be closed, and how, is not this
experiment's question.

#### 9. The vocabulary cannot say what the brief asked

The brief named three motivation contexts and offered three intentions for them.
Tested against the shipped vocabulary:

| Want | An intention that says what it intends | Verdict |
|---|---|---|
| `restore_standing` | `assert_authority` | **Expressible.** The shipped backstory already pairs them (b06) |
| `find_out` | `take_responsibility` | **Approximable only.** The shipped precedent is real — backstory p02 is Daniel searching the house under it, glossed "searching the house is what someone in charge does" — but that is the intention of a man in charge, not of a man who wants to know. And it has **no reader** |
| `get_food` | — | **Inexpressible.** No label in the vocabulary says wanting to eat. The nearest, `took_what_was_not_mine`, is about having done wrong |

So one of the brief's three intentions cannot be said at all, and a second can
only be approximated by a label that nothing reads. This is reported rather than
fixed, as instructed. It is also the deepest of the four loss boundaries, because
it is the one that makes the others unavoidable.

#### 10. No cheating

The brief warns against a result that is true only because a different string is
stored. Three checks against that:

- The **controls** are exact, not approximate. Hook unset, hook returning null,
  and hook attached then removed all reproduce the baseline in **50 of 50**
  mornings, every act and every margin to full floating-point precision.
- The three intentions with no reader moved **nothing, ever**, in 153 cases each.
  If the experiment could pass merely by storing a string, they would have moved
  something. They did not. The metadata alone does precisely nothing.
- The three that did move something moved it through a **named, shipped rule**
  that can be pointed at in the trace: `asserting_yourself_is_done_angry`,
  `looking_after_someone_does_not_stop_the_worry`,
  `what_you_did_in_the_night_is_felt_as_shame`, and
  `and_as_being_afraid_of_what_they_will_think`. Nothing was added to make them
  fire, and no reader was written for this experiment.

#### 11. Three things found that were not looked for

**A man counting the family's food feels nothing about it.** On the baseline, the
actor reads his own `count_supplies` as `neutral` at weight **0.00** — not a weak
reading but no reading at all, because no interpretation rule matches the event
unless the shelf is nearly bare. So does every witness. Today, carrying an
intention is the only way this act means anything to anybody.

**Nobody eats.** Across 50 mornings, **zero** portions were eaten, so the count
never falls and the one rule that would read a pantry-check never fires.

**`restore_standing` never led a pantry-check.** It is one of the four wants that
proposes the act, and in 50 mornings it led none of the 153. The three that did
are `find_out`, `get_food` and `guard_supplies`. The want the accumulated-history
experiment identified as the one that changes when a reading flips is the one
that never reaches this act in practice.

#### 12. What was predicted, and what was wrong

Twelve numbered predictions were committed before any arm ran. Eleven passed. One
— P9, that an unread intention would leave the actor with *less* than no
intention — has its mechanism confirmed from the code and its effect unobserved,
for the reason in section 6.

Two riskier claims were also committed. One was right and one was wrong, and the
wrong one matters:

- **Wrong:** "the strongest arm should be `assert_authority`". It was
  `took_what_was_not_mine`, 80 against 48.
- **Right, and predicted for the right reason:** "`took_what_was_not_mine` may
  outdo it despite being a worse fit, because it has two readers rather than one
  — meaning the size of an intention's effect is decided by how many rules happen
  to name it, not by what it means."

Full detail in `results.md`.

#### 13. What this does and does not license

It does **not** show that the action model is too weak. The opposite: one
physical act carried six different reasons without a single change to the action
model, the event model, the deliberator or any rule, and the reason it carried
reached behaviour. The apparent action bottleneck is not the action layer being
unable to represent the distinction.

It does **not** show that a want should map to an intention. The experiment
supplied the intention by hand precisely so that this question stayed open, and
the hook remains a hook.

It **does** show where the loss is: the reason an act expresses is representable,
transportable and consequential, and the system is built to read almost none of
it. Six intentions, three of them dead letters, none readable by interpretation,
belief, memory or attention, and no word at all for wanting to eat.

#### 14. Classification

| | |
|---|---|
| **ACTION REPRESENTATION** | **PROVEN.** One physical act carried six distinct intentions with the act, its event and its consequence unchanged. 153 acts, 918 arms, no production change |
| **INTENTION PRESERVATION** | **PROVEN.** The intention survives execution onto the event in 6 of 6, is recovered by the actor at weight 1.00, and is kept in memory. Removing it restores the baseline exactly in 50 of 50 mornings |
| **SEMANTIC PROPAGATION** | **PROVEN, AND NARROW.** It reaches appraisal and propagates from there to emotion, motivation and later action. It reaches nothing else: 0 interpretation rules, 0 belief nudges, 0 memory scalers, 0 attention weights, and 3 of the 6 intentions have no reader at all |
| **WITNESS INTENTION INFERENCE** | **UNPROVEN**, and correctly so. The witness gets nothing in 7 of 7 arms, which is knowledge locality working. But they are also given no observable evidence — no manner, no duration, no repetition, no gaze — from which anyone could infer anything |
| **BEHAVIOURAL CONSEQUENCE** | **PROVEN.** 189 of 918 arms changed a decision, 20.6 %, by a traced path through a shipped rule. Exactly 0 of 459 arms with an unread intention changed anything |

#### 15. Verdict

### MODIFY

Not the action layer. The action layer answered the question it was asked: the
same physical act carried six different reasons, and the reasons reached
behaviour. Rebuilding it would be rebuilding the part that worked.

What needs modifying is the reading side, in the order the loss boundaries fall:
the **vocabulary**, which has no word for half of what a person here can want;
and the **readers**, of which there is one kind, covering half the intentions
that do exist. The accumulated-history experiment ended on "what act does
`restore_standing` have that `find_out` does not? Today, none." This experiment
narrows that: the act is not the problem. `restore_standing` and `find_out` can
already do the same thing for different reasons and have it matter. What they
lack is anyone to read the difference.

No mechanism is added here, and nothing is proceeding to a larger experiment.
Stopping for review, as instructed.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter SameActExperimentTests`. The fixture takes
about four minutes; it runs roughly 1,100 whole mornings. Suite: PENDING.

---

## measurements.md

### Same act, different reason: measurements

Generated by `SameActExperimentTests` on the primary baseline. One physical act is held fixed and only the intention carried onto the event it becomes is varied, through the `IntentOfAct` hook, which is unset in every baseline arm. The random stream is forked per person and minute from the seed, so it cannot shift between arms.

#### M1. Four wants, one physical act

Every proposal in the shipped file that asks for `check_pantry`, and then the first real act in a live morning led by each of those wants.

| Proposal | Want | Fit |
|---|---|---|
| `see_what_there_is` | `get_food` | 0.400 |
| `count_it_properly` | `guard_supplies` | 0.500 |
| `look_at_the_shelf_yourself` | `find_out` | 0.600 |
| `check_it_yourself` | `restore_standing` | 0.450 |

| Want | Found | Who | Minute | Urgency | Chosen | Margin | Resolution | Commitment | Target | Destination | What was considered |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `get_food` | yes | mara | m9 | 0.534 | check_pantry | 0.242 | Clear | none | none | none | check_pantry +0.567; search_room +0.325; wait +0.152; go_to->hallway -0.002 |
| `guard_supplies` | yes | leo | m9 | 0.433 | check_pantry | 0.278 | Clear | none | none | none | check_pantry +0.531; search_room +0.253; wait +0.231; go_to->hallway -0.119 |
| `find_out` | yes | daniel | m1 | 0.808 | check_pantry | 0.146 | Clear | none | none | none | check_pantry +1.102; search_room +0.955; observe:elena +0.545; observe:mara +0.545 |
| `restore_standing` | **no** | - | - | - | - | - | - | - | - | - | led no pantry-check in 50 mornings |

And the event each act became:

| Want | Event action | Actor | Target | Topic | Valence | Intent | Witnesses | Summary |
|---|---|---|---|---|---|---|---|---|
| `get_food` | `count_supplies` | mara | none | supplies | neutral | **none** | daniel, elena, leo | Mara opens the pantry and counts what is left: 2. |
| `guard_supplies` | `count_supplies` | leo | none | supplies | neutral | **none** | daniel, elena, mara | Leo opens the pantry and counts what is left: 2. |
| `find_out` | `count_supplies` | daniel | none | supplies | neutral | **none** | elena, leo, mara | Daniel opens the pantry and counts what is left: 2. |

**153 real pantry-checks across 50 mornings, led by 3 different wants. Distinct event shapes, ignoring valence and the sentence: 1.**

Valence is `bad` when the count is low and `neutral` otherwise, so it reports the state of the shelf and not the reason for looking. The sentence is about the shelf for the same reason. Nothing on the event says which want sent him.

#### M2. One act, every intention the vocabulary has

**The act.** daniel checks the pantry, decided at m1 and finishing at m4, led by `find_out` at urgency 0.808. Condition `daniel_ate_it`, seed 1. Witnessed by elena, leo, mara.

Every arm is the same morning with the same seed, and the arms are identical up to m4 by construction: the intention is attached at the moment the act becomes an event, and nothing before that can see it.

##### The event

| Arm | Event | Action | Target | Topic | Valence | **Intent on the event** | Same sentence |
|---|---|---|---|---|---|---|---|
| baseline: no hook | yes | count_supplies | none | supplies | neutral | `none` | yes |
| control: hook set, carries nothing | yes | count_supplies | none | supplies | neutral | `none` | yes |
| intent `assert_authority` | yes | count_supplies | none | supplies | neutral | `assert_authority` | yes |
| intent `prevent_argument` | yes | count_supplies | none | supplies | neutral | `prevent_argument` | yes |
| intent `protect` | yes | count_supplies | none | supplies | neutral | `protect` | yes |
| intent `share_information` | yes | count_supplies | none | supplies | neutral | `share_information` | yes |
| intent `take_responsibility` | yes | count_supplies | none | supplies | neutral | `take_responsibility` | yes |
| intent `took_what_was_not_mine` | yes | count_supplies | none | supplies | neutral | `took_what_was_not_mine` | yes |

##### What the actor made of his own act

| Arm | Access | Interpretation | Kept as | Appraisal rules that fired | Belief nudges |
|---|---|---|---|---|---|
| baseline: no hook | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none |
| control: hook set, carries nothing | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none |
| intent `assert_authority` | was there and saw it | knew their own intention: assert_authority (weight 1.00, runner-up none) | assert_authority, salience 0.670, felt anger | anger 0.61 [asserting_yourself_is_done_angry] | none |
| intent `prevent_argument` | was there and saw it | knew their own intention: prevent_argument (weight 1.00, runner-up none) | prevent_argument, salience 0.150, felt none | nothing | none |
| intent `protect` | was there and saw it | knew their own intention: protect (weight 1.00, runner-up none) | protect, salience 0.539, felt anxiety | anxiety 0.46 [looking_after_someone_does_not_stop_the_worry] | none |
| intent `share_information` | was there and saw it | knew their own intention: share_information (weight 1.00, runner-up none) | share_information, salience 0.150, felt none | nothing | none |
| intent `take_responsibility` | was there and saw it | knew their own intention: take_responsibility (weight 1.00, runner-up none) | take_responsibility, salience 0.150, felt none | nothing | none |
| intent `took_what_was_not_mine` | was there and saw it | knew their own intention: took_what_was_not_mine (weight 1.00, runner-up none) | took_what_was_not_mine, salience 0.747, felt fear | fear 0.47 [and_as_being_afraid_of_what_they_will_think]; shame 0.44 [what_you_did_in_the_night_is_felt_as_shame] | none |

##### And what came of it

| Arm | Feelings at the end of the morning | Next decision after the act | Wants at that decision |
|---|---|---|---|
| baseline: no hook | none | m4 daniel search_room for find_out | find_out 0.757, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, restore_standing 0.392, keep_peace 0.349 |
| control: hook set, carries nothing | none | m4 daniel search_room for find_out | find_out 0.757, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, restore_standing 0.392, keep_peace 0.349 |
| intent `assert_authority` | none | m4 daniel search_room for find_out | find_out 0.757, restore_standing 0.615, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, keep_peace 0.349 |
| intent `prevent_argument` | none | m4 daniel search_room for find_out | find_out 0.757, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, restore_standing 0.392, keep_peace 0.349 |
| intent `protect` | none | m4 daniel search_room for find_out | find_out 0.757, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, keep_peace 0.418, restore_standing 0.392 |
| intent `share_information` | none | m4 daniel search_room for find_out | find_out 0.757, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, restore_standing 0.392, keep_peace 0.349 |
| intent `take_responsibility` | none | m4 daniel search_room for find_out | find_out 0.757, get_food 0.568, avoid_exposure 0.542, look_after:mara 0.500, guard_supplies 0.426, restore_standing 0.392, keep_peace 0.349 |
| intent `took_what_was_not_mine` | none | m4 daniel search_room for find_out | avoid_exposure 0.812, find_out 0.757, restore_standing 0.569, get_food 0.568, look_after:mara 0.500, guard_supplies 0.426, keep_peace 0.349 |

Beliefs at the end of the morning, for the same person:

| Arm | Beliefs |
|---|---|
| baseline: no hook | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| control: hook set, carries nothing | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| intent `assert_authority` | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| intent `prevent_argument` | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| intent `protect` | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| intent `share_information` | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| intent `take_responsibility` | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |
| intent `took_what_was_not_mine` | answerable_for(daniel,missing_can) 0.900, more_knowledgeable(leo,survival) 0.580, role_claim(daniel,leads_family) 0.800, supplies_short 0.663, tendency(leo,does_not_respect_me) 0.561, tendency(leo,treats_me_like_a_child) 0.120 |

**The intention survived execution onto the event in 6 of 6 arms.** The two control arms carry none, as they should.

#### M3. Taking the intention away

The null condition has to reproduce the existing behaviour exactly, or nothing else here means anything. Two ways of having no intention, over every condition and every seed, against the morning with no hook at all.

| Condition | Seed | Hook set, carries nothing | Hook set, then removed |
|---|---|---|---|
| `daniel_ate_it` | 1 | identical | identical |
| `daniel_hid_it` | 1 | identical | identical |
| `mara_ate_it` | 1 | identical | identical |
| `elena_fed_mara` | 1 | identical | identical |
| `miscount` | 1 | identical | identical |

**50 of 50 mornings identical on both.** Every act, every margin to full precision, every resolution. Only the first seed of each condition is listed; a difference anywhere would have been listed and would have failed the test.

#### M4. The witness

The actor is daniel; the witness is elena. Neither is told anything by the experiment. The witness responds only to what the existing perception system hands them.

| Arm | Witness access | Witness interpretation | Kept as | Appraisal | Belief nudges | Their next decision |
|---|---|---|---|---|---|---|
| baseline | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |
| intent `assert_authority` | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |
| intent `prevent_argument` | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |
| intent `protect` | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |
| intent `share_information` | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |
| intent `take_responsibility` | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |
| intent `took_what_was_not_mine` | was there and saw it | read it as neutral (0.00) (weight 0.00, runner-up none) | neutral, salience 0.150, felt none | nothing | none | m9 elena check_pantry for get_food |

**Distinct witness readings across 7 arms: 1.**

The witness sees the act. What the actor took himself to be doing is carried on the event, and the interpreter hands somebody their own intention only when the event's actor is the perceiver themselves. So the witness reads the act by rule, as they would anybody else's. That is knowledge locality working, not a defect. Whether they are given any evidence from which to infer more is a separate question, taken up in the report.

#### M5. Who reads an intention

Counted from the loaded rules, not from memory. A rule *reads* a label if it is keyed on it (`when.meanings`) or scales on a memory of it (`kind: memory`, `name: <label>`).

| Intention | Interpretation rules | Belief nudges | Appraisal rules | Memory scalers anywhere | Total readers |
|---|---|---|---|---|---|
| `assert_authority` | 0 | 0 | 1 (`asserting_yourself_is_done_angry` -> anger) | 0 | **1** |
| `prevent_argument` | 0 | 0 | 0 | 0 | **0** |
| `protect` | 0 | 0 | 1 (`looking_after_someone_does_not_stop_the_worry` -> anxiety) | 0 | **1** |
| `share_information` | 0 | 0 | 0 | 0 | **0** |
| `take_responsibility` | 0 | 0 | 0 | 0 | **0** |
| `took_what_was_not_mine` | 0 | 0 | 2 (`what_you_did_in_the_night_is_felt_as_shame` -> shame, `and_as_being_afraid_of_what_they_will_think` -> fear) | 0 | **2** |

For comparison, the same count for the meanings a person can read in somebody *else*:

| Meaning | Interpretation | Belief nudges | Appraisal | Memory scalers | Total |
|---|---|---|---|---|---|
| `challenge` | 3 | 0 | 2 | 0 | **2** |
| `concern` | 6 | 0 | 2 | 2 | **4** |
| `deception` | 0 | 0 | 0 | 0 | **0** |
| `disrespect` | 4 | 2 | 5 | 0 | **7** |
| `neutral` | 0 | 0 | 0 | 0 | **0** |
| `reassurance` | 1 | 0 | 0 | 0 | **0** |
| `request` | 0 | 0 | 0 | 0 | **0** |
| `support` | 3 | 1 | 3 | 0 | **4** |
| `threat` | 4 | 0 | 2 | 2 | **4** |

(The interpretation column means something different in the two tables: for a meaning it is the number of rules that can *produce* it, since no rule is keyed on a meaning to produce another. For an intention it is the number keyed on it, which is what a reader is.)

Every meaning any memory scaler names, anywhere in the rules: `concern`, `threat`. None is an intention, so a stored intention is invisible to every memory scaler there is.

##### Attention

Perception scales the feeling by how readily this person notices that kind of meaning. Here is what the cast carries:

| Person | Attention weights | Any weight on an intention |
|---|---|---|
| daniel | challenge 1.200, disrespect 1.300 | no |
| elena | challenge 1.300, deception 1.150, threat 1.200 | no |
| leo | concern 1.100, deception 1.250 | no |
| mara | disrespect 1.200, threat 1.400 | no |

##### Can the three wants the brief names say what they intend

The vocabulary has 6 intentions: `assert_authority`, `prevent_argument`, `protect`, `share_information`, `take_responsibility`, `took_what_was_not_mine`. It has 7 wants: `avoid_exposure`, `find_out`, `get_food`, `guard_supplies`, `keep_peace`, `look_after`, `restore_standing`. They are separate sets and nothing maps between them.

| Want | An intention that says what it intends | Readers that intention has |
|---|---|---|
| `find_out` | none exact; `take_responsibility` is the shipped precedent (backstory p02 is a search carried out under it) but means something else | 0 |
| `restore_standing` | `assert_authority`, paired with it in the shipped backstory (b06) | 1 |
| `get_food` | **none**; no label in the vocabulary says wanting to eat | n/a |

**Of the three motivations the brief names, one is expressible, one is approximable, and one cannot be said at all.**

#### M6. An intention does not only add

The interpreter hands an actor their own intention *instead of* running the rules, not as well as. So carrying an intention can leave a person with **less** than carrying none: whatever reading the rules would have given is gone, and so is the memory of it. Whether that costs anything depends on whether the rules had anything to say about the act, which for a pantry-check depends on how much food is left.

##### A count that found enough

The fixed act: daniel at m4 in `daniel_ate_it` seed 1, event valence `neutral`.

| Arm | Actor's reading | Rules consulted | Feelings from this act | Meaning kept in memory | Against baseline |
|---|---|---|---|---|---|
| baseline, no intention | neutral (witnessed) | yes | nothing | `neutral` | - |
| `assert_authority` | assert_authority (own intention) | no | anger 0.61 [asserting_yourself_is_done_angry] | `assert_authority` | **more** |
| `prevent_argument` | prevent_argument (own intention) | no | nothing | `prevent_argument` | same |
| `protect` | protect (own intention) | no | anxiety 0.46 [looking_after_someone_does_not_stop_the_worry] | `protect` | **more** |
| `share_information` | share_information (own intention) | no | nothing | `share_information` | same |
| `take_responsibility` | take_responsibility (own intention) | no | nothing | `take_responsibility` | same |
| `took_what_was_not_mine` | took_what_was_not_mine (own intention) | no | fear 0.47 [and_as_being_afraid_of_what_they_will_think]; shame 0.44 [what_you_did_in_the_night_is_felt_as_shame] | `took_what_was_not_mine` | **more** |

**Arms that left him with less than no intention at all: 0 of 6. Arms that gave him something the baseline did not: 3.**

##### A count that found the shelf nearly empty

No pantry-check in 50 mornings found the shelf low enough for the event to carry a bad valence, so the displacing case does not arise here. The morning starts with 2 portions and the rule that would have been displaced (`bad_news_reads_as_a_problem`) needs the count to fall to 1 or below, which takes somebody eating: 0 portions were eaten in the whole set, across 0 of 50 mornings, and no check followed one.

So the displacement is real in the code and costs nothing here, because for this act the rules had nothing to say in the first place. **On the baseline a man counting the family's food reads it as `neutral` at weight 0.00: no interpretation rule matches `count_supplies` at all unless the shelf is nearly bare.** Carrying an intention is the only way this act means anything to anybody.

The meaning kept in memory is the intention in every intention arm, which is the representation working. Whether that memory is ever read again is M5's question, and the answer there is no.

#### M7. Whether it ever reaches behaviour

Every real pantry-check in the design conditions, under every intention, against its own baseline. A divergence is the first decision anywhere in the house that differs.

| Condition | Seed | Who | m | Led by | Intention | Feelings differ at the end | A decision differs | First divergence |
|---|---|---|---|---|---|---|---|---|
| `daniel_ate_it` | 1 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_ate_it` | 1 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_ate_it` | 2 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 2 | leo | 4 | `find_out` | `protect` | no | **yes** | m10 leo: search_room for find_out -> wait for guard_supplies |
| `daniel_ate_it` | 2 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `daniel_ate_it` | 2 | mara | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m25 mara: wait for guard_supplies -> go_to->back_room for find_out |
| `daniel_ate_it` | 3 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `daniel_ate_it` | 3 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `daniel_ate_it` | 3 | mara | 12 | `get_food` | `assert_authority` | **yes** | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `daniel_ate_it` | 3 | mara | 12 | `get_food` | `protect` | no | **yes** | m12 mara: search_room for find_out -> wait for keep_peace |
| `daniel_ate_it` | 3 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `daniel_ate_it` | 4 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 4 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `daniel_ate_it` | 4 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `daniel_ate_it` | 4 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 4 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 5 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `daniel_ate_it` | 5 | leo | 4 | `find_out` | `protect` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `daniel_ate_it` | 5 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m9 leo: wait for guard_supplies -> search_room for find_out |
| `daniel_ate_it` | 5 | mara | 12 | `get_food` | `protect` | no | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 5 | mara | 12 | `get_food` | `took_what_was_not_mine` | no | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 6 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `daniel_ate_it` | 6 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 6 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 7 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_ate_it` | 7 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_ate_it` | 8 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `daniel_ate_it` | 8 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 8 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_ate_it` | 9 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `daniel_ate_it` | 9 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `daniel_ate_it` | 9 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `daniel_ate_it` | 10 | daniel | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m24 daniel: go_to->bathroom for find_out -> wait for guard_supplies |
| `daniel_ate_it` | 10 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `daniel_hid_it` | 1 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_hid_it` | 1 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_hid_it` | 2 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 2 | leo | 4 | `find_out` | `protect` | no | **yes** | m10 leo: search_room for find_out -> wait for guard_supplies |
| `daniel_hid_it` | 2 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `daniel_hid_it` | 2 | mara | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m25 mara: wait for guard_supplies -> go_to->back_room for find_out |
| `daniel_hid_it` | 3 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `daniel_hid_it` | 3 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `daniel_hid_it` | 3 | mara | 12 | `get_food` | `assert_authority` | **yes** | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `daniel_hid_it` | 3 | mara | 12 | `get_food` | `protect` | no | **yes** | m12 mara: search_room for find_out -> wait for keep_peace |
| `daniel_hid_it` | 3 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `daniel_hid_it` | 4 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 4 | leo | 4 | `find_out` | `protect` | **yes** | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `daniel_hid_it` | 4 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `daniel_hid_it` | 4 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 4 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 5 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `daniel_hid_it` | 5 | leo | 4 | `find_out` | `protect` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `daniel_hid_it` | 5 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m9 leo: wait for guard_supplies -> search_room for find_out |
| `daniel_hid_it` | 5 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 5 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 6 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `daniel_hid_it` | 6 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 6 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 7 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_hid_it` | 7 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `daniel_hid_it` | 8 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `daniel_hid_it` | 8 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 8 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `daniel_hid_it` | 9 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `daniel_hid_it` | 9 | leo | 4 | `find_out` | `protect` | **yes** | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `daniel_hid_it` | 9 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `daniel_hid_it` | 10 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 1 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `mara_ate_it` | 1 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `mara_ate_it` | 1 | elena | 23 | `get_food` | `protect` | **yes** | **yes** | m28 elena: wait for keep_peace -> comfort:mara for look_after:mara |
| `mara_ate_it` | 1 | elena | 23 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m23 elena: wait for keep_peace -> go_to->living_room for avoid_exposure |
| `mara_ate_it` | 2 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `mara_ate_it` | 2 | leo | 4 | `find_out` | `protect` | no | **yes** | m10 leo: search_room for find_out -> wait for guard_supplies |
| `mara_ate_it` | 2 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `mara_ate_it` | 2 | elena | 24 | `get_food` | `assert_authority` | **yes** | **yes** | m24 elena: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 2 | elena | 24 | `get_food` | `protect` | no | **yes** | m24 elena: wait for guard_supplies -> wait for keep_peace |
| `mara_ate_it` | 2 | elena | 24 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m24 elena: wait for guard_supplies -> search_room for restore_standing |
| `mara_ate_it` | 3 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `mara_ate_it` | 3 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 3 | elena | 24 | `get_food` | `assert_authority` | **yes** | **yes** | m42 elena: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 3 | elena | 24 | `get_food` | `protect` | **yes** | **yes** | m24 elena: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 3 | elena | 24 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m24 elena: search_room for find_out -> go_to->hallway for avoid_exposure |
| `mara_ate_it` | 4 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `mara_ate_it` | 4 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `mara_ate_it` | 4 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `mara_ate_it` | 4 | mara | 4 | `get_food` | `protect` | no | **yes** | m27 mara: search_room for find_out -> wait for guard_supplies |
| `mara_ate_it` | 4 | mara | 4 | `get_food` | `took_what_was_not_mine` | no | **yes** | m33 mara: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 4 | elena | 25 | `get_food` | `assert_authority` | **yes** | **yes** | m25 elena: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 4 | elena | 25 | `get_food` | `protect` | **yes** | **yes** | m25 elena: comfort:mara for look_after:mara -> wait for keep_peace |
| `mara_ate_it` | 4 | elena | 25 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m25 elena: comfort:mara for look_after:mara -> go_to->hallway for avoid_exposure |
| `mara_ate_it` | 5 | daniel | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m24 daniel: go_to->bathroom for find_out -> wait for guard_supplies |
| `mara_ate_it` | 5 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 5 | leo | 4 | `find_out` | `protect` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 5 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m9 leo: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 5 | elena | 23 | `get_food` | `assert_authority` | no | **yes** | m23 elena: wait for keep_peace -> search_room for find_out |
| `mara_ate_it` | 5 | elena | 23 | `get_food` | `protect` | **yes** | **yes** | m28 elena: wait for keep_peace -> comfort:mara for look_after:mara |
| `mara_ate_it` | 5 | elena | 23 | `get_food` | `took_what_was_not_mine` | no | **yes** | m23 elena: wait for keep_peace -> search_room for restore_standing |
| `mara_ate_it` | 6 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 6 | mara | 4 | `get_food` | `protect` | no | **yes** | m9 mara: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 6 | elena | 25 | `get_food` | `assert_authority` | **yes** | **yes** | m25 elena: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 6 | elena | 25 | `get_food` | `protect` | **yes** | **yes** | m25 elena: wait for guard_supplies -> wait for keep_peace |
| `mara_ate_it` | 6 | elena | 25 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m25 elena: wait for guard_supplies -> search_room for restore_standing |
| `mara_ate_it` | 7 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `mara_ate_it` | 7 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `mara_ate_it` | 7 | elena | 24 | `get_food` | `assert_authority` | no | **yes** | m42 elena: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 7 | elena | 24 | `get_food` | `protect` | no | **yes** | m24 elena: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 7 | elena | 24 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m24 elena: search_room for find_out -> go_to->living_room for avoid_exposure |
| `mara_ate_it` | 8 | leo | 12 | `guard_supplies` | `assert_authority` | **yes** | **yes** | m22 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 8 | leo | 12 | `guard_supplies` | `protect` | **yes** | **yes** | m22 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 8 | leo | 12 | `guard_supplies` | `took_what_was_not_mine` | **yes** | **yes** | m12 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 8 | elena | 25 | `get_food` | `assert_authority` | no | **yes** | m25 elena: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 8 | elena | 25 | `get_food` | `protect` | **yes** | **yes** | m25 elena: comfort:mara for look_after:mara -> wait for keep_peace |
| `mara_ate_it` | 8 | elena | 25 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m25 elena: comfort:mara for look_after:mara -> go_to->hallway for avoid_exposure |
| `mara_ate_it` | 9 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `mara_ate_it` | 9 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `mara_ate_it` | 9 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 9 | elena | 24 | `get_food` | `assert_authority` | **yes** | **yes** | m24 elena: wait for guard_supplies -> search_room for find_out |
| `mara_ate_it` | 9 | elena | 24 | `get_food` | `protect` | no | **yes** | m24 elena: wait for guard_supplies -> wait for keep_peace |
| `mara_ate_it` | 9 | elena | 24 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m24 elena: wait for guard_supplies -> search_room for restore_standing |
| `mara_ate_it` | 10 | daniel | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m24 daniel: go_to->bathroom for find_out -> wait for guard_supplies |
| `mara_ate_it` | 10 | leo | 12 | `guard_supplies` | `took_what_was_not_mine` | no | **yes** | m12 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `mara_ate_it` | 10 | elena | 25 | `get_food` | `protect` | **yes** | **yes** | m25 elena: search_room for find_out -> wait for keep_peace |
| `mara_ate_it` | 10 | elena | 25 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m25 elena: search_room for find_out -> search_room for restore_standing |
| `elena_fed_mara` | 1 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `elena_fed_mara` | 1 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `elena_fed_mara` | 2 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 2 | leo | 4 | `find_out` | `protect` | no | **yes** | m10 leo: search_room for find_out -> wait for guard_supplies |
| `elena_fed_mara` | 2 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `elena_fed_mara` | 2 | mara | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m25 mara: wait for guard_supplies -> go_to->back_room for find_out |
| `elena_fed_mara` | 3 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `elena_fed_mara` | 3 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `elena_fed_mara` | 3 | mara | 12 | `get_food` | `assert_authority` | no | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `elena_fed_mara` | 3 | mara | 12 | `get_food` | `protect` | no | **yes** | m12 mara: search_room for find_out -> wait for keep_peace |
| `elena_fed_mara` | 3 | mara | 12 | `get_food` | `took_what_was_not_mine` | no | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `elena_fed_mara` | 4 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 4 | leo | 4 | `find_out` | `protect` | **yes** | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `elena_fed_mara` | 4 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `elena_fed_mara` | 4 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 4 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 5 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `elena_fed_mara` | 5 | leo | 4 | `find_out` | `protect` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `elena_fed_mara` | 5 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m9 leo: wait for guard_supplies -> search_room for find_out |
| `elena_fed_mara` | 5 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 5 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 6 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `elena_fed_mara` | 6 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 6 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 7 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `elena_fed_mara` | 7 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `elena_fed_mara` | 8 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `elena_fed_mara` | 8 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 8 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 leo: search_room for find_out -> comfort:mara for look_after:mara |
| `elena_fed_mara` | 9 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `elena_fed_mara` | 9 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `elena_fed_mara` | 9 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `elena_fed_mara` | 10 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `miscount` | 1 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `miscount` | 1 | leo | 4 | `find_out` | `took_what_was_not_mine` | no | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `miscount` | 2 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `miscount` | 2 | leo | 4 | `find_out` | `protect` | no | **yes** | m10 leo: search_room for find_out -> wait for guard_supplies |
| `miscount` | 2 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `miscount` | 2 | mara | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m25 mara: wait for guard_supplies -> go_to->back_room for find_out |
| `miscount` | 3 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `miscount` | 3 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `miscount` | 3 | mara | 12 | `get_food` | `assert_authority` | no | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `miscount` | 3 | mara | 12 | `get_food` | `protect` | no | **yes** | m12 mara: search_room for find_out -> wait for keep_peace |
| `miscount` | 3 | mara | 12 | `get_food` | `took_what_was_not_mine` | no | **yes** | m25 mara: wait for guard_supplies -> search_room for find_out |
| `miscount` | 4 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: wait for keep_peace -> comfort:mara for look_after:mara |
| `miscount` | 4 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `miscount` | 4 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: wait for keep_peace -> search_room for find_out |
| `miscount` | 4 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 4 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 5 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `miscount` | 5 | leo | 4 | `find_out` | `protect` | no | **yes** | m4 leo: search_room for find_out -> wait for keep_peace |
| `miscount` | 5 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m9 leo: wait for guard_supplies -> search_room for find_out |
| `miscount` | 5 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 5 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 6 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `miscount` | 6 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 6 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 7 | leo | 4 | `find_out` | `assert_authority` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `miscount` | 7 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:daniel for look_after:daniel -> search_room for find_out |
| `miscount` | 8 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |
| `miscount` | 8 | mara | 12 | `get_food` | `protect` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 8 | mara | 12 | `get_food` | `took_what_was_not_mine` | **yes** | **yes** | m12 elena: check_pantry for get_food -> comfort:mara for look_after:mara |
| `miscount` | 9 | leo | 4 | `find_out` | `assert_authority` | no | **yes** | m4 leo: comfort:mara for look_after:mara -> comfort:daniel for look_after:daniel |
| `miscount` | 9 | leo | 4 | `find_out` | `protect` | no | **yes** | m9 leo: search_room for find_out -> wait for guard_supplies |
| `miscount` | 9 | leo | 4 | `find_out` | `took_what_was_not_mine` | **yes** | **yes** | m4 leo: comfort:mara for look_after:mara -> search_room for find_out |
| `miscount` | 10 | leo | 12 | `guard_supplies` | `protect` | no | **yes** | m12 leo: search_room for find_out -> wait for keep_peace |

Rows where nothing moved at all are left out. **153 real pantry-checks x 6 intentions = 918 arms.**

| | Count | Share |
|---|---|---|
| Arms where the actor's feelings still differed at the end of the morning | 103 | 11.2 % |
| Arms where any decision in the house differed | 189 | 20.6 % |

Feelings are read at the end of the morning, so a `no` there does not mean nothing was ever felt: a feeling can move a decision and then fade before the morning ends, which is why the second column is larger than the first for every intention that has a reader.

| Intention | Appraisal readers | Arms where feelings still differed at the end | Arms where a decision moved |
|---|---|---|---|
| `assert_authority` | 1 | 15 of 153 | 48 of 153 |
| `prevent_argument` | 0 | 0 of 153 | 0 of 153 |
| `protect` | 1 | 26 of 153 | 61 of 153 |
| `share_information` | 0 | 0 of 153 | 0 of 153 |
| `take_responsibility` | 0 | 0 of 153 | 0 of 153 |
| `took_what_was_not_mine` | 2 | 62 of 153 | 80 of 153 |

---

## predictions.md

### Same act, different reason: predictions

Written **before the experiment was run**, and kept as written.

The question: when one physical act is performed for different reasons, can the
current simulation keep the difference, and does anything read it?

The brief separates three questions and this file keeps them separate:

1. **Representation** — can the same act carry different intentions at all?
2. **Propagation** — does that difference survive act → event → perception → appraisal/memory/belief?
3. **Behaviour** — can it end in a different act?

A failure at 3 is not a failure at 1. A failure at 2 is the important one.

#### What was read before predicting, and what was not

Predictions are worthless if they are written after the answer. So, exactly:

- **Read before predicting:** the rule files and the perception code, to find
  which rules are *keyed* on which labels. This is static structure, not a
  result, and the brief asks for predictions "refined before execution if the
  actual existing code requires a more precise formulation". Where a prediction
  follows from that reading rather than from a guess, it is marked **(from the
  rules)** and claims no credit.
- **Not read, not run, not known:** any measurement. No arm of this experiment
  had been run when this file was written. Everything about what actually
  happens — which emotions land and how hard, what the witness makes of it,
  whether any later decision moves, whether removing the intent restores the
  baseline byte for byte — was open.

#### The reader map, from the rules

Six intentions exist in the shipped vocabulary (`self_meanings`):
`take_responsibility`, `share_information`, `protect`, `assert_authority`,
`prevent_argument`, `took_what_was_not_mine`.

Searching every rule file for rules keyed on any of them finds **four, all in
appraisal**:

| Intention | Rules that read it |
|---|---|
| `assert_authority` | `asserting_yourself_is_done_angry` -> anger |
| `protect` | `looking_after_someone_does_not_stop_the_worry` -> anxiety |
| `took_what_was_not_mine` | `what_you_did_in_the_night_is_felt_as_shame` -> shame; `and_as_being_afraid_of_what_they_will_think` -> fear |
| `take_responsibility` | **none** |
| `share_information` | **none** |
| `prevent_argument` | **none** |

No interpretation rule, no belief nudge, no motivation rule and no decision rule
is keyed on any intention. Memory scalers can match a stored meaning by name,
but the only two names used anywhere are `concern` and `threat`, which no
intention can ever equal.

#### The vocabulary question, asked in advance

The brief names three motivation contexts — `find_out`, `restore_standing`,
`get_food` — and asks whether the existing labels can say what each one intends.
**(from the rules)** The answer available before running anything:

| Want | Nearest shipped intention | Is it the same thing? |
|---|---|---|
| `restore_standing` | `assert_authority` | **Yes.** The shipped backstory already pairs them (b06) |
| `find_out` | `take_responsibility` | **No, but it is the shipped precedent.** p02 is Daniel searching the house with intent `take_responsibility`, glossed "searching the house is what someone in charge does". That is the intention of a man in charge, not the intention of a man who wants to know |
| `get_food` | **nothing** | No label in the vocabulary says "I want food". `took_what_was_not_mine` is about having done wrong, not about wanting to eat |

So one of the brief's three intentions is inexpressible and a second is only
approximately expressible. Rather than invent labels, the experiment runs **all
six shipped intentions** on the one act, plus a no-intent baseline, and reports
the vocabulary gap as a result in its own right.

#### Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | The same physical act, by the same person, at the same minute, in the same world, can be executed under each of the six intentions | any arm fails to produce the act, or the acts differ physically |
| P2 | With the hook unset, and with the hook set but returning null, the whole morning is identical to the baseline — every act, every margin, every event | any difference |
| P3 | The intention survives execution and is carried on the `WorldEvent` | the event's intent is null or wrong |
| P4 | The actor recovers the intention: his reading of his own act **is** the intention, at weight 1.00, with no rule consulted | he reads it by rule instead |
| P5 | A witness in the same room receives **nothing** that distinguishes the arms: same access, same reading, same weight, same everything | the witness differs between arms |
| P6 | **(from the rules)** Exactly one existing reader consumes the intention — appraisal — and it consumes only three of the six | a second kind of reader turns out to consume it, or appraisal does not |
| P7 | Where a reader exists (`assert_authority`, `protect`, `took_what_was_not_mine`), the actor's emotions after his own act differ from the baseline | the emotions are identical |
| P8 | Where no reader exists (`take_responsibility`, `share_information`, `prevent_argument`), everything downstream is identical **except the string kept in memory** | something else moves |
| P9 | Setting an intention does not only add. It **replaces** the reading the rules would have given, so an arm with an unread intention can end up with *less* than the baseline: the baseline's rule-derived meaning, and any memory of it, is gone | the rule-derived reading survives alongside the intention |
| P10 | The stored intention is invisible to every memory scaler, because the only meanings any scaler names are `concern` and `threat` | a scaler reads it |
| P11 | At least one arm changes a later decision in the same morning | no arm moves any decision |
| P12 | No new action, want, rule, number or production mechanism is needed to run any of this | one is needed |

**Committed in advance, and riskier:**

- The strongest arm should be `assert_authority`, because it is the only
  intention whose reader produces an emotion aimed at somebody — and on this act
  the event has **no target**, so the anger should land aimed at nobody. Whether
  an untargeted anger then does anything is unknown to me.
- `took_what_was_not_mine` has two readers, so it may produce more feeling than
  `assert_authority` despite being a worse fit for a man counting his own
  pantry. If so, the size of an intention's effect is decided by how many rules
  happen to name it, not by what it means. I expect this.
- P9 is the prediction I would most like to be wrong about, and the one I think
  is most likely to be right.

**What would make this a major result:** P7 and P11 both holding, by a traceable
path. **What would reproduce the known bottleneck:** P5, P6 and P8 holding
together — the distinction exists on the event, and almost nothing in the
simulation is built to read it.

---

## results.md

### Same act, different reason: results against the predictions

The measurements are in `measurements.md`, generated by `SameActExperimentTests`.
This is the assessment against `predictions.md`, which was written and committed
before any arm was run.

#### Runs

| | |
|---|---|
| Physical act | `check_pantry`, which four shipped proposals ask for |
| Conditions | the five design conditions, seeds 1 to 10, so 50 mornings |
| Real pantry-checks found | **153**, led by three different wants |
| Intentions | all **6** in the shipped vocabulary, plus two no-intention controls |
| Arms | 918 (153 checks x 6 intentions), plus 150 control mornings |
| What varied | the intention carried onto the event the act becomes, and nothing else |
| Randomness | forked per person and minute from the seed; the intention is attached when the act finishes, so it cannot shift a stream that was already drawn |
| New code or rules | **none**. No change to `Fallow.Core`, no change to any data file. The `IntentOfAct` hook already existed and stays unset by default |

#### Predictions

| # | Prediction | Result | Evidence |
|---|---|---|---|
| P1 | The same act can be executed under each of the six intentions | **PASS** | M2: the act, its event, its target, its valence and its sentence are identical in all six arms |
| P2 | Hook unset, and hook set but returning null, reproduce the baseline exactly | **PASS** | M3: 50 of 50 mornings identical on both, every act and every margin to full precision |
| P3 | The intention survives execution onto the `WorldEvent` | **PASS** | M2: 6 of 6 |
| P4 | The actor recovers it, at weight 1.00, with no rule consulted | **PASS** | M2: "knew their own intention", weight 1.00, no runner-up, no contributions |
| P5 | A witness receives nothing that distinguishes the arms | **PASS** | M4: 1 distinct witness reading across 7 arms — same access, same reading, same weight, same appraisal, same next decision |
| P6 | Exactly one kind of reader consumes it — appraisal — and only for three of the six | **PASS** | M5: 0 interpretation rules, 0 belief nudges, 0 memory scalers; 4 appraisal rules across 3 intentions |
| P7 | Where a reader exists, the actor's emotions differ from the baseline | **PASS** | M2: anger 0.61, anxiety 0.46, fear 0.47 + shame 0.44 where the baseline felt nothing |
| P8 | Where no reader exists, everything downstream is identical except the string in memory | **PASS** | M7: `take_responsibility`, `share_information` and `prevent_argument` moved a feeling or a decision in **0 of 153** cases each |
| P9 | An intention *replaces* the rule reading, so an unread one can leave the actor with less | **MECHANISM CONFIRMED, EFFECT NOT OBSERVED** | The interpreter returns before consulting a rule (M2: "rules consulted: no"). But in 50 mornings it never cost anything, because no interpretation rule matches `count_supplies` unless the shelf is nearly bare, and it never was. See below |
| P10 | The stored intention is invisible to every memory scaler | **PASS** | M5: the only meanings any scaler names anywhere are `concern` and `threat` |
| P11 | At least one arm changes a later decision | **PASS** | M7: 189 of 918 arms, 20.6 % |
| P12 | No new action, want, rule, number or mechanism is needed | **PASS** | no file under `Scripts/Core` or `Data` was touched |

**The two riskier claims committed in advance:**

| Claim | Result |
|---|---|
| The strongest arm should be `assert_authority`, the only intention whose reader aims a feeling at somebody | **FALSIFIED.** `took_what_was_not_mine` is the strongest by a wide margin: 80 of 153 against 48 |
| ...and on this act the event has no target, so that anger should land aimed at nobody | **HELD.** `$target` on a targetless event resolves to null, and the anger is filed against nobody |
| `took_what_was_not_mine` may outdo it despite being a worse fit, because it has two readers rather than one — meaning the size of an intention's effect is set by how many rules happen to name it, not by what it means | **HELD, and it is the finding of the experiment.** The ordering is exactly the reader count: 0 readers -> 0 arms moved, 1 reader -> 48 and 61, 2 readers -> 80 |

#### The central numbers

| Intention | Appraisal readers | Feelings still differ at the end | A decision moved |
|---|---|---|---|
| `prevent_argument` | 0 | 0 of 153 | **0 of 153** |
| `share_information` | 0 | 0 of 153 | **0 of 153** |
| `take_responsibility` | 0 | 0 of 153 | **0 of 153** |
| `assert_authority` | 1 | 15 of 153 | 48 of 153 |
| `protect` | 1 | 26 of 153 | 61 of 153 |
| `took_what_was_not_mine` | 2 | 62 of 153 | 80 of 153 |

Feelings are read at the end of the morning, so the first column understates: a
feeling can move a decision and then fade. That is why the second column is
larger than the first for every intention that has a reader at all.

**The separation is total.** Every intention with a reader moved something in a
third to a half of cases. Every intention without one moved nothing, ever, in
153 cases each. There is no intermediate behaviour, no leakage, no partial
credit. Whether a reason matters is decided entirely by whether somebody once
wrote an appraisal rule naming it.

#### Where the causal chain stops

The chain runs: want -> act -> **intention carried onto the event** -> the actor
reads his own act as that intention, at weight 1.00 -> appraisal -> emotion ->
motivation -> a later act. It is unbroken, and it is traceable end to end.

It stops at exactly one place: **appraisal is the only door.** Interpretation
does not read an intention, no belief moves because of one, no memory scaler can
see one, and no attention weight can be placed on one, because attention weights
are validated against the meanings a person reads in somebody *else*.

#### Three things the measurements found that were not asked for

**A man counting the family's food feels nothing about it.** On the baseline the
actor reads his own `count_supplies` as `neutral` at weight **0.00** — not a weak
reading, no reading at all, because no interpretation rule matches the event
unless the shelf is nearly bare. So does every witness. Carrying an intention is
currently the only way this act means anything to anybody.

**Nobody eats.** Across 50 mornings, **0 portions** were eaten. The count never
falls, so `bad_news_reads_as_a_problem` never fires on a pantry-check, which is
why P9's displacement never costs anything here. This is not an artefact of the
experiment; it is the baseline.

**`restore_standing` never led a pantry-check.** It is one of the four wants that
proposes the act, and one of the three the brief names, and in 50 mornings it led
none of the 153. The three that did are `find_out`, `get_food` and
`guard_supplies`.

