"""reports/door_after_facts.md, Q5: the kitchen's seeded turn-order draw (world.py:468-472, used at world.py:1394-1396)
on day 3 of v16 seed 2 (house day 6), through world.Morning.order_string itself. Read-only.

    python runs/door_after/order_draws.py        from Prototypes/llm-morning/
"""
import os
import random
import sys
from collections import Counter
from types import SimpleNamespace

sys.path.insert(0, os.getcwd())
import data                                             # noqa: E402
import quiet                                            # noqa: E402
import world                                            # noqa: E402

day3 = SimpleNamespace(seed=2, day=6)                   # day index 3 (world.day_index(6) == 3)
print(f"day_index(6) = {world.day_index(6)}")
three = ("elena", "leo", "mara")
first = Counter()
orders = Counter()
for t in range(0, quiet.DAY_END // data.MINUTES_PER_TURN):
    s = world.Morning.order_string(day3, t, "kitchen")
    rng = random.Random(s)
    draw = {q: rng.random() for q in data.ORDER}
    order = tuple(sorted(three, key=lambda x: draw[x]))
    first[order[0]] += 1
    orders[order] += 1
    if 54 <= t <= 58:
        print(f"t {t} ({quiet.clock(t * 3)}) '{s}': draws {', '.join(f'{q} {draw[q]:.4f}' for q in data.ORDER)}; "
              f"the kitchen's three by draw: {', '.join(order)}")
n = sum(first.values())
print(f"all {n} turns of day 3 (t = 0 to {n - 1}): lowest draw of the three: "
      + ", ".join(f"{q} {first[q]}" for q in three))
print("the six orders of the three: " + "; ".join(f"{' > '.join(o)} {c}" for o, c in orders.most_common()))
