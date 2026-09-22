# Causal routes: the blind annotation protocol

Committed with the predictions, before any reviewer was asked anything.

## What it is for, and what it is not

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

## Reviewers

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

## Order and orientation

The twelve items of `items.json` are shown in that file's order, rotated left by
2 x (k - 1) for reviewer k. For even-numbered reviewers, Reason 1 and Reason 2
are swapped within every two-reason item. So no reviewer sees the same order,
and position is balanced.

## The prompt, verbatim apart from the items

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

## Analysis, fixed now

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
