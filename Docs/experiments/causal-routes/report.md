# Causal routes: telling two reasons from one reason written twice

*What causal information must a representation hold, before anything is added
up, to tell "the character had two different reasons that happened to depend on
the same fact" from "the designer wrote the same reason twice"?*

## 1. The answer, first

**More explicit causal structure is required.** Nothing computed from the rules'
contents can tell the two cases apart.

- **The critical pair.** One reason written twice (A1) and two different reasons
  on the same facts (B1) are the same rule file apart from the rules' ids and
  the declared routes. Any representation that ignores rule ids and reads no
  declaration must treat them alike. That was committed as a theorem before
  anything ran. The three representations that read only the rules (A, the
  current selector; B, evidence identity; C, reason signatures) reach identical
  results on A1 and B1 in **2,187 of 2,187** cells.
- **Route identity is what separates them.** D reads a declared **route** for
  every statement: which reason it belongs to, independent of rule ids, order,
  wording and grouping. D tells the pair apart in 2,187 of 2,187 cells.
  - It passes **all 18 family pairs**; A passes 6, B 13 and C 11, exactly as
    predicted.
  - It is invariant to everything a restatement can change, including renaming
    every route.
  - It keeps everything already proven.
  - It never changes a conclusion silently. A copy of a rule that is declared a
    new route changes 20,021 cells, and D flags every one: *confirm these are
    two reasons*.
- **Route identity is not enough.** Two more pieces of structure turned out to
  be needed, and D, as built, has neither:
  - **The role a fact plays, where the role is not a weight.** The frozen file
    says the theft is "reachable only by somebody who believes they are
    answerable". Six of six reviewers read that belief as a precondition. D
    adds it like any other term, so **91 innocent profiles form the theft**
    over a rival.
  - **The circumstance each reason is about, including who it is about.** The
    reviewers agreed that every real pair of reasons is two different reasons,
    six of six each time. But on three of the four they said the person acts
    from one reason or the other, where the author had declared that both
    operate. Each time they explained it by a circumstance: whether the
    protected person is there, whether anyone is watching, whether the other
    party has arrived. **One of those circumstances cannot be written in the
    current gate at all.**
- **How co-active reasons combine matters less than expected.** Declaring two
  pairs of routes alternatives moves 1,604 of the sweep's cells and **no real
  decision** (0 of 1,028). And no reviewer described two reasons that apply in
  the same situation, lead to the same act, and still exclude each other.

Every one of these is a modelling judgment. The data cannot supply it. What a
representation can do is make it explicit, check it for consistency, and never
apply it silently.

**Verdict: MODIFY** (section 13), by the criteria committed before the
experiment ran.

## 2. What was run

| | |
|---|---|
| Frozen | `intentions.json`, sha256 `61e6412e...b099d92`, and `causal-routes.json`, sha256 `781b776d...c37828a`: both checked at the start and the end, **unchanged** |
| Production | **nothing changed**: not `Fallow.Core`, not the selector, shipped rules, wants, candidates, actions, scoring, beliefs, emotions, memories or character data |
| Committed first | in `3780435`: the predictions, the route declared for each frozen rule, twenty synthetic variants with eighteen declared pairs, the annotation items with their answer key, and the protocol |
| Representations | **A** the current selector, reproduced exactly (0 of 30,618 cells differ); **B** evidence identity; **C** reason signatures; **D** declared causal routes |
| Diagnostics | **D-alt** (two pairs of routes declared alternatives); **D-enablers** (the declared enabler honoured); **G** (a negative control for evidence reuse) |
| Sweep | 2,187 profiles x 7 wants x 2 circumstances = **30,618** cells per rule set; 95 rewritten rule sets, all in memory |
| Real mornings | 50 baseline mornings: **257** pantry-checks, **771** matched pairs, 1,028 real decisions |
| Annotation | 6 reviewers (2 opus, 2 sonnet, 2 haiku), blind, 12 items |
| Fixture | `CausalRouteExperimentTests`, **7 of 7 pass**, 32.5 minutes. No randomness |

