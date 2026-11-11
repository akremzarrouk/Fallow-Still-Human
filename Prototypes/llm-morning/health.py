"""Sickness and injury, from causes only (Docs/fable-audit-2026-11.md, 7.4; section 9, step 3).

No draw is made without a cause, so nobody falls sick for no reason:

  drinking rain water that was not boiled (there is no stove)      a stomach sickness
  being wet and cold                                              a chill
  days without enough food ("thin and weak" or worse)              faintness; every other chance is higher for them
  sharing a room with someone sick, or looking after them          catching it
  the day's work: the boards, carrying the water                   a cut hand, a strained back
  a night trip that goes wrong                                     a twisted ankle

A condition has three levels: 1 unwell or sore (works slower), 2 laid up (keeps to their bed and needs care), 3
bedridden. Each night it mends or worsens by a draw shaped by rest, food, water and care. At home it never goes past
bedridden: nobody is lost to sickness inside the week (7.4, "Losing someone").

Every draw is kept with the chance it was made at and the conditions that held (the LLM-off test's L12), and every
condition names its cause (L13). No chance reads the number of the day: the day is only part of a draw's seed string,
so that two days' draws are independent. Every number is in content/chances.json, with a line saying why.
"""
import random

import data

NAMES = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
ROOMMATE = {p: q for owners in data.OWNERS.values() for p in owners for q in owners if q != p}
LEVEL_WORDS = {1: "unwell", 2: "laid up", 3: "bedridden"}


