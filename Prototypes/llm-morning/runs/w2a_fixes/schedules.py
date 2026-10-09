"""reports/w2a_fixes.md: the first-visit schedule of seeds 1 to 10, days 3 to 10, no knock answered, at the approach
factor of population.json (1.0), twice: the bin never out; the bin set out on day 6 at 07:00 and never brought in (and
the person who set it out in the yard then). For each seed, which houses overlook no. 9's yard, who lives there, and
what each believes of no. 9 (occupied, has_surplus) before and when it saw the yard. No API; nothing written but
stdout.

    python runs/w2a_fixes/schedules.py          (from Prototypes/llm-morning/)
"""
import os
import statistics
import sys

sys.path.insert(0, os.getcwd())
import street                               # noqa: E402
import weather                              # noqa: E402

SEEDS, DAYS = range(1, 11), 10
pop = street.load("population")
over = street.load("street")["overlook"]["9"]
BIN_AT = street.midnight(6) + 7 * 60                # day 6, 07:00


def bin_out():
    return {"bin_out_at": BIN_AT, "people": [BIN_AT]}


def line(v):
    return (f"day {v['day']} {weather.hhmm(v['at'])} no. {v['home']} {v['purpose'].replace('_', ' ')}"
            + (f" (deferred {len(v['deferrals'])}x)" if v["deferrals"] else ""))


print(f"approach factor {pop['approach']['factor']}; houses overlooking no. 9's yard: {over}; a bin seen sets "
      f"has_surplus {pop['yard']['has_surplus']} (prior {pop['priors']['surplus']}) and occupied {pop['yard']['occupied']}")
counts = {}
for name, yard in (("BIN NEVER OUT", None), ("BIN OUT FROM DAY 6, 07:00, NEVER BROUGHT IN", bin_out)):
    print(f"\n{name}:")
    counts[name] = []
    for seed in SEEDS:
        vs = street.schedule(seed, DAYS, yard=yard)
        counts[name].append(len(vs))
        print(f"  seed {seed:2d}: {len(vs)} knock(s)  " + "; ".join(line(v) for v in vs))
    n = counts[name]
    print(f"  counts {n}; median {statistics.median(n)}; max {max(n)}")

print("\nWHO OVERLOOKS NO. 9'S YARD, AND WHAT EACH BELIEVES WHEN (the bin out from day 6, 07:00; no knock answered):")
for seed in SEEDS:
    st = street.generate(seed)
    w = weather.Weather(seed)
    who = []
    for n in over:
        h = st["houses"][n]
        hh = st["households"].get(h["household"])
        who.append(f"no. {n} {h['status']}" + (f" ({len(hh['drawn']['members'])}, {hh['drawn']['disposition']})" if hh else ""))
    first = {}
    for k in range(1, DAYS + 1):
        for p in range(4):
            s = street.midnight(k) + p * street.PART
            street.advance(st, s, w.raining, bin_out)
            for x in st["log"]:
                if x["what"] == "saw_yard" and x["house"] not in first:
                    hh = st["households"][x["household"]]
                    first[x["house"]] = (x["at"], x["metres"], hh["occupied"][9], hh["surplus"][9])
    print(f"  seed {seed:2d}: " + "; ".join(who))
    for n in over:
        hh = st["households"].get(st["houses"][n]["household"])
        if hh is None:
            continue
        if n in first:
            at, m, occ, sur = first[n]
            print(f"     no. {n}: before day 6, occupied {1.0 if abs(st['houses'][n]['x'] - st['houses'][9]['x']) <= 40 else pop['priors']['occupied']}, "
                  f"has_surplus {pop['priors']['surplus']}; saw the bin by day {street.day_of(at)} {weather.hhmm(at)} "
                  f"({m} m): occupied {occ}, has_surplus {sur}; at the end of day {DAYS}: occupied {hh['occupied'][9]}, "
                  f"has_surplus {hh['surplus'][9]}, kind {round(hh['kind'][9], 2)}, refused {hh['refused'].get(9, 0)}")
print(f"\nSEED 2, bin out: {counts['BIN OUT FROM DAY 6, 07:00, NEVER BROUGHT IN'][1]} visit(s) on days 3 to {DAYS}: "
      + ("READY FOR LIVE RUN" if counts["BIN OUT FROM DAY 6, 07:00, NEVER BROUGHT IN"][1] >= 3 else "NOT READY FOR LIVE RUN"))