Three things were decided after the predictions were committed (`results.md`
lists them). Only one bears on a conclusion. After the reviewer responses had
been read, a row was added comparing the reviewers' Q3 majority with the
relation the author declared. The verdict does not depend on it.

## 3. Evidence, route and intention, and the four representations

| | What it is | Example |
|---|---|---|
| **Evidence** | a fact about the person or the situation | `trait:empathetic`, `value:closeness`, `circumstance:others>=1` |
| **Route** | one declared explanation of why some evidence supports an intention | "I take it on myself to keep them from harm" |
| **Intention** | what the person is trying to accomplish | `protect` |

A route key names one declared meaning and nothing else. It is not a rule id:
one reason written as three rules carries one key. Renaming every key
consistently must change nothing, and changes nothing (R11, 0 cells).

| | Identity it reads | A repeat | One fact, two strengths | Relations between reasons |
|---|---|---|---|---|
| **A** | none: anonymous rules | adds | adds | none |
| **B** | the evidence key, per intention | once | once, at the strongest; flagged | none |
| **C** | the reason signature: intention, gate, set of evidence keys | once | once per signature; flagged | none |
| **D** | **the declared route**: each statement is (intention, route, evidence, coefficient, sign, role, the rule that stated it) | once within a route | a conflict within a route, flagged; separate across routes | declared: independent (the default) or alternative |

D's combination rules are the least that lets a declaration do anything:

- within a route, an identical statement counts once;
- independent routes add;
- a declared group of alternatives contributes its strongest member.

They were fixed before the run. They are not proposed as the formula. On the
frozen file only the first two are ever used, and they reproduce what A and C
already compute.

## 4. The critical pair

A1 is `duty` written twice. B1 is `duty` and `compassion`: two rules with
**identical contents** (base 0.10, empathy 0.40, closeness 0.25), declared as
two different reasons.

| Profile p54 (empathetic 0.85, closeness weight 0.75) | A | B | C | D |
|---|---|---|---|---|
| A0: `duty` once | 0.628 | 0.628 | 0.628 | 0.628 |
| A1: `duty` twice | **1.255** | 0.628 | 0.628 | 0.628 |
| B1: `duty` and `compassion` | 1.255 | 0.628 | 0.628 | **1.255** |

- **A counts both files twice.** It fails A1, where the reason is restated.
- **B and C count both once.** They fail B1, where the reasons are different.
- **D counts A1 once and B1 twice, because it was told which is which.** Over
  2,187 profiles, A1 and B1 differ under D in protect's support in every cell,
  and in the chosen intention in 1,259.

D's two explanations show the difference, and the doubt:

- A1: `duty{circumstance:any=0.100; trait:empathetic=0.340; value:closeness=0.188}`, with 3 restated statements recognised.
- B1: `compassion{...} + duty{...}`, the same evidence twice. D flags 1 pair of
  different routes stating identical evidence: *confirm these are two reasons*.

That flag is as far as a representation can go. If a designer writes the same
reason twice and declares it twice, D cannot know it was an accident. It says
so every time: on the frozen file, a copy declared a new route is flagged in all
78,732 (rule, cell) pairs where the copy applies.

## 5. The five families

Each variant is evaluated for `look_after` in company, over 2,187 profiles,
against the two frozen rivals. The pass criteria were fixed in advance: a *same*
pair must leave both the support and the explanation unchanged; a *different*
pair must change the support; a *structure* pair must keep the support and
change the explanation; a *malformed* variant must be flagged; a *reuse* pair
must leave the support unchanged.

