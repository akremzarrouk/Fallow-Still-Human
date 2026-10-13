"""Q1. Repetition, measured. Read-only. Inputs: runs/stuck_facts/asks.json (probes), asks_v22.json (v22 replay).
Unit = (dataset, scene, variant, person, day): the live day-phase asks of one person in one day, in the order asked.
Per unit: n asks; the most-chosen option, its count and share; the longest run of the same option over consecutive asks
of that person (same unit); the pairs of answers whose words share >= 60%.
Words: the `say` text, lower-cased, letters/digits/apostrophes only, split on whitespace; a set of distinct words.
Share of two answers A, B (sets): |A and B| / max(|A|, |B|) -- each answer has at least 60% of its words in the other.
Also printed: Jaccard >= 0.6, and |A and B| / min(|A|,|B|) >= 0.6, and word-for-word equal; `silent` has no words and is not paired."""
import collections, itertools, json, re, sys
sys.path.insert(0, ".")

def words(say):
    return set(re.findall(r"[a-z0-9']+", (say or "").lower()))

def pairs(rows):
    out = []
    ws = [(r, words(r["say"])) for r in rows if r["say"]]
    for (a, wa), (b, wb) in itertools.combinations(ws, 2):
        if not wa or not wb:
            continue
        inter = len(wa & wb)
        out.append(dict(a=a["clock"], b=b["clock"], oa=a["option"], ob=b["option"],
                        eq=(a["say"].strip().lower() == b["say"].strip().lower()),
                        cmax=inter / max(len(wa), len(wb)), jac=inter / len(wa | wb), cmin=inter / min(len(wa), len(wb))))
    return out

def runs(rows):
    best, cur, prev = 0, 0, None
    for r in rows:
        cur = cur + 1 if r["option"] == prev else 1
        prev = r["option"]; best = max(best, cur)
    return best

def kind_runs(rows):
    from talk import act_of
    best, cur, prev = 0, 0, None
    for r in rows:
        k = act_of(r["option"])[0]
        cur = cur + 1 if k == prev else 1
        prev = k; best = max(best, cur)
    return best

recs = json.load(open("runs/stuck_facts/asks.json"))
v22 = json.load(open("runs/stuck_facts/asks_v22.json"))
for i, a in enumerate(v22):
    pass
for a in v22:
    m = re.match(r"day(\d+)$", a["scene"])
    if not m or int(m.group(1)) < 3:
        continue
    ans = json.loads(a["answer"])
    clk = re.search(r"\nNow, (.*?), you are", a["prompt"])
    recs.append(dict(dataset="v22", scene="day" + m.group(1), variant="", day=int(m.group(1)), minute=None,
                     clock=clk.group(1) if clk else None, who=re.match(r"You are (\w+),", a["prompt"]).group(1).lower(),
                     option=ans["option"], say=ans.get("say"), prompt=a["prompt"], source="live"))
json.dump(recs, open("runs/stuck_facts/asks_all.json", "w"), indent=1)
# cross-check: v22's model decisions in the transcript, per day and person, in order, equal this replay's asks
t = json.load(open("runs/v22/daniel_ate_it-seed2.transcript.json"))
bad = 0
for d in range(3, 11):
    tr = collections.defaultdict(list)
    for turn in t[f"day{d}"]["turns"]:
        for a in turn["acts"]:
            if a["mode"] == "model":
                tr[a["who"]].append(a["option"])
    mine = collections.defaultdict(list)
    for r in recs:
        if r["dataset"] == "v22" and r["day"] == d:
            mine[r["who"]].append(r["option"])
    ok = all(tr[w] == mine[w] for w in set(tr) | set(mine))
    bad += not ok
    print(f"check v22 day {d}: transcript model acts {sum(map(len, tr.values()))}, replay asks {sum(map(len, mine.values()))}, same order per person: {ok}")
print("check v22 days that differ:", bad)
print()

units = collections.OrderedDict()
for i, r in enumerate(recs):
    r["_i"] = i
    units.setdefault((r["dataset"], str(r["scene"]), r["variant"], r["who"], r["day"]), []).append(r)

rows = []
for key, rs in units.items():
    # probes: order by minute (rows were written in minute order); v22: order asked (the replay's order)
    if key[0] != "v22":
        rs.sort(key=lambda r: (r["minute"], r["_i"]))
    c = collections.Counter(r["option"] for r in rs)
    top, tn = c.most_common(1)[0]
    ps = pairs(rs)
    rows.append(dict(dataset=key[0], scene=key[1], variant=key[2], who=key[3], day=key[4], n=len(rs), top=top, top_n=tn,
                     share=tn / len(rs), run=runs(rs), kind_run=kind_runs(rs), kind_run_ok=True,
                     silent=c.get("silent", 0), spoken=sum(1 for r in rs if r["say"]),
                     pairs=len(ps), eq=sum(p["eq"] for p in ps), c60=sum(p["cmax"] >= .6 for p in ps),
                     jac60=sum(p["jac"] >= .6 for p in ps), min60=sum(p["cmin"] >= .6 for p in ps),
                     options=dict(c), seq=[r["option"] for r in rs], pair_list=[p for p in ps if p["cmax"] >= .6]))
json.dump(rows, open("runs/stuck_facts/q1_units.json", "w"), indent=1)

def show(r, long=False):
    print(f"{r['dataset']:13s} {r['scene']:>5s} {r['variant']:>2s} {r['who']:6s} d{r['day']:<2d} n={r['n']:<2d} top={r['top']:<18s} {r['top_n']}/{r['n']} = {r['share']:.0%}  "
          f"run={r['run']}  spoken={r['spoken']}  pairs={r['pairs']}  >=60%: {r['c60']} (jac {r['jac60']}, min {r['min60']})  equal: {r['eq']}")

print("# UNITS (dataset, scene, variant, person, day)")
for r in rows:
    show(r)
print()
print("# SEQUENCES (options in the order asked)")
for r in rows:
    print(r["dataset"], r["scene"], r["variant"], r["who"], "d%d" % r["day"], " ".join(r["seq"]))
print()
print("# POOLED PER PERSON, calm_variants + calm_probe (live rows only, both scenes, all variants)")
for who in ("elena", "leo", "mara"):
    rs = [r for r in recs if r["dataset"] in ("calm_variants", "calm_probe") and r["who"] == who]
    c = collections.Counter(r["option"] for r in rs)
    top, tn = c.most_common(1)[0]
    ps = pairs(rs)
    print(f"{who:6s} live answers={len(rs)}  most-chosen={top} {tn}/{len(rs)}={tn/len(rs):.0%}  all options={dict(c)}  pairs={len(ps)}  >=60%: {sum(p['cmax']>=.6 for p in ps)}  equal: {sum(p['eq'] for p in ps)}")
print()
print("# POOLED PER PERSON, calm_variants + calm_probe, by version")
for who in ("elena", "leo", "mara"):
    for var in ("P", "T", "O", "TO"):
        rs = [r for r in recs if r["dataset"] in ("calm_variants", "calm_probe") and r["who"] == who and r["variant"] == var]
        c = collections.Counter(r["option"] for r in rs)
        print(f"{who:6s} {var:2s} n={len(rs)} {dict(c)}")
