"""Topics (reports/talk_design.md, as amended by the user, A1-A4): an earlier event a person can talk about, and tell
someone who missed it.

From day 3 on, a visit to the front door is a topic once it has ended (A1: the only kind in v1; TOPICS stays a table,
so that food is one entry later). Whoever perceived the visit holds their own account of it, written by quiet.door_end
into `p.topics`. The options are `talk_<topic>` and `tell_<names>_<topic>`, faded by the code alone (F1-F5, §1.4):
never a line telling a person they have said it before.

A tell gives each listener a belief (A3): the claim, built by code from the teller's own account and marked with its
source ("Elena told you that ..."), never from the world. It is kept on the listener (`p.beliefs`); the chronicle's
witnesses stay who perceived each event. The words said are kept as speech; T1 only logs when they name nothing of
the topic or deny its outcome (§3).
"""
import re

import data

TOPICS = {"visit": {"weight": 4, "gist": "the person at the front door"}}
TALK_WINDOW = 360           # F1: talk_<T> is offered for 6 hours from T's opening, and never after T's day
COOLDOWN = 60               # F2: after p chooses T's options, none of them is offered to p for 60 minutes
PER_DAY = 2                 # F3: p chooses T's options at most twice a day
ROOM_QUIET = 30             # F4: after anyone raises T in a room, talk_<T> is not offered there for 30 minutes
MAX_OPTIONS = 2             # §1.3: at most 2 topic options in a prompt
DOOR_ROOM = "kitchen"       # the door scene is played in the kitchen (quiet.Quiet.door_views, door_before)
T1_NOTHING = "T1 the words name nothing of the topic"
T1_DENIES = "T1 the words deny the outcome"
NEGATION = r"(?:not|never|no|nothing|didn't|did not|don't|wasn't|n't)"


def name(pid):
    return data.PEOPLE[pid]["name"]


def names(pids):
    return data._and([name(q) for q in pids])


# ---------- what a knower holds ----------
def visit_entry(q, k, day, sc, account, minute):
    """p.topics' entry for a door visit, as q perceived it. account: their own account (quiet.Quiet.visit_account), or
    None for someone who only heard knocking."""
    return {"key": f"visit:{sc['visit']}", "kind": "visit", "holder": q, "k": k, "day": day, "opened": minute,
            "start": sc["start"], "first": account is not None, "account": account,
            "who": account["who"] if account else None,
            "rooms": dict(sc["rooms"])}         # where each one was at the knock: for a teller's whereabouts line


def told_entry(source, listener):
    """A listener's entry once told: they know the topic (F5), and may talk about it, but hold no account of their
    own (§2.1: no second-hand telling in v1)."""
    return {**source, "holder": listener, "first": False, "account": None}


def when(entry, day):
    """"" on the topic's own day, else "yesterday " (from world.when_words, as the morning's blocks write it)."""
    from world import day_index, when_words
    return "" if day_index(day) == entry["k"] else when_words(("D", entry["k"]), day) + " "


def referent(entry, day):
    """The noun phrase for the topic in an option's label (§4): only what the speaker perceived."""
    who = entry["who"]
    if who is None:
        ref = "the knocking"
    elif who == "someone":
        ref = "someone"
    else:
        ref = "the " + who.split(" ", 1)[1]                 # "a woman of about forty-five": "the woman of ..."
    return f"{ref} at the front door {when(entry, day)}at {data.clock(entry['start'])}"


