using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Tracing;

namespace Fallow.Core.Testing
{
    /// <summary>
    /// Takes every decision of a batch of mornings apart, to find out what is
    /// actually deciding them.
    ///
    /// Built for S1.2, before anything in deliberation was changed, so that each
    /// change can be measured against the same instrument. It watches decisions
    /// as they are taken and re-weighs copies of them with one thing altered;
    /// it never changes a run.
    /// </summary>
    public sealed class DeliberationAudit
    {
        public int Mornings;
        public int Decisions;

        bool _weighWants = true;

        public readonly Dictionary<string, int> ChosenKinds = new Dictionary<string, int>(StringComparer.Ordinal);
        public readonly Dictionary<string, int> Why = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Settled by the seed, and of those, between different kinds of action.</summary>
        public int Ambiguous;
        public int GenuineTies;

        /// <summary>The best-scoring option drew on two or more different wants.</summary>
        public int TopDrewOnSeveral;

        /// <summary>
        /// The kind of action that came top would have been a different kind if
        /// every option were worth only its strongest single reason.
        /// </summary>
        public int SummingDecidedTheKind;

        /// <summary>The top option was credited more than once by the same want.</summary>
        public int TopCountedOneWantTwice;

        /// <summary>Counting each want once per option would have put a different option on top.</summary>
        public int DoubleCountingDecided;

        /// <summary>The top option, aimed at nobody, was credited by the same kind of want about several people.</summary>
        public int TopCountedOneKindOfWantPerPerson;

        public int WaitOnTop;
        public double WaitWantsTotal;
        public readonly Dictionary<string, double> WaitAppealByProposal = new Dictionary<string, double>(StringComparer.Ordinal);

        public int ObserveOnTop;
        public readonly Dictionary<string, double> ObserveAppealByProposal = new Dictionary<string, double>(StringComparer.Ordinal);

        /// <summary>Wants raised, and how many of them no available option served at all.</summary>
        public int WantsRaised;
        public int WantsWithNowhereToGo;

        /// <summary>For each want: decisions it was present in, and how many it was decisive for.</summary>
        public readonly Dictionary<string, int> Present = new Dictionary<string, int>(StringComparer.Ordinal);
        public readonly Dictionary<string, int> Pivotal = new Dictionary<string, int>(StringComparer.Ordinal);

        public int Interruptions;

        /// <summary>Of those, how many thought again and carried on with the same thing.</summary>
        public int CarriedOn;

        /// <summary>Interruptions where the event itself stirred less than the threshold, and the standing feeling did the rest.</summary>
        public int InterruptedByWhatTheyAlreadyFelt;

        /// <summary>Walks taken for a want, and how many were followed by something that did not serve it.</summary>
        public int WalksWithAPurpose;
        public int Abandoned;
        public int WalkedStraightBack;

        public int WorstPacing;
        public string WorstPacingWho;
        public double PacingTotal;
        public int PacingSeries;

        public int MorningsAnyoneAte;

        public readonly Dictionary<string, int> DecisionsBy = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <param name="alsoWatch">
        /// Another instrument that wants to see every decision as it is taken, with
        /// the run it belongs to. Added in S1.5 so that where wants come from can be
        /// counted on exactly the decisions audited here.
        /// </param>
        public static DeliberationAudit Run(
            Scenario001Content content, IReadOnlyList<string> variants, int seeds, ulong firstSeed = 1, int? minutes = null,
            bool weighWants = true, Action<DecisionMoment, Scenario001Run> alsoWatch = null)
        {
            var audit = new DeliberationAudit { _weighWants = weighWants };
            foreach (var variant in variants)
            for (var i = 0; i < seeds; i++)
            {
                var seed = firstSeed + (ulong)i;
                var run = Scenario001.Prepare(content, variant, seed);
                var moments = new List<DecisionMoment>();
                run.Morning.Decided = m =>
                {
                    audit.Look(content, m, moments);
                    alsoWatch?.Invoke(m, run);
                };
                run.Morning.Run(minutes ?? content.Morning.Minutes);
                audit.Finish(content, run, variant + "/" + seed, moments);
            }
            return audit;
        }

