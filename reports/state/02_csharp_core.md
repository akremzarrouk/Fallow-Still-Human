# 02: the C# simulation core, as it stands

Prepared 2026-09-26 by read-only inspection at HEAD `8b183d4`. Nothing was built, run or
edited except this file. Paths are relative to the repo root unless they start with a
folder named below.

- **Core** = `Assets/_Project/Scripts/Core/` (assembly `Fallow.Core`, 53 files, 8,554 lines)
- **Tests** = `Assets/_Project/Tests/EditMode/` (assembly `Fallow.Tests.Core`, 65 files)
- **Data** = `Assets/_Project/Data/`
- **Proto** = `Prototypes/llm-morning/`

`CLAUDE.md` holds one rule: "Never stop processes by name or broad filters; only by the
exact process ID you started." No process was started.

---

## 0. Where the core is, and what makes it pure

| Fact | Evidence |
|---|---|
| The core is one assembly, `Fallow.Core`, with no engine references | `Core/Fallow.Core.asmdef`: `"references": []`, `"noEngineReferences": true`, only precompiled ref `Newtonsoft.Json.dll` |
| No core file mentions `UnityEngine` | `grep -rlE 'using UnityEngine' Assets/_Project/Scripts` → no match |
| A test enforces it | `Tests/Scenario001Tests.cs:421` `TheSimulationDoesNotDependOnTheGameEngine` fails if any core file contains `UnityEngine` or `UnityEditor` |
| The only consumer is the EditMode test assembly | `Tests/Fallow.Tests.Core.asmdef` references `Fallow.Core`, `UnityEngine.TestRunner`, `UnityEditor.TestRunner`; Editor platform only |
| The core folders | `Data/` (loaders, validators, vocabulary) · `Model/` (state types) · `Rules/` (rule shapes, scaler arithmetic) · `Sim/` (pipeline, deliberation, the morning loop) · `Testing/` (batch and audit instruments) · `Tracing/` (trace log) |

---

## 1. Main types (one line each)

### Sim/ (the pipeline and the loop)

| Type | Responsibility | Path:line |
|---|---|---|
| `Simulation` | Runs events past a cast of minds; one `Mind` per character; access, interpretation, appraisal, memory, belief, ledger per event; time fading | `Core/Sim/Simulation.cs:86` |
| `PerceptionOutcome` | What one event did to one person (access, meaning, emotions, experience) | `Core/Sim/Simulation.cs:11` |
| `EventOutcome` | One event and its `PerceptionOutcome` per character | `Core/Sim/Simulation.cs:62` |
| `Mind` | One person's inside: `Profile`, `BeliefStore`, `Ledger`, `EmotionSet`, experiences, pursuit outcomes | `Core/Sim/Mind.cs:14` |
| `SilentMorning` | The minute-by-minute morning loop: world tick, completion of acts, visible distress, deciding for everyone idle; turns acts into `WorldEvent`s | `Core/Sim/SilentMorning.cs:119` |
| `ActionRecord` | What somebody did, when, why (leading motive), resolution, outcome text | `Core/Sim/SilentMorning.cs:11` |
| `DecisionMoment` | Read-only snapshot passed to the `Decided` instrument hook | `Core/Sim/SilentMorning.cs:55` |
| `InterruptionRecord` | Somebody stopped mid-act, and by which event | `Core/Sim/SilentMorning.cs:69` |
| `MorningResult` | Actions, decisions, events, world of one morning | `Core/Sim/SilentMorning.cs:84` |
| `Interpreter` | Turns an event into a meaning for one person (own intent, or heaviest-weighted interpretation rule) | `Core/Sim/Interpreter.cs:70` |
| `InterpretationResult` / `RuleContribution` | The winning reading, runner-up, and per-rule arithmetic | `Core/Sim/Interpreter.cs:35`, `:11` |
| `Appraiser` | Turns a meaning into emotions via appraisal rules, saturated to 0..1 | `Core/Sim/Appraiser.cs:45` |
| `EmotionContribution` | One emotion an event produced, with concern and target | `Core/Sim/Appraiser.cs:15` |
| `Motivator` | Raises wants (`Motive`) from motivation rules and the person's state, per percept | `Core/Sim/Motivator.cs:79` |
| `DecisionContext` | `IScalerContext` for deciding: percept, self, target, today, recall half-life | `Core/Sim/Motivator.cs:15` |
| `Needs` | The bodily needs known: only `hunger` | `Core/Sim/Motivator.cs:61` |
| `Deliberator` | Scores every available option (appeal − cost), handles a carried intention, settles near-ties with the seeded RNG | `Core/Sim/Deliberator.cs:227` |
| `Decision` | What was chosen, all ranked options, resolution, margin, intention held / formed | `Core/Sim/Deliberator.cs:141` |
| `ScoredOption` / `Contribution` | One option's appeal, cost, and each want's `urgency × fit` | `Core/Sim/Deliberator.cs:38`, `:11` |
| `Intention` | The want a walk was for, carried into the decision on arrival | `Core/Sim/Deliberator.cs:96` |
| `Commitment` | What became of a carried intention (`held`, `lapsed: …`) | `Core/Sim/Deliberator.cs:122` |
| `Resolution` | `Clear` or `Ambiguous` (seed settled it) | `Core/Sim/Deliberator.cs:78` |
| `ActionCatalog` | Which `ActionOption`s the percept allows; which a proposal endorses | `Core/Sim/ActionCatalog.cs:20` |
| `PursuitOutcome` / `OutcomeKind` / `Outcomes` | Record of what came of acting on a want (satisfied, blocked, …) | `Core/Sim/PursuitOutcome.cs:40`, `:7`, `:105` |
| `Scenario001Content` | Loads vocabulary, cast, backstory, morning, rules from `Data/` | `Core/Sim/Scenario001.cs:12` |
| `Scenario001` / `Scenario001Run` | Prepares a morning (backstory → night → opening) and runs it | `Core/Sim/Scenario001.cs:92`, `:55` |
| `DecisionTrace` | Prints one decision stage by stage from the numbers used | `Core/Sim/DecisionTrace.cs:20` |
| `S0Report`, `S1Report` | Human-readable reports of a run / a morning | `Core/Sim/S0Report.cs:18`, `Core/Sim/S1Report.cs:19` |

