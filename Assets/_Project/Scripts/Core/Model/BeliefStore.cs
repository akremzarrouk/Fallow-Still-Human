using System;
using System.Collections.Generic;
using System.Linq;

namespace Fallow.Core.Model
{
    /// <summary>What one person holds to be true, and how sure they are of it.</summary>
    public sealed class Belief
    {
        readonly List<int> _justifications = new List<int>();

        public string Predicate { get; }
        public IReadOnlyList<string> Args { get; }
        public double Confidence { get; internal set; }

        /// <summary>
        /// Trace ids of the experiences that moved this belief. A seeded belief
        /// has none, which is the honest record: the character brought it with
        /// them and cannot say where it came from.
        /// </summary>
        public IReadOnlyList<int> Justifications => _justifications;

        public Belief(string predicate, IReadOnlyList<string> args, double confidence)
        {
            Predicate = predicate;
            Args = args ?? new List<string>();
            Confidence = confidence;
        }

        public string Key => BeliefKey.Of(Predicate, Args);

        internal void AddJustification(int traceId)
        {
            if (!_justifications.Contains(traceId)) _justifications.Add(traceId);
        }

        public override string ToString() => $"{Key}={Confidence:0.00}";
    }

    /// <summary>
    /// One person's picture of how things are. Nothing here is checked against
    /// the world; two people can hold flatly contradictory beliefs and the store
    /// will never reconcile them, because people do not reconcile them either.
    /// </summary>
    public sealed class BeliefStore
    {
        readonly Dictionary<string, Belief> _beliefs = new Dictionary<string, Belief>(StringComparer.Ordinal);

        public IEnumerable<Belief> All => _beliefs.Values.OrderBy(b => b.Key, StringComparer.Ordinal);

        public void Seed(BeliefSeed seed)
        {
            if (seed?.Predicate == null) return;
            _beliefs[seed.Key] = new Belief(seed.Predicate, seed.Args, seed.Confidence);
        }

        public Belief Get(string predicate, params string[] args)
            => Get(predicate, (IReadOnlyList<string>)args);

        public Belief Get(string predicate, IReadOnlyList<string> args)
            => _beliefs.TryGetValue(BeliefKey.Of(predicate, args), out var b)
                ? b
                : new Belief(predicate, args, 0.0);

        public double Confidence(string predicate, params string[] args)
            => Confidence(predicate, (IReadOnlyList<string>)args);

        public double Confidence(string predicate, IReadOnlyList<string> args)
            => _beliefs.TryGetValue(BeliefKey.Of(predicate, args), out var b) ? b.Confidence : 0.0;

        public double ConfidenceByKey(string key)
            => key != null && _beliefs.TryGetValue(key, out var b) ? b.Confidence : 0.0;

        /// <summary>
        /// Moves a belief on the strength of one experience, and records which
        /// experience did it, so the belief can always be asked to explain itself.
        /// </summary>
        public double Nudge(string predicate, IReadOnlyList<string> args, double delta, int justificationTraceId)
        {
            var key = BeliefKey.Of(predicate, args);
            if (!_beliefs.TryGetValue(key, out var b))
            {
                b = new Belief(predicate, args, 0.0);
                _beliefs[key] = b;
            }

            b.Confidence = Accumulate.Toward(b.Confidence, delta);
            b.AddJustification(justificationTraceId);
            return b.Confidence;
        }
    }
}
