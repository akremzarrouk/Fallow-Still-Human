using System;
using System.Collections.Generic;
using System.IO;
using Fallow.Core.Data;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>Everything the slice needs, loaded once and shared.</summary>
    public sealed class Scenario001Content
    {
        public Vocabulary Vocabulary { get; }
        public IReadOnlyDictionary<string, Profile> Cast { get; }
        public ScenarioScript Backstory { get; }
        public MorningScenario Morning { get; }
        public RuleSet Rules { get; }

        public Scenario001Content(
            Vocabulary vocabulary, IReadOnlyDictionary<string, Profile> cast,
            ScenarioScript backstory, MorningScenario morning, RuleSet rules)
        {
            Vocabulary = vocabulary;
            Cast = cast;
            Backstory = backstory;
            Morning = morning;
            Rules = rules;
        }

        /// <summary>
        /// Loads the whole slice from a data folder. The event rules and the
        /// decision rules live in separate files and are folded together here,
        /// so how a person reads the world and what they do about it can be
        /// changed independently.
        /// </summary>
        public static Scenario001Content Load(string dataRoot)
        {
            var rulesDir = Path.Combine(dataRoot, "Rules");
            var scenarioDir = Path.Combine(dataRoot, "Scenario");

            var rules = RuleSetLoader.LoadFile(Path.Combine(rulesDir, "rules.json"));
            rules.With(RuleSetLoader.LoadFile(Path.Combine(rulesDir, "decisions.json")));

            return new Scenario001Content(
                VocabularyLoader.LoadFile(Path.Combine(rulesDir, "vocabulary.json")),
                ProfileLoader.LoadDirectory(Path.Combine(dataRoot, "Minds")),
                ScenarioLoader.LoadFile(Path.Combine(scenarioDir, "backstory.json")),
                MorningLoader.LoadFile(Path.Combine(scenarioDir, "morning.json")),
                rules);
        }
    }

    /// <summary>One prepared morning, ready to run or already run.</summary>
    public sealed class Scenario001Run
    {
        public string VariantId { get; }
        public ulong Seed { get; }
        public Simulation Simulation { get; }
        public SilentMorning Morning { get; }
        public WorldState World { get; }
        /// <summary>
        /// Everything that has happened so far. Always current, so a test can
        /// step the morning by hand and still ask what came of it.
        /// </summary>
        public MorningResult Result => Morning.Snapshot();

        public Scenario001Run(
            string variantId, ulong seed, Simulation simulation, SilentMorning morning, WorldState world)
        {
            VariantId = variantId;
            Seed = seed;
            Simulation = simulation;
            Morning = morning;
            World = world;
        }

        public TraceLog Trace => Simulation.Trace;
        public IReadOnlyDictionary<string, Mind> Minds => Simulation.Minds;
    }

    /// <summary>
    /// Sets up one silent morning and runs it.
    ///
    /// The order here is the argument of the whole slice. Three days of history
    /// go through the minds first, then whatever happened in the night reaches
    /// only the people who were there, then the discovery, and only then does
    /// anybody decide anything. By the time the first decision is taken, every
    /// difference between these four people has been produced rather than
    /// assigned: nobody was handed a feeling, a grudge or a suspicion.
    /// </summary>
    public static class Scenario001
    {
        public static Scenario001Run Prepare(Scenario001Content content, string variantId, ulong seed)
        {
            var variant = content.Morning.Variant(variantId);
            if (variant == null)
                throw new ArgumentException("no such variant: " + variantId);

            return PrepareWith(content, variantId, variant.NightEvents, seed);
        }

        /// <summary>
        /// The same preparation with the night given explicitly rather than by
        /// name, so an experiment can hold everything fixed and change one thing:
        /// leave an event out, or take one person out of the room it happened in.
        ///
        /// The stage callback sees the simulation after the backstory, after the
        /// night and after the opening, which is where a counterfactual needs to
        /// look to find out where a difference appears or disappears. It is read
        /// only in spirit; nothing in the slice passes one that writes.
        /// </summary>
        public static Scenario001Run PrepareWith(
            Scenario001Content content, string label, IReadOnlyList<WorldEvent> nightEvents, ulong seed,
            Action<string, Simulation> atStage = null)
        {
            var sim = new Simulation(content.Cast, content.Rules);

            // Three days of living, felt as it happened.
            sim.Run(content.Backstory);
            atStage?.Invoke(Stages.AfterBackstory, sim);

            // What actually happened in the night, known only to whoever was there.
            // From here on nothing that happens fades anybody it did not reach;
            // the rest of the night passes once, for everybody, whatever happened
            // in it, which is what makes two nights comparable.
            sim.FadeOnEachEvent = false;
            foreach (var e in nightEvents ?? new List<WorldEvent>()) sim.Apply(e);
            atStage?.Invoke(Stages.AfterNight, sim);
            sim.PassTime(1.0);

            var world = new WorldState(content.Morning.House, content.Morning.Portions);
            foreach (var pair in content.Morning.StartRooms) world.Place(pair.Key, pair.Value);
            foreach (var pair in content.Morning.StartHunger) world.SetHunger(pair.Key, pair.Value);

            var morning = new SilentMorning(sim, content.Rules, world, new Rng(seed), content.Morning.Day);

            // The one scripted moment of the morning, and the last one.
            if (content.Morning.Opening != null) sim.Apply(content.Morning.Opening);
            atStage?.Invoke(Stages.AfterOpening, sim);

            return new Scenario001Run(label, seed, sim, morning, world);
        }

        /// <summary>The points in preparation a counterfactual can look at.</summary>
        public static class Stages
        {
            public const string AfterBackstory = "after_backstory";
            public const string AfterNight = "after_night";
            public const string AfterOpening = "after_opening";
        }

        public static Scenario001Run Run(Scenario001Content content, string variantId, ulong seed, int? minutes = null)
        {
            var run = Prepare(content, variantId, seed);
            run.Morning.Run(minutes ?? content.Morning.Minutes);
            return run;
        }
    }
}
