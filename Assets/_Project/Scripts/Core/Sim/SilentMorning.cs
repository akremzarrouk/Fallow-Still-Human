using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Tracing;

namespace Fallow.Core.Sim
{
    /// <summary>What somebody did, when, and what came of it.</summary>
    public sealed class ActionRecord
    {
        public int Minute { get; }
        public string CharacterId { get; }
        public ActionOption Action { get; }
        public string RoomId { get; }
        public string LeadingMotive { get; }
        public double LeadingUrgency { get; }
        public Resolution Resolution { get; }
        public double Margin { get; }
        public int DecisionTraceId { get; }
        public string Outcome { get; internal set; }

        public ActionRecord(
            int minute, string characterId, ActionOption action, string roomId,
            string leadingMotive, double leadingUrgency,
            Resolution resolution, double margin, int decisionTraceId)
        {
            Minute = minute;
            CharacterId = characterId;
            Action = action;
            RoomId = roomId;
            LeadingMotive = leadingMotive;
            LeadingUrgency = leadingUrgency;
            Resolution = resolution;
            Margin = margin;
            DecisionTraceId = decisionTraceId;
        }

        public override string ToString()
            => "min " + Minute + " " + CharacterId + " " + Action +
               " in " + RoomId + " because " + LeadingMotive;
    }

    /// <summary>Everything one silent morning produced.</summary>
    public sealed class MorningResult
    {
        public IReadOnlyList<ActionRecord> Actions { get; }
        public IReadOnlyList<Decision> Decisions { get; }
        public IReadOnlyList<WorldEvent> Events { get; }
        public WorldState World { get; }

        public MorningResult(
            IReadOnlyList<ActionRecord> actions, IReadOnlyList<Decision> decisions,
            IReadOnlyList<WorldEvent> events, WorldState world)
        {
            Actions = actions;
            Decisions = decisions;
            Events = events;
            World = world;
        }

        public IReadOnlyList<ActionRecord> By(string characterId)
            => Actions.Where(a => string.Equals(a.CharacterId, characterId, StringComparison.Ordinal)).ToList();
    }

    /// <summary>
    /// A morning in the house with nobody speaking.
    ///
    /// Time passes a minute at a time. Anyone not already busy works out what
    /// they want and what to do about it, and does it. What they do changes the
    /// house and becomes something that happened, which everybody near enough
    /// perceives through exactly the same pipeline their history reached them
    /// by. That is the loop the slice exists to test: state to want to action to
    /// consequence to a different state.
    ///
    /// The world is held here and nowhere else. Minds are handed a Percept and
    /// can act only on what it contains, so nobody can be influenced by a room
    /// they are not in.
    /// </summary>
    public sealed class SilentMorning
    {
        sealed class Busy
        {
            public ActionOption Action;
            public int MinutesLeft;
            public int StartedAt;
        }

        readonly Simulation _sim;
        readonly RuleSet _rules;
        readonly WorldState _world;
        readonly Motivator _motivator;
        readonly Deliberator _deliberator;
        readonly Rng _rng;
        readonly int _day;

        readonly Dictionary<string, Busy> _busy = new Dictionary<string, Busy>(StringComparer.Ordinal);
        readonly Dictionary<string, HashSet<string>> _searchedBy = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        readonly HashSet<string> _showingIt = new HashSet<string>(StringComparer.Ordinal);
        readonly HashSet<string> _sawThePantry = new HashSet<string>(StringComparer.Ordinal);
        readonly Dictionary<string, int> _watched = new Dictionary<string, int>(StringComparer.Ordinal);

        readonly List<ActionRecord> _actions = new List<ActionRecord>();
        readonly List<Decision> _decisions = new List<Decision>();
        readonly List<WorldEvent> _events = new List<WorldEvent>();

        int _order;

        public SilentMorning(Simulation sim, RuleSet rules, WorldState world, Rng rng, int day)
        {
            _sim = sim;
            _rules = rules;
            _world = world;
            _rng = rng;
            _day = day;
            _motivator = new Motivator(rules);
            _deliberator = new Deliberator(rules);

            foreach (var id in world.Inhabitants) _searchedBy[id] = new HashSet<string>(StringComparer.Ordinal);

            // Everything the rules read about a body goes through here, so the
            // world stays the single source of it.
            _sim.Needs = (characterId, need) =>
                string.Equals(need, Needs.Hunger, StringComparison.Ordinal) ? _world.HungerOf(characterId) : 0.0;
        }

