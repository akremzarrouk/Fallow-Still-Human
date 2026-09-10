using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Rules;

namespace Fallow.Core.Data
{
    /// <summary>
    /// Checks the rule files against the vocabulary. A rule with a misspelled
    /// reading or a misspelled trait would sit in the file looking like design
    /// while doing nothing at all, which is the worst kind of bug to have in a
    /// slice whose whole purpose is to judge whether the rules work.
    /// </summary>
    public static class RuleSetValidator
    {
        static readonly string[] EventTypeNames = { "speech", "action" };
        static readonly string[] RelationNames = { "self", "junior", "peer", "senior" };
        static readonly string[] AccessNames = { "witnessed", "overheard" };
        static readonly string[] AddressedNames = { "me", "group", "other", "nobody" };
        static readonly string[] Tokens = { "$actor", "$self", "$target" };

        public static IReadOnlyList<string> Validate(RuleSet rules, Vocabulary vocab)
        {
            var problems = new List<string>();
            var ids = new HashSet<string>();

            foreach (var r in rules.Interpretation)
            {
                var where = Where("interpretation", r.Id, ids, problems);
                if (!vocab.Contains("meanings", r.Label))
                    problems.Add($"{where}: '{r.Label}' is not a reading in the vocabulary");
                if (r.BaseWeight == 0.0 && (r.ScaledBy == null || r.ScaledBy.Count == 0))
                    problems.Add($"{where}: carries no weight at all, so it can never do anything");
                problems.AddRange(ValidateCondition(where, r.When, vocab, allowMeanings: false));
                problems.AddRange(ValidateScalers(where, r.ScaledBy, vocab));
            }

            foreach (var r in rules.BeliefNudges)
            {
                var where = Where("belief nudge", r.Id, ids, problems);
                if (r.Predicate == null || !vocab.BeliefPredicates.TryGetValue(r.Predicate, out var spec))
                {
                    problems.Add($"{where}: '{r.Predicate}' is not a belief predicate");
                }
                else
                {
                    if (r.Args.Count != spec.Arity)
                        problems.Add($"{where}: '{r.Predicate}' takes {spec.Arity} arguments, got {r.Args.Count}");
                    else
                        problems.AddRange(ValidateArgs(where, r.Predicate, r.Args, spec, vocab));
                }
                if (r.Delta == 0.0)
                    problems.Add($"{where}: moves the belief by nothing");
                problems.AddRange(ValidateCondition(where, r.When, vocab, allowMeanings: true));
                problems.AddRange(ValidateScalers(where, r.ScaledBy, vocab));
            }

            foreach (var r in rules.Appraisal)
            {
                var where = Where("appraisal", r.Id, ids, problems);
                if (!vocab.Contains("emotions", r.Emotion))
                    problems.Add($"{where}: '{r.Emotion}' is not an emotion in the vocabulary");
                if (string.IsNullOrEmpty(r.Concern))
                    problems.Add($"{where}: has no concern, so the feeling could never explain itself");
                else if (!vocab.Contains("values", r.Concern))
                    problems.Add($"{where}: concern '{r.Concern}' is not a value in the vocabulary");
                if (r.Target != null && !Tokens.Contains(r.Target))
                    problems.Add($"{where}: target '{r.Target}' must be a token such as $actor, or absent");
                if (r.BaseIntensity <= 0.0 && (r.ScaledBy == null || r.ScaledBy.Count == 0))
                    problems.Add($"{where}: produces no feeling at all");
                problems.AddRange(ValidateCondition(where, r.When, vocab, allowMeanings: true));
                problems.AddRange(ValidateScalers(where, r.ScaledBy, vocab));
            }

            return problems;
        }

        static string Where(string kind, string id, HashSet<string> ids, List<string> problems)
        {
            if (string.IsNullOrEmpty(id))
            {
                problems.Add($"a {kind} rule has no id");
                return $"{kind} rule <no id>";
            }
            if (!ids.Add(kind + ":" + id))
                problems.Add($"{kind} rule '{id}': duplicate id");
            return $"{kind} rule '{id}'";
        }

        static IEnumerable<string> ValidateCondition(string where, Condition c, Vocabulary vocab, bool allowMeanings)
        {
            if (c == null) yield break;

            foreach (var p in Names(where, "event_types", c.EventTypes, EventTypeNames)) yield return p;
            foreach (var p in Names(where, "actor_relations", c.ActorRelations, RelationNames)) yield return p;
            foreach (var p in Names(where, "access", c.Access, AccessNames)) yield return p;
            foreach (var p in Names(where, "addressed", c.Addressed, AddressedNames)) yield return p;
            foreach (var p in Set(where, "acts", c.Acts, "acts", vocab)) yield return p;
            foreach (var p in Set(where, "actions", c.Actions, "actions", vocab)) yield return p;
            foreach (var p in Set(where, "topics", c.Topics, "topics", vocab)) yield return p;
            foreach (var p in Set(where, "tones", c.Tones, "tones", vocab)) yield return p;
            foreach (var p in Set(where, "directness", c.Directness, "directness", vocab)) yield return p;
            foreach (var p in Set(where, "valences", c.Valences, "valences", vocab)) yield return p;
            foreach (var p in Set(where, "actor_roles", c.ActorRoles, "family_roles", vocab)) yield return p;
            foreach (var p in Set(where, "self_roles", c.SelfRoles, "family_roles", vocab)) yield return p;

            if (c.Meanings != null && c.Meanings.Count > 0)
            {
                if (!allowMeanings)
                    yield return $"{where}: cannot condition on a reading, because it is what produces one";
                foreach (var m in c.Meanings)
                    if (!vocab.IsMeaning(m))
                        yield return $"{where}: '{m}' is not a reading in the vocabulary";
            }

            if (c.AudienceMin.HasValue && c.AudienceMin.Value < 0)
                yield return $"{where}: audience_min cannot be negative";
        }