### Model/ (state)

| Type | Responsibility | Path:line |
|---|---|---|
| `Profile` | Who someone is: traits, ranked values, perceptiveness, attention, expressiveness, hunger rate, seeded beliefs | `Core/Model/Profile.cs:15` |
| `EmotionSet` / `EmotionInstance` | Live feelings keyed by type+target, accumulating, decaying | `Core/Model/EmotionSet.cs:53`, `:12` |
| `BeliefStore` / `Belief` | Predicate→confidence with justifying trace ids | `Core/Model/BeliefStore.cs:45`, `:8` |
| `BeliefSeed` / `BeliefKey` | Initial belief from character data; canonical key `pred(a,b)` | `Core/Model/BeliefSeed.cs:11`, `:30` |
| `Ledger` / `LedgerRecord` | Specific things one person holds for/against another; strength derived on demand | `Core/Model/Ledger.cs:35`, `:8` |
| `Experience` / `ExperienceSource` | One person's record of one event: meaning, confidence, salience | `Core/Model/Experience.cs:21`, `:4` |
| `Motive` | A want: name, target, urgency, the terms that raised it | `Core/Model/Motive.cs:19` |
| `ActionKind` / `ActionOption` | The 7 physical acts; one concrete option with target/destination/duration | `Core/Model/ActionOption.cs:15`, `:47` |
| `Percept` | The house as one person can know it; the only input to deciding | `Core/Model/Percept.cs:16` |
| `WorldState` | World truth: minute, positions, portions, hunger, searched rooms | `Core/Model/WorldState.cs:16` |
| `WorldEvent` | Something that happened: actor, target, act, topic, tone, valence, intent, witnesses, overhearers | `Core/Model/WorldEvent.cs:12` |
| `Room` / `RoomGraph` | Rooms, tags, owners, adjacency, audibility, BFS distance | `Core/Model/RoomGraph.cs:13`, `:45` |
| `Access` | `None`, `Overheard`, `Witnessed` | `Core/Model/Access.cs:8` |
| `Relation` | `Self`, `Junior`, `Peer`, `Senior` (derived from age) | `Core/Model/Relation.cs:8` |
| `Accumulate` | The one accumulation curve (`Toward`, `Saturate`, `Knee`, `Combine`) | `Core/Model/Accumulate.cs:12` |
| `Rng` | splitmix64, forkable by purpose string | `Core/Model/Rng.cs:15` |
| `ScenarioScript` | Ordered list of events (backstory) | `Core/Model/ScenarioScript.cs:11` |
| `MorningScenario` / `MorningVariant` | House, start, opening, night variants (+ held-out) | `Core/Model/MorningScenario.cs:40`, `:16` |
| `LedgerEffect`, `BeliefEffect` | Authored per-event ledger/belief changes, access-filtered | `Core/Model/LedgerEffect.cs:8`, `Core/Model/BeliefEffect.cs:11` |
| `EventKind` | Said vs done | `Core/Model/EventKind.cs:4` |

### Rules/ (rule shapes and arithmetic)

| Type | Responsibility | Path:line |
|---|---|---|
| `RuleSet` | All rule lists + `Dynamics` + `DecisionDynamics`; `With()` folds decisions in | `Core/Rules/RuleSet.cs:86` |
| `InterpretationRule`, `BeliefNudgeRule`, `AppraisalRule` | Event-pipeline rules | `Core/Rules/RuleSet.cs:6`, `:17`, `:33` |
| `Dynamics` | Emotion decay, floor, overheard scaling, salience base, minutes per fade | `Core/Rules/RuleSet.cs:52` |
| `MotivationRule`, `ProposalRule`, `CostRule` | Decision rules: raise a want; action serves want with `fit`; action costs | `Core/Rules/DecisionRules.cs:12`, `:34`, `:56` |
| `DecisionDynamics` | Ambiguity band, interrupt threshold, hunger rates, action minutes, knee, modes | `Core/Rules/DecisionRules.cs:108` |
| `DispositionMode`, `MeansMode` | Switches: `standing`/`respond`/`gated`; `want`/`end` | `Core/Rules/DecisionRules.cs:70`, `:88` |
| `Condition` / `MatchContext` | Event-rule gate (circumstances only) and its evaluation context | `Core/Rules/Condition.cs:17`, `:99` |
| `SituationCondition` | Decision-rule gate: `Alone`, `InOwnRoom`, `InSomebodyElsesRoom`, `RoomHoldsFood`, `SearchedThisRoomMyself`, `OthersPresentMin` | `Core/Rules/SituationCondition.cs:17` |
| `Targeting`, `MotiveScope` | How a proposal picks targets/rooms; whether a want is per-person | `Core/Rules/SituationCondition.cs:44`, `:74` |
| `Scaler` / `ScalerKind` / `ScalerTerm` | What about the person pushes a weight (trait, value, belief, ledger, emotion, perceptiveness, constant, need, memory) | `Core/Rules/Scaler.cs:31`, `:6`, `:106` |
| `ScalerEval` / `IScalerContext` | The single weight arithmetic used by interpretation, appraisal, motivation and costs | `Core/Rules/ScalerEval.cs:42`, `:17` |

### Data/, Testing/, Tracing/

| Type | Responsibility | Path:line |
|---|---|---|
| `RuleSetLoader`, `ProfileLoader`, `ScenarioLoader`, `MorningLoader`, `VocabularyLoader` | JSON → model (Newtonsoft) | `Core/Data/RuleSetLoader.cs:9`, `ProfileLoader.cs:10`, `ScenarioLoader.cs:10`, `MorningLoader.cs:10`, `VocabularyLoader.cs:8` |
| `*Validator` (Rule, DecisionRule, Profile, Scenario, Morning) | Check data against vocabulary, cast, house | `Core/Data/RuleSetValidator.cs:13`, `DecisionRuleValidator.cs:17`, `ProfileValidator.cs:12`, `ScenarioValidator.cs:13`, `MorningLoader.cs:98` |
| `Vocabulary` | Controlled name lists | `Core/Data/Vocabulary.cs:12` |
| `BatchRunner` | Runs one morning many times; rows and counts | `Core/Testing/BatchRunner.cs:72` |
| `Counterfactual` | Two mornings identical but for one cause, same seed | `Core/Testing/Counterfactual.cs:142` |
| `DeliberationAudit` | Re-weighs copies of decisions with one thing altered | `Core/Testing/DeliberationAudit.cs:22` |
| `MotivationSources` | Counts where want terms come from | `Core/Testing/MotivationSources.cs:84` |
| `TraceLog` / `TraceRecord` / `TraceKind` | Append-only causal trace, every record with parent ids | `Core/Tracing/TraceLog.cs:74`, `:36`, `:9` |

