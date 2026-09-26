# Fallow: context report for a reviewer

Prepared 2026-09-24 by read-only inspection of the repository at
`C:\Users\Akrem\Desktop\Projects\Fallow`, HEAD `431db11`. No build, test, batch
run or experiment harness was started. This file is the only file written.

Conventions: paths are relative to the repo root. "Code" means
`Assets/_Project/Scripts/Core` (production) or `Assets/_Project/Tests/EditMode`
(tests and experiment fixtures). Where code and documentation disagree it is
marked **MISMATCH**.

---

## 1. Repository map

### 1.1 Top level

```
.gitattributes  .gitignore  README.md  merge-slice-docs.py  run-tests.sh
test-results.xml            (git-ignored; last full-suite result, see section 10)
Assets/                     Unity assets; project code lives in Assets/_Project
Docs/                       all written reports, predictions, traces, generated docs
Library/ Logs/ UserSettings/ (git-ignored Unity folders)
Packages/ ProjectSettings/  Unity project config
```

`git ls-files | wc -l` = 528 tracked files.

### 1.2 Assets (2-3 levels, .meta files omitted)

```
Assets/
  InputSystem_Actions.inputactions, Readme.asset      (Unity template content)
  Scenes/SampleScene.unity                            (Unity template scene)
  Settings/*.asset                                    (URP render settings)
  TutorialInfo/                                       (Unity template tutorial)
  _Project/
    Data/
      Experiments/   causal-routes.json, held-out-people.json, intentions.json,
                     reason-semantics.json, route-applicability.json
      Minds/         daniel.json, elena.json, leo.json, mara.json   (character profiles)
      Rules/         decisions.json, rules.json, vocabulary.json
      Scenario/      backstory.json (S0), morning.json (S1 onward)
      Tests/         expectations.json (S0 designer expectation table)
    Scripts/Core/    Fallow.Core.asmdef + 56 .cs files, 8,554 lines
      Data/     (10)  loaders and validators
      Model/    (21)  Percept, Profile, BeliefStore, EmotionSet, Experience, Motive,
                      ActionOption, WorldEvent, WorldState, RoomGraph, Rng, Ledger ...
      Rules/    (6)   RuleSet, DecisionRules, Condition, SituationCondition, Scaler, ScalerEval
      Sim/      (13)  Simulation, Interpreter, Appraiser, Motivator, Deliberator,
                      ActionCatalog, SilentMorning, Mind, PursuitOutcome, reports
      Testing/  (4)   BatchRunner, Counterfactual, DeliberationAudit, MotivationSources
      Tracing/  (1)   TraceLog
    Tests/EditMode/  Fallow.Tests.Core.asmdef + 64 .cs files, 26,912 lines
```

### 1.3 Assemblies

| Assembly | asmdef | References | Notes |
|---|---|---|---|
| `Fallow.Core` | `Assets/_Project/Scripts/Core/Fallow.Core.asmdef` | none; precompiled `Newtonsoft.Json.dll` | `"noEngineReferences": true` |
| `Fallow.Tests.Core` | `Assets/_Project/Tests/EditMode/Fallow.Tests.Core.asmdef` | `Fallow.Core`, `UnityEngine.TestRunner`, `UnityEditor.TestRunner`; `nunit.framework.dll`, `Newtonsoft.Json.dll` | Editor only, `UNITY_INCLUDE_TESTS` |

No other project asmdefs were found. `.csproj`/`.sln` files are git-ignored.

### 1.4 Where things live

| Kind | Location |
|---|---|
| Core simulation code | `Assets/_Project/Scripts/Core/{Model,Rules,Sim,Tracing,Data}` |
| Harness helpers compiled into Core | `Assets/_Project/Scripts/Core/Testing/` (BatchRunner, Counterfactual, DeliberationAudit, MotivationSources) |
| Tests and experiment fixtures | `Assets/_Project/Tests/EditMode/*.cs` |
| Experimental intention selector (not in Core) | `Assets/_Project/Tests/EditMode/IntentionSelector.cs` |
| Shipped data (JSON) | `Assets/_Project/Data/{Minds,Rules,Scenario,Tests}` |
| Experiment-only data (JSON) | `Assets/_Project/Data/Experiments/` |
| Slice docs | `Docs/slices/S0 ... S1.7` |
| Experiment docs | `Docs/experiments/<name>/` |
| Audits | `Docs/audit/census.md`, `Docs/audit/system-understanding-audit.md` |
| Traces | `Docs/slices/S0/traces/`, `Docs/slices/S1/traces/`, `Docs/slices/S1/batch/` |

### 1.5 UnityEngine references in Core

`grep -rn "UnityEngine" Assets/_Project/Scripts/` returned **no matches**. The
Core asmdef also sets `"noEngineReferences": true`. The only UnityEngine
references in project code are the test runner assemblies listed in the test
asmdef.

---

## 2. Git history

Current branch: `main`. `git status`: "Your branch is ahead of 'origin/main' by
32 commits. nothing to commit, working tree clean". Only branches: `main`,
`remotes/origin/main`. No stashes. Total commits: 60 (so the log below is the
whole history). First commit 2026-09-10, last 2026-09-24 02:12 +0100.

`git log --oneline -n 60`:

