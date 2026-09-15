using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Fallow.Core.Tracing
{
    /// <summary>Which step of the pipeline a trace record belongs to.</summary>
    public enum TraceKind
    {
        Event,
        Access,
        Interpretation,
        Experience,
        BeliefChange,
        LedgerEntry,
        Appraisal,
        Emotion,

        /// <summary>Something the person came to want, and what raised it.</summary>
        Motive,

        /// <summary>Weighing what to do, and what the alternatives scored.</summary>
        Deliberation,

        /// <summary>What they settled on doing.</summary>
        Action,

        /// <summary>What that changed about the house.</summary>
        Consequence,

        /// <summary>What came of acting on a want, judged by what happened. Added in S1.3.</summary>
        Outcome
    }

    public sealed class TraceRecord
    {
        public int Id { get; }
        public TraceKind Kind { get; }

        /// <summary>Whose step this was. Null for the world event itself.</summary>
        public string CharacterId { get; }

        public string EventId { get; }
        public string Summary { get; }
        public IReadOnlyList<int> ParentIds { get; }
        public IReadOnlyDictionary<string, string> Data { get; }

        public TraceRecord(
            int id, TraceKind kind, string characterId, string eventId, string summary,
            IReadOnlyList<int> parentIds, IReadOnlyDictionary<string, string> data)
        {
            Id = id;
            Kind = kind;
            CharacterId = characterId;
            EventId = eventId;
            Summary = summary;
            ParentIds = parentIds ?? new List<int>();
            Data = data ?? new Dictionary<string, string>();
        }

        public override string ToString()
            => $"#{Id} {Kind}{(CharacterId == null ? "" : " " + CharacterId)}: {Summary}";
    }

    /// <summary>
    /// The record of why. Every step of the pipeline appends here with a link to
    /// the step it came from, so any feeling or belief can be walked back to the
    /// thing that happened.
    ///
    /// This is a development instrument, not a game system. Nothing a player sees
    /// is ever drawn from it.
    /// </summary>
    public sealed class TraceLog
    {
        readonly List<TraceRecord> _records = new List<TraceRecord>();

        public IReadOnlyList<TraceRecord> All => _records;
        public int Count => _records.Count;

        public int Add(
            TraceKind kind,
            string characterId,
            string eventId,
            string summary,
            IEnumerable<int> parents = null,
            IReadOnlyDictionary<string, string> data = null)
        {
            var id = _records.Count;
            _records.Add(new TraceRecord(
                id, kind, characterId, eventId, summary,
                parents?.ToList() ?? new List<int>(),
                data));
            return id;
        }

        public TraceRecord Get(int id)
            => id >= 0 && id < _records.Count ? _records[id] : null;

        public IReadOnlyList<TraceRecord> For(string characterId)
            => _records.Where(r => string.Equals(r.CharacterId, characterId, StringComparison.Ordinal)).ToList();

        public IReadOnlyList<TraceRecord> For(string characterId, string eventId)
            => _records.Where(r =>
                string.Equals(r.CharacterId, characterId, StringComparison.Ordinal) &&
                string.Equals(r.EventId, eventId, StringComparison.Ordinal)).ToList();

        public IReadOnlyList<TraceRecord> ForEvent(string eventId)
            => _records.Where(r => string.Equals(r.EventId, eventId, StringComparison.Ordinal)).ToList();

        /// <summary>
        /// The record and everything it rests on, nearest reason first, each
        /// listed once however many paths lead to it.
        /// </summary>
        public IReadOnlyList<TraceRecord> Chain(int id)
        {
            var seen = new HashSet<int>();
            var chain = new List<TraceRecord>();
            Walk(id, seen, chain);
            return chain;
        }

        void Walk(int id, HashSet<int> seen, List<TraceRecord> chain)
        {
            if (!seen.Add(id)) return;
            var record = Get(id);
            if (record == null) return;
            chain.Add(record);
            foreach (var parent in record.ParentIds) Walk(parent, seen, chain);
        }

        /// <summary>
        /// The chain in words, as a tree: each record indented one step under
        /// the record it is a reason for. A record reached twice is written out
        /// the first time and referred to after that, so a shared cause is never
        /// repeated and two separate reasons are never shown as one causing the
        /// other.
        /// </summary>
        public string Why(int id)
        {
            var sb = new StringBuilder();
            Print(id, 0, new HashSet<int>(), sb);
            return sb.ToString();
        }

        void Print(int id, int depth, HashSet<int> shown, StringBuilder sb)
        {
            var r = Get(id);
            if (r == null) return;

            if (depth > 0) sb.Append(' ', depth * 2).Append("because ");

            if (!shown.Add(id))
            {
                sb.Append('#').Append(id).Append(' ').Append(r.Kind).AppendLine(", shown above");
                return;
            }

            sb.Append(r.Kind);
            if (r.CharacterId != null) sb.Append(" [").Append(r.CharacterId).Append(']');
            sb.Append(": ").Append(r.Summary);
            if (r.Data.Count > 0)
            {
                sb.Append("  {");
                sb.Append(string.Join(", ", r.Data.Select(kv => kv.Key + "=" + kv.Value)));
                sb.Append('}');
            }
            sb.AppendLine();

            foreach (var parent in r.ParentIds) Print(parent, depth + 1, shown, sb);
        }
    }
}
