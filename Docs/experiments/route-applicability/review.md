# Route applicability: review

*What causal information must a route contain to decide whether it applies in
the current situation, before its supporting and inhibiting evidence is
combined?*

This is a representation experiment. Nothing was implemented.

## 1. The answer, first

**A route needs one more layer than it has, and only one:** a set of conditions
under which it applies at all, kept apart from what makes it stronger.

- **What the layer must be able to express:**
  - a fact about the person that must hold;
  - a fact about the situation that must hold;
  - a situation fact that concerns the want's target (Mara, whoever she is in a
    given case), distinct from one that anyone at all satisfies.
- **The shape of the layer:**
  - **one construct, not two.** Conditions and circumstances behaved
    identically in every one of 209,952 cells. Readers give them different
    names ("prerequisite", "circumstance") and the same behaviour ("the reason
    disappears");
  - **declared per route, not inferred** from the kind of fact.
- **What stays outside it:** once a route applies, support and inhibitors change
  only its strength, never whether it applies.

The evidence, in short:

| | A: the causal-route D | B: typed roles | C: applicability layer |
|---|---|---|---|
| Route-layer families passed, of 10 | 3 | 6 | **10** |
| Prerequisite read as a weight (family A) | 26,244 false activations of 52,488 (50.0 %) | 0 | 0 |
| "Someone present" standing in for "Mara present" (family D) | 17,496 of 39,366 (44.4 %) | 17,496 (44.4 %) | 0 |
| "No applicable route" representable (family G) | no | for conditions only | yes |
| The causal-route experiment's 18 pairs | 18 of 18 | 18 of 18 | 18 of 18 |

**Every element of C was tested for need and for over-reach.** Each element
failed when removed:
- without target binding (C-entity): C, D, G and J fail;
- without conditions (C-conditions): A, B and G fail.

Each also failed when applied by the kind of fact instead of by declaration
(C-kind). Reading every belief as a precondition breaks the case where a belief
is only support. Binding every presence to the target breaks the case where
anyone will do.

Six blind readers drew every one of these distinctions the way it was declared
(facts kappa 0.931, Q7 0.891).

**What it changes in behaviour: on real mornings, nothing that is its own.**
- C and B change the same 99 of 1,028 real decisions.
- All 99 come from one modelling choice: a precondition adds no strength. With
  the weight kept, none change.
- The circumstance and target machinery changes thousands of synthetic cells
  and no real decision. No frozen rule declares a circumstance the shipped gate
  cannot already say.

**Two questions this experiment cannot settle, and should not:**
- **What the deliberator should do when no route applies.** Where "does not
  apply" is recorded already decides behaviour. Readers were unanimous that
  such an intention is not causally supported.
- **How to treat "applies, but pushes with nothing".** The representation keeps
  it as its own state; no reader recognised it.

These are the next experiment.

## 2. What was run

| | |
|---|---|
| Frozen | `intentions.json`, `causal-routes.json`, `held-out-people.json`, `reason-semantics.json`, `route-applicability.json`, and the fixtures `CausalRouteExperimentTests.cs`, `ReasonSemanticsExperimentTests.cs` and `IntentionSelector.cs`, all sha256-checked at the start and the end: **unchanged** (hashes in `protocol.md` and `measurements.md`) |
| Production | **nothing changed**. The causal-route fixture, with D, its 18 families, the critical pair and its rewrite and provenance tests, still runs unchanged in the suite |
| Committed first | `431db11`: predictions, protocol, 16 cases in ten families, the reading rules, two selection policies, D's published counts, an independent prediction model, and 16 annotation items with their key |
| Representations | S (the shipped selector), A (D), B (typed roles), C (applicability layer), and four ablations of C |
| Evaluation | 2,187 profiles x 6 presence sets (nobody; Mara; Daniel; Elena; Daniel and Elena; Mara and Daniel) = 13,122 cells per case and condition |
| Behaviour | the frozen file (30,618 cells); 50 real mornings (1,028 real decisions, 25,823 live cells) |
| Annotation | 6 blind language-model reviewers, 16 items, 9 questions each. Human reviewers were not available; the result is legibility evidence only |
| Fixture | `RouteApplicabilityExperimentTests`, **8 of 8 pass**, 28 minutes. No randomness |
| Predictions | 21 of 24 pass, 2 partly, 1 fails (`results.md`) |

## 3. The route layer

Errors against the declared meaning. FA: the representation applies a route
that should not apply. FS: it suppresses one that should.

| Family | Cells | S | A | B | C | C-entity | C-conditions | C-split | C-kind |
|---|---|---|---|---|---|---|---|---|---|
| A prerequisite absent/present | 52,488 | 26,244 FA | 26,244 FA | 0 | 0 | 0 | 26,244 FA | 0 | 0 |
| B prerequisite against evidence | 52,488 | 26,244 | 26,244 | 0 | 0 | 0 | 26,244 | 0 | **26,244** |
| C circumstance switch | 39,366 | 10,935 FA | 10,935 FA | 10,935 FA | 0 | 10,935 FA | 0 | 0 | 0 |
| D target-specific presence | 39,366 | 17,496 FA | 17,496 FA | 17,496 FA | 0 | 17,496 FA | 0 | 0 | 0 |
| J target against generic | 26,244 | 6,561 FA | 6,561 FA | 6,561 FA | 0 | 6,561 FA | 0 | 0 | **6,561 FS** |
| E support varied: applicability changed | 26,244 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| F inhibitor varied: applicability changed | 13,122 | **13,122** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| G wrong route-layer state | 52,488 | 17,493 | 13,125 | 6,561 | 0 | 6,561 | 6,564 | 0 | 0 |
| H irrelevant facts changed something | 588,303 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **6,561** |
| I causal-route controls failed | | many | I.4 (13,122) | 0 | 0 | 0 | 0 | 0 | 0 |
| **Families passed, of 10** | | **2** | **3** | **6** | **10** | **6** | **7** | **10** | **7** |

**What each row shows:**

- **Typed roles alone (B) fix preconditions and nothing else.** B reads
  "believes they are answerable" as a prerequisite, so an innocent person's
  theft route no longer applies (A, B, G). But B still takes "someone is
  present" for "Mara is present": 17,496 false activations when only Daniel,
  only Elena, or both are there.
- **Only a circumstance that can name the target distinguishes the four
  presence sets of family J.** For `protect(Mara)` with Mara present, Daniel
  present, Elena present or nobody present:
  - C applies the route exactly when Mara is present;
  - A, B and C-entity also apply it when only Daniel or only Elena is there;
  - `scene_mara`, whose circumstance really is "anyone", is applied by C with
    Daniel or Elena present.
  The same declared route with Daniel or Elena as the target follows its own
  target (0 errors), and no name appears in any route.
- **Applicability is separate from strength in every representation but the
  shipped selector.** Varying support or an inhibitor changed only strength,
  across 26,244 and 13,122 profile-situations. The shipped selector's discard
  turns the inhibitor into a switch in all 13,122: enough fear, and the rule
  disappears. It also turns "applies, with zero strength" into "no candidate"
  (4,368 cells).
- **An inhibitor never becomes a route or a prerequisite in B or C.** The route
  still applies at the highest fear. Its strength falls by exactly 0.60 per unit
  of fear, and goes to zero or below in 17,496 of 39,366 evaluations. That is
  reported, not floored.

## 4. Condition and circumstance: one construct

The brief asked whether conditions and circumstances are different concepts, and
said not to assume it. Two tests address it:

- **Behaviour.** C-split (conditions and circumstances as separate constructs,
  circumstances placed at candidacy as the shipped gate does) was compared with
  C (one construct at the route). Their route applicability differs in **0 of
  209,952** cells. They differ only in *where* a failed circumstance is
  recorded: "no candidate" rather than "candidate with no applicable route", in
  39,366 cells.
- **Readers.** Readers label a belief the reason needs a `prerequisite` (6 of 6,
  on three items) and a presence it needs a `circumstance` (6 of 6, on seven
  items). But when either changes, they say the reason **disappears**, by
  majorities of 4 to 6 of 6 on every item.

So the two differ in **what they read** (the person, or the situation) and in
**what they are called**. They do not differ in **what they do**. A single
applicability construct (a conjunction of predicates, each about the person or
the situation, each optionally bound to the target) expresses every case here.

The one real difference is placement, and placement is a selection question
(section 6).

## 5. Behaviour

**On the frozen file** (30,618 cells), read with the causal-route declarations
and nothing new:

| | Differs from A (P0) | No intention | Ties |
|---|---|---|---|
| B, P0 | 2,980 (9.7 %) | 0 | 32 |
| B, P1 | 4,074 (13.3 %) | 1,094 | 32 |
| C, P0 | 4,074 (13.3 %) | 0 | **1,126** |
| C, P1 | 4,074 (13.3 %) | 1,094 | 32 |
| C-split | as B | as B | as B |
| B with the condition keeping its weight | 91 / 1,185 | 0 / 1,094 | 25 |

**In real mornings:**

| | B | C | C-split | B+w |
|---|---|---|---|---|
| Real decisions whose intention changed, of 1,028 | 99 | 99 | 99 | 0 |
| Real decisions whose explanation changed, the act not | 3 | 3 | 3 | 102 |
| Real decisions with no intention | 0 | 0 | 0 | 0 |
| Live cells changed, of 25,823, P0 / P1 | 1,116 / 1,388 | 1,388 / 1,388 | 1,116 / 1,388 | 40 / 312 |
| Live cells with no intention (P1) or tied at zero (C, P0) | 272 | 272 | 272 | 272 |

- **The 99 real decisions are all the same event.** Daniel, in the mornings
  where he ate the can, is matched at others' `get_food` pantry-checks. Read as
  a pure prerequisite, his belief that he is answerable adds no strength, so he
  takes responsibility instead of owning a theft.
- **None of the 99 is a regression of the representation.** Each traces to one
  declared reading, and disappears when the condition keeps its weight.
- **The applicability layer contributes nothing of its own to real behaviour.**
  C and B change the same number of real decisions, and under P1 the same
  number of live cells. A representation that changes 17,496 synthetic cells in
  family D and no real decision is telling us something: the real rule file
  does not yet contain a route whose meaning needs it.

## 6. What the selection layer will have to decide

This was measured, not judged.

- **A candidate with no applicable route can still be chosen under P0.** Under
  C, `protect(Mara)` forms in all 8,748 cells of `only_side_mara` where Mara is
  absent. On the frozen file, 1,094 innocent people alone tie three intentions
  at zero support. In live cells, 272 do.
- **C-split does neither.** It records a failed circumstance at candidacy, as
  the shipped gate does, so the intention is not a candidate. **Where "does not
  apply" is recorded is already a selection policy.**
- **Readers answer part of the question.** They say an intention with no
  applicable route is not causally supported (Q9, 6 of 6, on both kinds). And
  they say the same of a route that applies but pushes with nothing: 6 of 6 say
  it does not apply at all, and 6 of 6 that the intention is not causally
  supported. The representation keeps "applicable, strength zero" as a state of
  its own. Readers do not recognise it.

## 7. The blind annotation

| Question | Majority matches the key | Fleiss' kappa |
|---|---|---|
| Q1 does the reason apply | 14 of 16 | 0.834 |
| Q3 to Q6 the part each fact plays | 46 of 46 | 0.931 |
| Q7 does applicability depend on a particular person | 15 of 16 | 0.891 |
| Q8 if the named fact changed: disappear, weaker or no change | 16 of 16 | 0.727 |
| Q9 still causally supported when the only route does not apply | 3 of 3 | undefined (18 of 18 answered `no`) |

The misses:
- `zero_support` (readers: does not apply, 6 of 6);
- `evid_absent` (no 3, yes 2, unclear 1);
- `duty_absent` Q7, split 3 and 3 between "no circumstance" and "Mara". All six
  agreed that her presence plays no part and changes nothing, so the question
  conflated "about Mara" with "depends on her presence".

**The reviewers are language models, not people**, and the author declared the
cases, wrote the items and wrote the key. Agreement shows that the distinctions
can be written down and read back consistently. It says nothing about how people
decide.

## 8. Limitations

- **Every route is declared by the author.** The checks prove what a
  representation does with a declaration, not that the declaration is right.
- **Only binary circumstances** (presence) and **binary conditions** (beliefs)
  were tested. A graded condition would need a threshold, which is a modelling
  choice this experiment avoided.
- **Presence is the only situation fact.** Watching, time, place and objects
  were not tested.
- **The target is the want's target.** Circumstances about other roles (the
  person one is hiding from, the owner of the can) were not tested.
