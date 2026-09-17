# Fallow: system understanding audit

Date: 2026-09-17. An investigation, not a slice. **No line of `Fallow.Core`, no rule, no data file
and no scenario was changed.**

## How to read this document

Three sources, kept apart throughout:

| Label | Source | What it can tell us |
|---|---|---|
| **INTENDED** | `README.md` and the slice reports under `Docs/slices/` | what we meant |
| **IMPLEMENTED** | `Assets/_Project/Scripts/Core` and `Assets/_Project/Data` | what the code and data say |
| **OBSERVED** | tests, generated traces, and the census below | what actually happens when it runs |

**There is no architecture or roadmap document in the repository.** The only design text is the
README and the slice reports. Anything the brief describes as intended but which appears in
neither (a SpeechAct system, a player knowledge layer, an S4 that makes the ledger live, the LLM
principle) is compared against the brief itself, and marked as such.

**Method.**
1. Every Core source file was read, and the data files were parsed rather than skimmed.
2. A reference census of the runtime code found which fields and methods have a reader
   (scratch scripts, not committed).
3. A census of the rule data found which conditions, scaler kinds and vocabulary items any rule
   uses (same).
4. **One read-only instrument was added:** `Assets/_Project/Tests/EditMode/AuditCensusTests.cs`,
   which runs the backstory once and the fifty standard mornings (five design conditions, seeds
   1 to 10) on the shipped rules, and counts what fires. Output: [`census.md`](census.md). It was
   necessary because "is this mechanism active" cannot be answered from the source, and the
   committed trace covers one morning and only what each decision rests on. It changes nothing
   and asserts nothing about behaviour.
5. Every existing slice report was read against the code.

**State of the tree at audit time.** S1.7 (its tests and documents) is still uncommitted from the
previous session, and its regression run never completed. The full suite was run during this
audit; its result is in section 20.

**The configuration audited is the shipped one**, which is *not* the one the last three slices
recommended: `decisions.json` sets neither `dispositions` nor `means`, so the shipped model is
S1.5's **Model A (standing wants)** with S1.6's walk-weighing **off**, and no scripted event carries
a minute. Every "IMPLEMENTED" and "OBSERVED" claim below is about that configuration unless it
says otherwise.

---

## 1. Executive Summary

**What Fallow is today:** a deterministic, rule-weighted appraisal simulation of four people in one
house over one morning, with one authored backstory, no speech, no player, no language, and no
engine integration. It is more coherent than a feature list would suggest and less deep than its
vocabulary suggests.

**What works, and is proven:**
- Events reach only the people who perceive them.
- The same event is read differently by different people, for traceable reasons.
- Readings produce feelings and move beliefs.
- Beliefs formed from experience change how later events are read.
- Feelings, memories of today, a few beliefs and hunger raise wants.
- Wants choose among seven physical acts.
- Acts become events that feed back in.
- Every step writes a causal record, and chains reconstruct from the trace alone.

**The seven findings that most change our picture of the machine:**

1. **The shipped motivation model is still the one we have already judged wrong.** 34.6 % of the
   32,555 wants raised in fifty mornings are moved only by traits and values, and every one of the
   2,149 choices to stand still is credited by the two proposals that credit standing still at
   every decision. S1.5 and S1.6 built and
   measured the alternatives and neither was shipped. **Every behavioural number since S1.5,
   including all of S1.7, was taken on Model A.**
2. **Interpretation is continuous inside and categorical at its boundary.** Rules sum into a weight
   per meaning; only the winning label leaves. The weight, the margin and the runner-up are
   recorded and read by nothing. No appraisal rule reads anything but traits and values. History
   can therefore reach a feeling only by flipping a label.
3. **Memory is a record of what an event *meant*, not what happened.** The act, its tone and its
   valence are not stored in the mind. Only four memory terms in two wants ever read a memory at
   all, and never one from an earlier day: 26.9 % of memories held at decisions are unreachable.
4. **People read their own morning acts as if they were watching someone else.** Morning events
   carry no intent. All 251 acts of comfort in fifty mornings were read by the comforter as
   support received, made them grateful *to themselves*, and nudged a belief about whether
   *they* respect *themselves*.
5. **The investigation loop cannot succeed.** `find_out` is served by searching, watching and
   checking the shelf, and nothing in the world records where the can went. No rule forms a
   belief from searching or watching. Searching matters only through how *other* people read it.
6. **Hearing through walls, the only cross-room channel, never happened in a morning.** Zero of
   the morning's events had an overhearer in fifty mornings. The one overheard event is authored
   backstory.
7. **Half of the emotional vocabulary has no motivational outlet.** Wants read anger, anxiety,
   fear and shame. Gratitude and relief, the two feelings most often being carried at a decision,
   along with hurt and frustration, are read by no want and no cost.

**The pattern across S0 to S1.7** (section 21): we repeatedly assumed a stage carried information
across a boundary, and it dropped it. We also repeatedly credited behaviour to a mechanism when a
standing credit was carrying it. Both errors survive because each slice measured its own mechanism
and nobody measured the whole writer-to-reader graph. This audit is that graph.

**Recommendation** (section 28): do not implement S1.8 as specified yet. First, make the baseline
decision S1.5 and S1.6 left open. Then run a measurement-only experiment on the
**motivation-to-action transfer function**: how far must a want move before what somebody does
changes, in real decision moments, on both baselines? S1.7 showed history changes wants and
rarely acts. Until we know whether deliberation or the baseline is the binding constraint,
propagating interpretation strength would make a graded input to a layer that may not respond
to grades.

---

## 2. What the System Actually Is

If the documentation were deleted and only the code, data, tests and traces remained, this is what
we would say.

> **Fallow is a headless C# rule engine that simulates how four fixed characters perceive, read,
> feel about and act on a short scripted history followed by a ninety-minute silent morning in one
> house.**
>
> An event is a hand-shaped record with an actor, a target, an act or action, a topic, a tone and a
> valence. Who perceives it is decided by who is in the room (or, in the backstory, by an authored
> list). Each perceiver scores every matching interpretation rule by adding up weights from their
> traits, ranked values, perceptiveness, a handful of beliefs and one ledger entry, and keeps only the
> meaning with the largest total. That meaning looks up feelings in a table weighted by the same
> traits and values; the feelings accumulate per type and target and fade on a clock. The meaning
> also nudges a small set of beliefs about people and about the food, which never fade. A record of
> the moment, as a meaning, is kept.
>
> Every minute, anyone idle turns their current feelings, memories of today, a few beliefs, hunger
> and, as shipped, their traits and values into seven wants. Each want adds urgency times a fixed fit
> to the physical acts that serve it, each act subtracts a trait-weighted price, and the best score
> wins. If the top scores are within 0.08, a seeded coin weighted by score picks among them, which
> happens in 38 % of decisions. A walk remembers which want it was for, and is abandoned on arrival if
> that want is no longer worth serving there. Acts change the house (who is where, hunger, portions)
> and become new events.
>
> Everything writes a causal trace that the simulation itself never reads, and a large test suite
> runs counterfactual pairs of mornings to measure whether a change in history changes what people
> want and do.
>
> It demonstrably makes four people behave differently from each other. It can make the same person
> want differently because of something that happened to them, and occasionally act differently. The
> action layer is shallow (seven acts, no speech, no plans beyond one walk, no way to learn anything
> from searching or watching). Much of what distinguishes the people is still standing wants from
> their traits, and much of what they do is standing still.

That is not a criticism. It is a fairly clean, honest, traceable core with a thin behavioural
surface and a number of wires that go nowhere.

---

## 3. Implemented Architecture

### What runs, in the order it runs

```
SETUP (Scenario001.PrepareWith)
  load data -> Simulation(cast, rules)  [Mind per person: Profile, seeded BeliefStore, Ledger, EmotionSet, Experiences, Outcomes]
  backstory: Simulation.Run -> Apply(event) x12        [fade every event]
  night:     Apply(event) x0..1, then PassTime(1.0)     [fade once, for everybody]
  WorldState(house, portions, rooms, hunger); SilentMorning(sim, rules, world, Rng(seed), day)
  opening:   Apply(m000-open)

PER EVENT (Simulation.Apply -> Perceive, for every mind)
  WorldEvent.AccessFor(person) -> None: stop
                                -> Witnessed | Overheard:
     Interpreter.Interpret  -> own act with intent? intent, weight 1
                            -> else: sum matching rules per label, argmax > 0, else "neutral"
     Appraiser.Appraise(meaning, reach x attention(meaning)) -> EmotionContributions
     salience = 0.15 + 0.85 x accumulate(intensities); confidence = 1 or 0.6
     Mind.Remember(Experience{meaning, topic, actor, target, day, order, minute, salience, ...})
     EmotionSet.Add per contribution (Accumulate.Toward per type|target)
     ApplyBeliefNudges (rules on meaning)       -> BeliefStore.Nudge
     ApplyAuthoredEffects (ledger/belief blocks on the event, access-gated)

PER MINUTE (SilentMorning.Step)
  WorldState.Tick (minute, hunger += 0.004 x hunger_rate); Simulation.PassTime(1/3 fade)
  for each busy person whose act finished: Complete(act) -> world change + Happened(event) -> Apply
  ShowWhatShows: dominant distress x expressiveness >= 0.30 -> show_distress / steady events
  for each idle person: Begin
     See -> Percept
     Motivator.Raise(mind, percept) -> Motives        [7 rules, no conditions, all evaluated every time]
     Deliberator.Decide(mind, percept, motives, rng.Fork(person@minute), holding)
        ActionCatalog.Available(percept) -> options
        Rank: appeal = sum(urgency x fit over proposals); cost = sum(cost rules); score = appeal - cost
        intention brought in? held -> consider only what serves it; else lapsed (3 reasons)
        band 0.08 -> PickWithin (seeded, score-weighted) or argmax
        Forms intention = Leading want (only kept if the act is a walk)
     record outcome if an intention lapsed on a need-reading want (PursuitOutcome)
     become Busy for the act's duration
  any event that stirs >= 0.45 in a busy person interrupts them (drops their intention)
```

### Classification of every mechanism

| Mechanism | Where | Status on shipped rules | Evidence |
|---|---|---|---|
| Access / perception gate | `WorldEvent.AccessFor`, `Simulation.Perceive` | **ACTIVE** | census: 8,473 witnessed, 2,077 "not there" |
| Overhearing | `RoomGraph.Audible`, `SilentMorning.Happened` | **PARTIALLY ACTIVE**: backstory only | census: 50 overheard (1 authored event x 50 runs), 0 morning events with an overhearer |
| Interpretation | `Interpreter` | **ACTIVE** | 8,523 readings; 20 of 21 rules matched |
| Own-intention reading | `Interpreter.Interpret` line 92 | **PARTIALLY ACTIVE**: authored events only; morning acts have no intent | census: 1,356 morning own-act readings, none from intent |
| Appraisal | `Appraiser` | **ACTIVE** | all 18 rules fired |
| Emotion accumulation and decay | `EmotionSet`, `Simulation.Fade` | **ACTIVE** | |
| Memory storage | `Mind.Remember` | **ACTIVE** | 128,117 memories held, summed over decisions |
| Memory recall | `ScalerEval.Recall` | **PARTIALLY ACTIVE**: 4 terms in 2 wants, same day only | 4,705 non-zero memory terms |
| Memory "answered" (`until`) | `ScalerEval.Recall` | **ACTIVE** for `look_after` | S1.4; 762 reassurance memories |
| Salience | `Simulation.Perceive` -> `Recall` | **ACTIVE** (read only by recall) | |
| Memory confidence | `Experience.Confidence` | **PRESENT BUT DISCONNECTED** | no runtime reader |
| Belief seeds | `Profile.InitialBeliefs`, `BeliefStore.Seed` | **ACTIVE** (some read, some not) | section 10 |
| Belief nudge rules | `Simulation.ApplyBeliefNudges` | **ACTIVE** | all 6 fired |
| Authored belief effects | `ApplyAuthoredEffects` | **DATA-ONLY in effect**: the one predicate written (`more_knowledgeable`) is read by nothing | |
| Ledger | `Ledger`, authored `ledger_effects` | **PARTIALLY ACTIVE**: 3 of 8 entry kinds read; none produced by the simulation | section 17 |
| Motivation, standing (A) | `Motivator.Weigh`, `Standing` | **ACTIVE (shipped)** | 34.6 % of wants standing-only |
| Motivation, respond/gated (B, B0) | `Motivator.Weigh` | **PRESENT, NOT SHIPPED** (test switch) | S1.5 |
| Urgency knee | `Accumulate.Knee`, 0.85 | **ACTIVE** | |
| Action availability | `ActionCatalog.Available` | **ACTIVE** | census availability counts |
| Proposals and fit | `Deliberator.Rank`, `ActionCatalog.Endorsed` | **ACTIVE** | 22 of 22 credited something |
| Costs | `Deliberator.PriceOf` | **ACTIVE**, one rule never applied | `with_them_standing_right_there`: 0 |
| Intention across a walk | `Deliberator.Decide` 253-270, `SilentMorning.Begin` 280-291 | **ACTIVE** | 222 held, 188 lapsed |
| Walk weighed by its end (M2) | `Deliberator.Rank` 383, `Foresee` 425 | **PRESENT, NOT SHIPPED** | `means` absent from data |
| Event minute (M1) | `ScenarioLoader.ReadEvent` | **PRESENT, NOT USED BY DATA** | no event sets `minute` |
| Ambiguity band and seeded pick | `Deliberator.PickWithin` | **ACTIVE** | 1,552 of 4,066 (38.2 %) |
| Interruption | `SilentMorning.Interrupt` | **ACTIVE** | 1,017 interruptions, 583 carried on |
| Visible distress / steady | `SilentMorning.ShowWhatShows` | **ACTIVE** | 321 / 283 events |
| Soothe (direct write into another mind) | `SilentMorning.Soothe` | **ACTIVE**, documented debt | 251 |
| Presence check on comfort | `SilentMorning.Complete` | **ACTIVE** | 45 failed sittings |
| Hunger, portions, eating | `WorldState`, `Complete` | **ACTIVE body; eating DEAD in the scenario as written** | eat available 3,620 times, chosen 0 |
| PursuitOutcome | `SilentMorning.Resolve/Keep`, `ScalerEval` need term | **TRACE-ONLY**: moves nothing by design | 185 records |
| World searched-room set | `WorldState.MarkSearched/WasSearched` | **DEAD** (written, never read) | no caller of `WasSearched` |
| Knowledge flags (pantry looked, rooms searched, just watched) | fields of `SilentMorning` | **ACTIVE**, outside the Mind | section 22 |
| Trace | `TraceLog` | **ACTIVE**, write-only for the simulation | no runtime reader |
| `TraceKind.Emotion`, `TraceKind.Action` | `TraceLog` | **DEAD** | never written |
| Reports (`S0Report`, `S1Report`, `DecisionTrace`) | `Sim/` | **TEST-ONLY** (live in Core) | |
| Instruments (`BatchRunner`, `Counterfactual`, `DeliberationAudit`, `MotivationSources`) | `Testing/` | **TEST-ONLY** (compiled into Core) | |
| Validators | `Data/*Validator` | **TEST-ONLY** (never called at load) | only tests call `Validate` |
| Speech | `EventKind.Speech`, `Act` | **DATA-ONLY**: 6 authored backstory events; nothing produces speech | section 18 |
| Player | `leo.json` note "Player character" | **DATA-ONLY** (a comment) | no code |
| LLM / language rendering | none | **ABSENT** | no code |
| Unity integration | none; `Fallow.Core` has `noEngineReferences: true` | **ABSENT** | only template scene |
| `competence_self_belief` in character files | never loaded by `ProfileLoader` | **DATA-ONLY** | |

