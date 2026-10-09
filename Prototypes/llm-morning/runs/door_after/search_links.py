"""reports/door_after_facts.md, Q1: in every prompt after 09:42 of the two noon traces, the lines (before "Your
options:") that could link the give to the refusal, and the options offered. Read-only.

    python runs/door_after/search_links.py        from Prototypes/llm-morning/
"""
import json
import re

PAT = re.compile(r"overr|despite|against (?:Elena|Mara|your)|although|even though|after Elena|refus|defi|disobey", re.I)
for k in (1, 2):
    o = json.load(open(f"runs/door_after/noon_scene{k}.json", encoding="utf-8"))
    allopts = set()
    for p in o["prompts"]:
        if p["minute"] <= 162:
            continue
        body, _, opts = p["prompt"].partition("Your options:")
        hits = [ln for ln in body.splitlines() if PAT.search(ln)]
        allopts |= set(re.findall(r"^- (\w+):", opts, flags=re.M))
        if hits:
            print(k, p["minute"], p["who"], hits)
    print(k, "options offered after 09:42:", sorted(allopts))
