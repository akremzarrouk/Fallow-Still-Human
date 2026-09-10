using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Model
{
    /// <summary>One specific thing a person did, which someone else has not forgotten.</summary>
    public sealed class LedgerRecord
    {
        public string AboutId { get; }
        public string Entry { get; }
        public double Weight { get; }
        public int TraceId { get; }
        public string EventId { get; }

        public LedgerRecord(string aboutId, string entry, double weight, int traceId, string eventId)
        {
            AboutId = aboutId;
            Entry = entry;
            Weight = weight;
            TraceId = traceId;
            EventId = eventId;
        }

        public override string ToString() => $"{Entry} ({AboutId}, {Weight:0.00}, {EventId})";
    }

    /// <summary>
    /// What one person holds against, and holds to the credit of, everyone else.
    ///
    /// The list is the relationship. Strength is only a summary computed from it,
    /// never stored and never a source of anything on its own, so a character can
    /// always name the thing rather than only feel the total.
    /// </summary>
    public sealed class Ledger
    {
        readonly List<LedgerRecord> _records = new List<LedgerRecord>();

        public IReadOnlyList<LedgerRecord> All => _records;

        public void Add(string aboutId, string entry, double weight, int traceId, string eventId)
        {
            if (aboutId == null || entry == null) return;
            _records.Add(new LedgerRecord(aboutId, entry, weight, traceId, eventId));
        }

        public IReadOnlyList<LedgerRecord> About(string aboutId)
            => _records.Where(r => string.Equals(r.AboutId, aboutId, StringComparison.Ordinal)).ToList();

        /// <summary>
        /// How heavily one kind of memory about one person weighs, derived on
        /// demand from the entries themselves. A tenth kindness counts for less
        /// than the first, which is why this saturates rather than sums.
        /// </summary>
        public double Strength(string aboutId, string entry)
        {
            var total = 0.0;
            foreach (var r in _records)
            {
                if (!string.Equals(r.AboutId, aboutId, StringComparison.Ordinal)) continue;
                if (!string.Equals(r.Entry, entry, StringComparison.Ordinal)) continue;
                total = Accumulate.Toward(total, r.Weight);
            }
            return total;
        }

        /// <summary>Every kind of memory this person holds about someone, with its strength.</summary>
        public IReadOnlyDictionary<string, double> SummaryAbout(string aboutId)
        {
            var kinds = About(aboutId).Select(r => r.Entry).Distinct(StringComparer.Ordinal);
            return kinds.ToDictionary(k => k, k => Strength(aboutId, k), StringComparer.Ordinal);
        }
    }
}
