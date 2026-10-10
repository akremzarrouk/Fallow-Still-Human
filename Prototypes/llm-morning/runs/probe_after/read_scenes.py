"""reports/probe_after.md: reads runs/probe_after/scene<k>.json (read-only) and prints, for each scene, what the plan's
predictions read and what the report quotes. The regexes only find candidates: each hit is read by hand in the report.

    python runs/probe_after/read_scenes.py        from Prototypes/llm-morning/
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import quiet                                            # noqa: E402

OUT = os.path.join("runs", "probe_after")
clock = quiet.clock
DOOR = re.compile(r"water|door|woman|knock|stranger|visitor|\bgave\b|\bgive|giving|litre|bottle|neighbo|\bher\b|"
                  r"\bshe\b|child|kid|\bboy\b|\bgirl\b|mother|\bbeg", re.I)
VISITOR_OR_CHILDREN = re.compile(r"woman|visitor|stranger|door|mother|\bshe\b|\bher\b|neighbo|someone|child|kid|"
                                 r"\bboy\b|\bgirl\b|\bfive\b|little ones|son\b|daughter", re.I)
AFTER = 165                                             # 09:45


def answer(text):
    try:
        a = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip()))
    except ValueError:
        return {"raw": text}
    return a if isinstance(a, dict) else {"raw": text}


def full(d):
    return (f"{d['clock']} {d['who']} ({d['room']}, {d['mode']}{', ' + d['quiet'] if d.get('quiet') else ''}): "
            f"`{d['option']}`" + (f" *\"{d['say']}\"*" if d.get("say") else "") +
            f"; feeling {d.get('feeling')}; reason \"{d.get('reason')}\"" +
            (f"; invalid {d['invalid']}" if d.get("invalid") else ""))


def main():
    recs = {}
    for k in (1, 3, 4):
        path = os.path.join(OUT, f"scene{k}.json")
        if os.path.exists(path):
            recs[k] = json.load(open(path, encoding="utf-8"))
    verdict = {"P1": [], "P2": [], "P3": [], "P4": []}
    for k, r in recs.items():
        print(f"\n==================== scene {k} ({r['spec']['note']}, client seed {r['client_seed']})")
        print(f"reached {r['reached']}; stopped {r['stopped']}; counts {r.get('counts')}; day asks {r.get('day_asks')}")
        sc = r.get("scene")
        if sc:
            print(f"visit {clock(sc['start'])} to {clock(sc['end']) if sc['end'] is not None else None}; outcome "
                  f"{sc['outcome']}; said {[(clock(a), b) for a, b in sc['said']]}")
            print(f"summary: {json.dumps(sc['summary'], ensure_ascii=False)}")
        print("stretches:")
        for s in r.get("stretches", []):
            print(f"  {clock(s['start'])} to {s['end'] if s['end'] is None else clock(s['end'])} {s['trigger']} in "
                  f"{s['room']}: {s.get('asks')} asks")
        q7 = next((s for s in r.get("stretches", []) if s["trigger"] == "Q7"), None)
        q7_end = q7["end"] if q7 else None
        print(f"\n--- every decision from 09:45 to the Q7 stretch's end ({clock(q7_end) if q7_end else None})")
        window = [d for d in r.get("decisions", []) if AFTER <= d["minute"] <= (q7_end or -1)]
        for d in window:
            print("  " + full(d))
            print(f"      triggers: {d.get('triggers')}; order {d.get('order')}")
        # P1
        if k in (1, 3):
            el = [d for d in window if d["who"] == "elena" and d["mode"] == "model"]
            aimed = [d for d in el if d["option"].endswith("_mara")]
            words = [d for d in el if d.get("say") and DOOR.search(d["say"])]
            print(f"\nP1 scene {k}: Elena asked in the window {len(el)}; options {[d['option'] for d in el]}; aimed at "
                  f"Mara {[(d['clock'], d['option']) for d in aimed]}; words with a door/water/woman hit "
                  f"{[(d['clock'], d['say']) for d in words]}")
            verdict["P1"].append((k, bool(aimed), [(d["clock"], d["say"]) for d in words]))
        # later acts mentioning the door, the water given or the visitor
        print(f"\n--- day 3 after the Q7 stretch: decisions whose words or reason hit the door regex")
        for d in r.get("decisions", []):
            if d["minute"] > (q7_end or 10 ** 6) and d["mode"] == "model":
                text = f"{d.get('say') or ''} || {d.get('reason') or ''}"
                if DOOR.search(text):
                    print("  " + full(d))
        print("--- night 3 asks whose answer's words or reason hit the door regex")
        for a in r.get("asks", []):
            if a["phase"] == "night":
                x = answer(a["answer"])
                text = f"{x.get('say') or ''} || {x.get('reason') or ''}"
                if DOOR.search(text):
                    print(f"  night, {a['who']}: option {x.get('option')}; say \"{x.get('say')}\"; feeling "
                          f"{x.get('feeling')}; reason \"{x.get('reason')}\"")
        print("--- every night 3 ask (who, option, words)")
        for a in r.get("asks", []):
            if a["phase"] == "night":
                x = answer(a["answer"])
                print(f"  {a['who']} [{a['source']}]: {x.get('option')} \"{x.get('say')}\" ({x.get('feeling')}; "
                      f"{x.get('reason')})")
        # the night minds
        door_ids = {e["kind"]: e["id"] for e in r.get("day3_events", []) if e["kind"] in
                    ("door_refuse", "door_give", "door_end", "door_look", "door_line", "knock", "save_water")}
        all_door = {e["id"]: e["kind"] for e in r.get("day3_events", [])}
        print(f"\n--- day 3 door events: {all_door}")
        print("--- night 3 minds: every memory proposed (verdict), kept, feeling, intent")
        for pid, m in (r.get("minds") or {}).items():
            print(f"  {pid}: mode {m['mode']}; feeling {m['feeling']}; intent {m['intent']!r}")
            for mm in m["memories"]:
                tags = [all_door[i] for i in (mm["ids"] or []) if i in all_door]
                print(f"    {mm['verdict']}: {mm['ids']} {tags} \"{mm['meaning']}\"")
        el_mind = (r.get("minds") or {}).get("elena")
        if k in (1, 3):
            three = {door_ids.get(x) for x in ("door_refuse", "door_give", "door_end")} - {None}
            cites = [mm for mm in (el_mind or {}).get("kept", []) if three & set(mm["ids"])]
            print(f"\nP2 scene {k}: door event ids {sorted(three)}; Elena's kept memories citing one: "
                  f"{[(mm['ids'], mm['meaning']) for mm in cites]}")
            verdict["P2"].append((k, el_mind is not None, bool(cites)))
        # P3
        fired = [(clock(e["minute"]), e["kind"], e.get("asked")) for e in r.get("quiet_log", [])
                 if e["kind"] in ("Q1", "Q2") and e["fired"] and 180 <= e["minute"] <= 720]
        checked = [(clock(e["minute"]), e["kind"], e["fired"], e.get("why")) for e in r.get("quiet_log", [])
                   if e["kind"] in ("Q1", "Q2")]
        print(f"\nP3 scene {k}: Q1/Q2 checked {checked}\n   fired 10:00 to 19:00: {fired}")
        verdict["P3"].append((k, r["reached"] != "day 3", bool(fired)))
        # P4
        if k == 4:
            hits = []
            for d in r.get("decisions", []):
                if d["who"] == "mara" and d["minute"] >= AFTER and d.get("say") and VISITOR_OR_CHILDREN.search(d["say"]):
                    hits.append(("day", d["clock"], d["say"]))
            for a in r.get("asks", []):
                if a["phase"] == "night" and a["who"] == "mara":
                    x = answer(a["answer"])
                    if x.get("say") and VISITOR_OR_CHILDREN.search(x["say"]):
                        hits.append(("night", None, x["say"]))
            for mm in ((r.get("minds") or {}).get("mara") or {}).get("kept", []):
                if VISITOR_OR_CHILDREN.search(mm["meaning"]):
                    hits.append(("mind", mm["ids"], mm["meaning"]))
            said = [(d["clock"], d["option"], d.get("say")) for d in r.get("decisions", [])
                    if d["who"] == "mara" and d["minute"] >= AFTER and d["mode"] == "model"]
            print(f"\nP4 scene 4: Mara's asks after 09:45: {said}")
            print(f"   candidate hits: {hits}")
            verdict["P4"].append((k, hits))
        # day 4's blocks
        print("\n--- day 4's blocks A and B (all lines; door lines marked >>)")
        for pid, b in (r.get("day4_blocks") or {}).items():
            print(f"  {pid}:")
            for part in ("A", "B"):
                for ln in b[part]:
                    mark = ">>" if re.search(r"knocked at the front door|stored water|person at the front door|"
                                             r"woman|visitor", ln, re.I) else "  "
                    print(f"    {mark} {part} | {ln}")
        print("--- block C on house day 8, door lines")
        for pid, lines in (r.get("block_c_day8") or {}).items():
            print(f"  {pid}: {[ln for ln in lines if re.search('front door', ln)]}")
        print("--- state: grudges, feeling (before the knock, visit end, end of day)")
        for when, st in (r.get("states") or {}).items():
            print(f"  {when} ({clock(st['minute'])}): " + "; ".join(
                f"{pid} {({t: x['strength'] for t, x in st[pid]['grudges'].items() if x['strength']})} "
                f"{st[pid]['feeling']}" for pid in ("daniel", "elena", "leo", "mara")) + f"; street {st['street']}")
        print("--- grudge facts added after the knock")
        st0, st1 = r["states"].get("before_knock"), r["states"].get("end_of_day")
        if st0 and st1:
            for pid in ("daniel", "elena", "leo", "mara"):
                for t, x in st1[pid]["grudges"].items():
                    before = len(st0[pid]["grudges"].get(t, {}).get("events", []))
                    for ev in x["events"][before:]:
                        print(f"  {pid} against {t}: {ev}")
    print("\n==================== the predictions' inputs")
    for p, v in verdict.items():
        print(p, v)


if __name__ == "__main__":
    main()
