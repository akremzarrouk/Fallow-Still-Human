"""Every day-3 ask after the morning in v17 (from runs/v17_meetings/replay/seedN.json, made by replay_v17.py): the
options offered, grouped by kind (talk.act_of), and the one chosen; and the lines of each prompt about tonight's trip.

    python runs/v17_meetings/scripts/asks.py asks      one line per ask
    python runs/v17_meetings/scripts/asks.py kinds     kind, asks offering it, options offered, times chosen
    python runs/v17_meetings/scripts/asks.py trip      the trip lines of every ask after the morning, deduplicated
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import data                                           # noqa: E402
from talk import act_of                               # noqa: E402


def kind(option):
    k = act_of(option)[0]
    return {"propose": "propose (propose_trip)", "volunteer": "volunteer", "back": "back (send_<q>)",
            "object": "object (nobody_goes, keep_<q>_home)", "decline": "decline (refuse_to_go)"}.get(k, k)


def asks():
    out = []
    for s in (1, 2, 3):
        r = json.load(open(f"runs/v17_meetings/replay/seed{s}.json", encoding="utf-8"))
        t = json.load(open(f"runs/v17/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
        end = t["day3"]["quiet"]["morning_end"]
        for i, a in enumerate(r["day3_asks"]):
            p = a["prompt"]
            m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", p, re.M)
            minute = int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - data.DAY_START
            if minute < end:
                continue
            block = p.split("Your options:")[-1]
            opts = re.findall(r"^- (\w+):", block, re.M)
            out.append({"seed": s, "i": i, "who": re.match(r"You are (\w+),", p).group(1), "minute": minute,
                        "options": opts, "chosen": json.loads(a["response"])["option"], "prompt": p})
    return out


what = sys.argv[1]
A = asks()
if what == "asks":
    for a in A:
        print(f"seed {a['seed']} #{a['i']} {data.clock(a['minute'])} {a['who']}: chose {a['chosen']}; offered "
              + ", ".join(a["options"]))
    print(f"asks after the morning: {len(A)}")
elif what == "kinds":
    asked, offered, chosen = collections.Counter(), collections.Counter(), collections.Counter()
    for a in A:
        ks = [kind(o) for o in a["options"]]
        offered.update(ks)
        asked.update(set(ks))
        chosen[kind(a["chosen"])] += 1
    print(f"| kind | asks offering it (of {len(A)}) | options offered | times chosen |")
    print("|---|---|---|---|")
    for k in sorted(asked, key=lambda k: (-chosen[k], -asked[k], k)):
        print(f"| {k} | {asked[k]} | {offered[k]} | {chosen[k]} |")
    by = collections.Counter((a["seed"], a["chosen"]) for a in A)
    print("chosen options, by seed:", dict(sorted(by.items())))
elif what == "trip":
    seen = collections.OrderedDict()
    keys = ("About going", "About food", "About the neighbour", "Outside, and not", "tonight")
    for a in A:
        for line in a["prompt"].splitlines():
            if any(k in line for k in keys) and not line.startswith("- propose_trip") and not line.startswith(
                    ("- volunteer", "- send_", "- nobody_goes", "- keep_", "- still_going", "- refuse_to_go")):
                text = re.sub(r"^.*(Outside, and not to be gone to this morning[^.]*\.).*$", r"\1", line)
                seen.setdefault(text, []).append(f"s{a['seed']}#{a['i']}")
    for text, where in seen.items():
        print(f"[{len(where)} asks: {where[0]} … {where[-1]}] {text}")
