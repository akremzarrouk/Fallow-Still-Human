# Slice S1 review: the silent house

Date: 2026-09-12
Status: complete, awaiting your KEEP / MODIFY / REBUILD / ABANDON decision.
Everything below is reproducible with `./run-tests.sh` from the project root.

## The hypothesis

> Do the minds created in S0 produce meaningfully different autonomous physical
> decisions when placed in the same circumstances?

## The answer in one line

Yes for **who they are**, and no for **what happened to them**.

| | Difference in how a morning is spent |
|---|---|
| Two different people, same morning | **0.62** |
| The same person, after four different nights | **0.04** |

Personality reaches behaviour. Circumstance almost does not. That ratio is the
finding of this slice, and everything below is either evidence for it or an
explanation of it.

---

## 1. What was actually implemented

Added to `Fallow.Core` (now 50 files, about 6,300 lines; S1 added roughly 3,400):

**The world.** A house of six rooms with doors and with walls you can be heard
through; who is in which room; what is left in the pantry; how hungry each person
is; and the clock. Held in one place and read by nobody.

**The Percept.** What one person can currently know of the house. Deliberation is
handed this and never the world, so what is absent from it cannot influence
anything. This is the structural form of knowledge locality, replacing S0 reliance
on authored witness lists.

**The deciding pipeline**, extending the S0 causal spine:

```
world event -> access -> interpretation -> experience -> belief
                                        -> appraisal   -> emotion
                                                            |
   world consequence <- action <- deliberation <- motivation +
            |                                                 (values, traits,
            +------------------> back into the pipeline        beliefs, ledger,
                                                               hunger)
```

- **Motivator**: seven wants, raised from values, emotions, beliefs, remembered
  moments and hunger. A want is a state of affairs, never an action.
- **ActionCatalog**: seven actions, and what the house allows right now. Runs
  before anything is scored, so wanting something cannot conjure it.
- **Deliberator**: appeal from the wants an option serves, minus what it costs
  this particular person, with a bounded ambiguity band.
- **Consequences**: every act changes the house and becomes an event that
  everybody near enough perceives through the same pipeline their history
  reached them by. The loop closes.
- **Interrupts**: something that lands hard enough stops what you were doing.

**Traceable wants.** Every term in a weighing keeps the records it drew on, so a
want leads back through the feelings and memories that raised it to the events
behind those. Section 11.

**Expression separated from feeling.** A person visible state is their strongest
feeling scaled by how much of themselves they let out. Composed people can be in a
state that the room cannot read.

**The batch runner.** Seeds times conditions to a CSV of decisions, plus action
profiles, motive distributions and a handful of counts. Deliberately thin.

**Content**, all data: 7 motivation rules, 22 proposals, 8 cost rules, 3 new
interpretation rules, 2 new belief inferences, 2 new appraisals, a house, and five
conditions for what happened in the night.

**The two S0 carry-over defects, fixed.** Section 8.

---

## 2. What was tested

182 tests, all passing. They fall into five kinds:

1. **Unit tests on the parts**: rooms, world state, percepts, motive raising,
   action availability, scoring, the ambiguity band, determinism.
2. **Invariants checked across whole runs**: knowledge locality, every decision
   traceable to a want and an event, nobody remembering what they did not see.
3. **Distributions across 200 mornings** (5 conditions times 40 seeds, 16,252
   decisions): action profiles, motive profiles, pairwise differences, oscillation,
   ambiguity share.
4. **A data-swap test**: exchange two people temperaments and nothing else.
5. **A held-out condition**, predicted in writing before it was ever run.

Seven of the tests are **characterisation tests for known defects**. They assert the
defect still has the size it has, and say in their names and comments that they
should be turned round when it is fixed. Nothing is hidden behind a green suite.

---

## 3. Exact results

### The experiment

