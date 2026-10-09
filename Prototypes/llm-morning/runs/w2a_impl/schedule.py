"""reports/w2a_impl.md, amendments 1 and 2: the first-visit schedule of seeds 1 to 10 (the visits to no. 9 on days 3 to
10 when no knock is answered, at most one a day), before calibration (factor 1.0) and for each factor up to the cap
of 2.0; the factor chosen as §2.7 says (median 4 knocks on days 3 to 10, no seed over 8) within the cap; and seed 2's
schedule with each visit's purpose. No API; nothing written but stdout.

    python runs/w2a_impl/schedule.py          (from Prototypes/llm-morning/)
"""
import os
import statistics
import sys

sys.path.insert(0, os.getcwd())
import street                               # noqa: E402
import weather                              # noqa: E402

SEEDS, DAYS = range(1, 11), 10
pop = street.load("population")
CAP = pop["approach"]["factor_cap"]


def show(factor):
    out = {}
    for seed in SEEDS:
        out[seed] = street.schedule(seed, DAYS, factor=factor)
        print(f"  seed {seed:2d}: {len(out[seed])} knock(s)  " + "; ".join(
            f"day {v['day']} {weather.hhmm(v['at'])} no. {v['home']} {v['purpose'].replace('_', ' ')}"
            + (f" (deferred {len(v['deferrals'])}x)" if v["deferrals"] else "") for v in out[seed]))
    n = [len(out[s]) for s in SEEDS]
    print(f"  counts {n}; median {statistics.median(n)}; max {max(n)}")
    return out, n


print(f"UNCALIBRATED (factor {pop['approach']['factor_uncalibrated']}: an ask plan goes to a door with chance "
      f"{pop['approach']['trips_a_part']} a part):")
show(pop["approach"]["factor_uncalibrated"])
print("\nTHE CALIBRATION, factors 0.25 to the cap (median and max of knocks on days 3-10 over seeds 1-10):")
best = None
for i in range(1, int(CAP / 0.25) + 1):
    f = i * 0.25
    n = [len(street.schedule(s, DAYS, factor=f)) for s in SEEDS]
    med = statistics.median(n)
    ok = med >= 4 and max(n) <= 8
    print(f"  factor {f:4.2f}: counts {n}; median {med}; max {max(n)}{'  meets §2.7' if ok else ''}")
    if ok and best is None:
        best = f
chosen = best if best is not None else CAP
print(f"\nCHOSEN: factor {chosen} ({'the smallest that meets §2.7' if best is not None else 'no factor up to the cap meets §2.7 (median 4, none over 8); the cap is the closest'}); "
      f"population.json has factor {pop['approach']['factor']}")
print(f"\nCALIBRATED (factor {chosen}):")
out, n = show(chosen)
print(f"\nSEED 2, days 3 to {DAYS}, factor {chosen}:")
for v in out[2]:
    hh = street.generate(2)["households"][v["household"]]
    who, _ = street.who_words(v["envoy"])
    print(f"  day {v['day']} {weather.hhmm(v['at'])}: no. {v['home']} ({len(hh['drawn']['members'])} people, "
          f"{hh['drawn']['disposition']}), {who}, purpose {v['purpose']} -> {'water' if v['purpose'] == 'ask_water' else 'food'}")
print(f"  {len(out[2])} visit(s): " + ("READY (3 or more)" if len(out[2]) >= 3 else "NOT READY FOR LIVE RUN (fewer than 3)"))

print("\nWHAT LIMITS THE KNOCKS: seed 2's street to the end of day 10, its plans and where each ask that went was aimed:")
import collections                          # noqa: E402
for f in (pop["approach"]["factor_uncalibrated"], chosen):
    st = street.generate(2)
    st["factor"] = f
    street.advance(st, street.midnight(DAYS + 1), weather.Weather(2).raining)
    plans = [x for x in st["log"] if x["what"] == "plan"]
    c = collections.Counter(x["plan"] for x in plans)
    gone = [x for x in plans if x.get("gone")]
    to = collections.Counter(x["target"] for x in gone)
    print(f"  factor {f}: plans {dict(sorted(c.items()))}; asks that went to a door {len(gone)}, to {len(to)} houses; "
          f"to no. 9: {to.get(9, 0)} (made before day 3 or at night: never)")
