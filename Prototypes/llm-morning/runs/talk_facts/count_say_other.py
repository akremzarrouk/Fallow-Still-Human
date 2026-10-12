"""reports/talk_facts.md, question 1: how often say_other was chosen in the cached (live-received) answers of
cache/v16, cache/probe_door2 and cache/probe_after. Read-only. Each cache entry is one answer received from the model
(gemini.Cache.put); probe caches start as copies of earlier ones, so answers are also counted once by cache key.

    python runs/talk_facts/count_say_other.py        from Prototypes/llm-morning/
"""
import glob, json, os, re

def parse(resp):
    try:
        return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", (resp or "").strip()))
    except ValueError:
        return None

seen = {}
for folder in ("cache/v16", "cache/probe_door2", "cache/probe_after"):
    tot = {"entries": 0, "decisions": 0, "say_other": 0}
    for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        n = {"entries": len(d), "decisions": 0, "say_other": 0}
        for k, e in d.items():
            a = parse(e["response"])
            opt = a.get("option") if isinstance(a, dict) else None
            if opt is not None:
                n["decisions"] += 1
            if opt == "say_other":
                n["say_other"] += 1
            seen.setdefault(k, (opt, path, e))
        print(f"{path}: {n}")
        for x in n:
            tot[x] += n[x]
    print(f"== {folder} total (with copies): {tot}")
uniq = [v for v in seen.values()]
print(f"== distinct cache keys over all three: {len(uniq)}; with an option: {sum(1 for o, _, _ in uniq if o)}; "
      f"say_other: {sum(1 for o, _, _ in uniq if o == 'say_other')}")
for o, path, e in uniq:
    if o == "say_other":
        a = parse(e["response"])
        who = re.match(r"You are (\w+)", e["prompt"]).group(1)
        now = re.findall(r"^Time: .*$|^It is .*$", e["prompt"], flags=re.M)[:1]
        print(f"  {path} | {who} | {now} | say: {a.get('say')!r}")

# How often it was offered: decisions whose prompt lists "- say_other:" among its options.
offered = [(o, path, e) for o, path, e in uniq if o and re.search(r"^- say_other:", e["prompt"], flags=re.M)]
print(f"== distinct decisions whose prompt offered say_other: {len(offered)} of {sum(1 for o, _, _ in uniq if o)}")
lines = {re.search(r"^- say_other:.*$", e["prompt"], flags=re.M).group(0) for _, _, e in offered}
print(f"   its option line, as offered: {sorted(lines)}")
for o, path, e in uniq:
    if o == "say_other":
        p = e["prompt"]
        print("   the say_other answer's prompt, lines with a time or 'Now':")
        for l in p.splitlines():
            if re.search(r"\b(Now|It is|minute|Day \d|morning)\b", l) and len(l) < 300:
                print(f"     | {l}")
        print(f"   response: {e['response']}")
