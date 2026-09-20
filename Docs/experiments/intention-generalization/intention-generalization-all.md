# intention-generalization: all documents

Merged by `merge-slice-docs.py` from the 4 Markdown files in `Docs/experiments/intention-generalization/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)

---

## report.md

### Intention formation: does it generalize

*Does the mechanism encode reusable relationships between a want, a person and a
situation, or is it a table fitted to four people?*

#### 1. Hypothesis

**H1.** The candidate-rule approach captures reusable relationships between
motivation, person, beliefs, traits, values, feelings and circumstances, rather
than encoding the four existing characters. If so, the **unchanged** rules should
produce context-sensitive variation for people they were never written against,
with no character-specific rule added.

**H2**, secondary and independent. If several rules contribute additively to one
intention, then adding a semantically redundant rule can change the chosen
intention with the person's state untouched. That would make the scoring
principle an artifact.

The brief is right that these can come apart, and they do. A mechanism can
generalize perfectly and still score for a bad reason. They are reported
separately, in sections 6 and 7.

#### 2. What was frozen

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| git blob | `41112b95d75d75786ad4df442e25330c74c5d6b3` |
| Bytes | 6,956 |
| Rules | 10 |
| Commits touching it | one, `8ede500` |

The fixture hashes the file **at the start of the run and again at the end**, and
both hashes are printed in the measurements. They match. No rule was added for a
held-out person, no weight was altered, no intention was renamed. The rule-count
experiment builds its extra rules **in memory**, which is why the file on disk
survives it untouched.

**No production change.** Nothing under `Assets/_Project/Scripts/Core` was
touched, and no shipped data file was edited. `IntentOfAct` is still null by
default. The one code change anywhere was to move the selector out of the
previous experiment's fixture into a shared test-only class so that both
experiments run the *same* mechanism rather than two copies that could drift —
and the previous experiment's generated document regenerated **byte-identical**,
which is the proof that the move changed nothing.

#### 3. Holdout design

**The declared four.** People placed by a stated principle in regions the shipped
cast does not occupy. The cast is nowhere below 0.50 on `empathetic` or `honest`,
nowhere above 0.70 on `cautious`, and never high on `dominant` and `empathetic`
together:

| Person | Principle |
|---|---|
| `hollow` | Below the cast's floor on the two traits it never goes low on: empathetic 0.10, honest 0.15 |
| `warden` | Dominant 0.95 **and** empathetic 0.95 together, which no cast member is; cautious 0.85, above all of them |
| `drifter` | Every trait at exactly 0.50; a single value the cast never ranks first |
| `firebrand` | Extremes on the volatile traits at once, and a value ordering nobody holds |

**The sweep, which is the actual evidence.** Every combination of the seven
shipped traits at three levels: **2,187 profiles**, enumerated mechanically, with
values and beliefs rotating by index. I did not design a single one of them, so
none of them can have been fitted to. If the rules were a table for four people,
a uniform sample of trait space is where that would show.

Both were declared in `Data/Experiments/held-out-people.json` and committed with
the predictions before anything ran.

#### 4. Is there character-specific encoding?

Searched: every rule's id, intent and want list, and every scaler's kind, name,
predicate, entry, about, topic, by, target and arguments, for all four cast ids
and all four held-out ids.

**Zero hits.** The only person-token any rule uses is `$self`, which resolves to
whoever is deciding. No rule is keyed on an identity, and no rule exists whose
purpose is to separate one character from another.

What the rules *do* read, which is a more useful fact:

| | Read | Never read |
|---|---|---|
| traits | anxious, cautious, dominant, empathetic, honest, proud | **impulsive** |
| values | closeness, control, fairness, family_safety, respect | **autonomy** |
| other | belief, emotion | ledger, memory, need, perceptiveness |

Ten rules cannot read seven traits and six values evenly. What they cannot feel
is as much a fact about the mechanism as what they can.

#### 5. Results: generalization

**The frozen rules transfer.** 28 of 28 held-out (person, want) cells in company
formed an intention, using four distinct ones. `warden`, who is dominant 0.95 and
empathetic 0.95 — a combination no cast member has — forms `take_responsibility`
for `find_out` where Daniel forms `assert_authority`, and `assert_authority` for
`guard_supplies` where Elena forms `take_responsibility`. `firebrand`, who
believes herself answerable for the missing can, forms `took_what_was_not_mine`
where everyone else forms `protect`.

**Across 2,187 undesigned profiles:**

| | |
|---|---|
| Distinct intentions per want | 2 or 3, for every one of the 7 |
| **Distinct signatures** (the seven intentions a profile forms, in order) | **56** |
| Most common signature, share of profiles | 11.6 % |
| Profiles whose intention changed on company arriving | 2,187 of 2,187 |

A table keyed on the want would produce **one** signature. Fifty-six is what a
function of the person produces.

**Counterfactual specificity**, one thing at a time, over 15,309 cells:

| Perturbation | Read by a rule | Cells changed |
|---|---|---|
| Three others come into the room | yes | **54.9 %** |
| Comes to believe they are answerable for the can | yes | 6.3 % |
| Comes to believe they lead the family | yes | 1.3 % |
| Hunger 0.30 -> 0.95 | **no** | **0.0 %** |
| Moved to a room with no food | **no** | **0.0 %** |

**Per trait**, both contexts, one trait moved 0.15 -> 0.85 with everything else
held:

| `honest` | `empathetic` | `cautious` | `dominant` | `proud` | `anxious` | `impulsive` |
|---|---|---|---|---|---|---|
| 12.8 % | 10.4 % | 6.8 % | 6.6 % | 2.0 % | **0.0 %** | **0.0 %** |

So: it generalizes, it is a function of generic state, it is exactly
reproducible, and it is provably blind to state no rule reads.

#### 6. Results: scoring validity, which is a different question

##### The rule-count experiment

Three conditions, identical people, wants, circumstances, beliefs, traits, values
and feelings. Only the rule set differs, and only in memory.

| | Rules | Total weight for that intention | Cells changed |
|---|---|---|---|
| **A** frozen | 10 | — | baseline |
| **B** plus an exact clone of one rule under a new id | 11 | **doubled** | **2,898** |
| **C** with one rule split into two halves | 11 | **unchanged** | **0** |

Over 4,382 cells per rule and all ten rules. Splitting a rule adds a rule and no
weight, and moves nothing. Cloning a rule adds a rule and doubles a weight, and
moves 2,898 outcomes.

**So the rule count is not the bias. The sum is.** And that is worse than the
thing I reported last time, not better: writing a second rule for an intention
and raising the first rule's numbers are *the same operation* as far as the
mechanism can tell. There is no discipline about rule-writing that avoids it,
because the problem is not in how rules are written.

**This corrects my previous report.** The intention-formation report says
`look_after` collapsed because "`protect` has two candidate rules and its
competitors have one each. Two rules beat one." That is loose. What beats one
rule is more total weight, and a second rule is merely one way of adding it. The
sentence is not retracted — it described that case correctly — but the mechanism
it names is wrong, and this measurement is the one to believe.

##### Two structural limits the sweep exposed

**Where only one intention is in the running, the person is irrelevant.** Across
all 30,618 cells, **28.6 %** had exactly one intention with any candidate
matching. Alone, that is **100 %** of profiles for `avoid_exposure`, `find_out`,
`keep_peace` and `look_after`. In those cells all 2,187 profiles form the same
intention and no psychology could change it. This — not the summation — is what
produces the flat columns in the tables.

**A trait can be read and still be deaf.** `anxious` is named by a candidate rule
and changed the intention in **0 of 4,382** cells in both contexts. Its only rule
is either the sole candidate in the running, in which case it wins whatever it
weighs, or it loses every time. Being read and being able to decide anything are
different properties.

#### 7. The known failure, off the cast

`look_after -> protect` was 851 of 851 on the shipped cast. Across the sweep it is
**93.5 %**, with **306 escapes** to `share_information` and `prevent_argument`.

So the answer to the brief's A-or-B is **A, with a large caveat**: the *totality*
is an accident of this cast, but the *strong tendency* is not. Diagnosed by
withholding one rule at a time, in memory:

| Rules | `look_after` across the sweep |
|---|---|
| all ten, as frozen | `protect` 93.5 %, `share_information` 6.1 %, `prevent_argument` 0.5 % |
| without `keeping_it_off_them` | **`none` 50.0 %**, `share_information` 24.0 %, `protect` 22.2 %, `prevent_argument` 3.8 % |
| without `standing_between_them_and_it` | `protect` 56.9 %, `share_information` 37.4 %, `prevent_argument` 5.8 % |

Not a fix, and nothing was changed: withhold the unconditional `protect` rule and
half of all cases form **no intention at all**, because the remaining candidates
are gated on company. The collapse and the coverage are the same rule.

**The innocent theft is general.** `took_what_was_not_mine` was formed 2,096 times
across the sweep, of which **91 (4.3 %)** were by a profile holding no belief they
are answerable for anything — against 3.2 % on the cast. Not a cast artifact.

#### 8. Limitations and overfitting risks

- **The sweep varies traits, values and beliefs; it does not vary feelings,
  memories or the ledger.** Two of the eight scaler kinds the rules could read are
  therefore untested here, and four kinds are read by no rule at all.
- **One house, one circumstance vocabulary.** `SituationCondition` has six fields;
  the experiment perturbs three of them.
- **Six intentions.** Unchanged from last time, and still the ceiling.
- **The held-out people are held out from the rules, not from me.** I wrote the
  principles that place them. The sweep is the answer to that objection and is
  why it carries the weight here.
- **Determinism cuts both ways.** No randomness makes every result exactly
  attributable, and also means the mechanism cannot represent a person who is
  torn.
- **Nothing here tests whether the intentions are *right*.** Causal dependence is
  measured. Psychological truth is not, and is not claimed.

#### 9. Classification

| | |
|---|---|
| **PROVEN** | The mechanism generalizes off the authored cast. 2,187 undesigned profiles, 56 distinct signatures, all seven wants many-valued, 28 of 28 held-out cells formed. Zero character-specific encoding. Exactly reproducible (300 of 300). Provably blind to unread state (0 of 15,309 on two irrelevant perturbations). Responds to generic state: five traits and two beliefs each move outcomes. **And the scoring principle is additive rather than principled: cloning a rule moves 2,898 outcomes, splitting one moves 0.** |
| **PLAUSIBLE** | That the variation is psychologically meaningful. `warden` differing from Daniel on `find_out` reads correctly, but that is a judgement and this experiment does not evidence it |
| **UNPROVEN** | That the approach survives a larger vocabulary, a second house, or scalers on feelings and memories. That 28.6 % of cells having nothing to compare is fixable without redesigning candidate gating |
| **FAILED** | The scoring principle as a principle. A duplicate rule changes the answer with the person untouched. Two of seven traits can never change anything, one of them despite being read. And `took_what_was_not_mine` is formed by innocent people at the same rate off the cast as on it |
| **UNKNOWN** | Whether a mechanism with these properties would still generalize once the scoring were fixed — every number here was produced under the broken scoring |

#### 10. Verdict

### MODIFY

Last time this line was **KEEP**. The generalization evidence would still support
that: the mechanism is demonstrably a function of person and circumstance rather
than a table for four people, and nothing in this experiment weakened that.

What changed is the scoring evidence, which did not exist before. **A duplicate
rule changes 2,898 outcomes while a weight-preserving split changes none.** That
is not a defect in the rules; it is a property of deciding by a sum. And 28.6 %
of all cells never compare anything at all, so in those the psychology is
decorative.

So: keep the constraint-not-mapping structure, keep the `SituationCondition`
gating that makes a circumstance unable to be a reason, keep the reuse of
`ScalerEval`. **Modify how candidates are ranked**, which is where the evidence
now points and where the brief says not to go yet. Nothing is being modified
here; the file is frozen, the hash is printed twice, and nothing enters
production.

#### 11. The question the brief asks to answer explicitly

> Does the current mechanism appear to encode reusable relationships between
> motivation, person and context, or does it primarily behave like a
> hand-authored table fitted to the existing cast?

**It encodes reusable relationships.** Not on the grounds that the outputs sound
human — they were not judged on that — but on the holdout and counterfactual
evidence:

- 2,187 profiles nobody designed produce **56 distinct signatures**; a table keyed
  on the want produces one.
- The rules contain **no character name or id**, and were run against four people
  outside the cast's trait ranges without a line being added.
- Outcomes move with generic state — `honest` 12.8 %, `empathetic` 10.4 %, a
  belief 6.3 % — and **never** move with state no rule reads: 0 of 15,309 on
  hunger, 0 of 15,309 on the room.
- It is exactly reproducible, so none of that variation is noise.

**But the answer has a second half, and it is not a caveat.** The mechanism
generalizes while ranking its candidates by a principle that does not survive
inspection: an intention wins because its rules sum higher, and a redundant rule
is indistinguishable from a bigger number. Where the circumstances leave one
candidate standing, which is 28.6 % of the time, nothing about the person is
consulted at all.

So the honest answer is: **it is a reusable function of character state, computed
by an arbitrary rule.** Both halves are measured, neither is inferred from
plausibility, and the second is where the next question lies.

Left exactly there, for review.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter IntentionGeneralizationExperimentTests`.
It takes about twenty seconds.

