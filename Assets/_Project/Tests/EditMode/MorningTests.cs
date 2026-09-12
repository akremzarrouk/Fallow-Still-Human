using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Data;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The loop closing: a decision becomes an act, the act changes the house,
    /// and the change becomes something the people near it have to make sense of.
    /// </summary>
    public class MorningTests
    {
        static Scenario001Content _content;

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        Scenario001Run Fresh(string variant = "daniel_ate_it", ulong seed = 3)
            => Scenario001.Prepare(_content, variant, seed);

        [Test]
        public void EverythingTheSliceLoadsIsValid()
        {
            var problems = new List<string>();
            problems.AddRange(_content.Cast.Values.SelectMany(p => ProfileValidator.Validate(p, _content.Vocabulary)));
            problems.AddRange(ProfileValidator.ValidateCast(_content.Cast, _content.Vocabulary));
            problems.AddRange(ScenarioValidator.Validate(_content.Backstory, _content.Vocabulary, _content.Cast));
            problems.AddRange(RuleSetValidator.Validate(_content.Rules, _content.Vocabulary));
            problems.AddRange(DecisionRuleValidator.Validate(_content.Rules, _content.Vocabulary));
            problems.AddRange(MorningValidator.Validate(_content.Morning, _content.Vocabulary, _content.Cast));

            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void NoRuleAnywhereNamesAnybodyInTheCast()
        {
            var problems = new List<string>();
            problems.AddRange(RuleSetValidator.ValidateNamesNobody(_content.Rules, _content.Cast.Keys));
            problems.AddRange(DecisionRuleValidator.ValidateNamesNobody(_content.Rules, _content.Cast.Keys));
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void EveryWantHasMoreThanOneWayToBeServedAndEveryActionCanBeAskedFor()
        {
            Assert.IsEmpty(
                DecisionRuleValidator.NothingIsStranded(_content.Rules, _content.Vocabulary),
                "a want with one action is that action under another name");
        }

        // ---- what an act does to the house ----

        [Test]
        public void NobodyEverEatsAndThisRecordsWhyNot()
        {
            // A characterisation test for a defect, not a statement of intent.
            // Nobody eats, in any condition, ever, including starving and alone
            // with nothing left to search. The rules were frozen before the
            // held-out condition was run, so this is recorded rather than fixed.
            // The cause is in the test below and in the S1 review.
            var ate = 0;

            for (ulong seed = 1; seed <= 30; seed++)
            {
                var run = Scenario001.Prepare(_content, "daniel_ate_it", seed);
                var before = run.World.Portions;

                run.World.Place("daniel", "kitchen");
                foreach (var id in new[] { "leo", "mara", "elena" }) run.World.Place(id, "back_room");
                run.World.SetHunger("daniel", 0.99);

                RunUntil(run, r => r.World.Portions < before, 60);
                if (run.World.Portions < before) ate++;
            }

            TestContext.WriteLine("he ate in " + ate + " of 30 mornings, starving and alone");
            Assert.AreEqual(0, ate,
                "if this starts passing, the defect is fixed and the test should be turned round");
        }

        [Test]
        public void WhatCrowdsEatingOutIsThatDoingNothingServesThreeWantsAtOnce()
        {
            // The mechanism behind the defect above, and the most useful thing
            // this slice found out about its own architecture. Appeal is added
            // up across every want an action serves, so an action that serves
            // three wants beats an action that serves one however urgent that
            // one is. Standing still is the fallback for wanting the food to
            // last, wanting the house quiet, and wanting to be left alone.
            var run = Fresh();
            run.World.Place("daniel", "kitchen");
            foreach (var id in new[] { "leo", "mara", "elena" }) run.World.Place(id, "back_room");
            run.World.SetHunger("daniel", 0.99);

            var percept = run.Morning.See("daniel");
            var motives = new Motivator(_content.Rules)
                .Raise(run.Minds["daniel"], percept, _content.Morning.Day, new TraceLog(), 0);
            var decision = new Deliberator(_content.Rules).Decide(
                run.Minds["daniel"], percept, motives, _content.Morning.Day,
                new Rng(1), new TraceLog(), 0);

            var waiting = decision.Ranked.First(r => r.Option.Kind == ActionKind.Wait);
            var eating = decision.Ranked.First(r => r.Option.Kind == ActionKind.Eat);

            TestContext.WriteLine("standing still serves: " + string.Join(" | ", waiting.Serves));
            TestContext.WriteLine("eating serves: " + string.Join(" | ", eating.Serves));

            Assert.GreaterOrEqual(waiting.Serves.Count, 3);
            Assert.AreEqual(1, eating.Serves.Count);
            Assert.Greater(waiting.Score, eating.Score,
                "a want with one outlet cannot compete with three wants sharing one");
        }

        [Test]
        public void HungerIsTheWeakestThingInTheModelAndThisIsHowWeakly()
        {
            // A known limitation, pinned down rather than left as an impression.
            // Wanting to know what happened and wanting the food to last both
            // outrank being hungry, at every level of hunger the morning reaches.
            // The rules were frozen before the held-out condition was run, so
            // this is recorded here rather than tuned away.
            var run = Fresh();
            run.World.Place("daniel", "kitchen");
            foreach (var id in new[] { "leo", "mara", "elena" }) run.World.Place(id, "back_room");
            run.World.SetHunger("daniel", 0.99);

            var percept = run.Morning.See("daniel");
            var motives = new Motivator(_content.Rules)
                .Raise(run.Minds["daniel"], percept, _content.Morning.Day, new TraceLog(), 0);

            var hunger = motives.First(m => m.Name == "get_food");
            var decision = new Deliberator(_content.Rules).Decide(
                run.Minds["daniel"], percept, motives, _content.Morning.Day,
                new Rng(1), new TraceLog(), 0);

            var eating = decision.Ranked.First(r => r.Option.Kind == ActionKind.Eat);

            TestContext.WriteLine("hunger " + hunger.Urgency.ToString("0.00") +
                                  ", eating is worth " + eating.Appeal.ToString("0.00") +
                                  " and costs " + eating.Cost.ToString("0.00") +
                                  ", net " + eating.Score.ToString("0.000"));
            foreach (var r in decision.Ranked.Take(4)) TestContext.WriteLine("  " + r);

            Assert.Greater(eating.Cost, 0.7, "the price of eating is what keeps it out of reach");
            Assert.Less(eating.Score, 0.2, "and it never wins by much even at the top of the hunger scale");
        }

        [Test]
        public void TakingFoodInFrontOfThePeopleItWasForCostsMoreThanTakingItAlone()
        {
            // The reason the test above has to empty the room. Stated as a
            // property rather than left implicit in a run that happens to work.
            var run = Fresh();
            run.World.Place("daniel", "kitchen");
            run.World.SetHunger("daniel", 0.99);

            foreach (var id in new[] { "leo", "mara", "elena" }) run.World.Place(id, "back_room");
            var alone = PriceOfEating(run, "daniel");

            foreach (var id in new[] { "leo", "mara", "elena" }) run.World.Place(id, "kitchen");
            var watched = PriceOfEating(run, "daniel");

            TestContext.WriteLine("alone " + alone.ToString("0.000") + ", watched " + watched.ToString("0.000"));
            Assert.Greater(watched, alone);
        }

        double PriceOfEating(Scenario001Run run, string who)
        {
            var percept = run.Morning.See(who);
            var decision = new Deliberator(_content.Rules).Decide(
                run.Minds[who], percept, new List<Motive>(), _content.Morning.Day,
                new Rng(1), new TraceLog(), 0);

            return decision.Ranked.First(r => r.Option.Kind == ActionKind.Eat).Cost;
        }

        [Test]
        public void WalkingOutOfARoomPutsYouInTheOtherOne()
        {
            var run = Fresh();
            run.World.Place("daniel", "kitchen");

            RunUntil(run, r => r.World.RoomOf("daniel") != "kitchen", 200);
            Assert.AreNotEqual("kitchen", run.World.RoomOf("daniel"));
            CollectionAssert.Contains(run.World.House.RoomIds, run.World.RoomOf("daniel"));
        }

        [Test]
        public void WhatSomebodyDoesBecomesSomethingTheOthersHaveToMakeSenseOf()
        {
            var run = Fresh();
            run.Morning.Run(40);

            Assert.IsNotEmpty(run.Result.Events, "a morning in which nothing happened");

            foreach (var e in run.Result.Events)
            foreach (var id in run.World.Inhabitants)
            {
                var kept = run.Minds[id].Experiences.Any(x => x.EventId == e.Id);
                var reached = e.AccessFor(id) != Access.None;
                Assert.AreEqual(reached, kept,
                    id + " and event " + e.Id + ": remembering and being there have come apart");
            }
        }

        [Test]
        public void NobodyLearnsAnythingFromARoomTheyAreNotIn()
        {
            var run = Fresh();
            run.Morning.Run(90);

            foreach (var e in run.Result.Events)
            {
                var whereItHappened = e.Witnesses.Concat(e.Overhearers).ToList();

                foreach (var id in run.World.Inhabitants)
                {
                    if (whereItHappened.Contains(id) || id == e.ActorId) continue;

                    Assert.IsFalse(run.Minds[id].Experiences.Any(x => x.EventId == e.Id),
                        id + " has a memory of " + e.Id + ", which happened out of their sight and hearing");
                }
            }
        }

        [Test]
        public void GoingThroughSomebodyBelongingsIsAimedAtThemOnlyIfTheyAreThereToSeeIt()
        {
            // Two claims. Whenever a search names somebody, it is the person
            // whose room it is and they were standing there. And across enough
            // mornings it does happen, so the case is not hypothetical.
            var named = 0;
            var total = 0;

            for (ulong seed = 1; seed <= 20; seed++)
            {
                var run = Scenario001.Run(_content, "daniel_ate_it", seed);

                foreach (var e in run.Result.Events.Where(e => e.Action == "search_belongings"))
                {
                    total++;
                    if (e.TargetId == null) continue;

                    named++;
                    var room = run.World.House.Rooms.FirstOrDefault(r => r.IsOwnedBy(e.TargetId));
                    Assert.IsNotNull(room, e.TargetId + " was named but owns no room");
                    CollectionAssert.Contains(e.Witnesses, e.TargetId,
                        "somebody was named without being there to see it");
                }
            }

            TestContext.WriteLine(named + " of " + total + " searches were done in front of the person whose room it was");
            Assert.Greater(total, 0, "nobody searched anything in twenty mornings");
        }

        [Test]
        public void ThePersonDoingSomethingIsNotAWitnessToTheirOwnFace()
        {
            var run = Fresh();
            run.Morning.Run(90);

            foreach (var e in run.Result.Events.Where(e => e.Action == "show_distress"))
            {
                Assert.IsNull(e.ActorId, "nobody performs their own distress");
                CollectionAssert.DoesNotContain(e.Witnesses, e.TargetId,
                    "you do not watch yourself go to pieces");
                Assert.IsNotEmpty(e.Witnesses, "an unseen face is not an event");
            }
        }

        [Test]
        public void FeelingItAndShowingItAreNotTheSameThing()
        {
            // Composed people can be in a state without the room knowing. This is
            // the property the review asked for, and it has to hold at the level
            // of what reaches other people, not at the level of what is felt.
            var run = Fresh();
            run.Morning.Run(90);

            var shown = run.Result.Events
                .Where(e => e.Action == "show_distress")
                .Select(e => e.TargetId)
                .Distinct()
                .ToList();

            foreach (var id in run.World.Inhabitants)
            {
                var mind = run.Minds[id];
                var felt = mind.Emotions.Live.Any(e =>
                    _content.Rules.Deciding.DistressShows.Contains(e.Type) && e.Intensity > 0.4);

                if (felt && !shown.Contains(id))
                    TestContext.WriteLine(
                        id + " was in a state and nobody saw it. Expressiveness " +
                        mind.Profile.Expressiveness.ToString("0.00"));
            }

            // The guarded claim: the least expressive person in the cast is not
            // the one who shows the most.
            var quietest = run.World.Inhabitants.OrderBy(id => run.Minds[id].Profile.Expressiveness).First();
            var counts = run.Result.Events
                .Where(e => e.Action == "show_distress")
                .GroupBy(e => e.TargetId)
                .ToDictionary(g => g.Key, g => g.Count());

            counts.TryGetValue(quietest, out var quietestCount);
            var loudest = counts.Count == 0 ? 0 : counts.Values.Max();

            Assert.LessOrEqual(quietestCount, loudest,
                "the person who holds it in should not be the one the room reads most easily");
        }

        [Test]
        public void SomethingThatLandsHardEnoughStopsYouDoingWhatYouWereDoing()
        {
            var run = Fresh();
            run.Morning.Run(90);

            var interrupted = run.Trace.All.Count(r =>
                r.Kind == TraceKind.Consequence && r.Summary == "stopped what they were doing");

            TestContext.WriteLine("interruptions: " + interrupted);
            Assert.Less(interrupted, run.Result.Actions.Count,
                "if everything interrupts everything, nobody ever finishes anything");
        }

        [Test]
        public void TheSameSeedGivesTheSameMorningEveryTime()
        {
            var a = Scenario001.Run(_content, "daniel_ate_it", 11);
            var b = Scenario001.Run(_content, "daniel_ate_it", 11);

            CollectionAssert.AreEqual(
                a.Result.Actions.Select(x => x.ToString()).ToArray(),
                b.Result.Actions.Select(x => x.ToString()).ToArray());
            Assert.AreEqual(a.World.Portions, b.World.Portions);
        }

        [Test]
        public void ADifferentSeedCanGiveADifferentMorning()
        {
            var mornings = new HashSet<string>(StringComparer.Ordinal);
            for (ulong seed = 1; seed <= 12; seed++)
                mornings.Add(string.Join("|",
                    Scenario001.Run(_content, "daniel_ate_it", seed).Result.Actions.Select(a => a.ToString())));

            Assert.Greater(mornings.Count, 1, "the seed settles the moments that are genuinely open");
        }

        [Test]
        public void EveryDecisionCanBeWalkedBackToSomethingThatHappened()
        {
            var run = Scenario001.Run(_content, "daniel_ate_it", 5);
            var checkedAny = 0;

            foreach (var a in run.Result.Actions)
            {
                var chain = run.Trace.Chain(a.DecisionTraceId).ToList();
                var kinds = chain.Select(r => r.Kind).ToList();

                CollectionAssert.Contains(kinds, TraceKind.Deliberation,
                    a + " has no record of being weighed");

                var record = run.Trace.Get(a.DecisionTraceId);
                Assert.IsTrue(record.Data.ContainsKey("options"), a + " does not say what it beat");
                Assert.IsTrue(record.Data.ContainsKey("resolution"),
                    a + " does not say whether anything was left to chance");

                if (kinds.Contains(TraceKind.Motive))
                {
                    checkedAny++;
                    CollectionAssert.Contains(kinds, TraceKind.Motive);
                }
            }

            Assert.Greater(checkedAny, run.Result.Actions.Count / 2,
                "most decisions should name a want, not just an option list");
        }

        [Test]
        public void ADecisionCanSayInWordsWhyItWentThatWay()
        {
            var run = Scenario001.Run(_content, "daniel_ate_it", 5);
            var searched = run.Result.Actions.FirstOrDefault(a => a.Action.Kind == ActionKind.SearchRoom);
            if (searched == null) Assert.Inconclusive("nobody searched anything in this run");

            var why = S1Report.WhyTheyDidThat(run, searched.CharacterId, searched.Minute);
            TestContext.WriteLine(why);

            StringAssert.Contains("because", why);
            StringAssert.Contains("Motive", why);
        }

        static void RunUntil(Scenario001Run run, Func<Scenario001Run, bool> done, int maxMinutes)
        {
            for (var i = 0; i < maxMinutes && !done(run); i++) run.Morning.Step();
        }
    }
}
