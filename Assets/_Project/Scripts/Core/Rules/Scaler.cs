using System.Collections.Generic;

namespace Fallow.Core.Rules
{
    /// <summary>The kinds of thing about a person that can push a rule's weight.</summary>
    public static class ScalerKind
    {
        public const string Trait = "trait";
        public const string Value = "value";
        public const string Belief = "belief";
        public const string Ledger = "ledger";
        public const string Emotion = "emotion";
        public const string Perceptiveness = "perceptiveness";
        public const string Constant = "constant";

        public static readonly IReadOnlyList<string> All =
            new[] { Trait, Value, Belief, Ledger, Emotion, Perceptiveness, Constant };
    }

    /// <summary>
    /// One reason a rule weighs more for this person than for that one. The
    /// factor may be negative, which is how a trait talks someone out of a
    /// reading rather than into it.
    /// </summary>
    public sealed class Scaler
    {
        public string Kind { get; set; }

        /// <summary>Trait, value or emotion name, depending on the kind.</summary>
        public string Name { get; set; }

        public string Predicate { get; set; }
        public IReadOnlyList<string> Args { get; set; }

        public string Entry { get; set; }
        public string About { get; set; }

        /// <summary>Who an emotion must be about. Null means about the situation.</summary>
        public string Target { get; set; }

        public double Factor { get; set; }

        /// <summary>
        /// Names this scaler for the trace. Pass a resolver and the tokens are
        /// replaced by the people they stood for, so the chain reads as a
        /// sentence about a family rather than about placeholders.
        /// </summary>
        public string Describe(System.Func<string, string> resolve = null)
        {
            string R(string token) => resolve == null ? token : resolve(token) ?? token;

            switch (Kind)
            {
                case ScalerKind.Trait: return $"trait {Name}";
                case ScalerKind.Value: return $"value {Name}";
                case ScalerKind.Belief:
                    var args = Args == null
                        ? null
                        : System.Linq.Enumerable.ToList(System.Linq.Enumerable.Select(Args, R));
                    return $"belief {Model.BeliefKey.Of(Predicate, args)}";
                case ScalerKind.Ledger: return $"remembers {Entry} of {R(About)}";
                case ScalerKind.Emotion: return $"feeling {Name}" + (Target == null ? "" : $" toward {R(Target)}");
                case ScalerKind.Perceptiveness: return "perceptiveness";
                default: return Kind ?? "unknown";
            }
        }
    }

    /// <summary>One line of the arithmetic behind a rule's weight, kept for the trace.</summary>
    public sealed class ScalerTerm
    {
        public string Description { get; }
        public double Level { get; }
        public double Factor { get; }
        public double Amount { get; }

        public ScalerTerm(string description, double level, double factor)
        {
            Description = description;
            Level = level;
            Factor = factor;
            Amount = level * factor;
        }

        public override string ToString() => $"{Description} {Level:0.00} x {Factor:0.00} = {Amount:+0.00;-0.00;0.00}";
    }
}
