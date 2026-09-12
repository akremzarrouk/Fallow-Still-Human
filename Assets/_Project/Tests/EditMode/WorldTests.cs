using System;
using System.IO;
using System.Linq;
using Fallow.Core.Data;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>The house itself: rooms, who can get where, and who can hear what.</summary>
    public class RoomGraphTests
    {
        static RoomGraph SmallHouse()
        {
            var house = new RoomGraph();
            house.AddRoom(new Room("kitchen", "kitchen", new[] { "pantry", "common" }, new string[0]));
            house.AddRoom(new Room("hall", "hallway", new[] { "passage" }, new string[0]));
            house.AddRoom(new Room("bedroom", "bedroom", new[] { "private" }, new[] { "mara" }));
            house.Connect("kitchen", "hall", true);
            house.Connect("hall", "bedroom", false);
            return house;
        }

        [Test]
        public void RoomsKnowWhatTheyAreForAndWhoseTheyAre()
        {
            var house = SmallHouse();
            Assert.IsTrue(house.Get("kitchen").HasTag("pantry"));
            Assert.IsFalse(house.Get("kitchen").HasTag("private"));
            Assert.IsTrue(house.Get("bedroom").IsOwnedBy("mara"));
            Assert.IsFalse(house.Get("bedroom").IsOwnedBy("daniel"));
            Assert.IsFalse(house.Get("kitchen").IsOwnedBy("mara"), "a shared room belongs to nobody");
        }

        [Test]
        public void DoorsGoBothWaysAndDistanceCountsThem()
        {
            var house = SmallHouse();
            CollectionAssert.Contains(house.Adjacent("hall"), "kitchen");
            CollectionAssert.Contains(house.Adjacent("kitchen"), "hall");

            Assert.AreEqual(0, house.Distance("kitchen", "kitchen"));
            Assert.AreEqual(1, house.Distance("kitchen", "hall"));
            Assert.AreEqual(2, house.Distance("kitchen", "bedroom"));
        }

        [Test]
        public void BeingNextDoorIsNotTheSameAsBeingWithinEarshot()
        {
            var house = SmallHouse();
            CollectionAssert.Contains(house.Audible("kitchen"), "hall");
            CollectionAssert.DoesNotContain(house.Audible("hall"), "bedroom",
                "the bedroom door is shut, which is why somebody can be surprised by what they find");
        }

        [Test]
        public void SomewhereUnreachableIsReportedAsSuchRatherThanGuessedAt()
        {
            var house = SmallHouse();
            house.AddRoom(new Room("cellar", "cellar", new string[0], new string[0]));
            Assert.AreEqual(-1, house.Distance("kitchen", "cellar"));
            Assert.AreEqual(-1, house.Distance("kitchen", "nowhere"));
        }
    }

    /// <summary>Where everybody is, what is left, and how hungry they are getting.</summary>
    public class WorldStateTests
    {
        static RoomGraph House()
        {
            var house = new RoomGraph();
            house.AddRoom(new Room("kitchen", "kitchen", new[] { "pantry" }, new string[0]));
            house.AddRoom(new Room("hall", "hall", new[] { "passage" }, new string[0]));
            house.AddRoom(new Room("bedroom", "bedroom", new[] { "private" }, new string[0]));
            house.Connect("kitchen", "hall", true);
            house.Connect("hall", "bedroom", false);
            return house;
        }

        [Test]
        public void PeopleAreSomewhereAndCanBeFoundThere()
        {
            var w = new WorldState(House(), 2);
            w.Place("leo", "kitchen");
            w.Place("mara", "kitchen");
            w.Place("daniel", "bedroom");

            Assert.AreEqual("kitchen", w.RoomOf("leo"));
            CollectionAssert.AreEqual(new[] { "leo", "mara" }, w.InRoom("kitchen").ToArray());
            CollectionAssert.AreEqual(new[] { "mara" }, w.WithMe("leo").ToArray());
            CollectionAssert.IsEmpty(w.WithMe("daniel"));
        }

        [Test]
        public void PuttingSomebodyNowhereIsRefusedRatherThanQuietlyAccepted()
        {
            var w = new WorldState(House(), 2);
            Assert.Throws<ArgumentException>(() => w.Place("leo", "attic"));
        }

        [Test]
        public void EarshotReachesTheNextRoomAndNoFurther()
        {
            var w = new WorldState(House(), 2);
            w.Place("leo", "hall");
            w.Place("mara", "bedroom");

            CollectionAssert.AreEqual(new[] { "leo" }, w.WithinEarshotOf("kitchen").ToArray());
            CollectionAssert.IsEmpty(w.WithinEarshotOf("bedroom"),
                "nothing carries out of the back of the house");
        }

        [Test]
        public void EverybodyGetsHungrierAtTheirOwnRate()
        {
            var w = new WorldState(House(), 2);
            w.Place("daniel", "kitchen");
            w.Place("elena", "kitchen");
            w.SetHunger("daniel", 0.5);
            w.SetHunger("elena", 0.5);

            for (var i = 0; i < 10; i++)
                w.Tick(new System.Collections.Generic.Dictionary<string, double>
                {
                    { "daniel", 0.01 }, { "elena", 0.005 }
                });

            Assert.AreEqual(10, w.Minute);
            Assert.Greater(w.HungerOf("daniel"), w.HungerOf("elena"));
            Assert.AreEqual(0.6, w.HungerOf("daniel"), 1e-9);
        }

        [Test]
        public void ThePantryRunsOutAndStaysOut()
        {
            var w = new WorldState(House(), 1);
            Assert.IsTrue(w.TakePortion());
            Assert.AreEqual(0, w.Portions);
            Assert.IsFalse(w.TakePortion(), "there is no going below empty");
            Assert.AreEqual(0, w.Portions);
        }
    }

    /// <summary>
    /// The boundary the whole design rests on. A person decides from a Percept,
    /// so what is absent from it is what they cannot possibly act on.
    /// </summary>
    public class PerceptTests
    {
        static Scenario001Run Fresh()
            => Scenario001.Prepare(Scenario001Content.Load(TestPaths.DataRoot), "daniel_ate_it", 7);

        [Test]
        public void WhatISeeIsMyRoomAndTheRoomOnly()
        {
            var run = Fresh();
            run.World.Place("daniel", "back_room");

            var mine = run.Morning.See("daniel");

            Assert.AreEqual("back_room", mine.Room.Id);
            CollectionAssert.IsEmpty(mine.Present, "the others are in the kitchen and he is not with them");
            CollectionAssert.Contains(mine.Adjacent, "hallway");
            CollectionAssert.DoesNotContain(mine.Adjacent, "kitchen",
                "the kitchen is two doors away, so it is not somewhere he can simply step into");
        }

        [Test]
        public void HowMuchIsLeftIsNotKnownFromAnotherRoom()
        {
            var run = Fresh();
            run.World.Place("leo", "back_room");
            Assert.IsNull(run.Morning.See("leo").FoodWithinReach,
                "he is nowhere near the pantry, so the question does not arise for him");

            run.World.Place("leo", "kitchen");
            Assert.AreEqual(true, run.Morning.See("leo").FoodWithinReach);
        }

        [Test]
        public void MyHungerIsMineAndNobodyElseIsOnHere()
        {
            var run = Fresh();
            run.World.SetHunger("daniel", 0.9);
            run.World.SetHunger("leo", 0.1);

            Assert.AreEqual(0.9, run.Morning.See("daniel").Hunger, 1e-9);
            Assert.AreEqual(0.1, run.Morning.See("leo").Hunger, 1e-9);
        }

        [Test]
        public void WhoseRoomThisIsFollowsFromTheHouseAndNotFromWhoIsStandingInIt()
        {
            var run = Fresh();

            run.World.Place("mara", "back_room");
            Assert.IsTrue(run.Morning.See("mara").InOwnRoom);
            Assert.IsFalse(run.Morning.See("mara").InSomebodyElsesRoom);

            run.World.Place("daniel", "back_room");
            Assert.IsFalse(run.Morning.See("daniel").InOwnRoom);
            Assert.IsTrue(run.Morning.See("daniel").InSomebodyElsesRoom);

            run.World.Place("daniel", "kitchen");
            Assert.IsFalse(run.Morning.See("daniel").InSomebodyElsesRoom,
                "the kitchen is nobody private room");
        }

        [Test]
        public void FindingTheWayToSomewhereIsSomethingYouKnowAboutYourOwnHouse()
        {
            var run = Fresh();
            run.World.Place("mara", "back_room");
            var mine = run.Morning.See("mara");

            Assert.AreEqual("kitchen", mine.NearestTagged("pantry"));
            Assert.AreEqual(2, mine.DistanceTo("kitchen"));
        }

        [Test]
        public void APerceptIsBuiltFromTheWorldAndNeverHandsBackTheWorld()
        {
            // The type carries no reference anybody could follow to the world
            // state, so there is no way for a rule to reach past it.
            var fields = typeof(Percept).GetProperties()
                .Select(p => p.PropertyType.Name)
                .ToList();

            CollectionAssert.DoesNotContain(fields, nameof(WorldState));
            CollectionAssert.DoesNotContain(fields, nameof(Mind));
        }
    }
}
