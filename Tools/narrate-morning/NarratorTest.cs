using System;
using System.Collections.Generic;
using Fallow.Core.Sim;

namespace Fallow.Tools.NarrateMorning
{
    /// <summary>
    /// The narrator's one test, run by `./narrate.sh --test`. It lives beside the
    /// tool rather than in the Unity suite because Unity compiles nothing outside
    /// Assets, so a Unity test could not reach this code.
    /// </summary>
    public static class NarratorTest
    {
        const string Variant = "daniel_ate_it";
        const ulong Seed = 1;

        /// <summary>
        /// The baseline's decision count for this morning, as BaselineTests recorded it:
        /// Docs/experiments/decision-sensitivity/baseline.md, section 2, "72 under the primary baseline".
        /// </summary>
        const int BaselineDecisions = 72;

        public static int Run(string root)
        {
            const string name = "DanielAteItSeed1IsTheBaselines72Decisions";
            var failures = new List<string>();

            var content = Scenario001Content.Load(Program.DataRoot(root));
            var once = Narrator.Tell(content, Variant, Seed);
            var again = Narrator.Tell(content, Variant, Seed);

            if (once.Decisions != BaselineDecisions)
                failures.Add("the morning took " + once.Decisions + " decisions, the baseline takes " + BaselineDecisions);
            if (once.Told != once.Decisions)
                failures.Add("the story accounts for " + once.Told + " of " + once.Decisions + " decisions");
            if (!once.Text.Contains("**" + BaselineDecisions + " decisions**"))
                failures.Add("the story does not report " + BaselineDecisions + " decisions");
            if (!string.Equals(once.Text, again.Text, StringComparison.Ordinal))
                failures.Add("telling the same morning twice gave two different stories");

            foreach (var f in failures) Console.WriteLine("  " + f);
            Console.WriteLine((failures.Count == 0 ? "PASS " : "FAIL ") + name + " (" + once.Decisions + " decisions)");
            return failures.Count == 0 ? 0 : 1;
        }
    }
}
