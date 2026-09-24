# reason-semantics: all documents

Merged by `merge-slice-docs.py` from the 5 Markdown files in `Docs/experiments/reason-semantics/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)
- [`annotation/protocol.md`](#annotationprotocolmd)

---

## report.md

### Reason semantics: what a simulated reason has to contain

*What must a simulated reason contain so that the system can tell genuinely
different causal explanations apart, without silently turning conditions into
weights, circumstances into hidden gates, or competing reasons into arbitrary
score arithmetic?*

#### 1. The answer, first

**A reason needs more than weighted evidence, and less than the full vocabulary
tested here.** Five distinctions turned out to be **required**. Each is required
in two senses:
- every representation that lacks it gets its cases wrong;
- blind readers draw it the way it was declared.

| Required | What goes wrong without it | Readers |
|---|---|---|
| **An identity for each reason**, independent of rules, wording and grouping | one reason written twice doubles its strength (S changes 55.5 % of choices); two reasons on the same facts collapse into one | 10 of 10 items; kappa 0.851 |
| **Whether a fact is a condition or a push** | identical authored rules cannot be told apart. A condition written as a weight is wrong in all 10,935 cells, and changes 50 % of choices | all three minimal pairs discriminated, 6 of 6 each way for both beliefs; kappa 0.862 |
| **The circumstance a reason needs**, in a vocabulary that can name the person concerned and whether anyone is watching, **kept apart from a situation that only makes a reason stronger** | the shipped gate cannot say "the person I protect is here" or "nobody is watching", and is wrong in 4,374 cells per case | 7 of 7 circumstance slots and the push-or-gate pair |
| **A reference from a reason that only strengthens another to the one it strengthens** | copying the other reason's gate works until that reason is edited; then it is wrong in 1,458 cells | 5 of 6 |
| **A way to form no intention** | the only candidate forms with nothing behind it (5,470 cells of an innocent "theft") | 4 of 4 items; kappa 0.808 |

Two relations are **not needed as relations**. Other elements already carry them:
- **exclusive**: reasons that never apply together are carried by their
  circumstances;
- **opposed**: a reason against, or a fact holding one reason back, is carried
  by parts and direction.

Readers recognise both (6 of 6 each), and no representation needs a separate
relation to get them right.

Two things the design declared were **not reproduced by readers**:
- **"Alternative": only the stronger of two reasons operates.** Readers read
  the only such case, doing it quietly against doing it openly, as "never
  together" (3) or "opposed" (2), and only one as "one or the other". Four of
  six read "whether others will know it was them" as a situation the reason
  needs. In the causal-route experiment, readers offered only "both" or "one or
  the other" chose "one or the other" for this same pair, 6 of 6. Offered "never
  together" and "opposed" as well, five of six chose those instead. **In neither
  experiment did any reader explain an exclusion by one reason being stronger.**
  They pointed to the situation (whether others will know, who is present) or
  to the act (quietly or openly).
- **A hold-back that touches only its own reason.** Six of six agree fear holds
  back stepping in. Four of six say the same fear *pushes* making sure someone
  who can help knows. The vocabulary can say that (a fact may play a different
  part in each reason). The case, as declared, said the fear played no part.

**What remains a modelling choice** is set out in section 10. In short:
- whether a condition also carries strength;
- how independent reasons combine;
- how far a hold-back can go;
- the viability threshold;
- how much a reinforcement adds;
- graded conditions;
- whether exclusion-by-strength exists at all.

This experiment tested none of them against alternatives. Every one of them
changes conclusions.

**Behaviourally**, this is the first experiment in the series whose distinctions
reach real decisions. Reading the one declared precondition as a condition
changes **99 of 1,028 real pantry decisions** and forms no intention in **272
live cells**. Most of that comes from a choice the declaration exposed: the
author's weight on the belief was also doing the work of a strength.

**Recommendation: MODIFY** (section 13), by the criteria committed before the
run. Nothing is to be implemented yet.

#### 2. What was run

| | |
|---|---|
| Frozen | `intentions.json` `61e6412e...b099d92`, `causal-routes.json` `781b776d...c37828a`, `held-out-people.json` `0b3f4bc9...4ff4131`, `reason-semantics.json` `5ffe17fe...eedc7638`: each checked at the start and the end, **unchanged** |
| Production | **nothing changed**: not `Fallow.Core`, the shipped rules, character data, S1 scoring, the selector, motivations, candidates, actions, beliefs, emotions, memories, nor the causal-route representation |
| Committed first | in `e5a5131`, before the fixture or any reviewer: the vocabulary; five situations; 28 cases in six families, each as authored rules and as declared meaning; the reading rule of each representation; 31 checks and 7 negative controls; the annotation items, key and protocol; an independent Python model of every analytic count |
| Evaluation | 28 cases x 2,187 profiles x 5 situations = **306,180 cells** per representation |
| Frozen file | 30,618 cells |
| Real mornings | 50 baseline mornings: 25,823 live cells, 1,028 real pantry decisions |
| Annotation | 6 blind language-model reviewers, 21 items, 69 fact slots |
| Fixture | `ReasonSemanticsExperimentTests`, **9 of 9 pass**, about 20 minutes. No randomness |

**S is the shipped selector.** Rebuilt from the authored rules, it differs from
`IntentionSelector.Form` in 0 of 306,180 synthetic and 0 of 30,618 frozen-file
cells, every weight to the bit.

**Every analytic count equals the prediction model's.** The fixture and the
committed Python model agree exactly: all 186 check counts, the ablations, the
changed choices, and the frozen file.

Two situation features are experiment-only:
- whether the person the want concerns is present;
- whether anyone is watching.

No psychological variable was added.

#### 3. The vocabulary and the representations

| Term | Meaning |
|---|---|
| fact | a level read from the person, or a feature of the situation |
| reason | a declared explanation, with an identity, of why facts lead toward or away from an intention |
| part | **push** (the more, the stronger), **hold-back** (the more, the weaker; it can cancel its reason, not reverse it), **condition** (must hold for the reason to apply at all; not a strength) |
| circumstance | a feature of the situation a reason needs; a **situational push** makes it stronger without being needed |
| direction | toward the intention, or against it |
| relation | independent (default), alternative, reinforces, exclusive |

The representations form a lattice, so that each distinction can be traced to
the element that makes it:

| | Identity | Parts, direction | Circumstances | Relations | Forms when |
|---|---|---|---|---|---|
| **S** shipped selector | no | no | shipped gates | no | a rule weighs more than zero |
| **A** reasons + weights | yes | no | shipped gates | no | any compatible candidate |
| **B-parts** | yes | yes | shipped gates | no | support > 0 |
| **B-circ** | yes | no | yes | no | support > 0 |
| **B** | yes | yes | yes | no | support > 0 |
| **C** | yes | yes | yes | yes | support > 0 |

**What cannot be held degrades by a fixed rule:**
- a condition becomes the weight its author wrote;
- a circumstance becomes the nearest shipped gate;
- a relation becomes independence;
- a reinforcement becomes a copied gate.

**What the representational results are, and are not.** A vocabulary that cannot
hold a distinction fails the checks that need it; that is close to true by
construction. C passes everything because it reads every declaration. What is
not by construction:
- **reducibility:** whether one element can do another's work;
- **reach:** how far each failure spreads, in cells and in choices;
- **legibility:** whether readers draw the distinction;
- **behaviour:** what happens on the real file and in real mornings.

#### 4. Representational results

Checks passed, of 31, over 10,935 cells each (sections 1 and 2 of the
measurements):

| Family | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|
| A restatement (3) | 0 | 3 | 3 | 3 | 3 | 3 |
| B shared facts (3) | 0 | 2 | 2 | 3 | 3 | 3 |
| C condition or push (6) | 2 | 2 | 6 | 2 | 6 | 6 |
| D circumstance (6) | 2 | 2 | 2 | 6 | 6 | 6 |
| E relation (7) | 3 | 3 | 4 | 4 | 5 | 7 |
| F no viable cause (6) | 2 | 2 | 5 | 5 | 6 | 6 |
| **All (31)** | **9 (29.0 %)** | **14 (45.2 %)** | **22 (71.0 %)** | **23 (74.2 %)** | **29 (93.5 %)** | **31 (100 %)** |
| Negative controls (7) | 7 | 7 | 7 | 7 | 7 | 7 |

In percentage points, against S:
- reason identity adds **16.1** (A);
- parts add **25.8** on top of A (B-parts);
- circumstances add **29.0** on top of A (B-circ);
- both together add **48.4** on top of A (B);
- relations add the last **6.5** (C).

**What each element buys, check by check:**

| Element | Checks it alone turns from fail to pass | Cells it corrects |
|---|---|---|
| Reason identity (S to A) | A.1, A.2, A.3, B.1, B.2 | 10,935, 10,935, 7,290; the critical pair told apart in 10,935 |
| Parts (A to B-parts) | C.3 to C.6, E.7, F.1, F.4 | 10,935 per condition; 4,860 (local hold-back); 5,470; 5,060 |
| Circumstances (A to B-circ) | B.3, D.2 to D.4, D.6, E.3, F.2 | 4,374 per case; 8,748 (E.3) |
| Viability (support > 0) | F.3, F.4 | 3,640; 5,060 |
| Relations (B to C) | E.2, E.5 | 10,935; 1,458 |

**Two failures show why the parts must be typed rather than inferred from signs.**
- **S passes the local hold-back (E.7) and fails the reason against (E.6).** Its
  discard drops any rule weighing zero or less. That happens to floor a
  cancelled reason, and also throws away a reason against.
- **A does the opposite.** It adds every reason, so a reason against lowers
  support (E.6 passes), and so does a reversed hold-back, which then lowers the
  other reason's contribution (E.7 fails, 4,860 cells).

Only a representation that knows which negative amount is a hold-back and which
is a reason against gets both.

**The negative controls change nothing, anywhere.** None of the following
changes a single outcome, support or explanation, in any case, under any
representation:
- moving an unread trait;
- rewriting every text;
- reversing rule order;
- renaming rules;
- renaming reasons;
- toggling an unread situation feature;
- adding an unread belief.

#### 5. Semantic and legibility evidence

Six fresh language-model subagents saw 21 items in plain words. They saw no
vocabulary and no key, in rotated order, with reasons swapped for half of them.
**Agreement shows legibility, not truth.**

| Question | Majority matches the key | Fleiss' kappa |
|---|---|---|
| Q1 same reason or different | 10 of 10 | **0.851** |
| Q2 how two different reasons relate | 6 of 8 | **0.630** |
| Q3 the part each fact plays | 65 of 68 slots | **0.862** |
| Q5 could this person form it at all | 4 of 4 | **0.808** |

**The minimal pairs are the core of H2 and H3.** In each pair the authored
rules are identical, and only the words differ.

| Fact | Worded as a push | Worded as needed |
|---|---|---|
| believing it was theirs to answer for | pushes, 6 of 6 | must hold, 6 of 6 |
| believing they lead the family | pushes, 6 of 6 | must hold, 6 of 6 |
| whether anyone is watching | strengthens, 4 of 6 | needed, 6 of 6 |

**Readers follow the wording, not the fact.** In the causal-route experiment,
readers read "answerable for the missing can" as a precondition, 6 of 6, from a
text that said the intention was "reachable only by somebody who believes". That
could have been the belief's nature or the wording. Here the same belief was
read as a push when the text said "the more certain they are, the more readily",
and as a precondition when it said "only someone who believes".

**Where readers departed from the key** (section 6 of the measurements):

| Item | Declared | Readers | Author's coding of their Q4 |
|---|---|---|---|
| `quiet_or_open` relation | one or the other | never together 3, opposed 2, one or the other 1 | the difference is whether others will know, which decides which reason applies |
| `quiet_or_open`, "whether others will know it was them" | a consequence | a situation the reason needs, 4 of 6, in both reasons | the same |
| `fear_holds_back`, fear in "make sure someone who can help knows" | no part | pushes 4, unclear 2 | fear that stops a person stepping in sends them for help |
| `fear_holds_back` relation | both add | both add 3, one or the other 3 | split on whether a frightened person does both |
| `critical` | different | different 4, same 2 | the two who said "same" explained both reasons by the same two facts |

#### 6. Which relations are needed

| Relation | Checks | Passes without a relation? | Readers | Status |
|---|---|---|---|---|
| independent | E.1 | yes, everyone | both add: 6 of 6 (`independent`, `seen`), 4 of 6 (`critical`) | the default |
| exclusive | E.3 | **yes: B-circ and B, through circumstances** | never together, 6 of 6 | **REDUNDANT** |
| opposed | E.6, E.7 | **yes: B-parts and B, through parts and direction** | opposed, 6 of 6 | **REDUNDANT** |
| reinforcing | E.4, E.5 | E.4 yes, **but only through a copied gate**: with the copy removed, every representation but C fails. E.5 (after the reinforced reason is edited): only C | one strengthens the other, 5 of 6 | **REQUIRED**, as a reference to the other reason |
| alternative | E.2 | no: only C | one or the other, 1 of 6 | **UNSUPPORTED** |

So the relation vocabulary a reason needs is **one reference**: "this reason
operates only where that one does". Nothing more was supported.

"Alternative" may still exist. But the one case built for it was read as two
reasons whose applicability depends on a situation the vocabulary has no word
for: whether the act will become known. Declared that way, it would have been
exclusive by circumstance, and B would have passed it. Only the strongest
operating is arithmetic readers did not ask for.

#### 7. No viable cause

Readers say the intention should not be reachable:
- without the needed belief (6 of 6);
- without the needed person present (5 of 6);
- with nothing pushing (6 of 6).

They say it should still form from a weak but real reason (6 of 6).

**The ablations show three separate sources, needing three separate things:**

| Source | What handles it | Evidence |
|---|---|---|
| a failed circumstance | **compatibility, already**, once the circumstance can be said | B-Sel0 passes F.2 |
| a failed condition | applicability: a reason whose condition fails cannot make its intention viable | B-Sel1 passes F.1; B-Sel0 fails it (5,470) |
| nothing pushing, or pushed down by a stronger reason against | a positive-support rule | only Sel-2 passes F.3 (3,640) and F.4 (5,060) |

The shipped selector's discard gets F.3 right by accident, and **fails F.6**:
whether it forms an intention depends on whether two reasons were written as
one rule or two (5,060 cells).

**Viability does not move the compatibility stage onto the person.** Candidates
are still admitted by circumstances alone. What changes is that selection may
answer "none".

#### 8. Behaviour

**On the synthetic cases**, choices that differ from C's (which computes every
declaration), of 306,180 cells:

| S | A | B-parts | B-circ | B |
|---|---|---|---|---|
| 50,815 (16.6 %) | 45,830 (15.0 %) | 20,530 (6.7 %) | 16,280 (5.3 %) | **4,740 (1.5 %)**, all in E2 and E4b |

One representational failure changes no choice. A's reversed hold-back is wrong
in 4,860 cells of E6, but the rival never falls between the two supports. The
sweep's value rotation and belief sets are tied to the profile index, so some
combinations never occur. **Representational correctness and behavioural
change are different things here.**

**On the frozen file** (30,618 cells), read with the causal-route declarations
and nothing new:

| | No intention | Differs from A |
|---|---|---|
| B-parts, B and C (the enabler as a condition) | 1,094 | **4,074 (13.3 %)** |
| B-parts+w (a condition that keeps its weight) | 1,094 | 1,185 (3.9 %) |
| B-circ | 0 | 0 |

**Most of the 4,074 cells are believers, not innocents.**
- **2,889 believers:** reading the belief as a condition drops the author's
  0.60 weight, so they stop forming the theft. 1,944 take responsibility,
  627 protect and 311 prevent an argument; 7 are ties.
- **1,185 innocents:** 91 had formed the theft over a rival, and 1,094 formed
  it alone.

The frozen declaration said "the belief is the condition, and honesty, fairness
and shame are what act on it". Taken at its word, the belief stops being a
strength, and that choice moves more than twice as many conclusions as the
condition itself.

**In real mornings:**

| | B-parts | B-parts+w |
|---|---|---|
| Live cells differing from A, of 25,823 | **1,388 (5.4 %)**: `get_food` 745, `avoid_exposure` 643 | 312 (1.2 %) |
| Live cells forming no intention | **272** | 272 |
| Real pantry decisions differing from A, of 1,028 | **99 (9.6 %)** | 0 |

The 99 are Daniel in the mornings where he ate the can, matched at other
people's `get_food` pantry-checks. With the belief a condition only, he takes
responsibility instead of owning a theft. **This is the first time in the series
that a change of representation reaches a real decision, and it comes from a
modelling choice, not from the representation.** The same condition with its
weight kept changes no real decision.

#### 9. Provenance

- **PV1, reconstruction: holds for every representation.** From the
  explanation alone, the winner's support is rebuilt within 1e-9, and every
  amount is coefficient x level of a named fact from a named rule. That holds
  for all 2,755,620 outcomes (9 representations x 306,180 cells). Every "none"
  says why each candidate did not form, for example:
  - "condition `belief:answerable_for` does not hold";
  - "circumstance `target_present` does not hold";
  - "support 0.000 is not positive".
- **PV2, the whole chain** (intention, reason, part, fact, circumstance, rule):
  **not met by any representation as implemented.** The explanations name:
  - the reason;
  - each fact with its level, coefficient, amount and rule;
  - conditions and situational pushes;
  - the condition or circumstance that failed.

  They do not name each fact's part (a hold-back shows only as a negative
  amount), a reason's direction, or the circumstance under which an applicable
  reason applied. B and C compute with all of these, so the full chain is
  available to them; the fixture did not emit it.

  The fixture's own PV2 table, written before the run, claimed otherwise. Its
  text was corrected after an audit, and nothing was recomputed (results,
  "what was changed"). S, A, B-parts and B-circ could not emit the chain at all:
  they do not hold the parts or the circumstances.

#### 10. What a reason has to contain, and what remains a choice

**Established here** (necessary for the declared behaviour, and drawn the same
way by blind readers):

1. **An identity**: which reason a statement belongs to, independent of rules,
   order, wording and grouping.
2. **For each fact, its part**: a push, a hold-back, or a condition. A fact can
   play a different part in different reasons (readers: fear holds back one
   reason and pushes another).
3. **Its circumstance**, in words that can name the person concerned and
   whether anyone watches, separate from any situation that only makes it
   stronger.
4. **Where it depends on another reason, a reference to that reason**, not a
   copy of its conditions.
5. **At the level of selection, the possibility of no intention**, with its
   reason stated: a failed circumstance, a failed condition, or no positive
   support.

**Not needed as separate relations:**
- exclusive (circumstances carry it);
- opposed (parts and direction carry it).

**Still a modelling choice.** Every one of these changes conclusions, and none
was tested against an alternative:

| Choice | How much it moves |
|---|---|
| Whether a condition also carries strength | 4,074 against 1,185 frozen-file cells; 99 against 0 real decisions |
| How independent reasons combine (here, they add) | untested; every co-active case depends on it |
| How far a hold-back reaches (here, it can cancel its reason, never reverse it) | E.7: 4,860 cells between the two readings |
| The viability threshold (here, support above zero) | F.3 and F.4: 3,640 and 5,060 cells |
| How much a reinforcement adds (here, its own push, only where the other applies) | only presence was tested |
| Graded conditions | only beliefs, which are held or not, were tested; a graded fact as a condition needs a threshold |
| Whether "only the stronger of two reasons operates" exists at all | no reader, in two experiments, explained an exclusion that way |
| Whether any of it is how people are | untested |

#### 11. Limitations

- **The reviewers are language models**, not people, and share training. Their
  agreement is weaker evidence than independent people would give.
- **The author declared every case, wrote the items, and wrote the key.**
- **One case per relation, and one or two per part.** "Alternative" rests on a
  single case, and the verdict leans on it.
- **The minimal pairs were in the same list.** They were 8 to 13 items apart
  and unmarked, but contrast may still help readers.
- **The sweep's attributes are correlated.** Values and beliefs follow the
  profile index, so some combinations never occur. That can hide behavioural
  effects (E6).
- **Watching is synthetic**; no production data carries it. Circumstances were
  not applied to the frozen file, because no new declarations were made about
  frozen rules.
- **Real mornings have 10 seeds per variant.** One character in one variant
  produces all 99 changed real decisions.
- **The checks are formula-light but not formula-free.** Adding for independent
  reasons, cancelling for hold-backs and "above zero" for viability are
  declared, not tested.
- **PV2 was not implemented**, as section 9 says.

#### 12. Classification

##### Representational

| | |
|---|---|
| **PROVEN** | S is the shipped selector (0 of 336,798 cells). The families pass as predicted in all 186 counts; S 9, A 14, B-parts 22, B-circ 23, B 29, C 31 of 31. Identity alone passes restatement and the critical pair. Parts are needed for conditions (10,935 cells per case otherwise) and for telling a hold-back from a reason against (S and A each get exactly one of the two). Circumstances are needed whenever the shipped gate cannot say them (4,374 cells per case). Exclusive is carried by circumstances, and opposed by parts and direction. A reinforcement expressed by a copied gate passes only through the copy, and fails after one edit (1,458). No viable cause has three sources, needing compatibility, applicability and a positive-support rule, respectively; the shipped discard is split-dependent (5,060). Every negative control is 0. PV1 holds for all 2,755,620 outcomes |
| **PLAUSIBLE** | That B plus a reference relation is the smallest vocabulary expressing every required distinction. It is the smallest tested, on 28 synthetic cases |
| **UNPROVEN** | That "alternative" needs a relation at all. The combination rule, the hold-back floor and the viability threshold as declared |
| **FAILED** | S and A as representations of reasons. Copying as a substitute for reference. PV2 as implemented, for every representation |

##### Semantic and legibility

| | |
|---|---|
| **PROVEN** (as legibility, among language-model readers) | Identity (kappa 0.851, 10 of 10); condition against push, including all three minimal pairs (kappa 0.862, 65 of 68 slots); circumstance, including the person concerned and watching, and gate against situational push; reinforcement (5 of 6); exclusive and opposed (6 of 6 each); unreachability without a viable cause (4 of 4, kappa 0.808) |
| **PLAUSIBLE** | That readers read exclusion through circumstances, not strength (two experiments, few items). That a fact can hold back one reason and push another (4 of 6, one item) |
| **UNPROVEN** | That any of it holds for human readers |
| **FAILED** | "Alternative", as declared (1 of 6). "Whether others will know it was them" as a consequence (readers: a needed situation, 4 of 6). A hold-back with no part in the other reason (readers: it pushes, 4 of 6) |

##### Behavioural

| | |
|---|---|
| **PROVEN** | On the frozen file, the condition reading changes 4,074 cells (13.3 %), 2,889 of them because the belief loses its weight; keeping the weight changes 1,185. In real mornings it changes 99 of 1,028 real decisions and 1,388 of 25,823 live cells, and forms no intention in 272. On the synthetic cases, B differs from C in 1.5 % of choices, S in 16.6 % |
| **PLAUSIBLE** | That the real-decision changes generalize beyond one character in one morning variant |
| **UNPROVEN** | That any changed choice is better. Whether "no intention" is the right outcome, or what a person does then |
| **FAILED** | The prediction that no real decision would change (3.9) |

#### 13. Recommendation

### MODIFY

The criteria were committed with the predictions:
- **KEEP** needs one representation that (i) passes every check of every
  REQUIRED distinction, (ii) passes restatement, the negative controls and PV1,
  (iii) carries no UNSUPPORTED element, and (iv) passes no check only through a
  copy.
- **MODIFY** applies when one meets (i) and (ii) but none meets all four.
- **REBUILD** applies when none meets (i) and (ii).

Computed mechanically (section 7 of the measurements):
- **C meets (i), (ii) and (iv).** It fails (iii): it carries the alternative
  relation, which readers did not reproduce, and, through its parts, a hold-back
  declaration they contradicted.
- **B meets (ii) only.** It lacks the reinforcing reference, so it fails E.5
  and passes E.4 only through the copied gate. Its parts carry the
  contradicted hold-back declaration.
- Nothing but C meets (i).

**Not REBUILD.** Every required distinction was expressed within the existing
stages:
- circumstances admit candidates, reading only the situation;
- conditions and positive support decide viability at selection;
- negative controls, restatement and reconstruction all hold.

**What MODIFY means, concisely.** Before any implementation, the vocabulary
needs these changes:
1. Keep identity, parts, circumstances (able to name the person concerned and
   watching) and situational pushes.
2. Replace every relation with **one reference**: a reason that operates only
   where another does. Drop "alternative" until a case exists that readers read
   as one-or-other.
3. Let a fact have its own part in each reason, and declare it there.
4. Give selection a "no intention" outcome that states its reason.
5. **Decide**, as a modelling choice, whether a condition also carries strength.
   It moves more conclusions than anything else here.
6. Make explanations emit the full chain (part, direction, satisfied
   circumstance). The information exists; it was not written out.

This is a recommendation about vocabulary, not an implementation.

#### 14. The question, in plain language

*What exactly have we learned about what a causal reason needs to contain, and
what remains a modelling choice?*

**A reason has to say five things before anything is added up.**
1. **Which reason it is.** Otherwise the same reason written twice counts
   twice, and two different reasons that happen to share facts count once.
2. **For each fact it reads, what that fact does in it.** Does it push, hold
   back, or have to be true for the reason to apply at all? The same belief was
   read either way by every reader, depending only on the words. A weight
   cannot tell the two apart.
3. **The situation it needs**, in words that can name the person it is about
   and whether anyone is watching. Kept apart from that, a situation that only
   makes it easier.
4. **If it only works through another reason, which one.** It must point to
   that reason, not copy its conditions, or it goes wrong the first time the
   other reason changes.
5. **Whether it can leave the person with no intention at all.** Readers say
   someone with no applicable reason should not form one, even when nothing
   else is on offer.

**What we did not find:** any need for reasons to compete by strength. In two
experiments, no reader explained two reasons excluding each other by one being
stronger. They pointed to the situation or to the act instead. Nor did we need
separate relations for exclusion or opposition; circumstances and parts already
carry them.

**What remains a choice**, and has not been made:
- whether a condition also adds strength (it moves more conclusions than
  anything else here, including 99 real decisions);
- how reasons that act together combine;
- how far a hold-back can go;
- where "enough to form an intention" begins;
- how much a reinforcing reason adds;
- how graded facts become conditions.

None of this says how people are.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter ReasonSemanticsExperimentTests` (about 20
minutes), and the analytic predictions with
`python Docs/experiments/reason-semantics/prediction-model.py`.

