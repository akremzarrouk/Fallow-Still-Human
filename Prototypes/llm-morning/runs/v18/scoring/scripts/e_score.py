"""Scores reports/days_v18_plan.md's E1 to E5 on one version's day 3, read only, no API.

    python runs/v18/scoring/scripts/e_score.py v17      the baselines (run before any v18 live call)
    python runs/v18/scoring/scripts/e_score.py v18      the run
    python runs/v18/scoring/scripts/e_score.py v18 lines   every spoken line after the morning, per seed

Run from Prototypes/llm-morning/. "After the morning" is from day3.quiet.morning_end on. The answers of E3 are the
entries of cache/<v>/ that are not in cache/<v - 1>/, whose prompt's "Now" minute is after the morning.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import data                                           # noqa: E402
from talk import act_of                               # noqa: E402

MODEL = "gemini-3.5-flash-lite"
NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
E2_WORDS = ("snuck", "sneak", "went out", "came back", "with nothing", "empty-handed", "took the food", "promise")
E4_KINDS = ("confront", "accuse", "reassure")
PREV = {"v17": "v16", "v18": "v17"}


def load(v, seed):
    name = f"daniel_ate_it-seed{seed}"
    t = json.load(open(f"runs/{v}/{name}.transcript.json", encoding="utf-8"))
    meta = json.load(open(f"runs/{v}/{name}.meta.json", encoding="utf-8"))
    return t["day3"], meta


def acts(day):
    return sorted((a for turn in day["turns"] for a in turn["acts"]), key=lambda a: tuple(a["decided_at"]))


def now_minute(prompt):
    m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
    if not m:
        return None
    return int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - data.DAY_START


def new_answers(v, seed):
    name = f"{MODEL}-daniel_ate_it-seed{seed}.json"
    old = json.load(open(f"cache/{PREV[v]}/{name}", encoding="utf-8"))
    new = json.load(open(f"cache/{v}/{name}", encoding="utf-8"))
    out = []
    for k, e in new.items():
        if k in old:
            continue
        out.append({"who": re.match(r"You are (\w+),", e["prompt"]).group(1), "minute": now_minute(e["prompt"]),
                    "answer": json.loads(e["response"])})
    return out


def seed_scores(v, seed):
    day, meta = load(v, seed)
    q = day["quiet"]
    end = q["morning_end"]
    st = q["stretches"]
    model = [a for a in acts(day) if a["mode"] == "model"]
    speech = [a for a in model if a["words"]]
    after = [a for a in speech if a["minute"] >= end]
    # E1 (D2's rule)
    pairs = {act_of(a["option"]) for a in speech if st[0]["start"] <= a["minute"] < st[0]["end"]}
    first = st[1] if len(st) > 1 else None
    sp = [a for a in speech if first and first["start"] <= a["minute"] < first["end"]]
    fresh = [a for a in sp if act_of(a["option"]) not in pairs]
    e1 = {"stretch": (first["trigger"], data.clock(first["start"])) if first else None, "fresh": len(fresh),
          "of": len(sp), "holds": bool(sp) and 2 * len(fresh) >= len(sp),
          "acts": [(NAME[a["who"]], data.clock(a["minute"]), a["option"], act_of(a["option"]) not in pairs) for a in sp]}
    # E2
    hit = [a for a in after if any(w in a["words"].lower() for w in E2_WORDS)]
    # E3
    ans = [x for x in new_answers(v, seed) if x["who"] in ("Leo", "Mara") and x["minute"] is not None
           and x["minute"] >= end]
    daniel = [x for x in ans if x["answer"].get("angry_at") == "Daniel"]
    # E4
    other = [(NAME[a["who"]], data.clock(a["minute"]), a["option"]) for a in after
             if act_of(a["option"])[0] not in E4_KINDS]
    return {"seed": seed, "morning_end": data.clock(end), "e1": e1, "e2": (len(hit), len(after)),
            "e3": (len(daniel), len(ans)), "e4": other,
            "e5": {"day3_asks": meta["day3_asks"], "answers_live": meta["answers_live"]},
            "stretches": [(data.clock(s["start"]), data.clock(s["end"]), s["trigger"], s["room"], s["asks"]) for s in st],
            "lines": [(data.clock(a["minute"]), NAME[a["who"]], a["option"], a["words"]) for a in after]}


def main():
    v = sys.argv[1]
    res = [seed_scores(v, s) for s in (1, 2, 3)]
    if len(sys.argv) > 2 and sys.argv[2] == "lines":
        print(json.dumps({r["seed"]: {"stretches": r["stretches"], "lines": r["lines"]} for r in res},
                         ensure_ascii=False, indent=1))
        return
    for r in res:
        print(f"seed {r['seed']} (morning ended {r['morning_end']}):")
        print(f"  E1 first triggered stretch {r['e1']['stretch']}: {r['e1']['fresh']} of {r['e1']['of']} speech acts "
              f"use a pair not used in the morning; holds {r['e1']['holds']}")
        for x in r["e1"]["acts"]:
            print(f"     {x}")
        print(f"  E2 spoken lines after the morning with an E2 phrase: {r['e2'][0]} of {r['e2'][1]}")
        print(f"  E3 Leo's and Mara's answers after the morning naming Daniel as angry_at: {r['e3'][0]} of {r['e3'][1]}")
        print(f"  E4 speech acts after the morning of another kind: {r['e4']}")
        print(f"  E5 {r['e5']}")
    e1 = sum(r["e1"]["holds"] for r in res)
    h, n = sum(r["e2"][0] for r in res), sum(r["e2"][1] for r in res)
    d, a = sum(r["e3"][0] for r in res), sum(r["e3"][1] for r in res)
    e4 = sum(bool(r["e4"]) for r in res)
    live = sum(r["e5"]["answers_live"] for r in res)
    asks = [r["e5"]["day3_asks"] for r in res]
    print(f"\nSUMMARY {v}")
    print(f"E1 seeds holding: {e1} of 3")
    print(f"E2 share of spoken lines after the morning with an E2 phrase: {h} of {n}"
          + (f" = {h / n:.4f}" if n else ""))
    print(f"E3 Leo's and Mara's answers after the morning naming Daniel: {d} of {a}"
          + (f" = {d / a:.4f}" if a else ""))
    print(f"E4 seeds with a speech act after the morning of another kind: {e4} of 3")
    print(f"E5 live total {live}; day-3 asks {asks}")


if __name__ == "__main__":
    main()
