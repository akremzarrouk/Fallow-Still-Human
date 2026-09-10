using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Fallow.Core.Model;
using Newtonsoft.Json.Linq;

namespace Fallow.Core.Data
{
    public static class ProfileLoader
    {
        public static Profile FromJson(string json)
        {
            var o = JObject.Parse(json);

            var traits = new Dictionary<string, double>();
            if (o["traits"] is JObject traitsNode)
                foreach (var p in traitsNode)
                    traits[p.Key] = p.Value?.Value<double>() ?? 0.0;

            var values = new List<string>();
            if (o["values"] is JArray valuesNode)
                foreach (var v in valuesNode)
                {
                    var s = v.Value<string>();
                    if (s != null) values.Add(s);
                }

            var perception = o["perception"] as JObject;
            var perceptiveness = perception?["perceptiveness"]?.Value<double>() ?? 0.0;

            var attention = new Dictionary<string, double>();
            if (perception?["attention"] is JObject attentionNode)
                foreach (var p in attentionNode)
                    attention[p.Key] = p.Value?.Value<double>() ?? 1.0;

            var beliefs = new List<BeliefSeed>();
            if (o["initial_beliefs"] is JArray beliefsNode)
                foreach (var b in beliefsNode)
                {
                    var args = new List<string>();
                    if (b["args"] is JArray argsNode)
                        foreach (var a in argsNode)
                        {
                            var s = a.Value<string>();
                            if (s != null) args.Add(s);
                        }

                    beliefs.Add(new BeliefSeed(
                        b["predicate"]?.Value<string>(),
                        args,
                        b["confidence"]?.Value<double>() ?? 0.0));
                }

            return new Profile(
                o["id"]?.Value<string>(),
                o["display_name"]?.Value<string>(),
                o["age"]?.Value<int>() ?? 0,
                o["family_role"]?.Value<string>(),
                traits,
                values,
                perceptiveness,
                attention,
                beliefs);
        }

        /// <summary>Loads every character file in a folder, keyed by character id.</summary>
        public static IReadOnlyDictionary<string, Profile> LoadDirectory(string path)
        {
            var cast = new Dictionary<string, Profile>(StringComparer.Ordinal);

            foreach (var file in Directory.GetFiles(path, "*.json").OrderBy(f => f, StringComparer.Ordinal))
            {
                var profile = FromJson(File.ReadAllText(file));
                if (string.IsNullOrEmpty(profile.Id))
                    throw new InvalidDataException($"Character file has no id: {file}");
                if (cast.ContainsKey(profile.Id))
                    throw new InvalidDataException($"Two character files share the id '{profile.Id}': {file}");
                cast[profile.Id] = profile;
            }

            return cast;
        }
    }
}
