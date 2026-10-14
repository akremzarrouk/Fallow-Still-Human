"""The rules layer. Keeps the house, each person's memory, and lists what each of them
may do. Asks the model when something social has just happened to a person, or when
something inside them has risen since they last decided; every other turn is settled here.

Within a turn, the people in a room act one after another: whoever was just spoken to
(or just took someone aside) goes first, then whoever shows the strongest feeling, then
an order drawn from the seed. Each of them sees what was already said and done in the
room this turn. A room's conversation ends after two full turns in a row with nothing
new in it; after that only something new there is a social moment.

Inside each person the rules keep hunger, a suspicion (a person and a strength from 0 to
3), grudges (toward each person, 0 to 3, raised by what that person did to them) and, for
whoever took the can (the scenario says who, if anyone), guilt. The model is shown the
events behind them as plain facts, with at most a
neutral level word; the numbers themselves only decide when an inner moment comes.

A lull moment asks the model for someone nothing social or inner has happened to, when the
room they are in has been still for a while and they have not been asked for a while; their
prompt says since when nothing has been said or done there (reports/lull_design.md).

The trip concern (reports/trip_design.md): once the shelf is empty or someone first becomes very
hungry, everyone is told there is no food for tomorrow and that the neighbour's house may have
some, and each of them may take a position on whether someone goes there tonight. The rules
record the positions and decide nothing; nobody leaves the house.

Time passing (reports/night_design.md): a Morning is day 1 (house day 4) or day 2 (house day 5).
Day 2 starts from the people as the night left them (night.py), with what each of them carries
in as a block of facts outside the prompt budget, and words the trip's options anew.
"""
import json
import random
import re

import data
from talk import SPEECH, TRIP_WHY, Conversations, Newness, act_of, aimed_at

NAMES = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
CHOICES = [NAMES[p] for p in data.ORDER] + ["nobody"]

SYSTEM = (
    "You decide what one person in a family does in the next three minutes. You get who "
    "they are, what they remember, what they see now, and the options open to them. They "
    "know only what is in their memory. Choose exactly one option id from the list. If the "
    "option is marked (speech), `say` must hold the exact words they say, in their own voice, "
    "one or two short sentences. For any other option `say` is a short line they say while "
    "doing it, or null. `feeling` names what they feel right now in one or two words. "
    "`reason` is their reason in one sentence, as they would think it. `suspects` is who they "
    "now believe took the can, and `angry_at` is who they are angry with right now: each is "
    'one of "Daniel", "Elena", "Leo", "Mara" or "nobody". Reply with JSON only: '
    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
    '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
)
# The night's own (reports/night_design.md, §3.2): the same answer, decided for tonight, in a low voice.
NIGHT_SYSTEM = (
    "You decide what one person in a family does tonight. You get who they are, what they "
    "remember, what they know now, and the options open to them. They know only what is in their "
    "memory. Choose exactly one option id from the list. If the option is marked (speech), `say` "
    "must hold the exact words they say, in a low voice, in their own voice, one or two short "
    "sentences. For any other option `say` is null. `feeling` names what they feel right now in "
    "one or two words. `reason` is their reason in one sentence, as they would think it. "
    "`suspects` is who they now believe took the can, and `angry_at` is who they are angry with "
    "right now: each is one of \"Daniel\", \"Elena\", \"Leo\", \"Mara\" or \"nobody\". Reply with "
    'JSON only: {"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": '
    '"<sentence>", "suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
)
NIGHT_MINUTE = data.MINUTES     # the clock the night's answers keep (day 1 ends at minute 90)

# Feelings that reach the face, by how strongly they show. Others in the room see them,
# and someone who looks like this counts as upset nearby. Anything else (guilty, ashamed,
# anxious, tense...) stays inside and shows as 0.
SHOWN = {
    3: ("terrif", "panic", "hysteri", "frantic", "furious", "rage", "devastat", "desperat", "sob"),
    2: ("scared", "afraid", "fright", "angry", "anger", "hurt", "upset", "distress", "betray",
        "outrag", "humiliat", "cry", "tear", "shak", "wounded"),
    1: ("sad", "miserab"),
}
FEELING_SHOWS_FOR_TURNS = 3
PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,370 at most in the second step
QUIET_TURNS = 2              # full turns with nothing new that end a conversation
INNER_EVERY = 9              # minutes: an inner moment at most this often per person
FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one step this often
LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
                             # off since reports/lull_v9.md, 9 in reports/lull_design.md
LULL_EVERY = 12              # minutes since a person was last asked before a lull
TRIP_HUNGER = 2              # the hunger level ("very hungry") that starts the trip concern
TRIP_ON = True               # the trip concern (reports/trip_design.md); off only in tests
TRIP_KINDS = tuple(TRIP_WHY)  # propose, volunteer, object, back, decline
# The body's food moment on day 2 (reports/body_design.md, §2): the chance a turn, at impulsive 0.5,
# by when they last ate; and the minutes between one person's moments.
FOOD_RATE = {"before yesterday": 0.07, "yesterday": 0.035}
FOOD_EVERY = 30
FOOD_MOMENT_LINE = "You are starving, and there is food on the shelf in front of everyone."

KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
    "ask": "asked who took the can", "deny": "denied taking it",
    "accuse": "accused someone of taking it", "confess": "admitted taking it",
    "reassure": "reassured someone", "say": "said something else",
    "silent": "stayed put and said nothing", "search": "searched", "go": "gone to another room",
    "sit": "sat with someone", "eat": "eaten", "share": "shared out the food",
    "aside": "taken someone aside", "accept_aside": "gone aside with someone",
    "refuse_aside": "refused to go aside",
    "propose": "said someone should go to the neighbour's house tonight",
    "volunteer": "offered to go there tonight", "object": "said someone should not go",
    "back": "said someone should be the one to go", "decline": "said you will not be the one to go",
    "give": "given someone a portion", "eat_given": "eaten", "refuse_given": "refused a portion",
    "confront": "confronted someone",
}

HUNGER_WORDS = ["a little hungry", "hungry", "very hungry", "starving"]
LEVEL_WORDS = {1: "a little", 2: "some", 3: "a lot"}   # the only words a level is given
EVENTS_SHOWN = 4             # most recent events shown per grudge and for guilt


def estimate_tokens(text, less=0):
    """less: characters of `text` that do not count (the trip block, reports/trip_design.md §2.5)."""
    return int((len(text) - less) / 3.6) + 1


def strength(feeling):
    f = (feeling or "").lower()
    s = max((level for level, stems in SHOWN.items() if any(x in f for x in stems)), default=0)
    if s and re.search(r"\b(deeply|very|extremely|utterly|so)\b", f):
        s += 1
    return s


def outward(feeling):
    return strength(feeling) > 0


def hunger_level(h):
    return 0 if h < 0.5 else 1 if h < 0.7 else 2 if h < 0.85 else 3


def hunger_words(h):
    return HUNGER_WORDS[hunger_level(h)]


def trait_words(traits):
    out = []
    for name, v in traits.items():
        if v >= 0.75:
            out.append(f"very {name}")
        elif v >= 0.55:
            out.append(name)
        elif v >= 0.4:
            out.append(f"somewhat {name}")
        else:
            out.append(f"not {name}")
    return ", ".join(out)


class Track:
    """A suspicion or a grudge: one person and a strength from 0 to 3. Naming the same person
    again raises it a step. Naming nobody, or someone else, lets it fall a step, but never
    more than one step per FALL_EVERY minutes; once it is down to 0, the new name takes it."""

    def __init__(self):
        self.target, self.strength, self.last_fall = None, 0, None

    def report(self, who, minute):
        """who: a person id or None. Returns "rose", "fell", "held" or "same"."""
        if who is not None and (self.strength == 0 or who == self.target):
            if self.strength == 3:
                return "same"
            self.target, self.strength = who, self.strength + 1
            return "rose"
        if self.strength == 0:
            return "same"
        if self.last_fall is not None and minute - self.last_fall < FALL_EVERY:
            return "held"
        self.strength -= 1
        self.last_fall = minute
        if self.strength == 0:
            self.target = None
            if who is not None:
                self.target, self.strength = who, 1
        return "fell"

    def short(self, what):
        return f"{what} {NAMES[self.target]} {self.strength}/3" if self.strength else f"{what} none"

    def state(self):
        return [self.target, self.strength]


class Grudge:
    """What one person holds against another: a strength from 0 to 3 and the events that
    raised it. It falls a step only when FALL_EVERY minutes have passed since it last rose or
    fell, and only when an answer of theirs does not name that person."""

    def __init__(self):
        self.strength, self.last_change, self.events = 0, None, []

    def rise(self, minute, fact, kind="event"):
        """kind "event": something the rules saw them do; "angry": named in an answer."""
        self.events.append((minute, fact, kind))
        self.last_change = minute
        if self.strength < 3:
            self.strength += 1
            return True
        return False

    def may_fall(self, minute):
        if self.strength and (self.last_change is None or minute - self.last_change >= FALL_EVERY):
            self.strength -= 1
            self.last_change = minute
            return True
        return False


# Day 2, for whoever knows of no visit to the neighbour's house (reports/night_design.md, §5.3):
# after a night when anyone could have gone, "nobody has been inside since" is no longer certain.
NEIGHBOUR_UNKNOWN = ("About the neighbour's house: its people left in the first days, so there may be food "
                     "there. Outside is dangerous.")


def portions_text(n):
    return f"{n} portion{'s' if n != 1 else ''}"


def minutes_text(ms):
    ms = [f"{m:02d}" for m in ms]
    return ms[0] if len(ms) == 1 else ", ".join(ms[:-1]) + " and " + ms[-1]


