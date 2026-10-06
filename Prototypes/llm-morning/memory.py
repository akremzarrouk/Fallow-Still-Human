"""What each morning carries of the days before (reports/days_design.md, §3): block A (yesterday's facts, written by
night.py), block B (last night's thoughts, from the night mind), block C (the earlier days: standing matters and one
line per person, by a fixed weight table), and the one bound the three share.
"""
import data
from chronicle import gist
from world import NAMES, day_index, estimate_tokens, when_words

MEMORY_MAX = 560            # estimated tokens of A, B and C together (§3.4)
B_HEAD = "What yesterday left in you (your own thoughts, last night):"
C_HEAD = "What stays with you from earlier days:"

# §3.3's table C2, by the line's key: how heavy each kind of event is. The amendment (reports/days_impl.md): every
# kind act between two people that the rules have, at weight 3. world.py has two: `reassure_<q>` and `sit_<q>`.
# (`give_<q>` was already in the table at 3; `reassure_all` is to everyone, not between two people.)
KIND_ACTS = ("reassure", "sit")
WEIGHT = {"confess": 5, "eat": 4, "went_out": 4, "accuse": 3, "give": 3, "share": 3, "reassure": 3, "sit": 3,
          "stop": 2, "confront": 2, "accuse_other": 2}
COUNTED = ("accuse", "accuse_other", "confront", "reassure", "sit")     # repeats are counted, not "again"
TIMES = {1: "", 2: " twice", 3: " three times"}


def times(n):
    return TIMES.get(n, f" {n} times")


def cap(text):
    return text[0].upper() + text[1:]


# ---------- B ----------
def b_items(result, chron, pid):
    """(ids, line without "- ") for each kept memory of last night (§3.2)."""
    out = []
    for m in (result or {}).get("kept", []):
        names = [gist(chron.event(i), pid) for i in m["ids"][:2] if chron.event(i)]
        out.append((list(m["ids"]), f'About {" and ".join(names)}: "{m["meaning"]}"'))
    return out


def block_b(result, chron, pid):
    """Block B: last night's kept memories, then the intent and the feeling, in their own words (§3.2)."""
    if not result:
        return []
    lines = [f"- {line}" for _, line in b_items(result, chron, pid)]
    if result.get("intent"):
        lines.append(f'- You meant to: "{result["intent"]}"')
    if result.get("feeling"):
        lines.append(f"- How it left you: {result['feeling']}.")
    return [B_HEAD] + lines if lines else []


# ---------- C ----------
def scene_key(scene):
    """(k, 0 for a day, 1 for its night): the order scenes happened in."""
    return int(scene[1:]), 0 if scene[0] == "D" else 1


def scene_when(scene, day):
    return when_words((scene[0], int(scene[1:])), day)