        public WorldState World => _world;

        public MorningResult Run(int minutes)
        {
            for (var minute = 0; minute < minutes; minute++) Step();
            return new MorningResult(_actions, _decisions, _events, _world);
        }

        /// <summary>
        /// One minute. Whatever finished resolves first, so that the people who
        /// have yet to decide are deciding about the house as it now is.
        /// </summary>
        public void Step()
        {
            var rates = _world.Inhabitants.ToDictionary(
                id => id,
                id => _rules.Deciding.HungerPerMinute * _sim.Minds[id].Profile.HungerRate,
                StringComparer.Ordinal);
            _world.Tick(rates);

            foreach (var id in _world.Inhabitants)
            {
                if (!_busy.TryGetValue(id, out var busy)) continue;
                busy.MinutesLeft--;
                if (busy.MinutesLeft > 0) continue;

                _busy.Remove(id);
                Complete(id, busy);
            }

            ShowWhatShows();

            foreach (var id in _world.Inhabitants)
            {
                if (_busy.ContainsKey(id)) continue;
                Begin(id);
            }
        }

        void Begin(string characterId)
        {
            var mind = _sim.Minds[characterId];
            var percept = See(characterId);

            var opening = _sim.Trace.Add(
                TraceKind.Access, characterId, null,
                "at minute " + _world.Minute + ", " + percept,
                null,
                new Dictionary<string, string>
                {
                    { "room", percept.Room?.Id },
                    { "present", percept.Present.Count == 0 ? "nobody" : string.Join(", ", percept.Present) },
                    { "hunger", percept.Hunger.ToString("0.00") }
                });

            var motives = _motivator.Raise(mind, percept, _day, _sim.Trace, opening);
            var decision = _deliberator.Decide(
                mind, percept, motives, _day, _rng.Fork(characterId + "@" + _world.Minute),
                _sim.Trace, opening);

            _decisions.Add(decision);

            var leading = decision.Leading;
            var record = new ActionRecord(
                _world.Minute, characterId, decision.Chosen, percept.Room?.Id,
                leading?.Key ?? "nothing pressing", leading?.Urgency ?? 0.0,
                decision.Resolution, decision.Margin, decision.TraceId);
            _actions.Add(record);

            _busy[characterId] = new Busy
            {
                Action = decision.Chosen,
                MinutesLeft = decision.Chosen.Duration,
                StartedAt = _world.Minute
            };
        }

        /// <summary>
        /// The house as this person can currently know it. This is the only way
        /// a mind ever learns anything about the world.
        /// </summary>
        public Percept See(string characterId)
        {
            var roomId = _world.RoomOf(characterId);
            var room = _world.House.Get(roomId);
            var holdsFood = room != null && room.HasTag(ActionCatalog.PantryTag);

            return new Percept(
                characterId,
                _world.Minute,
                room,
                _world.WithMe(characterId),
                _world.House.Adjacent(roomId),
                _world.HungerOf(characterId),
                holdsFood,
                // You can see there is food only by standing where it is kept.
                holdsFood ? (bool?)(_world.Portions > 0) : null,
                _searchedBy[characterId].Contains(roomId ?? ""),
                _world.House,
                _sawThePantry.Contains(characterId),
                _world.WithMe(characterId).Where(other => JustWatched(characterId, other)).ToList(),
                _searchedBy[characterId].OrderBy(r => r, StringComparer.Ordinal).ToList());
        }