| Measure | Result | Gate |
|---|---|---|
| Two people, same morning, difference in action profile | 0.62 mean | above 0.30 |
| Closest pair in the weakest condition | 0.31 | above 0.30 |
| The same person across the five conditions | 0.04 mean, 0.16 worst | wanted high, is low |
| Leading want, by person | four different ones | more than one |
| Behaviour change from swapping two temperaments | 0.62 | above 0.15 |
| Knowledge leaks across 200 mornings | 0 | 0 |
| Decisions settled by the seed | 49.1%, of which 41.8 points are real ties | wanted under 30% |
| Worst back-and-forth pacing in any run | 15 | wanted under 4 |
| Mornings in which anybody ate | 0 of 200 | wanted more than 0 |
| Searches done in front of the person whose room it was | 0 of 126 | wanted more than 0 |

### Who these four turned out to be

Across 40 mornings of `daniel_ate_it`, as a share of each person own decisions:

| | wait | observe | go to | check pantry | search | comfort | eat |
|---|---|---|---|---|---|---|---|
| Daniel | 21% | 17% | 31% | 10% | 20% | - | - |
| Elena | 59% | - | - | 4% | 0% | 37% | - |
| Leo | 72% | - | - | 14% | 10% | 5% | - |
| Mara | - | - | 6% | 12% | 14% | 68% | - |

And what was behind it:

- **Daniel**: needing to know what happened 65%, it has to last 20%, hunger 14%.
- **Elena**: wanting the house to hold 83%, it has to last 17%.
- **Leo**: it has to last 67%, wanting the house to hold 23%, needing to know 10%.
- **Mara**: somebody is not all right 68% (Elena 46%, Daniel 22%), needing to know 30%.

Four people who share every rule and differ only in data: one turns the house
over, one holds it together, one rations, one looks after whoever is nearest.

---

## 4. Which part of the hypothesis was supported

**Different minds produce different physical decisions, and for different
reasons.** Supported, and by more than the headline number:

- The rules name nobody. Both rule validators check this and both pass.
- Conditions structurally cannot ask about a trait, a value or a feeling; those
  can only move a weight.
- Every want has at least two ways of being served and every action is reachable
  from at least two wants, checked automatically. A want with one outlet would be
  that action under another name.
- Exchanging Daniel and Leo temperaments, changing nothing else, changes his
  morning by 0.62. The people carry the difference, not the file.

That last one is the strongest evidence here, and it is the same test that carried
S0.

---

## 5. Which parts failed

**Five failures, in the order I would fix them.**

### 5.1 Circumstance does not reach behaviour (the big one)

Four different things happened in the night and the mornings are nearly the same
morning. The largest difference any hidden truth made to anybody was 0.16, and
three of the five conditions produce **identical** motive distributions for three
of the four people.

The cause is specific. The only thing a condition changes is one person private
shame, and shame has exactly one outlet, `avoid_exposure`, which loses to nearly
every other want. So the guilty person feels different and behaves the same.

This is the failure that matters, because a scenario whose hidden truth cannot be
felt from the outside is not yet a scenario.

### 5.2 Nothing remembers why anybody went anywhere

Daniel walks to a room in order to search it, arrives, and walks back out without
searching, because on arrival the decision is taken again from nothing and
wanting food now outranks wanting to look. Worst case: 15 crossings back and
forth in one morning.

Commitment in S1 lasts as long as the action, not as long as the reason. This is
architectural, not content.

### 5.3 Wanting to do nothing beats wanting anything in particular

Appeal is summed over every want an option serves. Standing still serves wanting
the food to last, wanting the house quiet, and wanting to be left alone, and
collects from all three. Eating serves one want and collects from one.

Result: **nobody ate in any of the 200 mornings**, including when placed alone in
the kitchen at the top of the hunger scale with nothing left to search. The food
pressure the scenario was built around never fires.

### 5.4 Nearly half of all choices are settled by the seed

49.1% of decisions fell inside the ambiguity band. 15% of those were the same act
aimed somewhere else, which is honest indifference; the remaining **41.8% were
ties between genuinely different actions**, which by the design own account means
the weighing is too flat and the fix belongs in the rules.

This does not appear to be manufacturing the personalities, since the profiles are
strongly separated and the swap test still works. But it is well over the line the
design drew, and the line was drawn for a reason.

### 5.5 Urgency saturates, so fading memory cannot be felt

