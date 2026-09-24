# Route applicability: protocol

Committed with the predictions, before the fixture existed and before any
reviewer was asked anything.

## The question

*What causal information must a route contain to decide whether it applies in
the current situation, before its supporting and inhibiting evidence is
combined?*

This is a representation experiment. Nothing is implemented in production.

## What is frozen

Every file below is sha256-checked by the fixture at the start and at the end of
its run.

| File | sha256 | Role |
|---|---|---|
| `Assets/_Project/Data/Experiments/intentions.json` | `61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92` | the frozen candidate rules |
| `Assets/_Project/Data/Experiments/causal-routes.json` | `781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a` | the causal-route declarations, its 20 synthetic variants and 18 pairs |
| `Assets/_Project/Data/Experiments/held-out-people.json` | `0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131` | the 2,187-profile sweep |
| `Assets/_Project/Data/Experiments/reason-semantics.json` | `5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638` | the previous experiment's cases (not read; frozen) |
| `Assets/_Project/Data/Experiments/route-applicability.json` | `a0e965403d21a218ae63d3857acf0edaabf159f7603448b1b8a304257c8ce426` | this experiment's cases, reading rules and families |
| `Assets/_Project/Tests/EditMode/CausalRouteExperimentTests.cs` | `3fb852f2cb7763a44d331b62e0c8897e720228ff5cd2b32fbf177908039212c4` | D, its 18 families, the critical pair and the rewrite and provenance tests, **unchanged** and still run by the suite |
| `Assets/_Project/Tests/EditMode/ReasonSemanticsExperimentTests.cs` | `4bc51cbd4b0f3069de99845c9ef693fab1a482b82683e97c8b370aaf7f1c6d79` | the previous experiment, unchanged and still run |
| `Assets/_Project/Tests/EditMode/IntentionSelector.cs` | `8553b74ff0189f4be5cb10e2fded0a9d7c37268bf46eca3d42e3785b23f39cfd` | the experimental selector S, unchanged |

**Nothing in production changes:**
- not `Fallow.Core`, the selector's behaviour, the shipped rules, or character
  data;
- not beliefs, emotions, memories, actions or scoring.

The two failures S1.4 left (the pacing gate and the emergent-moment fading
check) must stay exactly as they are.

**"No Unity changes"** is read as: nothing in the game's Unity content or
runtime changes. As in every earlier experiment, the fixture is an EditMode
test under `Tests/EditMode`, run through the Unity test runner. It adds no
scene, asset or runtime code.

## Three things kept apart

| Layer | Question | Judged by |
|---|---|---|
| **Route layer** | does this route apply now, for this person, and how strong is it? | the families' checks |
| **Selection layer** | what does the deliberator choose, especially when no candidate has an applicable route? | reported under two policies, never judged |
| **Legibility** | do blind readers draw the same distinctions? | the annotation, reported as legibility only |

## Representations

The fixed reading rules are in `route-applicability.json`, under `reading_rules`.

| | Route identity | Typed roles (support, inhibitor, condition) | Applicability from declared circumstances | Circumstances can name the target | Where "does not apply" is recorded |
|---|---|---|---|---|---|
| **S** shipped selector (control) | no | no | no (shipped gates) | no | the discard, rule by rule |
| **A** D, unchanged | yes | recorded, not computed | no (shipped gates) | no | the candidate set (gates) |
| **B** typed roles | yes | yes | no (shipped gates) | no | gates, and conditions at the route |
| **C** applicability layer | yes | yes | yes, one construct for conditions and circumstances | yes | the route |
| C-entity (ablation) | yes | yes | yes | **no** | the route |
| C-conditions (ablation) | yes | **conditions read as weights** | yes | yes | the route |
| C-split (ablation) | yes | yes | conditions and circumstances **as separate constructs** | yes | circumstances at the candidate set, conditions at the route |
| C-kind (counterexample) | yes | **inferred from the kind of fact**, not declared | yes | **every presence bound to the target** | the route |

- **B, C and the ablations do D's arithmetic** once a route applies: restatement
  counted once, conflicts flagged, alternatives where declared.
- **An inhibitor is additive and is never floored.** A route's strength may be
  zero or negative, and that is reported, not corrected.
- **A condition, where it is read as one, adds no strength.**

## Selection policies

Neither policy is part of any representation.

- **P0, current:** the largest support among the candidates wins. A candidate
  with no applicable route has support 0 and can still win.
- **P1, active only:** only candidates with at least one applicable route may
  win; otherwise, no intention.

## The evaluation space

- **Profiles:** the 2,187 sweep profiles.
- **Situations:** six presence sets:
  - n0: nobody;
  - n1: Mara;
  - n2: Daniel;
  - n3: Elena;
  - n4: Daniel and Elena;
  - n5: Mara and Daniel.
- **Cells:** 2,187 x 6 = **13,122 per case and condition**.
- **Target:** each want's target is its motive target. Presence and targets are
  real Percept and Motive data.