        void Complete(string characterId, Busy busy)
        {
            var action = busy.Action;
            var roomId = _world.RoomOf(characterId);
            var record = _actions.LastOrDefault(a =>
                string.Equals(a.CharacterId, characterId, StringComparison.Ordinal) && a.Minute == busy.StartedAt);

            switch (action.Kind)
            {
                case ActionKind.Wait:
                    Note(record, "stayed where they were");
                    break;

                case ActionKind.Observe:
                    _watched[characterId + ">" + action.TargetId] = _world.Minute;
                    Note(record, "watched " + action.TargetId);
                    Happened(characterId, action.TargetId, "observe", "neutral", null, roomId,
                        Named(characterId) + " watches " + Named(action.TargetId) + " without saying anything.");
                    break;

                case ActionKind.GoTo:
                    Walk(characterId, roomId, action.DestinationRoomId, record);
                    break;

                case ActionKind.CheckPantry:
                    _sawThePantry.Add(characterId);
                    var short_ = _world.Portions <= _rules.Deciding.LowPortions;
                    Note(record, "found " + _world.Portions + " portions left");
                    Happened(characterId, null, "count_supplies", short_ ? "bad" : "neutral", "supplies", roomId,
                        Named(characterId) + " opens the pantry and counts what is left: " + _world.Portions + ".");
                    break;

                case ActionKind.SearchRoom:
                    _searchedBy[characterId].Add(roomId ?? "");
                    _world.MarkSearched(roomId);
                    var owner = OwnerPresentIn(roomId, characterId);
                    Note(record, owner == null ? "went through the room" : "went through " + owner + " things");
                    Happened(characterId, owner, "search_belongings", "neutral", "missing_can", roomId,
                        owner == null
                            ? Named(characterId) + " goes through the " + RoomName(roomId) + "."
                            : Named(characterId) + " goes through " + Named(owner) + " things while they stand there.");
                    break;

                case ActionKind.Comfort:
                    Note(record, "sat with " + action.TargetId);
                    Happened(characterId, action.TargetId, "comfort", "good", null, roomId,
                        Named(characterId) + " sits with " + Named(action.TargetId) + " for a while.");
                    Soothe(action.TargetId, characterId);
                    break;

                case ActionKind.Eat:
                    if (_world.TakePortion())
                    {
                        _world.SetHunger(characterId, _world.HungerOf(characterId) - _rules.Deciding.PortionRelief);
                        Note(record, "ate a portion, leaving " + _world.Portions);
                        Happened(characterId, null, "eat_portion",
                            _world.Portions <= _rules.Deciding.LowPortions ? "bad" : "neutral", "supplies", roomId,
                            Named(characterId) + " takes a portion and eats it. " + _world.Portions + " left.");
                    }
                    else
                    {
                        Note(record, "found nothing left to eat");
                    }
                    break;
            }
        }

        void Walk(string characterId, string fromRoom, string toRoom, ActionRecord record)
        {
            var leftBehind = _world.WithMe(characterId);
            _world.Place(characterId, toRoom);
            var walkedInOn = _world.WithMe(characterId);

            Note(record, "went to " + toRoom);

            if (leftBehind.Count > 0)
                Happened(characterId, null, "leave_room", "neutral", null, fromRoom,
                    Named(characterId) + " walks out of the " + RoomName(fromRoom) + ".",
                    leftBehind);

            if (walkedInOn.Count > 0)
                Happened(characterId, null, "enter_room", "neutral", null, toRoom,
                    Named(characterId) + " comes into the " + RoomName(toRoom) + ".",
                    walkedInOn);
        }

        /// <summary>
        /// Being sat with settles you. The feelings it settles are named in the
        /// rule data rather than here, because which ones they are is a claim
        /// about people and belongs where it can be argued with.
        /// </summary>
        void Soothe(string targetId, string byWhom)
        {
            if (targetId == null || !_sim.Minds.TryGetValue(targetId, out var mind)) return;

            var before = mind.Emotions.Dominant;
            foreach (var type in _rules.Deciding.ComfortSettles)
                mind.Emotions.Soften(type, _rules.Deciding.ComfortSettling, _rules.Dynamics.EmotionFloor);

            _sim.Trace.Add(
                TraceKind.Consequence, targetId, null,
                "was settled a little by " + byWhom,
                null,
                new Dictionary<string, string>
                {
                    { "before", before == null ? "nothing" : before.ToString() },
                    { "after", mind.Emotions.Dominant == null ? "nothing" : mind.Emotions.Dominant.ToString() }
                });
        }

