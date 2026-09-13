# Slice S1.2 report: deliberation

Date: 2026-09-13. Status: complete, stopped for review.
Reproduce with `./run-tests.sh`. **247 tests, 246 pass, 1 fails** (section 6, item 1; left
failing on purpose). Suite time about 750 s, against about 370 s at the end of S1.1.

| File | What it is |
|---|---|
| `baseline.md` | The S1.1 state before any change (by hand from test runs) |
| `diagnosis.md` | What was wrong, in words (by hand from `audit-before.md`, `reach-before.md`) |
| `audit-before.md`, `-after-c1`, `-after-c2`, `-current` | Every decision of 100 mornings taken apart, after each change |
| `reach-before.md`, `-after-c1`, `-after-c2`, `-current` | Whether a changed want reaches the choice, after each change |
| `c3-rejected/` | The change that was tried and taken out, with what it did |
| `experiment-results.md` | Tests 1 to 5 |
| `behaviour-noise-current.md`, `baseline-behaviour.md` | The behaviour effect against seed noise, counted three ways, before and after |

Commit order: `a354e98` instrument and diagnosis with behaviour unchanged, then this.

---

## 1. What was actually wrong

Measured on 7,960 decisions, before anything changed.

1. **People were stopped by what they were already feeling.** 44% of all decisions were
   taken because somebody had been interrupted, 35 interruptions a morning, and 47% of
   those were events that stirred almost nothing. The rule read the strongest feeling
   the person was carrying, not what the new event did. Mara chose to open the pantry
   at minutes 4, 7 and 10 of one morning, and never got to finish.
2. **Nothing remembered why anybody walked anywhere.** 47% of walks were followed by
   something the want behind the walk did not serve.
3. **Standing still was credited for what it avoids.** It came top in 45% of decisions,
   and all of its appeal came from two proposals that credit it for *not* eating and
   *not* confronting anybody. Sitting with somebody or opening the pantry avoid those
   just as well and got nothing. The two wants behind those credits were the most
   decisive in the model (56% and 50%); the want the night changes most was decisive in 2%.
4. **Summing across wants was not itself the fault.** 98% of winning options drew on two
   or more wants, which is what combining is for. The two mechanical forms of double
   counting I looked for are both at 0.0%.
5. **The seed settled 48% of choices, 41% between different kinds of action.** A symptom,
   not a mechanism; the band itself was not touched.

## 2. What I changed

| # | Change | Kept? |
|---|---|---|
| C1 | **Being stopped is earned by the new experience.** An interruption needs the event itself to stir at least the existing threshold (0.45), instead of whatever the person was carrying. Someone who is stopped weighs everything again, and if they choose the same thing they carry on with the minutes they had left. | Kept |
| C2 | **An intention survives a walk.** A walk leaves the person holding the want it was mostly for. On arrival they weigh only the options that serve it, unless the want has gone, nothing there serves it, or the best way of serving it costs more than it is worth. Something that lands hard enough to stop them means weighing everything again. No option gets a bonus; the test `HoldingAnIntentionAddsNothingToAnyScore` pins that. Only walking is a means in this slice, so nothing else carries an intention. | Kept |
| C3 | **The unearned credit moved.** Each want's weight on standing still moved, at the same weight, onto the acts it avoids. Which acts come from the event rules: the only acts anybody reads as a slight, a challenge or a threat. | **Rejected**, section 3 |

Also:
- Every scored option now carries per-want contributions as numbers.
- `Decision.Leading` is now the want that contributed most. It used to be whichever want happened to be listed first.
- `DecisionTrace.Explain` prints the required stage-by-stage trace from the numbers actually used.
- The morning gained a read-only decision hook, two read-only accessors, and an experiment method that makes something happen in the house.
- No rule was added. No data file changed.

**Tests changed, disclosed:**
- `SomebodyStillPacesBetweenTwoRooms...` was turned round, as its own message instructed.
- `EmergentMomentTest`: the end-of-morning shame check broke because Daniel now watches Elena again two minutes before the end. It now checks that shame fades after every look with 20 minutes to spare.
- `S1HeldOutTests.H2`: its proxy (shame greater than fear at one peak) went level, 0.19 against 0.20. Walking the terms back showed the fear comes from her night (section 5, example 3). The test now asserts that, labelled as observed rather than predicted.
- `S12ExperimentTests.T1b`: first asserted for Mara and failed. That miss is pinned, and the "somebody" claim was added after it.

## 3. C3, and why it was taken out

The unearned credit is real. `StandingStillsCreditIsExactlyAnAdvantage...` proves it on 2,407 options of real decisions: moving it changes every option's standing against standing still by exactly the credit, less what now counts against that option, and nothing else. Standing still against eating in front of people compares identically either way.

Removing it collapsed the cast (`c3-rejected/collapse.md`):

| | Credit in place | Credit moved |
|---|---|---|
| Sitting with somebody, share of all choices | 30% | **67%** |
| Different people, mean gap | 0.63 | 0.48 |
| Elena against Leo | 0.39 | **0.04** |
| Swap test (S1) | 0.63 | 0.38 |
| Elena deciding at the same minute in both worlds and choosing differently | 46 of 384 | **0 of 474** |

