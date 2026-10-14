"""v23's scorer (reports/v23_plan.md, section 3). Read-only; no API.

    python runs/v23/scoring/score.py --control
        P1 and P3 on v22 (runs/stuck_facts/asks_v22.json, the replay stuck_facts.md section 1 counted): must give
        20 of 32 and 23.
    python runs/v23/scoring/score.py <transcript.json> <asks.json>
        P1 to P4 and the per-day table of a v23 run (or its fake). For a resumed run, the final session's record:
        it replays every earlier answer from the cache, so it holds every ask of days 3 to 10 in order.

P1/P3 follow runs/stuck_facts/q1_repetition.py: unit = one person's asks in the day scene of day k >= 3, in the order
asked; top = the commonest option id; equal = same `say` lower-cased and trimmed, `silent` (no words) not paired.
"""
import collections
import itertools
import json
import re
import sys

PEOPLE = ["elena", "leo", "mara", "daniel"]


def words(say):
    return set(re.findall(r"[a-z0-9']+", (say or "").lower()))


def pairs(rows):
    out = []
    ws = [(r, words(r["say"])) for r in rows if r["say"]]
    for (a, wa), (b, wb) in itertools.combinations(ws, 2):
        if not wa or not wb:
            continue
        inter = len(wa & wb)
        out.append(dict(a=a, b=b, eq=(a["say"].strip().lower() == b["say"].strip().lower()),
                        cmax=inter / max(len(wa), len(wb))))
    return out


def longest_run(rows):
    best, cur, prev = 0, 0, None
    for r in rows:
        cur = cur + 1 if r["option"] == prev else 1
        prev = r["option"]
        best = max(best, cur)
    return best


def records(ask_files):
    recs = []
    for path in ask_files:
        for a in json.load(open(path, encoding="utf-8")):
            m = re.match(r"day(\d+)$", a["scene"])
            if not m or int(m.group(1)) < 3:
                continue
            try:
                ans = json.loads(a["answer"]) if isinstance(a["answer"], str) else a["answer"]
            except ValueError:
                ans = {"option": "<not json>"}
            if not isinstance(ans, dict):
                ans = {"option": "<not json>"}
            clk = re.search(r"\nNow, (.*?), you are", a["prompt"])
            recs.append(dict(day=int(m.group(1)), who=re.match(r"You are (\w+),", a["prompt"]).group(1).lower(),
                             clock=clk.group(1) if clk else None, option=ans.get("option"), say=ans.get("say"),
                             live=a.get("live", True), file=path))
    return recs


def units(recs):
    u = collections.OrderedDict()
    for r in recs:
        u.setdefault((r["day"], r["who"]), []).append(r)
    rows = {}
    for key, rs in u.items():
        c = collections.Counter(r["option"] for r in rs)
        top, tn = c.most_common(1)[0]
        ps = pairs(rs)
        rows[key] = dict(n=len(rs), top=top, top_n=tn, share=tn / len(rs), run=longest_run(rs),
                         eq=sum(p["eq"] for p in ps), c60=sum(p["cmax"] >= .6 for p in ps), pairs=len(ps),
                         eq_list=[(p["a"]["clock"], p["b"]["clock"], p["a"]["say"]) for p in ps if p["eq"]],
                         options=dict(c), still_going=c.get("still_going", 0))
    return rows


def p1_p3(rows):
    p1 = sum(r["share"] >= 0.5 for r in rows.values())
    p3 = sum(r["eq"] for r in rows.values())
    return p1, len(rows), p3


