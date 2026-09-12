using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Fallow.Core.Model;
using Newtonsoft.Json.Linq;

namespace Fallow.Core.Data
{
    public static class MorningLoader
    {
        public static MorningScenario LoadFile(string path) => FromJson(File.ReadAllText(path));

        public static MorningScenario FromJson(string json)
        {
            var root = JObject.Parse(json);

            var house = ReadHouse(root["house"] as JObject);
            var start = root["start"] as JObject;

            var rooms = new Dictionary<string, string>(StringComparer.Ordinal);
            if (start?["rooms"] is JObject roomsNode)
                foreach (var p in roomsNode)
                    rooms[p.Key] = p.Value?.Value<string>();

            var hunger = new Dictionary<string, double>(StringComparer.Ordinal);
            if (start?["hunger"] is JObject hungerNode)
                foreach (var p in hungerNode)
                    hunger[p.Key] = p.Value?.Value<double>() ?? 0.0;

            var variants = ReadVariants(root["variants"] as JArray);
            var heldOut = ReadVariants(root["held_out_variants"] as JArray);

            return new MorningScenario(
                root["id"]?.Value<string>(),
                root["description"]?.Value<string>(),
                root["day"]?.Value<int>() ?? 0,
                root["minutes"]?.Value<int>() ?? 0,
                house,
                start?["portions"]?.Value<int>() ?? 0,
                rooms,
                hunger,
                root["opening"] is JObject opening ? ScenarioLoader.ReadEvent(opening) : null,
                variants,
                heldOut);
        }

        static List<MorningVariant> ReadVariants(JArray node)
        {
            var variants = new List<MorningVariant>();
            if (node == null) return variants;

            foreach (var v in node)
            {
                var nights = new List<WorldEvent>();
                if (v["night_events"] is JArray nightNode)
                    foreach (var e in nightNode)
                        nights.Add(ScenarioLoader.ReadEvent((JObject)e));

                variants.Add(new MorningVariant(v["id"]?.Value<string>(), v["note"]?.Value<string>(), nights));
            }

            return variants;
        }

        public static RoomGraph ReadHouse(JObject o)
        {
            var house = new RoomGraph();
            if (o == null) return house;

            if (o["rooms"] is JArray roomsNode)
                foreach (var r in roomsNode)
                    house.AddRoom(new Room(
                        r["id"]?.Value<string>(),
                        r["name"]?.Value<string>(),
                        ScenarioLoader.ReadStrings(r["tags"]),
                        ScenarioLoader.ReadStrings(r["owners"])));

            if (o["connections"] is JArray linksNode)
                foreach (var c in linksNode)
                    house.Connect(
                        c["a"]?.Value<string>(),
                        c["b"]?.Value<string>(),
                        c["audible"]?.Value<bool>() ?? false);

            return house;
        }
    }

    /// <summary>
    /// Checks the morning against the vocabulary, the cast and the house.
    ///
    /// The check that matters is the last one: a night event may only be
    /// witnessed by people the scenario says were there. Authoring a secret that
    /// somebody knows without having been present would quietly undo the one
    /// property the whole design rests on.
    /// </summary>
    public static class MorningValidator
    {
        public static IReadOnlyList<string> Validate(
            MorningScenario morning, Vocabulary vocab, IReadOnlyDictionary<string, Profile> cast)
        {
            var problems = new List<string>();

            if (morning.House.Rooms.Count == 0) problems.Add("the house has no rooms");
            if (morning.Minutes <= 0) problems.Add("the morning has no length");
            if (morning.Portions < 0) problems.Add("the pantry holds a negative amount");

            foreach (var room in morning.House.Rooms)
            {
                if (string.IsNullOrEmpty(room.Id)) problems.Add("a room has no id");
                foreach (var tag in room.Tags)
                    if (!vocab.Contains("room_tags", tag))
                        problems.Add("room '" + room.Id + "': '" + tag + "' is not a kind of room");
                foreach (var owner in room.OwnerIds)
                    if (!cast.ContainsKey(owner))
                        problems.Add("room '" + room.Id + "': '" + owner + "' is not in the cast");
                if (morning.House.Adjacent(room.Id).Count == 0)
                    problems.Add("room '" + room.Id + "' has no way in or out");
            }

            foreach (var id in cast.Keys)
            {
                if (!morning.StartRooms.TryGetValue(id, out var room))
                    problems.Add("'" + id + "' does not start anywhere");
                else if (!morning.House.Has(room))
                    problems.Add("'" + id + "' starts in '" + room + "', which is not a room");

                if (!morning.StartHunger.ContainsKey(id))
                    problems.Add("'" + id + "' starts with no hunger set");
            }

            if (morning.Opening == null) problems.Add("the morning has no opening event");

            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var v in morning.Variants.Concat(morning.HeldOutVariants))
            {
                if (string.IsNullOrEmpty(v.Id)) problems.Add("a variant has no id");
                else if (!ids.Add(v.Id)) problems.Add("two variants share the id '" + v.Id + "'");

                foreach (var e in v.NightEvents)
                {
                    if (e.ActorId != null && !cast.ContainsKey(e.ActorId))
                        problems.Add("variant '" + v.Id + "': '" + e.ActorId + "' is not in the cast");
                    if (e.Action != null && !vocab.Contains("actions", e.Action))
                        problems.Add("variant '" + v.Id + "': '" + e.Action + "' is not an action");
                    if (e.Intent != null && !vocab.Contains("self_meanings", e.Intent))
                        problems.Add("variant '" + v.Id + "': '" + e.Intent + "' is not an intention");

                    foreach (var w in e.Witnesses)
                        if (!cast.ContainsKey(w))
                            problems.Add("variant '" + v.Id + "': '" + w + "' is not in the cast");
                }
            }

            return problems;
        }
    }
}
