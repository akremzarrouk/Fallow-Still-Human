"""The night between day 1 and day 2, and what day 2 starts from (reports/night_design.md, §2-§5).

After one plain line for the afternoon, everyone goes to bed in their own room and makes one
private decision. The rules work out who notices whom: from the rooms, from what carries through
the walls, and, for whoever is asleep, from a draw weighted by how anxious they are. Whoever
notices decides once more; a leaver who is stopped answers. The world decides each trip by two
draws from the seed: what the neighbour's house holds (once per seed) and what the street does to
whoever crosses it. Nothing in the night is asked of the model but those decisions.

`next_day` then hands day 2 each person as the night left them, with what they carry in: a block
of facts and conclusions the code writes from what they did, saw or heard.

Days that follow one another (reports/days_design.md): a night can be the second (`number`), finds the
neighbour's house as the last night left it, keeps whoever is away out of it, and records each thing that
happened as an event for the chronicle (chronicle.py), with each night line tied to the event it tells of.
`next_day` sets up day 3 the same way, and, given the chronicle, adds last night's thoughts (B) and the earlier
days (C) to what each person carries in (memory.py).
"""
import copy
import json
import random
import re

import data
import quiet
import water
import world
from world import (NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, day_index, estimate_tokens,
                   portions_text, when_words)

GAP_HUNGER = 0.3            # × hunger_rate, the afternoon and evening (§2)
NIGHT_HUNGER = 0.1          # × hunger_rate, the night
CARRY = 3                   # portions one person carries (§4.1)
CARRY_IN_MAX = 360          # estimated tokens of the carry-in block at most (§5.2)
HOUSE = [(0.30, 0), (0.65, 2), (0.90, 4), (1.00, 6)]                       # §4.1
ALONE = [(0.62, "clean"), (0.76, "scare_there"), (0.94, "scare_back"), (1.00, "not_back")]   # §4.2
GROUP = [(0.70, "clean"), (0.82, "scare_there"), (0.97, "scare_back"), (1.00, "not_back")]
ROOMMATE = {p: q for owners in data.OWNERS.values() for p in owners for q in owners if q != p}
OWN_ROOM = {p: room for room, owners in data.OWNERS.items() for p in owners}
BEDROOMS = tuple(data.OWNERS)
# "Daniel and Leo in the brothers room, Elena and Mara in the back room", in the family's order.
BEDS = ", ".join(" and ".join(NAMES[x] for x in data.ORDER if x in owners) + f" in the {data.ROOMS[room]}"
                 for room, owners in sorted(data.OWNERS.items(),
                                            key=lambda kv: min(data.ORDER.index(x) for x in kv[1])))
TRIGGER = "the family is together in the kitchen for the first time since last night"
CARRY_VARIANTS = ((False, True), (True, True), (True, False))     # (short, minutes), in the order they are tried

BEDTIME = [("sleep", "go to sleep"),
           ("lie_awake", "lie awake in your bed and listen"),
           ("watch_door", "sit up in the kitchen by the front door until morning, so nobody goes out without "
                          "you knowing"),
           ("go_next_door", "wait until the others are asleep, then go out by the front door to the "
                            "neighbour's house")]
BED_LINE = {"sleep": "You went to sleep.", "lie_awake": "You lay awake and listened.",
            "watch_door": "You sat up in the kitchen by the front door.",
            "go_next_door": "You meant to go to the neighbour's house once the others were asleep."}
# At bedtime, for whoever's latest word on the trip was that they would go (reports/body_design.md, §1).
PROMISE = "You said you would go to the neighbour's house tonight. If you are going, it is now."
TONIGHT = {"sleep": "you went to sleep.", "lie_awake": "you lay awake and listened.",
           "watch_door": "you sat up in the kitchen by the front door.",
           "go_next_door": "you meant to go to the neighbour's house once the others were asleep.",
           "go_further": "you meant to go to the houses further along the street once the others were asleep."}

# Stage B (reports/stage_b.md; reports/quiet_day_design.md §5, W2 and W5, and §1.2).
# W5: past the neighbour's house, for whoever knows it is empty. Each further house's food is drawn once, when first
# entered; a searched house is empty afterwards, and the next trip reaches the next house.
FAR = "the houses further along the street"
BEDTIME_FAR = ("go_further", "wait until the others are asleep, then go out by the front door, past the neighbour's "
                             "house, to the houses further along the street")
BED_LINE["go_further"] = "You meant to go to the houses further along the street once the others were asleep."
FAR_PROMISE = "You said you would go further along the street tonight. If you are going, it is now."
FAR_HOUSE = [(0.45, 0), (0.75, 2), (0.93, 4), (1.00, 6)]
STREET_UNSEARCHED = ("About the street: the houses further along it have not been searched; nobody knows what is left "
                     "in them, and it is further and more dangerous than next door.")
# The street as probabilities of (clean, scare_there, scare_back, not_back): §4.2's near tables (as ALONE and GROUP
# above), W5's far ones, and W2's shifts for a weak, very weak or exhausted body; a group takes its weakest member's
# shift at half size.
STREETS = ("clean", "scare_there", "scare_back", "not_back")
NEAR_ALONE, NEAR_GROUP = (0.62, 0.14, 0.18, 0.06), (0.70, 0.12, 0.15, 0.03)
FAR_ALONE, FAR_GROUP = (0.45, 0.17, 0.23, 0.15), (0.55, 0.15, 0.22, 0.08)
SHIFTS = {"weak": (-0.04, 0.0, 0.0, 0.04), "very weak": (-0.12, 0.0, 0.02, 0.10), "exhausted": (-0.02, 0.0, 0.0, 0.02)}
# Fasting's third stage (reports/ten_days_prep.md, fix 2): beyond very weak by the step from weak to very weak.
SHIFTS["barely standing"] = tuple(round(2 * v - w, 4) for w, v in zip(SHIFTS["weak"], SHIFTS["very weak"]))
NEAR_SHIFT = 0.5        # next door, a body shifts the street by half as much as further along
# §1.2: someone exhausted who watches the door or lies awake may doze, and then notices nothing.
DOZE_FROM, DOZE_BASE, DOZE_STEP, DOZE_MAX = 24, 0.3, 0.05, 0.7
DOZED = {"watch_door": "You dozed off in the night, and woke by the door at dawn.",
         "lie_awake": "You dozed off in the night."}
# W1 (reports/world_design.md, §4.1, §6): rain at bedtime, and the bin set out before sleeping; rain in the night masks
# the front door for whoever sleeps in a bedroom: moderate rain is about 50 dB(A) against a quiet night's 30 [S14], so
# the chance of waking is halved (est.). A night is rainy if any spell falls between 22:00 and 06:00 (est.).
BEDTIME_RAIN = ("rain_out", "set the bin under the drainpipe in the yard to catch the rain, then go to sleep")
BED_LINE["rain_out"] = "You set the bin under the drainpipe in the yard to catch the rain, then went to sleep."
TONIGHT["rain_out"] = "you set the bin out in the rain, then went to sleep."
RAIN_NOW = world.W1_NOW[1]
RAIN_MASK = 0.5
RAINY_FROM, RAINY_TO = 900, 1380        # 22:00 to 06:00, as minutes of the day the night follows


def pick(table, u):
    return next(v for c, v in table if u < c)


def house_portions(u):
    """What the neighbour's house holds, from its draw."""
    return pick(HOUSE, u)


def far_house_portions(u):
    """What a house further along holds, from its draw (W5)."""
    return pick(FAR_HOUSE, u)


def body_shift(fast_stage, debt_stage):
    """W2: how one body shifts the street (clean, scare_there, scare_back, not_back): weak, very weak or barely
    standing from fasting, and exhausted from sleep debt, added up. Fasting in days (reports/world_design.md,
    §4.3.1): light and slow (F2) is weak, thin and weak (F3) very weak, F4 and on barely standing."""
    out = (0.0, 0.0, 0.0, 0.0)
    for name, on in (("weak", fast_stage == 2), ("very weak", fast_stage == 3), ("barely standing", fast_stage >= 4),
                     ("exhausted", debt_stage >= 2)):
        if on:
            out = tuple(a + b for a, b in zip(out, SHIFTS[name]))
    return out


def group_shift(shifts):
    """Alone, one's own shift; a group takes its weakest member's (the most not_back) at half size (W2)."""
    weakest = max(shifts, key=lambda s: s[3])
    return weakest if len(shifts) == 1 else tuple(x * 0.5 for x in weakest)


