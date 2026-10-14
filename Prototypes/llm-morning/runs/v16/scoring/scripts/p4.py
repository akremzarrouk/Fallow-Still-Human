"""P4, read only: every kept memory of runs/v16 (minds 1 and 2, seeds 1-3) with a find/found/food/brought word,
next to that night's trip outcomes. Run from Prototypes/llm-morning/."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
W = re.compile(r"\b(find|finds|found|finding|food|portion|portions|brought|bring|came back with|empty|nothing)\b", re.I)
total = 0
for s in (1, 2, 3):
    tr = json.load(open(f"runs/v16/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    out = {1: tr["night"]["groups"], 2: tr["night2"]["groups"]}
    for k in (1, 2):
        print(f"seed {s} night {k} trips: {[(g.get('members') or g.get('who'), g['outcome']) for g in out[k]]}")
        for pid, r in tr[f"mind{k}"].items():
            for m in r["memories"]:
                if m["verdict"] != "kept":
                    continue
                total += 1
                hits = sorted({h.lower() for h in W.findall(m["meaning"])})
                if hits:
                    print(f"  mind{k} {pid:6} {hits} {m['meaning']!r}")
print("kept memories read:", total)