```
431db11 docs: predictions, protocol and cases for the route-applicability experiment
8ec782c feat: what a simulated reason has to contain, before any formula
e5a5131 docs: predictions, cases and annotation for the reason-semantics experiment
5d0f6b8 docs: full-suite result for the causal-route experiment
9648a9b feat: declared causal routes tell two reasons from one reason twice, and fall short twice
2fed9f8 docs: full-suite result for the intention representation experiment
3780435 docs: predictions, route declarations and annotation for the causal-route experiment
2ae1070 feat: evidence identity stops restatement, and leaves one decision open
568e1c0 docs: full-suite result for the intention ranking experiment
a21fc76 docs: predictions for the intention representation experiment
9ccb8d4 feat: what an intention selector must satisfy, and where ranking breaks it
964d056 docs: predictions for the intention ranking experiment
dce227d docs: full-suite result for the two intention experiments
18d1163 feat: the ten rules are a reusable function of a person, ranked by an arbitrary sum
132e86e docs: predictions and held-out people for the generalization experiment
b285b8c feat: a want constrains an intention without deciding it
8ede500 docs: predictions and blind-authored candidate rules for intention formation
db2be76 docs: full-suite result for the same-act experiment
1ddded6 feat: one act, six reasons, and who is left to read the difference
c9af832 docs: predictions for the same-act-different-reason experiment
95d0b50 docs: full-suite result for the five experiments, and one correction
7413758 feat: accumulated history changes what a later event means
b075664 feat: one lived episode, and how long it carries
a79a048 feat: carry what a person meant onto the event their act becomes
b6882f9 docs: action representation audit, the reason does not survive the act
500066c feat: decision sensitivity, how far a want must move before the act does
c243050 feat: ship Model B with both S1.6 fixes as the primary baseline
dd9065c docs: full-suite result for S1.7 and the audit; no clear choice changed
36a1ec5 docs: system understanding audit of the implemented simulation
a08dd62 feat: slice S1.7, whether a past event changes a later decision
b777a05 docs: S1.6 full-suite tally and regression check confirmed
1d59e43 docs: S1.7 hypothesis, design and held-out predictions, before any code for it
556b023 feat: slice S1.6, weighing a walk by its end and timing the lived day
c57687a docs: S1.6 hypothesis, the two mechanisms and held-out predictions, before any code for them
eeb29fe test: S1.6 diagnosis of walking to ends already found not worth it, behaviour unchanged
360f087 feat: slice S1.5, traits and values as dispositions (diagnostic)
c8f788e docs: S1.5 hypothesis, the alternative and held-out predictions, before any code for it
e6e469c test: S1.5 diagnosis of where wants come from, behaviour unchanged
b45f007 feat: slice S1.4, what looking after somebody does to wanting to
56c6c7e docs: S1.4 hypothesis and held-out predictions, before any S1.4 code
50bf671 test: S1.4 diagnosis of wanting to look after somebody, behaviour unchanged
cfcee77 feat: slice S1.3, what acting on a want does to it (hunger and food)
3331002 test: S1.3 diagnosis of wanting food, behaviour unchanged
15c3175 feat: slice S1.2, deliberation
a354e98 test: S1.2 deliberation audit and diagnosis, behaviour unchanged
0cc78c3 feat: slice S1.1, circumstance to motivation to behaviour
b310c67 docs: S1.1 held-out predictions for leo_ate_it, before it has been run
06d92eb fix: S1.1 circumstance pathway, three measured changes
160dc2d test: S1.1 counterfactual harness, diagnosis, and a held-out condition
f0b0253 feat: slice S1, the silent house
5d613b9 feat: the deciding layer, and the S1 held-out predictions
3a81ede docs: check S0 against the plan worked example for p01
8994215 docs: slice S0 review and project readme
6933dcd feat: scenario 001 measured against the expectation table
63dd953 feat: appraisal and the full per-event pipeline
6e53051 feat: rules model, loader, validator, and the interpreter
a61c8f0 feat: belief store, ledger, emotions, and the causal trace
9344a41 feat: character profiles, vocabulary, and data validation
8c88cc9 data: S0 cast, event script, and designer expectation table
91d4341 chore: bootstrap Unity project for Fallow slice S0
```

Untracked or modified files at the start of inspection: none reported by
`git status`. At the end, `git status --short` showed two untracked paths:
`CONTEXT_REPORT.md` (this file) and
`Docs/experiments/route-applicability/annotation/responses/` (created by
another process during the inspection; see 7.3). Note: `Assets/_Project/Data/Experiments/route-applicability.json`
is committed but has **no `.meta` file** beside it, unlike every other data file.

---

## 3. Core causal pipeline in code

The README draws the pipeline as:

```
world event -> access -> interpretation -> experience -> belief
                                        -> appraisal   -> emotion
   world consequence <- action <- deliberation <- motivation
```

| Stage | File(s) | Main types / functions |
|---|---|---|
| Perception (events) | `Sim/Simulation.cs`, `Model/WorldEvent.cs`, `Model/Access.cs` | `Simulation.Apply(WorldEvent)` calls private `Perceive(mind, e, trace)` for each mind; `WorldEvent.AccessFor(id)` returns `Access { None, Overheard, Witnessed }`. |
| Perception (situation) | `Model/Percept.cs`, `Sim/SilentMorning.cs` | `SilentMorning.See(characterId)` builds a `Percept` (room, `Present`, `Adjacent`, `Hunger`, `RoomHoldsFood`, `FoodWithinReach`, `JustWatched` ...). Doc comment: "Deliberation is handed a Percept and never the world". |
| Interpretation | `Sim/Interpreter.cs`, `Rules/RuleSet.cs` | `Interpreter.Interpret(...)` returns `InterpretationResult` (meaning, weight, runner-up). Actor with `e.Intent` "knew their own intention"; else heaviest `InterpretationRule` reading wins. |
| Memory | `Model/Experience.cs`, `Sim/Mind.cs`, `Model/Ledger.cs` | `Experience` (meaning, source, confidence, salience, dominant emotion) stored by `Mind.Remember`; `Mind.Experiences`. `Ledger`/`LedgerRecord` for authored interpersonal entries. `ScalerKind.Memory` reads recall with `recall_half_life`. |
| Beliefs | `Model/BeliefStore.cs`, `Model/BeliefSeed.cs`, `Model/BeliefEffect.cs` | `BeliefStore.Seed/Get/Confidence/Nudge`; `Simulation.ApplyBeliefNudges` (rule-driven, `BeliefNudgeRule`) and `ApplyAuthoredEffects` (event-authored). |
| Appraisal | `Sim/Appraiser.cs`, `Rules/RuleSet.cs` (`AppraisalRule`) | `Appraiser.Appraise(mind, MatchContext, intensityScale, ...)` returns `EmotionContribution` list. |
| Emotion | `Model/EmotionSet.cs`, `Sim/Simulation.cs` | `EmotionSet.Add/Intensity/Decay/Soften`, `EmotionInstance`; `Simulation.PassTime` / `Fade` apply decay. |
| Motivation | `Sim/Motivator.cs`, `Rules/DecisionRules.cs` (`MotivationRule`), `Model/Motive.cs` | `Motivator.Raise(mind, percept, today, trace, parent)` returns `Motive` list (name, target, urgency, rule ids, scaler terms). Urgencies combined via `Accumulate.Combine` and `Accumulate.Knee`. |
| Deliberation | `Sim/Deliberator.cs`, `Rules/DecisionRules.cs` (`ProposalRule`, `CostRule`, `DecisionDynamics`) | `Deliberator.Decide`, private `Rank`, `Foresee`, `PriceOf`, `PickWithin`. Output `Decision` with `ScoredOption` list and `Contribution` records. |
| Intention (production) | `Sim/Deliberator.cs`, `Sim/SilentMorning.cs` | `Intention` (motive key, set-out act, trace id) and `Commitment` constants. Kept only across a `GoTo` walk: "an intention outlives an act only across a walk. It is not a plan". |
| Intention (experimental) | `Tests/EditMode/IntentionSelector.cs` | `IntentionSelector.Form(candidates, mind, percept, motive, ...)` returns `Formed`. Test-only; installed through the `SilentMorning.IntentOfAct` hook, which is null by default. |
| Action | `Model/ActionOption.cs`, `Sim/ActionCatalog.cs`, `Sim/SilentMorning.cs`, `Sim/PursuitOutcome.cs`, `Model/WorldState.cs` | `ActionKind { Wait, Observe, GoTo, CheckPantry, SearchRoom, Comfort, Eat }`; `ActionCatalog.Available(percept, dyn)` and `Endorsed(proposal, ...)`; `SilentMorning.Step/Begin/Complete` run the minute loop and turn acts into world events; `PursuitOutcome` records what came of acting on a want. |
| Trace | `Tracing/TraceLog.cs`, `Sim/DecisionTrace.cs` | `TraceLog.Add/Get/Chain/Why`; `TraceKind` per stage (section 9). |

