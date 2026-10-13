"""Q3. For Elena and Mara in calm_variants (and calm_probe, the 4th version), which prompt lines are word for word the same at
10:00, 10:30 and 11:00? Per (scene, version, person): the 3 prompts are split into lines; each line gets a section; a line is
"fixed" if the same text is in all three prompts. Position from the end: the last line of the prompt is 1.
Read-only. Inputs: runs/calm_variants/scene<k>.json (all 54 rows, reused ones included), runs/calm_probe/scene<k>.json (18)."""
import collections, json, re, sys

HEADERS = [  # (line start, section) in the order they appear in a prompt
    ("You are the first to act", "now"),
    ("You are ", "sheet"), ("How you address them:", "sheet"), ("Who you are:", "sheet"), ("Temperament:", "sheet"),
    ("What matters to you:", "sheet"),
    ("Your body:", "body and 'About' lines"), ("About ", "body and 'About' lines"),
    ("Against ", "grudge lines"), ("On your conscience", "grudge lines"),
    ("The house:", "house"),
    ("What you remember from the days before:", "days before"),
    ("What stays with you from earlier days:", "carry-in: earlier days"),
    ("Yesterday and last night:", "carry-in: yesterday and last night"),
    ("What yesterday left in you", "carry-in: what yesterday left in you"),
    ("What you are sure of", "sure lines"),
    ("Your own last words", "own last words"),
    ("What else happened", "memory (what else happened)"),
    ("Nobody in the kitchen has said anything since", "T line"),
    ("You last spoke with", "now: meeting lines (world.py:1166)"),
    ("Now, ", "now"),
    ("You are the first to act", "now"),
    ("What you have been doing:", "pattern line"),
    ("Your options:", "options"),
]

def sections(prompt):
    out, cur = [], None
    for l in prompt.split("\n"):
        for start, name in HEADERS:
            if l.startswith(start) and not (start == "About " and cur in ("days before",) ) :
                # "- ..." lines never start with these; header lines only
                cur = name; break
        out.append((cur, l))
    return out

groups = collections.OrderedDict()
for k in (1, 3):
    d = json.load(open(f"runs/calm_variants/scene{k}.json"))
    for mo in d["moments"]:
        for a in mo["asks"]:
            groups.setdefault((k, a["variant"], a["who"]), {})[mo["clock"]] = a["prompt"]
    d = json.load(open(f"runs/calm_probe/scene{k}.json"))
    for mo in d["moments"]:
        for a in mo["asks"]:
            groups.setdefault((k, "P", a["who"]), {})[mo["clock"]] = a["prompt"]

print("# per group: lines per prompt, lines the same in all three, lines that differ (text at 10:00 | 10:30 | 11:00 shortened)")
rowsout = {}
for (k, var, who), by in groups.items():
    if who not in ("elena", "mara") or len(by) != 3:
        continue
    ps = [by[c].split("\n") for c in ("10:00", "10:30", "11:00")]
    n = len(ps[0])
    same_len = len({len(p) for p in ps}) == 1
    fixed, differ = [], []
    for i in range(n):
        t = {p[i] for p in ps} if same_len else None
        (fixed if t is not None and len(t) == 1 else differ).append(i)
    # a line is "fixed" if its text is in all three prompts (not necessarily the same index)
    sets = [set(p) for p in ps]
    inall = set.intersection(*sets)
    notall = [l for l in ps[0] if l not in inall]
    print(f"scene {k} {var:2s} {who:5s} lines {[len(p) for p in ps]} same-index-same-text {len(fixed)} differ-at-index {len(differ)}; "
          f"in all three prompts {sum(1 for l in ps[0] if l in inall)} of {len(ps[0])}; not in all three: "
          + " || ".join(l[:70] for l in notall))
    rowsout[(k, var, who)] = (ps, inall)

# the full listing, for scene 1, version P, for Elena and Mara; and an equality check of the fixed sets across versions
def listing(k, var, who):
    ps, inall = rowsout[(k, var, who)]
    secs = [sections(p) for p in ("\n".join(x) for x in ps)]
    N = [len(p) for p in ps]
    print(f"\n## scene {k}, version {var}, {who}: every line, its section, position from the end at 10:00 / 10:30 / 11:00, same in all three?")
    only_late = [(sec, l) for sec, l in secs[2] if l not in ps[0] and l not in ps[1]]
    only_early = [(sec, l) for sec, l in secs[0] if l not in ps[2]]
    for i, (sec, l) in enumerate(secs[0]):
        pos = []
        for j in range(3):
            if l in ps[j]:
                pos.append(str(N[j] - ps[j].index(l)))
            else:
                pos.append("-")
        print(f"{i+1:3d} | {sec:38s} | from end {'/'.join(pos):10s} | {'SAME' if l in inall else 'differs'} | {l if len(l) <= 160 else l[:157] + '...'}")
for who in ("elena", "mara"):
    listing(1, "P", who)
    ps, inall = rowsout[(1, "P", who)]
    secs = [sections("\n".join(x)) for x in ps]
    print(f"-- lines in the 11:00 prompt that are in neither the 10:00 nor the 10:30 prompt ({who}):")
    for sec, l in secs[2]:
        if l not in ps[0] and l not in ps[1]:
            print(f"   {sec:30s} from end {len(ps[2]) - ps[2].index(l)} | {l}")

print("\n# the lines that are not word for word the same at the three minutes, in every group (text of the 10:30 prompt)")
allnot = collections.Counter()
for key, (ps, inall) in rowsout.items():
    for l in ps[1]:
        if l not in inall:
            allnot[re.sub(r"\d\d:\d\d", "HH:MM", re.sub(r"\d+ minutes ago", "N minutes ago", l))] += 1
for l, c in allnot.items():
    print(c, "groups:", l)
print("groups:", len(rowsout))

# sections of the 'fixed' lines, counted, for scene 1 P (and same for all groups)
print("\n# fixed lines per section, per group (lines in all three prompts / lines in the section at 10:30)")
for key, (ps, inall) in rowsout.items():
    secs = sections("\n".join(ps[1]))
    c = collections.OrderedDict()
    for sec, l in secs:
        a = c.setdefault(sec, [0, 0]); a[1] += 1; a[0] += (l in inall)
    print(key, {s: f"{a}/{b}" for s, (a, b) in c.items()})
