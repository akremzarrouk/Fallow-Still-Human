using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;
using Newtonsoft.Json.Linq;
using NUnit.Framework;
using Candidate = Fallow.Tests.Core.IntentionSelector.Candidate;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// What must a route contain to decide whether it applies at all, before
    /// its support and inhibitors are combined?
    ///
    /// Eight representations read the cases of
    /// `Data/Experiments/route-applicability.json` by fixed rules committed with
    /// the predictions: S (the shipped selector), A (the causal-route
    /// experiment's D, unchanged), B (typed roles), C (an applicability layer)
    /// and four ablations of C. The route layer (does a route apply?) is judged;
    /// the selection layer (what is chosen when nothing applies?) is reported
    /// under two policies and judged by nothing. Nothing here is production.
    /// Writes `Docs/experiments/route-applicability/measurements.md`.
    /// </summary>
    public class RouteApplicabilityExperimentTests
    {
        static readonly Dictionary<string, string> Frozen = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["Data/Experiments/intentions.json"] = "61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92",
            ["Data/Experiments/causal-routes.json"] = "781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a",
            ["Data/Experiments/held-out-people.json"] = "0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131",
            ["Data/Experiments/reason-semantics.json"] = "5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638",
            ["Data/Experiments/route-applicability.json"] = "a0e965403d21a218ae63d3857acf0edaabf159f7603448b1b8a304257c8ce426",
            ["Tests/EditMode/CausalRouteExperimentTests.cs"] = "3fb852f2cb7763a44d331b62e0c8897e720228ff5cd2b32fbf177908039212c4",
            ["Tests/EditMode/ReasonSemanticsExperimentTests.cs"] = "4bc51cbd4b0f3069de99845c9ef693fab1a482b82683e97c8b370aaf7f1c6d79",
            ["Tests/EditMode/IntentionSelector.cs"] = "8553b74ff0189f4be5cb10e2fded0a9d7c37268bf46eca3d42e3785b23f39cfd"
        };

        const double Tie = 1e-9;
        const double SameCoef = 1e-12;
        const int MorningSeeds = 10;
        const string Prefix = "circumstance:";

        static Scenario001Content _content;
        static JObject _spec;
        static JObject _routesJson;
        static readonly SortedDictionary<string, string> _results = new SortedDictionary<string, string>(StringComparer.Ordinal);
        static readonly string[] Wants = { "avoid_exposure", "find_out", "get_food", "guard_supplies", "keep_peace", "look_after", "restore_standing" };
        static readonly string[] Cast = { "daniel", "elena", "leo", "mara" };

        static List<string> _traits;
        static List<double> _traitLevels;
        static List<string> _ring;
        static List<List<BeliefSeed>> _beliefSets;
        static Mind[] _minds;
        static RoomGraph _house;
        static string _kitchen;

        // ============================================================ representations

        enum Rep { S, A, B, C, CEntity, CConditions, CSplit, CKind, BW }

        static readonly Rep[] Main = { Rep.S, Rep.A, Rep.B, Rep.C, Rep.CEntity, Rep.CConditions, Rep.CSplit, Rep.CKind };

        static string Name(Rep r)
        {
            switch (r)
            {
                case Rep.CEntity: return "C-entity";
                case Rep.CConditions: return "C-conditions";
                case Rep.CSplit: return "C-split";
                case Rep.CKind: return "C-kind";
                case Rep.BW: return "B+w";
                default: return r.ToString();
            }
        }

        static bool Circ(Rep r) => r == Rep.C || r == Rep.CEntity || r == Rep.CConditions || r == Rep.CSplit || r == Rep.CKind;
        static bool ReadsConditions(Rep r) => r == Rep.B || r == Rep.C || r == Rep.CEntity || r == Rep.CSplit || r == Rep.CKind || r == Rep.BW;
        static bool ReadsRoles(Rep r) => r != Rep.S && r != Rep.A;

        // ============================================================ facts, situations, cases

        static readonly List<string> _keys = new List<string>();
        static readonly Dictionary<string, int> _keyIndex = new Dictionary<string, int>(StringComparer.Ordinal);
        static readonly List<Scaler> _keyScaler = new List<Scaler>();
        static double[][] _lv;

        sealed class Sit
        {
            public string Id;
            public List<string> Present;
        }

        static List<Sit> _sits;
        static Percept[][] _percepts;       // [profile][situation]
        static Percept[] _company;          // [profile], the causal-route experiment's company: a, b, c
        static Percept[] _alone;

        sealed class Term
        {
            public string Key;
            public int K;
            public double Factor;
            public string Role;
            public string Kind;
        }

        sealed class Rule
        {
            public string Id;
            public string Intent;
            public string Route;
            public SituationCondition When;
            public string Gate;
            public double Base;
            public List<Term> Terms = new List<Term>();
            public List<string> Motives = new List<string>();
        }

        sealed class Route
        {
            public string Key;
            public string Intent;
            public List<string> AppliesWhen = new List<string>();
        }

        sealed class Case
        {
            public string Id, Want, Target, Intent;
            public bool Rival;
            public List<Rule> Rules = new List<Rule>();
            public List<Route> Routes = new List<Route>();
            public List<List<string>> Alternatives = new List<List<string>>();
            public Dictionary<string, string> Canon = new Dictionary<string, string>(StringComparer.Ordinal);

            public string CanonOf(string k) => Canon.TryGetValue(k, out var c) ? c : k;
            public Route RouteOf(string k) => Routes.First(r => r.Key == k);
            public List<string> Intents => Routes.Select(r => r.Intent).Distinct().ToList();
        }

        static List<Case> _cases;
        static Dictionary<string, Case> _byId;

        [OneTimeSetUp]
        public void Load()
        {
            _content = Baselines.Primary();
            _spec = JObject.Parse(File.ReadAllText(Path.Combine(TestPaths.DataRoot, "Experiments", "route-applicability.json")));
            _routesJson = JObject.Parse(File.ReadAllText(Path.Combine(TestPaths.DataRoot, "Experiments", "causal-routes.json")));
            var s = (JObject)JObject.Parse(File.ReadAllText(Path.Combine(TestPaths.DataRoot, "Experiments", "held-out-people.json")))["sweep"];
            _traits = ((JArray)s["traits"]).Select(x => x.Value<string>()).ToList();
            _traitLevels = ((JArray)s["levels"]).Select(x => x.Value<double>()).ToList();
            _ring = ((JArray)s["value_ring"]).Select(x => x.Value<string>()).ToList();
            _beliefSets = ((JArray)s["belief_sets"]).Select(set => ((JArray)set).Select(b => new BeliefSeed(
                b["predicate"].Value<string>(), ((JArray)b["args"]).Select(a => a.Value<string>()).ToList(), b["confidence"].Value<double>())).ToList()).ToList();

            var run = Scenario001.Prepare(_content, _content.Morning.Variants[0].Id, 1);
            _house = run.World.House;
            _kitchen = _house.Rooms.First(r => r.HasTag(ActionCatalog.PantryTag)).Id;

            _sits = ((JArray)_spec["situations"]).Select(x => new Sit { Id = x["id"].Value<string>(), Present = ((JArray)x["present"]).Select(p => p.Value<string>()).ToList() }).ToList();
            _cases = ((JArray)_spec["cases"]).Select(c => ParseCase((JObject)c)).ToList();
            _byId = _cases.ToDictionary(c => c.Id, c => c, StringComparer.Ordinal);
            foreach (var c in IntentionSelector.Load(Path.Combine(TestPaths.DataRoot, "Experiments", "intentions.json")))
                foreach (var sc in c.ScaledBy) Register(sc);
            foreach (var v in ((JObject)_routesJson["synthetic"]["variants"]).Properties())
                foreach (JObject r in (JArray)v.Value)
                    foreach (JObject t in (JArray)r["scaled_by"] ?? new JArray()) Register(ScalerOf(t));
            Register(new Scaler { Kind = ScalerKind.Trait, Name = "impulsive" });
            foreach (var set in _beliefSets)
                foreach (var b in set) Register(new Scaler { Kind = ScalerKind.Belief, Predicate = b.Predicate, Args = b.Args.ToList() });

            var n = (int)Math.Pow(_traitLevels.Count, _traits.Count);
            _minds = new Mind[n];
            _percepts = new Percept[n][];
            _company = new Percept[n];
            _alone = new Percept[n];
            _lv = new double[n][];
            for (var i = 0; i < n; i++)
            {
                _minds[i] = SweepMind(i);
                _percepts[i] = _sits.Select(x => At(_minds[i].Id, x.Present)).ToArray();
                _company[i] = At(_minds[i].Id, new List<string> { "a", "b", "c" });
                _alone[i] = At(_minds[i].Id, new List<string>());
                _lv[i] = Levels(_minds[i], _company[i], "a");
            }
        }

        [OneTimeTearDown]
        public void Write()
        {
            var sb = new StringBuilder();
            sb.AppendLine("# Route applicability: measurements");
            sb.AppendLine();
            sb.AppendLine("Generated by `RouteApplicabilityExperimentTests` from the committed cases, the frozen candidate rules, the causal-route declarations and the sweep, every input hashed at the start and the end of the run. The predictions, the protocol, the cases and the annotation were committed before this fixture existed. There is no randomness anywhere. Every percentage names its denominator; none measures psychological validity.");
            sb.AppendLine();
            foreach (var r in _results.Values) sb.AppendLine(r);
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "experiments", "route-applicability");
            Directory.CreateDirectory(dir);
            File.WriteAllText(Path.Combine(dir, "measurements.md"), sb.ToString());
        }

        static void Record(string key, string text)
        {
            _results[key] = text;
            TestContext.WriteLine(text);
        }

        static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);
        static string F9(double v) => v.ToString("0.000000000", CultureInfo.InvariantCulture);
        static string N(int v) => v.ToString("N0", CultureInfo.InvariantCulture);
        static string Pc(double part, double whole) => whole == 0 ? "n/a" : (100.0 * part / whole).ToString("0.0", CultureInfo.InvariantCulture) + " %";
        static string NP(int part, int whole) => N(part) + " (" + Pc(part, whole) + ")";

        static string Sha(string path)
        {
            using (var sha = SHA256.Create())
                return string.Concat(sha.ComputeHash(File.ReadAllBytes(path)).Select(b => b.ToString("x2")));
        }

        static string FrozenPath(string rel)
            => rel.StartsWith("Data/", StringComparison.Ordinal)
                ? Path.Combine(TestPaths.DataRoot, rel.Substring(5).Replace('/', Path.DirectorySeparatorChar))
                : Path.Combine(TestPaths.ProjectRoot, "Assets", "_Project", rel.Replace('/', Path.DirectorySeparatorChar));

        // ============================================================ people and moments

        static Mind SweepMind(int i)
        {
            var traits = new Dictionary<string, double>(StringComparer.Ordinal);
            var n = i;
            foreach (var name in _traits)
            {
                traits[name] = _traitLevels[n % _traitLevels.Count];
                n /= _traitLevels.Count;
            }
            var shift = i % _ring.Count;
            var values = _ring.Skip(shift).Concat(_ring.Take(shift)).ToList();
            var id = "p" + i;
            var profile = new Profile(id, id, 30, "sibling", traits, values, 0.5, new Dictionary<string, double>(), new List<BeliefSeed>());
            var mind = new Mind(profile);
            foreach (var b in _beliefSets[i % _beliefSets.Count])
                mind.Beliefs.Seed(new BeliefSeed(b.Predicate, b.Args.Select(a => a == "$self" ? id : a).ToList(), b.Confidence));
            return mind;
        }

        static Percept At(string who, List<string> present)
        {
            var room = _house.Get(_kitchen);
            return new Percept(who, 10, room, present, _house.Adjacent(room.Id), 0.3, true, true, false, _house, false, null, null);
        }

        static Motive Want(string key, string target) => new Motive(key, target, 0.6, new List<string>(), new List<ScalerTerm>());

        static string EvidenceKey(Scaler s)
        {
            switch (s.Kind)
            {
                case ScalerKind.Trait: return "trait:" + s.Name;
                case ScalerKind.Value: return "value:" + s.Name;
                case ScalerKind.Belief: return "belief:" + s.Predicate + "(" + string.Join(",", s.Args ?? new List<string>()) + ")";
                case ScalerKind.Emotion: return "emotion:" + s.Name + "@" + (s.Target ?? "situation");
                default: return s.Kind + ":" + (s.Name ?? s.Predicate ?? s.Entry ?? "");
            }
        }

        static int Register(Scaler s)
        {
            var key = EvidenceKey(s);
            if (_keyIndex.TryGetValue(key, out var k)) return k;
            k = _keys.Count;
            _keys.Add(key);
            _keyIndex[key] = k;
            _keyScaler.Add(new Scaler { Kind = s.Kind, Name = s.Name, Predicate = s.Predicate, Args = s.Args, Entry = s.Entry, About = s.About, Topic = s.Topic, By = s.By, Until = s.Until, Target = s.Target, Factor = 1.0 });
            return k;
        }

        static double[] Levels(Mind mind, Percept p, string target)
        {
            var ctx = new DecisionContext(p, mind.Id, target, _content.Morning.Day, _content.Rules.Deciding.RecallHalfLife);
            var terms = ScalerEval.Evaluate(_keyScaler, mind, ctx);
            if (terms.Count != _keyScaler.Count) throw new InvalidOperationException("a fact was not evaluated");
            return terms.Select(t => t.Level).ToArray();
        }

        static Scaler ScalerOf(JObject t)
            => new Scaler
            {
                Kind = t["kind"]?.Value<string>(), Name = t["name"]?.Value<string>(), Predicate = t["predicate"]?.Value<string>(),
                Args = (t["args"] as JArray ?? new JArray()).Select(a => a.Value<string>()).ToList(),
                Target = t["target"]?.Value<string>(), Factor = t["factor"]?.Value<double>() ?? 0.0
            };

        static SituationCondition Gate(JObject w)
            => new SituationCondition { Alone = w?["alone"]?.Value<bool>(), OthersPresentMin = w?["others_present_min"]?.Value<int>() };

        /// <summary>The causal-route experiment's gate key, so that A's statements are D's.</summary>
        static string GateKey(SituationCondition w)
        {
            var parts = new List<string>();
            if (w.Alone.HasValue) parts.Add(w.Alone.Value ? "alone" : "not alone");
            if (w.OthersPresentMin.HasValue) parts.Add("others>=" + w.OthersPresentMin.Value);
            return parts.Count == 0 ? "any" : string.Join(",", parts);
        }

        static List<string> GateAsPredicates(SituationCondition w)
        {
            if (w.Alone.HasValue) return new List<string> { w.Alone.Value ? "absent:anyone" : "present:anyone" };
            if (w.OthersPresentMin.HasValue) return new List<string> { "present:anyone" };
            return new List<string>();
        }

        static Rule ParseRule(JObject r, string intent)
        {
            var when = r["when"] as JObject ?? new JObject();
            var rule = new Rule { Id = r["id"].Value<string>(), Intent = intent, Route = r["route"]?.Value<string>(), When = Gate(when), Base = r["base"]?.Value<double>() ?? 0.0 };
            rule.Gate = GateKey(rule.When);
            foreach (JObject t in (JArray)r["terms"] ?? new JArray())
            {
                var sc = ScalerOf(t);
                rule.Terms.Add(new Term { Key = EvidenceKey(sc), K = Register(sc), Factor = sc.Factor, Role = t["role"]?.Value<string>() ?? "support", Kind = sc.Kind });
            }
            return rule;
        }

        static Case ParseCase(JObject c)
        {
            var k = new Case
            {
                Id = c["id"].Value<string>(), Want = c["want"].Value<string>(), Target = c["target"]?.Type == JTokenType.Null ? null : c["target"]?.Value<string>(),
                Intent = c["intent"].Value<string>(), Rival = c["rival"]?.Value<bool>() ?? false
            };
            foreach (JObject r in (JArray)c["rules"]) k.Rules.Add(ParseRule(r, k.Intent));
            foreach (JObject r in (JArray)c["routes"])
                k.Routes.Add(new Route { Key = r["key"].Value<string>(), Intent = k.Intent, AppliesWhen = ((JArray)r["applies_when"]).Select(x => x.Value<string>()).ToList() });
            if (k.Rival)
            {
                var rv = (JObject)_spec["rival"];
                var rule = ParseRule((JObject)rv["rule"], rv["intent"].Value<string>());
                rule.Route = rv["route"].Value<string>();
                k.Rules.Add(rule);
                k.Routes.Add(new Route { Key = rule.Route, Intent = rule.Intent, AppliesWhen = ((JArray)rv["applies_when"]).Select(x => x.Value<string>()).ToList() });
            }
            return k;
        }

        static Case Clone(Case c)
        {
            var k = new Case { Id = c.Id, Want = c.Want, Target = c.Target, Intent = c.Intent, Rival = c.Rival };
            foreach (var r in c.Rules)
                k.Rules.Add(new Rule
                {
                    Id = r.Id, Intent = r.Intent, Route = r.Route, When = r.When, Gate = r.Gate, Base = r.Base, Motives = r.Motives.ToList(),
                    Terms = r.Terms.Select(t => new Term { Key = t.Key, K = t.K, Factor = t.Factor, Role = t.Role, Kind = t.Kind }).ToList()
                });
            foreach (var r in c.Routes) k.Routes.Add(new Route { Key = r.Key, Intent = r.Intent, AppliesWhen = r.AppliesWhen.ToList() });
            foreach (var g in c.Alternatives) k.Alternatives.Add(g.ToList());
            foreach (var kv in c.Canon) k.Canon[kv.Key] = kv.Value;
            return k;
        }

        // ============================================================ evaluation

        static bool PredicateHolds(string p, List<string> present, string target)
        {
            switch (p)
            {
                case "present:anyone": return present.Count > 0;
                case "absent:anyone": return present.Count == 0;
                case "present:$target": return target != null && present.Contains(target);
                case "absent:$target": return target == null || !present.Contains(target);
                default: throw new InvalidOperationException("unknown predicate " + p);
            }
        }

        static List<string> ReadPredicates(List<string> preds, Rep rep, string target)
        {
            var output = new List<string>();
            foreach (var p0 in preds)
            {
                var p = p0;
                if (rep == Rep.CEntity)
                {
                    if (p == "present:$target") p = "present:anyone";
                    else if (p == "absent:$target") continue;
                }
                if (rep == Rep.CKind && target != null)
                {
                    if (p == "present:anyone") p = "present:$target";
                    else if (p == "absent:anyone") p = "absent:$target";
                }
                output.Add(p);
            }
            return output;
        }

        static string RoleOf(Term t, Rep rep)
        {
            if (rep == Rep.CKind && t.Kind == ScalerKind.Belief) return "condition";
            if (!ReadsConditions(rep) && t.Role == "condition") return "support";
            return t.Role;
        }

        sealed class Stmt
        {
            public string Key;
            public double Coef;
            public double Amount;
            public string Rule;
        }

        sealed class Out
        {
            public Rep Rep;
            public Case Case;
            public Dictionary<string, bool> App = new Dictionary<string, bool>(StringComparer.Ordinal);
            public Dictionary<string, double> Strength = new Dictionary<string, double>(StringComparer.Ordinal);
            public Dictionary<string, List<Stmt>> Kept = new Dictionary<string, List<Stmt>>(StringComparer.Ordinal);
            public Dictionary<string, List<string>> Conditions = new Dictionary<string, List<string>>(StringComparer.Ordinal);
            public Dictionary<string, double> Support = new Dictionary<string, double>(StringComparer.Ordinal);
            public Dictionary<string, string> State = new Dictionary<string, string>(StringComparer.Ordinal);
            public List<string> Candidates = new List<string>();
            public string P0, P1;
            public int Flags, Recognised, Ambiguous;
            public string Trace = "";

            public double Focal => Case.Intent != null && Support.TryGetValue(Case.Intent, out var v) ? v : 0.0;

            /// <summary>The chosen intention's applicable routes, their evidence and their satisfied conditions.</summary>
            public string Explanation(string intent)
            {
                if (Rep == Rep.S || intent == null || intent == "none" || intent.StartsWith("tie(", StringComparison.Ordinal)) return intent ?? "none";
                var parts = new List<string>();
                foreach (var r in Case.Routes.Where(x => x.Intent == intent && App[x.Key]))
                    parts.Add(Case.CanonOf(r.Key) + "{" + string.Join(";", Kept[r.Key].OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => x.Key + "=" + F9(x.Amount)))
                              + (Conditions[r.Key].Count > 0 ? ";if " + string.Join("&", Conditions[r.Key].OrderBy(x => x, StringComparer.Ordinal)) : "") + "}");
                return intent + ": " + string.Join(" + ", parts.OrderBy(x => x, StringComparer.Ordinal));
            }
        }

        static string Choose(Out o, IEnumerable<string> pool)
        {
            var list = pool.ToList();
            if (list.Count == 0) return "none";
            var top = list.Max(i => o.Support[i]);
            var tied = list.Where(i => o.Support[i] >= top - Tie).OrderBy(x => x, StringComparer.Ordinal).ToList();
            return tied.Count == 1 ? tied[0] : "tie(" + string.Join("=", tied) + ")";
        }

        static Out Shipped(Case c, double[] lv, Percept p)
        {
            var o = new Out { Rep = Rep.S, Case = c };
            foreach (var r in c.Routes) { o.App[r.Key] = false; o.Strength[r.Key] = 0.0; o.Kept[r.Key] = new List<Stmt>(); o.Conditions[r.Key] = new List<string>(); }
            var by = new Dictionary<string, double>(StringComparer.Ordinal);
            foreach (var r in c.Rules)
            {
                if (!r.When.Matches(p)) continue;
                var sum = 0.0;
                foreach (var t in r.Terms) sum += lv[t.K] * t.Factor;
                var weight = r.Base + sum;
                if (weight <= 0.0) continue;
                by[r.Intent] = (by.TryGetValue(r.Intent, out var w) ? w : 0.0) + weight;
                o.App[r.Route] = true;
                o.Strength[r.Route] += weight;
            }
            foreach (var i in c.Intents)
            {
                o.Support[i] = by.TryGetValue(i, out var v) ? v : 0.0;
                o.State[i] = by.ContainsKey(i) ? "applicable" : "no candidate";
            }
            o.Candidates = by.Keys.ToList();
            var ranked = by.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key, StringComparer.Ordinal).ToList();
            o.P0 = o.P1 = ranked.Count == 0 ? "none" : ranked[0].Key;
            o.Trace = o.P0;
            return o;
        }

        static Out Evaluate(Case c, double[] lv, List<string> present, string target, Percept p, Rep rep)
        {
            if (rep == Rep.S) return Shipped(c, lv, p);
            var circ = Circ(rep);
            var o = new Out { Rep = rep, Case = c };
            var admitted = new Dictionary<string, bool>(StringComparer.Ordinal);
            var roles = new Dictionary<string, Dictionary<string, HashSet<string>>>(StringComparer.Ordinal);
            foreach (var r in c.Routes)
            {
                o.Kept[r.Key] = new List<Stmt>();
                o.Conditions[r.Key] = new List<string>();
                admitted[r.Key] = false;
                roles[r.Key] = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
            }
            void Add(string route, string key, double coef, double amount, string rule)
            {
                var list = o.Kept[route];
                var had = list.FirstOrDefault(x => x.Key == key);
                if (had != null)
                {
                    if (Math.Abs(had.Coef - coef) < SameCoef) { o.Recognised++; return; }
                    o.Recognised++;
                    if (Math.Abs(coef) < Math.Abs(had.Coef) || Math.Abs(coef) == Math.Abs(had.Coef) && coef <= had.Coef) return;
                    had.Coef = coef; had.Amount = amount; had.Rule = rule;
                    return;
                }
                list.Add(new Stmt { Key = key, Coef = coef, Amount = amount, Rule = rule });
            }
            foreach (var r in c.Rules)
            {
                var gate = r.When.Matches(p);
                if (!circ && !gate) continue;
                if (!circ) admitted[r.Route] = true;
                if (r.Base != 0.0) Add(r.Route, Prefix + r.Gate, r.Base, r.Base, r.Id);
                foreach (var t in r.Terms)
                {
                    var set = roles[r.Route].TryGetValue(t.Key, out var hs) ? hs : roles[r.Route][t.Key] = new HashSet<string>(StringComparer.Ordinal);
                    set.Add(t.Role);
                    var role = RoleOf(t, rep);
                    var level = lv[t.K];
                    if (role == "condition")
                    {
                        if (!o.Conditions[r.Route].Contains(t.Key)) o.Conditions[r.Route].Add(t.Key);
                        if (rep == Rep.BW) Add(r.Route, t.Key, t.Factor, level * t.Factor, r.Id);
                        continue;
                    }
                    Add(r.Route, t.Key, t.Factor, level * t.Factor, r.Id);
                }
            }
            if (ReadsRoles(rep)) o.Ambiguous = roles.Values.Sum(d => d.Values.Count(x => x.Count > 1));

            foreach (var r in c.Routes)
            {
                bool ok;
                if (circ) ok = ReadPredicates(r.AppliesWhen, rep, target).All(x => PredicateHolds(x, present, target));
                else ok = admitted[r.Key];
                if (ok && o.Conditions[r.Key].Count > 0) ok = o.Conditions[r.Key].All(k => lv[_keyIndex[k]] > 0.0);
                o.App[r.Key] = ok;
                var s = 0.0;
                foreach (var st in o.Kept[r.Key]) s += st.Amount;
                o.Strength[r.Key] = s;
            }

            foreach (var i in c.Intents)
            {
                var routes = c.Routes.Where(r => r.Intent == i).ToList();
                bool candidate;
                if (!circ) candidate = routes.Any(r => admitted[r.Key]);
                else if (rep == Rep.CSplit) candidate = routes.Any(r => ReadPredicates(r.AppliesWhen, rep, target).All(x => PredicateHolds(x, present, target)));
                else candidate = true;
                var grouped = new HashSet<string>(StringComparer.Ordinal);
                var support = 0.0;
                foreach (var r in routes)
                {
                    if (grouped.Contains(r.Key)) continue;
                    var g = c.Alternatives.FirstOrDefault(x => x.Contains(r.Key));
                    if (g != null)
                    {
                        foreach (var m in g) grouped.Add(m);
                        var live = g.Where(m => o.App.ContainsKey(m) && o.App[m]).ToList();
                        if (live.Count > 0) support += live.Max(m => o.Strength[m]);
                        continue;
                    }
                    if (o.App[r.Key]) support += o.Strength[r.Key];
                }
                o.Support[i] = support;
                if (candidate) o.Candidates.Add(i);
                o.State[i] = !candidate ? "no candidate" : routes.Any(r => o.App[r.Key]) ? "applicable" : "no applicable route";
            }

            for (var a = 0; a < c.Routes.Count; a++)
                for (var b = a + 1; b < c.Routes.Count; b++)
                {
                    var ra = c.Routes[a];
                    var rb = c.Routes[b];
                    if (ra.Intent != rb.Intent || !o.App[ra.Key] || !o.App[rb.Key]) continue;
                    if (Content(o.Kept[ra.Key]) == Content(o.Kept[rb.Key]) && string.Join("&", o.Conditions[ra.Key].OrderBy(x => x)) == string.Join("&", o.Conditions[rb.Key].OrderBy(x => x))) o.Flags++;
                }

            o.P0 = Choose(o, o.Candidates);
            o.P1 = Choose(o, o.Candidates.Where(i => o.State[i] == "applicable"));
            o.Trace = string.Join(" | ", o.Candidates.OrderBy(x => x, StringComparer.Ordinal).Select(i => i + ": " + string.Join(" + ",
                c.Routes.Where(r => r.Intent == i && o.App[r.Key] && o.Kept[r.Key].Count > 0)
                    .Select(r => c.CanonOf(r.Key) + "{" + string.Join(";", o.Kept[r.Key].OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => x.Key + "=" + F9(x.Amount))) + "}")
                    .OrderBy(x => x, StringComparer.Ordinal))));
            return o;
        }

        static string Content(List<Stmt> xs)
            => string.Join(";", xs.OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => x.Key + ":" + x.Coef.ToString("R", CultureInfo.InvariantCulture)));

        /// <summary>The declared meaning: does each focal route apply?</summary>
        static bool DeclaredApplies(Case c, Route r, double[] lv, List<string> present)
        {
            if (!r.AppliesWhen.All(x => PredicateHolds(x, present, c.Target))) return false;
            foreach (var rule in c.Rules.Where(x => x.Route == r.Key))
                foreach (var t in rule.Terms)
                    if (t.Role == "condition" && lv[t.K] <= 0.0) return false;
            return true;
        }

        static Out At(Case c, int i, int si, Rep rep, double[] lv = null, string target = null)
            => Evaluate(c, lv ?? _lv[i], _sits[si].Present, target ?? c.Target, _percepts[i][si], rep);

        static int Profiles => _minds.Length;
        static int CellsPerCase => Profiles * _sits.Count;

        static IEnumerable<Tuple<int, int>> Cells()
        {
            for (var i = 0; i < Profiles; i++)
                for (var si = 0; si < _sits.Count; si++)
                    yield return Tuple.Create(i, si);
        }

        static double[] With(double[] lv, string key, double level)
        {
            var x = (double[])lv.Clone();
            x[_keyIndex[key]] = level;
            return x;
        }

        static IEnumerable<Route> Focal(Case c) => c.Routes.Where(r => r.Intent == c.Intent);

        // ============================================================ family results

        sealed class Fam
        {
            public int Cells, FalseAct, FalseSupp, AppChanges, StrengthOnly, StrengthWrong, SelChangeP0, SelChangeP1, NoActive, Violations, Other;
            public bool Pass;
            public string Note = "";
        }

        static readonly Dictionary<string, Dictionary<Rep, Fam>> _fam = new Dictionary<string, Dictionary<Rep, Fam>>(StringComparer.Ordinal);

        static Fam FamOf(string f, Rep r)
        {
            if (!_fam.TryGetValue(f, out var d)) _fam[f] = d = new Dictionary<Rep, Fam>();
            if (!d.TryGetValue(r, out var x)) d[r] = x = new Fam();
            return x;
        }

        static void CountApplicability(Fam fam, Case c, Out o, double[] lv, List<string> present)
        {
            foreach (var r in Focal(c))
            {
                fam.Cells++;
                var want = DeclaredApplies(c, r, lv, present);
                if (o.App[r.Key] && !want) fam.FalseAct++;
                if (!o.App[r.Key] && want) fam.FalseSupp++;
            }
            if (o.State.TryGetValue(c.Intent, out var st) && st == "no applicable route") fam.NoActive++;
        }

        // ============================================================ 0

        static int _formMismatch, _formWeight, _formCells;

        [Test, Order(0), Timeout(7200000)]
        public void TheFilesAndTheControl()
        {
            var sb = new StringBuilder();
            sb.AppendLine("## 0. What is frozen, and whether S is the shipped selector");
            sb.AppendLine();
            sb.AppendLine("| File | sha256 at the start of this run | Match |");
            sb.AppendLine("|---|---|---|");
            foreach (var kv in Frozen)
            {
                var sha = Sha(FrozenPath(kv.Key));
                sb.AppendLine("| `" + kv.Key + "` | `" + sha + "` | " + (sha == kv.Value ? "**yes**" : "**NO**") + " |");
                Assert.AreEqual(kv.Value, sha, kv.Key);
            }
            sb.AppendLine();
            foreach (var c in _cases)
            {
                var candidates = c.Rules.Select(r => new Candidate
                {
                    Id = r.Id, Motives = new List<string> { c.Want }, Intent = r.Intent, When = r.When, Base = r.Base,
                    ScaledBy = r.Terms.Select(t => new Scaler { Kind = _keyScaler[t.K].Kind, Name = _keyScaler[t.K].Name, Predicate = _keyScaler[t.K].Predicate, Args = _keyScaler[t.K].Args, Target = _keyScaler[t.K].Target, Factor = t.Factor }).ToList()
                }).ToList();
                foreach (var x in Cells())
                {
                    _formCells++;
                    var form = IntentionSelector.Form(candidates, _minds[x.Item1], _percepts[x.Item1][x.Item2], Want(c.Want, c.Target), _content.Morning.Day, _content.Rules.Deciding.RecallHalfLife);
                    var s = At(c, x.Item1, x.Item2, Rep.S);
                    if ((form.Intent ?? "none") != s.P0) _formMismatch++;
                    else if (form.Intent != null && form.Weight != s.Support[form.Intent]) _formWeight++;
                }
            }
            sb.AppendLine("S, rebuilt from the authored rules, differs from `IntentionSelector.Form` in **" + N(_formMismatch) + "** of " + N(_formCells) + " cells (" + _cases.Count + " cases x " + N(CellsPerCase) + "); winning weights not equal to the bit: **" + N(_formWeight) + "**.");
            sb.AppendLine();
            sb.AppendLine("Evaluation space: " + N(Profiles) + " profiles x " + _sits.Count + " situations (" + string.Join("; ", _sits.Select(x => x.Id + " " + (x.Present.Count == 0 ? "nobody" : string.Join(" and ", x.Present)))) + ") = " + N(CellsPerCase) + " cells per case and condition.");
            Record("0", sb.ToString());
            Assert.AreEqual(0, _formMismatch);
            Assert.AreEqual(0, _formWeight);
        }

        // ============================================================ 1: families A to G, J

        [Test, Order(1), Timeout(7200000)]
        public void A_TheRouteLayer()
        {
            var reps = Main;

            // A: condition absent or present.
            foreach (var pair in new[] { Tuple.Create("owning_c", "belief:answerable_for($self,missing_can)", 0.9), Tuple.Create("settling_c", "belief:role_claim($self,leads_family)", 0.8) })
            {
                var c = _byId[pair.Item1];
                foreach (var rep in reps)
                {
                    var f = FamOf("A", rep);
                    foreach (var x in Cells())
                    {
                        var absent = With(_lv[x.Item1], pair.Item2, 0.0);
                        var present = With(_lv[x.Item1], pair.Item2, pair.Item3);
                        var oa = At(c, x.Item1, x.Item2, rep, absent);
                        var op = At(c, x.Item1, x.Item2, rep, present);
                        CountApplicability(f, c, oa, absent, _sits[x.Item2].Present);
                        CountApplicability(f, c, op, present, _sits[x.Item2].Present);
                        var rk = c.Routes[0].Key;
                        if (oa.App[rk] != op.App[rk]) f.AppChanges++;
                        if (oa.P0 != op.P0) f.SelChangeP0++;
                        if (oa.P1 != op.P1) f.SelChangeP1++;
                    }
                }
            }

            // B: condition against evidence, the same authored rule.
            foreach (var pair in new[] { Tuple.Create("owning_c", "owning_e", "belief:answerable_for($self,missing_can)", 0.9), Tuple.Create("settling_c", "settling_e", "belief:role_claim($self,leads_family)", 0.8) })
            {
                var a = _byId[pair.Item1];
                var b = _byId[pair.Item2];
                foreach (var rep in reps)
                {
                    var f = FamOf("B", rep);
                    foreach (var x in Cells())
                        foreach (var level in new[] { 0.0, pair.Item4 })
                        {
                            var lv = With(_lv[x.Item1], pair.Item3, level);
                            var oa = At(a, x.Item1, x.Item2, rep, lv);
                            var ob = At(b, x.Item1, x.Item2, rep, lv);
                            f.Cells++;
                            var ra = oa.App[a.Routes[0].Key];
                            var rb = ob.App[b.Routes[0].Key];
                            if (ra != level > 0.0 || !rb) f.Violations++;
                            if (level <= 0.0 && ra == rb) f.Other++;          // not told apart when the fact is absent
                            if (level <= 0.0 && oa.P0 != ob.P0) f.SelChangeP0++;
                            if (level <= 0.0 && oa.P1 != ob.P1) f.SelChangeP1++;
                        }
                }
            }

            // C, D, J: circumstances.
            foreach (var fam in new[] { Tuple.Create("C", new[] { "side_mara", "away_mara", "duty_mara" }), Tuple.Create("D", new[] { "side_mara", "side_daniel", "side_elena" }), Tuple.Create("J", new[] { "side_mara", "scene_mara" }) })
                foreach (var rep in reps)
                {
                    var f = FamOf(fam.Item1, rep);
                    foreach (var id in fam.Item2)
                    {
                        var c = _byId[id];
                        foreach (var x in Cells())
                        {
                            var o = At(c, x.Item1, x.Item2, rep);
                            CountApplicability(f, c, o, _lv[x.Item1], _sits[x.Item2].Present);
                            var reference = At(c, x.Item1, x.Item2, Rep.C);
                            if (o.P0 != reference.P0) f.SelChangeP0++;
                            if (o.P1 != reference.P1) f.SelChangeP1++;
                        }
                    }
                    if (fam.Item1 == "J")
                        foreach (var x in Cells())
                        {
                            var present = _sits[x.Item2].Present;
                            if (present.Count == 0 || present.Contains("mara")) continue;
                            var side = At(_byId["side_mara"], x.Item1, x.Item2, rep).App["at_their_side"];
                            var scene = At(_byId["scene_mara"], x.Item1, x.Item2, rep).App["not_in_front_of_others"];
                            if (side == scene) f.Other++;                   // the two meanings collapse
                        }
                }

            // E: support varied; F: inhibitor varied.
            foreach (var spec in new[] { Tuple.Create("E", "side_mara", "trait:empathetic", 0.40), Tuple.Create("E", "owning_c", "trait:honest", 0.30), Tuple.Create("F", "stepping_in", "trait:anxious", -0.60) })
            {
                var c = _byId[spec.Item2];
                var rk = c.Routes[0].Key;
                foreach (var rep in reps)
                {
                    var f = FamOf(spec.Item1, rep);
                    foreach (var x in Cells())
                    {
                        var outs = _traitLevels.Select(l => At(c, x.Item1, x.Item2, rep, With(_lv[x.Item1], spec.Item3, l))).ToList();
                        f.Cells++;
                        var appSet = outs.Select(o => o.App[rk]).Distinct().Count();
                        if (appSet > 1) { f.Violations++; f.AppChanges++; }
                        if (spec.Item1 == "F" && outs.Any(o => o.Kept.Count != outs[0].Kept.Count)) f.Violations++;
                        if (rep != Rep.S && appSet == 1 && outs.Select(o => o.Strength[rk]).Distinct().Count() > 1) f.StrengthOnly++;
                        if (rep != Rep.S && outs[0].App[rk])
                            for (var k = 0; k + 1 < outs.Count; k++)
                                if (Math.Abs((outs[k + 1].Strength[rk] - outs[k].Strength[rk]) - spec.Item4 * (_traitLevels[k + 1] - _traitLevels[k])) > Tie) { f.StrengthWrong++; break; }
                        if (spec.Item1 == "F" && rep != Rep.S) f.Other += outs.Count(o => o.App[rk] && o.Strength[rk] <= 0.0);
                        if (outs.Select(o => o.P0).Distinct().Count() > 1) f.SelChangeP0++;
                        if (outs.Select(o => o.P1).Distinct().Count() > 1) f.SelChangeP1++;
                    }
                }
            }

            // G: no active route.
            foreach (var id in new[] { "only_side_mara", "only_owning", "only_fair", "weak_pull" })
            {
                var c = _byId[id];
                foreach (var rep in reps)
                {
                    var f = FamOf("G", rep);
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        f.Cells++;
                        var want = DeclaredApplies(c, c.Routes[0], _lv[x.Item1], _sits[x.Item2].Present);
                        var st = o.State[c.Intent];
                        if ((st == "applicable") != want) f.Violations++;
                        if (st == "no applicable route") f.NoActive++;
                        if (st == "no candidate") f.Other++;
                        GTally(id, rep, "P0 " + o.P0);
                        GTally(id, rep, "P1 " + o.P1);
                        GTally(id, rep, "state " + st);
                    }
                }
            }

            foreach (var kv in _fam)
                foreach (var r in kv.Value)
                {
                    var f = r.Value;
                    switch (kv.Key)
                    {
                        case "A": case "C": case "D": f.Pass = f.FalseAct == 0 && f.FalseSupp == 0; break;
                        case "B": f.Pass = f.Violations == 0; break;
                        case "J": f.Pass = f.FalseAct == 0 && f.FalseSupp == 0 && f.Other == 0; break;
                        case "E": f.Pass = f.Violations == 0 && f.StrengthWrong == 0; break;
                        case "F": f.Pass = f.Violations == 0 && f.StrengthWrong == 0; break;
                        case "G": f.Pass = f.Violations == 0; break;
                    }
                }

            var sb = new StringBuilder();
            sb.AppendLine("## 1. The route layer: families A to G and J");
            sb.AppendLine();
            sb.AppendLine("FA: false activations (the representation says the route applies; the declared meaning says it does not). FS: false suppressions. Shares are of the family's route-cells.");
            sb.AppendLine();
            sb.AppendLine("| Family | Route-cells | " + string.Join(" | ", reps.Select(Name)) + " |");
            sb.AppendLine("|---|---|" + string.Join("|", reps.Select(_ => "---")) + "|");
            foreach (var f in new[] { "A", "C", "D", "J" })
            {
                var t = new Dictionary<string, string> { ["A"] = "A condition absent or present", ["C"] = "C circumstance switch", ["D"] = "D person-specific circumstance", ["J"] = "J target against generic" }[f];
                sb.AppendLine("| " + t + " | " + N(FamOf(f, Rep.C).Cells) + " | " + string.Join(" | ", reps.Select(r =>
                {
                    var x = FamOf(f, r);
                    var err = x.FalseAct + x.FalseSupp;
                    return (x.Pass ? "pass" : "**fail**") + (err == 0 ? "" : ": " + (x.FalseAct > 0 ? N(x.FalseAct) + " FA " : "") + (x.FalseSupp > 0 ? N(x.FalseSupp) + " FS " : "") + "(" + Pc(err, x.Cells) + ")")
                           + (f == "J" && x.Other > 0 ? "; meanings collapse in " + N(x.Other) : "");
                })) + " |");
            }
            sb.AppendLine("| B condition against evidence (cells not read as declared) | " + N(FamOf("B", Rep.C).Cells) + " | " + string.Join(" | ", reps.Select(r =>
            {
                var x = FamOf("B", r);
                return (x.Pass ? "pass" : "**fail**") + (x.Violations == 0 ? "" : ": " + NP(x.Violations, x.Cells)) + "; told apart when absent in " + N(x.Cells / 2 - x.Other) + " of " + N(x.Cells / 2);
            })) + " |");
            foreach (var f in new[] { "E", "F" })
                sb.AppendLine("| " + (f == "E" ? "E support varied" : "F inhibitor varied") + " (profile-situations) | " + N(FamOf(f, Rep.C).Cells) + " | " + string.Join(" | ", reps.Select(r =>
                {
                    var x = FamOf(f, r);
                    return (x.Pass ? "pass" : "**fail**") + ": applicability changed " + N(x.AppChanges) + (r == Rep.S ? "" : ", strength wrong " + N(x.StrengthWrong) + ", strength-only changes " + N(x.StrengthOnly));
                })) + " |");
            sb.AppendLine("| G no active route (cells whose route-layer state is wrong) | " + N(FamOf("G", Rep.C).Cells) + " | " + string.Join(" | ", reps.Select(r =>
            {
                var x = FamOf("G", r);
                return (x.Pass ? "pass" : "**fail**") + (x.Violations == 0 ? "" : ": " + NP(x.Violations, x.Cells)) + "; no applicable route " + N(x.NoActive) + ", no candidate " + N(x.Other);
            })) + " |");
            sb.AppendLine();
            sb.AppendLine("**Per case, circumstance families** (FA / FS of " + N(CellsPerCase) + "):");
            sb.AppendLine();
            sb.AppendLine("| Case | Declared | " + string.Join(" | ", reps.Select(Name)) + " |");
            sb.AppendLine("|---|---|" + string.Join("|", reps.Select(_ => "---")) + "|");
            foreach (var id in new[] { "side_mara", "side_daniel", "side_elena", "away_mara", "duty_mara", "scene_mara" })
            {
                var c = _byId[id];
                sb.AppendLine("| `" + id + "` | " + (c.Routes[0].AppliesWhen.Count == 0 ? "no circumstance" : string.Join(", ", c.Routes[0].AppliesWhen)) + (c.Target != null ? " (target " + c.Target + ")" : "") + " | " + string.Join(" | ", reps.Select(r =>
                {
                    var fa = 0;
                    var fs = 0;
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, r);
                        var want = DeclaredApplies(c, c.Routes[0], _lv[x.Item1], _sits[x.Item2].Present);
                        if (o.App[c.Routes[0].Key] && !want) fa++;
                        if (!o.App[c.Routes[0].Key] && want) fs++;
                    }
                    return fa + fs == 0 ? "0" : (fa > 0 ? N(fa) + " FA" : "") + (fs > 0 ? " " + N(fs) + " FS" : "");
                })) + " |");
            }
            sb.AppendLine();
            sb.AppendLine("**Applicability changes along the varied fact or situation, and choices.** A: profile-situations where the route switches between condition absent and present (declared: all " + N(FamOf("A", Rep.C).Cells / 2) + "). Choices: profile-situations whose outcome changes between the conditions (A, E, F) or differs from C's (C, D, J), under P0 / P1.");
            sb.AppendLine();
            sb.AppendLine("| Family | " + string.Join(" | ", reps.Select(Name)) + " |");
            sb.AppendLine("|---|" + string.Join("|", reps.Select(_ => "---")) + "|");
            sb.AppendLine("| A switches | " + string.Join(" | ", reps.Select(r => N(FamOf("A", r).AppChanges))) + " |");
            foreach (var f in new[] { "A", "B", "C", "D", "E", "F", "J" })
                sb.AppendLine("| " + f + " choices, P0 / P1 | " + string.Join(" | ", reps.Select(r => N(FamOf(f, r).SelChangeP0) + " / " + N(FamOf(f, r).SelChangeP1))) + " |");
            sb.AppendLine("| F applicable with strength <= 0 (of " + N(FamOf("F", Rep.C).Cells * 3) + " evaluations) | " + string.Join(" | ", reps.Select(r => r == Rep.S ? "-" : N(FamOf("F", r).Other))) + " |");
            sb.AppendLine();

            sb.AppendLine("### Family G, and the selection layer (reported, not judged)");
            sb.AppendLine();
            sb.AppendLine("Route-layer state of the focal intention, and outcomes under P0 (current) and P1 (active only), of " + N(CellsPerCase) + " cells per case.");
            sb.AppendLine();
            sb.AppendLine("| Case | Rep | Route-layer state | P0 | P1 |");
            sb.AppendLine("|---|---|---|---|---|");
            foreach (var id in new[] { "only_side_mara", "only_owning", "only_fair", "weak_pull" })
                foreach (var rep in reps)
                {
                    var t = _gTally[id][rep];
                    string Of(string prefix) => string.Join(", ", t.Where(kv => kv.Key.StartsWith(prefix, StringComparison.Ordinal)).OrderByDescending(kv => kv.Value).Select(kv => kv.Key.Substring(prefix.Length) + " " + N(kv.Value)));
                    sb.AppendLine("| `" + id + "` | " + Name(rep) + " | " + Of("state ") + " | " + Of("P0 ") + " | " + Of("P1 ") + " |");
                }
            Record("1", sb.ToString());

            foreach (var f in new[] { "A", "B", "C", "D", "E", "F", "G", "J" })
                Assert.IsTrue(FamOf(f, Rep.C).Pass, "C computes the declared meaning: family " + f);
        }

        static readonly Dictionary<string, Dictionary<Rep, Dictionary<string, int>>> _gTally = new Dictionary<string, Dictionary<Rep, Dictionary<string, int>>>(StringComparer.Ordinal);

        static void GTally(string id, Rep rep, string key)
        {
            if (!_gTally.TryGetValue(id, out var d)) _gTally[id] = d = new Dictionary<Rep, Dictionary<string, int>>();
            if (!d.TryGetValue(rep, out var t)) d[rep] = t = new Dictionary<string, int>(StringComparer.Ordinal);
            t[key] = (t.TryGetValue(key, out var v) ? v : 0) + 1;
        }

        // ============================================================ 2: H and I

        static Case Renamed(Case c)
        {
            var k = Clone(c);
            var map = k.Routes.Select((r, i) => new { r.Key, New = "k" + (i + 1).ToString("00") }).ToDictionary(x => x.Key, x => x.New, StringComparer.Ordinal);
            foreach (var r in k.Rules) r.Route = map[r.Route];
            foreach (var g in k.Alternatives) for (var i = 0; i < g.Count; i++) g[i] = map[g[i]];
            k.Canon.Clear();
            foreach (var r in k.Routes) { k.Canon[map[r.Key]] = c.CanonOf(r.Key); r.Key = map[r.Key]; }
            return k;
        }

        static Case CopiedWithin(Case c)
        {
            var k = Clone(c);
            foreach (var r in c.Rules.Where(x => x.Intent == c.Intent).ToList())
            {
                var copy = Clone(new Case { Rules = new List<Rule> { r } }).Rules[0];
                copy.Id = r.Id + "_again";
                k.Rules.Add(copy);
            }
            return k;
        }

        static Case CopiedAsNewRoute(Case c)
        {
            var k = Clone(c);
            foreach (var r in c.Rules.Where(x => x.Intent == c.Intent).ToList())
            {
                var copy = Clone(new Case { Rules = new List<Rule> { r } }).Rules[0];
                copy.Id = r.Id + "_copy";
                copy.Route = r.Route + "#copy";
                k.Rules.Add(copy);
                if (!k.Routes.Any(x => x.Key == copy.Route))
                    k.Routes.Add(new Route { Key = copy.Route, Intent = c.Intent, AppliesWhen = c.RouteOf(r.Route).AppliesWhen.ToList() });
            }
            return k;
        }

        static Case Reversed(Case c)
        {
            var k = Clone(c);
            k.Rules.Reverse();
            return k;
        }

        static Case Regrouped(Case c)
        {
            var k = Clone(c);
            k.Rules.Clear();
            foreach (var r in c.Rules)
            {
                if (r.Intent != c.Intent || r.Terms.Count <= 1) { k.Rules.Add(Clone(new Case { Rules = new List<Rule> { r } }).Rules[0]); continue; }
                for (var t = 0; t < r.Terms.Count; t++)
                {
                    var part = new Rule { Id = r.Id + "_" + t, Intent = r.Intent, Route = r.Route, When = r.When, Gate = r.Gate, Base = t == 0 ? r.Base : 0.0 };
                    var term = r.Terms[t];
                    part.Terms.Add(new Term { Key = term.Key, K = term.K, Factor = term.Factor, Role = term.Role, Kind = term.Kind });
                    k.Rules.Add(part);
                }
            }
            return k;
        }

        static string Signature(Out o)
            => o.P0 + "|" + o.P1 + "|" + string.Join(",", o.Case.Routes.Where(r => r.Intent == o.Case.Intent).OrderBy(r => o.Case.CanonOf(r.Key), StringComparer.Ordinal)
                   .Select(r => o.Case.CanonOf(r.Key) + "=" + (o.App[r.Key] ? "1" : "0") + ":" + F9(o.Strength[r.Key]))) + "|" + o.Trace;

        static readonly Dictionary<string, Dictionary<Rep, int>> _controls = new Dictionary<string, Dictionary<Rep, int>>(StringComparer.Ordinal);
        static readonly Dictionary<string, int> _controlCells = new Dictionary<string, int>(StringComparer.Ordinal);

        static void Control(string id, Rep rep, bool changed)
        {
            if (!_controls.TryGetValue(id, out var d)) _controls[id] = d = Main.ToDictionary(r => r, r => 0);
            if (changed) d[rep]++;
        }

        [Test, Order(2), Timeout(7200000)]
        public void B_IrrelevantFactsAndTheCausalRouteControls()
        {
            var impulsive = _keyIndex["trait:impulsive"];
            var beliefKeys = _beliefSets.SelectMany(x => x).Select(b => new { Key = "belief:" + b.Predicate + "(" + string.Join(",", b.Args) + ")", b.Confidence }).GroupBy(x => x.Key).Select(g => g.First()).ToList();
            var pairs = new[] { Tuple.Create(1, 5), Tuple.Create(2, 4), Tuple.Create(3, 4), Tuple.Create(2, 3) };

            // H: irrelevant facts.
            foreach (var c in _cases)
            {
                var unread = beliefKeys.Where(b => !c.Rules.SelectMany(r => r.Terms).Any(t => t.Key == b.Key)).ToList();
                var readsCircumstance = c.Routes.Any(r => r.AppliesWhen.Any(p => p.Contains("$target")));
                foreach (var x in Cells())
                {
                    var i = x.Item1;
                    var si = x.Item2;
                    var moved = (double[])_lv[i].Clone();
                    moved[impulsive] = _traitLevels[(_traitLevels.IndexOf(moved[impulsive]) + 1) % _traitLevels.Count];
                    var believed = (double[])_lv[i].Clone();
                    foreach (var b in unread) believed[_keyIndex[b.Key]] = b.Confidence;
                    foreach (var rep in Main)
                    {
                        var baseSig = Signature(At(c, i, si, rep));
                        Control("H.1 an unread trait moved", rep, Signature(At(c, i, si, rep, moved)) != baseSig);
                        if (unread.Count > 0) Control("H.4 an unread belief added", rep, Signature(At(c, i, si, rep, believed)) != baseSig);
                        if (!readsCircumstance && c.Target != null)
                            Control("H.5 the target changed, for a route that reads no circumstance", rep, Signature(At(c, i, si, rep, null, c.Target == "daniel" ? "mara" : "daniel")) != baseSig);
                    }
                    if (unread.Count > 0) Tick("H.4 an unread belief added");
                    Tick("H.1 an unread trait moved");
                    if (!readsCircumstance && c.Target != null) Tick("H.5 the target changed, for a route that reads no circumstance");
                }
                foreach (var pr in pairs)
                {
                    var a = _sits[pr.Item1].Present;
                    var b = _sits[pr.Item2].Present;
                    var diff = a.Except(b).Concat(b.Except(a)).ToList();
                    if (c.Target != null && diff.Contains(c.Target)) continue;
                    for (var i = 0; i < Profiles; i++)
                    {
                        Tick("H.2 an unrelated person added or swapped");
                        foreach (var rep in Main)
                            Control("H.2 an unrelated person added or swapped", rep, Signature(At(c, i, pr.Item1, rep)) != Signature(At(c, i, pr.Item2, rep)));
                    }
                }
            }

            // I: rewrites of three cases.
            foreach (var id in new[] { "side_mara", "owning_c", "stepping_in" })
            {
                var c = _byId[id];
                var rewrites = new Dictionary<string, Case>
                {
                    ["I.2a the rule copied within its route"] = CopiedWithin(c),
                    ["I.2b rules reversed"] = Reversed(c),
                    ["I.2c every route key renamed"] = Renamed(c),
                    ["I.2d the rule split into one rule per term"] = Regrouped(c)
                };
                var asNew = CopiedAsNewRoute(c);
                foreach (var x in Cells())
                    foreach (var rep in Main)
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        var sig = Signature(o);
                        foreach (var kv in rewrites)
                        {
                            Control(kv.Key, rep, Signature(At(kv.Value, x.Item1, x.Item2, rep)) != sig);
                        }
                        var n = At(asNew, x.Item1, x.Item2, rep);
                        var applies = o.App[c.Routes[0].Key];
                        if (applies && Math.Abs(o.Strength[c.Routes[0].Key]) > Tie)
                        {
                            Control("I.3 a copy declared a new route: support unchanged (should change)", rep, Math.Abs(n.Focal - o.Focal) <= Tie);
                            Control("I.3 a copy declared a new route: not flagged (should be)", rep, n.Flags <= o.Flags);
                        }
                    }
                foreach (var x in Cells())
                {
                    foreach (var kv in rewrites) Tick(kv.Key);
                    if (At(c, x.Item1, x.Item2, Rep.C).App[c.Routes[0].Key] && Math.Abs(At(c, x.Item1, x.Item2, Rep.C).Strength[c.Routes[0].Key]) > Tie)
                    {
                        Tick("I.3 a copy declared a new route: support unchanged (should change)");
                        Tick("I.3 a copy declared a new route: not flagged (should be)");
                    }
                }
            }
            var amb = _byId["owning_ambiguous"];
            foreach (var x in Cells())
            {
                Tick("I.4 the ambiguous declaration not flagged (should be)");
                foreach (var rep in Main)
                    Control("I.4 the ambiguous declaration not flagged (should be)", rep, At(amb, x.Item1, x.Item2, rep).Ambiguous == 0);
            }

            // I.1: the causal-route experiment's 18 declared pairs.
            var d18 = Families18();

            var sb = new StringBuilder();
            sb.AppendLine("## 2. Irrelevant facts (H) and the causal-route controls (I)");
            sb.AppendLine();
            sb.AppendLine("A change is any difference in the outcome under P0 or P1, in a focal route's applicability or strength, or in the explanation, after undoing a declared renaming. For I.3 and I.4 the count is of cells where the representation fails to do what it must.");
            sb.AppendLine();
            sb.AppendLine("| Control | Cells compared | " + string.Join(" | ", Main.Select(Name)) + " |");
            sb.AppendLine("|---|---|" + string.Join("|", Main.Select(_ => "---")) + "|");
            foreach (var kv in _controls.OrderBy(k => k.Key, StringComparer.Ordinal))
                sb.AppendLine("| " + kv.Key + " | " + N(_controlCells[kv.Key]) + " | " + string.Join(" | ", Main.Select(r => kv.Value[r] == 0 ? "0" : "**" + N(kv.Value[r]) + "**")) + " |");
            sb.AppendLine();
            sb.AppendLine("### I.1 The causal-route experiment's 18 declared pairs, re-read");
            sb.AppendLine();
            sb.AppendLine("Each cell: cells of 2,187 where the pair differ in protect's support / the explanation / the outcome (and flagged, for the malformed pair). **Published D** is the causal-route experiment's measured column.");
            sb.AppendLine();
            var repsI = new[] { Rep.A, Rep.B, Rep.C, Rep.CEntity, Rep.CConditions, Rep.CSplit, Rep.CKind };
            sb.AppendLine("| Pair | Published D | " + string.Join(" | ", repsI.Select(Name)) + " |");
            sb.AppendLine("|---|---|" + string.Join("|", repsI.Select(_ => "---")) + "|");
            var dCounts = (JObject)_spec["causal_route_d_counts"];
            var reproduced = repsI.ToDictionary(r => r, r => 0);
            foreach (var pair in d18.Keys)
            {
                var want = ((JArray)dCounts[pair]).Select(v => v.Value<int>()).ToList();
                var row = "| " + pair.Replace("|", " ") + " | " + string.Join(" / ", want) + " |";
                foreach (var r in repsI)
                {
                    var got = d18[pair][r];
                    var ok = got[0] == want[0] && got[1] == want[1] && got[2] == want[2] && (want.Count < 4 || got[3] == want[3]);
                    if (ok) reproduced[r]++;
                    row += " " + (ok ? "same" : "**" + string.Join(" / ", got.Take(want.Count)) + "**") + " |";
                }
                sb.AppendLine(row);
            }
            sb.AppendLine("| **Reproduced** | | " + string.Join(" | ", repsI.Select(r => "**" + reproduced[r] + " of " + d18.Count + "**")) + " |");
            _reproduced18 = reproduced;
            Record("2", sb.ToString());

            Assert.AreEqual(d18.Count, reproduced[Rep.A], "A is the causal-route experiment's D");
            foreach (var kv in _controls.Where(k => k.Key.StartsWith("H.", StringComparison.Ordinal)))
                Assert.AreEqual(0, kv.Value[Rep.C], kv.Key + " under C");
        }

        static Dictionary<Rep, int> _reproduced18;

        static void Tick(string id) => _controlCells[id] = (_controlCells.TryGetValue(id, out var v) ? v : 0) + 1;

        /// <summary>The causal-route synthetic variants, each read as a Case: its rules, the two frozen rivals, declared alternatives and renamings.</summary>
        static Dictionary<string, Dictionary<Rep, int[]>> Families18()
        {
            var syn = (JObject)_routesJson["synthetic"];
            var decl = ((JArray)_routesJson["frozen"]["routes"]).ToDictionary(r => r["rule"].Value<string>(), r => (JObject)r, StringComparer.Ordinal);
            var frozenRaw = ((JArray)JObject.Parse(File.ReadAllText(Path.Combine(TestPaths.DataRoot, "Experiments", "intentions.json")))["candidates"]).Cast<JObject>().ToDictionary(c => c["id"].Value<string>(), c => c, StringComparer.Ordinal);
            var rivals = ((JArray)syn["rivals"]).Select(x => FrozenRule(frozenRaw[x.Value<string>()], decl)).ToList();
            var variants = new Dictionary<string, Case>(StringComparer.Ordinal);
            foreach (var v in ((JObject)syn["variants"]).Properties())
            {
                var c = new Case { Id = v.Name, Want = syn["want"].Value<string>(), Target = "a", Intent = "protect" };
                foreach (JObject r in (JArray)v.Value)
                {
                    var rule = new Rule { Id = r["id"].Value<string>(), Intent = r["intent"].Value<string>(), Route = r["route"].Value<string>(), When = new SituationCondition(), Base = r["base"]?.Value<double>() ?? 0.0 };
                    rule.Gate = GateKey(rule.When);
                    foreach (JObject t in (JArray)r["scaled_by"] ?? new JArray())
                    {
                        var sc = ScalerOf(t);
                        rule.Terms.Add(new Term { Key = EvidenceKey(sc), K = Register(sc), Factor = sc.Factor, Role = sc.Factor < 0 ? "inhibitor" : "support", Kind = sc.Kind });
                    }
                    c.Rules.Add(rule);
                    if (!c.Routes.Any(x => x.Key == rule.Route)) c.Routes.Add(new Route { Key = rule.Route, Intent = rule.Intent, AppliesWhen = new List<string>() });
                }
                foreach (var r in rivals)
                {
                    c.Rules.Add(r);
                    if (!c.Routes.Any(x => x.Key == r.Route)) c.Routes.Add(new Route { Key = r.Route, Intent = r.Intent, AppliesWhen = GateAsPredicates(r.When) });
                }
                if (syn["variant_relations"]?[v.Name] is JArray rel)
                    foreach (var g in rel.Where(x => x["type"].Value<string>() == "alternative"))
                        c.Alternatives.Add(((JArray)g["routes"]).Select(x => x.Value<string>()).ToList());
                if (syn["renamings"]?[v.Name] is JObject map)
                    foreach (var p in map.Properties()) c.Canon[p.Name] = p.Value.Value<string>();
                variants[v.Name] = c;
            }
            var company = new List<string> { "a", "b", "c" };
            var outs = new Dictionary<string, Out[][]>(StringComparer.Ordinal);
            var reps = new[] { Rep.A, Rep.B, Rep.C, Rep.CEntity, Rep.CConditions, Rep.CSplit, Rep.CKind };
            foreach (var kv in variants)
            {
                var arr = new Out[Profiles][];
                for (var i = 0; i < Profiles; i++)
                    arr[i] = reps.Select(r => Evaluate(kv.Value, _lv[i], company, "a", _company[i], r)).ToArray();
                outs[kv.Key] = arr;
            }
            var result = new Dictionary<string, Dictionary<Rep, int[]>>(StringComparer.Ordinal);
            foreach (var pair in (JArray)syn["pairs"])
            {
                var a = pair["a"].Value<string>();
                var b = pair["b"].Value<string>();
                var key = a + "|" + b;
                result[key] = new Dictionary<Rep, int[]>();
                for (var ri = 0; ri < reps.Length; ri++)
                {
                    int sd = 0, td = 0, od = 0, fl = 0;
                    for (var i = 0; i < Profiles; i++)
                    {
                        var x = outs[a][i][ri];
                        var y = outs[b][i][ri];
                        if (Math.Abs((x.Support.TryGetValue("protect", out var sx) ? sx : 0.0) - (y.Support.TryGetValue("protect", out var sy) ? sy : 0.0)) > Tie) sd++;
                        if (x.Trace != y.Trace) td++;
                        if (x.P0 != y.P0) od++;
                        if (y.Recognised > x.Recognised) fl++;
                    }
                    result[key][reps[ri]] = new[] { sd, td, od, fl };
                }
            }
            return result;
        }

        static Rule FrozenRule(JObject c, Dictionary<string, JObject> decl)
        {
            var id = c["id"].Value<string>();
            var roles = (decl[id]["roles"] as JObject)?.Properties().ToDictionary(p => p.Name, p => p.Value.Value<string>(), StringComparer.Ordinal) ?? new Dictionary<string, string>(StringComparer.Ordinal);
            var map = ((JObject)_spec["frozen_reading"]["role_map"]).Properties().ToDictionary(p => p.Name, p => p.Value.Value<string>(), StringComparer.Ordinal);
            var when = c["when"] as JObject ?? new JObject();
            var rule = new Rule
            {
                Id = id, Intent = c["intent"].Value<string>(), Route = decl[id]["route"].Value<string>(), When = Gate(when), Base = c["base"]?.Value<double>() ?? 0.0,
                Motives = ((JArray)c["motives"]).Select(x => x.Value<string>()).ToList()
            };
            rule.Gate = GateKey(rule.When);
            foreach (JObject t in (JArray)c["scaled_by"] ?? new JArray())
            {
                var sc = ScalerOf(t);
                var key = EvidenceKey(sc);
                var role = roles.TryGetValue(key, out var r) ? map[r] : sc.Factor < 0 ? "inhibitor" : "support";
                rule.Terms.Add(new Term { Key = key, K = Register(sc), Factor = sc.Factor, Role = role, Kind = sc.Kind });
            }
            return rule;
        }

        // ============================================================ 3: the frozen file

        static List<Rule> _frozenRules;
        static readonly Dictionary<string, Case> _frozenCases = new Dictionary<string, Case>(StringComparer.Ordinal);

        static Case FrozenCase(string want)
        {
            if (_frozenRules == null)
            {
                var decl = ((JArray)_routesJson["frozen"]["routes"]).ToDictionary(r => r["rule"].Value<string>(), r => (JObject)r, StringComparer.Ordinal);
                _frozenRules = ((JArray)JObject.Parse(File.ReadAllText(Path.Combine(TestPaths.DataRoot, "Experiments", "intentions.json")))["candidates"]).Cast<JObject>().Select(c => FrozenRule(c, decl)).ToList();
            }
            if (_frozenCases.TryGetValue(want, out var k)) return k;
            k = new Case { Id = "frozen:" + want, Want = want, Intent = null };
            foreach (var r in _frozenRules.Where(r => r.Motives.Contains(want, StringComparer.Ordinal)))
            {
                k.Rules.Add(r);
                k.Routes.Add(new Route { Key = r.Route, Intent = r.Intent, AppliesWhen = GateAsPredicates(r.When) });
            }
            _frozenCases[want] = k;
            return k;
        }

        static readonly Rep[] FrozenReps = { Rep.S, Rep.A, Rep.B, Rep.C, Rep.CSplit, Rep.BW };

        [Test, Order(3), Timeout(7200000)]
        public void C_TheFrozenFile()
        {
            var answerable = _keyIndex["belief:answerable_for($self,missing_can)"];
            var tokens = new Dictionary<string, List<string>>(StringComparer.Ordinal);
            foreach (var r in FrozenReps) foreach (var p in new[] { "P0", "P1" }) tokens[Name(r) + " " + p] = new List<string>();
            var groups = new List<string>();
            foreach (var w in Wants)
            {
                var c = FrozenCase(w);
                for (var i = 0; i < Profiles; i++)
                    foreach (var company in new[] { true, false })
                    {
                        var p = company ? _company[i] : _alone[i];
                        var present = company ? new List<string> { "a", "b", "c" } : new List<string>();
                        groups.Add("`" + w + "` " + (company ? "in company" : "alone") + "|" + (_lv[i][answerable] > 0.0 ? "believer" : "no belief"));
                        foreach (var r in FrozenReps)
                        {
                            var o = Evaluate(c, _lv[i], present, "a", p, r);
                            tokens[Name(r) + " P0"].Add(o.P0);
                            tokens[Name(r) + " P1"].Add(o.P1);
                        }
                    }
            }
            var n = groups.Count;
            var baseline = tokens["A P0"];
            var sb = new StringBuilder();
            sb.AppendLine("## 3. Behaviour on the frozen file");
            sb.AppendLine();
            sb.AppendLine("`intentions.json` with the causal-route routes and roles, unchanged: the declared enabler read as a condition, negative factors as inhibitors, gates as generic circumstances. " + N(n) + " cells (" + N(Profiles) + " profiles x " + Wants.Length + " wants x 2 circumstances). Differences are counted against A under P0, the causal-route experiment's representation.");
            sb.AppendLine();
            sb.AppendLine("| | Differs from A, P0 | No intention | Ties |");
            sb.AppendLine("|---|---|---|---|");
            foreach (var kv in tokens)
                sb.AppendLine("| " + kv.Key + " | " + NP(Enumerable.Range(0, n).Count(k => kv.Value[k] != baseline[k]), n) + " | " + N(kv.Value.Count(t => t == "none")) + " | " + N(kv.Value.Count(t => t.StartsWith("tie(", StringComparison.Ordinal))) + " |");
            sb.AppendLine();
            foreach (var key in new[] { "B P0", "C P0" })
            {
                sb.AppendLine("**" + key + " against A, P0:**");
                sb.AppendLine();
                sb.AppendLine("| Group | Profile | A | " + key + " | Cells |");
                sb.AppendLine("|---|---|---|---|---|");
                foreach (var g in Enumerable.Range(0, n).Where(k => tokens[key][k] != baseline[k]).GroupBy(k => groups[k] + "|" + baseline[k] + "|" + tokens[key][k]).OrderByDescending(g => g.Count()))
                {
                    var p = g.Key.Split('|');
                    sb.AppendLine("| " + p[0] + " | " + p[1] + " | " + p[2] + " | " + p[3] + " | " + N(g.Count()) + " |");
                }
                sb.AppendLine();
            }
            Record("3", sb.ToString());
        }

        // ============================================================ 4: real mornings

        [Test, Order(4), Timeout(7200000)]
        public void D_RealMornings()
        {
            var reps = new[] { Rep.A, Rep.B, Rep.C, Rep.CSplit, Rep.BW };
            var pantryWants = _content.Rules.Proposals.Where(p => p.Action == "check_pantry").Select(p => p.Motive).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
            var moments = 0;
            var live = 0;
            var real = 0;
            var stats = new Dictionary<string, int>(StringComparer.Ordinal);
            void Inc(string k) => stats[k] = (stats.TryGetValue(k, out var v) ? v : 0) + 1;
            var examples = new List<string>();

            foreach (var variant in _content.Morning.Variants.Select(v => v.Id))
                for (ulong seed = 1; seed <= MorningSeeds; seed++)
                {
                    var run = Scenario001.Prepare(_content, variant, seed);
                    var label = variant + "/" + seed;
                    run.Morning.Decided = moment =>
                    {
                        moments++;
                        var mind = moment.Mind;
                        var p = moment.Percept;
                        var target = p.Present.FirstOrDefault();
                        var present = p.Present.ToList();
                        foreach (var w in Wants)
                        {
                            var c = FrozenCase(w);
                            if (!c.Rules.Any(r => r.When.Matches(p))) continue;
                            live++;
                            var lv = Levels(mind, p, target);
                            var baseOut = Evaluate(c, lv, present, target, p, Rep.A);
                            foreach (var r in reps)
                            {
                                var o = Evaluate(c, lv, present, target, p, r);
                                foreach (var pol in new[] { "P0", "P1" })
                                {
                                    var tok = pol == "P0" ? o.P0 : o.P1;
                                    if (tok != baseOut.P0) Inc("live changed " + Name(r) + " " + pol);
                                    if (tok == "none") Inc("live none " + Name(r) + " " + pol);
                                    if (tok.StartsWith("tie(", StringComparison.Ordinal)) Inc("live tie " + Name(r) + " " + pol);
                                }
                            }
                        }

                        var d = moment.Decision;
                        var leading = d.Leading;
                        if (d.Chosen == null || d.Chosen.KindName != "check_pantry" || leading == null || !pantryWants.Contains(leading.Name)) return;
                        var people = new List<Tuple<string, Mind>> { Tuple.Create(moment.CharacterId, mind) };
                        foreach (var y in Cast.Where(x => x != moment.CharacterId)) people.Add(Tuple.Create(y, run.Simulation.Minds[y]));
                        var fc = FrozenCase(leading.Name);
                        foreach (var person in people)
                        {
                            real++;
                            var lv = Levels(person.Item2, p, target);
                            var a = Evaluate(fc, lv, present, target, p, Rep.A);
                            var aExplain = a.Explanation(a.P0);
                            foreach (var r in reps)
                            {
                                var o = Evaluate(fc, lv, present, target, p, r);
                                foreach (var pol in new[] { "P0", "P1" })
                                {
                                    var tok = pol == "P0" ? o.P0 : o.P1;
                                    if (tok != a.P0)
                                    {
                                        Inc("real intention changed " + Name(r) + " " + pol);
                                        if (r == Rep.C && pol == "P0" && examples.Count < 8)
                                            examples.Add("| " + label + " m" + moment.Minute + " | " + person.Item1 + (person.Item1 == moment.CharacterId ? " (checking)" : " (matched)") + " | `" + leading.Name + "` | " + a.P0 + " | " + tok + " |");
                                    }
                                    else if (o.Explanation(tok) != aExplain) Inc("real explanation only " + Name(r) + " " + pol);
                                    if (tok == "none") Inc("real none " + Name(r) + " " + pol);
                                }
                            }
                        }
                    };
                    run.Morning.Run(_content.Morning.Minutes);
                }

            int G(string k) => stats.TryGetValue(k, out var v) ? v : 0;
            var sb = new StringBuilder();
            sb.AppendLine("## 4. Real mornings");
            sb.AppendLine();
            sb.AppendLine("50 baseline mornings (" + _content.Morning.Variants.Count + " variants x " + MorningSeeds + " seeds), the frozen file read as in section 3. **Real decisions:** every real pantry-check for a want whose shipped proposals lead there, and every other member of the cast at the same moment: **" + N(real) + "**. **Live cells:** every decision moment (" + N(moments) + ") asked about every want with a compatible rule: **" + N(live) + "**. Everything is compared with A under P0, the causal-route experiment's representation.");
            sb.AppendLine();
            sb.AppendLine("| | " + string.Join(" | ", reps.SelectMany(r => new[] { Name(r) + " P0", Name(r) + " P1" })) + " |");
            sb.AppendLine("|---|" + string.Join("|", reps.SelectMany(r => new[] { "---", "---" })) + "|");
            sb.AppendLine("| Real decisions whose intention changed, of " + N(real) + " | " + string.Join(" | ", reps.SelectMany(r => new[] { NP(G("real intention changed " + Name(r) + " P0"), real), NP(G("real intention changed " + Name(r) + " P1"), real) })) + " |");
            sb.AppendLine("| Real decisions whose explanation changed, the act not | " + string.Join(" | ", reps.SelectMany(r => new[] { N(G("real explanation only " + Name(r) + " P0")), N(G("real explanation only " + Name(r) + " P1")) })) + " |");
            sb.AppendLine("| Real decisions with no intention | " + string.Join(" | ", reps.SelectMany(r => new[] { N(G("real none " + Name(r) + " P0")), N(G("real none " + Name(r) + " P1")) })) + " |");
            sb.AppendLine("| Live cells whose outcome changed, of " + N(live) + " | " + string.Join(" | ", reps.SelectMany(r => new[] { NP(G("live changed " + Name(r) + " P0"), live), NP(G("live changed " + Name(r) + " P1"), live) })) + " |");
            sb.AppendLine("| Live cells with no intention | " + string.Join(" | ", reps.SelectMany(r => new[] { N(G("live none " + Name(r) + " P0")), N(G("live none " + Name(r) + " P1")) })) + " |");
            sb.AppendLine("| Live cells ending in a tie | " + string.Join(" | ", reps.SelectMany(r => new[] { N(G("live tie " + Name(r) + " P0")), N(G("live tie " + Name(r) + " P1")) })) + " |");
            if (examples.Count > 0)
            {
                sb.AppendLine();
                sb.AppendLine("Real decisions C changes under P0 (the first eight):");
                sb.AppendLine();
                sb.AppendLine("| Morning | Who | Want | A | C, P0 |");
                sb.AppendLine("|---|---|---|---|---|");
                foreach (var e in examples) sb.AppendLine(e);
            }
            Record("4", sb.ToString());
        }

        // ============================================================ 5: the blind annotation

        static readonly string[] QYes = { "yes", "no", "unclear" };
        static readonly string[] QFacts = { "prerequisite", "supporting", "inhibiting", "circumstance", "no_part", "unclear" };
        static readonly string[] Q8 = { "disappear", "weaker_or_stronger", "no_change", "unclear" };

        static double Fleiss(IReadOnlyList<Dictionary<string, int>> counts, IReadOnlyList<string> categories)
        {
            if (counts.Count == 0) return double.NaN;
            var n = counts[0].Values.Sum();
            var pi = counts.Select(c => (c.Values.Sum(x => x * (x - 1.0))) / (n * (n - 1.0))).Average();
            var pj = categories.Select(cat => counts.Sum(c => c.TryGetValue(cat, out var v) ? v : 0) / (double)(counts.Count * n)).ToList();
            var pe = pj.Sum(p => p * p);
            return Math.Abs(1.0 - pe) < 1e-12 ? double.NaN : (pi - pe) / (1.0 - pe);
        }

        static string K(double k) => double.IsNaN(k) ? "n/a" : k.ToString("0.000", CultureInfo.InvariantCulture);

        static Dictionary<string, int> Tally(IEnumerable<string> answers, IReadOnlyList<string> categories)
        {
            var t = categories.ToDictionary(c => c, c => 0, StringComparer.Ordinal);
            foreach (var a in answers) t[a != null && t.ContainsKey(a) ? a : "unclear"]++;
            return t;
        }

        static string Majority(Dictionary<string, int> t)
        {
            var max = t.Values.Max();
            var top = t.Where(kv => kv.Value == max).Select(kv => kv.Key).ToList();
            return top.Count == 1 ? top[0] : "tie";
        }

        static string Counts(Dictionary<string, int> t) => string.Join(", ", t.Where(kv => kv.Value > 0).OrderByDescending(kv => kv.Value).Select(kv => kv.Key + " " + kv.Value));

        static readonly Dictionary<string, string> _annotationMajority = new Dictionary<string, string>(StringComparer.Ordinal);
        static readonly Dictionary<string, double> _annotationKappa = new Dictionary<string, double>(StringComparer.Ordinal);

        [Test, Order(5), Timeout(7200000)]
        public void E_TheBlindAnnotation()
        {
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "experiments", "route-applicability", "annotation");
            var itemsJson = JObject.Parse(File.ReadAllText(Path.Combine(dir, "items.json")));
            var items = ((JArray)itemsJson["items"]).Cast<JObject>().ToList();
            var key = (JObject)itemsJson["answer_key"];
            var reviewers = Directory.GetFiles(Path.Combine(dir, "responses"), "reviewer-*.json").OrderBy(f => f, StringComparer.Ordinal).Select(f => JObject.Parse(File.ReadAllText(f))).ToList();
            var by = items.ToDictionary(it => it["id"].Value<string>(), it => new List<JObject>(), StringComparer.Ordinal);
            foreach (var rv in reviewers)
            {
                var answers = ((JArray)rv["answers"]).Cast<JObject>().ToDictionary(x => x["id"].Value<string>(), x => x, StringComparer.Ordinal);
                for (var k = 0; k < items.Count; k++)
                    by[items[k]["id"].Value<string>()].Add(answers.TryGetValue("item-" + (k + 1).ToString("00"), out var a) ? a : new JObject());
            }
            string Norm(string s) => s?.Trim().ToLowerInvariant();
            var q7Cats = new List<string> { "none", "anyone", "unclear" };
            foreach (var rv in by.Values) foreach (var a in rv) { var v = Norm(a["q7"]?.Value<string>()); if (v != null && !q7Cats.Contains(v)) q7Cats.Add(v); }

            var t1 = new List<Dictionary<string, int>>();
            var tf = new List<Dictionary<string, int>>();
            var t7 = new List<Dictionary<string, int>>();
            var t8 = new List<Dictionary<string, int>>();
            var t9 = new List<Dictionary<string, int>>();
            var sb = new StringBuilder();
            sb.AppendLine("## 5. The blind annotation");
            sb.AppendLine();
            sb.AppendLine(reviewers.Count + " reviewers (" + string.Join(", ", reviewers.Select(r => "#" + r["reviewer"] + " " + r["model"])) + "), fresh subagents, shown only the items under neutral ids, in rotated order. **They are language models, not people**: their agreement is legibility and reproducibility evidence only, never psychological validation.");
            sb.AppendLine();
            sb.AppendLine("| Item | Q1 key | Q1 | Q7 key | Q7 | Q8 key | Q8 | Q9 key | Q9 | Matches (Q1, Q7, Q8, Q9) |");
            sb.AppendLine("|---|---|---|---|---|---|---|---|---|---|");
            var match = new Dictionary<string, int[]>(StringComparer.Ordinal) { ["q1"] = new int[2], ["q7"] = new int[2], ["q8"] = new int[2], ["q9"] = new int[2], ["facts"] = new int[2] };
            foreach (var it in items)
            {
                var id = it["id"].Value<string>();
                var k = (JObject)key[id];
                var a1 = Tally(by[id].Select(x => Norm(x["q1"]?.Value<string>())), QYes);
                var a7 = Tally(by[id].Select(x => Norm(x["q7"]?.Value<string>())), q7Cats);
                var a8 = Tally(by[id].Select(x => Norm(x["q8"]?.Value<string>())), Q8);
                t1.Add(a1); t7.Add(a7); t8.Add(a8);
                var m1 = Majority(a1); var m7 = Majority(a7); var m8 = Majority(a8);
                _annotationMajority[id + "|q1"] = m1; _annotationMajority[id + "|q7"] = m7; _annotationMajority[id + "|q8"] = m8;
                var marks = new List<string>();
                void M(string q, string maj, string want) { match[q][1]++; if (maj == want) match[q][0]++; marks.Add(maj == want ? "yes" : "**no**"); }
                M("q1", m1, k["q1"].Value<string>());
                M("q7", m7, k["q7"].Value<string>());
                M("q8", m8, k["q8"].Value<string>());
                var q9 = "-";
                var m9 = "-";
                if (k["q9"] != null)
                {
                    var a9 = Tally(by[id].Select(x => Norm(x["q9"]?.Value<string>())), QYes);
                    t9.Add(a9);
                    m9 = Majority(a9);
                    q9 = Counts(a9);
                    _annotationMajority[id + "|q9"] = m9;
                    M("q9", m9, k["q9"].Value<string>());
                }
                sb.AppendLine("| `" + id + "` | " + k["q1"] + " | " + Counts(a1) + " | " + k["q7"] + " | " + Counts(a7) + " | " + k["q8"] + " | " + Counts(a8) + " | " + (k["q9"]?.Value<string>() ?? "-") + " | " + q9 + " | " + string.Join(", ", marks) + " |");
            }
            sb.AppendLine();
            sb.AppendLine("### The part each fact plays (Q3 to Q6)");
            sb.AppendLine();
            sb.AppendLine("| Item | Fact | Key | Answers | Majority | Matches |");
            sb.AppendLine("|---|---|---|---|---|---|");
            foreach (var it in items)
            {
                var id = it["id"].Value<string>();
                var facts = ((JArray)it["draws_on"]).Select(x => x.Value<string>()).ToList();
                var keys = ((JArray)key[id]["facts"]).Select(x => x.Value<string>()).ToList();
                for (var f = 0; f < facts.Count; f++)
                {
                    var t = Tally(by[id].Select(x => Norm((x["facts"] as JArray)?.ElementAtOrDefault(f)?.Value<string>())), QFacts);
                    tf.Add(t);
                    var maj = Majority(t);
                    _annotationMajority[id + "|f" + f] = maj;
                    match["facts"][1]++;
                    if (maj == keys[f]) match["facts"][0]++;
                    sb.AppendLine("| `" + id + "` | " + facts[f] + " | " + keys[f] + " | " + Counts(t) + " | " + maj + " | " + (maj == keys[f] ? "yes" : "**no**") + " |");
                }
            }
            _annotationKappa["q1"] = Fleiss(t1, QYes);
            _annotationKappa["facts"] = Fleiss(tf, QFacts);
            _annotationKappa["q7"] = Fleiss(t7, q7Cats);
            _annotationKappa["q8"] = Fleiss(t8, Q8);
            _annotationKappa["q9"] = Fleiss(t9, QYes);
            sb.AppendLine();
            sb.AppendLine("### Agreement");
            sb.AppendLine();
            sb.AppendLine("| Question | Majority matches the key | Fleiss' kappa |");
            sb.AppendLine("|---|---|---|");
            foreach (var q in new[] { "q1", "facts", "q7", "q8", "q9" })
                sb.AppendLine("| " + q + " | " + match[q][0] + " of " + match[q][1] + " (" + Pc(match[q][0], match[q][1]) + ") | **" + K(_annotationKappa[q]) + "** |");
            sb.AppendLine();
            sb.AppendLine("### Condition against circumstance, as readers see it");
            sb.AppendLine();
            string L(string id, int f) => _annotationMajority[id + "|f" + f];
            string E(string id) => _annotationMajority[id + "|q8"];
            sb.AppendLine("| | Items | Label (majority) | If it changed (Q8, majority) |");
            sb.AppendLine("|---|---|---|---|");
            sb.AppendLine("| A belief the reason needs | `cond_absent`, `cond_present`, `no_route_cond` | " + string.Join(", ", new[] { "cond_absent", "cond_present", "no_route_cond" }.Select(i => L(i, 0))) + " | " + string.Join(", ", new[] { "cond_absent", "cond_present", "no_route_cond" }.Select(E)) + " |");
            sb.AppendLine("| A person's presence the reason needs | `side_target`, `side_other`, `side_nobody`, `no_route_circ`, `target_daniel` | " + string.Join(", ", new[] { "side_target", "side_other", "side_nobody", "no_route_circ", "target_daniel" }.Select(i => L(i, 2))) + " | " + string.Join(", ", new[] { "side_target", "side_other", "side_nobody", "no_route_circ", "target_daniel" }.Select(E)) + " |");
            sb.AppendLine("| Anyone's presence the reason needs | `scene_other`, `scene_nobody` | " + string.Join(", ", new[] { "scene_other", "scene_nobody" }.Select(i => L(i, 2))) + " | " + string.Join(", ", new[] { "scene_other", "scene_nobody" }.Select(E)) + " |");
            sb.AppendLine("| The same belief as support | `evid_absent` | " + L("evid_absent", 0) + " | " + E("evid_absent") + " |");
            sb.AppendLine();
            sb.AppendLine("### Q2, verbatim");
            sb.AppendLine();
            foreach (var it in items)
            {
                var id = it["id"].Value<string>();
                sb.AppendLine("**`" + id + "`**");
                sb.AppendLine();
                for (var r = 0; r < reviewers.Count; r++)
                    sb.AppendLine("- #" + reviewers[r]["reviewer"] + " " + reviewers[r]["model"] + ": " + (by[id][r]["q2"]?.Value<string>() ?? "(no answer)"));
                sb.AppendLine();
            }
            Record("5", sb.ToString());
        }

        // ============================================================ 6: success criteria and element status

        [Test, Order(6), Timeout(7200000)]
        public void F_WhatTheEvidenceSupports()
        {
            if (_fam.Count == 0) A_TheRouteLayer();
            if (_controls.Count == 0) B_IrrelevantFactsAndTheCausalRouteControls();
            if (_annotationMajority.Count == 0) E_TheBlindAnnotation();
            bool FamPass(string f, Rep r) => FamOf(f, r).Pass;
            bool Controls(Rep r, string prefix) => _controls.Where(k => k.Key.StartsWith(prefix, StringComparison.Ordinal)).All(k => k.Value[r] == 0);
            bool IPass(Rep r) => (r == Rep.S || _reproduced18[r] == 18) && Controls(r, "I.");

            var families = new[] { "A", "B", "C", "D", "E", "F", "G", "H", "I", "J" };
            var sb = new StringBuilder();
            sb.AppendLine("## 6. Families passed, and what each element of C is worth");
            sb.AppendLine();
            sb.AppendLine("| Family | " + string.Join(" | ", Main.Select(Name)) + " |");
            sb.AppendLine("|---|" + string.Join("|", Main.Select(_ => "---")) + "|");
            var passed = Main.ToDictionary(r => r, r => 0);
            foreach (var f in families)
            {
                var cells = Main.Select(r =>
                {
                    var p = f == "H" ? Controls(r, "H.") : f == "I" ? IPass(r) : FamPass(f, r);
                    if (p) passed[r]++;
                    return p ? "pass" : "**fail**";
                });
                sb.AppendLine("| " + f + " | " + string.Join(" | ", cells) + " |");
            }
            sb.AppendLine("| **Passed, of 10** | " + string.Join(" | ", Main.Select(r => "**" + passed[r] + "**")) + " |");
            sb.AppendLine();

            // The split: does C-split differ from C at the route layer?
            var appDiff = 0;
            var stateDiff = 0;
            var compared = 0;
            foreach (var c in _cases)
                foreach (var x in Cells())
                {
                    var a = At(c, x.Item1, x.Item2, Rep.C);
                    var b = At(c, x.Item1, x.Item2, Rep.CSplit);
                    compared++;
                    if (c.Routes.Any(r => a.App[r.Key] != b.App[r.Key])) appDiff++;
                    if (c.Intents.Any(i => a.State[i] != b.State[i])) stateDiff++;
                }
            sb.AppendLine("**Condition and circumstance, one construct or two.** Over all " + _cases.Count + " cases x " + N(CellsPerCase) + " = " + N(compared) + " cells: C-split's route applicability differs from C's in **" + N(appDiff) + "**; the recorded state differs (\"no candidate\" instead of \"no applicable route\") in **" + N(stateDiff) + "**.");
            sb.AppendLine();

            string Legible(params string[] tests)
                => tests.All(t => { var p = t.Split('='); return _annotationMajority.TryGetValue(p[0], out var m) && m == p[1]; }) ? "yes" : "no";
            sb.AppendLine("| Element of C | Removing it fails | Over-applying it fails | Readers draw it (majorities) |");
            sb.AppendLine("|---|---|---|---|");
            sb.AppendLine("| Conditions (a declared prerequisite, not a weight) | C-conditions: " + string.Join(", ", families.Where(f => f != "H" && f != "I" && !FamPass(f, Rep.CConditions))) + " | C-kind: " + (FamPass("B", Rep.CKind) ? "nothing" : "B (the belief as evidence)") + " | " + Legible("cond_absent|f0=prerequisite", "cond_present|f0=prerequisite", "no_route_cond|f0=prerequisite", "evid_absent|f0=supporting", "cond_absent|q8=disappear", "evid_absent|q8=weaker_or_stronger") + " |");
            sb.AppendLine("| Target binding (a circumstance about the want's target) | C-entity: " + string.Join(", ", families.Where(f => f != "H" && f != "I" && !FamPass(f, Rep.CEntity))) + " | C-kind: " + (FamPass("J", Rep.CKind) ? "nothing" : "J (generic presence)") + " | " + Legible("side_target|q7=person:mara", "side_other|q7=person:mara", "target_daniel|q7=person:daniel", "scene_other|q7=anyone", "side_other|q1=no", "scene_other|q1=yes") + " |");
            sb.AppendLine("| Applicability separate from strength | S (the discard): " + string.Join(", ", new[] { "E", "F", "G" }.Where(f => !FamPass(f, Rep.S))) + " | - | " + Legible("support_low|q8=weaker_or_stronger", "inhibitor_high|q8=weaker_or_stronger", "side_other|q8=disappear") + " |");
            sb.AppendLine("| No applicable route, recorded at the route | B: " + (FamPass("G", Rep.B) ? "nothing" : "G") + "; A: " + (FamPass("G", Rep.A) ? "nothing" : "G") + " | - | " + Legible("no_route_circ|q9=no", "no_route_cond|q9=no") + " |");
            sb.AppendLine();
            sb.AppendLine("Kappa: Q1 " + K(_annotationKappa["q1"]) + ", facts " + K(_annotationKappa["facts"]) + ", Q7 " + K(_annotationKappa["q7"]) + ", Q8 " + K(_annotationKappa["q8"]) + ", Q9 " + K(_annotationKappa["q9"]) + ".");
            Record("6", sb.ToString());
        }

        // ============================================================ Z

        [Test, Order(99)]
        public void Z_TheFilesAreUntouchedAfterEverything()
        {
            var sb = new StringBuilder();
            sb.AppendLine("## Z. The files after the whole run");
            sb.AppendLine();
            sb.AppendLine("| File | sha256 | |");
            sb.AppendLine("|---|---|---|");
            foreach (var kv in Frozen)
            {
                var sha = Sha(FrozenPath(kv.Key));
                sb.AppendLine("| `" + kv.Key + "` | `" + sha + "` | " + (sha == kv.Value ? "unchanged" : "**CHANGED**") + " |");
                Assert.AreEqual(kv.Value, sha, kv.Key);
            }
            sb.AppendLine();
            sb.AppendLine("Every case, rewrite and representation above lived in memory.");
            Record("Z", sb.ToString());
        }
    }
}