**Suite: 414 tests, 412 pass, 2 fail** — the two regressions S1.4 left failing, unchanged (the pacing gate, still 7 on Model A, and the emergent-moment fading check). 401 before these two experiments, plus their seven and six tests, is exactly 414. **Every generated document of S0 to S1.7 and of the seven earlier experiments regenerated with identical content**; the only change anywhere in the repository was the wall-clock seconds in the decision-sensitivity results, and one file that differed in line endings only.

---

## measurements.md

### Intention formation, generalization: measurements

Generated by `IntentionGeneralizationExperimentTests` against the frozen candidate rules, whose hash is checked at the start and the end of the run. The held-out people were declared and committed before any of them was run. The selector has no randomness.

#### G1. The frozen rules, and whether they know anybody's name

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 at the start of this run | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Expected | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Match | **yes** |
| Rules | 10 |

**Character names or ids anywhere in a rule's id, intent, wants, or any scaler's kind, name, predicate, entry, about, topic, by, target or arguments: 0.** The only person-token any rule uses is `$self`, which is whoever is deciding.

##### What generic state the rules actually read

| Kind | Names read | Names in the vocabulary that no rule reads |
|---|---|---|
| trait | anxious, cautious, dominant, empathetic, honest, proud | **impulsive** |
| value | closeness, control, fairness, family_safety, respect | **autonomy** |
| other | belief, emotion | - |

