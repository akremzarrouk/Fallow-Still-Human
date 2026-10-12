"""The six CHECKABLE-NOW target-morning Never checks, on a run's transcript.

The spec is design/never-checker-design.md (commit 6d6abc1), §1 and §3: N2, N3, N4, N6, N8, N11. Each
check reads only the transcript's fields, never the rendered story, and returns its verdict with the acts
that triggered it. N9 and N12 need fields the transcript does not have yet; N1, N5, N7, N10 and N13 are
judgment and are not here.

    python never_check.py runs/v18/daniel_ate_it-seed1.transcript.json [more transcripts...]
"""
import json
import sys

import data
import talk

FOUND_NOTHING = "went through the room and found nothing."
# Options that name a person (design §3, N8), when followed by a cast id.
AIMED = ("reassure_", "accuse_", "sit_", "back_", "object_", "aside_")


def morning_of(transcript):
    """The discovery morning: the day1 object, or the top level of a single-morning transcript."""
    return transcript.get("day1", transcript)


def load(path):
    with open(path, encoding="utf-8") as f:
        return morning_of(json.load(f))


def acts(morning):
    """Every act of the morning, in the order they were said."""
    return sorted((a for t in morning["turns"] for a in t["acts"]), key=lambda a: tuple(a["said_at"]))


def hit(a):
    return a["minute"], a["who"], a["option"]


def finished_search(a):
    return a["option"] in ("search", "keep_searching") and a["came_of_it"] == FOUND_NOTHING


def n2(morning):
    """Someone other than the culprit chooses `search` in a room within 3 turns (9 minutes) after another
    person's act there whose came_of_it is "found nothing", with them in that act's audience."""
    out, seen = [], []
    for a in acts(morning):
        if a["option"] == "search" and a["who"] != morning["culprit"]:
            if any(f["who"] != a["who"] and f["room"] == a["room"] and a["who"] in f["audience"]
                   and a["minute"] - f["minute"] <= 9 for f in seen):
                out.append(hit(a))
        if finished_search(a):
            seen.append(a)
    return out


def n3(morning):
    """`search` in a room the person already searched to the end; `deny` after their own `confess`; `ask_who`
    after being in the audience of a `confess`."""
    out, searched, confessed, heard = [], set(), set(), set()
    for a in acts(morning):
        who, option = a["who"], a["option"]
        if ((option == "search" and (who, a["room"]) in searched) or (option == "deny" and who in confessed)
                or (option == "ask_who" and who in heard)):
            out.append(hit(a))
        if finished_search(a):
            searched.add((who, a["room"]))
        if option == "confess":
            confessed.add(who)
            heard.update(a["audience"])
    return out


def n4(morning):
    """A `sit_<q>` act while q is searching (latest act `search`, or `keep_searching` not ending in "found
    nothing") or leaving (an act with `moved_to` earlier in the same turn)."""
    out, latest, left_at = [], {}, {}
    for a in acts(morning):
        if a["option"].startswith("sit_"):
            q = a["option"][len("sit_"):]
            last = latest.get(q)
            searching = last is not None and (last["option"] == "search" or (
                last["option"] == "keep_searching" and last["came_of_it"] != FOUND_NOTHING))
            if searching or left_at.get(q) == a["minute"]:
                out.append(hit(a))
        latest[a["who"]] = a
        if a["moved_to"]:
            left_at[a["who"]] = a["minute"]
    return out


def n6(morning):
    """No act at minute 0 has words. Its triggering acts are minute 0's acts, all wordless."""
    zero = [a for a in acts(morning) if a["minute"] == 0]
    return [] if any(a["words"] for a in zero) else [hit(a) for a in zero]


def n8(morning):
    """An act whose option names a person, or whose `suspects` names someone, with a mode other than model."""
    def names_someone(a):
        aimed = any(a["option"].startswith(p) and a["option"][len(p):] in data.ORDER for p in AIMED)
        return aimed or a["suspects"] not in (None, "nobody")
    return [hit(a) for a in acts(morning) if a["mode"] != "model" and names_someone(a)]


def n11(morning):
    """One person's 3 or more consecutive model-decided acts of the same speech kind (talk.act_of), all with
    `new` false. Only `mode` model acts make up the sequence; any other model act breaks a run."""
    out, runs = [], {}
    def close(who):
        run = runs.pop(who, [])
        if len(run) >= 3 and all(a["new"] is False for a in run):
            out.extend(run)
    for a in acts(morning):
        if a["mode"] != "model":
            continue
        kind = talk.act_of(a["option"])[0]
        run = runs.get(a["who"], [])
        if kind in talk.SPEECH and run and talk.act_of(run[0]["option"])[0] == kind:
            run.append(a)
        else:
            close(a["who"])
            if kind in talk.SPEECH:
                runs[a["who"]] = [a]
    for who in list(runs):
        close(who)
    return [hit(a) for a in sorted(out, key=lambda a: tuple(a["said_at"]))]


def n9(morning):
    """At least 5 turns in a row in which (a) every act is `silent` (a silent lull included) or keeps sitting with
    the same person, and (b) `showing` is empty. Its hits are the stretches, as (first minute, last minute, turns).
    None if the transcript does not record `showing`."""
    if not all("showing" in t for t in morning["turns"]):
        return None
    out, run, last = [], [], {}
    def close():
        if len(run) >= 5:
            out.append((run[0], run[-1], len(run)))
    for t in morning["turns"]:
        quiet = True
        for a in sorted(t["acts"], key=lambda a: tuple(a["said_at"])):
            seated = a["option"].startswith("sit_") and last.get(a["who"]) == a["option"]
            quiet &= a["option"] == "silent" or seated
            last[a["who"]] = a["option"]
        if quiet and not t["showing"]:
            run.append(t["minute"])
        else:
            close()
            run = []
    close()
    return out


CHECKS = {"N2": n2, "N3": n3, "N4": n4, "N6": n6, "N8": n8, "N9": n9, "N11": n11}


def check(morning):
    """item -> ("pass" or "fail", triggering acts as (minute, who, option); for N9, stretches as (first minute,
    last minute, turns)). N9 is ("n/a", []) on a transcript without turns[].showing."""
    out = {}
    for item, f in CHECKS.items():
        hits = f(morning)
        out[item] = ("n/a", []) if hits is None else ("fail" if hits else "pass", hits)
    return out


def main(paths):
    for path in paths:
        print(path)
        for item, (verdict, hits) in check(load(path)).items():
            shown = (f"{a:02d}-{b:02d} ({n} turns)" for a, b, n in hits) if item == "N9" else (
                f"{m:02d} {who} {option}" for m, who, option in hits)
            print(f"  {item:<4} {verdict}" + ("" if not hits else ": " + "; ".join(shown)))


if __name__ == "__main__":
    main(sys.argv[1:])
