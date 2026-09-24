# Route applicability: predictions

Written and committed **before the fixture existed and before any reviewer was
asked anything**, together with:
- `protocol.md`: the frozen hashes, the representations, the metrics, the
  real-morning procedure and the annotation protocol;
- `Assets/_Project/Data/Experiments/route-applicability.json`: every case,
  reading rule and family;
- `annotation/items.json`: 16 items and their answer key;
- `prediction-model.py`: an independent Python reading of the same files, which
  produced every analytic count below.

Every prediction is marked either **analytic** or **empirical**:
- **analytic:** it follows from the reading rules by arithmetic. If it fails,
  the fixture or the model is wrong.
- **empirical:** it is a guess. If it fails, that is a finding.

## What this experiment is, and is not, about

Two earlier experiments bear on it:
- **The causal-route experiment** showed that a route identity is necessary.
- **The reason-semantics experiment** found that a condition cannot be written
  as a weight, and that the gate cannot say "the person concerned is present".

This experiment asks whether those distinctions are:
- **real:** each can be falsified, and some representation without it fails;
- **general:** an over-applied version of each fails a counterexample;
- **minimal:** whether condition and circumstance are two constructs, or one.

It also separates two questions the reason-semantics experiment joined:
- **Does the route apply?** (the route layer);
- **What should the deliberator do when nothing applies?** (the selection layer).

## The hypothesis, and what could falsify it

> A route needs `intention -> route -> applicability -> support and inhibitors -> strength`,
> where applicability can depend on conditions and circumstances.

| Distinction | Falsified if |
|---|---|
| Applicability is separate from strength | varying only support or an inhibitor changes whether a route applies (E, F) in the representation that has both |
| A condition is not a weight | C-conditions (conditions read as weights) passes A, B and G |
| A condition is a declared role, not a kind of fact | C-kind (every belief a condition) passes B's counterexample |
| A circumstance can concern a particular person | C-entity (presence only generic) passes D and J |
| Target presence is not the only kind of presence | C-kind (every presence bound to the target) passes J's generic route |
| **Condition and circumstance are different constructs** | **C-split (two constructs) behaves differently from C (one construct) at the route layer. Predicted: it does not** |
| "No applicable route" is representable | C fails G |

## P1. The route layer, family by family (analytic)

Cells in which the representation's applicability disagrees with the declared
meaning. FA: false activations. FS: false suppressions. The share is of
route-cells.

| Family | Route-cells | S | A | B | C | C-entity | C-conditions | C-split | C-kind |
|---|---|---|---|---|---|---|---|---|---|
| **A** condition absent/present | 52,488 | 26,244 FA (50.0 %) | 26,244 FA (50.0 %) | 0 | 0 | 0 | 26,244 FA (50.0 %) | 0 | 0 |
| **B** condition vs evidence (cells not read as declared) | 52,488 | 26,244 (50.0 %) | 26,244 (50.0 %) | 0 | 0 | 0 | 26,244 (50.0 %) | 0 | **26,244 (50.0 %)** |
| **C** circumstance switch | 39,366 | 10,935 FA (27.8 %) | 10,935 FA (27.8 %) | 10,935 FA (27.8 %) | 0 | 10,935 FA (27.8 %) | 0 | 0 | 0 |
| **D** person-specific circumstance | 39,366 | 17,496 FA (44.4 %) | 17,496 FA (44.4 %) | 17,496 FA (44.4 %) | 0 | 17,496 FA (44.4 %) | 0 | 0 | 0 |
| **J** target against generic | 26,244 | 6,561 FA (25.0 %) | 6,561 FA (25.0 %) | 6,561 FA (25.0 %) | 0 | 6,561 FA (25.0 %) | 0 | 0 | **6,561 FS (25.0 %)** |

Per case, in the circumstance families:

| Case | Declared | A, B, C-entity | C, C-split, C-kind |
|---|---|---|---|
| `side_mara` | Mara present | 6,561 FA (Daniel, Elena, or both, without Mara) | 0 |
| `side_daniel` | Daniel present | 4,374 FA | 0 |
| `side_elena` | Elena present | 6,561 FA | 0 |
| `away_mara` | Mara absent | 4,374 FA (A, B: no gate can say it; C-entity: dropped) | 0 |
| `duty_mara` | no circumstance | 0 | 0 |
| `scene_mara` | anyone present | 0 | 0, except **C-kind: 6,561 FS** |

The remaining families:

| Family | Check | S | A | B | C | C-entity | C-conditions | C-split | C-kind |
|---|---|---|---|---|---|---|---|---|---|
| **E** support varied (26,244 profile-situations, 3 levels) | applicability changes / strength wrong | 0 / - | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| **F** inhibitor varied (13,122, 3 levels) | applicability changes / strength wrong | **13,122 / -** | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| **G** no active route, wrong route-layer states | `only_side_mara` / `only_owning` / `only_fair` / `weak_pull` | 6,561 / 6,564 / **4,368** / 0 | 6,561 / 6,564 / 0 / 0 | 6,561 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 6,561 / 0 / 0 / 0 | 0 / 6,564 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| **H** irrelevant facts | changes | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

