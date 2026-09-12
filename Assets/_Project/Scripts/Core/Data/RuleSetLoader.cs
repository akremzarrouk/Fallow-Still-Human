using System;
using System.Collections.Generic;
using System.IO;
using Fallow.Core.Rules;
using Newtonsoft.Json.Linq;

namespace Fallow.Core.Data
{
    public static class RuleSetLoader
    {
        public static RuleSet LoadFile(string path) => FromJson(File.ReadAllText(path));

        public static RuleSet FromJson(string json)
        {
            var root = JObject.Parse(json);

            var interpretation = new List<InterpretationRule>();
            if (root["interpretation"] is JArray interpNode)
                foreach (var r in interpNode)
                    interpretation.Add(new InterpretationRule
                    {
                        Id = r["id"]?.Value<string>(),
                        Note = r["note"]?.Value<string>(),
                        When = ReadCondition(r["when"] as JObject),
                        Label = r["label"]?.Value<string>(),
                        BaseWeight = r["base_weight"]?.Value<double>() ?? 0.0,
                        ScaledBy = ReadScalers(r["scaled_by"] as JArray)
                    });

            var nudges = new List<BeliefNudgeRule>();
            if (root["belief_nudges"] is JArray nudgeNode)
                foreach (var r in nudgeNode)
                    nudges.Add(new BeliefNudgeRule
                    {
                        Id = r["id"]?.Value<string>(),
                        Note = r["note"]?.Value<string>(),
                        When = ReadCondition(r["when"] as JObject),
                        Predicate = r["predicate"]?.Value<string>(),
                        Args = ReadStrings(r["args"]),
                        Delta = r["delta"]?.Value<double>() ?? 0.0,
                        ScaledBy = ReadScalers(r["scaled_by"] as JArray)
                    });

            var appraisal = new List<AppraisalRule>();
            if (root["appraisal"] is JArray appraisalNode)
                foreach (var r in appraisalNode)
                    appraisal.Add(new AppraisalRule
                    {
                        Id = r["id"]?.Value<string>(),
                        Note = r["note"]?.Value<string>(),
                        When = ReadCondition(r["when"] as JObject),
                        Emotion = r["emotion"]?.Value<string>(),
                        Target = r["target"]?.Value<string>(),
                        Concern = r["concern"]?.Value<string>(),
                        BaseIntensity = r["base_intensity"]?.Value<double>() ?? 0.0,
                        ScaledBy = ReadScalers(r["scaled_by"] as JArray)
                    });

            var motivation = new List<MotivationRule>();
            if (root["motivation"] is JArray motivationNode)
                foreach (var r in motivationNode)
                    motivation.Add(new MotivationRule
                    {
                        Id = r["id"]?.Value<string>(),
                        Note = r["note"]?.Value<string>(),
                        When = ReadSituation(r["when"] as JObject),
                        Motive = r["motive"]?.Value<string>(),
                        Scope = r["scope"]?.Value<string>() ?? MotiveScope.Situation,
                        BaseUrgency = r["base_urgency"]?.Value<double>() ?? 0.0,
                        ScaledBy = ReadScalers(r["scaled_by"] as JArray)
                    });

            var proposals = new List<ProposalRule>();
            if (root["proposals"] is JArray proposalNode)
                foreach (var r in proposalNode)
                    proposals.Add(new ProposalRule
                    {
                        Id = r["id"]?.Value<string>(),
                        Note = r["note"]?.Value<string>(),
                        When = ReadSituation(r["when"] as JObject),
                        Motive = r["motive"]?.Value<string>(),
                        Action = r["action"]?.Value<string>(),
                        Targeting = r["targeting"]?.Value<string>() ?? Rules.Targeting.None,
                        RoomTag = r["room_tag"]?.Value<string>(),
                        Fit = r["fit"]?.Value<double>() ?? 1.0
                    });

            var costs = new List<CostRule>();
            if (root["costs"] is JArray costNode)
                foreach (var r in costNode)
                    costs.Add(new CostRule
                    {
                        Id = r["id"]?.Value<string>(),
                        Note = r["note"]?.Value<string>(),
                        When = ReadSituation(r["when"] as JObject),
                        Action = r["action"]?.Value<string>(),
                        Base = r["base"]?.Value<double>() ?? 0.0,
                        ScaledBy = ReadScalers(r["scaled_by"] as JArray)
                    });

            return new RuleSet
            {
                Interpretation = interpretation,
                BeliefNudges = nudges,
                Appraisal = appraisal,
                Dynamics = ReadDynamics(root["dynamics"] as JObject),
                Motivation = motivation,
                Proposals = proposals,
                Costs = costs,
                Deciding = ReadDeciding(root["deciding"] as JObject)
            };
        }

