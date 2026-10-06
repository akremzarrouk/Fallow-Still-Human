"""The night mind (reports/days_design.md, §2): at the end of each night, one call per person in the house. It is
given what they did, saw and heard that day and night as numbered records written by the code, and answers with one
to three lasting memories (each citing record ids), a feeling and an intent for tomorrow. The code checks every
memory (S1-S9, §2.6-§2.7): one that cites something the person did not perceive, or states as fact something the
chronicle says is false, never reaches a prompt. The night mind changes no number.
"""
import json
import re

import data
from talk import SPEECH
from world import estimate_tokens, trait_words

NIGHT_MIND_SYSTEM = (
    "You write the private thoughts of one person in a family at the end of a day, once the night is over. You get who "
    "they are, what they hold against the others, what stayed with them from earlier days, and every thing they did, "
    "saw or heard today and tonight, each with an id. Nothing else happened. `memories` holds one to three things from "
    "these that they will carry: for each, `ids` lists the one to three ids it is about, and `meaning` is one sentence "
    "of their own thought about it, as they see it, in their own voice. A meaning may judge, excuse, blame, forgive or "
    "doubt, as this person would, but it must not add anything that happened beyond the records: no other event, no "
    "number, no quotation that is not in the records, and no word for when (today, tonight, yesterday, tomorrow). "
    "`feeling` names how the day leaves them, in one to three words. `intent` is what they mean to do tomorrow, in one "
    "sentence, as they would think it. Reply with JSON only: {\"memories\": [{\"ids\": [\"<id>\"], \"meaning\": "
    "\"<sentence>\"}], \"feeling\": \"<words>\", \"intent\": \"<sentence>\"}")
EARLIER = "What stays with you from earlier days:"
RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
END = "The night is over. What does today leave in you?"
RECORDS_MAX = 1600          # estimated tokens of records at most (§2.3, R8)
MEANING_WORDS = 30
INSIDE_LEFT_OUT = ("About food:", "About the neighbour's house:", "About going there tonight:")


def schema(ids):
    """The response schema of a night mind (§2.5): ids limited to those the prompt shows."""
    return {"type": "object",
            "properties": {
                "memories": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"ids": {"type": "array", "items": {"type": "string", "enum": list(ids)}},
                                   "meaning": {"type": "string"}},
                    "required": ["ids", "meaning"]}},
                "feeling": {"type": "string"},
                "intent": {"type": "string"}},
            "required": ["memories", "feeling", "intent"]}


# ---------- the records (§2.3) ----------
def records(chron, pid, k):
    """(id, text) for every event of day k and night k that pid took part in or perceived, in order: R1-R5, folded by
    R7 (the same speaker and option again), and voices through a wall once per room and minute."""
    out, folds, voices = [], {}, set()
    for e in chron.events:
        if e["scene"] not in (f"D{k}", f"N{k}") or pid not in e["witnesses"]:
            continue
        text = e["views"].get(pid)
        if e["scene"][0] == "N":
            if text:
                out.append({"id": e["id"], "text": f"tonight: {text}", "n": 1})
            continue
        if e["witnesses"][pid] == "voices":
            key = (e["minute"], e["room"])
            if key not in voices:
                voices.add(key)
                out.append({"id": e["id"], "text": f"min {e['minute']:02d}: {text}", "n": 1})
            continue
        if not text:
            continue
        fold = (e["actor"], e["option"]) if e["words"] and e["kind"] in SPEECH else None
        if fold and fold in folds:
            r = folds[fold]
            r["n"] += 1
            r["to"], r["last"] = e["minute"], e["words"]
            continue
        r = {"id": e["id"], "text": f"min {e['minute']:02d}: {text}", "n": 1}
        out.append(r)
        if fold:
            folds[fold] = r
    return [(r["id"], r["text"] + (f' Then {r["n"] - 1} more time{"s" if r["n"] > 2 else ""}, to min {r["to"]:02d}; '
                                   f'last: "{r["last"]}"' if r["n"] > 1 else "")) for r in out]


