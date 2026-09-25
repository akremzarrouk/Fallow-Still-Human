"""Replays the three second-version mornings from their cache and checks their stories.

    python v2/check.py

v2/ is a frozen copy of the code that made the runs REPORT-2.md describes (people in a
room act one after another; a conversation ends after one quiet turn). Replaying makes
no API calls. Each replayed story must come out byte for byte as
runs/v2/daniel_ate_it-seed<N>.md, and its transcript as the one saved beside it.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from gemini import Cache, Oracle             # noqa: E402  (v2's own modules)
from story import render                     # noqa: E402
from world import Morning                    # noqa: E402

MODEL = "gemini-3.5-flash-lite"


def main():
    ok = True
    for seed in (1, 2, 3):
        cache = Cache(os.path.join(ROOT, "cache", "v2", f"{MODEL}-daniel_ate_it-seed{seed}.json"))
        oracle = Oracle(cache, MODEL, seed, client=None, replay=True)
        morning = Morning(oracle, seed)
        for t in range(morning.turns):
            morning.turn(t)
        morning.transcript["final_rooms"] = {r: [q for q in morning.people if morning.people[q].room == r]
                                             for r in morning.convos.rooms}
        text = render(morning, seed, MODEL, f"python morning.py --seed {seed}")
        base = os.path.join(ROOT, "runs", "v2", f"daniel_ate_it-seed{seed}")
        with open(base + ".md", "rb") as f:
            same_story = f.read() == text.encode("utf-8")
        with open(base + ".transcript.json", encoding="utf-8") as f:
            same_transcript = json.load(f) == json.loads(json.dumps(morning.transcript))
        ok &= same_story and same_transcript
        print(f"seed {seed}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
              f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
              f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