| Family | Pair | Declared | A | B | C | D | Why the failures fail |
|---|---|---|---|---|---|---|---|
| A, restatement | A0 A1, A2, A3 | same | fail | pass | pass | pass | A counts the copy |
| | A0 A4, partial copy | same | fail | pass | **fail** | pass | a partial copy is a new signature for C |
| | A0 A5, one reason as two rules | same | fail | pass | **fail** | pass | the explanation lists two rules or two signatures |
| | A0 A6, route key renamed | same | pass | pass | pass | pass | |
| B, two reasons on the same facts | **A1 B1** | **different** | **fail** | **fail** | **fail** | **pass** | the theorem |
| | A0 B1 | different | pass | fail | fail | pass | B and C merge the second reason |
| | B1 B3, reordered and renamed | same | pass | pass | pass | pass | |
| C, one fact, two intentions | C0 C1 | reuse | pass | pass | pass | pass | G fails it, as a negative control should |
| D, one reason on several facts | D0 D2, as three rules | same | fail | pass | fail | pass | grouping read as identity |
| | D0 D3, partly restated | same | fail | pass | fail | pass | |
| | D1 D4, one of three restated | same | fail | pass | pass | pass | |
| | D0 D1, same numbers, other structure | structure | pass | **fail** | pass | pass | B collapses three equal bases into one |
| E, strength and role | A0 E1, one route, two strengths | malformed | fail | pass | pass | pass | A adds it without a flag |
| | A0 E2, a second route at another strength | different | pass | pass | pass | pass | |
| | E2 E3, independent against alternative | different | fail | fail | fail | pass | only D can hold a relation |
| | A0 E4, driver and inhibitor | different | fail | fail | pass | pass | A discards the inhibitor; B keeps only the stronger statement |
| | | **Passed** | **6** | **13** | **11** | **18** | |

D passes every family **by construction: it reads the declarations.** That is
both the point and the limit. D is exactly as right as what it is told.

## 6. The invariants

Cells, of 30,618, whose outcome changed under each rewrite. Per-rule rewrites are
summed over the ten rules. In brackets: changes the representation did not flag.

| | Rewrite | A | B | C | D |
|---|---|---|---|---|---|
| R1 | reverse the rule order | 0 | 0 | 0 | 0 |
| R2 | new rule ids | 0 | 0 | 0 | 0 |
| R3 | rename the intentions | 12 (12) | 0 | 0 | 0 |
| R4a to R4c | exact, reworded and 0.99 copies, in the same route | 19,992; 19,992; 19,844 (all) | 0 | 0 | 0 |
| R4d | a partial copy, in the same route | 18,938 (all) | 0 | **19,062 (all)** | 0 |
| R4new | an exact copy **declared a new route** | 19,992 (all) | 0 | 0 | **20,021 (0)** |
| R5a | W to W/2 + W/2, in the same route | 0 | 15,210 (0) | 13,796 (0) | 13,796 (0) |
| R6, R7 | doubling a rule; strengthening it | respond; 0 away | respond; 0 away | respond; 0 away | respond; 0 away |
| R8 | changes outside where the rewritten rule applies | 0 | 0 | 0 | 0 |
| R9a, R9b | split by term; merge | 469; 0 | 0; 0 | 0; 0 | 0; 0 |
| R10 | candidates not the compatible set | 243 | 0 | 0 | 0 |
| **R11** | **rename every route key** | 0 | 0 | 0 | **0** |

The five invariants this experiment added:

| Invariant | Test | D |
|---|---|---|
| **Causal identity invariance**: a route is its declared meaning, not a name or a place | R2, R11, A0 A6, B1 B3 | 0, 0, pass, pass |
| **Route independence**: a second declared route contributes as a second reason; a restated one does not | A1 B1, A0 B1, A0 E2; R4a against R4new | pass; 0 against 20,021, all flagged |
| **Restatement immunity** | R4a to R4d; families A and D; real mornings | 0 each; pass; 0 of 5,140 |
| **Evidence reuse**: one fact supporting a second intention leaves the first unchanged | C0 C1; G as control | pass; G fails in 2,187 |
| **Provenance**: every winner traced from route to evidence to coefficient and sign to the level read, reconstructing its score | R15 | 30,593 of 30,593 winners within 1e-9 (the other 25 cells are ties) |