def claim(entry, teller, listener, day):
    """The claim a listener keeps of a tell (§2.2): the teller's own account, rendered for the listener, marked with
    its source. Nothing in it that the teller did not perceive."""
    a = entry["account"]
    her = a["pronoun"] if a["who"] != "someone" else "them"
    she = {"her": "she", "him": "he", "them": "they"}[her]

    def who(pid):
        if pid == teller:
            return f"{name(pid)} {data.PRONOUNS[pid]['himself']}"
        return "you" if pid == listener else name(pid)
    head = f"{name(teller)} told you that {when(entry, day)}at {data.clock(entry['start'])} {a['who']} knocked at the " \
           f"front door"
    if a["asked"]:
        head += f" and asked for {a['good']}" + (f" for {a['kids']}" if a["kids"] else "")
    acts = [(kind, by) for kind, by, _ in a["acts"]]
    if len(acts) == 2 and acts[0][0] == "door_refuse":
        tail = (f"that {who(acts[0][1])} told {her} to go away, and that {who(acts[1][1])} handed {her} about three "
                f"litres of the stored water anyway")
    elif len(acts) == 2:
        tail = (f"that {who(acts[0][1])} handed {her} about three litres of the stored water, and that then "
                f"{who(acts[1][1])} told {her} to go away")
    elif acts and acts[0][0] == "door_give":
        tail = f"that {who(acts[0][1])} handed {her} about three litres of the stored water"
    elif acts:
        tail = f"that {who(acts[0][1])} told {her} to go away"
    elif a["asked"]:
        tail = f"that {she} went away with nothing"
    else:
        tail = f"that nobody answered, and {she} went away"
    return f"{head}; {tail}."


# ---------- the options (§1.2-§1.4, §2.1, §4) ----------
def said_today(p, key, k):
    return [mm for kk, mm in p.topic_said.get(key, []) if kk == k]


def options(m, p, others, minute):
    """The topic options for p now: at most MAX_OPTIONS, one per topic, a tell before a talk, then the heavier topic,
    then the more recent. Empty (and so no change to any prompt) on days 1 and 2, before any visit has ended, and
    when nobody else is awake in the room."""
    q = getattr(m, "quiet", None)
    if q is None or minute is None or not p.topics:
        return []
    from world import Option
    k = q.k
    awake = [x for x in others if not q.resting(x.id)]
    if not awake:
        return []
    cands = []
    for key, t in p.topics.items():
        said = said_today(p, key, k)
        if said and minute - said[-1] < COOLDOWN:                                   # F2
            continue
        if len(said) >= PER_DAY:                                                    # F3
            continue
        lacking = [x.id for x in awake if key not in x.topics]                      # F5
        if lacking and t["first"] and k - t["k"] in (0, 1):                         # F1: its day and the next
            cands.append((0, t, lacking))
        elif (t["k"] == k and 0 <= minute - t["opened"] < TALK_WINDOW                # F1
              and minute - m.topic_raised.get((p.room, key), -10 ** 9) >= ROOM_QUIET):  # F4
            cands.append((1, t, None))
    cands.sort(key=lambda c: (c[0], -TOPICS[c[1]["kind"]]["weight"], -c[1]["k"], -c[1]["opened"]))
    cands = cands[:MAX_OPTIONS]
    out = []
    for rank, t, lacking in cands:
        same = [c for c in cands if c[1]["kind"] == t["kind"]]
        suffix = t["kind"] if len(same) == 1 else f"{t['kind']}_{t['key'].split(':', 1)[1]}"
        ref = referent(t, m.day)
        if lacking:
            ids = [x for x in data.ORDER if x in lacking]
            out.append(Option(f"tell_{'_'.join(ids)}_{suffix}", f"tell {names(ids)} about {ref}", True, kind="tell",
                                topic=t["key"], listeners=ids, referent=ref))
        else:
            out.append(Option(f"talk_{suffix}", f"talk about {ref}", True, kind="talk", topic=t["key"],
                                referent=ref))
    return out


def whereabouts(m, p, opts):
    """While a tell is offered to p (reports/tell_fix_impl.md), one line per listener of what p perceived of where they
    were: not in the room of the door scene when the visitor came, if p was in it at the knock and they were not; and,
    on the visit's own day, when they came in, if p perceived that. Gone once the listener knows the topic (F5 closes
    the tell)."""
    out = []
    for o in opts:
        if o.act.get("kind") != "tell":
            continue
        t = p.topics[o.act["topic"]]
        if t["rooms"].get(p.id) != DOOR_ROOM:
            continue
        visitor = "someone" if t["who"] == "someone" else f"the {noun(t['who'])}"
        room = data.ROOMS[DOOR_ROOM]
        ago = when(t, m.day).strip()                        # "" on its day, "yesterday" the next (F1)
        for x in o.act["listeners"]:
            if t["rooms"].get(x) == DOOR_ROOM:
                continue
            line = f"{name(x)} was not in the {room} when {visitor} came to the door" + (f" {ago}" if ago else "")
            came = None if ago else next((mm for mm, text in p.memory if mm >= t["start"]
                                          and text == f"{name(x)} comes into the {room}."), None)
            if came is not None:
                line += f"; {data.PRONOUNS[x]['he']} came in at {data.clock(came)}"
            out.append(line + ".")
    return out


