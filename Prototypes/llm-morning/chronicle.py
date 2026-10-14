"""The world chronicle (reports/days_design.md, §4): the code's record of what happened each day and night, facts
only. Each event is one thing done, with who did it, who perceived it and how, and the line each of them got of it.
Facts the world had not decided are fixed here the first time a rule needs them, and never drawn again.

It reads the scenes once they are over (a finished Morning, a finished Night) and changes nothing in them. The
night minds' answers are kept beside it (`minds`), never among the events: they are what a person made of the
facts, not facts.
"""
import data
from talk import SPEECH, act_of
from world import NAMES, day_index

KEYS = ("id", "scene", "minute", "kind", "option", "actor", "target", "members", "words", "room", "witnesses",
        "text", "gist", "group", "effects", "views", "outcome")
# A routine span and a need crossing a line (quiet.py) keep these too, after KEYS; no other event has them.
QUIET_KEYS = ("routine", "until", "need", "stage")
ROUTINE_GIST = {"rest": "lying down to rest", "withdraw": "going off to their own room", "sit": "sitting in the kitchen"}


def he(pid):
    return data.PRONOUNS[pid]["he"]


def gist(e, pid):
    """A short name for an event, as `pid` would call it (reports/days_design.md, §3.2, block B)."""
    actor, target, kind, option = e.get("actor"), e.get("target"), e["kind"], e.get("option") or ""
    t = "you" if target == pid else NAMES.get(target, "")
    pronoun = he(actor) if actor else "they"
    phrases = {
        "opening": "the count of the pantry" if e["scene"] == "D1" else "everyone coming into the kitchen",
        "ask": "asking who took the can", "deny": "denying taking it", "accuse": f"accusing {t} of taking the can",
        "confess": "admitting taking the can", "confront": f"confronting {t}",
        "reassure": f"reassuring {t}" if target else "reassuring everyone", "say": "speaking to everyone",
        "propose": "saying someone should go to the neighbour's house",
        "volunteer": (f"saying {pronoun} still means to go" if option == "still_going"
                      else "offering to go to the neighbour's house"),
        "object": f"saying {t} must stay home" if target else "saying nobody should go",
        "back": f"saying {t} should go", "decline": f"saying {pronoun} will not go",
        "eat": "eating a portion", "eat_empty": "reaching for the empty shelf", "share": "sharing out the food",
        "give": f"giving {t} a portion", "eat_given": "eating a portion handed over",
        "refuse_given": "putting a handed portion back", "search": "searching", "search_done": "searching",
        "go": "leaving the room", "sit": f"sitting with {t}", "aside": f"taking {t} aside",
        "accept_aside": "going aside", "refuse_aside": "refusing to go aside", "gap": "the afternoon and evening",
        "bedtime": "going to bed", "got_up": "getting up in the night", "at_door": "going to the front door in the night",
        "door": "the front door opening in the night", "reaction": "what you did in the night",
        "stop": f"telling {t}, low, not to go", "answer": "answering, low, in the night",
        "went_out": "going out to the neighbour's house", "street": "the neighbour's house and the street",
        "return": "coming back in before dawn",
        "routine": ROUTINE_GIST.get(e.get("routine"), "a routine"), "need": "how the body was"}
    phrase = phrases.get(kind, kind)
    if kind in ("door", "gap", "street"):
        return phrase
    if actor == pid:
        return phrase + (" yourself" if kind in ("eat", "went_out") else "")
    return f"{NAMES[actor]} {phrase}" if actor else phrase


def view_text(pid, actor, words, view):
    """The record of an act for `pid`, from the lines they got of it (§2.3, R1-R3): a pinned fact first, with the
    words said while doing it; their own speech with its words and the feeling they gave; or what they heard."""
    sure, memory = view.get("sure", []), view.get("memory", [])
    if sure:
        text = sure[0]
        if words and words not in text:
            text = text.rstrip(".") + f', saying: "{words}"'
        return text
    if pid == actor and memory:
        verb, sep, feel = memory[0].partition(". You felt ")
        if words:
            return f'{verb.rstrip(".")}, saying: "{words}"' + (f" You felt {feel}" if sep else "")
        return memory[0]
    return " ".join(memory)


