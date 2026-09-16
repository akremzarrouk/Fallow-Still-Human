# S1.7 hypothesis, the design, and held-out predictions

Written after inspecting the S1.6 code and rule data, and **before any S1.7 code exists**.
Nothing below has been run.

## 0. Why not the scenario that was suggested

The brief proposed: Daniel accuses Mara, Elena defends her, later Daniel asks Mara to do
something, and we compare whether she complies. After reading the architecture I think that
scenario would mostly measure things that are not there, and would hide the one thing that is.
Four reasons, each checkable in the code rather than a matter of taste:

1. **There is no compliance.** The decision layer has seven actions: wait, observe, go_to,
   check_pantry, search_room, comfort, eat. Nothing represents agreeing or refusing to do what
   somebody asked, and no motivation rule mentions a request. "Does Mara comply?" would require
   a new action, a new want and new proposals, all invented for this scenario, and the result
   would be a measurement of the thing I had just written rather than of the simulation.
2. **The ledger entry it would rely on is inert.** `p02` (Daniel empties Mara's bag while she
   stands there) already authors `searched_my_things` into Mara's ledger about Daniel at weight
   0.8. **No rule anywhere reads `searched_my_things`.** Five of the eight ledger entry types in
   the vocabulary are written by the scenario data and read by nothing. An experiment resting on
   that record would be measuring a variable with no wire attached.
3. **Nothing in the pipeline ever writes a ledger entry.** All fourteen ledger writes in the data
   are authored `ledger_effects` on hand-written events. Interpretation and appraisal never
   produce one. So "the relationship changed because of what happened" is, today, authored rather
   than simulated, and a scenario that authors the grudge and then reads it back would be the
   "hidden modifier to predetermined behaviour" the brief warns against.
4. **An accusation is not in the vocabulary.** The nearest general concepts are a `demand`
   addressed to me, or a `search_belongings` action aimed at me. Inventing an accusation act
   would again be scenario-specific content.

What the architecture *does* have is a genuine, general, already-shipped longitudinal loop that
no experiment has tested yet. That is what S1.7 should test.

## 1. What the architecture actually supports (from code, not from guesswork)

**The only two carriers that cross a day boundary are beliefs and the ledger.** A memory scaler
recalls only today: `ScalerEval.Recall` filters `x.Day == ctx.Today`. The ledger never decays but
is authored-only and mostly unread. Emotions decay every fade and are gone within a morning. So
**yesterday reaches today through beliefs, and essentially nothing else.**

**Beliefs are formed by general rules from what an event meant.** `belief_nudges` fire on the
*meaning* a person arrived at, not on the event: a reading of `disrespect` raises
`tendency($actor, does_not_respect_me)` by 0.15 plus pride, and a reading of `disrespect`
addressed to me raises `tendency($actor, treats_me_like_a_child)` by 0.12; `support` lowers
`does_not_respect_me`. None of these names a character, an act or a scenario.

**Those beliefs are then read back by interpretation rules**, which is the loop that makes
history matter:

| Belief | Written by | Read by |
|---|---|---|
| `tendency(x, does_not_respect_me)` | any `disrespect` reading (up), any `support` reading (down) | `corrected_by_a_junior_with_people_watching` 0.4, `being_watched` 0.3 |
| `tendency(x, treats_me_like_a_child)` | any `disrespect` reading addressed to me | `your_things_gone_through` 0.4, `being_watched` 0.4 |
| `tendency(x, needs_to_be_in_charge)` | **nothing** | `being_ordered_about` 0.4 |
| `supplies_short` | counting a short shelf, watching someone eat | `somebody_helping_themselves` 0.35, **and the `guard_supplies` want 0.5** |
| `answerable_for(me, missing_can)` | doing the thing, witnessed | `the_search_is_for_what_you_did` 1.0 |
| `role_claim(me, leads_family)` | **nothing** (authored) | `being_told_to_let_it_go` 0.3, **and the `find_out` want 0.3** |

