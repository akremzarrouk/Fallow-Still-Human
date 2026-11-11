"""The code brain: what a person does, decided by code alone (Docs/fable-audit-2026-11.md, sections 7.2, 7.3 and 10).

Where the engine asked a model (world.Morning.ask_model, night.Night.ask) it asks this instead, when a run is given
one. For each option offered, the brain looks up the move's considerations in content/weights.json, adds them up from
facts about the person deciding, applies the day's mood tilt, leaves out what the once rules rule out, takes the best,
and lets the seed choose among moves within the band of the best. It returns the fields the engine took from the model
(`option`, `say`, `feeling`, `reason`, `suspects`, `angry_at`), with the three largest terms of the choice and the
day's mood beside them.

It reads only the person it decides for and a `context` of what that person can see, built with the World out of
reach (truth.prompting). It never reads who took the can, another person's inside, or anything not yet perceived.

From step 2 the brain also keeps the heart (heart.py): what each person remembers of the others, whom they suspect and
from what, and the one thing they mean to do. In code mode nothing a model would have answered moves a level: the
heart is fed by what each person perceives (`saw`, `notice`), and settled once a night (`night_step`).

No model is called anywhere here. CodeOracle stands where the Oracle stands and raises if anything asks.
"""
import json
import os
import random

import data
import truth
from heart import Heart
from talk import act_of
from world import NAMES, OWED_TURNS, day_index, hunger_level, strength

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
MOODS = ("on edge", "low", "warm", "restless")      # and "steady": no tilt
OWN_ROOM = {p: room for room, owners in data.OWNERS.items() for p in owners}
ROOMMATE = {p: q for owners in data.OWNERS.values() for p in owners for q in owners if q != p}
TRAITS = ("cautious", "dominant", "empathetic", "impulsive", "proud", "anxious", "honest")
NEVER_CAPPED = ("stay", "sleep", "plate_eat")
# The night's options, which carry no kind (night.py): reaction and answer ids, by what they are.
NIGHT_KEYS = {"stay_home": {"answer": "answer_stay", "reaction": "give_up_going"}}
BAD_NIGHT = {"lie_awake": (1, "a bad night"), "watch_door": (2, "a night on watch"),
             "go_next_door": (2, "a night out"), "go_further": (2, "a night out"),
             "get_up_and_look": (2, "a night waiting up")}
MEAL_KINDS = ("meal", "meal_small", "plate_eat", "plate_to", "plate_back")
TRIP_MOVES = ("propose", "volunteer", "object", "object_all", "back", "decline", "propose_far", "volunteer_far")


class LLMCalled(RuntimeError):
    """Something asked a model in code mode."""


class CodeOracle:
    """In code mode, what the engine holds where it held the Oracle: the brain, and nothing that can answer."""
    live = from_cache = api_requests = 0

    def __init__(self, brain):
        self.brain = brain
        self.prompt_tokens = []
        self.asked = 0

    def new_scene(self):
        pass

    def ask(self, *a, **k):
        self.asked += 1
        raise LLMCalled("a model was asked in code mode: the brain decides everything there")


def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


