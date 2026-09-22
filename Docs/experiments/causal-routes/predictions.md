# Causal routes: predictions

Written and committed **before any fixture for this experiment existed**, with
three files that fix everything that could otherwise be fitted to the results:

| File | Fixes |
|---|---|
| `Assets/_Project/Data/Experiments/causal-routes.json` | the route declared for every frozen rule; the synthetic families, rule by rule; the pairs and what each is declared to be |
| `annotation/items.json` | the twelve items shown to reviewers, and the answer key they never see |
| `annotation/protocol.md` | reviewers, order, the prompt verbatim, and the analysis |

Every prediction is marked **analytic** (follows by arithmetic or by
construction; if it fails, the fixture is wrong) or **empirical** (a guess; if
it fails, that is a finding).

## The question

The intention-representation experiment left one decision open. When two
different reasons for one intention read the same fact about a person, should
that fact count once or twice? It showed that no invariant chooses, and that
the answer moves 660 conclusions.

This experiment asks a prior question: **what information does a
representation need to tell "the same reason written twice" from "two different
reasons that depend on the same fact"?** It does not assume either answer, and
it does not choose among formulas.

## What is frozen

| | |
|---|---|
| Rule file | `Assets/_Project/Data/Experiments/intentions.json`, sha256 `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92`, hashed at the start and the end |
| Production | nothing under `Fallow.Core`; no production selector, shipped rule, want, candidate generation, action, scoring, belief, emotion, memory or character data |
| New files | experiment-only: the route declarations, the synthetic families and the annotation. No production vocabulary is added |

## Three things, kept apart

| | What it is | Example |
|---|---|---|
| **Evidence** | a fact about the person or the situation | `trait:empathetic`, `value:control`, `belief:role_claim`, `emotion:anger`, `circumstance:others>=1` |
| **Route** | one declared explanation of why some evidence supports an intention | "I take it on myself to keep them from harm" |
| **Intention** | what the person is trying to accomplish | `protect` |

A **route key** is an experiment-only name for one declared meaning, and
nothing else. It is not a rule id: several rules can carry one route key (a
reason written more than once), and one rule's statements could carry several.
It is not a file position. Renaming every route key consistently must change
nothing, and is tested.

## The representations

| | Identity it reads | A repeat | Different statements of one fact | Relations between reasons | Negative totals | Ties |
|---|---|---|---|---|---|---|
| **A** | none: anonymous rules (the control, `IntentionSelector` bit for bit) | adds | add | none | a rule weighing <= 0 is discarded | by name |
| **B** | the evidence key, per intention (the base keyed by its gate) | once | once, at the strongest; flagged | none | counted | reported |
| **C** | the reason signature: intention, gate, set of evidence keys | once | once per signature, at the strongest; flagged | none | counted | reported |
| **D** | **the declared route**: every statement is (intention, route, evidence, coefficient, sign, role, provenance) | once within a route | **within one route**: a conflict, flagged, resolved at the strongest; **across routes**: each route keeps its own | declared: **independent** routes both contribute (the default); **alternative** routes, only the stronger operates | counted | reported |

**D in detail.**

- **A route's support** is its base plus one term per distinct piece of evidence
  it states.
- **An intention's support** is the sum of its independent routes, with each
  declared group of alternatives contributing only its strongest member.
- **Roles.** A role is `driver` for a positive coefficient and `inhibitor` for a
  negative one, unless declared otherwise; a declared role that contradicts its
  sign is flagged. `enabler` is a declared role that D records but, in its main
  form, computes additively like any other term (see D-enablers below).
- **Suspicion flag.** D flags two *different* routes for one intention that
  state exactly the same evidence at exactly the same coefficients. It does not
  merge them. It says: *confirm these really are two reasons.*
- **Provenance.** Every statement keeps the rules that stated it, and every trace
  runs from intention to route to evidence to coefficient and sign to the level
  read from the person or the world.

**Diagnostics, not candidates:**

