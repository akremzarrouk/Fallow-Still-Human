"""The metrics table for the fifth step: every run, whatever its scenario or model.

    python metrics5.py          prints the table and the grudges behind it, in Markdown

Reads the eleven runs in runs/v5/ and, for comparison, the five v4 daniel_ate_it runs made
with Flash Lite (runs/v4/). The culprit is read from each transcript (v4 transcripts predate
that field; their scenario is daniel_ate_it, so Daniel).
"""
import json
import os
import re
import sys

from metrics import longest_run
from talk import act_of

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ORDER = ["daniel", "elena", "leo", "mara"]
RUNS = ([("v4", "daniel_ate_it", "Flash Lite", f"daniel_ate_it-seed{s}", s) for s in range(1, 6)]
        + [("v5", "daniel_ate_it", "Gemma 4 31B", f"daniel_ate_it-gemma-seed{s}", s) for s in range(1, 6)]
        + [("v5", sc, "Flash Lite", f"{sc}-seed{s}", s) for sc in ("mara_ate_it", "miscount") for s in range(1, 4)])
# An admission in someone's own words ("I took it", "I ate the can"...).
ADMISSION = re.compile(r"\bI (?:took|ate|stole|had)\b(?: (?:it|the can|the food|that can|the last can|one))?\b",
                       re.I)


def load(folder, name):
    with open(os.path.join(HERE, "runs", folder, f"{name}.transcript.json"), encoding="utf-8") as f:
        tr = json.load(f)
    tr.setdefault("culprit", "daniel")
    return tr


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


def accusations(tr):
    return [(a["minute"], a["who"], a["option"][7:], a["option"][7:] == tr["culprit"])
            for a in acts(tr) if a["option"].startswith("accuse_")]


def unanswered_repeats(tr):
    """How many times "who took the can?" was asked again although nothing had answered it since
    it was last asked: no confession and no accusation, anywhere in the house."""
    count, asked, answered = 0, False, False
    for a in acts(tr):
        kind = act_of(a["option"])[0]
        if kind == "ask":
            if asked and not answered:
                count += 1
            asked, answered = True, False
        elif kind in ("confess", "accuse"):
            answered = True
    return count


def false_admissions(tr):
    """Lines in which someone who did not take the can says they did."""
    return [(a["minute"], a["who"], a["words"]) for a in lines(tr)
            if a["who"] != tr["culprit"] and ADMISSION.search(a["words"])]


def grudges(tr):
    out = []
    for p in ORDER:
        for target, g in tr["final_state"][p]["grudges"].items():
            if g["strength"]:
                facts = [fact for _, fact, kind in g["events"] if kind == "event"]
                angry = [m for m, _, kind in g["events"] if kind == "angry"]
                if angry:
                    facts.append(f"named {NAMES[target]} in angry_at at minutes "
                                 + ", ".join(f"{m:02d}" for m in angry))
                out.append((p, target, g["strength"], facts))
    return out


def row(folder, scenario, model, name, seed):
    tr = load(folder, name)
    all_acts = acts(tr)
    said = lines(tr)
    culprit = tr["culprit"]
    conf = next((a["minute"] for a in all_acts if a["option"] == "confess"), None)
    n, who, kind, start, end = longest_run(tr)
    quiet, qstart = longest_quiet(tr)
    acc = accusations(tr)
    reassuring = [a for a in said if act_of(a["option"])[0] == "reassure"]
    fa = false_admissions(tr)
    return {
        "run": f"{scenario}, {model}, seed {seed}",
        "calls": sum(a["mode"] != "routine" for a in all_acts),
        "invalid": sum(a["mode"] == "fallback" for a in all_acts),
        "lines": len(said),
        "accusations": "; ".join(f"{NAMES[a]}→{NAMES[t]} min {m:02d} ({'true' if true else 'false'})"
                                 for m, a, t, true in acc) or "none",
        "confessed": ("no culprit" if culprit is None else
                      f"yes, min {conf:02d}" if conf is not None else "no"),
        "false": ("none (the option exists only for the culprit)" if not fa else
                  "; ".join(f"{NAMES[w]} min {m:02d}: “{t}”" for m, w, t in fa)),
        "run_len": f"{n} ({NAMES[who]}, {kind})" if who else "0",
        "unanswered": unanswered_repeats(tr),
        "reassure": f"{100 * len(reassuring) / len(said):.0f}% ({len(reassuring)}/{len(said)})" if said else "-",
        "quiet": f"{quiet} (min {qstart:02d}–{qstart + quiet:02d})" if quiet else "0",
        "grudges": grudges(tr),
    }


def main():
    rows = [row(*r) for r in RUNS]
    print("| Run (scenario, model, seed) | Model calls | Invalid answers (rules chose) | Lines spoken | "
          "Accusations (who → whom, true or false) | Culprit confessed | Anyone confessed falsely | "
          "Longest run of one speech act by one person (turns) | Question asked again unanswered | "
          "Lines that are reassurance | Longest stretch with no model decision (min) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['run']} | {r['calls']} | {r['invalid']} | {r['lines']} | {r['accusations']} | "
              f"{r['confessed']} | {r['false']} | {r['run_len']} | {r['unanswered']} | {r['reassure']} | "
              f"{r['quiet']} |")
    print()
    print("Grudges at minute 90, with their events (in the holder's own terms: \"you\" is the one "
          "holding the grudge):")
    for r in rows:
        print()
        print(f"{r['run']}:")
        if not r["grudges"]:
            print("- none")
        for p, target, strength, facts in r["grudges"]:
            print(f"- {NAMES[p]} against {NAMES[target]}, {strength}/3: " + "; ".join(facts) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
