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
            int parentTraceId)
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
            var ctx = new MatchContext(e, perceiver.Profile, actor, access);

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

            result.TraceId = trace.Add(
                TraceKind.Interpretation, perceiver.Id, e.Id,
                $"read it as {meaning} ({weight:0.00})",
                new[] { parentTraceId },
                data);

            return result;
        }

        /// <summary>
        /// Works out how much each part of this person pushes a rule. Public so
        /// the appraiser and the belief nudges use exactly the same arithmetic.
        /// </summary>
        public static IReadOnlyList<ScalerTerm> Evaluate(
            IReadOnlyList<Scaler> scalers, Mind perceiver, MatchContext ctx)
        {
            var terms = new List<ScalerTerm>();
            if (scalers == null) return terms;

            foreach (var s in scalers)
            {
                double level;
                switch (s.Kind)
                {
                    case ScalerKind.Trait:
                        level = perceiver.Profile.Trait(s.Name);
                        break;
                    case ScalerKind.Value:
                        level = perceiver.Profile.ValueWeight(s.Name);
                        break;
                    case ScalerKind.Perceptiveness:
                        level = perceiver.Profile.Perceptiveness;
                        break;
                    case ScalerKind.Emotion:
                        level = perceiver.Emotions.Intensity(s.Name, ctx.Resolve(s.Target));
                        break;
                    case ScalerKind.Ledger:
                        level = perceiver.Ledger.Strength(ctx.Resolve(s.About), s.Entry);
                        break;
                    case ScalerKind.Belief:
                        level = perceiver.Beliefs.Confidence(
                            s.Predicate, s.Args.Select(ctx.Resolve).ToList());
                        break;
                    case ScalerKind.Constant:
                        level = 1.0;
                        break;
                    default:
                        continue;
                }

                terms.Add(new ScalerTerm(s.Describe(), level, s.Factor));
            }

            return terms;
        }
    }
}
