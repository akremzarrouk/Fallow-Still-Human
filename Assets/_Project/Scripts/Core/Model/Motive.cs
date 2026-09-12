using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Rules;

namespace Fallow.Core.Model
{
    /// <summary>
    /// Something a person currently wants, and how badly.
    ///
    /// A motive is a state of affairs rather than an action: wanting not to be
    /// looked at is one motive, and leaving the room, going to your own room and
    /// keeping your back turned are three ways of serving it. Keeping those
    /// apart is what stops the model collapsing into a table of feelings mapped
    /// to behaviours.
    ///
    /// The terms are kept because urgency on its own explains nothing. A motive
    /// must be able to say which feeling, which value and which memory raised it.
    /// </summary>
    public sealed class Motive
    {
        public string Name { get; }

        /// <summary>Who it is about, when it is about somebody. Null otherwise.</summary>
        public string TargetId { get; }

        public double Urgency { get; internal set; }
        public IReadOnlyList<string> RuleIds { get; }
        public IReadOnlyList<ScalerTerm> Terms { get; }
        public int TraceId { get; internal set; }

        public Motive(
            string name, string targetId, double urgency,
            IReadOnlyList<string> ruleIds, IReadOnlyList<ScalerTerm> terms)
        {
            Name = name;
            TargetId = targetId;
            Urgency = urgency;
            RuleIds = ruleIds ?? new List<string>();
            Terms = terms ?? new List<ScalerTerm>();
        }

        public string Key => TargetId == null ? Name : Name + ":" + TargetId;

        /// <summary>The reasons behind this want, in words, strongest first.</summary>
        public string Because
            => Terms.Count == 0
                ? "nothing in particular"
                : string.Join("; ", Terms.Where(t => t.Amount != 0.0)
                    .OrderByDescending(t => t.Amount)
                    .Select(t => t.ToString()));

        public override string ToString()
            => (TargetId == null ? Name : Name + " (" + TargetId + ")") + " " + Urgency.ToString("0.00");
    }
}
