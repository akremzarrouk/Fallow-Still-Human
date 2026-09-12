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
    /// The whole pipeline for one event: who had access, what they made of it,
    /// what it stirred, and what it left behind. Small inline data throughout,
    /// so these check the machinery rather than the cast.
    /// </summary>
    public class SimulationTests
    {
        static Profile Person(string id, int age, string traits, string values, string role = "sibling")
            => ProfileLoader.FromJson($@"{{
                ""id"": ""{id}"", ""display_name"": ""{id}"", ""age"": {age}, ""family_role"": ""{role}"",
                ""traits"": {{ {traits} }}, ""values"": [{values}],
                ""perception"": {{ ""perceptiveness"": 0.5 }},
                ""initial_beliefs"": []
            }}");

        static IReadOnlyDictionary<string, Profile> Cast(params Profile[] people)
            => people.ToDictionary(p => p.Id, p => p);

        const string TwoRules = @"{
            ""interpretation"": [
                { ""id"": ""bad_is_a_problem"", ""when"": { ""valences"": [""bad""] }, ""label"": ""concern"", ""base_weight"": 0.6 },
                { ""id"": ""ordered_about"", ""when"": { ""acts"": [""demand""], ""addressed"": [""me""] },
                  ""label"": ""disrespect"", ""base_weight"": 0.7 }
            ],
            ""belief_nudges"": [
                { ""id"": ""slights_add_up"", ""when"": { ""meanings"": [""disrespect""] },
                  ""predicate"": ""tendency"", ""args"": [""$actor"", ""does_not_respect_me""], ""delta"": 0.2 }
            ],
            ""appraisal"": [
                { ""id"": ""slight_shames"", ""when"": { ""meanings"": [""disrespect""] },
                  ""emotion"": ""shame"", ""concern"": ""respect"", ""base_intensity"": 0.2,
                  ""scaled_by"": [{ ""kind"": ""trait"", ""name"": ""proud"", ""factor"": 0.6 }] },
                { ""id"": ""slight_angers"", ""when"": { ""meanings"": [""disrespect""] },
                  ""emotion"": ""anger"", ""target"": ""$actor"", ""concern"": ""respect"", ""base_intensity"": 0.1,
                  ""scaled_by"": [{ ""kind"": ""trait"", ""name"": ""dominant"", ""factor"": 0.6 }] },
                { ""id"": ""problem_worries"", ""when"": { ""meanings"": [""concern""] },
                  ""emotion"": ""anxiety"", ""concern"": ""family_safety"", ""base_intensity"": 0.3 }
            ],
            ""dynamics"": { ""emotion_decay_base"": 0.5, ""emotion_decay_anxiety_resistance"": 0.0,
                            ""emotion_floor"": 0.05, ""overheard_confidence"": 0.6,
                            ""overheard_intensity_scale"": 0.5,
                            ""salience_base"": 0.1 }
        }";

        static string Demand(string actor, string target, string[] witnesses, string[] overhearers = null, string intent = null)
        {
            var w = string.Join(", ", witnesses.Select(x => $@"""{x}"""));
            var o = string.Join(", ", (overhearers ?? new string[0]).Select(x => $@"""{x}"""));
            var intentJson = intent == null ? "null" : $@"""{intent}""";
            return $@"{{
                ""id"": ""scenario"", ""description"": ""one demand"",
                ""characters"": [{string.Join(", ", new[] { actor, target }.Concat(witnesses).Concat(overhearers ?? new string[0]).Distinct().Select(x => $@"""{x}"""))}],
                ""events"": [{{
                    ""id"": ""e1"", ""day"": 1, ""order"": 1,
                    ""type"": ""speech"", ""actor"": ""{actor}"", ""target"": ""{target}"",
                    ""act"": ""demand"", ""topic"": ""who_decides"",
                    ""tone"": ""raised"", ""directness"": ""direct"", ""valence"": ""neutral"",
                    ""intent"": {intentJson},
                    ""witnesses"": [{w}], ""overhearers"": [{o}],
                    ""summary"": ""{actor} tells {target} how it is."", ""ledger_effects"": []
                }}]
            }}";
        }

        static Simulation Sim(IReadOnlyDictionary<string, Profile> cast, string rulesJson = TwoRules)
            => new Simulation(cast, RuleSetLoader.FromJson(rulesJson));

        // ---- locality ----

        [Test]
        public void SomeoneWhoWasNotThereKeepsNoMemoryOfIt()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("away", 25, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""));
            var sim = Sim(cast);

            var outcomes = sim.Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })));
            var away = outcomes[0].ByCharacter["away"];

            Assert.AreEqual(Access.None, away.Access);
            Assert.IsNull(away.Meaning);
            Assert.IsNull(away.Experience);
            Assert.IsEmpty(sim.Minds["away"].Experiences);
            Assert.IsEmpty(sim.Minds["away"].Emotions.Live);
            Assert.AreEqual(0.0, sim.Minds["away"].Beliefs.Confidence("tendency", "a", "does_not_respect_me"), 1e-9);
        }

        [Test]
        public void SomeoneWhoOnlyHeardItHoldsItLessSurelyAndFeelsItLess()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("wall", 22, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""));

            // Both b and wall are targeted the same way; only the access differs.
            var seen = Sim(cast).Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })))[0].ByCharacter["b"];
            var heard = Sim(cast).Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "x" }, new[] { "b" })))[0].ByCharacter["b"];

            Assert.AreEqual(Access.Witnessed, seen.Access);
            Assert.AreEqual(Access.Overheard, heard.Access);
            Assert.AreEqual(1.0, seen.Experience.Confidence, 1e-9);
            Assert.AreEqual(0.6, heard.Experience.Confidence, 1e-9);
            Assert.Less(heard.DominantIntensity, seen.DominantIntensity);
        }

        // ---- the pipeline ----

        [Test]
        public void AnEventBecomesAMemoryThatKnowsWhatItMeantAndHowMuchItStirred()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.8, ""dominant"": 0.2", @"""respect"""));

            var sim = Sim(cast);
            var outcome = sim.Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })))[0].ByCharacter["b"];

            Assert.AreEqual("disrespect", outcome.Meaning);
            Assert.AreEqual("shame", outcome.DominantEmotion);

            var memory = sim.Minds["b"].Experiences.Single();
            Assert.AreEqual("e1", memory.EventId);
            Assert.AreEqual("disrespect", memory.Meaning);
            Assert.AreEqual("shame", memory.DominantEmotion);
            Assert.AreEqual(ExperienceSource.Witnessed, memory.Source);
            Assert.Greater(memory.Salience, 0.1);
        }

        [Test]
        public void TheDominantFeelingIsTheOneThisEventStirredNotTheOneLeftOverFromBefore()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.9, ""dominant"": 0.1", @"""respect"""));
            var sim = Sim(cast);

            // A large pre-existing anger that this event does nothing to feed.
            sim.Minds["b"].Emotions.Add("anger", "someone", "respect", 0.95, traceId: 0, eventId: "long ago");

            var outcome = sim.Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })))[0].ByCharacter["b"];

            Assert.AreEqual("shame", outcome.DominantEmotion);
            Assert.AreEqual("anger", sim.Minds["b"].Emotions.Dominant.Type,
                "the old anger is still there, it just is not what this event did");
        }

        [Test]
        public void EveryFeelingCanNameTheConcernItCameFromAndWhoItIsAbout()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.2, ""dominant"": 0.9", @"""respect"""));
            var sim = Sim(cast);

            sim.Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })));

            var anger = sim.Minds["b"].Emotions.Live.Single(e => e.Type == "anger");
            Assert.AreEqual("respect", anger.Concern);
            Assert.AreEqual("a", anger.TargetId);
            Assert.IsNotEmpty(anger.Causes);
        }

        [Test]
        public void WhatAnEventMeantMovesWhatThePersonBelieves()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.8, ""dominant"": 0.2", @"""respect"""));
            var sim = Sim(cast);

            sim.Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })));

            var belief = sim.Minds["b"].Beliefs.Get("tendency", "a", "does_not_respect_me");
            Assert.AreEqual(0.2, belief.Confidence, 1e-9);
            Assert.IsNotEmpty(belief.Justifications, "a belief that moved must be able to say what moved it");
        }

        [Test]
        public void ThePersonWhoActedRecordsTheirOwnIntentionAndIsNotShamedByIt()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.9, ""dominant"": 0.9", @"""respect"""),
                Person("b", 20, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""));
            var sim = Sim(cast);

            var outcome = sim.Run(ScenarioLoader.FromJson(
                Demand("a", "b", new[] { "b" }, intent: "assert_authority")))[0].ByCharacter["a"];

            Assert.AreEqual("assert_authority", outcome.Meaning);
            Assert.IsTrue(outcome.Experience.FromOwnIntent);
            Assert.AreEqual(ExperienceSource.Self, outcome.Experience.Source);
            Assert.AreEqual("none", outcome.DominantEmotion ?? "none",
                "no rule speaks to that intention, so it stirs nothing");
        }

        // ---- what an event leaves behind ----

        [Test]
        public void AnAuthoredMemoryOnlyLandsOnSomeoneWhoWasThere()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("away", 25, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""));

            // The script credits both, but only b was in the room.
            var json = @"{
                ""id"": ""s"", ""description"": ""d"", ""characters"": [""a"", ""b"", ""away""],
                ""events"": [{
                    ""id"": ""e1"", ""day"": 1, ""order"": 1,
                    ""type"": ""action"", ""actor"": ""a"", ""target"": null,
                    ""action"": ""board_windows"", ""topic"": ""shelter"",
                    ""tone"": ""neutral"", ""directness"": ""direct"", ""valence"": ""good"", ""intent"": null,
                    ""witnesses"": [""b""], ""overhearers"": [], ""summary"": ""a boards the windows"",
                    ""ledger_effects"": [
                        { ""holder"": ""b"", ""about"": ""a"", ""entry"": ""protected_family"", ""weight"": 0.5 },
                        { ""holder"": ""away"", ""about"": ""a"", ""entry"": ""protected_family"", ""weight"": 0.5 }
                    ]
                }]
            }";

            var sim = Sim(cast);
            sim.Run(ScenarioLoader.FromJson(json));

            Assert.AreEqual(0.5, sim.Minds["b"].Ledger.Strength("a", "protected_family"), 1e-9);
            Assert.AreEqual(0.0, sim.Minds["away"].Ledger.Strength("a", "protected_family"), 1e-9);
        }

        [Test]
        public void AnAuthoredBeliefOnlyLandsOnSomeoneWhoWasThere()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("away", 25, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""));

            var json = @"{
                ""id"": ""s"", ""description"": ""d"", ""characters"": [""a"", ""b"", ""away""],
                ""events"": [{
                    ""id"": ""e1"", ""day"": 1, ""order"": 1,
                    ""type"": ""action"", ""actor"": null, ""target"": null,
                    ""action"": ""water_stops"", ""topic"": ""supplies"",
                    ""tone"": ""neutral"", ""directness"": ""direct"", ""valence"": ""bad"", ""intent"": null,
                    ""witnesses"": [""b""], ""overhearers"": [], ""summary"": ""the taps run dry"",
                    ""ledger_effects"": [],
                    ""belief_effects"": [
                        { ""holder"": ""b"", ""predicate"": ""more_knowledgeable"", ""args"": [""a"", ""survival""], ""delta"": 0.3 },
                        { ""holder"": ""away"", ""predicate"": ""more_knowledgeable"", ""args"": [""a"", ""survival""], ""delta"": 0.3 }
                    ]
                }]
            }";

            var sim = Sim(cast);
            sim.Run(ScenarioLoader.FromJson(json));

            Assert.AreEqual(0.3, sim.Minds["b"].Beliefs.Confidence("more_knowledgeable", "a", "survival"), 1e-9);
            Assert.AreEqual(0.0, sim.Minds["away"].Beliefs.Confidence("more_knowledgeable", "a", "survival"), 1e-9);
        }

        // ---- time passing ----

        [Test]
        public void FeelingsFadeBetweenEventsSoTheBackstoryLeavesMemoriesRatherThanMoods()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5, ""anxious"": 0.0", @"""respect"""),
                Person("b", 20, @"""proud"": 0.8, ""dominant"": 0.2, ""anxious"": 0.0", @"""respect"""));

            var json = @"{
                ""id"": ""s"", ""description"": ""d"", ""characters"": [""a"", ""b""],
                ""events"": [
                    { ""id"": ""e1"", ""day"": 1, ""order"": 1, ""type"": ""speech"", ""actor"": ""a"", ""target"": ""b"",
                      ""act"": ""demand"", ""topic"": ""who_decides"", ""tone"": ""raised"", ""directness"": ""direct"",
                      ""valence"": ""neutral"", ""intent"": null, ""witnesses"": [""b""], ""overhearers"": [],
                      ""summary"": ""a tells b how it is"", ""ledger_effects"": [] },
                    { ""id"": ""e2"", ""day"": 3, ""order"": 2, ""type"": ""action"", ""actor"": ""a"", ""target"": null,
                      ""action"": ""count_supplies"", ""topic"": ""supplies"", ""tone"": ""neutral"", ""directness"": ""direct"",
                      ""valence"": ""neutral"", ""intent"": null, ""witnesses"": [""b""], ""overhearers"": [],
                      ""summary"": ""a counts the tins"", ""ledger_effects"": [] }
                ]
            }";

            var sim = Sim(cast);
            var outcomes = sim.Run(ScenarioLoader.FromJson(json));

            var shameAtTheTime = outcomes[0].ByCharacter["b"].DominantIntensity;
            var shameLater = sim.Minds["b"].Emotions.Intensity("shame");

            Assert.Greater(shameAtTheTime, 0.0);
            Assert.Less(shameLater, shameAtTheTime, "the feeling fades");
            Assert.AreEqual(0.2, sim.Minds["b"].Beliefs.Confidence("tendency", "a", "does_not_respect_me"), 1e-9);
            Assert.AreEqual(2, sim.Minds["b"].Experiences.Count, "the memories do not fade");
        }

        // ---- the trace ----

        [Test]
        public void AFeelingCanBeWalkedBackToTheThingThatHappened()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.8, ""dominant"": 0.2", @"""respect"""));
            var sim = Sim(cast);

            sim.Run(ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" })));

            var shame = sim.Minds["b"].Emotions.Live.Single(e => e.Type == "shame");
            var chain = sim.Trace.Chain(shame.Causes[0]).ToList();

            Assert.GreaterOrEqual(chain.Count, 3, "a feeling that cannot explain itself is not usable evidence");
            CollectionAssert.Contains(chain.Select(r => r.Kind).ToArray(), TraceKind.Appraisal);
            CollectionAssert.Contains(chain.Select(r => r.Kind).ToArray(), TraceKind.Interpretation);
            CollectionAssert.Contains(chain.Select(r => r.Kind).ToArray(), TraceKind.Event);

            var why = sim.Trace.Why(shame.Causes[0]);
            StringAssert.Contains("disrespect", why);
            StringAssert.Contains("how it is", why);
        }

        [Test]
        public void RunningTheSameScriptTwiceGivesTheSameResultEveryTime()
        {
            var cast = Cast(
                Person("a", 30, @"""proud"": 0.5, ""dominant"": 0.5", @"""respect"""),
                Person("b", 20, @"""proud"": 0.8, ""dominant"": 0.2", @"""respect"""));
            var script = ScenarioLoader.FromJson(Demand("a", "b", new[] { "b" }));

            var first = Sim(cast).Run(script)[0].ByCharacter["b"];
            var second = Sim(cast).Run(script)[0].ByCharacter["b"];

            Assert.AreEqual(first.Meaning, second.Meaning);
            Assert.AreEqual(first.DominantEmotion, second.DominantEmotion);
            Assert.AreEqual(first.DominantIntensity, second.DominantIntensity, 1e-12);
        }
    }
}
