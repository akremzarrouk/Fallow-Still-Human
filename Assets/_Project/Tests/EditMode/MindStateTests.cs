using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    public class AccumulateTests
    {
        [Test]
        public void PositiveEvidenceClosesPartOfTheRemainingGap()
        {
            Assert.AreEqual(0.40, Accumulate.Toward(0.25, 0.20), 1e-9);
        }

        [Test]
        public void NegativeEvidenceTakesPartOfWhatIsThere()
        {
            Assert.AreEqual(0.32, Accumulate.Toward(0.40, -0.20), 1e-9);
        }

        [Test]
        public void CertaintyIsApproachedButNeverReached()
        {
            var v = 0.0;
            for (var i = 0; i < 200; i++) v = Accumulate.Toward(v, 0.30);

            Assert.Less(v, 1.0);
            Assert.Greater(v, 0.99);
        }

        [Test]
        public void NothingEverLeavesZeroToOne()
        {
            Assert.AreEqual(0.0, Accumulate.Toward(0.0, -0.9), 1e-9);
            Assert.LessOrEqual(Accumulate.Toward(0.99, 5.0), 1.0);
            Assert.GreaterOrEqual(Accumulate.Toward(0.01, -5.0), 0.0);
        }
    }

    public class BeliefStoreTests
    {
        [Test]
        public void AnUnheldBeliefHasNoConfidence()
        {
            var s = new BeliefStore();
            Assert.AreEqual(0.0, s.Confidence("tendency", "x", "lies"), 1e-9);
        }

        [Test]
        public void SeededBeliefsArriveWithoutJustification()
        {
            var s = new BeliefStore();
            s.Seed(new BeliefSeed("tendency", new[] { "x", "lies" }, 0.3));

            Assert.AreEqual(0.3, s.Confidence("tendency", "x", "lies"), 1e-9);
            Assert.IsEmpty(s.Get("tendency", "x", "lies").Justifications);
        }

        [Test]
        public void EvidenceMovesConfidenceAndIsRecordedAsTheReason()
        {
            var s = new BeliefStore();
            s.Seed(new BeliefSeed("tendency", new[] { "x", "lies" }, 0.25));

            s.Nudge("tendency", new[] { "x", "lies" }, 0.20, justificationTraceId: 41);

            Assert.AreEqual(0.40, s.Confidence("tendency", "x", "lies"), 1e-9);
            CollectionAssert.AreEqual(new[] { 41 }, s.Get("tendency", "x", "lies").Justifications.ToArray());
        }

        [Test]
        public void TwoBeliefsThatContradictEachOtherBothStand()
        {
            var s = new BeliefStore();
            s.Seed(new BeliefSeed("more_knowledgeable", new[] { "x", "survival" }, 0.7));
            s.Seed(new BeliefSeed("tendency", new[] { "x", "does_not_respect_me" }, 0.6));

            Assert.AreEqual(0.7, s.Confidence("more_knowledgeable", "x", "survival"), 1e-9);
            Assert.AreEqual(0.6, s.Confidence("tendency", "x", "does_not_respect_me"), 1e-9);
            Assert.AreEqual(2, s.All.Count());
        }
    }

    public class LedgerTests
    {
        [Test]
        public void NothingRememberedIsNoStrength()
        {
            var l = new Ledger();
            Assert.AreEqual(0.0, l.Strength("x", "helped_me"), 1e-9);
        }

        [Test]
        public void RepeatedKindnessAccumulatesWithoutRunningAway()
        {
            var l = new Ledger();
            for (var i = 0; i < 20; i++) l.Add("x", "protected_family", 0.5, traceId: i, eventId: "e" + i);

            Assert.Greater(l.Strength("x", "protected_family"), 0.9);
            Assert.LessOrEqual(l.Strength("x", "protected_family"), 1.0);
        }

        [Test]
        public void EntriesStayIndividuallyNameableNotJustSummed()
        {
            var l = new Ledger();
            l.Add("x", "overruled_me", 0.7, traceId: 1, eventId: "b05");
            l.Add("x", "proved_right", 0.6, traceId: 2, eventId: "b03");

            var about = l.About("x");
            Assert.AreEqual(2, about.Count);
            CollectionAssert.AreEquivalent(new[] { "b05", "b03" }, about.Select(r => r.EventId).ToArray());
            Assert.AreEqual("overruled_me", about.Single(r => r.EventId == "b05").Entry);
        }

        [Test]
        public void WhatIRememberAboutOnePersonSaysNothingAboutAnother()
        {
            var l = new Ledger();
            l.Add("x", "overruled_me", 0.7, traceId: 1, eventId: "b05");

            Assert.AreEqual(0.0, l.Strength("y", "overruled_me"), 1e-9);
            Assert.IsEmpty(l.About("y"));
        }
    }

    public class EmotionSetTests
    {
        [Test]
        public void FeelingTheSameThingTwiceDeepensItRatherThanDoublingIt()
        {
            var e = new EmotionSet();
            e.Add("shame", "x", "respect", 0.4, traceId: 1, eventId: "b05");
            e.Add("shame", "x", "respect", 0.4, traceId: 2, eventId: "p01");

            Assert.AreEqual(0.64, e.Intensity("shame", "x"), 1e-9);
            Assert.AreEqual(1, e.Live.Count);
            CollectionAssert.AreEqual(new[] { 1, 2 }, e.Live[0].Causes.ToArray());
        }

        [Test]
        public void TheSameEmotionAboutDifferentPeopleStaysSeparate()
        {
            var e = new EmotionSet();
            e.Add("anger", "x", "respect", 0.5, traceId: 1, eventId: "a");
            e.Add("anger", "y", "respect", 0.2, traceId: 2, eventId: "b");

            Assert.AreEqual(2, e.Live.Count);
            Assert.AreEqual(0.5, e.Intensity("anger", "x"), 1e-9);
            Assert.AreEqual(0.2, e.Intensity("anger", "y"), 1e-9);
        }

        [Test]
        public void EveryEmotionKnowsWhatItWasAboutAndWhichConcernItTouched()
        {
            var e = new EmotionSet();
            e.Add("shame", "x", "respect", 0.4, traceId: 7, eventId: "b05");

            var inst = e.Live.Single();
            Assert.AreEqual("shame", inst.Type);
            Assert.AreEqual("x", inst.TargetId);
            Assert.AreEqual("respect", inst.Concern);
            Assert.AreEqual("b05", inst.LastEventId);
        }

        [Test]
        public void FeelingsFadeAndFaintOnesStopBeingFeltAtAll()
        {
            var e = new EmotionSet();
            e.Add("anger", "x", "respect", 0.5, traceId: 1, eventId: "a");
            e.Add("fear", "y", "family_safety", 0.06, traceId: 2, eventId: "b");

            e.Decay(0.5, floor: 0.05);

            Assert.AreEqual(0.25, e.Intensity("anger", "x"), 1e-9);
            Assert.AreEqual(0.0, e.Intensity("fear", "y"), 1e-9);
            Assert.AreEqual(1, e.Live.Count);
        }

        [Test]
        public void TheStrongestFeelingIsTheDominantOneAndTiesResolveTheSameWayEveryTime()
        {
            var e = new EmotionSet();
            e.Add("fear", "y", "family_safety", 0.3, traceId: 1, eventId: "a");
            e.Add("anger", "x", "respect", 0.6, traceId: 2, eventId: "b");
            Assert.AreEqual("anger", e.Dominant.Type);

            var tied = new EmotionSet();
            tied.Add("shame", null, "respect", 0.4, traceId: 1, eventId: "a");
            tied.Add("anger", null, "respect", 0.4, traceId: 2, eventId: "b");
            Assert.AreEqual("anger", tied.Dominant.Type, "ties break by name so runs stay reproducible");
        }

        [Test]
        public void NoFeelingsMeansNoDominantOne()
        {
            Assert.IsNull(new EmotionSet().Dominant);
        }
    }

    public class TraceLogTests
    {
        [Test]
        public void EveryRecordGetsAnIdAndCanBeReadBack()
        {
            var t = new TraceLog();
            var id = t.Add(TraceKind.Event, null, "b05", "Leo refuses in front of everyone.");

            Assert.AreEqual(id, t.Get(id).Id);
            Assert.AreEqual(TraceKind.Event, t.Get(id).Kind);
            Assert.AreEqual("b05", t.Get(id).EventId);
        }

        [Test]
        public void AChainWalksBackFromAFeelingToTheThingThatHappened()
        {
            var t = new TraceLog();
            var ev = t.Add(TraceKind.Event, null, "b05", "Leo refuses in front of everyone.");
            var acc = t.Add(TraceKind.Access, "daniel", "b05", "Daniel was in the room.", new[] { ev });
            var interp = t.Add(TraceKind.Interpretation, "daniel", "b05", "Read as disrespect.", new[] { acc });
            var exp = t.Add(TraceKind.Experience, "daniel", "b05", "Stored as disrespect.", new[] { interp });
            var app = t.Add(TraceKind.Appraisal, "daniel", "b05", "Respect violated, with an audience.", new[] { exp });
            var emo = t.Add(TraceKind.Emotion, "daniel", "b05", "Shame 0.55.", new[] { app });

            var chain = t.Chain(emo).ToList();

            CollectionAssert.AreEqual(
                new[] { emo, app, exp, interp, acc, ev },
                chain.Select(r => r.Id).ToArray());
            Assert.GreaterOrEqual(chain.Count, 3);
        }

        [Test]
        public void WhyPrintsTheChainInWordsEndingAtTheEvent()
        {
            var t = new TraceLog();
            var ev = t.Add(TraceKind.Event, null, "b05", "Leo refuses in front of everyone.");
            var interp = t.Add(TraceKind.Interpretation, "daniel", "b05", "Read as disrespect.", new[] { ev });
            var emo = t.Add(TraceKind.Emotion, "daniel", "b05", "Shame 0.55.", new[] { interp });

            var why = t.Why(emo);

            StringAssert.Contains("Shame 0.55.", why);
            StringAssert.Contains("Read as disrespect.", why);
            StringAssert.Contains("Leo refuses in front of everyone.", why);
        }

        [Test]
        public void ARecordCanRestOnMoreThanOneReasonWithoutRepeatingAny()
        {
            var t = new TraceLog();
            var a = t.Add(TraceKind.Event, null, "e", "the event");
            var b = t.Add(TraceKind.Interpretation, "x", "e", "a reading", new[] { a });
            var c = t.Add(TraceKind.Experience, "x", "e", "a memory", new[] { a });
            var d = t.Add(TraceKind.Appraisal, "x", "e", "an appraisal", new[] { b, c });

            var ids = t.Chain(d).Select(r => r.Id).ToList();

            CollectionAssert.AreEquivalent(new[] { d, b, c, a }, ids);
            Assert.AreEqual(4, ids.Distinct().Count());
        }

        [Test]
        public void RecordsCanBeFilteredByPersonAndByEvent()
        {
            var t = new TraceLog();
            t.Add(TraceKind.Event, null, "e1", "one");
            t.Add(TraceKind.Interpretation, "x", "e1", "x reads it");
            t.Add(TraceKind.Interpretation, "y", "e1", "y reads it");
            t.Add(TraceKind.Interpretation, "x", "e2", "x reads another");

            Assert.AreEqual(2, t.For("x").Count);
            Assert.AreEqual(3, t.ForEvent("e1").Count);
            Assert.AreEqual(1, t.For("x", "e2").Count);
        }
    }
}
