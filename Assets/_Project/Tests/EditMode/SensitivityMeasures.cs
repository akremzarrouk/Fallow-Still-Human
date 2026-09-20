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
    /// The decision-sensitivity instrument: how far one want has to move before
    /// the act chosen changes.
    ///
    /// It takes a decision exactly as the morning took it (the same mind in the
    /// state it decided in, the same percept, the same wants, the same intention
    /// carried in and the same random stream) and weighs it again with the
    /// deliberator, unchanged, with the urgency of one want set to another
    /// value. Nothing else is touched: no memory, belief, feeling, trait, value,
    /// room, person, rule or number. A want set to zero is left out, as the
    /// motivator leaves out a want with nothing behind it; a want that was not
    /// raised can be given an urgency, which is the same as saying it was raised
    /// that strongly. The list is kept in the order the motivator would give it.
    ///
    /// Urgency is on a scale the motivator can never take to 1: the knee and the
    /// accumulation both approach it without arriving. So the sweep covers
    /// [0, 0.995], which is everything a want can be, and then probes 1.5, 3 and
    /// 10, which no want can be, only to tell "needs more than the scale allows"
    /// from "never".
    ///
    /// Nothing here is used by the simulation; it only calls it.
    /// </summary>
    internal static class Sensitivity
    {
        /// <summary>The most urgent a want can be: the motivator's curves approach 1 and never reach it.</summary>
        internal const double Reach = 0.995;

        internal static readonly double[] Beyond = { 1.5, 3.0, 10.0 };

        internal static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);
        internal static string F2(double v) => v.ToString("0.00", CultureInfo.InvariantCulture);
        internal static string P(double part, double whole) => whole == 0 ? "n/a" : (100.0 * part / whole).ToString("0.0", CultureInfo.InvariantCulture) + " %";

        internal static string KindOf(string optionKey)
        {
            if (optionKey == null) return null;
            var cut = optionKey.IndexOfAny(new[] { ':', '-' });
            return cut < 0 ? optionKey : optionKey.Substring(0, cut);
        }

        internal static string KeyOf(string name, string target) => target == null ? name : name + ":" + target;

        /// <summary>The same wants with one of them at another urgency, ordered as the motivator orders them.</summary>
        internal static IReadOnlyList<Motive> With(IReadOnlyList<Motive> motives, string name, string target, double urgency)
        {
            var key = KeyOf(name, target);
            var original = motives.FirstOrDefault(m => string.Equals(m.Key, key, StringComparison.Ordinal));
            var list = motives.Where(m => !string.Equals(m.Key, key, StringComparison.Ordinal)).ToList();
            if (urgency > 0.0)
                list.Add(new Motive(name, target, urgency, original?.RuleIds, original?.Terms) { TraceId = original?.TraceId ?? 0 });
            return list
                .OrderByDescending(m => m.Urgency)
                .ThenBy(m => m.Key, StringComparer.Ordinal)
                .ToList();
        }
    }

    /// <summary>A decision as it was taken, with everything needed to take it again.</summary>
    internal sealed class Moment
    {
        public string Condition;
        public string Variant;
        public ulong Seed;
        public int Minute;
        public string Who;
        public string Why;
        public Mind Mind;
        public Percept Percept;
        public IReadOnlyList<Motive> Motives;
        public Intention Holding;
        public Decision Original;
        public int Day;

        /// <summary>The random stream the decision drew on, fresh each time it is asked for.</summary>
        public Func<Rng> Stream;

        public string Circumstance
            => (Variant == null ? "" : Variant + " s" + Seed + " ") + "m" + Minute + ", " + Who + " in the " + Percept.Room?.Id +
               (Percept.Present.Count == 0 ? ", alone" : ", with " + string.Join(", ", Percept.Present)) +
               ", hunger " + Sensitivity.F2(Percept.Hunger) +
               (Holding == null ? "" : ", carrying " + Holding.MotiveKey);

        internal static Moment Of(DecisionMoment m, string condition, string variant, ulong seed, int day)
            => new Moment
            {
                Condition = condition, Variant = variant, Seed = seed, Minute = m.Minute, Who = m.CharacterId, Why = m.Why,
                Mind = m.Mind, Percept = m.Percept, Motives = m.Motives, Holding = m.Decision.Holding, Original = m.Decision, Day = day,
                Stream = () => new Rng(seed).Fork(m.CharacterId + "@" + m.Minute)
            };
    }

    /// <summary>The decision at one urgency of the want being moved.</summary>
    internal sealed class Point
    {
        public double U;
        public Decision Decision;

        /// <summary>The option preferred: first among those considered. No randomness is involved in it.</summary>
        public string Top;

        /// <summary>What was chosen with the random stream the morning used. Differs from Top only inside the band.</summary>
        public string Chosen;

        public bool Ambiguous;
        public int Band;
        public List<string> Tied = new List<string>();
        public string Commitment;

        /// <summary>The options the moved want added something to, here.</summary>
        public List<string> Credited = new List<string>();

        public bool WantCreditsTop;

        /// <summary>The best of those it credits, considered or not, and its score.</summary>
        public string BestCredited;
        public double BestCreditedScore = double.NaN;
        public double TopScore;
    }

    /// <summary>One want moved across its whole range at one decision.</summary>
    internal sealed class WantSweep
    {
        public string Name;
        public string Target;
        public string Key => Sensitivity.KeyOf(Name, Target);
        public double U0;
        public bool Raised;
        public bool Leads;
        public Point Base;

        /// <summary>Ascending: the grid within reach, u0, and the probes beyond reach.</summary>
        public List<Point> Points = new List<Point>();

        public IEnumerable<Point> WithinReach => Points.Where(p => p.U <= Sensitivity.Reach + 1e-12);
        public IEnumerable<Point> PastReach => Points.Where(p => p.U > Sensitivity.Reach + 1e-12);

        /// <summary>Everything it credits anywhere within reach, and past it.</summary>
        public HashSet<string> CreditedWithinReach = new HashSet<string>(StringComparer.Ordinal);
        public HashSet<string> CreditedPastReach = new HashSet<string>(StringComparer.Ordinal);

        /// <summary>The nearest urgency above and below u0 at which the preferred option changes, located to the tolerance.</summary>
        public double? UpTop, DownTop;
        public string UpTopTo, DownTopTo;
        public bool UpTopAmbiguous, DownTopAmbiguous;

        /// <summary>The same for the option actually chosen with the morning's random stream.</summary>
        public double? UpChosen, DownChosen;
        public string UpChosenTo, DownChosenTo;

        /// <summary>
        /// Where another act first becomes possible: the decision was clear and
        /// something else enters the ambiguity band, so from here on the seed can
        /// choose it. Not located when the decision as taken was already a tie.
        /// </summary>
        public double? UpEnter, DownEnter;

        /// <summary>Where another act is chosen with nothing left to the seed: preferred, and clear of the band.</summary>
        public double? UpClear, DownClear;
        public string UpClearTo, DownClearTo;

        public double? DeltaUpEnter => UpEnter.HasValue ? UpEnter.Value - U0 : (double?)null;
        public double? DeltaDownEnter => DownEnter.HasValue ? U0 - DownEnter.Value : (double?)null;
        public double? DeltaUpClear => UpClear.HasValue ? UpClear.Value - U0 : (double?)null;
        public double? DeltaDownClear => DownClear.HasValue ? U0 - DownClear.Value : (double?)null;

        static double? Nearer(double? up, double? down)
        {
            if (up == null) return down;
            if (down == null) return up;
            return Math.Min(up.Value, down.Value);
        }

        /// <summary>Within reach: the smallest change in either direction that makes another act possible, and that makes one certain.</summary>
        public double? NearestEnter => Nearer(UpEnter.HasValue && UpEnter.Value <= Sensitivity.Reach ? DeltaUpEnter : null, DeltaDownEnter);
        public double? NearestClear => Nearer(UpClear.HasValue && UpClear.Value <= Sensitivity.Reach ? DeltaUpClear : null, DeltaDownClear);

        /// <summary>How many times the preferred option changes across the reachable range, low to high.</summary>
        public int Flips;

        /// <summary>The preferred options reachable by moving this want alone, within reach.</summary>
        public HashSet<string> TopsWithinReach = new HashSet<string>(StringComparer.Ordinal);

        public string Class;
        public string Reason;

        public double? DeltaUp => UpTop.HasValue ? UpTop.Value - U0 : (double?)null;
        public double? DeltaDown => DownTop.HasValue ? U0 - DownTop.Value : (double?)null;

        /// <summary>The smallest change in either direction that changes the preferred option, within reach.</summary>
        public double? Nearest
        {
            get
            {
                var up = UpTop.HasValue && UpTop.Value <= Sensitivity.Reach ? DeltaUp : null;
                var down = DeltaDown;
                if (up == null) return down;
                if (down == null) return up;
                return Math.Min(up.Value, down.Value);
            }
        }
    }

    /// <summary>Every want moved, one at a time, at one decision.</summary>
    internal sealed class MomentSweep
    {
        public Moment Moment;
        public bool Faithful;
        public string FaithfulnessNote;
        public int Available;
        public int WithAppeal;
        public int WorthDoing;
        public string Top;
        public string Chosen;
        public bool Ambiguous;
        public double Margin;
        public string Commitment;
        public string Leading;
        public List<WantSweep> Wants = new List<WantSweep>();

        /// <summary>Every preferred option some single want could bring about within reach, the present one included.</summary>
        public HashSet<string> Reachable = new HashSet<string>(StringComparer.Ordinal);
    }

    /// <summary>Weighs decisions again with one want moved.</summary>
    internal sealed class Sweeper
    {
        public static class Classes
        {
            /// <summary>The act changes somewhere in the reachable range.</summary>
            public const string Moves = "moves the act";

            /// <summary>Nothing the want could credit exists here, at any urgency.</summary>
            public const string NoCandidate = "no candidate";

            /// <summary>It credits something, but only past what a want can be (the foresight gate on a walk opens beyond reach).</summary>
            public const string CandidateOnlyPastReach = "candidate only past reach";

            /// <summary>It credits something that never becomes preferred within reach; past reach it does.</summary>
            public const string OutweighedWithinScale = "outweighed within the scale";

            /// <summary>It credits something that is never preferred at any urgency probed.</summary>
            public const string OutweighedAlways = "outweighed at any urgency";

            /// <summary>An intention carried in holds throughout, and nothing it credits is among what is being decided between.</summary>
            public const string Committed = "held off by an intention";

            /// <summary>
            /// It adds to what is already preferred, so raising it only confirms
            /// the act, and taking it away changes nothing either: something else
            /// would choose the same.
            /// </summary>
            public const string AlreadyItsAct = "already its act";
        }

        readonly Scenario001Content _content;
        readonly Deliberator _deliberator;
        readonly double[] _grid;
        readonly double _tolerance;

        public int Decides;

        /// <summary>
        /// Whether the change in what the morning's random stream chooses is
        /// located as finely as the change in preference, or only read off the
        /// grid. The census reads it off the grid, to keep its cost down.
        /// </summary>
        public bool LocateChosen = true;

        public Sweeper(Scenario001Content content, double step, double tolerance = 0.001)
        {
            _content = content;
            _deliberator = new Deliberator(content.Rules);
            var grid = new List<double>();
            for (var i = 0; i * step < Sensitivity.Reach - 1e-9; i++) grid.Add(Math.Round(i * step, 6));
            grid.Add(Sensitivity.Reach);
            _grid = grid.ToArray();
            _tolerance = tolerance;
        }

        public IReadOnlyList<double> Grid => _grid;

        public Decision Decide(Moment m, IReadOnlyList<Motive> motives)
        {
            Decides++;
            return _deliberator.Decide(m.Mind, m.Percept, motives, m.Day, m.Stream(), new TraceLog(), 0, m.Holding);
        }

        /// <summary>Every want the rules could raise here: each situation want once, each want about people once per person present.</summary>
        public IEnumerable<(string Name, string Target)> WantSpace(Moment m)
        {
            foreach (var name in _content.Rules.Motivation.Select(r => r.Motive).Distinct().OrderBy(n => n, StringComparer.Ordinal))
            {
                var perPerson = _content.Rules.Motivation.Any(r => r.Motive == name && r.Scope == Fallow.Core.Rules.MotiveScope.EachPresent);
                if (!perPerson) yield return (name, null);
                else foreach (var who in m.Percept.Present.OrderBy(x => x, StringComparer.Ordinal)) yield return (name, who);
            }
        }

        public Point At(Moment m, string name, string target, double u)
        {
            var d = Decide(m, Sensitivity.With(m.Motives, name, target, u));
            return Describe(d, Sensitivity.KeyOf(name, target), u);
        }

        static Point Describe(Decision d, string key, double u)
        {
            var top = d.Considered[0];
            var p = new Point
            {
                U = u, Decision = d, Top = top.Option.Key, Chosen = d.Chosen.Key,
                Ambiguous = d.Resolution == Resolution.Ambiguous, Band = Math.Max(1, d.Tied.Count),
                Tied = d.Tied.Select(o => o.Key).ToList(),
                Commitment = d.Commitment, TopScore = top.Score
            };
            foreach (var r in d.Ranked)
            {
                if (!r.Contributions.Any(c => c.Amount > 0.0 && string.Equals(c.MotiveKey, key, StringComparison.Ordinal))) continue;
                p.Credited.Add(r.Option.Key);
                if (double.IsNaN(p.BestCreditedScore) || r.Score > p.BestCreditedScore)
                {
                    p.BestCreditedScore = r.Score;
                    p.BestCredited = r.Option.Key;
                }
            }
            p.WantCreditsTop = p.Credited.Contains(p.Top);
            return p;
        }

        /// <summary>
        /// Checks that the decision taken again with nothing changed is the
        /// decision the morning took: same choice, same resolution, same scores.
        /// </summary>
        public bool Faithful(Moment m, out string note)
        {
            var again = Decide(m, m.Motives);
            var o = m.Original;
            note = null;
            if (!again.Chosen.SameAs(o.Chosen)) note = "chose " + again.Chosen + " not " + o.Chosen;
            else if (again.Resolution != o.Resolution) note = "resolution differs";
            else if (again.Commitment != o.Commitment) note = "commitment differs";
            else if (again.Ranked.Count != o.Ranked.Count) note = "option count differs";
            else
                for (var i = 0; i < o.Ranked.Count; i++)
                    if (!again.Ranked[i].Option.SameAs(o.Ranked[i].Option) || Math.Abs(again.Ranked[i].Score - o.Ranked[i].Score) > 1e-12)
                    {
                        note = "score of " + o.Ranked[i].Option + " differs";
                        break;
                    }
            return note == null;
        }

        public MomentSweep Sweep(Moment m)
        {
            var result = new MomentSweep { Moment = m };
            result.Faithful = Faithful(m, out result.FaithfulnessNote);

            var o = m.Original;
            result.Available = o.Ranked.Count;
            result.WithAppeal = o.Ranked.Count(r => r.Appeal > 0.0);
            result.WorthDoing = o.Ranked.Count(r => r.Score > 0.0);
            result.Top = o.Considered[0].Option.Key;
            result.Chosen = o.Chosen.Key;
            result.Ambiguous = o.Resolution == Resolution.Ambiguous;
            result.Margin = o.Margin;
            result.Commitment = o.Commitment;
            result.Leading = o.Leading?.Key;
            result.Reachable.Add(result.Top);

            foreach (var (name, target) in WantSpace(m))
            {
                var w = SweepOne(m, name, target);
                result.Wants.Add(w);
                foreach (var t in w.TopsWithinReach) result.Reachable.Add(t);
            }
            return result;
        }

        public WantSweep SweepOne(Moment m, string name, string target)
        {
            var key = Sensitivity.KeyOf(name, target);
            var raised = m.Motives.FirstOrDefault(x => string.Equals(x.Key, key, StringComparison.Ordinal));
            var w = new WantSweep
            {
                Name = name, Target = target, U0 = raised?.Urgency ?? 0.0, Raised = raised != null,
                Leads = m.Original.Leading != null && string.Equals(m.Original.Leading.Key, key, StringComparison.Ordinal)
            };
            w.Base = Describe(Decide(m, m.Motives), key, w.U0);

            // The grid, with u0 itself in its place, then the probes past reach.
            foreach (var u in _grid.Concat(Sensitivity.Beyond))
                if (Math.Abs(u - w.U0) > 1e-12) w.Points.Add(At(m, name, target, u));
            w.Points.Add(w.Base);
            w.Points.Sort((a, b) => a.U.CompareTo(b.U));

            foreach (var p in w.WithinReach)
            {
                foreach (var c in p.Credited) w.CreditedWithinReach.Add(c);
                w.TopsWithinReach.Add(p.Top);
            }
            foreach (var p in w.PastReach)
            foreach (var c in p.Credited) w.CreditedPastReach.Add(c);

            string last = null;
            foreach (var p in w.WithinReach)
            {
                if (last != null && !string.Equals(last, p.Top, StringComparison.Ordinal)) w.Flips++;
                last = p.Top;
            }

            // Nearest change above and below u0: of the preferred option; of what
            // the morning's stream chooses; where another act first becomes
            // possible; and where another act is chosen clear of the band.
            var baseTop = w.Base.Top;
            var baseChosen = w.Base.Chosen;
            foreach (var up in new[] { true, false })
            {
                var top = Locate(m, w, name, target, up, p => !string.Equals(p.Top, baseTop, StringComparison.Ordinal), true);
                if (top.HasValue)
                {
                    if (up) { w.UpTop = top.Value.U; w.UpTopTo = top.Value.P.Top; w.UpTopAmbiguous = top.Value.P.Ambiguous; }
                    else { w.DownTop = top.Value.U; w.DownTopTo = top.Value.P.Top; w.DownTopAmbiguous = top.Value.P.Ambiguous; }
                }

                var chosen = Locate(m, w, name, target, up, p => !string.Equals(p.Chosen, baseChosen, StringComparison.Ordinal), LocateChosen);
                if (chosen.HasValue)
                {
                    if (up) { w.UpChosen = chosen.Value.U; w.UpChosenTo = chosen.Value.P.Chosen; }
                    else { w.DownChosen = chosen.Value.U; w.DownChosenTo = chosen.Value.P.Chosen; }
                }

                var clear = Locate(m, w, name, target, up, p => !p.Ambiguous && !string.Equals(p.Top, baseTop, StringComparison.Ordinal), true);
                if (clear.HasValue)
                {
                    if (up) { w.UpClear = clear.Value.U; w.UpClearTo = clear.Value.P.Top; }
                    else { w.DownClear = clear.Value.U; w.DownClearTo = clear.Value.P.Top; }
                }

                if (!w.Base.Ambiguous)
                {
                    var enter = Locate(m, w, name, target, up, p => p.Ambiguous || !string.Equals(p.Top, baseTop, StringComparison.Ordinal), true);
                    if (enter.HasValue)
                    {
                        if (up) w.UpEnter = enter.Value.U;
                        else w.DownEnter = enter.Value.U;
                    }
                }
            }

            Classify(w);
            return w;
        }

        /// <summary>
        /// The nearest urgency from u0, in one direction, at which a condition
        /// first holds: found on the grid, then narrowed to the tolerance by
        /// halving (when asked to), on the assumption that it does not come and
        /// go inside one step of the grid.
        /// </summary>
        (double U, Point P)? Locate(Moment m, WantSweep w, string name, string target, bool up, Func<Point, bool> holds, bool narrow)
        {
            var ordered = up
                ? w.Points.Where(p => p.U > w.U0).OrderBy(p => p.U).ToList()
                : w.Points.Where(p => p.U < w.U0).OrderByDescending(p => p.U).ToList();

            var near = w.U0;
            foreach (var p in ordered)
            {
                if (!holds(p))
                {
                    near = p.U;
                    continue;
                }

                double lo = near, hi = p.U;
                var at = p;
                while (narrow && Math.Abs(hi - lo) > _tolerance)
                {
                    var mid = (lo + hi) / 2.0;
                    var q = At(m, name, target, mid);
                    if (!holds(q)) lo = mid;
                    else
                    {
                        hi = mid;
                        at = q;
                    }
                }
                return (hi, at);
            }
            return null;
        }

        static void Classify(WantSweep w)
        {
            var movesWithinReach = w.TopsWithinReach.Count > 1;
            if (movesWithinReach)
            {
                w.Class = Classes.Moves;
                return;
            }

            if (w.CreditedWithinReach.Count == 0)
            {
                w.Class = w.CreditedPastReach.Count == 0 ? Classes.NoCandidate : Classes.CandidateOnlyPastReach;
                return;
            }

            var within = w.WithinReach.ToList();
            if (within.All(p => p.Commitment == Fallow.Core.Sim.Commitment.Held) &&
                within.All(p => !p.Decision.Considered.Any(c => p.Credited.Contains(c.Option.Key))))
            {
                w.Class = Classes.Committed;
                return;
            }

            if (within.Any(p => p.WantCreditsTop))
            {
                w.Class = Classes.AlreadyItsAct;
                return;
            }

            w.Class = w.PastReach.Any(p => !string.Equals(p.Top, w.Base.Top, StringComparison.Ordinal))
                ? Classes.OutweighedWithinScale
                : Classes.OutweighedAlways;

            // Why the best thing it credits stays behind, at the top of the scale.
            var high = within.Last();
            var best = high.Decision.Ranked.FirstOrDefault(r => r.Option.Key == high.BestCredited);
            if (best != null)
            {
                var fromIt = best.Contributions.Where(c => c.MotiveKey == w.Key).Sum(c => c.Amount);
                var fromOthers = best.Appeal - fromIt;
                w.Reason = fromIt < best.Cost - fromOthers
                    ? "price: at the top of the scale it adds " + Sensitivity.F(fromIt) + " to " + best.Option.Key + ", which costs " + Sensitivity.F(best.Cost) + (fromOthers > 0 ? " (other wants add " + Sensitivity.F(fromOthers) + ")" : "")
                    : "competition: " + best.Option.Key + " reaches " + Sensitivity.F(best.Score) + " against " + high.Top + " at " + Sensitivity.F(high.TopScore);
            }
        }
    }
}
