using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;

namespace Fallow.Core.Testing
{
    /// <summary>Where one term of a want came from.</summary>
    public enum Source
    {
        /// <summary>Something about now: the body, a memory of today, a live feeling. Each rests on what happened.</summary>
        Circumstance,

        /// <summary>Something durable that was learned from what happened: a belief with evidence behind it, a ledger entry.</summary>
        History,

        /// <summary>A belief written into the person with no evidence behind it, or a constant written into the rule.</summary>
        Authored,

        /// <summary>Who the person is: a trait, a value, how perceptive they are.</summary>
        Disposition
    }

    /// <summary>What a raised want rests on, as a matter of arithmetic and of record.</summary>
    public enum Support
    {
        /// <summary>Most of it comes from what happened, now or before.</summary>
        FromCircumstance,

        /// <summary>Something that happened is behind it, but most of it is who the person is.</summary>
        MostlyDisposition,

        /// <summary>Nothing that happened is behind it at all.</summary>
        Unsupported
    }

    /// <summary>One raised want, taken apart by where each part of it came from.</summary>
    public sealed class WantSupport
    {
        public string MotiveKey;
        public string MotiveName;
        public string CharacterId;
        public double Urgency;

        public double Circumstance;
        public double History;
        public double Authored;
        public double Disposition;

        public double Grounded => Circumstance + History;
        public double Ungrounded => Authored + Disposition;
        public double Total => Grounded + Ungrounded;

        public Support Class =>
            Grounded <= 0.0 ? Support.Unsupported
            : Grounded >= Ungrounded ? Support.FromCircumstance
            : Support.MostlyDisposition;

        /// <summary>Grounded only in what was learned before, with nothing about now behind it: a standing want with reasons.</summary>
        public bool StandingWithReasons => Circumstance <= 0.0 && History > 0.0;

        public double Of(Source s)
        {
            switch (s)
            {
                case Source.Circumstance: return Circumstance;
                case Source.History: return History;
                case Source.Authored: return Authored;
                default: return Disposition;
            }
        }
    }

    /// <summary>
    /// Counts where wants come from. Built for S1.5, before anything about how
    /// wants are raised was changed, so that the change can be measured against
    /// the same instrument. It reads wants and decisions; it never alters a run.
    /// </summary>
    public sealed class MotivationSources
    {
        public static Source SourceOf(ScalerTerm t)
        {
            switch (t.Kind)
            {
                case ScalerKind.Need:
                case ScalerKind.Memory:
                case ScalerKind.Emotion:
                    return Source.Circumstance;
                case ScalerKind.Belief:
                case ScalerKind.Ledger:
                    return t.Drew.Count > 0 ? Source.History : Source.Authored;
                case ScalerKind.Trait:
                case ScalerKind.Value:
                case ScalerKind.Perceptiveness:
                    return Source.Disposition;
                default:
                    return Source.Authored;
            }
        }

        public static WantSupport Of(Motive m, string characterId = null)
        {
            var w = new WantSupport { MotiveKey = m.Key, MotiveName = m.Name, CharacterId = characterId, Urgency = m.Urgency };
            foreach (var t in m.Terms)
            {
                if (t.Amount <= 0.0) continue;
                switch (SourceOf(t))
                {
                    case Source.Circumstance: w.Circumstance += t.Amount; break;
                    case Source.History: w.History += t.Amount; break;
                    case Source.Authored: w.Authored += t.Amount; break;
                    default: w.Disposition += t.Amount; break;
                }
            }
            return w;
        }

        /// <summary>Whether a record, followed back through its parents, reaches something that happened in the world.</summary>
        public static bool ReachesAnEvent(TraceLog trace, int id, Dictionary<int, bool> memo)
        {
            if (memo.TryGetValue(id, out var known)) return known;
            memo[id] = false;
            var r = trace.Get(id);
            var found = r != null && (r.Kind == TraceKind.Event || r.ParentIds.Any(p => ReachesAnEvent(trace, p, memo)));
            memo[id] = found;
            return found;
        }