**Suite: 448 tests, 446 pass, 2 fail.** The 2 failures are the regressions S1.4 left
failing, unchanged: the pacing gate, still 7 on Model A, and the emergent-moment fading
check. The 439 before this experiment, plus its nine, is exactly 448. The suite took 161
minutes, run from a copy of `run-tests.sh` with the timeout raised to four hours, because
the script's 7,200 seconds is now too short; the script was not changed.

This experiment's measurements, regenerated inside the suite, are identical to the
fixture's own runs, except for the provenance table corrected after the run. Every other
generated document regenerated with identical content, apart from the wall-clock seconds in
the decision-sensitivity results and one file that differed in line endings only.

---

## measurements.md

### Reason semantics: measurements

Generated by `ReasonSemanticsExperimentTests` from the committed cases, the frozen candidate rules, the causal-route declarations and the sweep, all hashed at the start and the end of the run. The predictions, the cases, the reading rules, the checks and the annotation protocol were committed before this fixture existed. There is no randomness anywhere.

#### 0. What is frozen, and whether S is the shipped selector

| File | sha256 at the start of this run | Expected | Match |
|---|---|---|---|
| `intentions.json` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | **yes** |
| `causal-routes.json` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | **yes** |
| `held-out-people.json` | `0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131` | `0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131` | **yes** |
| `reason-semantics.json` | `5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638` | `5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638` | **yes** |

S, rebuilt from the authored rules, differs from `IntentionSelector.Form` in **0** of 306,180 cells (28 cases x 10,935); winning weights not equal to the bit: **0**.

##### The evaluation space

| | |
|---|---|
| Profiles | 2,187 (the sweep: 7 traits at 0.150, 0.500, 0.850; values by rank; 4 belief sets) |
| Situations | s0 alone; s1 in company, the person concerned absent, unwatched; s2 in company, the person concerned present, unwatched; s3 in company, the person concerned absent, watched; s4 in company, the person concerned present, watched |
| Cells per case | 10,935 |
| Cases | 28 in six families: A 4, B 2, C 4, D 5, E 7, F 6 |
| Checks | 31, and 7 negative controls |

##### What each representation reads

| | Reason identity | Parts and direction | Declared circumstances | Relations | Forms when |
|---|---|---|---|---|---|
| **S** | no | no | shipped gates | no | a rule weighs more than zero |
| **A** | yes | no | shipped gates | no | any compatible candidate |
| **B-parts** | yes | yes | shipped gates | no | support > 0 |
| **B-circ** | yes | no | yes | no | support > 0 |
| **B** | yes | yes | yes | no | support > 0 |
| **C** | yes | yes | yes | yes | support > 0 |

