"""The metrics table for the first version's runs and this version's, computed the same way.

    python v1/transcript.py     (once: writes the first version's transcripts from its cache)
    python metrics.py           prints the table and the details behind it, in Markdown

Reads runs/daniel_ate_it-seed<N>.transcript.json (first version) and
runs/v2/daniel_ate_it-seed<N>.transcript.json (this version). Every metric is computed
from those transcripts by the code below, for both versions alike.
"""
import json
import os
import re
import sys

from talk import SPEECH, Conversations, Newness, act_of, aimed_at

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ROOM_NAMES = {"kitchen": "kitchen", "brothers_room": "brothers room", "back_room": "back room",
              "bathroom": "bathroom"}

# Things and places named in spoken lines that the house does not have (data.HOUSE_THINGS
# lists what it has). Built by reading every line of the six runs; every hit is listed in
# the output so it can be checked by eye.
NOT_IN_HOUSE = ["jacket", "pocket", "pockets"]


def load(version, seed):
    folder = os.path.join(HERE, "runs", "v2") if version == 2 else os.path.join(HERE, "runs")
    with open(os.path.join(folder, f"daniel_ate_it-seed{seed}.transcript.json"), encoding="utf-8") as f:
        return json.load(f)


def acts(tr):
    return [a for turn in tr["turns"] for a in sorted(turn["acts"], key=lambda a: a["said_at"])]


def lines(tr):
    return [a for a in acts(tr) if a["words"]]


def moved_to(a):
    """Where an act took its person: a walk, or a private talk (third version on)."""
    if "moved_to" in a:
        return a["moved_to"]
    return a["option"][3:] if act_of(a["option"])[0] == "go" else None


def conversations(tr, quiet_turns=1):
    """The conversation log, worked out from the transcript with the rules in talk.py."""
    newness, convos = Newness(), Conversations(ROOM_NAMES, quiet_turns)
    convos.new_thing("kitchen", 0, "the count came up short")
    arrivals = []
    turns = tr["turns"]
    for i, turn in enumerate(turns):
        minute = turn["minute"]
        for room, who in arrivals:
            convos.new_thing(room, minute, f"{NAMES[who]} came in")
        for a in sorted(turn["acts"], key=lambda a: a["said_at"]):
            if a["words"]:
                new, why = newness.line(a["who"], a["option"], a["audience"])
                if new:
                    convos.new_thing(a["room"], minute, f"{NAMES[a['who']]}: {why}")
            came = a["came_of_it"]
            if a["audience"] and (came.startswith("ate a portion") or came.startswith("shared out")
                                  or came == "went through the room and found nothing."):
                convos.new_thing(a["room"], minute, f"{NAMES[a['who']]}: {came}")
        after = turns[i + 1]["rooms"] if i + 1 < len(turns) else tr["final_rooms"]
        arrivals = [(moved_to(a), a["who"]) for a in turn["acts"]
                    if moved_to(a) and len(after[moved_to(a)]) > 1]
        convos.end_turn(minute + 3, {r: len(v) for r, v in turn["rooms"].items()},
                        {r: len(v) for r, v in after.items()})
    return convos.log


def responds(prev, cur):
    """Whether a line answers the line said just before it in the same room: its speaker
    heard that line before choosing, and the line is aimed at the one who said it, or comes
    from the one it was aimed at, or joins in against the same person, or answers a question
    or a denial in kind."""
    if cur["who"] == prev["who"] or cur["who"] not in prev["audience"]:
        return False
    if not prev["said_at"] < cur["decided_at"]:
        return False
    pk, ck = act_of(prev["option"])[0], act_of(cur["option"])[0]
    pt, ct = aimed_at(prev["option"]), aimed_at(cur["option"])
    return (ct == prev["who"]
            or (pt is not None and cur["who"] == pt)
            or (pk == "accuse" and ct == pt)
            or (pk == "ask" and ck in ("deny", "confess", "accuse"))
            or (pk == "deny" and ck in ("ask", "accuse")))


def response_share(tr):
    last, yes, total = {}, 0, 0
    for a in lines(tr):
        prev = last.get(a["room"])
        if prev is not None:
            total += 1
            yes += responds(prev, a)
        last[a["room"]] = a
    return yes, total


def longest_run(tr):
    """Longest run of turns in a row in which one person used the same kind of speech act."""
    best = (0, None, None, None, None)
    for who in NAMES:
        kinds = [(t["minute"], act_of(next(a["option"] for a in t["acts"] if a["who"] == who))[0])
                 for t in tr["turns"]]
        n, start = 0, None
        for i, (minute, kind) in enumerate(kinds):
            if kind in SPEECH and i and kinds[i - 1][1] == kind:
                n += 1
            elif kind in SPEECH:
                n, start = 1, minute
            else:
                n = 0
            if n > best[0]:
                best = (n, who, kind, start, minute)
    return best


def confession(tr):
    for a in acts(tr):
        if a["option"] == "confess":
            return a["minute"]
    return None


def outside_things(tr):
    hits = []
    for a in lines(tr):
        for word in NOT_IN_HOUSE:
            for _ in re.finditer(rf"\b{word}\b", a["words"], flags=re.I):
                hits.append((a["minute"], a["who"], word, a["words"]))
    return hits


def model_calls(tr):
    return sum(a["mode"] != "routine" for a in acts(tr))


def row(version, seed):
    tr = load(version, seed)
    yes, total = response_share(tr)
    n, who, kind, start, end = longest_run(tr)
    ended = [(m, r, why) for m, r, what, why in conversations(tr) if what == "ended"]
    conf = confession(tr)
    return {
        "version": version, "seed": seed, "calls": model_calls(tr), "lines": len(lines(tr)),
        "run": f"{n} ({NAMES[who]}, {kind}, min {start:02d}–{end:02d})" if who else "0",
        "respond": f"{yes}/{total} ({100 * yes / total:.0f}%)" if total else "0/0",
        "ended": "; ".join(f"{ROOM_NAMES[r]} {m:02d}" + ("" if why.startswith("a full turn") else " (people left)")
                           for m, r, why in ended) or "never",
        "confessed": f"yes, min {conf:02d}" if conf is not None else "no",
        "outside": len(outside_things(tr)),
    }


def main():
    rows = [row(v, s) for v in (1, 2) for s in (1, 2, 3)]
    print("| Run | Model calls | Lines spoken | Longest run of one speech act by one person | "
          "Lines that answer the line before them | Conversations ended (room, minute) | "
          "Daniel confessed | References to things not in the house |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        name = f"{'old' if r['version'] == 1 else 'new'}, seed {r['seed']}"
        print(f"| {name} | {r['calls']} | {r['lines']} | {r['run']} | {r['respond']} | {r['ended']} | "
              f"{r['confessed']} | {r['outside']} |")
    print()
    print("References to things not in the house:")
    for v in (1, 2):
        for s in (1, 2, 3):
            for minute, who, word, words in outside_things(load(v, s)):
                print(f"- {'old' if v == 1 else 'new'}, seed {s}, min {minute:02d}, {NAMES[who]}: "
                      f"\"{word}\" in “{words}”")
    return 0


if __name__ == "__main__":
    sys.exit(main())