Ten rules cannot read seven traits and six values evenly, and they do not. What they do not read at all is as much a fact about the mechanism as what they do.

#### G2. Four held-out people, beside the four the rules were written knowing

Each held-out person is placed by a stated principle outside the region the shipped cast occupies. The cast is nowhere below 0.50 on empathetic or honest, nowhere above 0.70 on cautious, and never high on dominant and empathetic together.

| Person | Held out | Principle | Traits | Values | Beliefs |
|---|---|---|---|---|---|
| **hollow** | yes | Below the cast's floor on the two traits it never goes low on: empathetic and honest. | anxious 0.500, cautious 0.500, dominant 0.600, empathetic 0.100, honest 0.150, impulsive 0.500, proud 0.500 | control, autonomy | none |
| **warden** | yes | High on dominant and empathetic together, which no member of the cast is, and more cautious than any of them. | anxious 0.150, cautious 0.850, dominant 0.950, empathetic 0.950, honest 0.900, impulsive 0.300, proud 0.300 | family_safety, respect | role_claim($self,leads_family)=0.95 |
| **drifter** | yes | The null person: every trait at exactly one half, and a single value the cast never ranks first. | anxious 0.500, cautious 0.500, dominant 0.500, empathetic 0.500, honest 0.500, impulsive 0.500, proud 0.500 | autonomy | none |
| **firebrand** | yes | Extremes on the volatile traits, outside the cast on impulsive, proud, anxious and cautious at once, holding a value ordering nobody holds. | anxious 0.950, cautious 0.100, dominant 0.450, empathetic 0.550, honest 0.350, impulsive 0.950, proud 0.950 | respect, control, autonomy | answerable_for($self,missing_can)=0.95 |
| daniel | no | shipped | anxious 0.650, cautious 0.350, dominant 0.850, empathetic 0.500, honest 0.500, impulsive 0.600, proud 0.850 | control, respect, family_safety | tendency(leo,does_not_respect_me)=0.25, more_knowledgeable(leo,survival)=0.40, role_claim(daniel,leads_family)=0.80 |
| elena | no | shipped | anxious 0.750, cautious 0.700, dominant 0.500, empathetic 0.900, honest 0.700, impulsive 0.250, proud 0.350 | family_safety, closeness, fairness | tendency(daniel,needs_to_be_in_charge)=0.70, more_knowledgeable(leo,survival)=0.65, role_claim(elena,leads_family)=0.60 |
| leo | no | shipped | anxious 0.250, cautious 0.700, dominant 0.350, empathetic 0.700, honest 0.800, impulsive 0.200, proud 0.500 | family_safety, fairness, autonomy, closeness | tendency(daniel,makes_risky_calls)=0.45, tendency(daniel,needs_to_be_in_charge)=0.55, more_knowledgeable(leo,survival)=0.85 |
| mara | no | shipped | anxious 0.800, cautious 0.500, dominant 0.250, empathetic 0.750, honest 0.550, impulsive 0.700, proud 0.550 | closeness, autonomy, fairness | tendency(daniel,treats_me_like_a_child)=0.55, tendency(elena,keeps_things_from_me)=0.35 |

