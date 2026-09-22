# intention-ranking: all documents

Merged by `merge-slice-docs.py` from the 4 Markdown files in `Docs/experiments/intention-ranking/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)

---

## report.md

### Intention ranking: what a selection mechanism must satisfy

*What properties must an intention-selection mechanism have for us to treat it as
a credible causal mechanism rather than an arbitrary numerical ranking, and which
of them does the current one have?*

#### 1. The answer, first

A credible mechanism has to meet three kinds of requirement.

1. **Its conclusion must not depend on how the same psychology is written
   down.** Rule order, rule names, intention names, restating a reason, and
   regrouping the same reasons must not change what a person intends.
2. **It must be clear what is allowed to change a conclusion.** A stronger reason
   can win and never makes its own intention lose. Changing a reason only affects
   the cases where it applies. What is *possible* depends on the want and the
   circumstance, and is declared. The person decides only among the possible.
   Everything the mechanism reads about a person can matter to somebody,
   somewhere.
3. **It must know when two reasons are the same reason.** This one is forced by
   a theorem, not chosen. No way of adding up anonymous contributions can ignore
   a restated reason, survive a weight-preserving split, and still respond to
   weight. The only way out is for a rule to carry the identity of the evidence
   it reads. That is a requirement on how rules are represented, not on the
   formula.

Measured against these, the current mechanism is sound **below** ranking and
unsound **at** ranking:

- **What holds.** The want decides what is available. The circumstance decides
  what is compatible, and no change to the person altered the compatible set in
  any of 642,978 tries. With the candidate set held fixed, the person still
  changes the intention in 6.1 % of contested single-attribute moves.
- **What fails.** Copying one existing rule, and changing nothing about anybody,
  reverses **48.8 %** of all conclusions in the sweep. 25 real ties are decided by
  the alphabet or by rounding. A negative term deletes the positive terms written
  in the same rule. Nine times, an intention is made impossible by gates that
  nobody declared, and eight of those override what the person would otherwise
  have chosen.

**Verdict: MODIFY** (section 14). The problem sits in ranking and in how a rule
represents its evidence. It is not in the architecture's decomposition of want,
circumstance and person.

#### 2. What was run

| | |
|---|---|
| Rules | the ten frozen rules, sha256 `61e6412e...b099d92`, checked at the start and the end: **unchanged** |
| Selector | `IntentionSelector.Form`, untouched |
| Production | nothing under `Scripts/Core`, no shipped data, no shipped weight |
| People | the 2,187-profile sweep of the generalization experiment, rebuilt, and checked against its published numbers: 28.6 %, 56 signatures, 8,407, 2,898, **all reproduced exactly** |
| Cells | **30,618** (profile x want x circumstance), every test on every cell |
| Person moves | 21 per profile (each trait to its other two levels, adjacent value ranks swapped, each belief toggled): 642,978 pairs |
| Rule-file rewrites | 11 transformations, 65 rewritten rule sets, and 17 more with gates lifted, all in memory |
| Aggregators | 6, parameter-free, fixed in the predictions before anything ran, and defined only in the fixture |
| Randomness | none |

The fixture takes the selector apart into the five stages it already has. It
runs stages 1 to 3 itself, so that stage 4 can be swapped. It checks on every cell
that, under the sum, the result is the selector: **0 of 30,618 cells differ,
and every winning weight is equal to the bit.** The same check passes on every
rewritten rule set that goes through `Form`.

| Stage | Depends on | Measured |
|---|---|---|
| 1 availability: a rule lists the want | the want | 2 or 3 intentions per want |
| 2 compatibility: its `when` matches | want + circumstance | **0** of 642,978 person moves changed it |
| 3 support: `base + factor x level` | the person | through the shipped `ScalerEval` |
| 3/4 **the discard**: a contribution <= 0 is thrown away | the person | 243 cells, 0 winners |
| 4 preference: the intention's score | the aggregation | the sum of its rules' contributions |
| 5 selection: the highest score | the score, **and the alphabet at a tie** | 12 exact ties, 13 more decided by rounding |

#### 3. Where availability decides, and where preference does

##### Availability

| | Cells | Share |
|---|---|---|
| One compatible intention: `avoid_exposure`, `find_out`, `keep_peace`, `look_after`, all alone | 8,748 | 28.6 % |
| ...plus `restore_standing` alone: three compatible intentions, and one winner for all 2,187 people | 2,187 | 7.1 % |
| **Same intention for every profile in the sweep** | **10,935** | **35.7 %** |
| **Changed by lifting every gate** | **8,407** | **27.5 %** |

In `restore_standing` alone, `prevent_argument` is **dominated for every
possible person**. Its best margin over `take_responsibility`, bounded over the
whole unit box, is -0.070. `assert_authority` is not dominated, but it can only
win through anger, which the sweep never contains. So three candidates, and no
person.

Lifting every gate changes exactly **8,407** cells. That is the same number that
company arriving changes, and it is not a coincidence. For every want, an
intention's gated reasons are either all company-only or all alone-only. So the
ungated winner always equals one of the two situated winners. **Every change a
circumstance makes to an intention is a gate decision.** Of those 8,407:

| Cause | Changes | Share |
|---|---|---|
| Availability: the new winner is an intention no rule offers alone | 4,911 | 58.4 % |
| A reason gated in or out, re-weighting intentions available in both | 3,496 | 41.6 % |

##### Preference

**19,683 cells (64.3 %)** are in groups where the winner varies with the person.
To separate preference from candidate generation, the circumstance was held and
one attribute of the person moved. The compatible set changed in **0** of 642,978
pairs. The supported set changed in 2,184, **all** of them through the discard.
With the candidate set identical:

| Compatible candidates | Pairs | Intention changed |
|---|---|---|
| 1 | 183,708 | **0** |
| 2 | 137,781 | 6,115 (**4.4 %**) |
| 3 | 319,305 | 21,836 (**6.8 %**) |
| 2 or 3 | 457,086 | 27,951 (**6.1 %**) |

| Moved | Changed | | Moved | Changed |
|---|---|---|---|---|
| belief `answerable_for` | 26.4 % | | trait `dominant` | 6.3 % |
| trait `honest` | 12.0 % | | value ranks 1-2 ... 4-5 swapped | 4.4 - 5.2 % |
| belief `role_claim` | 10.0 % | | trait `proud` | 1.8 % |
| trait `empathetic` | 9.8 % | | trait `anxious` | **0** |
| trait `cautious` | 6.5 % | | trait `impulsive` (read by no rule) | **0** |
| | | | value ranks 5-6 swapped | **0** |

**Preference is real, and it is separate from candidate generation.** It is also
modest. A single change to a person moves the intention about one time in
sixteen. One belief, `answerable_for`, moves it more than twice as often as any
trait.

##### More candidates do not mean more person

| K | Groups | Winners per group | Entropy (bits), range | Sensitivity, pooled | Range across groups |
|---|---|---|---|---|---|
| 1 | 4 | 1 | 0 | 0 | 0 |
| 2 | 3 | 2 | 0.70 - 0.99 | 4.4 % | 3.5 - 4.9 % |
| 3 | 7 | 2.71 | 0 - 1.43 | 6.8 % | **0** - 10.9 % |

A third candidate adds variation only if it is contestable. `restore_standing`
alone has three candidates and less variation than any group with two.
`guard_supplies` in company, also three, is less sensitive (4.0 %) than
`get_food` with two (4.9 %).

##### What gating currently means

The brief asks whether gating behaves as hard impossibility, situational
plausibility or preference. **Mechanically it is hard impossibility, at the
level of a reason.** A gated-out rule contributes exactly nothing, whatever the
person. It never depends on the person (0 of 642,978), and nothing is ever
partially gated. So it is never preference and never graded plausibility.

At the level of an **intention** it is something nobody wrote. A gate removes a
reason. An intention becomes impossible only where every reason for it happens
to be gated, and that is decided as much by which wants each rule lists as by
any gate. There are **nine** such exclusions, and none is declared anywhere:

| Group | Excluded | Would-be support, min / median / max | Would have won, of 2,187 people |
|---|---|---|---|
| `keep_peace` alone | share_information | 0.255 / 0.520 / 0.860 | **88.9 %** |
| `look_after` alone | share_information | 0.255 / 0.520 / 0.860 | **83.2 %** |
| `keep_peace` alone | protect | 0.210 / 0.490 / 0.840 | **81.5 %** |
| `avoid_exposure` alone | protect | 0.210 / 0.490 / 0.840 | 44.5 % |
| `look_after` alone | prevent_argument | 0.000 / 0.323 / 0.710 | 41.8 % |
| `avoid_exposure` alone | prevent_argument | 0.000 / 0.323 / 0.710 | 28.8 % |
| `find_out` alone | assert_authority | 0.190 / 0.680 / 1.113 | 14.4 % |
| `find_out` alone | share_information | 0.255 / 0.520 / 0.860 | 1.9 % |
| `restore_standing` in company | prevent_argument | 0.148 / 0.305 / 0.463 | 0 (the gate decides nothing) |

In **eight of nine**, the gate overrides a preference that goes one way for some
people and the other way for others. Reason-level gates decide a great deal too.
Lifting only `pulling_rank_needs_an_audience`'s gate changes `guard_supplies`
alone for **78.7 %** of people, and lifting only `letting_it_go_for_now`'s
changes `keep_peace` in company for 42.8 %.

The authored notes use this one switch for two different things. My reading,
which is a judgement and not a measurement:

| Rule | Gate | What its note says | Reading |
|---|---|---|---|
| `pulling_rank_needs_an_audience` | company | "Nobody pulls rank in an empty room" | a precondition of this reason; the intention stays available alone |
| `doing_it_where_nobody_is_watching` | alone | the reason is being unwatched | a precondition of this reason |
| `standing_between_them_and_it` | company | "takes somebody to put yourself in front of" | a precondition of this reason |
| `not_making_a_scene_of_it` | company | "Needs a scene to not make" | a precondition of this reason |
| `so_that_they_know_too` | company | "Needs somebody to tell" | **plausibility written as a precondition**: one can find out for people not in the room. It is share_information's only rule, so it makes the intention impossible alone |
| `letting_it_go_for_now` | alone | "with nobody there to have it out with yet" | **plausibility**: people let things go in company too |

**So gating currently means "this reason does not apply here", enforced as an
impossibility. It then composes into intention-level impossibilities that no one
decided.**

#### 4. What the current mechanism treats as meaningful

| Five ways to write one rule | Same total weight as W? | Treated as |
|---|---|---|
| W | - | class 1 |
| 2 rules x W/2 | yes | class 1: **0** of 306,180 (rule, cell) pairs differ |
| 4 rules x W/4 | yes | class 1: **0** differ |
| 1 rule x 2W | no | class 2 |
| W + W, the same rule twice | no | class 2: **0** cells differ from 2W, in any rule |

**The one representation change the sum treats as psychologically meaningful is a
change of total weight per intention.** It cannot tell "one stronger reason"
from "the same reason, said twice": both move the same 19,992 cells, cell for
cell.

| Rewrite | Should it change anything? | Cells changed |
|---|---|---|
| Duplicate one rule (T4) | no | **19,992**, every one toward the copied rule's intention, none outside where it applies |
| Near-duplicate, x 0.99 (T5) | no | **19,844** |
| Split into halves or quarters (T6, T7) | depends on what a rule is | **0** (regression invariant, asserted) |
| Split by term (T8) | no | **469**, all from `not_making_a_scene_of_it` |
| Merge co-compatible rules (T10) | no | 0 |
| Rename the intentions (T3) | no | **12**, every one an exact tie |
| Reverse order, rename rules, duplicate everything (T1, T2, T11) | no | 0 |

- **14,935 of 30,618 cells (48.8 %)** have a conclusion that copying one
  existing rule reverses. 217 of them can be reversed by copying any one of
  three different rules.
- **The discard makes grouping matter.** Split `not_making_a_scene_of_it` by
  term, and its negative `dominant` piece becomes a rule of its own. That rule
  weighs below zero and is thrown away, so the intention gains weight it never
  had.
- **25 cells are real ties.** Every level in the sweep is a whole multiple of
  0.05, and so is every factor, and every base is a multiple of 0.01. So every
  contribution is a whole multiple of 0.0025, and two real scores that differ at
  all differ by at least that. A gap below 1e-9 is a tie. Of the 25,
  12 are exactly equal and go to whichever intention's name sorts first. The
  other 13 differ only by floating-point rounding, and the rounding decides.

#### 5. The aggregation family, and why none of it is the answer

Stages 1 to 3 held, only the aggregation swapped. None of these is a proposal.

| | T4 duplicate | T5 near-dup. | T6 split | T8 by term | T9 2W | T10 merge | Monotone | Keeps | Gives up |
|---|---|---|---|---|---|---|---|---|---|
| **sum** (current) | **V** 19,992 | **V** | P | **V** 469 | responds | P | yes | weight, splitting, merging | restatement, term-grouping |
| max | P | P | **V** 16,721 | **V** | responds | **V** | yes | restatement | splitting, merging |
| mean | **V** 1,473 | **V** | **V** | **V** | responds | **V** | **no: 819 changes away** | only what all six keep | every rewrite of one rule, and monotonicity |
| normalized max | P | P | P | **V** 41,802 | **no response** | **V** | yes | restatement, splitting | **weight**, term-grouping, merging |
| noisy-OR | **V** 17,592 | **V** | **V** | **V** | **no response** | **V** | yes | little | restatement, splitting, **weight** |
| deduplicated sum | P | **V** 19,844 | **V** 13,743 | **V** 469 | responds | P | yes | exact copies | near-copies, splitting |

Four things stand out.

- **Deduplication is not the fix.** It is identical to the sum on the real file,
  which contains no exact duplicate. It defeats only the copy this experiment
  manufactures, and fails on a copy at 0.99 (19,844).
- **Normalized max survives restatement and splitting by ignoring weight.**
  Writing a rule at twice the weight does nothing, so an author cannot say one
  reason is stronger than another. It still fails term-grouping and merging.
- **More variety is not more validity.** noisy-OR gives the most distinct
  signatures of any aggregator (100, against the sum's 56) while ignoring weight
  and treating a copy as independent evidence.
- **Mean is not monotone.** Adding a copy of a reason for X made X *lose* in 819
  cells.

**The impossibility.** Let `f` score an intention. Invariance to restatement
gives `f(w/2, w/2) = f(w/2)`. Invariance to splitting gives
`f(w/2, w/2) = f(w)`. Together they give `f(w) = f(w/2)`, so weight cannot matter.
This was committed before the run. The measurement agrees: **none of the six
keeps T4 and T6 and responds to T9**, and each gives up at least one.

The consequence is the main finding of this experiment. **Whether a second rule
is new evidence or the same evidence twice cannot be known by any formula over
numbers.** Two contributions of 0.3 look the same whether they come from two
independent reasons or one reason written twice. The information that tells
them apart has to be in the representation of a rule.

#### 6. The properties, and where the current mechanism stands

##### Representation: the answer must not depend on how the psychology is written

| | Property | Test | Current |
|---|---|---|---|
| R1 | Rule order is not psychology | T1 | **holds** (0) |
| R2 | Rule names are not psychology | T2 | **holds** (0) |
| R3 | Intention names are not psychology, so a tie is a tie | T3; ties | **fails**: 12 cells decided by the alphabet, 13 by rounding |
| R4 | Restating a reason does not strengthen it | T4, T5 | **fails**: 19,992 and 19,844; 48.8 % of conclusions reversible |
| R5 | The same reasons, grouped differently, conclude the same | T8, T10 | **fails, narrowly**: T10 holds; T8 moves 469 cells through the discard |
| R6 | Scaling everything together changes nothing | T11 | **holds** (0) |

##### Causation: what may change the answer, and how

| | Property | Test | Current |
|---|---|---|---|
| C1 | A stronger reason can win | T9 | **holds** (19,992) |
| C2 | Strengthening a reason for X never makes X lose | duplication, direction | **holds** (0 away) |
| C3 | Changing a reason changes only cases where it applies | every per-rule rewrite | **holds** (0 outside, under every aggregator) |
| C4 | What is possible does not depend on the person | person moves | **holds for gates** (0 of 642,978); **fails in principle through the discard** (243 cells, 2,184 moves, 0 winners) |
| C5 | What is impossible is declared, not emergent | exclusions | **fails**: 9 of 9 emergent, 8 override a person-dependent preference |
| C6 | Everything read can matter to someone somewhere | dominance, live reads | **fails**: `anxious` provably idle for every person; one compatible candidate provably unwinnable; `respect` can decide only through anger |
| C7 | With the candidates fixed, the person decides | fixed-set moves | **holds** (6.1 %) |
| C8 | The same input gives the same answer | replay | **holds** (300 of 300 in the previous experiment; nothing here draws a random number) |

##### The joint constraint

| | Property | Current |
|---|---|---|
| J1 | Restatement invariance, split invariance and weight sensitivity cannot all hold for anonymous contributions. So **a reason must carry the identity of its evidence**, and support must aggregate over distinct evidence | the representation carries no evidence identity; the sum settles the question by treating every rule as independent evidence |

**What is not a property.** Invariance to proportional splitting (T6, T7) is not
required on its own. Under evidence identity, two halves of one rule are two
reasons reading identical evidence. They are a malformed rule set to be rejected,
not a rewrite to be survived. The current mechanism passes T6 and responds to
weight, and by the theorem that is exactly why it must fail R4.

#### 7. What the current mechanism violates

1. **R4 restatement**, the big one: 48.8 % of conclusions reversible by copying a line.
2. **J1**: rules carry no evidence identity, so R4 cannot be fixed by any choice of formula.
3. **R3 ties**: 25 cells decided by the alphabet or by rounding error.
4. **C4 and R5 through the discard**: the person can delete a candidate, and grouping terms into rules changes answers. On the frozen file it changed no winner; split one rule by term and it changes 469.
5. **C5**: nine intention-level impossibilities nobody declared, eight overriding preference.
6. **C6**: `anxious` is idle for every possible person, and one candidate is provably unwinnable.

#### 8. What any replacement must satisfy

**Hard requirements**, each with a test in this fixture that a replacement must pass:
R1, R2, R3 (report a tie or break it by a declared, recorded rule, never by a
label or by rounding), R4 (including near-duplicates), R5, R6, C1, C2, C3, C4
(nothing about the person removes a candidate), C7, C8, and J1.

**Audited properties**, measured and owned on every rule-file change:
C5 (possibility declared per want and circumstance), C6 (no idle reads, no
unwinnable candidates without saying so), and the forced share, which is
**35.7 %** now.

And it must keep what the generalization experiment proved: dozens of distinct
signatures across people nobody designed, no character-specific rule, and
blindness to state no rule reads.

#### 9. Local, or the architecture?

| Layer | Holds? | Evidence |
|---|---|---|
| 1 availability by want | yes | by construction; measured 2-3 intentions per want |
| 2 compatibility by circumstance | **yes** | 0 of 642,978 person moves changed it |
| 3 support by person, through `ScalerEval` | yes | bit-exact reconstruction; five traits, four of the five value swaps and both beliefs move it |
| 3/4 the discard | **no** | person-dependent exclusion; breaks R5 |
| 4 aggregation | **no** | R4; no alternative in the family satisfies the requirements |
| 5 selection | **no** | R3 |
| the rule representation | **no** | J1: no evidence identity; C5: no declared possibility |
| the authored content | partly | 35.7 % single-winner; `anxious` idle; these are properties of ten rules, not of the architecture |

**The problem is local.** It is in ranking (stages 4 and 5, and the discard at
the 3/4 boundary) and in what a rule is able to say about itself. The
decomposition into want, circumstance and person is not what fails. Every
measurement of it passed, including the strictest one: with the circumstance
fixed, no person was ever able to change what was possible.

It is not *purely* an aggregation fix, though. J1 means the formula cannot be
repaired without also changing the rule representation. A new formula over
today's rules would trade one invariant for another, as every member of the
family does.

#### 10. Only now: a direction for production, not implemented

The brief asks that this come last and that it not be built. It is a direction,
and every line of it is untested:

1. **Reasons have evidence identity.** For each (want, circumstance), an
   intention's support is one linear form over the distinct things it reads.
   Each thing read appears once per intention, and a validator rejects a rule
   set in which two reasons for the same intention read the same thing. In the
   frozen file that would flag `protect` reading `empathetic` twice (for
   `look_after` in company), and `assert_authority` reading `control` and
   `role_claim` twice. Restatement and proportional splitting then become
   unwritable, not merely harmless. That resolves J1 by removing the ambiguity,
   not by picking a formula. Under that constraint, and with 2 and 4 below, the
   sum would pass every test here. That is argued, not measured.
2. **No discard.** A negative term counts as negative. If the model ever needs
   the person to rule something out, that is declared as such.
3. **Possibility is declared** per want and circumstance, apart from reasons.
   Gates on reasons stay, meaning "this reason applies here". Whether plausibility
   should be a gate at all is a design question this experiment cannot settle.
4. **Ties are reported**, and broken by a declared rule written to the trace,
   in exact arithmetic or with a tolerance, never by a name.
5. **This fixture becomes the audit.** Transformations T1 to T11, the dominance
   bound and the live-read table run on every change to the rule file.

#### 11. What nobody predicted

- **48.8 %.** The predictions gave a count of duplication flips; they did not
  anticipate that half of all conclusions can be reversed by some single copy.
- **Lifting every gate changes exactly the cells the circumstance changes**
  (8,407 each), for the structural reason in section 3.
- **`respect` is live in exactly one group,** `restore_standing` alone, and there
  its rival can only win through anger. So in the sweep it decides nothing.
- **`honest` cancels in `get_food`.** Both rivals weigh it at 0.30, so a
  person's honesty can never choose between taking responsibility and admitting
  the theft.
- **A person's fifth and sixth values weigh nothing,** so swapping them changes
  nothing (0 of 21,870). This is a property of the shipped value weighting (a
  0.25 decay over six ranks), outside this experiment's scope, and left alone.
- **13 conclusions are decided by floating-point rounding,** beyond the 12 decided
  by the alphabet.
- **One of the nine exclusions is idle.** `prevent_argument` for
  `restore_standing` in company would win for nobody if its gate were lifted.

#### 12. Limitations

- **Most predictions were analytic.** They were derived from the rule file, so
  their holding mainly confirms the fixture. The empirical ones were ranges (A1,
  E3, E5, F3, F5, G3), and all held too.
- **The sweep never contains a feeling.** Three emotion reads are structurally
  live and untested. `assert_authority` in `restore_standing` alone is reachable
  only through one of them.
- **The sweep's value and belief rotations are coupled** through the parity of
  the profile index (`i mod 6` and `i mod 4`). For example, `control` ranked
  first never meets a `role_claim` belief, so some regions of person space are
  never visited.
- **Two circumstances.** `SituationCondition` has six fields, and only
  alone-or-company is exercised.
- **Single-attribute moves only.** Interactions between attributes are not
  measured.
- **Winners, not scores.** The theorem is about scores, and the table can only
  fail to contradict it.
- **The dominance bound is sound, not complete.** It relaxes value ranks to
  independent weights, so "dominated" is proven, while "not dominated" means only
  "not proven dominated".
- **Ten rules, six intentions.** The structural findings (stage separation,
  J1, the discard, the tie-break) are about the mechanism. The content findings
  (35.7 %, idle `anxious`) are about this file.
- **Psychological correctness is still not measured,** and is not claimed.

#### 13. Classification

Machine-readable in `classification.json`.

| | |
|---|---|
| **PROVEN** | The stages are separable and the reconstruction is exact (0 of 30,618). Compatibility never depends on the person (0 of 642,978). With the candidate set fixed, the person decides 6.1 % of contested moves. The sum's equivalence classes are {W, 2 x W/2, 4 x W/4} and {2W, W + W}. Restating one rule changes 19,992 cells (48.8 % of conclusions reversible), every one toward the copied intention and none outside where it applies. Splitting changes 0 of 306,180. No aggregator over anonymous contributions satisfies restatement, splitting and weight together (theorem, and 0 of 6 measured). The discard fires in 243 cells, changes 0 winners, and breaks term-grouping in 469. 25 real ties are settled by the alphabet (12) or by rounding (13). `anxious` is idle for every possible person. `prevent_argument` is unwinnable in `restore_standing` alone. Gates decide 27.5 % of cells, and every change a circumstance makes. 8 of 9 exclusions override a person-dependent preference |
| **PLAUSIBLE** | That evidence identity in the rule representation is the necessary repair. It follows from J1, but no design was built. That the authored gates mix preconditions with plausibility (a reading of the notes). That the failures are local to ranking and representation, and not the architecture |
| **UNPROVEN** | That a mechanism meeting every requirement in section 8 would still generalize as the current one does. That the 35.7 % single-winner share is a matter of authoring more rules rather than of the architecture. Whether plausibility belongs in a gate at all |
| **FAILED** | The current ranking as a causal mechanism: R3, R4, R5, C4 (through the discard), C5, C6, J1. Every aggregator in the family as a replacement: each gives up restatement, splitting, weight or monotonicity. Textual deduplication as a fix: defeated by a 0.99 copy |
| **UNKNOWN** | Anything involving feelings, memories or the ledger, which the sweep does not vary. Behaviour under a larger vocabulary or other circumstances. Whether any conclusion is psychologically right |

#### 14. Verdict

### MODIFY

The criteria were committed with the predictions. MODIFY required the violations
to sit in ranking and in how a rule represents its evidence, while gating stays
person-independent and preference decides a non-trivial share of contested
outcomes with the candidate set fixed. Both conditions hold: **0** of 642,978,
and **6.1 %**, against a REBUILD threshold of 1 %. The violations are exactly
where MODIFY puts them.

**Keep:** availability by want; compatibility by circumstance, as the only
thing a gate may read; support through the shipped `ScalerEval`; the absence of
any character-specific rule; exact replay.

**Modify:** how an intention's support is aggregated, together with what a rule
must declare about the evidence it reads, since J1 makes these one change and
not two. Also remove the discard, declare possibility instead of letting it
emerge, and stop ties being settled by names.

**Not REBUILD:** no stage below ranking failed. **Not ABANDON:** the reproduction
of the generalization experiment's numbers was exact.

Nothing has been implemented. The rule file is byte-identical, `Scripts/Core` is
untouched, and every alternative lives in the fixture and nowhere else.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter IntentionRankingExperimentTests`. It takes
about four minutes, most of it in the 65 rewritten rule sets.