def night_text(line):
    """A night line in the night's own words (§2.3, R5)."""
    line = line.replace("Last night you slept in", "You went to bed in")
    if line.startswith("In the night "):
        line = line[len("In the night "):]
    return line[0].upper() + line[1:]


class Chronicle:
    def __init__(self, seed, culprit=None):
        self.seed, self.culprit = seed, culprit
        self.scenes, self.events, self.open = [], [], []
        self.fixed = {"culprit": {"value": culprit, "draw": None, "string": None, "scene": "before D1",
                                  "why": "the scenario says who took the can, if anyone"}}
        self.by_id = {}
        self.minds = {}             # night number -> person -> the night mind's checked answer (mind.py)
        self.nights = []            # the Night objects, in order (not saved)
        self._house = None

    # ---------- reading ----------
    def event(self, eid):
        return self.by_id.get(eid)

    def perceived(self, pid):
        return [e for e in self.events if pid in e["witnesses"]]

    def knows_culprit(self, pid):
        """Who took the can, as `pid` knows it: themselves, or a confession they perceived."""
        if self.culprit is None:
            return None
        if pid == self.culprit:
            return pid
        if any(e["kind"] == "confess" and e["actor"] == self.culprit and pid in e["witnesses"] for e in self.events):
            return self.culprit
        return None

    def house_state(self):
        """The neighbour's house as the last night left it, for the next night (§4.3)."""
        return self._house

    def to_json(self):
        return {"scenes": self.scenes, "events": self.events, "fixed": self.fixed, "open": self.open}

    # ---------- writing ----------
    def add(self, e):
        """One event, its missing fields filled; returns it."""
        e = {**{k: None for k in KEYS}, "witnesses": {}, "gist": {}, "effects": {}, "views": {}, "text": "", **e}
        e = {k: e[k] for k in KEYS} | {k: e[k] for k in QUIET_KEYS if k in e}
        if not e["gist"]:
            e["gist"] = {pid: gist(e, pid) for pid in e["witnesses"]}
        self.events.append(e)
        self.by_id[e["id"]] = e
        return e

    @staticmethod
    def state(m):
        """A scene's end, in the rules' numbers."""
        people = m.people.values()
        return {"shelf": m.portions, "away": sorted(m.away),
                "rooms": {p.id: p.room for p in people},
                "hunger": {p.id: round(p.hunger, 4) for p in people},
                "grudges": {p.id: {t: g.strength for t, g in p.grudges.items() if g.strength} for p in people},
                "suspicion": {p.id: p.suspicion.state() for p in people},
                "guilt": {p.id: p.guilt for p in people if p.guilt is not None},
                "knows_culprit": {p.id: p.knows_culprit for p in people}}

    def add_day(self, m):
        """A finished morning: the opening, then every act that is not silence and that someone perceived (§4.2)."""
        k = day_index(m.day)
        sid = f"D{k}"
        self.scenes.append({"id": sid, "kind": "day", "house_day": m.day,
                            "start": {"shelf": m.start_portions, "away": sorted(m.away)}, "end": self.state(m)})
        n = 0

        def new_id():
            nonlocal n
            n += 1
            return f"{sid}-{n:03d}"
        present = [q for q in data.ORDER if q not in m.away]
        opening = {q: m.people[q].sure[0][8:] for q in present if m.people[q].sure}
        first = next(iter(opening.values()), "")
        self.add({"id": new_id(), "scene": sid, "minute": 0, "kind": "opening", "room": "kitchen",
                  "actor": "elena" if m.day == 4 else None,
                  "witnesses": {q: ("did" if m.day == 4 and q == "elena" else "saw") for q in opening},
                  "text": first.rsplit(" (you ", 1)[0], "views": opening})
        said = iter(m.said)
        shelf = m.start_portions
        groups = {}
        # From day 3, the routine spans and need crossings (quiet.py), each before the turns at or after its minute.
        extra = m.quiet.items() if getattr(m, "quiet", None) is not None else []

        def quiet_until(minute):
            while extra and (minute is None or extra[0]["minute"] <= minute):
                self.add({"id": new_id(), "scene": sid, **extra.pop(0)})
        for turn in m.transcript["turns"]:
            quiet_until(turn["minute"])
            for a in turn["acts"]:
                text = (next(said, None) or {}).get("text") if a["words"] else None
                seq = a["decided_at"][1]
                views = m.views.get(seq, {})
                heard = m.voices_heard.get(seq, {})
                if a["option"] == "silent" or (a["mode"] == "routine" and not views):
                    continue
                kind, target = act_of(a["option"])
                came = a.get("came_of_it") or ""
                if kind == "eat" and "found it empty" in came:
                    kind = "eat_empty"
                if came.startswith("went through the room and found nothing"):
                    kind = "search_done"
                # The person an act is aimed at, if one: never a room (go_<room>) or everyone (reassure_all).
                if kind not in ("accuse", "reassure", "confront", "back", "object", "give", "sit", "aside") \
                        or target not in data.PEOPLE:
                    target = None
                effects = {}
                if kind in ("eat", "give", "refuse_given", "share"):
                    after = {"eat": shelf - 1, "give": shelf - 1, "refuse_given": shelf + 1, "share": 0}[kind]
                    effects, shelf = {"shelf": [shelf, after]}, after
                witnesses = {a["who"]: "did"}
                witnesses.update({q: "saw" for q in views if q != a["who"]})
                witnesses.update({q: "voices" for q in heard if q not in witnesses})
                texts = {q: view_text(q, a["who"], a["words"], v) for q, v in views.items()}
                texts.update({q: f"Voices from the {data.ROOMS[r]}." for q, r in heard.items() if q not in texts})
                e = self.add({"id": new_id(), "scene": sid, "minute": turn["minute"], "kind": kind,
                              "option": a["option"], "actor": a["who"], "target": target, "words": a["words"],
                              "room": a["room"], "witnesses": witnesses,
                              "text": text or f"{NAMES[a['who']]} {came}".strip(), "effects": effects, "views": texts})
                if a["words"] and kind in SPEECH:
                    groups.setdefault((a["who"], a["option"]), []).append(e["id"])
        quiet_until(None)
        for ids in groups.values():
            if len(ids) > 1:
                for i in ids:
                    self.by_id[i]["group"] = list(ids)

    def add_night(self, n):
        """A finished night, after its gap: the gap, then every event of the night with the line each person
        got of it; the neighbour's house fixed the first time anyone got inside (§4.3)."""
        k = n.number
        present = [q for q in data.ORDER if q not in n.prev.away]
        self.scenes.append({"id": f"G{k}", "kind": "gap"})
        self.add({"id": f"G{k}-01", "scene": f"G{k}", "minute": data.MINUTES, "kind": "gap",
                  "witnesses": {q: "saw" for q in present}, "text": data.GAP})
        ids = {e["key"]: f"N{k}-{i:02d}" for i, e in enumerate(n.events, 1)}
        views = {}
        for pid in data.ORDER:
            for line, key in zip(n.lines[pid], n.line_events[pid]):
                if key is None:
                    continue
                v = views.setdefault(key, {})
                v[pid] = (v[pid] + " " if pid in v else "") + night_text(line)
        for e in n.events:
            self.add({"id": ids[e["key"]], "scene": f"N{k}", "minute": data.MINUTES, "kind": e["kind"],
                      "option": e.get("option"), "actor": e["actor"], "target": e.get("target"),
                      "members": e.get("members"), "words": e.get("words"), "witnesses": e["witnesses"],
                      "outcome": e.get("outcome"),
                      "text": f"{NAMES[e['actor']]}: {e['kind']}" + (f" ({e['outcome']})" if e.get("outcome") else ""),
                      "views": views.get(e["key"], {})})
        self.scenes.append({"id": f"N{k}", "kind": "night", "end": self.state(n.m) | {"shelf": n.portions,
                                                                                      "away": sorted(n.away)}})
        got_in = [g for g in n.groups if g["street"] in ("clean", "scare_back")]
        if got_in and "neighbour_house" not in self.fixed:
            self.fixed["neighbour_house"] = {"value": n.house, "draw": n.house_u, "string": n.draw_string("house"),
                                             "scene": f"N{k}", "why": "someone got inside for the first time"}
        if k == 1:
            self.open.append({"name": "the street", "since": "N1",
                              "what": "beyond 'something was moving', nothing about the street is fixed"})
        for x in data.ORDER:
            if x in n.away and x not in n.prev.away:
                self.open.append({"name": f"where {NAMES[x]} is", "since": f"N{k}",
                                  "what": "went out in the night and has not come back"})
        self._house = n.house_state()
        self.nights.append(n)
