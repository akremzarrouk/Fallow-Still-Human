"""reports/calm_variants.md: read-only. P1 to P4 and the over-steer flag as reports/calm_variants_plan.md counts them,
and all 54 rows beside calm_probe's answer, from runs/calm_variants/scene<k>.json.

    python runs/calm_variants/read_variants.py        from Prototypes/llm-morning/
"""
import json
import os

FOLDER = os.path.join("runs", "calm_variants")
rows = []
for k in (1, 3):
    r = json.load(open(os.path.join(FOLDER, f"scene{k}.json"), encoding="utf-8"))
    print(f"scene {k}: seed {r['seed']}; replay {r['replay']}; variant asks {r['calm']}; stopped {r['stopped']}")
    print(f"  how each minute was reached: {r['how']}")
    for mo in r["moments"]:
        for a in mo["asks"]:
            rows.append((k, a))


def tell_ids(a):
    return [o for o in a["offered"] if o.startswith("tell_") and o.endswith("_visit")]


print(f"\nrows: {len(rows)}; live: {sum(a['how'] == 'live' for _, a in rows)}; "
      f"taken from an identical prompt: {sum(a['how'] != 'live' for _, a in rows)}")
told = {}
for v in ("T", "O", "TO"):
    offered = [(k, a) for k, a in rows if a["variant"] == v and tell_ids(a)]
    took = [(k, a) for k, a in offered if a["option"] in tell_ids(a)]
    told[v] = (len(took), len(offered))
    print(f"{v}: asks offering a tell_*_visit option: {len(offered)}; choosing one: {len(took)} "
          f"{[(k, a['clock'], a['who']) for k, a in took]}; over-steered (12 or more of 14): {len(took) >= 12}")
print(f"P1 (T, at least 3): {told['T'][0]} of {told['T'][1]} -> {'holds' if told['T'][0] >= 3 else 'fails'}")
print(f"P2 (O, at least 5): {told['O'][0]} of {told['O'][1]} -> {'holds' if told['O'][0] >= 5 else 'fails'}")
t = [(k, a) for k, a in rows if a["variant"] == "T"]
diff = [(k, a["clock"], a["who"], a["baseline"]["option"], a["option"]) for k, a in t
        if a["option"] != a["baseline"]["option"]]
print(f"P3 (T differs from calm_probe in at least 6 of 18): {len(diff)} of {len(t)} -> "
      f"{'holds' if len(diff) >= 6 else 'fails'}; {diff}")
bad = [(k, a["variant"], a["clock"], a["who"], a["option"]) for k, a in rows if not a["valid"]]
print(f"P4 (no answer chooses an option not offered): {bad} of {len(rows)} -> {'holds' if not bad else 'fails'}")
for v in ("O", "TO"):
    d = sum(a["option"] != a["baseline"]["option"] for k, a in rows if a["variant"] == v)
    print(f"  ({v}: differs from calm_probe in {d} of 18)")

print("\nchoices by variant (calm_probe first):")
for who in ("elena", "leo", "mara"):
    for v in ("base", "T", "O", "TO"):
        ch = [(a["baseline"]["option"] if v == "base" else a["option"]) for k, a in rows
              if a["who"] == who and a["variant"] == ("T" if v == "base" else v)]
        print(f"  {who:5} {v:4} {ch}")

print("\n==================== the T line checks, one per scene and minute")
done = set()
for k, a in rows:
    if a["t_checks"] and (k, a["clock"]) not in done:
        done.add((k, a["clock"]))
        print(f"  scene {k}, {a['clock']}: {a['t_line']}\n    {a['t_checks']}")

print("\n==================== every row")
for k, a in rows:
    print(f"\n-- {a['variant']}, scene {k}, {a['clock']}, {a['who']}, client seed {a['seed']}: {a['how']}")
    print(f"   T line: {a['t_line']}")
    print(f"   tell position: {a['tell_position']} of {a['n_options']}; topic options {a['topic_offered']}")
    print(f"   chose: {a['option']} ({a['labels'].get(a['option'])}); valid {a['valid']}")
    print(f"   say: {a['say']!r}")
    print(f"   feeling: {a['feeling']!r}; reason: {a['reason']!r}; suspects {a['suspects']}; angry_at {a['angry_at']}")
    b = a["baseline"]
    print(f"   calm_probe: {b['option']}; say {b['say']!r}; feeling {b['feeling']!r}; reason {b['reason']!r}")
    lines = a["prompt"].splitlines()
    now = lines.index(next(x for x in lines if x.startswith("Now, ")))
    opt = lines.index("Your options:")
    print(f"   prompt lines {now - 2} to {now + 1}: {lines[now - 2:now + 2]}")
    print(f"   first options: {lines[opt + 1:opt + 4]}")
