# Intention representation: predictions

Written and committed **before the fixture that measures any of this existed**.
The predictions come from reading the frozen rule file, the shipped character
sheets and the ranking experiment's published numbers; nothing was simulated to
write them. They are kept as written, and `results.md` scores each one.

Every prediction is marked as one of two kinds:

- **analytic**: it follows from the rule file by arithmetic. If it fails, the
  fixture is wrong or I misread the file.
- **empirical**: it is a guess about a measurement. If it fails, that is a
  finding.

## What this experiment is for

The ranking experiment showed that ranking by an anonymous sum treats a restated
reason as new evidence. It also showed that no formula over anonymous
contributions can escape that, and it proposed that a rule should carry the
identity of the evidence it reads.

**This experiment treats that proposal as a hypothesis, not a conclusion.** It
builds the proposal (B), an alternative that answers the same problem
differently (C) and the current mechanism (A). It runs all of them over the same
frozen file, the same people and the same tests. The question is not which one
gives nicer numbers. The question is what information the ranking layer has to
keep, so that it can say why a person intends something without the way the
rules were written becoming part of the person.

## What is frozen

| | |
|---|---|
| Rule file | `Assets/_Project/Data/Experiments/intentions.json`, sha256 `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92`, hashed at the start and the end |
| Selector | `IntentionSelector.Form`, unedited. A must reproduce it bit for bit |
| Production | nothing under `Scripts/Core`, no shipped data, weights, wants, traits, values, emotions, memories, actions or candidate generation |
| People | the 2,187-profile sweep; the shipped cast at the top of the morning; the shipped cast inside 50 real baseline mornings (5 variants x 10 seeds, `IntentOfAct` left null, so every morning is the shipped baseline) |

Stages 1 and 2 are shared by every representation and not touched: which
intentions a want makes available, and which of them the circumstance leaves
compatible. The levels a person supplies are shared too, read through the
shipped `ScalerEval`. Only what happens to those levels afterwards differs.

## The representations, fixed now

A rule is made of **statements**. A term is a statement that some evidence, at
some coefficient, supports an intention. The base is a statement that the
circumstance the rule applies in supports it. The representations differ in what
they recognise as the same statement, and in what they do with a repeat.

**Evidence keys**, the identity B uses. They are derived mechanically from
fields the rule file already has, with nothing invented:

| Read | Key | Example |
|---|---|---|
| trait | kind and name | `trait:honest` |
| value | kind and name | `value:family_safety` |
| belief | predicate and argument tokens | `belief:role_claim($self,leads_family)` |
| emotion | name and target token | `emotion:anger@$anybody` |
| circumstance (a base) | the rule's gate | `circumstance:others>=1`, `circumstance:any` |

A base of exactly zero states nothing, and is not a statement.

| | Representation | Unit of identity | A repeat of the same unit | Negative totals | Ties |
|---|---|---|---|---|---|
| **A** | anonymous contributions: the current selector, reproduced exactly (the control) | none | adds | a rule weighing <= 0 is discarded | the name that sorts first |
| **A°** | A without the discard. **An ablation, not a candidate.** It exists to separate what the discard does from what identity does | none | adds | count | reported |
| **B** | **evidence-identified** | the evidence key, per intention | **the same statement twice** counts once. **Two different statements of the same evidence** (a conflict) count once at the strongest, and the conflict is recorded | count | reported |
| **C** | **reason-identified** | the reason: intention, gate and the *set* of evidence keys it reads | the same reason twice counts once. The same reason with different numbers counts once, at the strongest of each number, and is recorded. **Different reasons add, even if they read some of the same evidence** | count | reported |

**What C keeps and throws away, compared with B.**

- **C keeps** the grouping of evidence into reasons. It knows that "standing
  between them" is one configuration of empathy, family safety and anxiety.
- **C throws away** the identity of a single piece of evidence across reasons.
  It cannot see that two different reasons for `protect` both count the same
  person's empathy.
- **B keeps** that identity, and throws away the grouping. Once statements are
  keyed by evidence, which reason a statement came from is provenance for the
  trace, not part of the arithmetic.

The two answer one question oppositely: **is one fact about a person, used by
two different reasons, one piece of evidence or two?** B says one; C says two.
Neither answer is in the data.