**Suite: 424 tests, 422 pass, 2 fail**: the two regressions S1.4 left failing, unchanged
(the pacing gate, still 7 on Model A, and the emergent-moment fading check). The 414
before this experiment, plus its ten, is exactly 424. **Every generated document of S0
to S1.7 and of the nine earlier experiments regenerated with identical content.** The
only differences anywhere were the wall-clock seconds in the decision-sensitivity
results and one file that differed in line endings only.

---

## measurements.md

### Intention ranking: measurements

Generated by `IntentionRankingExperimentTests` against the frozen candidate rules, whose hash is checked at the start and the end of the run. The predictions, the transformations and the aggregators were committed before this fixture existed. There is no randomness anywhere.

#### 0. What is frozen, and whether taking the selector apart changed it

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 at the start of this run | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Expected | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Match | **yes** |
| Rules | 10 |
| Profiles | 2187 |
| Cells (profile x want x circumstance) | 30618 |

##### The stages reproduce the selector

This fixture runs stages 1 to 3 itself and aggregates what comes out, so that the aggregation can be swapped. Under the sum it must be the selector, and it is checked against `IntentionSelector.Form` on every cell rather than assumed.

| | Cells |
|---|---|
| Winner differs from `IntentionSelector.Form` | **0** of 30618 |
| Same winner, but its weight is not bit-for-bit equal | **0** |

