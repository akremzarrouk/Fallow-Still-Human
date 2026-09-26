using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Fallow.Core.Model;
using Fallow.Core.Sim;

namespace Fallow.Tools.NarrateMorning
{
    /// <summary>One morning told as a story, and the counts a check needs.</summary>
    public sealed class Narration
    {
        public string Text;

        /// <summary>Decisions the simulation recorded.</summary>
        public int Decisions;

        /// <summary>Decisions the story accounts for, one line each or inside a collapsed run.</summary>
        public int Told;

        public int Events;
        public int Stops;
        public int PortionsLeft;
    }

    /// <summary>
    /// Runs one morning through the unmodified simulation and tells it in plain
    /// words: who wanted what, what they chose, what made them choose it, and
    /// what came of it. Everything here is read off the simulation's own public
    /// records; nothing is recomputed and nothing in the simulation is changed.
    /// </summary>
    public static class Narrator
    {
        const string Nl = "\n";

        sealed class Moment
        {
            public int Minute;
            public string Who;
            public string Why;
            public Percept Percept;
            public IReadOnlyList<Motive> Motives;
            public Decision Decision;
            public ActionRecord Record;
            public List<Foresight> Foresaw;
            public int Index;
        }

        sealed class Foresight
        {
            public string Walk;
            public string Destination;
            public string Want;
            public string End;
            public double? Score;
            public bool NotWorth;
        }

        public static Narration Tell(Scenario001Content content, string variant, ulong seed)
        {
            var run = Scenario001.Prepare(content, variant, seed);
            var world = run.World;
            var house = world.House;
            var people = world.Inhabitants;
            string Name(string id) => id != null && run.Minds.TryGetValue(id, out var m) ? m.Profile.DisplayName : id;
            string RoomName(string id) => house.Get(id)?.DisplayName ?? id;

            // Minute 0: after the history, the night and the opening, before anybody decides.
            var cast = Cast(run, content, variant, Name);
            var startPortions = world.Portions;

            var moments = new List<Moment>();
            run.Morning.Decided = m => moments.Add(new Moment
            {
                Minute = m.Minute,
                Who = m.CharacterId,
                Why = m.Why,
                Percept = m.Percept,
                Motives = m.Motives,
                Decision = m.Decision,
                Index = moments.Count
            });

            var rooms = new SortedDictionary<int, string>();
            for (var i = 0; i < content.Morning.Minutes; i++)
            {
                var before = moments.Count;
                run.Morning.Step();
                if (moments.Count > before) rooms[world.Minute] = RoomLine(run, Name, RoomName);
            }

            var result = run.Result;
            if (result.Actions.Count != moments.Count)
                throw new InvalidOperationException("decisions and records differ in number");
            for (var i = 0; i < moments.Count; i++)
            {
                var r = result.Actions[i];
                if (r.Minute != moments[i].Minute || r.CharacterId != moments[i].Who)
                    throw new InvalidOperationException("decision " + i + " does not match its record");
                moments[i].Record = r;
                moments[i].Foresaw = Foresights(run, moments[i].Decision);
            }

            var events = result.Events.ToDictionary(e => e.Id, StringComparer.Ordinal);
            var stops = run.Morning.Interruptions;
            var usedRules = new SortedDictionary<string, string>(StringComparer.Ordinal);
            var byPerson = moments.GroupBy(m => m.Who).ToDictionary(g => g.Key, g => g.ToList(), StringComparer.Ordinal);

            // Runs of identical decisions, told once at the minute they start.
            var runStart = new Dictionary<int, List<Moment>>();
            var folded = new HashSet<int>();
            foreach (var mine in byPerson.Values)
            {
                var i = 0;
                while (i < mine.Count)
                {
                    var j = i + 1;
                    var key = RunKey(mine[i]);
                    while (key != null && j < mine.Count && RunKey(mine[j]) == key) j++;
                    if (j - i >= 2)
                    {
                        runStart[mine[i].Index] = mine.GetRange(i, j - i);
                        for (var k = i + 1; k < j; k++) folded.Add(mine[k].Index);
                    }
                    i = j;
                }
            }

            var told = 0;
            var story = new StringBuilder();
            foreach (var minute in rooms.Keys)
            {
                story.Append("**min ").Append(minute.ToString("00", CultureInfo.InvariantCulture)).Append("** · ").Append(rooms[minute]).Append(Nl);
                foreach (var m in moments.Where(x => x.Minute == minute))
                {
                    if (folded.Contains(m.Index)) continue;
                    if (runStart.TryGetValue(m.Index, out var same))
                    {
                        story.Append(RunLine(same, byPerson, run, Name, RoomName, usedRules)).Append(Nl);
                        told += same.Count;
                    }
                    else
                    {
                        story.Append(Line(m, byPerson, run, events, stops, Name, RoomName, usedRules)).Append(Nl);
                        told++;
                    }
                }
                story.Append(Nl);
            }

            var sb = new StringBuilder();
            var v = content.Morning.Variant(variant);
            sb.Append("# The morning as a story: ").Append(variant).Append(", seed ").Append(seed.ToString(CultureInfo.InvariantCulture)).Append(Nl).Append(Nl);
            sb.Append("Generated by `./narrate.sh ").Append(variant).Append(' ').Append(seed.ToString(CultureInfo.InvariantCulture))
              .Append("` from the shipped data and the unmodified simulation code. Do not edit it by hand; run the script again.").Append(Nl).Append(Nl);
            sb.Append("**").Append(moments.Count).Append(" decisions** in ").Append(content.Morning.Minutes).Append(" minutes. ")
              .Append(result.Events.Count).Append(" things happened in the house. Somebody was stopped part way through an act ")
              .Append(stops.Count).Append(" times. The pantry held ").Append(startPortions).Append(" portions at the start and ")
              .Append(world.Portions).Append(" at the end.").Append(Nl).Append(Nl);
            if (!string.IsNullOrEmpty(v?.Note))
                sb.Append("What the data says about this variant: \"").Append(v.Note).Append("\"").Append(Nl).Append(Nl);
            sb.Append("Settings read from the data: traits and values `").Append(content.Rules.Deciding.Dispositions)
              .Append("`, walks weighed by their `").Append(content.Rules.Deciding.Means).Append("`, choices within ")
              .Append(F(content.Rules.Deciding.AmbiguityBand)).Append(" of the best settled by the dice.").Append(Nl).Append(Nl);

            sb.Append(Legend(content)).Append(Nl);
            sb.Append(cast).Append(Nl);
            sb.Append("## The morning").Append(Nl).Append(Nl);
            sb.Append(story);
            var eaten = result.Events.Count(e => e.Action == "eat_portion");
            sb.Append("## At the end").Append(Nl).Append(Nl);
            sb.Append("At minute ").Append(world.Minute).Append(": ")
              .Append(string.Join(" · ", house.Rooms.Where(r => world.InRoom(r.Id).Count > 0)
                  .Select(r => r.DisplayName + ": " + string.Join(", ", world.InRoom(r.Id).Select(Name)))))
              .Append(". ").Append(world.Portions).Append(" of ").Append(startPortions).Append(" portions left; ")
              .Append(eaten).Append(eaten == 1 ? " portion" : " portions").Append(" eaten this morning.").Append(Nl).Append(Nl);
            sb.Append(RuleTable(usedRules));

            return new Narration
            {
                Text = sb.ToString(),
                Decisions = moments.Count,
                Told = told,
                Events = result.Events.Count,
                Stops = stops.Count,
                PortionsLeft = world.Portions
            };
        }