---

## 4. Actual Causal Pipeline

The pipeline is not a line. It is two loops that meet at the Mind:

```
                 +-------------------------------- the trace (records everything, read by nothing) ------------------------------+
                 |                                                                                                                  |
WORLD EVENT --access--> INTERPRETATION --meaning--> APPRAISAL --contributions--> EMOTION (per type|target, decays)                 |
     ^           |            ^    |                                    |                                                           |
     |           |            |    +--meaning--> BELIEF NUDGE --> BELIEF (never decays)                                            |
     |           |            |    +--meaning--> EXPERIENCE (memory: meaning, topic, who, when, salience)                          |
     |           |            +---- beliefs, ledger (as weights)                                                                    |
     |           |                                                                                                                  |
     |           +-- authored ledger/belief blocks --> LEDGER / BELIEF                                                              |
     |                                                                                                                              |
  CONSEQUENCE <-- ACT <-- DELIBERATION <-- MOTIVES <-- { emotions (4 types), memories of today (4 terms), beliefs (2),           |
     |                        ^   ^                     hunger, ledger (2 entries), traits, values }                              |
     |                        |   +-- costs <-- { traits, values, 1 belief, 1 emotion }                                             |
     |                        +------ percept <-- world truth filtered by room + knowledge flags held in SilentMorning               |
     +-- Soothe writes into another mind's emotions directly (not through perception) ---------------------------------------------+
```

Arrow by arrow. **P** preserved, **T** transformed, **D** discarded, **N** newly created, **I**
inaccessible downstream.

### 4.1 World event -> access

- **Crosses:** a `WorldEvent` (id, day, order, minute, kind, actor, target, act, action, topic, tone,
  directness, valence, intent, summary, witnesses, overhearers, authored effects).
- **Code:** `WorldEvent.AccessFor` (WorldEvent.cs 105-112). Actor is always Witnessed; else witness
  list, overhearer list, else None. In the morning the lists are built by
  `SilentMorning.Happened` (594-628) from room occupancy and `RoomGraph.Audible`.
- **P:** everything, for those with access.
- **T:** membership to `Access` enum.
- **D:** for `None`, everything, and a trace line says so (Simulation.cs 183-187).
- **I:** nothing reaches a mind without access. Verified in code and by S1.1 locality tests.

### 4.2 Access -> interpretation

- **Code:** `Interpreter.Interpret` (Interpreter.cs 81-160).
- **Own intention:** if the perceiver is the actor **and** the event has an intent, the intent is the
  meaning at weight 1.0 and no rule is consulted (line 92). **Morning events are built with intent
  `null`** (SilentMorning.cs 618), so this branch is taken only for authored events.
- **Otherwise:** every rule whose `when` matches contributes `base + sum(level x factor)`. Contributions
  are **summed per label** (line 118). Labels with total <= 0 are dropped (line 122). The largest wins,
  ties broken by label name. Nothing matching gives `neutral` (line 127).
- **P:** access, event.
- **T:** many rules into one winning label.
- **N:** `Weight`, `RunnerUpMeaning`, `RunnerUpWeight`, `Contributions`, a trace record naming every rule
  and term.
- **D (effectively):** everything but the label, see 4.3.

### 4.3 Interpretation -> appraisal

- **Code:** `Simulation.Perceive` 199-205.
- **Crosses:** `MatchContext` carrying the **meaning label**, and one scalar
  `reach x attention(meaning)` (reach 0.75 if overheard).
- **D:** **the interpretation weight, the runner-up and the margin.** They go into `PerceptionOutcome`
  (line 252-254), which no runtime code reads. This is the loss S1.7 measured: one earlier slight
  and six earlier slights gave weights 0.653 and 0.819 and byte-identical feelings, wants and choice.
- **Appraisal itself** (Appraiser.cs 64-150): each rule matching the meaning (and `addressed`,
  `audience_min` for two rules) gives `base + sum(trait/value terms)`, multiplied by the scalar, summed
  per emotion|target and squashed by `Saturate`.
- **N:** `EmotionContribution` list, each with a `Concern` label.

### 4.4 Interpretation -> experience (memory)

- **Code:** Simulation.cs 217-243.
- **Crosses:** meaning, access, the stirred intensities (as salience), event id, day, order, minute,
  actor, target (null for a whole-room target), topic, summary text.
- **T:** intensities into `salience = 0.15 + 0.85 x accumulate`.
- **N:** `Confidence` (1.0 or 0.6), `DominantEmotion`.
- **D:** **the act, action, tone, directness and valence.** A memory cannot say *what* happened, only
  what it meant, what it was about, and who. The witness list and the room are also gone.
- **I:** `Confidence`, `DominantEmotion`, `Access`, `FromOwnIntent`, `Order` and `Summary` are written and
  **read by no runtime code**.

### 4.5 Interpretation -> belief

- **Code:** `ApplyBeliefNudges` (Simulation.cs 257-289).
- **Crosses:** the meaning and the event's circumstances, through the same `MatchContext`.
- **T:** `delta = rule.Delta + sum(terms)` (line 264; only `slights_add_up` has a term, pride). Applied by
  `Accumulate.Toward`.
- **N:** two trace records per nudge, the belief's justification id.
- **D:** the experience itself is not consulted. Beliefs are formed from the *meaning at the moment
  of perception*, never from memory later. **Access is not consulted** by five of six nudge rules,
  so hearing a short count through a wall moves `supplies_short` exactly as seeing it would.

### 4.6 Authored effects -> ledger and belief

- **Code:** `ApplyAuthoredEffects` (291-332).
- Access-gated twice: by the validator when authored, and again at runtime.
- **N:** ledger records and belief moves that no reading produced.

### 4.7 Emotion, memory, belief, ledger, body -> motivation

- **Code:** `Motivator.Raise` (Motivator.cs 89-157). Every one of 7 rules is evaluated for every idle
  person every minute; **no motivation rule has a condition** (census of data).
- Per rule, each scaler is read by `ScalerEval.Evaluate`:
  - trait and value from the profile;
  - emotion from `EmotionSet.Live` (type, optional target);
  - memory by `Recall` (same day only, `salience x 20/(20+minutes)`, `minute -1` counts as fully
    fresh, answered memories skipped);
  - belief confidence;
  - ledger strength;
  - hunger from the percept.
- Shipped `Standing` adds everything (line 177). The knee compresses above 0.85. Several rules for
  the same want combine by `Accumulate.Combine`.
- **P:** each term, with the trace ids it drew on.
- **T:** all terms into one urgency per want (per target for `look_after`).
- **D:** which *feeling* or *memory* it was, beyond the id. Emotions other than anger, anxiety, fear
  and shame are not read at all. Memories other than concern and threat, on two subjects, are not
  read at all.

### 4.8 Motivation -> deliberation -> intention -> act

- **Code:** `Deliberator.Decide` (236-338), `Rank` (350), `PriceOf` (443), `PickWithin` (474);
  `ActionCatalog.Available` and `Endorsed`.
- **Crosses:** urgencies, the percept, the mind (for costs), an intention if one was carried across
  a walk.
- **T:**
  - each want contributes `urgency x fit` to each option its proposals endorse;
  - contributions are **summed across wants**;
  - costs are summed;
  - score = appeal - cost.
- **D:** everything but one scalar per option, and then, outside the band, everything but the top
  option.
- **N:** `Decision` (ranked options with contributions and prices, resolution, margin, ties,
  commitment), and an `Intention` holding only the **leading** want's key, kept only if the act is
  a walk (SilentMorning.cs 288).
- **I:** when a walk served three wants, only the largest is remembered as the reason for it. An
  interruption drops the intention entirely (Begin line 280).

### 4.9 Act -> consequence -> world event

- **Code:** `SilentMorning.Complete` (386-480), `Walk` (482-499), `Happened` (594-628), `Resolve`
  (640-682).
- Acts change `WorldState` (room, hunger, portions) or knowledge flags held in `SilentMorning`
  (`_sawThePantry`, `_searchedBy`, `_watched`), and most become events.
- **D:** the intent. **Every morning event is created with intent `null`**, so its own actor reads it
  through rules meant for witnesses (4.2). The census found all 251 acts of comfort read by the
  comforter as support, feeling grateful toward themselves.
- **D:** what a search or a watch found. Nothing. There is nothing in the world to find (section 14).
- **Side channel:** `Soothe` writes directly into the other person's `EmotionSet` (514-531), with no
  perception involved.

### 4.10 Where the loop is not closed

- **Memory -> belief.** Never: beliefs are only nudged at the moment of perception.
- **Memory -> interpretation.** Never: no interpretation rule reads memory (the capability exists,
  with `RecallHalfLife` 0 at interpretation time, and is unused).
- **Belief -> appraisal.** Never: no appraisal rule reads a belief.
- **Emotion -> interpretation or appraisal.** Never: current mood colours neither.
- **Anything -> a ledger entry.** Never, except authored data.
- **An act -> knowledge about the missing can.** Never.

---

## 5. Module-by-Module Audit

A responsibility, B inputs, C outputs, D state owned, E state read, F state modified, G consumers, H what it
does not do, I status.

### `WorldEvent` (Model/WorldEvent.cs)
- **A.** World truth of one moment.
- **B.** Constructor fields.
- **C.** Access per person, target tests, audience size.
- **D.** Immutable fields.
- **E.** None.
- **F.** None.
- **G.** `Simulation`, `Interpreter` via `MatchContext`, `SilentMorning.Interrupt`, instruments.
- **H.**
  - It does not hold where it happened: `Happened` knows the room, the event does not.
  - `Directness` is read by no rule.
  - `Intent` is null for every event the morning makes.
- **I.** ACTIVE.

### `Simulation` (Sim/Simulation.cs)
- **A.** Runs events past every mind; fades feelings.
- **B.** `WorldEvent`, optional cause trace ids.
- **C.** `EventOutcome`, `PerceptionOutcome` per person.
- **D.** Minds, trace, fade mode, `Needs` delegate.
- **E.** Rules, cast, minds.
- **F.** Experiences, emotions, beliefs, ledger of every mind with access.
- **G.** `SilentMorning`, `Scenario001`, instruments.
- **H.**
  - It does not give anyone knowledge of events they did not perceive.
  - It does not pass interpretation weight on.
  - It does not decay beliefs or ledger.
- **I.** ACTIVE.

### `Interpreter` (Sim/Interpreter.cs)
- **A.** Event -> meaning for one perceiver.
- **B.** Mind, event, access, cast profiles, needs.
- **C.** `InterpretationResult` (meaning, weight, runner-up, contributions).
- **D.** None.
- **E.** Profile, beliefs, ledger, emotions, memories (via scalers), actor profile (age, role).
- **F.** Trace only.
- **G.** `Simulation.Perceive` reads the meaning (and the own-intent flag into memory).
- **H.**
  - It does not read memory or mood (no rule asks).
  - It does not produce `request` or `deception` (in the vocabulary, produced by no rule).
  - It does not reconsider an earlier reading.
- **I.** ACTIVE; the own-intent branch is PARTIALLY ACTIVE.

### `Appraiser` (Sim/Appraiser.cs)
- **A.** Meaning -> feelings.
- **B.** Mind, `MatchContext` with meaning, intensity scale.
- **C.** `EmotionContribution`s with concern.
- **D.** None.
- **E.** Traits, values, perceptiveness (only kinds used by the data).
- **F.** Trace.
- **G.** `Simulation.Perceive` (emotion store, salience), `SilentMorning.Interrupt` (event's dominant
  intensity).
- **H.**
  - It does not see interpretation weight, beliefs, ledger, memory or current emotion.
  - It does not compute the concern (a label on the rule).
  - `reassurance`, `neutral` and three self-meanings produce nothing.
