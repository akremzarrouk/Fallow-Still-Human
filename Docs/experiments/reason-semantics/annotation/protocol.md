# Reason semantics: the blind annotation protocol

Committed with the predictions, before any reviewer was asked anything.

## What it is for, and what it is not

The representations B and C can distinguish a condition from a push, a
circumstance from a strength, and one relation between reasons from another only
because somebody declares which is which. Those declarations are modelling
judgments. This task asks two things of each one:

- **Is it legible?** Can a reader see the distinction from a plain description,
  without being told the vocabulary?
- **Is it reproducible?** Do independent readers draw it the same way?

**Reviewer agreement is not truth.** A unanimous panel can be wrong about people.
Agreement is evidence only that a distinction is specified well enough to be
written down and checked. Poor agreement on an item is reported as evidence that
the distinction, or its description, is underspecified.

## Reviewers

Six fresh Claude Code subagents, one per reviewer, told to use no tools and read
no files:

| Reviewer | Model |
|---|---|
| 1, 2 | opus |
| 3, 4 | sonnet |
| 5, 6 | haiku |

**They are language models, not people.** They share training and may share blind
spots, so their agreement is weaker evidence than agreement among independent
humans would be. The limitation is reported with the results.

Reviewers are never shown:
- the item ids of `items.json`, its sources or its answer key;
- the experiment's vocabulary (reason, part, condition, circumstance, relation);
- its hypotheses or its representations;
- each other's answers.

Each item is shown under a neutral id, `item-NN`, where NN is its position in
`items.json`.

## Order and orientation

- **Order:** the 21 items are shown in `items.json` order, rotated left by
  3 x (k - 1) for reviewer k.
- **Orientation:** for even-numbered reviewers, Reason 1 and Reason 2 are swapped
  within every two-reason item. Each response file records the rotation and
  whether the reasons were swapped. The analysis maps answers back to
  `items.json` order.
- **Minimal pairs:** the members of each pair (`owning_graded` and
  `owning_conditional`; `settling_graded` and `settling_conditional`;
  `easier_unseen` and `unseen_only`) are 8 to 13 items apart in every rotation,
  and nothing marks them as pairs.

## The prompt, verbatim apart from the items

> You are helping to check whether descriptions of a person's reasons are clear.
> Each item describes what a person intends and one or two reasons that could
> lead them there, with the facts each reason draws on. Some items also describe a
> particular person. Answer only from the text given. Do not use any tools and do
> not read any files.
>
> For every reason in every item, say what part each listed fact plays in THAT
> reason, using one of:
>
> - `pushes`: the more of it, the stronger this reason
> - `holds_back`: the more of it, the weaker this reason
> - `must_hold`: it must be true of the person for this reason to apply at all
> - `situation_needed`: a feature of the situation this reason needs in order to apply at all
> - `situation_strengthens`: a feature of the situation that makes this reason stronger, but is not needed for it
> - `consequence`: something that follows from acting, not a cause of it
> - `no_part`: it plays no part in this reason
> - `unclear`
>
> For each item with two reasons, also answer:
>
> - **Q1.** Are Reason 1 and Reason 2 the same reason (said twice, perhaps in
>   other words), or different reasons? `same`, `different` or `unclear`.
> - **Q2.** If they are different: in a situation where both could apply, how do
>   they relate? `both_add` (both operate, each adding its own push),
>   `one_strengthens_other` (both operate, but one only strengthens the other and
>   would do nothing on its own), `one_or_other` (the person acts from one or the
>   other, not both), `never_together` (they cannot both apply in the same
>   situation), `opposed` (one pushes the person away from what the other pushes
>   toward), or `unclear`. If they are the same, `not_applicable`.
>
> For each item that describes a particular person, also answer:
>
> - **Q5.** Given what is said about this person, could they form this intention
>   at all, in this situation? `yes`, `no` or `unclear`.
>
> For every item:
>
> - **Q4.** In at most 40 words: what would an explanation need to show for you
>   to understand why this person formed the intention (or did not)?
>
> Reply with JSON only: an array with one object per item, with the fields `id`,
> `parts` (an array with one array per reason, in the order shown, each listing
> one answer per fact in the order shown) and, where they apply, `q1`, `q2` and
> `q5`, and always `q4`.

The parts question is called Q3 in the analysis.

## Analysis, fixed now

- **Judgment (Q1).** The majority per two-reason item, its share, and whether it
  matches the key. Fleiss' kappa over the ten two-reason items (`same`,
  `different`, `unclear`).
- **Relation (Q2).** The majority per item the key calls different, and whether
  it matches the key. Fleiss' kappa over those eight items (six categories).
- **Parts (Q3).** The majority per (item, reason, fact) slot and whether it
  matches the key. Fleiss' kappa over all slots (eight categories). A confusion
  table of the key's part against the majority's part. The one pre-registered
  ambiguous slot (`answer_key.ambiguous_slots`) is excluded from both, and
  reported on its own.
- **The minimal pairs**, reported on their own:
  - the belief in the two `owning` items: `pushes` in the graded one, `must_hold`
    in the conditional one;
  - the belief in the two `settling` items: the same;
  - watching in `easier_unseen` (`situation_strengthens`) against `unseen_only`
    (`situation_needed`).

  A pair is **discriminated** when both majorities match the key.
- **Reachability (Q5).** The majority per item and whether it matches the key.
  Fleiss' kappa over the four items (three categories), reported with the warning
  that four items make it unstable.
- **Q4.** Reported verbatim. Its themes are coded afterwards by the author, and
  that coding is labelled as the author's.
- **Underspecified.** An item or slot whose majority has fewer than four of six;
  a question whose kappa is below 0.4.

The analysis is computed by `ReasonSemanticsExperimentTests` from the saved
responses, so it can be reproduced from the files alone.
