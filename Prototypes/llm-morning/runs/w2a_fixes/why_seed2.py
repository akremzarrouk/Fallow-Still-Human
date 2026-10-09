"""reports/w2a_fixes.md, §3: why the bin seen does not bring seed 2 a knock. Seed 2's street to the end of day 10 with
the bin out from day 6, 07:00 (no knock answered): for each household that overlooks no. 9's yard, its stores and needs
at the end, and its plan and scores in each part from day 5 on. No API."""
import os, sys
sys.path.insert(0, os.getcwd())
import street, weather
st = street.generate(2)
w = weather.Weather(2)
y = lambda: {"bin_out_at": street.midnight(6) + 420, "people": [street.midnight(6) + 420]}
street.advance(st, street.midnight(11), w.raining, y)
for n in street.load("street")["overlook"]["9"]:
    hid = st["houses"][n]["household"]
    if hid is None:
        print(f"no. {n}: {st['houses'][n]['status']}")
        continue
    hh = st["households"][hid]
    print(f"no. {n} ({len(hh['drawn']['members'])} people, {hh['drawn']['disposition']}): at the end of day 10 water "
          f"{hh['water']:.1f} L, food {hh['food']:.1f} days; need_w, need_f, u = "
          f"{[round(x, 2) for x in street.needs(hh, st['pop'])]}; belief of no. 9: occupied {hh['occupied'][9]}, "
          f"has_surplus {hh['surplus'][9]}")
    for x in st["log"]:
        if x["what"] == "plan" and x["household"] == hid and x["at"] >= street.midnight(5):
            print(f"   day {street.day_of(x['at'])} {weather.hhmm(x['at'])}: {x['plan']}"
                  + (f" -> no. {x['target']}" if x["target"] else "") + f"  {x['scores']}")
