"""Part 2 of reports/v22_gaps.md (read only, no API): Daniel's bedtime prompts of nights 6-9 and each day's Q5."""
import json, os, re, sys
sys.path.insert(0, os.getcwd()); sys.argv = ["x"]
exec(open("runs/w22/scoring/w1_score.py", encoding="utf-8").read().split("if __name__")[0])
t, _ = load("runs/v22")
pr = live_prompts("cache/v22/gemini-3.5-flash-lite-daniel_ate_it-seed2.json", 147)
npr = [p for p in pr if p["kind"] == "night"]
dec = [(k, x) for k, n in sorted(nights_of(t).items()) for x in n["decisions"] if x["mode"] == "model"]
assert len(dec) == len(npr) and all(NAME[x["person"]] == p["who"] for (_, x), p in zip(dec, npr))
bed = {k: (x, p["text"]) for (k, x), p in zip(dec, npr) if x["person"] == "daniel" and x["ask"] == "bedtime"}

def section(text, head, stop):
    L = text.splitlines(); out = []; on = False
    for l in L:
        if l == head: on = True; out.append(l); continue
        if on and (l.startswith(stop) or (not l.startswith("- ") and not l.startswith(head))):
            break
        if on: out.append(l)
    return out

print("== 2a. Daniel's bedtime prompt, the lines that come from the day just played (v22 cache; files runs/v22gaps/daniel_night<k>_bedtime_prompt.txt)")
for k in (6, 7, 8, 9):
    x, text = bed[k]
    L = text.splitlines()
    print(f"\n-- NIGHT {k}: options {x['options']}; chose {x['option']}; reason: {x.get('reason')!r}")
    print("   Daniel's trip-position acts on day %d: %s" % (k, [(data.clock(a['minute']), a['option'], a['words']) for a in speech(t[f'day{k}']) if a['who'] == 'daniel' and act_of(a['option'])[0] in world.TRIP_KINDS]))
    for head in ("What you are sure of from today:", "Your own last words today:", "What else happened today, most recent last:"):
        for l in section(text, head, "Now it is night"): print("   " + l[:300])
    for l in L:
        if l.startswith("Now it is night") or l.startswith("You said you would") or l.startswith("About going there tonight") \
           or re.match(r"(Against|On your conscience).*today", l):
            print("   " + l[:420])
    print("   'Yesterday and last night' (day %d's own lines? no: day %d's): lines naming a trip: %s" % (k, k - 1, [l[:240] for l in L if l.startswith("- What was said yesterday")]))

print("\n== 2c. each day's Q5 (quiet.log), Daniel's trip positions that day, and the night that followed")
for k in range(3, 11):
    d = t[f"day{k}"]; q = d["quiet"]
    e = next((e for e in q["log"] if e["kind"] == "Q5"), None)
    s = next((s for s in q["stretches"] if s["trigger"] == "Q5"), None)
    pos = [(data.clock(a["minute"]), a["option"]) for a in speech(d) if a["who"] == "daniel" and act_of(a["option"])[0] in world.TRIP_KINDS]
    tp = [a for a in speech(d) if act_of(a["option"])[0] in world.TRIP_KINDS]
    print(f"\nday {k}: trip-position acts {len(tp)}; Daniel's {len(pos)}; Q5 entry: " + (f"fired={e['fired']} asked={e['asked']} room={e['room']} why={e['why']} positions={e.get('positions')}" if e else "NONE"))
    if s:
        ev = [a for a in model_acts(d) if s["start"] <= a["minute"] < s["end"]]
        print(f"   Q5 stretch {data.clock(s['start'])}-{data.clock(s['end'])}, {s['asks']} asks:")
        for a in ev: print(f"      {data.clock(a['minute'])} {NAME[a['who']]} [{a['option']}] {a['words']}")
    if k < 10:
        n = t[nkey(k)]
        b = next(b for b in bedtimes(n) if b["person"] == "daniel")
        print(f"   night {k}: Daniel bedtime {b['option']}; leavers {n['leavers']}; groups {[(g['members'], g['outcome']) for g in n['groups']]}")
