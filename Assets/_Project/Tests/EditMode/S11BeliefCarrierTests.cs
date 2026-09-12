using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The stage the diagnosis found skipped. The night reached feeling, and
    /// feeling fades. It never reached belief, which is the one stage of the
    /// pipeline that lasts. These tests describe the smallest link: seeing who
    /// the food went to becomes a belief, and that belief changes what later
    /// events mean to the person who holds it.
    /// </summary>
    public class S11BeliefCarrierTests
    {
        static Scenario001Content _content;

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        static double Answerable(Scenario001Run run, string holder, string about)
            => run.Minds[holder].Beliefs.Confidence("answerable_for", about, "missing_can");

        [Test]
        public void WhoeverSawWhereTheFoodWentBelievesItAndNobodyElseDoes()
        {
            var ate = Scenario001.Prepare(_content, "mara_ate_it", 1);
            Assert.Greater(Answerable(ate, "mara", "mara"), 0.5, "she saw herself do it");
            foreach (var other in new[] { "daniel", "elena", "leo" })
                Assert.AreEqual(0.0, Answerable(ate, other, "mara"), other + " was asleep and cannot know");

            var fed = Scenario001.Prepare(_content, "elena_fed_mara", 1);
            Assert.Greater(Answerable(fed, "elena", "elena"), 0.5, "she knows what she did");
            Assert.Greater(Answerable(fed, "mara", "elena"), 0.5, "and Mara watched her do it");
            Assert.AreEqual(0.0, Answerable(fed, "mara", "mara"), "being given it is not being answerable for it");
            Assert.AreEqual(0.0, Answerable(fed, "daniel", "elena"));

            var none = Scenario001.Prepare(_content, "miscount", 1);
            foreach (var holder in _content.Cast.Keys)
            foreach (var about in _content.Cast.Keys)
                Assert.AreEqual(0.0, Answerable(none, holder, about), "nothing happened, so nobody believes anything about it");
        }

        [Test]
        public void TheBeliefCanSayWhichNightItCameFrom()
        {
            var run = Scenario001.Prepare(_content, "daniel_ate_it", 1);
            var belief = run.Minds["daniel"].Beliefs.Get("answerable_for", "daniel", "missing_can");

            Assert.IsNotEmpty(belief.Justifications);
            Assert.IsTrue(belief.Justifications.Any(j => run.Trace.Chain(j).Any(r => r.EventId == "n01")),
                "the belief should lead back to the night it was formed in");
        }

        [Test]
        public void TheSameSearchMeansSomethingDifferentToThePersonWhoKnowsTheyAreTheReason()
        {
            // One event, perceived by two people in the same room: one who took
            // the food in the night and one who did not. Nothing else differs
            // between them except who they are.
            foreach (var culprit in new[] { "daniel_ate_it", "mara_ate_it" })
            {
                var run = Scenario001.Prepare(_content, culprit, 1);
                var guilty = culprit.StartsWith("daniel") ? "daniel" : "mara";
                var innocent = guilty == "daniel" ? "mara" : "daniel";

                var search = new WorldEvent(
                    "probe-search", _content.Morning.Day, 5000, EventKind.Action, "leo", null,
                    null, "search_belongings", "missing_can", "neutral", "direct", "neutral", null,
                    "Leo goes through the kitchen cupboards.",
                    new[] { guilty, innocent }, new string[0], new List<LedgerEffect>(), null, 10);

                var outcome = run.Simulation.Apply(search);

                Assert.AreEqual("threat", outcome.ByCharacter[guilty].Meaning,
                    culprit + ": to " + guilty + " the search is closing in");
                Assert.AreNotEqual("threat", outcome.ByCharacter[innocent].Meaning,
                    culprit + ": to " + innocent + " it is only a search");

                var chain = run.Trace.Chain(outcome.ByCharacter[guilty].InterpretationTraceId);
                var reading = run.Trace.Get(outcome.ByCharacter[guilty].InterpretationTraceId);
                StringAssert.Contains("answerable_for(" + guilty + ",missing_can)", reading.Data["rules"],
                    "the reading must name the belief that coloured it");
            }
        }

        [Test]
        public void AReadingColouredByABeliefCanBeWalkedBackToWhatFormedTheBelief()
        {
            // Found by the S1.1 experiment. A reading used to rest only on having
            // been in the room, so a change in what somebody wanted could say in
            // words that a belief had coloured it, and could not be walked back
            // to the night the belief came from. Readings and feelings now rest on
            // the records their weights drew on, as wants already did.
            var run = Scenario001.Prepare(_content, "mara_ate_it", 1);

            var search = new WorldEvent(
                "probe-walk", _content.Morning.Day, 5002, EventKind.Action, "leo", null,
                null, "search_belongings", "missing_can", "neutral", "direct", "neutral", null,
                "Leo goes through the kitchen cupboards.",
                new[] { "mara" }, new string[0], new List<LedgerEffect>(), null, 10);

            var outcome = run.Simulation.Apply(search).ByCharacter["mara"];
            Assert.AreEqual("threat", outcome.Meaning);

            Assert.IsTrue(run.Trace.Chain(outcome.InterpretationTraceId).Any(r => r.EventId == "n01"),
                "the threat reading does not lead back to the night that made it a threat");

            var fear = outcome.Emotions.First(e => e.Type == "fear");
            Assert.IsTrue(run.Trace.Chain(fear.TraceId).Any(r => r.EventId == "n01"),
                "and neither does the fear it stirred");
        }

        [Test]
        public void NobodyIsThreatenedByTheirOwnSearch()
        {
            var run = Scenario001.Prepare(_content, "daniel_ate_it", 1);

            var ownSearch = new WorldEvent(
                "probe-own", _content.Morning.Day, 5001, EventKind.Action, "daniel", null,
                null, "search_belongings", "missing_can", "neutral", "direct", "neutral", null,
                "Daniel goes through the kitchen cupboards.",
                new[] { "mara" }, new string[0], new List<LedgerEffect>(), null, 10);

            var outcome = run.Simulation.Apply(ownSearch);
            Assert.AreNotEqual("threat", outcome.ByCharacter["daniel"].Meaning,
                "a search you are doing yourself is not something closing in on you");
        }
    }
}