        // ---- counts ----

        public int Decisions;
        public int Raised;
        public readonly Dictionary<Support, int> ByClass = new Dictionary<Support, int>();
        public readonly Dictionary<Source, double> Amounts = new Dictionary<Source, double>();
        public int StandingWithReasons;

        public readonly Dictionary<string, Dictionary<Support, int>> ClassByMotive = new Dictionary<string, Dictionary<Support, int>>(StringComparer.Ordinal);
        public readonly Dictionary<string, Dictionary<Source, double>> AmountsByMotive = new Dictionary<string, Dictionary<Source, double>>(StringComparer.Ordinal);
        public readonly Dictionary<string, Dictionary<Support, int>> ClassByPerson = new Dictionary<string, Dictionary<Support, int>>(StringComparer.Ordinal);

        /// <summary>Decisions where nothing at all was wanted.</summary>
        public int NothingWanted;

        /// <summary>Decisions where every want raised was unsupported.</summary>
        public int OnlyUnsupportedWants;

        /// <summary>What was chosen, by the support of the want that added most to it; "nothing" when no want added anything.</summary>
        public readonly Dictionary<string, int> ChosenBy = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Standing still chosen, by the support of the want behind it.</summary>
        public readonly Dictionary<string, int> WaitChosenBy = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Urgency, pre-knee, split by whether the term that carried it rests on a record that leads back to something that happened.</summary>
        public double UrgencyTraced;
        public double UrgencyUntraced;

        /// <summary>Wants with at least one term that leads back to something that happened.</summary>
        public int WantsTraced;

        public void Look(DecisionMoment m, TraceLog trace, Dictionary<int, bool> memo)
        {
            Decisions++;
            var supports = m.Motives.Select(x => Of(x, m.CharacterId)).ToList();
            if (supports.Count == 0) NothingWanted++;
            else if (supports.All(s => s.Class == Support.Unsupported)) OnlyUnsupportedWants++;

            for (var i = 0; i < supports.Count; i++)
            {
                var s = supports[i];
                Raised++;
                Bump(ByClass, s.Class);
                if (s.StandingWithReasons) StandingWithReasons++;
                Bump(Nested(ClassByMotive, s.MotiveName), s.Class);
                Bump(Nested(ClassByPerson, m.CharacterId), s.Class);
                foreach (Source src in Enum.GetValues(typeof(Source)))
                {
                    Add(Amounts, src, s.Of(src));
                    Add(Nested(AmountsByMotive, s.MotiveName), src, s.Of(src));
                }

                var anyTraced = false;
                foreach (var t in m.Motives[i].Terms)
                {
                    if (t.Amount <= 0.0) continue;
                    var traced = t.Kind == ScalerKind.Need || t.Drew.Any(id => ReachesAnEvent(trace, id, memo));
                    if (traced) { UrgencyTraced += t.Amount; anyTraced = true; }
                    else UrgencyUntraced += t.Amount;
                }
                if (anyTraced) WantsTraced++;
            }

            var leading = m.Decision.Leading;
            var label = leading == null ? "nothing" : Of(leading).Class.ToString();
            Bump(ChosenBy, label);
            if (m.Decision.Chosen.Kind == ActionKind.Wait) Bump(WaitChosenBy, label);
        }

        static Dictionary<TK, TV> Nested<TK, TV>(Dictionary<string, Dictionary<TK, TV>> d, string key)
        {
            if (!d.TryGetValue(key, out var inner)) d[key] = inner = new Dictionary<TK, TV>();
            return inner;
        }

        static void Bump<T>(Dictionary<T, int> d, T key)
        {
            d.TryGetValue(key, out var n);
            d[key] = n + 1;
        }

        static void Add<T>(Dictionary<T, double> d, T key, double v)
        {
            d.TryGetValue(key, out var n);
            d[key] = n + v;
        }

        static int Get<T>(Dictionary<T, int> d, T key) => d.TryGetValue(key, out var n) ? n : 0;
        static double Get<T>(Dictionary<T, double> d, T key) => d.TryGetValue(key, out var n) ? n : 0.0;

