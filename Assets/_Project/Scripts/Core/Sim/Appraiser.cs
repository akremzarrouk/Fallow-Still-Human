using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// One feeling this event produced, with the concern behind it. Several
    /// rules may speak to the same feeling; they are gathered into one
    /// contribution so that a person is shamed once, harder, rather than twice.
    /// </summary>
    public sealed class EmotionContribution
    {
        public string Type { get; }
        public string TargetId { get; }
        public string Concern { get; }
        public double Intensity { get; internal set; }
        public IReadOnlyList<string> RuleIds { get; }
        public int TraceId { get; internal set; }

        public EmotionContribution(string type, string targetId, string concern, double intensity, IReadOnlyList<string> ruleIds)
        {
            Type = type;
            TargetId = targetId;
            Concern = concern;
            Intensity = intensity;
            RuleIds = ruleIds ?? new List<string>();
        }

        public override string ToString()
            => TargetId == null
                ? $"{Type} {Intensity:0.00} ({Concern})"
                : $"{Type} {Intensity:0.00} toward {TargetId} ({Concern})";
    }

    /// <summary>
    /// Turns what an event meant into what it felt like. The same reading
    /// produces different feelings in different people because every rule is
    /// weighed by their values and temperament, which is why one person is
    /// ashamed where another is merely tired of it.
    /// </summary>
    public sealed class Appraiser
    {
        readonly RuleSet _rules;

        public Appraiser(RuleSet rules)
        {
            _rules = rules;
        }

        /// <summary>
        /// Works out what this reading stirred. Intensity is scaled by how
        /// directly the person met the event and by how primed they are to
        /// notice that kind of thing; neither can change which feeling wins,
        /// only how hard it lands.
        /// </summary>
        public IReadOnlyList<EmotionContribution> Appraise(
            Mind perceiver,
            MatchContext ctx,
            double intensityScale,
            TraceLog trace,
            int parentTraceId)
        {
            var merged = new Dictionary<string, EmotionContribution>(StringComparer.Ordinal);
            var detail = new Dictionary<string, List<string>>(StringComparer.Ordinal);
            var best = new Dictionary<string, double>(StringComparer.Ordinal);

            foreach (var rule in _rules.Appraisal)
            {
                if (!rule.When.Matches(ctx)) continue;

                var terms = Interpreter.Evaluate(rule.ScaledBy, perceiver, ctx);
                var intensity = rule.BaseIntensity + terms.Sum(t => t.Amount);
                if (intensity <= 0.0) continue;

                var target = ctx.Resolve(rule.Target);
                var key = rule.Emotion + "|" + (target ?? "");

                if (!merged.TryGetValue(key, out var contribution))
                {
                    contribution = new EmotionContribution(rule.Emotion, target, rule.Concern, 0.0, new List<string>());
                    merged[key] = contribution;
                    detail[key] = new List<string>();
                    best[key] = 0.0;
                }

                contribution.Intensity += intensity;
                ((List<string>)contribution.RuleIds).Add(rule.Id);
                detail[key].Add(terms.Count == 0
                    ? $"{rule.Id} {intensity:0.00}"
                    : $"{rule.Id} {intensity:0.00} (base {rule.BaseIntensity:0.00}; {string.Join("; ", terms)})");

                // The concern reported is the one from the rule that pushed hardest.
                if (intensity > best[key]) best[key] = intensity;
            }

            var results = merged.Values
                .OrderByDescending(c => c.Intensity)
                .ThenBy(c => c.Type, StringComparer.Ordinal)
                .ToList();

            foreach (var c in results)
            {
                c.Intensity *= intensityScale;
                var key = c.Type + "|" + (c.TargetId ?? "");

                var data = new Dictionary<string, string>
                {
                    { "emotion", c.Type },
                    { "concern", c.Concern },
                    { "intensity", c.Intensity.ToString("0.00") },
                    { "rules", string.Join(" | ", detail[key]) }
                };
                if (c.TargetId != null) data["toward"] = c.TargetId;
                if (Math.Abs(intensityScale - 1.0) > 1e-9)
                    data["scaled_by_reach"] = intensityScale.ToString("0.00");

                c.TraceId = trace.Add(
                    TraceKind.Appraisal, perceiver.Id, ctx.Event.Id,
                    $"{ctx.Meaning} touched {c.Concern}: {c}",
                    new[] { parentTraceId },
                    data);
            }

            return results;
        }
    }
}
