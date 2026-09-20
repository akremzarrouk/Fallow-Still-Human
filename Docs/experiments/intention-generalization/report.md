# Intention formation: does it generalize

*Does the mechanism encode reusable relationships between a want, a person and a
situation, or is it a table fitted to four people?*

## 1. Hypothesis

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

## 2. What was frozen

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

## 3. Holdout design

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

## 4. Is there character-specific encoding?

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

## 5. Results: generalization

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

## 6. Results: scoring validity, which is a different question

### The rule-count experiment

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

### Two structural limits the sweep exposed

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

## 7. The known failure, off the cast

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

## 8. Limitations and overfitting risks

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

## 9. Classification

| | |
|---|---|
| **PROVEN** | The mechanism generalizes off the authored cast. 2,187 undesigned profiles, 56 distinct signatures, all seven wants many-valued, 28 of 28 held-out cells formed. Zero character-specific encoding. Exactly reproducible (300 of 300). Provably blind to unread state (0 of 15,309 on two irrelevant perturbations). Responds to generic state: five traits and two beliefs each move outcomes. **And the scoring principle is additive rather than principled: cloning a rule moves 2,898 outcomes, splitting one moves 0.** |
| **PLAUSIBLE** | That the variation is psychologically meaningful. `warden` differing from Daniel on `find_out` reads correctly, but that is a judgement and this experiment does not evidence it |
| **UNPROVEN** | That the approach survives a larger vocabulary, a second house, or scalers on feelings and memories. That 28.6 % of cells having nothing to compare is fixable without redesigning candidate gating |
| **FAILED** | The scoring principle as a principle. A duplicate rule changes the answer with the person untouched. Two of seven traits can never change anything, one of them despite being read. And `took_what_was_not_mine` is formed by innocent people at the same rate off the cast as on it |
| **UNKNOWN** | Whether a mechanism with these properties would still generalize once the scoring were fixed — every number here was produced under the broken scoring |

## 10. Verdict

# MODIFY

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

## 11. The question the brief asks to answer explicitly

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
It takes about twenty seconds. Suite: PENDING.
