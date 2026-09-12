using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;

namespace Fallow.Core.Testing
{
    /// <summary>
    /// What one person wanted at one moment, and whether each want can be walked
    /// back to a given cause.
    /// </summary>
    public sealed class Landscape
    {
        /// <summary>Urgency by want. A want about people takes its strongest target.</summary>
        public Dictionary<string, double> Urgency = new Dictionary<string, double>(StringComparer.Ordinal);

        /// <summary>For each want, whether any term that moved it rests on the cause.</summary>
        public Dictionary<string, bool> RestsOnCause = new Dictionary<string, bool>(StringComparer.Ordinal);

        public double Of(string motive) => Urgency.TryGetValue(motive, out var u) ? u : 0.0;
    }

    /// <summary>One person, compared across two mornings that differ in one thing.</summary>
    public sealed class PersonComparison
    {
        public string CharacterId;

        /// <summary>Live feelings after the night and after the opening, in each world.</summary>
        public Dictionary<string, string> ControlFeelings = new Dictionary<string, string>(StringComparer.Ordinal);
        public Dictionary<string, string> TreatmentFeelings = new Dictionary<string, string>(StringComparer.Ordinal);

        /// <summary>Wants at minute zero, before anybody has done anything differently.</summary>
        public Landscape ControlAtStart;
        public Landscape TreatmentAtStart;

        /// <summary>Wants every minute of the morning.</summary>
        public List<Landscape> ControlTimeline = new List<Landscape>();
        public List<Landscape> TreatmentTimeline = new List<Landscape>();

        /// <summary>Strength of each feeling, whoever it is about, every minute.</summary>
        public List<Dictionary<string, double>> ControlFeelTimeline = new List<Dictionary<string, double>>();
        public List<Dictionary<string, double>> TreatmentFeelTimeline = new List<Dictionary<string, double>>();

        /// <summary>What the person did.</summary>
        public List<string> ControlActions = new List<string>();
        public List<string> TreatmentActions = new List<string>();

        public IReadOnlyDictionary<string, double> ControlProfile;
        public IReadOnlyDictionary<string, double> TreatmentProfile;

        /// <summary>
        /// How far the person's wants moved at the start of the morning: the
        /// mean absolute change in urgency across every want the rules know.
        /// Measured before anybody has acted, so nothing in it can be the echo of
        /// a different decision; it is the cause and nothing else.
        /// </summary>
        public double SensitivityAtStart(IReadOnlyList<string> motives)
            => motives.Average(m => Math.Abs(TreatmentAtStart.Of(m) - ControlAtStart.Of(m)));

        /// <summary>The same, averaged over the whole morning, which includes knock-on effects.</summary>
        public double SensitivityOverMorning(IReadOnlyList<string> motives)
        {
            var n = Math.Min(ControlTimeline.Count, TreatmentTimeline.Count);
            if (n == 0) return 0.0;

            var total = 0.0;
            for (var i = 0; i < n; i++)
                total += motives.Average(m => Math.Abs(TreatmentTimeline[i].Of(m) - ControlTimeline[i].Of(m)));
            return total / n;
        }

        /// <summary>The change in one want at the start, signed.</summary>
        public double ShiftAtStart(string motive) => TreatmentAtStart.Of(motive) - ControlAtStart.Of(motive);

        /// <summary>The mean change in one want across the morning, signed.</summary>
        public double ShiftOverMorning(string motive)
        {
            var n = Math.Min(ControlTimeline.Count, TreatmentTimeline.Count);
            if (n == 0) return 0.0;
            var total = 0.0;
            for (var i = 0; i < n; i++) total += TreatmentTimeline[i].Of(motive) - ControlTimeline[i].Of(motive);
            return total / n;
        }

        /// <summary>
        /// Of the wants that changed by more than the threshold at the start,
        /// the share whose treatment-side reasons can be walked back to the cause.
        /// Null when nothing changed, because a share of nothing is not zero.
        /// </summary>
        public double? AttributionAtStart(IReadOnlyList<string> motives, double threshold)
        {
            var changed = motives.Where(m => Math.Abs(ShiftAtStart(m)) > threshold).ToList();
            if (changed.Count == 0) return null;

            var traced = changed.Count(m =>
                TreatmentAtStart.RestsOnCause.TryGetValue(m, out var yes) && yes);
            return (double)traced / changed.Count;
        }

        public double BehaviourDifference => BatchRunner.HowDifferent(ControlProfile, TreatmentProfile);
    }

    /// <summary>
    /// Two mornings identical in everything except one cause, run side by side
    /// on the same seed.
    ///
    /// This is the instrument S1.1 exists to build. Comparing different seeds
    /// cannot say whether a difference came from the cause or from the dice;
    /// comparing different conditions cannot say which part of the condition did
    /// it. Holding the seed, the world, the people and every other event fixed,
    /// and changing one thing, can.
    ///
    /// Probing is read-only. The wants are raised into a scratch trace, so the
    /// runs themselves are exactly the runs that would have happened unobserved.
    /// </summary>
    public static class Counterfactual
    {
        public sealed class Pair
        {
            public string Label;
            public ulong Seed;
            public IReadOnlyList<string> CauseEventIds;
            public Scenario001Run Control;
            public Scenario001Run Treatment;
            public Dictionary<string, PersonComparison> People =
                new Dictionary<string, PersonComparison>(StringComparer.Ordinal);
        }

