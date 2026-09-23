# intention-representation: all documents

Merged by `merge-slice-docs.py` from the 4 Markdown files in `Docs/experiments/intention-representation/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)

---

## report.md

### Intention representation: what the ranking layer must keep

*Can a representation that knows what evidence each reason reads stop the way
rules are written from becoming part of the person, while keeping everything
the intention mechanism has already been shown to do?*

#### 1. The answer, first

**Partly. Evidence identity is necessary, and it is not sufficient.**

The evidence-identified representation (**B**) does everything it was built to
do:

- **Restating a reason never changes a conclusion in B.** That covers an exact
  copy, a copy with its terms reordered, a 0.99 copy and a copy missing one
  term: 0 changes in 306,180 cases each.
- **B knows when it is changing something.** A weight-preserving split does
  change B's conclusions, as the ranking experiment's theorem says any
  representation must. But B flags all 78,732 cells where the split rule
  applies and changes nothing without flagging it.
- **B keeps what was already proven.** The 28.6 % of single-candidate cells,
  blindness to hunger and to the room, exact replay and the absence of any
  character-specific rule all hold. With the candidates held fixed, the person
  still decides 7.1 % of contested moves.
- **B's stated reasons stay the same however the rules are rewritten.** It
  expresses the different reasons behind the same act from the existing rules
  and person data alone.

The alternative (**C**, which identifies whole reasons rather than pieces of
evidence) passes the same tests except one. **A partial restatement fools it:**
19,062 changes, none flagged. That is the ordinary way an author restates a
reason without noticing. So identity at the level of evidence, not of rules or
reasons, is what restatement invariance requires.

**But B changes 660 real conclusions on the frozen file, and the data cannot say
whether it should.** In five places, two *different* reasons for the same
intention read the same fact about a person:

- `standing_between_them_and_it` and `keeping_it_off_them` both read empathy for
  `protect`;
- `pulling_rank_needs_an_audience` and `being_the_one_who_decides_it` both read
  control and the role belief for `assert_authority`.

B counts such a fact once and C counts it twice. Every invariant is satisfied
either way. Even *how* B counts it once is a choice: taking the mean of the two
statements instead of the strongest changes another 242 conclusions.

So the ranking layer must keep what B keeps, and it also needs something no
representation here has: **an explicit, declared statement of how one fact
supports an intention when more than one reason cites it.**

**Verdict: MODIFY**, for the representation experiment, by the criteria committed
before it ran (section 14).

#### 2. What was run

| | |
|---|---|
| Rules | the frozen ten, sha256 `61e6412e...b099d92`, checked at the start and the end: **unchanged** |
| Production | nothing under `Scripts/Core`; no shipped rule, weight, want, trait, value, emotion, memory, action or candidate generation |
| Representations | **A** the current selector, reproduced exactly (the control); **A°** A without the discard (an ablation); **B** evidence-identified; **C** reason-identified; and **B-mean**, used only to show how much B's conflict policy decides |
| Sweep | the 2,187 profiles of the generalization experiment: **30,618** cells per rule set |
| Rewrites | 13 kinds, 94 rewritten rule sets, all in memory: 2.9 million staged decisions, each read by all four representations |
| Person moves | 21 single-attribute moves per profile: 642,978 pairs |
| Real mornings | 50 baseline mornings (5 variants x 10 seeds, `IntentOfAct` left null). **3,689** decision moments, each asked about every want: **25,823** live cells carrying real beliefs and feelings. **257** real pantry-checks and **771** matched pairs |
| Randomness | none |

**A is the selector.** Rebuilt from its stages, A differs from
`IntentionSelector.Form` in **0 of 30,618** cells, and every winning weight is
equal to the bit. A's duplicate count, taken through `Form` itself, is 19,992,
the published figure.

**One clarification, made before anything ran.** The committed predictions say a
conflict is settled by "the strongest" statement. The fixture takes that to mean
the largest in magnitude, keeping the sign. Taking the largest value instead
would silently weaken a negative term: a 0.99 copy of `-0.25` would win as
`-0.2475`.

#### 3. The four readings of the same file

A rule is made of **statements**. A term is a statement that some evidence
supports an intention at some coefficient. The base is a statement about the
circumstance the rule applies in. Evidence keys come mechanically from fields
the file already has: `trait:honest`, `value:family_safety`,
`belief:role_claim($self,leads_family)`, `emotion:anger@$anybody`,
`circumstance:others>=1`.

| | Identity | A repeat | Negative totals | Ties |
|---|---|---|---|---|
| **A** | none | adds | a rule weighing <= 0 is discarded | the name that sorts first |
| **A°** | none | adds | counted | reported |
| **B** | the evidence key, per intention | the same statement again counts once; a different statement of the same evidence is a **conflict**, counted once at the strongest and recorded | counted | reported |
| **C** | the reason: intention, gate and the set of evidence it reads | the same reason again counts once (at the strongest of each number if they differ); **different reasons add, whatever they share** | counted | reported |

**What C keeps and discards, compared with B.** C keeps the grouping of evidence
into reasons: it knows "standing between them" is one configuration of empathy,
family safety and anxiety. It discards the identity of a single piece of
evidence across reasons. B keeps that identity and discards the grouping, which
survives only as provenance for the trace. They answer one question oppositely:
**is one fact, cited by two reasons, one piece of evidence or two?**

#### 4. The invariants

Cells whose outcome changed, over 30,618; per-rule tests summed over the ten
rules. "Flagged" means the representation recognised the rewrite as a
restatement or conflict.

| | Rewrite | A | A° | B | C |
|---|---|---|---|---|---|
| R1 | reverse the rule order | 0 | 0 | 0 | 0 |
| R2 | rename every rule | 0 | 0 | 0 | 0 |
| R3 | rename the intentions | **12**, all ties | 0 | 0 | 0 |
| R4a | W + W | **19,992** | **20,021** | 0 | 0 |
| R4b | W + W', terms reversed, new id | **19,992** | **20,021** | 0 | 0 |
| R4c | W + 0.99W | **19,844** | **19,869** | 0 | 0 |
| R4d | W + W minus its last term | **18,938** | **19,062** | 0 | **19,062, none flagged** |
| R5a | W -> W/2 + W/2 | 0 | 0 | 15,210, **all flagged** | 13,796, **all flagged** |
| R5b | W -> 4 x W/4 | 0 | 0 | 19,340, **all flagged** | 18,632, **all flagged** |
| R6 | W -> 2W | 19,992 | 20,021 | 22,520 | 20,021 |
| R7 | base and positive factors x 2: changes **away** from the strengthened intention | **0** | **0** | **0** | **0** |
| R8 | changes outside where the rewritten rule applies, every per-rule test | **0** | **0** | **0** | **0** |
| R9a | split by term | **469** | 0 | 0 | 0 |
| R9b | merge co-compatible rules | 0 | 0 | 0 | 0 |
| R10 | cells where the candidates are not the compatible set: frozen file / every rewrite | **243 / 22,113** | 0 / 0 | 0 / 0 | 0 / 0 |

| | A | A° | B | C |
|---|---|---|---|---|
| **Fails** | R3, R4a-d, R9a, R10 | R4a-d | R5 (by design, and flagged) | **R4d (silently)**, R5 (by design, and flagged) |

What the table establishes:

- **The discard does two things and nothing else.** A° is A without it. It
  clears R9a (469 to 0) and R10 (243 to 0), and it changes no winner except by
  reporting 25 ties.
- **Tie reporting clears R3**, in every representation that uses it.
- **Only evidence identity clears R4.** A° fails all four restatements. C catches
  the three that restate a whole reason and misses the one that drops a term.
- **R5 cannot be cleared, and B and C both know it.** `W/2 + W/2` is two
  identical half-strength statements, which is exactly what a half-strength
  reason written twice looks like. A representation that refuses to strengthen
  restatements must read the split as the weaker reason. Both B and C flag
  **78,732 of the 78,732** cells where the split rule applies, and neither
  changes a single outcome unflagged. A production validator would reject such
  a file, which is what the ranking report's J1 said to do.
- **Weight still works.** Doubling a rule changes about 20,000 cells under every
  representation. Strengthening only what supports an intention never makes it
  lose.

#### 5. What is preserved

| | Published for A | A | A° | B | C |
|---|---|---|---|---|---|
| Single-candidate cells | 28.6 % | 28.6 % | 28.6 % | 28.6 % | 28.6 % |
| Distinct signatures in company | 56 | 56 | 64 | 78 | 64 |
| Changed by company arriving | 8,407 | 8,407 | 8,412 | 8,094 | 8,412 |
| Groups with one outcome for every profile | 5 of 14 | 5 | 5 | 5 | 5 |
| Reported ties | - | 0 | 25 | 25 | 25 |
| Hunger 0.30 -> 0.95 / a room with no food | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Replay, rebuilt from scratch | exact | 2,100 of 2,100 | 2,100 of 2,100 | 2,100 of 2,100 | 2,100 of 2,100 |
| Character names in any rule | 0 | 0 | 0 | 0 | 0 |
| Person decides, candidates fixed, K >= 2 | 6.1 % | 6.1 % | 6.1 % | **7.1 %** | 6.1 % |

**Everything that was proven survives B and C.** The differences in signatures
and in circumstance changes have two different sources:

- A° and C show **64 signatures instead of 56**, and 8,412 changes instead of
  8,407, only because they report the 25 ties that A breaks by name. **C reaches
  the same intention as A in every other cell of the sweep.**
- B shows 78 signatures and 8,094 changes because it changes 660 conclusions
  (section 6).

**More variation is not the aim and is not claimed as a gain.** B makes three
lopsided groups less lopsided. Whether that is closer to how people are is
exactly what this experiment cannot measure.

#### 6. Where B changes conclusions, and why that is a decision, not a finding

The frozen file states the same evidence twice for one intention in exactly
**five places, in three groups**:

| Group | Intention | Evidence | Stated by | B counts | A and C count |
|---|---|---|---|---|---|
| `look_after` in company | protect | `trait:empathetic` | `standing_between_them_and_it` 0.40, `keeping_it_off_them` 0.30 | 0.40 | 0.70 |
| `guard_supplies` in company | assert_authority | `value:control` | `pulling_rank_needs_an_audience` 0.35, `being_the_one_who_decides_it` 0.25 | 0.35 | 0.60 |
| `guard_supplies` in company | assert_authority | `belief:role_claim` | the same two, 0.30 and 0.25 | 0.30 | 0.55 |
| `restore_standing` in company | assert_authority | `value:control` | as above | 0.35 | 0.60 |
| `restore_standing` in company | assert_authority | `belief:role_claim` | as above | 0.30 | 0.55 |

B reaches a different outcome from A° in **660 cells**. Every one is in those
three groups, and in every one A° had formed the intention whose evidence B
stops counting twice:

| Group | A | B |
|---|---|---|
| `look_after` in company | protect 86.0 % | protect **78.2 %** |
| `guard_supplies` in company | assert_authority 80.6 % | assert_authority **69.0 %** |
| `restore_standing` in company | assert_authority 81.1 % | assert_authority **70.4 %** |

**The data cannot adjudicate this.** Take the empathy statements. "Standing
between them and it" and "keeping it off them" are two different routes to
protecting somebody, and both are driven by one fact: that the person is
empathetic.

- If a fact about a person supports an intention once however many routes cite
  it, B is right.
- If each route draws on it separately, C is right.

The invariants do not decide between the two, because both pass them. The only
test that separates B from C is a restatement, not two genuinely different
reasons.

**And B has to choose a second time.** When two reasons state the same fact at
different strengths (0.40 and 0.30), B keeps the stronger. **B-mean**, which keeps
their mean and is otherwise identical, reaches a different outcome in **242
cells**, all in the same three groups. So "count it once" is not yet a rule. It
is a family of rules, and the family is not small.

#### 7. The same act, different reasons

The wants whose shipped proposals lead to `check_pantry`, read from
`decisions.json`, are `find_out`, `get_food`, `guard_supplies` and
`restore_standing`. A reason is given as person evidence: each piece's share of
the winner's margin over the runner-up, in the representation's own arithmetic.
None of these mappings is written anywhere. They are read off the existing
rules and the character sheets.

**The brief's example**, at the top of the morning in the kitchen, in company,
with `find_out`:

| | A, A°, B and C agree |
|---|---|
| Daniel | `assert_authority`: `trait:dominant` 0.383, `value:control` 0.350, `belief:role_claim` 0.240 |
| Leo | `take_responsibility`: `value:family_safety` 0.350, `trait:cautious` 0.140 |
| Mara | `share_information`: `value:closeness` 0.300, `value:fairness` 0.100, `trait:honest` 0.055 |

**Where the stated reason depends on how the rules were written**: the same
Daniel, with `guard_supplies` or `restore_standing` in company.

| | Daniel's `assert_authority`, led by |
|---|---|
| A and C | `value:control` **0.600**, because two rules state it (0.35 + 0.25 at weight 1.0), then `role_claim` 0.440, then `dominant` 0.383 |
| B | `trait:dominant` **0.383**, then `control` 0.350, then `role_claim` 0.240 |

The intention is the same; the explanation of why is not. Under A, the fact that
two rules happen to mention control is what makes control his leading reason.

**In real mornings.** There were 257 real pantry-checks. Each was matched with
every other member of the cast at the same minute of the same morning: the same
world, room, company, want and act, and their own real mind. That gives 771
pairs:

| | A | A° | B | C |
|---|---|---|---|---|
| Pairs forming different intentions | 486 (63.0 %) | 486 | 486 | 486 |
| Pairs forming the same intention | 285 | 285 | 285 | 285 |
| ...led by a different piece of person evidence | 105 (36.8 %) | 105 | 105 | 105 |
| ...resting on different person evidence, in any piece or weight (added after the first run) | **285 (100 %)** | 285 | 285 | 285 |

So the same act, done for the same want at the same moment, is carried by
different intentions in 63 % of pairs. **Even where the intention is the same,
the reason is not**: every one of the 285 same-intention pairs rests on different
person evidence, in some piece or weight. That last row was added after the first
run, and its 100 % is mostly a fact about the cast: no two of the four hold every
trait and value the rules read at the same level. At the top of the morning, Elena checks the pantry for
`get_food` out of `family_safety` (0.350) and caution; Mara, forming the same
intention, out of caution alone (0.100).

**All four representations can state the reasons**, because they all read the
same levels through the same `ScalerEval`. **What separates them is whether the
stated reason survives a rewrite of the rule file.** Each real pantry-check was
re-decided with one rule copied, for each of the ten rules in turn (2,570
re-decisions), and again with one rule partly copied:

| | A | A° | B | C |
|---|---|---|---|---|
| Copy: the intention changed | **110** | **110** | 0 | 0 |
| Copy: same intention, different leading reason | 0 | 0 | 0 | 0 |
| Partial copy: the intention changed | **110** | **110** | 0 | **110** |
| Partial copy: same intention, different leading reason | **20** | **20** | 0 | **20** |

Under A, one copied line changes what a real person was doing in 110 of 2,570
real decisions; a partly copied line also re-ranks why, in 20 more. **Under B,
neither ever happens.**

#### 8. Candidate stages

| Compatible intentions | Groups | Cells | Share |
|---|---|---|---|
| 1 | 4 | 8,748 | 28.6 % |
| 2 | 3 | 6,561 | 21.4 % |
| 3 | 7 | 15,309 | 50.0 % |

The four stages stay separate in every representation:

- **Availability** is fixed by the want.
- **Compatibility** is fixed by the circumstance: it changed in **0 of 642,978**
  person moves, under all four.
- **Candidate selection**: under A, the discard changes the candidate set in
  2,184 of those moves. Under A°, B and C it never does.
- **Preference**, with the candidates fixed:

| | A | A° | B | C |
|---|---|---|---|---|
| K = 1 | 0 | 0 | 0 | 0 |
| K = 2 | 4.4 % | 4.4 % | 5.5 % | 4.4 % |
| K = 3 | 6.8 % | 6.9 % | 7.7 % | 6.9 % |
| **K >= 2** | **6.1 %** | **6.1 %** | **7.1 %** | **6.1 %** |

B raises preference sensitivity a little because it makes three groups less
lopsided. Per attribute, B raises `dominant` (6.3 % to 9.0 %) and `honest` (12.0 %
to 14.6 %), and lowers `role_claim` (10.0 % to 9.1 %), which it no longer counts
twice. `anxious`, `impulsive` and the swap of a person's fifth and sixth values
move nothing under any representation.

#### 9. The 35.7 % forced share

**35.7 % under every representation.** Its causes:

| Share | Group | Losing intention | Cause |
|---|---|---|---|
| 28.6 % | `avoid_exposure`, `find_out`, `keep_peace`, `look_after`, all alone | none; nothing else is compatible | **1. no alternative** |
| 7.1 % | `restore_standing` alone | `prevent_argument` | **2. dominated** for every possible person, best margin -0.070 |
| | | `assert_authority` | **4. evidence**: it needs `emotion:anger`, which no sweep profile feels |

**No forced cell is caused by the representation** (cause 3): no representation
breaks any of them. And the evidence limit is not an artifact of a sweep without
feelings. In **560** real moments asked about `restore_standing` alone, anger
included, `assert_authority` won **0** times under every representation. Daniel,
the most disposed to it, would need anger of 2.2 on a scale that stops at 1.

So in the forced share, **ranking is not decorating anything**. Where every
person agrees, it is because only one intention is possible (gating and
content), or because the rules as written make the alternative unreachable for
this cast. Neither is a ranking problem, and no ranking representation changes
it.

#### 10. Evidence-read audit

**No piece of evidence changes status (live, cancelled or idle) in any group
between A, A°, B and C.** The representations differ in how much a piece of
evidence can move things, never in whether it can.

| Evidence | Status, all representations | Measured |
|---|---|---|
| `anxious` | **idle everywhere**: read only in `keep_peace` alone (the sole candidate) and `restore_standing` alone (dominated) | 0 of 61,236 moves |
| `honest` | live in 8 groups, **cancelled in `get_food`** (both rivals read it at 0.30) | A 5,230, B 6,399 of 61,236 |
| `dominant` | live in 6 groups | A 2,675, B 3,951 |
| `empathetic` | live in 5 groups | A 4,291, B 4,608 |
| `cautious` | live in 10 groups | A 2,801, B 3,344 |
| `proud` | live in 4 groups | A 808, B 1,151 |
| `answerable_for` | live in 3 groups | 5,774 of 30,618 under every representation |
| `role_claim` | live in 5 groups | A 2,182, B 1,982 |
| values | `respect` live only in `restore_standing` alone, which needs anger; the others live in 5 to 10 groups | rank swaps 4.3 to 6.5 % |
| `anger` | live in 4 groups | changed 33 of 1,420 real cells where it was felt, under every representation |
| `anxiety` | live in 3 groups | 216 of 6,171 |
| `shame` | live in 3 groups | 60 of 1,500 |

**But restating a rule creates influence under A.** Copy one rule, and evidence
that was cancelled or idle becomes live:

| | A | A° | B | C |
|---|---|---|---|---|
| (group, evidence) pairs made live by copying one rule | **5** | **5** | 0 | 0 |
| ...by partly copying one rule | **5** | **5** | 0 | **5** |

Copy `what_you_did_in_the_night`, and a person's honesty starts to choose between
taking responsibility and admitting the theft. It changes the intention in 1,134
of 8,748 honesty moves in `get_food` under A, against 0 on the frozen file. Under B, still 0. Copy
`letting_it_go_for_now` under A, and `anxious`, idle for every possible person,
becomes live. **Under A, a trait can be brought back from the dead by pasting a
line.**

#### 11. What the ranking layer must keep

This is the answer the brief asks for. Each item is required by a measurement
above, not by taste.

| | Keep | Because | Evidence |
|---|---|---|---|
| 1 | **The identity of what every statement reads**: the evidence key per term, and the circumstance per base | Without it no restatement is recognisable. Reason-level identity is not enough | R4a-d: A fails 18,938 to 19,992; C fails R4d 19,062; B 0 |
| 2 | **Each statement's coefficient and sign, apart from the level** | Weight must mean something (R6). A restatement must be told from a conflict (equal coefficients or not). A negative term must stay a term | R6 ~20,000 everywhere; R7 0 away; the magnitude clarification |
| 3 | **Provenance**: which reason made which statement | To flag rewrites instead of silently absorbing them, and to trace a reason back to the rule that stated it | R5: 78,732 of 78,732 flagged by B and C |
| 4 | **A declared rule for one fact cited by several reasons for one intention** | The invariants cannot choose it, and it decides real conclusions | B against C: 660 cells. B against B-mean: 242 |
| 5 | **The compatible set as the candidate set** | Nothing about a person may remove a candidate | R10: A 243 and 22,113; A°, B, C 0 |
| 6 | **Ties, as ties** | A label is not psychology | R3: A 12; the others 0 |
| 7 | **The why, as person evidence**, derived from 1 and 2 | The same act must be distinguishable by its reasons, stably | 771 real pairs; 0 reason changes under B across 5,140 re-decisions |
| 8 | **Availability and compatibility as separate, earlier stages**, untouched | They are already correct and person-independent | 0 of 642,978 under all four |

**What it must not keep:** rule ids, rule order, rule count, the grouping of
statements into rules, the spelling of intention names. B drops all of them, and
the 94 rewritten rule sets showed nothing lost.

#### 12. Limitations

- **Psychological correctness is not tested.** B passing its invariants proves a
  property of the arithmetic, not that its 660 changed conclusions are truer.
- **Only five places in the frozen file exercise B's central choice.** They cite
  two facts and one trait, in three groups. The choice is general; the evidence
  for its consequences is narrow.
- **B's treatment of bases is unexercised by the frozen file.** A base is keyed
  by its rule's gate, so two reasons with the same gate for the same intention
  would share one base. No two such reasons exist in the file; only the
  rewrites tested it.
- **The sweep carries no feelings.** The 50 real mornings do, but for four people
  only, and the feeling audit zeroes a level in the arithmetic rather than
  replaying a morning without it.
- **Values cannot be moved one at a time**, because they weigh by rank.
- **The matched pairs are counterfactual in one respect.** The partner is placed
  in the checker's moment, with their own real mind, but did not choose that act
  themselves.
- **Most predictions were analytic**, so their holding mainly confirms the
  fixture. The empirical ones were ranges, and one missed in its form (results,
  8.4).

#### 13. Classification

| | |
|---|---|
| **PROVEN** | A is the selector (0 of 30,618). Evidence identity (B) is invariant to exact, reworded, near and partial restatement (0 each). Reason identity (C) is defeated by partial restatement (19,062, none flagged). No representation can treat a proportional split as the unsplit rule while refusing to strengthen restatements, and B and C both flag it in 78,732 of 78,732 cells. The discard is responsible for exactly R9a (469) and R10 (243). Tie reporting clears R3. B, A° and C preserve 28.6 %, blindness, replay, no character rules and non-trivial fixed-candidate sensitivity (7.1 %, 6.1 %, 6.1 %). C equals A outside 25 reported ties. B differs from A° in 660 cells, all away from `protect` or `assert_authority`, in the five places the file states one fact twice. The conflict policy alone decides 242 cells. The forced share is 35.7 % under every representation, with no representation cause. No evidence changes status between representations. Restating one rule makes cancelled or idle evidence live under A (5 pairs) and never under B. The same act is carried by different intentions in 63.0 % of matched real pairs, and under A one copied rule changes 110 of 2,570 real intentions, against 0 under B |
| **PLAUSIBLE** | That evidence identity is the right unit for a production ranking layer: it is the only one tested that passes every restatement, but it was tested on one file. That B's stated reasons are closer to a person's reasons than A's: they are invariant to rewriting, which A's are not, but invariance is not truth |
| **UNPROVEN** | Whether one fact cited by two reasons should count once (B) or twice (C), and if once, how (strongest, mean, or something else). Whether B's 660 changed conclusions are improvements. Whether B's base-by-gate identity is right, since the file never exercises it |
| **FAILED** | A as a representation: R3, R4a-d, R9a, R10, and influence created by pasting a line. C as a replacement: silently defeated by partial restatement. The hope that evidence identity alone would settle the representation: it leaves the shared-fact decision open, and that decision moves real conclusions |
| **UNKNOWN** | Psychological correctness of any conclusion. Behaviour on a file with many shared facts, or with feelings varied across the whole sweep. Whether any declared shared-fact rule would survive an authored file larger than ten rules |

#### 14. Verdict

### MODIFY

These criteria were committed with the predictions. **KEEP** needed everything
below, and needed B's changes to the frozen file to depend on no choice B had to
invent. **MODIFY** applies when all of that holds except that some conclusion B
reaches depends on a policy the representation does not declare. That is
exactly what happened:

- B passes R1 to R4, R6 to R10, and R5 by explicit detection.
- It keeps 28.6 %, blindness, replay and non-trivial fixed-candidate sensitivity.
- It states person-specific reasons for the same act, stable under restatement.
- C fails a test that B passes.
- And **660 of B's conclusions, 242 of them by the choice of conflict policy
  alone, rest on an undeclared answer to whether one fact cited by two reasons
  counts once.**

**Not REBUILD:** B failed nothing it was built to pass, and lost none of what was
already proven. **Not ABANDON:** every representation can state reasons as
person evidence.

**What MODIFY means here:** carry forward evidence identity, statement
coefficients and signs, provenance, no discard and tie reporting (section 11,
items 1 to 3 and 5 to 8). **Add** an explicit, declared combination rule for one
fact cited by several reasons for one intention. And decide that rule on
psychological grounds, because the invariants have been shown not to decide it.
Nothing here has been implemented, and the next step is a decision, not code.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter IntentionRepresentationExperimentTests`.
It takes about fifteen minutes, most of it in the 94 rewritten rule sets.

