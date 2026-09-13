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

    /// <summary>
    /// What somebody set out to do, and for which want, when getting it done
    /// takes more than one act.
    ///
    /// The only act in this slice that is a means rather than an end is walking
    /// somewhere, so an intention outlives an act only across a walk. It is not a
    /// plan: nothing is searched for and nothing is sequenced. It is the memory
    /// of why you came, carried into the one decision you take when you arrive.
    /// </summary>
    public sealed class Intention
    {
        public string MotiveKey { get; }
        public string MotiveName { get; }

        /// <summary>The act that set out on it.</summary>
        public ActionOption SetOutWith { get; }

        public int FormedAt { get; }

        /// <summary>The decision that formed it.</summary>
        public int TraceId { get; }

        public Intention(string motiveKey, string motiveName, ActionOption setOutWith, int formedAt, int traceId)
        {
            MotiveKey = motiveKey;
            MotiveName = motiveName;
            SetOutWith = setOutWith;
            FormedAt = formedAt;
            TraceId = traceId;
        }

        public override string ToString() => MotiveKey + " (set out at minute " + FormedAt + " with " + SetOutWith + ")";
    }

    /// <summary>What became of an intention somebody brought into a decision.</summary>
    public static class Commitment
    {
        /// <summary>Nothing was carried in.</summary>
        public const string None = "none";

        /// <summary>It still stands, and only what serves it was weighed.</summary>
        public const string Held = "held";

        /// <summary>The want behind it is no longer there.</summary>
        public const string NoLongerWanted = "lapsed: no longer wanted";

        /// <summary>Nothing that can be done from here serves it.</summary>
        public const string Impossible = "lapsed: nothing here serves it";

        /// <summary>The best way of serving it here costs more than it is worth.</summary>
        public const string NotWorthIt = "lapsed: not worth what it costs here";
    }

    /// <summary>What a person decided to do, and everything behind it.</summary>
    public sealed class Decision
    {
        public string CharacterId { get; }
        public ActionOption Chosen { get; }
        public IReadOnlyList<Motive> Motives { get; }

        /// <summary>Every option, scored, whether or not it was considered.</summary>
        public IReadOnlyList<ScoredOption> Ranked { get; }

        /// <summary>The options actually chosen among: all of them, or those serving an intention that held.</summary>
        public IReadOnlyList<ScoredOption> Considered { get; }

        public Resolution Resolution { get; }

        /// <summary>How far ahead the chosen option was of the next one considered.</summary>
        public double Margin { get; }

        /// <summary>The options that were too close to separate, when there were any.</summary>
        public IReadOnlyList<ActionOption> Tied { get; }

        /// <summary>The intention brought into this decision, if any, and what became of it.</summary>
        public Intention Holding { get; }
        public string Commitment { get; }

        /// <summary>The intention this decision leaves the person with: the want the chosen act was mostly for.</summary>
        public Intention Forms { get; internal set; }

        public int TraceId { get; internal set; }

        public Decision(
            string characterId, ActionOption chosen, IReadOnlyList<Motive> motives,
            IReadOnlyList<ScoredOption> ranked, Resolution resolution, double margin,
            IReadOnlyList<ActionOption> tied,
            IReadOnlyList<ScoredOption> considered = null, Intention holding = null, string commitment = null)
        {
            CharacterId = characterId;
            Chosen = chosen;
            Motives = motives ?? new List<Motive>();
            Ranked = ranked ?? new List<ScoredOption>();
            Considered = considered ?? Ranked;
            Resolution = resolution;
            Margin = margin;
            Tied = tied ?? new List<ActionOption>();
            Holding = holding;
            Commitment = commitment ?? Sim.Commitment.None;
        }

        /// <summary>What was chosen, with its arithmetic.</summary>
        public ScoredOption ChosenScored => Ranked.FirstOrDefault(r => r.Option.SameAs(Chosen));

        /// <summary>
        /// The want that added most to what was chosen. S1 took whichever want
        /// happened to be listed first, which was the most urgent want serving
        /// it rather than the one that contributed most.
        /// </summary>
        public Motive Leading
        {
            get
            {
                var top = ChosenScored;
                var biggest = top?.Contributions
                    .Where(c => c.Amount > 0.0)
                    .OrderByDescending(c => c.Amount)
                    .ThenBy(c => c.MotiveKey, StringComparer.Ordinal)
                    .FirstOrDefault();
                if (biggest == null) return null;
                return Motives.FirstOrDefault(m => string.Equals(m.Key, biggest.MotiveKey, StringComparison.Ordinal));
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
            int today, Rng rng, TraceLog trace, int parentTraceId, Intention holding = null)
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

            // Somebody who walked here for a reason weighs what serves that
            // reason, and nothing else, unless the reason has gone, cannot be
            // served from here, or is not worth what serving it would cost. No
            // option gets a bonus for being what was intended; the ones that do
            // not serve it are simply not what this person is deciding between.
            var considered = ranked;
            var commitment = Commitment.None;
            if (holding != null)
            {
                var serving = ranked
                    .Where(r => r.Contributions.Any(c => c.Amount > 0.0 &&
                                                         string.Equals(c.MotiveKey, holding.MotiveKey, StringComparison.Ordinal)))
                    .ToList();

                if (!motives.Any(m => string.Equals(m.Key, holding.MotiveKey, StringComparison.Ordinal)))
                    commitment = Commitment.NoLongerWanted;
                else if (serving.Count == 0)
                    commitment = Commitment.Impossible;
                else if (serving[0].Score <= 0.0)
                    commitment = Commitment.NotWorthIt;
                else
                {
                    commitment = Commitment.Held;
                    considered = serving;
                }
            }

            var top = considered[0];
            var band = considered.Where(s => top.Score - s.Score <= dyn.AmbiguityBand).ToList();
            var margin = considered.Count > 1 ? top.Score - considered[1].Score : top.Score;

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
                band.Count <= 1 ? new List<ActionOption>() : band.Select(b => b.Option).ToList(),
                considered, holding, commitment);

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
            if (holding != null)
            {
                data["intention"] = holding.MotiveKey + ", " + commitment;
                if (commitment == Commitment.Held && !ranked[0].Option.SameAs(picked.Option))
                    data["without_it"] = ranked[0].ToString();
            }

            var parents = motives.Select(m => m.TraceId).Concat(new[] { parentTraceId }).ToList();
            if (holding != null) parents.Add(holding.TraceId);

            decision.TraceId = trace.Add(
                TraceKind.Deliberation, mind.Id, null,
                (resolution == Resolution.Clear
                    ? "settled on " + picked.Option
                    : "had no real preference, and " + picked.Option + " is what happened"),
                parents,
                data);

            // What this leaves them intending. An intention that held and is
            // still being served goes on being the reason; otherwise it is the
            // want that added most to what was chosen.
            var leading = decision.Leading;
            if (commitment == Commitment.Held)
                decision.Forms = holding;
            else if (leading != null)
                decision.Forms = new Intention(leading.Key, leading.Name, picked.Option, percept.Minute, decision.TraceId);

            if (decision.Forms != null) data["intends"] = decision.Forms.MotiveKey;

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
