"""reports/talk_facts.md, questions 4 and 5: the stores lines of Leo's night-3 mind prompt, and day 4's blocks and
water line, in runs/probe_after/scene1.json. Read-only.

    python runs/talk_facts/stores_lines.py        from Prototypes/llm-morning/
"""
import json, os, re
r = json.load(open(os.path.join("runs", "probe_after", "scene1.json"), encoding="utf-8"))
STORES = re.compile(r"water|litre|portion|shelf|food|store|pantry|can\b|tin|ration|cup", re.I)

print("==== Q4: Leo's night-3 mind prompt (mind_input.leo.prompt)")
lp = r["mind_input"]["leo"]["prompt"]
print(f"prompt lines: {len(lp.splitlines())}")
for i, l in enumerate(lp.splitlines(), 1):
    if l.startswith("About ") or l.startswith("Your body") or l.startswith("Against"):
        print(f"  head line {i}: {l}")
print("  lines starting 'About water:' / 'About food:':",
      [l for l in lp.splitlines() if l.startswith(("About water:", "About food:"))])
print("  every line naming water, litres, portions, the shelf, food or the store:")
for i, l in enumerate(lp.splitlines(), 1):
    if STORES.search(l):
        print(f"  {i}: {l}")

print("\n==== Q5: day 4's blocks (day4_blocks)")
b = r["day4_blocks"]
print(f"type: {type(b).__name__}; keys: {list(b) if isinstance(b, dict) else None}")
print(json.dumps(b, ensure_ascii=False, indent=1))
print("\n==== other keys that may hold a day-4 water line or prompt")
for k, v in r.items():
    s = json.dumps(v, ensure_ascii=False)
    if "About water" in s:
        hits = sorted(set(re.findall(r'About water:[^"]*', s.replace('\\"', "'"))))
        print(f"  {k}: {len(hits)} distinct 'About water:' lines")
        for h in hits[-6:]:
            print(f"     {h}")