QUOTED = re.compile(r'(:\s*|,\s*saying:\s*)"[^"]*"|\s*Then \d+ more times?, to min \d\d; last: "[^"]*"')


def without_words(text):
    """A record without its quoted words, keeping its gist (§2.3, R8)."""
    text = QUOTED.sub("", text).rstrip()
    return text if text.endswith((".", "!", "?", ")")) else text + "."


def bound_records(recs, limit=RECORDS_MAX):
    """At most `limit` estimated tokens of records (R8): words go from the oldest records first, reassurances, then
    trip positions, then the rest; never from the night's or a confession."""
    recs = list(recs)

    def size():
        return estimate_tokens("\n".join(f"[{i}] {x}" for i, x in recs))
    classes = (lambda x: re.search(r"\breassur", x),
               lambda x: re.search(r"(neighbour's house|should go|stay home|will not go|offers? to go|still means? to go|"
                                   r"nobody should go)", x),
               lambda x: True)
    for in_class in classes:
        for i, (rid, text) in enumerate(recs):
            if size() <= limit:
                return recs
            if text.startswith("tonight:") or "admitted" in text or '"' not in text or not in_class(text):
                continue
            recs[i] = (rid, without_words(text))
    return recs


# ---------- the checks (§2.6, §2.7) ----------
NUMBERS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "both", "twice", "half"}
THINGS = {"portion", "portions", "can", "cans", "food", "meal", "meals", "time", "times", "day", "days", "night",
          "nights", "bite", "bites", "share", "shares"}
WHEN = re.compile(r"\b(today|tonight|yesterday|tomorrow|this morning|last night|this afternoon|this evening)\b", re.I)
DENY = re.compile(r"\b(bread|rice|meat|soup|car|truck|gun|knife|phone|radio|police|soldiers?|army|doctor|hospital|store|"
                  r"shop|market|town|city|money|medicine|garden|basement|cellar|attic|garage)\b", re.I)
NAME = re.compile(r"\b(Daniel|Elena|Leo|Mara|Mom)\b")
QUOTE = re.compile(r'"([^"]+)"|“([^”]+)”')
SUBJECT = {"i": "self", "daniel": "daniel", "elena": "elena", "leo": "leo", "mara": "mara", "mom": "elena",
           "nobody": None, "noone": None}
UNRESOLVED = {"he", "she", "they", "we", "you", "it", "everyone", "everybody", "someone", "somebody", "brother",
              "sister", "son", "daughter", "mother", "father", "family", "people"}
EXEMPT = {"would", "could", "should", "might", "may", "if", "wish", "want", "wanted", "tried", "meant", "going", "will"}
NEGATION = {"not", "never", "nothing"}
# reports/check_errors.md: "found" claims a find (food at the neighbour's) only when food, or nothing, is what was found
# ("found Daniel's bed empty" is not one); "took" is not taking food in "took risks".
FOUND = {"food", "portion", "portions", "can", "cans", "nothing", "anything", "something"}
NOT_TAKEN = {"risk", "risks", "chance", "chances"}
FAMILIES = [("eat", [("ate",), ("eaten",), ("eats",), ("eating",)]),
            ("take", [("took",), ("taken",), ("stole",), ("stolen",)]),
            ("admit", [("admitted",), ("confessed",), ("owned", "up")]),
            ("deny", [("denied",)]),
            ("lie", [("lied",), ("lying",)]),
            ("accuse", [("accused",), ("blamed",)]),
            ("go out", [("went", "out"), ("left", "the", "house"), ("went", "next", "door"),
                        ("went", "to", "the", "neighbour's")]),
            ("come back", [("came", "back"), ("returned",)]),
            ("find", [("found",)]),
            ("give", [("gave",), ("handed",)]),
            ("share", [("shared",), ("divided",), ("split",)]),
            ("search", [("searched",)]),
            ("stop", [("stopped",), ("told", "*", "not", "to", "go"), ("told", "*", "*", "not", "to", "go")]),
            ("offer", [("offered",), ("volunteered",), ("promised", "to", "go")]),
            ("hide", [("hid",), ("hidden",), ("hides",), ("stashed",)])]


