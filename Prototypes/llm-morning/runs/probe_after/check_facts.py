"""reports/probe_after.md: read-only checks on runs/probe_after/scene<k>.json: the water each one was told of in their
last day-3 prompt and in their night-mind prompt; the night minds' warnings; Mara's memory 09:45 to 09:51; Elena's
prompt lines about the door at her 09:45 and 09:48 asks.

    python runs/probe_after/check_facts.py        from Prototypes/llm-morning/
"""
import json, os, re, sys
sys.path.insert(0, os.getcwd())
import quiet
clock = quiet.clock
for k in (1, 3, 4):
    r = json.load(open(os.path.join("runs", "probe_after", f"scene{k}.json"), encoding="utf-8"))
    print(f"=== scene {k}")
    day = [a for a in r["asks"] if a["phase"] == "day" and a["who"]]
    for pid in ("elena", "leo", "mara"):
        last = [a for a in day if a["who"] == pid][-1]
        w = re.findall(r"^About water:.*$", last["prompt"], flags=re.M)
        print(f"  {pid} last day-3 ask {clock(last['minute'])}: {w}")
        mp = r["mind_input"].get(pid, {}).get("prompt", "")
        print(f"  {pid} night-mind prompt water lines: {[l for l in mp.splitlines() if re.search(r'litre|water', l, re.I)][:12]}")
    for pid, m in r["minds"].items():
        if m.get("warnings"):
            print(f"  mind warnings {pid}: {m['warnings']}")
    print(f"  mara memory 09:42-09:54: {[(clock(a), b) for a, b in r['memory']['mara'] if a <= 174]}")
    for a in day:
        if a["who"] == "elena" and a["minute"] in (165, 168):
            lines = [l for l in a["prompt"].split("Your options:")[0].splitlines()
                     if re.search(r"front door|stored water|handed|go away|About water|Mara", l) and not l.startswith("The house:")]
            print(f"  elena prompt {clock(a['minute'])} door/water/Mara lines:")
            for l in lines:
                print(f"    | {l}")
            opts = re.findall(r"^- (\w+):", a["prompt"].split("Your options:")[-1], flags=re.M)
            print(f"    options offered: {opts}")
    ev = [e for e in r["day3_events"] if e["kind"] == "save_water"] + [e for e in r.get("day3_events", [])]
    print(f"  stretches {[(clock(s['start']), clock(s['end']) if s['end'] else None, s['trigger'], s['asks']) for s in r['stretches']]}")
