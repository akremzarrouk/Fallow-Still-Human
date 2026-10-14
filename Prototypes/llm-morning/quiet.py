"""The quiet day, stage A (reports/quiet_day_design.md, §1.1, §1.2, §2.1, §2.2, §3, §4 and §6.1), from day 3 on.

The morning is played in 3-minute turns as before, until every room's conversation has ended. Then the day jumps from
one event to the next (a rest running out, a need crossing a line, a rest falling due) up to bedtime at 21:00, and the
time of each person between events is a routine span: resting on their own bed, keeping to their own room after a
quarrel, or sitting in the kitchen. Inside a quiet stretch the model is asked only when a need crosses a line with
someone awake there (Q1), or when a routine brings two people with a grievance together after an hour without a word
between them (Q2); then the house is played in turns again until that room's conversation ends.

Two needs are counted by the code from day 1 on. Fasting is the hours since they last ate × their hunger rate; sleep
debt is +1 an hour awake, paid back by the night's bedtime choice and by rest. At a threshold each changes the body
line: a situation, never an act. Neither is the model's.

The brief's amendments: no doze draw; each rest lasts a seeded 2 to 4 hours; records and summaries say the clock from
minute 90 on; only Q1 and Q2; at most 12 quiet asks (4 of one person) and 40 asks in a day.
"""
import math
import random

import data
from world import NAMES, day_index

DAY_END = 840               # 21:00, bedtime (§3)
CLOCK_FROM = 90             # from this minute on, records and summaries say the clock (amendment 3)
START = 7 * 60              # minute 00 is 07:00
WEAK, VERY_WEAK = 48, 96    # fasting (§1.1)
TIRED, EXHAUSTED = 16, 24   # sleep debt (§1.2)
DAY_HOURS = 14              # a day not played to bedtime: awake from 07:00 to 21:00
NIGHT_PAYS = {"sleep": 8, "lie_awake": 3, "watch_door": 0, "go_next_door": 0}
SLEEP_STARVING = 6
REST_PAYS = 1.5             # an hour on one's bed
REST_UNTIL = 12
REST_LENGTH = range(120, 241, 3)        # amendment 2: seeded, so they get up at different times
RESTS_A_DAY, REST_APART = 2, 120
BEFORE_DAY_1 = -720         # house day 3, 19:00: when each of them last ate before day 1, fixed by code (§1.1)
THE_CAN = -240              # house day 4, 03:00: the can, for whoever took it
STAYS = {"dominant": 0.8, "empathetic": 0.85}   # §2.1: Daniel (dominant 0.85) and Elena (empathetic 0.9) stay
WITHDRAW_GRUDGE = 3
Q2_GRUDGE, Q2_APART, Q2_EVERY = 2, 60, 120
QUIET_ASKS, QUIET_ASKS_EACH, DAY_ASKS = 12, 4, 40
HUNGER_A_MINUTE = 0.004     # × hunger rate, as a played turn adds it (world.py)
OWN_ROOM = {p: room for room, owners in data.OWNERS.items() for p in owners}

FAST_WORDS = {1: ", and weak from it: standing up makes your head spin",
              2: ", and very weak: your legs shake when you stand"}
DEBT_WORDS = {1: "you have hardly slept", 2: "you have barely slept for nights; your eyes close on their own"}
# A need crossing a line, as the person's own record of it (§3: its own event, with them alone as witness).
NEED_VIEWS = {("fast", 1): "You had grown weak from hunger: standing up made your head spin.",
              ("fast", 2): "You had grown very weak: your legs shook when you stood.",
              ("debt", 1): "You had hardly slept, and you felt it.",
              ("debt", 2): "You had barely slept for nights; your eyes were closing on their own."}


def clock(minute):
    """A minute of the day as records and summaries say it: "min 18" before minute 90, the clock from then on."""
    if minute < CLOCK_FROM:
        return f"min {minute:02d}"
    h, m = divmod(START + minute, 60)
    return f"{h:02d}:{m:02d}"


def grid(minute):
    """The first minute of the 3-minute grid at or after `minute`."""
    return int(math.ceil(minute / data.MINUTES_PER_TURN - 1e-9)) * data.MINUTES_PER_TURN


