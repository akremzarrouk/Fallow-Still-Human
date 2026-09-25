"""The rules layer. Keeps the house, each person's memory, and lists what each of them
may do. Asks the model only when something social has just happened to a person;
every other turn is settled here.

Within a turn, the people in a room act one after another: whoever was just spoken to
goes first, then whoever shows the strongest feeling, then an order drawn from the seed.
Each of them sees what was already said and done in the room this turn. A room's
conversation ends after a full turn with nothing new in it; after that only something
new there is a social moment.
"""
import json
import random
import re

import data
from talk import SPEECH, Conversations, Newness, act_of, aimed_at

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

# Feelings that reach the face, by how strongly they show. Others in the room see them,
# and someone who looks like this counts as upset nearby. Anything else (guilty, ashamed,
# anxious, tense...) stays inside and shows as 0.
SHOWN = {
    3: ("terrif", "panic", "hysteri", "frantic", "furious", "rage", "devastat", "desperat", "sob"),
    2: ("scared", "afraid", "fright", "angry", "anger", "hurt", "upset", "distress", "betray",
        "outrag", "humiliat", "cry", "tear", "shak", "wounded"),
    1: ("sad", "miserab"),
}
FEELING_SHOWS_FOR_TURNS = 3
PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,252 for an estimate of 1,250 before

KIND_DONE = {   # what a run of one kind of act looks like, told to the person who did it
    "ask": "asked who took the can", "deny": "denied taking it",
    "accuse": "accused someone of taking it", "confess": "admitted taking it",
    "reassure": "reassured someone", "say": "said something else",
    "silent": "stayed put and said nothing", "search": "searched", "go": "gone to another room",
    "sit": "sat with someone", "eat": "eaten", "share": "shared out the food",
}


def estimate_tokens(text):
    return int(len(text) / 3.6) + 1


def strength(feeling):
    f = (feeling or "").lower()
    s = max((level for level, stems in SHOWN.items() if any(x in f for x in stems)), default=0)
    if s and re.search(r"\b(deeply|very|extremely|utterly|so)\b", f):
        s += 1
    return s


def outward(feeling):
    return strength(feeling) > 0


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
        self.memory = []            # (minute, text) this morning, oldest first; trimmed to fit
        self.sure = []              # this morning's facts that are never trimmed
        self.said_lines = []        # their own words, oldest first
        self.triggers = []          # (text, is it new) social things since they last acted
        self.history = []           # one {"t", "kind", "seq"} per turn: what they did
        self.heard = []             # lines they heard: {"seq", "who", "kind", "target"}
        self.addressed = None       # the last line aimed at them since they last acted
        self.searched = set()
        self.knows_culprit = data.CULPRIT if pid == data.CULPRIT else None
        self.heard_question = False
        self.confessed = False
        self.eaten = 0.0


