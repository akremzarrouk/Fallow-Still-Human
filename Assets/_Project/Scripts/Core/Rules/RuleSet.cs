using System.Collections.Generic;

namespace Fallow.Core.Rules
{
    /// <summary>A reading an event may carry, and how strongly, for whoever it fits.</summary>
    public sealed class InterpretationRule
    {
        public string Id { get; set; }
        public string Note { get; set; }
        public Condition When { get; set; } = new Condition();
        public string Label { get; set; }
        public double BaseWeight { get; set; }
        public IReadOnlyList<Scaler> ScaledBy { get; set; } = new List<Scaler>();
    }

    /// <summary>A belief that shifts because of what an event turned out to mean.</summary>
    public sealed class BeliefNudgeRule
    {
        public string Id { get; set; }
        public string Note { get; set; }
        public Condition When { get; set; } = new Condition();
        public string Predicate { get; set; }
        public IReadOnlyList<string> Args { get; set; } = new List<string>();
        public double Delta { get; set; }
        public IReadOnlyList<Scaler> ScaledBy { get; set; } = new List<Scaler>();
    }

    /// <summary>
    /// A feeling that follows from a reading, and the concern it arose from.
    /// The concern is required: a feeling that cannot say which of your
    /// commitments was touched explains nothing.
    /// </summary>
    public sealed class AppraisalRule
    {
        public string Id { get; set; }
        public string Note { get; set; }
        public Condition When { get; set; } = new Condition();
        public string Emotion { get; set; }

        /// <summary>Who the feeling is about: a token such as $actor, or null for the situation.</summary>
        public string Target { get; set; }

        public string Concern { get; set; }
        public double BaseIntensity { get; set; }
        public IReadOnlyList<Scaler> ScaledBy { get; set; } = new List<Scaler>();
    }

    /// <summary>
    /// The few numbers that govern how memory and feeling move over time, kept
    /// as data so tuning them is an edit rather than a rebuild.
    /// </summary>
    public sealed class Dynamics
    {
        /// <summary>How much of a feeling survives to the next event, before temperament.</summary>
        public double EmotionDecayBase { get; set; } = 0.60;

        /// <summary>How much an anxious temperament slows that fading.</summary>
        public double EmotionDecayAnxietyResistance { get; set; } = 0.25;

        /// <summary>Below this, a feeling is no longer felt at all.</summary>
        public double EmotionFloor { get; set; } = 0.05;

        /// <summary>How sure you are of something you only heard through a wall.</summary>
        public double OverheardConfidence { get; set; } = 0.60;

        /// <summary>
        /// How much of an event sticks even when it stirred nothing. Feeling
        /// carries a memory the rest of the way, so this is the floor of the
        /// scale rather than a weight.
        /// </summary>
        public double SalienceBase { get; set; } = 0.15;

        /// <summary>How much less an overheard event stirs than a witnessed one.</summary>
        public double OverheardIntensityScale { get; set; } = 0.75;
    }

    public sealed class RuleSet
    {
        public IReadOnlyList<InterpretationRule> Interpretation { get; set; } = new List<InterpretationRule>();
        public IReadOnlyList<BeliefNudgeRule> BeliefNudges { get; set; } = new List<BeliefNudgeRule>();
        public IReadOnlyList<AppraisalRule> Appraisal { get; set; } = new List<AppraisalRule>();
        public Dynamics Dynamics { get; set; } = new Dynamics();

        // Deciding what to do, loaded from a separate file so that how a person
        // reads the world and what they do about it can be changed apart.

        public IReadOnlyList<MotivationRule> Motivation { get; set; } = new List<MotivationRule>();
        public IReadOnlyList<ProposalRule> Proposals { get; set; } = new List<ProposalRule>();
        public IReadOnlyList<CostRule> Costs { get; set; } = new List<CostRule>();
        public DecisionDynamics Deciding { get; set; } = new DecisionDynamics();

        /// <summary>Folds a decision rule file into this one, leaving the event rules alone.</summary>
        public RuleSet With(RuleSet decisions)
        {
            if (decisions == null) return this;
            Motivation = decisions.Motivation;
            Proposals = decisions.Proposals;
            Costs = decisions.Costs;
            Deciding = decisions.Deciding;
            return this;
        }
    }
}
