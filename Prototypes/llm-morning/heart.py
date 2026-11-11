"""The heart: what each person carries toward the others, kept by code alone (Docs/fable-audit-2026-11.md, 7.2).

Three things per person, none of them a model's word:

  stance      toward each other person, a short list of remembered acts, each with its day and its weight. Trust is
              their sum, between -3 and +3. An ordinary act fades by half every two nights; a mark does not fade.
  suspicion   points from things perceived, never from a guess. Without new evidence it loses a point every two days.
  intention   one thing they have decided to do and have not yet done, with a cause and an end date at most three
              days off. The night step renews it while its cause stands and drops it otherwise.

The heart reads nothing: the brain tells it what a person perceived (brain.CodeBrain.saw, .notice, .night_step). Every
weight and every sentence is in content/weights.json, under "heart".
"""
import data

NAMES = {p: data.PEOPLE[p]["name"] for p in data.ORDER}


def clip(x, lo=-3.0, hi=3.0):
    return max(lo, min(hi, x))


class Heart:
    def __init__(self, rules):
        self.rules = rules
        self.acts = {}          # (holder, other) -> [{"kind", "day", "w", "mark", "says"}], oldest first
        self.clues = {}         # (holder, other) -> [{"what", "day", "points", "says"}]
        self.intents = {}       # holder -> {"kind", "target", "cause", "made", "until", "says"}
        self.log = []           # every change, in order, for the record and the diary

    # ---------- stance ----------
    def remember(self, holder, other, kind, day, once_a_day=True):
        """holder now remembers that `other` did this to them. The same kind of act by the same person counts once a
        day. Returns the remembered act, or None if it was already counted."""
        if holder == other or holder is None or other is None:
            return None
        spec = self.rules["acts"][kind]
        mine = self.acts.setdefault((holder, other), [])
        if once_a_day and any(a["kind"] == kind and a["day"] == day for a in mine):
            return None
        pro = data.PRONOUNS[holder]
        act = {"kind": kind, "day": day, "w": spec["w"], "mark": bool(spec.get("mark")),
               "says": spec["says"].format(other=NAMES[other], him=pro["him"], his=pro["his"], he=pro["he"])}
        mine.append(act)
        self.log.append({"what": "remembered", "day": day, "who": holder, "of": other, "kind": kind, "w": spec["w"],
                         "mark": act["mark"]})
        return act

    @staticmethod
    def weight_now(act, day):
        """What a remembered act weighs on this day: a mark keeps its weight; anything else halves in two nights."""
        return act["w"] if act["mark"] else act["w"] * 0.5 ** (max(0, day - act["day"]) / 2)

    def trust(self, holder, other, day):
        return clip(sum(self.weight_now(a, day) for a in self.acts.get((holder, other), ())))

    def behind(self, holder, other, day, sign):
        """The remembered act of that sign that weighs most today, in words with its day; None if there is none."""
        mine = [a for a in self.acts.get((holder, other), ()) if a["w"] * sign > 0]
        if not mine:
            return None
        a = max(mine, key=lambda a: (abs(self.weight_now(a, day)), a["day"]))
        return f"{a['says']}, {'today' if a['day'] == day else 'day ' + str(a['day'])}"

    # ---------- suspicion ----------
    def clue(self, holder, other, what, day):
        """Something holder perceived that points at other."""
        if holder == other:
            return
        spec = self.rules["clues"][what]
        self.clues.setdefault((holder, other), []).append(
            {"what": what, "day": day, "points": spec["points"], "says": spec["says"].format(other=NAMES[other])})
        self.log.append({"what": "clue", "day": day, "who": holder, "of": other, "kind": what})

    def suspicion(self, holder, other, day):
        """Points against other as holder holds them today: the clues, less one point for every two days since the
        last one."""
        mine = self.clues.get((holder, other), ())
        if not mine:
            return 0
        last = max(c["day"] for c in mine)
        return max(0, sum(c["points"] for c in mine) - max(0, day - last) // 2)

    def suspect(self, holder, day, also=None):
        """(whom holder suspects most, the points), or (None, 0). also(other) -> extra points from temperament."""
        best = (None, 0)
        for other in data.ORDER:
            if other == holder:
                continue
            pts = self.suspicion(holder, other, day)
            if pts and also is not None:
                pts += also(other)
            if pts > best[1]:
                best = (other, pts)
        return best

    def clue_count(self, holder, other):
        return len(self.clues.get((holder, other), ()))

    # ---------- intention ----------
    def intend(self, holder, kind, target, cause, day, days=3):
        """holder decides to do something. One at a time: a new one takes the place of the old only if it is of
        another kind. Returns True if it was formed."""
        old = self.intents.get(holder)
        if old is not None and old["kind"] == kind and old["target"] == target:
            return False
        spec = self.rules["intentions"][kind]
        pro = data.PRONOUNS[holder]
        says = spec["says"].format(target=NAMES.get(target, ""), him=pro["him"], he=pro["he"])
        self.intents[holder] = {"kind": kind, "target": target, "cause": cause, "made": day,
                                "until": day + min(days, 3), "says": says}
        self.log.append({"what": "intended", "day": day, "who": holder, "kind": kind, "target": target, "cause": cause})
        return True

    def intends(self, holder, kind, target=None):
        i = self.intents.get(holder)
        return i is not None and i["kind"] == kind and (target is None or i["target"] == target)

    def settle(self, holder, day, done=False, gone=None):
        """The night step's verdict on holder's intention. done: they did it. gone: why it cannot or need not be done
        any more, in words. Otherwise it is renewed until its end date. Returns ("done" | "dropped" | "renewed" |
        None, the diary line or None)."""
        i = self.intents.get(holder)
        if i is None:
            return None, None
        if done:
            del self.intents[holder]
            self.log.append({"what": "intention done", "day": day, "who": holder, "kind": i["kind"]})
            return "done", None
        if gone is None and day >= i["until"]:
            gone = "the days went by"
        if gone is not None:
            del self.intents[holder]
            line = f"{NAMES[holder]} no longer meant to {i['says']}: {gone}."
            self.log.append({"what": "intention dropped", "day": day, "who": holder, "kind": i["kind"], "why": gone,
                             "line": line})
            return "dropped", line
        self.log.append({"what": "intention renewed", "day": day, "who": holder, "kind": i["kind"]})
        return "renewed", None

    # ---------- the record ----------
    def state(self, day):
        """Everyone's heart on this day, for the transcript."""
        out = {}
        for p in data.ORDER:
            out[p] = {
                "trust": {q: round(self.trust(p, q, day), 2) for q in data.ORDER
                          if q != p and self.acts.get((p, q))},
                "suspicion": {q: self.suspicion(p, q, day) for q in data.ORDER
                              if q != p and self.clues.get((p, q))},
                "intention": ({k: self.intents[p][k] for k in ("kind", "target", "cause", "made", "until")}
                              if p in self.intents else None)}
        return out
