using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>What one want added to one option, as it was actually calculated.</summary>
    public sealed class Contribution
    {
        public string MotiveKey { get; }
        public string MotiveName { get; }
        public double Urgency { get; }
        public double Fit { get; }
        public string ProposalId { get; }
        public int MotiveTraceId { get; }

        public double Amount => Urgency * Fit;

        public Contribution(string motiveKey, string motiveName, double urgency, double fit, string proposalId, int motiveTraceId)
        {
            MotiveKey = motiveKey;
            MotiveName = motiveName;
            Urgency = urgency;
            Fit = fit;
            ProposalId = proposalId;
            MotiveTraceId = motiveTraceId;
        }

        public override string ToString()
            => MotiveKey + " " + Amount.ToString("0.00") +
               " (urgency " + Urgency.ToString("0.00") + " x fit " + Fit.ToString("0.00") + ", " + ProposalId + ")";
    }

    /// <summary>One thing a person could do, everything for it, and everything against.</summary>
    public sealed class ScoredOption
    {
        public ActionOption Option { get; }

        /// <summary>Which wants this would serve, and by how much each.</summary>
        public IReadOnlyList<string> Serves { get; }

        /// <summary>The same, as numbers rather than words.</summary>
        public IReadOnlyList<Contribution> Contributions { get; }

        public double Appeal { get; }

        /// <summary>What it would cost this particular person, and why.</summary>
        public IReadOnlyList<string> Prices { get; }

        public double Cost { get; }

        public double Score => Appeal - Cost;

        /// <summary>The largest single thing any one want added.</summary>
        public double StrongestReason => Contributions.Count == 0 ? 0.0 : Contributions.Max(c => c.Amount);

        public ScoredOption(
            ActionOption option, IReadOnlyList<string> serves, double appeal,
            IReadOnlyList<string> prices, double cost, IReadOnlyList<Contribution> contributions = null)
        {
            Option = option;
            Serves = serves ?? new List<string>();
            Contributions = contributions ?? new List<Contribution>();
            Appeal = appeal;
            Prices = prices ?? new List<string>();
            Cost = cost;
        }

        public override string ToString()
            => Option + " " + Score.ToString("0.000") +
               " (for " + Appeal.ToString("0.00") + ", against " + Cost.ToString("0.00") + ")";
    }

    /// <summary>Whether the choice made itself, or had to be settled.</summary>
    public enum Resolution
    {
        /// <summary>One option was clearly ahead. Nothing random happened.</summary>
        Clear,

        /// <summary>Several were too close to call, and the seed settled it.</summary>
        Ambiguous
    }

    /// <summary>What a person decided to do, and everything behind it.</summary>
    public sealed class Decision
    {
        public string CharacterId { get; }
        public ActionOption Chosen { get; }
        public IReadOnlyList<Motive> Motives { get; }
        public IReadOnlyList<ScoredOption> Ranked { get; }
        public Resolution Resolution { get; }

        /// <summary>How far ahead the chosen option was of the next one.</summary>
        public double Margin { get; }

        /// <summary>The options that were too close to separate, when there were any.</summary>
        public IReadOnlyList<ActionOption> Tied { get; }

        public int TraceId { get; internal set; }

        public Decision(
            string characterId, ActionOption chosen, IReadOnlyList<Motive> motives,
            IReadOnlyList<ScoredOption> ranked, Resolution resolution, double margin,
            IReadOnlyList<ActionOption> tied)
        {
            CharacterId = characterId;
            Chosen = chosen;
            Motives = motives ?? new List<Motive>();
            Ranked = ranked ?? new List<ScoredOption>();
            Resolution = resolution;
            Margin = margin;
            Tied = tied ?? new List<ActionOption>();
        }

        /// <summary>The want that did most to produce this, for a one line account.</summary>
        public Motive Leading
        {
            get
            {
                var top = Ranked.FirstOrDefault(r => r.Option.SameAs(Chosen));
                if (top == null || top.Serves.Count == 0) return null;
                var name = top.Serves[0].Split(' ')[0];
                return Motives.FirstOrDefault(m => string.Equals(m.Key, name, StringComparison.Ordinal));
            }
        }
    }

    /// <summary>
    /// Chooses what to do now.
    ///
    /// Every option is worth the wants it serves and costs what it costs this
    /// person, and the best one wins. That is all the arithmetic there is: it
    /// exists so that plausible actions can be compared consistently, not
    /// because anyone believes a person is a sum.
    ///
    /// Randomness has exactly one job. When the top options are closer together
    /// than the ambiguity band, the difference between them is smaller than the
    /// precision of the weighing that produced it, so treating it as a
    /// preference would be false; the seed settles it instead, and the trace
    /// says so. Outside the band nothing random happens at all, which is why the
    /// same person in the same state does the same thing.
    /// </summary>
    public sealed class Deliberator
    {
        readonly RuleSet _rules;

        public Deliberator(RuleSet rules)
        {
            _rules = rules;
        }

        public Decision Decide(
            Mind mind, Percept percept, IReadOnlyList<Motive> motives,
            int today, Rng rng, TraceLog trace, int parentTraceId)
        {
            var dyn = _rules.Deciding;
            var available = ActionCatalog.Available(percept, dyn);

            var appeal = new Dictionary<string, double>(StringComparer.Ordinal);
            var serves = new Dictionary<string, List<string>>(StringComparer.Ordinal);
            var parts = new Dictionary<string, List<Contribution>>(StringComparer.Ordinal);
            var byKey = new Dictionary<string, ActionOption>(StringComparer.Ordinal);

            foreach (var option in available)
            {
                byKey[option.Key] = option;
                appeal[option.Key] = 0.0;
                serves[option.Key] = new List<string>();
                parts[option.Key] = new List<Contribution>();
            }

            foreach (var motive in motives)
            foreach (var proposal in _rules.Proposals)
            {
                if (!string.Equals(proposal.Motive, motive.Name, StringComparison.Ordinal)) continue;
                if (proposal.When != null && !proposal.When.Matches(percept)) continue;

                foreach (var option in ActionCatalog.Endorsed(proposal, motive, percept, available))
                {
                    var contribution = motive.Urgency * proposal.Fit;
                    if (contribution == 0.0) continue;

                    appeal[option.Key] += contribution;
                    parts[option.Key].Add(new Contribution(
                        motive.Key, motive.Name, motive.Urgency, proposal.Fit, proposal.Id, motive.TraceId));
                    serves[option.Key].Add(
                        motive.Key + " " + contribution.ToString("0.00") +
                        " (urgency " + motive.Urgency.ToString("0.00") +
                        " x fit " + proposal.Fit.ToString("0.00") + ", " + proposal.Id + ")");
                }
            }

            var scored = new List<ScoredOption>();
            foreach (var option in available)
            {
                var prices = new List<string>();
                var cost = PriceOf(option, mind, percept, today, prices);
                scored.Add(new ScoredOption(option, serves[option.Key], appeal[option.Key], prices, cost, parts[option.Key]));
            }

            var ranked = scored
                .OrderByDescending(s => s.Score)
                .ThenBy(s => s.Option.Key, StringComparer.Ordinal)
                .ToList();

            var top = ranked[0];
            var band = ranked.Where(s => top.Score - s.Score <= dyn.AmbiguityBand).ToList();
            var margin = ranked.Count > 1 ? top.Score - ranked[1].Score : top.Score;

            ScoredOption picked;
            Resolution resolution;

            if (band.Count <= 1)
            {
                picked = top;
                resolution = Resolution.Clear;
            }
            else
            {
                picked = PickWithin(band, top.Score, dyn.AmbiguityBand, rng);
                resolution = Resolution.Ambiguous;
            }

            var decision = new Decision(
                mind.Id, picked.Option, motives, ranked, resolution, margin,
                band.Count <= 1 ? new List<ActionOption>() : band.Select(b => b.Option).ToList());

            var data = new Dictionary<string, string>
            {
                { "chose", picked.Option.Key },
                { "score", picked.Score.ToString("0.000") },
                { "resolution", resolution == Resolution.Clear ? "clear" : "too close to call" },
                { "margin", margin.ToString("0.000") },
                { "options", string.Join(" | ", ranked.Take(6).Select(r => r.ToString())) },
                { "serves", string.Join("; ", picked.Serves) }
            };
            if (picked.Prices.Count > 0) data["against"] = string.Join("; ", picked.Prices);
            if (resolution == Resolution.Ambiguous)
                data["tied"] = string.Join(", ", band.Select(b => b.Option.Key));

            decision.TraceId = trace.Add(
                TraceKind.Deliberation, mind.Id, null,
                (resolution == Resolution.Clear
                    ? "settled on " + picked.Option
                    : "had no real preference, and " + picked.Option + " is what happened"),
                motives.Select(m => m.TraceId).Concat(new[] { parentTraceId }).ToList(),
                data);

            return decision;
        }

        double PriceOf(
            ActionOption option, Mind mind, Percept percept, int today, List<string> prices)
        {
            var ctx = new DecisionContext(
                percept, mind.Id, option.TargetId, today, _rules.Deciding.RecallHalfLife);
            var total = 0.0;

            foreach (var rule in _rules.Costs)
            {
                if (!string.Equals(rule.Action, option.KindName, StringComparison.Ordinal)) continue;
                if (rule.When != null && !rule.When.Matches(percept)) continue;

                var terms = ScalerEval.Evaluate(rule.ScaledBy, mind, ctx);
                var cost = rule.Base + terms.Sum(t => t.Amount);
                if (cost <= 0.0) continue;

                total += cost;
                prices.Add(terms.Count == 0
                    ? rule.Id + " " + cost.ToString("0.00")
                    : rule.Id + " " + cost.ToString("0.00") + " (" + string.Join("; ", terms) + ")");
            }

            return total;
        }

        /// <summary>
        /// Settles a choice nobody has a preference in. Weighted by how each
        /// option sits within the band, so the one at the top is still likeliest;
        /// this is a coin weighted by a difference too small to be called a
        /// reason, not a coin that ignores the scores.
        /// </summary>
        static ScoredOption PickWithin(IReadOnlyList<ScoredOption> band, double topScore, double width, Rng rng)
        {
            const double Floor = 1e-6;

            var weights = band.Select(b => Math.Max(Floor, b.Score - (topScore - width))).ToList();
            var total = weights.Sum();
            var roll = rng.NextDouble() * total;

            for (var i = 0; i < band.Count; i++)
            {
                roll -= weights[i];
                if (roll <= 0.0) return band[i];
            }

            return band[band.Count - 1];
        }
    }
}