Recall does fade with time, and on Mara it visibly does. On Daniel it cannot,
because the standing terms in wanting to know what happened, his values and his
claim on the household, already carry him to the top of the scale on their own.
His strongest want is pinned at 0.995 from minute one to minute ninety.

A scale everybody reaches the top of stops being a scale.

---

## 6. Which results are weak evidence

**The five conditions are nearly the same experiment.** Since the hidden truth
barely reaches behaviour, running five conditions gave roughly the evidence of
running one. The distinctness numbers are real but they are four people measured
five times, not twenty measurements.

**The action vocabulary was chosen knowing these seven wants.** Seven actions for
seven wants, with the crossings arranged by hand. The automatic check that no want
has a single outlet is real, but the shape of the crossing was designed, and a
different scenario might not decompose so conveniently.

**The distinctness result is partly guaranteed by arithmetic.** Mara comforts 68%
of the time because she is the only person with a strong `look_after`, and she has
that because she is the only one whose values and traits weight it highly. That is
the model working, but it is also close to tautology: I chose the scalers.

The parts that are not weak, and that I would defend: the swap test, the
structural impossibility of naming anybody in a rule, the structural impossibility
of thresholding on a person, and the held-out condition.

---

## 7. The held-out test

The decision rules were written against `daniel_ate_it` alone. Six predictions
were written and committed before `elena_fed_mara` had been run once, in
`held-out-predictions.md`, and the rules were not touched afterwards. The git
history shows the order.

**Five held, one missed.**

| | Prediction | Result |
|---|---|---|
| H1 | The one who took it is not ashamed, because she meant to protect her daughter | **Held.** Anxiety 0.68, shame 0.00 |
| H2 | She therefore never wants to be elsewhere | **MISSED.** Peaked at 0.41 |
| H3 | The guilty brother does want that, in the fitted condition | **Held.** 0.46 |
| H4 | He investigates at least as hard when innocent | **Held.** 4.00 searches either way |
| H5 | Knowing the truth changes nothing about what Mara does | **Held.** 0.01 difference |
| H6 | The four stay four people in all five conditions | **Held.** Worst 0.61 |

**The miss is the most interesting result in this document.** H1 and H2 are not
independent, and I predicted them as if they were. Elena carries no shame out of
the night, exactly as predicted. She acquires some during the morning, and that is
what makes her want to be out of the room.

Where it comes from, nobody wrote. Daniel wants to know what happened, so he
stands watching his mother. She reads being watched as a slight, in proportion to
her pride. What it mostly leaves her with is hurt, because she is close to him;
but it leaves a little shame as well, and shame is the thing that makes a person
want to be elsewhere. Meanwhile her daughter is visibly not coping, which
frightens her, and fear pulls the same way.

A mother made to feel like a suspect in her own kitchen, by a son who is only
trying to work out what happened, is the first thing this project has produced
that I did not put there. It is kept as a test, so that it stays true.

H4 is worth a second look: exactly 4.00 searches either way, to two decimal
places, in both conditions. Guilt is not competing with curiosity at all; it is
simply absent from that calculation. The prediction held for the wrong reason,
and I am counting it as weak.

---

## 8. The two S0 carry-over defects

**Emotion intensity now runs 0 to 1.** Rule contributions are summed and then
squashed by a saturating curve rather than clamped. The curve is strictly
increasing, so two strong feelings stay distinguishable instead of both arriving
at the ceiling, which is exactly what clamping did when I first tried it: Daniel
shame and anger both hit 1.00 and the tie-break flipped, costing two cells of the
S0 table. Strongest feeling anywhere in 25 mornings: 0.893.

**Salience now discriminates.** It spans the range from a moment that stirred
nothing to one that stirred everything. Of 150 memories in one morning: 22 distinct
levels, range 0.15 to 0.98, **0% at the ceiling**, against 75% before.

Salience also acquired a consumer, which the S0 review noted it lacked: recall is
how a moment goes on pressing on somebody after the feeling has faded.

The S0 expectation table is unchanged at **100% on readings and 83.3% on
feelings** after both fixes, which is what it was before them.

---

## 9. Where an act is understandable without being optimal

Several, but the cleanest is Leo.

