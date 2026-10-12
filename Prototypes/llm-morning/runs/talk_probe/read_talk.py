"""reports/talk_probe.md: read-only. V2 to V5 and P1 to P6 as reports/talk_probe_plan.md counts them, then what the
report shows of each scene, from runs/talk_probe/scene<k>.json (or another folder given as the first argument) and
runs/probe_after/scene<k>.json (for the Q1 that probe_after refused).

    python runs/talk_probe/read_talk.py [folder]        from Prototypes/llm-morning/
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import quiet                                            # noqa: E402
import topics                                           # noqa: E402

FOLDER = sys.argv[1] if len(sys.argv) > 1 else os.path.join("runs", "talk_probe")
SCENES = (1, 3, 4)
END = 165                                               # 09:45: the visit's end, in every scene
WORDS = re.compile(r"\b(woman|visitor|stranger|front door|knock\w*|boy|girl|child|children|kids?)\b", re.I)
KIDS = re.compile(r"\b(boy|girl|child|children|kids?|son|daughter|little one)\b", re.I)
DOOR = re.compile(r"front door|knock|told you that|woman|stranger|visitor|handed|go away", re.I)
clock = quiet.clock


def load(folder, k):
    path = os.path.join(folder, f"scene{k}.json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def topic_of(option):
    return topics.suffix_of(option) if option.startswith(("talk_", "tell_")) else None


def day3(rec):
    """Day-3 decisions from 09:45 (the counting rules' "day 3")."""
    return [d for d in rec["decisions"] if d["minute"] >= END]


ledger = json.load(open(os.path.join(FOLDER, "ledger.json"), encoding="utf-8"))
recs = {k: load(FOLDER, k) for k in SCENES}
after = {k: load(os.path.join("runs", "probe_after"), k) for k in SCENES}
print(f"folder: {FOLDER}")
print(f"ledger: live {ledger['live']}; phases "
      f"{[(p['phase'], p['seed'], p.get('reached'), p.get('stopped'), p['live_before'], p.get('live_after')) for p in ledger['phases']]}")

# ==================== the validity checks ====================
print("\n==================== V2 to V5")
v = {}
v["V2"] = {k: (r["counts"]["from_cache"], r.get("stopped")) for k, r in recs.items() if r}
print(f"V2 from_cache and stop, per scene: {v['V2']}")
v3 = {k: [(ph, mm, who, o) for ph, mm, who, o in r["topic_scan"] if ph == "day" and mm is not None and mm < END and o]
      for k, r in recs.items() if r}
print(f"V3 prompts before 09:45 with a topic option: {v3}; prompts scanned per scene "
      f"{ {k: len(r['topic_scan']) for k, r in recs.items() if r} }; of them day prompts before 09:45 "
      f"{ {k: sum(1 for ph, mm, *_ in r['topic_scan'] if ph == 'day' and mm is not None and mm < END) for k, r in recs.items() if r} }")
v4 = []
for k, r in recs.items():
    if not r:
        continue
    for t in r["tells"]:
        entry = r["topics"][t["teller"]][t["topic"]]
        for x in t["listeners"]:
            want = topics.claim(entry, t["teller"], x, r["day"])
            got = [b["claim"] for b in r["beliefs"][x] if b["source"] == t["teller"] and b["minute"] == t["minute"]]
            v4.append((k, clock(t["minute"]), t["teller"], x, got == [want]))
print(f"V4 (teller, listener) claims equal to the builder's: {v4}")
v5 = {}
for k, r in recs.items():
    if not r:
        continue
    counts = {}
    for d in day3(r):
        t = topic_of(d["option"])
        if t:
            counts[(d["who"], t)] = counts.get((d["who"], t), 0) + 1
    v5[k] = counts
print(f"V5 / P3 topic choices per (person, topic), day 3: {v5}")

# ==================== the predictions ====================
print("\n==================== P1 to P6")
p1 = {}
for k, r in recs.items():
    if not r:
        continue
    end = r["door_end_id"]
    events = [e for e in r["tell_events"] if e["kind"] == "tell" and "daniel" in (e["members"] or [])]
    beliefs = [b for b in r["beliefs"]["daniel"] if end in b["about"]]
    p1[k] = {"tell events to daniel": [(e["id"], clock(e["minute"]), e["actor"]) for e in events],
             "tell event has 'about'": any("about" in e for e in events),
             "daniel's beliefs about door_end": [(clock(b["minute"]), b["source"]) for b in beliefs],
             "counts": bool(beliefs)}
print(f"P1 per scene: {p1}")
print(f"P1 scenes that count: {[k for k in p1 if p1[k]['counts']]}")
p2 = {}
for k, r in recs.items():
    if not r:
        continue
    hits = []
    for d in r["decisions"]:
        if d["minute"] < 180:
            continue
        opt = d["option"] or ""
        by_opt = opt == "talk_visit" or (opt.startswith("tell_") and opt.endswith("_visit"))
        m = WORDS.search(d.get("say") or "")
        if by_opt or m:
            hits.append((clock(d["minute"]), d["who"], opt, m.group(0) if m else None))
    p2[k] = hits
print(f"P2 per scene (minute >= 10:00, the option or the words): {p2}")
print(f"P2 scenes that count: {[k for k in p2 if p2[k]]}")
print(f"P3 counts > 2: {[(k, w, n) for k, c in v5.items() for w, n in c.items() if n > 2]}")
num = den = 0
per = {}
for k, r in recs.items():
    if not r:
        continue
    for a in r["asks"]:
        if a["phase"] != "day" or a["mind"] or a["minute"] is None or a["minute"] < END:
            continue
        offered = re.findall(r"^- ((?:talk|tell)_\w+):", a["prompt"], flags=re.M)
        if not offered:
            continue
        try:
            chose = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", a["answer"].strip())).get("option")
        except (ValueError, AttributeError):
            chose = None
        took = chose in offered
        den += 1
        num += took
        per.setdefault(k, []).append((clock(a["minute"]), a["who"], offered, chose, took))
print(f"P4 decisions offering a topic option: {den}; choosing one: {num}; share {num / den if den else None}")
for k, xs in per.items():
    print(f"  scene {k}: {xs}")
p5 = {}
for k in p1:
    if not p1[k]["counts"]:
        continue
    lines = [x[2:] if x.startswith("- ") else x for x in recs[k]["day4_blocks"]["daniel"]["A"]]
    p5[k] = [x for x in lines if x.startswith("Yesterday at") and "told you that at 09:42" in x]
print(f"P5 Daniel's day-4 block A lines (bullet removed) starting 'Yesterday at' with 'told you that at 09:42': {p5}")
p6 = {}
for k in (3, 4):
    r = recs.get(k)
    if not r:
        continue
    first = next(e for e in r["day3_events"] if e["kind"] == "door_line")        # the line that names the children
    want = {3: "boy of six", 4: "girl and boy of five"}[k]
    p6[k] = [(clock(b["minute"]), b["source"], b["source"] in first["witnesses"], want in b["claim"])
             for b in r["beliefs"]["daniel"] if r["door_end_id"] in b["about"]]
print(f"P6 per scene, Daniel's claims (minute, teller, teller heard the line naming the children, names them): {p6}")

# ==================== what the report shows ====================
for k, r in recs.items():
    if not r:
        continue
    print(f"\n==================== scene {k} ({r['spec']['note']}, client seed {r['client_seed']}): "
          f"reached {r['reached']}; counts {r['counts']}; stopped {r.get('stopped')}")
    sc = r["scene"]
    print(f"visit {clock(sc['start'])} to {clock(sc['end'])}; outcome {sc['outcome']}; acts "
          f"{[(clock(a[0]), a[1], a[2]) for a in sc['acts']]}; door_end {r['door_end_id']}")
    print(f"first door line: {next(e['words'] for e in r['day3_events'] if e['kind'] == 'door_line')!r}")
    print("-- every talk and tell decision:")
    for d in r["decisions"]:
        if topic_of(d["option"] or ""):
            print(f"  {d['clock']} {d['who']} [{d['mode']}] {d['option']}: say {d['say']!r}; feeling {d['feeling']!r}; "
                  f"reason {d['reason']!r}")
    print("-- the tells (topics.tell) and T1:")
    for t in r["tells"]:
        print(f"  {clock(t['minute'])} {t['teller']} -> {t['listeners']}: words {t['words']!r}; T1 {t['warnings']}")
        for x, c in t["claims"].items():
            print(f"     claim for {x}: {c}")
    print("-- topic options offered and taken, per person (day 3 from 09:45):")
    seen = {}
    for a in r["asks"]:
        if a["phase"] == "day" and not a["mind"] and a["minute"] is not None and a["minute"] >= END:
            offered = re.findall(r"^- ((?:talk|tell)_\w+):", a["prompt"], flags=re.M)
            if offered:
                s = seen.setdefault(a["who"], {"offered": [], "taken": 0})
                s["offered"].append((clock(a["minute"]), offered))
    for d in day3(r):
        if topic_of(d["option"] or "") and d["who"] in seen:
            seen[d["who"]]["taken"] += 1
    for who, s in seen.items():
        print(f"  {who}: offered at {len(s['offered'])} asks, taken {s['taken']}: {s['offered']}")
    told = [b for b in r["beliefs"]["daniel"] if r["door_end_id"] in b["about"]]
    if told:
        t0 = told[0]["minute"]
        print(f"-- Daniel's decisions after he was told ({clock(t0)}):")
        for d in r["decisions"]:
            if d["who"] == "daniel" and d["minute"] >= t0:
                print(f"  {d['clock']} [{d['mode']}] {d['option']}: say {d['say']!r}; feeling {d['feeling']!r}; "
                      f"reason {d['reason']!r}")
    else:
        print("-- Daniel was not told on day 3")
    print("-- Daniel's night:")
    for d in (r.get("night_transcript") or {}).get("decisions", []):
        if d.get("person") == "daniel":
            print(f"  {d.get('ask')}: {d.get('option')}; say {d.get('say')!r}; reason {d.get('reason')!r}")
    print(f"  night lines: {r['night_lines'].get('daniel')}")
    print("-- words naming the children (day 3 from 09:45 and the night):")
    for d in day3(r):
        if KIDS.search(d.get("say") or ""):
            print(f"  {d['clock']} {d['who']} {d['option']}: {d['say']!r}")
    for d in (r.get("night_transcript") or {}).get("decisions", []):
        if KIDS.search(d.get("say") or ""):
            print(f"  night {d.get('person')} {d.get('option')}: {d.get('say')!r}")
    print("-- the night minds' kept memories:")
    for pid, m in r["minds"].items():
        print(f"  {pid} ({m['mode']}): {[(x['ids'], x['meaning']) for x in m['kept']]}; intent {m['intent']!r}; "
              f"warnings {m['warnings']}")
    print("-- day 4's door and belief lines (A and B), and the water line:")
    for pid, b in r["day4_blocks"].items():
        for part in ("A", "B"):
            for ln in b[part]:
                if DOOR.search(ln):
                    print(f"  {pid} {part}: {ln}")
    print(f"  water (Daniel): {r['day4_water'].get('daniel')}")
    print("-- Q1 that probe_after refused and this run fired (matched by person, need and stage):")
    old = {(e["who"], e["need"], e["stage"]): e for e in (after[k] or {}).get("quiet_log", [])
           if e["kind"] == "Q1" and not e["fired"]}
    new = [e for e in r["quiet_log"] if e["kind"] == "Q1" and e["fired"]]
    for e in new:
        o = old.get((e["who"], e["need"], e["stage"]))
        if o:
            print(f"  {clock(e['minute'])} {e['who']} {e['need']} {e['stage']}: fired here; probe_after refused it at "
                  f"{clock(o['minute'])}: {o['why']!r}")
    print(f"  all Q1 fired here: {[(clock(e['minute']), e['who'], e['need'], e['stage']) for e in new]}")
    print(f"  day 3 asks {r['day_asks']}; Q5: {[(clock(e['minute']), e['fired'], e['why']) for e in r['quiet_log'] if e['kind'] == 'Q5']}")

print(f"\n==================== T1 over all tells: "
      f"{sum(len(t['warnings']) for r in recs.values() if r for t in r['tells'])} warnings in "
      f"{sum(len(r['tells']) for r in recs.values() if r)} tells: "
      f"{[(k, clock(t['minute']), t['teller'], t['warnings']) for k, r in recs.items() if r for t in r['tells']]}")
