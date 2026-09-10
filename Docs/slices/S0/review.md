# Slice S0 review: the causal spine

Date: 2026-09-10
Status: complete, awaiting your KEEP / MODIFY / REBUILD decision.
Everything below is reproducible with `./run-tests.sh` from the project root.

## The hypothesis

> With one shared rule set and only per-character data, the same event produces
> distinct, explicable perception, memory, belief, appraisal and emotion results
> across the four characters.

## Result

| Measure | Result | Gate |
|---|---|---|
| Readings matched the designer's table | 100.0% (48/48) | 80% |
| Feelings matched the designer's table | 83.3% (40/48) | 70% |
| Character-specific branches in the simulation | 0 | 0 |
| Character names in the rule file | 0 | 0 |
| Events read differently by different people | 9 of 12 | more than half |
| Tests passing | 104 | all |

Both gates passed on the first run of the rules against the table. That number
is the least interesting thing in this document, for reasons set out under
"What this does not prove" below.

## What was built

Four assemblies of plain C# with no engine dependency (`Fallow.Core`, 31 files,
about 3,000 lines) and an EditMode test assembly (about 2,000 lines). The
pipeline runs end to end:

```
world event -> access -> interpretation -> experience -> belief change
                                        -> appraisal  -> emotion
```

Content is entirely data: four character files, a twelve-event script, one rule
file (16 interpretation rules, 3 belief nudges, 16 appraisal rules, 70 scalers),
and a controlled vocabulary that every other file is validated against.

## What the run actually produced

The event the slice was built around, in full:

> **b05.** Leo lays out, evenly and in front of everyone, why crossing at night
> gets someone killed. Daniel drops it.

- **Daniel** saw it, took it as **disrespect**, felt shame, then anger toward Leo.
- **Elena** saw it, took it as **support**, felt gratitude toward Leo, then relief.
- **Leo** knew what he meant, took it as **protect**, felt some anxiety.
- **Mara** saw it, took it as **support**, felt relief, then gratitude toward Leo.

One sentence, four people, four different things. Daniel's chain, printed by the
tool the slice exists to produce:

```
shame 1.90 (respect)
  because disrespect touched respect, with an audience
    because read as disrespect (1.46), where
        base 0.35
        trait proud 0.85 x 0.50 = +0.43
        value respect 0.75 x 0.40 = +0.30
        belief tendency(leo, does_not_respect_me) 0.43 x 0.40 = +0.17
        remembers overruled_me of leo 0.70 x 0.30 = +0.21
      runner-up: concern 0.71
    because he was there and saw it
      because Leo said maybe they should let someone else handle this one
```

By the end of the morning Daniel holds both of these at once, and neither has
driven the other out:

- `more_knowledgeable(leo, survival)` at 0.58, because he watched the water stop
  exactly as Leo said it would.
- `tendency(leo, does_not_respect_me)` at 0.56, because he read two of Leo's
  interventions as slights.

His ledger about Leo reads `proved_right 0.60` and `overruled_me 0.70`. Both are
named entries pointing at specific events, not a score. That contradiction was
not authored; it formed from the script.

Mara ends holding `protected_me 0.80` about Daniel, from the night he carried
her inside, and `searched_my_things 0.80` about Daniel, from the morning he
emptied her bag. Neither cancels the other.

Leo never learns that the bag was emptied. He was in another room, and nothing
in the system can tell him.

## What held

- **Knowledge stayed local, with no exceptions.** Across every event and every
  character, nobody kept a memory, a ledger entry or a belief from something
  they had no access to. This is checked twice: the validator refuses to author
  such a thing, and the simulation refuses to apply it.
- **Everything explains itself.** Every belief that moved cites the experiences
  that moved it; every feeling walks back through appraisal and interpretation
  to a world event in at least three steps, and names the concern it arose from.
- **The rules are reused, not one per case.** All 16 interpretation rules fired,
  59 firings across 33 rule-derived cells, an average of 3.4 each. Only three
  fired once. This is the honest anti-tautology number.
- **The people carry the difference, not the rules.** Exchanging Daniel's and
  Leo's temperaments, leaving ages, roles, beliefs, script and rules untouched,
  changes Daniel's reading of b05 away from disrespect. Being corrected in front
  of the family is only an insult to someone built to hear it that way.
- **History is part of hearing.** Running only the day-4 probes, with no three
  days behind them, Daniel still reads p01 as disrespect but more weakly. The
  argument they already had is part of what he hears.
- **Some readings were close.** Daniel's disrespect at b05 beat concern 1.46 to
  0.71, but his support reading of the same event was not far behind. There are
  moments here that could have gone the other way.

## What missed, and what I think it means

All eight misses are feelings, not readings, and seven of the eight are the same
disagreement: I wrote "none" and the model produced anxiety.