R5a is the theorem of the ranking experiment again. A representation that does
not add restatements cannot also treat a proportional split as the unsplit
rule. D, like B and C, reads W/2 + W/2 inside one route as a weaker reason
restated. It flags every such change.

## 7. The frozen file under declared routes

Every frozen rule was declared its own route, and all routes independent. So on
the frozen file:

- **D equals C in every cell, and A in every cell but 25, all of them ties D
  reports.** It keeps everything proven:
  - 28.6 % single-candidate cells;
  - blindness to hunger and to a foodless room;
  - exact replay;
  - no character names;
  - 6.1 % fixed-candidate sensitivity.
- **D differs from B in 660 cells.** These are the 660 the representation
  experiment left open, where one fact is cited by two different reasons for
  one intention. By D's declarations, B merged two different reasons there.
  The reviewers agree they are different reasons: six of six for each pair
  (section 9). Whether both *operate at once* is a different question, and it
  is where the reviewers and the declarations part.
- **Route identity changes nothing on this file.** Each route is exactly one
  rule, so the frozen file never exercises it. Everything route identity adds
  shows only under rewriting and in the synthetic families.

**What the relation judgment moves (D-alt).** Two pairs were declared
alternatives:

- `standing_in_the_way` and `shielding_from_afar`;
- the two authority routes.

This changes **1,604** cells: 877 in `look_after`, 378 in `guard_supplies` and
349 in `restore_standing`, all in company. `look_after -> protect` in company
falls from 86.0 % to 45.9 %. Neither figure is treated as better. The question
is what the person is, not how varied the outcomes are.

**What the role judgment moves (D-enablers).** Honouring `answerable_for` as the
condition of `owning_the_night` changes **91** cells. Every one is a profile
without the belief that formed the theft over a rival, in `avoid_exposure` in
company. Nothing else changes.

It also exposes what no representation here answers. **In `avoid_exposure`
alone, the theft is the only candidate.** There, 1,094 innocent profiles still
"form" it, now with zero support: an intention formed for no reason. That is a
question for selection: may a person form no intention?

Moving the enabler into the compatibility stage would break a proven property.
That stage reads only circumstances, by design, and that is why no change to a
person changes what is possible. D-enablers shows the enabler can live inside
support instead, as a condition on a route.

## 8. Real mornings

| | A | B | C | D | D-alt | D-enablers |
|---|---|---|---|---|---|---|
| Matched pairs where the same act is carried by different intentions | 486 of 771 | 486 | 486 | 486 | 486 | 486 |
| Same intention, different person evidence behind it | 285 of 285 | 285 | 285 | 285 | 285 | 285 |
| Real decisions differing from D | 0 | 0 | 0 | 0 | 0 | 0 |

- **On real mornings, nothing D decides differs from A.** The relation and role
  judgments change no real pantry decision.
- **Routes never separate two people who form the same intention.** The leading
  route differs in 0 of 285 such pairs. The person evidence differs in all 285.
  On these mornings, routes change how support is counted. They do not change
  who is distinguished from whom.

What routes change on real mornings is **how robust a decision is to the way the
rules are written**. Each real pantry-check was re-decided with one rule copied,
for each of the ten rules (2,570 re-decisions per row):

| Rewrite | A: intentions / reasons changed | C | D |
|---|---|---|---|
| Copied, same route | 110 / 257 | 0 / 0 | **0 / 0** |
| Partly copied, same route | 110 / 257 | 110 / 257 | **0 / 0** |
| Copied, **declared a new route** | 110 / 257 | 0 / 0 | 110 / 257, **all 110 flagged** |

Prediction 3.6 failed. D-enablers changes no real decision. The innocent theft
occurs in the sweep only in `avoid_exposure`, which never leads to a
pantry-check, so this sample could not show it.

## 9. The blind annotation