def listeners_of(option):
    """The listeners named in a tell option's id, tell_<names>_<topic>, in order; [] for any other option."""
    out = []
    for x in option.split("_")[1:] if option.startswith("tell_") else []:
        if x not in data.PEOPLE:
            break
        out.append(x)
    return out


def suffix_of(option):
    """The topic part of a talk or tell option's id: "visit" (or "visit_<id>" when two visits are open)."""
    parts = option.split("_")[1:]
    return "_".join(parts[len(listeners_of(option)):])


def noun(who):
    """The visitor's noun as perceived: "a woman of about forty-five" -> "woman"."""
    return who.split(" of ")[0].split()[-1]


# ---------- a choice of one of them ----------
def chose(m, p, key, minute):
    """p has chosen one of T's options at `minute`, in their room: F2 and F3 count it, and F4 holds talk back in the
    room."""
    p.topic_said.setdefault(key, []).append((m.quiet.k, minute))
    m.topic_raised[(p.room, key)] = minute


def tell(m, teller, listeners, key, minute, words):
    """teller tells `listeners` about T at `minute`, in these words: each listener gets a belief (A3) and knows T from
    now (F5); T1 checks the words. Returns the run log's record of the tell."""
    chose(m, teller, key, minute)
    entry = teller.topics[key]
    for x in listeners:
        q = m.people[x]
        c = claim(entry, teller.id, x, m.day)
        q.beliefs.append({"owner": x, "claim": c, "about": [], "source": teller.id, "minute": minute, "how": "told",
                          "day": m.day, "k": m.quiet.k, "topic": key, "refs": list(entry["account"]["refs"])})
        q.topics[key] = told_entry(entry, x)
    rec = {"minute": minute, "teller": teller.id, "listeners": list(listeners), "topic": key, "words": words,
           "claims": {x: m.people[x].beliefs[-1]["claim"] for x in listeners}, "warnings": t1(entry, words)}
    m.tells.append(rec)
    return rec


# ---------- T1 (§3): words versus claim, logged only ----------
def t1(entry, words):
    """Warnings for a tell whose words name nothing of the topic, or deny its outcome. Changes nothing."""
    text = (words or "").lower()
    a = entry["account"]
    anchors = [r"front door", r"\bdoor", r"\bknock", r"\bsomeone\b", r"\bwater\b", rf"\b{a['good']}\b"]
    if a["who"] not in (None, "someone"):
        anchors.append(rf"\b{noun(a['who'])}\b")                     # "a woman of about forty": woman
    for _, by, _ in a["acts"]:                                     # each actor, by name or as the holder calls them
        anchors += [rf"\b{w.lower()}\b" for w in {name(by), data.ADDRESS[entry["holder"]].get(by, name(by))}]
    out = []
    if not any(re.search(x, text) for x in anchors):
        out.append(T1_NOTHING)
    verbs = {"door_give": r"(?:gave|give|given|handed|hand)", "door_refuse": r"(?:told|tell|sent|send|turned|turn)"}
    for kind, _, _ in a["acts"]:
        if re.search(rf"\b{NEGATION}\b(?:\W+\w+){{0,3}}?\W+{verbs[kind]}\b", text):
            out.append(T1_DENIES)
            break
    return out


# ---------- the chronicle ----------
def gist(e, pid):
    """A short name for a talk or a tell event, as pid would call it (chronicle.gist)."""
    topic = TOPICS[suffix_of(e.get("option") or "").split("_")[0]]["gist"]
    if e["kind"] == "talk":
        return f"talking about {topic}"
    heard = [("you" if x == pid else name(x)) for x in (e.get("members") or [])]
    return f"telling {data._and(heard) if heard else 'someone'} about {topic}"