##### with three others in the room

| Want | **hollow** | **warden** | **drifter** | **firebrand** | daniel | elena | leo | mara |
|---|---|---|---|---|---|---|---|---|
| `avoid_exposure` | protect 0.190 over prevent_argument 0.175 | protect 0.880 over took_what_was_not_mine 0.320 | protect 0.350 over took_what_was_not_mine 0.200 | took_what_was_not_mine 0.725 over protect 0.370 | protect 0.525 over took_what_was_not_mine 0.200 | protect 0.860 over prevent_argument 0.495 | protect 0.780 over took_what_was_not_mine 0.478 | prevent_argument 0.563 over protect 0.450 |
| `find_out` | assert_authority 0.795 over take_responsibility 0.325 | take_responsibility 0.970 over assert_authority 0.858 | take_responsibility 0.430 over assert_authority 0.400 | assert_authority 0.708 over take_responsibility 0.305 | assert_authority 1.200 over take_responsibility 0.575 | take_responsibility 0.880 over share_information 0.725 | take_responsibility 0.910 over share_information 0.665 | share_information 0.740 over take_responsibility 0.445 |
| `get_food` | take_responsibility 0.325 over took_what_was_not_mine 0.095 | take_responsibility 0.970 over took_what_was_not_mine 0.320 | take_responsibility 0.430 over took_what_was_not_mine 0.200 | took_what_was_not_mine 0.725 over take_responsibility 0.305 | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.445 over took_what_was_not_mine 0.340 |
| `guard_supplies` | assert_authority 1.095 over take_responsibility 0.325 | assert_authority 1.145 over take_responsibility 0.970 | assert_authority 0.450 over take_responsibility 0.430 | assert_authority 0.945 over take_responsibility 0.305 | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 0.910 over assert_authority 0.383 | protect 0.575 over take_responsibility 0.445 |
| `keep_peace` | protect 0.190 over share_information 0.180 | protect 0.880 over share_information 0.480 | protect 0.350 over share_information 0.320 | protect 0.370 over share_information 0.260 | protect 0.525 over share_information 0.320 | protect 0.860 over share_information 0.725 | protect 0.780 over share_information 0.665 | share_information 0.740 over prevent_argument 0.563 |
| `look_after` | protect 0.320 over share_information 0.180 | protect 1.265 over share_information 0.480 | protect 0.600 over share_information 0.320 | protect 0.635 over share_information 0.260 | protect 0.775 over share_information 0.320 | protect 1.418 over share_information 0.725 | protect 1.153 over share_information 0.665 | protect 1.025 over share_information 0.740 |
| `restore_standing` | assert_authority 1.095 over take_responsibility 0.325 | assert_authority 1.145 over take_responsibility 0.970 | assert_authority 0.450 over take_responsibility 0.430 | assert_authority 0.945 over take_responsibility 0.305 | assert_authority 1.700 over take_responsibility 0.575 | take_responsibility 0.880 over assert_authority 0.758 | take_responsibility 0.910 over assert_authority 0.383 | take_responsibility 0.445 over assert_authority 0.345 |