        public static string P(double part, double whole)
            => whole == 0 ? "n/a" : (part / whole * 100).ToString("0.0", CultureInfo.InvariantCulture) + " %";

        public double Share(Support c) => Raised == 0 ? 0.0 : Get(ByClass, c) / (double)Raised;

        public double ShareOfUrgency(Source s)
        {
            var total = Amounts.Values.Sum();
            return total == 0 ? 0.0 : Get(Amounts, s) / total;
        }

        public string ToMarkdown()
        {
            var sb = new StringBuilder();
            var sources = (Source[])Enum.GetValues(typeof(Source));
            var classes = (Support[])Enum.GetValues(typeof(Support));

            sb.AppendLine(Decisions + " decisions, " + Raised + " wants raised.");
            sb.AppendLine();
            sb.AppendLine("| Wants raised | " + string.Join(" | ", classes.Select(c => c.ToString())) + " |");
            sb.AppendLine("|---|" + string.Join("|", classes.Select(_ => "---")) + "|");
            sb.AppendLine("| all | " + string.Join(" | ", classes.Select(c => P(Get(ByClass, c), Raised))) + " |");
            foreach (var k in ClassByMotive.OrderBy(k => k.Key, StringComparer.Ordinal))
            {
                var n = k.Value.Values.Sum();
                sb.AppendLine("| `" + k.Key + "` (" + n + ") | " + string.Join(" | ", classes.Select(c => P(Get(k.Value, c), n))) + " |");
            }
            foreach (var k in ClassByPerson.OrderBy(k => k.Key, StringComparer.Ordinal))
            {
                var n = k.Value.Values.Sum();
                sb.AppendLine("| " + k.Key + " (" + n + ") | " + string.Join(" | ", classes.Select(c => P(Get(k.Value, c), n))) + " |");
            }
            sb.AppendLine();
            sb.AppendLine("Grounded only in what was learned before (evidence, ledger), with nothing about now behind it: " + P(StandingWithReasons, Raised) + " of wants raised.");
            sb.AppendLine();

            sb.AppendLine("| Urgency came from | " + string.Join(" | ", sources.Select(s => s.ToString())) + " |");
            sb.AppendLine("|---|" + string.Join("|", sources.Select(_ => "---")) + "|");
            var all = Amounts.Values.Sum();
            sb.AppendLine("| all | " + string.Join(" | ", sources.Select(s => P(Get(Amounts, s), all))) + " |");
            foreach (var k in AmountsByMotive.OrderBy(k => k.Key, StringComparer.Ordinal))
            {
                var n = k.Value.Values.Sum();
                sb.AppendLine("| `" + k.Key + "` | " + string.Join(" | ", sources.Select(s => P(Get(k.Value, s), n))) + " |");
            }
            sb.AppendLine();

            sb.AppendLine("Decisions with nothing wanted at all: " + P(NothingWanted, Decisions) + "; with every want unsupported: " + P(OnlyUnsupportedWants, Decisions) + ".");
            sb.AppendLine();
            sb.AppendLine("What was chosen, by the support of the want that added most to it: " +
                          string.Join(", ", ChosenBy.OrderBy(k => k.Key, StringComparer.Ordinal).Select(k => k.Key + " " + P(k.Value, Decisions))) + ".");
            var waits = WaitChosenBy.Values.Sum();
            sb.AppendLine("Standing still chosen (" + P(waits, Decisions) + " of decisions), by the same: " +
                          string.Join(", ", WaitChosenBy.OrderBy(k => k.Key, StringComparer.Ordinal).Select(k => k.Key + " " + P(k.Value, waits))) + ".");
            sb.AppendLine();
            sb.AppendLine("Urgency carried by terms resting on a record that leads back to something that happened (or the body): " +
                          P(UrgencyTraced, UrgencyTraced + UrgencyUntraced) + ". Wants with at least one such term: " + P(WantsTraced, Raised) + ".");
            return sb.ToString();
        }
    }
}