62% of what then makes people sit with each other comes from traits and values. Only
34% comes from anything felt, remembered or believed about the morning or the night.
Those wants are raised every minute and nothing a person does ever lowers them, so
whatever they credit wins forever. The credit on standing still was the only
counterweight. **It is load-bearing and unearned, and it stays in, pinned as a known
defect.** Leo's distinctive S1 morning (78% standing still) rests on it.

## 4. Before and after

| Measure | S1.1 | S1.2 |
|---|---|---|
| Deciding because interrupted | 44.3% | 34.8% |
| Interrupted by an event that stirred less than the threshold | 46.8% | **0.0%** |
| Interruptions that ended in carrying on | n/a | 61% |
| Worst back-and-forth pacing (40 seeds) | 17 | **2** |
| Walks followed by walking straight back | 6.9% | **0.0%** |
| Walks followed by something else | 46.8% | 41.1%, all of them walks to the food ending in "not worth it" (262 of 262) |
| Held intention where something serving a different want scored higher | n/a | 0.0% |
| Settled by the seed / between different kinds (S1 test) | 47.6% / 40.8% | 47.6% / 40.0% |
| Standing still on top | 45.2% | 49.4% |
| `avoid_exposure` decisive | 1.9% | 3.1% |
| Different people, mean / closest pair | 0.65 / 0.29 | 0.63 / 0.28 |
| Swap test | 0.73 | 0.63 |
| Same person across seed pools vs closest two people (new) | n/a | 0.045 vs 0.35 |
| Mornings anyone ate | 0 | 0 |

**The primary target, Mara:**

| Link | S1.1 | S1.2 |
|---|---|---|
| Night changes her wants over the morning (`avoid_exposure`, 10 seeds) | +0.057 | +0.089; positive on 20 of 20 seeds |
| Belief carries the lasting effect | 63% | 69% |
| Night changes her options' appeal at minute zero | not measured | 4 options per seed, 100% traceable to the night |
| Best option at minute zero changed | not measured | 0 of 20 seeds |
| Same situation, both clear, choice changed | not measured | **0 of 13** |
| Same situation, seed settled it, choice changed | not measured | 16 of 51 |
| Removing the night event | identical | identical, 988 decisions to the last bit |
| Behaviour vs noise, seeds 1-40 (S1.1 measure) | 3.6x | 3.3x |
| Behaviour vs noise, seeds 41-80 | 2.6x | **1.1x, FAILS** |
| Behaviour vs noise, seeds 81-120 (new, gate set first) | n/a | 1.95x, passes |
| Behaviour vs noise by minutes, seeds 1-40 / 41-80 | 4.7x / 2.9x | **1.5x / 1.3x** |
| Behaviour effect with `avoid_exposure` removed from both worlds | n/a | 0.022 vs noise 0.017, 72% gone |

**Elena, Daniel:**
- Elena: same situation, both clear, 8 of 169 choices changed, all 8 led by a want resting on her night. Above noise on seeds 1-40 and 81-120, not on 41-80.
- Daniel (ate it): now above noise on both seed sets he was measured on (0.030 vs 0.017; 0.032 vs 0.016). In S1.1 he was not.
- Daniel (hid it): still not above noise.

## 5. Causal traces

Full stage-by-stage traces are in `experiment-results.md`; these are cut.

**1. Elena, `elena_fed_mara`, seed 1, minute 65.** Same kitchen, same people, same minute,
both clear.

```
without the night:  wait 0.710 = keep_peace 0.455 + guard_supplies 0.255 - 0   (clear by 0.111)
                    search_room 0.598 = find_out 0.48 x 0.80 = 0.384 + restore_standing 0.214
with the night:     search_room 0.796 = find_out 0.73 x 0.80 = 0.582 + restore_standing 0.214   (clear by 0.088)
                    wait 0.707
find_out 0.73 because memory of threat about missing_can 0.71 x 0.35 = +0.25 ...
  because she read "Leo goes through the kitchen" as a threat (0.90)
    because answerable_for(elena, missing_can)
      because "Elena opens a can and gives it to her daughter"
selected intention: find_out -> action: search_room (8 min)
```

**2. Mara, `mara_ate_it`, seed 1, minute 87: removing one want, same moment.**

```
with avoid_exposure:  go_to->back_room 0.433 = find_out 0.371 + avoid_exposure 0.44 x 0.50 = 0.222 - 0.160
                      comfort:daniel 0.390, comfort:elena 0.375
                      too close to call between all three; the seed chose the walk
without it:           go_to->back_room 0.211, out of the band
                      too close to call between comfort:daniel and comfort:elena
```

This is how her night reaches her choices: it puts an option into a close call.

**3. Elena's strongest wish to be elsewhere, 0.39** (the S1 held-out miss, re-read).

```
shame +0.19 <- read "Daniel watches Elena" as disrespect           (the morning only)
fear  +0.20 <- read "Mara goes through the kitchen" as a threat
            <- answerable_for(elena, missing_can) <- her night
```

## 6. What still fails