##### alone

| Want | **hollow** | **warden** | **drifter** | **firebrand** | daniel | elena | leo | mara |
|---|---|---|---|---|---|---|---|---|
| `avoid_exposure` | took_what_was_not_mine 0.095 | took_what_was_not_mine 0.320 | took_what_was_not_mine 0.200 | took_what_was_not_mine 0.725 | took_what_was_not_mine 0.200 | took_what_was_not_mine 0.385 | took_what_was_not_mine 0.478 | took_what_was_not_mine 0.340 |
| `find_out` | take_responsibility 0.670 | take_responsibility 1.415 | take_responsibility 0.775 | take_responsibility 0.963 | take_responsibility 1.158 | take_responsibility 1.188 | take_responsibility 1.255 | take_responsibility 0.803 |
| `get_food` | take_responsibility 0.325 over took_what_was_not_mine 0.095 | take_responsibility 0.970 over took_what_was_not_mine 0.320 | take_responsibility 0.430 over took_what_was_not_mine 0.200 | took_what_was_not_mine 0.725 over take_responsibility 0.305 | take_responsibility 0.575 over took_what_was_not_mine 0.200 | take_responsibility 0.880 over took_what_was_not_mine 0.385 | take_responsibility 0.910 over took_what_was_not_mine 0.478 | take_responsibility 0.445 over took_what_was_not_mine 0.340 |
| `guard_supplies` | take_responsibility 0.325 over assert_authority 0.300 | take_responsibility 0.970 over protect 0.385 | take_responsibility 0.430 over protect 0.250 | take_responsibility 0.305 over protect 0.265 | take_responsibility 0.575 over assert_authority 0.500 | take_responsibility 0.880 over protect 0.558 | take_responsibility 0.910 over protect 0.373 | protect 0.575 over take_responsibility 0.445 |
| `keep_peace` | prevent_argument 0.305 | prevent_argument 0.323 | prevent_argument 0.305 | prevent_argument 0.295 | prevent_argument 0.298 | prevent_argument 0.405 | prevent_argument 0.305 | prevent_argument 0.365 |
| `look_after` | protect 0.130 | protect 0.385 | protect 0.250 | protect 0.265 | protect 0.250 | protect 0.558 | protect 0.373 | protect 0.575 |
| `restore_standing` | take_responsibility 0.670 over prevent_argument 0.305 | take_responsibility 1.415 over prevent_argument 0.323 | take_responsibility 0.775 over prevent_argument 0.305 | take_responsibility 0.963 over prevent_argument 0.295 | take_responsibility 1.158 over assert_authority 0.500 | take_responsibility 1.188 over prevent_argument 0.405 | take_responsibility 1.255 over prevent_argument 0.305 | take_responsibility 0.803 over prevent_argument 0.365 |

**The frozen rules formed an intention in 28 of 28 held-out (person, want) cells in company, using 4 distinct intentions.**

#### G3. The sweep: 2187 profiles nobody designed

Every combination of the seven shipped traits at three levels, with values and beliefs rotating by index. The frozen rules have never seen any of them.

| Want | Distinct intentions across the sweep | Distribution, in company |
|---|---|---|
| `avoid_exposure` | 3 | `took_what_was_not_mine` 51.4 %, `protect` 34.2 %, `prevent_argument` 14.4 % |
| `find_out` | 3 | `assert_authority` 56.6 %, `take_responsibility` 29.9 %, `share_information` 13.5 % |
| `get_food` | 2 | `take_responsibility` 55.6 %, `took_what_was_not_mine` 44.4 % |
| `guard_supplies` | 3 | `assert_authority` 80.6 %, `take_responsibility` 18.9 %, `protect` 0.5 % |
| `keep_peace` | 3 | `share_information` 47.8 %, `protect` 44.0 %, `prevent_argument` 8.2 % |
| `look_after` | 3 | `protect` 86.0 %, `share_information` 12.8 %, `prevent_argument` 1.2 % |
| `restore_standing` | 2 | `assert_authority` 81.1 %, `take_responsibility` 18.9 % |

| | Value |
|---|---|
| Profiles | 2187 |
| **Distinct signatures** (the seven intentions a profile forms, in order) | **56** |
| Most common signature, share of profiles | 11.6 % |
| Profiles whose intention changed on the audience alone | 2187 | 

A mechanism that were a table keyed on the want would produce **one** signature. 56 is what a function of the person produces.

The five most common signatures:

| Share | `avoid_exposure` | `find_out` | `get_food` | `guard_supplies` | `keep_peace` | `look_after` | `restore_standing` |
|---|---|---|---|---|---|---|---|
| 11.6 % | took_what_was_not_mine | assert_authority | took_what_was_not_mine | assert_authority | share_information | protect | assert_authority |
| 10.5 % | protect | take_responsibility | take_responsibility | take_responsibility | protect | protect | take_responsibility |
| 10.0 % | protect | assert_authority | take_responsibility | assert_authority | protect | protect | assert_authority |
| 10.0 % | took_what_was_not_mine | assert_authority | took_what_was_not_mine | assert_authority | protect | protect | assert_authority |
| 6.4 % | protect | assert_authority | take_responsibility | assert_authority | share_information | protect | assert_authority |

