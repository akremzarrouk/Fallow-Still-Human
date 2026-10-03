"""The night between day 1 and day 2, and what day 2 starts from (reports/night_design.md, §2-§5).

After one plain line for the afternoon, everyone goes to bed in their own room and makes one
private decision. The rules work out who notices whom: from the rooms, from what carries through
the walls, and, for whoever is asleep, from a draw weighted by how anxious they are. Whoever
notices decides once more; a leaver who is stopped answers. The world decides each trip by two
draws from the seed: what the neighbour's house holds (once per seed) and what the street does to
whoever crosses it. Nothing in the night is asked of the model but those decisions.

`next_day` then hands day 2 each person as the night left them, with what they carry in: a block
of facts and conclusions the code writes from what they did, saw or heard.
"""
import copy
import json
import random

import data
import world
from world import NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, estimate_tokens, portions_text

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
           "go_next_door": "you meant to go to the neighbour's house once the others were asleep."}


def pick(table, u):
    return next(v for c, v in table if u < c)


def house_portions(u):
    """What the neighbour's house holds, from its draw."""
    return pick(HOUSE, u)


def street(u, size):
    """What the street does to a group of `size`: clean, scare_there, scare_back or not_back."""
    return pick(ALONE if size == 1 else GROUP, u)


def outcome_class(st, found):
    """The row of the outcome table (§4.3), from the street and what the house held when they got there."""
    if st == "not_back":
        return "not back by morning"
    if st == "scare_there":
        return "back shaken, with nothing"
    if st == "clean":
        return "back with food" if found else "back with nothing"
    return "back shaken, with food" if found else "back shaken, with nothing"


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
    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed."""

    def __init__(self, day1, oracle, draws=None):
        self.day1 = day1
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
        self.away = set()
        self.leavers = []           # everyone who went out, in order
        self.lines = {p: [] for p in data.ORDER}          # night lines for the carry-in, with words
        self.lines_short = {p: [] for p in data.ORDER}    # the same without quoted words
        self.knows = {p: [] for p in data.ORDER}          # who they know went out, in order
        self.visit = {}             # goer -> {"got_in", "found", "took"}
        self.choices, self.where, self.awake, self.reacted = {}, {}, {}, set()
        self.bedtime_hunger, self.rooms_at_bedtime, self.state_at_bedtime = {}, {}, {}
        self.morning_hunger = {}

    # ---------- chance ----------
    def u(self, name):
        if name in self.draws:
            return self.draws[name]
        return random.Random(f"{self.seed}:night:{name}").random()

    def order(self):
        """Everyone, in the order they would leave: lowest draw first."""
        if "order" in self.draws:
            return list(self.draws["order"])
        rng = random.Random(f"{self.seed}:night:order")
        draw = {q: rng.random() for q in data.ORDER}
        return sorted(data.ORDER, key=draw.get)

    # ---------- lines ----------
    def line(self, pid, full, short=None):
        self.lines[pid].append(full)
        self.lines_short[pid].append(full if short is None else short)

    def text(self, line):
        self.story.append(("text", line))

    # ---------- asking ----------
    def ask(self, pid, kind, now, opts, fallback):
        """One night decision. Returns (option id, words)."""
        p = self.people[pid]
        prompt = self.m.prompt_for(p, None, opts, night=now)
        d = {"person": pid, "ask": kind, "where": self.where.get(pid, OWN_ROOM[pid]), "now": list(now),
             "options": [o.id for o in opts]}
        seen = p.levels()
        text = self.oracle.ask(NIGHT_SYSTEM, prompt)
        p.seen = seen
        choice, why = self.m.parse(text, opts)
        byid = {o.id: o for o in opts}
        if choice is None:
            d.update(mode="fallback", invalid=why, option=fallback, say=None)
        else:
            if not byid[choice["option"]].speech and choice["say"]:
                choice["say"], choice["dropped_line"] = None, True     # words only for speech at night
            d.update(mode="model", **choice)
            self.m.take_answer(p, choice, NIGHT_MINUTE, d)
        d["label"] = byid[d["option"]].label
        self.decisions.append(d)
        self.story.append(("decision", d))
        return d["option"], d.get("say")

    def notice(self, who, of, how, draw=None, under=None, noticed=True):
        n = {"who": who, "of": of, "how": how, "awake": draw is None, "draw": draw, "under": under,
             "noticed": noticed, "where": self.where[who]}
        self.noticing.append(n)
        self.story.append(("noticing", n))

    # ---------- the night ----------
    def run(self):
        for p in self.people.values():                                  # the gap (§2)
            p.hunger = min(1.0, p.hunger + GAP_HUNGER * p.sheet["hunger_rate"])
            p.room = OWN_ROOM[p.id]
            p.activity = {"kind": "idle", "label": "in bed"}
        self.bedtime_hunger = {q: self.people[q].hunger for q in data.ORDER}
        self.rooms_at_bedtime = {q: self.people[q].room for q in data.ORDER}
        self.state_at_bedtime = {
            q: [json.dumps({t: [g.strength, g.events] for t, g in p.grudges.items()}), p.suspicion.state(), p.guilt]
            for q, p in self.people.items()}
        for q in data.ORDER:                                            # bedtime (§3.2)
            room = OWN_ROOM[q]
            r = ROOMMATE[q]
            now = ["Now it is night. " + data.GAP,
                   f"Everyone has gone to bed in their own room: {BEDS}.",
                   f"You are in the {data.ROOMS[room]}, in your bed. {NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.",
                   f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]
            own = self.people[q].trip_heard.get(q)
            if own and own[1] == "volunteer":           # `volunteer`, or day 2's `still_going`
                now.append(PROMISE)
            opts = [Option(i, label) for i, label in BEDTIME]
            choice, _ = self.ask(q, "bedtime", now, opts, "sleep")
            self.choices[q] = choice
            self.where[q] = "kitchen" if choice == "watch_door" else room
            self.awake[q] = choice != "sleep"
            self.people[q].tonight.append(TONIGHT[choice])
            self.line(q, f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}")
        self.house_u = self.u("house")
        self.house = self.house_left = house_portions(self.house_u)
        pending = [q for q in self.order() if self.choices[q] == "go_next_door"]
        while pending:
            self.leave(pending.pop(0), pending)
        for p in self.people.values():                                  # the rest of the night
            if p.id in self.away:
                p.room = None
                continue
            p.hunger = min(1.0, p.hunger + NIGHT_HUNGER * p.sheet["hunger_rate"])
            p.room = OWN_ROOM[p.id]
        self.morning_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
        return self

    def leave(self, L, pending):
        """L gets up to go: who notices, who stops or joins, the street, the return (§3.3)."""
        room = OWN_ROOM[L]
        group = [L]
        before = {}                 # joiner -> where they were before joining
        self.text(f"{NAMES[L]} gets up to go to the neighbour's house.")
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
        if self.where.get(R) == room:
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
                self.line(R, f"In the night {NAMES[L]} got up in the dark and left the room toward the kitchen and the "
                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).")
                if R not in self.reacted:
                    self.reacted.add(R)
                    now = [f"Now it is night, in the {data.ROOMS[room]}. "
                           + ("You were lying awake." if awake else "You were asleep and woke."),
                           f"{NAMES[L]} has got up in the dark and is leaving the room quietly, toward the kitchen "
                           f"and the front door."]
                    stop = self.react_seen(R, L, now, pending, join)
                    if stop and not self.answer(L, [stop], room, group):
                        back_to_bed()
                        return
        # 2. L passes through the kitchen: whoever sits up by the front door.
        stops = []
        for S in data.ORDER:
            if self.where.get(S) != "kitchen" or S in group:
                continue
            self.notice(S, L, "door watch")
            seen_by.add(S)
            self.knows[S] += [x for x in group if x not in self.knows[S]]
            who = names(group)
            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).")
            if S not in self.reacted:
                self.reacted.add(S)
                now = ["Now it is night. You are sitting up in the kitchen by the front door.",
                       f"{who} {'has' if len(group) == 1 else 'have'} come into the kitchen in the dark and "
                       f"{'is' if len(group) == 1 else 'are'} going to the front door."]
                stop = self.react_seen(S, L, now, pending, join)
                if stop:
                    stops.append(stop)
        if stops and not self.answer(L, stops, "kitchen", group):
            back_to_bed()
            return
        # 3. The front door opens: everyone in a bedroom who has not seen L go.
        for P in data.ORDER:
            if self.where.get(P) not in BEDROOMS or P in group or P in seen_by:
                continue
            awake = self.awake[P]
            if awake:
                self.notice(P, L, "front door")
                heard = True
            else:
                draw = self.u(f"door:{L}:{P}")
                heard = draw < wake_door(P)
                self.notice(P, L, "front door", draw, wake_door(P), heard)
            if not heard:
                continue
            self.awake[P] = True
            self.line(P, f"In the night you {'' if awake else 'woke and '}heard the front door being opened. "
                         f"You did not see who.")
            if P in self.reacted:
                continue
            self.reacted.add(P)
            now = [f"Now it is night, in the {data.ROOMS[self.where[P]]}. "
                   + ("You were lying awake." if awake else "You were asleep and woke."),
                   "From the kitchen comes the sound of the front door being opened. You cannot see who it is."]
            self.react_heard(P, L, now, pending, join, group)
        # 4. The street.
        for P in group:
            self.where[P] = "out"
        self.leavers += group
        self.trip(L, group)

    def react_seen(self, P, L, now, pending, join):
        """P sees L leave (roommate or door sitter). Returns (P, words) if P tells L not to go."""
        n = NAMES[L]
        if P in pending:            # P meant to go too
            opts = [Option(f"go_with_{L}", f"get up and go with {n} to the neighbour's house"),
                    Option(f"stop_{L}", f"tell {n}, low, to stay home, and go yourself instead", True),
                    Option(f"let_{L}_go", f"let {n} go, and go yourself later, alone"),
                    Option("stay_home", f"let {n} go, and stay in bed yourself after all")]
            fallback = f"let_{L}_go"
        else:
            opts = [Option(f"let_{L}_go", f"stay where you are and let {n} go without a word"),
                    Option(f"stop_{L}", f"tell {n}, low, not to go", True),
                    Option(f"go_with_{L}", f"get up and go with {n} to the neighbour's house")]
            fallback = f"let_{L}_go"
        waiting = P in pending
        choice, words = self.ask(P, "reaction", now, opts, fallback)
        if choice == f"go_with_{L}":
            join(P)
            self.line(P, f"You went with {him(L)}.")
            self.people[P].tonight.append(f"you went with {n}.")
        elif choice == f"stop_{L}":
            self.people[P].tonight.append(f"you told {n} not to go.")
            return P, words
        elif choice == "stay_home":
            pending.remove(P)
            self.line(P, f"You let {him(L)} go, and stayed in bed after all.")
        elif waiting:
            self.line(P, f"You let {him(L)} go, to go yourself later.")
        else:
            self.line(P, f"You let {him(L)} go without a word.")
            self.people[P].tonight.append(f"you let {n} go.")
        return None

    def react_heard(self, P, L, now, pending, join, group):
        """P hears the front door from a bedroom."""
        if P in pending:
            opts = [Option("go_after", "get up now and follow whoever it is out to the neighbour's house"),
                    Option("go_later", "wait, then go yourself later, alone"),
                    Option("stay_home", "stay in bed after all")]
            choice, _ = self.ask(P, "reaction", now, opts, "go_later")
            if choice == "go_after":
                join(P)
                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.")
            elif choice == "stay_home":
                pending.remove(P)
                self.line(P, "You stayed in bed after all.")
            else:
                self.line(P, "You waited, to go yourself later.")
            return
        opts = [Option("stay_in_bed", "stay in bed"),
                Option("get_up_and_look", "get up, see whose bed is empty, and wait up by the front door until morning")]
        choice, _ = self.ask(P, "reaction", now, opts, "stay_in_bed")
        if choice == "get_up_and_look":
            gone = [x for x in group]
            beds = (f"{NAMES[gone[0]]}'s bed was empty" if len(gone) == 1 else
                    " and ".join(f"{NAMES[x]}'s" for x in gone) + " beds were empty")
            full = self.lines[P][-1] + f" You got up: {beds}. You waited up by the front door."
            self.lines[P][-1] = self.lines_short[P][-1] = full
            self.where[P] = "kitchen"
            self.knows[P] += [x for x in gone if x not in self.knows[P]]
        else:
            self.line(P, "You stayed in bed.")

    def answer(self, L, stops, place, group):
        """L, told not to go, answers once. Returns True if L goes all the same."""
        where = (f"Now it is night, in the {data.ROOMS[place]}. You had got up to go to the neighbour's house."
                 if place != "kitchen" else
                 "Now it is night, in the kitchen, by the front door. You had got up to go to the neighbour's house.")
        now = [where] + [f'{NAMES[S]} is up and says to you, low: "{w}"' if w else f"{NAMES[S]} is up and tells you, low, not to go."
                         for S, w in stops]
        who = names([S for S, _ in stops])
        opts = [Option("go_anyway", f"answer {who}, and go out to the neighbour's house all the same", True),
                Option("stay_home", f"answer {who}, and go back to bed", True)]
        choice, a = self.ask(L, "answer", now, opts, "go_anyway")
        goes = choice == "go_anyway"
        went = "went all the same" if goes else "went back to bed"
        said = f' You answered: "{a}", and {went}.' if a else f" You {went}."
        told = " ".join(f"{NAMES[S]} told you, low, not to go: {quoted(w)}" if w else f"{NAMES[S]} told you, low, not to go."
                        for S, w in stops)
        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.")
        He = he(L).capitalize()
        for S, w in stops:
            told = f"You told {NAMES[L]}, low, not to go" + (f": {quoted(w)}" if w else ".")
            answered = f' {He} answered: "{a}", and {went}.' if a else f" {He} {went}."
            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.")
        # Low voices: heard, without words, by anyone awake elsewhere; nobody wakes for a whisper.
        talkers = {L} | {S for S, _ in stops} | set(group)
        for P in data.ORDER:
            w = self.where.get(P)
            if P in talkers or w in (None, "out", place) or not self.awake[P]:
                continue
            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.")
        if not goes:
            self.people[L].tonight.append("you went back to bed.")
        return goes

    def trip(self, L, group):
        """The street and the house decide; then the return (§4)."""
        u = self.u(f"trip:{L}")
        st = street(u, len(group))
        found = self.house_left
        g = {"leader": L, "members": list(group), "u": u, "street": st, "found": None, "took": 0, "lost": None,
             "lost_u": None, "shaken": [], "outcome": None}
        if st in ("clean", "scare_back"):
            g["found"] = found
            g["took"] = min(found, CARRY * len(group))
            self.house_left -= g["took"]
        if st in ("scare_there", "scare_back"):
            g["shaken"] = list(group)
        if st == "not_back":
            if len(group) == 1:
                g["lost"] = L
            else:
                g["lost_u"] = self.u(f"lost:{L}")
                g["lost"] = sorted(group)[int(g["lost_u"] * len(group))]
                g["shaken"] = [x for x in group if x != g["lost"]]
            self.away.add(g["lost"])
        g["outcome"] = outcome_class(st, found)
        self.groups.append(g)
        back = [x for x in group if x != g["lost"]]
        k, F = g["took"], g["found"]
        for P in back:
            if st == "clean" and F:
                rest = F - k
                took = (f"You took {k}; {rest} {'is' if rest == 1 else 'are'} still there." if rest else "You took all of it.")
                self.line(P, f"You got inside the neighbour's house and found {portions_text(F)} of food. {took} "
                             f"Nothing troubled you in the street.")
            elif st == "clean":
                self.line(P, "You got inside the neighbour's house and found no food there. Nothing troubled you in "
                             "the street.")
            elif st == "scare_there":
                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.")
            elif st == "scare_back":
                got = (f"and found {portions_text(F)} of food and took {k}" if F else "but found no food")
                self.line(P, f"You got inside the neighbour's house {got}. On the way back, something was moving in the "
                             f"street, and you ran the rest of the way.")
            else:
                self.line(P, f"In the street, something was moving. You lost sight of {NAMES[g['lost']]} in the dark "
                             f"and came back without {him(g['lost'])}.")
            self.line(P, "You came back in by the front door before dawn"
                      + (f" and put the {portions_text(k)} on the shelf." if k else "."))
            self.visit[P] = {"got_in": st in ("clean", "scare_back"), "found": F, "took": k}
        if not back:
            return
        self.portions += k
        # The return: the front door again.
        for P in back:
            self.where[P] = OWN_ROOM[P]
            self.awake[P] = True
        carrying = ", carrying food" if k else f", with nothing in {'their' if len(back) > 1 else data.PRONOUNS[back[0]]['his']} hands"
        shaken = ", and looked shaken" if g["shaken"] else ""
        alone = " alone" if g["lost"] else ""
        for P in data.ORDER:
            w = self.where.get(P)
            if P in group or w in (None, "out"):
                continue
            if w == "kitchen":
                self.notice(P, L, "return")
                self.knows[P] += [x for x in back if x not in self.knows[P]]
                self.line(P, f"Before dawn {names(back)} came back in{alone} by the front door{carrying}{shaken} "
                             f"(you saw it).")
            elif self.awake[P]:
                self.notice(P, L, "return")
                self.line(P, "Before dawn you heard the front door again. You did not see who.")
            else:
                draw = self.u(f"return:{L}:{P}")
                woke = draw < wake_door(P)
                self.notice(P, L, "return", draw, wake_door(P), woke)
                if woke:
                    self.awake[P] = True
                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.")

    # ---------- the record ----------
    def transcript(self):
        return {"house": self.house, "house_u": self.house_u, "house_left": self.house_left,
                "portions_before": self.day1.portions, "portions_after": self.portions,
                "bedtime_hunger": self.bedtime_hunger, "morning_hunger": self.morning_hunger,
                "choices": self.choices, "leavers": self.leavers, "away": [q for q in data.ORDER if q in self.away],
                "decisions": [{k: v for k, v in d.items()} for d in self.decisions],
                "noticing": self.noticing, "groups": self.groups,
                "lines": self.lines}


# ---------- day 2 ----------
def carry_in(day1, n, p, short=False, minutes=True):
    """What p carries into day 2 (§5.2): yesterday's facts as p had them, then their own night."""
    out = [f"Yesterday morning Elena counted the pantry and found one can fewer than she expected "
           f"({'you did it' if p.id == 'elena' else 'you saw it'})."]
    c = day1.culprit
    if p.confessed:
        sure = next(x for x in p.sure if "you admitted aloud that you took the can" in x)
        front = sure.split(", in front of ", 1)[1].rstrip(".").split(", ") if ", in front of " in sure else None
        out.append(f"You admitted at minute {sure[4:6]} that you took the can"
                   + (f", in front of {names([q for q in data.ORDER if NAMES[q] in front])}." if front else "."))
    elif p.knows_culprit and p.knows_culprit != p.id:
        sure = next(x for x in p.sure if " admitted taking the can: " in x)
        words = sure.split(" admitted taking the can: ", 1)[1].rsplit(" (you heard it)", 1)[0]
        after = ", after denying it to you" if p.knows_culprit in p.denials_heard else ""
        out.append(f"{NAMES[p.knows_culprit]} admitted taking the can at minute {p.confession_heard_at:02d}{after}: "
                   f"{words} (you heard it).")
    elif c is not None and p.id == c:
        accusers = [q for q in data.ORDER if q in p.accused_by]
        out.append("Nobody found out that you ate the can" + (f"; {names(accusers)} accused you." if accusers
                                                              else ", and nobody named you."))
    else:
        out.append("Nobody admitted taking the can, and it was not found.")
    for x in p.sure:
        if x[8:].startswith("you finished searching the "):
            out.append(f"You searched the {x[8 + len('you finished searching the '):].split(':')[0]} at minute "
                       f"{x[4:6]} and found nothing.")
    acc = {}
    for turn in day1.transcript["turns"]:
        for a in turn["acts"]:
            if a["option"].startswith("accuse_") and (a["who"] == p.id or p.id in a["audience"]):
                acc.setdefault((a["who"], a["option"][len("accuse_"):]), []).append(turn["minute"])
    if acc:
        parts = []
        for (a, t), ms in acc.items():
            times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
            when = f" (min {', '.join(f'{x:02d}' for x in ms)})" if minutes else ""
            parts.append(f"{'you' if a == p.id else NAMES[a]} accused {'you' if t == p.id else NAMES[t]}{times}{when}")
        text = "; ".join(parts)
        out.append(f"Accusations: {text}.")
    ate = {}
    for x in p.sure:
        if " ate one of the portions" in x:
            mm, rest = x[4:6], x[8:]
            ate.setdefault(mm, []).append("you" if rest.startswith("you ate") else rest.split(" ate one")[0])
    for mm, who in ate.items():
        mine = "you" in who
        who = (["You"] if mine else []) + [w for w in who if w != "you"]
        each = " each" if len(who) > 1 else ""
        out.append(f"{' and '.join(who)} ate a portion{each} at minute {mm}" + ("." if mine else " (you saw it)."))
    plan = day1.heard_plan(p)
    if plan:
        out.append("About going to the neighbour's house last night, where it was left: "
                   + plan[len("About going there tonight: "):])
    out.append(data.GAP)
    out += (n.lines_short if short else n.lines)[p.id]
    return ["Yesterday and last night:"] + [f"- {x}" for x in out]