- **I.** ACTIVE.

### `EmotionSet` (Model/EmotionSet.cs)
- **A.** Current feelings.
- **B.** Contributions, decay factor, soften.
- **C.** `Live` sorted, `Dominant`, intensity.
- **D.** Instances keyed type|target with intensity, concern, last event, causes.
- **E.** None.
- **F.** Itself.
- **G.**
  - `ScalerEval` emotion terms (motivation: 4 types; one cost: shame).
  - `ShowWhatShows` (dominant).
  - Instruments.
- **H.**
  - It does not keep causes apart (S1.1 P1 miss).
  - `Concern` and `LastEventId` are never read at runtime.
  - `IntensityAny` is test-only.
- **I.** ACTIVE.

### `Mind` / `Experience` (Sim/Mind.cs, Model/Experience.cs)
- **A.** One person's inside.
- **B.** Experiences, outcomes.
- **C.** Lists.
- **D.** Profile, beliefs, ledger, emotions, experiences, outcomes.
- **E.** None.
- **F.** Itself.
- **G.** Every stage via scalers.
- **H.**
  - Knowledge of the morning (pantry looked, rooms searched, who was just watched) is **not** in
    the Mind. It lives in `SilentMorning`.
  - Experience does not keep the act.
- **I.** ACTIVE; 6 Experience fields PRESENT BUT DISCONNECTED.

### `BeliefStore` (Model/BeliefStore.cs)
- **A.** Propositions with confidence.
- **B.** Seeds, nudges.
- **C.** Confidence, `Belief` with justifications.
- **D.** Dictionary.
- **E.** None.
- **F.** Itself.
- **G.** `ScalerEval.Held` in interpretation, motivation and cost rules.
- **H.**
  - No decay.
  - No contradiction handling.
  - A negative nudge on an absent belief creates it at 0.00 with a justification (census: several).
- **I.** ACTIVE.

### `Ledger` (Model/Ledger.cs)
- **A.** Named deeds about others.
- **B.** Authored effects.
- **C.** Strength (saturating).
- **D.** Records.
- **E.** None.
- **F.** Itself.
- **G.** `ScalerEval.Remembered`: `look_after` (2 entries), one interpretation rule (1 entry).
- **H.** It is never written by the simulation; `SummaryAbout` is report-only.
- **I.** PARTIALLY ACTIVE.

### `ScalerEval` (Rules/ScalerEval.cs)
- **A.** One arithmetic for every weight.
- **B.** Scalers, mind, context.
- **C.** `ScalerTerm`s with level, amount, drew ids, kind, answered.
- **D.** None.
- **E.** Profile, emotions, experiences, beliefs, ledger, needs, latest outcome.
- **F.** None.
- **G.** Every rule stage.
- **H.**
  - Memory recall across days (filtered out).
  - Aging of untimed memories.
  - Scaler kind `constant` and field `by` are unused by data.
- **I.** ACTIVE.

### `Motivator` (Sim/Motivator.cs)
- **A.** State -> wants.
- **B.** Mind, percept.
- **C.** `Motive`s with terms and trace ids.
- **D.** None.
- **E.** Via scalers.
- **F.** Trace.
- **G.** `Deliberator`, instruments.
- **H.**
  - Conditions are supported and used by no rule, so every want is considered everywhere.
  - Under shipped `Standing`, traits and values raise wants with nothing happening.
- **I.** ACTIVE (A); B/B0 NOT SHIPPED.

### `ActionCatalog` (Sim/ActionCatalog.cs)
- **A.** What is physically possible now.
- **B.** Percept, dynamics.
- **C.** Options with durations.
- **D.** None.
- **E.** Percept flags.
- **F.** None.
- **G.** `Deliberator`.
- **H.**
  - It does not check whether an act can achieve anything (a search that can find nothing is
    available).
  - It does not include speech.
  - Availability reasons are not traced.
- **I.** ACTIVE.

### `Deliberator` (Sim/Deliberator.cs)
- **A.** Wants + options -> one act.
- **B.** Mind, percept, motives, rng, intention.
- **C.** `Decision`.
- **D.** None.
- **E.** Rules, costs via mind.
- **F.** Trace.
- **G.** `SilentMorning`, instruments.
- **H.**
  - No plans beyond one walk.
  - No expected value or uncertainty.
  - As shipped, no check that a walk's end is worth doing.
  - Appeal is summed across wants (breadth beats urgency).
- **I.** ACTIVE; `means: end` PRESENT, NOT SHIPPED.

### `SilentMorning` (Sim/SilentMorning.cs)
- **A.** The world clock, acts, consequences, visibility of distress, interruptions.
- **B.** Simulation, rules, world, rng, day.
- **C.** `MorningResult`, decision hook.
- **D.**
  - Busy/stopped acts.
  - Intentions.
  - Knowledge flags (`_sawThePantry`, `_searchedBy`, `_watched`).
  - Distress visibility set.
- **E.** World, minds (emotions for visibility, experiences for interrupts).
- **F.**
  - World (room, hunger, portions, searched set).
  - **Other minds' emotions** (Soothe).
  - Outcomes.
- **G.** `Scenario001`, instruments.
- **H.**
  - It does not give morning acts an intent.
  - It does not traverse intermediate rooms on a walk.
  - It does not represent anything a search could find.
- **I.** ACTIVE.

### `Percept` (Model/Percept.cs)
- **A.** What one person can know now.
- **B.** Built by `See`.
- **C.** Room, present, adjacent, hunger, food visible, flags, house graph.
- **D.** Snapshot.
- **E.** None.
- **F.** None.
- **G.** `Motivator`, `Deliberator`, `ActionCatalog`, `SituationCondition`.
- **H.**
  - It does not include last-known locations of people.
  - It does not include portions count (only whether food is there when standing in the pantry
    room).
  - `Imagine` exists for M2 only.
- **I.** ACTIVE.

### `WorldState`, `RoomGraph` (Model)
- **A.** House truth.
- **B.** Placement, ticks, eating.
- **C.** Rooms, occupancy, hunger, portions, adjacency, audibility, distance.
- **D.** Those.
- **E.** None.
- **F.** Itself.
- **G.** `SilentMorning`.
- **H.** `WasSearched` has no caller.
- **I.** ACTIVE, one dead member.

### `Rng` (Model/Rng.cs)
- **A.** Deterministic randomness.
- **B.** Seed, fork purpose.
- **C.** Doubles.
- **D.** State.
- **G.** `Deliberator.PickWithin` only.
- **H.** `NextIndex` unused.
- **I.** ACTIVE (one consumer).

### `TraceLog` (Tracing/TraceLog.cs)
- **A.** Causal record.
- **B.** Every stage.
- **C.** Records, chains, `Why`.
- **D.** Records.
- **G.** Instruments, reports, tests only.
- **H.**
  - Never read by the simulation.
  - `Emotion` and `Action` kinds never written.
- **I.** ACTIVE (instrument).

### Loaders and validators (Data/)
- **A.** Read and check JSON.
- **H.**
  - Validators are called only by tests.
  - `ProfileLoader` ignores `competence_self_belief`.
  - `VocabularyLoader.Settings` is unused.
- **I.** Loaders ACTIVE; validators TEST-ONLY.

### Instruments and reports (Testing/, Sim/S0Report, S1Report, DecisionTrace)
- **I.** TEST-ONLY. They live in the `Fallow.Core` assembly. None is called by the simulation.

---

## 6. Writer -> Reader Map

"Runtime reader" means code that runs during a simulation and can change what somebody feels,
believes, wants or does. Trace, reports and instruments do not count.

### Interpretation output
```
InterpretationResult.Meaning
    written by: Interpreter.Interpret
    read by:    appraisal conditions; belief nudge conditions; Experience.Meaning; Profile.Attention(meaning)
    affects:    every feeling, every rule-formed belief, what recall can find
InterpretationResult.Weight / Margin / RunnerUpMeaning / RunnerUpWeight / Contributions
    written by: Interpreter.Interpret -> PerceptionOutcome.InterpretationWeight, RunnerUpMeaning
    read by:    trace, tests, S17 instruments
    never read by: any runtime code                                   PRODUCED BUT NEVER CONSUMED
```

### Memory
```
Experience.Meaning, Topic, TargetId, ActorId, Day, Minute
    written by: Simulation.Perceive
    read by:    ScalerEval.Recall (filters), Until (answers)
    affects:    find_out (concern/threat about missing_can), look_after (concern/threat about target)
Experience.Salience
    read by:    ScalerEval.Recall                                     ACTIVE
Experience.Confidence (0.6 when overheard)                            PRODUCED BUT NEVER CONSUMED
Experience.DominantEmotion, Access, FromOwnIntent, Order, Summary     PRODUCED BUT NEVER CONSUMED (reports/trace only)
Memories of any meaning other than concern/threat, or of any subject
other than missing_can / a present person                             STORED, NEVER RECALLED
Memories of earlier days (26.9 % of those held at decisions)         STORED, UNREACHABLE
```

### Beliefs
```
supplies_short
    written by: seeing_the_shelf_for_yourself (+0.55), watching_it_go (+0.25)  [rule, live]
    read by:    guard_supplies want 0.5; cost taking_it_when_there_is_little 0.5; interpretation somebody_helping_themselves 0.35
    affects:    guard_supplies in every decision (4,066 of 4,066); price of eating (3,620 pricings)
answerable_for(me, missing_can)
    written by: seeing_where_the_food_went (+0.9)                        [rule, live]
    read by:    the_search_is_for_what_you_did 1.0 (interpretation only)
    affects:    whether a search reads as a threat (S1.1: Mara's morning above noise)
tendency(x, does_not_respect_me)
    written by: slights_add_up (+0.15 + pride), kindness_wears_it_down (-0.1)   [rule, live]
    read by:    corrected_by_a_junior_with_people_watching 0.4, being_watched 0.3 (interpretation only)
tendency(x, treats_me_like_a_child)
    written by: being_handled_confirms_being_handled (+0.12)            [rule, live]; seed (Mara)
    read by:    your_things_gone_through 0.4, being_watched 0.4 (interpretation only)
tendency(x, needs_to_be_in_charge)
    written by: seeds only (Elena, Leo)                                  CONSUMED BUT NEVER PRODUCED BY THE SIMULATION
    read by:    being_ordered_about 0.4
role_claim(me, leads_family)
    written by: seeds only (Daniel 0.8, Elena 0.6)                       HAND-AUTHORED
    read by:    find_out want 0.3; being_told_to_let_it_go 0.3
more_knowledgeable(x, domain)
    written by: seeds; authored belief_effects on b03                    HAND-AUTHORED
    read by:    nothing                                                  PRODUCED BUT NEVER CONSUMED
tendency(x, makes_risky_calls), tendency(x, keeps_things_from_me)
    written by: seeds (Leo, Mara)                                        HAND-AUTHORED
    read by:    nothing                                                  PRODUCED BUT NEVER CONSUMED
```

### Ledger
```
comforted_me, protected_me    written: authored (b08, b09)    read: look_after want 0.15 each    ACTIVE (1,120 non-zero terms)
overruled_me                  written: authored (b05)         read: corrected_by_a_junior 0.3    ACTIVE (backstory readings)
protected_family, proved_right, raised_voice, raised_voice_at_me, searched_my_things
                              written: authored               read: nothing                       PRODUCED BUT NEVER CONSUMED
any entry                     written by the simulation: never                                    HAND-AUTHORED ONLY
```

### Emotions
```
anxiety      read by: keep_peace want 0.35; visible distress
fear         read by: avoid_exposure want 0.35; visible distress
shame        read by: avoid_exposure 0.8, restore_standing 0.5, cost not_while_they_are_watching 0.3; visible distress
anger        read by: restore_standing 0.45 (toward anyone); visible distress
hurt         read by: visible distress only
gratitude, relief, frustration
             read by: no want, no cost, not visible; only by being Dominant (which can hide distress),
             by raising salience, and by interrupting                           NO MOTIVATIONAL OUTLET
warmth       produced by: no rule                                               VOCABULARY ONLY
EmotionInstance.Concern, LastEventId                                            PRODUCED BUT NEVER CONSUMED
```

### Motivation and urgency
```
Motive.Urgency     written: Motivator     read: Deliberator (appeal), Leading, Intention
Motive.Terms       read: only by being summed into urgency; otherwise trace and instruments          TRACE-ONLY beyond urgency
Leading want       read: Intention for a walk (the only reason kept), ActionRecord, trace
```

### Action outcomes
```
PursuitOutcome (Kind, Before, After)   written: SilentMorning.Resolve/Keep    read: need scaler adds its trace id and a note    TRACE-ONLY
ActionRecord.Outcome (string)          written: SilentMorning.Note            read: instruments only                          TEST-ONLY
World portions, hunger                 read: percept (hunger; food visible), eat                                               ACTIVE
Knowledge flags                        read: ActionCatalog availability                                                        ACTIVE, outside the Mind
WorldState._searched                   read: nothing                                                                           DEAD
```

### Speech information
```
Act (tell/suggest/refuse/demand), Tone, Topic, Addressed
    written by: authored backstory speech events only (6)
    read by:    interpretation conditions (7 rules on acts, 4 on tones)
Directness    read by: nothing                                                  PRODUCED BUT NEVER CONSUMED
Summary text  read by: trace, reports                                           never by a rule
```

---

## 7. State Lifecycle

