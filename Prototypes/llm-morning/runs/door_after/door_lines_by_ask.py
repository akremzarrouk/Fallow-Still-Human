"""reports/door_after_facts.md: for each ask of day 3 after the visit in runs/door_after/full_scene1.json, which door
lines its prompt holds (the lines trace.py's filter keeps, but the About water line). Read-only.

    python runs/door_after/door_lines_by_ask.py        from Prototypes/llm-morning/
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import quiet                                            # noqa: E402

o = json.load(open(os.path.join("runs", "door_after", "full_scene1.json"), encoding="utf-8"))
for a in o["asks"]:
    if not a["asked"] or a["minute"] <= 162:
        continue
    lines = [x for x in a["door_lines"] or [] if not x.startswith("About water")
             and ("09:4" in x or "visitor" in x or "person at the door" in x or "front door says" in x
                  or "Footsteps" in x or "handed a woman" in x)]
    water = [x for x in a["door_lines"] or [] if x.startswith("About water")]
    print(f"{a['clock']} {a['who']} ({a['room']}, {a['source']}): {len(lines)} door line(s)"
          + "".join(f"\n    | {x}" for x in lines) + (f"\n    | water: {water[0][water[0].find('Since'):] if water and 'Since' in water[0] else '(no rule)'}"))
