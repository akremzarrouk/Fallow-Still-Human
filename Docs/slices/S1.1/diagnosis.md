# S1.1 diagnosis: where the circumstance is lost

Written from `diagnosis-before.md` and `fading-rate.md`, both generated against the
unchanged S1 code. Nothing here is inferred from reading rules; every claim is a
measured difference between a treatment and a control run on the same seed, with
the same world and the same people, differing only in the night.

## The short answer

The night does reach motivation. It is lost afterwards, in four separate places.
One of them is a knowledge leak the S1 tests could not see.

## Measured, stage by stage, for the person who took the can

`daniel_ate_it` against no night at all, seed 1. `mara_ate_it` is the same shape.

| Stage | Daniel | Mara |
|---|---|---|
| Perceived the night | yes, as `took_what_was_not_mine`, salience 0.75 | yes, same, 0.76 |
| Belief moved | `supplies_short` only | `supplies_short` only |
| Feeling after the opening count | shame +0.11, fear +0.21 against control | shame +0.12 |
| Wants at minute zero | `avoid_exposure` **+0.159**, traceable to the night | **+0.181**, traceable |
| Shame difference at minute 5, 10, 20 | +0.04, +0.03, **gone** | +0.12 at 1, +0.05 at 20, gone by 45 |
| `avoid_exposure` averaged over the morning | **-0.015** | **-0.020** |
| First three decisions | identical to control | different |

So the chain `event -> perception -> memory -> appraisal -> emotion -> motivation`
works at minute zero. By minute twenty it has nothing left to run on.

## Where it goes

### 1. A leak: an event nobody else perceived still changes them

In every overnight condition, people who were asleep in another room start the
morning with different feelings and different wants from the control.

| Who, which condition | Perceived the night | Wants moved at minute zero |
|---|---|---|
| Daniel, `mara_ate_it` | no | `avoid_exposure` -0.074, `restore_standing` -0.082 |
| Mara, `daniel_ate_it` | no | `avoid_exposure` -0.064, `restore_standing` -0.054 |
| Elena, `daniel_ate_it` | no | whole-morning behaviour difference 0.20, larger than Daniel own 0.12 |

The cause is in `Simulation.Apply`: every event fades every mind's feelings, whether
or not that mind perceived the event. One extra event in the night means one extra
fade for the whole house. The three conditions a person slept through produce
identical shifts for that person, which is the signature of a mechanical artifact
rather than a cause.

This is a knowledge-locality violation at the level of internal state. The S1 leak
tests check memories and grudges, not feelings, which is why 0 leaks was reported.
It also means the S1 figure of 0.04 for one person across conditions is part cause,
part this artifact, and part chaotic divergence once a small feeling difference
flips a tie. It cannot be read as a measure of circumstance at all.

### 2. The only lasting stage of the pipeline is never reached

The pipeline has one stage that does not fade by design: belief. Feelings fade.
Recall of a moment fades over a twenty-minute half-life. Beliefs stay until
evidence moves them.

The night moves no belief about what happened, only `supplies_short`. So the only
carriers of the night are the feelings it caused, and those are drained by about
thirty fades over the morning, one every 2.99 minutes on average.

Two further blocks sit behind this:

- Recall only counts memories from the same day, and the night events are dated
  the day before, so no motivation rule can recall last night at all.
- No motivation or interpretation rule reads anything about the night even if it
  could be recalled.

### 3. Saturation absorbs what does get through

| Who | Want | Control | Treatment | Traceable to the night |
|---|---|---|---|---|
| Elena, `elena_fed_mara` | `keep_peace` | 0.995 | 0.995 | **yes** |
| Daniel, every condition | `find_out` | 0.995 | 0.995 | n/a |
| Leo, every condition | `keep_peace` | 0.995 | 0.995 | n/a |

Elena's case is a direct observation of the block: the night pushed her want to keep
the house together, the push is in her trace, and it moved the number by nothing
because both worlds were already at the ceiling. Urgency is clamped by the
accumulation curve, which was written for inputs between 0 and 1; standing terms
from values and traits routinely sum past 1 before anything happens.

### 4. When motivation does change, the decision often does not

Daniel's `avoid_exposure` is 0.16 higher at minute zero and his first three decisions
are identical to the control, because his saturated `find_out` proposals outscore
everything. Mara's first decisions do change. This is the deliberation layer, which
S1.1 is told not to redesign, and it is recorded here so that a result measured at
the level of motivation is not mistaken for one measured at the level of behaviour.

## What this means for the fix

The diagnosis does not say "shame needs more outlets". It says:

1. The experiment cannot be trusted until feelings stop being faded by events a
   person never perceived. That fix is required, not optional.
2. The night never becomes anything that lasts. The hypothesis chain has BELIEF in
   it, and belief is exactly the stage that is skipped.
3. Even a lasting cause would be invisible on the wants that are pinned at the top.
4. Deliberation is a separate bottleneck and will be measured, not fixed.

The changes will be made one at a time and measured after each, so that the effect
of each one can be read separately.