class Health:
    def __init__(self, seed, chances):
        self.seed, self.chances = seed, chances
        self.now = {}           # person -> {"what", "cause", "level", "since", "kind", "catching", "cared": [days]}
        self.draws = []         # every draw made: what, who, the chance, the conditions, the draw, whether it hit
        self.events = []        # every onset and every change of a condition, with its line for the diary
        self.rain_seen = {}     # person -> litres of rain water drunk as of the last night
        self.levels = {}        # day -> person -> their level as the day began

    # ---------- what the rest of the game asks ----------
    def level(self, pid):
        return self.now.get(pid, {}).get("level", 0)

    def what(self, pid):
        return self.now.get(pid, {}).get("what")

    def cared(self, pid, day):
        if pid in self.now and day not in self.now[pid]["cared"]:
            self.now[pid]["cared"].append(day)

    def record(self):
        return {"draws": self.draws, "events": self.events, "levels": {str(k): v for k, v in self.levels.items()},
                "now": {p: {k: v for k, v in c.items()} for p, c in self.now.items()}}

    # ---------- a draw, and what it brings ----------
    def draw(self, name, day, pid, chance, conditions, tag=""):
        u = random.Random(f"{self.seed}:chance:{name}:{day}:{pid}:{tag}").random()
        rec = {"what": name, "day": day, "who": pid, "chance": round(min(1.0, max(0.0, chance)), 4),
               "draw": round(u, 4), "conditions": list(conditions), "hit": u < chance}
        self.draws.append(rec)
        return rec

    def fall(self, pid, name, day, conditions, factor=1.0, tag="", like=None):
        """A cause holds for pid: one draw. On a hit they have the condition it brings (or `like`: the condition they
        caught). Someone already sick or hurt is not drawn for again: their own condition takes its course."""
        if pid in self.now:
            return None
        spec = self.chances[name]
        rec = self.draw(name, day, pid, spec["chance"] * factor, conditions, tag)
        if not rec["hit"]:
            return None
        what = like["what"] if like else spec["brings"]
        he = data.PRONOUNS[pid]
        cause = spec["cause"].format(name=NAMES.get(tag, ""), his=he["his"])
        self.now[pid] = {"what": what, "cause": cause, "level": spec.get("level", 1), "since": day,
                         "kind": spec["kind"], "catching": bool(like["catching"] if like else spec.get("catching")),
                         "cared": []}
        line = f"{NAMES[pid]} " + spec["onset"].format(what=what, name=NAMES.get(tag, ""), his=he["his"]) + "."
        self.events.append({"day": day, "who": pid, "what": what, "cause": cause, "level": self.now[pid]["level"],
                            "change": "onset", "chance": rec["chance"], "conditions": rec["conditions"], "line": line})
        return line

    def hazard(self, p, name, day, minute):
        """Work that can hurt (content/practices.json): one draw as it is done; twice as likely for someone weak
        from hunger. Returns what came of it for the room, or None."""
        weak = (p.needs or {}).get("fast_stage", 0) >= 2
        line = self.fall(p.id, name, day, [f"did the work ({name})"] + (["weak from hunger"] if weak else []),
                         factor=2.0 if weak else 1.0, tag=str(minute))
        return line

    # ---------- once a night ----------
    def night(self, n, day, notes):
        """After day `day` and its night: each condition takes its course, then each cause that held today or tonight
        is drawn for. notes(pid) -> what the brain noted of pid's day ("wet", ("tended", x)). Returns the lines."""
        lines = []
        present = [q for q in data.ORDER if q not in n.away]
        course = self.chances["course"]
        before = {q: dict(c) for q, c in self.now.items()}
        for q in present:
            c = self.now.get(q)
            if c is None or c["since"] == day:
                continue
            needs = n.people[q].needs or {}
            hungry, thirsty = needs.get("fast_stage", 0) >= 2, needs.get("thirst_stage", 0) >= 2
            care, rest = day in c["cared"], c["level"] >= 2
            mend = (course["mend"] + (course["care"] if care else 0) + (course["rest"] if rest else 0)
                    - (course["hunger"] if hungry else 0) - (course["thirst"] if thirsty else 0))
            worse = (course["worsen"] + (course["hunger"] if hungry else 0) + (course["thirst"] if thirsty else 0)
                     - (course["care"] if care else 0))
            mend, worse = min(0.9, max(0.05, mend)), min(0.9, max(0.0, worse))
            conditions = ([f"{c['what']}, {LEVEL_WORDS[c['level']]}"] + (["looked after today"] if care else [])
                          + (["kept to bed"] if rest else []) + (["hungry"] if hungry else [])
                          + (["thirsty"] if thirsty else []))
            rec = self.draw("course", day, q, mend, conditions + [f"worsens above {round(1 - worse, 2)}"])
            u = rec["draw"]
            if u < mend:
                c["level"] -= 1
                change = "well" if c["level"] == 0 else "better"
            elif u > 1 - worse and c["level"] < 3:      # at home, never past bedridden
                c["level"] += 1
                change = "worse"
            else:
                continue
            line = {"well": f"{NAMES[q]} was well again.", "better": f"{NAMES[q]} was better: {LEVEL_WORDS.get(c['level'])} now.",
                    "worse": f"{NAMES[q]} was worse: {LEVEL_WORDS.get(c['level'])} now."}[change]
            self.events.append({"day": day, "who": q, "what": c["what"], "cause": c["cause"], "level": c["level"],
                                "change": change, "chance": rec["chance"], "conditions": rec["conditions"],
                                "line": line})
            lines.append(line)
            if c["level"] == 0:
                del self.now[q]
        w = n.world
        drunk = dict(getattr(w, "rain_drunk", {})) if w is not None else {}
        for q in present:
            p = n.people[q]
            needs = p.needs or {}
            weak = needs.get("fast_stage", 0) >= 3
            factor = self.chances["long_hunger"]["raises"] if weak else 1.0
            hungry = ["thin and weak from hunger"] if weak else []
            got = drunk.get(q, 0.0) - self.rain_seen.get(q, 0.0)
            if got > self.chances["rain_water"]["from_litres"]:
                lines.append(self.fall(q, "rain_water", day, [f"drank {got:.1f} L of rain water today"] + hungry, factor))
            mine = notes(q)
            wet = "wet" in mine or (n.rainy and q in n.leavers and q not in n.away)
            if wet:
                lines.append(self.fall(q, "wet_cold", day, ["was out in the rain"] + hungry, factor))
            if weak:
                lines.append(self.fall(q, "long_hunger", day, hungry))
            mate = before.get(ROOMMATE[q])
            if mate and mate["catching"] and ROOMMATE[q] in present:
                lines.append(self.fall(q, "room_mate", day, [f"shares a room with {NAMES[ROOMMATE[q]]}, who has "
                                                             f"{mate['what']}"] + hungry, factor, tag=ROOMMATE[q],
                                       like=mate))
            for x in sorted(t[1] for t in mine if isinstance(t, tuple) and t[0] == "tended"):
                sick = before.get(x)
                if sick and sick["catching"]:
                    lines.append(self.fall(q, "tending", day, [f"looked after {NAMES[x]}, who has {sick['what']}"]
                                           + hungry, factor, tag=x, like=sick))
            for g in n.groups:
                if q in g["shaken"]:
                    spared = g.get("spared") == q
                    lines.append(self.fall(q, "spared" if spared else "night_scare", day,
                                           ["a night trip that went wrong"] + hungry, 1.0 if spared else factor))
        self.rain_seen = drunk
        return [x for x in lines if x]
