"""DONE 4 of reports/facts_and_evening.md: v16 seed N through night 2 and its night mind, from a temp copy of
cache/v16, with no API call, on the code in CODE_DIR. Writes the story through night 2 and every scene's transcript to
OUT_DIR, to be compared byte for byte between HEAD's code and the new code.

    python runs/facts_evening/prefix.py CODE_DIR OUT_DIR SEED...      (from Prototypes/llm-morning/)
"""
import json
import os
import shutil
import sys
import tempfile

code_dir, out_dir, seeds = sys.argv[1], sys.argv[2], [int(s) for s in sys.argv[3:]]
here = os.getcwd()
sys.path.insert(0, os.path.abspath(code_dir))
assert not os.environ.get("GEMINI_API_KEY")
from chronicle import Chronicle                         # noqa: E402
from gemini import Cache, Oracle                        # noqa: E402
from mind import NightMind                              # noqa: E402
from night import Night                                 # noqa: E402
from story import render, render_day2, render_mind, render_night     # noqa: E402
from world import Morning                               # noqa: E402

MODEL = "gemini-3.5-flash-lite"
os.makedirs(out_dir, exist_ok=True)
for seed in seeds:
    name = f"daniel_ate_it-seed{seed}"
    tmp = tempfile.mkdtemp()
    copy = os.path.join(tmp, f"{MODEL}-{name}.json")
    shutil.copy(os.path.join(here, "cache", "v16", f"{MODEL}-{name}.json"), copy)
    oracle = Oracle(Cache(copy), MODEL, seed, client=None, replay=True)
    chron = Chronicle(seed, "daniel")

    def play(m):
        for t in range(m.turns):
            m.turn(t)
        m.finish()
        chron.add_day(m)
        return m
    day1 = play(Morning(oracle, seed))
    text = render(day1, seed, MODEL, f"python morning.py --seed {seed}")
    n1 = Night(day1, oracle, number=1).run()
    chron.add_night(n1)
    mind1 = NightMind(n1, chron, oracle).run()
    day2 = play(Morning.next_day(day1, n1, oracle, chronicle=chron))
    n2 = Night(day2, oracle, number=2, house=chron.house_state()).run()
    chron.add_night(n2)
    mind2 = NightMind(n2, chron, oracle).run()
    text += render_night(n1) + render_mind(mind1) + render_day2(day2) + render_night(n2) + render_mind(mind2)
    with open(os.path.join(out_dir, f"{name}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    tr = {"day1": day1.transcript, "night": n1.transcript(), "mind1": mind1.transcript(), "day2": day2.transcript,
          "night2": n2.transcript(), "mind2": mind2.transcript()}
    with open(os.path.join(out_dir, f"{name}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(tr, f, ensure_ascii=False, indent=1, sort_keys=True, default=str)
    shutil.rmtree(tmp)
    print(f"{name}: through night 2 and mind 2: {oracle.from_cache} answers from the cache, {oracle.live} live")