**Suite: 432 tests, 430 pass, 2 fail**: the two regressions S1.4 left failing, unchanged
(the pacing gate, still 7 on Model A, and the emergent-moment fading check). The 424
before this experiment, plus its eight, is exactly 432. **Every generated document of S0
to S1.7 and of the ten earlier experiments regenerated with identical content.** The only
differences anywhere were the wall-clock seconds in the decision-sensitivity results and
one file that differed in line endings only.

---

## measurements.md

### Intention representation: measurements

Generated by `IntentionRepresentationExperimentTests` against the frozen candidate rules, whose hash is checked at the start and the end of the run. The representations, the tests and the predictions were committed before this fixture existed. There is no randomness anywhere.

#### 0. What is frozen, whether A is the selector, and what the file states

| | |
|---|---|
| sha256 at the start of this run | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Expected | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Match | **yes** |
| A's winner differs from `IntentionSelector.Form` | **0** of 30618 cells |
| Same winner, weight not equal to the bit | **0** |

##### Every statement in the file, by evidence

| Rule | Intention | Gate | Statements (evidence key, coefficient) |
|---|---|---|---|
| `pulling_rank_needs_an_audience` | assert_authority | others>=1 | `circumstance:others>=1` 0.100; `trait:dominant` 0.450; `value:control` 0.350; `belief:role_claim($self,leads_family)` 0.300; `trait:proud` 0.150 |
| `being_the_one_who_decides_it` | assert_authority | any | `circumstance:any` 0.050; `value:control` 0.250; `belief:role_claim($self,leads_family)` 0.250; `emotion:anger@$anybody` 0.300 |
| `somebody_has_to_do_it` | take_responsibility | any | `circumstance:any` 0.180; `trait:honest` 0.300; `value:family_safety` 0.350; `trait:cautious` 0.200 |
| `doing_it_where_nobody_is_watching` | take_responsibility | alone | `circumstance:alone` 0.220; `trait:proud` 0.250; `value:respect` 0.200 |
| `so_that_they_know_too` | share_information | others>=1 | `circumstance:others>=1` 0.120; `trait:honest` 0.400; `value:closeness` 0.300; `value:fairness` 0.200 |
| `standing_between_them_and_it` | protect | others>=1 | `circumstance:others>=1` 0.150; `trait:empathetic` 0.400; `value:family_safety` 0.350; `emotion:anxiety@$anybody` 0.300 |
| `keeping_it_off_them` | protect | any | `circumstance:any` 0.100; `trait:empathetic` 0.300; `value:closeness` 0.250 |
| `not_making_a_scene_of_it` | prevent_argument | others>=1 | `circumstance:others>=1` 0.150; `trait:cautious` 0.350; `value:closeness` 0.300; `trait:dominant` -0.250 |
| `letting_it_go_for_now` | prevent_argument | alone | `circumstance:alone` 0.080; `trait:cautious` 0.250; `trait:anxious` 0.200 |
| `what_you_did_in_the_night` | took_what_was_not_mine | any | `circumstance:any` 0.050; `belief:answerable_for($self,missing_can)` 0.600; `trait:honest` 0.300; `value:fairness` 0.250; `emotion:shame@$anybody` 0.300 |