Six fresh subagents, shown only the items in a rotated and swapped order, under
neutral ids. **They are language models, not people.** Their agreement is
evidence that a distinction is legible and reproducible, never that it is true.

| Item | Declared | Judgment: restatement / different / unclear | Q3: both / one or other / unclear | Declared Q3 |
|---|---|---|---|---|
| `real_protect` | different | 0 / 6 / 0 | 1 / **5** / 0 | both |
| `real_assert` | different | 0 / 6 / 0 | 2 / **4** / 0 | both |
| `real_take` | different | 0 / 6 / 0 | **4** / 0 / 2 | both |
| `real_prevent` | different | 0 / 6 / 0 | 1 / **5** / 0 | both |
| `syn_critical` | different | 0 / 6 / 0 | **6** / 0 / 0 | both |
| `syn_alternative` | different | 0 / 6 / 0 | 0 / **6** / 0 | one or other |
| `syn_roles` | different | 0 / 6 / 0 | 0 / **6** / 0 | both (the question was ill-posed) |
| `control_different` | different | 0 / 6 / 0 | **6** / 0 / 0 | both |
| `syn_restate_protect` | restatement | **6** / 0 / 0 | | |
| `control_same` | restatement | **6** / 0 / 0 | | |
| `syn_restate_assert` | restatement | **5** / 0 / 1 | | |
| `real_role` (Q5) | precondition | precondition 6 of 6 | | |

- **Identity is legible and reproducible.**
  - Judgment kappa **0.925**.
  - The majority matches the key on 11 of 11 items.
  - Every real pair is six of six "different".
  - The critical pair is six of six "different", and its twin restatement six
    of six "restatement".
- **The relation is reproducible too.** Q3 kappa is **0.592**, where the
  prediction was below 0.4.
- **But the relation is not the author's.** On three of the four real pairs,
  the majority says the person acts from one reason or the other, where the
  author declared both.

**Reading that disagreement against the rules' gates** (the author's coding,
labelled as such by the protocol):

| Pair | Gates | Can both be candidates at once? | Circumstance named in Q4 | Q3 majority |
|---|---|---|---|---|
| `real_prevent` | `others_present_min: 1` / `alone` | **never** (`Percept.Alone` is `Present.Count == 0`) | whether the other party is there yet: 5 of 6 | one or other |
| `real_protect` | `others_present_min: 1` / none | yes, in company | whether the protected person is there: 4 of 6 | one or other |
| `real_assert` | `others_present_min: 1` / none | yes, in company | whether anyone is watching: 6 of 6 | one or other |
| `real_take` | none / `alone` | yes, alone | whether anyone is watching: 4 of 6 | **both** |

- **`real_prevent`.** The reviewers read what the gates already enforce. The
  author's declaration of "both" never computes anything, because the two
  routes are never candidates together.
- **`real_protect`.** The texts make the two reasons exclusive: one needs the
  protected person there ("somebody to put yourself in front of"), the other is
  about them not being there ("a thing they are not in the room for"). The gate
  of the second is empty. And **`SituationCondition` has no field for a
  particular person being present or absent.** It counts people; it does not
  know whom the intention is about. The route declaration had quietly
  broadened the note ("including when they are not there"). The reviewers saw
  the note.
- **`real_assert`.** The texts contradict each other. The first says settling
  something with nobody watching is "housekeeping", not authority. The second
  says settling is yours to do, audience or not. Reviewer 2 names this
  directly.
- **`real_take`.** Here the circumstances overlap: one reason needs nobody
  watching, the other does not care. The majority says both.