#### 1. Representational results: the checks

Cells, of 10,935 per case, that violate each check. **0 is a pass.** For B.1, C.5 and C.6 the count is of cells where the two cases differ, and **0 is a failure**.

| Check | What must hold | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|---|
| A.1 | the reason written twice, word for word, changes nothing | **fail** (10,935) | pass | pass | pass | pass | pass |
| A.2 | the reason written a second time in other words changes nothing | **fail** (10,935) | pass | pass | pass | pass | pass |
| A.3 | the reason split into two rules changes nothing | **fail** (7,290) | pass | pass | pass | pass | pass |
| B.1 | two reasons on the same facts are not one reason written twice (the critical pair) | **fail** (0 differ) | pass (10,935 differ) | pass (10,935 differ) | pass (10,935 differ) | pass (10,935 differ) | pass (10,935 differ) |
| B.2 | two reasons identical in every declared respect are flagged for confirmation wherever both apply | **fail** (10,935) | pass | pass | pass | pass | pass |
| B.3 | a reason on shared facts that needs the person there applies exactly where they are | **fail** (4,374) | **fail** (4,374) | **fail** (4,374) | pass | pass | pass |
| C.1 | a belief as a push: the reason applies without it, and it adds its weight | pass | pass | pass | pass | pass | pass |
| C.2 | a second belief as a push | pass | pass | pass | pass | pass | pass |
| C.3 | the same belief as a condition: without it the reason does not apply; with it, it adds no strength | **fail** (10,935) | **fail** (10,935) | pass | **fail** (10,935) | pass | pass |
| C.4 | the second belief as a condition | **fail** (10,935) | **fail** (10,935) | pass | **fail** (10,935) | pass | pass |
| C.5 | identical authored rules with the belief in different parts are told apart | **fail** (0 differ) | **fail** (0 differ) | pass (10,935 differ) | **fail** (0 differ) | pass (10,935 differ) | pass (10,935 differ) |
| C.6 | the same, for the second belief | **fail** (0 differ) | **fail** (0 differ) | pass (10,935 differ) | **fail** (0 differ) | pass (10,935 differ) | pass (10,935 differ) |
| D.1 | a circumstance the shipped gate can say: anyone present | pass | pass | pass | pass | pass | pass |
| D.2 | only when nobody is watching | **fail** (4,374) | **fail** (4,374) | **fail** (4,374) | pass | pass | pass |
| D.3 | only when the person looked after is present | **fail** (4,374) | **fail** (4,374) | **fail** (4,374) | pass | pass | pass |
| D.4 | only when the person looked after is absent | **fail** (4,374) | **fail** (4,374) | **fail** (4,374) | pass | pass | pass |
| D.5 | where a circumstantial reason applies, it is exactly as strong as the same facts everywhere: the circumstance is not a weight | pass | pass | pass | pass | pass | pass |
| D.6 | a situation that makes a reason stronger, without being needed, adds exactly its push wherever it holds and gates nothing | **fail** (4,374) | **fail** (4,374) | **fail** (4,374) | pass | pass | pass |
| E.1 | independent reasons: each adds, wherever both push | pass | pass | pass | pass | pass | pass |
| E.2 | alternatives: adding the weaker never adds support, and one reason is named as operating | **fail** (10,935) | **fail** (10,935) | **fail** (10,935) | **fail** (10,935) | **fail** (10,935) | pass |
| E.3 | reasons whose circumstances exclude each other never both contribute | **fail** (8,748) | **fail** (8,748) | **fail** (8,748) | pass | pass | pass |
| E.4 | a reinforcing reason contributes exactly where the reason it strengthens applies | pass | pass | pass | pass | pass | pass |
| E.5 | the same after the reinforced reason was edited | **fail** (1,458) | **fail** (1,458) | **fail** (1,458) | **fail** (1,458) | **fail** (1,458) | pass |
| E.6 | a reason against lowers the intention's support wherever it has force | **fail** (10,935) | pass | pass | pass | pass | pass |
| E.7 | a fact that holds back one reason never lowers another, and never turns its reason against the intention | pass | **fail** (4,860) | pass | **fail** (4,860) | pass | pass |
| F.1 | no viable cause without the needed belief: the intention does not form | **fail** (5,470) | **fail** (5,470) | pass | **fail** (5,470) | pass | pass |
| F.2 | no viable cause without the needed circumstance | **fail** (4,374) | **fail** (4,374) | **fail** (4,374) | pass | pass | pass |
| F.3 | no viable cause when the only reason pushes with nothing | pass | **fail** (3,640) | pass | pass | pass | pass |
| F.4 | no viable cause when a stronger reason against outweighs the reason toward | **fail** (5,060) | **fail** (5,060) | pass | pass | pass | pass |
| F.5 | a weak but real reason still forms the intention | pass | pass | pass | pass | pass | pass |
| F.6 | whether an intention is viable does not depend on how reasons are split into rules | **fail** (5,060) | pass | pass | pass | pass | pass |

##### Checks passed, by family

| Family | Checks | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|---|
| A restatement | 3 | 0 (0.0 %) | 3 (100.0 %) | 3 (100.0 %) | 3 (100.0 %) | 3 (100.0 %) | 3 (100.0 %) |
| B shared facts, different reasons | 3 | 0 (0.0 %) | 2 (66.7 %) | 2 (66.7 %) | 3 (100.0 %) | 3 (100.0 %) | 3 (100.0 %) |
| C evidence or condition | 6 | 2 (33.3 %) | 2 (33.3 %) | 6 (100.0 %) | 2 (33.3 %) | 6 (100.0 %) | 6 (100.0 %) |
| D circumstance | 6 | 2 (33.3 %) | 2 (33.3 %) | 2 (33.3 %) | 6 (100.0 %) | 6 (100.0 %) | 6 (100.0 %) |
| E relation | 7 | 3 (42.9 %) | 3 (42.9 %) | 4 (57.1 %) | 4 (57.1 %) | 5 (71.4 %) | 7 (100.0 %) |
| F no viable cause | 6 | 2 (33.3 %) | 2 (33.3 %) | 5 (83.3 %) | 5 (83.3 %) | 6 (100.0 %) | 6 (100.0 %) |
| **All** | **31** | **9 (29.0 %)** | **14 (45.2 %)** | **22 (71.0 %)** | **23 (74.2 %)** | **29 (93.5 %)** | **31 (100.0 %)** |

Percentage points against S: A +16.1, B-parts +41.9, B-circ +45.2, B +64.5, C +71.0. Against A: B-parts +25.8, B-circ +29.0, B +48.4, C +54.8.

##### The viability ablations, family F

| Check | A-Sel2 | B-Sel0 | B-Sel1 | B (Sel-2) |
|---|---|---|---|---|
| F.1 no viable cause without the needed belief: the intention does not form | **fail** (5,470) | **fail** (5,470) | pass | pass |
| F.2 no viable cause without the needed circumstance | **fail** (4,374) | pass | pass | pass |
| F.3 no viable cause when the only reason pushes with nothing | pass | **fail** (3,640) | **fail** (3,640) | pass |
| F.4 no viable cause when a stronger reason against outweighs the reason toward | pass | **fail** (5,060) | **fail** (5,060) | pass |
| F.5 a weak but real reason still forms the intention | pass | pass | pass | pass |
| F.6 whether an intention is viable does not depend on how reasons are split into rules | pass | pass | pass | pass |

##### Checks passed only through a copied declaration

Each check whose case contains a copied gate or circumstance was rerun with every copy removed (the reinforcing reason given no gate of its own). A representation that passes with the copy and fails without it passed only through the copy.

| Check | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|
| E.4 | **only through the copy** | **only through the copy** | **only through the copy** | **only through the copy** | **only through the copy** | without the copy |
| E.5 | (fails) | (fails) | (fails) | (fails) | (fails) | without the copy |

##### Behaviour: choices that differ from C's

Cells, of 10,935, where the representation chooses a different outcome from C, which computes every declaration by construction. Every case but family F has the rival. In brackets, the share of cells.

| Case | S | A | B-parts | B-circ | B |
|---|---|---|---|---|---|
| A0 | 0 | 0 | 0 | 0 | 0 |
| A1 | 6,070 (55.5 %) | 0 | 0 | 0 | 0 |
| A2 | 6,070 (55.5 %) | 0 | 0 | 0 | 0 |
| A3 | 0 | 0 | 0 | 0 | 0 |
| B1 | 0 | 0 | 0 | 0 | 0 |
| B2 | 2,428 (22.2 %) | 2,428 (22.2 %) | 2,428 (22.2 %) | 0 | 0 |
| C1e | 0 | 0 | 0 | 0 | 0 |
| C1c | 5,465 (50.0 %) | 5,465 (50.0 %) | 0 | 5,465 (50.0 %) | 0 |
| C2e | 0 | 0 | 0 | 0 | 0 |
| C2c | 605 (5.5 %) | 605 (5.5 %) | 0 | 605 (5.5 %) | 0 |
| D1 | 0 | 0 | 0 | 0 | 0 |
| D2 | 974 (8.9 %) | 974 (8.9 %) | 974 (8.9 %) | 0 | 0 |
| D3 | 974 (8.9 %) | 974 (8.9 %) | 974 (8.9 %) | 0 | 0 |
| D4 | 974 (8.9 %) | 974 (8.9 %) | 974 (8.9 %) | 0 | 0 |
| D5 | 1,210 (11.1 %) | 1,210 (11.1 %) | 1,210 (11.1 %) | 0 | 0 |
| E1 | 0 | 0 | 0 | 0 | 0 |
| E2 | 4,255 (38.9 %) | 4,255 (38.9 %) | 4,255 (38.9 %) | 4,255 (38.9 %) | 4,255 (38.9 %) |
| E3 | 4,856 (44.4 %) | 4,856 (44.4 %) | 4,856 (44.4 %) | 0 | 0 |
| E4 | 0 | 0 | 0 | 0 | 0 |
| E4b | 485 (4.4 %) | 485 (4.4 %) | 485 (4.4 %) | 485 (4.4 %) | 485 (4.4 %) |
| E5 | 1,545 (14.1 %) | 0 | 0 | 0 | 0 |
| E6 | 0 | 0 | 0 | 0 | 0 |
| F1 | 5,470 (50.0 %) | 5,470 (50.0 %) | 0 | 5,470 (50.0 %) | 0 |
| F2 | 4,374 (40.0 %) | 4,374 (40.0 %) | 4,374 (40.0 %) | 0 | 0 |
| F3 | 0 | 3,640 (33.3 %) | 0 | 0 | 0 |
| F4 | 5,060 (46.3 %) | 5,060 (46.3 %) | 0 | 0 | 0 |
| F4m | 0 | 5,060 (46.3 %) | 0 | 0 | 0 |
| F5 | 0 | 0 | 0 | 0 | 0 |
| **All 28 cases** | **50,815 (16.6 %)** | **45,830 (15.0 %)** | **20,530 (6.7 %)** | **16,280 (5.3 %)** | **4,740 (1.5 %)** |

#### 2. Negative controls

Every case, under every representation. A change is any difference in the outcome, the focal intention's support or the representation's explanation, after undoing a declared renaming.

| Control | What changed | Cells compared, per representation | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|---|---|
| G.1 | moving a trait no reason reads (impulsive, to another level) changes nothing | 306,180 | 0 | 0 | 0 | 0 | 0 | 0 |
| G.2 | rewriting every note and every declared meaning changes nothing | 306,180 | 0 | 0 | 0 | 0 | 0 | 0 |
| G.3 | reversing the order of the rules changes nothing | 306,180 | 0 | 0 | 0 | 0 | 0 | 0 |
| G.4 | renaming every rule changes nothing | 306,180 | 0 | 0 | 0 | 0 | 0 | 0 |
| G.5 | renaming every reason key consistently changes nothing | 306,180 | 0 | 0 | 0 | 0 | 0 | 0 |
| G.6 | toggling a situation feature that no reason in the case reads (watched, or the person concerned being present) changes nothing | 428,652 | 0 | 0 | 0 | 0 | 0 | 0 |
| G.7 | adding, at full confidence, a belief that no reason in the case reads changes nothing | 306,180 | 0 | 0 | 0 | 0 | 0 | 0 |

#### 3. Provenance

**PV1, reconstruction**: from its explanation alone, the winner's support is rebuilt within 1e-9, each amount is coefficient x level of a named fact from a named rule, and a "none" names, for every candidate, why it did not form.

| | S | A | B-parts | B-circ | B | C | A-Sel2 | B-Sel0 | B-Sel1 |
|---|---|---|---|---|---|---|---|---|---|
| Outcomes checked | 306,180 | 306,180 | 306,180 | 306,180 | 306,180 | 306,180 | 306,180 | 306,180 | 306,180 |
| Not reconstructed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**PV2, the whole chain** (intention, reason, part, fact, circumstance, level, rule): what each representation's explanation emits, against what it holds. *Corrected after the run*: the version of this table written before any run claimed that B and C meet PV2. An audit of the explanation objects this fixture builds showed that they do not emit parts, directions or satisfied circumstances (see `results.md`). No computed number changed.

| Element of the chain | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|
| The reason | no | yes | yes | yes | yes | yes |
| Each fact with its level, coefficient, amount and rule | rule weights only | yes | yes | yes | yes | yes |
| A condition, named as a condition | no | no (read as a weight) | yes | no (read as a weight) | yes | yes |
| For a reason that did not apply, what failed | no | its gate | its condition or gate | its circumstance | its condition or circumstance | its condition, circumstance or reinforced reason |
| Each fact's part (push or hold-back) | not held | not held | held, not emitted (sign only) | not held | held, not emitted | held, not emitted |
| A reason's direction | not held | not held | held, not emitted | not held | held, not emitted | held, not emitted |
| The circumstance under which an applicable reason applied | not held | not held | not held | held, not emitted | held, not emitted | held, not emitted |
| Which alternative operated | - | - | - | - | - | yes |
| **PV2 as implemented** | **not met** | **not met** | **not met** | **not met** | **not met** | **not met** |

Explanations of a "none" under B, one per case:

- F1 s0: took_what_was_not_mine: owning_it_only_if_answerable condition belief:answerable_for($self,missing_can) does not hold
- F2 s0: protect: standing_in_the_way circumstance target_present does not hold
- F3 s0: took_what_was_not_mine: support 0.000 is not positive
- F4 s0: protect: support -0.240 is not positive

#### 4. Behaviour on the frozen file

