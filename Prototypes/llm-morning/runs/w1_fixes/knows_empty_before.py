"""reports/w1_fixes.md: before fix 2, does a water haul from next door (no food) leave the house knowing next door is
empty of food? v16 seed 2 to night 3, Daniel next door, clean; day 4's knows_empty and far options. No API.

    python runs/w1_fixes/knows_empty_before.py      (from Prototypes/llm-morning/)
"""
import os
import sys

sys.path.insert(0, os.getcwd())
import test_morning as T              # noqa: E402
from world import Morning             # noqa: E402

t = T.PhysicalLayerTest("test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food")
t.setUp()
try:
    d, m, n3, _ = t.night3({"daniel": "go_next_door", "leo": "lie_awake"}, {**t.STILL, "trip:daniel": 0.1})
    g = n3.groups[0]
    print("night 3:", g["street"], "food", g["took"], "water", g["water"], "outcome", repr(g["outcome"]))
    d.chron.add_night(n3)
    day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
    print("day 4 knows_empty:", {q: p.knows_empty for q, p in day4.people.items()})
    print("day 4 volunteer_far offered:", {q: "volunteer_far" in [o.id for o in day4.options_for(p)]
                                           for q, p in day4.people.items()})
finally:
    t.tearDown()
