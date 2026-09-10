using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>What one event did to one person.</summary>
    public sealed class PerceptionOutcome
    {
        public string CharacterId { get; }
        public Access Access { get; }

        /// <summary>What it meant to them. Null when it never reached them.</summary>
        public string Meaning { get; }

        public bool FromOwnIntent { get; }
        public IReadOnlyList<EmotionContribution> Emotions { get; }
        public Experience Experience { get; }
        public int InterpretationTraceId { get; }

        /// <summary>How heavily the winning reading beat the alternatives.</summary>
        public double InterpretationWeight { get; }

        /// <summary>The reading that nearly won instead. Null when nothing else fitted.</summary>
        public string RunnerUpMeaning { get; }

        public PerceptionOutcome(
            string characterId, Access access, string meaning, bool fromOwnIntent,
            IReadOnlyList<EmotionContribution> emotions, Experience experience, int interpretationTraceId,
            double interpretationWeight = 0.0, string runnerUpMeaning = null)
        {
            CharacterId = characterId;
            Access = access;
            Meaning = meaning;
            FromOwnIntent = fromOwnIntent;
            Emotions = emotions ?? new List<EmotionContribution>();
            Experience = experience;
            InterpretationTraceId = interpretationTraceId;
            InterpretationWeight = interpretationWeight;
            RunnerUpMeaning = runnerUpMeaning;
        }

        /// <summary>
        /// The strongest feeling THIS event produced. Not the same as what the
        /// person is most strongly feeling, which may be left over from before.
        /// </summary>
        public EmotionContribution Dominant => Emotions.Count == 0 ? null : Emotions[0];

        public string DominantEmotion => Dominant?.Type;
        public double DominantIntensity => Dominant?.Intensity ?? 0.0;

        public override string ToString()
            => Access == Access.None
                ? $"{CharacterId}: was not there"
                : $"{CharacterId}: {Meaning}" + (DominantEmotion == null ? "" : $", {Dominant}");
    }

    /// <summary>One event, and what it did to everybody.</summary>
    public sealed class EventOutcome
    {
        public WorldEvent Event { get; }
        public IReadOnlyDictionary<string, PerceptionOutcome> ByCharacter { get; }
        public int TraceId { get; }

        public EventOutcome(WorldEvent worldEvent, IReadOnlyDictionary<string, PerceptionOutcome> byCharacter, int traceId)
        {
            Event = worldEvent;
            ByCharacter = byCharacter;
            TraceId = traceId;
        }
    }

    /// <summary>
    /// Runs a script of events past a cast of minds.
    ///
    /// The world holds what happened. Each mind receives only what its access
    /// allows, makes its own sense of it, and keeps its own record. Nothing is
    /// shared, nothing is reconciled, and no mind ever reads the script.
    ///
    /// Everything here is deterministic: no randomness at all in this slice, so
    /// the same script and cast always produce the same traces.
    /// </summary>
    public sealed class Simulation
    {
        readonly IReadOnlyDictionary<string, Profile> _cast;
        readonly IReadOnlyList<string> _order;
        readonly RuleSet _rules;
        readonly Interpreter _interpreter;
        readonly Appraiser _appraiser;
        readonly Dictionary<string, Mind> _minds = new Dictionary<string, Mind>(StringComparer.Ordinal);

        int _eventsProcessed;

        public TraceLog Trace { get; }
        public IReadOnlyDictionary<string, Mind> Minds => _minds;

        public Simulation(IReadOnlyDictionary<string, Profile> cast, RuleSet rules, TraceLog trace = null)
        {
            _cast = cast;
            _rules = rules;
            _interpreter = new Interpreter(rules);
            _appraiser = new Appraiser(rules);
            Trace = trace ?? new TraceLog();

            _order = cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();
            foreach (var id in _order) _minds[id] = new Mind(cast[id]);
        }

        public IReadOnlyList<EventOutcome> Run(ScenarioScript script)
        {
            var outcomes = new List<EventOutcome>();
            foreach (var e in script.Events) outcomes.Add(Apply(e));
            return outcomes;
        }

        public EventOutcome Apply(WorldEvent e)
        {
            var eventTrace = Trace.Add(TraceKind.Event, null, e.Id, e.Summary);

            // Time passes between events, so feelings fade before the next one
            // arrives. Memories and grudges do not.
            if (_eventsProcessed > 0)
                foreach (var id in _order) Fade(_minds[id]);
            _eventsProcessed++;

            var byCharacter = new Dictionary<string, PerceptionOutcome>(StringComparer.Ordinal);
            foreach (var id in _order) byCharacter[id] = Perceive(_minds[id], e, eventTrace);

            return new EventOutcome(e, byCharacter, eventTrace);
        }

        void Fade(Mind mind)
        {
            var factor = _rules.Dynamics.EmotionDecayBase
                       + _rules.Dynamics.EmotionDecayAnxietyResistance * mind.Profile.Trait("anxious");
            if (factor > 0.95) factor = 0.95;
            if (factor < 0.0) factor = 0.0;
            mind.Emotions.Decay(factor, _rules.Dynamics.EmotionFloor);
        }

        PerceptionOutcome Perceive(Mind mind, WorldEvent e, int eventTrace)
        {
            var access = e.AccessFor(mind.Id);

            if (access == Access.None)
            {
                Trace.Add(TraceKind.Access, mind.Id, e.Id, "was not there, and learns nothing", new[] { eventTrace });
                return new PerceptionOutcome(mind.Id, access, null, false, null, null, -1);
            }

            var accessTrace = Trace.Add(
                TraceKind.Access, mind.Id, e.Id,
                access == Access.Witnessed ? "was there and saw it" : "heard it without seeing it",
                new[] { eventTrace });

            var interpretation = _interpreter.Interpret(mind, e, access, _cast, Trace, accessTrace);

            _cast.TryGetValue(e.ActorId ?? "", out var actor);
            var ctx = new MatchContext(e, mind.Profile, actor, access, interpretation.Meaning);

            var reach = access == Access.Overheard ? _rules.Dynamics.OverheardIntensityScale : 1.0;
            var attention = mind.Profile.Attention(interpretation.Meaning);
            var emotions = _appraiser.Appraise(mind, ctx, reach * attention, Trace, interpretation.TraceId);

            // Several feelings at once make a moment stick harder, but not
            // without limit: a saturating fold keeps salience able to tell one
            // memory from another instead of pinning them all at the ceiling.
            var stirred = 0.0;
            foreach (var c in emotions) stirred = Accumulate.Toward(stirred, c.Intensity);
            var salience = Accumulate.Clamp01(
                (_rules.Dynamics.SalienceBase + _rules.Dynamics.SalienceEmotionWeight * stirred) * attention);
            var confidence = access == Access.Overheard ? _rules.Dynamics.OverheardConfidence : 1.0;

            var experience = new Experience(
                e.Id, e.Day, e.Order, e.ActorId,
                interpretation.Meaning, interpretation.FromOwnIntent, access,
                confidence, salience,
                emotions.Count == 0 ? null : emotions[0].Type,
                Trace.Add(
                    TraceKind.Experience, mind.Id, e.Id,
                    $"kept it as {interpretation.Meaning}"
                    + (emotions.Count == 0 ? "" : $", felt as {emotions[0].Type}"),
                    new[] { interpretation.TraceId },
                    new Dictionary<string, string>
                    {
                        { "meaning", interpretation.Meaning },
                        { "source", interpretation.FromOwnIntent ? "own intention" : access.ToString().ToLowerInvariant() },
                        { "confidence", confidence.ToString("0.00") },
                        { "salience", salience.ToString("0.00") }
                    }),
                e.Summary);

            mind.Remember(experience);

            foreach (var c in emotions)
                mind.Emotions.Add(c.Type, c.TargetId, c.Concern, c.Intensity, c.TraceId, e.Id);

            ApplyBeliefNudges(mind, ctx, e, experience.TraceId);
            ApplyAuthoredEffects(mind, e, experience.TraceId);

            return new PerceptionOutcome(
                mind.Id, access, interpretation.Meaning, interpretation.FromOwnIntent,
                emotions, experience, interpretation.TraceId,
                interpretation.Weight, interpretation.RunnerUpMeaning);
        }

        void ApplyBeliefNudges(Mind mind, MatchContext ctx, WorldEvent e, int experienceTrace)
        {
            foreach (var rule in _rules.BeliefNudges)
            {
                if (!rule.When.Matches(ctx)) continue;

                var terms = Interpreter.Evaluate(rule.ScaledBy, mind, ctx);
                var delta = rule.Delta + terms.Sum(t => t.Amount);
                if (Math.Abs(delta) < 1e-9) continue;

                var args = rule.Args.Select(ctx.Resolve).ToList();
                if (args.Any(a => a == null)) continue;

                var before = mind.Beliefs.Confidence(rule.Predicate, args);

                var traceId = Trace.Add(
                    TraceKind.BeliefChange, mind.Id, e.Id,
                    $"{BeliefKey.Of(rule.Predicate, args)}: {before:0.00} -> pending",
                    new[] { experienceTrace });

                var after = mind.Beliefs.Nudge(rule.Predicate, args, delta, traceId);

                Trace.Add(
                    TraceKind.BeliefChange, mind.Id, e.Id,
                    $"{BeliefKey.Of(rule.Predicate, args)} moved {before:0.00} -> {after:0.00}",
                    new[] { traceId },
                    new Dictionary<string, string>
                    {
                        { "rule", rule.Id },
                        { "delta", delta.ToString("+0.00;-0.00") }
                    });
            }
        }

        void ApplyAuthoredEffects(Mind mind, WorldEvent e, int experienceTrace)
        {
            foreach (var f in e.LedgerEffects)
            {
                if (!string.Equals(f.HolderId, mind.Id, StringComparison.Ordinal)) continue;

                // Belt and braces: the validator rejects this at author time, and
                // the simulation refuses it again here, because a memory of
                // something you were not there for is the one bug that would
                // quietly invalidate the whole slice.
                if (e.AccessFor(mind.Id) == Access.None) continue;

                var traceId = Trace.Add(
                    TraceKind.LedgerEntry, mind.Id, e.Id,
                    $"will not forget: {f.Entry} ({f.AboutId})",
                    new[] { experienceTrace },
                    new Dictionary<string, string> { { "weight", f.Weight.ToString("0.00") } });

                mind.Ledger.Add(f.AboutId, f.Entry, f.Weight, traceId, e.Id);
            }

            foreach (var f in e.BeliefEffects)
            {
                if (!string.Equals(f.HolderId, mind.Id, StringComparison.Ordinal)) continue;
                if (e.AccessFor(mind.Id) == Access.None) continue;

                var before = mind.Beliefs.ConfidenceByKey(f.Key);

                var traceId = Trace.Add(
                    TraceKind.BeliefChange, mind.Id, e.Id,
                    $"{f.Key}: {before:0.00} -> pending",
                    new[] { experienceTrace });

                var after = mind.Beliefs.Nudge(f.Predicate, f.Args, f.Delta, traceId);

                Trace.Add(
                    TraceKind.BeliefChange, mind.Id, e.Id,
                    $"{f.Key} moved {before:0.00} -> {after:0.00}",
                    new[] { traceId },
                    new Dictionary<string, string> { { "delta", f.Delta.ToString("+0.00;-0.00") } });
            }
        }
    }
}
