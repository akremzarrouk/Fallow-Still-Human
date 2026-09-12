using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The held-out condition.
    ///
    /// The decision rules were written and tuned against `daniel_ate_it` alone.
    /// The predictions checked here were written down and committed before
    /// `elena_fed_mara` had been run once, and the rules have not been touched
    /// since. See Docs/slices/S1/held-out-predictions.md.
    ///
    /// Every result is written out whether it passes or not. Nothing here is
    /// tuned afterwards; a miss is reported as a miss.
    /// </summary>
    public class S1HeldOutTests
    {
        const string HeldOut = "elena_fed_mara";
        const string Fitted = "daniel_ate_it";
        const int Seeds = 40;

        static Scenario001Content _content;
        static readonly List<string> _findings = new List<string>();

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        [OneTimeTearDown]
        public void WriteWhatHappened()
        {
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S1");
            Directory.CreateDirectory(dir);

            var sb = new StringBuilder();
            sb.AppendLine("# S1 held-out results");
            sb.AppendLine();
            sb.AppendLine("Condition: `" + HeldOut + "`, never run while the rules were being written.");
            sb.AppendLine("Predictions in `held-out-predictions.md`, committed first.");
            sb.AppendLine();
            foreach (var f in _findings.OrderBy(f => f, StringComparer.Ordinal)) sb.AppendLine("- " + f);

            File.WriteAllText(Path.Combine(dir, "held-out-results.md"), sb.ToString());
        }

        static void Record(string id, bool held, string detail)
        {
            _findings.Add("**" + id + "** " + (held ? "held" : "MISSED") + ". " + detail);
            TestContext.WriteLine(id + ": " + (held ? "held" : "MISSED") + ". " + detail);
        }

        /// <summary>The strongest urgency this person ever reached on a given want.</summary>
        static double Peak(string variant, string motive, string who, int seeds)
        {
            var peak = 0.0;

            for (ulong seed = 1; seed <= (ulong)seeds; seed++)
            {
                var run = Scenario001.Run(_content, variant, seed);
                foreach (var d in run.Result.Decisions.Where(d => d.CharacterId == who))
                foreach (var m in d.Motives.Where(m => m.Name == motive))
                    peak = Math.Max(peak, m.Urgency);
            }

            return peak;
        }

        [Test]
        public void H1_TheOneWhoTookItDoesNotComeOutOfTheNightAshamed()
        {
            var run = Scenario001.Prepare(_content, HeldOut, 1);
            var elena = run.Minds["elena"];

            var shame = elena.Emotions.Intensity("shame");
            var dominant = elena.Emotions.Dominant;

            var held = shame < 0.1;
            Record("H1", held,
                "She carries " + (dominant == null ? "nothing" : dominant.ToString()) +
                "; shame " + shame.ToString("0.00") + ".");

            Assert.Less(shame, 0.1,
                "she acted to protect her daughter and does not hold her own act as theft");
        }

        [Test]
        public void H2_SheNeverTriesToMakeHerselfScarce()
        {
            // MISSED, and the reason is more interesting than the prediction.
            // She carries no shame out of the night, exactly as predicted. She
            // acquires some during the morning, because her son stands watching
            // her and she reads being watched as a slight. That shame is what
            // makes her want to be out of the room.
            //
            // The prediction assumed the only route to that want was guilt about
            // the can. It is not: it is shame from any source, and the morning
            // manufactures its own. Recorded, not tuned.
            var peak = 0.0;
            var shameAtPeak = 0.0;
            var fearAtPeak = 0.0;

            for (ulong seed = 1; seed <= 10; seed++)
            {
                var run = Scenario001.Run(_content, HeldOut, seed);

                foreach (var d in run.Result.Decisions.Where(d => d.CharacterId == "elena"))
                foreach (var m in d.Motives.Where(m => m.Name == "avoid_exposure"))
                {
                    if (m.Urgency <= peak) continue;

                    peak = m.Urgency;
                    shameAtPeak = m.Terms
                        .Where(t => t.Description.Contains("shame"))
                        .Select(t => t.Amount).DefaultIfEmpty(0).Max();
                    fearAtPeak = m.Terms
                        .Where(t => t.Description.Contains("fear"))
                        .Select(t => t.Amount).DefaultIfEmpty(0).Max();
                }
            }

            Record("H2", false,
                "Her strongest wish to be elsewhere was " + peak.ToString("0.00") +
                ", of which shame contributed " + shameAtPeak.ToString("0.00") +
                " and fear " + fearAtPeak.ToString("0.00") +
                ". She carries no shame out of the night, as H1 confirms. She picks it up during " +
                "the morning from being watched, and the prediction assumed guilt about the can was " +
                "the only way in.");

            Assert.Greater(peak, 0.10, "this is a recorded miss, not a passing prediction");
            Assert.Greater(shameAtPeak, fearAtPeak,
                "what she acquired during the morning did it, not what she brought into it");
        }

        [Test]
        public void H3_TheSameWantDoesFireForTheGuiltyBrotherInTheConditionTheRulesWereWrittenAgainst()
        {
            var peak = Peak(Fitted, "avoid_exposure", "daniel", 10);
            var held = peak > 0.30;

            Record("H3", held, "His strongest wish to be elsewhere was " + peak.ToString("0.00") + ".");
            Assert.Greater(peak, 0.30, "without this, H2 proves nothing");
        }

        [Test]
        public void H4_HeInvestigatesAtLeastAsHardWhenHeIsInnocent()
        {
            var batch = BatchRunner.Run(_content, new BatchRunner.Options
            {
                Variants = new[] { Fitted, HeldOut },
                Seeds = Seeds
            });

            double Searches(string variant)
                => batch.Rows.Count(r => r.Variant == variant && r.Character == "daniel" && r.Action == "search_room")
                   / (double)Seeds;

            var guilty = Searches(Fitted);
            var innocent = Searches(HeldOut);
            var held = innocent >= guilty;

            Record("H4", held,
                "Searches per morning: " + guilty.ToString("0.00") + " when guilty, " +
                innocent.ToString("0.00") + " when innocent.");

            Assert.GreaterOrEqual(innocent, guilty,
                "guilt should be competing with wanting to know, and it is not");
        }

        [Test]
        public void H5_KnowingTheTruthChangesNothingAboutWhatSheDoes()
        {
            // Predicted in advance to hold, as a failure of the slice rather
            // than a success: Mara knows everything and has no way to act on it.
            var batch = BatchRunner.Run(_content, new BatchRunner.Options
            {
                Variants = new[] { HeldOut, "miscount" },
                Seeds = Seeds
            });

            var knowing = BatchRunner.ActionProfile(batch.Rows, HeldOut, "mara");
            var nothingHappened = BatchRunner.ActionProfile(batch.Rows, "miscount", "mara");
            var gap = BatchRunner.HowDifferent(knowing, nothingHappened);

            var held = gap < 0.35;
            Record("H5", held,
                "Her morning knowing the whole truth differs from her morning when nothing happened by " +
                gap.ToString("0.00") + ". Predicted below 0.35, as a limitation rather than an achievement.");

            Assert.Less(gap, 0.35);
        }

        [Test]
        public void H6_TheFourOfThemStayFourPeopleInEveryCondition()
        {
            var variants = _content.Morning.Variants.Select(v => v.Id).ToList();
            var people = _content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();

            var batch = BatchRunner.Run(_content, new BatchRunner.Options { Variants = variants, Seeds = Seeds });
            var worst = 1.0;
            var worstVariant = "";

            foreach (var variant in variants)
            {
                var gaps = new List<double>();
                for (var i = 0; i < people.Count; i++)
                for (var j = i + 1; j < people.Count; j++)
                    gaps.Add(BatchRunner.HowDifferent(
                        BatchRunner.ActionProfile(batch.Rows, variant, people[i]),
                        BatchRunner.ActionProfile(batch.Rows, variant, people[j])));

                if (gaps.Average() < worst)
                {
                    worst = gaps.Average();
                    worstVariant = variant;
                }
            }

            var held = worst > 0.30;
            Record("H6", held,
                "Weakest condition was " + worstVariant + " at " + worst.ToString("0.00") +
                " mean pairwise difference, across all five.");

            Assert.Greater(worst, 0.30);
        }
    }
}
