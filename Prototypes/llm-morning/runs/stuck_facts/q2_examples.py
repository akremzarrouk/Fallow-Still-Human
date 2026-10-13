"""Q2 examples: the pattern line and what follows it, from named asks in runs/stuck_facts/asks_all.json. Read-only."""
import json

recs = json.load(open("runs/stuck_facts/asks_all.json"))
WANT = [("talk_probe", "4", "mara", "14:51"), ("talk_probe", "4", "leo", "11:51"), ("talk_probe", "1", "daniel", "09:45"),
        ("talk_probe", "1", "elena", "09:45"), ("v22", "day3", "mara", "minute 09"), ("v22", "day10", "daniel", None)]
for ds, scene, who, clock in WANT:
    rs = [r for r in recs if r["dataset"] == ds and str(r["scene"]) == scene and r["who"] == who and (clock is None or r["clock"] == clock)]
    for r in rs:
        L = r["prompt"].split("\n")
        js = [i for i, l in enumerate(L) if l.startswith("What you have been doing")]
        if not js:
            continue
        j = js[0]
        tail = []
        k = j + 1
        while L[k] != "Your options:":
            tail.append(L[k])
            k += 1
        if clock is None and not (L[j].endswith("2 turns in a row.") and r["option"] == "still_going"):
            continue
        print(f"## {ds} scene {scene} {who} {r['clock']} (chose {r['option']}); the line is line {j+1} of {len(L)}, {len(L)-j} from the end")
        print("   " + L[j])
        for t in tail:
            print("   " + t)
        print()
        break
