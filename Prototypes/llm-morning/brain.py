"""The code brain: what a person does, decided by code alone (Docs/fable-audit-2026-11.md, sections 7.2, 7.3 and 10).

Where the engine asked a model (world.Morning.ask_model, night.Night.ask) it asks this instead, when a run is given
one. For each option offered, the brain looks up the move's considerations in content/weights.json, adds them up from
facts about the person deciding, applies the day's mood tilt, leaves out what the once-a-day rule rules out, takes the
best, and lets the seed choose among moves within the band of the best. It returns the fields the engine took from the
model (`option`, `say`, `feeling`, `reason`, `suspects`, `angry_at`), with the three largest terms of the choice and
the day's mood beside them.

It reads only the person it decides for and a `context` of what that person can see, built with the World out of
reach (truth.prompting). It never reads who took the can, another person's inside, or anything not yet perceived.

No model is called anywhere here. CodeOracle stands where the Oracle stands and raises if anything asks.
"""
import json
import os
import random

import data
import truth
from talk import act_of
from world import NAMES, OWED_TURNS, day_index, hunger_level, strength

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
MOODS = ("on edge", "low", "warm", "restless")      # and "steady": no tilt
OWN_ROOM = {p: room for room, owners in data.OWNERS.items() for p in owners}
TRAITS = ("cautious", "dominant", "empathetic", "impulsive", "proud", "anxious", "honest")
NEVER_CAPPED = ("stay", "sleep")
# The night's options, which carry no kind (night.py): reaction and answer ids, by what they are.
NIGHT_KEYS = {"stay_home": {"answer": "answer_stay", "reaction": "give_up_going"}}
BAD_NIGHT = {"lie_awake": (1, "a bad night"), "watch_door": (2, "a night on watch"),
             "go_next_door": (2, "a night out"), "go_further": (2, "a night out")}


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
        self.done = {}          # once keys -> how many times
        self.count = {}         # (person, day) -> option id -> how many times chosen
        self.calls = {}         # (person, day) -> how many decisions so far
        self.moods = {}         # (person, day) -> {"mood", "cause", "seeded", "points"}
        self.notes = {}         # (person, day) -> what happened to them that day: "accused", "comforted", "knock"
        self.heard_upto = {}    # (person, day) -> how much of their `heard` has been read
        self.evidence = {}      # (person, day) -> other -> points against them, each from something perceived
        self.room_seen = {}     # (person, day) -> (minute, who was in the room with them)
        self.last_question = {}  # (person, day) -> the minute they last heard the question or an accusation
        self.accused_seen = {}  # (person, day) -> other -> the place in `heard` where that other was accused
        self.told_anger = set()  # (person, accuser, day, minute): accusations already answered with anger
        self.last_night = {}    # person -> (day, bedtime option)
        self.woke = {}          # (person, day) -> the hunger level they woke at
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
               else "food" if d.get("food_moment") else "turn")
        others = []
        for q in m.others_here(p):
            level = hunger_level(q.hunger)
            others.append({"id": q.id, "activity": q.activity.get("kind"), "with": q.activity.get("with"),
                           "upset": strength(q.feeling) if (t is not None and m.shown(q, t)) else 0,
                           # Someone very hungry or worse looks it (section 10.2, the one added rule of perception).
                           "hungry": level if level >= 2 else 0})
        return {"seed": m.seed, "day": day_index(m.day), "house_day": m.day, "night": False, "ask": ask,
                "minute": None if t is None else t * data.MINUTES_PER_TURN, "room": p.room, "others": others,
                "partner": next((o.act["partner"] for o in opts if "partner" in o.act), None),
                "convo": sum(1 for _, r, what, _ in m.convos.log if r == p.room and what == "started")}

    def night_context(self, seed, day, ask, p, where=None, leaver=None):
        return {"seed": seed, "day": day, "house_day": day + 3, "night": True, "ask": ask, "minute": None,
                "room": where or OWN_ROOM[p.id], "others": [], "partner": None, "convo": 0, "leaver": leaver}

    # ---------- the two places the engine asks ----------
    def decide(self, m, p, t, opts, d, extra=None):
        return self.choose(p, opts, self.context_of(m, p, t, opts, d))

    def decide_night(self, n, p, kind, opts):
        leaver = next((o.id[len("stop_"):] for o in opts if o.id.startswith("stop_")), None)
        with truth.prompting():
            ctx = self.night_context(n.day1.seed, day_index(n.day1.day), kind, p, n.where.get(p.id), leaver)
        return self.choose(p, opts, ctx)

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
            "heard_question": float(p.heard_question),
            "counted": float(any(data.OPENING in line and "(you did it)" in line for line in p.sure)),
            "owes_nobody": float(owed is None), "owes_accusation": float(owed_kind == "accuse"),
            "accused_publicly": float(owed_kind == "accuse" and len(others) >= 2),
            "offered_today": float(bool(own) and own[1] == "volunteer"),
            "someone_offered": float(any(v[1] == "volunteer" for w, v in p.trip_heard.items() if w != p.id)),
            "weak": float(needs.get("fast_stage", 0) >= 3), "debt_stage": float(needs.get("debt_stage", 0)),
            "knock_today": float("knock" in notes),
        })
        f["_owed"] = owed
        f["_owed_kind"] = owed_kind
        return f

    def target_facts(self, p, ctx, o, target, f):
        """The facts that depend on whom or where the move is aimed."""
        other = next((x for x in ctx["others"] if x["id"] == target), None)
        owed, kind = f["_owed"], f["_owed_kind"]
        pos = p.trip_heard.get(target) if target in data.PEOPLE else None
        day_heard = p.heard
        return {
            "s_target": min(3, self.evidence.get((p.id, ctx["day"]), {}).get(target, 0)) / 3,
            "k_target": (p.grudges[target].strength / 3) if target in p.grudges else 0.0,
            "k_partner": (p.grudges[ctx["partner"]].strength / 3) if ctx.get("partner") in p.grudges else 0.0,
            "u_target": (other["upset"] / 3) if other else 0.0,
            "target_offered": float(bool(pos) and pos[1] in ("volunteer", "volunteer_far")),
            "owes_target_line": float(owed is not None and owed["who"] == target
                                      and kind in ("confront", "reassure", "say")),
            "to_own_room": float(o.act.get("kind") == "go" and o.act.get("to") == OWN_ROOM.get(p.id)),
            "target_accused_by_other": float(any(h["kind"] == "accuse" and h["target"] == target
                                                 and h["who"] != p.id for h in day_heard)),
        }

    # ---------- what reached them since they last decided ----------
    def notice(self, p, opts, ctx):
        """Reads the lines p has heard since the brain last looked, and who has left the room: what was done to
        them today (for tomorrow's mood), and the evidence of their own eyes (for their suspicion)."""
        key = (p.id, ctx["day"])
        notes = self.notes.setdefault(key, set())
        evidence = self.evidence.setdefault(key, {})
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
                    evidence[h["who"]] = evidence.get(h["who"], 0) + 1
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
                        evidence[q] = evidence.get(q, 0) + 1
            self.room_seen[key] = (ctx["minute"], here)

    # ---------- the day's mood (section 7.2) ----------
    def set_mood(self, pid, day, mood, cause=None):
        """For tests: p's mood on that day, as given."""
        self.moods[(pid, day)] = {"mood": mood, "cause": cause, "seeded": False, "points": {}}

    def mood_of(self, p, ctx):
        """p's mood on this day: set once, when they first decide. Mostly from causes (last night's sleep, hunger on
        waking, yesterday), plus a small seeded part; the mood with the most points wins, one with a cause beats one
        without, and no points is steady."""
        key = (p.id, ctx["day"])
        if key in self.moods:
            return self.moods[key]
        t = p.sheet["traits"]
        points = {m: 0 for m in MOODS}
        causes = {m: [] for m in MOODS}

        def add(mood, n, cause):
            points[mood] += n
            causes[mood].append(cause)
        night = self.last_night.get(p.id)
        if night and night[0] == ctx["day"] - 1 and night[1] in BAD_NIGHT:
            n, cause = BAD_NIGHT[night[1]]
            add("on edge" if t["anxious"] >= 0.6 and not cause == "a night out" else "low", n, cause)
        # Hunger colours the morning it is new or worse than the morning before. Hunger that has only gone on is
        # no news to the person: it still weighs in every decision (the hunger terms), but it does not name the day.
        level = hunger_level(p.hunger)
        self.woke[key] = level
        if level >= 2 and level > self.woke.get((p.id, ctx["day"] - 1), 0):
            add("on edge" if t["impulsive"] >= 0.6 else "low", 1, "hunger")
        yesterday = self.notes.get((p.id, ctx["day"] - 1), set())
        if "accused" in yesterday:
            add("low" if p.guilt is not None else "on edge", 2, "being accused yesterday")
        if "comforted" in yesterday:
            add("warm", 1, "yesterday's kindness")
        rng = random.Random(f"{self.seed}:mood:{ctx['day']}:{p.id}")
        seeded = rng.choice(MOODS) if rng.random() < 0.5 else None
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
        if not once:
            return None
        name = rule.get("once_key") or f"{key}#{i}"
        if once == "week":
            return (pid, name)
        if once == "accuser":
            return (pid, ctx["day"], name, (flags["_owed"] or {}).get("who"))
        if once == "convo":
            return (pid, ctx["day"], name, ctx["convo"])
        return (pid, ctx["day"], name) if rule.get("once_key") else (pid, ctx["day"], name, target)

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
            self.last_keys[o.id] = key if rule is not None or key == "stay" else f"{key} (default)"
            rows.append({"o": o, "key": key, "target": target, "score": score + tilt, "terms": terms, "tilt": tilt,
                         "once": once, "open": is_open})
        open_rows = [r for r in rows if r["open"]] or rows     # a list with nothing open (it has no "stay") is free
        self.last_scores = {r["o"].id: r["score"] for r in open_rows}
        best = max(r["score"] for r in open_rows)
        band = sorted((r for r in open_rows if r["score"] >= best - self.weights["band"] - 1e-9),
                      key=lambda r: r["o"].id)
        n = self.calls[(pid, day)] = self.calls.get((pid, day), 0) + 1
        if len(band) > 1:
            rng = random.Random(f"{self.seed}:tie:{day}:{ctx['minute']}:{pid}:{ctx['ask']}:{n}")
            row = rng.choice(band)
        else:
            row = band[0]
        o = row["o"]
        counts[o.id] = counts.get(o.id, 0) + 1
        if row["once"] is not None:
            self.done[row["once"]] = self.done.get(row["once"], 0) + 1
        if ctx["ask"] == "bedtime":
            self.last_night[pid] = (day, o.id)
        second = max((r["score"] for r in open_rows if r is not row), default=None)
        top = sorted(row["terms"], key=lambda kv: -abs(kv[1]))[:3]
        words = self.weights.get("words", {})

        def said(name):
            return ", ".join(words.get(x, x.replace("_", " ")) for x in name.split(", "))
        why = {"terms": [[said(name), round(v, 3)] for name, v in top], "score": round(row["score"], 3),
               "lead": None if second is None else round(row["score"] - second, 3), "tilt": row["tilt"],
               "among": [r["o"].id for r in band] if len(band) > 1 else None}
        reason = "; ".join(f"{name} {v:+.2f}" for name, v in why["terms"]) or "nothing weighed more"
        suspect = max(self.evidence.get((pid, day), {}).items(), key=lambda kv: (kv[1], kv[0]), default=(None, 0))
        return {"option": o.id, "say": self.line(p, row["key"], row["target"], ctx) if o.speech else None,
                "feeling": self.feeling(p, row["key"], base, mood, ctx), "reason": reason, "dropped_line": False,
                "suspects": NAMES[suspect[0]] if suspect[1] >= 1 else "nobody",
                "angry_at": self.angry_at(p, base, ctx), "why": why,
                "mood": {"mood": mood["mood"], "cause": mood["cause"]}}

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

    def angry_at(self, p, f, ctx):
        """Whoever accused them falsely today, said once for each accusation; else nobody."""
        if f["took_it"]:
            return "nobody"
        for x, minute in p.accused_by.items():
            mark = (p.id, x, ctx["house_day"], minute)
            if p.accused_day.get(x) == ctx["house_day"] and mark not in self.told_anger:
                self.told_anger.add(mark)
                return NAMES[x]
        return "nobody"

    def line(self, p, key, target, ctx):
        """Words for a spoken move, from content/lines.json: the speaker's own where there are any, never the variant
        they used last."""
        table = self.lines.get("by_person", {}).get(p.id, {}).get(key) or self.lines["default"].get(key)
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
