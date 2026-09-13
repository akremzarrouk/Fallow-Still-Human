using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The slice S1 experiment.
    ///
    /// The hypothesis is narrow: do the minds built in S0 produce meaningfully
    /// different physical decisions when put in the same house on the same
    /// morning? One run cannot answer that, because one run cannot tell a
    /// difference that comes from the people apart from a difference that comes
    /// from the seed. The batch can.
    /// </summary>
    public class S1ExperimentTests
    {
        const int Seeds = 40;

        static Scenario001Content _content;
        static BatchRunner.Batch _batch;
        static IReadOnlyList<string> _variants;
        static IReadOnlyList<string> _people;

        [OneTimeSetUp]
        public void RunTheBatchOnce()
        {
            _content = Scenario001Content.Load(TestPaths.DataRoot);
            _variants = _content.Morning.Variants.Select(v => v.Id).ToList();
            _people = _content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();

            _batch = BatchRunner.Run(_content, new BatchRunner.Options
            {
                Variants = _variants,
                Seeds = Seeds,
                FirstSeed = 1
            });

            WriteReports();
        }

        static string Dir(params string[] parts)
        {
            var path = Path.Combine(
                new[] { TestPaths.ProjectRoot, "Docs", "slices", "S1" }.Concat(parts).ToArray());
            Directory.CreateDirectory(path);
            return path;
        }

        static void WriteReports()
        {
            var batchDir = Dir("batch");
            File.WriteAllText(Path.Combine(batchDir, "decisions.csv"), BatchRunner.ToCsv(_batch.Rows));

            var traces = Dir("traces");
            foreach (var variant in _variants)
            {
                var run = Scenario001.Run(_content, variant, 1);
                File.WriteAllText(Path.Combine(traces, "morning-" + variant + ".md"), S1Report.Morning(run));
            }

            var sb = new StringBuilder();
            sb.AppendLine("# What each of them did with the morning");
            sb.AppendLine();
            sb.AppendLine("Across " + Seeds + " seeds per variant, " + _batch.Summary.Runs + " mornings in all.");
            sb.AppendLine();
            foreach (var variant in _variants)
            {
                sb.AppendLine(S1Report.WhatEachOfThemDid(_content, _batch, variant));
                sb.AppendLine();
            }
            File.WriteAllText(Path.Combine(batchDir, "what-each-of-them-did.md"), sb.ToString());
            File.WriteAllText(Path.Combine(batchDir, "what-was-behind-it.md"),
                S1Report.WhatTheyWanted(_content, _batch));

            var full = Scenario001.Run(_content, "daniel_ate_it", 1);
            File.WriteAllText(Path.Combine(traces, "full-trace-daniel_ate_it-seed1.txt"), S1Report.FullTrace(full));
        }

        // ---- the experiment ----

        [Test]
        public void TheFourOfThemSpendTheMorningDifferently()
        {
            var report = new StringBuilder();
            var worst = 1.0;

            foreach (var variant in _variants)
            {
                var gaps = new List<double>();
                for (var i = 0; i < _people.Count; i++)
                for (var j = i + 1; j < _people.Count; j++)
                {
                    var gap = BatchRunner.HowDifferent(
                        BatchRunner.ActionProfile(_batch.Rows, variant, _people[i]),
                        BatchRunner.ActionProfile(_batch.Rows, variant, _people[j]));
                    gaps.Add(gap);
                    report.AppendLine(variant + ": " + _people[i] + " vs " + _people[j] + " = " + gap.ToString("0.00"));
                }

                var mean = gaps.Average();
                report.AppendLine(variant + ": mean " + mean.ToString("0.00") + ", closest pair " + gaps.Min().ToString("0.00"));
                worst = Math.Min(worst, mean);
            }

            TestContext.WriteLine(report.ToString());
            Assert.Greater(worst, 0.30,
                "if their mornings look alike, the differences in the people are not reaching their behaviour");
        }

        [Test]
        public void WhatTheyWantIsDifferentToo()
        {
            // Behaviour differing is not enough on its own: it could differ for
            // one shared reason. The wants behind it should differ as well.
            var leading = _people.ToDictionary(
                id => id,
                id => _batch.Rows.Where(r => r.Character == id)
                    .GroupBy(r => r.Motive.Split(':')[0])
                    .OrderByDescending(g => g.Count())
                    .First().Key,
                StringComparer.Ordinal);

            foreach (var pair in leading) TestContext.WriteLine(pair.Key + " mostly acts out of " + pair.Value);

            Assert.Greater(leading.Values.Distinct().Count(), 1,
                "everybody doing everything for the same reason is one person in four bodies");
        }

        [Test]
        public void RandomnessSettlesOnlyWhatIsGenuinelyOpen()
        {
            var real = _batch.Summary.AmbiguousShare * (1.0 - _batch.Summary.InterchangeableShare);

            TestContext.WriteLine(
                "choices too close to call: " + _batch.Summary.AmbiguousShare.ToString("P1") +
                " of " + _batch.Summary.Decisions + ", of which " +
                _batch.Summary.InterchangeableShare.ToString("P1") +
                " were the same act aimed somewhere else (which way to walk out).");
            TestContext.WriteLine("ties between genuinely different actions: " + real.ToString("P1"));

            // DEFECT, recorded rather than tuned away. The design says a share
            // this high means the weighing is too flat, and that the fix belongs
            // in the rules rather than in the band. The rules were frozen before
            // the held-out condition was run, so the number is pinned here and
            // the argument is in the S1 review.
            Assert.Less(real, 0.45, "worse than it already is");
            Assert.Greater(real, 0.30, "if this starts failing the flatness is fixed, and the gate should come down to 0.30");
        }

        [Test]
        public void SomebodyStillPacesBetweenTwoRoomsAndThisIsHowBadly()
        {
            var worst = 0;
            string who = null;

            foreach (var group in _batch.Rows
                         .Where(r => r.Action == "go_to")
                         .GroupBy(r => r.Variant + "/" + r.Seed + "/" + r.Character))
            {
                var moves = group.OrderBy(r => r.Minute).Select(r => r.Target).ToList();
                var backAndForth = 0;

                for (var i = 2; i < moves.Count; i++)
                    if (moves[i] == moves[i - 2] && moves[i] != moves[i - 1])
                        backAndForth++;

                if (backAndForth > worst)
                {
                    worst = backAndForth;
                    who = group.Key;
                }
            }

            TestContext.WriteLine("worst back and forth: " + worst + " (" + who + ")");

            // Was a DEFECT, recorded in S1 with the instruction that when it
            // started failing the gate should come down to 4. It did in S1.2,
            // at a worst of 2, once people stopped being interrupted by feelings
            // they were already carrying and started carrying the reason for a
            // walk into the room they walked to. Turned round as instructed.
            Assert.Less(worst, 4, "pacing is back");
        }

        [Test]
        public void NoConditionProducesTheSameMorningEveryTime()
        {
            foreach (var variant in _variants)
            foreach (var id in _people)
            {
                var profile = BatchRunner.ActionProfile(_batch.Rows, variant, id);
                if (profile.Count == 0) continue;

                Assert.Less(profile.Values.Max(), 0.95,
                    variant + "/" + id + " does one thing and nothing else, which is not a person");
            }
        }

        [Test]
        public void TheHiddenTruthBarelyReachesAnybodyBehaviour()
        {
            // The other half of the question, and the one the slice does worst
            // on. Four different things happened in the night, and the mornings
            // that follow are nearly the same morning. Measured against how far
            // apart two people are, so the two numbers can be read side by side.
            var report = new StringBuilder();
            var biggest = 0.0;

            foreach (var id in _people)
            {
                for (var i = 0; i < _variants.Count; i++)
                for (var j = i + 1; j < _variants.Count; j++)
                {
                    var gap = BatchRunner.HowDifferent(
                        BatchRunner.ActionProfile(_batch.Rows, _variants[i], id),
                        BatchRunner.ActionProfile(_batch.Rows, _variants[j], id));

                    biggest = Math.Max(biggest, gap);
                    if (gap > 0.02)
                        report.AppendLine(
                            id + ": " + _variants[i] + " vs " + _variants[j] + " = " + gap.ToString("0.00"));
                }
            }

            TestContext.WriteLine(report.Length == 0
                ? "no condition changed anybody morning by more than 0.02"
                : report.ToString());
            TestContext.WriteLine("largest difference any hidden truth made: " + biggest.ToString("0.00"));
            TestContext.WriteLine("for comparison, two different people differ by about 0.61");

            // DEFECT, recorded rather than tuned away. What happened in the night
            // changes who is carrying what, and almost nothing about what anybody
            // does with their morning, because the only outlet private shame has
            // is one want that loses to every other want.
            Assert.Less(biggest, 0.30,
                "if this starts failing, circumstances have started to reach behaviour and the gate should be turned round");
        }

        [Test]
        public void WhoYouAreReachesBehaviourFarMoreThanWhatHappened()
        {
            var betweenPeople = new List<double>();
            var acrossConditions = new List<double>();

            foreach (var variant in _variants)
            for (var i = 0; i < _people.Count; i++)
            for (var j = i + 1; j < _people.Count; j++)
                betweenPeople.Add(BatchRunner.HowDifferent(
                    BatchRunner.ActionProfile(_batch.Rows, variant, _people[i]),
                    BatchRunner.ActionProfile(_batch.Rows, variant, _people[j])));

            foreach (var id in _people)
            for (var i = 0; i < _variants.Count; i++)
            for (var j = i + 1; j < _variants.Count; j++)
                acrossConditions.Add(BatchRunner.HowDifferent(
                    BatchRunner.ActionProfile(_batch.Rows, _variants[i], id),
                    BatchRunner.ActionProfile(_batch.Rows, _variants[j], id)));

            TestContext.WriteLine(
                "two people, same morning: " + betweenPeople.Average().ToString("0.00") +
                " | one person, different nights: " + acrossConditions.Average().ToString("0.00"));

            Assert.Greater(betweenPeople.Average(), acrossConditions.Average() * 4,
                "personality is doing the work and circumstance is not");
        }

        [Test]
        public void KnowledgeStaysLocalAcrossEveryRunInTheBatch()
        {
            foreach (var variant in _variants)
            for (ulong seed = 1; seed <= 5; seed++)
            {
                var run = Scenario001.Run(_content, variant, seed);

                foreach (var e in run.Result.Events)
                foreach (var id in run.World.Inhabitants)
                {
                    if (e.AccessFor(id) != Access.None) continue;
                    Assert.IsFalse(run.Minds[id].Experiences.Any(x => x.EventId == e.Id),
                        variant + "/" + seed + ": " + id + " knows about " + e.Id + " and should not");
                }
            }
        }

        [Test]
        public void ExchangingTwoPeopleDataChangesWhatTheyDoWithoutTouchingARule()
        {
            // The claim the whole slice rests on. If swapping who these two are
            // does not change what they do, the rules are carrying the behaviour
            // and the people are decoration.
            var swapped = new Dictionary<string, Profile>(StringComparer.Ordinal);
            foreach (var pair in _content.Cast) swapped[pair.Key] = pair.Value;
            swapped["daniel"] = Wearing(_content.Cast["daniel"], _content.Cast["leo"]);
            swapped["leo"] = Wearing(_content.Cast["leo"], _content.Cast["daniel"]);

            var otherwise = new Scenario001Content(
                _content.Vocabulary, swapped, _content.Backstory, _content.Morning, _content.Rules);

            var before = BatchRunner.Run(_content, new BatchRunner.Options
            { Variants = new[] { "daniel_ate_it" }, Seeds = 10 });
            var after = BatchRunner.Run(otherwise, new BatchRunner.Options
            { Variants = new[] { "daniel_ate_it" }, Seeds = 10 });

            var change = BatchRunner.HowDifferent(
                BatchRunner.ActionProfile(before.Rows, "daniel_ate_it", "daniel"),
                BatchRunner.ActionProfile(after.Rows, "daniel_ate_it", "daniel"));

            TestContext.WriteLine("his morning changed by " + change.ToString("0.00") + " when he became his brother");
            Assert.Greater(change, 0.15, "the people are not carrying the difference; the rules are");
        }

        static Profile Wearing(Profile self, Profile other)
            => new Profile(
                self.Id, self.DisplayName, self.Age, self.FamilyRole,
                other.Traits, other.Values, other.Perceptiveness, other.AttentionWeights,
                self.InitialBeliefs, other.Expressiveness, other.HungerRate);

        // ---- the carry-over defects from S0 ----

        [Test]
        public void NoFeelingIsEverStrongerThanFeelingSomethingCompletely()
        {
            var strongest = 0.0;

            foreach (var variant in _variants)
            for (ulong seed = 1; seed <= 5; seed++)
            {
                var run = Scenario001.Run(_content, variant, seed);
                foreach (var mind in run.Minds.Values)
                foreach (var e in mind.Emotions.Live)
                {
                    strongest = Math.Max(strongest, e.Intensity);
                    Assert.LessOrEqual(e.Intensity, 1.0, mind.Id + " feels " + e.Type + " more than completely");
                    Assert.GreaterOrEqual(e.Intensity, 0.0);
                }
            }

            TestContext.WriteLine("strongest feeling anywhere in the batch: " + strongest.ToString("0.000"));
            Assert.Greater(strongest, 0.5, "if nothing ever gets strong, the scale is not being used");
        }

        [Test]
        public void SalienceCanTellOneMemoryFromAnother()
        {
            var run = Scenario001.Run(_content, "daniel_ate_it", 1);
            var all = run.Minds.Values.SelectMany(m => m.Experiences).Select(x => x.Salience).ToList();

            var atTheCeiling = all.Count(v => v >= 0.99) / (double)all.Count;
            var distinct = all.Select(v => Math.Round(v, 2)).Distinct().Count();

            TestContext.WriteLine(
                all.Count + " memories, " + distinct + " distinct levels, " +
                atTheCeiling.ToString("P0") + " of them at the ceiling, " +
                "range " + all.Min().ToString("0.00") + " to " + all.Max().ToString("0.00"));

            Assert.Less(atTheCeiling, 0.5, "most memories sitting at the top means salience says nothing");
            Assert.Greater(distinct, 5, "salience needs to separate memories, not label them all the same");
        }

        [Test]
        public void RecallFadesButUrgencyIsSaturatedSoNobodyCanTell()
        {
            // The memory scaler does fade: the same want measured on somebody
            // whose urgency is not already at the ceiling drops away over the
            // morning. On Daniel it cannot show, because the standing terms in
            // wanting to know what happened, his values and his claim on the
            // household, already carry it to the top of the scale on their own.
            // Fading something that is saturated changes nothing.
            var run = Scenario001.Run(_content, "daniel_ate_it", 1);

            double Peak(string who, Func<ActionRecord, bool> when)
                => run.Result.Actions.Where(a => a.CharacterId == who).Where(when)
                    .Select(a => a.LeadingUrgency).DefaultIfEmpty(0).Max();

            var hisEarly = Peak("daniel", a => a.Minute < 20);
            var hisLate = Peak("daniel", a => a.Minute > 60);

            var herEarly = Peak("mara", a => a.Minute < 20);
            var herLate = Peak("mara", a => a.Minute > 60);

            TestContext.WriteLine("daniel: early " + hisEarly.ToString("0.00") + ", late " + hisLate.ToString("0.00"));
            TestContext.WriteLine("mara:   early " + herEarly.ToString("0.00") + ", late " + herLate.ToString("0.00"));

            Assert.AreEqual(hisEarly, hisLate, 1e-6,
                "DEFECT: his strongest want is pinned at the ceiling all morning and cannot fade");
            Assert.Less(herLate, herEarly,
                "on somebody not at the ceiling, the morning does stop pressing as it recedes");
        }
    }
}
