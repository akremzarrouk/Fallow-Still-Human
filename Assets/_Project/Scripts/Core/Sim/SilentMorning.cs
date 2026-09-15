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

    /// <summary>
    /// The moment somebody decided, with everything the decision was made from,
    /// for an instrument to look at. Read-only in spirit: whatever looks at it
    /// must not change the mind or the percept.
    ///
    /// The mind is the live one. Anything that weighs the decision again must do
    /// it inside the callback, while the mind is still in the state it decided
    /// in; by the end of the morning its feelings have moved on, and a decision
    /// weighed again then is weighed by somebody else.
    /// </summary>
    public sealed class DecisionMoment
    {
        public int Minute;
        public string CharacterId;
        public Mind Mind;
        public Percept Percept;
        public IReadOnlyList<Motive> Motives;
        public Decision Decision;

        /// <summary>Why they were deciding at all: the start, having finished, or having been stopped.</summary>
        public string Why;
    }

    /// <summary>Somebody stopped part way through something, and what stopped them.</summary>
    public sealed class InterruptionRecord
    {
        public int Minute;
        public string CharacterId;
        public string Was;
        public string EventId;

        /// <summary>The strongest feeling the interrupting event itself stirred in them.</summary>
        public double EventIntensity;

        /// <summary>The strongest feeling they were carrying at the time, from anything.</summary>
        public double StandingIntensity;
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

            /// <summary>The decision it was chosen by, so what comes of it can be judged against why.</summary>
            public Decision Decision;
        }

        readonly Simulation _sim;
        readonly RuleSet _rules;
        readonly WorldState _world;
        readonly Motivator _motivator;
        readonly Deliberator _deliberator;
        readonly Rng _rng;
        readonly int _day;

        readonly Dictionary<string, Busy> _busy = new Dictionary<string, Busy>(StringComparer.Ordinal);

        /// <summary>What somebody was in the middle of when something stopped them to think again.</summary>
        readonly Dictionary<string, Busy> _stopped = new Dictionary<string, Busy>(StringComparer.Ordinal);

        /// <summary>Why somebody is walking where they are walking, kept until they arrive and decide.</summary>
        readonly Dictionary<string, Intention> _intentions = new Dictionary<string, Intention>(StringComparer.Ordinal);
        readonly Dictionary<string, HashSet<string>> _searchedBy = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        readonly HashSet<string> _showingIt = new HashSet<string>(StringComparer.Ordinal);

        /// <summary>Whoever was sat with and settled this minute, and the record of the settling, so that what can be seen of it rests on it.</summary>
        readonly Dictionary<string, int> _settledThisMinute = new Dictionary<string, int>(StringComparer.Ordinal);
        readonly Dictionary<string, int[]> _beingSatWith = new Dictionary<string, int[]>(StringComparer.Ordinal);
        readonly HashSet<string> _sawThePantry = new HashSet<string>(StringComparer.Ordinal);
        readonly Dictionary<string, int> _watched = new Dictionary<string, int>(StringComparer.Ordinal);

        readonly List<ActionRecord> _actions = new List<ActionRecord>();
        readonly List<Decision> _decisions = new List<Decision>();
        readonly List<WorldEvent> _events = new List<WorldEvent>();
        readonly List<InterruptionRecord> _interruptions = new List<InterruptionRecord>();
        readonly Dictionary<string, string> _why = new Dictionary<string, string>(StringComparer.Ordinal);

        int _order;

        /// <summary>Called after every decision, for instruments. Nothing in the simulation reads it.</summary>
        public Action<DecisionMoment> Decided { get; set; }

        public IReadOnlyList<InterruptionRecord> Interruptions => _interruptions;

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

            // The morning has a clock, so time is measured by it and not by how
            // much is going on somewhere else in the house.
            _sim.FadeOnEachEvent = false;

            // Everything the rules read about a body goes through here, so the
            // world stays the single source of it.
            _sim.Needs = (characterId, need) =>
                string.Equals(need, Needs.Hunger, StringComparison.Ordinal) ? _world.HungerOf(characterId) : 0.0;
        }

        public WorldState World => _world;

        public MorningResult Run(int minutes)
        {
            for (var minute = 0; minute < minutes; minute++) Step();
            return Snapshot();
        }

        /// <summary>Everything that has happened so far, without advancing anything.</summary>
        public MorningResult Snapshot() => new MorningResult(_actions, _decisions, _events, _world);

        /// <summary>Why somebody is walking where they are walking. Null when they are not walking for anything.</summary>
        public Intention Intends(string characterId)
            => _intentions.TryGetValue(characterId, out var i) ? i : null;

        /// <summary>What somebody is in the middle of, and how many minutes of it are left. Null when idle.</summary>
        public (ActionOption Action, int MinutesLeft)? Doing(string characterId)
            => _busy.TryGetValue(characterId, out var b) ? (b.Action, b.MinutesLeft) : ((ActionOption, int)?)null;

        /// <summary>
        /// For experiments: something happens in the house that nobody in the
        /// morning decided to do. It reaches people by exactly the route their
        /// own actions reach each other, and can stop them exactly as those can.
        /// </summary>
        public EventOutcome Happen(WorldEvent e)
        {
            _events.Add(e);
            var outcome = _sim.Apply(e);
            Interrupt(e, outcome);
            return outcome;
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
            _sim.PassTime(1.0 / _rules.Dynamics.MinutesPerFade);

            foreach (var id in _world.Inhabitants)
            {
                if (!_busy.TryGetValue(id, out var busy)) continue;
                busy.MinutesLeft--;
                if (busy.MinutesLeft > 0) continue;

                _busy.Remove(id);
                _why[id] = "finished";
                Complete(id, busy);
            }

            ShowWhatShows();
            _settledThisMinute.Clear();
            _beingSatWith.Clear();

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

            // Arriving somewhere is the one moment an intention is carried into a
            // decision. Something that landed hard enough to stop you means
            // thinking again from the beginning, so it is not carried then.
            _why.TryGetValue(characterId, out var reason);
            _intentions.TryGetValue(characterId, out var holding);
            if (reason != "finished") holding = null;

            var decision = _deliberator.Decide(
                mind, percept, motives, _day, _rng.Fork(characterId + "@" + _world.Minute),
                _sim.Trace, opening, holding);

            // Only a walk is a means to something else, so only a walk leaves an
            // intention standing. Anything else is the thing itself.
            if (decision.Chosen.Kind == ActionKind.GoTo && decision.Forms != null)
                _intentions[characterId] = decision.Forms;
            else
                _intentions.Remove(characterId);

            // Walking somewhere for a want and giving it up on arrival is itself
            // something that came of acting on it.
            var lapsed = Outcomes.OfLapse(decision.Commitment);
            if (decision.Holding != null && lapsed.HasValue)
                foreach (var need in NeedsReadBy(decision.Holding.MotiveName))
                {
                    var level = _sim.Needs(characterId, need);
                    Keep(characterId, new PursuitOutcome(
                            decision.Holding.MotiveKey, decision.Holding.MotiveName, decision.Holding.SetOutWith.Key,
                            need, level, level, lapsed.Value, _world.Minute, null, decision.Commitment),
                        new[] { decision.TraceId, decision.Holding.TraceId });
                }

            _decisions.Add(decision);

            Decided?.Invoke(new DecisionMoment
            {
                Minute = _world.Minute,
                CharacterId = characterId,
                Mind = mind,
                Percept = percept,
                Motives = motives,
                Decision = decision,
                Why = _why.TryGetValue(characterId, out var why) ? why : "start"
            });

            var leading = decision.Leading;
            var record = new ActionRecord(
                _world.Minute, characterId, decision.Chosen, percept.Room?.Id,
                leading?.Key ?? "nothing pressing", leading?.Urgency ?? 0.0,
                decision.Resolution, decision.Margin, decision.TraceId);
            _actions.Add(record);

            // Thinking again is not the same as giving up. Somebody stopped part
            // way through who weighs it all again and still chooses the same
            // thing picks it up where they left off.
            if (_stopped.TryGetValue(characterId, out var was))
            {
                _stopped.Remove(characterId);
                if (decision.Chosen.SameAs(was.Action))
                {
                    // Carried on, and for the reasons weighed just now.
                    was.Decision = decision;
                    _busy[characterId] = was;
                    record.Outcome = "thought again, and carried on";
                    _sim.Trace.Add(
                        TraceKind.Consequence, characterId, null, "thought again, and carried on",
                        new[] { decision.TraceId },
                        new Dictionary<string, string>
                        {
                            { "with", was.Action.Key },
                            { "minutes_left", was.MinutesLeft.ToString() }
                        });
                    return;
                }
            }

            _busy[characterId] = new Busy
            {
                Action = decision.Chosen,
                MinutesLeft = decision.Chosen.Duration,
                StartedAt = _world.Minute,
                Decision = decision
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
                    // You cannot sit with somebody who has left the room. Until S1.4
                    // the world soothed them anyway, wherever they had gone.
                    if (!string.Equals(_world.RoomOf(action.TargetId), roomId, StringComparison.Ordinal))
                    {
                        Note(record, action.TargetId + " had gone before it could help");
                        _sim.Trace.Add(
                            TraceKind.Consequence, characterId, null,
                            "could not sit with " + action.TargetId + ": they had gone",
                            busy.Decision == null ? null : new[] { busy.Decision.TraceId },
                            new Dictionary<string, string> { { "act", action.Key }, { "could_happen", "no" } });
                        break;
                    }

                    Note(record, "sat with " + action.TargetId);
                    var sat = Happened(characterId, action.TargetId, "comfort", "good", null, roomId,
                        Named(characterId) + " sits with " + Named(action.TargetId) + " for a while.");
                    Soothe(action.TargetId, characterId, busy.Decision?.TraceId);

                    // Whatever can be seen of them afterwards rests on both things
                    // being sat with did to them: what they made of it, and the
                    // settling.
                    var felt = _sim.Minds[action.TargetId].Experiences.LastOrDefault(x => x.EventId == sat.Id);
                    if (felt != null && _settledThisMinute.TryGetValue(action.TargetId, out var settledRecord))
                        _beingSatWith[action.TargetId] = new[] { settledRecord, felt.TraceId };
                    break;

                case ActionKind.Eat:
                    var hungerBefore = _world.HungerOf(characterId);
                    if (_world.TakePortion())
                    {
                        _world.SetHunger(characterId, hungerBefore - _rules.Deciding.PortionRelief);
                        Note(record, "ate a portion, leaving " + _world.Portions);
                        var ate = Happened(characterId, null, "eat_portion",
                            _world.Portions <= _rules.Deciding.LowPortions ? "bad" : "neutral", "supplies", roomId,
                            Named(characterId) + " takes a portion and eats it. " + _world.Portions + " left.");
                        Resolve(characterId, busy, ate, true, Needs.Hunger, hungerBefore, _world.HungerOf(characterId));
                    }
                    else
                    {
                        // Reaching for food that is not there is something that
                        // happens, to the person reaching and in front of anybody
                        // in the room. Until S1.3 it was written on the action
                        // record and nowhere anybody could perceive it.
                        Note(record, "found nothing left to eat");
                        var gone = Happened(characterId, null, "find_nothing_left", "bad", "supplies", roomId,
                            Named(characterId) + " reaches for the food and there is none left.");
                        Resolve(characterId, busy, gone, false, Needs.Hunger, hungerBefore, _world.HungerOf(characterId));
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
        ///
        /// TECHNICAL DEBT, recorded in S1.1 and deliberately left in place. This
        /// is the only place in the simulation where one person changes another
        /// person's feelings without that person perceiving and appraising
        /// anything. It is not evidence that the social pipeline works, it must
        /// not be copied for any other interpersonal act, and it should be
        /// replaced by perception and appraisal of being comforted when
        /// interpersonal acts get that machinery.
        /// </summary>
        void Soothe(string targetId, string byWhom, int? decisionTraceId = null)
        {
            if (targetId == null || !_sim.Minds.TryGetValue(targetId, out var mind)) return;

            var before = mind.Emotions.Dominant;
            foreach (var type in _rules.Deciding.ComfortSettles)
                mind.Emotions.Soften(type, _rules.Deciding.ComfortSettling, _rules.Dynamics.EmotionFloor);

            _settledThisMinute[targetId] = _sim.Trace.Add(
                TraceKind.Consequence, targetId, null,
                "was settled a little by " + byWhom,
                decisionTraceId.HasValue ? new[] { decisionTraceId.Value } : null,
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
        /// Only the moments it becomes visible, and stops being visible, are
        /// events, because a person who has been upset for ten minutes is not news
        /// every minute. The second was added in S1.4.
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
                    // Distress stopping is as visible as distress starting. Until
                    // S1.4 only the start was announced, so nobody could ever see
                    // that somebody had come right, including whoever had just sat
                    // with them. If it stopped because they were just sat with, what
                    // can be seen rests on that.
                    if (_showingIt.Remove(id))
                    {
                        var watching = _world.WithMe(id);
                        if (watching.Count > 0)
                            Happened(null, id, "steady", "neutral", null, _world.RoomOf(id),
                                Named(id) + " seems to be holding together again.",
                                watching, audible: false,
                                causes: _beingSatWith.TryGetValue(id, out var sat) ? sat : null);
                    }
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
        WorldEvent Happened(
            string actorId, string targetId, string action, string valence, string topic,
            string roomId, string summary, IReadOnlyList<string> witnesses = null,
            bool audible = true, IReadOnlyList<int> causes = null)
        {
            var saw = witnesses ?? _world.InRoom(roomId)
                .Where(id => !string.Equals(id, actorId, StringComparison.Ordinal))
                .ToList();

            // Some things can only be seen: somebody's face settling makes no sound.
            var heard = !audible
                ? new List<string>()
                : _world.WithinEarshotOf(roomId)
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
            var outcome = _sim.Apply(e, causes);
            Interrupt(e, outcome);
            return e;
        }

        /// <summary>
        /// Judges what came of an act against the wants it was chosen for, by
        /// what its consequence did to the need each of them reads, and gives the
        /// person a record of it.
        ///
        /// Only wants that read the need the act touched are judged. The judgement
        /// uses nothing but the need before and after and whether the act could
        /// happen at all. It changes no level: the world has already done that, or
        /// has not.
        /// </summary>
        void Resolve(string characterId, Busy busy, WorldEvent consequence, bool couldHappen, string need, double before, double after)
        {
            var chosen = busy.Decision?.ChosenScored;
            if (chosen == null) return;

            var mind = _sim.Minds[characterId];
            var felt = mind.Experiences.LastOrDefault(x => x.EventId == consequence.Id);

            var world = _sim.Trace.Add(
                TraceKind.Consequence, characterId, consequence.Id,
                couldHappen
                    ? need + " " + before.ToString("0.00") + " -> " + after.ToString("0.00")
                    : "could not be done: " + need + " stays " + after.ToString("0.00"),
                new[] { busy.Decision.TraceId },
                new Dictionary<string, string>
                {
                    { "act", busy.Action.Key },
                    { "need", need },
                    { "before", before.ToString("0.000") },
                    { "after", after.ToString("0.000") },
                    { "could_happen", couldHappen ? "yes" : "no" }
                });

            foreach (var want in chosen.Contributions
                         .Where(c => c.Amount > 0.0)
                         .GroupBy(c => c.MotiveKey, StringComparer.Ordinal)
                         .Select(g => g.First()))
            {
                if (!NeedsReadBy(want.MotiveName).Contains(need, StringComparer.Ordinal)) continue;

                // Nearest reasons first: what the act did, what the person made of
                // it, the want it was for, and then the whole decision.
                var parents = new List<int> { world };
                if (felt != null) parents.Add(felt.TraceId);
                parents.Add(want.MotiveTraceId);
                parents.Add(busy.Decision.TraceId);

                Keep(characterId, new PursuitOutcome(
                        want.MotiveKey, want.MotiveName, busy.Action.Key, need, before, after,
                        Outcomes.OfConsequence(couldHappen, before, after), _world.Minute, consequence.Id),
                    parents);
            }
        }

        void Keep(string characterId, PursuitOutcome outcome, IEnumerable<int> restsOn)
        {
            outcome.TraceId = _sim.Trace.Add(
                TraceKind.Outcome, characterId, outcome.EventId,
                outcome.MotiveKey + ": " + outcome,
                restsOn.Distinct().ToList(),
                new Dictionary<string, string>
                {
                    { "want", outcome.MotiveKey },
                    { "outcome", PursuitOutcome.Words(outcome.Kind) },
                    { "need", outcome.Need },
                    { "before", outcome.Before.ToString("0.000") },
                    { "after", outcome.After.ToString("0.000") }
                });
            _sim.Minds[characterId].Record(outcome);
        }

        /// <summary>The needs a want reads, according to the rules that raise it.</summary>
        IReadOnlyList<string> NeedsReadBy(string motiveName)
            => _rules.Motivation
                .Where(r => string.Equals(r.Motive, motiveName, StringComparison.Ordinal))
                .SelectMany(r => r.ScaledBy ?? new List<Scaler>())
                .Where(sc => string.Equals(sc.Kind, ScalerKind.Need, StringComparison.Ordinal))
                .Select(sc => sc.Name)
                .Distinct(StringComparer.Ordinal)
                .ToList();

        /// <summary>
        /// Something that lands hard enough stops you doing what you were doing.
        /// Anything less and people finish what they started, which is what keeps
        /// them from turning round every time somebody walks past.
        ///
        /// What has to land is this moment. S1.2 found the rule reading the
        /// strongest feeling the person was carrying from anything at all, so
        /// somebody already upset was stopped by every door that opened: nearly
        /// half of all decisions in a morning were taken because of an
        /// interruption, and nearly half of those interruptions were events that
        /// stirred almost nothing. Being stopped is now earned by what just
        /// happened to you, measured against the same threshold.
        /// </summary>
        void Interrupt(WorldEvent e, EventOutcome outcome)
        {
            foreach (var id in _world.Inhabitants.ToList())
            {
                if (!_busy.TryGetValue(id, out var busy)) continue;
                if (e.AccessFor(id) == Access.None) continue;

                var mind = _sim.Minds[id];
                var stirred = mind.Experiences.LastOrDefault(x => x.EventId == e.Id);
                if (stirred == null) continue;

                PerceptionOutcome landed = null;
                if (outcome == null || !outcome.ByCharacter.TryGetValue(id, out landed)) continue;
                if (landed.Dominant == null || landed.DominantIntensity < _rules.Deciding.InterruptIntensity) continue;

                _interruptions.Add(new InterruptionRecord
                {
                    Minute = _world.Minute,
                    CharacterId = id,
                    Was = busy.Action.Key,
                    EventId = e.Id,
                    EventIntensity = landed.DominantIntensity,
                    StandingIntensity = mind.Emotions.Dominant?.Intensity ?? 0.0
                });
                _why[id] = "interrupted";
                _busy.Remove(id);
                _stopped[id] = busy;
                _sim.Trace.Add(
                    TraceKind.Consequence, id, e.Id, "stopped what they were doing",
                    new[] { stirred.TraceId },
                    new Dictionary<string, string>
                    {
                        { "was", busy.Action.Key },
                        { "minutes_left", busy.MinutesLeft.ToString() },
                        { "because", landed.Dominant.ToString() }
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
