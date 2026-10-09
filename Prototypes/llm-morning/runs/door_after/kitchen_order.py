"""reports/door_after_facts.md, Q5: the kitchen's acting order in the two noon traces, 09:42 to 09:57, with each one's
reason (world.py next_to_act), from runs/door_after/noon_scene<k>.json. Read-only.

    python runs/door_after/kitchen_order.py        from Prototypes/llm-morning/
"""
import json

for k in (1, 2):
    o = json.load(open(f"runs/door_after/noon_scene{k}.json", encoding="utf-8"))
    by = {}
    for a in o["asks"]:
        if a["room"] == "kitchen" and a["minute"] <= 177:
            by.setdefault(a["clock"], []).append(f"{a['order'][0]}. {a['who']} ({a['order'][1]})")
    print(f"scene {k}:")
    for c, xs in by.items():
        print(f"  {c}: " + "; ".join(sorted(xs)))