##### The same sweep as the generalization experiment

| Published there | Reproduced here |
|---|---|
| 28.6 % of 30618 cells with one intention in the running | 28.6 % (8748) |
| 56 distinct signatures in company | 56 |
| 8407 cells changed by company arriving | 8407 |
| 2898 changes from cloning a rule, every seventh profile | in section A |

##### What each stage lets through, by want

Stage 1 depends on the want alone and stage 2 on the want and the circumstance, so this table is the whole of both. A rule in brackets is gated out.

| Want | Available (stage 1) | Compatible in company (stage 2) | Compatible alone (stage 2) |
|---|---|---|---|
| `avoid_exposure` | protect, prevent_argument, took_what_was_not_mine | protect `standing_between_them_and_it`; prevent_argument `not_making_a_scene_of_it`; took_what_was_not_mine `what_you_did_in_the_night` | protect (`standing_between_them_and_it`); prevent_argument (`not_making_a_scene_of_it`); took_what_was_not_mine `what_you_did_in_the_night` |
| `find_out` | assert_authority, take_responsibility, share_information | assert_authority `pulling_rank_needs_an_audience`; take_responsibility `somebody_has_to_do_it` + (`doing_it_where_nobody_is_watching`); share_information `so_that_they_know_too` | assert_authority (`pulling_rank_needs_an_audience`); take_responsibility `somebody_has_to_do_it` + `doing_it_where_nobody_is_watching`; share_information (`so_that_they_know_too`) |
| `get_food` | take_responsibility, took_what_was_not_mine | take_responsibility `somebody_has_to_do_it`; took_what_was_not_mine `what_you_did_in_the_night` | take_responsibility `somebody_has_to_do_it`; took_what_was_not_mine `what_you_did_in_the_night` |
| `guard_supplies` | assert_authority, take_responsibility, protect | assert_authority `pulling_rank_needs_an_audience` + `being_the_one_who_decides_it`; take_responsibility `somebody_has_to_do_it`; protect `keeping_it_off_them` | assert_authority (`pulling_rank_needs_an_audience`) + `being_the_one_who_decides_it`; take_responsibility `somebody_has_to_do_it`; protect `keeping_it_off_them` |
| `keep_peace` | share_information, protect, prevent_argument | share_information `so_that_they_know_too`; protect `standing_between_them_and_it`; prevent_argument `not_making_a_scene_of_it` + (`letting_it_go_for_now`) | share_information (`so_that_they_know_too`); protect (`standing_between_them_and_it`); prevent_argument (`not_making_a_scene_of_it`) + `letting_it_go_for_now` |
| `look_after` | share_information, protect, prevent_argument | share_information `so_that_they_know_too`; protect `standing_between_them_and_it` + `keeping_it_off_them`; prevent_argument `not_making_a_scene_of_it` | share_information (`so_that_they_know_too`); protect (`standing_between_them_and_it`) + `keeping_it_off_them`; prevent_argument (`not_making_a_scene_of_it`) |
| `restore_standing` | assert_authority, take_responsibility, prevent_argument | assert_authority `pulling_rank_needs_an_audience` + `being_the_one_who_decides_it`; take_responsibility `somebody_has_to_do_it` + (`doing_it_where_nobody_is_watching`); prevent_argument (`letting_it_go_for_now`) | assert_authority (`pulling_rank_needs_an_audience`) + `being_the_one_who_decides_it`; take_responsibility `somebody_has_to_do_it` + `doing_it_where_nobody_is_watching`; prevent_argument `letting_it_go_for_now` |

