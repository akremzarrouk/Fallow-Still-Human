# Intention formation: predictions

Written and committed **before a single case was run**, together with the
candidate rule file they are about. Kept as written.

## The question

> Can Fallow derive a context-sensitive intention from an existing motivation
> without relying on a universal hardcoded Want -> Intention mapping?

## The three things kept apart

| | | Example |
|---|---|---|
| **Motivation** | what the person is currently driven toward | `restore_standing` |
| **Intention** | what they take themselves to be accomplishing | `assert_authority` |
| **Physical action** | what they actually do | `check_pantry` |

The previous experiment proved the third is independent of the second. This one
tests whether the second is independent of the first.

## How the candidate mechanism was authored, and when

The rules were written **blind**: from the shipped character sheets, the shipped
rule files and the shipped vocabulary, and from nothing else. No case of any
kind had been run, so no output could be fitted. The rule file is committed in
the same commit as this document and was not edited afterwards. Every case in the
experiment is therefore held out from authoring.

Whether that discipline held is checkable: `git log -p` on
`Assets/_Project/Data/Experiments/intentions.json` should show one commit, dated
before the fixture that reads it.

## The mechanism, stated before it was run

A **candidate rule** says that a given intention is *available* to a given set of
wants, in given circumstances, with a weight that depends on the person.

```
{ id, motives: [...], intent, when: { circumstances only }, base, scaled_by: [...] }
```

Three properties are structural, not promises:

1. **`when` cannot ask about the person.** It is the shipped `SituationCondition`,
   which has six fields, all circumstantial (alone, in my own room, in somebody
   else's, the room holds food, I have searched here, how many others are
   present). It has no field for a trait, a value, a feeling or a need. That is
   not a rule I am following; it is the type.
2. **Everything about the person is a scaler**, evaluated by the shipped
   `ScalerEval` — the same code that weighs an interpretation rule and prices an
   action. Traits, values, beliefs, the ledger, live emotions, memories,
   perceptiveness, bodily need.
3. **No randomness anywhere.** The winner is the heaviest intention, ties broken
   ordinally. Any variation observed is therefore attributable to context or to
   the person, and to nothing else.

Rules speaking for the same intention add up, exactly as interpretation rules
speaking for the same reading do. If nothing matches, the mechanism returns
**null** and the act carries no intention, which is the shipped behaviour.

## What is hand-authored, stated plainly

The `motives` list on each rule is a hand-authored table of **which intentions a
want may express**. I am not going to pretend otherwise. The claim being tested
is that it is a **constraint** table and not a **mapping** table, and that claim
is falsifiable in two ways, both of which are measured:

- if any want under test has only one reachable intention, it is a mapping;
- if any want produces the same intention in every context and for every person,
  it is a mapping in effect even if not in form.

The rule count, and the number of intentions each want can reach and does reach,
are reported as measurements rather than asserted.

## Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | Motivation does not uniquely determine intention: the same want under different contexts produces different intentions | every want yields one intention everywhere |
| P2 | Context matters: changing one contextual factor, with motivation and person unchanged, changes the intention | no contextual change ever moves it |
| P3 | Person matters: two characters with the same want in the same circumstances form different intentions | all four characters agree everywhere |
| P4 | Motivation still constrains: no want produces an intention outside the set its rules allow | an unrelated intention appears |
| P5 | The same intention serves different motivations | each intention is reachable from one want only |
| P6 | Intention stays distinct from action: one physical action still carries different intentions | the action determines the intention |
| P7 | No universal Want -> Intention lookup is needed: at least two wants are observed producing two or more different intentions in live mornings | every want is single-valued in practice |
| P8 | Reproducible: same state, same seed, same intention, every time | any run differs |
| P9 | Counterfactually sensitive in the right places: a change to something a rule reads can change the intention; a change to something no rule reads never does | an irrelevant change moves it, or no relevant change does |
| P10 | Generalises: the rules were authored blind, so every live morning is a held-out case. They should produce intentions across wants and people without an empty or degenerate result | most decisions get no intention, or one intention dominates everything |

**Controls, all of which must hold:**

| | Control |
|---|---|
| C1 | With the selector off, the morning is identical to the shipped baseline |
| C2 | With the selector installed but returning null, identically so |
| C3 | Same state and seed replayed gives the same intention |
| C4 | A perturbation of an unread circumstance changes nothing |
| C5 | The same probe run for four different characters |
| C6 | Every live morning is held out from authoring |

**Committed in advance, and riskier:**

- The clearest contrast should be **`restore_standing` with an audience against
  `restore_standing` alone**, for Daniel. Pulling rank needs somebody to pull it
  on. I expect `assert_authority` with company and `take_responsibility` alone.
- **Daniel and Leo should disagree** on `restore_standing` in identical
  circumstances — Daniel dominant 0.85 and holding `role_claim(daniel,
  leads_family)` at 0.80; Leo dominant 0.35, honest 0.80, and holding no such
  claim.
- I expect **`share_information` and `protect` to be reachable but rarely to
  win**, because the wants that can express them are not the wants that dominate
  these mornings.
- I expect the experiment to be **limited by the vocabulary, not by the
  mechanism**. Six intentions exist. The brief's own examples for
  `restore_standing` — demonstrate competence, avoid appearing weak, quietly
  prove themselves right, seek recognition — are four distinctions that the
  shipped vocabulary cannot make. If the result is thinner than the hypothesis
  deserves, I expect that to be why.

**What would count as failure**, in the brief's own terms: a constant mapping
(P1, P7 falsified) or arbitrary output (P8, P9 falsified). Both are measured
directly rather than judged by whether the intentions sound human.
