using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// Urgency saturation, as S1.1 found it: a want already at the ceiling in
    /// both worlds of a counterfactual cannot show that something pushed it.
    /// </summary>
    public class S11UrgencyTests
    {
        [Test]
        public void BelowTheKneeNothingChanges()
        {
            foreach (var v in new[] { 0.0, 0.1, 0.45, 0.7, 0.85 })
                Assert.AreEqual(v, Accumulate.Knee(v, 0.85), 1e-12);
        }

        [Test]
        public void AboveTheKneeMoreIsAlwaysALittleMoreAndNeverEverything()
        {
            var previous = Accumulate.Knee(0.85, 0.85);
            for (var raw = 0.86; raw < 3.0; raw += 0.01)
            {
                var bent = Accumulate.Knee(raw, 0.85);
                Assert.Greater(bent, previous, "order lost at raw " + raw.ToString("0.00"));
                Assert.Less(bent, 1.0);
                previous = bent;
            }
        }

        [Test]
        public void TheCurveDoesNotJumpAtTheKnee()
        {
            var justBelow = Accumulate.Knee(0.8499, 0.85);
            var justAbove = Accumulate.Knee(0.8501, 0.85);
            Assert.AreEqual(justBelow, justAbove, 0.001);
        }

        [Test]
        public void AKneeAtOneIsSwitchedOff()
        {
            Assert.AreEqual(0.9, Accumulate.Knee(0.9, 1.0), 1e-12);
            Assert.AreEqual(1.2, Accumulate.Knee(1.2, 1.0), 1e-12);
        }

        [Test]
        public void TwoWantsThatUsedToReadTheSameAtTheCeilingNowReadDifferently()
        {
            // The block S1.1 observed, in miniature. Two people want the same
            // thing for the same standing reasons; one also has a feeling pushing
            // it. With the knee, the push shows. Without it, both are pinned.
            MotivationRule Rule() => new MotivationRule
            {
                Id = "peace",
                Motive = "keep_peace",
                ScaledBy = new[]
                {
                    new Scaler { Kind = ScalerKind.Value, Name = "family_safety", Factor = 1.0 },
                    new Scaler { Kind = ScalerKind.Emotion, Name = "anxiety", Factor = 0.4 }
                }
            };

            var calm = new Mind(Bench.Person("a", values: new[] { "family_safety" }));
            var worried = new Mind(Bench.Person("b", values: new[] { "family_safety" }));
            worried.Emotions.Add("anxiety", null, "family_safety", 0.6, 0, "e1");

            double Urgency(Mind mind, double knee)
            {
                var rules = new RuleSet { Motivation = new[] { Rule() }, Deciding = Bench.Dynamics() };
                rules.Deciding.UrgencyKnee = knee;
                return new Motivator(rules).Raise(mind, Bench.Standing(mind.Id), 4, new TraceLog(), 0)
                    .Single().Urgency;
            }

            Assert.AreEqual(Urgency(calm, 1.0), Urgency(worried, 1.0), 1e-9,
                "without the knee the worry is invisible, which is the defect");
            Assert.Greater(Urgency(worried, 0.85), Urgency(calm, 0.85),
                "with the knee the worry shows");
        }
    }
}
