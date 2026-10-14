"""What counts as new in a conversation, and when a room's conversation ends.

Shared by the simulation (world.py), which uses it as the morning happens, and by
metrics.py, which runs the old and new transcripts through the same rules afterwards.
Knows nothing about the house beyond room names and option ids.
"""

SPEECH = ("ask", "deny", "accuse", "confess", "reassure", "say",
          "propose", "volunteer", "object", "back", "decline",     # these five: the trip
          "propose_far", "volunteer_far",                           # and further along the street (stage B, W5)
          "confront",       # from the night on (reports/food_confront_impl.md)
          "save_water", "ration_water",     # the water's rule, from day 3 (reports/world_design.md, §4.2.3)
          "door_call", "door_refuse",       # words at the front door (reports/w2_design.md, §4.2; W2a)
          "talk", "tell")                   # a topic from earlier, and news for who missed it (talk_design.md)


def act_of(option):
    """(kind, target) of an option id. Kinds group options that are the same kind of act:
    reassuring one person or everyone is `reassure`, starting or carrying on a search is
    `search`. The target is a person for accuse, reassure, sit, back, object and say_to, a room for go.
    The trip's options (reports/trip_design.md, §3.3): proposing it, volunteering, objecting
    to it or to one person going, backing one person to go, and declining to go. Day 2 words them
    anew (reports/night_design.md, §6) with the same kinds: nobody_goes, keep_<q>_home, send_<q>,
    still_going (a restated offer) and refuse_to_go. Giving a portion to one person at a food
    moment (reports/body_design.md, §2.4) is `give`, aimed at nobody. Confronting one person about
    something they did, other than taking the can, is `confront` (reports/food_confront_impl.md)."""
    if option == "ask_who":
        return "ask", None
    if option == "propose_trip":
        return "propose", None
    if option in ("object_trip", "nobody_goes"):
        return "object", None
    if option == "say_other":
        return "say", None
    if option.startswith("say_to_"):        # words to one person, with no meaning about the can (play_fix1.md, fix 2)
        return "say", option[len("say_to_"):]
    if option.startswith("talk_"):          # reports/talk_design.md: talk_<topic>, tell_<names>_<topic>
        return "talk", None
    if option.startswith("tell_"):
        return "tell", None
    if option == "reassure_all":
        return "reassure", None
    if option == "keep_searching":
        return "search", None
    if option == "still_going":
        return "volunteer", None
    if option == "refuse_to_go":
        return "decline", None
    if option.startswith("keep_") and option.endswith("_home"):
        return "object", option[len("keep_"):-len("_home")]
    if option.startswith("send_"):
        return "back", option[len("send_"):]
    for prefix in ("accuse", "reassure", "sit", "go", "aside", "back", "object", "give", "confront"):
        if option.startswith(prefix + "_"):
            return prefix, option[len(prefix) + 1:]
    return option, None     # silent, deny, confess, search, eat, share, volunteer, decline


def aimed_at(option):
    """The person a line is aimed at, or None for a line to everyone in the room."""
    kind, target = act_of(option)
    return target if kind in ("accuse", "reassure", "aside", "back", "object", "confront", "say") else None


# What a position on the trip is, for the story (reports/trip_design.md, §3.3).
TRIP_WHY = {"propose": "a proposal", "volunteer": "an offer to go", "object": "an objection",
            "back": "backing someone to go", "decline": "a refusal to go",
            "propose_far": "a proposal to go further along the street",
            "volunteer_far": "an offer to go further along the street"}