So there is a real loop: be treated badly, come to believe that of the person, read the next
ambiguous thing they do more darkly, feel differently, want differently, act differently. Every
link is a general rule already shipped. S1.7 needs **no new mechanism** to test it.

## 2. The structural prediction that makes this worth doing

Two facts, both confirmed in code, make a sharp and falsifiable prediction.

- **Interpretation weight is discarded.** `Simulation.Perceive` passes only
  `interpretation.Meaning` into appraisal and into the belief nudges. The weight that reading won
  by is recorded in the trace and used by nothing.
- **No appraisal rule reads history.** All eighteen appraisal rules are scaled only by traits,
  values and perceptiveness. Zero belief, ledger or memory scalers.

Therefore a belief about a person can only change what somebody feels **by changing which
meaning wins**. A history that moves `disrespect` from 0.86 to 0.94 produces byte-identical
emotion, salience, motivation and action. This predicts that interpersonal history is
**causally inert except at an interpretation boundary**, where it is abruptly decisive.

Beliefs about the *world* behave completely differently, because `supplies_short` and
`role_claim` are read directly by motivation rules, where any change moves the want
proportionally. So the architecture should have **two channels with opposite characters**:

- **Graded channel** (belief read by a motivation rule): continuous, any change moves behaviour a
  little.
- **Categorical channel** (belief read only by interpretation rules): a step function, nothing
  moves until the reading flips, then everything moves at once.

**This is the hypothesis S1.7 tests.** It is a claim about where causal influence survives and
where it dies, which is what the brief asked for, and it separates "the character remembers"
from "the memory changes what they do" by measuring the gap between them.

## 3. The experiment

**Subject held constant. Later event held constant. Only history varies.**

The probe is a `search_belongings` event aimed at the subject, topic `missing_can`, witnessed.
It is chosen because two interpretation rules compete on it, and both are carried by history:

- `your_things_gone_through` produces **disrespect**, carried by `treats_me_like_a_child`
  (learnable)
- `the_search_is_for_what_you_did` produces **threat**, carried by `answerable_for` (from the
  night)

and because the two readings lead to genuinely different feelings (shame, anger, hurt,
frustration against fear and anxiety) and so to different wants (`restore_standing` and
`avoid_exposure` against `keep_peace`). It is also an event the silent morning already produces
by itself when somebody searches a room its owner is standing in, so it is not a synthetic probe.

The history is prior `search_belongings` events by the same actor on earlier days: he has gone
through my things before. Each is read as disrespect by the existing rules and nudges the two
tendency beliefs. No new rule, no new act, no authored ledger entry, no character named anywhere.

**Arms.**

| Arm | What differs | What it controls for |
|---|---|---|
| **C** control | no prior event | the baseline |
| **T** treatment | prior event, subject witnesses it | the effect |
| **U** unperceived | prior event happens, subject is not a witness | knowledge locality: world truth must not leak |
| **P** other actor | prior event perceived, but the later search is by a different person | relational specificity: this must not be global grumpiness |

**Measurements, at every stage of the chain, for each arm:** whether the event was perceived,
whether an experience was kept and with what meaning and salience, the belief and its
justification trace, the later reading and every rule's weight in it, the emotions and their
intensities, every want raised and its urgency, the ranked options with their appeal and cost,
the chosen action, and whether the whole path reconstructs from the trace alone.

**E2, the response curve.** Sweep the number of prior slights from 0 upward and record every
stage. This is the measurement that distinguishes a mechanism from a patch: a patch would move
behaviour smoothly with the modifier, and the architecture predicts a flat band followed by a
step. Run the same sweep on `supplies_short` (the graded channel) as an internal control, to
prove the instrument can see a graded effect where one exists.

**E3, time.** The same history at lags of minutes, same day, one day, two days and three days.
Beliefs have no decay anywhere in the code, so the prediction is that the effect is identical at
every lag, which is itself a finding and the mirror of the never-fading memory S1.6 found.

