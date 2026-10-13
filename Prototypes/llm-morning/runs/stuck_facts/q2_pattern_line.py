"""Q2. In which of the live day asks (asks_all.json: the 140 probe asks and v22 days 3-10) does the prompt hold
"What you have been doing:"; the line, its n, and what follows it. Read-only."""
import collections, json, re
recs = json.load(open("runs/stuck_facts/asks_all.json"))
KEY = "What you have been doing:"
rows, examples = [], []
for i, r in enumerate(recs):
    lines = r["prompt"].split("\n")
    idx = [j for j, l in enumerate(lines) if l.startswith(KEY)]
    r["_has"] = bool(idx)
    if idx:
        j = idx[0]
        m = re.match(r"What you have been doing: you have (.*), (\d+) turns? in a row\.$", lines[j])
        tail = []
        k = j + 1
        while k < len(lines) and lines[k] != "Your options:":
            tail.append(lines[k]); k += 1
        r["_line"], r["_n"], r["_tail"] = lines[j], int(m.group(2)) if m else None, tail
        r["_from_end"] = len(lines) - j       # last line of the prompt = 1
        r["_nopts"] = len(lines) - 1 - lines.index("Your options:")
    else:
        # what is just above "Your options:" instead
        k = lines.index("Your options:")
        r["_above"] = lines[k - 1]
def key(r): return (r["dataset"], r["scene"] if r["dataset"] != "v22" else "days 3-10")
tot = collections.OrderedDict()
for r in recs:
    t = tot.setdefault(r["dataset"], collections.Counter())
    t["asks"] += 1; t["shown"] += r["_has"]
    if r["_has"]:
        t[f"n={min(r['_n'],4)}" + ("+" if r["_n"] >= 4 else "")] += 1
        t["tail:" + ("nobody answered" if r["_tail"] and r["_tail"][0].startswith("In that time nobody") else "replies listed")] += 1
print("# share of live day asks whose prompt holds 'What you have been doing:'")
for d, t in tot.items():
    print(f"{d:14s} {t['shown']:3d} of {t['asks']:3d} = {t['shown']/t['asks']:.0%}   " + "  ".join(f"{k}={v}" for k, v in sorted(t.items()) if k not in ("asks", "shown")))
allshown = sum(t["shown"] for t in tot.values()); allasks = sum(t["asks"] for t in tot.values())
print(f"ALL            {allshown:3d} of {allasks:3d} = {allshown/allasks:.0%}")
print()
print("# by person, probes (calm_probe + calm_variants) and talk_probe")
for ds in ("calm_probe", "calm_variants", "talk_probe"):
    for who in ("elena", "leo", "mara", "daniel"):
        rs = [r for r in recs if r["dataset"] == ds and r["who"] == who]
        if rs: print(f"{ds:14s} {who:6s} {sum(r['_has'] for r in rs):3d} of {len(rs):3d}")
print()
print("# v22 per day: shown / asks")
for d in range(3, 11):
    rs = [r for r in recs if r["dataset"] == "v22" and r["day"] == d]
    print(f"day {d:2d}: {sum(r['_has'] for r in rs):3d} of {len(rs):3d}")
print()
print("# distinct 'n' values in the shown lines (all datasets):", dict(sorted(collections.Counter(r['_n'] for r in recs if r['_has']).items())))
print("# distinct verb phrases shown:", dict(collections.Counter(re.match(r'What you have been doing: you have (.*), \d+ turns? in a row', r['_line']).group(1) for r in recs if r['_has'])))
print()
print("# what sits just above 'Your options:' when the line is absent (count, probes then v22)")
for ds in ("calm_probe", "calm_variants", "talk_probe", "v22"):
    c = collections.Counter(re.sub(r"\d\d:\d\d", "HH:MM", r["_above"])[:70] for r in recs if r["dataset"] == ds and not r["_has"])
    print(ds, c.most_common(5))
json.dump([{k: v for k, v in r.items() if k not in ("prompt",)} for r in recs], open("runs/stuck_facts/q2_rows.json", "w"), indent=1)
