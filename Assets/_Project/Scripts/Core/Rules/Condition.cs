using System;
using System.Collections.Generic;
using Fallow.Core.Model;

namespace Fallow.Core.Rules
{
    /// <summary>
    /// What a rule needs to be true before it has anything to say. Every term is
    /// optional; the ones that are present must all hold.
    ///
    /// Conditions may only ask about circumstances: what was said, how, who was
    /// there, and who those people are to each other. They may never ask about a
    /// trait, a value or a relationship strength, because that would turn a
    /// weight into a switch and make a person predictable in the wrong way.
    /// Those belong in the scalers instead.
    /// </summary>
    public sealed class Condition
    {
        public IReadOnlyList<string> EventTypes { get; set; }
        public IReadOnlyList<string> Acts { get; set; }
        public IReadOnlyList<string> Actions { get; set; }
        public IReadOnlyList<string> Topics { get; set; }
        public IReadOnlyList<string> Tones { get; set; }
        public IReadOnlyList<string> Directness { get; set; }
        public IReadOnlyList<string> Valences { get; set; }
        public IReadOnlyList<string> ActorRelations { get; set; }
        public IReadOnlyList<string> ActorRoles { get; set; }
        public IReadOnlyList<string> SelfRoles { get; set; }
        public IReadOnlyList<string> Access { get; set; }

        /// <summary>Only meaningful once the event has been read; interpretation rules leave it empty.</summary>
        public IReadOnlyList<string> Meanings { get; set; }

        /// <summary>
        /// Who the event was aimed at, from this person's seat: "me", "group",
        /// "other" or "nobody". Being one of a room addressed as a group is not
        /// the same as being the person spoken to, and rules need to tell those
        /// apart: you can watch an argument start, or you can be in it.
        /// </summary>
        public IReadOnlyList<string> Addressed { get; set; }

        public bool? ActorIsMinor { get; set; }
        public bool? SelfIsMinor { get; set; }
        public bool? HasActor { get; set; }
        public int? AudienceMin { get; set; }

        public bool Matches(MatchContext ctx)
        {
            if (!InList(EventTypes, ctx.EventTypeName)) return false;
            if (!InList(Acts, ctx.Event.Act)) return false;
            if (!InList(Actions, ctx.Event.Action)) return false;
            if (!InList(Topics, ctx.Event.Topic)) return false;
            if (!InList(Tones, ctx.Event.Tone)) return false;
            if (!InList(Directness, ctx.Event.Directness)) return false;
            if (!InList(Valences, ctx.Event.Valence)) return false;
            if (!InList(Access, ctx.AccessName)) return false;
            if (!InList(SelfRoles, ctx.Perceiver.FamilyRole)) return false;
            if (!InList(Addressed, ctx.AddressedName)) return false;

            if (Meanings != null && Meanings.Count > 0 && !InList(Meanings, ctx.Meaning)) return false;

            if (ActorRelations != null && ActorRelations.Count > 0)
            {
                if (ctx.Actor == null) return false;
                if (!InList(ActorRelations, ctx.RelationName)) return false;
            }

            if (ActorRoles != null && ActorRoles.Count > 0)
            {
                if (ctx.Actor == null) return false;
                if (!InList(ActorRoles, ctx.Actor.FamilyRole)) return false;
            }

            if (ActorIsMinor.HasValue)
            {
                if (ctx.Actor == null) return false;
                if (ctx.Actor.IsMinor != ActorIsMinor.Value) return false;
            }

            if (SelfIsMinor.HasValue && ctx.Perceiver.IsMinor != SelfIsMinor.Value) return false;
            if (HasActor.HasValue && (ctx.Actor != null) != HasActor.Value) return false;
            if (AudienceMin.HasValue && ctx.AudienceSize < AudienceMin.Value) return false;

            return true;
        }

        static bool InList(IReadOnlyList<string> allowed, string actual)
        {
            if (allowed == null || allowed.Count == 0) return true;
            if (actual == null) return false;
            for (var i = 0; i < allowed.Count; i++)
                if (string.Equals(allowed[i], actual, StringComparison.Ordinal))
                    return true;
            return false;
        }
    }

    /// <summary>Everything a rule is allowed to look at, assembled once per event per person.</summary>
    public sealed class MatchContext
    {
        public WorldEvent Event { get; }
        public Profile Perceiver { get; }
        public Profile Actor { get; }
        public Model.Access AccessLevel { get; }
        public int AudienceSize { get; }
        public bool TargetsSelf { get; }
        public Relation ActorRelation { get; }

        /// <summary>Null while the event is still being read; set once it has been.</summary>
        public string Meaning { get; }

        public MatchContext(
            WorldEvent worldEvent, Profile perceiver, Profile actor,
            Model.Access accessLevel, string meaning = null)
        {
            Event = worldEvent;
            Perceiver = perceiver;
            Actor = actor;
            AccessLevel = accessLevel;
            Meaning = meaning;
            AudienceSize = worldEvent.AudienceSizeFor(perceiver.Id);
            TargetsSelf = worldEvent.Targets(perceiver.Id);
            ActorRelation = actor == null ? Relation.Peer : perceiver.RelationOfActor(actor);
        }

        public MatchContext WithMeaning(string meaning)
            => new MatchContext(Event, Perceiver, Actor, AccessLevel, meaning);

        public string EventTypeName => Event.Kind == EventKind.Speech ? "speech" : "action";

        /// <summary>Who this event was aimed at, from this person's seat.</summary>
        public string AddressedName
        {
            get
            {
                if (Event.TargetId == null) return "nobody";
                if (Event.TargetsEveryone) return "group";
                return string.Equals(Event.TargetId, Perceiver.Id, StringComparison.Ordinal) ? "me" : "other";
            }
        }

        public string AccessName
            => AccessLevel == Model.Access.Witnessed ? "witnessed"
             : AccessLevel == Model.Access.Overheard ? "overheard"
             : "none";

        public string RelationName
            => ActorRelation == Relation.Self ? "self"
             : ActorRelation == Relation.Junior ? "junior"
             : ActorRelation == Relation.Senior ? "senior"
             : "peer";

        /// <summary>Resolves the tokens a rule may use in place of a name.</summary>
        public string Resolve(string token)
        {
            if (token == null) return null;
            switch (token)
            {
                case "$actor": return Event.ActorId;
                case "$self": return Perceiver.Id;
                case "$target": return Event.TargetsEveryone ? null : Event.TargetId;
                default: return token;
            }
        }
    }
}