---

## 2. One simulation tick, step by step

A tick is one minute: `SilentMorning.Step()` (`Core/Sim/SilentMorning.cs:240`).
`SilentMorning.Run(minutes)` calls `Step()` once per minute (`Core/Sim/SilentMorning.cs:206-209`);
`Scenario001.Run` uses `content.Morning.Minutes` (`Core/Sim/Scenario001.cs:153-157`), which is
90 in `Data/Scenario/morning.json`.

### 2.0 Before the first tick (preparation)

`Scenario001.PrepareWith` (`Core/Sim/Scenario001.cs:113`):

1. `new Simulation(cast, rules)` creates one `Mind` per character in ordinal id order (`Core/Sim/Simulation.cs:117-127`); each mind seeds its beliefs from the profile (`Core/Sim/Mind.cs:43-47`).
2. Backstory: `sim.Run(content.Backstory)` → `Apply` per event, with feelings fading one fade between events (`Core/Sim/Scenario001.cs:120`, `Core/Sim/Simulation.cs:129-134`, `:149-150`).
3. Night events for the chosen variant, with `FadeOnEachEvent = false`, then one `PassTime(1.0)` (`Core/Sim/Scenario001.cs:127-130`).
4. `WorldState` built from the morning's house, portions, start rooms, start hunger (`Core/Sim/Scenario001.cs:132-134`).
5. `new SilentMorning(sim, rules, world, new Rng(seed), day)` (`Core/Sim/Scenario001.cs:136`); the constructor turns off per-event fading and wires `sim.Needs` to `world.HungerOf` (`Core/Sim/SilentMorning.cs:196-201`).
6. The scripted opening event is applied (`Core/Sim/Scenario001.cs:139`).

### 2.1 `Step()`

| # | What happens | Path:line |
|---|---|---|
| 1 | Hunger rate per inhabitant = `HungerPerMinute × Profile.HungerRate` | `Core/Sim/SilentMorning.cs:242-245` |
| 2 | `WorldState.Tick`: minute++, each hunger += rate, clamped 0..1 | `Core/Sim/SilentMorning.cs:246`; `Core/Model/WorldState.cs:73-81` |
| 3 | `Simulation.PassTime(1 / MinutesPerFade)`: every mind's emotions decay by `factor^fades`, factor = `EmotionDecayBase + EmotionDecayAnxietyResistance × trait anxious`, capped 0.95; below `EmotionFloor` they are dropped | `Core/Sim/SilentMorning.cs:247`; `Core/Sim/Simulation.cs:164-177`; `Core/Model/EmotionSet.cs:120-129` |
| 4 | For each busy person: `MinutesLeft--`; at 0, remove from busy, mark `"finished"`, call `Complete` | `Core/Sim/SilentMorning.cs:249-258` |
| 5 | `ShowWhatShows`: if the dominant emotion is in `DistressShows` and `intensity × Expressiveness ≥ VisibleDistress`, a `show_distress` event reaches the room once; when it stops showing, a `steady` event (not audible) | `Core/Sim/SilentMorning.cs:260`, `:564-603` |
| 6 | Per-minute comfort bookkeeping is cleared | `Core/Sim/SilentMorning.cs:261-262` |
| 7 | For each idle inhabitant (ordinal order): `Begin(id)` | `Core/Sim/SilentMorning.cs:264-268` |

### 2.2 `Complete(id, busy)`: an act finishes and becomes something that happened

`Core/Sim/SilentMorning.cs:400-501`. Optional `IntentOfAct` hook supplies an intent (`:404`).
Per `ActionKind`:

| Act | World change | Event emitted (via `Happened`) | Path:line |
|---|---|---|---|
| `Wait` | none | none | `:410-412` |
| `Observe` | records watch time | `observe` | `:414-420` |
| `GoTo` | `world.Place` | `leave_room` (to those left), `enter_room` (to those walked in on) | `:422-424`, `:503-520` |
| `CheckPantry` | marks pantry seen | `count_supplies`, valence bad if portions ≤ `LowPortions` | `:426-433` |
| `SearchRoom` | marks room searched | `search_belongings` (target = owner present, if any) | `:435-445` |
| `Comfort` | if target still in room: `Soothe` directly softens target's `ComfortSettles` emotions | `comfort` | `:447-473`, `:535-552` |
| `Eat` | `TakePortion`, hunger −= `PortionRelief`; or nothing if empty | `eat_portion` or `find_nothing_left`; then `Resolve` writes a `PursuitOutcome` | `:475-499`, `:661-703` |

`Soothe` is marked in code as technical debt: the only place one person changes another's
feelings without perception and appraisal (`Core/Sim/SilentMorning.cs:527-533`).

### 2.3 `Happened(...)`: an act enters every mind by the event pipeline

`Core/Sim/SilentMorning.cs:615-649`:

1. Witnesses = everyone else in the room (or a given list) (`:620-622`).
2. Overhearers = people in rooms `Audible` from this one, minus witnesses, actor, target; none if not audible (`:625-631`; `Core/Model/WorldState.cs:63-64`).
3. A `WorldEvent` is built with id `m<minute>-<order>` (`:633-643`).
4. `_sim.Apply(e, causes)` (`:646`) → section 2.4.
5. `Interrupt(e, outcome)` (`:647`) → section 2.5.

### 2.4 `Simulation.Apply` and `Perceive`: what one event does to each mind

`Core/Sim/Simulation.cs:142-157`, then per character `Perceive` (`:179-255`):

