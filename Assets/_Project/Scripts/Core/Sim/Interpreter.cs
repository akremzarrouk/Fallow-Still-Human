using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>What one rule had to say, and the arithmetic behind it.</summary>
    public sealed class RuleContribution
    {
        public string RuleId { get; }
        public string Label { get; }
        public double BaseWeight { get; }
        public IReadOnlyList<ScalerTerm> Terms { get; }
        public double Total { get; }

        public RuleContribution(string ruleId, string label, double baseWeight, IReadOnlyList<ScalerTerm> terms)
        {
            RuleId = ruleId;
            Label = label;
            BaseWeight = baseWeight;
            Terms = terms ?? new List<ScalerTerm>();
            Total = baseWeight + Terms.Sum(t => t.Amount);
        }

        public override string ToString()
            => Terms.Count == 0
                ? $"{RuleId} -> {Label} {Total:0.00}"
                : $"{RuleId} -> {Label} {Total:0.00} (base {BaseWeight:0.00}; {string.Join("; ", Terms)})";
    }

    /// <summary>What an event came to mean to one person.</summary>
    public sealed class InterpretationResult
    {
        public string Meaning { get; }
        public double Weight { get; }
        public string RunnerUpMeaning { get; }
        public double RunnerUpWeight { get; }
        public bool FromOwnIntent { get; }
        public IReadOnlyList<RuleContribution> Contributions { get; }
        public int TraceId { get; internal set; }

        public InterpretationResult(
            string meaning, double weight, string runnerUpMeaning, double runnerUpWeight,
            bool fromOwnIntent, IReadOnlyList<RuleContribution> contributions)
        {
            Meaning = meaning;
            Weight = weight;
            RunnerUpMeaning = runnerUpMeaning;
            RunnerUpWeight = runnerUpWeight;
            FromOwnIntent = fromOwnIntent;
            Contributions = contributions ?? new List<RuleContribution>();
        }

        /// <summary>How clearly this reading beat the next one. Near zero means it was nearly the other thing.</summary>
        public double Margin => Weight - RunnerUpWeight;
    }

    /// <summary>
    /// Turns an event into what it meant to one person.
    ///
    /// Two things decide the answer. If the person acted, they simply know their
    /// own intention, and no rule is consulted. Otherwise every rule that fits
    /// the circumstances offers a reading, weighted by who this person is and
    /// what they already believe, remember and feel, and the heaviest reading
    /// wins. Nothing consults the world, and nothing consults another mind.
    /// </summary>
    public sealed class Interpreter
    {
        public const string Neutral = "neutral";

        readonly RuleSet _rules;

        public Interpreter(RuleSet rules)
        {
            _rules = rules;
        }

        public InterpretationResult Interpret(
            Mind perceiver,
            WorldEvent e,
            Access access,
            IReadOnlyDictionary<string, Profile> cast,
            TraceLog trace,
            int parentTraceId,
            Func<string, double> needs = null)
        {
            if (access == Access.None) return null;

            if (string.Equals(e.ActorId, perceiver.Id, StringComparison.Ordinal) && e.Intent != null)
            {
                var known = new InterpretationResult(e.Intent, 1.0, null, 0.0, true, new List<RuleContribution>());
                known.TraceId = trace.Add(
                    TraceKind.Interpretation, perceiver.Id, e.Id,
                    $"knew their own intention: {e.Intent}",
                    new[] { parentTraceId },
                    new Dictionary<string, string> { { "meaning", e.Intent }, { "source", "own intention" } });
                return known;
            }

            cast.TryGetValue(e.ActorId ?? "", out var actor);
            var ctx = new MatchContext(e, perceiver.Profile, actor, access, null, needs);

            var contributions = new List<RuleContribution>();
            var totals = new Dictionary<string, double>(StringComparer.Ordinal);

            foreach (var rule in _rules.Interpretation)
            {
                if (!rule.When.Matches(ctx)) continue;

                var terms = Evaluate(rule.ScaledBy, perceiver, ctx);
                var contribution = new RuleContribution(rule.Id, rule.Label, rule.BaseWeight, terms);
                contributions.Add(contribution);

                totals.TryGetValue(rule.Label, out var running);
                totals[rule.Label] = running + contribution.Total;
            }

            var ranked = totals
                .Where(t => t.Value > 0.0)
                .OrderByDescending(t => t.Value)
                .ThenBy(t => t.Key, StringComparer.Ordinal)
                .ToList();

            var meaning = ranked.Count > 0 ? ranked[0].Key : Neutral;
            var weight = ranked.Count > 0 ? ranked[0].Value : 0.0;
            var runnerUp = ranked.Count > 1 ? ranked[1].Key : null;
            var runnerUpWeight = ranked.Count > 1 ? ranked[1].Value : 0.0;

            var result = new InterpretationResult(meaning, weight, runnerUp, runnerUpWeight, false, contributions);

            var data = new Dictionary<string, string>
            {
                { "meaning", meaning },
                { "weight", weight.ToString("0.00") }
            };
            if (runnerUp != null) data["runner_up"] = $"{runnerUp} {runnerUpWeight:0.00}";
            if (contributions.Count > 0)
                data["rules"] = string.Join(" | ", contributions.Select(c => c.ToString()));

            // The reading rests on being there, and on every belief, memory,
            // grudge and feeling that pushed it towards what it became. Without
            // those links a reading can name in words the belief that coloured it
            // and cannot be walked back to where that belief came from.
            var restsOn = new List<int> { parentTraceId };
            foreach (var c in contributions.Where(c => c.Label == meaning))
            foreach (var t in c.Terms)
            foreach (var id in t.Drew)
                if (t.Amount != 0.0 && !restsOn.Contains(id)) restsOn.Add(id);

            result.TraceId = trace.Add(
                TraceKind.Interpretation, perceiver.Id, e.Id,
                $"read it as {meaning} ({weight:0.00})",
                restsOn,
                data);

            return result;
        }

        /// <summary>
        /// Works out how much each part of this person pushes a rule. Kept here
        /// as the name the event pipeline already used; the arithmetic itself is
        /// shared with deciding, so a weight means the same thing everywhere.
        /// </summary>
        public static IReadOnlyList<ScalerTerm> Evaluate(
            IReadOnlyList<Scaler> scalers, Mind perceiver, MatchContext ctx)
            => ScalerEval.Evaluate(scalers, perceiver, ctx);
    }
}
