using System.Collections.Generic;

namespace Fallow.Core.Rules
{
    /// <summary>
    /// A want this moment can raise, and how strongly, for whoever it fits.
    ///
    /// The urgency comes almost entirely from the scalers, which is deliberate:
    /// the circumstances say what there is to want, and the person decides how
    /// badly they want it.
    /// </summary>
    public sealed class MotivationRule
    {
        public string Id { get; set; }
        public string Note { get; set; }
        public SituationCondition When { get; set; } = new SituationCondition();
        public string Motive { get; set; }

        /// <summary>Whether this want is about the situation or about a particular person.</summary>
        public string Scope { get; set; } = MotiveScope.Situation;

        public double BaseUrgency { get; set; }
        public IReadOnlyList<Scaler> ScaledBy { get; set; } = new List<Scaler>();
    }

    /// <summary>
    /// A way of serving a want. One motive usually has several, and one action
    /// usually serves several motives; that crossing is what keeps an action
    /// from becoming another name for a feeling.
    ///
    /// Fit says how well this action serves that want. It does not say how much
    /// the person wants it, which lives on the motive.
    /// </summary>
    public sealed class ProposalRule
    {
        public string Id { get; set; }
        public string Note { get; set; }
        public SituationCondition When { get; set; } = new SituationCondition();
        public string Motive { get; set; }
        public string Action { get; set; }
        public string Targeting { get; set; } = Rules.Targeting.None;

        /// <summary>The kind of room aimed for, when the targeting needs one.</summary>
        public string RoomTag { get; set; }

        public double Fit { get; set; } = 1.0;
    }

    /// <summary>
    /// A reason to hesitate.
    ///
    /// Costs are what make two people with the same want do different things.
    /// Taking the last of the food is the same act for everybody, and it is not
    /// the same price for everybody.
    /// </summary>
    public sealed class CostRule
    {
        public string Id { get; set; }
        public string Note { get; set; }
        public SituationCondition When { get; set; } = new SituationCondition();
        public string Action { get; set; }
        public double Base { get; set; }
        public IReadOnlyList<Scaler> ScaledBy { get; set; } = new List<Scaler>();
    }

    /// <summary>
    /// How the traits and values named in a motivation rule enter the want it
    /// raises. Added in S1.5 to test whether they are better as dispositions.
    /// </summary>
    public static class DispositionMode
    {
        /// <summary>They add to the want like any other reason, whatever is happening: a want that is always on. Before S1.5, the only way.</summary>
        public const string Standing = "standing";

        /// <summary>They scale how strongly the person responds to what the rule responds to, and raise nothing on their own.</summary>
        public const string Respond = "respond";

        /// <summary>Diagnostic only: they add as in Standing, but only once the rule has something else behind it.</summary>
        public const string Gated = "gated";

        public static readonly IReadOnlyList<string> All = new[] { Standing, Respond, Gated };
    }

    /// <summary>
    /// The few numbers that govern deciding and doing, kept as data so that
    /// tuning them is an edit rather than a rebuild.
    /// </summary>
    public sealed class DecisionDynamics
    {
        /// <summary>
        /// How close two scores must be before the difference stops being a
        /// preference and starts being noise in a person own weighing. Inside
        /// this band the choice is genuinely open and the seed settles it.
        /// Outside it, nothing random happens at all.
        /// </summary>
        public double AmbiguityBand { get; set; } = 0.08;

        /// <summary>
        /// How hard something has to land before it stops you doing what you
        /// were doing. Below this, people finish what they started.
        /// </summary>
        public double InterruptIntensity { get; set; } = 0.45;

        /// <summary>How visible a feeling must be before somebody in the room can read it.</summary>
        public double VisibleDistress { get; set; } = 0.30;

        /// <summary>Hunger gained each minute, before a person own metabolism.</summary>
        public double HungerPerMinute { get; set; } = 0.004;

        /// <summary>How much hunger one portion takes away.</summary>
        public double PortionRelief { get; set; } = 0.45;

        /// <summary>At or below this many portions, the pantry is visibly bad news.</summary>
        public int LowPortions { get; set; } = 1;

        /// <summary>Which feelings show on a person at all. Being pleased is not distress.</summary>
        public IReadOnlyList<string> DistressShows { get; set; } = new List<string>();

        /// <summary>Which feelings being sat with actually settles.</summary>
        public IReadOnlyList<string> ComfortSettles { get; set; } = new List<string>();

        /// <summary>How much of those is left afterwards.</summary>
        public double ComfortSettling { get; set; } = 0.5;

        /// <summary>
        /// Where urgency stops being linear. Chosen from data, not tuned: across
        /// 32,123 wants raised in 50 mornings, measured after the fading fix, 90% of the wants that were not
        /// pinned at the ceiling sat at or below 0.85. Below the knee nothing
        /// changes. The default switches it off, so a rule set that does not ask
        /// for it behaves as before.
        /// </summary>
        public double UrgencyKnee { get; set; } = 1.0;

        /// <summary>Minutes after which a memory presses half as hard as it did.</summary>
        public double RecallHalfLife { get; set; } = 20.0;

        /// <summary>
        /// How long watching somebody goes on telling you anything. Look again
        /// straight away and you learn nothing you did not already have.
        /// </summary>
        public int WatchingGoesStaleAfter { get; set; } = 15;

        /// <summary>Minutes each kind of action occupies. Movement is per room crossed.</summary>
        public IReadOnlyDictionary<string, int> ActionMinutes { get; set; } = new Dictionary<string, int>();

        /// <summary>
        /// How traits and values enter a want (see DispositionMode). The default is
        /// how every slice before S1.5 raised wants. Added in S1.5 as a diagnostic
        /// switch, not as a decision: the shipped rules do not set it.
        /// </summary>
        public string Dispositions { get; set; } = DispositionMode.Standing;

        public int MinutesFor(string actionName, int fallback = 3)
            => actionName != null && ActionMinutes.TryGetValue(actionName, out var m) ? m : fallback;
    }
}
