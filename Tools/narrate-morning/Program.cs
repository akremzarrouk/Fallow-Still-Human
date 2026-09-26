using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using Fallow.Core.Sim;

namespace Fallow.Tools.NarrateMorning
{
    /// <summary>
    /// narrate &lt;repo root&gt; &lt;variant&gt; &lt;seed&gt;: writes Docs/understanding/runs/&lt;variant&gt;-&lt;seed&gt;.md.
    /// test &lt;repo root&gt;: runs the narrator's one test.
    /// Started by narrate.sh at the repository root, which builds this first.
    /// </summary>
    public static class Program
    {
        public static int Main(string[] args)
        {
            // Numbers in the story, and in the simulation's own strings the story
            // reads, are written the same way on every machine.
            CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
            CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;

            if (args.Length == 2 && args[0] == "test")
                return NarratorTest.Run(args[1]);

            if (args.Length != 4 || args[0] != "narrate" || !ulong.TryParse(args[3], NumberStyles.None, CultureInfo.InvariantCulture, out var seed))
            {
                Console.Error.WriteLine("usage: narrate <repo root> <variant> <seed> | test <repo root>");
                return 2;
            }

            var root = args[1];
            var variant = args[2];
            var content = Scenario001Content.Load(DataRoot(root));
            if (content.Morning.Variant(variant) == null)
            {
                Console.Error.WriteLine("no such variant: " + variant + ". Known: " +
                    string.Join(", ", content.Morning.Variants.Concat(content.Morning.HeldOutVariants).Select(v => v.Id)));
                return 2;
            }

            var told = Narrator.Tell(content, variant, seed);
            var relative = "Docs/understanding/runs/" + variant + "-" + seed.ToString(CultureInfo.InvariantCulture) + ".md";
            var path = Path.Combine(root, relative.Replace('/', Path.DirectorySeparatorChar));
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllText(path, told.Text, new UTF8Encoding(false));

            Console.WriteLine("wrote " + relative);
            Console.WriteLine("decisions=" + told.Decisions + " told=" + told.Told + " events=" + told.Events +
                              " stops=" + told.Stops + " portions_left=" + told.PortionsLeft);
            return 0;
        }

        public static string DataRoot(string root) => Path.Combine(root, "Assets", "_Project", "Data");
    }
}
