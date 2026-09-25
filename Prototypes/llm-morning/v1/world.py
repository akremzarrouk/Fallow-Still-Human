"""The rules layer. Keeps the house, each person's memory, and lists what each of them
may do. Asks the model only when something social has just happened to a person;
every other turn is settled here.
"""
import json
import re

import data

SYSTEM = (
    "You decide what one person in a family does in the next three minutes. You get who "
    "they are, what they remember, what they see now, and the options open to them. They "
    "know only what is in their memory. Choose exactly one option id from the list. If the "
    "option is marked (speech), `say` must hold the exact words they say, in their own voice, "
    "one or two short sentences. For any other option `say` is a short line they say while "
    "doing it, or null. `feeling` names what they feel right now in one or two words. "
    "`reason` is their reason in one sentence, as they would think it. Reply with JSON only: "
    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>"}'
)

# Feelings that reach the face. Others in the room see them, and someone who looks like
# this counts as upset nearby. Anything else (guilty, ashamed, anxious, tense...) stays inside.
OUTWARD = ("scared", "afraid", "fright", "terrif", "panic", "upset", "distress", "angry", "anger",
           "furious", "rage", "hurt", "sad", "cry", "tear", "desperat", "hysteri", "shak",
           "betray", "outrag", "humiliat", "frantic", "miserab", "devastat", "sob", "wounded")
FEELING_SHOWS_FOR_TURNS = 3
PROMPT_TOKEN_BUDGET = 1250   # estimated (~4,500 characters); the limit asked for is about 1,500


def estimate_tokens(text):
    return int(len(text) / 3.6) + 1


def outward(feeling):
    f = (feeling or "").lower()
    return any(stem in f for stem in OUTWARD)


def hunger_words(h):
    if h < 0.5:
        return "a little hungry"
    if h < 0.7:
        return "hungry"
    if h < 0.85:
        return "very hungry"
    return "weak with hunger"


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


class Option:
    def __init__(self, id, label, speech=False, **act):
        self.id, self.label, self.speech, self.act = id, label, speech, act


class Person:
    def __init__(self, pid):
        d = data.PEOPLE[pid]
        self.id, self.name = pid, d["name"]
        self.sheet = d
        self.hunger = d["hunger"]
        self.room = "kitchen"
        self.activity = {"kind": "idle", "label": "standing at the pantry"}
        self.feeling, self.feeling_until = None, -1
        self.backstory = [f"Day {day}: {text} (you {how} it)" for day, text, who in data.BACKSTORY
                          if (how := who.get(pid))]
        self.memory = []            # this morning, oldest first; trimmed to fit a prompt
        self.sure = []              # this morning's facts that are never trimmed
        self.said_lines = []        # their own words, oldest first
        self.just_now = []          # perceived since the last turn
        self.triggers = []          # social things that happened to them since the last turn
        self.searched = set()
        self.knows_culprit = data.CULPRIT if pid == data.CULPRIT else None
        self.heard_question = False
        self.confessed = False
        self.eaten = 0.0