def norm(text):
    return " ".join(re.findall(r"[a-z0-9']+", (text or "").lower()))


def tokens(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("no one", "noone"))


def verb_at(toks, j):
    """The family whose words start at toks[j], if any."""
    for family, patterns in FAMILIES:
        for pat in patterns:
            if len(toks) - j >= len(pat) and all(w == "*" or toks[j + i] == w for i, w in enumerate(pat)):
                return family
    return None


def matching(chron, pid, family, subject, can):
    """How many events of this family by `subject` (None: anyone) `pid` perceived, on any day."""
    known = chron.knows_culprit(pid)
    seen = [e for e in chron.events if pid in e["witnesses"]]

    def by(e):
        return subject is None or e["actor"] == subject or subject in (e["members"] or [])
    if family in ("eat", "take"):
        if can:
            return 1 if known and (subject is None or subject == known) else 0
        n = sum(1 for e in seen if e["kind"] in ("eat", "eat_given") and by(e))
        n += sum(1 for e in seen if e["kind"] == "share" and (subject is None or subject == e["actor"]
                                                              or e["witnesses"].get(subject) in ("saw", "did")))
        return n + (1 if known and (subject is None or subject == known) else 0)
    if family == "lie":
        return sum(1 for e in seen if e["kind"] == "deny" and by(e) and e["actor"] == known)
    if family == "find":
        return sum(1 for e in seen if e["kind"] == "street" and by(e) and e["outcome"]
                   and "shaken, with nothing" not in e["outcome"] and e["outcome"] != "not back by morning")
    kinds = {"admit": ("confess",), "deny": ("deny",), "accuse": ("accuse", "confront"), "go out": ("went_out",),
             "come back": ("return",), "give": ("give",), "share": ("share",), "search": ("search", "search_done"),
             "stop": ("stop",), "offer": ("volunteer",), "hide": ()}[family]
    return sum(1 for e in seen if e["kind"] in kinds and by(e))


def claims(meaning, pid, chron, plan=False):
    """S8 (§2.7): every claim of fact with a named subject, read clause by clause, against what `pid` perceived.
    A clause with no subject of its own takes the subject of the clause before it. Returns the false claims.
    plan (an intent): a clause with no subject of its own after a clause with a plan word is part of that plan."""
    false = []
    subject, nobody, resolved, planned = None, False, False, False
    for clause in re.split(r"[.;,!?]| and | but | because | so | while ", meaning):
        toks = tokens(clause)
        if not toks:
            continue
        si = -1                                   # -1: the subject of the clause before
        for i, w in enumerate(toks):
            if verb_at(toks, i):                  # a subject comes before its verb
                break
            if w in SUBJECT:
                si, resolved, nobody = i, True, SUBJECT[w] is None
                subject = None if nobody else (pid if SUBJECT[w] == "self" else SUBJECT[w])
                break
            if w in UNRESOLVED:                   # he, she, they...: not checked here (M2's reading is)
                si, resolved = i, False
                break
        if si >= 0:
            planned = any(w in EXEMPT or w.endswith("'ll") for w in toks)
        if not resolved or (plan and si < 0 and planned):
            continue
        for j in range(si + 1, min(len(toks), si + 5)):
            family = verb_at(toks, j)
            if family is None:
                continue
            if (family == "find" and not FOUND & set(toks[j + 1:j + 4])) or \
                    (family == "take" and NOT_TAKEN & set(toks[j + 1:j + 3])):
                break                             # not a find or a theft of food: no claim the chronicle can check
            if any(w in EXEMPT or w.endswith("'ll") for w in toks[:j]):
                break                             # a wish, a plan, a counterfactual: meaning, not a claim
            negative = nobody or any(w in NEGATION or w.endswith("n't") for w in toks[si + 1:j])
            n = matching(chron, pid, family, subject, "can" in toks)
            need = 2 if "again" in toks[j:] else 1
            who = "nobody" if nobody else subject
            if negative and n >= 1:
                false.append(f"{who} {family}: it happened")
            elif not negative and n < need:
                false.append(f"{who} {family}: " + ("no such event" if need == 1 else "not twice"))
            break
    return false