def block_c(chron, pid, day, away=()):
    """Block C for `pid` on the morning of house day `day` (§3.3): from day `day` - 2 and before, at most two standing
    matters, then one line for each person, themself included, each with at most one older thought. Each item is
    {"line", "ids", "weight", "standing", "self", "order", "thought"}."""
    today = day_index(day)
    old = [e for e in chron.events
           if e["scene"][0] in "DN" and scene_key(e["scene"])[0] <= today - 2 and pid in e["witnesses"]]
    items = []
    # C1: standing matters.
    known = chron.knows_culprit(pid)
    if today >= 3 and known is None and pid != chron.culprit:
        when = cap(when_words(("D", 1), day))
        count = next((e for e in chron.events if e["scene"] == "D1" and e["kind"] == "opening"), None)
        line = (f"{when} you counted the pantry and found one can fewer than you expected. Nobody has admitted taking it."
                if pid == "elena" else
                f"{when} Elena counted the pantry and found one can fewer than she expected. Nobody has admitted taking it.")
        items.append({"line": line, "ids": [count["id"]] if count else [], "weight": 9, "standing": True,
                      "self": False, "order": -1, "thought": None})
    for x in data.ORDER:
        if x in away and x != pid:
            went = next((e for e in reversed(chron.events) if e["kind"] == "went_out" and x in (e["members"] or [])),
                        None)
            when = scene_when(went["scene"], day) if went else "in the night"
            items.append({"line": f"{NAMES[x]} went out {when} and has not come back.",
                          "ids": [went["id"]] if went else [], "weight": 6, "standing": True, "self": False,
                          "order": -1, "thought": None})
    # C2: people. Each event of the past, as a candidate line for the person it is about.
    groups = {}                 # (q, key, other) -> events in order
    for e in old:
        a, kind, target = e["actor"], e["kind"], e["target"]
        if a is None:
            continue
        movers = e["members"] or [a]
        if kind == "went_out":
            for q in movers:
                if q not in away:
                    groups.setdefault((q, "went_out", None), []).append(e)
            continue
        key = None
        if kind == "confess":
            key = ("confess", None)
        elif kind in ("eat", "eat_given"):
            key = ("eat", None)
        elif kind == "accuse" and target:
            key = ("accuse", target) if (a == pid or target == pid) else ("accuse_other", target)
        elif kind == "confront" and target and (a == pid or target == pid):
            key = ("confront", target)
        elif kind == "give" and target and (a == pid or target == pid):
            key = ("give", target)
        elif kind == "share":
            key = ("share", None)
        elif kind in KIND_ACTS and target and (a == pid or target == pid):
            key = (kind, target)
        elif kind == "stop" and target and (a == pid or target == pid):
            key = ("stop", target)
        if key and a not in away:
            groups.setdefault((a, *key), []).append(e)
    order = {e["id"]: i for i, e in enumerate(chron.events)}
    best = {}
    for (q, key, other), evs in groups.items():
        cand = (WEIGHT[key], -order[evs[0]["id"]])        # heavier first; at equal weight, the older
        if q not in best or cand > best[q][0]:
            best[q] = (cand, key, other, evs)
    for q in data.ORDER:
        if q not in best:
            continue
        _, key, other, evs = best[q]
        line = person_line(chron, pid, q, key, other, evs, day)
        ids = [i for e in evs for i in (e["group"] or [e["id"]])]
        items.append({"line": line, "ids": list(dict.fromkeys(ids)), "weight": WEIGHT[key], "standing": False,
                      "self": q == pid, "order": order[evs[0]["id"]], "thought": None})
    # C3: one older thought per line, the most recent that cites its events.
    for it in items:
        ids = set(it["ids"])
        for k in sorted((k for k in chron.minds if k <= today - 2), reverse=True):
            mine = (chron.minds[k].get(pid) or {}).get("kept", [])
            hit = [m for m in mine if ids & set(m["ids"])]
            if hit:
                it["thought"] = hit[-1]["meaning"]
                break
    return items