def absolute(k, minute):
    """Minutes since 07:00 of day 1."""
    return (k - 1) * 1440 + minute


def fast_stage(f):
    return 2 if f >= VERY_WEAK else 1 if f >= WEAK else 0


def debt_stage(d):
    return 2 if d >= EXHAUSTED else 1 if d >= TIRED else 0


def body_line(hunger, fast, debt):
    """The body line from day 3 on: the hunger word, then what fasting and sleep debt have come to."""
    line = f"Your body: {hunger}" + FAST_WORDS.get(fast, "")
    if debt:
        line += ("; and " if fast else ", and ") + DEBT_WORDS[debt]
    return line + "."


def night_payback(choice, starving):
    """What a night's bedtime choice pays back of the debt (§1.2)."""
    if choice == "sleep" and starving:
        return SLEEP_STARVING
    return NIGHT_PAYS.get(choice, 0)


def rest_length(seed, k, pid, n):
    """The length of their n-th rest of day k, drawn from a string of its own (amendment 2)."""
    return random.Random(f"{seed}:day{k}:rest:{pid}:{n}").choice(REST_LENGTH)


def last_meals(chronicle, culprit):
    """When each of them last ate, in minutes since day 1, 07:00, from the chronicle's eat events."""
    out = {q: BEFORE_DAY_1 for q in data.ORDER}
    if culprit:
        out[culprit] = THE_CAN
    for e in chronicle.events:
        if e["scene"][0] != "D":
            continue
        if e["kind"] in ("eat", "eat_given"):
            eaters = [e["actor"]]
        elif e["kind"] == "share":
            eaters = [e["actor"]] + [q for q, how in e["witnesses"].items() if how == "saw"]
        else:
            continue
        at = absolute(int(e["scene"][1:]), e["minute"])
        for q in eaters:
            out[q] = max(out[q], at)
    return out


def setup(m, chronicle):
    """Day k ≥ 3, before anyone has decided: each person's needs as the days and nights before left them (§6)."""
    k = day_index(m.day)
    m.quiet = q = Quiet(m, k)
    meals = last_meals(chronicle, m.culprit)
    nights = chronicle.nights[:k - 1]
    for pid in data.ORDER:
        p = m.people[pid]
        if pid in m.away:
            p.needs = None
            continue
        if p.needs is not None:             # a quiet day before: its debt at bedtime, then last night
            debt, last = p.needs["debt"], nights[-1:]
        else:                               # from day 1, at 0: 14 hours a day, then each night
            debt, last = 0.0, None
        for n in (last if last is not None else nights):
            if last is None:
                debt += DAY_HOURS
            starving = n.bedtime_hunger.get(pid) is not None and n.bedtime_hunger[pid] >= 0.85
            debt = max(0.0, debt - night_payback(n.choices.get(pid), starving))
        p.needs = {"ate_at": meals[pid], "debt": debt, "debt_at": 0, "rests": 0, "last_rest_end": None,
                   "fast_stage": 0, "debt_stage": 0}
    q.tick(0)
    return q