def street_table(size, far=False, shift=None):
    """The street's probabilities for a group of `size`, near or far, shifted by the body: next door by half the
    shift (reports/stage_b_fixes.md, fix 2)."""
    table = (FAR_ALONE if size == 1 else FAR_GROUP) if far else (NEAR_ALONE if size == 1 else NEAR_GROUP)
    if shift is None:
        return table
    return tuple(a + (b if far else b * NEAR_SHIFT) for a, b in zip(table, shift))


def pick_street(u, table):
    c = 0.0
    for p, name in zip(table, STREETS):
        c += p
        if u < c:
            return name
    return STREETS[-1]


def doze_chance(debt):
    """§1.2: the chance an exhausted watcher dozes, 0.3 + 0.05 × (debt − 24), at most 0.7; none below 24."""
    if debt < DOZE_FROM:
        return 0.0
    return round(min(DOZE_MAX, DOZE_BASE + DOZE_STEP * (debt - DOZE_FROM)), 4)


def knows_next_door_empty(history, pid, away):
    """W5 (amendment 1): they got inside the neighbour's house on some night and left nothing there, or their own
    neighbour's-house line says a trip there came back with nothing (reports/stage_b_fixes.md, fix 1)."""
    if any(v and v["got_in"] and v["found"] - v["took"] == 0 for v in (night.visit.get(pid) for night in history)):
        return True
    if any(night.visit.get(pid) for night in history):         # their own visit is their line
        return False
    heard = heard_trip(history, pid)
    return heard is not None and heard[1] not in away and not heard[2]["took"]


def how_known(n, q, x):
    """How q knows x went out and did not come back (amendment 4): with them in the street, saw them go, heard the
    front door, or only found them gone."""
    if any(x in g["members"] and q in g["members"] for g in n.groups):
        return "with"
    for e in n.events:
        if x in (e.get("members") or [e["actor"]]):
            if e["kind"] in ("got_up", "at_door") and e["witnesses"].get(q) == "saw":
                return "saw"
            if e["kind"] == "door" and e["witnesses"].get(q) == "heard":
                return "heard"
    return "gone"


def missing_opening(x, how):
    """The morning after: what someone sees of x's absence, as they know it."""
    pro = data.PRONOUNS[x]
    return {"with": f"{NAMES[x]} is not here: {pro['he']} was with you in the street, you lost sight of {pro['him']} "
                    f"in the dark, and {pro['he']} has not come back.",
            "saw": f"{NAMES[x]} is not here: you saw {pro['him']} go out in the night, and {pro['he']} has not come "
                   f"back.",
            "heard": f"{NAMES[x]} is not here: {pro['his']} bed is empty and {pro['he']} is nowhere in the house. "
                     f"In the night you heard the front door; {pro['he']} has not come back.",
            # Where they went is the house's by morning (reports/household_knowledge.md): no "you do not know where".
            "gone": f"{NAMES[x]} is not here: {pro['his']} bed is empty and {pro['he']} is nowhere in the house."}[how]


def trips_known(history, pid):
    """Every trip of the nights so far, oldest first, as (night, group, who): who went is the whole house's by the
    next morning (reports/household_knowledge.md, fix 1). Their own, with "you" first; another's, all who went."""
    out = []
    for night in history:
        for g in night.groups:
            if pid in g["members"]:
                out.append((night, g, ["you"] + [NAMES[x] for x in g["members"] if x != pid]))
            else:
                out.append((night, g, [NAMES[x] for x in g["members"]]))
    return out


def seen_outcome(g):
    """What the house saw of another's trip by morning: back with food, back with nothing, or not back. A scare, and
    what a house held beyond what came home, stay with whoever went (reports/household_knowledge.md)."""
    if g["lost"] and len(g["members"]) == 1:
        return "has not come back"
    how = ("came back with food and water" if g["took"] and g.get("water") else "came back with food" if g["took"]
           else "came back with water" if g.get("water") else "came back with nothing")
    return how + (f"; {NAMES[g['lost']]} has not come back" if g["lost"] else "")


def joined(words):
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


FAR_REST = ("have not been searched: nobody knows what is left in them, and they are further and more dangerous than "
            "next door.")
COUNT = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def street_line(history, pid, day):
    """The "About the street:" line, each far trip oldest first (reports/facts_and_evening.md, fix 2;
    reports/household_knowledge.md, fix 1). Their own: the house they searched and what it held, or that they got
    inside none. Another's: only what the house saw (seen_outcome). Only searches of their own: the houses past them
    are unsearched. No far trip: STREET_UNSEARCHED."""
    def held(g):
        food = "no food" if not g["found"] else f"{portions_text(g['found'])}, all brought back"
        return food + (f", and you brought back {water_words(g['water'])} of water" if g.get("water") else "")
    items, searched = [], []
    for n, g, who in trips_known(history, pid):
        if not g.get("far"):
            continue
        when = when_words(("N", n.number), day)
        if who[0] != "you":
            items.append(f"{joined(who)} went further along it {when} and {seen_outcome(g)}")
        elif g["found"] is not None:
            searched.append((when, g, who))
            items.append(f"{joined(who)} searched a house further along it {when}, and it held {held(g)}")
        else:
            items.append(f"{joined(who)} went along it {when} but did not get inside any house further along")
    if not items:
        return STREET_UNSEARCHED
    if len(searched) == len(items) == 1:
        when, g, who = searched[0]
        return (f"About the street: {joined(who)} searched one house further along it {when}, and it held {held(g)}; "
                f"the houses past it {FAR_REST}")
    if len(searched) == len(items):
        each = "; ".join(f"one {when}, which held {held(g)}" for when, g, who in searched)
        return (f"About the street: you have searched {COUNT.get(len(searched), len(searched))} houses further along "
                f"it: {each}; the houses past them {FAR_REST}")
    return ("About the street: " + "; ".join(items) + "; nobody knows what is left in the houses further along, and "
            "they are further and more dangerous than next door.")


def outings_line(history, pid, day):
    """A quiet day's "About going out at night:" line (reports/facts_and_evening.md, fix 3): each trip of the nights so
    far (trips_known), oldest first: who, next door or further along, which night, and the outcome. Their own trip's
    from what they did; another's as the house saw it: food, nothing, or not back (reports/household_knowledge.md)."""
    items = []
    for n, g, who in trips_known(history, pid):
        where = "further along the street" if g.get("far") else "to the neighbour's house"
        when = when_words(("N", n.number), day)
        if who[0] == "you":
            there = " a house there" if g.get("far") else ""
            if g["found"] is None and g["lost"]:
                he = data.PRONOUNS[g["lost"]]["he"]
                how = f"lost sight of {NAMES[g['lost']]} in the street, and {he} has not come back"
            elif g["found"] is None:
                how = "turned back before getting inside"
            elif g["found"]:
                how = f"got inside{there}, found {portions_text(g['found'])} and brought back {g['took']}"
            else:
                how = f"got inside{there} and found no food"
            if g["found"] is not None and g.get("water"):
                how += f", and brought back {water_words(g['water'])} of water"
            items.append(f"{joined(who)} went {where} {when}, {how}")
            continue
        items.append(f"{joined(who)} went {where} {when} and {seen_outcome(g)}")
    return "About going out at night: " + ("; ".join(items) or "as far as you know, nobody has gone out") + "."


def water_words(litres):
    """Litres as an eye counts them: "10 litres", "about 5 litres", "a few litres"."""
    if litres < 2.5:
        return "a few litres"
    n = water.about(litres, 5)
    return f"{n} litres" if abs(n - litres) < 1e-9 else f"about {n} litres"


def street(u, size):
    """What the street does to a group of `size`: clean, scare_there, scare_back or not_back."""
    return pick(ALONE if size == 1 else GROUP, u)


def outcome_class(st, found, water=0):
    """The row of the outcome table (§4.3), from the street and what the house held when they got there; from night 3
    on, with the water they carried home (reports/w1_fixes.md, fix 2)."""
    if st == "not_back":
        return "not back by morning"
    if st == "scare_there":
        return "back shaken, with nothing"
    what = "food and water" if found and water else "food" if found else "water" if water else "nothing"
    return f"back with {what}" if st == "clean" else f"back shaken, with {what}"


def wake_room(pid):
    """The chance a sleeper wakes when their roommate gets up (§3.1)."""
    return round(0.30 + 0.40 * data.PEOPLE[pid]["traits"]["anxious"], 3)