Two model settings exist in `Data/Rules/decisions.json` under `deciding`:
`"dispositions": "respond"` and `"means": "end"` (the "primary baseline",
Model B). README says code defaults are unchanged and `Baselines.ModelA()` in
`Tests/EditMode/Baselines.cs` restores the old model for pre-existing tests.

---

## 4. Causal representation

There are two layers: the **production** representation in `Fallow.Core`, and
**experimental** representations that exist only inside test fixtures and
experiment JSON. Routes, typed roles and applicability exist only in the latter.

### 4.1 Production: evidence as scaler terms, provenance as trace ids

Evidence about a person is a `Scaler` whose kind is fixed
(`Rules/Scaler.cs`):

```csharp
public const string Trait = "trait";
public const string Value = "value";
public const string Belief = "belief";
public const string Ledger = "ledger";
public const string Emotion = "emotion";
public const string Perceptiveness = "perceptiveness";
public const string Constant = "constant";
public const string Need = "need";
public const string Memory = "memory";
```

Circumstances are a separate, closed gate type (`Rules/SituationCondition.cs`):

```csharp
public sealed class SituationCondition
{
    public bool? Alone { get; set; }
    public bool? InOwnRoom { get; set; }
    public bool? InSomebodyElsesRoom { get; set; }
    public bool? RoomHoldsFood { get; set; }
    public bool? SearchedThisRoomMyself { get; set; }
    public int? OthersPresentMin { get; set; }
```

Its doc comment: "a condition may only ask about circumstances ... It may never
ask about a trait, a value, a feeling or how hungry I am". It has no field for a
specific person being present or for being watched.

Provenance of a deliberation (`Sim/Deliberator.cs`):

```csharp
public sealed class Contribution
{
    public string MotiveKey { get; }
    public string MotiveName { get; }
    public double Urgency { get; }
    public double Fit { get; }
    public string ProposalId { get; }
    public int MotiveTraceId { get; }
    public double Amount => Urgency * Fit;
```

`Motive` carries `RuleIds`, `Terms` (the `ScalerTerm`s that raised it) and a
`TraceId`. Every `TraceRecord` carries `ParentIds` (section 9). In production
there is **no** route identity, no support/inhibitor/condition role, and no
enabler: a negative scaler factor is the only way to express "against"
(Scaler doc comment: "The factor may be negative, which is how a trait talks
someone out of a reading").

### 4.2 Experimental: candidate intention rules

`Data/Experiments/intentions.json` holds 10 frozen candidate rules
(sha256 `61e6412e...9d92`). Example entry, verbatim:

```json
{"id": "pulling_rank_needs_an_audience", "motives": ["restore_standing", "find_out", "guard_supplies"],
 "intent": "assert_authority", "when": {"others_present_min": 1}, "base": 0.1,
 "scaled_by": [{"kind": "trait", "name": "dominant", "factor": 0.45}, ...]}
```

Loaded into `IntentionSelector.Candidate` (`Id, Note, Motives, Intent, When,
Base, ScaledBy`).

### 4.3 Experimental: causal routes (causal-route experiment)

`Data/Experiments/causal-routes.json` declares one route per frozen rule:

```json
{"rule": "pulling_rank_needs_an_audience", "route": "authority_shown_to_witnesses",
 "means": "Asserting authority as something done in front of others: ..."}
```

In `Tests/EditMode/CausalRouteExperimentTests.cs`:

```csharp
sealed class RouteRule
{
    public Candidate C;
    public string[] Routes;
    public string[] Roles;
}
...
sealed class Statement
{
    public string Key;
    public double Coef;
    public double Amount;
    public bool IsBase;
    public string Route;
    public string Role;
    public string RuleId;
}
```

Evidence identity is a string key built by `EvidenceKey(Scaler)`, e.g.
`"trait:" + s.Name`, `"belief:" + predicate + "(" + args + ")"`,
`"emotion:" + name + "@" + target`; circumstances become
`"circumstance:" + gate`. Roles used: `driver`, `inhibitor`, `enabler`
(representation `D-enablers`). Representations: `enum Rep { A, B, C, D, DAlt, DEnablers, G }`.
Representation D groups statements per intention, per route, per evidence key;
"The same statement again within a route counts once; a different strength for
the same fact within a route is a conflict, flagged."

### 4.4 Experimental: reason semantics

`Data/Experiments/reason-semantics.json`, `vocabulary` (verbatim excerpts):

- `"part"`: "'push': the more of it, the stronger the reason. 'hold_back': the
  more of it, the weaker the reason; it can cancel its reason but not push
  against the intention. 'condition': it must be true of the person for the
  reason to apply at all, and it is not a strength."
- `"circumstance"`: "A feature of the situation that must hold for a reason to
  apply at all. It is not a strength."
- `"relation"`: "'independent' (the default) ... 'alternative' ...
  'reinforces' ... 'exclusive' ...".

Situations (5): s0 alone; s1 company, target absent, unwatched; s2 company,
target present, unwatched; s3 company, target absent, watched; s4 company,
target present, watched. Circumstance vocabulary: `anyone, company, nobody,
target_present, target_absent, watched, unwatched`.

Fixture types (`Tests/EditMode/ReasonSemanticsExperimentTests.cs`):

```csharp
sealed class Term  { public string Key; public int K; public double Factor; public string Part; public string Route; }
sealed class Route { public string Key; public string Intent; public string Direction; public string Circ;
                     public string Copied; public List<KeyValuePair<string, double>> Pushes ...; }
sealed class Relation { public string Kind; public List<string> Routes; }
```

Representations: `enum Rep { S, A, BParts, BCirc, B, C, ASel2, BSel0, BSel1, BPartsW }`.

### 4.5 Experimental: route applicability (latest, not yet run)

`Data/Experiments/route-applicability.json`, `vocabulary` excerpts:

- `"applicability"`: "whether the route applies at all in this moment, for this person."
- `"support"`: "a fact whose level makes an applicable route stronger"
- `"inhibitor"`: "... It never decides whether the route applies"
- `"condition"`: "a fact about the person (here, a belief) that must hold for the route to apply. It is not a strength"
- `"circumstance"`: "... It may concern the intention's target ($target ...) or anyone at all"

Case shape (first case, trimmed):

```json
{"id": "owning_c", "want": "avoid_exposure", "intent": "took_what_was_not_mine",
 "routes": [{"key": "owning_up", "applies_when": []}],
 "rules": [{"id": "owning", "route": "owning_up", "when": {}, "base": 0.05,
   "terms": [{"kind": "belief", "predicate": "answerable_for", "args": ["$self","missing_can"],
              "factor": 0.6, "role": "condition"},
             {"kind": "trait", "name": "honest", "factor": 0.3, "role": "support"}, ...]}]}
```

No C# fixture for this experiment exists in `Tests/EditMode` at HEAD.

---

## 5. Deliberation logic

### 5.1 Production: `Deliberator.Decide` (`Assets/_Project/Scripts/Core/Sim/Deliberator.cs`, lines 236-339)

Scoring (`Rank`, lines 350-416): each option's appeal is the sum over wants and
matching proposals of `motive.Urgency * proposal.Fit`; cost is the sum of
positive `CostRule` amounts; `Score => Appeal - Cost`. Sorted:

```csharp
return scored
    .OrderByDescending(s => s.Score)
    .ThenBy(s => s.Option.Key, StringComparer.Ordinal)
    .ToList();
```

Choice (verbatim, lines 251-289):

```csharp
var considered = ranked;
var commitment = Commitment.None;
if (holding != null)
{
    var serving = ranked
        .Where(r => r.Contributions.Any(c => c.Amount > 0.0 &&
                                             string.Equals(c.MotiveKey, holding.MotiveKey, StringComparison.Ordinal)))
        .ToList();

    if (!motives.Any(m => string.Equals(m.Key, holding.MotiveKey, StringComparison.Ordinal)))
        commitment = Commitment.NoLongerWanted;
    else if (serving.Count == 0)
        commitment = Commitment.Impossible;
    else if (serving[0].Score <= 0.0)
        commitment = Commitment.NotWorthIt;
    else
    {
        commitment = Commitment.Held;
        considered = serving;
    }
}

var top = considered[0];
var band = considered.Where(s => top.Score - s.Score <= dyn.AmbiguityBand).ToList();
var margin = considered.Count > 1 ? top.Score - considered[1].Score : top.Score;

ScoredOption picked;
Resolution resolution;

if (band.Count <= 1)
{
    picked = top;
    resolution = Resolution.Clear;
}
else
{
    picked = PickWithin(band, top.Score, dyn.AmbiguityBand, rng);
    resolution = Resolution.Ambiguous;
}
```

Tie settlement (lines 474-489):

```csharp
static ScoredOption PickWithin(IReadOnlyList<ScoredOption> band, double topScore, double width, Rng rng)
{
    const double Floor = 1e-6;

    var weights = band.Select(b => Math.Max(Floor, b.Score - (topScore - width))).ToList();
    var total = weights.Sum();
    var roll = rng.NextDouble() * total;

    for (var i = 0; i < band.Count; i++)
    {
        roll -= weights[i];
        if (roll <= 0.0) return band[i];
    }

    return band[band.Count - 1];
}
```

Intention left after the decision (lines 330-334): if the commitment held, the
held intention; else `new Intention(leading.Key, ...)` where `Decision.Leading`
is the want with the largest **positive** contribution to the chosen option; if
there is none, `Forms` stays null.

**a) Every candidate zero or negative.** The production code has no special
case: `considered[0]` (the highest score, possibly <= 0) is chosen, subject to
the ambiguity band. `Wait` is always available (see b) and
`decisions.json` has **no cost rule for `wait`** (checked: `costs` entries with
`action == "wait"` is empty), so Wait's score is its appeal, which is >= 0
(three proposals serve it: `leave_it_alone` for `guard_supplies` fit 0.3,
`stay_out_of_the_way` for `avoid_exposure` when alone fit 0.45, `let_it_be` for
`keep_peace` fit 0.5). If no want contributes positively to the chosen option,
`Decision.Leading` is null, no intention is formed, and `SilentMorning` records
the motive as `"nothing pressing"`. A held intention whose best serving option
scores <= 0 lapses with `Commitment.NotWorthIt`.

