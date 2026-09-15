using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Rules;
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
        public int Meals;
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

        /// <summary>The same content with one thing about deciding changed, and nothing else.</summary>
        internal static Scenario001Content Deciding(Scenario001Content c, Action<DecisionDynamics> change)
        {
            var r = c.Rules;
            var d = r.Deciding;
            var copy = new DecisionDynamics
            {
                AmbiguityBand = d.AmbiguityBand, InterruptIntensity = d.InterruptIntensity, VisibleDistress = d.VisibleDistress,
                HungerPerMinute = d.HungerPerMinute, PortionRelief = d.PortionRelief, LowPortions = d.LowPortions,
                DistressShows = d.DistressShows, ComfortSettles = d.ComfortSettles, ComfortSettling = d.ComfortSettling,
                UrgencyKnee = d.UrgencyKnee, RecallHalfLife = d.RecallHalfLife, WatchingGoesStaleAfter = d.WatchingGoesStaleAfter,
                ActionMinutes = d.ActionMinutes, Dispositions = d.Dispositions
            };
            change(copy);
            var rules = new RuleSet
            {
                Interpretation = r.Interpretation, BeliefNudges = r.BeliefNudges, Appraisal = r.Appraisal, Dynamics = r.Dynamics,
                Motivation = r.Motivation, Proposals = r.Proposals, Costs = r.Costs, Deciding = copy
            };
            return new Scenario001Content(c.Vocabulary, c.Cast, c.Backstory, c.Morning, rules);
        }

        internal static Scenario001Content Mode(Scenario001Content c, string mode) => Deciding(c, d => d.Dispositions = mode);

        /// <summary>A circumstance removed: nobody's distress is ever visible to anybody, however strong.</summary>
        internal static Scenario001Content DistressNeverShows(Scenario001Content c) => Deciding(c, d => d.VisibleDistress = 10.0);

        /// <summary>A circumstance removed: the opening count does not come up short, so nothing is missing this morning.</summary>
        internal static Scenario001Content NothingMissing(Scenario001Content c)
            => S13DiagnosisTests.Plenty(c, c.Morning.Portions, countComesUpShort: false);

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
            measured.Meals = batch.Rows.Count(r => r.Action == "eat" && r.Outcome != null && r.Outcome.StartsWith("ate", StringComparison.Ordinal));
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

        /// <summary>What a set of mornings came to, for the wants and acts a removed circumstance ought to take with it.</summary>
        internal sealed class WorldCounts
        {
            public int Mornings;
            public int Decisions;
            public int PeoplePresentAtDecisions;
            public int ShowDistress;

            public int LookAfterRaised;
            public int LookAfterUnsupported;
            public int LookAfterWithoutHistory;
            public int LookAfterOnHistoryOnly;
            public int Comfort;
            public int ComfortForLookAfter;

            public int FindOutRaised;
            public double FindOutUrgency;
            public int FindOutUnsupported;
            public int FindOutWithNothingNowBehindIt;
            public int FindOutWithNeitherCircumstanceNorAuthored;
            public int ForFindOut;
            public int Searches;

            public int Meals;
            public Dictionary<string, int> MealsBy = new Dictionary<string, int>(StringComparer.Ordinal);
            public Dictionary<string, int> Chosen = new Dictionary<string, int>(StringComparer.Ordinal);
        }

        internal static WorldCounts Count(Scenario001Content c, IEnumerable<string> variants, ulong firstSeed, int seeds)
        {
            var w = new WorldCounts();
            foreach (var v in variants)
            for (var seed = firstSeed; seed < firstSeed + (ulong)seeds; seed++)
            {
                var run = Scenario001.Prepare(c, v, seed);
                run.Morning.Decided = m =>
                {
                    w.Decisions++;
                    w.PeoplePresentAtDecisions += m.Percept.Present.Count;
                    var kind = m.Decision.Chosen.KindName;
                    w.Chosen.TryGetValue(kind, out var n);
                    w.Chosen[kind] = n + 1;

                    foreach (var x in m.Motives)
                    {
                        var s = MotivationSources.Of(x);
                        if (x.Name == "look_after")
                        {
                            w.LookAfterRaised++;
                            if (s.Class == Support.Unsupported) w.LookAfterUnsupported++;
                            if (s.History <= 0.0) w.LookAfterWithoutHistory++;
                            if (s.StandingWithReasons) w.LookAfterOnHistoryOnly++;
                        }
                        if (x.Name == "find_out")
                        {
                            w.FindOutRaised++;
                            w.FindOutUrgency += x.Urgency;
                            if (s.Class == Support.Unsupported) w.FindOutUnsupported++;
                            if (s.Circumstance <= 0.0) w.FindOutWithNothingNowBehindIt++;
                            if (s.Circumstance <= 0.0 && s.History <= 0.0 && s.Authored <= 0.0) w.FindOutWithNeitherCircumstanceNorAuthored++;
                        }
                    }

                    var leading = m.Decision.Leading;
                    if (m.Decision.Chosen.Kind == ActionKind.Comfort)
                    {
                        w.Comfort++;
                        if (leading != null && leading.Name == "look_after") w.ComfortForLookAfter++;
                    }
                    if (m.Decision.Chosen.Kind == ActionKind.SearchRoom) w.Searches++;
                    if (leading != null && leading.Name == "find_out") w.ForFindOut++;
                };
                run.Morning.Run(c.Morning.Minutes);
                w.Mornings++;
                w.ShowDistress += run.Result.Events.Count(e => e.Action == "show_distress");
                foreach (var a in run.Result.Actions.Where(a => a.Action.Kind == ActionKind.Eat && a.Outcome != null && a.Outcome.StartsWith("ate", StringComparison.Ordinal)))
                {
                    w.Meals++;
                    w.MealsBy.TryGetValue(a.CharacterId, out var n);
                    w.MealsBy[a.CharacterId] = n + 1;
                }
            }
            return w;
        }

        /// <summary>The S1.1 behaviour measure: the night against no night for one person, against the noise of two pools of the same.</summary>
        internal static (double Effect, double NoiseWithout, double NoiseWith) NightEffect(Scenario001Content c, string variant, string who, ulong from)
        {
            Dictionary<string, double> Pool(bool night, ulong start)
            {
                var counts = new Dictionary<string, double>(StringComparer.Ordinal);
                var total = 0;
                for (var seed = start; seed < start + 20; seed++)
                {
                    var run = Scenario001.PrepareWith(c, variant, night ? c.Morning.Variant(variant).NightEvents : new List<WorldEvent>(), seed);
                    run.Morning.Run(c.Morning.Minutes);
                    foreach (var a in run.Result.By(who))
                    {
                        counts.TryGetValue(a.Action.KindName, out var n);
                        counts[a.Action.KindName] = n + 1;
                        total++;
                    }
                }
                return counts.ToDictionary(k => k.Key, k => k.Value / Math.Max(1, total), StringComparer.Ordinal);
            }

            var t1 = Pool(true, from); var t2 = Pool(true, from + 20);
            var c1 = Pool(false, from); var c2 = Pool(false, from + 20);
            return ((BatchRunner.HowDifferent(t1, c2) + BatchRunner.HowDifferent(t2, c1)) / 2,
                BatchRunner.HowDifferent(c1, c2), BatchRunner.HowDifferent(t1, t2));
        }

        /// <summary>Each person as written, in a kitchen with the other three, nothing having happened, not hungry.</summary>
        internal static List<(string Who, IReadOnlyList<Motive> Wants, ScoredOption Choice)> NothingHappening(Scenario001Content c)
        {
            var rows = new List<(string, IReadOnlyList<Motive>, ScoredOption)>();
            foreach (var id in People)
            {
                var mind = new Mind(c.Cast[id]);
                var percept = Bench.Standing(id, present: People.Where(p => p != id).ToList(), hunger: 0.0);
                var wants = new Motivator(c.Rules).Raise(mind, percept, c.Morning.Day, new TraceLog(), 0);
                var decision = new Deliberator(c.Rules).Decide(mind, percept, wants, c.Morning.Day, new Rng(1), new TraceLog(), 0);
                rows.Add((id, wants, decision.ChosenScored));
            }
            return rows;
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
