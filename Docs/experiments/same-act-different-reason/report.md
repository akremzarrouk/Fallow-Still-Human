# Same act, different reason

*What, if anything, distinguishes the same physical act when it is chosen for
different reasons?*

## 1. Why this was asked

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

## 2. What was and was not done

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

## 3. Design

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

## 4. The three questions, kept apart

| | Question | Answer |
|---|---|---|
| 1 | **Representation** — can the same act carry different intentions? | **Yes.** 6 of 6, with the act, its event, its target, its valence and its sentence unchanged |
| 2 | **Propagation** — does the distinction survive to perception, appraisal, memory, belief? | **Partly.** It reaches the actor's own reading intact, and appraisal reads it. Nothing else does |
| 3 | **Behaviour** — can different intentions end in different acts? | **Yes.** 189 of 918 arms, 20.6 %, traceably |

A failure at 3 would not have been a failure at 1. As it happens there is no
failure at any of the three; the failure is narrower and more specific, and it is
at 2.

## 5. The causal trace, with every boundary marked

### A. `assert_authority` — an intention with a reader

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

### B. `take_responsibility` — an intention with no reader

Identical to A as far as memory, and then:

```
appraisal: no rule is keyed on take_responsibility
    | DISCARDED. Everything downstream is the baseline
memory: kept as `take_responsibility`
    | PRESERVED as a string, and never read again by anything
later act: 0 of 153
```

### C. The witness

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

## 6. Where the architecture drops causal information

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

## 7. What the numbers say

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

## 8. Actor against witness

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

## 9. The vocabulary cannot say what the brief asked

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

## 10. No cheating

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

## 11. Three things found that were not looked for

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

## 12. What was predicted, and what was wrong

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

## 13. What this does and does not license

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

## 14. Classification

| | |
|---|---|
| **ACTION REPRESENTATION** | **PROVEN.** One physical act carried six distinct intentions with the act, its event and its consequence unchanged. 153 acts, 918 arms, no production change |
| **INTENTION PRESERVATION** | **PROVEN.** The intention survives execution onto the event in 6 of 6, is recovered by the actor at weight 1.00, and is kept in memory. Removing it restores the baseline exactly in 50 of 50 mornings |
| **SEMANTIC PROPAGATION** | **PROVEN, AND NARROW.** It reaches appraisal and propagates from there to emotion, motivation and later action. It reaches nothing else: 0 interpretation rules, 0 belief nudges, 0 memory scalers, 0 attention weights, and 3 of the 6 intentions have no reader at all |
| **WITNESS INTENTION INFERENCE** | **UNPROVEN**, and correctly so. The witness gets nothing in 7 of 7 arms, which is knowledge locality working. But they are also given no observable evidence — no manner, no duration, no repetition, no gaze — from which anyone could infer anything |
| **BEHAVIOURAL CONSEQUENCE** | **PROVEN.** 189 of 918 arms changed a decision, 20.6 %, by a traced path through a shipped rule. Exactly 0 of 459 arms with an unread intention changed anything |

## 15. Verdict

# MODIFY

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
