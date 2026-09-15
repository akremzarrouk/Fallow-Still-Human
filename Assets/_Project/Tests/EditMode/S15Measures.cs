using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using Fallow.Core.Tracing;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// Every S1.5 measurement of one way of raising wants, taken the same way for
    /// each. Built before the alternative existed, and used unchanged for both.
    /// </summary>
    internal sealed class S15Measured
    {
        public string Label;

        // decisions, from the S1.2 audit instrument
        public DeliberationAudit Audit;
        public MotivationSources Sources;

        /// <summary>Decisions whose top option changes when every unsupported want is taken out.</summary>
        public int DecidedByUnsupportedWants;

        /// <summary>Decisions whose top option changes when the trait and value part of every want is taken out.</summary>
        public int DecidedByTraitsAndValuesInWants;

        // behaviour, from the S1 batch
        public int BatchMornings;
        public int BatchDecisions;
        public double WaitShare;
        public double SittingShare;
        public double MeanGap;
        public double WorstConditionMean;
        public double ClosestPair;
        public string ClosestWho;
        public int WorstPacing;
        public string WorstPacingWho;
        public double RealTies;
        public Dictionary<string, IReadOnlyDictionary<string, double>> ProfileByPerson = new Dictionary<string, IReadOnlyDictionary<string, double>>(StringComparer.Ordinal);

        public double LookAfterDecisive
        {
            get
            {
                Audit.Present.TryGetValue("look_after", out var n);
                Audit.Pivotal.TryGetValue("look_after", out var p);
                return n == 0 ? 0.0 : p / (double)n;
            }
        }

        public double Decisive(string want)
        {
            Audit.Present.TryGetValue(want, out var n);
            Audit.Pivotal.TryGetValue(want, out var p);
            return n == 0 ? 0.0 : p / (double)n;
        }

        public double WaitOnTopShare => Audit.WaitOnTop / (double)Math.Max(1, Audit.Decisions);
        public double AbandonedWalks => Audit.Abandoned / (double)Math.Max(1, Audit.WalksWithAPurpose);
        public double MeanPacing => Audit.PacingTotal / Math.Max(1, Audit.PacingSeries);
        public double GenuineTies => Audit.GenuineTies / (double)Math.Max(1, Audit.Decisions);
    }

    internal static class S15
    {
        internal static readonly string[] People = { "daniel", "elena", "leo", "mara" };

        internal static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);
        internal static string P(double v) => (v * 100).ToString("0.0", CultureInfo.InvariantCulture) + " %";

        /// <summary>A want with the trait and value part of it taken out, raised as the motivator would have raised the rest.</summary>
        internal static Motive WithoutDispositions(Motive m, double knee)
        {
            var rest = m.Terms.Where(t => MotivationSources.SourceOf(t) != Source.Disposition).Sum(t => t.Amount);
            var urgency = rest <= 0.0 ? 0.0 : Accumulate.Knee(rest, knee);
            return new Motive(m.Name, m.TargetId, urgency, m.RuleIds, m.Terms) { TraceId = m.TraceId };
        }

        internal static S15Measured Measure(Scenario001Content content, string label, IReadOnlyList<string> variants,
            int auditSeeds, int batchSeeds, ulong firstSeed = 1)
        {
            var measured = new S15Measured { Label = label, Sources = new MotivationSources() };
            Scenario001Run current = null;
            var memo = new Dictionary<int, bool>();
            var deliberator = new Deliberator(content.Rules);

            measured.Audit = DeliberationAudit.Run(content, variants, auditSeeds, firstSeed, alsoWatch: (m, run) =>
            {
                if (!ReferenceEquals(run, current)) { current = run; memo = new Dictionary<int, bool>(); }
                measured.Sources.Look(m, run.Trace, memo);

                var top = m.Decision.Considered[0].Option.Key;
                var unsupported = m.Motives.Where(x => MotivationSources.Of(x).Class == Support.Unsupported).ToList();
                if (unsupported.Count > 0)
                {
                    var without = m.Motives.Where(x => !unsupported.Contains(x)).ToList();
                    var again = deliberator.Decide(m.Mind, m.Percept, without, content.Morning.Day, new Rng(1), new TraceLog(), 0, m.Decision.Holding);
                    if (again.Considered[0].Option.Key != top) measured.DecidedByUnsupportedWants++;
                }

                if (m.Motives.Any(x => x.Terms.Any(t => t.Amount > 0.0 && MotivationSources.SourceOf(t) == Source.Disposition)))
                {
                    var stripped = m.Motives.Select(x => WithoutDispositions(x, content.Rules.Deciding.UrgencyKnee)).Where(x => x.Urgency > 0.0).ToList();
                    var again = deliberator.Decide(m.Mind, m.Percept, stripped, content.Morning.Day, new Rng(1), new TraceLog(), 0, m.Decision.Holding);
                    if (again.Considered[0].Option.Key != top) measured.DecidedByTraitsAndValuesInWants++;
                }
            });

            var batch = BatchRunner.Run(content, new BatchRunner.Options { Variants = variants, Seeds = batchSeeds, FirstSeed = firstSeed });
            measured.BatchMornings = batch.Summary.Runs;
            measured.BatchDecisions = batch.Rows.Count;
            measured.WaitShare = batch.Rows.Count(r => r.Action == "wait") / (double)Math.Max(1, batch.Rows.Count);
            measured.SittingShare = batch.Rows.Count(r => r.Action == "comfort") / (double)Math.Max(1, batch.Rows.Count);
            measured.RealTies = batch.Summary.AmbiguousShare * (1.0 - batch.Summary.InterchangeableShare);
            measured.WorstConditionMean = 1.0;
            measured.ClosestPair = 1.0;

            var people = content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();
            var gaps = new List<double>();
            foreach (var v in variants)
            {
                var here = new List<double>();
                for (var i = 0; i < people.Count; i++)
                for (var j = i + 1; j < people.Count; j++)
                {
                    var gap = BatchRunner.HowDifferent(BatchRunner.ActionProfile(batch.Rows, v, people[i]), BatchRunner.ActionProfile(batch.Rows, v, people[j]));
                    here.Add(gap);
                    if (gap < measured.ClosestPair) { measured.ClosestPair = gap; measured.ClosestWho = v + ": " + people[i] + "/" + people[j]; }
                }
                gaps.AddRange(here);
                measured.WorstConditionMean = Math.Min(measured.WorstConditionMean, here.Average());
            }
            measured.MeanGap = gaps.Average();
            foreach (var p in people) measured.ProfileByPerson[p] = BatchRunner.ActionProfile(batch.Rows, null, p);

            foreach (var group in batch.Rows.Where(r => r.Action == "go_to").GroupBy(r => r.Variant + "/" + r.Seed + "/" + r.Character))
            {
                var moves = group.OrderBy(r => r.Minute).Select(r => r.Target).ToList();
                var back = 0;
                for (var i = 2; i < moves.Count; i++)
                    if (moves[i] == moves[i - 2] && moves[i] != moves[i - 1]) back++;
                if (back > measured.WorstPacing) { measured.WorstPacing = back; measured.WorstPacingWho = group.Key; }
            }

            return measured;
        }

        internal static string Profiles(S15Measured m)
        {
            var kinds = m.ProfileByPerson.Values.SelectMany(p => p.Keys).Distinct().OrderBy(k => k, StringComparer.Ordinal).ToList();
            var sb = new StringBuilder();
            sb.AppendLine("| Who | " + string.Join(" | ", kinds) + " |");
            sb.AppendLine("|---|" + string.Join("|", kinds.Select(_ => "---")) + "|");
            foreach (var p in m.ProfileByPerson)
                sb.AppendLine("| " + p.Key + " | " + string.Join(" | ", kinds.Select(k => p.Value.TryGetValue(k, out var v) && v > 0 ? (v * 100).ToString("0", CultureInfo.InvariantCulture) + " %" : "-")) + " |");
            return sb.ToString();
        }
    }
}