| State | Who writes | Who reads | When it changes | How | Without a relevant event? | Across time | Across runs | Can go stale | Decay / reset / expiry |
|---|---|---|---|---|---|---|---|---|---|
| Experience (memory) | `Perceive` | `Recall` (2 wants) | on perception | appended, never edited | no | kept for ever; recall is same-day only | no (fresh minds per run) | **yes**: untimed memories stay fully fresh all day | recall fades by 20/(20+min); **untimed: never**; answered by `until` |
| Belief | seeds, nudges, authored effects | interpretation, 2 wants, 1 cost | on perception | `Toward` | no | **for ever** | no | **yes** (S1.7: identical after 30 days) | **none** |
| Interpretation weight | `Interpreter` | nobody at runtime | per perception | computed | no | not stored beyond trace | no | n/a | discarded |
| Emotion | `Perceive`, `Soothe` | 4 wants, 1 cost, visibility, dominance | perception; every fade; being sat with | `Toward`; `x factor^fades`; `x 0.55` | **yes: decay on the clock, and Soothe from another person** | minutes to an hour | no | no | decays; removed below 0.05; anxious people decay slower |
| Motive / urgency | `Motivator` | `Deliberator` | re-raised at every decision | from state | **yes, under Model A**: traits and values raise it with nothing happening | not stored | no | n/a | not stored, so no decay needed |
| Intention | `Deliberator`/`Begin` | next decision after a walk | when a walk is chosen | leading want key | no | until arrival | no | **yes**: kept even if the reason disappeared, checked on arrival | dropped on arrival, or on interruption |
| Ledger entry | authored effects | 2 wants, 1 interpretation rule | on perceiving an authored event | appended | no | for ever | no | yes | none |
| Hunger | `WorldState.Tick`, eating | percept -> `get_food`, eat | every minute; eating | +0.004 x rate; -0.45 | yes (the body) | the morning | no | no | n/a |
| Portions | `TakePortion` | percept (food visible), count event | eating | -1 | no | the morning | no | no | n/a |
| Room occupancy | `Place` (walk end) | percept, witnesses, hearers | when a walk completes | teleport | no | the morning | no | no | n/a |
| Pantry looked (`_sawThePantry`) | `Complete(CheckPantry)` | availability | once | set | no | **whole morning** | no | **yes**: after eating changes the shelf you can never look again | none |
| Rooms searched by me (`_searchedBy`) | `Complete(SearchRoom)` | availability, `nearest_unsearched` | once per room | set | no | whole morning | no | yes | none |
| Just watched (`_watched`) | `Complete(Observe)` | availability | per watch | minute stamp | **yes: expires after 15 minutes of clock** | 15 min | no | n/a | fixed timer |
| Visible distress set | `ShowWhatShows` | the same | each minute | threshold on emotion x expressiveness | yes (decay can end it) | while felt | no | no | n/a |
| PursuitOutcome | `Resolve`, `Keep` | trace link only | eating; lapse on arrival | appended | no | morning | no | n/a | none |
| Action history (`ActionRecord`) | `Begin`, `Note` | instruments only | per decision | appended | no | morning | no | n/a | none; no mind can see it |
| Trace | every stage | nobody at runtime | always | appended | no | run | no | n/a | none |

**Across runs:** nothing persists. Every run builds new minds, replays the backstory, and discards all
state at the end. There is no save, no second day of morning, and no long-term memory beyond one
authored backstory replayed identically.

**Temporal validity:** the only time-aware reader is `Recall`, and only within a day. Beliefs, ledger,
knowledge flags (except watching) and intentions have no notion of how long ago.

---

## 8. Knowledge Locality

### Where it is enforced (code paths)

1. **Access gate.** `WorldEvent.AccessFor` and `Simulation.Perceive` stop at `None` (Simulation.cs
   183-187). Nothing about an unperceived event reaches that mind. The S1.1 locality tests prove it
   for memories, grudges and feelings. S1.7 arm U shows 0.000 belief for an unseen event.
2. **Who perceives a morning event** is computed from the world, never authored:
   `SilentMorning.Happened` (599-610) uses room occupancy and `RoomGraph.Audible`.
3. **Authored effects are access-gated twice**: `ScenarioValidator` refuses to author a ledger entry
   or belief for someone without access, and `ApplyAuthoredEffects` checks again (301, 315).
4. **Decisions see only a Percept and their own Mind.** `Motivator`, `Deliberator` and
   `ActionCatalog` receive nothing else. `SituationCondition` reads only the percept.
5. **Intent is private.** Only the actor's reading uses `e.Intent` (Interpreter.cs 92).
6. **Time passes for everyone equally** on a clock, not per event (S1.1 fix), so an event cannot
   fade the feelings of someone who did not perceive it.
7. **The trace cannot leak into behaviour**: no runtime code reads it (verified by search).

### Where it is not enforced, or is weaker than it looks

| Finding | Evidence | Consequence |
|---|---|---|
| **Soothe writes into another mind** without that person perceiving anything | SilentMorning.cs 514-531; documented debt since S1.1 | 251 direct writes in 50 mornings. S1.4 found people come right about as often without it. |
| **Food is visible from world truth** by standing in the pantry room, with no event and no look | `See` line 378: `FoodWithinReach = world.Portions > 0` | Eating availability depends on a fact nobody perceived; the check-pantry act adds only the count as an event |
| **Knowledge of one's own morning lives in the world object**, not the Mind | `_sawThePantry`, `_searchedBy`, `_watched` in `SilentMorning` | It is local (per person) but invisible to memory, belief, trace and counterfactual tools, and never forgotten |
| **Hearing is treated as seeing for beliefs** | 5 of 6 nudge rules have no `access` condition; `Experience.Confidence` is unread | Overhearing a short count moves `supplies_short` +0.55 like looking at the shelf |
| **Bystanders update beliefs about themselves** from events aimed at others | `kindness_wears_it_down`, `slights_add_up` have no `addressed` condition | Watching Elena sit with Mara lowers the watcher's belief that Elena does not respect *them* |
| **Actors read their own morning acts as witnesses would** | intent null (618); census: 251 self-gratitude, 251 self-belief nudges | Not a leak of truth, but a mind not knowing its own intention |
| **Seeds inject beliefs with no evidence** | `Profile.InitialBeliefs` | By design (a life before the scenario); unlabelled in the trace except by having no justification |
| **Relative age and family role are universal knowledge** used as rule conditions | `RelationOfActor`, `SelfRoles` | Reasonable in a family; means rules can condition on a person attribute other than traits |
| **The M2 switch imagines the target present at a destination** | `Deliberator.Foresee`, not shipped | A knowledge assumption, disclosed in S1.6 |

### Player knowledge

**NOT IMPLEMENTED.** There is no player, no player-facing view and no player knowledge store. The
only mention is a note in `leo.json`. The questions "can the player know something NPCs cannot" and
the reverse cannot be answered from anything that exists. The trace, which knows everything, is a
developer instrument.

### Overall

World truth, character knowledge and character belief are **genuinely separated in code** for the
perception of events, and this is the strongest-evidenced property of the system. The separation is
weaker at the edges where the world acts on a mind directly (Soothe, food visibility, knowledge
flags) and where access is ignored after perception (belief nudges, confidence). Player knowledge
does not exist.

---

## 9. Memory

**What "memory" means in the implementation: a per-person list of `Experience` records, one per
perceived event, each holding what the event meant to them.**

| Question | Answer | Evidence |
|---|---|---|
| What is stored? | meaning, topic, actor, target (null if the whole room), day, order, minute, access, confidence, salience, dominant emotion, event id, summary text, trace id | Experience.cs; Simulation.cs 221-243 |
| What causes storage? | any access other than None, whatever the reading, including `neutral` and one's own acts | census: 3,229 neutral memories; 1,356 own-act memories |
| Event-specific? | yes, one per event per person | |
| Reconstructed? | no | |
| Summarised? | no; never merged | |
| Who did what? | **who** yes (actor, target); **what** no: action, act, tone, valence, directness are not kept | Experience has no such fields |
| Context? | topic only; not the room, not who else was there | |
| Interpretation? | **yes, and only the interpretation** (winning label) | |
| Emotional significance? | salience (from what the moment stirred) is read; dominant emotion is not | |
| Time? | day, order, minute; **minute is -1 for all authored events** | S1.6; data has no `minute` |
| Decay? | the record never goes; how hard it presses decays within its day, `salience x 20/(20+elapsed)` | ScalerEval.cs 222-232 |
| Less relevant without disappearing? | yes: freshness, and `until` answers | S1.4 |
| Old memories affecting interpretation indefinitely? | **memories never affect interpretation**; no interpretation rule reads memory | data census |
| Memory affecting belief? | **no**; beliefs move at the moment of perception from the meaning, and are never re-derived from memory | `ApplyBeliefNudges` |
| Belief affecting later interpretation? | **yes** | S1.7 E1, E2 |
| "I remember it happened" vs "I believe what it meant"? | the Mind can hold "I remember that moment as disrespect" (memory) and "I believe he treats me like a child" (belief) separately, but **cannot hold "what happened" apart from "what it meant"**: there is no record of the act in the mind to reinterpret | |

**Which memories matter at all:** four memory terms, in two wants.
- `find_out`: concern or threat about `missing_can`.
- `look_after`: concern or threat about that person, until reassurance.

Summed over every decision in fifty mornings, people held 128,117 memories:
- **26.9 % are from earlier days** and unreachable by recall.
- Of the rest, only those meanings and subjects are ever read.
- Memories of support, disrespect, challenge, own intentions and neutral readings are stored and
  never recalled.

**Current status of the persistence issues:**
- **Untimed memories never age (S1.6).** **Still present in the shipped configuration.** The loader
  can read a minute; no event sets one. The census shows at least 2,932 memory-term reads on
  untimed memories (the opening count and `p03`), against 621 on the most-read timed one.
- **Beliefs never decay (S1.7).** **Present and unchanged.** There is no decay code for beliefs
  anywhere.
- **Recall is day-scoped.** Present, by design (`ScalerEval.cs` 138). This is why "yesterday" can
  only work through beliefs, and why the S1.7 persistence finding is about belief, not memory.

---

## 10. Beliefs

| Aspect | Implementation |
|---|---|
| Representation | `Belief{Predicate, Args, Confidence in 0..0.995, Justifications: trace ids}` keyed `predicate(args)` |
| Created by | profile seeds (no justification); authored `belief_effects` (access-gated); nudge rules on a meaning (creating the entry at 0 if absent, even for a negative nudge) |
| Modified by | `Accumulate.Toward`: a positive delta closes that fraction of the room left, a negative one removes that fraction of what is there |
| Strength | confidence only; no separate evidence count |
| Subjects | via args: a person (`tendency`, `role_claim`, `answerable_for`, `more_knowledgeable`) or none (`supplies_short`) |
| Person-specific | yes |
| Event-specific | only through justifications (trace ids) |
| Decay | **none** |
| Contradictions | coexist freely; no predicate has an opposite, and nothing reconciles (S0: Daniel holds "Leo knows more" 0.58 and "Leo does not respect me" 0.56) |
| Normalisation | none |
| Personality in learning | `slights_add_up` delta scales with pride; others fixed |
| Influences interpretation | yes: 6 predicates across 7 rules |
| Influences appraisal | **no** |
| Influences motivation | yes: `supplies_short`, `role_claim` |
| Influences deliberation directly | **yes**: `supplies_short` prices eating, bypassing motivation |

**Belief exists vs belief changes behaviour:**

| Belief | Exists | Changes future behaviour? | Evidence | Label |
|---|---|---|---|---|
| `supplies_short` | formed from the opening count, every run | **yes**: raises `guard_supplies` at every decision, and prices eating out for everybody | census (4,066 terms; eat chosen 0 of 3,620); S1.3 | PROVEN |
| `answerable_for` | formed by the culprit's own act | **yes**: turns other people's searches into threats, which reaches wants and, for Mara, a morning above noise | S1.1 | PROVEN (Mara); FAILED (Daniel) |
| `tendency(x, treats_me_like_a_child)` / `does_not_respect_me` | formed from slights and kindness | **reading yes, action rarely**: flips a reading after 11 slights; act changed in 2 of 27 circumstances, both seed-settled ties; below noise over a morning | S1.7 | PROVEN for reading; FAILED for behaviour |
| `role_claim` | authored | **yes**: keeps `find_out` raised for Daniel and Elena with nothing missing | S1.5 section 7 | PROVEN |
| `tendency(x, needs_to_be_in_charge)` | authored | weights one reading of demands; cannot change | S1.7 E5 | PLAUSIBLE, and inert over time |
| `more_knowledgeable`, `makes_risky_calls`, `keeps_things_from_me` | authored | **no**: nothing reads them | data census | PROVEN inert |

---

## 11. Interpretation

**What it produces:** `InterpretationResult{Meaning, Weight, RunnerUpMeaning, RunnerUpWeight,
FromOwnIntent, Contributions}` and a trace record listing every matching rule with its arithmetic.

**How competing readings are generated:** every rule whose condition matches the event (act, action,
topic, tone, valence, access, addressed, relation, role, audience) contributes
`base + sum(level x factor)`. Conditions can never read a trait, value or belief. Those enter only as
scalers.

**How one is selected:**
1. Totals are summed per label (two rules for `disrespect` add together).
2. Labels at or below zero are dropped.
3. The largest total wins; exact ties go to the alphabetically first label.
4. If nothing matched, the reading is `neutral`.
5. For an actor with an authored intent, the intent is the reading.

**Is selection categorical?** Yes, at the output. Inside, it is continuous and additive.

**Where the strength goes:**
```
INTERPRETATION
    label     = preserved -> appraisal conditions, belief nudge conditions, memory, attention scale
    weight    = calculated -> PerceptionOutcome.InterpretationWeight -> read by nothing at runtime
    runner-up = calculated -> PerceptionOutcome.RunnerUpMeaning      -> read by nothing at runtime
    margin    = derivable  -> not stored
    per-rule contributions -> trace only
```