        static IEnumerable<string> Names(string where, string field, IReadOnlyList<string> given, string[] allowed)
        {
            if (given == null) yield break;
            foreach (var g in given)
                if (!allowed.Contains(g))
                    yield return $"{where}: {field} does not know '{g}'";
        }

        static IEnumerable<string> Set(string where, string field, IReadOnlyList<string> given, string setName, Vocabulary vocab)
        {
            if (given == null) yield break;
            foreach (var g in given)
                if (!vocab.Contains(setName, g))
                    yield return $"{where}: {field} names '{g}', which is not in '{setName}'";
        }

        static IEnumerable<string> ValidateScalers(string where, IReadOnlyList<Scaler> scalers, Vocabulary vocab)
        {
            if (scalers == null) yield break;

            foreach (var s in scalers)
            {
                if (s.Kind == null || !ScalerKind.All.Contains(s.Kind))
                {
                    yield return $"{where}: '{s.Kind}' is not a kind of scaler";
                    continue;
                }

                if (s.Factor == 0.0)
                    yield return $"{where}: scaler on {s.Describe()} has a factor of zero";

                switch (s.Kind)
                {
                    case ScalerKind.Trait:
                        if (!vocab.Contains("traits", s.Name))
                            yield return $"{where}: '{s.Name}' is not a trait";
                        break;
                    case ScalerKind.Value:
                        if (!vocab.Contains("values", s.Name))
                            yield return $"{where}: '{s.Name}' is not a value";
                        break;
                    case ScalerKind.Emotion:
                        if (!vocab.Contains("emotions", s.Name))
                            yield return $"{where}: '{s.Name}' is not an emotion";
                        if (s.Target != null && !Tokens.Contains(s.Target))
                            yield return $"{where}: emotion target '{s.Target}' must be a token such as $actor";
                        break;
                    case ScalerKind.Ledger:
                        if (!vocab.Contains("ledger_entries", s.Entry))
                            yield return $"{where}: '{s.Entry}' is not a ledger entry";
                        if (s.About == null || !Tokens.Contains(s.About))
                            yield return $"{where}: ledger scaler must be about a token such as $actor, got '{s.About}'";
                        break;
                    case ScalerKind.Belief:
                        if (s.Predicate == null || !vocab.BeliefPredicates.TryGetValue(s.Predicate, out var spec))
                        {
                            yield return $"{where}: '{s.Predicate}' is not a belief predicate";
                            break;
                        }
                        if (s.Args.Count != spec.Arity)
                        {
                            yield return $"{where}: belief '{s.Predicate}' takes {spec.Arity} arguments, got {s.Args.Count}";
                            break;
                        }
                        foreach (var p in ValidateArgs(where, s.Predicate, s.Args, spec, vocab)) yield return p;
                        break;
                }
            }
        }

        static IEnumerable<string> ValidateArgs(
            string where, string predicate, IReadOnlyList<string> args, BeliefPredicateSpec spec, Vocabulary vocab)
        {
            for (var i = 0; i < spec.Arity; i++)
            {
                var arg = args[i];
                var domain = spec.ArgDomains[i];

                if (domain == Vocabulary.CharacterDomain)
                {
                    if (!Tokens.Contains(arg))
                        yield return $"{where}: belief '{predicate}' argument {i + 1} must be a token such as $actor, got '{arg}'";
                    continue;
                }

                if (!vocab.Contains(domain, arg))
                    yield return $"{where}: belief '{predicate}' argument {i + 1} '{arg}' is not in '{domain}'";
            }
        }

        /// <summary>
        /// The rule that keeps the slice honest: no rule may mention a member of
        /// the cast. Rules describe kinds of people and kinds of moment. The
        /// moment one of them says a name, the model has stopped being a model.
        /// </summary>
        public static IReadOnlyList<string> ValidateNamesNobody(RuleSet rules, IEnumerable<string> castIds)
        {
            var problems = new List<string>();
            var names = new HashSet<string>(castIds);

            void Check(string where, string text)
            {
                if (text != null && names.Contains(text))
                    problems.Add($"{where}: names '{text}', a member of the cast");
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
                    Check(where, s.Predicate);
                    if (s.Args != null) foreach (var a in s.Args) Check(where, a);
                }
            }

            void CheckCondition(string where, Condition c)
            {
                if (c == null) return;
                foreach (var list in new[]
                         {
                             c.EventTypes, c.Acts, c.Actions, c.Topics, c.Tones, c.Directness,
                             c.Valences, c.ActorRelations, c.ActorRoles, c.SelfRoles, c.Access,
                             c.Meanings, c.Addressed
                         })
                {
                    if (list == null) continue;
                    foreach (var item in list) Check(where, item);
                }
            }

            foreach (var r in rules.Interpretation)
            {
                var where = $"interpretation rule '{r.Id}'";
                Check(where, r.Label);
                CheckCondition(where, r.When);
                CheckScalers(where, r.ScaledBy);
            }

            foreach (var r in rules.BeliefNudges)
            {
                var where = $"belief nudge '{r.Id}'";
                Check(where, r.Predicate);
                if (r.Args != null) foreach (var a in r.Args) Check(where, a);
                CheckCondition(where, r.When);
                CheckScalers(where, r.ScaledBy);
            }

            foreach (var r in rules.Appraisal)
            {
                var where = $"appraisal rule '{r.Id}'";
                Check(where, r.Emotion);
                Check(where, r.Concern);
                Check(where, r.Target);
                CheckCondition(where, r.When);
                CheckScalers(where, r.ScaledBy);
            }

            return problems;
        }
    }
}
