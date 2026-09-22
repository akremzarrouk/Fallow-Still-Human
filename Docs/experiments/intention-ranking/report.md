# Intention ranking: what a selection mechanism must satisfy

*What properties must an intention-selection mechanism have for us to treat it as
a credible causal mechanism rather than an arbitrary numerical ranking, and which
of them does the current one have?*

## 1. The answer, first

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

## 2. What was run

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

## 3. Where availability decides, and where preference does

### Availability

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

### Preference

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

### More candidates do not mean more person

| K | Groups | Winners per group | Entropy (bits), range | Sensitivity, pooled | Range across groups |
|---|---|---|---|---|---|
| 1 | 4 | 1 | 0 | 0 | 0 |
| 2 | 3 | 2 | 0.70 - 0.99 | 4.4 % | 3.5 - 4.9 % |
| 3 | 7 | 2.71 | 0 - 1.43 | 6.8 % | **0** - 10.9 % |

A third candidate adds variation only if it is contestable. `restore_standing`
alone has three candidates and less variation than any group with two.
`guard_supplies` in company, also three, is less sensitive (4.0 %) than
`get_food` with two (4.9 %).

### What gating currently means

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

## 4. What the current mechanism treats as meaningful

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

## 5. The aggregation family, and why none of it is the answer

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

## 6. The properties, and where the current mechanism stands

### Representation: the answer must not depend on how the psychology is written

| | Property | Test | Current |
|---|---|---|---|
| R1 | Rule order is not psychology | T1 | **holds** (0) |
| R2 | Rule names are not psychology | T2 | **holds** (0) |
| R3 | Intention names are not psychology, so a tie is a tie | T3; ties | **fails**: 12 cells decided by the alphabet, 13 by rounding |
| R4 | Restating a reason does not strengthen it | T4, T5 | **fails**: 19,992 and 19,844; 48.8 % of conclusions reversible |
| R5 | The same reasons, grouped differently, conclude the same | T8, T10 | **fails, narrowly**: T10 holds; T8 moves 469 cells through the discard |
| R6 | Scaling everything together changes nothing | T11 | **holds** (0) |

### Causation: what may change the answer, and how

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

### The joint constraint

| | Property | Current |
|---|---|---|
| J1 | Restatement invariance, split invariance and weight sensitivity cannot all hold for anonymous contributions. So **a reason must carry the identity of its evidence**, and support must aggregate over distinct evidence | the representation carries no evidence identity; the sum settles the question by treating every rule as independent evidence |

**What is not a property.** Invariance to proportional splitting (T6, T7) is not
required on its own. Under evidence identity, two halves of one rule are two
reasons reading identical evidence. They are a malformed rule set to be rejected,
not a rewrite to be survived. The current mechanism passes T6 and responds to
weight, and by the theorem that is exactly why it must fail R4.

## 7. What the current mechanism violates

1. **R4 restatement**, the big one: 48.8 % of conclusions reversible by copying a line.
2. **J1**: rules carry no evidence identity, so R4 cannot be fixed by any choice of formula.
3. **R3 ties**: 25 cells decided by the alphabet or by rounding error.
4. **C4 and R5 through the discard**: the person can delete a candidate, and grouping terms into rules changes answers. On the frozen file it changed no winner; split one rule by term and it changes 469.
5. **C5**: nine intention-level impossibilities nobody declared, eight overriding preference.
6. **C6**: `anxious` is idle for every possible person, and one candidate is provably unwinnable.

## 8. What any replacement must satisfy

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

## 9. Local, or the architecture?

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

## 10. Only now: a direction for production, not implemented

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

## 11. What nobody predicted

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

## 12. Limitations

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

## 13. Classification

Machine-readable in `classification.json`.

| | |
|---|---|
| **PROVEN** | The stages are separable and the reconstruction is exact (0 of 30,618). Compatibility never depends on the person (0 of 642,978). With the candidate set fixed, the person decides 6.1 % of contested moves. The sum's equivalence classes are {W, 2 x W/2, 4 x W/4} and {2W, W + W}. Restating one rule changes 19,992 cells (48.8 % of conclusions reversible), every one toward the copied intention and none outside where it applies. Splitting changes 0 of 306,180. No aggregator over anonymous contributions satisfies restatement, splitting and weight together (theorem, and 0 of 6 measured). The discard fires in 243 cells, changes 0 winners, and breaks term-grouping in 469. 25 real ties are settled by the alphabet (12) or by rounding (13). `anxious` is idle for every possible person. `prevent_argument` is unwinnable in `restore_standing` alone. Gates decide 27.5 % of cells, and every change a circumstance makes. 8 of 9 exclusions override a person-dependent preference |
| **PLAUSIBLE** | That evidence identity in the rule representation is the necessary repair. It follows from J1, but no design was built. That the authored gates mix preconditions with plausibility (a reading of the notes). That the failures are local to ranking and representation, and not the architecture |
| **UNPROVEN** | That a mechanism meeting every requirement in section 8 would still generalize as the current one does. That the 35.7 % single-winner share is a matter of authoring more rules rather than of the architecture. Whether plausibility belongs in a gate at all |
| **FAILED** | The current ranking as a causal mechanism: R3, R4, R5, C4 (through the discard), C5, C6, J1. Every aggregator in the family as a replacement: each gives up restatement, splitting, weight or monotonicity. Textual deduplication as a fix: defeated by a 0.99 copy |
| **UNKNOWN** | Anything involving feelings, memories or the ledger, which the sweep does not vary. Behaviour under a larger vocabulary or other circumstances. Whether any conclusion is psychologically right |

## 14. Verdict

# MODIFY

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

**Suite: pending**, to be filled in from the full run.