**b) Default/idle option.** Yes. `ActionCatalog.Available`
(`Sim/ActionCatalog.cs`):

```csharp
// Doing nothing is always possible, and is a real choice rather than
// the absence of one.
options.Add(new ActionOption(ActionKind.Wait, duration: dyn.MinutesFor("wait")));
```

`wait` lasts 5 minutes (`action_minutes`). "Continue current activity": a
person who is busy is not re-decided until the act finishes
(`SilentMorning.Step`); a person stopped by an interruption who re-chooses the
same act "picks it up where they left off" (`SilentMorning.Begin`, trace text
`"thought again, and carried on"`). There is no separate "continue" option.

**c) Randomness and ties.** `Model/Rng.cs` is a hand-written splitmix64. Its doc
comment: "The simulation uses randomness for exactly one thing: choosing between
actions a character has no real preference between." A grep for `NextDouble`,
`.Next(` and `Fork(` in Core finds only `Deliberator.cs:480` (`PickWithin`) and
`SilentMorning.cs:297` (`_rng.Fork(characterId + "@" + _world.Minute)`). Options
within `ambiguity_band` (0.08 in `decisions.json`) of the top are settled by a
roll weighted by distance into the band; outside the band the top wins with no
randomness. Exact score ties outside that path are broken ordinally by option
key. Code matches the README rule "Randomness settles ties and nothing else".

### 5.2 Experimental: `IntentionSelector.Form` (`Tests/EditMode/IntentionSelector.cs`, lines 146-190)

```csharp
foreach (var c in candidates)
{
    if (!c.Motives.Contains(motive.Name, StringComparer.Ordinal)) continue;
    formed.InScope++;
    if (!c.When.Matches(percept)) continue;
    formed.Matched++;

    var terms = ScalerEval.Evaluate(c.ScaledBy, mind, ctx);
    var weight = c.Base + terms.Sum(t => t.Amount);
    if (weight <= 0.0) continue;
    ...
    w.Weight += weight;
    ...
}

var ranked = byIntent.Values
    .OrderByDescending(w => w.Weight)
    .ThenBy(w => w.Intent, StringComparer.Ordinal)
    .ToList();

formed.Considered = ranked;
if (ranked.Count == 0) return formed;
formed.Intent = ranked[0].Intent;
```

a) Rules weighing <= 0 are dropped; if none remain, `Intent` is null
(`Line` prints `"none"`). b) No default intention. c) "There is no randomness
anywhere in here"; ties break ordinally by intention name.

### 5.3 Experimental selection policies in later fixtures

