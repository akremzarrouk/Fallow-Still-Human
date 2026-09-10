namespace Fallow.Core.Model
{
    /// <summary>
    /// A specific thing one person will remember another for. Authored on the
    /// event in this slice; derived from appraisal in a later one. Either way it
    /// only lands on someone who had access to the event.
    /// </summary>
    public sealed class LedgerEffect
    {
        public string HolderId { get; }
        public string AboutId { get; }
        public string Entry { get; }
        public double Weight { get; }

        public LedgerEffect(string holderId, string aboutId, string entry, double weight)
        {
            HolderId = holderId;
            AboutId = aboutId;
            Entry = entry;
            Weight = weight;
        }

        public override string ToString() => $"{HolderId} remembers {AboutId}: {Entry} ({Weight:0.00})";
    }
}
