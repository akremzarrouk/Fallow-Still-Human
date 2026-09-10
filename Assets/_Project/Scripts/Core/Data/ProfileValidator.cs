using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;

namespace Fallow.Core.Data
{
    /// <summary>
    /// Checks a character file against the vocabulary. A misspelled trait would
    /// otherwise read as zero and a misspelled belief pattern would sit inert,
    /// so both are reported rather than tolerated.
    /// </summary>
    public static class ProfileValidator
    {
        public static IReadOnlyList<string> Validate(Profile p, Vocabulary vocab)
        {
            var problems = new List<string>();
            var who = string.IsNullOrEmpty(p.Id) ? "<no id>" : p.Id;

            if (string.IsNullOrEmpty(p.Id)) problems.Add("character has no id");
            if (string.IsNullOrEmpty(p.DisplayName)) problems.Add($"{who}: no display_name");
            if (p.Age <= 0) problems.Add($"{who}: age must be positive, got {p.Age}");

            if (!vocab.Contains("family_roles", p.FamilyRole))
                problems.Add($"{who}: unknown family_role '{p.FamilyRole}'");

            foreach (var t in p.Traits)
            {
                if (!vocab.Contains("traits", t.Key))
                    problems.Add($"{who}: unknown trait '{t.Key}'");
                if (t.Value < 0.0 || t.Value > 1.0)
                    problems.Add($"{who}: trait '{t.Key}' must be within 0..1, got {t.Value}");
            }

            foreach (var expected in vocab.Traits)
                if (!p.Traits.ContainsKey(expected))
                    problems.Add($"{who}: does not declare trait '{expected}'");

            var seenValues = new HashSet<string>();
            foreach (var v in p.Values)
            {
                if (!vocab.Contains("values", v))
                    problems.Add($"{who}: unknown value '{v}'");
                if (!seenValues.Add(v))
                    problems.Add($"{who}: value '{v}' is ranked twice");
            }
            if (p.Values.Count == 0)
                problems.Add($"{who}: ranks no values, so nothing can matter to them");

            if (p.Perceptiveness < 0.0 || p.Perceptiveness > 1.0)
                problems.Add($"{who}: perceptiveness must be within 0..1, got {p.Perceptiveness}");

            foreach (var a in p.AttentionWeights)
            {
                if (!vocab.IsMeaning(a.Key))
                    problems.Add($"{who}: attention names '{a.Key}', which is not a meaning");
                if (a.Value <= 0.0)
                    problems.Add($"{who}: attention for '{a.Key}' must be above zero, got {a.Value}");
            }

            foreach (var b in p.InitialBeliefs)
                problems.AddRange(ValidateBelief(who, b, vocab));

            return problems;
        }

        static IEnumerable<string> ValidateBelief(string who, BeliefSeed b, Vocabulary vocab)
        {
            if (b.Predicate == null || !vocab.BeliefPredicates.TryGetValue(b.Predicate, out var spec))
            {
                yield return $"{who}: unknown belief predicate '{b.Predicate}'";
                yield break;
            }

            if (b.Args.Count != spec.Arity)
            {
                yield return $"{who}: belief '{b.Predicate}' takes {spec.Arity} arguments, got {b.Args.Count}";
                yield break;
            }

            for (var i = 0; i < spec.Arity; i++)
            {
                var domain = spec.ArgDomains[i];
                if (domain == Vocabulary.CharacterDomain) continue;
                if (!vocab.Contains(domain, b.Args[i]))
                    yield return $"{who}: belief '{b.Key}' argument {i + 1} '{b.Args[i]}' is not in '{domain}'";
            }

            if (b.Confidence < 0.0 || b.Confidence > 1.0)
                yield return $"{who}: belief '{b.Key}' confidence must be within 0..1, got {b.Confidence}";
        }

        /// <summary>
        /// Cast-level checks that a single file cannot make: that every character
        /// a belief refers to actually exists.
        /// </summary>
        public static IReadOnlyList<string> ValidateCast(
            IReadOnlyDictionary<string, Profile> cast, Vocabulary vocab)
        {
            var problems = new List<string>();

            foreach (var p in cast.Values)
            {
                foreach (var b in p.InitialBeliefs)
                {
                    if (b.Predicate == null || !vocab.BeliefPredicates.TryGetValue(b.Predicate, out var spec))
                        continue;
                    for (var i = 0; i < spec.Arity && i < b.Args.Count; i++)
                    {
                        if (spec.ArgDomains[i] != Vocabulary.CharacterDomain) continue;
                        if (!cast.ContainsKey(b.Args[i]))
                            problems.Add($"{p.Id}: belief '{b.Key}' names '{b.Args[i]}', who is not in the cast");
                    }
                }
            }

            return problems;
        }
    }
}
