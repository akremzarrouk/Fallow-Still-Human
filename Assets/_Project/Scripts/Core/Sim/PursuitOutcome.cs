using System;
using System.Globalization;

namespace Fallow.Core.Sim
{
    /// <summary>What came of acting on a want, judged by what actually happened.</summary>
    public enum OutcomeKind
    {
        /// <summary>The act did what the want was for, completely: the need it reads is gone.</summary>
        Satisfied,

        /// <summary>The act did some of it: the need is lower, and some remains.</summary>
        PartlySatisfied,

        /// <summary>The act could not do anything: the world did not allow it.</summary>
        Blocked,

        /// <summary>The act happened, or was given up, and the need is where it was.</summary>
        Unresolved,

        /// <summary>By the time it came to it, the want was no longer there to serve.</summary>
        NoLongerRelevant
    }

    /// <summary>
    /// One person's record of what came of acting on one of their wants.
    ///
    /// Added in S1.3. Wants are never stored: every want is raised again from
    /// the person's state each time they decide, so a want can only change
    /// because something it reads has changed. An outcome is not a second copy
    /// of the want and it moves no number. It is the record of why what the
    /// want reads is where it is, so that a want which fell because somebody ate
    /// can be walked back to the eating, and a want that did not fall because
    /// the food was gone can be walked back to finding it gone.
    ///
    /// Written by the world when an act that touches a need is resolved, and when
    /// an intention carried for such a want is given up on arrival. It is the
    /// person's own: nobody else's mind can read it.
    /// </summary>
    public sealed class PursuitOutcome
    {
        public string MotiveKey { get; }
        public string MotiveName { get; }

        /// <summary>What was done about it.</summary>
        public string Act { get; }

        /// <summary>The need the want reads, and where it stood before and after.</summary>
        public string Need { get; }
        public double Before { get; }
        public double After { get; }

        public OutcomeKind Kind { get; }
        public int Minute { get; }

        /// <summary>The event the consequence was, when it was one anybody could perceive. Null for an intention given up.</summary>
        public string EventId { get; }

        /// <summary>For an intention given up, why.</summary>
        public string Because { get; }

        /// <summary>Where the record of this outcome sits. Settable so that an experiment can hand one in.</summary>
        public int TraceId { get; set; }

        public PursuitOutcome(
            string motiveKey, string motiveName, string act, string need, double before, double after,
            OutcomeKind kind, int minute, string eventId, string because = null)
        {
            MotiveKey = motiveKey;
            MotiveName = motiveName;
            Act = act;
            Need = need;
            Before = before;
            After = after;
            Kind = kind;
            Minute = minute;
            EventId = eventId;
            Because = because;
        }

        public override string ToString()
        {
            var inv = CultureInfo.InvariantCulture;
            var level = Before == After
                ? Need + " " + After.ToString("0.00", inv)
                : Need + " " + Before.ToString("0.00", inv) + " -> " + After.ToString("0.00", inv);
            return Words(Kind) + " by " + Act + " at minute " + Minute + (Because == null ? "" : ", " + Because) + ", " + level;
        }

        public static string Words(OutcomeKind kind)
        {
            switch (kind)
            {
                case OutcomeKind.Satisfied: return "satisfied";
                case OutcomeKind.PartlySatisfied: return "partly satisfied";
                case OutcomeKind.Blocked: return "blocked";
                case OutcomeKind.Unresolved: return "unresolved";
                case OutcomeKind.NoLongerRelevant: return "no longer relevant";
                default: return kind.ToString();
            }
        }
    }

    /// <summary>How an outcome is judged. Nothing here is a threshold on a person: only on what happened.</summary>
    public static class Outcomes
    {
        /// <summary>
        /// From an act's consequence on the need a want reads. The only level
        /// consulted is the bottom of the scale, where there is nothing left to
        /// satisfy.
        /// </summary>
        public static OutcomeKind OfConsequence(bool couldHappen, double before, double after)
        {
            if (!couldHappen) return OutcomeKind.Blocked;
            if (after < before) return after <= 0.0 ? OutcomeKind.Satisfied : OutcomeKind.PartlySatisfied;
            return OutcomeKind.Unresolved;
        }

        /// <summary>From an intention given up on arrival. Null when it was not given up.</summary>
        public static OutcomeKind? OfLapse(string commitment)
        {
            switch (commitment)
            {
                case Commitment.Impossible: return OutcomeKind.Blocked;
                case Commitment.NotWorthIt: return OutcomeKind.Unresolved;
                case Commitment.NoLongerWanted: return OutcomeKind.NoLongerRelevant;
                default: return null;
            }
        }
    }
}
