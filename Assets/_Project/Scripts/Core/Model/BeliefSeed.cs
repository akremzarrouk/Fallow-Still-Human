using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// A belief a character already holds when the scenario starts, carried over
    /// from a life the simulation never ran. Seeds are the only beliefs that
    /// arrive without an evidence path, which is why they live in character data
    /// and nowhere else.
    /// </summary>
    public sealed class BeliefSeed
    {
        public string Predicate { get; }
        public IReadOnlyList<string> Args { get; }
        public double Confidence { get; }

        public BeliefSeed(string predicate, IReadOnlyList<string> args, double confidence)
        {
            Predicate = predicate;
            Args = args ?? new List<string>();
            Confidence = confidence;
        }

        public string Key => BeliefKey.Of(Predicate, Args);

        public override string ToString() => $"{Key}={Confidence:0.00}";
    }

    /// <summary>Canonical string key for a proposition, so beliefs can be looked up.</summary>
    public static class BeliefKey
    {
        public static string Of(string predicate, IReadOnlyList<string> args)
            => args == null || args.Count == 0
                ? predicate
                : predicate + "(" + string.Join(",", args) + ")";
    }
}
