using System.Collections.Generic;
using Fallow.Core.Model;

namespace Fallow.Core.Rules
{
    /// <summary>
    /// What a decision rule needs to be true of the moment before it has
    /// anything to say.
    ///
    /// The same restriction applies as in the event pipeline, for the same
    /// reason: a condition may only ask about circumstances. Where I am, whether
    /// anyone is with me, whose room this is. It may never ask about a trait, a
    /// value, a feeling or how hungry I am, because that would turn a weight
    /// into a switch and give a person a threshold they could be predicted by.
    /// Everything about the person belongs in the scalers.
    /// </summary>
    public sealed class SituationCondition
    {
        public bool? Alone { get; set; }
        public bool? InOwnRoom { get; set; }
        public bool? InSomebodyElsesRoom { get; set; }
        public bool? RoomHoldsFood { get; set; }
        public bool? SearchedThisRoomMyself { get; set; }
        public int? OthersPresentMin { get; set; }

        public bool Matches(Percept p)
        {
            if (p == null) return false;
            if (Alone.HasValue && p.Alone != Alone.Value) return false;
            if (InOwnRoom.HasValue && p.InOwnRoom != InOwnRoom.Value) return false;
            if (InSomebodyElsesRoom.HasValue && p.InSomebodyElsesRoom != InSomebodyElsesRoom.Value) return false;
            if (RoomHoldsFood.HasValue && p.RoomHoldsFood != RoomHoldsFood.Value) return false;
            if (SearchedThisRoomMyself.HasValue && p.SearchedThisRoomMyself != SearchedThisRoomMyself.Value) return false;
            if (OthersPresentMin.HasValue && p.Present.Count < OthersPresentMin.Value) return false;
            return true;
        }

        public bool IsEmpty
            => !Alone.HasValue && !InOwnRoom.HasValue && !InSomebodyElsesRoom.HasValue
               && !RoomHoldsFood.HasValue && !SearchedThisRoomMyself.HasValue && !OthersPresentMin.HasValue;
    }

    /// <summary>How a proposal turns into concrete things a person could do.</summary>
    public static class Targeting
    {
        /// <summary>The action needs nobody and nowhere.</summary>
        public const string None = "none";

        /// <summary>Aimed at the person the motive is about.</summary>
        public const string MotiveTarget = "motive_target";

        /// <summary>One option for each person in the room.</summary>
        public const string EachPresent = "each_present";

        /// <summary>Walk to the nearest room of a given kind.</summary>
        public const string NearestTagged = "nearest_tagged";

        /// <summary>
        /// Walk to the nearest room of a given kind that I have not already been
        /// through. Somebody looking for something does not search the same
        /// room twice, and without this a person with a strong enough reason to
        /// look walks back and forth between two rooms all morning.
        /// </summary>
        public const string NearestUnsearched = "nearest_unsearched";

        /// <summary>Walk out, wherever that leads. One option per way out.</summary>
        public const string AwayFromHere = "away_from_here";

        public static readonly IReadOnlyList<string> All =
            new[] { None, MotiveTarget, EachPresent, NearestTagged, NearestUnsearched, AwayFromHere };
    }

    /// <summary>How widely a motive is scoped.</summary>
    public static class MotiveScope
    {
        /// <summary>One want, about nobody in particular.</summary>
        public const string Situation = "situation";

        /// <summary>One want per person in the room, weighed separately for each.</summary>
        public const string EachPresent = "each_present";

        public static readonly IReadOnlyList<string> All = new[] { Situation, EachPresent };
    }
}