def check_transcript(t, recs):
    """Per day and person, the transcript's model acts equal the recorded asks, in order."""
    bad = 0
    for d in range(3, 11):
        if f"day{d}" not in t:
            continue
        tr = collections.defaultdict(list)
        for turn in t[f"day{d}"]["turns"]:
            for a in turn["acts"]:
                if a["mode"] in ("model", "fallback"):
                    tr[a["who"]].append((a["mode"], a["option"]))
        mine = collections.defaultdict(list)
        for r in recs:
            if r["day"] == d:
                mine[r["who"]].append(r["option"])
        # same number of asks per person; where the transcript took the model's answer, the same option
        ok = all(len(tr[w]) == len(mine[w]) and all(o == m for (md, o), m in zip(tr[w], mine[w]) if md == "model")
                 for w in set(tr) | set(mine))
        bad += not ok
        fb = sum(md == "fallback" for v in tr.values() for md, _ in v)
        print(f"check day {d}: transcript model acts {sum(map(len, tr.values())) - fb} + fallback {fb}, recorded asks "
              f"{sum(map(len, mine.values()))}, same order per person: {ok}")
    print("check days that differ:", bad)
    return bad


def hhmm(minute):
    return f"{7 + minute // 60:02d}:{minute % 60:02d}"


def score(t, recs):
    c = t["chronicle"]
    ev = c["events"]
    rows = units(recs)
    p1, n_pd, p3 = p1_p3(rows)
    out = {"P1": (p1, n_pd), "P3": p3}

    # P2: knock and door_line events of day scenes 3..10 with at least one witness
    street_ev = [e for e in ev if re.match(r"D(\d+)$", e["scene"]) and int(e["scene"][1:]) >= 3
                 and e["kind"] in ("knock", "door_line") and e["witnesses"]]
    visits = []
    for d in range(3, 11):
        if f"day{d}" in t:
            for sc in t[f"day{d}"]["quiet"]["door"]:
                visits.append((d, sc))
    out["P2"] = (len(street_ev), len(visits))

    # P4
    missed, missed_away = [], []
    for d, sc in visits:
        vev = [e for e in ev if e["scene"] == f"D{d}" and sc["start"] <= e["minute"] <= sc["end"]
               and (e["kind"] in ("knock", "door_line", "door_end") or e["kind"].startswith("door_"))]
        knew = set().union(*[set(e["witnesses"]) for e in vev]) if vev else set()
        away = set(t[f"day{d}"].get("away") or [])
        away_next = set(t[f"day{d + 1}"].get("away") or []) if f"day{d + 1}" in t else set(PEOPLE)
        for pid in PEOPLE:
            if pid in knew:
                continue
            if pid in away and pid in away_next:     # away at the visit and still away the next day: cannot be told
                missed_away.append((d, sc["visit"], pid))
                continue
            told = [b for b in c["beliefs"].get(pid, []) if b.get("topic") == f"visit:{sc['visit']}"
                    and b.get("k") in (d, d + 1)]
            missed.append(dict(day=d, visit=sc["visit"], who=pid, away=pid in away,
                               told=[(b["k"], b["minute"], b["source"]) for b in told],
                               later=[(b["k"], b["minute"], b["source"]) for b in c["beliefs"].get(pid, [])
                                      if b.get("topic") == f"visit:{sc['visit']}" and b.get("k") not in (d, d + 1)]))
    out["P4"] = missed
    out["P4_away"] = missed_away
    out["visits"] = visits
    out["street_ev"] = street_ev
    out["rows"] = rows
    return out


def verdicts(out):
    p1, n_pd = out["P1"]
    v = {"P1": ("PASS" if p1 < 20 else "FAIL", f"{p1} of {n_pd} person-days with top share >= 50%"),
         "P2": ("PASS" if out["P2"][0] >= 2 else "FAIL",
                f"{out['P2'][0]} street events reached someone ({out['P2'][1]} visits)"),
         "P3": ("PASS" if out["P3"] < 23 else "FAIL", f"{out['P3']} word-for-word equal pairs")}
    m = out["P4"]
    if not m:
        v["P4"] = ("NOT TESTED", ("no one missed a visit" if out["visits"] else "no visit")
                   + (f"; away through the next day, not counted: {out['P4_away']}" if out["P4_away"] else ""))
    else:
        untold = [x for x in m if not x["told"]]
        v["P4"] = ("FAIL" if untold else "PASS",
                   f"{len(m)} missed, {len(m) - len(untold)} told by the end of the next day; " +
                   "; ".join(f"day {x['day']} {x['visit']} {x['who']}{' (away)' if x['away'] else ''}: told "
                             f"{x['told'] or 'NO'}{' later ' + str(x['later']) if x['later'] else ''}" for x in m)
                   + (f"; away through the next day, not counted: {out['P4_away']}" if out["P4_away"] else ""))
    return v