        static SituationCondition ReadSituation(JObject o)
        {
            var c = new SituationCondition();
            if (o == null) return c;

            c.Alone = o["alone"]?.Value<bool>();
            c.InOwnRoom = o["in_own_room"]?.Value<bool>();
            c.InSomebodyElsesRoom = o["in_somebody_elses_room"]?.Value<bool>();
            c.RoomHoldsFood = o["room_holds_food"]?.Value<bool>();
            c.SearchedThisRoomMyself = o["searched_this_room_myself"]?.Value<bool>();
            c.OthersPresentMin = o["others_present_min"]?.Value<int>();

            return c;
        }

        static DecisionDynamics ReadDeciding(JObject o)
        {
            var d = new DecisionDynamics();
            if (o == null) return d;

            if (o["ambiguity_band"] != null) d.AmbiguityBand = o["ambiguity_band"].Value<double>();
            if (o["interrupt_intensity"] != null) d.InterruptIntensity = o["interrupt_intensity"].Value<double>();
            if (o["visible_distress"] != null) d.VisibleDistress = o["visible_distress"].Value<double>();
            if (o["hunger_per_minute"] != null) d.HungerPerMinute = o["hunger_per_minute"].Value<double>();
            if (o["portion_relief"] != null) d.PortionRelief = o["portion_relief"].Value<double>();
            if (o["low_portions"] != null) d.LowPortions = o["low_portions"].Value<int>();
            if (o["comfort_settling"] != null) d.ComfortSettling = o["comfort_settling"].Value<double>();
            if (o["recall_half_life"] != null) d.RecallHalfLife = o["recall_half_life"].Value<double>();
            if (o["urgency_knee"] != null) d.UrgencyKnee = o["urgency_knee"].Value<double>();
            if (o["watching_goes_stale_after"] != null)
                d.WatchingGoesStaleAfter = o["watching_goes_stale_after"].Value<int>();
            d.DistressShows = ReadStrings(o["distress_shows"]);
            d.ComfortSettles = ReadStrings(o["comfort_settles"]);

            var minutes = new Dictionary<string, int>(StringComparer.Ordinal);
            if (o["action_minutes"] is JObject minutesNode)
                foreach (var p in minutesNode)
                    minutes[p.Key] = p.Value?.Value<int>() ?? 1;
            d.ActionMinutes = minutes;

            return d;
        }

        static Condition ReadCondition(JObject o)
        {
            var c = new Condition();
            if (o == null) return c;

            c.EventTypes = ReadStrings(o["event_types"]);
            c.Acts = ReadStrings(o["acts"]);
            c.Actions = ReadStrings(o["actions"]);
            c.Topics = ReadStrings(o["topics"]);
            c.Tones = ReadStrings(o["tones"]);
            c.Directness = ReadStrings(o["directness"]);
            c.Valences = ReadStrings(o["valences"]);
            c.ActorRelations = ReadStrings(o["actor_relations"]);
            c.ActorRoles = ReadStrings(o["actor_roles"]);
            c.SelfRoles = ReadStrings(o["self_roles"]);
            c.Access = ReadStrings(o["access"]);
            c.Meanings = ReadStrings(o["meanings"]);
            c.Addressed = ReadStrings(o["addressed"]);
            c.ActorIsMinor = o["actor_is_minor"]?.Value<bool>();
            c.SelfIsMinor = o["self_is_minor"]?.Value<bool>();
            c.HasActor = o["has_actor"]?.Value<bool>();
            c.AudienceMin = o["audience_min"]?.Value<int>();

            return c;
        }

        static List<Scaler> ReadScalers(JArray node)
        {
            var list = new List<Scaler>();
            if (node == null) return list;

            foreach (var s in node)
                list.Add(new Scaler
                {
                    Kind = s["kind"]?.Value<string>(),
                    Name = s["name"]?.Value<string>(),
                    Predicate = s["predicate"]?.Value<string>(),
                    Args = ReadStrings(s["args"]),
                    Entry = s["entry"]?.Value<string>(),
                    About = s["about"]?.Value<string>(),
                    Topic = s["topic"]?.Value<string>(),
                    By = s["by"]?.Value<string>(),
                    Target = s["target"]?.Value<string>(),
                    Factor = s["factor"]?.Value<double>() ?? 0.0
                });

            return list;
        }

        static Dynamics ReadDynamics(JObject o)
        {
            var d = new Dynamics();
            if (o == null) return d;

            if (o["emotion_decay_base"] != null) d.EmotionDecayBase = o["emotion_decay_base"].Value<double>();
            if (o["emotion_decay_anxiety_resistance"] != null) d.EmotionDecayAnxietyResistance = o["emotion_decay_anxiety_resistance"].Value<double>();
            if (o["emotion_floor"] != null) d.EmotionFloor = o["emotion_floor"].Value<double>();
            if (o["overheard_confidence"] != null) d.OverheardConfidence = o["overheard_confidence"].Value<double>();
            if (o["salience_base"] != null) d.SalienceBase = o["salience_base"].Value<double>();
            if (o["overheard_intensity_scale"] != null) d.OverheardIntensityScale = o["overheard_intensity_scale"].Value<double>();
            if (o["minutes_per_fade"] != null) d.MinutesPerFade = o["minutes_per_fade"].Value<double>();

            return d;
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
