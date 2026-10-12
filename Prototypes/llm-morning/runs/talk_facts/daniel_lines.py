"""reports/talk_facts.md, question 3: what Daniel's prompts in runs/probe_after/scene1.json hold about the water and
the front door, from the knock (09:42) on. Read-only.

    python runs/talk_facts/daniel_lines.py        from Prototypes/llm-morning/
"""
import json, os, re, sys
sys.path.insert(0, os.getcwd())
from quiet import clock
r = json.load(open(os.path.join("runs", "probe_after", "scene1.json"), encoding="utf-8"))
asks = [a for a in r["asks"] if a["who"] == "daniel"]
print(f"Daniel's asks recorded from the knock: {len(asks)} ({[(a['phase'], clock(a['minute']) if a['minute'] is not None else None) for a in asks]})")
door = re.compile(r"front door|knock|stranger|visitor|woman|handed|go away", re.I)
for a in asks:
    when = clock(a["minute"]) if a["minute"] is not None else a["phase"]
    w = [l for l in a["prompt"].splitlines() if l.startswith("About water:")]
    d = [l for l in a["prompt"].splitlines() if door.search(l) and not l.startswith("The house:")]
    print(f"\n{a['phase']} {when}: water line: {w}")
    print(f"  lines (but the fixed 'The house:' line) naming the door, a knock, a stranger, a woman, handing or 'go away': {d}")
print("\nDaniel's night-3 mind records (mind_input.daniel.records), those from 09:42 to 10:00:")
for i, t in r["mind_input"]["daniel"]["records"]:
    if re.match(r"(09:4\d|09:5\d)", t):
        print(f"  [{i}] {t}")
