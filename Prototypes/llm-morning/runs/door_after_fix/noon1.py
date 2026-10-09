"""reports/door_memory_impl.md: probe_door2's scene 1 to 12:00 with the fake model after 09:42 (as runs/door_after/
trace.py noon 1, in this process, through test_morning.DoorAfterTest.noon_scene1); prints the stretches, the asks
from the knock and the quiet log. Writes nothing in the repository.

    python runs/door_after_fix/noon1.py        from Prototypes/llm-morning/
"""
import os
import sys
import unittest

os.environ.pop("GEMINI_API_KEY", None)
sys.path.insert(0, os.getcwd())
import test_morning as T                                # noqa: E402

t = T.DoorAfterTest("test_a_after_a_visit_its_stretch_asks_for_2_turns_at_most_and_the_10_00_q2_is_not_refused_for_the_budget")
t.setUp()
try:
    m, oracle = t.noon_scene1()
    q = m.quiet
    clock = T.data.clock
    sc = q.door_scenes[0]
    print(f"visit {clock(sc['start'])} to {clock(sc['end'])}, {sc['outcome']}; door asks {sc['door_asks']}")
    for s in q.stretches:
        if s["end"] is not None and s["end"] > 162:
            print(f"stretch {clock(s['start'])} to {clock(s['end'])} {s['trigger']} in {s['room']}: {s['asks']} asks")
    print("asked from the knock:")
    for r in m.log:
        if 162 <= r["minute"] < 300:
            who = [d["person"] for d in r["decisions"] if d["mode"] == "model"]
            if who:
                print(f"  {clock(r['minute'])}: {', '.join(who)}")
    print("quiet log from 09:45:")
    for e in q.log:
        if 165 <= e["minute"] < 300:
            print(f"  {clock(e['minute'])} {e['kind']} fired {e['fired']} why {e.get('why')}")
    print(f"day's asks at 12:00: {q.asks}")
finally:
    t.tearDown()