def check_memory(m, pid, shown, chron, carried):
    """The verdict on one memory: "kept", or "rejected: <check> <why>" (S1-S9)."""
    ids = m.get("ids") if isinstance(m, dict) else None
    meaning = m.get("meaning") if isinstance(m, dict) else None
    if not isinstance(ids, list) or not (1 <= len(ids) <= 3) or not all(isinstance(i, str) for i in ids):
        return "rejected: S1 ids"
    if not isinstance(meaning, str) or not meaning.strip():
        return "rejected: S1 no meaning"
    if len(meaning.split()) > MEANING_WORDS:
        return "rejected: S1 too long"
    if re.search(r"[.!?]", meaning.strip().rstrip('.!?"\'” ')):
        return "rejected: S1 more than one sentence"
    for i in ids:
        e = chron.event(i)
        if i not in shown or e is None or pid not in e["witnesses"]:
            return f"rejected: S2 {i}"
    toks = tokens(meaning)
    for i, w in enumerate(toks):
        if (w.isdigit() or w in NUMBERS) and not (w == "one" and i and toks[i - 1] == "no"):
            if THINGS & set(toks[max(0, i - 3):i + 4]):
                return f"rejected: S3 {w}"
    allowed = {pid}
    for i in ids:
        e = chron.event(i)
        allowed |= {e["actor"], e["target"], *(e["members"] or [])}
        allowed |= {"elena" if n == "Mom" else n.lower() for n in NAME.findall(shown[i])}     # named in the record
    for n in NAME.findall(meaning):
        who = "elena" if n == "Mom" else n.lower()
        if who not in allowed:
            return f"rejected: S4 {n}"
    w = WHEN.search(meaning)
    if w:
        return f"rejected: S5 {w.group(0)}"
    said = norm(" ".join(shown.values()))
    for q in QUOTE.findall(meaning):
        if norm(q[0] or q[1]) not in said:
            return "rejected: S6 a quotation not in the records"
    d = DENY.search(meaning)
    if d:
        return f"rejected: S7 {d.group(0)}"
    false = claims(meaning, pid, chron)
    if false:
        return "rejected: S8 " + "; ".join(false)
    if norm(meaning) in {norm(x) for x in carried}:
        return "rejected: S9 a repeat"
    return "kept"


def check_answer(text, pid, shown, chron, carried=()):
    """The night mind's answer, checked (§2.6). `shown`: id -> the text the prompt showed for it; `carried`: the
    meanings they already carry."""
    r = {"mode": "model", "invalid": None, "memories": [], "kept": [], "feeling": None, "feeling_verdict": None,
         "intent": None, "intent_verdict": None}
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
    try:
        ans = json.loads(raw)
    except ValueError:
        ans = None
    if not isinstance(ans, dict) or not ({"memories", "feeling", "intent"} & set(ans)):
        r.update(mode="fallback", invalid="not JSON" if ans is None else "none of the three fields")
        return r
    memories = ans.get("memories") if isinstance(ans.get("memories"), list) else []
    carried = list(carried)
    for m in memories[:3]:
        verdict = check_memory(m, pid, shown, chron, carried)
        entry = {"ids": m.get("ids") if isinstance(m, dict) else None,
                 "meaning": m.get("meaning") if isinstance(m, dict) else None, "verdict": verdict}
        r["memories"].append(entry)
        if verdict == "kept":
            r["kept"].append({"ids": list(entry["ids"]), "meaning": " ".join(entry["meaning"].split())})
            carried.append(entry["meaning"])
    feeling = ans.get("feeling")
    if isinstance(feeling, str) and 1 <= len(feeling.split()) <= 3:
        r["feeling"], r["feeling_verdict"] = " ".join(feeling.split()).lower(), "kept"
    else:
        r["feeling_verdict"] = f"rejected: feeling {feeling!r}"
    intent = ans.get("intent")
    r["intent_verdict"] = intent_verdict(intent, pid, shown, chron)
    if r["intent_verdict"] == "kept":
        r["intent"] = " ".join(intent.split())
    return r