- **D-alt**: D with two pairs of frozen routes declared alternatives rather than
  independent (`causal-routes.json`, `what_if_alternatives`). It measures how
  much the relation judgment moves real conclusions.
- **D-enablers**: D honouring the one declared `enabler`. The frozen rule
  `what_you_did_in_the_night` says its intention is "reachable only by somebody
  who believes they are answerable", so under D-enablers its route contributes
  nothing when that belief is absent. It measures how much the role judgment
  moves real conclusions.
- **G**: a negative control for evidence reuse. G gives each fact only to the
  intention that states it most strongly, so that the reuse test can be seen to
  fail when it should.

## The synthetic families

Every variant is written out rule by rule in `causal-routes.json`. Each is
evaluated for `look_after`, in company, over the 2,187 sweep profiles. The rivals
are the frozen `so_that_they_know_too` and `not_making_a_scene_of_it`,
unchanged. The focal route `duty` is base 0.10, `trait:empathetic` 0.40,
`value:closeness` 0.25.

| Family | Variants | Declared |
|---|---|---|
| **A** pure restatement | A0 `duty` once. A1 twice. A2 reworded (terms reversed, new id). A3 at 0.99. A4 partly. A5 as two rules, split by term. A6 with its key renamed | all the same reason as A0 |
| **B** different reasons, same facts | B1: `duty` and `compassion`, **identical in content to A1**. B3: B1 reordered, rules renamed, keys renamed | B1 is two reasons; A1 is one reason twice |
| **C** same fact, different intentions | C0: `duty` and `telling_them_gently` (`share_information`: base 0.05, empathetic **0.50**, honest 0.20). C1: `duty` alone | protect's support must not depend on whether empathy also supports sharing |
| **D** several facts in one reason | D0: `guardian`, one reason on empathy, family safety and closeness. D1: three single-fact reasons with the same total. D2: D0 as three rules. D3: D0 partly restated. D4: D1 with one reason restated | D0 = D2 = D3; D1 = D4; D0 and D1 have the same numbers and a different structure |
| **E** same fact, different strength or role | E1: `duty` also stated at empathy 0.30 in the same route. E2: `duty` and `compassion_distinct` (empathy 0.30, family safety 0.35). E3: E2 with the two declared alternatives. E4: `duty` and `overwhelmed` (empathy **-0.20**) | E1 is malformed (one reason, two strengths). E2 is two reasons. E3 is the same two, only one operating. E4 is a driver and an inhibitor |

**What passing means, fixed now:**

| Declared | Passes if |
|---|---|
| same | protect's support is identical in every cell, **and** the representation's explanation is identical (after undoing a declared renaming) |
| different | protect's support differs in some cell |
| structure (D0, D1) | support identical in every cell, **and** the explanation differs |
| malformed (E1) | the representation flags it |
| reuse (C0, C1) | protect's support identical in every cell |

An explanation is each representation's own attribution of the score, without
provenance:

- A: its anonymous rules and their amounts;
- B: evidence and amounts;
- C: reason signatures and amounts;
- D: routes, then evidence and amounts.

## The theorem, committed in advance

**No representation that ignores rule ids and reads no declared route can pass
the critical pair.** A1 and B1 are the same rule file except for rule ids, notes
and declared routes. A representation invariant to rule ids (R2) that does not
read notes or routes computes the same thing on both. So:

- A treats both as two contributions;
- B and C treat both as one reason;
- only D can treat A1 as one reason and B1 as two.

**Analytic.** If A, B or C passes the critical pair, the fixture is wrong.

## Predictions

### P1. The families (analytic)

