using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>S1.3: what an outcome is, and what it is not allowed to be.</summary>
    public class S13LifecycleTests
    {
        [Test]
        public void AnOutcomeIsJudgedOnlyByWhatHappenedToTheNeed()
        {
            Assert.AreEqual(OutcomeKind.PartlySatisfied, Outcomes.OfConsequence(true, 0.80, 0.35));
            Assert.AreEqual(OutcomeKind.Satisfied, Outcomes.OfConsequence(true, 0.30, 0.0));
            Assert.AreEqual(OutcomeKind.Unresolved, Outcomes.OfConsequence(true, 0.80, 0.80), "it happened and the need did not move");
            Assert.AreEqual(OutcomeKind.Blocked, Outcomes.OfConsequence(false, 0.80, 0.80), "it could not happen at all");
            Assert.AreEqual(OutcomeKind.Blocked, Outcomes.OfConsequence(false, 0.80, 0.30), "not happening is blocked whatever else moved the need");
        }

        [Test]
        public void GivingUpOnArrivalIsJudgedByWhyItWasGivenUp()
        {
            Assert.AreEqual(OutcomeKind.Blocked, Outcomes.OfLapse(Commitment.Impossible));
            Assert.AreEqual(OutcomeKind.Unresolved, Outcomes.OfLapse(Commitment.NotWorthIt));
            Assert.AreEqual(OutcomeKind.NoLongerRelevant, Outcomes.OfLapse(Commitment.NoLongerWanted));
            Assert.IsNull(Outcomes.OfLapse(Commitment.Held));
            Assert.IsNull(Outcomes.OfLapse(Commitment.None));
        }

        static RuleSet Hunger()
            => new RuleSet
            {
                Motivation = new List<MotivationRule>
                {
                    new MotivationRule
                    {
                        Id = "hunger", Motive = "get_food",
                        ScaledBy = new[] { new Scaler { Kind = ScalerKind.Need, Name = "hunger", Factor = 1.0 } }
                    }
                },
                Deciding = Bench.Dynamics()
            };

        [Test]
        public void ARecordOfWhatWasDoneMovesNoWantItOnlySaysWhyTheWantIsWhereItIs()
        {
            // No decay, no bonus, no timer: the same body raises exactly the same
            // want with or without a record of eating. What changes is that the
            // want can say why the body is where it is.
            var percept = Bench.Standing("mara", hunger: 0.35);

            var without = new Motivator(Hunger()).Raise(new Mind(Bench.Person("mara")), percept, 4, new TraceLog(), 0).Single();

            var mind = new Mind(Bench.Person("mara"));
            mind.Record(new PursuitOutcome("get_food", "get_food", "eat", "hunger", 0.80, 0.35, OutcomeKind.PartlySatisfied, 42, "m042-007") { TraceId = 77 });
            var with = new Motivator(Hunger()).Raise(mind, percept, 4, new TraceLog(), 0).Single();

            Assert.AreEqual(without.Urgency, with.Urgency, 0.0, "a record of eating moved the want");
            var term = with.Terms.Single();
            CollectionAssert.Contains(term.Drew.ToList(), 77, "the want cannot be walked back to the eating");
            StringAssert.Contains("partly satisfied by eat at minute 42", term.Description);
            StringAssert.Contains("0.80 -> 0.35", term.Description);
        }

        [Test]
        public void TheRecordAWantRestsOnIsTheLastThingDoneAboutThatNeed()
        {
            var mind = new Mind(Bench.Person("mara"));
            mind.Record(new PursuitOutcome("get_food", "get_food", "eat", "hunger", 0.80, 0.35, OutcomeKind.PartlySatisfied, 42, "e1") { TraceId = 1 });
            mind.Record(new PursuitOutcome("get_food", "get_food", "eat", "hunger", 0.60, 0.60, OutcomeKind.Blocked, 70, "e2") { TraceId = 2 });

            var want = new Motivator(Hunger()).Raise(mind, Bench.Standing("mara", hunger: 0.62), 4, new TraceLog(), 0).Single();
            CollectionAssert.AreEqual(new[] { 2 }, want.Terms.Single().Drew.ToArray());
            StringAssert.Contains("blocked", want.Terms.Single().Description);
        }
    }
}