        // ---------------------------------------------------------------- header

        static string Legend(Scenario001Content content)
        {
            var band = F(content.Rules.Deciding.AmbiguityBand);
            var sb = new StringBuilder();
            sb.Append("## How to read it").Append(Nl).Append(Nl);
            sb.Append("- A want's number is how strongly it is felt, from 0 to 1. An act's score is what it is worth to every want it serves, less what it costs this person.").Append(Nl);
            sb.Append("- *Italics* are rules written in the data, in plain words. The table at the end gives each one's real name.").Append(Nl);
            sb.Append("- **Clear**: the chosen act was more than ").Append(band).Append(" ahead of the next, and nothing random happened.").Append(Nl);
            sb.Append("- **DICE**: several acts were within ").Append(band).Append(" of the best; a seeded draw, weighted toward the top, picked one. The acts it chose between are listed.").Append(Nl);
            sb.Append("- **Walked here for** a want: arriving from a walk made for it, only acts serving it are weighed, unless it is gone, cannot be served here, or is not worth it here.").Append(Nl);
            sb.Append("- **Stopped by**: something that just happened stirred them enough to stop what they were doing and decide again.").Append(Nl);
            sb.Append("- **Pictured**: a walk counts for a want only if something worth doing for it is pictured at the other end. The pictured room holds only the person the want is about.").Append(Nl);
            sb.Append("- A line headed with a minute range folds a run of identical decisions by one person into one line.").Append(Nl);
            sb.Append("- Each **min** line lists every room at a minute when somebody decided: who is in it and what they are doing. \"to 12\" is when that act ends if nothing stops it.").Append(Nl);
            sb.Append("- The code behind each of these is cited in `Docs/understanding/morning-walkthrough.md`, section 1.").Append(Nl);
            return sb.ToString();
        }

