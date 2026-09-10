using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Fallow.Core.Data
{
    public static class VocabularyLoader
    {
        public static Vocabulary LoadFile(string path)
            => FromJson(File.ReadAllText(path));

        public static Vocabulary FromJson(string json)
        {
            var root = JObject.Parse(json);

            var sets = new Dictionary<string, IReadOnlyCollection<string>>();
            if (root["sets"] is JObject setsNode)
            {
                foreach (var pair in setsNode)
                {
                    var names = new HashSet<string>();
                    foreach (var item in pair.Value)
                    {
                        var s = item.Value<string>();
                        if (s != null) names.Add(s);
                    }
                    sets[pair.Key] = names;
                }
            }

            var predicates = new Dictionary<string, BeliefPredicateSpec>();
            if (root["belief_predicates"] is JObject predsNode)
            {
                foreach (var pair in predsNode)
                {
                    var domains = new List<string>();
                    if (pair.Value?["arg_domains"] != null)
                    {
                        foreach (var item in pair.Value["arg_domains"])
                        {
                            var s = item.Value<string>();
                            if (s != null) domains.Add(s);
                        }
                    }
                    predicates[pair.Key] = new BeliefPredicateSpec(domains);
                }
            }

            return new Vocabulary(sets, predicates);
        }

        /// <summary>Shared reader settings: data files are read strictly, so a malformed number is an error.</summary>
        internal static readonly JsonSerializerSettings Settings = new JsonSerializerSettings
        {
            FloatParseHandling = FloatParseHandling.Double,
            DateParseHandling = DateParseHandling.None,
            MissingMemberHandling = MissingMemberHandling.Ignore
        };
    }
}