| # | Stage | Path:line |
|---|---|---|
| 1 | Trace an `Event` record | `Core/Sim/Simulation.cs:144` |
| 2 | Fade only if `FadeOnEachEvent` (off during the morning) | `:149-151` |
| 3 | `Access = e.AccessFor(id)`: actor and witnesses → `Witnessed`, overhearers → `Overheard`, else `None` | `:181`; `Core/Model/WorldEvent.cs:105-112` |
| 4 | `None`: trace "was not there" and stop; nothing else changes | `:183-187` |
| 5 | Interpret: if the perceiver is the actor and the event has an `Intent`, the meaning is that intent; otherwise every matching `InterpretationRule` adds `BaseWeight + Σ scaler terms` to its label, heaviest positive label wins, else `"neutral"` | `:194-196`; `Core/Sim/Interpreter.cs:92-101`, `:109-130` |
| 6 | Build `MatchContext` with the meaning | `:198-201` |
| 7 | Appraise: every matching `AppraisalRule` gives `BaseIntensity + Σ terms`, × reach (0.75 if overheard) × `Profile.Attention(meaning)`; same emotion+target summed, then `Saturate` (1 − e^−x) | `:203-205`; `Core/Sim/Appraiser.cs:79-117` |
| 8 | Salience = `SalienceBase + (1 − SalienceBase) × stirred`, stirred = emotions folded with `Accumulate.Toward`; confidence = 0.60 if overheard else 1 | `:209-219` |
| 9 | Store an `Experience` in the mind | `:221-243` |
| 10 | Add each emotion to `EmotionSet` (same type+target deepens via `Toward`) | `:245-246`; `Core/Model/EmotionSet.cs:65-80` |
| 11 | `ApplyBeliefNudges`: matching `BeliefNudgeRule`s nudge a belief by `Delta + Σ terms`, justification = the experience trace | `:248`, `:257-289` |
| 12 | `ApplyAuthoredEffects`: event's `LedgerEffects` / `BeliefEffects` for this holder, only if they had access | `:249`, `:291-332` |

### 2.5 `Interrupt`

`Core/Sim/SilentMorning.cs:745-782`: a busy person who perceived the event is stopped when the
strongest emotion **this event** stirred is ≥ `InterruptIntensity` (0.45). Their act moves to
`_stopped` and `_why = "interrupted"`, so they decide again this or next minute.

### 2.6 `Begin(id)`: deciding

`Core/Sim/SilentMorning.cs:271-371`:

| # | Stage | Path:line |
|---|---|---|
| 1 | `See(id)` builds the `Percept` (room, present, adjacent, own hunger, food visible only in the pantry room, own searched rooms, recently watched) | `:274`, `:377-398` |
| 2 | Trace the opening | `:276-285` |
| 3 | `Motivator.Raise` → list of `Motive` | `:287` → section 4.1 |
| 4 | Carry an intention only if the person arrived after finishing a walk (`_why == "finished"`) | `:292-294` |
| 5 | `Deliberator.Decide` with an RNG forked by `"<id>@<minute>"` | `:296-298` → section 4.2 |
| 6 | Keep the formed intention only if the chosen act is `GoTo` | `:302-305` |
| 7 | If a carried intention lapsed, record a `PursuitOutcome` | `:309-318` |
| 8 | Store the decision; invoke the `Decided` instrument hook | `:320-331` |
| 9 | Record an `ActionRecord` | `:333-338` |
| 10 | If interrupted and the same act is chosen again, resume it with its remaining minutes | `:343-362` |
| 11 | Otherwise start the chosen act for `Duration` minutes | `:364-370` |

---

## 3. What state a person has

State is split between the `Mind` (inside), `WorldState` (body and position, world truth),
and `SilentMorning` (per-person bookkeeping of the loop).

### 3.1 `Profile` (fixed, from `Data/Minds/*.json`)

| Field | Type / meaning | Path:line |
|---|---|---|
| `Id`, `DisplayName` | strings | `Core/Model/Profile.cs:27-28` |
| `Age` | int; `IsMinor` = age < 18 | `:29`, `:21`, `:105` |
| `FamilyRole` | string (e.g. `"sibling"`) | `:30` |
| `Perceptiveness` | double | `:31` |
| `Expressiveness` | double, default 0.5; only decides whether distress is visible | `:41` |
| `HungerRate` | multiplier of base hunger per minute | `:44` |
| `InitialBeliefs` | list of `BeliefSeed` | `:46` |
| `Traits` | name → 0..1; `Trait(name)` returns 0 if absent | `:48`, `:79-80` |
| `AttentionWeights` | meaning → multiplier (default 1) | `:49`, `:102-103` |
| `Values` | ranked list; `ValueWeight` = 1 − 0.25 × rank, floor 0 | `:50`, `:18`, `:86-96` |
| `RelationOfActor` | Self / Junior / Senior / Peer by age comparison | `:108-115` |

JSON fields not read by `ProfileLoader`: `note`, `competence_self_belief` (present in
`Data/Minds/daniel.json`; the loader reads `traits`, `values`, `perception`, `expression`,
`needs`, `initial_beliefs`, `id`, `display_name`, `age`, `family_role`:
`Core/Data/ProfileLoader.cs:17-65`).

### 3.2 `Mind` (changes during a run)

| Field | Content | Path:line |
|---|---|---|
| `Profile` | above | `Core/Sim/Mind.cs:19` |
| `Beliefs` | `BeliefStore` | `Core/Sim/Mind.cs:20` |
| `Ledger` | `Ledger` | `Core/Sim/Mind.cs:21` |
| `Emotions` | `EmotionSet` | `Core/Sim/Mind.cs:22` |
| `Experiences` | list of `Experience`, oldest first | `Core/Sim/Mind.cs:16`, `:23` |
| `Outcomes` | list of `PursuitOutcome` | `Core/Sim/Mind.cs:17`, `:26` |

**Emotions**: `EmotionInstance` has `Type`, `TargetId` (null = about the situation),
`Concern`, `Intensity` 0..1, `LastEventId`, `Causes` (trace ids)
(`Core/Model/EmotionSet.cs:16-26`). Keyed by type+target (`:57`). `Dominant` = highest
intensity, ties by name (`:135`). `Soften` for comfort (`:104`), `Decay` for time (`:120`).

