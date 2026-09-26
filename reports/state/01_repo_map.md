# 01 · Repository map

Written 2026-09-26 by read-only inspection of `C:\Users\Akrem\Desktop\Projects\Fallow` at HEAD
`8b183d4` on `main`. Nothing was built, tested or run apart from the listing, counting, version
and git commands in the appendix. This file is the only file added to the repository.

Paths are relative to the repository root unless they start with a drive or `/c/`.
File counts are `find -type f` counts. "Excluding skipped" means `.venv`, `Library`, `Temp`,
`obj`, `bin`, `node_modules`, `cache`, `runs` and `__pycache__` were left out, as instructed.

---

## 1. Top-level contents

### Folders

| Folder | Files (all) | Files (excluding skipped) | Tracked by git | What it contains |
|---|---:|---:|---:|---|
| `Assets/` | 325 | 325 | 325 | Unity assets: 151 files plus 174 `.meta`. The project itself is `Assets/_Project/` (simulation code, tests, JSON data). The rest is the Unity URP template: `Scenes/SampleScene.unity`, `Settings/` (URP render-pipeline assets), `TutorialInfo/`, `InputSystem_Actions.inputactions`, `Readme.asset`. |
| `Docs/` | 191 | 190 | 190 | Markdown reports, reviews, traces and JSON results: `slices/` (S0 to S1.7), `experiments/` (13 experiments), `audit/` (2 files), `understanding/` (5 files plus `runs/`, 1 file). 160 `.md`, 25 `.json`, 3 `.txt`, 2 `.py`, 1 `.csv`. |
| `Library/` | 30,978 | 0 (skipped) | 0 (ignored, `.gitignore:2`) | Unity's generated cache, including `Library/PackageCache/`, which `narrate.sh` reads Newtonsoft.Json from. |
| `Logs/` | 7 | 7 | 0 (ignored, `.gitignore:7`) | Unity CLI logs and results from earlier runs: `unity-test-run.log`, `unity-test-filter.log`, `unity-test-long.log`, `test-results-filter.xml` (1 test, 2026-09-15), `test-results-long.xml` (17 tests, 2026-09-15), `Packages-Update.log`, a shader compiler log. |
| `Packages/` | 2 | 2 | 2 | `manifest.json` and `packages-lock.json` (Unity Package Manager). |
| `ProjectSettings/` | 24 | 24 | 24 | Unity project settings, including `ProjectVersion.txt`. |
| `Prototypes/` | 3,927 | 56 | 215 | One prototype, `Prototypes/llm-morning/`: a Python rules-plus-LLM (Gemini) version of the morning, steps 1 to 5, with frozen copies of earlier steps (`v1/` to `v4/`), reports, recorded runs (`runs/`, 132 files) and the model-answer cache (`cache/`, 28 files). `.venv/` and `__pycache__/` make up most of the 3,927. |
| `Tools/` | 10 | 4 | 0 (**untracked**) | `Tools/narrate-morning/`: a C# console narrator (`Program.cs`, `Narrator.cs`, `NarratorTest.cs`) compiled against `Assets/_Project/Scripts/Core` by `narrate.sh`; build output in `bin/` (6 files, ignored by `Tools/narrate-morning/.gitignore`). |
| `UserSettings/` | 2 | 2 | 0 (ignored, `.gitignore:8`) | `EditorUserSettings.asset`, `Search.settings`. |
| `.git/` | 567 | n/a | n/a | Git repository; 63 commits on `main`. |

`Temp/`, `obj/`, `bin/` (top level), `Build/`, `Builds/`, `node_modules/`, `.github/`, `.claude/`: NOT FOUND at the top level.

### Files at the root

| File | Size | Tracked | What it is |
|---|---:|---|---|
| `README.md` | 12,555 B | yes | Project README: what each slice and experiment found, layout, how to run tests, the five rules, known defects. |
| `CLAUDE.md` | 89 B | **untracked** | Agent instruction file (full text in section 2). |
| `CONTEXT_REPORT.md` | 50,886 B | **untracked** | "Fallow: context report for a reviewer", prepared 2026-09-24 at HEAD `431db11`, read-only. |
| `run-tests.sh` | 1,717 B | yes | Runs the Unity EditMode suite headlessly and prints a per-test summary. |
| `narrate.sh` | 4,887 B | **untracked** | Builds and runs `Tools/narrate-morning` without starting Unity. |
| `merge-slice-docs.py` | 3,628 B | yes | Merges every Markdown file of a slice or folder into one `<name>-all.md`. |
| `test-results.xml` | 1,189,924 B | no (ignored, `.gitignore:50`) | NUnit results of the last full run (2026-09-24). |
| `.gitignore` | 690 B | yes | Unity, IDE, OS, secrets, test output, prototype `.venv`. |
| `.gitattributes` | 97 B | yes | `* text=auto eol=lf`; binary for png, jpg, fbx, wav, mp3, dll. |

### Inside `Assets/_Project/`

| Path | Contents |
|---|---|
| `Scripts/Core/` | `Fallow.Core.asmdef` (`noEngineReferences: true`, references only `Newtonsoft.Json.dll`) and 55 `.cs` files: |
| `Scripts/Core/Data/` | 10 `.cs`: loaders and validators (`MorningLoader`, `ProfileLoader`, `RuleSetLoader`, `ScenarioLoader`, `VocabularyLoader`, `DecisionRuleValidator`, `ProfileValidator`, `RuleSetValidator`, `ScenarioValidator`, `Vocabulary`). |
| `Scripts/Core/Model/` | 21 `.cs`: data types (`Access`, `Accumulate`, `ActionOption`, `BeliefEffect`, `BeliefSeed`, `BeliefStore`, `EmotionSet`, `EventKind`, `Experience`, `Ledger`, `LedgerEffect`, `MorningScenario`, `Motive`, `Percept`, `Profile`, `Relation`, `Rng`, `RoomGraph`, `ScenarioScript`, `WorldEvent`, `WorldState`). |
| `Scripts/Core/Rules/` | 6 `.cs`: `Condition`, `DecisionRules`, `RuleSet`, `Scaler`, `ScalerEval`, `SituationCondition`. |
| `Scripts/Core/Sim/` | 13 `.cs`: `ActionCatalog`, `Appraiser`, `DecisionTrace`, `Deliberator`, `Interpreter`, `Mind`, `Motivator`, `PursuitOutcome`, `S0Report`, `S1Report`, `Scenario001`, `SilentMorning`, `Simulation`. |
| `Scripts/Core/Testing/` | 4 `.cs`: `BatchRunner`, `Counterfactual`, `DeliberationAudit`, `MotivationSources`. |
| `Scripts/Core/Tracing/` | 1 `.cs`: `TraceLog`. |
| `Tests/EditMode/` | `Fallow.Tests.Core.asmdef` and 65 `.cs` (section 5). |
| `Data/Minds/` | `daniel.json`, `elena.json`, `leo.json`, `mara.json` (the four people). |
| `Data/Rules/` | `rules.json`, `decisions.json`, `vocabulary.json`. |
| `Data/Scenario/` | `morning.json`, `backstory.json`. |
| `Data/Experiments/` | `causal-routes.json`, `held-out-people.json`, `intentions.json`, `reason-semantics.json`, `route-applicability.json`. |
| `Data/Tests/` | `expectations.json`. |