- **Holding everything else fixed:** where a family varies one fact (a
  prerequisite, a support, an inhibitor), the fact is overridden in every cell,
  and everything else is left as it is.

The families (A to J), their cases and what passing means are in the JSON,
under `families`, and summarised in `predictions.md`.

## Metrics

Every count is reported with its denominator.

| Metric | Definition |
|---|---|
| **cells** | profile x situation x condition x case, per family |
| **false activation** | the representation says the route applies; the declared meaning says it does not |
| **false suppression** | the reverse |
| **error rate** | (false activations + false suppressions) / route-cells, per family. Percentage points are differences in this rate |
| **applicability change** | along a family's varied fact or situation, the route switches between applying and not |
| **strength-only change** | along the varied fact, the strength changes and applicability does not |
| **selection change** | the chosen outcome differs, under P0 or P1, between the family's conditions or from C's |
| **no-active-route case** | a candidate with no applicable route |
| **invariant violation** | a change where the family requires none (E: applicability; F: applicability or the route set; H: anything; I: anything but a declared new route) |

**Aggregates.** No figure here measures psychological validity. Any aggregate
percentage names what it counts.

## Real-morning regression

This uses the same 50 baseline mornings as the causal-route experiment:
- **257 real pantry-checks**, with every other cast member at the same moment:
  **1,028 real decisions**;
- **every decision moment asked about every want** (live cells).

Each is decided under S, A, B, C and C-split, with the frozen file read by the
committed `frozen_reading`, and under P0 and P1. The fixture reports:
- decisions changed by B, and by C;
- decisions whose explanation changed while the chosen intention did not;
- decisions whose chosen intention changed;
- whether any decision differs from A, the causal-route experiment's
  representation. Any such decision is listed as a possible regression.

The explanation compared is the chosen intention's applicable routes, with
their evidence and amounts and their satisfied conditions.

## The blind annotation

**Reviewers.** Six fresh Claude Code subagents: 1 and 2 opus, 3 and 4 sonnet, 5
and 6 haiku. They use no tools and read no files. **They are language models,
not people.** Human reviewers were not available to this experiment. Their
agreement is reported as legibility and reproducibility only, never as
psychological validation. A human panel is the recommended follow-up.

**Material.** Each reviewer sees the 16 items of `annotation/items.json` under
neutral ids (`item-NN`, the position in the file), rotated left by 3 x (k - 1)
for reviewer k. They never see the ids, sources, answer key, vocabulary or
representations. No item says which representation produced it.

**The prompt, verbatim apart from the items:**

> You are helping to check whether descriptions of a person's reasons are clear.
> Each item gives something a person might intend, one reason that could lead
> them there with the facts it draws on, and a moment: who is present and what is
> true of the person. Answer only from the text given. Do not use any tools and
> do not read any files.
>
> For each item answer:
>
> - **Q1.** In this moment, does the reason apply to this person? `yes`, `no` or
>   `unclear`.
> - **Q2.** In at most 30 words: what makes it apply, or not?
> - **Q3 to Q6.** For each listed fact, in order, what part does it play in the
>   reason? `prerequisite` (it must hold for the reason to apply at all, and it is
>   something about the person), `supporting` (the more of it, the stronger the
>   reason), `inhibiting` (the more of it, the weaker the reason),
>   `circumstance` (a feature of the situation that must hold for the reason to
>   apply at all), `no_part`, or `unclear`.
> - **Q7.** Does whether the reason applies depend on a particular person or
>   thing being present? Answer `person:NAME` for a particular person, `anyone`
>   if anyone at all would do, `none` if no feature of the situation matters, or
>   `unclear`.
> - **Q8.** If the fact named for this item changed, should the reason
>   `disappear`, become `weaker_or_stronger`, or show `no_change`? Or `unclear`.
> - **Q9.** Only where the item says this is the person's only reason: is the
>   intention still causally supported for this person, in this moment? `yes`,
>   `no` or `unclear`.
>
> Reply with JSON only: an array with one object per item, with the fields `id`,
> `q1`, `q2`, `facts` (one answer per listed fact, in order), `q7`, `q8`, and
> `q9` where it is asked.

**Analysis, fixed now.**
- For Q1, the facts, Q7, Q8 and Q9: the majority per item or slot, whether it
  matches the key, and Fleiss' kappa over the items or slots it applies to.
- **Is the condition/circumstance split legible?** For the belief slots against
  the presence slots:
  - do readers label them `prerequisite` against `circumstance`;
  - and do they give both the same Q8 answer (`disappear`)?

  Different labels with the same Q8 is evidence of two names for one behaviour.
  Different Q8 answers is evidence of two behaviours.
- **Target or generic:** Q7 on the `side_*`, `scene_*` and `target_daniel`
  items.
- **Applicability or strength:** Q8 on the support, inhibitor and prerequisite
  items.
- **Applying with zero support:** Q1 and Q9 on `zero_support`.
- **Q2 and the Q4-style free text** are reported verbatim, and any coding is
  labelled as the author's.
- **Underspecified:** a majority of fewer than four of six, or a kappa below
  0.4.
