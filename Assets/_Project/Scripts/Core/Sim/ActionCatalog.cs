using System;
using System.Collections.Generic;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;

namespace Fallow.Core.Sim
{
    /// <summary>
    /// What a person could actually do from where they are standing.
    ///
    /// This runs before anything is weighed, and it is the reason wanting
    /// something badly enough can never conjure it: an action that the house
    /// does not allow never becomes an option, so it cannot be scored, so it
    /// cannot be chosen. Eating requires food within reach whoever you are.
    ///
    /// Availability is decided from the Percept alone, so a person cannot reach
    /// for something on the strength of a fact they have no way of knowing.
    /// </summary>
    public static class ActionCatalog
    {
        /// <summary>The kind of room the food is kept in.</summary>
        public const string PantryTag = "pantry";

        public static IReadOnlyList<ActionOption> Available(Percept p, DecisionDynamics dyn)
        {
            var options = new List<ActionOption>();
            if (p == null || p.Room == null) return options;

            // Doing nothing is always possible, and is a real choice rather than
            // the absence of one.
            options.Add(new ActionOption(ActionKind.Wait, duration: dyn.MinutesFor("wait")));

            foreach (var other in p.Present)
            {
                // Looking at somebody you have only just looked at is not
                // something a person can usefully decide to do.
                if (!p.JustWatched.Contains(other, StringComparer.Ordinal))
                    options.Add(new ActionOption(ActionKind.Observe, targetId: other, duration: dyn.MinutesFor("observe")));

                options.Add(new ActionOption(ActionKind.Comfort, targetId: other, duration: dyn.MinutesFor("comfort")));
            }

            // Somewhere to walk to: next door, and the nearest room of each kind
            // this house has. Anything further is reached one room at a time.
            var destinations = new SortedSet<string>(p.Adjacent, StringComparer.Ordinal);
            foreach (var tag in TagsWorthWalkingTo)
            {
                foreach (var room in new[] { p.NearestTagged(tag), p.NearestUnsearched(tag) })
                    if (room != null && !string.Equals(room, p.Room.Id, StringComparison.Ordinal))
                        destinations.Add(room);
            }

            foreach (var destination in destinations)
            {
                var steps = p.DistanceTo(destination);
                if (steps <= 0) continue;
                options.Add(new ActionOption(
                    ActionKind.GoTo,
                    destinationRoomId: destination,
                    duration: dyn.MinutesFor("go_to") * steps));
            }

            // Counting what is there is worth doing once. Opening the same door
            // again tells you what you already know.
            if (p.RoomHoldsFood && !p.LookedInThePantryMyself)
                options.Add(new ActionOption(ActionKind.CheckPantry, duration: dyn.MinutesFor("check_pantry")));

            if (p.FoodWithinReach == true)
                options.Add(new ActionOption(ActionKind.Eat, duration: dyn.MinutesFor("eat")));

            if (!p.SearchedThisRoomMyself)
                options.Add(new ActionOption(ActionKind.SearchRoom, duration: dyn.MinutesFor("search_room")));

            return options
                .OrderBy(o => o.Key, StringComparer.Ordinal)
                .ToList();
        }

        static readonly string[] TagsWorthWalkingTo = { PantryTag, "common", "private" };

        /// <summary>
        /// The options a proposal endorses, out of the ones that are available.
        ///
        /// A proposal says which kind of action serves a want and who it should
        /// be aimed at. It never introduces an option of its own, so the world
        /// always has the last word on what is possible.
        /// </summary>
        public static IEnumerable<ActionOption> Endorsed(
            ProposalRule proposal, Motive motive, Percept percept, IReadOnlyList<ActionOption> available)
        {
            var kind = proposal.Action;

            foreach (var option in available)
            {
                if (!string.Equals(option.KindName, kind, StringComparison.Ordinal)) continue;

                switch (proposal.Targeting)
                {
                    case Targeting.None:
                        if (option.TargetId == null && option.DestinationRoomId == null) yield return option;
                        break;

                    case Targeting.MotiveTarget:
                        if (motive.TargetId != null &&
                            string.Equals(option.TargetId, motive.TargetId, StringComparison.Ordinal))
                            yield return option;
                        break;

                    case Targeting.EachPresent:
                        if (option.TargetId != null) yield return option;
                        break;

                    case Targeting.NearestTagged:
                        var wanted = percept.NearestTagged(proposal.RoomTag);
                        if (wanted != null &&
                            string.Equals(option.DestinationRoomId, wanted, StringComparison.Ordinal))
                            yield return option;
                        break;

                    case Targeting.NearestUnsearched:
                        var fresh = percept.NearestUnsearched(proposal.RoomTag);
                        if (fresh != null &&
                            string.Equals(option.DestinationRoomId, fresh, StringComparison.Ordinal))
                            yield return option;
                        break;

                    case Targeting.AwayFromHere:
                        // Leaving means the next room, whichever it is. Which one
                        // is not part of the want, and is often a choice the
                        // person has no real preference about.
                        if (option.DestinationRoomId != null &&
                            percept.Adjacent.Contains(option.DestinationRoomId, StringComparer.Ordinal))
                            yield return option;
                        break;
                }
            }
        }
    }
}
