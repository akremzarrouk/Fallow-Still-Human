namespace Fallow.Core.Model
{
    /// <summary>
    /// How one person stands to another in the family, derived from data rather
    /// than authored. Rules read relations so that they stay general: a rule may
    /// say "a junior corrected me", never "my brother corrected me".
    /// </summary>
    public enum Relation
    {
        Self,
        Junior,
        Peer,
        Senior
    }
}
