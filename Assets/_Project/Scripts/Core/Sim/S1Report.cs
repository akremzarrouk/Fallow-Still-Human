using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Testing;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// Turns a morning into something a person can read and argue with.
    ///
    /// The slice is judged on these rather than on the numbers, so that a
    /// disagreement about whether somebody behaved plausibly is settled by
    /// reading what they did and why, not by comparing scores.
    /// </summary>
    public static class S1Report
    {
        public static string Morning(Scenario001Run run)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# The morning, minute by minute");
            sb.AppendLine();
            sb.AppendLine("Variant: **" + run.VariantId + "**, seed " + run.Seed + ".");
            sb.AppendLine();
            sb.AppendLine("Nothing below was scripted. The only thing anyone was told to do is the");
            sb.AppendLine("count that opens it.");
            sb.AppendLine();

            foreach (var a in run.Result.Actions.OrderBy(a => a.Minute).ThenBy(a => a.CharacterId, StringComparer.Ordinal))
            {
                var who = run.Minds[a.CharacterId].Profile.DisplayName;
                var how = a.Resolution == Resolution.Clear
                    ? ""
                    : " *(nothing in it either way)*";

                sb.AppendLine(
                    "- **" + a.Minute.ToString("00") + "** " + who + ", in the " + RoomName(run, a.RoomId) + ": " +
                    Describe(run, a.Action) +
                    " because " + Readable(a.LeadingMotive) + " (" + a.LeadingUrgency.ToString("0.00") + ")" +
                    how +
                    (a.Outcome == null ? "" : ". " + Capitalise(a.Outcome)));
            }

            sb.AppendLine();
            sb.AppendLine("At the end: " + run.World.Portions + " portions left, and " +
                          string.Join(", ", run.World.Inhabitants.Select(id =>
                              run.Minds[id].Profile.DisplayName + " in the " + RoomName(run, run.World.RoomOf(id)))) + ".");

            return sb.ToString();
        }

        /// <summary>What each of them spent the morning doing, side by side.</summary>
        public static string WhatEachOfThemDid(Scenario001Content content, BatchRunner.Batch batch, string variant)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# What each of them did with the morning");
            sb.AppendLine();
            sb.AppendLine("Variant **" + variant + "**, as a share of that person own decisions across every seed.");
            sb.AppendLine();

            var people = content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal).ToList();
            var actions = ActionOption.AllNames;

            sb.AppendLine("| | " + string.Join(" | ", actions) + " |");
            sb.AppendLine("|---|" + string.Join("|", actions.Select(_ => "---")) + "|");

            foreach (var id in people)
            {
                var profile = BatchRunner.ActionProfile(batch.Rows, variant, id);
                sb.AppendLine("| " + content.Cast[id].DisplayName + " | " +
                    string.Join(" | ", actions.Select(a =>
                        profile.TryGetValue(a, out var v) ? v.ToString("P0", CultureInfo.InvariantCulture) : "-")) +
                    " |");
            }

            sb.AppendLine();
            sb.AppendLine("How far apart they are, as the total difference between those profiles.");
            sb.AppendLine("Zero would mean two people doing the same morning.");
            sb.AppendLine();
            sb.AppendLine("| | " + string.Join(" | ", people.Select(p => content.Cast[p].DisplayName)) + " |");
            sb.AppendLine("|---|" + string.Join("|", people.Select(_ => "---")) + "|");

            foreach (var a in people)
            {
                var pa = BatchRunner.ActionProfile(batch.Rows, variant, a);
                sb.AppendLine("| " + content.Cast[a].DisplayName + " | " +
                    string.Join(" | ", people.Select(b =>
                    {
                        if (a == b) return "-";
                        var pb = BatchRunner.ActionProfile(batch.Rows, variant, b);
                        return BatchRunner.HowDifferent(pa, pb).ToString("0.00", CultureInfo.InvariantCulture);
                    })) + " |");
            }

            return sb.ToString();
        }

        /// <summary>The leading want behind each decision, counted.</summary>
        public static string WhatTheyWanted(Scenario001Content content, BatchRunner.Batch batch)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# What was behind it");
            sb.AppendLine();

            foreach (var variant in batch.Rows.Select(r => r.Variant).Distinct().OrderBy(v => v, StringComparer.Ordinal))
            {
                sb.AppendLine("## " + variant);
                sb.AppendLine();

                foreach (var id in content.Cast.Keys.OrderBy(k => k, StringComparer.Ordinal))
                {
                    var mine = batch.Rows
                        .Where(r => r.Variant == variant && r.Character == id)
                        .GroupBy(r => r.Motive, StringComparer.Ordinal)
                        .OrderByDescending(g => g.Count())
                        .Take(4)
                        .Select(g => Readable(g.Key) + " " + ((double)g.Count() /
                            batch.Rows.Count(r => r.Variant == variant && r.Character == id)).ToString("P0", CultureInfo.InvariantCulture))
                        .ToList();

                    sb.AppendLine("- **" + content.Cast[id].DisplayName + "**: " + string.Join(", ", mine));
                }

                sb.AppendLine();
            }

            return sb.ToString();
        }

        /// <summary>The chain behind one decision, in words.</summary>
        public static string WhyTheyDidThat(Scenario001Run run, string characterId, int minute)
        {
            var record = run.Result.Actions.FirstOrDefault(a =>
                string.Equals(a.CharacterId, characterId, StringComparison.Ordinal) && a.Minute == minute);

            if (record == null) return characterId + " decided nothing at minute " + minute + ".";

            var sb = new StringBuilder();
            sb.AppendLine(run.Minds[characterId].Profile.DisplayName + ", minute " + minute + ": " +
                          Describe(run, record.Action));
            sb.AppendLine();
            sb.Append(run.Trace.Why(record.DecisionTraceId));
            return sb.ToString();
        }

        /// <summary>Every decision one person took, with the chain behind each.</summary>
        public static string FullTrace(Scenario001Run run)
        {
            var sb = new StringBuilder();
            sb.AppendLine("Variant " + run.VariantId + ", seed " + run.Seed);
            sb.AppendLine();

            foreach (var a in run.Result.Actions)
            {
                sb.AppendLine(new string('=', 70));
                sb.AppendLine(a.ToString());
                sb.AppendLine(new string('=', 70));
                sb.AppendLine(run.Trace.Why(a.DecisionTraceId));
                sb.AppendLine();
            }

            return sb.ToString();
        }

        static string Describe(Scenario001Run run, ActionOption action)
        {
            switch (action.Kind)
            {
                case ActionKind.Wait: return "stays where they are";
                case ActionKind.Observe: return "watches " + Who(run, action.TargetId);
                case ActionKind.GoTo: return "goes to the " + RoomName(run, action.DestinationRoomId);
                case ActionKind.CheckPantry: return "opens the pantry and counts";
                case ActionKind.SearchRoom: return "goes through the room";
                case ActionKind.Comfort: return "sits with " + Who(run, action.TargetId);
                case ActionKind.Eat: return "takes a portion";
                default: return action.KindName;
            }
        }

        static readonly Dictionary<string, string> Plain = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            { "get_food", "hunger" },
            { "guard_supplies", "it has to last" },
            { "find_out", "needing to know what happened" },
            { "avoid_exposure", "not wanting to be looked at" },
            { "restore_standing", "wanting to be the one who settles it" },
            { "keep_peace", "wanting the house to hold" },
            { "look_after", "somebody is not all right" }
        };

        static string Readable(string motiveKey)
        {
            if (motiveKey == null) return "nothing pressing";
            var name = motiveKey.Split(':')[0];
            var who = motiveKey.Contains(":") ? motiveKey.Split(':')[1] : null;
            var text = Plain.TryGetValue(name, out var p) ? p : name;
            return who == null ? text : text + " (" + who + ")";
        }

        static string Who(Scenario001Run run, string id)
            => id != null && run.Minds.TryGetValue(id, out var m) ? m.Profile.DisplayName : id;

        static string RoomName(Scenario001Run run, string roomId)
            => run.World.House.Get(roomId)?.DisplayName ?? roomId;

        static string Capitalise(string s)
            => string.IsNullOrEmpty(s) ? s : char.ToUpperInvariant(s[0]) + s.Substring(1);
    }
}
