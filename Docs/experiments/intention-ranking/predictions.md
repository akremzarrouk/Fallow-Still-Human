# Intention ranking: predictions

Written and committed **before the fixture that measures any of this existed**.
Everything below is derived by reading the frozen rule file and the published
numbers of the generalization experiment. Nothing was simulated to write it. Kept
as written; where a prediction is wrong, `results.md` says so.

## What this experiment is for

The generalization experiment showed that the ten frozen rules are a reusable
function of a person. It also showed that the way they choose between intentions
does not survive inspection. This experiment does not fix that. It asks what an
intention-selection mechanism has to satisfy to count as a causal mechanism rather
than a numerical ranking, and measures which of those properties the current one
has.

| | |
|---|---|
| **H1** | The current ranking does not satisfy the invariants a reusable psychological mechanism needs |
| **H2** | Those invariants can be identified without choosing a production replacement |

## What is frozen

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Rules | 10, unedited |
| Selector | `IntentionSelector.Form`, unedited |
| Production | nothing under `Scripts/Core`, no shipped data, no shipped weight |

Every alternative rule set is built in memory. Every alternative aggregator lives
in the new fixture and nowhere else. The file is hashed at the start and the end.

## The five stages, defined before measuring them

The brief asks that these not be assumed to be the same thing. In the current
selector they are separate steps, and each depends on a different part of the
world:

| Stage | Operational definition | Can depend on |
|---|---|---|
| 1 **Availability** | intentions with a rule whose `motives` lists the want | the want only |
| 2 **Compatibility** | available intentions with a rule whose `when` matches the moment | the want and the circumstance |
| 3 **Support** | each compatible rule's contribution, `base + sum(factor x level)` through the shipped `ScalerEval` | the person |
| 4 **Preference** | each intention's score, currently the **sum** of its rules' positive contributions | the person, through 3 |
| 5 **Selection** | the highest score; an exact tie goes to the intention whose **name** sorts first | 4, and the alphabet |

One thing blurs the line between 3 and 2. A contribution at or below zero is
**discarded**, not counted as zero. So a person can remove a compatible rule from
the running, which is a person-dependent exclusion inside the support stage.

## The cells

| | |
|---|---|
| Profiles | the 2,187 of the generalization sweep, rebuilt identically |
| Wants | 7 |
| Circumstances | in company (three others present) and alone |
| **Cells** | **30,618** = 2,187 x 7 x 2. Every test below runs on all of them unless it says otherwise |
| Single-attribute perturbations of a person | 21: each of 7 traits moved to each of its other two sweep levels (14), each adjacent pair of value ranks swapped (5), each of the two beliefs toggled between absent and its sweep confidence (2) |

## The transformations, fixed in advance

| | Transformation | Applied |
|---|---|---|
| T1 | Reverse the order of the rules | once |
| T2 | Give every rule a new id | once |
| T3 | Rename the intentions so their alphabetical order reverses, and map back afterwards | once |
| T4 | Add an exact duplicate of one rule under a new id | per rule |
| T5 | Add a near-duplicate: the same rule with every number x 0.99 | per rule |
| T6 | Split one rule into two rules at half weight | per rule |
| T7 | Split one rule into four rules at quarter weight | per rule |
| T8 | Split one rule by term: its base as one rule, each scaler as a rule of its own | per rule |
| T9 | Scale one rule's weight x 2 (the "2W" condition) | per rule |
| T10 | Merge every set of rules that are compatible together for the same want, intention and circumstance into one rule | once |
| T11 | Duplicate every rule | once |

## The aggregators, fixed in advance

Each is a pure function of an intention's contributions. None has a parameter, so
none can be tuned.

| | Score of an intention | Why it is in the family |
|---|---|---|
| **sum** | the sum of its positive contributions | the current mechanism |
| **max** | its largest contribution | the best single reason decides |
| **mean** | the mean of its positive contributions | support per reason, not in total |
| **normalized max** | the largest of `contribution / that rule's own attainable maximum` | each reason judged against how strongly it could ever apply |
| **noisy-OR** | `1 - product(1 - normalized contribution)` | the textbook combination of independent evidence |
| **deduplicated sum** | the sum, counting rules identical in everything but their id once | the minimal repair aimed at duplication |

Ties break as they do now, by name, for all six, so that the tie-break is held
constant while the aggregation varies.

## Predictions

### A. Duplication

| # | Prediction | Falsified if |
|---|---|---|
| A1 | Under the current sum, duplicating a rule changes the winner in **19,000 to 21,500** of the 306,180 (rule, cell) pairs. The published figure was 2,898 on every seventh profile; the full sweep is seven times larger | outside that range |
| A2 | **Every** change is toward the duplicated rule's intention | any change goes elsewhere |
| A3 | **No** change occurs in a cell where the duplicated rule is not compatible | any does |
| A4 | Duplicating `doing_it_where_nobody_is_watching` changes **0** cells even on the full sweep: where it is compatible, its intention is either the only one in the running or already wins every time | it changes any |

