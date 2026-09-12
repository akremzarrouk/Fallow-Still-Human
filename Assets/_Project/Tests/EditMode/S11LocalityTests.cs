using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// Knowledge locality, extended from what a person remembers to how a person
    /// is. S1 checked that nobody keeps a memory of something they did not
    /// perceive. S1.1 found that people were still changed by such things,
    /// because every event faded everybody's feelings. These tests are the
    /// invariant that should have existed.
    /// </summary>
    public class S11LocalityTests
    {
        static Scenario001Content _content;

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        static IReadOnlyList<string> Motives => _content.Vocabulary.Set("motives").ToList();

        [Test]
        public void SomethingYouSleptThroughDoesNotChangeHowYouFeelOrWhatYouWant()
        {
            var problems = new List<string>();

            foreach (var variant in _content.Morning.Variants.Where(v => v.NightEvents.Count > 0))
            {
                var pair = Counterfactual.Run(
                    _content, variant.Id, new List<WorldEvent>(), variant.NightEvents,
                    variant.NightEvents.Select(e => e.Id).ToList(), 1, minutes: 0);

                foreach (var p in pair.People.Values)
                {
                    var reached = variant.NightEvents.Any(e => e.AccessFor(p.CharacterId) != Access.None);
                    if (reached) continue;

                    var before = p.ControlFeelings[Scenario001.Stages.AfterOpening];
                    var after = p.TreatmentFeelings[Scenario001.Stages.AfterOpening];
                    if (before != after)
                        problems.Add(variant.Id + "/" + p.CharacterId + " slept through it and feels different: " +
                                     before + "  vs  " + after);

                    foreach (var m in Motives)
                        if (Math.Abs(p.ShiftAtStart(m)) > 1e-9)
                            problems.Add(variant.Id + "/" + p.CharacterId + " slept through it and wants " + m +
                                         " differently by " + p.ShiftAtStart(m).ToString("+0.000;-0.000"));
                }
            }

            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void AMomentInAnotherRoomDoesNotChangeHowYouFeel()
        {
            // The same property during the morning itself: put one person alone
            // in a far room, and let something happen in the kitchen that they
            // cannot see or hear. Their feelings must be exactly what they would
            // have been if it had not happened.
            var quiet = Scenario001.Prepare(_content, "miscount", 1);
            var busy = Scenario001.Prepare(_content, "miscount", 1);

            foreach (var run in new[] { quiet, busy })
            {
                run.World.Place("leo", "bathroom");
                foreach (var id in new[] { "daniel", "mara", "elena" }) run.World.Place(id, "kitchen");
            }

            var extra = new WorldEvent(
                "probe-001", _content.Morning.Day, 5000, EventKind.Action, "daniel", "mara",
                null, "search_belongings", "missing_can", "firm", "direct", "bad", null,
                "Daniel goes through Mara things in the kitchen.",
                new[] { "mara", "elena" }, new string[0], new List<LedgerEffect>(), null, 0);

            Assert.AreEqual(Access.None, extra.AccessFor("leo"));

            var leoBefore = string.Join(", ", busy.Minds["leo"].Emotions.Live.Select(e => e.ToString()));
            busy.Simulation.Apply(extra);
            var leoAfter = string.Join(", ", busy.Minds["leo"].Emotions.Live.Select(e => e.ToString()));

            Assert.AreEqual(leoBefore, leoAfter, "something happened out of his sight and hearing, and he changed");
        }
    }
}
