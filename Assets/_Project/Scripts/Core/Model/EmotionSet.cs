using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Model
{
    /// <summary>
    /// A feeling someone is currently having, with the concern it touched and
    /// the experiences that caused it. An emotion that cannot say what it is
    /// about is not usable evidence for anything, so both are required.
    /// </summary>
    public sealed class EmotionInstance
    {
        readonly List<int> _causes = new List<int>();

        public string Type { get; }

        /// <summary>Who it is about. Null when it is about the situation rather than a person.</summary>
        public string TargetId { get; }

        /// <summary>The value or expectation this feeling arose from.</summary>
        public string Concern { get; internal set; }

        public double Intensity { get; internal set; }
        public string LastEventId { get; internal set; }
        public IReadOnlyList<int> Causes => _causes;

        public EmotionInstance(string type, string targetId, string concern, double intensity)
        {
            Type = type;
            TargetId = targetId;
            Concern = concern;
            Intensity = intensity;
        }

        internal void AddCause(int traceId)
        {
            if (!_causes.Contains(traceId)) _causes.Add(traceId);
        }

        public override string ToString()
            => TargetId == null
                ? $"{Type} {Intensity:0.00} ({Concern})"
                : $"{Type} {Intensity:0.00} toward {TargetId} ({Concern})";
    }

    /// <summary>
    /// What a person is feeling right now. Feeling the same thing again deepens
    /// it instead of stacking a second copy, and everything fades between events,
    /// which is why the backstory leaves memories and grudges behind rather than
    /// a character still visibly angry three days later.
    /// </summary>
    public sealed class EmotionSet
    {
        readonly Dictionary<string, EmotionInstance> _live = new Dictionary<string, EmotionInstance>(StringComparer.Ordinal);

        static string KeyOf(string type, string targetId) => type + "|" + (targetId ?? "");

        public IReadOnlyList<EmotionInstance> Live
            => _live.Values
                .OrderByDescending(e => e.Intensity)
                .ThenBy(e => e.Type, StringComparer.Ordinal)
                .ToList();

        public void Add(string type, string targetId, string concern, double intensity, int traceId, string eventId)
        {
            if (type == null || intensity <= 0.0) return;

            var key = KeyOf(type, targetId);
            if (!_live.TryGetValue(key, out var inst))
            {
                inst = new EmotionInstance(type, targetId, concern, 0.0);
                _live[key] = inst;
            }

            inst.Intensity = Accumulate.Toward(inst.Intensity, intensity);
            inst.Concern = concern ?? inst.Concern;
            inst.LastEventId = eventId;
            inst.AddCause(traceId);
        }

        public double Intensity(string type, string targetId = null)
            => _live.TryGetValue(KeyOf(type, targetId), out var e) ? e.Intensity : 0.0;

        /// <summary>Time passing. Anything left below the floor stops being felt.</summary>
        public void Decay(double factor, double floor)
        {
            var gone = new List<string>();
            foreach (var pair in _live)
            {
                pair.Value.Intensity *= factor;
                if (pair.Value.Intensity < floor) gone.Add(pair.Key);
            }
            foreach (var key in gone) _live.Remove(key);
        }

        /// <summary>
        /// The feeling with the upper hand. Ties break by name rather than by
        /// insertion order so that the same run always reads the same way.
        /// </summary>
        public EmotionInstance Dominant => Live.Count == 0 ? null : Live[0];
    }
}
