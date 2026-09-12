using System;
using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// The things a person can physically do in this slice. Nobody speaks yet;
    /// everything here is a body in a house.
    ///
    /// The list is short on purpose. Every one of them exists because some
    /// motive in the scenario needs a way to be served, and most of them serve
    /// several different motives, which is the property that stops an action
    /// from being a disguised name for a feeling.
    /// </summary>
    public enum ActionKind
    {
        /// <summary>Stay where you are and do nothing in particular.</summary>
        Wait,

        /// <summary>Watch somebody who is in the room with you.</summary>
        Observe,

        /// <summary>Walk to another room.</summary>
        GoTo,

        /// <summary>Open the pantry and see what is actually left.</summary>
        CheckPantry,

        /// <summary>Go through the room you are standing in.</summary>
        SearchRoom,

        /// <summary>Sit with somebody who is in the room with you.</summary>
        Comfort,

        /// <summary>Take a portion and eat it.</summary>
        Eat
    }

    /// <summary>
    /// One concrete thing a person could do right now: the kind, who or where it
    /// is aimed at, and how long it would take.
    ///
    /// Options are produced from what the world allows, before anything is
    /// scored. An action that is not possible never becomes an option at all, so
    /// no amount of wanting can produce it.
    /// </summary>
    public sealed class ActionOption
    {
        public ActionKind Kind { get; }

        /// <summary>Who it is aimed at, for the actions that need somebody.</summary>
        public string TargetId { get; }

        /// <summary>Where it leads, for movement.</summary>
        public string DestinationRoomId { get; }

        /// <summary>Minutes it occupies.</summary>
        public int Duration { get; }

        public ActionOption(ActionKind kind, string targetId = null, string destinationRoomId = null, int duration = 1)
        {
            Kind = kind;
            TargetId = targetId;
            DestinationRoomId = destinationRoomId;
            Duration = duration < 1 ? 1 : duration;
        }

        /// <summary>The name a rule uses for this kind of action.</summary>
        public string KindName => NameOf(Kind);

        public static string NameOf(ActionKind kind)
        {
            switch (kind)
            {
                case ActionKind.Wait: return "wait";
                case ActionKind.Observe: return "observe";
                case ActionKind.GoTo: return "go_to";
                case ActionKind.CheckPantry: return "check_pantry";
                case ActionKind.SearchRoom: return "search_room";
                case ActionKind.Comfort: return "comfort";
                case ActionKind.Eat: return "eat";
                default: return kind.ToString().ToLowerInvariant();
            }
        }

        public static readonly IReadOnlyList<string> AllNames = new[]
        {
            "wait", "observe", "go_to", "check_pantry", "search_room", "comfort", "eat"
        };

        /// <summary>Identity for comparison: two options are the same if they would do the same thing.</summary>
        public string Key
            => KindName +
               (TargetId == null ? "" : ":" + TargetId) +
               (DestinationRoomId == null ? "" : "->" + DestinationRoomId);

        public bool SameAs(ActionOption other)
            => other != null && string.Equals(Key, other.Key, StringComparison.Ordinal);

        public override string ToString() => Key;
    }
}
