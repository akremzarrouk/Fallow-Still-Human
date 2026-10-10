"""reports/probe_after.md: Mara's and Elena's memory lines from 09:45 to 09:51 in each scene (read-only), to show who
was in the kitchen when Elena was asked.

    python runs/probe_after/memory_0945.py        from Prototypes/llm-morning/
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
import quiet
for k in (1, 3, 4):
    r = json.load(open(os.path.join("runs", "probe_after", f"scene{k}.json"), encoding="utf-8"))
    print("scene", k)
    for pid in ("mara", "elena"):
        for a, b in r["memory"][pid]:
            if 165 <= a <= 171:
                print(f"  {pid} {quiet.clock(a)} {b}")
