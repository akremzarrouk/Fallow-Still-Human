"""reports/calm_probe.md: read-only. P1 and P2 as reports/calm_probe_plan.md counts them, every calm ask in full, and
for each prompt the lines that bear on the visit and on Daniel, from runs/calm_probe/scene<k>.json.

    python runs/calm_probe/read_calm.py        from Prototypes/llm-morning/
"""
import json
import os
import re

FOLDER = os.path.join("runs", "calm_probe")
asks = []
for k in (1, 3):
    r = json.load(open(os.path.join(FOLDER, f"scene{k}.json"), encoding="utf-8"))
    print(f"scene {k}: seed {r['seed']}; replay {r['replay']}; calm {r['calm']}; stopped {r['stopped']}")
    print(f"  visit {r['visit']}")
    print(f"  how each minute was reached: {r['how']}")
    for mo in r["moments"]:
        print(f"  {mo['clock']}: Daniel in {mo['daniel_room']}, resting {mo['daniel_resting']}, beliefs "
              f"{mo['daniel_beliefs']}; here {mo['here']}")
        for a in mo["asks"]:
            asks.append((k, a))

tell = [(k, a) for k, a in asks if any(o.startswith("tell_") and o.endswith("_visit") for o in a["offered"])]
took = [(k, a) for k, a in tell if a["option"] in [o for o in a["offered"] if o.startswith("tell_") and o.endswith("_visit")]]
print(f"\nP1: asks offering a tell_*_visit option: {len(tell)}; choosing one: {len(took)}; share "
      f"{len(took) / len(tell) if tell else None}")
print(f"P2: answers choosing an option not offered: {[(k, a['clock'], a['who'], a['option']) for k, a in asks if not a['valid']]} "
      f"(of {len(asks)} asks)")

print("\n==================== every ask in full")
for k, a in asks:
    opts = a["offered"]
    pos = {o: i + 1 for i, o in enumerate(opts)}
    print(f"\n-- scene {k}, {a['clock']}, {a['who']}, client seed {a['seed']}")
    print(f"   offered ({len(opts)}): {opts}")
    print(f"   topic options: {[(o, a['labels'][o], 'position ' + str(pos[o])) for o in a['topic_offered']]}")
    print(f"   chose: {a['option']} ({a['labels'].get(a['option'])})")
    print(f"   say: {a['say']!r}")
    print(f"   feeling: {a['feeling']!r}; reason: {a['reason']!r}; suspects {a['suspects']}; angry_at {a['angry_at']}")
    lines = a["prompt"].splitlines()
    door = [l for l in lines if re.search(r"front door|knock|woman|stranger|handed|visitor|boy", l)
            and not l.startswith("The house:")]
    print(f"   prompt lines about the visit: {door}")
    print(f"   prompt lines against or about Daniel (grudges, can): "
          f"{[l for l in lines if l.startswith(('Against Daniel', 'About the can', 'About going out'))]}")
    now = lines.index(next(l for l in lines if l.startswith("Now, ")))
    print(f"   Now block: {lines[now - 3:now + 6]}")
    print(f"   prompt: {len(lines)} lines, {len(a['prompt'])} characters")
