"""The metrics table for the second version's runs and the third's, computed the same way.

    python metrics3.py          prints the tables and the details behind them, in Markdown

Reads runs/v2/daniel_ate_it-seed<N>.transcript.json (second version) and
runs/v3/daniel_ate_it-seed<N>.transcript.json (third). Inner moments, private talks,
suspicion, grudges and guilt did not exist in the second version: those columns say so.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ORDER = ["daniel", "elena", "leo", "mara"]
ROOM_NAMES = {"kitchen": "kitchen", "brothers_room": "brothers room", "back_room": "back room",
              "bathroom": "bathroom"}


def load(version, seed):
    with open(os.path.join(HERE, "runs", f"v{version}", f"daniel_ate_it-seed{seed}.transcript.json"),
              encoding="utf-8") as f:
        return json.load(f)


def acts(tr):
    return [a for turn in tr["turns"] for a in sorted(turn["acts"], key=lambda a: a["said_at"])]


def longest_quiet(tr):
    """Longest stretch of turns in which the model decided nothing for anyone in the house."""
    best, run, start = (0, None), 0, None
    for turn in tr["turns"]:
        if any(a["mode"] != "routine" for a in turn["acts"]):
            run = 0
            continue
        if run == 0:
            start = turn["minute"]
        run += 1
        if run * 3 > best[0]:
            best = (run * 3, start)
    return best


def inner(tr):
    moments = [a for a in acts(tr) if a.get("inner")]
    causes = {}
    for a in moments:
        for c in a["inner"]:
            causes[c] = causes.get(c, 0) + 1
    return moments, causes


def restarts_by_inner(tr):
    return [e for e in tr.get("convo_log", []) if e["what"] == "started" and e.get("by_inner")]


def asides(tr):
    replies = [a for a in acts(tr) if a["option"] in ("accept_aside", "refuse_aside")]
    return sum(a["option"] == "accept_aside" for a in replies), sum(a["option"] == "refuse_aside" for a in replies)


def confession(tr):
    return next((a["minute"] for a in acts(tr) if a["option"] == "confess"), None)


def food(tr):
    out = []
    for a in acts(tr):
        if a["came_of_it"].startswith("ate a portion"):
            out.append(f"{NAMES[a['who']]} ate (min {a['minute']:02d})")
        elif a["came_of_it"].startswith("shared out"):
            out.append(f"{NAMES[a['who']]} shared (min {a['minute']:02d})")
    return "; ".join(out) or "no"


def track(state):
    target, strength = state
    return f"{NAMES[target]} {strength}/3" if strength else "none"


def row(version, seed):
    tr = load(version, seed)
    quiet, start = longest_quiet(tr)
    moments, causes = inner(tr)
    went, refused = asides(tr)
    conf = confession(tr)
    tracked = "final_state" in tr
    return {
        "name": f"v{version}, seed {seed}",
        "calls": sum(a["mode"] != "routine" for a in acts(tr)),
        "lines": sum(1 for a in acts(tr) if a["words"]),
        "quiet": f"{quiet} (min {start:02d}–{start + quiet:02d})" if quiet else "0",
        "inner": (f"{len(moments)}" + (" (" + ", ".join(f"{k} {v}" for k, v in sorted(causes.items(),
                                                                                 key=lambda kv: -kv[1])) + ")"
                                        if causes else "")) if tracked else "0 (none in v2)",
        "restarts": str(len(restarts_by_inner(tr))) if tracked else "0 (none in v2)",
        "asides": f"{went} / {refused}" if tracked else "0 / 0 (none in v2)",
        "confessed": f"yes, min {conf:02d}" if conf is not None else "no",
        "food": food(tr),
        "state": tr.get("final_state"),
    }


def main():
    rows = [row(v, s) for v in (2, 3) for s in (1, 2, 3)]
    print("| Run | Model calls | Lines spoken | Longest stretch with no model decision (minutes) | "
          "Inner moments (what rose) | Conversations restarted by an inner moment | "
          "Private talks (accepted / refused) | Daniel confessed | Food eaten or shared |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['name']} | {r['calls']} | {r['lines']} | {r['quiet']} | {r['inner']} | "
              f"{r['restarts']} | {r['asides']} | {r['confessed']} | {r['food']} |")
    print()
    print("Suspicion and grudge at minute 90, and Daniel's guilt (the rules kept none of these in v2):")
    print()
    print("| Run | " + " | ".join(f"{NAMES[p]}: suspects / grudge" for p in ORDER) + " | Daniel's guilt |")
    print("|---|" + "---|" * (len(ORDER) + 1))
    for r in rows:
        st = r["state"]
        if st is None:
            print(f"| {r['name']} | " + " | ".join("not tracked" for _ in ORDER) + " | not tracked |")
            continue
        print(f"| {r['name']} | " + " | ".join(f"{track(st[p]['suspicion'])} / {track(st[p]['grudge'])}"
                                               for p in ORDER) + f" | {st['daniel']['guilt']}/3 |")
    print()
    print("Inner moments, one by one:")
    for s in (1, 2, 3):
        for a in inner(load(3, s))[0]:
            print(f"- v3, seed {s}, min {a['minute']:02d}, {NAMES[a['who']]}: {', '.join(a['inner'])} "
                  f"-> {a['option']}")
    print()
    print("Conversations started by an inner moment:")
    for s in (1, 2, 3):
        for e in restarts_by_inner(load(3, s)):
            print(f"- v3, seed {s}, min {e['minute']:02d}, {ROOM_NAMES[e['room']]}: {e['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
