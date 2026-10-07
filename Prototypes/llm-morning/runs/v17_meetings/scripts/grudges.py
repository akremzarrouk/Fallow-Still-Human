"""Each day-3 grudge in v17: its level at 07:00, at the start of each triggered stretch (each meeting), and at 21:00;
and every change during the day, with the played minute and what made it (from runs/v17_meetings/replay, made by
replay_v17.py, and runs/v17's transcripts). Read only.

    python runs/v17_meetings/scripts/grudges.py
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import data                                           # noqa: E402

N = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
for s in (1, 2, 3):
    r = json.load(open(f"runs/v17_meetings/replay/seed{s}.json", encoding="utf-8"))
    t = json.load(open(f"runs/v17/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    q = t["day3"]["quiet"]
    meetings = [st for st in q["stretches"][1:]]
    snaps = [(-1, r["start"])] + [(x["minute"], x["grudges"]) for x in r["turns"]]

    def at(minute):
        """The levels as a meeting starts: after every played turn before that minute."""
        return [g for m, g in snaps if m < minute][-1]
    pairs = sorted({(a, b) for _, g in snaps for a in g for b in g[a] if g[a][b]}
                   | {(a, b) for a in r["end"] for b in r["end"][a] if r["end"][a][b]},
                   key=lambda x: (data.ORDER.index(x[0]), data.ORDER.index(x[1])))
    head = ["holder → target", "07:00"] + [f"{data.clock(m['start'])} {m['trigger']}" for m in meetings] + ["21:00"]
    print(f"## seed {s}")
    print("| " + " | ".join(head) + " |")
    print("|" + "---|" * len(head))
    for a, b in pairs:
        row = [r["start"][a].get(b, 0)] + [at(m["start"])[a].get(b, 0) for m in meetings] + [r["end"][a].get(b, 0)]
        print(f"| {N[a]} → {N[b]} | " + " | ".join(str(x) for x in row) + " |")
    # Every change during the day: between consecutive snapshots.
    print("changes:")
    for (m0, g0), (m1, g1) in zip(snaps, snaps[1:]):
        for a in data.ORDER:
            for b in set(g0[a]) | set(g1[a]):
                x, y = g0[a].get(b, 0), g1[a].get(b, 0)
                if x != y:
                    rises = [e for e in r["day3_grudge_events"][a].get(b, []) if e[0] == m1]
                    why = "; ".join(f"{e[2]}: {e[1]}" for e in rises) or "fell (an answer of theirs not naming them)"
                    print(f"  {data.clock(m1)}: {N[a]} → {N[b]} {x} → {y} ({why})")
    rises_kept = [(e[0], a, b, e[1]) for a in data.ORDER for b, ev in r["day3_grudge_events"][a].items()
                  for e in ev if 0 <= e[0] < 840 and len(e) == 3 and e[2] == "angry"]
    q2 = [e for e in q["log"] if e["kind"] == "Q2"]
    print("Q2 entries (grudges as quiet.py read them): "
          + "; ".join(f"{data.clock(e['minute'])} {N[e['arrived']]}→{N[e['there']]} {e['grudges']} "
                      f"{'fired' if e['fired'] else 'not: ' + e['why']}" for e in q2))
