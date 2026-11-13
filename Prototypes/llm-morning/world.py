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
import copy
import json
import random
import re

import data
import topics
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
INTENT_LINE = "- You meant to:"     # the first line of memory.block_b that is the night mind's intent
PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,370 at most in the second step
QUIET_TURNS = 2              # full turns with nothing new that end a conversation
INNER_EVERY = 9              # minutes: an inner moment at most this often per person
MEAL_KINDS = ("meal", "meal_small", "plate_eat", "plate_to", "plate_back",   # code mode (section 7.3)
              "water_round", "cup_drink")
MEAL_WORDS = {1.0: "a portion", 0.5: "half a portion", 0.25: "a quarter of a portion"}
OWED_TURNS = 2               # turns in which someone aimed at must answer (reports/play_fix2.md, fix 1)
OWES_ANSWER = ("accuse", "confront", "reassure", "say")     # acts aimed at someone that ask for an answer
HEADS_TURN = ("accuse", "confess")      # acts after which everyone else in the room stops what they were doing (fix 2)
FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one step this often
LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
                             # off since reports/lull_v9.md, 9 in reports/lull_design.md
LULL_EVERY = 12              # minutes since a person was last asked before a lull
TRIP_HUNGER = 2              # the hunger level ("very hungry") that starts the trip concern
TRIP_ON = True               # the trip concern (reports/trip_design.md); off only in tests
TRIP_KINDS = tuple(TRIP_WHY)  # propose, volunteer, object, back, decline; propose_far, volunteer_far (stage B)
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
    "propose_far": "said someone should try the houses further along the street tonight",      # stage B, W5
    "volunteer_far": "offered to go further along the street tonight",
    "give": "given someone a portion", "eat_given": "eaten", "refuse_given": "refused a portion",
    "confront": "confronted someone",
    "save_water": "said nobody should use the stored water for washing or the toilet",          # W1
    "ration_water": "said the water must be shared out by the cup",
    "collect_rain": "set the bin under the drainpipe in the rain",
    "door_look": "looked through the gap in the boards", "door_call": "called out through the front door",       # W2a
    "door_open": "opened the front door", "door_give": "handed out water at the front door",
    "door_refuse": "told the person at the door to go away",
    "talk": "talked about something that happened earlier",                                  # reports/talk_design.md
    "tell": "told someone something they had missed",
}
DOOR_KINDS = ("door_look", "door_call", "door_open", "door_give", "door_refuse")

# Fasting's stages in days (quiet.py; reports/world_design.md, §4.3.1), and thirst's (§4.3.2).
FAST_STAGE_WORD = {1: "hungry all the time", 2: "light and slow", 3: "thin and weak", 4: "losing strength",
                   5: "wasted"}
THIRST_STAGE_WORD = {1: "thirsty", 2: "badly thirsty", 3: "parched", 4: "confused from thirst"}
WATER_RULES = ("save_water", "ration_water")
RAIN_NOW_DAY = "- Rain is falling: you hear it on the roof and against the boards."
W1_NOW = (RAIN_NOW_DAY, "It is raining: you hear it on the roof.")        # the day's, and the night's (night.py)
W1_OPTIONS = WATER_RULES + ("collect_rain", "rain_out")
HUNGER_WORDS = ["a little hungry", "hungry", "very hungry", "starving"]
LEVEL_WORDS = {1: "a little", 2: "some", 3: "a lot"}   # the only words a level is given
EVENTS_SHOWN = 4             # most recent events shown per grudge and for guilt


def estimate_tokens(text, less=0):
    """less: characters of `text` that do not count (the trip block, reports/trip_design.md §2.5)."""
    return int((len(text) - less) / 3.6) + 1


NUMBER_WORDS = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def day_index(day):
    """The played day of a house day: day 4 is day 1 (reports/days_design.md)."""
    return day - 3


def when_words(scene, day):
    """When a scene was, seen from the morning of house day `day` (reports/days_design.md, §3.5): scene is
    ("D", k), the k-th played day, or ("N", k), the night after it."""
    kind, k = scene
    ago = day_index(day) - k
    if kind == "D":
        if ago <= 0:
            return "this morning"
        return {1: "yesterday", 2: "two days ago"}.get(ago) or f"{NUMBER_WORDS.get(ago, ago)} days ago"
    if ago <= 0:
        return "tonight"
    return {1: "last night", 2: "the night before last"}.get(ago) or f"{NUMBER_WORDS.get(ago, ago)} nights ago"


def strength(feeling):
    f = (feeling or "").lower()
    s = max((level for level, stems in SHOWN.items() if any(x in f for x in stems)), default=0)
    if s and re.search(r"\b(deeply|very|extremely|utterly|so)\b", f):
        s += 1
    return s


def outward(feeling):
    return strength(feeling) > 0


def face_word(feeling):
    """The word of a feeling that a face shows: the first word holding one of the strongest SHOWN stems in it, as the
    player's screen writes a face (reports/play_design.md §1.4, L4). "guilty and terrified" shows "terrified"."""
    f = (feeling or "").lower()
    level = max((lv for lv, stems in SHOWN.items() if any(x in f for x in stems)), default=0)
    for word in re.findall(r"[a-z']+", f):
        if any(x in word for x in SHOWN.get(level, ())):
            return word
    return feeling


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


def grudge_facts(name, events, limit=None, clock_from=None, night_from=None, today=None):
    """The facts behind a grudge: each event the rules saw, then one line for the times the
    person named them as who they were angry with. An event carried from an earlier day or night
    is (minute, text with its day word, kind, day word, scene, text) (reports/night_design.md, §5.3;
    reports/days_design.md, §3.5): its words are written when the next morning is set up. clock_from: data.CLOCK_FROM
    on a quiet day, whose minutes from 90 on are written as the clock (reports/quiet_day_fixes.md, fix 3).
    night_from: on a quiet day, the minute its night's answers keep (Morning.night_minute): those are "tonight",
    never a minute (reports/multiday.md)."""
    facts = [e[1] for e in events if e[2] == "event"]
    angry = [e for e in events if e[2] == "angry"]
    if limit:
        facts, angry = facts[-limit:], angry[-limit:]
    if angry and all(len(e) == 3 for e in events):
        ms = [e[0] for e in angry if night_from is None or e[0] < night_from]
        tonight = len(ms) < len(angry)
        parts = ([data.minutes_words(ms, clock_from)] if ms else []) + (["tonight"] if tonight else [])
        facts.append(f"you were angry with {name} " + "; and ".join(parts))
    elif angry:
        groups = {}             # day word -> (a night?, minutes), oldest first
        for e in angry:
            when = e[3] if len(e) > 3 else (today or "this morning")      # today: amendment 5, stage B
            night = e[4][0] == "N" if len(e) > 4 else when == "last night"
            if len(e) == 3 and night_from is not None and e[0] >= night_from:
                when, night = "tonight", True
            groups.setdefault(when, (night, []))[1].append(e[0])
        parts = [when if night else f"{when} {data.minutes_words(ms, clock_from)}"
                 for when, (night, ms) in groups.items()]
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


class Sure(list):
    """A person's sure lines. after[i] is how many of their memory lines came before line i, so that the player's screen
    shows a minute's lines in the order they happened (reports/play_fix1.md, fix 4)."""

    def __init__(self, person, lines=()):
        super().__init__(lines)
        self.person = person
        self.after = [len(person.memory)] * len(self)

    def append(self, line):
        self.after.append(len(self.person.memory))
        super().append(line)

    def __copy__(self):
        out = Sure(self.person, self)
        out.after = list(self.after)
        return out

    def __deepcopy__(self, memo):
        out = Sure.__new__(Sure)
        memo[id(self)] = out
        list.extend(out, copy.deepcopy(list(self), memo))
        out.person = copy.deepcopy(self.person, memo)
        out.after = list(self.after)
        return out


class Person:
    @property
    def sure(self):
        return self._sure

    @sure.setter
    def sure(self, lines):
        self._sure = Sure(self, lines)

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
        self.knows_empty = False    # stage B, W5: they got inside the neighbour's house and left nothing there
        self.missing = {}           # stage B: someone who did not come back -> (how they know it, the night)
        self.history = []           # one {"t", "kind", "seq"} per turn: what they did
        self.heard = []             # lines they heard: {"seq", "who", "kind", "target"}
        self.addressed = None       # the last line aimed at them since they last acted
        # reports/play_fix2.md, fix 1: who accused, confronted, reassured or spoke to them, in which turn and room, if they
        # have not answered yet; fix 3: those who accused them falsely and whom they now know to have been wrong.
        self.owed = None
        self.wronged = []
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
        # Days that follow one another (reports/days_design.md, §3.5): the house day of their confession, of the
        # confession they heard, of each denial and accusation heard; and the earlier days' suspicion minutes,
        # as (scene, minutes, or True for a night).
        self.confessed_day = None
        self.confession_heard_day = None
        self.denial_day = {}
        self.accused_day = {}
        self.suspected_past = []
        # The food moment (reports/body_design.md, §2): the minute they last ate this morning; on day 2,
        # the minute of yesterday's last meal (None: not since before yesterday); their last moment.
        self.last_meal = None
        self.ate_yesterday = None
        self.last_food = None
        # The quiet day (reports/quiet_day_design.md, §1), from day 3 on: when they last ate, their sleep debt, their
        # rests and the stages the body line states (quiet.py). None before day 3.
        self.needs = None
        # W1 (reports/world_design.md, §1.2): what they perceive of the weather and the water, written by the code
        # (quiet.py); never the World itself. rain_since: when the rain they hear now began; water: the "About water:"
        # line, the house's rule, and whether the bin is under the drainpipe, as they know them.
        self.rain_since = None
        self.water = None
        # W2a (reports/w2_design.md, §4.2): what they perceive of the front door now, written by the code (quiet.py):
        # {"lines", "options", "door", "opening", "give"}; None when nothing is there for them.
        self.door = None
        # reports/talk_design.md (amended): the topics they know (topics.py: key -> their own account, or that they
        # were told), when they chose one (key -> [(day k, minute)]), and their beliefs: what they were told, by whom.
        self.topics = {}
        self.topic_said = {}
        self.beliefs = []

    def grudge(self, against):
        return self.grudges.setdefault(against, Grudge())

    def levels(self):
        out = {"hunger": hunger_level(self.hunger), "suspicion": self.suspicion.strength,
               "grudges": {t: g.strength for t, g in self.grudges.items()}}
        if self.guilt is not None:
            out["guilt"] = self.guilt
        if self.needs is not None:          # from day 3: weak and very weak; exhausted (quiet.py, §4 Q1)
            out["fast"] = self.needs["fast_stage"]
            out["debt"] = int(self.needs["debt_stage"] >= 2)
            out["thirst"] = self.needs.get("thirst_stage", 0)
        return out