def bounded_carry_in(day1, n, p):
    """The block within CARRY_IN_MAX: the quoted night words go first, then the accusations' minutes."""
    for short, minutes in ((False, True), (True, True), (True, False)):
        block = carry_in(day1, n, p, short, minutes)
        if estimate_tokens("\n".join(block)) <= CARRY_IN_MAX:
            break
    return block


def neighbour_line(n, pid):
    """Their "About the neighbour's house:" line on day 2 (§5.3)."""
    v = n.visit.get(pid)
    if v:
        if v["got_in"] and v["found"]:
            rest = v["found"] - v["took"]
            left = f", and {rest} {'is' if rest == 1 else 'are'} still there" if rest else ", and none are left there"
            return (f"About the neighbour's house: you went in last night and found {portions_text(v['found'])}; "
                    f"you brought back {v['took']}{left}. Outside is dangerous.")
        if v["got_in"]:
            return "About the neighbour's house: you went in last night and found no food there. Outside is dangerous."
        return "About the neighbour's house: you did not get inside last night. Outside is dangerous."
    known = [x for x in n.knows[pid] if x != pid]
    if not known:
        return NEIGHBOUR_UNKNOWN
    x = known[0]
    g = next(g for g in n.groups if x in g["members"])
    if x in n.away:
        how = " and has not come back"
    else:
        how = " and came back with food" if g["took"] else " and came back with nothing"
    return f"About the neighbour's house: {NAMES[x]} went there last night{how}. Outside is dangerous."