- **In F, S fails because of its discard.** Where anxiety pushes the rule's
  weight to zero or below, S drops the rule. The inhibitor then works as a
  switch.
- **In G, S also turns "applies, with zero strength" into "no candidate"** for
  the 4,368 profile-situations in which fairness is not valued at all.
- **Every representation that computes strength** leaves `stepping_in`
  applicable with zero or negative strength in 17,496 of 39,366 evaluations.
  That is reported, not corrected: an inhibitor is not floored.

**Family I** (the causal-route controls):

| | S | A | B | C | C-entity | C-conditions | C-split | C-kind |
|---|---|---|---|---|---|---|---|---|
| I.1 the 18 pairs reproduce D's support, explanation, outcome and flagged counts | - (not a route representation) | **18 of 18** | **18 of 18** | **18 of 18** | 18 of 18 | 18 of 18 | 18 of 18 | 18 of 18 |
| I.2 copy within the route, reorder, rename routes, regroup: no change | fail (a copy doubles) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| I.3 a copy declared a new route changes support and is flagged; identical routes flagged | fail | pass | pass | pass | pass | pass | pass | pass |
| I.4 the ambiguous declaration (one belief both condition and support in one route) is flagged | fail | **fail** (roles not read) | pass | pass | pass | pass | pass | pass |

**Families passed, of 10:**

| S | A | B | C | C-entity | C-conditions | C-split | C-kind |
|---|---|---|---|---|---|---|---|
| 2 (E, H) | 3 (E, F, H) | 6 (A, B, E, F, H, I) | **10** | 6 (A, B, E, F, H, I) | 7 (C to F, H, I, J) | **10** | 8 (fails B, J) |

**What the pattern would mean:**
- **Typed roles alone (B)** solve conditions (A, B) and "no applicable route"
  for a failed condition. They solve nothing about circumstances (C, D, J).
- **Each element of C is needed.** Remove person binding and D and J fail;
  remove conditions and A, B and G fail.
- **Each element must be declared, not inferred.** Inferring roles from the
  kind of fact fails B's evidence counterexample, and binding every presence to
  the target fails J's generic route.
- **C and C-split pass exactly the same checks.** At the route layer, conditions
  and circumstances are one construct: a conjunction of predicates over the
  person and the situation. Separating them changes only where "does not apply"
  is recorded (section P2).

## P2. The selection layer (analytic; reported, not judged)

Outcomes of the sole-candidate cases of family G, of 13,122 cells each:

| Case | C, P0 | C, P1 | C-split, P0 | C-split, P1 | B, P0 | B, P1 |
|---|---|---|---|---|---|---|
| `only_side_mara` | protect 13,122 (8,748 with no applicable route) | protect 4,374, none 8,748 | protect 4,374, none 8,748 | the same | protect 10,935, none 2,187 | the same |
| `only_owning` | theft 13,122 (6,564 with no applicable route) | theft 6,558, none 6,564 | theft 13,122 | theft 6,558, none 6,564 | theft 13,122 | theft 6,558, none 6,564 |
| `only_fair` | theft 13,122 | theft 13,122 | the same | the same | the same | the same |

**Where "does not apply" is recorded decides what P0 does.**
- **A failed circumstance.** C records it at the route, and P0 still forms
  protect with nothing behind it. C-split records it at candidacy, as the
  shipped gate does, and P0 forms nothing.
- **A failed condition.** Every representation that reads conditions records
  it at the route, so only P1 leaves the person without an intention.

## P3. Behaviour on the frozen file (analytic; 30,618 cells)

The frozen file is read with the causal-route declarations and nothing new.
Circumstances are the shipped gates, read as generic predicates.

| | Differs from A, P0 | No intention | Ties |
|---|---|---|---|
| A, P0 or P1 | 0 | 0 | 25 |
| **B, P0** | **2,980 (9.7 %)** | 0 | 32 |
| B, P1 | 4,074 (13.3 %) | 1,094 | 32 |
| **C, P0** | **4,074 (13.3 %)** | 0 | **1,126** |
| C, P1 | 4,074 (13.3 %) | 1,094 | 32 |
| C-split, P0 / P1 | 2,980 / 4,074 | 0 / 1,094 | 32 / 32 |
| B+w (a condition that keeps its weight), P0 / P1 | 91 / 1,185 | 0 / 1,094 | 25 / 25 |

**B against A under P0** (2,980 cells):
- **2,889 believers.** The condition adds no strength, so they lose the belief's
  0.60: 972 each in `get_food` in company and alone move to
  `take_responsibility`, 627 move to `protect`, 311 to `prevent_argument`, and
  7 tie.
- **91 innocents** who had formed the theft over a rival.
- **The 1,094 innocents in `avoid_exposure` alone** still form the theft under
  P0, with no applicable route.

