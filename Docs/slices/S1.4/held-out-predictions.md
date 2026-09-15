# S1.4 hypothesis and held-out predictions

Written and committed after the diagnosis (`50bf671`) and **before any S1.4 simulation
code exists**. Nothing below has been run.

## Hypothesis

When somebody acts because they want to look after another person, what actually
happens to that person, as far as the helper can perceive it, changes what the want
reads.

The planned change, from the diagnosis:

1. **Distress stopping is perceivable.** When somebody's distress stops showing, everybody
   in the room with them perceives it, by the same route as distress starting. Nobody
   outside the room does.
2. **Seeing somebody come right answers having seen them go to pieces.** A memory of concern
   or threat about a person stops pressing once there is a later memory, about the same
   person, of seeing them come right. No number decides how much. It stops pressing,
   or it does not.
3. **Help that cannot reach its person does not happen.** Sitting with somebody who has left
   the room before it finishes does nothing to them.

The want itself, the proposals, the costs, deliberation, standing still, and the food and
hunger system are not to be touched.

## Controlled cases

| Case | What happens | Expected |
|---|---|---|
| A | Sits with somebody whose distress is showing, and it stops showing | The helper's concern about them is answered, and the want can be walked back to the sitting |
| B | Sits with them, and their distress is still showing | Nothing new is seen, the concern stands, and the want differs from A |
| C | They leave before it finishes | They are not soothed, the concern stands, and nothing is treated as help |
| D | Same state, no sitting | No answer unless the helper actually sees them come right on their own |
| E | Same seed, sitting soothes nothing, or nothing reads the new perception | Nothing differs until the consequence could matter |
| F | Anybody | Only people in the room hold the memory of seeing somebody come right |

## Held-out condition

`leo_ate_it`: held out since S1.1, and never run in S1.2, S1.3 or while designing S1.4.
No S1.4 test other than the ones checking these predictions may use it.

## Predictions for `leo_ate_it`, seeds 1 to 10

- **P1.** Every memory of seeing somebody come right is held only by people who were in the
  room with that person at that minute.
- **P2.** Whenever somebody's distress stops showing in front of others, every witness
  who decides again with that person present, and still wants to look after them, has
  both memory terms of that want at zero, and the want walks back to the moment they
  saw it.
- **P3.** Nobody who was out of the room at that moment has their concern about that person
  answered by it: any concern memory they hold about that person still presses at their
  next decision with that person present, unless they themselves later saw them come right.
- **P4.** Sittings where the other person's distress was showing and stopped by the end are
  followed, within the next 20 minutes, by no more sittings with the same person than
  sittings where it was still showing at the end, on average.
- **P5.** People stay different: the mean gap between different people's mornings in this
  condition stays above 0.50, measured the S1.1 way (S1.1 P7 measured 0.64 across the design
  conditions).
- **P6.** Total sittings per morning in this condition are lower than on the S1.3 code on
  the same seeds. **Not checkable after the change without the S1.3 code**, so it is
  recorded now from `diagnosis-before.md`: 492 sittings in the 50 design mornings. The
  check is the same count across the five design conditions after the change, and the
  prediction is fewer.

A miss is reported as a miss, and the rules are not touched afterwards.