##### How often the person cannot matter at all

An intention is chosen by comparing candidates. Where the circumstances leave only one intention with any candidate matching, there is nothing to compare and the person is irrelevant by construction, however elaborate their scalers.

| Want | In company | Alone |
|---|---|---|
| `avoid_exposure` | 0.0 % of profiles | 100.0 % of profiles |
| `find_out` | 0.0 % of profiles | 100.0 % of profiles |
| `get_food` | 0.0 % of profiles | 0.0 % of profiles |
| `guard_supplies` | 0.0 % of profiles | 0.0 % of profiles |
| `keep_peace` | 0.0 % of profiles | 100.0 % of profiles |
| `look_after` | 0.0 % of profiles | 100.0 % of profiles |
| `restore_standing` | 0.0 % of profiles | 0.0 % of profiles |

**28.6 % of all 30618 (profile, want, context) cells had only one intention in the running.** In those, every profile in the sweep forms the same intention, and no amount of psychology could change it.

##### The known failure, off the cast

`look_after` collapsed to `protect` in 851 of 851 decisions on the shipped cast. Across 2187 held-out profiles in two contexts, the number of times anything else won: **306**.
Examples: p6 in company -> prevent_argument; p7 in company -> prevent_argument; p84 in company -> share_information; p85 in company -> share_information; p89 in company -> prevent_argument.

##### The innocent theft, off the cast

`took_what_was_not_mine` was formed 2096 times in company across the sweep, of which **91** (4.3 %) were by a profile holding no belief that they are answerable for anything.

#### G4. Counterfactuals on held-out people

Each perturbation is applied to the whole sweep, one thing at a time, everything else held. A cell is one (profile, want) pair: 15309 of them.

| Perturbation | Read by a rule | Cells whose intention changed | Share |
|---|---|---|---|
| C1 three others come into the room | **yes**, six rules gate on it | 8407 | 54.9 % |
| C3 they come to believe they lead the family (0 -> 0.95) | **yes**, two rules scale on it | 202 | 1.3 % |
| C3 they come to believe they are answerable for the can (0 -> 0.95) | **yes**, one rule scales on it | 972 | 6.3 % |
| C2 hunger 0.30 -> 0.95 | **no rule reads it** | **0** | 0.0 % |
| C2 moved to a room with no food | **no rule reads it** | **0** | 0.0 % |

| C5 | the want itself | profiles for which changing the want changes the intention | 2187 of 2187, 100.0 % |

##### C4. One trait at a time

Every seventh profile in the sweep, in both contexts, with a single trait forced low and then high and nothing else touched. Both contexts matter: four of the ten rules are gated on being alone or on having company, so a trait only those rules read would look deaf if it were asked in one context only.

| Trait | Read by a rule | Cells changed by moving it 0.15 -> 0.85 | Share |
|---|---|---|---|
| `anxious` | yes | 0 | 0.0 % |
| `cautious` | yes | 300 | 6.8 % |
| `dominant` | yes | 289 | 6.6 % |
| `empathetic` | yes | 456 | 10.4 % |
| `honest` | yes | 562 | 12.8 % |
| `impulsive` | **no** | 0 | 0.0 % |
| `proud` | yes | 86 | 2.0 % |

**Traits that never changed an intention: `anxious`, `impulsive`.**

#### G5. Replay

**300 of 300 held-out signatures identical on replay.** The selector draws no random number, so this is exact rather than probable.

#### G6. Does having more rules beat having more weight

This is the second question and it is not about generalization. Contributions for one intention are **summed**. So two things that look different on the page may be the same arithmetic, and the way to find out is to separate them.

Three conditions, same people, same wants, same circumstances, same beliefs, same traits, same values:

| | Rules | Total weight for that intention |
|---|---|---|
| **A** frozen | 10 | unchanged |
| **B** plus an exact clone of one rule under a new id | 11 | **doubled** for that intention |
| **C** with one rule split into two halves | 11 | **unchanged** |

Nothing on disk changes: B and C are built in memory from the frozen rules.

| Rule cloned or split | Intention | Cells changed by **cloning** it (B) | Cells changed by **splitting** it (C) |
|---|---|---|---|
| `pulling_rank_needs_an_audience` | `assert_authority` | 187 (4.3 %) | 0 (0.0 %) |
| `being_the_one_who_decides_it` | `assert_authority` | 185 (4.2 %) | 0 (0.0 %) |
| `somebody_has_to_do_it` | `take_responsibility` | 779 (17.8 %) | 0 (0.0 %) |
| `doing_it_where_nobody_is_watching` | `take_responsibility` | 0 (0.0 %) | 0 (0.0 %) |
| `so_that_they_know_too` | `share_information` | 529 (12.1 %) | 0 (0.0 %) |
| `standing_between_them_and_it` | `protect` | 308 (7.0 %) | 0 (0.0 %) |
| `keeping_it_off_them` | `protect` | 226 (5.2 %) | 0 (0.0 %) |
| `not_making_a_scene_of_it` | `prevent_argument` | 327 (7.5 %) | 0 (0.0 %) |
| `letting_it_go_for_now` | `prevent_argument` | 6 (0.1 %) | 0 (0.0 %) |
| `what_you_did_in_the_night` | `took_what_was_not_mine` | 351 (8.0 %) | 0 (0.0 %) |

