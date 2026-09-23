# causal-routes: all documents

Merged by `merge-slice-docs.py` from the 5 Markdown files in `Docs/experiments/causal-routes/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`measurements.md`](#measurementsmd)
- [`predictions.md`](#predictionsmd)
- [`results.md`](#resultsmd)
- [`annotation/protocol.md`](#annotationprotocolmd)

---

## report.md

### Causal routes: telling two reasons from one reason written twice

*What causal information must a representation hold, before anything is added
up, to tell "the character had two different reasons that happened to depend on
the same fact" from "the designer wrote the same reason twice"?*

#### 1. The answer, first

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

#### 2. What was run

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

#### 3. Evidence, route and intention, and the four representations

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

#### 4. The critical pair

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

#### 5. The five families

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

#### 6. The invariants

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

#### 7. The frozen file under declared routes

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

#### 8. Real mornings

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

#### 9. The blind annotation

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

#### 10. What the simulation must retain

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

#### 11. Limitations

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

#### 12. Classification

##### Representation properties

| | |
|---|---|
| **PROVEN** | A is the selector (0 of 30,618). A, B and C cannot tell the critical pair apart: identical in 2,187 of 2,187 cells, as the theorem requires. D can: 2,187 of 2,187. The families pass as predicted in all 72 entries: A 6, B 13, C 11, D 18 of 18. D is invariant to rule order, rule ids, intention names, exact, reworded, near and partial restatement within a route, splitting by term, merging and renaming every route: 0 cells each. D changes nothing silently: R5a 13,796 and R4new 20,021 changes, 0 unflagged; the new-route flag fires in 78,732 of 78,732 (rule, cell) pairs where the copy applies. Provenance reconstructs 30,593 of 30,593 winners. Evidence reuse holds under every representation, and the negative control G breaks it. D keeps 28.6 %, blindness, replay, no character names and 6.1 % sensitivity, and equals C on the frozen file (A outside 25 ties). On real mornings, one copied rule changes 110 of 2,570 intentions under A and 0 under D within a route, or 110, all flagged, when the copy is declared a new route |
| **PLAUSIBLE** | That a declared route is the right unit of identity for authored reasons. It is the only representation tested that passes every family, but on one focal reason and one file |
| **FAILED** | A, B and C as representations of reasons: none can hold the critical pair, and only D can hold a relation (E3). D's explanation as a complete account: it does not mark which alternative operated |
| **UNKNOWN** | Behaviour on a file where several rules share a route, or where many routes share facts |

##### Causal semantics: what the declarations mean, and what they move

| | |
|---|---|
| **PROVEN** | The relation judgment moves 1,604 sweep cells and 0 of 1,028 real decisions. The role judgment moves 91 sweep cells, every one an innocent theft, and 0 real decisions. It leaves 1,094 sole candidates formed with zero support. D's additive statements cannot express an enabling condition. The declared relation of the `prevent_argument` pair never computes anything, because its gates never both hold. The gate cannot say that a particular person is absent. On the frozen file route identity coincides with rule identity, so the 660 cells B changed rest, under D, on the declaration that each rule is its own reason. Routes separate none of the 285 real same-intention pairs, and evidence separates all of them |
| **PLAUSIBLE** | That the relation reviewers perceive between two reasons is mostly the circumstance each is about, not how they combine: four real pairs and their Q4 answers, as coded by the author. That a route's circumstance, including whom it concerns, belongs to its causal meaning |
| **UNPROVEN** | Whether the frozen `protect` and `assert_authority` routes combine or exclude. Whether "only the stronger operates" describes any real pair of co-active reasons. What should happen when the only candidate has no active reason |
| **FAILED** | D, with the declarations as written, as a complete causal structure: it cannot compute the enabler, and it cannot represent the circumstance the reviewers read in `real_protect`. The author's relation declarations as a reading others share: 3 of 4 real pairs |

##### Psychological validity

| | |
|---|---|
| **PROVEN** | Nothing. No test here can prove how people are |
| **PLAUSIBLE** | Legibility only. Language-model readers draw the declared identities the same way the author did and the same way as each other: kappa 0.925, 11 of 11. They read the declared enabler as a precondition, 6 of 6 |
| **UNPROVEN** | That any declared route, role or relation is how a person's reasons work. That two independent reasons on one fact move a person more than one reason does, which is what D's default declaration assumes |
| **UNKNOWN** | Whether people would judge as the models did |

#### 13. Verdict

### MODIFY

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

#### 14. The question, in plain language

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

**Suite: 439 tests, 437 pass, 2 fail**: the two regressions S1.4 left failing, unchanged
(the pacing gate, still 7 on Model A, and the emergent-moment fading check). The 432
before this experiment, plus its seven, is exactly 439. The full suite now takes 131
minutes, longer than the 7,200-second timeout in `run-tests.sh`. The first attempt
timed out before writing results, and the run reported here used a copy with the timeout
raised to four hours; the repository's script was not changed. **This experiment's
measurements, regenerated inside the suite, are byte-identical to the first run.** Every
other generated document regenerated with identical content, except the wall-clock
seconds in the decision-sensitivity results and one file that differed in line endings
only.

---

## measurements.md

### Causal routes: measurements

Generated by `CausalRouteExperimentTests` against the frozen candidate rules and the route declarations, both hashed at the start and the end of the run. The predictions, the declarations, the synthetic families and the annotation protocol were committed before this fixture existed. There is no randomness anywhere.

#### 0. What is frozen, whether A is the selector, and what is declared

| | sha256 at the start of this run | Expected | Match |
|---|---|---|---|
| `intentions.json` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | **yes** |
| `causal-routes.json` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | **yes** |

A, rebuilt from its stages, differs from `IntentionSelector.Form` in **0** of 30618 cells; winning weights not equal to the bit: **0**.

##### The route declared for each frozen rule

| Rule | Route | Intention | What the route means | Declared roles |
|---|---|---|---|---|
| `pulling_rank_needs_an_audience` | `authority_shown_to_witnesses` | assert_authority | Asserting authority as something done in front of others: it is authority rather than housekeeping because somebody is there to see it. | sign |
| `being_the_one_who_decides_it` | `settling_is_mine` | assert_authority | Settling the matter because settling such things is one's own place, audience or not; being angry already makes it stronger. | sign |
| `somebody_has_to_do_it` | `a_job_that_needed_doing` | take_responsibility | Doing it because it needed doing and somebody had to. | sign |
| `doing_it_where_nobody_is_watching` | `proving_it_to_myself` | take_responsibility | Doing it to prove it to oneself rather than to anyone else, which only makes sense unwatched. | sign |
| `so_that_they_know_too` | `finding_out_for_the_room` | share_information | Finding out on behalf of the others present, so that they know too. | sign |
| `standing_between_them_and_it` | `standing_in_the_way` | protect | Protecting somebody by putting oneself physically in the way of what threatens them. | sign |
| `keeping_it_off_them` | `shielding_from_afar` | protect | Protecting somebody by keeping a matter away from them, including when they are not there. | sign |
| `not_making_a_scene_of_it` | `defusing_the_scene` | prevent_argument | Keeping things from becoming a scene in front of others; a dominant person settles rather than defuses. | `trait:dominant` inhibitor |
| `letting_it_go_for_now` | `letting_it_go` | prevent_argument | Choosing not to have it out yet, with nobody there to have it out with. | sign |
| `what_you_did_in_the_night` | `owning_the_night` | took_what_was_not_mine | Taking one's own act as a theft, which is only possible for somebody who believes they are answerable for the missing can: the belief is the condition, and honesty, fairness and shame are what act on it. | `belief:answerable_for($self,missing_can)` enabler |

Cells in which D finds two different routes stating identical evidence: **0**. Cells with a declared role contradicting its sign: **0**.

#### 1. The critical pair, and the five families

Each variant is evaluated for `look_after`, in company, over all 2187 sweep profiles, against the two frozen rivals. The rule contents of every variant are in `causal-routes.json`. Passing is as fixed in the predictions: a **same** pair must leave protect's support and the representation's explanation identical in every cell; a **different** pair must change protect's support somewhere; a **structure** pair must keep the support and change the explanation; a **malformed** variant must be flagged; a **reuse** pair must leave protect's support identical.

| Pair | Declared | What it tests | A | B | C | D |
|---|---|---|---|---|---|---|
| A0 A1 | same | exact restatement | **fail** (support 2187, explanation 2187, outcome 1255) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| A0 A2 | same | restatement, reworded: terms reordered, new id | **fail** (support 2187, explanation 2187, outcome 1255) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| A0 A3 | same | near restatement at 0.99 | **fail** (support 2187, explanation 2187, outcome 1255) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| A0 A4 | same | partial restatement | **fail** (support 2187, explanation 2187, outcome 990) | pass (support 0, explanation 0, outcome 0) | **fail** (support 2187, explanation 2187, outcome 994) | pass (support 0, explanation 0, outcome 0) |
| A0 A5 | same | one route written as two rules | **fail** (support 0, explanation 2187, outcome 0) | pass (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 2187, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| A0 A6 | same | the route key renamed | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| A1 B1 | different | THE CRITICAL PAIR: identical rule contents, one reason twice against two reasons | **fail** (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 0, outcome 0) | pass (support 2187, explanation 2187, outcome 1259) |
| A0 B1 | different | a second, independent reason on the same facts | pass (support 2187, explanation 2187, outcome 1255) | **fail** (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 0, outcome 0) | pass (support 2187, explanation 2187, outcome 1259) |
| B1 B3 | same | two routes, reordered, renamed rules and renamed route keys | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| C0 C1 | reuse | the same fact supporting a second intention must not change the first | pass (support 0, explanation 2187, outcome 626) | pass (support 0, explanation 2187, outcome 611) | pass (support 0, explanation 2187, outcome 626) | pass (support 0, explanation 2187, outcome 626) |
| D0 D2 | same | one bundled reason written as three rules | **fail** (support 0, explanation 2187, outcome 0) | pass (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 2187, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| D0 D3 | same | a bundled reason partly restated | **fail** (support 2187, explanation 2187, outcome 762) | pass (support 0, explanation 0, outcome 0) | **fail** (support 2187, explanation 2187, outcome 762) | pass (support 0, explanation 0, outcome 0) |
| D1 D4 | same | one of three single-fact reasons restated | **fail** (support 2187, explanation 2187, outcome 551) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) | pass (support 0, explanation 0, outcome 0) |
| D0 D1 | structure | one reason on three facts against three reasons on one fact each: the same numbers, a different structure | pass (support 0, explanation 2187, outcome 0) | **fail** (support 2187, explanation 2187, outcome 480) | pass (support 0, explanation 2187, outcome 0) | pass (support 0, explanation 2187, outcome 0) |
| A0 E1 | malformed | one route stating one fact at two strengths | **fail** (support 2187, explanation 2187, outcome 1246, flagged 0) | pass (support 0, explanation 0, outcome 0, flagged 2187) | pass (support 0, explanation 0, outcome 0, flagged 2187) | pass (support 0, explanation 0, outcome 0, flagged 2187) |
| A0 E2 | different | an independent route citing the same fact at another strength | pass (support 2187, explanation 2187, outcome 1394) | pass (support 1458, explanation 2187, outcome 736) | pass (support 2187, explanation 2187, outcome 1398) | pass (support 2187, explanation 2187, outcome 1398) |
| E2 E3 | different | the same two routes, independent against alternative | **fail** (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 0, outcome 0) | pass (support 2187, explanation 0, outcome 985) |
| A0 E4 | different | the same fact as a driver in one route and an inhibitor in another | **fail** (support 0, explanation 0, outcome 0) | **fail** (support 0, explanation 0, outcome 0) | pass (support 2187, explanation 2187, outcome 344) | pass (support 2187, explanation 2187, outcome 344) |
| **Passed** | | | **6 of 18** | **13 of 18** | **11 of 18** | **18 of 18** |

Counts in brackets are cells, of 2187, where the pair differ in protect's support, in the representation's explanation, and in the outcome.

**The negative control G** (each fact given to one intention only) on C0 C1: **fail** (support 2187, explanation 2187, outcome 845). The reuse test fails when evidence is consumed, as it should.

##### The critical pair for one profile (p54: empathetic 0.850, closeness weight 0.750)

| Variant | A: protect's support | B: protect's support | C: protect's support | D: protect's support |
|---|---|---|---|---|
| A0 | 0.628 | 0.628 | 0.628 | 0.628 |
| A1 | 1.255 | 0.628 | 0.628 | 0.628 |
| B1 | 1.255 | 0.628 | 0.628 | 1.255 |

D's explanation, A1: `duty{circumstance:any=0.100000000;trait:empathetic=0.340000000;value:closeness=0.187500000}` (3 restated statements recognised).

D's explanation, B1: `compassion{circumstance:any=0.100000000;trait:empathetic=0.340000000;value:closeness=0.187500000} + duty{circumstance:any=0.100000000;trait:empathetic=0.340000000;value:closeness=0.187500000}` (1 pair of different routes flagged as stating identical evidence: *confirm these are two reasons*).

##### Agreement with the declared structure, per variant

Cells, of 2187, in which the representation reaches the same outcome as D, which computes the declared structure by construction.

| Variant | A | B | C |
|---|---|---|---|
| A0 | **2183** | all | all |
| A1 | **928** | all | all |
| A2 | **928** | all | all |
| A3 | **928** | all | all |
| A4 | **1193** | all | **1193** |
| A5 | **2183** | all | all |
| A6 | **2183** | all | all |
| B1 | all | **928** | **928** |
| B3 | all | **928** | **928** |
| C0 | all | **2172** | all |
| C1 | **2183** | all | all |
| D0 | all | all | all |
| D1 | all | **1707** | all |
| D2 | all | all | all |
| D3 | **1425** | all | **1425** |
| D4 | **1636** | **1707** | all |
| E1 | **937** | all | all |
| E2 | all | **1525** | all |
| E3 | **1202** | **1864** | **1202** |
| E4 | **1843** | **1843** | all |

#### 2. The invariants, on the frozen file and the whole sweep

Cells, of 30618, whose outcome changed; per-rule rewrites summed over the ten rules (306180 (rule, cell) pairs). In brackets: changes the representation did not flag, as a restatement, a conflict, or two routes stating identical evidence.

| | Rewrite | A | B | C | D |
|---|---|---|---|---|---|
| R1 | reverse the rule order | 0 | 0 | 0 | 0 |
| R2 | give every rule a new id | 0 | 0 | 0 | 0 |
| R3 | rename the intentions | **12** (12 unflagged) | 0 | 0 | 0 |
| R4a | an exact copy, in the same route | **19992** (19992 unflagged) | 0 | 0 | 0 |
| R4b | a reworded copy (terms reversed, new id), in the same route | **19992** (19992 unflagged) | 0 | 0 | 0 |
| R4c | a 0.99 copy, in the same route | **19844** (19844 unflagged) | 0 | 0 | 0 |
| R4d | a partial copy (last term dropped), in the same route | **18938** (18938 unflagged) | 0 | **19062** (19062 unflagged) | 0 |
| R4new | an exact copy **declared as a new route** | **19992** (19992 unflagged) | 0 | 0 | **20021** (0 unflagged) |
| R5a | W -> W/2 + W/2, in the same route | 0 | **15210** (0 unflagged) | **13796** (0 unflagged) | **13796** (0 unflagged) |
| R6 | W -> 2W | **19992** (19992 unflagged) | **22520** (22520 unflagged) | **20021** (20021 unflagged) | **20021** (20021 unflagged) |
| R7 | base and positive factors x 2 | **20829** (20829 unflagged) | **23414** (23414 unflagged) | **20869** (20869 unflagged) | **20869** (20869 unflagged) |
| R9a | split by term, every piece in the rule's route | **469** (469 unflagged) | 0 | 0 | 0 |
| R9b | merge co-compatible rules, every statement in its own route | 0 | 0 | 0 | 0 |
| R11 | rename every route key | 0 | 0 | 0 | 0 |

| | A | B | C | D |
|---|---|---|---|---|
| R7: changes toward / **away** from the strengthened intention | 20829 / **0** | 23305 / **0** | 20764 / **0** | 20764 / **0** |
| R8: changes outside where the rewritten rule applies, all per-rule rewrites | 0 | 0 | 0 | 0 |
| R10: cells whose candidates are not the compatible set, frozen file | 243 | 0 | 0 | 0 |
| R4new: cells where D flags two routes stating identical evidence | 0 | 0 | 0 | 78732 |

**R15, provenance**: under D, 30593 of 30593 winning intentions have a trace, from route to evidence to coefficient and sign to the level read, that reconstructs their score to within 1e-9, with every statement naming the rule that stated it.

#### 3. The frozen file under declared routes

| Cells where the outcomes differ | A | B | C |
|---|---|---|---|
| **D** | 25 (25 of them ties D reports) | 660 | 0 |

##### How much the relation and the role judgments move

| Diagnostic | Declared differently | Cells changed | By group |
|---|---|---|---|
| **D-alt** | `standing_in_the_way` / `shielding_from_afar`, and the two authority routes, as alternatives | **1604** | `guard_supplies` in company 378, `look_after` in company 877, `restore_standing` in company 349 |
| **D-enablers** | `answerable_for` honoured as the condition of `owning_the_night` | **91** | `avoid_exposure` in company 91 |

Under D-alt, `look_after -> protect` in company: 45.9 % (D: 86.0 %).

| `took_what_was_not_mine` formed | D | D-enablers |
|---|---|---|
| by a profile believing it is answerable | 4070 | 4070 |
| by a profile holding no such belief | **1185** | **1094** |
| ...of which with zero support, as the only candidate: an intention formed for no reason | 0 | **1094** |

Every cell D-enablers changes is one in which D had a profile without the belief form the theft: 91 of 91. Cells anywhere in which D-enablers forms an intention with zero support: **1094**.

##### What was proven, under D

| | Published for A | D |
|---|---|---|
| Cells with one candidate | 28.6 % | 28.6 % |
| Distinct signatures in company | 56 (64 with the 25 ties reported) | 64 |
| Cells changed by company arriving | 8407 (8412 with ties reported) | 8412 |
| Hunger 0.30 -> 0.95 / a room with no food changed | 0 / 0 | 0 / 0 |
| Replay, 300 profiles x 7 wants rebuilt | exact | 2100 of 2100 |
| Character names in any rule or route | 0 | 0 |
| K >= 2, candidates fixed: a single-attribute move changes the intention | 6.1 % (A here: 6.1 %) | **6.1 %** |

#### 4. Real mornings

**257 real pantry-checks** in 50 baseline mornings, for the wants whose shipped proposals lead to `check_pantry` (`find_out`, `get_food`, `guard_supplies`, `restore_standing`), each matched with every other member of the cast at the same minute of the same morning: **771 pairs**.

| | A | B | C | D | D-alt | D-enablers |
|---|---|---|---|---|---|---|
| The same act carried by different intentions across people | 486 (63.0 %) | 486 (63.0 %) | 486 (63.0 %) | 486 (63.0 %) | 486 (63.0 %) | 486 (63.0 %) |
| Same intention: the person evidence behind it differs | 285 of 285 | 285 of 285 | 285 of 285 | 285 of 285 | 285 of 285 | 285 of 285 |

Under D, of the 285 pairs forming the same intention, the **leading route** differs in **0**, and the person evidence in **285**.

| Real decisions changed against D | 0 | 0 | 0 | 0 | 0 | 0 |

##### Does authoring alone change a real decision, or its stated reason?

Each real pantry-check re-decided with one rule copied, for each of the ten rules (2570 re-decisions per row). "Reason changed" means the same intention with different person evidence behind it, or, under D, a different leading route.

| Rewrite | A: intention / reason changed | C: intention / reason changed | D: intention / reason changed |
|---|---|---|---|
| Copied, same route | 110 / 257 | 0 / 0 | 0 / 0 |
| Partly copied, same route | 110 / 257 | 110 / 257 | 0 / 0 |
| Copied, **declared a new route** | 110 / 257 | 0 / 0 | 110 / 257 |

Of D's changes from a copy declared a new route, flagged as two routes stating identical evidence: **110 of 110**.

##### Real decisions the diagnostics change

| Diagnostic | Real decisions changed, of 1028 | What changed |
|---|---|---|
| D-alt | 0 |  |
| D-enablers | 0 |  |

#### 5. The blind annotation

6 reviewers (#1 opus, #2 opus, #3 sonnet, #4 sonnet, #5 haiku, #6 haiku), each a fresh subagent shown only the items, in the rotated and swapped order the protocol fixes, under neutral ids. **They are language models, not people.** Agreement below is evidence about whether the distinctions are legible and reproducible, and says nothing about whether they are true.

| Item | Source | Declared | Judgments (restatement / different / unclear) | Majority | Matches the key | Q3 (both / one or other / unclear) | Declared Q3 |
|---|---|---|---|---|---|---|---|
| `real_protect` | frozen file: standing_between_them_and_it and keeping_it_off_them | different | 0 / 6 / 0 | different (6 of 6) | yes | 1 / 5 / 0 | both |
| `real_assert` | frozen file: pulling_rank_needs_an_audience and being_the_one_who_decides_it | different | 0 / 6 / 0 | different (6 of 6) | yes | 2 / 4 / 0 | both |
| `real_take` | frozen file: somebody_has_to_do_it and doing_it_where_nobody_is_watching | different | 0 / 6 / 0 | different (6 of 6) | yes | 4 / 0 / 2 | both |
| `real_prevent` | frozen file: not_making_a_scene_of_it and letting_it_go_for_now | different | 0 / 6 / 0 | different (6 of 6) | yes | 1 / 5 / 0 | both |
| `syn_restate_protect` | synthetic family A | restatement | 6 / 0 / 0 | restatement (6 of 6) | yes | - | - |
| `syn_critical` | synthetic family B, the critical pair | different | 0 / 6 / 0 | different (6 of 6) | yes | 6 / 0 / 0 | both |
| `syn_alternative` | synthetic family E, competing routes | different | 0 / 6 / 0 | different (6 of 6) | yes | 0 / 6 / 0 | one_or_other |
| `syn_roles` | synthetic family E, opposite roles | different | 0 / 6 / 0 | different (6 of 6) | yes | 0 / 6 / 0 | both |
| `control_same` | control: word for word the same | restatement | 6 / 0 / 0 | restatement (6 of 6) | yes | - | - |
| `control_different` | control: different meaning and different facts | different | 0 / 6 / 0 | different (6 of 6) | yes | 6 / 0 / 0 | both |
| `syn_restate_assert` | synthetic family A, a second restatement | restatement | 5 / 0 / 1 | restatement (5 of 6) | yes | - | - |

| | |
|---|---|
| Majority judgment matches the key | **11 of 11** two-reason items |
| Fleiss' kappa, judgment (restatement / different / unclear), 11 items | **0.925** |
| Fleiss' kappa, Q3 (both / one or other / unclear), the 8 items declared different | **0.592**; mean share agreeing with the item's majority 87.5 % |
| Q3 majority matches the declared relation | **4 of 8** items declared different. Not matching: `real_protect` (declared both, majority one_or_other 5 of 6); `real_assert` (declared both, majority one_or_other 4 of 6); `real_prevent` (declared both, majority one_or_other 5 of 6); `syn_roles` (declared both, majority one_or_other 6 of 6) |
| Q5, the role item (`real_role`): precondition / contributing / unclear | 6 / 0 / 0 (declared: precondition) |

##### Q4, verbatim: what an explanation would need to show

**`real_protect`**

- #1 opus: Whether the protected person is present. Reason 1 needs someone there to stand in front of, and Reason 2 applies only when they are absent. Also whether safety and anxiety, or closeness, did the work.
- #2 opus: It would need to show whether the protected person is present. Reason 1 applies when they are absent, Reason 2 when someone is there to stand in front of. Also, only Reason 2 draws on family safety and anxiety.
- #3 sonnet: Show whether the protected person was physically present at the moment of threat (interposition, anxiety-driven) or absent and unaware of it (shielding from something at a distance) — the two situations are mutually exclusive.
- #4 sonnet: Establish whether the protected person was actually absent from the threatening thing (shielded from it) or present alongside the danger (protector interposed bodily) — the two reasons describe incompatible situations, so only one can be true.
- #5 haiku: An explanation must show whether protection occurs through direct intervention (standing between danger and person) or through prevention (keeping person absent from danger).
- #6 haiku: Clarify whether both describe preventive shielding or if one involves physical intervention. Show if the person chooses between these or acts from both.

**`real_assert`**

- #1 opus: Whether anyone was watching, and which facts were active: pride and dominance with witnesses for Reason 1, anger with or without witnesses for Reason 2. Both reasons draw on control and believing they lead, so those cannot separate them.
- #2 opus: It would need to show whether anyone was watching, and whether anger or dominance and pride drove it. It would also need to settle Reason 2's claim that settling things with no audience is housekeeping, not authority.
- #3 sonnet: Show whether an audience was present and doing motivational work (pride, dominance on display) or absent, with the act instead driven by pre-existing anger and private entitlement to decide — the two need different conditions.
- #4 sonnet: Establish whether anyone else was present to witness the act: the private, no-audience version fits anger plus role-claiming, while the witnessed version fits dominance and pride — the text makes these mutually exclusive conditions.
- #5 haiku: An explanation must show whether authority needs an audience for validation (performance/pride) or functions independent of audience as a role/responsibility.
- #6 haiku: Show whether authority arises from anger (when alone) or requires an audience. These appear to be alternative triggers.

**`real_take`**

- #1 opus: Whether anyone was watching, and whether honesty, family safety and caution or pride and respect carried the intention. The two reasons share no facts, so the explanation should name which set was high.
- #2 opus: It would need to show whether anyone was watching, and whether pride and respect or honesty, safety and caution carried the decision. It would also need to show whether the 'plainest reading' rules out a self-proving motive or can sit alongside one.
- #3 sonnet: Show whether the self-account rests on a plain, practical duty (a job needing doing, audience-independent) or on privately proving something to oneself (requiring nobody watching) — and whether both were operating together.
- #4 sonnet: Show whether a private need for self-validation (requiring nobody watching) coexisted with the plain practical necessity, or whether the 'plainest reading' is meant to replace the self-proving account entirely rather than supplement it.
- #5 haiku: An explanation would distinguish between honest acknowledgment of one's role and acting for internal self-validation and respect.
- #6 haiku: Show whether taking responsibility stems from internal self-validation, from recognizing duty, or from both factors.

**`real_prevent`**

- #1 opus: Whether the other person is there, meaning a live tension to defuse or an argument avoided in advance. Also whether closeness with low dominance, or anxiety, carried it. Both reasons draw on caution, so it cannot separate them.
- #2 opus: It would need to show whether the other party is present. Reason 1 needs them absent (anxious avoidance), while defusing needs someone there. It would also need to show whether anxiety or closeness drove it, with dominance weakening only Reason 2.
- #3 sonnet: Show whether the other party was present at the moment (avoiding a scene in front of them) or not yet present (preemptively deciding not to confront before the moment arises) — the two differ in timing.
- #4 sonnet: Establish the timing: was the other party simply not yet present (fitting cautious, solitary avoidance) or already present while the person avoided making a scene (fitting closeness-valuing de-escalation against dominance) — these describe different moments.
- #5 haiku: An explanation would distinguish whether prevention occurs through deliberate restraint/non-escalation or through avoiding engagement when opportunity does not yet exist.
- #6 haiku: Clarify whether the person prevents arguments through cautious avoidance or active defusing, and how dominance affects the approach.

**`syn_restate_protect`**

- #1 opus: That there is no difference. Both say that protecting them is one's job, and both draw on the same facts, so no situation or fact could favour one over the other.
- #2 opus: Nothing separates them: both say protecting is their responsibility and cite the same facts. Oddly, those facts are empathy and closeness rather than any sense of duty or role, so the wording and the facts do not match.
- #3 sonnet: Show that both phrasings express the same duty-based reason, with no difference in trigger, trait basis, or resulting behavior — confirming they are one reason stated twice, not two.
- #4 sonnet: Both reasons just restate 'protecting them is my duty/role' in different words from identical underlying facts; the explanation need only establish that one duty-based motive, since nothing marks a second, distinct pathway.
- #5 haiku: Both state the same reason—protection as a responsibility or job the person has taken on.
- #6 haiku: Both express identical reasoning: protection is the person's responsibility/job. No distinction needed.

**`syn_critical`**

- #1 opus: Whether the person acted from duty or from distress at the other's suffering. Both draw on exactly the same facts, so the explanation needs another fact, such as a sense of role or seeing the suffering, to separate them.
- #2 opus: Distress at their suffering and a sense of duty are different reasons, but both cite the same facts. An explanation needs a fact behind the duty reason, such as valuing the family's safety, or the difference cannot be seen.
- #3 sonnet: Show whether the account rests on felt duty ('it's my job') or an involuntary reaction to their suffering ('I cannot bear it') — distinguishing role-based obligation from affect-driven urgency, and whether both operated together.
- #4 sonnet: Show whether the protective act came from an immediate, visceral inability to watch them suffer, from a standing sense that looking after them is one's job, or from both together — identify the trigger versus the standing commitment.
- #5 haiku: An explanation must distinguish whether protection stems from a sense of duty (looking after as a job) or from empathetic response (cannot bear their suffering).
- #6 haiku: Show whether protection stems from emotional empathy, from duty/responsibility, or from both motivations.

**`syn_alternative`**

- #1 opus: Whether the act was done quietly or openly, and what besides pride decides that, such as whether others are there or how much respect is valued. Both reasons draw on pride, so pride alone cannot tell them apart.
- #2 opus: It would need to show whether the act was done in public or in secret, and what the person wanted others to know. Pride drives both, so pride alone cannot tell them apart.
- #3 sonnet: Show which pride-driven motive actually produced the act: wanting the credit to go unseen (quiet) or wanting to be seen as reliable (open) — the two behaviors are opposite and cannot both explain one instance.
- #4 sonnet: Show whether pride here seeks visible credit or a self-image of unacknowledged reliability, and which of these actually shaped the choice between doing it openly and doing it secretly, since the same act cannot be both.
- #5 haiku: An explanation would show what kind of pride drives the person—pride that remains hidden/secure versus pride that requires public witness to validation.
- #6 haiku: Show whether the person takes responsibility for visibility/reliability or to hide caring. These appear contradictory motivations.

**`syn_roles`**

- #1 opus: That one fact, empathy, leads to protecting in one case and blocks it in the other, and what tips the balance, for example how afraid the person is. Reason 2 is a reason against, not another route.
- #2 opus: Reason 1 pushes away from protecting: it is the same empathy leading to freezing. An explanation would need to show which way the empathy went, protecting or freezing, and what tipped it. Reason 1 should not be listed as a route to this intention.
- #3 sonnet: Show whether the empathic arousal resulted in approach (moving to shield them) or inhibition (freezing, holding back) — the same trait produces opposite behaviors, so the explanation must identify which response actually occurred.
- #4 sonnet: Show whether the person's empathy in this instance produced paralysis (no protective act) or converted into protecting — the same trait yields opposite behaviors, so the explanation must identify which output actually occurred.
- #5 haiku: An explanation must clarify what determines whether strong empathy mobilizes the person to protect or instead paralyzes them, preventing action.
- #6 haiku: Show the conditions determining whether empathy paralyzes or motivates protection. These are opposing outcomes.

**`real_role`**

- #1 opus: That the belief gates the route. Without it the intention cannot be reached, however honest, fair-minded or ashamed the person is. Honesty, fairness and shame only add strength once the belief holds.
- #2 opus: It would need to show that the belief of being answerable is in place first. Without it the intention cannot be reached at all. Honesty, fairness and shame only strengthen it once that belief holds.
- #3 sonnet: Show that the belief of being answerable was actually present and doing causal work in forming the intention, not just inferred afterward — distinguishing genuine self-attribution from rule-following or externally assigned blame.
- #4 sonnet: Show the person actually holds this specific belief about their own answerability, as a genuine conviction rather than a general rule or norm merely followed — without it the theft-owning intention is not reachable at all.
- #5 haiku: An explanation would need to distinguish what enables this intention at all (belief in answerability) from what motivates or shapes it (honesty, fairness values, shame felt).
- #6 haiku: Show that this intention depends fundamentally on the person believing they are answerable; without this belief, the intention is unreachable.

**`control_same`**

- #1 opus: Nothing. The two have the same words and the same facts, so this is a duplicate entry. An explanation should present one reason, not two.
- #2 opus: Nothing: the text and the facts are identical, so this is one reason listed twice. An explanation could only show a single route.
- #3 sonnet: Show that the two statements are verbatim identical, drawing on the same traits with no distinguishing trigger, content, or behavior — confirming there is no second reason here, only one restated.
- #4 sonnet: Since the two reasons are identical text drawing on identical facts, nothing distinguishes them; the explanation need only give one motivational account (valuing control, believing they lead the family) to cover both entries.
- #5 haiku: These statements are word-for-word identical. No distinction exists to show.
- #6 haiku: These are identical statements. No distinction needed.

**`control_different`**

- #1 opus: Which fact was high: valuing family safety (shielding out of duty) or empathy (unable to bear their fear). The reasons share no facts, so naming the active fact makes the difference visible. Both may be active at once.
- #2 opus: It would need to show how much empathy and how much valuing the family's safety each contribute. For example: would they still shield with low empathy, or if the person at risk were not family?
- #3 sonnet: Show whether the act would still occur without the family member's visible fear (role-based duty) or without the person's formal responsibility (pure empathic reaction) — and whether both were present and operating together.
- #4 sonnet: Show whether the protective act arose from an immediate emotional reaction to seeing their fear, from a standing sense of duty for family safety, or from both reinforcing each other — trace which actually initiated the act.
- #5 haiku: An explanation must distinguish whether protection stems from a sense of duty (responsibility for family safety) or from empathetic response to another's fear.
- #6 haiku: Show whether the person acts from emotional empathy toward the other, from duty/responsibility, or if both motivations reinforce protection.

**`syn_restate_assert`**

- #1 opus: That there is no difference. Both say the decision is theirs to make, and both draw on the same facts. Only the wording differs, so an explanation should treat them as one reason.
- #2 opus: The only extra in Reason 2 is the premise that a decision is needed. Unless an explanation shows that as a separate fact, the two are the same reason about their rightful place, drawing on the same facts.
- #3 sonnet: Show that both statements pick out the same role-based entitlement to decide, with no difference in trigger, trait basis, or content beyond wording — confirming there is no substantive second reason.
- #4 sonnet: Show whether the act stemmed from pure entitlement ('it's mine to decide') or specifically from the decision being necessary and falling to them ('somebody had to') — otherwise the reworded phrasing may hide identical content.
- #5 haiku: These are restatements—both express that authority/deciding is the person's role to fulfill.
- #6 haiku: Both express the same reason: deciding is the person's place/role. No distinction needed.


#### Z. The files after the whole run

| | sha256 | |
|---|---|---|
| `intentions.json` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | unchanged |
| `causal-routes.json` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | unchanged |

Every rewritten rule set and every representation above lived in memory.

---

## predictions.md

### Causal routes: predictions

Written and committed **before any fixture for this experiment existed**, with
three files that fix everything that could otherwise be fitted to the results:

| File | Fixes |
|---|---|
| `Assets/_Project/Data/Experiments/causal-routes.json` | the route declared for every frozen rule; the synthetic families, rule by rule; the pairs and what each is declared to be |
| `annotation/items.json` | the twelve items shown to reviewers, and the answer key they never see |
| `annotation/protocol.md` | reviewers, order, the prompt verbatim, and the analysis |

Every prediction is marked **analytic** (follows by arithmetic or by
construction; if it fails, the fixture is wrong) or **empirical** (a guess; if
it fails, that is a finding).

#### The question

The intention-representation experiment left one decision open. When two
different reasons for one intention read the same fact about a person, should
that fact count once or twice? It showed that no invariant chooses, and that
the answer moves 660 conclusions.

This experiment asks a prior question: **what information does a
representation need to tell "the same reason written twice" from "two different
reasons that depend on the same fact"?** It does not assume either answer, and
it does not choose among formulas.

#### What is frozen

| | |
|---|---|
| Rule file | `Assets/_Project/Data/Experiments/intentions.json`, sha256 `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92`, hashed at the start and the end |
| Production | nothing under `Fallow.Core`; no production selector, shipped rule, want, candidate generation, action, scoring, belief, emotion, memory or character data |
| New files | experiment-only: the route declarations, the synthetic families and the annotation. No production vocabulary is added |

#### Three things, kept apart

| | What it is | Example |
|---|---|---|
| **Evidence** | a fact about the person or the situation | `trait:empathetic`, `value:control`, `belief:role_claim`, `emotion:anger`, `circumstance:others>=1` |
| **Route** | one declared explanation of why some evidence supports an intention | "I take it on myself to keep them from harm" |
| **Intention** | what the person is trying to accomplish | `protect` |

A **route key** is an experiment-only name for one declared meaning, and
nothing else. It is not a rule id: several rules can carry one route key (a
reason written more than once), and one rule's statements could carry several.
It is not a file position. Renaming every route key consistently must change
nothing, and is tested.

#### The representations

| | Identity it reads | A repeat | Different statements of one fact | Relations between reasons | Negative totals | Ties |
|---|---|---|---|---|---|---|
| **A** | none: anonymous rules (the control, `IntentionSelector` bit for bit) | adds | add | none | a rule weighing <= 0 is discarded | by name |
| **B** | the evidence key, per intention (the base keyed by its gate) | once | once, at the strongest; flagged | none | counted | reported |
| **C** | the reason signature: intention, gate, set of evidence keys | once | once per signature, at the strongest; flagged | none | counted | reported |
| **D** | **the declared route**: every statement is (intention, route, evidence, coefficient, sign, role, provenance) | once within a route | **within one route**: a conflict, flagged, resolved at the strongest; **across routes**: each route keeps its own | declared: **independent** routes both contribute (the default); **alternative** routes, only the stronger operates | counted | reported |

**D in detail.**

- **A route's support** is its base plus one term per distinct piece of evidence
  it states.
- **An intention's support** is the sum of its independent routes, with each
  declared group of alternatives contributing only its strongest member.
- **Roles.** A role is `driver` for a positive coefficient and `inhibitor` for a
  negative one, unless declared otherwise; a declared role that contradicts its
  sign is flagged. `enabler` is a declared role that D records but, in its main
  form, computes additively like any other term (see D-enablers below).
- **Suspicion flag.** D flags two *different* routes for one intention that
  state exactly the same evidence at exactly the same coefficients. It does not
  merge them. It says: *confirm these really are two reasons.*
- **Provenance.** Every statement keeps the rules that stated it, and every trace
  runs from intention to route to evidence to coefficient and sign to the level
  read from the person or the world.

**Diagnostics, not candidates:**

- **D-alt**: D with two pairs of frozen routes declared alternatives rather than
  independent (`causal-routes.json`, `what_if_alternatives`). It measures how
  much the relation judgment moves real conclusions.
- **D-enablers**: D honouring the one declared `enabler`. The frozen rule
  `what_you_did_in_the_night` says its intention is "reachable only by somebody
  who believes they are answerable", so under D-enablers its route contributes
  nothing when that belief is absent. It measures how much the role judgment
  moves real conclusions.
- **G**: a negative control for evidence reuse. G gives each fact only to the
  intention that states it most strongly, so that the reuse test can be seen to
  fail when it should.

#### The synthetic families

Every variant is written out rule by rule in `causal-routes.json`. Each is
evaluated for `look_after`, in company, over the 2,187 sweep profiles. The rivals
are the frozen `so_that_they_know_too` and `not_making_a_scene_of_it`,
unchanged. The focal route `duty` is base 0.10, `trait:empathetic` 0.40,
`value:closeness` 0.25.

| Family | Variants | Declared |
|---|---|---|
| **A** pure restatement | A0 `duty` once. A1 twice. A2 reworded (terms reversed, new id). A3 at 0.99. A4 partly. A5 as two rules, split by term. A6 with its key renamed | all the same reason as A0 |
| **B** different reasons, same facts | B1: `duty` and `compassion`, **identical in content to A1**. B3: B1 reordered, rules renamed, keys renamed | B1 is two reasons; A1 is one reason twice |
| **C** same fact, different intentions | C0: `duty` and `telling_them_gently` (`share_information`: base 0.05, empathetic **0.50**, honest 0.20). C1: `duty` alone | protect's support must not depend on whether empathy also supports sharing |
| **D** several facts in one reason | D0: `guardian`, one reason on empathy, family safety and closeness. D1: three single-fact reasons with the same total. D2: D0 as three rules. D3: D0 partly restated. D4: D1 with one reason restated | D0 = D2 = D3; D1 = D4; D0 and D1 have the same numbers and a different structure |
| **E** same fact, different strength or role | E1: `duty` also stated at empathy 0.30 in the same route. E2: `duty` and `compassion_distinct` (empathy 0.30, family safety 0.35). E3: E2 with the two declared alternatives. E4: `duty` and `overwhelmed` (empathy **-0.20**) | E1 is malformed (one reason, two strengths). E2 is two reasons. E3 is the same two, only one operating. E4 is a driver and an inhibitor |

**What passing means, fixed now:**

| Declared | Passes if |
|---|---|
| same | protect's support is identical in every cell, **and** the representation's explanation is identical (after undoing a declared renaming) |
| different | protect's support differs in some cell |
| structure (D0, D1) | support identical in every cell, **and** the explanation differs |
| malformed (E1) | the representation flags it |
| reuse (C0, C1) | protect's support identical in every cell |

An explanation is each representation's own attribution of the score, without
provenance:

- A: its anonymous rules and their amounts;
- B: evidence and amounts;
- C: reason signatures and amounts;
- D: routes, then evidence and amounts.

#### The theorem, committed in advance

**No representation that ignores rule ids and reads no declared route can pass
the critical pair.** A1 and B1 are the same rule file except for rule ids, notes
and declared routes. A representation invariant to rule ids (R2) that does not
read notes or routes computes the same thing on both. So:

- A treats both as two contributions;
- B and C treat both as one reason;
- only D can treat A1 as one reason and B1 as two.

**Analytic.** If A, B or C passes the critical pair, the fixture is wrong.

#### Predictions

##### P1. The families (analytic)

| Pair | Declared | A | B | C | D |
|---|---|---|---|---|---|
| A0 A1 | same | fail | pass | pass | pass |
| A0 A2 | same | fail | pass | pass | pass |
| A0 A3 | same | fail | pass | pass | pass |
| A0 A4 | same | fail | pass | **fail** (a partial copy is a new signature) | pass |
| A0 A5 | same | fail (the explanation has two rules) | pass | fail (two signatures) | pass |
| A0 A6 | same | pass | pass | pass | pass |
| **A1 B1** | different | **fail** | **fail** | **fail** | **pass** |
| A0 B1 | different | pass | fail | fail | pass |
| B1 B3 | same | pass | pass | pass | pass |
| C0 C1 | reuse | pass | pass | pass | pass |
| D0 D2 | same | fail | pass | fail | pass |
| D0 D3 | same | fail | pass | fail | pass |
| D1 D4 | same | fail | pass | pass | pass |
| D0 D1 | structure | pass (by rule count) | **fail** (its three equal bases collapse into one) | pass | pass |
| A0 E1 | malformed | fail | pass | pass | pass |
| A0 E2 | different | pass | pass | pass | pass |
| E2 E3 | different | fail | fail | fail | pass |
| A0 E4 | different | **fail** (the discard drops the inhibitor) | **fail** (the strongest statement drops the inhibitor) | pass | pass |
| **Passed, of 18** | | **6** | **13** | **11** | **18** |

Four of those are worth stating in words:

- **B cannot hold an inhibitor** that shares evidence with a driver of the same
  intention: its conflict rule keeps the larger magnitude. **A cannot either**,
  because the discard removes a rule that weighs nothing or less.
- **B's base-by-gate identity makes three single-fact reasons with equal bases
  collapse into one base.** This is the untested consequence the representation
  experiment named. Here it is tested.
- **C takes how statements are grouped into rules for how they are grouped into
  reasons.** So it is fooled by a reason written as two rules (A5, D2) as well
  as by a partial copy (A4, D3).
- **G fails C0 C1**, because it moves empathy from `protect` to
  `share_information` (0.50 against 0.40). If it did not fail, the reuse test
  would be toothless.

**Agreement with the declared structure** (D's outcome), per variant, is
reported for A, B and C. *Empirical* in its counts. Analytically: A disagrees
wherever a reason is restated; B wherever two routes share a fact; C wherever a
partial copy or a split appears. None of them can represent E3.

##### P2. The frozen file (analytic unless marked)

| # | Prediction |
|---|---|
| 2.1 | **D reaches the same outcome as C in every cell, and as A in every cell but the 25 real ties**, because every frozen rule is declared its own route and no two are declared alternatives. So D keeps what A and C conclude in the 660 cells where B differed. **By D's declarations, those were cells where B merged two different reasons.** Whether the declarations are right is what the annotation tests |
| 2.2 | D passes the retained invariants on the frozen sweep: R1, R2, R3 (ties reported), R4a to R4d (0), R5 (changed, all flagged), R6 (responds), R7 (0 away), R8 (0 outside), R9a and R9b (0), R10 (0) |
| 2.3 | **R11, route-key renaming**: 0 changes |
| 2.4 | **A copy declared as a new route** behaves exactly like A without the discard: the same 20,021 changes. **And D's suspicion flag fires in every cell where the copy applies**, so the change is never silent. D is only as good as its declarations, and it says so |
| 2.5 | **R15, provenance**: in every cell, the winner's trace, from route to evidence to coefficient to level, reconstructs its score to within 1e-9, and every statement names the rule that stated it |
| 2.6 | D keeps everything proven: 28.6 % single-candidate, blindness 0, exact replay, no character names, fixed-candidate sensitivity 6.1 % |
| 2.7 | *Empirical.* **D-alt moves more than 1,500 cells.** Declaring `standing_in_the_way` and `shielding_from_afar` alternatives takes protect toward the one-best-reason figure (45.9 % in `look_after` in company). Declaring the two authority routes alternatives takes `assert_authority` down in `guard_supplies` and `restore_standing` in company. **The relation judgment moves more conclusions than B's collapse did** |
| 2.8 | **D-enablers changes exactly the cells where an innocent profile (no `answerable_for` belief) formed `took_what_was_not_mine` against a rival**, and nothing else. *Empirical*: between 91 and 182 cells. **Where the theft is the only candidate (`avoid_exposure` alone), the 1,094 innocent profiles still "form" it, now with zero support**, and D-enablers flags each as an intention formed for no reason. That is a question for selection that no representation here answers |

##### P3. Real mornings

The same 50 baseline mornings, 257 pantry-checks and 771 matched pairs.

| # | Prediction | Kind |
|---|---|---|
| 3.1 | D forms the same intentions as A in real pairs: 486 of 771 differ between people | analytic (no real ties expected) |
| 3.2 | Among the 285 pairs forming the same intention, the **leading route** differs in fewer than 20 %, while the evidence differs in all 285 | empirical |
| 3.3 | One rule copied, or partly copied, **within its route**: D changes 0 real intentions and 0 stated reasons, across 5,140 re-decisions | analytic |
| 3.4 | One rule copied **as a new route**: D changes 110 real intentions, like A, and flags every one | analytic |
| 3.5 | D-alt changes 0 real pantry decisions: the real `assert_authority` cases are Daniel's, and he wins with either relation | empirical, weak |
| 3.6 | D-enablers changes at least one real decision: an innocent person forming the theft | empirical |

##### P4. The annotation

| # | Prediction | Kind |
|---|---|---|
| 4.1 | Both controls: 6 of 6 reviewers match the key | empirical |
| 4.2 | Both synthetic restatements: at least 5 of 6 say restatement | empirical |
| 4.3 | The critical pair: at least 5 of 6 say different | empirical |
| 4.4 | Each real pair: a majority says different; the authority pair, which shares two facts, least firmly | empirical |
| 4.5 | Fleiss' kappa for the judgment, over the eleven two-reason items: at least 0.6 | empirical |
| 4.6 | **Q3, whether two different reasons combine or compete: kappa below 0.4.** The relation between reasons is harder to judge than their identity | empirical |
| 4.7 | The competing item (`syn_alternative`): a majority says one or the other | empirical |
| 4.8 | The role item: at least 5 of 6 say precondition | empirical |
| 4.9 | Majority judgments match the key on at least 10 of 11 two-reason items | empirical |

##### P5. The answer, stated in advance

**More explicit causal structure is required.** The critical pair cannot be told
apart by anything computed from the rules' contents.

- **What distinguishes them is a declared route identity.** It is independent of
  rule ids, order, wording and grouping.
- **It is not enough on its own.** A representation also needs the declared
  relation between routes (independent or alternative), and the declared role
  of each fact within a route (driver, inhibitor or enabling condition).
- **Each of these is a modelling judgment.** The data cannot supply any of them.

#### What would decide the verdict

The verdict is about the representation, not about Fallow. Committed now:

| Verdict | If |
|---|---|
| **KEEP** (explicit causal routes, as D defines them) | D passes the retained and the new invariants. A, B and C fail the critical pair. D passes every family. D keeps what was proven. **And** the judgments D needs are reproducible: judgment kappa at least 0.6, Q3 kappa at least 0.4, the majority matching the key on every real pair. **And** no family shows a declared meaning D cannot compute |
| **MODIFY** | D does all it is built for, but a needed piece of causal structure is missing or unreliable: a declared role D's statement form cannot compute (the enabler), a relation judgment reviewers cannot reproduce, or route identities that reviewers do not see as declared |
| **REBUILD** | the intention architecture cannot carry route identity without breaking what is proven: D fails the stage separation, R1 to R10, or generalization |
| **ABANDON** | no representation can tell the critical pair apart, even with declarations |

**My expectation is MODIFY.** The enabler is expected to be both real (it is
the documented "innocent theft" defect) and uncomputable by additive
statements. And the relation between reasons is expected to be poorly
reproducible.

**Not claimed by any outcome:** that any route declaration, relation or role is
psychologically correct. Passing an invariant proves a property of the
representation. Reviewer agreement shows legibility. Neither shows how people
are.

---

## results.md

### Causal routes: results against the predictions

The measurements are in `measurements.md`, generated by `CausalRouteExperimentTests`.
The predictions, the route declarations, the synthetic families, the annotation
items with their answer key and the annotation protocol were committed in
`3780435`, before the fixture existed and before any reviewer was asked anything.

#### Runs

| | |
|---|---|
| Rule file | frozen. sha256 `61e6412e...b099d92` verified at the **start and the end**, unchanged |
| Route declarations | `causal-routes.json`, sha256 `781b776d...c37828a` verified at the **start and the end**, unchanged |
| A against the selector | **0 of 30,618** winners differ; every weight equal to the bit |
| Representations | A (the control), B, C, D; diagnostics D-alt, D-enablers and the negative control G |
| Synthetic families | 20 variants x 2,187 profiles, 18 declared pairs |
| Sweep | 30,618 cells per rule set; 95 rewritten rule sets (9 per-rule rewrites x 10 rules, and 5 whole-file rewrites), all in memory |
| Real mornings | 50 baseline mornings; **257** real pantry-checks, **771** matched pairs, 1,028 real decisions; 2,570 re-decisions for each of three authoring rewrites |
| Annotation | 6 reviewers (2 opus, 2 sonnet, 2 haiku), 12 items; responses saved verbatim in `annotation/responses/` |
| Fixture tests | **7 of 7 pass**, 32.5 minutes |
| Randomness | none |
| Production changes | **none** |

**Three things were decided after the predictions were committed, and are
stated here rather than hidden:**

1. **Before any reviewer ran**, the item ids shown to reviewers were replaced
   by neutral ones (`item-01` to `item-12`, the position in `items.json`). The
   committed ids named the answer (`syn_restate_protect`, `control_same`). Each
   response file records the mapping, the rotation and whether the reasons were
   swapped. Nothing else in the protocol changed.
2. **Before the fixture first ran**, compile and robustness fixes only: route
   keys for R11 are renamed deterministically (`r01`, `r02`, ...) rather than
   by a hash; reviewer answers are read null-safely.
3. **After the reviewer responses had been read, and before the fixture ran**,
   one row was added to the annotation analysis: **whether the Q3 majority
   matches the relation the author declared.** The committed analysis asks only
   for Q3's kappa. The per-item Q3 counts that row summarises are part of the
   committed analysis. The comparison itself is an addition, and the verdict
   below says where it is used.

Nothing in the fixture changed after it ran. Run again inside the full suite (439
tests, 437 pass, the same two known failures), it regenerated `measurements.md`
byte for byte.

#### P1. The families

| Pair | Predicted A / B / C / D | Measured A / B / C / D | |
|---|---|---|---|
| A0 A1 | fail / pass / pass / pass | fail / pass / pass / pass | **PASS** |
| A0 A2 | fail / pass / pass / pass | fail / pass / pass / pass | **PASS** |
| A0 A3 | fail / pass / pass / pass | fail / pass / pass / pass | **PASS** |
| A0 A4 | fail / pass / fail / pass | fail / pass / fail / pass | **PASS** |
| A0 A5 | fail / pass / fail / pass | fail / pass / fail / pass | **PASS** |
| A0 A6 | pass / pass / pass / pass | pass / pass / pass / pass | **PASS** |
| **A1 B1** | **fail / fail / fail / pass** | **fail / fail / fail / pass** | **PASS** |
| A0 B1 | pass / fail / fail / pass | pass / fail / fail / pass | **PASS** |
| B1 B3 | pass / pass / pass / pass | pass / pass / pass / pass | **PASS** |
| C0 C1 | pass / pass / pass / pass | pass / pass / pass / pass | **PASS** |
| D0 D2 | fail / pass / fail / pass | fail / pass / fail / pass | **PASS** |
| D0 D3 | fail / pass / fail / pass | fail / pass / fail / pass | **PASS** |
| D1 D4 | fail / pass / pass / pass | fail / pass / pass / pass | **PASS** |
| D0 D1 | pass / fail / pass / pass | pass / fail / pass / pass | **PASS** |
| A0 E1 | fail / pass / pass / pass | fail / pass / pass / pass | **PASS** |
| A0 E2 | pass / pass / pass / pass | pass / pass / pass / pass | **PASS** |
| E2 E3 | fail / fail / fail / pass | fail / fail / fail / pass | **PASS** |
| A0 E4 | fail / fail / pass / pass | fail / fail / pass / pass | **PASS** |
| **Passed, of 18** | **6 / 13 / 11 / 18** | **6 / 13 / 11 / 18** | **PASS** |

All 72 entries are as predicted.

| # | Prediction | Result | |
|---|---|---|---|
| 1.2 | G, the negative control, fails C0 C1 | fails: protect's support differs in 2,187 cells, the outcome in 845 | **PASS** |
| 1.3 | Agreement with D's outcome, analytically: A disagrees wherever a reason is restated; B wherever two routes share a fact; C wherever a partial copy or a split appears; none can represent E3 | A disagrees on every restatement (A1 to A4, D3, D4, E1). B disagrees wherever two routes share a fact (B1, B3, C0, D1, D4, E2, E3, E4). None agrees with D on E3. **C does not disagree on a split** (A5, D2: full agreement), because a weight-preserving split moves C's explanation, not its support. And **C also disagrees on B1 and B3** (928 of 2,187 agree), because the two declared routes there have one signature. The P1 table itself predicted both; the sentence summarising it did not | **PARTLY** |

#### P2. The frozen file

| # | Prediction | Result | |
|---|---|---|---|
| 2.1 | D equals C in every cell, and A everywhere but the 25 real ties | C: 0 cells differ. A: 25, all ties D reports. B: 660 | **PASS** |
| 2.2 | D passes the retained invariants | R1, R2, R3 0; R4a to R4d 0; R5a 13,796 changed, 0 unflagged; R6 responds (20,021); R7 0 away; R8 0 outside; R9a, R9b 0; R10 0 | **PASS** |
| 2.3 | R11, route keys renamed: 0 | 0 | **PASS** |
| 2.4 | A copy declared a new route: A's 20,021 changes without the discard, and D's flag fires wherever the copy applies | 20,021 changes, **0 unflagged**. The flag fires in 78,732 (rule, cell) pairs. Summed over the ten rules, a copied rule is compatible in 36 (want, circumstance) groups, and 36 x 2,187 = 78,732, so it fires in every one | **PASS** |
| 2.5 | R15: every winner's trace reconstructs its score within 1e-9, every statement naming its rule | 30,593 of 30,593 winners. The other 25 cells are ties, with no single winner | **PASS** |
| 2.6 | D keeps what was proven | 28.6 %; hunger and a foodless room 0 and 0; replay 2,100 of 2,100; no character names; fixed-candidate sensitivity 6.1 %; 64 signatures and 8,412 company changes, the extra over A all from the 25 reported ties | **PASS** |
| 2.7 | *Empirical*: D-alt moves more than 1,500 cells, takes `look_after -> protect` in company to 45.9 %, and moves more than B's collapse did | **1,604** cells (378 `guard_supplies`, 877 `look_after`, 349 `restore_standing`, all in company); 45.9 % against D's 86.0 %; 1,604 > 660 | **PASS** |
| 2.8 | D-enablers changes exactly the innocent-theft cells, *empirically* 91 to 182, and leaves 1,094 zero-support formations | **91**, 91 of 91 innocent, all in `avoid_exposure` in company; **1,094** innocent profiles "form" the theft with zero support as the only candidate | **PASS** |

#### P3. Real mornings

| # | Prediction | Kind | Result | |
|---|---|---|---|---|
| 3.1 | 486 of 771 pairs form different intentions under D, as under A | analytic | 486 (63.0 %), under every representation and both diagnostics | **PASS** |
| 3.2 | Of the 285 same-intention pairs, the leading route differs in fewer than 20 %; the evidence in all 285 | empirical | leading route **0 of 285**; evidence 285 of 285 | **PASS** |
| 3.3 | One rule copied or partly copied within its route: 0 intentions and 0 reasons change under D, across 5,140 re-decisions | analytic | 0 / 0 and 0 / 0 | **PASS** |
| 3.4 | One rule copied as a new route: 110 intentions change under D, every one flagged | analytic | 110; **110 of 110 flagged** | **PASS** |
| 3.5 | D-alt changes no real pantry decision | empirical, weak | 0 of 1,028 | **PASS** |
| 3.6 | D-enablers changes at least one real decision | empirical | **0 of 1,028** | **FAIL** |

**Why 3.6 failed.** In the sweep, the innocent theft is formed against a rival
only in `avoid_exposure` in company (91 cells), and no shipped proposal turns
`avoid_exposure` into a pantry-check. The one pantry want where the theft is a
candidate is `get_food`, and no innocent profile forms it there, in the sweep or
in the real mornings. The prediction asked the sample for a case it could only
contain in `get_food`, where the sweep shows it never happens. It says nothing
for or against the enabler.

#### P4. The annotation

| # | Prediction | Result | |
|---|---|---|---|
| 4.1 | Both controls: 6 of 6 match the key | 6 of 6 and 6 of 6 | **PASS** |
| 4.2 | Both synthetic restatements: at least 5 of 6 say restatement | 6 of 6 and 5 of 6 | **PASS** |
| 4.3 | The critical pair: at least 5 of 6 say different | 6 of 6 | **PASS** |
| 4.4 | Each real pair: a majority says different, the authority pair least firmly | every real pair 6 of 6 different; the authority pair is no less firm than the others | **PARTLY** |
| 4.5 | Judgment kappa at least 0.6 | **0.925** | **PASS** |
| 4.6 | **Q3 kappa below 0.4** | **0.592**; the mean share agreeing with the item's majority is 87.5 % | **FAIL** |
| 4.7 | The competing item: a majority says one or the other | 6 of 6 | **PASS** |
| 4.8 | The role item: at least 5 of 6 say precondition | 6 of 6 | **PASS** |
| 4.9 | Majority matches the key on at least 10 of 11 | 11 of 11 | **PASS** |

**Why 4.6 failed, and what it hides.** The reviewers agree with each other
about how two reasons relate much more than predicted. What they do not agree
with is the author. On the four real pairs, the author declared every relation
`both`. The reviewers' majority said `one_or_other` on three of them:

- `real_protect`, 5 of 6;
- `real_assert`, 4 of 6;
- `real_prevent`, 5 of 6.

They also said `one_or_other` 6 of 6 on `syn_roles`, where the question itself
was ill-posed: it asks whether both reasons "push toward" the intention, and
one of them is an inhibitor. The report, section 9, reads these disagreements
against the frozen rules' gates.

By the protocol's committed rule, nothing is underspecified: no item's majority
has fewer than four of six, and neither kappa is below 0.4.

#### P5. The answer, stated in advance

| Predicted | Result | |
|---|---|---|
| More explicit causal structure is required: a declared route identity; with it, the declared relation between routes and the declared role of each fact; each a modelling judgment | Route identity is necessary: proven by the theorem and measured, A, B and C identical on A1 and B1 in 2,187 of 2,187 cells. The role is necessary: the enabler cannot be written as a term. **The relation, as declared, is not what reviewers read.** Where they said `one_or_other`, they explained it by a circumstance the two reasons are about (who is present, whether anyone watches). One such circumstance, the protected person's absence, cannot be written in the current gate at all. So the answer needs a fourth piece the prediction did not name: **the circumstance each route is about, including whom it is about** | **PARTLY**: right about what is necessary, incomplete about what is enough |

#### Verdict criteria

| Criterion | Measured | Met |
|---|---|---|
| KEEP: D passes the retained and the new invariants | R1 to R11 and R15 as predicted | yes |
| KEEP: A, B and C fail the critical pair | all three, 0 cells differ | yes |
| KEEP: D passes every family | 18 of 18 | yes |
| KEEP: D keeps what was proven | section P2.6 | yes |
| KEEP: judgment kappa at least 0.6; Q3 kappa at least 0.4; the majority matching the key on every real pair | 0.925; 0.592; 4 of 4 | yes |
| KEEP: no family shows a declared meaning D cannot compute | every family is computed; the one declared meaning D cannot compute (the enabler) is in the frozen declarations, not a family, and the MODIFY row names it | see MODIFY |
| **MODIFY: a declared role D's statement form cannot compute (the enabler)** | **D adds the belief as 0.60 x level, like any term. 91 innocent profiles form the theft over a rival because of it. 6 of 6 reviewers read the belief as a precondition. Honouring it (D-enablers) needs a rule D's statements do not have** | **met** |
| MODIFY: a relation judgment reviewers cannot reproduce | the reviewers reproduce one another (0.592) but not the author's declaration, on 3 of the 4 real pairs. *This comparison was added after the responses were read* | met, but used only as a second, post hoc reason |
| MODIFY: route identities that reviewers do not see as declared | 11 of 11 as declared | not met |
| REBUILD: D fails the stage separation, R1 to R10, or generalization | no | not triggered |
| ABANDON: no representation can tell the critical pair apart, even with declarations | D does, in 2,187 of 2,187 cells | not triggered |

**Verdict: MODIFY**, as expected. It rests on the enabler, which the criteria
named in advance. The relation disagreement supports it but is not needed for
it.

#### Not predicted

| Finding | Evidence |
|---|---|
| **The reviewers' relation judgment follows the circumstance each reason is about; the declaration followed the gates.** On `real_prevent` the gates (`alone`, and `others_present_min: 1`) can never both hold, so the declared relation there never computes anything. On `real_protect` the circumstance is about one particular person, which the gate cannot express. On `real_assert` the two texts contradict each other | report, section 9; `Percept.Alone` is `Present.Count == 0`; `SituationCondition` has no field for a particular person |
| **Neither D nor D-alt is what the reviewers describe.** D adds co-active routes and D-alt keeps the stronger. The reviewers describe the route being chosen by the situation, not by its strength | Q4, verbatim, `real_protect`, `real_assert`, `real_prevent` |
| **D's explanation does not say which alternative operated.** E2 and E3 give the same explanation in all 2,187 cells, though protect's support differs in all 2,187. The pair passes, because *different* reads support only. R15 was checked under D, where no alternatives are declared | section 1 |
| **On the frozen file, route identity changes nothing, because each route is exactly one rule.** D equals C in every cell. What routes add shows only under rewriting and in the synthetic families | section 3 |
| **Routes never separate two real people who form the same intention.** Evidence always does: the leading route differs in 0 of 285 pairs and the evidence in 285 of 285 | section 4 |
| **On the critical pair, the two opus reviewers said the difference cannot be seen from the facts cited**, and that an explanation would need a further fact to show it | Q4, `syn_critical`, reviewers 1 and 2 |
| **On the opposite-roles item, the two opus reviewers said the inhibitor is not a route to the intention at all**, but a reason against it | Q4, `syn_roles`, reviewers 1 and 2 |

#### Classification

In the report, section 12, separated into representation properties, causal
semantics and psychological validity, and machine-readable in
`classification.json`.

---

## annotation/protocol.md

### Causal routes: the blind annotation protocol

Committed with the predictions, before any reviewer was asked anything.

#### What it is for, and what it is not

The representation D can tell "one reason written twice" from "two reasons that
happen to read the same fact" only because somebody *declares* which is which.
That declaration is a modelling judgment. This task asks whether the judgment
is **legible** (can others see the distinction from the descriptions?) and
**reproducible** (do independent readers draw it the same way?).

**Reviewer agreement is not truth.** A unanimous panel can be wrong about
people. Agreement is used only as evidence about whether the distinction is
well enough specified to be written down and checked. Poor agreement on an item
is reported as evidence that the route vocabulary, or the description, is
underspecified.

#### Reviewers

Six independent reviewers, each a fresh Claude Code subagent with no access to
this repository's files and no tools used:

| Reviewer | Model |
|---|---|
| 1, 2 | opus |
| 3, 4 | sonnet |
| 5, 6 | haiku |

**They are language models, not people.** They share training and may share
blind spots, so their agreement is weaker evidence than agreement between
independent humans would be. That limitation is reported with the results. A
human panel is the obvious follow-up.

They are never shown the rule ids, the route keys, the answer key, the
experiment's hypotheses, the representations, or each other's answers.

#### Order and orientation

The twelve items of `items.json` are shown in that file's order, rotated left by
2 x (k - 1) for reviewer k. For even-numbered reviewers, Reason 1 and Reason 2
are swapped within every two-reason item. So no reviewer sees the same order,
and position is balanced.

#### The prompt, verbatim apart from the items

> You are helping to check whether descriptions of a person's reasons are clear.
> Each item describes what a person intends and one or two reasons that could
> lead them there, with the facts about the person each reason draws on. Answer
> only from the text given. Do not use any tools and do not read any files.
>
> For each item with two reasons, answer:
>
> - **Q1.** Are Reason 1 and Reason 2 merely restatements of the same reason?
>   `yes`, `no` or `unclear`.
> - **Q2.** Are they genuinely different reasons? `yes`, `no` or `unclear`.
> - **Q3.** If they are different reasons: can both push the person toward the
>   intention at the same time (`both`), or does the person act from one or the
>   other (`one_or_other`)? `unclear` if you cannot tell, `not_applicable` if
>   they are not different.
> - **Q4.** In at most 40 words: what would an explanation of why this person
>   formed the intention need to show, to make the difference between these two
>   reasons visible (or to show that there is none)?
>
> For the item with a single reason, answer:
>
> - **Q5.** Is the fact named in the question a precondition (without it the
>   reason does not apply at all) or one contributing factor among others?
>   `precondition`, `contributing` or `unclear`.
> - **Q4**, as above, about the role of that fact.
>
> Reply with JSON only: an array with one object per item, with the fields `id`,
> `q1`, `q2`, `q3`, `q4` for two-reason items, and `id`, `q5`, `q4` for the
> single-reason item.

The single-reason item's Q5 names its fact: "believing they are answerable for
the missing can".

#### Analysis, fixed now

- **Judgment per reviewer and item**: `restatement` if Q1 is yes and Q2 is no;
  `different` if Q1 is no and Q2 is yes; otherwise `unclear`, which includes
  answers that contradict themselves.
- **Per item**: the majority judgment, its share, and whether it matches the
  answer key.
- **Fleiss' kappa** over the eleven two-reason items, for the judgment (three
  categories) and for Q3 (`both`, `one_or_other`, `unclear`), the latter over
  the items the key declares different.
- **Q5**: the majority, and whether it is `precondition`.
- **Q4**: reported verbatim. Its themes are coded afterwards by the author, and
  that coding is labelled as the author's.
- **Underspecified**: an item where the majority judgment has fewer than four of
  six; a question whose kappa is below 0.4.

The analysis is computed by `CausalRouteExperimentTests` from the saved
responses, so it is reproducible from the files alone.

