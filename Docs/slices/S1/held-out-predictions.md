# S1 held-out predictions

**Written before the held-out condition was ever run.** The rules in
`decisions.json` were written and tuned against one variant only,
`daniel_ate_it`, and against nothing else. At the time of writing this file no
other variant has been executed even once, and the rules are frozen from here.

The git history is the evidence: this file is committed before the commit that
adds the held-out test, and `decisions.json` is not touched again in between.

## The held-out condition

`elena_fed_mara`. Mara was awake and crying in the night; Elena opened a can and
gave it to her. Two people know and neither will say. Elena is the one who took
the food, and she does not think of herself as having done anything wrong.

This condition was chosen because it is the one that most nearly inverts the
condition the rules were written against. In `daniel_ate_it` the person who took
the food is ashamed. Here the person who took the food acted protectively and
another person shares the secret. Nothing in the rules was written with either of
those in mind.

## Predictions

Each one is checked automatically. The result is recorded whether it passes or
not, and nothing is tuned afterwards.

**H1. Elena does not come out of the night ashamed.** Her intention was to
protect her daughter. Shame follows from having taken what was not yours, and she
does not hold her own act under that description, so she should carry anxiety
rather than shame.

**H2. Elena never tries to make herself scarce.** With no shame, the want that
makes a person leave the room should stay near zero for her all morning
(under 0.10 at every decision she takes).

**H3. The same want does fire for the guilty brother in the condition the rules
were written against**, so that H2 means something. In `daniel_ate_it`, Daniel
should exceed 0.30 on it at some point.

**H4. Daniel investigates at least as hard when he is innocent.** In
`elena_fed_mara` he carries no shame competing with wanting to know, so he should
search at least as many rooms per morning, on average, as he does in
`daniel_ate_it`.

**H5. Knowing the truth changes nothing about what Mara does.** This is a
prediction of failure, stated in advance. Mara witnessed the whole thing and is
the only person besides Elena who knows, but she is not guilty and this slice
gives her no way to act on knowledge. Her morning should look much like her
morning in `miscount`, where nothing happened at all: the two profiles should
differ by less than 0.35. If the architecture is honest, secret knowledge with no
outlet is invisible, and the slice should say so rather than pretend otherwise.

**H6. The four of them stay four people in every condition.** Mean pairwise
difference between action profiles above 0.30 in all five variants, including the
three the rules never saw.

## What a failure would mean

- H1 or H2 failing means the emotional consequences of an act are being read off
  the act rather than off what the person took themselves to be doing, which
  would be the model reaching for the outcome instead of the cause.
- H4 failing means guilt and curiosity are not actually competing, and the
  decision layer is not doing the work the design claims.
- H6 failing in a variant the rules never saw means the differences between these
  four people were fitted to one condition and do not generalise.
- H5 failing would be a pleasant surprise and would need explaining, not
  celebrating: there is no mechanism in S1 by which it should pass.