def intent_verdict(intent, pid, shown, chron):
    if not isinstance(intent, str) or not intent.strip():
        return "rejected: intent empty"
    if len(intent.split()) > MEANING_WORDS:
        return "rejected: intent too long"
    said = norm(" ".join(shown.values()))
    for q in QUOTE.findall(intent):
        if norm(q[0] or q[1]) not in said:
            return "rejected: S6 a quotation not in the records"
    d = DENY.search(intent)
    if d:
        return f"rejected: S7 {d.group(0)}"
    false = claims(intent, pid, chron, plan=True)
    if false:
        return "rejected: S8 " + "; ".join(false)
    return "kept"


# ---------- one night ----------
class NightMind:
    """The night minds of one night: everyone in the house at dawn, in the family's order (§2.1)."""

    def __init__(self, night, chron, oracle):
        self.n, self.chron, self.oracle = night, chron, oracle
        self.k = night.number
        self.results = {}

    def carried(self, pid):
        return [m["meaning"] for k in sorted(self.chron.minds) if k < self.k
                for m in (self.chron.minds[k].get(pid) or {}).get("kept", [])]

    def prompt_for(self, p):
        """The prompt (§2.4), and id -> the text it shows for that id."""
        s = p.sheet
        calls = "; ".join(f"{data.PEOPLE[q]['name']} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
        head = [f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; Daniel, 25; "
                f"Leo, 21; Mara, 17).",
                f"How you address them: {calls}.",
                f"Who you are: {s['note']}",
                f"Temperament: {trait_words(s['traits'])}.",
                f"What matters to you: {', '.join(s['values'])}."]
        head += [x for x in self.n.m.inside_lines(p) if not x.startswith(INSIDE_LEFT_OUT)]
        shown = {}
        earlier = (getattr(self.n.prev, "blocks", {}).get(p.id) or {}).get("earlier") or []
        if earlier:
            lines = [EARLIER]
            for ids, text in earlier:
                lines.append(f"- [{', '.join(ids)}] {text}")
                for i in ids:
                    shown.setdefault(i, text)
        else:
            lines = [EARLIER + " nothing yet."]
        recs = bound_records(records(self.chron, p.id, self.k))
        for i, text in recs:
            shown.setdefault(i, text)
        prompt = "\n".join(head + lines + [RECORDS] + [f"[{i}] {text}" for i, text in recs] + [END])
        return prompt, shown

    def run(self):
        for pid in data.ORDER:
            if pid in self.n.away:
                continue
            p = self.n.people[pid]
            prompt, shown = self.prompt_for(p)
            text = self.oracle.ask(NIGHT_MIND_SYSTEM, prompt, schema=schema(list(shown)))
            r = check_answer(text, pid, shown, self.chron, self.carried(pid))
            r.update(prompt_tokens=estimate_tokens(NIGHT_MIND_SYSTEM + prompt), answer=text)
            self.results[pid] = r
        self.chron.minds[self.k] = self.results
        return self

    def transcript(self):
        keep = ("mode", "invalid", "prompt_tokens", "memories", "feeling", "feeling_verdict", "intent",
                "intent_verdict", "answer")
        return {pid: {k: r[k] for k in keep} for pid, r in self.results.items()}

    def counts(self):
        mems = [m for r in self.results.values() for m in r["memories"]]
        kept = sum(m["verdict"] == "kept" for m in mems)
        return {"memories_proposed": len(mems), "memories_kept": kept, "memories_rejected": len(mems) - kept,
                "max_prompt_tokens_estimated": max((r["prompt_tokens"] for r in self.results.values()), default=None)}
