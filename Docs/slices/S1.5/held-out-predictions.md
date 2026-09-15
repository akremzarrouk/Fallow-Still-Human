# S1.5 hypothesis, the alternative, and held-out predictions

Written and committed after the diagnosis (`e6e469c`) and **before any code for the
alternative exists**. Nothing below has been run.

## Hypothesis

Traits and values do not have to behave like wants that are always on. They may be
better represented as dispositions: they shape how strongly a person responds when
something relevant has happened, rather than generating a standing want of their own.

## A: current

`urgency = Σ level × factor` over every scaler of the rule, then the knee. A trait or value
term adds the same amount at every decision, whatever is happening.

## B: the alternative

For each motivation rule, split its terms by kind:

- **C, what the rule responds to:** every term that is not a trait, value or
  perceptiveness. That is needs, memories, feelings, beliefs (evidenced or authored),
  ledger entries, and the rule's base.
- **D, the disposition:** the sum of the trait, value and perceptiveness terms, as they
  are now.

`urgency = C × (1 + D)`, then the knee. If C is zero, the want is not raised.

In the trace, each disposition term's amount becomes its level × factor × C. The terms of a
want still add up to its urgency, and the description says what it responded to.

Why this form:
- **No new number.** Every factor is the one already in `decisions.json`.
- **With no disposition, the circumstance alone:** D = 0 leaves C unchanged.
- **Nothing happened, nothing wanted:** C = 0 raises nothing.
- **A small circumstance gets a small response.** The diagnosis found memories never fade to
  zero within a morning. A gate would switch the whole standing part back on after any
  memory; this form does not.

**Deliberately not dispositions:** authored beliefs (`role_claim`), evidence-backed beliefs
(`supplies_short`) and ledger entries stay in C. The hypothesis is about traits and values.
Whatever standing wants remain under B, and what they rest on, is part of the result.

Selected by one setting, `deciding.dispositions`: `standing` (A, the default, which the
shipped rules keep) or `respond` (B). Removing the setting restores A exactly.

## B0: an attribution ablation, not a candidate

`gated`: A's arithmetic, but a rule with C = 0 raises nothing. It separates "no want
without a circumstance" from "the disposition scales the response". It is declared here so
that it cannot be chosen afterwards for its numbers.

## Not changed

Perception, memory, beliefs, emotions, relationships, `PursuitOutcome`, `steady`,
`reassurance`, `until`, presence checks, intentions, food and eating, movement, every
proposal, every cost, standing still, deliberation, and every number in the rule files.
No new want.

## Measured, A against B (and B0), with the same instrument

1. Wants raised by support (from circumstance, mostly disposition, unsupported), and urgency
   by source.
2. Standing still: share of choices, and share of decisions where it came top.
3. `look_after` decisive rate, and every other want's.
4. Pacing: mean and worst.
5. Completed walks followed by something the walk's want did not serve.
6. Different-person gap: mean, weakest condition, closest pair.
7. Same-person counterfactual: the night against no night, against the noise floor (the
   S1.1 measure).
8. Ties between genuinely different actions.
9. Food: mornings anyone ate, walks to the food given up on arrival, and meals where
   food is plenty.
10. Removing a relevant circumstance: nobody's distress can be seen; the count does not
    come up short. Does the behaviour that circumstance drives go with it?
11. Trace completeness: wants, and urgency, resting on something that happened.
12. With nothing happening (diagnosis section 4): what each person wants and does.

## Held-out condition

`leo_ate_it`, **seeds 101 to 140**. No test has run a seed above 80.

## Predictions for `leo_ate_it`, seeds 101 to 140

Structural (they check the mechanism does what it says, on cases not used to build it):

- **P1.** Under B, no want is raised on traits and values alone. Every unsupported want
  under B has an authored belief behind it. Under A, at least 30 % of wants are unsupported.
- **P2.** Under B, at least 90 % of wants raised rest on at least one term leading back to
  something that happened, or to the body. Under A, at most 70 %.
- **P3.** With nobody's distress visible, under B every `look_after` raised rests on ledger
  history about that person. Under A, `look_after` is raised about every person present at
  every decision.

Behavioural (I do not know these, and a miss is reported as a miss):

- **P4.** With nobody's distress visible, sittings under B fall to at most half of B's
  sittings with distress visible. Under A they stay above half of A's.
- **P5.** Standing still is a smaller share of choices under B than under A.
- **P6.** Ties between genuinely different actions are more frequent under B than under A.
  With less appeal behind anything, more options tie at nothing.
- **P7.** People do not collapse together under B. The closest pair is further apart than
  under A, and the mean different-person gap is at least A's minus 0.05.
- **P8.** Nobody eats under either A or B. Walks to the food given up on arrival are at
  least as many under B as under A.
- **P9.** Leo's night moves his behaviour further above the noise under B than under A
  (effect ÷ larger noise; pools of seeds 101–120 and 121–140).

No rule, factor or formula will be changed after these are run.