##### Where one intention states the same evidence twice

Within one (want, circumstance), two compatible rules for the same intention that read the same evidence. These are the only places B and C can disagree on the frozen file.

| Group | Intention | Evidence | Stated by | B counts | A and C count |
|---|---|---|---|---|---|
| `guard_supplies` in company | assert_authority | `value:control` | `pulling_rank_needs_an_audience` 0.350, `being_the_one_who_decides_it` 0.250 | 0.350 | 0.600 |
| `guard_supplies` in company | assert_authority | `belief:role_claim($self,leads_family)` | `pulling_rank_needs_an_audience` 0.300, `being_the_one_who_decides_it` 0.250 | 0.300 | 0.550 |
| `look_after` in company | protect | `trait:empathetic` | `standing_between_them_and_it` 0.400, `keeping_it_off_them` 0.300 | 0.400 | 0.700 |
| `restore_standing` in company | assert_authority | `value:control` | `pulling_rank_needs_an_audience` 0.350, `being_the_one_who_decides_it` 0.250 | 0.350 | 0.600 |
| `restore_standing` in company | assert_authority | `belief:role_claim($self,leads_family)` | `pulling_rank_needs_an_audience` 0.300, `being_the_one_who_decides_it` 0.250 | 0.300 | 0.550 |

**5 (group, intention, evidence) places where the frozen file states one piece of evidence twice for one intention.**

##### What each representation recognises on the frozen file

| | Cells with a recognised restatement or conflict | Cells whose candidate set differs from the compatible set |
|---|---|---|
| A | 0 | 243 |
| A° | 0 | 0 |
| B | 6561 | 0 |
| C | 0 | 0 |

#### 1. The invariants, R1 to R10

Cells, of 30618, whose outcome changed. For a per-rule test the count is summed over the ten rules (306180 (rule, cell) pairs). An outcome is an intention, or a reported tie. In brackets: changes the representation **did not flag** as a restatement or conflict it had recognised. A changed cell that is flagged was changed knowingly.

| | Rewrite | A | A° | B | C |
|---|---|---|---|---|---|
| R1 | reverse the rule order | 0 | 0 | 0 | 0 |
| R2 | give every rule a new id | 0 | 0 | 0 | 0 |
| R3 | rename the intentions | **12** (12 unflagged) | 0 | 0 | 0 |
| R4a | W + W, an exact copy | **19992** (19992 unflagged) | **20021** (20021 unflagged) | 0 | 0 |
| R4b | W + W', the same reason with its terms reversed and a new id | **19992** (19992 unflagged) | **20021** (20021 unflagged) | 0 | 0 |
| R4c | W + 0.99W | **19844** (19844 unflagged) | **19869** (19869 unflagged) | 0 | 0 |
| R4d | W + W without its last term (a partial restatement) | **18938** (18938 unflagged) | **19062** (19062 unflagged) | 0 | **19062** (19062 unflagged) |
| R5a | W -> W/2 + W/2 | 0 | 0 | **15210** (0 unflagged) | **13796** (0 unflagged) |
| R5b | W -> 4 x W/4 | 0 | 0 | **19340** (0 unflagged) | **18632** (0 unflagged) |
| R6 | W -> 2W | **19992** (19992 unflagged) | **20021** (20021 unflagged) | **22520** (22520 unflagged) | **20021** (20021 unflagged) |
| R7 | base and positive factors x 2 | **20829** (20829 unflagged) | **20869** (20869 unflagged) | **23414** (23414 unflagged) | **20869** (20869 unflagged) |
| R9a | split by term | **469** (469 unflagged) | 0 | 0 | 0 |
| R9b | merge co-compatible rules, statements unaltered | 0 | 0 | 0 | 0 |