### Inside `Docs/`

| Path | Files |
|---|---|
| `Docs/slices/` | `S0` (1 + `traces/` 5), `S1` (3 + `batch/` 3 + `traces/` 8), `S1.1` (14), `S1.2` (14 + `c3-rejected/` 5), `S1.3` (6), `S1.4` (9), `S1.5` (9), `S1.6` (8), `S1.7` (7). |
| `Docs/experiments/` | `accumulated-history` (5), `action-representation` (3), `causal-routes` (6 + `annotation/` 2 + `annotation/responses/` 6), `decision-sensitivity` (4), `episode` (5), `intent-carrying` (4), `intention-formation` (5), `intention-generalization` (5), `intention-ranking` (6), `intention-representation` (6), `reason-semantics` (7 + `annotation/` 2 + `annotation/responses/` 6), `route-applicability` (7 + `annotation/` 1 + `annotation/responses/` 6), `same-act-different-reason` (5). |
| `Docs/audit/` | `census.md`, `system-understanding-audit.md` (both dated 2026-09-17). |
| `Docs/understanding/` | `commit-log.md` (**untracked**), `morning-walkthrough.md`, `narrator-setup.md`, `target-morning.md`, `understanding-all.md`, `runs/daniel_ate_it-1.md`. |

### Inside `Prototypes/llm-morning/` (excluding `.venv`, `cache`, `runs`, `__pycache__`)

| Path | Contents |
|---|---|
| root, 22 files | `morning.py` (entry point), `world.py` (rules layer), `data.py`, `gemini.py` (API client, fake, cache), `story.py`, `talk.py`, `metrics.py`, `metrics3.py`, `metrics4.py`, `metrics5.py`, `list_models.py`, `probe_model.py`, `probe_prompt.py`, `test_morning.py`, `config.json`, `requirements.txt`, `.gitignore`, `REPORT.md`, `REPORT-2.md` … `REPORT-5.md`. |
| `v1/` (6), `v2/` (8), `v3/` (9), `v4/` (10) | Frozen copies of the code of steps 1 to 4, with `v1/transcript.py` and `v2/`–`v4/check.py` replays. |
| `reports/` (**untracked**) | `llm_call_audit.md`, `knowledge_audit.md` (both dated 2026-09-26). `knowledge_audit.md` was written at 01:57 today, during this inspection; it was not present at the first listing. |

---

## 2. Agent and project instruction files

### `CLAUDE.md` (repo root, untracked), full text

```
Never stop processes by name or broad filters; only by the exact process ID you started.
```

### Claude Code auto-memory for this project (outside the repository)

Location: `C:\Users\Akrem\.claude\projects\C--Users-Akrem-Desktop-Projects-Fallow\memory\`.
Full text of each file:

`MEMORY.md`

```
- [Merged docs, always](slice-docs-merged-file.md) - results are not delivered until `merge-slice-docs.py` has produced the all-in-one file; never wait to be asked, and re-merge whenever a doc changes
- [Unity filtered test runs](unity-filtered-test-runs.md) - one fixture in ~1 min via `unity test --filter`; full suite is ~3 h 10 min and outgrows run-tests.sh's 7200 s timeout
```

`slice-docs-merged-file.md`

```
---
name: slice-docs-merged-file
description: "Never report results without the merged all-in-one md file; produce it unasked, every time"
metadata:
  node_type: memory
  type: feedback
  originSessionId: cf761629-b415-4534-9679-53c67ff7bc18
  modified: 2026-09-20T01:56:11.178Z
---

**Results are not delivered until the merged file exists.** Whenever any piece of work produces
documents - a slice, an audit, an experiment - keep the individual md files as usual **and
always produce the merged one too, without being asked, in the same turn that reports the
results**. Then name it (and send it) alongside the individual files.

Run it at the repo root:
- a slice: `python merge-slice-docs.py S1.6` -> `Docs/slices/S1.6/S1.6-all.md`
- anything else: `python merge-slice-docs.py Docs/experiments/<name>` -> `<name>-all.md` in that
  folder (the script took folder paths from 2026-09-19).

Asked for at S1.5, then again at S1.6, S1.7, and again on 2026-09-20 after the intent-carrying
experiment, where I reported the results and waited to be told. **Do not wait to be told.**
Treat the merge as the last step of producing results, like saving the file.

**Why:** the user reads and shares a whole piece of work as one document, and having to ask for
it every time wastes their time.

**How to apply:** merge as soon as the documents are written, even if a test tally in the report
is still pending, and **merge again** whenever any of those documents change - after the suite
fills the tally in, after an erratum, after a regenerated results file - so the merged file
always matches what is on disk. See [[unity-filtered-test-runs]] for why a full run is slow
enough that this second merge comes up so often.
```

`unity-filtered-test-runs.md`

```
---
name: unity-filtered-test-runs
description: How to run one Fallow test fixture through the Unity CLI in about a minute instead of the two-hour full suite
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e238e8a-fdd0-432f-853a-aa488b30ce9d
  modified: 2026-09-16T01:25:31.967Z
---

