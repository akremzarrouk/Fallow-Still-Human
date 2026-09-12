using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using Fallow.Core.Testing;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// Concrete chains, taken from real runs rather than described: a night
    /// changes something inside a person, that changes what they want, and that
    /// changes what they decide. Each example is found by search, not chosen by
    /// hand, and written out in full.
    /// </summary>
    public class S11CausalExamplesTests
    {
        static Scenario001Content _content;
        static readonly StringBuilder _report = new StringBuilder();

        [OneTimeSetUp]
        public void Load()
        {
            _content = Scenario001Content.Load(TestPaths.DataRoot);
            _report.Clear();
            _report.AppendLine("# S1.1 causal examples");
            _report.AppendLine();
            _report.AppendLine("Found by `S11CausalExamplesTests`: the first seed on which the night changed a decision");
            _report.AppendLine("and the want behind the changed decision leads back to the night. Chains are printed");
            _report.AppendLine("by the trace tool as they are.");
            _report.AppendLine();
        }

        [OneTimeTearDown]
        public void Write()
        {
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S1.1");
            Directory.CreateDirectory(dir);
            File.WriteAllText(Path.Combine(dir, "causal-examples.md"), _report.ToString());
        }

        static IReadOnlyList<WorldEvent> Night(string v) => _content.Morning.Variant(v).NightEvents;

        /// <summary>
        /// Walks the seeds until the treatment takes a decision the control did
        /// not take at the same minute, where the want that led it rests on the
        /// night. Returns what it found, or null.
        /// </summary>
        static string FindChangedDecision(string variant, string who, int seeds)
        {
            var causes = Night(variant).Select(e => e.Id).ToList();

            for (ulong seed = 1; seed <= (ulong)seeds; seed++)
            {
                var pair = Counterfactual.Run(_content, variant, new List<WorldEvent>(), Night(variant), causes, seed);
                var control = pair.Control.Result;
                var treatment = pair.Treatment.Result;
                var memo = new Dictionary<int, bool>();

                for (var i = 0; i < treatment.Actions.Count; i++)
                {
                    var t = treatment.Actions[i];
                    if (t.CharacterId != who) continue;

                    var c = control.Actions.FirstOrDefault(a => a.CharacterId == who && a.Minute == t.Minute);
                    if (c == null || c.Action.SameAs(t.Action)) continue;

                    var decision = treatment.Decisions[i];
                    var leading = decision.Leading;
                    if (leading == null || !Counterfactual.ReachesCause(pair.Treatment.Trace, leading, causes, memo)) continue;

                    var sb = new StringBuilder();
                    sb.AppendLine("## " + variant + ", " + who + ", seed " + seed + ", minute " + t.Minute);
                    sb.AppendLine();
                    sb.AppendLine("- **Without the night:** " + c.Action + " because `" + c.LeadingMotive + "` (" + c.LeadingUrgency.ToString("0.00") + ")");
                    sb.AppendLine("- **With the night:** " + t.Action + " because `" + t.LeadingMotive + "` (" + t.LeadingUrgency.ToString("0.00") + ")");
                    sb.AppendLine();
                    sb.AppendLine("The want that led the changed decision, and everything it rests on:");
                    sb.AppendLine();
                    sb.AppendLine("```");
                    sb.AppendLine(Shorten(pair.Treatment.Trace.Why(leading.TraceId)));
                    sb.AppendLine("```");
                    return sb.ToString();
                }
            }

            return null;
        }

        /// <summary>Cuts the arithmetic out of long trace lines so the chain can be read.</summary>
        static string Shorten(string why)
            => string.Join(Environment.NewLine, why.Split('\n')
                .Select(l => l.TrimEnd('\r'))
                .Select(l => l.Length > 190 ? l.Substring(0, 187) + "..." : l));

        [Test]
        public void TheOneWhoAteIt()
        {
            var found = FindChangedDecision("mara_ate_it", "mara", 20);
            _report.AppendLine(found ?? "## mara_ate_it, mara" + Environment.NewLine + Environment.NewLine + "No changed decision with a traceable leading want in 20 seeds.");
            _report.AppendLine();
            TestContext.WriteLine(found);
            Assert.IsNotNull(found, "the night never changed one of her decisions for a reason that leads back to it");
        }

        [Test]
        public void TheOneWhoGaveItAway()
        {
            var found = FindChangedDecision("elena_fed_mara", "elena", 20);
            _report.AppendLine(found ?? "## elena_fed_mara, elena" + Environment.NewLine + Environment.NewLine + "No changed decision with a traceable leading want in 20 seeds.");
            _report.AppendLine();
            TestContext.WriteLine(found);
            Assert.IsNotNull(found, "the night never changed one of her decisions for a reason that leads back to it");
        }

        [Test]
        public void TheOneWhoDoesNotShowIt()
        {
            // The held-out case, to show what a change in wants without a change
            // in decisions looks like. His want to be elsewhere rises sharply and
            // leads back to the night; what he does at the start does not move.
            var causes = Night("leo_ate_it").Select(e => e.Id).ToList();
            var pair = Counterfactual.Run(_content, "leo_ate_it", new List<WorldEvent>(), Night("leo_ate_it"), causes, 1, minutes: 1);

            var percept = pair.Treatment.Morning.See("leo");
            var at = pair.Treatment.Trace.Add(Fallow.Core.Tracing.TraceKind.Access, "leo", null,
                "at minute " + percept.Minute + ", " + percept);
            var motives = new Motivator(_content.Rules).Raise(
                pair.Treatment.Minds["leo"], percept, _content.Morning.Day, pair.Treatment.Trace, at);
            var avoid = motives.First(m => m.Name == "avoid_exposure");
            var p = pair.People["leo"];

            _report.AppendLine("## leo_ate_it, leo, seed 1, first minute (held-out)");
            _report.AppendLine();
            _report.AppendLine("- **Wish to be elsewhere:** " + p.ControlAtStart.Of("avoid_exposure").ToString("0.00") + " without the night, " +
                               p.TreatmentAtStart.Of("avoid_exposure").ToString("0.00") + " with it");
            _report.AppendLine("- **First decision without the night:** " + p.ControlActions.FirstOrDefault());
            _report.AppendLine("- **First decision with the night:** " + p.TreatmentActions.FirstOrDefault());
            _report.AppendLine();
            _report.AppendLine("```");
            _report.AppendLine(Shorten(pair.Treatment.Trace.Why(avoid.TraceId)));
            _report.AppendLine("```");
            _report.AppendLine();

            Assert.IsTrue(Counterfactual.ReachesCause(pair.Treatment.Trace, avoid, causes));
        }
    }
}