#### A. Duplicating one rule

Each rule in turn is added again under a new id: same person, same state, same circumstances, one extra line in the rule file that says nothing it did not already say. Counted through `IntentionSelector.Form` itself, on all 30618 cells.

| Rule duplicated | Intention | Cells where it is compatible | **Winner changed** | of all cells | of cells where compatible | toward its own intention | elsewhere | where it is not compatible |
|---|---|---|---|---|---|---|---|---|
| `pulling_rank_needs_an_audience` | `assert_authority` | 6561 | **1295** | 4.2 % | 19.7 % | 1295 | 0 | 0 |
| `being_the_one_who_decides_it` | `assert_authority` | 8748 | **1223** | 4.0 % | 14.0 % | 1223 | 0 | 0 |
| `somebody_has_to_do_it` | `take_responsibility` | 17496 | **5339** | 17.4 % | 30.5 % | 5339 | 0 | 0 |
| `doing_it_where_nobody_is_watching` | `take_responsibility` | 4374 | **0** | 0.0 % | 0.0 % | 0 | 0 | 0 |
| `so_that_they_know_too` | `share_information` | 6561 | **3685** | 12.0 % | 56.2 % | 3685 | 0 | 0 |
| `standing_between_them_and_it` | `protect` | 6561 | **2167** | 7.1 % | 33.0 % | 2167 | 0 | 0 |
| `keeping_it_off_them` | `protect` | 8748 | **1623** | 5.3 % | 18.6 % | 1623 | 0 | 0 |
| `not_making_a_scene_of_it` | `prevent_argument` | 6561 | **2279** | 7.4 % | 34.7 % | 2279 | 0 | 0 |
| `letting_it_go_for_now` | `prevent_argument` | 4374 | **41** | 0.1 % | 0.9 % | 41 | 0 | 0 |
| `what_you_did_in_the_night` | `took_what_was_not_mine` | 8748 | **2340** | 7.6 % | 26.7 % | 2340 | 0 | 0 |

**Over 30618 cells and 10 rules, duplicating one rule changed the intention 19992 times.** On every seventh profile, the subset the generalization experiment used, it changed it 2898 times (published: 2898).

##### By want

| Want | Changes from duplicating some one rule, summed over the ten |
|---|---|
| `avoid_exposure` | 2309 |
| `find_out` | 3524 |
| `get_food` | 3402 |
| `guard_supplies` | 4001 |
| `keep_peace` | 2795 |
| `look_after` | 2446 |
| `restore_standing` | 1515 |

##### How many conclusions one copied line can reverse

| Rules whose duplication alone reverses the cell | Cells |
|---|---|
| 0 | 15683 |
| 1 | 10095 |
| 2 | 4623 |
| 3 | 217 |

**14935 of 30618 cells (48.8 %) have a conclusion that copying a single existing rule, and changing nothing about the person, reverses.**

#### B. Splitting one rule

Each rule in turn is replaced by equal parts that together weigh what it weighed. Counted through `IntentionSelector.Form`, on all 30618 cells. This is the regression invariant the generalization experiment found, and it is asserted.

| Rule split | Intention | Changed by two halves | Changed by four quarters |
|---|---|---|---|
| `pulling_rank_needs_an_audience` | `assert_authority` | 0 | 0 |
| `being_the_one_who_decides_it` | `assert_authority` | 0 | 0 |
| `somebody_has_to_do_it` | `take_responsibility` | 0 | 0 |
| `doing_it_where_nobody_is_watching` | `take_responsibility` | 0 | 0 |
| `so_that_they_know_too` | `share_information` | 0 | 0 |
| `standing_between_them_and_it` | `protect` | 0 | 0 |
| `keeping_it_off_them` | `protect` | 0 | 0 |
| `not_making_a_scene_of_it` | `prevent_argument` | 0 | 0 |
| `letting_it_go_for_now` | `prevent_argument` | 0 | 0 |
| `what_you_did_in_the_night` | `took_what_was_not_mine` | 0 | 0 |

**Over 306180 (rule, cell) pairs: splitting into halves changed 0; into quarters, 0.**

#### C. Weight against representation

Five ways of writing one rule: as it is (**W**), as two rules at half weight (**2 x W/2**), as four at a quarter (**4 x W/4**), as one rule at double weight (**2W**), and as itself twice (**W + W**). The first three carry the same total weight, the last two the same doubled weight. Cells in which two representations reach different intentions, under the current mechanism:

| Rule | W vs 2 x W/2 | W vs 4 x W/4 | W vs 2W | W vs W + W | 2 x W/2 vs 4 x W/4 | 2 x W/2 vs 2W | 2 x W/2 vs W + W | 4 x W/4 vs 2W | 4 x W/4 vs W + W | 2W vs W + W |
|---|---|---|---|---|---|---|---|---|---|---|
| `pulling_rank_needs_an_audience` | 0 | 0 | 1295 | 1295 | 0 | 1295 | 1295 | 1295 | 1295 | 0 |
| `being_the_one_who_decides_it` | 0 | 0 | 1223 | 1223 | 0 | 1223 | 1223 | 1223 | 1223 | 0 |
| `somebody_has_to_do_it` | 0 | 0 | 5339 | 5339 | 0 | 5339 | 5339 | 5339 | 5339 | 0 |
| `doing_it_where_nobody_is_watching` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `so_that_they_know_too` | 0 | 0 | 3685 | 3685 | 0 | 3685 | 3685 | 3685 | 3685 | 0 |
| `standing_between_them_and_it` | 0 | 0 | 2167 | 2167 | 0 | 2167 | 2167 | 2167 | 2167 | 0 |
| `keeping_it_off_them` | 0 | 0 | 1623 | 1623 | 0 | 1623 | 1623 | 1623 | 1623 | 0 |
| `not_making_a_scene_of_it` | 0 | 0 | 2279 | 2279 | 0 | 2279 | 2279 | 2279 | 2279 | 0 |
| `letting_it_go_for_now` | 0 | 0 | 41 | 41 | 0 | 41 | 41 | 41 | 41 | 0 |
| `what_you_did_in_the_night` | 0 | 0 | 2340 | 2340 | 0 | 2340 | 2340 | 2340 | 2340 | 0 |
| **all ten** | **0** | **0** | **19992** | **19992** | **0** | **19992** | **19992** | **19992** | **19992** | **0** |

##### Which representations each aggregator treats as the same

Two representations are the same to an aggregator if they never reach different intentions, for any of the ten rules, in any cell. The classes:

| Aggregator | Equivalence classes | W vs 2 x W/2 | W vs 4 x W/4 | W vs 2W | W vs W + W | 2 x W/2 vs 4 x W/4 | 2 x W/2 vs 2W | 2 x W/2 vs W + W | 4 x W/4 vs 2W | 4 x W/4 vs W + W | 2W vs W + W |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sum | {W, 2 x W/2, 4 x W/4} {2W, W + W} | 0 | 0 | 19992 | 19992 | 0 | 19992 | 19992 | 19992 | 19992 | 0 |
| max | {W, W + W} {2 x W/2} {4 x W/4} {2W} | 16721 | 19647 | 24346 | 0 | 2926 | 41067 | 16721 | 43993 | 19647 | 24346 |
| mean | {W} {2 x W/2} {4 x W/4} {2W} {W + W} | 19615 | 25290 | 26128 | 1473 | 5675 | 45743 | 19450 | 51418 | 25125 | 26293 |
| normalized max | {W, 2 x W/2, 4 x W/4, 2W, W + W} | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| noisy-OR | {W, 2W} {2 x W/2, W + W} {4 x W/4} | 17592 | 31286 | 0 | 17592 | 13694 | 17592 | 0 | 31286 | 13694 | 17592 |
| deduplicated sum | {W, W + W} {2 x W/2} {4 x W/4} {2W} | 13743 | 18567 | 19992 | 0 | 4824 | 33735 | 13743 | 38559 | 18567 | 19992 |

#### D. How many candidates, and how much the person can matter with each number

The number of **compatible** intentions depends on the want and the circumstance only, so it is a property of the 14 (want, circumstance) groups. The number of **supported** ones (a positive contribution) can be smaller, and depends on the person. Sensitivity is the share of the 21 single-attribute moves of a profile (section F) that change its intention, pooled over all 2187 profiles.