So in every real pair, the reviewers' relation judgment follows the
**circumstance each reason is about**. The author's declaration followed the
gates, or ignored them. **Neither D nor D-alt computes what the reviewers
describe.** D adds co-active routes, and D-alt keeps the stronger. The reviewers
describe the situation choosing the route. On the one item where they did
describe exclusion without a circumstance, `syn_alternative`, at least four of
six located it in the act (done quietly or openly: "the same act cannot be
both"), not in the reasons.

Outside the ill-posed `syn_roles`, no answer describes two reasons that apply in
the same situation, lead to the same act, and exclude each other. That is the
case D-alt computes. Two more observations, from the Q4 answers:

- **On `syn_roles`**, both opus reviewers said the inhibitor is not a route to
  the intention but a reason against it. Q3 asked whether both reasons "push
  toward" the intention, which presupposed otherwise. The six of six
  disagreement there is an artefact of the question.
- **On the critical pair**, both opus reviewers said the difference between the
  two reasons cannot be seen from the facts cited, and that an explanation would
  need a further fact to show it.

This is 24 short answers from language models, coded by the author who wrote
the declarations. It is suggestive and no more.

## 10. What the simulation must retain

Carried from the representation experiment, and confirmed here:

1. **Each statement's evidence key, coefficient and sign**, apart from the
   level read from the person.
2. **The compatible set as the candidate set, and ties as ties.**

New, and each one a declaration made before anything is added up:

3. **A declared route for every statement.** Its identity is a declared
   meaning, not a rule id, position, wording or grouping. Many rules may carry
   one route, and renaming routes changes nothing.
4. **Provenance.** Which rule made which statement, so that two routes stating
   exactly the same thing can be put in front of someone rather than decided
   silently.
5. **The role of each fact within its route**: driver, inhibitor, or **enabling
   condition**. An enabling condition is not a term and cannot be written as
   one.
6. **The circumstance each route is about, including whom it concerns.** The
   current gate can say "somebody is here" or "nobody is here". It cannot say
   "the person I am protecting is not here".
7. **For routes that are active together, whether they combine or exclude.**
   This is a declared, flagged judgment. It is the last of these to matter, and
   the least supported: no reviewer described such an exclusion between reasons
   rather than between situations or acts.
8. **Flags, never silent resolution:**
   - two routes stating identical evidence;
   - one fact at two strengths within a route;
   - a role contradicting its sign;
   - and, in explanations, which member of an alternative group operated. D's
     explanation does not yet say this: E2 and E3 explain identically in 2,187
     cells while their support differs in all 2,187.

It must **not** keep, as meaning: rule ids, rule order, rule count, the
grouping of statements into rules, wording, or the spelling of route keys.

## 11. Limitations

- **The reviewers are language models.** They share training and may share
  blind spots. Their agreement is weaker evidence than agreement between
  independent people. A human panel is the obvious next check.
- **The author declared the routes, wrote the items and wrote the answer key.**
  The reviewers were blind, but the material they judged was not neutral.
- **The real items used the rules' notes, which is what the file says.** For
  `keeping_it_off_them`, the declared route meaning was broader than the note
  the reviewers saw.
- **Q3 was ill-posed for the inhibitor item.** Its six of six disagreement is
  not evidence about roles.
- **The comparison of Q3 majorities with the declared relation was added after
  the responses were read.** The verdict does not rest on it.
- **The frozen file has one route per rule.** Route identity is exercised only by
  the synthetic families and the rewrites: 20 variants of one focal reason, and
  95 rewritten rule sets.
- **R15 was verified under D only.** No alternatives are declared there, and D's
  explanation does not mark which alternative operated.
- **The real-morning sample is pantry-checks.** The one real case where the
  enabler matters cannot occur in it.
- **One file of ten rules**, with feelings fixed across the sweep, as in the
  earlier experiments.
- **No selection rule** was tested for a sole candidate with no active reason.

## 12. Classification

### Representation properties

| | |
|---|---|
| **PROVEN** | A is the selector (0 of 30,618). A, B and C cannot tell the critical pair apart: identical in 2,187 of 2,187 cells, as the theorem requires. D can: 2,187 of 2,187. The families pass as predicted in all 72 entries: A 6, B 13, C 11, D 18 of 18. D is invariant to rule order, rule ids, intention names, exact, reworded, near and partial restatement within a route, splitting by term, merging and renaming every route: 0 cells each. D changes nothing silently: R5a 13,796 and R4new 20,021 changes, 0 unflagged; the new-route flag fires in 78,732 of 78,732 (rule, cell) pairs where the copy applies. Provenance reconstructs 30,593 of 30,593 winners. Evidence reuse holds under every representation, and the negative control G breaks it. D keeps 28.6 %, blindness, replay, no character names and 6.1 % sensitivity, and equals C on the frozen file (A outside 25 ties). On real mornings, one copied rule changes 110 of 2,570 intentions under A and 0 under D within a route, or 110, all flagged, when the copy is declared a new route |
| **PLAUSIBLE** | That a declared route is the right unit of identity for authored reasons. It is the only representation tested that passes every family, but on one focal reason and one file |
| **FAILED** | A, B and C as representations of reasons: none can hold the critical pair, and only D can hold a relation (E3). D's explanation as a complete account: it does not mark which alternative operated |
| **UNKNOWN** | Behaviour on a file where several rules share a route, or where many routes share facts |

### Causal semantics: what the declarations mean, and what they move

| | |
|---|---|
| **PROVEN** | The relation judgment moves 1,604 sweep cells and 0 of 1,028 real decisions. The role judgment moves 91 sweep cells, every one an innocent theft, and 0 real decisions. It leaves 1,094 sole candidates formed with zero support. D's additive statements cannot express an enabling condition. The declared relation of the `prevent_argument` pair never computes anything, because its gates never both hold. The gate cannot say that a particular person is absent. On the frozen file route identity coincides with rule identity, so the 660 cells B changed rest, under D, on the declaration that each rule is its own reason. Routes separate none of the 285 real same-intention pairs, and evidence separates all of them |
| **PLAUSIBLE** | That the relation reviewers perceive between two reasons is mostly the circumstance each is about, not how they combine: four real pairs and their Q4 answers, as coded by the author. That a route's circumstance, including whom it concerns, belongs to its causal meaning |
| **UNPROVEN** | Whether the frozen `protect` and `assert_authority` routes combine or exclude. Whether "only the stronger operates" describes any real pair of co-active reasons. What should happen when the only candidate has no active reason |
| **FAILED** | D, with the declarations as written, as a complete causal structure: it cannot compute the enabler, and it cannot represent the circumstance the reviewers read in `real_protect`. The author's relation declarations as a reading others share: 3 of 4 real pairs |

### Psychological validity

| | |
|---|---|
| **PROVEN** | Nothing. No test here can prove how people are |
| **PLAUSIBLE** | Legibility only. Language-model readers draw the declared identities the same way the author did and the same way as each other: kappa 0.925, 11 of 11. They read the declared enabler as a precondition, 6 of 6 |
| **UNPROVEN** | That any declared route, role or relation is how a person's reasons work. That two independent reasons on one fact move a person more than one reason does, which is what D's default declaration assumes |
| **UNKNOWN** | Whether people would judge as the models did |

## 13. Verdict

# MODIFY

These criteria were committed with the predictions:

> **KEEP**: D passes the retained and the new invariants. A, B and C fail the
> critical pair. D passes every family. D keeps what was proven. And the
> judgments D needs are reproducible: judgment kappa at least 0.6, Q3 kappa at
> least 0.4, the majority matching the key on every real pair. And no family
> shows a declared meaning D cannot compute.
>
> **MODIFY**: D does all it is built for, but a needed piece of causal structure
> is missing or unreliable: a declared role D's statement form cannot compute
> (the enabler), a relation judgment reviewers cannot reproduce, or route
> identities that reviewers do not see as declared.
>
> **REBUILD**: the intention architecture cannot carry route identity without
> breaking what is proven: D fails the stage separation, R1 to R10, or
> generalization.
>
> **ABANDON**: no representation can tell the critical pair apart, even with
> declarations.

**What was met.** Every quantitative condition of KEEP was met:

- D passes all its invariants and all 18 families;
- A, B and C fail the critical pair;
- D keeps everything proven;
- judgment kappa 0.925, Q3 kappa 0.592, and the key matched on all four real
  pairs.

**Why not KEEP.** The last KEEP condition speaks of the families, and every
family was computed. But the frozen declarations contain one meaning D cannot
compute, the enabler, and the MODIFY row names it explicitly. D adds the belief
as a weighted term. Innocent profiles form the theft over a rival in 91 cells,
and six of six reviewers read the belief as a precondition. **That alone makes
this MODIFY.**

A second reason points the same way, and it is labelled as post hoc. The
reviewers reproduce one another's relation judgments, but not the author's: 3
of 4 real pairs. Their reading turns on a circumstance that D's declarations
lack and, in one case, that the gate cannot express.

**Not REBUILD.** The critical distinction was expressed over the same staged
statements the selector already builds, with one declared key per statement.
Stage separation, R1 to R11 and generalization all held. Even the enabler can be
expressed without touching the stages. D-enablers makes it a condition on a
route inside support, and changes exactly the 91 innocent cells and nothing
else. The architecture can express the distinction. Its representation lacks
the declarations.

**Not ABANDON.** D tells the critical pair apart in every cell.

**What MODIFY means here:**

- **Keep what D adds** (section 10, items 1 to 4 and 8):
  - route identity per statement;
  - provenance;
  - restatement within a route counting once;
  - flags instead of silent merges.
- **Add, as declared structure, before any aggregation:**
  - **enabling conditions as conditions**, not terms, with a decision at the
    selection stage about a candidate left with no active reason;
  - **the circumstance each route is about**, including whom it concerns;
  - **the relation between co-active routes** as an explicit, flagged judgment.
    Decide whether "alternative" is a relation between reasons at all, or a
    sign that two reasons lead to different acts.
- **Make explanations name which routes operated.**
- **Nothing has been implemented.** The next step is a decision about what a
  route declaration may say, not code.

## 14. The question, in plain language

*What information must the simulation retain so that "the character had two
different reasons that happened to depend on the same fact" is meaningfully
different from "the designer accidentally wrote the same reason twice"?*

**More explicit causal structure is required.** The numbers alone cannot tell
these apart. A reason written twice and two reasons on the same fact produce
the same rules, the same facts and the same weights. Any method that looks only
at those must treat them the same. That was proven before it was measured, and
then measured: identical in every one of 2,187 cases.

To tell them apart at all, the simulation must keep, for every piece of every
reason:

- **Which reason it belongs to.** This is a declared identity: part of what the
  character is modelled as caring about. It is not the rule's name, its place
  in the file, its wording, or how it was split into rules. With it, writing
  the same reason twice changes nothing, and a second reason counts as a second
  reason.
- **How strongly, and in which direction, the fact acts within that reason**,
  kept apart from how much of that fact the person has.
- **Where it came from.** Then, when two declared reasons say exactly the same
  thing, the simulation can point at them and ask whether the designer meant
  it.

That makes the two cases different. To make the difference **mean** something,
beyond one of them counting twice, each reason must also carry what makes it a
different reason:

- **The situation it is about, and who it is about.** "I put myself between them
  and it" needs them there. "I keep it off them" is about them not being there.
- **The part each fact plays**: pushing toward the intention, holding back from
  it, or being the condition without which the reason does not apply at all.
- **Only then, for two reasons that apply at the same moment, whether they add
  up or replace each other.**

If two reasons read the same facts, in the same way, in the same situations,
the only thing separating them is the designer's say-so. The simulation cannot
check that. It can only keep it, and flag it for someone to confirm.

None of this can be learned from the data or produced by an aggregation formula.
It has to be written down, as a modelling judgment, before anything is added
up. It has not been implemented.

---

Reproduce with `./run-tests.sh`, or the fixture alone with
`unity test . --mode EditMode --filter CausalRouteExperimentTests`. It takes
about half an hour, most of it in the 95 rewritten rule sets.

**Suite: pending.**
