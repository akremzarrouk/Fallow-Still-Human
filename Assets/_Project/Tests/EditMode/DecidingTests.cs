using System;
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
    /// <summary>Shared scaffolding: a tiny house and a cast built by hand.</summary>
    public static class Bench
    {
        public static RoomGraph House()
        {
            var house = new RoomGraph();
            house.AddRoom(new Room("kitchen", "kitchen", new[] { "pantry", "common" }, new string[0]));
            house.AddRoom(new Room("hall", "hall", new[] { "passage" }, new string[0]));
            house.AddRoom(new Room("bedroom", "bedroom", new[] { "private" }, new[] { "mara" }));
            house.Connect("kitchen", "hall", true);
            house.Connect("hall", "bedroom", true);
            return house;
        }

        public static Profile Person(
            string id, IReadOnlyDictionary<string, double> traits = null,
            IReadOnlyList<string> values = null, int age = 30)
            => new Profile(
                id, id, age, "sibling",
                traits ?? new Dictionary<string, double>(),
                values ?? new List<string>(),
                0.5, new Dictionary<string, double>(), new List<BeliefSeed>());

        public static Percept Standing(
            string who, string room = "kitchen", IReadOnlyList<string> present = null,
            double hunger = 0.0, bool foodThere = true, bool searched = false,
            IReadOnlyList<string> searchedRooms = null)
        {
            var house = House();
            var r = house.Get(room);
            return new Percept(
                who, 10, r, present ?? new List<string>(), house.Adjacent(room), hunger,
                r.HasTag("pantry"), r.HasTag("pantry") ? (bool?)foodThere : null,
                searched, house, false, null, searchedRooms);
        }

        public static DecisionDynamics Dynamics()
            => new DecisionDynamics
            {
                AmbiguityBand = 0.08,
                ActionMinutes = new Dictionary<string, int>
                {
                    { "wait", 5 }, { "observe", 4 }, { "go_to", 2 },
                    { "check_pantry", 3 }, { "search_room", 8 }, { "comfort", 8 }, { "eat", 4 }
                }
            };
    }

    /// <summary>What a person comes to want, and why.</summary>
    public class MotivationTests
    {
        static RuleSet WithMotivation(params MotivationRule[] rules)
            => new RuleSet { Motivation = rules.ToList(), Deciding = Bench.Dynamics() };

        [Test]
        public void AWantComesOutOfTheStateThePersonIsIn()
        {
            var rules = WithMotivation(new MotivationRule
            {
                Id = "hunger",
                Motive = "get_food",
                ScaledBy = new[] { new Scaler { Kind = ScalerKind.Need, Name = "hunger", Factor = 1.0 } }
            });

            var mind = new Mind(Bench.Person("leo"));
            var motives = new Motivator(rules).Raise(mind, Bench.Standing("leo", hunger: 0.6), 4, new TraceLog(), 0);

            Assert.AreEqual(1, motives.Count);
            Assert.AreEqual("get_food", motives[0].Name);
            Assert.AreEqual(0.6, motives[0].Urgency, 1e-9);
        }

        [Test]
        public void TheSameMomentRaisesDifferentWantsInDifferentPeople()
        {
            var rules = WithMotivation(
                new MotivationRule
                {
                    Id = "control",
                    Motive = "find_out",
                    ScaledBy = new[] { new Scaler { Kind = ScalerKind.Value, Name = "control", Factor = 1.0 } }
                },
                new MotivationRule
                {
                    Id = "peace",
                    Motive = "keep_peace",
                    ScaledBy = new[] { new Scaler { Kind = ScalerKind.Value, Name = "family_safety", Factor = 1.0 } }
                });

            var driver = new Mind(Bench.Person("a", values: new[] { "control" }));
            var peacemaker = new Mind(Bench.Person("b", values: new[] { "family_safety" }));

            var m = new Motivator(rules);
            var one = m.Raise(driver, Bench.Standing("a"), 4, new TraceLog(), 0);
            var other = m.Raise(peacemaker, Bench.Standing("b"), 4, new TraceLog(), 0);

            Assert.AreEqual("find_out", one[0].Name);
            Assert.AreEqual("keep_peace", other[0].Name);
        }

        [Test]
        public void AWantAboutPeopleIsRaisedOncePerPersonAndWeighedSeparately()
        {
            var rules = WithMotivation(new MotivationRule
            {
                Id = "look",
                Motive = "look_after",
                Scope = MotiveScope.EachPresent,
                ScaledBy = new[]
                {
                    new Scaler { Kind = ScalerKind.Ledger, Entry = "comforted_me", About = "$target", Factor = 1.0 }
                }
            });

            var mind = new Mind(Bench.Person("leo"));
            mind.Ledger.Add("elena", "comforted_me", 0.8, 0, "e1");

            var motives = new Motivator(rules)
                .Raise(mind, Bench.Standing("leo", present: new[] { "elena", "daniel" }), 4, new TraceLog(), 0);

            Assert.AreEqual(1, motives.Count, "only the person there is anything to say about raises one");
            Assert.AreEqual("elena", motives[0].TargetId);
        }

        [Test]
        public void TwoReasonsToWantTheSameThingMakeItMorePressingWithoutRunningAway()
        {
            var rules = WithMotivation(
                new MotivationRule { Id = "one", Motive = "keep_peace", BaseUrgency = 0.7 },
                new MotivationRule { Id = "two", Motive = "keep_peace", BaseUrgency = 0.7 });

            var motives = new Motivator(rules)
                .Raise(new Mind(Bench.Person("leo")), Bench.Standing("leo"), 4, new TraceLog(), 0);

            Assert.AreEqual(1, motives.Count);
            Assert.Greater(motives[0].Urgency, 0.7);
            Assert.Less(motives[0].Urgency, 1.0, "wanting it twice does not make it more than everything");
            CollectionAssert.AreEquivalent(new[] { "one", "two" }, motives[0].RuleIds.ToArray());
        }

        [Test]
        public void AWantCanAlwaysNameWhatRaisedIt()
        {
            var rules = WithMotivation(new MotivationRule
            {
                Id = "shame_makes_you_scarce",
                Motive = "avoid_exposure",
                ScaledBy = new[] { new Scaler { Kind = ScalerKind.Emotion, Name = "shame", Factor = 0.8 } }
            });

            var mind = new Mind(Bench.Person("daniel"));
            mind.Emotions.Add("shame", null, "respect", 0.75, 0, "e1");

            var trace = new TraceLog();
            var motives = new Motivator(rules).Raise(mind, Bench.Standing("daniel"), 4, trace, 0);

            Assert.AreEqual(1, motives.Count);
            StringAssert.Contains("shame", motives[0].Because);

            var record = trace.Get(motives[0].TraceId);
            Assert.AreEqual(TraceKind.Motive, record.Kind);
            StringAssert.Contains("shame", record.Data["because"]);
        }

        [Test]
        public void AWantNothingSupportsIsNotRaisedAtAll()
        {
            var rules = WithMotivation(new MotivationRule
            {
                Id = "shame_makes_you_scarce",
                Motive = "avoid_exposure",
                ScaledBy = new[] { new Scaler { Kind = ScalerKind.Emotion, Name = "shame", Factor = 0.8 } }
            });

            var motives = new Motivator(rules)
                .Raise(new Mind(Bench.Person("leo")), Bench.Standing("leo"), 4, new TraceLog(), 0);

            CollectionAssert.IsEmpty(motives, "nobody wants to hide for no reason");
        }
    }

    /// <summary>What the house allows, before anybody wants anything.</summary>
    public class ActionCatalogTests
    {
        [Test]
        public void DoingNothingIsAlwaysOnTheList()
        {
            var options = ActionCatalog.Available(Bench.Standing("leo"), Bench.Dynamics());
            Assert.IsTrue(options.Any(o => o.Kind == ActionKind.Wait));
        }

        [Test]
        public void YouCannotEatWhereThereIsNoFood()
        {
            var inTheKitchen = ActionCatalog.Available(Bench.Standing("leo"), Bench.Dynamics());
            Assert.IsTrue(inTheKitchen.Any(o => o.Kind == ActionKind.Eat));

            var emptyShelf = ActionCatalog.Available(Bench.Standing("leo", foodThere: false), Bench.Dynamics());
            Assert.IsFalse(emptyShelf.Any(o => o.Kind == ActionKind.Eat));

            var elsewhere = ActionCatalog.Available(Bench.Standing("leo", "bedroom"), Bench.Dynamics());
            Assert.IsFalse(elsewhere.Any(o => o.Kind == ActionKind.Eat));
        }

        [Test]
        public void NobodyCanSitWithSomebodyWhoIsNotThere()
        {
            var alone = ActionCatalog.Available(Bench.Standing("leo"), Bench.Dynamics());
            Assert.IsFalse(alone.Any(o => o.Kind == ActionKind.Comfort));
            Assert.IsFalse(alone.Any(o => o.Kind == ActionKind.Observe));

            var together = ActionCatalog.Available(
                Bench.Standing("leo", present: new[] { "mara" }), Bench.Dynamics());
            Assert.IsTrue(together.Any(o => o.Kind == ActionKind.Comfort && o.TargetId == "mara"));
        }

        [Test]
        public void GoingSomewhereTakesLongerTheFurtherItIs()
        {
            var options = ActionCatalog.Available(Bench.Standing("leo", "kitchen"), Bench.Dynamics());

            var nextDoor = options.Single(o => o.DestinationRoomId == "hall");
            var further = options.Single(o => o.DestinationRoomId == "bedroom");

            Assert.AreEqual(2, nextDoor.Duration);
            Assert.AreEqual(4, further.Duration);
        }

        [Test]
        public void ARoomYouHaveAlreadyBeenThroughIsNotSomethingToSearchAgain()
        {
            var again = ActionCatalog.Available(Bench.Standing("leo", searched: true), Bench.Dynamics());
            Assert.IsFalse(again.Any(o => o.Kind == ActionKind.SearchRoom));
        }

        [Test]
        public void AProposalCanOnlyEndorseWhatIsAlreadyPossible()
        {
            // Wanting food badly cannot conjure a portion in a room with none.
            var percept = Bench.Standing("leo", "bedroom");
            var available = ActionCatalog.Available(percept, Bench.Dynamics());

            var proposal = new ProposalRule { Motive = "get_food", Action = "eat", Targeting = Targeting.None, Fit = 1.0 };
            var motive = new Motive("get_food", null, 0.99, null, null);

            CollectionAssert.IsEmpty(
                ActionCatalog.Endorsed(proposal, motive, percept, available).ToList(),
                "an impossible action stays impossible however badly it is wanted");
        }

        [Test]
        public void LeavingMeansTheNextRoomWhicheverItIs()
        {
            var percept = Bench.Standing("leo", "hall");
            var available = ActionCatalog.Available(percept, Bench.Dynamics());

            var proposal = new ProposalRule { Motive = "avoid_exposure", Action = "go_to", Targeting = Targeting.AwayFromHere };
            var motive = new Motive("avoid_exposure", null, 0.8, null, null);

            var ways = ActionCatalog.Endorsed(proposal, motive, percept, available).ToList();
            CollectionAssert.AreEquivalent(
                new[] { "kitchen", "bedroom" },
                ways.Select(w => w.DestinationRoomId).ToArray());
        }

        [Test]
        public void LookingSomewhereNewSkipsWhereverIHaveAlreadyBeen()
        {
            var percept = Bench.Standing("leo", "kitchen", searchedRooms: new[] { "bedroom" });
            Assert.AreEqual("bedroom", percept.NearestTagged("private"));
            Assert.IsNull(percept.NearestUnsearched("private"),
                "there is nowhere left of that kind worth going to");
        }
    }
}
