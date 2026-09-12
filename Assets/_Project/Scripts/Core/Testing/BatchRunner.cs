using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Sim;

namespace Fallow.Core.Testing
{
    /// <summary>One line of the batch: one thing one person did, and why.</summary>
    public sealed class BatchRow
    {
        public string Variant;
        public ulong Seed;
        public int Minute;
        public string Character;
        public string Room;
        public string Action;
        public string Target;
        public string Motive;
        public double Urgency;
        public string Resolution;
        public double Margin;
        public string Outcome;
    }

    /// <summary>What the whole batch came to, in the few numbers worth looking at.</summary>
    public sealed class BatchSummary
    {
        public int Runs;
        public int Decisions;

        /// <summary>How often the choice was too close to call and the seed settled it.</summary>
        public double AmbiguousShare;

        /// <summary>
        /// Of those, how often the options that tied were the same act aimed
        /// somewhere else, such as which way to walk out of a room. A tie like
        /// that is a real absence of preference rather than a flat weighing, and
        /// reading the two together would hide which problem we have.
        /// </summary>
        public double InterchangeableShare;

        /// <summary>Action counts, keyed variant then character then action.</summary>
        public Dictionary<string, int> ActionCounts = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Which motive led, keyed variant then character then motive.</summary>
        public Dictionary<string, int> MotiveCounts = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Portions left at the end, keyed variant then count.</summary>
        public Dictionary<string, int> PortionsLeft = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>How many runs ended with the given person having eaten, keyed variant then character.</summary>
        public Dictionary<string, int> Ate = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>How many runs had somebody go through a room that was not theirs, with the owner there.</summary>
        public Dictionary<string, int> SearchedOnThem = new Dictionary<string, int>(StringComparer.Ordinal);
    }

    /// <summary>
    /// Runs the same morning many times over and writes down what happened.
    ///
    /// This is an instrument, not a feature. It exists to tell two things apart
    /// that look identical from a single run: behaviour that is interesting
    /// because the people are different, and behaviour that is varied because
    /// something is broken. A distribution answers that; one run never can.
    ///
    /// Deliberately thin. Rows out, a handful of counts, and the full trace for
    /// whichever runs are asked for. Anything more would be a product.
    /// </summary>
    public static class BatchRunner
    {
        public sealed class Options
        {
            public IReadOnlyList<string> Variants;
            public int Seeds = 50;
            public ulong FirstSeed = 1;
            public int? Minutes;

            /// <summary>Runs whose whole trace is kept, so a surprise can be read back.</summary>
            public Func<Scenario001Run, bool> Keep;
        }

        public sealed class Batch
        {
            public List<BatchRow> Rows = new List<BatchRow>();
            public BatchSummary Summary = new BatchSummary();
            public List<Scenario001Run> Kept = new List<Scenario001Run>();
        }

