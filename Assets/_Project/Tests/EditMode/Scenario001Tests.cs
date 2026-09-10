using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Data;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using Newtonsoft.Json.Linq;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The slice S0 experiment itself: run the real cast through the real
    /// script under the real rules, and compare what each person made of each
    /// event against what the designer said they should.
    ///
    /// The expectation table was written and committed before any rule existed.
    /// The percentages are diagnostic, not truth: a miss is a prompt to read the
    /// trace and decide who was wrong, the rules or the expectation.
    /// </summary>
    public class Scenario001Tests
    {
        class Cell
        {
            public string Event;
            public string Character;
            public string Meaning;
            public string Emotion;
            public string Rationale;
        }

        static Vocabulary _vocab;
        static IReadOnlyDictionary<string, Profile> _cast;
        static ScenarioScript _script;
        static RuleSet _rules;
        static Simulation _sim;
        static IReadOnlyList<EventOutcome> _outcomes;
        static List<Cell> _cells;
        static double _meaningMatch, _emotionMatch, _meaningGate, _emotionGate;
        static List<string> _misses;

        [OneTimeSetUp]
        public void RunTheScenarioOnce()
        {
            _vocab = VocabularyLoader.LoadFile(Path.Combine(TestPaths.Rules, "vocabulary.json"));
            _cast = ProfileLoader.LoadDirectory(TestPaths.Minds);
            _script = ScenarioLoader.LoadFile(Path.Combine(TestPaths.Scenario, "backstory.json"));
            _rules = RuleSetLoader.LoadFile(Path.Combine(TestPaths.Rules, "rules.json"));

            _sim = new Simulation(_cast, _rules);
            _outcomes = _sim.Run(_script);

            JObject json = JObject.Parse(
                File.ReadAllText(Path.Combine(TestPaths.Tests, "expectations.json")));

            _meaningGate = (double)json["gates"]["meaning_match"];
            _emotionGate = (double)json["gates"]["emotion_match"];

            _cells = json["cells"].Select(c => new Cell
            {
                Event = (string)c["event"],
                Character = (string)c["character"],
                Meaning = (string)c["meaning"],
                Emotion = (string)c["dominant_emotion"],
                Rationale = (string)c["rationale"]
            }).ToList();

            var byEvent = _outcomes.ToDictionary(o => o.Event.Id, o => o, StringComparer.Ordinal);
            var meaningHits = 0;
            var emotionHits = 0;
            _misses = new List<string>();

            foreach (var cell in _cells)
            {
                var outcome = byEvent[cell.Event].ByCharacter[cell.Character];
                var meaning = outcome.Meaning ?? "none";
                var emotion = outcome.DominantEmotion ?? "none";

                if (meaning == cell.Meaning) meaningHits++;
                if (emotion == cell.Emotion) emotionHits++;

                if (meaning != cell.Meaning || emotion != cell.Emotion)
                {
                    var runnerUp = outcome.Emotions.Count > 1 ? $", runner-up {outcome.Emotions[1]}" : "";
                    _misses.Add(
                        $"{cell.Event}/{cell.Character}: expected {cell.Meaning}/{cell.Emotion}, " +
                        $"got {meaning}/{emotion} ({outcome.DominantIntensity:0.00}{runnerUp})\n" +
                        $"      designer said: {cell.Rationale}");
                }
            }

            _meaningMatch = (double)meaningHits / _cells.Count;
            _emotionMatch = (double)emotionHits / _cells.Count;

            WriteReports();
        }

        static void WriteReports()
        {
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S0", "traces");
            Directory.CreateDirectory(dir);

            File.WriteAllText(Path.Combine(dir, "event-by-event.md"), S0Report.EventByEvent(_sim, _outcomes));
            File.WriteAllText(Path.Combine(dir, "where-everyone-stands.md"), S0Report.WhereEveryoneStands(_sim));
            File.WriteAllText(Path.Combine(dir, "full-trace.txt"), S0Report.FullTrace(_sim));

            var sb = new StringBuilder();
            sb.AppendLine("# Scenario 001, slice S0: expectation table results");
            sb.AppendLine();
            sb.AppendLine($"Cells: {_cells.Count}");
            sb.AppendLine($"Meaning matched: {_meaningMatch:P1}  (gate {_meaningGate:P0})");
            sb.AppendLine($"Emotion matched: {_emotionMatch:P1}  (gate {_emotionGate:P0})");
            sb.AppendLine();
            sb.AppendLine($"## Misses ({_misses.Count})");
            sb.AppendLine();
            foreach (var m in _misses) sb.AppendLine("- " + m);
            File.WriteAllText(Path.Combine(dir, "expectation-results.md"), sb.ToString());

            // The chains behind the two cells the slice exists to test.
            var chains = new StringBuilder();
            chains.AppendLine("# Why they felt that");
            chains.AppendLine();
            foreach (var pair in new[]
                     {
                         ("daniel", "shame"), ("leo", "frustration"),
                         ("mara", "fear"), ("elena", "anxiety")
                     })
            {
                chains.AppendLine($"## {pair.Item1}, {pair.Item2}");
                chains.AppendLine();
                chains.AppendLine("```");
                chains.AppendLine(S0Report.WhyTheyFeltThat(_sim, pair.Item1, pair.Item2));
                chains.AppendLine("```");
                chains.AppendLine();
            }
            File.WriteAllText(Path.Combine(dir, "why-they-felt-that.md"), chains.ToString());
        }

        // ---- the data is sound before anything is measured ----

        [Test]
        public void EverythingTheSliceLoadsIsValid()
        {
            var problems = new List<string>();
            problems.AddRange(_cast.Values.SelectMany(p => ProfileValidator.Validate(p, _vocab)));
            problems.AddRange(ProfileValidator.ValidateCast(_cast, _vocab));
            problems.AddRange(ScenarioValidator.Validate(_script, _vocab, _cast));
            problems.AddRange(RuleSetValidator.Validate(_rules, _vocab));

            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void TheExpectationTableCoversEveryPersonAtEveryEvent()
        {
            Assert.AreEqual(_script.Events.Count * _cast.Count, _cells.Count);

            foreach (var e in _script.Events)
                Assert.AreEqual(_cast.Count, _cells.Count(c => c.Event == e.Id), $"{e.Id} is not fully covered");
        }

        // ---- the experiment ----

        [Test]
        public void TheSameEventMeansDifferentThingsToDifferentPeople()
        {
            var divided = _outcomes.Count(o =>
                o.ByCharacter.Values
                    .Where(p => p.Access != Access.None)
                    .Select(p => p.Meaning)
                    .Distinct(StringComparer.Ordinal)
                    .Count() > 1);

            Assert.Greater(divided, _outcomes.Count / 2,
                "if most events land the same way on everyone, the model is not doing its job");
        }

        [Test]
        public void ReadingsMatchWhatTheDesignerExpected()
        {
            TestContext.WriteLine(Summary());
            Assert.GreaterOrEqual(_meaningMatch, _meaningGate,
                "readings drifted from the design:\n" + string.Join("\n", _misses));
        }

        [Test]
        public void FeelingsMatchWhatTheDesignerExpected()
        {
            TestContext.WriteLine(Summary());
            Assert.GreaterOrEqual(_emotionMatch, _emotionGate,
                "feelings drifted from the design:\n" + string.Join("\n", _misses));
        }

        [Test]
        public void TheGatesAreNotTriviallyPassable()
        {
            var commonestMeaning = _cells.GroupBy(c => c.Meaning).Max(g => g.Count()) / (double)_cells.Count;
            var commonestEmotion = _cells.GroupBy(c => c.Emotion).Max(g => g.Count()) / (double)_cells.Count;

            Assert.Less(commonestMeaning, _meaningGate,
                "always answering the commonest reading would pass, so the gate proves nothing");
            Assert.Less(commonestEmotion, _emotionGate,
                "always answering the commonest feeling would pass, so the gate proves nothing");
        }

        // ---- knowledge stays local ----

        [Test]
        public void NobodyKnowsAboutAnythingTheyWereNotThereFor()
        {
            foreach (var outcome in _outcomes)
            foreach (var id in _cast.Keys)
            {
                if (outcome.Event.AccessFor(id) != Access.None) continue;

                var mind = _sim.Minds[id];
                Assert.IsFalse(mind.Experiences.Any(x => x.EventId == outcome.Event.Id),
                    $"{id} kept a memory of {outcome.Event.Id}, which they had no access to");
                Assert.IsFalse(mind.Ledger.All.Any(r => r.EventId == outcome.Event.Id),
                    $"{id} holds something against someone over {outcome.Event.Id}, which they had no access to");
            }
        }

        [Test]
        public void EveryBeliefThatMovedCanSayWhatMovedIt()
        {
            foreach (var mind in _sim.Minds.Values)
            foreach (var belief in mind.Beliefs.All)
            {
                var seeded = mind.Profile.InitialBeliefs.Any(s => s.Key == belief.Key);
                if (seeded && belief.Justifications.Count == 0) continue;

                Assert.IsNotEmpty(belief.Justifications,
                    $"{mind.Id} holds {belief.Key} with nothing behind it");

                foreach (var traceId in belief.Justifications)
                {
                    var chain = _sim.Trace.Chain(traceId);
                    CollectionAssert.Contains(chain.Select(r => r.Kind).ToArray(), TraceKind.Event,
                        $"{mind.Id}'s belief {belief.Key} does not lead back to anything that happened");
                }
            }
        }

        [Test]
        public void EveryFeelingLeadsBackToSomethingThatHappened()
        {
            var checkedAny = false;

            foreach (var mind in _sim.Minds.Values)
            foreach (var emotion in mind.Emotions.Live)
            foreach (var cause in emotion.Causes)
            {
                checkedAny = true;
                var chain = _sim.Trace.Chain(cause).ToList();

                Assert.GreaterOrEqual(chain.Count, 3,
                    $"{mind.Id}'s {emotion.Type} explains itself in fewer than three steps");
                CollectionAssert.Contains(chain.Select(r => r.Kind).ToArray(), TraceKind.Interpretation);
                CollectionAssert.Contains(chain.Select(r => r.Kind).ToArray(), TraceKind.Event);
                Assert.IsNotNull(emotion.Concern, $"{mind.Id}'s {emotion.Type} cannot name a concern");
            }

            Assert.IsTrue(checkedAny, "nobody is feeling anything, so this proves nothing");
        }

        // ---- the conflict the slice was built to produce ----

        [Test]
        public void TheOlderBrotherEndsUpHoldingTwoThingsThatDoNotAgree()
        {
            var daniel = _sim.Minds["daniel"];

            var respectsTheJudgement = daniel.Beliefs.Confidence("more_knowledgeable", "leo", "survival");
            var resentsTheManner = daniel.Beliefs.Confidence("tendency", "leo", "does_not_respect_me");

            Assert.Greater(respectsTheJudgement, 0.5, "he has watched his brother be right");
            Assert.Greater(resentsTheManner, 0.4, "and he has felt it every time");

            // Both sides of it are specific things he can name, not a score.
            Assert.Greater(daniel.Ledger.Strength("leo", "proved_right"), 0.0);
            Assert.Greater(daniel.Ledger.Strength("leo", "overruled_me"), 0.0);

            // And neither belief has driven the other out.
            Assert.Greater(Math.Min(respectsTheJudgement, resentsTheManner), 0.4,
                "the point is that he holds both at once, not that one won");
        }

        [Test]
        public void TheOneWhoDidTheProtectingIsAlsoRememberedForIt()
        {
            var mara = _sim.Minds["mara"];

            Assert.Greater(mara.Ledger.Strength("daniel", "protected_me"), 0.5,
                "he carried her inside, and that is not cancelled by the rest");
            Assert.Greater(mara.Ledger.Strength("daniel", "searched_my_things"), 0.5,
                "and he went through her bag, and that is not cancelled either");
        }

        [Test]
        public void TheOneWhoWasNotInTheRoomNeverFindsOut()
        {
            var leo = _sim.Minds["leo"];

            Assert.IsFalse(leo.Experiences.Any(x => x.EventId == "p02"),
                "Leo was not there when the bag was emptied out, and nobody has told him");
            Assert.IsTrue(_sim.Minds["mara"].Experiences.Any(x => x.EventId == "p02"));
            Assert.IsTrue(_sim.Minds["elena"].Experiences.Any(x => x.EventId == "p02"));
        }

        [Test]
        public void WhatWasHeardThroughAWallIsHeldLessSurelyThanWhatWasSeen()
        {
            var leo = _sim.Minds["leo"];
            var overheard = leo.Experiences.Single(x => x.EventId == "b08");
            var seen = leo.Experiences.Single(x => x.EventId == "b09");

            Assert.AreEqual(ExperienceSource.Overheard, overheard.Source);
            Assert.Less(overheard.Confidence, seen.Confidence);
        }

        // ---- is it the rules doing the work, or the people? ----

        [Test]
        public void GiveTheOlderBrotherHisBrotherTemperamentAndHeStopsTakingOffence()
        {
            // Same rules, same script, same ages and roles. Only the traits,
            // values and way of reading a room are exchanged. If the reading of
            // b05 survives that, the rules are carrying it rather than the
            // people, and the slice has proved nothing.
            var swapped = new Dictionary<string, Profile>(StringComparer.Ordinal);
            foreach (var pair in _cast) swapped[pair.Key] = pair.Value;
            swapped["daniel"] = WearingTheTemperamentOf(_cast["daniel"], _cast["leo"]);
            swapped["leo"] = WearingTheTemperamentOf(_cast["leo"], _cast["daniel"]);

            var otherwise = new Simulation(swapped, _rules);
            var otherOutcomes = otherwise.Run(_script).ToDictionary(o => o.Event.Id, o => o, StringComparer.Ordinal);

            var asWritten = _outcomes.Single(o => o.Event.Id == "b05").ByCharacter["daniel"];
            var asSwapped = otherOutcomes["b05"].ByCharacter["daniel"];

            Assert.AreEqual("disrespect", asWritten.Meaning);
            Assert.AreNotEqual("disrespect", asSwapped.Meaning,
                "being corrected in front of the family is only an insult to someone built to hear it that way");
        }

        [Test]
        public void WithoutTheThreeDaysBehindItTheSameSentenceLandsMoreLightly()
        {
            // The probe events alone, with no history to read them against.
            var probesOnly = new ScenarioScript(
                _script.Id, _script.Description, _script.CharacterIds,
                _script.Events.Where(e => e.Id.StartsWith("p", StringComparison.Ordinal)).ToList());

            var stranger = new Simulation(_cast, _rules);
            var withoutHistory = stranger.Run(probesOnly)
                .Single(o => o.Event.Id == "p01").ByCharacter["daniel"];

            var withHistory = _outcomes.Single(o => o.Event.Id == "p01").ByCharacter["daniel"];

            Assert.Greater(withHistory.InterpretationWeight, withoutHistory.InterpretationWeight,
                "the argument they already had is part of what he hears");
        }

        [Test]
        public void SomeReadingsAreCloseRunThingsRatherThanForegoneConclusions()
        {
            // A model where every reading wins by a mile is a model with one
            // answer per situation. Some of these should have nearly gone the
            // other way, because that is where the interesting people live.
            var contested = _outcomes
                .SelectMany(o => o.ByCharacter.Values)
                .Where(p => p.Access != Access.None && !p.FromOwnIntent && p.RunnerUpMeaning != null)
                .Count(p => p.InterpretationWeight - WeightOfRunnerUp(p) < 0.35);

            Assert.Greater(contested, 0,
                "nothing was a close call, which means nobody could have taken anything another way");
        }

        static double WeightOfRunnerUp(PerceptionOutcome outcome)
        {
            // Recovered from the trace rather than stored twice.
            var record = _sim.Trace.Get(outcome.InterpretationTraceId);
            if (record == null || !record.Data.ContainsKey("runner_up")) return 0.0;
            var text = record.Data["runner_up"];
            var space = text.LastIndexOf(' ');
            return space < 0 ? 0.0 : double.Parse(text.Substring(space + 1),
                System.Globalization.CultureInfo.InvariantCulture);
        }

        static Profile WearingTheTemperamentOf(Profile who, Profile temperament)
            => new Profile(
                who.Id, who.DisplayName, who.Age, who.FamilyRole,
                temperament.Traits, temperament.Values,
                temperament.Perceptiveness, temperament.AttentionWeights,
                who.InitialBeliefs);

        static string Summary()
            => $"cells {_cells.Count}; meaning {_meaningMatch:P1} (gate {_meaningGate:P0}); " +
               $"emotion {_emotionMatch:P1} (gate {_emotionGate:P0}); misses {_misses.Count}\n" +
               string.Join("\n", _misses);
    }

    /// <summary>
    /// The rules that keep the slice honest. If any of these fail, a passing
    /// expectation table proves nothing, because the model would have been
    /// allowed to cheat.
    /// </summary>
    public class PurityTests
    {
        static readonly string[] CastNames = { "leo", "daniel", "mara", "elena" };

        static IEnumerable<string> CoreSourceFiles()
            => Directory.GetFiles(TestPaths.CoreSources, "*.cs", SearchOption.AllDirectories);

        [Test]
        public void TheSimulationDoesNotDependOnTheGameEngine()
        {
            var offenders = CoreSourceFiles()
                .Where(f => File.ReadAllText(f).Contains("UnityEngine") || File.ReadAllText(f).Contains("UnityEditor"))
                .Select(f => Path.GetFileName(f))
                .ToList();

            Assert.IsEmpty(offenders,
                "Fallow.Core must stay headless so it can be batch-tested: " + string.Join(", ", offenders));
        }

        [Test]
        public void NoLineOfTheSimulationKnowsAnyCharacterByName()
        {
            var offenders = new List<string>();

            foreach (var file in CoreSourceFiles())
            {
                var lines = File.ReadAllLines(file);
                for (var i = 0; i < lines.Length; i++)
                foreach (var name in CastNames)
                {
                    if (!System.Text.RegularExpressions.Regex.IsMatch(
                            lines[i], $@"\b{name}\b",
                            System.Text.RegularExpressions.RegexOptions.IgnoreCase)) continue;
                    offenders.Add($"{Path.GetFileName(file)}:{i + 1} mentions {name}");
                }
            }

            Assert.IsEmpty(offenders,
                "the whole claim of the slice is that these people differ only in their data:\n"
                + string.Join("\n", offenders));
        }

        [Test]
        public void NoRuleKnowsAnyCharacterByName()
        {
            var rules = RuleSetLoader.LoadFile(Path.Combine(TestPaths.Rules, "rules.json"));
            var cast = ProfileLoader.LoadDirectory(TestPaths.Minds);

            var problems = RuleSetValidator.ValidateNamesNobody(rules, cast.Keys);
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void TheRuleFileItselfContainsNoCharacterName()
        {
            var text = File.ReadAllText(Path.Combine(TestPaths.Rules, "rules.json"));

            var offenders = CastNames
                .Where(n => System.Text.RegularExpressions.Regex.IsMatch(
                    text, $@"\b{n}\b", System.Text.RegularExpressions.RegexOptions.IgnoreCase))
                .ToList();

            Assert.IsEmpty(offenders,
                "a rule that names somebody is content pretending to be a model: " + string.Join(", ", offenders));
        }

        [Test]
        public void ARuleCannotAskWhetherSomeoneIsProudEnough()
        {
            // Enforced by construction: Condition exposes only circumstances.
            // This test guards the type against gaining a personal term later.
            var personalTerms = typeof(Condition)
                .GetProperties()
                .Select(p => p.Name)
                .Where(n => n.Contains("Trait") || n.Contains("Value") || n.Contains("Belief")
                            || n.Contains("Ledger") || n.Contains("Emotion") || n.Contains("Perceptiveness"))
                .ToList();

            Assert.IsEmpty(personalTerms,
                "conditions decide whether a rule applies to a moment, never to a person; "
                + "anything about the person belongs in scaled_by, where it is a weight: "
                + string.Join(", ", personalTerms));
        }
    }
}