        static string Cast(Scenario001Run run, Scenario001Content content, string variant, Func<string, string> name)
        {
            var world = run.World;
            var ids = world.Inhabitants;
            var sb = new StringBuilder();
            sb.Append("## The cast at minute 0").Append(Nl).Append(Nl);
            sb.Append("What the simulation records about each of them after the history, the night and the opening count, before anybody decides. \"not tracked\" means the simulation has no record of that kind.").Append(Nl).Append(Nl);

            sb.Append("| |");
            foreach (var id in ids) sb.Append(' ').Append(name(id)).Append(" |");
            sb.Append(Nl).Append("|---|");
            foreach (var _ in ids) sb.Append("---|");
            sb.Append(Nl);

            void Row(string label, Func<string, string> cell)
            {
                sb.Append("| ").Append(label).Append(" |");
                foreach (var id in ids) sb.Append(' ').Append(cell(id)).Append(" |");
                sb.Append(Nl);
            }

            var opening = content.Morning.Opening;
            var night = content.Morning.Variant(variant)?.NightEvents ?? new List<WorldEvent>();

            string Memory(string id, WorldEvent e)
            {
                var x = run.Minds[id].Experiences.LastOrDefault(ex => ex.EventId == e.Id);
                return x == null ? "no memory of it: was not there" : Known(x, id);
            }

            Row("Age", id => run.Minds[id].Profile.Age.ToString(CultureInfo.InvariantCulture));
            Row("Role in the family", id => run.Minds[id].Profile.FamilyRole ?? "not tracked");
            Row("Where, how hungry", id => world.House.Get(world.RoomOf(id))?.DisplayName + ", hunger " + F(world.HungerOf(id)));
            if (opening != null)
                Row("The count came up short", id => Memory(id, opening));
            if (night.Count == 0)
                Row("What happened in the night", id => "nothing happened in the night");
            foreach (var e in night)
                Row("The night: " + e.Summary.TrimEnd('.'), id => Memory(id, e));
            Row("Connects the night to the missing can", id =>
            {
                var mind = run.Minds[id];
                if (!night.Any(e => mind.Experiences.Any(x => x.EventId == e.Id))) return "-";
                // A belief rests on the memories that moved it, so this is read, not
                // inferred: beliefs about what went missing that a night memory moved.
                var fromNight = mind.Beliefs.All
                    .Where(b => b.Confidence > 0.0 && b.Justifications.Any(t => night.Any(e =>
                        run.Trace.Get(t)?.EventId == e.Id && e.Topic != null && b.Args.Contains(e.Topic, StringComparer.Ordinal))))
                    .ToList();
                return fromNight.Count == 0
                    ? "not tracked"
                    : "yes: from that memory, believes " + string.Join("; ", fromNight.Select(b => Belief(b, name)));
            });
            Row("Who they think took it", id =>
            {
                var held = run.Minds[id].Beliefs.All.Where(b => b.Predicate == "answerable_for" && b.Confidence > 0.0).ToList();
                return held.Count == 0 ? "not tracked" : "not tracked (nearest: " + string.Join(", ", held.Select(b => Belief(b, name))) + ")";
            });
            Row("Believes", id =>
            {
                var all = run.Minds[id].Beliefs.All.Where(b => b.Confidence > 0.0).ToList();
                return all.Count == 0 ? "nothing recorded" : string.Join("; ", all.Select(b => Belief(b, name)));
            });
            Row("Remembers others doing", id =>
            {
                var all = run.Minds[id].Ledger.All;
                return all.Count == 0 ? "nothing recorded" : string.Join("; ", all.Select(r => Words(r.Entry) + ": " + name(r.AboutId) + " (" + F(r.Weight) + ")"));
            });
            Row("Feels", id =>
            {
                var live = run.Minds[id].Emotions.Live;
                return live.Count == 0 ? "nothing" : string.Join(", ", live.Select(e => e.Type + (e.TargetId == null ? "" : " toward " + name(e.TargetId)) + " " + F(e.Intensity)));
            });
            Row("What they think the others know", id => "not tracked");
            sb.Append(Nl);
            sb.Append("\"Who they think took it\" has no record of its own: the simulation's beliefs are about supplies, roles, ")
              .Append("tendencies, who knows more, and who is answerable for something. The nearest record, a belief that someone ")
              .Append("is answerable for something, is shown in that row when one is held. \"Connects the night to the missing can\" ")
              .Append("is asked only of whoever remembers something from the night, and reads the beliefs that memory moved.").Append(Nl).Append(Nl);

            // Every memory any of them holds, oldest first.
            var seen = ids.SelectMany(id => run.Minds[id].Experiences)
                .GroupBy(x => x.EventId, StringComparer.Ordinal)
                .Select(g => g.First())
                .OrderBy(x => x.Day).ThenBy(x => x.Order).ThenBy(x => x.EventId, StringComparer.Ordinal)
                .ToList();
            sb.Append("### What each of them remembers at minute 0").Append(Nl).Append(Nl);
            sb.Append("One row per thing that happened, with how each of them came to know it and what they made of it.").Append(Nl).Append(Nl);
            sb.Append("| Day | What happened |");
            foreach (var id in ids) sb.Append(' ').Append(name(id)).Append(" |");
            sb.Append(Nl).Append("|---|---|");
            foreach (var _ in ids) sb.Append("---|");
            sb.Append(Nl);
            foreach (var e in seen)
            {
                sb.Append("| ").Append(e.Day).Append(" | ").Append(e.Summary).Append(" |");
                foreach (var id in ids)
                {
                    var x = run.Minds[id].Experiences.LastOrDefault(ex => ex.EventId == e.EventId);
                    sb.Append(' ').Append(x == null ? "not there" : Known(x, id)).Append(" |");
                }
                sb.Append(Nl);
            }
            return sb.ToString();
        }

        /// <summary>How somebody came to know a thing, and what they made of it.</summary>
        static string Known(Experience x, string selfId)
        {
            var how = x.ActorId == selfId ? "did it"
                    : x.Source == ExperienceSource.Overheard ? "heard it"
                    : "saw it";
            return how + ", read as " + Words(x.Meaning);
        }

