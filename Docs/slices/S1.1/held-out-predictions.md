# S1.1 held-out predictions

**Written before `leo_ate_it` has been run even once.** The condition was defined
in commit `160dc2d`, before any S1.1 change to the simulation. The rules were frozen
in commit `06d92eb`. This file is committed after that and before the held-out test
exists. The git history is the evidence of the order.

Nothing below says what Leo should do. Each prediction is about how the changed
night travels through the pipeline, and each was worked out by hand from the rule
files and Leo's character file, not by running anything.

## The condition

In the night Leo eats the can. Nobody sees. He is the most honest person in the
house (honest 0.80), holds family safety first and fairness second, and is the least
anxious (anxious 0.25). The design conditions used a culprit who was proud and
anxious (Daniel) and one who was young and very anxious (Mara). Leo is neither.

## What the rules imply, worked out by hand

| Stage | Leo | Compared with the design culprits |
|---|---|---|
| Night shame | 0.10 + 0.48 + 0.30 + 0.35 = 1.23 raw, **about 0.71** | Daniel about 0.44, Mara about 0.47 |
| Night fear | 0.10 + 0.13 + 0.13 = 0.35 raw, **about 0.30** | both about 0.47 |
| Reading of the opening count | threat 0.90 beats concern 0.60 | same as the design culprits |
| Fear from reading it as a threat | about 0.28 | Mara about 0.51 |
| Anxiety from reading it as a threat | about 0.60 | similar to reading it as a problem |

For a person this calm, being threatened and being worried come out almost the same.
So the belief that recolours the search should do little for Leo, while the night
shame should do a lot at first and then fade like any feeling.

## Predictions

**P1. Shame, not fear.** Coming out of the night, Leo carries more shame than fear,
and more shame than either design culprit carried in the same place.

**P2. A large change at the start.** At minute zero, `avoid_exposure` is higher than
in his no-night control by more than the design culprits' rises (+0.21 and +0.23),
and the rise is traceable to the night.

**P3. The same supply belief.** At minute zero, `guard_supplies` rises by about
+0.056, as it did for both design culprits, because eating a portion in the night
teaches the same thing about the shelf.

**P4. It lasts less well than Mara's.** The share of his start-of-morning motivation
change that survives as an average over the morning is lower than Mara's in
`mara_ate_it`, because what carries his change is shame, which fades, and the belief
that keeps re-reading the search as a threat produces little extra fear in him.
Measured as morning sensitivity divided by start sensitivity, averaged over seeds
1 to 20, against the same quantity for Mara.

**P5. Nobody else is touched.** Every other person's feelings after the opening and
wants at minute zero are exactly the same as in the control.

**P6. It does not reach his first decision.** His first decision is the same as in
the control on every seed from 1 to 20. Standing still serves his two strongest
wants at once, and walking out of the room costs him something and serves only the
new one. This is predicted as a limitation, and holding would mean the deliberation
bottleneck in the diagnosis is still there.

**P7. He stays himself.** Different-person behaviour difference across the design
conditions stays above 0.30.

## What a miss would mean

- **P1 or P2 missing** would mean night shame is not being produced from honesty and
  values the way the rules say, which is an appraisal problem.
- **P3 missing** would mean the belief step does not generalise past the people it was
  designed around.
- **P4 missing** would mean the belief carrier matters more for a calm person than the
  arithmetic says, which would need explaining before it could be counted as good news.
- **P5 missing** would mean the locality fix is incomplete.
- **P6 missing** would be a better result than predicted, and would also need
  explaining.
