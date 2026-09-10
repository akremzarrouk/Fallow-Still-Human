using System;
using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// Something that happened. This is world truth: the record of the act
    /// itself, before anybody has made anything of it. No mind reads a
    /// WorldEvent directly; each one receives only what its access allows and
    /// keeps its own version.
    /// </summary>
    public sealed class WorldEvent
    {
        /// <summary>The target value meaning the whole room rather than one person.</summary>
        public const string Everyone = "all";

        readonly HashSet<string> _witnesses;
        readonly HashSet<string> _overhearers;

        public string Id { get; }
        public int Day { get; }
        public int Order { get; }
        public EventKind Kind { get; }

        /// <summary>Null when the world acted rather than a person.</summary>
        public string ActorId { get; }

        /// <summary>A character id, the Everyone constant, or null.</summary>
        public string TargetId { get; }

        public string Act { get; }
        public string Action { get; }
        public string Topic { get; }
        public string Tone { get; }
        public string Directness { get; }
        public string Valence { get; }

        /// <summary>
        /// What the actor was trying to do. Only the actor knows this; it becomes
        /// their own memory of the event, and nobody else's.
        /// </summary>
        public string Intent { get; }

        public string Summary { get; }
        public IReadOnlyList<LedgerEffect> LedgerEffects { get; }

        public WorldEvent(
            string id, int day, int order, EventKind kind,
            string actorId, string targetId,
            string act, string action, string topic, string tone, string directness, string valence,
            string intent, string summary,
            IReadOnlyCollection<string> witnesses,
            IReadOnlyCollection<string> overhearers,
            IReadOnlyList<LedgerEffect> ledgerEffects)
        {
            Id = id;
            Day = day;
            Order = order;
            Kind = kind;
            ActorId = actorId;
            TargetId = targetId;
            Act = act;
            Action = action;
            Topic = topic;
            Tone = tone;
            Directness = directness;
            Valence = valence;
            Intent = intent;
            Summary = summary;
            _witnesses = new HashSet<string>(witnesses ?? Array.Empty<string>(), StringComparer.Ordinal);
            _overhearers = new HashSet<string>(overhearers ?? Array.Empty<string>(), StringComparer.Ordinal);
            LedgerEffects = ledgerEffects ?? new List<LedgerEffect>();
        }

        public IReadOnlyCollection<string> Witnesses => _witnesses;
        public IReadOnlyCollection<string> Overhearers => _overhearers;

        public bool TargetsEveryone => string.Equals(TargetId, Everyone, StringComparison.Ordinal);

        /// <summary>Was this aimed at the given person, either directly or as part of the room.</summary>
        public bool Targets(string characterId)
        {
            if (characterId == null) return false;
            if (TargetsEveryone) return !string.Equals(characterId, ActorId, StringComparison.Ordinal);
            return string.Equals(TargetId, characterId, StringComparison.Ordinal);
        }

        /// <summary>
        /// How much of this reached the given person. Doing something counts as
        /// witnessing it: nobody has to be told what they themselves just did.
        /// </summary>
        public Access AccessFor(string characterId)
        {
            if (characterId == null) return Access.None;
            if (string.Equals(characterId, ActorId, StringComparison.Ordinal)) return Access.Witnessed;
            if (_witnesses.Contains(characterId)) return Access.Witnessed;
            if (_overhearers.Contains(characterId)) return Access.Overheard;
            return Access.None;
        }

        /// <summary>Everyone present besides the actor and the given person.</summary>
        public int AudienceSizeFor(string characterId)
        {
            var n = 0;
            foreach (var w in _witnesses)
            {
                if (string.Equals(w, characterId, StringComparison.Ordinal)) continue;
                if (string.Equals(w, ActorId, StringComparison.Ordinal)) continue;
                n++;
            }
            return n;
        }

        public override string ToString() => $"[{Id}] {Summary}";
    }
}
