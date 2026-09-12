using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Model
{
    /// <summary>
    /// What is true of the house right now: the time, where everybody is, what
    /// is left in the pantry, how hungry each person is, and which rooms have
    /// been gone through.
    ///
    /// This is world truth. No mind reads it. Characters are handed a Percept
    /// built from it, which contains only what their position allows them to
    /// know, and every rule that decides anything reads the Percept instead.
    /// </summary>
    public sealed class WorldState
    {
        readonly Dictionary<string, string> _where = new Dictionary<string, string>(StringComparer.Ordinal);
        readonly Dictionary<string, double> _hunger = new Dictionary<string, double>(StringComparer.Ordinal);
        readonly HashSet<string> _searched = new HashSet<string>(StringComparer.Ordinal);

        public RoomGraph House { get; }

        /// <summary>Minutes since the morning began.</summary>
        public int Minute { get; private set; }

        /// <summary>Portions left in the pantry. The number nobody can see without looking.</summary>
        public int Portions { get; private set; }

        public WorldState(RoomGraph house, int portions)
        {
            House = house;
            Portions = portions;
        }

        public IReadOnlyList<string> Inhabitants
            => _where.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();

        public void Place(string characterId, string roomId)
        {
            if (characterId == null || !House.Has(roomId))
                throw new ArgumentException("cannot place '" + characterId + "' in '" + roomId + "'");
            _where[characterId] = roomId;
        }

        public string RoomOf(string characterId)
            => characterId != null && _where.TryGetValue(characterId, out var r) ? r : null;

        /// <summary>Everyone in the given room, in a fixed order.</summary>
        public IReadOnlyList<string> InRoom(string roomId)
            => _where.Where(p => string.Equals(p.Value, roomId, StringComparison.Ordinal))
                     .Select(p => p.Key)
                     .OrderBy(k => k, StringComparer.Ordinal)
                     .ToList();

        /// <summary>Everyone else in the same room as the given person.</summary>
        public IReadOnlyList<string> WithMe(string characterId)
            => InRoom(RoomOf(characterId))
                .Where(id => !string.Equals(id, characterId, StringComparison.Ordinal))
                .ToList();

        /// <summary>Everyone close enough to hear something in the given room without seeing it.</summary>
        public IReadOnlyList<string> WithinEarshotOf(string roomId)
            => House.Audible(roomId).SelectMany(InRoom).OrderBy(k => k, StringComparer.Ordinal).ToList();

        public void SetHunger(string characterId, double level)
            => _hunger[characterId] = Accumulate.Clamp01(level);

        public double HungerOf(string characterId)
            => characterId != null && _hunger.TryGetValue(characterId, out var h) ? h : 0.0;

        /// <summary>Time passing, and everyone getting hungrier by their own metabolism.</summary>
        public void Tick(IReadOnlyDictionary<string, double> ratePerMinute)
        {
            Minute++;
            foreach (var id in Inhabitants)
            {
                ratePerMinute.TryGetValue(id, out var rate);
                _hunger[id] = Accumulate.Clamp01(HungerOf(id) + rate);
            }
        }

        /// <summary>Takes a portion if there is one. Returns false when the pantry is bare.</summary>
        public bool TakePortion()
        {
            if (Portions <= 0) return false;
            Portions--;
            return true;
        }

        public void MarkSearched(string roomId)
        {
            if (roomId != null) _searched.Add(roomId);
        }

        public bool WasSearched(string roomId) => roomId != null && _searched.Contains(roomId);

        public override string ToString()
            => "minute " + Minute + ", " + Portions + " portions, " +
               string.Join(", ", Inhabitants.Select(id => id + " in " + RoomOf(id)));
    }
}
