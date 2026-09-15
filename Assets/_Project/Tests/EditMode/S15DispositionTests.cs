using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Data;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// S1.5, taken apart on a bench: the difference between what a person is
    /// disposed to (a trait, a value), what has happened to them (a feeling, a
    /// memory, the body), and a want that stands for a reason (history, evidence),
    /// under each way of letting traits and values into a want.
    /// </summary>
    public class S15DispositionTests
    {
        static RuleSet Rules(string mode, params MotivationRule[] rules)
        {
            var d = Bench.Dynamics();
            d.Dispositions = mode;
            return new RuleSet { Motivation = rules.ToList(), Deciding = d };
        }

        static MotivationRule KeepingThePeace() => new MotivationRule
        {
            Id = "peace",
            Motive = "keep_peace",
            ScaledBy = new[]
            {
                new Scaler { Kind = ScalerKind.Emotion, Name = "anxiety", Factor = 0.5 },
                new Scaler { Kind = ScalerKind.Trait, Name = "empathetic", Factor = 0.4 },
                new Scaler { Kind = ScalerKind.Value, Name = "family_safety", Factor = 0.2 }
            }
        };

        static Mind Person(string id, double empathetic, double anxiety = 0.0)
        {
            var mind = new Mind(Bench.Person(id, new Dictionary<string, double> { { "empathetic", empathetic } }, new[] { "family_safety" }));
            if (anxiety > 0.0) mind.Emotions.Add("anxiety", null, "family_safety", anxiety, 7, "e1");
            return mind;
        }

        static Motive Want(string mode, Mind mind, MotivationRule rule, TraceLog trace = null)
            => new Motivator(Rules(mode, rule)).Raise(mind, Bench.Standing(mind.Id, present: new[] { "elena" }), 4, trace ?? new TraceLog(), 0).FirstOrDefault();

        // ---- disposition ----

        [Test]
        public void ADispositionOnItsOwnIsAWantOnlyWhenItStandsAsAGoal()
        {
            var warm = Person("a", empathetic: 0.9);

            var standing = Want(DispositionMode.Standing, warm, KeepingThePeace());
            Assert.IsNotNull(standing, "as shipped, who you are is enough to want the peace kept");
            Assert.AreEqual(Support.Unsupported, MotivationSources.Of(standing).Class);

            Assert.IsNull(Want(DispositionMode.Respond, warm, KeepingThePeace()), "as a disposition, it has nothing to respond to");
            Assert.IsNull(Want(DispositionMode.Gated, warm, KeepingThePeace()));
        }

        [Test]
        public void GivenTheSameCircumstanceADispositionScalesTheResponse()
        {
            double U(string mode, double empathy, double anxiety) => Want(mode, Person("p", empathy, anxiety), KeepingThePeace()).Urgency;

            // Kept below 1 throughout, where the shipped combination would cap it.
            // Standing: the warm person wants it more by the same amount whatever
            // is happening. Respond: by more the more there is to respond to.
            var standingSmall = U(DispositionMode.Standing, 0.9, 0.2) - U(DispositionMode.Standing, 0.1, 0.2);
            var standingLarge = U(DispositionMode.Standing, 0.9, 0.8) - U(DispositionMode.Standing, 0.1, 0.8);
            Assert.AreEqual(standingSmall, standingLarge, 1e-9);

            var respondSmall = U(DispositionMode.Respond, 0.9, 0.2) - U(DispositionMode.Respond, 0.1, 0.2);
            var respondLarge = U(DispositionMode.Respond, 0.9, 0.8) - U(DispositionMode.Respond, 0.1, 0.8);
            Assert.Greater(respondSmall, 0.0);
            Assert.AreEqual(respondSmall * 4.0, respondLarge, 1e-9, "four times the feeling, four times the difference a warm temperament makes");

            // And the arithmetic is exactly C x (1 + D), with the terms still summing to it.
            var want = Want(DispositionMode.Respond, Person("p", 0.9, 0.4), KeepingThePeace());
            var c = 0.4 * 0.5;
            var d = 0.9 * 0.4 + 1.0 * 0.2;
            Assert.AreEqual(c * (1.0 + d), want.Urgency, 1e-9);
            Assert.AreEqual(want.Urgency, want.Terms.Sum(t => t.Amount), 1e-9);
            StringAssert.Contains("in response to", want.Because);
        }

        // ---- circumstance ----

        [Test]
        public void AWantThatOnlyReadsWhatHappenedIsTheSameInEveryMode()
        {
            var shame = new MotivationRule
            {
                Id = "shame",
                Motive = "avoid_exposure",
                ScaledBy = new[] { new Scaler { Kind = ScalerKind.Emotion, Name = "shame", Factor = 0.8 } }
            };

            foreach (var mode in DispositionMode.All)
            {
                var ashamed = new Mind(Bench.Person("a"));
                ashamed.Emotions.Add("shame", null, "respect", 0.5, 7, "e1");
                Assert.AreEqual(0.4, Want(mode, ashamed, shame).Urgency, 1e-9, mode);
                Assert.IsNull(Want(mode, new Mind(Bench.Person("b")), shame), mode + ": without the shame, nothing");
            }
        }

        [Test]
        public void TheGateSwitchesTheWholeStandingPartOnForAnyTraceOfACircumstance()
        {
            // Why the gate is only an ablation: a memory or a feeling that has all
            // but gone lets the whole of who you are back in as a want.
            var faint = Person("p", empathetic: 0.9, anxiety: 0.02);
            var gated = Want(DispositionMode.Gated, faint, KeepingThePeace()).Urgency;
            var respond = Want(DispositionMode.Respond, faint, KeepingThePeace()).Urgency;
            Assert.Greater(gated, 0.5);
            Assert.Less(respond, 0.02);
        }

        // ---- standing, with reasons ----

        [Test]
        public void AWantThatStandsOnHistoryStandsWithNothingHappening()
        {
            var rule = new MotivationRule
            {
                Id = "look",
                Motive = "look_after",
                Scope = MotiveScope.EachPresent,
                ScaledBy = new[]
                {
                    new Scaler { Kind = ScalerKind.Ledger, Entry = "comforted_me", About = "$target", Factor = 0.15 },
                    new Scaler { Kind = ScalerKind.Trait, Name = "empathetic", Factor = 0.15 }
                }
            };
            var mind = Person("a", empathetic: 0.9);
            mind.Ledger.Add("elena", "comforted_me", 0.8, 42, "e9");

            var want = Want(DispositionMode.Respond, mind, rule);
            Assert.IsNotNull(want, "somebody who comforted you is somebody you look out for, with nothing happening");
            var support = MotivationSources.Of(want);
            Assert.IsTrue(support.StandingWithReasons);
            Assert.AreNotEqual(Support.Unsupported, support.Class);
            CollectionAssert.Contains(want.Terms.SelectMany(t => t.Drew).ToList(), 42, "and it can say which moment it stands on");

            var stranger = Person("b", empathetic: 0.9);
            Assert.IsNull(Want(DispositionMode.Respond, stranger, rule), "the same temperament with no history wants nothing");
        }

        [Test]
        public void AnAuthoredBeliefIsNotADispositionAndStillStandsUnderRespond()
        {
            // Recorded, not fixed: the hypothesis is about traits and values. A
            // belief written into a person with nothing behind it keeps raising a
            // want on its own, and the instrument says it is unsupported.
            var rule = new MotivationRule
            {
                Id = "know",
                Motive = "find_out",
                ScaledBy = new[]
                {
                    new Scaler { Kind = ScalerKind.Belief, Predicate = "role_claim", Args = new[] { "$self", "leads_family" }, Factor = 0.3 },
                    new Scaler { Kind = ScalerKind.Value, Name = "control", Factor = 0.5 }
                }
            };
            var profile = new Profile("a", "a", 30, "sibling", new Dictionary<string, double>(), new[] { "control" },
                0.5, new Dictionary<string, double>(), new[] { new BeliefSeed("role_claim", new[] { "a", "leads_family" }, 0.8) });

            var want = Want(DispositionMode.Respond, new Mind(profile), rule);
            Assert.IsNotNull(want);
            Assert.AreEqual(0.24 * 1.5, want.Urgency, 1e-9);
            var support = MotivationSources.Of(want);
            Assert.AreEqual(Support.Unsupported, support.Class);
            Assert.Greater(support.Authored, 0.0);
        }

        // ---- the switch ----

        [Test]
        public void TheShippedRulesKeepTheStandingModeAndEveryModeIsValid()
        {
            var content = Scenario001Content.Load(TestPaths.DataRoot);
            Assert.AreEqual(DispositionMode.Standing, content.Rules.Deciding.Dispositions, "S1.5 is a diagnostic; the shipped rules do not change");

            foreach (var mode in DispositionMode.All)
                CollectionAssert.IsEmpty(DecisionRuleValidator.Validate(S15.Mode(content, mode).Rules, content.Vocabulary), mode);
            CollectionAssert.IsNotEmpty(DecisionRuleValidator.Validate(S15.Mode(content, "sometimes").Rules, content.Vocabulary));
        }
    }
}
