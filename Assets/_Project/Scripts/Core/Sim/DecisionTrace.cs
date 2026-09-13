using System;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// One decision written out stage by stage, in the order the arithmetic ran:
    /// the wants that were active, the options, what each want added to each
    /// option, what each option cost this person, the total, whether the choice
    /// was clear or too close to call, the intention it was taken under and left
    /// behind, and the act.
    ///
    /// Everything printed is read from the numbers the deliberator used. Nothing
    /// is reconstructed afterwards, so the account cannot disagree with the
    /// decision it describes.
    /// </summary>
    public static class DecisionTrace
    {
        public static string Explain(Decision d, int options = 6)
        {
            var sb = new StringBuilder();
            var inv = CultureInfo.InvariantCulture;

            sb.AppendLine("Active motivations");
            foreach (var m in d.Motives)
                sb.AppendLine("  " + m.Key + " " + m.Urgency.ToString("0.00", inv) + "   because " + m.Because);

            sb.AppendLine("-> candidate actions (" + d.Ranked.Count + "), best " + Math.Min(options, d.Ranked.Count) + " shown" +
                          (d.Considered.Count < d.Ranked.Count ? ", plus any that the intention left in" : ""));

            var best = d.Ranked.Take(options).ToList();
            var shown = d.Considered.Count < d.Ranked.Count
                ? best.Concat(d.Considered.Where(c => !best.Contains(c))).ToList()
                : best;

            foreach (var r in shown)
            {
                var considered = d.Considered.Contains(r);
                sb.AppendLine("  " + r.Option.Key + (r.Option.SameAs(d.Chosen) ? "   <- chosen" : "") +
                              (considered ? "" : "   (not considered: does not serve the intention)"));

                sb.AppendLine("    -> contribution from each motivation");
                if (r.Contributions.Count == 0) sb.AppendLine("       none");
                foreach (var c in r.Contributions)
                    sb.AppendLine("       " + c.MotiveKey + ": urgency " + c.Urgency.ToString("0.00", inv) +
                                  " x fit " + c.Fit.ToString("+0.00;-0.00", inv) + " = " + c.Amount.ToString("+0.000;-0.000", inv) +
                                  " (" + c.ProposalId + (c.Amount < 0 ? ", counts against" : "") + ")");

                sb.AppendLine("    -> trait/context costs");
                if (r.Prices.Count == 0) sb.AppendLine("       none");
                foreach (var p in r.Prices) sb.AppendLine("       " + p);

                sb.AppendLine("    -> total score " + r.Appeal.ToString("0.000", inv) + " - " + r.Cost.ToString("0.000", inv) +
                              " = " + r.Score.ToString("0.000", inv));
            }

            sb.Append("-> ambiguity status: ");
            if (d.Resolution == Resolution.Clear)
                sb.AppendLine("clear, ahead of the next option considered by " + d.Margin.ToString("0.000", inv));
            else
                sb.AppendLine("too close to call between " + string.Join(", ", d.Tied.Select(t => t.Key)) +
                              "; the seed settled it");

            sb.Append("-> selected intention: ");
            if (d.Holding != null)
                sb.Append("brought in " + d.Holding + ", " + d.Commitment + "; ");
            sb.AppendLine(d.Forms == null ? "nothing in particular" : d.Forms.MotiveKey +
                          (d.Chosen.Kind == ActionKind.GoTo ? ", kept until they arrive" : ", done once this is done"));

            sb.AppendLine("-> action: " + d.Chosen.Key + " (" + d.Chosen.Duration + " min)");
            return sb.ToString();
        }
    }
}