### B. Splitting

| # | Prediction | Falsified if |
|---|---|---|
| B1 | Splitting any rule into two halves changes **0** of 306,180, under the current mechanism. This is the regression invariant, and it is asserted | any change |
| B2 | Splitting into four quarters also changes **0** | any change. Floating point could in principle move an exact tie; I expect it not to |

### C. Weight against representation

For every rule: one rule at W, two at W/2, four at W/4, one at 2W, and two at W.

| # | Prediction | Falsified if |
|---|---|---|
| C1 | Under the sum there are exactly **two** equivalence classes: {W, 2 x W/2, 4 x W/4} and {2W, W + W}. Cell for cell, 2W and the duplicate agree **everywhere** | any cell where 2W and W + W disagree, or where the splits differ from W |
| C2 | So the one representation change the mechanism treats as meaningful is a change of **total weight per intention**. It cannot tell "one stronger reason" from "the same reason twice" | C1 fails |

### D. Candidate sets

Availability and compatibility depend only on the want and the circumstance, so
the number of compatible intentions is a property of the 14 (want, circumstance)
groups, not of the person.

| # | Prediction | Falsified if |
|---|---|---|
| D1 | **K = 1** in 4 groups, all alone: `avoid_exposure`, `find_out`, `keep_peace`, `look_after`. **8,748 cells, 28.6 %** | different |
| D2 | **K = 2** in 3 groups: `get_food` in both circumstances and `restore_standing` in company. **6,561 cells, 21.4 %** | different |
| D3 | **K = 3** in the other 7 groups. **15,309 cells, 50.0 %**. No group has more than three | different, or any K >= 4 |
| D4 | K = 1 groups show exactly **one** winner and **zero** sensitivity to any perturbation of the person. Structural | any variation |
| D5 | **`restore_standing` alone has three candidates and one winner:** `take_responsibility` in all 2,187 profiles. `prevent_argument` there is **strictly dominated for every possible person** (its best margin over `take_responsibility` in the unit box is -0.07). `assert_authority` is not dominated but can only win through anger, which the sweep does not vary | any other winner in the sweep, or `prevent_argument` not dominated |
| D6 | So cells whose winner is the same for every profile in the sweep are **at least 35.7 %**: the K = 1 groups plus `restore_standing` alone | fewer |
| D7 | Of the 27 (group, intention) pairs with K >= 2, exactly **one** is dominated (D5), exactly **one** is undominated but never wins in the sweep (`assert_authority`, `restore_standing` alone), and the other **25** win for some profile | any other count |
| D8 | **K does not predict sensitivity.** At least one K = 3 group is less sensitive than every K = 2 group | every K = 3 group is more sensitive than every K = 2 group |
| D9 | `anxious` is **structurally** unable to change any outcome for any person, not just unobserved to: its only rule is either the sole candidate or dominated | `anxious` changes a single cell under the sum |

### E. Gating against preference

Six rules are gated, four are not. At the level of intentions, a gate excludes an
available intention in exactly **9** (want, circumstance) pairs: eight alone
(`share_information` x 3, `protect` x 2, `prevent_argument` x 2,
`assert_authority` x 1) and one in company (`prevent_argument` for
`restore_standing`). Everywhere else a gate removes one **reason** for an
intention that another rule keeps available.

| # | Prediction | Falsified if |
|---|---|---|
| E1 | Mechanically, a gate is a **hard impossibility at the level of a reason**: a gated-out rule contributes exactly nothing, whatever the person | any partial contribution |
| E2 | No perturbation of the person ever changes the compatible set. Structural: the gate type has no field for a person | a single exception in 642,978 pairs |
| E3 | Removing every gate changes the winner in **20 % to 45 %** of all cells, far more alone than in company | outside |
| E4 | `avoid_exposure` and `look_after` alone, ungated, behave exactly as in company, because neither has an alone-only rule: 48.6 % and 14.0 % of their cells change | different |
| E5 | For most of the 9 intention-level exclusions, the excluded intention would win for **some but not all** profiles. So the gate overrides a person-dependent preference rather than an idle candidate | the excluded intentions would never win, or always |
| E6 | **The discard of non-positive contributions fires in exactly 243 cells**: `not_making_a_scene_of_it` reaches -0.010 for the 81 profiles with cautious 0.15, dominant 0.85 and closeness ranked fifth or sixth, in the three company wants it serves. It changes the **supported** set in those 243 cells and the **winner in none** | any other count, or any winner changed |

### F. Preference with the candidate set held fixed