`unity test <project> --editor-version 6000.3.24f1 --mode EditMode --filter <FixtureName> --output <scratch>/x.xml --no-banner --non-interactive --timeout 1800` runs one fixture. `--filter` is a regex on the full name, so `"Fixture.TestA|Fixture.TestB"` runs just those tests. A filtered run rewrites the doc its fixture generates with only the tests that ran; restore it with `git checkout --` or run the whole fixture. Editor startup is about 45 s; a fixture of 50 mornings adds about 30 s. Only one Unity process can hold the project at a time, so chain runs sequentially. Write results outside the repo: `run-tests.sh` owns `test-results.xml`, which is tracked in git and regenerated by the full suite.

**Why:** the full suite (`./run-tests.sh`) took about 67 minutes on 2026-09-19 (377 tests). By 2026-09-24 it is about 186 minutes (456 tests; the causal-route fixture alone is 32 min, route-applicability 28, reason-semantics 20, intention-representation about 15, decision-sensitivity 18), so iterating on one new fixture through it wastes most of a session. `run-tests.sh` hard-codes `--timeout 7200`, which the suite now exceeds: it dies with TEST_TIMED_OUT and "NO RESULTS FILE", which is not a compile error. Run a scratchpad copy with the timeout raised (`sed 's/--timeout 7200/--timeout 14400/' run-tests.sh > <scratch>/run-tests-long.sh`) unless the user has raised it in the repo. Launch it with Bash `run_in_background`.

**How to apply:** use a filtered run for every compile check and every new S1.x fixture; run the full suite once at the end of a slice to confirm the regenerated docs are byte-identical where they should be. See [[slice-docs-merged-file]] for the end-of-slice doc merge.
```

Fact check against the repository: the memory says `test-results.xml` "is tracked in git". It is not:
`git check-ignore -v test-results.xml` prints `.gitignore:50:/test-results.xml`, and it is absent from `git ls-files`.

### Project-rule text in `README.md` ("The rules that keep it honest", lines 134–153)

Five rules, stated as enforced by tests: nothing may name a member of the cast; a rule condition may
ask about circumstances only (anything about a person enters as a weight); nothing reads world truth
except the world (decisions use a `Percept`); randomness settles ties and nothing else; every want
has more than one way to be served (the validator rejects a single-action want).

### Other instruction files

`AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.github/copilot-instructions.md`, `CONTRIBUTING*`,
a project `.claude/` folder: NOT FOUND. `Assets/Readme.asset` and `Assets/TutorialInfo/` are the
Unity template's tutorial readme, not project instructions.

---

## 3. Languages, runtimes, versions

| Item | Version / value | Source |
|---|---|---|
| Unity Editor | `6000.3.24f1` (revision `4e7b9b5b6244`) | `ProjectSettings/ProjectVersion.txt` |
| Unity Editor installed | `/c/Program Files/Unity/Hub/Editor/6000.3.24f1` | directory listing |
| Unity CLI | `unity.exe` `1.0.0-beta.9` at `/c/Users/Akrem/AppData/Local/Unity/bin` | `unity --version`; path from `run-tests.sh:4` |
| Render pipeline | URP `com.unity.render-pipelines.universal` `17.3.0` | `Packages/manifest.json` |
| Test framework | `com.unity.test-framework` `1.6.0`; NUnit engine `3.5.0.0` in results | `Packages/manifest.json`; `test-results.xml` |
| JSON library | `com.unity.nuget.newtonsoft-json` `3.2.1` | `Packages/manifest.json` |
| C# API compatibility (Unity) | `apiCompatibilityLevel: 6` | `ProjectSettings/ProjectSettings.asset` |
| C# for the narrator | `-langversion:9.0`, runtimeconfig `tfm: net6.0` | `narrate.sh` |
| .NET runtime used by the narrator | Unity's bundled `NetCoreRuntime`, `Microsoft.NETCore.App 6.0.21`; compiler `Editor/Data/DotNetSdkRoslyn/csc.dll` | directory listing; `narrate.sh` |
| System .NET SDK (`dotnet` on PATH) | NOT FOUND | `dotnet --version` → command not found |
| Python | `3.12.10` (on PATH, and the prototype venv) | `python --version`; `Prototypes/llm-morning/.venv/pyvenv.cfg` |
| Python dependency | `google-genai==2.25.0` | `Prototypes/llm-morning/requirements.txt` |
| LLM models configured | `gemini-3.5-flash-lite` (default), `gemma-4-31b-it` (key `gemma`); key read from `GEMINI_API_KEY` | `Prototypes/llm-morning/config.json`; `morning.py` docstring |
| Shell scripts | bash (`#!/usr/bin/env bash`), run under Git Bash | `run-tests.sh`, `narrate.sh` |
| Other packages in manifest | ai.navigation 2.0.14, collab-proxy 2.13.6, ide.rider 3.0.40, ide.visualstudio 2.0.26, inputsystem 1.20.0, multiplayer.center 1.0.1, timeline 1.8.13, ugui 2.0.0, visualscripting 1.9.12, plus built-in modules | `Packages/manifest.json` |

Code by language (source files, excluding skipped folders): C# 122 in `Assets/` (55 Core, 65 tests,
2 Unity template) + 3 in `Tools/narrate-morning/`; Python 14 at the prototype root + 33 in `v1/`–`v4/`
+ 2 in `Docs/experiments/*/prediction-model.py` + `merge-slice-docs.py`; bash 2.

---

## 4. How to run each part (exact commands, with source)

