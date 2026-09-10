using System.Linq;
using Fallow.Core.Data;
using Fallow.Core.Model;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    public class ProfileTests
    {
        const string SampleJson = @"{
            ""id"": ""sample"",
            ""display_name"": ""Sample"",
            ""age"": 30,
            ""family_role"": ""sibling"",
            ""note"": ""a comment field the loader must ignore"",
            ""traits"": { ""proud"": 0.8, ""anxious"": 0.4 },
            ""values"": [""respect"", ""control"", ""fairness""],
            ""perception"": { ""perceptiveness"": 0.6, ""attention"": { ""threat"": 1.5 } },
            ""expression"": { ""expressiveness"": 0.2 },
            ""initial_beliefs"": [
                { ""predicate"": ""tendency"", ""args"": [""other"", ""does_not_respect_me""], ""confidence"": 0.3 }
            ]
        }";

        [Test]
        public void ParsesIdentityAndTraits()
        {
            var p = ProfileLoader.FromJson(SampleJson);

            Assert.AreEqual("sample", p.Id);
            Assert.AreEqual("Sample", p.DisplayName);
            Assert.AreEqual(30, p.Age);
            Assert.AreEqual("sibling", p.FamilyRole);
            Assert.AreEqual(0.8, p.Trait("proud"), 1e-9);
            Assert.AreEqual(0.4, p.Trait("anxious"), 1e-9);
        }

        [Test]
        public void UnlistedTraitReadsAsZero()
        {
            var p = ProfileLoader.FromJson(SampleJson);
            Assert.AreEqual(0.0, p.Trait("dominant"), 1e-9);
        }

        [Test]
        public void ValueWeightFallsWithRankAndIsZeroForUnheldValues()
        {
            var p = ProfileLoader.FromJson(SampleJson);

            Assert.Greater(p.ValueWeight("respect"), p.ValueWeight("control"));
            Assert.Greater(p.ValueWeight("control"), p.ValueWeight("fairness"));
            Assert.Greater(p.ValueWeight("fairness"), 0.0);
            Assert.AreEqual(0.0, p.ValueWeight("closeness"), 1e-9);
        }

        [Test]
        public void ParsesPerceptionAndAttention()
        {
            var p = ProfileLoader.FromJson(SampleJson);

            Assert.AreEqual(0.6, p.Perceptiveness, 1e-9);
            Assert.AreEqual(1.5, p.Attention("threat"), 1e-9);
        }

        [Test]
        public void UnlistedAttentionReadsAsOne()
        {
            var p = ProfileLoader.FromJson(SampleJson);
            Assert.AreEqual(1.0, p.Attention("support"), 1e-9);
        }

        [Test]
        public void ParsesInitialBeliefs()
        {
            var p = ProfileLoader.FromJson(SampleJson);

            Assert.AreEqual(1, p.InitialBeliefs.Count);
            var b = p.InitialBeliefs[0];
            Assert.AreEqual("tendency", b.Predicate);
            CollectionAssert.AreEqual(new[] { "other", "does_not_respect_me" }, b.Args.ToArray());
            Assert.AreEqual(0.3, b.Confidence, 1e-9);
        }

        [Test]
        public void RelationOfActorIsDerivedFromAge()
        {
            var older = ProfileLoader.FromJson(
                SampleJson.Replace("\"age\": 30", "\"age\": 40").Replace("\"sample\"", "\"older\""));
            var younger = ProfileLoader.FromJson(
                SampleJson.Replace("\"age\": 30", "\"age\": 20").Replace("\"sample\"", "\"younger\""));
            var sameAge = ProfileLoader.FromJson(SampleJson.Replace("\"sample\"", "\"twin\""));
            var me = ProfileLoader.FromJson(SampleJson);

            Assert.AreEqual(Relation.Senior, me.RelationOfActor(older));
            Assert.AreEqual(Relation.Junior, me.RelationOfActor(younger));
            Assert.AreEqual(Relation.Peer, me.RelationOfActor(sameAge));
        }

        [Test]
        public void IAmMyselfEvenNextToSomeoneMyOwnAge()
        {
            var me = ProfileLoader.FromJson(SampleJson);
            var twin = ProfileLoader.FromJson(SampleJson.Replace("\"sample\"", "\"twin\""));

            Assert.AreEqual(Relation.Self, me.RelationOfActor(me));
            Assert.AreNotEqual(Relation.Self, me.RelationOfActor(twin));
        }

        [Test]
        public void MinorIsDerivedFromAge()
        {
            var seventeen = ProfileLoader.FromJson(SampleJson.Replace("\"age\": 30", "\"age\": 17"));
            var eighteen = ProfileLoader.FromJson(SampleJson.Replace("\"age\": 30", "\"age\": 18"));

            Assert.IsTrue(seventeen.IsMinor);
            Assert.IsFalse(eighteen.IsMinor);
        }

        [Test]
        public void ShippedCastLoadsAndValidatesAgainstTheVocabulary()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var cast = ProfileLoader.LoadDirectory(TestPaths.Minds);

            CollectionAssert.AreEquivalent(
                new[] { "leo", "daniel", "mara", "elena" },
                cast.Keys.ToArray());

            var problems = cast.Values.SelectMany(p => ProfileValidator.Validate(p, vocab)).ToList();
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void ValidatorRejectsAnUnknownTraitName()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var p = ProfileLoader.FromJson(SampleJson.Replace("\"proud\"", "\"prowd\""));

            var problems = ProfileValidator.Validate(p, vocab);

            Assert.IsNotEmpty(problems);
            StringAssert.Contains("prowd", string.Join("\n", problems));
        }

        [Test]
        public void ValidatorRejectsATraitOutsideZeroToOne()
        {
            var vocab = VocabularyLoader.LoadFile(System.IO.Path.Combine(TestPaths.Rules, "vocabulary.json"));
            var p = ProfileLoader.FromJson(SampleJson.Replace("\"proud\": 0.8", "\"proud\": 1.8"));

            var problems = ProfileValidator.Validate(p, vocab);

            Assert.IsNotEmpty(problems);
            StringAssert.Contains("proud", string.Join("\n", problems));
        }
    }
}
