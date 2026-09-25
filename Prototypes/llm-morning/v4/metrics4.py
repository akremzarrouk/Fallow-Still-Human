"""The metrics table for the third version's runs and the fourth's, computed the same way.

    python metrics4.py          prints the table and the grudges behind it, in Markdown

Reads runs/v3/daniel_ate_it-seed<N>.transcript.json (seeds 1 to 3) and
runs/v4/daniel_ate_it-seed<N>.transcript.json (seeds 1 to 5).
"""
import json
import os
import sys

from talk import act_of

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ORDER = ["daniel", "elena", "leo", "mara"]
SEEDS = {3: (1, 2, 3), 4: (1, 2, 3, 4, 5)}


def load(version, seed):
    with open(os.path.join(HERE, "runs", f"v{version}", f"daniel_ate_it-seed{seed}.transcript.json"),
              encoding="utf-8") as f:
        return json.load(f)


def acts(tr):
    return [a for turn in tr["turns"] for a in sorted(turn["acts"], key=lambda a: a["said_at"])]


def lines(tr):
    return [a for a in acts(tr) if a["words"]]


def longest_quiet(tr):
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


def confession(tr):
    return next((a for a in acts(tr) if a["option"] == "confess"), None)


def wronged(tr):
    """Everyone Daniel lied to (heard him deny it) or accused, with how: in order of first time."""
    out = {}
    for a in acts(tr):
        if a["who"] != "daniel":
            continue
        if a["option"] == "deny":
            for q in a["audience"]:
                out.setdefault(q, set()).add("lied to")
        elif a["option"].startswith("accuse_"):
            out.setdefault(a["option"][7:], set()).add("accused")
    return out


def first_reassurance(tr, who, conf):
    """Minutes from the confession to who's first reassurance of Daniel himself, or None."""
    for a in acts(tr):
        if a["who"] == who and a["option"] == "reassure_daniel" and a["said_at"] > conf["said_at"]:
            return a["minute"] - conf["minute"]
    return None


def grudges_at_90(tr, version):
    """person -> [(target, strength, facts)] for every grudge still held at minute 90."""
    out = {}
    for p in ORDER:
        st = tr["final_state"][p]
        held = []
        if version == 3:
            target, strength = st["grudge"]
            if strength:
                named = [a["minute"] for a in acts(tr)
                         if a["who"] == p and a.get("angry_at") == NAMES[target]]
                held.append((target, strength, [f"named {NAMES[target]} as who they were angry with at "
                                                 f"minutes {', '.join(f'{m:02d}' for m in named)}"]))
        else:
            for target, g in st["grudges"].items():
                if g["strength"]:
                    facts = [fact for _, fact, kind in g["events"] if kind == "event"]
                    angry = [m for m, _, kind in g["events"] if kind == "angry"]
                    if angry:
                        facts.append(f"named {NAMES[target]} as who they were angry with at "
                                     f"minutes {', '.join(f'{m:02d}' for m in angry)}")
                    held.append((target, g["strength"], facts))
        out[p] = held
    return out


def row(version, seed):
    tr = load(version, seed)
    conf = confession(tr)
    said = lines(tr)
    reassuring = [a for a in said if act_of(a["option"])[0] == "reassure"]
    quiet, start = longest_quiet(tr)
    if conf is None:
        after = "no confession"
    else:
        parts = []
        for who, how in sorted(wronged(tr).items(), key=lambda kv: ORDER.index(kv[0])):
            gap = first_reassurance(tr, who, conf)
            parts.append(f"{NAMES[who]} ({' and '.join(sorted(how))}): "
                         + (f"{gap} min" if gap is not None else "never"))
        after = "; ".join(parts) or "he lied to and accused nobody"
    return {
        "name": f"v{version}, seed {seed}", "calls": sum(a["mode"] != "routine" for a in acts(tr)),
        "lines": len(said), "confessed": f"min {conf['minute']:02d}" if conf else "never",
        "after": after,
        "reassure": f"{len(reassuring)}/{len(said)} ({100 * len(reassuring) / len(said):.0f}%)" if said else "0/0",
        "quiet": f"{quiet} (min {start:02d}–{start + quiet:02d})" if quiet else "0",
        "grudges": grudges_at_90(tr, version),
    }


def main():
    rows = [row(v, s) for v in (3, 4) for s in SEEDS[v]]
    print("| Run | Model calls | Lines spoken | Daniel confessed | From his confession to the first "
          "reassurance of him, for each person he lied to or accused | Lines that are reassurance | "
          "Longest stretch with no model decision (minutes) |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['name']} | {r['calls']} | {r['lines']} | {r['confessed']} | {r['after']} | "
              f"{r['reassure']} | {r['quiet']} |")
    print()
    print("Grudges at minute 90, with the events behind them (in the holder's own terms: \"you\" "
          "is the one holding the grudge):")
    for r in rows:
        print()
        print(f"{r['name']}:")
        held = [(p, g) for p in ORDER for g in r["grudges"][p]]
        if not held:
            print("- nobody holds a grudge")
        for p, (target, strength, facts) in held:
            print(f"- {NAMES[p]} against {NAMES[target]}, {strength}/3: " + "; ".join(facts) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