| # | Prediction | Falsified if |
|---|---|---|
| F1 | With the circumstance fixed, person perturbations leave the compatible set identical in **every** pair | any exception |
| F2 | They leave the supported set identical except where the discard in E6 moves | any other exception |
| F3 | With the candidate set identical, person state changes the winner in a **non-zero** share of K >= 2 pairs. This is preference, separated from candidate generation | zero |
| F4 | `impulsive`, read by no rule, changes **0** pairs. (There is no pure `autonomy` perturbation: values weigh by rank, so moving one value moves another) | any |
| F5 | Of the company-arrival changes (8,407 in the published measurement), **50 % to 65 %** are availability: the new winner is an intention no rule offers alone. The rest are a reason-level gate re-weighting an intention available in both | outside |

### G. The aggregation family

| # | Prediction | Falsified if |
|---|---|---|
| G1 | The six aggregators disagree with the sum in some cells. Which is closer to human is **not** measured and not claimed | - |
| G2 | Under **max**, `anxious` becomes able to change outcomes: `letting_it_go_for_now` can beat the larger of `take_responsibility`'s two rules alone, where it can never beat their sum. So the deafness is a property of adding, not of the rule | `anxious` changes nothing under max |
| G3 | Under **max**, `look_after -> protect` **in company** falls below 60 %, from 86.0 % under the sum. (Alone it is the only candidate, so it stays at 100 % under every aggregator) | at or above 60 % |
| G4 | Gating is shared by every aggregator, so the forced share of D1 is identical for all six | any difference |

### H. Representation invariance

"P" = preserves the winner in every cell. "V" = changes at least one.

| | Should preserve? | sum | max | mean | norm. max | noisy-OR | dedup. sum |
|---|---|---|---|---|---|---|---|
| T1 reorder | yes | P | P | P | P | P | P |
| T2 rename rules | yes | P | P | P | P | P | P |
| T3 rename intentions | yes | V if any exact tie | same | same | same | same | same |
| T4 duplicate | yes: no new information | **V** | P | V | P | V | P |
| T5 near-duplicate | yes: behaves as T4 | **V** | P | V | P | V | **V** |
| T6 split x 2 | depends on what a rule is | P | V | V | P | V | V |
| T7 split x 4 | depends on what a rule is | P | V | V | P | V | V |
| T8 split by term | yes | **V, for `not_making_a_scene_of_it` only** | V | V | V | V | V, same |
| T9 scale x 2 | **no**: it must be able to change | V | V | V | **P** | **P** | V |
| T10 merge | yes | P | V | V | V | V | P |
| T11 duplicate all | yes | P | P | P | P | P | P |

Two things in that table are predictions about the mechanism, not the family:

- **T8 breaks the sum only through the discard.** Split `not_making_a_scene_of_it`
  by term and its negative `dominant` piece becomes a rule of its own, weighs
  below zero, and is thrown away, so the intention gains weight it never had.
  Grouping terms into rules changes the answer.
- **Under mean, duplicating a rule can make its own intention lose** (a reason
  weaker than its intention's average drags the average down). Every other
  aggregator is monotone: 0 changes away from the duplicated intention.

### The impossibility, committed in advance

No aggregator of anonymous contributions can be invariant to **duplication** and
to **proportional splitting** while still responding to **weight**. Let `f` score
an intention from its contributions. Duplication-invariance gives
`f(w/2, w/2) = f(w/2)`. Split-invariance gives `f(w/2, w/2) = f(w)`. So
`f(w) = f(w/2)` for every `w`, and a rule's weight cannot matter. The same holds
with other rules alongside: `f(w, R) = f(w/2, w/2, R) = f(w/2, R)`.

The theorem is about scores and the table measures winners, so the table can
contradict it but not prove it. It must show no aggregator with P on T4 and T6
and V on T9. If it shows one, the fixture is wrong.

The consequence, if it holds: whether a second rule is **new evidence** or **the
same evidence twice** is not something any formula over numbers can know. It has
to be in the representation of a rule.

## What would decide the verdict

Committed now, so the verdict cannot be fitted to the numbers:

| Verdict | If |
|---|---|
| **KEEP** | the current mechanism violates none of the invariants a replacement would be required to satisfy |
| **MODIFY** | the violations are located in ranking (aggregation, the tie-break, the discard) and in how a rule represents its evidence, **while** the stages below them hold: gates are person-independent (E2), and with the candidate set fixed, person state decides a non-trivial share of contested outcomes (F3) |
| **REBUILD** | a stage below ranking fails: gating is person-dependent in its winners, or with the candidate set fixed the person almost never matters (**under 1 %** of K >= 2 pairs), so that the architecture's person-dependence is made of gating |
| **ABANDON** | replay or generalization fails on reproduction |

My expectation is **MODIFY**. It is falsified by F3 coming in under 1 %, or E2
finding a single person-dependent gate.
