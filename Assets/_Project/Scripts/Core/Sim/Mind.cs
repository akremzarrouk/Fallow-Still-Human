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

        public Profile Profile { get; }
        public BeliefStore Beliefs { get; } = new BeliefStore();
        public Ledger Ledger { get; } = new Ledger();
        public EmotionSet Emotions { get; } = new EmotionSet();
        public IReadOnlyList<Experience> Experiences => _experiences;

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
