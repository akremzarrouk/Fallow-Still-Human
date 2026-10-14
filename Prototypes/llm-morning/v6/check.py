"""Replays the six sixth-version mornings from their cache and checks their stories.

    python v6/check.py

v6/ is a frozen copy of the code that made the runs reports/baseline_v6.md and
reports/witness_v6.md describe (daniel_ate_it, and daniel_ate_it_leo_heard). Replaying makes
no API calls. Each replayed story must come out byte for byte as
runs/v6/<name>.md, and its transcript as the one saved beside it.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from gemini import Cache, Oracle             # noqa: E402  (v6's own modules)
from story import render                     # noqa: E402
from world import Morning                    # noqa: E402

# (scenario, model key, model name, seeds), as the runs in runs/v6 were made.
RUNS = [("daniel_ate_it", None, "gemini-3.5-flash-lite", (1, 2, 3)),
        ("daniel_ate_it_leo_heard", None, "gemini-3.5-flash-lite", (1, 2, 3))]


def main():
    ok = True
    for scenario, key, model, seeds in RUNS:
        for seed in seeds:
            name = f"{scenario}-{key}-seed{seed}" if key else f"{scenario}-seed{seed}"
            cache = Cache(os.path.join(ROOT, "cache", "v6", f"{model}-{name}.json"))
            oracle = Oracle(cache, model, seed, client=None, replay=True)
            morning = Morning(oracle, seed, scenario)
            for t in range(morning.turns):
                morning.turn(t)
            morning.finish()
            command = ("python morning.py"
                       + (f" --scenario {scenario}" if scenario != "daniel_ate_it" else "")
                       + (f" --model {key}" if key else "") + f" --seed {seed}")
            text = render(morning, seed, model, command)
            base = os.path.join(ROOT, "runs", "v6", name)
            with open(base + ".md", "rb") as f:
                same_story = f.read() == text.encode("utf-8")
            with open(base + ".transcript.json", encoding="utf-8") as f:
                same_transcript = json.load(f) == json.loads(json.dumps(morning.transcript))
            ok &= same_story and same_transcript
            print(f"{name}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
