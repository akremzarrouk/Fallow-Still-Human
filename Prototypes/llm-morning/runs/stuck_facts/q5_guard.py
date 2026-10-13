"""Q5. The guard "a speech act used three turns in a row is not offered a fourth time" (world.py:626-629), against the data.
Read-only. Inputs: runs/stuck_facts/asks_all.json (136 probe asks and v22 days 3-10: 342 asks = 478 in all) and
runs/stuck_facts/state_probe.json (the calm probe's world at the 24 person-minutes).
1. Asks whose prompt says "N turns in a row" with N = 3: is any option of that kind in the option list?
2. Every ask in a run of 4 or more of the same option (consecutive asks of one person on one day): the "turns in a row"
   figure the prompt showed (or "-" when the line is absent), and the clock of the ask.
3. How often the guard could not act at the asks that repeated the previous option."""
import collections, json, re, sys
sys.path.insert(0, ".")
from talk import act_of
import world

PHRASE_KIND = {}
for k, v in world.KIND_DONE.items():
    PHRASE_KIND.setdefault(v, k)
recs = json.load(open("runs/stuck_facts/asks_all.json"))
rx = re.compile(r"What you have been doing: you have (.*), (\d+) turns? in a row\.")
for r in recs:
    L = r["prompt"].split("\n")
    m = next((rx.match(l) for l in L if rx.match(l)), None)
    r["_n"] = int(m.group(2)) if m else None
    r["_kind"] = PHRASE_KIND.get(m.group(1)) if m else None
    r["_offered"] = [l[2:].split(":")[0] for l in L[L.index("Your options:") + 1:]]

print("# 1. prompts that say 3 turns in a row")
three = [r for r in recs if r["_n"] == 3]
bad = [r for r in three if any(act_of(o)[0] == r["_kind"] for o in r["_offered"])]
print(f"asks with n=3: {len(three)}; of them with an option of that kind still offered: {len(bad)}")
print("  those still offered, by kind:", dict(collections.Counter(r["_kind"] for r in bad)),
      "| kinds in SPEECH (talk.py:8-14):", sorted({r["_kind"] for r in three if r["_kind"] in __import__("talk").SPEECH}),
      "| kinds not in SPEECH:", sorted({r["_kind"] for r in three if r["_kind"] not in __import__("talk").SPEECH}))
print("  asks with n=3 of a SPEECH kind:", sum(1 for r in three if r["_kind"] in __import__("talk").SPEECH),
      "| of them with an option of that kind still offered:", sum(1 for r in bad if r["_kind"] in __import__("talk").SPEECH))
print("by dataset:", dict(collections.Counter(r["dataset"] for r in three)))
print("kinds held back:", dict(collections.Counter(r["_kind"] for r in three)))
print("asks with n > 3: ", sum(1 for r in recs if (r["_n"] or 0) > 3))
print("what the person chose at the asks with n=3:", dict(collections.Counter(act_of(r["option"])[0] for r in three)))
print("n shown, all asks:", dict(sorted(collections.Counter(r["_n"] for r in recs).items(), key=lambda kv: (kv[0] is None, kv[0]))))

print()
print("# 2. runs of 4 or more of the same option (consecutive asks of one person on one day): clock, option, n shown")
units = collections.OrderedDict()
for r in recs:
    units.setdefault((r["dataset"], str(r["scene"]), r["variant"], r["who"], r["day"]), []).append(r)
longest = []
for key, rs in units.items():
    if key[0] != "v22":
        rs = sorted(rs, key=lambda x: (x["minute"]))
    i = 0
    while i < len(rs):
        j = i
        while j + 1 < len(rs) and rs[j + 1]["option"] == rs[i]["option"]:
            j += 1
        if j - i + 1 >= 4:
            longest.append((key, rs[i:j + 1]))
        i = j + 1
for key, run in longest:
    print(f"{key[0]} {key[1]} {key[3]} d{key[4]}: {run[0]['option']} x{len(run)}: " +
          "  ".join(f"{(r['clock'] or '').replace('minute ', 'min ')}:{r['_n'] if r['_n'] else '-'}" for r in run))

print()
print("# 3. asks that repeated the same OPTION as the same person's previous ask that day: what the prompt showed")
c = collections.Counter()
ck = collections.Counter()
for key, rs in units.items():
    if key[0] != "v22":
        rs = sorted(rs, key=lambda x: (x["minute"]))
    for a, b in zip(rs, rs[1:]):
        if b["option"] == a["option"] and act_of(b["option"])[0] in __import__("talk").SPEECH:
            c[(key[0], "line absent" if b["_n"] is None else f"n={b['_n']}")] += 1
            ck["all"] += 1
for k2, v in sorted(c.items()):
    print(k2, v)
print("total repeats of a speech option on the next ask:", ck["all"])

print()
print("# 4. Elena, v22 day 3: every ask, the line shown, whether any reassure option was offered, and what she did")
for r in recs:
    if r["dataset"] == "v22" and r["day"] == 3 and r["who"] == "elena":
        L = r["prompt"].split("\n")
        pat = next((l for l in L if l.startswith("What you have been doing")), "(no 'What you have been doing' line)")
        print(f"{r['clock']:10s} {r['option']:13s} reassure options offered: {sum(1 for o in r['_offered'] if act_of(o)[0] == 'reassure')}  | {pat}")

print()
print("# 5. the calm probe's world at the 24 person-minutes (state_probe.json): the last history entry, repeating(), guard")
rows = json.load(open("runs/stuck_facts/state_probe.json"))
print("rows:", len(rows), "| last history entry is 'routine':", sum(1 for r in rows if r["history_tail"][-1][1] == "routine"),
      "| repeating(p) = ('routine', 1):", sum(1 for r in rows if r["repeating"] == ["routine", 1]),
      "| pattern(p) is empty:", sum(1 for r in rows if not r["pattern"]), "| guard would apply:", sum(1 for r in rows if r["guard_would_apply"]))
for who in ("elena", "mara"):
    r = next(x for x in rows if x["who"] == who and x["scene"] == 1 and x["clock"] == "10:30")
    print(who, "scene 1 10:30 history tail (t, kind, seq):", r["history_tail"])

print()
print("# 6. Elena, talk_probe scene 3 (five answers of the kind reassure): clock, option, line shown")
for r in sorted([r for r in recs if r["dataset"] == "talk_probe" and str(r["scene"]) == "3" and r["who"] == "elena"], key=lambda x: x["minute"]):
    L = r["prompt"].split("\n")
    pat = next((l for l in L if l.startswith("What you have been doing")), "(no 'What you have been doing' line)")
    print(f"{r['clock']:6s} {r['option']:15s} reassure options offered: {sum(1 for o in r['_offered'] if act_of(o)[0] == 'reassure')}  | {pat}")
