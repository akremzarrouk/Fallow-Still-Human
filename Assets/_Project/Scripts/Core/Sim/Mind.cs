using System.Collections.Generic;
using Fallow.Core.Model;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// One person's inside. Everything a character knows, remembers and feels
    /// lives here and nowhere else; there is no shared store any mind can read.
    /// The world holds what happened, and each mind holds its own version.
    ///
    /// A Mind has no body and knows nothing about Unity, so the whole social
    /// simulation runs headless and can be batch-tested.
    /// </summary>
    public sealed class Mind
    {
        readonly List<Experience> _experiences = new List<Experience>();
        readonly List<PursuitOutcome> _outcomes = new List<PursuitOutcome>();

        public Profile Profile { get; }
        public BeliefStore Beliefs { get; } = new BeliefStore();
        public Ledger Ledger { get; } = new Ledger();
        public EmotionSet Emotions { get; } = new EmotionSet();
        public IReadOnlyList<Experience> Experiences => _experiences;

        /// <summary>What came of acting on their wants, oldest first. See PursuitOutcome.</summary>
        public IReadOnlyList<PursuitOutcome> Outcomes => _outcomes;

        /// <summary>
        /// Keeps what came of acting on a want. Written by the world as it
        /// resolves what somebody did; public so that an experiment can hand a
        /// mind a record it would otherwise have to run a morning to get.
        /// </summary>
        public void Record(PursuitOutcome outcome) => _outcomes.Add(outcome);

        /// <summary>The most recent thing done about a need, or null if nothing ever was.</summary>
        public PursuitOutcome LatestOutcomeFor(string need)
        {
            for (var i = _outcomes.Count - 1; i >= 0; i--)
                if (string.Equals(_outcomes[i].Need, need, System.StringComparison.Ordinal)) return _outcomes[i];
            return null;
        }

        public Mind(Profile profile)
        {
            Profile = profile;
            foreach (var seed in profile.InitialBeliefs) Beliefs.Seed(seed);
        }

        public string Id => Profile.Id;

        internal void Remember(Experience experience) => _experiences.Add(experience);

        public override string ToString() => $"Mind of {Profile}";
    }
}