**Memory**: `Experience` fields `EventId`, `Day`, `Order`, `ActorId`, `TargetId`, `Topic`,
`Minute` (−1 in backstory), `Meaning`, `FromOwnIntent`, `Access`, `Confidence`, `Salience`,
`DominantEmotion`, `TraceId`, `Summary` (`Core/Model/Experience.cs:23-55`); `Source` =
Self / Overheard / Witnessed (`:81`). Recalled by the `memory` scaler: same day, optional
topic/about/by/meaning filters, `Salience × Freshness`, freshness = `h / (h + elapsed)` with
`RecallHalfLife` (`Core/Rules/ScalerEval.cs:129-176`, `:222-232`); an `Until` reading later
about the same subject answers it to 0 (`:153-164`).

**Beliefs**: `Belief` = `Predicate`, `Args`, `Confidence` 0..0.995, `Justifications`
(trace ids) (`Core/Model/BeliefStore.cs:12-21`). `Nudge` moves confidence by
`Accumulate.Toward` and adds the justification (`:78-90`). Seeds have no justification (`:51`).
Nothing reconciles beliefs between minds (`:40-44` doc).

**Relationships**: `Ledger` is a list of `LedgerRecord` (`AboutId`, `Entry`, `Weight`,
`TraceId`, `EventId`) (`Core/Model/Ledger.cs:10-14`). Strength per (person, entry) is derived
on demand by folding weights with `Toward` (`:55-65`); never stored. Ledger entries come only
from authored `LedgerEffects` on events (`Core/Sim/Simulation.cs:293-310`). The structural
relation (junior/peer/senior) is computed from age, not stored (`Core/Model/Profile.cs:108-115`).

**Pursuit outcomes**: `PursuitOutcome` = `MotiveKey`, `MotiveName`, `Act`, `Need`, `Before`,
`After`, `Kind` (Satisfied, PartlySatisfied, Blocked, Unresolved, NoLongerRelevant), `Minute`,
`EventId`, `Because`, `TraceId` (`Core/Sim/PursuitOutcome.cs:7-23`, `:42-63`). Read back by the
`need` scaler as the trace a need rests on (`Core/Rules/ScalerEval.cs:77-90`).

### 3.3 Needs (body, in the world)

| Fact | Path:line |
|---|---|
| The only need is `hunger` | `Core/Sim/Motivator.cs:61-65` |
| Hunger lives in `WorldState._hunger`, not in the `Mind` | `Core/Model/WorldState.cs:19`, `:66-70` |
| A mind sees only its own hunger via `Percept.Hunger` | `Core/Model/Percept.cs:31` |
| During the event pipeline hunger is read through `Simulation.Needs`, wired to the world | `Core/Sim/Simulation.cs:112`; `Core/Sim/SilentMorning.cs:200-201` |

### 3.4 Per-person loop bookkeeping in `SilentMorning`

`_busy` (current act, minutes left, started, decision) · `_stopped` (interrupted act) ·
`_intentions` (why walking) · `_searchedBy` · `_showingIt` (distress visible) ·
`_sawThePantry` · `_watched` · `_why` (`start` / `finished` / `interrupted`)
(`Core/Sim/SilentMorning.cs:121-159`).

---

## 4. How actions are chosen

**Kind**: rule-driven utility scoring over an enumerated option set. No planner and no
search: the code states an intention "is not a plan: nothing is searched for and nothing is
sequenced" (`Core/Sim/Deliberator.cs:91-94`). Randomness only inside an ambiguity band
(`Core/Sim/Deliberator.cs:220-225`).

### 4.1 Wants (`Motivator.Raise`, `Core/Sim/Motivator.cs:88-160`)

1. For each `MotivationRule` whose `SituationCondition` matches the percept (`:95-97`).
2. Subjects: one (nobody) for `situation` scope, or one per person present for `each_present` (`:99`, `:216-225`).
3. Terms from `ScalerEval.Evaluate`; urgency by `Weigh` (`:103`, `:172-203`):
   - `standing`: `BaseUrgency + Σ terms`.
   - `respond`: trait/value/perceptiveness terms are multiplied by the non-disposition total, and give 0 if that total ≤ 0.
   - `gated`: diagnostic.
4. Urgency ≤ 0 dropped; `Accumulate.Knee(urgency, UrgencyKnee)` (`:104-108`).
5. Several rules on the same key combine with `Accumulate.Combine` (`:122`).
6. Sorted by urgency, and each want traced with parents = the records its terms drew on (`:128-157`).

Shipped rule data: 7 motivation rules over 7 motives (`avoid_exposure`, `find_out`,
`get_food`, `guard_supplies`, `keep_peace`, `look_after`, `restore_standing`), 22 proposals,
8 costs (`Data/Rules/decisions.json`).

### 4.2 Options and scores (`Deliberator.Decide`, `Core/Sim/Deliberator.cs:236-339`)

1. `ActionCatalog.Available(percept)` (`:241`; `Core/Sim/ActionCatalog.cs:25-78`). Always `wait`; `observe`/`comfort` per person present (no re-observe while fresh); `go_to` adjacent rooms plus the nearest `pantry`/`common`/`private` rooms and nearest unsearched of each, duration × steps; `check_pantry` if in the pantry room and not yet looked; `eat` only if `FoodWithinReach == true`; `search_room` if not searched here.
2. `Rank` (`:350-416`): for each motive × each `ProposalRule` with the same motive whose gate matches, each option the proposal endorses (`ActionCatalog.Endorsed`, `Core/Sim/ActionCatalog.cs:89-139`) gets `urgency × fit`.
   - With `MeansMode.End`, a `go_to` is credited to a want only if `Foresee` finds an option at the destination serving that want with score > 0 (`:383-392`, `:425-441`). `Foresee` uses `Percept.Imagine` (`Core/Model/Percept.cs:124`).
3. Cost per option = Σ over matching `CostRule`s of `Base + Σ terms`, positive only (`:443-466`).
4. Score = `Appeal − Cost`; sorted by score, then key (`Core/Sim/Deliberator.cs:55`, `:412-415`).
5. A carried `Intention` (`:253-271`): if the want is gone → `lapsed: no longer wanted`; nothing here serves it → `lapsed: nothing here serves it`; its best score ≤ 0 → `lapsed: not worth…`; else `held`, and only options serving it are considered.
6. Band = considered options within `AmbiguityBand` (0.08) of the top (`:274`). One → `Clear`; several → `PickWithin` weighted by position in the band with the seeded RNG → `Ambiguous` (`:280-289`, `:474-489`).
7. Trace the deliberation (`:319-325`). `Forms` = held intention, or a new intention from the `Leading` want (`:330-334`); `Leading` = the want contributing most to the chosen option (`:196-209`).