Leo is the one who knows most about survival. He spends **72% of the morning
standing still**, because rationing is his strongest want and not eating is the
way to serve it. He is right that the food has to last and wrong that there is
nothing else to do; the house is being turned over around him by somebody less
competent, and he lets it happen.

That is not the model failing. Leo values family safety first, is cautious, and
holds no claim on running the household, so nothing in him proposes taking charge.
It is a believable way to be wrong, and it comes from his data rather than from a
rule about him.

The second is Elena, who comforts 37% of the time and searches essentially never.
She is the only person who could settle the question by simply saying what she did
in three of the five conditions, and she spends the morning managing everybody
feelings instead. Silence is not yet a choice she makes; S1 has no speech, so it
is a choice she cannot make. The behaviour is right for the wrong reason.

---

## 10. Was randomness necessary anywhere

**Genuinely, in about 7% of decisions.** Those are the ones where the tied options
were the same act aimed somewhere else: which way to walk out of a room, which of
two people to watch. There is no fact about a person that answers those, and the
alternative is a deterministic tie-break that would read as a quirk.

**Not necessary, and probably harmful, in the other 42%.** Those are ties between
genuinely different things to do, and a person usually does have a preference
between standing still and going through a room. That share is a measurement of
flatness in the weighing, not a property of people.

So: the mechanism earns its place, the current amount does not.

---

## 11. Do the traces make decisions explainable

Yes, and this is the part I would keep unchanged. Every decision records what was
chosen, what it beat and by how much, which wants it served with the arithmetic
for each, what it cost and why, whether anything was left to chance, and which
options tied. Walking back from a decision reaches the wants, then what raised
them, then the feelings, then the readings, then the events.

The chain behind the emergent moment in section 7, printed by the tool and
shortened only by cutting the arithmetic from the middle of each line:

```
Motive [elena]: wants avoid_exposure 0.30
    because=feeling fear 0.48 x 0.35 = +0.17; feeling shame 0.16 x 0.80 = +0.13
  because Access [elena]: at minute 69, in kitchen, with daniel, leo, mara
    because Appraisal [elena]: disrespect touched respect: shame 0.33
        a_slight_is_felt_as_shame 0.18 | a_slight_in_front_of_others_is_worse 0.22
      because Interpretation [elena]: read it as disrespect (0.42)
          being_watched, base 0.30; trait proud 0.35 x 0.35 = +0.12
        because Access [elena]: was there and saw it
          because Event: Daniel watches Elena without saying anything.
    because Appraisal [elena]: concern touched family_safety: fear 0.48
      because Interpretation [elena]: read it as concern (1.54)
        because Access [elena]: was there and saw it
          because Event: Mara is not hiding it well.
```

Two causes, two events, both reached from one want.

This did not work when the review was first drafted: a want recorded only the
minute it was raised in, so the chain stopped at "she was standing in the
kitchen". Every term now keeps the records it drew on, so a feeling weighed by a
rule leads back to the appraisal that produced it. That was a real gap between
what the design claimed and what the trace did, and finding it while writing this
document is an argument for writing the document.

Two things I would still improve. The leading motive on an action record is the
largest single contributor, which misreports an option that won on three small
ones. And a decision settled inside the band does not record what the tied options
scored.

---

## 12. Architectural problems discovered

1. **No intent persistence.** The single most valuable thing this slice found.
   Deciding afresh every time, with no memory of the reason for the last decision,
   produces walking to a room and leaving without doing the thing.

2. **Additive appeal rewards breadth over urgency.** An option serving three
   moderate wants beats an option serving one urgent want. This is a property of
   summing, not a bug in the content, and it is why nobody eats.

3. **Urgency saturation flattens the top of the scale.** Once two or three
   standing terms are large, a want is pinned and nothing that happens afterwards
   can raise or lower it.

4. **Feelings have too few outlets.** Seven wants for nine emotions, and the
   emotions that most distinguish the conditions (shame, guilt) map to the one
   want that loses most often.

5. **`SituationCondition` and `Condition` are two condition languages** that will
   have to merge when speech arrives, since a speech act is both an event and a
   decision.

6. **The morning is one long tick loop with no notion of scene or place-change
   cost**, which is fine at four people in six rooms and will not survive S2.

