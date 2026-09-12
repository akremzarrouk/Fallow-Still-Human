using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// One version of what actually happened in the night.
    ///
    /// A variant is not a puzzle with a solution. It is a controlled condition:
    /// the same four people, the same morning, one difference in what is true
    /// and in who carries it. Whether anybody ever works it out is not what is
    /// being measured.
    ///
    /// The night events reach the culprit through the ordinary pipeline, so
    /// their guilt is appraised rather than authored. Nobody is handed a feeling.
    /// </summary>
    public sealed class MorningVariant
    {
        public string Id { get; }
        public string Note { get; }
        public IReadOnlyList<WorldEvent> NightEvents { get; }

        public MorningVariant(string id, string note, IReadOnlyList<WorldEvent> nightEvents)
        {
            Id = id;
            Note = note;
            NightEvents = nightEvents ?? new List<WorldEvent>();
        }

        public override string ToString() => Id;
    }

    /// <summary>
    /// The morning itself: the house, where everybody starts, how hungry they
    /// are, the one event that sets it going, and the versions of the night it
    /// can follow.
    ///
    /// Exactly one thing here is scripted, and that is the discovery. Everything
    /// after it is decided by the people.
    /// </summary>
    public sealed class MorningScenario
    {
        public string Id { get; }
        public string Description { get; }
        public int Day { get; }
        public int Minutes { get; }
        public RoomGraph House { get; }
        public int Portions { get; }
        public IReadOnlyDictionary<string, string> StartRooms { get; }
        public IReadOnlyDictionary<string, double> StartHunger { get; }
        public WorldEvent Opening { get; }
        public IReadOnlyList<MorningVariant> Variants { get; }

        /// <summary>
        /// Conditions kept out of every batch and every design pass, so that a
        /// prediction about them can be written before anybody has seen them run.
        /// Reachable by name, never by iterating the ordinary list.
        /// </summary>
        public IReadOnlyList<MorningVariant> HeldOutVariants { get; }

        public MorningScenario(
            string id, string description, int day, int minutes, RoomGraph house, int portions,
            IReadOnlyDictionary<string, string> startRooms,
            IReadOnlyDictionary<string, double> startHunger,
            WorldEvent opening, IReadOnlyList<MorningVariant> variants,
            IReadOnlyList<MorningVariant> heldOutVariants = null)
        {
            HeldOutVariants = heldOutVariants ?? new List<MorningVariant>();
            Id = id;
            Description = description;
            Day = day;
            Minutes = minutes;
            House = house;
            Portions = portions;
            StartRooms = startRooms ?? new Dictionary<string, string>();
            StartHunger = startHunger ?? new Dictionary<string, double>();
            Opening = opening;
            Variants = variants ?? new List<MorningVariant>();
        }

        public MorningVariant Variant(string id)
        {
            foreach (var v in Variants)
                if (v.Id == id) return v;
            foreach (var v in HeldOutVariants)
                if (v.Id == id) return v;
            return null;
        }
    }
}
