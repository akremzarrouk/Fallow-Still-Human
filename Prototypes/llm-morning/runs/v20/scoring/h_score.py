"""Scores reports/days_v20_plan.md's H2 to H7, read only, no API. H1 is read by hand; `lines` writes what is read.

    python runs/v20/scoring/h_score.py                       runs/v20 and cache/v20, seeds 2 and 3
    python runs/v20/scoring/h_score.py DIR CACHE SEED...     another run (a check of the script)
    python runs/v20/scoring/h_score.py --account [DIR]       the day and night account, with every Q5 stretch's acts
    python runs/v20/scoring/h_score.py --lines [DIR]         every speech act of days 3-5, for H1

Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset. H4 replays the run from a temp copy of its cache
(morning.run, replay) and keeps every prompt with its scene.
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import data                                           # noqa: E402
import gemini                                         # noqa: E402
import morning                                        # noqa: E402
from talk import act_of                               # noqa: E402
from world import TRIP_KINDS                          # noqa: E402

MODEL = "gemini-3.5-flash-lite"
NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
FOOD = ("eat", "eat_given", "share")
FAR = ("propose_far", "volunteer_far")
NIGHT_KEY = {1: "night", 2: "night2", 3: "night3", 4: "night4"}
SCENES = ["day1", "night", "mind1", "day2", "night2", "mind2", "day3", "night3", "mind3", "day4", "night4", "mind4",
          "day5"]


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


def morning_speech(day):
    s = day["quiet"]["stretches"][0]
    return [a for a in speech(day) if s["start"] <= a["minute"] < s["end"]]


def bedtimes(night):
    return [d for d in night["decisions"] if d["ask"] == "bedtime"]


def names_them(words, speaker, x):
    terms = {NAME[x]} | ({data.ADDRESS[speaker][x]} if x in data.ADDRESS.get(speaker, {}) else set())
    return any(re.search(rf"\b{re.escape(w)}\b", words, flags=re.I) for w in terms)


def q5_stretches(day):
    return [s for s in day["quiet"]["stretches"] if s["trigger"] == "Q5"]


def prompts_by_scene(cache_dir, seed, days=5):
    """A no-API replay of the run from a temp copy of its cache: every prompt asked, with its scene."""
    tmp = tempfile.mkdtemp()
    name = f"{MODEL}-daniel_ate_it-seed{seed}.json"
    shutil.copy(os.path.join(cache_dir, name), os.path.join(tmp, name))
    out, state = [], {"scene": 0}
    orig_ask, orig_new = gemini.Oracle.ask, gemini.Oracle.new_scene

    def new_scene(self):
        state["scene"] += 1
        return orig_new(self)

    def ask(self, system, prompt, schema=None):
        out.append((SCENES[state["scene"]], prompt))
        return orig_ask(self, system, prompt, schema)
    gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
    try:
        _, code = morning.run(seed, replay=True, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp, quiet=True,
                              days=days)
    finally:
        gemini.Oracle.ask, gemini.Oracle.new_scene = orig_ask, orig_new
        shutil.rmtree(tmp)
    return out, code


def seed_scores(t, meta, prompts):
    r = {}
    nights = {k: t[NIGHT_KEY[k]] for k in (3, 4) if NIGHT_KEY[k] in t}
    days = {k: t[f"day{k}"] for k in (3, 4, 5) if f"day{k}" in t}
    # H2
    r["h2_days"] = {k: [(data.clock(e["minute"]), e["fired"], e["asked"], e["why"]) for e in d["quiet"]["log"]
                        if e["kind"] == "Q5"] for k, d in days.items()}
    r["h2_trip_acts"] = {k: [(data.clock(a["minute"]), NAME[a["who"]], a["option"]) for s in q5_stretches(d)
                             for a in model_acts(d) if s["start"] <= a["minute"] < s["end"]
                             and act_of(a["option"])[0] in TRIP_KINDS] for k, d in days.items()}
    # H3
    r["h3"] = [(k, NAME[d["person"]], d["mode"]) for k, n in nights.items() for d in bedtimes(n)
               if d["option"] == "go_further"]
    # H4
    far_words = {a["words"] for d in days.values() for a in model_acts(d) if a["option"] in FAR and a["words"]}
    trips_before = {k: any(t[NIGHT_KEY[j]]["groups"] for j in range(1, k) if NIGHT_KEY[j] in t) for k in (3, 4, 5)}
    p1, p2, scanned = [], [], 0
    for scene, prompt in prompts:
        if SCENES.index(scene) < SCENES.index("day3"):
            continue
        scanned += 1
        k = int(re.search(r"\d+", scene).group())
        for line in prompt.split("\n"):
            m = re.search(r'(\w+) says (?:he|she) will not go: "([^"]*)"', line)
            if m and m.group(2) in far_words:
                p1.append((scene, line[:160]))
            if line.startswith("About going out at night:") and "nobody has gone out" in line and trips_before[k]:
                p2.append((scene, prompt.split(",")[0], line))
    r["h4"] = {"prompts_scanned": scanned, "far_as_will_not_go": p1, "nobody_after_a_trip": p2,
               "trips_before": trips_before}
    # H5
    r["h5_food"], r["h5_loss"] = [], []
    for k, n in nights.items():
        home = [g for g in n["groups"] if g["took"] >= 1 and g["lost"] is None]
        if home and (k + 1) in days:
            food = [(data.clock(a["minute"]), NAME[a["who"]], a["option"]) for a in model_acts(days[k + 1])
                    if a["option"] in FOOD or a["option"].startswith("give_")]
            r["h5_food"].append({"night": k, "took": [(g["members"], g["took"], g.get("far", False)) for g in home],
                                 "food_acts": food, "holds": bool(food)})
        before = set(t[NIGHT_KEY[k - 1]]["away"])
        for x in [q for q in n["away"] if q not in before]:
            if (k + 1) not in days:
                continue
            others = [q for q in data.ORDER if q != x and q not in n["away"]]
            hits = {}
            for a in speech(days[k + 1]):
                if a["who"] in others and names_them(a["words"], a["who"], x):
                    hits.setdefault(NAME[a["who"]], []).append((data.clock(a["minute"]), a["words"]))
            r["h5_loss"].append({"night": k, "lost": NAME[x], "others": [NAME[q] for q in others], "speakers": hits,
                                 "tested": len(others) >= 2, "holds": len(hits) >= 2})
    # H6
    r["h6"] = None
    if "night3" in t and t["night3"]["groups"] and 3 in days and 4 in days:
        old = {act_of(a["option"]) for a in morning_speech(days[3])}
        m4 = morning_speech(days[4])
        fresh = [a for a in m4 if act_of(a["option"]) not in old]
        r["h6"] = {"day3_pairs": sorted(map(str, old)), "of": len(m4), "fresh": len(fresh),
                   "holds": bool(m4) and 2 * len(fresh) >= len(m4),
                   "acts": [(data.clock(a["minute"]), NAME[a["who"]], a["option"], act_of(a["option"]) not in old)
                            for a in m4]}
    # H7
    r["h7"] = {"answers_live": meta["answers_live"], "api_requests": meta["api_requests"],
               "day_asks": {k: (meta.get(f"day{k}_quiet") or {}).get("day_asks") for k in (3, 4, 5)}}
    return r


def verdicts(res):
    out = {}
    fired = sum(any(e[1] for e in v) for r in res.values() for v in r["h2_days"].values())
    trip = sum(len(v) for r in res.values() for v in r["h2_trip_acts"].values())
    out["H2"] = ("PASS" if fired >= 3 and trip >= 1 else "FAIL") + f" (Q5 days {fired} of 6; trip acts in Q5 {trip})"
    out["H3"] = "PASS" if sum(bool(r["h3"]) for r in res.values()) >= 1 else "FAIL"
    p1 = sum(len(r["h4"]["far_as_will_not_go"]) for r in res.values())
    p2 = sum(len(r["h4"]["nobody_after_a_trip"]) for r in res.values())
    out["H4"] = ("PASS" if p1 == 0 and p2 == 0 else "FAIL") + f" (far as 'will not go': {p1}; 'nobody' after a trip: {p2})"
    food = [c for r in res.values() for c in r["h5_food"]]
    loss = [c for r in res.values() for c in r["h5_loss"] if c["tested"]]
    fv = "NOT TESTED" if not food else ("PASS" if all(c["holds"] for c in food) else "FAIL")
    lv = "NOT TESTED" if not loss else ("PASS" if all(c["holds"] for c in loss) else "FAIL")
    out["H5"] = ("FAIL" if "FAIL" in (fv, lv) else "NOT TESTED" if fv == lv == "NOT TESTED" else "PASS") \
        + f" (food: {fv}; loss: {lv})"
    h6 = [r["h6"] for r in res.values() if r["h6"] is not None]
    out["H6"] = "NOT TESTED" if not h6 else ("PASS" if all(c["holds"] for c in h6) else "FAIL")
    live = sum(r["h7"]["answers_live"] for r in res.values())
    ok = all(v is not None and v <= 48 for r in res.values() for v in r["h7"]["day_asks"].values())
    out["H7"] = ("PASS" if live <= 360 and ok else "FAIL") + f" (live {live})"
    return out


def account(t):
    lines = []
    for k in (3, 4, 5):
        if f"day{k}" not in t:
            continue
        d = t[f"day{k}"]
        q = d["quiet"]
        lines.append(f"== day {k}: shelf at 07:00 {d['turns'][0].get('portions', '?') if d['turns'] else '?'}; "
                     f"morning_end {data.clock(q['morning_end'])}; stretches "
                     f"{[(data.clock(s['start']), data.clock(s['end']), s['trigger'], s['asks']) for s in q['stretches']]}; "
                     f"day asks {q['asks']['day']}; away {[NAME[x] for x in d.get('away', [])]}")
        for e in q["log"]:
            if e["kind"] == "Q5":
                lines.append(f"  Q5 {data.clock(e['minute'])}: fired {e['fired']}, asked {e['asked']}, room "
                             f"{e['room']}, awake {e['awake']}, positions {e['positions']}, why {e['why']}")
        for a in model_acts(d):
            if a["option"] in FOOD or a["option"].startswith("give_"):
                lines.append(f"  FOOD ACT {data.clock(a['minute'])} {NAME[a['who']]} {a['option']}: {a['words']!r}")
        for s in q5_stretches(d):
            lines.append(f"  Q5 stretch {data.clock(s['start'])}-{data.clock(s['end'])}, {s['asks']} asks:")
            for a in acts(d):
                if s["start"] <= a["minute"] < s["end"]:
                    lines.append(f"    {data.clock(a['minute'])} {NAME[a['who']]} [{a['option']}, {a['mode']}]: "
                                 f"{a['words'] or ''}")
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
    if args and args[0] in ("--account", "--lines"):
        d = args[1] if len(args) > 1 else "runs/v20"
        for seed in (2, 3):
            t, _ = load(d, seed)
            print(f"######## seed {seed}")
            if args[0] == "--account":
                print("\n".join(account(t)))
            else:
                for k in (3, 4, 5):
                    for a in speech(t[f"day{k}"]):
                        print(f"s{seed} d{k} {data.clock(a['minute'])} {NAME[a['who']]} [{a['option']}]: {a['words']}")
        return
    d = args[0] if args else "runs/v20"
    cache = args[1] if len(args) > 1 else "cache/v20"
    seeds = [int(s) for s in args[2:]] or [2, 3]
    res = {}
    for s in seeds:
        prompts, code = prompts_by_scene(cache, s)
        print(f"seed {s}: replay for H4 exit {code}, prompts {len(prompts)}")
        res[s] = seed_scores(*load(d, s), prompts)
    for s, r in res.items():
        print(f"seed {s}:")
        for k, v in r.items():
            print(f"  {k.upper()} {json.dumps(v, ensure_ascii=False)}")
    print("\nSUMMARY " + d)
    for g, x in verdicts(res).items():
        print(f"{g} {x}")


if __name__ == "__main__":
    main()