##### R5: did the representation know what it was doing?

| | Splits | A | A° | B | C |
|---|---|---|---|---|---|
| R5a | cells in which the split rule is compatible, flagged as a repeat | 0 | 0 | 78732 | 78732 |
| R5a | outcomes changed, and of those unflagged | 0, 0 | 0, 0 | 15210, 0 | 13796, 0 |
| R5b | cells in which the split rule is compatible, flagged as a repeat | 0 | 0 | 78732 | 78732 |
| R5b | outcomes changed, and of those unflagged | 0, 0 | 0, 0 | 19340, 0 | 18632, 0 |

##### R6 and R7: weight, and its direction

| | A | A° | B | C |
|---|---|---|---|---|
| R6 2W: changed | 19992 | 20021 | 22520 | 20021 |
| R6 2W: toward the rule's intention / away from it | 19992 / 0 | 19928 / 0 | 22423 / 0 | 19928 / 0 |
| **R7** positive parts x 2: toward / **away** | 20829 / **0** | 20764 / **0** | 23305 / **0** | 20764 / **0** |

A 2W rule doubles its negative terms too, so for a person against whom a reason argues, doubling it can make its intention lose. That is weight, not a breach of monotonicity; R7 strengthens only what supports the intention.

##### R8 and R10

| | A | A° | B | C |
|---|---|---|---|---|
| **R8** changes outside the cells where the rewritten rule is compatible, all per-rule tests | 0 | 0 | 0 | 0 |
| **R10** cells whose candidate set differs from the compatible set: frozen file | 243 | 0 | 0 | 0 |
| **R10** the same, summed over every rewritten rule set | 22113 | 0 | 0 | 0 |

A's duplicate, counted through `IntentionSelector.Form` itself: **19992** (published: 19992).

#### 2. Does each representation keep what the generalization experiment proved?

| | Published for A | A | A° | B | C |
|---|---|---|---|---|---|
| Cells with one candidate | 28.6 % (8748) | 28.6 % (8748) | 28.6 % (8748) | 28.6 % (8748) | 28.6 % (8748) |
| Distinct signatures in company | 56 | 56 | 64 | 78 | 64 |
| Cells changed by company arriving | 8407 | 8407 | 8412 | 8094 | 8412 |
| Groups with one outcome for every profile | 5 of 14 | 5 of 14 | 5 of 14 | 5 of 14 | 5 of 14 |
| Reported ties | - | 0 | 25 | 25 | 25 |
| Hunger 0.30 -> 0.95 changed | 0 | 0 | 0 | 0 | 0 |
| A room with no food changed | 0 | 0 | 0 | 0 | 0 |
| Replay identical, 300 profiles x 7 wants rebuilt from scratch | 300 of 300 | 2100 of 2100 | 2100 of 2100 | 2100 of 2100 | 2100 of 2100 |
| Character names in any rule | 0 | 0 | 0 | 0 | 0 |

##### Where the representations reach different intentions on the frozen file

| Group | A | A° | B | C | Cells where B differs from A° | C differs from A |
|---|---|---|---|---|---|---|
| `avoid_exposure` in company | took_what_was_not_mine 51.4 %, protect 34.2 %, prevent_argument 14.4 % | took_what_was_not_mine 51.4 %, protect 34.2 %, prevent_argument 14.1 %, tie(prevent_argument=protect) 0.3 % | took_what_was_not_mine 51.4 %, protect 34.2 %, prevent_argument 14.1 %, tie(prevent_argument=protect) 0.3 % | took_what_was_not_mine 51.4 %, protect 34.2 %, prevent_argument 14.1 %, tie(prevent_argument=protect) 0.3 % | 0 | 7 |
| `avoid_exposure` alone | took_what_was_not_mine 100.0 % | took_what_was_not_mine 100.0 % | took_what_was_not_mine 100.0 % | took_what_was_not_mine 100.0 % | 0 | 0 |
| `find_out` in company | assert_authority 56.6 %, take_responsibility 29.9 %, share_information 13.5 % | assert_authority 56.0 %, take_responsibility 29.9 %, share_information 13.5 %, tie(assert_authority=take_responsibility) 0.6 % | assert_authority 56.0 %, take_responsibility 29.9 %, share_information 13.5 %, tie(assert_authority=take_responsibility) 0.6 % | assert_authority 56.0 %, take_responsibility 29.9 %, share_information 13.5 %, tie(assert_authority=take_responsibility) 0.6 % | 0 | 13 |
| `find_out` alone | take_responsibility 100.0 % | take_responsibility 100.0 % | take_responsibility 100.0 % | take_responsibility 100.0 % | 0 | 0 |
| `get_food` in company | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | 0 | 0 |
| `get_food` alone | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | 0 | 0 |
| `guard_supplies` in company | assert_authority 80.6 %, take_responsibility 18.9 %, protect 0.5 % | assert_authority 80.6 %, take_responsibility 18.9 %, protect 0.5 % | assert_authority 69.0 %, take_responsibility 29.1 %, protect 2.0 % | assert_authority 80.6 %, take_responsibility 18.9 %, protect 0.5 % | 254 | 0 |
| `guard_supplies` alone | take_responsibility 76.6 %, protect 21.5 %, assert_authority 1.8 % | take_responsibility 76.6 %, protect 21.5 %, assert_authority 1.8 % | take_responsibility 76.6 %, protect 21.5 %, assert_authority 1.8 % | take_responsibility 76.6 %, protect 21.5 %, assert_authority 1.8 % | 0 | 0 |
| `keep_peace` in company | share_information 47.8 %, protect 44.0 %, prevent_argument 8.2 % | share_information 47.8 %, protect 44.0 %, prevent_argument 8.0 %, tie(prevent_argument=protect) 0.2 % | share_information 47.8 %, protect 44.0 %, prevent_argument 8.0 %, tie(prevent_argument=protect) 0.2 % | share_information 47.8 %, protect 44.0 %, prevent_argument 8.0 %, tie(prevent_argument=protect) 0.2 % | 0 | 5 |
| `keep_peace` alone | prevent_argument 100.0 % | prevent_argument 100.0 % | prevent_argument 100.0 % | prevent_argument 100.0 % | 0 | 0 |
| `look_after` in company | protect 86.0 %, share_information 12.8 %, prevent_argument 1.2 % | protect 86.0 %, share_information 12.8 %, prevent_argument 1.2 % | protect 78.2 %, share_information 19.8 %, prevent_argument 2.1 % | protect 86.0 %, share_information 12.8 %, prevent_argument 1.2 % | 171 | 0 |
| `look_after` alone | protect 100.0 % | protect 100.0 % | protect 100.0 % | protect 100.0 % | 0 | 0 |
| `restore_standing` in company | assert_authority 81.1 %, take_responsibility 18.9 % | assert_authority 81.1 %, take_responsibility 18.9 % | assert_authority 70.4 %, take_responsibility 29.6 % | assert_authority 81.1 %, take_responsibility 18.9 % | 235 | 0 |
| `restore_standing` alone | take_responsibility 100.0 % | take_responsibility 100.0 % | take_responsibility 100.0 % | take_responsibility 100.0 % | 0 | 0 |

**B reaches a different outcome from A° in 660 cells; in 660 of them A° had formed `assert_authority` or `protect`, the two intentions whose evidence B stops counting twice. C differs from A in 25 cells, of which 25 are ties C reports and A breaks by name.**

##### How much B's conflict policy decides

B keeps the strongest of two different statements of the same evidence. B-mean keeps their mean. Everything else is identical.

| | Cells |
|---|---|
| Where B-mean and B reach different outcomes | **242** |
| ...by group | `guard_supplies` in company 69, `restore_standing` in company 74, `look_after` in company 99 |
| Where B-mean differs from A° | 902 |

#### 3. Candidate stages, and person sensitivity with the candidates fixed

| Compatible intentions | Groups | Cells | Share |
|---|---|---|---|
| 1 | 4 | 8748 | 28.6 % |
| 2 | 3 | 6561 | 21.4 % |
| 3 | 7 | 15309 | 50.0 % |

Every profile's 21 single-attribute moves, in every group: 642978 pairs.

| | A | A° | B | C |
|---|---|---|---|---|
| Compatible set changed by moving the person | **0** | **0** | **0** | **0** |
| Candidate set changed by moving the person | 2184 | 0 | 0 | 0 |
| K = 1, candidates fixed: outcome changed | 0 of 183708 (0.0 %) | 0 of 183708 (0.0 %) | 0 of 183708 (0.0 %) | 0 of 183708 (0.0 %) |
| K = 2, candidates fixed: outcome changed | 6115 of 137781 (4.4 %) | 6115 of 137781 (4.4 %) | 7519 of 137781 (5.5 %) | 6115 of 137781 (4.4 %) |
| K = 3, candidates fixed: outcome changed | 21836 of 319305 (6.8 %) | 22096 of 321489 (6.9 %) | 24868 of 321489 (7.7 %) | 22096 of 321489 (6.9 %) |
| **K >= 2, candidates fixed: outcome changed** | **6.1 %** | **6.1 %** | **7.1 %** | **6.1 %** |

##### By attribute, K >= 2, candidates fixed

| Moved | A | A° | B | C |
|---|---|---|---|---|
| trait:anxious | **0** | **0** | **0** | **0** |
| trait:cautious | 6.5 % | 6.5 % | 7.6 % | 6.5 % |
| trait:dominant | 6.3 % | 6.2 % | 9.0 % | 6.2 % |
| trait:empathetic | 9.8 % | 9.9 % | 10.5 % | 9.9 % |
| trait:honest | 12.0 % | 12.0 % | 14.6 % | 12.0 % |
| trait:impulsive | **0** | **0** | **0** | **0** |
| trait:proud | 1.8 % | 1.9 % | 2.6 % | 1.9 % |
| value ranks 1-2 | 5.2 % | 5.2 % | 6.1 % | 5.2 % |
| value ranks 2-3 | 5.1 % | 5.2 % | 6.5 % | 5.2 % |
| value ranks 3-4 | 4.6 % | 4.7 % | 6.0 % | 4.7 % |
| value ranks 4-5 | 4.4 % | 4.3 % | 5.1 % | 4.3 % |
| value ranks 5-6 | **0** | **0** | **0** | **0** |
| belief:role_claim($self,leads_family) | 10.0 % | 10.1 % | 9.1 % | 10.1 % |
| belief:answerable_for($self,missing_can) | 26.4 % | 26.4 % | 26.4 % | 26.4 % |