        static string Belief(Belief b, Func<string, string> name)
        {
            var a = b.Args.Select(s => name(s) ?? s).ToList();
            string text;
            switch (b.Predicate)
            {
                case "supplies_short": text = "supplies are short"; break;
                case "role_claim" when a.Count == 2: text = a[0] + " " + (a[1] == "leads_family" ? "leads the family" : Words(a[1])); break;
                case "answerable_for" when a.Count == 2: text = a[0] + " is answerable for the " + Words(a[1]); break;
                case "more_knowledgeable" when a.Count == 2: text = a[0] + " knows more about " + Words(a[1]); break;
                case "tendency" when a.Count == 2: text = a[0] + " " + Words(a[1]); break;
                default: text = Words(b.Predicate) + (a.Count == 0 ? "" : " (" + string.Join(", ", a.Select(Words)) + ")"); break;
            }
            return text + " " + F(b.Confidence);
        }

        // ---------------------------------------------------------------- rooms

        static string RoomLine(Scenario001Run run, Func<string, string> name, Func<string, string> roomName)
        {
            var world = run.World;
            var parts = new List<string>();
            var empty = new List<string>();
            foreach (var room in world.House.Rooms)
            {
                var here = world.InRoom(room.Id);
                if (here.Count == 0) { empty.Add(room.DisplayName); continue; }
                parts.Add(room.DisplayName + ": " + string.Join(", ", here.Select(id =>
                {
                    var doing = run.Morning.Doing(id);
                    if (doing == null) return name(id);
                    var (act, left) = doing.Value;
                    var until = world.Minute + left;
                    return name(id) + " " + Act(act, room.Id, name, roomName, true) +
                           (act.Kind == ActionKind.GoTo ? " (arrives " + until + ")" : " (to " + until + ")");
                })));
            }
            if (empty.Count > 0) parts.Add("nobody in " + string.Join(", ", empty));
            return string.Join(" · ", parts);
        }

        // ---------------------------------------------------------------- one decision

        static string Line(
            Moment m, Dictionary<string, List<Moment>> byPerson, Scenario001Run run,
            Dictionary<string, WorldEvent> events, IReadOnlyList<InterruptionRecord> stops,
            Func<string, string> name, Func<string, string> roomName, SortedDictionary<string, string> used)
        {
            var d = m.Decision;
            var chosen = d.ChosenScored;
            var room = m.Percept.Room?.Id;
            var sb = new StringBuilder();
            sb.Append("- **").Append(name(m.Who)).Append(".** ");

            if (m.Why == "interrupted")
            {
                var stop = stops.LastOrDefault(s => s.CharacterId == m.Who && s.Minute == m.Minute);
                var mine = byPerson[m.Who];
                var prev = mine.LastOrDefault(x => x.Index < m.Index);
                if (stop != null)
                {
                    sb.Append("Stopped");
                    if (prev != null) sb.Append(" while ").Append(Act(prev.Decision.Chosen, prev.Percept.Room?.Id, name, roomName, true));
                    sb.Append(" by: \"").Append(events.TryGetValue(stop.EventId, out var e) ? e.Summary : stop.EventId)
                      .Append("\" (it stirred them ").Append(F(stop.EventIntensity)).Append("). ");
                }
            }

            if (d.Holding != null)
            {
                var what = For(d.Holding.MotiveName, d.Holding.MotiveKey, name);
                if (d.Commitment == Commitment.Held)
                {
                    sb.Append("Walked here for ").Append(what).Append(", so only acts serving it were weighed");
                    var top = d.Ranked[0];
                    if (!top.Option.SameAs(d.Chosen))
                        sb.Append("; ").Append(Act(top.Option, room, name, roomName, true)).Append(" would otherwise have scored higher (")
                          .Append(F(top.Score)).Append(" against ").Append(F(chosen.Score)).Append(")");
                    sb.Append(". ");
                }
                else
                {
                    sb.Append("Walked here for ").Append(what).Append(" and gave it up: ").Append(Lapse(d.Commitment)).Append(".");
                    var best = d.Ranked.FirstOrDefault(r => r.Contributions.Any(c => c.Amount > 0.0 && c.MotiveKey == d.Holding.MotiveKey));
                    if (best != null)
                        sb.Append(' ').Append(Cap(Act(best.Option, room, name, roomName, true))).Append(" here scored ").Append(S(best.Score))
                          .Append(Against(best, used)).Append(".");
                    sb.Append(" Weighed everything again. ");
                }
            }

            var strongest = m.Motives.Count == 0 ? null : m.Motives[0];
            sb.Append("Wanted most: ").Append(strongest == null ? "nothing in particular" : Most(strongest, name) + " (" + F(strongest.Urgency) + ")").Append(". ");

            sb.Append("**Chose: ").Append(Act(d.Chosen, room, name, roomName, false)).Append("**");
            var leading = d.Leading;
            sb.Append(leading == null ? ", for no want at all (\"nothing pressing\")" : ", for " + For(leading.Name, leading.Key, name));
            var ways = chosen.Contributions.Where(c => c.Amount > 0.0).OrderByDescending(c => c.Amount).ThenBy(c => c.ProposalId, StringComparer.Ordinal)
                .Select(c => c.ProposalId).Distinct().ToList();
            if (ways.Count > 0) sb.Append(": ").Append(string.Join(", ", ways.Select(w => Way(w, used))));
            sb.Append(".");
            if (chosen.Cost > 0.0) sb.Append(" Cost to them:").Append(Prices(chosen, used).TrimStart(',')).Append(".");

            if (d.Chosen.Kind == ActionKind.GoTo && leading != null)
            {
                var f = m.Foresaw.FirstOrDefault(x => x.Walk == d.Chosen.Key && x.Want == leading.Key);
                if (f != null && f.End != null)
                    sb.Append(" Pictured ").Append(EndAct(f, name, roomName)).Append(" there: ").Append(S(f.Score.Value)).Append(".");
            }

            var unserved = Unserved(m, name, roomName, used);
            if (unserved != null) sb.Append(' ').Append(unserved.Text());

            sb.Append(' ').Append(Settled(d, room, name, roomName));

            if (m.Record.Outcome == "thought again, and carried on")
                sb.Append(" Weighed it again and carried on with it.");
            else
                sb.Append(" Came of it: ").Append(Outcome(m, byPerson, run, name, roomName));
            return sb.ToString();
        }

