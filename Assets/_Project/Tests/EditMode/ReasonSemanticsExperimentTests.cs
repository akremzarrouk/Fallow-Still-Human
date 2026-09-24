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
    /// What must a simulated reason contain to tell genuinely different causal
    /// explanations apart, without turning conditions into weights,
    /// circumstances into hidden gates, or competing reasons into arithmetic?
    ///
    /// Every case, every representation's reading rule and every check is
    /// declared in `Data/Experiments/reason-semantics.json`, committed with the
    /// predictions before this fixture existed. Six representations read the
    /// same cases: S (the shipped selector, the control), A (reasons and
    /// weights), B-parts, B-circ, B and C, each holding a little more of the
    /// declared meaning. Nothing is tuned per case, and nothing here is
    /// production. Writes `Docs/experiments/reason-semantics/measurements.md`.
    /// </summary>
    public class ReasonSemanticsExperimentTests
    {
        const string FrozenSha = "61e6412e8a7cb77674f0c7685e4cb0e5f7dca5db3ad05f928a63f34dfb099d92";
        const string RoutesSha = "781b776d3a1cbbba78cc215c85af4750261a79f998c317f6a1ee920c4c37828a";
        const string SweepSha = "0b3f4bc95fbeffbf4e1359b8779a45fdefabdbfb3bed28b3f4de975781ff4131";
        const string CasesSha = "5ffe17feb1cfe3cd36cf4043e06a75812133846ac5bfc3f51469b4eeeedc7638";
        const double Eps = 1e-9;
        const int MorningSeeds = 10;

        static Scenario001Content _content;
        static JObject _spec;
        static string _casesPath, _frozenPath, _routesPath, _sweepPath;
        static readonly SortedDictionary<string, string> _results = new SortedDictionary<string, string>(StringComparer.Ordinal);

        static readonly string[] Wants =
            { "avoid_exposure", "find_out", "get_food", "guard_supplies", "keep_peace", "look_after", "restore_standing" };
        static readonly string[] Cast = { "daniel", "elena", "leo", "mara" };

        static List<string> _sweepTraits;
        static List<double> _traitLevels;
        static List<string> _ring;
        static List<List<BeliefSeed>> _beliefSets;
        static Mind[] _minds;
        static RoomGraph _house;
        static string _kitchen;

        // ============================================================ representations

        enum Rep { S, A, BParts, BCirc, B, C, ASel2, BSel0, BSel1, BPartsW }

        static readonly Rep[] Main = { Rep.S, Rep.A, Rep.BParts, Rep.BCirc, Rep.B, Rep.C };
        static readonly Rep[] Ablations = { Rep.ASel2, Rep.BSel0, Rep.BSel1 };

        static string Name(Rep r)
        {
            switch (r)
            {
                case Rep.BParts: return "B-parts";
                case Rep.BCirc: return "B-circ";
                case Rep.ASel2: return "A-Sel2";
                case Rep.BSel0: return "B-Sel0";
                case Rep.BSel1: return "B-Sel1";
                case Rep.BPartsW: return "B-parts+w";
                default: return r.ToString();
            }
        }

        static bool Parts(Rep r) => r == Rep.BParts || r == Rep.B || r == Rep.C || r == Rep.BSel0 || r == Rep.BSel1 || r == Rep.BPartsW;
        static bool Circ(Rep r) => r == Rep.BCirc || r == Rep.B || r == Rep.C || r == Rep.BSel0 || r == Rep.BSel1;
        static bool Rel(Rep r) => r == Rep.C;
        static int Sel(Rep r) => r == Rep.A || r == Rep.BSel0 ? 0 : r == Rep.BSel1 ? 1 : 2;

        // ============================================================ facts, situations, cases

        static readonly List<string> _keys = new List<string>();
        static readonly Dictionary<string, int> _keyIndex = new Dictionary<string, int>(StringComparer.Ordinal);
        static readonly List<Scaler> _keyScaler = new List<Scaler>();
        static double[][] _lv;   // [profile][fact]

        sealed class Sit
        {
            public string Id;
            public string Label;
            public bool Others, Target, Watched;
        }

        static List<Sit> _sits;
        static Percept[][] _percepts;   // [profile][situation]
        static Dictionary<string, List<KeyValuePair<string, bool>>> _circs;

        sealed class Term
        {
            public string Key;
            public int K;
            public double Factor;
            public string Part;
            public string Route;
        }

        sealed class Rule
        {
            public string Id;
            public string Intent;
            public string Route;
            public SituationCondition When;
            public JObject WhenJson;
            public string Gate;
            public double Base;
            public List<Term> Terms = new List<Term>();
            public string Push;
            public List<string> Motives = new List<string>();
        }

        sealed class Route
        {
            public string Key;
            public string Intent;
            public string Direction;
            public string Circ;
            public string Copied;
            public List<KeyValuePair<string, double>> Pushes = new List<KeyValuePair<string, double>>();
        }

        sealed class Relation
        {
            public string Kind;
            public List<string> Routes;
        }

        sealed class Case
        {
            public string Id, Family, Want, Intent;
            public bool Rival;
            public List<Rule> Rules = new List<Rule>();
            public List<Route> Routes = new List<Route>();
            public List<Relation> Relations = new List<Relation>();
            public Dictionary<string, string> Canon = new Dictionary<string, string>(StringComparer.Ordinal);
            public Dictionary<string, int> RouteIndex = new Dictionary<string, int>(StringComparer.Ordinal);
            public List<string> Intents = new List<string>();

            public void Index()
            {
                RouteIndex.Clear();
                for (var i = 0; i < Routes.Count; i++) RouteIndex[Routes[i].Key] = i;
                Intents = Routes.Select(r => r.Intent).Distinct().ToList();
                foreach (var r in Routes)
                    if (!Canon.ContainsKey(r.Key)) Canon[r.Key] = r.Key;
            }

            public string CanonOf(string key) => Canon.TryGetValue(key, out var c) ? c : key;
        }

        static List<Case> _cases;
        static Dictionary<string, Case> _byId;
        static List<JObject> _checks;

        [OneTimeSetUp]
        public void Load()
        {
            _content = Baselines.Primary();
            _casesPath = Path.Combine(TestPaths.DataRoot, "Experiments", "reason-semantics.json");
            _frozenPath = Path.Combine(TestPaths.DataRoot, "Experiments", "intentions.json");
            _routesPath = Path.Combine(TestPaths.DataRoot, "Experiments", "causal-routes.json");
            _sweepPath = Path.Combine(TestPaths.DataRoot, "Experiments", "held-out-people.json");
            _spec = JObject.Parse(File.ReadAllText(_casesPath));

            var s = (JObject)JObject.Parse(File.ReadAllText(_sweepPath))["sweep"];
            _sweepTraits = ((JArray)s["traits"]).Select(x => x.Value<string>()).ToList();
            _traitLevels = ((JArray)s["levels"]).Select(x => x.Value<double>()).ToList();
            _ring = ((JArray)s["value_ring"]).Select(x => x.Value<string>()).ToList();
            _beliefSets = ((JArray)s["belief_sets"]).Select(set => ((JArray)set).Select(b => new BeliefSeed(
                b["predicate"].Value<string>(),
                ((JArray)b["args"]).Select(a => a.Value<string>()).ToList(),
                b["confidence"].Value<double>())).ToList()).ToList();

            var run = Scenario001.Prepare(_content, _content.Morning.Variants[0].Id, 1);
            _house = run.World.House;
            _kitchen = _house.Rooms.First(r => r.HasTag(ActionCatalog.PantryTag)).Id;

            _circs = ((JObject)_spec["circumstances"]).Properties().ToDictionary(
                p => p.Name,
                p => ((JObject)p.Value).Properties().Select(f => new KeyValuePair<string, bool>(f.Name, f.Value.Value<bool>())).ToList(),
                StringComparer.Ordinal);
            _sits = ((JArray)_spec["situations"]).Select(x => new Sit
            {
                Id = x["id"].Value<string>(),
                Label = x["label"].Value<string>(),
                Others = x["others_present"].Value<bool>(),
                Target = x["target_present"].Value<bool>(),
                Watched = x["watched"].Value<bool>()
            }).ToList();

            _cases = ((JArray)_spec["cases"]).Select(c => ParseCase((JObject)c)).ToList();
            _byId = _cases.ToDictionary(c => c.Id, c => c, StringComparer.Ordinal);
            _checks = ((JArray)_spec["checks"]).Cast<JObject>().ToList();

            // Every fact a frozen rule reads, and one no rule reads (for G.1), so
            // that the level table covers them all.
            foreach (var c in IntentionSelector.Load(_frozenPath))
                foreach (var sc in c.ScaledBy) Register(sc);
            Register(new Scaler { Kind = ScalerKind.Trait, Name = "impulsive" });
            foreach (var set in _beliefSets)
                foreach (var b in set) Register(new Scaler { Kind = ScalerKind.Belief, Predicate = b.Predicate, Args = b.Args.ToList() });

            var n = (int)Math.Pow(_traitLevels.Count, _sweepTraits.Count);
            _minds = new Mind[n];
            _percepts = new Percept[n][];
            _lv = new double[n][];
            for (var i = 0; i < n; i++)
            {
                _minds[i] = SweepMind(i);
                _percepts[i] = _sits.Select(x => At(_minds[i].Id, x)).ToArray();
                _lv[i] = Levels(_minds[i], _percepts[i][2], "a");
            }
        }

        [OneTimeTearDown]
        public void Write()
        {
            var sb = new StringBuilder();
            sb.AppendLine("# Reason semantics: measurements");
            sb.AppendLine();
            sb.AppendLine("Generated by `ReasonSemanticsExperimentTests` from the committed cases, the frozen candidate rules, the causal-route declarations and the sweep, all hashed at the start and the end of the run. The predictions, the cases, the reading rules, the checks and the annotation protocol were committed before this fixture existed. There is no randomness anywhere.");
            sb.AppendLine();
            foreach (var r in _results.Values) sb.AppendLine(r);
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "experiments", "reason-semantics");
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
        static string Pc(double part, double whole)
            => whole == 0 ? "n/a" : (100.0 * part / whole).ToString("0.0", CultureInfo.InvariantCulture) + " %";
        static string Pp(double a, double b) => ((a - b) >= 0 ? "+" : "") + (a - b).ToString("0.0", CultureInfo.InvariantCulture);

        static string Sha(string path)
        {
            using (var sha = SHA256.Create())
                return string.Concat(sha.ComputeHash(File.ReadAllBytes(path)).Select(b => b.ToString("x2")));
        }

        // ============================================================ people and moments

        static Mind Person(string id, IReadOnlyDictionary<string, double> traits,
            IReadOnlyList<string> values, IReadOnlyList<BeliefSeed> beliefs)
        {
            var profile = new Profile(id, id, 30, "sibling", traits, values, 0.5,
                new Dictionary<string, double>(), new List<BeliefSeed>());
            var mind = new Mind(profile);
            foreach (var b in beliefs ?? new List<BeliefSeed>())
                mind.Beliefs.Seed(new BeliefSeed(
                    b.Predicate, b.Args.Select(a => a == "$self" ? id : a).ToList(), b.Confidence));
            return mind;
        }

        static Mind SweepMind(int i)
        {
            var traits = new Dictionary<string, double>(StringComparer.Ordinal);
            var n = i;
            foreach (var name in _sweepTraits)
            {
                traits[name] = _traitLevels[n % _traitLevels.Count];
                n /= _traitLevels.Count;
            }
            var shift = i % _ring.Count;
            var values = _ring.Skip(shift).Concat(_ring.Take(shift)).ToList();
            return Person("p" + i, traits, values, _beliefSets[i % _beliefSets.Count]);
        }

        static Percept At(string who, Sit s)
        {
            var present = !s.Others ? new List<string>() : s.Target ? new List<string> { "a", "b", "c" } : new List<string> { "b", "c" };
            var room = _house.Get(_kitchen);
            return new Percept(who, 10, room, present, _house.Adjacent(room.Id), 0.3,
                true, true, false, _house, false, null, null);
        }

        static Motive Want(string key, string target = "a")
            => new Motive(key, target, 0.6, new List<string>(), new List<ScalerTerm>());

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
            _keyScaler.Add(new Scaler
            {
                Kind = s.Kind, Name = s.Name, Predicate = s.Predicate, Args = s.Args, Entry = s.Entry,
                About = s.About, Topic = s.Topic, By = s.By, Until = s.Until, Target = s.Target, Factor = 1.0
            });
            return k;
        }

        /// <summary>Every registered fact, read through the shipped ScalerEval.</summary>
        static double[] Levels(Mind mind, Percept p, string target)
        {
            var ctx = new DecisionContext(p, mind.Id, target, _content.Morning.Day, _content.Rules.Deciding.RecallHalfLife);
            var terms = ScalerEval.Evaluate(_keyScaler, mind, ctx);
            if (terms.Count != _keyScaler.Count) throw new InvalidOperationException("a fact was not evaluated");
            return terms.Select(t => t.Level).ToArray();
        }

        static bool Holds(string circ, Sit s)
        {
            if (!_circs.TryGetValue(circ, out var fs)) throw new InvalidOperationException("unknown circumstance " + circ);
            foreach (var f in fs)
            {
                var v = f.Key == "others_present" ? s.Others : f.Key == "target_present" ? s.Target : f.Key == "watched" ? s.Watched
                    : throw new InvalidOperationException("unknown feature " + f.Key);
                if (v != f.Value) return false;
            }
            return true;
        }

        static string GateKey(JObject w)
        {
            if (w == null || !w.Properties().Any()) return "any";
            return string.Join(",", w.Properties().OrderBy(p => p.Name, StringComparer.Ordinal).Select(p => p.Name + "=" + p.Value.ToString()));
        }

        static SituationCondition Gate(JObject w)
            => new SituationCondition
            {
                Alone = w?["alone"]?.Value<bool>(),
                InOwnRoom = w?["in_own_room"]?.Value<bool>(),
                InSomebodyElsesRoom = w?["in_somebody_elses_room"]?.Value<bool>(),
                RoomHoldsFood = w?["room_holds_food"]?.Value<bool>(),
                SearchedThisRoomMyself = w?["searched_this_room_myself"]?.Value<bool>(),
                OthersPresentMin = w?["others_present_min"]?.Value<int>()
            };

        static Scaler ScalerOf(JObject t)
            => new Scaler
            {
                Kind = t["kind"]?.Value<string>(),
                Name = t["name"]?.Value<string>(),
                Predicate = t["predicate"]?.Value<string>(),
                Args = (t["args"] as JArray ?? new JArray()).Select(a => a.Value<string>()).ToList(),
                Target = t["target"]?.Value<string>(),
                Factor = t["factor"]?.Value<double>() ?? 0.0
            };

        static Rule ParseRule(JObject r, string intent)
        {
            var when = r["when"] as JObject ?? new JObject();
            var rule = new Rule
            {
                Id = r["id"].Value<string>(),
                Intent = intent,
                Route = r["route"]?.Value<string>(),
                WhenJson = when,
                When = Gate(when),
                Gate = GateKey(when),
                Base = r["base"]?.Value<double>() ?? 0.0,
                Push = r["stands_for"]?["situational_push"]?.Value<string>()
            };
            foreach (JObject t in (JArray)r["terms"] ?? new JArray())
            {
                var sc = ScalerOf(t);
                rule.Terms.Add(new Term
                {
                    Key = EvidenceKey(sc), K = Register(sc), Factor = sc.Factor,
                    Part = t["part"]?.Value<string>() ?? "push", Route = t["route"]?.Value<string>()
                });
            }
            return rule;
        }

        static Case ParseCase(JObject c)
        {
            var k = new Case
            {
                Id = c["id"].Value<string>(),
                Family = c["family"].Value<string>(),
                Want = c["want"].Value<string>(),
                Intent = c["intent"].Value<string>(),
                Rival = c["rival"]?.Value<bool>() ?? false
            };
            foreach (JObject r in (JArray)c["rules"]) k.Rules.Add(ParseRule(r, k.Intent));
            foreach (JObject r in (JArray)c["routes"])
            {
                var route = new Route
                {
                    Key = r["key"].Value<string>(),
                    Intent = k.Intent,
                    Direction = r["direction"].Value<string>(),
                    Circ = r["circumstance"].Value<string>(),
                    Copied = r["circumstance_as_copied"]?.Value<string>()
                };
                foreach (JObject p in (JArray)r["situational_pushes"] ?? new JArray())
                    route.Pushes.Add(new KeyValuePair<string, double>(p["feature"].Value<string>(), p["amount"].Value<double>()));
                k.Routes.Add(route);
            }
            foreach (JObject r in (JArray)c["relations"] ?? new JArray())
                k.Relations.Add(new Relation { Kind = r["kind"].Value<string>(), Routes = ((JArray)r["routes"]).Select(x => x.Value<string>()).ToList() });
            if (k.Rival)
            {
                var rv = (JObject)_spec["rival"];
                var rule = ParseRule((JObject)rv["rule"], rv["intent"].Value<string>());
                rule.Route = rv["route"].Value<string>();
                k.Rules.Add(rule);
                k.Routes.Add(new Route { Key = rule.Route, Intent = rule.Intent, Direction = "toward", Circ = rv["circumstance"].Value<string>() });
            }
            k.Index();
            return k;
        }

        static Case Clone(Case c)
        {
            var k = new Case { Id = c.Id, Family = c.Family, Want = c.Want, Intent = c.Intent, Rival = c.Rival };
            foreach (var r in c.Rules)
                k.Rules.Add(new Rule
                {
                    Id = r.Id, Intent = r.Intent, Route = r.Route, When = r.When, WhenJson = r.WhenJson, Gate = r.Gate,
                    Base = r.Base, Push = r.Push, Motives = r.Motives.ToList(),
                    Terms = r.Terms.Select(t => new Term { Key = t.Key, K = t.K, Factor = t.Factor, Part = t.Part, Route = t.Route }).ToList()
                });
            foreach (var r in c.Routes)
                k.Routes.Add(new Route { Key = r.Key, Intent = r.Intent, Direction = r.Direction, Circ = r.Circ, Copied = r.Copied, Pushes = r.Pushes.ToList() });
            foreach (var r in c.Relations) k.Relations.Add(new Relation { Kind = r.Kind, Routes = r.Routes.ToList() });
            foreach (var kv in c.Canon) k.Canon[kv.Key] = kv.Value;
            k.Index();
            return k;
        }

        // ============================================================ evaluation

        sealed class Stmt
        {
            public string Key;
            public int K;
            public double Coef;
            public double Level;
            public double Amount;
            public string Rule;
            public bool IsBase;
        }

        sealed class RouteOut
        {
            public bool Applicable;
            public bool Admitted;
            public double Total;
            public double Contribution;
            public bool Operating;
            public double Final;
            public double Push;
            public List<string> PushRules = new List<string>();
            public List<Stmt> Stmts = new List<Stmt>();
            public List<KeyValuePair<string, double>> Conditions = new List<KeyValuePair<string, double>>();
            public string WhyNot;
        }

        sealed class Out
        {
            public Case Case;
            public Rep Rep;
            public string Token;
            public Dictionary<string, double> Support = new Dictionary<string, double>(StringComparer.Ordinal);
            public RouteOut[] Routes;
            public int Flags, Restated, Conflicts;
            public Dictionary<string, List<double>> RuleAmounts; // S only
            public List<string> WhyNone = new List<string>();

            public double Focal => Case.Intent != null && Support.TryGetValue(Case.Intent, out var v) ? v : 0.0;
            public double FinalOf(string route) => Case.RouteIndex.TryGetValue(route, out var i) ? Routes[i].Final : 0.0;
            public bool Contributes(string route) => Math.Abs(FinalOf(route)) > Eps;

            public string Explain()
            {
                var sb = new StringBuilder();
                sb.Append(Token).Append('|');
                if (Rep == Rep.S)
                {
                    foreach (var i in RuleAmounts.Keys.OrderBy(x => x, StringComparer.Ordinal))
                        sb.Append(i).Append('=').Append(F9(Support[i])).Append('[').Append(string.Join(",", RuleAmounts[i].Select(F9).OrderBy(x => x, StringComparer.Ordinal))).Append(']');
                    return sb.ToString();
                }
                foreach (var intent in Case.Intents.OrderBy(x => x, StringComparer.Ordinal))
                {
                    sb.Append(intent).Append('=').Append(F9(Support.TryGetValue(intent, out var v) ? v : 0.0)).Append('[');
                    var parts = new List<string>();
                    for (var i = 0; i < Case.Routes.Count; i++)
                    {
                        if (Case.Routes[i].Intent != intent) continue;
                        var ro = Routes[i];
                        parts.Add(Case.CanonOf(Case.Routes[i].Key) + (ro.Applicable ? "" : "!") + (ro.Operating || !ro.Applicable ? "" : "~") + "{"
                                  + string.Join(";", ro.Stmts.Select(x => x.Key + "=" + F9(x.Amount)).OrderBy(x => x, StringComparer.Ordinal))
                                  + (ro.Push != 0.0 ? ";push=" + F9(ro.Push) : "")
                                  + (ro.Conditions.Count > 0 ? ";if " + string.Join("&", ro.Conditions.Select(x => x.Key).OrderBy(x => x, StringComparer.Ordinal)) : "")
                                  + "}");
                    }
                    sb.Append(string.Join("+", parts.OrderBy(x => x, StringComparer.Ordinal))).Append(']');
                }
                return sb.ToString();
            }
        }

        static bool Same(double a, double b) => Math.Abs(a - b) <= Eps;

        static Out Shipped(Case c, double[] lv, Percept p)
        {
            var o = new Out { Case = c, Rep = Rep.S, Routes = c.Routes.Select(_ => new RouteOut()).ToArray(), RuleAmounts = new Dictionary<string, List<double>>(StringComparer.Ordinal) };
            var order = new List<string>();
            foreach (var r in c.Rules)
            {
                if (!r.When.Matches(p)) continue;
                var sum = 0.0;
                foreach (var t in r.Terms) sum += lv[t.K] * t.Factor;
                var weight = r.Base + sum;
                if (weight <= 0.0) continue;
                if (!o.Support.ContainsKey(r.Intent)) { o.Support[r.Intent] = 0.0; o.RuleAmounts[r.Intent] = new List<double>(); order.Add(r.Intent); }
                o.Support[r.Intent] += weight;
                o.RuleAmounts[r.Intent].Add(weight);
                var ri = c.RouteIndex[r.Route];
                o.Routes[ri].Final += weight;
                o.Routes[ri].Applicable = true;
                o.Routes[ri].Operating = true;
            }
            var ranked = o.Support.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key, StringComparer.Ordinal).ToList();
            o.Token = ranked.Count == 0 ? "none" : ranked[0].Key;
            if (ranked.Count == 0) o.WhyNone.Add("every compatible rule weighs zero or less, or none is compatible");
            return o;
        }

        static Out Evaluate(Case c, double[] lv, Sit s, Percept p, Rep rep)
        {
            if (rep == Rep.S) return Shipped(c, lv, p);
            var parts = Parts(rep);
            var circ = Circ(rep);
            var rel = Rel(rep);
            var n = c.Routes.Count;
            var o = new Out { Case = c, Rep = rep, Routes = new RouteOut[n] };
            var coefs = new Dictionary<string, Stmt>[n];
            for (var i = 0; i < n; i++)
            {
                o.Routes[i] = new RouteOut();
                coefs[i] = new Dictionary<string, Stmt>(StringComparer.Ordinal);
            }

            void Add(int ri, string key, int k, double coef, double level, string rule, bool isBase)
            {
                if (coefs[ri].TryGetValue(key, out var had))
                {
                    if (Same(had.Coef, coef)) { o.Restated++; return; }
                    o.Conflicts++;
                    if (Math.Abs(coef) <= Math.Abs(had.Coef)) return;
                    had.Coef = coef; had.Level = level; had.Amount = coef * level; had.Rule = rule;
                    return;
                }
                var st = new Stmt { Key = key, K = k, Coef = coef, Level = level, Amount = isBase ? coef : level * coef, Rule = rule, IsBase = isBase };
                coefs[ri][key] = st;
                o.Routes[ri].Stmts.Add(st);
            }

            foreach (var r in c.Rules)
            {
                var ri = c.RouteIndex[r.Route];
                var gate = r.When.Matches(p);
                if (circ && r.Push != null)
                {
                    if (Holds(r.Push, s)) { o.Routes[ri].Push += r.Base; o.Routes[ri].PushRules.Add(r.Id); }
                    continue;
                }
                if (!circ && !gate) continue;
                if (!circ) o.Routes[ri].Admitted = true;
                if (r.Base != 0.0) Add(ri, "base|" + r.Gate, -1, r.Base, 1.0, r.Id, true);
                foreach (var t in r.Terms)
                {
                    var ti = t.Route == null ? ri : c.RouteIndex[t.Route];
                    if (!circ) o.Routes[ti].Admitted = true;
                    var level = lv[t.K];
                    if (parts && t.Part == "condition")
                    {
                        if (!o.Routes[ti].Conditions.Any(x => x.Key == t.Key)) o.Routes[ti].Conditions.Add(new KeyValuePair<string, double>(t.Key, level));
                        if (rep == Rep.BPartsW) Add(ti, t.Key, t.K, t.Factor, level, r.Id, false);
                        continue;
                    }
                    Add(ti, t.Key, t.K, t.Factor, level, r.Id, false);
                }
            }

            // Where each reason applies.
            for (var i = 0; i < n; i++)
            {
                var route = c.Routes[i];
                var ro = o.Routes[i];
                bool ok;
                if (circ)
                {
                    var name = !rel && route.Copied != null ? route.Copied : route.Circ;
                    ro.Admitted = Holds(name, s);
                    ok = ro.Admitted;
                    if (!ok) ro.WhyNot = "circumstance " + name + " does not hold";
                }
                else
                {
                    ok = ro.Admitted;
                    if (!ok) ro.WhyNot = "no rule of it is admitted by its gate";
                }
                if (ok && parts)
                {
                    var failed = ro.Conditions.FirstOrDefault(x => x.Value <= 0.0);
                    if (failed.Key != null) { ok = false; ro.WhyNot = "condition " + failed.Key + " does not hold"; }
                }
                ro.Applicable = ok;
            }
            if (rel)
                foreach (var r in c.Relations.Where(x => x.Kind == "reinforces"))
                {
                    var a = c.RouteIndex[r.Routes[0]];
                    var b = c.RouteIndex[r.Routes[1]];
                    if (o.Routes[a].Applicable && !o.Routes[b].Applicable)
                    {
                        o.Routes[a].Applicable = false;
                        o.Routes[a].WhyNot = "it strengthens " + c.CanonOf(r.Routes[1]) + ", which does not apply";
                    }
                }

            // How much each contributes.
            for (var i = 0; i < n; i++)
            {
                var ro = o.Routes[i];
                ro.Operating = ro.Applicable;
                if (!ro.Applicable) continue;
                var total = 0.0;
                foreach (var st in ro.Stmts) total += st.Amount;
                total += ro.Push;
                ro.Total = total;
                ro.Contribution = !parts ? total : c.Routes[i].Direction == "toward" ? Math.Max(0.0, total) : Math.Min(0.0, total);
            }
            if (rel)
                foreach (var r in c.Relations.Where(x => x.Kind == "alternative"))
                {
                    var live = r.Routes.Select(k => c.RouteIndex[k]).Where(i => o.Routes[i].Applicable).ToList();
                    if (live.Count < 2) continue;
                    var best = live[0];
                    foreach (var i in live.Skip(1))
                        if (o.Routes[i].Contribution > o.Routes[best].Contribution + Eps) best = i;
                    foreach (var i in live)
                        if (i != best) o.Routes[i].Operating = false;
                }
            for (var i = 0; i < n; i++)
            {
                var ro = o.Routes[i];
                ro.Final = ro.Operating ? ro.Contribution : 0.0;
                var intent = c.Routes[i].Intent;
                o.Support[intent] = (o.Support.TryGetValue(intent, out var v) ? v : 0.0) + ro.Final;
            }

            // Two different reasons for one intention, identical in every respect this
            // representation reads: not merged, flagged.
            for (var a = 0; a < n; a++)
                for (var b = a + 1; b < n; b++)
                {
                    if (c.Routes[a].Intent != c.Routes[b].Intent || !o.Routes[a].Applicable || !o.Routes[b].Applicable) continue;
                    if (!SameContent(coefs[a], coefs[b])) continue;
                    if (!o.Routes[a].Conditions.Select(x => x.Key).OrderBy(x => x, StringComparer.Ordinal).SequenceEqual(o.Routes[b].Conditions.Select(x => x.Key).OrderBy(x => x, StringComparer.Ordinal))) continue;
                    if (circ && EffectiveCirc(c.Routes[a], rel) != EffectiveCirc(c.Routes[b], rel)) continue;
                    if (circ && Math.Abs(o.Routes[a].Push - o.Routes[b].Push) > Eps) continue;
                    if (parts && c.Routes[a].Direction != c.Routes[b].Direction) continue;
                    o.Flags++;
                }

            // Which intentions may form.
            var sel = Sel(rep);
            var candidates = new List<string>();
            foreach (var intent in c.Intents)
            {
                var idx = Enumerable.Range(0, n).Where(i => c.Routes[i].Intent == intent).ToList();
                bool ok;
                if (sel == 0) ok = idx.Any(i => o.Routes[i].Admitted);
                else if (sel == 1) ok = idx.Any(i => o.Routes[i].Applicable && c.Routes[i].Direction == "toward");
                else ok = o.Support[intent] > Eps;
                if (ok) candidates.Add(intent);
                else
                    o.WhyNone.Add(intent + ": " + (idx.All(i => !o.Routes[i].Applicable)
                        ? string.Join("; ", idx.Select(i => c.CanonOf(c.Routes[i].Key) + " " + o.Routes[i].WhyNot))
                        : "support " + F(o.Support[intent]) + " is not positive"));
            }
            if (candidates.Count == 0) o.Token = "none";
            else
            {
                var ranked = candidates.OrderByDescending(x => o.Support[x]).ThenBy(x => x, StringComparer.Ordinal).ToList();
                o.Token = ranked.Count > 1 && Math.Abs(o.Support[ranked[0]] - o.Support[ranked[1]]) <= Eps
                    ? "tie:" + ranked[0] + "=" + ranked[1]
                    : ranked[0];
            }
            return o;
        }

        static string EffectiveCirc(Route r, bool rel) => !rel && r.Copied != null ? r.Copied : r.Circ;

        static bool SameContent(Dictionary<string, Stmt> a, Dictionary<string, Stmt> b)
        {
            if (a.Count != b.Count) return false;
            foreach (var kv in a)
                if (!b.TryGetValue(kv.Key, out var x) || !Same(x.Coef, kv.Value.Coef)) return false;
            return true;
        }

        /// <summary>PV1: the outcome can be rebuilt from its explanation alone.</summary>
        static bool Reconstructs(Out o)
        {
            if (o.Token == "none") return o.WhyNone.Count == o.Case.Intents.Count || o.Rep == Rep.S && o.WhyNone.Count > 0;
            var winner = o.Token.StartsWith("tie:", StringComparison.Ordinal) ? o.Token.Substring(4).Split('=')[0] : o.Token;
            if (o.Rep == Rep.S)
            {
                var sum = 0.0;
                foreach (var w in o.RuleAmounts[winner]) sum += w;
                return Same(sum, o.Support[winner]);
            }
            var parts = Parts(o.Rep);
            var rebuilt = 0.0;
            for (var i = 0; i < o.Case.Routes.Count; i++)
            {
                if (o.Case.Routes[i].Intent != winner) continue;
                var ro = o.Routes[i];
                if (!ro.Operating) continue;
                var t = ro.Push;
                foreach (var st in ro.Stmts)
                {
                    if (st.Rule == null) return false;
                    if (!st.IsBase && !Same(st.Amount, st.Coef * st.Level)) return false;
                    t += st.Amount;
                }
                if (ro.Push != 0.0 && ro.PushRules.Count == 0) return false;
                rebuilt += !parts ? t : o.Case.Routes[i].Direction == "toward" ? Math.Max(0.0, t) : Math.Min(0.0, t);
            }
            return Same(rebuilt, o.Support[winner]);
        }

        // ============================================================ cells

        static int Profiles => _minds.Length;
        static int CellsPerCase => Profiles * _sits.Count;

        static IEnumerable<Tuple<int, int>> Cells()
        {
            for (var i = 0; i < Profiles; i++)
                for (var si = 0; si < _sits.Count; si++)
                    yield return Tuple.Create(i, si);
        }

        static Out At(Case c, int i, int si, Rep rep, double[] lv = null)
            => Evaluate(c, lv ?? _lv[i], _sits[si], _percepts[i][si], rep);

        // ============================================================ checks

        sealed class CheckResult
        {
            public bool Passed;
            public int Count;          // violating cells, or for differs_from the cells that differ
            public bool CountsDifference;
        }

        static readonly Dictionary<string, Dictionary<Rep, CheckResult>> _checkResults = new Dictionary<string, Dictionary<Rep, CheckResult>>(StringComparer.Ordinal);
        static readonly Dictionary<string, Dictionary<Rep, bool>> _passedOnlyByCopy = new Dictionary<string, Dictionary<Rep, bool>>(StringComparer.Ordinal);

        static double Strength(Case c, string route, double[] lv)
        {
            var t = 0.0;
            foreach (var r in c.Rules.Where(r => r.Route == route && r.Push == null))
            {
                t += r.Base;
                foreach (var x in r.Terms) t += x.Factor * lv[x.K];
            }
            return t;
        }

        static Case Solo(Case c, string keep)
        {
            var k = Clone(c);
            k.Rules = k.Rules.Where(r => r.Route == keep || r.Intent != c.Intent).ToList();
            k.Relations.Clear();
            k.Index();
            return k;
        }

        static Case CopyFree(Case c)
        {
            var k = Clone(c);
            foreach (var r in k.Routes)
            {
                if (r.Copied == null) continue;
                r.Copied = null;
                foreach (var rule in k.Rules.Where(x => x.Route == r.Key))
                {
                    rule.WhenJson = new JObject();
                    rule.When = Gate(rule.WhenJson);
                    rule.Gate = GateKey(rule.WhenJson);
                }
            }
            k.Index();
            return k;
        }

        static CheckResult RunCheck(JObject ch, Rep rep, Func<string, Case> caseOf)
        {
            var kind = ch["kind"].Value<string>();
            var res = new CheckResult();
            var bad = 0;
            Case c = ch["case"] != null ? caseOf(ch["case"].Value<string>()) : null;
            Case refCase = ch["reference"] != null ? caseOf(ch["reference"].Value<string>()) : null;
            switch (kind)
            {
                case "same_as":
                    foreach (var x in Cells())
                    {
                        var a = At(c, x.Item1, x.Item2, rep);
                        var b = At(refCase, x.Item1, x.Item2, rep);
                        if (a.Token != b.Token || !Same(a.Focal, b.Focal) || a.Explain() != b.Explain()) bad++;
                    }
                    break;
                case "differs_from":
                    res.CountsDifference = true;
                    foreach (var x in Cells())
                        if (!Same(At(c, x.Item1, x.Item2, rep).Focal, At(refCase, x.Item1, x.Item2, rep).Focal)) res.Count++;
                    res.Passed = res.Count > 0;
                    return res;
                case "flag_identical":
                {
                    var r1 = ((JArray)ch["routes"])[0].Value<string>();
                    var r2 = ((JArray)ch["routes"])[1].Value<string>();
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        var both = rep == Rep.S || o.Routes[c.RouteIndex[r1]].Applicable && o.Routes[c.RouteIndex[r2]].Applicable;
                        if (both && o.Flags == 0) bad++;
                    }
                    break;
                }
                case "applies_exactly":
                {
                    var route = ch["route"].Value<string>();
                    var circName = ch["circumstance"].Value<string>();
                    foreach (var x in Cells())
                        if (At(c, x.Item1, x.Item2, rep).Contributes(route) != Holds(circName, _sits[x.Item2])) bad++;
                    break;
                }
                case "evidence":
                case "condition":
                {
                    var route = ch["route"].Value<string>();
                    var fact = ch["fact"].Value<string>();
                    var k = _keyIndex[fact];
                    var coef = c.Rules.SelectMany(r => r.Terms).First(t => t.Key == fact).Factor;
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        var level = _lv[x.Item1][k];
                        bool applies;
                        double attributed;
                        if (rep == Rep.S)
                        {
                            applies = o.Contributes(route);
                            attributed = applies ? coef * level : 0.0;
                        }
                        else
                        {
                            var ro = o.Routes[c.RouteIndex[route]];
                            applies = ro.Applicable && Math.Abs(ro.Final) > Eps;
                            attributed = ro.Stmts.Where(st => st.Key == fact).Sum(st => st.Amount);
                        }
                        bool ok;
                        if (kind == "evidence") ok = applies && Same(attributed, coef * level);
                        else ok = level <= 0.0 ? !applies : applies && Math.Abs(attributed) <= Eps;
                        if (!ok) bad++;
                    }
                    break;
                }
                case "not_a_strength":
                {
                    var reference = caseOf(ch["reference"].Value<string>());
                    var refRoute = ch["reference_route"].Value<string>();
                    foreach (var id in ((JArray)ch["cases"]).Select(v => v.Value<string>()))
                    {
                        var cc = caseOf(id);
                        var route = cc.Routes[0].Key;
                        foreach (var x in Cells())
                        {
                            var o = At(cc, x.Item1, x.Item2, rep);
                            if (!o.Contributes(route)) continue;
                            if (!Same(o.FinalOf(route), At(reference, x.Item1, x.Item2, rep).FinalOf(refRoute))) bad++;
                        }
                    }
                    break;
                }
                case "situational_push":
                {
                    var route = ch["route"].Value<string>();
                    var feature = ch["feature"].Value<string>();
                    var amount = ch["amount"].Value<double>();
                    var refRoute = ch["reference_route"].Value<string>();
                    foreach (var x in Cells())
                    {
                        var want = At(refCase, x.Item1, x.Item2, rep).FinalOf(refRoute) + (Holds(feature, _sits[x.Item2]) ? amount : 0.0);
                        if (!Same(At(c, x.Item1, x.Item2, rep).FinalOf(route), want)) bad++;
                    }
                    break;
                }
                case "co_active":
                {
                    var r1 = ((JArray)ch["routes"])[0].Value<string>();
                    var r2 = ((JArray)ch["routes"])[1].Value<string>();
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        var a = o.FinalOf(r1);
                        var b = o.FinalOf(r2);
                        if (!(a > Eps && b > Eps && o.Focal > Math.Max(a, b) + Eps)) bad++;
                    }
                    break;
                }
                case "alternative":
                {
                    var r1 = ((JArray)ch["routes"])[0].Value<string>();
                    var r2 = ((JArray)ch["routes"])[1].Value<string>();
                    var s1 = Solo(c, r1);
                    var s2 = Solo(c, r2);
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        var alone = Math.Max(At(s1, x.Item1, x.Item2, rep).Focal, At(s2, x.Item1, x.Item2, rep).Focal);
                        var operating = rep == Rep.S ? 2 : new[] { r1, r2 }.Count(k => o.Routes[c.RouteIndex[k]].Applicable && o.Routes[c.RouteIndex[k]].Operating);
                        if (o.Focal > alone + Eps || operating != 1) bad++;
                    }
                    break;
                }
                case "exclusive":
                {
                    var r1 = ((JArray)ch["routes"])[0].Value<string>();
                    var r2 = ((JArray)ch["routes"])[1].Value<string>();
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        if (o.Contributes(r1) && o.Contributes(r2)) bad++;
                    }
                    break;
                }
                case "reinforces":
                {
                    var route = ch["route"].Value<string>();
                    var of = c.Routes.First(r => r.Key == ch["of"].Value<string>());
                    foreach (var x in Cells())
                    {
                        var want = Holds(of.Circ, _sits[x.Item2]) && Strength(c, route, _lv[x.Item1]) > Eps;
                        if (At(c, x.Item1, x.Item2, rep).Contributes(route) != want) bad++;
                    }
                    break;
                }
                case "against":
                {
                    var toward = c.Routes.Where(r => r.Intent == c.Intent && r.Direction == "toward").Select(r => r.Key).ToList();
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        var sum = toward.Sum(k => Math.Max(0.0, o.FinalOf(k)));
                        if (!(o.Focal < sum - Eps)) bad++;
                    }
                    break;
                }
                case "hold_back_local":
                {
                    var route = ch["route"].Value<string>();
                    var other = ch["other"].Value<string>();
                    foreach (var x in Cells())
                    {
                        var o = At(c, x.Item1, x.Item2, rep);
                        if (o.Focal < Strength(c, other, _lv[x.Item1]) - Eps || o.FinalOf(route) < -Eps) bad++;
                    }
                    break;
                }
                case "forms_iff":
                {
                    var w = (JObject)ch["when"];
                    foreach (var x in Cells())
                    {
                        var lv = _lv[x.Item1];
                        bool want;
                        if (w["held"] != null) want = lv[_keyIndex[w["held"].Value<string>()]] > 0.0;
                        else if (w["circumstance"] != null) want = Holds(w["circumstance"].Value<string>(), _sits[x.Item2]);
                        else if (w["positive"] != null)
                            want = w["positive"]["const"].Value<double>()
                                   + ((JObject)w["positive"]["terms"]).Properties().Sum(pr => pr.Value.Value<double>() * lv[_keyIndex[pr.Name]]) > Eps;
                        else want = true;
                        if ((At(c, x.Item1, x.Item2, rep).Token == c.Intent) != want) bad++;
                    }
                    break;
                }
                case "same_outcome":
                    foreach (var x in Cells())
                        if (At(c, x.Item1, x.Item2, rep).Token != At(refCase, x.Item1, x.Item2, rep).Token) bad++;
                    break;
                default:
                    throw new InvalidOperationException("unknown check " + kind);
            }
            res.Count = bad;
            res.Passed = bad == 0;
            return res;
        }

        static void EnsureChecks()
        {
            if (_checkResults.Count > 0) return;
            foreach (var ch in _checks)
            {
                var id = ch["id"].Value<string>();
                _checkResults[id] = new Dictionary<Rep, CheckResult>();
                foreach (var rep in Main.Concat(Ablations))
                {
                    if (Ablations.Contains(rep) && ch["family"].Value<string>() != "F") continue;
                    _checkResults[id][rep] = RunCheck(ch, rep, k => _byId[k]);
                }
                // (iv): would it still pass with every copied declaration removed?
                var caseIds = ch["case"] != null ? new[] { ch["case"].Value<string>() } : new string[0];
                if (!caseIds.Any(k => _byId[k].Routes.Any(r => r.Copied != null))) continue;
                _passedOnlyByCopy[id] = new Dictionary<Rep, bool>();
                foreach (var rep in Main)
                {
                    if (!_checkResults[id][rep].Passed) continue;
                    var free = RunCheck(ch, rep, k => CopyFree(_byId[k]));
                    _passedOnlyByCopy[id][rep] = !free.Passed;
                }
            }
        }

        // ============================================================ 0

        static int _formMismatch, _formWeightMismatch, _formCells;

        [Test, Order(0), Timeout(7200000)]
        public void TheFilesTheControlAndTheVocabulary()
        {
            var sb = new StringBuilder();
            sb.AppendLine("## 0. What is frozen, and whether S is the shipped selector");
            sb.AppendLine();
            sb.AppendLine("| File | sha256 at the start of this run | Expected | Match |");
            sb.AppendLine("|---|---|---|---|");
            foreach (var f in new[] { Tuple.Create(_frozenPath, FrozenSha), Tuple.Create(_routesPath, RoutesSha), Tuple.Create(_sweepPath, SweepSha), Tuple.Create(_casesPath, CasesSha) })
            {
                var sha = Sha(f.Item1);
                sb.AppendLine("| `" + Path.GetFileName(f.Item1) + "` | `" + sha + "` | `" + f.Item2 + "` | " + (sha == f.Item2 ? "**yes**" : "**NO**") + " |");
                Assert.AreEqual(f.Item2, sha, Path.GetFileName(f.Item1));
            }
            sb.AppendLine();

            // S, rebuilt from the authored rules, against IntentionSelector.Form itself.
            foreach (var c in _cases)
            {
                var candidates = c.Rules.Select(r => new Candidate
                {
                    Id = r.Id, Motives = new List<string> { c.Want }, Intent = r.Intent, When = r.When, Base = r.Base,
                    ScaledBy = r.Terms.Select(t => new Scaler
                    {
                        Kind = _keyScaler[t.K].Kind, Name = _keyScaler[t.K].Name, Predicate = _keyScaler[t.K].Predicate,
                        Args = _keyScaler[t.K].Args, Target = _keyScaler[t.K].Target, Factor = t.Factor
                    }).ToList()
                }).ToList();
                foreach (var x in Cells())
                {
                    _formCells++;
                    var form = IntentionSelector.Form(candidates, _minds[x.Item1], _percepts[x.Item1][x.Item2], Want(c.Want), _content.Morning.Day, _content.Rules.Deciding.RecallHalfLife);
                    var s = At(c, x.Item1, x.Item2, Rep.S);
                    var formToken = form.Intent ?? "none";
                    if (formToken != s.Token) _formMismatch++;
                    else if (form.Intent != null && form.Weight != s.Support[form.Intent]) _formWeightMismatch++;
                }
            }
            sb.AppendLine("S, rebuilt from the authored rules, differs from `IntentionSelector.Form` in **" + N(_formMismatch) + "** of " + N(_formCells)
                          + " cells (" + _cases.Count + " cases x " + N(CellsPerCase) + "); winning weights not equal to the bit: **" + N(_formWeightMismatch) + "**.");
            sb.AppendLine();
            sb.AppendLine("### The evaluation space");
            sb.AppendLine();
            sb.AppendLine("| | |");
            sb.AppendLine("|---|---|");
            sb.AppendLine("| Profiles | " + N(Profiles) + " (the sweep: " + _sweepTraits.Count + " traits at " + string.Join(", ", _traitLevels.Select(F)) + "; values by rank; " + _beliefSets.Count + " belief sets) |");
            sb.AppendLine("| Situations | " + string.Join("; ", _sits.Select(x => x.Id + " " + x.Label)) + " |");
            sb.AppendLine("| Cells per case | " + N(CellsPerCase) + " |");
            sb.AppendLine("| Cases | " + _cases.Count + " in six families: " + string.Join(", ", _cases.GroupBy(x => x.Family).Select(g => g.Key + " " + g.Count())) + " |");
            sb.AppendLine("| Checks | " + _checks.Count + ", and " + ((JArray)_spec["negative_controls"]).Count + " negative controls |");
            sb.AppendLine();
            sb.AppendLine("### What each representation reads");
            sb.AppendLine();
            sb.AppendLine("| | Reason identity | Parts and direction | Declared circumstances | Relations | Forms when |");
            sb.AppendLine("|---|---|---|---|---|---|");
            sb.AppendLine("| **S** | no | no | shipped gates | no | a rule weighs more than zero |");
            sb.AppendLine("| **A** | yes | no | shipped gates | no | any compatible candidate |");
            sb.AppendLine("| **B-parts** | yes | yes | shipped gates | no | support > 0 |");
            sb.AppendLine("| **B-circ** | yes | no | yes | no | support > 0 |");
            sb.AppendLine("| **B** | yes | yes | yes | no | support > 0 |");
            sb.AppendLine("| **C** | yes | yes | yes | yes | support > 0 |");
            Record("0", sb.ToString());
            Assert.AreEqual(0, _formMismatch, "S is the selector");
            Assert.AreEqual(0, _formWeightMismatch, "S's weights are the selector's");
        }

        // ============================================================ 1

        [Test, Order(1), Timeout(7200000)]
        public void A_TheChecks()
        {
            EnsureChecks();
            var sb = new StringBuilder();
            sb.AppendLine("## 1. Representational results: the checks");
            sb.AppendLine();
            sb.AppendLine("Cells, of " + N(CellsPerCase) + " per case, that violate each check. **0 is a pass.** For B.1, C.5 and C.6 the count is of cells where the two cases differ, and **0 is a failure**.");
            sb.AppendLine();
            sb.AppendLine("| Check | What must hold | " + string.Join(" | ", Main.Select(Name)) + " |");
            sb.AppendLine("|---|---|" + string.Join("|", Main.Select(_ => "---")) + "|");
            foreach (var ch in _checks)
            {
                var id = ch["id"].Value<string>();
                sb.AppendLine("| " + id + " | " + ch["text"].Value<string>() + " | " + string.Join(" | ", Main.Select(r => Cell(_checkResults[id][r]))) + " |");
            }
            sb.AppendLine();

            sb.AppendLine("### Checks passed, by family");
            sb.AppendLine();
            sb.AppendLine("| Family | Checks | " + string.Join(" | ", Main.Select(Name)) + " |");
            sb.AppendLine("|---|---|" + string.Join("|", Main.Select(_ => "---")) + "|");
            var families = _checks.Select(c => c["family"].Value<string>()).Distinct().ToList();
            var totals = Main.ToDictionary(r => r, r => 0);
            foreach (var f in families)
            {
                var ids = _checks.Where(c => c["family"].Value<string>() == f).Select(c => c["id"].Value<string>()).ToList();
                var cells = new List<string>();
                foreach (var r in Main)
                {
                    var p = ids.Count(i => _checkResults[i][r].Passed);
                    totals[r] += p;
                    cells.Add(p + " (" + Pc(p, ids.Count) + ")");
                }
                sb.AppendLine("| " + FamilyName(f) + " | " + ids.Count + " | " + string.Join(" | ", cells) + " |");
            }
            sb.AppendLine("| **All** | **" + _checks.Count + "** | " + string.Join(" | ", Main.Select(r => "**" + totals[r] + " (" + Pc(totals[r], _checks.Count) + ")**")) + " |");
            sb.AppendLine();
            var pct = Main.ToDictionary(r => r, r => 100.0 * totals[r] / _checks.Count);
            sb.AppendLine("Percentage points against S: " + string.Join(", ", Main.Skip(1).Select(r => Name(r) + " " + Pp(pct[r], pct[Rep.S]))) + ". Against A: "
                          + string.Join(", ", Main.Skip(2).Select(r => Name(r) + " " + Pp(pct[r], pct[Rep.A]))) + ".");
            sb.AppendLine();

            sb.AppendLine("### The viability ablations, family F");
            sb.AppendLine();
            sb.AppendLine("| Check | " + string.Join(" | ", Ablations.Select(Name)) + " | B (Sel-2) |");
            sb.AppendLine("|---|" + string.Join("|", Ablations.Select(_ => "---")) + "|---|");
            foreach (var ch in _checks.Where(c => c["family"].Value<string>() == "F"))
            {
                var id = ch["id"].Value<string>();
                sb.AppendLine("| " + id + " " + ch["text"].Value<string>() + " | " + string.Join(" | ", Ablations.Select(r => Cell(_checkResults[id][r]))) + " | " + Cell(_checkResults[id][Rep.B]) + " |");
            }
            sb.AppendLine();

            sb.AppendLine("### Checks passed only through a copied declaration");
            sb.AppendLine();
            sb.AppendLine("Each check whose case contains a copied gate or circumstance was rerun with every copy removed (the reinforcing reason given no gate of its own). A representation that passes with the copy and fails without it passed only through the copy.");
            sb.AppendLine();
            sb.AppendLine("| Check | " + string.Join(" | ", Main.Select(Name)) + " |");
            sb.AppendLine("|---|" + string.Join("|", Main.Select(_ => "---")) + "|");
            foreach (var kv in _passedOnlyByCopy)
                sb.AppendLine("| " + kv.Key + " | " + string.Join(" | ", Main.Select(r => !kv.Value.ContainsKey(r) ? "(fails)" : kv.Value[r] ? "**only through the copy**" : "without the copy")) + " |");
            sb.AppendLine();

            // Behaviour on the synthetic cases: choices that differ from C's.
            sb.AppendLine("### Behaviour: choices that differ from C's");
            sb.AppendLine();
            sb.AppendLine("Cells, of " + N(CellsPerCase) + ", where the representation chooses a different outcome from C, which computes every declaration by construction. Every case but family F has the rival. In brackets, the share of cells.");
            sb.AppendLine();
            sb.AppendLine("| Case | " + string.Join(" | ", Main.Where(r => r != Rep.C).Select(Name)) + " |");
            sb.AppendLine("|---|" + string.Join("|", Main.Where(r => r != Rep.C).Select(_ => "---")) + "|");
            var totalChanged = Main.ToDictionary(r => r, r => 0);
            foreach (var c in _cases)
            {
                var counts = Main.Where(r => r != Rep.C).ToDictionary(r => r, r => 0);
                foreach (var x in Cells())
                {
                    var reference = At(c, x.Item1, x.Item2, Rep.C).Token;
                    foreach (var r in counts.Keys.ToList())
                        if (At(c, x.Item1, x.Item2, r).Token != reference) counts[r]++;
                }
                foreach (var kv in counts) totalChanged[kv.Key] += kv.Value;
                sb.AppendLine("| " + c.Id + " | " + string.Join(" | ", counts.Select(kv => kv.Value == 0 ? "0" : N(kv.Value) + " (" + Pc(kv.Value, CellsPerCase) + ")")) + " |");
            }
            sb.AppendLine("| **All " + _cases.Count + " cases** | " + string.Join(" | ", Main.Where(r => r != Rep.C).Select(r => "**" + N(totalChanged[r]) + " (" + Pc(totalChanged[r], CellsPerCase * _cases.Count) + ")**")) + " |");
            Record("1", sb.ToString());

            foreach (var ch in _checks)
                Assert.IsTrue(_checkResults[ch["id"].Value<string>()][Rep.C].Passed, "C computes every declaration: " + ch["id"]);
        }

        static string Cell(CheckResult r)
            => r.CountsDifference
                ? (r.Passed ? "pass (" + N(r.Count) + " differ)" : "**fail** (0 differ)")
                : (r.Passed ? "pass" : "**fail** (" + N(r.Count) + ")");

        static string FamilyName(string f)
        {
            switch (f)
            {
                case "A": return "A restatement";
                case "B": return "B shared facts, different reasons";
                case "C": return "C evidence or condition";
                case "D": return "D circumstance";
                case "E": return "E relation";
                case "F": return "F no viable cause";
                default: return f;
            }
        }

        // ============================================================ 2

        static readonly Dictionary<string, Dictionary<Rep, int>> _controlChanges = new Dictionary<string, Dictionary<Rep, int>>(StringComparer.Ordinal);
        static readonly Dictionary<string, int> _controlCells = new Dictionary<string, int>(StringComparer.Ordinal);

        static Case Renamed(Case c, bool rules, bool routes)
        {
            var k = Clone(c);
            if (rules)
                for (var i = 0; i < k.Rules.Count; i++) k.Rules[i].Id = "r" + (i + 1).ToString("00");
            if (routes)
            {
                var map = k.Routes.Select((r, i) => new { r.Key, New = "k" + (i + 1).ToString("00") }).ToDictionary(x => x.Key, x => x.New, StringComparer.Ordinal);
                foreach (var r in k.Rules)
                {
                    r.Route = map[r.Route];
                    foreach (var t in r.Terms) if (t.Route != null) t.Route = map[t.Route];
                }
                foreach (var rel in k.Relations) rel.Routes = rel.Routes.Select(x => map[x]).ToList();
                var canon = new Dictionary<string, string>(StringComparer.Ordinal);
                foreach (var r in k.Routes)
                {
                    canon[map[r.Key]] = c.CanonOf(r.Key);
                    r.Key = map[r.Key];
                }
                k.Canon = canon;
            }
            k.Index();
            return k;
        }

        static Case Reversed(Case c)
        {
            var k = Clone(c);
            k.Rules.Reverse();
            k.Index();
            return k;
        }

        static Case TextRewritten(Case c)
        {
            var json = (JObject)((JArray)_spec["cases"]).First(x => x["id"].Value<string>() == c.Id).DeepClone();
            foreach (var t in json.Descendants().OfType<JProperty>().Where(p => p.Name == "note" || p.Name == "meaning").ToList())
                t.Value = new JValue("Rewritten: " + new string(t.Value.Value<string>().Reverse().ToArray()));
            return ParseCase(json);
        }

        static bool Reads(Case c, Func<string, bool> feature)
            => c.Routes.Any(r => r.Circ != null && _circs[r.Circ].Any(f => feature(f.Key)) || r.Copied != null && _circs[r.Copied].Any(f => feature(f.Key)))
               || c.Rules.Any(r => r.Push != null && _circs[r.Push].Any(f => feature(f.Key)));

        [Test, Order(2), Timeout(7200000)]
        public void B_TheNegativeControls()
        {
            var controls = ((JArray)_spec["negative_controls"]).Cast<JObject>().ToList();
            var impulsive = _keyIndex["trait:impulsive"];
            var beliefKeys = _beliefSets.SelectMany(x => x).Select(b => new { Key = "belief:" + b.Predicate + "(" + string.Join(",", b.Args) + ")", b.Confidence })
                .GroupBy(x => x.Key).Select(g => g.First()).ToList();
            foreach (var g in controls)
            {
                var id = g["id"].Value<string>();
                _controlChanges[id] = Main.ToDictionary(r => r, r => 0);
                _controlCells[id] = 0;
            }

            foreach (var c in _cases)
            {
                var variants = new Dictionary<string, Case>
                {
                    ["G.2"] = TextRewritten(c),
                    ["G.3"] = Reversed(c),
                    ["G.4"] = Renamed(c, true, false),
                    ["G.5"] = Renamed(c, false, true)
                };
                var readsWatched = Reads(c, f => f == "watched");
                var readsTarget = Reads(c, f => f == "target_present");
                var unreadBeliefs = beliefKeys.Where(b => !c.Rules.SelectMany(r => r.Terms).Any(t => t.Key == b.Key)).ToList();

                foreach (var x in Cells())
                {
                    var i = x.Item1;
                    var si = x.Item2;
                    foreach (var rep in Main)
                    {
                        var baseOut = At(c, i, si, rep);
                        var baseExplain = baseOut.Explain();
                        void Compare(string control, Out other)
                        {
                            if (other.Token != baseOut.Token || !Same(other.Focal, baseOut.Focal) || other.Explain() != baseExplain)
                                _controlChanges[control][rep]++;
                        }

                        // G.1: an unread trait moved to the next level.
                        var moved = (double[])_lv[i].Clone();
                        var at = _traitLevels.IndexOf(moved[impulsive]);
                        moved[impulsive] = _traitLevels[(at + 1) % _traitLevels.Count];
                        Compare("G.1", At(c, i, si, rep, moved));
                        foreach (var kv in variants) Compare(kv.Key, At(kv.Value, i, si, rep));

                        // G.6: an unread situation feature toggled.
                        if (!readsWatched && _sits[si].Others)
                        {
                            var twin = _sits.FindIndex(y => y.Others && y.Target == _sits[si].Target && y.Watched != _sits[si].Watched);
                            Compare("G.6", At(c, i, twin, rep));
                        }
                        if (!readsTarget && _sits[si].Others)
                        {
                            var twin = _sits.FindIndex(y => y.Others && y.Watched == _sits[si].Watched && y.Target != _sits[si].Target);
                            Compare("G.6", At(c, i, twin, rep));
                        }

                        // G.7: every unread belief added at full confidence.
                        if (unreadBeliefs.Count > 0)
                        {
                            var believed = (double[])_lv[i].Clone();
                            foreach (var b in unreadBeliefs) believed[_keyIndex[b.Key]] = b.Confidence;
                            Compare("G.7", At(c, i, si, rep, believed));
                        }
                    }
                    _controlCells["G.1"]++;
                    foreach (var kv in variants) _controlCells[kv.Key]++;
                    if (!readsWatched && _sits[si].Others) _controlCells["G.6"]++;
                    if (!readsTarget && _sits[si].Others) _controlCells["G.6"]++;
                    if (unreadBeliefs.Count > 0) _controlCells["G.7"]++;
                }
            }

            var sb = new StringBuilder();
            sb.AppendLine("## 2. Negative controls");
            sb.AppendLine();
            sb.AppendLine("Every case, under every representation. A change is any difference in the outcome, the focal intention's support or the representation's explanation, after undoing a declared renaming.");
            sb.AppendLine();
            sb.AppendLine("| Control | What changed | Cells compared, per representation | " + string.Join(" | ", Main.Select(Name)) + " |");
            sb.AppendLine("|---|---|---|" + string.Join("|", Main.Select(_ => "---")) + "|");
            foreach (var g in controls)
            {
                var id = g["id"].Value<string>();
                sb.AppendLine("| " + id + " | " + g["text"].Value<string>() + " | " + N(_controlCells[id]) + " | " + string.Join(" | ", Main.Select(r => _controlChanges[id][r] == 0 ? "0" : "**" + N(_controlChanges[id][r]) + "**")) + " |");
            }
            Record("2", sb.ToString());
            foreach (var kv in _controlChanges)
                foreach (var r in Main)
                    Assert.AreEqual(0, kv.Value[r], kv.Key + " under " + Name(r));
        }

        // ============================================================ 3

        static readonly Dictionary<Rep, int> _pvChecked = new Dictionary<Rep, int>();
        static readonly Dictionary<Rep, int> _pvFailed = new Dictionary<Rep, int>();

        [Test, Order(3), Timeout(7200000)]
        public void C_Provenance()
        {
            foreach (var r in Main.Concat(Ablations)) { _pvChecked[r] = 0; _pvFailed[r] = 0; }
            var exampleNone = new List<string>();
            foreach (var c in _cases)
                foreach (var x in Cells())
                    foreach (var r in Main.Concat(Ablations))
                    {
                        var o = At(c, x.Item1, x.Item2, r);
                        _pvChecked[r]++;
                        if (!Reconstructs(o)) _pvFailed[r]++;
                        if (r == Rep.B && o.Token == "none" && exampleNone.Count < 4 && !exampleNone.Any(e => e.StartsWith(c.Id + " ", StringComparison.Ordinal)))
                            exampleNone.Add(c.Id + " " + _sits[x.Item2].Id + ": " + string.Join("; ", o.WhyNone));
                    }

            var sb = new StringBuilder();
            sb.AppendLine("## 3. Provenance");
            sb.AppendLine();
            sb.AppendLine("**PV1, reconstruction**: from its explanation alone, the winner's support is rebuilt within 1e-9, each amount is coefficient x level of a named fact from a named rule, and a \"none\" names, for every candidate, why it did not form.");
            sb.AppendLine();
            sb.AppendLine("| | " + string.Join(" | ", Main.Concat(Ablations).Select(Name)) + " |");
            sb.AppendLine("|---|" + string.Join("|", Main.Concat(Ablations).Select(_ => "---")) + "|");
            sb.AppendLine("| Outcomes checked | " + string.Join(" | ", Main.Concat(Ablations).Select(r => N(_pvChecked[r]))) + " |");
            sb.AppendLine("| Not reconstructed | " + string.Join(" | ", Main.Concat(Ablations).Select(r => N(_pvFailed[r]))) + " |");
            sb.AppendLine();
            sb.AppendLine("**PV2, the whole chain** (intention, reason, part, fact, circumstance, level, rule): what each representation's explanation emits, against what it holds. *Corrected after the run*: the version of this table written before any run claimed that B and C meet PV2. An audit of the explanation objects this fixture builds showed that they do not emit parts, directions or satisfied circumstances (see `results.md`). No computed number changed.");
            sb.AppendLine();
            sb.AppendLine("| Element of the chain | S | A | B-parts | B-circ | B | C |");
            sb.AppendLine("|---|---|---|---|---|---|---|");
            sb.AppendLine("| The reason | no | yes | yes | yes | yes | yes |");
            sb.AppendLine("| Each fact with its level, coefficient, amount and rule | rule weights only | yes | yes | yes | yes | yes |");
            sb.AppendLine("| A condition, named as a condition | no | no (read as a weight) | yes | no (read as a weight) | yes | yes |");
            sb.AppendLine("| For a reason that did not apply, what failed | no | its gate | its condition or gate | its circumstance | its condition or circumstance | its condition, circumstance or reinforced reason |");
            sb.AppendLine("| Each fact's part (push or hold-back) | not held | not held | held, not emitted (sign only) | not held | held, not emitted | held, not emitted |");
            sb.AppendLine("| A reason's direction | not held | not held | held, not emitted | not held | held, not emitted | held, not emitted |");
            sb.AppendLine("| The circumstance under which an applicable reason applied | not held | not held | not held | held, not emitted | held, not emitted | held, not emitted |");
            sb.AppendLine("| Which alternative operated | - | - | - | - | - | yes |");
            sb.AppendLine("| **PV2 as implemented** | **not met** | **not met** | **not met** | **not met** | **not met** | **not met** |");
            sb.AppendLine();
            sb.AppendLine("Explanations of a \"none\" under B, one per case:");
            sb.AppendLine();
            foreach (var e in exampleNone) sb.AppendLine("- " + e);
            Record("3", sb.ToString());
            foreach (var r in Main.Concat(Ablations)) Assert.AreEqual(0, _pvFailed[r], "PV1 under " + Name(r));
        }

        // ============================================================ 4

        sealed class FrozenSet
        {
            public List<Rule> Rules = new List<Rule>();
        }

        static FrozenSet _frozenSet;

        static void EnsureFrozen()
        {
            if (_frozenSet != null) return;
            _frozenSet = new FrozenSet();
            var decl = JObject.Parse(File.ReadAllText(_routesPath));
            var routeOf = ((JArray)decl["frozen"]["routes"]).ToDictionary(r => r["rule"].Value<string>(), r => (JObject)r, StringComparer.Ordinal);
            var roleToPart = ((JObject)_spec["frozen_reading"]["role_to_part"]).Properties().ToDictionary(p => p.Name, p => p.Value.Value<string>(), StringComparer.Ordinal);
            var raw = JObject.Parse(File.ReadAllText(_frozenPath));
            foreach (JObject c in (JArray)raw["candidates"])
            {
                var id = c["id"].Value<string>();
                var d = routeOf[id];
                var roles = (d["roles"] as JObject)?.Properties().ToDictionary(p => p.Name, p => p.Value.Value<string>(), StringComparer.Ordinal)
                            ?? new Dictionary<string, string>(StringComparer.Ordinal);
                var when = c["when"] as JObject ?? new JObject();
                var rule = new Rule
                {
                    Id = id, Intent = c["intent"].Value<string>(), Route = d["route"].Value<string>(),
                    WhenJson = when, When = Gate(when), Gate = GateKey(when), Base = c["base"]?.Value<double>() ?? 0.0,
                    Motives = ((JArray)c["motives"]).Select(x => x.Value<string>()).ToList()
                };
                foreach (JObject t in (JArray)c["scaled_by"] ?? new JArray())
                {
                    var sc = ScalerOf(t);
                    var key = EvidenceKey(sc);
                    var role = roles.TryGetValue(key, out var rr) ? rr : sc.Factor < 0 ? "inhibitor" : "driver";
                    rule.Terms.Add(new Term { Key = key, K = Register(sc), Factor = sc.Factor, Part = roleToPart[role] });
                }
                _frozenSet.Rules.Add(rule);
            }
        }

        static readonly Dictionary<string, Case> _frozenCases = new Dictionary<string, Case>(StringComparer.Ordinal);

        static Case FrozenCase(string want)
        {
            if (_frozenCases.TryGetValue(want, out var k)) return k;
            k = new Case { Id = "frozen:" + want, Family = "frozen", Want = want, Intent = null };
            foreach (var r in _frozenSet.Rules.Where(r => r.Motives.Contains(want, StringComparer.Ordinal)))
            {
                k.Rules.Add(r);
                var circName = r.WhenJson.Properties().Any() ? (r.When.Alone == true ? "nobody" : r.When.OthersPresentMin.HasValue ? "company" : null) : "anyone";
                if (circName == null) throw new InvalidOperationException(r.Id + ": a gate this experiment cannot read as a circumstance");
                k.Routes.Add(new Route { Key = r.Route, Intent = r.Intent, Direction = "toward", Circ = circName });
            }
            k.Index();
            _frozenCases[want] = k;
            return k;
        }

        static readonly Rep[] FrozenReps = { Rep.S, Rep.A, Rep.BParts, Rep.BCirc, Rep.B, Rep.C, Rep.BPartsW, Rep.ASel2, Rep.BSel0, Rep.BSel1 };

        [Test, Order(4), Timeout(7200000)]
        public void D_TheFrozenFile()
        {
            EnsureFrozen();
            var candidates = IntentionSelector.Load(_frozenPath);
            var company = 2;
            var alone = 0;
            var tokens = FrozenReps.ToDictionary(r => r, r => new List<string>());
            var groups = new List<string>();
            var believer = new List<bool>();
            var formMismatch = 0;
            var formWeight = 0;
            var answerable = _keyIndex["belief:answerable_for($self,missing_can)"];
            for (var i = 0; i < Profiles; i++)
                foreach (var w in Wants)
                    foreach (var si in new[] { company, alone })
                    {
                        var c = FrozenCase(w);
                        groups.Add("`" + w + "` " + (si == company ? "in company" : "alone"));
                        believer.Add(_lv[i][answerable] > 0.0);
                        foreach (var r in FrozenReps) tokens[r].Add(At(c, i, si, r).Token);
                        var form = IntentionSelector.Form(candidates, _minds[i], _percepts[i][si], Want(w), _content.Morning.Day, _content.Rules.Deciding.RecallHalfLife);
                        var s = At(c, i, si, Rep.S);
                        if ((form.Intent ?? "none") != s.Token) formMismatch++;
                        else if (form.Intent != null && form.Weight != s.Support[form.Intent]) formWeight++;
                    }
            var n = groups.Count;

            var sb = new StringBuilder();
            sb.AppendLine("## 4. Behaviour on the frozen file");
            sb.AppendLine();
            sb.AppendLine("`intentions.json`, read with the causal-route declarations and nothing new: the declared enabler is read as a condition, the declared inhibitor as a hold-back, circumstances are the shipped gates, and there are no relations. Over the " + N(n) + " cells of the sweep (" + N(Profiles) + " profiles x " + Wants.Length + " wants x 2 circumstances). S differs from `IntentionSelector.Form` in **" + N(formMismatch) + "** cells; weights not equal to the bit: **" + N(formWeight) + "**.");
            sb.AppendLine();
            sb.AppendLine("| | No intention | Ties | Differs from A | Share | Differs from S |");
            sb.AppendLine("|---|---|---|---|---|---|");
            foreach (var r in FrozenReps)
            {
                var none = tokens[r].Count(t => t == "none");
                var ties = tokens[r].Count(t => t.StartsWith("tie:", StringComparison.Ordinal));
                var vsA = Enumerable.Range(0, n).Count(k => tokens[r][k] != tokens[Rep.A][k]);
                var vsS = Enumerable.Range(0, n).Count(k => tokens[r][k] != tokens[Rep.S][k]);
                sb.AppendLine("| " + Name(r) + " | " + N(none) + " | " + N(ties) + " | " + N(vsA) + " | " + Pc(vsA, n) + " | " + N(vsS) + " |");
            }
            sb.AppendLine();
            foreach (var r in new[] { Rep.BParts, Rep.BPartsW })
            {
                sb.AppendLine("**" + Name(r) + " against A, by group:** "
                              + string.Join(", ", Enumerable.Range(0, n).Where(k => tokens[r][k] != tokens[Rep.A][k]).GroupBy(k => groups[k]).OrderBy(g => g.Key, StringComparer.Ordinal).Select(g => g.Key + " " + N(g.Count()))) + ".");
                sb.AppendLine();
            }
            sb.AppendLine("**B-parts against A, by who changed and how:**");
            sb.AppendLine();
            sb.AppendLine("| Profile | A chose | B-parts chose | Cells |");
            sb.AppendLine("|---|---|---|---|");
            foreach (var g in Enumerable.Range(0, n).Where(k => tokens[Rep.BParts][k] != tokens[Rep.A][k])
                         .GroupBy(k => (believer[k] ? "believes it was theirs to answer for" : "holds no such belief") + "|" + tokens[Rep.A][k] + "|" + tokens[Rep.BParts][k])
                         .OrderByDescending(g => g.Count()))
            {
                var p = g.Key.Split('|');
                sb.AppendLine("| " + p[0] + " | " + p[1] + " | " + p[2] + " | " + N(g.Count()) + " |");
            }
            Record("4", sb.ToString());
            Assert.AreEqual(0, formMismatch, "S is the selector on the frozen file");
        }

        // ============================================================ 5

        [Test, Order(5), Timeout(7200000)]
        public void E_RealMornings()
        {
            EnsureFrozen();
            var reps = new[] { Rep.S, Rep.A, Rep.BParts, Rep.B, Rep.BPartsW };
            var pantryWants = _content.Rules.Proposals.Where(p => p.Action == "check_pantry").Select(p => p.Motive).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
            var moments = 0;
            var live = 0;
            var liveChanged = reps.ToDictionary(r => r, r => 0);
            var liveNone = reps.ToDictionary(r => r, r => 0);
            var liveByWant = new Dictionary<string, int>(StringComparer.Ordinal);
            var examples = new List<string>();
            var real = 0;
            var realChanged = reps.ToDictionary(r => r, r => 0);
            var realNone = reps.ToDictionary(r => r, r => 0);
            var realExamples = new List<string>();

            Dictionary<Rep, string> Decide(Mind mind, Percept p, string want, string target)
            {
                var lv = Levels(mind, p, target);
                var s = new Sit { Id = "real", Others = !p.Alone, Target = target != null && p.Present.Contains(target), Watched = false };
                var c = FrozenCase(want);
                return reps.ToDictionary(r => r, r => Evaluate(c, lv, s, p, r).Token);
            }

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
                        foreach (var w in Wants)
                        {
                            if (!FrozenCase(w).Rules.Any(r => r.When.Matches(p))) continue;
                            live++;
                            var outs = Decide(mind, p, w, target);
                            foreach (var r in reps)
                            {
                                if (outs[r] == "none") liveNone[r]++;
                                if (outs[r] != outs[Rep.A]) liveChanged[r]++;
                            }
                            if (outs[Rep.BParts] != outs[Rep.A])
                            {
                                liveByWant[w] = (liveByWant.TryGetValue(w, out var v) ? v : 0) + 1;
                                if (examples.Count < 8)
                                    examples.Add("| " + label + " m" + moment.Minute + " | " + moment.CharacterId + " | `" + w + "` " + (p.Alone ? "alone" : "in company") + " | " + outs[Rep.A] + " | " + outs[Rep.BParts] + " |");
                            }
                        }

                        var d = moment.Decision;
                        var leading = d.Leading;
                        if (d.Chosen == null || d.Chosen.KindName != "check_pantry" || leading == null || !pantryWants.Contains(leading.Name)) return;
                        var people = new List<Tuple<string, Mind>> { Tuple.Create(moment.CharacterId, mind) };
                        foreach (var y in Cast.Where(x => x != moment.CharacterId)) people.Add(Tuple.Create(y, run.Simulation.Minds[y]));
                        foreach (var person in people)
                        {
                            real++;
                            var outs = Decide(person.Item2, p, leading.Name, target);
                            foreach (var r in reps)
                            {
                                if (outs[r] == "none") realNone[r]++;
                                if (outs[r] != outs[Rep.A]) realChanged[r]++;
                            }
                            if (outs[Rep.BParts] != outs[Rep.A] && realExamples.Count < 8)
                                realExamples.Add("| " + label + " m" + moment.Minute + " | " + person.Item1 + (person.Item1 == moment.CharacterId ? " (checking)" : " (matched)") + " | `" + leading.Name + "` | " + outs[Rep.A] + " | " + outs[Rep.BParts] + " |");
                        }
                    };
                    run.Morning.Run(_content.Morning.Minutes);
                }

            var sb = new StringBuilder();
            sb.AppendLine("## 5. Behaviour in real mornings");
            sb.AppendLine();
            sb.AppendLine("50 baseline mornings (" + _content.Morning.Variants.Count + " variants x " + MorningSeeds + " seeds), the frozen file read as in section 4. **Live cells:** every real decision moment (" + N(moments) + ") asked about every want with a compatible rule: " + N(live) + " cells carrying real beliefs and feelings. **Real decisions:** every real pantry-check for a want whose shipped proposals lead there, with every other member of the cast at the same moment: " + N(real) + ".");
            sb.AppendLine();
            sb.AppendLine("| | " + string.Join(" | ", reps.Select(Name)) + " |");
            sb.AppendLine("|---|" + string.Join("|", reps.Select(_ => "---")) + "|");
            sb.AppendLine("| Live cells differing from A | " + string.Join(" | ", reps.Select(r => N(liveChanged[r]) + " (" + Pc(liveChanged[r], live) + ")")) + " |");
            sb.AppendLine("| Live cells with no intention | " + string.Join(" | ", reps.Select(r => N(liveNone[r]))) + " |");
            sb.AppendLine("| Real decisions differing from A | " + string.Join(" | ", reps.Select(r => N(realChanged[r]) + " of " + N(real))) + " |");
            sb.AppendLine("| Real decisions with no intention | " + string.Join(" | ", reps.Select(r => N(realNone[r]))) + " |");
            sb.AppendLine();
            sb.AppendLine("B-parts against A in live cells, by want: " + (liveByWant.Count == 0 ? "none" : string.Join(", ", liveByWant.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => "`" + kv.Key + "` " + N(kv.Value)))) + ".");
            if (examples.Count > 0)
            {
                sb.AppendLine();
                sb.AppendLine("| Morning | Who | Want | A | B-parts |");
                sb.AppendLine("|---|---|---|---|---|");
                foreach (var e in examples) sb.AppendLine(e);
            }
            if (realExamples.Count > 0)
            {
                sb.AppendLine();
                sb.AppendLine("Real decisions B-parts changes:");
                sb.AppendLine();
                sb.AppendLine("| Morning | Who | Want | A | B-parts |");
                sb.AppendLine("|---|---|---|---|---|");
                foreach (var e in realExamples) sb.AppendLine(e);
            }
            Record("5", sb.ToString());
        }

        // ============================================================ 6

        static readonly string[] Q1 = { "same", "different", "unclear" };
        static readonly string[] Q2 = { "both_add", "one_strengthens_other", "one_or_other", "never_together", "opposed", "unclear" };
        static readonly string[] Q3 = { "pushes", "holds_back", "must_hold", "situation_needed", "situation_strengthens", "consequence", "no_part", "unclear" };
        static readonly string[] Q5 = { "yes", "no", "unclear" };

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

        sealed class Annotation
        {
            public List<JObject> Items;
            public JObject Key;
            public List<JObject> Reviewers;
            public Dictionary<string, List<JObject>> ByItem;   // item id -> one answer per reviewer, reasons in items.json order
            public double KappaQ1, KappaQ2, KappaQ3, KappaQ5;
            public Dictionary<string, string> MajorityQ1 = new Dictionary<string, string>(StringComparer.Ordinal);
            public Dictionary<string, string> MajorityQ2 = new Dictionary<string, string>(StringComparer.Ordinal);
            public Dictionary<string, string> MajorityQ5 = new Dictionary<string, string>(StringComparer.Ordinal);
            public Dictionary<string, string> MajorityQ3 = new Dictionary<string, string>(StringComparer.Ordinal); // "item|r|f"
        }

        static Annotation _annotation;

        static Annotation EnsureAnnotation()
        {
            if (_annotation != null) return _annotation;
            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "experiments", "reason-semantics", "annotation");
            var itemsJson = JObject.Parse(File.ReadAllText(Path.Combine(dir, "items.json")));
            var a = new Annotation
            {
                Items = ((JArray)itemsJson["items"]).Cast<JObject>().ToList(),
                Key = (JObject)itemsJson["answer_key"],
                Reviewers = Directory.GetFiles(Path.Combine(dir, "responses"), "reviewer-*.json").OrderBy(f => f, StringComparer.Ordinal).Select(f => JObject.Parse(File.ReadAllText(f))).ToList()
            };
            a.ByItem = a.Items.ToDictionary(it => it["id"].Value<string>(), it => new List<JObject>(), StringComparer.Ordinal);
            foreach (var rv in a.Reviewers)
            {
                var swapped = rv["order"].Value<string>().Contains("swapped: yes");
                var answers = ((JArray)rv["answers"]).Cast<JObject>().ToDictionary(x => x["id"].Value<string>(), x => x, StringComparer.Ordinal);
                for (var k = 0; k < a.Items.Count; k++)
                {
                    var it = a.Items[k];
                    answers.TryGetValue("item-" + (k + 1).ToString("00"), out var ans);
                    var copy = ans == null ? new JObject() : (JObject)ans.DeepClone();
                    if (swapped && ((JArray)it["reasons"]).Count == 2 && copy["parts"] is JArray parts && parts.Count == 2)
                        copy["parts"] = new JArray(parts[1], parts[0]);
                    a.ByItem[it["id"].Value<string>()].Add(copy);
                }
            }

            var q1 = new List<Dictionary<string, int>>();
            var q2 = new List<Dictionary<string, int>>();
            var q3 = new List<Dictionary<string, int>>();
            var q5 = new List<Dictionary<string, int>>();
            var ambiguous = ((JArray)a.Key["ambiguous_slots"]["slots"]).Select(x => x["item"].Value<string>() + "|" + x["reason"].Value<int>() + "|" + x["fact"].Value<int>()).ToList();
            foreach (var it in a.Items)
            {
                var id = it["id"].Value<string>();
                var key = (JObject)a.Key[id];
                var answers = a.ByItem[id];
                var reasons = (JArray)it["reasons"];
                if (reasons.Count == 2)
                {
                    var t1 = Tally(answers.Select(x => x["q1"]?.Value<string>()), Q1);
                    q1.Add(t1);
                    a.MajorityQ1[id] = Majority(t1);
                    if (key["q1"].Value<string>() == "different")
                    {
                        var t2 = Tally(answers.Select(x => x["q2"]?.Value<string>()), Q2);
                        q2.Add(t2);
                        a.MajorityQ2[id] = Majority(t2);
                    }
                }
                if (it["this_person"] != null)
                {
                    var t5 = Tally(answers.Select(x => x["q5"]?.Value<string>()), Q5);
                    q5.Add(t5);
                    a.MajorityQ5[id] = Majority(t5);
                }
                for (var r = 0; r < reasons.Count; r++)
                    for (var f = 0; f < ((JArray)reasons[r]["draws_on"]).Count; f++)
                    {
                        var slot = id + "|" + r + "|" + f;
                        var t3 = Tally(answers.Select(x => (x["parts"] as JArray)?.ElementAtOrDefault(r)?.ElementAtOrDefault(f)?.Value<string>()), Q3);
                        a.MajorityQ3[slot] = Majority(t3);
                        if (!ambiguous.Contains(slot)) q3.Add(t3);
                    }
            }
            a.KappaQ1 = Fleiss(q1, Q1);
            a.KappaQ2 = Fleiss(q2, Q2);
            a.KappaQ3 = Fleiss(q3, Q3);
            a.KappaQ5 = Fleiss(q5, Q5);
            _annotation = a;
            return a;
        }

        static string KeyPart(Annotation a, string item, int r, int f) => ((JArray)((JArray)a.Key[item]["parts"])[r])[f].Value<string>();

        [Test, Order(6), Timeout(7200000)]
        public void F_TheBlindAnnotation()
        {
            var a = EnsureAnnotation();
            var sb = new StringBuilder();
            sb.AppendLine("## 6. Semantic and legibility evidence: the blind annotation");
            sb.AppendLine();
            sb.AppendLine(a.Reviewers.Count + " reviewers (" + string.Join(", ", a.Reviewers.Select(r => "#" + r["reviewer"] + " " + r["model"])) + "), each a fresh subagent shown only the items, in the rotated and swapped order the protocol fixes, under neutral ids. **They are language models, not people.** Agreement says whether a distinction is legible and reproducible, and nothing about whether it is true.");
            sb.AppendLine();
            sb.AppendLine("### Q1 and Q2: same or different, and how two different reasons relate");
            sb.AppendLine();
            sb.AppendLine("| Item | Q1 key | Q1 answers | Majority | Matches | Q2 key | Q2 answers | Majority | Matches |");
            sb.AppendLine("|---|---|---|---|---|---|---|---|---|");
            var q1Match = 0;
            var q1Items = 0;
            var q2Match = 0;
            var q2Items = 0;
            foreach (var it in a.Items.Where(x => ((JArray)x["reasons"]).Count == 2))
            {
                var id = it["id"].Value<string>();
                var key = (JObject)a.Key[id];
                var t1 = Tally(a.ByItem[id].Select(x => x["q1"]?.Value<string>()), Q1);
                q1Items++;
                if (a.MajorityQ1[id] == key["q1"].Value<string>()) q1Match++;
                var row = "| `" + id + "` | " + key["q1"] + " | " + Counts(t1) + " | " + a.MajorityQ1[id] + " | " + (a.MajorityQ1[id] == key["q1"].Value<string>() ? "yes" : "**no**");
                if (a.MajorityQ2.ContainsKey(id))
                {
                    var t2 = Tally(a.ByItem[id].Select(x => x["q2"]?.Value<string>()), Q2);
                    q2Items++;
                    if (a.MajorityQ2[id] == key["q2"].Value<string>()) q2Match++;
                    row += " | " + key["q2"] + " | " + Counts(t2) + " | " + a.MajorityQ2[id] + " | " + (a.MajorityQ2[id] == key["q2"].Value<string>() ? "yes" : "**no**") + " |";
                }
                else row += " | - | - | - | - |";
                sb.AppendLine(row);
            }
            sb.AppendLine();

            sb.AppendLine("### Q3: the part each fact plays");
            sb.AppendLine();
            sb.AppendLine("| Item | Reason | Fact | Key | Answers | Majority | Matches |");
            sb.AppendLine("|---|---|---|---|---|---|---|");
            var ambiguous = ((JArray)a.Key["ambiguous_slots"]["slots"]).Select(x => x["item"].Value<string>() + "|" + x["reason"].Value<int>() + "|" + x["fact"].Value<int>()).ToList();
            var slots = 0;
            var slotMatch = 0;
            var confusion = new Dictionary<string, Dictionary<string, int>>(StringComparer.Ordinal);
            foreach (var it in a.Items)
            {
                var id = it["id"].Value<string>();
                var reasons = (JArray)it["reasons"];
                for (var r = 0; r < reasons.Count; r++)
                    for (var f = 0; f < ((JArray)reasons[r]["draws_on"]).Count; f++)
                    {
                        var slot = id + "|" + r + "|" + f;
                        var keyPart = KeyPart(a, id, r, f);
                        var t3 = Tally(a.ByItem[id].Select(x => (x["parts"] as JArray)?.ElementAtOrDefault(r)?.ElementAtOrDefault(f)?.Value<string>()), Q3);
                        var maj = a.MajorityQ3[slot];
                        var isAmbiguous = ambiguous.Contains(slot);
                        if (!isAmbiguous)
                        {
                            slots++;
                            if (maj == keyPart) slotMatch++;
                            if (!confusion.ContainsKey(keyPart)) confusion[keyPart] = new Dictionary<string, int>(StringComparer.Ordinal);
                            confusion[keyPart][maj] = (confusion[keyPart].TryGetValue(maj, out var v) ? v : 0) + 1;
                        }
                        sb.AppendLine("| `" + id + "` | " + (r + 1) + " | " + ((JArray)reasons[r]["draws_on"])[f].Value<string>() + " | " + keyPart + " | " + Counts(t3) + " | " + maj + " | "
                                      + (isAmbiguous ? "(pre-registered ambiguous)" : maj == keyPart ? "yes" : "**no**") + " |");
                    }
            }
            sb.AppendLine();
            sb.AppendLine("**Key part against majority part**, over the " + slots + " slots that count:");
            sb.AppendLine();
            var majCats = Q3.Concat(new[] { "tie" }).Where(c => confusion.Values.Any(d => d.ContainsKey(c))).ToList();
            sb.AppendLine("| Key \\ majority | " + string.Join(" | ", majCats) + " |");
            sb.AppendLine("|---|" + string.Join("|", majCats.Select(_ => "---")) + "|");
            foreach (var kp in Q3.Where(confusion.ContainsKey))
                sb.AppendLine("| " + kp + " | " + string.Join(" | ", majCats.Select(c => confusion[kp].TryGetValue(c, out var v) ? v.ToString() : "")) + " |");
            sb.AppendLine();

            sb.AppendLine("### The minimal pairs");
            sb.AppendLine();
            sb.AppendLine("| Fact | Item | Key | Majority | Item | Key | Majority | Discriminated |");
            sb.AppendLine("|---|---|---|---|---|---|---|---|");
            foreach (var p in new[]
                     {
                         Tuple.Create("believing it was theirs to answer for", "owning_graded", 0, 0, "owning_conditional", 0, 0),
                         Tuple.Create("believing they lead the family", "settling_graded", 0, 0, "settling_conditional", 0, 0),
                         Tuple.Create("whether anyone is watching", "easier_unseen", 0, 2, "unseen_only", 0, 2)
                     })
            {
                var m1 = a.MajorityQ3[p.Item2 + "|" + p.Item3 + "|" + p.Item4];
                var m2 = a.MajorityQ3[p.Item5 + "|" + p.Item6 + "|" + p.Item7];
                var k1 = KeyPart(a, p.Item2, p.Item3, p.Item4);
                var k2 = KeyPart(a, p.Item5, p.Item6, p.Item7);
                sb.AppendLine("| " + p.Item1 + " | `" + p.Item2 + "` | " + k1 + " | " + m1 + " | `" + p.Item5 + "` | " + k2 + " | " + m2 + " | " + (m1 == k1 && m2 == k2 ? "**yes**" : "**no**") + " |");
            }
            sb.AppendLine();

            sb.AppendLine("### Q5: could this person form the intention at all?");
            sb.AppendLine();
            sb.AppendLine("| Item | Key | Answers | Majority | Matches |");
            sb.AppendLine("|---|---|---|---|---|");
            var q5Match = 0;
            foreach (var it in a.Items.Where(x => x["this_person"] != null))
            {
                var id = it["id"].Value<string>();
                var key = a.Key[id]["q5"].Value<string>();
                var t5 = Tally(a.ByItem[id].Select(x => x["q5"]?.Value<string>()), Q5);
                if (a.MajorityQ5[id] == key) q5Match++;
                sb.AppendLine("| `" + id + "` | " + key + " | " + Counts(t5) + " | " + a.MajorityQ5[id] + " | " + (a.MajorityQ5[id] == key ? "yes" : "**no**") + " |");
            }
            sb.AppendLine();

            sb.AppendLine("### Agreement");
            sb.AppendLine();
            sb.AppendLine("| Question | Items or slots | Majority matches the key | Fleiss' kappa |");
            sb.AppendLine("|---|---|---|---|");
            sb.AppendLine("| Q1 same or different | " + q1Items + " two-reason items | " + q1Match + " of " + q1Items + " (" + Pc(q1Match, q1Items) + ") | **" + K(a.KappaQ1) + "** |");
            sb.AppendLine("| Q2 relation | " + q2Items + " items keyed different | " + q2Match + " of " + q2Items + " (" + Pc(q2Match, q2Items) + ") | **" + K(a.KappaQ2) + "** |");
            sb.AppendLine("| Q3 part | " + slots + " slots (the one ambiguous slot excluded) | " + slotMatch + " of " + slots + " (" + Pc(slotMatch, slots) + ") | **" + K(a.KappaQ3) + "** |");
            sb.AppendLine("| Q5 reachable | " + a.MajorityQ5.Count + " items (unstable with so few) | " + q5Match + " of " + a.MajorityQ5.Count + " | **" + K(a.KappaQ5) + "** |");
            sb.AppendLine();
            var weak = a.MajorityQ3.Where(kv => !ambiguous.Contains(kv.Key)).Select(kv =>
            {
                var p = kv.Key.Split('|');
                var t = Tally(a.ByItem[p[0]].Select(x => (x["parts"] as JArray)?.ElementAtOrDefault(int.Parse(p[1]))?.ElementAtOrDefault(int.Parse(p[2]))?.Value<string>()), Q3);
                return new { Slot = "`" + p[0] + "` reason " + (int.Parse(p[1]) + 1) + " fact " + (int.Parse(p[2]) + 1), Top = t.Values.Max() };
            }).Where(x => x.Top < 4).Select(x => x.Slot + " (" + x.Top + " of " + a.Reviewers.Count + ")").ToList();
            sb.AppendLine("**Underspecified by the protocol's rule** (a majority of fewer than four, or a kappa below 0.4): " + (weak.Count == 0 ? "no item or slot" : string.Join("; ", weak))
                          + (new[] { a.KappaQ1, a.KappaQ2, a.KappaQ3, a.KappaQ5 }.Any(k => !double.IsNaN(k) && k < 0.4) ? "; and a question below 0.4 (see the table)" : "; no question below 0.4") + ".");
            sb.AppendLine();

            sb.AppendLine("### Q4, verbatim: what an explanation would need to show");
            sb.AppendLine();
            foreach (var it in a.Items)
            {
                var id = it["id"].Value<string>();
                sb.AppendLine("**`" + id + "`**");
                sb.AppendLine();
                for (var r = 0; r < a.Reviewers.Count; r++)
                    sb.AppendLine("- #" + a.Reviewers[r]["reviewer"] + " " + a.Reviewers[r]["model"] + ": " + (a.ByItem[id][r]["q4"]?.Value<string>() ?? "(no answer)"));
                sb.AppendLine();
            }
            Record("6", sb.ToString());
        }

        // ============================================================ 7

        sealed class Distinction
        {
            public string Name;
            public string Element;
            public string[] Checks;
            public string[] Questions;
            public string[] Tests;   // "item|q1|value", "item|q2|value", "item|q5|value", "item|r|f|value" (a Q3 slot)
        }

        static readonly Distinction[] Distinctions =
        {
            new Distinction { Name = "reason identity (H1)", Element = "identity", Checks = new[] { "A.1", "A.2", "A.3", "B.1", "B.2" }, Questions = new[] { "Q1" },
                Tests = new[] { "restate|q1|same", "verbatim|q1|same", "critical|q1|different" } },
            new Distinction { Name = "condition against push (H2)", Element = "parts", Checks = new[] { "C.3", "C.4", "C.5", "C.6", "F.1" }, Questions = new[] { "Q3" },
                Tests = new[] { "owning_graded|0|0|pushes", "owning_conditional|0|0|must_hold", "settling_graded|0|0|pushes", "settling_conditional|0|0|must_hold", "no_belief|0|0|must_hold" } },
            new Distinction { Name = "hold-back against a reason against", Element = "parts", Checks = new[] { "E.6", "E.7" }, Questions = new[] { "Q3", "Q2" },
                Tests = new[] { "fear_holds_back|0|1|holds_back", "fear_holds_back|1|2|no_part", "against|q2|opposed" } },
            new Distinction { Name = "circumstance (H3)", Element = "circumstances", Checks = new[] { "B.3", "D.2", "D.3", "D.4", "E.3", "F.2" }, Questions = new[] { "Q3" },
                Tests = new[] { "at_their_side|0|2|situation_needed", "unseen_only|0|2|situation_needed", "present_or_absent|0|2|situation_needed", "present_or_absent|1|2|situation_needed", "seen|1|2|situation_needed", "not_there|0|2|situation_needed", "worry_family|0|1|situation_needed" } },
            new Distinction { Name = "situational push against gate", Element = "circumstances", Checks = new[] { "D.6" }, Questions = new[] { "Q3" },
                Tests = new[] { "easier_unseen|0|2|situation_strengthens" } },
            new Distinction { Name = "alternative (H4)", Element = "relations", Checks = new[] { "E.2" }, Questions = new[] { "Q2" }, Tests = new[] { "quiet_or_open|q2|one_or_other" } },
            new Distinction { Name = "reinforcing (H4)", Element = "relations", Checks = new[] { "E.4", "E.5" }, Questions = new[] { "Q2" }, Tests = new[] { "worry_family|q2|one_strengthens_other" } },
            new Distinction { Name = "exclusive (H4)", Element = "relations", Checks = new[] { "E.3" }, Questions = new[] { "Q2" }, Tests = new[] { "present_or_absent|q2|never_together" } },
            new Distinction { Name = "opposed (H4)", Element = "relations", Checks = new[] { "E.6", "E.7" }, Questions = new[] { "Q2" }, Tests = new[] { "against|q2|opposed" } },
            new Distinction { Name = "no viable cause (H5)", Element = "viability", Checks = new[] { "F.1", "F.2", "F.3", "F.4", "F.5", "F.6" }, Questions = new[] { "Q5" },
                Tests = new[] { "no_belief|q5|no", "not_there|q5|no", "no_fairness|q5|no", "weak_pull|q5|yes" } }
        };

        static string[] ElementsOf(Rep r)
        {
            switch (r)
            {
                case Rep.S: return new string[0];
                case Rep.A: return new[] { "identity" };
                case Rep.BParts: return new[] { "identity", "parts", "viability" };
                case Rep.BCirc: return new[] { "identity", "circumstances", "viability" };
                case Rep.B: return new[] { "identity", "parts", "circumstances", "viability" };
                case Rep.C: return new[] { "identity", "parts", "circumstances", "viability", "relations" };
                default: return new string[0];
            }
        }

        [Test, Order(7), Timeout(7200000)]
        public void G_WhatIsRequired()
        {
            EnsureChecks();
            var a = EnsureAnnotation();
            if (_controlChanges.Count == 0) B_TheNegativeControls();
            if (_pvChecked.Count == 0) C_Provenance();
            double KappaOf(string q) => q == "Q1" ? a.KappaQ1 : q == "Q2" ? a.KappaQ2 : q == "Q3" ? a.KappaQ3 : a.KappaQ5;

            bool TestHolds(string t)
            {
                var p = t.Split('|');
                if (p.Length == 3)
                {
                    var map = p[1] == "q1" ? a.MajorityQ1 : p[1] == "q2" ? a.MajorityQ2 : a.MajorityQ5;
                    return map.TryGetValue(p[0], out var m) && m == p[2];
                }
                return a.MajorityQ3[p[0] + "|" + p[1] + "|" + p[2]] == p[3];
            }

            var status = new Dictionary<string, string>(StringComparer.Ordinal);
            var sb = new StringBuilder();
            sb.AppendLine("## 7. Which distinctions are required, and the verdict the committed criteria give");
            sb.AppendLine();
            sb.AppendLine("Computed from sections 1, 2, 3 and 6 by the rules committed in the predictions. **Necessary**: every representation lacking the element fails at least one of the distinction's checks. **Legible**: every annotation test of it has a majority matching the key, and the kappa of each question it rests on is at least 0.4. REQUIRED is both; REDUNDANT is not necessary; UNSUPPORTED is necessary but not legible.");
            sb.AppendLine();
            sb.AppendLine("| Distinction | Element | Checks | Representations lacking the element that pass them all | Annotation tests met | Kappa | Status |");
            sb.AppendLine("|---|---|---|---|---|---|---|");
            foreach (var d in Distinctions)
            {
                var lacking = Main.Where(r => !ElementsOf(r).Contains(d.Element)).ToList();
                var passing = lacking.Where(r => d.Checks.All(c => _checkResults[c][r].Passed)).ToList();
                var necessary = passing.Count == 0;
                var met = d.Tests.Count(TestHolds);
                var kappaOk = d.Questions.All(q => !double.IsNaN(KappaOf(q)) && KappaOf(q) >= 0.4);
                var legible = met == d.Tests.Length && kappaOk;
                var st = !necessary ? "REDUNDANT" : legible ? "REQUIRED" : "UNSUPPORTED";
                status[d.Name] = st;
                sb.AppendLine("| " + d.Name + " | " + d.Element + " | " + string.Join(", ", d.Checks) + " | " + (passing.Count == 0 ? "none" : string.Join(", ", passing.Select(Name)))
                              + " | " + met + " of " + d.Tests.Length + " | " + string.Join(", ", d.Questions.Select(q => q + " " + K(KappaOf(q)))) + " | **" + st + "** |");
            }
            sb.AppendLine();

            var allChecks = _checks.Select(c => c["id"].Value<string>()).ToList();
            sb.AppendLine("| Representation | (i) passes every check of every REQUIRED distinction | (ii) restatement, negative controls, PV1 | (iii) carries no UNSUPPORTED element | (iv) passes no check only through a copy | All four |");
            sb.AppendLine("|---|---|---|---|---|---|");
            var keep = new List<Rep>();
            var modify = new List<Rep>();
            foreach (var r in Main)
            {
                var i = Distinctions.Where(d => status[d.Name] == "REQUIRED").All(d => d.Checks.All(c => _checkResults[c][r].Passed));
                var ii = new[] { "A.1", "A.2", "A.3" }.All(c => _checkResults[c][r].Passed) && _controlChanges.Values.All(v => v[r] == 0) && _pvFailed[r] == 0;
                var iii = !Distinctions.Any(d => ElementsOf(r).Contains(d.Element) && status[d.Name] == "UNSUPPORTED");
                var iv = !_passedOnlyByCopy.Values.Any(v => v.TryGetValue(r, out var only) && only);
                if (i && ii && iii && iv) keep.Add(r);
                if (i && ii) modify.Add(r);
                sb.AppendLine("| " + Name(r) + " | " + (i ? "yes" : "no") + " | " + (ii ? "yes" : "no") + " | " + (iii ? "yes" : "no") + " | " + (iv ? "yes" : "no") + " | " + (i && ii && iii && iv ? "**yes**" : "no") + " |");
            }
            sb.AppendLine();
            var verdict = keep.Count > 0 ? "KEEP" : modify.Count > 0 ? "MODIFY" : "REBUILD";
            sb.AppendLine("**By the committed criteria: " + verdict + "**" + (keep.Count > 0 ? " (" + string.Join(", ", keep.Select(Name)) + " meets all four)" : modify.Count > 0 ? " (" + string.Join(", ", modify.Select(Name)) + " meets (i) and (ii); none meets all four)" : "") + ".");
            Record("7", sb.ToString());
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
            foreach (var f in new[] { Tuple.Create(_frozenPath, FrozenSha), Tuple.Create(_routesPath, RoutesSha), Tuple.Create(_sweepPath, SweepSha), Tuple.Create(_casesPath, CasesSha) })
            {
                var sha = Sha(f.Item1);
                sb.AppendLine("| `" + Path.GetFileName(f.Item1) + "` | `" + sha + "` | " + (sha == f.Item2 ? "unchanged" : "**CHANGED**") + " |");
                Assert.AreEqual(f.Item2, sha, Path.GetFileName(f.Item1));
            }
            sb.AppendLine();
            sb.AppendLine("Every case, variant and representation above lived in memory.");
            Record("Z", sb.ToString());
        }
    }
}
