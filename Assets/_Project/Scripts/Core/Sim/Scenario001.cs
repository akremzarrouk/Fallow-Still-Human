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

            var sim = new Simulation(content.Cast, content.Rules);

            // Three days of living, felt as it happened.
            sim.Run(content.Backstory);

            // What actually happened in the night, known only to whoever was there.
            foreach (var e in variant.NightEvents) sim.Apply(e);

            var world = new WorldState(content.Morning.House, content.Morning.Portions);
            foreach (var pair in content.Morning.StartRooms) world.Place(pair.Key, pair.Value);
            foreach (var pair in content.Morning.StartHunger) world.SetHunger(pair.Key, pair.Value);

            var morning = new SilentMorning(sim, content.Rules, world, new Rng(seed), content.Morning.Day);

            // The one scripted moment of the morning, and the last one.
            if (content.Morning.Opening != null) sim.Apply(content.Morning.Opening);

            return new Scenario001Run(variantId, seed, sim, morning, world);
        }

        public static Scenario001Run Run(Scenario001Content content, string variantId, ulong seed, int? minutes = null)
        {
            var run = Prepare(content, variantId, seed);
            run.Morning.Run(minutes ?? content.Morning.Minutes);
            return run;
        }
    }
}
