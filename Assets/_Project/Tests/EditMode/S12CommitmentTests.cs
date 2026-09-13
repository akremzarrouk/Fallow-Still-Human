using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// S1.2: once somebody has started something, what stops them.
    ///
    /// The claim is narrow. A person carries on with what they chose unless it
    /// finishes, becomes impossible, or something happens to them that matters
    /// enough to think again. What they were already feeling is not new, and
    /// thinking again is not the same as giving up.
    /// </summary>
    public class S12CommitmentTests
    {
        static Scenario001Content _content;

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        static double Threshold => _content.Rules.Deciding.InterruptIntensity;

        /// <summary>
        /// A morning stepped until the person is part way through something
        /// that is not a walk, with minutes of it still to go.
        /// </summary>
        static Scenario001Run Busy(string variant, string who, ulong seed)
        {
            var run = Scenario001.Prepare(_content, variant, seed);
            for (var i = 0; i < 60; i++)
            {
                run.Morning.Step();
                var doing = run.Morning.Doing(who);
                // Already under way, so that starting again from the beginning
                // and carrying on can be told apart.
                if (doing.HasValue && doing.Value.Action.Kind != ActionKind.GoTo &&
                    doing.Value.MinutesLeft >= 3 && doing.Value.MinutesLeft < doing.Value.Action.Duration)
                    return run;
            }
            return null;
        }

        static WorldEvent Something(Scenario001Run run, string id, string actor, string action, string topic, string valence, string summary, params string[] witnesses)
            => new WorldEvent(id, _content.Morning.Day, 9000, EventKind.Action, actor, null,
                null, action, topic, "neutral", "direct", valence, null, summary,
                witnesses, new string[0], new List<LedgerEffect>(), null, run.World.Minute);

        [Test]
        public void WhatYouWereAlreadyFeelingIsNotAReasonToStopWhatYouAreDoing()
        {
            var checkedAny = 0;
            for (ulong seed = 1; seed <= 10; seed++)
            {
                var run = Busy("mara_ate_it", "mara", seed);
                if (run == null) continue;

                var standing = run.Minds["mara"].Emotions.Dominant;
                if (standing == null || standing.Intensity < Threshold) continue;

                var before = run.Morning.Doing("mara").Value;
                var others = run.World.WithMe("mara");
                var actor = others.Count > 0 ? others[0] : "leo";

                var outcome = run.Morning.Happen(Something(run, "probe-mild-" + seed, actor, "enter_room", null, "neutral",
                    "Somebody comes into the room.", "mara"));
                var stirred = outcome.ByCharacter["mara"].DominantIntensity;
                if (stirred >= Threshold) continue;

                checkedAny++;
                var after = run.Morning.Doing("mara");
                Assert.IsTrue(after.HasValue,
                    "seed " + seed + ": already feeling " + standing + ", she was stopped by something that stirred only " +
                    stirred.ToString("0.00"));
                Assert.IsTrue(after.Value.Action.SameAs(before.Action));
                Assert.AreEqual(before.MinutesLeft, after.Value.MinutesLeft);
            }

            TestContext.WriteLine("checked on " + checkedAny + " seeds");
            Assert.Greater(checkedAny, 0, "never found her busy, upset, and passed by something that stirred little");
        }

        [Test]
        public void SomethingThatLandsHardStillMakesYouThinkAgain()
        {
            var checkedAny = 0;
            for (ulong seed = 1; seed <= 10; seed++)
            {
                var run = Busy("mara_ate_it", "mara", seed);
                if (run == null) continue;

                // Somebody going through the room she is standing in, looking for
                // what she took. The belief she formed in the night is what makes
                // this a threat to her; nothing here says it should.
                var searcher = run.World.Inhabitants.First(id => id != "mara");
                var outcome = run.Morning.Happen(Something(run, "probe-hard-" + seed, searcher, "search_belongings", "missing_can", "neutral",
                    "Somebody goes through the room, looking for the can.", "mara"));
                var stirred = outcome.ByCharacter["mara"].DominantIntensity;
                if (stirred < Threshold) continue;

                checkedAny++;
                Assert.IsFalse(run.Morning.Doing("mara").HasValue,
                    "seed " + seed + ": something stirred " + stirred.ToString("0.00") + " in her and she did not stop to think");
                Assert.IsTrue(run.Morning.Interruptions.Any(x => x.CharacterId == "mara" && x.EventId == "probe-hard-" + seed));
            }

            TestContext.WriteLine("checked on " + checkedAny + " seeds");
            Assert.Greater(checkedAny, 0, "the search never landed hard enough on her to test anything");
        }

        [Test]
        public void ThinkingAgainAndChoosingTheSameThingCarriesOnRatherThanStartingOver()
        {
            var carriedOn = 0;
            var changed = 0;

            for (ulong seed = 1; seed <= 20; seed++)
            {
                var run = Busy("mara_ate_it", "mara", seed);
                if (run == null) continue;

                var before = run.Morning.Doing("mara").Value;
                var searcher = run.World.Inhabitants.First(id => id != "mara");
                var outcome = run.Morning.Happen(Something(run, "probe-again-" + seed, searcher, "search_belongings", "missing_can", "neutral",
                    "Somebody goes through the room, looking for the can.", "mara"));
                if (outcome.ByCharacter["mara"].DominantIntensity < Threshold) continue;

                run.Morning.Step();
                var decided = run.Result.Actions.Last(a => a.CharacterId == "mara");
                var now = run.Morning.Doing("mara");

                if (decided.Action.SameAs(before.Action))
                {
                    carriedOn++;
                    Assert.IsTrue(now.HasValue);
                    Assert.AreEqual(before.MinutesLeft, now.Value.MinutesLeft,
                        "seed " + seed + ": she chose to carry on with " + before.Action + " and started it again from the beginning");
                }
                else
                {
                    changed++;
                }
            }

            TestContext.WriteLine("carried on " + carriedOn + ", changed course " + changed);
            Assert.Greater(carriedOn + changed, 0);
        }

        /// <summary>
        /// Somebody part way through a walk they set out on for a reason, found by
        /// stepping mornings until it happens. Returns the seed and person so the
        /// same moment can be prepared again.
        /// </summary>
        static (Scenario001Run run, string who, ulong seed, int steps)? Walking(string variant, ulong fromSeed)
        {
            for (var seed = fromSeed; seed < fromSeed + 30; seed++)
            {
                var run = Scenario001.Prepare(_content, variant, seed);
                for (var i = 0; i < 90; i++)
                {
                    run.Morning.Step();
                    foreach (var id in run.World.Inhabitants)
                    {
                        var doing = run.Morning.Doing(id);
                        if (doing.HasValue && doing.Value.Action.Kind == ActionKind.GoTo && doing.Value.MinutesLeft >= 2 &&
                            run.Morning.Intends(id) != null)
                            return (run, id, seed, i + 1);
                    }
                }
            }
            return null;
        }

        static Scenario001Run Again(string variant, ulong seed, int steps)
        {
            var run = Scenario001.Prepare(_content, variant, seed);
            for (var i = 0; i < steps; i++) run.Morning.Step();
            return run;
        }

        [Test]
        public void AWalkForAReasonSurvivesWhatDoesNotLandAndIsThoughtAboutAgainWhenSomethingDoes()
        {
            const string variant = "daniel_ate_it";
            var found = Walking(variant, 1);
            Assert.IsTrue(found.HasValue, "nobody ever walked anywhere for a reason");
            var (first, who, seed, steps) = found.Value;
            var intention = first.Morning.Intends(who);
            var others = first.World.Inhabitants.Where(id => id != who).ToList();

            // Something that does not land: they keep walking, and arrive still
            // carrying the reason they set out with.
            var mild = Again(variant, seed, steps);
            var passing = mild.Morning.Happen(Something(mild, "probe-walk-mild", others[0], "enter_room", null, "neutral", "Somebody comes in.", who));
            Assume.That(passing.ByCharacter[who].DominantIntensity, Is.LessThan(Threshold));
            Assert.IsTrue(mild.Morning.Doing(who).HasValue, "a moment that stirred nothing stopped them mid-walk");

            Decision arrival = null;
            mild.Morning.Decided = m => { if (m.CharacterId == who && arrival == null) arrival = m.Decision; };
            for (var i = 0; i < 10 && arrival == null; i++) mild.Morning.Step();
            Assert.IsNotNull(arrival);
            Assert.IsNotNull(arrival.Holding, "they arrived having forgotten why they came");
            Assert.AreEqual(intention.MotiveKey, arrival.Holding.MotiveKey);

            // Something that does land, tried with each act the event rules read
            // as a slight or a threat until one lands on this person: they stop,
            // and think again from the beginning, without the reason for the walk.
            string[][] hard =
            {
                new[] { "observe", null, "watches them" },
                new[] { "search_belongings", "missing_can", "goes through things, looking for the can" }
            };
            var landed = false;
            foreach (var h in hard)
            foreach (var actor in others)
            {
                if (landed) break;
                var run = Again(variant, seed, steps);
                var e = new WorldEvent("probe-walk-hard", _content.Morning.Day, 9000, EventKind.Action, actor,
                    h[0] == "observe" ? who : null, null, h[0], h[1], "neutral", "direct", "neutral", null,
                    "Somebody " + h[2] + ".", new[] { who }, new string[0], new List<LedgerEffect>(), null, run.World.Minute);
                var outcome = run.Morning.Happen(e);
                if (outcome.ByCharacter[who].DominantIntensity < Threshold) continue;

                landed = true;
                Assert.IsFalse(run.Morning.Doing(who).HasValue, "something landed and they walked on as if it had not");

                Decision next = null;
                run.Morning.Decided = m => { if (m.CharacterId == who && next == null) next = m.Decision; };
                run.Morning.Step();
                Assert.IsNotNull(next);
                Assert.IsNull(next.Holding, "they were stopped, and still weighed only the reason for the walk");
                TestContext.WriteLine(who + " walking for " + intention.MotiveKey + " was stopped by '" + e.Summary + "' (" +
                                      outcome.ByCharacter[who].Dominant + ") and chose " + next.Chosen);
            }

            if (!landed) Assert.Inconclusive("nothing tried landed hard enough on " + who + " to stop them");
        }

        [Test]
        public void AnIntentionNarrowsWhatIsWeighedButLeavesATieBetweenWaysOfServingItToTheSeed()
        {
            // Two ways of serving what they came for, equally good. The intention
            // does not pick between them; that is still genuinely open.
            var rules = Arriving();
            rules.Proposals = rules.Proposals.Concat(new[]
            {
                new Fallow.Core.Rules.ProposalRule { Id = "look_at_the_shelf", Motive = "find_out", Action = "check_pantry", Targeting = "none", Fit = 0.8 }
            }).ToList();
            rules.Costs = new List<Fallow.Core.Rules.CostRule>();

            var chosen = new HashSet<string>();
            for (ulong s = 1; s <= 40; s++)
            {
                var d = new Deliberator(rules).Decide(new Mind(Bench.Person("daniel")), Bench.Standing("daniel", "kitchen"),
                    new List<Motive> { new Motive("find_out", null, 0.6, null, null), new Motive("keep_peace", null, 0.9, null, null) },
                    4, new Rng(s), new Fallow.Core.Tracing.TraceLog(), 0, CameToLook);
                Assert.AreEqual(Commitment.Held, d.Commitment);
                Assert.AreEqual(Resolution.Ambiguous, d.Resolution);
                chosen.Add(d.Chosen.Key);
            }
            Assert.Greater(chosen.Count, 1, "the intention settled a tie that was genuinely open");
        }

        // ---- an intention carried across a walk ----

        static Fallow.Core.Rules.RuleSet Arriving(double searchCost = 0.0)
        {
            var rules = new Fallow.Core.Rules.RuleSet
            {
                Proposals = new List<Fallow.Core.Rules.ProposalRule>
                {
                    new Fallow.Core.Rules.ProposalRule { Id = "look_here", Motive = "find_out", Action = "search_room", Targeting = "none", Fit = 0.8 },
                    new Fallow.Core.Rules.ProposalRule { Id = "look_elsewhere", Motive = "find_out", Action = "observe", Targeting = "each_present", Fit = 0.4 },
                    new Fallow.Core.Rules.ProposalRule { Id = "eat_it", Motive = "get_food", Action = "eat", Targeting = "none", Fit = 1.0 },
                    new Fallow.Core.Rules.ProposalRule { Id = "sit_quiet", Motive = "keep_peace", Action = "wait", Targeting = "none", Fit = 1.0 }
                },
                Costs = new List<Fallow.Core.Rules.CostRule>
                {
                    new Fallow.Core.Rules.CostRule { Id = "searching", Action = "search_room", Base = searchCost == 0.0 ? 0.001 : searchCost }
                },
                Deciding = Bench.Dynamics()
            };
            return rules;
        }

        static readonly Intention CameToLook = new Intention("find_out", "find_out",
            new ActionOption(ActionKind.GoTo, destinationRoomId: "bedroom", duration: 4), 3, 0);

        static Decision Arrive(Fallow.Core.Rules.RuleSet rules, Intention holding, params Motive[] motives)
            => new Deliberator(rules).Decide(new Mind(Bench.Person("daniel")), Bench.Standing("daniel", "bedroom"),
                motives.ToList(), 4, new Rng(1), new Fallow.Core.Tracing.TraceLog(), 0, holding);

        [Test]
        public void ArrivingSomewhereForAReasonYouDoWhatYouCameFor()
        {
            var motives = new[] { new Motive("find_out", null, 0.6, null, null), new Motive("keep_peace", null, 0.9, null, null) };

            var fresh = Arrive(Arriving(), null, motives);
            var holding = Arrive(Arriving(), CameToLook, motives);

            Assert.AreEqual(ActionKind.Wait, fresh.Chosen.Kind, "without the reason, sitting quiet is what this person would prefer");
            Assert.AreEqual(ActionKind.SearchRoom, holding.Chosen.Kind, "they came here to look, and on arrival forgot why");
            Assert.AreEqual(Commitment.Held, holding.Commitment);
            Assert.AreEqual("find_out", holding.Forms.MotiveKey, "an intention still being served stays the reason");
        }

        [Test]
        public void HoldingAnIntentionAddsNothingToAnyScore()
        {
            // Commitment narrows what is being decided between. It never makes
            // the intended option worth more, so it cannot be tuned into a bonus.
            var motives = new[] { new Motive("find_out", null, 0.6, null, null), new Motive("keep_peace", null, 0.9, null, null) };

            var fresh = Arrive(Arriving(), null, motives);
            var holding = Arrive(Arriving(), CameToLook, motives);

            foreach (var r in fresh.Ranked)
                Assert.AreEqual(r.Score, holding.Ranked.First(x => x.Option.SameAs(r.Option)).Score, 1e-12, r.Option.Key);

            var record = new Fallow.Core.Tracing.TraceLog();
            var traced = new Deliberator(Arriving()).Decide(new Mind(Bench.Person("daniel")), Bench.Standing("daniel", "bedroom"),
                motives.ToList(), 4, new Rng(1), record, 0, CameToLook);
            var data = record.Get(traced.TraceId).Data;
            StringAssert.Contains("find_out, held", data["intention"]);
            StringAssert.Contains("wait", data["without_it"], "the trace says what would have won without the intention");
        }

        [Test]
        public void AnIntentionLapsesWhenTheWantBehindItHasGone()
        {
            var d = Arrive(Arriving(), CameToLook, new Motive("keep_peace", null, 0.9, null, null));
            Assert.AreEqual(Commitment.NoLongerWanted, d.Commitment);
            Assert.AreEqual(ActionKind.Wait, d.Chosen.Kind);
        }

        [Test]
        public void AnIntentionLapsesWhenNothingHereCanServeIt()
        {
            // Walked here hungry, and there is no food in this room.
            var hungry = new Intention("get_food", "get_food", new ActionOption(ActionKind.GoTo, destinationRoomId: "bedroom"), 3, 0);
            var d = Arrive(Arriving(), hungry, new Motive("get_food", null, 0.9, null, null), new Motive("keep_peace", null, 0.3, null, null));
            Assert.AreEqual(Commitment.Impossible, d.Commitment);
            Assert.AreEqual(ActionKind.Wait, d.Chosen.Kind);
        }

        [Test]
        public void AnIntentionLapsesWhenServingItHereCostsMoreThanItIsWorth()
        {
            // Looking was worth 0.48 and costs 0.60 in this room.
            var d = Arrive(Arriving(searchCost: 0.6), CameToLook,
                new Motive("find_out", null, 0.6, null, null), new Motive("keep_peace", null, 0.3, null, null));
            Assert.AreEqual(Commitment.NotWorthIt, d.Commitment);
            Assert.AreEqual(ActionKind.Wait, d.Chosen.Kind);
        }
    }
}
