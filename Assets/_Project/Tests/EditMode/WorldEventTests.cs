using System.IO;
using System.Linq;
using Fallow.Core.Data;
using Fallow.Core.Model;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    public class WorldEventTests
    {
        const string SpeechJson = @"{
            ""id"": ""x01"", ""day"": 2, ""order"": 5,
            ""type"": ""speech"", ""actor"": ""a"", ""target"": ""b"",
            ""act"": ""refuse"", ""topic"": ""going_outside"",
            ""tone"": ""calm"", ""directness"": ""direct"", ""valence"": ""neutral"",
            ""intent"": ""protect"",
            ""witnesses"": [""b"", ""c""], ""overhearers"": [""d""],
            ""summary"": ""A refuses B in front of C."",
            ""ledger_effects"": [
                { ""holder"": ""b"", ""about"": ""a"", ""entry"": ""overruled_me"", ""weight"": 0.7 }
            ]
        }";

        const string WorldJson = @"{
            ""id"": ""x02"", ""day"": 2, ""order"": 6,
            ""type"": ""action"", ""actor"": null, ""target"": null,
            ""action"": ""water_stops"", ""topic"": ""supplies"",
            ""tone"": ""neutral"", ""directness"": ""direct"", ""valence"": ""bad"",
            ""intent"": null,
            ""witnesses"": [""a"", ""b""], ""overhearers"": [],
            ""summary"": ""The taps run dry."",
            ""ledger_effects"": []
        }";

        [Test]
        public void ParsesASpeechEvent()
        {
            var e = ScenarioLoader.EventFromJson(SpeechJson);

            Assert.AreEqual("x01", e.Id);
            Assert.AreEqual(2, e.Day);
            Assert.AreEqual(5, e.Order);
            Assert.AreEqual(EventKind.Speech, e.Kind);
            Assert.AreEqual("a", e.ActorId);
            Assert.AreEqual("b", e.TargetId);
            Assert.AreEqual("refuse", e.Act);
            Assert.AreEqual("going_outside", e.Topic);
            Assert.AreEqual("calm", e.Tone);
            Assert.AreEqual("direct", e.Directness);
            Assert.AreEqual("neutral", e.Valence);
            Assert.AreEqual("protect", e.Intent);
            Assert.AreEqual(1, e.LedgerEffects.Count);
            Assert.AreEqual("overruled_me", e.LedgerEffects[0].Entry);
            Assert.AreEqual(0.7, e.LedgerEffects[0].Weight, 1e-9);
        }

        [Test]
        public void ParsesAWorldEventWithNoActor()
        {
            var e = ScenarioLoader.EventFromJson(WorldJson);

            Assert.AreEqual(EventKind.Action, e.Kind);
            Assert.IsNull(e.ActorId);
            Assert.AreEqual("water_stops", e.Action);
            Assert.IsNull(e.Intent);
        }

        [Test]
        public void ThePersonActingAlwaysWitnessesTheirOwnAct()
        {
            var e = ScenarioLoader.EventFromJson(SpeechJson);
            Assert.AreEqual(Access.Witnessed, e.AccessFor("a"));
        }

        [Test]
        public void ListedWitnessesSeeAndListedOverhearersOnlyHear()
        {
            var e = ScenarioLoader.EventFromJson(SpeechJson);

            Assert.AreEqual(Access.Witnessed, e.AccessFor("b"));
            Assert.AreEqual(Access.Witnessed, e.AccessFor("c"));
            Assert.AreEqual(Access.Overheard, e.AccessFor("d"));
        }

        [Test]
        public void SomeoneWhoWasNotThereGetsNothing()
        {
            var e = ScenarioLoader.EventFromJson(SpeechJson);
            Assert.AreEqual(Access.None, e.AccessFor("someone_else"));
        }

        [Test]
        public void TargetingEveryoneIsDistinctFromTargetingAPerson()
        {
            var toAll = ScenarioLoader.EventFromJson(SpeechJson.Replace(@"""target"": ""b""", @"""target"": ""all"""));
            var toOne = ScenarioLoader.EventFromJson(SpeechJson);

            Assert.IsTrue(toAll.TargetsEveryone);
            Assert.IsFalse(toOne.TargetsEveryone);
            Assert.IsTrue(toAll.Targets("b"));
            Assert.IsTrue(toAll.Targets("c"));
            Assert.IsTrue(toOne.Targets("b"));
            Assert.IsFalse(toOne.Targets("c"));
        }

        [Test]
        public void ShippedScenarioLoadsInOrderAndValidates()
        {
            var vocab = VocabularyLoader.LoadFile(Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var cast = ProfileLoader.LoadDirectory(TestPaths.Minds);
            var script = ScenarioLoader.LoadFile(Path.Combine(TestPaths.Scenario, "backstory.json"));

            Assert.AreEqual(12, script.Events.Count);
            CollectionAssert.IsOrdered(script.Events.Select(e => e.Order));

            var problems = ScenarioValidator.Validate(script, vocab, cast);
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void ValidatorRejectsALedgerEffectForSomeoneWhoWasNotThere()
        {
            var vocab = VocabularyLoader.LoadFile(Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var cast = ProfileLoader.LoadDirectory(TestPaths.Minds);

            // Only Elena and Mara are in the room. Crediting Leo from this event
            // would hand him a memory of something he never saw.
            const string json = @"{
                ""id"": ""tampered"", ""description"": ""one event with an absent beneficiary"",
                ""characters"": [""leo"", ""daniel"", ""mara"", ""elena""],
                ""events"": [{
                    ""id"": ""t01"", ""day"": 1, ""order"": 1,
                    ""type"": ""action"", ""actor"": ""elena"", ""target"": null,
                    ""action"": ""count_supplies"", ""topic"": ""supplies"",
                    ""tone"": ""neutral"", ""directness"": ""direct"", ""valence"": ""neutral"",
                    ""intent"": ""take_responsibility"",
                    ""witnesses"": [""mara""], ""overhearers"": [],
                    ""summary"": ""Elena counts the pantry with only Mara there."",
                    ""ledger_effects"": [
                        { ""holder"": ""leo"", ""about"": ""elena"", ""entry"": ""proved_right"", ""weight"": 0.5 }
                    ]
                }]
            }";

            var script = ScenarioLoader.FromJson(json);
            var problems = ScenarioValidator.Validate(script, vocab, cast);

            Assert.IsNotEmpty(problems);
            var text = string.Join("\n", problems);
            StringAssert.Contains("leo", text);
            StringAssert.Contains("no access", text);
        }

        [Test]
        public void ValidatorRejectsAnUnknownTopic()
        {
            var vocab = VocabularyLoader.LoadFile(Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var cast = ProfileLoader.LoadDirectory(TestPaths.Minds);
            var raw = File.ReadAllText(Path.Combine(TestPaths.Scenario, "backstory.json"));

            var script = ScenarioLoader.FromJson(raw.Replace(@"""topic"": ""shelter""", @"""topic"": ""shelters"""));
            var problems = ScenarioValidator.Validate(script, vocab, cast);

            Assert.IsNotEmpty(problems);
            StringAssert.Contains("shelters", string.Join("\n", problems));
        }
    }
}
