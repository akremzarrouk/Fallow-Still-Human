using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Fallow.Core.Model;
using Newtonsoft.Json.Linq;

namespace Fallow.Core.Data
{
    public static class ScenarioLoader
    {
        public static ScenarioScript LoadFile(string path) => FromJson(File.ReadAllText(path));

        public static ScenarioScript FromJson(string json)
        {
            var root = JObject.Parse(json);

            var characters = ReadStrings(root["characters"]);
            var events = new List<WorldEvent>();
            if (root["events"] is JArray eventsNode)
                foreach (var e in eventsNode)
                    events.Add(ReadEvent((JObject)e));

            return new ScenarioScript(
                root["id"]?.Value<string>(),
                root["description"]?.Value<string>(),
                characters,
                events.OrderBy(e => e.Order).ToList());
        }

        public static WorldEvent EventFromJson(string json) => ReadEvent(JObject.Parse(json));

        static WorldEvent ReadEvent(JObject o)
        {
            var typeName = o["type"]?.Value<string>();
            var kind = string.Equals(typeName, "speech", StringComparison.Ordinal)
                ? EventKind.Speech
                : EventKind.Action;

            var effects = new List<LedgerEffect>();
            if (o["ledger_effects"] is JArray effectsNode)
                foreach (var f in effectsNode)
                    effects.Add(new LedgerEffect(
                        f["holder"]?.Value<string>(),
                        f["about"]?.Value<string>(),
                        f["entry"]?.Value<string>(),
                        f["weight"]?.Value<double>() ?? 0.0));

            return new WorldEvent(
                o["id"]?.Value<string>(),
                o["day"]?.Value<int>() ?? 0,
                o["order"]?.Value<int>() ?? 0,
                kind,
                o["actor"]?.Value<string>(),
                o["target"]?.Value<string>(),
                o["act"]?.Value<string>(),
                o["action"]?.Value<string>(),
                o["topic"]?.Value<string>(),
                o["tone"]?.Value<string>(),
                o["directness"]?.Value<string>(),
                o["valence"]?.Value<string>(),
                o["intent"]?.Value<string>(),
                o["summary"]?.Value<string>(),
                ReadStrings(o["witnesses"]),
                ReadStrings(o["overhearers"]),
                effects);
        }

        static List<string> ReadStrings(JToken node)
        {
            var list = new List<string>();
            if (node is JArray arr)
                foreach (var item in arr)
                {
                    var s = item.Value<string>();
                    if (s != null) list.Add(s);
                }
            return list;
        }
    }
}