        public static Pair Run(
            Scenario001Content content, string label,
            IReadOnlyList<WorldEvent> controlNight, IReadOnlyList<WorldEvent> treatmentNight,
            IReadOnlyList<string> causeEventIds, ulong seed, int? minutes = null)
        {
            var pair = new Pair { Label = label, Seed = seed, CauseEventIds = causeEventIds };

            foreach (var id in content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal))
                pair.People[id] = new PersonComparison { CharacterId = id };

            pair.Control = Scenario001.PrepareWith(content, label + "/control", controlNight, seed,
                (stage, sim) => Snapshot(stage, sim, pair, control: true));
            pair.Treatment = Scenario001.PrepareWith(content, label + "/treatment", treatmentNight, seed,
                (stage, sim) => Snapshot(stage, sim, pair, control: false));

            foreach (var p in pair.People.Values)
            {
                p.ControlAtStart = Probe(content, pair.Control, p.CharacterId, causeEventIds);
                p.TreatmentAtStart = Probe(content, pair.Treatment, p.CharacterId, causeEventIds);
            }

            var length = minutes ?? content.Morning.Minutes;
            for (var minute = 0; minute < length; minute++)
            {
                pair.Control.Morning.Step();
                pair.Treatment.Morning.Step();

                foreach (var p in pair.People.Values)
                {
                    p.ControlTimeline.Add(Probe(content, pair.Control, p.CharacterId, causeEventIds));
                    p.TreatmentTimeline.Add(Probe(content, pair.Treatment, p.CharacterId, causeEventIds));
                    p.ControlFeelTimeline.Add(Feelings(pair.Control.Minds[p.CharacterId]));
                    p.TreatmentFeelTimeline.Add(Feelings(pair.Treatment.Minds[p.CharacterId]));
                }
            }

            foreach (var p in pair.People.Values)
            {
                p.ControlActions = pair.Control.Result.By(p.CharacterId).Select(a => a.Minute + ":" + a.Action.Key).ToList();
                p.TreatmentActions = pair.Treatment.Result.By(p.CharacterId).Select(a => a.Minute + ":" + a.Action.Key).ToList();
                p.ControlProfile = Profile(pair.Control, p.CharacterId);
                p.TreatmentProfile = Profile(pair.Treatment, p.CharacterId);
            }

            return pair;
        }

        static Dictionary<string, double> Feelings(Mind mind)
        {
            var d = new Dictionary<string, double>(StringComparer.Ordinal);
            foreach (var e in mind.Emotions.Live)
                if (!d.TryGetValue(e.Type, out var v) || e.Intensity > v) d[e.Type] = e.Intensity;
            return d;
        }

        static void Snapshot(string stage, Simulation sim, Pair pair, bool control)
        {
            foreach (var p in pair.People.Values)
            {
                var mind = sim.Minds[p.CharacterId];
                var feelings = mind.Emotions.Live.Count == 0
                    ? "nothing"
                    : string.Join(", ", mind.Emotions.Live.Select(e => e.ToString()));
                (control ? p.ControlFeelings : p.TreatmentFeelings)[stage] = feelings;
            }
        }

        /// <summary>
        /// What this person wants right now, raised exactly as the morning would
        /// raise it, into a trace nobody else reads. Each want is then checked for
        /// whether any reason behind it leads back to the cause.
        /// </summary>
        public static Landscape Probe(
            Scenario001Content content, Scenario001Run run, string characterId, IReadOnlyList<string> causeEventIds)
        {
            var landscape = new Landscape();
            var motives = new Motivator(content.Rules).Raise(
                run.Minds[characterId], run.Morning.See(characterId), content.Morning.Day, new TraceLog(), 0);

            foreach (var m in motives)
            {
                if (!landscape.Urgency.TryGetValue(m.Name, out var existing) || m.Urgency > existing)
                {
                    landscape.Urgency[m.Name] = m.Urgency;
                    landscape.RestsOnCause[m.Name] = ReachesCause(run.Trace, m, causeEventIds);
                }
            }

            return landscape;
        }

        /// <summary>Whether any term that actually moved a want draws on a record descended from the cause.</summary>
        public static bool ReachesCause(TraceLog trace, Motive motive, IReadOnlyList<string> causeEventIds)
        {
            if (causeEventIds == null || causeEventIds.Count == 0) return false;

            foreach (var term in motive.Terms)
            {
                if (term.Amount == 0.0) continue;
                foreach (var id in term.Drew)
                    if (trace.Chain(id).Any(r => r.EventId != null && causeEventIds.Contains(r.EventId)))
                        return true;
            }

            return false;
        }

        static IReadOnlyDictionary<string, double> Profile(Scenario001Run run, string characterId)
        {
            var mine = run.Result.By(characterId);
            if (mine.Count == 0) return new Dictionary<string, double>(StringComparer.Ordinal);

            return mine.GroupBy(a => a.Action.KindName, StringComparer.Ordinal)
                .ToDictionary(g => g.Key, g => (double)g.Count() / mine.Count, StringComparer.Ordinal);
        }
    }
}
