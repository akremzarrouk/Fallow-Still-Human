using System;
using System.IO;
using System.Linq;
using Fallow.Core.Sim;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// A first look at whether the morning runs at all, kept separate from the
    /// experiment itself so that a broken pipeline fails loudly and early rather
    /// than as a strange distribution somewhere downstream.
    /// </summary>
    public class SmokeTests
    {
        [Test]
        public void AMorningRunsAndSomebodyDoesSomething()
        {
            var content = Scenario001Content.Load(TestPaths.DataRoot);
            var run = Scenario001.Run(content, "daniel_ate_it", 1);

            Assert.IsNotEmpty(run.Result.Actions, "nobody did anything all morning");

            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S1", "traces");
            Directory.CreateDirectory(dir);
            File.WriteAllText(Path.Combine(dir, "smoke-morning.md"), S1Report.Morning(run));

            TestContext.WriteLine(S1Report.Morning(run));
            TestContext.WriteLine("portions left: " + run.World.Portions);

            foreach (var id in run.World.Inhabitants)
                TestContext.WriteLine(
                    id + ": " + string.Join(", ",
                        run.Result.By(id).GroupBy(a => a.Action.KindName)
                            .OrderByDescending(g => g.Count())
                            .Select(g => g.Key + " x" + g.Count())));
        }
    }
}