def wake_door(pid):
    """The chance a sleeper in a bedroom wakes at the front door, through a wall (§3.1)."""
    return round(0.10 + 0.20 * data.PEOPLE[pid]["traits"]["anxious"], 3)


def him(pid):
    return data.PRONOUNS[pid]["him"]


def he(pid):
    return data.PRONOUNS[pid]["he"]


def quoted(words):
    """Words in quotes, ending a sentence: the closing stop is added only if the words lack one."""
    return f'"{words}"' + ("" if words.rstrip()[-1:] in ".!?" else ".")


def names(pids):
    ns = [NAMES[q] for q in pids]
    return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]


class Night:
    """One night. `draws` forces named draws (tests): "order" (a list of leavers), "house",
    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed.
    number: which night this is (reports/days_design.md, §1.3); house: the neighbour's house as the night
    before left it ({"value", "u", "left", "entered"}), so it is never drawn again."""

    def __init__(self, day1, oracle, draws=None, number=1, house=None):
        self.day1 = self.prev = day1            # the day this night follows
        self.number = number
        self.house_given = house
        self.oracle = oracle
        self.seed = day1.seed
        self.draws = dict(draws or {})
        # Day 1's rules and lines, on copies of its people: day 1 itself is left as it ended.
        self.m = copy.copy(day1)
        self.m.people = copy.deepcopy(day1.people)
        self.m.max_prompt_tokens = 0
        self.people = self.m.people
        self.portions = day1.portions
        self.house = self.house_left = self.house_u = None
        self.decisions = []         # every night decision, in order
        self.noticing = []          # every check of who notices whom, in order
        self.story = []             # ("decision", d) | ("noticing", n) | ("text", line), in order
        self.groups = []
        self.away = set(day1.away)  # whoever did not come back from an earlier night is not in the house
        self.entered = bool(house and house.get("entered"))
        far = (house or {}).get("far") or {"houses": [], "us": [], "searched": 0}
        self.far = {"houses": list(far["houses"]), "us": list(far["us"]), "searched": far["searched"]}
        self.far_visit = {}         # goer -> {"got_in", "found", "took", "house"}: a trip further along (W5)
        self.dozed = set()          # who dozed at the door or in bed (§1.2)
        # W1: the World the day before it kept (truth.py), if it was a quiet day with one; whether it rains tonight.
        self.world = getattr(getattr(day1, "quiet", None), "world", None)
        self.rainy = False
        self.events = []            # what happened, for the chronicle: dicts with "key", in order
        self.line_events = {p: [] for p in data.ORDER}    # the event each night line tells of
        self.leavers = []           # everyone who went out, in order
        self.lines = {p: [] for p in data.ORDER}          # night lines for the carry-in, with words
        self.lines_short = {p: [] for p in data.ORDER}    # the same without quoted words
        self.knows = {p: [] for p in data.ORDER}          # who they know went out, in order
        self.visit = {}             # goer -> {"got_in", "found", "took"}
        self.choices, self.where, self.awake, self.reacted = {}, {}, {}, set()
        self.bedtime_hunger, self.rooms_at_bedtime, self.state_at_bedtime = {}, {}, {}
        self.morning_hunger = {}

    # ---------- chance ----------
    def draw_string(self, name):
        """The seed string of a draw (reports/days_design.md, §4.4): the first night keeps night_design's;
        a later night has its own; the neighbour's house is one fact, whatever the night."""
        if self.number == 1 or name == "house" or name.startswith("far_house:"):     # each house: one fact
            return f"{self.seed}:night:{name}"
        return f"{self.seed}:night{self.number}:{name}"

    def u(self, name):
        if name in self.draws:
            return self.draws[name]
        return random.Random(self.draw_string(name)).random()

    def house_state(self):
        """The neighbour's house as this night leaves it, for the next night (reports/days_design.md, §4.3)."""
        return {"value": self.house, "u": self.house_u, "left": self.house_left, "entered": self.entered,
                "far": {"houses": list(self.far["houses"]), "us": list(self.far["us"]),
                        "searched": self.far["searched"]}}

    def order(self):
        """Everyone, in the order they would leave: lowest draw first."""
        if "order" in self.draws:
            return list(self.draws["order"])
        rng = random.Random(self.draw_string("order"))
        draw = {q: rng.random() for q in data.ORDER}
        return sorted(data.ORDER, key=draw.get)

    # ---------- lines ----------
    def line(self, pid, full, short=None, event=None):
        self.lines[pid].append(full)
        self.lines_short[pid].append(full if short is None else short)
        self.line_events[pid].append(event)

    def event(self, kind, actor=None, witnesses=None, **more):
        """Something that happened tonight, for the chronicle; returns its key."""
        self.events.append({"key": len(self.events), "kind": kind, "actor": actor, "witnesses": dict(witnesses or {}),
                            **more})
        return len(self.events) - 1

    def text(self, line):
        self.story.append(("text", line))

    # ---------- asking ----------
    def ask(self, pid, kind, now, opts, fallback):
        """One night decision. Returns (option id, words)."""
        p = self.people[pid]
        d = {"person": pid, "ask": kind, "where": self.where.get(pid, OWN_ROOM[pid]), "now": list(now),
             "options": [o.id for o in opts]}
        byid = {o.id: o for o in opts}
        if self.m.is_player(p):         # the player decides (player.py; reports/play_design.md §4.3)
            d.update(self.m.player_choice(p, None, opts, kind, night=now))
            d["label"] = byid[d["option"]].label
            self.decisions.append(d)
            self.story.append(("decision", d))
            return d["option"], d.get("say")
        brain = self.m.brain()
        if brain is not None:           # code mode (brain.py): the brain decides, and no model is asked
            seen = p.levels()
            choice = brain.decide_night(self, p, kind, opts)
            p.seen = seen
            d.update(mode="code", **choice)
            brain.settle(p, day_index(self.day1.day), d)
            d["label"] = byid[d["option"]].label
            self.decisions.append(d)
            self.story.append(("decision", d))
            return d["option"], d.get("say")
        prompt = self.m.prompt_for(p, None, opts, night=now)
        seen = p.levels()
        text = self.oracle.ask(NIGHT_SYSTEM, prompt)
        p.seen = seen
        choice, why = self.m.parse(text, opts)
        if choice is None:
            d.update(mode="fallback", invalid=why, option=fallback, say=None)
        else:
            if not byid[choice["option"]].speech and choice["say"]:
                choice["say"], choice["dropped_line"] = None, True     # words only for speech at night
            d.update(mode="model", **choice)
            self.m.take_answer(p, choice, self.m.night_minute(), d)     # after a quiet day, 21:00
        d["label"] = byid[d["option"]].label
        self.decisions.append(d)
        self.story.append(("decision", d))
        return d["option"], d.get("say")

    def wake_door(self, pid):
        """The chance a sleeper wakes at the front door (§3.1), halved while it rains in the night (W1)."""
        return round(wake_door(pid) * RAIN_MASK, 4) if self.rainy else wake_door(pid)

    def notice(self, who, of, how, draw=None, under=None, noticed=True):
        n = {"who": who, "of": of, "how": how, "awake": draw is None, "draw": draw, "under": under,
             "noticed": noticed, "where": self.where[who]}
        self.noticing.append(n)
        self.story.append(("noticing", n))

    # ---------- the night ----------
    def run(self):
        played = getattr(self.day1, "quiet", None) is not None     # a quiet day was played to bedtime (quiet.py)
        for p in self.people.values():                                  # the gap (§2)
            if p.id in self.away:
                p.room = None
                continue
            if not played:
                p.hunger = min(1.0, p.hunger + self.m.hunger_rise(750, GAP_HUNGER) * p.sheet["hunger_rate"])
            p.room = OWN_ROOM[p.id]
            p.activity = {"kind": "idle", "label": "in bed"}
        self.bedtime_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
        self.rooms_at_bedtime = {q: self.people[q].room for q in data.ORDER}
        self.state_at_bedtime = {
            q: [json.dumps({t: [g.strength, g.events] for t, g in p.grudges.items()}), p.suspicion.state(), p.guilt]
            for q, p in self.people.items()}
        present = [q for q in data.ORDER if q not in self.away]
        k = day_index(self.day1.day)
        if self.world is not None:
            self.rainy = bool(self.world.weather.spells(quiet.absolute(k, RAINY_FROM), quiet.absolute(k, RAINY_TO)))
        beds = BEDS if not self.away else ", ".join(
            " and ".join(NAMES[x] for x in present if x in owners) + f" in the {data.ROOMS[room]}"
            for room, owners in sorted(data.OWNERS.items(), key=lambda kv: min(data.ORDER.index(x) for x in kv[1]))
            if any(x in present for x in owners))
        for q in present:                                               # bedtime (§3.2)
            room = OWN_ROOM[q]
            r = ROOMMATE[q]
            mate = (f"{NAMES[r]}'s bed is empty." if r in self.away else
                    f"{NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.")
            now = ["Now it is night. " + quiet.gap_line(self.day1, q),
                   (f"Everyone has gone to bed in their own room: {beds}." if not self.away else
                    f"Everyone in the house has gone to bed in their own room: {beds}."),
                   f"You are in the {data.ROOMS[room]}, in your bed. {mate}",
                   f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]
            p = self.people[q]
            if p.rain_since is not None:                    # W1: raining at bedtime, as they hear it
                now.append(RAIN_NOW)
            own = p.trip_heard.get(q)
            if own and own[1] == "volunteer":           # `volunteer`, or day 2's `still_going`
                now.append(PROMISE)
            elif own and own[1] == "volunteer_far":
                now.append(FAR_PROMISE)
            opts = [Option(i, label) for i, label in BEDTIME] + ([Option(*BEDTIME_FAR)] if p.knows_empty else [])
            if p.rain_since is not None and p.water is not None and not p.water["bin_out"]:
                opts.append(Option(*BEDTIME_RAIN))
            choice, _ = self.ask(q, "bedtime", now, opts, "sleep")
            self.choices[q] = choice
            self.where[q] = "kitchen" if choice == "watch_door" else room
            self.awake[q] = choice not in ("sleep", "rain_out")
            if choice == "rain_out":
                self.world.put_bin_out(q, quiet.absolute(k, quiet.DAY_END), wet=False)
            self.people[q].tonight.append(TONIGHT[choice])
            e = self.event("bedtime", q, {q: "did"}, option=choice)
            line = f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}"
            chance = doze_chance(p.needs["debt"]) if choice in DOZED and p.needs is not None else 0.0
            if chance:
                u = self.u(f"doze:{q}")
                if u < chance:              # §1.2: asleep after all, and noticing nothing
                    self.dozed.add(q)
                    self.awake[q] = False
                    line += " " + DOZED[choice]
                    self.text(f"{NAMES[q]} dozes off (draw {u:.3f}, under {chance:.2f}).")
            self.line(q, line, event=e)
        if self.house_given:                # fixed the night it first mattered, and as that night left it (§4.3)
            self.house, self.house_u = self.house_given["value"], self.house_given["u"]
            self.house_left = self.house_given["left"]
        else:
            self.house_u = self.u("house")
            self.house = self.house_left = house_portions(self.house_u)
        pending = [q for q in self.order() if self.choices.get(q) in ("go_next_door", "go_further")]
        while pending:
            self.leave(pending.pop(0), pending)
        for p in self.people.values():                                  # the rest of the night
            if p.id in self.away:
                p.room = None
                continue
            p.hunger = min(1.0, p.hunger + self.m.hunger_rise(600, NIGHT_HUNGER) * p.sheet["hunger_rate"])
            p.room = OWN_ROOM[p.id]
        self.morning_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
        for e in self.events:               # who knew that someone went out (§4.2)
            if e["kind"] == "went_out":
                for P in data.ORDER:
                    if P not in e["members"] and any(x in self.knows[P] for x in e["members"]):
                        e["witnesses"].setdefault(P, "knew")
        return self

    def leave(self, L, pending):
        """L gets up to go: who notices, who stops or joins, the street, the return (§3.3)."""
        room = OWN_ROOM[L]
        group = [L]
        before = {}                 # joiner -> where they were before joining
        far = self.choices.get(L) == "go_further"
        dest = FAR if far else "the neighbour's house"
        self.text(f"{NAMES[L]} gets up to go to {dest}.")
        seen_by = set()

        def join(P):
            before[P] = self.where[P]
            group.append(P)
            if P in pending:
                pending.remove(P)
            self.knows[P].append(L)

        def back_to_bed():
            self.where[L] = room
            for P in group[1:]:
                self.where[P] = before[P]
            self.text(f"{NAMES[L]} goes back to bed" + (f", and {names(group[1:])} with {him(L)}." if group[1:] else "."))

        # 1. L gets up: the roommate.
        R = ROOMMATE[L]
        if self.where.get(R) == room and R not in self.dozed:
            awake = self.awake[R]
            if awake:
                self.notice(R, L, "room")
                noticed = True
            else:
                draw = self.u(f"wake:{L}:{R}")
                noticed = draw < wake_room(R)
                self.notice(R, L, "room", draw, wake_room(R), noticed)
            if noticed:
                self.awake[R] = True
                seen_by.add(R)
                self.knows[R].append(L)
                e = self.event("got_up", L, {L: "did", R: "saw"})
                self.line(R, f"In the night {NAMES[L]} got up in the dark and left the room toward the kitchen and the "
                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).", event=e)
                if R not in self.reacted:
                    self.reacted.add(R)
                    now = [f"Now it is night, in the {data.ROOMS[room]}. "
                           + ("You were lying awake." if awake else "You were asleep and woke."),
                           f"{NAMES[L]} has got up in the dark and is leaving the room quietly, toward the kitchen "
                           f"and the front door."]
                    stop = self.react_seen(R, L, now, pending, join, dest)
                    if stop and not self.answer(L, [stop], room, group, dest):
                        back_to_bed()
                        return
        # 2. L passes through the kitchen: whoever sits up by the front door.
        stops = []
        at_door = None
        for S in data.ORDER:
            if self.where.get(S) != "kitchen" or S in group or S in self.dozed:
                continue
            self.notice(S, L, "door watch")
            seen_by.add(S)
            self.knows[S] += [x for x in group if x not in self.knows[S]]
            who = names(group)
            if at_door is None:
                at_door = self.event("at_door", L, {x: "did" for x in group}, members=list(group))
            self.events[at_door]["witnesses"][S] = "saw"
            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).",
                      event=at_door)
            if S not in self.reacted:
                self.reacted.add(S)
                now = ["Now it is night. You are sitting up in the kitchen by the front door.",
                       f"{who} {'has' if len(group) == 1 else 'have'} come into the kitchen in the dark and "
                       f"{'is' if len(group) == 1 else 'are'} going to the front door."]
                stop = self.react_seen(S, L, now, pending, join, dest)
                if stop:
                    stops.append(stop)
        if stops and not self.answer(L, stops, "kitchen", group, dest):
            back_to_bed()
            return
        # 3. The front door opens: everyone in a bedroom who has not seen L go.
        door = None
        for P in data.ORDER:
            if self.where.get(P) not in BEDROOMS or P in group or P in seen_by or P in self.dozed:
                continue
            awake = self.awake[P]
            if awake:
                self.notice(P, L, "front door")
                heard = True
            else:
                draw = self.u(f"door:{L}:{P}")
                chance = self.wake_door(P)
                heard = draw < chance
                self.notice(P, L, "front door", draw, chance, heard)
            if not heard:
                continue
            self.awake[P] = True
            if door is None:
                door = self.event("door", L, {x: "did" for x in group}, members=list(group))
            self.events[door]["witnesses"][P] = "heard"
            self.line(P, f"In the night you {'' if awake else 'woke and '}heard the front door being opened. "
                         f"You did not see who.", event=door)
            if P in self.reacted:
                continue
            self.reacted.add(P)
            now = [f"Now it is night, in the {data.ROOMS[self.where[P]]}. "
                   + ("You were lying awake." if awake else "You were asleep and woke."),
                   "From the kitchen comes the sound of the front door being opened. You cannot see who it is."]
            self.react_heard(P, L, now, pending, join, group, far)
        # 4. The street.
        for P in group:
            self.where[P] = "out"
        self.leavers += group
        self.event("went_out", L, {x: "did" for x in group}, members=list(group),
                   **({"option": "go_further"} if far else {}))
        self.trip(L, group, far)

    def react_seen(self, P, L, now, pending, join, dest="the neighbour's house"):
        """P sees L leave (roommate or door sitter). Returns (P, words) if P tells L not to go."""
        n = NAMES[L]
        if P in pending:            # P meant to go too
            opts = [Option(f"go_with_{L}", f"get up and go with {n} to {dest}"),
                    Option(f"stop_{L}", f"tell {n}, low, to stay home, and go yourself instead", True),
                    Option(f"let_{L}_go", f"let {n} go, and go yourself later, alone"),
                    Option("stay_home", f"let {n} go, and stay in bed yourself after all")]
            fallback = f"let_{L}_go"
        else:
            opts = [Option(f"let_{L}_go", f"stay where you are and let {n} go without a word"),
                    Option(f"stop_{L}", f"tell {n}, low, not to go", True),
                    Option(f"go_with_{L}", f"get up and go with {n} to {dest}")]
            fallback = f"let_{L}_go"
        waiting = P in pending
        choice, words = self.ask(P, "reaction", now, opts, fallback)
        e = None if choice == f"stop_{L}" else self.event("reaction", P, {P: "did"}, option=choice, target=L)
        if choice == f"go_with_{L}":
            join(P)
            self.line(P, f"You went with {him(L)}.", event=e)
            self.people[P].tonight.append(f"you went with {n}.")
        elif choice == f"stop_{L}":
            self.people[P].tonight.append(f"you told {n} not to go.")
            return P, words
        elif choice == "stay_home":
            pending.remove(P)
            self.line(P, f"You let {him(L)} go, and stayed in bed after all.", event=e)
        elif waiting:
            self.line(P, f"You let {him(L)} go, to go yourself later.", event=e)
        else:
            self.line(P, f"You let {him(L)} go without a word.", event=e)
            self.people[P].tonight.append(f"you let {n} go.")
        return None

    def react_heard(self, P, L, now, pending, join, group, far=False):
        """P hears the front door from a bedroom: they cannot tell where whoever it is is going."""
        if P in pending:
            opts = [Option("go_after", "get up now and follow whoever it is out" if far else
                           "get up now and follow whoever it is out to the neighbour's house"),
                    Option("go_later", "wait, then go yourself later, alone"),
                    Option("stay_home", "stay in bed after all")]
            choice, _ = self.ask(P, "reaction", now, opts, "go_later")
            e = self.event("reaction", P, {P: "did"}, option=choice, target=L)
            if choice == "go_after":
                join(P)
                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.", event=e)
            elif choice == "stay_home":
                pending.remove(P)
                self.line(P, "You stayed in bed after all.", event=e)
            else:
                self.line(P, "You waited, to go yourself later.", event=e)
            return
        opts = [Option("stay_in_bed", "stay in bed"),
                Option("get_up_and_look", "get up, see whose bed is empty, and wait up by the front door until morning")]
        choice, _ = self.ask(P, "reaction", now, opts, "stay_in_bed")
        e = self.event("reaction", P, {P: "did"}, option=choice, target=L)
        if choice == "get_up_and_look":
            gone = [x for x in group]
            beds = (f"{NAMES[gone[0]]}'s bed was empty" if len(gone) == 1 else
                    " and ".join(f"{NAMES[x]}'s" for x in gone) + " beds were empty")
            full = self.lines[P][-1] + f" You got up: {beds}. You waited up by the front door."
            self.lines[P][-1] = self.lines_short[P][-1] = full
            self.where[P] = "kitchen"
            self.knows[P] += [x for x in gone if x not in self.knows[P]]
        else:
            self.line(P, "You stayed in bed.", event=e)

    def answer(self, L, stops, place, group, dest="the neighbour's house"):
        """L, told not to go, answers once. Returns True if L goes all the same."""
        where = (f"Now it is night, in the {data.ROOMS[place]}. You had got up to go to {dest}."
                 if place != "kitchen" else
                 f"Now it is night, in the kitchen, by the front door. You had got up to go to {dest}.")
        now = [where] + [f'{NAMES[S]} is up and says to you, low: "{w}"' if w else f"{NAMES[S]} is up and tells you, low, not to go."
                         for S, w in stops]
        who = names([S for S, _ in stops])
        opts = [Option("go_anyway", f"answer {who}, and go out to {dest} all the same", True),
                Option("stay_home", f"answer {who}, and go back to bed", True)]
        choice, a = self.ask(L, "answer", now, opts, "go_anyway")
        goes = choice == "go_anyway"
        went = "went all the same" if goes else "went back to bed"
        stop_events = [self.event("stop", S, {S: "did", L: "heard"}, option=f"stop_{L}", target=L, words=w)
                       for S, w in stops]
        self.event("answer", L, {L: "did", **{S: "heard" for S, _ in stops}}, option=choice, words=a,
                   target=stops[0][0])
        said = f' You answered: "{a}", and {went}.' if a else f" You {went}."
        told = " ".join(f"{NAMES[S]} told you, low, not to go: {quoted(w)}" if w else f"{NAMES[S]} told you, low, not to go."
                        for S, w in stops)
        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.",
                  event=stop_events[0])
        He = he(L).capitalize()
        for (S, w), e in zip(stops, stop_events):
            told = f"You told {NAMES[L]}, low, not to go" + (f": {quoted(w)}" if w else ".")
            answered = f' {He} answered: "{a}", and {went}.' if a else f" {He} {went}."
            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.", event=e)
        # Low voices: heard, without words, by anyone awake elsewhere; nobody wakes for a whisper.
        talkers = {L} | {S for S, _ in stops} | set(group)
        for P in data.ORDER:
            w = self.where.get(P)
            if P in talkers or w in (None, "out", place) or not self.awake[P]:
                continue
            self.events[stop_events[0]]["witnesses"][P] = "voices"
            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.", event=stop_events[0])
        if not goes:
            self.people[L].tonight.append("you went back to bed.")
        return goes

    def trip(self, L, group, far=False):
        """The street and the house decide; then the return (§4). Further along (W5), the next unsearched house, its
        food drawn when first entered, all of it taken. After a quiet day the street is shifted by the bodies (W2)."""
        u = self.u(f"trip_far:{L}" if far else f"trip:{L}")
        needs = [self.people[x].needs for x in group]
        table = None
        if far or all(n is not None for n in needs):            # nights 1 and 2 have no needs: §4.2's tables
            shift = (group_shift([body_shift(n["fast_stage"], n["debt_stage"]) for n in needs])
                     if all(n is not None for n in needs) else None)
            table = street_table(len(group), far, shift)
            st = pick_street(u, table)
        else:
            st = street(u, len(group))
        found = self.house_left
        g = {"leader": L, "members": list(group), "u": u, "street": st, "found": None, "took": 0, "lost": None,
             "lost_u": None, "shaken": [], "outcome": None}
        if table is not None:
            g["table"] = list(table)
        if far:
            g["far"], g["house"] = True, self.far["searched"]
        if far and st in ("clean", "scare_back"):
            i = self.far["searched"]
            if i == len(self.far["houses"]):                    # first entered: its food is drawn now, once
                hu = self.u(f"far_house:{i}")
                self.far["houses"].append(far_house_portions(hu))
                self.far["us"].append(hu)
            found = self.far["houses"][i]
            g["found"] = g["took"] = found
            self.far["searched"] += 1                           # searched, and empty afterwards
        elif st in ("clean", "scare_back"):
            g["found"] = found
            g["took"] = min(found, CARRY * len(group))
            self.house_left -= g["took"]
        if self.world is not None and st in ("clean", "scare_back"):     # W1: water, up to what they can carry
            place = ("far", g["house"]) if far else "neighbour"
            at = quiet.absolute(day_index(self.day1.day), quiet.DAY_END)
            g["water"] = self.world.carry_home(place, water.CARRY * len(group), at)
            g["water_left"] = self.world.house_water(place, at)["left"]
        if st in ("scare_there", "scare_back"):
            g["shaken"] = list(group)
        if st == "not_back":
            if len(group) == 1:
                g["lost"] = L
            else:
                g["lost_u"] = self.u(f"lost:{L}")
                g["lost"] = sorted(group)[int(g["lost_u"] * len(group))]
                g["shaken"] = [x for x in group if x != g["lost"]]
            if g["lost"] == "leo" and self.m.brain() is not None:
                # Code mode (Docs/fable-audit-2026-11.md, 7.4): Leo is not lost. The exception is marked in the record.
                g["spared"], g["lost"], g["shaken"] = "leo", None, list(group)
                st = g["street"] = "scare_there"
            else:
                self.away.add(g["lost"])
        g["outcome"] = outcome_class(st, found, g.get("water", 0))
        self.groups.append(g)
        if st in ("clean", "scare_back") and not far:
            self.entered = True
        street_e = self.event("street", L, {x: "did" for x in group}, members=list(group), outcome=g["outcome"])
        back = [x for x in group if x != g["lost"]]
        return_e = self.event("return", L, {x: "did" for x in back}, members=list(back)) if back else None
        k, F = g["took"], g["found"]
        wl = g.get("water") or 0
        home = []
        if k:
            home.append(f"the {portions_text(k)} on the shelf")
        if wl:
            home.append(f"{water_words(wl)} of water in the kitchen")
        came_back = "You came back in by the front door before dawn" + (f" and put {' and '.join(home)}." if home else ".")
        for P in back:
            if far:
                self.far_line(P, st, F, g, street_e)
                self.line(P, came_back, event=return_e)
                self.far_visit[P] = {"got_in": st in ("clean", "scare_back"), "found": F, "took": k,
                                     "house": g["house"], "water": wl}
                continue
            if st == "clean" and F:
                rest = F - k
                took = (f"You took {k}; {rest} {'is' if rest == 1 else 'are'} still there." if rest else "You took all of it.")
                self.line(P, f"You got inside the neighbour's house and found {portions_text(F)} of food. {took} "
                             f"Nothing troubled you in the street.", event=street_e)
            elif st == "clean":
                self.line(P, "You got inside the neighbour's house and found no food there. Nothing troubled you in "
                             "the street.", event=street_e)
            elif st == "scare_there":
                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.",
                          event=street_e)
            elif st == "scare_back":
                got = (f"and found {portions_text(F)} of food and took {k}" if F else "but found no food")
                self.line(P, f"You got inside the neighbour's house {got}. On the way back, something was moving in the "
                             f"street, and you ran the rest of the way.", event=street_e)
            else:
                self.line(P, f"In the street, something was moving. You lost sight of {NAMES[g['lost']]} in the dark "
                             f"and came back without {him(g['lost'])}.", event=street_e)
            self.line(P, came_back, event=return_e)
            self.visit[P] = {"got_in": st in ("clean", "scare_back"), "found": F, "took": k, "water": wl,
                             "water_left": g.get("water_left", 0)}
        if not back:
            return
        self.portions += k
        if wl:
            self.world.receive(wl)
        # The return: the front door again.
        for P in back:
            self.where[P] = OWN_ROOM[P]
            self.awake[P] = True
        carrying = (", carrying food and water" if k and wl else ", carrying food" if k else ", carrying water" if wl
                    else f", with nothing in {'their' if len(back) > 1 else data.PRONOUNS[back[0]]['his']} hands")
        shaken = ", and looked shaken" if g["shaken"] else ""
        alone = " alone" if g["lost"] else ""
        for P in data.ORDER:
            w = self.where.get(P)
            if P in group or w in (None, "out") or P in self.dozed:      # a dozer notices nothing (§1.2)
                continue
            if w == "kitchen":
                self.notice(P, L, "return")
                self.knows[P] += [x for x in back if x not in self.knows[P]]
                self.events[return_e]["witnesses"][P] = "saw"
                self.line(P, f"Before dawn {names(back)} came back in{alone} by the front door{carrying}{shaken} "
                             f"(you saw it).", event=return_e)
            elif self.awake[P]:
                self.notice(P, L, "return")
                self.events[return_e]["witnesses"][P] = "heard"
                self.line(P, "Before dawn you heard the front door again. You did not see who.", event=return_e)
            else:
                draw = self.u(f"return:{L}:{P}")
                chance = self.wake_door(P)
                woke = draw < chance
                self.notice(P, L, "return", draw, chance, woke)
                if woke:
                    self.awake[P] = True
                    self.events[return_e]["witnesses"][P] = "heard"
                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.",
                              event=return_e)

    def far_line(self, P, st, F, g, street_e):
        """What P went through further along the street (W5)."""
        past = "You went past the neighbour's house to the houses further along the street"
        if st == "clean" and F:
            self.line(P, f"{past}, got inside the next one and found {portions_text(F)} of food. You took all of it. "
                         f"Nothing troubled you in the street.", event=street_e)
        elif st == "clean":
            self.line(P, f"{past} and got inside the next one, but found no food there. Nothing troubled you in the "
                         f"street.", event=street_e)
        elif st == "scare_there":
            self.line(P, "On the way along the street, past the neighbour's house, something was moving. You ran back "
                         "without getting inside anywhere.", event=street_e)
        elif st == "scare_back":
            got = f"found {portions_text(F)} of food and took all of it" if F else "found no food"
            self.line(P, f"{past}, got inside the next one and {got}. On the way back, something was moving in the "
                         f"street, and you ran the rest of the way.", event=street_e)
        else:
            self.line(P, f"Further along the street, something was moving. You lost sight of {NAMES[g['lost']]} in the "
                         f"dark and came back without {him(g['lost'])}.", event=street_e)

    # ---------- the record ----------
    def transcript(self):
        return {"house": self.house, "house_u": self.house_u, "house_left": self.house_left,
                "portions_before": self.day1.portions, "portions_after": self.portions,
                "bedtime_hunger": self.bedtime_hunger, "morning_hunger": self.morning_hunger,
                "choices": self.choices, "leavers": self.leavers, "away": [q for q in data.ORDER if q in self.away],
                "decisions": [{k: v for k, v in d.items()} for d in self.decisions],
                "noticing": self.noticing, "groups": self.groups,
                "lines": self.lines,
                # Days that follow one another (reports/days_design.md, §4.2): which night, what happened, and the
                # event each night line tells of.
                "number": self.number, "events": self.events, "line_events": self.line_events,
                # Stage B (reports/stage_b.md), only on a night that had any: the houses further along, and who dozed.
                **({"far": self.far, "far_visit": self.far_visit} if self.far["houses"] or self.far_visit else {}),
                **({"dozed": sorted(self.dozed)} if self.dozed else {})}


