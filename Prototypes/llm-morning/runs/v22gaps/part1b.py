"""Part 1b (read only): do a person's own earlier spoken words appear verbatim in their later prompts, and where?
Also the same line said word for word on 2+ days. v22 (cache/v22) and v21 (cache/v21)."""
import collections, json, os, re, sys
sys.path.insert(0, os.getcwd()); sys.argv = ["x"]
exec(open("runs/w22/scoring/w1_score.py", encoding="utf-8").read().split("if __name__")[0])
def run(d, cachef, base):
    t, _ = load(d)
    c = json.load(open(cachef, encoding="utf-8"))
    live = [(c[k]["prompt"], json.loads(c[k]["response"])) for k in list(c)[base:]]
    # all speech acts in order with their prompt via (who, say) matching in order
    said = {q: [] for q in data.ORDER}   # (day, minute, words)
    for k in range(3, DAYS + 1):
        for a in speech(t[f"day{k}"]): said[a["who"]].append((k, a["minute"], a["words"]))
    hits = collections.Counter(); where = collections.Counter(); ex = {}
    ndayprompts = 0
    for p, r in live:
        m = re.match(r"You are (\w+),", p)
        if not m or "Your options:" not in p or "Now it is night" in p: continue
        ndayprompts += 1
        who = next(q for q in data.ORDER if NAME[q] == m.group(1))
        mine = {w for (_, _, w) in said[who] if len(w) >= 25 and w != (r.get("say") or "")}
        # section headings
        sec = None
        for l in p.splitlines():
            if not l.startswith("- "): sec = l[:60]
            for w in mine:
                if w in l:
                    hits[who] += 1; where[sec] += 1; ex.setdefault(who, (sec, l[:200]))
    print(f"{d}: day prompts {ndayprompts}; verbatim own earlier words (>= 25 chars) found in a later prompt of the same person: {sum(hits.values())} lines")
    for q, v in hits.items(): print("   ", NAME[q], v, ex[q])
    print("    by section:", dict(where))
    # same line on 2+ days, same person
    cross = collections.defaultdict(set)
    for q in data.ORDER:
        for (k, m_, w) in said[q]: cross[(q, w)].add(k)
    multi = {key: sorted(v) for key, v in cross.items() if len(v) >= 2}
    cnt = collections.Counter(q for (q, w) in multi)
    print(f"    lines said word for word on 2+ different days: {len(multi)} ({dict((NAME[q], n) for q, n in cnt.items())})")
    for (q, w), days in list(multi.items())[:8]: print("      ", NAME[q], days, w[:110])
    return t
run("runs/v22", "cache/v22/gemini-3.5-flash-lite-daniel_ate_it-seed2.json", 147)
run("runs/v21", "cache/v21/gemini-3.5-flash-lite-daniel_ate_it-seed2.json", 147)