**E4, class generalisation.** Probe with several later events (`search_belongings` aimed at me,
`observe` aimed at me, a `demand` addressed to me, a junior refusing in front of others) against
C and T, to find which classes of later situation are history-sensitive at all, rather than
fitting one request.

**E5, the morning.** Full ninety-minute mornings with and without the prior event, on the shipped
rules (A) and on the configuration S1.6 recommended (B with both fixes), compared against the
S1.1 seed-noise floor. This asks whether any of it reaches behaviour over a morning.

## 4. Definitions

- **Independent variable:** the subject's prior history with one other person, varied only by
  whether earlier events occurred and whether the subject perceived them.
- **Dependent variables, in order:** experience kept; belief confidence; the winning meaning of
  the later event and its weight; emotions and intensities; wants and urgencies; option scores;
  chosen action.
- **Controls:** same subject, same profile, same later event object, same seed, same room, same
  people present, same hunger. The unperceived arm and the other-actor arm.
- **Confounds I can see:** (a) the prior events also produce emotions that may not have decayed
  by the probe, which would be a within-day effect rather than a longitudinal one, so the lag
  sweep must include lags long enough for emotion to be gone; (b) prior events add memories of
  today if placed on the same day, which recall can read, so the across-day arms are the clean
  ones; (c) the probe itself nudges beliefs, so measurements must be taken from the probe's own
  decision, not after it.
- **What counts as evidence:** a stage-by-stage trace in which every link is a real parent
  record, plus the counterfactual arms differing in the way the mechanism predicts and the
  locality arm showing no effect at all.
- **Failure conditions, stated in advance:** if the belief moves but no meaning ever flips at any
  history strength, the categorical channel is real but unreachable and the answer to the brief's
  question is "no, not for beliefs about people". If the meaning flips but emotion, motivation or
  action do not follow, the chain is broken at that stage and I will say where. If behaviour
  differs in the morning but the trace cannot reconstruct why, that is not evidence and will be
  reported as such.

## 5. Predictions, committed before running

Design conditions, the existing cast, the shipped rules unless stated.

- **P1.** In arm T the prior event is perceived, kept as an experience whose meaning is
  `disrespect`, and raises both `treats_me_like_a_child` and `does_not_respect_me` above their
  arm-C values. In arm U the event happens and the belief does not move at all.
- **P2.** With one prior slight, the later event's winning meaning is the **same** in T and C, and
  every downstream number (emotions, wants, option scores, chosen action) is **identical to
  within 1e-9**, while the interpretation weight differs. Memory persists; nothing follows.
- **P3.** There exists a number of prior slights at which the winning meaning flips, and at that
  point emotions, wants and the ranked options all change together, discontinuously.
- **P4.** The `supplies_short` sweep moves the `guard_supplies` want continuously from the first
  step, with no flat band. The two channels behave differently on the same instrument.
- **P5.** In arm P (the later search by a different person) the reading, emotions and wants match
  arm C, not arm T. The effect is about a person, not a mood.
- **P6.** The effect is identical at every lag from one day to three days, because no belief
  decays.
- **P7.** Of the four later-event classes, `observe` aimed at me is history-sensitive in weight
  but can never flip, because only one rule fires on it; `search_belongings` can flip; the
  `demand` cannot learn, because `needs_to_be_in_charge` is written by nothing.
- **P8.** Over a full morning, with one prior slight the action profiles in treatment and control
  are identical on a shared seed.

**Held out:** the boundary-crossing history strength predicted in P3 is not chosen in advance; I
will report the number the sweep finds. `leo_ate_it` seeds 201 to 240 are reserved for any
morning measurement, and no test has run a seed above 180.

## 6. What this slice will not do

No new action, no new want, no compliance, no relationship meter, no trauma, no decay constant,
no new emotion, no LLM, no Unity, no character-specific rule, and no change to any existing rule
or number. If the experiment shows a missing general mechanism, it will be named and specified,
and left for the next slice to implement against a fresh prediction.