        /// <summary>
        /// Feeling and showing are not the same thing, so this is where they come
        /// apart. What reaches the room is the strength of the feeling scaled by
        /// how much of themselves this person lets out; someone composed can be
        /// frightened in a room full of people and nobody is any the wiser.
        ///
        /// Only the moment it becomes visible is an event, because a person who
        /// has been upset for ten minutes is not news every minute.
        /// </summary>
        void ShowWhatShows()
        {
            foreach (var id in _world.Inhabitants)
            {
                var mind = _sim.Minds[id];
                var dominant = mind.Emotions.Dominant;

                var shows = dominant != null
                            && _rules.Deciding.DistressShows.Contains(dominant.Type, StringComparer.Ordinal)
                            && dominant.Intensity * mind.Profile.Expressiveness >= _rules.Deciding.VisibleDistress;

                if (!shows)
                {
                    _showingIt.Remove(id);
                    continue;
                }

                if (!_showingIt.Add(id)) continue;

                var audience = _world.WithMe(id);
                if (audience.Count == 0) continue;

                Happened(null, id, "show_distress", "bad", null, _world.RoomOf(id),
                    Named(id) + " is not hiding it well.",
                    audience);
            }
        }

        void Note(ActionRecord record, string outcome)
        {
            if (record != null) record.Outcome = outcome;
        }

        /// <summary>
        /// Turns something that was done into something that happened, and lets
        /// everyone near enough make of it what they will. Who counts as near
        /// enough is decided by the house, never by the event.
        /// </summary>
        void Happened(
            string actorId, string targetId, string action, string valence, string topic,
            string roomId, string summary, IReadOnlyList<string> witnesses = null)
        {
            var saw = witnesses ?? _world.InRoom(roomId)
                .Where(id => !string.Equals(id, actorId, StringComparison.Ordinal))
                .ToList();

            var heard = _world.WithinEarshotOf(roomId)
                .Where(id => !saw.Contains(id, StringComparer.Ordinal))
                .Where(id => !string.Equals(id, actorId, StringComparison.Ordinal))
                .Where(id => !string.Equals(id, targetId, StringComparison.Ordinal))
                .ToList();

            _order++;
            var e = new WorldEvent(
                "m" + _world.Minute.ToString("000") + "-" + _order.ToString("000"),
                _day, 1000 + _order, EventKind.Action,
                actorId, targetId,
                null, action, topic, "neutral", "direct", valence,
                null, summary,
                saw, heard,
                new List<LedgerEffect>(),
                null,
                _world.Minute);

            _events.Add(e);
            _sim.Apply(e);
            Interrupt(e);
        }

        /// <summary>
        /// Something that lands hard enough stops you doing what you were doing.
        /// Anything less and people finish what they started, which is what keeps
        /// them from turning round every time somebody walks past.
        /// </summary>
        void Interrupt(WorldEvent e)
        {
            foreach (var id in _world.Inhabitants.ToList())
            {
                if (!_busy.TryGetValue(id, out var busy)) continue;
                if (e.AccessFor(id) == Access.None) continue;

                var mind = _sim.Minds[id];
                var stirred = mind.Experiences.LastOrDefault(x => x.EventId == e.Id);
                if (stirred == null) continue;

                var dominant = mind.Emotions.Dominant;
                if (dominant == null || dominant.Intensity < _rules.Deciding.InterruptIntensity) continue;

                _busy.Remove(id);
                _sim.Trace.Add(
                    TraceKind.Consequence, id, e.Id, "stopped what they were doing",
                    new[] { stirred.TraceId },
                    new Dictionary<string, string>
                    {
                        { "was", busy.Action.Key },
                        { "because", dominant.ToString() }
                    });
            }
        }

        bool JustWatched(string characterId, string otherId)
            => _watched.TryGetValue(characterId + ">" + otherId, out var when)
               && _world.Minute - when < _rules.Deciding.WatchingGoesStaleAfter;

        string OwnerPresentIn(string roomId, string exceptId)
        {
            var room = _world.House.Get(roomId);
            if (room == null) return null;

            return _world.InRoom(roomId)
                .Where(id => !string.Equals(id, exceptId, StringComparison.Ordinal))
                .FirstOrDefault(room.IsOwnedBy);
        }

        string Named(string id)
            => id != null && _sim.Minds.TryGetValue(id, out var m) ? m.Profile.DisplayName : id;

        string RoomName(string roomId)
            => _world.House.Get(roomId)?.DisplayName ?? roomId;
    }
}