def grudge_facts(name, events, limit=None):
    """The facts behind a grudge: each event the rules saw, then one line for the times the
    person named them as who they were angry with. On day 2 an event carried from day 1 or the
    night has a fourth element, "yesterday" or "last night" (reports/night_design.md, §5.3)."""
    facts = [e[1] for e in events if e[2] == "event"]
    angry = [e for e in events if e[2] == "angry"]
    if limit:
        facts, angry = facts[-limit:], angry[-limit:]
    if angry and all(len(e) == 3 for e in events):
        ms = [e[0] for e in angry]
        facts.append(f"you were angry with {name} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
    elif angry:
        parts = []
        for when in ("yesterday", "last night", "this morning"):
            ms = [e[0] for e in angry if (e[3] if len(e) > 3 else "this morning") == when]
            if not ms:
                continue
            parts.append(when if when == "last night" else
                         f"{when} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
        facts.append(f"you were angry with {name} " + "; and ".join(parts))
    return facts


def trip_option(kind, target):
    """The option id of a position on the trip."""
    if kind in ("propose", "volunteer", "decline"):
        return {"propose": "propose_trip"}.get(kind, kind)
    return f"{kind}_{target}" if target else "object_trip"


class Option:
    def __init__(self, id, label, speech=False, **act):
        self.id, self.label, self.speech, self.act = id, label, speech, act


class Person:
    def __init__(self, pid, scenario=data.DEFAULT_SCENARIO):
        d = data.PEOPLE[pid]
        culprit = data.culprit(scenario)
        self.id, self.name = pid, d["name"]
        self.sheet = d
        self.hunger = d["hunger"]
        self.room = "kitchen"
        self.activity = {"kind": "idle", "label": "standing at the pantry"}
        self.feeling, self.feeling_until = None, -1
        self.backstory = [f"Day {day}: {text} (you {how} it)" for day, text, who in data.backstory(scenario)
                          if (how := who.get(pid))]
        self.memory = []            # (minute, text) this morning, oldest first; trimmed to fit
        self.sure = []              # this morning's facts that are never trimmed
        self.said_lines = []        # their own spoken lines, oldest first, without the words
        self.triggers = []          # (text, is it new) social things since they last acted
        self.history = []           # one {"t", "kind", "seq"} per turn: what they did
        self.heard = []             # lines they heard: {"seq", "who", "kind", "target"}
        self.addressed = None       # the last line aimed at them since they last acted
        self.aside_lead = None      # whom they took aside last turn, if the other came
        self.searched = set()
        self.knows_culprit = culprit if pid == culprit else None
        self.can_note = data.about_the_can(scenario, pid)  # what else they know of the night, if anything
        self.confession_heard_at = None     # minute they first heard the culprit admit it
        self.heard_question = False
        self.confessed = False
        self.eaten = 0.0
        self.suspicion = Track()
        self.suspected_at = []      # minutes their answers named their current suspect
        self.grudges = {}           # person -> Grudge
        self.denials_heard = {}     # person -> minute they last heard that person deny it
        self.accused_by = {}        # person -> minute that person last accused them
        # Whoever took the can starts with guilt at 1: they know what they did.
        self.guilt = 1 if pid == culprit else None
        self.guilt_events = []      # (minute, fact)
        self.seen = None            # the levels they were shown when they last decided
        self.last_inner = None      # minute of their last inner moment
        self.last_asked = None      # minute of their last model decision of any kind
        # The trip: each speaker's latest position they heard (their own included), as
        # (minute, kind, target, seq); whether they have proposed it; whether they have heard or
        # made a proposal, an offer or a backing; and the day-2 memories never trimmed once it
        # has started.
        self.trip_heard = {}
        self.proposed = False
        self.trip_raised = False
        self.trip_memories = {x for x in self.backstory
                              if any(x.startswith(f"Day 2: {m} (") for m in data.TRIP_MEMORIES)}
        # Time passing (reports/night_design.md): what they did tonight, for the night's later
        # prompts; and on day 2, what of day 1 still counts as yesterday's (None on day 1).
        self.tonight = []
        self.yesterday = None
        # The food moment (reports/body_design.md, §2): the minute they last ate this morning; on day 2,
        # the minute of yesterday's last meal (None: not since before yesterday); their last moment.
        self.last_meal = None
        self.ate_yesterday = None
        self.last_food = None

    def grudge(self, against):
        return self.grudges.setdefault(against, Grudge())

    def levels(self):
        out = {"hunger": hunger_level(self.hunger), "suspicion": self.suspicion.strength,
               "grudges": {t: g.strength for t, g in self.grudges.items()}}
        if self.guilt is not None:
            out["guilt"] = self.guilt
        return out


class Morning:
    def __init__(self, oracle, seed=0, scenario=data.DEFAULT_SCENARIO, day=4):
        """day 4: the morning of the count (day 1). day 5: the next morning (day 2), which
        `Morning.next_day` sets up from day 1 and the night."""
        self.oracle = oracle
        self.day = day
        self.away = set()           # day 2: who did not come back in the night
        self.carry = {}             # day 2: person -> the carry-in block (reports/night_design.md, §5.2)
        self.neighbour = {}         # day 2: person -> their "About the neighbour's house:" line
        self.carried = {}           # day 2: person -> their opening, food and neighbour lines at minute 00
        self.trip_ids = []          # day 2: the option id of each trip act, in order
        self.seed = seed
        self.scenario = scenario
        self.culprit = data.culprit(scenario)       # who took the can, or None
        self.people = {p: Person(p, scenario) for p in data.ORDER}
        self.portions = data.PORTIONS
        self.start_portions = self.portions     # day 2 starts from the night's shelf
        self.turns = data.MINUTES // data.MINUTES_PER_TURN
        self.log = []               # one record per turn
        self.said = []              # every line spoken, in order
        self.max_prompt_tokens = 0
        self.seq = 0                # counts acts, in the order they happen
        self.newness = Newness()
        self.convos = Conversations(data.ROOMS, QUIET_TURNS)
        self.start_by_inner = []    # for each conversation start: did an inner moment cause it
        self.present = None         # during a turn: room -> who is still in it
        self.so_far = None          # during a turn: room -> what was said and done in it
        self.acted = None           # during a turn: who has already acted
        self.moves = None           # during a turn: (person, room, partner) to move at its end
        self.arrivals = []          # (room, name, by an inner moment) to count as new next turn
        self.moved_by_inner = {}    # during a turn: person -> did an inner moment move them
        self.transcript = {"seed": seed, "scenario": scenario, "culprit": self.culprit, "turns": []}
        self.convo_told = 0         # how much of the conversation log the turn records hold
        # room -> the minute something other than staying put in silence, or staying seated,
        # was last done in it (the count at minute 00 was done in the kitchen)
        self.last_stir = {"kitchen": 0}
        self.trip = None            # the trip concern once started: {"minute", "why", "asked"}
        self.trip_acts = []         # (minute, who, kind, target, words), every position taken
        self.trip_now = set()       # during the turn it starts: who is asked because of it
        self.food_turn = None       # day 2: the turn of the house's last food moment
        self.holding = None         # day 2: (who, from whom) while someone decides about a handed portion
        if day != 4:
            return                  # day 2's opening is set up by next_day
        for p in self.people.values():
            how = "did it" if p.id == "elena" else "saw it"
            p.sure.append(f"min 00: {data.OPENING} (you {how})")
            if p.id == self.culprit:
                p.sure.append("You know where the can went: you ate it yourself in the night, and nobody saw.")
            p.triggers.append(("the count came up short in front of everyone", True))
            p.seen = p.levels()
        self.started("kitchen", 0, "the count came up short", False)

    @classmethod
    def next_day(cls, day1, night, oracle):
        """Day 2, from day 1 and the night that followed it (reports/night_design.md, §5)."""
        import night as night_mod
        return night_mod.next_day(day1, night, oracle)

    def started(self, room, minute, why, by_inner):
        if self.convos.new_thing(room, minute, why):
            self.start_by_inner.append(by_inner)

    # ---------- who is where ----------
    def others_here(self, p):
        if self.present is not None:
            ids = self.present[p.room]
        else:
            ids = [q for q in data.ORDER if self.people[q].room == p.room]
        return [self.people[q] for q in ids if q != p.id]

    def talking(self, room):
        count = len(self.present[room]) if self.present is not None else \
            sum(q.room == room for q in self.people.values())
        return self.convos.active[room] and count >= 2

    def shown(self, q, t):
        return outward(q.feeling) and q.feeling_until >= t

    def empty_room(self, p):
        """Where p could take someone aside: an empty room, their own first, then the other
        private rooms, then the kitchen, then the bathroom. None if every room has someone."""
        def taken(r):
            if self.present is not None:
                return bool(self.present[r]) or any(to == r for _, to, _ in self.moves)
            return any(q.room == r for q in self.people.values())
        rank = {r: (0 if p.id in data.OWNERS.get(r, ()) else 1 if r in data.OWNERS
                    else 2 if r == "kitchen" else 3) for r in data.ROOMS}
        free = [r for r in data.ROOMS if r != p.room and not taken(r)]
        return min(free, key=lambda r: rank[r]) if free else None

    # ---------- what the rules allow ----------
    def repeating(self, p):
        """(kind, how many turns in a row) of their latest acts."""
        if not p.history:
            return None, 0
        kind, n = p.history[-1]["kind"], 0
        for h in reversed(p.history):
            if h["kind"] != kind:
                break
            n += 1
        return kind, n

    def options_for(self, p):
        opts = []
        others = self.others_here(p)
        room = data.ROOMS[p.room]
        opts.append(Option("silent", "stay put and say nothing", kind="silent"))
        if others:
            if not p.knows_culprit:
                opts.append(Option("ask_who", "ask everyone here who took the can", True, kind="ask"))
            # Once it has been admitted, it cannot be taken back: the one who admitted it no
            # longer denies it or blames anyone, and whoever heard it knows who it was.
            if p.heard_question and not p.confessed:
                opts.append(Option("deny", "deny taking it", True, kind="deny"))
            for q in others:
                if p.confessed or (p.knows_culprit and p.id != p.knows_culprit and q.id != p.knows_culprit):
                    continue
                opts.append(Option(f"accuse_{q.id}", f"accuse {q.name} of taking it", True,
                                   kind="accuse", target=q.id))
            if p.id == self.culprit and not p.confessed:
                opts.append(Option("confess", "admit taking it", True, kind="confess"))
            # From the night on, something someone did other than taking the can can be put to them
            # (reports/food_confront_impl.md); day 1 keeps its options, so it replays.
            if self.day != 4:
                for q in others:
                    opts.append(Option(f"confront_{q.id}", f"confront {q.name} about something they did", True,
                                       kind="confront", target=q.id))
            for q in others:
                if q.id in p.grudges and p.grudges[q.id].strength >= 3:
                    continue
                opts.append(Option(f"reassure_{q.id}", f"reassure {q.name}", True,
                                   kind="reassure", target=q.id))
            if len(others) > 1:
                opts.append(Option("reassure_all", "reassure everyone here", True, kind="reassure_all"))
            opts += self.trip_options(p, others)
            opts.append(Option("say_other", "say something else", True, kind="say"))
            for q in others:
                if q.activity["kind"] in ("searching", "walking"):
                    continue
                sitting = p.activity["kind"] == "sitting" and p.activity["with"] == q.id
                opts.append(Option(f"sit_{q.id}", ("keep sitting with " if sitting else "sit with ") + q.name,
                                   kind="sit", target=q.id))
            # Taking someone aside: only someone who has not acted yet this turn (their answer
            # is their decision for the turn), and only to a room with nobody in it.
            aside = self.empty_room(p)
            for q in others:
                if aside and (self.acted is None or q.id not in self.acted):
                    opts.append(Option(f"aside_{q.id}", f"take {q.name} aside to the {data.ROOMS[aside]}",
                                       kind="aside", target=q.id, to=aside))
        # Nobody searches for a can they have heard admitted to, or admitted to themselves.
        settled = p.confessed or (p.knows_culprit and p.knows_culprit != p.id)
        if p.activity["kind"] == "searching" and not settled:
            opts.append(Option("keep_searching", f"carry on searching the {room}", kind="keep_searching"))
        elif p.activity["kind"] != "searching" and p.room not in p.searched and not settled:
            opts.append(Option("search", f"search the {room} for the can (takes about six minutes)",
                               kind="search"))
        for r in data.ROOMS:
            if r != p.room:
                opts.append(Option(f"go_{r}", f"go to the {data.ROOMS[r]}", kind="go", to=r))
        if p.room == "kitchen" and self.portions > 0:
            opts.append(Option("eat", "eat one of the portions", kind="eat"))
            if others:
                opts.append(Option("share", "share out what is left among everyone here", kind="share"))
        # A speech act used three turns in a row is not offered a fourth time.
        kind, n = self.repeating(p)
        if kind in SPEECH and n >= 3:
            opts = [o for o in opts if act_of(o.id)[0] != kind]
        return opts

    def trip_options(self, p, others):
        """The positions on the trip open to them (reports/trip_design.md, §3.1): none before it
        has started; never the position they already hold."""
        if self.trip is None:
            return []
        if self.day != 4:
            return self.trip_options_day2(p, others)
        pos = p.trip_heard.get(p.id)
        own = pos[1:3] if pos else None
        out = []
        if not p.proposed:
            out.append(Option("propose_trip", "say someone should go to the neighbour's house tonight", True,
                              kind="propose"))
        if own != ("volunteer", None):
            out.append(Option("volunteer", "offer to go there tonight yourself", True, kind="volunteer"))
        if p.trip_raised and own != ("object", None):
            out.append(Option("object_trip", "say nobody should go out tonight", True, kind="object"))
        for q in others:
            if own != ("back", q.id):
                out.append(Option(f"back_{q.id}", f"say {q.name} should be the one to go", True,
                                  kind="back", target=q.id))
        for q in others:
            if self.named_to_go(p, q.id) and own != ("object", q.id):
                out.append(Option(f"object_{q.id}", f"say {q.name} should not be the one to go", True,
                                  kind="object", target=q.id))
        backed = any(v[1:3] == ("back", p.id) for w, v in p.trip_heard.items() if w != p.id)
        if (backed or own == ("volunteer", None)) and own != ("decline", None):
            out.append(Option("decline", "say you will not be the one to go", True, kind="decline"))
        return out

    def trip_options_day2(self, p, others):
        """Day 2's wording of the same positions (reports/night_design.md, §6): ids that carry
        their meaning, labels that share no verb, for going first and against after, and
        `still_going` in place of `volunteer` while the offer is their position. When each is
        offered is as on day 1."""
        pos = p.trip_heard.get(p.id)
        own = pos[1:3] if pos else None
        out = []
        if not p.proposed:
            out.append(Option("propose_trip", "say someone should go to the neighbour's house tonight", True,
                              kind="propose"))
        if own != ("volunteer", None):
            out.append(Option("volunteer", "offer to go there tonight yourself", True, kind="volunteer"))
        else:
            out.append(Option("still_going", "say you still mean to go there tonight", True, kind="volunteer"))
        for q in others:
            if own != ("back", q.id):
                out.append(Option(f"send_{q.id}", f"say {q.name} is the one who should go there tonight", True,
                                  kind="back", target=q.id))
        if p.trip_raised and own != ("object", None):
            out.append(Option("nobody_goes", "say nobody should go out tonight", True, kind="object"))
        for q in others:
            if self.named_to_go(p, q.id) and own != ("object", q.id):
                out.append(Option(f"keep_{q.id}_home", f"say {q.name} must stay home tonight", True,
                                  kind="object", target=q.id))
        backed = any(v[1:3] == ("back", p.id) for w, v in p.trip_heard.items() if w != p.id)
        if (backed or own == ("volunteer", None)) and own != ("decline", None):
            out.append(Option("refuse_to_go", "say you yourself will not go", True, kind="decline"))
        return out

    @staticmethod
    def named_to_go(p, q):
        """As far as p has heard: q offered to go, or someone backed q since q last said they
        will not go."""
        pos = p.trip_heard.get(q)
        if pos and pos[1] == "volunteer":
            return True
        declined = pos[3] if pos and pos[1] == "decline" else -1
        return any(v[1:3] == ("back", q) and v[3] > declined for w, v in p.trip_heard.items() if w != q)

    def start_trip(self, minute):
        """At the start of a turn: the trip concern starts if the shelf is empty or someone is
        very hungry, once per morning. Returns who is asked because of it this turn."""
        if not TRIP_ON or self.trip is not None:
            return set()
        why, asked = [], set()
        if self.portions == 0:
            why.append("the shelf is empty")
            asked |= {q for q in data.ORDER if self.people[q].room == "kitchen"}
        for q in data.ORDER:
            if hunger_level(self.people[q].hunger) >= TRIP_HUNGER:
                why.append(f"{NAMES[q]} is {HUNGER_WORDS[TRIP_HUNGER]}")
                asked.add(q)
        if not why:
            return set()
        self.trip = {"minute": minute, "why": why, "asked": [q for q in data.ORDER if q in asked]}
        return asked

    def heard_plan(self, p):
        """The positions on the trip they heard, each speaker's latest, oldest first; None if
        they have heard none (reports/trip_design.md, §4.2)."""
        if not p.trip_heard:
            return None
        parts = []
        for who, heard in sorted(p.trip_heard.items(), key=lambda kv: kv[1][3]):
            minute, kind, target = heard[:3]
            option = heard[4] if len(heard) > 4 else None       # day 2 keeps the option id
            x = "you" if who == p.id else NAMES[who]
            he = "you" if who == p.id else data.PRONOUNS[who]["he"]
            q = None if target is None else "you" if target == p.id else NAMES[target]
            if kind == "propose":
                said = f"{x} said someone should go"
            elif option == "still_going":
                said = f"{x} said {he} still {'mean' if who == p.id else 'means'} to go"
            elif kind == "volunteer":
                said = f"{x} offered to go"
            elif kind == "object":
                said = (f"{x} said nobody should go" if q is None else f"{x} said {q} must stay home"
                        if option else f"{x} said {q} should not go")
            elif kind == "back":
                said = f"{x} said {q} is the one who should go" if option else f"{x} said {q} should go"
            else:
                said = f"{x} said {he} will not go"
            parts.append(f"{said} (min {minute:02d})")
        return "About going there tonight: " + "; ".join(parts) + "."

    def trip_lines(self, p):
        """What the trip concern adds after their "About the can:" line. On day 2 the food and
        the neighbour's house are as the night left them (reports/night_design.md, §5.3)."""
        if self.trip is None:
            return []
        plan = self.heard_plan(p)
        if self.day != 4:
            return [self.food_line(p), self.neighbour.get(p.id, NEIGHBOUR_UNKNOWN)] + ([plan] if plan else [])
        return [data.ABOUT_FOOD, data.ABOUT_NEIGHBOUR] + ([plan] if plan else [])

    def food_line(self, p=None):
        """Day 2's "About food:" line: what the shelf holds, and what that means for those here. For
        whoever is deciding about a portion just handed to them (reports/body_fix.md), the line also
        says they hold it and who handed it, and what it means counts that portion too."""
        n = self.portions
        k = sum(q.room is not None for q in self.people.values())
        held = p is not None and self.holding is not None and self.holding[0] == p.id
        if held:
            n += 1
        if n == 0:
            so = "there is nothing to eat today"
        elif n < k:
            so = "there is not one portion each"
        elif n // k == 1:
            so = "there is one portion each, and nothing after that"
        else:
            so = f"there are {n // k} portions each, and nothing after that"
        if held:
            return (f"About food: the shelf holds {portions_text(self.portions)}, and you hold the portion "
                    f"{NAMES[self.holding[1]]} has just handed you; there is no other food in the house, so {so}.")
        return f"About food: the shelf holds {portions_text(n)}, and there is no other food in the house, so {so}."

    def plan_text(self):
        """The state of the plan for tonight, from every position taken (reports/trip_design.md,
        §4.3): who has offered to go, then each other person's latest position."""
        if not self.trip_acts:
            return "no plan"
        latest = {}
        for _, who, kind, target, _ in self.trip_acts:
            latest.pop(who, None)
            latest[who] = (kind, target)
        going = [NAMES[w] for w, (kind, _) in latest.items() if kind == "volunteer"]
        if len(going) == 1:
            parts = [f"{going[0]} will go"]
        elif len(going) == 2:
            parts = [f"{going[0]} and {going[1]} have both offered to go"]
        elif going:
            parts = [f"{', '.join(going[:-1])} and {going[-1]} have all offered to go"]
        else:
            parts = ["nobody has offered to go"]
        for who, (kind, target) in latest.items():
            x = NAMES[who]
            if kind == "propose":
                parts.append(f"{x} said someone should go")
            elif kind == "back":
                parts.append(f"{x} wants {NAMES[target]} to go")
            elif kind == "object":
                parts.append(f"{x} is against anyone going" if target is None else
                             f"{x} is against {NAMES[target]} going")
            elif kind == "decline":
                parts.append(f"{x} will not go")
        return "; ".join(parts)

    def routine(self, p, opts):
        """No model: carry on with what they were doing, or stay put."""
        ids = {o.id for o in opts}
        if p.activity["kind"] == "searching" and "keep_searching" in ids:
            return "keep_searching"
        if p.activity["kind"] == "sitting" and f"sit_{p.activity['with']}" in ids:
            return f"sit_{p.activity['with']}"
        return "silent"

    # ---------- the body's food moment (reports/body_design.md, §2) ----------
    def food_band(self, p):
        """When they last ate, from their own records: "this morning", "yesterday" or "before yesterday"."""
        if p.eaten > 0:
            return "this morning"
        return "yesterday" if p.ate_yesterday is not None else "before yesterday"

    def food_chance(self, p):
        """The chance a turn: the band's rate × (0.5 + impulsive) (§2.2); 0 once they have eaten this morning."""
        band = self.food_band(p)
        if band == "this morning":
            return 0
        return round(FOOD_RATE[band] * (0.5 + p.sheet["traits"]["impulsive"]), 4)

    def food_draw(self, t, pid):
        """This person's draw for this turn (F9): a string of its own, so no draw depends on order."""
        return random.Random(f"{self.seed}:day2:food:{t}:{pid}").random()

    def food_due(self, p, t):
        """F1-F9 (§2.1): day 2, in the kitchen with food on the shelf and someone else there, starving,
        nothing eaten this morning, no moment of theirs in FOOD_EVERY minutes or of anyone's this turn,
        and their draw under their chance. Answers to an aside or a give never come here (F8)."""
        if self.day == 4 or p.room != "kitchen" or self.portions <= 0 or not self.others_here(p):
            return False
        if hunger_level(p.hunger) < 3 or p.eaten > 0:
            return False
        minute = t * data.MINUTES_PER_TURN
        if p.last_food is not None and minute - p.last_food < FOOD_EVERY:
            return False
        if self.food_turn == t:
            return False
        return self.food_draw(t, p.id) < self.food_chance(p)

    def food_options(self, p):
        """Food only (§2.4): eat, give a portion to each person here in the family's order, share."""
        return ([Option("eat", "eat one of the portions", kind="eat")]
                + [Option(f"give_{q.id}", f"give one of the portions to {q.name}", kind="give", target=q.id)
                   for q in self.others_here(p)]
                + [Option("share", "share out what is left among everyone here", kind="share")])

    @staticmethod
    def food_moment_line(p):
        """The moment's last `Now` line: only the situation, so the choice stays the person's
        (reports/food_wording_probe.md, variant B; reports/food_confront_impl.md)."""
        return FOOD_MOMENT_LINE

    def decide_food(self, p, t):
        """A food moment: it takes the place of their decision this turn. An answer that cannot be used
        leaves them where they are and the food on the shelf (§2.7)."""
        minute = t * data.MINUTES_PER_TURN
        opts = self.food_options(p)
        triggers = self.social_triggers(p, t)
        p.triggers = []
        d = {"person": p.id, "triggers": triggers, "offered": len(opts), "held_back": None,
             "food_moment": {"band": self.food_band(p), "chance": self.food_chance(p),
                             "draw": self.food_draw(t, p.id), "portions": self.portions}}
        p.last_food = minute
        self.food_turn = t
        choice, why = self.ask_model(p, t, opts, d, self.food_moment_line(p))
        if not choice:
            opts = opts + [Option("silent", "stay put and say nothing", kind="silent")]
            d.update(mode="fallback", invalid=why, option="silent", say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    def decide_given(self, q, p, t):
        """q has just been handed a portion by p: eat it, or put it back (§2.5). Always a model decision;
        an answer that cannot be used puts it back."""
        opts = [Option("eat_given", f"eat the portion {p.name} gave you", kind="eat_given", partner=p.id),
                Option("refuse_given", "refuse it, and put it back on the shelf", kind="refuse_given", partner=p.id)]
        handed = f"{p.name} hands you one of the portions"
        triggers = [handed] + [text for text, new in q.triggers if text != handed]
        q.triggers = []
        d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts),
             "held_back": None, "given_by": p.id}
        self.holding = (q.id, p.id)             # while q decides, the portion is in q's hand
        choice, why = self.ask_model(q, t, opts, d, f"{p.name} has just handed you one of the portions.")
        self.holding = None
        if not choice:
            d.update(mode="fallback", invalid=why, option="refuse_given", say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    # ---------- what is inside them ----------
    def risen(self, p):
        """What has risen a level since they last decided with the model: "hunger", "guilt",
        "suspicion", or "grudge:<person>" for each grudge that rose."""
        now, seen = p.levels(), p.seen
        out = [k for k in ("hunger", "guilt", "suspicion") if k in now and now[k] > seen[k]]
        out += [f"grudge:{t}" for t in data.ORDER
                if now["grudges"].get(t, 0) > seen["grudges"].get(t, 0)]
        return out

    def rise_words(self, p, kinds):
        """What rose, for the story."""
        out = []
        for k in kinds:
            if k == "hunger":
                out.append(f"hunger rose (now {hunger_words(p.hunger)})")
            elif k == "guilt":
                out.append(f"guilt rose (now {p.guilt} of 3)")
            elif k == "suspicion":
                out.append(f"suspicion of {NAMES[p.suspicion.target]} rose (now {p.suspicion.strength} of 3)")
            else:
                t = k.split(":")[1]
                out.append(f"grudge against {NAMES[t]} rose (now {p.grudges[t].strength} of 3)")
        return out

    def add_guilt(self, minute, fact, story, record):
        """An event that weighs on whoever took the can. It is always remembered as a fact; the
        counter only decides when an inner moment comes, and stops at 3."""
        culprit = self.people[self.culprit]
        culprit.guilt_events.append((minute, fact))
        if culprit.guilt < 3:
            culprit.guilt += 1
        record["guilt"].append((minute, culprit.guilt, story))

    def add_grudge(self, holder, against, minute, fact, story, record):
        """Something `against` did to `holder`. Remembered as a fact, and a step up."""
        holder.grudge(against.id).rise(minute, fact)
        record["grudges"].append((minute, holder.id, against.id, holder.grudges[against.id].strength, story))

    # ---------- what is inside them, as the prompt says it ----------
    def inside_lines(self, p):
        """Hunger in words; suspicion, grudges and guilt as the events behind them."""
        out = [f"Your body: {hunger_words(p.hunger)}."]
        if "hunger" in self.risen(p):
            out.append("Since you last decided, you have grown hungrier.")
        s = p.suspicion
        y = p.yesterday             # day 2 only (reports/night_design.md, §5.3)
        # What they know about the can wins over what their answers guessed.
        if p.knows_culprit == p.id:
            about = ("About the can: you ate it yourself, and you admitted it yesterday." if y and y["confessed"]
                     else "About the can: you ate it yourself.")
        elif p.knows_culprit and y and y["confession_heard"]:
            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it yesterday, at minute "
                     f"{p.confession_heard_at:02d}.")
        elif p.knows_culprit:
            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
                     f"{p.confession_heard_at:02d}.")
        elif s.strength and y is not None:
            when = []
            for word, ms in (("yesterday", y["suspected_at"]), ("last night", y["suspected_last_night"]),
                             ("this morning", p.suspected_at)):
                if ms is True:
                    when.append(word)
                elif ms:
                    ms = ms[-EVENTS_SHOWN:]
                    when.append(f"{word} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
            about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it"
                     + (", " + ", and ".join(when) if when else "") + ".")
        elif s.strength:
            about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
                     f"at minute{'s' if len(p.suspected_at) > 1 else ''} "
                     f"{minutes_text(p.suspected_at[-EVENTS_SHOWN:])}.")
        else:
            about = "About the can: you have not settled on who took it."
        out.append(f"{about} {p.can_note}" if p.can_note else about)
        out += self.trip_lines(p)
        held = [(t, p.grudges[t]) for t in data.ORDER if t in p.grudges and p.grudges[t].strength]
        if not held:
            out.append("Against the others: nothing.")
        for t, g in held:
            facts = "; ".join(grudge_facts(NAMES[t], g.events, EVENTS_SHOWN))
            out.append(f"Against {NAMES[t]} ({LEVEL_WORDS[g.strength]}): {facts}.")
        if p.guilt is not None:
            facts = ["you ate the can in the night, and nobody saw"]
            facts += [fact for _, fact in p.guilt_events[-EVENTS_SHOWN:]]
            out.append(f"On your conscience ({LEVEL_WORDS[p.guilt]}): " + "; ".join(facts) + ".")
        return out

    # ---------- the prompt ----------
    def pattern(self, p):
        """How many turns in a row they have done the same kind of act, and how the others
        answered them in that time (lines aimed at them or at everyone)."""
        kind, n = self.repeating(p)
        if not n:
            return []
        first = p.history[-n]["seq"]
        out = [f"What you have been doing: you have {KIND_DONE[kind]}, {n} turn{'s' if n > 1 else ''} in a row."]
        replies = {}
        for h in p.heard:
            if h["seq"] > first and h["who"] != p.id and h["target"] in (p.id, None):
                replies.setdefault(h["who"], []).append(h)
        if not replies:
            out.append("In that time nobody has said anything to you or to everyone.")
            return out
        parts, changed = [], []
        for who, hs in replies.items():
            name = self.people[who].name
            verbs = [self.heard_verb(h, p) for h in hs]
            parts.append(f"{name} {', then '.join(verbs)}")
            if len(set(verbs)) > 1:
                changed.append(name)
        out.append("In that time: " + "; ".join(parts) + ".")
        out.append(("Answered you differently from one time to the next: " + ", ".join(changed) + ".")
                   if changed else "Nobody answered you differently from one time to the next.")
        return out

    def heard_verb(self, h, listener):
        target = "you" if h["target"] == listener.id else None
        return {"ask": "asked who took the can", "deny": "denied taking it",
                "accuse": f"accused {target or 'someone'}", "confess": "admitted taking it",
                "confront": f"confronted {target or 'someone'}",
                "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone",
                "propose": "said someone should go to the neighbour's house tonight",
                "volunteer": "offered to go there tonight",
                "object": "said you should not be the one to go" if target else "said nobody should go",
                "back": "said you should be the one to go", "decline": "said they will not be the one to go",
                }.get(h["kind"], "spoke to everyone")

    def prompt_for(self, p, t, opts, lull=None, night=None, extra=None):
        """lull: for a lull moment, the minute the room was last stirred; None otherwise.
        night: the night's `Now` lines (reports/night_design.md, §3.2), which take the place of the
        room, the turn and the pattern block; None by day.
        extra: by day, a last `Now` line (a food moment's, or a handed portion's: reports/body_design.md,
        §2.4-§2.5); None otherwise."""
        s = p.sheet
        minute = None if night is not None else t * data.MINUTES_PER_TURN
        system = SYSTEM if night is None else NIGHT_SYSTEM
        calls = "; ".join(f"{self.people[q].name} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
        inside = self.inside_lines(p)
        head = [
            f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; "
            f"Daniel, 25; Leo, 21; Mara, 17).",
            f"How you address them: {calls}.",
            f"Who you are: {s['note']}",
            f"Temperament: {trait_words(s['traits'])}.",
            f"What matters to you: {', '.join(s['values'])}.",
        ] + inside
        house = (data.HOUSE_THINGS_NIGHT if night is not None
                 else data.HOUSE_THINGS_AFTER_TRIP if self.trip else data.HOUSE_THINGS)
        head += [f"The house: {data.HOUSE} {house}"]
        if night is not None:
            return self.prompt_parts(p, opts, head, list(night), system, "today", minute)
        room = data.ROOMS[p.room]
        now = [f"Now, minute {minute:02d}, you are in the {room}."]
        others = self.others_here(p)
        if not others:
            now.append("- Nobody else is here.")
        for q in others:
            look = f" {q.name} looks {q.feeling}." if self.shown(q, t) else ""
            now.append(f"- {q.name} is here, {q.activity['label']}.{look}")
        if p.room == "kitchen":
            now.append(f"- {self.portions} portion{'s' if self.portions != 1 else ''} on the shelf.")
        if lull is not None:
            now.append(f"Nothing has been said or done in the {room} since minute {lull:02d}.")
        so_far = self.so_far[p.room] if self.so_far is not None else []
        if so_far:
            now.append(f"Said and done in the {room} this turn, before you, in order:")
            now += [f"{i}. {x}" for i, x in enumerate(so_far, 1)]
        elif others:
            now.append(f"You are the first to act in the {room} this turn.")
        now += self.pattern(p)
        if extra:
            now.append(extra)
        return self.prompt_parts(p, opts, head, now, system, "this morning", minute)

    def prompt_parts(self, p, opts, head, now, system, when, minute):
        """The rest of the prompt, trimmed to the budget. when: "this morning", or "today" at
        night (reports/night_design.md, §3.2)."""
        tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]

        back = list(p.backstory)
        morning = [f"min {m:02d}: {x}" for m, x in p.memory if m != minute]  # this turn is above
        morning += [f"tonight: {x}" for x in p.tonight]
        pinned = [f"What you are sure of {'from today' if when == 'today' else when}:"] + [f"- {x}" for x in p.sure]
        if p.said_lines:
            pinned += [f"Your own last words {when}:"] + [f"- {x}" for x in p.said_lines[-3:]]
        carry = self.carry.get(p.id, [])
        # Once the trip concern has started, its block sits outside the budget
        # (reports/trip_design.md, §2.5): its lines, its options, the day-2 memories it keeps from
        # trimming, and "this morning" in the house line. `block` counts its characters. On day 2
        # the carry-in block sits outside the budget too (reports/night_design.md, §5.4).
        keep = p.trip_memories if self.trip else set()
        block = 0
        if self.trip:
            house = head[-1][len(f"The house: {data.HOUSE} "):]
            block += sum(len(x) + 1 for x in self.trip_lines(p))
            block += sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in TRIP_KINDS)
            block += sum(len(f"- {x}") + 1 for x in keep)
            block += max(0, len(house) - len(data.HOUSE_THINGS))
        block += sum(len(x) + 1 for x in carry)
        cut = False
        while True:
            parts = head + ["What you remember from the days before:"] + [f"- {x}" for x in back]
            parts += carry + pinned + [f"What else happened {when}, most recent last:"]
            parts += (["- (earlier things, left out here)"] if cut else [])
            parts += [f"- {x}" for x in morning] or ([] if cut else ["- nothing else yet"])
            parts += now + tail
            text = "\n".join(parts)
            loose = [x for x in back if x not in keep]      # all of them, before the trip
            if estimate_tokens(system + text, block) <= PROMPT_TOKEN_BUDGET or (not morning and not loose):
                break
            cut = True
            if len(morning) > 8:
                morning.pop(0)
            elif len(loose) > 4:
                back.remove(loose[0])
            elif morning:
                morning.pop(0)
            else:
                back.remove(loose[0])
        self.max_prompt_tokens = max(self.max_prompt_tokens, estimate_tokens(system + text))
        return text

    # ---------- reading the answer ----------
    @staticmethod
    def parse(text, opts):
        """Returns (choice dict, None) or (None, why it cannot be used)."""
        raw = (text or "").strip()
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
        try:
            ans = json.loads(raw)
        except ValueError:
            return None, "not JSON"
        if not isinstance(ans, dict):
            return None, "not a JSON object"
        for field in ("option", "feeling", "reason"):
            if not isinstance(ans.get(field), str) or not ans[field].strip():
                return None, f"no `{field}`"
        if "say" not in ans or not (ans["say"] is None or isinstance(ans["say"], str)):
            return None, "no `say`"
        named = {}
        for field in ("suspects", "angry_at"):
            value = ans.get(field)
            match = next((c for c in CHOICES if isinstance(value, str) and value.strip().lower() == c.lower()), None)
            if match is None:
                return None, f"`{field}` is not one of the family or nobody"
            named[field] = match
        byid = {o.id: o for o in opts}
        opt = byid.get(ans["option"].strip())
        if opt is None:
            return None, f"option `{ans['option']}` was not offered"
        say = " ".join((ans["say"] or "").split()).strip().strip('"').strip() or None
        if say and say.lower() in ("null", "none"):
            say = None
        if opt.speech and not say:
            return None, f"`{opt.id}` is speech but no words were given"
        dropped = False
        if opt.id == "silent" and say:
            say, dropped = None, True
        return {"option": opt.id, "say": say, "feeling": " ".join(ans["feeling"].split()).lower(),
                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped, **named}, None

    # ---------- one turn ----------
    def run(self):
        for t in range(self.turns):
            self.turn(t)
        self.finish()
        return self

    def finish(self):
        """What the transcript needs once the morning is over."""
        self.transcript["final_rooms"] = {r: [q for q in data.ORDER if self.people[q].room == r]
                                          for r in data.ROOMS}
        self.transcript["final_state"] = {
            p.id: {"suspicion": p.suspicion.state(),
                   "grudges": {t: {"strength": g.strength, "events": [list(e) for e in g.events]}
                               for t, g in p.grudges.items()},
                   "guilt": p.guilt, "guilt_events": [list(e) for e in p.guilt_events]}
            for p in self.people.values()}
        by_inner = iter(self.start_by_inner)
        self.transcript["convo_log"] = [
            {"minute": m, "room": r, "what": what, "why": why,
             "by_inner": next(by_inner) if what == "started" else None}
            for m, r, what, why in self.convos.log]
        # The trip concern (reports/trip_design.md, §4.1), or None if it never started.
        ids = (self.trip_ids if self.day != 4 else
               [trip_option(kind, target) for _, _, kind, target, _ in self.trip_acts])
        self.transcript["trip"] = None if self.trip is None else {
            **self.trip,
            "acts": [[m, who, i, words] for (m, who, _, _, words), i in zip(self.trip_acts, ids)],
            "plan": self.plan_text()}
        if self.day != 4:
            # Day 2 (reports/night_design.md, §8): who is away, and what each person carried in.
            self.transcript["away"] = [q for q in data.ORDER if q in self.away]
            self.transcript["carry_in"] = {q: list(lines) for q, lines in self.carry.items()}

    def social_triggers(self, p, t):
        """What counts now: anything new; anything else only while the room is talking."""
        talking = self.talking(p.room)
        found = list(dict.fromkeys(text for text, new in p.triggers if new or talking))
        if talking:
            for q in self.others_here(p):
                if self.shown(q, t):
                    found.append(f"{q.name} looks {q.feeling}")
        return found

    def next_to_act(self, remaining, t, draw):
        """Who acts next in a room, and why them."""
        def key(pid):
            q = self.people[pid]
            a = q.addressed
            first = a or q.aside_lead
            return (0 if first else 1, -(a["seq"] if a else 0), -strength(q.feeling) * self.shown(q, t), draw[pid])
        pid = min(remaining, key=key)
        q = self.people[pid]
        rest = [self.people[x] for x in remaining if x != pid]
        if q.addressed:
            how = "accused" if q.addressed["accused"] else "spoken to"
            return pid, f"just {how} by {self.people[q.addressed['who']].name}"
        if q.aside_lead:
            return pid, f"took {self.people[q.aside_lead].name} aside"
        if not rest:
            return pid, "the only one left to act here"
        mine = strength(q.feeling) * self.shown(q, t)
        if mine > max(strength(o.feeling) * self.shown(o, t) for o in rest):
            return pid, f"shows the strongest feeling here ({q.feeling})"
        return pid, "drawn by the seed among equals"

    def turn(self, t):
        minute = t * data.MINUTES_PER_TURN
        record = {"minute": minute, "decisions": [], "events": [], "convo": [], "guilt": [],
                  "grudges": []}
        self.trip_now = self.start_trip(minute)     # before anyone acts (reports/trip_design.md, §1)
        for room, name, by_inner in self.arrivals:
            self.started(room, minute, f"{name} came in", by_inner)
        self.arrivals = []
        start_room = {p.id: p.room for p in self.people.values()}
        self.present = {r: [q for q in data.ORDER if start_room[q] == r] for r in data.ROOMS}
        at_start = {r: len(v) for r, v in self.present.items()}
        self.so_far = {r: [] for r in data.ROOMS}
        self.acted, self.moves = set(), []
        tturn = {"minute": minute, "rooms": {r: list(v) for r, v in self.present.items()}, "acts": []}
        voices = []

        def act(p, d, room, place, why):
            d.update(room=room, place=place, order_reason=why)
            opt = d.pop("_opt")
            audience = [q.id for q in self.others_here(p)]
            self.acted.add(p.id)
            d["came_of_it"] = self.apply(p, opt, d, t, voices, record)
            record["decisions"].append(d)
            entry = {"minute": minute, "who": p.id, "room": room, "option": d["option"],
                     "words": d.get("say"), "audience": audience, "mode": d["mode"],
                     "decided_at": [minute, d["seq"]], "said_at": [minute, d["seq"]],
                     "came_of_it": d["came_of_it"], "new": d.get("new"), "new_why": d.get("new_why"),
                     "inner": d.get("inner_families"), "suspects": d.get("suspects"),
                     "angry_at": d.get("angry_at"), "lull": d.get("lull"),
                     "trip_moment": d.get("trip_moment"),
                     "moved_to": opt.act["to"] if opt.act["kind"] in ("go", "accept_aside") else None}
            if d.get("food_moment"):
                entry["food_moment"] = d["food_moment"]
            tturn["acts"].append(entry)
            return opt, entry

        for room in data.ROOMS:
            remaining = list(self.present[room])
            rng = random.Random(f"{self.seed}:{t}:{room}")
            draw = {q: rng.random() for q in data.ORDER}
            place = 0
            while remaining:
                pid, why = self.next_to_act(remaining, t, draw)
                remaining.remove(pid)
                place += 1
                p = self.people[pid]
                d = self.decide(p, t)
                opt, entry = act(p, d, room, place, why)
                if opt.act["kind"] == "aside":
                    # The one taken aside answers now; it is their decision for this turn.
                    q = self.people[opt.act["target"]]
                    remaining.remove(q.id)
                    place += 1
                    dq = self.decide_aside(q, p, opt.act["to"], t)
                    qopt, _ = act(q, dq, room, place, f"asked aside by {p.name}")
                    went = qopt.id == "accept_aside"
                    d["came_of_it"] += f" {q.name} {'went with them' if went else 'refused'}."
                    entry["came_of_it"] = d["came_of_it"]
                    entry["aside"] = {"with": q.id, "accepted": went}
                    if went:
                        entry["moved_to"] = opt.act["to"]
                elif opt.act["kind"] == "give":
                    # The one handed a portion answers now (reports/body_design.md, §2.5): their decision
                    # for this turn if they had not acted yet, otherwise an extra answer.
                    q = self.people[opt.act["target"]]
                    if q.id in remaining:
                        remaining.remove(q.id)
                    place += 1
                    dq = self.decide_given(q, p, t)
                    qopt, _ = act(q, dq, room, place, f"handed a portion by {p.name}")
                    d["came_of_it"] += f" {q.name} {'ate it' if qopt.id == 'eat_given' else 'put it back on the shelf'}."
                    entry["came_of_it"] = d["came_of_it"]
        record["rooms"] = {r: [(q.name, q.activity["label"]) for q in self.people.values()
                               if start_room[q.id] == r] for r in data.ROOMS}

        for p, to, partner in self.moves:
            p.room = to
            p.activity = {"kind": "idle", "label": "just come in"}
            self.last_stir[to] = minute         # coming in is something done in the room
        # Voices carry to everyone who did not hear the words, wherever they are at the end of
        # the turn, never into or out of the bathroom. Only a new line is a social moment for
        # someone who hears it through a wall.
        for room, new, heard_it in voices:
            for q in self.people.values():
                if q.id in heard_it or q.room == room or q.room is None or data.SOUNDPROOF & {room, q.room}:
                    continue
                line = f"Voices from the {data.ROOMS[room]}"
                if (minute, line + ".") not in q.memory:
                    q.memory.append((minute, line + "."))
                if new:
                    q.triggers.append((line, True))
        for p, to, partner in self.moves:
            there = [q for q in self.people.values() if q.room == to and q.id != p.id]
            for q in there:
                if q.id == partner:
                    text = f"You and {p.name} are in the {data.ROOMS[to]}, away from the others"
                else:
                    text = f"{p.name} comes into the {data.ROOMS[to]}"
                self.perceive(q, minute, text + ".", trigger=(text, True))
            if there:
                self.arrivals.append((to, p.name, self.moved_by_inner.get(p.id, False)))
        at_end = {r: sum(q.room == r for q in self.people.values()) for r in data.ROOMS}
        self.convos.end_turn(minute + data.MINUTES_PER_TURN, at_start, at_end)
        record["convo"] = self.convos.log[self.convo_told:]
        self.convo_told = len(self.convos.log)
        self.present, self.so_far, self.acted, self.moves = None, None, None, None
        self.moved_by_inner = {}
        self.trip_now = set()
        for p in self.people.values():
            if p.room is None:      # day 2: not back from the night, so not in the house
                continue
            p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
        record["portions"] = self.portions
        self.log.append(record)
        self.transcript["turns"].append(tturn)

    def ask_model(self, p, t, opts, d, extra=None):
        """One model decision: the prompt, the answer, and what it does to their suspicion and
        grudge. They have now seen the levels their prompt showed. extra: a last `Now` line."""
        minute = t * data.MINUTES_PER_TURN
        seen = p.levels()
        prompt = self.prompt_for(p, t, opts, d.get("lull"), extra=extra)
        p.last_asked = minute
        text = self.oracle.ask(SYSTEM, prompt)
        p.seen = seen
        choice, why = self.parse(text, opts)
        if not choice:
            return None, why
        d.update(mode="model", **choice)
        self.take_answer(p, choice, minute, d)
        return choice, None

    def take_answer(self, p, choice, minute, d):
        """What an answer does to their suspicion and grudges (the night's answers too, at
        NIGHT_MINUTE)."""
        def named(field):
            who = next((q for q in data.ORDER if NAMES[q] == choice[field]), None)
            return None if who == p.id else who     # naming yourself counts as nobody
        suspect = named("suspects")
        before = p.suspicion.target
        d["suspects_result"] = p.suspicion.report(suspect, minute)
        if p.suspicion.target != before:
            p.suspected_at = []
            if p.yesterday is not None:
                p.yesterday["suspected_at"], p.yesterday["suspected_last_night"] = [], False
        if suspect is not None and suspect == p.suspicion.target:
            p.suspected_at.append(minute)
        d["suspects_now"] = p.suspicion.short("suspicion")
        angry = named("angry_at")
        changes = []
        if angry is not None:
            rose = p.grudge(angry).rise(minute, f"you were angry with {NAMES[angry]}", kind="angry")
            changes.append(f"grudge against {NAMES[angry]} {'rose to' if rose else 'stays at'} "
                           f"{p.grudges[angry].strength}/3")
        for t in data.ORDER:
            if t != angry and t in p.grudges and p.grudges[t].may_fall(minute):
                changes.append(f"grudge against {NAMES[t]} fell to {p.grudges[t].strength}/3")
        kept = [t for t in data.ORDER if t != angry and t in p.grudges and p.grudges[t].strength
                and not any(c.startswith(f"grudge against {NAMES[t]} fell") for c in changes)]
        if kept:
            changes.append("kept: " + ", ".join(f"{NAMES[t]} {p.grudges[t].strength}/3" for t in kept))
        d["grudge_note"] = "; ".join(changes) or "no grudges"

    def decide(self, p, t):
        minute = t * data.MINUTES_PER_TURN
        # The body's food moment comes before anything else (reports/body_design.md, §2.1).
        if self.food_due(p, t):
            return self.decide_food(p, t)
        opts = self.options_for(p)
        triggers = self.social_triggers(p, t)
        p.triggers = []
        kind, n = self.repeating(p)
        d = {"person": p.id, "triggers": triggers, "offered": len(opts),
             "held_back": kind if kind in SPEECH and n >= 3 else None}
        if not triggers:
            rose = self.risen(p)
            if rose and (p.last_inner is None or minute - p.last_inner >= INNER_EVERY):
                p.last_inner = minute
                d["inner_kinds"] = rose
                d["inner_families"] = list(dict.fromkeys(k.split(":")[0] for k in rose))
                d["inner"] = self.rise_words(p, rose)
        # The turn the trip concern starts, whoever it names is asked (reports/trip_design.md, §1),
        # whatever the inner-moment spacing; an inner moment is still recorded if it is due.
        if p.id in self.trip_now:
            d["trip_moment"] = self.trip["minute"]
            d["trip_why"] = "; ".join(self.trip["why"])
        if not triggers and not d.get("inner_kinds") and "trip_moment" not in d and self.lull_due(p, minute):
            d["lull"] = self.last_stir[p.room]
        if triggers or d.get("inner_kinds") or "trip_moment" in d or "lull" in d:
            choice, why = self.ask_model(p, t, opts, d)
            if not choice:
                d.update(mode="fallback", invalid=why, option=self.routine(p, opts), say=None)
        else:
            d.update(mode="routine", option=self.routine(p, opts), say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    def lull_due(self, p, minute):
        """Their room has been still for LULL_QUIET minutes, and they have not been asked for
        LULL_EVERY minutes."""
        if LULL_QUIET is None or p.room not in self.last_stir:
            return False
        return (minute - self.last_stir[p.room] >= LULL_QUIET
                and (p.last_asked is None or minute - p.last_asked >= LULL_EVERY))

    def decide_aside(self, q, p, to, t):
        """q has been asked aside by p: go with them or refuse. Always a model decision."""
        opts = [Option("accept_aside", f"go with {p.name} to the {data.ROOMS[to]}", kind="accept_aside",
                       to=to, partner=p.id),
                Option("refuse_aside", f"refuse to go with {p.name}", kind="refuse_aside", partner=p.id)]
        asked = f"{p.name} asks you to come aside to the {data.ROOMS[to]}"
        triggers = [asked] + [text for text, new in q.triggers if text != asked]
        q.triggers = []
        d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts),
             "held_back": None}
        choice, why = self.ask_model(q, t, opts, d)
        if not choice:
            d.update(mode="fallback", invalid=why, option="refuse_aside", say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    # ---------- making it happen ----------
    def perceive(self, q, minute, text, trigger=None, remember=True):
        if remember:
            q.memory.append((minute, text))
        if trigger:
            q.triggers.append(trigger)

    def line_text(self, p, kind, target, words, listener, while_doing=None, option=None):
        aimed = ("you" if listener is not None and target is listener else target.name) if target else None
        if self.day != 4 and kind in TRIP_KINDS:
            gist = self.trip_gist(p, kind, aimed, option)
        elif kind == "ask":
            gist = f"{p.name} asks everyone who took the can"
        elif kind == "deny":
            gist = f"{p.name} denies taking it, to everyone"
        elif kind == "accuse":
            gist = f"{p.name} accuses {aimed} of taking it"
        elif kind == "confront":
            gist = f"{p.name} confronts {aimed}"
        elif kind == "confess":
            gist = f"{p.name} admits taking it, to everyone"
        elif kind == "reassure":
            gist = f"{p.name} reassures {aimed or 'everyone'}"
        elif kind == "propose":
            gist = f"{p.name} says someone should go to the neighbour's house tonight"
        elif kind == "volunteer":
            gist = f"{p.name} offers to go to the neighbour's house tonight"
        elif kind == "object":
            gist = (f"{p.name} says {aimed} should not be the one to go" if aimed
                    else f"{p.name} says nobody should go out tonight")
        elif kind == "back":
            gist = f"{p.name} says {aimed} should be the one to go"
        elif kind == "decline":
            gist = f"{p.name} says {data.PRONOUNS[p.id]['he']} will not be the one to go"
        elif while_doing:
            gist = f"{p.name} says to {aimed or 'everyone'}, while {while_doing}"
        else:
            gist = f"{p.name} says to everyone"
        return f"{gist}: \"{words}\""

    @staticmethod
    def trip_gist(p, kind, aimed, option):
        """What others hear of a position on day 2 (reports/night_design.md, §6)."""
        he = data.PRONOUNS[p.id]["he"]
        if kind == "propose":
            return f"{p.name} says someone should go to the neighbour's house tonight"
        if option == "still_going":
            return f"{p.name} says {he} still means to go tonight"
        if kind == "volunteer":
            return f"{p.name} offers to go to the neighbour's house tonight"
        if kind == "object":
            return f"{p.name} says {aimed} must stay home tonight" if aimed else f"{p.name} says nobody should go out tonight"
        if kind == "back":
            return f"{p.name} says {aimed} {'are' if aimed == 'you' else 'is'} the one who should go"
        return f"{p.name} says {he} will not go"

    def started_by(self, room, minute, why, d):
        self.started(room, minute, why, bool(d.get("inner_kinds")))

    def apply(self, p, opt, d, t, voices, record):
        minute = t * data.MINUTES_PER_TURN
        self.seq += 1
        d["seq"] = self.seq
        kind, _ = act_of(opt.id)
        room = p.room
        seen = self.others_here(p)
        culprit = self.people[self.culprit] if self.culprit else None
        feel = f" You felt {d['feeling']}." if d.get("feeling") else ""
        if d["mode"] == "model":
            p.feeling = d["feeling"]
            p.feeling_until = t + FEELING_SHOWS_FOR_TURNS if outward(d["feeling"]) else -1
        target_id = aimed_at(opt.id) or (opt.act.get("target") if kind == "sit" else None)
        target = self.people[target_id] if target_id else None
        partner = self.people[opt.act["partner"]] if "partner" in opt.act else None
        given_to = self.people[opt.act["target"]] if kind == "give" else None
        # Anything but staying put in silence, or staying seated with the same person, stirs the room.
        if not (kind == "silent" or (kind == "sit" and p.activity["kind"] == "sitting"
                                     and p.activity["with"] == target_id)):
            self.last_stir[room] = minute
        p.history.append({"t": t, "kind": kind, "seq": self.seq})
        p.addressed = None
        p.aside_lead = None
        so_far = self.so_far[room]
        out = []

        if kind != "sit" and p.activity["kind"] == "sitting" and kind not in SPEECH:
            p.activity = {"kind": "idle", "label": "standing"}

        # The culprit accusing someone else of what they did is someone else accused in their
        # hearing.
        if culprit is not None and p is culprit and kind == "accuse":
            he = data.PRONOUNS[p.id]["he"]
            self.add_guilt(minute, f"you accused {target.name} of what you did, at minute {minute:02d}",
                           f"{he} accused {target.name} of what {he} did", record)

        words = d.get("say")
        if words:
            doing = {"go": f"leaving for the {data.ROOMS.get(opt.act.get('to'), '')}",
                     "search": "searching", "sit": f"sitting down with {target.name if target else ''}",
                     "eat": "eating", "share": "sharing out the food",
                     "aside": f"asking {target.name if target else ''} to come aside",
                     "accept_aside": f"going aside with {partner.name if partner else ''}",
                     "refuse_aside": "refusing to go aside",
                     "give": f"handing {given_to.name if given_to else ''} a portion",
                     "eat_given": "eating", "refuse_given": "putting the portion back on the shelf"}.get(kind)
            spoken_kind = kind if kind in SPEECH else "say"
            aimed = aimed_at(opt.id)
            new, why = self.newness.line(p.id, opt.id, [q.id for q in seen])
            d["new"], d["new_why"] = new, why
            if new:
                self.started_by(room, minute, f"{p.name}: {why}", d)
            text = self.line_text(p, spoken_kind, target if aimed else None, words, None,
                                  None if opt.speech else doing, opt.id)
            self.said.append({"minute": minute, "room": data.ROOMS[room], "who": p.name,
                              "to": target.name if aimed else "everyone", "text": text,
                              "words": words, "new": new, "why": why})
            so_far.append(text)
            for q in seen:
                heard = self.line_text(p, spoken_kind, target if aimed else None, words, q,
                                       None if opt.speech else doing, opt.id)
                self.perceive(q, minute, heard, trigger=(heard, new))
                q.heard.append({"seq": self.seq, "who": p.id, "kind": spoken_kind,
                                "target": target_id if aimed else None})
                if aimed and q is target:
                    q.addressed = {"seq": self.seq, "who": p.id, "accused": kind == "accuse"}
                if kind in ("ask", "accuse"):
                    q.heard_question = True
                if kind == "confess":
                    if q.knows_culprit is None:
                        q.confession_heard_at = minute
                    q.knows_culprit = p.id
                    q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
                                  "(you heard it)")
                    # Grudges: it was admitted after being denied to them, or after accusing them.
                    # On day 2 a denial or accusation of day 1 is yesterday's (reports/night_design.md, §5.1).
                    y = q.yesterday or {"denials": (), "accused_by": ()}
                    if p.id in q.denials_heard:
                        when = "yesterday at" if p.id in y["denials"] else "at"
                        self.add_grudge(q, p, minute,
                                        f"{p.name} admitted taking it at minute {minute:02d}, after "
                                        f"denying it to you {when} minute {q.denials_heard[p.id]:02d}",
                                        f"{p.name} admitted it after denying it to {q.name}", record)
                    if p.id in q.accused_by:
                        when = "yesterday at" if p.id in y["accused_by"] else "at"
                        self.add_grudge(q, p, minute,
                                        f"{p.name} had accused you of it {when} minute {q.accused_by[p.id]:02d}",
                                        f"{p.name} had accused {q.name} of it", record)
                if kind == "deny":
                    q.denials_heard[p.id] = minute
                    if q.yesterday:
                        q.yesterday["denials"].discard(p.id)
                if kind == "accuse" and q is target:
                    q.accused_by[p.id] = minute
                    if q.yesterday:
                        q.yesterday["accused_by"].discard(p.id)
                    if q.id != self.culprit:        # a false accusation
                        self.add_grudge(q, p, minute,
                                        f"{p.name} accused you of taking the can at minute {minute:02d}, "
                                        f"and you had not",
                                        f"{p.name} accused {q.name} falsely", record)
                # The culprit's guilt: someone else accused of what they did in their hearing, or
                # someone reassuring them personally. Their denials and reassurance of everyone
                # add nothing.
                if culprit is not None and q is culprit and p is not culprit:
                    pro = data.PRONOUNS[q.id]
                    if kind == "accuse" and target is not culprit:
                        self.add_guilt(minute, f"{p.name} accused {target.name} of what you did, "
                                               f"at minute {minute:02d}",
                                       f"{p.name} accused {target.name} of what {pro['he']} did", record)
                    elif kind == "reassure" and target is culprit:
                        self.add_guilt(minute, f"{p.name} reassured you, at minute {minute:02d}",
                                       f"{p.name} reassured {pro['him']}", record)
            voices.append((room, new, {p.id} | {q.id for q in seen}))
            mine = {"ask": "asked who took it", "deny": "denied taking it",
                    "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
                    "confront": f"confronted {target.name if target else ''}",
                    "reassure": f"reassured {target.name if aimed else 'everyone'}",
                    "propose": "said someone should go to the neighbour's house tonight",
                    "volunteer": "offered to go there tonight",
                    "object": (f"said {target.name} should not be the one to go" if target
                               else "said nobody should go out tonight"),
                    "back": f"said {target.name if target else ''} should be the one to go",
                    "decline": "said you will not be the one to go"}.get(kind, "said")
            if self.day != 4 and kind in TRIP_KINDS:
                # Day 2's wording (reports/night_design.md, §6), for the speaker's own line.
                mine = {"still_going": "said you still mean to go there tonight",
                        "nobody_goes": "said nobody should go out tonight",
                        "refuse_to_go": "said you will not go"}.get(opt.id, mine)
                if target and kind == "back":
                    mine = f"said {target.name} is the one who should go"
                elif target and kind == "object":
                    mine = f"said {target.name} must stay home tonight"
            if kind in TRIP_KINDS:
                # The plan record (reports/trip_design.md, §4.1): every position taken, and each
                # speaker's latest one for everyone who heard it, the speaker included. Day 2 also
                # keeps the option id (reports/night_design.md, §6).
                aim = target_id if aimed else None
                self.trip_acts.append((minute, p.id, kind, aim, words))
                heard = (minute, kind, aim, self.seq) + ((opt.id,) if self.day != 4 else ())
                if self.day != 4:
                    self.trip_ids.append(opt.id)
                for x in [p] + seen:
                    x.trip_heard[p.id] = heard
                    if kind in ("propose", "volunteer", "back"):
                        x.trip_raised = True
                if kind == "propose":
                    p.proposed = True
            # Their own lines reach them without the words: minute and verb only
            # (reports/repetition_probe.md, variant B). The others hear the words.
            p.memory.append((minute, f"you {mine}.{feel}"))
            p.said_lines.append(f"min {minute:02d}, you {mine}.")
            if kind in ("ask", "accuse"):
                p.heard_question = True
            if kind == "confess":
                p.confessed = True
                p.sure.append(f"min {minute:02d}: you admitted aloud that you took the can"
                              + (f", in front of {', '.join(q.name for q in seen)}." if seen else "."))
            names = ", ".join(q.name for q in seen)
            out.append(f"said to {names}" if names else "said it to nobody")
            if opt.speech:
                if p.activity["kind"] == "searching":
                    p.activity = {"kind": "idle", "label": "standing"}
                elif p.activity["kind"] == "idle":
                    p.activity = {"kind": "idle", "label": "talking"}
                return "; ".join(out) + "."

        def fact(why, trig):
            """Something new that the others in the room saw."""
            if seen:
                self.started_by(room, minute, why, d)
                d["new_fact"] = why
                for q in seen:
                    self.perceive(q, minute, trig + ".", trigger=(trig, True), remember=False)

        def leave(person, to, with_whom=None):
            person.activity = {"kind": "walking", "label": f"leaving for the {data.ROOMS[to]}"}
            self.present[room].remove(person.id)
            self.moves.append((person, to, with_whom))
            self.moved_by_inner[person.id] = bool(d.get("inner_kinds"))

        if kind == "silent":
            p.activity = {"kind": "idle", "label": "staying put"}
            so_far.append(f"{p.name} stays put and says nothing.")
            if d["mode"] == "model":
                p.memory.append((minute, f"you stayed where you were and said nothing.{feel}"))
            return "stayed where they were" + (" (its line was dropped: silent means no words)"
                                               if d.get("dropped_line") else "") + "."
        if kind == "search":
            if opt.id == "search":
                p.activity = {"kind": "searching", "label": f"searching the {data.ROOMS[room]}",
                              "until": t + 1}
                so_far.append(f"{p.name} starts going through the {data.ROOMS[room]}.")
                for q in seen:
                    self.perceive(q, minute, f"{p.name} starts going through the {data.ROOMS[room]}.")
                p.memory.append((minute, f"you started searching the {data.ROOMS[room]}.{feel}"))
            else:
                so_far.append(f"{p.name} carries on searching the {data.ROOMS[room]}.")
            if p.activity["until"] <= t:
                p.searched.add(room)
                p.activity = {"kind": "idle", "label": "standing"}
                p.sure.append(f"min {minute:02d}: you finished searching the {data.ROOMS[room]}: "
                              "no can, nothing out of place.")
                fact(f"{p.name} finished searching the {data.ROOMS[room]} and found nothing",
                     f"{p.name} finishes going through the {data.ROOMS[room]}: no can, nothing out of place")
                return "went through the room and found nothing."
            return "started going through the room." if opt.id == "search" else "carried on searching."
        if kind == "go":
            to = opt.act["to"]
            so_far.append(f"{p.name} leaves for the {data.ROOMS[to]}.")
            for q in seen:
                self.perceive(q, minute, f"{p.name} leaves for the {data.ROOMS[to]}.")
            leave(p, to)
            p.memory.append((minute, f"you went to the {data.ROOMS[to]}.{feel}"))
            return f"went to the {data.ROOMS[to]}."
        if kind == "aside":
            to = opt.act["to"]
            so_far.append(f"{p.name} asks {target.name} to come aside to the {data.ROOMS[to]}.")
            for q in seen:
                if q is not target:
                    self.perceive(q, minute, f"{p.name} asks {target.name} to come aside to the {data.ROOMS[to]}.")
            p.memory.append((minute, f"you asked {target.name} to come aside to the {data.ROOMS[to]}.{feel}"))
            self.moved_by_inner[p.id] = bool(d.get("inner_kinds"))     # if the other comes
            return f"asked {target.name} to come aside to the {data.ROOMS[to]}."
        if kind == "accept_aside":
            to = opt.act["to"]
            so_far.append(f"{p.name} goes with {partner.name} to the {data.ROOMS[to]}.")
            for q in seen:
                if q is not partner:
                    self.perceive(q, minute, f"{partner.name} and {p.name} leave for the {data.ROOMS[to]} together.")
            by_inner = self.moved_by_inner.get(partner.id, False)   # how the asking came about
            for person, other in ((partner, p), (p, partner)):
                person.activity = {"kind": "walking", "label": f"leaving for the {data.ROOMS[to]}"}
                self.present[room].remove(person.id)
                self.moves.append((person, to, other.id))
                self.moved_by_inner[person.id] = by_inner
            partner.aside_lead = p.id
            p.memory.append((minute, f"you went with {partner.name} to the {data.ROOMS[to]}.{feel}"))
            partner.memory.append((minute, f"{p.name} came with you to the {data.ROOMS[to]}."))
            return f"went with {partner.name} to the {data.ROOMS[to]}."
        if kind == "refuse_aside":
            so_far.append(f"{p.name} refuses to go with {partner.name}.")
            for q in seen:
                text = f"{p.name} refuses to go aside with {'you' if q is partner else partner.name}"
                self.perceive(q, minute, text + ".", trigger=(text, False) if q is partner else None)
            partner.addressed = {"seq": self.seq, "who": p.id, "accused": False}
            p.memory.append((minute, f"you refused to go aside with {partner.name}.{feel}"))
            return f"refused to go with {partner.name}."
        if kind == "sit":
            new = not (p.activity["kind"] == "sitting" and p.activity["with"] == target.id)
            p.activity = {"kind": "sitting", "with": target.id, "label": f"sitting with {target.name}"}
            if new:
                so_far.append(f"{p.name} sits down with {target.name}.")
                for q in seen:
                    if q is target:
                        self.perceive(q, minute, f"{p.name} comes and sits with you.",
                                      trigger=(f"{p.name} came to sit with you", False))
                    else:
                        self.perceive(q, minute, f"{p.name} sits with {target.name}.")
                p.memory.append((minute, f"you sat with {target.name}.{feel}"))
                return f"sat with {target.name}."
            so_far.append(f"{p.name} stays sitting with {target.name}.")
            return f"stayed sitting with {target.name}."
        if kind == "eat":
            p.activity = {"kind": "idle", "label": "eating"}
            if self.portions <= 0:
                p.memory.append((minute, "you reached for the shelf; it was empty."))
                so_far.append(f"{p.name} reaches for the shelf; it is empty.")
                return "reached for the shelf and found it empty."
            self.portions -= 1
            p.hunger = max(0.0, p.hunger - 0.4)
            p.eaten += 1
            p.last_meal = minute
            so_far.append(f"{p.name} eats one of the portions.")
            for q in seen:
                q.sure.append(f"min {minute:02d}: {p.name} ate one of the portions (you saw it).")
                # A grudge toward someone who eats in front of you while you are hungry.
                if hunger_level(q.hunger) >= 1:
                    self.add_grudge(q, p, minute,
                                    f"{p.name} ate a portion in front of you at minute {minute:02d}, "
                                    f"while you were hungry",
                                    f"{p.name} ate in front of {q.name}, who was hungry", record)
            fact(f"{p.name} ate one of the portions", f"{p.name} eats one of the portions")
            p.sure.append(f"min {minute:02d}: you ate one of the portions. {self.portions} left.")
            record["events"].append(f"{p.name} ate a portion")
            return f"ate a portion; {self.portions} left."
        if kind == "share":
            p.activity = {"kind": "idle", "label": "sharing out the food"}
            if self.portions <= 0:
                so_far.append(f"{p.name} goes to share out the food; the shelf is empty.")
                return "went to share out the food and found the shelf empty."
            eaters = [p] + seen
            each = self.portions / len(eaters)
            names = ", ".join(q.name for q in eaters)
            for q in eaters:
                q.hunger = max(0.0, q.hunger - 0.4 * each)
                q.eaten += each
                q.last_meal = minute
            n, self.portions = self.portions, 0
            trig = f"{p.name} shares out the last {n} portion{'s' if n != 1 else ''} between {names}"
            so_far.append(trig + ".")
            for q in seen:
                q.sure.append(f"min {minute:02d}: {trig}; you had your part.")
            fact(f"{p.name} shared out the food", trig)
            p.sure.append(f"min {minute:02d}: you shared out the last {n} portions between {names}.")
            record["events"].append(f"{p.name} shared out {n} portions between {names}")
            return f"shared out the last {n} portions between {names}."
        # A food moment's gift (reports/body_design.md, §2.5-§2.6): the portion leaves the shelf for
        # the hands of the one it is given to, who answers at once; what the room sees is written then.
        if kind == "give":
            p.activity = {"kind": "idle", "label": f"handing {given_to.name} a portion"}
            self.portions -= 1
            record["events"].append(f"{p.name} gave a portion to {given_to.name}")
            return f"gave one of the portions to {given_to.name}."
        if kind == "eat_given":
            giver, him = partner, data.PRONOUNS[p.id]["him"]
            p.activity = {"kind": "idle", "label": "eating"}
            p.hunger = max(0.0, p.hunger - 0.4)
            p.eaten += 1
            p.last_meal = minute
            line = f"{giver.name} gives one of the portions to {p.name}, and {p.name} eats it"
            so_far.append(line + ".")
            for q in seen:
                if q is giver:
                    q.sure.append(f"min {minute:02d}: you gave one of the portions to {p.name}, and {p.name} ate it. "
                                  f"{self.portions} left.")
                    continue
                q.sure.append(f"min {minute:02d}: {giver.name} gave one of the portions to {p.name}, and {p.name} "
                              f"ate it (you saw it).")
                # Watching someone eat while hungry, as for `eat`; not the giver, who chose it.
                if hunger_level(q.hunger) >= 1:
                    self.add_grudge(q, p, minute,
                                    f"{p.name} ate a portion {giver.name} gave {him}, in front of you at minute "
                                    f"{minute:02d}, while you were hungry",
                                    f"{p.name} ate the portion {giver.name} gave {him} in front of {q.name}, "
                                    f"who was hungry", record)
            fact(f"{p.name} ate the portion {giver.name} gave {him}", line)
            p.sure.append(f"min {minute:02d}: {giver.name} gave you one of the portions, and you ate it. "
                          f"{self.portions} left.")
            record["events"].append(f"{p.name} ate the portion {giver.name} gave {him}")
            return f"ate the portion {giver.name} gave {him}; {self.portions} left."
        if kind == "refuse_given":
            giver, him = partner, data.PRONOUNS[p.id]["him"]
            p.activity = {"kind": "idle", "label": "standing"}
            self.portions += 1
            line = f"{giver.name} gives one of the portions to {p.name}; {p.name} puts it back on the shelf"
            so_far.append(line + ".")
            why = f"{p.name} put back the portion {giver.name} gave {him}"
            self.started_by(room, minute, why, d)
            d["new_fact"] = why
            for q in seen:
                if q is giver:
                    q.sure.append(f"min {minute:02d}: you gave one of the portions to {p.name}, and {p.name} put it "
                                  f"back on the shelf.")
                    self.perceive(q, minute, None, remember=False,
                                  trigger=(f"{p.name} puts the portion you gave back on the shelf", True))
                else:
                    q.sure.append(f"min {minute:02d}: {giver.name} gave one of the portions to {p.name}, and "
                                  f"{p.name} put it back on the shelf (you saw it).")
                    self.perceive(q, minute, None, remember=False, trigger=(line, True))
            p.sure.append(f"min {minute:02d}: {giver.name} gave you one of the portions, and you put it back on "
                          f"the shelf.")
            record["events"].append(f"{p.name} put back the portion {giver.name} gave {him}")
            return f"put the portion {giver.name} gave {him} back on the shelf; {self.portions} left."
        return ""
