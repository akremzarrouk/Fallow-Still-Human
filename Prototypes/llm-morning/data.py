"""The family, the house and what happened before the morning.

Copied by hand from the shipped data so the prototype never reads Assets/:
  people      Assets/_Project/Data/Minds/*.json (age, role, note, traits, values, hunger rate)
  house       Assets/_Project/Data/Scenario/morning.json (the kitchen and the private rooms)
  start       morning.json `start` and `opening`
  scenarios   morning.json `variants`: daniel_ate_it, mara_ate_it, miscount (the night, and who
              took the can, if anyone)
  backstory   Assets/_Project/Data/Scenario/backstory.json (who did, saw or heard each event)
Ages and family roles match Docs/understanding/target-morning.md. Nothing else from that
file is used anywhere in the prototype.
"""
import re

ORDER = ["daniel", "elena", "leo", "mara"]

PEOPLE = {
    "daniel": {
        "name": "Daniel", "age": 25, "role": "the eldest son", "role_short": "eldest son",
        "note": "Older brother. Takes charge because he is frightened, not because he is sure. "
                "Proud, poor at reading a room, genuinely protective. Believes responsibility "
                "is his by right of age.",
        "traits": {"cautious": 0.35, "dominant": 0.85, "empathetic": 0.5, "impulsive": 0.6,
                   "proud": 0.85, "anxious": 0.65, "honest": 0.5},
        "values": ["being in control", "being respected", "keeping the family safe"],
        "hunger": 0.55, "hunger_rate": 1.15,
    },
    "elena": {
        "name": "Elena", "age": 42, "role": "the mother", "role_short": "mother",
        "note": "Mother. Reads everyone, says little, holds it in. Will lie to keep the family "
                "whole. Fears the household breaking apart more than she fears the outside. "
                "Gentle by habit, but she will not be accused or talked down to by her own children; "
                "when wronged, she says so plainly.",
        "traits": {"cautious": 0.7, "dominant": 0.5, "empathetic": 0.9, "impulsive": 0.25,
                   "proud": 0.35, "anxious": 0.75, "honest": 0.7},
        "values": ["keeping the family safe", "closeness", "fairness"],
        "hunger": 0.60, "hunger_rate": 0.85,
    },
    "leo": {
        "name": "Leo", "age": 21, "role": "the younger son", "role_short": "younger son",
        "note": "Calm, rational, reads people well, knows survival. Annoyance shows as "
                "withdrawal and dry correction, not volume.",
        "traits": {"cautious": 0.7, "dominant": 0.35, "empathetic": 0.7, "impulsive": 0.2,
                   "proud": 0.5, "anxious": 0.25, "honest": 0.8},
        "values": ["keeping the family safe", "fairness", "deciding for yourself", "closeness"],
        "hunger": 0.45, "hunger_rate": 1.0,
    },
    "mara": {
        "name": "Mara", "age": 17, "role": "the youngest, the daughter", "role_short": "youngest",
        "note": "Younger sister. Frightened and easy to read, but old enough to resent being "
                "handled like a child. Everything she feels reaches her face before she decides "
                "to show it.",
        "traits": {"cautious": 0.5, "dominant": 0.25, "empathetic": 0.75, "impulsive": 0.7,
                   "proud": 0.55, "anxious": 0.8, "honest": 0.55},
        "values": ["closeness", "deciding for yourself", "fairness"],
        "hunger": 0.50, "hunger_rate": 0.95,
    },
}

ROOMS = {
    "kitchen": "kitchen",
    "brothers_room": "brothers room",
    "back_room": "back room",
    "bathroom": "bathroom",
}
ROOM_NOTES = {
    "kitchen": "the food is kept here",
    "brothers_room": "Daniel and Leo's room",
    "back_room": "Elena and Mara's room",
    "bathroom": "nothing is heard in or out of it",
}
# Whose room each private room is (morning.json `owners`).
OWNERS = {"brothers_room": ("leo", "daniel"), "back_room": ("elena", "mara")}
# Voices carry between rooms, but not into or out of the bathroom (morning.json: the
# only connection that is not audible is the bathroom's).
SOUNDPROOF = {"bathroom"}

PORTIONS = 2
MINUTES = 90
MINUTES_PER_TURN = 3

# How a minute of the day is written (reports/quiet_day_fixes.md, fix 3): before minute 90 as it always was; from
# minute 90 on (the quiet day's, from day 3) as the clock, minute 00 being 07:00. Days 1 and 2 end before minute 90.
CLOCK_FROM = 90
DAY_START = 7 * 60


def clock(minute):
    """The stamp of a record, a memory line or a fact: "min 18", or "10:21" from minute 90 on."""
    if minute < CLOCK_FROM:
        return f"min {minute:02d}"
    h, m = divmod(DAY_START + minute, 60)
    return f"{h:02d}:{m:02d}"


def minute_words(minute):
    """A minute in a sentence: "minute 18", or "10:21" from minute 90 on ("at " + it, "since " + it)."""
    return f"minute {minute:02d}" if minute < CLOCK_FROM else clock(minute)


