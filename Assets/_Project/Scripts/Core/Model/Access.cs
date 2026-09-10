namespace Fallow.Core.Model
{
    /// <summary>
    /// How much of an event reached a person. Access is the first gate in the
    /// pipeline and the one that makes knowledge local: a character who was not
    /// there learns nothing, and a character who only heard it learns less.
    /// </summary>
    public enum Access
    {
        None,
        Overheard,
        Witnessed
    }
}