class Morning:
    def __init__(self, oracle, seed=0):
        self.oracle = oracle
        self.seed = seed
        self.people = {p: Person(p) for p in data.ORDER}
        self.portions = data.PORTIONS
        self.turns = data.MINUTES // data.MINUTES_PER_TURN
        self.log = []               # one record per turn
        self.said = []              # every line spoken, in order
        self.max_prompt_tokens = 0
        self.seq = 0                # counts acts, in the order they happen
        self.newness = Newness()
        self.convos = Conversations(data.ROOMS)
        self.present = None         # during a turn: room -> who is still in it
        self.so_far = None          # during a turn: room -> what was said and done in it
        self.arrivals = []          # (room, name) to count as new next turn
        self.transcript = {"seed": seed, "turns": []}
        self.convo_told = 0         # how much of the conversation log the turn records hold
        for p in self.people.values():
            how = "did it" if p.id == "elena" else "saw it"
            p.sure.append(f"min 00: {data.OPENING} (you {how})")
            if p.id == data.CULPRIT:
                p.sure.append("You know where the can went: you ate it yourself in the night, and nobody saw.")
            p.triggers.append(("the count came up short in front of everyone", True))
        self.convos.new_thing("kitchen", 0, "the count came up short")

    # ---------- who is where ----------
    def others_here(self, p):
        if self.present is not None:
            ids = self.present[p.room]
        else:
            ids = [q for q in data.ORDER if self.people[q].room == p.room]
        return [self.people[q] for q in ids if q != p.id]

    def talking(self, room):
        count = len(self.present[room]) if self.present is not None else \
            sum(q.room == room for q in self.people.values())
        return self.convos.active[room] and count >= 2

    def shown(self, q, t):
        return outward(q.feeling) and q.feeling_until >= t

    # ---------- what the rules allow ----------
    def repeating(self, p):
        """(kind, how many turns in a row) of their latest acts."""
        if not p.history:
            return None, 0
        kind, n = p.history[-1]["kind"], 0
        for h in reversed(p.history):
            if h["kind"] != kind:
                break
            n += 1
        return kind, n

    def options_for(self, p):
        opts = []
        others = self.others_here(p)
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
        # A speech act used three turns in a row is not offered a fourth time.
        kind, n = self.repeating(p)
        if kind in SPEECH and n >= 3:
            opts = [o for o in opts if act_of(o.id)[0] != kind]
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
    def pattern(self, p):
        """How many turns in a row they have done the same kind of act, and how the others
        answered them in that time (lines aimed at them or at everyone)."""
        kind, n = self.repeating(p)
        if not n:
            return []
        first = p.history[-n]["seq"]
        out = [f"What you have been doing: you have {KIND_DONE[kind]}, {n} turn{'s' if n > 1 else ''} in a row."]
        replies = {}
        for h in p.heard:
            if h["seq"] > first and h["who"] != p.id and h["target"] in (p.id, None):
                replies.setdefault(h["who"], []).append(h)
        if not replies:
            out.append("In that time nobody has said anything to you or to everyone.")
            return out
        parts, changed = [], []
        for who, hs in replies.items():
            name = self.people[who].name
            verbs = [self.heard_verb(h, p) for h in hs]
            parts.append(f"{name} {', then '.join(verbs)}")
            if len({v for v in verbs}) > 1:
                changed.append(name)
        out.append("In that time: " + "; ".join(parts) + ".")
        out.append(("Answered you differently from one time to the next: " + ", ".join(changed) + ".")
                   if changed else "Nobody answered you differently from one time to the next.")
        return out

    def heard_verb(self, h, listener):
        target = "you" if h["target"] == listener.id else None
        return {"ask": "asked who took the can", "deny": "denied taking it",
                "accuse": f"accused {target or 'someone'}", "confess": "admitted taking it",
                "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone"
                }.get(h["kind"], "spoke to everyone")

    def prompt_for(self, p, t, opts):
        s = p.sheet
        minute = t * data.MINUTES_PER_TURN
        calls = "; ".join(f"{self.people[q].name} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
        head = [
            f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; "
            f"Daniel, 25; Leo, 21; Mara, 17).",
            f"How you address them: {calls}.",
            f"Who you are: {s['note']}",
            f"Temperament: {trait_words(s['traits'])}.",
            f"What matters to you: {', '.join(s['values'])}.",
            f"Your body: {hunger_words(p.hunger)}.",
            f"The house: {data.HOUSE} {data.HOUSE_THINGS}",
        ]
        room = data.ROOMS[p.room]
        now = [f"Now, minute {minute:02d}, you are in the {room}."]
        others = self.others_here(p)
        if not others:
            now.append("- Nobody else is here.")
        for q in others:
            look = f" {q.name} looks {q.feeling}." if self.shown(q, t) else ""
            now.append(f"- {q.name} is here, {q.activity['label']}.{look}")
        if p.room == "kitchen":
            now.append(f"- {self.portions} portion{'s' if self.portions != 1 else ''} on the shelf.")
        so_far = self.so_far[p.room] if self.so_far is not None else []
        if so_far:
            now.append(f"Said and done in the {room} this turn, before you, in order:")
            now += [f"{i}. {x}" for i, x in enumerate(so_far, 1)]
        elif others:
            now.append(f"You are the first to act in the {room} this turn.")
        now += self.pattern(p)
        tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]

        back = list(p.backstory)
        morning = [f"min {m:02d}: {x}" for m, x in p.memory if m != minute]  # this turn is above
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
        self.transcript["final_rooms"] = {r: [q for q in data.ORDER if self.people[q].room == r]
                                          for r in data.ROOMS}
        return self

    def social_triggers(self, p, t):
        """What counts now: anything new; anything else only while the room is talking."""
        talking = self.talking(p.room)
        found = list(dict.fromkeys(text for text, new in p.triggers if new or talking))
        if talking:
            for q in self.others_here(p):
                if self.shown(q, t):
                    found.append(f"{q.name} looks {q.feeling}")
        return found

    def next_to_act(self, remaining, t, draw):
        """Who acts next in a room, and why them."""
        def key(pid):
            q = self.people[pid]
            a = q.addressed
            return (0 if a else 1, -(a["seq"] if a else 0), -strength(q.feeling) * self.shown(q, t), draw[pid])
        pid = min(remaining, key=key)
        q = self.people[pid]
        rest = [self.people[x] for x in remaining if x != pid]
        if q.addressed:
            how = "accused" if q.addressed["accused"] else "spoken to"
            return pid, f"just {how} by {self.people[q.addressed['who']].name}"
        if not rest:
            return pid, "the only one left to act here"
        mine = strength(q.feeling) * self.shown(q, t)
        if mine > max(strength(o.feeling) * self.shown(o, t) for o in rest):
            return pid, f"shows the strongest feeling here ({q.feeling})"
        return pid, "drawn by the seed among equals"

    def turn(self, t):
        minute = t * data.MINUTES_PER_TURN
        record = {"minute": minute, "decisions": [], "events": [], "convo": []}
        for room, name in self.arrivals:
            self.convos.new_thing(room, minute, f"{name} came in")
        self.arrivals = []
        start_room = {p.id: p.room for p in self.people.values()}
        self.present = {r: [q for q in data.ORDER if start_room[q] == r] for r in data.ROOMS}
        at_start = {r: len(v) for r, v in self.present.items()}
        self.so_far = {r: [] for r in data.ROOMS}
        tturn = {"minute": minute, "rooms": {r: list(v) for r, v in self.present.items()}, "acts": []}
        moves, voices = [], []
        for room in data.ROOMS:
            remaining = list(self.present[room])
            rng = random.Random(f"{self.seed}:{t}:{room}")
            draw = {q: rng.random() for q in data.ORDER}
            place = 0
            while remaining:
                pid, why = self.next_to_act(remaining, t, draw)
                remaining.remove(pid)
                place += 1
                p = self.people[pid]
                d = self.decide(p, t)
                d.update(room=room, place=place, order_reason=why)
                opt = d.pop("_opt")
                audience = [q.id for q in self.others_here(p)]
                d["came_of_it"] = self.apply(p, opt, d, t, moves, voices, record)
                record["decisions"].append(d)
                tturn["acts"].append({
                    "minute": minute, "who": pid, "room": room, "option": d["option"],
                    "words": d.get("say"), "audience": audience, "mode": d["mode"],
                    "decided_at": [minute, d["seq"]], "said_at": [minute, d["seq"]],
                    "came_of_it": d["came_of_it"], "new": d.get("new"), "new_why": d.get("new_why")})
        record["rooms"] = {r: [(q.name, q.activity["label"]) for q in self.people.values()
                               if start_room[q.id] == r] for r in data.ROOMS}

        for p, to in moves:
            p.room = to
            p.activity = {"kind": "idle", "label": "just come in"}
        # Voices carry to everyone who did not hear the words, wherever they are at the end of
        # the turn, never into or out of the bathroom. Only a new line is a social moment for
        # someone who hears it through a wall.
        for room, new, heard_it in voices:
            for q in self.people.values():
                if q.id in heard_it or q.room == room or data.SOUNDPROOF & {room, q.room}:
                    continue
                line = f"Voices from the {data.ROOMS[room]}"
                if (minute, line + ".") not in q.memory:
                    q.memory.append((minute, line + "."))
                if new:
                    q.triggers.append((line, True))
        for p, to in moves:
            there = [q for q in self.people.values() if q.room == to and q.id != p.id]
            for q in there:
                text = f"{p.name} comes into the {data.ROOMS[to]}"
                self.perceive(q, minute, text + ".", trigger=(text, True))
            if there:
                self.arrivals.append((to, p.name))
        at_end = {r: sum(q.room == r for q in self.people.values()) for r in data.ROOMS}
        self.convos.end_turn(minute + data.MINUTES_PER_TURN, at_start, at_end)
        record["convo"] = self.convos.log[self.convo_told:]
        self.convo_told = len(self.convos.log)
        self.present, self.so_far = None, None
        for p in self.people.values():
            p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
        record["portions"] = self.portions
        self.log.append(record)
        self.transcript["turns"].append(tturn)

    def decide(self, p, t):
        opts = self.options_for(p)
        triggers = self.social_triggers(p, t)
        p.triggers = []
        kind, n = self.repeating(p)
        d = {"person": p.id, "triggers": triggers, "offered": len(opts),
             "held_back": kind if kind in SPEECH and n >= 3 else None}
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
        opt = next(o for o in opts if o.id == d["option"])
        d["label"] = opt.label
        d["_opt"] = opt
        return d

    # ---------- making it happen ----------
    def perceive(self, q, minute, text, trigger=None, remember=True):
        if remember:
            q.memory.append((minute, text))
        if trigger:
            q.triggers.append(trigger)

    def line_text(self, p, kind, target, words, listener, while_doing=None):
        aimed = ("you" if listener is not None and target is listener else target.name) if target else None
        if kind == "ask":
            gist = f"{p.name} asks everyone who took the can"
        elif kind == "deny":
            gist = f"{p.name} denies taking it, to everyone"
        elif kind == "accuse":
            gist = f"{p.name} accuses {aimed} of taking it"
        elif kind == "confess":
            gist = f"{p.name} admits taking it, to everyone"
        elif kind == "reassure":
            gist = f"{p.name} reassures {aimed or 'everyone'}"
        elif while_doing:
            gist = f"{p.name} says to everyone, while {while_doing}"
        else:
            gist = f"{p.name} says to everyone"
        return f"{gist}: \"{words}\""

    def apply(self, p, opt, d, t, moves, voices, record):
        minute = t * data.MINUTES_PER_TURN
        self.seq += 1
        d["seq"] = self.seq
        kind, _ = act_of(opt.id)
        room = p.room
        seen = self.others_here(p)
        feel = f" You felt {d['feeling']}." if d.get("feeling") else ""
        if d["mode"] == "model":
            p.feeling = d["feeling"]
            p.feeling_until = t + FEELING_SHOWS_FOR_TURNS if outward(d["feeling"]) else -1
        target_id = aimed_at(opt.id) or (opt.act.get("target") if kind == "sit" else None)
        target = self.people[target_id] if target_id else None
        p.history.append({"t": t, "kind": kind, "seq": self.seq})
        p.addressed = None
        so_far = self.so_far[room]
        out = []

        if kind != "sit" and p.activity["kind"] == "sitting" and kind not in SPEECH:
            p.activity = {"kind": "idle", "label": "standing"}

        words = d.get("say")
        if words:
            doing = {"go": f"leaving for the {data.ROOMS.get(opt.act.get('to'), '')}",
                     "search": "searching", "sit": f"sitting down with {target.name if target else ''}",
                     "eat": "eating", "share": "sharing out the food"}.get(kind)
            spoken_kind = kind if kind in SPEECH else "say"
            aimed = aimed_at(opt.id)
            new, why = self.newness.line(p.id, opt.id, [q.id for q in seen])
            d["new"], d["new_why"] = new, why
            if new:
                self.convos.new_thing(room, minute, f"{p.name}: {why}")
            self.said.append({"minute": minute, "room": data.ROOMS[room], "who": p.name,
                              "to": target.name if aimed else "everyone",
                              "text": self.line_text(p, spoken_kind, target if aimed else None, words, None,
                                                     None if opt.speech else doing),
                              "words": words, "new": new, "why": why})
            so_far.append(self.line_text(p, spoken_kind, target if aimed else None, words, None,
                                         None if opt.speech else doing))
            for q in seen:
                heard = self.line_text(p, spoken_kind, target if aimed else None, words, q,
                                       None if opt.speech else doing)
                self.perceive(q, minute, heard, trigger=(heard, new))
                q.heard.append({"seq": self.seq, "who": p.id, "kind": spoken_kind,
                                "target": target_id if aimed else None})
                if aimed and q is target:
                    q.addressed = {"seq": self.seq, "who": p.id, "accused": kind == "accuse"}
                if kind in ("ask", "accuse"):
                    q.heard_question = True
                if kind == "confess":
                    q.knows_culprit = p.id
                    q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
                                  "(you heard it)")
            voices.append((room, new, {p.id} | {q.id for q in seen}))
            mine = {"ask": "asked who took it", "deny": "denied taking it",
                    "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
                    "reassure": f"reassured {target.name if aimed else 'everyone'}"}.get(kind, "said")
            p.memory.append((minute, f"you {mine}: \"{words}\".{feel}"))
            p.said_lines.append(f"min {minute:02d}, you {mine}: \"{words}\"")
            if kind in ("ask", "accuse"):
                p.heard_question = True
            if kind == "confess":
                p.confessed = True
                p.sure.append(f"min {minute:02d}: you admitted aloud that you took the can"
                              + (f", in front of {', '.join(q.name for q in seen)}." if seen else "."))
            names = ", ".join(q.name for q in seen)
            out.append(f"said to {names}" if names else "said it to nobody")
            if opt.speech:
                if p.activity["kind"] == "searching":
                    p.activity = {"kind": "idle", "label": "standing"}
                elif p.activity["kind"] == "idle":
                    p.activity = {"kind": "idle", "label": "talking"}
                return "; ".join(out) + "."

        def fact(why, trig):
            """Something new that the others in the room saw."""
            if seen:
                self.convos.new_thing(room, minute, why)
                d["new_fact"] = why
                for q in seen:
                    self.perceive(q, minute, trig + ".", trigger=(trig, True), remember=False)

        if kind == "silent":
            p.activity = {"kind": "idle", "label": "staying put"}
            so_far.append(f"{p.name} stays put and says nothing.")
            if d["mode"] == "model":
                p.memory.append((minute, f"you stayed where you were and said nothing.{feel}"))
            return "stayed where they were" + (" (its line was dropped: silent means no words)"
                                               if d.get("dropped_line") else "") + "."
        if kind == "search":
            if opt.id == "search":
                p.activity = {"kind": "searching", "label": f"searching the {data.ROOMS[room]}",
                              "until": t + 1}
                so_far.append(f"{p.name} starts going through the {data.ROOMS[room]}.")
                for q in seen:
                    self.perceive(q, minute, f"{p.name} starts going through the {data.ROOMS[room]}.")
                p.memory.append((minute, f"you started searching the {data.ROOMS[room]}.{feel}"))
            else:
                so_far.append(f"{p.name} carries on searching the {data.ROOMS[room]}.")
            if p.activity["until"] <= t:
                p.searched.add(room)
                p.activity = {"kind": "idle", "label": "standing"}
                p.sure.append(f"min {minute:02d}: you finished searching the {data.ROOMS[room]}: "
                              "no can, nothing out of place.")
                fact(f"{p.name} finished searching the {data.ROOMS[room]} and found nothing",
                     f"{p.name} finishes going through the {data.ROOMS[room]}: no can, nothing out of place")
                return "went through the room and found nothing."
            return "started going through the room." if opt.id == "search" else "carried on searching."
        if kind == "go":
            to = opt.act["to"]
            p.activity = {"kind": "walking", "label": f"leaving for the {data.ROOMS[to]}"}
            so_far.append(f"{p.name} leaves for the {data.ROOMS[to]}.")
            for q in seen:
                self.perceive(q, minute, f"{p.name} leaves for the {data.ROOMS[to]}.")
            self.present[room].remove(p.id)
            moves.append((p, to))
            p.memory.append((minute, f"you went to the {data.ROOMS[to]}.{feel}"))
            return f"went to the {data.ROOMS[to]}."
        if kind == "sit":
            new = not (p.activity["kind"] == "sitting" and p.activity["with"] == target.id)
            p.activity = {"kind": "sitting", "with": target.id, "label": f"sitting with {target.name}"}
            if new:
                so_far.append(f"{p.name} sits down with {target.name}.")
                for q in seen:
                    if q is target:
                        self.perceive(q, minute, f"{p.name} comes and sits with you.",
                                      trigger=(f"{p.name} came to sit with you", False))
                    else:
                        self.perceive(q, minute, f"{p.name} sits with {target.name}.")
                p.memory.append((minute, f"you sat with {target.name}.{feel}"))
                return f"sat with {target.name}."
            so_far.append(f"{p.name} stays sitting with {target.name}.")
            return f"stayed sitting with {target.name}."
        if kind == "eat":
            p.activity = {"kind": "idle", "label": "eating"}
            if self.portions <= 0:
                p.memory.append((minute, "you reached for the shelf; it was empty."))
                so_far.append(f"{p.name} reaches for the shelf; it is empty.")
                return "reached for the shelf and found it empty."
            self.portions -= 1
            p.hunger = max(0.0, p.hunger - 0.4)
            p.eaten += 1
            so_far.append(f"{p.name} eats one of the portions.")
            for q in seen:
                q.sure.append(f"min {minute:02d}: {p.name} ate one of the portions (you saw it).")
            fact(f"{p.name} ate one of the portions", f"{p.name} eats one of the portions")
            p.sure.append(f"min {minute:02d}: you ate one of the portions. {self.portions} left.")
            record["events"].append(f"{p.name} ate a portion")
            return f"ate a portion; {self.portions} left."
        if kind == "share":
            p.activity = {"kind": "idle", "label": "sharing out the food"}
            if self.portions <= 0:
                so_far.append(f"{p.name} goes to share out the food; the shelf is empty.")
                return "went to share out the food and found the shelf empty."
            eaters = [p] + seen
            each = self.portions / len(eaters)
            names = ", ".join(q.name for q in eaters)
            for q in eaters:
                q.hunger = max(0.0, q.hunger - 0.4 * each)
                q.eaten += each
            n, self.portions = self.portions, 0
            trig = f"{p.name} shares out the last {n} portion{'s' if n != 1 else ''} between {names}"
            so_far.append(trig + ".")
            for q in seen:
                q.sure.append(f"min {minute:02d}: {trig}; you had your part.")
            fact(f"{p.name} shared out the food", trig)
            p.sure.append(f"min {minute:02d}: you shared out the last {n} portions between {names}.")
            record["events"].append(f"{p.name} shared out {n} portions between {names}")
            return f"shared out the last {n} portions between {names}."
        return ""
