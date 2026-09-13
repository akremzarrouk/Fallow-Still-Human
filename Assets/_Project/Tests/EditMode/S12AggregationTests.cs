using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using Fallow.Core.Tracing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// S1.2: what an option is worth, and what it is not.
    ///
    /// Standing still is credited by two wants for what it avoids, eating and
    /// confronting anybody, which every other option that neither eats nor
    /// confronts avoids equally. That is a structural advantage and these tests
    /// prove it is exactly that. Removing it was tried (change C3) and rejected,
    /// because it is load-bearing: without it, wants that need nothing to have
    /// happened pour into sitting with somebody, and four people become two.
    /// The removal is kept here as a variant so the finding stays reproducible.
    /// </summary>
    public class S12AggregationTests
    {
        static Scenario001Content _content;
        static Scenario001Content _withoutCredit;

        static readonly string[] Crediting = { "leave_it_alone", "let_it_be" };
        static readonly SortedDictionary<string, string> _collapse = new SortedDictionary<string, string>(StringComparer.Ordinal);

        [OneTimeTearDown]
        public void Write()
        {
            if (_collapse.Count == 0) return;
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S1.2", "c3-rejected");
            Directory.CreateDirectory(dir);
            File.WriteAllText(Path.Combine(dir, "collapse.md"), string.Join(Environment.NewLine, _collapse.Values));
        }

        [OneTimeSetUp]
        public void Load()
        {
            _content = Scenario001Content.Load(TestPaths.DataRoot);
            _withoutCredit = new Scenario001Content(_content.Vocabulary, _content.Cast, _content.Backstory, _content.Morning,
                WithoutTheCredit(_content.Rules));
        }

        /// <summary>
        /// C3, as it was tried: the weight each want put on standing still for
        /// what it avoids is moved onto the acts it avoids, at the same weight.
        /// Which acts is taken from the event rules, where going through a room,
        /// watching somebody and eating when there is little left are the only
        /// acts of the morning anybody can read as a slight, a challenge or a threat.
        /// </summary>
        public static RuleSet WithoutTheCredit(RuleSet rules)
        {
            var proposals = rules.Proposals.Where(p => !Crediting.Contains(p.Id)).ToList();
            proposals.Add(new ProposalRule { Id = "leave_it_alone", Motive = "guard_supplies", Action = "eat", Targeting = Targeting.None, Fit = -0.3 });
            proposals.Add(new ProposalRule { Id = "let_it_be", Motive = "keep_peace", Action = "search_room", Targeting = Targeting.None, Fit = -0.5,
                When = new SituationCondition { OthersPresentMin = 1 } });
            proposals.Add(new ProposalRule { Id = "not_standing_there_watching_them", Motive = "keep_peace", Action = "observe", Targeting = Targeting.EachPresent, Fit = -0.5 });
            proposals.Add(new ProposalRule { Id = "not_taking_it_in_front_of_them", Motive = "keep_peace", Action = "eat", Targeting = Targeting.None, Fit = -0.5,
                When = new SituationCondition { OthersPresentMin = 1 } });

            return new RuleSet
            {
                Interpretation = rules.Interpretation,
                BeliefNudges = rules.BeliefNudges,
                Appraisal = rules.Appraisal,
                Dynamics = rules.Dynamics,
                Motivation = rules.Motivation,
                Proposals = proposals,
                Costs = rules.Costs,
                Deciding = rules.Deciding
            };
        }

        /// <summary>
        /// Every decision of one morning. Anything that weighs a decision again
        /// does it in <paramref name="atTheMoment"/>, while the mind is still in the
        /// state it decided in.
        /// </summary>
        static List<DecisionMoment> Moments(Scenario001Content content, string variant, ulong seed, Action<DecisionMoment> atTheMoment = null)
        {
            var run = Scenario001.Prepare(content, variant, seed);
            var moments = new List<DecisionMoment>();
            run.Morning.Decided = m => { moments.Add(m); atTheMoment?.Invoke(m); };
            run.Morning.Run(content.Morning.Minutes);
            return moments;
        }

        [Test]
        public void StandingStillsCreditIsExactlyAnAdvantageOverEverythingThatAlsoAvoidsTheAct()
        {
            var shipped = new Deliberator(_content.Rules);
            var moved = new Deliberator(_withoutCredit.Rules);
            var checkedOptions = 0;
            var advantaged = 0;

            foreach (var variant in new[] { "mara_ate_it", "daniel_ate_it", "elena_fed_mara" })
            Moments(_content, variant, 1, m =>
            {
                var with = shipped.Decide(m.Mind, m.Percept, m.Motives, _content.Morning.Day, new Rng(1), new TraceLog(), 0);
                var without = moved.Decide(m.Mind, m.Percept, m.Motives, _content.Morning.Day, new Rng(1), new TraceLog(), 0);

                var waitWith = with.Ranked.First(r => r.Option.Kind == ActionKind.Wait);
                var waitWithout = without.Ranked.First(r => r.Option.Kind == ActionKind.Wait);
                var credit = waitWith.Contributions.Where(c => Crediting.Contains(c.ProposalId)).Sum(c => c.Amount);

                Assert.AreEqual(waitWith.Score - credit, waitWithout.Score, 1e-9, "standing still differs by more than its credit");

                foreach (var option in without.Ranked.Where(r => r.Option.Kind != ActionKind.Wait))
                {
                    var was = with.Ranked.First(r => r.Option.SameAs(option.Option));
                    var against = option.Contributions.Where(c => c.Amount < 0).Sum(c => c.Amount);

                    // Relative to standing still, every option moves by the credit
                    // standing still loses, less whatever now counts against that
                    // option. Nothing else moves.
                    var shift = (option.Score - waitWithout.Score) - (was.Score - waitWith.Score);
                    Assert.AreEqual(credit + against, shift, 1e-9,
                        m.CharacterId + " at minute " + m.Minute + ", " + option.Option.Key);
                    checkedOptions++;
                    if (against == 0.0 && credit > 0.0) advantaged++;
                }
            });

            TestContext.WriteLine(checkedOptions + " options checked; on " + advantaged +
                                  " of them standing still was ahead by weight for something that option also does not do");
            Assert.Greater(checkedOptions, 100);
            Assert.Greater(advantaged, 0);
        }

        [Test]
        public void TheComparisonTheCreditWasReallyAboutIsTheSameEitherWay()
        {
            // Standing still against eating in front of people.
            var shipped = new Deliberator(_content.Rules);
            var moved = new Deliberator(_withoutCredit.Rules);
            var compared = 0;

            Moments(_content, "daniel_ate_it", 2, m =>
            {
                if (m.Percept.Present.Count == 0) return;
                var with = shipped.Decide(m.Mind, m.Percept, m.Motives, _content.Morning.Day, new Rng(1), new TraceLog(), 0);
                var without = moved.Decide(m.Mind, m.Percept, m.Motives, _content.Morning.Day, new Rng(1), new TraceLog(), 0);

                var eatWith = with.Ranked.FirstOrDefault(r => r.Option.Kind == ActionKind.Eat);
                if (eatWith == null) return;
                var eatWithout = without.Ranked.First(r => r.Option.Kind == ActionKind.Eat);

                Assert.AreEqual(
                    with.Ranked.First(r => r.Option.Kind == ActionKind.Wait).Score - eatWith.Score,
                    without.Ranked.First(r => r.Option.Kind == ActionKind.Wait).Score - eatWithout.Score, 1e-9);
                compared++;
            });

            Assert.Greater(compared, 0, "nobody was ever in the kitchen with somebody else");
        }

        [Test]
        public void StandingStillIsStillCreditedForWhatItAvoidsAndThisIsAKnownDefect()
        {
            // DEFECT, recorded rather than removed; see the S1.2 report. Standing
            // still alone is the one act nobody can perceive, so crediting it for
            // not wanting to be looked at, when alone, is earned. The other two
            // credits are not. They stay because removing them collapses the
            // cast, which the two tests below measure.
            var unearned = _content.Rules.Proposals
                .Where(p => p.Action == "wait" && !(p.Motive == "avoid_exposure" && p.When != null && p.When.Alone == true))
                .Select(p => p.Id)
                .OrderBy(id => id, StringComparer.Ordinal)
                .ToList();

            CollectionAssert.AreEqual(new[] { "leave_it_alone", "let_it_be" }, unearned,
                "if this changes, the credit has been removed or added to; re-run the collapse measurement below");
        }

        static (Dictionary<string, Dictionary<string, double>> profiles, double meanGap, double closest, string closestPair, double comfort)
            Mornings(Scenario001Content content, int seeds)
        {
            var batch = BatchRunner.Run(content, new BatchRunner.Options { Variants = new[] { "daniel_ate_it", "mara_ate_it" }, Seeds = seeds });
            var people = content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();
            var profiles = people.ToDictionary(p => p,
                p => BatchRunner.ActionProfile(batch.Rows, null, p).ToDictionary(k => k.Key, k => k.Value), StringComparer.Ordinal);

            var gaps = new List<(string, double)>();
            for (var i = 0; i < people.Count; i++)
            for (var j = i + 1; j < people.Count; j++)
                gaps.Add((people[i] + "/" + people[j], BatchRunner.HowDifferent(profiles[people[i]], profiles[people[j]])));

            var comfort = batch.Rows.Count(r => r.Action == "comfort") / (double)batch.Rows.Count;
            var min = gaps.OrderBy(g => g.Item2).First();
            return (profiles, gaps.Average(g => g.Item2), min.Item2, min.Item1, comfort);
        }

        [Test]
        public void WithoutTheCreditTheCastCollapsesIntoSittingWithEachOther()
        {
            const int seeds = 10;
            var with = Mornings(_content, seeds);
            var without = Mornings(_withoutCredit, seeds);

            var sb = new StringBuilder();
            sb.AppendLine("# C3, rejected: removing standing still's unearned credit");
            sb.AppendLine();
            sb.AppendLine("Generated by `S12AggregationTests`. `daniel_ate_it` and `mara_ate_it`, seeds 1 to " + seeds + ", with C1 and C2 in place.");
            sb.AppendLine();
            sb.AppendLine("| | With the credit (shipped) | Credit moved onto the acts it avoids |");
            sb.AppendLine("|---|---|---|");
            sb.AppendLine("| Share of all choices that are sitting with somebody | " + with.comfort.ToString("P0") + " | " + without.comfort.ToString("P0") + " |");
            sb.AppendLine("| Different people, mean gap | " + with.meanGap.ToString("0.00") + " | " + without.meanGap.ToString("0.00") + " |");
            sb.AppendLine("| Closest pair | " + with.closestPair + " " + with.closest.ToString("0.00") + " | " + without.closestPair + " " + without.closest.ToString("0.00") + " |");
            sb.AppendLine();
            foreach (var (label, r) in new[] { ("With the credit", with), ("Without it", without) })
            {
                sb.AppendLine("**" + label + ":** " + string.Join("; ", r.profiles.Select(p => p.Key + " " +
                    string.Join(", ", p.Value.OrderByDescending(v => v.Value).Take(3).Select(v => v.Key + " " + v.Value.ToString("P0"))))));
                sb.AppendLine();
            }

            _collapse["1"] = sb.ToString();
            TestContext.WriteLine(sb.ToString());

            // FINDING, pinned. If these stop holding, the loop behind the collapse
            // has been dealt with and the credit can be removed.
            Assert.Greater(without.comfort, with.comfort * 1.5, "removing the credit no longer floods sitting with somebody");
            Assert.Less(without.meanGap, with.meanGap, "removing the credit no longer makes people more alike");
        }

        [Test]
        public void WhatFloodsInIsWantsThatNeedNothingToHaveHappened()
        {
            // The explanation for the collapse, checked rather than asserted in
            // prose. Without the credit, what makes sitting with somebody win is
            // mostly who the person is, not anything they saw: the wants behind
            // it are raised by traits, values and old history every minute, and
            // nothing a person does ever lowers them.
            double standing = 0, history = 0, morning = 0;
            var comforts = 0;

            foreach (var variant in new[] { "daniel_ate_it", "mara_ate_it" })
            foreach (var m in Moments(_withoutCredit, variant, 1))
            {
                if (m.Decision.Chosen.Kind != ActionKind.Comfort) continue;
                comforts++;
                foreach (var c in m.Decision.ChosenScored.Contributions.Where(c => c.Amount > 0))
                {
                    var motive = m.Motives.First(x => x.Key == c.MotiveKey);
                    var total = motive.Terms.Where(t => t.Amount > 0).Sum(t => t.Amount);
                    if (total <= 0) continue;
                    foreach (var t in motive.Terms.Where(t => t.Amount > 0))
                    {
                        var share = c.Amount * t.Amount / total;
                        if (t.Description.StartsWith("trait", StringComparison.Ordinal) || t.Description.StartsWith("value", StringComparison.Ordinal)) standing += share;
                        else if (t.Description.StartsWith("remembers", StringComparison.Ordinal)) history += share;
                        else morning += share;
                    }
                }
            }

            var all = standing + history + morning;
            var line = comforts + " choices to sit with somebody. Their appeal came from traits and values " + (standing / all).ToString("P0") +
                       ", from the backstory ledger " + (history / all).ToString("P0") +
                       ", from anything felt, remembered or believed about this morning or last night " + (morning / all).ToString("P0") + ".";
            _collapse["2"] = "## What floods in" + Environment.NewLine + Environment.NewLine +
                "Generated by `WhatFloodsInIsWantsThatNeedNothingToHaveHappened`, seed 1, without the credit. Each want's contribution is split in proportion to the terms that raised it." +
                Environment.NewLine + Environment.NewLine + line + Environment.NewLine;
            TestContext.WriteLine(line);

            Assert.Greater(comforts, 0);
            Assert.Greater(standing + history, morning, "what makes people sit with each other is mostly what happened after all");
        }

        [Test]
        public void ADecisionShowsEveryStageOfTheArithmeticItRan()
        {
            var moments = Moments(_content, "mara_ate_it", 1);
            var m = moments.First(x => x.CharacterId == "mara");
            var text = DecisionTrace.Explain(m.Decision);
            TestContext.WriteLine(text);

            var stages = new[] { "Active motivations", "-> candidate actions", "-> contribution from each motivation",
                "-> trait/context costs", "-> total score", "-> ambiguity status", "-> selected intention", "-> action" };
            var at = -1;
            foreach (var s in stages)
            {
                var i = text.IndexOf(s, at + 1, StringComparison.Ordinal);
                Assert.Greater(i, at, "stage '" + s + "' missing or out of order");
                at = i;
            }

            var chosen = m.Decision.ChosenScored;
            StringAssert.Contains("= " + chosen.Score.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture), text);
            Assert.AreEqual(chosen.Contributions.Sum(c => c.Amount), chosen.Appeal, 1e-9, "appeal is not the sum of what the wants added");
        }
    }
}