        void Look(Scenario001Content content, DecisionMoment m, List<DecisionMoment> moments)
        {
            moments.Add(m);
            Decisions++;
            Bump(DecisionsBy, m.CharacterId);
            Bump(ChosenKinds, m.Decision.Chosen.KindName);
            Bump(Why, m.Why);

            var d = m.Decision;
            if (d.Resolution == Resolution.Ambiguous)
            {
                Ambiguous++;
                if (d.Tied.Select(t => t.KindName).Distinct(StringComparer.Ordinal).Count() > 1) GenuineTies++;
            }

            var top = d.Considered[0];
            var wants = top.Contributions.Select(c => c.MotiveKey).Distinct(StringComparer.Ordinal).Count();
            if (wants >= 2) TopDrewOnSeveral++;

            var byStrongest = d.Considered
                .OrderByDescending(r => r.StrongestReason - r.Cost)
                .ThenBy(r => r.Option.Key, StringComparer.Ordinal)
                .First();
            if (wants >= 2 && byStrongest.Option.KindName != top.Option.KindName) SummingDecidedTheKind++;

            if (top.Contributions.GroupBy(c => c.MotiveKey).Any(g => g.Count() > 1)) TopCountedOneWantTwice++;

            var onceEach = d.Considered
                .OrderByDescending(r => r.Contributions.GroupBy(c => c.MotiveKey).Sum(g => g.Max(c => c.Amount)) - r.Cost)
                .ThenBy(r => r.Option.Key, StringComparer.Ordinal)
                .First();
            if (onceEach.Option.Key != top.Option.Key) DoubleCountingDecided++;

            if (top.Option.TargetId == null &&
                top.Contributions.GroupBy(c => c.MotiveName).Any(g => g.Select(c => c.MotiveKey).Distinct().Count() > 1))
                TopCountedOneKindOfWantPerPerson++;

            if (top.Option.Kind == ActionKind.Wait)
            {
                WaitOnTop++;
                WaitWantsTotal += wants;
                foreach (var c in top.Contributions)
                {
                    WaitAppealByProposal.TryGetValue(c.ProposalId, out var v);
                    WaitAppealByProposal[c.ProposalId] = v + c.Amount;
                }
            }

            if (top.Option.Kind == ActionKind.Observe)
            {
                ObserveOnTop++;
                foreach (var c in top.Contributions)
                {
                    ObserveAppealByProposal.TryGetValue(c.ProposalId, out var v);
                    ObserveAppealByProposal[c.ProposalId] = v + c.Amount;
                }
            }

            var credited = new HashSet<string>(
                d.Ranked.SelectMany(r => r.Contributions).Where(c => c.Amount > 0).Select(c => c.MotiveKey),
                StringComparer.Ordinal);
            foreach (var motive in m.Motives)
            {
                WantsRaised++;
                if (!credited.Contains(motive.Key)) WantsWithNowhereToGo++;
            }

            // Which wants were decisive: weigh the same moment again without each
            // one, and see whether something else comes out on top. The top of
            // the ranking is compared, not the pick, so the seed plays no part.
            var deliberator = new Deliberator(content.Rules);
            foreach (var name in m.Motives.Select(x => x.Name).Distinct(StringComparer.Ordinal).Where(_ => _weighWants))
            {
                Bump(Present, name);
                var without = m.Motives.Where(x => x.Name != name).ToList();
                var again = deliberator.Decide(m.Mind, m.Percept, without, content.Morning.Day, new Rng(1), new TraceLog(), 0, d.Holding);
                if (again.Considered[0].Option.Key != d.Considered[0].Option.Key) Bump(Pivotal, name);
            }

            if (d.Holding != null)
            {
                Bump(Commitments, d.Commitment);
                Bump(CommitmentsByWant, d.Holding.MotiveName + ": " + d.Commitment);
                if (d.Commitment == Commitment.Held)
                {
                    if (!d.Ranked[0].Option.SameAs(d.Chosen)) IntentionOverruledTheRanking++;
                    var fullBand = d.Ranked.Where(r => d.Ranked[0].Score - r.Score <= content.Rules.Deciding.AmbiguityBand).ToList();
                    if (fullBand.Select(r => r.Option.KindName).Distinct(StringComparer.Ordinal).Count() > 1) HeldWhereTheFullRankingWasATie++;
                }
            }
        }

        /// <summary>Intentions brought into decisions, and what became of them.</summary>
        public readonly Dictionary<string, int> Commitments = new Dictionary<string, int>(StringComparer.Ordinal);
        public readonly Dictionary<string, int> CommitmentsByWant = new Dictionary<string, int>(StringComparer.Ordinal);

        /// <summary>Held intentions where something not serving the intention scored higher overall.</summary>
        public int IntentionOverruledTheRanking;

        /// <summary>Held intentions where the full ranking, ignoring the intention, would have gone to the seed between different kinds.</summary>
        public int HeldWhereTheFullRankingWasATie;