| Group | K compatible | Compatible | Supported, min-max | Winners across the sweep | Entropy (bits) | Sensitivity |
|---|---|---|---|---|---|---|
| `avoid_exposure` in company | 3 | protect, prevent_argument, took_what_was_not_mine | 2-3 | took_what_was_not_mine 51.4 %, protect 34.2 %, prevent_argument 14.4 % | 1.426 | 10.0 % |
| `avoid_exposure` alone | 1 | took_what_was_not_mine | 1-1 | took_what_was_not_mine 100.0 % | 0.000 | 0.0 % |
| `find_out` in company | 3 | assert_authority, take_responsibility, share_information | 3-3 | assert_authority 56.6 %, take_responsibility 29.9 %, share_information 13.5 % | 1.376 | 10.9 % |
| `find_out` alone | 1 | take_responsibility | 1-1 | take_responsibility 100.0 % | 0.000 | 0.0 % |
| `get_food` in company | 2 | take_responsibility, took_what_was_not_mine | 2-2 | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | 0.991 | 4.9 % |
| `get_food` alone | 2 | take_responsibility, took_what_was_not_mine | 2-2 | take_responsibility 55.6 %, took_what_was_not_mine 44.4 % | 0.991 | 4.9 % |
| `guard_supplies` in company | 3 | assert_authority, take_responsibility, protect | 3-3 | assert_authority 80.6 %, take_responsibility 18.9 %, protect 0.5 % | 0.746 | 4.0 % |
| `guard_supplies` alone | 3 | assert_authority, take_responsibility, protect | 3-3 | take_responsibility 76.6 %, protect 21.5 %, assert_authority 1.8 % | 0.877 | 7.6 % |
| `keep_peace` in company | 3 | share_information, protect, prevent_argument | 2-3 | share_information 47.8 %, protect 44.0 %, prevent_argument 8.2 % | 1.326 | 9.4 % |
| `keep_peace` alone | 1 | prevent_argument | 1-1 | prevent_argument 100.0 % | 0.000 | 0.0 % |
| `look_after` in company | 3 | share_information, protect, prevent_argument | 2-3 | protect 86.0 %, share_information 12.8 %, prevent_argument 1.2 % | 0.644 | 5.6 % |
| `look_after` alone | 1 | protect | 1-1 | protect 100.0 % | 0.000 | 0.0 % |
| `restore_standing` in company | 2 | assert_authority, take_responsibility | 2-2 | assert_authority 81.1 %, take_responsibility 18.9 % | 0.699 | 3.5 % |
| `restore_standing` alone | 3 | assert_authority, take_responsibility, prevent_argument | 3-3 | take_responsibility 100.0 % | 0.000 | 0.0 % |

##### By number of compatible candidates

| K | Groups | Cells | Share of cells | Groups with one winner across the whole sweep | Mean winners per group | Pooled sensitivity | Least and most sensitive group |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 8748 | 28.6 % | 4 | 1.000 | 0.0 % | `avoid_exposure` alone 0.0 %; `avoid_exposure` alone 0.0 % |
| 2 | 3 | 6561 | 21.4 % | 0 | 2.000 | 4.4 % | `restore_standing` in company 3.5 %; `get_food` in company 4.9 % |
| 3 | 7 | 15309 | 50.0 % | 1 | 2.714 | 6.8 % | `restore_standing` alone 0.0 %; `find_out` in company 10.9 % |

**Cells in a group where every one of the 2187 profiles forms the same intention: 10935 (35.7 %)**, in `avoid_exposure` alone, `find_out` alone, `keep_peace` alone, `look_after` alone, `restore_standing` alone.

##### Which compatible intentions can win at all

For every group with two or more compatible intentions, each intention is **witnessed** if it wins for some profile in the sweep, **dominated** if some rival outscores it for every possible person (a bound over the whole unit box, with value ranks relaxed to independent weights, which can only widen it), or neither.

| | (group, intention) pairs |
|---|---|
| Witnessed | 25 |
| Dominated, so never able to win for anybody | 1 |
| Neither: could win, never did in the sweep | 1 |
| Total | 27 |

| Group | Intention | Status |
|---|---|---|
| `restore_standing` alone | assert_authority | not dominated, never won in the sweep |
| `restore_standing` alone | prevent_argument | **dominated** by take_responsibility: its best margin over every possible person is -0.070 |

##### Which things a rule reads can decide anything

A thing a rule reads can only change a winner in a group where at least two intentions that are not dominated weigh it differently. If every live rival weighs it the same, it cancels; if only a dominated or a lone intention reads it, it is idle. Measured changes are from the single-attribute moves of section F, pooled over all groups.

| Read | Groups where it can decide | Moves of it that changed an intention |
|---|---|---|
| belief answerable_for | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | 5774 of 30618 |
| belief role_claim | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | 2182 of 30618 |
| emotion anger | 4: `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | not varied by the sweep |
| emotion anxiety | 3: `avoid_exposure` in company, `keep_peace` in company, `look_after` in company | not varied by the sweep |
| emotion shame | 3: `avoid_exposure` in company, `get_food` in company, `get_food` alone | not varied by the sweep |
| trait anxious | **none** | 0 of 61236 |
| trait cautious | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | 2801 of 61236 |
| trait dominant | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `keep_peace` in company, `look_after` in company, `restore_standing` in company | 2675 of 61236 |
| trait empathetic | 5: `avoid_exposure` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | 4291 of 61236 |
| trait honest | 8: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | 5230 of 61236 |
| trait proud | 4: `find_out` in company, `guard_supplies` in company, `restore_standing` in company, `restore_standing` alone | 808 of 61236 |
| value closeness | 6: `avoid_exposure` in company, `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company | no single-value move exists: values weigh by rank |
| value control | 5: `find_out` in company, `guard_supplies` in company, `guard_supplies` alone, `restore_standing` in company, `restore_standing` alone | no single-value move exists: values weigh by rank |
| value fairness | 6: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `keep_peace` in company, `look_after` in company | no single-value move exists: values weigh by rank |
| value family_safety | 10: `avoid_exposure` in company, `find_out` in company, `get_food` in company, `get_food` alone, `guard_supplies` in company, `guard_supplies` alone, `keep_peace` in company, `look_after` in company, `restore_standing` in company, `restore_standing` alone | no single-value move exists: values weigh by rank |
| value respect | 1: `restore_standing` alone | no single-value move exists: values weigh by rank |

#### E. Gating against preference

A gate is a rule's `when`. It can only name circumstances. This section asks what a gate does to an intention the person would otherwise have preferred.

##### The gates, and what they exclude

| Rule | Intention | Gate | Note, as authored | Gated out in | There, the intention is |
|---|---|---|---|---|---|
| `pulling_rank_needs_an_audience` | assert_authority | others present >= 1 | Nobody pulls rank in an empty room. The want is the same; what makes it authority rather than housekeeping is that somebody is there to see it. | `find_out` alone<br>`guard_supplies` alone<br>`restore_standing` alone | **excluded**<br>kept by `being_the_one_who_decides_it`<br>kept by `being_the_one_who_decides_it` |
| `doing_it_where_nobody_is_watching` | take_responsibility | alone | Proving it to yourself rather than to them. Only alone, and strongest in the proud, who mind about being right more than about being seen to be. | `find_out` in company<br>`restore_standing` in company | kept by `somebody_has_to_do_it`<br>kept by `somebody_has_to_do_it` |
| `so_that_they_know_too` | share_information | others present >= 1 | Finding out on behalf of the room rather than for yourself. Needs somebody to tell. | `find_out` alone<br>`keep_peace` alone<br>`look_after` alone | **excluded**<br>**excluded**<br>**excluded** |
| `standing_between_them_and_it` | protect | others present >= 1 | Putting yourself in the way of something, which takes somebody to put yourself in front of. | `avoid_exposure` alone<br>`keep_peace` alone<br>`look_after` alone | **excluded**<br>**excluded**<br>kept by `keeping_it_off_them` |
| `not_making_a_scene_of_it` | prevent_argument | others present >= 1 | Defusing. Needs a scene to not make. The dominant factor is negative on purpose: a dominant person does not defuse, they settle it. | `avoid_exposure` alone<br>`keep_peace` alone<br>`look_after` alone | **excluded**<br>kept by `letting_it_go_for_now`<br>**excluded** |
| `letting_it_go_for_now` | prevent_argument | alone | Choosing not to have it out, with nobody there to have it out with yet. | `keep_peace` in company<br>`restore_standing` in company | kept by `not_making_a_scene_of_it`<br>**excluded** |

##### Intentions a gate excludes outright

For each available intention that no rule leaves compatible, its own rules' gates are lifted, in memory, and nothing else. Its would-be support is what the person would give it; the last column is how often that would have won.

| Group | Excluded intention | Would-be support: min, median, max | Would have won, of 2187 profiles | Reading |
|---|---|---|---|---|
| `avoid_exposure` alone | protect | 0.210, 0.490, 0.840 | 973 (44.5 %) | **overrides a preference that depends on the person** |
| `avoid_exposure` alone | prevent_argument | 0.000, 0.323, 0.710 | 629 (28.8 %) | **overrides a preference that depends on the person** |
| `find_out` alone | assert_authority | 0.190, 0.680, 1.113 | 315 (14.4 %) | **overrides a preference that depends on the person** |
| `find_out` alone | share_information | 0.255, 0.520, 0.860 | 41 (1.9 %) | **overrides a preference that depends on the person** |
| `keep_peace` alone | share_information | 0.255, 0.520, 0.860 | 1944 (88.9 %) | **overrides a preference that depends on the person** |
| `keep_peace` alone | protect | 0.210, 0.490, 0.840 | 1782 (81.5 %) | **overrides a preference that depends on the person** |
| `look_after` alone | share_information | 0.255, 0.520, 0.860 | 1820 (83.2 %) | **overrides a preference that depends on the person** |
| `look_after` alone | prevent_argument | 0.000, 0.323, 0.710 | 915 (41.8 %) | **overrides a preference that depends on the person** |
| `restore_standing` in company | prevent_argument | 0.148, 0.305, 0.463 | 0 (0.0 %) | idle: the gate decides nothing |

**9 intention-level exclusions; in 8 of them the gate overrides a preference that would have gone one way for some people and the other way for others.**

##### Reasons a gate removes while the intention stays available

