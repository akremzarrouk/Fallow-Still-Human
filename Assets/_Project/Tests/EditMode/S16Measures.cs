using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// What a person could have foreseen doing for a want at a destination, from
    /// what they knew before they set out. An instrument, built for the S1.6
    /// diagnosis before anything about deciding was changed, so that the same
    /// question can be asked of every walk before and after.
    ///
    /// It imagines the destination from the walker's own knowledge only: the
    /// room and whose it is (the house is not privileged knowledge), which rooms
    /// they have been through, whether they have looked in the pantry, how hungry
    /// they are, and their own mind as it stands. Two things it cannot know it
    /// takes at their most favourable for the want: nobody is there unless the
    /// want is about somebody, in which case that person is; and food kept there
    /// is within reach. If even at its most favourable the end is not worth
    /// doing, the walk to it could not have been worth taking.
    /// </summary>
    internal sealed class Foreseen
    {
        public string Want;
        public string Destination;

        /// <summary>The best thing that could be done there for the want, other than walking on. Null when nothing there serves it.</summary>
        public ScoredOption Best;

        public bool Possible => Best != null;
        public bool WorthIt => Best != null && Best.Score > 0.0;
        public double Score => Best == null ? double.NaN : Best.Score;

        public override string ToString()
            => Best == null
                ? "nothing there serves " + Want
                : Best.Option.Key + " " + Best.Score.ToString("+0.000;-0.000", CultureInfo.InvariantCulture) +
                  " (for " + Best.Appeal.ToString("0.00", CultureInfo.InvariantCulture) + ", against " + Best.Cost.ToString("0.00", CultureInfo.InvariantCulture) + ")";
    }

    internal static class S16
    {
        internal static readonly string[] People = { "daniel", "elena", "leo", "mara" };

        internal static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);
        internal static string P(double part, double whole) => whole == 0 ? "n/a" : (100.0 * part / whole).ToString("0.0", CultureInfo.InvariantCulture) + " %";

        /// <summary>The destination as the walker can imagine it now, from what they know.</summary>
        internal static Percept Imagine(RoomGraph house, Percept now, string destination, Motive want)
        {
            var room = house.Get(destination);
            var present = want?.TargetId != null ? new List<string> { want.TargetId } : new List<string>();
            var holdsFood = room != null && room.HasTag(ActionCatalog.PantryTag);
            return new Percept(
                now.CharacterId, now.Minute, room, present, house.Adjacent(destination), now.Hunger,
                holdsFood, holdsFood ? (bool?)true : null,
                now.RoomsIHaveSearched.Contains(destination, StringComparer.Ordinal),
                house, now.LookedInThePantryMyself, new List<string>(), now.RoomsIHaveSearched);
        }

        /// <summary>
        /// The best thing the person could foresee doing for a want at a
        /// destination. Weighed exactly as the deliberator will weigh it on
        /// arrival, with every want the person has now, on the imagined room.
        /// Must be called while the mind is in the state it decided in.
        /// </summary>
        internal static Foreseen Foresee(Scenario001Content c, DecisionMoment m, Motive want, string destination)
        {
            var hyp = Imagine(c.Morning.House, m.Percept, destination, want);
            var d = new Deliberator(c.Rules).Decide(m.Mind, hyp, m.Motives, c.Morning.Day, new Rng(1), new TraceLog(), 0);
            var best = d.Ranked
                .Where(r => r.Option.Kind != ActionKind.GoTo)
                .Where(r => r.Contributions.Any(x => x.Amount > 0.0 && string.Equals(x.MotiveKey, want.Key, StringComparison.Ordinal)))
                .OrderByDescending(r => r.Score)
                .ThenBy(r => r.Option.Key, StringComparer.Ordinal)
                .FirstOrDefault();
            return new Foreseen { Want = want.Key, Destination = destination, Best = best };
        }

        /// <summary>What one want added to the option that was chosen.</summary>
        internal static double AddedTo(ScoredOption chosen, string wantKey)
            => chosen == null ? 0.0 : chosen.Contributions.Where(x => string.Equals(x.MotiveKey, wantKey, StringComparison.Ordinal)).Sum(x => x.Amount);

        /// <summary>One walk, from setting out to deciding on arrival.</summary>
        internal sealed class WalkRecord
        {
            public string Variant;
            public ulong Seed;
            public string Who;
            public int SetOutAt;
            public string From;
            public string To;
            public string Want;
            public double WantUrgencyAtDeparture;
            public double WalkWorth;
            public Foreseen Foreseen;

            // filled in on arrival
            public int ArrivedAt = -1;
            public string Commitment;
            public double WantUrgencyOnArrival;
            public int PresentOnArrival;
            public ScoredOption BestServingOnArrival;
            public int ExperiencesGained;
            public string ExperienceMeanings;
            public int BeliefsMoved;
            public int OutcomesRecorded;
            public bool Interrupted;

            public bool Arrived => ArrivedAt >= 0 && !Interrupted && Commitment != null && Commitment != Fallow.Core.Sim.Commitment.None;
            public bool Held => Arrived && Commitment == Fallow.Core.Sim.Commitment.Held;
            public bool Lapsed => Arrived && !Held;
        }

        /// <summary>
        /// Every walk in a set of mornings, with what the walker could have
        /// foreseen at departure and what became of the intention on arrival.
        /// </summary>
        internal static List<WalkRecord> Walks(Scenario001Content c, IEnumerable<string> variants, ulong firstSeed, int seeds, Action<DecisionMoment, Scenario001Run> alsoWatch = null)
        {
            var walks = new List<WalkRecord>();
            foreach (var v in variants)
            for (var seed = firstSeed; seed < firstSeed + (ulong)seeds; seed++)
            {
                var run = Scenario001.Prepare(c, v, seed);
                var open = new Dictionary<string, WalkRecord>(StringComparer.Ordinal);
                var experiencesAt = new Dictionary<string, int>(StringComparer.Ordinal);
                var beliefsAt = new Dictionary<string, Dictionary<string, double>>(StringComparer.Ordinal);
                var outcomesAt = new Dictionary<string, int>(StringComparer.Ordinal);

                run.Morning.Decided = m =>
                {
                    alsoWatch?.Invoke(m, run);
                    var d = m.Decision;

                    if (open.TryGetValue(m.CharacterId, out var w))
                    {
                        open.Remove(m.CharacterId);
                        w.ArrivedAt = m.Minute;
                        w.Interrupted = m.Why != "finished";
                        w.Commitment = d.Holding == null ? "none" : d.Commitment;
                        var again = m.Motives.FirstOrDefault(x => x.Key == w.Want);
                        w.WantUrgencyOnArrival = again?.Urgency ?? 0.0;
                        w.PresentOnArrival = m.Percept.Present.Count;
                        w.BestServingOnArrival = d.Ranked
                            .Where(r => r.Contributions.Any(x => x.Amount > 0.0 && x.MotiveKey == w.Want))
                            .OrderByDescending(r => r.Score).ThenBy(r => r.Option.Key, StringComparer.Ordinal)
                            .FirstOrDefault();

                        var gained = m.Mind.Experiences.Skip(experiencesAt[m.CharacterId]).ToList();
                        w.ExperiencesGained = gained.Count;
                        w.ExperienceMeanings = string.Join(", ", gained.Select(x => x.Meaning).OrderBy(x => x, StringComparer.Ordinal));
                        var before = beliefsAt[m.CharacterId];
                        w.BeliefsMoved = m.Mind.Beliefs.All.Count(b => !before.TryGetValue(b.Key, out var conf) || Math.Abs(conf - b.Confidence) > 1e-9);
                        // The outcome for a lapse on arrival is written after this decision
                        // returns, for wants that read a need (S1.3), so it is counted here.
                        w.OutcomesRecorded = d.Holding != null && Outcomes.OfLapse(d.Commitment).HasValue && NeedsRead(c, d.Holding.MotiveName) ? 1 : 0;
                    }

                    if (d.Chosen.Kind != ActionKind.GoTo || d.Forms == null) return;
                    var want = m.Motives.FirstOrDefault(x => x.Key == d.Forms.MotiveKey);
                    if (want == null) return;
                    var record = new WalkRecord
                    {
                        Variant = v, Seed = seed, Who = m.CharacterId, SetOutAt = m.Minute,
                        From = m.Percept.Room?.Id, To = d.Chosen.DestinationRoomId,
                        Want = want.Key, WantUrgencyAtDeparture = want.Urgency,
                        WalkWorth = AddedTo(d.ChosenScored, want.Key),
                        Foreseen = Foresee(c, m, want, d.Chosen.DestinationRoomId)
                    };
                    walks.Add(record);
                    open[m.CharacterId] = record;
                    experiencesAt[m.CharacterId] = m.Mind.Experiences.Count;
                    beliefsAt[m.CharacterId] = m.Mind.Beliefs.All.ToDictionary(b => b.Key, b => b.Confidence, StringComparer.Ordinal);
                    outcomesAt[m.CharacterId] = m.Mind.Outcomes.Count;
                };
                run.Morning.Run(c.Morning.Minutes);
            }
            return walks;
        }

        static bool NeedsRead(Scenario001Content c, string motiveName)
            => c.Rules.Motivation.Where(r => r.Motive == motiveName).SelectMany(r => r.ScaledBy).Any(s => s.Kind == "need");

        /// <summary>Mean urgency of one want per person in ten-minute buckets, over a set of mornings.</summary>
        internal static string Timeline(Scenario001Content c, IEnumerable<string> variants, ulong firstSeed, int seeds, string wantName, int bucket = 10)
        {
            var sum = new Dictionary<string, double[]>(StringComparer.Ordinal);
            var n = new Dictionary<string, int[]>(StringComparer.Ordinal);
            var buckets = (c.Morning.Minutes + bucket - 1) / bucket;
            foreach (var p in People) { sum[p] = new double[buckets]; n[p] = new int[buckets]; }

            foreach (var v in variants)
            for (var seed = firstSeed; seed < firstSeed + (ulong)seeds; seed++)
            {
                var run = Scenario001.Prepare(c, v, seed);
                run.Morning.Decided = m =>
                {
                    var b = Math.Min(buckets - 1, Math.Max(0, (m.Minute - 1) / bucket));
                    var w = m.Motives.FirstOrDefault(x => x.Name == wantName);
                    sum[m.CharacterId][b] += w?.Urgency ?? 0.0;
                    n[m.CharacterId][b]++;
                };
                run.Morning.Run(c.Morning.Minutes);
            }

            var sb = new System.Text.StringBuilder();
            sb.Append("| Who |");
            for (var b = 0; b < buckets; b++) sb.Append(" " + (b * bucket + 1) + "-" + Math.Min(c.Morning.Minutes, (b + 1) * bucket) + " |");
            sb.AppendLine();
            sb.Append("|---|");
            for (var b = 0; b < buckets; b++) sb.Append("---|");
            sb.AppendLine();
            foreach (var p in People)
            {
                sb.Append("| " + p + " |");
                for (var b = 0; b < buckets; b++) sb.Append(" " + (n[p][b] == 0 ? "-" : (sum[p][b] / n[p][b]).ToString("0.00", CultureInfo.InvariantCulture)) + " |");
                sb.AppendLine();
            }
            return sb.ToString();
        }
    }
}
