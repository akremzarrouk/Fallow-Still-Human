using System;
using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// Who someone is, before anything happens to them: stable traits, ranked
    /// values, how well they read a room, and the beliefs they already carry.
    ///
    /// Traits and values never gate a decision. They scale weights. Nothing in
    /// the simulation asks "is this person proud enough"; it asks "how much does
    /// pride push this reading", which is why every accessor returns a number
    /// rather than a verdict.
    /// </summary>
    public sealed class Profile
    {
        /// <summary>How much weight a value loses per step down someone's priorities.</summary>
        public const double ValueRankDecay = 0.25;

        /// <summary>Age below which a character is treated as a minor by role rules.</summary>
        public const int MinorAge = 18;

        readonly IReadOnlyDictionary<string, double> _traits;
        readonly IReadOnlyDictionary<string, double> _attention;
        readonly IReadOnlyList<string> _values;

        public string Id { get; }
        public string DisplayName { get; }
        public int Age { get; }
        public string FamilyRole { get; }
        public double Perceptiveness { get; }
        public IReadOnlyList<BeliefSeed> InitialBeliefs { get; }

        public IReadOnlyDictionary<string, double> Traits => _traits;
        public IReadOnlyDictionary<string, double> AttentionWeights => _attention;
        public IReadOnlyList<string> Values => _values;

        public Profile(
            string id,
            string displayName,
            int age,
            string familyRole,
            IReadOnlyDictionary<string, double> traits,
            IReadOnlyList<string> values,
            double perceptiveness,
            IReadOnlyDictionary<string, double> attention,
            IReadOnlyList<BeliefSeed> initialBeliefs)
        {
            Id = id;
            DisplayName = displayName;
            Age = age;
            FamilyRole = familyRole;
            _traits = traits ?? new Dictionary<string, double>();
            _values = values ?? new List<string>();
            Perceptiveness = perceptiveness;
            _attention = attention ?? new Dictionary<string, double>();
            InitialBeliefs = initialBeliefs ?? new List<BeliefSeed>();
        }

        /// <summary>Trait level in 0..1. An undeclared trait reads as zero, never as an error.</summary>
        public double Trait(string name)
            => name != null && _traits.TryGetValue(name, out var v) ? v : 0.0;

        /// <summary>
        /// How much this person cares about a value, derived from where it sits
        /// in their priorities. A value they do not hold weighs nothing.
        /// </summary>
        public double ValueWeight(string name)
        {
            if (name == null) return 0.0;
            for (var i = 0; i < _values.Count; i++)
            {
                if (!string.Equals(_values[i], name, StringComparison.Ordinal)) continue;
                var w = 1.0 - i * ValueRankDecay;
                return w > 0.0 ? w : 0.0;
            }
            return 0.0;
        }

        /// <summary>
        /// How readily this person notices a given kind of meaning. One is
        /// ordinary attention; above one is a person primed to see it.
        /// </summary>
        public double Attention(string meaning)
            => meaning != null && _attention.TryGetValue(meaning, out var v) ? v : 1.0;

        public bool IsMinor => Age < MinorAge;

        /// <summary>What the given actor is to me: myself, a junior, a peer, or a senior.</summary>
        public Relation RelationOfActor(Profile actor)
        {
            if (actor == null) return Relation.Peer;
            if (string.Equals(actor.Id, Id, StringComparison.Ordinal)) return Relation.Self;
            if (actor.Age < Age) return Relation.Junior;
            if (actor.Age > Age) return Relation.Senior;
            return Relation.Peer;
        }

        public override string ToString() => $"{DisplayName} ({Id}, {Age})";
    }
}
