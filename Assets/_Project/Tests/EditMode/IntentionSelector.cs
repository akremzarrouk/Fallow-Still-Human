using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Newtonsoft.Json.Linq;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The experimental intention selector, shared by the intention-formation
    /// experiment and the generalization experiment that follows it, so that
    /// both run the same mechanism rather than two copies that could drift.
    ///
    /// Experiment code. Nothing in `Fallow.Core` knows this exists, and the
    /// `IntentOfAct` hook it is installed on stays null unless a test sets it.
    ///
    /// A candidate rule says an intention is AVAILABLE to a set of wants, in
    /// given circumstances, weighing an amount that depends on the person. It
    /// never says a want must express it. Two properties are structural rather
    /// than promised: `when` is the shipped `SituationCondition`, which has no
    /// field for a trait, a value, a feeling or a need, so a circumstance can
    /// gate a candidate but can never be the reason one wins; and everything
    /// about the person is a scaler, evaluated by the shipped `ScalerEval`.
    /// There is no randomness anywhere in here.
    /// </summary>
    public static class IntentionSelector
    {
        static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);

        /// <summary>One authored claim about when an intention is available.</summary>
        public sealed class Candidate
        {
            public string Id;
            public string Note;
            public IReadOnlyList<string> Motives;
            public string Intent;
            public SituationCondition When;
            public double Base;
            public IReadOnlyList<Scaler> ScaledBy;

            /// <summary>A copy under a new id, for the redundant-rule experiment.</summary>
            public Candidate CloneAs(string id, double scale = 1.0)
                => new Candidate
                {
                    Id = id,
                    Note = Note,
                    Motives = Motives.ToList(),
                    Intent = Intent,
                    When = When,
                    Base = Base * scale,
                    ScaledBy = ScaledBy.Select(s => new Scaler
                    {
                        Kind = s.Kind, Name = s.Name, Predicate = s.Predicate, Args = s.Args,
                        Entry = s.Entry, About = s.About, Topic = s.Topic, By = s.By,
                        Until = s.Until, Target = s.Target, Factor = s.Factor * scale
                    }).ToList()
                };
        }

        /// <summary>
        /// The whole of the experiment's parser. It reads the same keys the
        /// shipped loaders read, so a scaler written in a candidate file means
        /// what it would mean in `rules.json`.
        /// </summary>
        public static IReadOnlyList<Candidate> Load(string path)
        {
            var root = JObject.Parse(File.ReadAllText(path));
            var list = new List<Candidate>();
            foreach (var c in (JArray)root["candidates"])
            {
                var w = c["when"] as JObject;
                list.Add(new Candidate
                {
                    Id = c["id"].Value<string>(),
                    Note = c["note"]?.Value<string>(),
                    Motives = ((JArray)c["motives"]).Select(x => x.Value<string>()).ToList(),
                    Intent = c["intent"].Value<string>(),
                    Base = c["base"]?.Value<double>() ?? 0.0,
                    When = new SituationCondition
                    {
                        Alone = w?["alone"]?.Value<bool>(),
                        InOwnRoom = w?["in_own_room"]?.Value<bool>(),
                        InSomebodyElsesRoom = w?["in_somebody_elses_room"]?.Value<bool>(),
                        RoomHoldsFood = w?["room_holds_food"]?.Value<bool>(),
                        SearchedThisRoomMyself = w?["searched_this_room_myself"]?.Value<bool>(),
                        OthersPresentMin = w?["others_present_min"]?.Value<int>()
                    },
                    ScaledBy = (c["scaled_by"] as JArray ?? new JArray()).Select(s => new Scaler
                    {
                        Kind = s["kind"]?.Value<string>(),
                        Name = s["name"]?.Value<string>(),
                        Predicate = s["predicate"]?.Value<string>(),
                        Args = (s["args"] as JArray ?? new JArray()).Select(a => a.Value<string>()).ToList(),
                        Entry = s["entry"]?.Value<string>(),
                        About = s["about"]?.Value<string>(),
                        Topic = s["topic"]?.Value<string>(),
                        Target = s["target"]?.Value<string>(),
                        Factor = s["factor"]?.Value<double>() ?? 0.0
                    }).ToList()
                });
            }
            return list;
        }

        /// <summary>One intention that was in the running, and what it weighed.</summary>
        public sealed class Weighed
        {
            public string Intent;
            public double Weight;
            public List<string> Rules = new List<string>();
            public List<string> Why = new List<string>();

            public string Long => Intent + " " + F(Weight) + " [" + string.Join(" + ", Rules) + "]";
        }

        /// <summary>What the selector settled on, and everything it weighed to get there.</summary>
        public sealed class Formed
        {
            public string Intent;
            public double Weight;
            public string RunnerUp;
            public double RunnerUpWeight;
            public IReadOnlyList<Weighed> Considered = new List<Weighed>();
            public int Matched;
            public int InScope;

            public double Margin => Weight - RunnerUpWeight;

            public string Line => Intent == null ? "none"
                : Intent + " " + F(Weight) + (RunnerUp == null ? "" : " over " + RunnerUp + " " + F(RunnerUpWeight));
        }

        /// <summary>
        /// Form an intention from a want and a moment.
        ///
        /// Candidates in scope for the want, gated by circumstance, weighed by
        /// who this person is through the shipped scaler machinery, summed per
        /// intention the way interpretation rules speaking for the same reading
        /// are summed, and the heaviest wins. Ties break ordinally. Nothing here
        /// consults a die, a table keyed on the want alone, or the act.
        /// </summary>
        public static Formed Form(
            IReadOnlyList<Candidate> candidates, Mind mind, Percept percept, Motive motive,
            int today, double recallHalfLife)
        {
            var formed = new Formed();
            if (motive == null || percept == null) return formed;

            var ctx = new DecisionContext(percept, mind.Id, motive.TargetId, today, recallHalfLife);

            var byIntent = new Dictionary<string, Weighed>(StringComparer.Ordinal);
            foreach (var c in candidates)
            {
                if (!c.Motives.Contains(motive.Name, StringComparer.Ordinal)) continue;
                formed.InScope++;
                if (!c.When.Matches(percept)) continue;
                formed.Matched++;

                var terms = ScalerEval.Evaluate(c.ScaledBy, mind, ctx);
                var weight = c.Base + terms.Sum(t => t.Amount);
                if (weight <= 0.0) continue;

                if (!byIntent.TryGetValue(c.Intent, out var w))
                    byIntent[c.Intent] = w = new Weighed { Intent = c.Intent };
                w.Weight += weight;
                w.Rules.Add(c.Id + " " + F(weight));
                foreach (var t in terms.Where(t => Math.Abs(t.Amount) > 1e-9))
                    w.Why.Add(t.Description + " " + F(t.Level) + " x " + F(t.Factor) + " = " + F(t.Amount));
            }

            var ranked = byIntent.Values
                .OrderByDescending(w => w.Weight)
                .ThenBy(w => w.Intent, StringComparer.Ordinal)
                .ToList();

            formed.Considered = ranked;
            if (ranked.Count == 0) return formed;
            formed.Intent = ranked[0].Intent;
            formed.Weight = ranked[0].Weight;
            if (ranked.Count > 1)
            {
                formed.RunnerUp = ranked[1].Intent;
                formed.RunnerUpWeight = ranked[1].Weight;
            }
            return formed;
        }
    }
}