def _and(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def minutes_words(ms, clock_from=CLOCK_FROM):
    """"at minute 03", "at minutes 03 and 06", "at 10:21", "at minute 03, and at 10:21 and 10:24". clock_from=None
    for a list of days 1 and 2, whose minute 90 is the night's answers' (world.NIGHT_MINUTE), not a time of day."""
    if clock_from is None:
        return f"at minute{'s' if len(ms) > 1 else ''} {_and([f'{m:02d}' for m in ms])}"
    before = [f"{m:02d}" for m in ms if m < CLOCK_FROM]
    after = [clock(m) for m in ms if m >= CLOCK_FROM]
    parts = ([f"at minute{'s' if len(before) > 1 else ''} {_and(before)}"] if before else []) + \
            ([f"at {_and(after)}"] if after else [])
    return ", and ".join(parts)


def minutes_list(ms):
    """A list in brackets: "min 03, 06", "min 03, 10:21", "10:21, 10:24"."""
    before = [f"{m:02d}" for m in ms if m < CLOCK_FROM]
    after = [clock(m) for m in ms if m >= CLOCK_FROM]
    return ", ".join((["min " + ", ".join(before)] if before else []) + after)


def unstamp(line):
    """(minute, the rest) of a line stamped by clock(); (None, line) if it has no stamp."""
    m = re.match(r"^(?:min (\d+)|(\d\d):(\d\d)): (.*)$", line, flags=re.S)
    if not m:
        return None, line
    minute = int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - DAY_START
    return minute, m.group(4)

HOUSE = ("The family has shut itself in the house. The water has stopped. Food is short. "
         "Rooms: " + "; ".join(f"{ROOMS[r]} ({ROOM_NOTES[r]})" for r in ROOMS) + ".")

# Every thing and place the house has, as the backstory and the scenario establish them.
# The model is told that nothing else exists.
HOUSE_THINGS = (
    "The only places and things there are: the kitchen, with the pantry shelf where the food "
    "is kept, the counter and the dry taps; the brothers room, with Daniel's and Leo's beds; "
    "the back room, with Elena's and Mara's beds and Mara's bag; the bathroom; the doors "
    "between the rooms; the front door and the front windows, boarded up. Outside, and not "
    "to be gone to: the street and the neighbour's house. Do not mention any other object "
    "or place.")
# W1 (reports/world_design.md, §6, amendment 3): from day 3, the kitchen has a back door to a small walled yard with
# the drainpipe and the bin. There is no stove.
YARD = ("the counter and the dry taps;",
        "the counter, the dry taps and the back door to the yard; the yard behind the kitchen, small and walled, with "
        "the drainpipe and the bin;")
assert HOUSE_THINGS.count(YARD[0]) == 1


def with_yard(house_things):
    return house_things.replace(*YARD)


# W2a (reports/w2_design.md, §0.4 O1, §7.2): while someone is at the front door, the house line names the gap in the
# boards and the person there, since it says "Do not mention any other object or place".
DOOR = ("the front door and the front windows, boarded up.",
        "the front door and the front windows, boarded up, with a gap in the boards by the front door; the person at "
        "the front door.")
assert HOUSE_THINGS.count(DOOR[0]) == 1


def with_door(house_things):
    return house_things.replace(*DOOR)


# After the trip concern starts (reports/trip_design.md, §2.2): the trip the options speak of is
# tonight, and nobody goes out this morning.
HOUSE_THINGS_AFTER_TRIP = HOUSE_THINGS.replace("Outside, and not to be gone to:",
                                               "Outside, and not to be gone to this morning:")
assert HOUSE_THINGS_AFTER_TRIP != HOUSE_THINGS
# At night (reports/night_design.md, §3.2): tonight is when the plan said someone might go, so the
# line no longer forbids it.
HOUSE_THINGS_NIGHT = HOUSE_THINGS.replace("Outside, and not to be gone to:", "Outside:")
assert HOUSE_THINGS_NIGHT != HOUSE_THINGS

# The afternoon, skipped (reports/night_design.md, §2).
GAP = "The afternoon and evening passed in the house. Nobody ate."

# What everyone learns when the trip concern starts (reports/trip_design.md, §2.1): conclusions
# the code draws, told after their "About the can:" line.
# True next to the shelf's count, whatever it is (reports/play_fix1.md, fix 5).
ABOUT_FOOD = "About food: there is no food in the house but what is on the shelf; once it is eaten, there is nothing."
ABOUT_NEIGHBOUR = ("About the neighbour's house: its people left in the first days and nobody has been "
                   "inside since, so there may be food there. Outside is dangerous.")

# How each of them speaks to the others.
ADDRESS = {
    "daniel": {"elena": "Mom", "leo": "Leo", "mara": "Mara"},
    "elena": {"daniel": "Daniel", "leo": "Leo", "mara": "Mara"},
    "leo": {"elena": "Mom", "daniel": "Daniel", "mara": "Mara"},
    "mara": {"elena": "Mom", "daniel": "Daniel", "leo": "Leo"},
}

# The scenarios: morning.json `variants`, each with its night (nobody saw it) and who took the
# can. "Nobody sees." is added to each night as it was to daniel_ate_it's from the start.
SCENARIOS = {
    "daniel_ate_it": {
        "culprit": "daniel",
        "night": (3, "In the night Daniel eats a can standing at the counter in the dark. Nobody sees.",
                  {"daniel": "did"}),
    },
    "mara_ate_it": {
        "culprit": "mara",
        "night": (3, "In the night Mara eats a can sitting on the kitchen floor. Nobody sees.",
                  {"mara": "did"}),
    },
    "miscount": {             # nobody took anything; there were only ever two
        "culprit": None,
        "night": None,
    },
}
# Not in the shipped data: daniel_ate_it, and Leo heard the night from his bed but did not see
# who (reports/witness_design.md). It is told to Leo alone, at the end of his "About the can:"
# line (reports/witness_probe.md, variant B), so it names nobody he did not see. It says what
# follows from it too, so the model is not left to work that out (reports/belief_line_impl.md).
SCENARIOS["daniel_ate_it_leo_heard"] = {
    **SCENARIOS["daniel_ate_it"],
    "about_the_can": {"leo": "Last night you woke and heard someone open a can in the kitchen, so "
                             "someone in this house took it in the night. You did not see who."},
}
DEFAULT_SCENARIO = "daniel_ate_it"

# How the story speaks of each of them (as the shipped data's notes do).
PRONOUNS = {
    "daniel": {"he": "he", "him": "him", "his": "his", "himself": "himself"},
    "leo": {"he": "he", "him": "him", "his": "his", "himself": "himself"},
    "elena": {"he": "she", "him": "her", "his": "her", "himself": "herself"},
    "mara": {"he": "she", "him": "her", "his": "her", "himself": "herself"},
}

# (day, summary, {person: "did" | "saw" | "heard"}); people not listed were not there.
EVERYONE_SAW = {p: "saw" for p in ORDER}
NIGHT = object()
_BACKSTORY = [
    (1, "Daniel boards the front windows on his own while the others watch.",
     {**EVERYONE_SAW, "daniel": "did"}),
    (1, "Leo says the water will stop running within a day and they should fill everything they have.",
     {**EVERYONE_SAW, "leo": "did"}),
    (2, "The taps run dry, exactly as Leo said they would.", EVERYONE_SAW),
    (2, "Daniel says they should cross to the neighbour's house tonight and see what is left there.",
     {**EVERYONE_SAW, "daniel": "did"}),
    (2, "Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. "
        "Daniel drops it.", {**EVERYONE_SAW, "leo": "did"}),
    (2, "Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his.",
     {**EVERYONE_SAW, "daniel": "did"}),
    (2, "Elena counts what is left in the pantry with Mara beside her.", {"elena": "did", "mara": "saw"}),
    (3, "Mara cries in the night. Elena sits with her until it stops.",
     {"elena": "did", "mara": "saw", "leo": "heard"}),
    (3, "Mara freezes in the doorway with something moving in the street. Daniel picks her up and "
        "carries her inside.", {**EVERYONE_SAW, "daniel": "did"}),
    NIGHT,                    # the scenario's night, if it has one, goes here
    (4, "Leo says maybe they should let someone else handle this one.", {**EVERYONE_SAW, "leo": "did"}),
    (4, "Daniel empties Mara's bag onto the bed while she is standing there.",
     {"daniel": "did", "elena": "saw", "mara": "saw"}),
    (4, "Elena says she is quite sure nobody in this house would take food from the others.",
     {**EVERYONE_SAW, "elena": "did"}),
]
# Day 2's argument about crossing to the neighbour's house. Once the trip concern has started,
# trimming a prompt never drops these (reports/trip_design.md, §2.3).
TRIP_MEMORIES = tuple(e[1] for e in _BACKSTORY[3:6])


def backstory(scenario):
    """The days before, with this scenario's night in its place (or no night at all), followed
    by the scenario's own events of that night, if it has any."""
    s = SCENARIOS[scenario]
    night = ([s["night"]] if s["night"] else []) + s.get("after_night", [])
    return [x for e in _BACKSTORY for x in (night if e is NIGHT else [e])]


def culprit(scenario):
    """Who took the can in this scenario, or None."""
    return SCENARIOS[scenario]["culprit"]


def about_the_can(scenario, pid):
    """What else this person knows of the night in this scenario, told after their "About the
    can:" line; or None."""
    return SCENARIOS[scenario].get("about_the_can", {}).get(pid)

# What everyone saw at the start: Elena's count and what she said about it. It is true in every
# scenario, miscount included, where nothing was taken.
OPENING = ("Elena counts the pantry with everyone standing there. She finds one can fewer than she "
           "expected and says so. 2 portions are left.")
