using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;

namespace Fallow.Core.Data
{
    /// <summary>
    /// Checks the event script against the vocabulary and the cast. The check
    /// that matters most is the last one: a ledger effect may only land on
    /// someone who was actually there. Authoring a memory for an absent
    /// character is how world truth leaks into a mind, so it fails here.
    /// </summary>
    public static class ScenarioValidator
    {
        public static IReadOnlyList<string> Validate(
            ScenarioScript script,
            Vocabulary vocab,
            IReadOnlyDictionary<string, Profile> cast)
        {
            var problems = new List<string>();
            var seenIds = new HashSet<string>();
            var lastOrder = int.MinValue;

            foreach (var id in script.CharacterIds)
                if (!cast.ContainsKey(id))
                    problems.Add($"scenario lists character '{id}', who has no character file");

            foreach (var e in script.Events)
            {
                var where = string.IsNullOrEmpty(e.Id) ? "<event with no id>" : e.Id;

                if (string.IsNullOrEmpty(e.Id)) problems.Add("an event has no id");
                else if (!seenIds.Add(e.Id)) problems.Add($"{where}: duplicate event id");

                if (e.Order <= lastOrder)
                    problems.Add($"{where}: order {e.Order} does not follow the previous event");
                lastOrder = e.Order;

                if (string.IsNullOrEmpty(e.Summary))
                    problems.Add($"{where}: no summary, so its traces will be unreadable");

                if (e.Kind == EventKind.Speech)
                {
                    if (!vocab.Contains("acts", e.Act))
                        problems.Add($"{where}: unknown act '{e.Act}'");
                    if (e.Action != null)
                        problems.Add($"{where}: a speech event must not also carry an action");
                    if (string.IsNullOrEmpty(e.ActorId))
                        problems.Add($"{where}: a speech event needs someone to say it");
                }
                else
                {
                    if (!vocab.Contains("actions", e.Action))
                        problems.Add($"{where}: unknown action '{e.Action}'");
                    if (e.Act != null)
                        problems.Add($"{where}: an action event must not also carry a speech act");
                }

                if (!vocab.Contains("topics", e.Topic)) problems.Add($"{where}: unknown topic '{e.Topic}'");
                if (!vocab.Contains("tones", e.Tone)) problems.Add($"{where}: unknown tone '{e.Tone}'");
                if (!vocab.Contains("directness", e.Directness)) problems.Add($"{where}: unknown directness '{e.Directness}'");
                if (!vocab.Contains("valences", e.Valence)) problems.Add($"{where}: unknown valence '{e.Valence}'");

                if (e.Intent != null && !vocab.Contains("self_meanings", e.Intent))
                    problems.Add($"{where}: unknown intent '{e.Intent}'");
                if (e.Intent != null && string.IsNullOrEmpty(e.ActorId))
                    problems.Add($"{where}: has an intent but nobody to hold it");

                if (e.ActorId != null && !cast.ContainsKey(e.ActorId))
                    problems.Add($"{where}: actor '{e.ActorId}' is not in the cast");
                if (e.TargetId != null && !e.TargetsEveryone && !cast.ContainsKey(e.TargetId))
                    problems.Add($"{where}: target '{e.TargetId}' is not in the cast");

                foreach (var w in e.Witnesses)
                {
                    if (!cast.ContainsKey(w)) problems.Add($"{where}: witness '{w}' is not in the cast");
                    if (e.Overhearers.Contains(w)) problems.Add($"{where}: '{w}' is listed as both witness and overhearer");
                }
                foreach (var o in e.Overhearers)
                {
                    if (!cast.ContainsKey(o)) problems.Add($"{where}: overhearer '{o}' is not in the cast");
                    if (o == e.ActorId) problems.Add($"{where}: the actor cannot merely overhear their own act");
                }

                foreach (var f in e.LedgerEffects)
                {
                    if (!cast.ContainsKey(f.HolderId))
                        problems.Add($"{where}: ledger effect holder '{f.HolderId}' is not in the cast");
                    if (!cast.ContainsKey(f.AboutId))
                        problems.Add($"{where}: ledger effect is about '{f.AboutId}', who is not in the cast");
                    if (!vocab.Contains("ledger_entries", f.Entry))
                        problems.Add($"{where}: unknown ledger entry '{f.Entry}'");
                    if (f.Weight <= 0.0 || f.Weight > 1.0)
                        problems.Add($"{where}: ledger effect '{f.Entry}' weight must be within 0..1, got {f.Weight}");
                    if (e.AccessFor(f.HolderId) == Access.None)
                        problems.Add($"{where}: would give '{f.HolderId}' a memory of an event they had no access to");
                }

                foreach (var f in e.BeliefEffects)
                {
                    if (!cast.ContainsKey(f.HolderId))
                        problems.Add($"{where}: belief effect holder '{f.HolderId}' is not in the cast");
                    if (f.Predicate == null || !vocab.BeliefPredicates.TryGetValue(f.Predicate, out var spec))
                    {
                        problems.Add($"{where}: unknown belief predicate '{f.Predicate}'");
                    }
                    else if (f.Args.Count != spec.Arity)
                    {
                        problems.Add($"{where}: belief '{f.Predicate}' takes {spec.Arity} arguments, got {f.Args.Count}");
                    }
                    else
                    {
                        for (var i = 0; i < spec.Arity; i++)
                        {
                            var domain = spec.ArgDomains[i];
                            if (domain == Vocabulary.CharacterDomain)
                            {
                                if (!cast.ContainsKey(f.Args[i]))
                                    problems.Add($"{where}: belief '{f.Key}' names '{f.Args[i]}', who is not in the cast");
                            }
                            else if (!vocab.Contains(domain, f.Args[i]))
                            {
                                problems.Add($"{where}: belief '{f.Key}' argument {i + 1} '{f.Args[i]}' is not in '{domain}'");
                            }
                        }
                    }
                    if (f.Delta == 0.0)
                        problems.Add($"{where}: belief effect on '{f.Key}' moves it by nothing");
                    if (e.AccessFor(f.HolderId) == Access.None)
                        problems.Add($"{where}: would give '{f.HolderId}' a belief from an event they had no access to");
                }
            }

            return problems;
        }
    }
}
