# Reason semantics: predictions

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

## The question

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

## Hypotheses

| | |
|---|---|
| **H1** | A reason needs a declared identity, independent of rule identity |
| **H2** | A fact inside a reason can be a push or an enabling condition, and these must be represented differently if readers treat them differently |
| **H3** | A reason can depend on a circumstance (someone present or absent, someone watching, the person concerned present or absent), and a circumstance must not be smuggled into a weight |
| **H4** | Reasons for one intention cannot be assumed to add. Which of independent, alternative, reinforcing, opposed and exclusive are actually needed is to be found, not assumed |
| **H5** | An intention with no applicable reason, or no positive support, should not form merely because it is the only candidate; "no viable intention" may need to be representable |

## What is frozen

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

## Vocabulary

| Term | Meaning |
|---|---|
| **fact** | a level read from the person (trait, value, belief) or a feature of the situation |
| **intention** | what the person is trying to accomplish |
| **reason** | a declared explanation, with an identity, of why some facts lead toward (or away from) an intention |
| **part** | what a fact does inside a reason: **push** (the more, the stronger), **hold-back** (the more, the weaker; it can cancel its reason, not reverse it), **condition** (must be true for the reason to apply at all; not a strength) |
| **circumstance** | a feature of the situation a reason needs in order to apply at all; not a strength. A **situational push** makes a reason stronger without being needed |
| **direction** | whether a whole reason leads toward the intention or away from it |
| **relation** | independent (default), alternative, reinforces, exclusive |

## The evaluation space

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

## The representations

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

## The families and the checks

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

## P1. Representational predictions (analytic; `prediction-model.py`)

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

## P2. Semantic and legibility predictions (empirical)

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

## P3. Behavioural predictions

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

## P4. What the answer is expected to be

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

## What would decide the verdict

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