#### 4. The forced share: why every profile forms the same intention

For each representation, every group in which all 2187 profiles reach one outcome. Each compatible intention that never wins there is given a cause:

1. **no alternative**: it is the only compatible intention;
2. **dominated**: some rival outscores it for every possible person, under this representation's arithmetic;
3. **representation**: it wins for some profile under another of A, A°, B, C;
4. **evidence**: none of the above. It could win, and never does, because the people supplied never carry what it needs.

| Representation | Group | Cells | Winner | Losing intention | Cause | What it would need |
|---|---|---|---|---|---|---|
| A | `avoid_exposure` alone | 2187 | took_what_was_not_mine | - | 1 no alternative | - |
| A | `find_out` alone | 2187 | take_responsibility | - | 1 no alternative | - |
| A | `keep_peace` alone | 2187 | prevent_argument | - | 1 no alternative | - |
| A | `look_after` alone | 2187 | protect | - | 1 no alternative | - |
| A | `restore_standing` alone | 2187 | take_responsibility | assert_authority | 4 evidence | `emotion:anger@$anybody` 0.300 (no sweep profile feels anything) |
| A | `restore_standing` alone | 2187 | take_responsibility | prevent_argument | 2 dominated by take_responsibility (best margin -0.070) | - |
| A° | `avoid_exposure` alone | 2187 | took_what_was_not_mine | - | 1 no alternative | - |
| A° | `find_out` alone | 2187 | take_responsibility | - | 1 no alternative | - |
| A° | `keep_peace` alone | 2187 | prevent_argument | - | 1 no alternative | - |
| A° | `look_after` alone | 2187 | protect | - | 1 no alternative | - |
| A° | `restore_standing` alone | 2187 | take_responsibility | assert_authority | 4 evidence | `emotion:anger@$anybody` 0.300 (no sweep profile feels anything) |
| A° | `restore_standing` alone | 2187 | take_responsibility | prevent_argument | 2 dominated by take_responsibility (best margin -0.070) | - |
| B | `avoid_exposure` alone | 2187 | took_what_was_not_mine | - | 1 no alternative | - |
| B | `find_out` alone | 2187 | take_responsibility | - | 1 no alternative | - |
| B | `keep_peace` alone | 2187 | prevent_argument | - | 1 no alternative | - |
| B | `look_after` alone | 2187 | protect | - | 1 no alternative | - |
| B | `restore_standing` alone | 2187 | take_responsibility | assert_authority | 4 evidence | `emotion:anger@$anybody` 0.300 (no sweep profile feels anything) |
| B | `restore_standing` alone | 2187 | take_responsibility | prevent_argument | 2 dominated by take_responsibility (best margin -0.070) | - |
| C | `avoid_exposure` alone | 2187 | took_what_was_not_mine | - | 1 no alternative | - |
| C | `find_out` alone | 2187 | take_responsibility | - | 1 no alternative | - |
| C | `keep_peace` alone | 2187 | prevent_argument | - | 1 no alternative | - |
| C | `look_after` alone | 2187 | protect | - | 1 no alternative | - |
| C | `restore_standing` alone | 2187 | take_responsibility | assert_authority | 4 evidence | `emotion:anger@$anybody` 0.300 (no sweep profile feels anything) |
| C | `restore_standing` alone | 2187 | take_responsibility | prevent_argument | 2 dominated by take_responsibility (best margin -0.070) | - |

| | A | A° | B | C |
|---|---|---|---|---|
| **Forced share** | **35.7 %** (10935) | **35.7 %** (10935) | **35.7 %** (10935) | **35.7 %** (10935) |

##### The evidence-limited case, in real mornings, which do carry feelings

`restore_standing` asked of every real mind, alone, at every decision of the 50 baseline mornings:

| | A | A° | B | C |
|---|---|---|---|---|
| Cells | 560 | 560 | 560 | 560 |
| `assert_authority` won | **0** | **0** | **0** | **0** |

#### 5. Evidence-read audit

For every piece of person evidence a rule reads, its status in each of the 14 groups under each representation: **live** (two contenders weigh it differently), **cancelled** (every contender weighs it the same), **idle** (only a dominated or a lone intention reads it). Measured influence: single-attribute moves across the sweep for traits and beliefs; zeroing the feeling at every real decision of 50 mornings for emotions.