1. **`S11ExperimentTests.WhetherTheBehaviourEffectRepeatsOnSeedsNeverUsedBefore` fails.**
   Mara 0.060 against noise 0.055 on seeds 41 to 80. I left it red rather than bend it.
   She clears the same gate on 1 to 40 and on 81 to 120.
2. **Mara's night never changes a clear choice in an identical situation** (0 of 13). It
   changes what her options are worth, and it changes which of them end up in a close
   call, which the seed then settles.
3. **Her behaviour effect is smaller.** By minutes it fell from 4.7x and 2.9x to 1.5x and
   1.3x. The direction changed too: the night made her sit with somebody less on S1.1
   code (64% against 72%) and more on S1.2 code (78% against 73%). I tested the obvious
   explanation, that S1.1's effect travelled through the interruption defect, and it was
   not supported: being stopped by old feelings was 6.2 a morning with or without the
   night. **Why it shrank is not explained.**
4. **The unearned credit on standing still remains.** It can't be removed without
   collapsing the cast (section 3).
5. **Ties between different actions: 40%, unchanged.**
6. **Nobody eats.** Every walk to the food ends with eating priced out on arrival.
7. **The carrier still lands in `find_out`,** the mislabelled want, in both Elena
   examples. Daniel, hid it, still isn't above noise.
8. **C2's measured effect is small.** An intention that held never overruled a better
   option; it removed walking straight back and narrowed ties in 8% of held decisions.
9. **Recording "carried on" as a decision inflates decision-count measures** of behaviour.
10. **The suite takes twice as long.**

## 7. Classification

| Finding | Label |
|---|---|
| Being stopped by what you already felt is gone | **PROVEN** (0.0% across 100 mornings; tests failed before, pass after) |
| Something that lands hard still stops people, and reconsidering can mean carrying on | **PROVEN** |
| An intention survives a walk and lapses for exactly its three reasons | **PROVEN** (unit and in-run tests) |
| Commitment adds no score | **PROVEN** |
| Pacing fixed | **PROVEN** (17 to 2) |
| Each want's contribution is visible and is the calculation used | **PROVEN** (appeal = sum of contributions, to 1e-9) |
| Standing still receives a structural advantage, and exactly what it is | **PROVEN** |
| That advantage removed | **FAILED**: removal collapses personality, so it was taken out |
| Changed circumstance, then changed motivation, then changed candidate appeal | **PROVEN** (100% traceable, removing the cause restores every decision exactly) |
| Changed appeal, then changed clear choice in an identical situation | **PROVEN** for Elena (8 cases); **FAILED** for Mara (0 of 13) |
| Mara's behaviour differs because of her night, above seed noise | **PLAUSIBLE**: 2 of 3 disjoint seed sets, weaker than S1.1 |
| Her behaviour effect runs mostly through her wish to be elsewhere | **PLAUSIBLE** (72% gone without it, one seed set) |
| Removing a want changes only the choices it mattered to | **PROVEN** (exact arithmetic on every decision) |
| Personality differentiation intact | **PROVEN** (0.63; closest pair 0.35 against 0.045 same-person noise), with the swap test lower (0.73 to 0.63) |
| Ambiguity is not hidden | **PROVEN** in mechanism (the seed only settles close calls, and ties within an intention stay open); **FAILED** as a reduction: still 40% |
| No circumstance-to-action rule | **PROVEN** (no rule added; source scans) |
| Oscillation decreases | **PROVEN** |
| Why Mara's behaviour effect shrank | **UNPROVEN** |

## 8. Recommendation

**MODIFY.** Keep C1 and C2. Do not try to fix the rest of this in deliberation.

The deliberation arithmetic now does what it claims. It is traceable to the number,
commitment never changes a score, the seed touches only close calls, and removing a
cause or a want changes exactly what it should. What still stops a changed person
acting changed is not deliberation. **Most of what people want is raised every minute
by traits and values, and nothing anybody does ever satisfies it.** Summing across wants
is only safe while something balances those standing wants. The one thing balancing
them is a credit this slice proved is unearned.

**Can this deliberation model work without increasingly arbitrary scoring rules? Not on
top of the current motivation layer.** Every fix available inside deliberation is
another rule of the same kind: sitting with somebody goes stale after N minutes, a
bonus for continuing, a keep-peace brake. `WatchingGoesStaleAfter` is already one, and
C3 showed what happens without them. The next change belongs in motivation: a want that
has been served should be satisfied, and a want about a person should need something to
have happened to that person. That is outside what S1.2 was allowed to touch, so it is
not done here.

## The question

**Does changed circumstance now lead to changed motivation, then changed candidate appeal, then changed intention or action?**

For Elena, yes, through the whole chain. In the same room, with the same people, at the
same minute, her night turns standing still into going through the kitchen, clearly and
traceably to the can she gave away. For Mara, the chain stops one step short. Her night
changes what she wants (20 of 20 seeds) and what her options are worth (100% traceable),
and it changes what she does over a morning by more than seed noise on two of three
seed sets. But it does that by putting options into close calls, not by changing a
clear choice, and her behaviour effect is weaker than S1.1 measured. Deliberation is no
longer what blocks it. Standing wants that nothing satisfies are.