# ---------- day 2 ----------
def carry_in(day1, n, p, short=False, minutes=True):
    """What p carries into day 2 (§5.2): yesterday's facts as p had them, then their own night."""
    out = [f"Yesterday morning Elena counted the pantry and found one can fewer than she expected "
           f"({'you did it' if p.id == 'elena' else 'you saw it'})."]
    c = day1.culprit
    if p.confessed:
        sure = next(x for x in p.sure if "you admitted aloud that you took the can" in x)
        front = sure.split(", in front of ", 1)[1].rstrip(".").split(", ") if ", in front of " in sure else None
        out.append(f"You admitted at {data.minute_words(data.unstamp(sure)[0])} that you took the can"
                   + (f", in front of {names([q for q in data.ORDER if NAMES[q] in front])}." if front else "."))
    elif p.knows_culprit and p.knows_culprit != p.id:
        sure = next(x for x in p.sure if " admitted taking the can: " in x)
        words = sure.split(" admitted taking the can: ", 1)[1].rsplit(" (you heard it)", 1)[0]
        after = ", after denying it to you" if p.knows_culprit in p.denials_heard else ""
        out.append(f"{NAMES[p.knows_culprit]} admitted taking the can at {data.minute_words(p.confession_heard_at)}{after}: "
                   f"{words} (you heard it).")
    elif c is not None and p.id == c:
        accusers = [q for q in data.ORDER if q in p.accused_by]
        out.append("Nobody found out that you ate the can" + (f"; {names(accusers)} accused you." if accusers
                                                              else ", and nobody named you."))
    else:
        out.append("Nobody admitted taking the can, and it was not found.")
    for mm, rest in map(data.unstamp, p.sure):
        if rest.startswith("you finished searching the "):
            out.append(f"You searched the {rest[len('you finished searching the '):].split(':')[0]} at "
                       f"{data.minute_words(mm)} and found nothing.")
    acc = {}
    for turn in day1.transcript["turns"]:
        for a in turn["acts"]:
            if a["option"].startswith("accuse_") and (a["who"] == p.id or p.id in a["audience"]):
                acc.setdefault((a["who"], a["option"][len("accuse_"):]), []).append(turn["minute"])
    if acc:
        parts = []
        for (a, t), ms in acc.items():
            times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
            when = f" ({data.minutes_list(ms)})" if minutes else ""
            parts.append(f"{'you' if a == p.id else NAMES[a]} accused {'you' if t == p.id else NAMES[t]}{times}{when}")
        text = "; ".join(parts)
        out.append(f"Accusations: {text}.")
    ate = {}
    for x in p.sure:
        if " ate one of the portions" in x:
            mm, rest = data.unstamp(x)
            ate.setdefault(mm, []).append("you" if rest.startswith("you ate") else rest.split(" ate one")[0])
    for mm, who in ate.items():
        mine = "you" in who
        who = (["You"] if mine else []) + [w for w in who if w != "you"]
        each = " each" if len(who) > 1 else ""
        out.append(f"{' and '.join(who)} ate a portion{each} at {data.minute_words(mm)}" + ("." if mine else " (you saw it)."))
    plan = day1.heard_plan(p)
    if plan:
        out.append("About going to the neighbour's house last night, where it was left: "
                   + plan[len("About going there tonight: "):])
    out.append(data.GAP)
    out += (n.lines_short if short else n.lines)[p.id]
    return ["Yesterday and last night:"] + [f"- {x}" for x in out]


