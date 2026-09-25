"""Replays the three first-version mornings from their cache and writes their transcripts.

    python v1/transcript.py

v1/ is a frozen copy of the code that made the runs REPORT.md describes (everyone in a
turn decides at once, then the acts happen in a fixed order). Replaying makes no API
calls. Each replayed story must come out byte for byte as runs/daniel_ate_it-seed<N>.md,
which shows the copy is that code. The transcripts, runs/daniel_ate_it-seed<N>.transcript.json,
have the same shape as the ones the current version writes, for metrics.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import data                                  # noqa: E402  (v1's own modules)
from gemini import Cache, Oracle             # noqa: E402
from story import render                     # noqa: E402
from world import Morning                    # noqa: E402

MODEL = "gemini-3.5-flash-lite"
NAMES = {data.PEOPLE[p]["name"]: p for p in data.ORDER}


def transcript(morning, seed):
    turns = []
    for rec in morning.log:
        minute = rec["minute"]
        rooms = {r: [NAMES[n] for n, _ in people] for r, people in rec["rooms"].items()}
        where = {p: r for r, people in rooms.items() for p in people}
        acts = []
        # v1: everyone decided against the start of the turn, then the acts happened in
        # data.ORDER. So nobody heard a line of their own turn before deciding.
        for i, d in enumerate(rec["decisions"]):
            pid = d["person"]
            acts.append({
                "minute": minute, "who": pid, "room": where[pid], "option": d["option"],
                "words": d.get("say"), "audience": [q for q in rooms[where[pid]] if q != pid],
                "mode": d["mode"], "decided_at": [minute, -1], "said_at": [minute, i],
                "came_of_it": d["came_of_it"]})
        turns.append({"minute": minute, "rooms": rooms, "acts": acts})
    final = {r: [q for q in data.ORDER if morning.people[q].room == r] for r in data.ROOMS}
    return {"seed": seed, "version": 1, "turns": turns, "final_rooms": final}


def main():
    ok = True
    for seed in (1, 2, 3):
        cache = Cache(os.path.join(ROOT, "cache", f"{MODEL}-daniel_ate_it-seed{seed}.json"))
        oracle = Oracle(cache, MODEL, seed, client=None, replay=True)
        morning = Morning(oracle).run()
        text = render(morning, seed, MODEL, f"python morning.py --seed {seed}")
        with open(os.path.join(ROOT, "runs", f"daniel_ate_it-seed{seed}.md"), "rb") as f:
            same = f.read() == text.encode("utf-8")
        ok &= same
        path = os.path.join(ROOT, "runs", f"daniel_ate_it-seed{seed}.transcript.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(transcript(morning, seed), f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"seed {seed}: replayed {oracle.from_cache} answers from the cache, 0 API calls; "
              f"story {'IDENTICAL to' if same else 'DIFFERS from'} runs/daniel_ate_it-seed{seed}.md; "
              f"wrote {os.path.relpath(path, ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
