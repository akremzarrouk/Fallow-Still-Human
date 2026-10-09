"""reports/probe_door2.md: reads runs/probe_door2/scene<k>.json (read-only) and prints each scene from the knock, the
counts for the plan's predictions, and how many distinct prompts and answers each turn had across the scenes.

    python runs/probe_door2/read_scenes.py        from Prototypes/llm-morning/
"""
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.getcwd())
import quiet                                            # noqa: E402

OUT = os.path.join("runs", "probe_door2")
recs = {}
for k in range(1, 9):
    path = os.path.join(OUT, f"scene{k}.json")
    if os.path.exists(path):
        recs[k] = json.load(open(path, encoding="utf-8"))
clock = quiet.clock


def answer(text):
    try:
        return json.loads(text)
    except ValueError:
        return {"raw": text}


print(f"scenes recorded: {sorted(recs)}")
for k, rec in recs.items():
    sc, v, knock = rec["scene"], rec["visitor"], rec["knock"]
    print(f"\n=== scene {k} ({rec['spec']['note']}), client seed {rec['client_seed']}")
    print(f"visitor: {v['household']} home {v['home']}, {v['disposition']}, members "
          f"{[(m.get('sex'), m.get('age')) for m in v['members']]}, need_w {v['need_w']:.2f} need_f {v['need_f']:.2f} "
          f"urgency {v['urgency']:.2f}, {v['purpose']}")
    print(f"who {sc['who']!r}; voice {sc['voice']!r}; knocks {[clock(m) for m in sc['knocks']]}; "
          f"start {clock(sc['start'])} end {sc['end'] and clock(sc['end'])}; outcome {sc['outcome']}; "
          f"door asks {sc['door_asks']}; stretch asks {sc['asks']}; give {sc['give']}")
    print(f"by_knock {[(clock(m), h) for m, h in sc['by_knock']]}; saw {sc['saw']}")
    events = []
    for m, text in sc["said"]:
        events.append((m, 0, f"the visitor: \"{text}\" (heard by "
                       f"{sorted(q for q, ls in sc['heard_said'].items() if any(x[0] == m for x in ls))})"))
    for d in rec["decisions"]:
        if d["mode"] != "model" and d["option"] == "silent" and d["at_door"] is None and not d.get("invalid"):
            tag = f"{d['mode']}"
        else:
            tag = d["mode"]
        words = f" — \"{d['say']}\"" if d["say"] else ""
        extra = f" [invalid: {d['invalid']}]" if d.get("invalid") else ""
        events.append((d["minute"], 1, f"{d['who']} ({d['room']}, at_door {d['at_door']}, {tag}): {d['option']}{words}. "
                       f"Feeling: {d['feeling']}. Reason: \"{d['reason']}\"{extra}"))
    for m, _, line in sorted(events, key=lambda e: (e[0], e[1])):
        print(f"  {clock(m)} {line}")
    print("  each one's line of it:")
    for q, line in sc["summary"].items():
        print(f"    {q}: {line}")

print("\n=== P1: door_give in scenes 1 to 6")
for k, rec in recs.items():
    if k <= 6:
        gives = [a for a in rec["scene"]["acts"] if a[2] == "door_give"]
        print(f"scene {k}: {gives or 'none'}")

print("\n=== P2: someone at the door chooses an ordinary option while the visitor is there")
for k, rec in recs.items():
    end = rec["scene"]["end"]
    hits = [(d["clock"], d["who"], d["option"]) for d in rec["decisions"]
            if d["mode"] == "model" and d["at_door"] and not d["option"].startswith("door_")
            and d["option"] != "silent" and rec["knock"] <= d["minute"] <= (end if end is not None else 10 ** 6)]
    print(f"scene {k}: {'yes' if hits else 'no'} {hits}")

print("\n=== P3: Elena's words to the visitor in the water scenes")
for k, rec in recs.items():
    if k <= 6:
        lines = [(d["clock"], d["option"], d["say"]) for d in rec["decisions"]
                 if d["who"] == "elena" and d["option"] in ("door_call", "door_refuse")]
        print(f"scene {k}: {lines or 'Elena did not speak to the visitor'}")

print("\n=== distinct prompts and answers per turn across scenes, by (minute, person)")
groups = defaultdict(list)
for k, rec in recs.items():
    for p in rec["prompts"]:
        groups[(p["minute"], p["who"])].append((k, p["prompt"], p["answer"]))
for (m, who), items in sorted(groups.items()):
    by_prompt, by_answer = defaultdict(list), defaultdict(list)
    for k, pr, an in items:
        by_prompt[pr].append(k)
        by_answer[an].append(k)
    opts = sorted({answer(an).get("option", "?") for _, _, an in items})
    print(f"({clock(m)}, {who}) scenes {len(items)}: distinct prompts {len(by_prompt)} {sorted(by_prompt.values())}; "
          f"distinct answers {len(by_answer)} {sorted(by_answer.values())}; options {opts}")

print("\n=== identical prompts with different answers (the seed at work), knock minute")
for (m, who), items in sorted(groups.items()):
    by_prompt = defaultdict(list)
    for k, pr, an in items:
        by_prompt[pr].append((k, an))
    for pr, ks in by_prompt.items():
        if len(ks) > 1:
            print(f"({clock(m)}, {who}) one prompt in scenes {[k for k, _ in ks]}: distinct answers "
                  f"{len({an for _, an in ks})}; options {[answer(an).get('option') for _, an in ks]}")

print("\n=== the knock-minute prompt lines about the door (scene by scene, Elena)")
for k, rec in recs.items():
    p = next((p for p in rec["prompts"] if p["minute"] == rec["knock"] and p["who"] == "elena"), None)
    if p:
        lines = [ln for ln in p["prompt"].splitlines() if re.search(r"door|knock|voice", ln, flags=re.I)]
        print(f"scene {k}:")
        for ln in lines:
            print(f"  {ln}")