class Quiet:
    """The quiet layer of one day: the needs, the routine spans, the triggers and the budget."""

    def __init__(self, m, k):
        self.m, self.k = m, k
        self.open = {}              # pid -> the span they are in
        self.spans = []             # every span, closed, in the order they began
        self.pending = {}           # pid -> the quiet ask waiting for their next decision
        self.quiet_asked = []       # every quiet ask let through: {"minute", "who", "kind", "done"}
        self.log = []               # every Q1 and Q2 checked, fired or not, and why
        self.exchanged = {}         # (a, b) sorted -> the minute of the last line between them
        self.q2_last = {}           # (a, b) -> the minute Q2 last fired for them
        self.q1_done = set()        # (pid, need, stage)
        self.stages = {}            # pid -> (fasting stage, debt stage) at the last tick
        self.needs_log = {}         # pid -> [[minute, fasting, debt]] at every event
        self.need_events = []       # each need crossing a line
        self.withdrawals = []
        self.stretches = []         # each run of played turns: {"start", "end", "room", "trigger"}
        self.asks = 0               # the model's answers asked today
        self.morning_end = None
        self.seq = 0                # orders spans and need events that share a minute
        self.left = None            # the last move: (pid, the room they left, who saw them go)

    # ---------- the needs ----------
    def people(self):
        return [p for p in self.m.people.values() if p.id not in self.m.away and p.room is not None]

    def fast(self, p, minute):
        return max(0.0, absolute(self.k, minute) - p.needs["ate_at"]) / 60 * p.sheet["hunger_rate"]

    def resting(self, pid):
        return self.open.get(pid, {}).get("routine") == "rest"

    def debt(self, p, minute):
        rate = -REST_PAYS if self.resting(p.id) else 1.0
        return max(0.0, p.needs["debt"] + rate * (minute - p.needs["debt_at"]) / 60)

    def set_debt(self, p, value, minute):
        p.needs["debt"], p.needs["debt_at"] = value, minute

    def settle(self, p, minute):
        self.set_debt(p, self.debt(p, minute), minute)

    def tick(self, minute):
        """The needs at `minute`: each stage that rose since the last tick, as (pid, "fast" | "debt", stage)."""
        out = []
        for p in self.people():
            f, d = self.fast(p, minute), self.debt(p, minute)
            fs, ds = fast_stage(f), debt_stage(d)
            old = self.stages.get(p.id, (fs, ds))
            for need, now, before, value in (("fast", fs, old[0], f), ("debt", ds, old[1], d)):
                if now > before:
                    out.append((p.id, need, now))
                    self.seq += 1
                    self.need_events.append({"minute": minute, "who": p.id, "need": need, "stage": now,
                                             "value": round(value, 3), "room": p.room, "seq": self.seq,
                                             "view": NEED_VIEWS[(need, now)]})
            self.stages[p.id] = (fs, ds)
            p.needs["fast_stage"], p.needs["debt_stage"] = fs, ds
            log = self.needs_log.setdefault(p.id, [])
            if not log or log[-1][0] != minute:
                log.append([minute, round(f, 3), round(d, 3)])
        return out

    # ---------- the budget (§4) ----------
    def spent(self):
        return self.asks >= DAY_ASKS

    def budget(self, pid):
        """Why a quiet ask of pid cannot be made now, or None."""
        if self.spent():
            return f"the day's {DAY_ASKS} asks are spent"
        if len(self.quiet_asked) >= QUIET_ASKS:
            return f"{QUIET_ASKS} quiet asks today"
        if sum(1 for a in self.quiet_asked if a["who"] == pid) >= QUIET_ASKS_EACH:
            return f"{QUIET_ASKS_EACH} quiet asks of {NAMES[pid]} today"
        return None

    def ask(self, p, kind, minute, text, why):
        """A quiet trigger asks p at their next decision, and their room is played until its conversation ends."""
        if p.id in self.pending:
            if text:
                self.pending[p.id]["texts"].append(text)
            return
        self.pending[p.id] = {"kind": kind, "minute": minute, "texts": [text] if text else []}
        self.quiet_asked.append({"minute": minute, "who": p.id, "kind": kind, "done": False})
        if self.resting(p.id):
            self.end(p, minute, "woken")
            if text:
                p.memory.append((minute, text[0].upper() + text[1:] + "."))
        self.m.started(p.room, minute, why, kind == "Q1")

    def asked(self, pid):
        """The model has been asked for a pending quiet ask of pid."""
        for a in reversed(self.quiet_asked):
            if a["who"] == pid and not a["done"]:
                a["done"] = True
                return

    # ---------- spans (§2, §3) ----------
    def awake_with(self, p, room=None):
        room = room or p.room
        return [q for q in self.people() if q.room == room and q.id != p.id and not self.resting(q.id)]

    def start(self, p, routine, minute, planned=None, until=None, leave=None):
        """p begins a routine where they are."""
        self.settle(p, minute)
        self.seq += 1
        his = data.PRONOUNS[p.id]["his"]
        seen = self.awake_with(p)
        span = {"who": p.id, "routine": routine, "room": p.room, "start": minute, "end": None, "planned": planned,
                "until": until, "ended": None, "seen_start": [q.id for q in seen], "seen_end": [],
                "seen_leave": list(leave or []), "left": None, "seq": self.seq}
        self.open[p.id] = span
        self.spans.append(span)
        # Hours pass in a routine: what they did before it is not "in a row" with what they do after (world.pattern).
        p.history.append({"t": minute // data.MINUTES_PER_TURN, "kind": "routine", "seq": None})
        if routine == "rest":
            p.needs["rests"] += 1
            p.activity = {"kind": "resting", "label": f"lying on {his} bed"}
            p.memory.append((minute, "you lay down on your bed."))
            for q in seen:
                q.memory.append((minute, f"{p.name} lies down on {his} bed."))
        elif routine == "withdraw":
            p.activity = {"kind": "idle", "label": f"keeping to {his} room"}
        else:
            p.activity = {"kind": "idle", "label": "sitting in the kitchen"}
        return span

    def end(self, p, minute, why):
        span = self.open.get(p.id)
        if span is None:
            return None
        self.settle(p, minute)
        del self.open[p.id]
        span.update(end=minute, ended=why, seen_end=[q.id for q in self.awake_with(p)])
        if minute == span["start"]:         # over as it began: no span, no rest taken, and nobody saw one
            self.spans.remove(span)
            if span["routine"] == "rest":
                p.needs["rests"] -= 1
                p.activity = {"kind": "idle", "label": "just got up"}
                his = data.PRONOUNS[p.id]["his"]
                for q, line in [(p, "you lay down on your bed.")] + [(self.m.people[x], f"{p.name} lies down on {his} bed.")
                                                                      for x in span["seen_start"]]:
                    if (minute, line) in q.memory:
                        q.memory.remove((minute, line))
            return None
        if span["routine"] == "rest":
            his = data.PRONOUNS[p.id]["his"]
            p.needs["last_rest_end"] = minute
            p.activity = {"kind": "idle", "label": "just got up"}
            p.memory.append((minute, "you got up from your bed."))
            for q in self.awake_with(p):
                q.memory.append((minute, f"{p.name} gets up from {his} bed."))
        return span

    def rest_end(self, p, start, length):
        """When a rest begun at `start` ends: after its seeded length, or once debt is below 12 (§2.2). A rest begun
        below 12 (fasting made them lie down) lasts its length."""
        d = self.debt(p, start)
        end = start + length
        if d >= REST_UNTIL:
            by_debt = grid(start + (d - REST_UNTIL) / REST_PAYS * 60)
            if d - REST_PAYS * (by_debt - start) / 60 >= REST_UNTIL:
                by_debt += data.MINUTES_PER_TURN
            end = min(end, by_debt)
        return end

    def rest_due(self, p, minute):
        n = p.needs
        if n["rests"] >= RESTS_A_DAY or (n["last_rest_end"] is not None and minute - n["last_rest_end"] < REST_APART):
            return False
        return self.debt(p, minute) >= TIRED or self.fast(p, minute) >= VERY_WEAK

    def arrive(self, p, room, minute):
        """A routine brings p into `room`: who sees them go and come, a withdrawal it interrupts, and Q2. Returns the
        Q2 asks it fired."""
        left = p.room
        gone_from = self.awake_with(p, left)
        for q in gone_from:
            q.memory.append((minute, f"{p.name} goes to the {data.ROOMS[room]}."))
        p.memory.append((minute, f"you went to the {data.ROOMS[room]}."))
        p.room = room
        self.left = (p.id, left, [q.id for q in gone_from])
        there = [q for q in self.people() if q.room == room and q.id != p.id]
        for q in there:
            if not self.resting(q.id):
                q.memory.append((minute, f"{p.name} comes into the {data.ROOMS[room]}."))
        for q in there:
            if self.open.get(q.id, {}).get("routine") == "withdraw":
                self.end(q, minute, "someone came in")
        return self.meet(p, there, minute)

    def meet(self, a, there, minute):
        """Q2 (§4): a routine brings A into a room where B is; one of them holds a grudge of 2 or more against the
        other; no line between them for 60 minutes; not in the 2 hours since they last met this way. The holder of
        the higher grudge is asked, B on a tie."""
        fired = []
        for b in sorted(there, key=lambda x: data.ORDER.index(x.id)):
            ga = a.grudges[b.id].strength if b.id in a.grudges else 0
            gb = b.grudges[a.id].strength if a.id in b.grudges else 0
            if max(ga, gb) < Q2_GRUDGE:
                continue
            pair = tuple(sorted((a.id, b.id)))
            last = self.exchanged.get(pair)
            within = pair in self.q2_last and minute - self.q2_last[pair] < Q2_EVERY
            asked = a if ga > gb else b
            entry = {"kind": "Q2", "minute": minute, "room": a.room, "pair": list(pair), "arrived": a.id,
                     "there": b.id, "grudges": {a.id: ga, b.id: gb}, "last_line": last, "within_2h": within,
                     "fired": False, "asked": None, "why": None}
            self.log.append(entry)
            if last is not None and minute - last < Q2_APART:
                entry["why"] = f"a line between them {minute - last} minutes before"
                continue
            if within:
                entry["why"] = f"they met this way {minute - self.q2_last[pair]} minutes before"
                continue
            budget = self.budget(asked.id)
            if budget and asked.id not in self.pending:
                entry["budget"] = entry["why"] = budget
                continue
            entry.update(fired=True, asked=asked.id)
            self.q2_last[pair] = minute
            text = (f"{a.name} comes into the {data.ROOMS[a.room]}" if asked is b
                    else f"you come into the {data.ROOMS[a.room]}, where {b.name} is")
            self.ask(asked, "Q2", minute, text,
                     f"Q2, a grievance meets: {a.name} came into the {data.ROOMS[a.room]}, where {b.name} was")
            fired.append(entry)
        return fired

    def ask_q1(self, crossings, minute):
        """Q1 (§4): fasting reaches 48 or 96, or debt 24, in a quiet stretch, with another awake person in the room.
        Once per person per threshold; with nobody awake there it is recorded only."""
        fired = []
        for pid, need, stage in crossings:
            if (need == "debt" and stage < 2) or (pid, need, stage) in self.q1_done:
                continue
            p = self.m.people[pid]
            entry = {"kind": "Q1", "minute": minute, "room": p.room, "who": pid, "need": need, "stage": stage,
                     "fired": False, "asked": None, "why": None}
            self.log.append(entry)
            if self.resting(pid):
                entry["why"] = "asleep"
                continue
            if not self.awake_with(p):
                entry["why"] = "alone"
                continue
            budget = self.budget(pid)
            if budget:
                entry["budget"] = entry["why"] = budget
                continue
            entry.update(fired=True, asked=pid)
            self.q1_done.add((pid, need, stage))
            word = {("fast", 1): "weak", ("fast", 2): "very weak", ("debt", 2): "exhausted"}[(need, stage)]
            self.ask(p, "Q1", minute, None, f"Q1, a need crossed a line: {p.name} has grown {word}")
            fired.append(entry)
        return fired

    # ---------- quiet mode (§3) ----------
    def routine_for(self, p, minute):
        if self.rest_due(p, minute):
            return "rest", OWN_ROOM[p.id]
        return "sit", "kitchen"

    def assign(self, minute):
        """Everyone without a routine (and not about to be asked) takes one, in the family's order: rest if it is due,
        else sit in the kitchen (§2). A sitter whose rest falls due goes to rest; whoever keeps to their room stays."""
        for _ in range(len(data.ORDER) + 1):
            changed = False
            for p in sorted(self.people(), key=lambda x: data.ORDER.index(x.id)):
                span = self.open.get(p.id)
                if span and span["routine"] == "sit" and self.rest_due(p, minute):
                    self.end(p, minute, "went to rest")
                    span = None
                if span or p.id in self.pending or self.m.convos.active[p.room]:
                    continue
                routine, room = self.routine_for(p, minute)
                leave, left = [], None
                if p.room != room:
                    left = p.room
                    self.arrive(p, room, minute)
                    leave = self.left[2]
                    if p.id in self.pending or self.m.convos.active[room]:
                        changed = True              # a trigger starts the talk here: played first, routine after
                        continue
                if routine == "rest":
                    length = rest_length(self.m.seed, self.k, p.id, p.needs["rests"] + 1)
                    until = self.rest_end(p, minute, length)
                    span = self.start(p, "rest", minute, planned=length, until=until, leave=leave)
                else:
                    span = self.start(p, "sit", minute, leave=leave)
                span["left"] = left
                changed = True
            if not changed:
                break

    def run_out(self, minute):
        """Rests whose time is up end: after their seeded length ("time") or once debt is below 12 ("rested")."""
        for p in self.people():
            span = self.open.get(p.id)
            if span and span["until"] is not None and span["until"] <= minute:
                self.end(p, minute, "time" if span["until"] - span["start"] == span["planned"] else "rested")

    def step(self, minute):
        """Quiet mode at `minute`: the needs, routines running out, new routines and their arrivals, Q2 and Q1.
        Returns True when a trigger has fired, so played turns start here."""
        crossings = self.tick(minute)
        self.run_out(minute)
        self.assign(minute)
        self.ask_q1(crossings, minute)
        # Whoever began a routine this minute in a room where a trigger has just started the talk is in that talk.
        for p in self.people():
            span = self.open.get(p.id)
            if span and span["start"] == minute and self.m.convos.active[span["room"]]:
                self.end(p, minute, "the talk began")
        return bool(self.pending)

    def next_event(self, minute):
        """The next minute anything changes: a rest running out, a need crossing a line, a rest falling due for a
        sitter, or bedtime. Never past bedtime."""
        out = [DAY_END]
        for p in self.people():
            span = self.open.get(p.id)
            if span and span["until"] is not None:
                out.append(span["until"])
            rate = p.sheet["hunger_rate"]
            f = self.fast(p, minute)
            out += [grid(minute + (th - f) / rate * 60) for th in (WEAK, VERY_WEAK) if f < th]
            if not self.resting(p.id):
                d = self.debt(p, minute)
                out += [grid(minute + (th - d) * 60) for th in (TIRED, EXHAUSTED) if d < th]
                n = p.needs
                if span and span["routine"] == "sit" and n["rests"] < RESTS_A_DAY:
                    allowed = minute if n["last_rest_end"] is None else n["last_rest_end"] + REST_APART
                    due = min(minute + max(0.0, TIRED - d) * 60, minute + max(0.0, VERY_WEAK - f) / rate * 60)
                    out.append(grid(max(allowed, due)))
        return min([x for x in out if x > minute] or [minute + data.MINUTES_PER_TURN])

    def advance(self, minute, to):
        """The jump: hunger as played turns would have added it; debt and fasting are counted from the clock."""
        for p in self.people():
            p.hunger = min(1.0, p.hunger + HUNGER_A_MINUTE * (to - minute) * p.sheet["hunger_rate"])

    # ---------- played turns ----------
    def turn(self, t):
        """One played turn of a quiet day: the needs first (a line crossed here is that person's inner moment, not
        Q1), the turn, then what it changes for the routines."""
        minute = t * data.MINUTES_PER_TURN
        for pid, need, stage in self.tick(minute):
            self.q1_done.add((pid, need, stage))
        self.run_out(minute)            # a rest out of the played room ends on time; the next routine waits
        rooms = {p.id: p.room for p in self.m.people.values()}
        self.m.turn(t)
        self.after_turn(t, rooms)

    def after_turn(self, t, rooms):
        m = self.m
        minute = t * data.MINUTES_PER_TURN
        after = minute + data.MINUTES_PER_TURN
        acts = m.transcript["turns"][-1]["acts"]
        self.pending.clear()            # asked this turn; a withdraw below may fire a new one, for the next turn
        for a in acts:
            if a["words"]:
                for q in a["audience"]:
                    self.exchanged[tuple(sorted((a["who"], q)))] = minute
        # A routine ends when its person does anything but stay put; whoever keeps to their room is interrupted by
        # anyone coming in.
        for a in acts:
            if a["option"] != "silent":
                self.end(m.people[a["who"]], minute, "acted")
        for p in self.people():
            if p.room != rooms.get(p.id):
                for q in self.people():
                    if q.room == p.room and q.id != p.id and self.open.get(q.id, {}).get("routine") == "withdraw":
                        self.end(q, after, "someone came in")
        for a in acts:
            why = self.withdraw_why(m.people[a["who"]], a, minute)
            if why:
                self.withdraw(m.people[a["who"]], after, why)
        if self.spent():
            for r in data.ROOMS:
                if m.convos.active[r]:
                    m.convos.active[r] = False
                    m.convos.log.append((after, r, "ended", "the day's asks are spent"))

    def withdraw_why(self, p, a, minute):
        """§2.1: they chose `silent`; they spoke earlier in this conversation; they hold a grudge of 3 against someone
        still in the room; they are neither dominant nor empathetic enough to stay. The conditions, or None."""
        if a["option"] != "silent" or a["mode"] != "model" or p.room is None or p.room == OWN_ROOM[p.id]:
            return None
        if any(p.sheet["traits"][t] >= v for t, v in STAYS.items()):
            return None
        start = next((mm for mm, r, what, _ in reversed(self.m.convos.log)
                      if r == a["room"] and what == "started" and mm <= minute), None)
        if start is None:
            return None
        spoke = [turn["minute"] for turn in self.m.transcript["turns"] if start <= turn["minute"] < minute
                 for x in turn["acts"] if x["who"] == p.id and x["words"] and x["room"] == a["room"]]
        held = [q for q in data.ORDER if q in p.grudges and p.grudges[q].strength >= WITHDRAW_GRUDGE
                and self.m.people[q].room == p.room]
        if not spoke or not held:
            return None
        return {"chose": "silent", "spoke_at": spoke[-1], "grudge_against": held}

    def withdraw(self, p, minute, why):
        room = OWN_ROOM[p.id]
        self.end(p, minute, "withdrew")
        left = p.room
        self.arrive(p, room, minute)
        span = self.start(p, "withdraw", minute, leave=self.left[2])
        span["left"] = left
        self.withdrawals.append({"who": p.id, "minute": minute, "room": room, "why": why})

    def bedtime(self):
        self.tick(DAY_END)
        for p in self.people():
            self.end(p, DAY_END, "bedtime")
            self.settle(p, DAY_END)
        self.pending.clear()

    # ---------- the record ----------
    def views(self, span):
        """Each witness's own line of a span (§3): the actor's, then what each other saw of its start, its end, or
        their going."""
        who, room = span["who"], data.ROOMS[span["room"]]
        name, his = NAMES[who], data.PRONOUNS[who]["his"]
        s, e = clock(span["start"]), clock(span["end"])
        r = span["routine"]
        out = {who: {"rest": f"You lay on your bed in the {room} from {s} to {e}.",
                     "withdraw": f"You went off to your own room, the {room}, and kept to it from {s} to {e}.",
                     "sit": f"You sat in the kitchen from {s} to {e}."}[r]}
        both = {"rest": f"{name} lay on {his} bed in the {room} from {s} to {e}.",
                "withdraw": f"{name} kept to {his} room, the {room}, from {s} to {e}.",
                "sit": f"{name} sat in the kitchen from {s} to {e}."}[r]
        first = {"rest": f"{name} lay down on {his} bed in the {room} at {s}.",
                 "withdraw": f"{name} came into the {room}, {his} own room, at {s}.",
                 "sit": f"{name} sat down in the kitchen at {s}."}[r]
        last = {"rest": f"{name} got up from {his} bed in the {room} at {e}.",
                "withdraw": f"{name} was keeping to {his} room, the {room}, at {e}.",
                "sit": f"{name} was sitting in the kitchen at {e}."}[r]
        for q in data.ORDER:
            if q == who:
                continue
            parts = []
            if q in span["seen_leave"]:
                parts.append(f"{name} left the {data.ROOMS[span['left']]} for the {room} at {s}.")
            a, b = q in span["seen_start"], q in span["seen_end"]
            parts += [both] if a and b else [first] if a else [last] if b else []
            if parts:
                out[q] = " ".join(parts)
        return out

    def items(self):
        """The spans and need crossings as chronicle events, in the order they began."""
        out = []
        for s in self.spans:
            if s["end"] is None:
                continue
            views = self.views(s)
            out.append((s["start"], s["seq"], {
                "minute": s["start"], "kind": "routine", "routine": s["routine"], "until": s["end"], "actor": s["who"],
                "room": s["room"], "witnesses": {q: ("did" if q == s["who"] else "saw") for q in views},
                "views": views, "text": f"{NAMES[s['who']]}: {s['routine']} in the {data.ROOMS[s['room']]}, "
                                        f"{clock(s['start'])} to {clock(s['end'])}"}))
        for n in self.need_events:
            out.append((n["minute"], n["seq"], {
                "minute": n["minute"], "kind": "need", "need": n["need"], "stage": n["stage"], "actor": n["who"],
                "room": n["room"], "witnesses": {n["who"]: "did"}, "views": {n["who"]: n["view"]},
                "text": f"{NAMES[n['who']]}: {n['need']} reached stage {n['stage']} ({n['value']})"}))
        return [e for _, _, e in sorted(out, key=lambda x: (x[0], x[1]))]

    def transcript(self):
        keys = ("who", "routine", "room", "start", "end", "planned", "ended", "seen_start", "seen_end", "seen_leave",
                "left")
        done = [a for a in self.quiet_asked if a["done"]]
        return {"morning_end": self.morning_end,
                "spans": [{k: s[k] for k in keys} for s in self.spans if s["end"] is not None],
                "needs": self.needs_log,
                "need_events": [{k: v for k, v in n.items() if k not in ("seq", "view")} for n in self.need_events],
                "withdrawals": self.withdrawals, "log": self.log, "stretches": self.stretches,
                "asks": {"day": self.asks, "quiet": len(done),
                         "quiet_by_person": {q: sum(1 for a in done if a["who"] == q) for q in data.ORDER},
                         "quiet_let_through": len(self.quiet_asked)}}


def play(m, told=None):
    """A quiet day from its opening to bedtime (§3). told(t): called after each played turn."""
    q = m.quiet
    t = 0
    stretch = {"start": 0, "end": None, "room": "kitchen", "trigger": "the morning"}
    while t * data.MINUTES_PER_TURN < DAY_END:
        minute = t * data.MINUTES_PER_TURN
        if stretch is not None:
            q.turn(t)
            if told:
                told(t)
            t += 1
            if not any(m.convos.active.values()) and not m.arrivals:
                stretch["end"] = t * data.MINUTES_PER_TURN
                q.stretches.append(stretch)
                stretch = None
                if q.morning_end is None:
                    q.morning_end = t * data.MINUTES_PER_TURN
            continue
        if q.step(minute):
            first = next(e for e in q.log if e["minute"] == minute and e["fired"])
            stretch = {"start": minute, "end": None, "room": first["room"], "trigger": first["kind"]}
            continue
        nxt = q.next_event(minute)
        q.advance(minute, nxt)
        t = nxt // data.MINUTES_PER_TURN
    if stretch is not None:
        stretch["end"] = DAY_END
        q.stretches.append(stretch)
    q.bedtime()
    m.finish()
    return m


def gap_line(m, pid):
    """What took the place of the afternoon for pid (§3; Y8 of block A, and the bedtime prompt): their own spans
    after the morning, then whether anyone ate. data.GAP on a day that was not played to bedtime."""
    q = getattr(m, "quiet", None)
    if q is None:
        return data.GAP
    mine = []
    for s in sorted((s for s in q.spans if s["who"] == pid and s["end"] is not None), key=lambda s: s["start"]):
        if mine and (mine[-1]["routine"], mine[-1]["room"]) == (s["routine"], s["room"]):
            mine[-1] = {**mine[-1], "end": s["end"]}
        else:
            mine.append(s)
    parts = []
    for s in mine:
        when = f"({clock(s['start'])} to {clock(s['end'])})"
        room = data.ROOMS[s["room"]]
        if s["routine"] == "rest":
            parts.append(f"you lay on your bed in the {room} {when}")
        elif s["routine"] == "withdraw":
            parts.append(f"you kept to your own room, the {room} {when}")
        else:
            others = [NAMES[x] for x in data.ORDER if x in s["seen_start"]]
            company = (" with " + (others[0] if len(others) == 1 else ", ".join(others[:-1]) + " and " + others[-1])
                       if others else "")
            parts.append(f"you sat in the kitchen{company} {when}")
    after = q.morning_end or 0
    ate = any(a["option"] in ("eat", "eat_given", "share") and "empty" not in (a["came_of_it"] or "")
              for turn in m.transcript["turns"] if turn["minute"] >= after for a in turn["acts"])
    line = ("After the morning: " + "; ".join(parts) + ".") if parts else "After the morning: nothing changed."
    return line + ("" if ate else " Nobody ate.")