        void Finish(Scenario001Content content, Scenario001Run run, string label, List<DecisionMoment> moments)
        {
            Mornings++;

            Interruptions += run.Morning.Interruptions.Count;
            CarriedOn += run.Result.Actions.Count(a => a.Outcome == "thought again, and carried on");
            InterruptedByWhatTheyAlreadyFelt += run.Morning.Interruptions
                .Count(x => x.EventIntensity < content.Rules.Deciding.InterruptIntensity);

            foreach (var mine in moments.GroupBy(x => x.CharacterId))
            {
                var list = mine.ToList();
                for (var i = 0; i + 1 < list.Count; i++)
                {
                    var walk = list[i];
                    if (walk.Decision.Chosen.Kind != ActionKind.GoTo) continue;

                    var chosen = walk.Decision.Ranked.First(r => r.Option.SameAs(walk.Decision.Chosen));
                    var reason = chosen.Contributions.OrderByDescending(c => c.Amount).FirstOrDefault();
                    if (reason == null) continue;

                    var next = list[i + 1];
                    if (next.Why != "finished") continue;

                    WalksWithAPurpose++;
                    var then = next.Decision.Ranked.First(r => r.Option.SameAs(next.Decision.Chosen));
                    if (!then.Contributions.Any(c => c.MotiveKey == reason.MotiveKey)) Abandoned++;
                    if (next.Decision.Chosen.Kind == ActionKind.GoTo &&
                        next.Decision.Chosen.DestinationRoomId == walk.Percept.Room?.Id)
                        WalkedStraightBack++;
                }

                var moves = list.Where(x => x.Decision.Chosen.Kind == ActionKind.GoTo)
                    .Select(x => x.Decision.Chosen.DestinationRoomId).ToList();
                var pacing = 0;
                for (var i = 2; i < moves.Count; i++)
                    if (moves[i] == moves[i - 2] && moves[i] != moves[i - 1]) pacing++;

                PacingTotal += pacing;
                PacingSeries++;
                if (pacing > WorstPacing)
                {
                    WorstPacing = pacing;
                    WorstPacingWho = label + "/" + mine.Key;
                }
            }

            if (run.Result.Actions.Any(a => a.Action.Kind == ActionKind.Eat && a.Outcome != null && a.Outcome.StartsWith("ate", StringComparison.Ordinal)))
                MorningsAnyoneAte++;
        }

        static void Bump(Dictionary<string, int> d, string key)
        {
            d.TryGetValue(key ?? "", out var n);
            d[key ?? ""] = n + 1;
        }

        static string P(double part, double whole)
            => whole == 0 ? "n/a" : (part / whole).ToString("P1", CultureInfo.InvariantCulture);