| Group | Rule gated out | Intention kept by | Winner changed by lifting only this gate |
|---|---|---|---|
| `guard_supplies` alone | `pulling_rank_needs_an_audience` | `being_the_one_who_decides_it` | 1722 (78.7 %) |
| `restore_standing` alone | `pulling_rank_needs_an_audience` | `being_the_one_who_decides_it` | 1000 (45.7 %) |
| `find_out` in company | `doing_it_where_nobody_is_watching` | `somebody_has_to_do_it` | 1196 (54.7 %) |
| `restore_standing` in company | `doing_it_where_nobody_is_watching` | `somebody_has_to_do_it` | 774 (35.4 %) |
| `look_after` alone | `standing_between_them_and_it` | `keeping_it_off_them` | 0 (0.0 %) |
| `keep_peace` alone | `not_making_a_scene_of_it` | `letting_it_go_for_now` | 0 (0.0 %) |
| `keep_peace` in company | `letting_it_go_for_now` | `not_making_a_scene_of_it` | 937 (42.8 %) |

##### Every gate lifted at once

| Want | Changed in company | Changed alone |
|---|---|---|
| `avoid_exposure` | 0.0 % | 48.6 % |
| `find_out` | 54.7 % | 15.5 % |
| `get_food` | 0.0 % | 0.0 % |
| `guard_supplies` | 0.0 % | 78.7 % |
| `keep_peace` | 42.8 % | 49.0 % |
| `look_after` | 0.0 % | 14.0 % |
| `restore_standing` | 35.4 % | 45.7 % |
| **all** | **19.0 %** | **35.9 %** |

**With every gate lifted, 8407 of 30618 cells (27.5 %) form a different intention.** In those cells the circumstance, through a gate, is what decided.

##### The discard: where a person removes a candidate

The selector throws away a contribution at or below zero instead of counting it. That is the one place in the mechanism where something about the person, rather than the circumstance, takes a compatible candidate out of the running.

| | |
|---|---|
| Cells with a compatible contribution at or below zero | **243** |
| Profiles | 81 |
| Groups | `avoid_exposure` in company, `keep_peace` in company, `look_after` in company |
| Rules | `not_making_a_scene_of_it` down to -0.010 |
| Cells where it shrinks the supported set below the compatible set | 243 |
| Cells where counting it instead would change the winner | **0** |

#### F. Preference, with the candidate set held fixed

The circumstance is held, so the compatible set cannot move. One attribute of the person moves: each trait to each of its other two sweep levels, each adjacent pair of value ranks swapped, each belief toggled. Where the supported set is also identical, only preference is left to change the answer.

| | Pairs |
|---|---|
| (profile, move, want, circumstance) pairs | 642978 |
| Compatible set changed by moving the person | **0** |
| Supported set changed | 2184, of which explained by the discard: 2184 |
| Supported set identical | 640794 |

##### By number of compatible candidates, candidate set identical

| K | Pairs with the candidate set identical | Winner changed | Share |
|---|---|---|---|
| 1 | 183708 | 0 | 0.0 % |
| 2 | 137781 | 6115 | 4.4 % |
| 3 | 319305 | 21836 | 6.8 % |

**With two or more candidates and the candidate set identical, moving one attribute of the person changed the intention in 27951 of 457086 pairs (6.1 %).** That is preference, separated from candidate generation.

##### By attribute, candidate set identical, K >= 2

| Attribute moved | Pairs | Winner changed | Share |
|---|---|---|---|
| trait anxious | 43740 | 0 | 0.0 % |
| trait cautious | 42768 | 2801 | 6.5 % |
| trait dominant | 42768 | 2675 | 6.3 % |
| trait empathetic | 43740 | 4291 | 9.8 % |
| trait honest | 43740 | 5230 | 12.0 % |
| trait impulsive | 43740 | 0 | 0.0 % |
| trait proud | 43740 | 808 | 1.8 % |
| value ranks 1 <-> 2 | 21870 | 1133 | 5.2 % |
| value ranks 2 <-> 3 | 21870 | 1106 | 5.1 % |
| value ranks 3 <-> 4 | 21870 | 1008 | 4.6 % |
| value ranks 4 <-> 5 | 21630 | 943 | 4.4 % |
| value ranks 5 <-> 6 | 21870 | 0 | 0.0 % |
| belief role_claim | 21870 | 2182 | 10.0 % |
| belief answerable_for | 21870 | 5774 | 26.4 % |

##### One of each, as it happened

The first profile in each contested group where one move changed the intention with the candidate set identical.

| Group | Profile | Move | Before | After |
|---|---|---|---|---|
| `keep_peace` in company | p0 | cautious 0.150 -> 0.500 | share_information 0.455 over prevent_argument 0.390 | prevent_argument 0.513 over share_information 0.455 |
| `guard_supplies` alone | p0 | cautious 0.150 -> 0.850 | protect 0.333 over take_responsibility 0.255 | take_responsibility 0.395 over protect 0.333 |
| `look_after` in company | p0 | cautious 0.150 -> 0.850 | protect 0.543 over share_information 0.455 | prevent_argument 0.635 over protect 0.543 |
| `find_out` in company | p0 | dominant 0.150 -> 0.500 | share_information 0.455 over assert_authority 0.365 | assert_authority 0.523 over share_information 0.455 |
| `avoid_exposure` in company | p0 | empathetic 0.150 -> 0.850 | prevent_argument 0.390 over protect 0.210 | protect 0.490 over prevent_argument 0.390 |
| `guard_supplies` in company | p0 | empathetic 0.150 -> 0.850 | assert_authority 0.540 over protect 0.333 | protect 0.543 over assert_authority 0.540 |
| `get_food` in company | p0 | answerable_for taken up at 0.900 | take_responsibility 0.255 over took_what_was_not_mine 0.158 | took_what_was_not_mine 0.698 over take_responsibility 0.255 |
| `get_food` alone | p0 | answerable_for taken up at 0.900 | take_responsibility 0.255 over took_what_was_not_mine 0.158 | took_what_was_not_mine 0.698 over take_responsibility 0.255 |
| `restore_standing` in company | p3 | honest 0.150 -> 0.500 | assert_authority 0.680 over take_responsibility 0.588 | take_responsibility 0.693 over assert_authority 0.680 |

##### For contrast: the circumstance moves and the person does not

The same person, alone and then with three others in the room. Each change is classified by what made it:

| Cause | Changes | Share |
|---|---|---|
| **Availability**: the new winner is an intention no rule offers alone | 4911 | 58.4 % |
| Lost availability: the old winner is not offered in company | 0 | 0.0 % |
| **A reason gated in or out**: both intentions are available in both, and a gated rule re-weighted them | 3496 | 41.6 % |
| Total | 8407 | |

#### G. The aggregation family, over the same contributions

Stages 1 to 3 are held; only the way an intention's contributions become its score changes. None of these is proposed. Each is here to show which invariants a way of aggregating keeps and which it gives up, and none has a parameter that could be tuned toward an answer that looks human.

| Aggregator | Score of an intention |
|---|---|
| **sum** | the sum of its positive contributions; the current mechanism |
| **max** | its largest contribution |
| **mean** | the mean of its positive contributions |
| **normalized max** | the largest contribution / that rule's own attainable maximum |
| **noisy-OR** | 1 - product(1 - normalized contribution) |
| **deduplicated sum** | the sum, counting rules identical in all but their id once |

| Aggregator | Cells whose winner differs from the sum | Distinct signatures in company | `look_after -> protect` in company | Groups with one winner across the sweep | Exact ties | Ties within 1e-9 |
|---|---|---|---|---|---|---|
| sum | 0 (0.0 %) | 56 | 86.0 % | 5 of 14 | 12 | 25 |
| max | 1672 (5.5 %) | 53 | 45.9 % | 4 of 14 | 12 | 61 |
| mean | 3464 (11.3 %) | 82 | 28.9 % | 4 of 14 | 12 | 25 |
| normalized max | 6467 (21.1 %) | 86 | 54.9 % | 4 of 14 | 0 | 5 |
| noisy-OR | 4250 (13.9 %) | 100 | 84.2 % | 4 of 14 | 0 | 5 |
| deduplicated sum | 0 (0.0 %) | 56 | 86.0 % | 5 of 14 | 12 | 25 |

##### Which traits can move an intention, under each

Share of single-trait moves, in all groups, that change the intention. Gating is the same for all six, so the 28.6 % of cells with one candidate are the same for all six too.

| Aggregator | `anxious` | `cautious` | `dominant` | `empathetic` | `honest` | `impulsive` | `proud` | `role_claim` | `answerable_for` |
|---|---|---|---|---|---|---|---|---|---|
| sum | **0** | 4.6 % | 4.4 % | 7.0 % | 8.5 % | **0** | 1.3 % | 7.1 % | 18.9 % |
| max | 0.2 % | 6.7 % | 7.2 % | 7.2 % | 11.9 % | **0** | 2.2 % | 7.7 % | 18.9 % |
| mean | 0.5 % | 7.6 % | 6.6 % | 8.4 % | 14.0 % | **0** | 2.5 % | 10.6 % | 18.9 % |
| normalized max | 2.5 % | 13.4 % | 9.5 % | 8.9 % | 14.7 % | **0** | 3.6 % | 6.8 % | 13.0 % |
| noisy-OR | 1.0 % | 10.3 % | 7.7 % | 7.9 % | 11.8 % | **0** | 1.9 % | 7.2 % | 13.0 % |
| deduplicated sum | **0** | 4.6 % | 4.4 % | 7.0 % | 8.5 % | **0** | 1.3 % | 7.1 % | 18.9 % |

#### H. Representation invariance

Each transformation rewrites the rule file without changing anything about any person. The count is of cells, over all 30618, whose intention changed; for a per-rule transformation it is summed over the ten rules. In brackets, how many of those changes were in a cell where the top two were within 1e-9 of each other before or after: a tie in the real numbers, decided by the alphabet or by rounding.

