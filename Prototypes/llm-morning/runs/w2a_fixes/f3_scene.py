"""reports/w2a_fixes.md, fix 3: test F3's scene, turn by turn (v16 seed 2, day 3, a visit for water at 10:00; whoever is
offered the door walks away from it, then confronts someone). No API."""
import os, sys
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import test_morning as T, quiet

class Show(T.KnockFixTest):
    def runTest(self):
        def policy(who, minute, opts):
            if minute is None or minute < 180:
                return None
            if "door_call" in opts:
                return next((o for o in ("go_back_room", "go_brothers_room") if o in opts), None)
            return next((o for o in opts if o.startswith("confront_")), None)
        d, q, (v,) = self.door_day(T.PolicyFake(policy), [(180, "ask_water")])
        quiet.play(d.day3)
        for e in q.log:
            if e["kind"] == "Q7":
                print(f"{quiet.clock(e['minute'])} Q7: fired={e['fired']} room={e['room']} asked={e['asked']} why={e['why']} left={e.get('asks_left')}")
        for s in q.stretches:
            if 170 <= s["start"] <= 230:
                print(f"stretch {quiet.clock(s['start'])}-{quiet.clock(s['end'])} {s['trigger']} in {s['room']}: {s['asks']} asks")
        for turn in d.day3.transcript["turns"]:
            for a in turn["acts"]:
                if 180 <= a["minute"] <= 200 and a["mode"] != "routine":
                    print(f"  {quiet.clock(a['minute'])} {a['who']} in {a['room']}: {a['option']} [{a['mode']}]")
        sc = q.door_scenes[0]
        print(f"scene {quiet.clock(sc['start'])}-{quiet.clock(sc['end'])}: outcome {sc['outcome']}; Q7 asks {sc['q7_asks']}; knocks {[quiet.clock(k) for k in sc['knocks']]}; heard {sc['heard']}")
        print(f"day asks {q.asks}; reserved now {q.reserved}")
Show().run()
