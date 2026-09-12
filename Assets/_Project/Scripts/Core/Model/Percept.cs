using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Model
{
    /// <summary>
    /// The house as one person can currently know it.
    ///
    /// This type exists to make knowledge locality structural rather than a rule
    /// everyone has to remember. Deliberation is handed a Percept and never the
    /// world, so a character physically cannot decide on the strength of who is
    /// in another room, or how much food is left in a pantry they have not
    /// opened. If a fact is not on this object, nothing they do can depend on it.
    /// </summary>
    public sealed class Percept
    {
        readonly RoomGraph _house;

        public string CharacterId { get; }
        public int Minute { get; }
        public Room Room { get; }

        /// <summary>The others in the room with me, in a fixed order.</summary>
        public IReadOnlyList<string> Present { get; }

        /// <summary>Rooms I could walk into from here. Knowing my own house is not privileged.</summary>
        public IReadOnlyList<string> Adjacent { get; }

        /// <summary>How hungry I am, and nobody else.</summary>
        public double Hunger { get; }

        /// <summary>True if the room I am standing in is where the food is kept.</summary>
        public bool RoomHoldsFood { get; }

        /// <summary>
        /// Whether there is food here to take, which I know only because I am
        /// standing in front of it. Null anywhere else in the house.
        /// </summary>
        public bool? FoodWithinReach { get; }

        /// <summary>Whether I have already been through this room myself.</summary>
        public bool SearchedThisRoomMyself { get; }

        /// <summary>Whether I have already opened the pantry and seen for myself.</summary>
        public bool LookedInThePantryMyself { get; }

        /// <summary>
        /// People I have watched recently enough that watching them again would
        /// show me nothing I do not already have.
        /// </summary>
        public IReadOnlyList<string> JustWatched { get; }

        /// <summary>
        /// Rooms I have been through myself. My own memory of my own morning,
        /// which is why it is here and not read off the world: another person
        /// having searched a room is no help to me at all.
        /// </summary>
        public IReadOnlyList<string> RoomsIHaveSearched { get; }

        public Percept(
            string characterId, int minute, Room room, IReadOnlyList<string> present,
            IReadOnlyList<string> adjacent, double hunger,
            bool roomHoldsFood, bool? foodWithinReach, bool searchedThisRoomMyself,
            RoomGraph house, bool lookedInThePantryMyself = false,
            IReadOnlyList<string> justWatched = null,
            IReadOnlyList<string> roomsIHaveSearched = null)
        {
            LookedInThePantryMyself = lookedInThePantryMyself;
            JustWatched = justWatched ?? new List<string>();
            RoomsIHaveSearched = roomsIHaveSearched ?? new List<string>();
            CharacterId = characterId;
            Minute = minute;
            Room = room;
            Present = present ?? new List<string>();
            Adjacent = adjacent ?? new List<string>();
            Hunger = hunger;
            RoomHoldsFood = roomHoldsFood;
            FoodWithinReach = foodWithinReach;
            SearchedThisRoomMyself = searchedThisRoomMyself;
            _house = house;
        }

        public bool Alone => Present.Count == 0;
        public bool InOwnRoom => Room != null && Room.IsOwnedBy(CharacterId);

        /// <summary>Somebody else sleeps here, and I do not.</summary>
        public bool InSomebodyElsesRoom
            => Room != null && Room.OwnerIds.Count > 0 && !Room.IsOwnedBy(CharacterId);

        /// <summary>The nearest room of a given kind.</summary>
        public string NearestTagged(string tag) => Nearest(tag, false);

        /// <summary>The nearest room of a given kind that I have not been through.</summary>
        public string NearestUnsearched(string tag) => Nearest(tag, true);

        string Nearest(string tag, bool unsearchedOnly)
        {
            if (_house == null || Room == null) return null;

            return _house.Tagged(tag)
                .Where(r => !unsearchedOnly || !RoomsIHaveSearched.Contains(r.Id, StringComparer.Ordinal))
                .Select(r => new { r.Id, D = _house.Distance(Room.Id, r.Id) })
                .Where(x => x.D >= 0)
                .OrderBy(x => x.D)
                .ThenBy(x => x.Id, StringComparer.Ordinal)
                .Select(x => x.Id)
                .FirstOrDefault();
        }

        /// <summary>How far away a room is, in moves.</summary>
        public int DistanceTo(string roomId)
            => _house == null || Room == null ? -1 : _house.Distance(Room.Id, roomId);

        public override string ToString()
            => CharacterId + " in " + (Room == null ? "nowhere" : Room.Id) + " at minute " + Minute +
               ", with " + (Present.Count == 0 ? "nobody" : string.Join(", ", Present));
    }
}
