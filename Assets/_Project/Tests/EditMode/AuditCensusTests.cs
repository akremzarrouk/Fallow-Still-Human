using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// System understanding audit, 2026-09-17: what actually fires when the shipped
    /// rules run. Read-only. It runs the backstory once and the fifty standard
    /// mornings (five design conditions, seeds 1 to 10), and counts, from the trace
    /// and from the decision hook, which rules, readings, feelings, beliefs, wants,
    /// proposals and costs are exercised at all. It changes nothing and asserts
    /// nothing about behaviour. Writes Docs/audit/census.md.
    /// </summary>
    public class AuditCensusTests
    {
        const int Seeds = 10;

        sealed class Tally
        {
            readonly Dictionary<string, int> _n = new Dictionary<string, int>(StringComparer.Ordinal);
            public void Add(string key, int by = 1) { _n.TryGetValue(key ?? "(null)", out var v); _n[key ?? "(null)"] = v + by; }
            public int this[string key] => _n.TryGetValue(key, out var v) ? v : 0;
            public int Total => _n.Values.Sum();
            public IEnumerable<KeyValuePair<string, int>> Desc => _n.OrderByDescending(k => k.Value).ThenBy(k => k.Key, StringComparer.Ordinal);
            public string Line(int take = 1000) => _n.Count == 0 ? "none" : string.Join(", ", Desc.Take(take).Select(k => "`" + k.Key + "` " + k.Value));
        }

        static string P(double part, double whole) => whole == 0 ? "n/a" : (100.0 * part / whole).ToString("0.0", CultureInfo.InvariantCulture) + " %";

        static IEnumerable<string> Split(string s, string sep) => s == null ? Enumerable.Empty<string>() : s.Split(new[] { sep }, StringSplitOptions.RemoveEmptyEntries).Select(x => x.Trim());

        /// <summary>Everything countable in one trace, independent of how the events got there.</summary>
        static void CountTrace(TraceLog trace, Tally kinds, Tally access, Tally interpMatched, Tally interpWon, Tally meaningsBySource,
            Tally appraisalRules, Tally emotionsStirred, Tally nudges, Tally authoredBeliefs, Tally motiveRules, Tally consequences)
        {
            foreach (var r in trace.All)
            {
                kinds.Add(r.Kind.ToString());
                switch (r.Kind)
                {
                    case TraceKind.Access:
                        if (r.EventId != null) access.Add(r.Summary);
                        break;
                    case TraceKind.Interpretation:
                        if (r.Data.TryGetValue("source", out var src) && src == "own intention")
                        {
                            interpWon.Add("(own intention) " + r.Data["meaning"]);
                            break;
                        }
                        foreach (var c in Split(r.Data.TryGetValue("rules", out var rules) ? rules : null, " | "))
                            interpMatched.Add(c.Split(' ')[0]);
                        if (r.Data.TryGetValue("rules", out var won))
                        {
                            var meaning = r.Data["meaning"];
                            var winner = Split(won, " | ")
                                .Select(c => c.Split(' '))
                                .Where(p => p.Length >= 4 && p[2] == meaning)
                                .Select(p => p[0]).ToList();
                            foreach (var w in winner) interpWon.Add(w);
                        }
                        else interpWon.Add("(no rule matched) " + r.Data["meaning"]);
                        break;
                    case TraceKind.Experience:
                        meaningsBySource.Add(r.Data["source"] + ": " + r.Data["meaning"]);
                        break;
                    case TraceKind.Appraisal:
                        foreach (var c in Split(r.Data.TryGetValue("rules", out var ar) ? ar : null, " | ")) appraisalRules.Add(c.Split(' ')[0]);
                        emotionsStirred.Add(r.Data["emotion"]);
                        break;
                    case TraceKind.BeliefChange:
                        if (r.Data.TryGetValue("rule", out var rule)) nudges.Add(rule);
                        else if (r.Data.ContainsKey("delta") && !r.Summary.Contains("an experiment")) authoredBeliefs.Add(r.Summary.Split(' ')[0]);
                        break;
                    case TraceKind.Motive:
                        foreach (var id in Split(r.Data["rules"], ", ")) motiveRules.Add(id);
                        break;
                    case TraceKind.Consequence:
                        consequences.Add(r.Summary.StartsWith("hunger") ? "hunger changed by eating" :
                                         r.Summary.StartsWith("could not sit") ? "could not sit with (they had gone)" :
                                         r.Summary.StartsWith("was settled") ? "was settled by somebody (Soothe)" : r.Summary);
                        break;
                }
            }
        }

        [Test, Timeout(1800000)]
        public void Census()
        {
            var content = Scenario001Content.Load(TestPaths.DataRoot);
            var variants = content.Morning.Variants.Select(v => v.Id).ToList();
            var sb = new StringBuilder();
            sb.AppendLine("# Audit census: what actually fires on the shipped rules");
            sb.AppendLine();
            sb.AppendLine("Generated by `AuditCensusTests` for the system understanding audit (2026-09-17). Read-only: nothing in `Fallow.Core` or the data was changed. Shipped rules as loaded (`dispositions` " + content.Rules.Deciding.Dispositions + ", `means` " + content.Rules.Deciding.Means + "; scripted events untimed).");
            sb.AppendLine();

            // ---------------- the backstory ----------------
            {
                var sim = new Simulation(content.Cast, content.Rules);
                sim.Run(content.Backstory);
                Tally kinds = new Tally(), access = new Tally(), matched = new Tally(), won = new Tally(), bySource = new Tally(),
                    appraisal = new Tally(), stirred = new Tally(), nudges = new Tally(), authored = new Tally(), motives = new Tally(), cons = new Tally();
                CountTrace(sim.Trace, kinds, access, matched, won, bySource, appraisal, stirred, nudges, authored, motives, cons);

                sb.AppendLine("## 1. The backstory (12 authored events, days 1 to 4, run through `Simulation.Run`)");
                sb.AppendLine();
                sb.AppendLine("- Trace records by kind: " + kinds.Line());
                sb.AppendLine("- Access: " + access.Line());
                sb.AppendLine("- Interpretation rules that matched an event: " + matched.Line());
                sb.AppendLine("- Interpretation rules that won (or how a meaning was reached): " + won.Line());
                sb.AppendLine("- Memories kept, by source and meaning: " + bySource.Line());
                sb.AppendLine("- Appraisal rules that fired: " + appraisal.Line());
                sb.AppendLine("- Feelings stirred: " + stirred.Line());
                sb.AppendLine("- Belief nudge rules that fired: " + nudges.Line());
                sb.AppendLine("- Authored belief effects applied: " + authored.Line());
                sb.AppendLine("- Interpretation rules never matched in the backstory: " + string.Join(", ", content.Rules.Interpretation.Select(r => r.Id).Where(id => matched[id] == 0).Select(id => "`" + id + "`")));
                sb.AppendLine("- Appraisal rules never fired in the backstory: " + string.Join(", ", content.Rules.Appraisal.Select(r => r.Id).Where(id => appraisal[id] == 0).Select(id => "`" + id + "`")));
                sb.AppendLine();

                sb.AppendLine("Beliefs held at the end of the backstory, by where they came from:");
                sb.AppendLine();
                sb.AppendLine("| Who | Belief | Confidence | Justifications | Source |");
                sb.AppendLine("|---|---|---|---|---|");
                foreach (var id in content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal))
                foreach (var b in sim.Minds[id].Beliefs.All)
                {
                    var seeded = content.Cast[id].InitialBeliefs.Any(s => s.Key == b.Key);
                    var byRule = b.Justifications.Any(j => sim.Trace.All.Any(t => t.Kind == TraceKind.BeliefChange && t.ParentIds.Contains(j) && t.Data.ContainsKey("rule")));
                    var source = b.Justifications.Count == 0 ? "authored seed only" : (seeded ? "seed, then moved" : "formed during the run") + (byRule ? " (by rule)" : " (by authored effect)");
                    sb.AppendLine("| " + id + " | `" + b.Key + "` | " + b.Confidence.ToString("0.00", CultureInfo.InvariantCulture) + " | " + b.Justifications.Count + " | " + source + " |");
                }
                sb.AppendLine();
            }

            // ---------------- the mornings ----------------
            Tally mKinds = new Tally(), mAccess = new Tally(), mMatched = new Tally(), mWon = new Tally(), mBySource = new Tally(),
                mAppraisal = new Tally(), mStirred = new Tally(), mNudges = new Tally(), mAuthored = new Tally(), mMotiveRules = new Tally(), mCons = new Tally();
            Tally eventsByAction = new Tally(), eventsOverheard = new Tally();
            Tally chosen = new Tally(), available = new Tally(), resolution = new Tally(), commitment = new Tally(), why = new Tally();
            Tally proposalCredited = new Tally(), proposalCreditedChosen = new Tally(), costApplied = new Tally(), costChosen = new Tally();
            Tally wantRaised = new Tally(), wantStanding = new Tally(), termKinds = new Tally(), beliefTermsInWants = new Tally(), ledgerTermsInWants = new Tally();
            Tally memoryDrewOn = new Tally(), emotionsCarriedAtDecisions = new Tally(), leadingWant = new Tally();
            var decisions = 0; var unled = 0; var wantsNoOutlet = 0; var wantsTotal = 0; var oldDayMemories = 0; var todayMemories = 0;
            var costPriceBeliefTerms = new Tally(); var costPriceEmotionTerms = new Tally();
            Tally ownActReadings = new Tally(), selfDirected = new Tally(), ownActBeliefs = new Tally();

            foreach (var v in variants)
            for (ulong seed = 1; seed <= (ulong)Seeds; seed++)
            {
                var run = Scenario001.Prepare(content, v, seed);
                run.Morning.Decided = m =>
                {
                    decisions++;
                    var d = m.Decision;
                    why.Add(m.Why);
                    chosen.Add(d.Chosen.KindName);
                    resolution.Add(d.Resolution.ToString());
                    commitment.Add(d.Commitment);
                    leadingWant.Add(d.Leading?.Name ?? "(nothing pressing)");
                    if (d.Leading == null) unled++;
                    foreach (var r in d.Ranked)
                    {
                        available.Add(r.Option.KindName);
                        foreach (var c in r.Contributions.Where(c => c.Amount != 0.0).Select(c => c.ProposalId).Distinct()) proposalCredited.Add(c);
                        foreach (var price in r.Prices) costApplied.Add(price.Split(' ')[0]);
                    }
                    var picked = d.ChosenScored;
                    foreach (var c in picked.Contributions.Where(c => c.Amount != 0.0).Select(c => c.ProposalId).Distinct()) proposalCreditedChosen.Add(c);
                    foreach (var price in picked.Prices) costChosen.Add(price.Split(' ')[0]);

                    var credited = new HashSet<string>(d.Ranked.SelectMany(r => r.Contributions).Where(c => c.Amount > 0).Select(c => c.MotiveKey), StringComparer.Ordinal);
                    var today = m.Percept == null ? content.Morning.Day : content.Morning.Day;
                    foreach (var x in m.Mind.Experiences) { if (x.Day == today) todayMemories++; else oldDayMemories++; }
                    foreach (var e in m.Mind.Emotions.Live) emotionsCarriedAtDecisions.Add(e.Type);

                    foreach (var w in m.Motives)
                    {
                        wantsTotal++;
                        wantRaised.Add(w.Name);
                        if (!credited.Contains(w.Key)) wantsNoOutlet++;
                        var moving = w.Terms.Where(t => t.Amount != 0.0).ToList();
                        if (moving.Count > 0 && moving.All(t => t.Kind == ScalerKind.Trait || t.Kind == ScalerKind.Value || t.Kind == ScalerKind.Perceptiveness))
                            wantStanding.Add(w.Name);
                        foreach (var t in moving)
                        {
                            termKinds.Add(t.Kind ?? "(none)");
                            if (t.Kind == ScalerKind.Belief) beliefTermsInWants.Add(t.Description.Split(' ')[1]);
                            if (t.Kind == ScalerKind.Ledger) ledgerTermsInWants.Add(t.Description);
                            if (t.Kind == ScalerKind.Memory)
                                foreach (var id in t.Drew)
                                {
                                    var x = m.Mind.Experiences.FirstOrDefault(e => e.TraceId == id);
                                    if (x != null) memoryDrewOn.Add((x.Minute < 0 ? "no minute: " : "timed: ") + x.EventId.Split('-')[0] + " as " + x.Meaning);
                                }
                        }
                    }
                };
                run.Morning.Run(content.Morning.Minutes);

                CountTrace(run.Trace, mKinds, mAccess, mMatched, mWon, mBySource, mAppraisal, mStirred, mNudges, mAuthored, mMotiveRules, mCons);
                var byId = new Dictionary<string, WorldEvent>(StringComparer.Ordinal);
                foreach (var e in run.Result.Events)
                {
                    byId[e.Id] = e;
                    eventsByAction.Add(e.Action ?? e.Act);
                    if (e.Overhearers.Count > 0) eventsOverheard.Add(e.Action ?? e.Act);
                }
                foreach (var r in run.Trace.All)
                {
                    if (r.EventId == null || r.CharacterId == null || !byId.TryGetValue(r.EventId, out var ev)) continue;
                    var own = string.Equals(ev.ActorId, r.CharacterId, StringComparison.Ordinal);
                    if (r.Kind == TraceKind.Experience && own) ownActReadings.Add(ev.Action + " read by its own actor as " + r.Data["meaning"]);
                    if (r.Kind == TraceKind.Appraisal && r.Data.TryGetValue("toward", out var toward) && toward == r.CharacterId)
                        selfDirected.Add(r.Data["emotion"] + " toward themselves, on " + ev.Action);
                    if (r.Kind == TraceKind.BeliefChange && own && r.Data.TryGetValue("rule", out var nudge))
                        ownActBeliefs.Add(nudge + " on their own " + ev.Action + ": " + r.Summary.Split(' ')[0]);
                }
            }

            foreach (var c in content.Rules.Costs)
            foreach (var s in c.ScaledBy ?? new List<Scaler>())
            {
                if (s.Kind == ScalerKind.Belief) costPriceBeliefTerms.Add(c.Id + " reads " + s.Predicate);
                if (s.Kind == ScalerKind.Emotion) costPriceEmotionTerms.Add(c.Id + " reads " + s.Name);
            }

            sb.AppendLine("## 2. The fifty mornings (five design conditions, seeds 1 to " + Seeds + ")");
            sb.AppendLine();
            sb.AppendLine("Each run also re-runs the backstory, the night and the opening, so the trace counts below include them fifty times over.");
            sb.AppendLine();
            sb.AppendLine("### Events the morning itself produced");
            sb.AppendLine();
            sb.AppendLine("- By action: " + eventsByAction.Line());
            sb.AppendLine("- Of those, with at least one overhearer: " + eventsOverheard.Line());
            sb.AppendLine("- How the person who did a morning act read their own act (morning acts carry no intent): " + ownActReadings.Line());
            sb.AppendLine("- Feelings stirred toward the person feeling them: " + selfDirected.Line());
            sb.AppendLine("- Beliefs a person moved about themselves from their own act (key names the belief as written): " + ownActBeliefs.Line());
            sb.AppendLine();
            sb.AppendLine("### Perception, reading, memory, feeling, belief (whole trace)");
            sb.AppendLine();
            sb.AppendLine("- Trace records by kind: " + mKinds.Line());
            sb.AppendLine("- Access: " + mAccess.Line());
            sb.AppendLine("- Interpretation rules that matched: " + mMatched.Line());
            sb.AppendLine("- Interpretation rules that won, or how a meaning was reached: " + mWon.Line());
            sb.AppendLine("- Interpretation rules that never matched anything: " + string.Join(", ", content.Rules.Interpretation.Select(r => r.Id).Where(id => mMatched[id] == 0).Select(id => "`" + id + "`")));
            sb.AppendLine("- Interpretation rules that matched but never won: " + string.Join(", ", content.Rules.Interpretation.Select(r => r.Id).Where(id => mMatched[id] > 0 && mWon[id] == 0).Select(id => "`" + id + "` (" + mMatched[id] + ")")));
            sb.AppendLine("- Memories kept, by source and meaning: " + mBySource.Line());
            sb.AppendLine("- Appraisal rules that fired: " + mAppraisal.Line());
            sb.AppendLine("- Appraisal rules that never fired: " + string.Join(", ", content.Rules.Appraisal.Select(r => r.Id).Where(id => mAppraisal[id] == 0).Select(id => "`" + id + "`")));
            sb.AppendLine("- Feelings stirred: " + mStirred.Line());
            sb.AppendLine("- Belief nudge rules that fired: " + mNudges.Line());
            sb.AppendLine("- Belief nudge rules that never fired: " + string.Join(", ", content.Rules.BeliefNudges.Select(r => r.Id).Where(id => mNudges[id] == 0).Select(id => "`" + id + "`")));
            sb.AppendLine("- Authored belief effects applied: " + mAuthored.Line());
            sb.AppendLine("- World consequences: " + mCons.Line());
            sb.AppendLine();
            sb.AppendLine("### Deciding (" + decisions + " decisions, from the decision hook)");
            sb.AppendLine();
            sb.AppendLine("- Why they were deciding: " + why.Line());
            sb.AppendLine("- Chosen: " + chosen.Line());
            sb.AppendLine("- Options that were available at all, summed over decisions: " + available.Line());
            sb.AppendLine("- Resolution: " + resolution.Line());
            sb.AppendLine("- Intention brought in: " + commitment.Line());
            sb.AppendLine("- Want that added most to what was chosen: " + leadingWant.Line());
            sb.AppendLine("- Decisions led by no want: " + unled + " of " + decisions);
            sb.AppendLine("- Wants raised: " + wantsTotal + "; by want: " + wantRaised.Line());
            sb.AppendLine("- Wants raised with **only** trait, value or perceptiveness terms moving them (standing wants): " + wantStanding.Total + " (" + P(wantStanding.Total, wantsTotal) + "); by want: " + wantStanding.Line());
            sb.AppendLine("- Wants raised that no available option served at all: " + wantsNoOutlet + " (" + P(wantsNoOutlet, wantsTotal) + ")");
            sb.AppendLine("- Motivation rules that raised something: " + mMotiveRules.Line());
            sb.AppendLine("- Non-zero terms inside wants, by kind: " + termKinds.Line());
            sb.AppendLine("- Belief terms inside wants, by belief: " + beliefTermsInWants.Line());
            sb.AppendLine("- Ledger terms inside wants: " + ledgerTermsInWants.Line());
            sb.AppendLine("- What memory terms inside wants drew on: " + memoryDrewOn.Line(12));
            sb.AppendLine("- Memories held at decisions: from the day being lived " + todayMemories + ", from earlier days " + oldDayMemories + " (" + P(oldDayMemories, todayMemories + oldDayMemories) + " unreachable by recall)");
            sb.AppendLine("- Feelings being carried at decisions (instances): " + mStirred.Total + " stirred in all; carried at decisions by type: " + emotionsCarriedAtDecisions.Line());
            sb.AppendLine("- Proposals that credited any option: " + proposalCredited.Line());
            sb.AppendLine("- Proposals that credited the chosen option: " + proposalCreditedChosen.Line());
            sb.AppendLine("- Proposals that never credited anything: " + string.Join(", ", content.Rules.Proposals.Select(r => r.Id).Where(id => proposalCredited[id] == 0).Select(id => "`" + id + "`")));
            sb.AppendLine("- Cost rules applied to any option: " + costApplied.Line());
            sb.AppendLine("- Cost rules applied to the chosen option: " + costChosen.Line());
            sb.AppendLine("- Cost rules that read a belief or a feeling: " + costPriceBeliefTerms.Line() + "; " + costPriceEmotionTerms.Line());
            sb.AppendLine();

            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "audit");
            Directory.CreateDirectory(dir);
            File.WriteAllText(Path.Combine(dir, "census.md"), sb.ToString());
            TestContext.WriteLine(sb.ToString());
        }
    }
}
