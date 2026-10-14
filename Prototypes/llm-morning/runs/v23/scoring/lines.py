"""Read-only. Every spoken line, door event, tell, need event and rain onset of days 3 to 10, and each night's
bedtimes, reasons and trips, in order, from a run's transcript: the text the report's day readings are made from.

    python runs/v23/scoring/lines.py <transcript.json> > runs/v23/scoring/lines.txt
"""
import json
import sys


def hhmm(minute):
    return f"{7 + minute // 60:02d}:{minute % 60:02d}"


t = json.load(open(sys.argv[1], encoding="utf-8"))
ev = t["chronicle"]["events"]
for d in range(3, 11):
    if f"day{d}" not in t:
        continue
    day = t[f"day{d}"]
    q = day["quiet"]
    print(f"\n======== DAY {d} (away: {day.get('away')}) ========")
    for r in q.get("rain", []):
        print(f"  [rain] {json.dumps(r, ensure_ascii=False)[:200]}")
    for e in q.get("need_events", []):
        print(f"  [need] {hhmm(e['minute'])} {e['who']} {e['need']} stage {e['stage']}")
    for sc in q["door"]:
        print(f"  [door] {hhmm(sc['start'])}-{hhmm(sc['end'])} {sc['purpose']} {sc['who']} -> {sc['outcome']}; "
              f"rooms {sc.get('rooms')}; by_knock {sc.get('by_knock')}; said {sc.get('said')}; "
              f"heard_said {sc.get('heard_said')}; acts {sc['acts']}; give {sc.get('give')}")
    for s in q.get("stretches", []):
        print(f"  [stretch] {hhmm(s['start'])}-{hhmm(s['end'])} {s['room']} {s['trigger']} asks {s['asks']}")
    for e in ev:
        if e["scene"] == f"D{d}" and e["kind"] in ("tell", "knock", "door_line", "door_end", "ration_water",
                                                    "save_water", "collect_rain"):
            print(f"  [event] {e['id']} {hhmm(e['minute'])} {e['kind']} {e['actor']} -> {e.get('members')}: "
                  f"{e['text'][:300]}; witnesses {e['witnesses']}")
    for turn in day["turns"]:
        for a in turn["acts"]:
            if a["mode"] == "routine":
                continue
            m = a["minute"]
            clock = f"min {m:02d}" if m < q["morning_end"] else hhmm(m)
            print(f"  {clock} {a['who']:6s} [{a['mode'][0]}] {a['option']:<22s} {a['room'] or '':<12s} "
                  f"{a['words'] or ''}")
    if f"night{d}" in t:
        n = t[f"night{d}"]
        print(f"\n  ---- NIGHT {d}: leavers {n['leavers']}, away {n['away']} ----")
        for x in n["decisions"]:
            print(f"  [{x['ask']}] {x['person']:6s} {x['option']:<14s} say {x.get('say')!r} reason {x.get('reason')!r}")
        for g in n["groups"]:
            print(f"  [group] {json.dumps({k: g.get(k) for k in ('leader', 'members', 'street', 'outcome', 'far')}, ensure_ascii=False)}")
        for e in ev:
            if e["scene"] == f"N{d}" and e["kind"] in ("went_out", "street", "got_up", "at_door", "door", "return",
                                                        "back", "reaction"):
                print(f"  [n-event] {e['kind']} {e['actor']}: {e['text'][:200]}")
