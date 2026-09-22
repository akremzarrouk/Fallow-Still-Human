# Intention representation: what the ranking layer must keep

*Can a representation that knows what evidence each reason reads stop the way
rules are written from becoming part of the person, while keeping everything
the intention mechanism has already been shown to do?*

## 1. The answer, first

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

## 2. What was run

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

## 3. The four readings of the same file

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

## 4. The invariants

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

## 5. What is preserved

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

## 6. Where B changes conclusions, and why that is a decision, not a finding

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

## 7. The same act, different reasons

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

## 8. Candidate stages

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

## 9. The 35.7 % forced share

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

## 10. Evidence-read audit

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

## 11. What the ranking layer must keep

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

## 12. Limitations

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

## 13. Classification

| | |
|---|---|
| **PROVEN** | A is the selector (0 of 30,618). Evidence identity (B) is invariant to exact, reworded, near and partial restatement (0 each). Reason identity (C) is defeated by partial restatement (19,062, none flagged). No representation can treat a proportional split as the unsplit rule while refusing to strengthen restatements, and B and C both flag it in 78,732 of 78,732 cells. The discard is responsible for exactly R9a (469) and R10 (243). Tie reporting clears R3. B, A° and C preserve 28.6 %, blindness, replay, no character rules and non-trivial fixed-candidate sensitivity (7.1 %, 6.1 %, 6.1 %). C equals A outside 25 reported ties. B differs from A° in 660 cells, all away from `protect` or `assert_authority`, in the five places the file states one fact twice. The conflict policy alone decides 242 cells. The forced share is 35.7 % under every representation, with no representation cause. No evidence changes status between representations. Restating one rule makes cancelled or idle evidence live under A (5 pairs) and never under B. The same act is carried by different intentions in 63.0 % of matched real pairs, and under A one copied rule changes 110 of 2,570 real intentions, against 0 under B |
| **PLAUSIBLE** | That evidence identity is the right unit for a production ranking layer: it is the only one tested that passes every restatement, but it was tested on one file. That B's stated reasons are closer to a person's reasons than A's: they are invariant to rewriting, which A's are not, but invariance is not truth |
| **UNPROVEN** | Whether one fact cited by two reasons should count once (B) or twice (C), and if once, how (strongest, mean, or something else). Whether B's 660 changed conclusions are improvements. Whether B's base-by-gate identity is right, since the file never exercises it |
| **FAILED** | A as a representation: R3, R4a-d, R9a, R10, and influence created by pasting a line. C as a replacement: silently defeated by partial restatement. The hope that evidence identity alone would settle the representation: it leaves the shared-fact decision open, and that decision moves real conclusions |
| **UNKNOWN** | Psychological correctness of any conclusion. Behaviour on a file with many shared facts, or with feelings varied across the whole sweep. Whether any declared shared-fact rule would survive an authored file larger than ten rules |

## 14. Verdict

# MODIFY

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

**Suite: pending**, to be filled in from the full run.