def bounded_carry_in(day1, n, p):
    """The block within CARRY_IN_MAX: the quoted night words go first, then the accusations' minutes."""
    return carry_variants(day1, n, p)[0]


def carry_variants(prev, n, p):
    """Block A as it can be trimmed (reports/days_design.md, §3.4): from the first form within CARRY_IN_MAX, then
    the shorter ones. Day 2's is night_design's carry-in; a later day's is carry_in_later."""
    make = carry_in if prev.day == 4 else carry_in_later
    blocks = [make(prev, n, p, short, minutes) for short, minutes in CARRY_VARIANTS]
    first = next((i for i, b in enumerate(blocks) if estimate_tokens("\n".join(b)) <= CARRY_IN_MAX), 2)
    blocks = blocks[first:]
    return blocks + [blocks[-1]] * (3 - len(blocks))


def carry_in_later(prev, n, p, short=False, minutes=True):
    """Block A from day 3 on (reports/days_design.md, §3.2, lines Y1-Y8): yesterday's facts as p had them, then
    their own night. `prev` is yesterday's Morning, as it ended."""
    out = [f"Yesterday morning the shelf held {portions_text(prev.start_portions)}."]
    if p.confessed and p.confessed_day == prev.day:                               # Y2
        sure = next(x for x in p.sure if "you admitted aloud that you took the can" in x)
        front = sure.split(", in front of ", 1)[1].rstrip(".").split(", ") if ", in front of " in sure else None
        out.append(f"You admitted at {data.minute_words(data.unstamp(sure)[0])} that you took the can"
                   + (f", in front of {names([q for q in data.ORDER if NAMES[q] in front])}." if front else "."))
    elif p.knows_culprit and p.knows_culprit != p.id and p.confession_heard_day == prev.day:
        sure = next(x for x in p.sure if " admitted taking the can: " in x)
        words = sure.split(" admitted taking the can: ", 1)[1].rsplit(" (you heard it)", 1)[0]
        after = ", after denying it to you" if p.knows_culprit in p.denials_heard else ""
        out.append(f"{NAMES[p.knows_culprit]} admitted taking the can at {data.minute_words(p.confession_heard_at)}{after}: "
                   f"{words} (you heard it).")
    for label, prefix, verb in (("Accusations", "accuse_", "accused"), ("Confrontations", "confront_", "confronted")):
        acts = {}                                                                 # Y3, Y4
        for turn in prev.transcript["turns"]:
            for a in turn["acts"]:
                if a["option"].startswith(prefix) and (a["who"] == p.id or p.id in a["audience"]):
                    acts.setdefault((a["who"], a["option"][len(prefix):]), []).append(turn["minute"])
        if acts:
            parts = []
            for (a, tgt), ms in acts.items():
                times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
                when = f" ({data.minutes_list(ms)})" if minutes else ""
                parts.append(f"{'you' if a == p.id else NAMES[a]} {verb} {'you' if tgt == p.id else NAMES[tgt]}{times}{when}")
            out.append(f"{label}: " + "; ".join(parts) + ".")
    for mm, rest in map(data.unstamp, p.sure):                                   # Y5
        if rest.startswith("you finished searching the "):
            out.append(f"You searched the {rest[len('you finished searching the '):].split(':')[0]} at "
                       f"{data.minute_words(mm)} and found nothing.")
    ate = {}                                                                      # Y6
    for x in p.sure:
        if " ate one of the portions" in x:
            mm, rest = data.unstamp(x)
            ate.setdefault(mm, []).append("you" if rest.startswith("you ate") else rest.split(" ate one")[0])
    for mm, who in ate.items():
        mine = "you" in who
        who = (["You"] if mine else []) + [w for w in who if w != "you"]
        each = " each" if len(who) > 1 else ""
        out.append(f"{' and '.join(who)} ate a portion{each} at {data.minute_words(mm)}" + ("." if mine else " (you saw it)."))
    for x in p.sure:
        mm, rest = data.unstamp(x)
        g = re.match(r"^(\w+) gave one of the portions to (\w+), and \w+ (ate it|put it back on the shelf)", rest)
        if g:
            giver = "You" if g.group(1) == "you" else g.group(1)
            done = "ate it" if g.group(3) == "ate it" else "put it back"
            out.append(f"{giver} gave {g.group(2)} a portion at {data.minute_words(mm)}, and {g.group(2)} {done}"
                       + ("." if giver == "You" else " (you saw it)."))
            continue
        g = re.match(r"^(\w+) gave you one of the portions, and you (ate it|put it back on the shelf)", rest)
        if g:
            done = "ate it" if g.group(2) == "ate it" else "put it back"
            out.append(f"{g.group(1)} gave you a portion at {data.minute_words(mm)}, and you {done}.")
            continue
        if rest.startswith("you shared out the last "):
            out.append(f"You shared out the food at {data.minute_words(mm)}.")
        elif " shares out the last " in rest and rest.endswith("you had your part."):
            out.append(f"{rest.split(' shares out the last ')[0]} shared out the food at {data.minute_words(mm)}; you had your part.")
    q = getattr(prev, "quiet", None)                                              # W2a: yesterday's door
    for sc in (q.door_scenes if q is not None else []):
        if p.id in sc["summary"]:
            out.append(sc["summary"][p.id])
    for b in p.beliefs:                     # reports/talk_design.md, A4: what they were told yesterday, and by whom
        if b["day"] == prev.day:
            out.append(f"Yesterday at {data.clock(b['minute'])}, {b['claim']}")
    plan = prev.heard_plan(p)                                                     # Y7
    if plan:            # said yesterday, about last night (reports/facts_and_evening.md, fix 4), and what came of it
        out.append("What was said yesterday about going out last night, where it was left: "
                   + plan[len("About going there tonight: "):].rstrip(".") + "; " + night_came_to(n, p) + ".")
    out.append(quiet.gap_line(prev, p.id))                                        # Y8 (quiet.py, §3)
    out += (n.lines_short if short else n.lines)[p.id]
    return ["Yesterday and last night:"] + [f"- {x}" for x in out]


