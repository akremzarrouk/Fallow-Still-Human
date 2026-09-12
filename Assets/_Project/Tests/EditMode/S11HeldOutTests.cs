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
    /// The S1.1 held-out condition, `leo_ate_it`.
    ///
    /// Defined in commit 160dc2d before any S1.1 change; rules frozen in 06d92eb;
    /// predictions committed in b310c67 before this file existed or the condition
    /// had ever been run. See Docs/slices/S1.1/held-out-predictions.md.
    ///
    /// Each test checks one prediction exactly as written, and records the result
    /// whether it holds or not.
    /// </summary>
    public class S11HeldOutTests
    {
        const string HeldOut = "leo_ate_it";
        const int Seeds = 20;

        static Scenario001Content _content;
        static readonly SortedDictionary<string, string> _findings = new SortedDictionary<string, string>(StringComparer.Ordinal);

        [OneTimeSetUp]
        public void Load() => _content = Scenario001Content.Load(TestPaths.DataRoot);

        [OneTimeTearDown]
        public void Write()
        {
            var sb = new StringBuilder();
            sb.AppendLine("# S1.1 held-out results");
            sb.AppendLine();
            sb.AppendLine("Condition `" + HeldOut + "`, first run by `S11HeldOutTests`. Predictions in");
            sb.AppendLine("`held-out-predictions.md`, committed before this condition was ever run.");
            sb.AppendLine();
            foreach (var f in _findings.Values) sb.AppendLine("- " + f);

            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S1.1");
            Directory.CreateDirectory(dir);
            File.WriteAllText(Path.Combine(dir, "held-out-results.md"), sb.ToString());
        }

        static void Record(string id, bool held, string detail)
        {
            var line = "**" + id + "** " + (held ? "held" : "MISSED") + ". " + detail;
            _findings[id] = line;
            TestContext.WriteLine(line);
        }

        static IReadOnlyList<string> Motives => _content.Vocabulary.Set("motives").ToList();
        static IReadOnlyList<WorldEvent> Night(string v) => _content.Morning.Variant(v).NightEvents;

        static Counterfactual.Pair Pair(string variant, ulong seed, int? minutes = null)
            => Counterfactual.Run(_content, variant, new List<WorldEvent>(), Night(variant),
                Night(variant).Select(e => e.Id).ToList(), seed, minutes);

        static (double shame, double fear) AfterTheNight(string variant, string who)
        {
            var shame = 0.0;
            var fear = 0.0;
            Scenario001.PrepareWith(_content, variant, Night(variant), 1, (stage, sim) =>
            {
                if (stage != Scenario001.Stages.AfterNight) return;
                shame = sim.Minds[who].Emotions.IntensityAny("shame");
                fear = sim.Minds[who].Emotions.IntensityAny("fear");
            });
            return (shame, fear);
        }

        /// <summary>The shame the night event itself stirred, read from its appraisal record.</summary>
        static double ShameTheNightStirred(string variant, string who)
        {
            var run = Scenario001.Prepare(_content, variant, 1);
            return run.Trace.For(who, "n01")
                .Where(r => r.Kind == Fallow.Core.Tracing.TraceKind.Appraisal && r.Data.TryGetValue("emotion", out var e) && e == "shame")
                .Select(r => double.Parse(r.Data["intensity"], System.Globalization.CultureInfo.InvariantCulture))
                .DefaultIfEmpty(0.0).Max();
        }

        [Test]
        public void P1_ShameNotFear()
        {
            // MISSED on first run, recorded as written and not re-predicted.
            //
            // The prediction compared the shame each culprit's night produced.
            // What a person carries after the night is that shame merged with any
            // shame they already had, because a feeling is kept per kind and per
            // person it is about, not per cause. Daniel came into the night still
            // ashamed of being overruled by his brother on day two; the night's
            // shame about the food was folded into that one number. So "carries"
            // missed for Daniel by 0.02, while the shame the night itself stirred
            // ordered exactly as predicted.
            var leo = AfterTheNight(HeldOut, "leo");
            var daniel = AfterTheNight("daniel_ate_it", "daniel");
            var mara = AfterTheNight("mara_ate_it", "mara");

            var leoNight = ShameTheNightStirred(HeldOut, "leo");
            var danielNight = ShameTheNightStirred("daniel_ate_it", "daniel");
            var maraNight = ShameTheNightStirred("mara_ate_it", "mara");

            var held = leo.shame > leo.fear && leo.shame > daniel.shame && leo.shame > mara.shame;
            Record("P1", held,
                "After the night Leo carries shame " + leo.shame.ToString("0.00") + " and fear " + leo.fear.ToString("0.00") +
                "; Daniel carries shame " + daniel.shame.ToString("0.00") + ", Mara " + mara.shame.ToString("0.00") +
                ". The shame the night itself stirred: Leo " + leoNight.ToString("0.00") + ", Daniel " + danielNight.ToString("0.00") +
                ", Mara " + maraNight.ToString("0.00") + ". Daniel's total includes shame left over from being overruled on day two, " +
                "merged into the same feeling, which the prediction did not account for.");

            Assert.IsFalse(held, "this is a recorded miss; if it starts holding, find out what changed");
            Assert.Greater(leo.shame, leo.fear, "shame over fear held");
            Assert.Greater(leoNight, danielNight, "the night's own shame ordered as predicted against Daniel");
            Assert.Greater(leoNight, maraNight, "and against Mara");
        }

        [Test]
        public void P2_ALargeChangeAtTheStart()
        {
            var leo = Pair(HeldOut, 1, 0).People["leo"];
            var daniel = Pair("daniel_ate_it", 1, 0).People["daniel"].ShiftAtStart("avoid_exposure");
            var mara = Pair("mara_ate_it", 1, 0).People["mara"].ShiftAtStart("avoid_exposure");

            var shift = leo.ShiftAtStart("avoid_exposure");
            var traced = leo.TreatmentAtStart.RestsOnCause.TryGetValue("avoid_exposure", out var t) && t;
            var held = shift > Math.Max(daniel, mara) && traced;

            Record("P2", held, "Leo's `avoid_exposure` at minute zero moved " + shift.ToString("+0.000;-0.000") +
                               " (traceable to the night: " + traced + "), against Daniel " + daniel.ToString("+0.000") +
                               " and Mara " + mara.ToString("+0.000") + ".");

            Assert.Greater(shift, Math.Max(daniel, mara));
            Assert.IsTrue(traced);
        }

        [Test]
        public void P3_TheSameSupplyBelief()
        {
            var shift = Pair(HeldOut, 1, 0).People["leo"].ShiftAtStart("guard_supplies");
            var held = Math.Abs(shift - 0.056) < 0.02;

            Record("P3", held, "Leo's `guard_supplies` at minute zero moved " + shift.ToString("+0.000;-0.000") + ", predicted about +0.056.");
            Assert.AreEqual(0.056, shift, 0.02);
        }

        [Test]
        public void P4_ItLastsLessWellThanMaras()
        {
            double Ratio(string variant, string who)
            {
                var starts = new List<double>();
                var mornings = new List<double>();
                for (ulong seed = 1; seed <= Seeds; seed++)
                {
                    var p = Pair(variant, seed).People[who];
                    starts.Add(p.SensitivityAtStart(Motives));
                    mornings.Add(p.SensitivityOverMorning(Motives));
                }
                return mornings.Average() / starts.Average();
            }

            var leo = Ratio(HeldOut, "leo");
            var mara = Ratio("mara_ate_it", "mara");
            var held = leo < mara;

            Record("P4", held, "Share of the start-of-morning change that lasts, over " + Seeds + " seeds: Leo " +
                               leo.ToString("P0") + ", Mara " + mara.ToString("P0") + ".");
            Assert.Less(leo, mara);
        }

        [Test]
        public void P5_NobodyElseIsTouched()
        {
            var pair = Pair(HeldOut, 1, 0);
            var touched = new List<string>();

            foreach (var p in pair.People.Values.Where(p => p.CharacterId != "leo"))
            {
                if (p.ControlFeelings[Scenario001.Stages.AfterOpening] != p.TreatmentFeelings[Scenario001.Stages.AfterOpening])
                    touched.Add(p.CharacterId + " feels different");
                foreach (var m in Motives)
                    if (Math.Abs(p.ShiftAtStart(m)) > 1e-12) touched.Add(p.CharacterId + " wants " + m + " differently");
            }

            Record("P5", touched.Count == 0, touched.Count == 0
                ? "Daniel, Elena and Mara have exactly the feelings and wants of the control at the start."
                : string.Join("; ", touched) + ".");
            Assert.IsEmpty(touched);
        }

        [Test]
        public void P6_ItDoesNotReachHisFirstDecision()
        {
            var differed = new List<string>();
            for (ulong seed = 1; seed <= Seeds; seed++)
            {
                var p = Pair(HeldOut, seed, 2).People["leo"];
                var c = p.ControlActions.FirstOrDefault();
                var t = p.TreatmentActions.FirstOrDefault();
                if (c != t) differed.Add("seed " + seed + ": " + c + " became " + t);
            }

            Record("P6", differed.Count == 0, differed.Count == 0
                ? "His first decision was the same as the control on all " + Seeds + " seeds."
                : "His first decision differed on " + differed.Count + " of " + Seeds + " seeds: " + string.Join("; ", differed) + ".");
            Assert.IsEmpty(differed);
        }

        [Test]
        public void P7_HeStaysHimself()
        {
            var variants = _content.Morning.Variants.Select(v => v.Id).ToList();
            var people = _content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();
            var batch = BatchRunner.Run(_content, new BatchRunner.Options { Variants = variants, Seeds = 10 });

            var worst = variants.Min(v =>
            {
                var gaps = new List<double>();
                for (var i = 0; i < people.Count; i++)
                for (var j = i + 1; j < people.Count; j++)
                    gaps.Add(BatchRunner.HowDifferent(
                        BatchRunner.ActionProfile(batch.Rows, v, people[i]),
                        BatchRunner.ActionProfile(batch.Rows, v, people[j])));
                return gaps.Average();
            });

            Record("P7", worst > 0.30, "Weakest mean different-person behaviour difference across the design conditions: " + worst.ToString("0.00") + ".");
            Assert.Greater(worst, 0.30);
        }
    }
}