**The tie policy** for A°, B and C is to report the tie. If the top two scores
are within 1e-9, the outcome is the set of tied intentions and nothing is chosen
between them. In the sweep, every contribution is a whole multiple of 0.0025, so a
gap below 1e-9 is a real tie.

**The conflict policy** for B and C is "the strongest statement". That is a
choice, not a finding. To show how much it matters, B is also scored once with a
different policy (**B-mean**, the mean of the conflicting statements), on the
frozen file only. B-mean is not a candidate.

## The tests, fixed now

On all 30,618 cells (profile x want x circumstance). "Per rule" means applied
to each of the ten rules in turn: 306,180 (rule, cell) pairs.

| | Invariant | Transformation |
|---|---|---|
| R1 | rule order | reverse the rule list |
| R2 | rule names | give every rule a new id |
| R3 | intention names | rename the intentions so that their alphabetical order reverses, then map back |
| R4a | restatement | W + W: an exact copy, per rule |
| R4b | restatement, written differently | W + W': the same rule with its terms reversed and a new id, per rule |
| R4c | near restatement | W + 0.99W, per rule |
| R4d | **partial** restatement | W + W minus its last term. Nothing in the copy is new. Per rule |
| R5 | proportional splitting | W -> W/2 + W/2, and W -> 4 x W/4, per rule |
| R6 | weight | W -> 2W, per rule |
| R7 | monotonicity | double a rule's base and positive factors only: its intention must never lose |
| R8 | locality | no change from any per-rule rewrite outside the cells where that rule is compatible |
| R9 | grouping | split a rule by term; merge co-compatible rules by putting their statements in one rule |
| R10 | candidates | the set of intentions in the running equals the compatible set, in every cell, under every rewrite and every person move |

The live-state cells add what the sweep lacks: a real mind with real beliefs
and feelings. They are every decision moment of the 50 baseline mornings, asked
about every want. An emotion is audited there by setting its level to zero in
the arithmetic and seeing whether the intention moves.

## Predictions

### 1. Which invariants A fails (analytic, from the ranking experiment)

| | Result expected for A |
|---|---|
| R1, R2 | pass: 0 |
| R3 | **fail**: 12 cells decided by name (plus 13 decided by rounding) |
| R4a | **fail**: 19,992 |
| R4b | **fail**: 19,992, give or take tie cells, where reversing a rule's terms moves the last bit |
| R4c | **fail**: 19,844 |
| R4d | **fail**. *Empirical*: between 14,000 and 21,000. The partial copy of `not_making_a_scene_of_it` drops its negative `dominant` term, so it adds *more* than an exact copy does |
| R5 | pass: 0 for halves and quarters |
| R6 | pass: responds, 19,992 |
| R7 | pass: 0 changes away |
| R8 | pass: 0 outside |
| R9 | **fail**: term split 469 (through the discard); merge 0 |
| R10 | **fail**: the candidate set is smaller than the compatible set in 243 cells |

### 2. Which invariants B is expected to satisfy (analytic)

| | Result expected for B |
|---|---|
| R1, R2, R3 | pass: 0. Order cannot matter because B sums in key order; names are not read; ties are reported |
| R4a, R4b, R4c, R4d | **pass: 0 for all four.** Every statement in a copy, a reordered copy, a 0.99 copy or a partial copy is a statement B already holds, at the same or a weaker coefficient |
| R5 | **fails by design, and says so.** W/2 + W/2 is two identical statements of half strength. That is indistinguishable from a half-strength reason written twice, which B must not strengthen. So B reads the split as a weaker reason: the outcome changes, and **every changed cell is flagged** as holding restated evidence. The theorem says a representation can do no better; the honest answer is to reject such a file |
| R6 | pass: responds |
| R7 | pass: 0 away |
| R8 | pass: 0 outside |
| R9 | pass: 0 for the term split and for the merge |
| R10 | pass: 0 cells |

### 3. Which invariants C is expected to satisfy (analytic)

