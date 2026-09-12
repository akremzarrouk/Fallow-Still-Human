using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;

namespace Fallow.Core.Data
{
    /// <summary>
    /// Checks the decision rules against the vocabulary and against the rules
    /// the architecture is supposed to guarantee.
    ///
    /// Two of these checks matter more than the spelling. A want that nothing
    /// can serve is dead weight that looks like design, and an action that no
    /// want can ask for can never happen however well it scores. Both are the
    /// kind of fault that leaves the file looking richer than the behaviour.
    /// </summary>
    public static class DecisionRuleValidator
    {
        public static IReadOnlyList<string> Validate(RuleSet rules, Vocabulary vocab)
        {
            var problems = new List<string>();
            var ids = new HashSet<string>();

            foreach (var r in rules.Motivation)
            {
                var where = Where("motivation", r.Id, ids, problems);

                if (!vocab.Contains("motives", r.Motive))
                    problems.Add(where + ": '" + r.Motive + "' is not a motive in the vocabulary");
                if (!MotiveScope.All.Contains(r.Scope))
                    problems.Add(where + ": '" + r.Scope + "' is not a scope");
                if (r.BaseUrgency == 0.0 && (r.ScaledBy == null || r.ScaledBy.Count == 0))
                    problems.Add(where + ": carries no urgency at all, so it can never raise anything");

                problems.AddRange(ValidateScalers(where, r.ScaledBy, vocab));
            }

            foreach (var r in rules.Proposals)
            {
                var where = Where("proposal", r.Id, ids, problems);

                if (!vocab.Contains("motives", r.Motive))
                    problems.Add(where + ": '" + r.Motive + "' is not a motive in the vocabulary");
                if (!ActionOption.AllNames.Contains(r.Action))
                    problems.Add(where + ": '" + r.Action + "' is not an action");
                if (!Targeting.All.Contains(r.Targeting))
                    problems.Add(where + ": '" + r.Targeting + "' is not a way of targeting");
                if (r.Fit <= 0.0)
                    problems.Add(where + ": fits the motive by nothing, so it would never be proposed");

                var needsTag = r.Targeting == Targeting.NearestTagged
                            || r.Targeting == Targeting.NearestUnsearched;
                if (needsTag && !vocab.Contains("room_tags", r.RoomTag))
                    problems.Add(where + ": '" + r.RoomTag + "' is not a kind of room");
                if (!needsTag && r.RoomTag != null)
                    problems.Add(where + ": names a kind of room but does not walk anywhere");

                if (needsTag || r.Targeting == Targeting.AwayFromHere)
                {
                    if (r.Action != "go_to")
                        problems.Add(where + ": only walking can be aimed at a room");
                }
                else if (r.Action == "go_to" && r.Targeting != Targeting.None)
                {
                    problems.Add(where + ": walking has to be aimed at a room, not a person");
                }
            }

            foreach (var r in rules.Costs)
            {
                var where = Where("cost", r.Id, ids, problems);

                if (!ActionOption.AllNames.Contains(r.Action))
                    problems.Add(where + ": '" + r.Action + "' is not an action");
                if (r.Base == 0.0 && (r.ScaledBy == null || r.ScaledBy.Count == 0))
                    problems.Add(where + ": costs nothing at all");

                problems.AddRange(ValidateScalers(where, r.ScaledBy, vocab));
            }

            foreach (var d in rules.Deciding.DistressShows)
                if (!vocab.Contains("emotions", d))
                    problems.Add("deciding: '" + d + "' is not an emotion");

            foreach (var d in rules.Deciding.ComfortSettles)
                if (!vocab.Contains("emotions", d))
                    problems.Add("deciding: '" + d + "' is not an emotion");

            foreach (var name in rules.Deciding.ActionMinutes.Keys)
                if (!ActionOption.AllNames.Contains(name))
                    problems.Add("deciding: '" + name + "' is not an action");

            if (rules.Deciding.AmbiguityBand < 0.0)
                problems.Add("deciding: the ambiguity band cannot be negative");

            problems.AddRange(NothingIsStranded(rules, vocab));
            return problems;
        }

        /// <summary>
        /// Nothing in the decision layer is allowed to be inert.
        ///
        /// Every want must have at least one way of being served, or it is a
        /// feeling with nowhere to go. Every action must be reachable from at
        /// least one want, or it is scenery. And no want should have exactly one
        /// way of being served across the whole file, because a want with a
        /// single action is not a want, it is that action under another name,
        /// which is the failure this architecture exists to avoid.
        /// </summary>
        public static IReadOnlyList<string> NothingIsStranded(RuleSet rules, Vocabulary vocab)
        {
            var problems = new List<string>();

            var wanted = new HashSet<string>(rules.Motivation.Select(m => m.Motive));
            var served = rules.Proposals
                .GroupBy(p => p.Motive)
                .ToDictionary(g => g.Key, g => g.Select(p => p.Action).Distinct().Count());

            foreach (var motive in wanted.OrderBy(m => m))
            {
                if (!served.TryGetValue(motive, out var ways) || ways == 0)
                    problems.Add("motive '" + motive + "' can never be acted on: no proposal serves it");
                else if (ways < 2)
                    problems.Add(
                        "motive '" + motive + "' has only one way to be served, " +
                        "which makes it a name for that action rather than a want");
            }

            foreach (var proposal in rules.Proposals)
                if (!wanted.Contains(proposal.Motive))
                    problems.Add(
                        "proposal '" + proposal.Id + "' serves '" + proposal.Motive +
                        "', which nothing ever raises");

            var reachable = new HashSet<string>(rules.Proposals.Select(p => p.Action));
            foreach (var action in ActionOption.AllNames)
                if (!reachable.Contains(action))
                    problems.Add("nothing can ever ask for '" + action + "', so it is scenery");

            return problems;
        }

