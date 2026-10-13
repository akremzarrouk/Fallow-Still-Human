"""Q1 summary tables as Markdown, from runs/stuck_facts/q1_units.json and asks_all.json. Read-only."""
import collections, json

units = json.load(open("runs/stuck_facts/q1_units.json"))
recs = json.load(open("runs/stuck_facts/asks_all.json"))
PEOPLE = ("elena", "leo", "mara", "daniel")

print("### v22, days 3-10: per person per day: top option, its share of the day's asks, longest run of one option, pairs of answers >= 60%")
print()
print("| person | " + " | ".join(f"day {d}" for d in range(3, 11)) + " |")
print("|---|" + "---|" * 8)
for who in PEOPLE:
    cells = []
    for d in range(3, 11):
        u = next(x for x in units if x["dataset"] == "v22" and x["who"] == who and x["day"] == d)
        cells.append(f"{u['top']} {u['top_n']}/{u['n']} ({u['share']:.0%}); run {u['run']}; pairs {u['c60']}/{u['pairs']}")
    print(f"| {who} | " + " | ".join(cells) + " |")

print()
print("### v22, days 3-10, per person over the 8 days")
print()
print("| person | asks | days with top share >= 50% | highest day share | longest run | pairs >= 60% / all pairs | word-for-word equal pairs |")
print("|---|---|---|---|---|---|---|")
for who in PEOPLE:
    us = [x for x in units if x["dataset"] == "v22" and x["who"] == who]
    hi = max(us, key=lambda x: x["share"])
    lr = max(us, key=lambda x: x["run"])
    print(f"| {who} | {sum(x['n'] for x in us)} | {sum(1 for x in us if x['share'] >= .5)} of {len(us)} | "
          f"{hi['share']:.0%} (day {hi['day']}, {hi['top']} {hi['top_n']}/{hi['n']}) | {lr['run']} (day {lr['day']}, {lr['top']}) | "
          f"{sum(x['c60'] for x in us)} / {sum(x['pairs'] for x in us)} | {sum(x['eq'] for x in us)} |")
us = [x for x in units if x["dataset"] == "v22"]
print(f"| all | {sum(x['n'] for x in us)} | {sum(1 for x in us if x['share'] >= .5)} of {len(us)} | | {max(x['run'] for x in us)} | "
      f"{sum(x['c60'] for x in us)} / {sum(x['pairs'] for x in us)} | {sum(x['eq'] for x in us)} |")

print()
print("### talk_probe, day 3, live asks: per scene per person")
print()
print("| scene | person | asks | top option | share | longest run | pairs >= 60% / all | equal |")
print("|---|---|---|---|---|---|---|---|")
for u in units:
    if u["dataset"] == "talk_probe":
        print(f"| {u['scene']} | {u['who']} | {u['n']} | {u['top']} | {u['top_n']}/{u['n']} = {u['share']:.0%} | {u['run']} | {u['c60']} / {u['pairs']} | {u['eq']} |")

print()
print("### calm_probe + calm_variants, day 3, live asks (scenes 1 and 3 pooled; 10:00, 10:30, 11:00)")
print()
print("| person | version | live asks | options chosen | run in time order within a scene |")
print("|---|---|---|---|---|")
for who in ("elena", "leo", "mara"):
    for var in ("P", "T", "O", "TO"):
        us = [x for x in units if x["dataset"] in ("calm_probe", "calm_variants") and x["who"] == who and x["variant"] == var]
        c = collections.Counter()
        for x in us:
            c.update(x["options"])
        print(f"| {who} | {var} | {sum(x['n'] for x in us)} | {dict(c)} | {[x['run'] for x in us]} |")
print()
print("(P = calm_probe; T, O, TO = calm_variants. 'live asks' counts only rows asked live: Mara's O and TO rows in scene 3 reuse an earlier answer and are not counted.)")

print()
print("### v22: Daniel's still_going and volunteer asks (the 'I am going tonight' line)")
dn = [r for r in recs if r["dataset"] == "v22" and r["who"] == "daniel"]
c = collections.Counter(r["option"] for r in dn)
print(f"Daniel's {len(dn)} live day asks in days 3-10: " + ", ".join(f"{k} {v}" for k, v in c.most_common(8)))
print("still_going by day:", dict(collections.Counter(r["day"] for r in dn if r["option"] == "still_going")))