| | Result expected for C |
|---|---|
| R1, R2, R3 | pass: 0 |
| R4a, R4b, R4c | pass: 0. A reason's identity is a set, so reordering does not hide it |
| **R4d** | **fail**. A partial copy reads a different set of evidence, so C takes it for a different reason and adds it. *Empirical*: the same count as A's R4d, give or take the cells A breaks by name |
| R5 | fails by design, and is flagged, for the same reason as B |
| R6, R7, R8, R9, R10 | pass |

**So the tests separate B from C at exactly one point:** a restatement that
drops a term. That is the kind of rewrite an author makes without noticing.

### 4. Does B preserve what the generalization experiment proved?

| | Prediction | Kind |
|---|---|---|
| 4.1 | 28.6 % single-candidate cells: **identical** (8,748). Stages 1 and 2 are shared | analytic |
| 4.2 | No character-specific rule: identical, since the file is the same | analytic |
| 4.3 | Hunger and a foodless room: **0** changes, of 15,309 each | analytic |
| 4.4 | Replay: exact | analytic |
| 4.5 | **B differs from A° in three groups only**: `look_after`, `guard_supplies` and `restore_standing`, all in company. Those are the only places where two compatible reasons for one intention read the same evidence: `protect` reads `empathetic` in `standing_between_them_and_it` and in `keeping_it_off_them`; `assert_authority` reads `control` and `role_claim` in `pulling_rank_needs_an_audience` and in `being_the_one_who_decides_it`. In each case B drops the weaker statement, so **every change B makes is away from `protect` or away from `assert_authority`** | analytic |
| 4.6 | `look_after -> protect` in company falls from 86.0 % to between 65 % and 80 % | empirical |
| 4.7 | `assert_authority` in company falls from 81.1 % (`restore_standing`) and 80.6 % (`guard_supplies`) to between 55 % and 75 % | empirical |
| 4.8 | Circumstance changes: fewer than 8,407, by less than 10 % | empirical, weak |
| 4.9 | Distinct company signatures: not 56. I expect more rather than fewer, because three nearly collapsed wants become mixed. *More is not better*, and this is a prediction, not a goal | empirical, weak |

### 5. Does C preserve it?

| | Prediction | Kind |
|---|---|---|
| 5.1 | **C reaches the same intention as A in every cell except the real ties.** The frozen file holds no two rules with the same reason signature. The discard never changed a winner. So C differs from A only where A breaks a tie by a name or by rounding: 25 cells, which C reports as ties | analytic |
| 5.2 | Hence 28.6 %, blindness, replay and no character rules all hold. The 56 signatures and the 8,407 changes hold up to the tie cells | analytic |

### 6. The 35.7 % forced share

| | Prediction | Kind |
|---|---|---|
| 6.1 | **Unchanged at 35.7 % under A, A°, B and C.** B changes nothing in any group that is forced now | analytic |
| 6.2 | Its causes: the four K = 1 groups (28.6 %), cause 1, no alternative candidate. Plus `restore_standing` alone (7.1 %), where `prevent_argument` is cause 2, dominated for every possible person, and `assert_authority` is cause 4, not dominated, but needing anger that no sweep profile carries. **No forced cell is caused by the representation** (cause 3) | analytic |
| 6.3 | Even in the live mornings, which do carry anger, `assert_authority` **never** wins `restore_standing` alone for the real cast. Daniel is the most disposed to it, and he would need anger of 2.2 on a scale that stops at 1 (0.500 + 0.3 x anger against his 1.158). So for the cast this convergence is not an artifact of a sweep without feelings | analytic |

### 7. Person sensitivity with the candidates fixed

| | Prediction | Kind |
|---|---|---|
| 7.1 | The compatible set changes in **0** of 642,978 person moves, under every representation | analytic |
| 7.2 | With the candidate set fixed, sensitivity stays **non-trivial**: above 1 % of contested pairs for A, B and C | empirical |
| 7.3 | C's sensitivity equals A's (6.1 %) to within the tie cells. B's is between 6.1 % and 8 %, because B makes three groups less lopsided | empirical |

### 8. Semantic counterfactuals: the same act, different reasons

The matched cases are taken from reality, not built. Every `check_pantry` that a
real baseline morning chose, for one of the four wants whose shipped proposals
lead to `check_pantry`, is one case. For each case, every other member of the
cast is placed at the same minute of the same morning: the same world state,
room, company size, want and act, with their own real mind at that minute. The
four wants are read from `decisions.json`, not typed in.