def night_came_to(n, p):
    """What the night after the positions came to, as the house knows it (reports/ten_days_prep.md, fix 1): who went,
    where, "anyway" if a position heard said nobody should go or that one of them must stay home, and what could be
    seen of it; or that nobody went out."""
    if not n.groups:
        return "then nobody went out"
    against = {(kind, target) for _, kind, target, *_ in p.trip_heard.values() if kind == "object"}
    parts = []
    for g in n.groups:
        who = ["you" if x == p.id else NAMES[x] for x in g["members"]]
        anyway = ("object", None) in against or any(("object", x) in against for x in g["members"])
        where = "further along" if g.get("far") else "to the neighbour's house"
        parts.append(f"{joined(who)} went {where}{' anyway' if anyway else ''} and {seen_outcome(g)}")
    return "then " + ", and ".join(parts)


def neighbour_line(n, pid, history=None, day=None, away=None):
    """Their "About the neighbour's house:" line (night_design §5.3): their own visit on any night outranks one
    they know of, and a later night outranks an earlier one (reports/days_design.md, §3.5)."""
    history = history or [n]
    day = day or n.prev.day + 1
    away = n.away if away is None else away
    for night in reversed(history):
        v = night.visit.get(pid)
        if not v:
            continue
        when = when_words(("N", night.number), day)
        drink = ""
        if v.get("water"):              # W1: what they carried, and what they saw was left
            left = v.get("water_left", 0)
            drink = (f"; you brought back {water_words(v['water'])} of water, and "
                     + (f"{water_words(left)} {'is' if left < 2.5 else 'are'} still there" if left else
                        "no water is left there"))
        if v["got_in"] and v["found"]:
            rest = v["found"] - v["took"]
            left = f", and {rest} {'is' if rest == 1 else 'are'} still there" if rest else ", and none are left there"
            return (f"About the neighbour's house: you went in {when} and found {portions_text(v['found'])}; "
                    f"you brought back {v['took']}{left}{drink}. Outside is dangerous.")
        if v["got_in"]:
            return (f"About the neighbour's house: you went in {when} and found no food there{drink}. Outside is "
                    f"dangerous.")
        return f"About the neighbour's house: you did not get inside {when}. Outside is dangerous."
    heard = heard_trip(history, pid)
    if heard is None:
        return NEIGHBOUR_UNKNOWN
    night, x, g = heard
    if x in away:
        how = " and has not come back"
    else:
        how = " and " + seen_outcome({**g, "lost": None})
    return (f"About the neighbour's house: {NAMES[x]} went there {when_words(('N', night.number), day)}{how}. "
            f"Outside is dangerous.")