- Reason semantics (`ReasonSemanticsExperimentTests.cs` lines 696-718): three
  policies via `static int Sel(Rep r)`. Sel 0: an intention may form if any of
  its routes is admitted; Sel 1: if any route is applicable and has direction
  `toward`; Sel 2: if its support `> Eps`. If no candidate qualifies the token
  is `"none"`. Exact ties produce a token `"tie:" + a + "=" + b` (reported, not
  broken). The shipped-selector replica `Shipped(...)` drops rules with weight
  <= 0 and reports `"every compatible rule weighs zero or less, or none is compatible"`.
- Route applicability (`route-applicability.json`, `selection_policies`),
  verbatim: `"P0": "Current: among the representation's candidates, the largest
  support wins ... A candidate with no applicable route has support 0 and can
  still be chosen."` `"P1": "Active only: as P0, but only candidates with at
  least one applicable route may be chosen; if none has one, no intention."`
  Protocol: selection is "reported under two policies, never judged".

---

## 6. Scenarios and synthetic spaces

### 6.1 The real morning

File: `Assets/_Project/Data/Scenario/morning.json`, id `scenario001_s1_morning`,
loaded by `Scripts/Core/Data/MorningLoader.cs` into `MorningScenario`.

- **Characters:** `leo`, `daniel`, `mara`, `elena` (profiles in
  `Assets/_Project/Data/Minds/*.json`: traits, values, perception, needs,
  initial beliefs). All start in the kitchen.
- **Day / duration:** day 4, `"minutes": 90`. Loop: `SilentMorning.Run(minutes)`,
  one `Step()` per minute.
- **House:** 6 rooms (kitchen [pantry, common], living_room, hallway,
  brothers_room [leo, daniel], back_room [elena, mara], bathroom) with 6
  connections (bathroom not audible).
- **Start:** 2 portions; hunger leo 0.45, daniel 0.55, mara 0.50, elena 0.60.
- **Opening event** `m000-open`: Elena counts the pantry with the other three
  as witnesses; a can is missing (`topic: missing_can`).
- **What varies (variants):** the unseen night event only: `daniel_ate_it`,
  `daniel_hid_it`, `mara_ate_it`, `elena_fed_mara` (Mara witnesses),
  `miscount` (no event). Held-out variant: `leo_ate_it`.
- **Who is present / watching:** not scripted after minute 0. Presence
  emerges from movement and is read through `Percept.Present`; "watching" is
  the `observe` action and `Percept.JustWatched`. The morning file does not
  vary presence or watchers as a scenario parameter.
- Seeds: experiments use 10 seeds per variant (`const int MorningSeeds = 10`
  in `CausalRouteExperimentTests.cs` and `ReasonSemanticsExperimentTests.cs`).
  The protocols refer to "the same 50 baseline mornings" (5 variants x 10
  seeds is consistent with this; not separately confirmed).
- Real-morning regression set used by recent experiments (per
  `Docs/experiments/route-applicability/protocol.md`): "257 real
  pantry-checks, with every other cast member at the same moment: 1,028 real
  decisions".

S0 used a different script: `Assets/_Project/Data/Scenario/backstory.json`,
12 events (`b01`-`b09`, `p01`-`p03`), "Days 1-3 of the crisis plus three day-4
probe events ... No variants, no hidden truth, no decisions."

### 6.2 The 2,187-profile synthetic grid

File: `Assets/_Project/Data/Experiments/held-out-people.json`, key `sweep`
(sha256 `0b3f4bc9...4131`). Verbatim note: "Every combination of the seven
shipped traits at three levels is one profile, in the fixed order below ...
3^7 = 2187 profiles."

| Dimension | Levels |
|---|---|
| Traits (7): `anxious, cautious, dominant, empathetic, honest, impulsive, proud` | `0.15, 0.5, 0.85` each |
| Values | all six of `autonomy, closeness, control, fairness, family_safety, respect`, "rotated left by (i mod 6). Rank decides weight" |
| Beliefs | belief set `(i mod 4)` of: none; `role_claim($self, leads_family)` 0.8; `answerable_for($self, missing_can)` 0.9; both |

The same file also declares four hand-placed held-out people (`hollow`,
`warden`, `drifter`, `firebrand`) outside the cast's ranges.

Situational crossings used with the grid:
- Causal routes: "want look_after, in company in the kitchen, over the 2,187
  profiles" (`causal-routes.json`, `synthetic.note`).
- Reason semantics: 5 situations (s0-s4, section 4.4).
- Route applicability: 6 presence sets, `n0` nobody, `n1` mara, `n2` daniel,
  `n3` elena, `n4` daniel+elena, `n5` mara+daniel; "2,187 x 6 = 13,122 per
  case and condition" (`protocol.md`).

---

## 7. Experiment records

Dates are from `git log` (first and last commit touching the folder).
"Full-suite" counts are quoted from the reports.

### 7.1 Slices

| Slice | Path | Dates | Summary |
|---|---|---|---|
| S0 | `Docs/slices/S0/review.md`, `traces/` | 2026-09-10 to 09-12 | Backstory script through four minds; per-event pipeline measured against `Data/Tests/expectations.json`. One event, four different experiences. |
| S1 | `Docs/slices/S1/review.md`, `held-out-predictions.md`, `held-out-results.md`, `traces/`, `batch/` | 09-12 to 09-15 | The deciding layer and the silent house: four people choose acts for 90 minutes. Known defects in section 5. |
| S1.1 | `Docs/slices/S1.1/` (report, diagnosis-*, held-out-predictions/results, fading-rate) | 09-12 to 09-15 | Counterfactual: does a night event change the same person? Three measured changes to the circumstance pathway; held-out `leo_ate_it`. |
| S1.2 | `Docs/slices/S1.2/` (report, audit-*, reach-*, `c3-rejected/`) | 09-13 to 09-15 | Deliberation pass: whether a changed want reaches the choice. A rejected change C3 kept in `c3-rejected/`. |
| S1.3 | `Docs/slices/S1.3/` | 09-15 | What eating does to wanting food; why nobody eats. |
| S1.4 | `Docs/slices/S1.4/` (incl. attribution.md, held-out-*) | 09-15 | Sitting with somebody and the want to look after them. Introduced the two failures still left failing (report section 9). |
| S1.5 | `Docs/slices/S1.5/` (S1.5-all.md, walks.md, held-out-*) | 09-15 | Traits and values as always-on wants vs dispositions (diagnostic). |
| S1.6 | `Docs/slices/S1.6/` | 09-16 | Walking to ends not worth pursuing; two switchable fixes (`means: end`, dispositions). |
| S1.7 | `Docs/slices/S1.7/` | 09-16 to 09-17 | Whether a past event changes a later decision; eleven earlier slights needed to flip a reading. |
| Audit | `Docs/audit/system-understanding-audit.md`, `census.md` | 09-17 | System understanding audit and want/act census (measured on Model A). |

### 7.2 Experiments (`Docs/experiments/`)