### 4.3 Switches set by the shipped data

`Data/Rules/decisions.json:575-577` sets `"urgency_knee": 0.85`, `"dispositions": "respond"`,
`"means": "end"`. The code comments at `Core/Rules/DecisionRules.cs:169` ("the shipped rules do
not set it", for `Dispositions`) and `Core/Rules/DecisionRules.cs:175-176` (same, for `Means`)
say otherwise. **MISMATCH** between the comment and the data file.

---

## 5. "Causal semantics" and "route applicability" in the code

### 5.1 In production (`Fallow.Core`)

Neither concept exists in the core. No type, field or identifier.

```
$ grep -rniE 'causal|semantic' Assets/_Project/Scripts
(no output)
$ grep -rniE 'applicab|route' Assets/_Project/Scripts
Assets/_Project/Scripts/Core/Sim/SilentMorning.cs:225:        /// morning decided to do. It reaches people by exactly the route their
```

(The single hit is the English word "route" in a doc comment.)

The nearest production hook is `SilentMorning.IntentOfAct` (`Core/Sim/SilentMorning.cs:178`),
read at `:404`. It is null by default and set only in tests:
`Tests/IntentCarryingExperimentTests.cs:109`, `Tests/IntentionFormationExperimentTests.cs:493`,
`:730`, `Tests/SameActExperimentTests.cs:122`, `:516-517`.

### 5.2 Where they live: experiment test code and experiment data

```
$ grep -rliE 'causal|route.?applicab|reason.?semantic' Assets/_Project --include=*.cs --include=*.json
Assets/_Project/Data/Experiments/causal-routes.json
Assets/_Project/Data/Experiments/reason-semantics.json
Assets/_Project/Data/Experiments/route-applicability.json
Assets/_Project/Tests/EditMode/CausalRouteExperimentTests.cs
Assets/_Project/Tests/EditMode/IntentionRankingExperimentTests.cs
Assets/_Project/Tests/EditMode/ReasonSemanticsExperimentTests.cs
Assets/_Project/Tests/EditMode/RouteApplicabilityExperimentTests.cs
Assets/_Project/Tests/EditMode/S11CausalExamplesTests.cs
Assets/_Project/Tests/EditMode/S13ExperimentTests.cs
Assets/_Project/Tests/EditMode/S14ExperimentTests.cs
Assets/_Project/Tests/EditMode/S16HeldOutTests.cs
Assets/_Project/Tests/EditMode/S17ExperimentTests.cs
```

| Concept | Where it is defined | What it is in code |
|---|---|---|
| Shared intention selector | `Tests/IntentionSelector.cs:30` | Static class. Doc says "Experiment code. Nothing in `Fallow.Core` knows this exists" (`:18-19`). `Candidate` rule (`:35`); `Form` (`:146`). Uses the shipped `SituationCondition` and `ScalerEval` |
| **Causal route** | `Tests/CausalRouteExperimentTests.cs:34` | "A route is one declared explanation of why some evidence supports an intention; its key is an experiment-only name for that declared meaning" (`:21-23`). `RouteRule` = a `Candidate` + per-statement `Routes[]` and `Roles[]` (`:193-198`); `Declared` = rules, alternative groups, rename (`:201-209`). Representations `A, B, C, D, DAlt, DEnablers, G` (`:405`). Data: `Data/Experiments/causal-routes.json` |
| **"Causal semantics"** | a heading, not code | Heading "Causal semantics: what the declarations mean, and what they move" at `Docs/experiments/causal-routes/report.md:436`; key `"causal_semantics"` at `Docs/experiments/causal-routes/classification.json:109`. Its entries include `gate-cannot-name-a-person` ("SituationCondition has no field for a particular person being present or absent") and `prevent-relation-is-vacuous` |
| Reason semantics | `Tests/ReasonSemanticsExperimentTests.cs:30` | Representations `S, A, BParts, BCirc, B, C, …` (`:58`); `Route` (`:123`), `Relation` (`:133`), `Case` (`:139`). Data: `Data/Experiments/reason-semantics.json` |
| **Route applicability** | `Tests/RouteApplicabilityExperimentTests.cs:30` | "What must a route contain to decide whether it applies at all, before its support and inhibitors are combined?" (`:18-19`). `Route` = `Key`, `Intent`, `AppliesWhen` (list of predicate strings) (`:126-131`). `Rule` terms carry a `Role` (`:105-111`, e.g. `"condition"`, `"support"`). `DeclaredApplies` = every `AppliesWhen` predicate holds for the present people/target **and** every `condition`-role term's level > 0 (`:596-603`). Representations `S, A, B, C, CEntity, CConditions, CSplit, CKind, BW` (`:66`). Data: `Data/Experiments/route-applicability.json` (16 cases). Writes `Docs/experiments/route-applicability/measurements.md` |

Result recorded for route applicability: 24 predictions, 21 pass, 2 partly, 1 fail. "The
applicability layer adds nothing on real mornings": C and B change the same 99 real decisions
(`Docs/experiments/route-applicability/results.md:92-102`, `:114-120`). The experiment file
hashes frozen inputs and asserts nothing in production changed (`Tests/RouteApplicabilityExperimentTests.cs:32-42`;
`results.md` criterion "Nothing in production changed").

---

## 6. LLM integration in C#

**NOT FOUND.**

```
$ grep -rniE 'llm|gemini|openai|anthropic|claude|gpt|HttpClient|WebRequest|prompt|language.model' Assets/_Project/Scripts
(no output)
$ grep -rliE 'llm|gemini|openai|anthropic|claude|gpt|HttpClient|WebRequest|UnityWebRequest|prompt|language model' Assets --include=*.cs
Assets/_Project/Tests/EditMode/CausalRouteExperimentTests.cs
Assets/_Project/Tests/EditMode/ReasonSemanticsExperimentTests.cs
Assets/_Project/Tests/EditMode/RouteApplicabilityExperimentTests.cs
Assets/_Project/Tests/EditMode/S12CommitmentTests.cs
Assets/_Project/Tests/EditMode/Scenario001Tests.cs
Assets/_Project/Tests/EditMode/SensitivityExperimentTests.cs
```

None of the test hits is an LLM call:

- The three experiment files print a report sentence saying the annotation reviewers "are language models, not people" (`Tests/CausalRouteExperimentTests.cs:1487`, `Tests/ReasonSemanticsExperimentTests.cs:1805`, `Tests/RouteApplicabilityExperimentTests.cs:1500`). The reviewers' answers are read from committed JSON files (`Docs/experiments/*/annotation/responses/reviewer-N.json`, with `"model"` values `haiku`, `sonnet`, `opus`, 6 of each). They are not called from C#.
- `S12CommitmentTests.cs:86` (`…StiLLMakes…`), `Scenario001Tests.cs:22` (English "a prompt to read"), and `SensitivityExperimentTests.cs:655-660` (`allMoves`) are substring false positives.

The Unity package `com.unity.modules.unitywebrequest` is in `Packages/manifest.json` (a
default module), but no C# file uses it.

---

## 7. Shared data or code between the C# core and `Prototypes/llm-morning`

**Code: NOT FOUND.** The prototype is Python (14 `.py` files, 3,752 lines). No C# references it:

```
$ grep -rn 'Prototypes' Assets --include=*.cs
(no match)
```

**Data: shared by hand-copy, not by file.** No prototype file opens anything under `Assets/`
(its `open(` calls are its own `config.json`, `cache`, and `runs/`: `gemini.py:43`, `:192`,
`morning.py:85-124`, `metrics*.py`). `data.py` says so:

> `Proto/data.py:3` "Copied by hand from the shipped data so the prototype never reads Assets/"

| Copied item (per `Proto/data.py:4-9`) | C# source | Differences seen |
|---|---|---|
| people: age, role, note, traits, values, hunger rate | `Data/Minds/*.json` | Traits and hunger rates are the same for all four (e.g. daniel: `Proto/data.py:22-25` vs `Data/Minds/daniel.json`). Values are reworded (`"control"` → `"being in control"`, `"respect"` → `"being respected"`, `"family_safety"` → `"keeping the family safe"`). Role is reworded (`"sibling"` → `"the eldest son"`). Not copied: `perception` (perceptiveness, attention), `expression`, `initial_beliefs`, `competence_self_belief` (`grep -nE 'perceptiveness|attention|expressiveness|belief|competence' Proto/data.py` → no match) |
| house | `Data/Scenario/morning.json` `house` | rooms `kitchen`, `brothers_room`, `back_room`, `bathroom` (`Proto/data.py:57-68`) |
| start, opening | `morning.json` `start`, `opening` | start hunger is the same (daniel 0.55, elena 0.60, leo 0.45, mara 0.50) |
| scenarios | `morning.json` `variants` | Prototype has `daniel_ate_it`, `mara_ate_it`, `miscount` (`Proto/data.py:7`). C# has `daniel_ate_it`, `daniel_hid_it`, `mara_ate_it`, `elena_fed_mara`, `miscount` and held-out `leo_ate_it` |
| backstory | `Data/Scenario/backstory.json` | who did / saw / heard each event (`Proto/data.py:9`, `:157`) |

**Not shared, structurally different** (facts from the Python module docstring and prompt):

| Aspect | C# core | Prototype |
|---|---|---|
| Who chooses the act | `Deliberator` utility over rules (section 4) | The model, via `SYSTEM` prompt "Choose exactly one option id from the list" (`Proto/world.py:26-38`); the rules layer settles all other turns (`Proto/world.py:1-3`) |
| Time step | 1 minute (`Core/Sim/SilentMorning.cs:240`) | "the next three minutes" (`Proto/world.py:27`) |
| Speech | none; "Nobody speaks yet" (`Core/Model/ActionOption.cs:7` doc) | options marked `(speech)` carry the exact words (`Proto/world.py:29-31`) |
| Inner state | emotions, beliefs, ledger, experiences (section 3) | hunger, a suspicion 0-3, grudges 0-3, guilt (`Proto/world.py:11-15`) |
| Model | none | `gemini-3.5-flash-lite`, alt `gemma-4-31b-it` (`Proto/config.json`) |

---

## 8. What Unity shows or does with the core

**Nothing at runtime.** The core is only exercised by EditMode tests.

```
$ find Assets -name '*.unity'
Assets/Scenes/SampleScene.unity
$ find Assets -name '*.cs' -not -path 'Assets/_Project/*'
Assets/TutorialInfo/Scripts/Editor/ReadmeEditor.cs
Assets/TutorialInfo/Scripts/Readme.cs
$ grep -rlE 'MonoBehaviour|UnityEngine' Assets --include=*.cs
Assets/TutorialInfo/Scripts/Editor/ReadmeEditor.cs
Assets/TutorialInfo/Scripts/Readme.cs
Assets/_Project/Tests/EditMode/Scenario001Tests.cs
Assets/_Project/Tests/EditMode/TestPaths.cs
$ find Assets -name '*.prefab' | wc -l
0
```

| Fact | Evidence |
|---|---|
| One scene, in build settings | `ProjectSettings/EditorBuildSettings.asset:7-10` → `Assets/Scenes/SampleScene.unity` |
| The scene holds the URP template objects only: `Main Camera`, `Directional Light`, `Global Volume` | `SampleScene.unity:135`, `:271`, `:388` |
| Its three scripts are URP package scripts, not project scripts | GUIDs `a79441f3…` → `UniversalAdditionalCameraData.cs`, `474bcb49…` → `UniversalAdditionalLightData.cs`, `172515602…` → `Volume.cs` (resolved in `Library/PackageCache/com.unity.render-pipelines.*`; no match under `Assets/`) |
| The only MonoBehaviour-side scripts are the Unity template's `TutorialInfo` Readme | `Assets/TutorialInfo/Scripts/Readme.cs`, `…/Editor/ReadmeEditor.cs` |
| Test code's only engine use is locating folders | `Tests/TestPaths.cs:13`, `:21`, `:24` (`UnityEngine.Application.dataPath`) |
| Unity's role: host and runner of the EditMode test suite, which loads `Data/` and writes Markdown under `Docs/` | e.g. `Tests/RouteApplicabilityExperimentTests.cs:28` ("Writes `Docs/experiments/route-applicability/measurements.md`") |

---

## 9. Search commands used (all read-only)

Outputs that are long are summarized in the section cited. Shorter ones are quoted above.

| Command | Result / section |
|---|---|
| `cat CLAUDE.md; ls` | one rule; repo top level (§0) |
| `find Assets -name "*.asmdef"` | `Core/Fallow.Core.asmdef`, `Tests/Fallow.Tests.Core.asmdef` (§0) |
| `find Assets -name "*.cs" \| sed 's\|/[^/]*$\|\|' \| sort \| uniq -c` | 10 Data, 21 Model, 6 Rules, 13 Sim, 4 Testing, 1 Tracing, 65 EditMode tests, 2 TutorialInfo |
| `find Scripts -name "*.cs" \| xargs wc -l \| sort -n` | 8,554 lines total; largest `SilentMorning.cs` 804, `Deliberator.cs` 491 |
| `grep -rnE '^\s*(public\|internal)[a-z ]*(class\|enum\|interface\|struct) ' Assets/_Project/Scripts/Core` | the full type list used for §1 |
| `cat -n` / Read of `Simulation.cs`, `Mind.cs`, `SilentMorning.cs`, `Deliberator.cs`, `Motivator.cs`, `Interpreter.cs`, `Appraiser.cs`, `ActionCatalog.cs`, `Profile.cs`, `EmotionSet.cs`, `BeliefStore.cs`, `Ledger.cs`, `Experience.cs`, `WorldState.cs`, `Percept.cs`, `Motive.cs`, `ActionOption.cs`, `Accumulate.cs`, `RuleSet.cs`, `DecisionRules.cs`, `SituationCondition.cs`, `Scaler.cs`, `ScalerEval.cs`, `Condition.cs`, `WorldEvent.cs`, `RoomGraph.cs`, `Rng.cs`, `Scenario001.cs`, `MorningLoader.cs`, `MorningScenario.cs`, `TraceLog.cs`, `PursuitOutcome.cs` | §§2-4 |
| `grep -rniE 'causal\|semantic' Assets/_Project/Scripts` | no output (§5.1) |
| `grep -rniE 'applicab\|route' Assets/_Project/Scripts` | 1 comment hit (§5.1) |
| `git show --stat b344056 8ec782c` | route-applicability and reason-semantics commits touch only `Tests/`, `Data/Experiments/`, `Docs/`, `README.md` |
| `grep -rliE 'causal\|route.?applicab\|reason.?semantic' Assets/_Project --include=*.cs --include=*.json` | 3 data + 9 test files (§5.2) |
| `grep -rniE 'causal.?semantic' … (excl. Library)` | `CONTEXT_REPORT.md:655,659,928`, `Docs/experiments/causal-routes/report.md:436`, `…/causal-routes-all.md:452`, `…/classification.json:109` |
| `grep -nE '(class\|enum\|struct\|interface) '` over the three experiment test files | route/rep types (§5.2) |
| `grep -nE 'AppliesWhen\|bool Applies' Tests/RouteApplicabilityExperimentTests.cs` | `:130`, `:341`, `:348`, `:538`, `:552`, `:596-598`, … |
| `grep -rnE 'IntentOfAct\s*=' Assets --include=*.cs` | set only in tests (§5.1) |
| LLM greps (§6) | no production hit |
| `grep -h '"model"' Docs/experiments/*/annotation/responses/*.json \| sort \| uniq -c` | 6 haiku, 6 opus, 6 sonnet |
| `grep -rn 'Prototypes' Assets --include=*.cs` | no match (§7) |
| `grep -nE 'Assets\|_Project\|Minds\|…' Proto/*.py`; `grep -nE 'open\(\|json\.load' Proto/*.py` | only doc/comments name `Assets/`; no file under it is opened (§7) |
| `python -c` over `morning.json`, `rules.json`, `decisions.json`, `daniel.json` (read and print) | start state, variants, rule counts (21 interpretation, 6 belief nudges, 18 appraisal; 7 motivation, 22 proposals, 8 costs), deciding switches, profile keys |
| `grep -nE '"(dispositions\|means\|urgency_knee)"' Data/Rules/decisions.json` | `:575-577` (§4.3) |
| `find Assets -name '*.unity'`, `…'*.prefab'`, MonoBehaviour grep, `EditorBuildSettings.asset`, scene `m_Script` / `m_Name` grep, GUID lookup in `Library/PackageCache` | §8 |

---

## 10. NOT FOUND list

| Looked for | Where | Result |
|---|---|---|
| Any `UnityEngine` / `UnityEditor` use in the core | `Assets/_Project/Scripts` | NOT FOUND (enforced by test) |
| A type, field or identifier for "causal semantics" | core and tests (`.cs`) | NOT FOUND as code; only a report heading and a JSON key in `Docs/experiments/causal-routes/` |
| A type for "route" or "route applicability" in production | `Assets/_Project/Scripts` | NOT FOUND; exists only as private nested types in experiment test files |
| An LLM call, HTTP client, or prompt in C# | `Assets/**/*.cs` | NOT FOUND |
| Code shared between C# and the Python prototype | both | NOT FOUND |
| A prototype file that reads `Assets/` data at runtime | `Proto/*.py` | NOT FOUND (hand-copied instead) |
| A planner, search, or multi-step plan in action selection | `Core/Sim` | NOT FOUND (single-step utility; intention only across a walk) |
| Needs other than hunger | `Core/Sim/Motivator.cs:61-65` | NOT FOUND |
| Speech or dialogue acts in the core | `ActionKind` (`Core/Model/ActionOption.cs:15`) | NOT FOUND (7 physical acts) |
| A stored relationship score | `Core/Model/Ledger.cs` | NOT FOUND (strength derived from records on demand) |
| Loader use of `note` and `competence_self_belief` from mind files | `Core/Data/ProfileLoader.cs` | NOT FOUND |
| A project MonoBehaviour, prefab, or scene object that uses the core | `Assets/` | NOT FOUND |
| A project scene other than the URP template `SampleScene` | `Assets/` | NOT FOUND |
| Earlier `reports/state/01_*` file | repo | NOT FOUND (this is the first file in `reports/state/`) |