- **Route combination was deliberately not tested.** Every new case has one
  focal route. The 18 inherited pairs keep D's combination unchanged.
- **The sweep's attributes are correlated.** Values and beliefs follow the
  profile index, so some combinations never occur.
- **The real-morning sample has no route whose meaning needs the new layer**,
  so it cannot show that layer's behavioural value.
- **The reviewers are language models.** A human panel is the obvious next check
  of legibility.

## 9. Conclusions

### PROVEN

- A single applicability layer (C) expresses every declared distinction tested
  here: all ten route-layer families, with 0 false activations and 0 false
  suppressions. It does so with no name in any route: the same route with three
  targets follows each.
- A (the causal-route D) and B cannot. Treating a prerequisite as a weight
  activates the route in all 26,244 prerequisite-absent cells. Generic presence
  activates a target-bound route in 17,496 of 39,366 cells.
- Each element of C is needed, and needs to be declared:
  - removing target binding fails C, D, G and J;
  - removing conditions fails A, B and G;
  - inferring roles from the kind of fact fails the evidence counterexample
    (26,244), the generic-presence counterexample (6,561) and an irrelevant-fact
    control (6,561).
- Conditions and circumstances behave as one construct: C and C-split never
  differ in applicability (0 of 209,952).
- In A, B and C, support and inhibitors change strength and never
  applicability. The shipped selector's discard is the only thing here that
  turns an inhibitor into a switch (13,122 of 13,122).
