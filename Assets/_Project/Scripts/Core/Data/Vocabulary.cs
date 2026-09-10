using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Data
{
    /// <summary>
    /// The controlled name lists the whole slice validates against. Keeping them
    /// in one loaded object means a typo in a character file, an event or a rule
    /// is a test failure rather than a silently inert rule.
    /// </summary>
    public sealed class Vocabulary
    {
        /// <summary>Argument domain meaning "any character in the cast", checked at cast level, not here.</summary>
        public const string CharacterDomain = "character";

        readonly IReadOnlyDictionary<string, IReadOnlyCollection<string>> _sets;

        public IReadOnlyDictionary<string, BeliefPredicateSpec> BeliefPredicates { get; }

        public Vocabulary(
            IReadOnlyDictionary<string, IReadOnlyCollection<string>> sets,
            IReadOnlyDictionary<string, BeliefPredicateSpec> beliefPredicates)
        {
            _sets = sets ?? new Dictionary<string, IReadOnlyCollection<string>>();
            BeliefPredicates = beliefPredicates ?? new Dictionary<string, BeliefPredicateSpec>();
        }

        public bool HasSet(string setName) => setName != null && _sets.ContainsKey(setName);

        public IReadOnlyCollection<string> Set(string setName)
            => setName != null && _sets.TryGetValue(setName, out var s)
                ? s
                : Array.Empty<string>();

        /// <summary>True when the name belongs to the named set. An unknown set never matches.</summary>
        public bool Contains(string setName, string name)
            => name != null && setName != null
               && _sets.TryGetValue(setName, out var s)
               && s.Contains(name);

        public IReadOnlyCollection<string> SetNames => _sets.Keys.ToList();

        public IReadOnlyCollection<string> Traits => Set("traits");
        public IReadOnlyCollection<string> Values => Set("values");
        public IReadOnlyCollection<string> Meanings => Set("meanings");
        public IReadOnlyCollection<string> SelfMeanings => Set("self_meanings");
        public IReadOnlyCollection<string> Emotions => Set("emotions");
        public IReadOnlyCollection<string> LedgerEntries => Set("ledger_entries");

        /// <summary>A meaning may come from a reading of someone else or from knowing one's own intention.</summary>
        public bool IsMeaning(string name) => Contains("meanings", name) || Contains("self_meanings", name);
    }

    /// <summary>What a belief predicate takes, so validation stays data-driven.</summary>
    public sealed class BeliefPredicateSpec
    {
        public IReadOnlyList<string> ArgDomains { get; }

        public BeliefPredicateSpec(IReadOnlyList<string> argDomains)
        {
            ArgDomains = argDomains ?? new List<string>();
        }

        public int Arity => ArgDomains.Count;
    }
}
