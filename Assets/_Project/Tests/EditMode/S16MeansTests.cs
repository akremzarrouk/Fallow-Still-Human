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
    /// S1.6, the mechanisms themselves, on the bench: a walk credited to a want
    /// only if its end could be worth doing (M2), and scripted events of the
    /// lived day carrying a minute (M1). Nothing here runs a morning except the
    /// last test, which checks that the mechanism and the diagnosis instrument
    /// agree on every walk actually taken.
    /// </summary>
    public class S16MeansTests
    {
        static Scenario001Content _content;

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        static Scenario001Content Weighing(string means) => S16.Means(_content, means);

        /// <summary>Somebody who will not go through another person's things: warm, and values their privacy.</summary>
        static Mind WillNotSearch() => new Mind(Bench.Person("a",
            new Dictionary<string, double> { { "empathetic", 0.9 } }, new List<string> { "closeness", "autonomy" }));

        /// <summary>Somebody with no such qualms.</summary>
        static Mind WillSearch() => new Mind(Bench.Person("b"));

        static Motive Want(string name, double urgency, string target = null)
            => new Motive(name, target, urgency, new List<string>(), new List<ScalerTerm>());

        /// <summary>In the kitchen, already through it, so that the only way of looking further is the bedroom.</summary>
        static Percept InTheKitchen(string who, IReadOnlyList<string> present = null)
            => Bench.Standing(who, "kitchen", present, hunger: 0.0, foodThere: true, searched: true, searchedRooms: new List<string> { "kitchen" });

        static Decision Decide(Scenario001Content c, Mind mind, Percept percept, IReadOnlyList<Motive> wants, TraceLog trace = null, Intention holding = null)
            => new Deliberator(c.Rules).Decide(mind, percept, wants, c.Morning.Day, new Rng(1), trace ?? new TraceLog(), 0, holding);

        static ScoredOption Walk(Decision d, string to) => d.Ranked.First(r => r.Option.Kind == ActionKind.GoTo && r.Option.DestinationRoomId == to);

        [Test]
        public void AWalkToAnEndThatWouldNotBeWorthDoingIsNotCreditedToTheWant()
        {
            var wants = new[] { Want("find_out", 0.5) };
            var asWant = Walk(Decide(Weighing(MeansMode.Want), WillNotSearch(), InTheKitchen("a"), wants), "bedroom");
            var asEnd = Walk(Decide(Weighing(MeansMode.End), WillNotSearch(), InTheKitchen("a"), wants), "bedroom");

            Assert.AreEqual(0.5 * 0.7, asWant.Appeal, 1e-9, "a walk is worth its want, as shipped");
            Assert.AreEqual(0.0, asEnd.Appeal, 1e-9, "not credited: going through the bedroom would cost more than it is worth");
            Assert.IsEmpty(asEnd.Contributions);
        }

        [Test]
        public void AWalkToAnEndWorthDoingIsWorthExactlyWhatItWas()
        {
            var wants = new[] { Want("find_out", 0.5) };
            var asWant = Decide(Weighing(MeansMode.Want), WillSearch(), InTheKitchen("b"), wants);
            var asEnd = Decide(Weighing(MeansMode.End), WillSearch(), InTheKitchen("b"), wants);

            Assert.AreEqual(0.5 * 0.7, Walk(asEnd, "bedroom").Appeal, 1e-9);
            foreach (var r in asWant.Ranked)
            {
                var same = asEnd.Ranked.First(x => x.Option.SameAs(r.Option));
                Assert.AreEqual(r.Appeal, same.Appeal, 1e-9, r.Option + ": no number changes when the end is worth it");
                Assert.AreEqual(r.Cost, same.Cost, 1e-9, r.Option + ": no price changes");
            }
            Assert.AreEqual(asWant.Chosen.Key, asEnd.Chosen.Key);
        }

        [Test]
        public void ArrivingWhereTheEndWasForeseenWorthDoingTheIntentionHolds()
        {
            var c = Weighing(MeansMode.End);
            var wants = new[] { Want("find_out", 0.5) };
            var setOut = Decide(c, WillSearch(), InTheKitchen("b"), wants);
            var walk = Walk(setOut, "bedroom");
            Assert.Greater(walk.Score, 0.0, "the walk is credited, and worth taking");

            var there = Bench.Standing("b", "bedroom", searched: false, searchedRooms: new List<string> { "kitchen" });
            var holding = new Intention("find_out", "find_out", walk.Option, 10, 0);
            var arrived = Decide(c, WillSearch(), there, wants, holding: holding);
            Assert.AreEqual(Commitment.Held, arrived.Commitment);
            Assert.AreEqual("search_room", arrived.Chosen.Key);

            // And somebody for whom the walk would not have been credited, had they
            // arrived anyway, gives it up on arrival for exactly the reason foreseen.
            var gaveUp = Decide(c, WillNotSearch(), Bench.Standing("a", "bedroom", searched: false, searchedRooms: new List<string> { "kitchen" }), wants, holding: holding);
            Assert.AreEqual(Commitment.NotWorthIt, gaveUp.Commitment);
        }

        [Test]
        public void AWalkCreditedByTwoWantsKeepsOnlyTheWantWhoseEndIsWorthIt()
        {
            // Wanting to look further (the bedroom would not be searched) and
            // wanting to be out of sight (the bedroom has a door, and waiting there
            // alone serves it) both propose the same walk.
            var wants = new[] { Want("find_out", 0.5), Want("avoid_exposure", 0.3) };
            var asWant = Walk(Decide(Weighing(MeansMode.Want), WillNotSearch(), InTheKitchen("a", new[] { "mara" }), wants), "bedroom");
            var asEnd = Walk(Decide(Weighing(MeansMode.End), WillNotSearch(), InTheKitchen("a", new[] { "mara" }), wants), "bedroom");

            Assert.AreEqual(0.5 * 0.7 + 0.3 * 0.5, asWant.Appeal, 1e-9);
            Assert.AreEqual(0.3 * 0.5, asEnd.Appeal, 1e-9);
            CollectionAssert.AreEquivalent(new[] { "avoid_exposure" }, asEnd.Contributions.Select(x => x.MotiveKey).ToList());
        }

        [Test]
        public void TheDecisionSaysWhatWasForeseenAndWhyAWalkWasNotCredited()
        {
            var trace = new TraceLog();
            var d = Decide(Weighing(MeansMode.End), WillNotSearch(), InTheKitchen("a"), new[] { Want("find_out", 0.5) }, trace);
            var record = trace.Get(d.TraceId);
            Assert.IsTrue(record.Data.ContainsKey("foresaw"), "the trace records what was foreseen");
            StringAssert.Contains("go_to->bedroom for find_out: search_room -0.735, not worth walking for", record.Data["foresaw"]);
            // With the walk not credited, what is left for the want is what can be
            // done for it here: this person has not looked in the pantry yet.
            Assert.AreEqual("check_pantry", d.Chosen.Key);
            Assert.AreEqual("find_out", d.Leading.Name);
            Assert.Less(Walk(d, "bedroom").Score, 0.0, "the walk is now worth less than nothing: its price, for no want");
        }

        [Test]
        public void TheImaginedRoomKnowsOnlyWhatTheWalkerKnows()
        {
            var here = Bench.Standing("leo", "kitchen", hunger: 0.4, searched: true, searchedRooms: new List<string> { "kitchen" });

            var bedroom = here.Imagine("bedroom", new List<string>(), ActionCatalog.PantryTag);
            Assert.AreEqual("bedroom", bedroom.Room.Id);
            Assert.IsTrue(bedroom.InSomebodyElsesRoom, "whose room it is comes from the house");
            Assert.IsTrue(bedroom.Alone, "who is there cannot be known");
            Assert.IsFalse(bedroom.RoomHoldsFood);
            Assert.IsNull(bedroom.FoodWithinReach);
            Assert.IsFalse(bedroom.SearchedThisRoomMyself);
            Assert.AreEqual(0.4, bedroom.Hunger, 1e-9);
            CollectionAssert.AreEqual(new[] { "hall" }, bedroom.Adjacent.ToList());
            CollectionAssert.AreEqual(new[] { "kitchen" }, bedroom.RoomsIHaveSearched.ToList());

            var kitchen = here.Imagine("kitchen", new List<string> { "mara" }, ActionCatalog.PantryTag);
            Assert.IsTrue(kitchen.RoomHoldsFood);
            Assert.AreEqual(true, kitchen.FoodWithinReach, "food kept there is taken to be within reach");
            Assert.IsTrue(kitchen.SearchedThisRoomMyself, "my own searches are my own memory");
            CollectionAssert.AreEqual(new[] { "mara" }, kitchen.Present.ToList());

            Assert.IsNull(here.Imagine("attic", new List<string>(), ActionCatalog.PantryTag), "a room that does not exist cannot be imagined");
        }

        [Test]
        public void TheShippedRulesDoNotSetItAndTheValidatorKnowsTheWays()
        {
            Assert.AreEqual(MeansMode.Want, _content.Rules.Deciding.Means, "the shipped rules weigh a walk by its want, as before S1.6");
            Assert.IsEmpty(DecisionRuleValidator.Validate(Weighing(MeansMode.End).Rules, _content.Vocabulary));
            var problems = DecisionRuleValidator.Validate(Weighing("elsewhere").Rules, _content.Vocabulary);
            Assert.IsTrue(problems.Any(p => p.Contains("elsewhere")), string.Join("\n", problems));
        }

        [Test]
        public void AScriptedEventMayCarryAMinute()
        {
            var timed = ScenarioLoader.EventFromJson("{\"id\":\"x\",\"day\":4,\"order\":1,\"type\":\"action\",\"minute\":7}");
            var untimed = ScenarioLoader.EventFromJson("{\"id\":\"y\",\"day\":4,\"order\":2,\"type\":\"action\"}");
            Assert.AreEqual(7, timed.Minute);
            Assert.AreEqual(-1, untimed.Minute, "absent, only the order is known");
        }

        [Test]
        public void TheTimedMorningStampsExactlyTheScriptedEventsOfTheLivedDay()
        {
            var timed = S16.Timed(_content);
            var day = _content.Morning.Day;

            Assert.AreEqual(0, timed.Morning.Opening.Minute);
            foreach (var e in timed.Backstory.Events)
                Assert.AreEqual(e.Day == day ? 0 : -1, e.Minute, e.Id);
            Assert.AreEqual(3, timed.Backstory.Events.Count(e => e.Minute == 0), "the three day-4 events of the backstory");
            foreach (var v in timed.Morning.Variants)
            foreach (var e in v.NightEvents)
                Assert.AreEqual(-1, e.Minute, "the night is not on the lived day, and is not touched");

            // And the memory fades from then on, as any memory of the morning does.
            var run = Scenario001.Prepare(S15.Mode(timed, DispositionMode.Respond), "daniel_ate_it", 1);
            foreach (var id in S16.People)
            foreach (var x in run.Minds[id].Experiences.Where(x => x.Day == day))
                Assert.AreEqual(0, x.Minute, id + " remembers " + x.EventId + " at minute 0");
        }

        [Test]
        public void InARunEveryWalkTakenIsOneWhoseEndCouldBeWorthIt()
        {
            // The mechanism in the deliberator and the instrument of the
            // diagnosis are two implementations of the same question. Every walk
            // actually set out on under `end` must be one the instrument would
            // have foreseen worth it, on a morning where the loop was worst.
            var c = S16.Means(S15.Mode(_content, DispositionMode.Respond), MeansMode.End);
            var walks = S16.Walks(c, new[] { "daniel_ate_it" }, 9, 1);
            Assert.Greater(walks.Count, 0, "somebody still walks somewhere");
            foreach (var w in walks)
                Assert.IsTrue(w.Foreseen.WorthIt, w.Who + " at minute " + w.SetOutAt + " set out for " + w.Want + " to " + w.To + ", foreseen " + w.Foreseen);
        }
    }
}