        static string Settled(Decision d, string room, Func<string, string> name, Func<string, string> roomName)
        {
            if (d.Resolution == Resolution.Ambiguous)
            {
                var among = d.Tied.Select(o => Act(o, room, name, roomName, false) + " (" + F(d.Ranked.First(r => r.Option.SameAs(o)).Score) + ")");
                return "**DICE** between " + string.Join(", ", among) + ": it picked " + Act(d.Chosen, room, name, roomName, false) + ".";
            }
            var next = d.Considered.Count > 1 ? d.Considered[1] : null;
            return next == null
                ? "Clear: the only act weighed."
                : "Clear, " + F(d.Margin) + " ahead of " + Act(next.Option, room, name, roomName, true) + ".";
        }

        static string Outcome(Moment m, Dictionary<string, List<Moment>> byPerson, Scenario001Run run, Func<string, string> name, Func<string, string> roomName)
        {
            if (m.Record.Outcome != null) return Sentence(Plain(m.Record.Outcome, run, name, roomName));
            var next = byPerson[m.Who].FirstOrDefault(x => x.Index > m.Index);
            if (next == null) return "still at it when the morning ended.";
            if (next.Why == "interrupted") return "stopped at minute " + next.Minute + " before it was done.";
            return "nothing recorded.";
        }

        // ---------------------------------------------------------------- runs

        /// <summary>Two decisions are the same when everything a line says about them but the numbers is the same.</summary>
        static string RunKey(Moment m)
        {
            var d = m.Decision;
            if (m.Why != "finished" || d.Holding != null || d.Resolution != Resolution.Clear) return null;
            if (m.Record.Outcome == "thought again, and carried on") return null;
            if (m.Motives.Count == 0 || d.Leading == null) return null;
            var costs = string.Join(",", d.ChosenScored.Prices.Select(p => p.Split(' ')[0]));
            var unserved = UnservedKey(m);
            return string.Join("|", d.Chosen.Key, d.Leading.Key, m.Motives[0].Key, m.Percept.Room?.Id, costs, unserved);
        }

        static string RunLine(
            List<Moment> same, Dictionary<string, List<Moment>> byPerson, Scenario001Run run,
            Func<string, string> name, Func<string, string> roomName, SortedDictionary<string, string> used)
        {
            var first = same[0];
            var last = same[same.Count - 1];
            var d = first.Decision;
            var room = first.Percept.Room?.Id;
            var strongest = first.Motives[0];
            var sb = new StringBuilder();
            sb.Append("- **").Append(name(first.Who)).Append(", minutes ").Append(first.Minute).Append("–").Append(last.Minute)
              .Append(" (").Append(same.Count).Append(" decisions, the same each time).** ");
            sb.Append("Wanted most: ").Append(Most(strongest, name)).Append(", ").Append(Change(same.Select(x => x.Motives[0].Urgency).ToList())).Append(". ");
            sb.Append("**Chose: ").Append(Act(d.Chosen, room, name, roomName, false)).Append("** each time, for ").Append(For(d.Leading.Name, d.Leading.Key, name));
            var ways = same.SelectMany(x => x.Decision.ChosenScored.Contributions)
                .Where(c => c.Amount > 0.0 && c.MotiveKey == d.Leading.Key)
                .Select(c => c.ProposalId).Distinct().OrderBy(p => p, StringComparer.Ordinal).ToList();
            if (ways.Count > 0) sb.Append(": ").Append(string.Join(", ", ways.Select(w => Way(w, used))));
            sb.Append(".");
            var others = same.SelectMany(x => x.Decision.ChosenScored.Contributions)
                .Where(c => c.Amount > 0.0 && c.MotiveKey != d.Leading.Key)
                .Select(c => c.MotiveKey).Distinct().OrderBy(k => k, StringComparer.Ordinal).ToList();
            if (others.Count > 0)
                sb.Append(" At times it also served ").Append(string.Join(" and ", others.Select(k => For(k.Split(':')[0], k, name)))).Append(".");

            var notes = same.Select(x => Unserved(x, name, roomName, used)).ToList();
            if (notes[0] != null) sb.Append(' ').Append(UnservedNote.Range(notes));

            sb.Append(" Clear every time, by ").Append(Range(same.Select(x => x.Decision.Margin).ToList())).Append(".");
            var endings = same.Select(x => Outcome(x, byPerson, run, name, roomName)).ToList();
            var distinct = endings.Distinct().ToList();
            sb.Append(" Came of it: ");
            if (distinct.Count == 1) sb.Append(distinct[0]).Append(distinct[0].EndsWith(".") ? "" : ".");
            else
            {
                var common = endings.GroupBy(x => x).OrderByDescending(g => g.Count()).First().Key;
                sb.Append(common.TrimEnd('.'));
                foreach (var x in same.Where((x, i) => endings[i] != common))
                    sb.Append("; at minute ").Append(x.Minute).Append(", ").Append(Outcome(x, byPerson, run, name, roomName).TrimEnd('.'));
                sb.Append(".");
            }
            return sb.ToString();
        }

