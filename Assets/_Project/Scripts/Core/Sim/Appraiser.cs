using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
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
        /// Works out what this reading stirred.
        ///
        /// Intensity runs 0 to 1, where 1 is as hard as this person feels
        /// anything and is never quite reached. Several rules pushing the same
        /// feeling add up, and the total is then squashed onto that scale, so a
        /// feeling cannot be stacked past the top of it by writing another rule
        /// and two strong feelings stay tellable apart. How directly the person
        /// met the event,
        /// and how primed they are to notice that kind of thing, scale each push
        /// before it is folded in; neither can change which feeling wins, only
        /// how hard it lands.
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
            var drew = new Dictionary<string, List<int>>(StringComparer.Ordinal);

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
                    drew[key] = new List<int>();
                }

                foreach (var t in terms)
                foreach (var id in t.Drew)
                    if (t.Amount != 0.0 && !drew[key].Contains(id)) drew[key].Add(id);

                // Kept as a raw total for now and squashed onto the scale once
                // every rule has spoken, so that two strong feelings stay
                // distinguishable instead of both arriving at the ceiling.
                var landed = intensity * intensityScale;
                contribution.Intensity += landed;
                ((List<string>)contribution.RuleIds).Add(rule.Id);
                detail[key].Add(terms.Count == 0
                    ? $"{rule.Id} {landed:0.00}"
                    : $"{rule.Id} {landed:0.00} (base {rule.BaseIntensity:0.00}; {string.Join("; ", terms)})");

                // The concern reported is the one from the rule that pushed hardest.
                if (landed > best[key]) best[key] = landed;
            }

            foreach (var c in merged.Values) c.Intensity = Accumulate.Saturate(c.Intensity);

            var results = merged.Values
                .OrderByDescending(c => c.Intensity)
                .ThenBy(c => c.Type, StringComparer.Ordinal)
                .ToList();

            foreach (var c in results)
            {
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

                var restsOn = new List<int> { parentTraceId };
                restsOn.AddRange(drew[key].Where(id => id != parentTraceId));

                c.TraceId = trace.Add(
                    TraceKind.Appraisal, perceiver.Id, ctx.Event.Id,
                    $"{ctx.Meaning} touched {c.Concern}: {c}",
                    restsOn,
                    data);
            }

            return results;
        }
    }
}
