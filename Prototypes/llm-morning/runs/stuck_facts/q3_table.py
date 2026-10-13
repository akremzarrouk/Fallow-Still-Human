"""Q3 as Markdown tables: for scene 1 version P (calm_probe), Elena and Mara, every line before "Your options:" with its
section, its position from the end of the prompt at 10:00 / 10:30 / 11:00 (the last line of the prompt is 1), and whether the
same text is in all three prompts. Also, for all 16 groups (2 scenes x 4 versions x Elena, Mara), the lines that are not in all
three prompts and the minutes at which they are missing. Read-only."""
import collections, json, sys
sys.path.insert(0, "runs/stuck_facts")
from sections import sections

CLOCKS = ("10:00", "10:30", "11:00")
groups = collections.OrderedDict()
for k in (1, 3):
    for mo in json.load(open(f"runs/calm_variants/scene{k}.json"))["moments"]:
        for a in mo["asks"]:
            groups.setdefault((k, a["variant"], a["who"]), {})[mo["clock"]] = a["prompt"].split("\n")
    for mo in json.load(open(f"runs/calm_probe/scene{k}.json"))["moments"]:
        for a in mo["asks"]:
            groups.setdefault((k, "P", a["who"]), {})[mo["clock"]] = a["prompt"].split("\n")


def clip(s, n=118):
    s = s.replace("|", "\\|")
    return s if len(s) <= n else s[:n - 3] + "..."


for who in ("elena", "mara"):
    by = groups[(1, "P", who)]
    ps = [by[c] for c in CLOCKS]
    secs = sections("\n".join(ps[0]))
    inall = set.intersection(*[set(p) for p in ps])
    cut = ps[0].index("Your options:")
    print(f"#### {who.capitalize()}, scene 1, calm_probe prompts at 10:00 / 10:30 / 11:00 (lines before the options: {cut}, {cut} at 10:00 and 10:30, {ps[2].index('Your options:')} at 11:00)")
    print()
    print("| # (10:00) | section | from end 10:00 / 10:30 / 11:00 | same in all three | text |")
    print("|---|---|---|---|---|")
    for i in range(cut):
        l = ps[0][i]
        pos = "/".join(str(len(p) - p.index(l)) if l in p else "-" for p in ps)
        print(f"| {i+1} | {secs[i][0]} | {pos} | {'yes' if l in inall else 'NO'} | {clip(l)} |")
    # lines that exist only at 11:00
    for l in ps[2]:
        if l not in ps[0] and l not in ps[1]:
            print(f"| (11:00 only) | {sections(chr(10).join(ps[2]))[ps[2].index(l)][0]} | -/-/{len(ps[2]) - ps[2].index(l)} | NO | {clip(l)} |")
    print()
    print(f"The options: 'Your options:' is {len(ps[0]) - cut} from the end at every minute, and the {len(ps[0]) - cut - 1} option lines under it are the same, in the same order, at 10:00, 10:30 and 11:00.")
    print()

print("#### All 16 groups: lines not word for word in all three prompts, and the minutes where they are missing")
print()
print("| scene | version | person | lines per prompt | line | missing at |")
print("|---|---|---|---|---|---|")
for (k, var, who), by in groups.items():
    if who not in ("elena", "mara"):
        continue
    ps = [by[c] for c in CLOCKS]
    inall = set.intersection(*[set(p) for p in ps])
    seen = set()
    for j, p in enumerate(ps):
        for l in p:
            if l not in inall and l not in seen:
                seen.add(l)
                miss = [CLOCKS[x] for x in range(3) if l not in ps[x]]
                print(f"| {k} | {var} | {who} | {'/'.join(str(len(x)) for x in ps)} | {clip(l, 90)} | {', '.join(miss)} |")

print()
print("#### Scene 1, version P: per section, the number of lines at each minute, how many of the 10:00 lines are in all three, and the positions from the end (first-last) at each minute")
print()
print("| person | section | lines at 10:00 / 10:30 / 11:00 | of the 10:00 lines, in all three | from end at 10:00 | at 10:30 | at 11:00 |")
print("|---|---|---|---|---|---|---|")
for who in ("elena", "mara"):
    by = groups[(1, "P", who)]
    ps = [by[c] for c in CLOCKS]
    inall = set.intersection(*[set(p) for p in ps])
    S = [sections("\n".join(p)) for p in ps]
    order = []
    for sec, _ in S[0]:
        if sec not in order:
            order.append(sec)
    for sec in order + [s for s in dict.fromkeys(x for SS in S for x, _ in SS) if s not in order]:
        cells, counts = [], []
        for j in range(3):
            idx = [i for i, (s, _) in enumerate(S[j]) if s == sec]
            counts.append(len(idx))
            cells.append("-" if not idx else (f"{len(ps[j]) - idx[0]}-{len(ps[j]) - idx[-1]}" if len(idx) > 1 else f"{len(ps[j]) - idx[0]}"))
        n_all = sum(1 for s, l in S[0] if s == sec and l in inall)
        print(f"| {who} | {sec} | {'/'.join(map(str, counts))} | {n_all} of {counts[0]} | {cells[0]} | {cells[1]} | {cells[2]} |")