        /// <summary>
        /// The same rule that keeps the event layer honest. No decision rule may
        /// mention a member of the cast, so that the difference between two
        /// people deciding differently is always the people and never the file.
        /// </summary>
        public static IReadOnlyList<string> ValidateNamesNobody(RuleSet rules, IEnumerable<string> castIds)
        {
            var problems = new List<string>();
            var names = new HashSet<string>(castIds);

            void Check(string where, string text)
            {
                if (text != null && names.Contains(text))
                    problems.Add(where + ": names '" + text + "', a member of the cast");
            }

            void CheckScalers(string where, IReadOnlyList<Scaler> scalers)
            {
                if (scalers == null) return;
                foreach (var s in scalers)
                {
                    Check(where, s.Name);
                    Check(where, s.Entry);
                    Check(where, s.About);
                    Check(where, s.Target);
                    Check(where, s.Topic);
                    Check(where, s.Predicate);
                    if (s.Args != null) foreach (var a in s.Args) Check(where, a);
                }
            }

            foreach (var r in rules.Motivation)
            {
                var where = "motivation rule '" + r.Id + "'";
                Check(where, r.Motive);
                CheckScalers(where, r.ScaledBy);
            }

            foreach (var r in rules.Proposals)
            {
                var where = "proposal rule '" + r.Id + "'";
                Check(where, r.Motive);
                Check(where, r.Action);
                Check(where, r.RoomTag);
            }

            foreach (var r in rules.Costs)
            {
                var where = "cost rule '" + r.Id + "'";
                Check(where, r.Action);
                CheckScalers(where, r.ScaledBy);
            }

            return problems;
        }

        static string Where(string kind, string id, HashSet<string> ids, List<string> problems)
        {
            if (string.IsNullOrEmpty(id))
            {
                problems.Add("a " + kind + " rule has no id");
                return kind + " rule <no id>";
            }
            if (!ids.Add(kind + ":" + id))
                problems.Add(kind + " rule '" + id + "': duplicate id");
            return kind + " rule '" + id + "'";
        }

        static IEnumerable<string> ValidateScalers(string where, IReadOnlyList<Scaler> scalers, Vocabulary vocab)
        {
            if (scalers == null) yield break;

            foreach (var s in scalers)
            {
                if (s.Kind == null || !ScalerKind.All.Contains(s.Kind))
                {
                    yield return where + ": '" + s.Kind + "' is not a kind of scaler";
                    continue;
                }

                if (s.Factor == 0.0)
                    yield return where + ": scaler on " + s.Describe() + " has a factor of zero";

                switch (s.Kind)
                {
                    case ScalerKind.Trait:
                        if (!vocab.Contains("traits", s.Name))
                            yield return where + ": '" + s.Name + "' is not a trait";
                        break;
                    case ScalerKind.Value:
                        if (!vocab.Contains("values", s.Name))
                            yield return where + ": '" + s.Name + "' is not a value";
                        break;
                    case ScalerKind.Emotion:
                        if (!vocab.Contains("emotions", s.Name))
                            yield return where + ": '" + s.Name + "' is not an emotion";
                        break;
                    case ScalerKind.Need:
                        if (!vocab.Contains("needs", s.Name))
                            yield return where + ": '" + s.Name + "' is not a need";
                        break;
                    case ScalerKind.Memory:
                        if (s.Name != null && !vocab.IsMeaning(s.Name))
                            yield return where + ": a memory of '" + s.Name + "' is not a reading";
                        if (s.Topic != null && !vocab.Contains("topics", s.Topic))
                            yield return where + ": '" + s.Topic + "' is not a topic";
                        break;
                    case ScalerKind.Ledger:
                        if (!vocab.Contains("ledger_entries", s.Entry))
                            yield return where + ": '" + s.Entry + "' is not a ledger entry";
                        break;
                    case ScalerKind.Belief:
                        if (s.Predicate == null || !vocab.BeliefPredicates.TryGetValue(s.Predicate, out var spec))
                        {
                            yield return where + ": '" + s.Predicate + "' is not a belief predicate";
                            break;
                        }
                        if (s.Args.Count != spec.Arity)
                            yield return where + ": belief '" + s.Predicate + "' takes " + spec.Arity +
                                         " arguments, got " + s.Args.Count;
                        break;
                }
            }
        }
    }
}