| Pair | Declared | A | B | C | D |
|---|---|---|---|---|---|
| A0 A1 | same | fail | pass | pass | pass |
| A0 A2 | same | fail | pass | pass | pass |
| A0 A3 | same | fail | pass | pass | pass |
| A0 A4 | same | fail | pass | **fail** (a partial copy is a new signature) | pass |
| A0 A5 | same | fail (the explanation has two rules) | pass | fail (two signatures) | pass |
| A0 A6 | same | pass | pass | pass | pass |
| **A1 B1** | different | **fail** | **fail** | **fail** | **pass** |
| A0 B1 | different | pass | fail | fail | pass |
| B1 B3 | same | pass | pass | pass | pass |
| C0 C1 | reuse | pass | pass | pass | pass |
| D0 D2 | same | fail | pass | fail | pass |
| D0 D3 | same | fail | pass | fail | pass |
| D1 D4 | same | fail | pass | pass | pass |
| D0 D1 | structure | pass (by rule count) | **fail** (its three equal bases collapse into one) | pass | pass |
| A0 E1 | malformed | fail | pass | pass | pass |
| A0 E2 | different | pass | pass | pass | pass |
| E2 E3 | different | fail | fail | fail | pass |
| A0 E4 | different | **fail** (the discard drops the inhibitor) | **fail** (the strongest statement drops the inhibitor) | pass | pass |
| **Passed, of 18** | | **6** | **13** | **11** | **18** |

Four of those are worth stating in words:

- **B cannot hold an inhibitor** that shares evidence with a driver of the same
  intention: its conflict rule keeps the larger magnitude. **A cannot either**,
  because the discard removes a rule that weighs nothing or less.
- **B's base-by-gate identity makes three single-fact reasons with equal bases
  collapse into one base.** This is the untested consequence the representation
  experiment named. Here it is tested.
- **C takes how statements are grouped into rules for how they are grouped into
  reasons.** So it is fooled by a reason written as two rules (A5, D2) as well
  as by a partial copy (A4, D3).
- **G fails C0 C1**, because it moves empathy from `protect` to
  `share_information` (0.50 against 0.40). If it did not fail, the reuse test
  would be toothless.

