# S1.6 hypothesis, the two mechanisms, and held-out predictions

Written and committed after the diagnosis and **before any code for either mechanism
exists**. Nothing below has been run.

## Hypothesis

The pacing S1.5 exposed under B is not a failure of feedback from acting into memory, belief
or motivation. Nothing is learned on a walk that is given up, and nothing could be: 92.5 % of
those walks were foreseeably not worth taking from what the walker already knew, and the rest
are somebody being in the room. The want is right to persist. What is wrong is that a means
was proposed without regard to its end, and that half of the wants behind the walks rest on
scripted memories that never age.

So two changes, each a defect fix in its own stage, and each switchable so that it can be
measured alone and with the other:

## M1: scripted events of the lived day carry the clock's minute

**Where:** the event record (world truth), and the data. An event may say when in the day it
happened. The four scripted events of day 4 (`p01`–`p03` in the backstory, the opening count)
happen before the morning's first decision, so they carry minute 0. Nothing about recall
changes: freshness is what it always was, 20 / (20 + minutes since). A memory that carries
no minute is still treated as fresh, which is right for days with no clock, and after this
no memory of the lived day is without one.

In the experiment the four events are re-stamped in code; the loader accepts `minute` so that
the fix can be data when it ships.

## M2: a walk is endorsed for a want only if its end could be worth doing

**Where:** deliberation, at the moment a proposal endorses a walk. Before crediting a walk to
a want, the deliberator asks the question it already asks on arrival: of everything that could
be done for this want at the destination other than walking on, is the best worth more than
nothing, weighed with every want the person has now and priced as this person prices it? If
not, the walk is not endorsed for that want. The trace records what was foreseen either way.

The destination is imagined from what the walker knows and nothing else: the room and whose
it is (the house is not privileged), the rooms they have been through, whether they have
looked in the pantry, how hungry they are, and their own mind as it stands. Two things they
cannot know are taken at their most favourable for the want: nobody is there unless the want
is about somebody, in which case that person is; food kept there is within reach. If the end
is not worth it even then, the walk could not have been worth taking. If it is, the walk is
taken and the arrival may still disappoint, honestly, because of who turned out to be there
or what turned out to be gone.

**No number changes.** A walk that is endorsed is worth exactly what it was: urgency × fit.
Nothing is added, subtracted, decayed, or remembered. A walk endorsed for one want and not
for another keeps the first want's contribution only. The arrival judgement is unchanged.

Selected by `deciding.means`: `want` (the default, which the shipped rules keep: a walk is
worth its want) or `end` (M2). Removing the setting restores the shipped behaviour exactly.

## What this is not

- Not a cooldown, a blacklist, a boredom, a penalty on walking, a value on standing still,
  or a memory of having been somewhere. A walk that is worth taking is taken every time it
  is worth taking, and one that is not is never taken, from the first.
- Not a plan. One step: the walk and what could be done at its end. Nothing is sequenced.
- Not a fix for a want: `find_out` under M1 fades and is reactivated by what happens; under
  M2 it stays whatever it is. Neither touches its sources.

## Not changed

Perception, interpretation, appraisal, emotions, beliefs, the ledger, `PursuitOutcome`,
`until`, presence, interruption, food and eating, every proposal, every cost, every
motivation rule, every number in the rule files, the ambiguity band, and everything about
how traits and values enter a want (B stays `respond` throughout).

## Conditions

On B (`respond`), a 2 × 2: M1 off/on × M2 off/on. Plus A (`standing`) as shipped, and A with
M1, to see what the timing fix does where standing wants hide the loop.

## Measured, with the S1.5 instruments and the S1.6 diagnosis instrument

1. Walks set out on; walks whose end was foreseeably not worth doing; walks given up on
   arrival, and how many of those had somebody in the room.
2. Pacing, mean and worst; walks followed by something the walk's want did not serve.
3. `find_out` over the morning, by ten minutes, per person.
4. Standing still, share and on top; each want's decisive rate; sittings; searches.
5. Different-person gap: mean, weakest condition, closest pair.
6. The night against no night, over noise (S1.1 measure), for the four design culprits.
7. Meals, as written and with plenty.
8. Where wants come from (unsupported, traced), so that B's causal properties are seen to
   survive both changes.
9. Decisions led by no want, and what was chosen.
10. Leo on `daniel_ate_it` seed 9, minute by minute, under each condition.
11. One walk under M2 traced, showing what was foreseen and why a walk was or was not endorsed.

## Predictions on the design conditions (seeds 1 to 10 and 1 to 40)

Stated so that they can be wrong.

- **M2 alone** removes the walks to ends that were foreseeably not worth it: 0 such walks
  set out on. Walks given up on arrival fall to under 10 % of walks that arrive, and every
  one has somebody in the room. Pacing falls below A's (0.43). `find_out` stays flat.
- **M1 alone** makes `find_out` fall over the morning for Daniel, Leo and Mara (the last ten
  minutes under half the first ten) and removes most walks to look for something after the
  first twenty minutes, but leaves the walks to the food (about 450 given up under B) nearly
  where they are, so pacing stays well above A's.
- **Both**: the least pacing of the four, and walks given up under 10 %.
- **A with M1** changes A's behaviour little: pacing stays near 0.43 and standing still near
  half of choices, because A's standing wants are what decide it.
- Under both, B's causal properties hold: nothing raised on traits and values alone, and
  wants traced at or above 90 %.

## Held-out condition

`leo_ate_it`, **seeds 141 to 180**. No test has run those seeds.

## Predictions for `leo_ate_it`, seeds 141 to 180

Structural:

- **P1.** Under B with M2, no walk is set out on whose end was foreseeably not worth doing, as
  the diagnosis instrument measures it: 0 of all walks. Under B without M2, at least half.
- **P2.** Under B with M2, of walks given up on arrival as not worth it, every one has somebody
  in the room on arrival.
- **P3.** Under B with M1 and without M2, Leo's mean `find_out` in the last ten minutes is
  below half of the first ten. Without M1 it is the same in both.
- **P4.** Under B with both, nothing is raised on traits and values alone, and at least 90 %
  of wants rest on something that happened or the body.

Behavioural (I do not know these, and a miss is reported as a miss):

- **P5.** Under B with M1 alone, walks to the food given up on arrival are at least 80 % of
  what they are under B alone.
- **P6.** Under B with both, mean pacing is below A's on the same seeds, and the worst pacing
  is at most 3.
- **P7.** Under B with both, standing still is a smaller share of choices than under A (B's
  property, kept).
- **P8.** Under B with both, Leo's night stands out from no night, over noise, more than under
  A (S1.5 P9, kept).
- **P9.** Under B with both, somebody still eats (meals > 0), and no more walks to the food
  are given up than there are meals plus walks where somebody was present.
- **P10.** Under B with both, the mean different-person gap is at least B's minus 0.02, and
  the closest pair is no closer than under B.

No rule, factor or formula will be changed after these are run.
