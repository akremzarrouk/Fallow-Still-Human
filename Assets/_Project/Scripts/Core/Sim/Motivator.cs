using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// What the tokens stand for while a person is deciding, and how their body
    /// stands. The same shape the event pipeline supplies, so a weight is worked
    /// out identically whether it is reading a remark or pricing an action.
    /// </summary>
    public sealed class DecisionContext : IScalerContext
    {
        public Percept Percept { get; }
        public string SelfId { get; }

        /// <summary>Who the want, or the action being priced, is about.</summary>
        public string TargetId { get; }

        public int Today { get; }
        public int Now => Percept.Minute;
        public double RecallHalfLife { get; }

        public DecisionContext(Percept percept, string selfId, string targetId, int today, double recallHalfLife)
        {
            Percept = percept;
            SelfId = selfId;
            TargetId = targetId;
            Today = today;
            RecallHalfLife = recallHalfLife;
        }

        public DecisionContext About(string targetId)
            => new DecisionContext(Percept, SelfId, targetId, Today, RecallHalfLife);

        public string Resolve(string token)
        {
            if (token == null) return null;
            switch (token)
            {
                case "$self": return SelfId;
                case "$target": return TargetId;
                case "$actor": return SelfId;
                default: return token;
            }
        }

        /// <summary>
        /// The only bodily need this slice models. Everything else people want
        /// is expressed through their values and what they are feeling, which is
        /// a decision to be judged empirically rather than a claim about people.
        /// </summary>
        public double Need(string name)
            => string.Equals(name, Needs.Hunger, StringComparison.Ordinal) ? Percept.Hunger : 0.0;
    }

    /// <summary>The bodily needs the simulation knows about.</summary>
    public static class Needs
    {
        public const string Hunger = "hunger";
        public static readonly IReadOnlyList<string> All = new[] { Hunger };
    }

    /// <summary>
    /// Turns how a person is into what they currently want.
    ///
    /// Wants are not actions. Wanting not to be looked at is one want, and it
    /// does not say whether you leave, or go to your own room, or simply keep
    /// busy; that is settled afterwards by what the house allows and what each
    /// of those would cost you. Keeping the two apart is what stops this
    /// becoming a table of feelings mapped to behaviours.
    ///
    /// Nothing here reads the world. The only picture of the house it gets is
    /// the one that person can see.
    /// </summary>
    public sealed class Motivator
    {
        readonly RuleSet _rules;

        public Motivator(RuleSet rules)
        {
            _rules = rules;
        }

        public IReadOnlyList<Motive> Raise(
            Mind mind, Percept percept, int today, TraceLog trace, int parentTraceId)
        {
            var merged = new Dictionary<string, Motive>(StringComparer.Ordinal);
            var terms = new Dictionary<string, List<ScalerTerm>>(StringComparer.Ordinal);
            var rules = new Dictionary<string, List<string>>(StringComparer.Ordinal);

            foreach (var rule in _rules.Motivation)
            {
                if (rule.When != null && !rule.When.Matches(percept)) continue;

                foreach (var about in Subjects(rule, percept))
                {
                    var ctx = new DecisionContext(
                        percept, mind.Id, about, today, _rules.Deciding.RecallHalfLife);
                    var scaled = ScalerEval.Evaluate(rule.ScaledBy, mind, ctx);
                    var urgency = rule.BaseUrgency + scaled.Sum(t => t.Amount);
                    if (urgency <= 0.0) continue;

                    var key = about == null ? rule.Motive : rule.Motive + ":" + about;
                    if (!merged.TryGetValue(key, out var motive))
                    {
                        motive = new Motive(rule.Motive, about, 0.0, new List<string>(), new List<ScalerTerm>());
                        merged[key] = motive;
                        terms[key] = new List<ScalerTerm>();
                        rules[key] = new List<string>();
                    }

                    // Two reasons to want the same thing make it more pressing,
                    // each adding less than the last, so urgency stays on one
                    // scale however many rules happen to speak to it.
                    motive.Urgency = Accumulate.Toward(motive.Urgency, urgency);
                    terms[key].AddRange(scaled);
                    rules[key].Add(rule.Id);
                }
            }

            var result = merged.Values
                .OrderByDescending(m => m.Urgency)
                .ThenBy(m => m.Key, StringComparer.Ordinal)
                .ToList();

            var final = new List<Motive>();
            foreach (var m in result)
            {
                var withReasons = new Motive(m.Name, m.TargetId, m.Urgency, rules[m.Key], terms[m.Key]);
                withReasons.TraceId = trace.Add(
                    TraceKind.Motive, mind.Id, null,
                    "wants " + withReasons,
                    new[] { parentTraceId },
                    new Dictionary<string, string>
                    {
                        { "motive", m.Name },
                        { "urgency", m.Urgency.ToString("0.00") },
                        { "rules", string.Join(", ", rules[m.Key]) },
                        { "because", withReasons.Because }
                    });
                final.Add(withReasons);
            }

            return final;
        }

        /// <summary>
        /// Who a want is about. A want about the situation has one subject, which
        /// is nobody; a want about people has one per person in the room, weighed
        /// separately, so that caring about one of them is not the same as
        /// caring about whoever happens to be nearest.
        /// </summary>
        static IEnumerable<string> Subjects(MotivationRule rule, Percept percept)
        {
            if (!string.Equals(rule.Scope, MotiveScope.EachPresent, StringComparison.Ordinal))
            {
                yield return null;
                yield break;
            }

            foreach (var id in percept.Present) yield return id;
        }
    }
}