**Agreement with the declared structure** (D's outcome), per variant, is
reported for A, B and C. *Empirical* in its counts. Analytically: A disagrees
wherever a reason is restated; B wherever two routes share a fact; C wherever a
partial copy or a split appears. None of them can represent E3.

### P2. The frozen file (analytic unless marked)

| # | Prediction |
|---|---|
| 2.1 | **D reaches the same outcome as C in every cell, and as A in every cell but the 25 real ties**, because every frozen rule is declared its own route and no two are declared alternatives. So D keeps what A and C conclude in the 660 cells where B differed. **By D's declarations, those were cells where B merged two different reasons.** Whether the declarations are right is what the annotation tests |
| 2.2 | D passes the retained invariants on the frozen sweep: R1, R2, R3 (ties reported), R4a to R4d (0), R5 (changed, all flagged), R6 (responds), R7 (0 away), R8 (0 outside), R9a and R9b (0), R10 (0) |
| 2.3 | **R11, route-key renaming**: 0 changes |
| 2.4 | **A copy declared as a new route** behaves exactly like A without the discard: the same 20,021 changes. **And D's suspicion flag fires in every cell where the copy applies**, so the change is never silent. D is only as good as its declarations, and it says so |
| 2.5 | **R15, provenance**: in every cell, the winner's trace, from route to evidence to coefficient to level, reconstructs its score to within 1e-9, and every statement names the rule that stated it |
| 2.6 | D keeps everything proven: 28.6 % single-candidate, blindness 0, exact replay, no character names, fixed-candidate sensitivity 6.1 % |
| 2.7 | *Empirical.* **D-alt moves more than 1,500 cells.** Declaring `standing_in_the_way` and `shielding_from_afar` alternatives takes protect toward the one-best-reason figure (45.9 % in `look_after` in company). Declaring the two authority routes alternatives takes `assert_authority` down in `guard_supplies` and `restore_standing` in company. **The relation judgment moves more conclusions than B's collapse did** |
| 2.8 | **D-enablers changes exactly the cells where an innocent profile (no `answerable_for` belief) formed `took_what_was_not_mine` against a rival**, and nothing else. *Empirical*: between 91 and 182 cells. **Where the theft is the only candidate (`avoid_exposure` alone), the 1,094 innocent profiles still "form" it, now with zero support**, and D-enablers flags each as an intention formed for no reason. That is a question for selection that no representation here answers |

### P3. Real mornings

The same 50 baseline mornings, 257 pantry-checks and 771 matched pairs.

| # | Prediction | Kind |
|---|---|---|
| 3.1 | D forms the same intentions as A in real pairs: 486 of 771 differ between people | analytic (no real ties expected) |
| 3.2 | Among the 285 pairs forming the same intention, the **leading route** differs in fewer than 20 %, while the evidence differs in all 285 | empirical |
| 3.3 | One rule copied, or partly copied, **within its route**: D changes 0 real intentions and 0 stated reasons, across 5,140 re-decisions | analytic |
| 3.4 | One rule copied **as a new route**: D changes 110 real intentions, like A, and flags every one | analytic |
| 3.5 | D-alt changes 0 real pantry decisions: the real `assert_authority` cases are Daniel's, and he wins with either relation | empirical, weak |
| 3.6 | D-enablers changes at least one real decision: an innocent person forming the theft | empirical |

### P4. The annotation

| # | Prediction | Kind |
|---|---|---|
| 4.1 | Both controls: 6 of 6 reviewers match the key | empirical |
| 4.2 | Both synthetic restatements: at least 5 of 6 say restatement | empirical |
| 4.3 | The critical pair: at least 5 of 6 say different | empirical |
| 4.4 | Each real pair: a majority says different; the authority pair, which shares two facts, least firmly | empirical |
| 4.5 | Fleiss' kappa for the judgment, over the eleven two-reason items: at least 0.6 | empirical |
| 4.6 | **Q3, whether two different reasons combine or compete: kappa below 0.4.** The relation between reasons is harder to judge than their identity | empirical |
| 4.7 | The competing item (`syn_alternative`): a majority says one or the other | empirical |
| 4.8 | The role item: at least 5 of 6 say precondition | empirical |
| 4.9 | Majority judgments match the key on at least 10 of 11 two-reason items | empirical |

### P5. The answer, stated in advance

**More explicit causal structure is required.** The critical pair cannot be told
apart by anything computed from the rules' contents.

- **What distinguishes them is a declared route identity.** It is independent of
  rule ids, order, wording and grouping.
- **It is not enough on its own.** A representation also needs the declared
  relation between routes (independent or alternative), and the declared role
  of each fact within a route (driver, inhibitor or enabling condition).
- **Each of these is a modelling judgment.** The data cannot supply any of them.

## What would decide the verdict

The verdict is about the representation, not about Fallow. Committed now:

| Verdict | If |
|---|---|
| **KEEP** (explicit causal routes, as D defines them) | D passes the retained and the new invariants. A, B and C fail the critical pair. D passes every family. D keeps what was proven. **And** the judgments D needs are reproducible: judgment kappa at least 0.6, Q3 kappa at least 0.4, the majority matching the key on every real pair. **And** no family shows a declared meaning D cannot compute |
| **MODIFY** | D does all it is built for, but a needed piece of causal structure is missing or unreliable: a declared role D's statement form cannot compute (the enabler), a relation judgment reviewers cannot reproduce, or route identities that reviewers do not see as declared |
| **REBUILD** | the intention architecture cannot carry route identity without breaking what is proven: D fails the stage separation, R1 to R10, or generalization |
| **ABANDON** | no representation can tell the critical pair apart, even with declarations |

**My expectation is MODIFY.** The enabler is expected to be both real (it is
the documented "innocent theft" defect) and uncomputable by additive
statements. And the relation between reasons is expected to be poorly
reproducible.

**Not claimed by any outcome:** that any route declaration, relation or role is
psychologically correct. Passing an invariant proves a property of the
representation. Reviewer agreement shows legibility. Neither shows how people
are.
