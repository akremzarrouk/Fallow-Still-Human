"""reports/probe_door2.md: the body, food and water lines and the `Now` block of each prompt of scenes 1 to 3
(read-only).

    python runs/probe_door2/prompt_lines.py        from Prototypes/llm-morning/
"""
import json

for k in (1, 2, 3):
    r = json.load(open(f"runs/probe_door2/scene{k}.json", encoding="utf-8"))
    for p in r["prompts"]:
        lines = p["prompt"].splitlines()
        water = [l for l in lines if l.startswith("About water") or l.startswith("About food") or l.startswith("Your body")]
        i = next(i for i, l in enumerate(lines) if l.startswith("Now, "))
        j = next(i for i, l in enumerate(lines) if l.startswith("Your options:"))
        print(f"--- scene {k}, {p['who']} at {p['minute']}")
        for l in water:
            print("  " + l)
        for l in lines[i:j]:
            print("  " + l)
