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

        // ---- conditions ----

        /// <summary>
        /// M1: the same content with every scripted event of the lived day
        /// carrying the clock's minute, 0, instead of no minute at all. The four
        /// such events (the three day-4 events of the backstory and the opening)
        /// all happen before the morning's first decision.
        /// </summary>
        internal static Scenario001Content Timed(Scenario001Content c)
        {
            var day = c.Morning.Day;
            WorldEvent At(WorldEvent e, int minute) => new WorldEvent(
                e.Id, e.Day, e.Order, e.Kind, e.ActorId, e.TargetId, e.Act, e.Action, e.Topic, e.Tone,
                e.Directness, e.Valence, e.Intent, e.Summary, e.Witnesses, e.Overhearers,
                e.LedgerEffects, e.BeliefEffects, minute);
            WorldEvent Stamp(WorldEvent e) => e != null && e.Day == day && e.Minute < 0 ? At(e, 0) : e;

            var backstory = new ScenarioScript(
                c.Backstory.Id, c.Backstory.Description, c.Backstory.CharacterIds,
                c.Backstory.Events.Select(Stamp).ToList());
            var m = c.Morning;
            var morning = new MorningScenario(
                m.Id, m.Description, m.Day, m.Minutes, m.House, m.Portions, m.StartRooms, m.StartHunger,
                Stamp(m.Opening), m.Variants, m.HeldOutVariants);
            return new Scenario001Content(c.Vocabulary, c.Cast, backstory, morning, c.Rules);
        }

        /// <summary>M2: the same content with walks credited to a want the given way (see MeansMode).</summary>
        internal static Scenario001Content Means(Scenario001Content c, string mode) => S15.Deciding(c, d => d.Means = mode);

        /// <summary>The six conditions of the S1.6 experiment, in the order they are reported.</summary>
        internal static readonly (string Label, Func<Scenario001Content, Scenario001Content> Make)[] Conditions =
        {
            ("A", c => S15.Mode(c, Fallow.Core.Rules.DispositionMode.Standing)),
            ("A timed", c => Timed(S15.Mode(c, Fallow.Core.Rules.DispositionMode.Standing))),
            ("B", c => S15.Mode(c, Fallow.Core.Rules.DispositionMode.Respond)),
            ("B timed", c => Timed(S15.Mode(c, Fallow.Core.Rules.DispositionMode.Respond))),
            ("B end", c => Means(S15.Mode(c, Fallow.Core.Rules.DispositionMode.Respond), Fallow.Core.Rules.MeansMode.End)),
            ("B timed end", c => Means(Timed(S15.Mode(c, Fallow.Core.Rules.DispositionMode.Respond)), Fallow.Core.Rules.MeansMode.End))
        };

        /// <summary>One person's morning, decision by decision, as walks.md printed it.</summary>
        internal static string Table(Scenario001Content c, string variant, ulong seed, string who)
        {
            var run = Scenario001.Prepare(c, variant, seed);
            var sb = new System.Text.StringBuilder();
            sb.AppendLine("| Minute | Room | Chose | For | Intention brought in | Wants at 0.10 or more |");
            sb.AppendLine("|---|---|---|---|---|---|");
            run.Morning.Decided = m =>
            {
                if (m.CharacterId != who) return;
                var d = m.Decision;
                var l = d.Leading;
                sb.AppendLine("| " + m.Minute + " | " + m.Percept.Room.Id + " | " + d.Chosen + " | " + (l == null ? "nothing" : l.Name) + " | " +
                              (d.Holding == null ? "" : d.Holding.MotiveName + ": " + d.Commitment) + " | " +
                              string.Join("; ", m.Motives.Where(x => x.Urgency >= 0.1).Select(x => x.Key + " " + x.Urgency.ToString("0.00", CultureInfo.InvariantCulture))) + " |");
            };
            run.Morning.Run(c.Morning.Minutes);
            return sb.ToString();
        }

        /// <summary>Decisions in a set of mornings where no want added to what was chosen, and what was chosen.</summary>
        internal static (int Decisions, int Unled, Dictionary<string, int> Chose, int Ambiguous) NothingPressing(Scenario001Content c, IEnumerable<string> variants, ulong firstSeed, int seeds)
        {
            var decisions = 0; var unled = 0; var ambiguous = 0;
            var chose = new Dictionary<string, int>(StringComparer.Ordinal);
            foreach (var v in variants)
            for (var seed = firstSeed; seed < firstSeed + (ulong)seeds; seed++)
            {
                var run = Scenario001.Prepare(c, v, seed);
                run.Morning.Decided = m =>
                {
                    decisions++;
                    if (m.Decision.Leading != null) return;
                    unled++;
                    if (m.Decision.Resolution == Resolution.Ambiguous) ambiguous++;
                    chose.TryGetValue(m.Decision.Chosen.KindName, out var n);
                    chose[m.Decision.Chosen.KindName] = n + 1;
                };
                run.Morning.Run(c.Morning.Minutes);
            }
            return (decisions, unled, chose, ambiguous);
        }

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
