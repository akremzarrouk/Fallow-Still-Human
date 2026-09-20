using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// How one arm of the S1.7 experiment is set up: whose history, how much of
    /// it, whether they saw it, how long ago, and what happens to them later.
    ///
    /// Everything here is scenario data. Nothing in it is read by a rule, and no
    /// field names a mechanism: the simulation is handed events and a person, and
    /// whatever it does with them is the measurement.
    /// </summary>
    internal sealed class S17Arm
    {
        public string Label = "";

        /// <summary>The person whose history is varied and whose chain is measured.</summary>
        public string Subject = "elena";

        /// <summary>Who goes through the subject's things, earlier and (unless ProbeActor says otherwise) later.</summary>
        public string Other = "daniel";

        /// <summary>Who does the later thing. Null means the same person as the earlier history.</summary>
        public string ProbeActor;

        /// <summary>How many earlier times this person went through the subject's things.</summary>
        public int PriorSlights;

        /// <summary>Whether the subject was there to see them. False is the knowledge-locality arm.</summary>
        public bool SubjectSeesPriors = true;

        /// <summary>Whether the subject did the thing the house is short of, which is what makes them answerable.</summary>
        public bool Answerable = true;

        /// <summary>Days between the last earlier event and the later one.</summary>
        public int LagDays = 1;

        /// <summary>Fades of time between the earlier history and the later event. One fade is what a backstory episode costs.</summary>
        public double LagFades = 1.0;

        /// <summary>What happens later: search, observe, demand or refuse. See S17.Probe.</summary>
        public string ProbeKind = S17.Search;

        /// <summary>Where the subject is standing when they decide, and who is with them.</summary>
        public string Room = "back_room";
        public IReadOnlyList<string> Present;

        /// <summary>How hungry the subject is when they decide. Null leaves the scenario's own figure.</summary>
        public double? Hunger;

        /// <summary>Set instead of PriorSlights to put a belief at an exact level, for the response curve.</summary>
        public Dictionary<string, double> ForceBeliefs;

        public S17Arm With(Action<S17Arm> change)
        {
            var copy = (S17Arm)MemberwiseClone();
            if (ForceBeliefs != null) copy.ForceBeliefs = new Dictionary<string, double>(ForceBeliefs, StringComparer.Ordinal);
            change(copy);
            return copy;
        }
    }

    /// <summary>
    /// Every stage of one person's chain at one later event, in the order the
    /// pipeline produced them. Built only from what the simulation returned and
    /// from the trace; nothing is recomputed by hand.
    /// </summary>
    internal sealed class S17Chain
    {
        public string Label;

        // perception and memory
        public bool Perceived;
        public string ExperienceMeaning;
        public double Salience;
        public int ExperienceTraceId = -1;

        // belief, as it stood before the later event moved anything
        public Dictionary<string, double> BeliefsBefore = new Dictionary<string, double>(StringComparer.Ordinal);
        public Dictionary<string, double> BeliefsAfter = new Dictionary<string, double>(StringComparer.Ordinal);
        public Dictionary<string, int> BeliefJustifications = new Dictionary<string, int>(StringComparer.Ordinal);

        // interpretation
        public string Meaning;
        public double Weight;
        public string RunnerUp;
        public double RunnerUpWeight;
        public string RulesDetail;
        public int InterpretationTraceId = -1;

        // internal state. What this event itself stirred, and what the person is
        // carrying in total, which also holds whatever earlier events left behind.
        public Dictionary<string, double> ProbeEmotions = new Dictionary<string, double>(StringComparer.Ordinal);
        public Dictionary<string, double> Emotions = new Dictionary<string, double>(StringComparer.Ordinal);

        // motivation, deliberation, action
        public Dictionary<string, double> Wants = new Dictionary<string, double>(StringComparer.Ordinal);
        public List<string> Ranked = new List<string>();
        public Dictionary<string, double> Scores = new Dictionary<string, double>(StringComparer.Ordinal);
        public string Chosen;
        public string LeadingWant;
        public string Resolution;
        public int DecisionTraceId = -1;

        // The decision as it was taken, kept so that it can be weighed again
        // with one want changed (the decision-sensitivity experiment). Read
        // only: nothing here is used by S1.7 itself.
        public Mind Mind;
        public Percept Percept;
        public IReadOnlyList<Motive> Motives;
        public int Day;

        public TraceLog Trace;

        /// <summary>The ids of the earlier events this arm lived through, so a trace can be asked to reach them.</summary>
        public List<string> HistoryEventIds = new List<string>();

        public double Belief(string key) => BeliefsBefore.TryGetValue(key, out var v) ? v : 0.0;
        public double Emotion(string type) => Emotions.TryGetValue(type, out var v) ? v : 0.0;
        public double Stirred(string type) => ProbeEmotions.TryGetValue(type, out var v) ? v : 0.0;
        public double Want(string key) => Wants.TryGetValue(key, out var v) ? v : 0.0;
        public double Score(string option) => Scores.TryGetValue(option, out var v) ? v : 0.0;

        /// <summary>What this event itself stirred, exactly. Appraisal's own output, before anything left over is added in.</summary>
        public string Stirring =>
            string.Join(",", ProbeEmotions.OrderBy(k => k.Key, StringComparer.Ordinal)
                .Select(k => k.Key + "=" + k.Value.ToString("F9", CultureInfo.InvariantCulture)));

        /// <summary>Everything downstream of the reading, as one string, so two arms can be compared exactly.</summary>
        public string Downstream =>
            "emotions[" + string.Join(",", Emotions.OrderBy(k => k.Key, StringComparer.Ordinal).Select(k => k.Key + "=" + k.Value.ToString("F9", CultureInfo.InvariantCulture))) + "] " +
            "wants[" + string.Join(",", Wants.OrderBy(k => k.Key, StringComparer.Ordinal).Select(k => k.Key + "=" + k.Value.ToString("F9", CultureInfo.InvariantCulture))) + "] " +
            "scores[" + string.Join(",", Scores.OrderBy(k => k.Key, StringComparer.Ordinal).Select(k => k.Key + "=" + k.Value.ToString("F9", CultureInfo.InvariantCulture))) + "] " +
            "chose=" + Chosen;
    }

    internal static class S17
    {
        public const string Search = "search";
        public const string Observe = "observe";
        public const string Demand = "demand";
        public const string Refuse = "refuse";

        /// <summary>The beliefs this experiment watches. Named here only so the report can print them.</summary>
        internal static readonly string[] Watched =
        {
            "tendency(daniel,treats_me_like_a_child)",
            "tendency(daniel,does_not_respect_me)",
            "tendency(daniel,needs_to_be_in_charge)",
            "tendency(leo,treats_me_like_a_child)",
            "tendency(leo,does_not_respect_me)",
            "answerable_for(elena,missing_can)",
            "supplies_short()"
        };

        internal static readonly string[] People = { "daniel", "elena", "leo", "mara" };

        internal static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);

        // ---- events. Every one is ordinary scenario data. ----

        static int _order;

        static WorldEvent Event(
            string id, int day, EventKind kind, string actor, string target,
            string act, string action, string topic, string tone, string valence, string intent,
            IReadOnlyList<string> witnesses, string summary)
            => new WorldEvent(
                id, day, ++_order, kind, actor, target, act, action, topic, tone, "direct", valence,
                intent, summary, witnesses, new List<string>(), new List<LedgerEffect>(), null, -1);

        /// <summary>Somebody goes through somebody else's things while they are standing there.</summary>
        internal static WorldEvent WentThroughTheirThings(string actor, string subject, int day, IReadOnlyList<string> witnesses)
            => Event("s17-slight-" + day + "-" + _order, day, EventKind.Action, actor, subject,
                null, "search_belongings", "missing_can", "firm", "neutral", "take_responsibility",
                witnesses, actor + " goes through " + subject + "'s things while they stand there.");

        /// <summary>The subject does the thing the house will later be short of, in front of one person.</summary>
        internal static WorldEvent TookAPortion(string actor, string target, int day)
            => Event("s17-night-" + day, day, EventKind.Action, actor, target,
                null, "give_portion", "missing_can", "neutral", "good", "protect",
                target == null ? new List<string>() : new List<string> { target },
                actor + " opens a can in the night and gives it to " + target + ".");

        /// <summary>The later event, built the same way in every arm.</summary>
        internal static WorldEvent Probe(string kind, string actor, string subject, int day, IReadOnlyList<string> witnesses)
        {
            switch (kind)
            {
                case Observe:
                    return Event("s17-probe", day, EventKind.Action, actor, subject,
                        null, "observe", null, "neutral", "neutral", null,
                        witnesses, actor + " watches " + subject + " without saying anything.");
                case Demand:
                    return Event("s17-probe", day, EventKind.Speech, actor, subject,
                        "demand", null, "who_decides", "calm", "neutral", "assert_authority",
                        witnesses, actor + " tells " + subject + " what is going to happen.");
                case Refuse:
                    return Event("s17-probe", day, EventKind.Speech, actor, subject,
                        "refuse", null, "going_outside", "calm", "neutral", "protect",
                        witnesses, actor + " refuses, in front of everyone.");
                default:
                    return Event("s17-probe", day, EventKind.Action, actor, subject,
                        null, "search_belongings", "missing_can", "firm", "neutral", "take_responsibility",
                        witnesses, actor + " goes through " + subject + "'s things while they stand there.");
            }
        }

        // ---- running one arm ----

        /// <summary>
        /// One arm: build fresh minds, live the history, let time pass, then let
        /// the later event happen and watch what the person does about it.
        ///
        /// The backstory is deliberately not run. The only history these people
        /// have is the history this arm gives them, so the independent variable is
        /// the only thing that differs between arms.
        /// </summary>
        internal static S17Chain Run(Scenario001Content content, S17Arm arm)
        {
            _order = 0;
            var chain = new S17Chain { Label = arm.Label };
            var trace = new TraceLog();
            var sim = new Simulation(content.Cast, content.Rules, trace) { FadeOnEachEvent = false };
            chain.Trace = trace;

            var subject = arm.Subject;
            var other = arm.Other;
            var probeActor = arm.ProbeActor ?? other;
            var everyone = content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();

            // 1. The history. Each earlier time is its own day, so nothing in the
            //    later decision can be recalled as a memory of today.
            var day = 1;
            for (var i = 0; i < arm.PriorSlights; i++)
            {
                var witnesses = arm.SubjectSeesPriors
                    ? new List<string> { subject }
                    : new List<string>();
                var slight = WentThroughTheirThings(other, subject, day, witnesses);
                chain.HistoryEventIds.Add(slight.Id);
                sim.Apply(slight);
                sim.PassTime(1.0);
                day++;
            }

            // 2. A belief set directly, for the response curve. An experiment
            //    reaching into a mind on purpose, recorded as what it is.
            if (arm.ForceBeliefs != null)
                foreach (var pair in arm.ForceBeliefs)
                {
                    var (predicate, args) = SplitKey(pair.Key);
                    var mind = sim.Minds[subject];
                    var at = mind.Beliefs.Confidence(predicate, args);
                    var id = trace.Add(TraceKind.BeliefChange, subject, null,
                        "an experiment set " + pair.Key + " to " + F(pair.Value) + " (was " + F(at) + ")");
                    mind.Beliefs.Nudge(predicate, args, 0.0, id);
                    Force(mind, predicate, args, pair.Value, id);
                }

            // 3. What makes the subject answerable for what is missing.
            if (arm.Answerable)
            {
                var toldTo = everyone.FirstOrDefault(p => p != subject && p != other) ?? other;
                sim.Apply(TookAPortion(subject, toldTo, day));
                sim.PassTime(1.0);
                day++;
            }

            // 4. Time between the history and the later event.
            day += Math.Max(0, arm.LagDays - 1);
            if (arm.LagFades > 0.0) sim.PassTime(arm.LagFades);

            // 5. Beliefs as they stand before the later event moves anything.
            foreach (var key in Watched)
            {
                var (predicate, args) = SplitKey(key);
                chain.BeliefsBefore[key] = sim.Minds[subject].Beliefs.Confidence(predicate, args);
            }

            // 6. The later event, identical in every arm but for who does it.
            var present = arm.Present ?? new List<string> { probeActor };
            var audience = new List<string> { subject };
            foreach (var p in present) if (p != subject && p != probeActor) audience.Add(p);
            var probe = Probe(arm.ProbeKind, probeActor, subject, day, audience);
            var outcome = sim.Apply(probe);

            var seen = outcome.ByCharacter[subject];
            chain.Perceived = seen.Access != Access.None;
            chain.Meaning = seen.Meaning;
            chain.Weight = seen.InterpretationWeight;
            chain.RunnerUp = seen.RunnerUpMeaning;
            chain.InterpretationTraceId = seen.InterpretationTraceId;
            var record = trace.Get(seen.InterpretationTraceId);
            if (record != null)
            {
                chain.RulesDetail = record.Data.TryGetValue("rules", out var r) ? r : null;
                if (record.Data.TryGetValue("runner_up", out var ru))
                {
                    var bits = ru.Split(' ');
                    double.TryParse(bits[bits.Length - 1], NumberStyles.Float, CultureInfo.InvariantCulture, out var w);
                    chain.RunnerUpWeight = w;
                }
            }
            if (seen.Experience != null)
            {
                chain.ExperienceMeaning = seen.Experience.Meaning;
                chain.Salience = seen.Experience.Salience;
                chain.ExperienceTraceId = seen.Experience.TraceId;
            }
            foreach (var key in Watched)
            {
                var (predicate, args) = SplitKey(key);
                var belief = sim.Minds[subject].Beliefs.Get(predicate, args);
                chain.BeliefsAfter[key] = belief.Confidence;
                if (belief.Justifications.Count > 0) chain.BeliefJustifications[key] = belief.Justifications[belief.Justifications.Count - 1];
            }

            foreach (var c in seen.Emotions)
                if (!chain.ProbeEmotions.TryGetValue(c.Type, out var stirred) || c.Intensity > stirred)
                    chain.ProbeEmotions[c.Type] = c.Intensity;

            foreach (var e in sim.Minds[subject].Emotions.Live)
                if (!chain.Emotions.TryGetValue(e.Type, out var at) || e.Intensity > at)
                    chain.Emotions[e.Type] = e.Intensity;

            // 7. What they now want, and what they do about it.
            var world = new WorldState(content.Morning.House, content.Morning.Portions);
            foreach (var id in everyone) world.Place(id, id == subject || present.Contains(id) ? arm.Room : "living_room");
            foreach (var pair in content.Morning.StartHunger) world.SetHunger(pair.Key, pair.Value);
            if (arm.Hunger.HasValue) world.SetHunger(subject, arm.Hunger.Value);

            var morning = new SilentMorning(sim, content.Rules, world, new Rng(1), probe.Day);
            var percept = morning.See(subject);
            var motives = new Motivator(content.Rules).Raise(sim.Minds[subject], percept, probe.Day, trace, seen.InterpretationTraceId);
            var decision = new Deliberator(content.Rules).Decide(
                sim.Minds[subject], percept, motives, probe.Day, new Rng(1), trace, seen.InterpretationTraceId);

            foreach (var m in motives) chain.Wants[m.Key] = m.Urgency;
            foreach (var r in decision.Ranked)
            {
                chain.Ranked.Add(r.Option.Key);
                chain.Scores[r.Option.Key] = r.Score;
            }
            chain.Chosen = decision.Chosen.Key;
            chain.LeadingWant = decision.Leading?.Key ?? "nothing";
            chain.Resolution = decision.Resolution == Resolution.Clear ? "clear" : "too close to call";
            chain.DecisionTraceId = decision.TraceId;
            chain.Mind = sim.Minds[subject];
            chain.Percept = percept;
            chain.Motives = motives;
            chain.Day = probe.Day;
            return chain;
        }

        /// <summary>
        /// Puts a belief at an exact level. Only an experiment may do this, and it
        /// is written into the trace as an intervention so that no chain built on
        /// it can be mistaken for one the world produced.
        /// </summary>
        static void Force(Mind mind, string predicate, IReadOnlyList<string> args, double target, int traceId)
        {
            var at = mind.Beliefs.Confidence(predicate, args);
            for (var i = 0; i < 400 && Math.Abs(at - target) > 1e-6; i++)
            {
                var room = target > at ? 1.0 - at : at;
                if (room <= 1e-12) break;
                mind.Beliefs.Nudge(predicate, args, (target - at) / room, traceId);
                at = mind.Beliefs.Confidence(predicate, args);
            }
        }

        static (string, IReadOnlyList<string>) SplitKey(string key)
        {
            var open = key.IndexOf('(');
            if (open < 0) return (key, new List<string>());
            var predicate = key.Substring(0, open);
            var inside = key.Substring(open + 1, key.Length - open - 2);
            var args = inside.Length == 0
                ? new List<string>()
                : inside.Split(',').Select(a => a.Trim()).ToList();
            return (predicate, args);
        }

        /// <summary>
        /// The same slice with the subject's history written into the backstory,
        /// so that a whole morning can be run with it and without it. The earlier
        /// times sit between the last day-3 episode and the day-4 ones, which is
        /// where they belong chronologically.
        /// </summary>
        internal static Scenario001Content WithHistory(Scenario001Content c, int times, string actor, string subject)
        {
            WorldEvent Renumbered(WorldEvent e, int order) => new WorldEvent(
                e.Id, e.Day, order, e.Kind, e.ActorId, e.TargetId, e.Act, e.Action, e.Topic, e.Tone,
                e.Directness, e.Valence, e.Intent, e.Summary, e.Witnesses, e.Overhearers,
                e.LedgerEffects, e.BeliefEffects, e.Minute);

            var events = c.Backstory.Events.Select(e => Renumbered(e, e.Order * 100)).ToList();
            for (var i = 0; i < times; i++)
            {
                var slight = WentThroughTheirThings(actor, subject, 3, new List<string> { subject });
                events.Add(Renumbered(slight, 900 + 1 + i));
            }

            var backstory = new ScenarioScript(
                c.Backstory.Id, c.Backstory.Description, c.Backstory.CharacterIds,
                events.OrderBy(e => e.Order).ToList());
            return new Scenario001Content(c.Vocabulary, c.Cast, backstory, c.Morning, c.Rules);
        }

        // ---- reporting ----

        internal static string ChainTable(IEnumerable<S17Chain> chains)
        {
            var list = chains.ToList();
            var sb = new System.Text.StringBuilder();
            string Row(string name, Func<S17Chain, string> value)
                => "| " + name + " | " + string.Join(" | ", list.Select(value)) + " |";

            sb.AppendLine("| Stage | " + string.Join(" | ", list.Select(c => c.Label)) + " |");
            sb.AppendLine("|---|" + string.Join("|", list.Select(_ => "---")) + "|");
            sb.AppendLine(Row("1 perceived the later event", c => c.Perceived ? "yes" : "no"));
            sb.AppendLine(Row("2 kept it as", c => c.ExperienceMeaning ?? "nothing"));
            sb.AppendLine(Row("  salience", c => F(c.Salience)));
            foreach (var key in Watched.Where(k => list.Any(c => c.Belief(k) > 0.0)))
                sb.AppendLine(Row("3 belief `" + key + "` before", c => F(c.Belief(key))));
            sb.AppendLine(Row("4 read the later event as", c => c.Meaning + " " + F(c.Weight)));
            sb.AppendLine(Row("  next best reading", c => c.RunnerUp == null ? "none" : c.RunnerUp + " " + F(c.RunnerUpWeight)));
            foreach (var e in list.SelectMany(c => c.ProbeEmotions.Keys).Distinct().OrderBy(k => k, StringComparer.Ordinal))
                sb.AppendLine(Row("5 it stirred " + e, c => c.Stirred(e) == 0.0 ? "-" : F(c.Stirred(e))));
            foreach (var e in list.SelectMany(c => c.Emotions.Keys).Distinct().OrderBy(k => k, StringComparer.Ordinal))
                sb.AppendLine(Row("  carrying " + e, c => c.Emotion(e) == 0.0 ? "-" : F(c.Emotion(e))));
            foreach (var w in list.SelectMany(c => c.Wants.Keys).Distinct().OrderBy(k => k, StringComparer.Ordinal))
                sb.AppendLine(Row("6 wants " + w, c => c.Want(w) == 0.0 ? "-" : F(c.Want(w))));
            sb.AppendLine(Row("7 best option", c => c.Ranked.Count == 0 ? "-" : c.Ranked[0] + " " + F(c.Score(c.Ranked[0]))));
            sb.AppendLine(Row("  chose", c => c.Chosen));
            sb.AppendLine(Row("  for", c => c.LeadingWant));
            sb.AppendLine(Row("  resolution", c => c.Resolution));
            return sb.ToString();
        }
    }
}
