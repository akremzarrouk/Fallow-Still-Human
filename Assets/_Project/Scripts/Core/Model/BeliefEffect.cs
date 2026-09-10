using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// A belief an event shifts directly, authored on the event rather than
    /// derived from a rule. It exists for the things a slice cannot yet infer,
    /// such as watching a prediction come true, and it is filtered by access
    /// exactly like every other consequence: only someone who was there gets it.
    /// </summary>
    public sealed class BeliefEffect
    {
        public string HolderId { get; }
        public string Predicate { get; }
        public IReadOnlyList<string> Args { get; }
        public double Delta { get; }

        public BeliefEffect(string holderId, string predicate, IReadOnlyList<string> args, double delta)
        {
            HolderId = holderId;
            Predicate = predicate;
            Args = args ?? new List<string>();
            Delta = delta;
        }

        public string Key => BeliefKey.Of(Predicate, Args);

        public override string ToString() => $"{HolderId}: {Key} {Delta:+0.00;-0.00}";
    }
}