        public string ToMarkdown()
        {
            var sb = new StringBuilder();
            sb.AppendLine(Mornings + " mornings, " + Decisions + " decisions (" +
                          (Decisions / (double)Math.Max(1, Mornings * 4)).ToString("0.0", CultureInfo.InvariantCulture) +
                          " per person per morning).");
            sb.AppendLine();

            sb.AppendLine("### What was chosen");
            sb.AppendLine();
            sb.AppendLine("| " + string.Join(" | ", ActionOption.AllNames) + " |");
            sb.AppendLine("|" + string.Join("|", ActionOption.AllNames.Select(_ => "---")) + "|");
            sb.AppendLine("| " + string.Join(" | ", ActionOption.AllNames.Select(n =>
                P(ChosenKinds.TryGetValue(n, out var c) ? c : 0, Decisions))) + " |");
            sb.AppendLine();
            sb.AppendLine("Why they were deciding: " + string.Join(", ", Why.OrderBy(k => k.Key, StringComparer.Ordinal)
                .Select(k => k.Key + " " + P(k.Value, Decisions))) + ".");
            sb.AppendLine();

            sb.AppendLine("### How appeal was put together");
            sb.AppendLine();
            sb.AppendLine("| Measure | Share of decisions |");
            sb.AppendLine("|---|---|");
            sb.AppendLine("| Settled by the seed | " + P(Ambiguous, Decisions) + " |");
            sb.AppendLine("| ... between different kinds of action | " + P(GenuineTies, Decisions) + " |");
            sb.AppendLine("| Top option drew on two or more wants | " + P(TopDrewOnSeveral, Decisions) + " |");
            sb.AppendLine("| Summing changed which kind of action came top (vs strongest single reason) | " + P(SummingDecidedTheKind, Decisions) + " |");
            sb.AppendLine("| Top option credited twice by one want | " + P(TopCountedOneWantTwice, Decisions) + " |");
            sb.AppendLine("| Counting each want once would have changed the top option | " + P(DoubleCountingDecided, Decisions) + " |");
            sb.AppendLine("| Top option, aimed at nobody, credited once per person by the same kind of want | " + P(TopCountedOneKindOfWantPerPerson, Decisions) + " |");
            sb.AppendLine("| Standing still on top | " + P(WaitOnTop, Decisions) + " |");
            sb.AppendLine();

            if (WaitOnTop > 0)
            {
                var total = WaitAppealByProposal.Values.Sum();
                sb.AppendLine("When standing still came top it drew on " +
                              (WaitWantsTotal / WaitOnTop).ToString("0.00", CultureInfo.InvariantCulture) +
                              " wants on average. Its appeal came from: " +
                              string.Join(", ", WaitAppealByProposal.OrderByDescending(k => k.Value)
                                  .Select(k => "`" + k.Key + "` " + P(k.Value, total))) + ".");
                sb.AppendLine();
            }

            if (ObserveOnTop > 0)
            {
                var total = ObserveAppealByProposal.Values.Sum();
                sb.AppendLine("Watching somebody came top in " + P(ObserveOnTop, Decisions) + " of decisions. Its appeal came from: " +
                              string.Join(", ", ObserveAppealByProposal.OrderByDescending(k => k.Value)
                                  .Select(k => "`" + k.Key + "` " + P(k.Value, total))) + ".");
                sb.AppendLine();
            }

            sb.AppendLine("Wants raised with no available option serving them at all: " + P(WantsWithNowhereToGo, WantsRaised) +
                          " of " + WantsRaised + ".");
            sb.AppendLine();

            sb.AppendLine("### Which wants decide anything");
            sb.AppendLine();
            sb.AppendLine("Each decision weighed again without one want. Decisive means a different option came top.");
            sb.AppendLine();
            sb.AppendLine("| Want | Present in | Decisive in | Share |");
            sb.AppendLine("|---|---|---|---|");
            foreach (var k in Present.OrderBy(k => k.Key, StringComparer.Ordinal))
            {
                Pivotal.TryGetValue(k.Key, out var piv);
                sb.AppendLine("| `" + k.Key + "` | " + k.Value + " | " + piv + " | " + P(piv, k.Value) + " |");
            }
            sb.AppendLine();

            sb.AppendLine("### Carrying things through");
            sb.AppendLine();
            sb.AppendLine("| Measure | Value |");
            sb.AppendLine("|---|---|");
            sb.AppendLine("| Interruptions per morning | " + (Interruptions / (double)Math.Max(1, Mornings)).ToString("0.00", CultureInfo.InvariantCulture) + " |");
            sb.AppendLine("| ... where the event itself stirred less than the threshold | " + P(InterruptedByWhatTheyAlreadyFelt, Interruptions) + " |");
            sb.AppendLine("| ... after which they thought again and carried on | " + P(CarriedOn, Interruptions) + " |");
            var brought = Commitments.Values.Sum();
            sb.AppendLine("| Decisions taken with an intention carried in | " + P(brought, Decisions) + " |");
            foreach (var k in Commitments.OrderBy(k => k.Key, StringComparer.Ordinal))
                sb.AppendLine("| ... " + k.Key + " | " + P(k.Value, brought) + " |");
            Commitments.TryGetValue(Commitment.Held, out var held);
            sb.AppendLine("| ... held, where something serving a different want scored higher overall | " + P(IntentionOverruledTheRanking, held) + " |");
            sb.AppendLine("| ... held, where ignoring the intention would have been a tie between different kinds | " + P(HeldWhereTheFullRankingWasATie, held) + " |");
            sb.AppendLine("| Walks completed and followed by a decision | " + WalksWithAPurpose + " |");
            sb.AppendLine("| ... followed by something the want behind the walk did not serve | " + P(Abandoned, WalksWithAPurpose) + " |");
            sb.AppendLine("| ... followed by walking straight back | " + P(WalkedStraightBack, WalksWithAPurpose) + " |");
            sb.AppendLine("| Back-and-forth pacing, mean per person per morning | " + (PacingTotal / Math.Max(1, PacingSeries)).ToString("0.00", CultureInfo.InvariantCulture) + " |");
            sb.AppendLine("| Worst pacing | " + WorstPacing + " (" + WorstPacingWho + ") |");
            sb.AppendLine("| Mornings anyone ate | " + MorningsAnyoneAte + " of " + Mornings + " |");

            if (CommitmentsByWant.Count > 0)
            {
                sb.AppendLine();
                sb.AppendLine("Intentions carried into a decision, by the want behind them: " +
                              string.Join(", ", CommitmentsByWant.OrderBy(k => k.Key, StringComparer.Ordinal)
                                  .Select(k => "`" + k.Key + "` " + k.Value)) + ".");
            }
            return sb.ToString();
        }
    }
}
