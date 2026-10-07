"""Scores reports/days_v19_plan.md's G1 to G7, read only, no API.

    python runs/v19/scoring/g_score.py                     runs/v19, seeds 2 and 3
    python runs/v19/scoring/g_score.py DIR SEED [SEED...]  another run directory (a check of the script)
    python runs/v19/scoring/g_score.py --account [DIR]     the day and night account for the report

Run from Prototypes/llm-morning/.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import data                                           # noqa: E402
from talk import act_of                               # noqa: E402

NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
FOOD = ("eat", "eat_given", "share")
FAR = ("propose_far", "volunteer_far")
NIGHT_KEY = {1: "night", 2: "night2", 3: "night3", 4: "night4"}


def load(d, seed):
    name = f"daniel_ate_it-seed{seed}"
    t = json.load(open(os.path.join(d, f"{name}.transcript.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(d, f"{name}.meta.json"), encoding="utf-8"))
    return t, meta


def acts(day):
    return sorted((a for turn in day["turns"] for a in turn["acts"]), key=lambda a: tuple(a["decided_at"]))


def model_acts(day):
    return [a for a in acts(day) if a["mode"] == "model"]


def speech(day):
    return [a for a in model_acts(day) if a["words"]]


def morning(day):
    s = day["quiet"]["stretches"][0]
    return [a for a in speech(day) if s["start"] <= a["minute"] < s["end"]]


def bedtimes(night):
    return [d for d in night["decisions"] if d["ask"] == "bedtime"]


def names_them(words, speaker, x):
    terms = {NAME[x]} | ({data.ADDRESS[speaker][x]} if x in data.ADDRESS.get(speaker, {}) else set())
    return any(re.search(rf"\b{re.escape(w)}\b", words, flags=re.I) for w in terms)


def seed_scores(t, meta):
    r = {}
    nights = {k: t[NIGHT_KEY[k]] for k in (3, 4) if NIGHT_KEY[k] in t}
    days = {k: t[f"day{k}"] for k in (3, 4, 5) if f"day{k}" in t}
    # G1
    r["g1"] = [(k, NAME[d["person"]], d["mode"]) for k, n in nights.items() for d in bedtimes(n)
               if d["option"] == "go_further"]
    # G2
    r["g2"] = [(k, data.clock(a["minute"]), NAME[a["who"]], a["option"], a["words"]) for k, d in days.items()
               for a in model_acts(d) if a["option"] in FAR]
    # G3
    r["g3"] = []
    for k, n in nights.items():
        home = [g for g in n["groups"] if g["took"] >= 1 and g["lost"] is None]
        if home and (k + 1) in days:
            food = [(data.clock(a["minute"]), NAME[a["who"]], a["option"]) for a in model_acts(days[k + 1])
                    if a["option"] in FOOD or a["option"].startswith("give_")]
            r["g3"].append({"night": k, "took": [(g["members"], g["took"], g.get("far", False)) for g in home],
                            "food_acts": food, "holds": bool(food)})
    # G4
    r["g4"] = []
    for k, n in nights.items():
        before = set(t[NIGHT_KEY[k - 1]]["away"])
        for x in [q for q in n["away"] if q not in before]:
            if (k + 1) not in days:
                continue
            others = [q for q in data.ORDER if q != x and q not in n["away"]]
            hits = {}
            for a in speech(days[k + 1]):
                if a["who"] in others and names_them(a["words"], a["who"], x):
                    hits.setdefault(NAME[a["who"]], []).append((data.clock(a["minute"]), a["words"]))
            r["g4"].append({"night": k, "lost": NAME[x], "others": [NAME[q] for q in others], "speakers": hits,
                            "tested": len(others) >= 2, "holds": len(hits) >= 2})
    # G5
    r["g5"] = None
    if "night3" in t and t["night3"]["groups"] and 3 in days and 4 in days:
        old = {act_of(a["option"]) for a in morning(days[3])}
        m4 = morning(days[4])
        fresh = [a for a in m4 if act_of(a["option"]) not in old]
        r["g5"] = {"day3_pairs": sorted(map(str, old)), "of": len(m4), "fresh": len(fresh),
                   "holds": bool(m4) and 2 * len(fresh) >= len(m4),
                   "acts": [(data.clock(a["minute"]), NAME[a["who"]], a["option"], str(act_of(a["option"])),
                             act_of(a["option"]) not in old) for a in m4]}
    # G6
    knowers = [(k, d) for k, n in nights.items() for d in bedtimes(n) if "go_further" in d["options"]]
    r["g6"] = {"knower_bedtimes": [(k, NAME[d["person"]], d["option"]) for k, d in knowers],
               "violations": [(k, NAME[d["person"]]) for k, d in knowers if d["option"] == "go_next_door"]}
    # G7
    r["g7"] = {"answers_live": meta["answers_live"], "api_requests": meta["api_requests"],
               "day_asks": {3: meta.get("day3_asks"), **{k: (meta.get(f"day{k}_quiet") or {}).get("day_asks")
                                                         for k in (4, 5)}}}
    return r


def verdicts(res):
    out = {}
    out["G1"] = "PASS" if sum(bool(r["g1"]) for r in res.values()) >= 1 else "FAIL"
    out["G2"] = "PASS" if sum(len(r["g2"]) for r in res.values()) >= 1 else "FAIL"
    g3 = [c for r in res.values() for c in r["g3"]]
    out["G3"] = "NOT TESTED" if not g3 else ("PASS" if all(c["holds"] for c in g3) else "FAIL")
    g4 = [c for r in res.values() for c in r["g4"] if c["tested"]]
    out["G4"] = ("NOT TESTED" if not g4 else ("PASS" if all(c["holds"] for c in g4) else "FAIL"))
    g5 = [r["g5"] for r in res.values() if r["g5"] is not None]
    out["G5"] = "NOT TESTED" if not g5 else ("PASS" if all(c["holds"] for c in g5) else "FAIL")
    kb = [x for r in res.values() for x in r["g6"]["knower_bedtimes"]]
    out["G6"] = ("NOT TESTED" if not kb else
                 ("PASS" if not any(r["g6"]["violations"] for r in res.values()) else "FAIL"))
    live = sum(r["g7"]["answers_live"] for r in res.values())
    days_ok = all(v is not None and v <= 40 for r in res.values() for v in r["g7"]["day_asks"].values())
    out["G7"] = "PASS" if live <= 360 and days_ok else "FAIL"
    return out, live


def account(t, meta):
    """Per day and night: bedtime choices, trips, food, losses; and the spoken lines on the houses, food, the missing."""
    lines = []
    words_far = re.compile(r"further|down the street|along the street|other houses|houses|street", re.I)
    words_food = re.compile(r"food|portion|eat|ate|shelf|brought|bring|hungry|starv", re.I)
    for k in (3, 4, 5):
        if f"day{k}" not in t:
            continue
        d = t[f"day{k}"]
        q = d["quiet"]
        missing = [NAME[x] for x in d.get("away", [])]
        lines.append(f"== day {k}: morning_end {data.clock(q['morning_end'])}; stretches "
                     f"{[(data.clock(s['start']), data.clock(s['end']), s['trigger']) for s in q['stretches']]}; "
                     f"away {missing}")
        for a in model_acts(d):
            if a["option"] in FOOD or a["option"].startswith("give_"):
                lines.append(f"  FOOD ACT {data.clock(a['minute'])} {NAME[a['who']]} {a['option']}: {a['words']!r}")
        for a in speech(d):
            tags = []
            if a["option"] in FAR or words_far.search(a["words"]):
                tags.append("far")
            if words_food.search(a["words"]):
                tags.append("food")
            if any(names_them(a["words"], a["who"], x) for x in d.get("away", []) if x != a["who"]):
                tags.append("missing")
            lines.append(f"  {data.clock(a['minute'])} {NAME[a['who']]} [{a['option']}] {','.join(tags) or '-'}: "
                         f"{a['words']}")
        nk = NIGHT_KEY.get(k)
        if nk and nk in t and k in (3, 4):
            n = t[nk]
            lines.append(f"== night {k}: portions {n['portions_before']} -> {n['portions_after']}; away {n['away']}; "
                         f"far {n.get('far')}; dozed {n.get('dozed')}")
            for b in bedtimes(n):
                lines.append(f"  bedtime {NAME[b['person']]}: {b['option']} (offered go_further: "
                             f"{'go_further' in b['options']}; mode {b['mode']}); reason {b.get('reason')!r}")
            for x in n["decisions"]:
                if x["ask"] != "bedtime":
                    lines.append(f"  {x['ask']} {NAME[x['person']]}: {x['option']} say {x.get('say')!r}")
            for g in n["groups"]:
                lines.append(f"  group {g['members']} far={g.get('far', False)} house={g.get('house')} street "
                             f"{g['street']} found {g['found']} took {g['took']} lost {g['lost']}: {g['outcome']}")
    return lines


def main():
    args = sys.argv[1:]
    if args and args[0] == "--account":
        d = args[1] if len(args) > 1 else "runs/v19"
        for seed in (2, 3):
            t, meta = load(d, seed)
            print(f"######## seed {seed}")
            print("\n".join(account(t, meta)))
        return
    d = args[0] if args else "runs/v19"
    seeds = [int(s) for s in args[1:]] or [2, 3]
    res = {s: seed_scores(*load(d, s)) for s in seeds}
    for s, r in res.items():
        print(f"seed {s}:")
        for g in ("g1", "g2", "g3", "g4", "g5", "g6", "g7"):
            print(f"  {g.upper()} {json.dumps(r[g], ensure_ascii=False)}")
    v, live = verdicts(res)
    print("\nSUMMARY " + d)
    for g, x in v.items():
        print(f"{g} {x}")
    print(f"live asks in total {live}")


if __name__ == "__main__":
    main()