def person_line(chron, pid, q, key, other, evs, day):
    first, last = evs[0], evs[-1]
    when = cap(scene_when(first["scene"], day))
    again = ""
    if key not in COUNTED and scene_key(last["scene"]) != scene_key(first["scene"]):
        again = f", and again {scene_when(last['scene'], day)}"
    n = len(evs)
    me = q == pid
    Q = NAMES[q]
    T = "you" if other == pid else NAMES.get(other, "")
    him = data.PRONOUNS[q]["him"]
    if key == "confess":
        if me:
            return f"{when}, you admitted taking the can, in front of everyone{again}."
        before = [e for e in chron.events if chron.events.index(e) < chron.events.index(first)
                  and e["actor"] == q and pid in e["witnesses"]]
        denied = ", after denying it to you" if any(e["kind"] == "deny" for e in before) else ""
        accused = (", after accusing you of it" if any(e["kind"] == "accuse" and e["target"] == pid for e in before)
                   else "")
        return f"{when}, {Q} admitted taking the can{denied}{accused}{again}."
    if key == "eat":
        return (f"{when}, you ate a portion in front of the others{again}." if me else
                f"{when}, {Q} ate a portion in front of you{again}.")
    if key == "went_out":
        told = any(e["kind"] == "stop" and e["actor"] == pid and e["target"] == q and e["scene"] == first["scene"]
                   for e in chron.events) and not me
        back = next((e for e in chron.events if e["kind"] == "return" and e["scene"] == first["scene"]
                     and q in (e["members"] or []) and pid in e["witnesses"]), None)
        street = next((e for e in chron.events if e["kind"] == "street" and e["scene"] == first["scene"]
                       and q in (e["members"] or [])), None)
        how = ""
        if back and street:
            outcome = street["outcome"] or ""
            how = (" and came back shaken" if "shaken" in outcome else
                   " and came back with food" if "with food" in outcome else " and came back with nothing")
        who = "you" if me else Q
        return f"{when}, {who} went out to the neighbour's house{f' after you told {him} not to' if told else ''}{how}{again}."
    if key == "accuse":
        if me:
            return f"{when}, you accused {T} of taking the can{times(n)}."
        innocent = ", and you had not" if pid != chron.culprit else ""
        return f"{when}, {Q} accused you of taking the can{times(n)}{innocent}."
    if key == "accuse_other":
        return f"{when}, {Q} accused {T} of taking the can{times(n)}."
    if key == "confront":
        return f"{when}, you confronted {T}{times(n)}." if me else f"{when}, {Q} confronted you{times(n)}."
    if key == "give":
        return f"{when}, you gave {T} a portion{again}." if me else f"{when}, {Q} gave you a portion{again}."
    if key == "share":
        return f"{when}, you shared out the food{again}." if me else f"{when}, {Q} shared out the food with you{again}."
    if key == "reassure":
        return f"{when}, you reassured {T}{times(n)}." if me else f"{when}, {Q} reassured you{times(n)}."
    if key == "sit":
        return f"{when}, you sat with {T}{times(n)}." if me else f"{when}, {Q} sat with you{times(n)}."
    if key == "stop":
        return (f"{when}, you told {T}, low, not to go{again}." if me else
                f"{when}, {Q} told you, low, not to go{again}.")
    raise ValueError(key)


# ---------- the bound ----------
def render_c(items):
    if not items:
        return []
    return [C_HEAD] + [f"- {it['line']}" + (f' You thought then: "{it["thought"]}"' if it.get("thought") else "")
                       for it in items]


def bounded(a_variants, b_lines, c_items, cap=MEMORY_MAX):
    """A, B and C within `cap` estimated tokens (§3.4), trimmed in this order: A's quoted night words, A's minutes,
    C's older thoughts (oldest first), C's people lines (lowest weight first; within a weight the oldest, the self
    line last), B's feeling, then B's intent. Never: C's standing lines, B's memories, A's lines themselves."""
    ai = 0
    items = [dict(it) for it in c_items]
    b = list(b_lines)

    def size():
        return estimate_tokens("\n".join(render_c(items) + a_variants[ai] + b))
    while size() > cap:
        if ai < len(a_variants) - 1:
            ai += 1
            continue
        thoughts = sorted((it for it in items if it.get("thought")), key=lambda it: it["order"])
        if thoughts:
            thoughts[0]["thought"] = None
            continue
        people = sorted((it for it in items if not it["standing"]), key=lambda it: (it["weight"], it["self"], it["order"]))
        if people:
            items.remove(people[0])
            continue
        feeling = next((x for x in b if x.startswith("- How it left you:")), None)
        if feeling:
            b.remove(feeling)
            continue
        intent = next((x for x in b if x.startswith("- You meant to:")), None)
        if intent:
            b.remove(intent)
            continue
        break
    return {"A": a_variants[ai], "B": b, "C": render_c(items), "C_items": items}