| Does it affect... | Answer |
|---|---|
| appraisal | only through the label and `attention(label)` |
| emotion | only through appraisal |
| motivation | only through emotions, memories of that label, and beliefs nudged by that label |
| deliberation | no direct path |

**Verdict: a hybrid, and specifically *continuous weighing feeding a categorical selector whose
continuous output is discarded*.** Downstream behaviour responds to interpretation as a step
function.

- **S1.7 D4:** weights 0.653 and 0.819 on the same label gave byte-identical downstream state.
- **S1.7 E2:** one downstream state across eleven history levels, then a step at the twelfth.

Two properties of the implementation matter as much as the discard:
- **35.7 % of all readings are `neutral`** (3,041 of 8,523), because no rule matched. Most movement,
  most bystander searches, and every observer's own watching mean nothing, and leave a memory
  nobody reads.
- **Summation per label rewards breadth.** A reading supported by several weak rules can beat one
  supported by a single strong rule, which is the interpretation-stage twin of the summed-appeal
  problem S1 found in deliberation.

---

## 12. Appraisal / Emotion

| Input | Received? |
|---|---|
| the winning meaning | yes (every appraisal rule conditions on it) |
| interpretation strength | **no** |
| belief strength | **no** (engine supports it; no rule uses it) |
| context | only `addressed` (1 rule) and `audience_min` (1 rule) |
| personality (traits) | yes: 26 trait terms |
| values | yes: 15 value terms |
| perceptiveness | yes: 1 term |
| current emotion | **no** |
| access | yes, as a flat x0.75 for overheard |
| attention (per meaning) | yes, as a multiplier on all feelings from that meaning |

