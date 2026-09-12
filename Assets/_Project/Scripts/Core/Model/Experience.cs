namespace Fallow.Core.Model
{
    /// <summary>How someone came to know a thing.</summary>
    public enum ExperienceSource
    {
        /// <summary>They did it, so they know what they meant by it.</summary>
        Self,

        /// <summary>They were there and saw it.</summary>
        Witnessed,

        /// <summary>They heard it without seeing it, and hold it less surely.</summary>
        Overheard
    }

    /// <summary>
    /// One person's record of one event: not what happened, but what they made
    /// of it. Two people in the same room keep different records of the same
    /// minute, and neither can consult the other's.
    /// </summary>
    public sealed class Experience
    {
        public string EventId { get; }
        public int Day { get; }
        public int Order { get; }
        public string ActorId { get; }

        /// <summary>Who it was aimed at, as far as this person could tell.</summary>
        public string TargetId { get; }

        /// <summary>What it was about. A memory that cannot say what it concerned cannot be recalled by subject.</summary>
        public string Topic { get; }

        /// <summary>When in the day it happened, or -1 when only the order is known.</summary>
        public int Minute { get; }

        /// <summary>What it meant to this person.</summary>
        public string Meaning { get; }

        /// <summary>True when the meaning is their own intention rather than a reading of someone else.</summary>
        public bool FromOwnIntent { get; }

        public Access Access { get; }

        /// <summary>How sure they are that it happened the way they hold it.</summary>
        public double Confidence { get; }

        /// <summary>How much of a mark it left, and so how readily it comes back.</summary>
        public double Salience { get; }

        /// <summary>The strongest feeling this event stirred, if any.</summary>
        public string DominantEmotion { get; }

        public int TraceId { get; }
        public string Summary { get; }

        public Experience(
            string eventId, int day, int order, string actorId,
            string meaning, bool fromOwnIntent, Access access,
            double confidence, double salience, string dominantEmotion,
            int traceId, string summary,
            string targetId = null, string topic = null, int minute = -1)
        {
            Minute = minute;
            EventId = eventId;
            Day = day;
            Order = order;
            ActorId = actorId;
            TargetId = targetId;
            Topic = topic;
            Meaning = meaning;
            FromOwnIntent = fromOwnIntent;
            Access = access;
            Confidence = confidence;
            Salience = salience;
            DominantEmotion = dominantEmotion;
            TraceId = traceId;
            Summary = summary;
        }

        public ExperienceSource Source
            => FromOwnIntent ? ExperienceSource.Self
             : Access == Access.Overheard ? ExperienceSource.Overheard
             : ExperienceSource.Witnessed;

        public override string ToString()
            => $"{EventId}: {Meaning} ({Source}, confidence {Confidence:0.00}, salience {Salience:0.00})";
    }
}