**Over 4382 cells per rule and 10 rules: cloning changed the intention 2898 times; splitting changed it 0 times.**

Splitting a rule in two adds a rule and adds no weight. Cloning a rule adds a rule and doubles the weight. If the count mattered, both would move the answer. Only one does, which means **the rule count is not the bias; the sum is.** Writing a second rule for an intention and raising the first rule's numbers are the same operation as far as the mechanism can tell.

##### `look_after`, diagnosed by removal

Not a fix. The frozen file is untouched; this asks what the collapse is made of by running the sweep with one rule withheld in memory.

| Rules used | Distinct intentions for `look_after` across the sweep | Distribution |
|---|---|---|
| **all ten, as frozen** | 3 | `protect` 93.5 %, `share_information` 6.1 %, `prevent_argument` 0.5 % |
| without `keeping_it_off_them` | 3 | `none` 50.0 %, `share_information` 24.0 %, `protect` 22.2 %, `prevent_argument` 3.8 % |
| without `standing_between_them_and_it` | 3 | `protect` 56.9 %, `share_information` 37.4 %, `prevent_argument` 5.8 % |

The frozen hash is checked again at the end of this test to show that none of this touched the file.

**sha256 after the whole run: `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` — unchanged.**

---

## predictions.md

### Intention formation, generalization: predictions

Written and committed **before the held-out people were run through the frozen
rules**, together with the file that declares them. Kept as written.

#### The two questions, kept apart

The brief is right that these can come apart, and the report keeps them apart:

| | Question |
|---|---|
| **Generalization** | Do the rules work on cases they were not authored against? |
| **Scoring validity** | Do they rank intentions for psychologically meaningful reasons? |

A mechanism can generalize perfectly and still score for a bad reason. H2 below
is about the second and is measured independently of the first.

#### What is frozen

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| git blob | `41112b95d75d75786ad4df442e25330c74c5d6b3` |
| Bytes | 6,956 |
| Commits touching it | one, `8ede500`, before the fixture that reads it existed |

Ten candidate rules. Not one byte changes. No rule is added for a held-out
person, no weight is altered, no intention is renamed. The rule-count experiment
(H2) builds its extra rules **in memory at run time**, so the file on disk stays
identical and is hashed again at the end of the run to prove it.

#### Holdout design

**Option A, the declared four.** Four people whose traits, values and beliefs are
placed by a stated principle in a region the shipped cast does not occupy. The
cast is nowhere below 0.50 on empathetic or honest, nowhere above 0.70 on
cautious, and never high on dominant and empathetic together; each held-out
person breaks at least one of those. Declared in
`Data/Experiments/held-out-people.json` and committed before running.

**Option A+, the sweep, which is the real evidence.** Every combination of the
seven shipped traits at three levels: **2,187 profiles**, enumerated
mechanically, with values and beliefs rotating by index. Nobody designed them, so
nothing in them can have been fitted to. If the mechanism is a table fitted to
four people, a uniform sample of trait space is where that shows.

No character-specific rule is written, and the rules cannot contain one: they are
hashed, and searched for character names, and the search result is reported.

#### Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | The frozen rules give a held-out profile at least two reachable intentions for at least some wants | every want is single-valued for every held-out profile |
| P2 | At least one meaningful contextual perturbation changes the intention for held-out people | no context ever moves it |
| P3 | At least one meaningful belief, trait or value perturbation changes it | no state change ever moves it |
| P4 | An irrelevant perturbation never changes it | one does |
| P5 | Changing the want changes the reachable intention space | the reachable set is the same for every want |
| P6 | Held-out intentions arise from generic state, not character-specific rules | any rule names or is keyed on a character |
| P7 | Deterministic under replay | any replay differs |
| P8 | The `look_after -> protect` collapse either reproduces outside the cast or does not; report which | not measured |
| P9 | The redundant-rule test settles whether rule count biases the result | not measured |
| P10 | No character-specific production code or data is required | any is |

**Committed in advance, and riskier:**

- **P8, my expectation:** the collapse **will** reproduce across the sweep, and
  for nearly every profile. `protect` has two candidates to its rivals' one, so
  its total is the sum of two positive contributions where theirs is one. A
  person would have to be very low on empathy *and* closeness to escape it. If
  I am right, the failure is structural rather than a property of this cast.
- **P9, and this is a correction I expect to have to make.** My last report said
  "two rules beat one". That is loose. Contributions are **summed**, so what beats
  one rule is not the *count* but the *total weight*, and a second rule is simply
  a way of adding weight. The sharp test separates them:

  | Condition | Rules | Total weight for that intention | Expect |
  |---|---|---|---|
  | A | frozen | unchanged | baseline |
  | B | A + an exact clone of one rule under a new id | **doubled** | flips often |
  | C | A with one rule split into two halves | **unchanged** | flips **never** |

  If B flips and C does not, then rule count as such is *not* the bias; additive
  weight is, and writing another rule is indistinguishable from raising a number.
  That is a worse finding than the one I reported, not a better one, because it
  means the pathology cannot be avoided by counting rules more carefully.