class Morning:
    def __init__(self, oracle, seed=0, scenario=data.DEFAULT_SCENARIO, day=4, player=None):
        """day 4: the morning of the count (day 1). day 5: the next morning (day 2), which
        `Morning.next_day` sets up from day 1 and the night. player: whoever plays one of them (player.py,
        reports/play_design.md), or None: the model decides for everyone, as it always has."""
        self.oracle = oracle
        self.day = day
        self.player = player
        self.away = set()           # day 2: who did not come back in the night
        self.street = {}            # stage B, W5: person -> their "About the street:" line, once next door is empty
        self.outings = {}           # a quiet day: person -> their "About going out at night:" line (facts_and_evening)
        self.carry = {}             # day 2: person -> the carry-in block (reports/night_design.md, §5.2)
        self.neighbour = {}         # day 2: person -> their "About the neighbour's house:" line
        self.carried = {}           # day 2: person -> their opening, food and neighbour lines at minute 00
        self.trip_ids = []          # day 2: the option id of each trip act, in order
        self.seed = seed
        self.scenario = scenario
        self.culprit = data.culprit(scenario)       # who took the can, or None
        self.people = {p: Person(p, scenario) for p in data.ORDER}
        self.portions = data.PORTIONS
        # Code mode (brain.py; Docs/fable-audit-2026-11.md, 7.4, the scenario change): a countable stock for about
        # four days, and how far a portion pushes hunger back. With a model the shelf and the body are as they were.
        self.relief, self.hunger_a_day = 0.4, None
        scenario_start = getattr(getattr(oracle, "brain", None), "scenario", None)
        if scenario_start:
            self.portions, self.relief = scenario_start["portions"], scenario_start["relief"]
            self.hunger_a_day = scenario_start["hunger_a_day"]
        self.plates = {}            # code mode: person -> the share set out for them that they have not yet eaten
        self.meal_at = None         # code mode: the minute today's meal was set out
        # The week (week.py): the beat under way ("morning", "work", "afternoon", "evening", or None); the meals set
        # out today, by beat; the day's tasks taken, task -> who.
        self.beat = None
        self.meals = set()
        self.tasks = {}
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
        # For the chronicle (reports/days_design.md, §4): act seq -> person -> {"memory": [...], "sure": [...]},
        # the lines each of them got of it; act seq -> person -> the room whose voices they heard.
        self.views = {}
        self.voices_heard = {}
        self.blocks = {}            # day 2 on: person -> the memory blocks A, B and C (reports/days_design.md, §3)
        self.quiet = None           # day 3 on: the quiet layer (quiet.py), which plays the day to bedtime
        self.now = None             # during a turn: its minute
        self.topic_raised = {}      # (room, topic) -> the minute someone last raised it there (topics.py, F4)
        self.tells = []             # every tell: who told whom, the claims, the words, T1's warnings (topics.py)
        self.topic_line = None      # during a talk or tell act: its option's act (topic, referent, listeners)
        if day != 4:
            return                  # day 2's opening is set up by next_day
        for p in self.people.values():
            how = "did it" if p.id == "elena" else "saw it"
            opening = data.OPENING.replace(f"{data.PORTIONS} portions are left.",
                                           f"{portions_text(self.portions)} are left.")
            p.sure.append(f"min 00: {opening} (you {how})")
            if p.id == self.culprit:
                p.sure.append("You know where the can went: you ate it yourself in the night, and nobody saw.")
            p.triggers.append(("the count came up short in front of everyone", True))
            p.seen = p.levels()
        self.started("kitchen", 0, "the count came up short", False)

    @classmethod
    def next_day(cls, day1, night, oracle, chronicle=None):
        """The next morning, from the day before and the night that followed it (reports/night_design.md, §5;
        reports/days_design.md, §3, with the chronicle)."""
        import night as night_mod
        m = night_mod.next_day(day1, night, oracle, chronicle)
        if m.brain() is not None:
            m.brain().new_day(m)
        return m

    def order_string(self, t, room):
        """The seed string of a room's turn order (reports/days_design.md, §4.4): days 1 and 2 share one."""
        if self.day <= 5:
            return f"{self.seed}:{t}:{room}"
        return f"{self.seed}:day{day_index(self.day)}:{t}:{room}"

    def food_string(self, t, pid):
        """The seed string of a food moment's draw (reports/body_design.md, §2.1; days_design.md, §4.4)."""
        return f"{self.seed}:day{day_index(self.day)}:food:{t}:{pid}"

    def started(self, room, minute, why, by_inner):
        if self.convos.new_thing(room, minute, why):
            self.start_by_inner.append(by_inner)

    def is_player(self, p):
        """p is played by the player (reports/play_design.md), not the model."""
        return getattr(self, "player", None) is not None and p.id == self.player.pid

    def brain(self):
        """The code brain (brain.py; Docs/fable-audit-2026-11.md, section 10.1) when the run was given one, in place of
        the oracle; None otherwise: the model decides, as it always has."""
        return getattr(self.oracle, "brain", None)

    def unasked(self):
        """The mode of an act the rules chose because nobody could be asked. With a model: "fallback", its answer could
        not be used. In code mode nothing was asked and the day's asks were spent, so it is the rules' own: "routine"."""
        return "routine" if self.brain() is not None else "fallback"

    # ---------- who is where ----------
    def others_here(self, p):
        if self.present is not None:
            ids = self.present[p.room]
        else:
            ids = [q for q in data.ORDER if self.people[q].room == p.room]
        return [self.people[q] for q in ids if q != p.id]

    def night_minute(self):
        """The minute the night's answers keep: 90 after days 1 and 2 (NIGHT_MINUTE), when the day ends at minute 90;
        after a quiet day, its bedtime, 21:00, so that no minute of the day is read as the night's
        (reports/multiday.md)."""
        import quiet
        return quiet.DAY_END if self.quiet is not None else NIGHT_MINUTE

    def night_from(self):
        """On a quiet day, the minute from which an answer is the night's, for the facts that list minutes; None on
        days 1 and 2, whose prompts stay as they were."""
        return self.night_minute() if self.quiet is not None else None

    def clock_from(self):
        """From what minute a list of this day's minutes says the clock: from 90 on a quiet day (quiet.py); never on
        days 1 and 2, whose night answers keep minute 90 (NIGHT_MINUTE)."""
        return data.CLOCK_FROM if self.quiet is not None else None

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
        lead = []           # the topic options, first in the list (reports/tell_fix_impl.md)
        others = self.others_here(p)
        room = data.ROOMS[p.room]
        opts.append(Option("silent", "stay put and say nothing", kind="silent"))
        if others:
            if not p.knows_culprit:
                opts.append(Option("ask_who", "ask everyone here who took the can", True, kind="ask"))
            # Once it has been admitted, it cannot be taken back: the one who admitted it no
            # longer denies it or blames anyone, and whoever heard it knows who it was, so has
            # nothing to deny (reports/play_fix1.md, fix 3). The one who took it may still lie.
            if p.heard_question and not p.confessed and p.knows_culprit in (None, p.id):
                opts.append(Option("deny", "deny taking it", True, kind="deny"))
            for q in others:
                if p.confessed or (p.knows_culprit and p.id != p.knows_culprit and q.id != p.knows_culprit):
                    continue
                opts.append(Option(f"accuse_{q.id}", f"accuse {q.name} of taking it", True,
                                   kind="accuse", target=q.id))
            if p.id == self.culprit and not p.confessed:
                opts.append(Option("confess", "admit taking it", True, kind="confess"))
            # Code mode: someone who was told who took it can tell those here who have not heard.
            if (self.brain() is not None and p.knows_culprit and p.knows_culprit != p.id
                    and any(q.knows_culprit is None and q.id != p.knows_culprit for q in others)):
                opts.append(Option("reveal", f"tell the others here that {NAMES[p.knows_culprit]} took the can", True,
                                   kind="reveal"))
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
            if p.water is not None and p.water["level"] == "as_before":     # W1 (world_design §4.2.3)
                opts.append(Option("save_water", "say nobody should use the stored water for washing or the toilet "
                                                 "any more", True, kind="save_water"))
            if p.water is not None and p.water["level"] != "rationed":
                opts.append(Option("ration_water", "say the water must be shared out by the cup from now on", True,
                                   kind="ration_water"))
            opts.append(Option("say_other", "say something else", True, kind="say"))
            # Words to one person, with no meaning about the can: they are spoken to (reports/play_fix1.md, fix 2).
            for q in others:
                opts.append(Option(f"say_to_{q.id}", f"say something to {q.name}", True, kind="say", target=q.id))
            lead = topics.options(self, p, others, self.now)      # reports/talk_design.md: from day 3, a visit
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
        if self.rain_action(p):
            opts.append(Option("collect_rain", "go out the back door into the rain and set the bin under the "
                                               "drainpipe in the yard", kind="collect_rain"))
        if p.door is not None and p.door["options"] and p.room == "kitchen":
            opts += self.door_options(p)
        code = self.brain() is not None
        if p.room == "kitchen" and self.portions > 0:
            opts.append(Option("eat", "eat one of the portions", kind="eat"))
            # In code mode the shelf holds days of food: sharing out "what is left" is for the last of it only.
            # On a full day (week.py) the meals do the sharing: what there is goes out at the morning's and the evening's.
            if others and (not code or self.portions <= len(others) + 1) and not self.full_days():
                opts.append(Option("share", "share out what is left among everyone here", kind="share"))
            if code and others and self.meal_open():        # the meal (section 7.3)
                full, small = MEAL_WORDS[self.meal_size()], MEAL_WORDS[self.meal_size() / 2]
                opts.append(Option("meal", f"set out the meal: {full} each for everyone in the house", kind="meal",
                                   says=True))
                opts.append(Option("meal_small", f"set out a small meal: {small} each", kind="meal_small", says=True))
        if code and p.room == "kitchen" and others and self.water_open():
            opts.append(Option("water_round", "hand out the water: a cup each", kind="water_round", says=True))
        if code and p.room == "kitchen" and self.away and self.full_days() and self.beat == "morning":
            # Someone did not come back: the first thing in the morning is the street.
            gone = data._and([NAMES[x] for x in data.ORDER if x in self.away])
            opts.append(Option("look_out", f"stand at the gap in the boards and watch the street for {gone}",
                               kind="look_out"))
        if code:
            opts += self.task_options(p)
        opts = lead + opts
        # A speech act used three turns in a row is not offered a fourth time: a guard against the model's loops, so
        # not for the player, who may say a thing a fourth time as anyone can (reports/play_s1.md, C9).
        kind, n = self.repeating(p)
        if kind in SPEECH and n >= 3 and not self.is_player(p):
            opts = [o for o in opts if act_of(o.id)[0] != kind]
        if not self.is_player(p):               # the player's options are the player's (reports/play_fix2.md)
            opts = self.answer_owed(p, opts)
            opts = self.wronged_first(p, opts)
        return opts

    def answer_owed(self, p, opts):
        """Someone who has just been accused, confronted, reassured or spoken to answers the one who did it: for their
        next decision in that room, within the next 2 turns, they may deny (where it is offered), confess (the one who
        took it), say or do anything aimed at that person, stay silent or go (reports/play_fix2.md, fix 1). Only in a
        turn: outside one nothing is decided."""
        o = p.owed
        if (o is None or self.present is None or self.now is None or p.room != o["room"]
                or self.now // data.MINUTES_PER_TURN > o["turn"] + OWED_TURNS):
            return opts
        # Code mode: owing someone an answer does not stop anyone setting out the meal or the water.
        return [x for x in opts if x.id in ("silent", "deny", "confess") or act_of(x.id)[0] == "go"
                or aimed_at(x.id) == o["who"] or x.act.get("kind") in ("meal", "meal_small", "water_round")]

    @staticmethod
    def wronged_first(p, opts):
        """After a confession, the options aimed at someone who accused them falsely come first (reports/play_fix2.md,
        fix 3), what they would say to that person before the rest, which keep their order; for the rest of the day,
        which is as long as a Morning lasts."""
        if not p.wronged:
            return opts
        aimed = [x for x in opts if aimed_at(x.id) in p.wronged]
        first = [x for x in aimed if act_of(x.id)[0] == "say"] + [x for x in aimed if act_of(x.id)[0] != "say"]
        return first + [x for x in opts if x not in first]

    @staticmethod
    def door_options(p):
        """The door's options (reports/w2_design.md, §4.6), in a fixed order: by what the door is (shut or open) and
        whether there is water to give to someone who asked for it; never by how the family feels."""
        d = p.door
        out = []
        if d["door"] == "shut":
            out.append(Option("door_look", "look through the gap in the boards", kind="door_look"))
            out.append(Option("door_call", "call out through the front door", True, kind="door_call"))
            if not d["opening"]:
                out.append(Option("door_open", "unbar and open the front door", kind="door_open"))
        else:
            out.append(Option("door_call", "speak to the person on the step", True, kind="door_call"))
        if d["give"]:
            out.append(Option("door_give", "hand out some of the stored water", kind="door_give"))
        out.append(Option("door_refuse", "send the person at the door away", True, kind="door_refuse"))
        return out

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
        if p.knows_empty:           # stage B, W5: further along the street, once next door is known empty
            mine = pos[4] if pos and len(pos) > 4 else None
            if mine != "propose_far":
                out.append(Option("propose_far", "say someone should try the houses further along the street tonight",
                                  True, kind="propose_far"))
            if mine != "volunteer_far":
                out.append(Option("volunteer_far", "offer to go further along the street tonight yourself", True,
                                  kind="volunteer_far"))
        return out

    @staticmethod
    def named_to_go(p, q):
        """As far as p has heard: q offered to go, or someone backed q since q last said they
        will not go."""
        pos = p.trip_heard.get(q)
        if pos and pos[1] in ("volunteer", "volunteer_far"):
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
            if kind == "propose_far":
                said = f"{x} said someone should try the houses further along the street"
            elif kind == "volunteer_far":
                said = f"{x} offered to go further along the street"
            elif kind == "propose":
                said = f"{x} said someone should go"
            elif option == "still_going":
                said = f"{x} said {he} still {'mean' if who == p.id else 'means'} to go"
            elif kind == "volunteer":
                said = f"{x} offered to go"
            elif kind == "object":
                said = (f"{x} said nobody should go" if q is None else f"{x} said {q} must stay home"
                        if option else f"{x} said {q} should not go")
            elif kind == "back":
                said = (f"{x} said {q} {'are' if q == 'you' else 'is'} the one who should go" if option
                        else f"{x} said {q} should go")
            else:
                said = f"{x} said {he} will not go"
            parts.append(f"{said} ({data.clock(minute)})")
        return "About going there tonight: " + "; ".join(parts) + "."

    @staticmethod
    def rain_action(p):
        """Whether p is offered `collect_rain`: in the kitchen, while it rains for them, with the bin not out."""
        return p.room == "kitchen" and p.rain_since is not None and p.water is not None and not p.water["bin_out"]

    def trip_lines(self, p):
        """What the trip concern adds after their "About the can:" line. On day 2 the food and
        the neighbour's house are as the night left them (reports/night_design.md, §5.3)."""
        if self.trip is None:
            return []
        plan = self.heard_plan(p)
        if self.day != 4:
            street = [self.street[p.id]] if p.id in self.street else []        # stage B, W5
            # A quiet day and its night: every outing they know of (reports/facts_and_evening.md, fix 3).
            outings = [self.outings[p.id]] if p.id in self.outings else []
            return ([self.food_line(p), self.neighbour.get(p.id, NEIGHBOUR_UNKNOWN)] + street + outings
                    + ([plan] if plan else []))
        return [data.ABOUT_FOOD, data.ABOUT_NEIGHBOUR] + ([plan] if plan else [])

    def missing_lines(self, p):
        """Stage B, amendment 4: for each one who did not come back, what p knows of it."""
        out = []
        for x, (how, k, *where) in p.missing.items():
            pro = data.PRONOUNS[x]
            when = when_words(("N", k), self.day)
            gone = (f"About {NAMES[x]}: {pro['he']} went {where[0]} {when} and has not come back." if where else
                    f"About {NAMES[x]}: {pro['he']} has been gone since {when}.")     # household_knowledge.md
            out.append({"with": f"About {NAMES[x]}: {pro['he']} was with you in the street {when}; you lost sight of "
                                f"{pro['him']} in the dark, and {pro['he']} has not come back.",
                        "saw": f"About {NAMES[x]}: you saw {pro['him']} go out {when}, and {pro['he']} has not come "
                               f"back.",
                        "heard": f"About {NAMES[x]}: {when} you heard the front door, and by morning {pro['he']} was "
                                 f"gone; {pro['he']} has not come back.",
                        "gone": gone}[how])
        return out

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
        return random.Random(self.food_string(t, pid)).random()

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
            d.update(mode=self.unasked(), invalid=why, option="silent", say=None)
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
        if self.is_player(q):
            d = self.played(q, t, opts, d, "given", f"{p.name} has just handed you one of the portions.")
            self.holding = None
            return d
        choice, why = self.ask_model(q, t, opts, d, f"{p.name} has just handed you one of the portions.")
        self.holding = None
        if not choice:
            d.update(mode=self.unasked(), invalid=why, option="refuse_given", say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    def decide_plate(self, q, server, t, given=False):
        """q's share of the meal is in front of them: eat it, give it to someone here, or put it back. A share that
        was given to them can only be eaten or put back."""
        his = data.PRONOUNS[q.id]["his"]
        if self.plates.get(q.id) == "cup":          # the water round: there is only the drinking of it
            opts = [Option("cup_drink", "drink your cup of water", kind="cup_drink")]
            line = f"{server.name} has handed you a cup of water." if server is not None else "Your cup of water is here."
        else:
            opts = [Option("plate_eat", "eat your share", kind="plate_eat")]
            if not given:
                opts += [Option(f"plate_to_{x.id}", f"give your share to {x.name}", kind="plate_to", target=x.id,
                                says=True) for x in self.others_here(q)]
            opts.append(Option("plate_back", "put your share back on the shelf", kind="plate_back", says=True))
            line = (f"{server.name} has set out the meal: your share is in front of you." if server is not None
                    else "Your share of the meal is set out for you.")
        triggers = [line] + [text for text, new in q.triggers if text != line]
        q.triggers = []
        d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts), "held_back": None,
             "plate": self.plates.get(q.id)}
        if self.is_player(q):
            return self.played(q, t, opts, d, "plate", line)
        choice, why = self.ask_model(q, t, opts, d, line)
        if not choice:
            d.update(mode=self.unasked(), invalid=why, option="plate_eat", say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    def hunger_rise(self, minutes, as_it_was):
        """How far hunger rises over these minutes, before the person's own rate. With a model: as it always was.
        In code mode: by the clock, `hunger_a_day` over 24 hours (content/weights.json, scenario)."""
        return as_it_was if self.hunger_a_day is None else self.hunger_a_day * minutes / 1440

    def full_days(self):
        return getattr(self.brain(), "full_days", False)

    def laid_up(self, pid):
        """Sick or hurt badly enough to keep to their bed (health.py): never with a model, or before week.py."""
        health = getattr(self.brain(), "health", None)
        return health is not None and health.level(pid) >= 2

    def meal_open(self):
        """Whether a meal can be set out now (code mode). On a full day: at the morning's and the evening's beat,
        once each. Otherwise once a morning."""
        if self.brain() is None or self.portions <= 0:
            return False
        if self.full_days():
            return self.beat in ("morning", "evening") and self.beat not in self.meals
        return self.meal_at is None

    def water_open(self):
        """On a full day with nothing on the shelf, the meal's hour is the water's: a cup each, once at each."""
        return (self.full_days() and self.portions <= 0 and self.beat in ("morning", "evening")
                and self.beat not in self.meals)

    def meal_size(self):
        """A meal's share: a portion each where there is one meal a day, half a portion where there are two."""
        return 0.5 if self.full_days() else 1.0

    def task_options(self, p):
        """The day's work (section 7.3), at the work beat: each task nobody has taken yet today, and looking after
        whoever is sick or hurt."""
        if self.beat != "work" or not self.full_days():
            return []
        tasks = self.brain().practices["tasks"]
        out = [Option(f"task_{name}", t["label"], kind="task", task=name, says=True)
               for name, t in tasks.items() if name not in self.tasks]
        health = self.brain().health
        for q in data.ORDER:
            if q != p.id and q not in self.away and health is not None and health.level(q) >= 1 \
                    and f"tend_{q}" not in self.tasks:
                out.append(Option(f"task_tend_{q}", f"look after {NAMES[q]}", kind="task", task=f"tend_{q}", target=q,
                                  says=True))
        return out

    def tidy_portions(self):
        """The shelf's count, whole where it is whole."""
        self.portions = int(self.portions) if self.portions == int(self.portions) else round(self.portions, 2)

    # ---------- what is inside them ----------
    def risen(self, p):
        """What has risen a level since they last decided with the model: "hunger", "guilt",
        "suspicion", or "grudge:<person>" for each grudge that rose."""
        now, seen = p.levels(), p.seen
        out = [k for k in ("hunger", "guilt", "suspicion", "fast", "debt", "thirst")
               if k in now and now[k] > seen.get(k, now[k])]
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
            elif k == "fast":
                out.append(f"fasting crossed a line (now {FAST_STAGE_WORD[p.needs['fast_stage']]})")
            elif k == "debt":
                out.append("sleep debt crossed a line (now exhausted)")
            elif k == "thirst":
                out.append(f"thirst crossed a line (now {THIRST_STAGE_WORD[p.needs['thirst_stage']]})")
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
        """Something `against` did to `holder`. Remembered as a fact, and a step up. Never for the player's person,
        whose grudges are the player's (reports/play_design.md §3); what was done to them is in their lines."""
        if self.is_player(holder):
            return
        holder.grudge(against.id).rise(minute, fact)
        record["grudges"].append((minute, holder.id, against.id, holder.grudges[against.id].strength, story))

    # ---------- what is inside them, as the prompt says it ----------
    def inside_lines(self, p, today=False):
        """Hunger in words; suspicion, grudges and guilt as the events behind them."""
        rose = self.risen(p)
        if p.needs is None:
            out = [f"Your body: {hunger_words(p.hunger)}."]
        else:                               # from day 3 (reports/quiet_day_design.md, §1)
            import quiet
            out = [quiet.body_line(hunger_words(p.hunger), p.needs["fast_stage"], p.needs["debt_stage"],
                                   thirst=p.needs.get("thirst_stage", 0), cold=p.needs.get("cold", False))]
        if "hunger" in rose:
            out.append("Since you last decided, you have grown hungrier.")
        if "fast" in rose:
            out.append("Since you last decided, you have grown weaker.")
        if "debt" in rose:
            out.append("Since you last decided, you have grown more tired.")
        if "thirst" in rose:
            out.append("Since you last decided, you have grown thirstier.")
        s = p.suspicion
        # What they know about the can wins over what their answers guessed. From day 2 on, a confession of an
        # earlier day says when (reports/night_design.md, §5.3; reports/days_design.md, §3.5).
        if p.knows_culprit == p.id:
            about = (f"About the can: you ate it yourself, and you admitted it "
                     f"{when_words(('D', day_index(p.confessed_day)), self.day)}."
                     if p.confessed and p.confessed_day not in (None, self.day)
                     else "About the can: you ate it yourself.")
        elif p.knows_culprit and p.confession_heard_day not in (None, self.day):
            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it "
                     f"{when_words(('D', day_index(p.confession_heard_day)), self.day)}, at "
                     f"{data.minute_words(p.confession_heard_at)}.")
        elif p.knows_culprit:
            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it at "
                     f"{data.minute_words(p.confession_heard_at)}.")
        elif s.strength and self.day != 4:
            when = []
            past = [(when_words(scene, self.day), ms) for scene, ms in p.suspected_past]
            own = "today" if today else "this morning"      # reports/stage_b_fixes.md, fix 3: as the grudge lines
            now = [(own, p.suspected_at)]
            if self.night_from() is not None:       # a quiet day's night: its answers are "tonight", never a minute
                day_ms = [mm for mm in p.suspected_at if mm < self.night_from()]
                now = [(own, day_ms)] + ([("tonight", True)] if len(day_ms) < len(p.suspected_at) else [])
            for word, ms in past + now:
                if ms is True:
                    when.append(word)
                elif ms:
                    ms = ms[-EVENTS_SHOWN:]
                    when.append(f"{word} {data.minutes_words(ms, self.clock_from())}")
            about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it"
                     + (", " + ", and ".join(when) if when else "") + ".")
        elif s.strength:
            about = (f"About the can ({LEVEL_WORDS[s.strength]}): you thought {NAMES[s.target]} took it, "
                     f"{data.minutes_words(p.suspected_at[-EVENTS_SHOWN:], self.clock_from())}.")
        else:
            about = "About the can: you have not settled on who took it."
        out.append(f"{about} {p.can_note}" if p.can_note else about)
        out += self.trip_lines(p)
        out += self.missing_lines(p)
        if p.water is not None:                     # W1: the water as they see it (quiet.py)
            out.append(p.water["line"])
        held = [(t, p.grudges[t]) for t in data.ORDER if t in p.grudges and p.grudges[t].strength]
        if not held:
            out.append("Against the others: nothing.")
        for t, g in held:
            facts = "; ".join(grudge_facts(NAMES[t], g.events, EVENTS_SHOWN, self.clock_from(), self.night_from(),
                                           "today" if today else None))
            out.append(f"Against {NAMES[t]} ({LEVEL_WORDS[g.strength]}): {facts}.")
        if p.guilt is not None:
            facts = ["you ate the can in the night, and nobody saw"]
            facts += [e[1] for e in p.guilt_events[-EVENTS_SHOWN:]]
            out.append(f"On your conscience ({LEVEL_WORDS[p.guilt]}): " + "; ".join(facts) + ".")
        return out

    # ---------- the prompt ----------
    def pattern(self, p):
        """How many turns in a row they have done the same kind of act, and how the others
        answered them in that time (lines aimed at them or at everyone)."""
        kind, n = self.repeating(p)
        if not n or kind == "routine":      # nothing done since a routine began (quiet.py)
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
                "reassure": f"reassured {target or 'everyone'}", "say": f"spoke to {target or 'everyone'}",
                "propose": "said someone should go to the neighbour's house tonight",
                "volunteer": "offered to go there tonight",
                "object": "said you should not be the one to go" if target else "said nobody should go",
                "back": "said you should be the one to go", "decline": "said they will not be the one to go",
                "talk": "talked about something that happened earlier", "tell": "told someone something they had missed",
                }.get(h["kind"], "spoke to everyone")

    def prompt_for(self, p, t, opts, lull=None, night=None, extra=None):
        """Every prompt is built with World out of reach (truth.prompting; reports/world_design.md, §1.2)."""
        import truth
        with truth.prompting():
            return self._prompt_for(p, t, opts, lull, night, extra)

    def _prompt_for(self, p, t, opts, lull=None, night=None, extra=None):
        """lull: for a lull moment, the minute the room was last stirred; None otherwise.
        night: the night's `Now` lines (reports/night_design.md, §3.2), which take the place of the
        room, the turn and the pattern block; None by day.
        extra: by day, a last `Now` line (a food moment's, or a handed portion's: reports/body_design.md,
        §2.4-§2.5); None otherwise."""
        s = p.sheet
        minute = None if night is not None else t * data.MINUTES_PER_TURN
        system = SYSTEM if night is None else NIGHT_SYSTEM
        calls = "; ".join(f"{self.people[q].name} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
        # Amendment 5 (reports/stage_b.md): a quiet day's own events, from minute 90 on and at its night, are "today".
        today = self.quiet is not None and (night is not None or minute >= data.CLOCK_FROM)
        inside = self.inside_lines(p, today)
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
        if self.quiet is not None:                 # W1, from day 3: the back door and the yard
            house = data.with_yard(house)
        if p.door is not None and p.door["options"]:      # W2a: the gap and the person at the door
            house = data.with_door(house)
        if p.knows_empty or p.id in self.street:   # stage B, W5: their places include the houses further along
            house = house.replace("the street and the neighbour's house",
                                  "the street, the neighbour's house and the houses further along the street")
        head += [f"The house: {data.HOUSE} {house}"]
        if night is not None:
            return self.prompt_parts(p, opts, head, list(night), system, "today", minute)
        # A quiet day from minute 90 on (reports/meeting_fixes.md): a meeting after an hour apart gets its own lines,
        # just before "Now", and the headings say "today".
        late = self.quiet is not None and minute >= data.CLOCK_FROM
        now = self.now_lines(p, t, minute, lull)
        if extra:
            now.append(extra)
        return self.prompt_parts(p, opts, head, now, system, "today" if late else "this morning", minute)

    def now_lines(self, p, t, minute, lull=None, screen=False):
        """What p perceives now, by day: the prompt's lines from "Now" to the pattern block. screen: the player's
        screen (reports/play_design.md §1.2-§1.4): a face names only the word that shows (L4), and the lines that are
        the model's aids (who acts first, the pattern block) are left out."""
        room = data.ROOMS[p.room]
        late = self.quiet is not None and minute >= data.CLOCK_FROM
        now = self.quiet.meeting_lines(p, minute) + self.quiet.evening_lines(p, minute) if late else []
        now += [f"Now, {data.minute_words(minute)}, you are in the {room}."]
        if p.rain_since is not None:                # W1: what they hear now
            now.append(RAIN_NOW_DAY)
        if p.door is not None:                      # W2a: what they perceive of the front door now (quiet.py)
            now += p.door["lines"]
        others = self.others_here(p)
        if not others:
            now.append("- Nobody else is here.")
        for q in others:
            look = f" {q.name} looks {face_word(q.feeling) if screen else q.feeling}." if self.shown(q, t) else ""
            now.append(f"- {q.name} is here, {q.activity['label']}.{look}")
        if p.room == "kitchen":
            now.append(f"- {self.portions} portion{'s' if self.portions != 1 else ''} on the shelf.")
        if lull is not None:
            now.append(f"Nothing has been said or done in the {room} since {data.minute_words(lull)}.")
        so_far = self.so_far[p.room] if self.so_far is not None else []
        if so_far:
            now.append(f"Said and done in the {room} this turn, before you, in order:")
            now += [f"{i}. {x if isinstance(x, str) else x.get(p.id, x[None])}" for i, x in enumerate(so_far, 1)]
        elif others and not screen:
            now.append(f"You are the first to act in the {room} this turn.")
        if not screen:
            now += self.pattern(p)
        return now

    def prompt_parts(self, p, opts, head, now, system, when, minute):
        """The rest of the prompt, trimmed to the budget. when: "this morning", or "today" at
        night (reports/night_design.md, §3.2) and on a quiet day from minute 90 on (minute is None at night)."""
        tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]

        back = list(p.backstory)
        morning = [f"{data.clock(m)}: {x}" for m, x in p.memory if m != minute]  # this turn is above
        morning += [f"tonight: {x}" for x in p.tonight]
        sure = "from today" if when == "today" and minute is None else when     # "from today" at night only
        pinned = [f"What you are sure of {sure}:"] + [f"- {x}" for x in p.sure]
        # What they were told today (reports/talk_design.md, A4): each belief, from the store, on its day and night.
        pinned += [f"- {data.clock(b['minute'])}: {b['claim']}" for b in p.beliefs if b["day"] == self.day]
        # While a tell is offered: where each listener was, as the teller perceived it (reports/tell_fix_impl.md).
        where = [f"- {x}" for x in topics.whereabouts(self, p, opts)] if self.quiet is not None else []
        pinned += where
        if p.said_lines:
            pinned += [f"Your own last words {when}:"] + [f"- {x}" for x in p.said_lines[-3:]]
        carry = self.carry.get(p.id, [])
        if self.quiet is not None and p.said_lines:
            # From day 3 on, last night's intent is shown until their first speech act of the day (reports/v22_fixes.md,
            # rule 2). Days 1 and 2 are as they were, so that v16's cache still answers them.
            carry = [x for x in carry if not x.startswith(INTENT_LINE)]
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
            # The door's words in the house line (W2a) are inside the budget, as its other lines are.
            block += max(0, len(house.replace(data.DOOR[1], data.DOOR[0])) - len(data.HOUSE_THINGS))
        block += sum(len(x) + 1 for x in carry)
        if self.quiet is not None:
            # W1 (reports/world_design.md, §6): the water line, the rain heard now, the water's options and the yard
            # sit outside the budget too, so that they never push a memory line out. The yard is in the house line,
            # which the trip block already counts once the trip concern has started.
            block += sum(len(x) + 1 for x in head + now if x.startswith("About water:") or x in W1_NOW)
            block += sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if o.id in W1_OPTIONS)
            # The topic options (reports/talk_design.md §5) sit outside the budget: they never push a memory out.
            block += sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in ("talk", "tell"))
            block += sum(len(x) + 1 for x in where)          # and so do the lines that come with a tell
            if not self.trip:
                block += len(data.YARD[1]) - len(data.YARD[0])
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
        self.last_block = block
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
        for pid, size in sorted(self.plates.items()):      # code mode: a share nobody came for goes back on the shelf
            if size == "cup":
                continue
            self.portions += size
            self.transcript.setdefault("plates_left", []).append([pid, size])
        self.plates = {}
        self.tidy_portions()
        self.transcript["final_rooms"] = {r: [q for q in data.ORDER if self.people[q].room == r]
                                          for r in data.ROOMS}
        if self.quiet is not None:
            self.transcript["quiet"] = self.quiet.transcript()
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
        self.now = minute
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
            before = {q.id: (len(q.memory), len(q.sure)) for q in self.people.values()}
            d["came_of_it"] = self.apply(p, opt, d, t, voices, record)
            if self.is_player(p):           # what reaches them from now on is new for "wait" (player.py)
                self.player.mark(self, p)
            # What each person got of this act, in their own lines (reports/days_design.md, §2.3, §4.2).
            got = {}
            for q in self.people.values():
                m0, s0 = before[q.id]
                memory = [x for _, x in q.memory[m0:]]
                sure = [data.unstamp(x)[1] for x in q.sure[s0:]]
                if memory or sure:
                    got[q.id] = {"memory": memory, "sure": sure}
            self.views[d["seq"]] = got
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
            for k in ("why", "mood"):       # code mode (brain.py): the reasons of the choice, and the day's mood
                if k in d:
                    entry[k] = d[k]
            tturn["acts"].append(entry)
            return opt, entry

        for room in data.ROOMS:
            remaining = list(self.present[room])
            rng = random.Random(self.order_string(t, room))
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
                elif opt.act["kind"] in ("meal", "meal_small", "water_round"):
                    # Everyone in the room answers now for their share, the one who set it out last: their decision
                    # for this turn if they had not acted yet. A share given on is answered at once too.
                    served = [x for x in self.present[room] if x != p.id] + [p.id]
                    for x in served:
                        q = self.people[x]
                        if x not in self.plates:
                            continue
                        if x in remaining:
                            remaining.remove(x)
                        place += 1
                        dq = self.decide_plate(q, p, t)
                        qopt, _ = act(q, dq, room, place, f"served by {p.name}")
                        if qopt.act["kind"] == "plate_to":
                            r = self.people[qopt.act["target"]]
                            place += 1
                            dr = self.decide_plate(r, q, t, given=True)
                            act(r, dr, room, place, f"given {q.name}'s share")
        record["rooms"] = {r: [(q.name, q.activity["label"]) for q in self.people.values()
                               if start_room[q.id] == r] for r in data.ROOMS}

        for p, to, partner in self.moves:
            p.room = to
            p.activity = {"kind": "idle", "label": "just come in"}
            self.last_stir[to] = minute         # coming in is something done in the room
        # Voices carry to everyone who did not hear the words, wherever they are at the end of
        # the turn, never into or out of the bathroom. Only a new line is a social moment for
        # someone who hears it through a wall.
        for room, new, heard_it, seq in voices:
            for q in self.people.values():
                if q.id in heard_it or q.room == room or q.room is None or data.SOUNDPROOF & {room, q.room}:
                    continue
                self.voices_heard.setdefault(seq, {})[q.id] = room
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
                if p.history:            # seen as part of the act that moved them (reports/days_design.md, §4.2)
                    view = self.views.setdefault(p.history[-1]["seq"], {})
                    view.setdefault(q.id, {"memory": [], "sure": []})["memory"].append(text + ".")
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
            p.hunger = min(1.0, p.hunger + self.hunger_rise(data.MINUTES_PER_TURN, 0.004 * data.MINUTES_PER_TURN)
                           * p.sheet["hunger_rate"])
        record["portions"] = self.portions
        self.log.append(record)
        self.transcript["turns"].append(tturn)

    def ask_model(self, p, t, opts, d, extra=None):
        """One model decision: the prompt, the answer, and what it does to their suspicion and
        grudge. They have now seen the levels their prompt showed. extra: a last `Now` line. From day 3, no more than
        the day's asks (quiet.py, §4)."""
        minute = t * data.MINUTES_PER_TURN
        if self.quiet is not None:
            if self.quiet.spent(p):
                return None, self.quiet.spent_why()
            full = self.quiet.door_full(p)          # a visit asks at most 18 of those at the door (door_heard_impl)
            if full:
                return None, full
            self.quiet.counted()
            self.quiet.door_asked(p)
        seen = p.levels()
        brain = self.brain()
        if brain is not None:       # code mode (brain.py): no prompt is built and no model is asked
            p.last_asked = minute
            choice = brain.decide(self, p, t, opts, d, extra)
            p.seen = seen
            d.update(mode="code", **choice)
            brain.settle(p, day_index(self.day), d)     # the heart sets their suspicion; no answer moves a level
            return choice, None
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
            p.suspected_past = []
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
        if self.is_player(p):
            return self.decide_player(p, t)
        minute = t * data.MINUTES_PER_TURN
        # From day 3 (quiet.py): a quiet trigger's ask waiting for them; nobody is asked once the day's asks are
        # spent; and someone out of every conversation, or resting, has no inner moment.
        quiet = self.quiet
        pending = quiet.pending.pop(p.id, None) if quiet is not None else None
        spent = quiet is not None and quiet.spent(p)
        inner_ok = quiet is None or pending is not None or (self.talking(p.room) and not quiet.resting(p.id))
        if p.id in self.plates and p.room == "kitchen":     # code mode: their share is set out and waiting
            return self.decide_plate(p, None, t)
        # The body's food moment comes before anything else (reports/body_design.md, §2.1).
        if not spent and self.food_due(p, t):
            return self.decide_food(p, t)
        opts = self.options_for(p)
        triggers = self.social_triggers(p, t)
        p.triggers = []
        if pending and pending["texts"]:
            triggers = pending["texts"] + [x for x in triggers if x not in pending["texts"]]
        kind, n = self.repeating(p)
        d = {"person": p.id, "triggers": triggers, "offered": len(opts),
             "held_back": kind if kind in SPEECH and n >= 3 else None}
        if pending:
            d["quiet"] = pending["kind"]
        if not triggers and inner_ok:
            rose = self.risen(p)
            forced = bool(pending) and pending["kind"] == "Q1"
            if rose and (forced or p.last_inner is None or minute - p.last_inner >= INNER_EVERY):
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
        # In code mode asking costs nothing, so nobody waits for a trigger: whoever is in a talk, or was asked for by
        # a quiet trigger, decides every played turn (Docs/fable-audit-2026-11.md, section 9, step 2a).
        free = self.brain() is not None and inner_ok
        if (triggers or d.get("inner_kinds") or "trip_moment" in d or "lull" in d or pending or free) and not spent:
            choice, why = self.ask_model(p, t, opts, d)
            if pending:
                quiet.asked(p.id)
            if not choice:
                d.update(mode=self.unasked(), invalid=why, option=self.routine(p, opts), say=None)
            elif free and d["option"] == self.routine(p, opts) and (d["option"] != "silent" or not (
                    triggers or d.get("inner_kinds") or "trip_moment" in d or "lull" in d or pending)):
                # They carried on as they were (still searching, still sitting with someone), or nothing called on
                # them and they stayed put: the rules' own, as it was before the brain was asked every turn. The
                # brain's reasons stay in the record. A silence kept when something did call on them is a choice.
                d["mode"] = "routine"
        else:
            d.update(mode="routine", option=self.routine(p, opts), say=None)
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    # ---------- the player (player.py; reports/play_design.md §1 to §4.1) ----------
    def decide_player(self, p, t):
        """The player decides for p every played turn (§4.1), unless their standing order is "wait" and nothing has
        reached p since their last act: then p keeps their routine, as anyone not asked does. No food, inner or lull
        moment, and no answer to read: nothing the player does moves a level of p's (§3)."""
        quiet = self.quiet
        pending = quiet.pending.pop(p.id, None) if quiet is not None else None
        if pending:
            quiet.asked(p.id)
        opts = self.options_for(p)
        reached = bool(p.triggers) or self.player.reached(self, p)
        triggers = self.social_triggers(p, t)
        p.triggers = []
        d = {"person": p.id, "triggers": triggers, "offered": len(opts), "held_back": None}
        if pending:
            d["quiet"] = pending["kind"]
        if p.id in self.trip_now:
            d["trip_moment"] = self.trip["minute"]
            d["trip_why"] = "; ".join(self.trip["why"])
        if self.player.waiting and not reached:
            d.update(mode="routine", option=self.routine(p, opts), say=None)
        else:
            d.update(self.player_choice(p, t, opts, "turn"))
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    def played(self, q, t, opts, d, kind, extra):
        """An aside or a handed portion, for the player's person (§2.4): the player's answer, not the model's."""
        d.update(self.player_choice(q, t, opts, kind, extra=extra))
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    def player_choice(self, p, t, opts, kind, night=None, extra=None):
        """Shows the player p's screen and asks again until their answer can be used (player.check); nothing happens
        meanwhile. Returns {"option", "say", "mode"}: "routine" for "wait" on a turn (§4.1), else "player"."""
        import player as playermod
        message = None
        tries = 0
        while True:
            # A script that keeps giving an answer the screen cannot take would be asked for ever, and every screen
            # is kept: stop it long before it can fill the memory. Nobody at a keyboard mistypes 200 times running.
            tries += 1
            if tries > 200:
                raise RuntimeError(f"the player's answer for a {kind} screen could not be used 200 times in a row; "
                                   f"the choices were {[o.id for o in opts]}")
            view = self.player_view(p, t, opts, night, extra)
            p.seen = p.levels()             # they have now seen how their body is
            answer = self.player.decide(self.player.screen(self, p, view, kind, message))
            if kind == "turn" and answer == playermod.WAIT:
                self.player.waiting = True
                return {"option": self.routine(p, opts), "say": None, "mode": "routine"}
            choice, message = ((None, playermod.UNKNOWN) if answer == playermod.WAIT else
                               playermod.check(answer, opts, night=night is not None))
            if choice:
                self.player.waiting = False
                self.player.chose(self, view, choice, next(o for o in opts if o.id == choice["option"]))
                return {**choice, "mode": "player"}

    def player_view(self, p, t, opts, night=None, extra=None):
        """p's own lines for the player's screen (§1.2, §1.3), built as a prompt is, with World out of reach
        (truth.prompting). Never another person's state but what "Now" shows of them, and never the lines that are
        the model's alone: the can as a stance, the grudges, the conscience, the pattern block."""
        import player as playermod
        import truth
        with truth.prompting():
            minute = None if night is not None else t * data.MINUTES_PER_TURN
            today = self.quiet is not None and (night is not None or minute >= data.CLOCK_FROM)
            inside = self.inside_lines(p, today)
            now = list(night) if night is not None else self.now_lines(p, t, minute, screen=True) + \
                ([extra] if extra else [])
            return {"day": day_index(self.day), "minute": minute, "room": p.room,
                    "body": [x for x in inside if x.startswith(("Your body:", "Since you last decided"))],
                    "know": [x for x in inside if x.startswith("About ") and not x.startswith(playermod.CAN_STANCE)],
                    "now": now, "memory": list(p.memory), "sure": list(p.sure), "sure_after": list(p.sure.after),
                    "beliefs": [b for b in p.beliefs if b["day"] == self.day],
                    "carry": list(self.carry.get(p.id, [])), "backstory": list(p.backstory),
                    "options": [(o.id, o.label, o.speech) for o in opts]}

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
        if self.is_player(q):
            return self.played(q, t, opts, d, "aside", f"{p.name} asks you to come aside to the {data.ROOMS[to]}.")
        choice, why = self.ask_model(q, t, opts, d)
        if not choice:
            d.update(mode=self.unasked(), invalid=why, option="refuse_aside", say=None)
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

    def spoken_to(self, p, kind, target, listener, listeners=None):
        """To whom p's line was said, as `listener` names it: "to you", "to <name>" or "to everyone"; a tell's listeners;
        at the front door, through it or to the person there (reports/play_fix1.md, fix 1)."""
        if kind == "tell" and listeners:
            told = ["you" if listener is not None and x == listener.id else NAMES[x] for x in listeners]
            return f"to {data._and(told)}"
        if kind == "door_refuse":
            return "to the person at the front door"
        if kind == "door_call":
            return ("through the front door" if p.door is None or p.door.get("door") != "open"
                    else "to the person on the step")
        if target is not None:
            return "to you" if listener is not None and target is listener else f"to {target.name}"
        return "to everyone"

    def line_text(self, p, kind, target, words, listener, while_doing=None, speech=True):
        """A line with words, as `listener` hears it (None: as the transcript keeps it). Speech is heard as words: who
        spoke, to whom and the words, never the act's gist; the act still drives every effect (reports/play_fix1.md,
        fix 1). Words said while doing something else are heard as said while doing it."""
        if speech:
            listeners = self.topic_line.get("listeners") if self.topic_line else None
            return f"{p.name}, {self.spoken_to(p, kind, target, listener, listeners)}: \"{words}\""
        aimed = ("you" if listener is not None and target is listener else target.name) if target else None
        if while_doing:
            return f"{p.name} says to {aimed or 'everyone'}, while {while_doing}: \"{words}\""
        return f"{p.name} says to everyone: \"{words}\""

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
        if d["mode"] in ("model", "code"):
            p.feeling = d["feeling"]
            p.feeling_until = t + FEELING_SHOWS_FOR_TURNS if outward(d["feeling"]) else -1
        target_id = aimed_at(opt.id) or (opt.act.get("target") if kind == "sit" else None)
        target = self.people[target_id] if target_id else None
        partner = self.people[opt.act["partner"]] if "partner" in opt.act else None
        given_to = self.people[opt.act["target"]] if kind == "give" else None
        mkind = opt.act.get("kind") if opt.act.get("kind") in MEAL_KINDS else None
        brain = self.brain()
        if brain is not None and not (kind in ("eat", "share") and self.portions <= 0):
            # Code mode: what each person in the room now remembers of this act (brain.CodeBrain.saw; heart.py).
            brain.saw(self, p, mkind or kind, target_id or (opt.act.get("target") if mkind else None),
                      [q.id for q in seen], partner.id if partner else None)
        # Anything but staying put in silence, or staying seated with the same person, stirs the room.
        if not (kind == "silent" or (kind == "sit" and p.activity["kind"] == "sitting"
                                     and p.activity["with"] == target_id)):
            self.last_stir[room] = minute
        p.history.append({"t": t, "kind": kind, "seq": self.seq})
        p.addressed = None
        p.owed = None
        p.aside_lead = None
        so_far = self.so_far[room]
        out = []

        if kind != "sit" and p.activity["kind"] == "sitting" and kind not in SPEECH:
            p.activity = {"kind": "idle", "label": "standing"}

        # The culprit accusing someone else of what they did is someone else accused in their
        # hearing.
        if culprit is not None and p is culprit and kind == "accuse":
            he = data.PRONOUNS[p.id]["he"]
            self.add_guilt(minute, f"you accused {target.name} of what you did, at {data.minute_words(minute)}",
                           f"{he} accused {target.name} of what {he} did", record)

        if kind in WATER_RULES and self.quiet is not None:      # W1: the house's rule, from this minute
            self.quiet.water_rule(p, kind, minute)
        door_line = None
        if kind in DOOR_KINDS and self.quiet is not None:       # W2a: what the act does at the door (quiet.py)
            door_line = self.quiet.door_act(p, kind, minute, d.get("say"))
        self.topic_line = opt.act if kind in ("talk", "tell") else None
        if kind == "tell":                  # reports/talk_design.md: each listener gets a belief (topics.py, A3)
            d["tell"] = topics.tell(self, p, opt.act["listeners"], opt.act["topic"], minute, d.get("say"))
        elif kind == "talk":
            topics.chose(self, p, opt.act["topic"], minute)
        words = d.get("say")
        if words:
            doing = {"door_look": "looking through the gap in the boards", "door_open": "unbarring the front door",
                     "door_give": "handing water out at the front door",
                     "collect_rain": "going out into the rain with the bin","go": f"leaving for the {data.ROOMS.get(opt.act.get('to'), '')}",
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
            if self.is_player(p):           # reports/play_design.md §5.1, change 1: someone spoken to answers
                new, why = True, "the player's words"
            d["new"], d["new_why"] = new, why
            if new:
                self.started_by(room, minute, f"{p.name}: {why}", d)
            text = self.line_text(p, spoken_kind, target if aimed else None, words, None,
                                  None if opt.speech else doing, opt.speech)
            self.said.append({"minute": minute, "room": data.ROOMS[room], "who": p.name,
                              "to": (target.name if aimed else data._and([NAMES[x] for x in opt.act["listeners"]])
                                     if kind == "tell" else "everyone"), "text": text,
                              "words": words, "new": new, "why": why})
            line = {None: text}         # this turn's line as each one here heard it ("you" to whom it was said)
            so_far.append(line)
            for q in seen:
                heard = self.line_text(p, spoken_kind, target if aimed else None, words, q,
                                       None if opt.speech else doing, opt.speech)
                line[q.id] = heard
                # An accusation or a confession turns every head: it counts whether or not it is new, and whoever was
                # searching or sitting stops (reports/play_fix2.md, fix 2).
                self.perceive(q, minute, heard, trigger=(heard, new or kind in HEADS_TURN))
                if kind in HEADS_TURN and q.activity["kind"] in ("searching", "sitting"):
                    q.activity = {"kind": "idle", "label": "standing"}
                q.heard.append({"seq": self.seq, "who": p.id, "kind": spoken_kind,
                                "target": target_id if aimed else None})
                if (aimed and q is target) or (kind == "tell" and q.id in opt.act["listeners"]):
                    q.addressed = {"seq": self.seq, "who": p.id, "accused": kind == "accuse"}
                if aimed and q is target and kind in OWES_ANSWER:       # reports/play_fix2.md, fix 1
                    q.owed = {"who": p.id, "turn": t, "room": room}
                if kind in ("ask", "accuse"):
                    q.heard_question = True
                if kind == "confess":
                    if q.knows_culprit is None:
                        q.confession_heard_at = minute
                        q.confession_heard_day = self.day
                    q.knows_culprit = p.id
                    q.sure.append(f"{data.clock(minute)}: {p.name} admitted taking the can: \"{words}\" "
                                  "(you heard it)")
                    # Whoever was accused of it today, falsely, now knows who was wrong, and what to turn to (fix 3).
                    for x, said_at in q.accused_by.items():
                        if q is not p and q.accused_day.get(x) == self.day:
                            q.sure.append(f"{data.clock(minute)}: {NAMES[x]} accused you of taking it at "
                                          f"{data.minute_words(said_at)}. It was {p.name}.")
                            if x not in q.wronged:
                                q.wronged.append(x)
                    # Grudges: it was admitted after being denied to them, or after accusing them. A denial or
                    # accusation of an earlier day says when (reports/night_design.md, §5.1; days_design.md, §3.5).
                    def at(day):
                        return "at" if day in (None, self.day) else f"{when_words(('D', day_index(day)), self.day)} at"
                    if p.id in q.denials_heard:
                        when = at(q.denial_day.get(p.id))
                        self.add_grudge(q, p, minute,
                                        f"{p.name} admitted taking it at {data.minute_words(minute)}, after "
                                        f"denying it to you {when} {data.minute_words(q.denials_heard[p.id])}",
                                        f"{p.name} admitted it after denying it to {q.name}", record)
                    if p.id in q.accused_by:
                        when = at(q.accused_day.get(p.id))
                        self.add_grudge(q, p, minute,
                                        f"{p.name} had accused you of it {when} {data.minute_words(q.accused_by[p.id])}",
                                        f"{p.name} had accused {q.name} of it", record)
                if kind == "reveal" and q.knows_culprit is None and q.id != p.knows_culprit:
                    # Told by someone who heard it owned up to: they know now, and hold the denial against the one
                    # who made it to them.
                    who = self.people[p.knows_culprit]
                    q.knows_culprit = who.id
                    q.confession_heard_at = minute      # when they learned it (not heard from the one who took it)
                    q.sure.append(f"{data.clock(minute)}: {p.name} said that {who.name} took the can and has owned "
                                  f"up to it (you heard it)")
                    if who.id in q.denials_heard:
                        self.add_grudge(q, who, minute, f"{who.name} took the can, after denying it to you",
                                        f"{who.name} had denied it to {q.name}", record)
                if kind == "deny":
                    q.denials_heard[p.id] = minute
                    q.denial_day[p.id] = self.day
                if kind == "accuse" and q is target:
                    q.accused_by[p.id] = minute
                    q.accused_day[p.id] = self.day
                    if q.id != self.culprit:        # a false accusation
                        self.add_grudge(q, p, minute,
                                        f"{p.name} accused you of taking the can at {data.minute_words(minute)}, "
                                        f"and you had not",
                                        f"{p.name} accused {q.name} falsely", record)
                # The culprit's guilt: someone else accused of what they did in their hearing, or
                # someone reassuring them personally. Their denials and reassurance of everyone
                # add nothing.
                if culprit is not None and q is culprit and p is not culprit:
                    pro = data.PRONOUNS[q.id]
                    if kind == "accuse" and target is not culprit:
                        self.add_guilt(minute, f"{p.name} accused {target.name} of what you did, "
                                               f"at {data.minute_words(minute)}",
                                       f"{p.name} accused {target.name} of what {pro['he']} did", record)
                    elif kind == "reassure" and target is culprit:
                        self.add_guilt(minute, f"{p.name} reassured you, at {data.minute_words(minute)}",
                                       f"{p.name} reassured {pro['him']}", record)
            voices.append((room, new, {p.id} | {q.id for q in seen}, self.seq))
            mine = {"ask": "asked who took it", "deny": "denied taking it",
                    "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
                    "confront": f"confronted {target.name if target else ''}",
                    "reassure": f"reassured {target.name if aimed else 'everyone'}",
                    "say": f"spoke to {target.name}" if aimed else "said",
                    "propose": "said someone should go to the neighbour's house tonight",
                    "volunteer": "offered to go there tonight",
                    "object": (f"said {target.name} should not be the one to go" if target
                               else "said nobody should go out tonight"),
                    "back": f"said {target.name if target else ''} should be the one to go",
                    "decline": "said you will not be the one to go",
                    "propose_far": "said someone should try the houses further along the street tonight",
                    "volunteer_far": "offered to go further along the street tonight",
                    "save_water": "said nobody should use the stored water for washing or the toilet any more",
                    "ration_water": "said the water must be shared out by the cup from now on",
                    "door_call": "called out through the front door",
                    "door_refuse": "told the person at the door to go away",
                    # an act at the door with words (reports/door_memory_impl.md): what they did, not "said"
                    "door_look": "looked through the gap in the boards", "door_open": "unbarred the front door",
                    "door_give": "handed water out at the front door",
                    # reports/talk_design.md: a topic, as the speaker perceived it
                    "talk": f"talked about {opt.act.get('referent')}",
                    "tell": (f"told {data._and([NAMES[x] for x in opt.act['listeners']])} about "
                             f"{opt.act['referent']}" if kind == "tell" else None)}.get(kind, "said")
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
                    if kind in ("propose", "volunteer", "back", "propose_far", "volunteer_far"):
                        x.trip_raised = True
                if kind == "propose":
                    p.proposed = True
            # Their own lines reach them without the words: minute and verb only
            # (reports/repetition_probe.md, variant B). The others hear the words.
            p.memory.append((minute, f"you {mine}.{feel}"))
            p.said_lines.append(f"{data.clock(minute)}, you {mine}.")
            if kind in ("ask", "accuse"):
                p.heard_question = True
            if kind == "confess":
                p.confessed = True
                p.confessed_day = self.day
                p.sure.append(f"{data.clock(minute)}: you admitted aloud that you took the can"
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
            if self.quiet is not None and p.id in self.quiet.open:      # in a routine (quiet.py): it goes on
                so_far.append(f"{p.name} is {p.activity['label']}.")
            else:
                p.activity = {"kind": "idle", "label": "staying put"}
                so_far.append(f"{p.name} stays put and says nothing.")
            if d["mode"] in ("model", "player", "code"):
                p.memory.append((minute, f"you stayed where you were and said nothing.{feel}"))
            return "stayed where they were" + (" (its line was dropped: silent means no words)"
                                               if d.get("dropped_line") else "") + "."
        if mkind in ("meal", "meal_small"):         # code mode: the meal is set out, a share for everyone at home
            his = data.PRONOUNS[p.id]["his"]
            home = [q for q in data.ORDER if q not in self.away]
            size = min(self.meal_size() if mkind == "meal" else self.meal_size() / 2, self.portions / len(home))
            self.portions -= size * len(home)
            self.tidy_portions()
            for x in home:
                self.plates[x] = self.plates.get(x, 0) + size
            self.meal_at = minute
            self.meals.add(self.beat)
            what = MEAL_WORDS.get(size, "what there is, shared")
            # Whoever is laid up is brought their share where they lie, and eats it there.
            for x in home:
                q = self.people[x]
                if self.laid_up(x) and q.room != room:
                    got = self.plates.pop(x)
                    q.hunger = max(0.0, q.hunger - self.relief * got)
                    q.eaten += got
                    q.last_meal = minute
                    if self.quiet is not None:
                        self.quiet.ate(q, minute)
                    q.memory.append((minute, f"{p.name} brought you your share of the meal, and you ate it."))
                    record["events"].append(f"{p.name} took {q.name} {data.PRONOUNS[x]['his']} share")
            trig = f"{p.name} sets out the meal: {what} each"
            p.activity = {"kind": "idle", "label": "setting out the meal"}
            so_far.append(trig + ".")
            for q in seen:
                q.sure.append(f"{data.clock(minute)}: {trig}. {portions_text(self.portions)} left on the shelf "
                              f"(you saw it).")
            fact(f"{p.name} set out the meal", trig)
            p.sure.append(f"{data.clock(minute)}: you set out the meal: {what} each. {portions_text(self.portions)} "
                          f"left on the shelf.")
            record["events"].append(f"{p.name} set out the meal: {what} each")
            return f"set out the meal: {what} each; {self.portions} left."
        if mkind == "water_round":                  # code mode: no food, so the hour is the water's
            home = [q for q in data.ORDER if q not in self.away]
            for x in home:
                if self.laid_up(x) and self.people[x].room != room:
                    self.people[x].memory.append((minute, f"{p.name} brought you a cup of water."))
                else:
                    self.plates[x] = "cup"
            self.meals.add(self.beat)
            p.activity = {"kind": "idle", "label": "handing out the water"}
            trig = f"{p.name} hands out the water: a cup each"
            so_far.append(trig + ".")
            for q in seen:
                self.perceive(q, minute, trig + ".")
            p.memory.append((minute, f"you handed out the water: a cup each.{feel}"))
            record["events"].append(f"{p.name} handed out the water")
            return "handed out the water: a cup each."
        if mkind == "cup_drink":
            self.plates.pop(p.id, None)
            p.activity = {"kind": "idle", "label": "drinking"}
            so_far.append(f"{p.name} drinks.")
            p.memory.append((minute, f"you drank your cup of water.{feel}"))
            return "drank."
        if opt.act.get("kind") == "look_out":      # code mode: watching the street for whoever did not come back
            p.activity = {"kind": "idle", "label": "watching the street through the gap in the boards"}
            so_far.append(f"{p.name} stands at the gap in the boards, watching the street.")
            for q in seen:
                self.perceive(q, minute, f"{p.name} stands at the gap in the boards, watching the street.")
            p.memory.append((minute, f"you stood at the gap in the boards and watched the street.{feel}"))
            return "watched the street."
        if opt.act.get("kind") == "task":          # code mode: one of the day's tasks (section 7.3)
            name = opt.act["task"]
            self.tasks[name] = p.id
            to = self.people[opt.act["target"]] if opt.act.get("target") else None
            spec = brain.practices["tasks"].get(name) or brain.practices["tend"]
            did = spec["did"].format(name=to.name if to else "")
            p.activity = {"kind": "idle", "label": spec["doing"].format(name=to.name if to else "")}
            so_far.append(f"{p.name} {did}.")
            for q in seen:
                self.perceive(q, minute, f"{p.name} {did}.")
            came = brain.did_task(self, p, name, to.id if to else None, minute)
            p.memory.append((minute, f"you {did}.{feel}"))
            if name == "stores":            # whoever counts says the count: everyone here now knows it
                for q in [p] + seen:
                    q.sure.append(f"{data.clock(minute)}: {'you' if q is p else p.name} counted the stores: "
                                  f"{portions_text(self.portions)} on the shelf.")
            record["events"].append(f"{p.name} {did}" + (f" ({came})" if came else ""))
            return f"{did}." + (f" {came}" if came else "")
        if mkind == "plate_eat":
            his = data.PRONOUNS[p.id]["his"]
            size = self.plates.pop(p.id, 0)
            p.activity = {"kind": "idle", "label": "eating"}
            p.hunger = max(0.0, p.hunger - self.relief * size)
            p.eaten += size
            p.last_meal = minute
            if self.quiet is not None:
                self.quiet.ate(p, minute)
            so_far.append(f"{p.name} eats {his} share.")
            for q in seen:
                self.perceive(q, minute, f"{p.name} eats {his} share.")
            p.memory.append((minute, f"you ate your share.{feel}"))
            record["events"].append(f"{p.name} ate {his} share")
            return f"ate {his} share."
        if mkind == "plate_to":
            his = data.PRONOUNS[p.id]["his"]
            to = self.people[opt.act["target"]]
            size = self.plates.pop(p.id, 0)
            self.plates[to.id] = self.plates.get(to.id, 0) + size
            p.activity = {"kind": "idle", "label": f"giving {his} share to {to.name}"}
            line = f"{p.name} gives {his} share to {to.name}"
            so_far.append(line + ".")
            for q in seen:
                q.sure.append(f"{data.clock(minute)}: {p.name} gave {his} share of the meal to "
                              f"{'you' if q is to else to.name} (you saw it).")
            fact(f"{p.name} gave {his} share to {to.name}", line)
            p.sure.append(f"{data.clock(minute)}: you gave your share of the meal to {to.name}.")
            record["events"].append(f"{p.name} gave {his} share to {to.name}")
            return f"gave {his} share to {to.name}."
        if mkind == "plate_back":
            his = data.PRONOUNS[p.id]["his"]
            size = self.plates.pop(p.id, 0)
            self.portions += size
            self.tidy_portions()
            p.activity = {"kind": "idle", "label": "standing"}
            line = f"{p.name} puts {his} share back on the shelf and does not eat"
            so_far.append(line + ".")
            for q in seen:
                q.sure.append(f"{data.clock(minute)}: {p.name} put {his} share of the meal back on the shelf and did "
                              f"not eat (you saw it).")
            fact(f"{p.name} put {his} share back", line)
            p.sure.append(f"{data.clock(minute)}: you put your share of the meal back on the shelf and did not eat.")
            record["events"].append(f"{p.name} put {his} share back on the shelf")
            return f"put {his} share back on the shelf; {self.portions} left."
        if kind == "collect_rain":                  # W1: out the back door and back, within the turn
            seen_text = (f"{p.name} goes out the back door into the rain and sets the bin under the drainpipe in the "
                         f"yard.")
            so_far.append(seen_text)
            if seen:
                self.started_by(room, minute, f"{p.name} set the bin out in the rain", d)
            for q in seen:
                self.perceive(q, minute, seen_text, trigger=(seen_text.rstrip("."), True))
            p.memory.append((minute, f"you went out the back door into the rain and set the bin under the drainpipe "
                                     f"in the yard.{feel}"))
            self.quiet.collect_rain(p, minute)
            return "went out into the rain and set the bin under the drainpipe."
        if kind in ("door_look", "door_open", "door_give"):      # W2a: at the front door, within the turn
            seen_text = {"door_look": f"{p.name} looks through the gap in the boards beside the front door.",
                         "door_open": f"{p.name} unbars the front door and opens it.",
                         "door_give": f"{p.name} hands some of the stored water out at the front door."}[kind]
            so_far.append(seen_text)
            if seen:
                self.started_by(room, minute, seen_text.rstrip("."), d)
            for q in seen:
                self.perceive(q, minute, seen_text, trigger=(seen_text.rstrip("."), True))
            p.memory.append((minute, (door_line or f"you {KIND_DONE[kind]}.") + feel))
            return {"door_look": "looked through the gap in the boards.", "door_open": "unbarred the front door.",
                    "door_give": "handed some of the stored water out at the front door."}[kind]
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
                p.sure.append(f"{data.clock(minute)}: you finished searching the {data.ROOMS[room]}: "
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
            took = min(1, self.portions)        # in code mode the shelf can hold less than a portion: never below 0
            self.portions -= took
            self.tidy_portions()
            p.hunger = max(0.0, p.hunger - self.relief * took)
            p.eaten += took
            p.last_meal = minute
            if self.quiet is not None:          # fasting counts from this meal (reports/w1_fixes.md, fix 1)
                self.quiet.ate(p, minute)
            so_far.append(f"{p.name} eats one of the portions.")
            for q in seen:
                q.sure.append(f"{data.clock(minute)}: {p.name} ate one of the portions (you saw it).")
                # A grudge toward someone who eats in front of you while you are hungry.
                if hunger_level(q.hunger) >= 1:
                    self.add_grudge(q, p, minute,
                                    f"{p.name} ate a portion in front of you at {data.minute_words(minute)}, "
                                    f"while you were hungry",
                                    f"{p.name} ate in front of {q.name}, who was hungry", record)
            fact(f"{p.name} ate one of the portions", f"{p.name} eats one of the portions")
            p.sure.append(f"{data.clock(minute)}: you ate one of the portions. {self.portions} left.")
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
                q.hunger = max(0.0, q.hunger - self.relief * each)
                q.eaten += each
                q.last_meal = minute
                if self.quiet is not None:
                    self.quiet.ate(q, minute)
            n, self.portions = self.portions, 0
            self.meals.add(self.beat)           # on a full day, sharing out the last of it is that hour's meal
            trig = f"{p.name} shares out the last {n} portion{'s' if n != 1 else ''} between {names}"
            so_far.append(trig + ".")
            for q in seen:
                q.sure.append(f"{data.clock(minute)}: {trig}; you had your part.")
            fact(f"{p.name} shared out the food", trig)
            p.sure.append(f"{data.clock(minute)}: you shared out the last {n} portions between {names}.")
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
            p.hunger = max(0.0, p.hunger - self.relief)
            p.eaten += 1
            p.last_meal = minute
            if self.quiet is not None:
                self.quiet.ate(p, minute)
            line = f"{giver.name} gives one of the portions to {p.name}, and {p.name} eats it"
            so_far.append(line + ".")
            for q in seen:
                if q is giver:
                    q.sure.append(f"{data.clock(minute)}: you gave one of the portions to {p.name}, and {p.name} ate it. "
                                  f"{self.portions} left.")
                    continue
                q.sure.append(f"{data.clock(minute)}: {giver.name} gave one of the portions to {p.name}, and {p.name} "
                              f"ate it (you saw it).")
                # Watching someone eat while hungry, as for `eat`; not the giver, who chose it.
                if hunger_level(q.hunger) >= 1:
                    self.add_grudge(q, p, minute,
                                    f"{p.name} ate a portion {giver.name} gave {him}, in front of you at "
                                    f"{data.minute_words(minute)}, while you were hungry",
                                    f"{p.name} ate the portion {giver.name} gave {him} in front of {q.name}, "
                                    f"who was hungry", record)
            fact(f"{p.name} ate the portion {giver.name} gave {him}", line)
            p.sure.append(f"{data.clock(minute)}: {giver.name} gave you one of the portions, and you ate it. "
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
                    q.sure.append(f"{data.clock(minute)}: you gave one of the portions to {p.name}, and {p.name} put it "
                                  f"back on the shelf.")
                    self.perceive(q, minute, None, remember=False,
                                  trigger=(f"{p.name} puts the portion you gave back on the shelf", True))
                else:
                    q.sure.append(f"{data.clock(minute)}: {giver.name} gave one of the portions to {p.name}, and "
                                  f"{p.name} put it back on the shelf (you saw it).")
                    self.perceive(q, minute, None, remember=False, trigger=(line, True))
            p.sure.append(f"{data.clock(minute)}: {giver.name} gave you one of the portions, and you put it back on "
                          f"the shelf.")
            record["events"].append(f"{p.name} put back the portion {giver.name} gave {him}")
            return f"put the portion {giver.name} gave {him} back on the shelf; {self.portions} left."
        return ""
