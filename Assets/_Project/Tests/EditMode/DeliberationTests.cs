using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>Weighing what to do, and what randomness is and is not for.</summary>
    public class DeliberationTests
    {
        static RuleSet Rules(
            IEnumerable<MotivationRule> motivation = null,
            IEnumerable<ProposalRule> proposals = null,
            IEnumerable<CostRule> costs = null,
            double band = 0.08)
        {
            var d = Bench.Dynamics();
            d.AmbiguityBand = band;
            return new RuleSet
            {
                Motivation = (motivation ?? Enumerable.Empty<MotivationRule>()).ToList(),
                Proposals = (proposals ?? Enumerable.Empty<ProposalRule>()).ToList(),
                Costs = (costs ?? Enumerable.Empty<CostRule>()).ToList(),
                Deciding = d
            };
        }

        static Decision Decide(
            RuleSet rules, Mind mind, Percept percept, IEnumerable<Motive> motives, ulong seed = 1,
            TraceLog trace = null)
            => new Deliberator(rules).Decide(
                mind, percept, motives.ToList(), 4, new Rng(seed), trace ?? new TraceLog(), 0);

        [Test]
        public void TheOptionThatServesWhatIsWantedMostWins()
        {
            var rules = Rules(proposals: new[]
            {
                new ProposalRule { Id = "eat", Motive = "get_food", Action = "eat", Targeting = Targeting.None, Fit = 1.0 },
                new ProposalRule { Id = "sit", Motive = "keep_peace", Action = "wait", Targeting = Targeting.None, Fit = 1.0 }
            });

            var decision = Decide(rules, new Mind(Bench.Person("leo")), Bench.Standing("leo"), new[]
            {
                new Motive("get_food", null, 0.9, null, null),
                new Motive("keep_peace", null, 0.2, null, null)
            });

            Assert.AreEqual(ActionKind.Eat, decision.Chosen.Kind);
            Assert.AreEqual(Resolution.Clear, decision.Resolution);
        }

        [Test]
        public void TwoWantsPullingTheSameWayAddUp()
        {
            var rules = Rules(proposals: new[]
            {
                new ProposalRule { Id = "a", Motive = "find_out", Action = "check_pantry", Targeting = Targeting.None, Fit = 0.5 },
                new ProposalRule { Id = "b", Motive = "guard_supplies", Action = "check_pantry", Targeting = Targeting.None, Fit = 0.5 },
                new ProposalRule { Id = "c", Motive = "keep_peace", Action = "wait", Targeting = Targeting.None, Fit = 0.8 }
            });

            var decision = Decide(rules, new Mind(Bench.Person("leo")), Bench.Standing("leo"), new[]
            {
                new Motive("find_out", null, 0.6, null, null),
                new Motive("guard_supplies", null, 0.6, null, null),
                new Motive("keep_peace", null, 0.7, null, null)
            });

            Assert.AreEqual(ActionKind.CheckPantry, decision.Chosen.Kind,
                "two half reasons outweigh one whole one");
        }

        [Test]
        public void TheSameWantGivesDifferentPeopleDifferentAnswersBecauseOfWhatItCostsThem()
        {
            var rules = Rules(
                proposals: new[]
                {
                    new ProposalRule { Id = "eat", Motive = "get_food", Action = "eat", Targeting = Targeting.None, Fit = 1.0 },
                    new ProposalRule { Id = "sit", Motive = "get_food", Action = "wait", Targeting = Targeting.None, Fit = 0.5 }
                },
                costs: new[]
                {
                    new CostRule
                    {
                        Id = "taking_it",
                        Action = "eat",
                        Base = 0.0,
                        ScaledBy = new[] { new Scaler { Kind = ScalerKind.Value, Name = "fairness", Factor = 1.0 } }
                    }
                });

            var motive = new[] { new Motive("get_food", null, 0.8, null, null) };

            var scrupulous = new Mind(Bench.Person("leo", values: new[] { "fairness" }));
            var not = new Mind(Bench.Person("daniel", values: new[] { "control" }));

            Assert.AreEqual(ActionKind.Wait, Decide(rules, scrupulous, Bench.Standing("leo"), motive).Chosen.Kind);
            Assert.AreEqual(ActionKind.Eat, Decide(rules, not, Bench.Standing("daniel"), motive).Chosen.Kind);
        }

        [Test]
        public void AClearBestAnswerIsTakenWithNothingRandomAboutIt()
        {
            var rules = Rules(proposals: new[]
            {
                new ProposalRule { Id = "eat", Motive = "get_food", Action = "eat", Targeting = Targeting.None, Fit = 1.0 }
            });

            var motive = new[] { new Motive("get_food", null, 0.9, null, null) };
            var mind = new Mind(Bench.Person("leo"));

            var chosen = new HashSet<string>(StringComparer.Ordinal);
            for (ulong seed = 1; seed <= 40; seed++)
                chosen.Add(Decide(rules, mind, Bench.Standing("leo"), motive, seed).Chosen.Key);

            Assert.AreEqual(1, chosen.Count, "the seed must not touch a choice that was not close");
            Assert.AreEqual("eat", chosen.Single());
        }

        [Test]
        public void WhenTwoThingsAreEquallyGoodTheSeedSettlesItAndTheTraceSaysSo()
        {
            var rules = Rules(proposals: new[]
            {
                new ProposalRule { Id = "a", Motive = "m", Action = "eat", Targeting = Targeting.None, Fit = 1.0 },
                new ProposalRule { Id = "b", Motive = "m", Action = "check_pantry", Targeting = Targeting.None, Fit = 1.0 }
            });

            var motive = new[] { new Motive("m", null, 0.7, null, null) };
            var mind = new Mind(Bench.Person("leo"));

            var chosen = new HashSet<string>(StringComparer.Ordinal);
            Decision last = null;

            for (ulong seed = 1; seed <= 60; seed++)
            {
                last = Decide(rules, mind, Bench.Standing("leo"), motive, seed);
                chosen.Add(last.Chosen.Key);
            }

            Assert.Greater(chosen.Count, 1, "a genuine tie should not always fall the same way");
            Assert.AreEqual(Resolution.Ambiguous, last.Resolution);
            Assert.AreEqual(2, last.Tied.Count);
        }

        [Test]
        public void ADifferenceBiggerThanTheBandIsAPreferenceAndIsNotGambledOn()
        {
            var rules = Rules(
                proposals: new[]
                {
                    new ProposalRule { Id = "a", Motive = "m", Action = "eat", Targeting = Targeting.None, Fit = 1.0 },
                    new ProposalRule { Id = "b", Motive = "m", Action = "check_pantry", Targeting = Targeting.None, Fit = 0.5 }
                },
                band: 0.05);

            var motive = new[] { new Motive("m", null, 0.8, null, null) };
            var mind = new Mind(Bench.Person("leo"));

            for (ulong seed = 1; seed <= 40; seed++)
            {
                var d = Decide(rules, mind, Bench.Standing("leo"), motive, seed);
                Assert.AreEqual(ActionKind.Eat, d.Chosen.Kind);
                Assert.AreEqual(Resolution.Clear, d.Resolution);
            }
        }

        [Test]
        public void TheSameSeedAndTheSameStateGiveTheSameAnswerEveryTime()
        {
            var rules = Rules(proposals: new[]
            {
                new ProposalRule { Id = "a", Motive = "m", Action = "eat", Targeting = Targeting.None, Fit = 1.0 },
                new ProposalRule { Id = "b", Motive = "m", Action = "check_pantry", Targeting = Targeting.None, Fit = 1.0 },
                new ProposalRule { Id = "c", Motive = "m", Action = "wait", Targeting = Targeting.None, Fit = 1.0 }
            });

            var motive = new[] { new Motive("m", null, 0.7, null, null) };
            var mind = new Mind(Bench.Person("leo"));

            for (ulong seed = 1; seed <= 20; seed++)
            {
                var first = Decide(rules, mind, Bench.Standing("leo"), motive, seed).Chosen.Key;
                var again = Decide(rules, mind, Bench.Standing("leo"), motive, seed).Chosen.Key;
                Assert.AreEqual(first, again);
            }
        }

        [Test]
        public void WhatWasWeighedAndWhatWonAreBothOnTheRecord()
        {
            var rules = Rules(
                proposals: new[]
                {
                    new ProposalRule { Id = "eat_it", Motive = "get_food", Action = "eat", Targeting = Targeting.None, Fit = 1.0 },
                    new ProposalRule { Id = "sit_tight", Motive = "keep_peace", Action = "wait", Targeting = Targeting.None, Fit = 1.0 }
                },
                costs: new[]
                {
                    new CostRule { Id = "taking_it", Action = "eat", Base = 0.1 }
                });

            var trace = new TraceLog();
            var motives = new List<Motive>
            {
                new Motive("get_food", null, 0.9, null, null)
                    { TraceId = trace.Add(TraceKind.Motive, "leo", null, "wants food") },
                new Motive("keep_peace", null, 0.2, null, null)
                    { TraceId = trace.Add(TraceKind.Motive, "leo", null, "wants quiet") }
            };

            var decision = Decide(rules, new Mind(Bench.Person("leo")), Bench.Standing("leo"), motives, 1, trace);
            var record = trace.Get(decision.TraceId);

            Assert.AreEqual(TraceKind.Deliberation, record.Kind);
            StringAssert.Contains("eat", record.Data["chose"]);
            StringAssert.Contains("get_food", record.Data["serves"]);
            StringAssert.Contains("taking_it", record.Data["against"]);
            StringAssert.Contains("wait", record.Data["options"], "what it beat is on the record too");

            // And the chain reaches back through the wants to what raised them.
            var chain = trace.Chain(decision.TraceId).Select(r => r.Kind).ToList();
            CollectionAssert.Contains(chain, TraceKind.Motive);
        }

        [Test]
        public void WithNothingWantedAtAllAndNothingCostingAnythingTheChoiceIsOpen()
        {
            // Worth stating plainly rather than hiding: when every option is
            // worth exactly the same, there is no preference to express, and the
            // seed settles it. Whatever comes out is flagged as having had
            // nothing behind it.
            var decision = Decide(Rules(), new Mind(Bench.Person("leo")), Bench.Standing("leo"), new Motive[0]);

            Assert.IsNotNull(decision.Chosen);
            Assert.AreEqual(Resolution.Ambiguous, decision.Resolution);
            Assert.IsTrue(decision.Ranked.All(r => r.Score == 0.0));
        }

        [Test]
        public void WithNothingWantedAPersonStaysPutBecauseMovingCostsSomethingAndStayingDoesNot()
        {
            // Which is what actually happens, because the shipped rules price
            // getting up. Doing nothing is the only thing that is free.
            var rules = Rules(costs: new[]
            {
                new CostRule { Id = "getting_up", Action = "go_to", Base = 0.12 },
                new CostRule { Id = "opening_it", Action = "check_pantry", Base = 0.08 },
                new CostRule { Id = "taking_it", Action = "eat", Base = 0.15 }
            });

            for (ulong seed = 1; seed <= 20; seed++)
            {
                var decision = Decide(rules, new Mind(Bench.Person("leo")), Bench.Standing("leo"), new Motive[0], seed);

                Assert.AreNotEqual(ActionKind.GoTo, decision.Chosen.Kind,
                    "nobody walks into another room for no reason at all");
                Assert.AreNotEqual(ActionKind.Eat, decision.Chosen.Kind);
                Assert.AreNotEqual(ActionKind.CheckPantry, decision.Chosen.Kind);
            }
        }

        [Test]
        public void EveryOptionIsPricedEvenTheOnesThatLose()
        {
            var rules = Rules(
                proposals: new[]
                {
                    new ProposalRule { Id = "a", Motive = "m", Action = "eat", Targeting = Targeting.None, Fit = 1.0 }
                },
                costs: new[]
                {
                    new CostRule { Id = "walking", Action = "go_to", Base = 0.2 }
                });

            var decision = Decide(rules, new Mind(Bench.Person("leo")), Bench.Standing("leo"),
                new[] { new Motive("m", null, 0.5, null, null) });

            var walking = decision.Ranked.First(r => r.Option.Kind == ActionKind.GoTo);
            Assert.AreEqual(0.2, walking.Cost, 1e-9);
            Assert.AreEqual(-0.2, walking.Score, 1e-9);
        }
    }
}