| | Transformation | Should it preserve the conclusion? | sum | max | mean | normalized max | noisy-OR | deduplicated sum |
|---|---|---|---|---|---|---|---|---|
| T1 | reverse the order of the rules | yes | 0 | 0 | 0 | 0 | 0 | 0 |
| T2 | give every rule a new id | yes | 0 | 0 | 0 | 0 | 0 | 0 |
| T3 | rename the intentions (reverse their alphabetical order) | yes: a label is not psychology | **12** (12) | **12** (12) | **12** (12) | 0 | 0 | **12** (12) |
| T4 | duplicate one rule | yes: an exact copy says nothing new about the person | **19992** (136) | 0 | **1473** (27) | 0 | **17592** (18) | 0 |
| T5 | near-duplicate one rule (x 0.99) | yes: behaves as T4 | **19844** (47) | 0 | **1557** (25) | 0 | **17592** (18) | **19844** (47) |
| T6 | split one rule into two halves | depends on what a rule is | 0 | **16721** (108) | **19615** (54) | 0 | **17592** (18) | **13743** (72) |
| T7 | split one rule into four quarters | depends on what a rule is | 0 | **19647** (222) | **25290** (168) | 0 | **31286** (10) | **18567** (168) |
| T8 | split one rule by term | yes: the same reasons, grouped differently | **469** | **16298** (93) | **24471** (168) | **41802** (10) | **39533** (10) | **469** |
| T9 | scale one rule x 2 (2W) | **no**: a stronger reason must be able to win | **19992** (136) | **24346** (157) | **26128** (144) | 0 | 0 | **19992** (136) |
| T10 | merge co-compatible rules into one per want, intention and circumstance | yes: the same reasons, grouped differently | 0 | **1672** (10) | **3464** | **1533** | **3802** | 0 |
| T11 | duplicate every rule | yes: nothing is relatively stronger | 0 | 0 | 0 | 0 | 0 | 0 |

##### Preserved or violated, counting only changes that are not ties

| | sum | max | mean | normalized max | noisy-OR | deduplicated sum |
|---|---|---|---|---|---|---|
| T1 | P | P | P | P | P | P |
| T2 | P | P | P | P | P | P |
| T3 | P | P | P | P | P | P |
| T4 | **V** | P | **V** | P | **V** | P |
| T5 | **V** | P | **V** | P | **V** | **V** |
| T6 | P | **V** | **V** | P | **V** | **V** |
| T7 | P | **V** | **V** | P | **V** | **V** |
| T8 | **V** | **V** | **V** | **V** | **V** | **V** |
| T9 | **V** | **V** | **V** | P | P | **V** |
| T10 | P | **V** | **V** | **V** | **V** | P |
| T11 | P | P | P | P | P | P |

##### Monotonicity: where a duplicate sends the answer

Adding a copy of a reason for X should never make X lose. Changes from T4, by where they went:

| Aggregator | Toward the duplicated rule's intention | **Away from it** | Between two others | In a cell where the rule is not compatible |
|---|---|---|---|---|
| sum | 19992 | 0 | 0 | 0 |
| max | 0 | 0 | 0 | 0 |
| mean | 654 | **819** | 0 | 0 |
| normalized max | 0 | 0 | 0 | 0 |
| noisy-OR | 17592 | 0 | 0 | 0 |
| deduplicated sum | 0 | 0 | 0 | 0 |

##### Splitting by term, rule by rule, under the sum

| Rule | Changed | At a tie |
|---|---|---|
| `pulling_rank_needs_an_audience` | 0 | 0 |
| `being_the_one_who_decides_it` | 0 | 0 |
| `somebody_has_to_do_it` | 0 | 0 |
| `doing_it_where_nobody_is_watching` | 0 | 0 |
| `so_that_they_know_too` | 0 | 0 |
| `standing_between_them_and_it` | 0 | 0 |
| `keeping_it_off_them` | 0 | 0 |
| `not_making_a_scene_of_it` | 469 | 0 |
| `letting_it_go_for_now` | 0 | 0 |
| `what_you_did_in_the_night` | 0 | 0 |

##### The impossibility, checked

No aggregator of anonymous contributions can be invariant to duplication (T4) and to proportional splitting (T6) and still respond to weight (T9). Aggregators here that show all three: **none**.

| Aggregator | T4 duplicate | T6 split | T9 scale x 2 | Gives up |
|---|---|---|---|---|
| sum | V | P | responds | duplication |
| max | P | V | responds | splitting |
| mean | V | V | responds | duplication, splitting |
| normalized max | P | P | no response | **weight** |
| noisy-OR | V | V | no response | duplication, splitting, **weight** |
| deduplicated sum | P | V | responds | splitting |

#### Z. The frozen file after the whole run

**sha256: `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` — unchanged.** Every rewritten rule set above was built in memory.

---

## predictions.md

### Intention ranking: predictions

Written and committed **before the fixture that measures any of this existed**.
Everything below is derived by reading the frozen rule file and the published
numbers of the generalization experiment. Nothing was simulated to write it. Kept
as written; where a prediction is wrong, `results.md` says so.

#### What this experiment is for

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

#### What is frozen