def heard_trip(history, pid):
    """The latest trip next door that someone else went on, as (night, who, group), or None: not whoever got up and
    was talked back to bed. By the next morning the whole house knows who went (reports/household_knowledge.md)."""
    for night in reversed(history):
        for g in night.groups:
            known = [x for x in g["members"] if x != pid]
            if known and not g.get("far"):
                return night, known[0], g
    return None


def tag_events(p, k, day, night_from=NIGHT_MINUTE):
    """Grudge and guilt events keep the scene they happened in, and their day words are written for `day`
    (reports/days_design.md, §3.5): (minute, text with its word, kind, word, scene, text) for a grudge,
    (minute, text with its word, scene, text) for guilt. k: the played day that has just ended. night_from: the
    minute its night's answers kept (Morning.night_minute); an event before it is the day's (reports/multiday.md)."""
    for g in p.grudges.values():
        events = []
        for e in g.events:
            scene, raw = ((("N", k) if e[0] >= night_from else ("D", k)), e[1]) if len(e) == 3 else (e[4], e[5])
            word = when_words(scene, day)
            events.append((e[0], f"{word}, {raw}" if e[2] == "event" else raw, e[2], word, scene, raw))
        g.events = events
    tagged = []
    for e in p.guilt_events:
        scene, raw = ((("N", k) if e[0] >= night_from else ("D", k)), e[1]) if len(e) == 2 else (e[2], e[3])
        tagged.append((e[0], f"{when_words(scene, day)}, {raw}", scene, raw))
    p.guilt_events = tagged