def next_day(day1, n, oracle):
    """Day 2: a Morning of day 5 with each person as the night left them (§5.1)."""
    m = world.Morning(oracle, day1.seed, day1.scenario, day=5)
    m.people = n.people
    m.portions = m.start_portions = n.portions
    m.away = set(n.away)
    m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}
    present = [q for q in data.ORDER if q not in m.away]
    before, after = n.day1.portions, n.portions
    for q in data.ORDER:
        p = m.people[q]
        m.carry[q] = bounded_carry_in(day1, n, p)
        m.neighbour[q] = neighbour_line(n, q)
    brought = {P: g["took"] for g in n.groups for P in g["members"] if g["took"] and P not in m.away}
    shaken = {P for g in n.groups for P in g["shaken"] if P not in m.away}
    for q in data.ORDER:
        p = m.people[q]
        p.yesterday = {"confessed": p.confessed,
                       "confession_heard": bool(p.knows_culprit and p.knows_culprit != p.id),
                       "suspected_at": [mm for mm in p.suspected_at if mm < NIGHT_MINUTE],
                       "suspected_last_night": any(mm >= NIGHT_MINUTE for mm in p.suspected_at),
                       "denials": set(p.denials_heard),
                       "accused_by": set(p.accused_by)}
        for g in p.grudges.values():
            g.events = [(e[0], ("yesterday, " + e[1]) if e[2] == "event" else e[1], e[2],
                         "last night" if e[0] >= NIGHT_MINUTE else "yesterday") for e in g.events]
            g.last_change = 0
        p.suspicion.last_fall = 0
        p.suspected_at = []
        p.guilt_events = [(mm, "yesterday, " + fact) for mm, fact in p.guilt_events]
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
        for x in data.ORDER:
            if x in m.away:
                pro = data.PRONOUNS[x]
                opening += (f" {NAMES[x]} is not here: {pro['his']} bed is empty and {pro['he']} is nowhere in the "
                            f"house, so {pro['he']} went out in the night and has not come back.")
        p.sure = [f"min 00: {opening} (you saw it)"]
        p.triggers.append((TRIGGER, True))
        p.seen = p.levels()
    for q in m.away:
        m.people[q].seen = m.people[q].levels()
    # For the story: what each of them had at minute 00 besides the block.
    m.carried = {q: m.people[q].sure[:1] + m.trip_lines(m.people[q])[:2] for q in present}
    m.started("kitchen", 0, TRIGGER, False)
    return m