---

## 13. Where the implementation became imitation rather than causation

Three places, honestly:

**`WatchingGoesStaleAfter`.** Watching somebody you have just watched is removed
from the option list after fifteen minutes. That is a rule about what is useful
rather than a consequence of anything, and it exists because Daniel otherwise
stared at his mother for forty minutes. The honest version would be that watching
somebody tells you something, and that something stops being new; that needs
belief formation from cues, which is S3.

**`NearestUnsearched`.** The same shape. A person looking for something does not
search the same room twice, which is true, but it is implemented as a targeting
mode rather than as a belief about where the can is not.

**The `comfort` softening.** Being sat with reduces the other person fear and
anxiety by a fixed proportion. The list of which feelings it settles is data, but
the mechanism is a direct write into another mind rather than something that
person perceives and appraises. It is the only place in the codebase where one
character changes another internal state without going through perception, and it
should be removed when speech arrives.

Everything else routes through the pipeline. No rule names anybody; no condition
thresholds on a person; no character has special-case code.

---

## 14. What remains unproven

- **That any of this is interesting to watch.** S1 measures whether four people
  behave differently. Whether a person would look at the result and see four
  people is S2.
- **That circumstances can reach behaviour at all** in this architecture. The
  fixes in section 15 are hypotheses, not known quantities.
- **That the decision layer scales past seven wants.** Adding wants makes the
  crowding problem worse, not better.
- **That the rules generalise beyond this house.** One held-out condition inside
  the same scenario is a weak generalisation test. A different scenario would be a
  real one.
- **That the ambiguity band is the right mechanism** rather than a way of hiding
  places where the weighing has nothing to say.

---

## 15. Recommendation

**MODIFY.**

The causal spine carries the weight. Four people who share every rule and differ
only in data spend a morning visibly differently, for different reasons, and the
whole thing explains itself. That is what S1 set out to test and it passed.

It failed on the other half, which S1 did not set out to test but cannot be
deferred: what happened in the night barely reaches what anybody does. I would not
go to S2 until that is fixed, because the thing S2 asks a human to see is exactly
the thing that is currently invisible.

**Four changes, in order, before S2. All small.**

1. **Give a decision a reason that outlives it.** When an option is chosen, the
   want that carried it stays raised for as long as the plan takes, so arriving
   somewhere for a reason means doing the thing. Fixes the pacing, and is the
   smallest change with the largest effect.

2. **Stop summing appeal.** Take the strongest want an option serves, plus a
   reduced share of the others. Standing still stops collecting three
   part-reasons and outranking one whole one, and food pressure starts working.

3. **Give shame and guilt more than one outlet.** A person who has done something
   is not only somebody who wants to leave the room: they also avoid the person
   they wronged, and they take on work that makes them look useful. Two more
   proposals on existing wants would probably do it.

4. **Un-saturate urgency.** Either drop the standing terms in `find_out` or stop
   merging motive rules with the accumulation curve, so that what happens during a
   morning can still move a want that is already strong.

Then re-run this exact batch, with the same held-out discipline, and check one
number: **the same person across the five conditions should differ by more than
0.2**, against 0.04 today. If it does, S2 has something worth embodying. If it
does not after those four changes, the problem is deeper than the decision layer
and we should talk about it before building anything else.

---

## Questions for you

1. **Do you accept MODIFY with those four changes, or would you rather see S2 in
   3D first** on the grounds that the people are already distinct enough to be
   worth looking at? I lean to fixing first, but the argument for looking first is
   real: everything in section 5 is measured, and none of it is measured against a
   human being.

2. **The comfort mechanism writes into another mind.** Leave it until speech
   arrives, or take it out now and accept that comforting somebody does nothing
   except be perceived?

3. **Is `eat` worth keeping in S1 at all** if the fix in point 2 does not make it
   fire? It is currently scenery, and scenery is the thing the validator is
   supposed to catch.

4. **How much should the batch grow?** 40 seeds times 5 conditions takes about 50
   seconds. 200 seeds would take four minutes and make the small differences
   trustworthy. Worth it, or keep the suite fast?
