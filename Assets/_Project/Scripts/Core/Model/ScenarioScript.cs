using System.Collections.Generic;

namespace Fallow.Core.Model
{
    /// <summary>
    /// The ordered list of things that happen, and to whom. Backstory and live
    /// events sit in the same list on purpose: a character's history reaches
    /// them through perception exactly as the present does, so there is no
    /// second path by which someone can come to know something.
    /// </summary>
    public sealed class ScenarioScript
    {
        public string Id { get; }
        public string Description { get; }
        public IReadOnlyList<string> CharacterIds { get; }
        public IReadOnlyList<WorldEvent> Events { get; }

        public ScenarioScript(
            string id,
            string description,
            IReadOnlyList<string> characterIds,
            IReadOnlyList<WorldEvent> events)
        {
            Id = id;
            Description = description;
            CharacterIds = characterIds ?? new List<string>();
            Events = events ?? new List<WorldEvent>();
        }
    }
}