| | Prediction | Kind |
|---|---|---|
| 8.1 | All three representations can state a person's reasons as person evidence, and the reasons differ between matched people | empirical |
| 8.2 | The brief's example, reproduced from data: `find_out` in the kitchen in company, at the top of the morning. Daniel forms `assert_authority`, led by `trait:dominant`; Leo forms `take_responsibility`, led by `value:family_safety`. **The same under A, B and C**, because no shared evidence is involved | analytic |
| 8.3 | **Where representations disagree about *why*.** `restore_standing` and `guard_supplies` in company: Daniel's `assert_authority` is led by `value:control` under A and C, because two rules state it (0.35 + 0.25 at weight 1.0 = 0.60). Under B it is led by `trait:dominant` (0.45 x 0.85 = 0.383, against `control` at 0.35). **The label is the same; the stated reason is a property of how the rules were written** | analytic |
| 8.4 | Restating one rule changes the **leading reason** of some real decisions under A, and of none under B. C is immune to exact restatement and not to partial restatement | empirical for A's count; analytic for B's zero |

### 9. Does previously idle evidence become influential merely because of representation?

| | Prediction | Kind |
|---|---|---|
| 9.1 | **No, under B or C.** `anxious` stays idle everywhere. `honest` still cancels in `get_food`, because the two rivals there are different intentions and B only merges within one. `respect` is still live only through anger. No evidence changes status between A, B and C | analytic |
| 9.2 | **Under A, restating a single rule *creates* influence.** Copying `what_you_did_in_the_night` gives `took_what_was_not_mine` 0.60 of `honest` against 0.30, so honesty, which cannot choose in `get_food` today, starts to choose. Under B, never. Under C, not by an exact copy, but yes by a partial one | analytic |
| 9.3 | In the live-state cells, zeroing `anger` changes some intention, and so does zeroing `anxiety`, under every representation. For `shame` I do not know | empirical |

### 10. Can a representation tell "the same evidence twice" from "two different pieces of evidence" without counting rules?

**Analytic.** Both B and C recognise repeats by content and not by rule count. B
catches every repeat of a piece of evidence, including partial restatements and
splits. C catches only repeats of a whole reason.

**Neither can decide the one case the frozen file actually contains:** the same
fact read by two different reasons. B counts it once and C counts it twice, and
the invariants cannot choose between them, because both pass every test except
the one that separates them (R4d). **That is a semantic decision the
representation has to make explicit, not something a formula or a validator can
find.** On the frozen file it decides the three groups of prediction 4.5.

## What would decide the verdict

The verdict is about the representation, not about Fallow. Committed now:

| Verdict | If |
|---|---|
| **KEEP** (evidence identity, as B defines it, is the representation to design against) | B passes R1 to R4, R6 to R10, and R5 by explicit detection. It keeps 28.6 %, blindness, replay and non-trivial fixed-candidate sensitivity. It expresses person-specific reasons for the same act, stable under restatement. C fails a test that B passes. **And** B's changes to the frozen file's conclusions depend on no choice B had to invent |
| **MODIFY** | all of KEEP holds, except that **some conclusion B reaches depends on a policy the representation does not declare**: the treatment of one fact used by two reasons, or the conflict policy. Then evidence identity is necessary but not sufficient, and the representation needs an explicit field for it |
| **REBUILD** | B fails a test it was built to pass (R1 to R4, R6 to R10); or it loses person dependence (fixed-candidate sensitivity under 1 %) or blindness; or it cannot state different reasons for the same act |
| **ABANDON** | no representation can state reasons as person evidence at all |

**My expectation is MODIFY.** B should pass everything it is built for. But
prediction 4.5 says B changes real conclusions in three groups. It does so
through a policy (one fact counts once, at the strongest statement) that the
data cannot justify and C contradicts. Two things would falsify MODIFY: B
changing no conclusion outside the tie cells, which would mean KEEP; or B failing
one of its own tests, which would mean REBUILD.

**Not claimed by any outcome here:** that any representation's conclusions are
psychologically correct. Passing an invariant proves a property of the
mechanism, not a fact about people.
