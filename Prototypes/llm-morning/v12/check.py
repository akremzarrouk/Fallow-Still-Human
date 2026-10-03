"""Replays the three twelfth-version runs from their cache and checks their stories.

    python v12/check.py

v12/ is a frozen copy of the code that made the runs reports/night_v12.md describes
(daniel_ate_it: day 1 from the v11 answers, then the night and day 2 of reports/night_design.md).
Replaying makes no API calls. Each replayed story must come out byte for byte as runs/v12/<name>.md,
and its transcript (day 1, the night and day 2) as the one saved beside it.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from gemini import Cache, Oracle                         # noqa: E402  (v12's own modules)
from night import Night                                  # noqa: E402
from story import render, render_day2, render_night      # noqa: E402
from world import Morning                                # noqa: E402

# (scenario, model key, model name, seeds), as the runs in runs/v12 were made.
RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3))]


def main():
    ok = True
    for scenario, key, model, seeds in RUNS:
        for seed in seeds:
            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
            cache = Cache(os.path.join(ROOT, "cache", "v12", f"{model}-{name}.json"))
            oracle = Oracle(cache, model, seed, client=None, replay=True)
            command = ("python morning.py"
                       + (f" --scenario {scenario}" if scenario != "daniel_ate_it" else "")
                       + (f" --model {key}" if key else "") + f" --seed {seed}")
            # As morning.run does it: day 1, its story, then the night and day 2.
            morning = Morning(oracle, seed, scenario)
            for t in range(morning.turns):
                morning.turn(t)
            morning.finish()
            day1_text = render(morning, seed, model, command)
            oracle.new_scene()
            night = Night(morning, oracle).run()
            oracle.new_scene()
            day2 = Morning.next_day(morning, night, oracle)
            for t in range(day2.turns):
                day2.turn(t)
            day2.finish()
            text = day1_text + render_night(night) + render_day2(day2)
            transcript = {"day1": morning.transcript, "night": night.transcript(), "day2": day2.transcript}
            base = os.path.join(ROOT, "runs", "v12", name)
            with open(base + ".md", "rb") as f:
                same_story = f.read() == text.encode("utf-8")
            with open(base + ".transcript.json", encoding="utf-8") as f:
                same_transcript = json.load(f) == json.loads(json.dumps(transcript))
            ok &= same_story and same_transcript
            print(f"{name}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