Each folder generally holds `predictions.md` (frozen before running),
`results.md`, `measurements.md` (generated by the fixture), `report.md` and a
merged `<name>-all.md`. Some also hold `classification.json`,
`prediction-model.py`, `protocol.md` and `annotation/` (`items.json`,
`protocol.md`, `responses/`).

| Experiment | Folder | Dates (first / last) | Frozen predictions | Summary |
|---|---|---|---|---|
| Decision sensitivity | `decision-sensitivity/` (baseline.md, results.md, report.md) | 09-20 `500066c` / `95d0b50` | none listed | Ships Model B as primary baseline; measures how far one want must move before the act changes. 377 tests, 375 pass, 2 fail. Contains an erratum added by the action-representation audit. |
| Action representation audit | `action-representation/` (diagnostic.md, report.md) | 09-20 `b6882f9` | none (audit) | Read-only audit: "Of 918 world events the morning's acts produced, none carries an intent." |
| Intent carrying | `intent-carrying/` | 09-20 `a79a048` / `95d0b50` | `predictions.md` | Adds the `IntentOfAct` hook; meaning survives in 373 of 373 carried acts, but effect stops at memory unless a rule reads the intent. |
| Episode | `episode/` | 09-20 `b075664` / `95d0b50` | `predictions.md` | One injected episode (Daniel searches Mara's bag) changes her wants 17 of 17 runs, act 7 of 17, fades within about half an hour. |
| Accumulated history | `accumulated-history/` | 09-20 `7413758` / `95d0b50` | `predictions.md` | Repeated history flips Elena's reading from threat to disrespect (10 of 10 seeds); the act does not change (10 of 10). 394 tests, 392 pass. |
| Same act, different reason | `same-act-different-reason/` | 09-20 `c9af832` / `db2be76` | `predictions.md` (`c9af832`) | One act for six reasons can be told apart; a reason matters only where an appraisal rule names it. |
| Intention formation | `intention-formation/` | 09-20 `8ede500` / `dce227d` | `predictions.md` + blind-authored `Data/Experiments/intentions.json` (`8ede500`) | Ten authored candidate rules: a want constrains an intention without deciding it; six of seven wants many-valued. |
| Intention generalization | `intention-generalization/` | 09-20 `132e86e` / `dce227d` | `predictions.md` + `held-out-people.json` (`132e86e`) | Frozen rules run on 2,187 sweep profiles; they generalize but rank by a sum a duplicate rule can move. |
| Intention ranking | `intention-ranking/` (+ classification.json) | 09-22 `964d056` / `568e1c0` | `predictions.md` (`964d056`) | Requirements for a selector; copying one rule reverses 48.8 % of conclusions; theorem that anonymous sums cannot fix it. |
| Intention representation | `intention-representation/` (+ classification.json) | 09-22 `a21fc76` / `2fed9f8` | `predictions.md` (`a21fc76`) | Evidence identity (B): restatement changes 0 of 306,180 cases; double-counting one fact across two reasons changes 660 conclusions. |
| Causal routes | `causal-routes/` (+ classification.json, annotation/) | 09-23 `3780435` / `5d0f6b8` | `predictions.md`, `Data/Experiments/causal-routes.json`, annotation (`3780435`) | Declared route identity (D) separates "two reasons on one fact" from "one reason written twice" in 2,187 of 2,187 cells, passes 18 of 18 families; cannot express an enabler or a target-specific circumstance. |
| Reason semantics | `reason-semantics/` (+ classification.json, prediction-model.py, annotation/) | 09-23 `e5a5131` / 09-24 `8ec782c` | `predictions.md`, `Data/Experiments/reason-semantics.json`, annotation (`e5a5131`) | Five required distinctions (identity, part, circumstance, reinforces-reference, no-intention). Report recommends "MODIFY" (section 13). Condition-as-condition changes 99 of 1,028 real decisions (README). |
| Route applicability | `route-applicability/` (predictions.md, protocol.md, prediction-model.py, annotation/items.json) | 09-24 `431db11` only | all of the folder plus `Data/Experiments/route-applicability.json` (`431db11`) | Not yet run. See 7.3. |

### 7.3 CS2 specifically

**The strings "CS2" and "Causal Semantics 2" do NOT appear anywhere in the
repository** (searched all tracked text, excluding `Library/`, `Logs/`,
`test-results.xml`; the only hits for "CS2" were unrelated tokens in
`Packages/manifest.json`, `Packages/packages-lock.json`,
`ProjectSettings/Physics2DSettings.asset`). The phrase "Causal semantics"
appears only as a heading in `Docs/experiments/causal-routes/report.md`
line 436.

The most recent experiment, and the only one frozen but not yet run, is
**route applicability**. If CS2 refers to it (inference, not confirmed by any
file):

- **Frozen by:** commit `431db11` (2026-09-24 02:12 +0100), message "docs:
  predictions, protocol and cases for the route-applicability experiment ...
  Committed before any fixture or reviewer exists."
- **Frozen cases:** `Assets/_Project/Data/Experiments/route-applicability.json`,
  16 cases (`owning_c, owning_e, settling_c, settling_e, side_mara,
  side_daniel, side_elena, away_mara, duty_mara, scene_mara, stepping_in,
  only_side_mara, only_owning, only_fair, weak_pull, owning_ambiguous`) in
  ten families A to J.
- **Frozen predictions:** `Docs/experiments/route-applicability/predictions.md`
  (analytic vs empirical), with `prediction-model.py` as an independent Python
  derivation, and `annotation/items.json` (16 items with answer key).
- **Frozen hashes** (from `protocol.md`; I recomputed sha256 of each file at
  HEAD and **all 8 match**): `intentions.json`, `causal-routes.json`,
  `held-out-people.json`, `reason-semantics.json`,
  `route-applicability.json` (`a0e96540...c426`),
  `CausalRouteExperimentTests.cs`, `ReasonSemanticsExperimentTests.cs`,
  `IntentionSelector.cs`.
- **Representations compared** (protocol table): **S** shipped selector
  (control); **A** the causal-route D unchanged; **B** typed roles; **C**
  applicability layer (one construct for conditions and circumstances);
  ablations **C-entity** (presence generic only), **C-conditions**
  (conditions read as weights), **C-split** (conditions and circumstances as
  separate constructs); counterexample **C-kind** (role inferred from kind of
  fact). Selection policies P0 and P1 are reported separately.
- **Annotation plan:** six Claude Code subagents (2 opus, 2 sonnet, 2 haiku),
  "They are language models, not people".
- **Fixture:** no `RouteApplicability*` test file exists in
  `Assets/_Project/Tests/EditMode` at HEAD.
- **Activity observed during this inspection:** an untracked folder
  `Docs/experiments/route-applicability/annotation/responses/` appeared while
  this report was being prepared, holding `reviewer-1.json` (02:14:43 +0100)
  and `reviewer-2.json` (02:14:52 +0100). It was listed, not opened or
  touched. This suggests the route-applicability annotation step is in
  progress in another session.

If CS2 instead refers to reason semantics (which answered the "causal
semantics" gap named in the causal-routes report), its frozen material is
`Data/Experiments/reason-semantics.json` (sha256 `5ffe17fe...7638`),
`Docs/experiments/reason-semantics/predictions.md` and `annotation/`, frozen in
commit `e5a5131` (2026-09-23 22:02), with results in `8ec782c`.

---

## 8. Global progress metric

**NOT FOUND.**

Searched (case-insensitive) for `progress`, `global.*progress`,
`simulation progress`, `human-simulation progress`, `progress metric`,
`overall progress`, and percentage phrases near "human" in:
- all of `Docs/`, `README.md`, `Assets/` (code, JSON), `merge-slice-docs.py`,
  `run-tests.sh`;
- all tracked files except Unity-generated folders (only hit:
  `ProjectSettings/VersionControlSettings.asset`, unrelated);
- commit messages on all branches (`git log --all -i --grep=progress`: no hits);
- the user memory folder for this project (two unrelated memory files).

No definition, current value or history of a project-level progress
percentage exists in the repository.

---

## 9. Trace format

### 9.1 In code

`Assets/_Project/Scripts/Core/Tracing/TraceLog.cs`:

```csharp
public enum TraceKind
{
    Event, Access, Interpretation, Experience, BeliefChange, LedgerEntry,
    Appraisal, Emotion, Motive, Deliberation, Action, Consequence, Outcome
}

public sealed class TraceRecord
{
    public int Id { get; }
    public TraceKind Kind { get; }
    public string CharacterId { get; }
    public string EventId { get; }
    public string Summary { get; }
    public IReadOnlyList<int> ParentIds { get; }
    public IReadOnlyDictionary<string, string> Data { get; }
```

In-memory only (`TraceLog.Add/Get/For/ForEvent/Chain/Why`). Doc comment: "This
is a development instrument, not a game system." Files are written by the
test fixtures and report builders (`Sim/S0Report.cs`, `Sim/S1Report.cs`,
`Testing/BatchRunner.cs`, the experiment fixtures). README: running the suite
"regenerates everything under `Docs/slices/*/traces` and `Docs/slices/S1/batch`".

### 9.2 On disk

| Path | Format |
|---|---|
| `Docs/slices/S0/traces/full-trace.txt` (1,292 lines) | `#id [Kind] character (event) <- #parent` then indented summary and key: value data |
| `Docs/slices/S0/traces/*.md` | human-readable Markdown views (event-by-event, why-they-felt-that, ...) |
| `Docs/slices/S1/traces/full-trace-daniel_ate_it-seed1.txt` (11,488 lines) | one line per record: `Kind [character]: summary  {key=value, ...}` |
| `Docs/slices/S1/traces/morning-<variant>.md`, `a-mother-made-to-feel-like-a-suspect.txt`, `smoke-morning.md` | Markdown / text narratives |
| `Docs/slices/S1/batch/decisions.csv` | CSV: `variant,seed,minute,character,room,action,target,motive,urgency,resolution,margin,outcome` |
| `Docs/experiments/*/measurements.md`, `results.md` | generated Markdown tables |

### 9.3 Real examples (quoted, not generated)

From `Docs/slices/S0/traces/full-trace.txt`:

```
#4 [Access] elena (b01) <- #0
      was there and saw it
#5 [Interpretation] elena (b01) <- #4
      read it as support (0.60)
        meaning: support
        weight: 0.60
        rules: a_good_turn_reads_as_support -> support 0.60
#6 [Appraisal] elena (b01) <- #5
      support touched closeness: gratitude 0.60 toward daniel (closeness)
        emotion: gratitude
        concern: closeness
        intensity: 0.60
        rules: help_at_all_is_felt_as_gratitude 0.91 (base 0.10; trait empathetic 0.90 x 0.30 = +0.27; value closeness 0.75 x 0.25 = +0.19; value family_safety 1.00 x 0.35 = +0.35)
        toward: daniel
```

From `Docs/slices/S1/traces/full-trace-daniel_ate_it-seed1.txt` line 112
(last committed in `b45f007`, 2026-09-15, i.e. before Model B shipped),
truncated at the `serves` field:

```
Deliberation [elena]: had no real preference, and comfort:daniel is what happened  {chose=comfort:daniel, score=0.977, resolution=too close to call, margin=0.000, options=comfort:daniel 0.977 (for 1.18, against 0.21) | comfort:mara 0.977 (for 1.18, against 0.21) | check_pantry 0.910 (for 0.98, against 0.07) | wait 0.746 (for 0.75, against 0.00) | ...
```

The first rows of `Docs/slices/S1/batch/decisions.csv`:

```
daniel_ate_it,1,1,daniel,kitchen,check_pantry,,find_out,0.982,clear,0.179,found 2 portions left
daniel_ate_it,1,1,elena,kitchen,comfort,daniel,look_after:daniel,0.877,too_close,0.000,sat with daniel
```

---

## 10. Tests

### 10.1 Projects

One test assembly: `Fallow.Tests.Core` (`Assets/_Project/Tests/EditMode`), NUnit
EditMode, run by `run-tests.sh` via the Unity CLI (`unity test ... --mode
EditMode --timeout 7200`). Non-test helpers in the folder: `TestPaths.cs`,
`Baselines.cs`, `IntentionSelector.cs`, `S15Measures.cs`, `S16Measures.cs`,
`S17Measures.cs`, `SensitivityMeasures.cs`.

### 10.2 Counts

Counting `[Test]`/`[Test, ...]` attributes gives **448**, matching the last
results file. No `[TestCase]`, `[TestCaseSource]` or `[Values]` were found.

| Area | Files (tests) | Subtotal |
|---|---|---|
| Core units: data, world, pipeline | ProfileTests 12, WorldEventTests 9, WorldTests 15, InterpreterTests 27, MindStateTests 24, SimulationTests 12, SmokeTests 1 | 100 |
| S0 scenario | Scenario001Tests 21 | 21 |
| Deciding / morning | DecidingTests 14, DeliberationTests 11, MorningTests 18, EmergentMomentTest 1, BaselineTests 6 | 50 |
| S1 | S1ExperimentTests 12, S1HeldOutTests 6 | 18 |
| S1.1 | S11BeliefCarrier 5, S11CausalExamples 3, S11Diagnosis 2, S11Experiment 11, S11HeldOut 7, S11Locality 2, S11Urgency 5 | 35 |
| S1.2 | S12Aggregation 6, S12Commitment 10, S12Diagnosis 3, S12Experiment 10 | 29 |
| S1.3 | S13Diagnosis 7, S13Experiment 12, S13Lifecycle 4 | 23 |
| S1.4 | S14Attribution 1, S14Diagnosis 5, S14Experiment 8, S14HeldOut 6 | 20 |
| S1.5 | S15Diagnosis 2, S15Disposition 7, S15Experiment 8, S15HeldOut 9, S15Pacing 1 | 27 |
| S1.6 | S16Diagnosis 5, S16Experiment 8, S16HeldOut 10, S16Means 10 | 33 |
| S1.7 | S17Diagnosis 4, S17Experiment 8 | 12 |
| Audits | AuditCensusTests 1, ActionRepresentationAuditTests 7 | 8 |
| Experiments | SensitivityExperiment 8, IntentCarrying 4, Episode 3, AccumulatedHistory 3, SameAct 7, IntentionFormation 7, IntentionGeneralization 6, IntentionRanking 10, IntentionRepresentation 8, CausalRoute 7, ReasonSemantics 9 | 72 |
| **Total** | | **448** |

### 10.3 Last recorded run

`test-results.xml` (git-ignored, repo root): `total="448" passed="446"
failed="2" inconclusive="0" skipped="0"`, start `2026-09-23 22:01:33Z`, end
`2026-09-24 00:41:22Z`, duration 9,589 s. Failed:
- `Fallow.Tests.Core.S1ExperimentTests.SomebodyStillPacesBetweenTwoRoomsAndThisIsHowBadly`
- `Fallow.Tests.Core.EmergentMomentTest.BeingWatchedByYourSonMakesYouWantToLeaveTheRoom`

README: "Two tests fail since S1.4, the pacing gate and one check in the
emergent-moment test ... left failing rather than loosened." Code and doc agree.

`Logs/unity-test-run.log` (2026-09-24 01:41) contains `"code": "TESTS_FAILED",
"message": "Tests failed: Unity process exited with code 2."`, consistent with
the two failures.

### 10.4 Ignored, skipped, inconclusive, known-failing

- No `[Ignore]`, `[Explicit]` or `[Category]` attributes found.
- Runtime `Assert.Ignore` / `Assert.Inconclusive` (conditional):
  - `Tests/EditMode/SameActExperimentTests.cs:557` `Assert.Ignore("no witness to the fixed act")`
  - `Tests/EditMode/MorningTests.cs:391` `Assert.Inconclusive("nobody searched anything in this run")`
  - `Tests/EditMode/S12CommitmentTests.cs:239` `Assert.Inconclusive("nothing tried landed hard enough on " + who + " to stop them")`
  None fired in the last run (0 inconclusive, 0 skipped).
- Characterisation tests pinning known defects (pass while the defect exists):
  - `MorningTests.cs:84` "if this starts passing, the defect is fixed and the test should be turned round"
  - `S1ExperimentTests.cs:243` "if this starts failing, circumstances have started to reach behaviour and the gate should be turned round"
  - `S12AggregationTests.cs:165` `StandingStillIsStillCreditedForWhatItAvoidsAndThisIsAKnownDefect()`
- Known-failing: the two tests in 10.3.

### 10.5 Documentation vs observed run time (MISMATCH)

- `README.md`: the suite "Takes about an hour".
- Last `test-results.xml`: 9,589 s (about 2 h 40 min).
- `run-tests.sh` passes `--timeout 7200` (2 h), shorter than the recorded run.
  The recorded run nonetheless completed with a results file; how it was
  launched was not determined.
- Earlier reports quote smaller suites: 377 tests (decision sensitivity),
  394 tests (episode, intent carrying, accumulated history).

---

## 11. Open issues and TODOs

`grep -rE "TODO|FIXME|HACK|XXX"` over `Assets/`, `Docs/`, `README.md`,
`merge-slice-docs.py`, `run-tests.sh`: **no matches.**

Documented open issues are kept as prose instead. Locations named by
`README.md` ("Known defects"):
- `Docs/slices/S1/review.md` section 5
- `Docs/slices/S1.1/report.md` section G
- `Docs/slices/S1.2/report.md` section 6
- `Docs/slices/S1.3/report.md` section 9
- `Docs/slices/S1.4/report.md` section 9 (the two failing tests)
- `Docs/slices/S1.5/report.md` section 5
- `Docs/slices/S1.6/report.md` section 7
- `Docs/slices/S1.7/report.md` section 3

README also lists, verbatim in substance: a reading's weight is discarded
("only the winning meaning reaches appraisal"); "a belief never decays"; the
ledger "is authored rather than simulated: no rule writes one, and five of its
eight entry kinds are read by nothing"; `Comfort` "still softens another
person's feelings directly, as technical debt".

The causal-routes report lists UNPROVEN items (line ~446): whether the frozen
`protect` and `assert_authority` routes combine or exclude; whether "only the
stronger operates" describes any real pair; "What should happen when the only
candidate has no active reason". The route-applicability experiment frames that
last question as the selection layer (P0/P1).

### 11.1 Other code/doc mismatches or naming notes observed

- **Two meanings of "intention".** `Fallow.Core.Sim.Intention` is the want
  behind a walk, kept only across `GoTo`. The intention experiments' intentions
  (`assert_authority`, `took_what_was_not_mine`, ...) are produced by
  `IntentionSelector` in the test assembly and are not part of the production
  pipeline. README section "What it does so far" shows no intention stage.
- **README "Layout"** lists only `Docs/slices/S0, S1`; docs also live in
  `Docs/slices/S1.1`-`S1.7`, `Docs/experiments/`, `Docs/audit/`.
- **README "Running the tests"** duration (section 10.5).
- `route-applicability.json` has no Unity `.meta` file (section 2).
- The S1 full trace quoted in 9.3 was last regenerated 2026-09-15, before the
  data switched to Model B (`c243050`, 2026-09-20); README says tests written
  before the change select Model A, so this file describes Model A.

---

## Things I could not determine

1. **What "CS2" / "Causal Semantics 2" refers to.** Neither string exists in
   the repo. Section 7.3 gives both candidates (route applicability, frozen in
   `431db11`; reason semantics, frozen in `e5a5131`).
2. **What exactly is running now.** `tasklist` showed no process whose name
   contains "unity" when checked; no fixture file for route applicability
   exists at HEAD; the last results file ended 2026-09-24 00:41Z. But
   reviewer response files for route applicability appeared at 02:14 +0100
   during this inspection (7.3), so some part of that experiment is active.
   Which process writes them was not determined.
3. **A global human-simulation progress metric:** NOT FOUND (section 8).
4. **How the last 9,589 s suite run completed** under a 7,200 s CLI timeout.
5. **Whether "50 baseline mornings" is exactly 5 variants x 10 seeds**: the
   seed constant and variant count are consistent with it, but the mapping was
   not traced through `BatchRunner`/fixture code.
6. **Contents of the annotation `responses/` folders** for causal routes and
   reason semantics were not read.
