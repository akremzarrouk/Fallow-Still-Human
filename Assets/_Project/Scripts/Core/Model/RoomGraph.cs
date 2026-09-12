using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Model
{
    /// <summary>
    /// One room, what it is for, and whose it is.
    ///
    /// Rules never name a room. They ask for a kind of room, so that a rule about
    /// going where the food is kept still works in a different house.
    /// </summary>
    public sealed class Room
    {
        public string Id { get; }
        public string DisplayName { get; }
        public IReadOnlyList<string> Tags { get; }

        /// <summary>Who sleeps here. Empty for shared rooms.</summary>
        public IReadOnlyList<string> OwnerIds { get; }

        public Room(string id, string displayName, IReadOnlyList<string> tags, IReadOnlyList<string> ownerIds)
        {
            Id = id;
            DisplayName = displayName;
            Tags = tags ?? new List<string>();
            OwnerIds = ownerIds ?? new List<string>();
        }

        public bool HasTag(string tag) => tag != null && Tags.Contains(tag, StringComparer.Ordinal);
        public bool IsOwnedBy(string characterId) => characterId != null && OwnerIds.Contains(characterId, StringComparer.Ordinal);

        public override string ToString() => DisplayName;
    }

    /// <summary>
    /// The house: which rooms there are, which ones you can walk between, and
    /// which ones you can be heard from.
    ///
    /// Audibility is a property of the house rather than of physics, which is
    /// how one character comes to half-know something another one did. Hearing
    /// through a wall is the only way information crosses a room boundary in
    /// this slice; there is no other channel.
    /// </summary>
    public sealed class RoomGraph
    {
        readonly Dictionary<string, Room> _rooms = new Dictionary<string, Room>(StringComparer.Ordinal);
        readonly Dictionary<string, HashSet<string>> _adjacent = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        readonly Dictionary<string, HashSet<string>> _audible = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);

        public IReadOnlyList<Room> Rooms => _rooms.Values.OrderBy(r => r.Id, StringComparer.Ordinal).ToList();
        public IReadOnlyList<string> RoomIds => _rooms.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();

        public void AddRoom(Room room)
        {
            _rooms[room.Id] = room;
            if (!_adjacent.ContainsKey(room.Id)) _adjacent[room.Id] = new HashSet<string>(StringComparer.Ordinal);
            if (!_audible.ContainsKey(room.Id)) _audible[room.Id] = new HashSet<string>(StringComparer.Ordinal);
        }

        public void Connect(string a, string b, bool audible)
        {
            Link(_adjacent, a, b);
            if (audible) Link(_audible, a, b);
        }

        static void Link(Dictionary<string, HashSet<string>> map, string a, string b)
        {
            if (!map.TryGetValue(a, out var sa)) map[a] = sa = new HashSet<string>(StringComparer.Ordinal);
            if (!map.TryGetValue(b, out var sb)) map[b] = sb = new HashSet<string>(StringComparer.Ordinal);
            sa.Add(b);
            sb.Add(a);
        }

        public Room Get(string roomId)
            => roomId != null && _rooms.TryGetValue(roomId, out var r) ? r : null;

        public bool Has(string roomId) => roomId != null && _rooms.ContainsKey(roomId);

        public IReadOnlyList<string> Adjacent(string roomId)
            => _adjacent.TryGetValue(roomId ?? "", out var s)
                ? s.OrderBy(x => x, StringComparer.Ordinal).ToList()
                : new List<string>();

        /// <summary>Rooms from which what happens here can be heard but not seen.</summary>
        public IReadOnlyList<string> Audible(string roomId)
            => _audible.TryGetValue(roomId ?? "", out var s)
                ? s.OrderBy(x => x, StringComparer.Ordinal).ToList()
                : new List<string>();

        public IReadOnlyList<Room> Tagged(string tag)
            => Rooms.Where(r => r.HasTag(tag)).ToList();

        /// <summary>
        /// How many moves it takes to get there, or -1 if you cannot. Ties in the
        /// search are broken by name so that the same house always walks the
        /// same way.
        /// </summary>
        public int Distance(string from, string to)
        {
            if (from == null || to == null || !Has(from) || !Has(to)) return -1;
            if (string.Equals(from, to, StringComparison.Ordinal)) return 0;

            var seen = new HashSet<string>(StringComparer.Ordinal) { from };
            var frontier = new List<string> { from };
            var steps = 0;

            while (frontier.Count > 0)
            {
                steps++;
                var next = new List<string>();
                foreach (var room in frontier)
                foreach (var n in Adjacent(room))
                {
                    if (!seen.Add(n)) continue;
                    if (string.Equals(n, to, StringComparison.Ordinal)) return steps;
                    next.Add(n);
                }
                frontier = next;
            }

            return -1;
        }
    }
}