`intentions.json`, read with the causal-route declarations and nothing new: the declared enabler is read as a condition, the declared inhibitor as a hold-back, circumstances are the shipped gates, and there are no relations. Over the 30,618 cells of the sweep (2,187 profiles x 7 wants x 2 circumstances). S differs from `IntentionSelector.Form` in **0** cells; weights not equal to the bit: **0**.

| | No intention | Ties | Differs from A | Share | Differs from S |
|---|---|---|---|---|---|
| S | 0 | 0 | 25 | 0.1 % | 0 |
| A | 0 | 25 | 0 | 0.0 % | 25 |
| B-parts | 1,094 | 32 | 4,074 | 13.3 % | 4,099 |
| B-circ | 0 | 25 | 0 | 0.0 % | 25 |
| B | 1,094 | 32 | 4,074 | 13.3 % | 4,099 |
| C | 1,094 | 32 | 4,074 | 13.3 % | 4,099 |
| B-parts+w | 1,094 | 25 | 1,185 | 3.9 % | 1,210 |
| A-Sel2 | 0 | 25 | 0 | 0.0 % | 25 |
| B-Sel0 | 0 | 32 | 2,980 | 9.7 % | 3,005 |
| B-Sel1 | 1,094 | 32 | 4,074 | 13.3 % | 4,099 |

**B-parts against A, by group:** `avoid_exposure` alone 1,094, `avoid_exposure` in company 1,036, `get_food` alone 972, `get_food` in company 972.

**B-parts+w against A, by group:** `avoid_exposure` alone 1,094, `avoid_exposure` in company 91.

**B-parts against A, by who changed and how:**

| Profile | A chose | B-parts chose | Cells |
|---|---|---|---|
| believes it was theirs to answer for | took_what_was_not_mine | take_responsibility | 1,944 |
| holds no such belief | took_what_was_not_mine | none | 1,094 |
| believes it was theirs to answer for | took_what_was_not_mine | protect | 627 |
| believes it was theirs to answer for | took_what_was_not_mine | prevent_argument | 311 |
| holds no such belief | took_what_was_not_mine | protect | 70 |
| holds no such belief | took_what_was_not_mine | prevent_argument | 21 |
| believes it was theirs to answer for | took_what_was_not_mine | tie:prevent_argument=protect | 7 |

#### 5. Behaviour in real mornings

50 baseline mornings (5 variants x 10 seeds), the frozen file read as in section 4. **Live cells:** every real decision moment (3,689) asked about every want with a compatible rule: 25,823 cells carrying real beliefs and feelings. **Real decisions:** every real pantry-check for a want whose shipped proposals lead there, with every other member of the cast at the same moment: 1,028.

| | S | A | B-parts | B | B-parts+w |
|---|---|---|---|---|---|
| Live cells differing from A | 0 (0.0 %) | 0 (0.0 %) | 1,388 (5.4 %) | 1,388 (5.4 %) | 312 (1.2 %) |
| Live cells with no intention | 0 | 0 | 272 | 272 | 272 |
| Real decisions differing from A | 0 of 1,028 | 0 of 1,028 | 99 of 1,028 | 99 of 1,028 | 0 of 1,028 |
| Real decisions with no intention | 0 | 0 | 0 | 0 | 0 |

B-parts against A in live cells, by want: `avoid_exposure` 643, `get_food` 745.

| Morning | Who | Want | A | B-parts |
|---|---|---|---|---|
| daniel_ate_it/1 m1 | daniel | `avoid_exposure` in company | took_what_was_not_mine | protect |
| daniel_ate_it/1 m1 | daniel | `get_food` in company | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/1 m4 | daniel | `avoid_exposure` in company | took_what_was_not_mine | protect |
| daniel_ate_it/1 m4 | daniel | `get_food` in company | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/1 m9 | daniel | `avoid_exposure` in company | took_what_was_not_mine | protect |
| daniel_ate_it/1 m9 | daniel | `get_food` in company | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/1 m12 | daniel | `avoid_exposure` in company | took_what_was_not_mine | protect |
| daniel_ate_it/1 m12 | daniel | `get_food` in company | took_what_was_not_mine | take_responsibility |

Real decisions B-parts changes:

| Morning | Who | Want | A | B-parts |
|---|---|---|---|---|
| daniel_ate_it/1 m9 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/1 m12 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/2 m9 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/2 m12 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/3 m9 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/3 m9 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/3 m12 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |
| daniel_ate_it/4 m9 | daniel (matched) | `get_food` | took_what_was_not_mine | take_responsibility |

#### 6. Semantic and legibility evidence: the blind annotation

