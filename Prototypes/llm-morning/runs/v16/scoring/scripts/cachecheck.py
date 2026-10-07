"""Read only: each cache/v16 file keeps every cache/v15 entry unchanged; how many entries are new, by kind."""
import json
R = "What you did, saw and heard today and tonight, in order (each with its id):"
for s in (1, 2, 3):
    a = json.load(open(f"cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    b = json.load(open(f"cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    new = [b[k]["prompt"] for k in b if k not in a]
    mind = sum(R in p for p in new)
    night = sum("\nNow it is night" in p and R not in p for p in new)
    print(f"seed {s}: v15 entries {len(a)}, v16 entries {len(b)}, all v15 kept unchanged "
          f"{all(k in b and b[k] == v for k, v in a.items())}; new {len(new)}: night {night}, night mind {mind}, "
          f"day {len(new) - mind - night}")