- I expect the sweep to show the mechanism is **strongly sensitive to two or
  three traits and nearly blind to the rest**, because ten rules cannot read
  seven traits evenly. If so, "it generalizes" and "it uses the person" are both
  true and still thinner than they sound.
- I expect **`empathetic` to be the most load-bearing trait** and `impulsive` to
  be read by nothing at all — no candidate rule names it.

**What would count as failure:** the sweep producing one intention per want
regardless of the person (a table), or held-out people producing nothing at all
(rules too narrow to transfer).

---

## results.md

### Intention formation, generalization: results against the predictions

The measurements are in `measurements.md`, generated by
`IntentionGeneralizationExperimentTests`. The predictions and the held-out people
were committed together, before any of it was run.

#### Runs

| | |
|---|---|
| Rule file | frozen. sha256 `61e6412e...b099d92` verified at the **start and the end** of the run, unchanged |
| Rules | 10, unedited. Nothing added for a held-out person |
| Declared held-out people | 4, placed outside the cast's trait ranges by stated principle |
| Sweep | **2,187** mechanically enumerated profiles |
| Cells | 30,618 (profile x want x context) for the sweep measures; 4,382 per rule for the rule-count experiment |
| Randomness | none |
| Production changes | **none** |

#### Predictions

| # | Prediction | Result | Evidence |
|---|---|---|---|
| P1 | The frozen rules give a held-out profile two or more reachable intentions for some wants | **PASS** | 28 of 28 held-out cells formed an intention, using 4 distinct ones. Across the sweep every want produced 2 or 3 |
| P2 | A meaningful contextual perturbation changes the intention | **PASS** | Company arriving changed it in **54.9 %** of 15,309 cells |
| P3 | A meaningful belief, trait or value perturbation changes it | **PASS** | Believing oneself answerable: 6.3 %. Believing oneself head of the family: 1.3 %. Single traits: up to 12.8 % |
| P4 | An irrelevant perturbation never changes it | **PASS** | Hunger 0.30 -> 0.95: **0 of 15,309**. Moved to a foodless room: **0 of 15,309** |
| P5 | Changing the want changes the reachable intention space | **PASS** | 2,187 of 2,187 profiles |
| P6 | Held-out intentions arise from generic state, not character-specific rules | **PASS** | 0 character names in any rule id, intent, want or scaler field. The only person-token is `$self` |
| P7 | Deterministic under replay | **PASS** | 300 of 300 held-out signatures identical |
| P8 | Report whether the `look_after -> protect` collapse reproduces off the cast | **REPORTED: it does not** | 100 % on the cast (851 of 851); **93.5 %** across the sweep, with 306 escapes to `share_information` and `prevent_argument`. A strong tendency, not a structural certainty |
| P9 | The redundant-rule test settles whether rule count biases the result | **PASS, and it settles it against my earlier wording** | Cloning a rule: 2,898 flips. Splitting a rule in two: **0 flips**, over 4,382 cells per rule |
| P10 | No character-specific production code or data required | **PASS** | No file under `Scripts/Core` touched; no shipped data edited |

#### The riskier claims, committed in advance

| Claim | Result |
|---|---|
| The collapse **will** reproduce across the sweep, for nearly every profile, making it structural | **FALSIFIED.** It reproduces as a 93.5 % tendency, not as a certainty. 306 held-out profiles escape it. The totality on the cast is a property of that cast |
| Cloning a rule flips outcomes; splitting one in half does not — so the bias is weight, not count | **HELD, exactly.** 2,898 against 0 |
| The mechanism is strongly sensitive to two or three traits and nearly blind to the rest | **HELD.** `honest` 12.8 %, `empathetic` 10.4 %, `cautious` 6.8 %, `dominant` 6.6 %, `proud` 2.0 %, `anxious` **0.0 %**, `impulsive` **0.0 %** |
| `empathetic` will be the most load-bearing trait, and `impulsive` read by nothing | **HALF.** `impulsive` is indeed read by no rule. But the most load-bearing trait is `honest`, not `empathetic` |

#### Two findings the predictions did not anticipate

**A trait can be read and still be deaf.** `anxious` appears in a candidate rule
and changed the intention in **0 of 4,382** cells, in both contexts. Its only
rule, `letting_it_go_for_now`, is either the sole candidate in the running — in
which case it wins whatever it weighs — or it loses every time. Being read by a
rule and being able to change an outcome are different properties, and only the
second one matters.

**Where only one intention is in the running, the person is irrelevant by
construction.** Across all 30,618 cells, **28.6 %** had exactly one intention with
any candidate matching. Alone, that is **100 %** of profiles for
`avoid_exposure`, `find_out`, `keep_peace` and `look_after`. In those cells every
one of the 2,187 profiles forms the same intention, and no psychology could
change it. This, not the summation, is what produces the flat columns.

#### The answer to the two questions, separately

| | Verdict |
|---|---|
| **Generalization** — does the mechanism work outside the authored cases? | **Yes.** 2,187 undesigned profiles produced **56 distinct signatures**, the most common covering 11.6 %. A table keyed on the want would have produced one |
| **Scoring validity** — does it rank intentions for meaningful reasons? | **Not established, and partly refuted.** Adding a duplicate rule moves 2,898 outcomes without changing anything about the person. Two of seven traits can never move anything. 28.6 % of cells have nothing to compare |