        // ---------------------------------------------------------------- the strongest want, when the act did not serve it

        /// <summary>
        /// Why the strongest want got nothing from the act chosen: the best act for
        /// it scored lower, a walk for it was pictured as not worth making, or
        /// nothing here served it at all.
        /// </summary>
        sealed class UnservedNote
        {
            public string Key;
            public string What;
            public string Act;
            public List<string> Against = new List<string>();
            public List<string> AgainstWithAmounts = new List<string>();
            public string Walk;
            public double? Score;

            public string Text()
            {
                if (Key.StartsWith("best:", StringComparison.Ordinal))
                    return Cap(What) + " went unserved: the best act for it, " + Act + ", scored " + S(Score.Value) +
                           (AgainstWithAmounts.Count == 0 ? "" : " (against: " + string.Join(", ", AgainstWithAmounts) + ")") + ".";
                if (Key.StartsWith("walk:", StringComparison.Ordinal))
                    return Walk + " for " + What + " was pictured as not worth it (" + (Act == null ? "nothing there would serve it" : Act + " there: " + S(Score.Value)) + ").";
                return "Nothing here served " + What + ".";
            }

            public static string Range(List<UnservedNote> notes)
            {
                var n = notes[0];
                var scores = RangeS(notes.Select(x => x.Score).ToList());
                if (n.Key.StartsWith("best:", StringComparison.Ordinal))
                    return Cap(n.What) + " went unserved every time: the best act for it, " + n.Act + ", scored " + scores +
                           (n.Against.Count == 0 ? "" : " (against: " + string.Join(", ", n.Against) + ")") + ".";
                if (n.Key.StartsWith("walk:", StringComparison.Ordinal))
                    return n.Walk + " for " + n.What + " was pictured as not worth it every time (" + (n.Act == null ? "nothing there would serve it" : n.Act + " there: " + scores) + ").";
                return "Nothing here served " + n.What + ".";
            }
        }

        static string UnservedKey(Moment m) => Unserved(m, id => id, id => id, new SortedDictionary<string, string>())?.Key ?? "served";

        static UnservedNote Unserved(Moment m, Func<string, string> name, Func<string, string> roomName, SortedDictionary<string, string> used)
        {
            if (m.Motives.Count == 0) return null;
            var d = m.Decision;
            var s = m.Motives[0];
            var chosen = d.ChosenScored;
            if (chosen.Contributions.Any(c => c.Amount > 0.0 && c.MotiveKey == s.Key)) return null;

            var room = m.Percept.Room?.Id;
            var note = new UnservedNote { What = For(s.Name, s.Key, name) };
            var best = d.Ranked.FirstOrDefault(r => r.Contributions.Any(c => c.Amount > 0.0 && c.MotiveKey == s.Key));
            if (best != null)
            {
                // Beaten on the dice, not weighed because a walk's reason held, or the
                // very act a lapsed walk was for: the line says so already.
                if (best.Score >= chosen.Score) return null;
                if (d.Tied.Any(o => o.SameAs(best.Option))) return null;
                if (d.Holding != null && d.Commitment != Commitment.Held && d.Holding.MotiveKey == s.Key) return null;
                note.Key = "best:" + best.Option.Key + ":" + string.Join(",", best.Prices.Select(p => p.Split(' ')[0]));
                note.Act = Act(best.Option, room, name, roomName, true);
                note.Score = best.Score;
                foreach (var p in best.Prices)
                {
                    var parts = p.Split(' ');
                    note.Against.Add(Cost(parts[0], used));
                    note.AgainstWithAmounts.Add(Cost(parts[0], used) + (parts.Length > 1 ? " " + parts[1] : ""));
                }
                return note;
            }

            var walk = m.Foresaw.Where(f => f.Want == s.Key && f.NotWorth).OrderBy(f => f.Walk, StringComparer.Ordinal).FirstOrDefault();
            if (walk != null)
            {
                note.Key = "walk:" + walk.Walk + ":" + walk.End;
                note.Walk = "Walking to the " + roomName(walk.Destination);
                note.Act = walk.End == null ? null : EndAct(walk, name, roomName);
                note.Score = walk.Score;
                return note;
            }

            note.Key = "none";
            return note;
        }

        static string Against(ScoredOption o, SortedDictionary<string, string> used)
            => o.Cost > 0.0 ? " (against:" + Prices(o, used).TrimStart(',') + ")" : "";