class CodeBrain:
    def __init__(self, seed, tilt=True, weights=None, lines=None):
        self.seed = seed
        self.tilt_on = tilt
        self.weights = weights or load("weights.json")
        self.lines = lines or load("lines.json")
        self.scenario = self.weights["scenario"]
        self.heart = Heart(self.weights["heart"])
        self.done = {}          # once keys -> how many times
        self.caused = {}        # (person, move, target) -> what stood when they last made that move (its cause)
        self.count = {}         # (person, day) -> option id -> how many times chosen
        self.calls = {}         # (person, day) -> how many decisions so far
        self.moods = {}         # (person, day) -> {"mood", "cause", "seeded", "points"}
        self.notes = {}         # (person, day) -> what happened to them that day: "accused", "comforted", "fed", ...
        self.heard_upto = {}    # (person, day) -> how much of their `heard` has been read
        self.room_seen = {}     # (person, day) -> (minute, who was in the room with them)
        self.last_question = {}  # (person, day) -> the minute they last heard the question or an accusation
        self.accused_seen = {}  # (person, day) -> other -> the place in `heard` where that other was accused
        self.last_night = {}    # person -> (day, what their night was: a bedtime option, or "get_up_and_look")
        self.woke = {}          # (person, day) -> the hunger level they woke at
        self.shelf = {}         # person -> the shelf's count as they last saw it or were told it
        self.outings = {}       # person -> how many goings-out at night they know of
        self.lapsed = {}        # person -> how many times they let go of meaning to go out
        self.told_empty = set()  # who has heard someone speak of going further: so next door is no use
        self.nights = {}        # night number -> the night step's record
        self.last_line = {}     # (person, line key) -> the variant last used
        self.spoken = set()     # every line said
        self.last_scores = {}   # of the latest choice: option id -> score, for the moves that were open
        self.last_keys = {}     # of the latest choice: option id -> the weight entry it was scored by

    # ---------- what the person can see ----------
    def context_of(self, m, p, t, opts, d=None):
        """The day's context for p, built as a prompt was: with the World out of reach."""
        with truth.prompting():
            return self._context(m, p, t, opts, d or {})

    def _context(self, m, p, t, opts, d):
        ids = {o.id for o in opts}
        ask = ("aside" if "accept_aside" in ids else "given" if "eat_given" in ids
               else "plate" if "plate_eat" in ids else "food" if d.get("food_moment") else "turn")
        others = []
        for q in m.others_here(p):
            level = hunger_level(q.hunger)
            others.append({"id": q.id, "activity": q.activity.get("kind"), "with": q.activity.get("with"),
                           "upset": strength(q.feeling) if (t is not None and m.shown(q, t)) else 0,
                           # Someone very hungry or worse looks it (section 10.2, the one added rule of perception).
                           "hungry": level if level >= 2 else 0})
        minute = None if t is None else t * data.MINUTES_PER_TURN
        if p.room == "kitchen" or minute == 0 or p.id not in self.shelf:    # they see the shelf, or were told the count
            self.shelf[p.id] = m.portions
        return {"seed": m.seed, "day": day_index(m.day), "house_day": m.day, "night": False, "ask": ask,
                "minute": minute, "room": p.room, "others": others,
                "partner": next((o.act["partner"] for o in opts if "partner" in o.act), None),
                "convo": sum(1 for _, r, what, _ in m.convos.log if r == p.room and what == "started"),
                "shelf": self.shelf[p.id], "home": len(data.ORDER) - len(m.away), "missing": sorted(m.away),
                "plate": getattr(m, "plates", {}).get(p.id), "meal_done": getattr(m, "meal_at", None) is not None}

    def night_context(self, seed, day, ask, p, where=None, leaver=None, shelf=None, missing=(), someone_up=False):
        """A night decision's context. shelf: what the bedtime line said the shelf holds (the last they saw, if not
        given). someone_up: someone else is already up and in the kitchen."""
        if shelf is not None:
            self.shelf[p.id] = shelf
        return {"seed": seed, "day": day, "house_day": day + 3, "night": True, "ask": ask, "minute": None,
                "room": where or OWN_ROOM[p.id], "others": [], "partner": None, "convo": 0, "leaver": leaver,
                "shelf": self.shelf.get(p.id, self.scenario["portions"]), "home": len(data.ORDER) - len(missing),
                "missing": sorted(missing), "plate": None, "someone_up": someone_up}

    # ---------- the two places the engine asks ----------
    def decide(self, m, p, t, opts, d, extra=None):
        return self.choose(p, opts, self.context_of(m, p, t, opts, d))

    def decide_night(self, n, p, kind, opts):
        leaver = next((o.id[len("stop_"):] for o in opts if o.id.startswith("stop_")), None)
        up = [q for q in data.ORDER if q != p.id and n.where.get(q) == "kitchen" and n.awake.get(q)
              and q not in n.dozed]
        with truth.prompting():
            ctx = self.night_context(n.day1.seed, day_index(n.day1.day), kind, p, n.where.get(p.id), leaver,
                                     shelf=n.portions, missing=n.away, someone_up=bool(up))
        choice = self.choose(p, opts, ctx)
        if kind == "reaction" and choice["option"] == "get_up_and_look":
            self.last_night[p.id] = (ctx["day"], "get_up_and_look")
        return choice

    def new_day(self, m):
        """A new morning has been set up (world.Morning.next_day): what the brain's people carry into it that the
        engine works out afresh each day."""
        for q in self.told_empty:
            if q not in m.away:
                m.people[q].knows_empty = True

    # ---------- what a person perceives of an act (world.Morning.apply, in code mode) ----------
    def saw(self, m, p, kind, target, seen, partner=None):
        """p has just done `kind` (aimed at `target`, a person id or None) in front of `seen` (person ids). Each of
        them now remembers it, by what it was to them. Only those in the room are told: this is perception."""
        day = day_index(m.day)
        h = self.heart
        people = m.people

        def note(pid, what):
            self.notes.setdefault((pid, day), set()).add(what)
        if kind == "accuse" and target in seen and people[target].guilt is None:
            h.remember(target, p.id, "accused_falsely", day)
            note(target, "quarrel")
        elif kind == "confront" and target in seen:
            h.remember(target, p.id, "confronted", day)
            note(target, "quarrel")
        elif kind == "reassure" and target in seen:
            h.remember(target, p.id, "reassured", day)
            note(target, "comforted")
        elif kind == "sit" and target in seen:
            h.remember(target, p.id, "sat_with", day)
            note(target, "comforted")
        elif kind == "share":
            for q in seen:
                h.remember(q, p.id, "shared_food", day)
        elif kind == "eat":
            for q in seen:
                if hunger_level(people[q].hunger) >= 1:
                    h.remember(q, p.id, "ate_in_front", day)
        elif kind == "eat_given" and partner is not None:
            h.remember(p.id, partner, "gave_share", day)
            note(p.id, "fed")
        elif kind == "plate_to" and target is not None:
            h.remember(target, p.id, "gave_share", day)
            note(target, "fed")
        elif kind == "plate_back":
            for q in seen:
                h.clue(q, p.id, "refused_share", day)
        elif kind == "confess":
            for q in seen:
                h.remember(q, p.id, "lied" if p.id in people[q].denials_heard else "owned_up", day)
        elif kind == "object" and target in seen:
            note(target, "refused")
        elif kind in ("volunteer_far", "propose_far"):
            # Whoever hears someone speak of the houses further along concludes that next door is no use.
            for q in seen:
                self.told_empty.add(q)
                people[q].knows_empty = True

    # ---------- facts about the person deciding ----------
    def facts(self, p, ctx):
        """Numbers from 0 to 1 (a few run below 0) about p's own state and what p sees. Nothing else is weighed."""
        f = {t: p.sheet["traits"][t] for t in TRAITS}
        others = ctx["others"]
        level = hunger_level(p.hunger)
        owed = p.owed
        if owed is not None and (owed["room"] != p.room or (
                ctx["minute"] is not None and ctx["minute"] // data.MINUTES_PER_TURN > owed["turn"] + OWED_TURNS)):
            owed = None
        owed_kind = None
        if owed is not None:
            owed_kind = next((h["kind"] for h in reversed(p.heard)
                              if h["who"] == owed["who"] and h["target"] == p.id), None)
        own = p.trip_heard.get(p.id)
        needs = p.needs or {}
        # A denial answers something: the question, or an accusation of them, heard since they last denied.
        put_to_them = max((h["seq"] for h in p.heard
                           if h["kind"] == "ask" or (h["kind"] == "accuse" and h["target"] == p.id)), default=-1)
        denied = max((x["seq"] for x in p.history if x["kind"] == "deny"), default=-1)
        hungriest = max([level] + [o["hungry"] for o in others])
        notes = self.notes.get((p.id, ctx["day"]), set())
        offered = bool(own) and own[1] == "volunteer"
        # Whoever asked the question is still waiting while someone here has not answered it.
        asked = max((x["seq"] for x in p.history if x["kind"] == "ask"), default=None)
        answered = {h["who"] for h in p.heard if asked is not None and h["seq"] > asked
                    and h["kind"] in ("deny", "confess", "accuse")}
        turn = None if ctx["minute"] is None else ctx["minute"] // data.MINUTES_PER_TURN
        asked_at = max((x["t"] for x in p.history if x["kind"] == "ask"), default=None)
        awaiting = (asked is not None and turn is not None and turn - asked_at <= OWED_TURNS
                    and any(o["id"] not in answered for o in others))
        f.update({
            "anxious_over_half": f["anxious"] - 0.5, "empathetic_over_half": f["empathetic"] - 0.5,
            "boldness": min(1.0, max(f["impulsive"] / 0.6, f["dominant"] / 0.8)),
            "h": level / 3, "starving": float(level == 3),
            "H": hungriest / 3, "H_past_hungry": max(0, hungriest - 1) / 2,
            "question_open": float(put_to_them > denied),
            "took_it": float(p.guilt is not None), "g": (p.guilt or 0) / 3,
            "others_here": float(bool(others)), "alone_with_one": float(len(others) == 1),
            "listening": len(others) / 3,
            "upset_share": (sum(1 for o in others if o["upset"]) / len(others)) if others else 0.0,
            "heard_question": float(p.heard_question), "not_asked": float(not p.heard_question),
            "counted": float(any("Elena counts the pantry" in line and "(you did it)" in line for line in p.sure)),
            "owes_nobody": float(owed is None), "owes_accusation": float(owed_kind == "accuse"),
            "accused_publicly": float(owed_kind == "accuse" and len(others) >= 2),
            "offered_today": float(offered),
            "means_to_go": float((offered or self.heart.intends(p.id, "go_out")) and not p.knows_empty),
            "knows_empty": float(bool(p.knows_empty)), "awaiting_answers": float(awaiting),
            "meal_due": float(not ctx["night"] and ctx["shelf"] > 0 and not ctx.get("meal_done")),
            # Someone did not come back, last night or the night before: the house is grieving.
            "grief": float(any(isinstance(x, tuple) and x[0] == "lost"
                               for d in (1, 2) for x in self.notes.get((p.id, ctx["day"] - d), ()))),
            # The can is a live subject on a day it was asked about or someone was accused of it.
            "can_alive": float(any(h["kind"] in ("ask", "accuse") for h in p.heard)
                               or any(x["kind"] in ("ask", "accuse") for x in p.history)),
            "ate_today": float(p.eaten > 0),
            "means_far": float((bool(own) and own[1] == "volunteer_far") or self.heart.intends(p.id, "go_far")),
            "intends_watch": float(self.heart.intends(p.id, "watch")),
            "someone_offered": float(any(v[1] == "volunteer" for w, v in p.trip_heard.items() if w != p.id)),
            "someone_means_to_go": float(any(v[1] in ("volunteer", "volunteer_far")
                                             for w, v in p.trip_heard.items() if w != p.id)),
            "named_to_go": float(any(v[1:3] == ("back", p.id) for w, v in p.trip_heard.items() if w != p.id)),
            "weak": float(needs.get("fast_stage", 0) >= 3), "debt_stage": float(needs.get("debt_stage", 0)),
            "knock_today": float("knock" in notes),
            "shelf_empty": float(ctx["shelf"] <= 0), "food_short": float(ctx["shelf"] < 2 * ctx["home"]),
            "someone_up": float(bool(ctx.get("someone_up"))),
        })
        f["_owed"] = owed
        f["_owed_kind"] = owed_kind
        f["_level"] = level
        return f

    def temper(self, pid, day):
        """What temperament adds to a person's suspicion of another (weights.json, heart.temper)."""
        t = self.weights["heart"].get("temper", {}).get(pid, {})
        if t.get("suspects_resented"):
            return lambda other: t["suspects_resented"] if self.heart.trust(pid, other, day) <= -1 else 0
        return None

    def target_facts(self, p, ctx, o, target, f):
        """The facts that depend on whom or where the move is aimed."""
        other = next((x for x in ctx["others"] if x["id"] == target), None)
        owed, kind = f["_owed"], f["_owed_kind"]
        person = target in data.PEOPLE
        pos = p.trip_heard.get(target) if person else None
        day = ctx["day"]
        out = {
            "k_target": (p.grudges[target].strength / 3) if target in p.grudges else 0.0,
            "k_partner": (p.grudges[ctx["partner"]].strength / 3) if ctx.get("partner") in p.grudges else 0.0,
            "u_target": (other["upset"] / 3) if other else 0.0,
            "target_offered": float(bool(pos) and pos[1] in ("volunteer", "volunteer_far")),
            "owes_target_line": float(owed is not None and owed["who"] == target
                                      and kind in ("confront", "reassure", "say")),
            "to_own_room": float(o.act.get("kind") == "go" and o.act.get("to") == OWN_ROOM.get(p.id)),
            "target_accused_by_other": float(any(h["kind"] == "accuse" and h["target"] == target
                                                 and h["who"] != p.id for h in p.heard)),
            "s_target": 0.0, "kind_target": 0.0, "hurt_target": 0.0, "intends_tell_target": 0.0,
            "hungrier_target": 0.0, "_says": {},
        }
        if person:
            also = self.temper(p.id, day)
            points = self.heart.suspicion(p.id, target, day)
            trust = self.heart.trust(p.id, target, day)
            out.update({
                "s_target": min(3, points + (also(target) if points and also else 0)) / 3,
                "kind_target": max(0.0, trust) / 3, "hurt_target": max(0.0, -trust) / 3,
                "intends_tell_target": float(self.heart.intends(p.id, "tell", target)),
                "hungrier_target": max(0, (other["hungry"] if other else 0) - f["_level"]) / 3})
            for name, sign in (("kind_target", 1), ("hurt_target", -1)):
                said = self.heart.behind(p.id, target, day, sign)
                if said:
                    out["_says"][name] = said
        return out

    # ---------- what reached them since they last decided ----------
    def notice(self, p, opts, ctx):
        """Reads the lines p has heard since the brain last looked, and who has left the room: what was done to
        them today (for tomorrow's mood), and the evidence of their own eyes (for their suspicion)."""
        day = ctx["day"]
        key = (p.id, day)
        notes = self.notes.setdefault(key, set())
        accused = self.accused_seen.setdefault(key, {})
        upto = self.heard_upto.get(key, 0)
        for i, h in enumerate(p.heard[upto:], start=upto):
            if h["kind"] == "accuse" and h["target"] == p.id:
                notes.add("accused")
            if h["kind"] == "reassure" and h["target"] == p.id:
                notes.add("comforted")
            if h["kind"] in ("ask", "accuse") and ctx["minute"] is not None:
                self.last_question[key] = ctx["minute"]
            if h["kind"] == "accuse":
                # Someone who accuses another straight after being accused themselves.
                if h["who"] in accused and i - accused[h["who"]] <= 2 and h["who"] != p.id:
                    self.heart.clue(p.id, h["who"], "accused_back", day)
                    del accused[h["who"]]
                if h["target"] and h["target"] != p.id:
                    accused[h["target"]] = i
        self.heard_upto[key] = len(p.heard)
        if any(o["activity"] == "sitting" and o["with"] == p.id for o in ctx["others"]):
            notes.add("comforted")
        if any(o.id.startswith("door_") for o in opts):
            notes.add("knock")
        if ctx["minute"] is not None and not ctx["night"]:
            here = {o["id"] for o in ctx["others"]}
            before = self.room_seen.get(key)
            asked = self.last_question.get(key)
            if before is not None and asked is not None and ctx["minute"] - asked <= 2 * data.MINUTES_PER_TURN:
                # Someone who left the room within two turns of the question or an accusation.
                for q in before[1] - here:
                    if ("left", q) not in notes:
                        notes.add(("left", q))
                        self.heart.clue(p.id, q, "left_at_question", day)
            self.room_seen[key] = (ctx["minute"], here)

    # ---------- the day's mood (section 7.2) ----------
    def set_mood(self, pid, day, mood, cause=None):
        """For tests: p's mood on that day, as given."""
        self.moods[(pid, day)] = {"mood": mood, "cause": cause, "seeded": False, "points": {}}

    def mood_of(self, p, ctx):
        """p's mood on this day: set once, when they first decide. Mostly from causes (last night's sleep, hunger on
        the morning it is new or worse, yesterday), plus a small seeded part; the mood with the most points wins, one
        with a cause beats one without, and no points is steady. Long hunger limits what is possible: after two
        mornings of it the seeded part cannot make anyone warm."""
        day = ctx["day"]
        key = (p.id, day)
        if key in self.moods:
            return self.moods[key]
        t = p.sheet["traits"]
        points = {m: 0 for m in MOODS}
        causes = {m: [] for m in MOODS}

        def add(mood, n, cause):
            points[mood] += n
            causes[mood].append(cause)
        night = self.last_night.get(p.id)
        if night and night[0] == day - 1 and night[1] in BAD_NIGHT:
            n, cause = BAD_NIGHT[night[1]]
            add("on edge" if t["anxious"] >= 0.6 and not cause == "a night out" else "low", n, cause)
        # Hunger colours the morning it is new or worse than the morning before. Hunger that has only gone on is
        # no news to the person: it still weighs in every decision (the hunger terms), but it does not name the day.
        level = hunger_level(p.hunger)
        self.woke[key] = level
        before = self.woke.get((p.id, day - 1), 0)
        if level >= 2 and level > before:
            add("on edge" if t["impulsive"] >= 0.6 else "low", 1, "hunger")
        yesterday = self.notes.get((p.id, day - 1), set())
        if "accused" in yesterday:
            add("low" if p.guilt is not None else "on edge", 2, "being accused yesterday")
        elif "quarrel" in yesterday or "refused" in yesterday:
            add("on edge", 1, "yesterday's quarrel")
        if "comforted" in yesterday:
            add("warm", 1, "yesterday's kindness")
        if "fed" in yesterday:
            add("warm", 1, "being given food")
        # Someone who did not come back colours more than one morning: the first two after it, the first hardest.
        for back, n in ((1, 3), (2, 2)):
            lost = sorted(x[1] for x in self.notes.get((p.id, day - back), ()) if isinstance(x, tuple) and x[0] == "lost")
            if lost:
                add("low", n, f"{data._and([NAMES[x] for x in lost])} not coming back")
                break
        long_hunger = level >= 2 and before >= 2
        rng = random.Random(f"{self.seed}:mood:{day}:{p.id}")
        seeded = rng.choice(MOODS) if rng.random() < 0.5 else None
        if seeded == "warm" and long_hunger:
            seeded = None                   # nobody wakes warm after days without food unless something gave a reason
        if seeded:
            points[seeded] += 1
        top = max(points.values())
        if top == 0:
            mood = "steady"
        else:
            best = [m for m in MOODS if points[m] == top]
            caused = [m for m in best if causes[m]]
            mood = rng.choice(caused or best) if len(caused or best) > 1 else (caused or best)[0]
        cause = " and ".join(causes[mood]) if mood != "steady" and causes[mood] else None
        self.moods[key] = {"mood": mood, "cause": cause, "seeded": bool(seeded and seeded == mood),
                           "points": {m: n for m, n in points.items() if n}}
        return self.moods[key]

    def moods_json(self):
        out = {}
        for (pid, day), m in sorted(self.moods.items(), key=lambda kv: (kv[0][1], data.ORDER.index(kv[0][0]))):
            out.setdefault(str(day), {})[pid] = m
        return out

    def tilt(self, mood, key, o, flags):
        """At most the tilt, up or down: a mood makes a few moves a little likelier and a few a little less."""
        spec = self.weights["moods"].get(mood)
        if not self.tilt_on or spec is None:
            return 0.0

        def fits(entries):
            for e in entries:
                name, _, flag = e.partition(":")
                if name == key and (not flag or flags.get(flag)):
                    return True
            return False
        if fits(spec["more"]):
            return self.weights["tilt"]
        if fits(spec["less"]) or ("speech" in spec["less"] and o.speech):
            return -self.weights["tilt"]
        return 0.0

    # ---------- scoring ----------
    @staticmethod
    def stay_option(p, ids):
        """Staying as they are (world.Morning.routine): carrying on a search or a sitting, else silent."""
        if p.activity.get("kind") == "searching" and "keep_searching" in ids:
            return "keep_searching"
        if p.activity.get("kind") == "sitting" and f"sit_{p.activity.get('with')}" in ids:
            return f"sit_{p.activity['with']}"
        return "silent" if "silent" in ids else None

    @staticmethod
    def key_of(o, ctx):
        """(the weight entry's name, whom or where the move is aimed)."""
        if ctx["night"]:
            for prefix, key in (("stop_", "stop"), ("let_", "let_go"), ("go_with_", "go_with")):
                if o.id.startswith(prefix):
                    return key, ctx.get("leaver")
            return NIGHT_KEYS.get(o.id, {}).get(ctx["ask"], o.id), None
        if o.act.get("kind") in MEAL_KINDS:
            return o.act["kind"], o.act.get("target")
        kind, target = act_of(o.id)
        if kind == "reassure" and target is None:
            return "reassure_all", None
        if kind == "say":
            return ("say_to" if target else "say_other"), target
        if kind == "object" and target is None:
            return "object_all", None
        if kind == "sit":
            target = o.act.get("target")
        return kind, target

    def rule_for(self, key, flags):
        for i, rule in enumerate(self.weights["moves"].get(key, ())):
            if all(self.holds(w, flags) for w in rule.get("when", ())):
                return rule, i
        return None, None

    @staticmethod
    def holds(when, flags):
        return not flags.get(when[1:]) if when.startswith("!") else bool(flags.get(when))

    def weigh(self, rule, flags):
        """(score, [(what, how much)]) of one rule for these facts."""
        terms = []
        if rule.get("base"):
            terms.append(("base", rule["base"]))
        for w, *names in rule.get("terms", ()):
            v = w
            for n in names:
                v *= flags.get(n, 0.0)
            if v:
                terms.append((", ".join(names), v))
        return sum(v for _, v in terms), terms

    def once_key(self, rule, i, key, pid, target, flags, ctx):
        once = rule.get("once")
        if not once or once == "cause":
            return None
        name = rule.get("once_key") or f"{key}#{i}"
        if once == "week":
            return (pid, name)
        if once == "accuser":
            return (pid, ctx["day"], name, (flags["_owed"] or {}).get("who"))
        if once == "convo":
            return (pid, ctx["day"], name, ctx["convo"])
        return (pid, ctx["day"], name) if rule.get("once_key") else (pid, ctx["day"], name, target)

    # ---------- once is enough, for the whole week: a repeat needs a new cause (section 7.3) ----------
    def cause_of(self, subject, p, ctx, target, flags):
        """What stands, as p perceives it, behind a move on this subject. A move made once is open again only when
        this has changed since: that change is its new cause."""
        if subject == "trip":
            worst = max([flags["_level"]] + [o["hungry"] for o in ctx["others"]])
            # "Short" covers an empty shelf too: a few portions brought home and eaten do not make the trip new.
            return {"shelf": "short" if flags["food_short"] else "enough",
                    "hunger": "starving" if flags["shelf_empty"] and worst >= 3 else "",
                    "next_door": "empty" if p.knows_empty else "unknown",
                    "resolve": self.lapsed.get(p.id, 0), "away": ", ".join(NAMES[x] for x in ctx["missing"])}
        if subject == "leaving":       # telling someone not to go out: said once, unless someone has since been lost
            return {"away": ", ".join(NAMES[x] for x in ctx["missing"])}
        if subject == "can":
            return {"clues": self.heart.clue_count(p.id, target) if target in data.PEOPLE else 0,
                    "known": bool(p.knows_culprit)}
        return {}

    def cause_key(self, rule, key, pid, target):
        name = rule.get("once_key") or key
        return (pid, name, None if rule.get("once_key") else target)

    def new_cause(self, rule, key, p, ctx, target, flags):
        """(open?, the cause as it stands, what is new in words or None). Open the first time; after that only if
        something in the cause has changed."""
        now = self.cause_of(rule["subject"], p, ctx, target, flags)
        was = self.caused.get(self.cause_key(rule, key, p.id, target))
        if was is None:
            return True, now, None
        words = self.weights.get("causes", {})
        for k, v in now.items():
            if was.get(k) != v:
                said = words.get(f"{k}:{v}") or words.get(k, k.replace("_", " ") + " changed")
                return True, now, said.format(value=v)
        return False, now, None

    def choose(self, p, opts, ctx):
        """The decision: every offered move scored, the best open one taken."""
        pid, day = p.id, ctx["day"]
        self.notice(p, opts, ctx)
        mood = self.mood_of(p, ctx)
        base = self.facts(p, ctx)
        ids = {o.id for o in opts}
        stay = self.stay_option(p, ids)
        counts = self.count.setdefault((pid, day), {})
        rows, self.last_keys = [], {}
        for o in opts:
            key, target = self.key_of(o, ctx)
            flags = dict(base)
            flags.update(self.target_facts(p, ctx, o, target, base))
            cause = new = None
            if o.id == stay:
                key, rule, i = "stay", None, None
                score, terms = self.weights["stay"], [("base", self.weights["stay"])]
            else:
                rule, i = self.rule_for(key, flags)
                if rule is None:
                    score, terms = self.weights["default"], [("base", self.weights["default"])]
                else:
                    score, terms = self.weigh(rule, flags)
            for q in self.weights.get("quirks", ()):
                if q["who"] == pid and q["move"] == key and all(self.holds(w, flags) for w in q.get("when", ())):
                    score += q["add"]
                    terms.append((q["says"], q["add"]))
            tilt = self.tilt(mood["mood"], key, o, flags)
            once = self.once_key(rule, i, key, pid, target, flags, ctx) if rule else None
            is_open = (key in NEVER_CAPPED
                       or (counts.get(o.id, 0) < self.weights["cap_per_day"]
                           and (once is None or self.done.get(once, 0) < rule.get("limit", 1))))
            if rule is not None and rule.get("once") == "cause":
                fresh, cause, new = self.new_cause(rule, key, p, ctx, target, flags)
                is_open = is_open and fresh
            self.last_keys[o.id] = key if rule is not None or key == "stay" else f"{key} (default)"
            rows.append({"o": o, "key": key, "target": target, "score": score + tilt, "terms": terms, "tilt": tilt,
                         "once": once, "open": is_open, "rule": rule, "cause": cause, "new": new,
                         "says": flags["_says"]})
        open_rows = [r for r in rows if r["open"]] or rows     # a list with nothing open (it has no "stay") is free
        self.last_scores = {r["o"].id: r["score"] for r in open_rows}
        best = max(r["score"] for r in open_rows)
        band = sorted((r for r in open_rows if r["score"] >= best - self.weights["band"] - 1e-9),
                      key=lambda r: r["o"].id)
        n = self.calls[(pid, day)] = self.calls.get((pid, day), 0) + 1
        top_row = max(open_rows, key=lambda r: r["score"])
        if top_row["key"] == "stay":
            band = [top_row]            # staying as they are wins unless something outweighs it: no draw against it
        if len(band) > 1:
            rng = random.Random(f"{self.seed}:tie:{day}:{ctx['minute']}:{pid}:{ctx['ask']}:{n}")
            row = rng.choice(band)
        else:
            row = band[0]
        o = row["o"]
        counts[o.id] = counts.get(o.id, 0) + 1
        if row["once"] is not None:
            self.done[row["once"]] = self.done.get(row["once"], 0) + 1
        if row["cause"] is not None:
            self.caused[self.cause_key(row["rule"], row["key"], pid, row["target"])] = row["cause"]
        if ctx["ask"] == "bedtime":
            self.last_night[pid] = (day, o.id)
        self.intend(p, row, base, ctx)
        second = max((r["score"] for r in open_rows if r is not row), default=None)
        top = sorted(row["terms"], key=lambda kv: -abs(kv[1]))[:3]
        words = self.weights.get("words", {})

        def said(name):
            return ", ".join(row["says"].get(x) or words.get(x, x.replace("_", " ")) for x in name.split(", "))
        why = {"terms": [[said(name), round(v, 3)] for name, v in top], "score": round(row["score"], 3),
               "lead": None if second is None else round(row["score"] - second, 3), "tilt": row["tilt"],
               "among": [r["o"].id for r in band] if len(band) > 1 else None}
        if row["new"]:
            why["new_cause"] = row["new"]
        reason = "; ".join(f"{name} {v:+.2f}" for name, v in why["terms"]) or "nothing weighed more"
        suspect = self.heart.suspect(pid, day, self.temper(pid, day))
        return {"option": o.id, "say": self.line(p, row["key"], row["target"], ctx, o) if o.speech else None,
                "feeling": self.feeling(p, row["key"], base, mood, ctx), "reason": reason, "dropped_line": False,
                "suspects": NAMES[suspect[0]] if suspect[1] >= 1 else "nobody", "angry_at": "nobody", "why": why,
                "mood": {"mood": mood["mood"], "cause": mood["cause"]}}

    # ---------- intentions (section 7.2) ----------
    def intend(self, p, row, f, ctx):
        """What a choice, or the lack of one, makes them mean to do."""
        key, day, h = row["key"], ctx["day"], self.heart
        if key == "volunteer":
            h.intend(p.id, "go_out", None, "the food is short", day)
        elif key == "volunteer_far":
            h.intend(p.id, "go_far", None, "next door is empty", day)
        elif key == "decline" and (h.intends(p.id, "go_out") or h.intends(p.id, "go_far")):
            h.settle(p.id, day, gone="they said they would not go")
        elif (f["took_it"] and f["g"] >= 2 / 3 - 1e-9 and not p.confessed and not ctx["night"]
              and len(ctx["others"]) >= 2 and key != "confess" and p.id not in h.intents):
            # It is on them, and there are too many listening: they mean to tell one person, alone.
            here = {o["id"] for o in ctx["others"]}
            for q in self.weights["heart"].get("confidant", {}).get(p.id, ()):
                if q in here and h.trust(p.id, q, day) > -1:
                    h.intend(p.id, "tell", q, "what is on them", day)
                    break

    # ---------- in code mode an answer moves no level: the heart does (world.Morning.ask_model) ----------
    def settle(self, p, day, d=None):
        """p's suspicion as the engine shows it, set from the heart's clues. Grudges are not touched here: they rise
        with what was done to them (world.add_grudge) and settle once a night (night_step)."""
        who, points = self.heart.suspect(p.id, day, self.temper(p.id, day))
        before = p.suspicion.state()
        p.suspicion.target, p.suspicion.strength = (who, min(3, points)) if points >= 1 else (None, 0)
        if d is not None:
            now = p.suspicion.state()
            d["suspects_result"] = ("same" if now == before else "rose" if now[1] > before[1] or now[0] != before[0]
                                    else "fell")
            d["suspects_now"] = p.suspicion.short("suspicion")
            kept = [f"{NAMES[t]} {g.strength}/3" for t, g in p.grudges.items() if g.strength]
            d["grudge_note"] = ("kept: " + ", ".join(kept)) if kept else "no grudges"

    # ---------- the night step (section 7.2): once a night, for everyone at home ----------
    def night_step(self, n):
        """Run after a night (mind.NightMind.run, in code mode), on the people as the night left them. Trust fades by
        the calendar (heart.Heart.weight_now), so there is nothing to do for it but record it. Grudges nobody renewed
        today drop a step; a mark holds one at 1. Intentions are renewed while their cause stands, and dropped, with a
        line for the diary, when done, impossible, pointless or out of date. What the night did to each person is
        kept for tomorrow's mood. Returns the record."""
        day = day_index(n.day1.day)
        h = self.heart
        present = [q for q in data.ORDER if q not in n.away]
        rec = {"night": n.number, "day": day, "grudges": [], "intentions": [], "lines": [], "remembered": []}
        mark = len(h.log)
        # What the night showed each of them.
        for g in n.groups:
            back = [x for x in g["members"] if x != g["lost"]]
            for L in g["members"]:
                self.outings[L] = self.outings.get(L, 0) + 1
            for P in present:
                if P in g["members"]:
                    continue
                known = [x for x in g["members"] if x in n.knows[P]]
                if not known:
                    continue
                self.outings[P] = self.outings.get(P, 0) + 1
                own = n.people[P].trip_heard.get(P)
                for L in known:
                    if own and own[1] == "object" and own[2] in (None, L):
                        h.remember(P, L, "defied", day)
                    if g["took"] and L in back:
                        h.remember(P, L, "brought_food", day)
                        self.notes.setdefault((P, day), set()).add("fed")
            if g["lost"]:
                for P in present:
                    self.notes.setdefault((P, day), set()).add(("lost", g["lost"]))
        # Grudges settle.
        for P in present:
            p = n.people[P]
            for t, gr in p.grudges.items():
                if not gr.strength:
                    continue
                renewed = any(len(e) == 3 for e in gr.events)       # an event of the day that has just ended
                floor = 1 if any(a["mark"] and a["w"] < 0 for a in h.acts.get((P, t), ())) else 0
                if not renewed and gr.strength > floor:
                    gr.strength -= 1
                    rec["grudges"].append({"who": P, "against": t, "now": gr.strength, "why": "nobody renewed it today"})
        # Intentions: done, dropped or renewed; and whoever knows someone went out may mean to watch for them.
        for P in present:
            p = n.people[P]
            i = h.intents.get(P)
            if i is not None:
                done, gone = False, None
                weak = (p.needs or {}).get("fast_stage", 0) >= 3
                if i["kind"] in ("go_out", "go_far"):
                    # Going once does not settle it: they mean to go until there is food, or they cannot, or the
                    # place is known to be empty, or the days go by.
                    visit = n.visit.get(P) or {}
                    if n.portions >= 2 * len(present):
                        done, gone = P in n.leavers, "there is food on the shelf"
                    elif weak:
                        gone = "too weak to go"
                    elif i["kind"] == "go_out" and visit.get("got_in") and not visit["found"] - visit["took"]:
                        gone = "next door is empty"
                    elif any(P in g["shaken"] for g in n.groups):
                        gone = "it nearly went wrong out there"     # a scare: nobody goes straight back out
                elif i["kind"] == "tell":
                    done = p.confessed
                    if i["target"] in n.away:
                        gone = f"{NAMES[i['target']]} is not there to tell"
                    elif (p.guilt or 0) < 2:
                        gone = "it weighs less now"
                elif i["kind"] == "watch":
                    if i["target"] in n.leavers and i["target"] not in n.away:
                        i["until"] = day + 2            # they went out again: the cause is as new as tonight
                    if i["target"] in n.away:
                        gone = f"{NAMES[i['target']]} did not come back"
                    elif i["target"] not in n.leavers and n.choices.get(P) == "watch_door":
                        done = True                 # they watched, and nobody went
                how, line = h.settle(P, day, done=done, gone=gone)
                if how == "dropped" and i["kind"] in ("go_out", "go_far") and gone is None:
                    self.lapsed[P] = self.lapsed.get(P, 0) + 1     # the days went by: deciding again is open to them
                rec["intentions"].append({"who": P, "kind": i["kind"], "target": i["target"], "what": how})
                if line:
                    rec["lines"].append(line)
            if P not in h.intents and P not in n.leavers:
                gone_out = [x for x in n.leavers if x in n.knows[P] and x not in n.away]
                cares = p.sheet["traits"]["empathetic"] >= self.weights["heart"]["watch_from"]
                if gone_out and cares and h.trust(P, gone_out[0], day) > -1:
                    if h.intend(P, "watch", gone_out[0], f"{NAMES[gone_out[0]]} went out in the night", day, days=2):
                        rec["intentions"].append({"who": P, "kind": "watch", "target": gone_out[0], "what": "formed"})
        for P in present:
            self.settle(n.people[P], day + 1)
        rec["remembered"] = h.log[mark:]
        rec["heart"] = h.state(day + 1)
        self.nights[n.number] = rec
        return rec

    # ---------- what goes with the choice ----------
    def feeling(self, p, key, f, mood, ctx):
        """Set by code from the move and the state (section 10.2). "hurt" and "scared" reach the face; the rest stay
        inside (world.SHOWN)."""
        if f["owes_accusation"] and not f["took_it"]:
            return "hurt"
        if f["took_it"] and key == "confess":
            return "ashamed"
        if f["took_it"] and (f["owes_accusation"] or key == "deny"):
            return "tense"
        asked = self.last_question.get((p.id, ctx["day"]))
        if (f["anxious"] >= 0.8 and "accused" not in self.notes.get((p.id, ctx["day"]), set()) and asked is not None
                and ctx["minute"] is not None and ctx["minute"] - asked <= data.MINUTES_PER_TURN
                and any(h["kind"] == "accuse" for h in p.heard[-3:])):
            return "scared"
        return "calm" if mood["mood"] == "steady" else mood["mood"]

    def line(self, p, key, target, ctx, o=None):
        """Words for a spoken move, from content/lines.json: the speaker's own where there are any, never the variant
        they used last. An option's own id is looked up before its kind (`still_going` before `volunteer`)."""
        mine, default = self.lines.get("by_person", {}).get(p.id, {}), self.lines["default"]
        oid = o.id if o is not None else None
        table = mine.get(oid) or default.get(oid) or mine.get(key) or default.get(key)
        slots = {}
        if target in data.PEOPLE:
            call = data.ADDRESS[p.id].get(target, NAMES[target])
            slots = {"to": call, "leaver": call}
        usable = [v for v in (table or ()) if all(("{" + s + "}") not in v or s in slots for s in ("to", "leaver"))]
        if not usable:
            usable = self.lines["default"]["any"]
        n = self.calls.get((p.id, ctx["day"]), 0)
        i = random.Random(f"{self.seed}:line:{ctx['day']}:{p.id}:{key}:{n}").randrange(len(usable))
        if len(usable) > 1 and self.last_line.get((p.id, key)) == i:
            i = (i + 1) % len(usable)
        self.last_line[(p.id, key)] = i
        text = usable[i].format(**slots) if slots else usable[i]
        self.spoken.add(text)
        return text
