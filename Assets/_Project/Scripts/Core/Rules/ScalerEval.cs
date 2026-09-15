using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;

namespace Fallow.Core.Rules
{
    /// <summary>
    /// Everything a scaler may need that is not already on the mind: what the
    /// tokens stand for here, and how hungry the person is.
    ///
    /// Both the event pipeline and the decision pipeline supply one of these, so
    /// a weight is worked out the same way whether it is deciding what a remark
    /// meant or what to do about it.
    /// </summary>
    public interface IScalerContext
    {
        /// <summary>Turns a token such as $actor into the person it stands for here.</summary>
        string Resolve(string token);

        /// <summary>A bodily need, 0..1. Zero where the context has no body in view.</summary>
        double Need(string name);

        /// <summary>The day being lived, so that a memory scaler can mean "today".</summary>
        int Today { get; }

        /// <summary>Minutes into the day, or -1 when nothing is keeping time.</summary>
        int Now { get; }

        /// <summary>How long it takes a memory to press half as hard as it did.</summary>
        double RecallHalfLife { get; }
    }

    /// <summary>
    /// Works out how much each part of a person pushes a rule.
    ///
    /// One implementation for the whole simulation, so an interpretation, a
    /// feeling, a want and the cost of an action are all weighed by the same
    /// arithmetic and read the same way in a trace.
    /// </summary>
    public static class ScalerEval
    {
        public static IReadOnlyList<ScalerTerm> Evaluate(
            IReadOnlyList<Scaler> scalers, Mind mind, IScalerContext ctx)
        {
            var terms = new List<ScalerTerm>();
            if (scalers == null) return terms;

            foreach (var s in scalers)
            {
                double level;
                string note = null;
                var answered = false;
                var drew = new List<int>();

                switch (s.Kind)
                {
                    case ScalerKind.Trait:
                        level = mind.Profile.Trait(s.Name);
                        break;
                    case ScalerKind.Value:
                        level = mind.Profile.ValueWeight(s.Name);
                        break;
                    case ScalerKind.Perceptiveness:
                        level = mind.Profile.Perceptiveness;
                        break;
                    case ScalerKind.Emotion:
                        level = Feeling(mind, s, ctx, drew);
                        break;
                    case ScalerKind.Ledger:
                        level = Remembered(mind, s, ctx, drew);
                        break;
                    case ScalerKind.Belief:
                        level = Held(mind, s, ctx, drew);
                        break;
                    case ScalerKind.Need:
                        // The level is the body, read now. What the term rests on
                        // is the last thing this person did about it, so a need
                        // that fell because they ate, or stayed because the food
                        // was gone, can say so. The record moves nothing: time and
                        // the body do the rest, as they always did. Added in S1.3.
                        level = ctx.Need(s.Name);
                        var latest = mind.LatestOutcomeFor(s.Name);
                        if (latest != null)
                        {
                            drew.Add(latest.TraceId);
                            note = " (" + latest + ")";
                        }
                        break;
                    case ScalerKind.Memory:
                        level = Recall(mind, s, ctx, drew, out var answer);
                        if (answer != null && level == 0.0)
                        {
                            answered = true;
                            note = " (answered: " + answer.Meaning + " at minute " + answer.Minute + ")";
                        }
                        break;
                    case ScalerKind.Constant:
                        level = 1.0;
                        break;
                    default:
                        continue;
                }

                terms.Add(new ScalerTerm(s.Describe(ctx.Resolve) + note, level, s.Factor, drew, answered, s.Kind));
            }

            return terms;
        }