| Part | Command | Source |
|---|---|---|
| Full Unity EditMode suite | `./run-tests.sh` | `README.md:117` |
| (what it runs) | `unity test "$PROJ" --editor-version 6000.3.24f1 --mode EditMode --format json --no-banner --non-interactive --timeout 7200 >"$LOG" 2>&1` | `run-tests.sh:12-13` |
| One Unity fixture | `` `unity test . --mode EditMode --filter <FixtureName>` `` | `README.md:125` |
| Merge a slice's docs | `python merge-slice-docs.py S1.5` | `README.md:129` |
| Merge a folder's docs | `python merge-slice-docs.py Docs/experiments/decision-sensitivity` | `merge-slice-docs.py:4` (docstring) |
| Narrate one morning (C#, no Unity process) | `./narrate.sh <variant> <seed>` (example `./narrate.sh daniel_ate_it 1`) | `narrate.sh:4`; `Docs/understanding/narrator-setup.md:10` |
| Narrator's test | `./narrate.sh --test` | `narrate.sh:5`; `Docs/understanding/narrator-setup.md:14` |
| Prototype setup | `python -m venv .venv` then `.venv/Scripts/python -m pip install -r requirements.txt` | `Prototypes/llm-morning/REPORT.md:77-78` |
| Prototype: fresh morning (calls Gemini) | `python morning.py --seed 1` | `Prototypes/llm-morning/morning.py` docstring |
| Prototype: replay from cache, no API | `python morning.py --seed 1 --replay` | same |
| Prototype: fake model | `python morning.py --seed 1 --fake` | same |
| Prototype options | `--scenario NAME` (`daniel_ate_it`, `mara_ate_it`, `miscount`), `--model KEY`, `--out DIR` | same |
| Prototype tests | `python -m unittest -v test_morning` | `Prototypes/llm-morning/test_morning.py` docstring; `REPORT-5.md:252` |
| Prototype: list models | `python list_models.py [filter]` | `list_models.py` docstring |
| Prototype: probe a model | `python probe_model.py gemma-4-31b-it [--no-schema] [--no-system]` | `probe_model.py` docstring |
| Prototype: probe a prompt | `python probe_prompt.py <cache file> <scenario> <run seed> <model> <probe seed>` | `probe_prompt.py` docstring |
| Prototype metrics | `python metrics.py`, `python metrics3.py`, `python metrics4.py`, `python metrics5.py` | each file's docstring |
| Prototype: rebuild v1 transcripts | `python v1/transcript.py` | `v1/transcript.py` docstring |
| Prototype: replay-check v2, v3, v4 | `python v2/check.py`, `python v3/check.py`, `python v4/check.py` | each `check.py` docstring |
| Experiment prediction models | `python prediction-model.py` and `python prediction-model.py frozen` | `Docs/experiments/reason-semantics/prediction-model.py:15-16`; `Docs/experiments/route-applicability/prediction-model.py` docstring |
| Run the game / enter Play mode | NOT FOUND | no gameplay scene; `Assets/Scenes/SampleScene.unity` is the template scene; `README.md:14` says "No dialogue, no player, no 3D." |
| Build a player | NOT FOUND | no build script, no `Build/` or `Builds/` |
| Open in the Unity Editor | NOT FOUND as a written command | |

Run-time facts recorded in the repo: `README.md:120` says the suite "Takes about an hour";
`test-results.xml` records `duration="11094.8859012"` (3 h 4 min 55 s) for the 2026-09-24 run;
`run-tests.sh` sets `--timeout 7200`.

---

## 5. Test suites (counted, not run)

| Suite | Location | Framework | Count |
|---|---|---|---:|
| Unity EditMode | `Assets/_Project/Tests/EditMode/` (asmdef `Fallow.Tests.Core`, Editor only, `UNITY_INCLUDE_TESTS`) | NUnit via Unity Test Framework 1.6.0 | **456** `[Test]` methods in 58 files (68 classes); 0 `[TestCase]`, 0 `[TestCaseSource]`, 0 `[UnityTest]`, 0 parameterised (`[Values]` etc.) |
| Unity PlayMode | NOT FOUND | | 0 |
| Python prototype | `Prototypes/llm-morning/test_morning.py` | `unittest` | **49** `test_` methods in 5 `unittest.TestCase` classes (`FakeMorningTest`, `SequentialTalkTest`, `PressureTest`, `ScenarioTest`, `GeminiClientTest`) |
| Narrator | `Tools/narrate-morning/NarratorTest.cs` (untracked) | hand-written, run by `./narrate.sh --test` | **1** |
| Prototype replay checks | `Prototypes/llm-morning/v2/check.py`, `v3/check.py`, `v4/check.py` | scripts comparing replayed output byte for byte | 3 scripts (not test frameworks) |

The 7 `.cs` files in `Tests/EditMode/` without tests are helpers: `Baselines.cs`, `IntentionSelector.cs`,
`S15Measures.cs`, `S16Measures.cs`, `S17Measures.cs`, `SensitivityMeasures.cs`, `TestPaths.cs`.

EditMode `[Test]` count per source file:

| File | Tests | File | Tests | File | Tests |
|---|---:|---|---:|---|---:|
| AccumulatedHistoryExperimentTests | 3 | S11BeliefCarrierTests | 5 | S15DispositionTests | 7 |
| ActionRepresentationAuditTests | 7 | S11CausalExamplesTests | 3 | S15ExperimentTests | 8 |
| AuditCensusTests | 1 | S11DiagnosisTests | 2 | S15HeldOutTests | 9 |
| BaselineTests | 6 | S11ExperimentTests | 11 | S15PacingTests | 1 |
| CausalRouteExperimentTests | 7 | S11HeldOutTests | 7 | S16DiagnosisTests | 5 |
| DecidingTests | 14 | S11LocalityTests | 2 | S16ExperimentTests | 8 |
| DeliberationTests | 11 | S11UrgencyTests | 5 | S16HeldOutTests | 10 |
| EmergentMomentTest | 1 | S12AggregationTests | 6 | S16MeansTests | 10 |
| EpisodeExperimentTests | 3 | S12CommitmentTests | 10 | S17DiagnosisTests | 4 |
| IntentCarryingExperimentTests | 4 | S12DiagnosisTests | 3 | S17ExperimentTests | 8 |
| IntentionFormationExperimentTests | 7 | S12ExperimentTests | 10 | S1ExperimentTests | 12 |
| IntentionGeneralizationExperimentTests | 6 | S13DiagnosisTests | 7 | S1HeldOutTests | 6 |
| IntentionRankingExperimentTests | 10 | S13ExperimentTests | 12 | SameActExperimentTests | 7 |
| IntentionRepresentationExperimentTests | 8 | S13LifecycleTests | 4 | Scenario001Tests | 21 |
| InterpreterTests | 27 | S14AttributionTests | 1 | SensitivityExperimentTests | 8 |
| MindStateTests | 24 | S14DiagnosisTests | 5 | SimulationTests | 12 |
| MorningTests | 18 | S14ExperimentTests | 8 | SmokeTests | 1 |
| ProfileTests | 12 | S14HeldOutTests | 6 | WorldEventTests | 9 |
| ReasonSemanticsExperimentTests | 9 | S15DiagnosisTests | 2 | WorldTests | 15 |
| RouteApplicabilityExperimentTests | 8 | | | **Total** | **456** |

Last recorded results (read from existing files, not produced by this inspection):

- `test-results.xml`: 2026-09-24 01:56:49Z to 05:01:43Z, `total="456" passed="454" failed="2"`.
  Failed: `Fallow.Tests.Core.EmergentMomentTest.BeingWatchedByYourSonMakesYouWantToLeaveTheRoom`
  and `Fallow.Tests.Core.S1ExperimentTests.SomebodyStillPacesBetweenTwoRoomsAndThisIsHowBadly`
  (`README.md:122-124` describes two known failures since S1.4: the pacing gate and one check in
  the emergent-moment test).
- `Logs/unity-test-run.log`: `"success": false`, `"code": "TESTS_FAILED"`, `"Unity process exited with code 2."`

---

## 6. Git

- Current branch: `main`. Only local branch; remote branch `origin/main`.
- Remote: `origin https://github.com/akremzarrouk/Fallow-Still-Human.git`.
- `main` is ahead of `origin/main` by 35 commits. 63 commits in total. No stashes.
- HEAD: `8b183d4478c7a66ed4b2984ea6e6040a8aabb315`, 2026-09-26 00:31:43 +0100.
- Tracked files by top-level entry: `Assets` 325, `Docs` 190, `Prototypes` 215, `ProjectSettings` 24,
  `Packages` 2, and `.gitattributes`, `.gitignore`, `README.md`, `merge-slice-docs.py`, `run-tests.sh`.

Last 20 commits and working-tree status: see appendix commands A13 and A14.

Uncommitted changes: no modified or staged tracked files. Untracked: `CLAUDE.md`, `CONTEXT_REPORT.md`,
`Docs/understanding/commit-log.md`, `Prototypes/llm-morning/reports/`, `Tools/`, `narrate.sh`
(and now `reports/`, this deliverable).

---

## 7. NOT FOUND list

1. `AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.github/copilot-instructions.md`, `CONTRIBUTING*`.
2. A project-level `.claude/` folder in the repository.
3. CI configuration (`.github/`, any `*.yml`/`*.yaml` within two levels of the root).
4. A README inside `Prototypes/llm-morning/` or `Tools/narrate-morning/` (their docs are `REPORT*.md` and `Docs/understanding/narrator-setup.md`).
5. `.sln` / `.csproj` files (ignored by `.gitignore`; none present), `global.json`, `.editorconfig`.
6. `pyproject.toml`, `setup.cfg`, `pytest.ini`, `tox.ini`, `Makefile`.
7. A system .NET SDK on PATH (`dotnet: command not found`).
8. A command to run the game or enter Play mode.
9. A command or script to build a player; `Build/` and `Builds/` folders.
10. Unity PlayMode tests.
11. `[TestCase]`, `[TestCaseSource]`, `[UnityTest]` or parameterised tests in the EditMode suite.
12. `Temp/`, `obj/`, `node_modules/` at the top level.
13. `Secrets/` (ignored by `.gitignore:46`; the comment on line 45 says "not used until slice S7").
14. An "Open in the Unity Editor" instruction written in the repository.

---

## Appendix: commands run and their output

All in Git Bash at the repository root unless a `cd` is shown. Long outputs are cut where marked `[…]`;
nothing inside a quoted output was changed.

**A1. Instruction files and top level**

```
$ cat CLAUDE.md
Never stop processes by name or broad filters; only by the exact process ID you started.

$ ls -la
drwxr-xr-x .git
-rw-r--r--     97 .gitattributes
-rw-r--r--    690 .gitignore
drwxr-xr-x Assets
-rw-r--r--     89 CLAUDE.md
-rw-r--r--  50886 CONTEXT_REPORT.md
drwxr-xr-x Docs
drwxr-xr-x Library
drwxr-xr-x Logs
drwxr-xr-x Packages
drwxr-xr-x ProjectSettings
drwxr-xr-x Prototypes
-rw-r--r--  12555 README.md
drwxr-xr-x Tools
drwxr-xr-x UserSettings
-rwxr-xr-x   3628 merge-slice-docs.py
-rwxr-xr-x   4887 narrate.sh
-rwxr-xr-x   1717 run-tests.sh
-rw-r--r-- 1189924 test-results.xml
[owner, date columns cut]

$ find . <skipped dirs pruned> -type f \( -iname 'README*' -o -iname 'CLAUDE.md' -o -iname 'AGENTS.md' \
    -o -iname 'GEMINI.md' -o -iname '.cursorrules' -o -iname 'copilot-instructions.md' -o -iname 'CONTRIBUTING*' \) -print
./Assets/Readme.asset
./Assets/Readme.asset.meta
./Assets/TutorialInfo/Scripts/Editor/ReadmeEditor.cs
./Assets/TutorialInfo/Scripts/Editor/ReadmeEditor.cs.meta
./Assets/TutorialInfo/Scripts/Readme.cs
./Assets/TutorialInfo/Scripts/Readme.cs.meta
./CLAUDE.md
./README.md
```

Also read in full: `README.md`, `run-tests.sh`, `narrate.sh`, `merge-slice-docs.py`, `.gitignore`, `.gitattributes`.

**A2. File counts per top-level folder**

```
$ for d in */ .git; do total=$(find "$d" -type f | wc -l); filt=$(find "$d" \( <skipped names> \) -prune -o -type f -print | wc -l); echo "$d total=$total excluding_skipped=$filt"; done
Assets total=325 excluding_skipped=325
Docs total=191 excluding_skipped=190
Library total=30978 excluding_skipped=0
Logs total=7 excluding_skipped=7
Packages total=2 excluding_skipped=2
ProjectSettings total=24 excluding_skipped=24
Prototypes total=3927 excluding_skipped=56
Tools total=10 excluding_skipped=4
UserSettings total=2 excluding_skipped=2
.git total=567 excluding_skipped=567
```

**A3. Directory tree with direct file counts (skipped dirs pruned)**

```
8 Assets
2 Assets/Scenes
14 Assets/Settings
4 Assets/TutorialInfo
2 Assets/TutorialInfo/Icons
3 Assets/TutorialInfo/Scripts
2 Assets/TutorialInfo/Scripts/Editor
3 Assets/_Project
5 Assets/_Project/Data
10 Assets/_Project/Data/Experiments
8 Assets/_Project/Data/Minds
6 Assets/_Project/Data/Rules
4 Assets/_Project/Data/Scenario
2 Assets/_Project/Data/Tests
1 Assets/_Project/Scripts
8 Assets/_Project/Scripts/Core
20 Assets/_Project/Scripts/Core/Data
42 Assets/_Project/Scripts/Core/Model
12 Assets/_Project/Scripts/Core/Rules
26 Assets/_Project/Scripts/Core/Sim
8 Assets/_Project/Scripts/Core/Testing
2 Assets/_Project/Scripts/Core/Tracing
1 Assets/_Project/Tests
132 Assets/_Project/Tests/EditMode
0 Docs
2 Docs/audit
[Docs/experiments/* and Docs/slices/* as tabulated in section 1]
5 Docs/understanding
7 Logs
2 Packages
24 ProjectSettings
0 Prototypes
22 Prototypes/llm-morning
1 Prototypes/llm-morning/reports
6 Prototypes/llm-morning/v1
8 Prototypes/llm-morning/v2
9 Prototypes/llm-morning/v3
10 Prototypes/llm-morning/v4
0 Tools
4 Tools/narrate-morning
2 UserSettings
```
(Counts include `.meta` files. The `reports` count of 1 predates `knowledge_audit.md`, see A9.)

**A4. Unity version, packages, asmdefs**

```
$ cat ProjectSettings/ProjectVersion.txt
m_EditorVersion: 6000.3.24f1
m_EditorVersionWithRevision: 6000.3.24f1 (4e7b9b5b6244)

$ cat Packages/manifest.json
{ "dependencies": {
    "com.unity.nuget.newtonsoft-json": "3.2.1",
    "com.unity.ai.navigation": "2.0.14",
    "com.unity.collab-proxy": "2.13.6",
    "com.unity.ide.rider": "3.0.40",
    "com.unity.ide.visualstudio": "2.0.26",
    "com.unity.inputsystem": "1.20.0",
    "com.unity.multiplayer.center": "1.0.1",
    "com.unity.render-pipelines.universal": "17.3.0",
    "com.unity.test-framework": "1.6.0",
    "com.unity.timeline": "1.8.13",
    "com.unity.ugui": "2.0.0",
    "com.unity.visualscripting": "1.9.12",
    [35 com.unity.modules.* entries, all 1.0.0, cut]
} }

$ cat Assets/_Project/Scripts/Core/Fallow.Core.asmdef
{ "name": "Fallow.Core", "rootNamespace": "Fallow.Core", "references": [],
  "overrideReferences": true, "precompiledReferences": [ "Newtonsoft.Json.dll" ],
  "autoReferenced": true, "noEngineReferences": true, [empty arrays and false flags cut] }

$ cat Assets/_Project/Tests/EditMode/Fallow.Tests.Core.asmdef
{ "name": "Fallow.Tests.Core", "rootNamespace": "Fallow.Tests.Core",
  "references": [ "Fallow.Core", "UnityEngine.TestRunner", "UnityEditor.TestRunner" ],
  "includePlatforms": [ "Editor" ], "overrideReferences": true,
  "precompiledReferences": [ "nunit.framework.dll", "Newtonsoft.Json.dll" ],
  "autoReferenced": false, "defineConstraints": [ "UNITY_INCLUDE_TESTS" ],
  "noEngineReferences": false, [empty arrays and false flags cut] }

$ grep -h "apiCompatibilityLevel\|scriptingBackend" ProjectSettings/ProjectSettings.asset
  scriptingBackend:
  apiCompatibilityLevelPerPlatform: {}
  apiCompatibilityLevel: 6
```

**A5. EditMode test counts**

```
$ cd Assets/_Project/Tests/EditMode
$ ls *.cs | wc -l
65
$ grep -cE '^\s*\[(Test|UnityTest|Theory)\b|\[Test[,\]]|\bTestCase\(' *.cs | awk -F: '{s+=$2} END{print s}'
456
$ for f in *.cs; do ... count [Test], TestCase(, TestCaseSource, [UnityTest, [TestFixture ...; done
[per-file counts as tabulated in section 5; testcase=0 tcsource=0 unitytest=0 fixture=0 for every file]
$ grep -lE '\[(Values|Range|ValueSource|Random|Combinatorial|Sequential)' *.cs
(no output)
$ python (count every `Test` attribute occurrence, including inline forms, per file)
total 456
```

**A6. Existing results files (read, not produced)**

```
$ grep -oE '<test-run [^>]*>' test-results.xml
<test-run id="2" testcasecount="456" result="Failed(Child)" total="456" passed="454" failed="2" inconclusive="0" skipped="0" asserts="0" engine-version="3.5.0.0" clr-version="4.0.30319.42000" start-time="2026-09-24 01:56:49Z" end-time="2026-09-24 05:01:43Z" duration="11094.8859012">
$ grep -c '<test-case ' test-results.xml
456
-- Logs/test-results-filter.xml
<test-run id="2" testcasecount="1" result="Passed" total="1" passed="1" failed="0" [...] start-time="2026-09-15 03:46:15Z" end-time="2026-09-15 03:46:38Z" duration="23.1804611">
-- Logs/test-results-long.xml
<test-run id="2" testcasecount="17" result="Passed" total="17" passed="17" failed="0" [...] start-time="2026-09-15 03:35:14Z" end-time="2026-09-15 03:43:46Z" duration="511.5828461">

$ cat Logs/unity-test-run.log
{ "success": false, "command": "test", "data": null,
  "errors": [ { "code": "TESTS_FAILED", "message": "Tests failed: Unity process exited with code 2." } ],
  "warnings": [] }

$ python (tally test-case elements in test-results.xml by classname)
NOT PASSED: Fallow.Tests.Core.EmergentMomentTest.BeingWatchedByYourSonMakesYouWantToLeaveTheRoom
NOT PASSED: Fallow.Tests.Core.S1ExperimentTests.SomebodyStillPacesBetweenTwoRoomsAndThisIsHowBadly
[68 per-class lines cut]
fixtures 68 cases 456
```

**A7. Python prototype**

```
$ cd Prototypes/llm-morning
$ cat requirements.txt
# Official Google Gen AI Python SDK (import: from google import genai).
# Not the older google-generativeai package, which it replaces.
google-genai==2.25.0
$ cat config.json
{ "model": "gemini-3.5-flash-lite", "temperature": 1.0, "min_seconds_between_calls": 4.5,
  "max_calls_per_morning": 150, "max_retries": 6, "backoff_base_seconds": 5,
  "backoff_max_seconds": 120, "max_output_tokens": 2048,
  "models": { "gemma": { "model": "gemma-4-31b-it", "min_seconds_between_calls": 6.5 } } }
$ cat .venv/pyvenv.cfg
home = C:\Users\Akrem\AppData\Local\Programs\Python\Python312
include-system-site-packages = false
version = 3.12.10
[...]
$ python --version
Python 3.12.10
$ head -25 morning.py
"""Runs a morning with rules plus a language model, and writes it as a story.
    python morning.py --seed 1              a fresh morning; answers not in the cache are asked of Gemini
    python morning.py --seed 1 --replay     the same morning from the cache only, with no API calls;
                                            writes runs/<out>/<name>.replay.md and compares it with
                                            runs/<out>/<name>.md
    python morning.py --seed 1 --fake       the same, against the fake model (for building and testing)
    --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
    --model KEY       another model from config.json `models` (default: config.json `model`)
    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v5; v4 replays
                      the fourth version's runs)
The model names and call limits are in config.json. The key is read from GEMINI_API_KEY.
Exit codes: 0 done (and, for --replay, identical); 1 replay differs; 3 stopped cleanly part way
(quota, rate limit, call cap, or a replay cache miss): see the message.
"""
$ head test_morning.py
"""Tests against the fake model and a stubbed API. No network, no quota.
    python -m unittest -v test_morning
"""
$ grep -cE '^\s+def test_' test_morning.py
49
$ grep -E '^class \w+\(unittest.TestCase\)' test_morning.py
class FakeMorningTest(unittest.TestCase):
class SequentialTalkTest(unittest.TestCase):
class PressureTest(unittest.TestCase):
class ScenarioTest(unittest.TestCase):
class GeminiClientTest(unittest.TestCase):
$ ls v*/test_*
(none)
$ find runs -type f | wc -l ; find cache -type f | wc -l
132
28
$ grep -m2 -E '^\s+python ' v2/check.py v3/check.py ; head v4/check.py
    python v2/check.py
    python v3/check.py
    python v4/check.py
$ grep -rnE 'pip install|-m venv' --include='*.md' --include='*.py' . (excluding .venv, runs, cache)
REPORT.md:77:python -m venv .venv
REPORT.md:78:.venv/Scripts/python -m pip install -r requirements.txt
```
The other docstrings quoted in section 4 were read with `head -25` on each `.py` file.

**A8. Narrator tool**

```
$ cat Tools/narrate-morning/.gitignore
bin/
$ head -40 Tools/narrate-morning/Program.cs
    /// narrate <repo root> <variant> <seed>: writes Docs/understanding/runs/<variant>-<seed>.md.
    /// test <repo root>: runs the narrator's one test.
    /// Started by narrate.sh at the repository root, which builds this first.
[...]
$ head -20 Tools/narrate-morning/NarratorTest.cs
    /// The narrator's one test, run by `./narrate.sh --test`. It lives beside the
    /// tool rather than in the Unity suite because Unity compiles nothing outside
    /// Assets, so a Unity test could not reach this code.
[...]
$ ls Tools/narrate-morning/bin | wc -l
6
$ ls Docs/understanding/runs
daniel_ate_it-1.md
```

**A9. Docs, reports, file types**

```
$ find Docs -type f | sed 's/.*\.//' | sort | uniq -c
      1 csv
     25 json
    160 md
      2 py
      3 txt
$ find Docs -type f \( -name '*.py' -o -name '*.txt' -o -name '*.csv' \)
Docs/experiments/reason-semantics/prediction-model.py
Docs/experiments/route-applicability/prediction-model.py
Docs/slices/S0/traces/full-trace.txt
Docs/slices/S1/batch/decisions.csv
Docs/slices/S1/traces/a-mother-made-to-feel-like-a-suspect.txt
Docs/slices/S1/traces/full-trace-daniel_ate_it-seed1.txt
$ ls -la Prototypes/llm-morning/reports
-rw-r--r-- 41045 Sep 26 01:57 knowledge_audit.md
-rw-r--r-- 24233 Sep 26 00:47 llm_call_audit.md
$ grep -m1 '^#' <each report>
CONTEXT_REPORT.md: # Fallow: context report for a reviewer
Docs/audit/census.md: # Audit census: what actually fires on the shipped rules
Docs/audit/system-understanding-audit.md: # Fallow: system understanding audit
Docs/understanding/commit-log.md: # Commit log: LLM morning prototype, steps 1 to 5
Docs/understanding/morning-walkthrough.md: # One morning in the house, told plainly
Docs/understanding/narrator-setup.md: # The morning narrator: setup
Docs/understanding/target-morning.md: # Target morning: what a believable run looks like
Docs/understanding/understanding-all.md: # understanding: all documents
Prototypes/llm-morning/REPORT.md: # LLM morning prototype: report
Prototypes/llm-morning/REPORT-2.md: # LLM morning prototype, step 2: sequential conversation
Prototypes/llm-morning/REPORT-3.md: # LLM morning prototype, step 3: inner pressure and lasting grudges
Prototypes/llm-morning/REPORT-4.md: # LLM morning prototype, step 4: guilt and grudges from events
Prototypes/llm-morning/REPORT-5.md: # LLM morning prototype, step 5: other scenarios, another model
Prototypes/llm-morning/reports/knowledge_audit.md: # Knowledge audit: what each person knows, believes and has been told
Prototypes/llm-morning/reports/llm_call_audit.md: # LLM call audit: where the Gemini requests go
```

**A10. Assets composition**

```
$ echo "meta $(find Assets -name '*.meta' | wc -l), non-meta $(find Assets -type f -not -name '*.meta' | wc -l), .cs $(find Assets -name '*.cs' | wc -l), .json $(find Assets -name '*.json' | wc -l)"
meta 174, non-meta 151, .cs 122, .json 15
```
Per-folder `.cs` listings as in section 1 (`Data` 10, `Model` 21, `Rules` 6, `Sim` 13, `Testing` 4, `Tracing` 1, `TutorialInfo/Scripts` 1 + `Editor` 1).

**A11. Tool versions and locations**

```
$ dotnet --version
/usr/bin/bash: line 1: dotnet: command not found
$ ls /c/Users/Akrem/AppData/Local/Unity/bin
unity.exe
$ /c/Users/Akrem/AppData/Local/Unity/bin/unity --version
1.0.0-beta.9
$ ls "/c/Program Files/Unity/Hub/Editor/"
6000.3.24f1
$ ls ".../6000.3.24f1/Editor/Data/NetCoreRuntime/shared/Microsoft.NETCore.App/"
6.0.21
$ ls ".../6000.3.24f1/Editor/Data/DotNetSdkRoslyn/csc.dll"
/c/Program Files/Unity/Hub/Editor/6000.3.24f1/Editor/Data/DotNetSdkRoslyn/csc.dll
$ ls -a .github ; find . -maxdepth 2 \( -name '*.yml' -o -name '*.yaml' -o -name Makefile -o -name pyproject.toml \
    -o -name setup.cfg -o -name pytest.ini -o -name tox.ini -o -name '*.sln' -o -name '*.csproj' \
    -o -name global.json -o -name .editorconfig -o -name .claude \) -not -path './Library/*'
ls: cannot access '.github': No such file or directory
(no output from find)
$ ls -a .claude
ls: cannot access '.claude': No such file or directory
```

**A12. Run commands quoted in docs**

```
$ grep -rnE '(\./run-tests\.sh|\./narrate\.sh|unity test|python (-m )?[a-zA-Z_./-]+\.py|python -m unittest)' README.md CONTEXT_REPORT.md Docs/understanding/narrator-setup.md Docs/understanding/target-morning.md Prototypes/llm-morning/REPORT-5.md
README.md:117:    ./run-tests.sh
README.md:125:`unity test . --mode EditMode --filter <FixtureName>` in about a minute.
README.md:129:    python merge-slice-docs.py S1.5
CONTEXT_REPORT.md:813:EditMode, run by `run-tests.sh` via the Unity CLI (`unity test ... --mode
Docs/understanding/narrator-setup.md:10:./narrate.sh daniel_ate_it 1
Docs/understanding/narrator-setup.md:14:./narrate.sh --test
Prototypes/llm-morning/REPORT-5.md:205:python list_models.py gemma
Prototypes/llm-morning/REPORT-5.md:206:python probe_model.py gemma-4-31b-it
Prototypes/llm-morning/REPORT-5.md:252:python -m unittest -v test_morning
Prototypes/llm-morning/REPORT-5.md:319:for s in 1 2 3 4 5; do env -u GEMINI_API_KEY python morning.py --seed $s --replay --out v4; done
Prototypes/llm-morning/REPORT-5.md:343:python morning.py --model gemma --seed 1
Prototypes/llm-morning/REPORT-5.md:686:python morning.py --scenario mara_ate_it --seed 1
Prototypes/llm-morning/REPORT-5.md:803:python morning.py --scenario miscount --seed 1
[further repeats of these forms with other seeds cut]
```

**A13. Git: branch and last 20 commits**

```
$ git branch --show-current
main
$ git log --oneline -20
8b183d4 LLM morning prototype, steps 1 to 5
8cdf644 docs: full-suite result for the route-applicability experiment
b344056 feat: route applicability is one layer, one construct, and needs a target
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
$ git rev-list --count HEAD
63
$ git remote -v
origin	https://github.com/akremzarrouk/Fallow-Still-Human.git (fetch)
origin	https://github.com/akremzarrouk/Fallow-Still-Human.git (push)
$ git branch -a
* main
  remotes/origin/main
$ git stash list
(no output)
$ git log -1 --format='%H %ad' --date=iso
8b183d4478c7a66ed4b2984ea6e6040a8aabb315 2026-09-26 00:31:43 +0100
```

**A14. Git: status, tracked and ignored files**

```
$ git status
On branch main
Your branch is ahead of 'origin/main' by 35 commits.
  (use "git push" to publish your local commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	CLAUDE.md
	CONTEXT_REPORT.md
	Docs/understanding/commit-log.md
	Prototypes/llm-morning/reports/
	Tools/
	narrate.sh

nothing added to commit but untracked files present (use "git add" to track)

$ git ls-files | cut -d/ -f1 | sort | uniq -c
      1 .gitattributes
      1 .gitignore
    325 Assets
    190 Docs
      2 Packages
     24 ProjectSettings
    215 Prototypes
      1 README.md
      1 merge-slice-docs.py
      1 run-tests.sh

$ git ls-files Prototypes/llm-morning | cut -d/ -f3 | sort | uniq -c   (entries with more than one file)
     28 cache
    132 runs
      6 v1
      8 v2
      9 v3
     10 v4

$ git check-ignore -v test-results.xml Logs UserSettings Library Tools/narrate-morning/bin Prototypes/llm-morning/.venv
.gitignore:50:/test-results.xml	test-results.xml
.gitignore:7:/[Ll]ogs/	Logs
.gitignore:8:/[Uu]ser[Ss]ettings/	UserSettings
.gitignore:2:/[Ll]ibrary/	Library
Tools/narrate-morning/.gitignore:1:bin/	Tools/narrate-morning/bin
Prototypes/llm-morning/.gitignore:1:.venv/	Prototypes/llm-morning/.venv
```
(The `git status` above was taken before this file was written, so `reports/` is not in it.)

**A15. Auto-memory (outside the repository)**

```
$ cd /c/Users/Akrem/.claude/projects/C--Users-Akrem-Desktop-Projects-Fallow/memory && for f in *.md; do cat "$f"; done
[full text reproduced in section 2]
$ ls -a /c/Users/Akrem/Desktop/Projects/Fallow/.claude
ls: cannot access '/c/Users/Akrem/Desktop/Projects/Fallow/.claude': No such file or directory
```