        static string Prices(ScoredOption o, SortedDictionary<string, string> used)
        {
            var sb = new StringBuilder();
            foreach (var p in o.Prices)
            {
                var parts = p.Split(' ');
                sb.Append(", ").Append(Cost(parts[0], used));
                if (parts.Length > 1) sb.Append(' ').Append(parts[1]);
            }
            return sb.ToString();
        }

        // ---------------------------------------------------------------- foresight, as the deliberation recorded it

        static readonly Regex ForesightEntry = new Regex(
            @"^(?<walk>\S+) for (?<want>\S+): (?:(?<end>\S+) (?<score>[+-]\d+(?:\.\d+)?)|nothing there serves it)(?<no>, not worth walking for)?$",
            RegexOptions.CultureInvariant);

        static List<Foresight> Foresights(Scenario001Run run, Decision d)
        {
            var list = new List<Foresight>();
            var record = run.Trace.Get(d.TraceId);
            if (record?.Data == null || !record.Data.TryGetValue("foresaw", out var text) || string.IsNullOrEmpty(text)) return list;
            foreach (var entry in text.Split(new[] { "; " }, StringSplitOptions.RemoveEmptyEntries))
            {
                var m = ForesightEntry.Match(entry);
                if (!m.Success) continue;
                var walk = m.Groups["walk"].Value;
                var arrow = walk.IndexOf("->", StringComparison.Ordinal);
                list.Add(new Foresight
                {
                    Walk = walk,
                    Destination = arrow < 0 ? null : walk.Substring(arrow + 2),
                    Want = m.Groups["want"].Value,
                    End = m.Groups["end"].Success ? m.Groups["end"].Value : null,
                    Score = m.Groups["score"].Success ? double.Parse(m.Groups["score"].Value, CultureInfo.InvariantCulture) : (double?)null,
                    NotWorth = m.Groups["no"].Success
                });
            }
            return list;
        }

        static string EndAct(Foresight f, Func<string, string> name, Func<string, string> roomName)
        {
            var key = f.End;
            if (key.StartsWith("comfort:", StringComparison.Ordinal)) return "sitting with " + name(key.Substring(8));
            if (key.StartsWith("observe:", StringComparison.Ordinal)) return "watching " + name(key.Substring(8));
            switch (key)
            {
                case "wait": return "staying put";
                case "eat": return "eating";
                case "check_pantry": return "counting the pantry";
                case "search_room": return "searching the " + roomName(f.Destination);
                default: return Words(key);
            }
        }

        // ---------------------------------------------------------------- words

        static string Act(ActionOption a, string roomId, Func<string, string> name, Func<string, string> roomName, bool ing)
        {
            switch (a.Kind)
            {
                case ActionKind.Wait: return ing ? "staying put" : "stay put";
                case ActionKind.Observe: return (ing ? "watching " : "watch ") + name(a.TargetId);
                case ActionKind.GoTo: return (ing ? "walking to the " : "walk to the ") + roomName(a.DestinationRoomId);
                case ActionKind.CheckPantry: return ing ? "counting the pantry" : "count the pantry";
                case ActionKind.SearchRoom: return (ing ? "searching the " : "search the ") + roomName(roomId);
                case ActionKind.Comfort: return (ing ? "sitting with " : "sit with ") + name(a.TargetId);
                case ActionKind.Eat: return ing ? "eating" : "eat a portion";
                default: return a.KindName;
            }
        }

        static readonly Dictionary<string, string[]> WantWords = new Dictionary<string, string[]>(StringComparer.Ordinal)
        {
            // { what they want, what an act is for }
            { "find_out", new[] { "to know what happened to the can", "knowing what happened" } },
            { "get_food", new[] { "food", "food" } },
            { "guard_supplies", new[] { "to make the food last", "making the food last" } },
            { "avoid_exposure", new[] { "not to be looked at", "not being looked at" } },
            { "restore_standing", new[] { "to be the one who settles it", "being the one who settles it" } },
            { "keep_peace", new[] { "to keep the house calm", "keeping the house calm" } },
            { "look_after", new[] { "to look after {0}", "looking after {0}" } }
        };

        static string Most(Motive m, Func<string, string> name) => WantWord(m.Name, m.TargetId, name, 0);

        static string For(string motiveName, string motiveKey, Func<string, string> name)
        {
            var colon = motiveKey.IndexOf(':');
            return WantWord(motiveName, colon < 0 ? null : motiveKey.Substring(colon + 1), name, 1);
        }

        static string WantWord(string motiveName, string target, Func<string, string> name, int form)
        {
            if (!WantWords.TryGetValue(motiveName, out var words))
                return Words(motiveName) + (target == null ? "" : " (" + name(target) + ")");
            return string.Format(CultureInfo.InvariantCulture, words[form], target == null ? "" : name(target));
        }