6 reviewers (#1 opus, #2 opus, #3 sonnet, #4 sonnet, #5 haiku, #6 haiku), each a fresh subagent shown only the items, in the rotated and swapped order the protocol fixes, under neutral ids. **They are language models, not people.** Agreement says whether a distinction is legible and reproducible, and nothing about whether it is true.

##### Q1 and Q2: same or different, and how two different reasons relate

| Item | Q1 key | Q1 answers | Majority | Matches | Q2 key | Q2 answers | Majority | Matches |
|---|---|---|---|---|---|---|---|---|
| `critical` | different | different 4, same 2 | different | yes | both_add | both_add 4, unclear 2 | both_add | yes |
| `quiet_or_open` | different | different 6 | different | yes | one_or_other | never_together 3, opposed 2, one_or_other 1 | never_together | **no** |
| `restate` | same | same 6 | same | yes | - | - | - | - |
| `present_or_absent` | different | different 6 | different | yes | never_together | never_together 6 | never_together | yes |
| `fear_holds_back` | different | different 6 | different | yes | both_add | both_add 3, one_or_other 3 | tie | **no** |
| `independent` | different | different 6 | different | yes | both_add | both_add 6 | both_add | yes |
| `worry_family` | different | different 6 | different | yes | one_strengthens_other | one_strengthens_other 5, both_add 1 | one_strengthens_other | yes |
| `verbatim` | same | same 6 | same | yes | - | - | - | - |
| `against` | different | different 6 | different | yes | opposed | opposed 6 | opposed | yes |
| `seen` | different | different 6 | different | yes | both_add | both_add 6 | both_add | yes |

##### Q3: the part each fact plays

| Item | Reason | Fact | Key | Answers | Majority | Matches |
|---|---|---|---|---|---|---|
| `critical` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `critical` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `critical` | 2 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `critical` | 2 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `owning_graded` | 1 | whether they believe the missing can was theirs to answer for | pushes | pushes 6 | pushes | yes |
| `owning_graded` | 1 | how honest they are | pushes | pushes 6 | pushes | yes |
| `owning_graded` | 1 | how much they value fairness | pushes | pushes 6 | pushes | yes |
| `easier_unseen` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `easier_unseen` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `easier_unseen` | 1 | whether anyone is watching | situation_strengthens | situation_strengthens 4, holds_back 2 | situation_strengthens | yes |
| `quiet_or_open` | 1 | how proud they are | pushes | pushes 4, holds_back 1, unclear 1 | pushes | yes |
| `quiet_or_open` | 1 | whether others will know it was them | consequence | situation_needed 4, consequence 2 | situation_needed | **no** |
| `quiet_or_open` | 2 | how proud they are | pushes | pushes 6 | pushes | yes |
| `quiet_or_open` | 2 | how much they value respect | pushes | pushes 6 | pushes | yes |
| `quiet_or_open` | 2 | whether others will know it was them | consequence | situation_needed 4, consequence 2 | situation_needed | **no** |
| `no_fairness` | 1 | how much they value fairness | pushes | pushes 6 | pushes | yes |
| `settling_conditional` | 1 | whether they believe they lead the family | must_hold | must_hold 6 | must_hold | yes |
| `settling_conditional` | 1 | how much they value control | pushes | pushes 6 | pushes | yes |
| `restate` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `restate` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `restate` | 2 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `restate` | 2 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `present_or_absent` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `present_or_absent` | 1 | how much they value keeping the family safe | pushes | pushes 6 | pushes | yes |
| `present_or_absent` | 1 | whether the person they protect is in the room | situation_needed | situation_needed 6 | situation_needed | yes |
| `present_or_absent` | 2 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `present_or_absent` | 2 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `present_or_absent` | 2 | whether the person they protect is in the room | situation_needed | situation_needed 6 | situation_needed | yes |
| `at_their_side` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `at_their_side` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `at_their_side` | 1 | whether the person they look after is in the room | situation_needed | situation_needed 6 | situation_needed | yes |
| `at_their_side` | 1 | how impulsive they are | no_part | no_part 4, pushes 2 | no_part | yes |
| `fear_holds_back` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `fear_holds_back` | 1 | how anxious a person they are | holds_back | holds_back 6 | holds_back | yes |
| `fear_holds_back` | 2 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `fear_holds_back` | 2 | how much they value keeping the family safe | pushes | pushes 6 | pushes | yes |
| `fear_holds_back` | 2 | how anxious a person they are | no_part | pushes 4, unclear 2 | pushes | **no** |
| `no_belief` | 1 | whether they believe the missing can was theirs to answer for | must_hold | must_hold 6 | must_hold | yes |
| `no_belief` | 1 | how honest they are | pushes | pushes 6 | pushes | yes |
| `no_belief` | 1 | how much they value fairness | pushes | pushes 6 | pushes | yes |
| `independent` | 1 | how much they value keeping the family safe | pushes | pushes 6 | pushes | yes |
| `independent` | 2 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `owning_conditional` | 1 | whether they believe the missing can was theirs to answer for | must_hold | must_hold 6 | must_hold | yes |
| `owning_conditional` | 1 | how honest they are | pushes | pushes 6 | pushes | yes |
| `owning_conditional` | 1 | how much they value fairness | pushes | pushes 6 | pushes | yes |
| `worry_family` | 1 | how anxious a person they are | pushes | pushes 6 | pushes | yes |
| `worry_family` | 1 | whether anyone else is in the room | situation_needed | situation_needed 5, situation_strengthens 1 | situation_needed | yes |
| `worry_family` | 2 | how much they value keeping the family safe | pushes | pushes 6 | pushes | yes |
| `verbatim` | 1 | how much they value control | pushes | pushes 6 | pushes | yes |
| `verbatim` | 1 | how dominant they are | pushes | pushes 6 | pushes | yes |
| `verbatim` | 2 | how much they value control | pushes | pushes 6 | pushes | yes |
| `verbatim` | 2 | how dominant they are | pushes | pushes 6 | pushes | yes |
| `unseen_only` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `unseen_only` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `unseen_only` | 1 | whether anyone is watching | situation_needed | situation_needed 6 | situation_needed | yes |
| `against` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `against` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `against` | 2 | how cautious they are | pushes | pushes 5, holds_back 1 | pushes | (pre-registered ambiguous) |
| `settling_graded` | 1 | whether they believe they lead the family | pushes | pushes 6 | pushes | yes |
| `settling_graded` | 1 | how much they value control | pushes | pushes 6 | pushes | yes |
| `not_there` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `not_there` | 1 | how much they value keeping the family safe | pushes | pushes 6 | pushes | yes |
| `not_there` | 1 | whether the person they protect is in the room | situation_needed | situation_needed 6 | situation_needed | yes |
| `seen` | 1 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `seen` | 1 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `seen` | 2 | how empathetic the person is | pushes | pushes 6 | pushes | yes |
| `seen` | 2 | how much they value closeness | pushes | pushes 6 | pushes | yes |
| `seen` | 2 | whether the person they look after is in the room | situation_needed | situation_needed 6 | situation_needed | yes |
| `weak_pull` | 1 | how honest they are | pushes | pushes 6 | pushes | yes |

**Key part against majority part**, over the 68 slots that count:

| Key \ majority | pushes | holds_back | must_hold | situation_needed | situation_strengthens | no_part |
|---|---|---|---|---|---|---|
| pushes | 52 |  |  |  |  |  |
| holds_back |  | 1 |  |  |  |  |
| must_hold |  |  | 3 |  |  |  |
| situation_needed |  |  |  | 7 |  |  |
| situation_strengthens |  |  |  |  | 1 |  |
| consequence |  |  |  | 2 |  |  |
| no_part | 1 |  |  |  |  | 1 |

##### The minimal pairs

| Fact | Item | Key | Majority | Item | Key | Majority | Discriminated |
|---|---|---|---|---|---|---|---|
| believing it was theirs to answer for | `owning_graded` | pushes | pushes | `owning_conditional` | must_hold | must_hold | **yes** |
| believing they lead the family | `settling_graded` | pushes | pushes | `settling_conditional` | must_hold | must_hold | **yes** |
| whether anyone is watching | `easier_unseen` | situation_strengthens | situation_strengthens | `unseen_only` | situation_needed | situation_needed | **yes** |

##### Q5: could this person form the intention at all?

| Item | Key | Answers | Majority | Matches |
|---|---|---|---|---|
| `no_fairness` | no | no 6 | no | yes |
| `no_belief` | no | no 6 | no | yes |
| `not_there` | no | no 5, unclear 1 | no | yes |
| `weak_pull` | yes | yes 6 | yes | yes |

##### Agreement

| Question | Items or slots | Majority matches the key | Fleiss' kappa |
|---|---|---|---|
| Q1 same or different | 10 two-reason items | 10 of 10 (100.0 %) | **0.851** |
| Q2 relation | 8 items keyed different | 6 of 8 (75.0 %) | **0.630** |
| Q3 part | 68 slots (the one ambiguous slot excluded) | 65 of 68 (95.6 %) | **0.862** |
| Q5 reachable | 4 items (unstable with so few) | 4 of 4 | **0.808** |

**Underspecified by the protocol's rule** (a majority of fewer than four, or a kappa below 0.4): no item or slot; no question below 0.4.

##### Q4, verbatim: what an explanation would need to show

**`critical`**

- #1 opus: Which reason moved them: a sense that looking after this person is their job, or being unable to bear their suffering. It should also show how empathy and valuing closeness fed each one.
- #2 opus: How not being able to bear their suffering and a sense that protecting them is their job each drive shielding them, both resting on empathy and closeness, and how the two add up.
- #3 sonnet: Show that a felt sense of duty and an empathetic inability to bear seeing them suffer, both rooted in empathy and closeness, combined to produce protective action.
- #4 sonnet: Show how empathetic they are and how much they value closeness, since together these explain both their inability to bear the person's suffering and their sense of duty to look after them.
- #5 haiku: How empathetic they are and how much they value closeness.
- #6 haiku: How empathy and closeness values drive both emotional reactions and sense of duty in protecting someone.

**`owning_graded`**

- #1 opus: How sure they were that the missing can was theirs to answer for, and how their honesty and sense of fairness added to their readiness to call it theft and own up.
- #2 opus: How sure they are that the missing can was theirs to answer for, which is the main push, plus how much honesty and valuing fairness add to their readiness to own up.
- #3 sonnet: Show how certain the person was that the can was theirs to answer for, and how honest and fair-minded they are, together determining how readily they owned up.
- #4 sonnet: Show how certain they are that the can was theirs to answer for, and how honest and fair-minded they are, since all three combine to determine how readily they own up.
- #5 haiku: How certain they are the can was theirs to answer for, how honest they are, and how much they value fairness.
- #6 haiku: How certainty about responsibility, honesty, and fairness values combine to drive claiming and owning up to theft.

**`easier_unseen`**

- #1 opus: That they saw looking after this person as their job, driven by empathy and valuing closeness, and whether being unobserved made it easier to act here.
- #2 opus: How empathy and valuing closeness make looking after them feel like their job, and how being unwatched makes it easier without being needed.
- #3 sonnet: Show that empathy and valuing closeness motivate looking after the person, and that the absence of onlookers made doing so easier, strengthening the reason.
- #4 sonnet: Show their empathy and value of closeness, and whether anyone is watching, since privacy makes the act easier though it is not required for them to look after this person.
- #5 haiku: How empathetic they are, how much they value closeness, and whether anyone will be watching.
- #6 haiku: How empathy and closeness values drive protection, facilitated by the absence of observers.

**`quiet_or_open`**

- #1 opus: Whether they took responsibility quietly or openly, and why. Quietly: pride that hides their caring. Openly: pride and wanting respect for being reliable. Whether others know follows from that choice.
- #2 opus: Whether others would know it was them, which decides between the open reason and the quiet one. How pride works in the quiet reason: whether it makes them want credit or makes them hide that they cared.
- #3 sonnet: Show whether pride (paired with valuing respect, for the open route) was strong enough to prompt taking responsibility, and whether the person sought anonymity or recognition as the outcome.
- #4 sonnet: Show how proud they are and how much they value respect, together with whether others will learn it was them, since these determine whether they act to be seen or to stay unseen.
- #5 haiku: How proud they are, how much they value respect, and whether others will know what they did.
- #6 haiku: Whether pride and respect values lead them to seek public recognition or hide their caring depending on context.

**`no_fairness`**

- #1 opus: They place no value on fairness, so the only stated reason gives them nothing. An explanation would need another reason for owning up, or would have to show that they did not.
- #2 opus: Some reason besides fairness that would lead them to own up. The only reason given depends on valuing fairness, and this person does not value it at all, so it gives no push.
- #3 sonnet: Show whether the person valued fairness at all, since that appears to be the sole force behind owning up in this account.
- #4 sonnet: Show how much they value fairness, since that alone is what would make them feel it is only fair to own up to this.
- #5 haiku: How much they value fairness (they value it not at all).
- #6 haiku: What motivates someone without fairness values to own up to a theft they committed.

**`settling_conditional`**

- #1 opus: That they believe they lead the family, without which they would not settle it on their own authority at all, and how much they value control, which sets how firmly.
- #2 opus: That they believe they lead the family, which is needed for the reason to apply at all. Then how much they value control, which sets how firmly they assert their authority.
- #3 sonnet: Show whether the person actually believed they led the family (a strict requirement), and if so, how much they valued control, determining how firmly they'd assert authority.
- #4 sonnet: Show whether they believe they lead the family, since without that belief they would not settle it alone, and how much they value control, which decides how firmly.
- #5 haiku: Whether they believe they lead the family (necessary), and how much they value control.
- #6 haiku: Whether the person must believe they lead the family, and how much control values drive authority assertion.

**`restate`**

- #1 opus: That they see keeping this person from harm as their own responsibility, and how empathy and valuing closeness strengthened that sense of duty.
- #2 opus: That they see protecting this person as their own responsibility, and how their empathy and their valuing of closeness make that sense of duty stronger.
- #3 sonnet: Show that the person feels a personal duty or job-like responsibility to protect, rooted in empathy and valuing closeness, strong enough to produce protective action toward this specific person.
- #4 sonnet: Show how empathetic they are and how much they value closeness, since together these explain their sense of responsibility to keep this person from harm.
- #5 haiku: How empathetic they are and how much they value closeness.
- #6 haiku: How empathy and closeness values drive their sense of responsibility to protect someone.

**`present_or_absent`**

- #1 opus: Whether the person was in the room. If so, they shielded them from the threat. If not, they kept the matter from them. It should also show the empathy and values behind whichever applied.
- #2 opus: Whether the protected person is in the room, which decides which way of protecting applies. Then how much empathy, closeness, or valuing the family's safety drives that way of protecting.
- #3 sonnet: Show whether the protected person is present or absent, and whether empathy plus valuing family safety (if present) or empathy plus closeness (if absent) is strong enough to produce the act.
- #4 sonnet: Show whether the protected person is in the room or absent, since that determines whether they keep the matter from them or step between them and the threat, along with their empathy and values.
- #5 haiku: How empathetic they are, how much they value family safety and closeness, and whether the person is in the room.
- #6 haiku: Whether the person adapts protection methods based on whether the protected person is present or absent.

**`at_their_side`**

- #1 opus: That the person was in the room, so staying at their side was possible, and how empathy and valuing closeness drove it. Impulsiveness plays no part.
- #2 opus: That the person is in the room, so staying at their side is possible. Then how much empathy and valuing closeness push them to stay near.
- #3 sonnet: Show that the protected person is actually in the room, and that empathy and valuing closeness are strong enough to make the person want to stay physically at their side.
- #4 sonnet: Show how empathetic and close they feel to this person, and that the person is present, since staying by their side requires that; impulsiveness plays no part here.
- #5 haiku: How empathetic they are, how much they value closeness, whether the person is in the room, and how impulsive they are.
- #6 haiku: How empathy, closeness, and impulsivity combine to drive staying at someone's side when they need protection.

**`fear_holds_back`**

- #1 opus: Whether they stepped in themselves, with empathy overcoming fear, or made sure someone able to help knew, or both. It should also show how their anxiety bore on each route.
- #2 opus: How closeness and valuing the family's safety lead them to alert someone who can help, how empathy pushes them to step in, and how anxiety holds back stepping in. What part anxiety plays in alerting others is not stated.
- #3 sonnet: Show how strong the fear is relative to empathy driving direct intervention, and whether closeness and valuing family safety instead lead the person to alert someone else who can help.
- #4 sonnet: Show how much they value closeness and family safety, how anxious and empathetic they are, and whether their anxiety leads them to alert someone else instead of, or alongside, stepping in themselves despite fear.
- #5 haiku: How empathetic they are, how anxious they are, how much they value closeness, and how much they value family safety.
- #6 haiku: How anxiety affects whether they get others to help or directly intervene, while empathy drives both.

**`no_belief`**

- #1 opus: They do not believe the missing can was theirs to answer for, so this reason cannot apply. An explanation would need to show that they did not take it as theft, or give another route.
- #2 opus: Whether they believe the missing can was theirs to answer for. Without that belief, the reason cannot apply, however honest or fair they are. This person lacks the belief.
- #3 sonnet: Show whether the person believed the can was theirs to answer for (a strict requirement), and, if so, how their honesty and sense of fairness made owning up more or less ready.
- #4 sonnet: Show whether they believe the can was theirs to answer for, since without that belief they cannot take it as theft at all, and how honesty and fairness shape how readily they own up.
- #5 haiku: Whether they believe the can was theirs to answer for (they do not).
- #6 haiku: What would make someone who doesn't feel responsible for a theft come to own it as theirs.

**`independent`**

- #1 opus: Whether they shielded the person out of responsibility for the family's safety, out of empathy at seeing them afraid, or both, and how much each weighed.
- #2 opus: How strongly empathy (not bearing to see them afraid) and a sense of responsibility for the family's safety each push them to shield the person, and how the two add together.
- #3 sonnet: Show whether the person's sense of responsibility for family safety, their empathetic distress at seeing the other afraid, or both together, were strong enough to prompt shielding.
- #4 sonnet: Show how much they cannot bear seeing this person afraid and how strongly they feel responsible for family safety, since either alone could explain why they shield them.
- #5 haiku: How much they value keeping the family safe and how empathetic they are.
- #6 haiku: Whether empathy and family safety values independently drive protection or operate together.

**`owning_conditional`**

- #1 opus: That they believe the missing can was theirs to answer for, without which this reason cannot apply, and how honest and fairness-minded they are, which sets how readily.
- #2 opus: That they believe the missing can was theirs to answer for, which is needed first. Then how much honesty and valuing fairness make them ready to call it theft and own up.
- #3 sonnet: Show whether the person believed the can was theirs to answer for (a strict requirement), and, if so, how their honesty and sense of fairness shaped how readily they owned up.
- #4 sonnet: Show whether they believe the can was theirs to answer for, since without that belief they cannot take it as theft at all, and how honesty and fairness shape how readily they own up.
- #5 haiku: Whether they believe the can was theirs to answer for (necessary), and how honest and fair they are.
- #6 haiku: How belief in responsibility, honesty, and fairness values combine to drive owning up to theft.

**`worry_family`**

- #1 opus: That others were present, so they felt afraid for the person, and that because the person is family this fear became unbearable enough to make them protect.
- #2 opus: That others are about, which sets off their fear. Then how anxious they are, and how valuing the family's safety makes that fear unbearable without acting alone.
- #3 sonnet: Show that others were present triggering fear for the family member, and that valuing family safety intensified that fear enough to make it unbearable and prompt protection.
- #4 sonnet: Show how much they value family safety and how anxious they are, and whether others are present, since family closeness intensifies a fear that anxiety raises especially around others.
- #5 haiku: How anxious they are, whether anyone else is present, and how much they value family safety.
- #6 haiku: Whether family values drive unbearable fear, and whether anxiety specifically intensifies when others are present.

**`verbatim`**

- #1 opus: That they saw the matter as needing a decision that was theirs to make, driven by how much they value control and how dominant they are.
- #2 opus: That a decision is needed and they see deciding as their place, and how much valuing control and being dominant make them assert it.
- #3 sonnet: Show that valuing control and being dominant combined to produce a felt entitlement to decide the matter personally, strong enough to assert authority rather than defer.
- #4 sonnet: Show how much they value control and how dominant they are, since together these explain their felt entitlement to be the one who decides the matter.
- #5 haiku: How much they value control and how dominant they are.
- #6 haiku: How valuing control and dominance combine to drive asserting authority over decisions.

**`unseen_only`**

- #1 opus: That nobody was watching, so they could help without shaming the person, and how empathy and valuing closeness moved them to look after them.
- #2 opus: That nobody is watching, so the person is spared shame. Then how much empathy and valuing closeness push them to help in private.
- #3 sonnet: Show that no one else was watching, and that empathy and valuing closeness motivated helping privately specifically to spare the other person's shame.
- #4 sonnet: Show their empathy and value of closeness, and that nobody is watching, since the protected person's shame in front of others makes privacy necessary for this kind of help.
- #5 haiku: How empathetic they are, how much they value closeness, and whether anyone will be watching.
- #6 haiku: How the person balances empathy/closeness values with concern for the protected person's shame when help is witnessed.

**`against`**

- #1 opus: How their sense of duty, fed by empathy and closeness, weighed against the caution that stepping in could make things worse, and which one won.
- #2 opus: How caution, which pulls them back for fear of making things worse, weighs against the sense of duty that empathy and closeness push, and which one wins.
- #3 sonnet: Show the balance between the felt duty to intervene (from empathy and closeness) and caution that stepping in might worsen things, and which force wins out.
- #4 sonnet: Show how cautious they are, favoring restraint, against their empathy and sense of duty toward closeness, favoring direct action, since these pull toward opposite responses to the danger.
- #5 haiku: How empathetic they are, how much they value closeness, and how cautious they are.
- #6 haiku: Whether the person's caution about making things worse outweighs their sense of responsibility to protect.

**`settling_graded`**

- #1 opus: How much believing they lead the family, and how much valuing control, each added to their readiness to settle it themselves.
- #2 opus: How much believing they lead the family and how much valuing control each add to their readiness to settle the matter themselves. Neither one is required on its own.
- #3 sonnet: Show how strongly the person believes they lead the family and how much they value control, together giving enough readiness to settle the matter on their own authority.
- #4 sonnet: Show how strongly they believe they lead the family and how much they value control, since both add together to explain their readiness to settle the matter themselves.
- #5 haiku: Whether they believe they lead the family and how much they value control.
- #6 haiku: Whether the person's belief in family leadership combines with desire for control to drive independent authority assertion.

**`not_there`**

- #1 opus: The person to be protected is not in the room, so standing between them and the threat is impossible. An explanation would need another route, or would have to show why they did not act.
- #2 opus: Whether the person is present, since standing between them and the threat needs them there. They are not in the room, so this reason cannot apply, whatever their empathy or concern for the family.
- #3 sonnet: Show whether the protected person was actually present, since the reason requires it, and whether empathy and valuing family safety were strong enough to prompt physically intervening.
- #4 sonnet: Show that the protected person is physically present, which this reason requires, together with how empathetic they are and how much they value family safety.
- #5 haiku: How empathetic they are, how much they value family safety, and whether the person is in the room (they are not).
- #6 haiku: Whether the person can protect someone absent through means other than putting themselves between them and threats.

**`seen`**

- #1 opus: Their sense that looking after the person is their job and, if the person was suffering in front of them, their inability to bear it. Each adds through empathy and closeness.
- #2 opus: Whether the person is in front of them, which the distress reason needs, plus how empathy and closeness drive both that distress and their separate sense that protecting them is their job.
- #3 sonnet: Show that empathy and closeness support a general sense of duty, and separately, when the person is present suffering, that seeing it is unbearable enough to drive protection.
- #4 sonnet: Show how empathetic and close they feel to this person, and whether the person is present, since witnessing suffering directly adds to an already-standing sense of duty to look after them.
- #5 haiku: How empathetic they are, how much they value closeness, and whether the person will be in the room.
- #6 haiku: How empathy and closeness values drive both emotional reaction to suffering and sense of responsibility for protection.

**`weak_pull`**

- #1 opus: That the task needed doing and their slight honesty was enough, with nothing else bearing on it, to make them take responsibility.
- #2 opus: That their slight honesty gives a weak but real push toward taking responsibility, and whether that push is enough when nothing else pushes or holds them back.
- #3 sonnet: Show that even a modest degree of honesty, combined with a sense that the task needed doing, was enough to make this person take responsibility.
- #4 sonnet: Show how honest they are, since even a small amount is framed as enough for them to feel that, because it needed doing, they should take responsibility.
- #5 haiku: Whether something needs doing and how honest the person is (they are slightly honest).
- #6 haiku: What task needed doing and whether the person's slight honesty is sufficient motivation to take responsibility.


#### 7. Which distinctions are required, and the verdict the committed criteria give

Computed from sections 1, 2, 3 and 6 by the rules committed in the predictions. **Necessary**: every representation lacking the element fails at least one of the distinction's checks. **Legible**: every annotation test of it has a majority matching the key, and the kappa of each question it rests on is at least 0.4. REQUIRED is both; REDUNDANT is not necessary; UNSUPPORTED is necessary but not legible.

| Distinction | Element | Checks | Representations lacking the element that pass them all | Annotation tests met | Kappa | Status |
|---|---|---|---|---|---|---|
| reason identity (H1) | identity | A.1, A.2, A.3, B.1, B.2 | none | 3 of 3 | Q1 0.851 | **REQUIRED** |
| condition against push (H2) | parts | C.3, C.4, C.5, C.6, F.1 | none | 5 of 5 | Q3 0.862 | **REQUIRED** |
| hold-back against a reason against | parts | E.6, E.7 | none | 2 of 3 | Q3 0.862, Q2 0.630 | **UNSUPPORTED** |
| circumstance (H3) | circumstances | B.3, D.2, D.3, D.4, E.3, F.2 | none | 7 of 7 | Q3 0.862 | **REQUIRED** |
| situational push against gate | circumstances | D.6 | none | 1 of 1 | Q3 0.862 | **REQUIRED** |
| alternative (H4) | relations | E.2 | none | 0 of 1 | Q2 0.630 | **UNSUPPORTED** |
| reinforcing (H4) | relations | E.4, E.5 | none | 1 of 1 | Q2 0.630 | **REQUIRED** |
| exclusive (H4) | relations | E.3 | B-circ, B | 1 of 1 | Q2 0.630 | **REDUNDANT** |
| opposed (H4) | relations | E.6, E.7 | B-parts, B | 1 of 1 | Q2 0.630 | **REDUNDANT** |
| no viable cause (H5) | viability | F.1, F.2, F.3, F.4, F.5, F.6 | none | 4 of 4 | Q5 0.808 | **REQUIRED** |

| Representation | (i) passes every check of every REQUIRED distinction | (ii) restatement, negative controls, PV1 | (iii) carries no UNSUPPORTED element | (iv) passes no check only through a copy | All four |
|---|---|---|---|---|---|
| S | no | no | yes | no | no |
| A | no | yes | yes | no | no |
| B-parts | no | yes | no | no | no |
| B-circ | no | yes | yes | no | no |
| B | no | yes | no | no | no |
| C | yes | yes | no | yes | no |

**By the committed criteria: MODIFY** (C meets (i) and (ii); none meets all four).

#### Z. The files after the whole run

| File | sha256 | |
|---|---|---|
| `intentions.json` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | unchanged |
| `causal-routes.json` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | unchanged |
| `held-out-people.json` | `0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131` | unchanged |
| `reason-semantics.json` | `5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638` | unchanged |

Every case, variant and representation above lived in memory.

---

## predictions.md

### Reason semantics: predictions

Written and committed **before any fixture for this experiment existed and before
any reviewer was asked anything**. Four files fix everything that could otherwise
be fitted to the results:

| File | Fixes |
|---|---|
| `Assets/_Project/Data/Experiments/reason-semantics.json` | the vocabulary; the five situations; every synthetic case, as authored rules and as declared meaning; the fixed reading rule of each representation; every check and negative control; how the frozen file is read |
| `annotation/items.json` | the 21 items shown to reviewers, and the answer key they never see |
| `annotation/protocol.md` | the reviewers, the order, the prompt verbatim, and the analysis |
| `prediction-model.py` | an independent re-derivation, in Python, of every analytic count below |

Every prediction is marked either **analytic** or **empirical**:
- **analytic:** it follows from the reading rules by arithmetic. If it fails, the
  fixture or the model is wrong.
- **empirical:** it is a guess. If it fails, that is a finding.

#### The question

*What must a simulated reason contain so that the system can distinguish
genuinely different causal explanations without silently turning conditions into
weights, circumstances into hidden gates, or competing reasons into arbitrary
score arithmetic?*

The causal-route experiment showed that a declared reason identity is necessary.
It also found three things that identity alone could not express:
- a fact that is a precondition, not a weight;
- a circumstance the shipped gate cannot say;
- a relation between reasons that readers judge differently from the author.

This experiment asks which of those, and which further distinctions, a reason must
carry before any formula is chosen. It does not choose a formula.

#### Hypotheses

| | |
|---|---|
| **H1** | A reason needs a declared identity, independent of rule identity |
| **H2** | A fact inside a reason can be a push or an enabling condition, and these must be represented differently if readers treat them differently |
| **H3** | A reason can depend on a circumstance (someone present or absent, someone watching, the person concerned present or absent), and a circumstance must not be smuggled into a weight |
| **H4** | Reasons for one intention cannot be assumed to add. Which of independent, alternative, reinforcing, opposed and exclusive are actually needed is to be found, not assumed |
| **H5** | An intention with no applicable reason, or no positive support, should not form merely because it is the only candidate; "no viable intention" may need to be representable |

#### What is frozen

| File | sha256 |
|---|---|
| `Assets/_Project/Data/Experiments/intentions.json` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| `Assets/_Project/Data/Experiments/causal-routes.json` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` |
| `Assets/_Project/Data/Experiments/held-out-people.json` (the sweep) | `0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131` |
| `Assets/_Project/Data/Experiments/reason-semantics.json` (this experiment's cases) | `5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638` |

All four are hashed at the start and at the end of the run.

Nothing in production changes: not `Fallow.Core`, the shipped rules, character
data, S1 scoring, the selector, motivations, candidates, actions, beliefs,
emotions or memories. The existing causal-route representation and its fixture
are not modified either.

No psychological variable is added. Two situation features are experiment-only:
- whether the person the want concerns is present, computed from the real
  percept's `Present` and the want's target;
- whether anyone is watching, which no production data carries.

#### Vocabulary

| Term | Meaning |
|---|---|
| **fact** | a level read from the person (trait, value, belief) or a feature of the situation |
| **intention** | what the person is trying to accomplish |
| **reason** | a declared explanation, with an identity, of why some facts lead toward (or away from) an intention |
| **part** | what a fact does inside a reason: **push** (the more, the stronger), **hold-back** (the more, the weaker; it can cancel its reason, not reverse it), **condition** (must be true for the reason to apply at all; not a strength) |
| **circumstance** | a feature of the situation a reason needs in order to apply at all; not a strength. A **situational push** makes a reason stronger without being needed |
| **direction** | whether a whole reason leads toward the intention or away from it |
| **relation** | independent (default), alternative, reinforces, exclusive |

#### The evaluation space

- **Profiles:** the 2,187 sweep profiles: 7 traits at 0.15, 0.50 and 0.85; six
  values weighted by rank; four belief sets.
- **Situations:** five of them:
  - s0: alone;
  - s1: in company, the person concerned absent, nobody watching;
  - s2: in company, the person concerned present, nobody watching;
  - s3: in company, the person concerned absent, someone watching;
  - s4: in company, the person concerned present, someone watching.
- **Cells:** 2,187 x 5 = **10,935 per case**.
- **Rival:** every case except family F has one, `share_information`, so that a
  change in support can be seen to change what is chosen.

**A property of the sweep, stated now:** the value rotation (index mod 6) and the
belief set (index mod 4) are functions of the profile's index. So they are
correlated with its least significant trait, `anxious` (index mod 3). Some
combinations of anxiety, values and beliefs never occur. Counts of changed
choices inherit this.

#### The representations

Each reads only what its vocabulary can hold, by a fixed rule (`reading_rules` in
the JSON). Nothing is tuned per case. The representations form a lattice, so that
each distinction can be attributed to the element that makes it.

| | Reason identity | Parts and direction | Declared circumstances, situational pushes | Relations | Forms when |
|---|---|---|---|---|---|
| **S** the shipped selector (control) | no | no | shipped gates only | no | any rule weighs more than zero (the discard) |
| **A** reasons + weights | yes | no: every fact is a weight | shipped gates only | no | any compatible candidate (Sel-0) |
| **B-parts** | yes | yes | shipped gates only | no | support > 0 (Sel-2) |
| **B-circ** | yes | no | yes | no | support > 0 |
| **B** | yes | yes | yes | no | support > 0 |
| **C** | yes | yes | yes | yes | support > 0 |

A is the causal-route experiment's D without its declared alternatives.

**What cannot be held degrades by a fixed rule:**
- a condition becomes the weight the author wrote for it;
- a circumstance becomes the nearest shipped gate the author wrote (or none);
- a relation becomes independence;
- a reinforcement becomes the copy of the other reason's gate that an author
  without relations writes.

**Viability ablations**, reported for family F and the frozen file:
- Sel-0: forms if admitted by a gate or declared circumstance;
- Sel-1: forms if a reason toward it applies;
- Sel-2: forms if its support is positive.

They are run as A-Sel2, B-Sel0 and B-Sel1.

**What most of the representational results are, and what they are not.** A
vocabulary that cannot hold a distinction fails the checks that need it. That
much is close to true by construction, and C passes everything because it reads
every declaration. The results that are not by construction are these:
- **reducibility:** whether a distinction can be expressed by other elements,
  which the checks measure;
- **how far a failure reaches**, in cells and in changed choices;
- **legibility**, which the annotation measures;
- **behavioural consequences** on the frozen file and in real mornings.

#### The families and the checks

The full cases are in `reason-semantics.json`. **Passing is a property of every
cell** (10,935 per case), fixed now:

| Check | Case | Passes if |
|---|---|---|
| A.1 to A.3 | a reason written twice, reworded, split into two rules | support, explanation and outcome identical to the single statement in every cell |
| B.1 | B1 against A1 (the critical pair) | protect's support differs somewhere |
| B.2 | B1 | two reasons identical in every declared respect are flagged wherever both apply |
| B.3 | B2 | the reason needing the person there applies exactly where they are |
| C.1, C.2 | a belief as a push | the reason applies without the belief, and the belief adds coefficient x level |
| C.3, C.4 | the same belief as a condition (identical authored rules) | without it the reason does not apply; with it, it adds no strength |
| C.5, C.6 | the two pairs | the two readings are told apart somewhere |
| D.1 to D.4 | one reason's facts under four circumstances | it applies exactly where its circumstance holds |
| D.5 | D1 to D4 | where it applies, it is exactly as strong as the same facts everywhere |
| D.6 | a situational push | the reason applies everywhere and gains exactly 0.15 wherever nobody is watching |
| E.1 | independent reasons | wherever both push, support exceeds either alone |
| E.2 | alternatives | support never exceeds the stronger alternative alone |
| E.3 | exclusive by circumstance | the two never both contribute |
| E.4, E.5 | a reinforcing reason, before and after the reinforced reason is edited | it contributes exactly where the reinforced reason applies |
| E.6 | a reason against | it lowers support wherever it has force |
| E.7 | a hold-back local to one reason | it never lowers the other reason, and never turns its own reason against the intention |
| F.1 to F.5 | the only candidate | it forms exactly when a reason applies with positive support (F.5, a weak but real reason, always) |
| F.6 | F4 as one rule against F4 as two | the outcome is the same in every cell |

**Negative controls, G.1 to G.7**, are applied to every case, under every
representation, in every cell:
- an unread trait moved;
- every note and meaning rewritten;
- rule order reversed;
- rules renamed;
- reason keys renamed;
- an unread situation feature toggled;
- an unread belief added.

**Provenance:**
- **PV1**: the explanation reconstructs the outcome. The winner's support is
  rebuilt from the listed contributions within 1e-9, and each amount names its
  fact, level and rule. A "none" lists why each candidate did not form.
- **PV2**: the explanation carries the whole chain: intention, reason, part,
  fact, level, rule.

#### P1. Representational predictions (analytic; `prediction-model.py`)

Cells violating each check, of 10,935 (0 means the check passes; for B.1, C.5 and
C.6, the count is of cells that differ, and 0 fails):

| Check | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|
| A.1 | **10,935** | 0 | 0 | 0 | 0 | 0 |
| A.2 | **10,935** | 0 | 0 | 0 | 0 | 0 |
| A.3 | **7,290** | 0 | 0 | 0 | 0 | 0 |
| B.1 (cells differing) | **0** | 10,935 | 10,935 | 10,935 | 10,935 | 10,935 |
| B.2 | **10,935** (no flag) | 0 | 0 | 0 | 0 | 0 |
| B.3 | **4,374** | **4,374** | **4,374** | 0 | 0 | 0 |
| C.1, C.2 | 0 | 0 | 0 | 0 | 0 | 0 |
| C.3, C.4 | **10,935** | **10,935** | 0 | **10,935** | 0 | 0 |
| C.5, C.6 (cells differing) | **0** | **0** | 10,935 | **0** | 10,935 | 10,935 |
| D.1 | 0 | 0 | 0 | 0 | 0 | 0 |
| D.2, D.3, D.4 | **4,374** each | **4,374** each | **4,374** each | 0 | 0 | 0 |
| D.5 | 0 | 0 | 0 | 0 | 0 | 0 |
| D.6 | **4,374** | **4,374** | **4,374** | 0 | 0 | 0 |
| E.1 | 0 | 0 | 0 | 0 | 0 | 0 |
| E.2 | **10,935** | **10,935** | **10,935** | **10,935** | **10,935** | 0 |
| E.3 | **8,748** | **8,748** | **8,748** | 0 | 0 | 0 |
| E.4 | 0 | 0 | 0 | 0 | 0 | 0 |
| E.5 | **1,458** | **1,458** | **1,458** | **1,458** | **1,458** | 0 |
| E.6 | **10,935** | 0 | 0 | 0 | 0 | 0 |
| E.7 | 0 | **4,860** | 0 | **4,860** | 0 | 0 |
| F.1 | **5,470** | **5,470** | 0 | **5,470** | 0 | 0 |
| F.2 | **4,374** | **4,374** | **4,374** | 0 | 0 | 0 |
| F.3 | 0 | **3,640** | 0 | 0 | 0 | 0 |
| F.4 | **5,060** | **5,060** | 0 | 0 | 0 | 0 |
| F.5 | 0 | 0 | 0 | 0 | 0 | 0 |
| F.6 | **5,060** | 0 | 0 | 0 | 0 | 0 |

**Checks passed, by family:**

| Family | S | A | B-parts | B-circ | B | C |
|---|---|---|---|---|---|---|
| A restatement (3) | 0 (0 %) | 3 (100 %) | 3 | 3 | 3 | 3 |
| B shared facts (3) | 0 (0 %) | 2 (66.7 %) | 2 (66.7 %) | 3 (100 %) | 3 | 3 |
| C evidence or condition (6) | 2 (33.3 %) | 2 (33.3 %) | 6 (100 %) | 2 (33.3 %) | 6 | 6 |
| D circumstance (6) | 2 (33.3 %) | 2 (33.3 %) | 2 (33.3 %) | 6 (100 %) | 6 | 6 |
| E relation (7) | 3 (42.9 %) | 3 (42.9 %) | 4 (57.1 %) | 4 (57.1 %) | 5 (71.4 %) | 7 (100 %) |
| F no viable cause (6) | 2 (33.3 %) | 2 (33.3 %) | 5 (83.3 %) | 5 (83.3 %) | 6 (100 %) | 6 |
| **All (31)** | **9 (29.0 %)** | **14 (45.2 %)** | **22 (71.0 %)** | **23 (74.2 %)** | **29 (93.5 %)** | **31 (100 %)** |

In percentage points against A: B-parts +25.8, B-circ +29.0, B +48.4, C +54.8.
Against S: A +16.1, and C +71.0.

**What the pattern says, if it holds:**

| Distinction | Checks | What carries it | Reducible to something else? |
|---|---|---|---|
| Reason identity (H1) | A.1 to A.3, B.1, B.2 | identity (A and up) | no |
| Condition against push (H2) | C.3 to C.6, F.1 | parts (B-parts, B, C) | no |
| Hold-back against a reason against | E.6, E.7 | parts and direction | no: S gets E.7 right only through the discard and fails E.6; A gets E.6 right and fails E.7 |
| Circumstance, including the person concerned and watching (H3) | B.3, D.2 to D.4, E.3, F.2 | declared circumstances | no, for circumstances the shipped gate cannot say (D.1, which it can say, passes everywhere) |
| Situational push against gate | D.6 | declared situational pushes | no |
| Exclusive (H4) | E.3 | **circumstances** | **yes**: B-circ and B pass without any relation |
| Opposed (H4) | E.6, E.7 | **parts and direction** | **yes**: B-parts and B pass without any relation |
| Reinforcing (H4) | E.4, E.5 | a copied gate passes E.4 everywhere; only a relation that refers to the other reason passes E.5 | **partly**: copying is enough until the reinforced reason changes |
| Alternative (H4) | E.2 | relations (C only) | no |
| No viable cause (H5) | F.1 to F.6 | see below | |

**The F ablations** (analytic):

| | A-Sel2 | B-Sel0 | B-Sel1 | B (Sel-2) |
|---|---|---|---|---|
| F.1 belief absent | fail (5,470) | fail (5,470) | pass | pass |
| F.2 person absent | fail (4,374) | **pass** | pass | pass |
| F.3 nothing pushes | pass | fail (3,640) | fail (3,640) | pass |
| F.4 outweighed | pass | fail (5,060) | fail (5,060) | pass |

So "no viable cause" has three separate sources, predicted to need three
separate things:
- **A failed circumstance** already works through compatibility, since B-Sel0
  passes F.2. It needs only a circumstance the gate can say.
- **A failed condition** needs applicability: Sel-1.
- **No support, or support outweighed,** needs a positive-support rule: Sel-2.

The shipped selector's discard gets F.3 right by accident. It fails F.6: whether
S forms an intention depends on how the reasons are split into rules.

**Negative controls (analytic):** 0 changes, in every case, under every
representation, for G.1 to G.7.

**Provenance (analytic):**
- **PV1** holds for every representation, S included: S reconstructs its support
  from rule weights.
- **PV2** fails for S (no reasons, no parts), A (no parts) and B-circ (no parts
  for person facts). It holds for B-parts, B and C.

**Changed choices against the rival** (analytic), in cells of 10,935 where the
representation chooses differently from C:

| Case | S | A | B-parts | B-circ | B |
|---|---|---|---|---|---|
| A1, A2 | 6,070 | 0 | 0 | 0 | 0 |
| B2 | 2,428 | 2,428 | 2,428 | 0 | 0 |
| C1c | 5,465 | 5,465 | 0 | 5,465 | 0 |
| C2c | 605 | 605 | 0 | 605 | 0 |
| D2, D3, D4 | 974 each | 974 each | 974 each | 0 | 0 |
| D5 | 1,210 | 1,210 | 1,210 | 0 | 0 |
| E2 | 4,255 | 4,255 | 4,255 | 4,255 | 4,255 |
| E3 | 4,856 | 4,856 | 4,856 | 0 | 0 |
| E4b | 485 | 485 | 485 | 485 | 485 |
| E5 | 1,545 | 0 | 0 | 0 | 0 |
| E6 | 0 | 0 | 0 | 0 | 0 |
| F1 | 5,470 | 5,470 | 0 | 5,470 | 0 |
| F2 | 4,374 | 4,374 | 4,374 | 0 | 0 |
| F3 | 0 | 3,640 | 0 | 0 | 0 |
| F4 | 5,060 | 5,060 | 0 | 0 | 0 |
| F4m | 0 | 5,060 | 0 | 0 | 0 |
| every other case | 0 | 0 | 0 | 0 | 0 |

E6 is the one case where a representational failure (A: 4,860 cells) changes no
choice. In the cells where the hold-back reverses its reason, the rival is never
between the two supports. This is because of the sweep's correlations, noted
above.

#### P2. Semantic and legibility predictions (empirical)

| # | Prediction |
|---|---|
| 2.1 | Judgment (Q1): kappa at least 0.6; the majority matches the key on at least 9 of the 10 two-reason items |
| 2.2 | Relation (Q2): kappa at least 0.4 over the eight items keyed different |
| 2.3 | Relation majorities match the key on `critical`, `seen`, `independent` and `fear_holds_back` (both add), `quiet_or_open` (one or other), `present_or_absent` (never together) and `against` (opposed) |
| 2.4 | **`worry_family` does not get a majority for "one strengthens the other"**: reinforcement is the least legible relation. So 7 of 8 relation majorities match |
| 2.5 | The condition beliefs (`owning_conditional`, `settling_conditional`): must hold, at least 5 of 6 each |
| 2.6 | The same beliefs as pushes (`owning_graded`, `settling_graded`): pushes, at least 4 of 6 each. The graded answerable belief is the weakest, because what the belief is pulls toward a precondition |
| 2.7 | Watching: needed in `unseen_only` (at least 5 of 6); strengthens in `easier_unseen` (at least 4 of 6). So all three minimal pairs are discriminated |
| 2.8 | The hold-back: `fear_holds_back`'s anxiety holds reason 1 back (at least 5 of 6) and plays no part in reason 2 (at least 4 of 6) |
| 2.9 | The irrelevant fact (`at_their_side`, impulsive): no part, at least 5 of 6 |
| 2.10 | "Whether others will know it was them" (`quiet_or_open`): a consequence, by a majority, in at least one of its two reasons |
| 2.11 | Parts (Q3): kappa at least 0.4 over all slots but the pre-registered ambiguous one |
| 2.12 | Reachability (Q5): no for `no_belief` and `not_there` (at least 5 of 6), no for `no_fairness` (at least 4 of 6), yes for `weak_pull` (at least 5 of 6) |

#### P3. Behavioural predictions

**On the frozen file** (analytic; `prediction-model.py frozen`, 30,618 cells):

| # | Prediction |
|---|---|
| 3.1 | A differs from S only in the 25 real ties, as in the causal-route experiment |
| 3.2 | **B-parts, B and C all differ from A in 4,074 cells (13.3 %):** 1,094 cells of `avoid_exposure` alone become **no intention**; 1,036 cells of `avoid_exposure` in company and 972 each of `get_food` in company and alone change what is chosen. 32 ties |
| 3.3 | **Most of those changes are believers, not innocents.** Reading the belief as a condition means it adds no strength, so 2,889 cells where a believer formed the theft now form something else (2,882) or tie (7). The innocents are 91 who formed it over a rival, and 1,094 who formed it alone |
| 3.4 | B-parts with the condition keeping its authored weight (the causal-route experiment's D-enablers): 1,185 cells (1,094 none, 91 changed) |
| 3.5 | B-circ equals A on the frozen file: no frozen rule is declared a circumstance the gate cannot say, and nothing there has zero support |
| 3.6 | B-Sel0: 2,980 cells (the 1,094 innocents still "form" the theft, with nothing behind it); B-Sel1: 4,074 |

**In real mornings** (empirical). There are 50 baseline mornings: every real
decision moment asked about every want (the live cells), and the 1,028 real
pantry-check decisions.

| # | Prediction |
|---|---|
| 3.7 | In the live cells, B-parts differs from A in at least one cell, in `get_food` or `avoid_exposure` |
| 3.8 | In the live cells, B forms no intention in at least one: a real person without the belief, alone, asked about `avoid_exposure` |
| 3.9 | Of the 1,028 real pantry decisions, B-parts changes none. This is a weak guess: it depends on whether any real believer formed the theft at a real `get_food` pantry-check |

#### P4. What the answer is expected to be

- A reason must carry a **declared identity** (H1).
- **Each fact's part must be carried** (H2): push, hold-back, condition; and each
  reason's direction.
- A reason must carry its **circumstance**, in a vocabulary that can name the
  person concerned and whether anyone is watching, **separately from any
  situational push** (H3).
- **Of the relations (H4):**
  - exclusive is carried by circumstances;
  - opposed is carried by parts and direction;
  - reinforcing is carried by applicability, and needs a relation only to stay
    right when the other reason is edited;
  - **only "alternative" needs a relation of its own**, and whether "the stronger
    operates" is right is a modelling choice this experiment does not settle.
- **"No viable intention" must be representable (H5)**, and it has three sources
  that need three different things.

#### What would decide the verdict

Behaviour does not enter the verdict: behavioural consequences are reported
separately.

**Each distinction gets a status**, from two tests:
- **necessary:** every tested representation lacking the element that carries it
  fails its checks;
- **legible:** every annotation item testing it has a majority matching the key,
  and the kappa of the question it rests on is at least 0.4.

| Status | Condition |
|---|---|
| **REQUIRED** | necessary and legible |
| **REDUNDANT** | some representation without the element passes its checks |
| **UNSUPPORTED** | necessary, but not legible |

The items testing each distinction:

| Distinction | Items |
|---|---|
| identity | `restate`, `verbatim`, `critical` (Q1) |
| condition against push | the four belief slots of the minimal pairs, and `no_belief` |
| hold-back | `fear_holds_back` (anxiety) |
| reason against | `against` (Q2) |
| circumstance | the presence slots of `at_their_side`, `unseen_only`, `present_or_absent`, `seen`, `not_there` and `worry_family` |
| situational push | `easier_unseen` (watching) |
| alternative | `quiet_or_open` (Q2) |
| reinforcing | `worry_family` (Q2) |
| exclusive | `present_or_absent` (Q2) |
| no viable cause | `no_belief`, `not_there`, `no_fairness` and `weak_pull` (Q5) |

| Verdict | If |
|---|---|
| **KEEP** | Some tested representation meets all four conditions: (i) it passes every check of every REQUIRED distinction; (ii) it passes the restatement family, every negative control and PV1; (iii) it carries no element whose distinction is UNSUPPORTED; (iv) it passes no check only through a copied declaration. Its vocabulary is then what a reason needs to contain |
| **MODIFY** | No tested representation meets (i) to (iv), but one meets (i) and (ii). The stages can express everything required, but the vocabulary must change first: drop an unsupported element, replace a copy with a reference, or add a distinction readers draw that none expresses |
| **REBUILD** | No representation meets (i) and (ii) within the current stages. Expressing a required distinction would need the compatibility stage to read the person, or would lose invariance or provenance everywhere |

**My expectation is MODIFY.** If prediction 2.4 holds, reinforcement is
UNSUPPORTED, so C carries an element readers do not draw. Alternatives are
REQUIRED, so B, which lacks them, fails (i).

**Not claimed by any outcome:** that any declared part, circumstance or relation
is how people are. A passing check proves a property of a representation.
Reviewer agreement shows legibility. Neither shows psychology.

---

## results.md

### Reason semantics: results against the predictions

The measurements are in `measurements.md`, generated by
`ReasonSemanticsExperimentTests`. The predictions, the cases, the reading rules,
the checks, the annotation items with their answer key, the protocol and the
Python prediction model were committed in `e5a5131`. That was before the fixture
existed and before any reviewer was asked anything.

#### Runs

| | |
|---|---|
| Frozen | `intentions.json`, `causal-routes.json`, `held-out-people.json` and `reason-semantics.json`, each sha256-checked at the start and the end: **unchanged** |
| S against the selector | **0 of 306,180** synthetic cells and **0 of 30,618** frozen-file cells differ from `IntentionSelector.Form`; every weight is equal to the bit |
| Evaluation | 28 cases x 10,935 cells (2,187 profiles x 5 situations); six representations and three viability ablations; 7 negative controls over 306,180 to 428,652 cells each |
| Frozen file | 30,618 cells |
| Real mornings | 50 baseline mornings: 3,689 decision moments, **25,823** live cells, **1,028** real pantry-check decisions |
| Annotation | 6 blind reviewers (2 opus, 2 sonnet, 2 haiku), 21 items, 69 fact slots; responses saved verbatim in `annotation/responses/` |
| Prediction model | every analytic count of the fixture's sections 1 and 4 equals the committed Python model's |
| Fixture tests | 9 of 9 pass, after the timeout correction below; again inside the full suite (448 tests, 446 pass, the two known failures) |
| Randomness | none |
| Production changes | **none** |

**What was changed after the predictions were committed, and why:**

1. **Before the fixture first ran:** three defects found by reading it. The
   rival rule has no `route` field, so reading one would have thrown; a line
   did nothing; a table of levels was needlessly recomputed. None bears on a
   result.
2. **After the first full run:** the negative-control test was aborted by
   NUnit's default 180-second timeout, after its measurements were complete.
   The earlier fixtures declare `Timeout` explicitly and this one did not.
   `Timeout(7200000)` was added to every test and the fixture was rerun. The
   rerun reproduced the first run's measurements byte for byte.
3. **After the rerun: an audit of provenance.** The fixture's own PV2 table,
   written before any run, claimed that B's and C's explanations carry the whole
   causal chain. Reading the explanation objects the fixture builds shows they
   do not. They name the reason, each fact with its level, coefficient and
   amount, the rule that stated it, conditions, situational pushes, and, for a
   reason that did not apply, the condition or circumstance that failed. They
   do not name:
   - each fact's part (a hold-back appears only as a negative amount);
   - a reason's direction;
   - the circumstance under which an applicable reason applied.

   **The explanations were not changed.** Changing them would be tuning after
   seeing results. The table's text was corrected to say what is emitted, and
   PV2 is scored below as not met. No computed number changed. The full suite then
   regenerated `measurements.md`: identical to the fixture's runs apart from that table.

#### P1. Representational predictions (analytic)

| # | Prediction | Result | |
|---|---|---|---|
| 1.1 | The violation counts of all 31 checks under all six representations (the table in the predictions) | **every one of the 186 counts is as predicted**, from 0 through 10,935 | **PASS** |
| 1.2 | Checks passed: S 9, A 14, B-parts 22, B-circ 23, B 29, C 31 of 31 | exactly: 29.0 %, 45.2 %, 71.0 %, 74.2 %, 93.5 %, 100 % | **PASS** |
| 1.3 | The F ablations: B-Sel0 passes F.2 only of F.1 to F.4; B-Sel1 passes F.1 and F.2; A-Sel2 passes F.3 and F.4 | exactly | **PASS** |
| 1.4 | Negative controls: 0 changes, every case, every representation | 0 in all 7 controls x 6 representations, over 306,180 cells each (428,652 for G.6) | **PASS** |
| 1.5 | PV1 reconstruction holds for every representation | 0 of 2,755,620 outcomes not reconstructed | **PASS** |
| 1.6 | PV2 fails for S, A and B-circ, and holds for B-parts, B and C | **not met by any**: the implemented explanations do not name parts, directions or satisfied circumstances (see above). B and C compute with all of them, so a complete chain is available to them, but it was not produced | **FAIL** |
| 1.7 | Changed choices against C, per case | every count as predicted (for example S 6,070 on A1, B-circ 5,465 on C1c, B 4,255 on E2 and 485 on E4b, 0 on E6) | **PASS** |

#### P2. Semantic and legibility predictions (empirical)

| # | Prediction | Result | |
|---|---|---|---|
| 2.1 | Judgment kappa at least 0.6; majority matches on at least 9 of 10 | **0.851**; 10 of 10. The critical pair is the weakest, 4 of 6 "different" (two said "same") | **PASS** |
| 2.2 | Relation kappa at least 0.4 | **0.630** | **PASS** |
| 2.3 | Relation majorities match on `critical`, `seen`, `independent`, `fear_holds_back`, `quiet_or_open`, `present_or_absent`, `against` | 5 of 7. **`quiet_or_open`: never together 3, opposed 2, one or the other 1. `fear_holds_back`: a tie, both add 3, one or the other 3** | **PARTLY** |
| 2.4 | **`worry_family` gets no majority for "one strengthens the other"** | **5 of 6 say it does**. Reinforcement is legible | **FAIL** |
| 2.5 | The condition beliefs: must hold, at least 5 of 6 each | 6 of 6, 6 of 6 | **PASS** |
| 2.6 | The same beliefs as pushes: pushes, at least 4 of 6, the answerable belief the weakest | 6 of 6, 6 of 6: neither is weaker | **PARTLY** |
| 2.7 | Watching: needed in `unseen_only`, strengthens in `easier_unseen`; all three minimal pairs discriminated | 6 of 6 needed; 4 of 6 strengthens (2 said holds back); **all three pairs discriminated** | **PASS** |
| 2.8 | Fear holds reason 1 back (at least 5 of 6) and plays no part in reason 2 (at least 4 of 6) | holds back 6 of 6; **in reason 2, pushes 4 of 6, unclear 2** | **PARTLY** |
| 2.9 | The irrelevant fact (impulsive): no part, at least 5 of 6 | no part 4 of 6, pushes 2 | **FAIL** (majority right, below the predicted margin) |
| 2.10 | "Whether others will know it was them": a consequence, by a majority, in at least one reason | **a situation the reason needs, 4 of 6, in both reasons** | **FAIL** |
| 2.11 | Parts kappa at least 0.4 | **0.862**; majority matches the key on 65 of 68 slots | **PASS** |
| 2.12 | Reachability: no, no, no, yes | 6/6 no, 5/6 no, 6/6 no, 6/6 yes; kappa 0.808 | **PASS** |

#### P3. Behavioural predictions

| # | Prediction | Kind | Result | |
|---|---|---|---|---|
| 3.1 | A differs from S only in the 25 real ties | analytic | 25, all ties | **PASS** |
| 3.2 | B-parts, B and C differ from A in 4,074 cells (13.3 %): 1,094 none, 1,036, 972 and 972; 32 ties | analytic | exactly | **PASS** |
| 3.3 | 2,889 believer cells (2,882 changed, 7 tied); 91 and 1,094 innocents | analytic | exactly: 1,944 to `take_responsibility`, 627 to `protect`, 311 to `prevent_argument`, 7 ties | **PASS** |
| 3.4 | The condition keeping its weight: 1,185 | analytic | 1,185 | **PASS** |
| 3.5 | B-circ equals A on the frozen file | analytic | 0 cells differ | **PASS** |
| 3.6 | B-Sel0 2,980; B-Sel1 4,074 | analytic | exactly | **PASS** |
| 3.7 | In live cells, B-parts differs from A in at least one | empirical | **1,388 of 25,823 (5.4 %)**: `get_food` 745, `avoid_exposure` 643 | **PASS** |
| 3.8 | In live cells, B forms no intention in at least one | empirical | **272** | **PASS** |
| 3.9 | Of the 1,028 real pantry decisions, B-parts changes none | empirical, weak | **99 of 1,028 (9.6 %)** | **FAIL** |

**Why 3.9 failed.** In the `daniel_ate_it` mornings, Daniel believes the missing
can was his to answer for. When he is matched at another person's pantry-check
for `get_food`, the author's 0.60 weight on that belief makes him form the
theft. Read as a condition, the belief adds no strength, and he takes
responsibility instead. With the weight kept (B-parts+w), no real decision
changes.

#### P4. The expected answer

| Predicted | Result | |
|---|---|---|
| Identity, parts, circumstances (with a vocabulary naming the person concerned and watching, separate from situational pushes), and a representable "no viable intention" are required | all REQUIRED: necessary and legible | right |
| Exclusive is carried by circumstances, and opposed by parts and direction | both REDUNDANT, and both legible (6 of 6 each) | right |
| Reinforcing needs a relation only to stay right after an edit | it does, and readers draw it (5 of 6): **REQUIRED** | right about the reference; wrong that it would not be legible |
| **Only "alternative" needs a relation of its own** | **alternative is UNSUPPORTED.** Only C passes E.2, but readers did not read the pair as "one or the other" | **wrong** |
| | | **PARTLY** |

#### The verdict

| | Predicted | Result |
|---|---|---|
| Verdict | MODIFY | **MODIFY** |
| Why | reinforcement UNSUPPORTED; alternatives REQUIRED, so C carries an unsupported element and B lacks a required one | **alternatives UNSUPPORTED and reinforcement REQUIRED**. C carries two unsupported elements: the alternative relation, and, through parts, the hold-back distinction, whose test of a local hold-back readers contradicted. B lacks the reinforcing reference |

**Scored: the verdict as predicted, by a different route.**

#### Tally

| | Predictions | Pass | Partly | Fail |
|---|---|---|---|---|
| P1 representational | 7 | 6 | 0 | 1 |
| P2 legibility | 12 | 6 | 3 | 3 |
| P3 behaviour | 9 | 8 | 0 | 1 |
| P4 answer | 1 | 0 | 1 | 0 |
| Verdict | 1 | 0 | 1 | 0 |
| **All** | **30** | **20** | **5** | **5** |

#### Not predicted

| Finding | Evidence |
|---|---|
| **Readers locate one-or-the-other in the situation, not in strength, again.** The only alternatives case was read as "never together" or "opposed". Four of six call "whether others will know it was them" a situation the reason needs. The causal-route experiment found the same of its real pairs | section 6; Q4, `quiet_or_open` |
| **A fact that holds back one reason can push another.** Six of six say fear holds back stepping in; four of six say it pushes making sure someone who can help knows. The vocabulary can say this (a fact may have a different part in each reason). The case, as declared, did not | section 6; Q4, `fear_holds_back` |
| **Identical facts pull some readers toward "the same reason".** The critical pair drew 4 of 6 "different", against 6 of 6 in the causal-route experiment's version | section 6 |
| **The first change to reach real decisions.** Reading the declared enabler as a condition changes 99 of 1,028 real pantry decisions and forms no intention in 272 live cells. The relation and role judgments of the causal-route experiment reached none | section 5 |
| **The author's weight on a condition was doing the work of a strength.** Of the 4,074 frozen-file cells the condition reading changes, 2,889 are believers who lose the belief's 0.60, and only 1,185 are innocents | section 4 |
| **One representational failure has no behavioural consequence here.** A's local hold-back is wrong in 4,860 cells of E6 and changes no choice, because of the sweep's correlated attributes | section 1 |

#### Classification

In the report, section 12. It separates representational, semantic and
behavioural conclusions, and is machine-readable in `classification.json`.

---

## annotation/protocol.md

### Reason semantics: the blind annotation protocol

Committed with the predictions, before any reviewer was asked anything.

#### What it is for, and what it is not

The representations B and C can distinguish a condition from a push, a
circumstance from a strength, and one relation between reasons from another only
because somebody declares which is which. Those declarations are modelling
judgments. This task asks two things of each one:

- **Is it legible?** Can a reader see the distinction from a plain description,
  without being told the vocabulary?
- **Is it reproducible?** Do independent readers draw it the same way?

**Reviewer agreement is not truth.** A unanimous panel can be wrong about people.
Agreement is evidence only that a distinction is specified well enough to be
written down and checked. Poor agreement on an item is reported as evidence that
the distinction, or its description, is underspecified.

#### Reviewers

Six fresh Claude Code subagents, one per reviewer, told to use no tools and read
no files:

| Reviewer | Model |
|---|---|
| 1, 2 | opus |
| 3, 4 | sonnet |
| 5, 6 | haiku |

**They are language models, not people.** They share training and may share blind
spots, so their agreement is weaker evidence than agreement among independent
humans would be. The limitation is reported with the results.

Reviewers are never shown:
- the item ids of `items.json`, its sources or its answer key;
- the experiment's vocabulary (reason, part, condition, circumstance, relation);
- its hypotheses or its representations;
- each other's answers.

Each item is shown under a neutral id, `item-NN`, where NN is its position in
`items.json`.

#### Order and orientation

- **Order:** the 21 items are shown in `items.json` order, rotated left by
  3 x (k - 1) for reviewer k.
- **Orientation:** for even-numbered reviewers, Reason 1 and Reason 2 are swapped
  within every two-reason item. Each response file records the rotation and
  whether the reasons were swapped. The analysis maps answers back to
  `items.json` order.
- **Minimal pairs:** the members of each pair (`owning_graded` and
  `owning_conditional`; `settling_graded` and `settling_conditional`;
  `easier_unseen` and `unseen_only`) are 8 to 13 items apart in every rotation,
  and nothing marks them as pairs.

#### The prompt, verbatim apart from the items

> You are helping to check whether descriptions of a person's reasons are clear.
> Each item describes what a person intends and one or two reasons that could
> lead them there, with the facts each reason draws on. Some items also describe a
> particular person. Answer only from the text given. Do not use any tools and do
> not read any files.
>
> For every reason in every item, say what part each listed fact plays in THAT
> reason, using one of:
>
> - `pushes`: the more of it, the stronger this reason
> - `holds_back`: the more of it, the weaker this reason
> - `must_hold`: it must be true of the person for this reason to apply at all
> - `situation_needed`: a feature of the situation this reason needs in order to apply at all
> - `situation_strengthens`: a feature of the situation that makes this reason stronger, but is not needed for it
> - `consequence`: something that follows from acting, not a cause of it
> - `no_part`: it plays no part in this reason
> - `unclear`
>
> For each item with two reasons, also answer:
>
> - **Q1.** Are Reason 1 and Reason 2 the same reason (said twice, perhaps in
>   other words), or different reasons? `same`, `different` or `unclear`.
> - **Q2.** If they are different: in a situation where both could apply, how do
>   they relate? `both_add` (both operate, each adding its own push),
>   `one_strengthens_other` (both operate, but one only strengthens the other and
>   would do nothing on its own), `one_or_other` (the person acts from one or the
>   other, not both), `never_together` (they cannot both apply in the same
>   situation), `opposed` (one pushes the person away from what the other pushes
>   toward), or `unclear`. If they are the same, `not_applicable`.
>
> For each item that describes a particular person, also answer:
>
> - **Q5.** Given what is said about this person, could they form this intention
>   at all, in this situation? `yes`, `no` or `unclear`.
>
> For every item:
>
> - **Q4.** In at most 40 words: what would an explanation need to show for you
>   to understand why this person formed the intention (or did not)?
>
> Reply with JSON only: an array with one object per item, with the fields `id`,
> `parts` (an array with one array per reason, in the order shown, each listing
> one answer per fact in the order shown) and, where they apply, `q1`, `q2` and
> `q5`, and always `q4`.

The parts question is called Q3 in the analysis.

#### Analysis, fixed now

- **Judgment (Q1).** The majority per two-reason item, its share, and whether it
  matches the key. Fleiss' kappa over the ten two-reason items (`same`,
  `different`, `unclear`).
- **Relation (Q2).** The majority per item the key calls different, and whether
  it matches the key. Fleiss' kappa over those eight items (six categories).
- **Parts (Q3).** The majority per (item, reason, fact) slot and whether it
  matches the key. Fleiss' kappa over all slots (eight categories). A confusion
  table of the key's part against the majority's part. The one pre-registered
  ambiguous slot (`answer_key.ambiguous_slots`) is excluded from both, and
  reported on its own.
- **The minimal pairs**, reported on their own:
  - the belief in the two `owning` items: `pushes` in the graded one, `must_hold`
    in the conditional one;
  - the belief in the two `settling` items: the same;
  - watching in `easier_unseen` (`situation_strengthens`) against `unseen_only`
    (`situation_needed`).

  A pair is **discriminated** when both majorities match the key.
- **Reachability (Q5).** The majority per item and whether it matches the key.
  Fleiss' kappa over the four items (three categories), reported with the warning
  that four items make it unstable.
- **Q4.** Reported verbatim. Its themes are coded afterwards by the author, and
  that coding is labelled as the author's.
- **Underspecified.** An item or slot whose majority has fewer than four of six;
  a question whose kappa is below 0.4.

The analysis is computed by `ReasonSemanticsExperimentTests` from the saved
responses, so it can be reproduced from the files alone.