- **Event-specific:** yes, per perceived event.
- **Accumulation:** `EmotionSet.Add` uses `Toward` per type and target. The same feeling about the
  same person deepens; its causes are merged into one number (S1.1's P1 miss).
- **Decay:** every fade multiplies by `0.6 + 0.25 x anxious` (cap 0.95). One fade is 3 minutes in the
  morning, one event in the backstory. Below 0.05 a feeling is removed.
- **Conflict:** feelings coexist; nothing inhibits another. The strongest (`Dominant`) decides
  visibility and nothing else.
- **Derived or assigned:** derived from appraisal, with one exception, `Soothe`, which multiplies
  fear and anxiety by 0.55 in another person directly.

**Where "event label -> emotion" happens without meaningful appraisal.** Everywhere, in the sense
the brief means.
- 18 of 18 appraisal rules condition on the meaning, and are weighted only by the perceiver's traits
  and values.
- There is no appraisal of goal relevance, agency, controllability, coping or expectation.
- The `concern` each rule names is a fixed label written on the rule, stored on the feeling, and
  **read by nothing**.
- Own-intention meanings map directly to fixed feelings:
  - `protect` gives anxiety;
  - `took_what_was_not_mine` gives shame and fear;
  - `assert_authority` gives anger toward the target;
  - `take_responsibility`, `share_information` and `prevent_argument` give nothing.
- `reassurance` and `neutral` give nothing.

**It is still genuinely personal:** the same label feels different to different people. S0: Daniel's
shame versus Elena's anxiety. S1.7: fear and anxiety versus hurt, frustration, anger and shame when
the label flips. **The same event producing different emotions through different interpretation is
proven** (S0 b05; S1.7 E1).

**The emotional vocabulary is only half connected to behaviour.** Of the eight feelings produced:
- anxiety, fear, shame and anger raise wants;
- hurt only makes distress visible;
- gratitude (the feeling most often being carried at a decision, 4,590 times), relief (3,103) and
  frustration (2,197) raise no want, set no price and are not visible distress. Their only effects
  are becoming dominant (which can *hide* visible distress, the S1.4 mechanism), raising a memory's
  salience, and interrupting whoever is busy.

---

## 13. Motivation

**How a want is made** (shipped, Model A): for each of 7 rules, with no condition, sum every term,
compress above 0.85, combine rules for the same want. `look_after` is raised once per person present.

| Want | Circumstance terms | History terms | Authored | Trait / value terms | Standing-only in 50 mornings |
|---|---|---|---|---|---|
| `get_food` | hunger | (outcome record, trace only) | | | 0 |
| `avoid_exposure` | shame, fear | | | | 0 (not raised with neither) |
| `find_out` | memory of concern/threat about the can | | `role_claim` | control, fairness, dominant | 0 as written (an untimed memory or an authored belief is always there) |
| `guard_supplies` | | `supplies_short` | | family_safety, cautious | 0 as written (`supplies_short` always there) |
| `keep_peace` | anxiety | | | family_safety, empathetic, cautious | 1,337 |
| `restore_standing` | shame, anger | | | respect, proud | 2,976 |
| `look_after` (each person) | memory of concern/threat about them | ledger `comforted_me`, `protected_me` | | empathetic, closeness | 6,940 |

**Quantified (census and S1.5 diagnosis, both on the shipped rules):**
- 32,555 wants raised; **11,253 (34.6 %) moved only by traits and values**.
- Non-zero terms by kind: trait 29,713, value 18,986, emotion 8,352, belief 6,185, memory 4,705, need 4,066,
  ledger 1,120.
- **53.0 % of all urgency comes from traits and values** (S1.5 diagnosis).
- Every one of the 2,149 choices to stand still was credited by both standing proposals (`let_it_be`,
  `leave_it_alone`); `keep_peace` was the leading want in 2,149 decisions.
- Decisions led by no want: **0 of 4,066**. Somebody always wants something, largely because of the
  standing part.

**Answers to the brief's questions, for the shipped model:**

| Question | Answer |
|---|---|
| Is the cause traceable? | yes, term by term to the records drawn on; trait and value terms rest on nothing |
| Generated from current circumstances? | partly (emotion, hunger, memory of today) |
| From a trait or value directly? | **yes, as standing additive terms** (A); switchable to responses (B) but not shipped |
| From emotion? | 4 emotion types |
| From belief? | 2 beliefs, one authored and never changing |
| From memory? | 4 terms, same day only |
| From a standing desire? | **yes**: the trait/value part is a standing desire in all but name, and so are `role_claim` (authored) and the untimed opening memory |
| Does urgency have a causal source? | only for the non-disposition part |
| Can motivation exist without a relevant circumstance? | **yes: 34.6 % of wants** |

**Remaining versions of the standing-want architecture, all live:**
1. **Model A itself** (shipped).
2. **`role_claim`**: an authored belief that nothing can change keeps `find_out` raised for two people.
3. **The untimed opening memory**: a circumstance that never ages keeps `find_out` raised all morning.
4. **`supplies_short`**: an evidenced belief that never decays keeps `guard_supplies` raised at every
   decision. This one is honest (the shelf *is* short), but it behaves as a standing want because
   nothing can lower it.
5. **Two proposals that always credit standing still** (`let_it_be`, `leave_it_alone`), 4,066 of 4,066
   decisions.

---

## 14. Deliberation / Actions

### From motivation to act

1. **Candidates** (`ActionCatalog.Available`, from the percept only):
   - wait, always;
   - observe each person not watched in the last 15 minutes;
   - comfort each person present;
   - walk to each adjacent room and to the nearest room of each tag (pantry, common, private) and
     the nearest unsearched one;
   - check the pantry if standing in it and never looked this morning;
   - eat if food is visible;
   - search if this room was never searched by me.
2. **Preconditions** are exactly those gates. None asks whether the act can achieve anything.
3. **Credit** (`Rank`): each want gives `urgency x fit` to each option its proposals endorse. Targeting
   resolves people and rooms. Credits are **summed across wants**.
4. **Cost** (`PriceOf`): each matching cost rule adds `base + sum(terms)`. Terms are traits and values,
   with one belief (`supplies_short`) and one emotion (shame).
5. **Score** = appeal - cost; ranked.
6. **Intention:** after a walk, only options serving the carried want are considered, unless it is no
   longer wanted, nothing here serves it, or the best way costs more than it is worth.
7. **Ambiguity:** options within 0.08 of the top are a band; a seeded pick weighted by distance into
   the band chooses.
8. **The intention formed** is the leading want (largest single contribution), kept only for a walk.

| Factor | Present? | How |
|---|---|---|
| means/end reasoning | **no** (shipped); one-step foresight for walks exists as a switch | section below |
| destination evaluation | tag and nearest; `nearest_unsearched` for looking | |
| costs | yes | |
| urgency | yes | |
| personality | through urgency (A: standing), fit is fixed, costs are trait-weighted | |
| values | same | |
| current circumstances | percept gates and conditions (alone, others present, somebody else's room, searched here) | |
| known information | percept only | |
| uncertainty | **none represented** | no probabilities or expected outcomes |
| ambiguity | fixed absolute band 0.08 | |
| randomisation | seeded, only inside the band | section 15 |
| tie-breaking | inside the band by the pick; exact score ties outside it by option key order | |

### What S1.6 changed, traced in code

1. **`Deliberator.Rank` gained a `lookAhead` flag** (line 350). It is true only when
   `Deciding.Means == "end"` (`WeighsMeansByTheirEnds`, line 341). When true, before a walk is
   credited to a want, `Foresee` (425) builds `Percept.Imagine(destination)` and ranks the non-walk
   options there with every current want. The walk is credited only if the best option serving that
   want scores above zero (383-393), and the trace records a `foresaw` line.
2. **`ScenarioLoader.ReadEvent`** reads an optional `minute`.
3. **Neither is used by the shipped data.** `decisions.json` has no `means` key, so `lookAhead` is false,
   and `Rank` computes exactly what `Decide` computed before S1.6. No event sets `minute`. **The
   means/end defect is therefore live in the shipped simulation.** On these seeds, all 185 walks taken
   for food lapsed on arrival (S1.5 `walks.md`, Model A), of 188 lapses in all (census).
   Model A's standing still hides most of it, as S1.5 showed.

### Other instances of the same general problem

**A means selected because its motivational source is attractive, without verifying that the end is
achievable or worthwhile.** Found, not fixed:

| Means | Want | Why the end is unverified | Evidence |
|---|---|---|---|
| `somewhere_worth_looking` (walk to an unsearched private room) | `find_out` | shipped: whether searching there is affordable is not checked | S1.6 (702 of 759 lapses foreseeable) |
| `go_where_the_food_is`, `keep_it_in_sight` | `get_food`, `guard_supplies` | shipped: whether eating is affordable is not checked; "in sight" is not a state anything reads | S1.5 `walks.md`: 185 food walks, all lapsed |
| `be_where_they_are` (walk to the nearest common room) | `keep_peace` | nobody checks whether anyone is there, and nothing `keep_peace` reads changes by being in a common room | census: credited the chosen walk 185 times |
| `go_to_where_they_will_be` | `look_after` a person **who is in the room now** | walks away from the person you want to look after | credited 6 times, never chosen |
| `turn_the_room_over`, `watch_them`, `look_at_the_shelf_yourself` | `find_out` | **no act can find anything**: no world state holds where the can went, and no rule forms a belief from searching or watching | code; census: searchers read their own search as `neutral` 374 of 374 |
| `keep_an_eye_on_them`, `be_the_one_who_settles_it` | `restore_standing` | nothing `restore_standing` reads (shame, anger, respect, pride) is changed by watching or searching | code |
| `settle_them_down` (comfort each present) | `keep_peace` | credits comforting people who show no distress | census: credited for 9,383 options |

**The pattern:** a want is connected to acts by a fixed *fit*, and the connection is never checked
against what the act does to anything the want reads. For `get_food` the loop closes through the
body (S1.3). For `look_after` it closes through a sight (S1.4). For `find_out`, `keep_peace` and
`restore_standing` it does not close at all.

---

## 15. Randomness

**Exactly one source of randomness affects behaviour.**

| Where | What | Why | Range and distribution | Seed | Fixed seed |
|---|---|---|---|---|---|
| `Deliberator.PickWithin` (474-489) | which option inside the 0.08 band is chosen | options too close to be a preference | weights `max(1e-6, score - (top - 0.08))`: linear in how far into the band an option sits, so the top is likeliest and the band's floor nearly impossible | per morning `Rng(seed)`, forked per decision by `person@minute` (FNV-1a hash XOR seed, splitmix64) | fully deterministic; `MorningTests.TheSameSeedGivesTheSameMorningEveryTime` |

Verified absent:
- `System.Random`, `Guid`, clock time or tick counts anywhere in Core.
- Randomness in perception, interpretation, appraisal, belief, motivation, costs or world
  consequences.
- Dictionary-order effects: every relevant enumeration is sorted by ordinal key.
- `Rng.NextIndex` exists and is unused.

**Is it resolving genuine ambiguity, or compensating?** Mechanically it respects the principle: no
noise is added to any score, and outside the band nothing is random. Behaviourally it does a great
deal of work:
- **38.2 % of decisions** (1,552 of 4,066) are settled inside the band.
- **35.4 % of batch decisions are ties between genuinely different acts** (S1.5 A).
- S1's review judged only about 7 % to be honest indifference, such as which of two people to watch.
  The rest measures how flat the weighing is.
- Some documented effects exist only through the band: S1.2 found Mara's night changed no clear
  choice (0 of 13) and reached behaviour only by moving options into close calls.

**Insight worth keeping:** because the pick is weighted by score *inside* the band, **the band is
the only place where a small change in motivation changes behaviour gradually** (a probability
shifts). Everywhere else the action layer is argmax, a step function. S1.7 measured argmax changes
only; how history shifts choice *probabilities* has never been measured.

---

## 16. Personality / Values

**Stored:**
- **Traits** (7, 0..1): `Profile.Traits`.
- **Values** (ranked list): `ValueWeight = 1 - 0.25 x rank`, 0 if not held. Ranking replaces
  intensity, so a person's fourth value weighs 0.25 regardless of how much it matters to them.
- **Perceptiveness**, **attention per meaning**, **expressiveness**, **hunger rate**, **age**,
  **family role**.

**Where each is read** (number of rules per stage, from the data):

| Trait / value | Interpretation | Belief nudge | Appraisal | Motivation (wants) | Cost | Hidden reader |
|---|---|---|---|---|---|---|
| cautious | 3 | | 1 | 2 (guard_supplies, keep_peace) | 1 | |
| dominant | 2 | | 4 | 1 (find_out) | 1 | |
| empathetic | 2 | | 7 | 2 (keep_peace, look_after) | 4 | |
| impulsive | | | 2 | | 1 | |
| proud | 4 | 1 | 3 | 1 (restore_standing) | 1 | |
| anxious | 5 | | 8 | | | **emotion decay rate** (Simulation.cs 173) |
| honest | | | 1 | | 2 | |
| family_safety | 4 | | 5 | 2 (guard_supplies, keep_peace) | 1 | |
| respect | 2 | | 4 | 1 (restore_standing) | | |
| control | 2 | | 1 | 1 (find_out) | | |
| fairness | 1 | | 1 | 1 (find_out) | 2 | |
| autonomy | 3 | | 1 | | 1 | |
| closeness | 1 | | 3 | 1 (look_after) | 2 | |
| perceptiveness | 4 | | 1 | | | |
| attention(meaning) | | | multiplies all feelings from that meaning | | | `deception` attention (Elena, Leo) is dead: no rule produces `deception` |
| expressiveness | | | | | | **decides whether distress becomes a world event** |
| age | relation conditions (junior/peer/senior) | | | | | **decides which rules can fire** |
| family role | 1 condition (`self_roles: parent`) | | | | | |

**What personality mathematically does:**
- **Interpretation:** additive weights on readings. Because only the argmax survives, **traits act
  as a gate in effect**: they decide which label wins.
- **Appraisal:** additive terms on feeling intensity. A true multiplier through attention.
- **Belief learning:** pride scales one nudge.
- **Motivation (shipped A):** **additive standing terms. Personality is a permanent motivation.**
  Under B it would be a multiplier on the circumstance, but B is not shipped.
- **Costs:** additive prices. Conditions cannot read traits, so personality never gates an act
  directly, but it can price one out for ever (S1.3: Elena and Leo can never eat).
- **Hidden:** anxious slows the decay of *every* feeling; expressiveness decides whether others ever
  learn of a feeling; age decides relation-conditioned rules.

**Verdict: in the shipped simulation personality acts as both DISPOSITION** (interpretation,
appraisal, costs, decay) **and PERMANENT MOTIVATION** (motivation, as Model A). S1.5 proved the
second is wrong and built the alternative. It was not shipped.

---

## 17. Ledger

| Entry | Created | Dynamic or authored | Read by | Affects interpretation | Appraisal | Deliberation |
|---|---|---|---|---|---|---|
| `comforted_me` | b08 (Mara about Elena) | authored | `look_after` want 0.15 | no | no | via want |
| `protected_me` | b09 (Mara about Daniel) | authored | `look_after` want 0.15 | no | no | via want |
| `overruled_me` | b05 (Daniel about Leo) | authored | `corrected_by_a_junior_with_people_watching` 0.3 | yes | no | no |
| `protected_family` | b01, b05, b09 | authored | **nothing** | | | |
| `proved_right` | b03 | authored | **nothing** | | | |
| `raised_voice` | b06 | authored | **nothing** | | | |
| `raised_voice_at_me` | b06 | authored | **nothing** | | | |
| `searched_my_things` | p02 | authored | **nothing** | | | |

- **Live today:**
  - `Ledger.Add` and `Strength` (saturating).
  - Access-gated authored writes.
  - Three consumers: the `look_after` ledger terms (1,120 non-zero in fifty mornings) and one
    backstory interpretation rule.
- **Scaffolding for S4 (as the brief names it; not documented in the repo except one comment):**
  - `LedgerEffect`'s own summary says "Authored on the event in this slice; derived from appraisal
    in a later one".
  - `LedgerRecord.EventId` and `TraceId` are ready for derived entries.
  - Five entry kinds are waiting for readers.
  - The vocabulary lists them.
- **Not scaffolding but missing:** no rule, stage or code path can create an entry from what an event
  meant. The ledger never grows during a morning (census: 15 entries per run, all backstory).

---

## 18. Speech / LLM Boundary

| Question | Answer |
|---|---|
| What the simulation decides about speech | **nothing**; no decision produces speech; `ActionCatalog` has no speech option |
| What language rendering decides | there is **no language rendering** |
| Do NPC listeners consume SpeechActs? | there is **no SpeechAct type**. Speech is a `WorldEvent` with `Kind = Speech` and an `Act` string (tell, suggest, refuse, demand), plus tone, topic, directness and target. Six exist, all authored backstory. Listeners consume the structured fields through interpretation conditions (7 rules on acts, 4 on tones) |
| Rendered text or structured acts? | structured fields only; `Summary` text is carried into memory and the trace and **read by no rule** |
| Are LLMs involved? | **no**: no code, no package, no network call, no model identifier anywhere in `Assets/_Project` |
| Can an LLM influence state? | no |
| A separate path for player language? | **no player and no language input exist** |

**Does the architecture satisfy "delete the LLM, decisions unchanged"?** **Vacuously yes, and
untested.** There is nothing to delete. The structured-event design is compatible with the principle.
Listeners read fields, never text, and the validator keeps speech and action fields apart. But
**nothing yet demonstrates the boundary**: no speech is ever *decided*, so no path from a decision to
words to a listener exists to test.

---

## 19. Traceability

| Stage | Recorded | Causal source recorded | Relevant input recorded | Why reconstructible | Verdict |
|---|---|---|---|---|---|
| World event | yes (summary) | yes for `steady` (causes) | **no**: act, action, tone, valence, witnesses are not in the record | only by joining to the world's event list | PARTIALLY TRACEABLE |
| Access | yes | event | kind of access | yes | TRACEABLE |
| Interpretation | yes | access; the belief, ledger, memory and feeling ids behind the *winning* label's terms | every matching rule with base, terms and total; runner-up | yes for rules that matched; **no record of rules that did not match or why** | TRACEABLE |
| Experience (memory) | yes | interpretation | meaning, source, confidence, salience | yes | TRACEABLE |
| Belief change | yes, two records | experience | rule, delta, before, after | yes; **seeds are not traced** (they appear only as terms with no justification) | TRACEABLE (seeds PARTIAL) |
| Ledger entry | yes | experience | weight | authored, so "why" is "the script said so" | TRACEABLE |
| Appraisal | yes | interpretation; drew ids | rules, landed intensities, concern, target, reach | yes | TRACEABLE |
| Emotion state | **no record kind is used** (`TraceKind.Emotion` never written) | the appraisal ids live on the instance | **accumulation and decay are not traced** | current intensity at a decision cannot be recomputed from the trace without replaying every fade | PARTIALLY TRACEABLE |
| Memory recall | inside the want's terms | the experience id | level; "answered" note | freshness arithmetic implicit | MOSTLY TRACEABLE |
| Motivation | yes | access record at the decision; drew ids of non-zero and answered terms | every term, urgency, rules | knee and combining are not itemised, so terms do not always sum to urgency | TRACEABLE |
| Percept | partly (access record at the decision) | none | room, present, hunger only; **not** adjacency, knowledge flags, food visibility, just watched | why an option was or was not available cannot be reconstructed | PARTIALLY TRACEABLE |
| Candidate generation | **no** | | | | NOT TRACEABLE |
| Deliberation | yes | every motive; intention | top 6 options (score, appeal, cost), chosen option's credits and prices, resolution, tie list, intention and commitment, `foresaw` under M2 | non-chosen options' itemised credits and prices beyond the top-6 totals are missing; **the random draw is not recorded** (seed and fork key are) | PARTIALLY TRACEABLE |
| Act / consequence | as events; `Consequence` records for eating, failed sitting, Soothe, interruption, carry-on | the decision | | walks, waits, watches and searches completing have no consequence record | PARTIALLY TRACEABLE |
| World state (hunger ticks, portions, placement) | **no** | | | | NOT TRACEABLE |
| Knowledge flags | **no** | | | | NOT TRACEABLE |

**Demonstrated reconstructions:**
- S1.7 E8: a decision walks back through 73 records to twelve earlier events.
- S1.4: 71 of 71 helping loops.
- S1.3: 41 of 41 eating loops.

The trace is a strong instrument for "why did this person read, feel and want this".

It is weak for three questions:
- **"Why was this option possible?"**
- **"How strong was this feeling at that moment, and why?"**
- **"What did the dice do?"**

One known instrument blind spot: `Counterfactual.ReachesCause` ignores zero terms, so it cannot see
answered memories (S1.4).

---

## 20. Test Coverage vs Behavioural Evidence

**Suite:** 363 tests.
- 125 unit tests on parts.
- 40 scenario-level tests (the S0 expectation table, morning invariants, the emergent moment).
- 197 slice experiments, diagnoses and held-out predictions.
- 1 audit census.

38 markers pin known defects or recorded misses to be turned round when fixed.

**Full-suite result for this audit:** **363 tests, 359 pass, 4 fail.** Two are the regressions S1.4 left failing (the pacing gate and the emergent-moment fading check). The other two, `S14AttributionTests.WhereTheChangeInBehaviourComesFrom` and `S1HeldOutTests.H6_TheFourOfThemStayFourPeopleInEveryCondition`, failed on their wall-clock timeouts, not on an assertion: their recorded durations (1.6 h and 13.6 h, against 69 s and 40 s in the S1.6 run) show the host was suspended during the run, H6's own output reports the prediction held, and re-run alone on the same code both pass (88.5 s and 41.3 s). No generated file for S0 to S1.6 changed.

| Mechanism | Unit tests | Scenario / integration | Behavioural experiment | Knowledge |
|---|---|---|---|---|
| Knowledge locality of perception | yes | yes (whole mornings) | S1.1 (feelings), S1.4, S1.7 arm U | **PROVEN** |
| Differentiated interpretation | yes | S0 table (fitted) | S0 swap test, S1.7 | **PROVEN** (mechanism); PLAUSIBLE (that readings are right) |
| Appraisal produces personal feelings | yes | S0 table (83 %, fitted) | S1.1 trait change | **PROVEN** (mechanism); PLAUSIBLE (psychological fit) |
| Emotion decay on the clock | yes | S1.1 locality | S1.7 diagnosis | **PROVEN** |
| Belief formation from readings | yes | | S1.1, S1.7 | **PROVEN** |
| Belief changes later reading | | | S1.7 E1, E2 | **PROVEN** |
| Belief (about people) changes later action | | | S1.7 E6, E7 | **FAILED** (2 of 27, both ties; below noise) |
| Belief (about the world) changes behaviour | | | S1.3, census | **PROVEN** (`supplies_short` prices eating out) |
| Memory recall shapes wants | yes | | S1.1, S1.4 | **PROVEN** (same day) |
| Memory ages correctly | | | S1.6 | **FAILED** for scripted events (shipped) |
| Interpretation strength matters downstream | | | S1.7 D4 | **FAILED** (discarded) |
| A night changes the same person's wants | | | S1.1 (20 of 20 seeds) | **PROVEN** |
| A night changes the same person's behaviour above noise | | | S1.1, S1.4, S1.5, S1.6 | **PROVEN** for Mara; mixed for others |
| Personality differentiates behaviour | | batch | S1 swap test 0.62-0.73 | **PROVEN**, but largely through standing wants (S1.5) |
| Differentiation without standing wants | | | S1.6 | **FAILED** to hold at A's level (0.267) |
| Intention across a walk | yes | | S1.2 | **PROVEN** (mechanism) |
| Walks weighed by their end | yes | | S1.6 | **PROVEN** as a switch; not shipped |
| Social help reaches the helper's want | | | S1.4 | **PROVEN** |
| Eating closes the hunger loop | yes | | S1.3 | **PROVEN** (mechanism); **FAILED** in the scenario as written (0 meals) |
| Investigation achieves anything | | | none | **UNPROVEN**, and impossible by construction |
| Overhearing shapes behaviour | yes (backstory) | | none | **UNPROVEN** (never happens in a morning) |
| Ledger shapes behaviour | | | S1.7 diagnosis (connectivity only) | **UNPROVEN** for the live entries; PROVEN inert for five |
| Speech decisions / LLM boundary | | | none | **UNKNOWN** (not implemented) |
| Randomness only in genuine ties | yes (determinism) | batch | S1 section 10 | **PROVEN** mechanically; **FAILED** in amount (35-38 %) |
| Traceability | yes | | S1.3, S1.4, S1.7 | **PROVEN** for reading-feeling-want chains; PARTIAL for availability, emotion state, dice |
| The simulation is interesting to a human | | | none | **UNKNOWN** |

The unit tests are strong on construction (loaders, validators, arithmetic, locality invariants) and
say nothing about whether a mechanism is psychologically convincing. The S0 expectation table was
written first but the rules were written to it (S0 review), so it is evidence of expressiveness, not
prediction. The held-out predictions from S1 onward are the strongest behavioural evidence the
project has.

---

## 21. S0-S1.7 Discoveries

| Discovery | Slice | What we thought before | What the implementation revealed | Current status |
|---|---|---|---|---|
| Differentiated perception | S0 | shared rules plus per-person data make different readings | true (9 of 12 events read differently; swap test works); the 100 % table match was fitting; "none" for calm people was stoicism mistaken for absence of feeling; salience saturated | mechanism KEPT; salience fixed in S1 |
| Expression is not feeling | S0-S1 | calm people feel less | feel the same, show less (expressiveness) | ACTIVE (visibility) |
| Personality reaches behaviour, circumstance does not | S1 | a night would change a morning | 0.62 between people, 0.04 within a person | partly answered by S1.1 |
| No memory of why one walked | S1 | decisions are independent | pacing 15 | intention added (S1.2) |
| Summed appeal rewards breadth | S1 | adding reasons is neutral | nobody eats; standing still collects three part-reasons | **unchanged**; C3 rejected (S1.2) |
| Half of choices are coin flips | S1 | the band is for true indifference | 49 % settled by seed, 42 points between different acts | **35-38 % still** |
| Feelings leaked across rooms | S1.1 | fading was harmless bookkeeping | every event faded every mind, perceived or not | fixed (clock) |
| The belief stage was skipped | S1.1 | the pipeline carried nights into mornings | only feelings did, and they faded | `answerable_for` added; active |
| Recall is day-scoped | S1.1 | memory is continuous | last night is invisible to recall | **unchanged** |
| Interruptions by feelings already held | S1.2 | interrupt read the new event | read the strongest feeling from anything | fixed |
| Standing still is credited for what it avoids | S1.2 | the credit was harmless | it is load-bearing: removing it collapses the cast | **unchanged** |
| Eating already lowered the want; the record was missing | S1.3 | eating did not update hunger | it did; failure left no record; price keeps two people from ever eating | outcome record (trace-only); eating 0 as written |
| Help reached absent people; concern could not be answered | S1.4 | helping satisfies wanting to help | only fading lowered it | `steady`, `until`, presence check: active |
| Answering the concern exposed standing wants | S1.4 | differentiation was concern | 83 % of `look_after` has no memory behind it | open |
| Standing-want problem (Model A) | S1.5 | traits and values are part of what one wants | 53 % of urgency, 37 % unsupported wants, all standing still | **B built, not shipped; A still shipped** |
| Model A vs Model B | S1.5 | B would be causal and calmer | causal (96 % traced) and paced (2.74) | switch only |
| Pointless movement / means-end | S1.6 | failed attempts must teach something | 92.5 % of lapses were foreseeable; walks are credited without their end | **M2 built, not shipped** |
| Memory temporal validity | S1.6 | the opening memory fades | untimed events are fresh all day | **loader supports minute; data does not use it** |
| Reduced differentiation after removing pathology | S1.5-S1.6 | the cast was distinct because of personality | distinctness was standing wants (A) or the loop (B); 0.267, closest pair 0.012 | open |
| History -> belief -> interpretation | S1.7 | longitudinal effects needed new machinery | a general loop already existed and works | active, shipped |
| Interpretation strength discarded | S1.7 | a stronger reading lands harder | only the label propagates; a step at 11 slights | **unchanged** |
| History changes internal state more than action | S1.7 | a changed want changes the act | 2 of 27 circumstances, both ties settled by the seed; below noise over a morning | open |
| Ledger connectivity | S1.7 | the ledger is relationship history | authored only; 5 of 8 entry kinds unread | **unchanged** |
| **Own morning acts read as a witness would** | **this audit** | actors know what they meant | morning events have no intent; 251 of 251 comforters grateful to themselves | new |
| **Overhearing never happens in a morning** | **this audit** | walls carry information between rooms | 0 of 1,960 morning events had an overhearer | new |
| **Investigation cannot find anything** | **this audit** | searching and watching serve finding out | no world fact and no belief rule exist for it | new |
| **Half the feelings have no outlet** | **this audit** | feelings drive wants | 4 of 8 produced feelings are read by any want or cost | new |
| **Shipped configuration is not the recommended one** | **this audit** | S1.5-S1.7 findings describe the current system | S1.7 ran on A with M1/M2 off; recommendations accumulated unshipped | new |

### The pattern

1. **Information is dropped at stage boundaries and nobody notices until an experiment needs it.**
   Every major discovery has this shape:
   - the fade leak (time crossed a boundary it should not have);
   - the skipped belief stage;
   - the missing intent across a walk;
   - the missing minute on scripted events;
   - interpretation weight;
   - intent on morning events;
   - access after perception.
   The architecture diagram draws arrows; the implementation passes a label, an id or nothing.
2. **Behaviour attributed to a mechanism was carried by a standing credit.**
   - S1.2 (standing-still credit load-bearing).
   - S1.4 (an unanswerable concern carried differentiation).
   - S1.5 (standing wants hid the loop).
   - S1.6 (the loop carried B's differentiation).
   Each removal of a pathology removed some apparent personality.
3. **Records that exist were assumed to be causal.**
   - Salience in S0.
   - The outcome record in S1.3 and S1.4.
   - The ledger in the S1.7 brief.
   - Confidence, concern and interpretation weight today.
4. **Recommendations were measured and not adopted**, so the thing we reason about (B with the fixes)
   and the thing that runs (A) drifted apart.

**Why our model lagged:** each slice built one mechanism and measured its own effect with a purpose-built
instrument. None measured, for the whole system, *who writes each piece of state and who reads it*.
The mental model grew by addition. The implementation grew by addition too, but its wires were
never inventoried.

---

## 22. Hidden Coupling

Each finding is written as source -> hidden dependency -> downstream effect.

1. **A morning act -> built with intent `null` (SilentMorning.cs 618) -> the actor reads it through witness
   rules.**
   - Every comforter reads their own sitting as support received and feels grateful toward themselves
     (251 of 251).
   - They nudge `tendency(self, does_not_respect_me)` (251).
   - Every searcher, watcher, counter and walker reads their own act as `neutral` and keeps a memory
     nothing reads (1,105).
2. **The trait `anxious` -> `Simulation.Fade` decay factor (173) -> every feeling of an anxious person lasts
   longer.**
   - More visible distress, more `keep_peace` and `avoid_exposure` urgency, more interruptions.
   - Nowhere in the README's diagram.
3. **A private feeling x `expressiveness` -> `ShowWhatShows` (552) -> a world event (`show_distress`,
   `steady`).**
   - Other people's concern memories, `look_after`, and whether a concern is ever answered.
   - The world reads a mind to decide what exists.
4. **Soothe -> `EmotionSet.Soften` on another mind (520) -> that person's fear and anxiety fall without
   perception.**
5. **The belief `supplies_short` -> cost `taking_it_when_there_is_little` -> eating priced out.**
   - A belief reaches deliberation without passing through motivation.
   - The largest reason nobody eats.
6. **The feeling `shame` -> cost `not_while_they_are_watching` -> the price of eating with others there.**
7. **The kitchen is tagged both `pantry` and `common` -> three proposals credit one walk
   (`go_where_the_food_is`, `keep_it_in_sight`, `be_where_they_are`) -> a walk to the kitchen collects
   three wants.**
   - 185 chosen walks, each credited by all three.
   - Room tagging in the scenario data is a motivational coupling.
8. **Two standing proposals -> credit `wait` in every decision (`let_it_be`, `leave_it_alone`, 4,066 of
   4,066) -> standing still starts every decision with two credits.**
   - The S1.2 "load-bearing credit".
9. **An event's stirred intensity >= 0.45 -> `Interrupt` (737) -> the busy person thinks again and loses
   their intention (Begin 280).**
   - Any feeling can do it, including gratitude.
   - 1,017 interruptions in 50 mornings.
10. **Knowledge flags held in `SilentMorning` -> `ActionCatalog` availability -> acts depend on state
    outside the Mind and outside the trace.**
    - Checking the pantry is possible once a morning.
    - Searching a room once.
    - Watching somebody is impossible for 15 minutes after the last time.
    - `WatchingGoesStaleAfter` is a fixed cooldown, disclosed in S1 as imitation.
11. **World portions -> `Percept.FoodWithinReach` (See 378) -> `eat` availability depends on world truth
    nobody perceived.**
12. **Age -> `Profile.RelationOfActor` -> `junior`/`senior` conditions -> which interpretation rules can
    fire.**
    - `corrected_by_a_junior_with_people_watching`, `the_search_is_for_what_you_did`.
    - Relation is age, not role: Leo is junior to Daniel, Daniel to Elena.
13. **Interpretation totals summed per label (Interpreter.cs 118) -> many weak rules beat one strong one
    -> breadth wins inside interpretation**, as it does in deliberation.
14. **Belief nudges with no `addressed` or `access` condition -> bystanders and overhearers update beliefs
    as if they were the target and had seen it.**
15. **Scripted events carry minute -1 -> `Freshness` returns 1.0 (ScalerEval.cs 224) -> `find_out` rests on
    fully fresh memories all morning** (at least 2,932 reads in 50 mornings).
16. **Walks relocate instantly at completion (Walk 485) -> nobody is ever in a room *in passing* -> the
    hallway, the only room audible from both bedrooms, is occupied only by somebody who chose to stand
    there -> the overheard channel is silent in the morning** (0 overheard morning events).
    - The count is PROVEN.
    - That this is the reason is PLAUSIBLE: occupancy of audible rooms was not measured.
17. **The leading want -> the only reason an intention keeps -> a walk carried by three wants remembers
    one of them.**
    - On arrival only options serving that one are considered.
18. **The value rank -> `ValueWeight = 1 - 0.25 x rank` -> a person's fourth value weighs 0.25 and their
    fifth 0** whatever the data means by listing it.

---

## 23. Information Bottlenecks

Ranked by causal importance to believable behaviour, not by difficulty.

| Rank | Compression | Lost | Why it matters | Evidence |
|---|---|---|---|---|
| 1 | **All wants -> one summed score per option -> argmax, else a 0.08 coin** | which want an act serves, how urgent the most urgent reason is, and every change smaller than the margin | this is where S1.7's history died (2 of 27 acts changed, both inside the band); breadth beats urgency (nobody eats); 38 % coin | S1, S1.7, census |
| 2 | **Many interpretation rules -> one label** (weight, margin, runner-up discarded) | how clearly something was read; whether it was nearly read otherwise | history about people can matter only by flipping a label (11 slights) | S1.7 D4, E2 |
| 3 | **An event -> a memory of its meaning** (act, tone, valence, context discarded) | what happened, as opposed to what it meant | no reinterpretation; no recall by kind of act; no learning from a pattern of acts | Experience fields |
| 4 | **A morning act -> an event with no intent** | the actor's own meaning | actors misread themselves; self-gratitude; beliefs about oneself | census |
| 5 | **Feelings -> 4 of 8 types reach any want** | gratitude, relief, frustration, hurt as reasons | the commonest feelings carried cannot make anyone do anything | data census |
| 6 | **A feeling per type and target** (causes merged) | shame about X vs shame about Y | a specific experience does not stay specific | S1.1 P1 |
| 7 | **A search or a watch -> nothing** | any information | `find_out` can never be served; investigation is theatre with social side effects | code |
| 8 | **Access -> one flag after perception** (confidence discarded) | hearing vs seeing | beliefs from overhearing as strong as from seeing | reference census |
| 9 | **A walk's reasons -> the leading want** | the other wants that made the walk worth it | arrival reconsiders one reason only | code |
| 10 | **Beliefs -> a confidence with no age** | how long ago, how often | history never wears off, and a stale belief cannot be told from a fresh one | S1.7 E4 |
| 11 | **Relationship history -> authored ledger entries** | anything the simulation experiences about people beyond two `tendency` beliefs | relationships are authored, not lived | S1.7 D2 |
| 12 | **Percept -> room, people present, flags** | where people were last seen, what was seen on the shelf last time | walks cannot anticipate company; the honest residue of S1.6's lapses | S1.6 |

---

## 24. False Completeness

Mechanisms that look more complete than they are.

**Structures with no consumer:**
- `Experience.Confidence`, `DominantEmotion`, `Access`, `FromOwnIntent`, `Order` and `Summary` (runtime).
- `PerceptionOutcome.InterpretationWeight` and `RunnerUpMeaning`.
- `EmotionInstance.Concern` and `LastEventId`. The validator *requires* every appraisal rule to name
  a concern "so the feeling could explain itself"; the concern is then read by nothing.
- `WorldState.WasSearched`: the searched-room set is written and never read.
- `TraceKind.Emotion` and `TraceKind.Action`: declared, never written.
- `Rng.NextIndex`, `VocabularyLoader.Settings`: unused.

**Data with no effect:**
- Five of eight ledger entry kinds.
- Belief predicates `more_knowledgeable`, `makes_risky_calls`, `keeps_things_from_me`, and the
  authored `belief_effects` on b03 that move one of them.
- `competence_self_belief` in every character file (not loaded).
- Attention toward `deception` (no rule produces it).
- Event `directness` (no rule reads it).
- Vocabulary never produced or never read:
  - meanings `request`, `deception`;
  - emotion `warmth`;
  - domains `survival`, `physical`, `social` (used only as authored args);
  - tones `calm`, `neutral`, `firm`;
  - topics `shelter`, `supplies`, `sister`;
  - room tag `passage`.
- Condition keys supported and used by no rule: `event_types`, `directness`, `actor_roles`,
  `actor_is_minor`, `self_is_minor`, `has_actor`, `in_own_room`, `room_holds_food`.
- Scaler kind `constant`, scaler field `by`.

**Mechanisms with no runtime path in the shipped configuration:**
- Model B and B0.
- M2 (walks weighed by their ends).
- Event minutes.

All three are tested and switchable, and none is set by the data.

**Mechanisms that run and cannot achieve their purpose:**
- **Investigation:** `find_out`, three proposals, `search_room`, `observe`, `nearest_unsearched`
  targeting. Nothing can be found.
- **Eating as written:** available 3,620 times, chosen 0.
- **Overhearing in a morning:** fully implemented, 0 occurrences.
- **`PursuitOutcome`:** five outcome kinds, recorded, moving nothing by design.
- **`with_them_standing_right_there`:** a cost never applied.
- **`go_to_where_they_will_be`:** credited 6 times, never chosen.

**Names that suggest more than exists:**
- **"SpeechAct"**: a string field on six authored events.
- **"Player character"**: a JSON comment.
- **"Relationship"**: two beliefs and three read ledger entries.
- **"Plan" / "intention"**: one want key carried across one walk.
- **"Appraisal"**: a meaning-keyed table weighted by personality, with no goal, agency or coping
  dimension.

**Tests that validate construction, not behaviour:**
- Validators, loaders and arithmetic tests are real and useful. They show the data is well-formed,
  not that the psychology is right.
- The S0 expectation table (100 % / 83 %) was fitted.
- The distinctness batch is partly arithmetic of chosen scalers (S1 review section 6).

**Instruments in the production assembly:** `Testing/`, `S0Report`, `S1Report` and `DecisionTrace`
compile into `Fallow.Core`, so the Core's size overstates the simulation's.

---

## 25. Known Problems / Unknowns

Recorded, not fixed.

**1. The shipped baseline is Model A.**
- **Evidence:** `decisions.json` has no `dispositions` or `means`; census 34.6 % standing-only wants;
  S1.5 53 % of urgency.
- **Why it matters:** every behavioural conclusion since S1.5 is about a model we have judged wrong.
- **Current consequence:** S1.7's "dies at action" may be partly A's standing credits.
- **Confidence:** high.
- **Possible experiment:** rerun S1.7 E6-E7 on B with M1 and M2.

**2. Interpretation weight is discarded.**
- **Evidence:** Simulation.cs 199-205; S1.7 D4, E2.
- **Why it matters:** graded history cannot reach feeling.
- **Current consequence:** a step at 11 slights.
- **Confidence:** high.
- **Possible experiment:** S1.8 as a switch, but after item 3 (section 28).

**3. Motivation rarely reaches action.**
- **Evidence:** S1.7 E6 (2 of 27, both ties the seed settled: no clear choice changed), E7 (below noise); 38 % ties; summed appeal.
- **Why it matters:** internal life that never shows is not a life anyone lives through.
- **Current consequence:** a changed person acts the same.
- **Confidence:** high that it happens; **unknown why** (baseline, fit, vocabulary, or band).
- **Possible experiment:** the transfer-function measurement (section 28).

**4. Morning acts carry no intent.**
- **Evidence:** SilentMorning.cs 618; census 251 self-gratitude, 251 self-belief nudges, 1,105 neutral
  own-act memories.
- **Why it matters:** a person does not know what they meant; emotions and beliefs are contaminated at
  scale.
- **Current consequence:** gratitude is the most carried feeling at decisions, partly
  self-generated.
- **Confidence:** high for the mechanism; the share of carried gratitude it explains is unmeasured.
- **Possible experiment:** give morning acts the leading want as intent (diagnosis first).

**5. Investigation can find nothing.**
- **Evidence:** no world state for the can; no rule forms a belief from search or watch.
- **Why it matters:** the scenario's central question is unanswerable by action.
- **Current consequence:** `find_out` persists and its acts matter only socially.
- **Confidence:** high.
- **Possible experiment:** a scenario where something can be found.

**6. Untimed scripted memories never age.**
- **Evidence:** S1.6; data has no minute; census 2,932 reads.
- **Why it matters:** a standing want in disguise.
- **Current consequence:** `find_out` flat all morning for three people.
- **Confidence:** high.
- **Possible experiment:** already built (M1), unshipped.

**7. Beliefs never decay.**
- **Evidence:** no decay code; S1.7 E4.
- **Why it matters:** history never wears off, and cannot be told old from new.
- **Current consequence:** one bad week lasts for ever.
- **Confidence:** high.
- **Possible experiment:** diagnose whether any reading should weaken a belief before adding time.

**8. Half the feelings have no outlet.**
- **Evidence:** data census.
- **Why it matters:** gratitude, relief, frustration and hurt cannot motivate.
- **Current consequence:** being helped, or being fed up, changes nothing one does.
- **Confidence:** high.
- **Possible experiment:** measure what share of emotional change is behaviourally inert.

**9. The ledger is authored.**
- **Evidence:** D2; census.
- **Why it matters:** relationships are not lived.
- **Current consequence:** the S1.7 brief's scenario was unrunnable.
- **Confidence:** high.
- **Possible experiment:** S4 as intended.

**10. Knowledge flags live outside the Mind.**
- **Evidence:** `SilentMorning` fields.
- **Why it matters:** invisible to trace and counterfactuals, never forgotten, and a hard-coded
  cooldown.
- **Current consequence:** availability cannot be explained from the trace.
- **Confidence:** high.
- **Possible experiment:** trace availability before moving anything.

**11. Overhearing never occurs in mornings.**
- **Evidence:** census 0 of 1,960.
- **Why it matters:** the only cross-room channel is untested in use.
- **Current consequence:** information never crosses walls after the backstory.
- **Confidence:** high for the count; the reason is plausible, not isolated.
- **Possible experiment:** count occupancy of audible rooms.

**12. Hearing counts as seeing for beliefs.**
- **Evidence:** nudge rules; confidence unread.
- **Why it matters:** certainty is not local.
- **Current consequence:** latent (no morning overhearing).
- **Confidence:** high.
- **Possible experiment:** only matters once overhearing happens.

**13. Randomness settles 38 % of decisions.**
- **Evidence:** census; S1.
- **Why it matters:** much behaviour is the seed's.
- **Current consequence:** effects surface as probability shifts that nobody measures.
- **Confidence:** high.
- **Possible experiment:** measure choice probabilities, not only argmax.

**14. Soothe writes into another mind.**
- **Evidence:** 514-531.
- **Why it matters:** a locality exception.
- **Current consequence:** S1.4: roughly neutral in effect.
- **Confidence:** high.
- **Possible experiment:** remove once being comforted is appraised.

**Unknowns:**
- Why history's changed wants rarely change acts (item 3).
- Whether B with M1 and M2 changes that.
- What share of carried gratitude is self-inflicted.
- Why nobody is ever in a room audible from events.
- Whether any of the cast's behaviour reads as human to a human.

---

## 26. What We Actually Know

- Events reach only those with access, and nothing reaches anyone else. **PROVEN.**
- The same event is read and felt differently by different people, for reasons the trace can print.
  **PROVEN.**
- Readings form beliefs; beliefs about people change later readings of the same kind of event by the
  same person. **PROVEN.**
- Beliefs never fade; feelings fade within the hour; memories press only on the day they were made.
  **PROVEN.**
- A changed night changes what the culprit wants, and for some people what they do, above seed
  noise. **PROVEN** (Mara); mixed for others.
- Traits and values raise about a third of all wants and half of all urgency with nothing happening.
  This decides most of what people do in the shipped model. **PROVEN.**
- Walks are made to ends the walker could have known were not worth it, and a one-step foresight
  removes them. **PROVEN** (not shipped).
- A changed want seldom changes a clear choice. **PROVEN** on the bench (S1.7).
- Interpretation weight, memory confidence and emotional concern are computed and unused.
  **PROVEN.**
- Only the tie band is random, and the same seed gives the same morning. **PROVEN.**
- There is no speech decision, no LLM, no player and no engine integration. **PROVEN.**

## 27. What We Do Not Know

- **Where exactly motivation stops reaching action**: the baseline, the fits, the seven-act vocabulary,
  summation, or the band.
- **Whether choice probabilities move** with history even when the argmax does not.
- **Whether B with M1 and M2 is a better base for longitudinal effects** than A (S1.7 did not test it).
- **How much of the emotional texture is an artefact** of actors misreading their own acts.
- **Whether any belief should ever weaken**, and by what, other than contrary readings.
- **Whether the rules generalise beyond this house, this cast and this missing can.** Every held-out
  test so far used the same scenario.
- **Whether the result is believable to a person watching it.** Nothing has measured that.
- **What a speech decision would do to all of the above**, since speech is the obvious outlet for
  hurt, gratitude and frustration.

---

## 28. Recommended Next Experiment

**Do not implement S1.8 (propagating interpretation strength) yet. Modify its place in the sequence.**

### Why not S1.8 now

S1.8 would turn the categorical channel into a graded one *at the level of feeling and wanting*. S1.7
already showed that history changes feelings and wants and seldom changes the act. That happened in
2 of 27 circumstances, both of them ties the seed settled, and below noise over a morning. A graded input to a layer that responds as a
step function is unlikely to show a behavioural difference. If it shows none, we will not know
whether S1.8 failed or deliberation hid it. The largest unknown is downstream of S1.8, not upstream.

### What to do first

**Step 0: a decision, not an experiment.** Choose the baseline. S1.5 and S1.6 recommended B with M1
and M2. The shipped rules are still A. Every later measurement is uninterpretable until one of these
is true:
- the choice is made explicitly;
- every experiment runs on both.

This needs no code: the switches exist.

**Step 1: the motivation-to-action transfer function (measurement only, no mechanism).**

On the fifty standard mornings, for every real decision moment, on **both** A and B+M1+M2, measure:

1. **Margin in want-units.** For each want present, the smallest change in its urgency that would
   change the top option. This is computable exactly by re-weighing the decision, as the S1.2 audit
   already does for removing a want.
2. **Probability sensitivity inside the band.** How much the chosen option's probability moves for a
   small change in each want, from the pick weights. This is the channel S1.7 never measured.
3. **Who carries the winner.** The standing, belief, memory, emotion and need shares of the
   winning option's appeal.
4. **The sizes of change history actually produces.** From S1.7: `keep_peace` -0.14,
   `restore_standing` +0.22, `find_out` -0.31. Place them on the margin distribution.

**Hypothesis:** in most moments the margin needed exceeds the size of change history produces, and the
gap is larger on A than on B+M1+M2. **Failure conditions:**
- If typical margins are *smaller* than S1.7's changes, deliberation is not the constraint. Then the
  problem is the few moments where those wants are present at all, and S1.8 becomes the right next
  step.
- If margins are large on both baselines, the action vocabulary or summation is the constraint, and
  S1.8 would be premature.

**Why this is the smallest experiment that reduces the largest uncertainty:**
- It adds no mechanism.
- It reuses the S1.2 audit's re-weighing and the S1.5 source instrument.
- It runs in minutes.
- It directly locates the bottleneck that S1.7 identified and could not explain.
- It decides between the three candidate next steps (S1.8, a deliberation change, a richer action
  vocabulary such as speech) on evidence.

### Worth doing alongside, because they are cheap and contaminate everything

- **Diagnose the null intent on morning acts** (census already counts it). If actors misreading
  themselves inflates gratitude and self-beliefs, every emotional measurement since S1 carries that
  error.
- **Trace action availability** (why an option was or was not possible). That is the largest
  observability gap for any deliberation experiment.

Neither is a new psychological mechanism; both are prerequisites for trusting the transfer-function
measurement.

---

## 29. KEEP / MODIFY / REBUILD / ABANDON Assessment

| Component | Assessment | Reason |
|---|---|---|
| Access and perception gate | **KEEP** | the best-evidenced property of the system |
| World event as structured record | **KEEP** | clean; ready for speech acts; drop or use `directness` |
| Interpretation as competing weighted rules | **MODIFY** | sound mechanism; the discarded weight and per-label summation need a deliberate decision |
| Appraisal | **MODIFY** | personal and traceable, but a meaning-keyed table; no goal/agency/coping dimension; concern unused |
| Emotion store and clock decay | **KEEP**, with the cause-merging and self-reading defects recorded | |
| Memory (Experience) | **MODIFY** | stores meaning, not event; only 4 terms read it; untimed scripted events |
| Recall (same-day, freshness, `until`) | **KEEP** mechanism, **MODIFY** data (minutes) | |
| Beliefs and nudge rules | **KEEP** | the only working longitudinal carrier; decay and access questions open |
| Authored belief effects | **ABANDON** when inference exists | the one use moves a belief nothing reads |
| Ledger | **REBUILD** when relationships are the subject | authored, mostly unread, never produced |
| Motivation, Model A (standing) | **ABANDON** as the shipped model | proven wrong in S1.5, still shipped |
| Motivation, Model B (respond) | **KEEP** as the direction; decide whether to ship | |
| Urgency knee | **KEEP** | |
| Action catalog (seven acts) | **MODIFY** | too few outlets; investigation cannot succeed; availability untraced |
| Proposals with fixed fit | **MODIFY** | means are never checked against what the want reads |
| Summed appeal | **MODIFY** | breadth beats urgency; S1.2 showed it cannot simply be removed |
| Costs | **KEEP** | the main carrier of personality as disposition |
| Intention across a walk | **KEEP** | keeps only the leading reason |
| Walks weighed by their end (M2) | **KEEP**; decide whether to ship | |
| Ambiguity band and seeded pick | **KEEP** mechanism, **MODIFY** frequency | 38 % is weighing flatness |
| Interruption | **KEEP** | drops intentions; any feeling can interrupt |
| Visible distress / steady | **KEEP** | the world reading a mind is acceptable as a body |
| Soothe | **ABANDON** when being comforted is appraised | locality exception; roughly neutral in effect |
| Knowledge flags in `SilentMorning` | **MODIFY** | move into observable state before experimenting on deliberation |
| PursuitOutcome | **KEEP** as trace for needs | behaviourally inert by design |
| Trace | **KEEP** | add availability and emotion-state records when an experiment needs them |
| Counterfactual and batch instruments | **KEEP** | the project's real method |
| Instruments inside `Fallow.Core` | **MODIFY** eventually | they inflate the Core's apparent size |
| The silent-morning scenario | **KEEP** as the bench; **not enough** as the test of believable life | nothing can be found, nobody speaks, and overhearing never happens |
| Speech / LLM boundary | **UNKNOWN**: not implemented | the design is compatible with the principle; nothing tests it |
