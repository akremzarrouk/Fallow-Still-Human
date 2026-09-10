using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// Turns a finished run into something a person can read: what each event
    /// meant to each character, why, and what each of them was left holding.
    ///
    /// This is the instrument the slice is judged with. It exists so that a
    /// disagreement about a character is settled by reading the chain rather
    /// than by arguing about the numbers.
    /// </summary>
    public static class S0Report
    {
        public static string EventByEvent(Simulation sim, IReadOnlyList<EventOutcome> outcomes)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# Scenario 001, slice S0: event by event");
            sb.AppendLine();
            sb.AppendLine("What each event meant to each person, and what it stirred. A person");
            sb.AppendLine("who was not there has no line, which is the point.");
            sb.AppendLine();

            foreach (var outcome in outcomes)
            {
                var e = outcome.Event;
                sb.AppendLine($"## {e.Id}  (day {e.Day})");
                sb.AppendLine();
                sb.AppendLine($"> {e.Summary}");
                sb.AppendLine();

                foreach (var pair in outcome.ByCharacter.OrderBy(p => p.Key, StringComparer.Ordinal))
                {
                    var o = pair.Value;
                    var who = sim.Minds[pair.Key].Profile.DisplayName;

                    if (o.Access == Access.None)
                    {
                        sb.AppendLine($"- **{who}** was not there.");
                        continue;
                    }

                    var how = o.FromOwnIntent ? "knew what they meant"
                            : o.Access == Access.Overheard ? "only heard it"
                            : "saw it";
                    var felt = o.Emotions.Count == 0
                        ? "felt nothing in particular"
                        : "felt " + string.Join(", ", o.Emotions.Select(c => $"{c.Type} {c.Intensity:0.00}"
                            + (c.TargetId == null ? "" : $" toward {sim.Minds[c.TargetId].Profile.DisplayName}")));

                    sb.AppendLine($"- **{who}** {how}, took it as **{o.Meaning}**, {felt}.");
                }

                sb.AppendLine();
            }

            return sb.ToString();
        }

        public static string WhereEveryoneStands(Simulation sim)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# Scenario 001, slice S0: where everyone stands at the end");
            sb.AppendLine();

            foreach (var id in sim.Minds.Keys.OrderBy(k => k, StringComparer.Ordinal))
            {
                var mind = sim.Minds[id];
                sb.AppendLine($"## {mind.Profile.DisplayName} ({mind.Profile.Age})");
                sb.AppendLine();

                sb.AppendLine("Believes:");
                var beliefs = mind.Beliefs.All.ToList();
                if (beliefs.Count == 0) sb.AppendLine("- nothing in particular");
                foreach (var b in beliefs)
                    sb.AppendLine($"- {b.Key} at {b.Confidence:0.00}"
                        + (b.Justifications.Count == 0 ? "  (brought it with them)" : $"  ({b.Justifications.Count} things moved it)"));
                sb.AppendLine();

                sb.AppendLine("Has not forgotten:");
                var ledger = mind.Ledger.All.ToList();
                if (ledger.Count == 0) sb.AppendLine("- nothing");
                foreach (var about in ledger.Select(r => r.AboutId).Distinct(StringComparer.Ordinal).OrderBy(x => x, StringComparer.Ordinal))
                {
                    var name = sim.Minds.ContainsKey(about) ? sim.Minds[about].Profile.DisplayName : about;
                    foreach (var kind in mind.Ledger.SummaryAbout(about).OrderByDescending(k => k.Value))
                        sb.AppendLine($"- {name}: {kind.Key} ({kind.Value:0.00})");
                }
                sb.AppendLine();

                sb.AppendLine("Still feeling:");
                var live = mind.Emotions.Live;
                if (live.Count == 0) sb.AppendLine("- nothing that has lasted");
                foreach (var em in live)
                    sb.AppendLine($"- {em}");
                sb.AppendLine();

                sb.AppendLine("Remembers, most strongly first:");
                foreach (var x in mind.Experiences.OrderByDescending(x => x.Salience).Take(6))
                    sb.AppendLine($"- {x.EventId} as {x.Meaning} ({x.Source}, salience {x.Salience:0.00}): {x.Summary}");
                sb.AppendLine();
            }

            return sb.ToString();
        }

        /// <summary>Every step of every chain, for reading line by line.</summary>
        public static string FullTrace(Simulation sim)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# Scenario 001, slice S0: the full trace");
            sb.AppendLine();
            sb.AppendLine("Every step, in the order it happened, with the record it came from.");
            sb.AppendLine();

            foreach (var r in sim.Trace.All)
            {
                var parents = r.ParentIds.Count == 0 ? "" : $" <- #{string.Join(",#", r.ParentIds)}";
                sb.AppendLine($"#{r.Id} [{r.Kind}]{(r.CharacterId == null ? "" : " " + r.CharacterId)} ({r.EventId}){parents}");
                sb.AppendLine($"      {r.Summary}");
                foreach (var kv in r.Data)
                    sb.AppendLine($"        {kv.Key}: {kv.Value}");
            }

            return sb.ToString();
        }

        /// <summary>The chain behind one person's feeling, printed the way it would be read aloud.</summary>
        public static string WhyTheyFeltThat(Simulation sim, string characterId, string emotionType)
        {
            var mind = sim.Minds[characterId];
            var emotion = mind.Emotions.Live.FirstOrDefault(e => e.Type == emotionType);
            if (emotion == null || emotion.Causes.Count == 0)
                return $"{characterId} is not feeling {emotionType}.";

            return sim.Trace.Why(emotion.Causes[emotion.Causes.Count - 1]);
        }
    }
}