- The causal-route experiment's invariants survive every representation: 18 of
  18 pairs reproduced exactly; restatement, reordering, renaming and regrouping
  change nothing; copies and ambiguous declarations are flagged.
- On real mornings, the new layer changes no decision of its own. The 99
  changed real decisions all come from the precondition carrying no weight, and
  none change when it keeps its weight.

### PLAUSIBLE

- That one construct with target binding is the smallest applicability layer
  that will serve the real rules. It is the smallest tested, but on 16 synthetic
  cases and one real rule file that exercises none of its circumstances.
- That readers' "applies" means "applies and pushes". Two items point that way
  (`zero_support`, `evid_absent`), and Q9 was unanimous.

### UNPROVEN

- What the deliberator should do when no candidate has an applicable route, or
  only routes that push with nothing.
- Whether a precondition should also carry strength when it holds. Only this
  choice moves real decisions (99 against 0).
- Circumstances beyond presence, conditions beyond held beliefs, and targets
  beyond the want's own.
- Whether any of it describes people.

### FAILED

- A (the causal-route D) as a representation of applicability: 3 of 10
  families.
- B (typed roles without applicability): 6 of 10; blind to whom a circumstance
  concerns.
- The shipped discard as a notion of "does not apply": it conflates strength
  with applicability (families F and G).