| Evidence | Rep | Live in | Cancelled in | Idle in | Measured: outcomes changed |
|---|---|---|---|---|---|
| `belief:answerable_for($self,missing_can)` | A | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 5774 of 30618 sweep moves |
| `belief:answerable_for($self,missing_can)` | A° | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 5774 of 30618 sweep moves |
| `belief:answerable_for($self,missing_can)` | B | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 5774 of 30618 sweep moves |
| `belief:answerable_for($self,missing_can)` | C | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 5774 of 30618 sweep moves |
| `belief:role_claim($self,leads_family)` | A | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 2182 of 30618 sweep moves |
| `belief:role_claim($self,leads_family)` | A° | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 2201 of 30618 sweep moves |
| `belief:role_claim($self,leads_family)` | B | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 1982 of 30618 sweep moves |
| `belief:role_claim($self,leads_family)` | C | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 2201 of 30618 sweep moves |
| `emotion:anger@$anybody` | A | 4: `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 33 of 1420 live cells where it was felt |
| `emotion:anger@$anybody` | A° | 4: `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 33 of 1420 live cells where it was felt |
| `emotion:anger@$anybody` | B | 4: `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 33 of 1420 live cells where it was felt |
| `emotion:anger@$anybody` | C | 4: `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | 33 of 1420 live cells where it was felt |
| `emotion:anxiety@$anybody` | A | 3: `avoid_exposure` in company, `keep_peace` in company, `look_after` in company | - | - | 216 of 6171 live cells where it was felt |
| `emotion:anxiety@$anybody` | A° | 3: `avoid_exposure` in company, `keep_peace` in company, `look_after` in company | - | - | 216 of 6171 live cells where it was felt |
| `emotion:anxiety@$anybody` | B | 3: `avoid_exposure` in company, `keep_peace` in company, `look_after` in company | - | - | 216 of 6171 live cells where it was felt |
| `emotion:anxiety@$anybody` | C | 3: `avoid_exposure` in company, `keep_peace` in company, `look_after` in company | - | - | 216 of 6171 live cells where it was felt |
| `emotion:shame@$anybody` | A | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 60 of 1500 live cells where it was felt |
| `emotion:shame@$anybody` | A° | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 60 of 1500 live cells where it was felt |
| `emotion:shame@$anybody` | B | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 60 of 1500 live cells where it was felt |
| `emotion:shame@$anybody` | C | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | - | 1: `avoid_exposure` alone | 60 of 1500 live cells where it was felt |
| `trait:anxious` | A | - | - | 2: `keep_peace` alone, `restore_standing` alone | 0 of 61236 sweep moves |
| `trait:anxious` | A° | - | - | 2: `keep_peace` alone, `restore_standing` alone | 0 of 61236 sweep moves |
| `trait:anxious` | B | - | - | 2: `keep_peace` alone, `restore_standing` alone | 0 of 61236 sweep moves |
| `trait:anxious` | C | - | - | 2: `keep_peace` alone, `restore_standing` alone | 0 of 61236 sweep moves |
| `trait:cautious` | A | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 2: `find_out` alone, `keep_peace` alone | 2801 of 61236 sweep moves |
| `trait:cautious` | A° | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 2: `find_out` alone, `keep_peace` alone | 2851 of 61236 sweep moves |
| `trait:cautious` | B | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 2: `find_out` alone, `keep_peace` alone | 3344 of 61236 sweep moves |
| `trait:cautious` | C | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 2: `find_out` alone, `keep_peace` alone | 2851 of 61236 sweep moves |
| `trait:dominant` | A | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `keep_peace` in company, `look_after` in company, `restore_standing` in company | - | - | 2675 of 61236 sweep moves |
| `trait:dominant` | A° | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `keep_peace` in company, `look_after` in company, `restore_standing` in company | - | - | 2716 of 61236 sweep moves |
| `trait:dominant` | B | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `keep_peace` in company, `look_after` in company, `restore_standing` in company | - | - | 3951 of 61236 sweep moves |
| `trait:dominant` | C | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `keep_peace` in company, `look_after` in company, `restore_standing` in company | - | - | 2716 of 61236 sweep moves |
| `trait:empathetic` | A | 5: `avoid_exposure` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | 4291 of 61236 sweep moves |
| `trait:empathetic` | A° | 5: `avoid_exposure` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | 4313 of 61236 sweep moves |
| `trait:empathetic` | B | 5: `avoid_exposure` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | 4608 of 61236 sweep moves |
| `trait:empathetic` | C | 5: `avoid_exposure` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | 4313 of 61236 sweep moves |
| `trait:honest` | A | 8: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | 2: `get_food` in company, `get_food` alone | 2: `avoid_exposure` alone, `find_out` alone | 5230 of 61236 sweep moves |
| `trait:honest` | A° | 8: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | 2: `get_food` in company, `get_food` alone | 2: `avoid_exposure` alone, `find_out` alone | 5256 of 61236 sweep moves |
| `trait:honest` | B | 8: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | 2: `get_food` in company, `get_food` alone | 2: `avoid_exposure` alone, `find_out` alone | 6399 of 61236 sweep moves |
| `trait:honest` | C | 8: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | 2: `get_food` in company, `get_food` alone | 2: `avoid_exposure` alone, `find_out` alone | 5256 of 61236 sweep moves |
| `trait:proud` | A | 4: `find_out` in company, `guard_supplies` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | 808 of 61236 sweep moves |
| `trait:proud` | A° | 4: `find_out` in company, `guard_supplies` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | 834 of 61236 sweep moves |
| `trait:proud` | B | 4: `find_out` in company, `guard_supplies` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | 1151 of 61236 sweep moves |
| `trait:proud` | C | 4: `find_out` in company, `guard_supplies` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | 834 of 61236 sweep moves |
| `value:closeness` | A | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | values weigh by rank: see section 3 |
| `value:closeness` | A° | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | values weigh by rank: see section 3 |
| `value:closeness` | B | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | values weigh by rank: see section 3 |
| `value:closeness` | C | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | - | 1: `look_after` alone | values weigh by rank: see section 3 |
| `value:control` | A | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | values weigh by rank: see section 3 |
| `value:control` | A° | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | values weigh by rank: see section 3 |
| `value:control` | B | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | values weigh by rank: see section 3 |
| `value:control` | C | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | - | - | values weigh by rank: see section 3 |
| `value:fairness` | A | 6: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `keep_peace` in company, `look_after` in company | - | 1: `avoid_exposure` alone | values weigh by rank: see section 3 |
| `value:fairness` | A° | 6: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `keep_peace` in company, `look_after` in company | - | 1: `avoid_exposure` alone | values weigh by rank: see section 3 |
| `value:fairness` | B | 6: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `keep_peace` in company, `look_after` in company | - | 1: `avoid_exposure` alone | values weigh by rank: see section 3 |
| `value:fairness` | C | 6: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `keep_peace` in company, `look_after` in company | - | 1: `avoid_exposure` alone | values weigh by rank: see section 3 |
| `value:family_safety` | A | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:family_safety` | A° | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:family_safety` | B | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:family_safety` | C | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:respect` | A | 1: `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:respect` | A° | 1: `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:respect` | B | 1: `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |
| `value:respect` | C | 1: `restore_standing` alone | - | 1: `find_out` alone | values weigh by rank: see section 3 |

**Evidence whose status in some group depends on the representation: none.**

##### Does restating a single rule create influence?

For each rule, the file with that rule copied (R4a) or partly copied (R4d). Counted: (group, evidence) pairs that are cancelled or idle on the frozen file and live after the copy. Nothing about any person has changed.

| Restatement | A | A° | B | C |
|---|---|---|---|---|
| R4a exact copy | **5** | **5** | 0 | 0 |
| R4d partial copy | **5** | **5** | 0 | **5** |

- A, R4a exact copy of `somebody_has_to_do_it`: `trait:honest` in `get_food` in company goes from Cancelled to live
- A, R4a exact copy of `somebody_has_to_do_it`: `trait:honest` in `get_food` alone goes from Cancelled to live
- A°, R4a exact copy of `somebody_has_to_do_it`: `trait:honest` in `get_food` in company goes from Cancelled to live
- A°, R4a exact copy of `somebody_has_to_do_it`: `trait:honest` in `get_food` alone goes from Cancelled to live
- A, R4a exact copy of `letting_it_go_for_now`: `trait:anxious` in `restore_standing` alone goes from Idle to live
- A°, R4a exact copy of `letting_it_go_for_now`: `trait:anxious` in `restore_standing` alone goes from Idle to live
- A, R4a exact copy of `what_you_did_in_the_night`: `trait:honest` in `get_food` in company goes from Cancelled to live
- A, R4a exact copy of `what_you_did_in_the_night`: `trait:honest` in `get_food` alone goes from Cancelled to live
- A°, R4a exact copy of `what_you_did_in_the_night`: `trait:honest` in `get_food` in company goes from Cancelled to live
- A°, R4a exact copy of `what_you_did_in_the_night`: `trait:honest` in `get_food` alone goes from Cancelled to live
- A, R4d partial copy of `somebody_has_to_do_it`: `trait:honest` in `get_food` in company goes from Cancelled to live
- A, R4d partial copy of `somebody_has_to_do_it`: `trait:honest` in `get_food` alone goes from Cancelled to live

##### Measured: can a person's honesty choose between taking responsibility and admitting the theft?

Both rivals in `get_food` read `honest` at 0.30, so today it cancels. Every sweep profile's honesty moved to each other level, both circumstances:

| Rule file | A | A° | B | C |
|---|---|---|---|---|
| frozen | 0 of 8748 | 0 of 8748 | 0 of 8748 | 0 of 8748 |
| `what_you_did_in_the_night` copied | **1134** of 8748 | **1134** of 8748 | 0 of 8748 | 0 of 8748 |
| `what_you_did_in_the_night` partly copied | **1134** of 8748 | **1134** of 8748 | 0 of 8748 | **1134** of 8748 |

##### Feelings, zeroed at real decisions

3689 decision moments across 50 baseline mornings, each asked about every want: 25823 live cells.

| Feeling | A | A° | B | C |
|---|---|---|---|---|
| `emotion:anger` | 33 of 1420 | 33 of 1420 | 33 of 1420 | 33 of 1420 |
| `emotion:anxiety` | 216 of 6171 | 216 of 6171 | 216 of 6171 | 216 of 6171 |
| `emotion:shame` | 60 of 1500 | 60 of 1500 | 60 of 1500 | 60 of 1500 |

Under B, as it happened:

| Morning | Who | Want | Zeroed | With it | Without it |
|---|---|---|---|---|---|
| daniel_ate_it/1 m1 | daniel | `avoid_exposure` in company | emotion:shame | took_what_was_not_mine 0.892 over protect 0.800 | protect 0.800 over took_what_was_not_mine 0.740 |
| daniel_ate_it/1 m1 | mara | `avoid_exposure` in company | emotion:anxiety | protect 0.706 over prevent_argument 0.563 | prevent_argument 0.563 over protect 0.450 |
| daniel_ate_it/1 m4 | mara | `avoid_exposure` in company | emotion:anxiety | protect 0.655 over prevent_argument 0.563 | prevent_argument 0.563 over protect 0.450 |
| daniel_ate_it/1 m9 | mara | `avoid_exposure` in company | emotion:anxiety | protect 0.591 over prevent_argument 0.563 | prevent_argument 0.563 over protect 0.450 |
| daniel_ate_it/1 m17 | mara | `avoid_exposure` in company | emotion:anxiety | protect 0.624 over prevent_argument 0.563 | prevent_argument 0.563 over protect 0.450 |
| daniel_ate_it/2 m1 | daniel | `avoid_exposure` in company | emotion:shame | took_what_was_not_mine 0.892 over protect 0.800 | protect 0.800 over took_what_was_not_mine 0.740 |

#### 6. The same act, different reasons

Wants whose shipped proposals lead to `check_pantry`, read from `decisions.json`: `find_out`, `get_food`, `guard_supplies`, `restore_standing`.

A reason is stated as person evidence: each piece's share of the winner's margin over the runner-up, in that representation's own arithmetic. Circumstance statements are left out of the lists below.

##### At the top of the morning, in the kitchen, in company

| Want | Person | A | A° | B | C |
|---|---|---|---|---|---|
| `find_out` | daniel | assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 |
| `find_out` | elena | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| `find_out` | leo | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| `find_out` | mara | share_information: value:closeness 0.300, value:fairness 0.100, trait:honest 0.055 | share_information: value:closeness 0.300, value:fairness 0.100, trait:honest 0.055 | share_information: value:closeness 0.300, value:fairness 0.100, trait:honest 0.055 | share_information: value:closeness 0.300, value:fairness 0.100, trait:honest 0.055 |
| `get_food` | daniel | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 |
| `get_food` | elena | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| `get_food` | leo | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| `get_food` | mara | take_responsibility: trait:cautious 0.100 | take_responsibility: trait:cautious 0.100 | take_responsibility: trait:cautious 0.100 | take_responsibility: trait:cautious 0.100 |
| `guard_supplies` | daniel | assert_authority: value:control 0.600, belief:role_claim($self,leads_family) 0.440, trait:dominant 0.383 | assert_authority: value:control 0.600, belief:role_claim($self,leads_family) 0.440, trait:dominant 0.383 | assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | assert_authority: value:control 0.600, belief:role_claim($self,leads_family) 0.440, trait:dominant 0.383 |
| `guard_supplies` | elena | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 |
| `guard_supplies` | leo | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 |
| `guard_supplies` | mara | protect: value:closeness 0.250, trait:empathetic 0.225 | protect: value:closeness 0.250, trait:empathetic 0.225 | protect: value:closeness 0.250, trait:empathetic 0.225 | protect: value:closeness 0.250, trait:empathetic 0.225 |
| `restore_standing` | daniel | assert_authority: value:control 0.600, belief:role_claim($self,leads_family) 0.440, trait:dominant 0.383 | assert_authority: value:control 0.600, belief:role_claim($self,leads_family) 0.440, trait:dominant 0.383 | assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | assert_authority: value:control 0.600, belief:role_claim($self,leads_family) 0.440, trait:dominant 0.383 |
| `restore_standing` | elena | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 |
| `restore_standing` | leo | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 |
| `restore_standing` | mara | take_responsibility: trait:honest 0.165, trait:cautious 0.100 | take_responsibility: trait:honest 0.165, trait:cautious 0.100 | take_responsibility: trait:honest 0.165, trait:cautious 0.100 | take_responsibility: trait:honest 0.165, trait:cautious 0.100 |

##### At the top of the morning, in the kitchen, alone

| Want | Person | A | A° | B | C |
|---|---|---|---|---|---|
| `find_out` | daniel | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 |
| `find_out` | elena | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 |
| `find_out` | leo | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 |
| `find_out` | mara | take_responsibility: trait:honest 0.165, trait:proud 0.138, trait:cautious 0.100 | take_responsibility: trait:honest 0.165, trait:proud 0.138, trait:cautious 0.100 | take_responsibility: trait:honest 0.165, trait:proud 0.138, trait:cautious 0.100 | take_responsibility: trait:honest 0.165, trait:proud 0.138, trait:cautious 0.100 |
| `get_food` | daniel | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:cautious 0.070 |
| `get_food` | elena | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| `get_food` | leo | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| `get_food` | mara | take_responsibility: trait:cautious 0.100 | take_responsibility: trait:cautious 0.100 | take_responsibility: trait:cautious 0.100 | take_responsibility: trait:cautious 0.100 |
| `guard_supplies` | daniel | take_responsibility: value:family_safety 0.175, trait:honest 0.150, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:honest 0.150, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:honest 0.150, trait:cautious 0.070 | take_responsibility: value:family_safety 0.175, trait:honest 0.150, trait:cautious 0.070 |
| `guard_supplies` | elena | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:cautious 0.140 |
| `guard_supplies` | leo | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:cautious 0.140 |
| `guard_supplies` | mara | protect: value:closeness 0.250, trait:empathetic 0.225 | protect: value:closeness 0.250, trait:empathetic 0.225 | protect: value:closeness 0.250, trait:empathetic 0.225 | protect: value:closeness 0.250, trait:empathetic 0.225 |
| `restore_standing` | daniel | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 | take_responsibility: trait:proud 0.213, value:family_safety 0.175, value:respect 0.150 |
| `restore_standing` | elena | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:proud 0.088 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:proud 0.088 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:proud 0.088 | take_responsibility: value:family_safety 0.350, trait:honest 0.210, trait:proud 0.088 |
| `restore_standing` | leo | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:proud 0.125 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:proud 0.125 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:proud 0.125 | take_responsibility: value:family_safety 0.350, trait:honest 0.240, trait:proud 0.125 |
| `restore_standing` | mara | take_responsibility: trait:honest 0.165, trait:proud 0.138 | take_responsibility: trait:honest 0.165, trait:proud 0.138 | take_responsibility: trait:honest 0.165, trait:proud 0.138 | take_responsibility: trait:honest 0.165, trait:proud 0.138 |

##### In real mornings

**257 real pantry-checks** for those wants in 50 baseline mornings. Each is matched with every other member of the cast, at the same minute of the same morning: the same world, room, company, want and act, and their own real mind. **771 matched pairs.**

| | A | A° | B | C |
|---|---|---|---|---|
| Pairs forming different intentions | 486 (63.0 %) | 486 (63.0 %) | 486 (63.0 %) | 486 (63.0 %) |
| Pairs forming the same intention | 285 | 285 | 285 | 285 |
| ...of which led by different person evidence | **105** (36.8 %) | **105** (36.8 %) | **105** (36.8 %) | **105** (36.8 %) |
| ...of which the top three reasons differ as a set | 105 (36.8 %) | 105 (36.8 %) | 105 (36.8 %) | 105 (36.8 %) |
| ...of which the person evidence supporting that intention differs in any piece or weight (added after the first run) | **285** (100.0 %) | **285** (100.0 %) | **285** (100.0 %) | **285** (100.0 %) |

The last row was added after the first run, because the leading piece of evidence hides differences of weight: two people can both be led by `value:family_safety` and differ in how much their honesty adds. It compares, piece by piece, the person evidence each representation counts for the intention the two share.

##### What leads each intention, in real pantry-checks and their matched partners

| Rep | Intention | Leading person evidence, by count |
|---|---|---|
| A | assert_authority | `trait:dominant` 120, `value:control` 10 |
| A | protect | `value:closeness` 10 |
| A | share_information | `value:closeness` 120 |
| A | take_responsibility | `value:family_safety` 576, `trait:cautious` 90 |
| A | took_what_was_not_mine | `belief:answerable_for($self,missing_can)` 102 |
| A° | assert_authority | `trait:dominant` 120, `value:control` 10 |
| A° | protect | `value:closeness` 10 |
| A° | share_information | `value:closeness` 120 |
| A° | take_responsibility | `value:family_safety` 576, `trait:cautious` 90 |
| A° | took_what_was_not_mine | `belief:answerable_for($self,missing_can)` 102 |
| B | assert_authority | `trait:dominant` 130 |
| B | protect | `value:closeness` 10 |
| B | share_information | `value:closeness` 120 |
| B | take_responsibility | `value:family_safety` 576, `trait:cautious` 90 |
| B | took_what_was_not_mine | `belief:answerable_for($self,missing_can)` 102 |
| C | assert_authority | `trait:dominant` 120, `value:control` 10 |
| C | protect | `value:closeness` 10 |
| C | share_information | `value:closeness` 120 |
| C | take_responsibility | `value:family_safety` 576, `trait:cautious` 90 |
| C | took_what_was_not_mine | `belief:answerable_for($self,missing_can)` 102 |

##### Is the stated reason a property of the person, or of how the rules were written?

Each real pantry-check re-decided with one rule copied, for each of the ten rules in turn (2570 re-decisions), and again with one rule partly copied. Nothing about the person changes.

| Copy: the intention changed | 110 | 110 | 0 | 0 |
| Copy: same intention, **different leading reason** | **0** | **0** | **0** | **0** |
| Partial copy: the intention changed | 110 | 110 | 0 | 110 |
| Partial copy: same intention, **different leading reason** | **20** | **20** | **0** | **20** |

##### A few real pairs, under B

| Morning | Want | Who checked the pantry, and why | The same moment for somebody else |
|---|---|---|---|
| daniel_ate_it/1 m9 | `get_food` | elena: take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | mara: take_responsibility: trait:cautious 0.100 |
| daniel_ate_it/3 m9 | `get_food` | mara: take_responsibility: trait:cautious 0.100 | elena: take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| daniel_ate_it/3 m9 | `get_food` | mara: take_responsibility: trait:cautious 0.100 | leo: take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| elena_fed_mara/3 m9 | `get_food` | mara: take_responsibility: trait:cautious 0.100 | daniel: take_responsibility: value:family_safety 0.175, trait:cautious 0.070 |
| daniel_ate_it/1 m1 | `find_out` | daniel: assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | elena: take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| daniel_ate_it/1 m1 | `find_out` | daniel: assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | leo: take_responsibility: value:family_safety 0.350, trait:cautious 0.140 |
| daniel_ate_it/1 m1 | `find_out` | daniel: assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 | mara: share_information: value:closeness 0.300, value:fairness 0.100, trait:honest 0.055 |
| daniel_ate_it/1 m1 | `find_out` | leo: take_responsibility: value:family_safety 0.350, trait:cautious 0.140 | daniel: assert_authority: trait:dominant 0.383, value:control 0.350, belief:role_claim($self,leads_family) 0.240 |

#### Z. The frozen file after the whole run

**sha256: `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` — unchanged.** Every rewritten rule set and every representation above lived in memory.

---

## predictions.md

### Intention representation: predictions

Written and committed **before the fixture that measures any of this existed**.
The predictions come from reading the frozen rule file, the shipped character
sheets and the ranking experiment's published numbers; nothing was simulated to
write them. They are kept as written, and `results.md` scores each one.

Every prediction is marked as one of two kinds:

- **analytic**: it follows from the rule file by arithmetic. If it fails, the
  fixture is wrong or I misread the file.
- **empirical**: it is a guess about a measurement. If it fails, that is a
  finding.

#### What this experiment is for

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

#### What is frozen

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

#### The representations, fixed now

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

#### The tests, fixed now

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

#### Predictions

##### 1. Which invariants A fails (analytic, from the ranking experiment)

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

##### 2. Which invariants B is expected to satisfy (analytic)

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

##### 3. Which invariants C is expected to satisfy (analytic)

| | Result expected for C |
|---|---|
| R1, R2, R3 | pass: 0 |
| R4a, R4b, R4c | pass: 0. A reason's identity is a set, so reordering does not hide it |
| **R4d** | **fail**. A partial copy reads a different set of evidence, so C takes it for a different reason and adds it. *Empirical*: the same count as A's R4d, give or take the cells A breaks by name |
| R5 | fails by design, and is flagged, for the same reason as B |
| R6, R7, R8, R9, R10 | pass |

**So the tests separate B from C at exactly one point:** a restatement that
drops a term. That is the kind of rewrite an author makes without noticing.

##### 4. Does B preserve what the generalization experiment proved?

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

##### 5. Does C preserve it?

| | Prediction | Kind |
|---|---|---|
| 5.1 | **C reaches the same intention as A in every cell except the real ties.** The frozen file holds no two rules with the same reason signature. The discard never changed a winner. So C differs from A only where A breaks a tie by a name or by rounding: 25 cells, which C reports as ties | analytic |
| 5.2 | Hence 28.6 %, blindness, replay and no character rules all hold. The 56 signatures and the 8,407 changes hold up to the tie cells | analytic |

##### 6. The 35.7 % forced share

| | Prediction | Kind |
|---|---|---|
| 6.1 | **Unchanged at 35.7 % under A, A°, B and C.** B changes nothing in any group that is forced now | analytic |
| 6.2 | Its causes: the four K = 1 groups (28.6 %), cause 1, no alternative candidate. Plus `restore_standing` alone (7.1 %), where `prevent_argument` is cause 2, dominated for every possible person, and `assert_authority` is cause 4, not dominated, but needing anger that no sweep profile carries. **No forced cell is caused by the representation** (cause 3) | analytic |
| 6.3 | Even in the live mornings, which do carry anger, `assert_authority` **never** wins `restore_standing` alone for the real cast. Daniel is the most disposed to it, and he would need anger of 2.2 on a scale that stops at 1 (0.500 + 0.3 x anger against his 1.158). So for the cast this convergence is not an artifact of a sweep without feelings | analytic |

##### 7. Person sensitivity with the candidates fixed

| | Prediction | Kind |
|---|---|---|
| 7.1 | The compatible set changes in **0** of 642,978 person moves, under every representation | analytic |
| 7.2 | With the candidate set fixed, sensitivity stays **non-trivial**: above 1 % of contested pairs for A, B and C | empirical |
| 7.3 | C's sensitivity equals A's (6.1 %) to within the tie cells. B's is between 6.1 % and 8 %, because B makes three groups less lopsided | empirical |

##### 8. Semantic counterfactuals: the same act, different reasons

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

##### 9. Does previously idle evidence become influential merely because of representation?

| | Prediction | Kind |
|---|---|---|
| 9.1 | **No, under B or C.** `anxious` stays idle everywhere. `honest` still cancels in `get_food`, because the two rivals there are different intentions and B only merges within one. `respect` is still live only through anger. No evidence changes status between A, B and C | analytic |
| 9.2 | **Under A, restating a single rule *creates* influence.** Copying `what_you_did_in_the_night` gives `took_what_was_not_mine` 0.60 of `honest` against 0.30, so honesty, which cannot choose in `get_food` today, starts to choose. Under B, never. Under C, not by an exact copy, but yes by a partial one | analytic |
| 9.3 | In the live-state cells, zeroing `anger` changes some intention, and so does zeroing `anxiety`, under every representation. For `shame` I do not know | empirical |

##### 10. Can a representation tell "the same evidence twice" from "two different pieces of evidence" without counting rules?

**Analytic.** Both B and C recognise repeats by content and not by rule count. B
catches every repeat of a piece of evidence, including partial restatements and
splits. C catches only repeats of a whole reason.

**Neither can decide the one case the frozen file actually contains:** the same
fact read by two different reasons. B counts it once and C counts it twice, and
the invariants cannot choose between them, because both pass every test except
the one that separates them (R4d). **That is a semantic decision the
representation has to make explicit, not something a formula or a validator can
find.** On the frozen file it decides the three groups of prediction 4.5.

#### What would decide the verdict

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

---

## results.md

### Intention representation: results against the predictions

The measurements are in `measurements.md`, generated by
`IntentionRepresentationExperimentTests`. The predictions, the representations,
the tests and the verdict criteria were committed in `a21fc76`, before the
fixture existed.

#### Runs

| | |
|---|---|
| Rule file | frozen. sha256 `61e6412e...b099d92` verified at the **start and the end**, unchanged |
| A against the selector | **0 of 30,618** winners differ; every weight equal to the bit; A's duplicate count through `Form` itself: **19,992**, the published figure |
| Representations | A, A° (ablation), B, C; B-mean for policy sensitivity only |
| Cells | 30,618 per rule set; 94 rewritten rule sets; 642,978 person moves; 25,823 live cells from 3,689 real decision moments; 257 real pantry-checks, 771 matched pairs |
| Fixture tests | **8 of 8 pass**, about 15 minutes. Run twice; the second run reproduced the first byte for byte, apart from the two edits made between them (below) |
| Randomness | none |
| Production changes | **none** |

**Two things were decided after the predictions were committed, and are stated
here rather than hidden:**

1. **Before any run**, "the strongest statement" was implemented as the largest
   in magnitude, keeping the sign. The largest value would have let a 0.99 copy
   of a negative term (-0.2475) replace the original (-0.25).
2. **After the first run**, one row was added to section 6 of the
   measurements: whether two people forming the same intention rest on
   different person evidence in any piece or weight, not only in the leading
   piece. And the example pairs listed there were de-duplicated, because the
   first run showed the same two people four times. Nothing else was changed
   between the runs.

#### Predictions

##### 1. Which invariants A fails

| | Predicted | Result | |
|---|---|---|---|
| R1, R2 | pass | 0, 0 | **PASS** |
| R3 | fail: 12 by name | 12, every one a tie | **PASS** |
| R4a | fail: 19,992 | 19,992 | **PASS** |
| R4b | fail: 19,992, give or take ties | 19,992 | **PASS** |
| R4c | fail: 19,844 | 19,844 | **PASS** |
| R4d | *empirical*: fail, 14,000 to 21,000 | 18,938 | **PASS** |
| R5 | pass | 0 and 0 | **PASS** |
| R6, R7, R8 | pass | 19,992; 0 away; 0 outside | **PASS** |
| R9 | fail by term (469), merge 0 | 469, 0 | **PASS** |
| R10 | fail: 243 | 243 | **PASS** |

##### 2. Which invariants B satisfies

| | Predicted | Result | |
|---|---|---|---|
| R1, R2, R3 | 0 | 0, 0, 0 | **PASS** |
| R4a-d | 0 for all four | 0, 0, 0, 0 | **PASS** |
| R5 | changes, every changed cell flagged | 15,210 and 19,340 changed; **0 unflagged**; 78,732 of 78,732 cells where the split rule applies flagged | **PASS** |
| R6, R7, R8 | responds; 0 away; 0 outside | 22,520; 0; 0 | **PASS** |
| R9 | 0, 0 | 0, 0 | **PASS** |
| R10 | 0 | 0 | **PASS** |

##### 3. Which invariants C satisfies

| | Predicted | Result | |
|---|---|---|---|
| R1, R2, R3, R4a-c | 0 | 0 each | **PASS** |
| R4d | fail, *empirical*: A's count give or take ties | **19,062, none flagged**: exactly A°'s count | **PASS** |
| R5 | changes, flagged | 13,796 and 18,632; 0 unflagged | **PASS** |
| R6 to R10 | pass | 20,021; 0 away; 0 outside; 0; 0 | **PASS** |

##### 4. Does B preserve the generalization properties?

| # | Prediction | Kind | Result | |
|---|---|---|---|---|
| 4.1 | 28.6 % single-candidate, identical | analytic | 28.6 % (8,748) | **PASS** |
| 4.2 | No character-specific rule | analytic | 0 | **PASS** |
| 4.3 | Hunger and a foodless room: 0 | analytic | 0 and 0 of 30,618 each | **PASS** |
| 4.4 | Exact replay | analytic | 2,100 of 2,100 | **PASS** |
| 4.5 | B differs from A° only in the three groups, and only away from `protect` or `assert_authority` | analytic | 660 cells, all in the three groups, 660 of 660 away from those two | **PASS** |
| 4.6 | `look_after -> protect` in company: 65 % to 80 % | empirical | **78.2 %** | **PASS** |
| 4.7 | `assert_authority` in company: 55 % to 75 % | empirical | **69.0 %** (`guard_supplies`), **70.4 %** (`restore_standing`) | **PASS** |
| 4.8 | Circumstance changes fewer than 8,407, by under 10 % | empirical | **8,094**, 3.7 % fewer | **PASS** |
| 4.9 | Signatures not 56; more rather than fewer | empirical | **78** | **PASS**, and not read as a gain |

##### 5. Does C preserve them?

| # | Prediction | Result | |
|---|---|---|---|
| 5.1 | Same intention as A everywhere except the 25 real ties | differs in 25 cells, 25 of them ties C reports | **PASS** |
| 5.2 | So everything holds up to the tie cells | 28.6 %; blindness 0; replay exact; 64 signatures and 8,412 changes, the extra all from the 25 reported ties | **PASS** |

##### 6. The forced share

| # | Prediction | Result | |
|---|---|---|---|
| 6.1 | 35.7 % under A, A°, B and C | 35.7 % (10,935) under all four | **PASS** |
| 6.2 | Causes: 28.6 % no alternative; `restore_standing` alone: `prevent_argument` dominated, `assert_authority` evidence-limited by anger; no representation cause | exactly those, under all four | **PASS** |
| 6.3 | In real mornings, `assert_authority` never wins `restore_standing` alone for the cast | 0 of 560, under all four | **PASS** |

##### 7. Person sensitivity with the candidates fixed

| # | Prediction | Result | |
|---|---|---|---|
| 7.1 | The compatible set never changes | 0 of 642,978, under all four | **PASS** |
| 7.2 | Non-trivial, above 1 %, for A, B and C | 6.1 %, 7.1 %, 6.1 % | **PASS** |
| 7.3 | C equals A; B between 6.1 % and 8 % | C 6.1 %; B **7.1 %** | **PASS** |

##### 8. Semantic counterfactuals

| # | Prediction | Kind | Result | |
|---|---|---|---|---|
| 8.1 | All representations state person-specific reasons that differ between matched people | empirical | 63.0 % of 771 real pairs form different intentions; of the 285 that form the same one, 36.8 % are led by different evidence, and all 285 rest on different evidence in some piece or weight (a row added after the first run) | **PASS** |
| 8.2 | Daniel `assert_authority` led by `dominant`, Leo `take_responsibility` led by `family_safety`, the same under all four | analytic | exactly | **PASS** |
| 8.3 | Daniel's `assert_authority` in `guard_supplies` and `restore_standing` in company: led by `control` under A and C, by `dominant` under B | analytic | `control` 0.600 under A and C; `dominant` 0.383 under B | **PASS** |
| 8.4 | Restating one rule changes the leading reason of some real decisions under A, and of none under B; C immune to exact copies, not to partial ones | empirical for A, analytic for B | **B: 0**, as predicted. C: 0 for copies; 110 intentions and 20 leading reasons for partial copies, as predicted. **A: an exact copy never re-ranks the reasons behind an unchanged intention (0); it changes the intention itself in 110 of 2,570 real decisions. Only a partial copy re-ranks reasons (20)** | **PARTLY**: right that A's stated reasons move and B's do not; wrong about how. Copying a rule scales all its statements together, so their order is kept; what moves is the label |

##### 9. Idle evidence

| # | Prediction | Result | |
|---|---|---|---|
| 9.1 | No evidence changes status between A, B and C | none, in any group, under any of the four | **PASS** |
| 9.2 | Under A a single restatement creates influence; never under B; under C only by a partial copy | A 5 and 5, B 0 and 0, C 0 and 5 (group, evidence) pairs. Measured: honesty in `get_food`, 0 on the frozen file, **1,134 of 8,748** moves with `what_you_did_in_the_night` copied under A; B 0; C 0 copied, 1,134 partly copied | **PASS** |
| 9.3 | *Empirical*: zeroing anger and anxiety changes some intention under every representation; shame unknown | anger 33 of 1,420; anxiety 216 of 6,171; **shame 60 of 1,500**; identical under all four | **PASS**, and the unknown resolved: yes |

##### 10. Same evidence twice, or two pieces of evidence?

| Predicted | Result | |
|---|---|---|
| Both B and C recognise repeats without counting rules. B catches every repeat of a piece of evidence, C only repeats of a whole reason. Neither can decide the file's actual case, one fact cited by two different reasons, and R4d is the only test that separates them | B recognises restatement in 6,561 cells of the frozen file (exactly the three groups) and C in none. They disagree in 660 cells, and nothing but R4d separates them | **PASS** |

#### Verdict criteria

| Criterion | Measured | Met |
|---|---|---|
| B passes R1 to R4, R6 to R10, R5 by explicit detection | yes: see section 2 above | yes |
| Keeps 28.6 %, blindness, replay, non-trivial sensitivity | 28.6 %; 0; exact; 7.1 % | yes |
| Expresses person-specific reasons for the same act, stable under restatement | 771 pairs; 0 reason or intention changes under B across 5,140 re-decisions | yes |
| C fails a test B passes | R4d, 19,062 unflagged | yes |
| **B's changes depend on no policy it had to invent** | **no: 660 cells rest on counting one fact once, and 242 of them on how** | **not met: MODIFY** |
| REBUILD: B fails its own tests, or loses person dependence or blindness | no | not triggered |
| ABANDON: no representation can state reasons as evidence | all can | not triggered |

**Verdict: MODIFY**, as expected.

#### Not predicted

| Finding | Evidence |
|---|---|
| **B is more weight-sensitive than A.** Doubling a rule moves 22,520 cells against 19,992, because B leaves three groups less lopsided, so there is more to tip | R6 |
| **The conflict policy alone decides 242 cells**, more than a third of B's 660 | B against B-mean |
| **Pasting a line can bring a dead trait back to life under A.** Copying `letting_it_go_for_now` makes `anxious`, idle for every possible person, live in `restore_standing` alone | section 5, restatement table |
| **An exact copy never re-ranks reasons under A; it flips the label instead.** A partial copy does both | section 6 |
| **Feelings are untouched by the choice of representation.** No feeling is read twice for one intention anywhere in the file, so anger, anxiety and shame move exactly the same cells under all four | section 5, feelings |
| **On real mornings, the B/C disagreement barely shows.** It changes no real pantry-check's intention. It changes the leading reason in only 10 of the 1,028 decisions (257 checks and their 771 partners), every one an `assert_authority` for `guard_supplies` in company, led by `control` under A and C and by `dominant` under B. The disagreement is concentrated where the sweep puts many dominant, controlling people in company | section 6 |
| **The discard costs nothing to remove.** Without it (A°), no winner changes except by reporting ties, and R9a and R10 clear | A° column |

#### Classification

In the report, section 13, and machine-readable in `classification.json`.

