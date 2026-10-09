"""reports/budget_fix_impl.md (c): the Q1 and Q2 that fire from 10:00 to 19:00 (day minutes 180 to 720, 19:00 left out)
in a trace's quiet log, before (runs/door_memory/) and after (runs/budget_fix/), and each day's asks."""
import json
import sys

for path in sys.argv[1:]:
    out = json.load(open(path, encoding="utf-8"))
    log = [e for e in out["quiet_log"] if e["kind"] in ("Q1", "Q2") and 180 <= e["minute"] < 720]
    fired = [e for e in log if e["fired"]]
    print(path)
    print(f"  Q1 and Q2 checked 10:00 to 19:00: {len(log)}; fired: {len(fired)} "
          f"(Q1 {sum(e['kind'] == 'Q1' for e in fired)}, Q2 {sum(e['kind'] == 'Q2' for e in fired)})")
    for e in log:
        print(f"    {e['minute'] // 60 + 7:02d}:{e['minute'] % 60:02d} {e['kind']} fired {e['fired']} why {e['why']}")
    print(f"  day 3's asks: {out['asks_count']['day']}")
    print("  stretches from the knock:", [(s["start"], s["end"], s["trigger"], s["asks"]) for s in out["stretches"]])
