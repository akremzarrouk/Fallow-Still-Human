# Reason semantics: what a simulated reason has to contain

*What must a simulated reason contain so that the system can tell genuinely
different causal explanations apart, without silently turning conditions into
weights, circumstances into hidden gates, or competing reasons into arbitrary
score arithmetic?*

## 1. The answer, first

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

## 2. What was run

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

## 3. The vocabulary and the representations

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

## 4. Representational results

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

## 5. Semantic and legibility evidence

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

## 6. Which relations are needed

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

## 7. No viable cause

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

## 8. Behaviour

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

## 9. Provenance

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

## 10. What a reason has to contain, and what remains a choice

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

## 11. Limitations

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

## 12. Classification

### Representational

| | |
|---|---|
| **PROVEN** | S is the shipped selector (0 of 336,798 cells). The families pass as predicted in all 186 counts; S 9, A 14, B-parts 22, B-circ 23, B 29, C 31 of 31. Identity alone passes restatement and the critical pair. Parts are needed for conditions (10,935 cells per case otherwise) and for telling a hold-back from a reason against (S and A each get exactly one of the two). Circumstances are needed whenever the shipped gate cannot say them (4,374 cells per case). Exclusive is carried by circumstances, and opposed by parts and direction. A reinforcement expressed by a copied gate passes only through the copy, and fails after one edit (1,458). No viable cause has three sources, needing compatibility, applicability and a positive-support rule, respectively; the shipped discard is split-dependent (5,060). Every negative control is 0. PV1 holds for all 2,755,620 outcomes |
| **PLAUSIBLE** | That B plus a reference relation is the smallest vocabulary expressing every required distinction. It is the smallest tested, on 28 synthetic cases |
| **UNPROVEN** | That "alternative" needs a relation at all. The combination rule, the hold-back floor and the viability threshold as declared |
| **FAILED** | S and A as representations of reasons. Copying as a substitute for reference. PV2 as implemented, for every representation |

### Semantic and legibility

| | |
|---|---|
| **PROVEN** (as legibility, among language-model readers) | Identity (kappa 0.851, 10 of 10); condition against push, including all three minimal pairs (kappa 0.862, 65 of 68 slots); circumstance, including the person concerned and watching, and gate against situational push; reinforcement (5 of 6); exclusive and opposed (6 of 6 each); unreachability without a viable cause (4 of 4, kappa 0.808) |
| **PLAUSIBLE** | That readers read exclusion through circumstances, not strength (two experiments, few items). That a fact can hold back one reason and push another (4 of 6, one item) |
| **UNPROVEN** | That any of it holds for human readers |
| **FAILED** | "Alternative", as declared (1 of 6). "Whether others will know it was them" as a consequence (readers: a needed situation, 4 of 6). A hold-back with no part in the other reason (readers: it pushes, 4 of 6) |

### Behavioural

| | |
|---|---|
| **PROVEN** | On the frozen file, the condition reading changes 4,074 cells (13.3 %), 2,889 of them because the belief loses its weight; keeping the weight changes 1,185. In real mornings it changes 99 of 1,028 real decisions and 1,388 of 25,823 live cells, and forms no intention in 272. On the synthetic cases, B differs from C in 1.5 % of choices, S in 16.6 % |
| **PLAUSIBLE** | That the real-decision changes generalize beyond one character in one morning variant |
| **UNPROVEN** | That any changed choice is better. Whether "no intention" is the right outcome, or what a person does then |
| **FAILED** | The prediction that no real decision would change (3.9) |

## 13. Recommendation

# MODIFY

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

## 14. The question, in plain language

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