        public static Batch Run(Scenario001Content content, Options options)
        {
            var batch = new Batch();
            var variants = options.Variants ?? content.Morning.Variants.Select(v => v.Id).ToList();

            var ambiguous = 0;
            var interchangeable = 0;
            var decisions = 0;

            foreach (var variant in variants)
            for (var i = 0; i < options.Seeds; i++)
            {
                var seed = options.FirstSeed + (ulong)i;
                var run = Scenario001.Run(content, variant, seed, options.Minutes);
                batch.Summary.Runs++;

                foreach (var d in run.Result.Decisions)
                {
                    if (d.Resolution != Resolution.Ambiguous) continue;
                    if (d.Tied.Select(t => t.KindName).Distinct(StringComparer.Ordinal).Count() == 1)
                        interchangeable++;
                }

                foreach (var a in run.Result.Actions)
                {
                    decisions++;
                    if (a.Resolution == Resolution.Ambiguous) ambiguous++;

                    batch.Rows.Add(new BatchRow
                    {
                        Variant = variant,
                        Seed = seed,
                        Minute = a.Minute,
                        Character = a.CharacterId,
                        Room = a.RoomId,
                        Action = a.Action.KindName,
                        Target = a.Action.TargetId ?? a.Action.DestinationRoomId,
                        Motive = a.LeadingMotive,
                        Urgency = a.LeadingUrgency,
                        Resolution = a.Resolution == Resolution.Clear ? "clear" : "too_close",
                        Margin = a.Margin,
                        Outcome = a.Outcome
                    });

                    Bump(batch.Summary.ActionCounts, variant + "/" + a.CharacterId + "/" + a.Action.KindName);
                    Bump(batch.Summary.MotiveCounts, variant + "/" + a.CharacterId + "/" + a.LeadingMotive);
                }

                Bump(batch.Summary.PortionsLeft, variant + "/" + run.World.Portions);

                foreach (var id in run.World.Inhabitants)
                    if (run.Result.By(id).Any(a => a.Action.Kind == ActionKind.Eat && a.Outcome != null && a.Outcome.StartsWith("ate")))
                        Bump(batch.Summary.Ate, variant + "/" + id);

                if (run.Result.Events.Any(e =>
                        string.Equals(e.Action, "search_belongings", StringComparison.Ordinal) && e.TargetId != null))
                    Bump(batch.Summary.SearchedOnThem, variant);

                if (options.Keep != null && options.Keep(run)) batch.Kept.Add(run);
            }

            batch.Summary.Decisions = decisions;
            batch.Summary.AmbiguousShare = decisions == 0 ? 0.0 : (double)ambiguous / decisions;
            batch.Summary.InterchangeableShare = ambiguous == 0 ? 0.0 : (double)interchangeable / ambiguous;
            return batch;
        }

        static void Bump(Dictionary<string, int> counts, string key)
        {
            counts.TryGetValue(key, out var n);
            counts[key] = n + 1;
        }

        public static string ToCsv(IEnumerable<BatchRow> rows)
        {
            var sb = new StringBuilder();
            sb.AppendLine("variant,seed,minute,character,room,action,target,motive,urgency,resolution,margin,outcome");

            foreach (var r in rows)
                sb.AppendLine(string.Join(",", new[]
                {
                    Field(r.Variant), r.Seed.ToString(CultureInfo.InvariantCulture),
                    r.Minute.ToString(CultureInfo.InvariantCulture),
                    Field(r.Character), Field(r.Room), Field(r.Action), Field(r.Target), Field(r.Motive),
                    r.Urgency.ToString("0.000", CultureInfo.InvariantCulture),
                    Field(r.Resolution),
                    r.Margin.ToString("0.000", CultureInfo.InvariantCulture),
                    Field(r.Outcome)
                }));

            return sb.ToString();
        }

        static string Field(string s)
        {
            if (s == null) return "";
            return s.IndexOfAny(new[] { ',', '"', '\n' }) < 0
                ? s
                : "\"" + s.Replace("\"", "\"\"") + "\"";
        }

        /// <summary>
        /// The distribution of what each person did, as a share of their own
        /// decisions. This is the number that says whether four people are four
        /// people or one person in four hats.
        /// </summary>
        public static IReadOnlyDictionary<string, double> ActionProfile(
            IEnumerable<BatchRow> rows, string variant, string characterId)
        {
            var mine = rows
                .Where(r => variant == null || string.Equals(r.Variant, variant, StringComparison.Ordinal))
                .Where(r => string.Equals(r.Character, characterId, StringComparison.Ordinal))
                .ToList();

            if (mine.Count == 0) return new Dictionary<string, double>(StringComparer.Ordinal);

            return mine
                .GroupBy(r => r.Action, StringComparer.Ordinal)
                .ToDictionary(g => g.Key, g => (double)g.Count() / mine.Count, StringComparer.Ordinal);
        }

        /// <summary>
        /// How far apart two people are in what they spend a morning doing: the
        /// total difference between their action profiles, from 0 when they are
        /// indistinguishable to 1 when they share nothing.
        /// </summary>
        public static double HowDifferent(
            IReadOnlyDictionary<string, double> a, IReadOnlyDictionary<string, double> b)
        {
            var keys = new HashSet<string>(a.Keys, StringComparer.Ordinal);
            keys.UnionWith(b.Keys);

            var total = 0.0;
            foreach (var k in keys)
            {
                a.TryGetValue(k, out var x);
                b.TryGetValue(k, out var y);
                total += Math.Abs(x - y);
            }

            return total / 2.0;
        }
    }
}