class Newness:
    """Decides whether a spoken line adds something. New: a question, an accusation, a
    denial of a new accusation, a confession, a position on the trip the speaker has not
    taken before, a confrontation of someone they had not confronted before. Not new:
    reassurance, a stance the speaker has taken before this morning, and any other remark (the rules cannot read what free words add). New facts and people coming in are handled by the caller."""

    def __init__(self):
        self.stances = {}        # speaker -> stances already taken this morning
        self.unanswered = {}     # person -> new accusations against them not yet denied

    def line(self, speaker, option, audience):
        kind, target = act_of(option)
        taken = self.stances.setdefault(speaker, set())
        if kind == "confess":
            return True, "a confession"
        if kind == "ask":
            new = "ask" not in taken
            taken.add("ask")
            return new, "a question" if new else "a question they had asked before"
        if kind == "accuse":
            new = ("accuse", target) not in taken
            taken.add(("accuse", target))
            if new and target in audience:
                self.unanswered.setdefault(target, set()).add(speaker)
            return new, "an accusation" if new else "an accusation they had made before"
        if kind == "deny":
            pending = self.unanswered.pop(speaker, set())
            return (bool(pending), "a denial of a new accusation" if pending
                    else "a denial with no new accusation to answer")
        if kind == "confront":          # new the first time toward that person, as an accusation
            new = ("confront", target) not in taken
            taken.add(("confront", target))
            return new, "a confrontation" if new else "a confrontation they had made before"
        if kind == "reassure":
            return False, "reassurance"
        if kind in ("save_water", "ration_water"):     # a rule for the water: new the first time they say it
            new = kind not in taken
            taken.add(kind)
            return new, "a rule for the water" if new else "a rule for the water they had said before"
        if kind in ("door_call", "door_refuse"):      # W2a: new the first time in a door scene (forget_door)
            new = ("door", kind) not in taken
            taken.add(("door", kind))
            return new, "an answer at the door" if new else "an answer at the door they had given before"
        if kind in ("talk", "tell"):    # reports/talk_design.md: new the first time, per speaker and option
            new = (kind, option) not in taken
            taken.add((kind, option))
            what = "something from earlier" if kind == "talk" else "news for someone who had missed it"
            return new, what if new else what + " they had raised before"
        if kind in TRIP_WHY:
            stance = (kind, target)
            new = stance not in taken
            taken.add(stance)
            return new, TRIP_WHY[kind] if new else TRIP_WHY[kind] + " they had made before"
        return False, "a remark (the rules cannot tell what free words add)"


    def forget_door(self):
        """A new door scene: an answer at the door is new again for everyone."""
        for taken in self.stances.values():
            taken.discard(("door", "door_call"))
            taken.discard(("door", "door_refuse"))


class Conversations:
    """One conversation per room. Something new starts it (or keeps it going); `quiet_turns`
    full turns in a row with nothing new, or fewer than two people left, end it."""

    def __init__(self, rooms, quiet_turns=1):
        self.rooms = list(rooms)
        self.quiet_turns = quiet_turns
        self.active = {r: False for r in self.rooms}
        self.new = {r: False for r in self.rooms}
        self.quiet = {r: 0 for r in self.rooms}
        self.log = []            # (minute, room, "started" | "ended", why)

    def new_thing(self, room, minute, why):
        """Returns True when this starts the room's conversation."""
        self.new[room] = True
        self.quiet[room] = 0
        if not self.active[room]:
            self.active[room] = True
            self.log.append((minute, room, "started", why))
            return True
        return False

    def end_turn(self, minute_after, at_start, at_end):
        """at_start / at_end: room -> how many people were in it when the turn began / ended."""
        for r in self.rooms:
            if self.active[r]:
                if at_end[r] < 2:
                    self.active[r] = False
                    self.log.append((minute_after, r, "ended", "fewer than two people left in it"))
                elif at_start[r] >= 2 and not self.new[r]:
                    self.quiet[r] += 1
                    if self.quiet[r] >= self.quiet_turns:
                        self.active[r] = False
                        self.log.append((minute_after, r, "ended", "a full turn with nothing new"
                                         if self.quiet_turns == 1 else
                                         f"{self.quiet_turns} full turns in a row with nothing new"))
            self.new[r] = False
