"""reports/w2a_impl.md: the estimated tokens a door scene adds to a kitchen prompt (T5's count), shut with the voice
line and every option, and open; v16 seed 2, day 3, a visit for water at 07:30, Leo calls at 07:30. No API."""
import os, re, sys
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import unittest, test_morning as T
from world import estimate_tokens

class Count(T.KnockTest):
    def runTest(self):
        pol = lambda who, minute, opts: ("door_call" if "door_call" in opts and minute == 30 else
                                         "door_open" if "door_open" in opts and minute == 33 else None)
        d, q, (v,) = self.door_day(T.PolicyFake(pol), [(30, "ask_water")])
        m = d.day3
        for t in range(0, 13):
            q.turn(t)
            p = next((x for x in m.people.values() if x.room == "kitchen" and x.door and x.door["options"]), None)
            if p is None:
                continue
            with_door = m.prompt_for(p, t, m.options_for(p))
            lines = self.door_lines(with_door)
            house = next(x for x in with_door.split("\n") if x.startswith("The house:"))
            seen, p.door = p.door, None
            plain = m.prompt_for(p, t, m.options_for(p))
            p.door = seen
            plain_house = next(x for x in plain.split("\n") if x.startswith("The house:"))
            extra = estimate_tokens("\n".join(lines)) + (len(house) - len(plain_house)) / 3.6
            print(f"{T.data.clock(t * 3)} {p.name}: door {seen['door']}; {len(lines)} lines; {extra:.1f} est. tokens")
            for x in lines:
                print("    " + x)
Count().run()