- The prediction that no irrelevant fact would change anything under any
  representation (C-kind, H.5).

### OVERFITTING RISKS

- **Target binding was tested on one predicate** (the target's presence) and
  one kind of target. A route about someone other than the want's target (a
  witness, a rival) would need binding to that role, and nothing here shows the
  construct generalises to it.
- **The circumstance cases were authored with their answer in mind.** Their
  counterexamples (generic presence, no circumstance, an unrelated person) guard
  against over-application, but all were written by the same author, in the same
  vocabulary.
- **"One construct" rests on presence and belief**, both binary. A graded or
  temporal circumstance ("has been alone for an hour") might need something a
  conjunction of predicates cannot say.
- **The layer changed no real decision**, so there is no behavioural evidence
  that it is needed, only representational evidence that it is sufficient.

### KEEP

- Route identity and the causal-route invariants: restatement counted once,
  flags for copies and ambiguity.
- D's arithmetic once a route applies.
- The shipped compatibility stage as it is: circumstances there are
  person-independent, and no change to a person changes what is possible.

### MODIFY

- Give a route an applicability layer: one conjunction of predicates over the
  person and the situation, where a situation predicate names either the want's
  target or anyone.
- Declare roles per route (prerequisite, support, inhibitor); never infer them
  from the kind of fact.
- Record applicability separately from strength. An inhibitor is never a
  switch.

### REBUILD

- **Nothing.** Every distinction was expressed over the existing stages, and
  every earlier invariant held.

### ABANDON

- **Conditions and circumstances as separate constructs.** They never behave
  differently. Keep the words as documentation of what a predicate reads.
- **Generic presence as a stand-in for a particular person's presence.**
- **The discard of rules weighing zero or less** as a way of saying "does not
  apply".

### NEXT EXPERIMENT

**The selection layer: what should a person do when none of their candidate
intentions has an applicable route, or only routes that push with nothing?**

The smallest version holds the route layer fixed as C and compares only
selection policies, including:
- P0;
- P1;
- recording failed circumstances at candidacy (C-split);
- treating "applicable, strength zero or less" as unsupported.

Run it on the three states the route layer can report (no candidate, no
applicable route, applicable without push) and on the real mornings' 272 live
cells. Ask blind human readers, not only models, what a person with no
supported intention does. The precondition-weight choice (99 real decisions)
should be decided alongside it, because it is the only choice here that moves
real behaviour.

**Nothing has been implemented. This is a recommendation about vocabulary, not
architecture.**

---

Reproduce with `./run-tests.sh` or, for the fixture alone,
`unity test . --mode EditMode --filter RouteApplicabilityExperimentTests` (about
30 minutes); the analytic predictions with
`python Docs/experiments/route-applicability/prediction-model.py`.

**Suite: 456 tests, 454 pass, 2 fail.** The 2 failures are the regressions S1.4 left, unchanged:
the pacing gate, still 7 on Model A, and the emergent-moment fading check. The 448 before
this experiment, plus its eight, is exactly 456. The causal-route fixture (D, its 18
families, the critical pair, its rewrite and provenance tests) and the reason-semantics
fixture ran unchanged and passed.

This experiment's measurements, regenerated inside the suite, are byte-identical to the
fixture's own run. Every other generated document regenerated with identical content,
apart from the wall-clock seconds in the decision-sensitivity results and one file that
differed in line endings only.

The suite took 186 minutes, run from a copy of `run-tests.sh` with its timeout raised to
four hours; the script itself was not changed.