class Morning:
    def __init__(self, oracle):
        self.oracle = oracle
        self.people = {p: Person(p) for p in data.ORDER}
        self.portions = data.PORTIONS
        self.turns = data.MINUTES // data.MINUTES_PER_TURN
        self.log = []               # one record per turn
        self.said = []              # every line spoken, in order
        self.max_prompt_tokens = 0
        for p in self.people.values():
            how = "did it" if p.id == "elena" else "saw it"
            p.sure.append(f"min 00: {data.OPENING} (you {how})")
            if p.id == data.CULPRIT:
                p.sure.append("You know where the can went: you ate it yourself in the night, and nobody saw.")
            p.just_now.append(data.OPENING)
            p.triggers.append("the count came up short in front of everyone")
            p.heard_question = False

    # ---------- who is where ----------
    def here(self, room, but=None):
        return [q for q in self.people.values() if q.room == room and q.id != but]

    def name(self, pid):
        return self.people[pid].name

    # ---------- what the rules allow ----------
    def options_for(self, p):
        opts = []
        others = self.here(p.room, but=p.id)
        room = data.ROOMS[p.room]
        opts.append(Option("silent", "stay put and say nothing", kind="silent"))
        if others:
            if not p.knows_culprit:
                opts.append(Option("ask_who", "ask everyone here who took the can", True, kind="ask"))
            # Once it has been admitted, it cannot be taken back: the one who admitted it no
            # longer denies it or blames anyone, and whoever heard it knows who it was.
            if p.heard_question and not p.confessed:
                opts.append(Option("deny", "deny taking it", True, kind="deny"))
            for q in others:
                if p.confessed or (p.knows_culprit and p.id != p.knows_culprit and q.id != p.knows_culprit):
                    continue
                opts.append(Option(f"accuse_{q.id}", f"accuse {q.name} of taking it", True,
                                   kind="accuse", target=q.id))
            if p.id == data.CULPRIT and not p.confessed:
                opts.append(Option("confess", "admit taking it", True, kind="confess"))
            for q in others:
                opts.append(Option(f"reassure_{q.id}", f"reassure {q.name}", True,
                                   kind="reassure", target=q.id))
            if len(others) > 1:
                opts.append(Option("reassure_all", "reassure everyone here", True, kind="reassure_all"))
            opts.append(Option("say_other", "say something else", True, kind="say"))
            for q in others:
                if q.activity["kind"] in ("searching", "walking"):
                    continue
                sitting = p.activity["kind"] == "sitting" and p.activity["with"] == q.id
                opts.append(Option(f"sit_{q.id}", ("keep sitting with " if sitting else "sit with ") + q.name,
                                   kind="sit", target=q.id))
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
        if p.room == "kitchen" and self.portions > 0:
            opts.append(Option("eat", "eat one of the portions", kind="eat"))
            if others:
                opts.append(Option("share", "share out what is left among everyone here", kind="share"))
        return opts

    def routine(self, p, opts):
        """No model: carry on with what they were doing, or stay put."""
        ids = {o.id for o in opts}
        if p.activity["kind"] == "searching" and "keep_searching" in ids:
            return "keep_searching"
        if p.activity["kind"] == "sitting" and f"sit_{p.activity['with']}" in ids:
            return f"sit_{p.activity['with']}"
        return "silent"

    # ---------- the prompt ----------
    def prompt_for(self, p, t, opts):
        s = p.sheet
        head = [
            f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; "
            f"Daniel, 25; Leo, 21; Mara, 17).",
            f"Who you are: {s['note']}",
            f"Temperament: {trait_words(s['traits'])}.",
            f"What matters to you: {', '.join(s['values'])}.",
            f"Your body: {hunger_words(p.hunger)}.",
            f"The house: {data.HOUSE}",
        ]
        now = [f"Now, minute {t * data.MINUTES_PER_TURN:02d}, you are in the {data.ROOMS[p.room]}."]
        others = self.here(p.room, but=p.id)
        if not others:
            now.append("- Nobody else is here.")
        for q in others:
            look = f" {q.name} looks {q.feeling}." if outward(q.feeling) and q.feeling_until >= t else ""
            now.append(f"- {q.name} is here, {q.activity['label']}.{look}")
        if p.room == "kitchen":
            now.append(f"- {self.portions} portion{'s' if self.portions != 1 else ''} on the shelf.")
        tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]

        back = list(p.backstory)
        morning = list(p.memory)
        pinned = ["What you are sure of this morning:"] + [f"- {x}" for x in p.sure]
        if p.said_lines:
            pinned += ["Your own last words this morning:"] + [f"- {x}" for x in p.said_lines[-3:]]
        cut = False
        while True:
            parts = head + ["What you remember from the days before:"] + [f"- {x}" for x in back]
            parts += pinned + ["What else happened this morning, most recent last:"]
            parts += (["- (earlier things, left out here)"] if cut else [])
            parts += [f"- {x}" for x in morning] or ([] if cut else ["- nothing else yet"])
            parts += now + tail
            text = "\n".join(parts)
            if estimate_tokens(SYSTEM + text) <= PROMPT_TOKEN_BUDGET or (not morning and not back):
                break
            cut = True
            if len(morning) > 8:
                morning.pop(0)
            elif len(back) > 4:
                back.pop(0)
            elif morning:
                morning.pop(0)
            else:
                back.pop(0)
        self.max_prompt_tokens = max(self.max_prompt_tokens, estimate_tokens(SYSTEM + text))
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
                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped}, None

    # ---------- one turn ----------
    def run(self):
        for t in range(self.turns):
            self.turn(t)
        return self

    def social_triggers(self, p, t):
        found = list(dict.fromkeys(p.triggers))
        for q in self.here(p.room, but=p.id):
            if outward(q.feeling) and q.feeling_until >= t:
                found.append(f"{q.name} looks {q.feeling}")
        return found

    def turn(self, t):
        minute = t * data.MINUTES_PER_TURN
        record = {"minute": minute, "decisions": [], "events": []}
        choices = []
        for pid in data.ORDER:
            p = self.people[pid]
            opts = self.options_for(p)
            triggers = self.social_triggers(p, t)
            d = {"person": pid, "triggers": triggers, "offered": len(opts)}
            if triggers:
                prompt = self.prompt_for(p, t, opts)
                text = self.oracle.ask(SYSTEM, prompt)
                choice, why = self.parse(text, opts)
                if choice:
                    d.update(mode="model", **choice)
                else:
                    d.update(mode="fallback", invalid=why, option=self.routine(p, opts), say=None)
            else:
                d.update(mode="routine", option=self.routine(p, opts), say=None)
            d["label"] = next(o.label for o in opts if o.id == d["option"])
            choices.append((p, next(o for o in opts if o.id == d["option"]), d))
            record["decisions"].append(d)

        # Everybody decided against the same moment; now it happens, in a fixed order.
        start_room = {p.id: p.room for p in self.people.values()}
        for p in self.people.values():
            p.just_now, p.triggers = [], []
        moves = []
        self._leaving = {p.id for p, opt, d in choices if opt.act["kind"] == "go"}
        for p, opt, d in choices:
            d["came_of_it"] = self.apply(p, opt, d, t, start_room, moves, record)
        record["rooms"] = {r: [(q.name, q.activity["label"]) for q in self.people.values()
                               if start_room[q.id] == r] for r in data.ROOMS}
        for p, to in moves:
            p.room = to
            p.activity = {"kind": "idle", "label": "just come in"}
        for p in self.people.values():
            p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
        record["portions"] = self.portions
        self.log.append(record)

    # ---------- making it happen ----------
    def perceive(self, q, minute, text, trigger=None, remember=True):
        q.just_now.append(text)
        if remember:
            q.memory.append(f"min {minute:02d}: {text}")
        if trigger:
            q.triggers.append(trigger)

    def witnesses(self, p, start_room):
        return [q for q in self.people.values() if q.id != p.id and start_room[q.id] == start_room[p.id]]

    def apply(self, p, opt, d, t, start_room, moves, record):
        minute = t * data.MINUTES_PER_TURN
        kind = opt.act["kind"]
        room = start_room[p.id]
        seen = self.witnesses(p, start_room)
        feel = f" You felt {d['feeling']}." if d.get("feeling") else ""
        if d["mode"] == "model" and outward(d["feeling"]):
            p.feeling, p.feeling_until = d["feeling"], t + FEELING_SHOWS_FOR_TURNS
            for q in seen:
                self.perceive(q, minute, f"{p.name} looks {d['feeling']}.", remember=False)
        elif d["mode"] == "model":
            p.feeling, p.feeling_until = d["feeling"], -1
        target = self.people[opt.act["target"]] if "target" in opt.act else None
        out = []

        if kind != "sit" and p.activity["kind"] == "sitting" and not (
                kind in ("reassure", "say", "ask", "deny", "accuse", "confess", "reassure_all")):
            p.activity = {"kind": "idle", "label": "standing"}

        if opt.speech or d.get("say"):
            words = d["say"]
            speech = {"ask": "asks who took it", "deny": "denies taking it",
                      "accuse": f"accuses {target.name if target else ''}", "confess": "admits taking it",
                      "reassure": f"reassures {target.name if target else ''}",
                      "reassure_all": "reassures everyone", "say": "says"}.get(kind, "says")
            self.said.append({"minute": minute, "room": data.ROOMS[room], "who": p.name,
                              "act": speech, "words": words})
            for q in seen:
                trig = f"{p.name} {speech}: \"{words}\""
                if kind == "accuse" and q is target:
                    trig = f"{p.name} accuses you: \"{words}\""
                self.perceive(q, minute, trig, trigger=trig)
                if kind in ("ask", "accuse"):
                    q.heard_question = True
                if kind == "confess":
                    q.knows_culprit = p.id
                    q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
                                  "(you heard it)")
            heard_through = [q for q in self.people.values() if start_room[q.id] != room
                             and room not in data.SOUNDPROOF and start_room[q.id] not in data.SOUNDPROOF]
            for q in heard_through:
                line = f"Voices from the {data.ROOMS[room]}"
                if line + "." not in q.just_now:
                    self.perceive(q, minute, line + ".", trigger=line)
            mine = {"ask": "asked who took it", "deny": "denied taking it",
                    "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
                    "reassure": f"reassured {target.name if target else ''}",
                    "reassure_all": "reassured everyone"}.get(kind, "said")
            p.memory.append(f"min {minute:02d}: you {mine}: \"{words}\".{feel}")
            p.said_lines.append(f"min {minute:02d}, you {mine}: \"{words}\"")
            if kind in ("ask", "accuse"):
                p.heard_question = True
            if kind == "confess":
                p.confessed = True
                p.sure.append(f"min {minute:02d}: you admitted aloud that you took the can"
                              + (f", in front of {', '.join(q.name for q in seen)}." if seen else "."))
            names = ", ".join(q.name for q in seen)
            out.append(f"said to {names}" if names else "said it to nobody")
            if heard_through:
                out.append("heard as voices by " + ", ".join(q.name for q in heard_through))
            if opt.speech:
                if p.activity["kind"] == "searching":
                    p.activity = {"kind": "idle", "label": "standing"}
                elif p.activity["kind"] == "idle":
                    p.activity = {"kind": "idle", "label": "talking"}
                return "; ".join(out) + "."

        if kind == "silent":
            p.activity = {"kind": "idle", "label": "staying put"}
            if d["mode"] == "model":
                p.memory.append(f"min {minute:02d}: you stayed where you were and said nothing.{feel}")
            return "stayed where they were" + (" (its line was dropped: silent means no words)"
                                               if d.get("dropped_line") else "") + "."
        if kind in ("search", "keep_searching"):
            if kind == "search":
                p.activity = {"kind": "searching", "label": f"searching the {data.ROOMS[room]}",
                              "until": t + 1}
                for q in seen:
                    self.perceive(q, minute, f"{p.name} starts going through the {data.ROOMS[room]}.")
                p.memory.append(f"min {minute:02d}: you started searching the {data.ROOMS[room]}.{feel}")
            if p.activity["until"] <= t:
                p.searched.add(room)
                p.activity = {"kind": "idle", "label": "standing"}
                p.sure.append(f"min {minute:02d}: you finished searching the {data.ROOMS[room]}: "
                              "no can, nothing out of place.")
                return "went through the room and found nothing."
            return "started going through the room." if kind == "search" else "carried on searching."
        if kind == "go":
            to = opt.act["to"]
            p.activity = {"kind": "walking", "label": f"leaving for the {data.ROOMS[to]}"}
            for q in seen:
                self.perceive(q, minute, f"{p.name} leaves for the {data.ROOMS[to]}.")
            for q in self.people.values():
                if start_room[q.id] == to and q.id != p.id:
                    self.perceive(q, minute, f"{p.name} comes into the {data.ROOMS[to]}.")
            moves.append((p, to))
            p.memory.append(f"min {minute:02d}: you went to the {data.ROOMS[to]}.{feel}")
            return f"went to the {data.ROOMS[to]}."
        if kind == "sit":
            if target.id in self._leaving:
                p.activity = {"kind": "idle", "label": "standing"}
                return f"meant to sit with {target.name}, who was leaving."
            new = not (p.activity["kind"] == "sitting" and p.activity["with"] == target.id)
            p.activity = {"kind": "sitting", "with": target.id, "label": f"sitting with {target.name}"}
            if new:
                for q in seen:
                    if q is target:
                        self.perceive(q, minute, f"{p.name} comes and sits with you.",
                                      trigger=f"{p.name} came to sit with you")
                    else:
                        self.perceive(q, minute, f"{p.name} sits with {target.name}.")
                p.memory.append(f"min {minute:02d}: you sat with {target.name}.{feel}")
                return f"sat with {target.name}."
            return f"stayed sitting with {target.name}."
        if kind == "eat":
            p.activity = {"kind": "idle", "label": "eating"}
            if self.portions <= 0:
                p.memory.append(f"min {minute:02d}: you reached for the shelf; it was empty.")
                return "reached for the shelf and found it empty."
            self.portions -= 1
            p.hunger = max(0.0, p.hunger - 0.4)
            p.eaten += 1
            for q in seen:
                trig = f"{p.name} eats one of the portions"
                self.perceive(q, minute, trig + ".", trigger=trig, remember=False)
                q.sure.append(f"min {minute:02d}: {p.name} ate one of the portions (you saw it).")
            p.sure.append(f"min {minute:02d}: you ate one of the portions. {self.portions} left.")
            record["events"].append(f"{p.name} ate a portion")
            return f"ate a portion; {self.portions} left."
        if kind == "share":
            p.activity = {"kind": "idle", "label": "sharing out the food"}
            if self.portions <= 0:
                return "went to share out the food and found the shelf empty."
            eaters = [p] + seen
            each = self.portions / len(eaters)
            names = ", ".join(q.name for q in eaters)
            for q in eaters:
                q.hunger = max(0.0, q.hunger - 0.4 * each)
                q.eaten += each
            n, self.portions = self.portions, 0
            for q in seen:
                trig = f"{p.name} shares out the last {n} portion{'s' if n != 1 else ''} between {names}"
                self.perceive(q, minute, trig + ".", trigger=trig, remember=False)
                q.sure.append(f"min {minute:02d}: {trig}; you had your part.")
            p.sure.append(f"min {minute:02d}: you shared out the last {n} portions between {names}.")
            record["events"].append(f"{p.name} shared out {n} portions between {names}")
            return f"shared out the last {n} portions between {names}."
        return ""