def day_table(t, out):
    c = t["chronicle"]
    ev = c["events"]
    lines = []
    for d in range(3, 11):
        if f"day{d}" not in t:
            continue
        q = t[f"day{d}"]["quiet"]
        rain = [hhmm(r["minute"]) if isinstance(r, dict) and "minute" in r else str(r) for r in q.get("rain", [])]
        doors = [f"{hhmm(sc['start'])} {sc['purpose']} -> {sc['outcome']}; heard by "
                 f"{sorted(set().union(*[set(h) for _, h in sc.get('by_knock', [])]) if sc.get('by_knock') else set())}; "
                 f"words heard by {sorted(sc.get('heard_said', {}))}; acts {[a[1] + ' ' + a[2] for a in sc['acts']]}"
                 for sc in q["door"]]
        tells = [f"{hhmm(e['minute'])} {e['actor']} -> {','.join(e['members'])} ({e['option']})"
                 for e in ev if e["scene"] == f"D{d}" and e["kind"] == "tell"]
        trips = [f"{e['actor']} {e['kind']}{' (' + str(e.get('outcome')) + ')' if e.get('outcome') else ''}"
                 for e in ev if e["scene"] == f"N{d}" and e["kind"] in ("went_out", "street", "got_up", "at_door")]
        tops = {w: out["rows"].get((d, w)) for w in PEOPLE}
        lines.append(dict(day=d, rain=rain, doors=doors, tells=tells, trips_night_after=trips,
                          tops={w: (f"{r['top']} {r['top_n']}/{r['n']} ({r['share']:.0%})" if r else "-")
                                for w, r in tops.items()},
                          eq={w: (r["eq"] if r else 0) for w, r in tops.items()},
                          still_going=(tops["daniel"] or {}).get("still_going", 0),
                          asks=sum(r["n"] for r in tops.values() if r)))
    return lines


def main():
    if sys.argv[1:] == ["--control"]:
        recs = records(["runs/stuck_facts/asks_v22.json"])
        t = json.load(open("runs/v22/daniel_ate_it-seed2.transcript.json", encoding="utf-8"))
        bad = check_transcript(t, recs)
        p1, n, p3 = p1_p3(units(recs))
        print(f"v22 control: P1 {p1} of {n} (stuck_facts: 20 of 32) | P3 {p3} (stuck_facts: 23) | "
              f"{'MATCH' if (p1, n, p3) == (20, 32, 23) and not bad else 'DIFFERS'}")
        return
    t = json.load(open(sys.argv[1], encoding="utf-8"))
    recs = records(sys.argv[2:3])     # the final session's record: every ask, earlier sessions' from the cache
    check_transcript(t, recs)
    out = score(t, recs)
    for k, (verdict, why) in verdicts(out).items():
        print(f"{k} {verdict} ({why})")
    print()
    print("street events:")
    for e in out["street_ev"]:
        print(f"  {e['id']} {hhmm(e['minute'])} {e['kind']} witnesses {e['witnesses']}: {e['text']}")
    print()
    print("units (day, person): top n/asks share | run | equal | >=60% / pairs | still_going")
    for (d, w), r in out["rows"].items():
        print(f"  day {d} {w:6s} {r['top']:<22s} {r['top_n']}/{r['n']} ({r['share']:.0%}) | run {r['run']} | eq {r['eq']} "
              f"| {r['c60']}/{r['pairs']} | {r['still_going']}")
        for a, b, s in r["eq_list"]:
            print(f"      equal {a} / {b}: {s}")
    print()
    print("per day:")
    for row in day_table(t, out):
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
