"""Read-only. Totals for reports/v23.md beside v22's (stuck_facts.md section 1): per person, days with top share >= 50%,
share >= 80%, longest run, pairs sharing 60% of words, equal pairs; per day, trip-position acts and still_going.
    python runs/v23/scoring/summary.py"""
import collections, json, sys
sys.path.insert(0, "runs/v23/scoring")
import score
TRIP = ("volunteer", "volunteer_far", "propose_trip", "propose_far", "still_going", "keep_daniel_home", "nobody_goes",
        "send_daniel", "back_out")
for name, files in (("v22", ["runs/stuck_facts/asks_v22.json"]), ("v23", ["runs/v23/asks3.json"])):
    recs = score.records(files)
    rows = score.units(recs)
    print(f"== {name}: {len(recs)} day asks, {len(rows)} person-days")
    for w in score.PEOPLE:
        rs = {d: r for (d, ww), r in rows.items() if ww == w}
        print(f"  {w:6s} asks {sum(r['n'] for r in rs.values())}; days >=50% {sum(r['share'] >= .5 for r in rs.values())} of {len(rs)};"
              f" >=80% {sum(r['share'] >= .8 for r in rs.values())}; longest run {max(r['run'] for r in rs.values())};"
              f" >=60% pairs {sum(r['c60'] for r in rs.values())}/{sum(r['pairs'] for r in rs.values())}; equal {sum(r['eq'] for r in rs.values())}")
    print(f"  all: >=50% {sum(r['share'] >= .5 for r in rows.values())}; >=80% {sum(r['share'] >= .8 for r in rows.values())};"
          f" longest {max(r['run'] for r in rows.values())}; >=60% {sum(r['c60'] for r in rows.values())}/{sum(r['pairs'] for r in rows.values())};"
          f" equal {sum(r['eq'] for r in rows.values())}")
    byday = collections.Counter(r["day"] for r in recs if r["option"] in TRIP)
    sg = collections.Counter(r["day"] for r in recs if r["option"] == "still_going")
    acc = collections.Counter(r["who"] for r in recs if r["option"] in ("accuse_daniel", "confront_daniel"))
    n = collections.Counter(r["who"] for r in recs)
    print("  trip-position acts by day", dict(sorted(byday.items())), "total", sum(byday.values()))
    print("  still_going by day", dict(sorted(sg.items())), "total", sum(sg.values()))
    print("  accuse_daniel or confront_daniel / asks:", {w: f"{acc[w]}/{n[w]}" for w in score.PEOPLE})
    print("  asks by day", dict(sorted(collections.Counter(r["day"] for r in recs).items())))
    print("  options seen", len({r["option"] for r in recs}), "| silent", sum(r["option"] == "silent" for r in recs))
