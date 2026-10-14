"""Replays what the fourteenth version's code made, and checks it.

    python v14/check.py

v14/ is a frozen copy of the code at 90133b4 and c717b0f: v13 plus the neutral food moment line and
confront_<name> from the night on (reports/food_confront_impl.md). No run was ever made with it: it was
frozen before multi-day life (reports/days_design.md) was built on top. What it can still be held to is day 1,
which it replays from the v11 answers. Each replayed day-1 story must come out byte for byte as runs/v11/<name>.md,
and its transcript as the one saved beside it. Replaying makes no API calls.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from gemini import Cache, Oracle                         # noqa: E402  (v14's own modules)
from story import render                                 # noqa: E402
from world import Morning                                # noqa: E402

# (scenario, model name, seeds): day 1 of these, from cache/v11, against runs/v11.
RUNS = [("daniel_ate_it", "gemini-3.5-flash-lite", (1, 2, 3))]


def main():
    ok = True
    for scenario, model, seeds in RUNS:
        for seed in seeds:
            name = f"{scenario}-seed{seed}"
            cache = Cache(os.path.join(ROOT, "cache", "v11", f"{model}-{name}.json"))
            oracle = Oracle(cache, model, seed, client=None, replay=True)
            morning = Morning(oracle, seed, scenario)
            for t in range(morning.turns):
                morning.turn(t)
            morning.finish()
            text = render(morning, seed, model, f"python morning.py --seed {seed}")
            base = os.path.join(ROOT, "runs", "v11", name)
            with open(base + ".md", "rb") as f:
                same_story = f.read() == text.encode("utf-8")
            with open(base + ".transcript.json", encoding="utf-8") as f:
                same_transcript = json.load(f) == json.loads(json.dumps(morning.transcript))
            ok &= same_story and same_transcript
            print(f"{name}: day 1 replayed {oracle.from_cache} answers from cache/v11, 0 API calls; "
                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