**Under C and P0, those 1,094 become three-way ties at zero support.** Protect,
prevent-argument and the theft are all candidates, and none of them applies.
This is the placement effect, not a finding about people.

## P4. Real mornings (empirical)

| # | Prediction |
|---|---|
| 4.1 | Of the 1,028 real pantry decisions, **B and C change the same 99 under P0**: Daniel, in the mornings where he ate the can, matched at others' `get_food` checks. The reason-semantics experiment found these 99 under its condition reading |
| 4.2 | C-split equals B on every real decision |
| 4.3 | B+w (the condition keeps its weight) changes no real decision |
| 4.4 | At least one real decision's explanation changes while its chosen intention does not (a believer who still forms the theft, with the belief now a condition rather than an amount). Weak |
| 4.5 | In the live cells, C under P0 produces zero-support ties where B does not: people alone and without the belief, asked about `avoid_exposure`. B under P1 forms no intention there |
| 4.6 | Every real decision that changes is one A formed as a theft |

## P5. The annotation (empirical)

| # | Prediction |
|---|---|
| 5.1 | Q1 (does the reason apply?): the majority matches the key on at least 14 of 16 items; kappa at least 0.6 |
| 5.2 | **`zero_support` does not match: readers say the reason does not apply** to someone who does not value fairness at all (key: it applies, with nothing behind it). Readers are predicted not to separate "applies with zero strength" from "does not apply" |
| 5.3 | Facts: the belief in `cond_*` and `no_route_cond` is a `prerequisite` (at least 5 of 6); the presence facts are `circumstance` (at least 4 of 6); the belief in `evid_absent` is `supporting` (at least 4 of 6); fear in `inhibitor_high` is `inhibiting` (at least 5 of 6) |
| 5.4 | **Two names, one behaviour:** Q8 is `disappear` for the prerequisite items and for the presence items alike (at least 5 of 6 each), while their labels differ (prerequisite against circumstance) |
| 5.5 | Q8 is `weaker_or_stronger` for `support_low`, `inhibitor_high` and `evid_absent` (at least 5 of 6), and `no_change` for `duty_absent` and `irrelevant_person` (at least 4 of 6) |
| 5.6 | Q7: `person:mara` on the `side_*` items and `no_route_circ`, `person:daniel` on `target_daniel`, `anyone` on the `scene_*` items (at least 5 of 6 each) |
| 5.7 | Q9: `no` on `no_route_circ`, `no_route_cond` and `zero_support` (at least 5 of 6) |
| 5.8 | Kappa at least 0.4 for the facts, Q7 and Q8 |

## P6. The expected answer

- A route needs **applicability as its own layer**, separate from strength.
- Applicability is **one construct**: a conjunction of predicates, each over
  either the person (a belief) or the situation (presence). A situation
  predicate can be bound to the want's target (`$target`) or be generic
  (anyone). **Condition and circumstance are two names for the same construct,
  not two constructs.** Separating them changes only the placement of "does not
  apply".
- Roles must be **declared per route**, not inferred from the kind of fact.
- Support and inhibitors change strength and never applicability. An inhibitor
  never becomes a switch.
- "No applicable route" is representable at the route layer. **What the
  deliberator should do then is a selection question** that the placement of
  circumstances already prejudges. It is the next experiment.

## Success criteria (from the brief, section 12, committed)

**C counts as an improvement only if all of the following hold:**
1. It passes families A, B, C, D, E, F, G and J: prerequisite absent against
   present, prerequisite against evidence, circumstance, target, support,
   inhibition, and no applicable route.
2. A or B fails at least one of them, and an ablation shows each failure comes
   from information A or B lacks.
3. It passes H (irrelevant facts) and I (the causal-route invariants: the 18
   pairs reproduce D; restatement, reordering, renaming and regrouping change
   nothing; copies and ambiguity are flagged).
4. The parametric targets pass: the same declared route with Mara, Daniel and
   Elena, and no name in any route.
5. Nothing in production changed, and the S1.4 failures are exactly as before.

**No element of C counts as needed unless:**
- removing it fails a family (an ablation);
- over-applying it fails a counterexample (C-kind), where one exists;
- readers draw it: the relevant majorities match, with kappa at least 0.4.

**Condition and circumstance count as different constructs only if** C-split
passes something C fails, or readers give them different Q8 answers. Otherwise
the split goes under ABANDON, and the labels are kept only as documentation.

## How the final sections will be filled

The review ends with PROVEN, PLAUSIBLE, UNPROVEN, FAILED, OVERFITTING RISKS,
KEEP, MODIFY, REBUILD, ABANDON and NEXT EXPERIMENT. Each is decided from the
rules above:
- **REBUILD** only if some required distinction cannot be expressed without
  breaking the invariants of family I or the stage separation;
- **ABANDON** for any construct an ablation shows adds nothing.

**Not claimed by any outcome:** that any declared applicability is how people
are. The checks prove properties of representations. The reviewers show
legibility.
