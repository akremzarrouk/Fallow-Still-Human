using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Data;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The interpreter turns an event into what it meant to one person. These
    /// tests use small inline rule sets rather than the shipped ones, so they
    /// check the machinery rather than the content.
    /// </summary>
    public class InterpreterTests
    {
        static Profile Person(string id, int age, string role = "sibling", string traits = @"""proud"": 0.5", string values = @"""respect""")
        {
            return ProfileLoader.FromJson($@"{{
                ""id"": ""{id}"", ""display_name"": ""{id}"", ""age"": {age}, ""family_role"": ""{role}"",
                ""traits"": {{ {traits} }},
                ""values"": [{values}],
                ""perception"": {{ ""perceptiveness"": 0.5 }},
                ""initial_beliefs"": []
            }}");
        }

        static WorldEvent Speech(
            string actor, string target, string act = "suggest", string topic = "who_decides",
            string tone = "calm", string directness = "indirect", string intent = null,
            params string[] witnesses)
        {
            var intentJson = intent == null ? "null" : $@"""{intent}""";
            var w = string.Join(", ", witnesses.Select(x => $@"""{x}"""));
            return ScenarioLoader.EventFromJson($@"{{
                ""id"": ""t01"", ""day"": 1, ""order"": 1,
                ""type"": ""speech"", ""actor"": ""{actor}"", ""target"": ""{target}"",
                ""act"": ""{act}"", ""topic"": ""{topic}"",
                ""tone"": ""{tone}"", ""directness"": ""{directness}"", ""valence"": ""neutral"",
                ""intent"": {intentJson},
                ""witnesses"": [{w}], ""overhearers"": [],
                ""summary"": ""a test event"", ""ledger_effects"": []
            }}");
        }

        static RuleSet Rules(string interpretationRulesJson)
        {
            return RuleSetLoader.FromJson($@"{{
                ""interpretation"": {interpretationRulesJson},
                ""belief_nudges"": [],
                ""appraisal"": [],
                ""dynamics"": {{}}
            }}");
        }

        static Interpreter InterpreterWith(RuleSet rules) => new Interpreter(rules);

        // ---- access and self-knowledge ----

        [Test]
        public void SomeoneWhoWasNotThereMakesNothingOfIt()
        {
            var cast = Cast(Person("a", 30), Person("b", 20));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var mind = new Mind(cast["b"]);
            var interp = InterpreterWith(Rules("[]"));

            var result = interp.Interpret(mind, e, Access.None, cast, new TraceLog(), 0);

            Assert.IsNull(result);
        }

        [Test]
        public void ThePersonActingKnowsWhatTheyMeantByIt()
        {
            var cast = Cast(Person("a", 30), Person("b", 20));
            var e = Speech("a", "b", intent: "protect", witnesses: new[] { "b" });
            var mind = new Mind(cast["a"]);

            // A rule that would read it as disrespect if rules were consulted at all.
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 5.0 }]");

            var result = InterpreterWith(rules).Interpret(mind, e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("protect", result.Meaning);
            Assert.IsTrue(result.FromOwnIntent);
            Assert.IsEmpty(result.Contributions, "own intention is known, not inferred");
        }

        [Test]
        public void AnActWithNoStatedIntentionIsReadLikeAnybodyElseWouldReadIt()
        {
            var cast = Cast(Person("a", 30), Person("b", 20));
            var e = Speech("a", "b", intent: null, witnesses: new[] { "b" });
            var mind = new Mind(cast["a"]);
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": {}, ""label"": ""challenge"", ""base_weight"": 1.0 }]");

            var result = InterpreterWith(rules).Interpret(mind, e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("challenge", result.Meaning);
            Assert.IsFalse(result.FromOwnIntent);
        }

        // ---- scoring ----

        [Test]
        public void TheHeaviestReadingWins()
        {
            var cast = Cast(Person("a", 30), Person("b", 20));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var mind = new Mind(cast["b"]);
            var rules = Rules(@"[
                { ""id"": ""light"", ""when"": {}, ""label"": ""concern"",    ""base_weight"": 0.3 },
                { ""id"": ""heavy"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 0.9 }
            ]");

            var result = InterpreterWith(rules).Interpret(mind, e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("disrespect", result.Meaning);
            Assert.AreEqual(0.9, result.Weight, 1e-9);
            Assert.AreEqual("concern", result.RunnerUpMeaning);
        }

        [Test]
        public void TwoRulesForTheSameReadingAddUp()
        {
            var cast = Cast(Person("a", 30), Person("b", 20));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var mind = new Mind(cast["b"]);
            var rules = Rules(@"[
                { ""id"": ""one"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.3 },
                { ""id"": ""two"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.4 }
            ]");

            var result = InterpreterWith(rules).Interpret(mind, e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("concern", result.Meaning);
            Assert.AreEqual(0.7, result.Weight, 1e-9);
        }

        [Test]
        public void PrideDecidesWhetherTheSameSentenceIsAnInsult()
        {
            var cast = Cast(
                Person("a", 20),
                Person("proudOne", 30, traits: @"""proud"": 0.9"),
                Person("humbleOne", 30, traits: @"""proud"": 0.1"));
            var e = Speech("a", "proudOne", witnesses: new[] { "proudOne", "humbleOne" });

            var rules = Rules(@"[
                { ""id"": ""slight"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 0.2,
                  ""scaled_by"": [{ ""kind"": ""trait"", ""name"": ""proud"", ""factor"": 0.6 }] },
                { ""id"": ""plain"",  ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.5 }
            ]");
            var interp = InterpreterWith(rules);

            var proud = interp.Interpret(new Mind(cast["proudOne"]), e, Access.Witnessed, cast, new TraceLog(), 0);
            var humble = interp.Interpret(new Mind(cast["humbleOne"]), e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("disrespect", proud.Meaning);
            Assert.AreEqual("concern", humble.Meaning);
        }

        [Test]
        public void WhatIAlreadyBelieveAboutSomeoneColoursWhatTheySay()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var e = Speech("a", "b", witnesses: new[] { "b" });

            var rules = Rules(@"[
                { ""id"": ""slight"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 0.2,
                  ""scaled_by"": [{ ""kind"": ""belief"", ""predicate"": ""tendency"",
                                    ""args"": [""$actor"", ""does_not_respect_me""], ""factor"": 0.8 }] },
                { ""id"": ""plain"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.5 }
            ]");
            var interp = InterpreterWith(rules);

            var trusting = new Mind(cast["b"]);
            var suspicious = new Mind(cast["b"]);
            suspicious.Beliefs.Seed(new BeliefSeed("tendency", new[] { "a", "does_not_respect_me" }, 0.8));

            Assert.AreEqual("concern", interp.Interpret(trusting, e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("disrespect", interp.Interpret(suspicious, e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void WhatSomeoneDidToMeBeforeColoursWhatTheyDoNow()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var e = Speech("a", "b", witnesses: new[] { "b" });

            var rules = Rules(@"[
                { ""id"": ""slight"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 0.2,
                  ""scaled_by"": [{ ""kind"": ""ledger"", ""entry"": ""overruled_me"", ""about"": ""$actor"", ""factor"": 0.8 }] },
                { ""id"": ""plain"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.5 }
            ]");
            var interp = InterpreterWith(rules);

            var fresh = new Mind(cast["b"]);
            var sore = new Mind(cast["b"]);
            sore.Ledger.Add("a", "overruled_me", 0.7, traceId: 0, eventId: "earlier");

            Assert.AreEqual("concern", interp.Interpret(fresh, e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("disrespect", interp.Interpret(sore, e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void WhatIAmAlreadyFeelingColoursWhatIHear()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var e = Speech("a", "b", witnesses: new[] { "b" });

            var rules = Rules(@"[
                { ""id"": ""alarm"", ""when"": {}, ""label"": ""threat"", ""base_weight"": 0.1,
                  ""scaled_by"": [{ ""kind"": ""emotion"", ""name"": ""fear"", ""factor"": 0.9 }] },
                { ""id"": ""plain"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.5 }
            ]");
            var interp = InterpreterWith(rules);

            var calm = new Mind(cast["b"]);
            var frightened = new Mind(cast["b"]);
            frightened.Emotions.Add("fear", null, "family_safety", 0.8, traceId: 0, eventId: "earlier");

            Assert.AreEqual("concern", interp.Interpret(calm, e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("threat", interp.Interpret(frightened, e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void ANegativeScalerCanTalkSomeoneOutOfAReading()
        {
            var cast = Cast(Person("a", 20), Person("b", 30, traits: @"""proud"": 0.5, ""empathetic"": 0.9"));
            var e = Speech("a", "b", witnesses: new[] { "b" });

            var rules = Rules(@"[
                { ""id"": ""slight"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 0.8,
                  ""scaled_by"": [{ ""kind"": ""trait"", ""name"": ""empathetic"", ""factor"": -0.7 }] },
                { ""id"": ""plain"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.5 }
            ]");

            var result = InterpreterWith(rules).Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("concern", result.Meaning);
        }

        [Test]
        public void NothingThatFitsReadsAsNeutral()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""topics"": [""missing_can""] }, ""label"": ""deception"", ""base_weight"": 1.0 }]");

            var result = InterpreterWith(rules).Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("neutral", result.Meaning);
        }

        [Test]
        public void TiesBreakByNameSoTheSameRunAlwaysReadsTheSame()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var rules = Rules(@"[
                { ""id"": ""one"", ""when"": {}, ""label"": ""threat"",  ""base_weight"": 0.5 },
                { ""id"": ""two"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 0.5 }
            ]");

            var result = InterpreterWith(rules).Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0);

            Assert.AreEqual("concern", result.Meaning);
        }

        // ---- conditions ----

        [Test]
        public void ARuleOnlyFiresForTheActItNames()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""acts"": [""demand""] }, ""label"": ""disrespect"", ""base_weight"": 1.0 }]");
            var interp = InterpreterWith(rules);

            var demanded = Speech("a", "b", act: "demand", witnesses: new[] { "b" });
            var suggested = Speech("a", "b", act: "suggest", witnesses: new[] { "b" });

            Assert.AreEqual("disrespect", interp.Interpret(new Mind(cast["b"]), demanded, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("neutral", interp.Interpret(new Mind(cast["b"]), suggested, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void ARuleCanAskWhoTheOtherPersonIsToMeWithoutNamingThem()
        {
            var cast = Cast(Person("young", 20), Person("old", 40));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""actor_relations"": [""junior""] }, ""label"": ""disrespect"", ""base_weight"": 1.0 }]");
            var interp = InterpreterWith(rules);

            var fromYounger = Speech("young", "old", witnesses: new[] { "old" });
            var fromOlder = Speech("old", "young", witnesses: new[] { "young" });

            Assert.AreEqual("disrespect", interp.Interpret(new Mind(cast["old"]), fromYounger, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("neutral", interp.Interpret(new Mind(cast["young"]), fromOlder, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void ARuleCanRequireAnAudience()
        {
            var cast = Cast(Person("a", 20), Person("b", 30), Person("c", 35));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""audience_min"": 1 }, ""label"": ""disrespect"", ""base_weight"": 1.0 }]");
            var interp = InterpreterWith(rules);

            var watched = Speech("a", "b", witnesses: new[] { "b", "c" });
            var alone = Speech("a", "b", witnesses: new[] { "b" });

            Assert.AreEqual("disrespect", interp.Interpret(new Mind(cast["b"]), watched, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("neutral", interp.Interpret(new Mind(cast["b"]), alone, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void ARuleCanCareWhetherItWasAimedAtMe()
        {
            var cast = Cast(Person("a", 20), Person("b", 30), Person("c", 35));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""addressed"": [""me""] }, ""label"": ""disrespect"", ""base_weight"": 1.0 }]");
            var interp = InterpreterWith(rules);

            var e = Speech("a", "b", witnesses: new[] { "b", "c" });

            Assert.AreEqual("disrespect", interp.Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("neutral", interp.Interpret(new Mind(cast["c"]), e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void ARuleCanRequireHavingSeenItRatherThanOnlyHeardIt()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""access"": [""witnessed""] }, ""label"": ""deception"", ""base_weight"": 1.0 }]");
            var interp = InterpreterWith(rules);
            var e = Speech("a", "b", witnesses: new[] { "b" });

            Assert.AreEqual("deception", interp.Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("neutral", interp.Interpret(new Mind(cast["b"]), e, Access.Overheard, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void ARuleCanRequireThatSomebodyRatherThanTheWorldDidIt()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""has_actor"": false }, ""label"": ""threat"", ""base_weight"": 1.0 }]");
            var interp = InterpreterWith(rules);

            var byPerson = Speech("a", "b", witnesses: new[] { "b" });
            var byWorld = ScenarioLoader.EventFromJson(@"{
                ""id"": ""w"", ""day"": 1, ""order"": 1, ""type"": ""action"", ""actor"": null, ""target"": null,
                ""action"": ""water_stops"", ""topic"": ""supplies"", ""tone"": ""neutral"",
                ""directness"": ""direct"", ""valence"": ""bad"", ""intent"": null,
                ""witnesses"": [""b""], ""overhearers"": [], ""summary"": ""taps dry"", ""ledger_effects"": [] }");

            Assert.AreEqual("neutral", interp.Interpret(new Mind(cast["b"]), byPerson, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("threat", interp.Interpret(new Mind(cast["b"]), byWorld, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void BeingOneOfARoomAddressedIsNotTheSameAsBeingSpokenTo()
        {
            var cast = Cast(Person("a", 20), Person("b", 30), Person("c", 35));
            var rules = Rules(@"[
                { ""id"": ""aimed"",   ""when"": { ""addressed"": [""me""] },    ""label"": ""disrespect"", ""base_weight"": 1.0 },
                { ""id"": ""atRoom"",  ""when"": { ""addressed"": [""group""] }, ""label"": ""concern"",    ""base_weight"": 1.0 },
                { ""id"": ""atOther"", ""when"": { ""addressed"": [""other""] }, ""label"": ""threat"",     ""base_weight"": 1.0 }
            ]");
            var interp = InterpreterWith(rules);

            var toRoom = Speech("a", "all", witnesses: new[] { "b", "c" });
            var toB = Speech("a", "b", witnesses: new[] { "b", "c" });

            Assert.AreEqual("concern", interp.Interpret(new Mind(cast["b"]), toRoom, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("disrespect", interp.Interpret(new Mind(cast["b"]), toB, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
            Assert.AreEqual("threat", interp.Interpret(new Mind(cast["c"]), toB, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        [Test]
        public void AnEventAimedAtNoOneIsAddressedToNobody()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": { ""addressed"": [""nobody""] }, ""label"": ""concern"", ""base_weight"": 1.0 }]");
            var e = ScenarioLoader.EventFromJson(@"{
                ""id"": ""w"", ""day"": 1, ""order"": 1, ""type"": ""action"", ""actor"": ""a"", ""target"": null,
                ""action"": ""board_windows"", ""topic"": ""shelter"", ""tone"": ""neutral"",
                ""directness"": ""direct"", ""valence"": ""good"", ""intent"": null,
                ""witnesses"": [""b""], ""overhearers"": [], ""summary"": ""a boards up"", ""ledger_effects"": [] }");

            Assert.AreEqual("concern", InterpreterWith(rules).Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0).Meaning);
        }

        // ---- explainability ----

        [Test]
        public void EveryTermThatMovedTheReadingIsItemised()
        {
            var cast = Cast(Person("a", 20), Person("b", 30, traits: @"""proud"": 0.8"));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var rules = Rules(@"[{ ""id"": ""slight"", ""when"": {}, ""label"": ""disrespect"", ""base_weight"": 0.2,
                ""scaled_by"": [{ ""kind"": ""trait"", ""name"": ""proud"", ""factor"": 0.5 }] }]");

            var result = InterpreterWith(rules).Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, new TraceLog(), 0);

            var contribution = result.Contributions.Single();
            Assert.AreEqual("slight", contribution.RuleId);
            Assert.AreEqual(0.2, contribution.BaseWeight, 1e-9);
            Assert.AreEqual(0.6, contribution.Total, 1e-9);

            var term = contribution.Terms.Single();
            Assert.AreEqual(0.4, term.Amount, 1e-9);
            StringAssert.Contains("proud", term.Description);
        }

        [Test]
        public void TheReadingIsWrittenIntoTheTraceUnderTheStepItCameFrom()
        {
            var cast = Cast(Person("a", 20), Person("b", 30));
            var e = Speech("a", "b", witnesses: new[] { "b" });
            var rules = Rules(@"[{ ""id"": ""r"", ""when"": {}, ""label"": ""challenge"", ""base_weight"": 0.6 }]");
            var trace = new TraceLog();
            var parent = trace.Add(TraceKind.Access, "b", "t01", "b was in the room");

            var result = InterpreterWith(rules).Interpret(new Mind(cast["b"]), e, Access.Witnessed, cast, trace, parent);

            var record = trace.Get(result.TraceId);
            Assert.AreEqual(TraceKind.Interpretation, record.Kind);
            Assert.AreEqual("b", record.CharacterId);
            CollectionAssert.Contains(record.ParentIds.ToArray(), parent);
            StringAssert.Contains("challenge", record.Summary);
        }

        static IReadOnlyDictionary<string, Profile> Cast(params Profile[] people)
            => people.ToDictionary(p => p.Id, p => p);
    }

    public class MindTests
    {
        [Test]
        public void AMindStartsOutHoldingTheBeliefsItsCharacterFileGaveIt()
        {
            var profile = ProfileLoader.FromJson(@"{
                ""id"": ""x"", ""display_name"": ""X"", ""age"": 30, ""family_role"": ""sibling"",
                ""traits"": { ""proud"": 0.5 }, ""values"": [""respect""],
                ""perception"": { ""perceptiveness"": 0.5 },
                ""initial_beliefs"": [
                    { ""predicate"": ""tendency"", ""args"": [""y"", ""makes_risky_calls""], ""confidence"": 0.45 }
                ]
            }");

            var mind = new Mind(profile);

            Assert.AreEqual(0.45, mind.Beliefs.Confidence("tendency", "y", "makes_risky_calls"), 1e-9);
            Assert.AreEqual("x", mind.Id);
            Assert.IsEmpty(mind.Ledger.All);
            Assert.IsEmpty(mind.Emotions.Live);
            Assert.IsEmpty(mind.Experiences);
        }
    }

    public class RuleValidationTests
    {
        [Test]
        public void ShippedRulesLoadAndValidate()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var rules = RuleSetLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "rules.json"));

            var problems = RuleSetValidator.Validate(rules, vocab);

            Assert.IsEmpty(problems, string.Join("\n", problems));
            Assert.IsNotEmpty(rules.Interpretation, "the slice needs interpretation rules to say anything");
            Assert.IsNotEmpty(rules.Appraisal, "the slice needs appraisal rules to feel anything");
        }

        [Test]
        public void ValidatorRejectsAReadingThatIsNotInTheVocabulary()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var rules = RuleSetLoader.FromJson(@"{
                ""interpretation"": [{ ""id"": ""r"", ""when"": {}, ""label"": ""disrespekt"", ""base_weight"": 1.0 }],
                ""belief_nudges"": [], ""appraisal"": [], ""dynamics"": {} }");

            var problems = RuleSetValidator.Validate(rules, vocab);

            Assert.IsNotEmpty(problems);
            StringAssert.Contains("disrespekt", string.Join("\n", problems));
        }

        [Test]
        public void ValidatorRejectsARuleThatScalesOnATraitNobodyHas()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var rules = RuleSetLoader.FromJson(@"{
                ""interpretation"": [{ ""id"": ""r"", ""when"": {}, ""label"": ""concern"", ""base_weight"": 1.0,
                    ""scaled_by"": [{ ""kind"": ""trait"", ""name"": ""smug"", ""factor"": 0.5 }] }],
                ""belief_nudges"": [], ""appraisal"": [], ""dynamics"": {} }");

            var problems = RuleSetValidator.Validate(rules, vocab);

            Assert.IsNotEmpty(problems);
            StringAssert.Contains("smug", string.Join("\n", problems));
        }

        [Test]
        public void ValidatorRejectsAConditionOnATermThatDoesNotExist()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var rules = RuleSetLoader.FromJson(@"{
                ""interpretation"": [{ ""id"": ""r"", ""when"": { ""tones"": [""shouty""] }, ""label"": ""concern"", ""base_weight"": 1.0 }],
                ""belief_nudges"": [], ""appraisal"": [], ""dynamics"": {} }");

            var problems = RuleSetValidator.Validate(rules, vocab);

            Assert.IsNotEmpty(problems);
            StringAssert.Contains("shouty", string.Join("\n", problems));
        }
    }
}