def next_day(day1, n, oracle, chronicle=None):
    """The next morning: a Morning of the next house day with each person as the night left them (§5.1). `day1` is
    the day the night followed. Given the chronicle, each person also carries last night's thoughts (B) and, from
    day 3 on, the earlier days (C), under one bound with A (reports/days_design.md, §3)."""
    import memory
    day = day1.day + 1
    k = day_index(day1.day)
    m = world.Morning(oracle, day1.seed, day1.scenario, day=day, player=getattr(day1, "player", None))
    m.people = n.people
    m.portions = m.start_portions = n.portions
    m.away = set(n.away)
    m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}
    present = [q for q in data.ORDER if q not in m.away]
    before, after = n.day1.portions, n.portions
    history = chronicle.nights if chronicle is not None and chronicle.nights else [n]
    full = getattr(getattr(oracle, "brain", None), "full_days", False)     # week.py: every day is a full day
    if (day >= 6 or full) and chronicle is not None:    # from day 3: the needs, before anyone has seen their levels
        quiet.setup(m, chronicle)
    for q in present:
        p = m.people[q]
        p.knows_empty = knows_next_door_empty(history, q, m.away)           # W5 (amendment 1; fix 1)
        street = street_line(history, q, day)
        if p.knows_empty or street != STREET_UNSEARCHED:    # and whoever knows of a far trip (facts_and_evening)
            m.street[q] = street
        if m.quiet is not None:                                             # facts_and_evening, fix 3
            m.outings[q] = outings_line(history, q, day)
        for x in data.ORDER:                                                # amendment 4
            if x in n.away and x not in day1.away:
                g = next((g for g in n.groups if x in g["members"]), {})
                p.missing[x] = (how_known(n, q, x), n.number,
                                "further along the street" if g.get("far") else "to the neighbour's house")
    for q in data.ORDER:
        p = m.people[q]
        variants = carry_variants(day1, n, p)
        if chronicle is None:
            m.carry[q] = variants[0]
            m.blocks[q] = {"A": variants[0], "B": [], "C": [], "earlier": []}
        else:
            b_items = memory.b_items(chronicle.minds.get(n.number, {}).get(q), chronicle, q)
            b = memory.block_b(chronicle.minds.get(n.number, {}).get(q), chronicle, q)
            c = memory.block_c(chronicle, q, day, away=m.away) if day >= 6 else []
            r = memory.bounded(variants, b, c, memory.MEMORY_MAX)
            m.carry[q] = r["C"] + r["A"] + r["B"]
            earlier = [(it["ids"][:3], it["line"] + (f' You thought then: "{it["thought"]}"' if it.get("thought") else ""))
                       for it in r["C_items"] if it.get("ids")]
            earlier += [(ids, line) for ids, line in b_items if f"- {line}" in r["B"]]
            m.blocks[q] = {"A": r["A"], "B": r["B"], "C": r["C"], "earlier": earlier}
        m.neighbour[q] = neighbour_line(n, q, history, day, m.away)
    brought = {P: g["took"] for g in n.groups for P in g["members"] if g["took"] and P not in m.away}
    carried = {P: g["water"] for g in n.groups for P in g["members"] if g.get("water") and P not in m.away}
    water_in = sum(g.get("water") or 0 for g in n.groups)
    shaken = {P for g in n.groups for P in g["shaken"] if P not in m.away}
    for q in data.ORDER:
        p = m.people[q]
        # The suspicion minutes of the day that ended, and of its night, keep their scene (§3.5).
        night_from = day1.night_minute()
        day_ms = [mm for mm in p.suspected_at if mm < night_from]
        if day_ms:
            p.suspected_past.append((("D", k), day_ms))
        if any(mm >= night_from for mm in p.suspected_at):
            p.suspected_past.append((("N", k), True))
        tag_events(p, k, day, night_from)
        for g in p.grudges.values():
            g.last_change = 0
        p.suspicion.last_fall = 0
        p.suspected_at = []
        p.memory, p.said_lines, p.history, p.heard, p.triggers, p.tonight = [], [], [], [], [], []
        p.trip_heard, p.proposed, p.trip_raised = {}, False, False
        p.addressed = p.aside_lead = None
        p.eaten = 0.0
        # The food moment's band (reports/body_design.md, §2.2): yesterday's last meal, if any.
        p.ate_yesterday, p.last_meal, p.last_food = p.last_meal, None, None
        p.last_inner = p.last_asked = None
        p.feeling, p.feeling_until = (("shaken", world.FEELING_SHOWS_FOR_TURNS - 1) if q in shaken else (None, -1))
        p.activity = {"kind": "idle", "label": "just got up"}
        if q in m.away:
            p.room, p.sure = None, []
            continue
        p.room = "kitchen"
        opening = (f"Everyone{' else' if m.away else ''} gets up and comes into the kitchen. Last night the shelf "
                   f"held {portions_text(before)}; this morning it holds {portions_text(after)}")
        if q in brought:
            opening += f": the {brought[q]} you brought back are on it."
        elif after > before:
            opening += ". So someone brought food into the house in the night."
        else:
            opening += "."
        if q in carried:                # W1: water carried in tonight
            opening += f" The water you brought back is in the kitchen: {water_words(carried[q])}."
        elif water_in:
            opening += (f" In the kitchen there is water that was not there last night: {water_words(water_in)}. So "
                        f"someone brought water into the house in the night.")
        for x in data.ORDER:
            if x in m.away:
                how, k = p.missing.get(x, ("gone", n.number))[:2]
                opening += (" " + missing_opening(x, how) if k == n.number else
                            f" {NAMES[x]} is still not here: {data.PRONOUNS[x]['he']} has not come back.")
        p.sure = [f"min 00: {opening} (you saw it)"]
        p.triggers.append((TRIGGER, True))
        p.seen = p.levels()
    for q in m.away:
        m.people[q].seen = m.people[q].levels()
    # For the story: what each of them had at minute 00 besides the block.
    m.carried = {q: m.people[q].sure[:1] + m.trip_lines(m.people[q])[:2] for q in present}
    m.started("kitchen", 0, TRIGGER, False)
    return m