| Cell | I wrote | Model produced |
|---|---|---|
| b03, b04, p03 / Leo | none | anxiety, about 0.9 |
| b05 / Leo, b09 / Daniel, p03 / Elena | none | anxiety, 0.36 to 0.79 |
| b05 / Elena, b08 / Mara | relief | gratitude |

**On the anxiety misses, I think the model is right and I was wrong.** I wrote
Leo as unflappable and Elena as composed, and then gave both of them
`family_safety` as their first value. A person whose first commitment is the
safety of their household, watching the water run out, feels something. Writing
"none" was me modelling stoicism as absence of feeling rather than as
non-expression. The two are different, and the difference belongs in the
expression profile, which S0 loads but does not yet use.

**On the two gratitude-versus-relief misses I am less sure.** Being sat with
until you stop crying and being carried in from the doorway are both help aimed
at you, and the rules cannot currently tell "the danger is gone" from "someone
was kind to me". That is a real gap, not a tuning error.

## Weaknesses found, none of which S0 needed to solve

1. **Emotion intensity is not bounded above one.** Two appraisal rules for the
   same feeling sum, so Daniel's shame at b05 reports as 1.90. Stored emotions
   are clamped, so nothing breaks, but the reported number is a strength rather
   than a proportion and the scale needs a decision. I deliberately did not
   clamp it late in the slice: clamping would have tied shame and anger at 1.00
   for Daniel at p01 and flipped the result on a tie-break, which is exactly the
   kind of change that should be made deliberately rather than to tidy a number.
2. **Salience is saturated and therefore currently useless.** Eighteen of
   twenty-four sampled memories sit at 1.00, because it is computed from
   intensities that exceed one. It tells us nothing about which memories matter
   most. Nothing in S0 reads it, so it costs nothing yet, but it must be fixed
   before anything depends on recall.
3. **Attention can change how hard something lands but never what it is.**
   Because it scales every feeling from a reading equally, Mara's priming toward
   threat cannot make her feel fear where she would otherwise feel something
   else. That may be the right model. It is not the one I described.
4. **The expression profile is loaded and unused.** Deliberate, and the right
   place for it is the slice where behaviour becomes visible.
5. **Two of sixteen interpretation rules are close to naming a single moment.**
   `your_things_gone_through` and `being_ordered_about` each fired once. They
   are written generally, but they have not been shown to generalise.

## Design decisions taken during the slice

These were not in the plan and are worth your attention:

- **`addressed` replaced `targets_self`,** with four values: me, group, other,
  nobody. Being one of a room addressed as a group is not the same as being the
  person spoken to. Without that distinction a bystander could not read an
  argument starting while the person in it read an insult.
- **Events carry a `valence`** (good, neutral, bad), so a rule can say "bad news
  reads as a problem" without listing every kind of bad news.
- **Events may carry authored `belief_effects`,** access-filtered exactly like
  ledger effects. This is how Daniel comes to believe his brother knows more
  about survival than he does, which S0 cannot yet infer. It is scaffolding, and
  it should be replaced by inference in S3.
- **Nobody is ever completely certain.** Accumulation is capped below 1.0, so a
  belief can always be argued back down.
- **No randomness at all.** S0 is fully deterministic; the same script and cast
  always produce the same traces. The ambiguity band arrives with decisions, in S1.

## What this does not prove

The 100% reading match is weak evidence on its own, and I want to be plain about
why: **I worked through the expectation table by hand while writing the rules.**
The table was written and committed first, which the git history shows, but the
rules were then written to satisfy it. That is fitting, not prediction.

What actually carries weight is narrower:

- the rules were reused 3.4 times each rather than written one per cell;
- no rule and no line of the simulation names anybody;
- conditions structurally cannot ask about a trait, a value or a relationship,
  so nothing can be tuned by thresholding on a person;
- exchanging two characters' temperaments changes the outcome in the direction
  the design predicts.

The honest test of generality is an event the rules have never seen, with the
expectation written afterwards and the rules left alone. That should be part of
the S1 review, and it will be cheap once decisions exist.

Also unproven, and out of scope by design: that any of this is interesting to a
human being. S0 says the representation works. Whether the people are worth
meeting is what S1 and S2 are for.

## Recommendation

**KEEP.** The representation carries the weight the later slices need to put on
it, and the trace is good enough to argue with.

Proceed to S1 (the silent house: motivations and physical decisions) with three
carry-over items:

1. Decide the emotion intensity scale, and fix salience with it.
2. Decide whether "calm" people should feel less or merely show less. My
   recommendation is show less, which makes it an expression matter and leaves
   appraisal alone.
3. Add one held-out event to the S1 review, with its expectations written after
   the rules are frozen.

## Questions for you

1. The seven anxiety misses: do you accept that Leo and Elena feel it and simply
   do not show it, or do you want them to feel less?
2. Should authored `belief_effects` survive past S3, or is it a scaffold you
   want removed the moment inference can replace it?
3. Do you want `neutral` to remain a real reading a character can hold, or
   should an event nothing fits leave no memory at all?