| | |
|---|---|
| File | `Assets/_Project/Data/Experiments/intentions.json` |
| sha256 | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` |
| Rules | 10, unedited |
| Selector | `IntentionSelector.Form`, unedited |
| Production | nothing under `Scripts/Core`, no shipped data, no shipped weight |

Every alternative rule set is built in memory. Every alternative aggregator lives
in the new fixture and nowhere else. The file is hashed at the start and the end.

#### The five stages, defined before measuring them

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

#### The cells

| | |
|---|---|
| Profiles | the 2,187 of the generalization sweep, rebuilt identically |
| Wants | 7 |
| Circumstances | in company (three others present) and alone |
| **Cells** | **30,618** = 2,187 x 7 x 2. Every test below runs on all of them unless it says otherwise |
| Single-attribute perturbations of a person | 21: each of 7 traits moved to each of its other two sweep levels (14), each adjacent pair of value ranks swapped (5), each of the two beliefs toggled between absent and its sweep confidence (2) |

#### The transformations, fixed in advance

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

#### The aggregators, fixed in advance

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

#### Predictions

##### A. Duplication

| # | Prediction | Falsified if |
|---|---|---|
| A1 | Under the current sum, duplicating a rule changes the winner in **19,000 to 21,500** of the 306,180 (rule, cell) pairs. The published figure was 2,898 on every seventh profile; the full sweep is seven times larger | outside that range |
| A2 | **Every** change is toward the duplicated rule's intention | any change goes elsewhere |
| A3 | **No** change occurs in a cell where the duplicated rule is not compatible | any does |
| A4 | Duplicating `doing_it_where_nobody_is_watching` changes **0** cells even on the full sweep: where it is compatible, its intention is either the only one in the running or already wins every time | it changes any |

##### B. Splitting

| # | Prediction | Falsified if |
|---|---|---|
| B1 | Splitting any rule into two halves changes **0** of 306,180, under the current mechanism. This is the regression invariant, and it is asserted | any change |
| B2 | Splitting into four quarters also changes **0** | any change. Floating point could in principle move an exact tie; I expect it not to |

##### C. Weight against representation

For every rule: one rule at W, two at W/2, four at W/4, one at 2W, and two at W.

| # | Prediction | Falsified if |
|---|---|---|
| C1 | Under the sum there are exactly **two** equivalence classes: {W, 2 x W/2, 4 x W/4} and {2W, W + W}. Cell for cell, 2W and the duplicate agree **everywhere** | any cell where 2W and W + W disagree, or where the splits differ from W |
| C2 | So the one representation change the mechanism treats as meaningful is a change of **total weight per intention**. It cannot tell "one stronger reason" from "the same reason twice" | C1 fails |

##### D. Candidate sets

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

##### E. Gating against preference

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

##### F. Preference with the candidate set held fixed

| # | Prediction | Falsified if |
|---|---|---|
| F1 | With the circumstance fixed, person perturbations leave the compatible set identical in **every** pair | any exception |
| F2 | They leave the supported set identical except where the discard in E6 moves | any other exception |
| F3 | With the candidate set identical, person state changes the winner in a **non-zero** share of K >= 2 pairs. This is preference, separated from candidate generation | zero |
| F4 | `impulsive`, read by no rule, changes **0** pairs. (There is no pure `autonomy` perturbation: values weigh by rank, so moving one value moves another) | any |
| F5 | Of the company-arrival changes (8,407 in the published measurement), **50 % to 65 %** are availability: the new winner is an intention no rule offers alone. The rest are a reason-level gate re-weighting an intention available in both | outside |

##### G. The aggregation family

| # | Prediction | Falsified if |
|---|---|---|
| G1 | The six aggregators disagree with the sum in some cells. Which is closer to human is **not** measured and not claimed | - |
| G2 | Under **max**, `anxious` becomes able to change outcomes: `letting_it_go_for_now` can beat the larger of `take_responsibility`'s two rules alone, where it can never beat their sum. So the deafness is a property of adding, not of the rule | `anxious` changes nothing under max |
| G3 | Under **max**, `look_after -> protect` **in company** falls below 60 %, from 86.0 % under the sum. (Alone it is the only candidate, so it stays at 100 % under every aggregator) | at or above 60 % |
| G4 | Gating is shared by every aggregator, so the forced share of D1 is identical for all six | any difference |

##### H. Representation invariance

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

##### The impossibility, committed in advance

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

#### What would decide the verdict

Committed now, so the verdict cannot be fitted to the numbers:

| Verdict | If |
|---|---|
| **KEEP** | the current mechanism violates none of the invariants a replacement would be required to satisfy |
| **MODIFY** | the violations are located in ranking (aggregation, the tie-break, the discard) and in how a rule represents its evidence, **while** the stages below them hold: gates are person-independent (E2), and with the candidate set fixed, person state decides a non-trivial share of contested outcomes (F3) |
| **REBUILD** | a stage below ranking fails: gating is person-dependent in its winners, or with the candidate set fixed the person almost never matters (**under 1 %** of K >= 2 pairs), so that the architecture's person-dependence is made of gating |
| **ABANDON** | replay or generalization fails on reproduction |

My expectation is **MODIFY**. It is falsified by F3 coming in under 1 %, or E2
finding a single person-dependent gate.

---

## results.md

### Intention ranking: results against the predictions

The measurements are in `measurements.md`, generated by
`IntentionRankingExperimentTests`. The predictions, the eleven transformations,
the six aggregators and the verdict criteria were committed in `964d056`, before
the fixture existed.

#### Runs

| | |
|---|---|
| Rule file | frozen. sha256 `61e6412e...b099d92` verified at the **start and the end** of the run, unchanged |
| Selector | `IntentionSelector.Form`, unedited. The fixture's stage-wise reconstruction matches it in **30,618 of 30,618** cells, weights equal to the bit, and on every rewritten rule set that goes through it |
| Sweep | the generalization experiment's 2,187 profiles. Its published 28.6 %, 56, 8,407 and 2,898 all **reproduced exactly** |
| Cells | 30,618 per rule set; 306,180 (rule, cell) pairs per per-rule transformation; 642,978 person-move pairs |
| Fixture tests | **10 of 10 pass**, about 3.5 minutes |
| Randomness | none |
| Production changes | **none** |

#### Predictions

Most of these were derived analytically from the rule file. That they hold is
chiefly a check that the fixture measures what it claims to. The ones that were
ranges or guesses are marked *empirical*.

##### A. Duplication

| # | Prediction | Result | Evidence |
|---|---|---|---|
| A1 | *Empirical.* Duplication changes 19,000 to 21,500 of 306,180 | **PASS** | **19,992**. On every seventh profile, 2,898, exactly the published figure |
| A2 | Every change is toward the duplicated rule's intention | **PASS** | 19,992 of 19,992 |
| A3 | No change where the duplicated rule is not compatible | **PASS** | 0 |
| A4 | Duplicating `doing_it_where_nobody_is_watching` changes 0 | **PASS** | 0 |

##### B. Splitting

| # | Prediction | Result | Evidence |
|---|---|---|---|
| B1 | Halves change 0 of 306,180 (asserted) | **PASS** | 0 |
| B2 | Quarters change 0 | **PASS** | 0 |

##### C. Weight against representation

| # | Prediction | Result | Evidence |
|---|---|---|---|
| C1 | Two classes under the sum, {W, 2 x W/2, 4 x W/4} and {2W, W + W}; 2W and W + W agree everywhere | **PASS** | exactly those classes; 2W against W + W: 0 cells, for all ten rules |
| C2 | The only representation change the sum treats as meaningful is total weight per intention | **PASS** | follows from C1 |

##### D. Candidate sets

| # | Prediction | Result | Evidence |
|---|---|---|---|
| D1 | K = 1 in 4 groups, all alone; 8,748 cells, 28.6 % | **PASS** | exactly |
| D2 | K = 2 in 3 groups; 6,561 cells, 21.4 % | **PASS** | exactly |
| D3 | K = 3 in 7 groups; 15,309 cells, 50.0 %; none larger | **PASS** | exactly |
| D4 | K = 1 groups: one winner, zero sensitivity | **PASS** | 0 of 183,708 moves (asserted) |
| D5 | `restore_standing` alone: `take_responsibility` for all 2,187; `prevent_argument` dominated at -0.07; `assert_authority` undominated, anger only | **PASS** | 100.0 %; bound -0.070; undominated and unwitnessed |
| D6 | At least 35.7 % of cells have one winner across the sweep | **PASS** | 10,935, 35.7 % |
| D7 | Of 27 pairs with K >= 2: 25 witnessed, 1 dominated, 1 neither | **PASS** | 25, 1, 1 |
| D8 | K does not predict sensitivity | **PASS** | `restore_standing` alone (K = 3): 0.0 %; every K = 2 group: 3.5 to 4.9 % |
| D9 | `anxious` is structurally unable to change anything | **PASS** | live in no group, measured 0 of 61,236 |

##### E. Gating against preference

| # | Prediction | Result | Evidence |
|---|---|---|---|
| E1 | A gate is a hard impossibility at the level of a reason | **PASS** | by construction: a failed `when` skips the rule before any support is computed, so nothing partial exists to observe |
| E2 | No person move changes the compatible set | **PASS** | 0 of 642,978 (asserted) |
| E3 | *Empirical.* Lifting every gate changes 20 to 45 % of cells, far more alone | **PASS** | **27.5 %**: alone 35.9 %, company 19.0 % |
| E4 | `avoid_exposure` and `look_after` alone, ungated, behave as in company: 48.6 % and 14.0 % | **PASS** | 48.6 % and 14.0 % |
| E5 | *Empirical.* Most of the 9 intention-level exclusions override a person-dependent preference | **PASS** | **8 of 9**; the ninth is idle |
| E6 | The discard fires in exactly 243 cells (81 profiles, `not_making_a_scene_of_it` at -0.010) and changes no winner | **PASS** | 243, 81, -0.010, 0 |

##### F. Preference with the candidate set fixed

| # | Prediction | Result | Evidence |
|---|---|---|---|
| F1 | Compatible set identical in every pair | **PASS** | 0 changed of 642,978 |
| F2 | Supported set moves only through the discard | **PASS** | 2,184 of 2,184 explained (asserted) |
| F3 | *Empirical.* Non-zero preference with candidates fixed | **PASS** | **6.1 %** of 457,086 contested pairs |
| F4 | `impulsive` changes 0 | **PASS** | 0 (asserted) |
| F5 | *Empirical.* 50 to 65 % of company-arrival changes are availability | **PASS** | **58.4 %** (4,911 of 8,407) |

##### G. The aggregation family

| # | Prediction | Result | Evidence |
|---|---|---|---|
| G1 | The aggregators disagree with the sum somewhere | **PASS** | max 5.5 %, mean 11.3 %, normalized max 21.1 %, noisy-OR 13.9 % of cells; deduplicated sum 0, because the file holds no exact duplicate |
| G2 | Under max, `anxious` can change outcomes | **PASS** | 0.2 % of its moves. The deafness belongs to adding, not to the rule |
| G3 | *Empirical.* Under max, `look_after -> protect` in company below 60 % | **PASS** | **45.9 %**, from 86.0 % |
| G4 | The forced share is identical under all six | **PASS** | 28.6 % for all; gating is shared |

##### H. Representation invariance

| # | Prediction | Result | Evidence |
|---|---|---|---|
| H1 | The 66-cell table of P and V (11 transformations x 6 aggregators) | **PASS, every cell** | measurements, section H, "preserved or violated" |
| H2 | T8 breaks the sum only through the discard, for `not_making_a_scene_of_it` | **PASS** | 469 cells, all from that rule, none at a tie |
| H3 | Under mean, duplicating a rule can make its own intention lose; every other aggregator is monotone | **PASS** | mean: **819** away; the other five: 0 |
| H4 | No aggregator keeps T4 and T6 and responds to T9 | **PASS** | none (asserted) |

#### Verdict criteria, committed in advance

| Criterion | Measured | Met? |
|---|---|---|
| MODIFY needs violations located in ranking and representation | R3, R4, R5 (discard), C4 (discard), J1 in ranking and representation; C5, C6 in representation and content | **yes** |
| ...while gates are person-independent (E2) | 0 of 642,978 | **yes** |
| ...and with candidates fixed the person decides a non-trivial share (F3), REBUILD below 1 % | 6.1 % | **yes** |
| ABANDON if reproduction fails | every published number reproduced exactly | **not triggered** |

**Verdict: MODIFY**, as committed.

#### Not predicted

| Finding | Evidence |
|---|---|
| **48.8 % of all conclusions** can be reversed by copying some single existing rule | 14,935 of 30,618 cells; 217 by any one of three rules |
| Lifting every gate changes **exactly** the 8,407 cells that company arriving changes: every change a circumstance makes is a gate decision | structural: no intention has both company-only and alone-only reasons for one want |
| **25 real ties** under the sum: 12 settled by the alphabet, 13 by floating-point rounding | every sweep contribution is a multiple of 0.0025, so gaps below 1e-9 are ties |
| `respect` can decide only in `restore_standing` alone, where its rival needs anger: in the sweep, nothing | live-read table |
| `honest` cancels in `get_food`: both rivals weigh it 0.30 | live-read table |
| A person's fifth and sixth values weigh nothing, so their order never matters | 0 of 21,870; shipped `ValueRankDecay` 0.25 over six ranks. Out of scope, untouched |
| One exclusion is idle: `prevent_argument` for `restore_standing` in company would win for nobody | 0 of 2,187 |
| Lifting a single **reason's** gate can decide as much as an intention's | `pulling_rank_needs_an_audience` for `guard_supplies` alone: 78.7 % |
| **Textual deduplication is defeated by a 0.99 copy** | 19,844 |
| **More variety is not more validity**: noisy-OR gives 100 signatures while ignoring weight | section G |

#### The five success conditions

| | Condition | Answer | Evidence |
|---|---|---|---|
| 1 | Where availability determines outcomes | 35.7 % of cells have one winner whoever the person is. Gates decide 27.5 % of cells, including every change a circumstance makes | D, E, F |
| 2 | Where preference determines outcomes | 64.3 % of cells vary with the person. With candidates fixed, one attribute moves 6.1 % of contested pairs: `answerable_for` 26.4 %, `honest` 12.0 %, `role_claim` 10.0 %, `empathetic` 9.8 % | D, F |
| 3 | Which invariants the current mechanism violates | R3 ties, R4 restatement, R5 grouping (discard), C4 person-dependent exclusion (discard), C5 undeclared impossibility, C6 idle reads, J1 no evidence identity | A, C, E, H |
| 4 | Which invariants any replacement must satisfy | R1 to R6, C1 to C4, C7, C8 and J1 as hard requirements; C5, C6 and the forced share as audited | report, section 8 |
| 5 | Local, or the architecture? | **Local**: ranking plus the rule representation. Every stage below ranking passed every test. Not *only* aggregation: J1 ties the formula to the representation | report, section 9 |

#### Classification

Machine-readable in `classification.json`; in prose, in the report, section 13.

