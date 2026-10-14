"""What counts as new in a conversation, and when a room's conversation ends.

Shared by the simulation (world.py), which uses it as the morning happens, and by
metrics.py, which runs the old and new transcripts through the same rules afterwards.
Knows nothing about the house beyond room names and option ids.
"""

SPEECH = ("ask", "deny", "accuse", "confess", "reassure", "say")


def act_of(option):
    """(kind, target) of an option id. Kinds group options that are the same kind of act:
    reassuring one person or everyone is `reassure`, starting or carrying on a search is
    `search`. The target is a person for accuse, reassure and sit, a room for go."""
    if option == "ask_who":
        return "ask", None
    if option == "say_other":
        return "say", None
    if option == "reassure_all":
        return "reassure", None
    if option == "keep_searching":
        return "search", None
    for prefix in ("accuse", "reassure", "sit", "go", "aside"):
        if option.startswith(prefix + "_"):
            return prefix, option[len(prefix) + 1:]
    return option, None     # silent, deny, confess, search, eat, share


def aimed_at(option):
    """The person a line is aimed at, or None for a line to everyone in the room."""
    kind, target = act_of(option)
    return target if kind in ("accuse", "reassure", "aside") else None


class Newness:
    """Decides whether a spoken line adds something. New: a question, an accusation, a
    denial of a new accusation, a confession. Not new: reassurance, a stance the speaker
    has taken before this morning, and any other remark (the rules cannot read what free
    words add). New facts and people coming in are handled by the caller."""

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
        if kind == "reassure":
            return False, "reassurance"
        return False, "a remark (the rules cannot tell what free words add)"


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