        /// <summary>
        /// How strongly this person is carrying a memory of a given kind.
        ///
        /// Salience decides how hard it landed, which is the whole point of
        /// keeping it, and time decides how much of that is still pressing now.
        /// Something that landed hard an hour ago is still there and no longer
        /// urgent, which is what stops a person acting on the same moment over
        /// and over for a whole morning.
        ///
        /// Who a memory is about and who did it are different questions, and
        /// they are asked separately. Watching somebody deliver bad news is not
        /// the same as watching somebody go to pieces, and a rule that ran the
        /// two together would have the whole house comforting the messenger.
        ///
        /// Only the day being lived counts. Yesterday works through beliefs and
        /// grudges instead, as it should.
        /// </summary>
        static double Recall(Mind mind, Scaler s, IScalerContext ctx, List<int> drew, out Experience answeredBy)
        {
            var about = ctx.Resolve(s.About);
            var by = ctx.Resolve(s.By);
            var best = 0.0;
            Experience strongest = null;
            answeredBy = null;

            bool SameSubject(Experience x)
                => x.Day == ctx.Today
                   && (s.Topic == null || string.Equals(x.Topic, s.Topic, StringComparison.Ordinal))
                   && (about == null || string.Equals(x.TargetId, about, StringComparison.Ordinal))
                   && (by == null || string.Equals(x.ActorId, by, StringComparison.Ordinal));

            var experiences = mind.Experiences;
            for (var i = 0; i < experiences.Count; i++)
            {
                var x = experiences[i];
                if (!SameSubject(x)) continue;
                if (s.Name != null && !string.Equals(x.Meaning, s.Name, StringComparison.Ordinal)) continue;

                // Answered by anything later about the same subject that carries
                // one of the readings that answer it. Memories are kept in the
                // order they were made, so later means further along the list.
                if (s.Until != null && s.Until.Count > 0)
                {
                    Experience answer = null;
                    for (var j = i + 1; j < experiences.Count; j++)
                        if (SameSubject(experiences[j]) && s.Until.Contains(experiences[j].Meaning, StringComparer.Ordinal))
                            answer = experiences[j];
                    if (answer != null)
                    {
                        answeredBy = answer;
                        continue;
                    }
                }

                var pressing = x.Salience * Freshness(x.Minute, ctx);
                if (pressing <= best) continue;

                best = pressing;
                strongest = x;
            }

            if (strongest != null) drew.Add(strongest.TraceId);
            else if (answeredBy != null) drew.Add(answeredBy.TraceId);
            return best;
        }

        /// <summary>The feeling a rule weighed, and what caused it.</summary>
        static double Feeling(Mind mind, Scaler s, IScalerContext ctx, List<int> drew)
        {
            var anybody = string.Equals(s.Target, Scaler.Anybody, StringComparison.Ordinal);
            var target = anybody ? null : ctx.Resolve(s.Target);

            var instance = mind.Emotions.Live.FirstOrDefault(e =>
                string.Equals(e.Type, s.Name, StringComparison.Ordinal)
                && (anybody || string.Equals(e.TargetId, target, StringComparison.Ordinal)));

            if (instance == null) return 0.0;

            drew.AddRange(instance.Causes);
            return instance.Intensity;
        }

        /// <summary>What this person holds against somebody, and the moments it came from.</summary>
        static double Remembered(Mind mind, Scaler s, IScalerContext ctx, List<int> drew)
        {
            var about = ctx.Resolve(s.About);

            foreach (var r in mind.Ledger.About(about))
                if (string.Equals(r.Entry, s.Entry, StringComparison.Ordinal))
                    drew.Add(r.TraceId);

            return mind.Ledger.Strength(about, s.Entry);
        }

        /// <summary>A belief, and the evidence that moved it.</summary>
        static double Held(Mind mind, Scaler s, IScalerContext ctx, List<int> drew)
        {
            var args = s.Args == null ? new List<string>() : s.Args.Select(ctx.Resolve).ToList();
            var belief = mind.Beliefs.Get(s.Predicate, args);

            drew.AddRange(belief.Justifications);
            return belief.Confidence;
        }

        /// <summary>
        /// How much of a memory is still pressing. Nothing is lost from the
        /// record, but the urgency of it halves over the recall half life, so
        /// wanting to do something about a moment is loudest just after it and
        /// quiet an hour later.
        /// </summary>
        static double Freshness(int minute, IScalerContext ctx)
        {
            if (minute < 0 || ctx.Now < 0) return 1.0;

            var half = ctx.RecallHalfLife;
            if (half <= 0.0) return 1.0;

            var elapsed = ctx.Now - minute;
            if (elapsed <= 0) return 1.0;
            return half / (half + elapsed);
        }
    }
}