        static readonly Dictionary<string, string> WayWords = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            { "eat_it", "eating" },
            { "go_where_the_food_is", "walk to where the food is" },
            { "see_what_there_is", "counting shows what food there is" },
            { "count_it_properly", "counting properly helps it last" },
            { "leave_it_alone", "staying put leaves the food alone" },
            { "keep_it_in_sight", "walk to where the food is, to keep it in sight" },
            { "turn_the_room_over", "searching a room is how you find out" },
            { "look_at_the_shelf_yourself", "counting the shelf yourself tells you what happened" },
            { "watch_them", "watching people may show what happened" },
            { "somewhere_worth_looking", "once this room is searched, walk to the nearest private room you have not searched" },
            { "get_out_of_the_room", "with people around, walk out to the next room" },
            { "somewhere_with_a_door", "a private room is somewhere not to be seen" },
            { "stay_out_of_the_way", "alone, staying put keeps you out of sight" },
            { "be_the_one_who_settles_it", "searching is taking charge" },
            { "check_it_yourself", "checking it yourself is taking charge" },
            { "keep_an_eye_on_them", "keeping an eye on them is taking charge" },
            { "let_it_be", "staying put keeps the house calm" },
            { "be_where_they_are", "walk to where the others are" },
            { "settle_them_down", "sitting with anyone calms the house" },
            { "sit_with_them", "sitting with someone is how you look after them" },
            { "see_how_they_are", "watching someone shows how they are" },
            { "go_to_where_they_will_be", "walk to where people gather" }
        };

        static readonly Dictionary<string, string> CostWords = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            { "taking_it_when_there_is_little", "not when there is so little" },
            { "not_while_they_are_watching", "not in front of the others" },
            { "going_through_what_is_not_yours", "going through someone else's things" },
            { "with_them_standing_right_there", "with them standing right there" },
            { "staring_at_somebody", "staring at someone" },
            { "reaching_out_does_not_come_easily_to_everyone", "reaching out does not come easily" },
            { "getting_up_and_going_somewhere", "the effort of getting up and going" },
            { "opening_the_cupboard_again", "opening the cupboard again" }
        };

        static string Way(string id, SortedDictionary<string, string> used)
        {
            var text = WayWords.TryGetValue(id, out var w) ? w : Words(id);
            used[text] = id;
            return "*" + text + "*";
        }

        static string Cost(string id, SortedDictionary<string, string> used)
        {
            var text = CostWords.TryGetValue(id, out var w) ? w : Words(id);
            used[text] = id;
            return "*" + text + "*";
        }

        static string Lapse(string commitment)
        {
            switch (commitment)
            {
                case Commitment.NoLongerWanted: return "no longer wanted";
                case Commitment.Impossible: return "nothing here serves it";
                case Commitment.NotWorthIt: return "not worth what it costs here";
                default: return commitment;
            }
        }

        static string RuleTable(SortedDictionary<string, string> used)
        {
            var sb = new StringBuilder();
            sb.Append("## Rules named in the story").Append(Nl).Append(Nl);
            sb.Append("All are in `Assets/_Project/Data/Rules/decisions.json` (`proposals` and `costs`).").Append(Nl).Append(Nl);
            sb.Append("| In the story | Rule id |").Append(Nl).Append("|---|---|").Append(Nl);
            foreach (var pair in used) sb.Append("| *").Append(pair.Key).Append("* | `").Append(pair.Value).Append("` |").Append(Nl);
            return sb.ToString();
        }

        /// <summary>A simulation outcome string with ids replaced by the names people use.</summary>
        static string Plain(string text, Scenario001Run run, Func<string, string> name, Func<string, string> roomName)
        {
            var owned = Regex.Match(text, @"^went through (\w+) things$", RegexOptions.CultureInvariant);
            if (owned.Success && run.Minds.ContainsKey(owned.Groups[1].Value))
                return "went through " + name(owned.Groups[1].Value) + "'s things";
            return Regex.Replace(text, @"[a-z_]+", w =>
            {
                if (run.Minds.ContainsKey(w.Value)) return name(w.Value);
                if (run.World.House.Has(w.Value)) return "the " + roomName(w.Value);
                return w.Value;
            }, RegexOptions.CultureInvariant);
        }

        static string Words(string id) => id?.Replace('_', ' ');

        static string Cap(string s) => string.IsNullOrEmpty(s) ? s : char.ToUpperInvariant(s[0]) + s.Substring(1);

        static string Sentence(string s) => string.IsNullOrEmpty(s) ? s : (s.EndsWith(".") ? s : s + ".");

        static string F(double v) => v.ToString("0.00", CultureInfo.InvariantCulture);

        static string S(double v) => v.ToString("+0.00;−0.00;0.00", CultureInfo.InvariantCulture);

        static string Range(List<double> xs)
        {
            var lo = xs.Min();
            var hi = xs.Max();
            return F(lo) == F(hi) ? F(lo) : F(lo) + " to " + F(hi);
        }

        static string RangeS(List<double?> xs)
        {
            var v = xs.Where(x => x.HasValue).Select(x => x.Value).ToList();
            if (v.Count == 0) return "";
            var lo = v.Min();
            var hi = v.Max();
            return S(lo) == S(hi) ? S(lo) : S(lo) + " to " + S(hi);
        }

        static string Change(List<double> xs)
        {
            var a = F(xs[0]);
            var b = F(xs[xs.Count - 1]);
            if (a == b) return "steady at " + a;
            return (xs[xs.Count - 1] > xs[0] ? "rising from " : "falling from ") + a + " to " + b;
        }
    }
}
